#!/usr/bin/env python3
"""Build build/timeline.json from script_lines.json + build/audio/manifest.json + timeline_config.json.

All times are seconds relative to the start of each scene.
    python3 video/timeline.py
"""
import json
import os

ROOT = os.path.dirname(os.path.abspath(__file__))


def build():
    lines = json.load(open(os.path.join(ROOT, "script_lines.json")))
    man = json.load(open(os.path.join(ROOT, "build", "audio", "manifest.json")))
    cfg = json.load(open(os.path.join(ROOT, "timeline_config.json")))
    scenes = {}
    for l in lines:
        scenes.setdefault(l["scene"], []).append(l)
    out = {"fps": 24, "scenes": {}}
    total = 0.0
    for sc in sorted(scenes):
        pad = dict(cfg["defaults"])
        pad.update(cfg["scene_padding"].get(str(sc), {}))
        t = pad["lead_in"]
        items = []
        for i, l in enumerate(scenes[sc]):
            t += cfg["line_gap_before"].get(l["id"], 0.0)
            if l["id"] not in man:
                raise SystemExit(f"missing audio for {l['id']} - run audio/build_audio.py")
            dur = man[l["id"]]["duration"]
            items.append({
                "id": l["id"], "index": i, "speaker": l["speaker"], "role": l.get("role"),
                "text": l["text"], "start": round(t, 3), "end": round(t + dur, 3), "duration": dur,
            })
            t += dur + l.get("pause_after", 0.0)
        # last line's pause_after is replaced by the tail
        last = scenes[sc][-1]
        t = t - last.get("pause_after", 0.0) + pad["tail"]
        out["scenes"][str(sc)] = {"scene": sc, "duration": round(t, 3), "offset": round(total, 3),
                                  "lead_in": pad["lead_in"], "tail": pad["tail"], "lines": items}
        total += t
    out["total_duration"] = round(total, 3)
    path = os.path.join(ROOT, "build", "timeline.json")
    json.dump(out, open(path, "w"), indent=1)
    return out


if __name__ == "__main__":
    tl = build()
    for k, s in tl["scenes"].items():
        print(f"scene {k:>2}: {s['duration']:6.2f}s  ({len(s['lines'])} lines)")
    print(f"total: {tl['total_duration']:.2f}s = {tl['total_duration']/60:.2f} min")
