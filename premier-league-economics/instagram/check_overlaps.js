const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1350 } });
  await p.goto('file://' + process.argv[2] + '/carousel.html'); await p.evaluate(() => document.fonts.ready);
  const out = await p.evaluate(() => {
    const res = [];
    document.querySelectorAll('section.slide').forEach(sec => {
      const S = sec.getBoundingClientRect();
      const els = [...sec.querySelectorAll('h1,h2,p,.kicker,.cut,.cap,.note,.torn,.src,.foot,.top,.pen,.num,.label,.rule,.paper,[class=ser]')]
        .filter(e => !e.closest('.cut') || e.classList.contains('cut'));
      const boxes = els.map(e => {
        // text boxes: use range rects to get tight text extent
        let r = e.getBoundingClientRect();
        const isText = /^(H1|H2|P)$/.test(e.tagName) || /kicker|cap|src|pen|label|ser/.test(e.className);
        if (isText) { const rg = document.createRange(); rg.selectNodeContents(e); const rs = [...rg.getClientRects()].filter(q => q.width > 1);
          if (rs.length) { const L = Math.min(...rs.map(q => q.left)), T = Math.min(...rs.map(q => q.top)), R = Math.max(...rs.map(q => q.right)), B2 = Math.max(...rs.map(q => q.bottom)); r = { left: L, top: T, right: R, bottom: B2, width: R - L }; } }
        return { e, name: e.tagName.toLowerCase() + (e.className ? '.' + String(e.className).split(' ')[0] : '') + ' "' + (e.textContent || e.getAttribute('src') || '').trim().slice(0, 24) + '"', r };
      }).filter(x => x.r.width > 0);
      for (let i = 0; i < boxes.length; i++) for (let j = i + 1; j < boxes.length; j++) {
        const A = boxes[i], B = boxes[j];
        if (A.e.contains(B.e) || B.e.contains(A.e)) continue;
        const x = Math.min(A.r.right, B.r.right) - Math.max(A.r.left, B.r.left);
        const y = Math.min(A.r.bottom, B.r.bottom) - Math.max(A.r.top, B.r.top);
        if (x > 4 && y > 4) res.push(`${sec.id}: ${A.name}  X  ${B.name}  (${Math.round(x)}x${Math.round(y)})`);
      }
      boxes.filter(A => !A.e.classList.contains('torn')).forEach(A => { const r = A.r; if (r.left < S.left + 40 || r.right > S.right - 40 || r.top < S.top + 40 || r.bottom > S.bottom - 40) res.push(`${sec.id}: ${A.name} crosses frame`); });
    });
    return res;
  });
  console.log(out.join('\n') || 'no overlaps'); await b.close();
})();
