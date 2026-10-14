# Người que và animation cho video review sách

Tài liệu này biến phân tích ở [`phan-tich-hinh-anh-kenh-vui-ve.md`](phan-tich-hinh-anh-kenh-vui-ve.md) thành cách làm cụ thể: dựng một nhân vật người que, cho nó cử động, và **đánh dấu kịch bản** để biết từng câu thoại đi với tư thế, biểu cảm và chuyển động nào.

- Demo chạy được (xem từng kỹ thuật chuyển động, phát kịch bản mẫu): [`demo/nguoi-que-animation.html`](demo/nguoi-que-animation.html)
- Kịch bản mẫu đã đánh dấu đầy đủ: [`../templates/kich-ban-mau-nguoi-que.md`](../templates/kich-ban-mau-nguoi-que.md)
- Template storyboard: [`../templates/storyboard-video-review-sach.md`](../templates/storyboard-video-review-sach.md)

Nhân vật trong demo ("Mọt") là thiết kế riêng cho dự án này. Học **cách làm** của kênh Vui Vẻ, đừng chép nhân vật tóc hồng của họ.

---

## 1. Vì sao người que hợp với review sách

- **Rẻ và nhanh.** Một bộ phận rời vẽ một lần, dùng cho hàng trăm video. Video 20 phút của Vui Vẻ chỉ cần khoảng 10 tư thế tay và 6 kiểu mắt/miệng.
- **Không tranh chỗ với nội dung.** Thân mảnh, chiếm ít diện tích, nên còn nhiều chỗ cho bìa sách, trích dẫn, sơ đồ.
- **Biểu cảm dồn vào mặt và tay.** Đó là hai thứ người xem nhìn khi nghe giọng nói.
- **Người xem tự lấp phần còn thiếu.** Hình càng đơn giản, người xem càng dễ đặt mình vào nhân vật.

---

## 2. Dựng nhân vật

### Tỉ lệ

Chia chiều cao nhân vật làm 10 phần:

| Bộ phận | Tỉ lệ | Ghi chú |
|---------|-------|---------|
| Đầu (kể cả tóc) | 4/10 | Đầu to là nơi chứa biểu cảm, phải đọc được khi nhân vật nhỏ ở góc màn hình |
| Thân (áo) | 2/10 | Hình thang hoặc chữ nhật bo góc, có **một chi tiết chữ ký** (Vui Vẻ dùng túi đeo chéo; Mọt trong video mặc áo polo xanh viền trắng, đeo thẻ sinh viên dây xanh sọc đỏ; bản demo HTML vẫn dùng dây đánh dấu sách màu cam) |
| Chân | 4/10 | Hai nét đơn, giày hình bầu dục |
| Tay | dài bằng thân + nửa đầu | Hai đoạn (vai–khuỷu–bàn tay), bàn tay tròn |

**Kiểm tra nhận diện:** thu nhân vật về 50 pixel chiều cao. Nếu vẫn nhận ra ngay, thiết kế đạt. Thường là nhờ một mảng màu lớn (tóc) và một chi tiết chữ ký.

**Nét và màu:** viền đen dày đều cho mọi bộ phận, không đổ bóng, tối đa 3 màu nhận diện. Viền dày giúp nhân vật tách khỏi mọi loại nền, kể cả ảnh chụp.

**Góc nhìn:** đứng nghiêng 3/4, mặt quay về phía hình minh họa. Có thêm một bản lật ngang để đứng được bên kia khung hình.

### Tách lớp (rig)

Mỗi bộ phận là một lớp riêng, có **điểm xoay (pivot)** đặt đúng khớp:

```
Mọt
├── chan-trai, chan-phai          pivot: hông
├── than                          pivot: hông
│   └── day-the (demo: day-danh-dau)  pivot: cổ áo   (chuyển động phụ)
├── tay-trai, tay-phai            pivot: vai
│   └── ban-tay  [nam | chi | v | xoe | ok]       (đổi hình, không xoay)
└── dau                           pivot: cổ
    ├── toc
    ├── mat      [thuong | cuoi | tron | luom | x | nham]
    └── mieng    [ngam | he | mo | cuoi | mim | o | meo]   (noi = luân phiên ngam/he/mo)
```

Mắt, miệng và bàn tay **đổi hình** (swap), không biến dạng. Đây là cốt lõi của limited animation: thay vì vẽ chuyển động, ta đổi giữa các hình vẽ sẵn.

### Bộ tư thế tối thiểu

Vẽ trước 13 tư thế này là làm được gần hết mọi video:

| Mã | Tư thế | Dùng khi |
|----|--------|----------|
| `dung` | Đứng, tay buông | Nghỉ giữa hai ý |
| `chao` | Giơ chữ V | Mở đầu, chào, kết |
| `chi-len` | Giơ một ngón trỏ | Nêu ý, "thứ nhất…" |
| `chia-tay` | Một tay chìa về phía hình | Giới thiệu hình minh họa (dùng nhiều nhất) |
| `nhun-vai` | Hai tay ngửa | "Thế đấy", chuyện vô lý |
| `chong-cam` | Tay chống cằm | Suy nghĩ, câu hỏi tu từ |
| `ok` | Ra dấu OK | Khen, đồng ý |
| `khoanh-tay` | Khoanh tay | Chê, phán xét |
| `chi-nguoi-xem` | Chỉ thẳng ra trước | Nói với "bạn", kêu gọi |
| `an-mung` | Hai tay giơ cao | Ăn mừng, phấn khích |
| `cam-sach` | Hai tay cầm sách mở | Đang đọc, trích dẫn |
| `ngoi-may` | Ngồi trước máy tính | "Tôi tra thêm thì…" |
| `ngu` | Nằm quấn chăn (thêm `FX: zzz`) | Ngủ, chán, "đọc đến đây thì…" |

### Bộ biểu cảm

| Mã mắt | Mã miệng hay đi kèm | Cảm xúc |
|--------|---------------------|---------|
| `thuong` | `noi` | Trung tính, đang nói |
| `cuoi` | `cuoi` | Vui, đắc ý |
| `tron` | `o` | Sốc, ngạc nhiên |
| `luom` | `mim` | Mỉa mai, nghi ngờ |
| `x` | `meo` | Đau, xấu hổ, "toang" |
| `nham` | `cuoi` | Tự hào, hồi tưởng |

---

## 3. Mười nguyên tắc chuyển động cho người que

Số khung tính ở **24 fps** (24 khung = 1 giây). Ở 30 fps thì nhân khoảng 1,25.

| # | Nguyên tắc | Cách làm | Số khung |
|---|-----------|----------|----------|
| 1 | **Pose-to-pose, cắt gọn** | Đổi thẳng từ tư thế này sang tư thế kia, chỉ chèn 1 khung trung gian hoặc không chèn gì. Chuyển động mượt quá sẽ trông như phần mềm, mất chất hoạt hình tay. | 0–2 khung trung gian |
| 2 | **Giữ đủ lâu** | Mỗi tư thế giữ ít nhất nửa giây để mắt kịp đọc. Đổi tư thế theo **câu**, không theo từ. | ≥ 12 khung |
| 3 | **Không bao giờ chết đứng** | Khi đang giữ tư thế vẫn có chớp mắt và "thở" (thân nhích lên xuống 1–2%). | Thở: chu kỳ 2 giây |
| 4 | **Chớp mắt** | Nhắm mắt 2–3 khung, cách nhau ngẫu nhiên 2–5 giây. Chớp ngay khi đổi tư thế lớn để che cú cắt. | 2–3 khung |
| 5 | **Nhép miệng** | Đổi `ngam` → `he` → `mo` theo âm lượng giọng. Không cần khớp từng âm tiết. | 2–4 khung mỗi hình |
| 6 | **Lấy đà** | Trước động tác lớn (chỉ tay, giơ tay ăn mừng), nhích ngược chiều một chút. | 2–3 khung |
| 7 | **Bật ra rồi dội lại** | Đồ vật xuất hiện: phóng từ 0% → 110% → 100%. | 6–8 khung |
| 8 | **Chuyển động phụ** | Tóc, dây đánh dấu, túi... trễ hơn thân 2 khung và lắc thêm một nhịp. | trễ 2 khung |
| 9 | **Nhịp hài (beat)** | Sau câu đùa, giữ im 0,5–1 giây rồi mới cắt sang mặt phản ứng. Không có khoảng lặng này thì câu đùa trôi mất. | 12–24 khung |
| 10 | **Camera làm hộ animation** | Cắt cận mặt (punch-in), rung, lia. Một cú cắt cận rẻ hơn nhiều so với vẽ biểu cảm phức tạp. | cắt: 0 khung, rung: 6–8 khung |

### Camera

| Mã | Làm gì | Khi nào |
|----|--------|---------|
| `punch-in` | Cắt thẳng (không zoom từ từ) vào mặt, 150–200% | Chốt câu đùa, cảm xúc mạnh, kêu gọi |
| `punch-out` | Cắt về toàn cảnh | Quay lại giải thích |
| `rung` | Lắc 2–4% kích thước khung, giảm dần trong 6–8 khung | Sốc, tiếng động lớn, "toang" |
| `lia-trai`, `lia-phai` | Trượt camera trên nền rộng, 1–2 giây | Đi từ nhân vật sang hình minh họa, khám phá bối cảnh |
| `giu` | Không đổi | Mặc định |

### Kiểu xuất hiện của đồ vật và chữ

| Mã | Kiểu | Dùng cho |
|----|------|----------|
| `pop` | Bật ra (nguyên tắc 7) | Bìa sách, icon, meme |
| `truot` | Trượt từ mép khung vào | Ảnh lớn, tranh chuyển cảnh |
| `go-chu` | Hiện từng chữ | Trích dẫn |
| `hien-dan` | Hiện từng phần theo lời kể | Sơ đồ, danh sách, con số |
| `dap` | Rơi từ trên xuống, nảy nhẹ, kèm rung | Từ khóa quan trọng (chữ động) |

### Hiệu ứng biểu tượng

`zzz` (ngủ, chán) · `set` (tia sét: giận, bị sốc) · `mo-hoi` (giọt mồ hôi: ngại, lúng túng) · `bong-nghi` (bong bóng suy nghĩ: tưởng tượng, nhớ lại) · `lap-lanh` (khen, "xịn") · `dau-hoi` (thắc mắc) · `tim` (thích).

Hiệu ứng là **hình dán**, không phải mô phỏng. Chúng bật ra (`pop`) cạnh đầu nhân vật và tự mất sau 1–2 giây.

---

## 4. Đánh dấu kịch bản

Đây là bước nối kịch bản với animation. Dưới mỗi câu thoại, viết **một dòng cue** bắt đầu bằng `>`:

```
Lời thoại của câu.
> P: <tư thế> | E: <mắt> | M: <miệng> | IN: <đồ vật> (<kiểu>, <vị trí>) | CAM: <camera> | FX: <hiệu ứng> | NEN: <A/B/C>
```

- Chỉ ghi trường **thay đổi** so với câu trước. Trường không ghi thì giữ nguyên.
- `M` mặc định là `noi` (nhép miệng) khi có thoại, không cần ghi.
- `NEN`: `A` nền trắng, `B` ảnh thật làm nền, `C` cảnh vẽ (xem mục 3 của bản phân tích).
- `OUT: <đồ vật>` để cho đồ vật biến mất.
- `BEAT: 0.5s` để chèn khoảng lặng.
- `X2` khi nhân vật cần hai phiên bản cùng lúc (so sánh trước/sau). `X2: tat` để về lại một nhân vật.

Ví dụ:

```
Cuốn sách này bán được hơn 20 triệu bản.
> P: chia-tay | IN: bia-sach (pop, phai) | IN: so "20.000.000" (dap, tren)

Và tôi đọc nó… ba lần mới hết.
> P: chong-cam | E: luom | OUT: so | BEAT: 0.5s | CAM: punch-in | FX: mo-hoi
```

### Từ điển: loại câu → cue mặc định

Khi chưa biết đánh dấu gì, tra bảng này rồi chỉnh theo ý:

| Loại câu trong kịch bản | Cue gợi ý |
|-------------------------|-----------|
| Mở đầu, chào | `P: chao` · `E: cuoi` · `NEN: A` |
| Nêu tên sách, tác giả | `P: chia-tay` · `IN: bia-sach (pop)` |
| Câu hỏi trung tâm, câu hỏi tu từ | `P: chong-cam` · `FX: dau-hoi` |
| Liệt kê "thứ nhất, thứ hai…" | `P: chi-len` · `IN: chu "1." (dap)` ; đổi số mỗi ý |
| Giải thích một khái niệm | `P: chia-tay` · `IN: so-do (hien-dan)` ; mỗi từ khóa hiện một phần |
| Trích dẫn từ sách | `P: cam-sach` · `IN: trich-dan (go-chu)` kèm **số trang** |
| Ví dụ đời thường | `NEN: B` hoặc `C` · nhân vật diễn tình huống |
| Câu đùa | đặt vấn đề ở câu trước → `BEAT: 0.5s` → `CAM: punch-in` · `E: luom` hoặc `x` |
| Twist, điều bất ngờ | `E: tron` · `M: o` · `CAM: rung` |
| Khen | `P: ok` · `E: cuoi` · `FX: lap-lanh` |
| Chê | `P: khoanh-tay` · `E: luom` |
| "Tôi tra thêm thì…" | `P: ngoi-may` |
| So sánh hai thứ, trước và sau | `X2` hoặc chia đôi khung, hai bên đặt cạnh nhau |
| Nói với người xem, kêu gọi | `P: chi-nguoi-xem` · `CAM: punch-in` |
| Chuyển sang mục mới | `CAM: punch-out` · `IN: luoi-muc-luc (pop)` ; khoanh mục sắp nói |
| Kết | `P: chao` · `NEN: A` · câu kết cố định |

### Mật độ cue

- **Mỗi câu ít nhất một thay đổi** (tư thế, biểu cảm, đồ vật hoặc camera). Đây là cách giữ "không quá 10 giây hình đứng yên".
- **Không quá 3 thay đổi trong một câu.** Nhiều hơn thì người xem không biết nhìn đâu.
- **Mỗi 20–30 giây một cú camera** (punch-in/out, lia) để đổi nhịp thị giác.
- **Câu đùa nào cũng có `BEAT`.**

---

## 5. Quy trình từ kịch bản đến video

1. **Viết kịch bản** theo [`huong-dan-review-sach.md`](huong-dan-review-sach.md). Mỗi câu một dòng, câu ngắn.
2. **Đánh dấu cue** cho từng câu (mục 4). Làm trên văn bản thuần, chưa mở phần mềm.
3. **Thu giọng** trước khi dựng hình. Animation bám theo giọng, không ngược lại.
4. **Đặt mốc thời gian**: nghe lại bản thu, ghi giây bắt đầu của mỗi câu vào cột thời điểm trong [template storyboard](../templates/storyboard-video-review-sach.md).
5. **Dựng theo lượt**, mỗi lượt một lớp cho cả video:
   1. Nền (A/B/C) và đồ vật vào/ra.
   2. Tư thế nhân vật theo cue `P`.
   3. Biểu cảm `E` và nhép miệng (tự động nếu phần mềm hỗ trợ).
   4. Camera và hiệu ứng.
   5. Chớp mắt, thở, chuyển động phụ. Thêm sau cùng vì đây là lớp "làm cho sống".
6. **Xem lại không tiếng.** Hình có tự kể được câu chuyện không? Có đoạn nào hình đứng yên quá 10 giây không?
7. **Xem lại chỉ nghe tiếng, không nhìn.** Câu đùa có khoảng lặng chưa?

### Làm bằng công cụ nào

| Công cụ | Hợp với | Cách làm cue |
|---------|---------|--------------|
| **Adobe Character Animator** | Làm nhiều video, muốn nhép miệng tự động | Gán mỗi tư thế `P` vào một phím (trigger), mắt/miệng tự chạy theo webcam và giọng. Diễn trực tiếp theo cue khi nghe lại bản thu. |
| **After Effects** (+ Duik hoặc Puppet Pin) | Muốn kiểm soát từng khung | Mỗi tư thế là một khung hình giữ (hold keyframe). Pop dùng scale 0 → 110 → 100. Rung dùng expression `wiggle` trong 6–8 khung. |
| **Moho** | Rig xương 2D, đổi hình bằng switch layer | Mắt, miệng, bàn tay là switch layer, đúng với hệ mã E/M/bàn tay. |
| **CapCut / Premiere** | Mới bắt đầu, ít ngân sách | Xuất sẵn mỗi tư thế thành một PNG (đã gồm mắt/miệng). Mỗi cue `P`/`E` là một lần thay ảnh. Pop và rung dùng hiệu ứng có sẵn. Nhép miệng bằng cách xen kẽ hai PNG miệng ngậm/mở. |

Bắt đầu với CapCut + bộ PNG là đủ để ra video đầu tiên. Khi đã quen nhịp cue, chuyển sang Character Animator để đỡ việc nhép miệng.

---

## 6. Lỗi hay gặp

| Lỗi | Dấu hiệu | Sửa |
|-----|----------|-----|
| Mượt quá | Tay trôi như robot, trông như slide PowerPoint | Bỏ bớt khung trung gian, cắt thẳng giữa các tư thế |
| Đổi quá nhanh | Tư thế đổi theo từng từ, nhìn giật | Giữ mỗi tư thế ≥ 0,5 giây, đổi theo câu |
| Nhân vật chết đứng | Nói 10 giây không cử động | Thêm chớp mắt, thở, đổi tay ở giữa câu dài |
| Nhân vật che hình | Bìa sách hoặc chữ bị đầu nhân vật che | Nhân vật đứng 1/3 khung, hình ở 2/3 còn lại; đổi bên khi cần |
| Câu đùa trôi | Người xem không kịp cười | Thêm `BEAT` rồi cắt cận mặt |
| Quá nhiều hiệu ứng | Màn hình rối, không biết nhìn đâu | Tối đa 3 thay đổi mỗi câu, mỗi lúc một hiệu ứng |
| Spoil bằng hình | Dựng lại cảnh cao trào trong phần "không spoil" | Phần không spoil chỉ minh họa tiền đề và cảm giác |
