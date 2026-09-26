"""Soundtrack for the Vox-style cold open: soft plucked bed + paper foley. 120 BPM (cuts land on beats)."""
import numpy as np, wave, os
src = open(os.path.join(os.path.dirname(__file__), '..', 'source', 'sound.py')).read()
exec(src.split('# ---------------- arrangement')[0].replace('DUR = 72.0', 'DUR = 90.0'))

def pluck(freq, dur=1.2):
    n = int(dur * SR); t = np.arange(n) / SR
    s = np.sin(2*np.pi*freq*t) + .35*np.sin(2*np.pi*2*freq*t)*np.exp(-t*6) + .12*np.sin(2*np.pi*3*freq*t)*np.exp(-t*9)
    return s * np.minimum(1, t/.004) * np.exp(-t*3.2)
def paper_slap():
    n = int(.12*SR); t = np.arange(n)/SR
    return bp(rng.standard_normal(n), 300, 5000)*np.exp(-t*45) + np.sin(2*np.pi*110*t)*np.exp(-t*35)*.4
def swish(dur=.7):
    n = int(dur*SR); x = np.linspace(0, 1, n)
    return sweep_filter(rng.standard_normal(n), 400*(8**np.sin(np.pi*x))) * np.sin(np.pi*x)**1.5 * .5

# A minor → F → C → G, arpeggiated 8ths
PROG = [[57, 60, 64, 69], [53, 57, 60, 65], [48, 55, 60, 64], [55, 59, 62, 67]]
for bar in range(45):
    t0 = bar*2.0; ch = PROG[bar % 4]
    if 84 <= t0: break
    lvl = .16 if t0 < 12 else .22
    for k in range(8):
        note = ch[[0, 2, 1, 3, 2, 1, 3, 2][k]] + 12
        add(pluck(midi(note)), t0 + k*.25, lvl*(1 if k % 2 == 0 else .7), (k % 4 - 1.5)*.25, .35)
    add(pad_chord([m - 12 for m in ch[:3]], 2.5), t0 - .25, .10, 0, .3)
    if t0 >= 12:
        for b in range(4): add(kick(.5), t0 + b*.5, .25 if b % 2 == 0 else 0, 0, .05)
        for b in range(8): add(hat(), t0 + b*.25 + .125, .03, .2)
    add(pluck_bass(midi(ch[0] - 24), .5), t0, .30)
    add(pluck_bass(midi(ch[0] - 24), .5), t0 + 1.0, .22)

# paper foley on element entrances
for t in [0.3, 1.1, 2.2, 12.2, 12.6, 18.2, 19.0, 26.3, 31.4, 33.2, 36.6, 42.2, 52.2, 64.2, 64.4, 64.7, 64.9, 65.1, 65.3, 65.6, 65.8, 78.2, 78.6, 79.0, 79.4]:
    add(paper_slap(), t + .25, .35, rng.uniform(-.4, .4), .2)
for c in [12, 26, 42, 52, 64, 78]: add(swish(), c - .35, .5, 0, .2)
# highlighter squeaks (marker)
for t in [38.2, 53.0, 53.5, 59.2, 71.4]: add(bp(rng.standard_normal(int(.35*SR)), 2500, 7000)*np.linspace(.3, 1, int(.35*SR))*.2, t, .3, .3)
# tag flip + counters
add(swish(.9), 57.1, .4); add(impact()[:int(1.5*SR)], 58.2, .35, 0, .5)
for k in range(9): add(tick(1800 + k*80), 18.6 + k*.12, .08)
for k in range(7): add(tick(2000 + k*80), 19.4 + k*.15, .08)
add(impact(), 79.4, .45, 0, .6)
n = int(8*SR); tt = np.arange(n)/SR; add(np.sin(2*np.pi*midi(33)*tt)*np.minimum(1, tt/.05)*np.exp(-tt/3), 79.4, .3)

irn = int(2.5*SR); it = np.arange(irn)/SR; ir = lp(rng.standard_normal(irn)*np.exp(-it*2.6), 5000)
wet = fftconvolve(RV, ir)[:N]*.06
mix = np.stack([L + wet, R + np.roll(wet, int(.013*SR))], 1); mix = hp(mix.T, 30).T
t = np.arange(N)/SR; mix *= (np.minimum(1, t/.4)*np.clip((90 - t)/1.5, 0, 1))[:, None]
body = mix[int(12*SR):int(78*SR)]; mix = mix/np.sqrt((body**2).mean())*.12; mix = np.tanh(mix/.9)*.9
with wave.open('cold_open_score.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix*32767).astype(np.int16).tobytes())
print('ok')
