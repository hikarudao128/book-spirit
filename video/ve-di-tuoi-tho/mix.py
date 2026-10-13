#!/usr/bin/env python3
"""Mix narration + sound effects into the final stereo track.

Usage: python3 mix.py build/narration.wav build/sfx_events.json build/final_audio.wav

sfx_events.json: [{"frame": 123, "type": "pop"}, ...]
Narration -> ~-16 LUFS (measured with ffmpeg ebur128); sfx sit ~9 dB below
speech RMS; same-type events within 2 frames are de-duplicated; soft limiter
keeps the peak at <= -1 dBFS. Output: 48 kHz stereo 16-bit WAV, same length
as the narration.
"""
import json
import os
import re
import subprocess
import sys
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SFX_DIR = os.path.join(HERE, "build", "sfx")
SR, FPS = 48000, 24
TARGET_LUFS = -16.0
SFX_BELOW_DB = 9.0
CEIL = 10 ** (-1 / 20)
TYPES = {"pop", "whoosh", "thud", "stamp", "chime", "flip"}
# small per-type pan so the mix is not perfectly mono (-1 left .. +1 right)
PAN = {"pop": 0.0, "whoosh": 0.15, "thud": 0.0, "stamp": 0.0, "chime": -0.12, "flip": 0.1}


def read_wav(path):
    with wave.open(path, "rb") as w:
        sr, ch, sw = w.getframerate(), w.getnchannels(), w.getsampwidth()
        data = np.frombuffer(w.readframes(w.getnframes()), dtype="<i2")
    assert sw == 2 and sr == SR, f"{path}: need 16-bit {SR} Hz"
    x = data.astype(np.float64) / 32768.0
    return x.reshape(-1, ch).mean(axis=1)


def integrated_lufs(path):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af", "ebur128",
                        "-f", "null", "-"], capture_output=True, text=True)
    m = re.findall(r"I:\s+(-?[\d.]+|-inf)\s+LUFS", r.stderr)
    if not m or m[-1] == "-inf":
        return None
    return float(m[-1])


def active_rms_db(x):
    win = SR // 100
    n = len(x) // win
    if n == 0:
        return -120.0
    r = np.sqrt(np.mean(x[: n * win].reshape(n, win) ** 2, axis=1) + 1e-12)
    db = 20 * np.log10(r)
    act = db[db > db.max() - 30]
    return float(10 * np.log10(np.mean(10 ** (act / 10))))


def soft_limit(y, ceil=CEIL, knee_db=6.0):
    th = ceil * 10 ** (-knee_db / 20)
    a = np.abs(y)
    over = a > th
    out = y.copy()
    rng_ = ceil - th
    out[over] = np.sign(y[over]) * (th + rng_ * np.tanh((a[over] - th) / rng_))
    m = np.max(np.abs(out))
    if m > ceil:
        out *= ceil / m
    return out


def main():
    if len(sys.argv) != 4:
        print(__doc__)
        sys.exit(1)
    narr_p, ev_p, out_p = sys.argv[1:]
    narr = read_wav(narr_p)
    lufs = integrated_lufs(narr_p)
    # mono measured as 1 channel; duplicated to L+R it reads ~+3.01 LU louder
    gain_db = (TARGET_LUFS - 3.01 - lufs) if lufs is not None else 0.0
    narr = narr * 10 ** (gain_db / 20)
    speech_db = active_rms_db(narr)
    print(f"narration (mono): {lufs} LUFS -> gain {gain_db:+.1f} dB; speech RMS {speech_db:.1f} dBFS")

    events = []
    if os.path.exists(ev_p):
        with open(ev_p, encoding="utf-8") as f:
            events = json.load(f)
    else:
        print(f"warning: {ev_p} not found; mixing narration only")

    cache = {}
    L = narr.copy()
    R = narr.copy()
    last = {}
    placed = dropped = 0
    for ev in sorted(events, key=lambda e: (e.get("frame", 0), e.get("type", ""))):
        typ, fr = ev.get("type"), ev.get("frame")
        if typ not in TYPES:
            print(f"warning: unknown sfx type {typ!r} at frame {fr}; ignored")
            continue
        if not isinstance(fr, (int, float)) or fr < 0:
            print(f"warning: bad frame {fr!r} for {typ}; ignored")
            continue
        if typ in last and fr - last[typ] <= 2:
            dropped += 1
            continue
        last[typ] = fr
        if typ not in cache:
            p = os.path.join(SFX_DIR, typ + ".wav")
            if not os.path.exists(p):
                print(f"warning: {p} missing (run sfx.py); {typ} ignored")
                cache[typ] = None
            else:
                s = read_wav(p)
                g = 10 ** ((speech_db - SFX_BELOW_DB - active_rms_db(s)) / 20)
                cache[typ] = s * g
        s = cache[typ]
        if s is None:
            continue
        off = int(round(fr * SR / FPS))
        if off >= len(L):
            continue
        seg = s[: len(L) - off]
        pan = PAN.get(typ, 0.0)
        gl, gr = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
        L[off: off + len(seg)] += seg * gl * np.sqrt(2)
        R[off: off + len(seg)] += seg * gr * np.sqrt(2)
        placed += 1

    st = np.stack([L, R], axis=1)
    pk = np.max(np.abs(st))
    st = soft_limit(st)
    y = np.clip(np.round(st * 32767), -32768, 32767).astype("<i2")
    os.makedirs(os.path.dirname(os.path.abspath(out_p)), exist_ok=True)
    with wave.open(out_p, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(y.tobytes())
    print(f"sfx placed {placed}, duplicates dropped {dropped}; pre-limit peak "
          f"{20 * np.log10(pk + 1e-12):.1f} dBFS; wrote {out_p} ({len(y) / SR:.2f} s)")


if __name__ == "__main__":
    main()
