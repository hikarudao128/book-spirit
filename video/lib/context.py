"""SceneContext: what a scene's render_frame(t, ctx) gets to know about its timeline."""
import json
import os
import re
from dataclasses import dataclass, field

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # video/
FPS = 24
KID_SPEAKERS = ("MUI", "HAI", "TUN", "TI")


@dataclass
class Line:
    id: str
    index: int
    speaker: str
    text: str
    start: float
    end: float
    duration: float
    role: str = None
    envelope: list = field(default_factory=list, repr=False)

    def progress(self, t):
        """0..1 progress through this line (clamped)."""
        if self.duration <= 0:
            return 1.0
        return min(1.0, max(0.0, (t - self.start) / self.duration))

    def active(self, t):
        return self.start <= t < self.end


class SceneContext:
    """Timeline access for one scene. Times are seconds from the scene start.

    ctx.scene, ctx.duration, ctx.fps, ctx.lines (list[Line]), ctx.preview (bool)
    ctx.canvas(bg)                      -> new Canvas for the frame (use this, not Canvas())
    ctx.line("s01_l04") / ctx.line(3)  -> Line (by id or 0-based index)
    ctx.current(t)                      -> Line being spoken at t, or None
    ctx.speaking(speaker, t)            -> bool (speaker as in script: "MUI", "OLD MUI", ...)
    ctx.mouth(speaker, t)               -> 0..1 mouth openness from the line's RMS envelope
    ctx.words(line_id)                  -> [(word, start, end)] estimated word timings
    ctx.word_time(line_id, word_index)  -> start time of the n-th word (estimate)
    ctx.find_word(line_id, "Kites")     -> start time of first word containing that text
    """

    def __init__(self, scene, timeline=None, manifest=None, preview=False):
        timeline = timeline or json.load(open(os.path.join(ROOT, "build", "timeline.json")))
        manifest = manifest or json.load(open(os.path.join(ROOT, "build", "audio", "manifest.json")))
        sc = timeline["scenes"][str(scene)]
        self.scene = scene
        self.duration = sc["duration"]
        self.fps = timeline.get("fps", FPS)
        self.preview = preview
        self.ss = 1 if preview else 2          # supersampling used by ctx.canvas()
        self.lines = [Line(l["id"], l["index"], l["speaker"], l["text"], l["start"], l["end"], l["duration"],
                           l.get("role"), manifest.get(l["id"], {}).get("envelope", [])) for l in sc["lines"]]
        self._by_id = {l.id: l for l in self.lines}

    def canvas(self, bg=(255, 255, 255)):
        """A fresh Canvas for this frame (supersampled unless previewing)."""
        from .core import Canvas
        return Canvas(bg=bg, ss=self.ss)

    # -------------------------------------------------- lookup
    def line(self, key):
        return self.lines[key] if isinstance(key, int) else self._by_id[key]

    def current(self, t):
        for l in self.lines:
            if l.active(t):
                return l
        return None

    def lines_of(self, speaker):
        return [l for l in self.lines if l.speaker == speaker]

    def speaking(self, speaker, t, include_class=True):
        for l in self.lines:
            if l.active(t) and (l.speaker == speaker or
                                (include_class and l.speaker == "THE WHOLE CLASS" and speaker in KID_SPEAKERS)):
                return True
        return False

    def mouth(self, speaker, t, include_class=True):
        """Mouth openness 0..1 for `speaker` at time t (0 when not speaking)."""
        for l in self.lines:
            if not l.active(t):
                continue
            if l.speaker == speaker or (include_class and l.speaker == "THE WHOLE CLASS" and speaker in KID_SPEAKERS):
                env = l.envelope
                if not env:
                    return 0.5 + 0.5 * abs(((t - l.start) * 7.0) % 2 - 1)
                i = int((t - l.start) * self.fps)
                if 0 <= i < len(env):
                    # light smoothing with the next frame so the flap is not too jittery
                    j = min(i + 1, len(env) - 1)
                    return max(0.0, min(1.0, 0.7 * env[i] + 0.3 * env[j]))
                return 0.0
        return 0.0

    # -------------------------------------------------- word timing (estimates)
    def words(self, line_id):
        """Estimate word start/end by distributing the line duration over characters,
        with extra weight for punctuation pauses. Good enough for visual beats."""
        l = self.line(line_id)
        toks = l.text.split()
        weights = []
        for w in toks:
            wt = len(re.sub(r"[^\w']", "", w)) + 1.5
            if re.search(r"[.!?]$", w):
                wt += 5
            elif re.search(r"[,;:—]$", w) or w == "—":
                wt += 2.5
            weights.append(wt)
        total = sum(weights) or 1
        out, acc = [], 0.0
        for w, wt in zip(toks, weights):
            s = l.start + l.duration * acc / total
            acc += wt
            out.append((w, s, l.start + l.duration * acc / total))
        return out

    def word_time(self, line_id, idx):
        return self.words(line_id)[idx][1]

    def find_word(self, line_id, text, nth=0):
        hits = [s for w, s, e in self.words(line_id) if text.lower() in w.lower()]
        return hits[nth] if len(hits) > nth else self.line(line_id).start
