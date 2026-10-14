"""Scene 4 - Idea #1: New Names for Everything (plan, then obstacle).

Beats (all from ctx):
  "Idea number one."   IDEA NUMBER ONE / NEW NAMES FOR EVERYTHING card swings in
  "Who decided that a dog is called a "dog"? Adults."  dog with an official DOG sign, a big "?",
                        then a giant adult in a tie leans in and the sign gets an OFFICIAL stamp
  "So the kids invent their own words."  HQ whiteboard; Mui with a pointer like a general, the crew
                        on plastic stools
  each renaming line writes a visual equation on the board as it is said:
      notebook = "HAT" (Mui's notebook pops onto his head) / dog = "BANANA" / Tun: "Okay!" (arms up)
      / feet = "MOUTH"
  "It's a brilliant plan." sparkles, proud faces / "Just one problem:" record scratch, smiles drop /
  "nobody told the adults." red stamp ADULTS: NOT INFORMED
  dinner: Mom, hands on hips: "...wash your feet" -> Mui's dictionary card pops: FEET = MOUTH;
          Mui horrified; FOOT WATER basin; Mom "What?" -> "?" ; "the banana ate my hat" -> "??" "???"
  cut: the dog sits by a chewed notebook, wagging, labels BANANA / HAT; final narrator line over it.
"""
import math

from lib import palette as P
from lib.backgrounds import draw_dining_room, draw_dinner_table, draw_plastic_stool
from lib.characters import draw_character, draw_dog
from lib.core import INK, clamp, ease_in_out, ease_out, lerp, pop, progress
from lib.extra_s2_4 import (chewed_notebook, draw_basin, icon_banana, icon_dog, icon_foot, icon_hat, icon_mouth,
                            icon_notebook, sparkle, stamp, sweat, from_screen)
from lib.fx import flash
from lib.text import idea_card, label

KIDS = [("HAI", 220), ("TUN", 425), ("TI", 630)]


def beats(ctx):
    l1, l2, hat, ban, ok, mouth, plan, mom, wash, what, banana, end = (ctx.line(i) for i in range(12))
    b = dict(
        card=l1.start - 0.1, who=ctx.find_word(l1.id, "Who"), dog_word=ctx.find_word(l1.id, "dog"),
        adults=ctx.find_word(l1.id, "Adults"),
        board_cut=l2.start - 0.15,
        hat_line=hat, nb=ctx.find_word(hat.id, "notebook"), hat=ctx.find_word(hat.id, "hat"),
        ban_line=ban, dog=ctx.find_word(ban.id, "dog"), banana=ctx.find_word(ban.id, "banana"),
        ok=ok, mouth_line=mouth, feet=ctx.find_word(mouth.id, "feet"), mouth=ctx.find_word(mouth.id, "mouth"),
        plan=plan, brilliant=ctx.find_word(plan.id, "brilliant"), problem=ctx.find_word(plan.id, "Just"),
        nobody=ctx.find_word(plan.id, "nobody"), adults2=ctx.find_word(plan.id, "adults"),
        dinner_cut=plan.end + 0.25,
        mom=mom, mom_feet=ctx.find_word(mom.id, "feet"),
        wash=wash, foot=ctx.find_word(wash.id, "foot"),
        what=what, ban2=banana, ban2_word=ctx.find_word(banana.id, "banana"), hat2=ctx.find_word(banana.id, "hat"),
        dog_cut=banana.end + 0.35, end=end,
    )
    return b


def audio_cues(ctx):
    b = beats(ctx)
    return [
        {"sfx": "whoosh", "start": b["card"], "gain": 0.3},
        {"sfx": "thud", "start": b["card"] + 0.35, "gain": 0.3},
        {"sfx": "pop", "start": b["who"], "gain": 0.25},
        {"sfx": "thud", "start": b["adults"] + 0.35, "gain": 0.4},
        {"sfx": "music_bed", "start": b["board_cut"], "dur": b["problem"] - b["board_cut"], "gain": 0.12,
         "fade_out": 0.03},
        {"sfx": "pop", "start": b["nb"], "gain": 0.2},
        {"sfx": "pop", "start": b["hat"], "gain": 0.3},
        {"sfx": "boing", "start": b["hat"] + 0.1, "gain": 0.25},
        {"sfx": "pop", "start": b["dog"], "gain": 0.2},
        {"sfx": "pop", "start": b["banana"], "gain": 0.3},
        {"sfx": "pop", "start": b["feet"], "gain": 0.2},
        {"sfx": "pop", "start": b["mouth"], "gain": 0.3},
        {"sfx": "ding", "start": b["brilliant"], "gain": 0.25},
        {"sfx": "record_scratch", "start": b["problem"] - 0.05, "gain": 0.35},
        {"sfx": "thud", "start": b["adults2"] + 0.1, "gain": 0.45},
        {"sfx": "pop", "start": b["mom_feet"] + 0.25, "gain": 0.25},
        {"sfx": "pop", "start": b["foot"], "gain": 0.25},
        {"sfx": "boing", "start": b["what"].start, "gain": 0.25},
        {"sfx": "pop", "start": b["ban2_word"], "gain": 0.2},
        {"sfx": "pop", "start": b["hat2"], "gain": 0.2},
        {"sfx": "whoosh", "start": b["dog_cut"] - 0.05, "gain": 0.2},
        {"sfx": "pop", "start": b["dog_cut"] + 0.5, "gain": 0.25},
        {"sfx": "pop", "start": b["dog_cut"] + 0.9, "gain": 0.25},
    ]


# ------------------------------------------------------------------ shots
def shot_card(t, ctx, b, cv):
    cv.rect(-10, -10, 1290, 730, fill=P.CARD_BG, outline=None)
    for k in range(-6, 20):
        x = k * 110 + (t * 20) % 110
        cv.poly([(x, -10), (x + 50, -10), (x - 250, 730), (x - 300, 730)], fill=(250, 238, 210), outline=None)
    idea_card(cv, t, b["card"], "IDEA NUMBER ONE", "NEW NAMES FOR EVERYTHING", y=350)


def shot_dog(t, ctx, b, cv):
    cv.rect(-10, -10, 1290, 520, fill=P.HOUSE_COLORS[4], outline=None)
    cv.rect(-10, 520, 1290, 730, fill=P.GROUND, outline=None)
    cv.line([(-10, 520), (1290, 520)], (70, 60, 66), 3)
    draw_dog(cv, 470, 640, 2.4, pose="sit", t=t)
    # the official DOG sign
    s = pop(t, b["dog_word"] - 0.2, 0.3)
    if s > 0:
        with cv.at(470, 190, s):
            cv.limb([(0, 60), (0, 200)], 10, P.WOOD)
            cv.rect(-130, -60, 130, 60, fill=P.WHITE, ow=4, radius=8)
            cv.text(0, 2, "DOG", 72, INK, "black")
    q = pop(t, b["who"], 0.3) * (1 - progress(t, b["adults"], 0.15))
    if q > 0:
        with cv.at(780, 230, q, rot=10):
            cv.text(0, 0, "?", 220, P.ACCENT, "black", stroke=6, stroke_fill=INK)
    # a giant adult leans in from the right
    a = ease_out(progress(t, b["adults"] - 0.1, 0.35))
    if a > 0:
        draw_character(cv, "DAD", lerp(1500, 1060, a), 1180, 2.5, pose="point", flip=True, outfit="work",
                       expression="neutral", t=t)
    stamp(cv, 470, 290, "OFFICIAL", pop(t, b["adults"] + 0.35, 0.2), rot=-10, size=40, fill=P.WHITE)


def _board(cv, t, b):
    x0, y0, x1, y1 = 150, 34, 890, 396
    cv.rect(x0 + 8, y0 + 10, x1 + 8, y1 + 10, fill=INK, outline=None, radius=10)
    cv.rect(x0, y0, x1, y1, fill=(200, 200, 205), radius=10)
    cv.rect(x0 + 12, y0 + 12, x1 - 12, y1 - 12, fill=P.WHITE, outline=None, radius=4)
    cv.text(520, 90, "OUR NEW WORDS", 44, P.ACCENT2, "black")
    cv.line([(220, 122), (820, 122)], P.ACCENT2, 4)
    rows = [(icon_notebook, b["nb"], "“HAT”", b["hat"], icon_hat),
            (icon_dog, b["dog"], "“BANANA”", b["banana"], icon_banana),
            (icon_foot, b["feet"], "“MOUTH”", b["mouth"], icon_mouth)]
    for i, (ic, t1, word, t2, ic2) in enumerate(rows):
        y = 180 + i * 80
        s1 = pop(t, t1 - 0.05, 0.3)
        if s1 > 0:
            ic(cv, 270, y, 0.75 * s1)
        s2 = pop(t, t2 - 0.05, 0.3)
        if s2 > 0:
            cv.text(370, y, "=", 60 * s2, INK, "black")
            cv.text(560, y + 2, word, 52 * s2, P.ACCENT, "black")
            ic2(cv, 790, y, 0.65 * s2)
    stamp(cv, 520, 260, "ADULTS: NOT INFORMED", pop(t, b["adults2"] + 0.1, 0.2), rot=-6, size=52,
          fill=P.WHITE)


def shot_board(t, ctx, b, cv):
    cv.rect(-10, -10, 1290, 560, fill=P.HOUSE_COLORS[0], outline=None)
    cv.rect(-10, 560, 1290, 730, fill=P.GROUND, outline=None)
    cv.line([(-10, 560), (1290, 560)], (70, 60, 66), 3)
    _board(cv, t, b)
    proud = b["brilliant"] - 0.1 <= t < b["problem"]
    after = t >= b["problem"]
    for i, (nm, x) in enumerate(KIDS):
        draw_plastic_stool(cv, x, 712, color=[P.PLASTIC_RED, P.PLASTIC_BLUE, P.PLASTIC_RED][i], scale=1.5)
        speaking = ctx.speaking(nm, t)
        pose, jump, expr, look = "sit", 0, None, (0.4, -0.5)
        if speaking:
            pose, look = "sit_point_up", (0, 0)
        if nm == "TUN" and b["ok"].start - 0.1 <= t < b["ok"].end + 0.4:
            pose, expr = "sit_arms_up", "happy"
            jump = -abs(math.sin((t - b["ok"].start) * 9)) * 30
        if proud:
            expr, look = "proud", (0, 0)
        if after:
            expr, look = ("neutral" if t < b["adults2"] else ("scared" if nm == "TUN" else "deadpan")), (0, 0)
        draw_character(cv, nm, x, 620 + jump, 1.6, pose=pose, expression=expr, t=t + i * 0.5, look=look,
                       mouth_open=ctx.mouth(nm, t), nod=math.sin(t * 20) * 4 if nm == "TUN" and pose == "sit_arms_up" else 0)
    props = ("pointer",) + (("notebook_hat",) if t >= b["hat"] else ())
    expr = "proud" if proud else ("deadpan" if after else "smug")
    look = (-0.6, -0.3) if not after else (0, 0)
    hs = pop(t, b["hat"], 0.3)
    # pointer tip lands on the board rows (hand ~(882, 494), tip ~(618, 340))
    draw_character(cv, "MUI", 1010, 712, 2.2 * (1 + 0.04 * (hs - 1 if hs < 1 else 0)), pose="point",
                   props=props, flip=True, expression=expr, t=t, look=look, mouth_open=ctx.mouth("MUI", t))
    if proud:
        for k, (x, y) in enumerate(((170, 70), (880, 90), (860, 440), (140, 420), (1150, 300))):
            sparkle(cv, x, y, pop(t, b["brilliant"] + k * 0.08, 0.3) * (1 + 0.2 * math.sin(t * 9 + k)) * 1.3)


def shot_dinner(t, ctx, b, cv):
    with cv.camera(600, 430, 1.22):
        _dinner(t, ctx, b, cv)


def _dinner(t, ctx, b, cv):
    draw_dining_room(cv, t, night=True)
    draw_dinner_table(cv, 1090, 560, w=400)
    # Mom
    mom_expr = "angry"
    if t >= b["what"].start - 0.1:
        mom_expr = "shocked"
    ma = draw_character(cv, "MOM", 320, 740, 1.3, pose="hands_hip", expression=mom_expr, t=t,
                        mouth_open=ctx.mouth("MOM", t), look=(0.6, 0.2))
    # Mui
    horrified = b["wash"].start - 0.15 <= t < b["ban2"].start - 0.1
    expr = "scared" if horrified else ("deadpan" if t >= b["ban2"].start - 0.1 else "bored")
    lean = -8 if horrified else 0
    look = (-0.6, -0.4) if t < b["ban2"].start else (-0.5, -0.4)
    a = draw_character(cv, "MUI", 800, 712, 1.6, pose="cover_head" if horrified and t < b["foot"] else "stand",
                       expression=expr, t=t, mouth_open=ctx.mouth("MUI", t), look=look, lean=lean)
    if horrified:
        hx, hy = from_screen(cv, a["head"])
        hr = a["head_r"] / 1.22
        sweat(cv, hx + hr * 0.95, hy - hr * 0.3, 1.2, t, 1.0)
        sweat(cv, hx - hr * 0.9, hy - hr * 0.1, 1.0, t, 1.3, 2)
    # Mui's dictionary card: FEET = MOUTH
    s = pop(t, b["mom_feet"] + 0.25, 0.3) * (1 - progress(t, b["what"].start, 0.2))
    if s > 0.01:
        with cv.at(920, 220, s, rot=4):
            cv.rect(-150, -70, 150, 70, fill=P.PAPER, ow=4, radius=10)
            cv.text(0, -48, "MUI'S DICTIONARY", 18, P.ACCENT2, "black")
            icon_foot(cv, -80, 14, 0.8)
            cv.text(0, 12, "=", 56, INK, "black")
            icon_mouth(cv, 80, 18, 0.8)
    bs = pop(t, b["foot"], 0.3)
    if bs > 0:
        draw_basin(cv, 590, 650, 1.0 * bs, stink=True, t=t)
    # Mom's growing confusion
    hx, hy = from_screen(cv, ma["top"])
    marks = [b["what"].start, b["ban2_word"], b["hat2"]]
    for k, m in enumerate(marks):
        q = pop(t, m, 0.3)
        if q > 0:
            with cv.at(hx + 120 + k * 58, hy + 70 - k * 8, q, rot=-10 + k * 10):
                cv.text(0, 0, "?", 90, P.ACCENT, "black", stroke=4, stroke_fill=INK)


def shot_final(t, ctx, b, cv):
    cv.rect(-10, -10, 1290, 400, fill=(244, 214, 170), outline=None)
    cv.rect(-10, 400, 1290, 730, fill=P.FLOOR_TILE, outline=None)
    cv.line([(-10, 400), (1290, 400)], (70, 60, 66), 3)
    for k in range(-2, 18):
        cv.line([(k * 100 + 40, 400), (k * 160 - 360, 730)], (190, 168, 140), 2)
    u = t - b["dog_cut"]
    z = 1 + 0.04 * ease_in_out(clamp(u / 4))
    with cv.at(640, 400, z):
        with cv.at(-640, -400):
            chewed_notebook(cv, 860, 610, 2.0)
            draw_dog(cv, 420, 680, 3.0, pose="sit", t=t, mouth_prop="notebook")
    s1 = pop(t, b["dog_cut"] + 0.5, 0.3)
    s2 = pop(t, b["dog_cut"] + 0.9, 0.3)
    if s1 > 0:
        label(cv, 250, 170, "BANANA", 48, bg=P.HIGHLIGHT, scale=s1, rot=-6)
        cv.line([(300, 215), (390, 330)], INK, 6 * s1)
    if s2 > 0:
        label(cv, 1060, 400, "HAT", 48, bg=P.HIGHLIGHT, scale=s2, rot=5)
        cv.line([(1030, 445), (950, 535)], INK, 6 * s2)


def render_frame(t, ctx):
    b = beats(ctx)
    cv = ctx.canvas(P.CARD_BG)
    if t < b["who"] - 0.1:
        shot_card(t, ctx, b, cv)
    elif t < b["board_cut"]:
        shot_dog(t, ctx, b, cv)
    elif t < b["dinner_cut"]:
        shot_board(t, ctx, b, cv)
    elif t < b["dog_cut"]:
        shot_dinner(t, ctx, b, cv)
    else:
        shot_final(t, ctx, b, cv)
    img = cv.finish()
    for cut in (b["who"] - 0.1, b["dinner_cut"], b["dog_cut"]):
        f = 1 - progress(t, cut, 0.12)
        if t >= cut and f > 0:
            img = flash(img, 0.3 * f)
    return img
