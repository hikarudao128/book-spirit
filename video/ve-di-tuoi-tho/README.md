# Video: Cho tôi xin một vé đi tuổi thơ

Video review 6:54, 1080p, 24 khung/giây, dựng hoàn toàn bằng code từ kịch bản
[`../../reviews/cho-toi-xin-mot-ve-di-tuoi-tho/kich-ban-video.md`](../../reviews/cho-toi-xin-mot-ve-di-tuoi-tho/kich-ban-video.md).

| File | Vai trò |
|------|---------|
| `script.js` | Lời thoại + hành động theo từ (cú pháp cue). **Sửa nội dung ở đây.** |
| `engine.js`, `engine.html` | Engine người que: tư thế, biểu cảm, nhép miệng theo âm lượng, camera, phụ đề |
| `props.js` | Đồ vật và bối cảnh (vé tàu, bìa minh họa, nền xóm, văn phòng…) |
| `build_audio.py` | Giọng đọc Google TTS + mốc thời gian từng từ |
| `sfx.py`, `mix.py`, `mux.sh` | Hiệu ứng âm thanh, trộn, ghép |
| `render.mjs` | Render song song bằng Chromium + ffmpeg |

## Dựng lại sau khi sửa

```bash
node -e "require('./script.js');require('fs').writeFileSync('build/script.json',JSON.stringify(SCRIPT.map(s=>s.t?{i:s.i,text:s.t}:{i:s.i,text:null,beat:s.beat})))"
python3 build_audio.py build/script.json      # chỉ gọi TTS lại cho câu đã đổi
python3 sfx.py
node render.mjs --workers 4                   # ~7 phút
python3 mix.py build/narration.wav build/sfx_events.json build/final_audio.wav
bash mux.sh build/video.mp4 build/final_audio.wav out/ve-di-tuoi-tho.mp4
```

Xem thử vài khung: `node render.mjs --stills 100,2000,5000` (ảnh ở `build/stills/`).

## Thay giọng đọc

Giọng hiện tại là giọng tổng hợp. Muốn dùng giọng thật: thu từng câu thành
`build/tts/line_XXX.wav` (48 kHz mono, đánh số theo `i` trong `build/script.json`),
rồi chạy lại từ bước `build_audio.py`; mốc thời gian và nhép miệng tự khớp theo bản thu.
