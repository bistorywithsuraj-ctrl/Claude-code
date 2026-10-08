"""Hinglish narration for the trend-format reel (structure mirrors the viral tutorial). Voice: Kokoro hm_psi (lively Hindi male)."""
import json, re, subprocess, numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
CLI = '/home/user/Claude-code/tool-sites/creator/promo/reels-16-hinglish/source/g2p_cli.mjs'
LINES = [  # (beat, text, gap before)
 ('hook',   'ये नया trend internet पर छा गया है, और इस free website से आप भी किसी भी footage में cartoon characters डाल सकते हो।', .15),
 ('open',   'बस creatorbenchtool dot com खोलो, और अपना clip डालो।', .25),
 ('pick',   'कोई भी character चुनो, या comment में TREND लिखो, मैं link भेज दूँगा।', .2),
 ('drag',   'अब उन्हें अपनी footage पर drag करो।', .2),
 ('how',    'पर ये असली जैसे कैसे दिखेंगे?', .3),
 ('match',  'Color match बढ़ाओ, ताकि वो footage का माहौल पकड़ लें।', .2),
 ('better', 'और भी अच्छा कर सकते हैं!', .25),
 ('shadow', 'पैरों के नीचे soft shadow डालो, और थोड़ा सा blur।', .2),
 ('ground', 'आखिर में, feet in the grass on करो, और effect एकदम real लगेगा।', .25),
]
k = Kokoro('kokoro-v1.0.int8.onnx', 'voices-v1.0.bin'); SR = 24000
G = json.loads(subprocess.run(['node', CLI], input=json.dumps([l[1] for l in LINES]).encode(), capture_output=True, check=True).stdout)
def trim(a): nz = np.where(np.abs(a) > .01)[0]; return a[max(0, nz[0] - 300): nz[-1] + 700] if len(nz) else a
def words_of(text, t0, t1):
    ws = text.split(); wt = [len(re.sub(r'\W', '', w)) + 1.2 for w in ws]; tot = sum(wt); out = []; c = t0
    for w, x in zip(ws, wt): d = (t1 - t0) * x / tot; out.append(dict(w=w, s=round(c, 3), e=round(c + d, 3))); c += d
    return out
t = 0; chunks = []; lines = []
for (beat, text, gap), g in zip(LINES, G):
    chunks.append(np.zeros(int(gap * SR))); t += gap
    a = trim(k.create(g['ph'].replace('dˈɔʈ', 'ɖɔʈ'), voice='hm_psi', speed=1.18, is_phonemes=True)[0])
    cap = g['roman'].replace('creatorbenchtool dot com', 'creatorbenchtool.com')
    lines.append(dict(beat=beat, text=cap, t0=round(t, 3), t1=round(t + len(a) / SR, 3), words=words_of(cap, t, t + len(a) / SR))); chunks.append(a); t += len(a) / SR
chunks.append(np.zeros(int(1.8 * SR))); t += 1.8
sf.write('vo.wav', np.concatenate(chunks), SR)
json.dump(dict(lines=lines, dur=round(t, 3)), open('meta.json', 'w'), indent=1, ensure_ascii=False)
for l in lines: print(f"{l['beat']:7s} {l['t0']:5.2f}-{l['t1']:5.2f}  {l['text']}")
print('total', round(t, 2))
