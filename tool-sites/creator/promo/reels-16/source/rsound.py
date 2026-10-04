import numpy as np, wave, json, subprocess, sys
FF = '/tmp/claude-0/-home-user-Claude-code/b8e4b5b5-0315-5db7-bd49-a5dfd041999d/scratchpad/ffmpeg'; SR = 48000
def lp(x, k):
    if k <= 1: return x
    c = np.cumsum(np.concatenate([[0.], x])); y = (c[k:] - c[:-k]) / k; p = len(x) - len(y); return np.concatenate([np.full(p // 2, y[0]), y, np.full(p - p // 2, y[-1])])
hp = lambda x: np.diff(x, prepend=0); note = lambda m: 440 * 2 ** ((m - 69) / 12); tt = lambda d: np.arange(int(d * SR)) / SR
def build(rid, seed):
    rng = np.random.default_rng(seed); M = json.load(open(f'out/{rid}/meta.json')); C = json.load(open(f'out/{rid}/cap.json')); S = M['scenes']; N = int(M['dur'] * SR)
    subprocess.run([FF, '-v', 'error', '-y', '-i', f'out/{rid}/vo.wav', '-ar', str(SR), '-ac', '1', f'out/{rid}/vo48.wav'], check=True)
    w = wave.open(f'out/{rid}/vo48.wav'); vo = np.frombuffer(w.readframes(w.getnframes()), '<i2').astype(float) / 32768; vo = np.pad(vo, (0, max(0, N - len(vo))))[:N]
    mus = np.zeros((N, 2)); sfx = np.zeros((N, 2))
    def add(buf, t, sig, g=1., pan=.5):
        s = int(t * SR)
        if s < 0 or s >= N: return
        sig = sig[:N - s]; buf[s:s + len(sig), 0] += sig * g * (1 - pan) * 1.41; buf[s:s + len(sig), 1] += sig * g * pan * 1.41
    kick = lambda g=1: (lambda t: np.sin(2 * np.pi * (45 * t + 140 / 28 * (1 - np.exp(-t * 28)))) * np.exp(-t * 7) * g)(tt(.42))
    boom = lambda: (lambda t: np.tanh(2.5 * np.sin(2 * np.pi * (36 * t + 160 / 18 * (1 - np.exp(-t * 18)))) * np.exp(-t * 1.7)))(tt(2.0))
    clap = lambda: (lambda t: hp(lp(rng.standard_normal(len(t)), 3)) * (np.exp(-t * 30) + .5 * np.exp(-((t - .012) * 300) ** 2)) * .9)(tt(.22))
    hat = lambda: (lambda t: hp(hp(rng.standard_normal(len(t)))) * np.exp(-t * 80) * .35)(tt(.06))
    tick = lambda f=2600, d=.035: (lambda t: (np.sin(2 * np.pi * f * t) * .6 + hp(rng.standard_normal(len(t))) * .3) * np.exp(-t * 140))(tt(d))
    key = lambda: (lambda t: (hp(lp(rng.standard_normal(len(t)), 2)) * .7 + np.sin(2 * np.pi * rng.uniform(1700, 2600) * t) * .25) * np.exp(-t * 220))(tt(.03))
    click = lambda: (lambda t: np.sin(2 * np.pi * 1500 * t) * np.exp(-t * 90) + .5 * np.sin(2 * np.pi * 3100 * t) * np.exp(-t * 160))(tt(.06))
    def bubble(f0=500, f1=1300, d=.12): t = tt(d); f = f0 + (f1 - f0) * (t / d) ** .5; return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 28) * (1 - np.exp(-t * 900))
    def whoosh(d=.4): t = tt(d); n = rng.standard_normal(len(t)); m = t / d; return (lp(n, 30) * (1 - m) + lp(n, 4) * m) * np.sin(np.pi * m) ** 2 * 1.4
    def scratch(d=.22): t = tt(d); return hp(lp(rng.standard_normal(len(t)), 3)) * np.abs(np.sin(2 * np.pi * 22 * t)) ** 2 * np.exp(-t * 4) * .9
    def riser(d):
        t = tt(d); n = rng.standard_normal(len(t)); out = np.zeros_like(t); seg = max(1, len(t) // 10)
        for i in range(10): a = i * seg; out[a:a + seg] = lp(n[a:a + seg], max(1, 34 - i * 3))
        return (out + np.sin(2 * np.pi * np.cumsum(220 + 900 * (t / d) ** 2) / SR) * .25) * (t / d) ** 2
    ding = lambda: (lambda t: sum(np.sin(2 * np.pi * note(m) * t) * np.exp(-t * k) * g for m, k, g in ((88, 3, .5), (95, 4, .25), (100, 6, .12))))(tt(1.4))
    def pluck(m, d=.3): t = tt(d); f = note(m); return (np.sin(2 * np.pi * f * t) + .4 * np.sign(np.sin(2 * np.pi * f * t)) * np.exp(-t * 18)) * np.exp(-t * 9) * .5
    def bass(m, d): t = tt(d); return np.tanh(1.8 * np.sin(2 * np.pi * note(m) * t)) * np.minimum(1, t * 60) * np.exp(-t * 1.2)
    # hook
    add(sfx, .05, bubble(300, 700, .1), .45); add(sfx, .45, kick(.9), .7); add(sfx, .5, bubble(350, 1400, .16), .55); add(sfx, .8, scratch(.3), .4)
    # pain: accelerating clock + card thuds + scribbles
    a, b = S['pain']; tk, iv = a, .42
    while tk < b - .35: add(sfx, tk, tick(3000 if int(tk * 7) % 2 else 2300, .03), .3); iv = max(.1, iv * .9); tk += iv
    n = len(M['pain']); pace = min(.45, (b - a - .5) / n)
    for i in range(n): t0 = a + .15 + i * pace; add(sfx, t0 - .04, whoosh(.22), .3, .7); add(sfx, t0 + .1, kick(.55), .55); add(sfx, t0 + .12, tick(1800 + i * 150, .05), .35)
    for i in range(n): add(sfx, b - .38 + i * .06, scratch(), .55, .3 + i * .12)
    t = tt(.5); add(sfx, b - .38, np.sin(2 * np.pi * 40 * t) * np.exp(-t * 4), .5)
    # turn: riser, gap, drop at demo
    ta, tb = S['turn']; add(mus, ta, riser(max(.3, tb - ta)), .7); add(sfx, ta + .25, bubble(300, 1500, .18), .55)
    D = S['demo'][0]; add(sfx, D, boom(), .85); add(sfx, D, (lambda t: hp(rng.standard_normal(len(t))) * np.exp(-t * 2.4) * .3)(tt(1.6)), .6)
    # groove from the drop to the end
    bt = 60 / 120; prog = [57, 53, 48, 55]; ch = {57: [69, 72, 76], 53: [65, 69, 72], 48: [67, 72, 76], 55: [67, 71, 74]}; k = 0; x = D; duck = np.ones(N)
    while x < M['dur'] - .6:
        root = prog[(k // 4) % 4]
        if k: add(mus, x, kick(), .8)
        s0 = int(x * SR); L = int(.16 * SR); duck[s0:s0 + L] = np.minimum(duck[s0:s0 + L], .4 + .6 * np.linspace(0, 1, L) ** 2)
        if k % 2: add(mus, x, clap(), .45)
        add(mus, x + bt / 2, hat(), .5, .62)
        if k % 4 == 0: add(mus, x, bass(root - 24, bt * 4), .32)
        for j, m in enumerate(ch[root]): add(mus, x + bt / 2, pluck(m), .12, .3 + j * .2)
        x += bt; k += 1
    # demo events
    tg = 0
    for e in C['events']:
        te = D + e[0] / 30
        if e[1] == 'key': add(sfx, te, key(), .45, rng.uniform(.35, .65))
        elif e[1] == 'tap': add(sfx, te, click(), .5)
        elif e[1] == 'tick': add(sfx, te, tick(2300, .05), .4)
        elif e[1] == 'pop': add(sfx, te, bubble(500, 1100), .5)
        elif e[1] == 'toggle': add(sfx, te - .05, click(), .45); add(sfx, te, bubble(600 + tg * 200, 1300 + tg * 250), .55); tg += 1
    # cta
    c0 = S['cta'][0]; add(sfx, c0 - .25, whoosh(.32), .5); add(sfx, c0 + .05, bubble(300, 900, .15), .5)
    for i in range(20): add(sfx, c0 + .55 + .85 * i / 20, key(), .4, rng.uniform(.4, .6))
    add(sfx, c0 + 1.42, ding(), .5); add(sfx, c0 + 1.2, bubble(400, 900), .35)
    # mix: duck under voice
    env = np.sqrt(lp(vo ** 2, int(SR * .2))); env /= env.max() + 1e-9; vduck = lp(1 - .6 * np.clip(env * 6, 0, 1), int(SR * .12))
    mus *= (duck ** .8 * vduck)[:, None]
    rev = np.zeros_like(mus)
    for d, g in [(.029, .3), (.043, .26), (.067, .22), (.101, .17), (.149, .12)]: kk = int(d * SR); rev[kk:, 0] += mus[:-kk, 1] * g; rev[kk:, 1] += mus[:-kk, 0] * g
    out = (mus + rev * .5) * .6 + sfx * .75 + np.stack([vo, vo], 1) * 1.2
    fo = int(.4 * SR); out[-fo:] *= np.linspace(1, 0, fo)[:, None]; out = np.tanh(out * 1.15); out /= np.abs(out).max() / .89
    with wave.open(f'out/{rid}/mix.wav', 'wb') as ww: ww.setnchannels(2); ww.setsampwidth(2); ww.setframerate(SR); ww.writeframes((out * 32767).astype('<i2').tobytes())
for i, rid in enumerate(sys.argv[1:]): build(rid, 100 + i); print('mixed', rid, flush=True)
