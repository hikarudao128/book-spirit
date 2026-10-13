#!/usr/bin/env python3
"""Dựng video xem trước từ ảnh trong video/images theo kịch bản video/kich-ban.md.

Mỗi cảnh: hiệu ứng Ken Burns (zoom/pan chậm), chuyển cảnh mờ chéo, phụ đề có fade,
giọng đọc tiếng Việt, nhạc nền và âm thanh môi trường (xem soundtrack.py).
Thời lượng mỗi cảnh co giãn theo độ dài câu đọc.
Cần ffmpeg (có libass), numpy; gTTS nếu chưa có file giọng đọc trong video/audio.
Chạy: python3 video/make_preview.py [output.mp4]
"""
import subprocess
import sys
import tempfile
from pathlib import Path

import soundtrack

ROOT = Path(__file__).resolve().parent
W, H, FPS = 1920, 1080, 30
MIN_SHOT = 7.0  # giây tối thiểu mỗi cảnh
FADE = 1.0  # giây chuyển cảnh
VOICE_DELAY = 1.0  # lời đọc bắt đầu sau khi cảnh hiện
END_HOLD = 3.5  # cảnh cuối giữ thêm cho tiêu đề kết

# (ảnh, hướng chuyển động, lời dẫn)
SCENES = [
    ("01-thanh-pho.webp", "in-right",
     "Giữa thành phố lên đèn,\ncó những ký ức chưa bao giờ cũ."),
    ("02-ban-hoc.webp", "in-left",
     "Một ngọn đèn, một chén trà, vài cuốn sách cũ…\nvà cả một miền quê trong trí nhớ."),
    ("03-goc-me.webp", "out",
     "Ngày ấy, dưới gốc me đầu ngõ,\nchúng tôi kể nhau nghe những câu chuyện không hồi kết."),
    ("04-hieu-sach.webp", "in-left",
     "Lớn lên, tôi tìm lại những câu chuyện ấy\ntrong từng trang sách."),
    ("05-trao-sach.webp", "in",
     "Có những cuốn sách được trao từ đời này sang đời khác,\nnhư một linh hồn không bao giờ già."),
]
END_TITLE = "BOOK SPIRIT"


def zoompan(motion: str, dur: float) -> str:
    n = int(dur * FPS)
    p = f"(on/{n})"  # tiến độ 0→1
    zin, zout = f"1.0+0.12*{p}", f"1.12-0.12*{p}"
    cx, cy = "(iw-iw/zoom)/2", "(ih-ih/zoom)/2"
    z, x, y = {
        "in": (zin, cx, cy),
        "out": (zout, cx, cy),
        "in-right": (zin, f"(iw-iw/zoom)*(0.3+0.4*{p})", cy),
        "in-left": (zin, f"(iw-iw/zoom)*(0.7-0.4*{p})", cy),
    }[motion]
    # Phóng ảnh lên 2x trước khi zoompan để chuyển động mượt, không giật.
    return (f"scale={W*2}:{H*2}:flags=lanczos,"
            f"zoompan=z='{z}':x='{x}':y='{y}':d=1:s={W}x{H}:fps={FPS},"
            f"setsar=1,format=yuv420p")


def ts(t: float) -> str:
    h, rem = divmod(t, 3600)
    m, s = divmod(rem, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def build_ass(cues: list[tuple[float, float, str]], total: float) -> str:
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,DejaVu Serif,50,&H00F4F8FF,&H00FFFFFF,&H00202020,&H90000000,0,1,0,0,100,100,0,0,1,2.2,2,2,120,120,90,1
Style: Title,DejaVu Serif,110,&H00E6F2FF,&H00FFFFFF,&H00303030,&H80000000,1,0,0,0,100,100,14,0,1,3,3,5,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = [f"Dialogue: 0,{ts(a)},{ts(b)},Cap,,0,0,0,,"
             f"{{\\fad(400,500)}}{text.replace(chr(10), '\\N')}" for a, b, text in cues]
    lines.append(f"Dialogue: 0,{ts(total - 3.0)},{ts(total)},Title,,0,0,0,,"
                 f"{{\\fad(800,0)}}{END_TITLE}")
    return head + "\n".join(lines) + "\n"


def main() -> None:
    out = Path(sys.argv[1] if len(sys.argv) > 1 else ROOT / "preview.mp4").resolve()

    voices = soundtrack.voice_durations([text for _, _, text in SCENES])
    vlen = [len(v) / soundtrack.SR for v in voices]
    durs = [max(MIN_SHOT, VOICE_DELAY + v + 1.6) for v in vlen]
    durs[-1] += END_HOLD
    starts = [sum(d - FADE for d in durs[:i]) for i in range(len(durs))]
    total = starts[-1] + durs[-1]
    voice_at = [s + VOICE_DELAY for s in starts]
    cues = [(a - 0.3, a + v + 0.7, text) for a, v, (_, _, text) in zip(voice_at, vlen, SCENES)]

    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"]
    parts = []
    for i, ((img, motion, _), dur) in enumerate(zip(SCENES, durs)):
        cmd += ["-loop", "1", "-framerate", str(FPS), "-t", f"{dur}",
                "-i", str(ROOT / "images" / img)]
        parts.append(f"[{i}:v]{zoompan(motion, dur)}[v{i}]")

    prev = "v0"
    for i in range(1, len(SCENES)):
        parts.append(f"[{prev}][v{i}]xfade=transition=fade:duration={FADE}:offset={starts[i]:.3f}[x{i}]")
        prev = f"x{i}"

    with tempfile.TemporaryDirectory() as tmp:
        ass = Path(tmp) / "subs.ass"
        ass.write_text(build_ass(cues, total), encoding="utf-8")
        wav = Path(tmp) / "mix.wav"
        soundtrack.build(wav, starts, durs, voices, voice_at, total)
        cmd += ["-i", str(wav)]
        parts.append(f"[{prev}]fade=t=in:st=0:d=1.2,fade=t=out:st={total-1.5}:d=1.5,"
                     f"ass={ass}[out]")
        cmd += ["-filter_complex", ";".join(parts), "-map", "[out]", "-map", f"{len(SCENES)}:a",
                "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "192k",
                "-movflags", "+faststart", "-t", f"{total}", str(out)]
        subprocess.run(cmd, check=True)
    print(f"Đã xuất {out} ({total:.1f}s)")
    for i, (s, d) in enumerate(zip(starts, durs), 1):
        print(f"  Cảnh {i}: {s:.1f}–{s + d:.1f}s")


if __name__ == "__main__":
    main()
