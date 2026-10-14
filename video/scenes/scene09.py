"""Scene 9 - The twist: Old Mui.

Beats (all from ctx):
  open on the scene-1 alley: little Mui bored on his step
  "But here's the twist."  a FAST-FORWARD badge snaps on
  "The person telling this story isn't eight."  time-lapse: sun whips across the sky, towers rise behind
      the tube houses, shop signs and motorbikes multiply, Mui cross-fades kid -> teen -> young man ->
      Old Mui while an AGE counter spins 8 -> 49
  "It's Mui, almost fifty..."  push-in + name tag OLD MUI (callback to scene 1)
  kitchen: his two kids at the table, instant noodles, faces lit by phones
  OLD MUI "What are you doing?" / HIS KID "Texting my girlfriend." (hearts float off the phone)
  OLD MUI "At your age?" (shocked)  ...  "Actually, at your age I was suing my dad." eyes slide away,
      a sepia flashback bubble of the plastic-stool courtroom (gavel bang on "dad")
  "Little Mui thought adults were boring." polaroid of little Mui;  "Old Mui has become one." the
      BORING ADULT label slams onto his chest
  "So who is this book really for?"  book cover pops on a sunburst
  "...anyone who was once a child. Which is everyone."  banner + the whole cast pops up + EVERYONE stamp
  "...a train with no ticket inspector."  golden-hour countryside, a little train chugs through, the
      inspector's booth is empty, cap swinging on its hook
  "You can go back to childhood any time you like."  the kids wave from the windows, Old Mui drives
  "Nobody checks."  push in on the empty booth. Deadpan hold.
"""
import math

from PIL import Image, ImageDraw, ImageOps

from lib import palette as P
from lib.backgrounds import (SOFT, draw_alley, draw_book_cover, draw_cloud, draw_dinner_table, draw_kitchen,
                             draw_plastic_stool, draw_sun)
from lib.characters import draw_character
from lib.core import INK, Canvas, clamp, ease_in_out, ease_out, ease_out_back, lerp, lerp_color, pop, progress
from lib.extra_s8_11 import (blink, draw_motorbike, draw_seated, draw_rails, draw_sign, draw_steam_puffs, draw_tower,
                             draw_train_car, sign_layout)
from lib.text import label, name_tag, text_width

STEP_X = 1100
GROUND = 560


def beats(ctx):
    L = [ctx.line(i) for i in range(11)]
    b = dict(L=L)
    b["ff"] = ctx.find_word(L[0].id, "twist")
    b["lapse0"] = ctx.find_word(L[0].id, "person") - 0.1
    b["lapse1"] = ctx.find_word(L[1].id, "almost")
    b["meet"] = ctx.find_word(L[1].id, "Mui")
    b["cut_kitchen"] = L[2].start - 0.45
    b["what"], b["text"], b["age"], b["actually"] = L[2].start, L[3].start, L[4].start, L[5].start
    b["bubble"] = ctx.find_word(L[5].id, "suing") - 0.25
    b["dad"] = ctx.find_word(L[5].id, "dad")
    b["little"] = L[6].start
    b["boring"] = ctx.find_word(L[6].id, "become") + 0.25
    b["cut_book"] = L[7].start - 0.15
    b["book"] = ctx.find_word(L[7].id, "book") - 0.1
    b["for"] = ctx.find_word(L[7].id, "for")
    b["anyone"] = ctx.find_word(L[8].id, "anyone")
    b["which"] = ctx.find_word(L[8].id, "Which")
    b["everyone"] = ctx.find_word(L[8].id, "everyone")
    b["cut_train"] = L[9].start - 0.3
    b["no_insp"] = ctx.find_word(L[9].id, "no")
    b["back"] = ctx.find_word(L[10].id, "back")
    b["nobody"] = ctx.find_word(L[10].id, "Nobody")
    return b


def audio_cues(ctx):
    b = beats(ctx)
    c = [{"sfx": "music_bed", "start": 0.0, "dur": b["ff"], "gain": 0.13, "fade_out": 0.05},
         {"sfx": "record_scratch", "start": b["ff"] - 0.05, "gain": 0.28},
         {"sfx": "whoosh", "start": b["lapse0"], "gain": 0.25},
         {"sfx": "whoosh", "start": b["lapse0"] + 0.9, "gain": 0.2},
         {"sfx": "whoosh", "start": b["lapse0"] + 1.8, "gain": 0.2},
         {"sfx": "ding", "start": b["lapse1"], "gain": 0.15},
         {"sfx": "shutter", "start": b["meet"], "gain": 0.4},
         {"sfx": "whoosh", "start": b["cut_kitchen"] - 0.05, "gain": 0.2},
         {"sfx": "pop", "start": b["text"] + 0.4, "gain": 0.15},
         {"sfx": "boing", "start": b["age"] + 0.1, "gain": 0.18},
         {"sfx": "pop", "start": b["bubble"], "gain": 0.25},
         {"sfx": "gavel", "start": b["dad"], "gain": 0.35},
         {"sfx": "shutter", "start": b["little"] + 0.05, "gain": 0.35},
         {"sfx": "slap", "start": b["boring"], "gain": 0.45},
         {"sfx": "whoosh", "start": b["cut_book"] - 0.1, "gain": 0.25},
         {"sfx": "music_bed", "start": b["cut_book"], "dur": ctx.duration - b["cut_book"], "gain": 0.12,
          "fade_out": 1.2},
         {"sfx": "pop", "start": b["book"], "gain": 0.3},
         {"sfx": "pop", "start": b["anyone"], "gain": 0.2},
         {"sfx": "thud", "start": b["everyone"] + 0.2, "gain": 0.35},
         {"sfx": "whoosh", "start": b["cut_train"] - 0.1, "gain": 0.25},
         {"sfx": "ding", "start": b["cut_train"] + 0.4, "gain": 0.12},
         {"sfx": "pop", "start": b["no_insp"] + 0.1, "gain": 0.2},
         {"sfx": "tick", "start": b["nobody"] + 0.9, "gain": 0.3},
         {"sfx": "tick", "start": b["nobody"] + 1.6, "gain": 0.25}]
    for i in range(7):
        c.append({"sfx": "pop", "start": b["which"] + i * 0.11, "gain": 0.1})
    return c


def sky_bands(cv, top, bottom, x0=-10, x1=1290, y0=-10, y1=730, n=10):
    """Gradient made of rects in the current transform (so it slides with whip pans)."""
    h = (y1 - y0) / n
    for k in range(n):
        cv.rect(x0, y0 + k * h - 1, x1, y0 + (k + 1) * h + 1, fill=lerp_color(top, bottom, k / (n - 1)), outline=None)


# ================================================================== phase 1: time-lapse
TOWERS = [(-120, 170, 560, (200, 214, 226)), (180, 140, 470, (170, 190, 214)), (420, 200, 640, (214, 210, 200)),
          (700, 150, 520, (186, 206, 220)), (930, 180, 700, (206, 200, 214)), (1250, 160, 560, (190, 214, 206)),
          (1480, 200, 620, (214, 206, 190))]
SIGNS = sign_layout(21, -150, 1650, GROUND, n=30)
# growing up = Mui's own designs, scaled uniformly: kid `mui` -> bigger `mui` -> `muilon` without the eye bags
# -> `muilon`
TEEN = dict(k=1.25 * 1.3)
YOUNG = dict(bags=False)


def _lapse(t, b):
    return ease_in_out(progress(t, b["lapse0"], b["lapse1"] - b["lapse0"]))


def _age(t, b):
    return 8 + 41 * _lapse(t, b)


def _stage(age):
    """Continuous stage 0..3 (kid, teen, young man, Old Mui) with short morph windows."""
    for i, (a0, a1) in enumerate(((11, 14), (18, 21), (31, 36))):
        if age < a0:
            return float(i)
        if age < a1:
            return i + (age - a0) / (a1 - a0)
    return 3.0


def _draw_mui_stage(cv, k, t, look, expr):
    y = GROUND - 26
    kw = dict(pose="sit_chin_on_hand", t=t, look=look, blink=blink(t, 2))
    if k == 0:
        draw_seated(cv, "MUI", STEP_X, y, 1.0, expression=expr or "bored", **kw)
    elif k == 1:
        draw_seated(cv, "MUI", STEP_X, y, 1.0, expression=expr or "bored", variant=TEEN, **kw)
    elif k == 2:
        draw_seated(cv, "OLD_MUI", STEP_X, y, 0.95, expression=expr or "bored", variant=YOUNG, **kw)
    else:
        draw_seated(cv, "OLD_MUI", STEP_X, y, 0.95, expression=expr or "bored", **kw)


def _camera1(t, b):
    p = ease_in_out(progress(t, b["meet"] - 0.3, 1.2))
    return lerp(700, 930, p), lerp(360, 410, p), lerp(1.0, 1.28, p)


def phase1(cv, t, b, stage_k):
    m = _lapse(t, b)
    tau = t + 36 * m                                     # "virtual clock" that races during the lapse
    sun_f = (0.8 + (tau - t) / 12) % 1.0
    day = math.sin(math.pi * sun_f)
    sky_top = lerp_color((60, 70, 120), P.SKY_TOP, clamp(day * 1.6))
    sky_bot = lerp_color((240, 170, 120), P.SKY_BOTTOM, clamp(day * 1.6))
    sky_bands(cv, sky_top, sky_bot)
    if 0.0 < sun_f < 1.0:
        draw_sun(cv, lerp(-100, 1380, sun_f), 300 - 220 * day, 50, t, rays=m < 0.02 or m > 0.98)
    for i, (cx, cy, s, sp) in enumerate([(160, 110, 1.0, 6), (560, 70, 0.8, 4), (880, 160, 0.7, 5)]):
        draw_cloud(cv, (cx + tau * sp * (1 + 6 * (0 < m < 1))) % 1600 - 160, cy, s)
    cx, cy, z = _camera1(t, b)
    with cv.camera(cx, cy, z):
        # towers rise behind the tube houses
        for i, (x, w, h, col) in enumerate(TOWERS):
            g = ease_out(clamp((m - 0.08 * i - 0.1) / 0.35))
            if g > 0.01:
                draw_tower(cv, x, w, h * g + 150, GROUND - 150, col, seed=i, lit=clamp(1 - day * 1.5))
        draw_alley(cv, t, ground_y=GROUND, step_x=STEP_X)
        # extra tangled wires
        for k in range(int(m * 6)):
            for a, bb in ((-320, 200), (200, 720), (720, 1240), (1240, 1760)):
                p0, p2 = (a + 20, GROUND - 440 + k * 6), (bb - 20, GROUND - 436 + k * 5)
                cv.curve(p0, ((p0[0] + p2[0]) / 2, GROUND - 360 + k * 14), p2, P.WIRE, 2.0)
        for sg in SIGNS:
            sp = clamp((m - sg["order"] * 0.85) / 0.08)
            if sp > 0:
                draw_sign(cv, sg, ease_out_back(sp, 2.0))
        # Mui on the step, growing up
        look = (0.75, 0.35)
        if t > b["meet"] + 0.3:
            lp = ease_in_out(progress(t, b["meet"] + 0.3, 0.6))
            look = (lerp(0.75, 0.0, lp), lerp(0.35, 0.0, lp))
        _draw_mui_stage(cv, stage_k, t, look, None)
        # motorbikes, more and more of them
        nb = 1 + int(m * 9)
        for i in range(10):
            if i >= nb and not (m == 0 and i == 0):
                continue
            lane = i % 2
            spd = 260 + (i * 53) % 120
            span = 2600
            if lane == 0:
                x = (tau * spd + i * 397) % span - 600
                y, fl = 642, False
            else:
                x = span - 600 - (tau * spd + i * 523) % span
                y, fl = 700, True
            if m == 0 and i == 0 and t < b["lapse0"]:
                continue
            col = [P.ACCENT, P.ACCENT2, (250, 190, 40), (60, 160, 90), (200, 60, 150)][i % 5]
            draw_motorbike(cv, x, y, 0.62, col, flip=fl, t=tau, rider=[(90, 120, 200), (230, 120, 80),
                                                                      (110, 110, 120)][i % 3],
                           passengers=1 + (i % 3 == 2))


def phase1_overlay(cv, t, b):
    m_raw = progress(t, b["lapse0"], b["lapse1"] - b["lapse0"])
    ffs = pop(t, b["ff"], 0.3) * (1 - progress(t, b["lapse1"] + 0.6, 0.25))
    if ffs > 0.01:
        with cv.at(150, 90, ffs):
            cv.rect(-112, -46, 120, 52, fill=INK, outline=None, radius=12)
            cv.rect(-118, -52, 114, 46, fill=P.WHITE, radius=12, ow=3.4)
            blinkon = (t * 3) % 1 < 0.6 or m_raw <= 0
            col = P.ACCENT if blinkon else (240, 180, 170)
            for dx in (-82, -46):
                cv.poly([(dx, -26), (dx + 34, 0), (dx, 26)], fill=col, ow=2.5)
            cv.text(42, -14, "AGE", 20, (120, 110, 120), "black")
            cv.text(42, 16, str(int(round(_age(t, b)))), 40, INK, "black")
        if 0 < m_raw < 1:
            label(cv, 150, 165, "x 100,000", 20, bg=P.HIGHLIGHT, scale=ffs)
    name_tag(cv, t, b["meet"], "OLD MUI", "AGE 49. STILL NOT IMPRESSED.", x=70, y=600,
             dur=b["cut_kitchen"] - b["meet"] - 0.35)


# ================================================================== phase 2: kitchen
SIS = dict(shirt=(110, 200, 190))          # generic KID (engine `em`), recoloured only


def _phone_hands(cv, x, y, t, skin, seed, glow=True):
    with cv.at(x, y, 1, rot=math.sin(t * 2 + seed) * 3):
        cv.rect(-14, -24, 14, 22, fill=INK, radius=5, ow=2.4)
        cv.rect(-10, -19, 10, 15, fill=(160, 220, 255), outline=None, radius=2)
        if glow:
            for k in range(3):
                cv.line([(-6, -12 + k * 8), (6 - (k % 2) * 6, -12 + k * 8)], (90, 150, 220), 2)
        cv.circle(-15, 8, 9, fill=skin)
        cv.circle(15, 8, 9, fill=skin)
        thumb = math.sin(t * 14 + seed) > 0
        cv.circle(8 if thumb else -6, 0, 5, fill=skin, ow=2)


def _noodle_cup(cv, x, y, t, seed):
    cv.poly([(x - 26, y - 52), (x + 26, y - 52), (x + 19, y), (x - 19, y)], fill=(250, 240, 220))
    cv.rect(x - 25, y - 44, x + 25, y - 30, fill=P.ACCENT, outline=None)
    cv.poly([(x - 26, y - 52), (x + 26, y - 52), (x + 19, y), (x - 19, y)], fill=None)
    cv.text(x, y - 37, "MÌ", 11, P.WHITE, "black")
    cv.line([(x - 4, y - 50), (x + 22, y - 96)], P.WOOD_DARK, 3.4)
    cv.line([(x + 4, y - 50), (x + 30, y - 92)], P.WOOD_DARK, 3.4)
    for i in range(3):
        ph = (t * 0.7 + i / 3 + seed * 0.13) % 1
        cv.circle(x - 10 + i * 10 + math.sin(ph * 6 + i) * 4, y - 60 - ph * 50, 4 + ph * 6, fill=P.WHITE,
                  outline=None)


def _heart(cv, x, y, r, col=P.ACCENT):
    cv.circle(x - r * 0.5, y, r * 0.58, fill=col, outline=None)
    cv.circle(x + r * 0.5, y, r * 0.58, fill=col, outline=None)
    cv.poly([(x - r * 1.05, y + r * 0.15), (x + r * 1.05, y + r * 0.15), (x, y + r * 1.2)], fill=col, outline=None)


def _camera2(t, b):
    p = ease_in_out(progress(t, b["actually"] - 0.2, 0.8))
    q = ease_in_out(progress(t, b["little"] - 0.1, 0.6))
    z = lerp(1.3, 1.42, p) * lerp(1, 1.3 / 1.42, q)
    return lerp(650, 740, p * (1 - q)), lerp(470, 455, p * (1 - q)), z


def phase2(cv, t, b, ctx):
    cx, cy, z = _camera2(t, b)
    out = {}
    with cv.camera(cx, cy, z):
        draw_kitchen(cv, t, night=True)
        # the kids at the table
        draw_character(cv, "HIS_KID", 350, 672, 1.1, pose="sit", expression="bored", t=t, look=(0, 0.9),
                       mouth_open=ctx.mouth("HIS KID", t), blink=blink(t, 4))
        draw_character(cv, "KID", 560, 652, 1.3, pose="sit", expression="bored", t=t + 1, look=(0, 0.9),
                       variant=SIS, blink=blink(t, 6))
        # phone glow on faces
        draw_dinner_table(cv, 470, 600, 500, dishes=False)
        _noodle_cup(cv, 250, 600, t, 0)
        _noodle_cup(cv, 660, 600, t, 1)
        _phone_hands(cv, 362, 592, t, P.SKIN, 0)          # held low at the table edge, chins above
        _phone_hands(cv, 566, 594, t, P.SKIN, 2)
        # hearts float off the son's phone while he texts his girlfriend
        hp = progress(t, b["text"] + 0.3, 2.2)
        if 0 < hp < 1:
            for i in range(3):
                q = (hp * 1.6 - i * 0.25)
                if 0 < q < 1:
                    _heart(cv, 380 + math.sin(q * 6 + i) * 18 + i * 10, 560 - q * 120, 9 * (1 - q * 0.4))
        # Old Mui
        expr, pose, look = "neutral", "stand", (-0.8, 0.45)
        if t >= b["age"] - 0.1:
            expr, pose, look = "shocked", "shrug", (-0.8, 0.3)
        if t >= b["actually"] - 0.15:
            sl = ease_in_out(progress(t, b["actually"] - 0.15, 0.5))
            expr, pose, look = "deadpan", "stand", (lerp(-0.8, 1.0, sl), lerp(0.3, -0.35, sl))
        if t >= b["little"]:
            expr, look = "bored", (0.0, 0.0)
        a = draw_character(cv, "OLD_MUI", 930, 715, 1.0, pose=pose, expression=expr, look=look,
                           mouth_open=ctx.mouth("OLD MUI", t), t=t, blink=blink(t, 9) if t < b["actually"] else 0)
        out["mui"] = a
    return out


def _flashback(cv, t, b, head):
    s = pop(t, b["bubble"], 0.35) * (1 - ease_out(progress(t, b["little"] - 0.1, 0.25)))
    if s <= 0.01:
        return None
    bx, by = 1070, 170
    hx, hy = head
    # thought-bubble chain
    for k, r in enumerate((9, 13, 18)):
        u = (k + 1) / 4
        cv.circle(lerp(hx + 40, bx - 90, u), lerp(hy - 50, by + 90, u), r * s, fill=P.WHITE, ow=3)
    with cv.at(bx, by, s):
        for dx, dy, r in ((-120, -40, 60), (-50, -85, 66), (40, -80, 70), (118, -30, 62), (110, 50, 60),
                          (20, 85, 66), (-80, 80, 60), (-140, 20, 52)):
            cv.circle(dx, dy, r + 3.4, fill=INK, outline=None)
        for dx, dy, r in ((-120, -40, 60), (-50, -85, 66), (40, -80, 70), (118, -30, 62), (110, 50, 60),
                          (20, 85, 66), (-80, 80, 60), (-140, 20, 52)):
            cv.circle(dx, dy, r, fill=P.WHITE, outline=None)
        cv.rect(-150, -90, 150, 90, fill=(236, 214, 176), radius=10, ow=3)
        cv.rect(-150, 30, 150, 90, fill=(206, 190, 160), outline=None, radius=10)
        cv.text(0, -68, "COURT", 20, INK, "black")
        draw_plastic_stool(cv, 70, 82, P.PLASTIC_RED, 0.6)
        draw_plastic_stool(cv, 120, 82, P.PLASTIC_RED, 0.6)
        cv.text(70, 64, "MOM", 11, P.WHITE, "black")
        cv.text(120, 64, "DAD", 11, P.WHITE, "black")
        draw_plastic_stool(cv, -70, 80, P.PLASTIC_BLUE, 0.75)
        hit = progress(t, b["dad"] - 0.18, 0.18)
        draw_character(cv, "MUI", -70, 36, 0.52, pose="sit_point", props=("wig", "gavel"), expression="angry",
                       t=t, lean=lerp(0, -10, hit), blink=0)
    if s >= 0.99:
        return (bx - 150, by - 90, bx + 150, by + 90)
    return None


def _sepia(img, box):
    x0, y0, x1, y1 = [int(v) for v in box]
    reg = img.crop((x0, y0, x1, y1))
    sep = ImageOps.colorize(ImageOps.grayscale(reg), (70, 50, 30), (250, 230, 190))
    mask = Image.new("L", reg.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([1, 1, reg.width - 2, reg.height - 2], 10, fill=255)
    img.paste(sep, (x0, y0), mask)
    return img


def _polaroid(cv, t, b):
    s = pop(t, b["little"] + 0.05, 0.35) * (1 - progress(t, b["cut_book"] - 0.1, 0.1))
    if s <= 0.01:
        return
    with cv.at(250, 210, s, rot=-6):
        cv.rect(-140, -150, 152, 162, fill=INK, outline=None, radius=6)
        cv.rect(-146, -156, 146, 156, fill=P.WHITE, radius=6, ow=3)
        cv.rect(-126, -136, 126, 92, fill=P.SKY_BOTTOM, ow=2.5)
        cv.rect(-126, 52, 126, 92, fill=P.GROUND, outline=None)
        cv.rect(-60, 32, 60, 56, fill=P.STEP, ow=2.4)
        draw_character(cv, "MUI", 0, 34, 0.66, pose="sit_chin_on_hand", expression="bored", t=t, look=(0.7, 0.3),
                       blink=blink(t, 2))
        # adults in the background, as Mui sees them
        cv.rect(-126, -136, 126, 92, fill=None, ow=2.5)
        cv.text(0, 124, "ADULTS = BORING", 22, INK, "black")


def _boring_stamp(cv, t, b, chest):
    p = progress(t, b["boring"], 0.18)
    if p <= 0:
        return
    s = lerp(2.6, 1.0, ease_out(p))
    x, y = chest
    label(cv, x, y + 10, "BORING ADULT", 26, fill=P.WHITE, bg=P.ACCENT, scale=s, rot=-8)


# ================================================================== phase 3: book
CROWD = [("DAD", None, 0.85), ("KID", dict(shirt=(250, 190, 110)), 1.0), ("TI", None, 1.0), ("MUI", None, 1.0),
         ("HAI", None, 1.0), ("TUN", None, 1.0), ("KID", dict(shirt=(160, 120, 220)), 1.0), ("HIS_KID", None, 1.0),
         ("OLD_MUI", None, 1.0)]


def _rays(cv, t, cx, cy, c1, c2):
    cv.rect(-10, -10, 1290, 730, fill=c1, outline=None)
    for k in range(16):
        a0 = math.radians(k * 22.5 + t * 6)
        a1 = a0 + math.radians(11.25)
        cv.poly([(cx, cy), (cx + 1600 * math.cos(a0), cy + 1600 * math.sin(a0)),
                 (cx + 1600 * math.cos(a1), cy + 1600 * math.sin(a1))], fill=c2, outline=None)


def phase3(cv, t, b):
    _rays(cv, t, 640, 250, (255, 236, 190), (255, 226, 160))
    s = ease_out_back(progress(t, b["book"], 0.5), 1.8)
    if s > 0.01:
        draw_book_cover(cv, 640, 245, w=240, h=350, rot=math.sin(t * 1.3) * 2.5 + (1 - s) * -20, scale=s)
    qs = pop(t, b["for"], 0.3) * (1 - progress(t, b["anyone"] - 0.2, 0.2))
    if qs > 0.01:
        with cv.at(860, 150, qs, rot=10):
            cv.circle(0, 0, 56, fill=P.ACCENT2, ow=4)
            cv.text(0, 4, "?", 74, P.WHITE, "black")
    bs = pop(t, b["anyone"] - 0.1, 0.35)
    label(cv, 640, 462, "FOR ANYONE WHO WAS ONCE A CHILD", 28, bg=P.WHITE, scale=bs)
    n = len(CROWD)
    for i, (nm, var, sc) in enumerate(CROWD):
        ps = pop(t, b["which"] + i * 0.08, 0.35)
        if ps <= 0.01:
            continue
        x = 85 + i * (1110 / (n - 1))
        y = 742 + (1 - ps) * 200
        expr = "bored" if nm in ("MUI", "OLD_MUI", "HIS_KID") else "happy"
        draw_character(cv, nm, x, y, sc, pose="arms_up" if expr == "happy" else "stand", expression=expr, t=t + i,
                       variant=var, blink=blink(t, i))
    es = pop(t, b["everyone"] + 0.2, 0.25)
    if es > 0.01:
        with cv.at(1010, 330, es, rot=-10):
            cv.rect(-150, -40, 150, 40, fill=P.WHITE, outline=P.ACCENT, ow=6, radius=8)
            cv.text(0, 2, "= EVERYONE", 40, P.ACCENT, "black")


# ================================================================== phase 4: train
RAIL_Y = 520
BOOTH = (1040, 690)


def _booth(cv, t, b):
    x, y = BOOTH
    cv.rect(x - 230, y - 6, x + 240, y + 60, fill=(200, 190, 176), outline=SOFT, ow=2.4)   # platform
    cv.rect(x - 230, y - 6, x + 240, y + 6, fill=(250, 214, 80), outline=None)              # yellow line
    with cv.at(x, y, 1.0):
        cv.rect(-90, -230, 90, 0, fill=(150, 200, 220), radius=6)
        cv.rect(-104, -256, 104, -222, fill=P.ACCENT, radius=6)
        cv.rect(-60, -200, 60, -110, fill=(70, 80, 100))                                   # empty window
        draw_plastic_stool(cv, 0, -112, P.PLASTIC_BLUE, 0.5)                               # nobody on it
        cv.rect(-70, -112, 70, -100, fill=P.WOOD, radius=3)                                # counter
        cv.text(0, -238, "SOÁT VÉ", 20, P.WHITE, "black")
        cv.rect(-56, -84, 56, -54, fill=P.WHITE, ow=2.4, radius=4)
        cv.text(0, -69, "TICKETS", 15, INK, "black")
        # hook + cap on the side wall
        hx, hy = 116, -150
        cv.limb([(88, hy), (hx, hy)], 5, (120, 120, 130))                                 # peg on the side
        cv.circle(hx, hy, 4, fill=(120, 120, 130), ow=2)
        sw = math.sin(t * 2.2) * 6 + 10 * math.sin(t * 7) * math.exp(-max(0, t - b["no_insp"]) * 2) * \
            (t > b["no_insp"])
        with cv.at(hx, hy, 1.0, rot=sw):
            cv.rect(-26, 6, 26, 30, fill=(40, 52, 96), radius=8)
            cv.ellipse(0, 31, 32, 6, fill=INK, outline=None)
            cv.rect(-26, 18, 26, 24, fill=P.GOLD, outline=None)
            cv.circle(0, 14, 5, fill=P.GOLD, ow=1.8)


def _train_x(t, b):
    """Chug in, linger mid-frame while the kids wave ("...any time you like."), then leave before "Nobody"."""
    t0, t1, t2 = b["cut_train"] + 0.2, b["back"] + 0.3, b["nobody"] - 0.35
    if t < t1:
        u = progress(t, t0, t1 - t0)
        return lerp(-1000, 620, 1 - (1 - u) ** 2)
    if t < t2:
        return lerp(620, 760, progress(t, t1, t2 - t1))
    u = progress(t, t2, 0.75)
    return lerp(760, 2400, u * u)


def phase4(cv, t, b):
    zp = ease_in_out(progress(t, b["nobody"] - 0.1, 0.7))
    cx, cy, z = lerp(640, BOOTH[0] + 10, zp), lerp(360, BOOTH[1] - 150, zp), lerp(1.0, 1.9, zp)
    with cv.camera(cx, cy, z):
        sky_bands(cv, (250, 170, 120), (255, 226, 170), x0=-400, x1=1700, y0=-300, y1=RAIL_Y)
        draw_sun(cv, 300, 330, 70, t)
        for hx, hy, rx, ry, col in ((200, 520, 420, 160, (130, 180, 100)), (800, 530, 520, 140, (110, 170, 96)),
                                    (1300, 520, 380, 170, (140, 190, 110))):
            cv.ellipse(hx, hy, rx, ry, fill=col, outline=SOFT, ow=2.4)
        cv.rect(-400, RAIL_Y - 10, 1700, 1000, fill=(170, 200, 110), outline=None)
        draw_rails(cv, -400, 1700, RAIL_Y)
        # the train (engine leads to the right)
        tx = _train_x(t, b)
        moving = b["cut_train"] + 0.2 < t < b["nobody"] + 0.4

        def kids_in(names):
            def f(cv_, wx, wy, ww, wh, i):
                if i < len(names) and names[i]:
                    nm = names[i]
                    if nm == "OLD_MUI":
                        _head_in_window(cv_, wx, wy, ww, wh, t)
                        return
                    sc = 0.62
                    hc = wy + wh * 0.55
                    off = 132 if nm != "OLD_MUI" else 410
                    expr = "happy" if nm != "OLD_MUI" else "proud"
                    draw_character(cv_, nm, wx + ww / 2, hc + off * sc, sc, pose="wave" if nm != "OLD_MUI" else "stand",
                                   expression=expr, t=t + i, blink=blink(t, i + 3))
            return f

        draw_train_car(cv, tx - 640, RAIL_Y, 300, 150, (90, 160, 210), t if moving else 0,
                       inside=kids_in(["TI", "KID", "TUN"]))
        draw_train_car(cv, tx - 330, RAIL_Y, 300, 150, (240, 180, 70), t if moving else 0,
                       inside=kids_in(["HAI", "MUI", None]))
        draw_train_car(cv, tx - 20, RAIL_Y, 300, 150, (230, 90, 70), t if moving else 0,
                       inside=kids_in(["OLD_MUI"]), engine=True, sign="→ TUỔI THƠ")
        if moving:
            draw_steam_puffs(cv, tx + 30, RAIL_Y - 260, t)
        _booth(cv, t, b)
    ls = pop(t, b["no_insp"] + 0.1, 0.3) * (1 - progress(t, b["nobody"] - 0.2, 0.2))
    if ls > 0.01:
        label(cv, 1040, 398, "INSPECTOR: ---", 24, bg=P.WHITE, scale=ls, rot=4)
    cs = pop(t, b["back"], 0.3) * (1 - progress(t, b["nobody"] - 0.2, 0.2))
    if cs > 0.01:
        label(cv, 330, 110, "NEXT STOP: CHILDHOOD", 26, fill=P.WHITE, bg=P.ACCENT2, scale=cs)


def _head_in_window(cv, wx, wy, ww, wh, t):
    """Old Mui's head only, framed in the cab window: draw him on a small offscreen canvas and paste the
    crop (the window frame cannot mask an adult's long legs below the car)."""
    k = 4
    sub = Canvas(bg=(255, 236, 190), ss=1, w=int(ww * k), h=int(wh * k))
    hs = 0.5                                   # head (r ~ 62 px at scale 1) fits the 60 px cab window
    with sub.at(ww * k / 2, wh * k * 0.6 + 231 * hs * k, hs * k):
        draw_character(sub, "OLD_MUI", 0, 0, 1.0, expression="proud", t=t, look=(0.6, 0), blink=blink(t, 8))
    cv.paste(sub.finish(), wx, wy, scale=1.0 / k)


# ================================================================== frame
def render_frame(t, ctx):
    b = beats(ctx)
    if t < b["cut_kitchen"]:
        s = _stage(_age(t, b))
        k0 = int(math.floor(s))
        f = s - k0
        img = _phase1_img(ctx, t, b, k0)
        if f > 0.01 and k0 < 3:
            img = Image.blend(img, _phase1_img(ctx, t, b, k0 + 1), ease_in_out(f))
        return img
    if t < b["cut_book"] - 0.2:
        cv = ctx.canvas(P.CARD_BG)
        out = phase2(cv, t, b, ctx)
        a = out["mui"]
        box = _flashback(cv, t, b, a["head"])
        _polaroid(cv, t, b)
        _boring_stamp(cv, t, b, a["chest"])
        img = cv.finish()
        if box:
            img = _sepia(img, [v * 1 for v in box])
        return img
    cv = ctx.canvas(P.CARD_BG)
    w = ease_in_out(progress(t, b["cut_train"] - 0.2, 0.4))
    if w < 1:
        with cv.at(-1400 * w, 0):
            w0 = ease_in_out(progress(t, b["cut_book"] - 0.2, 0.4))
            with cv.at(1400 * (1 - w0), 0):
                phase3(cv, t, b)
    if w > 0:
        with cv.at(1400 * (1 - w), 0):
            phase4(cv, t, b)
    return cv.finish()


def _phase1_img(ctx, t, b, k):
    cv = ctx.canvas(P.SKY_BOTTOM)
    phase1(cv, t, b, k)
    phase1_overlay(cv, t, b)
    return cv.finish()
