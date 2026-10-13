# Video: Cho tôi xin một vé đi tuổi thơ

Video review khoảng 7:31, 1080p, 60 khung/giây, dựng hoàn toàn bằng code. Bản hiện tại là bản hài hước, lời thoại đọc được ở
[`../../reviews/cho-toi-xin-mot-ve-di-tuoi-tho/kich-ban-video-hai-huoc.md`](../../reviews/cho-toi-xin-mot-ve-di-tuoi-tho/kich-ban-video-hai-huoc.md)
(bản gốc có ghi chú: [`kich-ban-video.md`](../../reviews/cho-toi-xin-mot-ve-di-tuoi-tho/kich-ban-video.md)).

| File | Vai trò |
|------|---------|
| `script.js` | Lời thoại + hành động theo từ (cú pháp cue). **Sửa nội dung ở đây.** Trường `say` (tùy chọn) là cách đọc cho giọng TTS, phải cùng số chữ với `t` (phụ đề). |
| `qa.mjs` | Kiểm tra tĩnh kịch bản: từ kích hoạt có trong câu, tên hành động/nhân vật/tư thế/đồ vật hợp lệ, `say` khớp số chữ |
| `engine.js`, `engine.html` | Engine người que 60 khung/giây: tư thế nội suy theo khớp, biểu cảm, nhép miệng theo âm lượng, camera, chuyển cảnh, phụ đề |
| `props.js` | Đồ vật và bối cảnh (vé tàu, bìa minh họa, nền xóm, văn phòng…) |
| `build_audio_edge.py` | Giọng Microsoft Edge TTS (vi-VN-NamMinhNeural) + mốc thời gian thật của từng từ. **Dùng mặc định.** |
| `build_audio.py` | Giọng Google TTS, mốc từ ước lượng (dự phòng khi Edge TTS không dùng được) |
| `sfx.py`, `mix.py`, `mux.sh` | Hiệu ứng âm thanh, trộn, ghép |
| `render.mjs` | Render song song bằng Chromium + ffmpeg |

## Dựng lại sau khi sửa

```bash
node qa.mjs                                   # dừng lại sửa nếu có lỗi
node -e "require('./script.js');require('fs').writeFileSync('build/script.json',JSON.stringify(SCRIPT.map(s=>s.t?{i:s.i,text:s.say||s.t}:{i:s.i,text:null,beat:s.beat})))"
python3 build_audio_edge.py build/script.json # chỉ gọi TTS lại cho câu đã đổi (~2 phút nếu làm lại hết)
python3 sfx.py
node render.mjs --stills 100,2000,5000        # xem thử vài khung trước (ảnh ở build/stills/)
node render.mjs --workers 4                   # ~15–20 phút ở 60 khung/giây
python3 mix.py build/narration.wav build/sfx_events.json build/final_audio.wav
bash mux.sh build/video.mp4 build/final_audio.wav out/ve-di-tuoi-tho.mp4
```

Edge TTS cần `edge-tts` bản 7.3 trở lên (`pip install -U edge-tts`); bản cũ bị máy chủ trả 403.

## Thay giọng đọc bằng giọng thật

Thu từng câu thành file riêng, rồi sửa `build_audio_edge.py` (hàm `line_audio`) để đọc file thu
thay vì gọi TTS. Mốc từ khi đó cần ước lượng như `build_audio.py` (hàm `word_starts`),
vì giọng thu không có sự kiện mốc từ.
