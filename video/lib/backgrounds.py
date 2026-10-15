"""Backgrounds and set pieces. All functions draw onto a Canvas in the CURRENT transform
(world coords), except draw_sky which is screen-space.

Main sets:
  draw_sky(cv, t, ...)                       screen-space gradient + sun + drifting clouds
  draw_alley(cv, t, ...) -> anchors           Vietnamese alley: tube houses, wires, kites, ground
  draw_classroom(cv, t, board_lines=...)      wall, blackboard (chalk text), windows, fan, clock
  draw_desks(cv, y, n, ...)                   foreground row of school desks
  draw_dining_room(cv, t) / draw_dinner_table(cv, x, y, w)
  draw_curtain(cv, open_amount, t)            red stage curtain (0 closed .. 1 open)
  draw_courtroom(cv, t, ...)                  plastic-stool courtroom with cardboard sign
  draw_plastic_stool(cv, x, y, color, scale)  the iconic red/blue VN plastic stool
  draw_gavel(cv, x, y, rot, scale)
  draw_kitchen(cv, t, night=True)
  draw_book_cover(cv, cx, cy, w, h, rot, scale)
  draw_kite(cv, x, y, size, color, t, tail=5)
  draw_sun(cv, x, y, r, t)
  draw_plant(cv, x, y, scale, kind)
"""
import functools
import math
import random

import numpy as np
from PIL import Image

from . import palette as P
from .core import INK, OW, H, W, bezier, ellipse_pts, lerp, lerp_color

SOFT = (70, 60, 66)   # thinner/softer outline colour for background depth


# ------------------------------------------------------------------ sky
@functools.lru_cache(maxsize=16)
def _gradient(w, h, top, bottom):
    a = np.linspace(0, 1, h)[:, None, None]
    arr = (np.array(top)[None, None, :] * (1 - a) + np.array(bottom)[None, None, :] * a)
    arr = np.repeat(arr, w, axis=1).astype(np.uint8)
    return Image.fromarray(arr, "RGB")


def draw_gradient(cv, top, bottom, y0=0, y1=H):
    """Screen-space vertical gradient between logical rows y0..y1."""
    ss = cv.ss
    g = _gradient(cv.w * ss, int((y1 - y0) * ss), tuple(top), tuple(bottom))
    cv.img.paste(g, (0, int(y0 * ss)))


def draw_sun(cv, x, y, r=60, t=0.0, rays=True):
    if rays:
        n = 12
        rot = t * 8
        for i in range(n):
            a = math.radians(rot + i * 360 / n)
            a1, a2 = a - 0.09, a + 0.09
            r1, r2 = r * 1.25, r * (1.75 if i % 2 else 1.55)
            cv.poly([(x + r1 * math.cos(a1), y + r1 * math.sin(a1)), (x + r2 * math.cos(a), y + r2 * math.sin(a)),
                     (x + r1 * math.cos(a2), y + r1 * math.sin(a2))], fill=P.SUN_RAY, outline=None)
    cv.circle(x, y, r * 1.1, fill=(255, 236, 160), outline=None)
    cv.circle(x, y, r, fill=P.SUN, ow=3)


def draw_cloud(cv, x, y, s=1.0, col=P.CLOUD):
    blobs = [(-50, 6, 30), (-18, -14, 38), (24, -6, 32), (52, 10, 24), (0, 12, 30)]
    for bx, by, br in blobs:
        cv.circle(x + bx * s, y + by * s, br * s + 2.5, fill=SOFT, outline=None)
    for bx, by, br in blobs:
        cv.circle(x + bx * s, y + by * s, br * s, fill=col, outline=None)
    cv.rect(x - 52 * s, y + 8 * s, x + 54 * s, y + 34 * s, fill=col, outline=None, radius=10 * s)


def draw_sky(cv, t=0.0, top=P.SKY_TOP, bottom=P.SKY_BOTTOM, sun=(1060, 120), clouds=True, horizon=720):
    """Screen-space sky. sun=None to hide. Clouds drift slowly with t."""
    draw_gradient(cv, top, bottom, 0, horizon)
    if sun:
        draw_sun(cv, sun[0], sun[1], 58, t)
    if clouds:
        for i, (cx, cy, s, sp) in enumerate([(160, 110, 1.0, 6), (560, 70, 0.8, 4), (880, 160, 0.7, 5),
                                             (1300, 90, 0.9, 6)]):
            x = (cx + t * sp) % 1600 - 160
            draw_cloud(cv, x, cy, s)


# ------------------------------------------------------------------ kites
def draw_kite(cv, x, y, size=40, color=P.ACCENT, t=0.0, tail=5, seed=0, string_to=None):
    """Diamond kite centred at (x,y) with a wavy bow tail. string_to=(x,y) draws the line."""
    sway = math.sin(t * 1.6 + seed) * 8
    rot = math.sin(t * 1.3 + seed * 2) * 10
    if string_to:
        cv.curve((x, y + size * 0.9), ((x + string_to[0]) / 2 + 30, (y + string_to[1]) / 2 + 40), string_to,
                 (90, 80, 80), 1.6)
    with cv.at(x + sway, y, 1, rot=rot):
        pts = [(0, -size), (size * 0.72, -size * 0.1), (0, size * 0.95), (-size * 0.72, -size * 0.1)]
        cv.poly(pts, fill=color, ow=3)
        light = lerp_color(color, (255, 255, 255), 0.45)
        cv.poly([(0, -size), (size * 0.72, -size * 0.1), (0, -size * 0.1)], fill=light, outline=None)
        cv.poly([(0, -size * 0.1), (-size * 0.72, -size * 0.1), (0, size * 0.95)], fill=light, outline=None)
        cv.poly(pts, fill=None, ow=3)
        cv.line([(0, -size), (0, size * 0.95)], INK, 2)
        cv.line([(-size * 0.72, -size * 0.1), (size * 0.72, -size * 0.1)], INK, 2)
        # tail
        pts = []
        for i in range(tail * 4 + 1):
            u = i / (tail * 4)
            pts.append((math.sin(u * 7 - t * 5 + seed) * 10 * u, size * 0.95 + u * size * 2.6))
        cv.line(pts, INK, 1.8)
        for k in range(1, tail + 1):
            px, py = pts[int(k * 4) - 1]
            cv.poly([(px, py), (px - 8, py - 6), (px - 8, py + 6)], fill=P.HIGHLIGHT, ow=1.8)
            cv.poly([(px, py), (px + 8, py - 6), (px + 8, py + 6)], fill=P.HIGHLIGHT, ow=1.8)


# ------------------------------------------------------------------ plants
def draw_plant(cv, x, y, scale=1.0, kind="pot"):
    """Potted plant standing on (x,y)."""
    with cv.at(x, y, scale):
        for i, (dx, h, a) in enumerate([(-14, 46, -25), (0, 60, 0), (14, 48, 25), (-6, 36, -50), (8, 38, 50)]):
            tip = (dx + math.sin(math.radians(a)) * h, -24 - math.cos(math.radians(a)) * h)
            cv.poly(bezier((dx - 6, -24), (tip[0] - 14, tip[1] + 20), tip, 6)
                    + bezier(tip, (tip[0] + 14, tip[1] + 22), (dx + 6, -24), 6),
                    fill=P.LEAF if i % 2 else P.LEAF_DARK, ow=2.4)
        cv.poly([(-22, -30), (22, -30), (16, 0), (-16, 0)], fill=P.POT, ow=3)
        cv.rect(-25, -34, 25, -26, fill=lerp_color(P.POT, (255, 255, 255), 0.15), radius=2, ow=3)


# ------------------------------------------------------------------ alley
@functools.lru_cache(maxsize=8)
def _alley_layout(seed, x0, x1):
    rng = random.Random(seed)
    houses = []
    x = x0
    i = 0
    while x < x1:
        w = rng.choice([150, 170, 190, 210])
        floors = rng.choice([2, 3, 3, 2])
        col = P.HOUSE_COLORS[(i * 3 + seed) % len(P.HOUSE_COLORS)]
        houses.append(dict(x=x, w=w, floors=floors, color=col, door=rng.choice(["roller", "shop", "door"]),
                           roof=rng.choice(["flat", "tiled", "flat"]), tank=rng.random() < 0.45,
                           balcony=[rng.random() < 0.6 for _ in range(floors)],
                           laundry=rng.random() < 0.35, shutter=rng.choice([P.SHUTTER, P.SHUTTER_ALT, P.SHUTTER]),
                           sign=rng.random() < 0.3, plant=rng.random() < 0.6))
        x += w
        i += 1
    return houses


def _house(cv, h, gy, t):
    x, w, col = h["x"], h["w"], h["color"]
    fh = 118
    gh = 150
    top = gy - gh - fh * (h["floors"] - 1)
    dark = lerp_color(col, (60, 40, 40), 0.18)
    # facade
    cv.rect(x, top, x + w, gy, fill=col, outline=SOFT, ow=2.6)
    # roof
    if h["roof"] == "tiled":
        cv.poly([(x - 8, top + 4), (x + w / 2, top - 46), (x + w + 8, top + 4)], fill=P.ROOF, outline=SOFT, ow=2.6)
        for k in range(1, 4):
            yy = top + 4 - 50 * k / 4
            dx = (w / 2 + 8) * (1 - k / 4)
            cv.line([(x + w / 2 - dx, yy), (x + w / 2 + dx, yy)], lerp_color(P.ROOF, INK, 0.3), 2)
    else:
        cv.rect(x - 4, top - 14, x + w + 4, top + 4, fill=dark, outline=SOFT, ow=2.6)
        if h["tank"]:
            tx = x + w * 0.68
            cv.rect(tx - 26, top - 62, tx + 26, top - 14, fill=(200, 205, 212), outline=SOFT, ow=2.6, radius=8)
            cv.line([(tx - 26, top - 46), (tx + 26, top - 46)], SOFT, 2)
            cv.line([(tx - 26, top - 30), (tx + 26, top - 30)], SOFT, 2)
    # upper floors
    for f in range(h["floors"] - 1):
        fy = top + f * fh
        wx0, wx1 = x + w * 0.22, x + w * 0.78
        wy0, wy1 = fy + 22, fy + 84
        cv.rect(wx0, wy0, wx1, wy1, fill=(70, 80, 100), outline=SOFT, ow=2.4)
        # open shutters
        sw = (wx1 - wx0) * 0.32
        cv.rect(wx0 - sw, wy0, wx0, wy1, fill=h["shutter"], outline=SOFT, ow=2.4)
        cv.rect(wx1, wy0, wx1 + sw, wy1, fill=h["shutter"], outline=SOFT, ow=2.4)
        for k in range(1, 4):
            yy = wy0 + (wy1 - wy0) * k / 4
            cv.line([(wx0 - sw + 3, yy), (wx0 - 3, yy)], lerp_color(h["shutter"], INK, 0.3), 1.6)
            cv.line([(wx1 + 3, yy), (wx1 + sw - 3, yy)], lerp_color(h["shutter"], INK, 0.3), 1.6)
        if h["balcony"][f]:
            by = fy + fh - 10
            cv.rect(x + 8, by - 4, x + w - 8, by + 6, fill=dark, outline=SOFT, ow=2.2)
            cv.line([(x + 12, by - 40), (x + w - 12, by - 40)], P.RAIL, 2.6)
            for k in range(9):
                xx = x + 12 + (w - 24) * k / 8
                cv.line([(xx, by - 40), (xx, by - 4)], P.RAIL, 2)
            if h["plant"]:
                draw_plant(cv, x + w - 30, by - 4, 0.55)
            if h["laundry"] and f == 0:
                ly = by - 70
                cv.line([(x + 14, ly), (x + w - 14, ly + 4)], SOFT, 1.5)
                for k, c in enumerate([(240, 120, 120), (120, 170, 240), (250, 250, 250)]):
                    lx = x + 30 + k * 34
                    sway = math.sin(t * 2 + k + x) * 2
                    cv.poly([(lx, ly + 1), (lx + 24, ly + 2), (lx + 22 + sway, ly + 30), (lx + 2 + sway, ly + 30)],
                            fill=c, outline=SOFT, ow=2)
    # ground floor
    gy0 = gy - gh
    cv.line([(x, gy0), (x + w, gy0)], SOFT, 2.6)
    dx0, dx1 = x + 16, x + w - 16
    if h["door"] == "roller":
        cv.rect(dx0, gy0 + 22, dx1, gy, fill=P.ROLLER, outline=SOFT, ow=2.4)
        for k in range(1, 12):
            yy = gy0 + 22 + (gy - gy0 - 22) * k / 12
            cv.line([(dx0 + 2, yy), (dx1 - 2, yy)], (150, 150, 156), 1.6)
    elif h["door"] == "shop":
        cv.rect(dx0, gy0 + 22, dx1, gy, fill=(96, 80, 74), outline=SOFT, ow=2.4)
        # awning
        aw = [(x - 6, gy0 + 6), (x + w + 6, gy0 + 6), (x + w + 16, gy0 + 40), (x - 16, gy0 + 40)]
        cv.poly(aw, fill=P.ACCENT, outline=SOFT, ow=2.4)
        n = 6
        for k in range(n):
            if k % 2 == 0:
                xa = lerp(x - 6, x + w + 6, k / n)
                xb = lerp(x - 6, x + w + 6, (k + 1) / n)
                xc = lerp(x - 16, x + w + 16, (k + 1) / n)
                xd = lerp(x - 16, x + w + 16, k / n)
                cv.poly([(xa, gy0 + 6), (xb, gy0 + 6), (xc, gy0 + 40), (xd, gy0 + 40)], fill=P.WHITE, outline=None)
        cv.poly(aw, fill=None, outline=SOFT, ow=2.4)
        # shelves
        for k in range(2):
            sy = gy0 + 70 + k * 36
            cv.line([(dx0 + 8, sy), (dx1 - 8, sy)], (60, 50, 46), 3)
            for j in range(4):
                cv.rect(dx0 + 14 + j * 30, sy - 18, dx0 + 34 + j * 30, sy - 2,
                        fill=[(240, 200, 80), (120, 190, 220), (230, 120, 100), (160, 210, 120)][(j + k) % 4],
                        outline=SOFT, ow=1.6)
    else:
        mx = x + w / 2
        cv.rect(mx - 34, gy0 + 34, mx + 34, gy, fill=(150, 96, 60), outline=SOFT, ow=2.4)
        cv.line([(mx, gy0 + 34), (mx, gy)], SOFT, 2)
        cv.circle(mx - 8, gy0 + 100, 3, fill=P.GOLD, outline=None)
        cv.rect(x + 12, gy0 + 46, mx - 46, gy0 + 100, fill=(70, 80, 100), outline=SOFT, ow=2.2)
        cv.rect(mx + 46, gy0 + 46, x + w - 12, gy0 + 100, fill=(70, 80, 100), outline=SOFT, ow=2.2)
    if h["sign"] and h["door"] != "shop":
        cv.rect(x + 20, gy0 - 6, x + w - 20, gy0 + 18, fill=P.WHITE, outline=SOFT, ow=2)
        cv.line([(x + 34, gy0 + 6), (x + w - 60, gy0 + 6)], P.ACCENT, 4)


def _wires(cv, x0, x1, gy, t):
    poles = list(range(int(x0) + 80, int(x1), 520))
    for px in poles:
        cv.rect(px - 7, gy - 470, px + 7, gy, fill=P.POLE, outline=SOFT, ow=2.4)
        cv.rect(px - 40, gy - 452, px + 40, gy - 444, fill=P.POLE, outline=SOFT, ow=2)
    for a, b in zip(poles[:-1], poles[1:]):
        for k, (dy, sag) in enumerate([(-450, 46), (-446, 70), (-440, 58), (-430, 90)]):
            p0 = (a + 30 - k * 20, gy + dy)
            p2 = (b - 30 + k * 18, gy + dy + 4)
            mid = ((p0[0] + p2[0]) / 2, gy + dy + sag * 2 + math.sin(t * 0.8 + k) * 2)
            cv.curve(p0, mid, p2, P.WIRE, 2.0, n=20)
        # a bird or two on the wire
    # tangled wire knot on first pole
    if poles:
        px = poles[0]
        for k in range(5):
            cv.ellipse(px + 12, gy - 400 + k * 4, 20 - k * 2, 8 + k, fill=None, outline=P.WIRE, ow=1.8)


def draw_alley(cv, t=0.0, x0=-400, x1=2000, ground_y=560, seed=3, kites=True, wires=True, step_x=None):
    """Vietnamese alley in world coords. Returns {"ground_y", "step": (x, y_top) or None}."""
    houses = _alley_layout(seed, x0, x1)
    vx0, vy0, vx1, vy1 = cv.view_bounds()
    for h in houses:
        if h["x"] + h["w"] + 40 < vx0 or h["x"] - 40 > vx1:
            continue          # off-camera
        _house(cv, h, ground_y, t)
    if wires:
        _wires(cv, x0, x1, ground_y, t)
    # ground
    cv.rect(x0 - 200, ground_y, x1 + 200, ground_y + 400, fill=P.GROUND, outline=None)
    cv.rect(x0 - 200, ground_y, x1 + 200, ground_y + 14, fill=P.CURB, outline=None)
    cv.line([(x0 - 200, ground_y), (x1 + 200, ground_y)], SOFT, 2.6)
    cv.line([(x0 - 200, ground_y + 14), (x1 + 200, ground_y + 14)], SOFT, 1.8)
    rng = random.Random(seed + 7)
    for _ in range(int((x1 - x0) / 140)):
        cx = rng.uniform(x0, x1)
        cy = ground_y + rng.uniform(50, 150)
        cv.line([(cx, cy), (cx + 18, cy + 4), (cx + 30, cy - 2)], P.GROUND_DARK, 2.2)
    for h in houses[::3]:
        draw_plant(cv, h["x"] + 10, ground_y + 14, 0.8)
    out = {"ground_y": ground_y, "step": None}
    if step_x is not None:
        sy = ground_y + 14
        cv.rect(step_x - 120, sy - 4, step_x + 120, sy + 30, fill=P.STEP, outline=SOFT, ow=2.6)
        cv.rect(step_x - 100, sy - 40, step_x + 100, sy - 4, fill=lerp_color(P.STEP, (255, 255, 255), 0.15),
                outline=SOFT, ow=2.6)
        out["step"] = (step_x, sy - 40)
        out["step_low"] = (step_x, sy - 4)
    return out


# ------------------------------------------------------------------ classroom
def draw_classroom(cv, t=0.0, board_lines=(), board_title="", fan=True):
    """Classroom wall (yellow over green), central blackboard with chalk text, windows, fan, clock."""
    cv.rect(-200, -200, 1480, 470, fill=(250, 226, 150), outline=None)
    cv.rect(-200, 470, 1480, 620, fill=P.WALL_GREEN, outline=None)
    cv.line([(-200, 470), (1480, 470)], SOFT, 3)
    cv.rect(-200, 620, 1480, 920, fill=(200, 160, 120), outline=None)
    cv.line([(-200, 620), (1480, 620)], SOFT, 3)
    # blackboard
    cv.rect(330, 90, 950, 400, fill=P.WOOD, ow=3.4, radius=6)
    cv.rect(346, 106, 934, 384, fill=P.CHALKBOARD, outline=None)
    cv.rect(340, 398, 940, 410, fill=P.WOOD_DARK, ow=2.6)
    if board_title:
        cv.text(640, 150, board_title, 40, P.CHALK, "bold")
    for i, ln in enumerate(board_lines):
        cv.text(380, 200 + i * 46, ln, 32, P.CHALK, "medium", anchor="lm")
    # windows
    for wx in (60, 1110):
        cv.rect(wx, 130, wx + 140, 360, fill=(170, 220, 240), outline=SOFT, ow=3)
        for k in range(1, 6):
            xx = wx + 140 * k / 6
            cv.line([(xx, 130), (xx, 360)], (90, 90, 96), 3)
        cv.line([(wx, 245), (wx + 140, 245)], SOFT, 3)
    # clock
    cv.circle(1020, 80, 30, fill=P.WHITE)
    a = t * 0.4
    cv.line([(1020, 80), (1020 + 18 * math.sin(a), 80 - 18 * math.cos(a))], INK, 3)
    cv.line([(1020, 80), (1032, 86)], INK, 3)
    if fan:
        cx, cy = 640, 18
        cv.line([(cx, -40), (cx, cy)], SOFT, 4)
        for k in range(3):
            a = t * 9 + k * 2 * math.pi / 3
            ex = cx + math.cos(a) * 150
            cv.poly([(cx, cy - 4), (ex, cy - 8 + math.sin(a) * 4), (ex, cy + 8 + math.sin(a) * 4), (cx, cy + 4)],
                    fill=(230, 230, 230), outline=SOFT, ow=2)
        cv.circle(cx, cy, 14, fill=(200, 200, 205), outline=SOFT, ow=2.4)


def draw_desks(cv, y=640, n=4, x0=110, gap=300, w=220, color=P.WOOD):
    """A row of wooden school desks whose top edge is at y (draw after the kids sitting behind)."""
    for i in range(n):
        x = x0 + i * gap
        cv.rect(x - w / 2 + 14, y + 20, x - w / 2 + 28, y + 140, fill=P.WOOD_DARK)
        cv.rect(x + w / 2 - 28, y + 20, x + w / 2 - 14, y + 140, fill=P.WOOD_DARK)
        cv.rect(x - w / 2, y, x + w / 2, y + 26, fill=color, radius=4)
        cv.rect(x - w / 2 + 10, y + 26, x + w / 2 - 10, y + 70, fill=lerp_color(color, INK, 0.15))


# ------------------------------------------------------------------ dining room
def draw_dining_room(cv, t=0.0, night=True):
    cv.rect(-200, -200, 1480, 560, fill=(244, 214, 170), outline=None)
    cv.rect(-200, 560, 1480, 920, fill=P.FLOOR_TILE, outline=None)
    cv.line([(-200, 560), (1480, 560)], SOFT, 3)
    for k in range(-2, 18):
        cv.line([(k * 100, 560), (k * 140 - 400, 920)], lerp_color(P.FLOOR_TILE, INK, 0.12), 2)
    # window
    cv.rect(900, 110, 1120, 330, fill=(40, 50, 100) if night else (170, 220, 240), outline=SOFT, ow=3)
    if night:
        cv.circle(1060, 170, 22, fill=(250, 240, 200), outline=None)
    cv.line([(1010, 110), (1010, 330)], SOFT, 3)
    cv.line([(900, 220), (1120, 220)], SOFT, 3)
    # calendar
    cv.rect(200, 140, 300, 260, fill=P.WHITE, ow=2.6)
    cv.rect(200, 140, 300, 172, fill=P.ACCENT, ow=2.6)
    cv.text(250, 220, "15", 46, P.ACCENT, "black")
    # hanging lamp
    cv.line([(640, -10), (640, 80)], SOFT, 2.4)
    cv.poly([(600, 120), (680, 120), (660, 80), (620, 80)], fill=(240, 200, 90))
    cv.ellipse(640, 124, 18, 8, fill=(255, 245, 200), outline=None)


def draw_dinner_table(cv, x=640, y=560, w=620, dishes=True):
    """Table top edge at y, centred at x. Draw after characters sitting behind it."""
    cv.rect(x - w / 2 + 30, y + 30, x - w / 2 + 52, y + 170, fill=P.WOOD_DARK)
    cv.rect(x + w / 2 - 52, y + 30, x + w / 2 - 30, y + 170, fill=P.WOOD_DARK)
    cv.rect(x - w / 2, y, x + w / 2, y + 34, fill=P.WOOD, radius=6)
    if dishes:
        # rice pot, fish plate, bowls with chopsticks
        cv.ellipse(x, y - 4, 70, 14, fill=P.WHITE)
        cv.poly([(x - 50, y - 6), (x + 50, y - 6), (x + 30, y - 22), (x - 30, y - 22)], fill=(240, 160, 90))
        for bx in (x - 200, x + 200):
            cv.poly(ellipse_pts(bx, y - 22, 34, 22, 0, 180, 10), fill=P.WHITE)
            cv.ellipse(bx, y - 22, 34, 7, fill=(250, 250, 245))
            cv.line([(bx + 10, y - 30), (bx + 50, y - 64)], P.WOOD_DARK, 3)
            cv.line([(bx + 18, y - 28), (bx + 56, y - 58)], P.WOOD_DARK, 3)


# ------------------------------------------------------------------ curtain
def draw_curtain(cv, open_amount=0.0, t=0.0, color=P.CURTAIN):
    """Full-frame stage curtain. open_amount 0 = closed, 1 = fully open (bunched at sides)."""
    dark = P.CURTAIN_DARK
    half = 660 * (1 - open_amount * 0.82)
    for side in (-1, 1):
        x_edge = 640 + side * (640 - half)
        x_out = 640 + side * 720
        xa, xb = min(x_edge, x_out), max(x_edge, x_out)
        cv.rect(xa, -20, xb, 760, fill=color, outline=None)
        n = 8
        for k in range(n + 1):
            xx = lerp(xa, xb, k / n) + math.sin(t * 2 + k) * 2
            cv.line([(xx, -20), (xx + side * open_amount * 10, 760)], dark, 10 if k % 2 else 4)
        cv.line([(x_edge, -20), (x_edge, 760)], INK, 4)
    # valance
    cv.rect(-20, -20, 1300, 60, fill=dark, outline=None)
    for k in range(14):
        cv.poly(ellipse_pts(k * 100 + 50, 60, 50, 26, 0, 180, 10), fill=dark, outline=None)
    cv.line([(-20, 50), (1300, 50)], P.GOLD, 6)


# ------------------------------------------------------------------ courtroom
def draw_plastic_stool(cv, x, y, color=P.PLASTIC_RED, scale=1.0, label=None):
    """Iconic Vietnamese plastic stool standing on (x,y)."""
    with cv.at(x, y, scale):
        dark = lerp_color(color, INK, 0.25)
        cv.poly([(-40, -60), (40, -60), (50, 0), (30, 0), (24, -40), (-24, -40), (-30, 0), (-50, 0)], fill=color)
        cv.ellipse(0, -64, 46, 10, fill=lerp_color(color, (255, 255, 255), 0.2))
        cv.circle(0, -64, 7, fill=dark, outline=None)
        cv.line([(-36, -24), (36, -24)], dark, 3)
        if label:
            cv.text(0, -88, label, 22, INK, "black")


def draw_gavel(cv, x, y, rot=0.0, scale=1.0):
    with cv.at(x, y, scale, rot=rot):
        cv.limb([(0, 0), (0, -80)], 8, P.WOOD)
        cv.rect(-28, -104, 28, -76, fill=P.WOOD_DARK, radius=6)
        cv.rect(-30, -98, -22, -82, fill=P.GOLD, outline=None)
        cv.rect(22, -98, 30, -82, fill=P.GOLD, outline=None)


def draw_courtroom(cv, t=0.0, sign="COURT", defendants=("MOM", "DAD"), bench_x=640):
    """Courtyard 'courtroom': wall, cardboard sign, a bench made of stacked stools + plank,
    and empty plastic stools for the defendants (labelled)."""
    cv.rect(-200, -200, 1480, 520, fill=(236, 214, 176), outline=None)
    for k in range(-2, 16):
        cv.line([(k * 100, -200), (k * 100, 520)], lerp_color((236, 214, 176), INK, 0.06), 2)
    cv.rect(-200, 520, 1480, 920, fill=(206, 190, 160), outline=None)
    cv.line([(-200, 520), (1480, 520)], SOFT, 3)
    # cardboard sign, slightly crooked
    with cv.at(bench_x, 130, 1, rot=-3):
        cv.rect(-170, -50, 170, 50, fill=(214, 170, 112), ow=3)
        cv.text(0, 2, sign, 56, INK, "black")
        cv.line([(-150, -50), (-120, -110)], SOFT, 2)
        cv.line([(150, -50), (120, -110)], SOFT, 2)
    # bench: plank on two stools
    draw_plastic_stool(cv, bench_x - 120, 470, P.PLASTIC_BLUE, 1.3)
    draw_plastic_stool(cv, bench_x + 120, 470, P.PLASTIC_BLUE, 1.3)
    cv.rect(bench_x - 210, 360, bench_x + 210, 392, fill=P.WOOD, radius=4)
    # defendant stools
    for i, d in enumerate(defendants):
        draw_plastic_stool(cv, 180 + i * 150, 620, P.PLASTIC_RED, 1.0, label=d)


# ------------------------------------------------------------------ kitchen
def draw_kitchen(cv, t=0.0, night=True):
    cv.rect(-200, -200, 1480, 540, fill=(214, 228, 220), outline=None)
    for gx in range(0, 1280, 64):        # tiles band
        cv.line([(gx, 300), (gx, 540)], (190, 206, 198), 2)
    for gy in range(300, 541, 60):
        cv.line([(-200, gy), (1480, gy)], (190, 206, 198), 2)
    cv.rect(-200, 540, 1480, 920, fill=(180, 150, 120), outline=None)
    cv.line([(-200, 540), (1480, 540)], SOFT, 3)
    # window
    cv.rect(520, 80, 760, 260, fill=(40, 50, 100) if night else (170, 220, 240), outline=SOFT, ow=3)
    cv.line([(640, 80), (640, 260)], SOFT, 3)
    # fridge
    cv.rect(1020, 140, 1200, 540, fill=(236, 236, 240), ow=3.4, radius=14)
    cv.line([(1020, 290), (1200, 290)], INK, 3)
    cv.rect(1040, 200, 1050, 260, fill=(170, 170, 176), outline=None)
    cv.rect(1040, 320, 1050, 400, fill=(170, 170, 176), outline=None)
    for i, c in enumerate([(240, 120, 120), (120, 190, 240), (250, 210, 90)]):
        cv.circle(1100 + i * 26, 220, 9, fill=c, ow=2)
    # stove counter
    cv.rect(60, 380, 420, 540, fill=(170, 120, 80), ow=3)
    cv.rect(50, 366, 430, 384, fill=(220, 220, 224), ow=3)
    cv.ellipse(150, 360, 50, 10, fill=(80, 80, 84))
    cv.ellipse(320, 360, 50, 10, fill=(80, 80, 84))
    # kettle
    cv.poly(ellipse_pts(150, 330, 40, 30, 180, 360, 10) + [(190, 356), (110, 356)], fill=(230, 200, 80))
    # wall clock
    cv.circle(880, 120, 34, fill=P.WHITE)
    cv.line([(880, 120), (880, 96)], INK, 3)
    cv.line([(880, 120), (898, 128)], INK, 3)


# ------------------------------------------------------------------ book cover
def draw_book_cover(cv, cx=640, cy=360, w=300, h=440, rot=0.0, scale=1.0, show_english=True):
    """Stylised cover of 'Cho tôi xin một vé đi tuổi thơ' (Nguyễn Nhật Ánh); Vietnamese title + author,
    show_english adds the English title line at the bottom."""
    from .text import fit_size, wrap_text
    with cv.at(cx, cy, scale, rot=rot):
        # shadow + spine
        cv.rect(-w / 2 + 10, -h / 2 + 12, w / 2 + 10, h / 2 + 12, fill=INK, outline=None, radius=8)
        cv.rect(-w / 2, -h / 2, w / 2, h / 2, fill=(250, 222, 120), ow=4, radius=8)
        cv.rect(-w / 2, -h / 2, -w / 2 + 18, h / 2, fill=(230, 180, 70), ow=3, radius=4)
        title = "Cho tôi xin một vé đi tuổi thơ"
        tsize = 30 * w / 300
        lines = wrap_text(title, tsize, w - 70, "black")
        # illustration window below the title block: sky, sun, ticket, kite
        ix0, iy0, ix1, iy1 = -w / 2 + 34, -h / 2 + 38 + len(lines) * tsize * 1.13 + 34, w / 2 - 18, h / 2 - 70
        cv.rect(ix0, iy0, ix1, iy1, fill=(150, 210, 236), ow=3, radius=6)
        cv.circle(ix1 - 36, iy0 + 34, 18, fill=P.SUN, ow=2.6)
        cv.rect(ix0 + 2, iy1 - 34, ix1 - 2, iy1 - 2, fill=P.GRASS, outline=None)
        cv.line([(ix0, iy1 - 34), (ix1, iy1 - 34)], INK, 2.6)
        # tiny kite (behind the ticket, so it never covers the TICKET word)
        draw_kite(cv, ix0 + 30, iy0 + 30, 14, P.ACCENT, 0, tail=2)
        # ticket
        tx, ty = (ix0 + ix1) / 2, iy1 - 74
        with cv.at(tx, ty, 1, rot=-8):
            cv.rect(-70, -28, 70, 28, fill=(255, 250, 236), ow=3, radius=4)
            cv.line([(30, -24), (30, 24)], (200, 120, 100), 2)
            cv.text(-20, 0, "TICKET", 21, P.ACCENT, "black")
            cv.text(50, 0, "★", 18, P.ACCENT, "bold")
        # title
        for i, ln in enumerate(lines):
            cv.text(9, -h / 2 + 38 + i * tsize * 1.13, ln, tsize, INK, "black")
        cv.text(9, -h / 2 + 30 + len(lines) * tsize * 1.13 + 6, "NGUYỄN NHẬT ÁNH", 16 * w / 300, P.ACCENT,
                "extrabold")
        if show_english:
            s = fit_size("Give Me a Ticket to Childhood", w - 60, 18, "bolditalic")
            cv.text(9, h / 2 - 40, "Give Me a Ticket to Childhood", s, INK, "bolditalic")
