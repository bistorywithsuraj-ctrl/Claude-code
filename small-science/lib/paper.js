// Paper-world helpers shared by Small Science episodes (extracted from the Greenback cold open).
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const lerp = (a, b, p) => a + (b - a) * p;
const inv = (a, b, x) => clamp((x - a) / (b - a));
const E = {
  outExpo: p => p >= 1 ? 1 : 1 - Math.pow(2, -10 * p),
  inOutCubic: p => p < .5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2,
  outBack: p => { const c1 = 1.5, c3 = c1 + 1; return 1 + c3 * Math.pow(p - 1, 3) + c1 * Math.pow(p - 1, 2); },
  inCubic: p => p * p * p, outCubic: p => 1 - Math.pow(1 - p, 3),
};
const P = (t, a, b, e = E.outExpo) => e(inv(a, b, t));
function rng(seed) { let s = seed >>> 0; return () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; }
const font = (s, w = 800, f = 'IT', st = '') => `${st} ${w} ${s}px ${f}`.trim();
// stop-motion wobble: stepped at 12 fps like hand-animated paper
const wob = (t, seed, amt = 1) => { const q = Math.floor(t * 12); const r = rng(seed * 997 + q); return (r() - .5) * amt; };

// ------------------------------------------------------------ assets
const IMG = {};
function loadImg(key, src) { return new Promise(res => { const i = new Image(); i.onload = () => { IMG[key] = i; res(); }; i.onerror = () => res(); i.src = src; }); }
const LOGOS = { f1: '#E10600', ferrari: '#D40000', mclaren: '#FF8000', redbull: '#DB0A40', astonmartin: '#00665E',
  renault: '#1A1A1A', cadillac: '#1A1A1A', audi: '#1A1A1A', honda: '#E40521', netflix: '#E50914', dhl: '#D40511', shell: '#DD1D21' };
const PHOTOS = ['claire_williams', 'frank_williams', 'williams_car_2020', 'monza_2020', 'interview_claire_2020'];
const tinted = {};
function tint(key, color, w) {  // rasterise an SVG logo in brand color
  const id = key + color + w; if (tinted[id]) return tinted[id];
  const im = IMG['logo_' + key]; if (!im) return null;
  const h = w * im.height / im.width; const c = document.createElement('canvas'); c.width = w; c.height = h;
  const g = c.getContext('2d'); g.drawImage(im, 0, 0, w, h); g.globalCompositeOperation = 'source-in'; g.fillStyle = color; g.fillRect(0, 0, w, h);
  return (tinted[id] = c);
}

// ------------------------------------------------------------ paper textures
function makeTex(w, h, seed, base, fibers = 900, grainAmt = 22) {
  const c = document.createElement('canvas'); c.width = w; c.height = h; const g = c.getContext('2d'); const r = rng(seed);
  g.fillStyle = base; g.fillRect(0, 0, w, h);
  const id = g.getImageData(0, 0, w, h);
  for (let i = 0; i < id.data.length; i += 4) { const n = (r() - .5) * grainAmt; id.data[i] += n; id.data[i + 1] += n; id.data[i + 2] += n; }
  g.putImageData(id, 0, 0);
  g.globalAlpha = .05; g.strokeStyle = '#000'; g.lineWidth = .7;
  for (let i = 0; i < fibers; i++) { const x = r() * w, y = r() * h, a = r() * 6.28, l = 6 + r() * 26;
    g.beginPath(); g.moveTo(x, y); g.quadraticCurveTo(x + Math.cos(a + .6) * l * .5, y + Math.sin(a + .6) * l * .5, x + Math.cos(a) * l, y + Math.sin(a) * l); g.stroke(); }
  // blotches
  g.globalAlpha = .012; for (let i = 0; i < 14; i++) { g.fillStyle = r() > .5 ? '#000' : '#fff'; g.beginPath(); g.arc(r() * w, r() * h, 40 + r() * 160, 0, 7); g.fill(); }
  return c;
}
let TEX = {};
const grainFrames = [];
function buildTextures() {
  TEX = {};
  TEX.bg = makeTex(W, H, 11, C.paper, 2600, 16);
  TEX.card = makeTex(900, 700, 21, C.green, 700, 20);
  TEX.white = makeTex(900, 900, 31, C.white, 700, 12);
  const r = rng(5);
  for (let k = 0; k < 6; k++) { const c = document.createElement('canvas'); c.width = 960; c.height = 540; const g = c.getContext('2d');
    const id = g.createImageData(960, 540); for (let i = 0; i < id.data.length; i += 4) { const v = r() * 255; id.data[i] = id.data[i + 1] = id.data[i + 2] = v; id.data[i + 3] = 255; }
    g.putImageData(id, 0, 0); grainFrames.push(c); }
}

// ------------------------------------------------------------ primitives
function tornPath(x, y, w, h, seed, rough = 5) {  // slightly irregular paper rectangle
  const r = rng(seed); ctx.beginPath();
  const pts = []; const step = 28;
  for (let i = 0; i <= w; i += step) pts.push([x + i, y + (r() - .5) * rough]);
  for (let i = 0; i <= h; i += step) pts.push([x + w + (r() - .5) * rough, y + i]);
  for (let i = w; i >= 0; i -= step) pts.push([x + i, y + h + (r() - .5) * rough]);
  for (let i = h; i >= 0; i -= step) pts.push([x + (r() - .5) * rough, y + i]);
  pts.forEach((p, i) => i ? ctx.lineTo(...p) : ctx.moveTo(...p)); ctx.closePath();
}
function shadow(on, blur = 24, oy = 10, a = .28) { if (on) { ctx.shadowColor = `rgba(0,0,0,${a})`; ctx.shadowBlur = blur; ctx.shadowOffsetY = oy; ctx.shadowOffsetX = 3; } else { ctx.shadowColor = 'transparent'; ctx.shadowBlur = 0; ctx.shadowOffsetY = 0; ctx.shadowOffsetX = 0; } }

// place a paper element: slide/drop-in with overshoot, rotation, stepped wobble
function place(t, t0, x, y, rot, seed, draw, opt = {}) {
  const o = Object.assign({ from: 'up', dur: .6, out: 1e9, outTo: 'down' }, opt);
  const p = E.outBack(inv(t0, t0 + o.dur, t)); const q = E.inCubic(inv(o.out, o.out + .45, t));
  if (p <= 0 || q >= 1) return;
  const dist = 1300; const dir = { up: [0, -1], down: [0, 1], left: [-1, 0], right: [1, 0] };
  const [fx, fy] = dir[o.from]; const [tx, ty] = dir[o.outTo];
  ctx.save();
  ctx.translate(x + fx * dist * (1 - p) + tx * dist * q + wob(t, seed, 1.2), y + fy * dist * (1 - p) + ty * dist * q + wob(t, seed + 1, 1.2));
  ctx.rotate((rot + (1 - p) * 8 * (fx || fy) + wob(t, seed + 2, .25)) * Math.PI / 180);
  draw(); ctx.restore();
}

// green card with white type
function greenCard(w, h, lines, seed, opt = {}) {
  ctx.save(); shadow(true); tornPath(-w / 2, -h / 2, w, h, seed, 4); ctx.fillStyle = C.green; ctx.fill(); shadow(false);
  ctx.clip(); ctx.drawImage(TEX.card, -w / 2, -h / 2, w, h); ctx.restore();
  let y = -h / 2 + (opt.pad || 60);
  lines.forEach(l => {
    ctx.font = font(l.size, l.w || 800, l.fam || 'IT', l.style || ''); ctx.fillStyle = l.color || C.white; ctx.textAlign = 'left';
    if (l.track) ctx.letterSpacing = l.track + 'px';
    y += l.size * (l.lh || 1.0); ctx.fillText(l.text, -w / 2 + (opt.pad || 60), y); ctx.letterSpacing = '0px'; y += l.gap || 14;
  });
}
function whitePaper(w, h, seed) { shadow(true); tornPath(-w / 2, -h / 2, w, h, seed, 3); ctx.fillStyle = C.white; ctx.fill(); shadow(false);
  ctx.save(); ctx.clip(); ctx.drawImage(TEX.white, -w / 2, -h / 2, w, h); ctx.restore(); }
function tape(x, y, w, rot) { ctx.save(); ctx.translate(x, y); ctx.rotate(rot * Math.PI / 180); ctx.fillStyle = 'rgba(246,214,70,.75)'; ctx.fillRect(-w / 2, -14, w, 28); ctx.restore(); }

// highlighter behind text, sweeping left→right
function hiText(str, x, y, size, t, t0, opt = {}) {
  const o = Object.assign({ w: 800, fam: 'IT', style: '', color: C.ink, hi: C.yellow, align: 'left', dur: .5 }, opt);
  ctx.save(); ctx.font = font(size, o.w, o.fam, o.style); const tw = ctx.measureText(str).width;
  const x0 = o.align === 'center' ? x - tw / 2 : x;
  const p = E.outCubic(inv(t0, t0 + o.dur, t));
  if (p > 0) { ctx.globalCompositeOperation = 'multiply'; ctx.fillStyle = o.hi; const r = rng(Math.floor(x));
    ctx.beginPath(); ctx.moveTo(x0 - 10, y - size * .78); ctx.lineTo(x0 - 10 + (tw + 20) * p, y - size * .82 + r() * 4);
    ctx.lineTo(x0 - 10 + (tw + 20) * p, y + size * .18); ctx.lineTo(x0 - 12, y + size * .2); ctx.closePath(); ctx.fill(); ctx.globalCompositeOperation = 'source-over'; }
  ctx.fillStyle = o.color; ctx.fillText(str, x0, y); ctx.restore(); return tw;
}

// narration caption (stands in for VO until voice is recorded)
const CAPS = [];
const cap = (a, b, text, hi = []) => CAPS.push({ a, b, text, hi });
function captions(t) {
  const c = CAPS.find(c => t >= c.a && t < c.b); if (!c) return;
  const p = inv(c.a, c.a + .25, t) * (1 - inv(c.b - .25, c.b, t));
  ctx.save(); ctx.globalAlpha = p; ctx.font = font(34, 700); ctx.textAlign = 'left';
  const words = c.text.split(' '); const lines = [[]]; let lw = 0; const maxW = 1400;
  words.forEach(wd => { const w = ctx.measureText(wd + ' ').width; if (lw + w > maxW) { lines.push([]); lw = 0; } lines[lines.length - 1].push(wd); lw += w; });
  const lh = 46, y0 = H - 70 - (lines.length - 1) * lh;
  lines.forEach((ln, li) => { const s = ln.join(' '); const tw = ctx.measureText(s).width; let x = W / 2 - tw / 2; const y = y0 + li * lh;
    ctx.fillStyle = 'rgba(22,22,22,.88)'; ctx.fillRect(x - 18, y - 36, tw + 36, 48);
    ln.forEach(wd => { const clean = wd.replace(/[.,!?—:;"]/g, ''); ctx.fillStyle = c.hi.includes(clean) ? C.yellow : C.white; ctx.fillText(wd, x, y); x += ctx.measureText(wd + ' ').width; }); });
  ctx.restore();
}


// scene registry
const SCENES = []; const scene = (a, b, fn) => SCENES.push({ a, b, fn });
