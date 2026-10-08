"""Soundtrack: original lo-fi trend beat (synthesised), narration on top with ducking, whooshes on cuts, pop on the comment bubble."""
import json, numpy as np, soundfile as sf, subprocess, sys
SR = 48000; M = json.load(open('meta.json')); N = int(M['dur'] * SR); rng = np.random.default_rng(7)
tt = lambda d: np.arange(int(d * SR)) / SR
def lp(x, k):
    c = np.cumsum(np.concatenate([[0.], x])); y = (c[k:] - c[:-k]) / k; p = len(x) - len(y); return np.concatenate([np.full(p // 2, y[0]), y, np.full(p - p // 2, y[-1])])
hp = lambda x: np.diff(x, prepend=0)
mus = np.zeros(N); sfx = np.zeros(N)
def add(buf, t, sig, g=1.):
    s = int(t * SR)
    if 0 <= s < N: sig = sig[:N - s]; buf[s:s + len(sig)] += sig * g
note = lambda m: 440 * 2 ** ((m - 69) / 12)
kick = lambda: (lambda t: np.sin(2 * np.pi * (48 * t + 120 / 25 * (1 - np.exp(-t * 25)))) * np.exp(-t * 8))(tt(.4))
snare = lambda: (lambda t: hp(lp(rng.standard_normal(len(t)), 2)) * np.exp(-t * 22) * .8 + np.sin(2 * np.pi * 190 * t) * np.exp(-t * 30) * .3)(tt(.25))
hat = lambda: (lambda t: hp(hp(rng.standard_normal(len(t)))) * np.exp(-t * 90) * .25)(tt(.05))
def keys(ms, d):   # soft electric-piano chord
    t = tt(d); return sum(np.sin(2 * np.pi * note(m) * t) * (1 + .3 * np.sin(2 * np.pi * 5 * t)) * np.exp(-t * 1.6) for m in ms) * .12
bass = lambda m, d: (lambda t: np.tanh(1.5 * np.sin(2 * np.pi * note(m) * t)) * np.minimum(1, t * 40) * np.exp(-t * 2.2) * .35)(tt(d))
BPM = 98; bt = 60 / BPM; prog = [([60, 64, 67, 71], 48), ([57, 60, 64, 67], 45), ([62, 65, 69, 72], 50), ([55, 59, 62, 65], 43)]
x = 0.; b = 0
while x < M['dur']:
    ch, root = prog[(b // 4) % 4]
    if b % 4 == 0: add(mus, x, keys(ch, bt * 4), .9); add(mus, x, bass(root, bt * 2)); add(mus, x + bt * 2.5, bass(root + 7, bt * 1.5))
    add(mus, x, kick(), .9 if b % 2 == 0 else .0); add(mus, x + bt * .75, kick(), .5 if b % 4 == 2 else 0)
    if b % 2 == 1: add(mus, x, snare(), .55)
    for h in range(2): add(mus, x + h * bt / 2, hat(), .8 if h else .5)
    x += bt; b += 1
def whoosh(d=.35): t = tt(d); n = rng.standard_normal(len(t)); m = t / d; return (lp(n, 25) * (1 - m) + lp(n, 4) * m) * np.sin(np.pi * m) ** 2 * 1.2
pop = lambda: (lambda t: np.sin(2 * np.pi * np.cumsum(500 + 900 * np.sqrt(t / .12)) / SR) * np.exp(-t * 26))(tt(.14))
ding = lambda: (lambda t: (np.sin(2 * np.pi * 1318 * t) + .5 * np.sin(2 * np.pi * 1975 * t)) * np.exp(-t * 6) * .4)(tt(.8))
L = {l['beat']: l for l in M['lines']}
for k in ['open', 'pick', 'drag', 'how', 'better', 'shadow']: add(sfx, L[k]['t0'] - .45, whoosh(), .5)
w = next((x for x in L['pick']['words'] if 'TREND' in x['w'].upper()), None); add(sfx, (w['s'] if w else L['pick']['t0'] + 1.5) - .1, pop(), .6); add(sfx, (w['s'] if w else 0) - .05, ding(), .35)
add(sfx, L['ground']['t1'] + .4, ding(), .4)
subprocess.run([sys.argv[1], '-v', 'error', '-y', '-i', 'vo.wav', '-ar', str(SR), '-ac', '1', 'vo48.wav'], check=True)
vo, _ = sf.read('vo48.wav'); vo = np.pad(vo, (0, max(0, N - len(vo))))[:N]
env = lp(np.abs(vo), int(SR * .12)); duck = 1 - .55 * np.clip(env / (env.max() * .25 + 1e-9), 0, 1)
out = mus * .3 * duck + sfx * .6 + vo * 1.0; out = out / max(1, np.abs(out).max() / .95)
fo = np.ones(N); n = int(.3 * SR); fo[-n:] = np.linspace(1, 0, n); sf.write('mix.wav', np.stack([out * fo, out * fo], 1), SR); print('mixed', round(N / SR, 2), 's')
