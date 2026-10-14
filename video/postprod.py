#!/usr/bin/env python3
"""Post-production: subtitles, final assembly, loudness, QA sheets.

  python3 video/postprod.py subs        # out/ticket-to-childhood.{en,vi}.srt
  python3 video/postprod.py mixcheck    # per-scene speech vs music/SFX levels (numeric)
  python3 video/postprod.py assemble    # out/ticket-to-childhood.mp4 (needs build/scenes/sceneNN.mp4 + .wav)
  python3 video/postprod.py qa          # contact sheets -> build/qa/
  python3 video/postprod.py all         # subs + assemble + qa

Scene video/audio come from render.py (sceneNN.mp4 is video only, sceneNN.wav the scene mix).
Video streams are concatenated losslessly (same encoder params for every scene); the audio is
concatenated as PCM with 15 ms edge fades, loudness-normalised (two-pass loudnorm, -16 LUFS,
-1.5 dBTP) and encoded once, so there is no per-scene AAC priming drift.
"""
import json
import math
import os
import re
import subprocess
import sys
import wave

import numpy as np

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
BUILD = os.path.join(ROOT, "build")
OUT = os.path.join(ROOT, "out")
NAME = "ticket-to-childhood"
FADE_S = 0.015
LUFS, TP, LRA = -16.0, -1.5, 11.0


def timeline():
    tl = json.load(open(os.path.join(BUILD, "timeline.json")))
    fps = tl["fps"]
    scenes, off = [], 0.0
    for k in sorted(tl["scenes"], key=int):
        s = tl["scenes"][k]
        length = int(round(s["duration"] * fps)) / fps     # what render.py actually renders
        scenes.append({"n": int(k), "offset": off, "length": length, "lines": s["lines"]})
        off += length
    return fps, scenes, off


# ------------------------------------------------------------------ subtitles
def _wrap(text, width=42):
    words, lines, cur = text.split(), [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > width:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}" if cur else w
    if cur:
        lines.append(cur)
    return lines


def _balance(lines):
    """Re-split 2 wrapped lines so they are roughly equal in length (reads better)."""
    if len(lines) != 2:
        return lines
    words = " ".join(lines).split()
    best = None
    for i in range(1, len(words)):
        a, b = " ".join(words[:i]), " ".join(words[i:])
        if len(a) <= 42 and len(b) <= 42:
            score = abs(len(a) - len(b))
            if best is None or score < best[0]:
                best = (score, [a, b])
    return best[1] if best else lines


def _chunks(text, width=42):
    """Split text into cue chunks of at most 2 lines x ~width chars, of similar length,
    preferring breaks after punctuation."""
    if len(_wrap(text, width)) <= 2:
        return [_balance(_wrap(text, width))]
    words = text.split()
    ends, pos = [], 0
    for w in words:
        pos += len(w) + 1
        ends.append(pos)
    total = ends[-1]
    k = math.ceil(len(_wrap(text, width)) / 2)
    while True:
        cuts, prev = [], 0
        for j in range(1, k):
            target = total * j / k
            best = None
            for i in range(prev + 1, len(words)):
                score = abs(ends[i - 1] - target) - (14 if re.search(r"[.!?…:,—]$", words[i - 1]) else 0)
                if best is None or score < best[0]:
                    best = (score, i)
            cuts.append(best[1])
            prev = best[1]
        bounds = [0] + cuts + [len(words)]
        groups = [" ".join(words[bounds[i]:bounds[i + 1]]) for i in range(k)]
        if all(g and len(_wrap(g, width)) <= 2 for g in groups):
            return [_balance(_wrap(g, width)) for g in groups]
        k += 1


def _ts(t):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def make_srt(texts, path):
    _, scenes, _ = timeline()
    cues = []
    for sc in scenes:
        for ln in sc["lines"]:
            text = texts[ln["id"]]
            t0, t1 = sc["offset"] + ln["start"], sc["offset"] + ln["end"]
            chunks = _chunks(text)
            total = sum(len(" ".join(c)) for c in chunks)
            t = t0
            for c in chunks:
                d = (t1 - t0) * len(" ".join(c)) / total
                cues.append([t, t + d, "\n".join(c)])
                t += d
    # minimum display time: extend short cues into the following silence (never overlap the next cue)
    for i, c in enumerate(cues):
        nxt = cues[i + 1][0] if i + 1 < len(cues) else c[1] + 2
        want = max(c[1] + 0.25, c[0] + 1.0)
        c[1] = max(c[1], min(want, nxt - 0.04))
    with open(path, "w", encoding="utf-8") as f:
        for i, (a, b, s) in enumerate(cues, 1):
            f.write(f"{i}\n{_ts(a)} --> {_ts(b)}\n{s}\n\n")
    print(f"{path}: {len(cues)} cues")
    return path


def subs():
    os.makedirs(OUT, exist_ok=True)
    lines = json.load(open(os.path.join(ROOT, "script_lines.json")))
    en = {l["id"]: l["text"] for l in lines}
    vi = json.load(open(os.path.join(ROOT, "subtitles_vi.json")))
    missing = [k for k in en if k not in vi]
    assert not missing, f"missing vi lines: {missing}"
    make_srt(en, os.path.join(OUT, f"{NAME}.en.srt"))
    make_srt(vi, os.path.join(OUT, f"{NAME}.vi.srt"))


# ------------------------------------------------------------------ audio
def _read_wav(path):
    with wave.open(path, "rb") as w:
        assert w.getnchannels() == 1
        return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768.0, w.getframerate()


def _write_wav(path, x, sr):
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())


def full_audio():
    fps, scenes, total = timeline()
    parts, sr = [], None
    for sc in scenes:
        x, sr = _read_wav(os.path.join(BUILD, "scenes", f"scene{sc['n']:02d}.wav"))
        n = int(round(sc["length"] * sr))
        x = np.pad(x, (0, max(0, n - len(x))))[:n].copy()
        k = int(FADE_S * sr)
        ramp = np.sin(np.linspace(0, math.pi / 2, k)) ** 2
        x[:k] *= ramp
        x[-k:] *= ramp[::-1]
        parts.append(x)
    full = np.concatenate(parts)
    path = os.path.join(BUILD, "scenes", "final_mix.wav")
    _write_wav(path, full, sr)
    print(f"mix: {len(full) / sr:.3f}s (timeline {total:.3f}s)")
    return path


def loudnorm_measure(path, extra=""):
    af = f"{extra}loudnorm=I={LUFS}:TP={TP}:LRA={LRA}:print_format=json"
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af", af, "-f", "null", "-"],
                       capture_output=True, text=True)
    m = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", r.stderr, re.S)
    return json.loads(m.group(0))


def ebur128(path):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-map", "0:a",
                        "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True)
    tail = r.stderr[r.stderr.rfind("Summary:"):]
    i = float(re.search(r"I:\s+(-?[\d.]+) LUFS", tail).group(1))
    lra = float(re.search(r"LRA:\s+(-?[\d.]+) LU", tail).group(1))
    tp = float(re.search(r"Peak:\s+(-?[\d.inf]+) dBFS", tail).group(1))
    return {"I": i, "LRA": lra, "TP": tp}


# ------------------------------------------------------------------ mix check
def mixcheck():
    """Speech level vs music/SFX level per scene (numeric only)."""
    import importlib
    from lib.context import SceneContext
    from lib import sfx
    man = json.load(open(os.path.join(BUILD, "audio", "manifest.json")))
    sr = man["_meta"]["sample_rate"]
    _, scenes, _ = timeline()
    db = lambda v: 20 * math.log10(max(v, 1e-9))
    print("scene  speech_rms  bed_rms_under_speech  bed_rms_gaps  speech-bed(dB)  boundary_jump")
    for sc in scenes:
        ctx = SceneContext(sc["n"])
        n = int(round(sc["length"] * sr))
        speech, bed = np.zeros(n + sr, np.float32), np.zeros(n + sr, np.float32)
        mask = np.zeros(n + sr, bool)
        for l in ctx.lines:
            d, _ = _read_wav(os.path.join(BUILD, "audio", l.id + ".wav"))
            i = int(l.start * sr)
            d = d[: max(0, len(speech) - i)]
            speech[i:i + len(d)] += d
            mask[i:i + len(d)] = True
        mod = importlib.import_module(f"scenes.scene{sc['n']:02d}")
        for cue in (mod.audio_cues(ctx) if hasattr(mod, "audio_cues") else []):
            i, d = sfx.render_cue(cue, sr)
            d = d[: max(0, len(bed) - i)]
            bed[i:i + len(d)] += d
        speech, bed, mask = speech[:n], bed[:n], mask[:n]
        # speech RMS over voiced 50 ms windows only
        w = int(0.05 * sr)
        nb = n // w
        s_win = np.sqrt((speech[:nb * w].reshape(nb, w) ** 2).mean(1))
        b_win = np.sqrt((bed[:nb * w].reshape(nb, w) ** 2).mean(1))
        voiced = s_win > 0.01
        s_rms = np.sqrt((s_win[voiced] ** 2).mean()) if voiced.any() else 0
        b_rms_sp = np.sqrt((b_win[voiced] ** 2).mean()) if voiced.any() else 0
        b_rms_gap = np.sqrt((b_win[~voiced] ** 2).mean()) if (~voiced).any() else 0
        # loudest 0.5 s of bed under speech (worst-case masking)
        b_peak = 0.0
        if voiced.any():
            k = 10
            bb = np.convolve(b_win ** 2 * voiced, np.ones(k) / k, "same")
            b_peak = math.sqrt(bb.max())
        mix, _ = _read_wav(os.path.join(BUILD, "scenes", f"scene{sc['n']:02d}.wav"))
        print(f"{sc['n']:5d}  {db(s_rms):9.1f}  {db(b_rms_sp):19.1f}  {db(b_rms_gap):12.1f}  "
              f"{db(s_rms) - db(b_rms_sp):12.1f}  (worst 0.5s bed {db(b_peak):.1f})  "
              f"edges in/out {abs(mix[0]):.3f}/{abs(mix[-1]):.3f}")


# ------------------------------------------------------------------ assembly
def assemble(crf=None):
    os.makedirs(OUT, exist_ok=True)
    fps, scenes, total = timeline()
    sdir = os.path.join(BUILD, "scenes")
    for sc in scenes:
        p = os.path.join(sdir, f"scene{sc['n']:02d}.mp4")
        d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p],
                                 capture_output=True, text=True).stdout)
        flag = "" if abs(d - sc["length"]) < 0.1 else "  <-- MISMATCH"
        print(f"scene {sc['n']:2d}: video {d:.3f}s, timeline {sc['length']:.3f}s{flag}")
    lst = os.path.join(sdir, "final_concat.txt")
    with open(lst, "w") as f:
        for sc in scenes:
            f.write(f"file 'scene{sc['n']:02d}.mp4'\n")
    wav = full_audio()
    m = loudnorm_measure(wav)
    print("loudnorm pass 1:", {k: m[k] for k in ("input_i", "input_tp", "input_lra", "input_thresh")})
    af = (f"loudnorm=I={LUFS}:TP={TP}:LRA={LRA}:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
          f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:"
          f"linear=true,aresample=48000")
    norm = os.path.join(sdir, "final_mix_norm.wav")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-af", af, "-ac", "2", "-c:a", "pcm_s16le",
                    norm], check=True)
    vcodec = ["-c:v", "copy"] if crf is None else ["-c:v", "libx264", "-preset", "medium", "-crf", str(crf),
                                                   "-pix_fmt", "yuv420p", "-r", str(fps)]
    out = os.path.join(OUT, f"{NAME}.mp4")
    en, vi = os.path.join(OUT, f"{NAME}.en.srt"), os.path.join(OUT, f"{NAME}.vi.srt")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-i", norm,
           "-i", en, "-i", vi, "-map", "0:v", "-map", "1:a", "-map", "2:s", "-map", "3:s", *vcodec,
           "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", "-c:s", "mov_text",
           "-metadata:s:s:0", "language=eng", "-metadata:s:s:0", "title=English",
           "-metadata:s:s:1", "language=vie", "-metadata:s:s:1", "title=Tiếng Việt",
           "-disposition:s:0", "default", "-disposition:s:1", "0",
           "-metadata", "title=Give Me a Ticket to Childhood", "-movflags", "+faststart", out]
    subprocess.run(cmd, check=True)
    d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", out],
                             capture_output=True, text=True).stdout)
    print(f"-> {out}: {d:.3f}s (sum of scenes {total:.3f}s), {os.path.getsize(out) / 1e6:.1f} MB")
    print("final loudness:", ebur128(out))
    return out


# ------------------------------------------------------------------ QA sheets
def qa():
    fps, scenes, total = timeline()
    src = os.path.join(OUT, f"{NAME}.mp4")
    qdir = os.path.join(BUILD, "qa")
    os.makedirs(qdir, exist_ok=True)
    for f in os.listdir(qdir):
        if f.endswith(".png"):
            os.remove(os.path.join(qdir, f))
    # every 3 s
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-vf",
                    "fps=1/3,scale=426:240,drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:"
                    "text='%{pts\\:hms}':x=4:y=4:fontsize=14:fontcolor=white:box=1:boxcolor=black@0.6,"
                    "tile=4x3:padding=4:color=gray", os.path.join(qdir, "every3s_%02d.png")], check=True)
    # first/last frame of each scene + full-size boundary frames
    frames = []
    for sc in scenes:
        n0 = int(round(sc["offset"] * fps))
        n1 = n0 + int(round(sc["length"] * fps)) - 1
        frames += [(sc["n"], "first", n0), (sc["n"], "last", n1)]
    sel = "+".join(f"eq(n\\,{n})" for _, _, n in frames)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-vf", f"select='{sel}'", "-vsync", "0",
                    os.path.join(qdir, "edge_%03d.png")], check=True)
    names = []
    for i, (s, kind, n) in enumerate(frames, 1):
        a = os.path.join(qdir, f"edge_{i:03d}.png")
        b = os.path.join(qdir, f"scene{s:02d}_{kind}.png")
        os.rename(a, b)
        names.append(b)
    # boundary sheet: pairs (last of N, first of N+1)
    seq = []
    for sc in scenes:
        seq += [os.path.join(qdir, f"scene{sc['n']:02d}_first.png"), os.path.join(qdir, f"scene{sc['n']:02d}_last.png")]
    for i, p in enumerate(seq):
        os.symlink(p, os.path.join(qdir, f"_seq_{i:03d}.png"))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", "1", "-i", os.path.join(qdir, "_seq_%03d.png"),
                    "-vf", "scale=426:240,tile=4x3:padding=4:color=gray", os.path.join(qdir, "scene_edges_%02d.png")],
                   check=True)
    for f in os.listdir(qdir):
        if f.startswith("_seq_"):
            os.remove(os.path.join(qdir, f))
    print("QA sheets ->", qdir)


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    if what in ("subs", "all"):
        subs()
    if what == "mixcheck":
        mixcheck()
    if what in ("assemble", "all"):
        assemble(int(sys.argv[2]) if len(sys.argv) > 2 else None)
    if what in ("qa", "all"):
        qa()
