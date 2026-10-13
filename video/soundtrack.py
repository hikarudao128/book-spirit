"""Tạo nhạc nền, âm thanh môi trường và trộn với giọng đọc cho video xem trước.

Mọi âm thanh trừ giọng đọc đều được tổng hợp bằng numpy, nên không cần file nhạc ngoài.
Giọng đọc: video/audio/narration-NN.mp3 (gTTS tiếng Việt); thiếu file nào thì tạo bằng gTTS.
"""
import subprocess
from pathlib import Path

import numpy as np

SR = 44100
AUDIO_DIR = Path(__file__).resolve().parent / "audio"
# Giọng vui tươi, tự nhiên: giữ giọng gốc của gTTS (ít xử lý = ít "máy"),
# đọc nhanh hơn một chút và nâng cao độ ~1 nốt, giữ nguyên âm sắc.
TEMPO = 1.04
PITCH = 1.06
rng = np.random.default_rng(7)


# ---------- giọng đọc ----------

def narration_path(i: int, text: str) -> Path:
    path = AUDIO_DIR / f"narration-{i + 1:02d}.mp3"
    if not path.exists():
        from gtts import gTTS  # chỉ cần khi chưa có file

        AUDIO_DIR.mkdir(exist_ok=True)
        gTTS(text.replace("\n", " "), lang="vi").save(str(path))
    return path


def load_voice(path: Path) -> np.ndarray:
    """Giải mã, nâng nhẹ cao độ cho tươi, cắt im lặng hai đầu, EQ sáng.

    Không thêm vang hay nén: giọng khô, gần mic nghe tự nhiên và rõ chữ hơn.
    """
    af = (f"aresample=24000,"
          f"rubberband=pitch={PITCH}:tempo={TEMPO}:formant=preserved:pitchq=quality,"
          "highpass=f=90,equalizer=f=250:t=q:w=1:g=-1.5,equalizer=f=3500:t=q:w=1.5:g=2,"
          "highshelf=f=9000:g=-1,"
          "silenceremove=start_periods=1:start_threshold=-45dB,"
          "areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
          "loudnorm=I=-16:TP=-2")
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(path), "-af", af,
         "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
        check=True, capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32).astype(np.float64)


def voice_durations(texts: list[str]) -> list[np.ndarray]:
    return [load_voice(narration_path(i, t)) for i, t in enumerate(texts)]


# ---------- dụng cụ tổng hợp ----------

def t_axis(sec: float) -> np.ndarray:
    return np.arange(int(sec * SR)) / SR


def lowpass(x: np.ndarray, cutoff: float) -> np.ndarray:
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i, v in enumerate(x):  # IIR một cực; đủ nhanh cho vài chục giây
        acc = (1 - a) * v + a * acc
        y[i] = acc
    return y


def bandnoise(sec: float, lo: float, hi: float) -> np.ndarray:
    """Nhiễu trắng lọc dải bằng FFT."""
    n = int(sec * SR)
    spec = np.fft.rfft(rng.standard_normal(n))
    f = np.fft.rfftfreq(n, 1 / SR)
    spec[(f < lo) | (f > hi)] = 0
    x = np.fft.irfft(spec, n)
    return x / (np.abs(x).max() + 1e-9)


def env_ad(n: int, attack: float, decay: float) -> np.ndarray:
    t = np.arange(n) / SR
    return np.minimum(1, t / attack) * np.exp(-t / decay)


def note_freq(midi: int) -> float:
    return 440.0 * 2 ** ((midi - 69) / 12)


def piano(midi: int, sec: float, vel: float = 1.0) -> np.ndarray:
    """Nốt kiểu piano/celesta mềm: vài bồi âm, tắt dần, bồi cao tắt nhanh hơn."""
    t = t_axis(sec)
    f = note_freq(midi)
    x = np.zeros_like(t)
    for k, amp in [(1, 1.0), (2, 0.35), (3, 0.12), (4, 0.06)]:
        x += amp * np.sin(2 * np.pi * f * k * t) * np.exp(-t * (1.1 + 0.9 * k))
    return vel * x * np.minimum(1, t / 0.008)


def pad(midis: list[int], sec: float) -> np.ndarray:
    """Nền dây ấm: sóng sin hơi lệch tông, vào/ra chậm."""
    t = t_axis(sec)
    x = np.zeros_like(t)
    for m in midis:
        f = note_freq(m)
        for det in (-0.12, 0.0, 0.13):
            x += np.sin(2 * np.pi * f * (1 + det / 100) * t + rng.uniform(0, 6.28))
    fade = np.minimum(1, np.minimum(t / 1.2, (sec - t) / 1.2))
    return x * fade / (3 * len(midis))


def place(dst: np.ndarray, src: np.ndarray, at: float, gain: float = 1.0) -> None:
    i = int(at * SR)
    if i >= len(dst):
        return
    n = min(len(src), len(dst) - i)
    dst[i:i + n] += gain * src[:n]


# ---------- nhạc nền ----------

def pluck(midi: int, sec: float, vel: float = 1.0) -> np.ndarray:
    """Tiếng dây gảy kiểu ukulele (Karplus-Strong)."""
    n = int(sec * SR)
    period = max(2, int(SR / note_freq(midi)))
    buf = rng.uniform(-1, 1, period)
    buf = np.convolve(buf, np.ones(4) / 4, mode="same")  # bớt chói lúc gảy
    out = np.empty(n)
    for i in range(n):
        j = i % period
        out[i] = buf[j]
        buf[j] = 0.996 * 0.5 * (buf[j] + buf[(j + 1) % period])
    return vel * out


def shaker(vel: float) -> np.ndarray:
    n = int(0.09 * SR)
    return vel * bandnoise(0.09, 5000, 11000) * env_ad(n, 0.004, 0.025)


def music(total: float) -> np.ndarray:
    """Nhạc vui tươi: vòng C – G – Am – F, ukulele gảy nhịp nảy ~92 bpm, nền dây, tiếng lắc."""
    out = np.zeros(int(total * SR))
    beat = 60 / 92
    bar = 4 * beat
    chords = [
        ([48, 55, 64], [60, 64, 67, 72]),  # C
        ([43, 55, 62], [59, 62, 67, 71]),  # G
        ([45, 57, 64], [57, 60, 64, 69]),  # Am
        ([41, 57, 65], [57, 60, 65, 69]),  # F
    ]
    # nhịp gảy (đơn vị: phách) kiểu "đập – nảy"
    strum = [0, 1, 1.5, 2.5, 3, 3.5]
    cache: dict[tuple[int, int], np.ndarray] = {}

    def pl(m: int, dur: float) -> np.ndarray:
        key = (m, int(dur * 10))
        if key not in cache:
            cache[key] = pluck(m, dur)
        return cache[key]

    t, k = 0.0, 0
    while t < total - 3.0:  # chừa chỗ cho hợp âm kết
        low, high = chords[k % len(chords)]
        place(out, pad(low, bar + 1.0), t, 0.10)
        place(out, piano(low[0], 2.0, 0.35), t)
        place(out, piano(low[0], 1.5, 0.22), t + 2 * beat)
        for s_i, b in enumerate(strum):
            vel = 0.30 if b == int(b) else 0.20
            for q, m in enumerate(high):  # quét dây lệch nhau vài ms như gảy thật
                place(out, pl(m, 1.2), t + b * beat + q * 0.012, vel)
        # giai điệu chuông nhẹ ở phách 1 và 3 của mỗi ô nhịp chẵn
        if k % 2 == 1:
            place(out, piano(high[-1] + 12, 1.5, 0.18), t)
            place(out, piano(high[-2] + 12, 1.5, 0.14), t + 2 * beat)
        for h in range(8):
            place(out, shaker(0.08 if h % 2 else 0.04), t + h * beat / 2)
        t += bar
        k += 1
    # kết: hợp âm C ngân trên tiêu đề
    for m in (60, 64, 67, 72, 76):
        place(out, pluck(m, 3.0, 0.3), total - 3.0 + (m - 60) * 0.004)
        place(out, piano(m + 12, 4.0, 0.12), total - 3.0)
    return out / (np.abs(out).max() + 1e-9)


# ---------- âm thanh môi trường ----------

def amb_city(sec: float) -> np.ndarray:
    hum = bandnoise(sec, 40, 400) * 0.7
    t = t_axis(sec)
    swell = 0.6 + 0.4 * np.sin(2 * np.pi * 0.11 * t)
    honk = np.zeros_like(t)
    place(honk, np.sin(2 * np.pi * 420 * t_axis(0.35)) * env_ad(int(0.35 * SR), 0.03, 0.15), sec * 0.55)
    return hum * swell + 0.05 * lowpass(honk, 900)


def amb_wind(sec: float) -> np.ndarray:
    t = t_axis(sec)
    return bandnoise(sec, 200, 1400) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.15 * t) ** 2)


def amb_cicada(sec: float) -> np.ndarray:
    t = t_axis(sec)
    buzz = bandnoise(sec, 4200, 6500)
    pulse = (0.5 + 0.5 * np.sin(2 * np.pi * 38 * t)) ** 3
    swell = 0.3 + 0.7 * np.clip(np.sin(2 * np.pi * t / sec * 1.5), 0, 1)
    return buzz * pulse * swell


def amb_water(sec: float) -> np.ndarray:
    t = t_axis(sec)
    base = bandnoise(sec, 300, 2500)
    lap = 0.55 + 0.45 * np.sin(2 * np.pi * 0.35 * t + np.sin(2 * np.pi * 0.07 * t) * 3)
    # tiếng chim lích chích thưa thớt
    birds = np.zeros_like(t)
    for at in np.arange(0.8, sec - 0.5, 2.3):
        n = int(0.09 * SR)
        tt = np.arange(n) / SR
        chirp = np.sin(2 * np.pi * (3200 + 9000 * tt) * tt) * np.hanning(n)
        for r in range(3):
            place(birds, chirp, at + r * 0.13)
    return base * lap + 0.35 * birds


def page_turn() -> np.ndarray:
    n = int(0.55 * SR)
    x = bandnoise(0.55, 1500, 7000)
    t = np.arange(n) / SR
    flutter = 0.6 + 0.4 * np.sin(2 * np.pi * 23 * t)
    return x * flutter * np.sin(np.pi * t / 0.55) ** 2


def faded(x: np.ndarray, fade: float) -> np.ndarray:
    n = len(x)
    f = int(fade * SR)
    env = np.ones(n)
    ramp = np.linspace(0, 1, f)
    env[:f] *= ramp
    env[-f:] *= ramp[::-1]
    return x * env


# ---------- trộn ----------

def build(path: Path, starts: list[float], durs: list[float], voices: list[np.ndarray],
          voice_at: list[float], total: float) -> None:
    n = int(total * SR)
    mix_music = music(total)
    amb = np.zeros(n)
    makers = [(amb_city, 0.10), (amb_wind, 0.07), (amb_cicada, 0.05),
              (amb_water, 0.07), (amb_wind, 0.04)]
    for (mk, g), st, d in zip(makers, starts, durs):
        place(amb, faded(mk(d), 1.0), st, g)
    sfx = np.zeros(n)
    place(sfx, page_turn(), starts[3] + 2.0, 0.10)
    place(sfx, page_turn(), starts[4] + 0.4, 0.14)
    place(sfx, page_turn(), starts[4] + 1.0, 0.09)

    voice = np.zeros(n)
    duck = np.zeros(n)
    for v, at in zip(voices, voice_at):
        place(voice, v, at)
        i, j = int((at - 0.3) * SR), int((at + len(v) / SR + 0.4) * SR)
        duck[max(i, 0):min(j, n)] = 1
    k = int(0.4 * SR)  # làm mềm đường hạ nhạc
    duck = np.convolve(duck, np.ones(k) / k, mode="same")

    mix = mix_music * (0.17 - 0.10 * duck) + amb * (1 - 0.4 * duck) + sfx + 0.95 * voice
    t = np.arange(n) / SR
    mix *= np.minimum(1, np.minimum(t / 1.2, (total - t) / 1.8))
    mix /= max(1.0, np.abs(mix).max() / 0.95)
    pcm = (np.clip(mix, -1, 1) * 32767).astype("<i2")
    stereo = np.repeat(pcm[:, None], 2, axis=1)
    import wave

    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(stereo.tobytes())

