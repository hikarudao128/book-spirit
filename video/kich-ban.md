# Kịch bản video xem trước — Book Spirit

**Ý tưởng:** Từ nỗi nhớ giữa phố thị, quay về tuổi thơ làng quê, tìm lại những câu chuyện trong sách, rồi tới hình ảnh sách được trao từ đời này sang đời khác. Đây là tinh thần của kênh review sách *book-spirit*.

**Thông số:** 1920×1080, 30 fps, có tiếng (AAC stereo), tổng dài **40 giây**. Mỗi cảnh dài ít nhất 7 giây và tự kéo dài theo câu đọc; hai cảnh liền nhau mờ chéo 1 giây; cảnh cuối giữ thêm 3,5 giây để hiện tiêu đề kết **BOOK SPIRIT**. Toàn bộ video mờ dần vào 1,2 giây ở đầu và mờ dần ra 1,5 giây ở cuối.

| Cảnh | Thời gian | Ảnh | Chuyển động máy | Lời dẫn/phụ đề | Âm thanh nền |
|---|---|---|---|---|---|
| 1 | 0–7s | `01-thanh-pho.webp`: cụ già trong căn hộ thành phố lúc hoàng hôn, tay cầm tấm ảnh cũ chụp lũ trẻ trong làng | Zoom vào chậm, lia từ trái sang phải (`in-right`) | Giữa thành phố lên đèn, / có những ký ức chưa bao giờ cũ. | Nhạc piano nhẹ vào dần; tiếng phố xa ù ù, một tiếng còi xe vọng lại |
| 2 | 6–15,1s | `02-ban-hoc.webp`: bàn gỗ cũ có đèn, sách, chén trà, cửa sổ nhìn ra sông quê lúc hoàng hôn | Zoom vào chậm, lia từ phải sang trái (`in-left`) | Một ngọn đèn, một chén trà, vài cuốn sách cũ… / và cả một miền quê trong trí nhớ. | Tiếng phố nhỏ dần, thay bằng tiếng gió nhẹ ngoài cửa sổ |
| 3 | 14,1–22,8s | `03-goc-me.webp`: bốn đứa trẻ ngồi trên bức tường gạch dưới gốc me | Zoom ra chậm, giữ khung ở giữa (`out`) | Ngày ấy, dưới gốc me đầu ngõ, / chúng tôi kể nhau nghe những câu chuyện không hồi kết. | Tiếng ve râm ran lên dần |
| 4 | 21,8–28,8s | `04-hieu-sach.webp`: hiệu sách quê đầy nắng bên bờ sông | Zoom vào chậm, lia từ phải sang trái (`in-left`) | Lớn lên, tôi tìm lại những câu chuyện ấy / trong từng trang sách. | Tiếng nước sông, chim lích chích; một tiếng lật sách |
| 5 | 27,8–40s (tiêu đề từ ~37s) | `05-trao-sach.webp`: bàn tay trẻ nhỏ và bàn tay người già cùng chạm vào cuốn sách đang mở | Zoom vào chậm, giữ khung ở giữa (`in`) | Có những cuốn sách được trao từ đời này sang đời khác, / như một linh hồn không bao giờ già. → **BOOK SPIRIT** | Tiếng lật sách gần; nhạc lắng xuống, ngân một nốt khi hiện tiêu đề |

*Lời dẫn được đọc 1 giây sau khi cảnh hiện, phụ đề chạy cùng lời đọc. Dấu "/" là chỗ xuống dòng.*

## Âm thanh

- **Giọng đọc:** giọng nam trầm, ấm, khoảng 130 Hz, đọc chậm thong thả như người kể chuyện review sách. Gốc là gTTS tiếng Việt (chỉ có giọng nữ), được đổi giọng trong `video/soundtrack.py`: hạ âm sắc 12% và hạ cao độ thêm 30% (chỉnh bằng `FORMANT`, `PITCH`), EQ ấm, không vang. File gốc nằm ở `video/audio/narration-NN.mp3`; xóa file nào thì lần dựng sau sẽ tạo lại từ lời dẫn mới (cần mạng). Muốn dùng giọng thật thì ghi âm đè lên đúng tên file và đặt `FORMANT = PITCH = 1`.
- **Nhạc nền:** tự tổng hợp trong `video/soundtrack.py` (vòng hòa âm Fmaj7–Em7–Dm7–Cmaj7, piano rải nốt và nền dây), tự hạ nhỏ khi có lời đọc.
- **Âm thanh môi trường:** cũng tự tổng hợp: phố, gió, ve, nước, chim, lật sách. Đây là bản phác; khi làm bản chính nên thay bằng nhạc và hiệu ứng thật.

## Cách dựng lại

```bash
python3 video/make_preview.py            # xuất video/preview.mp4
python3 video/make_preview.py out.mp4    # hoặc ghi ra file khác
```

Cần cài `ffmpeg` có hỗ trợ libass và `numpy` (thêm `gTTS` nếu phải tạo lại giọng đọc). Muốn đổi lời dẫn, ảnh, kiểu chuyển động (`in`, `out`, `in-left`, `in-right`) hay thứ tự cảnh thì sửa danh sách `SCENES` trong `video/make_preview.py`. Muốn đổi tiêu đề kết thì sửa `END_TITLE`. Video hiện chưa có tiếng; cột âm thanh ở trên chỉ là gợi ý cho khâu hậu kỳ.
