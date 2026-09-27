"""Soundtrack for Small Science · F1 fuel: light plucky bed + engine, stamps, counters, paper foley."""
import numpy as np, wave, os
src = open(os.path.join(os.path.dirname(__file__), '..', 'f1-economics', 'source', 'sound.py')).read()
exec(src.split('# ---------------- arrangement')[0].replace('SR, DUR = 48000, 72.0', 'SR, DUR = 48000, 84.0'))

def pluck(freq, dur=1.0):
    n = int(dur*SR); t = np.arange(n)/SR
    s = np.sin(2*np.pi*freq*t) + .3*np.sin(2*np.pi*2*freq*t)*np.exp(-t*7)
    return s*np.minimum(1, t/.003)*np.exp(-t*4)
def slap():
    n = int(.12*SR); t = np.arange(n)/SR
    return bp(rng.standard_normal(n), 300, 5000)*np.exp(-t*45) + np.sin(2*np.pi*110*t)*np.exp(-t*35)*.4
def swish(dur=.7):
    n = int(dur*SR); x = np.linspace(0, 1, n)
    return sweep_filter(rng.standard_normal(n), 400*(8**np.sin(np.pi*x)))*np.sin(np.pi*x)**1.5*.5
def stamp_hit():
    n = int(.4*SR); t = np.arange(n)/SR
    return np.tanh((np.sin(2*np.pi*(60+80*np.exp(-t*30))*t)*np.exp(-t*10) + lp(rng.standard_normal(n), 2500)*np.exp(-t*25))*2)

# upbeat major bed, 120 BPM: C – G – Am – F
PROG = [[60, 64, 67, 72], [55, 59, 62, 67], [57, 60, 64, 69], [53, 57, 60, 65]]
for bar in range(42):
    t0 = bar*2.0; ch = PROG[bar % 4]
    for k in range(8):
        add(pluck(midi(ch[[0, 2, 1, 3, 2, 1, 3, 2][k]] + 12)), t0 + k*.25, .14 if k % 2 == 0 else .09, (k % 4 - 1.5)*.25, .3)
    add(pad_chord([m - 12 for m in ch[:3]], 2.5), t0 - .25, .08, 0, .3)
    for b in range(4): add(kick(.5), t0 + b*.5, .22 if b % 2 == 0 else 0, 0, .05)
    for b in range(8): add(hat(), t0 + b*.25 + .125, .03, .2)
    add(pluck_bass(midi(ch[0] - 24), .5), t0, .28); add(pluck_bass(midi(ch[0] - 24), .5), t0 + 1.0, .2)

# engine pass-bys (S1, S6, end)
for (t0, dur, g) in [(0.2, 6.0, .22), (60.5, 5.0, .16), (76.0, 5.0, .14)]:
    e, pan = engine(dur, dur/2); i0 = int(t0*SR); e = e[:N - i0]; pan = pan[:len(e)]
    L[i0:i0+len(e)] += e*np.cos((pan+1)*np.pi/4)*g*1.4; R[i0:i0+len(e)] += e*np.sin((pan+1)*np.pi/4)*g*1.4
# counters
for k in range(40): add(tick(1800 + k*30), 0.8 + k*.1, .05)
for k in range(24): add(tick(2000 + k*40), 22.3 + 6.2 + k*.1, .05)
for k in range(30): add(tick(1500 + k*30), 60.3 + 6.0 + k*.21, .04)
# stamps, slaps, swishes
add(stamp_hit(), 6.6, .6); add(stamp_hit(), 11.3 + 5.4, .6)
for t in [5.8, 11.5, 12.1, 17.7, 25.3, 26.9, 37.1, 41.5, 43.9, 55.5, 61.3, 66.7, 74.5, 74.9, 76.3]: add(slap(), t, .3, rng.uniform(-.4, .4), .2)
for c in [11.3, 22.3, 35.3, 47.3, 60.3, 74.3]: add(swish(), c - .35, .45, 0, .2)
# battery zap
n = int(.6*SR); tt = np.arange(n)/SR; add(np.sin(2*np.pi*(400 + 1200*tt)*tt)*np.exp(-tt*4)*.3, 47.3 + 8.2, .5, .4, .3)
add(impact()[:int(2*SR)], 74.3, .35, 0, .5)

irn = int(2.2*SR); it = np.arange(irn)/SR; ir = lp(rng.standard_normal(irn)*np.exp(-it*2.8), 5000)
wet = fftconvolve(RV, ir)[:N]*.06
mix = np.stack([L + wet, R + np.roll(wet, int(.013*SR))], 1); mix = hp(mix.T, 30).T
t = np.arange(N)/SR; mix *= (np.minimum(1, t/.4)*np.clip((84 - t)/1.5, 0, 1))[:, None]
mix = mix/np.sqrt((mix[int(2*SR):int(80*SR)]**2).mean())*.12; mix = np.tanh(mix/.9)*.9
with wave.open('f1_fuel_score.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix*32767).astype(np.int16).tobytes())
print('ok')
