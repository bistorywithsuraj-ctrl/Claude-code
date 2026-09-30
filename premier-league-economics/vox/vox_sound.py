"""Soundtrack for the Premier League cold open: soft plucked bed + paper foley + a stamp thud. 120 BPM (cuts land on beats).
Reuses the synth from ../source/sound.py (same instruments as Episode 1) with a D-minor progression so the two episodes sound related, not identical."""
import numpy as np, wave, os
src = open(os.path.join(os.path.dirname(__file__), '..', 'source', 'sound.py')).read()
exec(src.split('# ---------------- arrangement')[0].replace('SR, DUR = 48000, 72.0', 'SR, DUR = 48000, 90.0'))

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
def stamp_thud():  # rubber stamp hitting card stock
    n = int(.25*SR); t = np.arange(n)/SR
    return (np.sin(2*np.pi*(90 + 70*np.exp(-t*50))*t)*np.exp(-t*26) + lp(rng.standard_normal(n), 1500)*np.exp(-t*60)*.7)

# D minor → Bb → F → C, arpeggiated 8ths
PROG = [[62, 65, 69, 74], [58, 62, 65, 70], [53, 60, 65, 69], [60, 64, 67, 72]]
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

# paper foley on element entrances (scene-local times + scene start, see cold_open.html)
ENTRANCES = [0.3, 1.1, 2.2,                        # S1 photo, card, shop photo
             12.2, 12.7, 18.2, 18.8, 19.4,         # S2 cutout, headline, three counters
             26.3, 27.6, 28.9, 32.2,               # S3 three cards, clipping
             42.2,                                  # S4 clip frame
             52.2,                                  # S5 price tag
             64.2, 64.4, 64.6, 64.7, 64.9, 65.1, 65.3, 65.5, 65.6, 65.8,  # S6 ten logo cards
             78.2, 78.6, 79.0, 79.4]               # S7 title pieces
for t in ENTRANCES: add(paper_slap(), t + .25, .35, rng.uniform(-.4, .4), .2)
for c in [12, 26, 42, 52, 64, 78]: add(swish(), c - .35, .5, 0, .2)
# the sanctions stamp (S1, t=7.2) and the frost that follows
add(stamp_thud(), 7.25, .55, .3, .3); add(impact()[:int(1.2*SR)], 7.25, .18, 0, .4)
# highlighter squeaks (marker)
for t in [14.8, 37.4, 53.0, 53.3, 53.6, 59.2, 71.4]: add(bp(rng.standard_normal(int(.35*SR)), 2500, 7000)*np.linspace(.3, 1, int(.35*SR))*.2, t, .3, .3)
# trophy counters tick up
for k in range(5): add(tick(1800 + k*80), 18.6 + k*.16, .08)
for k in range(2): add(tick(2000 + k*80), 19.2 + k*.2, .08)
for k in range(12): add(tick(2200 + k*50), 19.8 + k*.09, .07)
# 90-day countdown ticks (S3)
for k in range(24): add(tick(1500, .008), 31.9 + k*.3, .05, -.3)
# tag flip + ×18 impact
add(swish(.9), 57.1, .4); add(impact()[:int(1.5*SR)], 59.4, .35, 0, .5)
# title impact + sub-bass
add(impact(), 79.4, .45, 0, .6)
n = int(8*SR); tt = np.arange(n)/SR; add(np.sin(2*np.pi*midi(38)*tt)*np.minimum(1, tt/.05)*np.exp(-tt/3), 79.4, .3)

irn = int(2.5*SR); it = np.arange(irn)/SR; ir = lp(rng.standard_normal(irn)*np.exp(-it*2.6), 5000)
wet = fftconvolve(RV, ir)[:N]*.06
mix = np.stack([L + wet, R + np.roll(wet, int(.013*SR))], 1); mix = hp(mix.T, 30).T
t = np.arange(N)/SR; mix *= (np.minimum(1, t/.4)*np.clip((90 - t)/1.5, 0, 1))[:, None]
body = mix[int(12*SR):int(78*SR)]; mix = mix/np.sqrt((body**2).mean())*.12; mix = np.tanh(mix/.9)*.9
with wave.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cold_open_score.wav'), 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix*32767).astype(np.int16).tobytes())
print('ok')
