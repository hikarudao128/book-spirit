"""Extra helpers for scenes 2-4 (owned by those scenes; other scenes may import but should not edit).

  phrase_starts(ctx, line_id, n)       phrase onsets from the line's audio envelope (comma pauses),
                                       more accurate than ctx.find_word for fast lists
  polaroid(cv, draw_fn, ...)           render a little 1280x720 "world" into a tilted instant photo
  photo_back(cv, ...)                  cheap stand-in for an older photo lying under the current one
  to_world(pt, cam)                    screen anchor -> world coords for a cv.camera(cx, cy, zoom)
  props: bed, toothbrush/foam, sink+mirror, alarm clock, school gate, desk lamp, notebook stack,
         basin, sweat drop, lightbulb, number badge, rubber stamp, chewed notebook, icons, thought bubble,
         spotlight, speed lines, sparkle, heat waves, jail bars
"""
import math

from PIL import Image

from . import palette as P
from .core import INK, Canvas, clamp, ease_out, ease_out_back, ellipse_pts, lerp, lerp_color, progress
from .text import text_width

SOFT = (70, 60, 66)


# ------------------------------------------------------------------ timing
def _silent_runs(env, thr=0.08):
    loud = [k for k, v in enumerate(env) if v >= thr]
    if len(loud) < 2:
        return []
    first, last = loud[0], loud[-1]
    runs, k = [], first
    while k <= last:
        if env[k] < thr:
            j = k
            while j <= last and env[j] < thr:
                j += 1
            runs.append((k, j))
            k = j
        else:
            k += 1
    return runs


def phrase_starts(ctx, line_id, words, snap=0.4, thr=0.08):
    """Onset times of phrases beginning at the given words (list of word substrings, in order).
    Starts from ctx.find_word estimates, then snaps each one to the end of the nearest silent run in
    the line's audio envelope (within `snap` s). Much tighter than the raw estimate on fast lists."""
    l = ctx.line(line_id)
    fps = ctx.fps
    runs = _silent_runs(l.envelope, thr)
    loud0 = next((k for k, v in enumerate(l.envelope) if v >= thr), 0)
    ends = [(l.start + loud0 / fps, 6)] + [(l.start + j / fps, j - k) for k, j in runs]
    out, nth = [], {}
    for w in words:
        n = nth.get(w, 0)
        nth[w] = n + 1
        est = ctx.find_word(line_id, w, n)
        # prefer real pauses (longer silent runs) over tiny dips between syllables
        best = min(ends, key=lambda e: abs(e[0] - est) - 0.04 * min(e[1], 6))[0] if ends else est
        out.append(best if abs(best - est) <= snap else est)
    # keep monotonic
    for i in range(1, len(out)):
        out[i] = max(out[i], out[i - 1] + 0.12)
    return out


def to_world(pt, cam):
    cx, cy, z = cam
    return ((pt[0] - 640) / z + cx, (pt[1] - 360) / z + cy)


# ------------------------------------------------------------------ photos
def polaroid(cv, draw_fn, cx, cy, w=880, h=495, rot=0.0, scale=1.0, caption="", border=18, bottom=76,
             cap_size=40, cap_color=INK, shadow=True):
    """Render draw_fn(sub_canvas) - authored in 1280x720 world coords - inside an instant photo
    centred at screen (cx, cy). Call OUTSIDE any camera. rot in degrees (clockwise)."""
    if scale <= 0.01:
        return
    ss = cv.ss
    s = scale
    TW, TH = (w + 2 * border) * s, (h + border + bottom) * s
    sub = Canvas(bg=P.WHITE, ss=ss, w=int(round(TW)), h=int(round(TH)))
    with sub.at(border * s, border * s, s * w / 1280.0):
        draw_fn(sub)
    # re-cover the border (content may spill) and draw the frame
    sub.rect(0, 0, TW, border * s, fill=P.WHITE, outline=None)
    sub.rect(0, 0, border * s, TH, fill=P.WHITE, outline=None)
    sub.rect(TW - border * s, 0, TW, TH, fill=P.WHITE, outline=None)
    sub.rect(0, (border + h) * s, TW, TH, fill=P.WHITE, outline=None)
    sub.rect(border * s, border * s, (border + w) * s, (border + h) * s, fill=None, ow=2.5 * s)
    if caption:
        size = cap_size
        while size > 18 and text_width(caption, size, "black") > w - 20:
            size -= 2
        sub.text(TW / 2, (border + h + bottom / 2 + 2) * s, caption, size * s, cap_color, "black")
    im = sub.img
    hw, hh = TW / 2, TH / 2
    corners = [(-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)]
    if shadow:
        with cv.at(cx + 9 * s, cy + 12 * s, 1, rot=rot):
            cv.poly(corners, fill=(40, 30, 30), outline=None)
    if abs(rot) > 0.05:
        im = im.convert("RGBA").rotate(-rot, resample=Image.NEAREST, expand=True)
    X, Y = cv.to_screen(cx, cy)
    px, py = int(round(X * ss - im.width / 2)), int(round(Y * ss - im.height / 2))
    cv.img.paste(im, (px, py), im if im.mode == "RGBA" else None)
    with cv.at(cx, cy, 1, rot=rot):
        cv.poly(corners, fill=None, ow=3)


def photo_back(cv, cx, cy, w=880, h=495, rot=0.0, scale=1.0, tone=(200, 200, 200), border=18, bottom=76):
    """An older photo under the pile: frame + a flat tone."""
    s = scale
    TW, TH = (w + 2 * border) * s, (h + border + bottom) * s
    with cv.at(cx, cy, 1, rot=rot):
        cv.poly([(-TW / 2 + 8, -TH / 2 + 10), (TW / 2 + 8, -TH / 2 + 10), (TW / 2 + 8, TH / 2 + 10),
                 (-TW / 2 + 8, TH / 2 + 10)], fill=(40, 30, 30), outline=None)
        cv.rect(-TW / 2, -TH / 2, TW / 2, TH / 2, fill=P.WHITE, ow=3)
        x0, y0 = -TW / 2 + border * s, -TH / 2 + border * s
        cv.rect(x0, y0, x0 + w * s, y0 + h * s, fill=tone, ow=2)


def corkboard(cv, t=0.0):
    """Full-frame cork texture (screen space)."""
    cv.rect(-10, -10, 1290, 730, fill=(196, 150, 100), outline=None)
    import random
    rnd = random.Random(7)
    for _ in range(140):
        x, y = rnd.uniform(0, 1280), rnd.uniform(0, 720)
        r = rnd.uniform(2, 5)
        cv.ellipse(x, y, r, r * 0.7, fill=(176, 130, 84), outline=None)
    cv.rect(-10, -10, 1290, 22, fill=P.WOOD, outline=None)
    cv.rect(-10, 698, 1290, 730, fill=P.WOOD, outline=None)
    cv.line([(-10, 22), (1290, 22)], INK, 3)
    cv.line([(-10, 698), (1290, 698)], INK, 3)


def pin(cv, x, y, color=P.ACCENT):
    cv.circle(x + 2, y + 3, 9, fill=(60, 40, 30), outline=None)
    cv.circle(x, y, 9, fill=color, ow=2.5)
    cv.circle(x - 3, y - 3, 3, fill=P.WHITE, outline=None)


# ------------------------------------------------------------------ props: home
def draw_bed(cv, x, y, w=420, night=False, blanket=True, front_only=False):
    """Bed whose mattress top is at y, centred on x. front_only draws only the blanket (call
    after the sleeper)."""
    frame = P.WOOD if not night else lerp_color(P.WOOD, (30, 30, 70), 0.45)
    sheet = (240, 240, 250) if not night else (120, 130, 180)
    blank = (110, 160, 220) if not night else (60, 80, 150)
    if not front_only:
        cv.rect(x - w / 2 - 14, y - 150, x - w / 2 + 6, y + 110, fill=frame, radius=6)   # headboard
        cv.rect(x - w / 2, y, x + w / 2, y + 50, fill=sheet, radius=10)                   # mattress
        cv.rect(x - w / 2, y + 50, x + w / 2, y + 80, fill=frame, radius=4)
        cv.rect(x - w / 2 + 10, y + 80, x - w / 2 + 30, y + 110, fill=frame)
        cv.rect(x + w / 2 - 30, y + 80, x + w / 2 - 10, y + 110, fill=frame)
        cv.ellipse(x - w / 2 + 70, y - 14, 60, 26, fill=P.WHITE)                           # pillow
    if blanket:
        cv.poly([(x - w / 2 + 110, y - 18), (x + w / 2 + 8, y - 10), (x + w / 2 + 14, y + 58),
                 (x - w / 2 + 104, y + 58)], fill=blank)
        cv.line([(x - w / 2 + 112, y - 4), (x + w / 2 + 8, y + 4)], lerp_color(blank, P.WHITE, 0.4), 6)


def draw_alarm_clock(cv, x, y, t=0.0, ringing=True, s=1.0):
    sh = math.sin(t * 60) * 5 if ringing else 0
    with cv.at(x + sh, y, s, rot=sh * 1.2):
        for side in (-1, 1):
            cv.circle(side * 26, -50, 14, fill=P.ACCENT, ow=3)
        cv.line([(-24, 22), (-30, 34)], INK, 4)
        cv.line([(24, 22), (30, 34)], INK, 4)
        cv.circle(0, 0, 38, fill=P.ACCENT, ow=3.4)
        cv.circle(0, 0, 28, fill=P.WHITE, ow=2.5)
        cv.line([(0, 0), (0, -18)], INK, 3)
        cv.line([(0, 0), (12, 4)], INK, 3)
    if ringing:
        for side in (-1, 1):
            for k in range(3):
                a = math.radians(-60 + k * 30)
                r0, r1 = 56, 74
                cv.line([(x + side * math.cos(a) * r0 * s, y - 10 * s + math.sin(a) * r0 * s),
                         (x + side * math.cos(a) * r1 * s, y - 10 * s + math.sin(a) * r1 * s)], INK, 4)


def draw_window(cv, x0, y0, x1, y1, sky=(170, 220, 240), night=False, bars=0, bar_col=(70, 70, 80)):
    cv.rect(x0, y0, x1, y1, fill=(40, 50, 100) if night else sky, outline=SOFT, ow=4)
    if night:
        cv.circle(x1 - (x1 - x0) * 0.3, y0 + (y1 - y0) * 0.3, 18, fill=(250, 240, 200), outline=None)
    cv.line([((x0 + x1) / 2, y0), ((x0 + x1) / 2, y1)], SOFT, 4)
    cv.line([(x0, (y0 + y1) / 2), (x1, (y0 + y1) / 2)], SOFT, 4)
    for k in range(1, bars + 1):
        xx = x0 + (x1 - x0) * k / (bars + 1)
        cv.line([(xx, y0), (xx, y1)], bar_col, 6)


def draw_toothbrush(cv, hand, mouth, t=0.0, color=(70, 180, 220)):
    """Brush from the hand to the mouth, scrubbing."""
    jig = math.sin(t * 40) * 4
    hx, hy = hand
    mx, my = mouth[0] + jig, mouth[1]
    cv.limb([(hx, hy), (mx, my)], 6, color)
    cv.rect(mx - 9, my - 6, mx + 6, my + 3, fill=P.WHITE, ow=2)


def draw_foam(cv, x, y, r=1.0, t=0.0):
    import random
    rnd = random.Random(3)
    for k in range(9):
        a = rnd.uniform(0, 2 * math.pi)
        d = rnd.uniform(4, 22) * r
        rr = rnd.uniform(5, 9) * r * (1 + 0.15 * math.sin(t * 12 + k))
        cv.circle(x + math.cos(a) * d * 1.3, y + math.sin(a) * d * 0.6, rr, fill=P.WHITE, ow=2)


def draw_sink_mirror(cv, x, mirror_y=200, sink_y=520):
    cv.rect(x - 180, mirror_y - 150, x + 180, mirror_y + 130, fill=(180, 200, 210), radius=20, ow=4)
    cv.rect(x - 160, mirror_y - 130, x + 160, mirror_y + 110, fill=(210, 232, 240), outline=None, radius=14)
    cv.line([(x - 120, mirror_y - 90), (x - 60, mirror_y - 120)], P.WHITE, 8)
    cv.line([(x - 130, mirror_y - 50), (x - 40, mirror_y - 100)], P.WHITE, 5)


def draw_sink_front(cv, x, sink_y=520):
    cv.rect(x - 60, sink_y + 30, x + 60, sink_y + 220, fill=(235, 235, 240))
    cv.rect(x - 200, sink_y - 10, x + 200, sink_y + 40, fill=P.WHITE, radius=14)
    cv.rect(x - 20, sink_y - 46, x + 20, sink_y - 10, fill=(190, 190, 200), radius=4)
    cv.rect(x - 8, sink_y - 46, x + 40, sink_y - 34, fill=(190, 190, 200), radius=4)


def draw_tiles(cv, x0, y0, x1, y1, col=(190, 228, 222), gap=64):
    cv.rect(x0, y0, x1, y1, fill=col, outline=None)
    line = lerp_color(col, INK, 0.12)
    x = x0
    while x <= x1:
        cv.line([(x, y0), (x, y1)], line, 2)
        x += gap
    y = y0
    while y <= y1:
        cv.line([(x0, y), (x1, y)], line, 2)
        y += gap


def draw_school_gate(cv, x, ground):
    for side in (-1, 1):
        cv.rect(x + side * 300 - 34, ground - 330, x + side * 300 + 34, ground, fill=(236, 214, 150), ow=3.4)
        cv.rect(x + side * 300 - 44, ground - 350, x + side * 300 + 44, ground - 326, fill=P.ROOF, ow=3)
    cv.rect(x - 280, ground - 320, x + 280, ground - 250, fill=(40, 90, 170), ow=3.4, radius=6)
    cv.text(x, ground - 285, "TRƯỜNG TIỂU HỌC", 36, P.HIGHLIGHT, "black")
    # gate bars
    for k in range(9):
        xx = x - 250 + k * 62
        cv.line([(xx, ground - 230), (xx, ground)], (110, 110, 120), 6)
    cv.line([(x - 266, ground - 230), (x + 266, ground - 230)], (110, 110, 120), 8)
    cv.line([(x - 266, ground - 110), (x + 266, ground - 110)], (110, 110, 120), 6)


def draw_backpack(cv, x, y, scale=1.0, facing=1, color=(230, 90, 60)):
    """Side-view school backpack on the BACK of a walking stick kid whose feet are at (x, y) and who
    faces `facing` (+1 right, -1 left). Sized for Mui-like kids (shoulder ~97 px above the feet at
    scale 1). Draw BEFORE the kid."""
    s = scale
    bx = x - facing * 22 * s
    with cv.at(bx, y - 74 * s, s):
        cv.rect(-17, -26, 17, 26, fill=color, radius=9, ow=3)
        cv.rect(-13 if facing < 0 else -4, -6, 4 if facing < 0 else 13, 16,
                fill=lerp_color(color, INK, 0.15), radius=5, ow=2.4)
        cv.line([(-8, -30), (8, -30)], lerp_color(color, INK, 0.3), 3)


def draw_backpack_straps(cv, x, y, scale=1.0, facing=1, color=(230, 90, 60)):
    """The one strap visible over the near shoulder (draw AFTER the kid)."""
    s = scale
    cv.line([(x - facing * 6 * s, y - 97 * s), (x + facing * 3 * s, y - 72 * s), (x - facing * 8 * s, y - 56 * s)],
            lerp_color(color, INK, 0.25), 3.6 * s)


def draw_desk_lamp(cv, x, y, on=True, s=1.0):
    with cv.at(x, y, s):
        if on:
            cv.poly([(-10, -150), (90, -150), (150, 0), (-70, 0)], fill=(255, 240, 170), outline=None)
        cv.ellipse(0, 0, 40, 10, fill=(80, 80, 90))
        cv.limb([(0, 0), (-30, -90), (20, -150)], 8, (80, 80, 90))
        cv.poly([(0, -170), (60, -150), (40, -120), (-10, -140)], fill=(80, 140, 90))


def draw_notebook_stack(cv, x, y, n=8, w=120, seed=0):
    """A wobbly stack of notebooks whose bottom is at y."""
    import random
    rnd = random.Random(seed)
    cols = [(70, 120, 200), (230, 90, 70), (110, 180, 110), (250, 200, 80), (170, 120, 200)]
    yy = y
    for k in range(n):
        h = 18
        dx = rnd.uniform(-12, 12)
        cv.rect(x - w / 2 + dx, yy - h, x + w / 2 + dx, yy, fill=cols[(k + seed) % len(cols)], radius=3, ow=2.6)
        cv.line([(x - w / 2 + dx + 8, yy - h / 2), (x + w / 2 + dx - 30, yy - h / 2)], P.WHITE, 2)
        yy -= h
    return yy


def draw_basin(cv, x, y, s=1.0, stink=True, t=0.0, label=True):
    with cv.at(x, y, s):
        cv.poly(ellipse_pts(0, -30, 80, 40, 0, 180, 14) + [(-80, -30)], fill=(90, 140, 200))
        cv.ellipse(0, -30, 80, 18, fill=(120, 170, 220))
        cv.ellipse(0, -30, 64, 11, fill=(150, 160, 110), outline=None)
        if stink:
            for k in range(3):
                xx = -40 + k * 40
                ph = t * 3 + k
                pts = [(xx + math.sin(ph + j * 0.9) * 8, -50 - j * 12) for j in range(7)]
                cv.line(pts, (120, 150, 60), 4)
    if label:
        from .text import label as _label
        _label(cv, x, y + 30 * s, "FOOT WATER", int(20 * s), bg=P.HIGHLIGHT)


def sweat(cv, x, y, s=1.0, t=0.0, period=1.2, seed=0):
    """A sweat drop sliding down from (x, y)."""
    ph = ((t + seed * 0.37) % period) / period
    yy = y + ph * 40 * s
    with cv.at(x, yy, s * (1 - 0.2 * ph)):
        cv.poly([(0, -16)] + ellipse_pts(0, 0, 9, 10, -10, 190, 10), fill=(150, 210, 250), ow=2.5)
        cv.circle(-3, 1, 2.5, fill=P.WHITE, outline=None)


def lightbulb(cv, x, y, s=1.0, glow=1.0):
    if s <= 0.01:
        return
    with cv.at(x, y, s):
        if glow > 0:
            for k in range(8):
                a = math.radians(k * 45 + 22)
                cv.line([(math.cos(a) * 52, math.sin(a) * 52 - 8), (math.cos(a) * 72, math.sin(a) * 72 - 8)],
                        P.HIGHLIGHT, 6)
        cv.circle(0, -10, 38, fill=(255, 236, 120), ow=3.4)
        cv.rect(-16, 22, 16, 46, fill=(170, 170, 180), radius=4, ow=3)
        cv.line([(-16, 32), (16, 32)], INK, 2.5)
        cv.curve((-12, 6), (0, -24), (12, 6), (230, 160, 40), 3)


def badge(cv, x, y, s, text, size=70, fill=P.ACCENT, ink=P.WHITE, r=56):
    if s <= 0.01:
        return
    with cv.at(x, y, s):
        cv.circle(5, 7, r, fill=INK, outline=None)
        cv.circle(0, 0, r, fill=fill, ow=4)
        cv.text(0, 2, text, size, ink, "black", stroke=3, stroke_fill=INK)


def stamp(cv, x, y, text, s=1.0, rot=-12, color=P.ACCENT, size=48, fill=None):
    """Rubber-stamp text box (red outline + red letters); fill=colour gives it a solid backing."""
    if s <= 0.01:
        return
    w = text_width(text, size, "black") + 50
    h = size * 1.4
    with cv.at(x, y, s, rot=rot):
        if fill is not None:
            cv.rect(-w / 2, -h / 2, w / 2, h / 2, fill=fill, outline=None, radius=10)
        cv.rect(-w / 2, -h / 2, w / 2, h / 2, fill=None, outline=color, ow=7, radius=10)
        cv.text(0, 2, text, size, color, "black")


def chewed_notebook(cv, x, y, s=1.0, rot=-8):
    with cv.at(x, y, s, rot=rot):
        pts = [(-50, -30), (-20, -32), (-14, -24), (-4, -34), (10, -26), (22, -34), (50, -30), (54, 4),
               (44, 10), (50, 20), (40, 30), (-48, 32), (-40, 18), (-54, 10)]
        cv.poly(pts, fill=(70, 120, 200), ow=3)
        cv.poly([(-36, -16), (30, -18), (34, 14), (-30, 18)], fill=(240, 236, 220), ow=2)
        for k in range(3):
            cv.line([(-26, -8 + k * 9), (24, -9 + k * 9)], (150, 170, 210), 2)
        # bite marks
        for bx in (-14, 4, 22):
            cv.circle(bx, -32, 6, fill=P.FLOOR_TILE, outline=None)
    # paper shreds around
    import random
    rnd = random.Random(5)
    for k in range(7):
        sx = x + rnd.uniform(-110, 110) * s
        sy = y + rnd.uniform(16, 44) * s
        with cv.at(sx, sy, s, rot=rnd.uniform(-60, 60)):
            cv.poly([(-9, -5), (8, -6), (10, 4), (-7, 6)], fill=(240, 236, 220) if k % 2 else (70, 120, 200),
                    ow=2)


# ------------------------------------------------------------------ icons (for visual equations)
def icon_notebook(cv, x, y, s=1.0):
    with cv.at(x, y, s, rot=-6):
        cv.rect(-30, -38, 30, 38, fill=(70, 120, 200), radius=4, ow=3)
        cv.rect(-18, -26, 20, -10, fill=P.WHITE, outline=None)
        cv.line([(-30, -38), (-30, 38)], INK, 5)


def icon_hat(cv, x, y, s=1.0):
    with cv.at(x, y, s):
        cv.ellipse(0, 18, 48, 12, fill=(200, 80, 70))
        cv.rect(-28, -30, 28, 18, fill=(200, 80, 70), radius=10)
        cv.rect(-28, 2, 28, 12, fill=INK, outline=None)


def icon_dog(cv, x, y, s=1.0):
    with cv.at(x, y, s):
        col = (222, 168, 96)
        cv.poly([(-14, -30), (-34, -6), (-20, 4)], fill=(160, 120, 70))
        cv.circle(0, 0, 30, fill=col)
        cv.ellipse(22, 12, 20, 14, fill=(236, 196, 140))
        cv.circle(40, 6, 6, fill=INK, outline=None)
        cv.circle(8, -6, 5, fill=INK, outline=None)
        cv.poly([(-6, -28), (-30, 0), (-12, 10)], fill=(160, 120, 70))


def icon_banana(cv, x, y, s=1.0):
    with cv.at(x, y, s, rot=-20):
        pts = ellipse_pts(0, -30, 48, 54, 30, 150, 14) + ellipse_pts(0, -40, 40, 40, 140, 40, 14)
        cv.poly(pts, fill=(255, 220, 80), ow=3)
        cv.line([(-37, 4), (-42, 0)], INK, 5)


def icon_foot(cv, x, y, s=1.0):
    with cv.at(x, y, s):
        cv.ellipse(0, 6, 26, 36, fill=P.SKIN)
        for k, (tx, ty, r) in enumerate(((-16, -34, 8), (-3, -40, 7.5), (9, -38, 6.5), (18, -32, 6), (24, -24, 5))):
            cv.circle(tx, ty, r, fill=P.SKIN, ow=2.6)


def icon_mouth(cv, x, y, s=1.0):
    with cv.at(x, y, s):
        pts = ellipse_pts(0, -6, 42, 34, 0, 180, 16) + [(-42, -6)]
        cv.poly(pts, fill=P.MOUTH, ow=3.4)
        cv.rect(-30, -6, 30, 4, fill=P.TEETH, outline=None)
        cv.ellipse(0, 16, 18, 8, fill=P.TONGUE, outline=None)
        cv.line([(-46, -6), (46, -6)], (190, 70, 80), 6)


def icon_briefcase(cv, x, y, s=1.0, col=(120, 110, 100)):
    with cv.at(x, y, s):
        cv.rect(-18, -42, 18, -26, fill=None, ow=5, radius=6)
        cv.rect(-46, -30, 46, 30, fill=col, radius=8)
        cv.line([(-46, -4), (46, -4)], INK, 3)
        cv.rect(-8, -10, 8, 4, fill=(200, 190, 160), ow=2)


def thought_bubble(cv, x, y, w, h, tail_to, s=1.0, fill=P.WHITE):
    """Cloud-ish thought bubble centred (x, y); tail_to = (tx, ty) point near the thinker's head."""
    if s <= 0.01:
        return
    tx, ty = tail_to
    for k, r in enumerate((7, 11, 16)):
        f = (k + 1) / 4
        cv.circle(lerp(tx, x, f * 0.8), lerp(ty, y + h / 2 * s, f * 0.9), r * s, fill=fill, ow=3)
    with cv.at(x, y, s):
        n = 10
        for k in range(n):
            a = 2 * math.pi * k / n
            cv.circle(math.cos(a) * w * 0.42, math.sin(a) * h * 0.4, min(w, h) * 0.26, fill=fill, ow=3.2)
        cv.ellipse(0, 0, w * 0.46, h * 0.42, fill=fill, outline=None)
        for k in range(n):
            a = 2 * math.pi * k / n
            cv.circle(math.cos(a) * w * 0.42, math.sin(a) * h * 0.4, min(w, h) * 0.26 - 3.5, fill=fill,
                      outline=None)


# ------------------------------------------------------------------ fx-ish drawing
def spotlight(cv, x, top, floor_y, w_top=120, w_floor=520, col=(70, 80, 130), floor_col=(96, 104, 150)):
    cv.poly([(x - w_top / 2, top), (x + w_top / 2, top), (x + w_floor / 2, floor_y), (x - w_floor / 2, floor_y)],
            fill=col, outline=None)
    cv.ellipse(x, floor_y, w_floor / 2, w_floor * 0.09, fill=floor_col, outline=None)


def speed_lines(cv, x0, x1, y_mid, spread=200, n=9, seed=0, col=P.WHITE, t=0.0, width=5):
    import random
    rnd = random.Random(seed)
    for k in range(n):
        yy = y_mid + rnd.uniform(-spread / 2, spread / 2)
        a = rnd.uniform(0, 1)
        l = rnd.uniform(0.3, 0.8) * (x1 - x0)
        xs = x0 + ((a + t * 3) % 1) * (x1 - x0) * 0.5
        cv.line([(xs, yy), (xs + l, yy)], col, width)


def sparkle(cv, x, y, s=1.0, col=P.HIGHLIGHT):
    if s <= 0.01:
        return
    with cv.at(x, y, s):
        pts = []
        for k in range(8):
            a = math.radians(k * 45 - 90)
            r = 26 if k % 2 == 0 else 8
            pts.append((math.cos(a) * r, math.sin(a) * r))
        cv.poly(pts, fill=col, ow=2.6)


def heat_waves(cv, x0, x1, y, t, n=5, col=(255, 200, 120), amp=8):
    for k in range(n):
        xx = lerp(x0, x1, (k + 0.5) / n)
        pts = [(xx + math.sin(t * 6 + j * 0.8 + k) * amp, y - j * 16) for j in range(8)]
        cv.line(pts, col, 4)


def jail_bars(cv, drop=1.0, n=7, col=(80, 84, 96), y_top=-20, y_bot=740):
    """Foreground cell bars (screen space) sliding down from the top; drop 0..1."""
    if drop <= 0:
        return
    off = (1 - drop) * -(y_bot - y_top)
    for k in range(n):
        x = 1280 * (k + 0.5) / n
        cv.rect(x - 14, y_top + off, x + 14, y_bot + off, fill=col, ow=4)
        cv.rect(x - 6, y_top + off, x - 1, y_bot + off, fill=lerp_color(col, P.WHITE, 0.3), outline=None)
    cv.rect(-20, 80 + off, 1300, 110 + off, fill=col, ow=4)
    cv.rect(-20, 600 + off, 1300, 630 + off, fill=col, ow=4)


def dark_variant(name, dark=(26, 28, 44)):
    """colors= dict that turns a character into a silhouette with glowing eyes."""
    d = dict(shirt=dark, pants=dark, skin=dark, hair_color=dark, shoes=dark, skirt=dark, cheeks=False,
             bandaid=False, bow_color=dark, stripes=False)
    return d


def pop_scale(t, start, dur=0.3, s=2.2):
    return ease_out_back(progress(t, start, dur), s) if t >= start else 0.0


def from_screen(cv, pt):
    """Inverse of cv.to_screen under the current transform: draw_character anchors -> local coords."""
    a, b, c, d, e, f = cv.m
    det = a * e - b * d
    X, Y = pt[0] - c, pt[1] - f
    return ((e * X - b * Y) / det, (-d * X + a * Y) / det)
