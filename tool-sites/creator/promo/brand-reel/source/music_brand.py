"""Original 60 s track for the brand reel, 120 BPM. Sections follow the edit:
intro hook 0-4 (build), drop 4-37.5, breakdown 37.5-44.5, build 44.5-48, drop 2 48-54, outro 54-60."""
import numpy as np, soundfile as sf
SR = 48000; DUR = 60; N = DUR * SR; BT = .5; rng = np.random.default_rng(11)
tt = lambda d: np.arange(int(d * SR)) / SR
def lp(x, k):
    if k <= 1: return x
    c = np.cumsum(np.concatenate([[0.], x])); y = (c[k:] - c[:-k]) / k; p = len(x) - len(y); return np.concatenate([np.full(p // 2, y[0]), y, np.full(p - p // 2, y[-1])])
hp = lambda x: np.diff(x, prepend=0); note = lambda m: 440 * 2 ** ((m - 69) / 12)
L = np.zeros(N); R = np.zeros(N)
def add(t, sig, g=1., pan=0.):
    s = int(t * SR)
    if 0 <= s < N: sig = sig[:N - s]; L[s:s + len(sig)] += sig * g * (1 - max(0, pan)); R[s:s + len(sig)] += sig * g * (1 + min(0, pan))
kick = lambda: (lambda t: np.tanh(2.2 * np.sin(2 * np.pi * (46 * t + 150 / 26 * (1 - np.exp(-t * 26))))) * np.exp(-t * 6.5))(tt(.45))
clap = lambda: (lambda t: hp(lp(rng.standard_normal(len(t)), 2)) * (np.exp(-t * 28) + .6 * np.exp(-((t - .01) * 250) ** 2)) * .9)(tt(.25))
hat = lambda o=False: (lambda t: hp(hp(rng.standard_normal(len(t)))) * np.exp(-t * (18 if o else 70)) * .3)(tt(.18 if o else .05))
def saw(f, d, cut=8):
    t = tt(d); ph = (f * t) % 1; return lp(2 * ph - 1, cut)
def stab(ms, d=.22): t = tt(d); return sum(saw(note(m), d, 6) for m in ms) * np.exp(-t * 9) * .16
def pad(ms, d): t = tt(d); env = np.minimum(1, t / .8) * np.minimum(1, (d - t) / .8); return sum(np.sin(2 * np.pi * note(m) * t + .3 * np.sin(2 * np.pi * .3 * t)) for m in ms) * env * .07
def bass(m, d): t = tt(d); return np.tanh(2.5 * np.sin(2 * np.pi * note(m) * t)) * np.minimum(1, t * 60) * np.exp(-t * 3) * .4
def riser(d):
    t = tt(d); n = rng.standard_normal(len(t)); out = np.zeros_like(t); seg = max(1, len(t) // 12)
    for i in range(12): a = i * seg; out[a:a + seg] = lp(n[a:a + seg], max(1, 40 - i * 3))
    return (out * .8 + np.sin(2 * np.pi * np.cumsum(200 + 1400 * (t / d) ** 2) / SR) * .3) * (t / d) ** 2
def impact(): t = tt(2.5); return (np.tanh(3 * np.sin(2 * np.pi * (34 * t + 120 / 14 * (1 - np.exp(-t * 14))))) * np.exp(-t * 1.6) + lp(rng.standard_normal(len(t)), 3) * np.exp(-t * 5) * .5) * .9
def whoosh(d=.3): t = tt(d); n = rng.standard_normal(len(t)); m = t / d; return (lp(n, 22) * (1 - m) + lp(n, 3) * m) * np.sin(np.pi * m) ** 2
PROG = [([57, 60, 64], 45), ([53, 57, 60], 41), ([48, 52, 55], 36), ([55, 59, 62], 43)]   # Am F C G
drop = lambda t: 4 <= t < 37.5 or 48 <= t < 54
b = 0; t = 0.
while t < DUR - 1e-6:
    ch, root = PROG[(b // 8) % 4]
    if drop(t):
        add(t, kick(), .9)
        if b % 2 == 1: add(t, clap(), .55)
        for k in range(4): add(t + k * BT / 4, hat(k == 2), .5 if k % 2 else .3, (-.3 if k % 2 else .3))
        add(t, bass(root - 12 + (7 if b % 4 == 3 else 0), BT * .9), .9)
        if b % 2 == 0: add(t + BT * .5, stab([m + 12 for m in ch]), .8, .2)
    elif t < 4:   # intro: hits on the hook, filtered hats
        if b in (0, 2, 4, 6): add(t, kick(), .8)
        add(t, hat(), .25)
    elif 37.5 <= t < 44.5:   # breakdown
        if b % 8 == 0: add(t, pad(ch + [ch[0] + 12], BT * 8), 1.)
        if b % 2 == 0: add(t, hat(), .15)
    elif 44.5 <= t < 48:   # build: snare roll speeding up
        if b % 8 == 0: add(t, pad(ch, BT * 7), .8)
        n = 1 if t < 46 else 2 if t < 47 else 4
        for k in range(n): add(t + k * BT / n, clap(), .25 + .3 * (t - 44.5) / 3.5)
    elif t >= 54:   # outro
        if b % 8 == 0: add(t, pad([57, 64, 69, 72], 6), 1.)
    t += BT; b += 1
add(2.4, riser(1.6), .45); add(4.0, impact(), .55); add(46.0, riser(2.0), .5); add(48.0, impact(), .6); add(54.0, impact(), .45)
for c in [7.5, 12.5, 17.5, 22.5, 27.5, 32.5, 37.5, 40, 42.5, 47.5, 50, 51.5]: add(c - .25, whoosh(), .35, .2)
for k in range(6): add(50 + k * .25, hat(True), .4)
out = np.stack([L, R], 1); out /= np.abs(out).max() / .9
fade = np.ones(N); n = int(1.5 * SR); fade[-n:] = np.linspace(1, 0, n) ** 2; out *= fade[:, None]
sf.write('music.wav', out, SR); print('music', DUR, 's')
