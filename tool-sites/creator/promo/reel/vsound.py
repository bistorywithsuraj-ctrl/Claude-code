import numpy as np, wave, json
TL = json.load(open('timeline.json')); EV = json.load(open('live/events.json'))
SR = 48000; DUR = TL['duration']; N = int(SR * (DUR + .2))
mus = np.zeros((N, 2)); sfx = np.zeros((N, 2)); rng = np.random.default_rng(3)
def add(buf, t, sig, g=1.0, pan=.5):
    s = int(t * SR)
    if s >= N or s < 0: return
    sig = sig[:N - s]
    if sig.ndim == 1: buf[s:s + len(sig), 0] += sig * g * (1 - pan) * 2 ** .5; buf[s:s + len(sig), 1] += sig * g * pan * 2 ** .5
    else: buf[s:s + len(sig)] += sig * g
def tt(d): return np.arange(int(d * SR)) / SR
def lp(x, k): return np.convolve(x, np.ones(k) / k, 'same')
def hp(x): return np.diff(x, prepend=0)
note = lambda m: 440 * 2 ** ((m - 69) / 12)
# ---------- instruments ----------
def kick(g=1): t = tt(.45); return np.sin(2 * np.pi * (45 * t + 140 / 28 * (1 - np.exp(-t * 28)))) * np.exp(-t * 7) * g
def boom(): t = tt(2.2); return np.tanh(2.5 * np.sin(2 * np.pi * (36 * t + 160 / 18 * (1 - np.exp(-t * 18)))) * np.exp(-t * 1.6))
def clap(): t = tt(.25); n = rng.standard_normal(len(t)); e = np.exp(-t * 30) + .5 * np.exp(-((t - .012) * 300) ** 2) + .4 * np.exp(-((t - .024) * 300) ** 2); return hp(lp(n, 3)) * e * .9
def hat(): t = tt(.06); return hp(hp(rng.standard_normal(len(t)))) * np.exp(-t * 80) * .35
def tick(f=2600, d=.035): t = tt(d); return (np.sin(2 * np.pi * f * t) * .6 + hp(rng.standard_normal(len(t))) * .3) * np.exp(-t * 140)
def key(): t = tt(.03); return (hp(lp(rng.standard_normal(len(t)), 2)) * .7 + np.sin(2 * np.pi * rng.uniform(1700, 2600) * t) * .25) * np.exp(-t * 220)
def click(): t = tt(.06); return (np.sin(2 * np.pi * 1500 * t) * np.exp(-t * 90) + .5 * np.sin(2 * np.pi * 3100 * t) * np.exp(-t * 160) + hp(rng.standard_normal(len(t))) * .15 * np.exp(-t * 300))
def bubble(f0=500, f1=1300, d=.12): t = tt(d); f = f0 + (f1 - f0) * (t / d) ** .5; return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 28) * (1 - np.exp(-t * 900))
def whoosh(d=.45, up=True):
    t = tt(d); n = rng.standard_normal(len(t)); env = np.sin(np.pi * t / d) ** 2
    lo, hi = lp(n, 30), lp(n, 4); m = (t / d) if up else 1 - t / d; return (lo * (1 - m) + hi * m) * env * 1.4
def scratch(d=.2): t = tt(d); n = rng.standard_normal(len(t)); return hp(lp(n, 3)) * (np.abs(np.sin(2 * np.pi * 22 * t)) ** 2) * np.exp(-t * 4) * .9
def riser(d):
    t = tt(d); n = rng.standard_normal(len(t)); out = np.zeros_like(t); seg = len(t) // 12
    for i in range(12): a = i * seg; out[a:a + seg] = lp(n[a:a + seg], max(1, 40 - i * 3))
    tone = np.sin(2 * np.pi * np.cumsum(200 + 900 * (t / d) ** 2) / SR) * .25
    return (out + tone) * (t / d) ** 2
def ding(): t = tt(1.4); return sum(np.sin(2 * np.pi * note(m) * t) * np.exp(-t * k) * g for m, k, g in ((88, 3, .5), (95, 4, .25), (100, 6, .12)))
def crash(): t = tt(1.8); return hp(rng.standard_normal(len(t))) * np.exp(-t * 2.2) * .35
def pluck(m, d=.35): t = tt(d); f = note(m); return (np.sin(2 * np.pi * f * t) + .45 * np.sign(np.sin(2 * np.pi * f * t)) * np.exp(-t * 18)) * np.exp(-t * 9) * .5
def bass(m, d): t = tt(d); f = note(m); return np.tanh(1.8 * np.sin(2 * np.pi * f * t)) * np.minimum(1, t * 60) * np.exp(-t * 1.2)
# ---------- pre-drop: problem ----------
add(sfx, .05, bubble(300, 700, .1), .5); add(sfx, .45, bubble(400, 900), .6); add(sfx, .7, kick(.9), .9); add(sfx, 1.0, scratch(.3), .5)
tk, iv = .1, .5
while tk < 4.42: add(sfx, tk, tick(3200 if int(tk / iv) % 2 else 2400, .03), .35); iv = max(.09, .5 - (tk / 4.4) * .42); tk += iv
for i in range(len(TL['choreList'])):
    t0 = TL['choreStart'] + i * TL['chorePace']; add(sfx, t0 - .05, whoosh(.22), .35, .7); add(sfx, t0 + .1, kick(.6), .6); add(sfx, t0 + .12, tick(1800 + i * 120, .05), .45)
add(mus, 1.6, riser(2.8) * .5, .5)
for i in range(4): add(sfx, 4.42 + i * .07, scratch(.22), .7, .3 + i * .15)
t = tt(.6); add(sfx, 4.42, np.sin(2 * np.pi * 38 * t) * np.exp(-t * 4), .6)
# turn
add(sfx, 4.82, whoosh(.3, False), .4); add(sfx, 5.1, bubble(350, 1500, .18), .7); add(mus, 4.85, riser(.7), .9)
# ---------- drop + groove ----------
D, b = TL['drop'], TL['beat']; END = TL['end'][0]
add(sfx, D, boom(), .95); add(sfx, D, crash(), .7); add(sfx, D + .05, bubble(200, 900, .2), .5)
prog = [57, 53, 48, 55]   # Am F C G
chords = {57: [69, 72, 76], 53: [65, 69, 72], 48: [67, 72, 76], 55: [67, 71, 74]}
k = 0; tb = D
duck = np.ones(N)
while tb < END - .01:
    bar = k // 4; root = prog[bar % 4]
    if k > 0: add(mus, tb, kick(), .85)
    s = int(tb * SR); L = int(.18 * SR); duck[s:s + L] = np.minimum(duck[s:s + L], .35 + .65 * np.linspace(0, 1, L) ** 2)
    if k % 2 == 1: add(mus, tb, clap(), .5)
    add(mus, tb + b / 2, hat(), .55, .62); add(mus, tb + b / 4 * 3, hat(), .25, .4)
    if k % 4 == 0: add(mus, tb, bass(root - 24, b * 4), .38)
    for j, m in enumerate(chords[root]): add(mus, tb + b / 2, pluck(m + (12 if k % 8 >= 4 and j == 2 else 0)), .16, .3 + j * .2)
    tb += b; k += 1
# ---------- live scene sfx ----------
scenes = [('map-stops', TL['mapStops'][0]), ('map-render', TL['mapRender'][0])] + [(s, TL['toolsStart'] + i * TL['toolDur']) for i, s in enumerate(TL['tools'])]
for sc, t0 in scenes:
    add(sfx, t0 - .2, whoosh(.32), .55, .35 if hash(sc) % 2 else .65)
    tog = 0
    for e in EV.get(sc, []):
        te = t0 + e[0] / 30
        if e[1] == 'key': add(sfx, te, key(), .5, rng.uniform(.35, .65))
        elif e[1] == 'tap': add(sfx, te, click(), .55)
        elif e[1] == 'tick': add(sfx, te, tick(2200 + e[0] * 20, .05), .45)
        elif e[1] == 'pop': add(sfx, te, bubble(500, 1100), .55)
        elif e[1] == 'toggle': add(sfx, te - .05, click(), .5); add(sfx, te, bubble(500 + tog * 150, 1100 + tog * 250), .6); tog += 1
add(sfx, TL['mapRender'][0], bubble(400, 1000), .5)   # globe toggle (already on)
add(sfx, TL['more'][0], kick(1.0), .8); add(sfx, TL['more'][0], crash(), .35); add(sfx, TL['more'][0] - .3, riser(.3), .5)
# intro accents
a = TL['intro'][0]; add(sfx, a + .3, ding() * .5, .45); add(sfx, a + .8, click(), .5)
# ---------- end card ----------
a = TL['end'][0]; add(sfx, a - .25, whoosh(.3), .5); add(sfx, a, boom(), .6)
t = tt(4.2)
for m in (57, 64, 69, 72, 76): add(mus, a, np.sin(2 * np.pi * note(m) * t) * np.exp(-t * .9) * np.minimum(1, t * 8) * .07, 1, .5)
add(sfx, a + .35, bubble(300, 1200, .2), .7); add(sfx, a + .36, kick(1.0), .7)
url_n = len('creatorbenchtool.com')
for i in range(url_n): add(sfx, a + 1.45 + .65 * i / url_n, key(), .55, rng.uniform(.4, .6))
add(sfx, a + 1.3, click(), .5); add(sfx, a + 2.12, ding(), .6); add(sfx, a + 2.3, bubble(400, 900), .4)
# ---------- mix ----------
mus *= duck[:, None] ** .8
rev = np.zeros_like(mus)
for d, g in [(.029, .3), (.043, .26), (.067, .22), (.101, .17), (.149, .12), (.223, .08)]:
    k = int(d * SR); rev[k:, 0] += mus[:-k, 1] * g; rev[k:, 1] += mus[:-k, 0] * g
out = mus * 1.0 + rev * .5 + sfx * 1.1
fo = int(.5 * SR); out[-fo:] *= np.linspace(1, 0, fo)[:, None]
out = np.tanh(out * 1.2); out /= np.abs(out).max() / .9
with wave.open('viral.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out[:int(DUR * SR)] * 32767).astype('<i2').tobytes())
print('sound ok', DUR)
