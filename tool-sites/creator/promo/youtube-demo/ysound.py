import numpy as np, wave, json
SC = json.load(open('scenes.json')); EV = json.load(open('cap/events.json')); S = {s['id']: s for s in SC}
SR = 48000; DUR = SC[-1]['t0'] + SC[-1]['dur']; N = int(SR * (DUR + .1))
w = wave.open('vo48.wav'); vo = np.frombuffer(w.readframes(w.getnframes()), '<i2').astype(float) / 32768; vo = np.pad(vo, (0, max(0, N - len(vo))))[:N]
mus = np.zeros((N, 2)); sfx = np.zeros((N, 2)); rng = np.random.default_rng(5)
def add(buf, t, sig, g=1.0, pan=.5):
    s = int(t * SR)
    if s >= N or s < 0: return
    sig = sig[:N - s]
    if sig.ndim == 1: buf[s:s + len(sig), 0] += sig * g * (1 - pan) * 2 ** .5; buf[s:s + len(sig), 1] += sig * g * pan * 2 ** .5
    else: buf[s:s + len(sig)] += sig * g
tt = lambda d: np.arange(int(d * SR)) / SR
def lp(x, k):
    if k <= 1: return x
    c = np.cumsum(np.concatenate([[0.0], x])); y = (c[k:] - c[:-k]) / k; pad = len(x) - len(y); return np.concatenate([np.full(pad // 2, y[0]), y, np.full(pad - pad // 2, y[-1])])
hp = lambda x: np.diff(x, prepend=0)
note = lambda m: 440 * 2 ** ((m - 69) / 12)
def kick(g=1): t = tt(.4); return np.sin(2 * np.pi * (48 * t + 110 / 26 * (1 - np.exp(-t * 26)))) * np.exp(-t * 8) * g
def boom(): t = tt(2.4); return np.tanh(2.2 * np.sin(2 * np.pi * (36 * t + 150 / 18 * (1 - np.exp(-t * 18)))) * np.exp(-t * 1.5))
def snare(): t = tt(.22); return (hp(lp(rng.standard_normal(len(t)), 4)) * .8 + np.sin(2 * np.pi * 190 * t) * .4) * np.exp(-t * 22)
def hat(): t = tt(.05); return hp(hp(rng.standard_normal(len(t)))) * np.exp(-t * 90) * .3
def tick(f=2600, d=.035): t = tt(d); return (np.sin(2 * np.pi * f * t) * .6 + hp(rng.standard_normal(len(t))) * .3) * np.exp(-t * 140)
def key(): t = tt(.03); return (hp(lp(rng.standard_normal(len(t)), 2)) * .7 + np.sin(2 * np.pi * rng.uniform(1700, 2600) * t) * .25) * np.exp(-t * 220)
def click(): t = tt(.06); return np.sin(2 * np.pi * 1500 * t) * np.exp(-t * 90) + .5 * np.sin(2 * np.pi * 3100 * t) * np.exp(-t * 160)
def bubble(f0=500, f1=1300, d=.12): t = tt(d); f = f0 + (f1 - f0) * (t / d) ** .5; return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 28) * (1 - np.exp(-t * 900))
def whoosh(d=.5): t = tt(d); n = rng.standard_normal(len(t)); env = np.sin(np.pi * t / d) ** 2; m = t / d; return (lp(n, 30) * (1 - m) + lp(n, 4) * m) * env * 1.3
def scratch(d=.22): t = tt(d); return hp(lp(rng.standard_normal(len(t)), 3)) * np.abs(np.sin(2 * np.pi * 22 * t)) ** 2 * np.exp(-t * 4) * .9
def riser(d):
    t = tt(d); n = rng.standard_normal(len(t)); out = np.zeros_like(t); seg = len(t) // 12
    for i in range(12): a = i * seg; out[a:a + seg] = lp(n[a:a + seg], max(1, 40 - i * 3))
    return (out + np.sin(2 * np.pi * np.cumsum(200 + 900 * (t / d) ** 2) / SR) * .25) * (t / d) ** 2
def ding(): t = tt(1.4); return sum(np.sin(2 * np.pi * note(m) * t) * np.exp(-t * k) * g for m, k, g in ((88, 3, .5), (95, 4, .25), (100, 6, .12)))
def keys_chord(ms, d): t = tt(d); trem = 1 + .15 * np.sin(2 * np.pi * 4.5 * t); return sum((np.sin(2 * np.pi * note(m) * t) + .2 * np.sin(2 * np.pi * 2 * note(m) * t)) * np.exp(-t * 1.1) for m in ms) * trem * np.minimum(1, t * 40) * .18
def bass(m, d): t = tt(d); return np.sin(2 * np.pi * note(m) * t) * np.minimum(1, t * 50) * np.exp(-t * .9) * .9
# ---------- cold open: clock + cards + scribble + riser ----------
c = S['cold']; tk, iv = .3, .55
while tk < c['vo'][3]['t0'] + 1.6: add(sfx, tk, tick(3000 if int(tk * 10) % 2 else 2300, .03), .22); iv = max(.12, .55 - tk / c['dur'] * .45); tk += iv
l1, l1e = c['vo'][1]['t0'], c['vo'][1]['t1']
times = [l1 + (l1e - l1) * i / 4 + .1 for i in range(4)] + [c['vo'][2]['t0'] + 1.4] + [c['vo'][3]['t0'] + .3 + i * .28 for i in range(3)]
for tm in times: add(sfx, tm - .05, whoosh(.25), .25, .7); add(sfx, tm + .1, kick(.5), .5); add(sfx, tm + .12, tick(1900, .05), .3)
for i in range(4): add(sfx, c['vo'][3]['t0'] + 1.6 + i * .08, scratch(), .5, .3 + i * .15)
add(mus, c['dur'] - 3.0, riser(3.0), .35)
# ---------- music from intro on: 92 BPM lo-fi ----------
D = S['intro']['t0']; b = 60 / 92
add(sfx, D, boom(), .7); add(sfx, D + .35, ding() * .5, .35)
prog = [[62, 66, 69, 73], [59, 62, 66, 69], [55, 59, 62, 66], [57, 61, 64, 66]]; roots = [50, 47, 43, 45]
END = SC[-1]['t0'] + SC[-1]['dur'] - 1.0; k = 0; tb = D
while tb < END:
    bar = (k // 4) % 4
    if k % 4 == 0: add(mus, tb, keys_chord(prog[bar], b * 4.2), 1.0); add(mus, tb, bass(roots[bar] - 12, b * 3.8), .5)
    if k % 2 == 0: add(mus, tb, kick(.8), .55)
    else: add(mus, tb, snare(), .25)
    add(mus, tb + b / 2, hat(), .4, .62); tb += b; k += 1
# ---------- live-scene sfx ----------
prev = None
for s in SC:
    if s['page'] != prev and s['page'] != 'kinetic' and s['id'] != 'intro': add(sfx, s['t0'] - .25, whoosh(.45), .45, .4)
    prev = s['page']
    for e in EV.get(s['id'], []):
        te = s['t0'] + e[0] / 30
        if e[1] == 'key': add(sfx, te, key(), .32, rng.uniform(.35, .65))
        elif e[1] == 'tap': add(sfx, te, click(), .35)
        elif e[1] == 'tick': add(sfx, te, tick(2300, .05), .3)
        elif e[1] == 'pop': add(sfx, te, bubble(500, 1100), .35)
add(sfx, S['intro']['vo'][2]['t0'] - .25, whoosh(.45), .4)
# ---------- outro accents ----------
o = S['outro']
for i in range(14): add(sfx, o['vo'][0]['t0'] + .3 + i * .06, bubble(500 + i * 40, 1000 + i * 60, .08), .18)
for i, d in enumerate([0, .9, 2.2]): add(sfx, o['vo'][1]['t0'] + d, kick(.7), .45)
a2 = o['vo'][2]['t0']
for i in range(20): add(sfx, a2 + .3 + 1.1 * i / 20, key(), .35)
add(sfx, a2 + 1.45, ding(), .45); add(sfx, o['vo'][3]['t0'], bubble(300, 900, .2), .35)
# ---------- mix: duck music under the voice ----------
env = np.sqrt(lp(vo ** 2, int(SR * .25))); env = env / (env.max() + 1e-9)
duck = 1 - .72 * np.clip(env * 6, 0, 1); duck = lp(duck, int(SR * .15))
rev = np.zeros_like(mus)
for d, g in [(.031, .3), (.047, .26), (.071, .2), (.11, .15), (.16, .1)]: kk = int(d * SR); rev[kk:, 0] += mus[:-kk, 1] * g; rev[kk:, 1] += mus[:-kk, 0] * g
music = (mus + rev * .5) * duck[:, None] * .55
out = music + sfx * .8 + np.stack([vo, vo], 1) * 1.15
fo = int(1.2 * SR); out[-fo:] *= np.linspace(1, 0, fo)[:, None]
out = np.tanh(out * 1.1); out /= np.abs(out).max() / .89
with wave.open('yt.wav', 'wb') as ww:
    ww.setnchannels(2); ww.setsampwidth(2); ww.setframerate(SR); ww.writeframes((out[:int(DUR * SR)] * 32767).astype('<i2').tobytes())
print('ok', DUR)
