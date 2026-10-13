# Prompt dựng cảnh: *Cho tôi xin một vé đi tuổi thơ*

Bộ prompt tạo hình ảnh và video AI cho từng cảnh trong [`cho-toi-xin-mot-ve-di-tuoi-tho.md`](cho-toi-xin-mot-ve-di-tuoi-tho.md). Số cảnh ở đây khớp với số cảnh trong kịch bản.

## Cách dùng

- **Prompt ảnh** dùng cho Midjourney, DALL·E, Ideogram, Flux, Leonardo, v.v. **Prompt video** dùng cho Runway, Kling, Veo, Pika, Hailuo, v.v., hoặc dùng ảnh vừa tạo làm khung đầu (image-to-video).
- Prompt viết bằng tiếng Anh vì đa số công cụ hiểu tiếng Anh tốt hơn. Ghi chú tiếng Việt ở dưới mỗi prompt giải thích cảnh đó dùng để làm gì.
- Luôn **dán khối "Phong cách chung" vào cuối mỗi prompt** để các cảnh đồng bộ màu sắc và nét vẽ.
- Khung hình mặc định là 16:9 (`--ar 16:9` trên Midjourney). Bản Shorts/Reels thì đổi sang 9:16.
- Chữ trên màn hình (tiêu đề, câu trích, điểm số) nên **thêm ở bước dựng (CapCut, Premiere…)**, đừng bắt AI vẽ chữ: AI viết tiếng Việt có dấu rất hay sai.

## Những thứ KHÔNG tạo bằng AI

| Tư liệu | Vì sao | Thay bằng |
|---------|--------|-----------|
| Bìa sách, trang sách, tranh minh họa gốc trong sách | AI sẽ vẽ sai, và có thể khiến người xem tưởng là ấn phẩm thật | Quay / chụp chính cuốn sách của bạn |
| Chân dung tác giả Nguyễn Nhật Ánh | Không tạo hình người thật bằng AI | Ảnh báo chí có ghi nguồn |
| Bìa *Hoa vàng trên cỏ xanh*, *Hoàng tử bé*, *Totto-chan*, bản tiếng Anh | Như trên | Chụp sách thật hoặc ảnh bìa từ NXB, ghi nguồn |
| Bắt chước nét vẽ của họa sĩ minh họa trong sách | Tôn trọng tác quyền của họa sĩ | Dùng phong cách riêng ở khối dưới |

Bốn nhân vật nhỏ trong các prompt dưới đây là **hình dung riêng của kênh**, không phải hình minh họa chính thức. Có thể ghi một dòng nhỏ trên màn hình: *"Hình minh họa do AI tạo, không phải tranh trong sách."*

---

## Phong cách chung (dán vào cuối mọi prompt)

```
Style: warm hand-drawn watercolor and colored-pencil illustration, soft paper texture,
nostalgic palette of sun-faded yellow, rice-field green, terracotta and sky blue,
gentle golden afternoon light, rural southern Vietnam in the 1960s–70s,
simple shapes, calm composition, cinematic 16:9 framing.
No text, no letters, no watermark, no logo.
```

**Negative prompt** (với công cụ có ô này):

```
text, letters, words, watermark, logo, signature, modern buildings, smartphones,
cars, anime style, 3D render, photorealistic faces, extra fingers, distorted hands,
horror, dark mood
```

## Bảng nhân vật (giữ cố định để các cảnh giống nhau)

Tạo ảnh bảng nhân vật trước, rồi dùng làm ảnh tham chiếu (`--cref` trên Midjourney, "character reference" / "consistent character" trên công cụ khác).

```
Character sheet, four Vietnamese village children around 8 years old, standing side by side,
front view, full body, plain cream background:
1) a curious boy with a short bowl haircut, white short-sleeve shirt, dark blue shorts, barefoot;
2) a tall skinny boy with long thin legs, striped shirt, rolled-up trousers, mischievous grin;
3) a small girl with two short pigtails, light pink blouse, brown trousers, shy smile;
4) a cheerful girl with a short bob haircut and a gap-toothed smile, yellow blouse, black trousers.
Consistent proportions, same art style across all four.
[+ Phong cách chung]
```

> Ghi chú: thứ tự lần lượt là Mùi, Hải cò, Tủn, Tí sún. Ngoại hình là do kênh tự đặt; nếu sách có mô tả khác thì sửa cho khớp.

---

## Cảnh 1 — Tiểu phẩm ở hiệu sách (0:00–0:35)

Cảnh này nên **quay người thật**. AI chỉ dùng cho cảnh mở và cảnh chèn.

**Ảnh — Cảnh mở (establishing):**

```
A cozy small Vietnamese bookstore corner, wooden shelves full of colorful books,
a sunbeam falling through the window onto a display table, dust particles in the light,
quiet and inviting, empty of people.
[+ Phong cách chung]
```

**Video — Chuyển cảnh khi nghe "giải văn học ASEAN":**

```
Slow push-in toward a single book glowing softly on a wooden table in a dim bookstore,
light rays brighten around it, dust motes float, a faint golden sparkle.
3–4 seconds, smooth camera, no text.
```

> Ghi chú: đặt cuốn sách thật vào chỗ "cuốn sách phát sáng" ở hậu kỳ, hoặc quay sách thật rồi chỉ dùng hiệu ứng ánh sáng.

---

## Cảnh 2 — Câu hỏi trung tâm (0:35–1:05)

**Ảnh — Nền cho câu hỏi "SÁCH NÀY VIẾT CHO AI?":**

```
Split composition: on the left a small child's hand, on the right an adult's hand,
both reaching toward the same open book in the center, soft warm light, simple background
with empty space at the top for a title.
[+ Phong cách chung]
```

> Ghi chú: để trống phía trên để chèn câu hỏi trung tâm ở bước dựng.

---

## Cảnh 3 — Lăng kính người review (1:05–1:40)

Cảnh này quay trước ống kính. AI chỉ tạo **nền dự phòng** nếu cần:

```
Soft-focus background of a reading nook: a stack of old paperback books, a desk lamp,
a cup of tea, a potted plant, warm evening light, shallow depth of field.
[+ Phong cách chung]
```

---

## Cảnh 4 — Tiền đề, không spoil (1:40–2:30)

**Ảnh 4a — Người kể chuyện khi đã lớn:**

```
A man in his forties seen from behind, sitting by a window in a modern city apartment at dusk,
looking out at the skyline, an old photograph in his hand showing children playing in a village,
melancholic but warm mood.
[+ Phong cách chung]
```

**Ảnh 4b — Bốn đứa trẻ trong xóm** *(dùng ảnh bảng nhân vật làm tham chiếu)*:

```
The four village children from the character sheet sitting together on a low brick wall
in front of a tiled-roof house, a big tamarind tree behind them, chickens nearby,
they are whispering and planning something secret, playful mood, late afternoon.
[+ Phong cách chung]
```

**Video 4c — Chuyển từ hiện tại về quá khứ:**

```
Camera slowly zooms into an old photograph held in an adult's hand until the photo fills the
frame, then the photo comes alive: children in a village begin to move and laugh,
colors warm up from faded sepia to bright watercolor. 5 seconds, smooth transition.
```

> Ghi chú: 4a đi với câu "người kể là một người đàn ông đã lớn", 4b đi với câu giới thiệu Mùi và ba người bạn, 4c dùng làm chuyển cảnh giữa hai câu đó.

---

## Cảnh 5 — Chuyện bên lề (2:30–3:15)

Cảnh này chủ yếu dùng **ảnh thật** (tác giả, các ấn bản). AI chỉ làm nền cho dòng chữ giải thưởng:

```
An elegant, simple background: a laurel wreath drawn in golden watercolor around an empty
center, soft cream paper texture, gentle light, lots of empty space for overlay text.
[+ Phong cách chung]
```

> Ghi chú: chèn chữ "Giải thưởng Văn học ASEAN 2010" vào giữa ở bước dựng. Không vẽ logo giải thưởng bằng AI.

---

## Cảnh 6 — Điểm sáng 1: Giọng kể hai lớp (3:15–4:25)

**Ảnh — Màn hình chia đôi "MÙI 8 TUỔI / MÙI NGƯỜI LỚN":**

```
Split-screen illustration divided by a vertical line. Left half: an 8-year-old boy
(bowl haircut, white shirt) laughing in a sunny village yard, bright saturated colors.
Right half: the same person as a man in his forties sitting at a desk at night, smiling
wistfully, muted blue tones. Both face toward the center line as if looking at each other.
[+ Phong cách chung]
```

**Video — Hai thế hệ "nhìn nhau":**

```
Slow horizontal camera slide from a child playing in a sunny village yard to a grown man
watching from a dark window on the other side of a soft vertical divide; the man smiles
gently. 5 seconds, dreamy, slow motion.
```

**Ảnh phụ — Câu ví von cây kem:**

```
Close-up of a child's hand holding a melting colorful popsicle in hot sunlight, an adult's
hand nearby pointing at it, nostalgic, soft background of a village street.
[+ Phong cách chung]
```

---

## Cảnh 7 — Điểm sáng 2 và 3: Các trò chơi (4:25–5:35)

**Ảnh 7a — Trò đặt lại tên đồ vật:**

```
The four village children from the character sheet in a simple wooden house, playfully
sticking small blank paper labels onto everyday objects: a rice bowl, a conical hat, a broom,
a clay water jar, a sleeping dog; they giggle; one adult in the doorway looks confused.
[+ Phong cách chung]
```

> Ghi chú: để nhãn giấy **trống**, rồi chèn chữ ở bước dựng (gạch tên cũ, viết tên mới đè lên) để đúng tiếng Việt.

**Video 7b — Nhãn giấy bay lên:**

```
Small blank paper labels flutter up from everyday household objects and swirl in the air
like butterflies, then land on different objects, playful, sunny room, 4 seconds.
```

**Ảnh 7c — Câu hỏi "Ai quy định thế?":**

```
A small boy with a bowl haircut standing with hands on hips, looking up boldly at a very tall
adult figure who is drawn only from the knees down, low camera angle from the child's height,
humorous and bold mood.
[+ Phong cách chung]
```

**Ảnh 7d — Trẻ con "xử" người lớn:**

```
The four children sitting behind a low table like a pretend judge's bench made of a wooden
plank, one holds a wooden spoon as a gavel, two adults stand in front of them looking
sheepish, comedic, warm afternoon light in a village courtyard.
[+ Phong cách chung]
```

> Ghi chú: 7d chỉ dùng nếu bạn đã kiểm lại tình tiết này có trong sách (xem ghi chú ở Cảnh 7 của kịch bản).

**Ảnh phụ — Câu đùa con mèo:**

```
A sleepy orange cat on a sofa staring judgmentally at a young adult who is scrolling a phone,
comedic, modern apartment, warm light.
[+ Phong cách chung]
```

---

## Cảnh 8 — Điểm chưa tới (5:35–7:00)

**Video 8a — Chuyển cảnh "GIỜ ĐẾN PHẦN CHÊ":**

```
The warm watercolor village scene quickly desaturates to grey and the sky darkens slightly,
a gust of wind turns pages of an open book, camera stops abruptly. 2–3 seconds.
```

**Ảnh 8b — "Truyện lỏng", lại một trò nữa:**

```
A long row of small game scenes lined up like train carriages: children playing hopscotch,
flying a kite, playing marbles, hide and seek, repeated into the distance, a child at the
front yawning, gentle humor.
[+ Phong cách chung]
```

**Ảnh 8c — "Giảng giải quá tay":**

```
A child happily showing a paper boat, while a large adult silhouette leans over the child
pointing at a blackboard full of blank diagrams, the child's smile fading, gentle comedy.
[+ Phong cách chung]
```

**Ảnh 8d — "Trẻ con nói như triết gia":**

```
An 8-year-old boy sitting cross-legged on a straw mat wearing oversized round reading
glasses and stroking an imaginary beard, very serious face, an old philosophy-style pose,
humorous.
[+ Phong cách chung]
```

**Ảnh 8e — "Công thức quen":**

```
A cooking scene in a rustic kitchen: hands pouring ingredients from small unlabeled jars into a pot one by one;
the jars hold tiny village houses, childhood toys and a wilted blue flower; steam rising, warm humor, the same
recipe being made again.
[+ Phong cách chung]
```

> Ghi chú: ở 8e, chèn chữ lên các hũ ở bước dựng: "làng quê", "trò nghịch", "một chút buồn".

---

## Cảnh 9 — Ấn phẩm (7:00–7:30)

Cảnh này **quay sách thật**. Prompt dưới chỉ làm cảnh chèn cho câu so sánh giá vui:

```
Two plastic cups of bubble milk tea placed next to a closed paperback book on a café table,
top-down view, soft daylight, playful comparison composition, book cover left blank.
[+ Phong cách chung]
```

> Ghi chú: thay cuốn sách trống trong ảnh bằng ảnh sách thật ở bước dựng, hoặc chụp thật luôn cho nhanh.

---

## Cảnh 10 — So sánh (7:30–8:20)

Bìa sách dùng ảnh thật. AI làm **nền cho bảng so sánh**:

```
Three empty wooden pedestals of equal height standing side by side on a soft cream
background, gentle spotlight on each, space above each pedestal for a book cover,
balanced and fair composition.
[+ Phong cách chung]
```

> Ghi chú: ba bục **bằng nhau** để nói "so sánh công bằng". Đặt ba bìa sách thật lên trên ở bước dựng.

---

## Cảnh 11 — ⚠️ Phần spoil (8:20–9:10)

**Ảnh 11a — Nền cảnh báo spoil:**

```
A red-and-cream vintage railway warning sign shape with no text, on a simple background,
railroad tracks fading into the distance, slightly dramatic lighting.
[+ Phong cách chung]
```

> Ghi chú: chèn "⚠️ CẢNH BÁO SPOIL — Chưa đọc thì tua đến 9:10" ở bước dựng.

**Ảnh 11b — Tấm vé:**

```
An old paper train ticket held between an adult's fingers on an empty rural train platform
at sunset, the ticket is blank and slightly worn, a distant village with tiled roofs
on the horizon, bittersweet mood.
[+ Phong cách chung]
```

**Video 11c — Chuyến tàu về tuổi thơ:**

```
A small vintage train slowly pulls away from a quiet rural station at sunset; through the
window, the faint reflection of an adult face turns into the face of a child; golden light,
gentle and emotional, 6 seconds, slow camera.
```

**Ảnh 11d — Gấp sách lại:**

```
Close-up of an adult's hands slowly closing a book on a wooden table at night, a desk lamp
glowing, a quiet emotional pause, soft shadows.
[+ Phong cách chung]
```

> Ghi chú: chọn ảnh/video theo nội dung bạn điền cho đoạn kết. Không mô tả chi tiết đoạn kết trong prompt để tránh lộ spoil qua thumbnail hoặc ảnh xem trước.

---

## Cảnh 12 — Kết luận và điểm "Vé Khứ Hồi" (9:10–10:20)

**Ảnh 12a — Nền "Nên đọc / Có thể bỏ qua":**

```
Two paths splitting at a fork in a village dirt road: the left path sunny and leading to
a group of playing children, the right path leading to a modern city skyline in grey-blue,
wide shot, empty space in the sky for text.
[+ Phong cách chung]
```

**Ảnh 12b — Thẻ điểm "Vé Khứ Hồi":**

```
A large vintage round-trip train ticket in the center, illustrated with a small village on
one half and a city on the other half, a punched hole in the middle, golden border,
blank areas for text, celebratory soft confetti.
[+ Phong cách chung]
```

> Ghi chú: chèn "8/10 · VÉ KHỨ HỒI — đi thì vui, về thì hơi nhói" ở bước dựng.

**Video 12c — Cảnh cuối, chạy cùng câu chào:**

```
The four village children from the character sheet run down a dirt road toward the sunset,
then turn around and wave goodbye to the camera; the camera slowly rises, the image gently
fades into soft paper texture. 6 seconds.
```

---

## Thumbnail (ảnh bìa video)

```
Bold YouTube thumbnail composition: on the left, an adult in office clothes looking surprised,
holding a small children's book; on the right, a cheerful 8-year-old village boy with a bowl
haircut pointing at the viewer; a golden train ticket floating between them; high contrast,
bright saturated colors, clean background, large empty area at the top for a title.
[+ Phong cách chung, bỏ dòng "calm composition"]
```

> Ghi chú: chữ trên thumbnail (gợi ý: **"SÁCH THIẾU NHI MÀ ĐOẠT GIẢI?"**) và ảnh bìa sách thật thêm bằng Canva / Photoshop. Thumbnail không được lộ spoil.

## Mẹo giữ hình đồng bộ

1. Tạo bảng nhân vật trước, chọn một bản ưng ý nhất và dùng nó làm tham chiếu cho mọi cảnh có trẻ con.
2. Giữ nguyên khối "Phong cách chung"; muốn đổi tông cho một cảnh (ví dụ cảnh 8 xám hơn) thì thêm một câu ở prompt cảnh đó, không sửa khối chung.
3. Nếu công cụ có "seed", ghi lại seed của ảnh đẹp để tạo các ảnh cùng bộ.
4. Video AI nên ngắn (3–6 giây) và chuyển động chậm; cắt ghép nhiều đoạn ngắn sẽ ổn định hơn một đoạn dài.
5. Kiểm tra tay, ngón tay và các chữ lạ lọt vào ảnh trước khi đưa vào dựng.
