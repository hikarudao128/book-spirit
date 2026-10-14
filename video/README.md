# Video pipeline: *Give Me a Ticket to Childhood*

This folder builds a flat-2D animated explainer in the OverSimplified style from
`../kich-ban/cho-toi-xin-mot-ve-di-tuoi-tho.md`. It uses Pillow for drawing, Piper for offline
TTS and ffmpeg for encoding. Output is 1280x720 at 24 fps.

## Pipeline

```bash
python3 video/audio/build_audio.py      # TTS -> build/audio/<line_id>.wav + manifest.json (cached)
python3 video/timeline.py               # -> build/timeline.json (per-scene line start/end)
python3 video/render.py --scene 1       # -> build/scenes/scene01.mp4 (video) + scene01_av.mp4 (with audio)
python3 video/render.py --scene 1 --still 4.6,14,20.5   # PNGs for visual QA -> build/stills/
python3 video/render.py --scene 1 --preview             # fast 640x360@12fps check -> scene01_preview.mp4
python3 video/render.py --scene all     # every scene + out/full.mp4
python3 video/gallery.py                # reference sheets of all characters/sets/props -> build/stills/gallery_*.png
```

| File | What it is |
|------|------------|
| `script_lines.json` | Every spoken line in order: `id`, `scene`, `speaker`, `text` (shown/faithful), `pause_after`; optional `tts_text` (pronunciation workaround), `length_scale` (per-line speed), `role` ("AS MOM" …) |
| `audio/voices.json` | Voice casting (Piper model, pitch factor, speed), the pronunciation map (`Mui`→`Mooey` …) and loudness targets |
| `timeline_config.json` | Per-scene `lead_in` / `tail`, and `line_gap_before` (extra silent holds for visual gags) |
| `build/audio/manifest.json` | Each line's `duration`, `peak`, `rms` and `envelope` (mouth RMS per video frame) |
| `build/timeline.json` | `scenes["N"] = {duration, offset, lines:[{id,index,speaker,role,text,start,end,duration}]}` |

To change timing, edit `pause_after` in `script_lines.json` or `timeline_config.json`, then re-run
`timeline.py`; there is no need to rebuild the audio. Editing a line's text or voice needs
`build_audio.py`, which only re-synthesizes lines whose content changed.

Voices are read from `$PIPER_VOICES_DIR`. The default is the session scratchpad `tts/voices`.

## Scene API

Each scene is `scenes/sceneNN.py`:

```python
def render_frame(t: float, ctx: SceneContext) -> PIL.Image.Image   # 1280x720 RGB, t = seconds from scene start
def audio_cues(ctx) -> list[dict]                                  # optional: music / sfx under the dialogue
```

`render_frame` must be a pure function of `t`, with no state carried between frames, because frames
render in parallel across processes. Use seeded randomness only.

`ctx` (`lib/context.py`):

| member | meaning |
|--------|---------|
| `ctx.scene`, `ctx.duration`, `ctx.fps`, `ctx.preview` | basics |
| `ctx.canvas(bg)` | new `Canvas` for this frame, supersampled 2x (1x in preview). **Always use this.** |
| `ctx.lines` | list of `Line(id, index, speaker, text, start, end, duration, role)` |
| `ctx.line("s04_l03")` / `ctx.line(2)` | a line by id or by 0-based index within the scene |
| `ctx.current(t)` | the line being spoken at `t`, or None |
| `ctx.speaking("MUI", t)` | bool. Speakers use script names: `"OLD MUI"`, `"HIS KID"`, `"THE WHOLE CLASS"` … |
| `ctx.mouth("MUI", t)` | 0..1 mouth openness from the line's audio envelope; pass it as `mouth_open=`. Kids also flap during `THE WHOLE CLASS` lines. |
| `ctx.words(id)` | `[(word, start, end)]`, *estimated* word timings (character-weighted, pauses at punctuation) |
| `ctx.find_word(id, "Kites")` | estimated start time of the first word containing that text |
| `line.progress(t)`, `line.active(t)` | helpers |

Cue dicts for `audio_cues`: `{"sfx": name, "start": s, "gain": 0.3, "dur": s, "fade_out": s}`. The names are
`music_bed`, `music_sad`, `record_scratch`, `pop`, `whoosh`, `thud`, `gavel`, `ding`, `shutter`, `boing`,
`tick` and `slap` (`lib/sfx.py`). A good music level under narration is gain about 0.15.

**Derive all timings from `ctx`, never from hard-coded seconds**, so they survive audio changes. Put them
in one `beats(ctx)` function, as `scenes/scene01.py` does.

### Minimal example

```python
from lib import palette as P
from lib.backgrounds import draw_classroom, draw_desks
from lib.characters import draw_character
from lib.core import pop, ease_in_out, progress, lerp
from lib.text import idea_card, speech_bubble

def beats(ctx):
    return {"teacher": ctx.line("s02_l06"), "class": ctx.line("s02_l07")}

def audio_cues(ctx):
    return [{"sfx": "pop", "start": beats(ctx)["class"].start, "gain": 0.3}]

def render_frame(t, ctx):
    b = beats(ctx)
    cv = ctx.canvas(P.WALL_WARM)
    zoom = lerp(1.0, 1.2, ease_in_out(progress(t, b["class"].start, 1.5)))
    with cv.camera(640, 360, zoom):                     # world -> screen camera
        draw_classroom(cv, t, board_lines=["2 x 2 = 4"])
        draw_character(cv, "TEACHER", 1050, 760, 1.0, pose="point", props=("pointer",),
                       mouth_open=ctx.mouth("TEACHER", t), t=t)
        for i, kid in enumerate(["MUI", "HAI", "TUN", "TI"]):
            draw_character(cv, kid, 160 + i * 230, 700, 0.9, outfit="uniform",
                           mouth_open=ctx.mouth(kid, t), t=t + i)
        draw_desks(cv, 610)
    return cv.finish()
```

## Library (`lib/`)

### `core.py`: math and the Canvas
* `W, H, FPS = 1280, 720, 24`, `INK` (the single outline colour), `OW` (default outline width 3.4)
* `clamp, lerp, lerp_pt, lerp_color, progress(t, start, dur)`
* easing: `ease_in, ease_out, ease_in_out, ease_out_back(x, s), ease_out_elastic, bounce`;
  `pop(t, start, dur)` gives a 0 → overshoot → 1 scale for pop-ins; `wiggle(t, freq, amp, seed)`
* `bezier(p0, p1, p2, n)`, `ellipse_pts(cx, cy, rx, ry, a0, a1, n)`
* `Canvas(bg, ss=2)`: all coordinates are logical 1280x720 px; outlines scale with zoom.
  * transforms (context managers): `cv.at(x, y, scale=1, flip=False, rot=0)` and
    `cv.camera(cx, cy, zoom=1, rot=0)` (world point (cx, cy) goes to the frame centre)
  * shapes (outline=INK by default; `outline=None` turns it off; `fill=None` draws a ring):
    `poly(pts, fill, outline, ow, closed)`, `ellipse(cx, cy, rx, ry, …)`, `circle(cx, cy, r, …)`,
    `rect(x0, y0, x1, y1, fill, outline, ow, radius)`, `line(pts, fill, width)`,
    `limb(pts, width, fill)` (an outlined thick stroke), `curve(p0, p1, p2, fill, width)`,
    `text(x, y, s, size, fill, weight, anchor="mm", stroke, stroke_fill)`, `paste(img, x, y)`,
    `overlay(color, alpha)`
  * `to_screen(x, y)`, `view_bounds()`, `finish()` → 1280x720 PIL image

### `palette.py`
Flat warm colours: `SKY_TOP/BOTTOM, SUN, GROUND, HOUSE_COLORS[...], SKIN, HAIR, NAVY, SCARF_RED,
CHALKBOARD, CHALK, PLASTIC_RED/BLUE, CURTAIN, ACCENT (red), ACCENT2 (blue), HIGHLIGHT (yellow),
CARD_BG, GREY_MOOD …`

### `characters.py`
```python
anchors = draw_character(cv, name, x, y, scale=1.0, expression=None, mouth_open=0.0, flip=False,
                         pose="stand", props=(), t=0.0, look=(0, 0), blink=None, outfit=None,
                         nod=0.0, lean=0.0, variant=None, colors=None)
```
* `name`: `MUI, HAI, TUN, TI, OLD_MUI, MOM, DAD, TEACHER, HIS_KID, VENDOR, KID` (a generic classmate;
  recolour it with `colors={"shirt": …}` or `variant={"hair": "bob", "bottom": "dress"}`).
  `SPEAKER_TO_CHAR` maps script speaker names to these keys.
* `(x, y)` is the ground point between the feet. For `sit*` poses it is the seat, and the feet hang
  about 0.9 × leg length below it.
* Sizes at scale 1: kids are about 175 px tall (Hai is taller, with stork legs). Adults are about 420 px,
  roughly 2x a kid, so put them low or off-frame to get the "only see up to the chest" framing.
* `expression`: `neutral, bored, deadpan, happy, smug, shocked, angry, sad, scared, proud`. Each
  character has a default: Mui bored, Hai smug, Tun and Ti happy.
* `mouth_open`: 0..1. Pass `ctx.mouth(SPEAKER, t)`.
* `pose`: `stand, wave, point, point_up, hands_hip, arms_up, shrug, hold, hold_both, present,
  cover_head, chin_on_hand, salute, fist_up, facepalm, walk, run, sit, sit_<armpose>` (for example
  `sit_chin_on_hand`). `walk`/`run` animate from `t`.
* `look=(lx, ly)`: pupil direction, -1..1. `blink=None` gives automatic blinking. `nod` offsets the
  head (use `math.sin(t*8)*4` for Tun's nodding). `lean` is degrees.
* `outfit`: `uniform` (white shirt and red scarf), `police`, `flight`, `principal`, `snow_white`,
  `dad_role` (notebook hat), `work`.
* `props`: head props `notebook_hat, wig, police_cap, flight_cap, crown`; hand props `phone, pointer,
  gavel, ruler, stick, notebook, bowl, noodles, kite_string` (right hand by default; add `"@L"` for the
  left hand, as in `"phone@L"`).
* returns screen-space anchors: `head, head_r, mouth, hand_r, hand_l, top, chest, feet`. Use them for
  speech bubbles, custom props and labels. Inside a camera, convert them back with
  `world = (screen - (640, 360)) / zoom + cam`.
* Signature features: Ti always shows her two missing front teeth when smiling or talking. Hai has a
  band-aid and spiky hair. Tun has huge eyes. Old Mui has Mui's bowl cut gone grey, plus a mustache and belly.

`draw_dog(cv, x, y, scale, flip=False, pose="stand"|"run"|"sit"|"wag", t, color, expression, mouth_prop=None|"notebook")`
draws a side-view street dog facing right.
`draw_vendor(cv, x, y, scale, flip, t, walking=True, steam=True)` draws a street vendor in a nón lá with a gánh.

### `backgrounds.py`
`draw_sky(cv, t, top, bottom, sun=(x,y)|None, clouds)` is screen space. Everything below is drawn in world
coordinates under the current camera:
`draw_alley(cv, t, x0=-400, x1=2000, ground_y=560, seed=3, kites=True, wires=True, step_x=None) -> {"ground_y", "step", "step_low"}`,
`draw_kite(cv, x, y, size, color, t, tail, seed, string_to)`, `draw_sun`, `draw_cloud`, `draw_plant`,
`draw_classroom(cv, t, board_lines, board_title, fan)`, `draw_desks(cv, y, n, x0, gap, w)`,
`draw_dining_room(cv, t, night)`, `draw_dinner_table(cv, x, y, w, dishes)`, `draw_curtain(cv, open_amount, t)`,
`draw_courtroom(cv, t, sign, defendants, bench_x)`, `draw_plastic_stool(cv, x, y, color, scale, label)`,
`draw_gavel(cv, x, y, rot, scale)`, `draw_kitchen(cv, t, night)`,
`draw_book_cover(cv, cx, cy, w=300, h=440, rot, scale, show_english)`, `draw_gradient(cv, top, bottom, y0, y1)`.

### `text.py`
`font(px, weight)`, `text_width`, `wrap_text`, `fit_size`, `wrapped(cv, x, y, s, size, max_w)`,
`label(cv, x, y, s, size, fill, bg, scale, rot)` (pill label),
`board(cv, x, y, w, h, title, lines, style="whiteboard"|"chalk"|"cardboard"|"paper", reveal=0..1)`,
`idea_card(cv, t, start, kicker, title)` (the swinging "IDEA NUMBER ONE" chalkboard),
`name_tag(cv, t, start, name, subtitle, x, y, color, dur)` (freeze-frame intro band),
`speech_bubble(cv, x, y, s, tail=(dx, dy), size, max_w, scale)`, `caption(cv, s, y)`.
The fonts are Inter (regular … black) and render Vietnamese diacritics.

### `fx.py`: post effects on the finished image
`desaturate(img, amount)` (Scene 7 grey), `tint`, `fade(img, amount, color)`, `flash`, `brightness`,
`vignette(img, strength)`, `freeze_frame(img, amount)`, `iris(img, amount, center)`, `letterbox`,
and `shake(t, amp)` → `(dx, dy)` to add to a camera.

### `placeholder.py`
`placeholder_frame(t, ctx, title)` is what the stub scenes use.

## Conventions
* Keep one outline colour (`INK`) and default widths, and draw backgrounds with the softer `SOFT` outline.
* Draw order is back to front: sky, then the set inside `cv.camera`, then characters sorted by `y`,
  then foreground furniture, then screen-space UI (labels, name tags) outside the camera, then post fx.
* Speed budget is under 60 ms per frame per core. `--preview` gives a fast check, and `--still` covers visual QA.
* Don't change `lib/` signatures without updating this README; other scenes depend on them.
  Adding new optional parameters is fine.
