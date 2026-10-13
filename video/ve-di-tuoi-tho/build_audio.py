#!/usr/bin/env python3
"""Build narration audio + frame timing for the video.

Usage: python3 build_audio.py build/script.json

Outputs (relative to this script's directory):
  build/tts/line_XXX.mp3 (+ .txt sidecar)   raw gTTS result, cached by text
  build/tts/line_XXX.wav (+ .key sidecar)   processed 48k mono, atempo 1.12, trimmed
  build/narration.wav                       48 kHz mono 16-bit, frame-aligned
  build/timing.json                         per-line frame timing, amp, wordStarts
"""
import hashlib
import json
import math
import os
import subprocess
import sys
import time
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, "build")
TTS_DIR = os.path.join(BUILD, "tts")

FPS = 24
SR = 48000
SPF = SR // FPS  # 2000 samples per frame
ATEMPO = 1.12
TRIM_DB = -45.0
TRIM_PAD = 0.040
LEAD_IN = 0.40
GAP_SHORT = 0.22
GAP_LONG = 0.38
TAIL = 3.0
VOICED_THR = 0.06
MIN_GAP_FRAMES = 4
PUNCT = (",", ".", ":", "…", "?", ";", "!")

PIPER_MODEL = os.environ.get(
    "PIPER_MODEL",
    "/tmp/claude-0/-home-user-book-spirit/17939cde-8149-5441-ac1c-3c0b80f1bfba/"
    "scratchpad/piper/vi_VN-vais1000-medium.onnx",
)
PROC_VERSION = "v1"  # bump to invalidate processed-wav cache

fallbacks = []


def sec_to_frames(s):
    return int(round(s * FPS))


def sha(s):
    return hashlib.sha1(s.encode("utf-8")).hexdigest()


def read_text(p):
    try:
        with open(p, encoding="utf-8") as f:
            return f.read()
    except OSError:
        return None


def write_text(p, s):
    with open(p, "w", encoding="utf-8") as f:
        f.write(s)


# ---------------------------------------------------------------- TTS
def tts_gtts(text, mp3_path):
    from gtts import gTTS

    delays = [2, 4, 8, 16]
    last_err = None
    for attempt in range(len(delays) + 1):
        try:
            tmp = mp3_path + ".part"
            gTTS(text, lang="vi").save(tmp)
            if os.path.getsize(tmp) < 200:
                raise RuntimeError("gTTS returned tiny file")
            os.replace(tmp, mp3_path)
            return True
        except Exception as e:  # noqa: BLE001
            last_err = e
            if attempt < len(delays):
                print(f"    gTTS error ({e!r}); retry in {delays[attempt]}s", flush=True)
                time.sleep(delays[attempt])
    print(f"    gTTS failed permanently: {last_err!r}", flush=True)
    return False


def tts_piper(text, wav_path):
    r = subprocess.run(
        [sys.executable, "-m", "piper", "-m", PIPER_MODEL, "-f", wav_path],
        input=text.encode("utf-8"),
        capture_output=True,
    )
    if r.returncode != 0 or not os.path.exists(wav_path):
        raise RuntimeError("piper failed: " + r.stderr.decode("utf-8", "replace")[-500:])


def get_raw(i, text):
    """Return (path, engine) of raw TTS audio for this line, using cache."""
    base = os.path.join(TTS_DIR, f"line_{i:03d}")
    mp3, side = base + ".mp3", base + ".txt"
    pwav, pside = base + ".piper.wav", base + ".piper.txt"
    if os.path.exists(mp3) and read_text(side) == text:
        return mp3, "gtts"
    if os.path.exists(pwav) and read_text(pside) == text:
        # previously fell back; try gTTS again once
        pass
    print(f"  [tts] line {i}: {text[:60]}", flush=True)
    time.sleep(0.4)
    if tts_gtts(text, mp3):
        write_text(side, text)
        return mp3, "gtts"
    print(f"  [tts] line {i}: FALLBACK to Piper", flush=True)
    if not (os.path.exists(pwav) and read_text(pside) == text):
        tts_piper(text, pwav)
        write_text(pside, text)
    fallbacks.append(i)
    return pwav, "piper"


# ---------------------------------------------------------------- audio io
def read_wav(path):
    with wave.open(path, "rb") as w:
        assert w.getsampwidth() == 2 and w.getnchannels() == 1
        data = np.frombuffer(w.readframes(w.getnframes()), dtype="<i2")
    return data.astype(np.float32) / 32768.0


def write_wav(path, x, sr=SR):
    y = np.clip(np.round(x * 32767.0), -32768, 32767).astype("<i2")
    tmp = path + ".part"
    with wave.open(tmp, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(y.tobytes())
    os.replace(tmp, path)


def trim_silence(x):
    win = int(0.010 * SR)
    n = len(x) // win
    if n == 0:
        return x
    rms = np.sqrt(np.mean(x[: n * win].reshape(n, win) ** 2, axis=1) + 1e-12)
    db = 20 * np.log10(rms)
    idx = np.where(db > TRIM_DB)[0]
    if len(idx) == 0:
        return x
    pad = int(TRIM_PAD * SR)
    a = max(0, idx[0] * win - pad)
    b = min(len(x), (idx[-1] + 1) * win + pad)
    y = x[a:b].copy()
    # tiny fades to avoid clicks
    f = min(int(0.005 * SR), len(y) // 2)
    if f > 0:
        ramp = np.linspace(0, 1, f, dtype=np.float32)
        y[:f] *= ramp
        y[-f:] *= ramp[::-1]
    return y


def processed(i, text):
    raw, engine = get_raw(i, text)
    base = os.path.join(TTS_DIR, f"line_{i:03d}")
    wav, keyp = base + ".wav", base + ".key"
    key = sha(f"{PROC_VERSION}|{engine}|{ATEMPO}|{TRIM_DB}|{TRIM_PAD}|{text}")
    if os.path.exists(wav) and read_text(keyp) == key:
        return read_wav(wav), engine
    tmp = base + ".tmp.wav"
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-i", raw, "-af", f"atempo={ATEMPO}",
         "-ar", str(SR), "-ac", "1", "-sample_fmt", "s16", tmp],
        check=True,
    )
    x = trim_silence(read_wav(tmp))
    os.remove(tmp)
    write_wav(wav, x)
    write_text(keyp, key)
    return x, engine


# ---------------------------------------------------------------- word timing
def word_starts(text, amp):
    words = text.split()
    n = len(words)
    F = len(amp)
    if n == 0:
        return []
    voiced = np.where(amp > VOICED_THR)[0]
    if len(voiced) == 0:
        return [min(F - 1, int(k * F / n)) for k in range(n)]
    first, last = int(voiced[0]), int(voiced[-1])

    # internal silent gaps (>= MIN_GAP_FRAMES) between first and last voiced frame
    gaps = []  # (gap_start, gap_end_exclusive)
    f = first
    while f <= last:
        if amp[f] <= VOICED_THR:
            g0 = f
            while f <= last and amp[f] <= VOICED_THR:
                f += 1
            if f - g0 >= MIN_GAP_FRAMES:
                gaps.append((g0, f))
        else:
            f += 1

    vmask = amp > VOICED_THR
    cum = np.cumsum(vmask)  # number of voiced frames in [0..f]

    def spread(w0, w1, fa, fb):
        """Distribute words w0..w1-1 across voiced frames in [fa, fb)."""
        fr = [x for x in range(fa, fb) if vmask[x]]
        if not fr:
            fr = list(range(fa, max(fb, fa + 1)))
        m = w1 - w0
        return [fr[min(len(fr) - 1, int(k * len(fr) / m))] for k in range(m)]

    # baseline proportional estimate for each word
    base = spread(0, n, first, last + 1)

    # punctuation breaks: word index k such that words[k-1] ends with punctuation
    breaks = [k for k in range(1, n) if words[k - 1].rstrip("\"'”)»").endswith(PUNCT)]
    anchors = {0: first}
    if gaps and breaks:
        tol = max(12, int(0.30 * (last - first + 1)))
        if len(gaps) == len(breaks):
            pairs = list(zip(breaks, gaps))
        else:
            pairs, gi = [], 0
            for k in breaks:
                best, bestd = None, None
                for j in range(gi, len(gaps)):
                    d = abs(gaps[j][1] - base[k])
                    if bestd is None or d < bestd:
                        best, bestd = j, d
                if best is not None and bestd <= tol:
                    pairs.append((k, gaps[best]))
                    gi = best + 1
        for k, (g0, g1) in pairs:
            anchors[k] = g1
    keys = sorted(anchors)
    out = [0] * n
    for a_i, k in enumerate(keys):
        k2 = keys[a_i + 1] if a_i + 1 < len(keys) else n
        fb = anchors[keys[a_i + 1]] if a_i + 1 < len(keys) else last + 1
        # stop before the gap that precedes the next anchor
        seg = spread(k, k2, anchors[k], fb)
        out[k:k2] = seg
    # monotonic + clamp
    res, prev = [], 0
    for v in out:
        v = int(max(prev, min(F - 1, max(0, v))))
        res.append(v)
        prev = v
    return res


# ---------------------------------------------------------------- main
def gap_after(text):
    t = text.rstrip().rstrip("\"'”)»")
    if t.endswith("?") or t.endswith("…") or t.endswith("..."):
        return GAP_LONG
    return GAP_SHORT


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    t0 = time.time()
    os.makedirs(TTS_DIR, exist_ok=True)
    with open(sys.argv[1], encoding="utf-8") as f:
        script = json.load(f)
    for pos, e in enumerate(script):
        if e.get("i") != pos:
            sys.exit(f"entry at position {pos} has i={e.get('i')} (must equal position)")

    # pass 1: audio per line + layout in frames
    clips, layout = [], []
    frame = sec_to_frames(LEAD_IN)
    engines = {}
    for idx, e in enumerate(script):
        text = e.get("text")
        is_last = idx == len(script) - 1
        if text:
            x, eng = processed(e["i"], text)
            engines[e["i"]] = eng
            nfr = max(1, math.ceil(len(x) / SPF))
            layout.append({"i": e["i"], "start": frame, "frames": nfr, "spoken": True, "text": text})
            clips.append(x)
            frame += nfr
            if not is_last:
                frame += sec_to_frames(gap_after(text))
        else:
            nfr = sec_to_frames(float(e.get("beat", 0) or 0))
            layout.append({"i": e["i"], "start": frame, "frames": nfr, "spoken": False, "text": None})
            clips.append(None)
            frame += nfr
    total = frame + sec_to_frames(TAIL)

    # pass 2: assemble at exact frame-aligned sample offsets
    narr = np.zeros(total * SPF, dtype=np.float32)
    for L, x in zip(layout, clips):
        if x is not None:
            off = L["start"] * SPF
            narr[off: off + len(x)] += x
    peak = float(np.max(np.abs(narr))) if len(narr) else 0
    if peak > 0.99:
        narr *= 0.99 / peak
    write_wav(os.path.join(BUILD, "narration.wav"), narr)

    # per-frame RMS, normalized by p95 over spoken frames
    frms = np.sqrt(np.mean(narr.reshape(total, SPF) ** 2, axis=1))
    spoken_frames = np.concatenate(
        [np.arange(L["start"], L["start"] + L["frames"]) for L in layout if L["spoken"]]
        or [np.arange(0)]
    ).astype(int)
    ref = float(np.percentile(frms[spoken_frames], 95)) if len(spoken_frames) else 1.0
    ref = ref if ref > 1e-9 else 1.0
    ampall = np.clip(frms / ref, 0, 1)

    lines = []
    for L in layout:
        s, n = L["start"], L["frames"]
        if L["spoken"]:
            amp = ampall[s: s + n]
            ws = word_starts(L["text"], amp)
            ampl = [round(float(v), 3) for v in amp]
        else:
            ws, ampl = [], [0.0] * n
        lines.append({"i": L["i"], "start": s, "frames": n, "spoken": L["spoken"],
                      "wordStarts": ws, "amp": ampl})
    timing = {"fps": FPS, "totalFrames": total, "lines": lines}
    with open(os.path.join(BUILD, "timing.json"), "w", encoding="utf-8") as f:
        json.dump(timing, f, ensure_ascii=False, separators=(",", ":"))

    nsp = sum(1 for L in layout if L["spoken"])
    print("---- build_audio summary ----")
    print(f"entries: {len(layout)} ({nsp} spoken, {len(layout) - nsp} beats)")
    print(f"total: {total} frames = {total / FPS:.2f} s ({int(total / FPS // 60)}m{(total / FPS) % 60:04.1f}s)")
    print(f"engines: gtts={sum(1 for v in engines.values() if v == 'gtts')}, "
          f"piper={sum(1 for v in engines.values() if v == 'piper')}")
    pip = sorted(k for k, v in engines.items() if v == "piper")
    print(f"piper fallback lines: {pip if pip else 'none'}")
    print(f"wrote build/narration.wav, build/timing.json  ({time.time() - t0:.1f}s)")


if __name__ == "__main__":
    main()
