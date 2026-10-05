"""Hindi YouTube Short: 'Free AI Voiceover website | No app needed'. Narrator (hm_omega) + a sample made on the website (hf_alpha)."""
import json, re, subprocess, numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
CLI = '/home/user/Claude-code/tool-sites/creator/promo/reels-16-hinglish/source/g2p_cli.mjs'
k = Kokoro('kokoro-v1.0.int8.onnx', 'voices-v1.0.bin'); SR = 24000
UI = dict(manual='Purana tareeka:', turn=('Ye try karo', 'bhai.'), cta='Free hai. Login nahi.', bio='link bio mein')
SAMPLE_TEXT = 'नमस्ते! मैं Creator Bench की AI आवाज़ हूँ। आपकी script, मेरी आवाज़, बिल्कुल free।'
PLAN = [('hook', 'Voiceover के लिए कोई app download मत करो। ये website free में AI आवाज़ बना देती है।', .35),
        ('pain', 'Mic खरीदो, शांत कमरा ढूँढो, या हर महीने paid app के पैसे दो।', .3),
        ('turn', 'इसकी जगह ये try करो।', .25),
        ('demo', 'Script लिखो, Hindi या English आवाज़ चुनो, और generate दबाओ। सुनो।', .45),
        ('sample', SAMPLE_TEXT, .35),
        ('demo', 'MP3 या WAV download करो। Monetised videos में भी use कर सकते हो।', .45),
        ('cta', 'बिल्कुल free है, कोई login नहीं। Link bio में है।', .4)]
G = json.loads(subprocess.run(['node', CLI], input=json.dumps([p[1] for p in PLAN]).encode(), capture_output=True, check=True).stdout)
def trim(a): nz = np.where(np.abs(a) > .01)[0]; return a[max(0, nz[0] - 400): nz[-1] + 900] if len(nz) else a
def words_of(text, t0, t1):
    ws = text.split(); wt = [len(re.sub(r'\W', '', w)) + 1.5 for w in ws]; tot = sum(wt); out = []; c = t0
    for w, x in zip(ws, wt): d = (t1 - t0) * x / tot; out.append(dict(w=w, s=round(c, 3), e=round(c + d, 3))); c += d
    return out
smp, ssr = sf.read('sample.wav', dtype='float32'); assert ssr == SR
t = 0; chunks = []; lines = []
for (key, text, gap), g in zip(PLAN, G):
    chunks.append(np.zeros(int(gap * SR))); t += gap
    a = trim(smp) if key == 'sample' else trim(k.create(g['ph'], voice='hm_omega', speed=1.1, is_phonemes=True)[0])
    cap = g['roman'][0].upper() + g['roman'][1:]
    lines.append(dict(key=key, text=cap, t0=round(t, 3), t1=round(t + len(a) / SR, 3), words=words_of(cap, t, t + len(a) / SR))); chunks.append(a); t += len(a) / SR
chunks.append(np.zeros(int(1.6 * SR))); t += 1.6
sf.write('out/ai-voiceover/vo.wav', np.concatenate(chunks), SR)
sc = {}
for l in lines:
    key = 'demo' if l['key'] == 'sample' else l['key']; sc.setdefault(key, [l['t0'], l['t1']]); sc[key][1] = l['t1']
sc['hook'][0] = 0; sc['pain'][0] = sc['hook'][1] + .05; sc['turn'] = [sc['pain'][1] + .1, sc['demo'][0] - .05]; sc['demo'][1] = sc['cta'][0] - .1; sc['cta'][1] = t
for l in lines:   # the sample is shown as captions like the narration
    if l['key'] == 'sample': l['key'] = 'demo'; l['sample'] = True
meta = dict(id='ai-voiceover', name='AI Voiceover', sub='Hindi aur English, free', hook=('Free AI Voiceover', 'website!'),
            pain=[('Mic kharido', 'Rs 3,000'), ('Shaant kamra dhoondho', 'uff'), ('Paid AI app', 'Rs 999/mo')], ui=UI, lines=lines, scenes=sc, dur=round(t, 3))
json.dump(meta, open('out/ai-voiceover/meta.json', 'w'), indent=1, ensure_ascii=False)
print(json.dumps({l['key'] + ('*' if l.get('sample') else ''): [l['t0'], l['t1']] for l in lines}), sc, round(t, 1))
