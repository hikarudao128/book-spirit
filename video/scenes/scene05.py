"""Scene 5 - Idea #2: Be the Adults.

Beats (all derived from ctx):
  "Idea number two..."          swinging idea card over a turning sunburst
  "Everyone picks a job."       cut to a little stage: the four kids line up, then dash behind the curtain
  Hai / Tun / Mui / Ti          one by one the curtain parts and a kid pops out in costume under a spotlight,
                                says the job, then slides to a slot in the line-up (police salute,
                                flight-safety arms, principal with pointer, Snow White princess wave)
  "That's not a job."           Hai points, deadpan; a red NOT A JOB sticker slaps onto Ti
  "It is now."                  Ti smug; the NOT falls off, the sticker turns gold, crown twinkles
  "They also play house..."     whoosh cut to a living room: DAD (Mui, notebook hat), MOM (Ti), CHILD (Tun)
                                doing homework at a little table; HOUSE RULES sign builds on "rules"
  "What are you doing?!"        camera pushes to Ti, hands on hips
  "...My homework?"             push to Tun, small shrug
  "In THIS house? Go outside…"  Mui points at the open door; Tun bolts out happily in the tail
"""
import math

from lib import palette as P
from lib.backgrounds import draw_curtain, draw_dining_room, draw_plastic_stool
from lib.characters import draw_character
from lib.core import INK, clamp, ease_in, ease_in_out, ease_out, ease_out_back, lerp, pop, progress
from lib.extra_s5_7 import (cam_keys, draw_door, draw_low_table, draw_open_notebook, draw_pencil, sparkle,
                            spotlight, stage_floor, title_backdrop, to_world)
from lib.fx import flash
from lib.text import board, idea_card, label

GROUND = 668            # stage: kids' feet
KS = 1.3                # kid scale on stage
SLOTS = {"HAI": 315, "TUN": 478, "MUI": 802, "TI": 640}      # final line-up (Ti keeps the centre spot)
PLAIN = {"HAI": 330, "TUN": 530, "MUI": 750, "TI": 950}     # plain-clothes line-up before the dash
STAGE_CAM = (640, 480, 1.4)
ORDER = ["HAI", "TUN", "MUI", "TI"]
COSTUME = {
    "HAI": dict(outfit="police", pose="salute", expression="proud", props=()),
    "TUN": dict(outfit="flight", pose="present", expression="happy", props=()),
    "MUI": dict(outfit="principal", pose="hold", expression="deadpan", props=("pointer",)),
    "TI": dict(outfit="snow_white", pose="wave", expression="happy", props=("crown",), variant={"bow": False}),
}
SLIDE = 0.36            # seconds to walk from the centre to the line-up slot
JOB = {"HAI": "CHIEF OF POLICE", "TUN": "FLIGHT ATTENDANT", "MUI": "SCHOOL PRINCIPAL", "TI": "SNOW WHITE"}

# house set
HFLOOR = 640
DOOR_X = 1085
TI_X, MUI_X, TUN_X = 345, 545, 830
WALL = (244, 214, 170)
SIGN_X, SIGN_Y = 700, 296   # HOUSE RULES sign (top ~221, bottom ~371: clear of the heads, inside every house shot)


def beats(ctx):
    L = {i: ctx.line(f"s05_l{i:02d}") for i in range(1, 13)}
    b = dict(L=L)
    b["card"] = L[1].start - 0.3
    b["stage"] = L[2].start - 0.15                     # cut to the stage
    b["dash"] = ctx.find_word(L[2].id, "picks")       # kids run behind the curtain
    b["dash_end"] = L[3].start - 0.3
    spk = {"HAI": L[3], "TUN": L[4], "MUI": L[5], "TI": L[6]}
    b["out"] = {k: spk[k].start - 0.32 for k in ORDER}            # curtain parts, kid steps out
    nxt = {"HAI": "TUN", "TUN": "MUI", "MUI": "TI"}
    # move aside just before the curtain parts for the next kid, so the two never overlap at the centre
    b["slide"] = {k: b["out"][nxt[k]] - 0.3 for k in nxt}
    b["slide"]["TI"] = None
    b["notjob"] = ctx.find_word(L[7].id, "job")
    b["isnow"] = ctx.find_word(L[8].id, "now")
    b["house"] = L[9].start - 0.12
    b["roles"] = ctx.find_word(L[9].id, "house")
    b["rules"] = ctx.find_word(L[9].id, "rules")
    b["right"] = ctx.find_word(L[9].id, "right")
    b["go"] = ctx.find_word(L[12].id, "Go")
    b["this"] = ctx.find_word(L[12].id, "THIS")
    b["bolt"] = L[12].end + 0.35
    b["end"] = ctx.duration
    return b


def audio_cues(ctx):
    b = beats(ctx)
    L = b["L"]
    cues = [
        {"sfx": "music_bed", "start": 0.0, "dur": b["end"], "gain": 0.12, "fade_out": 0.8},
        {"sfx": "whoosh", "start": b["card"] + 0.05, "gain": 0.25},
        {"sfx": "whoosh", "start": b["stage"], "gain": 0.22},
        {"sfx": "whoosh", "start": b["dash"] + 0.25, "gain": 0.2},
        {"sfx": "slap", "start": b["notjob"] + 0.05, "gain": 0.25},
        {"sfx": "boing", "start": b["isnow"] + 0.15, "gain": 0.22},
        {"sfx": "ding", "start": b["isnow"] + 0.3, "gain": 0.22},
        {"sfx": "whoosh", "start": b["house"], "gain": 0.22},
        {"sfx": "pop", "start": b["roles"], "gain": 0.22},
        {"sfx": "pop", "start": b["rules"], "gain": 0.22},
        {"sfx": "whoosh", "start": b["bolt"] + 0.1, "gain": 0.25},
    ]
    for k in ORDER:
        cues.append({"sfx": "pop", "start": b["out"][k] + 0.12, "gain": 0.28})
    return cues


# ------------------------------------------------------------------ stage part
def _kid_on_stage(t, ctx, b, name):
    """-> (x, y, scale, layer, kwargs) for a kid on the stage, or None while hidden."""
    i = ORDER.index(name)
    slot = PLAIN[name]
    out = b["out"][name]
    mouth = ctx.mouth(name, t)
    if t < b["dash"] + i * 0.06:                         # in plain clothes, lined up
        look = (lerp(-0.5, 0.6, i / 3), -0.3)
        return slot, GROUND, KS, "front", dict(t=t + i, look=look, mouth_open=0,
                                               expression="happy" if name != "MUI" else "bored")
    if t < out:
        p = progress(t, b["dash"] + i * 0.06, b["dash_end"] - b["dash"] - 0.2)
        if p >= 1:
            return None
        x = lerp(slot, 640, ease_in(p))
        layer = "behind" if p > 0.82 else "front"
        sc = KS * (lerp(1.0, 0.86, ease_in(p)))
        return x, lerp(GROUND, GROUND - 40, ease_in(p)), sc, layer, dict(
            t=t * 1.3 + i, pose="run", flip=slot > 640, mouth_open=0,
            expression="happy" if name != "MUI" else "bored")
    # costume
    c = COSTUME[name]
    kw = dict(outfit=c["outfit"], props=c["props"], t=t + i, mouth_open=mouth, variant=c.get("variant"))
    slot = SLOTS[name]
    step = ease_out_back(progress(t, out, 0.36), 1.4)
    x, y, sc = 640, lerp(GROUND - 46, GROUND, step), KS * lerp(0.86, 1.0, step)
    layer = "front" if step > 0.25 else "behind"
    slide = b["slide"][name]
    pose, expr = c["pose"], c["expression"]
    if slide is not None and t >= slide:
        sp = progress(t, slide, SLIDE)
        x = lerp(640, slot, ease_in_out(sp))
        if sp < 1:
            pose = "walk"
            kw["t"] = t * 1.4 + i
    kw.update(pose=pose, expression=expr)
    # a little bounce on the reveal
    if t < out + 0.6:
        kw["look"] = (0, 0)
    # reactions
    L = b["L"]
    if name == "HAI" and t >= L[7].start - 0.1 and t < b["house"]:
        kw.update(pose="point", expression="deadpan")
    if name == "TI" and t >= L[8].start - 0.05:
        kw.update(pose="hands_hip", expression="smug", look=(-0.6, 0))
    elif name == "TI" and t >= L[7].start:
        kw.update(pose="stand", expression="neutral", look=(-0.8, 0))
    if name in ("TUN", "MUI") and t >= L[7].start and slide is not None and t >= slide + SLIDE:
        kw["look"] = (-0.6 if name == "MUI" else 0.8, 0)
    if name == "HAI" and t >= b["slide"]["HAI"] + SLIDE and t < L[7].start - 0.1:
        kw.update(pose="salute", expression="proud")    # keeps saluting, of course
    if name == "TUN" and t >= b["slide"]["TUN"] + SLIDE:
        kw["pose"] = "present"
    return x, y, sc, layer, kw


def _render_stage(t, ctx, b, cv):
    L = b["L"]
    # curtain gap: parts while someone goes in / comes out
    opens = [progress(t, b["dash"] + 0.25, 0.25) * (1 - progress(t, b["dash_end"] - 0.05, 0.2))]
    for k in ORDER:
        o = b["out"][k]
        opens.append(math.sin(math.pi * progress(t, o - 0.12, 0.55)))
    gap = 0.2 * max(opens)

    kids = {k: _kid_on_stage(t, ctx, b, k) for k in ORDER}
    cv.rect(-10, -10, 1290, 730, fill=(40, 26, 34), outline=None)        # backstage dark
    with cv.camera(*STAGE_CAM):
        for k in ORDER:
            st = kids[k]
            if st and st[3] == "behind":
                draw_character(cv, k, st[0], st[1], st[2], **st[4])
    draw_curtain(cv, gap, t)                     # screen space: the valance stays in frame
    with cv.camera(*STAGE_CAM):
        anchors = _stage_front(t, b, cv, kids)
    _sticker(t, b, cv, anchors)
    return kids, anchors


def _stage_front(t, b, cv, kids):
    stage_floor(cv, 600)
    anchors = {}
    front = sorted([k for k in ORDER if kids[k] and kids[k][3] == "front"], key=lambda k: kids[k][1])
    for k in front:
        x, y, sc, _, kw = kids[k]
        if k == "TI" and t >= b["isnow"] + 0.15:
            y -= 14 * math.sin(math.pi * progress(t, b["isnow"] + 0.15, 0.3))     # tiny smug hop
        anchors[k] = draw_character(cv, k, x, y, sc, **kw)

    # job labels, once each kid is in their slot
    for k in ORDER:
        st = kids[k]
        if not st or k not in anchors:
            continue
        sl = b["slide"][k]
        if sl is not None:
            s = pop(t, sl + SLIDE, 0.3)
            if s > 0.01 and t < b["house"]:
                label(cv, SLOTS[k], GROUND + 26, JOB[k], 14, scale=s, bg=P.WHITE, pad=(10, 5), ow=2.6)
    return anchors


def _sticker(t, b, cv, anchors):
    """NOT A JOB sticker slapped across Ti's chest (screen space); on "It is now" the NOT half
    peels off and falls, and the rest turns into a gold A JOB! badge."""
    if "TI" not in anchors or t < b["notjob"]:
        return
    from lib.text import text_width
    a = anchors["TI"]
    size = 26
    cx, cy = a["chest"][0] + 4, a["chest"][1] - 2
    s = pop(t, b["notjob"], 0.25)
    fall = progress(t, b["isnow"] + 0.1, 0.7)
    gold = fall > 0.05
    rot = -8
    w_not = text_width("NOT", size, "extrabold") + 24
    w_job = text_width("A JOB!", size, "extrabold") + 24
    total = w_not + w_job - 6
    # the two halves sit edge to edge, centred on the chest, along the sticker's tilt
    ca, sa = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    def along(d):
        return cx + d * ca, cy + d * sa
    jx, jy = along(-total / 2 + w_not - 6 + w_job / 2)
    label(cv, jx, jy, "A JOB" + ("!" if gold else ""), size, fill=INK if gold else P.WHITE,
          bg=P.HIGHLIGHT if gold else P.ACCENT, pad=(12, 6), scale=s, rot=rot)
    if fall < 1:
        nx, ny = along(-total / 2 + w_not / 2)
        fx = nx - 70 * fall
        fy = ny + 420 * fall * fall
        label(cv, fx, fy, "NOT", size, fill=P.WHITE, bg=P.ACCENT, pad=(12, 6), scale=s,
              rot=rot - 150 * fall)
    sparkle(cv, jx + w_job / 2 + 6, jy - 24, 24, t, b["isnow"] + 0.3)
    sparkle(cv, a["head"][0] + 46, a["top"][1] - 4, 20, t, b["isnow"] + 0.45)


# ------------------------------------------------------------------ house part
def _house_cam(t, b):
    L = b["L"]
    wide = (692, 434, 1.45)
    on_ti = (TI_X + 70, 532, 2.2)          # sign is fully out of this one (bottom edge above frame)
    on_tun = (TUN_X + 20, 448, 1.5)        # sign fully in frame above Tun
    on_mui = (MUI_X + 125, 446, 1.45)      # sign fully in frame; Ti stays whole at the left
    keys = [(b["house"], wide), (L[10].start + 0.1, wide), (L[10].start + 0.45, on_ti, 0.35),
            (L[11].start - 0.2, on_ti), (L[11].start + 0.2, on_tun, 0.4),
            (L[12].start - 0.1, on_tun), (L[12].start + 0.35, on_mui, 0.45),
            (b["go"], on_mui), (b["go"] + 0.5, wide, 0.5)]
    return cam_keys(t, keys)


def _render_house(t, ctx, b, cv):
    L = b["L"]
    cam = _house_cam(t, b)
    with cv.camera(*cam):
        draw_dining_room(cv, t, night=False)
        cv.rect(880, 100, 1140, 340, fill=WALL, outline=None)      # no window / calendar on this wall
        cv.rect(190, 130, 310, 270, fill=WALL, outline=None)
        draw_door(cv, DOOR_X, 560, open_amount=1.0)
        # HOUSE RULES sign on the wall
        board(cv, SIGN_X, SIGN_Y, 280, 150, "HOUSE RULES", ["1. NO HOMEWORK", "2. GET DIRTY"], style="paper",
              title_size=25, line_size=20, scale=pop(t, b["rules"] - 0.1, 0.35), rot=2,
              reveal=progress(t, b["rules"] + 0.15, 0.6))

        # Tun, the child, at a little table - bolts out the door in the tail
        bolt = progress(t, b["bolt"], 1.2)
        homework = t < L[10].start + 0.2
        if bolt <= 0:
            tun_kw = dict(pose="sit_hold", expression="happy", look=(0.1, 0.7), t=t,
                          nod=(math.sin(t * 7) * 2 if homework else 0), mouth_open=ctx.mouth("TUN", t))
            if t >= L[10].start + 0.2:
                tun_kw.update(expression="neutral", look=(-0.9, -0.1), pose="sit")
            if t >= L[11].start - 0.05:
                tun_kw.update(pose="sit_shrug", expression="neutral")
            if t >= b["go"] + 0.3:
                tun_kw.update(pose="sit", expression="shocked", look=(-0.9, -0.2))
            a_tun = draw_character(cv, "TUN", TUN_X, 560, KS, **tun_kw)
        else:
            # runs to the door, then shrinks into the doorway and is gone in a puff
            p = ease_in(clamp(bolt / 0.7))
            q = progress(bolt, 0.7, 0.18)
            x = lerp(TUN_X + 40, DOOR_X, p)
            y = lerp(640, 600, p) + lerp(0, -30, q)
            jump = -abs(math.sin(bolt * 14)) * 16
            if q < 1:
                draw_character(cv, "TUN", x, y + jump, KS * lerp(1.0, 0.75, q), pose="run",
                               expression="happy", t=t * 1.3, look=(0.8, 0))
            puff = progress(bolt, 0.8, 0.5)
            if 0 < puff < 1:
                for k in range(6):
                    a = k * 1.05 + 0.4
                    r = lerp(10, 26, puff) * (1 - puff * 0.6)
                    cv.circle(DOOR_X + math.cos(a) * 40 * puff, 540 + math.sin(a) * 26 * puff - 20, r,
                              fill=(250, 248, 240), ow=2.2)
        draw_plastic_stool(cv, TUN_X, 640, P.PLASTIC_BLUE, 1.0)
        draw_low_table(cv, TUN_X + 20, 560, w=230)
        draw_open_notebook(cv, TUN_X + 10, 552, 1.0, scribble=progress(t, b["house"], 2.5))
        if bolt <= 0 and homework:
            draw_pencil(cv, TUN_X + 32 + math.sin(t * 14) * 4, 540, rot=-30)
        elif bolt <= 0:
            draw_pencil(cv, TUN_X + 60, 556, rot=-80)

        # Mom (Ti) and Dad (Mui)
        ti_kw = dict(outfit=None, pose="hands_hip", expression="angry", look=(0.9, 0.2), t=t,
                     mouth_open=ctx.mouth("TI", t))
        if t < L[10].start - 0.1:
            ti_kw.update(pose="stand", expression="happy", look=(0.4, 0))
        if t >= L[11].end:
            ti_kw.update(pose="hands_hip", expression="smug", look=(0.9, 0.1))
        if t >= b["bolt"]:
            ti_kw.update(pose="stand", expression="proud", look=(1, 0))
        a_ti = draw_character(cv, "TI", TI_X, HFLOOR, KS, **ti_kw)

        mui_kw = dict(outfit="dad_role", pose="stand", expression="bored", look=(0.6, 0), t=t,
                      mouth_open=ctx.mouth("MUI", t))
        if t >= L[10].start:
            mui_kw.update(expression="deadpan", look=(1, 0.2))
        if t >= L[12].start:
            mui_kw.update(pose="hands_hip", expression="angry")
        if t >= b["go"]:
            mui_kw.update(pose="point", expression="angry", look=(1, -0.1))
        if t >= b["bolt"] + 0.3:
            mui_kw.update(pose="stand", expression="proud", look=(1, 0), nod=math.sin(t * 6) * 2)
        a_mui = draw_character(cv, "MUI", MUI_X, HFLOOR, KS, **mui_kw)

    # role labels (screen space, above the heads), popped on "play house"
    for i, (a, txt, col) in enumerate(((a_mui, "DAD", P.ACCENT2), (a_ti, "MOM", P.ACCENT))):
        s = pop(t, b["roles"] + i * 0.12, 0.3) * (1 - progress(t, b["rules"] - 0.25, 0.2))
        if s > 0.01:
            label(cv, a["top"][0], a["top"][1] - 40, txt, 24, fill=P.WHITE, bg=col, scale=s)
    s = pop(t, b["roles"] + 0.24, 0.3) * (1 - progress(t, b["rules"] - 0.25, 0.2))
    if s > 0.01 and bolt <= 0:
        label(cv, a_tun["top"][0], a_tun["top"][1] - 34, "CHILD", 24, bg=P.HIGHLIGHT, scale=s)


# ------------------------------------------------------------------ frame
def render_frame(t, ctx):
    b = beats(ctx)
    cv = ctx.canvas(P.WALL_WARM)
    if t < b["stage"]:
        title_backdrop(cv, t)
        idea_card(cv, t, b["card"], "IDEA NUMBER TWO", "BE THE ADULTS")
        return cv.finish()

    if t < b["house"]:
        kids, anchors = _render_stage(t, ctx, b, cv)
        img = cv.finish()
        # spotlight on whoever just stepped out (center) during their announcement
        amt = 0.0
        for k in ORDER:
            o = b["out"][k]
            end = b["slide"][k] if b["slide"][k] is not None else b["L"][7].start - 0.2
            amt = max(amt, 0.55 * progress(t, o + 0.05, 0.2) * (1 - progress(t, end, 0.2)))
        img = spotlight(img, 640, 450, 210, 330, amt)
        return img

    _render_house(t, ctx, b, cv)
    img = cv.finish()
    return img
