/* Creator Bench Hindi text -> phonemes for the Kokoro Hindi voices (espeak-style IPA).
   Devanagari is read with schwa-deletion rules; romanised Hinglish words are transliterated first.
   Exposes self.HindiG2P = { devanagari(text) -> string, toDevanagari(romanWord) -> string, isHindiRoman(word) -> bool } */
(function (root) {
  const C = { 'क': 'k', 'ख': 'kʰ', 'ग': 'ɡ', 'घ': 'ɡʰ', 'ङ': 'ŋ', 'च': 'c', 'छ': 'cʰ', 'ज': 'ɟ', 'झ': 'ɟʰ', 'ञ': 'ɲ', 'ट': 'ʈ', 'ठ': 'ʈʰ', 'ड': 'ɖ', 'ढ': 'ɖʰ', 'ण': 'ɳ',
    'त': 't', 'थ': 'tʰ', 'द': 'd', 'ध': 'dʰ', 'न': 'n', 'प': 'p', 'फ': 'pʰ', 'ब': 'b', 'भ': 'bʰ', 'म': 'm', 'य': 'j', 'र': 'ɾ', 'ल': 'l', 'ळ': 'l', 'व': 'ʋ', 'श': 'ʃ', 'ष': 'ʂ', 'स': 's', 'ह': 'h' };
  const NUKTA = { 'क': 'q', 'ख': 'x', 'ग': 'ɣ', 'ज': 'z', 'फ': 'f', 'ड': 'ɽ', 'ढ': 'ɽʰ' };
  const PRE = { 'क़': 'q', 'ख़': 'x', 'ग़': 'ɣ', 'ज़': 'z', 'फ़': 'f', 'ड़': 'ɽ', 'ढ़': 'ɽʰ' };   // precomposed forms
  const V = { 'अ': 'ə', 'आ': 'aː', 'इ': 'ɪ', 'ई': 'iː', 'उ': 'ʊ', 'ऊ': 'uː', 'ऋ': 'ɾɪ', 'ए': 'eː', 'ऐ': 'ɛː', 'ओ': 'oː', 'औ': 'ɔː', 'ऑ': 'ɔ', 'ऍ': 'ɛ' };
  const M = { 'ा': 'aː', 'ि': 'ɪ', 'ी': 'iː', 'ु': 'ʊ', 'ू': 'uː', 'ृ': 'ɾɪ', 'े': 'eː', 'ै': 'ɛː', 'ो': 'oː', 'ौ': 'ɔː', 'ॉ': 'ɔ', 'ॅ': 'ɛ' };
  const VIRAMA = '्', NUK = '़', ANUS = 'ं', CHANDRA = 'ँ', VISARGA = 'ः';
  const LONG = /ː|ɛ|ɔ/;

  function units(word) {   // -> [{c, v, nas, h}] one per akshara
    const u = [], ch = [...word.normalize('NFC')];
    for (let i = 0; i < ch.length; i++) {
      const x = ch[i], last = u[u.length - 1];
      if (PRE[x]) u.push({ c: PRE[x], v: 'ə', inh: true });
      else if (C[x]) { if (ch[i + 1] === NUK) { u.push({ c: NUKTA[x] || C[x], v: 'ə', inh: true }); i++; } else u.push({ c: C[x], v: 'ə', inh: true }); }
      else if (V[x]) u.push({ c: '', v: V[x], inh: false });
      else if (M[x] && last) { last.v = M[x]; last.inh = false; }
      else if (x === VIRAMA && last) { last.v = ''; last.inh = false; }
      else if ((x === ANUS || x === CHANDRA) && last) last.nas = x;
      else if (x === VISARGA && last) last.h = true;
    }
    // ज्ञ is said "gy"; क्ष stays kʂ -> kʃ in everyday Hindi
    for (let i = 0; i + 1 < u.length; i++) {
      if (u[i].c === 'ɟ' && u[i].v === '' && u[i + 1].c === 'ɲ') { u[i].c = 'ɡ'; u[i + 1].c = 'j'; }
      if (u[i].c === 'k' && u[i].v === '' && u[i + 1].c === 'ʂ') u[i + 1].c = 'ʃ';
    }
    return u;
  }
  function deleteSchwas(u) {
    const has = k => u[k] && u[k].v !== '';
    const n = u.length;
    // word-final inherent schwa goes, unless the word is a single akshara or ends in a cluster like मित्र
    if (n > 1 && u[n - 1].inh && u[n - 1].c && !(n > 2 && u[n - 2].v === '' && /[ɾjʋ]/.test(u[n - 1].c))) u[n - 1].v = '';
    // medial: V C ə C V -> V C C V, right to left
    for (let i = n - 2; i >= 1; i--) {
      const x = u[i]; if (!x.inh || !x.c || x.nas) continue;
      if (has(i - 1) && u[i + 1].c && has(i + 1)) x.v = '';
    }
    return u;
  }
  function homorganic(c) { return /^[kɡ]/.test(c) ? 'ŋ' : /^[cɟ]/.test(c) ? 'ɲ' : /^[ʈɖ]/.test(c) ? 'ɳ' : /^[pbm]/.test(c) ? 'm' : /^[tdnslɾ]/.test(c) ? 'n' : ''; }
  function nasal(v) { if (!v) return v; const b = v[0] === 'ɪ' ? 'i' : v[0] === 'ʊ' ? 'u' : v[0]; return b + '\u0303' + v.slice(1); }
  function wordPhones(word) {
    const u = deleteSchwas(units(word)), seg = [];   // seg: [{p, vowel}]
    for (let i = 0; i < u.length; i++) {
      const x = u[i];
      if (x.c) seg.push({ p: x.c });
      if (x.v) {
        let v = x.v; const next = u[i + 1];
        if (i === u.length - 1 && u.length > 1) v = v === 'iː' ? 'i' : v === 'uː' ? 'u' : v;   // final ई/ऊ are short
        const hom = x.nas === ANUS && v === 'ə' && next && next.c ? homorganic(next.c) : '';   // संगीत səŋɡiːt, ठंडा ʈʰəɳɖaː; elsewhere a nasal vowel (हिंदी hĩdi)
        if (hom) { seg.push({ p: v, vowel: true }); seg.push({ p: hom }); }
        else seg.push({ p: x.nas ? nasal(v) : v, vowel: true });
      } else if (x.nas) seg.push({ p: 'n' });
      if (x.h) seg.push({ p: 'h' });
    }
    for (let i = seg.length - 1; i > 0; i--) {   // doubled consonants: बच्चा bəcːaː, अच्छा əcʰcʰaː
      const a = seg[i - 1], c = seg[i]; if (a.vowel || c.vowel) continue;
      if (a.p === c.p) { a.p += 'ː'; seg.splice(i, 1); } else if (a.p + 'ʰ' === c.p) a.p = c.p;
    }
    // stress: first heavy non-final syllable (long vowel or closed), else the first syllable
    const nuc = seg.map((s, i) => s.vowel ? i : -1).filter(i => i >= 0);
    if (nuc.length > 1) {
      let pick = nuc[0];
      for (let k = 0; k < nuc.length - 1; k++) {
        const i = nuc[k], closed = seg[i + 1] && !seg[i + 1].vowel && seg[i + 2] && !seg[i + 2].vowel;
        if (LONG.test(seg[i].p) || closed) { pick = i; break; }
        if (k === nuc.length - 2 && LONG.test(seg[nuc[k + 1]].p)) pick = nuc[k + 1];   // only light syllables before a long final: nəhˈĩː
      }
      if (seg[pick].p === 'ə') seg[pick].p = 'ʌ';
      seg[pick].p = 'ˈ' + seg[pick].p;   // eSpeak/Kokoro put the stress mark right before the vowel: dˈoːstõ
    }
    return seg.map(s => s.p).join('');
  }
  const DEVA = /[ऀ-ॿ]/;
  function devanagari(text) {   // Hindi words -> phonemes; anything else is passed through untouched
    return text.replace(/[।॥]/g, '.').replace(/[ऀ-ॿ]+/g, w => DEVA.test(w) ? wordPhones(w) : w);
  }

  // ---- romanised Hinglish ----
  const LEX = { hai: 'है', hain: 'हैं', ho: 'हो', tha: 'था', thi: 'थी', the: 'थे', main: 'मैं', mai: 'मैं', mein: 'में', me: 'में', hum: 'हम', tum: 'तुम', aap: 'आप', ap: 'आप', yeh: 'यह', ye: 'ये', woh: 'वो', wo: 'वो', vo: 'वो',
    kya: 'क्या', kyu: 'क्यों', kyun: 'क्यों', kyon: 'क्यों', kaise: 'कैसे', kaisa: 'कैसा', kahan: 'कहाँ', kab: 'कब', kaun: 'कौन', kitna: 'कितना', kitne: 'कितने', kuch: 'कुछ', sab: 'सब', bhi: 'भी', hi: 'ही', to: 'तो', na: 'ना', nahi: 'नहीं', nahin: 'नहीं',
    ka: 'का', ki: 'की', ke: 'के', ko: 'को', se: 'से', par: 'पर', pe: 'पे', aur: 'और', ya: 'या', lekin: 'लेकिन', magar: 'मगर', agar: 'अगर', jab: 'जब', tab: 'तब', ab: 'अब', abhi: 'अभी', phir: 'फिर', fir: 'फिर', bas: 'बस', sirf: 'सिर्फ़',
    bahut: 'बहुत', bohot: 'बहुत', bohut: 'बहुत', accha: 'अच्छा', acha: 'अच्छा', achha: 'अच्छा', bura: 'बुरा', naya: 'नया', nayi: 'नई', purana: 'पुराना', bada: 'बड़ा', badi: 'बड़ी', chhota: 'छोटा', chota: 'छोटा', jaldi: 'जल्दी', sasta: 'सस्ता', mehnga: 'महँगा',
    paisa: 'पैसा', paise: 'पैसे', mat: 'मत', do: 'दो', karo: 'करो', karna: 'करना', karte: 'करते', karta: 'करता', karti: 'करती', kar: 'कर', banao: 'बनाओ', banana: 'बनाना', banata: 'बनाता', banati: 'बनाती', banate: 'बनाते', bana: 'बना', deti: 'देती', deta: 'देता', dete: 'देते', de: 'दे', dena: 'देना',
    lo: 'लो', le: 'ले', lena: 'लेना', jao: 'जाओ', jaata: 'जाता', jata: 'जाता', jati: 'जाती', jaate: 'जाते', jayega: 'जाएगा', jaayega: 'जाएगा', hoga: 'होगा', hogi: 'होगी', hota: 'होता', hoti: 'होती', hote: 'होते', raha: 'रहा', rahi: 'रही', rahe: 'रहे', gaya: 'गया', gayi: 'गई', gaye: 'गए',
    dekho: 'देखो', dekhiye: 'देखिए', dekh: 'देख', suno: 'सुनो', likho: 'लिखो', likhiye: 'लिखिए', likh: 'लिख', bolo: 'बोलो', bol: 'बोल', chahiye: 'चाहिए', chahte: 'चाहते', sakte: 'सकते', sakta: 'सकता', sakti: 'सकती', milta: 'मिलता', milti: 'मिलती', milega: 'मिलेगा', milegi: 'मिलेगी',
    apna: 'अपना', apni: 'अपनी', apne: 'अपने', mera: 'मेरा', meri: 'मेरी', mere: 'मेरे', tera: 'तेरा', teri: 'तेरी', hamara: 'हमारा', tumhara: 'तुम्हारा', aapka: 'आपका', aapki: 'आपकी', aapke: 'आपके', iska: 'इसका', iski: 'इसकी', iske: 'इसके', isse: 'इससे', isme: 'इसमें', ismein: 'इसमें', uska: 'उसका',
    doston: 'दोस्तों', dosto: 'दोस्तो', dost: 'दोस्त', bhai: 'भाई', log: 'लोग', logo: 'लोगों', logon: 'लोगों', namaste: 'नमस्ते', shukriya: 'शुक्रिया', dhanyavaad: 'धन्यवाद', haan: 'हाँ', han: 'हाँ', ji: 'जी', aaj: 'आज', kal: 'कल', din: 'दिन', raat: 'रात', saal: 'साल', minute: 'मिनट', ghanta: 'घंटा',
    ek: 'एक', teen: 'तीन', char: 'चार', chaar: 'चार', paanch: 'पाँच', panch: 'पाँच', das: 'दस', sau: 'सौ', hazaar: 'हज़ार', hazar: 'हज़ार', lakh: 'लाख', crore: 'करोड़', karod: 'करोड़', rupaye: 'रुपये', rupay: 'रुपये',
    muft: 'मुफ़्त', bilkul: 'बिल्कुल', zaroor: 'ज़रूर', jaroor: 'ज़रूर', sach: 'सच', jhooth: 'झूठ', kaam: 'काम', baat: 'बात', cheez: 'चीज़', chiz: 'चीज़', duniya: 'दुनिया', zindagi: 'ज़िंदगी', awaaz: 'आवाज़', awaz: 'आवाज़', aawaz: 'आवाज़', wala: 'वाला', wali: 'वाली', wale: 'वाले', vala: 'वाला', vali: 'वाली',
    sabse: 'सबसे', pehle: 'पहले', pahle: 'पहले', baad: 'बाद', saath: 'साथ', sath: 'साथ', bina: 'बिना', liye: 'लिए', liya: 'लिया', diya: 'दिया', kiya: 'किया', yahan: 'यहाँ', wahan: 'वहाँ', andar: 'अंदर', bahar: 'बाहर', upar: 'ऊपर', neeche: 'नीचे', jaise: 'जैसे', aisa: 'ऐसा', aise: 'ऐसे', waisa: 'वैसा',
    bataiye: 'बताइए', batao: 'बताओ', kahani: 'कहानी', kahaniyan: 'कहानियाँ', karenge: 'करेंगे', karein: 'करें', karen: 'करें', dijiye: 'दीजिए', kijiye: 'कीजिए', chuniye: 'चुनिए', sochiye: 'सोचिए', samjho: 'समझो', samajh: 'समझ', video: null };
  const ENG = new Set(('website websites free voice voiceover video videos reel reels short shorts app apps tool tools online offline script scripts caption captions subtitle subtitles phone mobile laptop computer page image images photo photos ' +
    'data beta meta camera edit editing editor editors download upload link button time line done note notes quote write site sites state stage huge cute mute vote base case home name game same make take like share comment ' +
    'india media drama idea area extra ultra quota pasta insta delta vista agenda banana china protein pizza yoga sofa visa cinema formula camera aroma panorama ' +
    'one gone none bone tone zone alone online engine machine magazine routine').split(' '));
  const HINDI_END = /(aa|ii|oo|na|ne|ni|ta|ti|te|ga|gi|ge|oge|enge|ega|egi|iye|iya|kar|wala|wali|wale|aon|aan)$/;
  const ENG_SHAPE = /(tion|sion|ing|ness|ment|able|ible|ful|ous|ive|ize|ise|ght|ph|th$|ck|x|w[aeiou]|[^aeiou][aeiou](te|ne|ge|de|ke|pe|be|ve|me)$)/;
  function isHindiRoman(w) { const k = w.toLowerCase(); if (LEX[k]) return true; if (ENG.has(k)) return false;
    return k.length > 3 && HINDI_END.test(k) && (!ENG_SHAPE.test(k) || /(aa|ee|oo)[a-z]?e$|[^aeiou]{2}e$|oge$|enge$/.test(k)); }
  // rough Roman -> Devanagari for words not in the lexicon
  const RC = [['chh', 'छ'], ['kh', 'ख'], ['gh', 'घ'], ['ch', 'च'], ['jh', 'झ'], ['th', 'थ'], ['dh', 'ध'], ['ph', 'फ'], ['bh', 'भ'], ['sh', 'श'], ['k', 'क'], ['q', 'क़'], ['g', 'ग'], ['j', 'ज'], ['z', 'ज़'], ['t', 'त'], ['d', 'द'],
    ['n', 'न'], ['p', 'प'], ['f', 'फ़'], ['b', 'ब'], ['m', 'म'], ['y', 'य'], ['r', 'र'], ['l', 'ल'], ['v', 'व'], ['w', 'व'], ['s', 'स'], ['h', 'ह'], ['c', 'क'], ['x', 'क्स']];
  const RV = [['aa', 'आ', 'ा'], ['ai', 'ऐ', 'ै'], ['au', 'औ', 'ौ'], ['ee', 'ई', 'ी'], ['ii', 'ई', 'ी'], ['oo', 'ऊ', 'ू'], ['a', 'अ', ''], ['i', 'इ', 'ि'], ['u', 'उ', 'ु'], ['e', 'ए', 'े'], ['o', 'ओ', 'ो']];
  function toDevanagari(w) {
    const k = w.toLowerCase(); if (LEX[k]) return LEX[k];
    let s = k, out = '', prevC = false, lastV = '';
    while (s) {
      const v = RV.find(([r]) => s.startsWith(r));
      if (v) { let [r, ind, mat] = v; const rest = s.slice(r.length), end = !rest;
        if (r === 'a' && prevC && (end || /^[aeiou]/.test(rest))) mat = 'ा';   // kya, jaoge
        if (r === 'i' && end && prevC) mat = 'ी';
        out += prevC ? mat : ind; s = rest; prevC = false; lastV = r; continue; }
      if (s === 'n' && out && !prevC && /^(o|ei|ai|aa|ee|e)$/.test(lastV)) { out += ANUS; break; }   // baaton, mein, hain: final n is nasal
      const c = RC.find(([r]) => s.startsWith(r));
      if (c) { if (prevC) out += VIRAMA; out += c[1]; s = s.slice(c[0].length); prevC = true; continue; }
      s = s.slice(1);
    }
    return out;
  }
  // ---- Devanagari -> casual Hinglish spelling (for captions) ----
  const RO_C = { 'क': 'k', 'ख': 'kh', 'ग': 'g', 'घ': 'gh', 'ङ': 'n', 'च': 'ch', 'छ': 'chh', 'ज': 'j', 'झ': 'jh', 'ञ': 'n', 'ट': 't', 'ठ': 'th', 'ड': 'd', 'ढ': 'dh', 'ण': 'n', 'त': 't', 'थ': 'th', 'द': 'd', 'ध': 'dh', 'न': 'n',
    'प': 'p', 'फ': 'ph', 'ब': 'b', 'भ': 'bh', 'म': 'm', 'य': 'y', 'र': 'r', 'ल': 'l', 'ळ': 'l', 'व': 'v', 'श': 'sh', 'ष': 'sh', 'स': 's', 'ह': 'h' };
  const RO_N = { 'क': 'k', 'ख': 'kh', 'ग': 'g', 'ज': 'z', 'फ': 'f', 'ड': 'r', 'ढ': 'rh' }, RO_PRE = { 'क़': 'k', 'ख़': 'kh', 'ग़': 'g', 'ज़': 'z', 'फ़': 'f', 'ड़': 'r', 'ढ़': 'rh' };
  const RO_V = { 'अ': 'a', 'आ': 'aa', 'इ': 'i', 'ई': 'ee', 'उ': 'u', 'ऊ': 'oo', 'ऋ': 'ri', 'ए': 'e', 'ऐ': 'ai', 'ओ': 'o', 'औ': 'au', 'ऑ': 'o', 'ऍ': 'e' };
  const RO_M = { 'ा': 'aa', 'ि': 'i', 'ी': 'ee', 'ु': 'u', 'ू': 'oo', 'ृ': 'ri', 'े': 'e', 'ै': 'ai', 'ो': 'o', 'ौ': 'au', 'ॉ': 'o', 'ॅ': 'e' };
  const RO_WORD = { 'है': 'hai', 'हैं': 'hain', 'में': 'mein', 'मैं': 'main', 'नहीं': 'nahi', 'यह': 'yeh', 'वह': 'woh', 'और': 'aur', 'क्या': 'kya', 'हूँ': 'hoon', 'हूं': 'hoon', 'क्यों': 'kyun', 'कहाँ': 'kahan', 'यहाँ': 'yahan', 'वहाँ': 'wahan', 'हाँ': 'haan', 'हां': 'haan', 'बहुत': 'bahut', 'एक': 'ek', 'वीडियो': 'video', 'डाउनलोड': 'download', 'अपलोड': 'upload', 'स्क्रिप्ट': 'script', 'वॉइसओवर': 'voiceover', 'वेबसाइट': 'website',
    'फ्री': 'free', 'फ़्री': 'free', 'कैप्शन': 'caption', 'कैप्शंस': 'captions', 'चैनल': 'channel', 'सब्सक्राइब': 'subscribe', 'लाइक': 'like', 'कमेंट': 'comment', 'शेयर': 'share', 'फ़ोन': 'phone', 'फोन': 'phone', 'मोबाइल': 'mobile', 'ऐप': 'app',
    'रील': 'reel', 'रील्स': 'reels', 'टूल': 'tool', 'टूल्स': 'tools', 'ऑनलाइन': 'online', 'यूट्यूब': 'YouTube', 'इंस्टाग्राम': 'Instagram', 'थंबनेल': 'thumbnail', 'एडिट': 'edit', 'एडिटिंग': 'editing', 'कंटेंट': 'content', 'क्रिएटर': 'creator', 'क्रिएटर्स': 'creators' };
  function romanWord(word) {
    word = word.normalize('NFC'); if (RO_WORD[word]) return RO_WORD[word];
    const u = [], ch = [...word];
    for (let i = 0; i < ch.length; i++) {
      const x = ch[i], last = u[u.length - 1];
      if (RO_PRE[x]) u.push({ c: RO_PRE[x], v: 'a', inh: true });
      else if (RO_C[x]) { if (ch[i + 1] === NUK) { u.push({ c: RO_N[x] || RO_C[x], v: 'a', inh: true }); i++; } else u.push({ c: RO_C[x], v: 'a', inh: true }); }
      else if (RO_V[x]) u.push({ c: '', v: RO_V[x], inh: false });
      else if (RO_M[x] && last) { last.v = RO_M[x]; last.inh = false; }
      else if (x === VIRAMA && last) { last.v = ''; last.inh = false; }
      else if ((x === ANUS || x === CHANDRA) && last) last.nas = true;
      else if (x === VISARGA && last) last.h = true;
    }
    deleteSchwas(u);
    let out = '';
    u.forEach((x, i) => { let v = x.v; const fin = i === u.length - 1, prev = u[i - 1];
      if (!x.c && prev && prev.v && /(i|ee|aa|a|o|oo|u)$/.test(prev.v) && /^(e|ee)$/.test(v)) v = 'y' + v;   // लिखिए likhiye, जाए jaaye
      if (fin && v === 'aa') v = 'a'; if (fin && v === 'ee') v = 'i';   // karna, hindi
      out += x.c + v + (x.nas ? 'n' : '') + (x.h ? 'h' : ''); });
    return out.replace(/chchh?/g, 'cch');   // अच्छा accha, बच्चा baccha
  }
  function toRoman(text) { return text.replace(/[।॥]/g, '.').replace(/[\u0900-\u097F]+/g, romanWord); }
  // English phonemes (eSpeak 'en') -> Indian English, which the Hindi voices say naturally
  const INDIAN = [[/əʊ|oʊ/g, 'oː'], [/eɪ/g, 'eː'], [/ɜː|ɚ/g, 'əɾ'], [/ɑː/g, 'aː'], [/ɹ/g, 'ɾ'], [/θ/g, 'tʰ'], [/ð/g, 'd'], [/[wv]/g, 'ʋ'], [/æ/g, 'ɛ'], [/ɒ/g, 'ɔ'], [/t(?!ʃ)/g, 'ʈ'], [/d(?!ʒ)/g, 'ɖ'], [/ɐ/g, 'ə'], [/ᵻ/g, 'ɪ'], [/ə(?=ˈ|$| )/g, 'ə']];
  function indianEnglish(ph) { return INDIAN.reduce((x, [a, b]) => x.replace(a, b), ph); }
  root.HindiG2P = { devanagari, toDevanagari, toRoman, isHindiRoman, wordPhones, indianEnglish };
})(typeof self !== 'undefined' ? self : globalThis);
