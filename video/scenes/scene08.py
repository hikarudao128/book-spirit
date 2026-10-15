"""Scene 8 - The Rules of Childhood.

Beats (all from ctx):
  "So here's how childhood works."  the three-node cycle diagram builds on the left
  "Renaming everything went badly." / "Becoming adults went worse." /
  "And suing your parents went exactly how you'd expect."
      three thumbnail cards pop on the right, each with a HOW IT WENT meter that escalates:
      BADLY -> WORSE -> the third meter overflows on "went exactly", the gavel slams and the
      "...AS EXPECTED" stamp lands on "expect"
  "Then they tried raising stray dogs as house pets."  whip-pan to the alley: scruffy dogs pile in
      around the kids, a puppy lands on Mui's head
  HAI "Can we keep them?"  pleading sparkly eyes
  (gap) Dad stomps in, giant.  DAD "No."  deadpan hold, kids deflate
  whip-pan back to the diagram, centred.  Little Mui runs node to node in sync with
  "Kids have an idea." / "Adults find out." / "Everything goes back to normal."
  "And repeat."  Mui laps the loop faster and faster (accelerating ticks)
"""
import math

from lib import palette as P
from lib.backgrounds import draw_alley, draw_gavel, draw_plastic_stool
from lib.characters import draw_character, draw_dog
from lib.core import INK, clamp, ease_in_out, ease_out, ease_out_back, lerp, lerp_color, pop, progress
from lib.extra_s8_11 import arrow_head, blink, draw_bulb, draw_star_burst
from lib.fx import shake
from lib.text import label, speech_bubble, text_width

NODE_ANG = (-90, 30, 150)
NODE_TXT = ("KIDS HAVE IDEA", "ADULTS FIND OUT", "EVERYTHING BACK\nTO NORMAL")
NODE_COL = (P.HIGHLIGHT, P.ACCENT, (170, 200, 230))


def beats(ctx):
    L = [ctx.line(i) for i in range(11)]
    b = dict(L=L)
    b["nodes"] = (ctx.find_word(L[0].id, "here"), ctx.find_word(L[0].id, "childhood"),
                  ctx.find_word(L[0].id, "works"))
    b["cards"] = (L[1].start, L[2].start, L[3].start)
    b["results"] = (ctx.find_word(L[1].id, "badly"), ctx.find_word(L[2].id, "worse"),
                    ctx.find_word(L[3].id, "expect"))
    b["overflow"] = ctx.find_word(L[3].id, "went")
    b["expect"] = ctx.find_word(L[3].id, "expect")
    b["cut1"] = L[4].start - 0.25                       # whip to the dogs
    b["dogs"] = ctx.find_word(L[4].id, "stray")
    b["pets"] = ctx.find_word(L[4].id, "pets")
    b["plead"] = L[5].start - 0.2
    b["dad_in"] = L[5].end + 0.25
    b["no"] = L[6].start
    b["deflate"] = L[6].end + 0.05
    b["cut2"] = L[7].start - 0.35                       # whip back to the diagram
    b["idea"], b["find"], b["normal"], b["repeat"] = L[7].start, L[8].start, L[9].start, L[10].start
    return b


# ------------------------------------------------------------------ token path (Mui running the loop)
OMEGA0, ALPHA = 220.0, 520.0     # deg/s, deg/s^2 for "And repeat."


def _theta(t, b):
    th = -90.0
    th += 120 * ease_in_out(progress(t, b["find"] + 0.05, 0.55))
    th += 120 * ease_in_out(progress(t, b["normal"] + 0.05, 0.6))
    u = max(0.0, t - b["repeat"])
    th += OMEGA0 * u + 0.5 * ALPHA * u * u
    return th


def _speed(t, b):
    u = max(0.0, t - b["repeat"])
    if u > 0:
        return OMEGA0 + ALPHA * u
    for k, d in (("find", 0.55), ("normal", 0.6)):
        p = progress(t, b[k] + 0.05, d)
        if 0 < p < 1:
            return 120 / d * 1.5 * math.sin(math.pi * p)
    return 0.0


def _pass_times(b, end):
    """Times at which the runner crosses a node during the repeat laps (for tick sfx)."""
    out = []
    k = 1
    while True:
        dth = 120 * k                                  # node every 120 deg past 150
        u = (-OMEGA0 + math.sqrt(OMEGA0 ** 2 + 2 * ALPHA * dth)) / ALPHA
        tt = b["repeat"] + u
        if tt > end:
            return out
        out.append(tt)
        k += 1


def audio_cues(ctx):
    b = beats(ctx)
    cues = [{"sfx": "music_bed", "start": 0.0, "dur": b["cut1"] + 0.1, "gain": 0.13, "fade_out": 0.3}]
    for tt in b["nodes"]:
        cues.append({"sfx": "pop", "start": tt, "gain": 0.25})
    for tt in b["cards"]:
        cues.append({"sfx": "whoosh", "start": tt - 0.05, "gain": 0.15})
    cues += [{"sfx": "thud", "start": b["results"][0], "gain": 0.3},
             {"sfx": "thud", "start": b["results"][1], "gain": 0.4},
             {"sfx": "boing", "start": b["overflow"] + 0.15, "gain": 0.3},
             {"sfx": "slap", "start": b["expect"], "gain": 0.4},
             {"sfx": "whoosh", "start": b["cut1"] - 0.05, "gain": 0.3}]
    for i in range(6):
        cues.append({"sfx": "pop", "start": _dog_in(b, i) + 0.35, "gain": 0.16})
    cues += [{"sfx": "boing", "start": _dog_in(b, 6) + 0.45, "gain": 0.3},
             {"sfx": "thud", "start": b["dad_in"] + 0.15, "gain": 0.45},
             {"sfx": "thud", "start": b["dad_in"] + 0.5, "gain": 0.55},
             {"sfx": "record_scratch", "start": b["no"] + 0.05, "gain": 0.12},
             {"sfx": "whoosh", "start": b["cut2"] - 0.05, "gain": 0.3},
             {"sfx": "ding", "start": b["idea"] + 0.1, "gain": 0.18},
             {"sfx": "slap", "start": b["find"] + 0.55, "gain": 0.3},
             {"sfx": "tick", "start": b["normal"] + 0.65, "gain": 0.4},
             {"sfx": "music_bed", "start": b["cut2"], "dur": ctx.duration - b["cut2"], "gain": 0.12,
              "fade_out": 0.8}]
    for tt in _pass_times(b, ctx.duration - 0.1):
        cues.append({"sfx": "tick", "start": tt, "gain": 0.35})
    return cues


# ------------------------------------------------------------------ diagram
def _node_icon(cv, i, x, y, s, t, glow=0.0):
    if s <= 0.01:
        return
    with cv.at(x, y, s):
        r = 50
        if glow > 0:
            cv.circle(0, 0, r + 14 * glow, fill=lerp_color(P.CARD_BG, NODE_COL[i], 0.6), outline=None)
        cv.circle(0, 0, r, fill=P.WHITE, ow=4)
        if i == 0:
            draw_bulb(cv, 0, 4, 0.72, glow=0.4 + 0.6 * glow)
        elif i == 1:      # an adult face that found out
            cv.circle(0, 2, 30, fill=P.SKIN_ADULT, ow=3)
            cv.poly([(-30, -4), (-28, -26), (0, -34), (28, -26), (30, -4), (14, -18), (-14, -18)], fill=P.HAIR,
                    ow=2.5)
            for sd in (-1, 1):
                cv.circle(sd * 11, 4, 8, fill=None, ow=2.4)
                cv.circle(sd * 11, 5, 2.6, fill=INK, outline=None)
                cv.line([(sd * 4, -6), (sd * 18, -11)], INK, 3)
            cv.line([(-9, 20), (0, 17), (9, 20)], INK, 3)
            cv.rect(34, -36, 44, -6, fill=P.ACCENT, ow=2.4, radius=3)
            cv.circle(39, 4, 5, fill=P.ACCENT, ow=2.4)
        else:             # reset: circular arrow around a flat face
            cv.circle(0, 0, 28, fill=(250, 226, 170), ow=3)
            for sd in (-1, 1):
                cv.line([(sd * 13 - 6, -2), (sd * 13 + 6, -2)], INK, 3)
            cv.line([(-9, 13), (9, 13)], INK, 3)
            pts = [(math.cos(math.radians(a)) * 40, math.sin(math.radians(a)) * 40) for a in range(-60, 230, 10)]
            cv.line(pts, NODE_COL[2] if glow == 0 else P.ACCENT2, 5)
            arrow_head(cv, pts[-1][0], pts[-1][1], 140, 13, NODE_COL[2] if glow == 0 else P.ACCENT2)


def _node_label(cv, i, x, y, s):
    if s <= 0.01:
        return
    lines = NODE_TXT[i].split("\n")
    size = 21
    w = max(text_width(l, size, "black") for l in lines) + 30
    h = len(lines) * size * 1.15 + 16
    with cv.at(x, y, s):
        cv.rect(-w / 2 + 4, -h / 2 + 5, w / 2 + 4, h / 2 + 5, fill=INK, outline=None, radius=10)
        cv.rect(-w / 2, -h / 2, w / 2, h / 2, fill=NODE_COL[i], radius=10)
        for k, l in enumerate(lines):
            cv.text(0, -h / 2 + 9 + size * 0.6 + k * size * 1.15, l, size, INK if i != 1 else P.WHITE, "black")


def draw_cycle(cv, t, b, cx, cy, R, shows, arrows, glows=(0, 0, 0), label_scale=1.0):
    """shows: pop scale per node; arrows: 0..1 growth per arrow (node i -> i+1)."""
    # arrows (arcs) behind the nodes
    gap = 24
    for i in range(3):
        a0 = NODE_ANG[i] + gap
        a1 = NODE_ANG[i] + 120 - gap
        g = arrows[i]
        if g <= 0.01:
            continue
        a_end = lerp(a0, a1, g)
        n = max(2, int((a_end - a0) / 4))
        pts = [(cx + R * math.cos(math.radians(lerp(a0, a_end, k / n))),
                cy + R * math.sin(math.radians(lerp(a0, a_end, k / n)))) for k in range(n + 1)]
        cv.line(pts, INK, 15)
        cv.line(pts, (120, 110, 120), 9)
        ex, ey = pts[-1]
        arrow_head(cv, ex, ey, a_end + 90, 26, (120, 110, 120))
    for i in range(3):
        a = math.radians(NODE_ANG[i])
        x, y = cx + R * math.cos(a), cy + R * math.sin(a)
        _node_icon(cv, i, x, y, shows[i], t, glows[i])
        if i == 0:
            lx, ly = x, y - 92
        else:                         # below the bottom arc, nudged outward
            lx, ly = x + (40 if i == 1 else -40), cy + R + (40 if i == 1 else 52)
        _node_label(cv, i, lx, ly, shows[i] * label_scale)


# ------------------------------------------------------------------ attempt cards
CARD_TXT = ("RENAMING EVERYTHING", "BECOMING ADULTS", "SUING YOUR PARENTS")
RESULT = ("BADLY", "WORSE", "...AS EXPECTED")
LEVEL = (0.42, 0.78, 1.0)
RES_COL = ((240, 150, 50), P.ACCENT, (150, 20, 30))


def _thumb(cv, i, x, y, t, b):
    cv.rect(x - 66, y - 62, x + 66, y + 62, fill=(214, 236, 245) if i < 2 else (236, 214, 176), radius=8, ow=3)
    if i == 0:
        cv.rect(x - 64, y + 30, x + 64, y + 60, fill=P.GROUND, outline=None)
        draw_dog(cv, x - 12, y + 44, 0.68, pose="wag", t=t, mouth_prop="notebook")
    elif i == 1:
        cv.rect(x - 64, y + 30, x + 64, y + 60, fill=P.GROUND, outline=None)
        draw_character(cv, "TI", x, y + 50, 0.58, outfit="snow_white", props=("crown",), pose="hands_hip",
                       expression="proud", t=t, blink=blink(t, 3))
    else:
        draw_plastic_stool(cv, x + 4, y + 52, P.PLASTIC_RED, 0.95, label=None)
        cv.text(x + 4, y + 28, "DAD", 15, P.WHITE, "black")
        hit = progress(t, b["results"][2] - 0.25, 0.25)
        draw_gavel(cv, x + 42, y + 2, rot=lerp(40, -58, ease_out(hit)) + math.sin(t * 6) * 3 * (1 - hit), scale=0.55)
        if hit >= 1:
            draw_star_burst(cv, x - 10, y - 18, 20, P.HIGHLIGHT, 8, rot=t * 40)
    cv.rect(x - 66, y - 62, x + 66, y + 62, fill=None, radius=8, ow=3.4)


def draw_card(cv, i, x, y, t, b):
    s = pop(t, b["cards"][i] - 0.05, 0.4)
    if s <= 0.01:
        return
    res_t = b["results"][i]
    shk = (0, 0)
    if i == 2:
        q = progress(t, b["overflow"] + 0.1, 1.6) * (1 - progress(t, b["expect"] + 0.6, 0.4))
        shk = shake(t, 5 * q, 30, seed=2)
    w, h = 460, 156
    with cv.at(x + shk[0], y + shk[1], s, rot=(-1.5, 1.2, -1.0)[i]):
        cv.rect(-w / 2 + 7, -h / 2 + 8, w / 2 + 7, h / 2 + 8, fill=INK, outline=None, radius=14)
        cv.rect(-w / 2, -h / 2, w / 2, h / 2, fill=P.WHITE, radius=14, ow=3.4)
        _thumb(cv, i, -w / 2 + 82, 0, t, b)
        tx = -w / 2 + 166
        cv.text(tx, -46, CARD_TXT[i], 23, INK, "black", anchor="lm")
        cv.text(tx, -14, "HOW IT WENT:", 15, (120, 110, 120), "extrabold", anchor="lm")
        # meter
        mx0, mx1, my = tx, w / 2 - 22, 18
        cv.rect(mx0, my - 13, mx1, my + 13, fill=(236, 230, 220), radius=13, ow=3)
        if i < 2:
            fill = LEVEL[i] * ease_out(progress(t, res_t - 0.55, 0.6))
        else:
            fill = ease_out(progress(t, b["overflow"], 0.5)) + 0.9 * ease_out_back(
                progress(t, b["overflow"] + 0.45, 0.6), 2.5)
        if fill > 0.02:
            col = lerp_color((120, 200, 110), RES_COL[i], clamp(fill / 0.8))
            fx = mx0 + (mx1 - mx0) * fill
            cv.rect(mx0, my - 13, max(mx0 + 26, fx), my + 13, fill=col, radius=13, ow=3)
            if fill > 1.0:   # bursting out of the card
                draw_star_burst(cv, mx1 + 8, my, 30 + 5 * math.sin(t * 20), P.HIGHLIGHT, 9, rot=t * 90)
                cv.text(mx1 - 40, my - 34, "!!", 26, P.ACCENT, "black")
        # result stamp
        rs = pop(t, res_t, 0.3) if i < 2 else pop(t, b["expect"], 0.3)
        if rs > 0.01:
            with cv.at(tx + 196 if i < 2 else tx + 148, 54, rs, rot=-6):
                txt = RESULT[i]
                sz = 24 if i < 2 else 23
                tw = text_width(txt, sz, "black") + 22
                cv.rect(-tw / 2, -17, tw / 2, 17, fill=P.WHITE, outline=RES_COL[i], ow=3.5, radius=5)
                cv.text(0, 1, txt, sz, RES_COL[i], "black")


# ------------------------------------------------------------------ phase A / C
def _paper(cv):
    cv.rect(-10, -10, 1290, 730, fill=P.CARD_BG, outline=None)
    for gx in range(0, 1281, 40):
        cv.line([(gx, 0), (gx, 720)], (244, 234, 210), 1.5)
    for gy in range(0, 721, 40):
        cv.line([(0, gy), (1280, gy)], (244, 234, 210), 1.5)


def phase_a(cv, t, b):
    _paper(cv)
    shows = [pop(t, b["nodes"][i] - 0.05, 0.4) for i in range(3)]
    # each arrow grows into the next node as that node pops (never ahead of it); the last closes the loop
    arrows = [ease_out(progress(t, b["nodes"][1], 0.35)), ease_out(progress(t, b["nodes"][2], 0.35)),
              ease_out(progress(t, b["nodes"][2] + 0.3, 0.5))]
    draw_cycle(cv, t, b, 345, 360, 185, shows, arrows)
    hs = pop(t, b["cards"][0] - 0.3, 0.35)
    if hs > 0.01:
        label(cv, 1010, 62, "PREVIOUS ATTEMPTS", 24, bg=INK, fill=P.WHITE, scale=hs)
    for i, y in enumerate((200, 380, 560)):
        draw_card(cv, i, 1010, y, t, b)


def phase_c(cv, t, b, ctx):
    _paper(cv)
    cx, cy, R = 640, 380, 240
    TR = R - 145                    # inner track; Mui's head stays clear of the top node's glow ring
    FOOT = 84                       # feet below the track point so the figure is centred on it
    th = _theta(t, b)
    spd = _speed(t, b)
    # node glow when the runner is at / near it
    glows = []
    for i in range(3):
        d = abs(((th - NODE_ANG[i]) + 180) % 360 - 180)
        glows.append(clamp(1 - d / 40))
    draw_cycle(cv, t, b, cx, cy, R, (1, 1, 1), (1, 1, 1), glows)
    for k in range(36):             # dotted running track
        a = math.radians(k * 10)
        cv.circle(cx + TR * math.cos(a), cy + TR * math.sin(a) + FOOT, 4, fill=(220, 205, 180), outline=None)
    # runner trail
    if spd > 200:
        n = int(clamp((spd - 200) / 1400) * 18) + 3
        for k in range(n):
            a = math.radians(th - (k + 1) * clamp(spd / 24 / n, 0, 14))
            rr = 18 * (1 - k / n) + 4
            cv.circle(cx + TR * math.cos(a), cy + TR * math.sin(a) - 10, rr,
                      fill=lerp_color(P.SHIRT_BLUE, P.CARD_BG, k / n), outline=None)
    a = math.radians(th)
    mx, my = cx + TR * math.cos(a), cy + TR * math.sin(a)
    vx = -math.sin(a)
    running = spd > 5
    dizzy = progress(t, b["repeat"] + 1.6, 1.0)
    draw_character(cv, "MUI", mx, my + FOOT, 0.76, pose="run" if running else "stand", t=t * (1 + spd / 400),
                   flip=vx < -0.05, expression="bored" if dizzy < 0.5 else "scared", blink=blink(t, 1),
                   look=(0, 0) if dizzy < 0.5 else (math.sin(t * 9), math.cos(t * 9)))
    # loop count
    laps = max(0, int((th - 150) // 360) + 1) if t > b["repeat"] else 0
    if t >= b["repeat"]:
        label(cv, 1110, 120, f"LOOP x{max(1, laps)}", 40, fill=P.WHITE, bg=P.ACCENT, scale=pop(t, b["repeat"], 0.3))
    # title on top
    label(cv, 170, 60, "THE RULES OF CHILDHOOD", 22, bg=P.WHITE, scale=pop(t, b["cut2"] + 0.2, 0.35))


# ------------------------------------------------------------------ phase B: the dogs
GROUND = 560
CAM_B = (640, 482, 1.25)
KIDS_B = [("MUI", 480, 0.95), ("HAI", 620, 0.95), ("TUN", 760, 0.95), ("TI", 880, 0.95)]
DOGS = [  # final x, y, scale, color, flip, from_side, pose
    (380, 700, 0.62, (196, 150, 100), False, -1, "sit"),
    (560, 728, 0.7, (120, 100, 90), False, -1, "wag"),
    (700, 742, 0.66, (232, 214, 186), True, 1, "wag"),
    (950, 735, 0.72, (60, 56, 60), True, 1, "sit"),     # beside Ti, not on her feet
    (330, 735, 0.6, (222, 168, 96), False, -1, "wag"),
    (455, 750, 0.58, (176, 120, 80), False, -1, "wag"),
]


def _dog_in(b, i):
    if i < 3:
        return b["dogs"] - 0.15 + i * 0.32
    if i < 6:
        return b["pets"] - 0.35 + (i - 3) * 0.28
    return b["pets"] + 0.55            # the puppy that lands on Mui's head


def scruffy_dog(cv, x, y, s, color, flip, pose, t, seed):
    draw_dog(cv, x, y, s, flip=flip, pose=pose, t=t + seed, color=color)
    dark = lerp_color(color, INK, 0.35)
    with cv.at(x, y, s, flip=flip):
        if pose != "sit":
            cv.ellipse(-12 + seed * 3 % 14, -56, 14, 9, fill=dark, outline=None)
            for k in range(4):
                bx = -30 + k * 14
                cv.line([(bx, -68), (bx + 4, -78), (bx + 8, -69)], INK, 2.2)
            cv.line([(36, -96), (42, -106), (47, -96)], INK, 2.2)
        else:
            cv.ellipse(0, -50, 10, 8, fill=dark, outline=None)
            cv.line([(16, -106), (22, -116), (28, -106)], INK, 2.2)


def phase_b(cv, t, b, ctx):
    for k in range(8):   # sky in local coords so it slides with the whip pans (draw_sky pastes screen-space)
        cv.rect(-2, k * 90 - 2, 1282, k * 90 + 92, fill=lerp_color(P.SKY_TOP, P.SKY_BOTTOM, k / 7), outline=None)
    cx, cy, z = CAM_B
    # Dad's stomps shake the camera
    q = 0.0
    for st in (b["dad_in"] + 0.15, b["dad_in"] + 0.5):
        q = max(q, 1 - progress(t, st, 0.25)) if t >= st else q
    sx, sy = shake(t, 6 * q, 40, 5)
    with cv.camera(cx + sx, cy + sy, z):
        draw_alley(cv, t, ground_y=GROUND, seed=5)
        deflate = ease_out(progress(t, b["deflate"], 0.4))
        dad_p = ease_out(progress(t, b["dad_in"], 0.6))
        looking_up = progress(t, b["dad_in"] + 0.2, 0.3)
        heads = {}
        plead = t >= b["plead"] and t < b["deflate"]
        # back row dogs (y < kids)
        items = []
        for i, d in enumerate(DOGS):
            items.append((d[1], "dog", i))
        for k in KIDS_B:
            items.append((690, "kid", k))
        items.sort(key=lambda it: it[0])
        for _, kind, it in items:
            if kind == "kid":
                nm, x, sc = it
                expr = None
                pose = "stand"
                if plead:
                    expr = "sad"
                    pose = "hold_both" if nm != "MUI" else "stand"
                if t >= b["deflate"]:
                    expr = "deadpan" if nm != "MUI" else "bored"
                    pose = "stand"
                if nm == "MUI":
                    expr = "bored" if t < b["deflate"] else "deadpan"
                lk = (0.3, -0.6) if plead else (0, 0)
                lk = (lerp(lk[0], 0.9, looking_up), lerp(lk[1], -1.0, looking_up)) if t < b["deflate"] else (0.6, 0.3)
                if nm == "MUI":
                    lk = (0, -0.9) if t > _dog_in(b, 6) + 0.5 and t < b["dad_in"] else lk
                a = draw_character(cv, nm, x, 690 + deflate * 4, sc, pose=pose, expression=expr,
                                   mouth_open=ctx.mouth(nm, t), t=t + x * 0.01, look=lk,
                                   blink=0 if plead else blink(t, len(nm)))
                heads[nm] = a
            else:
                i = it
                fx, fy, s, col, flip, side, pose = DOGS[i]
                p = progress(t, _dog_in(b, i), 0.55)
                if p <= 0:
                    continue
                if t > b["deflate"] + 0.3:
                    pose = "stand"
                if p < 1:
                    x = lerp(fx + side * 900, fx, ease_out(p))
                    scruffy_dog(cv, x, fy, s, col, flip, "run", t, i)
                else:
                    scruffy_dog(cv, fx, fy, s, col, flip, pose, t if t < b["deflate"] else 0.0, i)
        # the puppy that lands on Mui's head
        pp = progress(t, _dog_in(b, 6), 0.55)
        if pp > 0 and "MUI" in heads:
            hx, hy = heads["MUI"]["top"]
            wx, wy = (hx - 640) / z + cx + sx, (hy - 360) / z + cy + sy
            yy = lerp(wy - 420, wy + 14, pp ** 2)
            squash = 1 - 0.15 * math.sin(math.pi * progress(t, _dog_in(b, 6) + 0.55, 0.25))
            scruffy_dog(cv, wx - 6, yy, 0.42 * squash, (240, 236, 226), False, "sit", t if pp >= 1 else 0, 9)
        # Dad, giant, from the right
        if dad_p > 0:
            dx = lerp(1700, 1070, dad_p)
            walking = dad_p < 1
            draw_character(cv, "DAD", dx, 700, 1.3, pose="walk" if walking else "hands_hip", t=t,
                           expression="neutral", mouth_open=ctx.mouth("DAD", t), look=(-0.7, 0.6),
                           blink=blink(t, 11) if t < b["no"] else 0)
    # pleading sparkles on the speaking kids (screen space)
    if plead:
        for nm in ("HAI", "TUN", "TI"):
            a = heads.get(nm)
            if not a:
                continue
            hx, hy = a["head"]
            R = a["head_r"] * z
            es = 1.45 if nm == "TUN" else 1.0
            for sd in (-1, 1):
                ex, ey = hx + sd * R * 0.38, hy + R * 0.02
                tw = 0.6 + 0.4 * math.sin(t * 12 + sd)
                cv.circle(ex - R * 0.05 * es, ey - R * 0.07 * es, R * 0.07 * es * tw + 1, fill=P.WHITE, outline=None)
                cv.circle(ex + R * 0.05 * es, ey + R * 0.05 * es, R * 0.035 * es + 0.5, fill=P.WHITE, outline=None)
        hs = pop(t, b["plead"] + 0.1, 0.3) * (1 - progress(t, b["dad_in"], 0.2))
        if "HAI" in heads:
            mx_, my_ = heads["HAI"]["top"]
            speech_bubble(cv, mx_ - 150, my_ - 70, "Can we keep them?", tail=(120, 62), size=30, scale=hs)
    # "NO." stamp
    ns = pop(t, b["no"], 0.25)
    if ns > 0.01:
        with cv.at(400, 160, ns, rot=-8):
            cv.rect(-110, -54, 110, 54, fill=P.WHITE, outline=P.ACCENT, ow=8, radius=10)
            cv.text(0, 2, "NO.", 72, P.ACCENT, "black")


# ------------------------------------------------------------------ frame
def render_frame(t, ctx):
    b = beats(ctx)
    cv = ctx.canvas(P.CARD_BG)

    def whip(t0):
        return ease_in_out(progress(t, t0 - 0.2, 0.4))

    w1, w2 = whip(b["cut1"]), whip(b["cut2"])
    if w1 < 1:
        with cv.at(-1400 * w1, 0):
            phase_a(cv, t, b)
    if w1 > 0 and w2 < 1:
        with cv.at(1400 * (1 - w1) - 1400 * w2, 0):
            phase_b(cv, t, b, ctx)
    if w2 > 0:
        with cv.at(1400 * (1 - w2), 0):
            phase_c(cv, t, b, ctx)
    # speed lines during whips
    for w in (w1, w2):
        if 0 < w < 1:
            k = math.sin(math.pi * w)
            for i in range(9):
                y = 60 + i * 75
                cv.line([(1280 - (i * 137) % 900, y), (1280 - (i * 137) % 900 - 420 * k, y)], INK, 3)
    return cv.finish()
