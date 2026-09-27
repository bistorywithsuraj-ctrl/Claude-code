// Shared characters & annotation helpers for Small Science.
// ---------------------------------------------------------------- mascot
// talking: mouth flaps; point: arm angle (radians) or null; blink every ~3 s
function pip(x, y, s, t, opt = {}) {
  const o = Object.assign({ talking: false, point: null, seed: 1 }, opt);
  ctx.save(); ctx.translate(x + wob(t, o.seed, 1.5), y + wob(t, o.seed + 1, 1.5)); ctx.scale(s, s);
  ctx.rotate(wob(t, o.seed + 2, .012));
  const outline = (fn) => { ctx.save(); shadow(true, 14, 6, .25); ctx.lineJoin = 'round'; ctx.strokeStyle = C.white; ctx.lineWidth = 10; fn(); ctx.stroke(); ctx.fill(); shadow(false); ctx.restore(); };
  // body: green paper coat
  ctx.fillStyle = C.green; outline(() => { ctx.beginPath(); ctx.moveTo(-70, 60); ctx.quadraticCurveTo(-80, 200, -75, 250); ctx.lineTo(75, 250); ctx.quadraticCurveTo(80, 200, 70, 60); ctx.quadraticCurveTo(0, 30, -70, 60); ctx.closePath(); });
  ctx.fillStyle = C.yellow; ctx.beginPath(); ctx.moveTo(-18, 58); ctx.lineTo(0, 110); ctx.lineTo(18, 58); ctx.closePath(); ctx.fill();   // collar/tie
  ctx.fillStyle = 'rgba(0,0,0,.15)'; ctx.fillRect(-4, 110, 8, 140);
  // pointing arm
  if (o.point !== null) {
    ctx.save(); ctx.translate(60, 95); ctx.rotate(o.point + Math.sin(t * 5) * .04);
    ctx.fillStyle = C.green; outline(() => { ctx.beginPath(); ctx.roundRect(0, -16, 120, 32, 16); });
    ctx.fillStyle = C.skin; outline(() => { ctx.beginPath(); ctx.arc(128, 0, 18, 0, 7); }); ctx.restore();
  }
  // head
  ctx.fillStyle = C.skin; outline(() => { ctx.beginPath(); ctx.ellipse(0, -20, 78, 84, 0, 0, 7); });
  // hair: a single swooping paper tuft
  ctx.fillStyle = '#2B2622'; ctx.beginPath(); ctx.moveTo(-78, -30); ctx.quadraticCurveTo(-80, -110, 0, -106); ctx.quadraticCurveTo(70, -110, 80, -40);
  ctx.quadraticCurveTo(40, -80, -10, -70); ctx.quadraticCurveTo(-40, -60, -78, -30); ctx.fill();
  ctx.beginPath(); ctx.moveTo(10, -104); ctx.quadraticCurveTo(40, -150, 70, -130); ctx.quadraticCurveTo(40, -125, 26, -100); ctx.fill();
  // glasses
  ctx.strokeStyle = C.ink; ctx.lineWidth = 6; ctx.fillStyle = 'rgba(255,255,255,.35)';
  [-30, 30].forEach(ex => { ctx.beginPath(); ctx.arc(ex, -18, 26, 0, 7); ctx.fill(); ctx.stroke(); });
  ctx.beginPath(); ctx.moveTo(-4, -18); ctx.lineTo(4, -18); ctx.stroke();
  // eyes (blink)
  const blink = (t % 3.1) < .12;
  ctx.fillStyle = C.ink; [-30, 30].forEach(ex => { if (blink) ctx.fillRect(ex - 9, -19, 18, 4); else { ctx.beginPath(); ctx.arc(ex + 3, -16, 7, 0, 7); ctx.fill(); } });
  // cheeks
  ctx.fillStyle = 'rgba(214,69,61,.3)'; [-52, 52].forEach(cx => { ctx.beginPath(); ctx.arc(cx, 16, 12, 0, 7); ctx.fill(); });
  // mouth
  const open = o.talking ? Math.abs(Math.sin(t * 13)) * (0.5 + .5 * Math.abs(Math.sin(t * 3.7))) : 0;
  ctx.fillStyle = '#5A1E1A'; ctx.beginPath(); ctx.ellipse(0, 30, 16, 3 + open * 13, 0, 0, 7); ctx.fill();
  ctx.restore();
}

function paperDot(x, y, r, fill) { ctx.beginPath(); ctx.arc(x, y, r, 0, 7); ctx.fillStyle = C.white; ctx.fill(); ctx.beginPath(); ctx.arc(x, y, r - 3, 0, 7); ctx.fillStyle = fill; ctx.fill(); }
function label(text, x, y, t, t0, opt = {}) {  // green card label that pops in
  const p = E.outBack(inv(t0, t0 + .45, t)); if (p <= 0) return;
  ctx.save(); ctx.translate(x, y); ctx.rotate((opt.rot || 0) * Math.PI / 180); ctx.scale(p, p);
  ctx.font = font(opt.size || 30, 800); const w = ctx.measureText(text).width + 50;
  greenCard(w, (opt.size || 30) + 40, [{ text, size: opt.size || 30, w: 800 }], opt.seed || 7, { pad: 25 });
  ctx.restore();
}
function arrow(x1, y1, x2, y2, p) { ctx.save(); ctx.strokeStyle = C.ink; ctx.lineWidth = 5; ctx.lineCap = 'round'; ctx.setLineDash([12, 10]);
  const x = lerp(x1, x2, p), y = lerp(y1, y2, p); ctx.beginPath(); ctx.moveTo(x1, y1); ctx.lineTo(x, y); ctx.stroke(); ctx.setLineDash([]);
  if (p > .95) { const a = Math.atan2(y2 - y1, x2 - x1); ctx.beginPath(); ctx.moveTo(x2, y2); ctx.lineTo(x2 - Math.cos(a - .5) * 22, y2 - Math.sin(a - .5) * 22); ctx.moveTo(x2, y2); ctx.lineTo(x2 - Math.cos(a + .5) * 22, y2 - Math.sin(a + .5) * 22); ctx.stroke(); }
  ctx.restore(); }

