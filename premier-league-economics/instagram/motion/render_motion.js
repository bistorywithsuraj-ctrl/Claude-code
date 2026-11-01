// Motion-graphic carousel renderer for Greenback.
// Takes a static carousel.html, injects entrance animations, steps time
// deterministically, and writes one MP4 per slide (with a slice of the theme).
//
// usage: node render_motion.js <carousel_dir> [seconds=6] [fps=30]
// output: <carousel_dir>/motion/greenback_motion_0N.mp4
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path'), { execFileSync } = require('child_process');

const DIR = path.resolve(process.argv[2]);
const SECS = +(process.argv[3] || 6), FPS = +(process.argv[4] || 30);
const MUSIC = path.resolve(__dirname, '..', 'music', 'greenback_theme.m4a');
const OUT = path.join(DIR, 'motion'); fs.mkdirSync(OUT, { recursive: true });

const CSS = `
@keyframes gbRise   { from { opacity:0; translate:0 36px } to { opacity:1; translate:0 0 } }
@keyframes gbFade   { from { opacity:0 } to { opacity:1 } }
@keyframes gbDrop   { 0% { opacity:0; translate:0 -70px; scale:1.12 } 70% { opacity:1; translate:0 6px; scale:.99 } 100% { opacity:1; translate:0 0; scale:1 } }
@keyframes gbPop    { 0% { opacity:0; scale:.4 } 70% { opacity:1; scale:1.08 } 100% { opacity:1; scale:1 } }
@keyframes gbSlideL { from { opacity:0; translate:-80px 0 } to { opacity:1; translate:0 0 } }
@keyframes gbWipe   { from { clip-path: inset(-20% 100% -20% -5%) } to { clip-path: inset(-20% -5% -20% -5%) } }
@keyframes gbMark   { from { background-size: 0% 100% } to { background-size: 100% 100% } }
@keyframes gbGrow   { from { scale: 1 0 } to { scale: 1 1 } }
@keyframes gbDrift  { from { scale: 1 } to { scale: 1.035 } }
.hy { background: linear-gradient(var(--yellow), var(--yellow)) no-repeat 0 0 / 100% 100%; }
.gb-bar { transform-origin: 50% 100%; }
`;

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1350 } });
  await page.goto('file://' + path.join(DIR, 'carousel.html'));
  await page.addStyleTag({ content: CSS });
  await page.evaluate(() => document.fonts.ready);

  const nSlides = await page.evaluate(() => {
    const A = (el, name, delay, dur, ease = 'cubic-bezier(.2,.8,.2,1)') => {
      el.style.animation = `${name} ${dur}s ${ease} ${delay}s both`;
      el.dataset.gbDelay = delay;
    };
    const slides = [...document.querySelectorAll('section.slide')];
    slides.forEach(sec => {
      let t = 0.15;
      const step = (d = 0.22) => (t += d) - d;
      sec.querySelectorAll('.top').forEach(e => A(e, 'gbFade', 0, .5));
      sec.querySelectorAll('.kicker').forEach(e => A(e, 'gbSlideL', step(.2), .6));
      sec.querySelectorAll('h1, h2').forEach(e => A(e, 'gbRise', step(.35), .8));
      // marker highlights sweep after their headline lands
      sec.querySelectorAll('.hy').forEach(e => { const d = step(.3); e.style.animation = `gbMark .7s cubic-bezier(.6,0,.3,1) ${d}s both`; e.dataset.gbDelay = d; });
      sec.querySelectorAll('.rule').forEach(e => A(e, 'gbWipe', step(.15), .7));
      sec.querySelectorAll(':scope > div > .ser, .ser').forEach(e => { if (!e.style.animation) A(e, 'gbRise', step(.25), .8); });
      [...sec.querySelectorAll('p')].forEach(e => A(e, 'gbFade', step(.3), .7));
      // stickers (logos) pop, cutouts drop like paper
      sec.querySelectorAll('div.cut').forEach(e => A(e, 'gbPop', step(.25), .7, 'cubic-bezier(.3,1.4,.5,1)'));
      sec.querySelectorAll('img.cut').forEach(e => {
        const d = step(.25);
        e.style.animation = `gbDrop .8s cubic-bezier(.3,1.2,.5,1) ${d}s both, gbDrift ${6}s linear ${d + .8}s both`;
        e.dataset.gbDelay = d;
      });
      sec.querySelectorAll('.note, .torn, .paper').forEach(e => A(e, 'gbRise', step(.25), .7));
      // bar chart (slide 5): bars grow from the axis
      sec.querySelectorAll('div[style*="height:"][style*="background"]').forEach(e => {
        if (e.closest('.note') || e.classList.contains('cut')) return;
        const h = parseFloat((e.style.height || '0')); if (h < 10) return;
        e.classList.add('gb-bar'); A(e, 'gbGrow', step(.2), 1.0, 'cubic-bezier(.2,.9,.2,1)');
      });
      sec.querySelectorAll('.pen, .cap').forEach(e => A(e, 'gbWipe', step(.3), .9, 'cubic-bezier(.5,0,.3,1)'));
      sec.querySelectorAll('.src').forEach(e => A(e, 'gbFade', step(.2), .6));
      sec.querySelectorAll('.foot').forEach(e => A(e, 'gbFade', step(.1), .6));
      // anything still static (arrows, bar labels, axis labels) fades in, in reading order,
      // timed with whatever animated element sits nearest above it
      const S = sec.getBoundingClientRect();
      const animated = [...sec.querySelectorAll('[data-gb-delay]')];
      sec.querySelectorAll('div, span, img, svg').forEach(e => {
        if (e.closest('[data-gb-delay]') || e.querySelector('[data-gb-delay]') || e.classList.contains('frame')) return;
        const own = [...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim()) || /IMG|svg/i.test(e.tagName);
        if (!own) return;
        const r = e.getBoundingClientRect(); if (!r.width) return;
        let best = 0;
        animated.forEach(a => { const ar = a.getBoundingClientRect(); if (ar.top <= r.top + 5) best = Math.max(best, +a.dataset.gbDelay); });
        // bar-value labels wait for their bar
        const bar = e.parentElement && e.parentElement.querySelector('.gb-bar');
        A(e, 'gbFade', bar ? +bar.dataset.gbDelay + .6 : best + .25, .5);
      });
      // count-up numbers
      sec.querySelectorAll('.num').forEach(e => {
        const m = e.textContent.trim().match(/^([^\d]*)([\d.]+)(.*)$/); if (!m) return;
        e.dataset.pre = m[1]; e.dataset.val = m[2]; e.dataset.suf = m[3];
        e.dataset.dec = (m[2].split('.')[1] || '').length;
        const host = e.closest('[data-gb-delay]');
        e.dataset.start = ((host ? +host.dataset.gbDelay : t) + .15).toFixed(2);
      });
    });
    document.getAnimations().forEach(a => a.pause());
    return slides.length;
  });

  const setTime = async (sec, ms) => page.evaluate(([id, ms]) => {
    const s = document.getElementById(id);
    s.getAnimations({ subtree: true }).forEach(a => { a.currentTime = ms; });
    s.querySelectorAll('.num[data-val]').forEach(e => {
      const p = Math.min(1, Math.max(0, (ms / 1000 - +e.dataset.start) / 1.1));
      const k = 1 - Math.pow(1 - p, 3);
      e.textContent = e.dataset.pre + (+e.dataset.val * k).toFixed(+e.dataset.dec) + e.dataset.suf;
    });
  }, [sec, ms]);

  for (let i = 1; i <= nSlides; i++) {
    const id = 's' + i, frames = path.join(OUT, 'frames_' + i);
    fs.rmSync(frames, { recursive: true, force: true }); fs.mkdirSync(frames);
    const loc = page.locator('#' + id);
    await loc.scrollIntoViewIfNeeded();
    for (let f = 0; f < SECS * FPS; f++) {
      await setTime(id, (f / FPS) * 1000);
      await loc.screenshot({ path: path.join(frames, String(f).padStart(4, '0') + '.png') });
    }
    const out = path.join(OUT, `greenback_motion_0${i}.mp4`);
    const start = ((i - 1) * SECS).toFixed(2);
    execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-framerate', String(FPS), '-i', path.join(frames, '%04d.png'),
      '-ss', start, '-t', String(SECS), '-i', MUSIC,
      '-af', `afade=t=in:st=0:d=0.3,afade=t=out:st=${SECS - 0.5}:d=0.5`,
      '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '17', '-preset', 'medium',
      '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', out]);
    fs.rmSync(frames, { recursive: true, force: true });
    console.log('wrote', out);
  }
  await browser.close();
})();
