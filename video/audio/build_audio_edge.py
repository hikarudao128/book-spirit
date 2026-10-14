#!/usr/bin/env python3
"""Generate one WAV per spoken line + build/audio/manifest.json with Microsoft Edge neural TTS.

This is the default voice builder. `build_audio.py` (offline Piper) stays as a fallback and writes
the same files, minus the real word timings.

Usage:
    python3 video/audio/build_audio_edge.py            # build everything (cached)
    python3 video/audio/build_audio_edge.py --scene 4  # only lines of scene 4
    python3 video/audio/build_audio_edge.py --force    # ignore the TTS cache
    python3 video/audio/build_audio_edge.py --samples  # also write build/audio/samples.mp3 (one line per voice)

Casting: `edge` section of audio/voices.json (voice, rate, pitch per speaker; layers for group lines;
per-line overrides). A line's `length_scale` in script_lines.json still works: it scales the speaking
rate on top of the speaker's rate (1.18 = slower, 0.85 = faster).

Output (same as build_audio.py):
    build/audio/<line_id>.wav     mono, 16-bit, sample_rate from voices.json (22050)
    build/audio/manifest.json     {line_id: {scene, speaker, text, duration, peak, rms, envelope, words}}
`words` = [[display_word, start, end], ...] in seconds from the start of the line's WAV, taken from
the TTS WordBoundary events (real timings, not estimates). lib/context.py's ctx.words() uses them.

Cache: build/audio/_edge/<hash>.mp3 + .json (word marks); hash of (voice, rate, pitch, text).
Needs network access. In the cloud sandbox certifi is pointed at the proxy CA automatically.
"""
import argparse
import asyncio
import difflib
import hashlib
import json
import os
import re
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_audio import ROOT, BUILD, FPS, write_wav, normalize, envelope, tts_text_for  # noqa: E402

CACHE = os.path.join(BUILD, "_edge")
PROXY_CA = "/root/.ccr/ca-bundle.crt"


def _edge():
    import certifi
    if os.path.exists(PROXY_CA):
        certifi.where = lambda: PROXY_CA   # the sandbox proxy re-signs TLS with its own CA
    import edge_tts
    return edge_tts


# ------------------------------------------------------------------ synthesis + cache
def _fmt_rate(pct):
    pct = int(round(pct))
    return f"{'+' if pct >= 0 else '-'}{abs(pct)}%"


def _fmt_pitch(hz):
    hz = int(round(hz))
    return f"{'+' if hz >= 0 else '-'}{abs(hz)}Hz"


def _key(voice, rate, pitch, text):
    return hashlib.sha1(json.dumps([voice, rate, pitch, text]).encode()).hexdigest()[:16]


async def _synth_one(edge_tts, voice, rate, pitch, text, base, sem, attempts=5):
    async with sem:
        last = None
        for i in range(attempts):
            try:
                com = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch, volume="+0%",
                                           boundary="WordBoundary")
                audio, marks = bytearray(), []
                async for ch in com.stream():
                    if ch["type"] == "audio":
                        audio += ch["data"]
                    elif ch["type"] == "WordBoundary":
                        marks.append({"t": ch["offset"] / 1e7, "d": ch["duration"] / 1e7, "w": ch["text"]})
                if not audio or not marks:
                    raise RuntimeError("empty audio or no word marks")
                with open(base + ".mp3", "wb") as f:
                    f.write(audio)
                json.dump({"voice": voice, "rate": rate, "pitch": pitch, "text": text, "marks": marks},
                          open(base + ".json", "w"), indent=0)
                return
            except Exception as e:   # network hiccups, throttling, 'No audio was received'
                last = e
                wait = 1.5 * 2 ** i
                print(f"  retry {i + 1}/{attempts} {voice} {text[:40]!r}: {e!r} (wait {wait:.0f}s)",
                      file=sys.stderr)
                await asyncio.sleep(wait)
        raise RuntimeError(f"Edge TTS failed for {voice} {text!r}: {last!r}")


def synth_all(requests, force=False, jobs=6):
    """requests: iterable of (voice, rate, pitch, text). Fills the cache; returns {req: base_path}."""
    os.makedirs(CACHE, exist_ok=True)
    paths, todo = {}, []
    for r in set(requests):
        base = os.path.join(CACHE, _key(*r))
        paths[r] = base
        if force or not (os.path.exists(base + ".mp3") and os.path.exists(base + ".json")):
            todo.append((r, base))
    if todo:
        edge_tts = _edge()
        print(f"synthesizing {len(todo)} clips with Edge TTS ...")

        async def run():
            sem = asyncio.Semaphore(jobs)
            await asyncio.gather(*[_synth_one(edge_tts, *r, base, sem) for r, base in todo])
        asyncio.run(run())
    return paths


def load_clip(base, sr):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", base + ".mp3", "-ac", "1", "-ar", str(sr),
                          "-f", "s16le", "-"], check=True, capture_output=True).stdout
    data = np.frombuffer(raw, dtype="<i2").astype(np.float32) / 32768.0
    marks = json.load(open(base + ".json"))["marks"]
    return data, marks


def trim_marks(data, marks, sr, lead=0.05, tail=0.12, thr_db=-42):
    """Cut leading/trailing silence by energy (10 ms windows, thr_db below the loudest window), never
    cutting into a word mark; keep `lead`/`tail` of room so onsets and breathy decays survive."""
    win = int(sr * 0.01)
    n = len(data) // win
    rms = np.sqrt((data[: n * win].reshape(n, win) ** 2).mean(axis=1) + 1e-12)
    idx = np.where(rms > rms.max() * 10 ** (thr_db / 20))[0]
    on, off = (idx[0] * win / sr, (idx[-1] + 1) * win / sr) if len(idx) else (0, len(data) / sr)
    on = min(on, marks[0]["t"]) if marks else on
    off = max(off, marks[-1]["t"] + marks[-1]["d"]) if marks else off
    a = max(0, int((on - lead) * sr))
    b = min(len(data), int((off + tail) * sr))
    out = data[a:b].copy()
    f = min(len(out) // 4, int(0.01 * sr))
    if f > 0:
        out[:f] *= np.linspace(0, 1, f)
        out[-f:] *= np.linspace(1, 0, f)
    shift = a / sr
    return out, [{**m, "t": m["t"] - shift} for m in marks]


def tighten_pauses(data, marks, sr, max_pause=0.5, keep=0.42, xf=0.012):
    """Shorten silences between words longer than `max_pause` down to `keep` seconds (Edge's slowed
    voices pause ~0.9 s at full stops, which sounds like dead air in a cartoon). The cut is taken from
    the middle of the gap with a short crossfade; the marks after it move earlier."""
    cuts = []
    for a, b in zip(marks, marks[1:]):
        g0, g1 = a["t"] + a["d"], b["t"]
        if g1 - g0 > max_pause:
            excess = (g1 - g0) - keep
            mid = (g0 + g1) / 2
            cuts.append((mid - excess / 2, mid + excess / 2))
    if not cuts:
        return data, marks
    x = int(xf * sr)
    bounds = [0] + [int(c * sr) for cut in cuts for c in cut] + [len(data)]
    pieces = [data[bounds[i]:bounds[i + 1]] for i in range(0, len(bounds), 2)]
    out = pieces[0].copy()
    fo, fi = np.linspace(1, 0, x), np.linspace(0, 1, x)
    for p in pieces[1:]:
        out[-x:] = out[-x:] * fo + p[:x] * fi       # crossfade join (each join removes x samples)
        out = np.concatenate([out, p[x:]])
    new = []
    for m in marks:
        done = [c for c in cuts if c[1] <= m["t"]]
        new.append({**m, "t": m["t"] - sum(c1 - c0 for c0, c1 in done) - len(done) * x / sr})
    return out, new


# ------------------------------------------------------------------ word alignment
def _norm(w):
    return re.sub(r"[^\w]", "", w.lower())


def align_words(display_text, marks, pronounce, line_end):
    """Map TTS WordBoundary marks onto the display words (text.split()).

    Respellings are undone first (Mooey -> mui), then difflib matches the token sequences; words the
    TTS spoke differently (2010 -> "twenty ten", S.E.A. -> Sea) take the span of the marks between
    their matched neighbours. Returns ([[word, start, end], ...], n_interpolated)."""
    back = {_norm(v): _norm(k) for k, v in pronounce.items()}
    words = display_text.split()
    dn = [_norm(w) for w in words]
    mn = [back.get(_norm(m["w"]), _norm(m["w"])) for m in marks]
    sm = difflib.SequenceMatcher(a=dn, b=mn, autojunk=False)
    span = [None] * len(words)   # (first_mark, last_mark)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            for k in range(i2 - i1):
                span[i1 + k] = (j1 + k, j1 + k)
        elif tag == "replace" and j2 > j1:
            # spread the replaced marks over the replaced words in order
            nw, nm = i2 - i1, j2 - j1
            for k in range(nw):
                s = j1 + (k * nm) // nw
                e = j1 + max((k + 1) * nm // nw - 1, (k * nm) // nw)
                span[i1 + k] = (s, e)
    out, miss = [], 0
    for i, w in enumerate(words):
        if span[i] is not None:
            s, e = span[i]
            out.append([w, marks[s]["t"], marks[e]["t"] + marks[e]["d"]])
        else:
            out.append([w, None, None])
            if dn[i]:
                miss += 1
    # fill gaps (pure punctuation tokens like "—", or unmatched words) by interpolation
    for i, rec in enumerate(out):
        if rec[1] is None:
            prev = next((out[k][2] for k in range(i - 1, -1, -1) if out[k][1] is not None), 0.0)
            nxt = next((out[k][1] for k in range(i + 1, len(out)) if out[k][1] is not None), line_end)
            rec[1], rec[2] = prev, max(prev, nxt)
    return [[w, round(s, 3), round(e, 3)] for w, s, e in out], miss


# ------------------------------------------------------------------ per-line build
def voice_params(cfg, key, line=None):
    ed = cfg["edge"]
    v = ed["voices"][key]
    rate = v.get("rate", 0)
    pitch = v.get("pitch", 0)
    if line is not None:
        ov = ed.get("lines", {}).get(line["id"], {})
        if "rate" in ov:
            rate = ov["rate"]
        elif line.get("length_scale"):
            # length_scale > 1 = slower; apply on top of the voice's own rate
            rate = ((1 + rate / 100.0) / line["length_scale"] - 1) * 100
        pitch = ov.get("pitch", pitch)
    return v["voice"], _fmt_rate(rate), _fmt_pitch(pitch)


def tts_text(line, cfg):
    ov = cfg["edge"].get("lines", {}).get(line["id"], {})
    if "tts_text" in ov:
        line = {**line, "tts_text": ov["tts_text"]}
    return tts_text_for(line, {"pronounce": cfg["edge"].get("pronounce", cfg.get("pronounce", {}))})


def requests_for(line, cfg):
    text = tts_text(line, cfg)
    v = cfg["edge"]["voices"][line["speaker"]]
    if "layers" in v:
        return [voice_params(cfg, k, line) + (text,) for k, _ in v["layers"]]
    return [voice_params(cfg, line["speaker"], line) + (text,)]


def pause_limits(ed, key):
    """(max_pause, keep_pause) for a voice: per-voice keys override the edge-wide defaults."""
    v = ed["voices"][key]
    return v.get("max_pause", ed.get("max_pause", 0.5)), v.get("keep_pause", ed.get("keep_pause", 0.42))


def build_line(line, cfg, sr, paths):
    ed = cfg["edge"]
    v = ed["voices"][line["speaker"]]
    text = tts_text(line, cfg)
    target, peak_db = ed.get("target_rms_dbfs", cfg["target_rms_dbfs"]), ed.get("peak_dbfs", cfg["peak_dbfs"])
    if "layers" in v:
        parts, marks0 = [], None
        for key, off_ms in v["layers"]:
            d, m = load_clip(paths[voice_params(cfg, key, line) + (text,)], sr)
            d, m = trim_marks(d, m, sr, lead=0.0, tail=0.12)
            d, m = tighten_pauses(d, m, sr, *pause_limits(ed, key))
            d = normalize(d, target, 0.0)
            parts.append((int(off_ms / 1000 * sr), d))
            if marks0 is None:          # word marks follow the first (offset 0) layer
                marks0 = [{**x, "t": x["t"] + off_ms / 1000} for x in m]
        n = max(o + len(d) for o, d in parts)
        data = np.zeros(n, np.float32)
        for o, d in parts:
            data[o:o + len(d)] += d
        marks = marks0
        data, marks = trim_marks(data, marks, sr)
    else:
        data, marks = load_clip(paths[voice_params(cfg, line["speaker"], line) + (text,)], sr)
        data, marks = trim_marks(data, marks, sr)
        data, marks = tighten_pauses(data, marks, sr, *pause_limits(ed, line["speaker"]))
    data = normalize(data, target, peak_db)
    write_wav(os.path.join(BUILD, line["id"] + ".wav"), data, sr)
    dur = len(data) / sr
    words, miss = align_words(line["text"], marks, ed.get("pronounce", {}), dur)
    return {
        "id": line["id"], "scene": line["scene"], "speaker": line["speaker"], "text": line["text"],
        "duration": round(dur, 3), "peak": round(float(np.abs(data).max()), 3),
        "rms": round(float(np.sqrt((data ** 2).mean())), 4),
        "envelope": envelope(data, sr), "words": words, "_miss": miss,
        "_spoken": [m["w"] for m in marks],
    }


# ------------------------------------------------------------------ samples
def write_samples(cfg, lines, sr):
    """build/audio/samples.mp3: one line per speaker (first line with >= 3 words, else the longest),
    0.5 s apart, plus the narrator alternates listed in edge.audition."""
    from build_audio import read_wav
    picks, seen = [], set()
    for sp in cfg["edge"]["sample_order"]:
        cands = [l for l in lines if l["speaker"] == sp and not l.get("role")]
        if not cands:
            continue
        good = [l for l in cands if len(l["text"].split()) >= 3]
        picks.append((good or sorted(cands, key=lambda l: -len(l["text"])))[0])
    gap = np.zeros(int(0.5 * sr), np.float32)
    chunks = []
    for l in picks:
        chunks += [read_wav(os.path.join(BUILD, l["id"] + ".wav"))[0], gap]
    alts = cfg["edge"].get("audition", [])
    if alts:
        reqs = [(a["voice"], _fmt_rate(a.get("rate", 0)), _fmt_pitch(a.get("pitch", 0)), a["text"]) for a in alts]
        paths = synth_all(reqs)
        for r in reqs:
            d, m = load_clip(paths[r], sr)
            d, _ = trim_marks(d, m, sr)
            chunks += [normalize(d, cfg["edge"]["target_rms_dbfs"], cfg["edge"]["peak_dbfs"]), gap]
    wav = os.path.join(CACHE, "samples.wav")
    write_wav(wav, np.concatenate(chunks), sr)
    out = os.path.join(BUILD, "samples.mp3")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", wav, "-b:a", "128k", out], check=True)
    order = [f"{l['speaker']} ({l['id']})" for l in picks] + [f"ALT {a['label']}" for a in alts]
    print("samples.mp3:", " | ".join(order))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scene", type=int)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--jobs", type=int, default=6)
    ap.add_argument("--samples", action="store_true")
    args = ap.parse_args()
    cfg = json.load(open(os.path.join(HERE, "voices.json")))
    sr = cfg["sample_rate"]
    lines = json.load(open(os.path.join(ROOT, "script_lines.json")))
    todo = [l for l in lines if args.scene is None or l["scene"] == args.scene]
    paths = synth_all([r for l in todo for r in requests_for(l, cfg)], args.force, args.jobs)

    man_path = os.path.join(BUILD, "manifest.json")
    manifest = json.load(open(man_path)) if os.path.exists(man_path) else {}
    manifest.pop("_meta", None)
    order = {l["id"]: i for i, l in enumerate(lines)}
    for k in [k for k in manifest if k not in order]:   # lines deleted from the script
        manifest.pop(k)
        p = os.path.join(BUILD, k + ".wav")
        if os.path.exists(p):
            os.remove(p)

    problems = []
    for l in todo:
        r = build_line(l, cfg, sr, paths)
        manifest[r["id"]] = {k: r[k] for k in ("scene", "speaker", "text", "duration", "peak", "rms",
                                                "envelope", "words")}
        manifest[r["id"]]["tts"] = "edge"
        nwords = len([w for w in r["text"].split() if _norm(w)])
        wps = nwords / max(r["duration"], 0.01)
        if r["rms"] < 0.01:
            problems.append(f"{r['id']}: near-silent (rms {r['rms']})")
        if r["peak"] >= 0.999:
            problems.append(f"{r['id']}: clipped")
        if wps > 4.8 or (wps < 1.0 and nwords > 1):
            problems.append(f"{r['id']}: odd speed {wps:.2f} words/s ({r['duration']}s, {nwords} words)")
        if r["_miss"]:
            problems.append(f"{r['id']}: {r['_miss']} word(s) without a direct TTS mark "
                            f"(spoken: {' '.join(r['_spoken'])})")
    manifest = dict(sorted(manifest.items(), key=lambda kv: order.get(kv[0], 1e9)))
    meta = {"sample_rate": sr, "fps": FPS, "tts": "edge",
            "total_speech_seconds": round(sum(m["duration"] for m in manifest.values()), 2)}
    json.dump({"_meta": meta, **manifest}, open(man_path, "w"), indent=0)
    print(f"built {len(todo)} lines; total speech {meta['total_speech_seconds']}s")
    for p in problems:
        print("NOTE", p)
    if args.samples:
        write_samples(cfg, lines, sr)


if __name__ == "__main__":
    main()
