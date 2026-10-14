#!/usr/bin/env python3
"""Generate one WAV per spoken line + build/audio/manifest.json.

Usage:
    python3 video/audio/build_audio.py            # build everything (cached)
    python3 video/audio/build_audio.py --scene 4  # only lines of scene 4
    python3 video/audio/build_audio.py --force    # ignore TTS cache

Voices dir: $PIPER_VOICES_DIR (default: the session scratchpad tts/voices).
Output: build/audio/<line_id>.wav (mono, 16-bit, sample_rate from voices.json)
        build/audio/manifest.json  {line_id: {duration, speaker, text, envelope[...]}}
The envelope is mouth-flap data: RMS per video frame (24 fps), 0..1.
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import wave
from concurrent.futures import ThreadPoolExecutor

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)  # video/
BUILD = os.path.join(ROOT, "build", "audio")
CACHE = os.path.join(BUILD, "_cache")
FPS = 24
DEFAULT_VOICES_DIR = "/tmp/claude-0/-home-user-book-spirit/44f212b8-f27c-5e8a-880b-20012ef7665b/scratchpad/tts/voices"
VOICES_DIR = os.environ.get("PIPER_VOICES_DIR", DEFAULT_VOICES_DIR)


def read_wav(path):
    with wave.open(path, "rb") as w:
        sr = w.getframerate()
        n = w.getnframes()
        ch = w.getnchannels()
        data = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float32) / 32768.0
    if ch > 1:
        data = data.reshape(-1, ch).mean(axis=1)
    return data, sr


def write_wav(path, data, sr):
    data = np.clip(data, -1.0, 1.0)
    pcm = (data * 32767.0).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())


def tts_text_for(line, cfg):
    text = line.get("tts_text") or line["text"]
    for src, dst in cfg.get("pronounce", {}).items():
        text = re.sub(r"\b%s\b" % re.escape(src), dst, text)
    text = text.replace("—", ",").replace("–", ",")
    return text


def synth(voice_key, text, cfg, sr, force=False, length_scale=None):
    """Piper + pitch shift for one voice. Returns float32 array. Cached by content hash."""
    v = cfg["voices"][voice_key]
    ls = length_scale if length_scale is not None else v.get("length_scale", 1.0)
    pitch = v.get("pitch", 1.0)
    key = json.dumps([v["model"], text, ls, pitch, v.get("noise_scale"), sr], sort_keys=True)
    h = hashlib.sha1(key.encode()).hexdigest()[:16]
    out = os.path.join(CACHE, f"{voice_key.replace(' ', '_')}_{h}.wav")
    if os.path.exists(out) and not force:
        return read_wav(out)[0]
    raw = out + ".raw.wav"
    model = os.path.join(VOICES_DIR, v["model"] + ".onnx")
    cmd = [sys.executable, "-m", "piper", "-m", model, "-f", raw, "--length-scale", str(ls)]
    if v.get("noise_scale") is not None:
        cmd += ["--noise-scale", str(v["noise_scale"])]
    subprocess.run(cmd, input=text.encode(), check=True, capture_output=True)
    if abs(pitch - 1.0) > 1e-3:
        # Shift pitch+formants by `pitch` while keeping duration.
        af = f"asetrate={int(sr * pitch)},aresample={sr},atempo={1.0 / pitch:.5f}"
    else:
        af = f"aresample={sr}"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-af", af,
                    "-ac", "1", "-ar", str(sr), out], check=True)
    os.remove(raw)
    return read_wav(out)[0]


def trim(data, sr, pad=0.04):
    if len(data) == 0:
        return data
    win = int(sr * 0.01)
    n = len(data) // win
    if n == 0:
        return data
    rms = np.sqrt((data[: n * win].reshape(n, win) ** 2).mean(axis=1) + 1e-12)
    thr = rms.max() * 10 ** (-40 / 20)
    idx = np.where(rms > thr)[0]
    if len(idx) == 0:
        return data
    a = max(0, idx[0] * win - int(pad * sr))
    b = min(len(data), (idx[-1] + 1) * win + int(pad * sr))
    out = data[a:b].copy()
    f = min(len(out) // 4, int(0.01 * sr))  # 10 ms fades to avoid clicks
    if f > 0:
        out[:f] *= np.linspace(0, 1, f)
        out[-f:] *= np.linspace(1, 0, f)
    return out


def normalize(data, target_dbfs, peak_dbfs):
    """Scale so the RMS of voiced parts hits target, then soft-limit peaks."""
    win = 512
    n = len(data) // win
    if n == 0:
        return data
    rms = np.sqrt((data[: n * win].reshape(n, win) ** 2).mean(axis=1) + 1e-12)
    active = rms[rms > rms.max() * 0.1]
    level = np.sqrt((active ** 2).mean()) if len(active) else rms.max()
    gain = 10 ** (target_dbfs / 20) / max(level, 1e-6)
    out = data * gain
    ceiling = 10 ** (peak_dbfs / 20)
    over = np.abs(out) > ceiling * 0.8
    if over.any():
        knee = ceiling * 0.8
        s = np.sign(out)
        a = np.abs(out)
        a = np.where(a > knee, knee + (ceiling - knee) * np.tanh((a - knee) / (ceiling - knee)), a)
        out = s * a
    return out.astype(np.float32)


def envelope(data, sr, fps=FPS):
    hop = sr / fps
    n = int(np.ceil(len(data) / hop))
    env = []
    for i in range(n):
        a, b = int(i * hop), int((i + 1) * hop)
        seg = data[a:b]
        env.append(float(np.sqrt((seg ** 2).mean())) if len(seg) else 0.0)
    env = np.array(env)
    if env.max() > 0:
        env = env / np.percentile(env, 95)
    env = np.clip(env, 0, 1)
    env[env < 0.12] = 0.0  # gate: closed mouth in pauses
    return [round(float(x), 2) for x in env]


def build_line(line, cfg, sr, force):
    text = tts_text_for(line, cfg)
    speaker = line["speaker"]
    v = cfg["voices"][speaker]
    ls_override = line.get("length_scale")
    if "layers" in v:
        parts = []
        for key, off_ms in v["layers"]:
            d = trim(synth(key, text, cfg, sr, force, ls_override), sr, pad=0.0)
            d = normalize(d, cfg["target_rms_dbfs"], 0.0)
            parts.append((int(off_ms / 1000 * sr), d))
        n = max(o + len(d) for o, d in parts)
        mix = np.zeros(n, np.float32)
        for o, d in parts:
            mix[o:o + len(d)] += d
        data = trim(mix, sr)
    else:
        data = trim(synth(speaker, text, cfg, sr, force, ls_override), sr)
    data = normalize(data, cfg["target_rms_dbfs"], cfg["peak_dbfs"])
    path = os.path.join(BUILD, line["id"] + ".wav")
    write_wav(path, data, sr)
    peak = float(np.abs(data).max())
    rms = float(np.sqrt((data ** 2).mean()))
    return {
        "id": line["id"], "scene": line["scene"], "speaker": speaker, "text": line["text"],
        "duration": round(len(data) / sr, 3), "peak": round(peak, 3), "rms": round(rms, 4),
        "envelope": envelope(data, sr),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scene", type=int)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--jobs", type=int, default=4)
    args = ap.parse_args()
    cfg = json.load(open(os.path.join(HERE, "voices.json")))
    sr = cfg["sample_rate"]
    lines = json.load(open(os.path.join(ROOT, "script_lines.json")))
    todo = [l for l in lines if args.scene is None or l["scene"] == args.scene]
    os.makedirs(CACHE, exist_ok=True)
    man_path = os.path.join(BUILD, "manifest.json")
    manifest = json.load(open(man_path)) if os.path.exists(man_path) else {}
    manifest.pop("_meta", None)

    # Pre-warm layered voices sequentially-safe: synth() is idempotent per cache key.
    with ThreadPoolExecutor(args.jobs) as ex:
        results = list(ex.map(lambda l: build_line(l, cfg, sr, args.force), todo))
    problems = []
    for r in results:
        manifest[r["id"]] = {k: r[k] for k in ("scene", "speaker", "text", "duration", "peak", "rms", "envelope")}
        if r["rms"] < 0.01:
            problems.append(f"{r['id']}: near-silent (rms {r['rms']})")
        if r["peak"] >= 0.999:
            problems.append(f"{r['id']}: clipped")
        words = len(r["text"].split())
        wps = words / max(r["duration"], 0.01)
        if wps > 4.5 or wps < 1.0 and words > 1:
            problems.append(f"{r['id']}: odd speed {wps:.2f} words/s ({r['duration']}s, {words} words)")
    order = {l["id"]: i for i, l in enumerate(lines)}
    manifest = dict(sorted(manifest.items(), key=lambda kv: order.get(kv[0], 1e9)))
    meta = {"sample_rate": sr, "fps": FPS,
            "total_speech_seconds": round(sum(m["duration"] for m in manifest.values()), 2)}
    manifest = {"_meta": meta, **manifest}
    json.dump(manifest, open(man_path, "w"), indent=0)
    print(f"built {len(results)} lines; total speech {meta['total_speech_seconds']}s")
    for p in problems:
        print("WARNING", p)


if __name__ == "__main__":
    main()
