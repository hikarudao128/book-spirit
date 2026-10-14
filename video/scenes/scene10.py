"""Scene 10 - The verdict.

Beats (all from ctx):
  "So, is it worth the ticket?"  a big childhood ticket drops in, a WORTH IT? stamp wobbles
  "The good stuff."  the ticket flies off, a two-column board slides up: GOOD STUFF / LESS GOOD STUFF
  "It's short." / "It's funny." / "...a child's voice"  rows pop with icons (thin book, laughing face,
      slingshot). "...the sharpest weapon against adult nonsense" -> in the empty right column a big
      slingshot fires a pebble into a tower of ADULT NONSENSE paperwork, which explodes
  "S.E.A. Write Award in 2010" trophy row;  "hundreds of thousands of copies" the book-stack icon
      grows into a wobbling tower
  "Mostly, I assume, to adults who felt personally attacked."  footnote + an adult reading the book
      gets hit in the chest by an arrow (literally personally attacked)
  "Now, to be fair."  LESS GOOD header pops;  "big plot" flat-line plot icon;  "string of episodes"
      little episode cards pop along a string;  "English version ... Southern flavor gets lost" a bowl
      of noodle soup drains to grey as it travels into an EN book
  "Who should read it? Anyone who was once eight."  board slides away; little Mui with an 8 balloon
  "Especially anyone who now has an eight-year-old."  Dad walks in holding Ti's hand; ESPECIALLY star
"""
import math

from lib import palette as P
from lib.backgrounds import draw_book_cover
from lib.characters import draw_character
from lib.core import INK, clamp, ease_in, ease_in_out, ease_out, ease_out_back, lerp, lerp_color, pop, progress
from lib.extra_s8_11 import arrow_head, blink, draw_star_burst
from lib.text import label, text_width

GOOD = (90, 160, 90)
BAD = P.ACCENT
COLX = (70, 660)
ROWY = (205, 290, 375, 460, 545)


def beats(ctx):
    L = [ctx.line(i) for i in range(10)]
    w = ctx.find_word
    b = dict(L=L)
    b["ticket"] = w(L[0].id, "ticket")
    b["board"] = L[1].start - 0.1
    b["short"], b["funny"] = w(L[1].id, "short"), w(L[1].id, "funny")
    b["voice"] = w(L[2].id, "child")
    b["sharp"], b["against"] = w(L[2].id, "sharpest"), w(L[2].id, "against")
    b["nonsense"] = w(L[2].id, "nonsense")
    b["award"], b["hundreds"] = w(L[3].id, "Award"), w(L[3].id, "hundreds")
    b["vietnam"] = w(L[3].id, "Vietnam")
    b["mostly"], b["attacked"] = L[4].start, w(L[4].id, "attacked")
    b["fair"], b["plot"] = w(L[5].id, "fair"), w(L[5].id, "plot")
    b["string"], b["adventure"] = w(L[6].id, "string"), w(L[6].id, "adventure")
    b["english"], b["flavor"], b["lost"] = w(L[7].id, "English"), w(L[7].id, "flavor"), w(L[7].id, "lost")
    b["who"], b["eight"] = L[8].start - 0.2, w(L[8].id, "Anyone")
    b["especially"] = L[9].start
    return b


def audio_cues(ctx):
    b = beats(ctx)
    c = [{"sfx": "music_bed", "start": 0.0, "dur": ctx.duration, "gain": 0.11, "fade_out": 1.0},
         {"sfx": "thud", "start": 0.35, "gain": 0.3},
         {"sfx": "slap", "start": b["ticket"], "gain": 0.3},
         {"sfx": "whoosh", "start": b["board"], "gain": 0.25}]
    for k in ("short", "funny", "voice", "award", "hundreds", "plot", "string", "english"):
        c.append({"sfx": "pop", "start": b[k], "gain": 0.25})
    c += [{"sfx": "boing", "start": b["against"], "gain": 0.3},
          {"sfx": "thud", "start": b["nonsense"], "gain": 0.45},
          {"sfx": "ding", "start": b["award"] + 0.15, "gain": 0.15},
          {"sfx": "thud", "start": b["attacked"] + 0.1, "gain": 0.4},
          {"sfx": "whoosh", "start": b["attacked"] - 0.15, "gain": 0.2},
          {"sfx": "record_scratch", "start": b["fair"] - 0.35, "gain": 0.12},
          {"sfx": "whoosh", "start": b["who"], "gain": 0.3},
          {"sfx": "pop", "start": b["eight"], "gain": 0.25},
          {"sfx": "ding", "start": b["especially"] + 0.9, "gain": 0.2}]
    for i in range(5):
        c.append({"sfx": "tick", "start": b["string"] + 0.15 + i * 0.13, "gain": 0.25})
    return c


# ------------------------------------------------------------------ icons
def icon(cv, kind, x, y, s, t, b):
    if s <= 0.01:
        return
    with cv.at(x, y, s):
        cv.circle(0, 0, 34, fill=P.WHITE, ow=3)
        if kind == "short":
            cv.rect(-20, -8, 20, 8, fill=(250, 214, 110), ow=3, radius=2)
            cv.line([(-16, 0), (16, 0)], INK, 1.6)
            cv.text(0, -20, "↔", 14, INK, "black")
        elif kind == "funny":
            cv.circle(0, 0, 22, fill=P.HIGHLIGHT, ow=3)
            cv.curve((-12, -6), (-8, -11), (-4, -6), INK, 2.6)
            cv.curve((4, -6), (8, -11), (12, -6), INK, 2.6)
            cv.poly([(-12, 3), (12, 3), (0, 16)], fill=P.MOUTH, ow=2.4)
            cv.circle(-22, -2, 3, fill=(120, 190, 240), outline=None)
            cv.circle(22, -2, 3, fill=(120, 190, 240), outline=None)
        elif kind == "voice":
            _slingshot(cv, 0, 6, 0.42, 0)
        elif kind == "award":
            cv.poly([(-16, -20), (16, -20), (12, 0), (-12, 0)], fill=P.GOLD, ow=2.6)
            cv.curve((-16, -16), (-28, -10), (-12, -2), INK, 2.4)
            cv.curve((16, -16), (28, -10), (12, -2), INK, 2.4)
            cv.rect(-4, 0, 4, 10, fill=P.GOLD, ow=2.2)
            cv.rect(-12, 10, 12, 18, fill=P.WOOD_DARK, ow=2.2)
            if (t * 2) % 1 < 0.5:
                draw_star_burst(cv, 18, -24, 6, P.WHITE, 4)
        elif kind == "copies":
            n = 3 + int(round(9 * _tower(t, b)))
            sway = math.sin(t * 7) * 2.5 * _tower(t, b)
            for k in range(n):
                col = [(230, 90, 70), (90, 160, 210), (250, 200, 80), (110, 180, 110)][k % 4]
                xx = sway * k * 0.4 + (k % 2) * 3 - 1.5
                cv.rect(xx - 20, 16 - (k + 1) * 9, xx + 20, 16 - k * 9, fill=col, ow=2.2, radius=2)
        elif kind == "plot":
            cv.line([(-22, -18), (-22, 18), (22, 18)], INK, 3)
            cv.line([(-18, 4), (20, 4)], P.ACCENT, 3.4)
            cv.circle(20, 4, 3.5, fill=P.ACCENT, outline=None)
        elif kind == "episodes":
            cv.curve((-26, -12), (0, 0), (26, -12), INK, 2)
            for k, xx in enumerate((-18, -6, 6, 18)):
                yy = -10 + 5 * (1 - abs(xx) / 18)
                cv.rect(xx - 5, yy, xx + 5, yy + 14, fill=[(250, 200, 80), (120, 190, 240), (240, 140, 160),
                                                         (140, 200, 120)][k], ow=1.8)
        elif kind == "flavor":
            g = _drain(t, b)
            cv.poly([(-22, -2), (22, -2), (14, 16), (-14, 16)], fill=P.WHITE, ow=2.6)
            cv.ellipse(0, -2, 22, 6, fill=lerp_color((220, 130, 60), (190, 186, 182), g), ow=2.4)
            for k, (xx, col) in enumerate(((-10, (80, 170, 80)), (2, (230, 60, 50)), (12, (80, 170, 80)))):
                cv.circle(xx, -3, 3.5, fill=lerp_color(col, (170, 168, 166), g), outline=None)


def _tower(t, b):
    up = ease_out_back(progress(t, b["hundreds"], 0.9), 1.4)
    down = ease_in_out(progress(t, b["vietnam"] + 0.3, 0.5))
    return up * (1 - down)


def _drain(t, b):
    return ease_in_out(progress(t, b["flavor"], b["lost"] + 0.4 - b["flavor"]))


def _slingshot(cv, x, y, s, pull):
    with cv.at(x, y, s):
        cv.limb([(0, 60), (0, 10), (-30, -40)], 12, P.WOOD)
        cv.limb([(0, 10), (30, -40)], 12, P.WOOD)
        px = -60 * pull
        cv.line([(-30, -40), (px - 6, -26 + 10 * pull)], (150, 60, 50), 4)
        cv.line([(30, -40), (px - 6, -26 + 10 * pull)], (150, 60, 50), 4)
        cv.rect(px - 14, -34 + 10 * pull, px + 2, -18 + 10 * pull, fill=(150, 60, 50), radius=3, ow=2)


# ------------------------------------------------------------------ board
def row(cv, col, i, kind, text, start, t, b, sub=None, color=INK):
    s = pop(t, start, 0.35)
    if s <= 0.01:
        return
    x, y = COLX[col], ROWY[i]
    icon(cv, kind, x + 40, y, s, t, b)
    with cv.at(x + 90 + (1 - ease_out(progress(t, start, 0.3))) * 40, y, 1.0):
        lines = text.split("\n")
        for k, ln in enumerate(lines):
            cv.text(0, (k - (len(lines) - 1) / 2) * 30 - (8 if sub else 0), ln, 26 if len(lines) == 1 else 23,
                    color, "black", anchor="lm")
        if sub:
            cv.text(0, 22 + (len(lines) - 1) * 14, sub, 17, (120, 110, 120), "bolditalic", anchor="lm")


def draw_board(cv, t, b):
    cv.rect(46, 50, 1246, 700, fill=INK, outline=None, radius=14)
    cv.rect(36, 40, 1236, 690, fill=(200, 200, 205), radius=14)
    cv.rect(50, 54, 1222, 676, fill=P.WHITE, outline=None, radius=6)
    cv.line([(640, 80), (640, 650)], (220, 220, 224), 3)
    hs = pop(t, b["board"] + 0.15, 0.35)
    if hs > 0.01:
        with cv.at(345, 112, hs):
            cv.text(0, 0, "GOOD STUFF", 40, GOOD, "black")
        cv.line([(90, 148), (600, 148)], INK, 3)
    hs2 = pop(t, b["fair"], 0.35)
    if hs2 > 0.01:
        with cv.at(935, 112, hs2):
            cv.text(0, 0, "LESS GOOD STUFF", 40, BAD, "black")
        cv.line([(680, 148), (1190, 148)], INK, 3)
    row(cv, 0, 0, "short", "SHORT", b["short"], t, b)
    row(cv, 0, 1, "funny", "FUNNY", b["funny"], t, b)
    row(cv, 0, 2, "voice", "CHILD'S VOICE", b["voice"], t, b, sub="sharpest weapon vs adult nonsense"
        if t > b["sharp"] else None)
    row(cv, 0, 3, "award", "S.E.A. WRITE AWARD 2010", b["award"], t, b)
    row(cv, 0, 4, "copies", "100,000s OF COPIES SOLD*", b["hundreds"], t, b)
    fs = pop(t, b["attacked"] + 0.4, 0.3)
    if fs > 0.01:
        with cv.at(345, 628, fs):
            cv.text(0, 0, "*mostly to adults who felt personally attacked", 18, (120, 110, 120), "bolditalic")
    row(cv, 1, 0, "plot", "NO BIG PLOT", b["plot"], t, b)
    row(cv, 1, 1, "episodes", "A STRING OF EPISODES", b["string"], t, b,
        sub="not one big adventure" if t > b["adventure"] - 0.2 else None)
    row(cv, 1, 2, "flavor", "ENGLISH EDITION LOSES\nSOME SOUTHERN FLAVOR", b["english"], t, b, color=INK)


# ------------------------------------------------------------------ right-column gags
NONSENSE = ("TAXES", "RULES", "BEDTIME 8PM", "MEETINGS", "BE SENSIBLE")


def gag_slingshot(cv, t, b):
    t0, t_end = b["sharp"] - 0.35, b["award"] - 0.3
    s = pop(t, t0, 0.35) * (1 - ease_in(progress(t, t_end, 0.3)))
    if s <= 0.01:
        return
    with cv.at(930, 420, s):
        # tower of adult nonsense
        hit = progress(t, b["nonsense"], 1.2)
        for k, txt in enumerate(NONSENSE):
            if hit <= 0:
                x, y, r = 150, 150 - k * 46, (k % 2) * 3 - 1.5
            else:
                ang = (k - 2) * 0.55 - 0.3
                d = ease_out(hit) * (260 + k * 40)
                x = 150 + math.sin(ang) * d
                y = 150 - k * 46 - math.cos(ang) * d * 0.7 + 400 * hit * hit
                r = hit * (k - 2) * 120
            with cv.at(x, y, 1, rot=r):
                w = text_width(txt, 18, "black") + 26
                cv.rect(-w / 2, -18, w / 2, 18, fill=P.PAPER, ow=2.6, radius=3)
                cv.text(0, 1, txt, 18, INK, "black")
        if hit <= 0:
            cv.text(150, -105, "ADULT NONSENSE", 18, P.ACCENT, "black")
        if 0 < hit < 0.3:
            draw_star_burst(cv, 150, 60, 60 * (1 - hit), P.HIGHLIGHT, 10)
        # slingshot pulls back, then fires
        pull = ease_out(progress(t, b["sharp"], b["against"] - b["sharp"])) * (1 - progress(t, b["against"], 0.06))
        _slingshot(cv, -180, 60, 1.6, pull)
        label(cv, -180, 210, "CHILD'S VOICE", 20, bg=P.HIGHLIGHT, rot=-3)
        fp = progress(t, b["against"], b["nonsense"] - b["against"])
        if 0 < fp < 1:
            cv.circle(lerp(-200, 150, fp), lerp(10, 70, fp) - 80 * math.sin(math.pi * fp), 10, fill=(120, 116, 120))


def gag_attacked(cv, t, b):
    t0, t_end = b["mostly"] - 0.1, b["fair"] - 0.45
    s = ease_out(progress(t, t0, 0.4)) * (1 - ease_in(progress(t, t_end, 0.35)))
    if s <= 0.01:
        return
    hit = t >= b["attacked"] + 0.1
    y = lerp(900, 0, s)
    with cv.at(0, y):
        a = draw_character(cv, "DAD", 930, 880, 1.0, pose="hold_both", expression="shocked" if hit else "neutral",
                           t=t, look=(0, 0.8) if not hit else (0, 0), blink=blink(t, 5), lean=-5 if hit else 0)
        hx = (a["hand_r"][0] + a["hand_l"][0]) / 2
        hy = (a["hand_r"][1] + a["hand_l"][1]) / 2
        with cv.at(hx, hy + 6, 1, rot=-4):             # the book he is reading
            cv.rect(-46, -62, 46, 4, fill=(250, 222, 120), radius=4, ow=3)
            cv.rect(-46, -62, -38, 4, fill=(230, 180, 70), radius=2, ow=2.4)
            cv.text(4, -36, "VÉ", 22, P.ACCENT, "black")
        for sd in (-1, 1):
            cv.circle(a["hand_r" if sd > 0 else "hand_l"][0], a["hand_r" if sd > 0 else "hand_l"][1], 12,
                      fill=P.SKIN_ADULT)
        cx_, cy_ = a["chest"][0] + 18, a["chest"][1] - 34
        ap = progress(t, b["attacked"] - 0.15, 0.25)
        if ap > 0:
            sx = lerp(1300, cx_ - 30, ease_in(ap))
            sy = lerp(cy_ - 160, cy_, ease_in(ap))
            with cv.at(sx, sy, 1, rot=-30 if ap < 1 else -30 + math.sin(t * 40) * 4 * max(0, 1 - (t - b["attacked"]))):
                cv.limb([(0, 0), (110, 0)], 5, P.WOOD)
                cv.poly([(0, 0), (16, -8), (16, 8)], fill=(150, 150, 160), ow=2)
                cv.poly([(100, 0), (124, -12), (116, 0), (124, 12)], fill=P.ACCENT, ow=2)
        if hit:
            label(cv, 1100, 430 + 2 * math.sin(t * 30), "PERSONALLY ATTACKED", 18, fill=P.WHITE, bg=P.ACCENT,
                  scale=pop(t, b["attacked"] + 0.15, 0.25), rot=6)


# only the episodes the script names (renaming, being adults / playing house, the trial, stray dogs)
EPISODES = ("NEW NAMES", "GROWN-UPS", "COURT", "STRAY DOGS")


def gag_episodes(cv, t, b):
    """Episode cards pop along a string; the one big adventure mountain gets crossed out."""
    out = ease_in(progress(t, b["english"] - 0.25, 0.25))
    if t < b["string"] or out >= 1:
        return
    with cv.at(0, out * 500):
        n = len(EPISODES)
        x0, x1, y0 = 690, 1190, 430
        pts = [(lerp(x0, x1, k / 20), y0 + 26 * math.sin(math.pi * k / 20)) for k in range(21)]
        g = ease_out(progress(t, b["string"], 0.4))
        cv.line(pts[: max(2, int(21 * g))], INK, 2.4)
        for i, txt in enumerate(EPISODES):
            s = pop(t, b["string"] + 0.15 + i * 0.13, 0.3)
            if s <= 0.01:
                continue
            u = (i + 0.5) / n
            x = lerp(x0, x1, u)
            y = y0 + 26 * math.sin(math.pi * u)
            with cv.at(x, y, s, rot=math.sin(t * 2 + i) * 4):
                cv.rect(-44, 4, 44, 64, fill=[(250, 200, 80), (120, 190, 240), (240, 140, 160), (140, 200, 120),
                                              (200, 170, 240)][i], radius=4, ow=2.6)
                cv.text(0, 20, f"EP.{i + 1}", 13, INK, "black")
                cv.text(0, 42, txt, 9.5, INK, "black")
        ms = pop(t, b["adventure"] - 0.3, 0.3)
        if ms > 0.01:
            with cv.at(940, 600, ms):
                cv.poly([(-120, 40), (-30, -50), (10, -10), (50, -60), (130, 40)], fill=(150, 170, 190), ow=3)
                cv.poly([(-30, -50), (-46, -34), (-14, -34)], fill=P.WHITE, ow=2)
                cv.text(0, 22, "ONE BIG ADVENTURE", 15, INK, "black")
                xp = ease_out(progress(t, b["adventure"] + 0.2, 0.25))
                if xp > 0:
                    cv.line([(-120, -60), (lerp(-120, 130, xp), lerp(-60, 50, xp))], P.ACCENT, 8)
                    cv.line([(130, -60), (lerp(130, -120, xp), lerp(-60, 50, xp))], P.ACCENT, 8)


def gag_bowl(cv, t, b):
    """Noodle soup travelling into the English edition and draining to grey."""
    s = pop(t, b["english"] + 0.3, 0.35) * (1 - ease_in(progress(t, b["who"] - 0.3, 0.25)))
    if s <= 0.01:
        return
    g = _drain(t, b)
    with cv.at(935, 560, s):
        mv = ease_in_out(progress(t, b["flavor"] - 0.2, b["lost"] - b["flavor"] + 0.6))
        bx = lerp(-170, 60, mv)
        # EN edition
        cv.rect(110, -78, 230, 78, fill=INK, outline=None, radius=6)
        cv.rect(100, -86, 220, 70, fill=lerp_color((240, 240, 236), (200, 200, 200), g), radius=6, ow=3)
        cv.text(160, -40, "EN", 34, ACC_EN, "black")
        cv.text(160, 2, "Ticket to", 15, INK, "bold")
        cv.text(160, 22, "Childhood", 15, INK, "bold")
        arrow_head(cv, 80, 0, 0, 18, (170, 170, 170))
        cv.line([(-60, 0), (66, 0)], (170, 170, 170), 5)
        # bowl
        with cv.at(bx, 0, 1 - 0.25 * mv):
            cv.poly([(-60, -6), (60, -6), (40, 46), (-40, 46)], fill=P.WHITE, ow=3)
            cv.ellipse(0, -6, 60, 15, fill=lerp_color((220, 130, 60), (196, 192, 188), g), ow=3)
            for k, (xx, yy, col) in enumerate(((-30, -8, (80, 170, 80)), (-8, -12, (230, 60, 50)),
                                              (14, -6, (80, 170, 80)), (34, -10, (250, 200, 60)),
                                              (-18, -2, (240, 160, 150)))):
                cv.circle(xx, yy, 7, fill=lerp_color(col, (176, 174, 172), g), ow=2)
            if g < 0.6:
                for i in range(3):
                    ph = (t * 0.8 + i / 3) % 1
                    cv.circle(-20 + i * 20 + math.sin(ph * 6) * 4, -30 - ph * 40, (5 + ph * 6) * (1 - g),
                              fill=P.WHITE, outline=None)
            cv.line([(30, -10), (70, -60)], P.WOOD_DARK, 4)
            cv.line([(38, -8), (80, -54)], P.WOOD_DARK, 4)
        if g > 0.5:
            label(cv, -110, 92, "where did the flavor go?", 16, bg=P.WHITE, scale=pop(t, b["lost"], 0.3))


ACC_EN = (40, 80, 160)


# ------------------------------------------------------------------ ticket / ending
def draw_ticket(cv, t, b):
    s = ease_out_back(progress(t, 0.2, 0.5), 1.6)
    out = ease_in(progress(t, b["board"] - 0.2, 0.4))
    if s <= 0.01 or out >= 1:
        return
    with cv.at(640 + out * -900, 330 - out * 300, s, rot=-6 + math.sin(t * 2) * 2 + out * -40):
        cv.rect(-300, -130, 310, 142, fill=INK, outline=None, radius=14)
        cv.rect(-310, -140, 300, 130, fill=(255, 248, 230), radius=14, ow=4)
        cv.line([(150, -130), (150, 120)], (200, 120, 100), 3)
        for yy in range(-120, 130, 22):
            cv.circle(150, yy, 4, fill=P.CARD_BG, outline=None)
        cv.text(-80, -60, "VÉ", 80, P.ACCENT, "black")
        cv.text(-80, 30, "ĐI TUỔI THƠ", 40, INK, "black")
        cv.text(-80, 80, "1 × CHILDHOOD", 22, (120, 110, 120), "extrabold")
        cv.text(225, 0, "★", 60, P.ACCENT, "bold")
    ss = pop(t, b["ticket"], 0.25) * (1 - out)
    if ss > 0.01:
        with cv.at(900, 470, ss, rot=-12):
            cv.rect(-150, -46, 150, 46, fill=P.WHITE, outline=P.ACCENT2, ow=7, radius=10)
            cv.text(0, 2, "WORTH IT?", 46, P.ACCENT2, "black")


def draw_who(cv, t, b):
    _bg_rays(cv, t)
    label(cv, 640, 70, "WHO SHOULD READ IT?", 36, bg=P.WHITE, scale=pop(t, b["who"] + 0.25, 0.35))
    # anyone who was once eight
    ms = pop(t, b["eight"] - 0.05, 0.4)
    if ms > 0.01:
        with cv.at(330, 650, ms):
            a = draw_character(cv, "MUI", 0, 0, 1.55, pose="hold", expression="bored", t=t, blink=blink(t, 1))
        hx, hy = a["hand_r"]
        bx, by = hx + 150 + math.sin(t * 1.5) * 8, hy - 300
        cv.curve((hx, hy), (hx + 120, hy - 120), (bx, by + 52), (90, 80, 80), 2)
        cv.ellipse(bx, by, 44, 52, fill=P.ACCENT)
        cv.poly([(bx - 6, by + 54), (bx + 6, by + 54), (bx, by + 46)], fill=P.ACCENT, ow=2)
        cv.text(bx, by, "8", 50, P.WHITE, "black")
        label(cv, 330, 690, "ANYONE WHO WAS ONCE 8", 22, bg=P.HIGHLIGHT, scale=ms)
    # ...especially anyone who has one now
    st = b["especially"] - 0.3
    wp = progress(t, st, 1.0)
    if wp > 0:
        dx = lerp(700, 0, ease_out(wp))
        walking = wp < 1
        ti = draw_character(cv, "TI", 840 + dx, 660, 1.2, pose="walk" if walking else "point_up", t=t,
                            expression="happy", look=(0.6, -0.7), blink=blink(t, 3))
        dad = draw_character(cv, "DAD", 990 + dx, 680, 1.0, pose="walk" if walking else "stand", t=t + 0.2,
                             expression="happy", look=(-0.6, 0.6), blink=blink(t, 7))
        h1, h2 = ti["hand_r"], dad["hand_l"]
        mx, my = (h1[0] + h2[0]) / 2, (h1[1] + h2[1]) / 2
        cv.limb([h1, (mx, my)], 13, P.SKIN)
        cv.limb([h2, (mx, my)], 20, P.SKIN_ADULT)
        cv.circle(mx, my, 12, fill=P.SKIN_ADULT)
        es = pop(t, b["especially"] + 0.9, 0.35)
        if es > 0.01:
            with cv.at(1120, 200, es, rot=10):
                draw_star_burst(cv, 0, 0, 100, P.HIGHLIGHT, 12, rot=t * 20)
                cv.text(0, -8, "ESPECIALLY", 17, INK, "black")
                cv.text(0, 20, "YOU", 30, P.ACCENT, "black")
            label(cv, 930, 700, "...OR HAS AN 8-YEAR-OLD", 22, bg=P.WHITE, scale=es)


def _bg_rays(cv, t):
    cv.rect(-10, -10, 1290, 730, fill=(255, 238, 200), outline=None)
    for k in range(16):
        a0 = math.radians(k * 22.5 + t * 5)
        a1 = a0 + math.radians(11.25)
        cv.poly([(640, 420), (640 + 1600 * math.cos(a0), 420 + 1600 * math.sin(a0)),
                 (640 + 1600 * math.cos(a1), 420 + 1600 * math.sin(a1))], fill=(255, 228, 176), outline=None)


def _paper(cv):
    cv.rect(-10, -10, 1290, 730, fill=P.CARD_BG, outline=None)
    for gx in range(0, 1281, 40):
        cv.line([(gx, 0), (gx, 720)], (244, 234, 210), 1.5)
    for gy in range(0, 721, 40):
        cv.line([(0, gy), (1280, gy)], (244, 234, 210), 1.5)


# ------------------------------------------------------------------ frame
def render_frame(t, ctx):
    b = beats(ctx)
    cv = ctx.canvas(P.CARD_BG)
    _paper(cv)
    up = ease_out_back(progress(t, b["board"], 0.5), 1.2)
    away = ease_in_out(progress(t, b["who"], 0.45))
    if up > 0 and away < 1:
        with cv.at(0, (1 - up) * 760 - away * 800):
            draw_board(cv, t, b)
            gag_slingshot(cv, t, b)
            gag_attacked(cv, t, b)
            gag_episodes(cv, t, b)
            gag_bowl(cv, t, b)
    draw_ticket(cv, t, b)
    if away > 0:
        with cv.at(0, (1 - away) * 760):
            draw_who(cv, t, b)
    return cv.finish()
