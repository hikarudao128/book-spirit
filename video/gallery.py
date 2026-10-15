#!/usr/bin/env python3
"""Dump reference sheets of every character, background and prop to build/stills/gallery_*.png.
    python3 video/gallery.py
Scene authors: look at these before building a scene."""
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

from lib import palette as P  # noqa: E402
from lib.backgrounds import (draw_book_cover, draw_classroom, draw_courtroom, draw_curtain, draw_desks,  # noqa
                             draw_dining_room, draw_dinner_table, draw_gavel, draw_kitchen, draw_plastic_stool)
from lib.characters import draw_character, draw_dog, draw_vendor  # noqa: E402
from lib.core import Canvas  # noqa: E402
from lib.text import board, caption, idea_card, label, name_tag, speech_bubble  # noqa: E402

OUT = os.path.join(ROOT, "build", "stills")


def save(cv, name):
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, f"gallery_{name}.png")
    cv.finish().save(p)
    print(p)


def main():
    cv = Canvas(bg=(236, 228, 210))
    cv.rect(-10, 620, 1300, 730, fill=P.GROUND, outline=None)
    for x, n in zip([70, 190, 300, 410, 520, 660, 830, 1010, 1180],
                    ["MUI", "HAI", "TUN", "TI", "HIS_KID", "MOM", "DAD", "TEACHER", "OLD_MUI"]):
        a = draw_character(cv, n, x, 640, 0.85 if n in ("MOM", "DAD", "TEACHER", "OLD_MUI") else 1.0, t=0.5,
                           props=("phone",) if n == "HIS_KID" else ())
        label(cv, x, 690, n, 16)
    draw_dog(cv, 600, 715, 0.6, t=0.3)
    save(cv, "characters")

    cv = Canvas(bg=(236, 228, 210))
    ex = ["neutral", "bored", "happy", "shocked", "angry", "sad", "smug", "deadpan", "scared", "proud"]
    for i, e in enumerate(ex):
        x = 70 + i * 126
        draw_character(cv, "MUI", x, 300, 1.0, expression=e, t=0.5)
        draw_character(cv, "TUN", x, 620, 1.0, expression=e, t=0.5, mouth_open=0.6 if i % 2 else 0)
        label(cv, x, 680, e, 15)
    save(cv, "expressions")

    cv = Canvas(bg=(236, 228, 210))
    poses = ["stand", "wave", "point", "point_up", "hands_hip", "arms_up", "shrug", "hold_both", "present",
             "cover_head", "salute", "facepalm", "fist_up", "walk", "run", "sit", "sit_chin_on_hand"]
    for i, ps in enumerate(poses):
        x = 70 + (i % 9) * 140
        y = 300 if i < 9 else 640
        draw_character(cv, "HAI" if i % 2 else "MUI", x, y - (40 if ps.startswith("sit") else 0), 0.9, pose=ps,
                       t=0.3)
        label(cv, x, y + 30, ps, 14)
    save(cv, "poses")

    cv = Canvas(bg=(236, 228, 210))
    outfits = [("HAI", "police", ()), ("TUN", "flight", ()), ("MUI", "principal", ()), ("TI", "snow_white", ()),
               ("MUI", "dad_role", ()), ("MUI", "uniform", ()), ("HAI", None, ("wig", "gavel")),
               ("TEACHER", None, ("pointer",)), ("MOM", None, ("stick",)), ("OLD_MUI", "work", ())]
    for i, (n, o, pr) in enumerate(outfits):
        x = 70 + i * 126
        adult = n in ("TEACHER", "MOM", "OLD_MUI")
        draw_character(cv, n, x, 640, 0.6 if adult else 1.0, outfit=o, props=pr, t=0.3,
                       pose="hands_hip" if n == "MOM" else "stand")
        label(cv, x, 680, o or "+".join(pr), 14)
    draw_vendor(cv, 640, 330, 0.55, t=0.2)
    draw_dog(cv, 120, 330, 0.8, pose="sit", t=0.2)
    draw_dog(cv, 300, 330, 0.8, pose="run", t=0.2)
    draw_dog(cv, 1050, 330, 0.8, pose="stand", t=0.2, mouth_prop="notebook", flip=True)
    save(cv, "outfits_props")

    for name, fn in (("classroom", lambda c: (draw_classroom(c, 1.0, ["REPEAT AFTER ME:", "2 x 2 = 4"],
                                                             "LESSON"), draw_desks(c, 600))),
                     ("dining", lambda c: (draw_dining_room(c), draw_dinner_table(c, 640, 520))),
                     ("courtroom", lambda c: (draw_courtroom(c), draw_gavel(c, 700, 360, -20))),
                     ("kitchen", lambda c: draw_kitchen(c)),
                     ("curtain", lambda c: draw_curtain(c, 0.35, 0.0))):
        cv = Canvas(bg=(255, 255, 255))
        fn(cv)
        save(cv, name)

    cv = Canvas(bg=P.CARD_BG)
    idea_card(cv, 1, 0, "IDEA NUMBER ONE", "NEW NAMES FOR EVERYTHING", y=200, w=760, h=260)
    board(cv, 1020, 520, 400, 300, "GOOD STUFF", ["+ Short", "+ Funny", "+ Child's voice"], style="whiteboard")
    draw_book_cover(cv, 220, 470, 260, 380, rot=-4)
    speech_bubble(cv, 620, 470, "From now on, a notebook is a hat.", tail=(-80, 90))
    name_tag(cv, 1, 0, "HAI", "FAST. SNEAKY. NEVER SORRY.", x=430, y=640)
    save(cv, "text_and_cards")


if __name__ == "__main__":
    main()
