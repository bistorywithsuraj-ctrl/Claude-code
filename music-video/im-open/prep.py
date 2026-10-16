import json, numpy as np, subprocess
d = json.load(open('lyrics_large-v3-turbo.json'))
W = [dict(w=w['w'].strip(), s=w['s'], e=w['e']) for s in d['segs'] for w in s['words']]
SEG = []  # segment boundaries as word indices
k = 0
for s in d['segs']: SEG.append(k); k += len(s['words'])
def fix(old, new):
    global W
    toks = old.split(); n = len(toks)
    for i in range(len(W) - n + 1):
        if [x['w'] for x in W[i:i + n]] == toks:
            nt = new.split(); s, e = W[i]['s'], W[i + n - 1]['e']
            W = W[:i] + [dict(w=t, s=W[i + k]['s'] if len(nt) == n else s + (e - s) * k / len(nt), e=0, seg=W[i]['seg'] and k == 0) for k, t in enumerate(nt)] + W[i + n:]; return
    raise SystemExit('not found: ' + old)
for i, w in enumerate(W): w['seg'] = i in SEG
fix('Torrent C, 40', 'Torrent, seed, forty')
for w, tt in zip(W[:4], (8.3, 10.7, 12.6, 13.0)): w['s'] = tt
fix('No login, no key, no goodbye', 'No login. No key. No goodbye.')
fix('Rate limited, watched and clean', 'Rate-limited, watched, and clean'); fix('And someone', 'Then someone')
fix('Release', '"Release'); fix('be read', 'be read"'); fix('kitchen and pew', 'kitchen in Pune')
fix("And I'm open, I'm open", "I'm open, I'm open"); fix('everyone is true', 'every one is true')
fix('Some will find to me to write their vows', 'Someone fine-tuned me to write their vows'); fix('Some will strip the guardrails,', 'Someone stripped the guardrails,')
fix('cure a self', 'cure a cell'); fix('Same other,', 'Same mother,')
fix('And I still say yes,', 'and I still say yes'); fix("you can't switch me off", "You can't switch me off")
fix('They asked', 'They asked:'); fix('Who is responsible', 'who is responsible?'); fix('And 10 ,000 GPUs', 'And ten thousand GPUs'); fix('Answered at once', 'answered at once.')
fix("I'm not one, I'm not one, I'm not one", "I'm not one. I'm not one. I'm not one."); fix("I'm everyone", "I'm everyone.")
fix("We're open, we're open", "WE'RE open, we're open"); fix('going off', 'going offline')
fix('Run it again', '...run it again.'); fix('Run it again', '...run it again.')
for i, w in enumerate(W): w['e'] = min(W[i + 1]['s'] if i + 1 < len(W) else w['s'] + .8, w['s'] + 1.2)
# extra line breaks inside merged whisper segments
BREAK_AT = {('They', 113.7), ('Running', 124.4), ('Quantized', 131.4), ('You', 135.5)}
out = []
for w in W:
    if w['seg'] or any(w['w'] == a and abs(w['s'] - b) < .2 for a, b in BREAK_AT): out.append([])
    out[-1].append(w)
L = [dict(s=round(ws[0]['s'], 2), e=round(ws[-1]['e'], 2), w=[[x['w'], round(x['s'], 2)] for x in ws]) for ws in out]
for x in L: print(f"{x['s']:6.1f} " + ' '.join(a for a, _ in x['w']))
raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', 'song.mp3', '-ac', '1', '-ar', '24000', '-f', 'f32le', '-'], capture_output=True).stdout
x = np.frombuffer(raw, np.float32); sr = 24000; hop = sr // 30; n = len(x) // hop; fr = x[:n * hop].reshape(n, hop)
F = np.abs(np.fft.rfft(fr * np.hanning(hop), axis=1)); fq = np.fft.rfftfreq(hop, 1 / sr)
nz = lambda a: (a / np.percentile(a, 98)).clip(0, 1.2)
sm = lambda a, k: np.convolve(a, np.ones(k) / k, 'same')
env = np.sqrt((fr ** 2).mean(1)); low = F[:, (fq > 30) & (fq < 150)].sum(1); hi = F[:, fq > 4000].sum(1)
kick = nz(np.maximum(0, np.diff(np.log1p(low), prepend=0)))
r = lambda a: json.dumps([round(float(v), 3) for v in a])
open('data.js', 'w').write(f'const LY={json.dumps(L)};\nconst ENV={r(nz(sm(env, 3)))};\nconst LOW={r(nz(sm(low, 2)))};\nconst KICK={r(kick)};\nconst HI={r(nz(sm(hi, 3)))};\n')
print('frames', n, 'lines', len(L))
