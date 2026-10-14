"""Procedural sound effects + music bed (numpy, deterministic, no downloads).

A scene may define `audio_cues(ctx) -> list[dict]`; render.py mixes them under the dialogue:
    {"sfx": "music_bed", "start": 0.0, "dur": 9.5, "gain": 0.18, "fade_out": 0.0}
    {"sfx": "record_scratch", "start": 9.5, "gain": 0.5}
Available names: see SFX dict at the bottom (music_bed, music_sad, record_scratch, pop, whoosh,
thud, gavel, ding, shutter, boing, tick, slap).
"""
import math

import numpy as np

SR = 22050


def _t(dur, sr=SR):
    return np.arange(int(dur * sr)) / sr


def _env(n, attack=0.005, decay=0.3, sr=SR):
    t = np.arange(n) / sr
    a = np.clip(t / max(attack, 1e-4), 0, 1)
    return a * np.exp(-t / max(decay, 1e-4))


def _pluck(freq, dur=0.9, sr=SR, bright=0.5):
    t = _t(dur, sr)
    y = np.zeros_like(t)
    for k, amp in enumerate([1.0, 0.5 * bright, 0.3 * bright, 0.15 * bright], start=1):
        y += amp * np.sin(2 * np.pi * freq * k * t) * np.exp(-t * (3 + k * 2.5))
    return y * np.clip(t / 0.004, 0, 1)


def _note(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def music_bed(dur, sr=SR, bpm=96, seed=1, mood="happy"):
    """Gentle plucked pentatonic loop (ukulele-ish) with soft bass. mood: happy | sad."""
    rng = np.random.default_rng(seed)
    beat = 60 / bpm
    out = np.zeros(int((dur + 2) * sr))
    if mood == "happy":
        prog = [(48, [60, 64, 67, 72]), (45, [57, 60, 64, 69]), (41, [57, 60, 65, 69]), (43, [55, 59, 62, 67])]
    else:
        prog = [(45, [57, 60, 64]), (41, [53, 57, 60]), (48, [55, 60, 64]), (40, [55, 59, 64])]
        bpm = 70
        beat = 60 / bpm
    bar = 4 * beat
    nbars = int(dur / bar) + 2
    for b in range(nbars):
        root, chord = prog[b % len(prog)]
        t0 = b * bar
        for k in (0, 2):
            i = int((t0 + k * beat) * sr)
            s = _pluck(_note(root), 1.2, sr, 0.2) * 0.55
            out[i:i + len(s)] += s[: max(0, len(out) - i)]
        for e in range(8):
            if mood == "sad" and e % 2:
                continue
            n = chord[(e if e < 4 else 7 - e) % len(chord)]
            if rng.random() < 0.25:
                n += 12
            i = int((t0 + e * beat / 2) * sr)
            s = _pluck(_note(n), 0.8, sr, 0.6) * (0.32 if e % 2 else 0.4)
            out[i:i + len(s)] += s[: max(0, len(out) - i)]
        if mood == "happy":   # soft shaker on off-beats
            for e in range(1, 8, 2):
                i = int((t0 + e * beat / 2) * sr)
                n = int(0.05 * sr)
                s = rng.standard_normal(n) * _env(n, 0.002, 0.015, sr) * 0.05
                out[i:i + n] += s[: max(0, len(out) - i)]
    out = out[: int(dur * sr)]
    fi = min(len(out), int(0.6 * sr))
    out[:fi] *= np.linspace(0, 1, fi)
    return out / (np.abs(out).max() + 1e-9) * 0.8


def record_scratch(sr=SR):
    t = _t(0.38, sr)
    f = 900 * np.exp(-t * 6) + 150
    ph = 2 * np.pi * np.cumsum(f) / sr
    saw = 2 * ((ph / (2 * np.pi)) % 1) - 1
    noise = np.random.default_rng(3).standard_normal(len(t))
    y = (0.6 * saw + 0.4 * noise) * np.exp(-t * 5) * np.clip(t / 0.01, 0, 1)
    return y / np.abs(y).max()


def pop(sr=SR):
    t = _t(0.09, sr)
    f = 500 + 900 * t / 0.09
    y = np.sin(2 * np.pi * np.cumsum(f) / sr) * np.exp(-t * 40)
    return y / np.abs(y).max()


def whoosh(sr=SR, dur=0.45):
    t = _t(dur, sr)
    n = np.random.default_rng(5).standard_normal(len(t))
    k = 30
    n = np.convolve(n, np.ones(k) / k, mode="same")
    env = np.sin(np.pi * t / dur) ** 2
    y = n * env
    return y / np.abs(y).max()


def thud(sr=SR):
    t = _t(0.3, sr)
    y = np.sin(2 * np.pi * (90 + 60 * np.exp(-t * 30)) * t) * np.exp(-t * 14)
    return y / np.abs(y).max()


def gavel(sr=SR):
    t = _t(0.25, sr)
    click = np.random.default_rng(7).standard_normal(len(t)) * np.exp(-t * 120)
    body = np.sin(2 * np.pi * 420 * t) * np.exp(-t * 30) + 0.6 * np.sin(2 * np.pi * 180 * t) * np.exp(-t * 20)
    y = 0.6 * click + body
    return y / np.abs(y).max()


def ding(sr=SR):
    t = _t(1.4, sr)
    y = (np.sin(2 * np.pi * 1320 * t) + 0.4 * np.sin(2 * np.pi * 2640 * t) + 0.2 * np.sin(2 * np.pi * 3960 * t))
    y *= np.exp(-t * 3.5) * np.clip(t / 0.003, 0, 1)
    return y / np.abs(y).max()


def shutter(sr=SR):
    out = np.zeros(int(0.14 * sr))
    rng = np.random.default_rng(9)
    for st in (0.0, 0.07):
        i = int(st * sr)
        n = int(0.025 * sr)
        out[i:i + n] += rng.standard_normal(n) * _env(n, 0.001, 0.006, sr)
    return out / np.abs(out).max()


def boing(sr=SR):
    t = _t(0.5, sr)
    f = 220 + 120 * np.sin(2 * np.pi * 12 * t) * np.exp(-t * 4) + 80 * t
    y = np.sin(2 * np.pi * np.cumsum(f) / sr) * np.exp(-t * 5)
    return y / np.abs(y).max()


def tick(sr=SR):
    t = _t(0.03, sr)
    y = np.sin(2 * np.pi * 2000 * t) * np.exp(-t * 200)
    return y / np.abs(y).max()


def slap(sr=SR):
    t = _t(0.18, sr)
    n = np.random.default_rng(11).standard_normal(len(t)) * np.exp(-t * 45)
    y = n + 0.5 * np.sin(2 * np.pi * 160 * t) * np.exp(-t * 25)
    return y / np.abs(y).max()


SFX = {
    "music_bed": lambda dur, sr: music_bed(dur, sr, mood="happy"),
    "music_sad": lambda dur, sr: music_bed(dur, sr, mood="sad"),
    "record_scratch": lambda dur, sr: record_scratch(sr),
    "pop": lambda dur, sr: pop(sr),
    "whoosh": lambda dur, sr: whoosh(sr),
    "thud": lambda dur, sr: thud(sr),
    "gavel": lambda dur, sr: gavel(sr),
    "ding": lambda dur, sr: ding(sr),
    "shutter": lambda dur, sr: shutter(sr),
    "boing": lambda dur, sr: boing(sr),
    "tick": lambda dur, sr: tick(sr),
    "slap": lambda dur, sr: slap(sr),
}


def render_cue(cue, sr=SR):
    """-> (start_sample, float32 array) for one cue dict."""
    name = cue["sfx"]
    dur = cue.get("dur", 1.0)
    y = SFX[name](dur, sr).astype(np.float32)
    if "dur" in cue:
        y = y[: int(cue["dur"] * sr)]
    fo = cue.get("fade_out", 0.02)
    n = min(len(y), int(fo * sr))
    if n > 0:
        y[-n:] *= np.linspace(1, 0, n)
    return int(cue["start"] * sr), y * cue.get("gain", 0.4)
