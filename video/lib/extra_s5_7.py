"""Small helpers shared by scenes 5, 6 and 7 only (owned by those scenes).

Nothing here changes existing lib behaviour; it only adds set pieces / effects that
the shared library does not have yet.
"""
import functools
import math

import numpy as np
from PIL import Image

from . import palette as P
from .core import INK, clamp, ease_in_out, ease_out, ease_out_back, lerp, lerp_color, progress
from .backgrounds import SOFT


# ------------------------------------------------------------------ camera
def cam_keys(t, keys):
    """Piecewise eased camera. keys = [(time, (cx, cy, zoom), hold_style)] sorted by time.
    Between two keys the camera eases (in-out) from one to the next over `dur` given as the
    3rd item of the *target* key (default: the whole gap). Returns (cx, cy, zoom)."""
    if t <= keys[0][0]:
        return keys[0][1]
    for (t0, a, *_), (t1, b, *rest) in zip(keys, keys[1:]):
        if t < t1:
            dur = rest[0] if rest else (t1 - t0)
            # the move happens during the last `dur` seconds before t1
            p = ease_in_out(progress(t, t1 - dur, dur))
            return tuple(lerp(x, y, p) for x, y in zip(a, b))
    return keys[-1][1]


def cam_cut(t, shots):
    """Hard cuts: shots = [(start_time, (cx, cy, zoom))]; returns the active shot."""
    cur = shots[0][1]
    for st, v in shots:
        if t >= st:
            cur = v
    return cur


def to_world(pt, cam):
    """Screen anchor -> world coords under cv.camera(cx, cy, z)."""
    cx, cy, z = cam
    return ((pt[0] - 640) / z + cx, (pt[1] - 360) / z + cy)


# ------------------------------------------------------------------ post fx
@functools.lru_cache(maxsize=64)
def _spot_mask(w, h, cx, cy, rx, ry, soft):
    y, x = np.ogrid[:h, :w]
    d = np.sqrt(((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2)
    m = np.clip((d - 1.0) / soft, 0, 1)
    return m


def spotlight(img, cx, cy, rx, ry, amount, soft=0.35, color=(20, 14, 24)):
    """Darken everything outside an ellipse (screen coords). amount 0..1."""
    if amount <= 0.01:
        return img
    m = _spot_mask(img.width, img.height, int(cx) // 4 * 4, int(cy) // 4 * 4, int(rx), int(ry), soft)
    a = (m * clamp(amount) * 255).astype(np.uint8)
    return Image.composite(Image.new("RGB", img.size, color), img, Image.fromarray(a, "L"))


def grade(img, sat=1.0, mul=(1.0, 1.0, 1.0), lift=(0, 0, 0)):
    """Simple colour grade: saturation, per-channel gain, then lift (one PIL colour matrix, fast)."""
    wr, wg, wb = 0.299, 0.587, 0.114
    rows = []
    for ch in range(3):
        row = [(1 - sat) * w for w in (wr, wg, wb)]
        row[ch] += sat
        rows += [v * mul[ch] for v in row] + [float(lift[ch])]
    return img.convert("RGB", tuple(rows))


# ------------------------------------------------------------------ backdrops
def title_backdrop(cv, t, base=(244, 214, 150), ray=(250, 226, 172)):
    """Screen-space sunburst behind an idea card (slowly turning rays)."""
    cv.rect(-10, -10, 1290, 730, fill=base, outline=None)
    n = 16
    a0 = t * 6
    for k in range(n):
        a = math.radians(a0 + k * 360 / n)
        b = math.radians(a0 + k * 360 / n + 360 / n / 2)
        cv.poly([(640, 360), (640 + math.cos(a) * 1600, 360 + math.sin(a) * 1600),
                 (640 + math.cos(b) * 1600, 360 + math.sin(b) * 1600)], fill=ray, outline=None)


def stage_floor(cv, y=600, x0=-200, x1=1480):
    """Wooden stage boards from y down."""
    cv.rect(x0, y, x1, y + 400, fill=(176, 120, 76), outline=None)
    cv.rect(x0, y, x1, y + 16, fill=(150, 98, 60), outline=None)
    cv.line([(x0, y), (x1, y)], INK, 3.4)
    for k in range(1, 5):
        yy = y + 16 + k * k * 9
        cv.line([(x0, yy), (x1, yy)], (150, 98, 60), 2.4)


def draw_door(cv, x, floor_y, w=170, h=330, open_amount=1.0, outside=(196, 232, 240), frame=P.WOOD_DARK):
    """A doorway in a wall: frame, bright outside, and a door leaf swung open (towards the viewer, left)."""
    x0, x1, y0 = x - w / 2, x + w / 2, floor_y - h
    cv.rect(x0 - 14, y0 - 14, x1 + 14, floor_y, fill=frame, outline=SOFT, ow=2.6)
    cv.rect(x0, y0, x1, floor_y, fill=outside, outline=SOFT, ow=2.4)
    # outside: sunny alley ground + a far house
    cv.rect(x0, floor_y - 70, x1, floor_y, fill=P.GROUND, outline=None)
    cv.rect(x0 + 18, y0 + 40, x0 + 90, floor_y - 70, fill=P.HOUSE_COLORS[0], outline=SOFT, ow=2)
    cv.rect(x0 + 34, y0 + 70, x0 + 72, y0 + 120, fill=P.SHUTTER, outline=SOFT, ow=2)
    cv.circle(x1 - 40, y0 + 50, 20, fill=P.SUN, outline=None)
    # open leaf (a slanted quad, hinge on the right edge)
    lw = w * (1 - 0.75 * open_amount)
    cv.poly([(x1, y0), (x1 + lw * 0.0 + 4, y0), (x1 + 4, floor_y), (x1, floor_y)], fill=P.WOOD, outline=None)
    leaf = [(x0, y0), (x0 + lw, y0 + 14 * open_amount), (x0 + lw, floor_y - 14 * open_amount), (x0, floor_y)]
    if open_amount < 0.99:
        cv.poly(leaf, fill=P.WOOD, outline=SOFT, ow=2.4)
    else:
        lf = [(x0, y0), (x0 - w * 0.32, y0 + 22), (x0 - w * 0.32, floor_y + 22), (x0, floor_y)]
        cv.poly(lf, fill=P.WOOD, outline=SOFT, ow=2.4)
        cv.circle(x0 - w * 0.25, floor_y - h * 0.45 + 18, 6, fill=P.GOLD, outline=SOFT, ow=1.6)


def draw_low_table(cv, x, y, w=220, color=P.WOOD):
    """Little kid's study table, top edge at y (draw after the kid sitting behind it)."""
    dark = lerp_color(color, INK, 0.25)
    cv.rect(x - w / 2 + 14, y + 16, x - w / 2 + 30, y + 92, fill=dark)
    cv.rect(x + w / 2 - 30, y + 16, x + w / 2 - 14, y + 92, fill=dark)
    cv.rect(x - w / 2, y, x + w / 2, y + 20, fill=color, radius=4)


def draw_open_notebook(cv, x, y, s=1.0, scribble=1.0):
    """Open exercise book lying on a table, centred at (x, y)."""
    with cv.at(x, y, s):
        cv.poly([(-62, 0), (-4, -6), (-4, 10), (-60, 14)], fill=P.WHITE, ow=2.4)
        cv.poly([(62, 0), (4, -6), (4, 10), (60, 14)], fill=P.WHITE, ow=2.4)
        n = int(3 * clamp(scribble) + 0.999)
        for k in range(n):
            cv.line([(-52, 2 + k * 3.5), (-14, -2 + k * 3.5)], (90, 110, 170), 1.4)
            cv.line([(14, -2 + k * 3.5), (50, 2 + k * 3.5)], (90, 110, 170), 1.4)


def draw_pencil(cv, x, y, rot=-35, s=1.0):
    with cv.at(x, y, s, rot=rot):
        cv.rect(-4, -40, 4, 6, fill=P.HIGHLIGHT, ow=2)
        cv.poly([(-4, 6), (4, 6), (0, 16)], fill=(240, 210, 160), ow=2)
        cv.rect(-4, -46, 4, -40, fill=(240, 130, 150), ow=2)


def draw_stick(cv, x, y, length=230, rot=0.0, color=(176, 136, 84), w=7):
    """A bamboo switch / cane. (x, y) = bottom end, rot = degrees from vertical (clockwise)."""
    with cv.at(x, y, 1, rot=rot):
        cv.limb([(0, 0), (2, -length * 0.5), (0, -length)], w, color)
        for k in (0.3, 0.62):
            cv.line([(-w / 2 - 1, -length * k), (w / 2 + 1, -length * k)], lerp_color(color, INK, 0.4), 2)
        cv.line([(0, -length), (-10, -length - 18)], color, 2.5)


# ------------------------------------------------------------------ text-ish gags
def stamp(cv, t, start, x, y, text, color=P.ACCENT, rot=-12, size=48, dur=0.16):
    """A rubber stamp slamming down (scale 2.2 -> 1). Draws nothing before `start`.
    Double border (outer + thin inner), sized from the measured text via text.rubber_stamp."""
    p = progress(t, start, dur)
    if p <= 0:
        return
    s = lerp(2.2, 1.0, ease_out(p))
    from .text import rubber_stamp
    rubber_stamp(cv, x, y, text, size=size, color=color, rot=rot, scale=s, ow=6, pad=(24, 18), inner=True,
                 radius=8)


def sparkle(cv, x, y, r, t, start, color=P.HIGHLIGHT):
    """Four-point twinkle that pops and fades over ~0.6 s."""
    p = progress(t, start, 0.6)
    if p <= 0 or p >= 1:
        return
    s = math.sin(p * math.pi) * r
    cv.poly([(x, y - s), (x + s * 0.25, y - s * 0.25), (x + s, y), (x + s * 0.25, y + s * 0.25),
             (x, y + s), (x - s * 0.25, y + s * 0.25), (x - s, y), (x - s * 0.25, y - s * 0.25)],
            fill=color, ow=2.2)
