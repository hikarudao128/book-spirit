"""Extra props / helpers used by scenes 8-11 only (grown-up kids, motorbikes, towers, train ...).

Nothing in here is used by other scenes; it only builds on the public lib API.
"""
import math
import random

from . import palette as P
from .backgrounds import SOFT
from .characters import draw_character
from .core import INK, bezier, clamp, ellipse_pts, lerp, lerp_color


def blink(t, seed=0, period=3.7):
    """Deterministic blink with a phase seed (independent of lib's auto_blink)."""
    ph = (t + seed * 0.37) % period
    return math.sin(ph / 0.12 * math.pi) if ph < 0.12 else 0.0


# ------------------------------------------------------------------ grown-up kids
# The four friends forty years on. Each keeps a signature feature from the kid design.
GROWN = {
    "MUI": ("OLD_MUI", dict(shirt=(200, 206, 214), pants=(60, 60, 70), tie=True)),
    "HAI": ("DAD", dict(hair="spiky", glasses=False, bandaid=True, torso_w=84, leg=200, torso_h=150,
                        shirt=(150, 190, 140), pants=(120, 96, 70), tie=True, head_r=50, hair_color=(70, 64, 66))),
    "TUN": ("MOM", dict(hair="bob", eye_scale=1.3, hair_color=(64, 40, 30), shirt=(240, 200, 90),
                        pants=(70, 66, 74), lips=True)),
    "TI": ("MOM", dict(hair="ponytail_bow", missing_teeth=True, shirt=(236, 140, 160), pants=(60, 60, 80),
                       lips=True, glasses=True)),
}


def draw_grown(cv, who, x, y, scale=1.0, **kw):
    base, over = GROWN[who]
    v = dict(over)
    v.update(kw.pop("variant", {}) or {})
    kw.setdefault("blink", blink(kw.get("t", 0.0), seed=len(who) * 7))
    return draw_character(cv, base, x, y, scale, variant=v, **kw)


def draw_briefcase(cv, x, y, s=1.0, color=(120, 80, 50)):
    """Briefcase hanging from a hand at (x, y)."""
    with cv.at(x, y, s):
        cv.rect(-12, -2, 12, 10, fill=None, ow=3, radius=4)
        cv.rect(-34, 8, 34, 54, fill=color, radius=6)
        cv.line([(-34, 22), (34, 22)], lerp_color(color, INK, 0.4), 2.4)
        cv.rect(-6, 18, 6, 27, fill=P.GOLD, ow=2)


# ------------------------------------------------------------------ city pieces
def draw_motorbike(cv, x, y, s=1.0, color=P.ACCENT, flip=False, t=0.0, rider=(90, 120, 200), helmet=None,
                   passengers=1):
    """Side-view scooter with a rider, (x, y) = ground under the middle. Faces right."""
    helmet = helmet or lerp_color(color, P.WHITE, 0.25)
    bob = math.sin(t * 30 + x * 0.01) * 1.2
    with cv.at(x, y + bob, s, flip=flip):
        for wx in (-44, 46):
            cv.circle(wx, -18, 18, fill=(60, 56, 64))
            cv.circle(wx, -18, 7, fill=(180, 180, 186), ow=2)
        cv.poly([(-66, -30), (-20, -36), (10, -30), (30, -48), (50, -50), (60, -30), (40, -18), (-50, -18)],
                fill=color)
        cv.rect(-60, -50, -6, -38, fill=(50, 46, 54), radius=5)          # seat
        cv.line([(46, -50), (40, -86)], INK, 5)                          # handlebar post
        cv.line([(32, -88), (50, -84)], INK, 5)
        cv.circle(62, -40, 6, fill=P.HIGHLIGHT, ow=2)                     # headlight
        for k in range(passengers):
            rx = -28 - k * 30
            col = rider if k == 0 else lerp_color(rider, (240, 120, 120), 0.6)
            cv.limb([(rx, -44), (rx + 26, -20)], 11, (60, 60, 80))        # leg
            cv.rect(rx - 14, -100, rx + 14, -44, fill=col, radius=10)    # body
            cv.limb([(rx + 6, -88), (36 if k == 0 else rx + 30, -86)], 9, col)
            cv.circle(rx + 2, -118, 17, fill=P.SKIN_ADULT)
            cv.poly(ellipse_pts(rx + 2, -120, 19, 19, 180, 360, 12), fill=helmet if k == 0 else P.WHITE)
            cv.rect(rx + 6, -122, rx + 20, -114, fill=(60, 70, 90), outline=None, radius=3)  # visor


def draw_tower(cv, x, w, h, gy, color, seed=0, lit=0.0):
    """Modern glass/concrete building, bottom at gy."""
    rng = random.Random(seed)
    top = gy - h
    dark = lerp_color(color, INK, 0.25)
    cv.rect(x, top, x + w, gy, fill=color, outline=SOFT, ow=2.4)
    cv.rect(x - 4, top - 10, x + w + 4, top + 4, fill=dark, outline=SOFT, ow=2.2)
    cols = max(2, int(w // 34))
    rows = int((h - 30) // 40)
    win = lerp_color((150, 200, 230), (255, 230, 140), lit)
    for r in range(rows):
        for c in range(cols):
            wx = x + 10 + c * (w - 20) / cols
            wy = top + 18 + r * 40
            cv.rect(wx + 3, wy, wx + (w - 20) / cols - 3, wy + 24,
                    fill=win if rng.random() > 0.25 else lerp_color(win, INK, 0.35), outline=None)
    if rng.random() < 0.5:
        cv.line([(x + w * 0.7, top - 10), (x + w * 0.7, top - 50)], SOFT, 3)
        cv.circle(x + w * 0.7, top - 52, 4, fill=P.ACCENT, outline=None)


SIGN_TEXT = ["PHỞ", "CƠM", "CAFE", "4G", "SALE", "SPA", "BÁNH MÌ", "KARAOKE", "SHOP", "TRÀ SỮA", "HOTEL", "ATM",
             "GYM", "NAIL", "WIFI"]
SIGN_COLS = [(230, 70, 60), (40, 120, 200), (250, 190, 40), (60, 160, 90), (200, 60, 150), (240, 120, 40),
             (40, 40, 60)]


def sign_layout(seed, x0, x1, gy, n=26):
    rng = random.Random(seed)
    out = []
    for i in range(n):
        txt = rng.choice(SIGN_TEXT)
        w = 30 + len(txt) * 16 + rng.choice([0, 10, 20])
        h = rng.choice([30, 36, 44])
        x = rng.uniform(x0, x1)
        y = gy - rng.uniform(120, 360)
        vertical = rng.random() < 0.22
        out.append(dict(x=x, y=y, w=w, h=h, txt=txt, col=SIGN_COLS[i % len(SIGN_COLS)], vertical=vertical,
                        order=rng.random()))
    return out


def draw_sign(cv, sg, s=1.0):
    if s <= 0.01:
        return
    with cv.at(sg["x"], sg["y"], s):
        if sg["vertical"]:
            h = sg["w"] * 1.1
            cv.rect(-20, -h / 2, 20, h / 2, fill=sg["col"], outline=SOFT, ow=2.2, radius=3)
            txt = sg["txt"].replace(" ", "")[:4]
            for i, ch in enumerate(txt):
                cv.text(0, -h / 2 + 14 + i * (h - 20) / max(1, len(txt)), ch, 16, P.WHITE, "black")
        else:
            cv.rect(-sg["w"] / 2, -sg["h"] / 2, sg["w"] / 2, sg["h"] / 2, fill=sg["col"], outline=SOFT, ow=2.2,
                    radius=3)
            cv.text(0, 1, sg["txt"], sg["h"] * 0.5, P.WHITE, "black")


# ------------------------------------------------------------------ train
def draw_rails(cv, x0, x1, y):
    cv.rect(x0, y, x1, y + 26, fill=(170, 150, 130), outline=None)
    for k in range(int(x0) // 40 * 40, int(x1), 40):
        cv.rect(k, y + 4, k + 18, y + 22, fill=P.WOOD_DARK, outline=None)
    cv.line([(x0, y + 6), (x1, y + 6)], (110, 110, 120), 4)
    cv.line([(x0, y + 18), (x1, y + 18)], (110, 110, 120), 4)


def draw_train_car(cv, x, y, w=300, h=150, color=(230, 90, 70), t=0.0, inside=None, engine=False,
                   sign=None):
    """One car, (x, y) = bottom-left at rail level. `inside(cv, wx, wy, ww, wh, i)` draws passengers in
    each window BEFORE the frame is drawn, so the frame masks their bodies."""
    top = y - 24 - h
    by = y - 24
    nwin = 3 if not engine else 1
    wins = []
    if engine:
        wins.append((x + w - 120, top + 26, x + w - 40, top + 86))
    else:
        ww = (w - 40) / nwin
        for i in range(nwin):
            wins.append((x + 20 + i * ww + 8, top + 24, x + 20 + (i + 1) * ww - 8, top + 92))
    # window interiors + passengers
    for i, (a, b, c, d) in enumerate(wins):
        cv.rect(a, b, c, d, fill=(255, 236, 190), outline=None)
        if inside:
            inside(cv, a, b, c - a, d - b, i)
    light = lerp_color(color, P.WHITE, 0.3)
    # frame pieces around the windows
    cv.rect(x, top, x + w, wins[0][1], fill=color, outline=None)                 # above
    cv.rect(x, wins[0][3], x + w, by, fill=color, outline=None)                  # below
    xs = [x] + [v for wn in wins for v in (wn[0], wn[2])] + [x + w]
    for k in range(0, len(xs), 2):
        cv.rect(xs[k], wins[0][1] - 1, xs[k + 1], wins[0][3] + 1, fill=color, outline=None)
    cv.rect(x, by - 30, x + w, by - 18, fill=light, outline=None)                 # stripe
    for a, b, c, d in wins:
        cv.rect(a, b, c, d, fill=None, ow=3, radius=4)
    cv.rect(x, top, x + w, by, fill=None, ow=3.4, radius=12)
    # roof
    cv.rect(x + 8, top - 14, x + w - 8, top + 2, fill=lerp_color(color, INK, 0.3), radius=6)
    if engine:
        cv.rect(x + 30, top - 60, x + 70, top - 10, fill=(70, 66, 74), radius=4)    # chimney
        cv.rect(x + 22, top - 70, x + 78, top - 56, fill=(70, 66, 74), radius=4)
        cv.circle(x + w - 6, by - 44, 12, fill=P.HIGHLIGHT, ow=3)                   # lamp
        cv.poly([(x + w, by - 4), (x + w + 34, by + 18), (x + w, by + 18)], fill=(90, 90, 100))  # cow-catcher
        if sign:
            cv.rect(x + 20, top + 30, x + w - 140, top + 76, fill=INK, radius=6)
            cv.text(x + (w - 120) / 2, top + 53, sign, 20, P.HIGHLIGHT, "black")
    # wheels
    for k in range(2 if not engine else 3):
        wx = x + 50 + k * (w - 100) / max(1, (1 if not engine else 2))
        cv.circle(wx, y - 2, 22, fill=(60, 56, 64))
        a = -t * 12
        cv.line([(wx, y - 2), (wx + 14 * math.cos(a), y - 2 + 14 * math.sin(a))], (200, 200, 205), 3)
        cv.circle(wx, y - 2, 6, fill=(200, 200, 205), ow=2)


def draw_steam_puffs(cv, x, y, t, n=5):
    for i in range(n):
        ph = (t * 0.9 + i / n) % 1
        cv.circle(x - ph * 160 + math.sin(ph * 7 + i) * 10, y - ph * 90, 12 + ph * 26,
                  fill=lerp_color(P.WHITE, (230, 230, 236), ph), outline=SOFT, ow=2)


# ------------------------------------------------------------------ small icons
def draw_bulb(cv, x, y, s=1.0, glow=1.0):
    with cv.at(x, y, s):
        if glow > 0:
            for k in range(8):
                a = math.radians(k * 45)
                cv.line([(math.cos(a) * 48, -10 + math.sin(a) * 48), (math.cos(a) * (48 + 16 * glow),
                         -10 + math.sin(a) * (48 + 16 * glow))], P.HIGHLIGHT, 5)
        cv.circle(0, -10, 32, fill=lerp_color((240, 240, 230), P.HIGHLIGHT, glow))
        cv.rect(-14, 18, 14, 40, fill=(170, 170, 180), radius=3)
        cv.line([(-14, 26), (14, 26)], INK, 2)
        cv.line([(-14, 33), (14, 33)], INK, 2)
        cv.curve((-8, 10), (0, -14), (8, 10), INK, 2.4)


def draw_star_burst(cv, x, y, r, color=P.HIGHLIGHT, n=10, rot=0.0):
    pts = []
    for k in range(n * 2):
        a = math.radians(rot + k * 180 / n)
        rr = r if k % 2 == 0 else r * 0.62
        pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr))
    cv.poly(pts, fill=color, ow=3)


def arrow_head(cv, x, y, ang, size=22, color=INK):
    a = math.radians(ang)
    pts = [(x + math.cos(a) * size, y + math.sin(a) * size),
           (x + math.cos(a + 2.5) * size * 0.8, y + math.sin(a + 2.5) * size * 0.8),
           (x + math.cos(a - 2.5) * size * 0.8, y + math.sin(a - 2.5) * size * 0.8)]
    cv.poly(pts, fill=color, ow=3)
