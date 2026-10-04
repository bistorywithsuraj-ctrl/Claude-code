import json, re, os, numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
from reels import R, TURN, CTA
k = Kokoro('kokoro-v1.0.int8.onnx', 'voices-v1.0.bin'); SR = 24000; SPEED = 1.08
def say(text):
    a, sr = k.create(text, voice='am_michael', speed=SPEED, lang='en-us'); nz = np.where(np.abs(a) > .01)[0]
    return a[max(0, nz[0] - 400): nz[-1] + 900] if len(nz) else a
def words_of(text, t0, t1):  # approximate word timing by letter share (TTS speaks at a steady rate)
    ws = text.replace('S R T', 'SRT').replace('P N G', 'PNG').replace('S V G', 'SVG').split(); wt = [len(re.sub(r'\W', '', w)) + 1.5 for w in ws]; tot = sum(wt); out = []; c = t0
    for w, x in zip(ws, wt): d = (t1 - t0) * x / tot; out.append(dict(w=w, s=round(c, 3), e=round(c + d, 3))); c += d
    return out
for r in R:
    d = f"out/{r['id']}"; os.makedirs(d, exist_ok=True)
    plan = [('hook', r['vo'][0], .35), ('pain', r['vo'][1], .3), ('turn', TURN, .25), ('demo', r['vo'][2], .45), ('demo', r['vo'][3], .3), ('cta', CTA, .4)]
    t = 0; chunks = []; lines = []
    for key, text, gap in plan:
        chunks.append(np.zeros(int(gap * SR))); t += gap; a = say(text); lines.append(dict(key=key, text=text, t0=round(t, 3), t1=round(t + len(a) / SR, 3), words=words_of(text, t, t + len(a) / SR))); chunks.append(a); t += len(a) / SR
    chunks.append(np.zeros(int(1.6 * SR))); t += 1.6
    sf.write(f'{d}/vo.wav', np.concatenate(chunks), SR)
    sc = {}
    for l in lines: sc.setdefault(l['key'], [l['t0'], l['t1']]); sc[l['key']][1] = l['t1']
    sc['hook'][0] = 0; sc['pain'][0] = sc['hook'][1] + .05; sc['turn'] = [sc['pain'][1] + .1, sc['demo'][0] - .05]; sc['demo'][1] = sc['cta'][0] - .1; sc['cta'][1] = t
    json.dump(dict(id=r['id'], name=r['name'], sub=r['sub'], hook=r['hook'], pain=r['pain'], lines=lines, scenes=sc, dur=round(t, 3)), open(f'{d}/meta.json', 'w'), indent=1)
    print(f"{r['id']:18s} {t:5.1f}s  demo {sc['demo'][1] - sc['demo'][0]:4.1f}s")
