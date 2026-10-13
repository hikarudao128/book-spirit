#!/usr/bin/env python3
"""Giọng đọc bằng Microsoft Edge TTS (vi-VN-NamMinhNeural), kèm mốc thời gian thật của từng từ.

Chạy: python3 build_audio_edge.py build/script.json [--voice vi-VN-NamMinhNeural] [--rate +6%]

Đầu ra giống build_audio.py để engine dùng chung:
  build/narration.wav  48 kHz mono 16-bit
  build/timing.json    {"fps":24,"totalFrames":N,"lines":[{i,start,frames,spoken,wordStarts,amp}]}
Mốc từ lấy từ sự kiện WordBoundary của TTS, không phải ước lượng.
"""
import argparse, asyncio, hashlib, json, os, re, subprocess, sys, wave
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, 'build')
CACHE = os.path.join(BUILD, 'tts_edge')
FPS, SR = 24, 48000
SPF = SR // FPS                       # mẫu âm thanh mỗi khung
LEAD_IN, TAIL = 0.40, 3.0
GAP, GAP_LONG = 0.24, 0.40

def ca_bundle():
    import certifi
    p = '/root/.ccr/ca-bundle.crt'
    if os.path.exists(p):
        certifi.where = lambda: p     # proxy của môi trường dùng CA riêng
ca_bundle()
import edge_tts

def norm(w):
    return re.sub(r'[^\w]', '', w.lower())

async def synth(text, voice, rate, mp3):
    com = edge_tts.Communicate(text, voice, rate=rate, boundary='WordBoundary')
    marks = []
    with open(mp3, 'wb') as f:
        async for ch in com.stream():
            if ch['type'] == 'audio':
                f.write(ch['data'])
            elif ch['type'] == 'WordBoundary':
                marks.append({'t': ch['offset'] / 1e7, 'd': ch['duration'] / 1e7, 'w': ch['text']})
    return marks

def decode(mp3):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', mp3, '-ac', '1', '-ar', str(SR), '-f', 's16le', '-'],
                         check=True, capture_output=True).stdout
    return np.frombuffer(raw, dtype='<i2').astype(np.float32) / 32768.0

def line_audio(entry, voice, rate):
    os.makedirs(CACHE, exist_ok=True)
    key = hashlib.sha1(f'{voice}|{rate}|{entry["text"]}'.encode()).hexdigest()[:16]
    base = os.path.join(CACHE, f'line_{entry["i"]:03d}_{key}')
    if not (os.path.exists(base + '.mp3') and os.path.exists(base + '.json')):
        for attempt in range(5):
            try:
                marks = asyncio.run(synth(entry['text'], voice, rate, base + '.mp3'))
                if not marks:
                    raise RuntimeError('không có mốc từ')
                json.dump(marks, open(base + '.json', 'w'), ensure_ascii=False)
                break
            except Exception as e:
                print(f'  dòng {entry["i"]}: lỗi {e!r}, thử lại', file=sys.stderr)
                asyncio.run(asyncio.sleep(2 ** attempt))
        else:
            sys.exit(f'Không tạo được giọng cho dòng {entry["i"]}')
    marks = json.load(open(base + '.json'))
    audio = decode(base + '.mp3')
    # Cắt khoảng lặng: giữ 60 ms trước từ đầu, 180 ms sau từ cuối
    t0 = max(0.0, marks[0]['t'] - 0.06)
    t1 = min(len(audio) / SR, marks[-1]['t'] + marks[-1]['d'] + 0.18)
    seg = audio[int(t0 * SR):int(t1 * SR)].copy()
    fade = int(0.012 * SR)                        # vào/ra 12 ms để không lụp bụp
    seg[:fade] *= np.linspace(0, 1, fade)
    seg[-fade:] *= np.linspace(1, 0, fade)
    for m in marks:
        m['t'] -= t0
    return seg, marks

def align(words, marks):
    """Gán mốc thời gian TTS cho từng từ của câu (từ = text.split())."""
    toks = [norm(m['w']) for m in marks]
    out, j = [None] * len(words), 0
    for i, w in enumerate(words):
        nw = norm(w)
        if not nw:
            continue
        for k in range(j, min(j + 4, len(toks))):
            if toks[k] == nw or (toks[k] and (toks[k].startswith(nw) or nw.startswith(toks[k]))):
                out[i] = marks[k]['t']; j = k + 1
                break
    # điền chỗ trống bằng nội suy giữa hai mốc đã biết
    known = [(i, t) for i, t in enumerate(out) if t is not None]
    if not known:
        return [0.0] * len(words), len(words)
    miss = 0
    for i in range(len(out)):
        if out[i] is None:
            miss += 1
            prev = max([k for k in known if k[0] < i], default=(0, 0.0), key=lambda k: k[0])
            nxt = min([k for k in known if k[0] > i], default=(len(out), marks[-1]['t'] + marks[-1]['d']), key=lambda k: k[0])
            out[i] = prev[1] + (nxt[1] - prev[1]) * (i - prev[0]) / max(1, nxt[0] - prev[0])
    return out, miss

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('script')
    ap.add_argument('--voice', default='vi-VN-NamMinhNeural')
    ap.add_argument('--rate', default='+6%')
    a = ap.parse_args()
    entries = json.load(open(a.script))
    pieces, lines, cur = [], [], int(round(LEAD_IN * FPS))
    total_miss = 0
    for e in entries:
        if e.get('text'):
            seg, marks = line_audio(e, a.voice, a.rate)
            words = e['text'].split()
            ws, miss = align(words, marks)
            if miss:
                print(f'  dòng {e["i"]}: {miss} từ nội suy mốc')
            total_miss += miss
            frames = int(np.ceil(len(seg) / SPF))
            lines.append({'i': e['i'], 'start': cur, 'frames': frames, 'spoken': True,
                          'wordStarts': [min(frames - 1, max(0, int(round(t * FPS)))) for t in ws]})
            pieces.append((cur, seg))
            end = e['text'].rstrip()
            gap = GAP_LONG if end.endswith(('?', '…', '...')) else GAP
            cur += frames + int(round(gap * FPS))
        else:
            frames = int(round(e['beat'] * FPS))
            lines.append({'i': e['i'], 'start': cur, 'frames': frames, 'spoken': False, 'wordStarts': []})
            cur += frames
    total = cur + int(round(TAIL * FPS))
    narr = np.zeros(total * SPF, dtype=np.float32)
    for start, seg in pieces:
        narr[start * SPF:start * SPF + len(seg)] += seg
    # biên độ theo khung, chuẩn hóa theo bách phân vị 95 của các khung có tiếng
    rms = np.sqrt(np.mean(narr.reshape(total, SPF) ** 2, axis=1))
    ref = np.percentile(rms[rms > 1e-3], 95) if np.any(rms > 1e-3) else 1.0
    ampn = np.clip(rms / ref, 0, 1)
    for l in lines:
        l['amp'] = [round(float(x), 3) for x in ampn[l['start']:l['start'] + l['frames']]]
    peak = float(np.max(np.abs(narr))) or 1.0
    narr = narr / peak * 0.89
    with wave.open(os.path.join(BUILD, 'narration.wav'), 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((narr * 32767).astype('<i2').tobytes())
    json.dump({'fps': FPS, 'totalFrames': total, 'lines': lines}, open(os.path.join(BUILD, 'timing.json'), 'w'))
    print(f'{len(entries)} mục, {sum(1 for l in lines if l["spoken"])} câu nói, '
          f'dài {total / FPS:.1f} s, {total_miss} từ phải nội suy mốc')

if __name__ == '__main__':
    main()
