# Kịch bản video xem trước — Book Spirit

**Ý tưởng:** Từ nỗi nhớ giữa phố thị, quay về tuổi thơ làng quê, tìm lại những câu chuyện trong sách, rồi tới hình ảnh sách được trao từ đời này sang đời khác. Đây là tinh thần của kênh review sách *book-spirit*.

**Thông số:** 1920×1080, 30 fps, tổng dài **33,5 giây**. Mỗi cảnh dài 7 giây, hai cảnh liền nhau mờ chéo vào nhau 1 giây; cảnh cuối giữ thêm 2,5 giây để hiện tiêu đề kết **BOOK SPIRIT** (khoảng 30,7–33,5s). Toàn bộ video mờ dần vào 1,2 giây ở đầu và mờ dần ra 1,2 giây ở cuối.

| Cảnh | Thời gian | Ảnh | Chuyển động máy | Lời dẫn/phụ đề | Gợi ý âm thanh |
|---|---|---|---|---|---|
| 1 | 0–7s | `01-thanh-pho.webp`: cụ già trong căn hộ thành phố lúc hoàng hôn, tay cầm tấm ảnh cũ chụp lũ trẻ trong làng | Zoom vào chậm, lia từ trái sang phải (`in-right`) | Giữa thành phố lên đèn, / có những ký ức chưa bao giờ cũ. | Piano nhẹ vào dần; tiếng phố xa, còi xe vọng lại |
| 2 | 6–13s | `02-ban-hoc.webp`: bàn gỗ cũ có đèn, sách, chén trà, cửa sổ nhìn ra sông quê lúc hoàng hôn | Zoom vào chậm, lia từ phải sang trái (`in-left`) | Một ngọn đèn, một chén trà, vài cuốn sách cũ… / và cả một miền quê trong trí nhớ. | Tiếng phố nhỏ dần; tiếng rót trà, tiếng gió nhẹ ngoài cửa sổ |
| 3 | 12–19s | `03-goc-me.webp`: bốn đứa trẻ ngồi trên bức tường gạch dưới gốc me | Zoom ra chậm, giữ khung ở giữa (`out`) | Ngày ấy, dưới gốc me đầu ngõ, / chúng tôi kể nhau nghe những câu chuyện không hồi kết. | Tiếng ve, tiếng trẻ con cười đùa xa xa; nhạc thêm sáo trúc hoặc đàn guitar |
| 4 | 18–25s | `04-hieu-sach.webp`: hiệu sách quê đầy nắng bên bờ sông | Zoom vào chậm, lia từ phải sang trái (`in-left`) | Lớn lên, tôi tìm lại những câu chuyện ấy / trong từng trang sách. | Tiếng gà gáy, tiếng nước sông; tiếng lật sách sột soạt |
| 5 | 24–33,5s (tiêu đề từ ~30,7s) | `05-trao-sach.webp`: bàn tay trẻ nhỏ và bàn tay người già cùng chạm vào cuốn sách đang mở | Zoom vào chậm, giữ khung ở giữa (`in`) | Có những cuốn sách được trao từ đời này sang đời khác, / như một linh hồn không bao giờ già. → **BOOK SPIRIT** | Tiếng lật sách thật gần; nhạc lên cao trào rồi lắng xuống, để một nốt ngân khi hiện tiêu đề |

*Phụ đề mỗi cảnh hiện sau khi cảnh bắt đầu 0,6s và tắt trước lúc chuyển cảnh. Dấu "/" là chỗ xuống dòng.*

## Cách dựng lại

```bash
python3 video/make_preview.py            # xuất video/preview.mp4
python3 video/make_preview.py out.mp4    # hoặc ghi ra file khác
```

Cần cài `ffmpeg` có hỗ trợ libass. Muốn đổi lời dẫn, ảnh, kiểu chuyển động (`in`, `out`, `in-left`, `in-right`) hay thứ tự cảnh thì sửa danh sách `SCENES` trong `video/make_preview.py`. Muốn đổi tiêu đề kết thì sửa `END_TITLE`. Video hiện chưa có tiếng; cột âm thanh ở trên chỉ là gợi ý cho khâu hậu kỳ.
