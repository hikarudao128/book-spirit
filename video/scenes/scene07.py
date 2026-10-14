"""Scene 7 - No More Jokes.

Tonal shift. No gags, no pops, no cuts. The alley from scene 1 at dusk, drained of colour. One child
sits alone on the doorstep (a silhouette against a dim lit doorway), head down. A bamboo cane leans
against the wall beside the door. The only motion is a very slow camera push, the wires barely
swaying and the child's breathing. The narration is left to breathe; very soft sad music under it.
"""
import math

from lib import palette as P
from lib.backgrounds import SOFT, draw_alley, draw_sky
from lib.characters import draw_character
from lib.core import ease_in_out, lerp, progress
from lib.extra_s5_7 import draw_stick, grade, to_world
from lib.fx import fade, vignette

STEP_X = 860
GROUND = 560
SIL = (36, 34, 42)              # silhouette tone
SILHOUETTE = {"skin": SIL, "shirt": SIL, "pants": SIL, "hair_color": SIL, "shoes": SIL, "cheeks": False}


def beats(ctx):
    first, last = ctx.line(0), ctx.line(len(ctx.lines) - 1)
    return dict(
        first=first, last=last,
        push_start=0.0,
        push_end=last.end + 0.5,
        punish=ctx.find_word(ctx.line(1).id, "punish"),
        stick=ctx.find_word(last.id, "stick"),
        fade_start=last.end + 0.6,
        end=ctx.duration,
    )


def audio_cues(ctx):
    b = beats(ctx)
    return [{"sfx": "music_sad", "start": 0.3, "dur": b["end"] - 0.3, "gain": 0.05, "fade_out": 1.6}]


def _camera(t, b):
    p = ease_in_out(progress(t, b["push_start"], b["push_end"] - b["push_start"]))
    return (lerp(720, STEP_X - 30, p), lerp(392, 452, p), lerp(1.0, 1.45, p))


def render_frame(t, ctx):
    b = beats(ctx)
    cv = ctx.canvas((150, 150, 158))
    draw_sky(cv, t * 0.2, top=(118, 112, 138), bottom=(214, 170, 150), sun=None, clouds=False)
    cx, cy, z = _camera(t, b)
    with cv.camera(cx, cy, z):
        draw_alley(cv, t * 0.3, step_x=STEP_X, ground_y=GROUND, kites=False)
        # a dim lit doorway behind the step
        dx0, dx1, dy0 = STEP_X - 62, STEP_X + 62, GROUND - 250
        cv.rect(dx0 - 12, dy0 - 12, dx1 + 12, GROUND - 26, fill=(110, 84, 64), outline=SOFT, ow=2.4)
        cv.rect(dx0, dy0, dx1, GROUND - 26, fill=(236, 196, 140), outline=SOFT, ow=2)
        cv.rect(dx0, GROUND - 120, dx1, GROUND - 26, fill=(214, 172, 120), outline=None)
        # the cane, leaning against the wall beside the door
        draw_stick(cv, STEP_X - 104, GROUND - 2, length=175, rot=9, color=(150, 112, 70), w=6)
        # the child, alone, head down, breathing
        breath = math.sin(t * 2 * math.pi / 4.2) * 1.2
        # chin on hand, turned toward the cane; a pure silhouette (no face features)
        a = draw_character(cv, "MUI", STEP_X, GROUND - 26 + breath * 0.3, 1.0, pose="sit_chin_on_hand",
                           expression="sad", look=(0, 1), blink=1.0, nod=5 + breath, t=0.0, flip=True,
                           lean=4, colors=SILHOUETTE)
        hx, hy = to_world(a["head"], (cx, cy, z))
        r = a["head_r"]
        cv.ellipse(hx, hy + r * 0.05, r * 0.86, r * 0.9, fill=SIL, outline=None)
    img = cv.finish()
    img = grade(img, sat=0.12, mul=(0.86, 0.87, 0.94), lift=(6, 6, 10))
    img = vignette(img, 0.7)
    f = progress(t, b["fade_start"], b["end"] - b["fade_start"])
    if f > 0:
        img = fade(img, 0.55 * ease_in_out(f), (20, 20, 26))
    return img
