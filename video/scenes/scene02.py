"""Scene 2 - The Evidence (rapid verb list, then school).

Beats (all times from ctx):
  "To be fair, he has evidence."  corkboard + "EXHIBIT A" sign; Mui presents it with a pointer
  the list: one instant photo per phrase slaps onto the board (shutter click), timed to the
            pauses in the narrator's audio, so the cuts speed up as the narrator does:
            EVERY DAY / WAKE UP / BRUSH TEETH / BREAKFAST / SCHOOL / MEMORIZE / HOME / HOMEWORK /
            MORE HOMEWORK / BED / WAKE UP (AGAIN) / BRUSH TEETH (AGAI- ...cut on the dash
  "See?"    snap close-up: Mui, toothbrush in mouth, foam, deadpan to camera
  "And school is the worst part."  classroom; giant teacher (head near the top of frame)
  "Repeat after me." teacher bubble / the class repeats it: word tiles fly out of every mouth into
            perfectly neat rows / silence / "...Not that part." facepalm, the tiles drop
  "Mui feels like a prisoner." snap close-up of Mui at his desk; on "prisoner" cell bars slam down,
            flash, he is in an orange jumpsuit ("INMATE #08" desk plate)
  "...hot afternoon, is not a crazy comparison." bars lift, the sun swells in the barred window,
            heat shimmer, sweat, the useless fan; Mui slowly turns to the camera
"""
import math
import random

from lib import palette as P
from lib.backgrounds import draw_classroom, draw_desks, draw_dinner_table, draw_sun
from lib.characters import char_spec, draw_character
from lib.core import INK, clamp, ease_in, ease_in_out, ease_out, ease_out_back, lerp, lerp_color, pop, progress
from lib.extra_s2_4 import (corkboard, draw_alarm_clock, draw_backpack, draw_backpack_straps, draw_bed,
                            draw_desk_lamp, draw_foam, draw_notebook_stack, draw_school_gate, draw_sink_front,
                            draw_sink_mirror, draw_tiles, draw_toothbrush, draw_window, heat_waves, jail_bars,
                            phrase_starts, photo_back, pin, polaroid, sweat, to_world, from_screen)
from lib.fx import flash, tint
from lib.text import label, speech_bubble, text_width

JUMPSUIT = dict(shirt=(250, 140, 50), pants=(240, 130, 45))
CLASS_KIDS = [("TI", 560, dict(outfit="uniform")), ("MUI", 740, dict(outfit="uniform")),
              ("HAI", 920, dict(outfit="uniform")), ("TUN", 1100, dict(outfit="uniform"))]
CHANT = ["REPEAT", "AFTER", "ME."]


# ------------------------------------------------------------------ timing
def beats(ctx):
    l1, l2, l3, see, worst, rep, cls, notthat, pris, hot = (ctx.line(i) for i in range(10))
    a = phrase_starts(ctx, l2.id, ["Every", "wakes", "brushes", "eats", "goes", "memorizes"])
    b = phrase_starts(ctx, l3.id, ["comes", "does", "gets", "goes", "wakes", "brushes"])
    starts = [s - 0.05 for s in a + b]
    b_ = dict(
        intro=l1, list_start=starts[0], photos=starts,
        evidence=ctx.find_word(l1.id, "evidence"),
        dash=ctx.find_word(l3.id, "—"),
        see=see.start - 0.12,                    # snap cut a hair before "See?"
        class_cut=worst.start - 0.25,
        rep=rep, cls=cls, notthat=notthat,
        cls_words=[ctx.find_word(cls.id, w) for w in ("Repeat", "after", "me")],
        drop=notthat.start + 0.15,
        stare=cls.end + 0.15,
        pris_cut=pris.start - 0.2,
        prisoner=ctx.find_word(pris.id, "prisoner"),
        hot_line=hot,
        bars_up=hot.start + 0.2,
        hot=ctx.find_word(hot.id, "hot"),
        crazy=ctx.find_word(hot.id, "crazy"),
        end=ctx.duration,
    )
    # the montage cuts must not run past the dash (the "See?" cut)
    b_["photo_end"] = b_["see"]
    return b_


def audio_cues(ctx):
    b = beats(ctx)
    cues = [{"sfx": "pop", "start": b["evidence"], "gain": 0.25}]
    for i, s in enumerate(b["photos"]):
        cues.append({"sfx": "shutter", "start": s, "gain": 0.32 if i else 0.4})
    cues += [
        {"sfx": "whoosh", "start": b["see"] - 0.05, "gain": 0.25},
        {"sfx": "whoosh", "start": b["class_cut"] - 0.05, "gain": 0.2},
        {"sfx": "music_bed", "start": b["class_cut"], "dur": b["cls"].end + 0.2 - b["class_cut"], "gain": 0.09,
         "fade_out": 0.05},
    ]
    for w in b["cls_words"]:
        cues.append({"sfx": "pop", "start": w + 0.05, "gain": 0.18})
    cues += [
        {"sfx": "thud", "start": b["drop"] + 0.45, "gain": 0.3},
        {"sfx": "slap", "start": b["notthat"].start + 0.05, "gain": 0.3},
        {"sfx": "gavel", "start": b["prisoner"] + 0.12, "gain": 0.45},
        {"sfx": "thud", "start": b["prisoner"] + 0.12, "gain": 0.35},
        {"sfx": "whoosh", "start": b["bars_up"], "gain": 0.15},
        {"sfx": "tick", "start": b["hot"], "gain": 0.2},
    ]
    return cues


# ------------------------------------------------------------------ montage tableaux (world 1280x720)
def _floor(cv, y, col):
    cv.rect(-200, y, 1480, 900, fill=col, outline=None)
    cv.line([(-200, y), (1480, y)], (70, 60, 66), 3)


def tab_calendar(cv, u, ctx):
    cv.rect(-200, -200, 1480, 900, fill=(242, 228, 200), outline=None)
    _floor(cv, 650, P.FLOOR_TILE)
    x, y = 420, 330
    cv.rect(x - 200, y - 230, x + 200, y + 230, fill=P.WHITE, ow=4)
    cv.rect(x - 200, y - 230, x + 200, y - 140, fill=P.ACCENT, ow=4)
    cv.text(x, y - 185, "SCHOOL DAY", 46, P.WHITE, "black")
    n = 1 + int(u * 10) % 30
    days = ["MON", "TUE", "WED", "THU", "FRI", "SAT"]
    cv.text(x, y + 30, str(n), 200, P.ACCENT, "black")
    cv.text(x, y + 175, days[(n - 1) % 6], 52, INK, "black")
    # torn pages flying off
    for k in range(3):
        f = (u * 3 + k / 3) % 1
        with cv.at(x + 80 + f * 520, y - 150 - f * 220 + math.sin(f * 7) * 30, 1 - f * 0.5, rot=f * 160):
            cv.rect(-70, -70, 70, 70, fill=P.WHITE, ow=3)
            cv.text(0, 0, str(max(1, n - k - 1)), 60, P.ACCENT, "black")
    draw_character(cv, "MUI", 960, 720, 2.6, outfit="uniform", expression="bored", t=u, look=(-0.8, 0))


def tab_wake(cv, u, ctx, again=False):
    cv.rect(-200, -200, 1480, 900, fill=(196, 216, 236), outline=None)
    _floor(cv, 640, (190, 160, 130))
    draw_window(cv, 80, 60, 360, 300, sky=(250, 220, 160))
    draw_sun(cv, 270, 140, 40, u, rays=False)
    draw_bed(cv, 560, 520, w=760)
    yawn = 0.25 + 0.75 * clamp(math.sin(clamp(u / 0.5) * math.pi))
    draw_character(cv, "MUI", 330, 492, 2.5, pose="sit", expression="bored" if not again else "deadpan",
                   mouth_open=yawn, t=u, blink=0.0, look=(0.3, 0.2))
    # sitting up in bed: the blanket covers his legs
    blank = (110, 160, 220)
    cv.poly([(250, 486), (340, 470), (430, 478), (560, 498), (950, 504), (952, 614), (248, 614)], fill=blank, ow=3.4)
    cv.line([(262, 500), (940, 514)], lerp_color(blank, P.WHITE, 0.4), 6)
    cv.rect(1000, 470, 1240, 680, fill=P.WOOD, ow=3.4)
    draw_alarm_clock(cv, 1120, 390, u, ringing=True, s=1.5)


def tab_brush(cv, u, ctx, again=False, look=(0.0, 0.25), mouth=0.0, expr="bored"):
    draw_tiles(cv, -200, -200, 1480, 900)
    draw_sink_mirror(cv, 640, 210)
    a = draw_character(cv, "MUI", 640, 905, 3.4, pose="hold", expression=expr, t=u, look=look,
                       mouth_open=mouth)
    hand = from_screen(cv, a["hand_r"])
    m = from_screen(cv, a["mouth"])
    draw_toothbrush(cv, hand, (m[0] + 18, m[1] + 4), t=u)
    draw_foam(cv, m[0] + 6, m[1] + 14, 2.0, u)
    draw_sink_front(cv, 640, 660)


def tab_breakfast(cv, u, ctx):
    cv.rect(-200, -200, 1480, 900, fill=(244, 214, 170), outline=None)
    _floor(cv, 640, P.FLOOR_TILE)
    draw_window(cv, 900, 70, 1160, 300, sky=(190, 230, 245))
    chew = 0.15 + 0.6 * abs(math.sin(u * 9))
    draw_character(cv, "MUI", 640, 664, 3.0, pose="sit_hold", props=("bowl",), outfit="uniform",
                   expression="bored", mouth_open=chew, t=u)
    draw_dinner_table(cv, 640, 640, w=980, dishes=True)


def tab_school(cv, u, ctx):
    cv.rect(-200, -200, 1480, 900, fill=(170, 220, 245), outline=None)
    _floor(cv, 600, P.GROUND)
    draw_school_gate(cv, 870, 600)
    x = lerp(230, 420, clamp(u / 0.8))
    s = 2.6
    draw_backpack(cv, x, 790, s, facing=1)
    draw_character(cv, "MUI", x, 790, s, pose="walk", outfit="uniform", expression="bored", t=u * 1.4)
    draw_backpack_straps(cv, x, 790, s, facing=1)


def tab_memorize(cv, u, ctx):
    with cv.at(640, 360, 1.25):
        with cv.at(-640, -330):
            draw_classroom(cv, u, board_lines=["2 × 2 = 4", "2 × 3 = 6", "2 × 4 = 8"], board_title="LESSON 5",
                           fan=False)
    draw_character(cv, "MUI", 640, 700, 2.4, pose="sit_chin_on_hand", outfit="uniform", expression="bored",
                   t=u, mouth_open=0.2 + 0.4 * abs(math.sin(u * 10)))
    for k in range(3):
        a = u * 2.5 + k * 2.1
        x = 640 + math.cos(a) * 330
        y = 330 + math.sin(a) * 90
        label(cv, x, y, "2 × 2 = 4", 40, bg=P.HIGHLIGHT, rot=math.sin(a) * 8)
    draw_desks(cv, 640, n=1, x0=640, w=640)


def tab_home(cv, u, ctx):
    cv.rect(-200, -200, 1480, 900, fill=(250, 170, 110), outline=None)
    draw_sun(cv, 1060, 440, 80, u, rays=False)
    cv.rect(-40, 40, 520, 660, fill=P.HOUSE_COLORS[1], ow=3.4)
    cv.rect(140, 300, 380, 660, fill=P.SHUTTER, ow=3.4)
    for k in range(1, 4):
        cv.line([(140 + 60 * k, 300), (140 + 60 * k, 660)], lerp_color(P.SHUTTER, INK, 0.3), 3)
    cv.rect(50, 100, 430, 230, fill=(250, 200, 140), ow=3)
    cv.text(240, 165, "HOME", 64, P.ACCENT, "black")
    _floor(cv, 660, (226, 170, 120))
    x = lerp(900, 700, clamp(u / 0.8))
    s = 2.6
    draw_backpack(cv, x, 800, s, facing=-1)
    draw_character(cv, "MUI", x, 800, s, pose="walk", outfit="uniform", expression="deadpan", t=u * 1.2,
                   flip=True)
    draw_backpack_straps(cv, x, 800, s, facing=-1)


def tab_homework(cv, u, ctx, more=False):
    cv.rect(-200, -200, 1480, 900, fill=(110, 116, 170), outline=None)
    _floor(cv, 640, (90, 80, 110))
    draw_window(cv, 80, 60, 330, 300, night=True)
    draw_desk_lamp(cv, 1000, 610, on=True, s=1.6)
    draw_character(cv, "MUI", 560, 690, 2.4, pose="sit_hold", props=("notebook",), outfit=None,
                   expression="deadpan" if more else "bored", t=u,
                   look=(0.0, 0.7) if not more else (0.7, -0.5))
    cv.rect(140, 610, 1180, 656, fill=P.WOOD, radius=4)
    cv.rect(160, 656, 1160, 800, fill=P.WOOD_DARK)
    if more:
        d = ease_out(clamp(u / 0.14))
        y = lerp(-500, 610, d)
        draw_notebook_stack(cv, 840, y, n=20, w=200, seed=2)
        # Mom's giant arm reaches in from off-frame and points at the pile
        reach = ease_out_back(clamp((u - 0.1) / 0.25), 1.3)
        hx, hy = lerp(1420, 985, reach), lerp(120, 250, reach)
        cv.rect(1200, -100, 1500, 170, fill=char_spec("MOM")["shirt"], ow=4)          # a sliver of her shirt
        cv.line([(1230, 120), (hx, hy)], INK, 17)
        cv.circle(hx, hy, 27, fill=(251, 227, 214), ow=4)


def tab_bed(cv, u, ctx):
    cv.rect(-200, -200, 1480, 900, fill=(52, 58, 104), outline=None)
    _floor(cv, 640, (40, 40, 70))
    draw_window(cv, 900, 60, 1160, 300, night=True)
    draw_bed(cv, 640, 470, w=900, night=True, blanket=False)
    # lying on his back, head on the pillow, tucked in to the chest
    with cv.at(665, 432, 1, rot=-90):
        draw_character(cv, "MUI", 0, 0, 2.6, pose="stand", expression="neutral", blink=1.0, t=0)
    # blanket pulled up to his chin (bulges over the body)
    blank = (60, 80, 150)
    top = [(392, 404), (520, 386), (700, 392), (900, 404), (1100, 412)]
    cv.poly(top + [(1104, 524), (388, 524)], fill=blank, ow=3.4)
    cv.line([(396, 420), (1098, 428)], lerp_color(blank, P.WHITE, 0.35), 6)
    for k in range(3):
        f = (u * 1.5 + k / 3) % 1
        cv.text(300 + f * 140 + k * 10, 260 - f * 170, "z", 50 + f * 40, P.WHITE, "black")


def _montage(ctx):
    """(caption, draw_fn, tone, rot) per photo, in order."""
    return [
        ("EVERY DAY", tab_calendar, (240, 226, 200), -2.5),
        ("WAKE UP", tab_wake, (196, 216, 236), 2.0),
        ("BRUSH TEETH", tab_brush, (190, 228, 222), -1.5),
        ("EAT BREAKFAST", tab_breakfast, (244, 214, 170), 2.8),
        ("GO TO SCHOOL", tab_school, (170, 220, 245), -3.0),
        ("MEMORIZE THINGS", tab_memorize, (250, 226, 150), 1.5),
        ("COME HOME", tab_home, (250, 170, 110), -2.0),
        ("HOMEWORK", tab_homework, (110, 116, 170), 3.0),
        ("MORE HOMEWORK", lambda cv, u, c: tab_homework(cv, u, c, more=True), (110, 116, 170), -2.5),
        ("GO TO BED", tab_bed, (52, 58, 104), 2.0),
        ("WAKE UP (AGAIN)", lambda cv, u, c: tab_wake(cv, u, c, again=True), (196, 216, 236), -1.0),
        ("BRUSH TEETH (AGAIN)", lambda cv, u, c: tab_brush(cv, u, c, again=True), (190, 228, 222), 2.5),
    ]


def _photo_pos(i):
    rnd = random.Random(40 + i)
    return 640 + rnd.uniform(-40, 40), 352 + rnd.uniform(-14, 14)


def render_montage(t, ctx, b, cv):
    corkboard(cv, t)
    # "DAY" sticky note on the board corner
    photos = _montage(ctx)
    starts = b["photos"]
    idx = max([i for i, s in enumerate(starts) if t >= s], default=-1)
    day = 2 if idx >= 10 else 1
    with cv.at(1190, 70, 1, rot=6):
        cv.rect(-70, -40, 70, 40, fill=P.HIGHLIGHT, ow=3)
        cv.text(0, 2, f"DAY {day}", 32, INK, "black")
    pin(cv, 1190, 40)

    # intro: EXHIBIT A sign, Mui presenting it
    if idx < 0:
        with cv.at(470, 300, 1, rot=-2):
            cv.rect(-300, -150, 300, 150, fill=P.PAPER, ow=4)
            cv.text(0, -70, "EXHIBIT A", 72, P.ACCENT, "black")
            cv.text(0, 20, "A DAY IN THE LIFE", 42, INK, "black")
            cv.text(0, 80, "OF MUI (AGE 8)", 42, INK, "black")
        pin(cv, 470, 162)
        s = pop(t, b["evidence"] - 0.05, 0.35)
        draw_character(cv, "MUI", 1010, 690, 1.65, pose="point", props=("pointer",), flip=True,
                       expression="deadpan", mouth_open=0, t=t, look=(-0.5, 0) if t < b["intro"].end else (0, 0))
        label(cv, 1010, 160, "EVIDENCE", 30, bg=P.HIGHLIGHT, scale=s, rot=5)

    # older photos (cheap stand-ins), then the newest one slapping down
    for j in range(max(0, idx - 2), idx):
        cap, fn, tone, rot = photos[j]
        x, y = _photo_pos(j)
        photo_back(cv, x, y, rot=rot, tone=tone)
    if idx >= 0:
        cap, fn, tone, rot = photos[idx]
        x, y = _photo_pos(idx)
        p = ease_out(progress(t, starts[idx], 0.12))
        sc = lerp(1.22, 1.0, p)
        r = lerp(rot + 7 * (1 if idx % 2 else -1), rot, p)
        u = t - starts[idx]
        cap_col = P.ACCENT if "AGAIN" in cap else INK
        polaroid(cv, lambda sub: fn(sub, u, ctx), x, y, rot=r, scale=sc, caption=cap, cap_color=cap_col)
        pin(cv, x, y - 300 * sc + 6, (60, 120, 210) if idx % 2 else P.ACCENT)
    img = cv.finish()
    if idx >= 0:
        img = flash(img, 0.35 * (1 - progress(t, starts[idx], 0.1)))
    return img


# ------------------------------------------------------------------ "See?"
def render_see(t, ctx, b, cv):
    u = t - b["see"]
    z = lerp(1.75, 1.85, ease_in_out(progress(t, b["see"], 1.0)))
    with cv.camera(640, 400, z):
        mouth = ctx.mouth("MUI", t)
        tab_brush(cv, t, ctx, look=(0, 0), mouth=mouth, expr="deadpan")
    return cv.finish()


# ------------------------------------------------------------------ classroom
def _class_cam(t, b):
    z = lerp(1.0, 1.04, ease_in_out(progress(t, b["class_cut"], 6)))
    cx, cy = 640, 360
    # push in on the teacher for "...Not that part."
    p = ease_in_out(progress(t, b["stare"], 0.5))
    cx, cy, z = lerp(cx, 360, p), lerp(cy, 300, p), lerp(z, 1.45, p)
    return cx, cy, z


def render_class(t, ctx, b, cv):
    cam = _class_cam(t, b)
    rep, cls, nt = b["rep"], b["cls"], b["notthat"]
    anchors = {}
    with cv.camera(*cam):
        draw_classroom(cv, t, board_lines=["2 × 2 = 4", "2 × 3 = 6"], board_title="LESSON 5", fan=True)
        # back row of classmates (smaller, partly hidden)
        for i, x in enumerate((650, 830, 1010, 1190)):
            col = [(240, 240, 236), (236, 240, 250), (250, 244, 236), (240, 250, 240)][i]
            draw_character(cv, "KID", x, 590, 1.1, pose="sit", colors={"shirt": col}, t=t + i * 0.7,
                           variant={"scarf": True, "hair": "bob" if i % 2 else "short",
                                    "bottom": "shorts"},
                           mouth_open=ctx.mouth("MUI", t) * 0.9, expression="neutral")
        draw_desks(cv, 575, n=4, x0=650, gap=180, w=160)
        for i, (nm, x, kw) in enumerate(CLASS_KIDS):
            expr = "bored" if nm == "MUI" else ("neutral" if nm == "KID" else None)
            if t >= nt.start - 0.6 and t < b["pris_cut"]:
                expr = {"MUI": "bored", "HAI": "smug", "TUN": "happy", "TI": "happy"}.get(nm, "neutral")
            m = ctx.mouth(nm if nm != "KID" else "MUI", t)
            a = draw_character(cv, nm, x, 712, 1.4, pose="sit", expression=expr, mouth_open=m,
                               t=t + i * 0.37, look=(-0.6, -0.2) if t < cls.start or t >= b["stare"] else (0, 0),
                               **kw)
            anchors[nm + str(i)] = a
        draw_desks(cv, 684, n=4, x0=560, gap=180, w=170)
        # the giant teacher, left, head near the top of frame
        if t < nt.start:
            pose, props, expr = ("point", ("pointer",), "neutral") if t < rep.end + 0.3 else ("stand", (), "neutral")
            if t >= b["stare"]:
                expr = "deadpan"
        else:
            pose, props, expr = "facepalm", (), "deadpan"
        ta = draw_character(cv, "TEACHER", 210, 790, 1.62, pose=pose, props=props, expression=expr,
                            mouth_open=ctx.mouth("TEACHER", t), t=t,
                            look=(0.6, 0.1) if t < b["stare"] else (0, 0))
    # teacher's bubble (screen space)
    if rep.start - 0.1 <= t < cls.start - 0.05:
        s = pop(t, rep.start - 0.1, 0.3)
        hx, hy = ta["head"]
        speech_bubble(cv, hx + 60, hy - 250, "Repeat after me.", tail=(-20, 90), size=30, scale=s)
    # chant tiles: every kid emits the same word, they land in perfect rows
    if cls.start - 0.1 <= t < b["drop"] + 1.2:
        fall = progress(t, b["drop"], 0.6)
        # rows are laid out in screen space for the camera at the start of the chant, so they stay put
        # (and inside the frame) when the camera later pushes in on the teacher
        cam0 = _class_cam(cls.start, b)
        for row, (word, ws) in enumerate(zip(CHANT, b["cls_words"])):
            p = ease_out_back(progress(t, ws - 0.05, 0.35), 1.4)
            if p <= 0:
                continue
            for i, (nm, x, kw) in enumerate(CLASS_KIDS):
                mx, my = anchors[nm + str(i)]["mouth"]
                tx, ty = cv_to_screen_x(x, cam0), 180 + row * 64
                px, py = lerp(mx, tx, p), lerp(my, ty, p)
                rot = 0
                if fall > 0:
                    rnd = random.Random(row * 10 + i)
                    py += ease_in(fall) * (700 + rnd.uniform(0, 200))
                    rot = fall * rnd.uniform(-90, 90)
                label(cv, px, py, word, 24, bg=P.WHITE, scale=clamp(0.4 + 0.6 * p, 0, 1.2), rot=rot)
    return cv.finish()


def cv_to_screen_x(x, cam):
    cx, cy, z = cam
    return (x - cx) * z + 640


# ------------------------------------------------------------------ prisoner / hot afternoon
def render_prison(t, ctx, b, cv):
    hot_p = ease_in_out(progress(t, b["hot"] - 0.1, 0.8))
    jail = t >= b["prisoner"] + 0.1
    z = lerp(1.0, 1.06, ease_in_out(progress(t, b["pris_cut"], 8)))
    with cv.camera(640, 360, z):
        cv.rect(-200, -200, 1480, 900, fill=lerp_color((250, 226, 150), (255, 200, 120), hot_p * 0.6),
                outline=None)
        cv.rect(-200, 560, 1480, 900, fill=P.WALL_GREEN, outline=None)
        # barred classroom window, hot sky
        sky = lerp_color((180, 225, 245), (255, 214, 120), hot_p)
        cv.rect(80, 70, 600, 470, fill=sky, outline=(70, 60, 66), ow=5)
        draw_sun(cv, 340, 250, lerp(46, 120, hot_p), t * (1 + 3 * hot_p), rays=True)
        if hot_p > 0:
            heat_waves(cv, 120, 560, 460, t, n=6, col=(255, 236, 180))
        for k in range(1, 7):
            xx = 80 + 520 * k / 7
            cv.line([(xx, 70), (xx, 470)], (80, 80, 90), 7)
        cv.line([(80, 270), (600, 270)], (70, 60, 66), 5)
        # wall clock barely moving
        cv.circle(1140, 120, 46, fill=P.WHITE, ow=3.4)
        cv.line([(1140, 120), (1140, 86)], INK, 4)
        cv.line([(1140, 120), (1166, 132)], INK, 4)
        cv.text(1140, 196, "2:00 PM", 22, INK, "black")
        # Mui at his desk
        colors = JUMPSUIT if jail else None
        look = (-0.8, -0.3)          # gazing at the barred window
        lp = ease_in_out(progress(t, b["crazy"], 0.6))
        look = (lerp(look[0], 0, lp), lerp(look[1], 0, lp))
        expr = "bored" if not jail else ("sad" if hot_p < 0.5 else "deadpan")
        a = draw_character(cv, "MUI", 890, 668, 3.3, pose="sit_chin_on_hand", outfit=None if jail else "uniform",
                           colors=colors, expression=expr, t=t, look=look, mouth_open=0)
        if hot_p > 0:
            hx, hy = a["head"]
            hr = a["head_r"]
            for k in range(3):
                sweat(cv, hx + (-1) ** k * hr * (0.95 - k * 0.1), hy - hr * (0.4 - k * 0.3), 1.2, t, 1.1, k)
        cv.rect(560, 600, 1200, 640, fill=P.WOOD, radius=4)
        cv.rect(580, 640, 1180, 760, fill=P.WOOD_DARK)
        if jail:
            cv.rect(780, 660, 980, 712, fill=P.WHITE, ow=3)
            cv.text(880, 687, "INMATE #08", 26, INK, "black")
        # ceiling fan (useless, slow)
        cx_, cy_ = 860, 34
        cv.line([(cx_, -60), (cx_, cy_)], (70, 60, 66), 5)
        sp = t * lerp(4, 1.2, hot_p)
        for k in range(3):
            a_ = sp + k * 2 * math.pi / 3
            ex = cx_ + math.cos(a_) * 220
            cv.poly([(cx_, cy_ - 6), (ex, cy_ - 10 + math.sin(a_) * 6), (ex, cy_ + 12 + math.sin(a_) * 6),
                     (cx_, cy_ + 6)], fill=(230, 230, 230), outline=(70, 60, 66), ow=2)
        cv.circle(cx_, cy_, 20, fill=(200, 200, 205), outline=(70, 60, 66), ow=2.4)
    # foreground cell bars slam down on "prisoner", lift on the next line
    drop = ease_out_back(progress(t, b["prisoner"], 0.16), 1.2) * (1 - ease_in_out(progress(t, b["bars_up"], 0.5)))
    jail_bars(cv, drop)
    img = cv.finish()
    if hot_p > 0:
        img = tint(img, (255, 150, 40), 0.12 * hot_p)
    fl = 1 - progress(t, b["prisoner"] + 0.1, 0.25)
    if t >= b["prisoner"] + 0.1 and fl > 0:
        img = flash(img, 0.6 * fl)
    return img


# ------------------------------------------------------------------ frame
def render_frame(t, ctx):
    b = beats(ctx)
    if t < b["see"]:
        return render_montage(t, ctx, b, ctx.canvas((196, 150, 100)))
    if t < b["class_cut"]:
        return render_see(t, ctx, b, ctx.canvas(P.WHITE))
    if t < b["pris_cut"]:
        return render_class(t, ctx, b, ctx.canvas(P.WALL_WARM))
    return render_prison(t, ctx, b, ctx.canvas(P.WALL_WARM))
