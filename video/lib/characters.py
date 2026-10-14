"""Procedural cartoon characters (flat colours, thick INK outlines, big heads).

Main entry point:

    anchors = draw_character(cv, "MUI", x, y, scale=1.0, expression=None, mouth_open=0.0,
                             flip=False, pose="stand", props=(), t=0.0, look=(0, 0),
                             blink=None, outfit=None, nod=0.0, lean=0.0)

(x, y) is the point between the feet on the ground (for pose="sit*": the seat
point under the bottom; feet hang ~0.9*leg below it).
Returns anchors in the caller's coordinate frame:
    {"head": (x,y), "head_r": r, "mouth": (x,y), "hand_r": (x,y), "hand_l": (x,y),
     "top": (x,y) top of head/hair, "chest": (x,y), "feet": (x,y)}
so scenes can attach speech bubbles, custom props, kite strings, labels...

Names: MUI, OLD_MUI, HAI, TUN, TI, MOM, DAD, TEACHER, HIS_KID, VENDOR, KID (generic
classmate; pass outfit/hair via `variant`), plus draw_dog(...) for DOG.
"""
import math

from . import palette as P
from .core import INK, OW, bezier, clamp, ellipse_pts, lerp

# ------------------------------------------------------------------ specs
_KID = dict(kind="kid", head_r=40, leg=46, torso_h=54, torso_w=58, arm_w=13, leg_w=15, hand_r=8,
            skin=P.SKIN, hair_color=P.HAIR, eye_scale=1.0, cheeks=True, shoes=P.SANDAL, neck=0.0)
_ADULT = dict(kind="adult", head_r=54, leg=170, torso_h=150, torso_w=104, arm_w=22, leg_w=28, hand_r=12,
              skin=P.SKIN_ADULT, hair_color=P.HAIR, eye_scale=0.9, cheeks=False, shoes=P.PANTS_DARK, neck=10)

SPECS = {
    "MUI": dict(_KID, hair="bowl", shirt=P.SHIRT_BLUE, bottom="shorts", pants=P.NAVY, expr="bored"),
    "HAI": dict(_KID, hair="spiky", head_r=37, leg=84, torso_h=60, torso_w=44, arm_w=11, leg_w=12,
                shirt=P.SHIRT_GREEN, stripes=True, bottom="shorts", pants=(196, 140, 80), expr="smug",
                bandaid=True),
    "TUN": dict(_KID, hair="bob", eye_scale=1.45, shirt=P.DRESS_YELLOW, bottom="dress", expr="happy",
                hair_color=(64, 40, 30)),
    "TI": dict(_KID, hair="ponytail_bow", head_r=39, shirt=P.DRESS_PINK, bottom="dress", expr="happy",
               missing_teeth=True),
    "KID": dict(_KID, hair="short", shirt=P.SHIRT_WHITE, bottom="shorts", pants=P.NAVY, expr="neutral"),
    "MOM": dict(_ADULT, hair="bun", shirt=P.MOM_TOP, bottom="pants", pants=P.PANTS_DARK, expr="neutral",
                lips=True),
    "DAD": dict(_ADULT, hair="short", head_r=56, shirt=P.DAD_SHIRT, bottom="pants", pants=(64, 74, 96),
                expr="neutral", glasses=True, torso_w=112),
    "TEACHER": dict(_ADULT, hair="bun", shirt=P.AODAI, bottom="aodai", pants=P.WHITE, expr="neutral",
                    glasses=True, lips=True),
    "OLD_MUI": dict(_ADULT, hair="bowl_grey", head_r=57, shirt=(214, 196, 150), bottom="pants",
                    pants=(90, 84, 80), expr="bored", mustache=True, belly=True, hair_color=(70, 66, 70),
                    torso_w=118),
    "HIS_KID": dict(_KID, kind="teen", hair="messy", head_r=38, leg=96, torso_h=92, torso_w=70, arm_w=15,
                    leg_w=18, hand_r=9, shirt=P.HOODIE, bottom="pants", pants=(60, 70, 100), expr="bored",
                    cheeks=False, eye_scale=0.95, shoes=(240, 240, 240), neck=4, hood=True),
    "VENDOR": dict(_ADULT, hair="non_la", shirt=(120, 160, 120), bottom="pants", pants=(60, 56, 64),
                   expr="happy", leg=150, torso_h=135, torso_w=96),
}
# script speaker name -> spec key
SPEAKER_TO_CHAR = {"MUI": "MUI", "OLD MUI": "OLD_MUI", "HAI": "HAI", "TUN": "TUN", "TI": "TI", "MOM": "MOM",
                   "DAD": "DAD", "TEACHER": "TEACHER", "HIS KID": "HIS_KID"}

OUTFITS = {
    # name: overrides applied on top of spec
    "uniform": dict(shirt=P.SHIRT_WHITE, pants=P.NAVY, scarf=True, stripes=False),
    "police": dict(shirt=(70, 96, 150), pants=(50, 60, 90), stripes=False, hat="police_cap", badge=True),
    "flight": dict(shirt=(40, 70, 140), stripes=False, hat="flight_cap", scarf_color=P.ACCENT, scarf=True),
    "principal": dict(shirt=P.SHIRT_WHITE, pants=P.PANTS_DARK, tie=True, glasses=True, stripes=False),
    "snow_white": dict(shirt=(60, 100, 200), skirt=(255, 220, 80), bottom="dress", bow_color=(220, 40, 50)),
    "dad_role": dict(hat="notebook_hat"),
    "work": dict(shirt=(200, 206, 214), pants=(60, 60, 70), tie=True, stripes=False),
}

EXPRESSIONS = {
    #            lid   pupil  brow_dy brow_tilt mouth        eye_scale
    "neutral":  (0.00, 1.0,   0.00,   0,        "flat",      1.0),
    "bored":    (0.50, 1.0,   0.10,   0,        "flat_side", 1.0),
    "deadpan":  (0.55, 0.9,   0.10,   0,        "flat",      1.0),
    "happy":    (0.00, 1.0,  -0.08,   0,        "smile",     1.0),
    "smug":     (0.38, 1.0,   0.00,  -1,        "smirk",     1.0),
    "shocked":  (0.00, 0.55, -0.22,   0,        "O",         1.3),
    "angry":    (0.22, 1.0,   0.08,   1,        "frown_flat", 1.0),
    "sad":      (0.25, 1.0,   0.00,   2,        "frown",     1.0),
    "scared":   (0.00, 0.6,  -0.12,   2,        "wavy",      1.2),
    "proud":    (0.45, 1.0,  -0.06,   0,        "smile",     1.0),
}


def char_spec(name, outfit=None, **overrides):
    s = dict(SPECS[name])
    s["name"] = name
    if outfit:
        s.update(OUTFITS[outfit])
    s.update(overrides)
    return s


# ------------------------------------------------------------------ helpers
def _ik(sh, target, l1, l2, side, prefer="out"):
    """Two-bone IK. Returns elbow point; elbow bends outward (prefer='out') or down ('down')."""
    dx, dy = target[0] - sh[0], target[1] - sh[1]
    d = math.hypot(dx, dy)
    d = clamp(d, abs(l1 - l2) + 1e-3, l1 + l2 - 1e-3)
    a = math.acos(clamp((l1 * l1 + d * d - l2 * l2) / (2 * l1 * d), -1, 1))
    base = math.atan2(dy, dx)
    # choose the elbow solution that sits further outward
    c1 = base + a
    c2 = base - a
    e1 = (sh[0] + l1 * math.cos(c1), sh[1] + l1 * math.sin(c1))
    e2 = (sh[0] + l1 * math.cos(c2), sh[1] + l1 * math.sin(c2))
    if prefer == "down":
        return e1 if e1[1] > e2[1] else e2
    return e1 if (e1[0] - e2[0]) * side > 0 else e2


def _dir(a, side):
    r = math.radians(a)
    return (side * math.sin(r), math.cos(r))


# pose -> per-arm (upper_angle, elbow_bend) measured from straight down, + = outward.
# a value of "ik:<target>" uses IK to a named target.
ARM_POSES = {
    "stand": ((14, -6), (14, -6)),
    "point": ((86, 4), (14, -6)),
    "point_up": ((142, 14), (14, -6)),
    "hands_hip": ((52, -118), (52, -118)),
    "arms_up": ((155, 12), (155, 12)),
    "shrug": ((58, 92), (58, 92)),
    "hold": ((14, -100), (14, -6)),
    "hold_both": ((14, -100), (14, -100)),
    "present": ((70, 12), (70, 12)),
    "cover_head": ("ik:head_top", "ik:head_top"),
    "chin_on_hand": ("ik:chin", (14, -6)),
    "salute": ("ik:brow", (14, -6)),
    "fist_up": ((150, -70), (14, -6)),
    "facepalm": ("ik:face", (14, -6)),
}


def _pose_parts(pose):
    """'sit_chin_on_hand' -> (sitting=True, arm_pose='chin_on_hand'); 'walk', 'run' handled separately."""
    sitting = pose.startswith("sit")
    arm = pose[4:] if pose.startswith("sit_") else ("stand" if pose == "sit" else pose)
    return sitting, arm


# ------------------------------------------------------------------ main
def draw_character(cv, name, x, y, scale=1.0, expression=None, mouth_open=0.0, flip=False, pose="stand",
                   props=(), t=0.0, look=(0.0, 0.0), blink=None, outfit=None, nod=0.0, lean=0.0,
                   variant=None, colors=None):
    """Draw a character. See module docstring. `variant`/`colors` = dict overrides of the spec
    (e.g. colors={"shirt": (200,0,0)}) for generic KIDs or recolours."""
    s = char_spec(name, outfit, **(variant or {}), **(colors or {}))
    expr = expression or s["expr"]
    if blink is None:
        blink = auto_blink(t, seed=hash(name) % 97)
    R = s["head_r"]
    leg, th, tw = s["leg"], s["torso_h"], s["torso_w"]
    sitting, arm_pose = _pose_parts(pose)
    walking = pose in ("walk", "run")
    phase = t * (2.2 if pose == "walk" else 3.6) * 2 * math.pi

    bob = 0.0
    if walking:
        bob = -abs(math.sin(phase)) * (4 if pose == "walk" else 9)
    if pose == "run":
        lean = lean or 8
    hip_y = (-leg if not sitting else 0.0) + bob
    top = hip_y - th
    head_cy = top - R * 0.80 - s.get("neck", 0) + nod
    if s["kind"] == "adult":
        head_cy = top - R * 0.92 - s.get("neck", 0) + nod

    out = {}
    with cv.at(x, y, scale, flip=flip, rot=lean if not flip else -lean):
        # ---------------- legs
        hx = tw * 0.24
        feet = []
        for side in (-1, 1):
            hip = (side * hx, hip_y)
            if sitting:
                knee = (side * (hx + tw * 0.2), hip_y + 4)
                foot = (side * (hx + tw * 0.14), hip_y + leg * 0.9)
                pts = [knee, foot]
            elif walking:
                ph = phase + (0 if side > 0 else math.pi)
                lift = max(0.0, math.sin(ph)) * leg * (0.28 if pose == "walk" else 0.45)
                foot = (side * hx + math.cos(ph) * (3 if pose == "walk" else 8), -lift)
                pts = [hip, foot]
            else:
                foot = (side * (hx + 2), 0.0)
                pts = [hip, foot]
            feet.append(foot)
            legcol = s["skin"] if s["bottom"] in ("shorts", "dress") else s["pants"]
            if s["bottom"] == "aodai":
                legcol = s["pants"]
            cv.limb(pts, s["leg_w"], legcol)
            # shoe
            fx, fy = foot
            cv.ellipse(fx + side * 5, fy - s["leg_w"] * 0.25, s["leg_w"] * 0.85, s["leg_w"] * 0.45, fill=s["shoes"])
            if sitting:
                cv.circle(knee[0], knee[1], s["leg_w"] * 0.7,
                          fill=s["skin"] if s["bottom"] in ("shorts", "dress") else s["pants"])

        # ---------------- torso / clothes
        shirt = s["shirt"]
        belly = s.get("belly", False)
        if s["bottom"] == "shorts":
            sh_y1 = hip_y + leg * 0.32 if not sitting else hip_y + 8
            if sitting:   # thighs come toward the camera: wide, short shorts
                cv.rect(-tw / 2 - tw * 0.16, hip_y - 14, tw / 2 + tw * 0.16, sh_y1, fill=s["pants"], radius=10)
            else:
                cv.rect(-tw / 2 + 2, hip_y - 14, tw / 2 - 2, sh_y1, fill=s["pants"], radius=6)
            if not sitting:
                cv.line([(0, hip_y - 4), (0, sh_y1 - 2)], INK, 2.5)
        elif s["bottom"] == "pants":
            cv.rect(-tw / 2 + 4, hip_y - 14, tw / 2 - 4, hip_y + 12, fill=s["pants"], radius=8)
        if s["bottom"] == "dress":
            skirt = s.get("skirt", shirt)
            hem = hip_y + (leg * 0.42 if not sitting else 14)
            cv.poly([(-tw * 0.42, top + th * 0.45), (tw * 0.42, top + th * 0.45), (tw * 0.68, hem),
                     (-tw * 0.68, hem)], fill=skirt)
            cv.rect(-tw / 2, top, tw / 2, top + th * 0.55, fill=shirt, radius=tw * 0.22)
        elif s["bottom"] == "aodai":
            hem = hip_y + (leg * 0.62 if not sitting else 20)
            cv.poly([(-tw * 0.46, top + 10), (tw * 0.46, top + 10), (tw * 0.52, hem), (-tw * 0.52, hem)],
                    fill=shirt)
            cv.line([(-tw * 0.5, hip_y - 30), (-tw * 0.52, hem)], INK, 2.5)   # side slits
            cv.line([(tw * 0.5, hip_y - 30), (tw * 0.52, hem)], INK, 2.5)
            cv.rect(-tw / 2, top, tw / 2, hip_y - 20, fill=shirt, radius=tw * 0.25)
            cv.ellipse(0, top + 6, tw * 0.16, 7, fill=shirt)   # mandarin collar
        elif belly:
            cv.rect(-tw / 2, top, tw / 2, hip_y + 4, fill=shirt, radius=tw * 0.3)
            cv.ellipse(0, hip_y - th * 0.30, tw * 0.62, th * 0.42, fill=shirt)
            cv.circle(0, hip_y - th * 0.26, 3, fill=INK, outline=None)   # belly button hint / button
        elif s["kind"] == "adult":
            cv.poly(_torso_pts(tw, top, hip_y + 8, 0.84, tw * 0.22), fill=shirt)
        else:
            cv.rect(-tw / 2, top, tw / 2, hip_y - (6 if s["bottom"] == "shorts" else -6), fill=shirt,
                    radius=tw * 0.22)
        if s.get("stripes"):
            for k in range(1, 4):
                yy = top + th * k / 4
                cv.line([(-tw / 2 + 5, yy), (tw / 2 - 5, yy)], (80, 150, 80), 5, round_caps=False)
        if s.get("hood"):
            cv.ellipse(0, top + 4, tw * 0.38, 12, fill=tuple(int(c * 0.85) for c in shirt))
            cv.line([(-8, top + 12), (-10, top + 40)], P.WHITE, 2.5)
            cv.line([(8, top + 12), (10, top + 40)], P.WHITE, 2.5)
        if s.get("tie"):
            cv.poly([(-6, top + 6), (6, top + 6), (9, top + th * 0.6), (0, top + th * 0.7), (-9, top + th * 0.6)],
                    fill=P.ACCENT, ow=2.5)
        if s.get("scarf"):
            sc = s.get("scarf_color", P.SCARF_RED)
            cv.poly([(-tw * 0.36, top + 2), (tw * 0.36, top + 2), (0, top + th * 0.36)], fill=sc, ow=2.8)
            cv.poly([(-4, top + 10), (4, top + 10), (12, top + th * 0.5), (-2, top + th * 0.42)], fill=sc, ow=2.5)
        if s.get("badge"):
            cv.circle(tw * 0.22, top + th * 0.3, 6, fill=P.GOLD, ow=2.2)

        if s["kind"] != "kid":
            cv.limb([(0, top + 6), (0, head_cy + R * 0.6)], R * 0.34, s["skin"])
            if s.get("bottom") == "aodai":
                cv.ellipse(0, top + 2, R * 0.3, 8, fill=shirt)
        # ---------------- arms
        arm_w, hr = s["arm_w"], s["hand_r"]
        ua = th * (0.50 if s["kind"] != "adult" else 0.46)
        fa = ua * 0.95
        hands = {}
        mouth_y = head_cy + R * 0.48
        targets = {
            "chin": (R * 0.12, head_cy + R * 0.98 + hr * 0.4),
            "head_top": (R * 1.0, head_cy - R * 0.1),     # hands clutching the sides of the head
            "brow": (R * 0.55, head_cy - R * 0.4),
            "face": (R * 0.1, head_cy + R * 0.05),
        }
        for side, spec in ((1, None), (-1, None)):
            if walking:
                ph = phase + (math.pi if side > 0 else 0)
                spec = (16 + 18 * math.sin(ph), -15 - 10 * max(0, math.sin(ph)))
            else:
                pa = ARM_POSES.get(arm_pose, ARM_POSES["stand"])
                spec = pa[0] if side > 0 else pa[1]
            sh = (side * (tw / 2 - arm_w * 0.55), top + arm_w * 0.75)
            if arm_pose == "wave" and side > 0:
                spec = (148 + 6 * math.sin(t * 9), -30 + 28 * math.sin(t * 9))
            if isinstance(spec, str):
                tgt = targets[spec.split(":")[1]]
                tgt = (side * abs(tgt[0]), tgt[1]) if not spec.endswith("chin") else (tgt[0] * side, tgt[1])
                elbow = _ik(sh, tgt, ua, fa, side, "down" if spec.endswith("chin") else "out")
                hand = tgt
            else:
                a, e = spec
                d1 = _dir(a, side)
                elbow = (sh[0] + ua * d1[0], sh[1] + ua * d1[1])
                d2 = _dir(a + e, side)
                hand = (elbow[0] + fa * d2[0], elbow[1] + fa * d2[1])
            hands[side] = (sh, elbow, hand)
        # arms that reach the face are drawn after the head
        late = [sd for sd in (1, -1) if hands[sd][2][1] < hands[sd][0][1] - ua * 0.3 or (
            isinstance(ARM_POSES.get(arm_pose, ARM_POSES["stand"])[0 if sd > 0 else 1], str) and not walking)]
        for side in (1, -1):
            if side not in late:
                _draw_arm(cv, s, *hands[side])

        # ---------------- head
        _draw_head(cv, s, head_cy, expr, mouth_open, look, blink, t, props)

        for side in late:
            _draw_arm(cv, s, *hands[side])

        # ---------------- hand props
        for pr in props:
            nm, _, hand = pr.partition("@")
            if nm in HAND_PROPS:
                side = -1 if hand == "L" else 1
                HAND_PROPS[nm](cv, hands[side][2], side, s, t)

        def g(p):
            return cv.to_screen(*p)

        out = {
            "head": g((0, head_cy)), "head_r": R * scale, "mouth": g((0, mouth_y)),
            "hand_r": g(hands[1][2]), "hand_l": g(hands[-1][2]),
            "top": g((0, head_cy - R * 1.15)), "chest": g((0, top + th * 0.35)),
            "feet": g((0, 0 if not sitting else hip_y + leg * 0.88)),
        }
    # to_screen gives screen coords; convert back into the caller's frame is not needed for
    # the common case (caller frame == screen or camera). Provide both for clarity.
    return out


def _torso_pts(tw, top, bottom, waist, r):
    """Shoulders tw wide with rounded corners, tapering to waist*tw at the bottom."""
    pts = ellipse_pts(-tw / 2 + r, top + r, r, r, 180, 270, 6) + ellipse_pts(tw / 2 - r, top + r, r, r, 270, 360, 6)
    pts += [(tw * waist / 2, bottom), (-tw * waist / 2, bottom)]
    return pts


def _draw_arm(cv, s, sh, elbow, hand):
    skin = s["skin"]
    cv.limb([sh, elbow, hand], s["arm_w"], skin)
    # short sleeve over the upper arm
    sl = (lerp(sh[0], elbow[0], 0.55), lerp(sh[1], elbow[1], 0.55))
    sleeve_col = s["shirt"]
    long_sleeve = s["kind"] == "adult" and s["name"] in ("TEACHER",) or s.get("hood")
    if long_sleeve:
        cv.limb([sh, elbow, (lerp(elbow[0], hand[0], 0.8), lerp(elbow[1], hand[1], 0.8))], s["arm_w"] + 3,
                sleeve_col)
    else:
        cv.limb([sh, sl], s["arm_w"] + 4, sleeve_col)
    cv.circle(hand[0], hand[1], s["hand_r"], fill=skin)


def auto_blink(t, seed=0, period=3.7):
    """Deterministic blink: returns 0..1 eyelid closure, a quick blink every ~period s."""
    ph = (t + seed * 0.37) % period
    if ph < 0.12:
        return math.sin(ph / 0.12 * math.pi)
    return 0.0


# ------------------------------------------------------------------ head & face
def _draw_head(cv, s, cy, expr, mouth_open, look, blink, t, props):
    R = s["head_r"]
    skin = s["skin"]
    hair = s.get("hair")
    hc = s["hair_color"]
    # back hair layers
    if hair == "bob":
        cv.poly([(-R * 1.12, cy - R * 0.2)] + ellipse_pts(0, cy - R * 0.05, R * 1.12, R * 1.08, 180, 360, 24)
                + [(R * 1.12, cy + R * 0.62), (-R * 1.12, cy + R * 0.62)], fill=hc)
    elif hair == "ponytail_bow":
        sway = math.sin(t * 3) * 4
        cv.poly(bezier((R * 0.6, cy - R * 0.75), (R * 1.7 + sway, cy - R * 0.8), (R * 1.35 + sway, cy + R * 0.7), 12)
                + bezier((R * 1.1 + sway, cy + R * 0.6), (R * 1.25, cy - R * 0.2), (R * 0.5, cy - R * 0.45), 10),
                fill=hc)
    elif hair == "bun":
        cv.circle(0, cy - R * 1.02, R * 0.42, fill=hc)
    # ears
    for side in (-1, 1):
        cv.circle(side * R * 0.97, cy + R * 0.12, R * 0.2, fill=skin)
    cv.circle(0, cy, R, fill=skin)

    _draw_face(cv, s, cy, expr, mouth_open, look, blink)

    # front hair
    if hair == "bowl" or hair == "bowl_grey":
        fr = -0.42 if hair == "bowl" else -0.56
        pts = ellipse_pts(0, cy - R * 0.04, R * 1.07, R * 1.08, 172, 368, 30)
        fringe = []
        n = 7
        for i in range(n + 1):
            fx = lerp(R * 0.74, -R * 0.74, i / n)
            fy = cy + R * fr + (R * 0.05 if i % 2 else 0)
            fringe.append((fx, fy))
        pts = pts + [(R * 0.80, cy + R * 0.12)] + fringe + [(-R * 0.80, cy + R * 0.12)]
        cv.poly(pts, fill=hc)
        if hair == "bowl":
            cv.curve((R * 0.05, cy - R * 1.08), (R * 0.25, cy - R * 1.45), (R * 0.42, cy - R * 1.2), INK, 3.2)
        else:
            for side in (-1, 1):   # grey temples
                cv.poly([(side * R * 1.02, cy - R * 0.1), (side * R * 0.8, cy + R * 0.12),
                         (side * R * 0.74, cy - R * 0.3), (side * R * 0.98, cy - R * 0.4)], fill=P.HAIR_WHITE,
                        ow=2.5)
    elif hair == "spiky":
        pts = []
        n = 9
        for i in range(n + 1):
            a = 180 + 180 * i / n
            r = R * (1.38 if i % 2 else 1.02)
            pts.append((math.cos(math.radians(a)) * r, cy - R * 0.05 + math.sin(math.radians(a)) * r))
        pts += [(R * 0.9, cy - R * 0.05), (R * 0.55, cy - R * 0.42), (R * 0.25, cy - R * 0.3),
                (-R * 0.1, cy - R * 0.45), (-R * 0.45, cy - R * 0.32), (-R * 0.9, cy - R * 0.05)]
        cv.poly(pts, fill=hc)
    elif hair == "bob":
        pts = ellipse_pts(0, cy - R * 0.05, R * 1.1, R * 1.08, 180, 360, 24)
        pts += [(R * 1.1, cy + R * 0.55), (R * 0.82, cy + R * 0.55), (R * 0.78, cy - R * 0.32),
                (-R * 0.78, cy - R * 0.32), (-R * 0.82, cy + R * 0.55), (-R * 1.1, cy + R * 0.55)]
        cv.poly(pts, fill=hc)
    elif hair == "ponytail_bow":
        pts = ellipse_pts(0, cy - R * 0.03, R * 1.06, R * 1.06, 185, 355, 24)
        pts += bezier((R * 1.0, cy - R * 0.25), (R * 0.2, cy - R * 0.2), (-R * 0.55, cy - R * 0.55), 10)
        pts += [(-R * 0.9, cy - R * 0.1)]
        cv.poly(pts, fill=hc)
        _bow(cv, -R * 0.55, cy - R * 0.98, R * 0.55, s.get("bow_color", P.BOW_RED))
    elif hair == "bun":
        pts = ellipse_pts(0, cy - R * 0.05, R * 1.06, R * 1.05, 182, 358, 24)
        pts += bezier((R * 1.0, cy + R * 0.05), (R * 0.6, cy - R * 0.62), (0, cy - R * 0.62), 8)
        pts += bezier((0, cy - R * 0.62), (-R * 0.6, cy - R * 0.62), (-R * 1.0, cy + R * 0.05), 8)
        cv.poly(pts, fill=hc)
    elif hair == "short":
        pts = ellipse_pts(0, cy - R * 0.05, R * 1.06, R * 1.05, 185, 355, 24)
        pts += [(R * 0.98, cy - R * 0.15), (R * 0.85, cy - R * 0.5), (-R * 0.2, cy - R * 0.62),
                (-R * 0.85, cy - R * 0.35), (-R * 0.98, cy - R * 0.15)]
        cv.poly(pts, fill=hc)
    elif hair == "messy":
        pts = ellipse_pts(0, cy - R * 0.05, R * 1.1, R * 1.1, 180, 360, 24)
        pts += [(R * 1.05, cy + R * 0.1), (R * 0.7, cy - R * 0.2), (R * 0.45, cy - R * 0.1), (R * 0.15, cy - R * 0.28),
                (-R * 0.2, cy - R * 0.12), (-R * 0.5, cy - R * 0.3), (-R * 0.8, cy - R * 0.05), (-R * 1.05, cy + R * 0.1)]
        cv.poly(pts, fill=hc)
    elif hair == "non_la":
        cv.poly(ellipse_pts(0, cy - R * 0.1, R * 1.04, R * 1.0, 185, 355, 16) + [(R * 0.9, cy - R * 0.1),
                                                                               (-R * 0.9, cy - R * 0.1)], fill=hc)
        cv.poly([(0, cy - R * 1.75), (R * 1.55, cy - R * 0.38), (-R * 1.55, cy - R * 0.38)], fill=(238, 214, 156))
        for k in (0.35, 0.6, 0.82):
            cv.line([(-R * 1.55 * k, cy - R * 1.75 + R * 1.37 * k), (R * 1.55 * k, cy - R * 1.75 + R * 1.37 * k)],
                    (190, 160, 100), 2)
        cv.curve((-R * 0.85, cy - R * 0.4), (0, cy + R * 1.25), (R * 0.85, cy - R * 0.4), INK, 2)

    # eyebrows (after hair so they read on top)
    _draw_brows(cv, s, cy, expr)

    # head props
    for pr in props:
        if pr in HEAD_PROPS:
            HEAD_PROPS[pr](cv, cy, R, s, t)
    if s.get("hat") and s["hat"] in HEAD_PROPS and s["hat"] not in props:
        HEAD_PROPS[s["hat"]](cv, cy, R, s, t)


def _bow(cv, x, y, r, col):
    cv.poly([(x, y), (x - r, y - r * 0.6), (x - r * 0.95, y + r * 0.55)], fill=col)
    cv.poly([(x, y), (x + r, y - r * 0.6), (x + r * 0.95, y + r * 0.55)], fill=col)
    cv.circle(x, y, r * 0.26, fill=col)


def _draw_brows(cv, s, cy, expr):
    R = s["head_r"]
    e = EXPRESSIONS.get(expr, EXPRESSIONS["neutral"])
    dy, tilt = e[2], e[3]
    es = s["eye_scale"]
    ex = R * 0.38
    by = cy - R * (0.28 + 0.06 * (es - 1)) + dy * R
    if s.get("hair") == "bowl":
        by = max(by, cy - R * 0.36)
    elif s.get("hair") == "bowl_grey":
        by = max(by, cy - R * 0.46)
    col = INK
    for side in (-1, 1):
        x0, x1 = side * (ex - R * 0.17), side * (ex + R * 0.17)
        y0 = y1 = by
        if tilt == 1:      # angry: inner end down
            y0 += R * 0.10
            y1 -= R * 0.04
        elif tilt == 2:    # sad: inner end up
            y0 -= R * 0.10
            y1 += R * 0.03
        elif tilt == -1 and side == -1:  # smug: one brow up
            y0 -= R * 0.08
            y1 -= R * 0.12
        cv.line([(x0, y0), (x1, y1)], col, max(2.6, R * 0.085))


def _draw_face(cv, s, cy, expr, mouth_open, look, blink):
    R = s["head_r"]
    e = EXPRESSIONS.get(expr, EXPRESSIONS["neutral"])
    lid, pup_s, _, _, mouth, e_sc = e
    es = s["eye_scale"] * e_sc
    ex, ey = R * 0.38, cy + R * 0.02
    rx, ry = R * 0.16 * es, R * 0.20 * es
    pr = R * 0.085 * math.sqrt(es) * pup_s
    lx, ly = look
    if expr in ("bored",) and ly == 0:
        ly = 0.35
    closure = clamp(max(lid, blink))
    for side in (-1, 1):
        x = side * ex
        if closure >= 0.92:
            cv.line([(x - rx, ey + ry * 0.2), (x + rx, ey + ry * 0.2)], INK, 3)
            continue
        cv.ellipse(x, ey, rx, ry, fill=P.EYE_WHITE, ow=2.6)
        px = x + lx * (rx - pr) * 0.85
        py = ey + ly * (ry - pr) * 0.85
        cv.circle(px, py, pr, fill=INK, outline=None)
        cv.circle(px - pr * 0.35, py - pr * 0.35, pr * 0.3, fill=P.WHITE, outline=None)
        if closure > 0.02:
            cut = ey - ry + 2 * ry * closure
            arc = [(px_, py_) for px_, py_ in ellipse_pts(x, ey, rx + 1.4, ry + 1.4, 180, 360, 20) if py_ <= cut]
            if arc:
                lidpoly = [(x - rx - 1.6, cut)] + arc + [(x + rx + 1.6, cut)]
                cv.poly(lidpoly, fill=s["skin"], outline=None)
                cv.ellipse(x, ey, rx, ry, fill=None, ow=2.6)
                cv.line([(x - rx, cut), (x + rx, cut)], INK, 2.8)
    # cheeks
    if s.get("cheeks"):
        for side in (-1, 1):
            cv.ellipse(side * R * 0.62, cy + R * 0.36, R * 0.13, R * 0.09, fill=P.CHEEK, outline=None)
    # nose
    if s["kind"] == "adult":
        cv.curve((-R * 0.02, cy + R * 0.08), (R * 0.12, cy + R * 0.28), (-R * 0.06, cy + R * 0.3), INK, 2.6)
    else:
        cv.curve((-R * 0.06, cy + R * 0.24), (0, cy + R * 0.3), (R * 0.06, cy + R * 0.24), INK, 2.4)
    if s.get("bandaid"):
        with cv.at(R * 0.6, cy + R * 0.45, 1, rot=-25):
            cv.rect(-R * 0.18, -R * 0.07, R * 0.18, R * 0.07, fill=(240, 210, 170), radius=3, ow=2)
            cv.line([(-R * 0.03, -R * 0.03), (R * 0.03, R * 0.03)], (200, 160, 120), 1.5)
    if s.get("glasses"):
        for side in (-1, 1):
            cv.ellipse(side * ex, ey, R * 0.25, R * 0.22, fill=None, ow=2.6)
        cv.line([(-ex + R * 0.25, ey - 2), (ex - R * 0.25, ey - 2)], INK, 2.6)
    if s.get("mustache"):
        my = cy + R * 0.38
        cv.poly(bezier((0, my - R * 0.06), (-R * 0.35, my - R * 0.12), (-R * 0.48, my + R * 0.12), 8)
                + bezier((-R * 0.48, my + R * 0.12), (-R * 0.2, my + R * 0.04), (0, my + R * 0.06), 6)
                + bezier((0, my + R * 0.06), (R * 0.2, my + R * 0.04), (R * 0.48, my + R * 0.12), 6)
                + bezier((R * 0.48, my + R * 0.12), (R * 0.35, my - R * 0.12), (0, my - R * 0.06), 8),
                fill=(84, 78, 82), ow=2.4)
    _draw_mouth(cv, s, cy, mouth, mouth_open)


def _draw_mouth(cv, s, cy, mouth, m):
    R = s["head_r"]
    my = cy + R * (0.5 if not s.get("mustache") else 0.62)
    mw = R * 0.36
    teeth = s.get("missing_teeth")
    m = clamp(m)
    lipcol = (190, 70, 80) if s.get("lips") else INK
    if m > 0.06 or mouth in ("O",):
        if mouth == "O" and m < 0.3:
            m = 0.55
        if mouth in ("smile", "smirk"):
            h = R * (0.12 + 0.22 * m)
            pts = [(-mw * 0.75, my - R * 0.03)] + ellipse_pts(0, my - R * 0.03, mw * 0.75, h, 0, 180, 16)[::-1]
            pts = ellipse_pts(0, my - R * 0.03, mw * 0.75, h, 0, 180, 16) + [(-mw * 0.75, my - R * 0.03)]
            cv.poly(pts, fill=P.MOUTH, ow=2.8)
            top = my - R * 0.03
        else:
            rx = mw * (0.42 + 0.18 * m)
            ry = R * (0.05 + 0.17 * m)
            cv.ellipse(0, my, rx, ry, fill=P.MOUTH, ow=2.8)
            top = my - ry
            if ry > R * 0.1:
                cv.ellipse(0, my + ry * 0.45, rx * 0.55, ry * 0.4, fill=P.TONGUE, outline=None)
        if teeth:
            _gap_teeth(cv, R, top, mw)
        return
    if mouth == "flat":
        cv.line([(-mw * 0.45, my), (mw * 0.45, my)], lipcol, 3)
    elif mouth == "flat_side":
        cv.line([(-mw * 0.35, my + 1), (mw * 0.5, my - 1.5)], lipcol, 3)
    elif mouth == "smile":
        if teeth:
            pts = ellipse_pts(0, my - R * 0.04, mw * 0.72, R * 0.2, 0, 180, 16) + [(-mw * 0.72, my - R * 0.04)]
            cv.poly(pts, fill=P.MOUTH, ow=2.8)
            _gap_teeth(cv, R, my - R * 0.04, mw)
        else:
            cv.curve((-mw * 0.7, my - R * 0.05), (0, my + R * 0.2), (mw * 0.7, my - R * 0.05), lipcol, 3.2)
    elif mouth == "smirk":
        cv.curve((-mw * 0.5, my + R * 0.02), (mw * 0.1, my + R * 0.08), (mw * 0.65, my - R * 0.1), lipcol, 3.2)
    elif mouth == "frown":
        cv.curve((-mw * 0.6, my + R * 0.08), (0, my - R * 0.12), (mw * 0.6, my + R * 0.08), lipcol, 3.2)
    elif mouth == "frown_flat":
        cv.line([(-mw * 0.5, my + 3), (0, my), (mw * 0.5, my + 3)], lipcol, 3.2)
    elif mouth == "wavy":
        pts = [(-mw * 0.6 + i * mw * 0.2, my + (3 if i % 2 else -3)) for i in range(7)]
        cv.line(pts, lipcol, 2.8)


def _gap_teeth(cv, R, top, mw):
    """Ti's signature: front teeth missing (a gap in the middle of the top row)."""
    th = R * 0.08
    cv.rect(-mw * 0.55, top, -R * 0.07, top + th, fill=P.TEETH, outline=None)
    cv.rect(R * 0.07, top, mw * 0.55, top + th, fill=P.TEETH, outline=None)


# ------------------------------------------------------------------ props
def _hp_notebook_hat(cv, cy, R, s, t):
    with cv.at(0, cy - R * 0.98, 1, rot=-8):
        cv.poly([(-R * 0.95, 0), (0, -R * 0.55), (R * 0.95, 0)], fill=(70, 120, 200))   # open book tent
        cv.line([(0, -R * 0.55), (0, -R * 0.05)], INK, 2)
        cv.line([(-R * 0.6, -R * 0.12), (-R * 0.1, -R * 0.42)], P.WHITE, 2)


def _hp_wig(cv, cy, R, s, t):
    pts = [(-1.15, 0.25), (-1.2, -0.15), (-1.0, -0.6), (-0.6, -0.95), (-0.15, -1.1), (0.3, -1.05), (0.75, -0.85),
           (1.05, -0.5), (1.2, -0.1), (1.15, 0.3), (-1.15, 0.65), (1.15, 0.7), (-1.05, 1.0), (1.05, 1.0)]
    for i, (px, py) in enumerate(pts):
        cv.circle(px * R, cy + py * R, R * (0.33 if i < 10 else 0.27), fill=P.WHITE, ow=2.4)


def _hp_police_cap(cv, cy, R, s, t):
    cv.rect(-R * 0.95, cy - R * 1.25, R * 0.95, cy - R * 0.62, fill=(50, 64, 110), radius=R * 0.25)
    cv.ellipse(0, cy - R * 0.6, R * 1.05, R * 0.14, fill=INK, outline=None)
    cv.circle(0, cy - R * 0.95, R * 0.16, fill=P.GOLD, ow=2.2)


def _hp_flight_cap(cv, cy, R, s, t):
    with cv.at(R * 0.2, cy - R * 0.95, 1, rot=12):
        cv.rect(-R * 0.55, -R * 0.25, R * 0.55, R * 0.12, fill=(40, 70, 140), radius=6)
        cv.line([(-R * 0.55, 0), (R * 0.55, 0)], P.GOLD, 3, round_caps=False)


def _hp_crown(cv, cy, R, s, t):
    y = cy - R * 0.95
    cv.poly([(-R * 0.5, y), (-R * 0.55, y - R * 0.45), (-R * 0.25, y - R * 0.2), (0, y - R * 0.55),
             (R * 0.25, y - R * 0.2), (R * 0.55, y - R * 0.45), (R * 0.5, y)], fill=P.GOLD)


HEAD_PROPS = {"notebook_hat": _hp_notebook_hat, "wig": _hp_wig, "police_cap": _hp_police_cap,
              "flight_cap": _hp_flight_cap, "crown": _hp_crown}


def _p_phone(cv, h, side, s, t):
    x, y = h
    cv.rect(x - 9, y - 26, x + 9, y + 6, fill=INK, radius=4, ow=2)
    cv.rect(x - 6, y - 22, x + 6, y + 1, fill=(140, 210, 255), outline=None, radius=2)
    cv.circle(x, y, s["hand_r"] * 0.9, fill=s["skin"])


def _p_pointer(cv, h, side, s, t):
    x, y = h
    cv.limb([(x - side * 10, y + 14), (x + side * 120, y - 70)], 5, P.WOOD)
    cv.circle(x, y, s["hand_r"], fill=s["skin"])


def _p_gavel(cv, h, side, s, t, swing=0.0):
    x, y = h
    with cv.at(x, y, 1, rot=-side * 30):
        cv.limb([(0, 12), (0, -46)], 7, P.WOOD)
        cv.rect(-20, -62, 20, -40, fill=P.WOOD_DARK, radius=5)
    cv.circle(x, y, s["hand_r"], fill=s["skin"])


def _p_ruler(cv, h, side, s, t):
    x, y = h
    with cv.at(x, y, 1, rot=side * 35):
        cv.rect(-6, -90, 6, 14, fill=(240, 210, 110), radius=2, ow=2.6)
        for k in range(6):
            cv.line([(-6, -80 + k * 15), (0, -80 + k * 15)], INK, 1.6, round_caps=False)
    cv.circle(x, y, s["hand_r"], fill=s["skin"])


def _p_stick(cv, h, side, s, t):
    x, y = h
    cv.limb([(x - side * 8, y + 16), (x + side * 70, y - 110)], 5, (190, 150, 90))
    cv.circle(x, y, s["hand_r"], fill=s["skin"])


def _p_notebook(cv, h, side, s, t):
    x, y = h
    cv.rect(x - 16, y - 34, x + 16, y + 4, fill=(70, 120, 200), radius=3, ow=2.6)
    cv.rect(x - 10, y - 28, x + 8, y - 20, fill=P.WHITE, outline=None)
    cv.circle(x, y, s["hand_r"], fill=s["skin"])


def _p_bowl(cv, h, side, s, t):
    x, y = h
    cv.poly(ellipse_pts(x, y - 14, 22, 18, 0, 180, 12), fill=P.WHITE)
    cv.ellipse(x, y - 14, 22, 5, fill=P.WHITE, ow=2.2)
    cv.circle(x, y, s["hand_r"], fill=s["skin"])


def _p_noodles(cv, h, side, s, t):
    x, y = h
    cv.poly([(x - 18, y - 36), (x + 18, y - 36), (x + 13, y + 2), (x - 13, y + 2)], fill=(250, 240, 220))
    cv.rect(x - 18, y - 30, x + 18, y - 20, fill=P.ACCENT, outline=None)
    cv.circle(x, y, s["hand_r"], fill=s["skin"])


def _p_kite_string(cv, h, side, s, t):
    x, y = h
    cv.line([(x, y), (x + side * 160, y - 260)], (90, 80, 80), 1.5)
    cv.circle(x, y, s["hand_r"], fill=s["skin"])


HAND_PROPS = {"phone": _p_phone, "pointer": _p_pointer, "gavel": _p_gavel, "ruler": _p_ruler, "stick": _p_stick,
              "notebook": _p_notebook, "bowl": _p_bowl, "noodles": _p_noodles, "kite_string": _p_kite_string}


# ------------------------------------------------------------------ dog
def draw_dog(cv, x, y, scale=1.0, flip=False, pose="stand", t=0.0, color=(222, 168, 96), expression="happy",
             mouth_prop=None):
    """Side-view street dog facing right (flip=True faces left). (x,y) = ground under the belly.
    pose: 'stand' | 'run' | 'sit' | 'wag' (stand + fast tail).  mouth_prop: None | 'notebook'."""
    dark = tuple(int(c * 0.72) for c in color)
    run = pose == "run"
    ph = t * 9.0 if run else 0.0
    bob = -abs(math.sin(ph)) * 8 if run else 0.0
    wag = math.sin(t * (18 if pose in ("wag", "sit") or run else 6)) * (16 if pose != "stand" else 8)
    with cv.at(x, y + bob, scale, flip=flip):
        sit = pose == "sit"
        body_y = -48 if not sit else -40
        # tail
        tb = (-40, body_y - 8) if not sit else (-30, -22)
        cv.limb(bezier(tb, (-62, body_y - 30 + wag * 0.3), (-58 + wag * 0.4, body_y - 52 + abs(wag) * 0.2), 8),
                7, color)
        # legs (far pair darker)
        legs = [(-26, 1), (24, 1), (-18, -1), (32, -1)] if not sit else [(-14, 1), (26, 1)]
        for i, (lx, k) in enumerate(legs):
            swing = math.sin(ph + i * 1.6) * 14 if run else 0
            col = color if k > 0 else dark
            if sit and i == 0:
                cv.ellipse(-16, -14, 24, 16, fill=color)
                continue
            cv.limb([(lx, body_y + 8), (lx + swing, -4)], 9, col)
            cv.ellipse(lx + swing + 4, -3, 8, 4.5, fill=col)
        # body
        if sit:
            cv.poly([(-34, -6), (-30, -52), (8, -76), (30, -64), (22, -8)], fill=color)
        else:
            cv.ellipse(0, body_y, 50, 22, fill=color)
            cv.ellipse(-4, body_y + 4, 22, 9, fill=tuple(min(255, c + 20) for c in color), outline=None)
        # head
        hx, hy = (44, body_y - 26) if not sit else (26, -86)
        cv.poly([(hx + 2, hy - 18), (hx - 14, hy + 8), (hx - 4, hy + 14)], fill=dark)  # ear (back)
        cv.circle(hx, hy, 22, fill=color)
        cv.ellipse(hx + 22, hy + 8, 16, 11, fill=tuple(min(255, c + 25) for c in color))
        cv.circle(hx + 36, hy + 3, 5, fill=INK, outline=None)
        cv.poly([(hx - 8, hy - 18), (hx - 26, hy + 2), (hx - 12, hy + 10)], fill=dark)   # ear (front, floppy)
        cv.circle(hx + 8, hy - 5, 4.6, fill=INK, outline=None)
        cv.circle(hx + 6.6, hy - 6.6, 1.5, fill=P.WHITE, outline=None)
        if expression == "happy" and mouth_prop is None:
            cv.curve((hx + 16, hy + 16), (hx + 24, hy + 22), (hx + 32, hy + 15), INK, 2.4)
            cv.ellipse(hx + 24, hy + 24, 5, 8, fill=P.TONGUE, ow=2)
        if mouth_prop == "notebook":
            with cv.at(hx + 30, hy + 20, 1, rot=12):
                cv.rect(-18, -10, 18, 12, fill=(70, 120, 200), ow=2.6)
                cv.poly([(4, -10), (10, -4), (18, -10)], fill=P.WHITE, ow=1.6)   # chewed corner
                cv.line([(-12, 2), (6, 2)], P.WHITE, 2)
    return {"head": cv.to_screen(x + (44 if not flip else -44) * scale, y - 74 * scale)}


# ------------------------------------------------------------------ vendor extras
def draw_vendor(cv, x, y, scale=1.0, flip=False, t=0.0, walking=True, steam=True):
    """Street vendor woman (nón lá) carrying a gánh (shoulder pole with two baskets)."""
    pose = "walk" if walking else "stand"
    a = draw_character(cv, "VENDOR", x, y, scale, pose=pose, t=t, flip=flip)
    s = SPECS["VENDOR"]
    sh_y = y - (s["leg"] + s["torso_h"] - 6) * scale
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
