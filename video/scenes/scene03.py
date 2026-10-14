"""Scene 3 - The Crew (heist-movie line-up).

Beats (all from ctx):
  "Luckily, Mui is not alone."  Mui alone in a spotlight in a dark hideout, bored
  "He has a crew."              three silhouettes with glowing eyes pop in behind him (thud)
  "Hai."   Hai zips in from the right (speed lines), FREEZE + name tag; "sneaky" eyes dart;
           "never, ever sorry" a pot falls off the crate and smashes, Hai shrugs, smug
  "Tun."   Tun walks in, FREEZE + tag; "Sweet" hearts; "agrees with literally everything" she nods
           like crazy while YES! / OKAY! / SURE! pop around her
  "And Ti." Ti struts in, FREEZE + tag; "Stylish" sparkles; "confident" hands on hips;
           "missing her two front teeth" snap zoom on her grin, red circle on the gap
  "It'th a look."  smug, sparkle ding
  "Together..."  all four in a row; ADULT WORLD picture pops, BORING stamp; "...change it." fists up,
           stamp CHANGE IT!
  "How?"   Hai shrugs, everyone looks at Mui
  "I have three ideas."  Mui points up: lightbulb + a big "3" badge
"""
import math

from lib import palette as P
from lib.characters import draw_character
from lib.core import INK, clamp, ease_in_out, ease_out, lerp, pop, progress
from lib.extra_s2_4 import (badge, dark_variant, from_screen, icon_briefcase, lightbulb, sparkle, speed_lines,
                            spotlight, stamp)
from lib.fx import flash, freeze_frame, letterbox
from lib.text import label, name_tag

BG = (30, 34, 58)
FLOOR = (44, 48, 80)
FLOOR_Y = 600
INTRO_X = 880
GROUP = [("HAI", 280), ("MUI", 530), ("TUN", 780), ("TI", 1020)]


def beats(ctx):
    l1, hai, tun, ti, look, tog, how, ideas = (ctx.line(i) for i in range(8))
    b = dict(
        l1=l1, crew=ctx.find_word(l1.id, "He"),
        hai=hai, hai_cut=hai.start - 0.35, hai_name=hai.start,
        fast=ctx.find_word(hai.id, "Fast"), sneaky=ctx.find_word(hai.id, "sneaky"),
        never=ctx.find_word(hai.id, "never"), sorry=ctx.find_word(hai.id, "sorry"),
        tun=tun, tun_cut=tun.start - 0.45, tun_name=tun.start,
        sweet=ctx.find_word(tun.id, "Sweet"), agrees=ctx.find_word(tun.id, "agrees"),
        ti=ti, ti_cut=ti.start - 0.4, ti_name=ctx.find_word(ti.id, "Ti"),
        stylish=ctx.find_word(ti.id, "Stylish"), confident=ctx.find_word(ti.id, "confident"),
        missing=ctx.find_word(ti.id, "missing"), teeth=ctx.find_word(ti.id, "teeth"),
        look=look,
        tog=tog, group_cut=tog.start - 0.3, adult=ctx.find_word(tog.id, "adult"),
        boring=ctx.find_word(tog.id, "boring"), change=ctx.find_word(tog.id, "change"),
        how=how, ideas=ideas, three=ctx.find_word(ideas.id, "three"),
    )
    b["freeze"] = {"HAI": b["hai_name"] + 0.05, "TUN": b["tun_name"] + 0.05, "TI": b["ti_name"] + 0.05}
    return b


def audio_cues(ctx):
    b = beats(ctx)
    return [
        {"sfx": "music_bed", "start": 0.0, "dur": ctx.duration, "gain": 0.1, "fade_out": 0.6},
        {"sfx": "thud", "start": b["crew"], "gain": 0.4},
        {"sfx": "whoosh", "start": b["hai_cut"], "gain": 0.3},
        {"sfx": "shutter", "start": b["freeze"]["HAI"], "gain": 0.45},
        {"sfx": "thud", "start": b["never"] + 0.3, "gain": 0.35},
        {"sfx": "shutter", "start": b["freeze"]["TUN"], "gain": 0.45},
        {"sfx": "pop", "start": b["sweet"], "gain": 0.2},
        {"sfx": "pop", "start": b["agrees"] + 0.3, "gain": 0.2},
        {"sfx": "pop", "start": b["agrees"] + 0.7, "gain": 0.2},
        {"sfx": "pop", "start": b["agrees"] + 1.1, "gain": 0.2},
        {"sfx": "shutter", "start": b["freeze"]["TI"], "gain": 0.45},
        {"sfx": "whoosh", "start": b["missing"], "gain": 0.25},
        {"sfx": "ding", "start": b["look"].end + 0.05, "gain": 0.3},
        {"sfx": "whoosh", "start": b["group_cut"], "gain": 0.2},
        {"sfx": "pop", "start": b["adult"], "gain": 0.25},
        {"sfx": "thud", "start": b["boring"] + 0.15, "gain": 0.35},
        {"sfx": "slap", "start": b["change"], "gain": 0.4},
        {"sfx": "ding", "start": b["three"], "gain": 0.4},
    ]


# ------------------------------------------------------------------ helpers
def _hideout(cv, t, spot_x, spot_w=520):
    cv.rect(-300, -300, 1580, FLOOR_Y, fill=BG, outline=None)
    for k in range(7):                     # faint brick rows
        y = 60 + k * 76
        cv.line([(-300, y), (1580, y)], (40, 44, 72), 3)
        for j in range(-2, 16):
            x = j * 120 + (60 if k % 2 else 0)
            cv.line([(x, y), (x, y + 76)], (40, 44, 72), 3)
    cv.rect(-300, FLOOR_Y, 1580, 1000, fill=FLOOR, outline=None)
    cv.line([(-300, FLOOR_Y), (1580, FLOOR_Y)], (20, 22, 40), 3)
    spotlight(cv, spot_x, -10, FLOOR_Y + 40, w_top=140, w_floor=spot_w)
    cv.line([(spot_x, -40), (spot_x, 20)], (20, 22, 40), 4)
    cv.poly([(spot_x - 36, 46), (spot_x + 36, 46), (spot_x + 16, 14), (spot_x - 16, 14)], fill=(90, 90, 110))
    cv.ellipse(spot_x, 48, 30, 8, fill=(255, 240, 180), outline=None)


def _heart(cv, x, y, s):
    if s <= 0.01:
        return
    with cv.at(x, y, s):
        cv.poly([(0, 22)] + [(math.cos(math.radians(a)) * 12 - 11, math.sin(math.radians(a)) * 12 - 6)
                             for a in range(150, 361, 30)]
                + [(math.cos(math.radians(a)) * 12 + 11, math.sin(math.radians(a)) * 12 - 6)
                   for a in range(180, 391, 30)], fill=(240, 90, 120), ow=2.6)


def _pot(cv, x, y, broken):
    if not broken:
        cv.poly([(x - 34, y - 70), (x + 34, y - 70), (x + 24, y), (x - 24, y)], fill=P.POT)
        cv.rect(x - 40, y - 82, x + 40, y - 66, fill=P.POT, radius=4)
        for dx, h in ((-14, 70), (4, 92), (20, 64)):
            cv.limb([(x + dx * 0.5, y - 80), (x + dx, y - 80 - h)], 8, P.LEAF)
    else:
        cv.ellipse(x, y, 70, 14, fill=(110, 80, 60), outline=None)
        for dx, rot in ((-50, -30), (-10, 15), (36, 50)):
            with cv.at(x + dx, y - 8, 1, rot=rot):
                cv.poly([(-18, -12), (20, -10), (12, 10), (-14, 8)], fill=P.POT, ow=2.6)
        cv.limb([(x + 10, y - 6), (x + 70, y - 30)], 8, P.LEAF)


# ------------------------------------------------------------------ shots
def shot_alone(t, ctx, b, cv):
    _hideout(cv, t, 640)
    sil = pop(t, b["crew"], 0.3)
    if sil > 0:
        for i, (nm, x) in enumerate((("HAI", 300), ("TUN", 980), ("TI", 1170))):
            draw_character(cv, nm, x, FLOOR_Y + 10 + (1 - sil) * 30, 1.6, colors=dark_variant(nm),
                           expression="smug" if nm == "HAI" else "neutral", t=t + i, look=(-0.6 if x > 640 else 0.6, 0))
    draw_character(cv, "MUI", 640, FLOOR_Y + 40, 1.9, expression="bored", t=t,
                   look=(0, 0) if t < b["crew"] + 0.3 else (-0.7, 0), mouth_open=ctx.mouth("MUI", t))


def shot_hai(t, ctx, b, cv):
    _hideout(cv, t, INTRO_X)
    arrive = ease_out(progress(t, b["hai_cut"], 0.3))
    x = lerp(1600, INTRO_X, arrive)
    if arrive < 1 or t < b["freeze"]["HAI"] + 0.6:
        speed_lines(cv, x + 60, x + 600, FLOOR_Y - 150, spread=260, seed=3, t=t * (arrive < 1))
    broken = t >= b["never"] + 0.3
    fall = progress(t, b["never"], 0.3)
    if 0 < fall < 1:
        with cv.at(1100 + fall * 20, FLOOR_Y + 40 - 170 * (1 - fall ** 2), 1, rot=fall * 70):
            _pot(cv, 0, 0, False)
    elif not broken:
        _pot(cv, 1100, FLOOR_Y - 130, False)
    cv.rect(1040, FLOOR_Y - 130, 1160, FLOOR_Y + 40, fill=P.WOOD, ow=3.4)   # crate
    cv.line([(1040, FLOOR_Y - 45), (1160, FLOOR_Y - 45)], P.WOOD_DARK, 4)
    if broken:
        _pot(cv, 1150, FLOOR_Y + 60, True)
    look = (0, 0)
    if b["sneaky"] <= t < b["never"]:
        look = (math.copysign(0.9, math.sin((t - b["sneaky"]) * 14)), 0)
    pose = "run" if arrive < 1 else ("shrug" if t >= b["sorry"] - 0.1 else "stand")
    draw_character(cv, "HAI", x, FLOOR_Y + 60, 2.25, pose=pose, expression="smug", t=t, look=look,
                   lean=-14 if arrive < 1 else 0)


def shot_tun(t, ctx, b, cv):
    _hideout(cv, t, INTRO_X)
    arrive = ease_out(progress(t, b["tun_cut"], 0.45))
    x = lerp(-200, INTRO_X, arrive)
    nod = 0.0
    if t >= b["agrees"]:
        nod = math.sin((t - b["agrees"]) * 22) * 7
    a = draw_character(cv, "TUN", x, FLOOR_Y + 60, 2.6, pose="walk" if arrive < 1 else "stand",
                       expression="happy", t=t, nod=nod, look=(0, -0.2))
    hx, hy = a["head"]
    for k in range(3):
        _heart(cv, hx - 140 + k * 140, hy - 150 - 20 * (k % 2) - (t - b["sweet"]) * 30,
               pop(t, b["sweet"] + k * 0.12, 0.3) * (1 - progress(t, b["agrees"], 0.3)) * 1.4)
    for k, (word, dx, dy, rot) in enumerate((("YES!", -230, -80, -10), ("OKAY!", 210, -120, 8),
                                             ("SURE!", -190, 60, 6), ("TOTALLY!", 230, 40, -6))):
        s = pop(t, b["agrees"] + 0.3 + k * 0.4, 0.3)
        label(cv, hx + dx, hy + dy, word, 30, bg=P.HIGHLIGHT, scale=s, rot=rot)


def shot_ti(t, ctx, b, cv):
    zoom_p = ease_in_out(progress(t, b["missing"], 0.35)) * (1 - ease_in_out(progress(t, b["look"].end + 0.35, 0.3)))
    head = (INTRO_X, FLOOR_Y + 60 - 2.6 * 140)
    cam = (lerp(640, head[0], zoom_p), lerp(360, head[1] + 10, zoom_p), lerp(1.0, 2.1, zoom_p))
    with cv.camera(*cam):
        _hideout(cv, t, INTRO_X)
        arrive = ease_out(progress(t, b["ti_cut"], 0.45))
        x = lerp(1500, INTRO_X, arrive)
        pose = "walk" if arrive < 1 else ("hands_hip" if t >= b["confident"] else "stand")
        talking = b["look"].start <= t < b["look"].end
        expr = "smug" if (talking or t >= b["look"].end) else "happy"
        a = draw_character(cv, "TI", x, FLOOR_Y + 60, 2.6, pose=pose, expression=expr, t=t,
                           mouth_open=ctx.mouth("TI", t), look=(0, 0) if zoom_p > 0.5 else (-0.3, 0))
        m = from_screen(cv, a["mouth"])
        for k, (dx, dy) in enumerate(((-150, -260), (140, -300), (170, -120), (-170, -80))):
            sparkle(cv, x + dx * 1.3, FLOOR_Y + 60 + dy * 1.3, pop(t, b["stylish"] + k * 0.1, 0.3) *
                    (0.8 + 0.2 * math.sin(t * 8 + k)) * (1 - progress(t, b["missing"], 0.2)) * 1.3)
    # red circle on the gap (screen space, after the zoom)
    if zoom_p > 0.9:
        mx, my = cv.to_screen(*m) if False else _cam_pt(m, cam)
        s = pop(t, b["teeth"], 0.3)
        if s > 0 and t < b["look"].start:
            cv.ellipse(mx, my - 6, 70 * s, 42 * s, fill=None, outline=P.ACCENT, ow=6)
            label(cv, mx + 330, my + 70, "MISSING", 40, bg=P.WHITE, fill=P.ACCENT, scale=s, rot=-6)
            cv.line([(mx + 240, my + 60), (mx + 75, my)], P.ACCENT, 6)
        if t >= b["look"].end:
            hx, hy = _cam_pt((INTRO_X, FLOOR_Y + 40 - 2.0 * 140), cam)
            sparkle(cv, mx + 160, my - 160, pop(t, b["look"].end, 0.3) * 2.0)


def _cam_pt(p, cam):
    cx, cy, z = cam
    return ((p[0] - cx) * z + 640, (p[1] - cy) * z + 360)


def shot_group(t, ctx, b, cv):
    _hideout(cv, t, 640, spot_w=1100)
    # the "adult world" picture
    s = pop(t, b["adult"], 0.3) * (1 - ease_out(progress(t, b["change"], 0.15)))
    if s > 0.01:
        with cv.at(640, 150, s, rot=-2):
            cv.rect(-190, -105, 190, 105, fill=(170, 170, 176), ow=4)
            cv.rect(-174, -89, 174, 89, fill=(130, 130, 138), outline=None)
            icon_briefcase(cv, -80, 10, 1.3, col=(100, 100, 106))
            cv.rect(30, -40, 130, 60, fill=(200, 200, 200), ow=3)
            for k in range(4):
                cv.line([(45, -22 + k * 20), (115, -22 + k * 20)], (120, 120, 120), 3)
            cv.text(0, -122 + 230, "ADULT WORLD", 26, P.WHITE, "black", stroke=3)
        stamp(cv, 660, 150, "BORING", s * pop(t, b["boring"] + 0.15, 0.2), rot=-14, size=56)
    stamp(cv, 640, 150, "CHANGE IT!", pop(t, b["change"], 0.25) * (1 - ease_out(progress(t, b["how"].start - 0.2, 0.2))),
          rot=-6, color=P.HIGHLIGHT, size=70)
    for i, (nm, x) in enumerate(GROUP):
        pose, expr, look = "stand", None, (0, 0)
        if t >= b["adult"]:
            look = (0, -0.8)
        if t >= b["change"]:
            pose, expr, look = "arms_up", "proud", (0, 0)
        if t >= b["how"].start - 0.15:
            pose, expr = "stand", None
            look = (0.9 if x < 540 else (-0.9 if x > 540 else 0), 0)
            if nm == "HAI":
                pose, expr = "shrug", "neutral"
        if nm == "MUI" and t >= b["ideas"].start - 0.1:
            pose, expr, look = "point_up", "smug", (0, 0)
        a = draw_character(cv, nm, x, FLOOR_Y + 80, 2.1, pose=pose, expression=expr, t=t + i * 0.6,
                           mouth_open=ctx.mouth(nm, t), look=look)
        if nm == "MUI":
            mui = a
    hx, hy = mui["hand_r"]
    badge(cv, hx - 10, hy - 80, pop(t, b["three"], 0.35), "3", size=72)
    tx, ty = mui["top"]
    lightbulb(cv, tx - 10, ty - 85, pop(t, b["three"] - 0.15, 0.35) * 1.1)


# ------------------------------------------------------------------ frame
def render_frame(t, ctx):
    b = beats(ctx)
    # freeze-frames: hold the drawing time still for a beat
    who = None
    tt = t
    for nm, fz in b["freeze"].items():
        if fz <= t < fz + 0.55:
            who, tt = nm, fz
    cv = ctx.canvas(BG)
    intro = False
    if t < b["hai_cut"]:
        shot_alone(t, ctx, b, cv)
    elif t < b["tun_cut"]:
        shot_hai(tt, ctx, b, cv)
        intro = "HAI"
    elif t < b["ti_cut"]:
        shot_tun(tt, ctx, b, cv)
        intro = "TUN"
    elif t < b["group_cut"]:
        shot_ti(tt, ctx, b, cv)
        intro = "TI"
    else:
        shot_group(t, ctx, b, cv)
    if intro == "HAI":
        name_tag(cv, t, b["freeze"]["HAI"], "HAI", "FAST. SNEAKY. NEVER SORRY.", x=60, y=580,
                 color=(60, 150, 80))
    elif intro == "TUN":
        name_tag(cv, t, b["freeze"]["TUN"], "TUN", "SWEET. GENTLE. AGREES WITH EVERYTHING.", x=60, y=580,
                 color=(230, 160, 30))
    elif intro == "TI":
        name_tag(cv, t, b["freeze"]["TI"], "TI", "STYLISH. CONFIDENT. TWO TEETH SHORT.", x=60, y=580,
                 color=(220, 80, 130), dur=b["missing"] - b["freeze"]["TI"] - 0.1)
    img = cv.finish()
    if intro:
        img = letterbox(img, 1.0, bar=44)
    if who:
        img = freeze_frame(img, 1.0)
        img = flash(img, 0.5 * (1 - progress(t, b["freeze"][who], 0.15)))
    return img
