import json, numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
k = Kokoro('kokoro-v1.0.int8.onnx', 'voices-v1.0.bin'); VOICE = 'am_michael'
SC = json.load(open('script.json')); SR = 24000
LEAD, GAP, TAIL = 0.5, 0.32, 0.7
t = 0.0; full = []; meta = []
for s in SC:
    start = t; lines = []; cur = LEAD; chunks = [np.zeros(int(LEAD * SR))]
    for i, line in enumerate(s['lines']):
        a, sr = k.create(line, voice=VOICE, speed=1.0, lang='en-us'); assert sr == SR
        # trim leading/trailing near-silence
        nz = np.where(np.abs(a) > 0.01)[0]; a = a[max(0, nz[0] - 600): nz[-1] + 1200] if len(nz) else a
        lines.append(dict(text=line, t0=round(start + cur, 3), t1=round(start + cur + len(a) / SR, 3)))
        chunks += [a]; cur += len(a) / SR
        if i < len(s['lines']) - 1: chunks.append(np.zeros(int(GAP * SR))); cur += GAP
    chunks.append(np.zeros(int(TAIL * SR))); cur += TAIL
    seg = np.concatenate(chunks); full.append(seg)
    meta.append(dict(**s, t0=round(start, 3), dur=round(len(seg) / SR, 3), vo=lines)); t += len(seg) / SR
sf.write('vo.wav', np.concatenate(full), SR)
json.dump(meta, open('scenes.json', 'w'), indent=1)
for m in meta: print(f"{m['id']:18s} {m['t0']:7.2f} {m['dur']:6.2f}")
print('total', round(t, 2))
