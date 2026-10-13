// Kịch bản dựng cho video review "Cho tôi xin một vé đi tuổi thơ" — bản hài hước.
// Bản gốc có ghi chú: reviews/cho-toi-xin-mot-ve-di-tuoi-tho/kich-ban-video.md
// Bản lời thoại đọc được: reviews/cho-toi-xin-mot-ve-di-tuoi-tho/kich-ban-video-hai-huoc.md
//
// Mỗi mục: { t: lời thoại, a: [[trigger, action, ...args], ...] } hoặc { beat: giây, a: [...] }.
// trigger: 0 = đầu câu; '@từ' = lúc đọc tới từ đó (lần xuất hiện đầu); '@từ#2' = lần thứ hai;
//          số n = từ thứ n; 'e' = cuối câu.
// Nguyên tắc hài: chỉ đùa về người lớn, về chính người review và thói quen mạng xã hội;
// không đùa về tác giả, không nêu tình tiết chưa đối chiếu với sách.

(function (root) {
  const A = 560, XOM = 360;                       // vị trí Mọt ở nền trắng / ở xóm
  const KIDS = [['mui', 1010], ['haico', 1220], ['tisun', 1440], ['tun', 1640]];
  const TK = { x: 1320, y: 470, s: 1 }, TKC = { x: 1250, y: 480, s: 1.15 };
  const R = { x: 1330, y: 470 };                  // vùng hình minh họa bên phải
  const showKids = (t0 = 0) => KIDS.map(([id, x], k) => [t0, 'show', id, { x, flip: true, mode: 'pop', delay: k * 3 }]);
  const hideKids = (t = 0) => KIDS.map(([id]) => [t, 'hide', id, 'cut']);

  root.SCRIPT = [
    // ---------- Mở đầu ----------
    { t: 'Nếu có một quầy bán vé về tuổi thơ, bạn sẵn sàng trả bao nhiêu?', a: [
      [0, 'bg', 'A', 'cut'], [0, 'show', 'mot', { x: A, mode: 'cut' }], [0, 'pose', 'mot', 'chia-tay'],
      ['@quầy', 'prop', 've', 'ticket', [], { ...TK, mode: 'pop' }], ['@trả', 'eyes', 'mot', 'tron'] ] },
    { t: 'Tôi thì trả ngay. Một tháng lương cũng được.', a: [
      [0, 'jump', 'mot', 'an-mung'], [0, 'eyes', 'mot', 'cuoi'], ['@Một', 'fx', 'mot', 'lap-lanh'] ] },
    { t: 'Mà khoan. Về tuổi thơ thì có bị kiểm tra bài cũ đầu giờ không?', a: [
      [0, 'pose', 'mot', 'chong-cam'], [0, 'eyes', 'mot', 'luom'], ['@kiểm', 'fx', 'mot', 'dau-hoi'] ] },
    { beat: 0.6, a: [[0, 'mouth', 'mot', 'mim']] },
    { t: 'Thôi, để tôi suy nghĩ lại.', a: [
      [0, 'mouth', 'mot', null], [0, 'unprop', 've'], [0, 'pose', 'mot', 'khoanh-tay'], [0, 'cam', 'in', 'mot'], [0, 'fx', 'mot', 'mo-hoi'] ] },
    { t: 'Tin vui là không cần một tháng lương. Nguyễn Nhật Ánh bán đúng cái vé đó, với giá một cuốn sách mỏng, không cần săn sale.', say: 'Tin vui là không cần một tháng lương. Nguyễn Nhật Ánh bán đúng cái vé đó, với giá một cuốn sách mỏng, không cần săn sêu.', a: [
      [0, 'cam', 'out'], [0, 'eyes', 'mot', 'thuong'], [0, 'pose', 'mot', 'chia-tay'],
      ['@cuốn', 'prop', 'book1', 'book1', [], { ...R, s: 1, mode: 'pop' }],
      ['@săn', 'text', 'sale', 'không cần săn sale', { x: 1330, y: 175, style: 'warm', mode: 'dap' }] ] },
    { t: 'Xin chào, tôi là Mọt, người đọc sách hộ bạn.', a: [
      [0, 'unprop', 'book1'], [0, 'unprop', 'sale'], [0, 'jump', 'mot', 'chao'], [0, 'eyes', 'mot', 'cuoi'] ] },
    { t: 'Và hôm nay, tôi review cho bạn một tour chữa lành rẻ nhất thị trường: Cho tôi xin một vé đi tuổi thơ, của Nguyễn Nhật Ánh.', say: 'Và hôm nay, tôi review cho bạn một tua chữa lành rẻ nhất thị trường: Cho tôi xin một vé đi tuổi thơ, của Nguyễn Nhật Ánh.', a: [
      [0, 'pose', 'mot', 'chia-tay'], [0, 'eyes', 'mot', 'thuong'],
      ['@chữa', 'text', 'heal', '#chữa lành', { x: 1330, y: 175, style: 'dark', mode: 'dap' }],
      ['@rẻ', 'eyes', 'mot', 'cuoi'], ['@Cho', 'prop', 'book1', 'book1', [], { ...R, s: 1, mode: 'pop' }] ] },
    { t: 'Một cuốn sách hay được xếp ở kệ thiếu nhi, nhưng người khóc nhiều nhất khi đọc lại là… người lớn đang bị deadline dí.', say: 'Một cuốn sách hay được xếp ở kệ thiếu nhi, nhưng người khóc nhiều nhất khi đọc lại là… người lớn đang bị đét-lai dí.', a: [
      [0, 'unprop', 'heal'], ['@kệ', 'text', 'tag1', 'thiếu nhi?', { x: 1330, y: 175, style: 'warm', mode: 'dap' }],
      ['@người#2', 'eyes', 'mot', 'luom'], ['@deadline', 'fx', 'mot', 'mo-hoi'], ['@deadline', 'shake', 10] ] },
    { t: 'Vậy rốt cuộc, đây là sách thiếu nhi, hay là sách viết cho người lớn, đội lốt thiếu nhi?', a: [
      [0, 'jump', 'mot', 'chi-nguoi-xem'], [0, 'eyes', 'mot', 'tron'], ['@hay', 'cam', 'in', 'mot'] ] },

    // ---------- Tâm thế ----------
    { t: 'Nói trước để các bạn trừ hao: tôi là fan Nguyễn Nhật Ánh.', a: [
      [0, 'cam', 'out'], [0, 'unprop', 'book1'], [0, 'unprop', 'tag1'], [0, 'pose', 'mot', 'chi-len'], [0, 'eyes', 'mot', 'thuong'],
      ['@fan', 'pose', 'mot', 'ok'], ['@fan', 'eyes', 'mot', 'cuoi'], ['@fan', 'fx', 'mot', 'lap-lanh'] ] },
    { t: 'Nên nếu tôi khen hơi nhiều, cứ trừ điểm. Còn nếu tôi chê, thì chắc là thật.', a: [
      [0, 'pose', 'mot', 'chi-len'], [0, 'eyes', 'mot', 'thuong'], ['@chê,', 'eyes', 'mot', 'luom'], ['@thật.', 'fx', 'mot', 'mo-hoi'] ] },
    { t: 'Cuốn này có một điều đặc biệt: đọc lúc nhỏ và đọc lúc lớn, gần như là hai cuốn sách khác nhau.', a: [
      [0, 'move', 'mot', 1300, 10], [0, 'pose', 'mot', 'dung'], [0, 'eyes', 'mot', 'thuong'], ['@đọc', 'show', 'motnho', { x: 600, mode: 'pop' }],
      ['@nhỏ', 'text', 'tNho', 'lúc nhỏ', { x: 640, y: 210, style: 'warm', mode: 'pop' }],
      ['@lớn,', 'text', 'tLon', 'lúc lớn', { x: 1340, y: 210, style: 'cool', mode: 'pop' }] ] },
    { t: 'Đọc lúc nhỏ thì cười như được nghỉ học.', a: [
      [0, 'speaker', 'motnho'], [0, 'jump', 'motnho', 'an-mung'], [0, 'eyes', 'motnho', 'cuoi'], ['@nghỉ', 'fx', 'motnho', 'lap-lanh'] ] },
    { t: 'Đọc lúc lớn thì cười xong, im lặng một lúc lâu, rồi nhớ ra mai phải đi làm.', a: [
      [0, 'speaker', 'mot'], [0, 'pose', 'mot', 'cam-sach'], [0, 'eyes', 'mot', 'cuoi'], ['@im', 'eyes', 'mot', 'nham'],
      ['@nhớ', 'eyes', 'mot', 'tron'], ['@làm.', 'eyes', 'mot', 'x'], ['@làm.', 'fx', 'mot', 'mo-hoi'] ] },

    // ---------- Ga 1 ----------
    { t: 'Rồi, check-in ga đầu tiên.', a: [
      [0, 'hide', 'motnho'], [0, 'unprop', 'tNho'], [0, 'unprop', 'tLon'], [0, 'move', 'mot', A, 10], [0, 'eyes', 'mot', 'cuoi'],
      [0, 'pose', 'mot', 'chao'], ['@check-in', 'prop', 've', 'ticket', [], { ...TKC, mode: 'pop' }], ['@đầu', 'cam', 'row', 've', 0] ] },
    { t: 'Truyện xoay quanh bốn đứa trẻ trong một xóm nhỏ.', a: [
      [0, 'cam', 'out'], [0, 'unprop', 've', 'cut'], [0, 'bg', 'xom', 'slide'], [0, 'move', 'mot', XOM, 0], [0, 'pose', 'mot', 'chia-tay'], [0, 'eyes', 'mot', 'thuong'] ] },
    { t: 'Mùi, người kể chuyện.', a: [[0, 'show', 'mui', { x: 1010, flip: true, mode: 'pop' }]] },
    { t: 'Hải cò. Cái tên đã tự review đôi chân.', a: [
      [0, 'show', 'haico', { x: 1220, flip: true, mode: 'pop' }], ['@review', 'fx', 'haico', 'lap-lanh'], ['@review', 'eyes', 'mot', 'luom'] ] },
    { t: 'Tí sún. Cái tên cũng đã tự review hàm răng.', a: [
      [0, 'show', 'tisun', { x: 1440, flip: true, mode: 'pop' }], ['@răng.', 'mouth', 'tisun', 'sun'], ['@răng.', 'eyes', 'tisun', 'cuoi'] ] },
    { t: 'Và con Tủn. Nhỏ nhất bọn, nhưng đừng dại mà coi thường.', a: [
      [0, 'show', 'tun', { x: 1640, flip: true, mode: 'pop' }], ['@đừng', 'eyes', 'tun', 'luom'], ['@coi', 'fx', 'tun', 'set'] ] },
    { t: 'Người kể là Mùi lúc đã lớn, ngồi nhớ lại hồi mình còn nhỏ.', a: [
      [0, 'bg', 'split', 'slide'], [0, 'hide', 'mot', 'cut'], [0, 'hide', 'haico', 'cut'], [0, 'hide', 'tisun', 'cut'], [0, 'hide', 'tun', 'cut'],
      [0, 'move', 'mui', 470, 0], [0, 'flip', 'mui', false], [0, 'eyes', 'mui', 'thuong'],
      ['@lớn,', 'show', 'muilon', { x: 1450, flip: true, mode: 'pop' }], ['@nhớ', 'eyes', 'muilon', 'nham'], ['@nhớ', 'fx', 'muilon', 'bong-nghi'] ] },
    { t: 'Tức là một người lớn, đi review tuổi thơ của chính mình. Nghe quen quen không?', a: [
      [0, 'bg', 'A', 'cut'], [0, 'hide', 'mui', 'cut'], [0, 'hide', 'muilon', 'cut'], [0, 'show', 'mot', { x: A, mode: 'cut' }],
      [0, 'pose', 'mot', 'chi-len'], [0, 'eyes', 'mot', 'thuong'], ['@Nghe', 'pose', 'mot', 'chi-nguoi-xem'], ['@Nghe', 'eyes', 'mot', 'luom'], ['@quen#2', 'cam', 'in', 'mot'] ] },
    { t: 'Truyện không có phản diện, không có âm mưu, không có ai mất trí nhớ rồi gặp lại nhau ở sân bay.', a: [
      [0, 'cam', 'out'], [0, 'pose', 'mot', 'nhun-vai'], [0, 'eyes', 'mot', 'thuong'],
      ['@mất', 'text', 'drama', 'không có drama', { x: 1330, y: 400, style: 'light', mode: 'dap' }], ['@sân', 'eyes', 'mot', 'luom'] ] },
    { t: 'Chỉ có một đám con nít bày đủ trò cho thế giới bớt nhàm chán, nhất là thế giới của người lớn.', a: [
      [0, 'unprop', 'drama', 'cut'], [0, 'bg', 'xom', 'slide'], [0, 'move', 'mot', XOM, 0], [0, 'pose', 'mot', 'chia-tay'], [0, 'eyes', 'mot', 'thuong'], ...showKids('@con') ] },
    { t: 'Và trò của tụi nó thì… hơi nguy hiểm, cho người lớn.', a: [
      [0, 'eyes', 'mot', 'luom'], ['@hơi', 'fx', 'mot', 'set'], ['@hơi', 'eyes', 'tun', 'luom'] ] },
    { beat: 0.4, a: [] },
    { t: 'Tôi sẽ không kể cụ thể trò nào, vì tiết lộ trước nội dung sách của Nguyễn Nhật Ánh là một tội rất nặng.', a: [
      [0, 'pose', 'mot', 'chi-len'], [0, 'eyes', 'mot', 'thuong'], [0, 'eyes', 'tun', 'thuong'], ['@tội', 'eyes', 'mot', 'tron'], ['@nặng.', 'fx', 'mot', 'mo-hoi'] ] },
    { t: 'Chỉ biết là tụi nhỏ có luật chơi riêng, có cả ngôn ngữ riêng, khó hiểu hơn cả tiếng lóng của Gen Z.', a: [
      ['@luật', 'prop', 'b1', 'bubble', ['★?!'], { x: 1060, y: 330, mode: 'pop' }],
      ['@chơi', 'prop', 'b2', 'bubble', ['◆@#'], { x: 1270, y: 250, mode: 'pop' }],
      ['@ngôn', 'prop', 'b3', 'bubble', ['♪~'], { x: 1490, y: 330, mode: 'pop' }],
      ['@khó', 'prop', 'b4', 'bubble', ['&%!'], { x: 1690, y: 400, mode: 'pop' }],
      ['@luật', 'eyes', 'mui', 'cuoi'], ['@ngôn', 'eyes', 'tisun', 'cuoi'], ['@Gen', 'eyes', 'mot', 'tron'] ] },
    { t: 'Tụi nó hiểu nhau. Người lớn thì… ét o ét, cần phiên dịch.', a: [
      [0, 'jump', 'haico', 'an-mung'], [0, 'eyes', 'haico', 'cuoi'], [0, 'eyes', 'mot', 'thuong'],
      ['@Người', 'show', 'muilon', { x: 1790, flip: true, mode: 'slideR' }],
      ['@ét', 'eyes', 'muilon', 'tron'], ['@ét', 'fx', 'muilon', 'dau-hoi'], ['@ét', 'shake', 14],
      ['@cần', 'text', 'sos', 'cần phiên dịch', { x: 1560, y: 140, style: 'cool', mode: 'dap' }] ] },

    // ---------- Bên lề ----------
    { t: 'Chút chuyện bên lề: sách ra năm 2008, do Nhà xuất bản Trẻ phát hành.', a: [
      [0, 'bg', 'A', 'cut'], ...hideKids(), [0, 'hide', 'muilon', 'cut'], [0, 'unprop', 'sos', 'cut'], ...['b1', 'b2', 'b3', 'b4'].map((b) => [0, 'unprop', b, 'cut']),
      [0, 'show', 'mot', { x: A, mode: 'cut' }], [0, 'pose', 'mot', 'cam-sach'], [0, 'eyes', 'mot', 'thuong'],
      ['@2008,', 'text', 'n1', '2008', { x: 1330, y: 360, size: 240, mode: 'dap' }],
      ['@Nhà', 'text', 'n1b', 'NXB Trẻ', { x: 1330, y: 540, style: 'dark', mode: 'pop' }] ] },
    { t: 'Hai năm sau, flex nhẹ một cái: Giải thưởng Văn học ASEAN, cho chính cuốn sách này.', a: [
      [0, 'unprop', 'n1'], [0, 'unprop', 'n1b'], ['@flex', 'text', 'flex', 'flex nhẹ', { x: 1330, y: 175, style: 'light', mode: 'dap' }],
      ['@Giải', 'jump', 'mot', 'an-mung'], ['@Giải', 'eyes', 'mot', 'cuoi'],
      ['@Giải', 'text', 'n2', 'Giải thưởng', { x: 1330, y: 360, size: 110, mode: 'pop' }],
      ['@ASEAN,', 'text', 'n2b', 'Văn học ASEAN 2010', { x: 1330, y: 500, style: 'warm', mode: 'dap' }],
      ['@chính', 'fx', 'mot', 'lap-lanh'] ] },
    { t: 'Một cuốn truyện viết bằng giọng con nít, mà được giải văn học khu vực. Chi tiết đó đã trả lời được phần nào câu hỏi hôm nay.', a: [
      [0, 'pose', 'mot', 'chong-cam'], [0, 'eyes', 'mot', 'thuong'], ['@Chi', 'unprop', 'n2'], ['@Chi', 'unprop', 'n2b'], ['@Chi', 'unprop', 'flex'], ['@câu', 'fx', 'mot', 'dau-hoi'] ] },
    { t: 'Đó là chuyện bên lề. Còn bản thân cuốn sách thì sao?', a: [
      [0, 'pose', 'mot', 'chia-tay'], [0, 'prop', 've', 'ticket', [], { ...TK, mode: 'pop' }], ['@Còn', 'stamp', 've', 0] ] },

    // ---------- Ga 2: Hai giọng kể ----------
    { t: 'Điểm hay nhất, theo tôi, là cuốn sách có hai giọng kể chồng lên nhau.', a: [
      [0, 'unprop', 've'], [0, 'pose', 'mot', 'chi-len'],
      ['@hai', 'text', 'g2', '1 người kể', { x: 1330, y: 360, size: 120, mode: 'pop' }],
      ['@giọng', 'text', 'g2b', '= 2 giọng', { x: 1330, y: 520, size: 120, color: '#D9661A', mode: 'dap' }] ] },
    { t: 'Giọng thứ nhất là Mùi lúc nhỏ: thấy gì kể nấy, hồn nhiên, nhiều khi vô lý một cách rất hợp lý.', a: [
      [0, 'unprop', 'g2', 'cut'], [0, 'unprop', 'g2b', 'cut'], [0, 'hide', 'mot', 'cut'], [0, 'bg', 'split', 'slide'],
      [0, 'show', 'mui', { x: 470, flip: false, mode: 'pop' }], ['@thấy', 'jump', 'mui', 'an-mung'], ['@thấy', 'eyes', 'mui', 'cuoi'],
      ['@vô', 'eyes', 'mui', 'tron'], ['@hợp', 'eyes', 'mui', 'cuoi'] ] },
    { t: 'Giọng thứ hai là Mùi người lớn: chen vào giữa câu chuyện, bình luận, tiếc nuối, giống như một dòng phụ đề của người lớn chạy bên dưới tuổi thơ.', a: [
      [0, 'pose', 'mui', 'dung'], [0, 'show', 'muilon', { x: 1450, flip: true, mode: 'pop' }], ['@chen', 'pose', 'muilon', 'chong-cam'],
      ['@tiếc', 'eyes', 'muilon', 'nham'], ['@phụ', 'eyes', 'muilon', 'luom'], ['@phụ', 'mouth', 'muilon', 'mim'] ] },
    { t: 'Thế nên cùng một trò nghịch, đứa trẻ thấy một trò chơi, còn người lớn thấy một bài học.', a: [
      [0, 'mouth', 'muilon', null], [0, 'eyes', 'muilon', 'thuong'], ['@đứa', 'fx', 'mui', 'lap-lanh'], ['@đứa', 'glow', 0.35, 10],
      ['@còn', 'fx', 'muilon', 'bong-nghi'], ['@còn', 'dim', 0.3, 10] ] },
    { t: 'Kiểu câu này các bạn sẽ gặp rất nhiều: kể xong một trò nghịch, giọng người lớn thêm một câu làm mình khựng lại.', a: [
      [0, 'glow', 0, 1], [0, 'dim', 0, 1], [0, 'bg', 'A', 'cut'], [0, 'hide', 'mui', 'cut'], [0, 'hide', 'muilon', 'cut'],
      [0, 'show', 'mot', { x: A, mode: 'cut' }], [0, 'pose', 'mot', 'cam-sach'], [0, 'eyes', 'mot', 'thuong'],
      ['@kể', 'prop', 'page', 'markPage', [], { ...R, mode: 'pop' }], ['@thêm', 'progress', 'page', 'setProgress', 0, 1, 26], ['@khựng', 'eyes', 'mot', 'tron'] ] },
    { t: 'Đọc những câu đó, mình cười trước, rồi mới thấy buồn.', a: [['@cười', 'eyes', 'mot', 'cuoi'], ['@buồn.', 'eyes', 'mot', 'nham']] },
    { t: 'Cười vì tụi nhỏ ngốc thật. Buồn vì người lớn đúng thật.', a: [
      [0, 'unprop', 'page'], [0, 'eyes', 'mot', 'cuoi'], [0, 'mouth', 'mot2', 'meo'], [0, 'eyes', 'mot2', 'nham'],
      [0, 'show', 'mot2', { x: 1360, mode: 'pop' }], ['@Buồn', 'speaker', 'mot2'], ['@Buồn', 'mouth', 'mot2', null] ] },
    { beat: 0.6, a: [[0, 'speaker', 'mot']] },
    { t: 'Và cái đúng đó, mới là thứ đáng buồn.', a: [
      [0, 'hide', 'mot2', 'cut'], [0, 'cam', 'in', 'mot'], [0, 'eyes', 'mot', 'nham'], [0, 'pose', 'mot', 'dung'] ] },
    { t: 'Viết kiểu này không dễ. Nghiêng về giọng trẻ con một chút là thành truyện tranh chữ, nghiêng về giọng người lớn một chút là thành sách dạy đời.', a: [
      [0, 'cam', 'out'], [0, 'eyes', 'mot', 'thuong'], [0, 'pose', 'mot', 'nhun-vai'],
      ['@Nghiêng', 'prop', 'scale', 'scale', [], { x: 1330, y: 520, mode: 'pop' }],
      ['@truyện', 'tilt', 'scale', -14, 10], ['@sách', 'tilt', 'scale', 14, 14] ] },
    { t: 'Ở phần lớn cuốn sách, Nguyễn Nhật Ánh giữ được cái cân ở giữa. Tay nghề lão luyện là đây.', a: [
      [0, 'tilt', 'scale', 0, 12], ['@giữ', 'pose', 'mot', 'ok'], ['@giữ', 'eyes', 'mot', 'cuoi'], ['@Tay', 'fx', 'mot', 'lap-lanh'] ] },

    // ---------- Ga 3: Trò chơi ----------
    { t: 'Ga tiếp theo: trò chơi.', a: [
      [0, 'unprop', 'scale'], [0, 'eyes', 'mot', 'thuong'], [0, 'pose', 'mot', 'chia-tay'], [0, 'prop', 've', 'ticket', [], { ...TK, mode: 'pop' }], ['@trò', 'stamp', 've', 1] ] },
    { t: 'Cái tài của sách là để trò nghịch của tụi nhỏ có logic riêng, và logic đó chặt chẽ đến buồn cười.', say: 'Cái tài của sách là để trò nghịch của tụi nhỏ có lô-gích riêng, và lô-gích đó chặt chẽ đến buồn cười.', a: [
      [0, 'unprop', 've', 'cut'], [0, 'bg', 'xom', 'slide'], [0, 'move', 'mot', XOM, 0], ...showKids('@trò'),
      ['@buồn', 'eyes', 'tun', 'cuoi'], ['@buồn', 'eyes', 'mui', 'cuoi'] ] },
    { t: 'Trẻ con không phá phách vô cớ. Tụi nó phản đối. Phản đối luật lệ, phản đối sự nhàm chán, phản đối việc người lớn lúc nào cũng đúng.', a: [
      ['@phản', 'jump', 'mui', 'an-mung'], ['@phản', 'sign', 's1', 'mui', 'PHẢN\nĐỐI!'],
      ['@luật', 'jump', 'haico', 'an-mung'], ['@luật', 'sign', 's2', 'haico', 'LUẬT GÌ\nKỲ VẬY'],
      ['@sự', 'jump', 'tisun', 'an-mung'], ['@sự', 'sign', 's3', 'tisun', 'CHÁN!'],
      ['@việc', 'jump', 'tun', 'an-mung'], ['@việc', 'sign', 's4', 'tun', 'CHO\nCHƠI!'], ['@việc', 'eyes', 'mot', 'tron'] ] },
    { t: 'Nhìn như một cuộc biểu tình, chỉ có điều người biểu tình cao chưa tới một mét hai, và giờ giải tán là giờ cơm tối.', a: [
      [0, 'eyes', 'mot', 'cuoi'], ['@cao', 'eyes', 'tun', 'luom'], ['@cao', 'cam', 'in', 'tun', 2.0],
      ['@giờ', 'cam', 'out'], ['@cơm', 'fx', 'mot', 'lap-lanh'] ] },
    { beat: 0.5, a: [] },
    { t: 'Có những trò mà người lớn đọc xong phải tự hỏi: rốt cuộc, ai mới là người vô lý?', a: [
      [0, 'bg', 'A', 'cut'], ...hideKids(), ...['s1', 's2', 's3', 's4'].map((s) => [0, 'unprop', s, 'cut']),
      [0, 'show', 'mot', { x: A, mode: 'cut' }], [0, 'pose', 'mot', 'chong-cam'], [0, 'eyes', 'mot', 'thuong'],
      ['@rốt', 'text', 'q1', 'Ai vô lý?', { x: 1330, y: 420, size: 150, mode: 'dap' }], ['@vô', 'fx', 'mot', 'dau-hoi'] ] },
    { t: 'Cái hay là sách không bảo trẻ con đúng. Sách chỉ cho thấy người lớn ít khi chịu nghe lý lẽ của trẻ con.', a: [
      [0, 'unprop', 'q1'], [0, 'pose', 'mot', 'chi-len'], ['@Sách#2', 'pose', 'mot', 'chia-tay'],
      ['@ít', 'text', 'q2', 'ít khi chịu nghe', { x: 1330, y: 420, style: 'cool', mode: 'dap' }] ] },
    { t: 'POV: bạn là phụ huynh, và bạn vừa đọc tới đoạn này.', a: [
      [0, 'unprop', 'q2'], [0, 'text', 'pov', 'POV: bạn là phụ huynh', { x: 1330, y: 400, style: 'dark', mode: 'dap' }],
      [0, 'pose', 'mot', 'cam-sach'], [0, 'eyes', 'mot', 'thuong'], ['@đọc', 'eyes', 'mot', 'tron'] ] },
    { t: 'Hơi nhột, đúng không?', a: [
      [0, 'unprop', 'pov'], [0, 'jump', 'mot', 'chi-nguoi-xem'], [0, 'eyes', 'mot', 'luom'], [0, 'cam', 'in', 'mot'], ['@nhột,', 'fx', 'mot', 'mo-hoi'] ] },

    // ---------- Ga 4: Tuổi thơ là gì ----------
    { t: 'Ga thứ tư, cũng là ga tôi thích nhất.', a: [
      [0, 'cam', 'out'], [0, 'eyes', 'mot', 'cuoi'], [0, 'pose', 'mot', 'chia-tay'],
      [0, 'prop', 've', 'ticket', [], { ...TK, mode: 'pop' }], ['@cũng', 'stamp', 've', 2] ] },
    { t: 'Đọc đến cuối, tôi hiểu cái tên sách theo một nghĩa khác.', a: [[0, 'unprop', 've'], [0, 'pose', 'mot', 'cam-sach'], [0, 'eyes', 'mot', 'nham']] },
    { t: 'Tuổi thơ trong sách gắn với độ tuổi thì ít, gắn với cách nhìn thì nhiều.', a: [
      [0, 'bg', 'split', 'slide'], [0, 'hide', 'mot', 'cut'], [0, 'show', 'mui', { x: 470, flip: false, mode: 'pop' }],
      [0, 'show', 'muilon', { x: 1450, flip: true, mode: 'pop' }], [0, 'eyes', 'mui', 'thuong'], [0, 'eyes', 'muilon', 'thuong'], [0, 'pose', 'mui', 'dung'], [0, 'pose', 'muilon', 'dung'] ] },
    { t: 'Lúc còn nhìn thế giới bằng mắt con nít, cái gì cũng mới, cái gì cũng đáng thử.', a: [
      [0, 'jump', 'mui', 'an-mung'], [0, 'eyes', 'mui', 'tron'], ['@cái', 'eyes', 'mui', 'cuoi'], ['@cái', 'glow', 0.4, 12], ['@mới,', 'fx', 'mui', 'lap-lanh'] ] },
    { t: 'Còn khi nhìn bằng mắt người lớn, mọi thứ chỉ còn ba câu thần chú: biết rồi, để sau, và không được đâu.', a: [
      ['@mọi', 'dim', 0.35, 12], ['@biết', 'text', 'w1', 'biết rồi', { x: 1450, y: 170, style: 'cool', mode: 'dap' }],
      ['@để', 'text', 'w2', 'để sau', { x: 1450, y: 270, style: 'cool', mode: 'dap' }],
      ['@không', 'text', 'w3', 'không được đâu', { x: 1450, y: 370, style: 'cool', mode: 'dap' }],
      ['@biết', 'fx', 'muilon', 'zzz', 60], ['@biết', 'eyes', 'muilon', 'nham'] ] },
    { t: 'Cho nên cái vé trong tên sách không đưa bạn về tuổi thơ được. Không gì làm được việc đó.', a: [
      [0, 'glow', 0, 1], [0, 'dim', 0, 1], [0, 'unprop', 'w1', 'cut'], [0, 'unprop', 'w2', 'cut'], [0, 'unprop', 'w3', 'cut'],
      [0, 'bg', 'A', 'cut'], [0, 'hide', 'mui', 'cut'], [0, 'hide', 'muilon', 'cut'], [0, 'show', 'mot', { x: A, mode: 'cut' }],
      [0, 'pose', 'mot', 'nhun-vai'], [0, 'eyes', 'mot', 'thuong'], ['@vé', 'prop', 've', 'ticket', [], { ...TK, mode: 'pop' }] ] },
    { t: 'Nó chỉ cho bạn mượn lại đôi mắt hồi bé, trong vài giờ đọc sách. Hết giờ thì trả, không tính phí trễ hạn.', a: [
      ['@mượn', 'flipcard', 've', 'back'], ['@mượn', 'eyes', 'mot', 'tron'], ['@trong', 'eyes', 'mot', 'cuoi'], ['@trong', 'pose', 'mot', 'chia-tay'],
      ['@sách.', 'fx', 'mot', 'lap-lanh'], ['@không', 'pose', 'mot', 'ok'] ] },
    { t: 'Và với tôi, chỉ riêng chuyện đó thôi, đã đáng tiền vé.', a: [[0, 'pose', 'mot', 'ok'], ['@đáng', 'unprop', 've'], ['@đáng', 'cam', 'in', 'mot']] },

    // ---------- Ga 5: Chỗ xóc ----------
    { t: 'Vừa rồi là phần khen. Giờ đến đoạn đường hơi xóc.', a: [
      [0, 'cam', 'out'], [0, 'prop', 've', 'ticket', [], { ...TK, mode: 'pop' }], [0, 'pose', 'mot', 'chia-tay'], ['@đường', 'stamp', 've', 3], ['@xóc.', 'shake', 18], ['@xóc.', 'eyes', 'mot', 'x'] ] },
    { t: 'Chỗ xóc thứ nhất: cốt truyện lỏng.', a: [
      [0, 'unprop', 've'], [0, 'eyes', 'mot', 'thuong'], [0, 'pose', 'mot', 'chi-len'],
      ['@cốt', 'text', 'c1', '1. Cốt truyện lỏng', { x: 1330, y: 170, style: 'warm', mode: 'dap' }] ] },
    { t: 'Sách là một chuỗi trò nghịch nối nhau. Mỗi chương gần như đọc riêng được.', a: [
      [0, 'pose', 'mot', 'chia-tay'], ['@chuỗi', 'prop', 'ch', 'chapters', [], { x: 1330, y: 520, s: 0.95, mode: 'cut' }],
      ...[0, 1, 2, 3, 4, 5].map((k) => ['@chuỗi', 'reveal', 'ch', 'boxes', k, 'pop', k * 4]) ] },
    { t: 'Nếu bạn đang quen nhịp phim hành động, cao trào dồn dập, thì cuốn này sẽ thấy hơi lững thững, như đi dạo chiều trong xóm.', a: [
      [0, 'pose', 'mot', 'chong-cam'], ['@thì', 'pose', 'mot', 'nhun-vai'], ['@lững', 'eyes', 'mot', 'luom'], ['@dạo', 'eyes', 'mot', 'nham'] ] },
    { t: 'Đặt cạnh Tôi thấy hoa vàng trên cỏ xanh, cũng của Nguyễn Nhật Ánh, cũng viết về tuổi thơ, sự khác biệt rất rõ.', a: [
      [0, 'unprop', 'ch'], [0, 'unprop', 'c1'], [0, 'eyes', 'mot', 'thuong'], [0, 'pose', 'mot', 'chia-tay'],
      ['@Tôi', 'prop', 'book2', 'book2', [], { x: 1580, y: 470, mode: 'pop' }] ] },
    { t: 'Ở đó có hai anh em Thiều và Tường, có ghen tị, có hối hận, có một mạch truyện kéo người đọc đi.', a: [
      [0, 'pose', 'mot', 'chi-len'], ['@Thiều', 'show', 'anh', { x: 1060, flip: true, mode: 'pop' }], ['@Tường,', 'show', 'em', { x: 1230, flip: true, mode: 'pop' }],
      ['@ghen', 'eyes', 'anh', 'luom'], ['@hối', 'eyes', 'anh', 'nham'], ['@hối', 'eyes', 'em', 'nham'] ] },
    { t: 'Còn Vé đi tuổi thơ thì giống một cuốn album hơn là một bộ phim.', a: [
      [0, 'unprop', 'book2'], [0, 'hide', 'anh'], [0, 'hide', 'em'], [0, 'eyes', 'mot', 'nham'],
      ['@album', 'prop', 'alb', 'album', [], { ...R, mode: 'pop' }], ['@hơn', 'progress', 'alb', 'setFlip', 0, 2, 30] ] },
    { t: 'Đây không phải red flag. Cùng lắm là một lá cờ vàng nhỏ, vì tác giả cố ý chọn lối đó. Bạn chỉ cần biết trước, để khỏi đòi hoàn tiền vé.', a: [
      [0, 'unprop', 'alb'], [0, 'pose', 'mot', 'ok'], [0, 'eyes', 'mot', 'thuong'], ['@red', 'text', 'flag1', 'không phải red flag', { x: 1330, y: 175, style: 'light', mode: 'dap' }],
      ['@vàng', 'text', 'flag2', 'cờ vàng nhỏ', { x: 1330, y: 290, style: 'warm', mode: 'dap' }], ['@Bạn', 'pose', 'mot', 'chi-nguoi-xem'], ['@hoàn', 'eyes', 'mot', 'cuoi'] ] },
    { t: 'Chỗ xóc thứ hai, cái này tôi thấy cấn hơn: Mùi người lớn đôi khi nói hơi nhiều.', a: [
      [0, 'unprop', 'flag1'], [0, 'unprop', 'flag2'], [0, 'pose', 'mot', 'khoanh-tay'], [0, 'eyes', 'mot', 'luom'],
      ['@cấn', 'text', 'c2', '2. Lời bình hơi nhiều', { x: 1330, y: 170, style: 'warm', mode: 'dap' }] ] },
    { t: 'Có những đoạn trò chơi đã tự nói lên ý nghĩa rồi, nhưng giọng người lớn vẫn chen vào giải thích thêm một lần nữa.', a: [
      [0, 'unprop', 'c2', 'cut'], [0, 'hide', 'mot', 'cut'], [0, 'bg', 'split', 'slide'],
      [0, 'show', 'mui', { x: 470, flip: false, mode: 'pop' }], [0, 'eyes', 'mui', 'cuoi'], [0, 'jump', 'mui', 'an-mung'],
      ['@nhưng', 'show', 'muilon', { x: 1450, flip: true, mode: 'pop' }], ['@chen', 'pose', 'muilon', 'chi-len'], ['@chen', 'talk', 'muilon', true],
      ['@giải', 'pose', 'mui', 'dung'], ['@giải', 'eyes', 'mui', 'nham'], ['@thêm', 'fx', 'mui', 'zzz', 60] ] },
    { t: 'Giống như kể chuyện cười xong, rồi giải thích vì sao nó buồn cười.', a: [
      [0, 'talk', 'muilon', false], [0, 'bg', 'A', 'cut'], [0, 'hide', 'mui', 'cut'], [0, 'hide', 'muilon', 'cut'],
      [0, 'show', 'mot', { x: A, mode: 'cut' }], [0, 'pose', 'mot', 'nhun-vai'], [0, 'eyes', 'mot', 'thuong'] ] },
    { t: 'Mà nói câu này trong một video dài bảy phút, thì tôi cũng hơi tự vả.', a: [
      [0, 'eyes', 'mot', 'tron'], ['@tự', 'cam', 'in', 'mot'], ['@tự', 'eyes', 'mot', 'x'], ['@tự', 'mouth', 'mot', 'meo'], ['@vả.', 'shake', 16] ] },
    { beat: 0.6, a: [] },
    { t: 'Không nhiều đâu, nhưng đủ để tôi muốn lấy bút chì gạch bớt vài câu. Bút chì thôi nhé, gạch nhẹ tay.', a: [
      [0, 'cam', 'out'], [0, 'mouth', 'mot', null], [0, 'eyes', 'mot', 'thuong'], [0, 'pose', 'mot', 'cam-sach'],
      ['@bút', 'prop', 'strike', 'strikePage', [], { ...R, mode: 'pop' }], ['@gạch', 'progress', 'strike', 'setProgress', 0, 1, 30], ['@nhẹ', 'eyes', 'mot', 'cuoi'] ] },
    { t: 'Và đây cũng là lý do nhiều bạn nhỏ đọc sẽ thấy đoạn đầu vui, đoạn giữa bắt đầu… khó hiểu.', a: [
      [0, 'unprop', 'strike'], [0, 'pose', 'mot', 'nhun-vai'], [0, 'eyes', 'mot', 'thuong'], ['@vui,', 'eyes', 'mot', 'cuoi'], ['@khó', 'eyes', 'mot', 'luom'], ['@khó', 'fx', 'mot', 'dau-hoi'] ] },
    { t: 'Vì những đoạn đó vốn không viết cho các bạn ấy.', a: [[0, 'pose', 'mot', 'chi-len'], [0, 'eyes', 'mot', 'nham'], ['@không', 'cam', 'in', 'mot']] },

    // ---------- Ga cuối ----------
    { t: 'Ga cuối rồi.', a: [
      [0, 'cam', 'out'], [0, 'eyes', 'mot', 'cuoi'], [0, 'pose', 'mot', 'chao'], [0, 'prop', 've', 'ticket', [], { ...TK, mode: 'pop' }], ['@rồi.', 'stamp', 've', 4] ] },
    { t: 'Tóm lại: sách có hai giọng kể khéo, trò chơi có logic riêng buồn cười, và một ý tưởng về tuổi thơ đọng lại rất lâu.', say: 'Tóm lại: sách có hai giọng kể khéo, trò chơi có lô-gích riêng buồn cười, và một ý tưởng về tuổi thơ đọng lại rất lâu.', a: [
      [0, 'unprop', 've'], [0, 'pose', 'mot', 'chi-len'], [0, 'eyes', 'mot', 'thuong'],
      [0, 'prop', 'cl', 'checklist', [[{ kind: 'ok', text: 'Hai giọng kể khéo' }, { kind: 'ok', text: 'Trò chơi có logic riêng' }, { kind: 'ok', text: 'Ý tưởng về tuổi thơ' }, { kind: 'minus', text: 'Cốt truyện lỏng' }, { kind: 'minus', text: 'Lời bình đôi chỗ dư' }]], { x: 1330, y: 500, mode: 'cut' }],
      ['@hai', 'reveal', 'cl', 'rows', 0, 'pop'], ['@trò', 'reveal', 'cl', 'rows', 1, 'pop'], ['@một', 'reveal', 'cl', 'rows', 2, 'pop'] ] },
    { t: 'Đổi lại, cốt truyện lỏng, và lời bình đôi chỗ dư.', a: [
      [0, 'pose', 'mot', 'nhun-vai'], ['@cốt', 'reveal', 'cl', 'rows', 3, 'pop'], ['@lời', 'reveal', 'cl', 'rows', 4, 'pop'] ] },
    { t: 'Vậy, đây là sách thiếu nhi, hay sách cho người lớn đội lốt thiếu nhi?', a: [
      [0, 'unprop', 'cl'], [0, 'pose', 'mot', 'chong-cam'], ['@hay', 'fx', 'mot', 'dau-hoi'] ] },
    { t: 'Câu trả lời của tôi: đây là sách thiếu nhi, viết cho người lớn.', a: [
      [0, 'jump', 'mot', 'chi-nguoi-xem'], [0, 'eyes', 'mot', 'tron'],
      ['@thiếu', 'text', 'ans1', 'thiếu nhi', { x: 1330, y: 330, style: 'warm', mode: 'dap' }],
      ['@viết', 'text', 'ans2', 'viết cho người lớn', { x: 1330, y: 470, style: 'cool', mode: 'dap' }], ['e', 'unprop', 'ans1'], ['e', 'unprop', 'ans2'], ['e', 'cam', 'in', 'mot'] ] },
    { t: 'Trẻ con đọc sẽ thấy một đám bạn nghịch giống mình. Người lớn đọc sẽ thấy chính mình, ở cả hai phía.', a: [
      [0, 'cam', 'out'], [0, 'hide', 'mot', 'cut'], [0, 'bg', 'split2', 'slide'],
      [0, 'show', 'motnho', { x: 470, mode: 'pop' }], [0, 'eyes', 'motnho', 'cuoi'], [0, 'jump', 'motnho', 'an-mung'], [0, 'speaker', 'motnho'],
      ['@Người', 'speaker', 'mot2'], ['@Người', 'show', 'mot2', { x: 1450, flip: true, mode: 'pop' }], ['@Người', 'eyes', 'mot2', 'nham'], ['@hai', 'eyes', 'mot2', 'cuoi'] ] },
    { t: 'Nên đọc, nếu bạn đã đi làm, đang hơi mệt, và lâu rồi không làm gì chỉ vì nó vui.', a: [
      [0, 'speaker', 'mot'], [0, 'bg', 'A', 'cut'], [0, 'hide', 'motnho', 'cut'], [0, 'hide', 'mot2', 'cut'], [0, 'show', 'mot', { x: A, mode: 'cut' }],
      [0, 'pose', 'mot', 'chi-nguoi-xem'], [0, 'eyes', 'mot', 'thuong'], [0, 'text', 'r1', 'Nên đọc', { x: 1330, y: 200, style: 'dark', mode: 'dap' }],
      ['@mệt,', 'eyes', 'mot', 'nham'], ['@vui.', 'eyes', 'mot', 'cuoi'] ] },
    { t: 'Nên đọc, nếu bạn là phụ huynh, nhất là khi vừa nói câu không được đâu với con. Ba lần trong một buổi sáng.', a: [
      [0, 'pose', 'mot', 'chi-len'], ['@không', 'eyes', 'mot', 'luom'], ['@không', 'text', 'r1b', 'không được đâu', { x: 1330, y: 420, style: 'cool', mode: 'dap' }],
      ['@Ba', 'text', 'r1c', 'x3', { x: 1630, y: 420, size: 110, color: '#D9661A', mode: 'pop' }], ['@sáng.', 'fx', 'mot', 'mo-hoi'] ] },
    { t: 'Các bạn nhỏ từ khoảng mười tuổi đọc vẫn vui, và nên giữ lại cuốn sách, để đọc lần hai khi lớn.', a: [
      [0, 'unprop', 'r1b'], [0, 'unprop', 'r1c'], [0, 'pose', 'mot', 'ok'], [0, 'eyes', 'mot', 'cuoi'],
      ['@nhỏ', 'show', 'motnho', { x: 1330, flip: true, mode: 'pop' }], ['@vui,', 'pose', 'motnho', 'chao'], ['@vui,', 'eyes', 'motnho', 'cuoi'] ] },
    { t: 'Có thể bỏ qua, nếu bạn cần một câu chuyện có cao trào kịch tính. Lúc đó, hãy đọc Tôi thấy hoa vàng trên cỏ xanh trước.', a: [
      [0, 'hide', 'motnho'], [0, 'unprop', 'r1'], [0, 'pose', 'mot', 'chia-tay'], [0, 'eyes', 'mot', 'thuong'],
      [0, 'text', 'r2', 'Có thể bỏ qua', { x: 1330, y: 200, style: 'light', mode: 'dap' }], ['@Tôi', 'prop', 'book2', 'book2', [], { x: 1330, y: 580, s: 0.85, mode: 'pop' }] ] },
    { t: 'Về tay nghề, tôi chấm tám trên mười. Hai điểm còn lại, tôi để dành cho tuổi thơ của bạn tự chấm.', a: [
      [0, 'unprop', 'r2'], [0, 'unprop', 'book2'], [0, 'pose', 'mot', 'cam-sach'], ['@tám', 'text', 'sc', '8/10', { x: 1330, y: 450, size: 280, mode: 'dap' }],
      ['@Hai', 'pose', 'mot', 'chi-nguoi-xem'], ['@Hai', 'eyes', 'mot', 'cuoi'], ['@tự', 'fx', 'mot', 'lap-lanh'] ] },
    { t: 'Còn về cảm xúc thì… đây là kiểu sách đọc xong, rất dễ muốn nhắn tin cho một đứa bạn hồi nhỏ.', a: [
      [0, 'unprop', 'sc'], [0, 'eyes', 'mot', 'nham'], [0, 'pose', 'mot', 'dung'], ['@đây', 'bg', 'xom', 'fade'], ['@đây', 'move', 'mot', XOM, 12],
      ['@nhắn', 'show', 'mui', { x: 1150, flip: true, mode: 'pop' }], ['@nhắn', 'show', 'tisun', { x: 1400, flip: true, mode: 'pop' }],
      ['@bạn', 'eyes', 'mui', 'cuoi'], ['@bạn', 'jump', 'mui', 'chao'] ] },
    { t: 'Rồi phát hiện ra nó đã có hai con. Và nó cũng vừa đọc lại cuốn này.', a: [
      ['@hai', 'eyes', 'mot', 'tron'], ['@hai', 'fx', 'mot', 'mo-hoi'], ['@cũng', 'eyes', 'mot', 'cuoi'], ['@cũng', 'eyes', 'tisun', 'cuoi'], ['@lại', 'fx', 'mui', 'lap-lanh'] ] },
    { beat: 0.5, a: [] },
    { t: 'Và nếu phải chấm một điểm sáng tạo, tôi chấm cuốn này: kem que.', a: [
      [0, 'bg', 'A', 'cut'], [0, 'hide', 'mui', 'cut'], [0, 'hide', 'tisun', 'cut'], [0, 'move', 'mot', A, 0],
      [0, 'pose', 'mot', 'chi-len'], [0, 'eyes', 'mot', 'thuong'], ['@kem', 'prop', 'kem', 'icecream', [], { x: 1330, y: 480, mode: 'pop' }], ['@que.', 'fx', 'mot', 'lap-lanh'] ] },
    { t: 'Ngọt, mát, đúng vị tuổi thơ, và tan nhanh hơn bạn muốn.', a: [
      [0, 'pose', 'mot', 'ok'], [0, 'eyes', 'mot', 'cuoi'], ['@tan', 'drip', 'kem'] ] },
    { beat: 0.6, a: [] },
    { t: 'Cũng giống tuổi thơ.', a: [[0, 'cam', 'in', 'mot'], [0, 'eyes', 'mot', 'nham'], [0, 'pose', 'mot', 'dung']] },
    { t: 'Đây là cảm nhận của riêng tôi. Bạn đã đọc cuốn này chưa, và đọc lần đầu năm mấy tuổi? Kể tôi nghe ở phần bình luận nhé.', a: [
      [0, 'cam', 'out'], [0, 'unprop', 'kem'], [0, 'eyes', 'mot', 'cuoi'], [0, 'pose', 'mot', 'chi-nguoi-xem'],
      ['@Bạn', 'prop', 've', 'ticket', [], { ...TK, mode: 'pop' }], ['@Kể', 'stamp', 've', 5] ] },
    { t: 'Tôi là Mọt, người đọc sách hộ bạn. Hẹn gặp ở chuyến tàu sau.', a: [
      [0, 'unprop', 've'], [0, 'jump', 'mot', 'chao'], [0, 'eyes', 'mot', 'cuoi'], ['e', 'endcard'] ] },
  ];
  root.SCRIPT.forEach((s, i) => { s.i = i; });
})(typeof window !== 'undefined' ? window : globalThis);
