"""Scene 1 - Opening (build up, then knock down).

Beats (times come from ctx, never hard-coded to audio):
  wide alley, music bed, kids flying kites, vendor + dog pass
  "Sunshine." sun pulses / "Kites." kites rise / "Street food." vendor steam
  "No deadlines, no rent, no emails." -> three icons pop and get slashed
  after l03: record scratch, music cuts, snap-zoom onto Mui on the step
  "Meet Mui." freeze-frame + name tag; Mui says "Life is boring."
  "Thank you, Mui." -> Mui slowly looks at camera; a kite crashes next to him. He does not care.
"""
import math

from lib import palette as P
from lib.backgrounds import draw_alley, draw_kite, draw_sky, draw_sun
from lib.characters import draw_character, draw_dog, draw_vendor
from lib.core import INK, clamp, ease_in_out, ease_out, ease_out_back, lerp, pop, progress
from lib.fx import flash, freeze_frame
from lib.text import label, name_tag

STEP_X = 1100
GROUND = 560
KIDS = [("HAI", 330, 0.95, P.ACCENT), ("TUN", 500, 0.95, P.ACCENT2), ("TI", 650, 0.95, (250, 170, 40))]
KITE_POS = [(450, 185), (610, 110), (800, 200)]
STRING = (70, 60, 60)


def _stoop(cv):
    """Two-step concrete stoop with visible treads (so sitting on it reads), centred on STEP_X."""
    from lib.core import lerp_color
    base = GROUND + 44
    top_c = lerp_color(P.STEP, (255, 255, 255), 0.35)
    face_c = P.STEP
    soft = (120, 100, 90)
    # lower step: tread (top surface) + riser
    cv.poly([(STEP_X - 130, base - 26), (STEP_X + 130, base - 26), (STEP_X + 118, base - 36),
             (STEP_X - 118, base - 36)], fill=top_c, outline=soft, ow=2.4)
    cv.rect(STEP_X - 130, base - 26, STEP_X + 130, base, fill=face_c, outline=soft, ow=2.6)
    # upper step
    cv.poly([(STEP_X - 104, base - 66), (STEP_X + 104, base - 66), (STEP_X + 94, base - 80),
             (STEP_X - 94, base - 80)], fill=top_c, outline=soft, ow=2.4)
    cv.rect(STEP_X - 104, base - 66, STEP_X + 104, base - 36, fill=lerp_color(face_c, (255, 255, 255), 0.12),
            outline=soft, ow=2.6)
    return base - 72, base - 31          # seat y (middle of the upper tread), lower tread y


def beats(ctx):
    """Every timing of the scene in one place, derived from the timeline."""
    l1, l2, l3, l4, l5, l6 = (ctx.line(i) for i in range(6))
    b = dict(
        sunshine=ctx.find_word(l1.id, "Sunshine"),
        kites=ctx.find_word(l1.id, "Kites"),
        food=ctx.find_word(l1.id, "Street"),
        no1=ctx.find_word(l2.id, "deadlines"), no2=ctx.find_word(l2.id, "rent"),
        no3=ctx.find_word(l2.id, "emails"),
        icons_out=l3.start + 0.2,
        cut=l3.end + 0.25,                     # music stops, zoom starts
        meet=ctx.find_word(l4.id, "Mui"),
        tag_out=l5.start - 0.3,
        mui=l5, thank=l6,
        look=l6.start + 0.35,
        kite_fall=l6.end + 0.2,
    )
    b["zoom_end"] = b["cut"] + 0.55
    b["kite_land"] = b["kite_fall"] + 1.0
    return b


def audio_cues(ctx):
    b = beats(ctx)
    return [
        {"sfx": "music_bed", "start": 0.0, "dur": b["cut"], "gain": 0.16, "fade_out": 0.03},
        {"sfx": "record_scratch", "start": b["cut"] - 0.05, "gain": 0.35},
        {"sfx": "whoosh", "start": b["cut"], "gain": 0.22},
        {"sfx": "pop", "start": b["no1"], "gain": 0.25},
        {"sfx": "pop", "start": b["no2"], "gain": 0.25},
        {"sfx": "pop", "start": b["no3"], "gain": 0.25},
        {"sfx": "shutter", "start": b["meet"], "gain": 0.45},
        {"sfx": "thud", "start": b["kite_land"], "gain": 0.4},
    ]


# ------------------------------------------------------------------ helpers
def _icon(cv, kind, x, y, s, slash):
    if s <= 0.01:
        return
    with cv.at(x, y, s):
        cv.rect(-62, -62, 62, 62, fill=P.WHITE, radius=18, ow=4)
        if kind == "deadline":
            cv.rect(-34, -30, 34, 34, fill=P.WHITE, ow=3)
            cv.rect(-34, -30, 34, -12, fill=P.ACCENT, ow=3)
            cv.text(0, 12, "31", 26, INK, "black")
            cv.ellipse(0, 12, 22, 16, fill=None, outline=P.ACCENT, ow=3)
        elif kind == "rent":
            cv.poly([(-36, -4), (0, -36), (36, -4)], fill=P.ROOF, ow=3)
            cv.rect(-28, -4, 28, 34, fill=P.HOUSE_COLORS[0], ow=3)
            cv.text(0, 16, "$", 30, P.LEAF_DARK, "black")
        else:
            cv.rect(-38, -24, 38, 28, fill=P.PAPER, ow=3)
            cv.line([(-38, -24), (0, 6), (38, -24)], INK, 3)
            cv.circle(30, -24, 12, fill=P.ACCENT, ow=2.5)
            cv.text(30, -24, "9", 14, P.WHITE, "black")
        if slash > 0:
            r = 70
            cv.circle(0, 0, r, fill=None, outline=P.ACCENT, ow=9 * slash)
            a = math.radians(-45)
            ex, ey = math.cos(a + math.pi) * r * 0.7, -math.sin(a + math.pi) * r * 0.7
            cv.line([(-ex * slash, -ey * slash), (ex * slash, ey * slash)], P.ACCENT, 9)
    names = {"deadline": "DEADLINES", "rent": "RENT", "email": "EMAILS"}
    label(cv, x, y + 92 * s, names[kind], 22, scale=s, bg=P.HIGHLIGHT)


def _camera(t, b):
    pan = lerp(560, 700, ease_in_out(clamp(t / b["cut"])))
    wide = (pan, 360, 1.0)
    close = (STEP_X - 30, 470, 2.6)
    p = ease_in_out(progress(t, b["cut"], b["zoom_end"] - b["cut"]))
    p = 1 - (1 - p) ** 3 if p < 1 else 1
    cx = lerp(wide[0], close[0], p)
    cy = lerp(wide[1], close[1], p)
    z = lerp(wide[2], close[2], p)
    # gentle push-in during the close-up, and a tiny hold-still on the deadpan
    z *= 1 + 0.04 * ease_in_out(progress(t, b["zoom_end"], 8))
    return cx, cy, z


# ------------------------------------------------------------------ frame
def render_frame(t, ctx):
    b = beats(ctx)
    cv = ctx.canvas(P.SKY_BOTTOM)
    zoomed = progress(t, b["cut"], b["zoom_end"] - b["cut"])
    sun_pulse = 1 + 0.18 * math.sin(math.pi * progress(t, b["sunshine"], 0.6))
    draw_sky(cv, t, sun=None)
    if zoomed < 1:
        with cv.at(0, 0, 1):
            draw_sun(cv, 1080, 112, 58 * sun_pulse, t)

    cx, cy, z = _camera(t, b)
    with cv.camera(cx, cy, z):
        draw_alley(cv, t, ground_y=GROUND)
        seat_y, _ = _stoop(cv)

        # kites rise on "Kites."
        rise = ease_out_back(progress(t, b["kites"] - 0.3, 1.1), 1.2)
        kid_hands = {}
        # vendor walks behind the kids
        vx = lerp(-260, 1720, (t - 0.3) / (b["cut"] - 0.3))
        draw_vendor(cv, vx, GROUND + 52, 0.55, t=t, steam=t > b["food"] - 0.5)

        happy_jump = progress(t, b["no1"], 0.01) * (1 - progress(t, b["cut"], 0.01))
        for i, (nm, x, sc, col) in enumerate(KIDS):
            jump = -abs(math.sin(t * 5 + i)) * 10 * happy_jump
            a = draw_character(cv, nm, x, GROUND + 120 + jump, sc, pose="point", t=t + i,
                               expression="happy", look=(0.3, -0.8), mouth_open=0.0)
            kid_hands[nm] = a["hand_r"]
        for i, (nm, x, sc, col) in enumerate(KIDS):
            kx, ky = KITE_POS[i]
            ky = lerp(GROUND + 40, ky, rise)
            if rise > 0.02:
                hx, hy = kid_hands[nm]
                # hand anchor is in screen coords; convert back to world for the camera frame
                wx = (hx - 640) / z + cx
                wy = (hy - 360) / z + cy
                kx_s = kx + math.sin(t * 1.6 + i) * 8
                # string: from the kite's bridle down to the kid's fist, with a soft sag
                ex, ey = kx_s, ky + 40
                mx, my = (ex + wx) / 2 + 26, (ey + wy) / 2 + 30
                cv.curve((ex, ey), (mx, my), (wx, wy), STRING, 2.6)
                draw_kite(cv, kx, ky, 44, col, t, tail=4, seed=i)

        # Mui on the step, bored. Looks at camera on "Thank you, Mui."
        look_p = ease_in_out(progress(t, b["look"], 0.7))
        look = (lerp(-0.75, 0.0, look_p), lerp(0.35, 0.0, look_p))
        expr = "deadpan" if look_p > 0.5 else "bored"
        mouth = ctx.mouth("MUI", t)
        # faces left (toward the kids and the falling kite); sits on the upper tread, feet on the lower one
        draw_character(cv, "MUI", STEP_X + 14, seat_y, 1.0, pose="sit_chin_on_hand", t=t, expression=expr,
                       look=look, mouth_open=mouth, flip=True)

        # the dog trots over and sits by the step; stops wagging when the music dies
        dog_run = progress(t, 5.4, 4.6)
        if dog_run < 1:
            dx = lerp(-120, 1222, dog_run)
            if dog_run > 0.85:   # last stretch: up to the step
                pass
            draw_dog(cv, dx, GROUND + 150, 0.75, pose="run", t=t)
        else:
            draw_dog(cv, 1222, GROUND + 50, 0.75, flip=True, pose="sit" if t < b["cut"] else "stand",
                     t=t if t < b["cut"] else 0.0, expression="happy" if t < b["cut"] else "neutral")

        # a kite gives up and lands next to Mui
        kp = progress(t, b["kite_fall"], b["kite_land"] - b["kite_fall"])
        if kp > 0:
            fx = lerp(STEP_X - 90, STEP_X - 150, kp) + math.sin(kp * 9) * 22 * (1 - kp)
            fy = lerp(300, GROUND + 22, kp ** 1.6)
            with cv.at(fx, fy, 1, rot=lerp(0, 75, kp)):
                draw_kite(cv, 0, 0, 26, P.ACCENT, 0 if kp >= 1 else t, tail=3, seed=1)

    # "No deadlines, no rent, no emails." icons (screen space)
    out = 1 - ease_out(progress(t, b["icons_out"], 0.35))
    for kind, x, start in (("deadline", 360, b["no1"]), ("rent", 640, b["no2"]), ("email", 920, b["no3"])):
        s = pop(t, start - 0.1, 0.35) * out
        _icon(cv, kind, x, 230, s, ease_out(progress(t, start + 0.25, 0.25)))

    # name tag on "Meet Mui."
    name_tag(cv, t, b["meet"], "MUI", "AGE 8. NOT IMPRESSED.", x=70, y=600, dur=b["tag_out"] - b["meet"])

    img = cv.finish()
    fz = progress(t, b["meet"], 0.05) * (1 - progress(t, b["meet"] + 0.45, 0.2))
    if fz > 0:
        img = freeze_frame(img, fz)
        img = flash(img, 0.6 * (1 - progress(t, b["meet"], 0.18)))
    return img
