"""Placeholder frame used by unimplemented scene stubs."""
from . import palette as P
from .core import INK
from .text import wrapped


def placeholder_frame(t, ctx, title="", note=""):
    cv = ctx.canvas(P.CARD_BG)
    cv.rect(140, 160, 1140, 560, fill=P.WHITE, radius=24, ow=5)
    cv.text(640, 270, f"Scene {ctx.scene}", 84, P.ACCENT, "black")
    if title:
        wrapped(cv, 640, 380, title, 40, 900, INK, "bold")
    cur = ctx.current(t)
    if cur:
        wrapped(cv, 640, 490, f"{cur.speaker}: {cur.text}", 24, 940, (90, 90, 96), "medium")
    cv.rect(140, 600, 140 + 1000 * min(1, t / ctx.duration), 616, fill=P.ACCENT, outline=None, radius=8)
    return cv.finish()
