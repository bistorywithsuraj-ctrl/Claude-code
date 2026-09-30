"""Procedural score + SFX for the F1 intro. 120 BPM so every scene cut (whole seconds) lands on a beat."""
import numpy as np, wave
from scipy.signal import butter, sosfilt, fftconvolve

SR, DUR = 48000, 72.0
N = int(SR * DUR)
rng = np.random.default_rng(3)
L = np.zeros(N); R = np.zeros(N)       # dry bus
RV = np.zeros(N)                        # reverb send (mono)
BEAT = 0.5

def lp(x, f, o=2): return sosfilt(butter(o, f, 'low', fs=SR, output='sos'), x)
def hp(x, f, o=2): return sosfilt(butter(o, f, 'high', fs=SR, output='sos'), x)
def bp(x, a, b, o=2): return sosfilt(butter(o, [a, b], 'band', fs=SR, output='sos'), x)
def midi(m): return 440 * 2 ** ((m - 69) / 12)
def saw(ph): return 2 * (ph % 1.0) - 1

def add(sig, t0, gain=1.0, pan=0.0, rev=0.0):
    i = int(t0 * SR)
    if i >= N: return
    if i < 0: sig = sig[-i:]; i = 0
    sig = sig[:N - i]
    gl, gr = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    L[i:i + len(sig)] += sig * gain * gl * 1.414
    R[i:i + len(sig)] += sig * gain * gr * 1.414
    RV[i:i + len(sig)] += sig * gain * rev

def env(n, a, d, sus=None):
    t = np.arange(n) / SR
    e = np.minimum(1, t / max(a, 1e-4)) * np.exp(-np.maximum(0, t - a) / d)
    return e

# ---------------- instruments ----------------
def kick(g=1.0):
    n = int(.5 * SR); t = np.arange(n) / SR
    f = 45 + 95 * np.exp(-t * 28)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7)
    s += lp(rng.standard_normal(n), 4000) * np.exp(-t * 180) * .3
    return np.tanh(s * 1.6) * g

def hat(open_=False):
    n = int((.18 if open_ else .05) * SR)
    return hp(rng.standard_normal(n), 7500) * env(n, .001, .06 if open_ else .012)

def snare():
    n = int(.3 * SR); t = np.arange(n) / SR
    return bp(rng.standard_normal(n), 1200, 6000) * np.exp(-t * 18) * .8 + np.sin(2 * np.pi * 185 * t) * np.exp(-t * 30) * .5

def pluck_bass(freq, dur=.24):
    n = int(dur * SR); t = np.arange(n) / SR
    s = saw(freq * t) * .6 + saw(freq * 1.005 * t) * .4
    s = lp(s, 300 + 900 * np.exp(-t * 20).mean())
    return lp(s, 500) * env(n, .004, .12)

def pad_chord(notes, dur):
    n = int(dur * SR); t = np.arange(n) / SR; s = np.zeros(n)
    for m in notes:
        for det in (-.12, 0, .11):
            s += saw(midi(m + det) * t + rng.random())
    s = lp(s, 900, 4) / (len(notes) * 3)
    a = np.minimum(1, t / .6) * np.minimum(1, (dur - t) / .6)
    return s * a

def tick(f=2600, d=.012):
    n = int(.04 * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * f * t) * np.exp(-t / d)

def thump():
    n = int(.18 * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * (70 + 60 * np.exp(-t * 40)) * t) * np.exp(-t * 22) + lp(rng.standard_normal(n), 900) * np.exp(-t * 40) * .5)

def paper():  # riffle of cash
    n = int(.07 * SR); t = np.arange(n) / SR
    return bp(rng.standard_normal(n), 2500, 9000) * np.exp(-t * 60)

def sweep_filter(x, fc):  # time-varying state-variable bandpass
    y = np.zeros_like(x); low = band = 0.0; q = .9
    for i in range(len(x)):
        f = 2 * np.sin(np.pi * fc[i] / SR)
        high = x[i] - low - q * band; band += f * high; low += f * band; y[i] = band
    return y

def whoosh(dur=.9, f0=250, f1=5000):
    n = int(dur * SR); t = np.linspace(0, 1, n)
    shape = np.sin(np.pi * t) ** 2
    fc = f0 * (f1 / f0) ** np.sin(np.pi * t)
    return sweep_filter(rng.standard_normal(n), fc) * shape * .6

def impact():
    n = int(3.5 * SR); t = np.arange(n) / SR
    sub = np.sin(2 * np.pi * (38 + 60 * np.exp(-t * 12)) * t) * np.exp(-t * 1.3)
    crack = lp(rng.standard_normal(n), 3000) * np.exp(-t * 9) * .6
    return np.tanh((sub + crack) * 1.4)

def riser(dur):
    n = int(dur * SR); t = np.arange(n) / SR; p = t / dur
    noise = sweep_filter(rng.standard_normal(n), 300 * (30 ** p)) * p ** 2
    tone = np.sin(2 * np.pi * np.cumsum(110 * 2 ** (2.5 * p)) / SR) * p ** 3 * .25
    return noise * .8 + tone

def engine(dur, tc):
    """F1-style V6 howl passing by at time tc (relative), with doppler + pan."""
    n = int(dur * SR); t = np.arange(n) / SR
    rpm = 240 + 90 * (t / dur)                      # rising revs
    dop = 1 + .18 * np.tanh((tc - t) * 2.2)          # approaching higher, receding lower
    f = rpm * dop
    ph = np.cumsum(f) / SR
    s = saw(ph) * .5 + saw(ph * 2 + .3) * .3 + np.sin(2 * np.pi * ph * 3) * .2
    s *= 1 + .25 * np.sin(2 * np.pi * ph * .5)       # combustion rasp
    s = lp(s, 2600, 4) + hp(rng.standard_normal(n), 3000) * .03
    amp = 1 / (1 + ((t - tc) * 1.6) ** 2)
    return s * amp, np.tanh((t - tc) * 1.5)

# ---------------- arrangement ----------------
PROG = [[62, 65, 69], [58, 62, 65], [65, 69, 72], [60, 64, 67]]   # Dm Bb F C
ROOT = [38, 34, 41, 36]
for bar in range(36):                     # 72 s / 2 s per bar
    t0 = bar * 2.0; c = bar % 4
    level = .20 if t0 < 64 else .28
    add(pad_chord([m - 12 for m in PROG[c]] + [PROG[c][0]], 2.6), t0 - .3, level, 0, .35)

# groove sections (kick/hat/bass) — muted in the cold open, the typographic drop and the title
def grooving(t): return (7 <= t < 22) or (28 <= t < 63)
for b in range(int(72 / BEAT)):
    t = b * BEAT
    if not grooving(t): continue
    bar = int(t // 2); c = bar % 4
    add(kick(), t, .55, 0, .05)
    add(hat(), t + .25, .10, .3)
    add(hat(), t + .125, .04, -.3); add(hat(), t + .375, .04, -.3)
    if b % 4 == 2 and t >= 28: add(snare(), t, .22, 0, .25)
    for k, off in enumerate((0, .25)):
        add(pluck_bass(midi(ROOT[c] + (12 if k and b % 2 else 0))), t + off, .35)

# sidechain-ish duck on everything but drums: done by kick level being loud; keep simple

# heartbeat in cold open
for t in np.arange(0.5, 7, 1.0): add(kick(.6), t, .45, 0, .1)

# engine flyby (car appears ~2.6 s) and title-card car
e, pan = engine(4.5, 2.2)
i0 = int(2.2 * SR); seg = e
Lp = seg * np.cos((pan + 1) * np.pi / 4) * 1.414; Rp = seg * np.sin((pan + 1) * np.pi / 4) * 1.414
L[i0:i0 + len(seg)] += Lp * .35; R[i0:i0 + len(seg)] += Rp * .35; RV[i0:i0 + len(seg)] += seg * .12
e2, pan2 = engine(5, 2.8)
i1 = int(65.6 * SR)
L[i1:i1 + len(e2)] += e2 * np.cos((pan2 + 1) * np.pi / 4) * .25; R[i1:i1 + len(e2)] += e2 * np.sin((pan2 + 1) * np.pi / 4) * .25

# counter ticks ($180M counting 2.2–3.6)
for t in np.arange(2.2, 3.6, .05): add(tick(2200 + (t - 2.2) * 800), t, .10, .2)
add(impact()[:int(1.2 * SR)], 2.1, .35, 0, .3)

# standings bars ticks (S2)
for i in range(10): add(tick(1800 - i * 60), 7.35 + i * .08, .10, -.2 + i * .04)
add(thump(), 11.3, .6, 0, .4)            # highlight on Williams
add(impact()[:int(1.5 * SR)], 11.4, .30, 0, .4)

# S3 squares
add(thump(), 15.0, .5); add(whoosh(1.4, 120, 1800), 16.2, .35, 0, .2)
for k in range(17): add(tick(1500 + k * 40), 17.8 + k * .06, .07, (k % 4 - 1.5) * .3)
add(impact()[:int(2 * SR)], 19.0, .45, 0, .4)

# S4 typographic: strike + business hit
add(whoosh(.6, 800, 7000), 23.3, .45, .4)
add(impact(), 24.5, .45, 0, .5)

# S5 cash tower: 40 bricks
for i in range(40):
    t = 28 + 1.9 + i * .085 + .3
    add(thump(), t, .22, .1); add(paper(), t, .12, .3)
add(tick(3000), 33.6, .2)

# S6 cards
for i in range(3): add(thump(), 37 + 1.2 + i * 1.9, .45, -.4 + i * .4, .3); add(whoosh(.5, 600, 5000), 37 + 1.0 + i * 1.9, .2, -.4 + i * .4)

# S7 revenue bars
for i in range(8): add(tick(1200 + i * 150), 47 + .9 + i * .22, .12, -.3 + i * .08)
add(impact()[:int(1.5 * SR)], 47 + .9 + 7 * .22 + .3, .35, .3, .4)

# S8 flows: coin clinks
for k, t in enumerate(np.arange(57.2, 62.5, .18)): add(tick(3200 + (k % 5) * 300, .006), t, .06, (k % 7 - 3) / 4)

# transitions
for w in (7, 14, 22, 28, 37, 47, 55): add(whoosh(.9), w - .5, .55, 0, .25)

# build into title
add(riser(4.0), 60.0, .6, 0, .2)
for k, t in enumerate(np.arange(62.0, 63.9, .125)): add(snare(), t, .08 + k * .012, 0, .2)
add(impact(), 64.0, .5, 0, .6)
add(whoosh(1.2, 150, 3000), 63.4, .4)
# final sting: low D sustain
n = int(6 * SR); tt = np.arange(n) / SR
add(np.sin(2 * np.pi * midi(26) * tt) * np.minimum(1, tt / .05) * np.exp(-tt / 3), 64.0, .35)

# ---------------- reverb & master ----------------
irn = int(2.8 * SR); it = np.arange(irn) / SR
ir = rng.standard_normal(irn) * np.exp(-it * 2.4); ir = lp(ir, 5000)
wet = fftconvolve(RV, ir)[:N] * .06
wetL = wet; wetR = np.roll(wet, int(.013 * SR))
mixL, mixR = L + wetL, R + wetR
mix = np.stack([mixL, mixR], 1)
mix = hp(mix.T, 25).T
# fades
t = np.arange(N) / SR
fade = np.minimum(1, t / .3) * np.clip((72 - t) / 1.2, 0, 1)
mix *= fade[:, None]
body = mix[int(7*SR):int(62*SR)]; mix = mix / np.sqrt((body**2).mean()) * .13
mix = np.tanh(mix / .9) * .9
pcm = (mix * 32767).astype(np.int16)
with wave.open('score.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print('ok', pcm.shape)
