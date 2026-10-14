"""Core drawing: constants, easing, and the Canvas (vector-ish drawing on Pillow).

All coordinates are LOGICAL pixels of a 1280x720 frame. The Canvas keeps an
affine transform stack (camera, character placement, flips, rotation) and
supersamples (ss=2 by default) so shapes come out anti-aliased after finish().
Outline widths are in logical px and scale with the transform, like vector art.
"""
import math
from contextlib import contextmanager

from PIL import Image, ImageDraw

W, H, FPS = 1280, 720, 24
INK = (38, 32, 40)          # the one outline colour used everywhere
OW = 3.4                    # default outline width (logical px at scale 1)


# ---------------------------------------------------------------- math / easing
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def lerp(a, b, t):
    return a + (b - a) * t


def lerp_pt(p, q, t):
    return (lerp(p[0], q[0], t), lerp(p[1], q[1], t))


def lerp_color(c1, c2, t):
    return tuple(int(round(lerp(a, b, clamp(t)))) for a, b in zip(c1, c2))


def progress(t, start, dur):
    """0 before start, 1 after start+dur, linear in between."""
    if dur <= 0:
        return 1.0 if t >= start else 0.0
    return clamp((t - start) / dur)


def ease_in(x):
    return x * x * x


def ease_out(x):
    return 1 - (1 - x) ** 3


def ease_in_out(x):
    x = clamp(x)
    return 4 * x * x * x if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def ease_out_back(x, s=1.70158):
    x = clamp(x)
    return 1 + (s + 1) * (x - 1) ** 3 + s * (x - 1) ** 2


def ease_out_elastic(x):
    x = clamp(x)
    if x in (0, 1):
        return x
    return 2 ** (-10 * x) * math.sin((x * 10 - 0.75) * (2 * math.pi / 3)) + 1


def bounce(x):
    """Ease-out bounce (ball landing)."""
    x = clamp(x)
    n1, d1 = 7.5625, 2.75
    if x < 1 / d1:
        return n1 * x * x
    if x < 2 / d1:
        x -= 1.5 / d1
        return n1 * x * x + 0.75
    if x < 2.5 / d1:
        x -= 2.25 / d1
        return n1 * x * x + 0.9375
    x -= 2.625 / d1
    return n1 * x * x + 0.984375


def pop(t, start, dur=0.35):
    """Scale factor 0 -> overshoot -> 1 for things popping into view."""
    return ease_out_back(progress(t, start, dur), 2.2)


def wiggle(t, freq=1.0, amp=1.0, seed=0):
    """Smooth deterministic noise in [-amp, amp]."""
    return amp * (0.6 * math.sin(t * freq * 2 * math.pi + seed * 1.7)
                  + 0.4 * math.sin(t * freq * 2 * math.pi * 2.13 + seed * 3.1))


def bezier(p0, p1, p2, n=16):
    """Quadratic bezier points."""
    out = []
    for i in range(n + 1):
        u = i / n
        a, b, c = (1 - u) ** 2, 2 * (1 - u) * u, u * u
        out.append((a * p0[0] + b * p1[0] + c * p2[0], a * p0[1] + b * p1[1] + c * p2[1]))
    return out


def ellipse_pts(cx, cy, rx, ry, a0=0, a1=360, n=40):
    """Points on an ellipse arc; angles in degrees, 0 = +x, 90 = +y (down)."""
    out = []
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        out.append((cx + rx * math.cos(a), cy + ry * math.sin(a)))
    return out


# ---------------------------------------------------------------- canvas
class Canvas:
    """Supersampled drawing surface with a transform stack.

    cv = Canvas(bg=(255,255,255))
    with cv.camera(640, 400, zoom=1.5):        # look at (640,400), zoomed in
        cv.circle(640, 400, 50, fill=(255,0,0))  # outlined with INK by default
    img = cv.finish()                           # 1280x720 RGB PIL.Image
    """

    def __init__(self, bg=(255, 255, 255), ss=2, w=W, h=H):
        self.w, self.h, self.ss = w, h, ss
        self.img = Image.new("RGB", (w * ss, h * ss), bg)
        self.d = ImageDraw.Draw(self.img)
        self.m = (1.0, 0.0, 0.0, 0.0, 1.0, 0.0)   # logical affine: X=a x+b y+c, Y=d x+e y+f
        self._stack = []

    # ---- transforms
    def _mul(self, n):
        a, b, c, d, e, f = self.m
        A, B, C, D, E, F = n
        self.m = (a * A + b * D, a * B + b * E, a * C + b * F + c,
                  d * A + e * D, d * B + e * E, d * C + e * F + f)

    @contextmanager
    def at(self, x=0.0, y=0.0, scale=1.0, flip=False, rot=0.0, sy=None):
        """Local frame: origin at (x,y), uniform scale, optional horizontal flip,
        rotation in degrees (clockwise on screen)."""
        self._stack.append(self.m)
        sx = -scale if flip else scale
        sy = scale if sy is None else sy
        r = math.radians(rot)
        cr, sr = math.cos(r), math.sin(r)
        self._mul((cr * sx, -sr * sy, x, sr * sx, cr * sy, y))
        try:
            yield self
        finally:
            self.m = self._stack.pop()

    @contextmanager
    def camera(self, cx, cy, zoom=1.0, rot=0.0):
        """World point (cx,cy) is shown at the frame centre, magnified by zoom."""
        self._stack.append(self.m)
        self._mul((1, 0, self.w / 2, 0, 1, self.h / 2))
        r = math.radians(rot)
        self._mul((zoom * math.cos(r), -zoom * math.sin(r), 0, zoom * math.sin(r), zoom * math.cos(r), 0))
        self._mul((1, 0, -cx, 0, 1, -cy))
        try:
            yield self
        finally:
            self.m = self._stack.pop()

    def to_screen(self, x, y):
        """Logical screen coords of a local point (useful for anchors/text overlays)."""
        a, b, c, d, e, f = self.m
        return (a * x + b * y + c, d * x + e * y + f)

    def scale_now(self):
        a, b, c, d, e, f = self.m
        return math.sqrt(abs(a * e - b * d))

    def _rotated(self):
        a, b, c, d, e, f = self.m
        return abs(b) > 1e-6 or abs(d) > 1e-6

    def _dev(self, x, y):
        a, b, c, d, e, f = self.m
        s = self.ss
        return ((a * x + b * y + c) * s, (d * x + e * y + f) * s)

    def _devw(self, w):
        return max(1, int(round(w * self.scale_now() * self.ss)))

    # ---- primitives (all take local coords; outline=None disables stroke)
    def poly(self, pts, fill=None, outline=INK, ow=OW, closed=True):
        dp = [self._dev(x, y) for x, y in pts]
        if fill is not None and len(dp) >= 3:
            self.d.polygon(dp, fill=fill)
        if outline is not None and ow > 0:
            w = self._devw(ow)
            path = dp + [dp[0]] if closed else dp
            self._stroke(path, outline, w, True)

    def ellipse(self, cx, cy, rx, ry, fill=None, outline=INK, ow=OW):
        if self._rotated():
            self.poly(ellipse_pts(cx, cy, rx, ry, n=48), fill, outline, ow)
            return
        x0, y0 = self._dev(cx - rx, cy - ry)
        x1, y1 = self._dev(cx + rx, cy + ry)
        x0, x1 = min(x0, x1), max(x0, x1)
        y0, y1 = min(y0, y1), max(y0, y1)
        if outline is not None and ow > 0 and fill is None:
            h = self._devw(ow) / 2.0
            self.d.ellipse([x0 - h, y0 - h, x1 + h, y1 + h], outline=outline, width=self._devw(ow))
        elif outline is not None and ow > 0:
            h = self._devw(ow) / 2.0
            self.d.ellipse([x0 - h, y0 - h, x1 + h, y1 + h], fill=outline)
            if fill is not None and x1 - h > x0 + h and y1 - h > y0 + h:
                self.d.ellipse([x0 + h, y0 + h, x1 - h, y1 - h], fill=fill)
        elif fill is not None:
            self.d.ellipse([x0, y0, x1, y1], fill=fill)

    def circle(self, cx, cy, r, fill=None, outline=INK, ow=OW):
        self.ellipse(cx, cy, r, r, fill, outline, ow)

    def rect(self, x0, y0, x1, y1, fill=None, outline=INK, ow=OW, radius=0):
        if self._rotated():
            if radius > 0:
                pts = rrect_pts(x0, y0, x1, y1, radius)
            else:
                pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
            self.poly(pts, fill, outline, ow)
            return
        X0, Y0 = self._dev(x0, y0)
        X1, Y1 = self._dev(x1, y1)
        X0, X1 = min(X0, X1), max(X0, X1)
        Y0, Y1 = min(Y0, Y1), max(Y0, Y1)
        R = radius * self.scale_now() * self.ss
        if outline is not None and ow > 0 and fill is None:
            h = self._devw(ow) / 2.0
            self.d.rounded_rectangle([X0 - h, Y0 - h, X1 + h, Y1 + h], radius=R + h, outline=outline,
                                     width=self._devw(ow))
        elif outline is not None and ow > 0:
            h = self._devw(ow) / 2.0
            self.d.rounded_rectangle([X0 - h, Y0 - h, X1 + h, Y1 + h], radius=R + h, fill=outline)
            if fill is not None and X1 - h > X0 + h and Y1 - h > Y0 + h:
                self.d.rounded_rectangle([X0 + h, Y0 + h, X1 - h, Y1 - h], radius=max(0, R - h), fill=fill)
        elif fill is not None:
            self.d.rounded_rectangle([X0, Y0, X1, Y1], radius=R, fill=fill)

    def _stroke(self, dp, fill, w, round_caps):
        """Thick polyline in device px with round joints (circles are much cheaper than
        Pillow's joint='curve', which draws a pieslice per vertex)."""
        self.d.line(dp, fill=fill, width=w)
        if w <= 2:
            return
        r = w / 2.0 - 0.25
        pts = dp if round_caps else dp[1:-1]
        last = None
        for x, y in pts:
            if last is not None and abs(x - last[0]) + abs(y - last[1]) < r * 0.5:
                continue      # skip near-duplicate vertices on dense curves
            self.d.ellipse([x - r, y - r, x + r, y + r], fill=fill)
            last = (x, y)

    def view_bounds(self):
        """Visible rectangle (x0, y0, x1, y1) in current local coords (ignores rotation)."""
        a, b, c, d, e, f = self.m
        x0, x1 = (0 - c) / a, (self.w - c) / a
        y0, y1 = (0 - f) / e, (self.h - f) / e
        return (min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1))

    def line(self, pts, fill=INK, width=OW, round_caps=True):
        dp = [self._dev(x, y) for x, y in pts]
        self._stroke(dp, fill, self._devw(width), round_caps)

    def limb(self, pts, width, fill, outline=INK, ow=OW):
        """Thick rounded stroke with an outline (arms, legs, poles, ropes)."""
        if outline is not None:
            self.line(pts, outline, width + 2 * ow)
        self.line(pts, fill, width)

    def curve(self, p0, p1, p2, fill=INK, width=OW, n=16):
        self.line(bezier(p0, p1, p2, n), fill, width)

    def text(self, x, y, s, size, fill=INK, weight="bold", anchor="mm", stroke=0, stroke_fill=INK,
             spacing=4, align="center"):
        from .text import font
        X, Y = self._dev(x, y)
        sc = self.scale_now() * self.ss
        f = font(max(1, int(round(size * sc))), weight)
        sw = int(round(stroke * sc))
        if "\n" in s:
            self.d.multiline_text((X, Y), s, font=f, fill=fill, anchor=anchor, stroke_width=sw,
                                  stroke_fill=stroke_fill, spacing=int(spacing * sc), align=align)
        else:
            self.d.text((X, Y), s, font=f, fill=fill, anchor=anchor, stroke_width=sw, stroke_fill=stroke_fill)

    def paste(self, im, x, y, scale=1.0):
        """Paste an RGBA/RGB image whose top-left is the local point (x,y). No rotation."""
        sc = self.scale_now() * self.ss * scale
        if abs(sc - 1) > 1e-3:
            im = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.BILINEAR)
        X, Y = self._dev(x, y)
        self.img.paste(im, (int(X), int(Y)), im if im.mode == "RGBA" else None)

    def overlay(self, color, alpha):
        """Full-frame translucent colour wash (screen space)."""
        if alpha <= 0:
            return
        layer = Image.new("RGB", self.img.size, color)
        self.img = Image.blend(self.img, layer, clamp(alpha))
        self.d = ImageDraw.Draw(self.img)

    def finish(self):
        img = self.img
        if self.ss > 1:
            img = img.reduce(self.ss)
        return img


def rrect_pts(x0, y0, x1, y1, r, n=6):
    r = min(r, (x1 - x0) / 2, (y1 - y0) / 2)
    pts = []
    for cx, cy, a0 in ((x1 - r, y0 + r, 270), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)):
        pts += ellipse_pts(cx, cy, r, r, a0, a0 + 90, n)
    return pts
