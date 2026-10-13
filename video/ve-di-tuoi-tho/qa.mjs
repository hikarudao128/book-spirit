// Kiểm tra tĩnh kịch bản dựng trước khi tạo giọng và render.
// Chạy: node qa.mjs   (thoát mã 1 nếu có lỗi)
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
require('./script.js');
const S = globalThis.SCRIPT;

const ACTIONS = new Set(['bg', 'show', 'hide', 'move', 'flip', 'pose', 'jump', 'eyes', 'mouth', 'talk', 'speaker', 'fx', 'prop', 'text',
  'unprop', 'stamp', 'flipcard', 'tilt', 'progress', 'reveal', 'sign', 'drip', 'glow', 'dim', 'cam', 'shake', 'endcard']);
const ACTORS = new Set(['mot', 'mot2', 'motnho', 'mui', 'muilon', 'haico', 'tisun', 'tun', 'anh', 'em']);
const POSES = new Set(['dung', 'chao', 'chi-len', 'chia-tay', 'nhun-vai', 'chong-cam', 'ok', 'khoanh-tay', 'chi-nguoi-xem', 'an-mung', 'cam-sach']);
const EYES = new Set(['thuong', 'cuoi', 'tron', 'luom', 'x', 'nham']);
const MOUTHS = new Set(['cuoi', 'sun', 'mim', 'o', 'meo', 'ngam']);
const FX = new Set(['zzz', 'set', 'mo-hoi', 'lap-lanh', 'dau-hoi', 'bong-nghi']);
const BUILDERS = new Set(['ticket', 'book1', 'book2', 'scale', 'chapters', 'album', 'strikePage', 'markPage', 'checklist', 'icecream', 'bubble', 'sign']);
const BGS = new Set(['A', 'xom', 'office', 'split', 'split2', 'end']);
const STYLES = new Set(['dark', 'light', 'warm', 'cool']);

const norm = (w) => w.toLowerCase().replace(/[.,:;!?…"“”()]/g, '');
function wordIndex(text, token) {
  const [tok, nth] = token.slice(1).split('#');
  const words = text.split(/\s+/), want = +(nth || 1);
  let c = 0;
  for (let i = 0; i < words.length; i++) if (words[i].toLowerCase() === tok.toLowerCase() && ++c === want) return i;
  c = 0;
  for (let i = 0; i < words.length; i++) if (norm(words[i]) === norm(tok) && ++c === want) return i;
  return -1;
}

const errors = [], warns = [];
const live = new Set();          // đồ vật đang có trên màn hình (theo thứ tự kịch bản, gần đúng)
let words = 0;
S.forEach((s, i) => {
  const where = `#${i} "${(s.t || 'beat').slice(0, 40)}"`;
  if (s.t) {
    words += s.t.split(/\s+/).length;
    if (s.say && s.say.split(/\s+/).length !== s.t.split(/\s+/).length) errors.push(`${where}: "say" phải có cùng số chữ với lời thoại`);
    if (s.t.length > 170) warns.push(`${where}: câu dài ${s.t.length} ký tự, phụ đề sẽ phải chia nhiều mảnh`);
  }
  for (const [trig, name, ...args] of s.a || []) {
    if (!ACTIONS.has(name)) errors.push(`${where}: hành động lạ "${name}"`);
    if (typeof trig === 'string' && trig[0] === '@') {
      if (!s.t) errors.push(`${where}: dòng im lặng không dùng được trigger ${trig}`);
      else if (wordIndex(s.t, trig) < 0) errors.push(`${where}: không tìm thấy từ ${trig}`);
    }
    const [a0, a1, a2] = args;
    if (['show', 'hide', 'move', 'flip', 'pose', 'jump', 'eyes', 'mouth', 'talk', 'speaker', 'fx'].includes(name) && !ACTORS.has(a0)) errors.push(`${where}: nhân vật lạ "${a0}"`);
    if ((name === 'pose' || name === 'jump') && !POSES.has(a1)) errors.push(`${where}: tư thế lạ "${a1}"`);
    if (name === 'eyes' && !EYES.has(a1)) errors.push(`${where}: mắt lạ "${a1}"`);
    if (name === 'mouth' && a1 !== null && !MOUTHS.has(a1)) errors.push(`${where}: miệng lạ "${a1}"`);
    if (name === 'fx' && !FX.has(a1)) errors.push(`${where}: hiệu ứng lạ "${a1}"`);
    if (name === 'bg' && !BGS.has(a0)) errors.push(`${where}: nền lạ "${a0}"`);
    if (name === 'prop') { if (!BUILDERS.has(a1)) errors.push(`${where}: đồ vật lạ "${a1}"`); live.add(a0); }
    if (name === 'text') { if (a2.style && !STYLES.has(a2.style)) errors.push(`${where}: kiểu nhãn lạ "${a2.style}"`); live.add(a0); }
    if (name === 'sign') live.add(a0);
    if (name === 'unprop') { if (!live.has(a0)) warns.push(`${where}: gỡ "${a0}" nhưng chưa thấy nó được tạo`); live.delete(a0); }
    if (['stamp', 'flipcard', 'tilt', 'progress', 'reveal', 'drip'].includes(name) && !live.has(a0)) errors.push(`${where}: "${name}" trên "${a0}" chưa có trên màn hình`);
  }
});
if (live.size) warns.push(`Đồ vật còn lại tới cuối (màn kết sẽ dọn): ${[...live].join(', ')}`);
console.log(`${S.length} mục, ${S.filter((s) => s.t).length} câu, ${words} âm tiết lời thoại`);
warns.forEach((w) => console.log('CẢNH BÁO', w));
errors.forEach((e) => console.log('LỖI', e));
console.log(errors.length ? `${errors.length} lỗi` : 'Không có lỗi');
process.exit(errors.length ? 1 : 0);
