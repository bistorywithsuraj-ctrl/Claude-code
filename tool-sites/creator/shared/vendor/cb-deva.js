/* Creator Bench: Hindi (Devanagari) text on canvas.
   Adds a matching Devanagari font to every canvas font: serif faces get Tiro Devanagari Hindi, others get Mukta.
   The fonts are OFL licensed and served by Google Fonts; with unicode-range only the Devanagari files load.
   CBDeva.ready() resolves when they are loaded. */
(function () {
  const link = document.createElement('link'); link.rel = 'stylesheet';
  link.href = 'https://fonts.googleapis.com/css2?family=Mukta:wght@600;800&family=Tiro+Devanagari+Hindi&display=swap';
  document.head.appendChild(link);
  const SERIF = /serif"?\s*$|Playfair|Abril|Baskerville|Old Standard|Georgia|Times|Fraunces|Lora|Merriweather|Unifraktur/i;
  const d = Object.getOwnPropertyDescriptor(CanvasRenderingContext2D.prototype, 'font');
  const add = v => {
    if (/Devanagari|Mukta/.test(v)) return v;
    const extra = SERIF.test(v) && !/sans-serif\s*$/.test(v) ? '"Tiro Devanagari Hindi"' : 'Mukta';
    const m = v.match(/,\s*(serif|sans-serif|monospace|system-ui|cursive)\s*$/);   // keep the generic family last
    return m ? v.slice(0, m.index) + ', ' + extra + m[0] : v + ', ' + extra;
  };
  if (d && d.set) Object.defineProperty(CanvasRenderingContext2D.prototype, 'font', { configurable: true, get: d.get, set(v) { d.set.call(this, add(String(v))); } });
  const loads = () => Promise.all(['800 40px Mukta', '600 40px Mukta', '400 40px "Tiro Devanagari Hindi"'].map(f => document.fonts.load(f, 'हिंदी'))).catch(() => {});
  const css = new Promise(r => { link.onload = r; link.onerror = r; setTimeout(r, 4000); });
  const p = css.then(loads);
  p.then(() => window.dispatchEvent(new Event('cb-deva-fonts')));
  window.CBDeva = { ready: () => p, has: t => /[\u0900-\u097F]/.test(t || '') };
})();
