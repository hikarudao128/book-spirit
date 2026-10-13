#!/usr/bin/env python3
"""Synthesize gentle sound effects (48 kHz mono 16-bit) into build/sfx/.

Usage: python3 sfx.py
"""
import os
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "build", "sfx")
SR = 48000
PEAK = 10 ** (-6 / 20)  # -6 dBFS
rng = np.random.default_rng(1234)


def t_axis(dur):
    return np.arange(int(dur * SR)) / SR


def fade(x, fin=0.003, fout=0.010):
    x = x.copy()
    a, b = int(fin * SR), int(fout * SR)
    if a:
        x[:a] *= np.linspace(0, 1, a) ** 2
    if b:
        x[-b:] *= np.linspace(1, 0, b) ** 2
    return x


def onepole_lp(x, fc):
    """One-pole low-pass; fc may be scalar or per-sample array."""
    fc = np.broadcast_to(np.asarray(fc, dtype=float), x.shape)
    a = np.exp(-2 * np.pi * fc / SR)
    y = np.empty_like(x)
    s = 0.0
    for n in range(len(x)):
        s = (1 - a[n]) * x[n] + a[n] * s
        y[n] = s
    return y


def bandpass(x, lo, hi):
    return onepole_lp(x, hi) - onepole_lp(onepole_lp(x, hi), lo)


def norm(x, peak=PEAK):
    m = np.max(np.abs(x))
    return x * (peak / m) if m > 0 else x


def save(name, x):
    x = norm(fade(x))
    y = np.clip(np.round(x * 32767), -32768, 32767).astype("<i2")
    with wave.open(os.path.join(OUT, name), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(y.tobytes())
    print(f"  {name:11s} {len(x) / SR * 1000:5.0f} ms")


def pop():
    t = t_axis(0.070)
    f = 520 + 900 * (t / t[-1]) ** 0.7  # upward blip
    ph = 2 * np.pi * np.cumsum(f) / SR
    env = np.minimum(1, t / 0.004) * np.exp(-t / 0.022)
    return (np.sin(ph) + 0.25 * np.sin(2 * ph)) * env


def whoosh():
    t = t_axis(0.260)
    n = rng.standard_normal(len(t))
    u = t / t[-1]
    fc = 400 + 2600 * np.sin(np.pi * u) ** 2  # sweep up then down
    x = bandpass(n, 250, fc)
    env = np.sin(np.pi * u) ** 1.5
    return x * env


def thud():
    t = t_axis(0.180)
    f = 95 * np.exp(-t / 0.08) + 55
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * np.exp(-t / 0.05)
    click = onepole_lp(rng.standard_normal(len(t)), 900) * np.exp(-t / 0.006) * 0.6
    return body + click


def stamp():
    t = t_axis(0.200)
    f = 120 * np.exp(-t / 0.05) + 60
    ph = 2 * np.pi * np.cumsum(f) / SR
    thump = np.sin(ph) * np.exp(-t / 0.045)
    paper = bandpass(rng.standard_normal(len(t)), 1500, 6000) * np.exp(-t / 0.012)
    paper = np.roll(paper, int(0.004 * SR))
    paper[: int(0.004 * SR)] = 0
    return thump + 0.9 * paper / (np.max(np.abs(paper)) + 1e-9)


def chime():
    t = t_axis(0.600)
    x = np.zeros_like(t)
    for f0, amp, delay, dec in [(1568.0, 1.0, 0.0, 0.25), (2093.0, 0.8, 0.07, 0.22)]:
        tt = np.clip(t - delay, 0, None)
        on = (t >= delay).astype(float)
        env = on * np.minimum(1, tt / 0.003) * np.exp(-tt / dec)
        x += amp * env * (np.sin(2 * np.pi * f0 * tt) + 0.15 * np.sin(2 * np.pi * f0 * 2.76 * tt))
    return x


def flip():
    t = t_axis(0.120)
    n = bandpass(rng.standard_normal(len(t)), 800, 5000)
    u = t / t[-1]
    # two quick flutters
    env = np.exp(-((u - 0.25) / 0.12) ** 2) + 0.6 * np.exp(-((u - 0.6) / 0.15) ** 2)
    return n * env


def main():
    os.makedirs(OUT, exist_ok=True)
    print("writing build/sfx/:")
    for name, fn in [("pop", pop), ("whoosh", whoosh), ("thud", thud),
                     ("stamp", stamp), ("chime", chime), ("flip", flip)]:
        save(name + ".wav", fn())


if __name__ == "__main__":
    main()
