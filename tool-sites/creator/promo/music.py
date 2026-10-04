import numpy as np, wave
SR, DUR = 48000, 30.0
N = int(SR * DUR); t = np.arange(N) / SR
out = np.zeros((N, 2))
rng = np.random.default_rng(7)
def note(f): return 440 * 2 ** ((f - 69) / 12)
BPM = 96; beat = 60 / BPM
# I - vi - IV - V in D major, two bars each (warm, optimistic)
chords = [[50, 57, 62, 66, 69], [47, 54, 59, 62, 66], [43, 50, 55, 59, 62], [45, 52, 57, 61, 64]]
bar = beat * 4
def env(n, a, r):
    e = np.ones(n); a = int(a * SR); r = int(r * SR)
    e[:a] = np.linspace(0, 1, a); e[-r:] *= np.linspace(1, 0, r); return e
# pads
i = 0; start = 0.0
while start < DUR:
    ch = chords[i % 4]; s0 = int(start * SR); L = min(int(bar * 2 * SR) + int(.8 * SR), N - s0)
    if L <= 0: break
    tt = np.arange(L) / SR; e = env(L, .9, .9)
    for k, m in enumerate(ch):
        f = note(m)
        for det, pan in ((-0.12, .3), (0.12, .7)):
            w = np.sin(2 * np.pi * (f + det) * tt + k) * 0.6 + 0.25 * np.sin(2 * np.pi * 2 * (f + det) * tt)
            out[s0:s0 + L, 0] += w * e * (1 - pan) * .028; out[s0:s0 + L, 1] += w * e * pan * .028
    start += bar * 2; i += 1
# plucks: arpeggio from ~2.6s, eighth notes
step = beat / 2; k = 0; tp = 2.6
while tp < 28.6:
    ci = int(tp // (bar * 2)) % 4; ch = chords[ci]; m = ch[[2, 3, 4, 3][k % 4]] + 12
    s0 = int(tp * SR); L = min(int(1.2 * SR), N - s0); tt = np.arange(L) / SR; f = note(m)
    w = (np.sin(2 * np.pi * f * tt) + .3 * np.sin(2 * np.pi * 2 * f * tt) + .1 * np.sin(2 * np.pi * 3 * f * tt)) * np.exp(-tt * 5.5)
    pan = .35 + .3 * (k % 2); g = .05 if k % 2 == 0 else .035
    out[s0:s0 + L, 0] += w * g * (1 - pan); out[s0:s0 + L, 1] += w * g * pan
    tp += step; k += 1
# soft kick + shaker from the device sequence (5.2s) to the end card
tb = 5.2
while tb < 26.2:
    s0 = int(tb * SR); L = int(.35 * SR); tt = np.arange(L) / SR
    kick = np.sin(2 * np.pi * (48 + 60 * np.exp(-tt * 30)) * tt) * np.exp(-tt * 9) * .16
    out[s0:s0 + L] += kick[:, None]
    s1 = int((tb + beat / 2) * SR); L2 = int(.08 * SR); sh = rng.standard_normal(L2) * np.exp(-np.arange(L2) / SR * 60) * .018
    sh = np.convolve(sh, [1, -1], 'same'); out[s1:s1 + L2, 0] += sh * .8; out[s1:s1 + L2, 1] += sh
    tb += beat
# whooshes on cuts
def whoosh(at, g=.09, d=.7):
    L = int(d * SR); s0 = int((at - d * .6) * SR); n = rng.standard_normal(L)
    a = np.exp(-((np.arange(L) / L - .6) ** 2) / .03)
    # sweeping low-pass via moving average of decreasing width
    y = np.zeros(L); acc = 0
    for j in range(L): pass
    from numpy.lib.stride_tricks import sliding_window_view
    sm = np.convolve(n, np.ones(12) / 12, 'same'); y = (sm * .7 + n * .3 * np.linspace(0, 1, L)) * a * g
    out[s0:s0 + L, 0] += y * np.linspace(.3, .7, L); out[s0:s0 + L, 1] += y * np.linspace(.7, .3, L)
for c in [2.4, 5.0] + [5.2 + 3 * i for i in range(1, 7)]: whoosh(c, .06)
whoosh(26.2, .1, 1.0)
# end-card swell + low hit
s0 = int(26.3 * SR); L = N - s0; tt = np.arange(L) / SR
hit = np.sin(2 * np.pi * note(38) * tt) * np.exp(-tt * 1.6) * .2 + np.sin(2 * np.pi * note(50) * tt) * np.exp(-tt * 1.2) * .08
out[s0:, :] += hit[:, None]
for m in [62, 66, 69, 74]:
    out[s0:, 0] += np.sin(2 * np.pi * note(m) * tt) * np.exp(-tt * .9) * .025; out[s0:, 1] += np.sin(2 * np.pi * note(m) * tt + .5) * np.exp(-tt * .9) * .025
# simple reverb (multi-tap), master fade, normalize
rev = np.zeros_like(out)
for d, g in [(.031, .35), (.047, .3), (.073, .25), (.113, .2), (.167, .15), (.241, .1)]:
    k = int(d * SR); rev[k:, 0] += out[:-k, 1] * g; rev[k:, 1] += out[:-k, 0] * g
out = out + rev * .6
fade = np.ones(N); fi = int(.4 * SR); fo = int(1.6 * SR); fade[:fi] = np.linspace(0, 1, fi); fade[-fo:] = np.linspace(1, 0, fo) ** 1.5
out *= fade[:, None]; out = np.tanh(out * 1.4); out /= np.abs(out).max() / .89
with wave.open('music.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out * 32767).astype('<i2').tobytes())
print('ok')
