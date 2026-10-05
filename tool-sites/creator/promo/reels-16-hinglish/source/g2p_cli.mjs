// stdin: JSON array of lines -> stdout: JSON [{ph, roman}] using the site's Hindi reader and eSpeak English
import fs from 'fs';
const KK = process.env.PHONEMIZER || '/tmp/claude-0/-home-user-Claude-code/b8e4b5b5-0315-5db7-bd49-a5dfd041999d/scratchpad/kk/package/dist/phonemizer.js';
await import(new URL('../../../shared/vendor/hindi-g2p.js', import.meta.url).pathname);
const { phonemize } = await import(KK); const G = globalThis.HindiG2P;
async function ph(text) {
  const toks = text.replace(/।/g, '.').match(/[ऀ-ॿ]+|[A-Za-z']+|\d+(?:[.,]\d+)*|[,.!?;:—…-]|\s+/g) || [], out = []; let eng = [];
  const flush = async () => { if (!eng.length) return; out.push(G.indianEnglish((await phonemize(eng.join(' '), 'en')).join(' '))); eng = []; };
  for (const t of toks) {
    if (/^\s+$/.test(t)) continue;
    if (/[ऀ-ॿ]/.test(t)) { await flush(); out.push(G.devanagari(t)); }
    else if (/^[A-Za-z']+$/.test(t) && G.isHindiRoman(t)) { await flush(); out.push(G.wordPhones(G.toDevanagari(t))); }
    else if (/^[A-Za-z'\d]/.test(t)) eng.push(t);
    else { await flush(); out.push(t); }
  }
  await flush(); return out.join(' ').replace(/\s+([,.!?;:])/g, '$1');
}
const lines = JSON.parse(fs.readFileSync(0, 'utf8')), res = [];
for (const l of lines) res.push({ ph: await ph(l), roman: G.toRoman(l) });
process.stdout.write(JSON.stringify(res));
