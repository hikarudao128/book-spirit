"""Scene 11 - Ending (callback to scene 1).

Beats (all from ctx):
  the scene-1 alley, same composition, but washed-out: Mui's step is empty, the dog sits by it.
  "And so, Mui and his friends grew up..."  four grown-ups trudge to work in single file, briefcases,
      bored faces (Hai still tall with his band-aid, Ti with her bow and gap teeth, Tun's big eyes, Old Mui)
  "...became sensible adults"  SENSIBLE ADULTS label;  "...never did anything silly ever again."  SILLINESS: 0
  (pause) the others walk out of frame; Old Mui stops, looks at the dog. Camera eases in.
  OLD MUI "...Banana."  turned to the dog, eyes on it, tiny smile; the dog wags, colour comes back into the street
  "For about forty years."  a kite climbs over the rooftops behind him
  fade to black, title card "Give me a ticket to childhood." held through the tail with a soft sting
"""
import math

from lib import palette as P
from lib.backgrounds import draw_alley, draw_kite, draw_sky, draw_sun
from lib.characters import draw_character, draw_dog
from lib.core import INK, clamp, ease_in_out, ease_out, ease_out_back, lerp, pop, progress
from lib.extra_s8_11 import blink, draw_briefcase, draw_grown
from lib.fx import desaturate, fade
from lib.text import label

STEP_X = 1100
GROUND = 560
WALK_Y = GROUND + 120
GS = 1.08                    # grown-ups: ~325 px (Old Mui), the scale of the scene-1 adults vs the alley
DOG_X = 1262
STOP_X = 1060
ORDER = (("HAI", 600), ("TI", 420), ("TUN", 240), ("MUI", 0))      # offset ahead of Mui


def beats(ctx):
    l1, l2, l3 = ctx.line(0), ctx.line(1), ctx.line(2)
    b = dict(l1=l1, l2=l2, l3=l3)
    b["sensible"] = ctx.find_word(l1.id, "sensible")
    b["silly"] = ctx.find_word(l1.id, "silly")
    b["stop"] = l1.end + 0.25
    b["look"] = b["stop"] + 0.35
    b["zoom0"] = l1.end + 0.1
    b["banana"] = l2.start
    b["smile"] = l2.start + 0.1
    b["forty"] = l3.start
    b["fade"] = l3.end + 0.35
    b["title"] = b["fade"] + 0.9
    return b


def audio_cues(ctx):
    b = beats(ctx)
    return [{"sfx": "music_sad", "start": 0.0, "dur": b["banana"] - 0.3, "gain": 0.12, "fade_out": 0.8},
            {"sfx": "pop", "start": b["sensible"], "gain": 0.2},
            {"sfx": "tick", "start": b["silly"] + 0.1, "gain": 0.3},
            {"sfx": "boing", "start": b["banana"] + 0.9, "gain": 0.12},
            {"sfx": "whoosh", "start": b["forty"] - 0.2, "gain": 0.12},
            {"sfx": "ding", "start": b["title"], "gain": 0.22},
            {"sfx": "music_bed", "start": b["title"] - 0.3, "dur": ctx.duration - b["title"] + 0.3, "gain": 0.14,
             "fade_out": 1.5}]


def _mui_x(t, b):
    """Old Mui's x: steady walk, easing to a stop near the dog."""
    v = (STOP_X + 160) / (b["stop"] + 0.5)          # px/s so he would reach STOP_X a bit after `stop`
    x_lin = -160 + v * t
    if t < b["stop"] - 0.6:
        return x_lin
    # smooth deceleration into STOP_X
    t0 = b["stop"] - 0.6
    x0 = -160 + v * t0
    u = progress(t, t0, 1.2)
    return lerp(x0, STOP_X, 1 - (1 - u) ** 2)


def _camera(t, b):
    pan = lerp(560, 760, ease_in_out(clamp(t / b["zoom0"])))
    p = ease_in_out(progress(t, b["zoom0"], 1.6))
    return lerp(pan, 1150, p), lerp(360, 452, p), lerp(1.0, 1.4, p)


def render_frame(t, ctx):
    b = beats(ctx)
    if t >= b["title"] - 0.05:
        return _title(ctx, t, b)
    cv = ctx.canvas(P.SKY_BOTTOM)
    draw_sky(cv, t, sun=None)
    cx, cy, z = _camera(t, b)
    if z < 1.2:
        draw_sun(cv, 1080 - (cx - 560) * 0.3, 112, 58, t)
    with cv.camera(cx, cy, z):
        draw_alley(cv, t, step_x=STEP_X, ground_y=GROUND)
        # a kite climbs over the rooftops on "forty years"
        kp = ease_out_back(progress(t, b["forty"], 1.6), 1.1)
        if kp > 0.01:
            draw_kite(cv, 1290, lerp(GROUND - 120, 320, kp), 30, P.ACCENT, t, tail=4, seed=2, string_to=(1560, 900))
        # the dog by the empty step
        wag = t >= b["banana"] + 0.4
        draw_dog(cv, DOG_X, GROUND + 50, 0.75, flip=True, pose="sit" if not wag else "wag", t=t if wag else 0.0,
                 expression="happy" if wag else "neutral")
        mx = _mui_x(t, b)
        walking_mui = t < b["stop"] + 0.4
        for nm, off in sorted(ORDER, key=lambda o: -o[1]):
            if nm == "MUI":
                continue
            x = mx + off if t < b["stop"] - 0.6 else (-160 + (STOP_X + 160) / (b["stop"] + 0.5) * t) + off \
                + 260 * max(0.0, t - b["stop"] + 0.6) ** 1.5      # they keep going (and hurry off)
            if x > 2100:
                continue
            a = draw_grown(cv, nm, x, WALK_Y + 4, GS, pose="walk", t=t + off * 0.003, expression="bored",
                           look=(0.5, 0.3))
            draw_briefcase(cv, *_w(a["hand_r"], cx, cy, z), 0.9)
        # Old Mui
        look = (0.5, 0.3)
        lp = ease_in_out(progress(t, b["look"], 0.5))
        if lp > 0:
            look = (lerp(0.5, 1.0, lp), lerp(0.3, 0.6, lp))
        expr = "bored"
        if t >= b["smile"]:
            expr = "happy"          # open eyes, pupils on the dog: he says "...Banana." TO the dog, not to us
        a = draw_grown(cv, "MUI", mx, WALK_Y + 4, GS, pose="walk" if walking_mui else "stand",
                       t=t, expression=expr, look=look, mouth_open=ctx.mouth("OLD MUI", t),
                       blink=blink(t, 5) if t < b["look"] else 0)
        draw_briefcase(cv, *_w(a["hand_r"], cx, cy, z), 0.9)
    # labels
    sens = pop(t, b["sensible"] - 0.05, 0.35) * (1 - progress(t, b["stop"], 0.3))
    if sens > 0.01:
        label(cv, 330, 130, "SENSIBLE ADULTS", 30, bg=P.WHITE, scale=sens, rot=-3)
    sil = pop(t, b["silly"], 0.3) * (1 - progress(t, b["stop"], 0.3))
    if sil > 0.01:
        label(cv, 330, 196, "SILLINESS: 0", 24, fill=P.WHITE, bg=INK, scale=sil, rot=2)
    img = cv.finish()
    grey = 0.55 * (1 - ease_in_out(progress(t, b["smile"], 1.6)))
    img = desaturate(img, grey)
    f = ease_in_out(progress(t, b["fade"], 0.9))
    if f > 0:
        img = fade(img, f)
    return img


def _w(p, cx, cy, z):
    """Screen anchor -> world coords under the current camera."""
    return ((p[0] - 640) / z + cx, (p[1] - 360) / z + cy)


def _title(ctx, t, b):
    cv = ctx.canvas((12, 10, 14))
    a = ease_out(progress(t, b["title"], 1.2))
    col = tuple(int(lerp(12, c, a)) for c in (250, 244, 228))
    s = 0.94 + 0.06 * a + 0.015 * progress(t, b["title"], ctx.duration - b["title"])
    with cv.at(640, 340, s):
        cv.text(0, 0, "Give me a ticket to childhood.", 52, col, "black")
    # a small ticket stub under the line
    ts = pop(t, b["title"] + 0.8, 0.5)
    if ts > 0.01:
        with cv.at(640, 440, ts, rot=-4):
            cv.rect(-80, -26, 80, 26, fill=(255, 248, 230), radius=5, ow=2.4, outline=(250, 244, 228))
            cv.line([(40, -22), (40, 22)], (200, 120, 100), 2)
            cv.text(-18, 1, "VÉ", 24, P.ACCENT, "black")
            cv.text(60, 1, "★", 18, P.ACCENT, "bold")
    return cv.finish()
