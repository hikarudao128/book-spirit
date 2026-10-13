#!/usr/bin/env python3
"""Dựng video xem trước từ ảnh trong video/images theo kịch bản video/kich-ban.md.

Mỗi cảnh: hiệu ứng Ken Burns (zoom/pan chậm), chuyển cảnh mờ chéo, phụ đề có fade.
Cần ffmpeg (có libass). Chạy: python3 video/make_preview.py [output.mp4]
"""
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
W, H, FPS = 1920, 1080, 30
SHOT = 7.0  # giây mỗi cảnh
FADE = 1.0  # giây chuyển cảnh

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


def zoompan(motion: str) -> str:
    n = int(SHOT * FPS)
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


def build_ass(total: float) -> str:
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
    lines = []
    for i, (_, _, text) in enumerate(SCENES):
        start = i * (SHOT - FADE) + 0.6
        end = start + SHOT - FADE - 0.9
        if i == len(SCENES) - 1:
            end = total - 3.2
        lines.append(f"Dialogue: 0,{ts(start)},{ts(end)},Cap,,0,0,0,,"
                     f"{{\\fad(600,500)}}{text.replace(chr(10), '\\N')}")
    lines.append(f"Dialogue: 0,{ts(total - 2.8)},{ts(total)},Title,,0,0,0,,"
                 f"{{\\fad(700,0)}}{END_TITLE}")
    return head + "\n".join(lines) + "\n"


def main() -> None:
    out = Path(sys.argv[1] if len(sys.argv) > 1 else ROOT / "preview.mp4").resolve()
    last_extra = 2.5  # cảnh cuối giữ lâu hơn cho tiêu đề kết
    total = len(SCENES) * (SHOT - FADE) + FADE + last_extra

    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"]
    parts = []
    for i, (img, motion, _) in enumerate(SCENES):
        dur = SHOT + (last_extra if i == len(SCENES) - 1 else 0)
        cmd += ["-loop", "1", "-framerate", str(FPS), "-t", f"{dur}",
                "-i", str(ROOT / "images" / img)]
        zp = zoompan(motion).replace(f"(on/{int(SHOT*FPS)})", f"(on/{int(dur*FPS)})")
        parts.append(f"[{i}:v]{zp}[v{i}]")

    prev = "v0"
    for i in range(1, len(SCENES)):
        offset = i * (SHOT - FADE)
        parts.append(f"[{prev}][v{i}]xfade=transition=fade:duration={FADE}:offset={offset}[x{i}]")
        prev = f"x{i}"

    with tempfile.TemporaryDirectory() as tmp:
        ass = Path(tmp) / "subs.ass"
        ass.write_text(build_ass(total), encoding="utf-8")
        parts.append(f"[{prev}]fade=t=in:st=0:d=1.2,fade=t=out:st={total-1.2}:d=1.2,"
                     f"ass={ass}[out]")
        cmd += ["-filter_complex", ";".join(parts), "-map", "[out]",
                "-c:v", "libx264", "-preset", "medium", "-crf", "20",
                "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-t", f"{total}", str(out)]
        subprocess.run(cmd, check=True)
    print(f"Đã xuất {out} ({total:.1f}s)")


if __name__ == "__main__":
    main()
