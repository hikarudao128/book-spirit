# Phân tích hình ảnh và animation của kênh Vui Vẻ

Tài liệu này mổ xẻ phần **hình ảnh** trong 4 video của kênh **Vui Vẻ**: cách thiết kế nhân vật, dựng khung cảnh, chọn hình minh họa, dẫn dắt mắt người xem và làm animation. Mục tiêu là rút ra một "ngôn ngữ hình" dùng được cho video review sách. Phần nội dung và lời dẫn của video review đã có ở [`huong-dan-review-sach.md`](huong-dan-review-sach.md); tài liệu này bổ sung phần hình. Template storyboard dùng ngay ở [`../templates/storyboard-video-review-sach.md`](../templates/storyboard-video-review-sach.md).

| Video | Đăng | Dài | Lượt xem* | Kiểu nội dung |
|-------|------|-----|-----------|---------------|
| [Tất cả các quyển sách self-help bị chửi mà tôi biết (có Đắc Nhân Tâm)](https://www.youtube.com/watch?v=rFGNYlorK6o) | 15/01/2025 | 27:29 | 1,3 triệu | Điểm nhanh ~40 cuốn sách |
| [Tất cả các truyện ngắn mà bạn được học trong sách giáo khoa](https://www.youtube.com/watch?v=QICWDoSEklM) | 20/05/2025 | 15:05 | 1,6 triệu | Kể lại 17 truyện |
| [Tất cả các thiên tài khủng nhất của thế giới (Phần 1)](https://www.youtube.com/watch?v=2246gxgBcAs) | 30/08/2025 | 16:06 | 2,9 triệu | Tiểu sử 9 nhân vật |
| [12 thuyết tâm lý học hữu ích trong 19 phút](https://www.youtube.com/watch?v=uqXylqA918Y) | 27/05/2026 | 18:57 | 1,7 triệu | Giải thích 12 lý thuyết |

\* Lượt xem tại thời điểm tải dữ liệu (13/10/2026).

Transcript (phụ đề tự động, có lỗi chính tả, có mốc thời gian 30 giây) nằm trong [`../sources/transcripts/`](../sources/transcripts/).

## 0. Nguồn dữ liệu và giới hạn

Môi trường làm việc **không tải được file video** (YouTube trả 403 cho luồng video). Phân tích dựa trên:

- **Storyboard của YouTube**: ảnh xem trước của thanh tua, **1 khung mỗi ~10 giây**, độ phân giải 160×90. Tổng 471 khung cho 4 video.
- **Thumbnail** 1280×720 của cả 4 video.
- **Phụ đề tự động**, dùng để khớp lời thoại với từng khung hình.

Hệ quả:

- **Chắc chắn**: thiết kế nhân vật, bảng màu, bố cục, loại hình minh họa, nhịp đổi cảnh ở mức 10 giây, cấu trúc cả video.
- **Suy luận từ ảnh tĩnh, chưa kiểm chứng bằng chuyển động**: kiểu animation, cách chuyển cảnh, chuyển động camera. Các mục này ghi rõ *(suy luận)*. Muốn xác nhận thì xem trực tiếp các mốc thời gian được dẫn link.

---

## 1. Nhân vật dẫn chuyện: một mascot dễ nhận ra ở 48 pixel

Cả 4 video do cùng một nhân vật dẫn: chàng trai tóc hồng. Đây là "gương mặt" của kênh, xuất hiện trong gần như mọi khung hình trên nền trắng.

### Giải phẫu nhân vật

| Bộ phận | Thiết kế | Vì sao hiệu quả |
|---------|----------|-----------------|
| **Tóc** | Hồng đậm, dựng nhọn như ngọn lửa, chiếm 1/3 chiều cao đầu | Mảng màu lớn nhất, nhận ra được ngay cả ở storyboard 48×27 pixel |
| **Mặt** | Khối gần vuông, hơi vát cằm, màu da hồng nhạt, không tai, không mũi | Hình học đơn giản, dễ vẽ lại ở mọi góc, ít chi tiết phải animate |
| **Mắt** | Hai vạch đứng hoặc hai chấm tròn | Đổi mắt là đổi cảm xúc (xem bảng biểu cảm) |
| **Miệng** | Hình hạt đậu đỏ, đổi hình theo câu thoại | Gánh phần lớn biểu cảm |
| **Thân** | Áo phông vàng, **túi đeo chéo tím** | Vàng–tím là cặp màu bổ túc, nổi trên nền trắng; túi chéo là chi tiết "chữ ký" |
| **Tay chân** | Que mảnh, bàn tay tròn, giày trắng | Thân nhỏ để đầu và tay (cử chỉ) nổi bật |
| **Nét** | Viền đen dày, đều, không đổ bóng | Tách nhân vật khỏi mọi loại nền, kể cả ảnh chụp lộn xộn |

**Bảng màu nhận diện:** hồng (tóc) · vàng (áo) · tím (túi) · trắng (nền). Ba màu này lặp lại cả trên thumbnail.

### Hai cỡ hình (suy luận: cùng một rig, hai tỉ lệ)

- **Toàn thân, nhỏ**, đứng ở 1/3 trái hoặc phải khung hình: dùng khi đang giải thích, chừa chỗ cho hình minh họa.
- **Cận mặt, lớn**, chỉ thấy đầu và vai: dùng khi phản ứng mạnh, đùa, chốt ý.

Ví dụ: video tâm lý học, [~1:09–1:29](https://www.youtube.com/watch?v=uqXylqA918Y&t=69s): cùng một phòng khách, khung đầu nhân vật nhỏ ngồi sofa, khung sau cận mặt đang hét, khung sau nữa cận mặt cạnh nhân vật nữ. Cắt từ toàn cảnh vào cận cảnh để nhấn cảm xúc.

### Thư viện biểu cảm và tư thế

Đếm qua storyboard, nhân vật chỉ dùng một bộ tư thế nhỏ, lặp đi lặp lại:

| Tư thế tay | Dùng khi |
|------------|----------|
| Giơ hai ngón (peace) | Mở đầu, chào, chuyển mục vui |
| Chỉ tay lên / giơ một ngón | Nêu ý, "bài học thứ nhất…" |
| Một tay chìa ra phía hình minh họa | Giới thiệu hình bên cạnh (tư thế phổ biến nhất) |
| Nhún vai hai tay ngửa | "Thế đấy", chuyện vô lý |
| Chống cằm / tay xoa đầu | Nghi ngờ, suy nghĩ |
| Ra dấu OK | Đồng ý, khen |
| Khoanh tay | Chê, phán xét |
| Chỉ thẳng vào người xem | Kêu gọi, nói "bạn" |
| Giơ hai nắm tay lên trời | Ăn mừng |

| Biểu cảm mắt/miệng | Nghĩa |
|--------------------|-------|
| Mắt vạch, miệng mở | Trung tính, đang nói |
| Mắt nhắm cong, miệng cười | Đắc ý, kể chuyện vui |
| Mắt "3 3" (như thumbnail video tâm lý học) | Ngơ ngác, sốc |
| Mắt lườm, một mày nhướn | Mỉa mai, "thật à?" |
| Mắt chữ X, miệng méo | Đau, xấu hổ |
| Nước mắt chảy, lau khăn | Cảm động (giả) |

**Bài học:** không cần nhiều tư thế. Khoảng 10 tư thế tay × 6 kiểu mắt/miệng đã đủ cho video gần 30 phút. Cái làm video sống động là **đổi tư thế liên tục theo nhịp câu nói**, không phải độ phức tạp của từng tư thế.

### Phụ kiện = vai diễn

Nhân vật giữ nguyên đầu và màu, chỉ thêm một món đồ để đổi vai:

| Phụ kiện | Vai | Ví dụ |
|----------|-----|-------|
| Kính tròn + cuốn sách xanh | "Người đọc / người tra cứu" | Mở đầu video thiên tài, video SGK; mọi lúc nói "tôi đọc được là…" |
| Ngồi trước máy tính bàn | "Tôi tìm trên mạng" | Video tâm lý học, lặp lại nhiều lần |
| Khăn quàng đỏ, áo đồng phục | Học sinh | Thumbnail và nhiều cảnh video SGK |
| Áo blouse + ống nghe | Bác sĩ, nhà nghiên cứu | Video tâm lý học |
| Vest, kính đen | "Làm sang" | Video tâm lý học |
| Thân béo, ăn burger | Phiên bản "tương lai tệ" của chính mình | Video tâm lý học, bong bóng suy nghĩ |
| Chăn quấn, chữ ZZZ | Ngủ | Video self-help, phần *Atomic Habits* |

**Hai phiên bản cùng lúc:** khi so sánh, nhân vật được nhân đôi (một bản khóc, một bản cười; một bản vest, một bản kính đen). Không cần vẽ thêm nhân vật mới để thể hiện "trước/sau" hay "người này/người kia".

---

## 2. Nhân vật phụ: chibi hóa có quy tắc

### Người thật: ảnh trước, chibi sau

Video thiên tài lặp đúng một quy trình cho mỗi người:

1. **Ảnh tư liệu thật** (đen trắng, có chú thích tên) để người xem nhận diện.
2. **Phiên bản chibi** đứng cạnh hoặc thay thế, giữ **1–2 đặc điểm nhận diện mạnh nhất**: Einstein tóc bạc bù xù + thè lưỡi; Darwin râu trắng dài; Newton tóc giả xoăn; Leonardo mũ nồi xanh + râu; Marie Curie búi tóc nâu, váy đen.
3. Từ đó về sau, **chỉ dùng chibi** để diễn các tình huống trong đời người đó.

Ví dụ: [Einstein ~0:30](https://www.youtube.com/watch?v=2246gxgBcAs&t=30s): ảnh thật bên trái, chibi bên phải. Ngay sau đó chibi Einstein bị dán lên ảnh trường đại học Thụy Sĩ, với tờ giấy "EXAM [FAIL]" ([~1:09](https://www.youtube.com/watch?v=2246gxgBcAs&t=69s)).

### Nhân vật hư cấu: một chi tiết là đủ

Video SGK chibi hóa nhân vật văn học, mỗi người một "móc nhận diện":

| Nhân vật | Chi tiết nhận diện |
|----------|--------------------|
| Thần chết | Đầu lâu, áo choàng đen có cánh |
| Ông lão đánh cá | Râu bạc, ôm con cá vàng |
| Lão Hạc | Áo nâu vá, đứng cạnh con chó vàng |
| Chí Phèo | Mặt đầy sẹo |
| Chị Dậu | Khăn mỏ quạ |
| Mị (Vợ chồng A Phủ) | Khăn đội đầu và vòng bạc H'Mông |
| Người họa sĩ (Chiếc lá cuối cùng) | Mũ nồi, tạp dề dính sơn |

Tạo hình chung: **đầu to, thân nhỏ, mắt chấm, cùng nét viền đen** với nhân vật chính, để mọi nhân vật thuộc cùng một thế giới.

### Quần chúng: tối giản tối đa

Đám đông (học sinh trong thí nghiệm, lính, dân làng) được vẽ đầu tròn trên thân trụ, gần như không có tay, cùng một mẫu nhân bản nhiều lần. Ví dụ: thí nghiệm chia nhóm của Tajfel, [~9:53–10:33](https://www.youtube.com/watch?v=uqXylqA918Y&t=593s): một hàng học sinh đồng phục, phía trên hiện các con số điểm đổi màu xanh/đỏ theo lời kể.

### Dàn nhân vật lặp lại

Video tâm lý học (2026) có thêm **chó vàng và mèo tím** xuất hiện ở nhiều chương, đứng cạnh nhân vật chính. Đây là dấu hiệu kênh đang xây "vũ trụ nhân vật" để người xem quen mặt qua nhiều video.

---

## 3. Khung cảnh: ba tầng nền

Mỗi khung hình thuộc một trong ba kiểu nền. Đổi kiểu nền là một cách báo cho người xem rằng "chế độ" của video vừa đổi.

| Tầng | Mô tả | Dùng khi | Chi phí làm |
|------|-------|----------|-------------|
| **A. Nền trắng trống** | Chỉ nhân vật + 1 hình minh họa hoặc chữ | Người dẫn đang giải thích, bình luận | Thấp nhất |
| **B. Collage: ảnh thật làm nền** | Ảnh chụp/ảnh mạng full khung, nhân vật vẽ dán lên | Đặt nhân vật vào bối cảnh có thật (trường đại học, căn phòng bừa bộn, vụ nổ hạt nhân) | Thấp |
| **C. Cảnh vẽ hoàn chỉnh** | Bối cảnh vẽ tay tông pastel, phẳng, ít chi tiết | Kể chuyện, tái hiện thí nghiệm | Cao, nhưng **tái sử dụng được** |

Tỉ lệ khung hình nền trắng (đo tự động: khung có trên 60% điểm ảnh gần trắng):

| Video | Đăng | Khung nền trắng |
|-------|------|-----------------|
| Self-help | 01/2025 | 59% |
| Truyện SGK | 05/2025 | 36% |
| Thiên tài | 08/2025 | 77% |
| Tâm lý học | 05/2026 | 57% |

Video SGK có ít nền trắng nhất vì bản chất là **kể chuyện**, cần cảnh vẽ. Video self-help và thiên tài chủ yếu là **giải thích**, nên nền trắng + ảnh thật là đủ.

### Đặc điểm cảnh vẽ (tầng C)

- **Phẳng, pastel, nét mảnh hơn nhân vật.** Nền không bao giờ tranh chú ý với nhân vật.
- **Phối cảnh một điểm, nhìn thẳng**, như sân khấu: phòng khách sofa đỏ, phòng thí nghiệm tường xám, cung điện hồng có bậc thang, lớp học bảng đen.
- **Tái sử dụng**: phòng khách sofa đỏ xuất hiện ít nhất 5 lần trong video tâm lý học, mỗi lần một góc cắt (toàn cảnh, trung cảnh, cận cảnh). Phòng thí nghiệm xám dùng cho 3 thí nghiệm khác nhau (Little Albert, thí nghiệm chia nhóm, chó trong chuồng).
- **Màu theo cảm xúc**: *Cô bé bán diêm* ([~1:09](https://www.youtube.com/watch?v=QICWDoSEklM&t=69s)) dùng đêm xanh tím, đốm sáng ấm từ que diêm; *Người mẹ và thần chết* đi từ làng sáng sang rừng xanh rồi hang tối tím khi gặp thần chết ([0:10–0:40](https://www.youtube.com/watch?v=QICWDoSEklM&t=10s)); *Ông lão đánh cá* biển xanh ngọc.

### Collage (tầng B): luật dán nhân vật lên ảnh

- Nhân vật vẽ **luôn có viền đen dày** nên không bị chìm trong ảnh chụp.
- Ảnh nền thường **đúng nghĩa đen của câu nói**: nói "nằm ngủ trên đống quần áo" thì nhân vật quấn chăn được dán lên ảnh căn phòng bừa bộn thật ([~2:48](https://www.youtube.com/watch?v=rFGNYlorK6o&t=168s)).
- Ảnh nền là **ảnh chụp thực tế, không chỉnh sửa cầu kỳ**, đôi khi chỉ là ảnh mạng chất lượng thấp. Cái hài đến từ độ lệch giữa nhân vật hoạt hình và thế giới thật.

---

## 4. Từ vựng hình ảnh: mỗi danh từ một hình

Quy tắc xuyên suốt: **khi lời thoại nhắc đến một thứ cụ thể, thứ đó hiện lên màn hình.** Phân loại các hình minh họa đã gặp:

| Loại hình | Ví dụ | Vai trò |
|-----------|-------|---------|
| **Bìa sách dạng huy hiệu tròn** | Lưới bìa sách trong thumbnail và đầu mỗi mục của video self-help | Nhận diện sách, làm "mục lục" |
| **Sơ đồ chụp từ sách** | Vòng "Identity – Habits – Environment", bảng "The four stages of habit" ([~0:50–1:10](https://www.youtube.com/watch?v=rFGNYlorK6o&t=50s)) | Bằng chứng: "sách nói thế này" |
| **Câu trích nguyên văn** | "We don't rise to the level of our goals…" hiện chữ trên nền trắng ([~0:40](https://www.youtube.com/watch?v=rFGNYlorK6o&t=40s)) | Trích dẫn |
| **Chữ động (kinetic text) từ khóa** | "KHAO KHÁT" ([~1:39](https://www.youtube.com/watch?v=rFGNYlorK6o&t=99s)), "HELICOPTER PARENT", "Năng lực – Gắn kết – Tự chủ" bay quanh nhân vật ([~14:14](https://www.youtube.com/watch?v=uqXylqA918Y&t=854s)) | Đóng đinh thuật ngữ |
| **Meme, ảnh văn hóa đại chúng** | Squidward ngủ, thân hình cơ bắp "như anh này", logo BlackBerry gắn mắt lồi ([~6:27](https://www.youtube.com/watch?v=rFGNYlorK6o&t=387s)) | Gây cười, kéo về trải nghiệm quen thuộc |
| **Ảnh tư liệu** | Ảnh đen trắng nhà khoa học, ảnh gia đình Curie, ảnh thí nghiệm Little Albert | Độ tin cậy |
| **Ảnh phim chuyển thể** | Ảnh đen trắng phim *Làng Vũ Đại ngày ấy* cho Chí Phèo, Chị Dậu | Nối sách với ký ức thị giác của khán giả |
| **Biểu tượng hiệu ứng** | ZZZ, tia sét giận, giọt mồ hôi, bong bóng suy nghĩ, kính lấp lánh | Thay cho animation phức tạp |

### Hình minh họa diễn câu đùa

Phần lớn tiếng cười đến từ việc **hình minh họa nghĩa đen một câu nói ví von**:

- "Muốn có cơ thể **của anh này**" → ảnh một người cơ bắp.
- "BlackBerry… giờ không biết **đang ở đâu** rồi" → logo BlackBerry có mắt ngơ ngác.
- "Táo rơi trúng đầu Newton" → táo rơi trúng nhân vật chính đang nằm, Newton đứng nhìn.

**Bài học cho review sách:** viết kịch bản xong, gạch chân mọi danh từ cụ thể và mọi phép so sánh. Mỗi chỗ gạch chân là một hình cần tìm hoặc vẽ.

---

## 5. Flow hình ảnh: dẫn mắt người xem đi đâu

### 5.1. Thumbnail = mục lục = bản đồ của video

Cả 4 thumbnail dùng **một bố cục**:

- Nhân vật chính (hoặc một nhân vật tiêu biểu như Leonardo) **cận mặt, chiếm 1/3 trái**, có viền trắng tách nền, che một phần lưới phía sau.
- Phía sau là **lưới 3×5 hoặc 3×6 huy hiệu tròn**, mỗi huy hiệu một mục (bìa sách / chân dung chibi), có chú thích tên.
- Biểu cảm nhân vật = cảm xúc chủ đạo: ngạc nhiên khi đọc *Đắc Nhân Tâm*, mắt "3 3" ngơ ngác với tâm lý học, cười tự tin với truyện SGK.

Bên trong video, **lưới huy hiệu này xuất hiện lại** ở mở đầu và ở các điểm chuyển mục. Video self-help quay về lưới bìa sách khi chuyển từ cuốn này sang cuốn khác ([~3:17](https://www.youtube.com/watch?v=rFGNYlorK6o&t=197s), [~5:16](https://www.youtube.com/watch?v=rFGNYlorK6o&t=316s)). Video thiên tài mở bằng lưới chân dung ([~0:20](https://www.youtube.com/watch?v=2246gxgBcAs&t=20s)). Người xem luôn biết mình đang ở đâu trong danh sách. Ở video dạng liệt kê, đây là thứ giữ người xem ở lại.

### 5.2. Nhịp đổi hình

- **Không có hai khung storyboard liền nhau giống nhau.** Nghĩa là hình thay đổi ít nhất mỗi 10 giây, và thực tế còn nhanh hơn: trong 10 giây thường có 2–3 lần đổi tư thế hoặc thêm/bớt hình.
- Hình minh họa bám theo **từng câu**, không theo từng đoạn.

### 5.3. Bố cục trái–phải và hướng nhìn

Bố cục mặc định ở nền trắng: **nhân vật một bên, hình minh họa bên kia.** Nhân vật chìa tay hoặc chỉ về phía hình, nên mắt người xem đi từ mặt nhân vật (nơi có giọng nói) sang hình (nơi có thông tin). Khi chuyển hình, nhân vật thường đổi bên để khung hình không lặp lại.

### 5.4. Khuôn ba nhịp cho mỗi mục

Mỗi cuốn sách, mỗi thuyết, mỗi thiên tài đi theo cùng một khuôn:

1. **Giới thiệu, nhận diện**: bìa sách / ảnh thật / tên chương bằng chữ, nhân vật đứng cạnh.
2. **Giải thích**: nền trắng, nhân vật + sơ đồ, trích dẫn, chữ động.
3. **Ví dụ đời thường hoặc tái hiện**: chuyển sang collage hoặc cảnh vẽ, nhân vật bước vào tình huống. Thường chốt bằng một câu đùa có hình minh họa nghĩa đen.

Sau đó quay về nền trắng hoặc lưới mục lục, rồi sang mục kế tiếp.

### 5.5. Tái hiện thí nghiệm và tình huống bằng cảnh vẽ

Video tâm lý học không chỉ kể thí nghiệm mà **dựng lại** nó:

- **Little Albert** ([~2:48–3:08](https://www.youtube.com/watch?v=uqXylqA918Y&t=168s)): ảnh tư liệu thật, rồi tái hiện bằng cảnh vẽ: em bé trong phòng xám, con chuột trắng, nhà nghiên cứu chibi.
- **Cây cầu treo** ([~12:02](https://www.youtube.com/watch?v=uqXylqA918Y&t=722s)): hai khung song song, cầu gỗ vững trên suối và cầu treo lung lay trên vực, cùng một cô gái phỏng vấn. Người xem thấy ngay biến số của thí nghiệm.
- **Chó bất lực tập nhiễm** ([~12:45](https://www.youtube.com/watch?v=uqXylqA918Y&t=765s)): chuồng có vách ngăn, chó bị giật điện có tia sét trên đầu.

Đây là chỗ hình ảnh làm việc mà lời nói khó làm: **so sánh hai điều kiện cạnh nhau**.

### 5.6. Nén nhịp về cuối

Thời lượng mỗi truyện trong video SGK (theo chương YouTube):

| Truyện | Thời lượng |
|--------|-----------|
| Người mẹ và thần chết | 56s |
| Chiếc lá cuối cùng (có quảng cáo xen giữa) | 123s |
| Cây bút thần | 121s |
| Lặng lẽ Sa Pa | 15s |
| Vợ nhặt | 15s |
| Chiếc thuyền ngoài xa | 18s |

Phần đầu kể kỹ, có cảnh vẽ đầy đủ. Phần cuối chỉ còn **một chân dung chibi + một ảnh phim + một câu đùa**. Video tăng tốc về cuối, không bị lê thê, và lời kết "còn nhiều truyện khác… thôi dừng ở đây" trở thành một miếng hài.

### 5.7. Quảng cáo: tách bằng màu, nối bằng ý

- **Nối bằng ý:** video self-help đi từ bài học của *The Innovator's Dilemma* ("đừng bảo thủ, hãy đón cái mới") sang "một số cái mới như… điện thoại Nothing Phone" ([~6:35](https://www.youtube.com/watch?v=rFGNYlorK6o&t=395s)).
- **Tách bằng hình:** video SGK chuyển sang **nền lưới xanh dương đậm**, khác hẳn nền trắng và cảnh pastel ([~2:57](https://www.youtube.com/watch?v=QICWDoSEklM&t=177s)), rồi quay lại đúng cảnh *Chiếc lá cuối cùng* đang dở. Video self-help dán nhân vật vào góc của video quay sản phẩm thật.
- Nhân vật chính **vẫn có mặt** trong quảng cáo, nên người xem không có cảm giác "đã sang video khác".

### 5.8. Mở và kết

- **Mở:** nhân vật trên nền trắng, giơ hai ngón chào, một câu đặt khung ("Hôm nay tôi sẽ nói về tất cả…"), kèm câu miễn trừ quen thuộc ("thông tin cóp nhặt trên mạng, sai thì comment"). Trong 20 giây đầu đã có lưới mục lục.
- **Kết:** nhân vật đứng nền trắng, câu chốt cố định "Tôi là Vui Vẻ, đừng quên đăng ký…". Đây là nhận diện âm thanh và hình ảnh của kênh.

---

## 6. Animation

### Kiểu animation (suy luận)

Mọi dấu hiệu trong storyboard cho thấy đây là **animation cắt ghép (cut-out / puppet), loại limited animation**:

- Nhân vật giữ nguyên dáng đứng và tỉ lệ qua hàng trăm khung. Chỉ **tay, mắt, miệng** đổi. Đây là kiểu rig bộ phận rời: tay là một lớp, mắt là một lớp, miệng là một lớp, mỗi lớp có vài phiên bản để đổi qua lại.
- Tư thế tay lặp lại y hệt giữa các video cách nhau hơn một năm, tức là có **thư viện tư thế dùng chung**.
- Nhân vật phụ quần chúng không có tay, hoặc tay dính vào thân. Càng ít bộ phận chuyển động, càng rẻ.
- Hiệu ứng (ZZZ, tia sét, mồ hôi, lấp lánh) là **biểu tượng dán thêm**, không phải hiệu ứng mô phỏng.

### Chuyển động camera (suy luận)

- **Cắt cận (punch-in)** từ toàn cảnh vào mặt nhân vật để nhấn cảm xúc (phòng khách, video tâm lý học, [~1:09](https://www.youtube.com/watch?v=uqXylqA918Y&t=69s)).
- **Pan/zoom trên cảnh vẽ rộng**: cùng một bối cảnh xuất hiện ở nhiều khung với các góc cắt khác nhau (phòng khách, phòng thí nghiệm, sân trường đại học). Nhiều khả năng là một ảnh nền lớn, camera di chuyển trên đó.
- **Phần tử hiện dần theo lời kể**: con số trên đầu học sinh trong thí nghiệm chia nhóm hiện và đổi màu qua 5 khung liên tiếp; tờ "EXAM" rồi chữ "[FAIL]" xuất hiện sau.

### Chưa xác định được

Với dữ liệu 1 khung/10 giây, **chưa thể khẳng định**: kiểu chuyển cảnh (cắt thẳng hay có hiệu ứng), easing của chuyển động, có khớp khẩu hình (lip-sync) hay chỉ đóng/mở miệng, có nhún nhảy (bounce) khi nhân vật xuất hiện hay không. Khi xem trực tiếp video, nên ghi lại các điểm này vào bảng ở mục 7.

### Công cụ phù hợp với phong cách này

Phong cách này làm được bằng công cụ phổ thông, không cần phần mềm 2D chuyên sâu:

- **Vẽ nhân vật và tư thế**: bất kỳ app vẽ vector/raster nào (Procreate, Clip Studio, Illustrator, Krita). Xuất từng bộ phận thành lớp PNG nền trong.
- **Rig và diễn**: Adobe Character Animator (khớp miệng theo giọng tự động, đổi tư thế bằng phím), Moho, hoặc After Effects với Duik / Puppet Pin.
- **Dựng video**: CapCut, Premiere hoặc DaVinci Resolve đủ cho nền trắng + dán hình + chữ động + zoom.

---

## 7. Áp dụng cho video review sách

### Bộ nhận diện cần làm một lần

1. **Một nhân vật dẫn chuyện**: 3 màu nhận diện, 1 chi tiết chữ ký (như túi đeo chéo), viền đen dày, nhận ra được khi thu nhỏ còn 50 pixel.
2. **Thư viện ~10 tư thế tay + ~6 bộ mắt/miệng.**
3. **Bộ phụ kiện đổi vai**: kính + sách (đang đọc), máy tính (tra cứu), áo theo thể loại sách (áo blouse cho sách khoa học, áo vest cho sách kinh doanh…).
4. **2–3 bối cảnh vẽ dùng lại**: góc đọc sách, phòng làm việc, một "sân khấu" trống để tái hiện ví dụ trong sách.
5. **Mẫu huy hiệu bìa sách tròn** có chú thích tên sách + tác giả, dùng cho thumbnail và mục lục.
6. **Câu mở và câu kết cố định.**

### Quy trình từ kịch bản đến hình

1. Viết kịch bản theo [`huong-dan-review-sach.md`](huong-dan-review-sach.md).
2. Chia kịch bản thành các câu, mỗi câu một dòng trong [template storyboard](../templates/storyboard-video-review-sach.md).
3. Với mỗi câu, chọn **tầng nền** (A trắng / B collage / C cảnh vẽ) và **loại hình** (bìa, sơ đồ, trích dẫn, chữ động, meme, tư liệu, tái hiện).
4. Gạch chân mọi danh từ cụ thể và phép so sánh: mỗi chỗ là một hình.
5. Chọn **tư thế + biểu cảm** của nhân vật cho câu đó.
6. Kiểm tra nhịp: không đoạn nào quá 10 giây mà hình đứng yên.
7. Kiểm tra mỗi mục có đủ ba nhịp (nhận diện → giải thích → ví dụ/tái hiện).

### Chuyển thể cho từng loại sách

| Loại sách | Hình chủ đạo | Ví dụ áp dụng |
|-----------|--------------|---------------|
| **Self-help, kinh doanh** | Nền trắng + sơ đồ trong sách + collage đời thường | Mô hình 4 bước của *Atomic Habits* thành sơ đồ, rồi nhân vật diễn từng bước trong căn phòng thật |
| **Khoa học, tâm lý** | Tái hiện thí nghiệm bằng cảnh vẽ, so sánh hai điều kiện cạnh nhau | Như cây cầu treo hay thí nghiệm chia nhóm |
| **Tiểu thuyết, truyện** | Cảnh vẽ màu theo cảm xúc, nhân vật chibi có một chi tiết nhận diện | Như *Cô bé bán diêm*: đêm xanh tím, ánh diêm ấm. **Không spoil bằng hình**: tránh dựng cảnh cao trào ở phần không spoil |
| **Tiểu sử, lịch sử** | Ảnh thật trước, chibi sau, collage trên ảnh địa danh | Như Einstein dán lên ảnh trường đại học |
| **Danh sách nhiều cuốn** | Lưới huy hiệu làm mục lục, quay về lưới khi chuyển mục, nén nhịp về cuối | Như video self-help |

### Những điều không nên chép

- **Ảnh mạng và ảnh phim không rõ bản quyền.** Kênh dùng nhiều ảnh mạng, meme và ảnh phim. Khi làm kênh riêng, ưu tiên ảnh tự chụp (bìa sách tự chụp, trang sách có trích dẫn), ảnh có giấy phép tự do, hoặc tự vẽ lại.
- **Đùa thô tục hoặc nhạy cảm chính trị.** Phù hợp với giọng của kênh Vui Vẻ, nhưng không bắt buộc cho review sách. Cái nên học là **cơ chế** (hình nghĩa đen của câu ví von), không phải nội dung câu đùa.
- **"Thông tin cóp nhặt trên mạng".** Review sách cần dẫn trang và trích dẫn chính xác (xem nguyên tắc dẫn chứng trong hướng dẫn chính).
