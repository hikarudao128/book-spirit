// Engine dựng hình theo từng khung cho video người que (bản mượt, 60 khung/giây).
// Mọi trạng thái là hàm tất định của số khung: chạy lại từ 0 luôn ra cùng một kết quả,
// nên nhiều tiến trình có thể render song song các đoạn khác nhau.
// Kịch bản (script.js) và timing.json vẫn tính theo 24 khung/giây; engine tự quy đổi.
(function () {
  'use strict';
  const FPS = 60, SRC_FPS = 24, W = 1920, H = 1080, GROUND = 930;
  const R24 = FPS / SRC_FPS;                       // hệ số đổi khung 24 → 60
  const fr = (n24) => Math.max(1, Math.round(n24 * R24));
  const sec = (s) => Math.max(1, Math.round(s * FPS));
  const NS = 'http://www.w3.org/2000/svg';
  const INK = '#1D1D1F', SKIN = '#FBE3D6', RED = '#D1495B';
  const mk = (tag, attrs = {}, parent) => {
    const e = document.createElementNS(NS, tag);
    for (const k in attrs) e.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(e);
    return e;
  };
  const lerp = (a, b, t) => a + (b - a) * t;
  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
  const smooth = (t) => t * t * (3 - 2 * t);
  const inOut = (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);
  const outC = (t) => 1 - Math.pow(1 - t, 3);
  const inC = (t) => t * t * t;
  const outBack = (t, s = 1.70158) => { const c3 = s + 1; return 1 + c3 * Math.pow(t - 1, 3) + s * Math.pow(t - 1, 2); };
  const inBack = (t, s = 1.70158) => (s + 1) * t * t * t - s * t * t;
  function outBounce(t) {
    const n = 7.5625, d = 2.75;
    if (t < 1 / d) return n * t * t;
    if (t < 2 / d) return n * (t -= 1.5 / d) * t + 0.75;
    if (t < 2.5 / d) return n * (t -= 2.25 / d) * t + 0.9375;
    return n * (t -= 2.625 / d) * t + 0.984375;
  }
  function rng(seed) { let s = seed >>> 0; return () => { s = (Math.imul(s, 1664525) + 1013904223) >>> 0; return s / 4294967296; }; }
  const angDiff = (a, b) => { let d = b - a; while (d > Math.PI) d -= 2 * Math.PI; while (d < -Math.PI) d += 2 * Math.PI; return d; };
  const f1 = (v) => v.toFixed(1), f3 = (v) => v.toFixed(3);

  // ---------- Tư thế ----------
  const SH = { L: [-24, -180], R: [24, -180] };
  const POSES = {
    'dung':          { L: { e: [-34, -142], h: [-36, -104], s: 'nam' }, R: { e: [34, -142], h: [36, -104], s: 'nam' } },
    'chao':          { L: { e: [-34, -142], h: [-36, -104], s: 'nam' }, R: { e: [50, -198], h: [58, -248], s: 'v' } },
    'chi-len':       { L: { e: [-34, -142], h: [-36, -104], s: 'nam' }, R: { e: [52, -178], h: [60, -228], s: 'chi' } },
    'chia-tay':      { L: { e: [-34, -142], h: [-36, -104], s: 'nam' }, R: { e: [58, -160], h: [98, -172], s: 'xoe' } },
    'nhun-vai':      { L: { e: [-52, -156], h: [-74, -178], s: 'xoe' }, R: { e: [52, -156], h: [76, -178], s: 'xoe' } },
    'chong-cam':     { L: { e: [-6, -146], h: [40, -150], s: 'nam' }, R: { e: [46, -150], h: [30, -198], s: 'nam' } },
    'ok':            { L: { e: [-34, -142], h: [-36, -104], s: 'nam' }, R: { e: [54, -168], h: [74, -210], s: 'ok' } },
    'khoanh-tay':    { L: { e: [-36, -150], h: [22, -160], s: 'nam' }, R: { e: [36, -148], h: [-18, -152], s: 'nam' } },
    'chi-nguoi-xem': { L: { e: [-34, -142], h: [-36, -104], s: 'nam' }, R: { e: [62, -178], h: [110, -188], s: 'chi' } },
    'an-mung':       { L: { e: [-52, -216], h: [-60, -266], s: 'nam' }, R: { e: [52, -216], h: [60, -266], s: 'nam' } },
    'cam-sach':      { L: { e: [-14, -142], h: [18, -162], s: 'nam' }, R: { e: [52, -150], h: [94, -162], s: 'nam' } },
  };
  // Tay biểu diễn bằng góc + độ dài (vai → khuỷu, khuỷu → bàn tay) để nội suy theo cung, không co rút.
  function toPolar(side, p) {
    const sh = SH[side];
    const ex = p.e[0] - sh[0], ey = p.e[1] - sh[1], hx = p.h[0] - p.e[0], hy = p.h[1] - p.e[1];
    return { a1: Math.atan2(ey, ex), l1: Math.hypot(ex, ey), a2: Math.atan2(hy, hx), l2: Math.hypot(hx, hy), s: p.s };
  }
  function fromPolar(side, q) {
    const sh = SH[side];
    const e = [sh[0] + Math.cos(q.a1) * q.l1, sh[1] + Math.sin(q.a1) * q.l1];
    return { e, h: [e[0] + Math.cos(q.a2) * q.l2, e[1] + Math.sin(q.a2) * q.l2], s: q.s };
  }
  const clonePose = (p) => JSON.parse(JSON.stringify(p));

  // ---------- Nhân vật ----------
  const HAIR = {
    // Mọi chỗ lõm giữa hai chỏm tóc nằm trên đỉnh đầu (y < -332) hoặc ngoài mép đầu, để góc bo của đầu không lòi ra.
    spiky: 'M -68 -270 L -76 -318 L -62 -322 L -56 -352 L -34 -336 L -16 -366 L 4 -340 L 26 -364 L 40 -338 L 62 -350 L 66 -324 L 78 -304 L 70 -268 Q 40 -298 0 -296 Q -40 -298 -68 -270 Z',
    tuft: 'M -66 -278 Q -68 -332 -16 -340 Q 34 -346 66 -310 L 68 -282 Q 30 -302 -66 -278 Z M -14 -338 L -24 -374 L 0 -346 L 8 -380 L 20 -342 Z',
    neat: 'M -66 -280 Q -66 -338 0 -340 Q 66 -340 68 -288 Q 24 -314 -16 -302 Q -42 -296 -66 -280 Z',
    short: 'M -64 -288 Q -62 -336 0 -338 Q 64 -336 66 -290 Q 0 -312 -64 -288 Z',
    bob: 'M -72 -228 Q -80 -344 0 -346 Q 80 -344 74 -228 L 60 -228 Q 62 -298 30 -300 Q 0 -296 -40 -306 Q -58 -298 -58 -228 Z',
    topknot: 'M -64 -284 Q -60 -336 0 -338 Q 62 -336 66 -286 Q 0 -308 -64 -284 Z M -20 -352 a 22 22 0 1 0 40 0 a 22 22 0 1 0 -40 0 Z',
  };
  const POLO = '#1E4FC2', POLO_RED = '#E03A3E';   // áo polo xanh của Mọt
  const CHARS = {
    mot:    { k: 1.8, hair: 'spiky', hairC: '#263859', shirt: POLO, polo: true, neck: 'lanyard' },
    mot2:   { k: 1.8, hair: 'spiky', hairC: '#263859', shirt: POLO, polo: true, neck: 'lanyard' },
    motnho: { k: 1.3, hair: 'spiky', hairC: '#263859', shirt: '#2A9D8F', neck: 'scarf' },
    mui:    { k: 1.25, hair: 'tuft', hairC: '#4A3426', shirt: '#F4C542' },
    muilon: { k: 1.75, hair: 'neat', hairC: '#4A3426', shirt: '#6C7A89', neck: 'tie', bags: true },
    haico:  { k: 1.22, legs: 1.75, hair: 'short', hairC: '#2B2B2B', shirt: '#A8754E' },
    tisun:  { k: 1.18, hair: 'bob', hairC: '#3B2A20', shirt: '#F28DB2' },
    tun:    { k: 0.98, hair: 'topknot', hairC: '#2B2B2B', shirt: '#B9A7E6' },
    anh:    { k: 1.15, hair: 'short', hairC: '#3A2A1F', shirt: '#E07A5F' },
    em:     { k: 0.98, hair: 'tuft', hairC: '#3A2A1F', shirt: '#81B29A' },
  };
  const E1 = [6, -262], E2 = [36, -262], MO = [24, -224];
  function eyeSVG(kind, [x, y]) {
    const st = `stroke="${INK}" stroke-width="6" stroke-linecap="round" fill="none"`;
    switch (kind) {
      case 'blink': return `<path d="M ${x - 9} ${y} L ${x + 9} ${y}" ${st}/>`;
      case 'half': return `<path d="M ${x} ${y - 4} L ${x} ${y + 5}" ${st}/>`;
      case 'cuoi': return `<path d="M ${x - 9} ${y + 4} Q ${x} ${y - 9} ${x + 9} ${y + 4}" ${st}/>`;
      case 'nham': return `<path d="M ${x - 9} ${y - 2} Q ${x} ${y + 7} ${x + 9} ${y - 2}" ${st}/>`;
      case 'tron': return `<circle cx="${x}" cy="${y}" r="10" fill="#FFFFFF" stroke="${INK}" stroke-width="5"/><circle cx="${x + 1}" cy="${y + 1}" r="4" fill="${INK}"/>`;
      case 'luom': return `<path d="M ${x - 10} ${y - 3} L ${x + 10} ${y - 3}" ${st}/><circle cx="${x + 5}" cy="${y + 3}" r="4" fill="${INK}"/>`;
      case 'x': return `<path d="M ${x - 8} ${y - 8} L ${x + 8} ${y + 8} M ${x + 8} ${y - 8} L ${x - 8} ${y + 8}" ${st}/>`;
      default: return `<path d="M ${x} ${y - 10} L ${x} ${y + 10}" ${st}/>`;
    }
  }
  function mouthSVG(kind, [x, y]) {
    const st = `stroke="${INK}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"`;
    if (kind.startsWith('talk:')) {            // miệng nói: độ mở liên tục theo âm lượng
      const o = +kind.slice(5);
      const ry = 2.5 + 9.5 * o, rx = 8 + 3.5 * o;
      return `<ellipse cx="${x}" cy="${f1(y + o * 2)}" rx="${f1(rx)}" ry="${f1(ry)}" fill="${RED}" ${st}/>`;
    }
    switch (kind) {
      case 'cuoi': return `<path d="M ${x - 14} ${y - 5} Q ${x} ${y + 16} ${x + 14} ${y - 5} Z" fill="${RED}" ${st}/>`;
      case 'sun': return `<path d="M ${x - 16} ${y - 6} Q ${x} ${y + 18} ${x + 16} ${y - 6} Z" fill="${RED}" ${st}/><rect x="${x - 12}" y="${y - 5}" width="24" height="7" fill="#FFFFFF"/><rect x="${x - 2}" y="${y - 5}" width="6" height="7" fill="${INK}"/>`;
      case 'mim': return `<path d="M ${x - 11} ${y} Q ${x} ${y + 7} ${x + 12} ${y - 5}" fill="none" ${st}/>`;
      case 'o': return `<circle cx="${x}" cy="${y + 2}" r="8" fill="${RED}" ${st}/>`;
      case 'meo': return `<path d="M ${x - 12} ${y + 4} Q ${x - 4} ${y - 7} ${x + 2} ${y + 2} Q ${x + 8} ${y + 7} ${x + 13} ${y - 2}" fill="none" ${st}/>`;
      default: return `<path d="M ${x - 8} ${y} L ${x + 8} ${y}" fill="none" ${st}/>`;
    }
  }
  function handSVG() {                // bàn tay tròn, không vẽ ngón; các kiểu chi/v/ok/xoe chỉ còn khác ở vị trí tay
    return `<circle r="11" fill="${SKIN}" stroke="${INK}" stroke-width="4"/>`;
  }
  const FX_SVG = {
    'zzz': `<text x="70" y="-372" font-family="Baloo 2" font-weight="800" font-size="46" fill="${INK}">Z<tspan font-size="36" dy="-22">z</tspan><tspan font-size="28" dy="-18">z</tspan></text>`,
    'set': `<path d="M -92 -380 L -66 -380 L -80 -346 L -58 -346 L -98 -296 L -86 -336 L -106 -336 Z" fill="#F6C343" stroke="${INK}" stroke-width="5" stroke-linejoin="round"/>`,
    'mo-hoi': `<path d="M 76 -326 Q 62 -300 76 -294 Q 90 -300 76 -326 Z" fill="#8CC8F0" stroke="${INK}" stroke-width="4"/>`,
    'lap-lanh': ['M 96 -352 l 6 -16 l 6 16 l 16 6 l -16 6 l -6 16 l -6 -16 l -16 -6 Z', 'M 70 -390 l 4 -10 l 4 10 l 10 4 l -10 4 l -4 10 l -4 -10 l -10 -4 Z', 'M 126 -310 l 4 -10 l 4 10 l 10 4 l -10 4 l -4 10 l -4 -10 l -10 -4 Z'].map((d) => `<path d="${d}" fill="#F6C343" stroke="${INK}" stroke-width="3" stroke-linejoin="round"/>`).join(''),
    'dau-hoi': `<text x="78" y="-322" font-family="Baloo 2" font-weight="800" font-size="84" fill="#D9661A" stroke="${INK}" stroke-width="3">?</text>`,
    'bong-nghi': `<circle cx="78" cy="-330" r="7" fill="#FFFFFF" stroke="${INK}" stroke-width="4"/><circle cx="96" cy="-356" r="11" fill="#FFFFFF" stroke="${INK}" stroke-width="4"/><ellipse cx="160" cy="-410" rx="64" ry="42" fill="#FFFFFF" stroke="${INK}" stroke-width="5"/><text x="160" y="-398" text-anchor="middle" font-family="Baloo 2" font-weight="800" font-size="40" fill="${INK}">…</text>`,
  };
  const FX_SFX = { 'lap-lanh': 'chime', 'set': 'thud', 'dau-hoi': 'pop', 'mo-hoi': 'pop', 'bong-nghi': 'pop', 'zzz': 'pop' };

  // ---------- Trạng thái toàn cục ----------
  let F = -1;
  let tweens = [], laters = [], sfx = [];
  let events = [], evPtr = 0;
  let amp24 = null;                  // biên độ giọng theo khung 24
  let ampS = 0;                      // biên độ đã làm mượt (bám nhanh, nhả chậm)
  let speaker = 'mot';
  const cam = { s: 1, fx: W / 2, fy: H / 2, shakeF: -1, shakeA: 0 };
  const actors = {}, items = {}, bgs = {};
  let curBg = null, stamped = 0;
  let wipe = null;                   // {f0} khi đang chạy tấm che chuyển cảnh
  let subChunks = [], subEl = null;
  let L = {};
  const tween = (n, fn, delay = 0) => tweens.push({ f0: F + delay, n: Math.max(1, n), fn });
  const later = (delay, fn) => laters.push({ f: F + delay, fn });
  const playSfx = (type, delay = 0) => sfx.push({ frame: (F + delay) / R24, type });
  const time = () => F / FPS;
  function ampAt(f) {                // nội suy biên độ 24 khung sang 60 khung
    if (!amp24) return 0;
    const x = f / R24, i = Math.floor(x), t = x - i;
    return lerp(amp24[i] || 0, amp24[i + 1] || 0, t);
  }

  // ---------- Tạo nhân vật ----------
  function makeActor(id) {
    const d = CHARS[id];
    const legL = d.legs || 1, u = -(102 * legL - 102);
    const g = mk('g', { display: 'none' }, L.actors);
    const legs = mk('g', { stroke: INK, 'stroke-width': 7, 'stroke-linecap': 'round', fill: 'none' }, g);
    const hip = -16 - 102 * legL;
    const legPath = mk('path', {}, legs);
    mk('ellipse', { cx: -20, cy: -9, rx: 16, ry: 9, fill: '#FFFFFF', 'stroke-width': 5 }, legs);
    mk('ellipse', { cx: 21, cy: -9, rx: 16, ry: 9, fill: '#FFFFFF', 'stroke-width': 5 }, legs);
    const up0 = mk('g', { transform: `translate(0 ${u})` }, g);
    const upper = mk('g', {}, up0);
    mk('path', { d: 'M -27 -190 L 27 -190 L 33 -112 Q 0 -106 -33 -112 Z', fill: d.shirt, stroke: INK, 'stroke-width': 6, 'stroke-linejoin': 'round' }, upper);
    if (d.polo) {                         // cổ polo viền trắng + logo đỏ trên ngực
      for (const fl of ['M -22 -192 L -1 -191 L -10 -170 Z', 'M 1 -191 L 22 -192 L 10 -170 Z']) {
        mk('path', { d: fl, fill: d.shirt, stroke: INK, 'stroke-width': 4, 'stroke-linejoin': 'round' }, upper);
      }
      mk('path', { d: 'M -18 -189 L -10 -174 M 18 -189 L 10 -174', stroke: '#FFFFFF', 'stroke-width': 2.5, 'stroke-linecap': 'round' }, upper);
      mk('rect', { x: -18, y: -168, width: 10, height: 7, rx: 1.5, fill: POLO_RED, stroke: INK, 'stroke-width': 2.5 }, upper);
    }
    let tie = null;
    if (d.neck === 'bookmark') {
      tie = mk('g', {}, upper);
      mk('path', { d: 'M -7 0 L 7 0 L 7 50 L 0 41 L -7 50 Z', fill: '#F08A24', stroke: INK, 'stroke-width': 4, 'stroke-linejoin': 'round' }, tie);
    } else if (d.neck === 'lanyard') {     // dây đeo thẻ: xanh đậm sọc đỏ, thẻ lắc theo thân
      tie = mk('g', {}, upper);
      const strap = 'M -12 0 L -2 38 M 12 0 L 2 38';
      mk('path', { d: strap, stroke: INK, 'stroke-width': 9, 'stroke-linecap': 'round', fill: 'none' }, tie);
      mk('path', { d: strap, stroke: '#1B2F7A', 'stroke-width': 5, 'stroke-linecap': 'round', fill: 'none' }, tie);
      mk('path', { d: strap, stroke: POLO_RED, 'stroke-width': 1.6, fill: 'none' }, tie);
      mk('rect', { x: -11, y: 35, width: 22, height: 30, rx: 3, fill: '#FFFFFF', stroke: INK, 'stroke-width': 3.5 }, tie);
      mk('path', { d: 'M -9.3 37 L 9.3 37 L 9.3 44 L -9.3 44 Z', fill: POLO_RED }, tie);
      mk('path', { d: 'M -6 51 L 6 51 M -6 57 L 3 57', stroke: '#9AA6B5', 'stroke-width': 2.5, 'stroke-linecap': 'round' }, tie);
    } else if (d.neck === 'tie') {
      tie = mk('g', {}, upper);
      mk('path', { d: 'M -7 0 L 7 0 L 10 56 L 0 68 L -10 56 Z', fill: '#2E3A59', stroke: INK, 'stroke-width': 4, 'stroke-linejoin': 'round' }, tie);
    } else if (d.neck === 'scarf') {
      mk('path', { d: 'M -28 -192 L 28 -192 L 6 -150 L 0 -138 L -6 -150 Z', fill: '#D62828', stroke: INK, 'stroke-width': 4, 'stroke-linejoin': 'round' }, upper);
    }
    const book = mk('g', { display: 'none' }, upper);
    book.innerHTML = `<path d="M 56 -114 L 18 -134 L 18 -190 L 56 -170 Z" fill="#FFFFFF" stroke="${INK}" stroke-width="5" stroke-linejoin="round"/><path d="M 56 -114 L 94 -134 L 94 -190 L 56 -170 Z" fill="#F4F6F8" stroke="${INK}" stroke-width="5" stroke-linejoin="round"/><path d="M 28 -160 L 48 -150 M 28 -148 L 48 -138 M 66 -150 L 86 -160 M 66 -138 L 86 -148" stroke="#9AA6B5" stroke-width="3"/>`;
    const head = mk('g', {}, upper);
    mk('rect', { x: -60, y: -332, width: 124, height: 140, rx: 26, fill: SKIN, stroke: INK, 'stroke-width': 6 }, head);
    mk('path', { d: HAIR[d.hair], fill: d.hairC, stroke: INK, 'stroke-width': 6, 'stroke-linejoin': 'round' }, head);
    if (d.bags) mk('path', { d: 'M -2 -244 Q 6 -238 14 -244 M 28 -244 Q 36 -238 44 -244', stroke: '#9A8FA6', 'stroke-width': 4, fill: 'none', 'stroke-linecap': 'round' }, head);
    const eyes = mk('g', {}, head), mouth = mk('g', {}, head);
    const arms = mk('g', { stroke: INK, 'stroke-width': 7, 'stroke-linecap': 'round', 'stroke-linejoin': 'round', fill: 'none' }, upper);
    const armL = mk('polyline', {}, arms), armR = mk('polyline', {}, arms);
    let sleeves = null;
    if (d.polo) {                         // tay áo ngắn, xoay theo cánh tay trên, viền trắng ở gấu
      sleeves = ['L', 'R'].map(() => {
        const sg = mk('g', {}, upper);
        mk('path', { d: 'M -4 -10 L 25 -9 L 25 9 L -4 10 Z', fill: d.shirt }, sg);
        mk('path', { d: 'M 20 -8 L 20 8', stroke: '#FFFFFF', 'stroke-width': 3 }, sg);
        mk('path', { d: 'M -1 -10 L 25 -9 L 25 9 L -1 10', fill: 'none', stroke: INK, 'stroke-width': 4.5, 'stroke-linejoin': 'round', 'stroke-linecap': 'round' }, sg);
        return sg;
      });
    }
    upper.appendChild(book);               // sách nằm trên tay áo, dưới bàn tay: hai tay cầm hai mép bìa
    const handL = mk('g', {}, upper), handR = mk('g', {}, upper);
    const fxg = mk('g', {}, L.fx);
    const r = rng(id.split('').reduce((a, c) => a * 31 + c.charCodeAt(0), 7));
    const a = {
      id, d, u, hip, g, legPath, upper, head, tie, book, sleeves, eyesG: eyes, mouthG: mouth, armL, armR, handL, handR, fxg, r,
      vis: false, x: 0, y: GROUND, flip: false, k: d.k, pop: 1, sq: 0, dy: 0, slideX: 0, lean: 0,
      arms: clonePose(POSES.dung), pose: 'dung', eyes: 'thuong', mouthRest: 'ngam', mouthOv: null, fakeTalk: false,
      blinkF: -100, nextBlink: sec(0.5) + Math.floor(r() * sec(2)), tieA: 0, tieV: 0, kicks: [], fx: [],
      phase: r() * Math.PI * 2, talkS: 0, last: { eyes: '', mouth: '', hL: '', hR: '' },
    };
    actors[id] = a;
    return a;
  }
  const actor = (id) => actors[id] || makeActor(id);
  function headWorld(a) {
    const sx = a.flip ? -1 : 1;
    return [a.x + a.slideX + sx * 20 * a.k, a.y + a.dy + (-262 + a.u) * a.k];
  }
  function blinkKey(a) {               // chớp mắt: nửa → nhắm → nhắm → nửa (khoảng 80 ms)
    const age = F - a.blinkF;
    if (age < 0 || age > 4 || ['x', 'nham'].includes(a.eyes)) return a.eyes;
    if (age === 0 || age === 4) return a.eyes === 'thuong' ? 'half' : 'blink';
    return 'blink';
  }
  function drawActor(a) {
    a.g.setAttribute('display', a.vis ? 'inline' : 'none');
    a.fxg.setAttribute('display', a.vis ? 'inline' : 'none');
    if (!a.vis) return;
    const sx = a.flip ? -1 : 1, s = a.k * a.pop;
    const sqx = 1 + a.sq * 0.12, sqy = 1 - a.sq * 0.12;   // nén/giãn khi lấy đà và tiếp đất
    a.g.setAttribute('transform', `translate(${f1(a.x + a.slideX)} ${f1(a.y + a.dy)}) scale(${f3(s * sx * sqx)} ${f3(s * sqy)})`);
    const t = time() + a.phase;
    const breath = Math.sin(t * Math.PI * 2 / 2.2) * 1.6;
    const sway = Math.sin(t * Math.PI * 2 / 3.7) * 0.7 + a.lean;
    a.upper.setAttribute('transform', `translate(0 ${f1(breath)}) rotate(${f3(sway)} 0 -118)`);
    // đầu gật nhẹ theo giọng nói
    const nod = a.talkS * (2.2 + Math.sin(t * 9) * 1.4), tilt = a.talkS * Math.sin(t * 3.1) * 2.2;
    a.head.setAttribute('transform', `translate(0 ${f1(-nod)}) rotate(${f3(tilt)} 0 -192)`);
    if (a.tie) a.tie.setAttribute('transform', `translate(4 -188) rotate(${f3(a.tieA - sway * 1.5)})`);
    a.legPath.setAttribute('d', `M -9 ${a.hip} L -15 -16 M 9 ${a.hip} L 15 -16`);
    const ek = blinkKey(a);
    if (ek !== a.last.eyes) { a.eyesG.innerHTML = eyeSVG(ek, E1) + eyeSVG(ek, E2); a.last.eyes = ek; }
    const mkey = mouthFor(a);
    if (mkey !== a.last.mouth) { a.mouthG.innerHTML = mouthSVG(mkey, MO); a.last.mouth = mkey; }
    for (const side of ['L', 'R']) {
      const p = a.arms[side], sh = SH[side];
      a['arm' + side].setAttribute('points', `${sh[0]},${sh[1]} ${f1(p.e[0])},${f1(p.e[1])} ${f1(p.h[0])},${f1(p.h[1])}`);
      const ang = Math.atan2(p.h[1] - p.e[1], p.h[0] - p.e[0]) * 180 / Math.PI;
      if (a.sleeves) {
        const ua = Math.atan2(p.e[1] - sh[1], p.e[0] - sh[0]) * 180 / Math.PI;
        a.sleeves[side === 'L' ? 0 : 1].setAttribute('transform', `translate(${sh[0]} ${sh[1]}) rotate(${f1(ua)})`);
      }
      const hg = a['hand' + side];
      hg.setAttribute('transform', `translate(${f1(p.h[0])} ${f1(p.h[1])}) rotate(${f1(ang)})`);
      if (a.last['h' + side] !== p.s) { hg.innerHTML = handSVG(p.s); a.last['h' + side] = p.s; }
    }
    const [hx, hy] = headWorld(a);
    a.fxg.setAttribute('transform', `translate(${f1(hx + (a.flip ? -150 * a.k : 0))} ${f1(hy)}) scale(${a.k}) translate(-20 262)`);
  }
  function mouthFor(a) {
    if (a.mouthOv) return a.mouthOv;
    if (a.talkS < 0.07) return a.mouthRest;
    return 'talk:' + (Math.round(clamp(a.talkS, 0, 1) * 12) / 12).toFixed(3);
  }
  const TIE_W = 13, TIE_Z = 0.22;
  function stepActor(a) {
    if (F >= a.nextBlink) { a.blinkF = F; a.nextBlink = F + sec(2) + Math.floor(a.r() * sec(3)); }
    // độ mở miệng: bám nhanh khi to lên, nhả chậm khi nhỏ lại
    let target = 0;
    if (a.fakeTalk) target = 0.35 + 0.35 * Math.sin(time() * 17) * Math.sin(time() * 5.3);
    else if (a.id === speaker) target = ampS;
    a.talkS += (target - a.talkS) * (target > a.talkS ? 0.55 : 0.3);
    // dây đánh dấu: lò xo tắt dần, tính theo giây nên không phụ thuộc số khung
    a.kicks = a.kicks.filter((kk) => { if (kk.f <= F) { a.tieV += kk.v; return false; } return true; });
    const dt = 1 / FPS;
    const acc = -TIE_W * TIE_W * a.tieA - 2 * TIE_Z * TIE_W * a.tieV;
    a.tieV += acc * dt; a.tieA += a.tieV * dt;
    a.fx = a.fx.filter((fx) => {
      const age = F - fx.f0, popN = sec(0.28), outN = sec(0.2);
      let sc = 1;
      if (age < popN) sc = outBack(age / popN, 2.2);
      else if (age > fx.hold) sc = 1 - inC(clamp((age - fx.hold) / outN, 0, 1));
      const bob = Math.sin((age / FPS) * Math.PI * 2 * 1.2) * 4;
      fx.el.setAttribute('transform', `translate(0 ${f1(bob)}) translate(90 -340) scale(${f3(Math.max(0, sc))}) translate(-90 340)`);
      if (age > fx.hold + outN) { fx.el.remove(); return false; }
      return true;
    });
  }

  // ---------- Hành động nhân vật ----------
  function setPose(a, name, dur = 0.3) {
    const to = POSES[name];
    const fromQ = { L: toPolar('L', a.arms.L), R: toPolar('R', a.arms.R) };
    const toQ = { L: toPolar('L', to.L), R: toPolar('R', to.R) };
    a.book.setAttribute('display', name === 'cam-sach' ? 'inline' : 'none');
    a.pose = name;
    tween(sec(dur), (t) => {
      const e = outBack(t, 1.15);      // vượt đích một chút rồi về: có lực, không robot
      for (const side of ['L', 'R']) {
        const f = fromQ[side], b = toQ[side];
        const q = {
          a1: f.a1 + angDiff(f.a1, b.a1) * e, l1: lerp(f.l1, b.l1, e),
          a2: f.a2 + angDiff(f.a2, b.a2) * e, l2: lerp(f.l2, b.l2, e),
          s: t >= 0.45 ? b.s : f.s,
        };
        a.arms[side] = fromPolar(side, q);
      }
    });
    a.kicks.push({ f: F + sec(0.08), v: 110 });
    const lean = { 'chi-nguoi-xem': 2.5, 'chia-tay': 1.2, 'khoanh-tay': -1.5, 'chong-cam': 1, 'an-mung': 0, 'nhun-vai': 0 }[name] || 0;
    const l0 = a.lean;
    tween(sec(0.35), (t) => { a.lean = lerp(l0, lean, inOut(t)); });
  }
  function jump(a, name) {
    // lấy đà (hạ + nén) → bật lên (giãn) → tiếp đất có nảy nhỏ
    const n = sec(0.55);
    tween(n, (t) => {
      const s = t * 0.55;
      if (s < 0.12) { const k = smooth(s / 0.12); a.dy = 12 * k; a.sq = 0.6 * k; }
      else if (s < 0.27) { const k = (s - 0.12) / 0.15; a.dy = lerp(12, -16, outC(k)); a.sq = lerp(0.6, -0.5, k); }
      else if (s < 0.42) { const k = (s - 0.27) / 0.15; a.dy = lerp(-16, 3, inOut(k)); a.sq = lerp(-0.5, 0.25, k); }
      else { const k = (s - 0.42) / 0.13; a.dy = lerp(3, 0, outC(k)); a.sq = lerp(0.25, 0, outC(k)); }
    });
    later(sec(0.1), () => setPose(a, name, 0.26));
    a.kicks.push({ f: F + sec(0.3), v: 160 });
  }
  function showActor(a, o) {
    const run = () => {
      a.vis = true; a.x = o.x; if (o.flip !== undefined) a.flip = o.flip; a.dy = 0; a.slideX = 0; a.sq = 0;
      const mode = o.mode || 'pop';
      if (mode === 'pop') {
        a.pop = 0; playSfx('pop');
        tween(sec(0.36), (t) => { a.pop = outBack(t, 2.0); a.sq = Math.sin(t * Math.PI) * -0.35; });
        a.kicks.push({ f: F + sec(0.2), v: 90 });
      } else if (mode === 'slideR' || mode === 'slideL') {
        const from = mode === 'slideR' ? (W + 300 - o.x) : (-300 - o.x);
        a.slideX = from; a.pop = 1; playSfx('whoosh');
        tween(sec(0.5), (t) => { a.slideX = from * (1 - outBack(t, 1.1)); a.lean = (mode === 'slideR' ? 1 : -1) * 6 * Math.sin(t * Math.PI) * (1 - t); });
        a.kicks.push({ f: F + sec(0.4), v: 200 });
      } else a.pop = 1;
    };
    if (o.delay) later(fr(o.delay), run); else run();
  }
  function hideActor(a, mode = 'pop') {
    if (!a.vis) return;
    if (mode === 'cut') { a.vis = false; a.fx.forEach((fx) => fx.el.remove()); a.fx = []; return; }
    const p0 = a.pop;
    tween(sec(0.22), (t) => { a.pop = p0 * (1 - inBack(t, 1.6)); if (t >= 1) { a.vis = false; a.pop = 1; } });
  }
  function fxOn(a, name, hold24 = 36) {
    const el = mk('g', {}, a.fxg);
    el.innerHTML = FX_SVG[name];
    a.fx.push({ el, f0: F, hold: fr(hold24) });
    if (FX_SFX[name]) playSfx(FX_SFX[name]);
  }

  // ---------- Đồ vật ----------
  function placeItem(it) {
    const t = it.attach ? attachPos(it.attach) : [it.x, it.y];
    const s = it.s * it.pop;
    const age = (F - it.f0) / FPS;
    const float = it.float ? Math.sin(age * Math.PI * 2 / 3 + it.id.length) * 5 : 0;   // đồ vật lơ lửng nhẹ
    it.el.setAttribute('transform', `translate(${f1(t[0])} ${f1(t[1] + it.ty + float)}) rotate(${f3(it.rot)}) scale(${f3(s * it.sx)} ${f3(s)})`);
    it.el.setAttribute('opacity', f3(it.alpha));
    it.el.setAttribute('display', it.vis ? 'inline' : 'none');
    if (it.dripF !== undefined && it.obj.setDrip) it.obj.setDrip(Math.max(0, (F - it.dripF) / FPS));
  }
  function attachPos({ actor: id, lx, ly }) {
    const a = actors[id]; const sx = a.flip ? -1 : 1;
    return [a.x + a.slideX + sx * lx * a.k, a.y + a.dy + (ly + a.u) * a.k];
  }
  function addItem(id, obj, o) {
    if (items[id]) items[id].el.remove();
    const el = mk('g', {}, L.props);
    el.appendChild(obj.el);
    const it = { id, obj, el, f0: F, x: o.x ?? W / 2, y: o.y ?? H / 2, s: o.s ?? 1, sx: 1, pop: 1, ty: 0, rot: 0, alpha: 1, vis: true, attach: o.attach, float: !o.attach };
    items[id] = it;
    enter(it, o.mode || 'pop');
    return it;
  }
  function enter(it, mode) {
    if (mode === 'pop') {
      it.pop = 0; playSfx('pop');
      tween(sec(0.38), (t) => { it.pop = outBack(t, 2.0); it.rot = (1 - outC(t)) * -6; });
    } else if (mode === 'dap') {
      // rơi xuống theo trọng lực, nảy hai nhịp
      const n = sec(0.62);
      it.ty = -520;
      tween(n, (t) => { it.ty = -520 * (1 - outBounce(t)); });
      later(Math.round(n / 2.75), () => { shake(9); playSfx('thud'); });
    } else if (mode === 'fade') { it.alpha = 0; tween(sec(0.45), (t) => { it.alpha = inOut(t); }); }
  }
  function removeItem(id, mode = 'pop') {
    const it = items[id]; if (!it) return;
    delete items[id];
    if (mode === 'cut') { it.el.remove(); return; }
    const p0 = it.pop;
    tween(sec(0.24), (t) => { it.pop = p0 * (1 - inBack(t, 1.4)); it.alpha = 1 - inC(t); placeItem(it); if (t >= 1) it.el.remove(); });
  }
  function wrapPart(part) {
    if (part.__inner) return part.__inner;
    const inner = mk('g', {});
    while (part.firstChild) inner.appendChild(part.firstChild);
    part.appendChild(inner); part.__inner = inner;
    return inner;
  }

  // ---------- Nền và chuyển cảnh ----------
  function getBg(name) {
    if (bgs[name]) return bgs[name];
    let obj;
    if (name === 'A') { obj = { el: mk('g'), parts: {} }; mk('rect', { x: 0, y: 0, width: W, height: H, fill: '#FFFFFF' }, obj.el); }
    else if (name === 'xom') obj = PROPS.bgXom();
    else if (name === 'office') obj = PROPS.bgOffice();
    else if (name === 'split') obj = PROPS.bgSplit();
    else if (name === 'split2') obj = PROPS.bgSplit('lúc nhỏ', 'lúc lớn');
    else if (name === 'end') obj = PROPS.endCard();
    const wrap = mk('g', { display: 'none' }, L.bg);
    wrap.appendChild(obj.el);
    bgs[name] = { name, obj, el: wrap, alpha: 1 };
    return bgs[name];
  }
  function setBg(name, mode) {
    const nb = getBg(name), old = curBg;
    if (old === nb) return;
    L.bg.appendChild(nb.el);
    nb.el.setAttribute('display', 'inline');
    curBg = nb;
    if (mode === 'fade') {
      nb.alpha = 0;
      tween(sec(0.7), (t) => { nb.alpha = inOut(t); if (t >= 1 && old && old !== curBg) old.el.setAttribute('display', 'none'); });
    } else { nb.alpha = 1; if (old) old.el.setAttribute('display', 'none'); }
  }
  function bgPart(name) { return curBg && curBg.obj.parts ? curBg.obj.parts[name] : null; }
  // Tấm che quét ngang: che trong WIPE_IN khung, đổi cảnh lúc che kín, mở ra trong WIPE_OUT khung.
  const WIPE_IN = sec(0.26), WIPE_HOLD = sec(0.05), WIPE_OUT = sec(0.3);
  function buildWipe() {
    const g = mk('g', { display: 'none' }, L.over);
    const slant = 260;
    mk('path', { d: `M ${-slant} 0 L ${W + slant} 0 L ${W} ${H} L ${-2 * slant} ${H} Z`, fill: '#FFF6E0' }, g);
    mk('path', { d: `M ${W + slant} 0 L ${W + slant + 70} 0 L ${W + 70} ${H} L ${W} ${H} Z`, fill: '#F08A24' }, g);
    mk('path', { d: `M ${W + slant + 70} 0 L ${W + slant + 100} 0 L ${W + 100} ${H} L ${W + 70} ${H} Z`, fill: '#2A9D8F' }, g);
    mk('path', { d: `M ${-slant - 100} 0 L ${-slant - 70} 0 L ${-2 * slant - 70} ${H} L ${-2 * slant - 100} ${H} Z`, fill: '#2A9D8F' }, g);
    mk('path', { d: `M ${-slant - 70} 0 L ${-slant} 0 L ${-2 * slant} ${H} L ${-2 * slant - 70} ${H} Z`, fill: '#F08A24' }, g);
    // ba ô cửa sổ toa tàu chạy qua, gợi chuyến "tàu về tuổi thơ"
    for (let k = 0; k < 3; k++) mk('rect', { x: 560 + k * 300, y: 420, width: 200, height: 150, rx: 28, fill: '#BFE6F5', stroke: INK, 'stroke-width': 8 }, g);
    mk('rect', { x: 460, y: 640, width: 1000, height: 22, rx: 11, fill: INK }, g);
    return g;
  }
  function wipeOffset(age) {          // vị trí tấm che theo tuổi (khung)
    const span = W + 400;
    if (age < WIPE_IN) return span * (1 - inOut(age / WIPE_IN));
    if (age < WIPE_IN + WIPE_HOLD) return 0;
    const t = (age - WIPE_IN - WIPE_HOLD) / WIPE_OUT;
    return -span * inOut(clamp(t, 0, 1));
  }
  const covered = () => wipe && F - wipe.f0 >= WIPE_IN - 1 && F - wipe.f0 < WIPE_IN + WIPE_HOLD + 2;

  // ---------- Camera ----------
  function shake(amp) { cam.shakeF = F; cam.shakeA = amp; }
  function camSet(s, fx, fy, dur) {
    const hw = W / 2 / s, hh = H / 2 / s;
    const to = { s, fx: clamp(fx, hw, W - hw), fy: clamp(fy, hh, H - hh) };
    if (covered() || !dur) { Object.assign(cam, to); return; }
    const from = { s: cam.s, fx: cam.fx, fy: cam.fy };
    tween(sec(dur), (t) => {
      const e = s > from.s ? outC(t) : inOut(t);
      cam.s = lerp(from.s, to.s, e); cam.fx = lerp(from.fx, to.fx, e); cam.fy = lerp(from.fy, to.fy, e);
    });
  }

  // ---------- Bảng hành động (đơn vị khung trong kịch bản vẫn là 24 khung/giây) ----------
  const ACT = {
    wipeStart: () => { wipe = { f0: F }; playSfx('whoosh'); },
    bg: (name, mode) => setBg(name, mode),
    show: (id, o) => showActor(actor(id), covered() ? { ...o, mode: 'cut' } : o),
    hide: (id, mode) => hideActor(actor(id), mode),
    move: (id, x, n = 8) => {
      const a = actor(id); const x0 = a.x;
      if (!n || covered()) { a.x = x; return; }
      tween(fr(n * 1.6), (t) => { a.x = lerp(x0, x, inOut(t)); a.dy = -Math.abs(Math.sin(t * Math.PI * 3)) * 9; if (t >= 1) a.dy = 0; });
    },
    flip: (id, v) => { actor(id).flip = v; },
    pose: (id, name) => setPose(actor(id), name),
    jump: (id, name) => jump(actor(id), name),
    eyes: (id, e) => { const a = actor(id); if (a.eyes !== e) { a.eyes = e; if (F - a.blinkF > 10) a.blinkF = F - 1; } },
    mouth: (id, m) => { actor(id).mouthOv = m; },
    talk: (id, v) => { actor(id).fakeTalk = v; },
    speaker: (id) => { speaker = id; },
    fx: (id, name, hold) => fxOn(actor(id), name, hold),
    prop: (id, builder, args, o) => {
      const obj = PROPS[builder](...(args || []));
      if (builder === 'chapters') obj.parts.boxes.forEach((p) => p.setAttribute('display', 'none'));
      if (builder === 'checklist') obj.parts.rows.forEach((p) => p.setAttribute('display', 'none'));
      if (builder === 'ticket') for (let k = 0; k < stamped; k++) obj.parts.stamps[k].setAttribute('display', 'inline');
      addItem(id, obj, covered() ? { ...o, mode: 'cut' } : o);
    },
    text: (id, str, o) => {
      const obj = o.style ? PROPS.tag(str, o.style) : PROPS.bigText(str, { size: o.size || 120, color: o.color });
      addItem(id, obj, o);
    },
    unprop: (id, mode) => removeItem(id, covered() ? 'cut' : mode),
    stamp: (id, n) => {
      const it = items[id]; if (!it) return;
      stamped = Math.max(stamped, n + 1);
      const st = it.obj.parts.stamps[n], inner = it.obj.parts.stampInner ? it.obj.parts.stampInner[n] : wrapPart(st);
      st.setAttribute('display', 'inline');
      const base = inner.getAttribute('data-base') ?? (inner.getAttribute('transform') || '');
      inner.setAttribute('data-base', base);
      const n2 = sec(0.3), hit = Math.round(n2 * 0.4);
      tween(n2, (t) => {
        const sc = t < 0.4 ? lerp(2.6, 0.92, inC(t / 0.4)) : lerp(0.92, 1, outBack((t - 0.4) / 0.6, 2));
        inner.setAttribute('transform', `${base} scale(${f3(sc)})`);
        inner.setAttribute('opacity', f3(clamp(t * 4, 0, 1)));
      });
      later(hit, () => { playSfx('stamp'); shake(11); });
    },
    flipcard: (id, side) => {
      const it = items[id]; if (!it) return;
      playSfx('flip');
      const h = sec(0.17);
      tween(h, (t) => { it.sx = 1 - inC(t); it.ty = -18 * Math.sin(t * Math.PI / 2); if (t >= 1) it.obj.setFace(side); });
      later(h, () => tween(sec(0.24), (t) => { it.sx = outBack(t, 1.6); it.ty = -18 * (1 - outC(t)); }));
    },
    tilt: (id, deg, n) => {
      const it = items[id]; if (!it) return;
      const from = it.tilt || 0; it.tilt = deg;
      tween(fr(n * 1.4), (t) => it.obj.setTilt(lerp(from, deg, outBack(t, 1.4))));
    },
    progress: (id, method, a, b, n) => { const it = items[id]; if (!it) return; tween(fr(n), (t) => it.obj[method](lerp(a, b, inOut(t)))); },
    reveal: (id, partName, idx, mode, delay = 0) => {
      later(fr(delay), () => {
        const it = items[id]; if (!it) return;
        const part = it.obj.parts[partName][idx], inner = wrapPart(part);
        part.setAttribute('display', 'inline'); playSfx('pop');
        tween(sec(0.4), (t) => {
          inner.setAttribute('transform', `translate(${f1(-50 * (1 - outBack(t, 1.3)))} ${f1(-14 * (1 - outC(t)))})`);
          inner.setAttribute('opacity', f3(clamp(t * 2.2, 0, 1)));
        });
      });
    },
    sign: (id, actorId, text) => {
      const obj = PROPS.sign(text);
      later(sec(0.18), () => {
        const it = addItem(id, obj, { mode: 'pop', s: 0.95, attach: { actor: actorId, lx: 60, ly: -270 } });
        it.wave = true;
      });
    },
    drip: (id) => { const it = items[id]; if (it) it.dripF = F; },
    glow: (op, n) => { const p = bgPart('glowLeft'); if (!p) return; const a0 = +(p.getAttribute('opacity') || 0); tween(fr(n * 1.5), (t) => p.setAttribute('opacity', f3(lerp(a0, op, inOut(t))))); },
    dim: (op, n) => { const p = bgPart('dimRight'); if (!p) return; const a0 = +(p.getAttribute('opacity') || 0); tween(fr(n * 1.5), (t) => p.setAttribute('opacity', f3(lerp(a0, op, inOut(t))))); },
    cam: (kind, target, zoom) => {
      if (kind === 'out') camSet(1, W / 2, H / 2, 0.42);
      else if (kind === 'in') { const a = actor(target); const [hx, hy] = headWorld(a); camSet(zoom || 1.75, hx, hy + 40, 0.3); }
      else if (kind === 'row') {
        const it = items[target]; if (!it) return;
        // phóng vừa đủ để cả tấm vé nằm trên dải phụ đề
        camSet(1.5, it.x, it.y + 20, 0.4);
      }
    },
    shake: (amp) => shake(amp),
    endcard: () => {
      setBg('end', 'fade');
      const a = actor('mot'); const x0 = a.x;
      tween(sec(0.8), (t) => { a.x = lerp(x0, 450, inOut(t)); });
      for (const id in items) removeItem(id);
      subEl.style.opacity = '0';
    },
  };

  // ---------- Biên dịch kịch bản thành sự kiện theo khung ----------
  const norm = (w) => w.toLowerCase().replace(/[.,:;!?…"“”()]/g, '');
  function wordIndex(text, token) {
    const [tok, nth] = token.slice(1).split('#');
    const words = text.split(/\s+/), want = +(nth || 1);
    let c = 0;
    for (let i = 0; i < words.length; i++) if (words[i].toLowerCase() === tok.toLowerCase() && ++c === want) return i;
    c = 0;
    for (let i = 0; i < words.length; i++) if (norm(words[i]) === norm(tok) && ++c === want) return i;
    console.warn('Không tìm thấy từ', token, 'trong:', text);
    return 0;
  }
  function compile(script, timing) {
    const byI = {};
    timing.lines.forEach((l) => {
      byI[l.i] = { start: Math.round(l.start * R24), frames: Math.round(l.frames * R24), wordStarts: l.wordStarts.map((w) => Math.round(w * R24)) };
    });
    amp24 = new Float32Array(timing.totalFrames + 2);
    for (const l of timing.lines) for (let k = 0; k < l.frames; k++) amp24[l.start + k] = l.amp[k] || 0;
    const ev = [];
    script.forEach((s) => {
      const l = byI[s.i];
      (s.a || []).forEach(([trig, name, ...args]) => {
        let f = l.start;
        if (trig === 'e') f = l.start + l.frames;
        else if (typeof trig === 'number') f = l.start + (l.wordStarts[trig] || 0);
        else if (typeof trig === 'string' && trig[0] === '@') f = l.start + (l.wordStarts[wordIndex(s.t, trig)] || 0);
        ev.push({ f, k: ev.length, name, args });
      });
      if (s.t) buildSubs(s, l);
    });
    ev.sort((a, b) => a.f - b.f || a.k - b.k);
    // Mỗi lần đổi nền (trừ nền đầu tiên và kiểu 'fade'), chèn tấm che bắt đầu trước đó WIPE_IN khung
    // để lúc đổi cảnh màn hình đã được che kín.
    let cur = null;
    const extra = [];
    for (const e of ev) {
      if (e.name !== 'bg') continue;
      const [name, mode] = e.args;
      if (cur && name !== cur && mode !== 'fade') extra.push({ f: Math.max(0, e.f - WIPE_IN), k: -1, name: 'wipeStart', args: [] });
      cur = name;
    }
    return ev.concat(extra).sort((a, b) => a.f - b.f || a.k - b.k);
  }
  function buildSubs(s, l) {
    const words = s.t.split(/\s+/);
    const chunks = []; let cur = [];
    words.forEach((w, i) => {
      cur.push(i);
      const txt = cur.map((j) => words[j]).join(' ');
      const strong = /[.?!:…]$/.test(w), weak = /[,;]$/.test(w);
      if ((strong && txt.length > 18) || (weak && txt.length > 38) || txt.length > 58) { chunks.push(cur); cur = []; }
    });
    if (cur.length) chunks.push(cur);
    chunks.forEach((c, k) => {
      const start = l.start + (l.wordStarts[c[0]] || 0);
      const end = k + 1 < chunks.length ? l.start + (l.wordStarts[chunks[k + 1][0]] || l.frames) : l.start + l.frames + sec(0.25);
      subChunks.push({ start, end, text: c.map((j) => words[j]).join(' ') });
    });
  }

  // ---------- Vòng chạy ----------
  function step() {
    F++;
    while (evPtr < events.length && events[evPtr].f <= F) {
      const e = events[evPtr++];
      if (!ACT[e.name]) console.warn('Hành động lạ', e.name); else ACT[e.name](...e.args);
    }
    laters.sort((a, b) => a.f - b.f);
    while (laters.length && laters[0].f <= F) laters.shift().fn();
    tweens = tweens.filter((tw) => {
      if (F < tw.f0) return true;
      const t = Math.min(1, (F - tw.f0 + 1) / tw.n);
      tw.fn(t);
      return t < 1;
    });
    const raw = ampAt(F);
    ampS += (raw - ampS) * (raw > ampS ? 0.6 : 0.25);
    for (const id in actors) stepActor(actors[id]);
  }
  function draw() {
    for (const id in actors) drawActor(actors[id]);
    for (const id in items) {
      const it = items[id];
      if (it.wave) it.rot = Math.sin(((F - it.f0) / FPS) * Math.PI * 2 * 1.4) * 5;   // biển phản đối lắc lư
      placeItem(it);
    }
    for (const n in bgs) bgs[n].el.setAttribute('opacity', f3(bgs[n].alpha));
    let sx = 0, sy = 0;
    if (cam.shakeF >= 0) {
      const t = (F - cam.shakeF) / FPS;
      if (t < 0.5) { const d = cam.shakeA * Math.exp(-t * 9); sx = d * Math.sin(t * 2 * Math.PI * 11); sy = d * 0.5 * Math.cos(t * 2 * Math.PI * 13); }
    }
    L.cam.setAttribute('transform', `translate(${f1(W / 2 + sx)} ${f1(H / 2 + sy)}) scale(${f3(cam.s)}) translate(${f1(-cam.fx)} ${f1(-cam.fy)})`);
    if (wipe) {
      const age = F - wipe.f0;
      if (age > WIPE_IN + WIPE_HOLD + WIPE_OUT) { wipe = null; L.wipe.setAttribute('display', 'none'); }
      else { L.wipe.setAttribute('display', 'inline'); L.wipe.setAttribute('transform', `translate(${f1(wipeOffset(age))} 0)`); }
    }
    const sub = subChunks.find((c) => F >= c.start && F < c.end);
    const txt = sub ? sub.text : '';
    if (subEl.textContent !== txt) subEl.textContent = txt;
    subEl.style.visibility = txt ? 'visible' : 'hidden';
  }

  window.ENGINE = {
    FPS,
    init(timing) {
      const svg = document.getElementById('stage');
      L.cam = mk('g', {}, svg);
      L.bg = mk('g', {}, L.cam); L.props = mk('g', {}, L.cam); L.actors = mk('g', {}, L.cam); L.fx = mk('g', {}, L.cam);
      L.over = mk('g', {}, svg);
      L.wipe = buildWipe();
      subEl = document.getElementById('sub');
      events = compile(window.SCRIPT, timing);
      this.totalFrames = Math.ceil(timing.totalFrames * R24);
    },
    simTo(n) { while (F < n) step(); draw(); return F; },
    frame() { return F; },
    sfxEvents() { return sfx.slice(); },
  };
})();
