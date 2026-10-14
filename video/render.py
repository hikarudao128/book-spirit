#!/usr/bin/env python3
"""Render scenes to video.

  python3 video/render.py --scene 1             # build/scenes/scene01.mp4 + scene01_av.mp4
  python3 video/render.py --scene all           # every scene, then out/full.mp4
  python3 video/render.py --scene 1 --preview   # 640x360 @ 12 fps, no supersampling -> scene01_preview.mp4
  python3 video/render.py --scene 1 --still 3.5,10,14.2   # PNGs in build/stills/
  python3 video/render.py --scene 1 --audio-only          # just rebuild scene01.wav + mux

Requires build/timeline.json (python3 video/timeline.py) and build/audio/*.wav.
"""
import argparse
import importlib
import json
import math
import os
import subprocess
import sys
import time
import wave
from multiprocessing import Pool

import numpy as np

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

from lib.context import SceneContext  # noqa: E402
from lib import sfx  # noqa: E402

BUILD = os.path.join(ROOT, "build")
W, H = 1280, 720

_MOD = None
_CTX = None
_OUT = None


def scene_module(n):
    return importlib.import_module(f"scenes.scene{n:02d}")


def _init(scene, preview):
    global _MOD, _CTX, _OUT
    _MOD = scene_module(scene)
    _CTX = SceneContext(scene, preview=preview)
    _OUT = (640, 360) if preview else (W, H)


def _frame_bytes(t):
    img = _MOD.render_frame(t, _CTX)
    if img.size != _OUT:
        img = img.resize(_OUT)
    if img.mode != "RGB":
        img = img.convert("RGB")
    return img.tobytes()


def n_frames(duration, fps):
    return int(round(duration * fps))


def render_video(scene, preview=False, jobs=4):
    ctx = SceneContext(scene, preview=preview)
    fps = 12 if preview else ctx.fps
    n = n_frames(ctx.duration, fps)
    times = [i / fps for i in range(n)]
    os.makedirs(os.path.join(BUILD, "scenes"), exist_ok=True)
    out = os.path.join(BUILD, "scenes", f"scene{scene:02d}{'_preview_v' if preview else ''}.mp4")
    size = (640, 360) if preview else (W, H)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{size[0]}x{size[1]}", "-r", str(fps), "-i", "-",
           "-c:v", "libx264", "-preset", "veryfast" if preview else "medium", "-crf", "20",
           "-pix_fmt", "yuv420p", out]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    t0 = time.time()
    if jobs > 1:
        with Pool(jobs, initializer=_init, initargs=(scene, preview)) as pool:
            for b in pool.imap(_frame_bytes, times, chunksize=4):
                ff.stdin.write(b)
    else:
        _init(scene, preview)
        for t in times:
            ff.stdin.write(_frame_bytes(t))
    ff.stdin.close()
    ff.wait()
    dt = time.time() - t0
    print(f"scene {scene}: {n} frames in {dt:.1f}s ({dt / max(n, 1) * 1000 * jobs:.0f} ms/frame/core) -> {out}")
    return out, n / fps


def _read_wav(path):
    with wave.open(path, "rb") as w:
        return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768.0, w.getframerate()


def build_scene_audio(scene, length_s):
    ctx = SceneContext(scene)
    man = json.load(open(os.path.join(BUILD, "audio", "manifest.json")))
    sr = man["_meta"]["sample_rate"]
    mix = np.zeros(int(math.ceil(length_s * sr)) + 1, np.float32)
    for l in ctx.lines:
        d, _ = _read_wav(os.path.join(BUILD, "audio", l.id + ".wav"))
        i = int(l.start * sr)
        d = d[: max(0, len(mix) - i)]
        mix[i:i + len(d)] += d
    mod = scene_module(scene)
    if hasattr(mod, "audio_cues"):
        for cue in mod.audio_cues(ctx):
            i, d = sfx.render_cue(cue, sr)
            d = d[: max(0, len(mix) - i)]
            mix[i:i + len(d)] += d
    mix = np.tanh(mix * 1.1) / np.tanh(1.1)    # gentle safety limiter
    mix = mix[: int(round(length_s * sr))]
    out = os.path.join(BUILD, "scenes", f"scene{scene:02d}.wav")
    with wave.open(out, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((np.clip(mix, -1, 1) * 32767).astype(np.int16).tobytes())
    return out


def mux(video, audio, out):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", video, "-i", audio, "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", out], check=True)
    return out


def render_still(scene, t):
    _init(scene, False)
    img = _MOD.render_frame(t, _CTX)
    os.makedirs(os.path.join(BUILD, "stills"), exist_ok=True)
    p = os.path.join(BUILD, "stills", f"scene{scene:02d}_t{t:05.2f}.png")
    img.save(p)
    print(p)
    return p


def concat_all(scenes):
    os.makedirs(os.path.join(ROOT, "out"), exist_ok=True)
    lst = os.path.join(BUILD, "scenes", "concat.txt")
    with open(lst, "w") as f:
        for s in scenes:
            f.write(f"file 'scene{s:02d}.mp4'\n")
    vid = os.path.join(BUILD, "scenes", "full_video.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", vid],
                   check=True)
    parts = [_read_wav(os.path.join(BUILD, "scenes", f"scene{s:02d}.wav")) for s in scenes]
    sr = parts[0][1]
    full = np.concatenate([p[0] for p in parts])
    wav = os.path.join(BUILD, "scenes", "full.wav")
    with wave.open(wav, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((full * 32767).astype(np.int16).tobytes())
    out = mux(vid, wav, os.path.join(ROOT, "out", "full.mp4"))
    print("->", out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scene", required=True, help="scene number or 'all'")
    ap.add_argument("--preview", action="store_true")
    ap.add_argument("--still", help="comma-separated times (s) to dump as PNG")
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--audio-only", action="store_true")
    args = ap.parse_args()
    tl = json.load(open(os.path.join(BUILD, "timeline.json")))
    scenes = sorted(int(k) for k in tl["scenes"]) if args.scene == "all" else [int(args.scene)]
    for s in scenes:
        if args.still:
            for t in args.still.split(","):
                render_still(s, float(t))
            continue
        fps = 12 if args.preview else tl["fps"]
        length = n_frames(tl["scenes"][str(s)]["duration"], fps) / fps
        if args.audio_only:
            vid = os.path.join(BUILD, "scenes", f"scene{s:02d}.mp4")
        else:
            vid, length = render_video(s, args.preview, args.jobs)
        wav = build_scene_audio(s, length)
        out = os.path.join(BUILD, "scenes", f"scene{s:02d}{'_preview' if args.preview else '_av'}.mp4")
        mux(vid, wav, out)
        print("->", out)
    if args.scene == "all" and not args.still and not args.preview:
        concat_all(scenes)


if __name__ == "__main__":
    main()
