/* props.js — prop & background SVG builders for "Cho tôi xin một vé đi tuổi thơ".
 * Plain script: defines window.PROPS. Every builder returns { el, parts, ...methods }.
 * `el` is a fresh, unattached <g>; content is wrapped inside so the engine may set el's transform.
 * Builders are pure/deterministic (no timers, no randomness). Methods only update attributes.
 */
(function () {
  'use strict';
  const NS = 'http://www.w3.org/2000/svg';
  const C = {
    ink: '#1D1D1F', white: '#FFFFFF', paper: '#FFF6E0', paper2: '#F7E3BC',
    sun: '#F6C343', orange: '#F08A24', leaf: '#6BAF5B', leafDark: '#4F9442', leafLight: '#A8D48F',
    sky: '#BFE6F5', red: '#D62828', teal: '#2A9D8F', pink: '#F48FB1', pinkLight: '#F9C5D5',
    wood: '#C98B55', woodDark: '#8B5A3C', roof: '#C8553D', roofDark: '#9E3F2C', lane: '#EBD3AA', curb: '#D8B583',
    cardboard: '#E9C89B', greyBlue: '#6C7A89', greyBlue2: '#9AA9B8', slate: '#3E4C5E', pale: '#DCE3EA',
    paleBlue: '#C9D3DD', grey: '#6B7280', bar: '#C5CCD6', highlight: '#FFE14D',
    warmSkyTop: '#FFD49A', warmSkyLow: '#FFF0D2',
  };
  const INK = C.ink, SW = 6;
  const FD = "'Baloo 2', 'DejaVu Sans', sans-serif";
  const FB = "'Be Vietnam Pro', 'DejaVu Sans', sans-serif";

  // ---------- low-level helpers ----------
  function mk(tag, attrs, parent) {
    const e = document.createElementNS(NS, tag);
    if (attrs) for (const k in attrs) if (attrs[k] != null) e.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(e);
    return e;
  }
  const G = (p, a) => mk('g', a, p);
  const OL = (x) => Object.assign({ stroke: INK, 'stroke-width': SW, 'stroke-linejoin': 'round', 'stroke-linecap': 'round' }, x);
  const R = (p, x, y, w, h, rx, fill, x2) => mk('rect', OL(Object.assign({ x, y, width: w, height: h, rx: rx || 0, fill }, x2)), p);
  const P = (p, d, fill, x2) => mk('path', OL(Object.assign({ d, fill: fill || 'none' }, x2)), p);
  const Ci = (p, cx, cy, r, fill, x2) => mk('circle', OL(Object.assign({ cx, cy, r, fill }, x2)), p);
  const E = (p, cx, cy, rx, ry, fill, x2) => mk('ellipse', OL(Object.assign({ cx, cy, rx, ry, fill }, x2)), p);
  const L = (p, x1, y1, x2, y2, x3) => mk('line', OL(Object.assign({ x1, y1, x2, y2 }, x3)), p);
  const NOSTROKE = { stroke: 'none' };
  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
  const smooth = (t) => t * t * (3 - 2 * t);
  const hash = (n) => { const x = Math.sin(n * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
  const strHash = (s) => { let h = 7; for (let i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) % 100003; return h; };

  function fontAttrs(o) {
    const fam = o.fam === 'b' ? FB : FD;
    return { 'font-family': fam, 'font-weight': o.w || (o.fam === 'b' ? 600 : 800), 'font-size': o.size || 40 };
  }
  // Text (centered by default); supports "\n" multi-line, vertically centered on y.
  function T(p, str, x, y, o) {
    o = o || {};
    const size = o.size || 40;
    const t = mk('text', Object.assign({ x, y, fill: o.fill || INK, 'text-anchor': o.anchor || 'middle', 'dominant-baseline': 'central' }, fontAttrs(o)), p);
    if (o.stroke) { t.setAttribute('stroke', o.strokeColor || '#fff'); t.setAttribute('stroke-width', o.stroke); t.setAttribute('paint-order', 'stroke'); t.setAttribute('stroke-linejoin', 'round'); }
    if (o.ls != null) t.setAttribute('letter-spacing', o.ls);
    if (o.transform) t.setAttribute('transform', o.transform);
    const lines = String(str).split('\n');
    if (lines.length === 1) t.textContent = lines[0];
    else {
      const lh = size * (o.lh || 1.05);
      lines.forEach((ln, i) => { mk('tspan', { x, dy: i === 0 ? -(lines.length - 1) * lh / 2 : lh }, t).textContent = ln; });
    }
    return t;
  }
  // Width of (the widest line of) a string in the given font. Fonts must be loaded.
  function measure(str, o) {
    const svg = mk('svg', { width: 10, height: 10, style: 'position:absolute;left:-9999px;top:-9999px;visibility:hidden' });
    document.body.appendChild(svg);
    let w = 0;
    for (const ln of String(str).split('\n')) {
      const t = mk('text', fontAttrs(o), svg);
      if (o.ls != null) t.setAttribute('letter-spacing', o.ls);
      t.textContent = ln;
      w = Math.max(w, t.getComputedTextLength());
    }
    svg.remove();
    return w;
  }
  // Font size so that str fits maxW (never larger than o.size).
  const fit = (str, o, maxW) => { const w = measure(str, o); return w > maxW ? Math.floor(o.size * maxW / w) : o.size; };

  function pill(p, text, o) {
    const size = o.size || 38, h = o.h || 78, pad = o.pad == null ? 34 : o.pad, fam = o.fam || 'b', w = o.w || 700;
    const W = measure(text, { fam, w, size }) + pad * 2;
    const g = G(p);
    const bg = R(g, -W / 2, -h / 2, W, h, h / 2, o.bg, o.border ? { 'stroke-width': o.border } : NOSTROKE);
    const tx = T(g, text, 0, 1, { size, fam, w, fill: o.fg });
    return { g, bg, text: tx, width: W, height: h };
  }
  const TAG_STYLES = {
    dark: { bg: INK, fg: '#fff', border: 0 },
    light: { bg: '#fff', fg: INK, border: 5 },
    warm: { bg: C.orange, fg: '#fff', border: 5 },
    cool: { bg: C.greyBlue, fg: '#fff', border: 5 },
  };

  // ---------- shared small art ----------
  function sun(p, x, y, r) {
    Ci(p, x, y, r * 1.45, '#FFE7A6', NOSTROKE);
    Ci(p, x, y, r, C.sun);
  }
  function cloud(p, x, y, s) {
    const g = G(p, { transform: `translate(${x},${y}) scale(${s})` });
    P(g, 'M-90,30 A34,34 0 0 1 -60,-14 A46,46 0 0 1 20,-30 A38,38 0 0 1 84,0 A30,30 0 0 1 90,30 Z', '#fff', { 'stroke-width': SW / s });
    return g;
  }
  // Indian almond tree: layered flat canopy.
  function almondTree(p, x, base, s) {
    const g = G(p, { transform: `translate(${x},${base}) scale(${s})` });
    const sw = { 'stroke-width': SW / s };
    P(g, 'M-22,0 L-16,-430 L16,-430 L24,0 Z', C.woodDark, sw);
    P(g, 'M-10,-250 L-120,-300 M8,-330 L110,-380 M0,-420 L-60,-470', 'none', { 'stroke-width': 14, stroke: INK });
    P(g, 'M-10,-250 L-120,-300 M8,-330 L110,-380 M0,-420 L-60,-470', 'none', { 'stroke-width': 7, stroke: C.woodDark });
    const tiers = [[-290, 215, 50], [-370, 175, 44], [-450, 130, 40], [-520, 78, 32]];
    tiers.forEach(([ty, rx, ry], i) => {
      E(g, 0, ty, rx, ry, i % 2 ? C.leafDark : C.leaf, sw);
      P(g, `M${-rx * 0.62},${ty - ry * 0.35} Q0,${ty - ry * 0.85} ${rx * 0.62},${ty - ry * 0.35}`, 'none', { stroke: C.leafLight, 'stroke-width': 7 });
    });
    [[-150, -282], [120, -300], [-60, -372], [90, -446], [-170, -300]].forEach(([lx, ly], i) =>
      E(g, lx, ly, 13, 8, i % 2 ? C.red : C.orange, { 'stroke-width': 3 / s, transform: `rotate(${i * 37 - 30} ${lx} ${ly})` }));
    return g;
  }
  function picketFence(p, x0, x1, top, base, color) {
    const g = G(p);
    R(g, x0, top + 22, x1 - x0, 14, 3, color || '#fff', { 'stroke-width': 4 });
    R(g, x0, base - 34, x1 - x0, 14, 3, color || '#fff', { 'stroke-width': 4 });
    for (let x = x0 + 6; x < x1 - 20; x += 36)
      P(g, `M${x},${base} L${x},${top + 10} L${x + 11},${top} L${x + 22},${top + 10} L${x + 22},${base} Z`, color || '#fff', { 'stroke-width': 4 });
    return g;
  }
  function blinds(p, x, y, w, h) {
    R(p, x - 14, y - 14, w + 28, h + 28, 6, '#F4F7FA');
    R(p, x, y, w, h, 2, '#BFD0DD', { 'stroke-width': 4 });
    for (let yy = y + 6; yy < y + h * 0.72; yy += 26) R(p, x + 4, yy, w - 8, 16, 3, '#EEF2F6', { 'stroke-width': 3 });
    L(p, x + w - 30, y + 6, x + w - 30, y + h * 0.82, { 'stroke-width': 3 });
    Ci(p, x + w - 30, y + h * 0.82 + 8, 7, C.greyBlue2, { 'stroke-width': 3 });
  }
  function wallClock(p, x, y, r) {
    Ci(p, x, y, r, '#fff');
    for (let i = 0; i < 12; i++) {
      const a = i * Math.PI / 6, r1 = r * (i % 3 ? 0.8 : 0.7);
      L(p, x + Math.cos(a) * r1, y + Math.sin(a) * r1, x + Math.cos(a) * r * 0.88, y + Math.sin(a) * r * 0.88, { 'stroke-width': i % 3 ? 3 : 5 });
    }
    L(p, x, y, x, y - r * 0.6, { 'stroke-width': 6 });
    L(p, x, y, x + r * 0.42, y + r * 0.2, { 'stroke-width': 7 });
    Ci(p, x, y, 6, INK, NOSTROKE);
  }
  // Pencil-like sprite with its tip at (0,0), body going up-right.
  function stickSprite(p, kind) {
    const g = G(p);
    const a = G(g, { transform: 'rotate(-55)' });
    if (kind === 'pencil') {
      P(a, 'M0,0 L40,-15 L40,15 Z', '#F3D2A2', { 'stroke-width': 5 });
      P(a, 'M0,0 L13,-5 L13,5 Z', INK, { 'stroke-width': 4 });
      R(a, 40, -15, 130, 30, 0, C.sun, { 'stroke-width': 5 });
      L(a, 42, 0, 168, 0, { 'stroke-width': 3, stroke: '#D9A21E' });
      R(a, 170, -15, 18, 30, 0, '#B8C2CC', { 'stroke-width': 5 });
      R(a, 188, -15, 28, 30, 8, '#F49AC1', { 'stroke-width': 5 });
    } else { // highlighter
      P(a, 'M0,-4 L16,-14 L34,-14 L34,14 L16,14 L0,4 Z', '#F2D21B', { 'stroke-width': 5 });
      R(a, 34, -20, 120, 40, 8, C.highlight, { 'stroke-width': 5 });
      R(a, 140, -22, 60, 44, 10, INK, { 'stroke-width': 5 });
    }
    return g;
  }

  // ---------- 1. ticket ----------
  function ticket() {
    const el = G(), root = G(el);
    const X0 = -390, X1 = 390, Y0 = -225, Y1 = 225, r = 20, nx = -220, n = 18;
    const outline = `M${X0 + r},${Y0} L${nx - n},${Y0} A${n},${n} 0 0 0 ${nx + n},${Y0} L${X1 - r},${Y0} A${r},${r} 0 0 1 ${X1},${Y0 + r} L${X1},${Y1 - r} A${r},${r} 0 0 1 ${X1 - r},${Y1} L${nx + n},${Y1} A${n},${n} 0 0 0 ${nx - n},${Y1} L${X0 + r},${Y1} A${r},${r} 0 0 1 ${X0},${Y1 - r} L${X0},${Y0 + r} A${r},${r} 0 0 1 ${X0 + r},${Y0} Z`;
    const stubD = `M${X0 + r},${Y0} L${nx - n},${Y0} A${n},${n} 0 0 0 ${nx},${Y0 + n} L${nx},${Y1 - n} A${n},${n} 0 0 0 ${nx - n},${Y1} L${X0 + r},${Y1} A${r},${r} 0 0 1 ${X0},${Y1 - r} L${X0},${Y0 + r} A${r},${r} 0 0 1 ${X0 + r},${Y0} Z`;
    P(root, outline, INK, { transform: 'translate(14,14)', stroke: 'none', opacity: 0.16 });
    const body = (g, stubFill) => {
      P(g, outline, C.paper, NOSTROKE);
      P(g, stubD, stubFill, NOSTROKE);
      L(g, nx, Y0 + n + 10, nx, Y1 - n - 10, { 'stroke-width': 4, 'stroke-dasharray': '2 14' });
      P(g, outline, 'none');
    };
    const sx = (X0 + nx) / 2;

    // front
    const front = G(root);
    body(front, C.paper2);
    T(front, 'VÉ TÀU', sx, -180, { size: 34, fill: C.red });
    [['Hạng', 'con nít', -128], ['Số ghế', 'hàng đầu', -50], ['Giờ chạy', 'khi mở sách', 28]].forEach(([k, v, y]) => {
      T(front, k, sx, y, { fam: 'b', size: 19, fill: '#8A6D3B' });
      T(front, v, sx, y + 34, { size: fit(v, { size: 32 }, 140) });
    });
    let bars = '';
    for (let i = 0, x = sx - 62; x < sx + 60; i++) { const w = 3 + Math.round(hash(i + 3) * 5); bars += `M${x},128 h${w} v62 h${-w} Z `; x += w + 3 + Math.round(hash(i + 50) * 4); }
    mk('path', { d: bars, fill: INK }, front);
    T(front, 'Nº 1975', sx, 206, { fam: 'b', size: 16, fill: '#8A6D3B' });
    R(front, -196, -202, 568, 74, 18, C.orange);
    T(front, 'VÉ ĐI TUỔI THƠ', 88, -164, { size: 52, fill: '#fff', ls: 1 });
    const rowY = [-86, -30, 26, 82, 138, 194], rowX = -150;
    L(front, -178, rowY[0], -178, rowY[5], { 'stroke-width': 8 });
    L(front, -178, rowY[0], -178, rowY[5], { 'stroke-width': 3, stroke: C.paper, 'stroke-dasharray': '8 10' });
    const names = ['Ga 1|Xóm nhỏ', 'Ga 2|Hai giọng kể', 'Ga 3|Trò chơi', 'Ga 4|Tuổi thơ là gì', 'Ga 5|Chỗ xóc', 'Ga cuối|Ai nên lên tàu'];
    const stamps = [], stampInner = [], rows = [];
    names.forEach((nm, i) => {
      Ci(front, -178, rowY[i], 12, i === 5 ? C.red : C.sun, { 'stroke-width': 5 });
      const [a, b] = nm.split('|');
      const t = T(front, '', rowX, rowY[i], { fam: 'b', size: 29, anchor: 'start' });
      mk('tspan', { fill: C.orange, 'font-family': FD, 'font-weight': 800, 'font-size': 31 }, t).textContent = a;
      mk('tspan', {}, t).textContent = ' · ' + b;
      rows.push(t);
    });
    names.forEach((_, i) => {
      const s = G(front, { transform: `translate(300,${rowY[i]})`, display: 'none' });
      const inner = G(s);
      const art = G(inner, { transform: 'rotate(-12)', opacity: 0.92 });
      R(art, -60, -22, 120, 44, 9, 'rgba(214,40,40,0.10)', { stroke: C.red, 'stroke-width': 5 });
      R(art, -54, -16, 108, 32, 5, 'none', { stroke: C.red, 'stroke-width': 2 });
      T(art, 'ĐÃ QUA', 0, 1, { size: 26, fill: C.red, ls: 1 });
      stamps.push(s); stampInner.push(inner);
    });

    // back
    const back = G(root, { display: 'none' });
    body(back, C.paper2);
    T(back, 'Cho tôi xin một vé', sx, 0, { size: 32, fill: C.orange, transform: `rotate(-90 ${sx} 0)` });
    const ex = 85;
    [-100, 100].forEach((dx) => {
      E(back, ex + dx, -62, 78, 88, '#fff');
      Ci(back, ex + dx + 8, -50, 46, INK, NOSTROKE);
      Ci(back, ex + dx - 8, -66, 15, '#fff', NOSTROKE);
      Ci(back, ex + dx + 22, -30, 7, '#fff', NOSTROKE);
      P(back, `M${ex + dx - 60},${-168} Q${ex + dx},${-196} ${ex + dx + 60},${-170}`, 'none', { 'stroke-width': 8 });
    });
    T(back, 'Cho mượn: đôi mắt hồi bé', ex, 98, { size: 44 });
    T(back, 'Hạn dùng: vài giờ đọc sách', ex, 158, { fam: 'b', size: 30, fill: '#6B5A3A' });

    return {
      el, parts: { front, back, stamps, stampInner, rowY, rowX, rows },
      setFace(side) { const b = side === 'back'; front.setAttribute('display', b ? 'none' : 'inline'); back.setAttribute('display', b ? 'inline' : 'none'); },
    };
  }

  // ---------- 2/3. book covers ----------
  function bookCover(o) {
    const el = G(), root = G(el);
    R(root, -136, -206, 300, 440, 14, INK, { stroke: 'none', opacity: 0.85 });
    const cover = R(root, -150, -220, 300, 440, 14, o.bg);
    P(root, 'M-124,-220 L-136,-220 A14,14 0 0 0 -150,-206 L-150,206 A14,14 0 0 0 -136,220 L-124,220 Z', o.spine, NOSTROKE);
    L(root, -124, -217, -124, 217, { 'stroke-width': 4 });
    R(root, -150, -220, 300, 440, 14, 'none');
    const title = G(root);
    o.lines.forEach((ln, i) => {
      const txt = ln.t || ln;
      T(title, txt, 13, -170 + i * 46, { size: fit(txt, { size: 46 }, 236), fill: ln.c || '#fff', stroke: 7, strokeColor: INK });
    });
    const art = G(root);
    R(art, -106, -40, 238, 190, 14, o.panel);
    o.illus(art);
    R(art, -106, -40, 238, 190, 14, 'none');
    T(root, 'Nguyễn Nhật Ánh', 13, 188, { fam: 'b', w: 700, size: 22, fill: '#fff', stroke: 5, strokeColor: INK });
    T(root, '(bìa minh họa)', 7, 268, { fam: 'b', w: 500, size: 20, fill: C.grey });
    return { el, parts: { cover, title, art } };
  }
  function book1() {
    return bookCover({
      bg: C.orange, spine: '#C96A12', panel: C.sky,
      lines: ['CHO TÔI XIN', { t: 'MỘT VÉ', c: C.sun }, 'ĐI TUỔI THƠ'],
      illus(g) {
        sun(g, 82, 10, 24);
        P(g, 'M-103,95 Q-20,70 60,90 Q100,98 129,88 L129,147 L-103,147 Z', C.leaf, { 'stroke-width': 5 });
        P(g, 'M-6,147 L18,96 L36,96 L64,147 Z', C.paper, { 'stroke-width': 4 });
        const t = G(g, { transform: 'translate(-30,6) rotate(-14)' });
        R(t, -44, -26, 88, 52, 6, C.paper, { 'stroke-width': 4 });
        L(t, -22, -20, -22, 20, { 'stroke-width': 2.5, 'stroke-dasharray': '4 5' });
        L(t, -10, -8, 30, -8, { 'stroke-width': 3 }); L(t, -10, 6, 20, 6, { 'stroke-width': 3 });
        Ci(g, -60, 62, 9, INK, NOSTROKE);
        P(g, 'M-60,70 L-60,92 M-60,76 L-70,86 M-60,76 L-50,66 M-60,92 L-67,104 M-60,92 L-53,104', 'none', { 'stroke-width': 5 });
      },
    });
  }
  function book2() {
    return bookCover({
      bg: C.leaf, spine: C.leafDark, panel: '#E4F4FA',
      lines: ['TÔI THẤY', { t: 'HOA VÀNG', c: C.sun }, 'TRÊN CỎ XANH'],
      illus(g) {
        P(g, 'M-103,60 Q0,20 129,55 L129,147 L-103,147 Z', '#8CC97A', { 'stroke-width': 5 });
        P(g, 'M-103,105 Q20,80 129,108 L129,147 L-103,147 Z', C.leaf, { 'stroke-width': 5 });
        for (let i = 0; i < 14; i++) {
          const x = -90 + hash(i + 11) * 205, y = 60 + hash(i + 31) * 78, s = 0.55 + hash(i + 71) * 0.5;
          flower(g, x, y, 9 * s);
        }
        L(g, 30, 50, 30, 100, { 'stroke-width': 5, stroke: C.leafDark });
        flower(g, 30, 30, 20);
      },
    });
  }
  function flower(g, x, y, r) {
    for (let k = 0; k < 5; k++) { const a = k * 2 * Math.PI / 5 - Math.PI / 2; Ci(g, x + Math.cos(a) * r, y + Math.sin(a) * r, r * 0.72, C.sun, { 'stroke-width': Math.max(2, r * 0.22) }); }
    Ci(g, x, y, r * 0.55, C.orange, { 'stroke-width': Math.max(2, r * 0.22) });
  }

  // ---------- 4. scale ----------
  function scale() {
    const el = G(), root = G(el);
    const PY = -150, ARM = 230, HANG = 140;
    P(root, 'M-120,190 L-92,154 L92,154 L120,190 Z', C.slate);
    R(root, -15, PY, 30, 306, 8, C.sun);
    const sides = [{ dir: -1, label: 'truyện tranh chữ', bg: C.orange }, { dir: 1, label: 'sách dạy đời', bg: C.greyBlue }];
    const hangs = sides.map((s) => {
      const h = G(root);
      L(h, 0, 0, -96, HANG, { 'stroke-width': 4 }); L(h, 0, 0, 96, HANG, { 'stroke-width': 4 });
      const lb = pill(h, s.label, { size: 25, h: 52, pad: 20, bg: s.bg, fg: '#fff', border: 5 });
      lb.g.setAttribute('transform', `translate(0,${HANG - 30})`);
      P(h, `M-110,${HANG} L110,${HANG} Q88,${HANG + 56} 0,${HANG + 56} Q-88,${HANG + 56} -110,${HANG} Z`, C.sun);
      Ci(h, 0, 0, 9, C.slate, { 'stroke-width': 4 });
      return h;
    });
    const beam = G(root);
    R(beam, -ARM - 16, PY - 12, 2 * ARM + 32, 24, 12, C.orange);
    [-ARM, ARM].forEach((x) => Ci(beam, x, PY, 6, INK, NOSTROKE));
    P(root, `M-26,${PY - 36} L26,${PY - 36} L0,${PY - 4} Z`, C.slate, { 'stroke-width': 5 });
    Ci(root, 0, PY, 18, C.sun);
    const api = {
      el, parts: { beam, hangs, pivot: { x: 0, y: PY } },
      // deg > 0 tips the right pan down (clockwise).
      setTilt(deg) {
        const a = deg * Math.PI / 180;
        beam.setAttribute('transform', `rotate(${deg} 0 ${PY})`);
        sides.forEach((s, i) => hangs[i].setAttribute('transform', `translate(${(s.dir * ARM * Math.cos(a)).toFixed(2)},${(PY + s.dir * ARM * Math.sin(a)).toFixed(2)})`));
      },
    };
    api.setTilt(0);
    return api;
  }

  // ---------- 5. chapters ----------
  function chapters() {
    const el = G(), root = G(el);
    const X0 = -470, X1 = 470, YE = -70, YC = -10;
    const ropeY = (x) => { const t = (x - X0) / (X1 - X0); return YE * (1 - t) * (1 - t) + 2 * t * (1 - t) * YC + YE * t * t; };
    [X0, X1].forEach((x) => { R(root, x - 12, YE - 30, 24, 50, 6, C.woodDark, { 'stroke-width': 5 }); });
    P(root, `M${X0},${YE} Q0,${YC} ${X1},${YE}`, 'none', { 'stroke-width': 6 });
    const colors = [C.sun, C.sky, C.leafLight, '#F7C6B5', '#FFD9A0', '#D7C8F0'];
    const tilt = [-4, 3, -2, 4, -3, 2];
    const boxes = [], boxInner = [], boxPos = [];
    for (let i = 0; i < 6; i++) {
      const x = -375 + i * 150, y = ropeY(x);
      const b = G(root, { transform: `translate(${x},${y.toFixed(1)})` });
      const inner = G(b);
      const art = G(inner, { transform: `rotate(${tilt[i]})` });
      R(art, -58, 10, 116, 124, 12, colors[i]);
      T(art, 'Ch.' + (i + 1), 0, 58, { size: 42 });
      L(art, -34, 98, 34, 98, { 'stroke-width': 5, stroke: 'rgba(29,29,31,0.35)' });
      L(art, -22, 114, 22, 114, { 'stroke-width': 5, stroke: 'rgba(29,29,31,0.35)' });
      R(art, -10, -20, 20, 44, 4, '#E2B47C', { 'stroke-width': 4 });
      L(art, 0, -16, 0, 20, { 'stroke-width': 3 });
      Ci(art, 0, 0, 4, '#B8C2CC', { 'stroke-width': 2.5 });
      boxes.push(b); boxInner.push(inner); boxPos.push({ x, y });
    }
    return { el, parts: { boxes, boxInner, boxPos } };
  }

  // ---------- 6. album ----------
  function polaroid(p, caption, scene) {
    R(p, -172, -192, 360, 400, 8, INK, { stroke: 'none', opacity: 0.18 });
    R(p, -180, -200, 360, 400, 8, '#fff');
    const ph = G(p);
    scene(ph);
    R(p, -155, -175, 310, 290, 4, 'none', { 'stroke-width': 5 });
    T(p, caption, 0, 158, { size: 42, w: 700 });
  }
  const SCENES = [
    ['thả diều', (g) => {
      R(g, -155, -175, 310, 290, 4, C.sky, NOSTROKE);
      cloud(g, -70, -110, 0.45);
      P(g, 'M-155,60 Q0,30 155,55 L155,115 L-155,115 Z', C.leaf, { 'stroke-width': 5 });
      P(g, 'M70,-140 L100,-100 L70,-50 L40,-100 Z', C.red, { 'stroke-width': 5 });
      L(g, 70, -140, 70, -50, { 'stroke-width': 3 }); L(g, 40, -100, 100, -100, { 'stroke-width': 3 });
      P(g, 'M70,-50 q-12,14 0,26 q12,12 -2,26', 'none', { 'stroke-width': 4 });
      P(g, 'M70,-50 Q20,10 -40,40', 'none', { 'stroke-width': 2.5 });
      [[-40, 40, C.orange], [-90, 50, C.teal]].forEach(([x, y, c]) => {
        Ci(g, x, y - 34, 11, INK, NOSTROKE);
        P(g, `M${x - 11},${y + 4} L${x - 8},${y - 22} L${x + 8},${y - 22} L${x + 11},${y + 4} Z`, c, { 'stroke-width': 4 });
        P(g, `M${x - 5},${y + 4} L${x - 6},${y + 22} M${x + 5},${y + 4} L${x + 6},${y + 22} M${x + 8},${y - 18} L${x + 18},${y - 32}`, 'none', { 'stroke-width': 4 });
      });
    }],
    ['con hẻm', (g) => {
      R(g, -155, -175, 310, 290, 4, '#FFE3B0', NOSTROKE);
      sun(g, 90, -120, 22);
      R(g, -150, -60, 120, 130, 0, '#F7C6B5', { 'stroke-width': 4 });
      P(g, 'M-155,-60 L-130,-95 L-40,-95 L-20,-60 Z', C.roof, { 'stroke-width': 4 });
      R(g, -115, -10, 40, 80, 0, C.teal, { 'stroke-width': 4 });
      P(g, 'M-155,115 L-30,70 L40,70 L155,115 Z', C.lane, { 'stroke-width': 4 });
      R(g, 66, -40, 14, 110, 0, C.woodDark, { 'stroke-width': 4 });
      E(g, 73, -40, 70, 18, C.leaf, { 'stroke-width': 4 });
      E(g, 73, -70, 50, 15, C.leafDark, { 'stroke-width': 4 });
      E(g, 73, -95, 28, 12, C.leaf, { 'stroke-width': 4 });
    }],
    ['mèo nhà bên', (g) => {
      R(g, -155, -175, 310, 290, 4, '#F6B98A', NOSTROKE);
      Ci(g, -90, -115, 26, C.paper, { 'stroke-width': 4 });
      R(g, -155, 75, 310, 40, 0, C.lane, NOSTROKE);
      for (let x = -150; x < 150; x += 38) P(g, `M${x},95 L${x},0 L${x + 14},-14 L${x + 28},0 L${x + 28},95 Z`, '#fff', { 'stroke-width': 4 });
      R(g, -155, 14, 310, 14, 0, '#fff', { 'stroke-width': 4 });
      const cat = 'M10,-14 C10,-50 30,-70 60,-70 L58,-96 L74,-80 L86,-80 L100,-96 L98,-66 C110,-50 104,-30 90,-24 C110,-24 116,-14 116,-14 Z';
      P(g, cat, INK, { 'stroke-width': 4 });
      P(g, 'M14,-16 C-20,-20 -26,-50 -6,-60', 'none', { 'stroke-width': 9 });
      Ci(g, 72, -56, 4, C.sun, NOSTROKE); Ci(g, 92, -56, 4, C.sun, NOSTROKE);
    }],
  ];
  function album() {
    const el = G(), root = G(el);
    const base = [{ x: 0, y: 0, r: -3 }, { x: 16, y: 8, r: 5 }, { x: -14, y: 12, r: -7 }];
    const cards = [];
    for (let k = 2; k >= 0; k--) { const c = G(root); polaroid(c, SCENES[k][0], SCENES[k][1]); cards[k] = c; }
    const api = {
      el, parts: { cards },
      setFlip(t) {
        for (let k = 0; k < 3; k++) {
          const b = base[k], c = cards[k];
          const p = k < 2 ? clamp(t - k, 0, 1) : 0, e = smooth(p);
          const settle = k > 0 ? smooth(clamp(t - k + 1, 0, 1)) : 0;
          const rot = b.r * (1 - 0.6 * settle) + e * 38;
          c.setAttribute('transform', `translate(${(b.x * (1 - settle) + e * 560).toFixed(1)},${(b.y * (1 - settle) - e * 300).toFixed(1)}) rotate(${rot.toFixed(2)})`);
          c.setAttribute('opacity', (1 - e).toFixed(3));
          c.setAttribute('display', p >= 1 ? 'none' : 'inline');
        }
      },
    };
    api.setFlip(0);
    return api;
  }

  // ---------- 7/8. pages ----------
  const BAR_Y = [-150, -100, -50, 0, 50, 100, 150], BAR_X = -238, BAR_L = [470, 420, 500, 380, 460, 310, 430];
  function page() {
    const el = G(), root = G(el);
    R(root, -296, -206, 620, 440, 14, INK, { stroke: 'none', opacity: 0.18 });
    R(root, -310, -220, 620, 440, 14, '#fff');
    L(root, -262, -214, -262, 214, { stroke: '#F2A3A3', 'stroke-width': 3 });
    for (let i = 0; i < 7; i++) { Ci(root, -286, -180 + i * 60, 9, C.pale, { 'stroke-width': 4 }); }
    const under = G(root), bars = [];
    BAR_Y.forEach((y, i) => bars.push(R(root, BAR_X, y - 9, BAR_L[i], 18, 9, C.bar, NOSTROKE)));
    const over = G(root);
    return { el, root, under, over, bars };
  }
  function strikePage() {
    const pg = page();
    const lines = [2, 4].map(() => mk('path', { stroke: C.red, 'stroke-width': 9, 'stroke-linecap': 'round', fill: 'none', display: 'none' }, pg.over));
    const pencil = stickSprite(pg.over, 'pencil');
    const api = {
      el: pg.el, parts: { bars: pg.bars, strikes: lines, pencil },
      setProgress(t) {
        t = clamp(t, 0, 1);
        const ps = [clamp(t / 0.5, 0, 1), clamp((t - 0.5) / 0.5, 0, 1)];
        let tip;
        [2, 4].forEach((bi, j) => {
          const x0 = BAR_X - 6, y = BAR_Y[bi] + 1, x1 = x0 + (BAR_L[bi] + 12) * ps[j];
          lines[j].setAttribute('d', `M${x0},${y} L${x1.toFixed(1)},${y}`);
          lines[j].setAttribute('display', ps[j] > 0 ? 'inline' : 'none');
          if ((j === 0 && t < 0.5) || (j === 1 && t >= 0.5)) tip = [x1, y];
        });
        pencil.setAttribute('transform', `translate(${tip[0].toFixed(1)},${tip[1]})`);
      },
    };
    api.setProgress(0);
    return api;
  }
  function markPage() {
    const pg = page();
    const bi = 3, x0 = BAR_X - 12, W = BAR_L[bi] + 24;
    const hl = mk('rect', { x: x0, y: BAR_Y[bi] - 23, height: 46, width: 0, rx: 4, fill: C.highlight, opacity: 0.85 }, pg.under);
    const marker = stickSprite(pg.over, 'marker');
    const api = {
      el: pg.el, parts: { bars: pg.bars, highlight: hl, marker },
      setProgress(t) {
        t = clamp(t, 0, 1);
        hl.setAttribute('width', (W * t).toFixed(1));
        marker.setAttribute('transform', `translate(${(x0 + W * t).toFixed(1)},${BAR_Y[bi] + 4})`);
      },
    };
    api.setProgress(0);
    return api;
  }

  // ---------- 9. checklist ----------
  function checklist(rows) {
    const el = G(), root = G(el);
    const H = 92, W = 760, top = -rows.length * H / 2;
    const gs = rows.map((r, i) => {
      const g = G(root, { transform: `translate(0,${top + H / 2 + i * H})` });
      const ok = r.kind === 'ok';
      Ci(g, -W / 2 + 34, 0, 32, ok ? C.teal : C.orange, { 'stroke-width': 5 });
      if (ok) P(g, `M${-W / 2 + 19},1 L${-W / 2 + 30},13 L${-W / 2 + 50},-12`, 'none', { stroke: '#fff', 'stroke-width': 8 });
      else L(g, -W / 2 + 19, 0, -W / 2 + 49, 0, { stroke: '#fff', 'stroke-width': 8 });
      T(g, r.text, -W / 2 + 90, 2, { fam: 'b', size: 44, anchor: 'start' });
      return g;
    });
    return { el, parts: { rows: gs } };
  }

  // ---------- 10. icecream ----------
  function icecream() {
    const el = G(), root = G(el);
    const BOT = 80, PUD = 250;
    const puddle = E(root, 0, PUD, 0, 0, '#F7A9C4', { 'stroke-width': 4, display: 'none' });
    R(root, -20, 40, 40, 175, 14, '#E2B47C');
    L(root, -6, 90, -6, 190, { stroke: '#C08E57', 'stroke-width': 4 });
    const body = 'M-90,56 L-90,-140 A60,60 0 0 1 -30,-200 L8,-200 A26,26 0 0 0 48,-176 A26,26 0 0 0 90,-138 L90,56 A24,24 0 0 1 66,80 L-66,80 A24,24 0 0 1 -90,56 Z';
    P(root, body, '#F48FB1', NOSTROKE);
    P(root, 'M-90,-20 Q-60,-38 -30,-20 T30,-20 T90,-20 L90,56 A24,24 0 0 1 66,80 L-66,80 A24,24 0 0 1 -90,56 Z', C.orange, NOSTROKE);
    P(root, 'M-90,-20 Q-60,-38 -30,-20 T30,-20 T90,-20', 'none', { 'stroke-width': 4 });
    P(root, 'M-62,-150 L-62,-60 M-62,10 L-62,40', 'none', { stroke: '#fff', 'stroke-width': 10, opacity: 0.7 });
    P(root, body, 'none');
    const DROPS = [{ x: -60, P: 1.3, d: 0.0 }, { x: 50, P: 1.0, d: 0.35 }, { x: -36, P: 1.7, d: 0.8 }];
    const drops = DROPS.map((d, i) => mk('path', OL({ fill: i === 1 ? C.orange : '#F48FB1', 'stroke-width': 4, display: 'none' }), root));
    const dropD = (cx, cy, r) => `M${cx},${cy - 1.8 * r} Q${cx + r * 1.05},${cy - 0.25 * r} ${cx + r},${cy + 0.1 * r} A${r},${r} 0 1 1 ${cx - r},${cy + 0.1 * r} Q${cx - r * 1.05},${cy - 0.25 * r} ${cx},${cy - 1.8 * r} Z`;
    const api = {
      el, parts: { drops, puddle },
      setDrip(sec) {
        sec = Math.max(0, sec || 0);
        DROPS.forEach((d, i) => {
          const s = sec - d.d;
          if (s < 0) { drops[i].setAttribute('display', 'none'); return; }
          const u = (s / d.P) % 1, R0 = 13;
          let cy, r;
          if (u < 0.5) { r = R0 * Math.max(0.15, u / 0.5); cy = BOT - 6 + r * 1.5; }
          else { const f = (u - 0.5) / 0.5; r = R0; cy = BOT - 6 + R0 * 1.5 + (PUD - BOT - 10) * f * f; }
          drops[i].setAttribute('d', dropD(d.x, +cy.toFixed(1), +r.toFixed(2)));
          drops[i].setAttribute('display', cy > PUD - 4 || r < 3 ? 'none' : 'inline');
        });
        const g = clamp((sec - 0.6) / 6, 0, 1);
        puddle.setAttribute('display', sec > 0.6 ? 'inline' : 'none');
        puddle.setAttribute('rx', (24 + 66 * Math.sqrt(g)).toFixed(1));
        puddle.setAttribute('ry', (6 + 10 * Math.sqrt(g)).toFixed(1));
      },
    };
    api.setDrip(0);
    return api;
  }

  // ---------- 11. bubble ----------
  function bubble(text) {
    const el = G(), root = G(el);
    const body = P(root, 'M-50,-65 L50,-65 A50,50 0 0 1 100,-15 L100,15 A50,50 0 0 1 50,65 L-8,65 L-78,104 L-48,62 A50,50 0 0 1 -100,15 L-100,-15 A50,50 0 0 1 -50,-65 Z', '#fff');
    const t = T(root, text, 0, 0, { size: fit(text, { size: 52, w: 700 }, 168), w: 700 });
    return { el, parts: { body, text: t } };
  }

  // ---------- 12. sign ----------
  function sign(text) {
    const el = G(), root = G(el);
    const BY = -200, W = 250, H = 130, seed = strHash(String(text));
    R(root, -9, BY, 18, -BY, 4, C.wood, { 'stroke-width': 5 });
    const b = G(root, { transform: `translate(0,${BY}) rotate(-2)` });
    const pts = [], j = (k) => (hash(seed + k) - 0.5) * 7;
    let k = 0;
    const edge = (x0, y0, x1, y1, n) => { for (let i = 0; i < n; i++) { const f = i / n; pts.push([x0 + (x1 - x0) * f + (i ? j(k++) : 0), y0 + (y1 - y0) * f + (i ? j(k++) : 0)]); } };
    edge(-W / 2, -H / 2, W / 2, -H / 2, 6); edge(W / 2, -H / 2, W / 2, H / 2, 3); edge(W / 2, H / 2, -W / 2, H / 2, 6); edge(-W / 2, H / 2, -W / 2, -H / 2, 3);
    const d = 'M' + pts.map((p) => p.map((v) => v.toFixed(1)).join(',')).join(' L') + ' Z';
    const board = P(b, d, C.cardboard);
    L(b, -W / 2 + 18, H / 2 - 14, -W / 2 + 70, H / 2 - 14, { stroke: '#C9A472', 'stroke-width': 4 });
    L(b, W / 2 - 60, -H / 2 + 14, W / 2 - 22, -H / 2 + 14, { stroke: '#C9A472', 'stroke-width': 4 });
    const lines = String(text).split('\n').length;
    const t = T(b, text, 0, 2, { size: fit(text, { size: 40 }, 218), lh: 1.0, transform: 'rotate(-2)' });
    if (lines > 2) t.setAttribute('font-size', 30);
    return { el, parts: { board, text: t, boardCenter: { x: 0, y: BY } } };
  }

  // ---------- 13/14. tag & bigText ----------
  function tag(text, style) {
    const el = G();
    const s = TAG_STYLES[style] || TAG_STYLES.light;
    const p = pill(el, text, { bg: s.bg, fg: s.fg, border: s.border });
    return { el, parts: { bg: p.bg, text: p.text }, width: p.width, height: p.height };
  }
  function bigText(text, opts) {
    const o = Object.assign({ size: 120, color: INK, weight: 800, family: 'Baloo 2' }, opts || {});
    const el = G();
    const t = T(el, text, 0, 0, { size: o.size, fill: o.color, w: o.weight, stroke: o.stroke, strokeColor: o.strokeColor || '#fff' });
    t.setAttribute('font-family', `'${o.family}', 'DejaVu Sans', sans-serif`);
    return { el, parts: { text: t } };
  }

  // ---------- backgrounds ----------
  function skyGrad(p, id, top, low) {
    const defs = mk('defs', null, p);
    const lg = mk('linearGradient', { id, x1: 0, y1: 0, x2: 0, y2: 1 }, defs);
    mk('stop', { offset: 0, 'stop-color': top }, lg); mk('stop', { offset: 1, 'stop-color': low }, lg);
    return `url(#${id})`;
  }
  function roof(p, x0, x1, y, h, color, dark) {
    const oh = 22, ins = 44;
    P(p, `M${x0 - oh},${y} L${x0 + ins},${y - h} L${x1 - ins},${y - h} L${x1 + oh},${y} Z`, color);
    let d = '';
    for (let r = 0; r < 4; r++) {
      const ya = y - h * r / 4, yb = y - h * (r + 1) / 4, fa = r / 4;
      const xa = x0 - oh + (oh + ins) * fa, xb = x1 + oh - (oh + ins) * fa;
      if (r) d += `M${xa + 6},${ya} L${xb - 6},${ya} `;
      for (let x = xa + 16 + (r % 2) * 14; x < xb - 12; x += 28) d += `M${x},${ya - 4} L${x},${yb + 5} `;
    }
    mk('path', { d, stroke: dark, 'stroke-width': 3, 'stroke-linecap': 'round', fill: 'none' }, p);
    P(p, `M${x0 - oh},${y} L${x0 + ins},${y - h} L${x1 - ins},${y - h} L${x1 + oh},${y} Z`, 'none');
    R(p, x0 - oh - 6, y - 4, x1 - x0 + 2 * oh + 12, 14, 4, dark, { 'stroke-width': 5 });
  }
  function house(p, x, w, top, base, o) {
    const g = G(p);
    R(g, x, top, w, base - top, 0, o.wall);
    roof(g, x, x + w, top, o.rh || 80, o.roof || C.roof, C.roofDark);
    (o.win || []).forEach((wo) => {
      const wx = x + wo, wy = top + 44;
      R(g, wx - 70, wy, 22, 96, 2, o.door, { 'stroke-width': 4 });
      R(g, wx + 48, wy, 22, 96, 2, o.door, { 'stroke-width': 4 });
      R(g, wx - 48, wy, 96, 96, 2, '#FFF1C7', { 'stroke-width': 5 });
      let d = ''; for (let bx = wx - 30; bx < wx + 40; bx += 20) d += `M${bx},${wy + 4} L${bx},${wy + 92} `;
      P(g, d, 'none', { 'stroke-width': 3 });
      R(g, wx - 56, wy + 96, 112, 10, 3, '#fff', { 'stroke-width': 4 });
    });
    if (o.doorAt != null) {
      const dx = x + w * o.doorAt, dw = 120, dh = 176;
      R(g, dx - dw / 2 - 10, base - dh - 10, dw + 20, dh + 10, 2, '#fff', { 'stroke-width': 4 });
      R(g, dx - dw / 2, base - dh, dw, dh, 2, o.door, { 'stroke-width': 5 });
      L(g, dx, base - dh, dx, base, { 'stroke-width': 4 });
      R(g, dx - 48, base - dh + 18, 36, 56, 2, 'rgba(255,255,255,0.25)', { 'stroke-width': 3 });
      R(g, dx + 12, base - dh + 18, 36, 56, 2, 'rgba(255,255,255,0.25)', { 'stroke-width': 3 });
      Ci(g, dx - 10, base - 88, 4, INK, NOSTROKE); Ci(g, dx + 10, base - 88, 4, INK, NOSTROKE);
    }
    return g;
  }
  function plant(p, x, base, kind, s) {
    const g = G(p, { transform: `translate(${x},${base}) scale(${s || 1})` });
    if (kind === 'spiky') [-30, -12, 8, 26].forEach((a, i) => E(g, a * 0.9, -78 - (i % 2) * 14, 11, 40, i % 2 ? C.leafDark : C.leaf, { 'stroke-width': 4, transform: `rotate(${a} ${a * 0.9} -60)` }));
    else { Ci(g, -18, -66, 24, C.leaf, { 'stroke-width': 4 }); Ci(g, 18, -70, 24, C.leafDark, { 'stroke-width': 4 }); Ci(g, 0, -88, 24, C.leaf, { 'stroke-width': 4 }); if (kind === 'flower') [[-20, -80], [16, -92], [6, -66]].forEach(([fx, fy]) => Ci(g, fx, fy, 7, C.red, { 'stroke-width': 3 })); }
    P(g, 'M-30,-52 L30,-52 L22,0 L-22,0 Z', '#D9693F', { 'stroke-width': 5 });
    R(g, -34, -58, 68, 12, 3, '#C8553D', { 'stroke-width': 4 });
    return g;
  }
  function leafOnGround(p, x, y, rot, c) {
    const g = G(p, { transform: `translate(${x},${y}) rotate(${rot})` });
    E(g, 0, 0, 22, 12, c, { 'stroke-width': 3.5 });
    L(g, -18, 0, 20, 0, { 'stroke-width': 2.5 });
  }

  function bgXom() {
    const el = G(), root = G(el);
    R(root, 0, 0, 1920, 1080, 0, skyGrad(root, 'propsXomSky', C.warmSkyTop, C.warmSkyLow), NOSTROKE);
    sun(root, 1430, 210, 78);
    cloud(root, 820, 140, 0.9); cloud(root, 1720, 330, 0.6); cloud(root, 520, 300, 0.55);
    // far trees peeking over roofs
    [[560, 480, 70], [640, 460, 60], [1180, 470, 70], [1260, 490, 56], [1620, 470, 64]].forEach(([x, y, r]) => Ci(root, x, y, r, '#9CCB86', { 'stroke-width': 5 }));
    house(root, -40, 430, 560, 800, { wall: '#FBE8C4', door: C.teal, doorAt: 0.72, win: [110], rh: 80 });
    house(root, 390, 380, 590, 800, { wall: '#F7C6B5', door: '#3D7EA6', doorAt: 0.35, win: [290], rh: 70 });
    house(root, 770, 450, 570, 800, { wall: '#FCE29A', door: C.leafDark, doorAt: 0.68, win: [130], rh: 86 });
    house(root, 1220, 360, 590, 800, { wall: '#CDE8C4', door: C.orange, doorAt: 0.3, win: [255], rh: 70 });
    house(root, 1580, 380, 560, 800, { wall: '#FBE8C4', door: '#3D7EA6', doorAt: 0.25, win: [290], rh: 84 });
    picketFence(root, 1404, 1572, 724, 800);
    plant(root, 640, 800, 'flower', 0.8); plant(root, 1150, 800, 'round', 0.8); plant(root, 1745, 800, 'spiky', 0.85); plant(root, 1830, 800, 'flower', 0.75);
    // lane
    R(root, -10, 800, 1940, 290, 0, C.lane, { 'stroke-width': 0 });
    R(root, -10, 798, 1940, 22, 0, C.curb, { 'stroke-width': 5 });
    P(root, 'M120,1000 q60,-10 120,6 M1640,1030 q80,-14 170,4 M760,1050 q40,-8 90,2', 'none', { stroke: '#D4B585', 'stroke-width': 5 });
    [[60, 1050, 14], [1880, 980, 10], [1560, 1060, 12], [300, 1070, 9]].forEach(([x, y, r]) => E(root, x, y, r, r * 0.6, '#CDB28A', { 'stroke-width': 4 }));
    [[240, 870, -20, C.red], [330, 990, 30, C.orange], [1700, 960, 70, C.red], [1820, 880, -40, C.sun], [90, 940, 10, C.orange], [1600, 1040, 5, C.orange]].forEach((l) => leafOnGround(root, ...l));
    // almond tree (left edge)
    R(root, 120, 790, 110, 30, 6, '#B8A48A', { 'stroke-width': 5 });
    almondTree(root, 175, 805, 1.0);
    // electric pole + wires (right edge)
    P(root, 'M1760,165 Q1100,300 -10,190 M1760,175 Q1000,330 -10,240 M1880,160 Q1900,200 1930,210', 'none', { 'stroke-width': 3.5 });
    R(root, 1755, 100, 26, 720, 4, '#B8B2A8');
    R(root, 1700, 150, 136, 18, 4, '#8E877C', { 'stroke-width': 5 });
    [1714, 1822].forEach((x) => R(root, x - 6, 132, 12, 20, 4, C.paper, { 'stroke-width': 4 }));
    P(root, 'M1745,330 q-24,10 0,20 q24,10 0,20 q-24,10 0,20', 'none', { 'stroke-width': 4 });
    R(root, 1790, 420, 60, 80, 6, '#8E877C', { 'stroke-width': 5 });
    // a little bird on the wire
    const bx = 1200, by = 262;
    P(root, `M${bx - 18},${by - 2} Q${bx - 16},${by - 22} ${bx},${by - 22} Q${bx + 14},${by - 22} ${bx + 16},${by - 10} L${bx + 26},${by - 8} L${bx + 16},${by - 4} Q${bx + 6},${by + 2} ${bx - 18},${by - 2} Z`, C.slate, { 'stroke-width': 4 });
    return { el, parts: { groundY: 930 } };
  }

  function officeScene(p, x0, x1) {
    const xl = x0 ? x0 : -10;
    R(p, x0, 0, x1 - x0, 930, 0, C.pale, NOSTROKE);
    R(p, x0, 760, x1 - x0, 170, 0, C.paleBlue, NOSTROKE);
    L(p, x0, 760, x1, 760, { 'stroke-width': 5 });
    R(p, xl, 930, x1 - xl + 10, 160, 0, C.greyBlue2, { 'stroke-width': 0 });
    let d = '';
    for (let y = 980; y < 1080; y += 50) d += `M${x0},${y} L${x1},${y} `;
    for (let x = x0 + 80, r = 0; x < x1; x += 240, r++) d += `M${x},930 L${x},980 M${x + 120},980 L${x + 120},1030 M${x},1030 L${x},1080 `;
    mk('path', { d, stroke: '#8796A6', 'stroke-width': 4, fill: 'none' }, p);
    R(p, xl, 912, x1 - xl + 10, 22, 0, C.slate, { 'stroke-width': 5 });
  }
  function bgOffice() {
    const el = G(), root = G(el);
    officeScene(root, 0, 1920);
    R(root, 720, -10, 480, 34, 6, '#F4F7FA');
    blinds(root, 320, 100, 360, 300);
    wallClock(root, 1010, 190, 68);
    // calendar
    R(root, 1260, 130, 170, 190, 6, '#fff');
    R(root, 1260, 130, 170, 42, 6, C.greyBlue, { 'stroke-width': 5 });
    let d = ''; for (let r = 0; r < 4; r++) for (let c = 0; c < 5; c++) d += `M${1278 + c * 28},${188 + r * 30} h18 v18 h-18 Z `;
    mk('path', { d, fill: C.pale, stroke: '#9AA9B8', 'stroke-width': 2 }, root);
    // filing cabinet
    R(root, 40, 560, 230, 370, 8, C.greyBlue2);
    for (let i = 0; i < 3; i++) { R(root, 58, 578 + i * 116, 194, 100, 6, '#B7C3CF', { 'stroke-width': 5 }); R(root, 125, 610 + i * 116, 60, 14, 7, C.slate, { 'stroke-width': 4 }); }
    R(root, 70, 520, 150, 40, 4, '#F4F7FA', { 'stroke-width': 5 }); R(root, 84, 496, 130, 26, 4, C.paleBlue, { 'stroke-width': 5 });
    // plant
    E(root, 312, 820, 12, 60, '#7FA58F', { 'stroke-width': 4, transform: 'rotate(-14 312 860)' });
    E(root, 340, 800, 12, 74, '#6C9481', { 'stroke-width': 4 });
    E(root, 366, 820, 12, 60, '#7FA58F', { 'stroke-width': 4, transform: 'rotate(14 366 860)' });
    P(root, 'M300,860 L380,860 L370,930 L310,930 Z', C.slate, { 'stroke-width': 5 });
    // desk + monitor (right edge)
    R(root, 1500, 720, 60, 210, 4, C.slate, { 'stroke-width': 5 });
    R(root, 1720, 730, 210, 200, 4, C.greyBlue, { 'stroke-width': 5 });
    [790, 860].forEach((y) => R(root, 1790, y, 70, 12, 6, C.slate, { 'stroke-width': 4 }));
    R(root, 1470, 700, 470, 32, 6, '#8796A6');
    R(root, 1694, 650, 26, 52, 2, C.slate, { 'stroke-width': 5 });
    R(root, 1640, 690, 134, 14, 6, C.slate, { 'stroke-width': 5 });
    R(root, 1560, 450, 300, 200, 12, C.slate);
    R(root, 1578, 468, 264, 164, 4, '#AFC0D0', { 'stroke-width': 4 });
    let s = ''; for (let r = 0; r < 5; r++) s += `M1592,${488 + r * 28} h${236 - (r * 37) % 90} `;
    mk('path', { d: s, stroke: C.greyBlue, 'stroke-width': 8, 'stroke-linecap': 'round' }, root);
    R(root, 1836, 470, 44, 44, 3, '#E9E3B4', { 'stroke-width': 4, transform: 'rotate(8 1858 492)' });
    R(root, 1500, 652, 54, 50, 8, '#F4F7FA', { 'stroke-width': 5 });
    P(root, 'M1554,664 q22,0 22,14 q0,14 -22,14', 'none', { 'stroke-width': 5 });
    return { el, parts: { groundY: 930 } };
  }

  function bgSplit(leftText, rightText) {
    leftText = leftText == null ? 'Mùi lúc nhỏ' : leftText;
    rightText = rightText == null ? 'Mùi người lớn' : rightText;
    const el = G(), root = G(el);
    // left: warm xom
    const lw = G(root);
    R(lw, 0, 0, 960, 1080, 0, skyGrad(lw, 'propsSplitSky', C.warmSkyTop, C.warmSkyLow), NOSTROKE);
    sun(lw, 760, 230, 64);
    cloud(lw, 430, 190, 0.6);
    house(lw, 360, 560, 640, 820, { wall: '#FBE8C4', door: C.teal, doorAt: 0.78, win: [], rh: 70 });
    picketFence(lw, 250, 760, 744, 820);
    R(lw, -10, 818, 980, 270, 0, C.lane, { 'stroke-width': 0 });
    R(lw, -10, 816, 980, 20, 0, C.curb, { 'stroke-width': 5 });
    R(lw, 90, 810, 110, 30, 6, '#B8A48A', { 'stroke-width': 5 });
    almondTree(lw, 145, 825, 0.9);
    plant(lw, 860, 820, 'flower', 0.8);
    [[300, 990, 20, C.red], [700, 1040, -30, C.orange]].forEach((l) => leafOnGround(lw, ...l));
    // right: cool office
    const rw = G(root);
    officeScene(rw, 960, 1920);
    blinds(rw, 1080, 190, 300, 250);
    wallClock(rw, 1700, 250, 58);
    R(rw, 1540, 720, 400, 30, 6, '#8796A6'); R(rw, 1580, 750, 50, 180, 4, C.slate, { 'stroke-width': 5 });
    R(rw, 1660, 520, 220, 150, 10, C.slate); R(rw, 1676, 536, 188, 118, 4, '#AFC0D0', { 'stroke-width': 4 });
    R(rw, 1756, 670, 30, 52, 2, C.slate, { 'stroke-width': 5 });
    const glowLeft = mk('rect', { x: 0, y: 0, width: 960, height: 1080, fill: '#FFD25A', opacity: 0 }, root);
    const dimRight = mk('rect', { x: 960, y: 0, width: 960, height: 1080, fill: '#22304A', opacity: 0 }, root);
    R(root, 955, -10, 10, 1100, 0, '#fff', { 'stroke-width': 4 });
    const labels = [[leftText, 'warm', 480], [rightText, 'cool', 1440]].map(([t, st, x]) => {
      const tg = tag(t, st); tg.el.setAttribute('transform', `translate(${x},84)`); root.appendChild(tg.el); return tg.el;
    });
    return { el, parts: { left: lw, right: rw, glowLeft, dimRight, labels, groundY: 930 } };
  }

  function endCard() {
    const el = G(), root = G(el);
    R(root, 0, 0, 1920, 1080, 0, '#fff', NOSTROKE);
    const cx = 1240;
    const title = T(root, 'Mọt', cx, 420, { size: 160 });
    P(root, `M${cx - 130},532 Q${cx},506 ${cx + 130},528`, 'none', { stroke: C.orange, 'stroke-width': 12 });
    const sub = T(root, 'người đọc sách hộ bạn', cx, 612, { fam: 'b', w: 700, size: 54 });
    const credit = T(root, 'Hình minh họa tự vẽ · Giọng đọc tổng hợp', cx, 708, { fam: 'b', w: 500, size: 28, fill: C.grey });
    [[1600, 300, C.sun], [880, 300, C.teal], [1640, 760, C.orange], [860, 780, C.leaf]].forEach(([x, y, c], i) =>
      i % 2 ? Ci(root, x, y, 12, c, { 'stroke-width': 4 }) : R(root, x - 12, y - 12, 24, 24, 4, c, { 'stroke-width': 4, transform: `rotate(20 ${x} ${y})` }));
    return { el, parts: { title, sub, credit, mascotArea: { x0: 200, x1: 700 } } };
  }

  window.PROPS = {
    palette: C,
    ticket, book1, book2, scale, chapters, album, strikePage, markPage, checklist, icecream,
    bubble, sign, tag, bigText, bgXom, bgOffice, bgSplit, endCard,
    util: { measure },
  };
})();
