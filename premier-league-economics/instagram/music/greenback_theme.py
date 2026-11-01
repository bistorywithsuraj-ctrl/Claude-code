"""Greenback theme: an original cinematic cue for Instagram carousels and Reels.
Style brief: posh, rich, classy, in the epic-minimal film-score tradition
(ticking clock pulse, low brass swells, rising string ostinato, sparse piano).
Original composition: no melody or recording is copied from any existing work.

60 s, 72 BPM, D minor:  Dm - Bb - F - C  (i - VI - III - VII), 2 bars per chord.
Structure:  0-13 s  clock + piano + soft pad
           13-27 s  low strings ostinato enters
           27-40 s  full strings, brass swells, pulse doubles
           40-53 s  climax: brass braam on every chord, high strings
           53-60 s  resolve on D, piano alone, clock stops
Run:  python3 greenback_theme.py   ->  greenback_theme.wav (48 kHz stereo) + .m4a
"""
import numpy as np, wave, os, subprocess
from scipy.signal import fftconvolve, butter, sosfilt

SR, DUR, BPM = 48000, 60.0, 72
BEAT = 60 / BPM
N = int(SR * DUR)
L = np.zeros(N); R = np.zeros(N)
rng = np.random.default_rng(7)
midi = lambda m: 440 * 2 ** ((m - 69) / 12)

def lp(x, f, o=2): return sosfilt(butter(o, f, 'low', fs=SR, output='sos'), x)
def hp(x, f, o=2): return sosfilt(butter(o, f, 'high', fs=SR, output='sos'), x)
def bp(x, a, b): return sosfilt(butter(2, [a, b], 'band', fs=SR, output='sos'), x)

def level(t):
    """section dynamics: quiet intro, growing to full at the climax"""
    pts = [(0, .32), (13, .45), (27, .68), (40, 1.0), (53.3, 1.0), (60, .8)]
    return float(np.interp(t, [p[0] for p in pts], [p[1] for p in pts]))

def add(sig, t, gain=1.0, pan=0.0, auto=True):
    if auto: gain *= level(t)
    i = int(t * SR)
    if i >= N: return
    sig = sig[:N - i] * gain
    L[i:i + len(sig)] += sig * np.sqrt((1 - pan) / 2) * 1.414
    R[i:i + len(sig)] += sig * np.sqrt((1 + pan) / 2) * 1.414

def env(n, a, r):
    t = np.arange(n) / SR; d = n / SR
    return np.minimum(1, t / max(a, 1e-4)) * np.minimum(1, (d - t) / max(r, 1e-4))

def saw(f, n, detune=0.0):
    t = np.arange(n) / SR
    out = np.zeros(n)
    for d in (-detune, 0, detune):
        ph = (t * f * (1 + d)) % 1.0
        out += 2 * ph - 1
    return out / 3

# ---------- instruments ----------
def strings(notes, dur, bright=1800, a=1.2, r=1.4):
    n = int(dur * SR); s = np.zeros(n)
    for m in notes: s += saw(midi(m), n, .004)
    vib = 1 + .003 * np.sin(2 * np.pi * 5.2 * np.arange(n) / SR)
    s = lp(s * vib, bright, 2)
    return s * env(n, a, r) / len(notes)

def brass_braam(root, dur=3.6):
    """low brass swell: filter opens as it grows"""
    n = int(dur * SR); t = np.arange(n) / SR
    s = saw(midi(root), n, .006) + .8 * saw(midi(root + 12), n, .005) + .5 * saw(midi(root + 7), n, .004)
    cut = 200 + 2200 * np.minimum(1, t / (dur * .55)) ** 2
    out = np.zeros(n); blk = 2048
    for i in range(0, n, blk):
        seg = s[max(0, i - 512):i + blk]
        f = lp(seg, float(cut[min(i, n - 1)]), 2)
        out[i:i + blk] = f[-len(s[i:i + blk]):]
    sub = np.sin(2 * np.pi * midi(root - 12) * t)
    return (out * .6 + sub * .5) * env(n, .35, 1.6)

def piano(m, dur=3.0):
    n = int(dur * SR); t = np.arange(n) / SR; f = midi(m)
    s = sum(a * np.sin(2 * np.pi * f * k * t * (1 + .0004 * k * k)) * np.exp(-t * (1.6 + k * .9))
            for k, a in [(1, 1), (2, .45), (3, .22), (4, .1), (5, .05)])
    hammer = bp(rng.standard_normal(n), 1500, 6000) * np.exp(-t * 90) * .15
    return (s + hammer) * np.minimum(1, t / .003)

def cello_note(m, dur):
    n = int(dur * SR)
    s = lp(saw(midi(m), n, .003), 900, 2) + .4 * np.sin(2 * np.pi * midi(m - 12) * np.arange(n) / SR)
    return s * env(n, .02, .08)

def tick(hi=True):
    n = int(.05 * SR); t = np.arange(n) / SR
    click = bp(rng.standard_normal(n), 2500 if hi else 1500, 9000) * np.exp(-t * 260)
    body = np.sin(2 * np.pi * (3200 if hi else 2400) * t) * np.exp(-t * 180) * .3
    return click + body

def taiko(dur=1.2):
    n = int(dur * SR); t = np.arange(n) / SR
    f = 52 + 60 * np.exp(-t * 18)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 4.5)
    return s + lp(rng.standard_normal(n), 900) * np.exp(-t * 30) * .3

def riser(dur):
    n = int(dur * SR); x = np.linspace(0, 1, n)
    noise = bp(rng.standard_normal(n), 300, 8000)
    return hp(noise, 400) * x ** 3 * .25

# ---------- harmony ----------
# Dm, Bb, F, C (voicings around middle C, root for bass)
CHORDS = [(50, [62, 65, 69]), (46, [62, 65, 70]), (41, [60, 65, 69]), (48, [60, 64, 67])]
BAR = 4 * BEAT                 # 3.333 s
CH_LEN = 2 * BAR               # each chord holds 2 bars
SECTIONS = int(DUR / CH_LEN) + 1

# piano motif (original): a falling-then-rising figure on each chord
MOTIF = [(0, 2), (1.5, 1), (3, 0), (5, 1), (6, 2)]   # (beat, chord-tone index)

for c in range(SECTIONS):
    t0 = c * CH_LEN
    if t0 >= 54: break
    root, tones = CHORDS[c % 4]
    climax = 40 <= t0 < 53.3
    build = 27 <= t0 < 40

    # pad strings, always (wider + brighter as it builds)
    bright = 1100 if t0 < 13 else 1800 if t0 < 27 else 2800 if not climax else 3800
    add(strings([m - 12 for m in tones] + [root + 12], CH_LEN + 1.0, bright), t0, .20 if t0 < 27 else .26, -.3)
    add(strings([m for m in tones], CH_LEN + 1.0, bright), t0, .14 if t0 < 27 else .20, .3)
    if climax:
        add(strings([m + 12 for m in tones], CH_LEN + .8, 4200, a=.6), t0, .12, .5)

    # bass
    add(strings([root - 12, root], CH_LEN + .5, 500, a=.4), t0, .30)

    # cello ostinato: 16ths on root/5th/octave from 13 s
    if t0 >= 13:
        pat = [root, root + 7, root + 12, root + 7]
        step = BEAT / 4 if (build or climax) else BEAT / 2
        k = 0; t = t0
        while t < t0 + CH_LEN - .01:
            acc = 1.0 if k % 4 == 0 else .65
            add(cello_note(pat[k % 4], step * .9), t, .16 * acc, -.15 if k % 2 else .15)
            t += step; k += 1

    # brass swell
    if build and c % 2 == 0:
        add(brass_braam(root - 12, CH_LEN * .95), t0, .22)
    if climax:
        add(brass_braam(root - 12, CH_LEN * .95), t0, .32)
        for b in range(0, 8, 2): add(taiko(), t0 + b * BEAT, .45 if b == 0 else .25)

    # piano motif (sparse, high, with space)
    if t0 < 27 or t0 >= 46:
        for beat, idx in MOTIF:
            add(piano(tones[idx] + 12, 3.2), t0 + beat * BEAT, .22, .25, auto=t0 >= 27)

# ticking clock: quarter notes, eighths during the build/climax
t = 0.0
while t < 53.3:
    hi = int(round(t / BEAT * 2)) % 2 == 0
    if t < 27: add(tick(hi), t, .05 if hi else .03, .4, auto=False)
    else:
        add(tick(True), t, .07, .4, auto=False)
        add(tick(False), t + BEAT / 2, .045, -.4, auto=False)
    t += BEAT

# risers into sections, final hit
for s in (13.33, 26.67, 40.0):
    add(riser(2.4), s - 2.4, 1.0)
add(taiko(2.0), 53.33, .7); add(brass_braam(38, 6.0), 53.33, .38)
add(strings([50, 57, 62, 65, 69], 6.6, 2200, a=.05, r=4.0), 53.33, .3)
add(piano(74, 6.0), 54.0, .3, .2); add(piano(69, 5.5), 55.2, .22, -.2); add(piano(62, 4.8), 56.4, .25)

# ---------- hall reverb ----------
def reverb_ir(sec=3.2, seed=1):
    n = int(sec * SR); t = np.arange(n) / SR
    g = np.random.default_rng(seed).standard_normal(n) * np.exp(-t * 2.1)
    return lp(g, 6000) / np.sqrt(np.sum(g ** 2))
wetL = fftconvolve(L, reverb_ir(seed=1))[:N]; wetR = fftconvolve(R, reverb_ir(seed=2))[:N]
L2 = L * .78 + wetL * .55; R2 = R * .78 + wetR * .55

# master: gentle low-cut, soft clip, fade, normalise to -1 dBFS
mix = np.stack([hp(L2, 30), hp(R2, 30)])
mix = np.tanh(mix * 1.4) / np.tanh(1.4)
fade = np.ones(N); fi = int(.04 * SR); fo = int(3.0 * SR)
fade[:fi] = np.linspace(0, 1, fi); fade[-fo:] = np.linspace(1, 0, fo) ** 1.5
mix *= fade
mix /= np.max(np.abs(mix)) / 10 ** (-1 / 20)

here = os.path.dirname(os.path.abspath(__file__))
out = os.path.join(here, 'greenback_theme.wav')
with wave.open(out, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix.T * 32767).astype('<i2').tobytes())
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', out, '-c:a', 'aac', '-b:a', '256k',
                os.path.join(here, 'greenback_theme.m4a')], check=True)
print('wrote', out)
