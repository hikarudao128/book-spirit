"""Scene 6 - Idea #3: Put the Parents on Trial.

Beats (all derived from ctx):
  "Idea number three..."        idea card over the sunburst
  "The kids hold a court..."    cut to the plastic-stool courtroom: Judge Hai (cotton-wool wig) behind the
                                bench, Tun + Ti in the gallery, Mui as clerk; a DEFENDANTS -> sign
                                points off-frame on "defendants"
  "Order! Order in the court!"  snap-zoom to Hai, two gavel bangs (gavel sfx + shake)
  Charge number one             a paper charge sheet slides in and builds line by line with the words
  "I made that charge up."      red MADE UP stamp slams onto it; "(but true)" on "true"
  "How do you plead?"           slow pan to the two EMPTY defendant stools; hold the silence
  "They're at work."            cut to Tun, matter-of-fact shrug
  "Then they're guilty..."      cut back to Hai, bang on "dismissed"
  hard cut                      dark, desaturated: four tiny kids before four giant adults (cropped at the
                                chest), one holding a cane, one a ruler. No violence: slow push on the
                                scared faces, then cut to black on "beating".
"""
import math

from lib import palette as P
from lib.backgrounds import SOFT, draw_courtroom, draw_plastic_stool
from lib.characters import draw_character
from lib.core import INK, clamp, ease_in_out, ease_out, lerp, lerp_color, pop, progress, wiggle
from lib.extra_s5_7 import cam_keys, draw_stick, grade, spotlight, stamp, title_backdrop, to_world
from lib.fx import shake, vignette
from lib.text import board, idea_card, label

BENCH_X = 640
HAI_Y = 488                      # Hai stands behind the plank (plank top at y=360); hands at plank height
GALLERY = {"TUN": 100, "TI": 240, "MUI": 380}
STOOL_Y = 680
DEF_X = (1520, 1690)

# giant adults for the "parents found out" shot: (name, x, scale, shirt) - shoulders sit at the top edge
# of the frame so only torsos, hanging arms and the long legs show; they form a dark wall behind the kids
ADULT_TONE = (34, 30, 38)
ADULTS = [("DAD", 150, 4.25), ("MOM", 478, 4.0), ("DAD", 800, 4.1), ("MOM", 1128, 4.3)]
KIDS_SMALL = [("HAI", 470, False), ("MUI", 585, False), ("TUN", 700, True), ("TI", 812, True)]


def beats(ctx):
    L = {i: ctx.line(f"s06_l{i:02d}") for i in range(1, 11)}
    b = dict(L=L)
    b["card"] = L[1].start - 0.3
    b["court"] = L[2].start - 0.12
    b["defendants"] = ctx.find_word(L[2].id, "defendants")
    b["order1"] = L[3].start + 0.05
    b["order2"] = ctx.words(L[3].id)[1][1] + 0.05          # the second "Order"
    b["paper_in"] = L[4].start + 0.1
    b["lying"] = ctx.find_word(L[4].id, "lying")
    b["home"] = ctx.find_word(L[4].id, "we're")
    b["borrow"] = ctx.find_word(L[4].id, "borrow")
    b["made"] = ctx.find_word(L[5].id, "made")
    b["true"] = ctx.find_word(L[5].id, "true")
    b["paper_out"] = L[6].start - 0.25
    b["pan"] = L[6].end + 0.05                 # pan to the empty stools after the question
    b["tun_cut"] = L[7].start - 0.12
    b["hai_cut"] = L[8].start - 0.1
    b["dismissed"] = ctx.find_word(L[8].id, "dismissed") + 0.08
    b["dark"] = L[9].start - 0.35              # hard cut to the giant adults
    b["black"] = ctx.find_word(L[10].id, "beating") + 0.45
    b["bangs"] = [b["order1"], b["order2"], b["dismissed"]]
    return b


def audio_cues(ctx):
    b = beats(ctx)
    cues = [
        {"sfx": "music_bed", "start": 0.0, "dur": b["L"][6].end, "gain": 0.12, "fade_out": 0.4},
        {"sfx": "whoosh", "start": b["card"] + 0.05, "gain": 0.25},
        {"sfx": "whoosh", "start": b["court"], "gain": 0.2},
        {"sfx": "pop", "start": b["defendants"], "gain": 0.25},
        {"sfx": "whoosh", "start": b["paper_in"], "gain": 0.18},
        {"sfx": "thud", "start": b["made"] + 0.12, "gain": 0.45},
        {"sfx": "pop", "start": b["true"], "gain": 0.2},
        {"sfx": "music_bed", "start": b["tun_cut"], "dur": b["dark"] - b["tun_cut"], "gain": 0.1, "fade_out": 0.05},
        {"sfx": "thud", "start": b["dark"], "gain": 0.5},
        {"sfx": "music_sad", "start": b["dark"] + 0.2, "dur": b["black"] - b["dark"], "gain": 0.07,
         "fade_out": 0.3},
    ]
    for tb in b["bangs"]:
        cues.append({"sfx": "gavel", "start": tb, "gain": 0.5})
    return cues


# ------------------------------------------------------------------ helpers
def _gavel(cv, hx, hy, ang, s=1.0, hand=True):
    """Gavel held at (hx, hy); ang = direction of the handle in degrees (0 = right, -90 = up)."""
    a = math.radians(ang)
    dx, dy = math.cos(a), math.sin(a)
    L = 58 * s
    ex, ey = hx + dx * L, hy + dy * L
    cv.limb([(hx - dx * 10 * s, hy - dy * 10 * s), (ex, ey)], 7 * s, P.WOOD)
    with cv.at(ex, ey, s, rot=ang):
        cv.rect(-12, -24, 12, 24, fill=P.WOOD_DARK, radius=5)
        cv.rect(-12, -24, 12, -17, fill=P.GOLD, outline=None)
        cv.rect(-12, 17, 12, 24, fill=P.GOLD, outline=None)
    if hand:
        cv.circle(hx, hy, 8 * s, fill=P.SKIN)
    return ex + dx * 14 * s, ey + dy * 14 * s


def _bang_state(t, bangs):
    """-> (raised 0..1, impact 0..1) for the gavel arm."""
    raised, impact = 0.0, 0.0
    for tb in bangs:
        up = progress(t, tb - 0.32, 0.18)
        down = progress(t, tb - 0.08, 0.08)
        if 0 < up and t < tb + 0.4:
            raised = max(raised, up * (1 - down))
        impact = max(impact, 1 - progress(t, tb, 0.25) if t >= tb else 0)
    return raised, impact


def _court_cam(t, b):
    L = b["L"]
    wide = (540, 400, 1.12)
    hai = (640, 285, 2.0)
    charge = (840, 300, 1.55)
    stools = (1605, 520, 1.55)
    tun = (GALLERY["TUN"] + 68, 566, 2.25)
    keys = [(b["court"], wide), (b["order1"] - 0.25, wide), (b["order1"] - 0.05, hai, 0.2),
            (b["paper_in"] - 0.05, hai), (b["paper_in"] + 0.5, charge, 0.5),
            (b["paper_out"], charge), (L[6].start + 0.2, hai, 0.45),
            (b["pan"], hai), (b["pan"] + 1.1, stools, 1.1)]
    if t >= b["hai_cut"]:
        return (640, 285, lerp(1.9, 2.05, progress(t, b["hai_cut"], 2.0)))
    if t >= b["tun_cut"]:
        return tun
    if t >= b["pan"] + 1.1:      # hold on the empty stools, creeping in
        return (stools[0], stools[1], stools[2] * (1 + 0.06 * progress(t, b["pan"] + 1.1, 2.0)))
    return cam_keys(t, keys)


def _render_court(t, ctx, b, cv):
    L = b["L"]
    cx, cy, z = _court_cam(t, b)
    raised, impact = _bang_state(t, b["bangs"])
    sx, sy = shake(t, 7 * impact, seed=3)
    cam = (cx + sx / z, cy + sy / z, z)
    with cv.camera(*cam):
        # the courtroom set ends at x=1480; extend the wall/floor for the defendants' corner
        wall, floor = (236, 214, 176), (206, 190, 160)
        cv.rect(1400, -200, 2200, 520, fill=wall, outline=None)
        for k in range(14, 22):
            cv.line([(k * 100, -200), (k * 100, 520)], (226, 205, 168), 2)
        cv.rect(1400, 520, 2200, 920, fill=floor, outline=None)
        cv.line([(1400, 520), (2200, 520)], SOFT, 3)
        draw_courtroom(cv, t, sign="COURT", defendants=(), bench_x=BENCH_X)
        # defendants' corner, off to the right
        with cv.at(1605, 420, 1, rot=2):
            cv.rect(-150, -36, 150, 36, fill=(214, 170, 112), ow=3)
            cv.text(0, 2, "DEFENDANTS", 34, INK, "black")
        for x, who in zip(DEF_X, ("MOM", "DAD")):
            draw_plastic_stool(cv, x, STOOL_Y, P.PLASTIC_RED, 1.1)
            label(cv, x, STOOL_Y - 112, who, 22, bg=P.WHITE)
        # wall clock - the only thing moving during the silence
        ckx, cky = 1605, 320
        cv.circle(ckx, cky, 28, fill=P.WHITE)
        a = t * 2 * math.pi / 6
        cv.line([(ckx, cky), (ckx + 20 * math.sin(a), cky - 20 * math.cos(a))], P.ACCENT, 2.6)
        cv.line([(ckx, cky), (ckx + 10, cky - 8)], INK, 3)

        # DEFENDANTS >> pointer sign on "defendants"
        s = pop(t, b["defendants"], 0.3) * (1 - progress(t, b["order1"] - 0.3, 0.2))
        if s > 0.01:
            label(cv, 1010, 300, "DEFENDANTS  >>", 26, fill=P.WHITE, bg=P.ACCENT, scale=s, rot=-3)

        # Judge Hai behind the bench
        striking = impact > 0 and raised <= 0.3
        hai_pose = "fist_up" if raised > 0.3 else ("point" if striking else "hold")
        hai_expr = "angry" if (raised > 0.3 or striking) else "smug"
        look = (0, 0)
        if L[6].start - 0.1 <= t < b["tun_cut"]:
            look = (0.9, 0.1)
            hai_expr = "deadpan" if t > b["pan"] else "smug"
        if b["tun_cut"] <= t < b["hai_cut"]:
            look = (-0.8, 0.2)
        if L[4].start <= t < L[5].start:
            hai_expr = "proud"
        if t >= b["dismissed"] + 0.3:
            hai_expr = "proud"
        a = draw_character(cv, "HAI", BENCH_X, HAI_Y, 1.25, pose=hai_pose, expression=hai_expr, props=("wig",),
                           variant={"hair_color": (250, 250, 247)},   # white cap under the curls: all wig, no black hair
                           mouth_open=ctx.mouth("HAI", t), t=t, look=look)
        hx, hy = to_world(a["hand_r"], cam)
        # bench: plank on two blue stools, re-drawn over Hai, plus a paper JUDGE sign hiding his legs
        draw_plastic_stool(cv, BENCH_X - 120, 470, P.PLASTIC_BLUE, 1.3)
        draw_plastic_stool(cv, BENCH_X + 120, 470, P.PLASTIC_BLUE, 1.3)
        with cv.at(BENCH_X, 440, 1, rot=-2):
            cv.rect(-74, -52, 74, 52, fill=P.PAPER, ow=2.6)
            cv.text(0, 2, "JUDGE", 30, INK, "black")
        cv.rect(BENCH_X - 210, 360, BENCH_X + 210, 392, fill=P.WOOD, radius=4)
        # gavel: in the air for the swing, slammed on the plank, otherwise lying on the bench
        if raised > 0.3:
            _gavel(cv, hx, hy, lerp(-40, -95, raised), 1.25)
        elif striking:
            head = _gavel(cv, hx, hy, 28, 1.25)
            for k in range(5):
                ang = math.radians(-160 + k * 35)
                r0, r1 = 34, 34 + 44 * impact
                ox, oy = head[0], 356
                cv.line([(ox + math.cos(ang) * r0, oy + math.sin(ang) * r0),
                         (ox + math.cos(ang) * r1, oy + math.sin(ang) * r1)], INK, 3.5)
        else:
            # resting: handle in his hand, head lying on the plank
            ang = math.degrees(math.atan2(352 - hy, 60))
            _gavel(cv, hx, hy, ang, 1.25)

        # gallery: Tun, Ti and Mui on red stools
        for nm, x in GALLERY.items():
            draw_plastic_stool(cv, x, STOOL_Y, P.PLASTIC_RED, 1.0)
            kw = dict(pose="sit", expression=None, look=(0.8, -0.3), t=t + x, mouth_open=ctx.mouth(nm, t))
            if nm == "MUI":
                kw.update(pose="sit_chin_on_hand", expression="bored", look=(0.7, -0.3))
            if nm == "TUN" and t >= b["tun_cut"]:
                kw.update(pose="sit_shrug", expression="neutral", look=(0.6, -0.4))
            if nm == "TUN" and t >= L[7].end + 0.1:
                kw.update(pose="sit", expression="happy")
            if t >= b["pan"] and t < b["tun_cut"]:
                kw["look"] = (1, -0.1)
            draw_character(cv, nm, x, STOOL_Y - 66, 1.0, **kw)

    # charge sheet (screen space)
    pin = ease_out(progress(t, b["paper_in"], 0.4))
    pout = progress(t, b["paper_out"], 0.35)
    if pin > 0 and pout < 1:
        px = lerp(1500, 905, pin) + 700 * pout ** 2
        lines = ['"Lying is wrong."', 'ALSO: "We\'re not home!"', "(to the neighbor who", "  wants to borrow money)"]
        n = 0
        for tt, k in ((b["lying"], 1), (b["home"], 2), (b["borrow"] - 0.1, 4)):
            if t >= tt:
                n = k
        with cv.at(px - 905, 0):
            board(cv, 905, 340, 540, 400, "CHARGE No. 1", lines, style="paper", title_size=40, line_size=28,
                  rot=2, reveal=n / len(lines))
            stamp(cv, t, b["made"], 1030, 470, "MADE UP", rot=-12, size=44)
            s = pop(t, b["true"], 0.3)
            if s > 0.01:
                label(cv, 780, 485, "(but true)", 24, fill=P.ACCENT2, bg=P.WHITE, scale=s, rot=-6, ow=2.4)


def _render_dark(t, ctx, b, cv):
    """Four small kids before four giant adults, seen from the kids' height (worm's-eye). The adults are
    near-black silhouettes cropped at the shoulders; one lets a cane hang from his hand, one a ruler.
    Implication only: nobody moves toward anyone. Slow push on the scared faces, cut to black on "beating"."""
    push = ease_in_out(progress(t, b["dark"], b["black"] - b["dark"]))
    cam = (640, lerp(372, 430, push), lerp(1.0, 1.14, push))
    sil = {"skin": ADULT_TONE, "shirt": ADULT_TONE, "pants": ADULT_TONE, "hair_color": ADULT_TONE,
           "shoes": ADULT_TONE, "cheeks": False,
           "polo": False}          # no white collar trim; the work lanyards stay (they're "at work")
    hands = []
    with cv.camera(*cam):
        # dim courtyard wall, a little lighter low down so the dark figures read against it
        for k in range(12):
            y0 = -300 + k * 80
            cv.rect(-300, y0, 1580, y0 + 82, fill=lerp_color((70, 64, 70), (132, 120, 112), k / 11), outline=None)
        cv.rect(-300, 610, 1580, 1100, fill=(96, 88, 84), outline=None)
        cv.line([(-300, 610), (1580, 610)], INK, 3)
        for i, (nm, x, sc) in enumerate(ADULTS):
            breathe = math.sin(t * 1.6 + i * 1.3) * 3
            feet = -24 + 174 * sc + breathe      # shoulders (and the big heads) just above the frame
            a = draw_character(cv, nm, x, feet, sc, pose="stand", colors=sil, t=0, blink=1.0)
            hands.append((to_world(a["hand_r"], cam), to_world(a["hand_l"], cam), a["head_r"] * 11 / 70))
    bg = grade(cv.finish(), sat=0.35, mul=(0.8, 0.77, 0.84))
    cv2 = ctx.canvas((0, 0, 0))
    cv2.paste(bg, 0, 0)      # paste() upsamples the finished frame to the canvas resolution
    with cv2.camera(*cam):
        # the cane hangs from the first adult's right hand, the ruler from the last one's left hand
        (hx, hy), _, hr = hands[0]
        sway = math.sin(t * 1.3) * 1.5
        draw_stick(cv2, hx + 30, hy + 330, length=350, rot=-6 + sway, color=(178, 136, 84), w=9)
        cv2.circle(hx, hy, hr, fill=ADULT_TONE, ow=3)
        _, (lx, ly), hr = hands[3]
        with cv2.at(lx, ly, 1, rot=4 + sway):
            cv2.rect(-11, -6, 11, 250, fill=(226, 200, 120), radius=3, ow=3)
            for k in range(1, 12):
                cv2.line([(-11, k * 21), (-1 if k % 2 else 3, k * 21)], INK, 2, round_caps=False)
        cv2.circle(lx, ly, hr, fill=ADULT_TONE, ow=3)
        for i, (nm, x, fl) in enumerate(KIDS_SMALL):
            jit = wiggle(t, 7, 1.4, seed=i)
            draw_character(cv2, nm, x + jit, 708, 1.22, expression="scared", look=(0, -0.95), flip=fl,
                           pose="stand", t=t + i, blink=0)
    img = grade(cv2.finish(), sat=0.55, mul=(0.86, 0.84, 0.88))
    img = spotlight(img, 640, 590, 330, 190, 0.5, soft=0.9)
    return vignette(img, 0.7)


# ------------------------------------------------------------------ frame
def render_frame(t, ctx):
    b = beats(ctx)
    cv = ctx.canvas(P.WALL_WARM)
    if t < b["court"]:
        title_backdrop(cv, t)
        idea_card(cv, t, b["card"], "IDEA NUMBER THREE", "PUT THE PARENTS ON TRIAL")
        return cv.finish()
    if t < b["dark"]:
        _render_court(t, ctx, b, cv)
        return cv.finish()
    if t < b["black"]:
        return _render_dark(t, ctx, b, cv)
    cv = ctx.canvas((0, 0, 0))
    return cv.finish()
