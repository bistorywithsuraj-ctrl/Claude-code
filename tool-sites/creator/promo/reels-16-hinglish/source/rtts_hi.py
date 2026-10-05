"""Hindi voiceover + timing for the Hinglish reels. Phonemes come from the site's Hindi reader (g2p_cli.mjs)."""
import json, re, os, sys, subprocess, numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
from reels_hi import R, TURN, CTA, UI
CLI = os.environ.get('G2P_CLI', '/home/user/Claude-code/tool-sites/creator/promo/reels-16-hinglish/source/g2p_cli.mjs')
k = Kokoro('kokoro-v1.0.int8.onnx', 'voices-v1.0.bin'); SR = 24000; SPEED = 1.1; VOICE = os.environ.get('VOICE', 'hm_omega')
def g2p(lines): return json.loads(subprocess.run(['node', CLI], input=json.dumps(lines).encode(), capture_output=True, check=True).stdout)
def say(ph):
    a, sr = k.create(ph, voice=VOICE, speed=SPEED, is_phonemes=True); nz = np.where(np.abs(a) > .01)[0]
    return a[max(0, nz[0] - 400): nz[-1] + 900] if len(nz) else a
def words_of(text, t0, t1):  # word timing by letter share (TTS speaks at a steady rate)
    ws = text.split(); wt = [len(re.sub(r'\W', '', w)) + 1.5 for w in ws]; tot = sum(wt); out = []; c = t0
    for w, x in zip(ws, wt): d = (t1 - t0) * x / tot; out.append(dict(w=w, s=round(c, 3), e=round(c + d, 3))); c += d
    return out
only = sys.argv[1:]
for r in R:
    if only and r['id'] not in only: continue
    d = f"out/{r['id']}"; os.makedirs(d, exist_ok=True)
    plan = [('hook', r['vo'][0], .35), ('pain', r['vo'][1], .3), ('turn', TURN, .25), ('demo', r['vo'][2], .45), ('demo', r['vo'][3], .3), ('cta', CTA, .4)]
    G = g2p([p[1] for p in plan]); t = 0; chunks = []; lines = []
    for (key, text, gap), g in zip(plan, G):
        chunks.append(np.zeros(int(gap * SR))); t += gap; a = say(g['ph']); cap = g['roman'][0].upper() + g['roman'][1:]
        lines.append(dict(key=key, text=cap, t0=round(t, 3), t1=round(t + len(a) / SR, 3), words=words_of(cap, t, t + len(a) / SR))); chunks.append(a); t += len(a) / SR
    chunks.append(np.zeros(int(1.6 * SR))); t += 1.6
    sf.write(f'{d}/vo.wav', np.concatenate(chunks), SR)
    sc = {}
    for l in lines: sc.setdefault(l['key'], [l['t0'], l['t1']]); sc[l['key']][1] = l['t1']
    sc['hook'][0] = 0; sc['pain'][0] = sc['hook'][1] + .05; sc['turn'] = [sc['pain'][1] + .1, sc['demo'][0] - .05]; sc['demo'][1] = sc['cta'][0] - .1; sc['cta'][1] = t
    frames = json.load(open(f'{d}/cap.json'))['frames']
    json.dump(dict(id=r['id'], name=r['name'], sub=r['sub'], hook=r['hook'], pain=r['pain'], ui=UI, lines=lines, scenes=sc, dur=round(t, 3)), open(f'{d}/meta.json', 'w'), indent=1, ensure_ascii=False)
    print(f"{r['id']:18s} {t:5.1f}s  demo {sc['demo'][1] - sc['demo'][0]:4.1f}s (recorded {frames / 30:4.1f}s)", flush=True)
