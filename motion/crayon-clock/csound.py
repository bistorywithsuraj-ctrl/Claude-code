import numpy as np, wave
SR = 48000; DUR = 12.0; N = int(SR * DUR); rng = np.random.default_rng(9)
out = np.zeros((N, 2))
def add(t, sig, g=1., pan=.5):
    s = int(t * SR)
    if s < 0 or s >= N: return
    sig = sig[:N - s]; out[s:s + len(sig), 0] += sig * g * (1 - pan) * 1.41; out[s:s + len(sig), 1] += sig * g * pan * 1.41
tt = lambda d: np.arange(int(d * SR)) / SR
def lp(x, k):
    c = np.cumsum(np.concatenate([[0.], x])); y = (c[k:] - c[:-k]) / k; p = len(x) - len(y); return np.concatenate([np.full(p // 2, y[0]), y, np.full(p - p // 2, y[-1])])
hp = lambda x: np.diff(x, prepend=0); note = lambda m: 440 * 2 ** ((m - 69) / 12)
def scribble(d): t = tt(d); n = hp(lp(rng.standard_normal(len(t)), 3)); m = .5 + .5 * np.abs(np.sin(2 * np.pi * rng.uniform(5, 9) * t + rng.uniform(0, 6))); return n * m * np.sin(np.pi * t / d) * .5
def tick(f, d=.04): t = tt(d); return (np.sin(2 * np.pi * f * t) * .7 + hp(rng.standard_normal(len(t))) * .4) * np.exp(-t * 130)
def tap(): t = tt(.05); return (hp(lp(rng.standard_normal(len(t)), 2)) * .6 + np.sin(2 * np.pi * 900 * t) * .3) * np.exp(-t * 120)
def bell(): t = tt(4.0); return sum(np.sin(2 * np.pi * f * t) * np.exp(-t * k) * g for f, k, g in ((note(81), .9, .5), (note(81) * 2.76, 1.6, .22), (note(81) * 5.4, 2.6, .1), (note(69), .7, .25)))
# crayon scratching while things draw in
tc = .1
while tc < 4.6: d = rng.uniform(.18, .45); add(tc, scribble(d), .55 if tc < 2.2 else .35, rng.uniform(.3, .7)); tc += d * rng.uniform(.6, 1.0)
for n in range(12): add(3.9 + n * .11, tap(), .5, .3 + n / 24)
add(5.25, tap(), .6)
# clock-time model (mirrors clock.html) -> tick on every 5-minute step
def ease_out(p): return 1 - (1 - p) ** 3
def inv(a, b, x): return min(1, max(0, (x - a) / (b - a)))
def ctime(t):
    if t < 7.0: return int(max(0, min(t, 7.0) - 5.6) / .5) * 5 / 60
    base = int((7.0 - 5.6) / .5) * 5 / 60; target = 10 + 10 / 60 + 24; p = inv(7.0, 11.2, t)
    s = (p / .75) ** 2.2 * .96 if p < .75 else .96 + .04 * ease_out((p - .75) / .25); return base + (target - base) * s
last, lt, k = 0, -1, 0
for i in range(int(5.6 * SR), int(11.3 * SR), int(SR / 600)):
    t = i / SR; step = int(ctime(t) * 12)
    if step != last:
        if t - lt > .016: add(t, tick(2400 if k % 2 else 1800), .45 if t < 7.2 else .3, .5 + (.1 if k % 2 else -.1)); lt = t; k += 1
        last = step
# whirr + riser while spinning
t = tt(3.6); n = rng.standard_normal(len(t)); r = (lp(n, 6) * (t / 3.6) ** 2) * .5 + np.sin(2 * np.pi * np.cumsum(150 + 500 * (t / 3.6) ** 2) / SR) * .12 * (t / 3.6); add(7.0, r * np.minimum(1, (3.6 - t) * 6), .6)
# dreamy pad underneath
t = tt(DUR)
pad = sum(np.sin(2 * np.pi * note(m) * t + i) * .05 for i, m in enumerate((50, 57, 62, 66, 69))) * (1 + .2 * np.sin(2 * np.pi * .2 * t))
pad *= np.minimum(1, t / 2.0) * (1 - .6 * np.array([inv(7, 10.5, x) for x in t[::480]]).repeat(480)[:len(t)]); add(0, pad, .9)
add(11.15, bell(), .7); t = tt(1.5); add(11.15, np.sin(2 * np.pi * 45 * t) * np.exp(-t * 3), .5)
rev = np.zeros_like(out)
for d, g in [(.037, .35), (.053, .3), (.079, .25), (.12, .18), (.18, .12), (.27, .08)]: kk = int(d * SR); rev[kk:, 0] += out[:-kk, 1] * g; rev[kk:, 1] += out[:-kk, 0] * g
out = out + rev * .6; f = int(.3 * SR); out[:f] *= np.linspace(0, 1, f)[:, None]; out[-f:] *= np.linspace(1, 0, f)[:, None]
out = np.tanh(out * 1.3); out /= np.abs(out).max() / .89
with wave.open('clock.wav', 'wb') as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out * 32767).astype('<i2').tobytes())
print('ok')
