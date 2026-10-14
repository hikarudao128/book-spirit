#!/usr/bin/env python3
"""Composed thumbnail -> out/thumbnail.png (1280x720): the four kids in the alley + the title."""
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

from lib import palette as P  # noqa: E402
from lib.backgrounds import draw_alley, draw_sky  # noqa: E402
from lib.characters import draw_character  # noqa: E402
from lib.core import Canvas, INK  # noqa: E402
from lib.text import label  # noqa: E402
from lib.fx import vignette  # noqa: E402


def main():
    cv = Canvas(P.SKY_TOP, ss=2)
    draw_sky(cv, 0.0, sun=(1130, 110))
    with cv.camera(640, 330, 1.0):
        draw_alley(cv, 0.0, seed=3)
    cv.overlay((255, 244, 214), 0.18)
    # title band
    cv.rect(-20, 36, 1300, 214, fill=(255, 250, 238), outline=INK, ow=5, radius=0)
    cv.text(640, 98, "GIVE ME A TICKET", 74, P.ACCENT, "black")
    cv.text(640, 170, "TO CHILDHOOD", 74, INK, "black")
    label(cv, 1110, 232, "BOOK REVIEW", 26, fill=P.WHITE, bg=P.ACCENT2, rot=4)
    # the crew, big
    kids = [("HAI", "smug", "hands_hip"), ("MUI", "bored", "hands_hip"), ("TUN", "happy", "wave"),
            ("TI", "happy", "arms_up")]
    for i, (k, ex, pose) in enumerate(kids):
        draw_character(cv, k, 230 + i * 270, 712, 1.8, expression=ex, pose=pose, blink=0.0,
                       mouth_open=0.55 if k in ("TI", "TUN") else 0.0, look=(0.2 if i < 2 else -0.2, 0))
    label(cv, 170, 234, "NGUYỄN NHẬT ÁNH", 24, fill=INK, bg=P.HIGHLIGHT, rot=-4)
    img = vignette(cv.finish(), 0.25)
    os.makedirs(os.path.join(ROOT, "out"), exist_ok=True)
    out = os.path.join(ROOT, "out", "thumbnail.png")
    img.save(out)
    print(out, img.size)


if __name__ == "__main__":
    main()
