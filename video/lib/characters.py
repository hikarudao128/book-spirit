"""Stick-figure characters ("người que"), drawn exactly like the project's SVG engine
(darwin branch: video/ve-di-tuoi-tho/engine.js): egg-shaped head, solid oval eyes with thick
expressive brows, a small tunic-shaped shirt, thick ink stick limbs, round hands without fingers
and oval ink shoes. All body shapes are the engine's SVG paths, drawn in the engine's units
(head ≈ 144 units tall, shoulders at y=-180, ground at y=0) and scaled to pixels by K = k * F.

Main entry point:

    anchors = draw_character(cv, "MUI", x, y, scale=1.0, expression=None, mouth_open=0.0,
                             flip=False, pose="stand", props=(), t=0.0, look=(0, 0),
                             blink=None, outfit=None, nod=0.0, lean=0.0)

(x, y) is the point between the feet on the ground (for pose="sit*": the seat
point under the bottom; feet hang below it).
Returns anchors in screen coordinates (same as cv.to_screen):
    {"head": (x,y), "head_r": r, "mouth": (x,y), "hand_r": (x,y), "hand_l": (x,y),
     "top": (x,y) top of head/hair, "chest": (x,y), "feet": (x,y),
     "shoulder": (x,y) (extra: centre between the shoulders)}

Facing: the face is drawn in 3/4 view looking right (engine default). flip=True mirrors the whole
figure. The face also turns toward `look` when |look[0]| >= 0.25, so a character told to look
left faces left even without flip.

Names: MUI, OLD_MUI, HAI, TUN, TI, MOM, DAD, TEACHER, HIS_KID, VENDOR, KID (generic
classmate; pass hair/colours via `variant` / `colors`), plus draw_dog(...) for DOG.
"""
import math
import re
import zlib
from functools import lru_cache

from . import palette as P
from .core import INK, bezier, clamp, ellipse_pts

# ------------------------------------------------------------------ engine constants
F = 0.42                         # px per engine unit at k = 1 (MUI, k = 1.25, is ~178 px tall)
SKIN = (251, 227, 214)           # engine SKIN #FBE3D6
MOUTH_RED = (209, 73, 91)        # engine RED  #D1495B
WHITE = (255, 255, 255)


def _hex(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def shade(c, k):
    """engine shade(): k < 1 darker, k > 1 lighter."""
    if k < 1:
        return tuple(int(round(clamp(v * k, 0, 255))) for v in c)
    return tuple(int(round(clamp(v + (255 - v) * (k - 1) * 0.35, 0, 255))) for v in c)


# engine HAIR paths (verbatim) + a few new ones in the same construction
HAIR = {
    "spiky": "M -68 -270 L -76 -318 L -62 -322 L -56 -352 L -34 -336 L -16 -366 L 4 -340 L 26 -364 L 40 -338 "
             "L 62 -350 L 66 -324 L 78 -304 L 70 -268 Q 40 -298 0 -296 Q -40 -298 -68 -270 Z",
    "tuft": "M -66 -278 Q -68 -332 -16 -340 Q 34 -346 66 -310 L 68 -282 Q 30 -302 -66 -278 Z "
            "M -14 -338 L -24 -374 L 0 -346 L 8 -380 L 20 -342 Z",
    "neat": "M -66 -280 Q -66 -338 0 -340 Q 66 -340 68 -288 Q 24 -314 -16 -302 Q -42 -296 -66 -280 Z",
    "short": "M -64 -288 Q -62 -336 0 -338 Q 64 -336 66 -290 Q 0 -312 -64 -288 Z",
    "bob": "M -72 -228 Q -80 -344 0 -346 Q 80 -344 74 -228 L 60 -228 Q 62 -298 30 -300 Q 0 -296 -40 -306 "
           "Q -58 -298 -58 -228 Z",
    "topknot": "M -64 -284 Q -60 -336 0 -338 Q 62 -336 66 -286 Q 0 -308 -64 -284 Z",
    # new, same style
    "bun": "M -68 -238 Q -76 -340 0 -342 Q 68 -340 68 -284 Q 30 -306 -8 -300 Q -44 -294 -54 -238 Z",
    "messy": "M -66 -262 L -72 -300 Q -66 -344 -6 -346 Q 52 -348 72 -306 L 74 -268 L 60 -290 L 54 -270 "
             "L 40 -296 L 24 -282 L 14 -302 Q -28 -300 -52 -282 Z",
    "cap_short": "M -62 -282 Q -60 -334 0 -336 Q 62 -334 64 -284 Q 0 -300 -62 -282 Z",   # under a hat
}
HAIR_LINES = {"spiky": "M -44 -318 L -36 -304 M -8 -334 L -2 -316 M 30 -330 L 34 -314 M 58 -316 L 56 -302"}
HEAD_PATH = ("M 2 -334 C 50 -334 66 -300 66 -258 C 66 -214 42 -190 2 -190 C -38 -190 -62 -214 -62 -258 "
             "C -62 -300 -46 -334 2 -334 Z")
HAIR_TOP = {"spiky": -366, "tuft": -346, "neat": -340, "short": -338, "bob": -346, "topknot": -374, "bun": -366,
            "messy": -346, "cap_short": -336, "non_la": -430}
# legacy hair names used by older scene code
HAIR_ALIAS = {"bowl": "tuft", "bowl_grey": "neat", "ponytail_bow": "bob"}

E1, E2, MO = (6, -256), (36, -256), (24, -220)   # far eye, near eye, mouth (engine)
SH_X, SH_Y = 24, -180                           # shoulders (engine)


@lru_cache(maxsize=None)
def _path(d, n=10):
    """Tiny SVG path parser (absolute M/L/Q/C/Z) -> tuple of subpaths (tuples of points)."""
    toks = re.findall(r"[MLQCZ]|-?\d+(?:\.\d+)?", d)
    subs, cur, i, cmd, pos = [], [], 0, None, (0.0, 0.0)

    def num():
        nonlocal i
        v = float(toks[i])
        i += 1
        return v
    while i < len(toks):
        tk = toks[i]
        if tk in "MLQCZ":
            cmd = tk
            i += 1
            if cmd == "Z":
                if cur:
                    subs.append(tuple(cur))
                cur = []
                continue
        if cmd == "M":
            if cur:
                subs.append(tuple(cur))
            pos = (num(), num())
            cur = [pos]
            cmd = "L"
        elif cmd == "L":
            pos = (num(), num())
            cur.append(pos)
        elif cmd == "Q":
            c1 = (num(), num())
            p2 = (num(), num())
            cur += bezier(pos, c1, p2, n)[1:]
            pos = p2
        elif cmd == "C":
            c1, c2, p3 = (num(), num()), (num(), num()), (num(), num())
            for k in range(1, n + 1):
                u = k / n
                a, b, c, e = (1 - u) ** 3, 3 * (1 - u) ** 2 * u, 3 * (1 - u) * u * u, u ** 3
                cur.append((a * pos[0] + b * c1[0] + c * c2[0] + e * p3[0],
                            a * pos[1] + b * c1[1] + c * c2[1] + e * p3[1]))
            pos = p3
    if cur:
        subs.append(tuple(cur))
    return tuple(subs)


def _draw_path(cv, d, fill=None, ow=6, outline=INK, dx=0.0, dy=0.0):
    for sp in _path(d):
        pts = [(x + dx, y + dy) for x, y in sp] if (dx or dy) else sp
        cv.poly(pts, fill=fill, outline=outline, ow=ow)


def _q(cv, p0, p1, p2, width, col=INK):
    cv.line(bezier(p0, p1, p2, 10), col, width)


# ------------------------------------------------------------------ specs
# k: engine scale; legs/torso: length factors (engine haico has legs 1.75); width: shirt width factor.
_KID = dict(kind="kid", k=1.15, legs=1.0, torso=1.0, width=1.0, skin=SKIN, eye_scale=1.0, bottom="shorts",
            neck=None, shoes=INK, pants=P.NAVY)
_ADULT = dict(kind="adult", k=1.8, legs=2.3, torso=1.85, width=1.15, skin=SKIN, eye_scale=1.0, bottom="pants",
              neck=None, shoes=INK, pants=P.PANTS_DARK)

SPECS = {
    # engine cast (CHARS) -------------------------------------------------------------
    "MUI": dict(_KID, k=1.25, hair="tuft", hair_color=_hex("#4A3426"), shirt=_hex("#F4C542"), expr="bored",
                legacy=(40, 46, 54, 58)),                                   # engine `mui`
    "HAI": dict(_KID, k=1.22, legs=1.75, hair="short", hair_color=_hex("#2B2B2B"), shirt=_hex("#A8754E"),
                expr="smug", bandaid=True, legacy=(37, 84, 60, 44)),        # engine `haico`
    "TI": dict(_KID, k=1.18, hair="bob", hair_color=_hex("#3B2A20"), shirt=_hex("#F28DB2"), expr="happy",
               missing_teeth=True, bow=True, legacy=(39, 46, 54, 58)),   # engine `tisun`
    "TUN": dict(_KID, k=1.06, hair="topknot", hair_color=_hex("#2B2B2B"), shirt=_hex("#B9A7E6"), expr="happy",
                eye_scale=1.18, legacy=(40, 46, 54, 58)),   # engine `tun` (a bit taller)
    "OLD_MUI": dict(_ADULT, k=1.85, legs=2.2, torso=1.9, hair="neat", hair_color=_hex("#4A3426"),
                    shirt=_hex("#6C7A89"), neck="tie", tie_color=_hex("#2E3A59"), bags=True, grey_temples=True,
                    belly=True, expr="bored", legacy=(57, 170, 150, 118)),  # engine `muilon`
    "KID": dict(_KID, k=1.15, hair="short", hair_color=_hex("#3A2A1F"), shirt=_hex("#E07A5F"), expr="neutral",
                legacy=(40, 46, 54, 58)),                                   # engine `anh` (recolourable)
    # new cast in the same style ------------------------------------------------------------
    "MOM": dict(_ADULT, k=1.8, legs=2.35, torso=1.85, hair="bun", hair_color=_hex("#2B2220"),
                shirt=_hex("#C4464F"), expr="neutral", lips=True, legacy=(54, 170, 150, 104)),
    "DAD": dict(_ADULT, k=1.95, legs=2.25, torso=1.9, width=1.22, hair="short", hair_color=_hex("#2B2B2B"),
                shirt=_hex("#E9E6DC"), expr="neutral", glasses=True, legacy=(56, 170, 150, 112)),
    "TEACHER": dict(_ADULT, k=1.8, legs=2.3, torso=1.85, hair="bun", hair_color=_hex("#2B2220"),
                    shirt=_hex("#82BEE6"), bottom="aodai", expr="neutral", glasses=True, lips=True,
                    legacy=(54, 170, 150, 104)),
    "HIS_KID": dict(_KID, kind="teen", k=1.3, legs=1.9, torso=1.3, width=1.08, hair="messy",
                    hair_color=_hex("#2B2B2B"), shirt=_hex("#C8463C"), bottom="pants", expr="bored", hood=True,
                    legacy=(38, 96, 92, 70)),
    "VENDOR": dict(_ADULT, k=1.75, legs=2.1, torso=1.8, hair="cap_short", hair_color=_hex("#2B2220"),
                   shirt=_hex("#7FA77A"), expr="happy", hat="non_la", legacy=(54, 150, 135, 96)),
}
# script speaker name -> spec key
SPEAKER_TO_CHAR = {"MUI": "MUI", "OLD MUI": "OLD_MUI", "HAI": "HAI", "TUN": "TUN", "TI": "TI", "MOM": "MOM",
                   "DAD": "DAD", "TEACHER": "TEACHER", "HIS KID": "HIS_KID"}

OUTFITS = {
    # name: overrides applied on top of spec (small costume pieces on the stick figure)
    "uniform": dict(shirt=(247, 247, 242), neck="scarf", scarf_color=_hex("#D62828")),
    "police": dict(shirt=(70, 96, 154), neck=None, hat="police_cap", badge=True),
    "flight": dict(shirt=(44, 76, 140), hat="flight_cap", neck="scarf", scarf_color=P.ACCENT),
    "principal": dict(shirt=(247, 247, 242), neck="tie", tie_color=P.ACCENT, glasses=True),
    "snow_white": dict(shirt=(60, 100, 200), skirt=(255, 220, 80), bottom="dress", bow=True,
                       bow_color=(220, 40, 50)),
    "dad_role": dict(hat="notebook_hat"),
    "work": dict(shirt=(200, 206, 214), neck="tie", tie_color=_hex("#2E3A59")),
}

# expression -> (eyes, brows, resting mouth, talking mouth)   (engine eye/mouth names)
EXPRESSIONS = {
    "neutral": ("thuong", "thuong", "ngam", "talk"),
    "bored":   ("half", "flat", "side", "talk"),
    "deadpan": ("half", "flat", "ngam", "talk"),
    "happy":   ("thuong", "cuoi", "cuoi", "smile"),
    "smug":    ("luom", "luom", "mim", "talk"),
    "shocked": ("tron", "tron", "o", "talk"),
    "angry":   ("thuong", "angry", "frown", "talk"),
    "sad":     ("thuong", "sad", "frown", "talk"),
    "scared":  ("tron", "sad", "meo", "talk"),
    "proud":   ("nham", "cuoi", "cuoi", "smile"),
}

# legacy scene keys -> new keys
_KEY_ALIAS = {"hairC": "hair_color"}


def char_spec(name, outfit=None, **overrides):
    s = dict(SPECS[name])
    s["name"] = name
    if outfit:
        s.update(OUTFITS[outfit])
        if outfit == "dad_role":
            s["hat"] = "notebook_hat"
    _apply_overrides(s, overrides)
    s["hair"] = HAIR_ALIAS.get(s.get("hair"), s.get("hair"))
    if s.get("hair") == "non_la":
        s["hair"], s["hat"] = "cap_short", "non_la"
    if s.get("tie") and not s.get("neck"):
        s["neck"] = "tie"
    if s.get("scarf") and not s.get("neck"):
        s["neck"] = "scarf"
    return s


def _apply_overrides(s, ov):
    """Applies variant/colors overrides; translates the old pixel geometry keys (head_r, leg,
    torso_h, torso_w) into k/legs/torso/width relative to the spec's legacy proportions."""
    ov = {_KEY_ALIAS.get(k, k): v for k, v in ov.items()}
    geo = {k: ov.pop(k) for k in ("head_r", "leg", "torso_h", "torso_w") if k in ov}
    if "hair" in ov and ov["hair"] == "ponytail_bow":
        ov.setdefault("bow", True)
    if ov.get("tie") is False and s.get("neck") == "tie":
        s["neck"] = None
    if ov.get("scarf") is False and s.get("neck") == "scarf":
        s["neck"] = None
    s.update(ov)
    if geo:
        hr0, leg0, th0, tw0 = s["legacy"]
        k0 = s["k"]
        k1 = k0 * geo.get("head_r", hr0) / hr0
        s["k"] = k1
        s["legs"] = s["legs"] * geo.get("leg", leg0) / leg0 * k0 / k1
        s["torso"] = s["torso"] * geo.get("torso_h", th0) / th0 * k0 / k1
        s["width"] = s["width"] * (geo.get("torso_w", tw0) / tw0) ** 0.5
        if s["torso"] > 1.2 and s.get("kind") == "kid":
            s["kind"] = "teen"


def _geom(s, sitting=False):
    lf, tf = s["legs"], s["torso"]
    if sitting:
        hip = -18.0
    else:
        hip = -(16 + 102 * lf)
    hem = hip + 18
    top = hem - 90 * tf
    u = top + 190                 # shift applied to engine upper-body coordinates
    return dict(hip=hip, hem=hem, top=top, u=u, K=s["k"] * F, lf=lf, tf=tf, wf=s["width"],
                af=1.0 + (tf - 1.0) * 0.85)


# ------------------------------------------------------------------ poses (engine joint system)
# per arm: ("a", elbow, hand) = arm-relative (scaled with arm length), ("h", elbow_hint, hand) = hand on
# the head (absolute engine coords; elbow re-solved by IK when the arms are longer)
_DUNG_L = ("a", (-34, -142), (-36, -104))
_DUNG_R = ("a", (34, -142), (36, -104))
POSES = {
    "stand":        (_DUNG_L, _DUNG_R),                                         # dung
    "wave":         (_DUNG_L, ("a", (50, -198), (58, -248))),                   # chao
    "point_up":     (_DUNG_L, ("a", (52, -178), (60, -228))),                   # chi-len
    "present":      (_DUNG_L, ("a", (58, -160), (98, -172))),                   # chia-tay
    "shrug":        (("a", (-52, -156), (-74, -178)), ("a", (52, -156), (76, -178))),   # nhun-vai
    "chin_on_hand": (("a", (-6, -146), (40, -150)), ("h", (46, -150), (30, -187))),     # chong-cam
    "ok":           (_DUNG_L, ("a", (54, -168), (74, -210))),                   # ok
    "cross_arms":   (("a", (-36, -150), (22, -160)), ("a", (36, -148), (-18, -152))),   # khoanh-tay
    "point":        (_DUNG_L, ("a", (62, -178), (110, -188))),                  # chi-nguoi-xem
    "arms_up":      (("a", (-52, -216), (-60, -266)), ("a", (52, -216), (60, -266))),   # an-mung
    "hold_both":    (("a", (-14, -142), (18, -162)), ("a", (52, -150), (94, -162))),    # cam-sach
    # invented in the same joint system
    "hands_hip":    (("a", (-60, -150), (-36, -116)), ("a", (60, -150), (36, -116))),
    "hold":         (_DUNG_L, ("a", (42, -142), (62, -164))),
    "cover_head":   (("h", (-82, -224), (-62, -298)), ("h", (88, -224), (68, -298))),
    "salute":       (_DUNG_L, ("h", (86, -214), (62, -284))),
    "fist_up":      (_DUNG_L, ("a", (50, -210), (56, -260))),
    "facepalm":     (_DUNG_L, ("h", (66, -172), (30, -252))),
    "carry":        (("a", (-46, -150), (-40, -186)), ("a", (46, -150), (40, -186))),   # hands on a shoulder pole
}


def _pose_parts(pose):
    """'sit_chin_on_hand' -> (sitting=True, arm_pose='chin_on_hand'); 'walk', 'run' handled separately."""
    sitting = pose.startswith("sit")
    arm = pose[4:] if pose.startswith("sit_") else ("stand" if pose == "sit" else pose)
    return sitting, arm


def _ik(sh, target, l1, l2, hint):
    dx, dy = target[0] - sh[0], target[1] - sh[1]
    d = clamp(math.hypot(dx, dy), abs(l1 - l2) + 1e-3, l1 + l2 - 1e-3)
    a = math.acos(clamp((l1 * l1 + d * d - l2 * l2) / (2 * l1 * d), -1, 1))
    base = math.atan2(dy, dx)
    cands = [(sh[0] + l1 * math.cos(base + sg * a), sh[1] + l1 * math.sin(base + sg * a)) for sg in (1, -1)]
    return min(cands, key=lambda e: (e[0] - hint[0]) ** 2 + (e[1] - hint[1]) ** 2)


def _rot(p, c, ang):
    ca, sa = math.cos(ang), math.sin(ang)
    x, y = p[0] - c[0], p[1] - c[1]
    return (c[0] + x * ca - y * sa, c[1] + x * sa + y * ca)


def _arms(g, arm_pose, pose, t):
    """Returns {side: (shoulder, elbow, hand)} in engine upper-body coords (before the u shift)."""
    af, wf = g["af"], g["wf"]
    out = {}
    walking = pose in ("walk", "run")
    if pose == "walk_carry":
        arm_pose = "carry"
    for idx, side in enumerate((-1, 1)):
        sh = (side * SH_X * wf, SH_Y)
        sh0 = (side * SH_X, SH_Y)
        if walking:
            run = pose == "run"
            ph = t * (2.2 if not run else 3.6) * 2 * math.pi + (math.pi if side > 0 else 0)
            sw = math.sin(ph) * (0.3 if not run else 0.6)
            if run:
                e = (sh[0] + side * 12 * af, sh[1] + 34 * af)
                h = (e[0] + side * 6 * af, e[1] - 30 * af)
            else:
                e = (sh[0] + side * 10 * af, sh[1] + 38 * af)
                h = (e[0] + side * 2 * af, e[1] + 38 * af)
            e, h = _rot(e, sh, sw), _rot(h, sh, sw)
            out[side] = (sh, e, h)
            continue
        kind, e0, h0 = POSES.get(arm_pose, POSES["stand"])[idx]
        if kind == "a":
            e = (sh[0] + (e0[0] - sh0[0]) * af, sh[1] + (e0[1] - sh0[1]) * af)
            h = (e[0] + (h0[0] - e0[0]) * af, e[1] + (h0[1] - e0[1]) * af)
        else:
            h = h0
            if af == 1.0 and wf == 1.0:
                e = e0
            else:
                L = 39 * af
                e = _ik(sh, h, L, L, (e0[0] * wf, sh[1] + (e0[1] - SH_Y) * af))
        if arm_pose == "wave" and side > 0:
            h = _rot(h, e, math.radians(22) * math.sin(t * 9))
        out[side] = (sh, e, h)
    return out


# ------------------------------------------------------------------ main
def draw_character(cv, name, x, y, scale=1.0, expression=None, mouth_open=0.0, flip=False, pose="stand",
                   props=(), t=0.0, look=(0.0, 0.0), blink=None, outfit=None, nod=0.0, lean=0.0,
                   variant=None, colors=None):
    """Draw a character. See module docstring. `variant`/`colors` = dict overrides of the spec
    (e.g. colors={"shirt": (200,0,0)}) for generic KIDs or recolours."""
    s = char_spec(name, outfit, **(variant or {}), **(colors or {}))
    expr = expression or s["expr"]
    if blink is None:
        blink = auto_blink(t, seed=zlib.crc32(name.encode()) % 97)
    sitting, arm_pose = _pose_parts(pose)
    walking = pose in ("walk", "run", "walk_carry")
    g = _geom(s, sitting)
    K = g["K"]
    if pose == "run":
        lean = lean or 8
    phase = t * (3.6 if pose == "run" else 2.2) * 2 * math.pi
    bob = 0.0
    if walking:
        bob = -abs(math.sin(phase)) * (5 if pose == "walk" else 12)
    u = g["u"] + bob
    body_dir = -1 if flip else 1
    lx, ly = look
    face_dir = (1 if lx > 0 else -1) if abs(lx) >= 0.25 else body_dir
    head_m = face_dir * body_dir          # +1: head drawn as in the engine, -1: mirrored
    out = {}
    with cv.at(x, y, scale * K, flip=flip, rot=lean if not flip else -lean):
        legs_feet = _draw_legs(cv, s, g, sitting, pose, phase, bob)
        with cv.at(0, u):
            _draw_torso(cv, s, g)
            arms = _arms(g, arm_pose, pose, t)
            hy = nod / K if K else 0.0
            with cv.at(4 if head_m < 0 else 0, hy, 1, flip=head_m < 0):
                hd = _draw_head(cv, s, expr, mouth_open, (lx * body_dir * head_m, ly), blink, t, props)
                pts = {k: cv.to_screen(*p) for k, p in hd.items()}
            for side in (-1, 1):
                sh, e, h = arms[side]
                cv.line([sh, e, h], s.get("arm_color", INK), 7)
            for side in (-1, 1):
                h = arms[side][2]
                cv.circle(h[0], h[1], 11, fill=s["skin"], ow=4)
            pts["hand_r"] = cv.to_screen(*arms[1][2])
            pts["hand_l"] = cv.to_screen(*arms[-1][2])
            pts["chest"] = cv.to_screen(0, -160 + 40 * (g["tf"] - 1) * 0.3)
            pts["shoulder"] = cv.to_screen(0, SH_Y)
            hands_local = {side: arms[side][2] for side in (-1, 1)}
        pts["feet"] = cv.to_screen(0, legs_feet)
        # hand props are sized in character pixels: draw them in the (x, y, scale) frame
        hp = [pr for pr in props if pr.partition("@")[0] in HAND_PROPS]
        if hp:
            ps = dict(s, hand_r=11 * K, hand_ow=4 * K)
            with cv.at(0, 0, 1 / K):
                for pr in hp:
                    nm, _, hand = pr.partition("@")
                    side = -1 if hand == "L" else 1
                    hx, hy2 = hands_local[side]
                    HAND_PROPS[nm](cv, (hx * K, (hy2 + u) * K), side, ps, t)
    out.update(pts)
    out["head_r"] = 70 * K * scale
    return out


def _draw_legs(cv, s, g, sitting, pose, phase, bob):
    """Ink stick legs with oval ink shoes. Returns the local y of the feet."""
    hip = g["hip"] + bob
    shoes = s.get("shoes", INK)
    if sitting:
        L = 102 * g["lf"]
        fy = hip + 0.86 * L + 16
        for side in (-1, 1):
            kx = 40 + 9 * side + 10 * (g["lf"] - 1)
            knee = (kx, hip + 6)
            foot = (kx - 2, fy - 16)
            cv.line([(side * 8, hip), knee, foot], INK, 7)
            cv.ellipse(kx + 6, fy - 9, 15, 8, fill=shoes, ow=4)
        return fy
    if pose in ("walk", "run", "walk_carry"):
        run = pose == "run"
        L = -16 - g["hip"]
        for side in (-1, 1):
            ph = phase + (0 if side > 0 else math.pi)
            stride = math.cos(ph) * L * (0.24 if not run else 0.42)
            lift = max(0.0, math.sin(ph)) * L * (0.12 if not run else 0.3)
            fx = side * 4 + stride
            fy = -16 - lift
            if lift > 2:
                knee = (side * 4 + stride * 0.5 + L * (0.08 if not run else 0.2), hip + L * 0.5 - lift * 0.5)
                cv.line([(side * 6, hip), knee, (fx, fy)], INK, 7)
            else:
                cv.line([(side * 6, hip), (fx, fy)], INK, 7)
            cv.ellipse(fx + 5, fy + 7, 15, 8, fill=shoes, ow=4)
        return 0.0
    cv.line([(-9, hip), (-15, -16)], INK, 7)
    cv.line([(9, hip), (15, -16)], INK, 7)
    cv.ellipse(-20, -9, 15, 8, fill=shoes, ow=4)
    cv.ellipse(21, -9, 15, 8, fill=shoes, ow=4)
    return 0.0


def _draw_torso(cv, s, g):
    """Engine shirt (tunic) in upper-body coords: top at -190, hem at -190 + 90*torso."""
    tf, wf = g["tf"], g["wf"]
    top, hem = -190.0, -190.0 + 90 * tf
    shirt = s["shirt"]
    w0, w1 = 27 * wf, 34 * wf
    bottom = s.get("bottom")
    if s.get("hood"):     # hood behind the neck
        cv.ellipse(0, top + 2, 34 * wf, 14, fill=shade(shirt, 0.8), ow=5)
    if bottom == "aodai":
        # áo dài: fitted to the waist, long front/back panels down the legs, side slits
        long_hem = hem + 0.55 * (102 * g["lf"])
        pts = [(-w0, top), (w0, top), (w1 * 0.92, hem - 6), (w1 * 1.08, long_hem),
               (-w1 * 1.08, long_hem), (-w1 * 0.92, hem - 6)]
        cv.poly(pts, fill=shirt, outline=None)
        cv.poly([(-w0, top), (-w0 * 0.5, top), (-w1 * 0.5, long_hem), (-w1 * 1.08, long_hem), (-w1 * 0.92, hem - 6)],
                fill=shade(shirt, 0.78), outline=None)
        cv.poly(pts, fill=None, ow=6)
        cv.line([(0, hem - 6), (0, long_hem)], INK, 3)
        cv.rect(-12, top - 6, 16, top + 6, fill=shirt, ow=4, radius=4)       # mandarin collar
        return
    if bottom == "dress":
        skirt = s.get("skirt", shirt)
        waist = top + (hem - top) * 0.55
        fl = 44 * wf
        sk = [(-w0 * 1.02, waist), (w0 * 1.02, waist), (fl, hem + 10), (-fl, hem + 10)]
        cv.poly(sk, fill=skirt, outline=None)
        cv.poly([(-w0 * 1.02, waist), (-w0 * 0.5, waist), (-fl * 0.5, hem + 10), (-fl, hem + 10)],
                fill=shade(skirt, 0.78), outline=None)
        cv.poly(sk, fill=None, ow=6)
        body = [(-w0, top), (w0, top), (w0 * 1.04, waist + 2), (-w0 * 1.04, waist + 2)]
        cv.poly(body, fill=shirt, outline=None)
        cv.poly([(-w0, top), (-13 * wf, top), (-14 * wf, waist + 2), (-w0 * 1.04, waist + 2)],
                fill=shade(shirt, 0.78), outline=None)
        cv.poly(body, fill=None, ow=6)
    else:
        if s.get("belly"):
            front = bezier((w0, top), (w1 * 1.45, top + (hem - top) * 0.7), (w1 * 1.02, hem), 10)
            pts = [(-w0, top)] + front + bezier((w1 * 1.02, hem), (0, hem + 7), (-w1, hem), 8)[1:]
        else:
            pts = [(-w0, top), (w0, top)] + bezier((w1, hem), (0, hem + 7), (-w1, hem), 8)
        cv.poly(pts, fill=shirt, outline=None)
        cv.poly([(-w0, top), (-13 * wf, top), (-15 * wf, hem + 4), (-25 * wf, hem + 3), (-w1, hem)],
                fill=shade(shirt, 0.78), outline=None)
        cv.poly(pts, fill=None, ow=6)
    if s.get("hood"):     # drawstrings
        cv.line([(-7, top + 4), (-9, top + 30)], WHITE, 3)
        cv.line([(9, top + 4), (11, top + 30)], WHITE, 3)
    neck = s.get("neck")
    if neck == "tie":
        ln = min(tf, 1.5)
        with cv.at(4, -188):
            cv.poly([(-7, 0), (7, 0), (10, 56 * ln), (0, 68 * ln), (-10, 56 * ln)], fill=s.get("tie_color", INK),
                    ow=4)
    elif neck == "scarf":
        cv.poly([(-28 * wf, -192), (28 * wf, -192), (6, -150), (0, -138), (-6, -150)],
                fill=s.get("scarf_color", _hex("#D62828")), ow=4)
    if s.get("badge"):
        cv.circle(16 * wf, -160, 6, fill=P.GOLD, ow=3)
    if bottom == "dress" and s.get("bow_color") and s.get("skirt"):
        _bow(cv, 2, -186, 14, s.get("bow_color"))


# ------------------------------------------------------------------ head & face
def _draw_head(cv, s, expr, mouth_open, look, blink, t, props):
    """Engine head in upper-body coords. Returns local anchor points."""
    hair = s.get("hair") or "short"
    hc = s["hair_color"]
    skin = s["skin"]
    hat = s.get("hat")
    hp = set(props) | ({hat} if hat else set())
    if hair == "topknot":
        cv.circle(0, -352, 21, fill=hc, ow=6)
    if hair == "bun":
        cv.circle(-46, -334, 25, fill=hc, ow=6)
    if "wig" in hp:
        _hp_wig_back(cv, s)
    _draw_path(cv, HEAD_PATH, fill=skin, ow=6)
    if hair in HAIR and not ("police_cap" in hp or "non_la" in hp):
        _draw_path(cv, HAIR[hair], fill=hc, ow=6)
        if hair in HAIR_LINES:
            for sp in _path(HAIR_LINES[hair]):
                cv.line(sp, shade(hc, 1.6), 4)
    elif hair in HAIR:     # hat covers the top: show only the sides
        _draw_path(cv, HAIR["cap_short"], fill=hc, ow=6)
    if s.get("grey_temples"):
        grey = (196, 192, 188)
        cv.poly([(-66, -281), (-64, -300), (-54, -297), (-56, -284)], fill=grey, outline=None)
        cv.poly([(68, -289), (66, -306), (58, -300), (60, -292)], fill=grey, outline=None)
        cv.line([(-64, -296), (-58, -308)], grey, 3)
        cv.line([(20, -334), (30, -316)], grey, 3)
    if s.get("bow") and not hat:
        _bow(cv, 42, -338, 17, s.get("bow_color", _hex("#E0405A")))
    _draw_face(cv, s, expr, mouth_open, look, blink)
    for pr in props:
        if pr in HEAD_PROPS:
            HEAD_PROPS[pr](cv, s, t)
    if hat and hat in HEAD_PROPS and hat not in props:
        HEAD_PROPS[hat](cv, s, t)
    top = min(HAIR_TOP.get(hair, -340), -334)
    if hat == "non_la" or "non_la" in props:
        top = -430
    elif hat or any(p in HEAD_PROPS for p in props):
        top = min(top, -372)
    return {"head": (2, -262), "mouth": (MO[0], MO[1] + 2), "top": (2, top)}


def _bow(cv, x, y, r, col):
    cv.poly([(x, y), (x - r, y - r * 0.65), (x - r, y + r * 0.6)], fill=col, ow=4)
    cv.poly([(x, y), (x + r, y - r * 0.65), (x + r, y + r * 0.6)], fill=col, ow=4)
    cv.circle(x, y, r * 0.3, fill=col, ow=4)


def _lum(c):
    return 0.3 * c[0] + 0.59 * c[1] + 0.11 * c[2]


def _draw_face(cv, s, expr, mouth_open, look, blink):
    eyes, brows, m_rest, m_talk = EXPRESSIONS.get(expr, EXPRESSIONS["neutral"])
    lx, ly = clamp(look[0], -1, 1), clamp(look[1], -1, 1)
    dx, dy = lx * 4, ly * 4
    if eyes == "half" and ly == 0:
        dy = 2
    ink = INK if _lum(s["skin"]) > 90 else (255, 246, 210)      # silhouettes: glowing eyes
    es = s.get("eye_scale", 1.0)
    # brows (thick, follow the expression)
    for i, (ex, ey) in enumerate((E1, E2)):
        _brow(cv, brows, ex + dx * 0.5, ey, i, ink)
    if s.get("bags"):
        _q(cv, (-2, -244), (6, -238), (14, -244), 4, (154, 143, 166))
        _q(cv, (28, -244), (36, -238), (44, -244), 4, (154, 143, 166))
    ek = eyes
    if blink >= 0.5 and eyes not in ("x", "nham", "cuoi"):
        ek = "blink"
    elif blink >= 0.15 and eyes == "thuong":
        ek = "half"
    for ex, ey in (E1, E2):
        _eye(cv, ek, ex + dx, ey + dy, es, ink)
    if s.get("glasses"):
        for ex, ey in (E1, E2):
            cv.circle(ex, ey, 15, fill=None, ow=4)
        cv.line([(E1[0] + 15, E1[1] - 2), (E2[0] - 15, E2[1] - 2)], INK, 4)
        cv.line([(E1[0] - 15, E1[1] - 4), (-30, -262)], INK, 4)
    if s.get("bandaid"):
        with cv.at(-34, -230, 1, rot=28):
            cv.rect(-11, -5, 11, 5, fill=(240, 210, 170), radius=3, ow=3)
            cv.line([(-2, -2), (2, 2)], (200, 160, 120), 2)
    if s.get("mustache"):
        cv.poly(bezier((24, -232), (4, -236), (2, -224), 6) + bezier((2, -224), (24, -228), (46, -224), 6)
                + bezier((46, -224), (44, -236), (24, -232), 6), fill=(84, 78, 82), ow=3)
    _mouth(cv, s, m_rest, m_talk, mouth_open, ink)


def _brow(cv, kind, x, y, i, ink):
    w = 6.5

    def arc(dy, h):
        _q(cv, (x - 9, y + dy), (x, y + dy - h), (x + 9, y + dy), w, ink)

    def tilt(a, b):
        cv.line([(x - 9, y + a), (x + 9, y + b)], ink, w)
    if kind in ("cuoi", "nham"):
        arc(-22, 5)
    elif kind == "tron":
        arc(-25, 4)
    elif kind == "luom":
        if i:
            arc(-23, 5)
        else:
            tilt(-20, -14)
    elif kind == "x":                      # engine 'x' (pain)
        if i:
            tilt(-16, -24)
        else:
            tilt(-24, -16)
    elif kind == "sad":                    # worried / sad: inner ends up
        if i:
            tilt(-24, -15)
        else:
            tilt(-15, -24)
    elif kind == "angry":                  # inner ends down
        if i:
            tilt(-14, -24)
        else:
            tilt(-24, -14)
    elif kind == "flat":
        tilt(-17, -17)
    else:
        arc(-20, 3)


def _eye(cv, kind, x, y, es, ink):
    w = 7
    if kind == "blink":
        cv.line([(x - 9, y), (x + 9, y)], ink, w)
    elif kind == "half":                   # heavy lid: flat lid line over the lower half of the oval
        cv.poly(ellipse_pts(x, y + 1, 7 * es, 8 * es, 0, 180, 12), fill=ink, outline=None)
        cv.line([(x - 9 * es, y + 1), (x + 9 * es, y + 1)], ink, 5)
    elif kind == "cuoi":
        _q(cv, (x - 9, y + 4), (x, y - 9), (x + 9, y + 4), w, ink)
    elif kind == "nham":
        _q(cv, (x - 9, y - 2), (x, y + 7), (x + 9, y - 2), w, ink)
    elif kind == "tron":
        cv.circle(x, y, 10 * es, fill=WHITE, outline=ink if ink == INK else INK, ow=5)
        cv.circle(x + 1, y + 1, 4 * es, fill=INK, outline=None)
    elif kind == "luom":
        cv.line([(x - 10, y - 3), (x + 10, y - 3)], ink, w)
        cv.circle(x + 5, y + 3, 4, fill=ink, outline=None)
    elif kind == "x":
        cv.line([(x - 8, y - 8), (x + 8, y + 8)], ink, w)
        cv.line([(x + 8, y - 8), (x - 8, y + 8)], ink, w)
    else:
        cv.ellipse(x, y, 7 * es, 10 * es, fill=ink, outline=None)


def _mouth(cv, s, rest, talk, m, ink):
    x, y = MO
    m = clamp(m)
    teeth = s.get("missing_teeth")
    line_col = (176, 60, 72) if s.get("lips") and ink == INK else ink
    st = 5
    if m > 0.06 or rest == "o":
        if rest == "o" and m < 0.3:
            m = 0.45
        if talk == "smile":
            k = 1.0 + 0.6 * m
            pts = bezier((x - 14 * k, y - 5), (x, y + 16 * k + 4 * m), (x + 14 * k, y - 5), 12)
            cv.poly(pts, fill=MOUTH_RED, ow=st)
            if teeth:
                _gap_teeth(cv, x, y - 5, 11 * k, 7)
            return
        ry, rx = 2.5 + 9.5 * m, 8 + 3.5 * m
        cy = y + m * 2
        cv.ellipse(x, cy, rx, ry, fill=MOUTH_RED, ow=st)
        if teeth and ry > 5:
            top = cy - ry
            th = min(6.0, ry * 0.7)
            band = [(px, py) for px, py in ellipse_pts(x, cy, rx - 1.5, ry - 1.5, 180, 360, 20) if py <= top + th + 1.5]
            if len(band) > 2:
                cv.poly(band, fill=WHITE, outline=None)
                cv.rect(x - 3, top, x + 3, top + th + 1, fill=INK, outline=None)
            cv.ellipse(x, cy, rx, ry, fill=None, ow=st)
        return
    if rest == "cuoi":
        if teeth:      # engine 'sun' mouth: wide grin with the gap in the front teeth
            cv.poly(bezier((x - 16, y - 6), (x, y + 24), (x + 16, y - 6), 12), fill=MOUTH_RED, ow=st)
            cv.rect(x - 12, y - 5, x + 12, y + 2, fill=WHITE, outline=None)
            cv.rect(x - 2, y - 5, x + 4, y + 2, fill=INK, outline=None)
        else:
            cv.poly(bezier((x - 14, y - 5), (x, y + 16), (x + 14, y - 5), 12), fill=MOUTH_RED, ow=st)
    elif rest == "mim":
        _q(cv, (x - 11, y), (x, y + 7), (x + 12, y - 5), st, line_col)
    elif rest == "meo":
        cv.line(bezier((x - 12, y + 4), (x - 4, y - 7), (x + 2, y + 2), 6)
                + bezier((x + 2, y + 2), (x + 8, y + 7), (x + 13, y - 2), 6)[1:], line_col, st)
    elif rest == "frown":
        _q(cv, (x - 11, y + 4), (x, y - 6), (x + 11, y + 4), st, line_col)
    elif rest == "side":
        cv.line([(x - 8, y + 1), (x + 9, y - 2)], line_col, st)
    else:  # ngam
        cv.line([(x - 8, y), (x + 8, y)], line_col, st)


def _gap_teeth(cv, x, top, half_w, th):
    """Ti's signature: two front teeth missing (white top row with an ink gap in the middle)."""
    cv.rect(x - half_w * 0.85, top + 0.5, x + half_w * 0.85, top + th, fill=WHITE, outline=None)
    cv.rect(x - 3, top + 0.5, x + 3, top + th, fill=INK, outline=None)


def auto_blink(t, seed=0, period=3.7):
    """Deterministic blink: returns 0..1 eyelid closure, a quick blink every ~period s."""
    ph = (t + seed * 0.37) % period
    if ph < 0.12:
        return math.sin(ph / 0.12 * math.pi)
    return 0.0


# ------------------------------------------------------------------ head props (engine units)
def _hp_notebook_hat(cv, s, t):
    with cv.at(2, -334, 1, rot=-8):
        cv.poly([(-62, 6), (0, -40), (62, 6)], fill=(70, 120, 200), ow=5)        # open notebook as a tent
        cv.line([(0, -40), (0, 4)], INK, 4)
        cv.line([(-40, -6), (-8, -28)], WHITE, 4)
        cv.line([(10, -26), (40, -6)], WHITE, 4)


def _hp_wig_back(cv, s):
    for px, py in ((-66, -220), (-72, -250), (70, -220), (74, -250), (-62, -196), (66, -196)):
        cv.circle(px, py, 18, fill=WHITE, ow=4)


def _hp_wig(cv, s, t):
    pts = [(-70, -280), (-64, -310), (-44, -334), (-14, -346), (18, -346), (46, -334), (66, -310), (72, -280)]
    for px, py in pts:
        cv.circle(px, py, 20, fill=WHITE, ow=4)


def _hp_police_cap(cv, s, t):
    cv.poly([(-66, -292), (-74, -352), (78, -352), (70, -292)], fill=(50, 64, 110), ow=6)
    cv.poly([(-8, -298), (82, -298), (96, -284), (-4, -284)], fill=INK, ow=4)            # visor (front)
    cv.circle(4, -324, 11, fill=P.GOLD, ow=4)


def _hp_flight_cap(cv, s, t):
    with cv.at(14, -334, 1, rot=10):
        cv.poly([(-40, 8), (-34, -18), (36, -18), (44, 8)], fill=(40, 70, 140), ow=5)
        cv.line([(-38, 0), (40, 0)], P.GOLD, 4, round_caps=False)


def _hp_crown(cv, s, t):
    y = -330
    cv.poly([(-36, y), (-42, y - 36), (-18, y - 16), (2, y - 44), (22, y - 16), (46, y - 36), (40, y)], fill=P.GOLD,
            ow=5)
    cv.circle(2, y - 44, 5, fill=P.ACCENT, ow=3)


def _hp_non_la(cv, s, t):
    """Conical hat (nón lá)."""
    cv.poly([(2, -432)] + bezier((118, -290), (2, -276), (-114, -290), 10), fill=(238, 214, 156), ow=6)
    for k in (0.4, 0.68):
        y0 = -432 + 142 * k
        cv.line([(2 - 116 * k, y0), (2 + 116 * k, y0)], (190, 160, 100), 3)


HEAD_PROPS = {"notebook_hat": _hp_notebook_hat, "wig": _hp_wig, "police_cap": _hp_police_cap,
              "flight_cap": _hp_flight_cap, "crown": _hp_crown, "non_la": _hp_non_la}


# ------------------------------------------------------------------ hand props (character pixels)
def _hand(cv, h, s):
    cv.circle(h[0], h[1], s["hand_r"], fill=s["skin"], ow=s["hand_ow"])


def _p_phone(cv, h, side, s, t):
    x, y = h
    cv.rect(x - 9, y - 26, x + 9, y + 6, fill=INK, radius=4, ow=2)
    cv.rect(x - 6, y - 22, x + 6, y + 1, fill=(140, 210, 255), outline=None, radius=2)
    _hand(cv, h, s)


def _p_pointer(cv, h, side, s, t):
    x, y = h
    cv.limb([(x - side * 10, y + 14), (x + side * 120, y - 70)], 5, P.WOOD, ow=2.4)
    _hand(cv, h, s)


def _p_gavel(cv, h, side, s, t, swing=0.0):
    x, y = h
    with cv.at(x, y, 1, rot=-side * 30):
        cv.limb([(0, 12), (0, -46)], 7, P.WOOD, ow=2.4)
        cv.rect(-20, -62, 20, -40, fill=P.WOOD_DARK, radius=5, ow=2.6)
    _hand(cv, h, s)


def _p_ruler(cv, h, side, s, t):
    x, y = h
    with cv.at(x, y, 1, rot=side * 35):
        cv.rect(-6, -90, 6, 14, fill=(240, 210, 110), radius=2, ow=2.6)
        for k in range(6):
            cv.line([(-6, -80 + k * 15), (0, -80 + k * 15)], INK, 1.6, round_caps=False)
    _hand(cv, h, s)


def _p_stick(cv, h, side, s, t):
    x, y = h
    cv.limb([(x - side * 8, y + 16), (x + side * 70, y - 110)], 5, (190, 150, 90), ow=2.4)
    _hand(cv, h, s)


def _p_notebook(cv, h, side, s, t):
    x, y = h
    cv.rect(x - 16, y - 34, x + 16, y + 4, fill=(70, 120, 200), radius=3, ow=2.6)
    cv.rect(x - 10, y - 28, x + 8, y - 20, fill=P.WHITE, outline=None)
    _hand(cv, h, s)


def _p_bowl(cv, h, side, s, t):
    x, y = h
    cv.poly(ellipse_pts(x, y - 14, 22, 18, 0, 180, 12), fill=P.WHITE, ow=2.6)
    cv.ellipse(x, y - 14, 22, 5, fill=P.WHITE, ow=2.2)
    _hand(cv, h, s)


def _p_noodles(cv, h, side, s, t):
    x, y = h
    cv.poly([(x - 18, y - 36), (x + 18, y - 36), (x + 13, y + 2), (x - 13, y + 2)], fill=(250, 240, 220), ow=2.6)
    cv.rect(x - 18, y - 30, x + 18, y - 20, fill=P.ACCENT, outline=None)
    _hand(cv, h, s)


def _p_kite_string(cv, h, side, s, t):
    x, y = h
    cv.line([(x, y), (x + side * 160, y - 260)], (90, 80, 80), 1.5)
    _hand(cv, h, s)


HAND_PROPS = {"phone": _p_phone, "pointer": _p_pointer, "gavel": _p_gavel, "ruler": _p_ruler, "stick": _p_stick,
              "notebook": _p_notebook, "bowl": _p_bowl, "noodles": _p_noodles, "kite_string": _p_kite_string}


# ------------------------------------------------------------------ dog
def draw_dog(cv, x, y, scale=1.0, flip=False, pose="stand", t=0.0, color=(222, 168, 96), expression="happy",
             mouth_prop=None):
    """Side-view street dog facing right (flip=True faces left). (x,y) = ground under the belly.
    pose: 'stand' | 'run' | 'sit' | 'wag' (stand + fast tail).  mouth_prop: None | 'notebook'.
    Same ink style as the people: flat colour, thick ink outline, stick legs, oval ink eye."""
    dark = shade(color, 0.78)
    run = pose == "run"
    ph = t * 9.0 if run else 0.0
    bob = -abs(math.sin(ph)) * 8 if run else 0.0
    wag = math.sin(t * (18 if pose in ("wag", "sit") or run else 6)) * (16 if pose != "stand" else 8)
    ow = 3.4
    with cv.at(x, y + bob, scale, flip=flip):
        sit = pose == "sit"
        body_y = -48 if not sit else -40
        tb = (-40, body_y - 8) if not sit else (-30, -22)
        cv.line(bezier(tb, (-62, body_y - 30 + wag * 0.3), (-58 + wag * 0.4, body_y - 52 + abs(wag) * 0.2), 8),
                INK, 6)
        legs = [(-26, 1), (24, 1), (-18, -1), (32, -1)] if not sit else [(-14, 1), (26, 1)]
        for i, (lx, k) in enumerate(legs):
            swing = math.sin(ph + i * 1.6) * 14 if run else 0
            if sit and i == 0:
                cv.ellipse(-16, -14, 24, 16, fill=color, ow=ow)
                continue
            cv.line([(lx, body_y + 8), (lx + swing, -4)], INK, 6)
            cv.ellipse(lx + swing + 4, -3, 8, 4.5, fill=INK, outline=None)
        if sit:
            cv.poly([(-34, -6), (-30, -52), (8, -76), (30, -64), (22, -8)], fill=color, ow=ow)
        else:
            cv.ellipse(0, body_y, 50, 22, fill=color, ow=ow)
            cv.poly([(-50, body_y), (-26, body_y - 20), (-10, body_y + 21), (-44, body_y + 12)], fill=dark,
                    outline=None)
            cv.ellipse(0, body_y, 50, 22, fill=None, ow=ow)
        hx, hy = (44, body_y - 26) if not sit else (26, -86)
        cv.poly([(hx + 2, hy - 18), (hx - 14, hy + 8), (hx - 4, hy + 14)], fill=dark, ow=ow)
        cv.circle(hx, hy, 22, fill=color, ow=ow)
        cv.ellipse(hx + 22, hy + 8, 16, 11, fill=color, ow=ow)
        cv.ellipse(hx + 36, hy + 3, 5, 4, fill=INK, outline=None)
        cv.poly([(hx - 8, hy - 18), (hx - 26, hy + 2), (hx - 12, hy + 10)], fill=dark, ow=ow)
        cv.ellipse(hx + 8, hy - 5, 3.2, 4.6, fill=INK, outline=None)
        cv.line([(hx + 3, hy - 13), (hx + 13, hy - 14)], INK, 3)
        if expression == "happy" and mouth_prop is None:
            cv.curve((hx + 16, hy + 16), (hx + 24, hy + 22), (hx + 32, hy + 15), INK, 2.6)
            cv.ellipse(hx + 24, hy + 24, 5, 8, fill=MOUTH_RED, ow=2.4)
        if mouth_prop == "notebook":
            with cv.at(hx + 30, hy + 20, 1, rot=12):
                cv.rect(-18, -10, 18, 12, fill=(70, 120, 200), ow=2.6)
                cv.poly([(4, -10), (10, -4), (18, -10)], fill=P.WHITE, ow=1.6)   # chewed corner
                cv.line([(-12, 2), (6, 2)], P.WHITE, 2)
    return {"head": cv.to_screen(x + (44 if not flip else -44) * scale, y - 74 * scale)}


# ------------------------------------------------------------------ vendor extras
def draw_vendor(cv, x, y, scale=1.0, flip=False, t=0.0, walking=True, steam=True):
    """Street vendor woman (nón lá) carrying a gánh (shoulder pole with two baskets)."""
    pose = "walk_carry" if walking else "carry"
    a = draw_character(cv, "VENDOR", x, y, scale, pose=pose, t=t, flip=flip)
    g = _geom(char_spec("VENDOR"))
    sh_y = y + (g["u"] + SH_Y - 4) * g["K"] * scale
    sway = math.sin(t * 2.2 * 2 * math.pi) * 3 if walking else 0
    with cv.at(x, sh_y, scale, flip=flip):
        pole = [(-150, 6 + sway), (150, 6 - sway)]
        for end, goods in ((-1, "fruit"), (1, "pot")):
            px = end * 138
            py = 6 - end * sway
            swing = math.sin(t * 4.4 + end) * 3 if walking else 0
            by = py + 120
            cv.line([(px - 30, py), (px - 34 + swing, by - 26)], INK, 2)
            cv.line([(px + 30, py), (px + 34 + swing, by - 26)], INK, 2)
            cv.ellipse(px + swing, by - 26, 40, 9, fill=(200, 160, 90))
            cv.poly([(px - 40 + swing, by - 26), (px + 40 + swing, by - 26), (px + 30 + swing, by + 6),
                     (px - 30 + swing, by + 6)], fill=(214, 172, 100))
            for k in range(3):
                cv.line([(px - 34 + swing + k * 4, by - 16 + k * 10), (px + 34 + swing - k * 4, by - 16 + k * 10)],
                        (170, 128, 64), 2)
            if goods == "fruit":
                for i, c in enumerate([(240, 200, 60), (120, 190, 80), (240, 120, 60), (240, 200, 60)]):
                    cv.circle(px - 24 + i * 16 + swing, by - 34 - (i % 2) * 6, 10, fill=c, ow=2.4)
            else:
                cv.rect(px - 26 + swing, by - 52, px + 26 + swing, by - 26, fill=(150, 150, 160), radius=4)
                cv.ellipse(px + swing, by - 52, 28, 6, fill=(170, 170, 180))
                if steam:
                    for i in range(3):
                        ph = (t * 0.8 + i / 3) % 1
                        sx = px + swing - 14 + i * 14 + math.sin(ph * 6 + i) * 5
                        sy = by - 60 - ph * 50
                        cv.circle(sx, sy, 6 + ph * 6, fill=(255, 255, 255), outline=None)
        cv.limb(pole, 6, P.WOOD)
    return a
