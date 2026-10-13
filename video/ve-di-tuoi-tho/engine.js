// Engine dựng hình theo từng khung cho video người que.
// Tất cả trạng thái là hàm tất định của số khung: chạy lại từ 0 luôn ra cùng một kết quả,
// nên nhiều tiến trình có thể render song song các đoạn khác nhau.
(function () {
  'use strict';
  const FPS = 24, W = 1920, H = 1080, GROUND = 930;
  const NS = 'http://www.w3.org/2000/svg';
  const INK = '#1D1D1F', SKIN = '#FBE3D6', RED = '#D1495B';
  const mk = (tag, attrs = {}, parent) => {
    const e = document.createElementNS(NS, tag);
    for (const k in attrs) e.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(e);
    return e;
  };
  const lerp = (a, b, t) => a + (b - a) * t;
  const ease = (t) => (t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2);
  const easeOut = (t) => 1 - Math.pow(1 - t, 3);
  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
  function rng(seed) { let s = seed >>> 0; return () => { s = (Math.imul(s, 1664525) + 1013904223) >>> 0; return s / 4294967296; }; }

  // ---------- Tư thế (giống demo) ----------
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
    'cam-sach':      { L: { e: [-8, -150], h: [22, -176], s: 'nam' }, R: { e: [50, -146], h: [92, -176], s: 'nam' } },
  };
  const clonePose = (p) => JSON.parse(JSON.stringify(p));

  // ---------- Nhân vật ----------
  const HAIR = {
    spiky: 'M -66 -276 L -72 -316 L -52 -308 L -48 -346 L -26 -326 L -12 -360 L 6 -332 L 28 -356 L 34 -326 L 60 -340 L 56 -308 L 72 -296 L 66 -270 Q 50 -300 0 -298 Q -40 -300 -66 -276 Z',
    tuft: 'M -66 -278 Q -68 -332 -16 -340 Q 34 -346 66 -310 L 68 -282 Q 30 -302 -66 -278 Z M -14 -338 L -24 -374 L 0 -346 L 8 -380 L 20 -342 Z',
    neat: 'M -66 -280 Q -66 -338 0 -340 Q 66 -340 68 -288 Q 24 -314 -16 -302 Q -42 -296 -66 -280 Z',
    short: 'M -64 -288 Q -62 -336 0 -338 Q 64 -336 66 -290 Q 0 -312 -64 -288 Z',
    bob: 'M -72 -228 Q -80 -344 0 -346 Q 80 -344 74 -228 L 60 -228 Q 62 -298 30 -300 Q 0 -296 -40 -306 Q -58 -298 -58 -228 Z',
    topknot: 'M -64 -284 Q -60 -336 0 -338 Q 62 -336 66 -286 Q 0 -308 -64 -284 Z M -20 -352 a 22 22 0 1 0 40 0 a 22 22 0 1 0 -40 0 Z',
  };
  const CHARS = {
    mot:    { k: 1.8, hair: 'spiky', hairC: '#263859', shirt: '#2A9D8F', neck: 'bookmark' },
    mot2:   { k: 1.8, hair: 'spiky', hairC: '#263859', shirt: '#2A9D8F', neck: 'bookmark' },
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
    switch (kind) {
      case 'he': return `<ellipse cx="${x}" cy="${y}" rx="9" ry="5" fill="${RED}" ${st}/>`;
      case 'mo': return `<ellipse cx="${x}" cy="${y + 2}" rx="11" ry="11" fill="${RED}" ${st}/>`;
      case 'cuoi': return `<path d="M ${x - 14} ${y - 5} Q ${x} ${y + 16} ${x + 14} ${y - 5} Z" fill="${RED}" ${st}/>`;
      case 'sun': return `<path d="M ${x - 16} ${y - 6} Q ${x} ${y + 18} ${x + 16} ${y - 6} Z" fill="${RED}" ${st}/><rect x="${x - 12}" y="${y - 5}" width="24" height="7" fill="#FFFFFF"/><rect x="${x - 2}" y="${y - 5}" width="6" height="7" fill="${INK}"/>`;
      case 'mim': return `<path d="M ${x - 11} ${y} Q ${x} ${y + 7} ${x + 12} ${y - 5}" fill="none" ${st}/>`;
      case 'o': return `<circle cx="${x}" cy="${y + 2}" r="8" fill="${RED}" ${st}/>`;
      case 'meo': return `<path d="M ${x - 12} ${y + 4} Q ${x - 4} ${y - 7} ${x + 2} ${y + 2} Q ${x + 8} ${y + 7} ${x + 13} ${y - 2}" fill="none" ${st}/>`;
      default: return `<path d="M ${x - 8} ${y} L ${x + 8} ${y}" fill="none" ${st}/>`;
    }
  }
  function handSVG(shape) {
    const f = `fill="${SKIN}" stroke="${INK}" stroke-width="4"`;
    const finger = (rot) => `<rect x="4" y="-4" width="22" height="8" rx="4" ${f} transform="rotate(${rot})"/>`;
    switch (shape) {
      case 'chi': return finger(0) + `<circle r="10" ${f}/>`;
      case 'v': return finger(-22) + finger(22) + `<circle r="10" ${f}/>`;
      case 'xoe': return `<rect x="2" y="-4" width="14" height="8" rx="4" ${f} transform="rotate(-75)"/><circle r="12" ${f}/>`;
      case 'ok': return finger(-40) + `<circle r="11" ${f}/><circle cx="2" cy="1" r="4" fill="#FFFFFF" stroke="${INK}" stroke-width="3"/>`;
      default: return `<circle r="11" ${f}/>`;
    }
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
  let events = [];       // [{f, fn}] đã sắp xếp
  let evPtr = 0;
  let ampAll = null;     // biên độ giọng theo khung
  let speaker = 'mot';
  let lastTalkShape = 'ngam', lastTalkF = -10;
  const cam = { s: 1, fx: W / 2, fy: H / 2, shake: [] };
  const actors = {}, items = {}, bgs = {};
  let curBg = null;
  let subChunks = [], subEl = null;
  let L = {};            // các lớp svg
  const tween = (n, fn, delay = 0) => tweens.push({ f0: F + delay, n: Math.max(1, n), fn });
  const later = (delay, fn) => laters.push({ f: F + delay, fn });
  const playSfx = (type, delay = 0) => sfx.push({ frame: F + delay, type });

  // ---------- Tạo nhân vật ----------
  function makeActor(id) {
    const d = CHARS[id];
    const legL = d.legs || 1, u = -(102 * legL - 102);
    const g = mk('g', { display: 'none' }, L.actors);
    const legs = mk('g', { stroke: INK, 'stroke-width': 7, 'stroke-linecap': 'round', fill: 'none' }, g);
    const hip = -16 - 102 * legL;
    mk('path', { d: `M -9 ${hip} L -15 -16 M 9 ${hip} L 15 -16` }, legs);
    mk('ellipse', { cx: -20, cy: -9, rx: 16, ry: 9, fill: '#FFFFFF', 'stroke-width': 5 }, legs);
    mk('ellipse', { cx: 21, cy: -9, rx: 16, ry: 9, fill: '#FFFFFF', 'stroke-width': 5 }, legs);
    const up0 = mk('g', { transform: `translate(0 ${u})` }, g);
    const upper = mk('g', {}, up0);
    mk('path', { d: 'M -27 -190 L 27 -190 L 33 -112 Q 0 -106 -33 -112 Z', fill: d.shirt, stroke: INK, 'stroke-width': 6, 'stroke-linejoin': 'round' }, upper);
    let tie = null;
    if (d.neck === 'bookmark') {
      tie = mk('g', {}, upper);
      mk('path', { d: 'M -7 0 L 7 0 L 7 50 L 0 41 L -7 50 Z', fill: '#F08A24', stroke: INK, 'stroke-width': 4, 'stroke-linejoin': 'round' }, tie);
    } else if (d.neck === 'tie') {
      tie = mk('g', {}, upper);
      mk('path', { d: 'M -7 0 L 7 0 L 10 56 L 0 68 L -10 56 Z', fill: '#2E3A59', stroke: INK, 'stroke-width': 4, 'stroke-linejoin': 'round' }, tie);
    } else if (d.neck === 'scarf') {
      mk('path', { d: 'M -28 -192 L 28 -192 L 6 -150 L 0 -138 L -6 -150 Z', fill: '#D62828', stroke: INK, 'stroke-width': 4, 'stroke-linejoin': 'round' }, upper);
    }
    const book = mk('g', { display: 'none' }, upper);
    book.innerHTML = `<path d="M 56 -150 L 18 -170 L 18 -226 L 56 -206 Z" fill="#FFFFFF" stroke="${INK}" stroke-width="5" stroke-linejoin="round"/><path d="M 56 -150 L 94 -170 L 94 -226 L 56 -206 Z" fill="#F4F6F8" stroke="${INK}" stroke-width="5" stroke-linejoin="round"/><path d="M 28 -196 L 48 -186 M 28 -184 L 48 -174 M 66 -186 L 86 -196 M 66 -174 L 86 -184" stroke="#9AA6B5" stroke-width="3"/>`;
    const head = mk('g', {}, upper);
    mk('rect', { x: -60, y: -332, width: 124, height: 140, rx: 26, fill: SKIN, stroke: INK, 'stroke-width': 6 }, head);
    mk('path', { d: HAIR[d.hair], fill: d.hairC, stroke: INK, 'stroke-width': 6, 'stroke-linejoin': 'round' }, head);
    if (d.bags) mk('path', { d: 'M -2 -244 Q 6 -238 14 -244 M 28 -244 Q 36 -238 44 -244', stroke: '#9A8FA6', 'stroke-width': 4, fill: 'none', 'stroke-linecap': 'round' }, head);
    const eyes = mk('g', {}, head), mouth = mk('g', {}, head);
    const arms = mk('g', { stroke: INK, 'stroke-width': 7, 'stroke-linecap': 'round', 'stroke-linejoin': 'round', fill: 'none' }, upper);
    const armL = mk('polyline', {}, arms), armR = mk('polyline', {}, arms);
    const handL = mk('g', {}, upper), handR = mk('g', {}, upper);
    const fxg = mk('g', {}, L.fx);
    const r = rng(id.split('').reduce((a, c) => a * 31 + c.charCodeAt(0), 7));
    const a = {
      id, d, u, g, upper, tie, book, eyesG: eyes, mouthG: mouth, armL, armR, handL, handR, fxg, r,
      vis: false, x: 0, y: GROUND, flip: false, k: d.k, pop: 1, dy: 0, slideX: 0,
      arms: clonePose(POSES.dung), pose: 'dung', eyes: 'thuong', mouthRest: 'ngam', mouthOv: null, fakeTalk: false,
      blink: 0, nextBlink: 20 + Math.floor(r() * 60), tieA: 0, tieV: 0, kicks: [], fx: [],
      phase: r() * Math.PI * 2, last: { eyes: '', mouth: '', hL: '', hR: '' },
    };
    actors[id] = a;
    return a;
  }
  const actor = (id) => actors[id] || makeActor(id);
  function headWorld(a) {
    const sx = a.flip ? -1 : 1;
    return [a.x + a.slideX + sx * 20 * a.k, a.y + a.dy + (-262 + a.u) * a.k];
  }
  function drawActor(a) {
    a.g.setAttribute('display', a.vis ? 'inline' : 'none');
    a.fxg.setAttribute('display', a.vis ? 'inline' : 'none');
    if (!a.vis) return;
    const sx = a.flip ? -1 : 1, s = a.k * a.pop;
    a.g.setAttribute('transform', `translate(${(a.x + a.slideX).toFixed(1)} ${(a.y + a.dy).toFixed(1)}) scale(${(s * sx).toFixed(4)} ${s.toFixed(4)})`);
    const breath = Math.round(Math.sin(F / 48 * Math.PI * 2 + a.phase) * 2);
    a.upper.setAttribute('transform', `translate(0 ${breath})`);
    if (a.tie) a.tie.setAttribute('transform', `translate(4 -188) rotate(${a.tieA.toFixed(2)})`);
    const ek = a.blink > 0 && !['x', 'nham'].includes(a.eyes) ? 'blink' : a.eyes;
    if (ek !== a.last.eyes) { a.eyesG.innerHTML = eyeSVG(ek, E1) + eyeSVG(ek, E2); a.last.eyes = ek; }
    const mkey = mouthFor(a);
    if (mkey !== a.last.mouth) { a.mouthG.innerHTML = mouthSVG(mkey, MO); a.last.mouth = mkey; }
    for (const side of ['L', 'R']) {
      const p = a.arms[side], sh = SH[side];
      a['arm' + side].setAttribute('points', `${sh[0]},${sh[1]} ${p.e[0].toFixed(1)},${p.e[1].toFixed(1)} ${p.h[0].toFixed(1)},${p.h[1].toFixed(1)}`);
      const ang = Math.atan2(p.h[1] - p.e[1], p.h[0] - p.e[0]) * 180 / Math.PI;
      const hg = a['hand' + side];
      hg.setAttribute('transform', `translate(${p.h[0].toFixed(1)} ${p.h[1].toFixed(1)}) rotate(${ang.toFixed(1)})`);
      if (a.last['h' + side] !== p.s) { hg.innerHTML = handSVG(p.s); a.last['h' + side] = p.s; }
    }
    // hiệu ứng: đặt cạnh đầu, không lật theo nhân vật
    const [hx, hy] = headWorld(a);
    a.fxg.setAttribute('transform', `translate(${(hx + (a.flip ? -150 * a.k : 0)).toFixed(1)} ${hy.toFixed(1)}) scale(${a.k}) translate(-20 262)`);
  }
  function mouthFor(a) {
    if (a.mouthOv) return a.mouthOv;
    let talking = false, amp = 0;
    if (a.fakeTalk) { talking = true; amp = [0.5, 0.2, 0.8, 0.1, 0.6, 0.3][Math.floor(F / 3) % 6]; }
    else if (a.id === speaker && ampAll) { amp = ampAll[F] || 0; talking = amp > 0.07; }
    if (!talking) return a.mouthRest;
    if (F - lastTalkF < 2 && a.id === speaker) return lastTalkShape;
    const shape = amp < 0.3 ? 'he' : 'mo';
    if (a.id === speaker) { lastTalkShape = shape; lastTalkF = F; }
    return shape;
  }
  function stepActor(a) {
    if (a.blink > 0) a.blink--;
    else if (F >= a.nextBlink) { a.blink = 2; a.nextBlink = F + 48 + Math.floor(a.r() * 72); }
    a.kicks = a.kicks.filter((kk) => { if (kk.f <= F) { a.tieV += kk.v; return false; } return true; });
    a.tieV += -0.32 * a.tieA - 0.22 * a.tieV; a.tieA += a.tieV;
    if (Math.abs(a.tieA) < 0.05 && Math.abs(a.tieV) < 0.05) { a.tieA = 0; a.tieV = 0; }
    a.fx = a.fx.filter((fx) => {
      const age = F - fx.f0;
      const POP = [0.45, 0.85, 1.1, 1.06, 1.0];
      const sc = age < POP.length ? POP[age] : (age > fx.hold + 5 ? Math.max(0, 1 - (age - fx.hold - 5) / 3) : 1);
      fx.el.setAttribute('transform', `translate(90 -340) scale(${sc}) translate(-90 340)`);
      if (age > fx.hold + 8) { fx.el.remove(); return false; }
      return true;
    });
  }

  // ---------- Hành động nhân vật ----------
  function setPose(a, name, n = 2) {
    const to = POSES[name], from = clonePose(a.arms);
    a.book.setAttribute('display', name === 'cam-sach' ? 'inline' : 'none');
    a.pose = name;
    tween(n, (t) => {
      for (const side of ['L', 'R']) {
        const p = a.arms[side], f = from[side], b = to[side];
        p.e = [lerp(f.e[0], b.e[0], t), lerp(f.e[1], b.e[1], t)];
        p.h = [lerp(f.h[0], b.h[0], t), lerp(f.h[1], b.h[1], t)];
        p.s = t >= 0.5 ? b.s : f.s;
      }
    });
    a.kicks.push({ f: F + 2, v: 7 });
  }
  function jump(a, name) {
    const keys = [4, 8, 10, -8, -4, 0];
    tween(keys.length, (t) => { a.dy = keys[Math.min(keys.length - 1, Math.round(t * keys.length) - 1)]; });
    later(3, () => setPose(a, name));
    a.kicks.push({ f: F + 5, v: 9 });
  }
  const POPK = [0, 0.45, 0.85, 1.1, 1.06, 1.0];
  function showActor(a, o) {
    const run = () => {
      a.vis = true; a.x = o.x; if (o.flip !== undefined) a.flip = o.flip; a.dy = 0; a.slideX = 0;
      const mode = o.mode || 'pop';
      if (mode === 'pop') { tween(POPK.length, (t) => { a.pop = POPK[Math.min(POPK.length - 1, Math.round(t * POPK.length) - 1)]; }); a.pop = 0; playSfx('pop'); }
      else if (mode === 'slideR' || mode === 'slideL') {
        const from = mode === 'slideR' ? (W + 300 - o.x) : (-300 - o.x);
        a.slideX = from; a.pop = 1; playSfx('whoosh');
        tween(9, (t) => { a.slideX = from * (1 - easeOut(t)); });
      } else a.pop = 1;
    };
    if (o.delay) later(o.delay, run); else run();
  }
  function hideActor(a, mode = 'pop') {
    if (!a.vis) return;
    if (mode === 'cut') { a.vis = false; a.fx.forEach((fx) => fx.el.remove()); a.fx = []; return; }
    const keys = [1.06, 0.6, 0];
    tween(3, (t) => { a.pop = keys[Math.min(2, Math.round(t * 3) - 1)]; if (t >= 1) a.vis = false; });
  }
  function fxOn(a, name, hold = 36) {
    const el = mk('g', {}, a.fxg);
    el.innerHTML = FX_SVG[name];
    a.fx.push({ el, f0: F, hold });
    if (FX_SFX[name]) playSfx(FX_SFX[name]);
  }

  // ---------- Đồ vật ----------
  function placeItem(it) {
    const t = it.attach ? attachPos(it.attach) : [it.x, it.y];
    const s = it.s * it.pop;
    it.el.setAttribute('transform', `translate(${t[0].toFixed(1)} ${(t[1] + it.ty).toFixed(1)}) scale(${(s * it.sx).toFixed(4)} ${s.toFixed(4)})`);
    it.el.setAttribute('opacity', it.alpha.toFixed(3));
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
    const it = { id, obj, el, x: o.x ?? W / 2, y: o.y ?? H / 2, s: o.s ?? 1, sx: 1, pop: 1, ty: 0, alpha: 1, vis: true, attach: o.attach };
    items[id] = it;
    enter(it, o.mode || 'pop');
    return it;
  }
  function enter(it, mode) {
    if (mode === 'pop') { it.pop = 0; tween(POPK.length, (t) => { it.pop = POPK[Math.min(POPK.length - 1, Math.round(t * POPK.length) - 1)]; }); playSfx('pop'); }
    else if (mode === 'dap') {
      const keys = [-460, -300, -130, 0, -26, 0];
      it.ty = keys[0];
      tween(keys.length, (t) => { it.ty = keys[Math.min(keys.length - 1, Math.round(t * keys.length) - 1)]; });
      later(3, () => { shake(9); playSfx('thud'); });
    } else if (mode === 'fade') { it.alpha = 0; tween(10, (t) => { it.alpha = t; }); }
  }
  function removeItem(id, mode = 'pop') {
    const it = items[id]; if (!it) return;
    delete items[id];
    if (mode === 'cut') { it.el.remove(); return; }
    const keys = [1.06, 0.6, 0];
    tween(3, (t) => { it.pop = keys[Math.min(2, Math.round(t * 3) - 1)]; placeItem(it); if (t >= 1) it.el.remove(); });
  }
  function wrapPart(part) {
    if (part.__inner) return part.__inner;
    const inner = mk('g', {});
    while (part.firstChild) inner.appendChild(part.firstChild);
    part.appendChild(inner); part.__inner = inner;
    return inner;
  }

  // ---------- Nền ----------
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
    bgs[name] = { name, obj, el: wrap, x: 0, alpha: 1 };
    return bgs[name];
  }
  function setBg(name, mode = 'cut') {
    const nb = getBg(name), old = curBg;
    if (old === nb) return;
    L.bg.appendChild(nb.el);               // lên trên cùng của lớp nền
    nb.el.setAttribute('display', 'inline');
    curBg = nb;
    const drop = () => { if (old && old !== curBg) old.el.setAttribute('display', 'none'); };
    if (mode === 'slide') {
      nb.x = W; playSfx('whoosh');
      tween(10, (t) => { nb.x = W * (1 - easeOut(t)); if (t >= 1) drop(); });
    } else if (mode === 'fade') {
      nb.alpha = 0; tween(12, (t) => { nb.alpha = t; if (t >= 1) drop(); });
    } else { nb.x = 0; nb.alpha = 1; drop(); }
  }
  function bgPart(name) { return curBg && curBg.obj.parts ? curBg.obj.parts[name] : null; }

  // ---------- Camera ----------
  function shake(amp) { cam.shake = [1, -0.8, 0.6, -0.4, 0.2, 0].map((f) => [amp * f, amp * f * 0.4]); }
  function camSet(s, fx, fy) {
    const hw = W / 2 / s, hh = H / 2 / s;
    cam.s = s; cam.fx = clamp(fx, hw, W - hw); cam.fy = clamp(fy, hh, H - hh);
  }

  // ---------- Bảng hành động ----------
  const ACT = {
    bg: (name, mode) => setBg(name, mode),
    show: (id, o) => showActor(actor(id), o),
    hide: (id, mode) => hideActor(actor(id), mode),
    move: (id, x, n = 8) => { const a = actor(id); const x0 = a.x; if (!n) a.x = x; else tween(n, (t) => { a.x = lerp(x0, x, ease(t)); }); },
    flip: (id, v) => { actor(id).flip = v; },
    pose: (id, name) => setPose(actor(id), name),
    jump: (id, name) => jump(actor(id), name),
    eyes: (id, e) => { actor(id).eyes = e; },
    mouth: (id, m) => { actor(id).mouthOv = m; },
    talk: (id, v) => { actor(id).fakeTalk = v; },
    speaker: (id) => { speaker = id; },
    fx: (id, name, hold) => fxOn(actor(id), name, hold),
    prop: (id, builder, args, o) => {
      const obj = PROPS[builder](...(args || []));
      if (builder === 'chapters') obj.parts.boxes.forEach((p) => p.setAttribute('display', 'none'));
      if (builder === 'checklist') obj.parts.rows.forEach((p) => p.setAttribute('display', 'none'));
      addItem(id, obj, o);
    },
    text: (id, str, o) => {
      const obj = o.style ? PROPS.tag(str, o.style) : PROPS.bigText(str, { size: o.size || 120, color: o.color });
      addItem(id, obj, o);
    },
    unprop: (id, mode) => removeItem(id, mode),
    stamp: (id, n) => {
      const it = items[id]; if (!it) return;
      const st = it.obj.parts.stamps[n], inner = it.obj.parts.stampInner ? it.obj.parts.stampInner[n] : wrapPart(st);
      st.setAttribute('display', 'inline');
      const keys = [2.4, 1.5, 0.9, 1.05, 1];
      tween(keys.length, (t) => { inner.setAttribute('transform', `scale(${keys[Math.min(keys.length - 1, Math.round(t * keys.length) - 1)]})`); });
      later(2, () => { playSfx('stamp'); shake(10); });
    },
    flipcard: (id, side) => {
      const it = items[id]; if (!it) return;
      playSfx('flip');
      tween(4, (t) => { it.sx = 1 - t; if (t >= 1) it.obj.setFace(side); });
      later(4, () => tween(4, (t) => { it.sx = t; }));
    },
    tilt: (id, deg, n) => {
      const it = items[id]; if (!it) return;
      const from = it.tilt || 0; it.tilt = deg;
      tween(n, (t) => it.obj.setTilt(lerp(from, deg, ease(t))));
    },
    progress: (id, method, a, b, n) => { const it = items[id]; if (!it) return; tween(n, (t) => it.obj[method](lerp(a, b, t))); },
    reveal: (id, partName, idx, mode, delay = 0) => {
      later(delay, () => {
        const it = items[id]; if (!it) return;
        const part = it.obj.parts[partName][idx], inner = wrapPart(part);
        part.setAttribute('display', 'inline'); playSfx('pop');
        tween(6, (t) => { inner.setAttribute('transform', `translate(${(-40 * (1 - easeOut(t))).toFixed(1)} 0)`); inner.setAttribute('opacity', t.toFixed(3)); });
      });
    },
    sign: (id, actorId, text) => {
      const obj = PROPS.sign(text);
      later(3, () => addItem(id, obj, { mode: 'pop', s: 0.95, attach: { actor: actorId, lx: 60, ly: -270 } }));
    },
    drip: (id) => { const it = items[id]; if (it) it.dripF = F; },
    glow: (op, n) => { const p = bgPart('glowLeft'); if (!p) return; const a0 = +(p.getAttribute('opacity') || 0); tween(n, (t) => p.setAttribute('opacity', lerp(a0, op, t))); },
    dim: (op, n) => { const p = bgPart('dimRight'); if (!p) return; const a0 = +(p.getAttribute('opacity') || 0); tween(n, (t) => p.setAttribute('opacity', lerp(a0, op, t))); },
    cam: (kind, target, zoom) => {
      if (kind === 'out') camSet(1, W / 2, H / 2);
      else if (kind === 'in') { const a = actor(target); const [hx, hy] = headWorld(a); camSet(zoom || 1.75, hx, hy + 40); }
      else if (kind === 'row') {
        const it = items[target]; if (!it) return;
        const p = it.obj.parts; const lx = (p.rowX || -200) + 160, ly = p.rowY[zoom || 0];
        camSet(1.9, it.x + it.s * lx, it.y + it.s * ly);
      }
    },
    shake: (amp) => shake(amp),
    endcard: () => {
      setBg('end', 'fade');
      const a = actor('mot'); tween(12, (t) => { a.x = lerp(560, 450, ease(t)); });
      for (const id in items) removeItem(id, 'cut');
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
    const byI = {}; timing.lines.forEach((l) => { byI[l.i] = l; });
    const ev = [];
    ampAll = new Float32Array(timing.totalFrames + 2);
    for (const l of timing.lines) for (let k = 0; k < l.frames; k++) ampAll[l.start + k] = l.amp[k] || 0;
    script.forEach((s) => {
      const l = byI[s.i];
      (s.a || []).forEach(([trig, name, ...args], order) => {
        let f = l.start;
        if (trig === 'e') f = l.start + l.frames;
        else if (typeof trig === 'number') f = l.start + (l.wordStarts[trig] || 0);
        else if (typeof trig === 'string' && trig[0] === '@') f = l.start + (l.wordStarts[wordIndex(s.t, trig)] || 0);
        ev.push({ f, k: ev.length, name, args });
      });
      if (s.t) buildSubs(s, l);
    });
    ev.sort((a, b) => a.f - b.f || a.k - b.k);
    return ev;
  }
  function buildSubs(s, l) {
    const words = s.t.split(/\s+/);
    // chia câu dài thành các mảnh ≤ 58 ký tự, ưu tiên cắt sau dấu câu
    const chunks = []; let cur = [];
    const len = (arr) => arr.join(' ').length;
    words.forEach((w, i) => {
      cur.push(i);
      const txt = cur.map((j) => words[j]).join(' ');
      const strong = /[.?!:…]$/.test(w), weak = /[,;]$/.test(w);
      if ((strong && txt.length > 18) || (weak && txt.length > 38) || txt.length > 58) { chunks.push(cur); cur = []; }
    });
    if (cur.length) chunks.push(cur);
    chunks.forEach((c, k) => {
      const start = l.start + (l.wordStarts[c[0]] || 0);
      const end = k + 1 < chunks.length ? l.start + (l.wordStarts[chunks[k + 1][0]] || l.frames) : l.start + l.frames + 6;
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
    for (const id in actors) stepActor(actors[id]);
  }
  function draw() {
    for (const id in actors) drawActor(actors[id]);
    for (const id in items) placeItem(items[id]);
    for (const n in bgs) { const b = bgs[n]; b.el.setAttribute('transform', `translate(${b.x.toFixed(1)} 0)`); b.el.setAttribute('opacity', b.alpha); }
    const sh = cam.shake.length ? cam.shake.shift() : [0, 0];
    L.cam.setAttribute('transform', `translate(${W / 2 + sh[0]} ${H / 2 + sh[1]}) scale(${cam.s}) translate(${-cam.fx} ${-cam.fy})`);
    const sub = subChunks.find((c) => F >= c.start && F < c.end);
    const txt = sub ? sub.text : '';
    if (subEl.textContent !== txt) subEl.textContent = txt;
    subEl.style.visibility = txt ? 'visible' : 'hidden';
  }

  window.ENGINE = {
    init(timing) {
      const svg = document.getElementById('stage');
      L.cam = mk('g', {}, svg);
      L.bg = mk('g', {}, L.cam); L.props = mk('g', {}, L.cam); L.actors = mk('g', {}, L.cam); L.fx = mk('g', {}, L.cam);
      subEl = document.getElementById('sub');
      events = compile(window.SCRIPT, timing);
      this.totalFrames = timing.totalFrames;
    },
    simTo(n) { while (F < n) step(); draw(); return F; },
    frame() { return F; },
    sfxEvents() { return sfx.slice(); },
  };
})();
