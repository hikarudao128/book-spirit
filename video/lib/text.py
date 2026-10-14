"""Fonts and text-based graphics: title cards, boards, labels, name tags, bubbles.

Fonts: Inter (supports Vietnamese diacritics). weights: regular, medium, semibold,
bold, extrabold, black. All sizes are logical px (scaled by the canvas transform).
"""
import functools
import math

from PIL import ImageFont

from . import palette as P
from .core import INK, OW, clamp, ease_out_back, ease_out, progress

FONT_DIR = "/usr/share/fonts/opentype/inter/"
_WEIGHTS = {
    "regular": "Inter-Regular.otf", "medium": "Inter-Medium.otf", "semibold": "Inter-SemiBold.otf",
    "bold": "Inter-Bold.otf", "extrabold": "Inter-ExtraBold.otf", "black": "Inter-Black.otf",
    "italic": "Inter-Italic.otf", "bolditalic": "Inter-BoldItalic.otf",
}


@functools.lru_cache(maxsize=256)
def font(px, weight="bold"):
    """Pillow font at an absolute pixel size (device px)."""
    return ImageFont.truetype(FONT_DIR + _WEIGHTS.get(weight, _WEIGHTS["bold"]), px)


def text_width(s, size, weight="bold"):
    """Width in logical px of a single line at logical size."""
    f = font(max(1, int(size * 4)), weight)   # measure at 4x for precision
    return f.getlength(s) / 4.0


def wrap_text(s, size, max_w, weight="bold"):
    """Greedy word wrap -> list of lines that fit max_w logical px."""
    words, lines, cur = s.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if text_width(trial, size, weight) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_size(s, max_w, size, weight="bold", min_size=10):
    while size > min_size and text_width(s, size, weight) > max_w:
        size -= 1
    return size


def wrapped(cv, x, y, s, size, max_w, fill=INK, weight="bold", line_h=1.18, anchor="mm"):
    """Draw wrapped, centred text block whose centre is (x,y)."""
    lines = wrap_text(s, size, max_w, weight)
    total = len(lines) * size * line_h
    y0 = y - total / 2 + size * line_h / 2
    for i, ln in enumerate(lines):
        cv.text(x, y0 + i * size * line_h, ln, size, fill, weight, anchor=anchor)
    return len(lines)


def label(cv, x, y, s, size=26, fill=INK, bg=P.WHITE, pad=(16, 8), weight="extrabold", radius=12,
          outline=INK, ow=OW, scale=1.0, rot=0.0):
    """Pill/box label centred at (x,y). scale lets you pop it in (use core.pop)."""
    if scale <= 0.01:
        return
    w = text_width(s, size, weight) + 2 * pad[0]
    h = size * 1.15 + 2 * pad[1]
    with cv.at(x, y, scale, rot=rot):
        cv.rect(-w / 2 + 4, -h / 2 + 5, w / 2 + 4, h / 2 + 5, fill=INK, outline=None, radius=radius)  # drop shadow
        cv.rect(-w / 2, -h / 2, w / 2, h / 2, fill=bg, outline=outline, ow=ow, radius=radius)
        cv.text(0, 1, s, size, fill, weight)


def board(cv, x, y, w, h, title="", lines=(), style="whiteboard", title_size=40, line_size=30,
          scale=1.0, rot=0.0, reveal=1.0):
    """A sign / board centred at (x,y).
    style: 'whiteboard' | 'chalk' | 'cardboard' | 'paper'.
    reveal: 0..1 fraction of `lines` shown (for bullet-by-bullet builds)."""
    if scale <= 0.01:
        return
    styles = {
        "whiteboard": (P.WHITE, (200, 200, 205), INK, P.ACCENT),
        "chalk": (P.CHALKBOARD, P.WOOD, P.CHALK, P.HIGHLIGHT),
        "cardboard": ((214, 170, 112), (184, 140, 86), INK, P.ACCENT),
        "paper": (P.PAPER, (230, 220, 196), INK, P.ACCENT),
    }
    bg, frame, ink, accent = styles[style]
    with cv.at(x, y, scale, rot=rot):
        cv.rect(-w / 2 + 6, -h / 2 + 8, w / 2 + 6, h / 2 + 8, fill=INK, outline=None, radius=10)
        cv.rect(-w / 2, -h / 2, w / 2, h / 2, fill=frame, radius=10)
        cv.rect(-w / 2 + 12, -h / 2 + 12, w / 2 - 12, h / 2 - 12, fill=bg, outline=None, radius=4)
        ty = -h / 2 + 22
        if title:
            tl = wrap_text(title, title_size, w - 70, "black")
            for i, ln in enumerate(tl):
                cv.text(0, ty + title_size * 0.65 + i * title_size * 1.1, ln, title_size, accent, "black")
            ty += len(tl) * title_size * 1.1 + 18
            cv.line([(-w / 2 + 40, ty), (w / 2 - 40, ty)], ink, 3)
            ty += 16
        n = int(math.floor(len(lines) * clamp(reveal) + 1e-6))
        for i, ln in enumerate(lines[:n]):
            cv.text(-w / 2 + 44, ty + line_size * 0.7 + i * line_size * 1.45, ln, line_size, ink, "bold",
                    anchor="lm")


def idea_card(cv, t, start, kicker, title, x=640, y=330, w=900, h=300, style="chalk"):
    """'IDEA NUMBER ONE' style title board that swings in at `start`.
    kicker = small top line ('IDEA NUMBER ONE'), title = big text."""
    p = progress(t, start, 0.6)
    if p <= 0:
        return
    s = ease_out_back(p, 1.6)
    rot = (1 - ease_out(p)) * -8
    styles = {"chalk": (P.CHALKBOARD, P.CHALK, P.HIGHLIGHT), "paper": (P.PAPER, INK, P.ACCENT)}
    bg, ink, accent = styles.get(style, styles["chalk"])
    with cv.at(x, y, s, rot=rot):
        cv.rect(-w / 2 + 8, -h / 2 + 10, w / 2 + 8, h / 2 + 10, fill=INK, outline=None, radius=14)
        cv.rect(-w / 2, -h / 2, w / 2, h / 2, fill=P.WOOD, radius=14)
        cv.rect(-w / 2 + 18, -h / 2 + 18, w / 2 - 18, h / 2 - 18, fill=bg, outline=None, radius=6)
        cv.text(0, -h / 2 + 62, kicker, 34, accent, "black")
        size = 64
        lines = wrap_text(title, size, w - 100, "black")
        while len(lines) > 2 and size > 30:
            size -= 4
            lines = wrap_text(title, size, w - 100, "black")
        y0 = 30 - (len(lines) - 1) * size * 0.55
        for i, ln in enumerate(lines):
            cv.text(0, y0 + i * size * 1.1, ln, size, ink, "black")


def name_tag(cv, t, start, name, subtitle="", x=80, y=560, color=P.ACCENT, dur=None):
    """Freeze-frame character intro: a slanted colour band slides in from the left
    with a big NAME and a small subtitle. Left edge at x, baseline area around y.
    dur=None keeps it on screen; otherwise it slides out after dur seconds."""
    p = progress(t, start, 0.35)
    if p <= 0:
        return
    out = progress(t, start + dur, 0.3) if dur else 0.0
    off = (1 - ease_out(p)) * -700 + ease_out(out) * -900
    name_size, sub_size = 64, 26
    w = max(text_width(name, name_size, "black"), text_width(subtitle, sub_size, "bold")) + 90
    with cv.at(x + off, y, 1.0):
        band = [(-30, -52), (w, -52), (w - 36, 62), (-30, 62)]
        cv.poly([(px + 7, py + 8) for px, py in band], fill=INK, outline=None)
        cv.poly(band, fill=color)
        cv.text(26, -8, name, name_size, P.WHITE, "black", anchor="lm", stroke=3, stroke_fill=INK)
        if subtitle:
            cv.rect(20, 32, 20 + text_width(subtitle, sub_size, "bold") + 24, 32 + sub_size + 10,
                    fill=P.WHITE, radius=4, ow=2.5)
            cv.text(32, 32 + (sub_size + 10) / 2 + 1, subtitle, sub_size, INK, "bold", anchor="lm")


def speech_bubble(cv, x, y, s, tail=(0, 60), size=28, max_w=360, fill=P.WHITE, scale=1.0, weight="bold"):
    """Rounded speech bubble centred at (x,y); tail = offset of the tail tip from centre."""
    if scale <= 0.01:
        return
    lines = wrap_text(s, size, max_w, weight)
    w = max(text_width(l, size, weight) for l in lines) + 44
    h = len(lines) * size * 1.2 + 28
    with cv.at(x, y, scale):
        tx, ty = tail
        bx = max(-w / 2 + 20, min(w / 2 - 50, tx * 0.4))
        cv.poly([(bx, h / 2 - 6), (bx + 30, h / 2 - 6), (tx, ty)], fill=fill)
        cv.rect(-w / 2, -h / 2, w / 2, h / 2, fill=fill, radius=min(26, h / 2))
        cv.poly([(bx + 3, h / 2 - 8), (bx + 27, h / 2 - 8), (bx + 12, h / 2 + 6)], fill=fill, outline=None)
        for i, ln in enumerate(lines):
            cv.text(0, -h / 2 + 14 + size * 0.6 + i * size * 1.2, ln, size, INK, weight)


def caption(cv, s, y=660, size=30, alpha_bg=True):
    """Bottom caption strip (screen space) - e.g. for on-screen jokes / dates."""
    w = text_width(s, size, "bold") + 40
    cv.rect(640 - w / 2, y - size * 0.8, 640 + w / 2, y + size * 0.8, fill=INK, outline=None, radius=8)
    cv.text(640, y + 1, s, size, P.WHITE, "bold")
