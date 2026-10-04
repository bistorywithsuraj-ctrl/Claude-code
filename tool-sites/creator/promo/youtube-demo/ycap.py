"""Record desktop live demos for the YouTube video, frame by frame, synced to the voiceover timings."""
import asyncio, json, pathlib, sys, base64
from playwright.async_api import async_playwright
D = pathlib.Path('.').resolve(); OUT = D / 'cap'; OUT.mkdir(exist_ok=True)
BASE = 'http://localhost:8790'; VW, VH, DPR, FPS = 1280, 720, 1.5, 30
CSS = ('.rail,.ad-slot,.ad{display:none!important} .wrap{grid-template-columns:minmax(0,1fr)!important;max-width:none!important} .content{max-width:none!important}'
       ' *{caret-color:#E5157A} html{scroll-behavior:auto!important}')
SC = {s['id']: s for s in json.load(open('scenes.json'))}
ease = lambda p: p * p * (3 - 2 * p)
def L(sid, i, d=0.0): s = SC[sid]; return s['vo'][i]['t0'] - s['t0'] + d
EVENTS = {}

class Scene:
    def __init__(s, sid, page, files=None, patch=False): s.sid, s.page, s.files, s.patch = sid, page, files, patch; s.cam = []; s.acts = []; s.typers = []; s.tick = None
    def at(s, t, kind, *a): s.acts.append([t, kind, a, False]); return s
    def typer(s, sel, text, t0, t1, idx=None): s.typers.append((sel, text, t0, t1, idx)); return s
    def camk(s, t, target, off=0): s.cam.append((t, (target, off))); return s

async def ypos(pg, tgt):
    target, off = tgt
    if target == 'top': return off
    if isinstance(target, (int, float)): return target + off
    if target.startswith('PANEL'): js = f"document.querySelectorAll('main .panel')[{int(target[5:])}]"
    else: js = f"document.querySelector({json.dumps(target)})"
    return await pg.evaluate(f"(() => {{ const e = {js}; if (!e) return 0; return e.getBoundingClientRect().top + scrollY; }})()") + off
async def camy(pg, cam, t):
    cam = sorted(cam, key=lambda c: c[0])
    for (ta, a), (tb, b) in zip(cam, cam[1:]):
        if t < tb:
            ya = await ypos(pg, a)
            if t <= ta: return ya
            yb = await ypos(pg, b); return ya + (yb - ya) * ease(min(1, (t - ta) / min(1.2, tb - ta)))
    return await ypos(pg, cam[-1][1])
# camera keyframes mean "arrive at target starting at t, over <=1.2s"; we model that as: hold previous until t, glide 1.2s
async def camy2(pg, cam, t):
    if not cam: return 0
    cam = sorted(cam, key=lambda c: c[0]); y = await ypos(pg, cam[0][1])
    for (tk, tgt) in cam[1:]:
        if t < tk: break
        y2 = await ypos(pg, tgt); y = y + (y2 - y) * ease(min(1, (t - tk) / 1.2))
    return y

async def tap_ev(pg, sel, ev, f, by_role=False):
    loc = pg.get_by_role('button', name=sel, exact=True).first if by_role else pg.locator(sel).first
    bb = await loc.bounding_box()
    if bb: ev.append([f, 'tap', (bb['x'] + bb['width'] / 2) / VW, (bb['y'] + bb['height'] / 2) / VH])
    return loc

async def run_act(pg, kind, a, f, ev):
    if kind == 'tap':
        loc = await tap_ev(pg, a[0], ev, f); await loc.click(no_wait_after=True)
    elif kind == 'tapname':
        loc = await tap_ev(pg, a[0], ev, f, True); await loc.click(no_wait_after=True)
    elif kind == 'ripple':   # visual tap only
        await tap_ev(pg, a[0], ev, f)
    elif kind == 'check':
        loc = await tap_ev(pg, a[0], ev, f); await loc.check()
    elif kind == 'set':      # value + events (selects, numbers)
        await pg.evaluate("([s, v]) => { const e = document.querySelector(s); if (e.tagName === 'SELECT' && typeof v === 'number') e.selectedIndex = v; else e.value = v; e.dispatchEvent(new Event('input', {bubbles: true})); e.dispatchEvent(new Event('change', {bubbles: true})); }", [a[0], a[1]])
        ev.append([f, a[2] if len(a) > 2 else 'tick'] + ([a[3]] if len(a) > 3 else []))
    elif kind == 'label': ev.append([f, 'label', a[0]])
    elif kind == 'js': await pg.evaluate(a[0])
    elif kind == 'clear':
        await pg.evaluate("s => { const e = document.querySelector(s); e.value = ''; e.dispatchEvent(new Event('input', {bubbles: true})); }", a[0])

async def record(b, sc):
    s = SC[sc.sid]; N = int(round(s['dur'] * FPS)); d = OUT / sc.sid; d.mkdir(exist_ok=True); ev = []
    pg = await b.new_page(viewport={'width': VW, 'height': VH}, device_scale_factor=DPR, accept_downloads=False)
    if sc.patch:
        async def patch(route):
            r = await route.fetch(); body = (await r.text()).replace('  setRatio(); renderStops();', "  window.__ma = { draw: T => draw(T), total: () => total(), cv };\n  setRatio(); renderStops();", 1)
            await route.fulfill(response=r, body=body)
        await pg.route('**/map-animator.html', patch)
    await pg.goto(f'{BASE}/{sc.page}.html'); await pg.evaluate('localStorage.clear()')
    if sc.setup_ls: await pg.evaluate(sc.setup_ls)
    await pg.reload(); await pg.add_style_tag(content=CSS)
    if sc.files: await pg.set_input_files(sc.files[0], [str(D / f) for f in sc.files[1]])
    await pg.wait_for_timeout(2200 if sc.patch else 1200)
    if sc.pre: await pg.evaluate(sc.pre); await pg.wait_for_timeout(600)
    for f in range(N):
        t = f / FPS
        for act in sc.acts:
            if not act[3] and t >= act[0]: act[3] = True; await run_act(pg, act[1], act[2], f, ev)
        for sel, text, t0, t1, idx in sc.typers:
            if t0 <= t <= t1 + 1 / FPS:
                n = len(text) if t >= t1 else int(len(text) * (t - t0) / (t1 - t0))
                q = f"document.querySelectorAll({json.dumps(sel)})[{idx}]" if idx is not None else f"document.querySelector({json.dumps(sel)})"
                prev = await pg.evaluate(f"{q}.value")
                if prev != text[:n]:
                    await pg.evaluate(f"(t => {{ const e = {q}; e.focus({{preventScroll: true}}); e.value = t; try {{ e.setSelectionRange(t.length, t.length) }} catch (x) {{}} e.dispatchEvent(new Event('input', {{bubbles: true}})); }})", text[:n])
                    if n > len(prev) or not text[:n].startswith(prev): ev.append([f, 'key'])
        if sc.tick: await sc.tick(pg, t, f, ev)
        y = await camy2(pg, sc.cam, t); await pg.evaluate(f"window.scrollTo(0, {max(0, y)})")
        if sc.slow: await pg.wait_for_timeout(70)
        await pg.screenshot(path=str(d / f'{f:04d}.jpg'), type='jpeg', quality=84)
    EVENTS[sc.sid] = ev; await pg.close(); print(sc.sid, N, 'frames', len(ev), 'events', flush=True)

Scene.setup_ls = None; Scene.pre = None; Scene.slow = False
SCENES = []
def add(sc): SCENES.append(sc); return sc
# ---- intro: homepage tour
sc = add(Scene('intro', 'index')); sc.camk(0, 'top', 0).camk(L('intro', 2), '#cards', -110).camk(L('intro', 3), '#cards', 360)
# ---- map: stops
MA_LS = "localStorage.setItem('ma-v1', JSON.stringify({stops: [], hl: true, globe: false, 'ma-title': 'The route', 'ma-style': 'paper', 'ma-ratio': '16:9', 'ma-cam': 'follow', 'ma-leg': '2', 'ma-color': '#D6453D', 'ma-hi': '#F3D54E'}))"
sc = add(Scene('map-stops', 'map-animator', patch=True)); sc.setup_ls = MA_LS; sc.camk(0, 'PANEL0', 330)
cities = [('Mumbai', L('map-stops', 1, .1)), ('Dubai', L('map-stops', 1, 1.3)), ('France', L('map-stops', 1, 2.7)), ('Monza', L('map-stops', 2, 2.2))]
for i, (c, t0) in enumerate(cities):
    sc.at(t0 - .35, 'tap', '#ma-add'); sc.typer('#ma-stops li input', c, t0, t0 + .7, i)
sc.at(L('map-stops', 2, .5), 'set', '#ma-stops li:nth-child(2) select', 'plane', 'pop'); sc.at(L('map-stops', 2, 1.2), 'set', '#ma-stops li:nth-child(3) select', 'train', 'pop', 'Train')
sc.at(L('map-stops', 2, 3.2), 'set', '#ma-stops li:nth-child(4) select', 'car', 'pop', 'Car')
# ---- map: styles
sc = add(Scene('map-styles', 'map-animator', patch=True)); sc.camk(0, 'PANEL0', -20)
sc.setup_ls = MA_LS.replace("stops: []", "stops: [{name:'Mumbai',mode:'plane'},{name:'Dubai',mode:'plane'},{name:'France',mode:'train'},{name:'Monza',mode:'car'}]")
for t, (v, name) in zip([L('map-styles', 1, .3), L('map-styles', 1, 1.5), L('map-styles', 1, 2.6), L('map-styles', 1, 3.6), L('map-styles', 1, 5.0)],
                        [('paper', 'Explainer paper'), ('vintage', 'Vintage atlas'), ('blueprint', 'Blueprint'), ('dark', 'Night'), ('satellite', 'Satellite · NASA imagery')]):
    sc.at(t, 'set', '#ma-style', v, 'pop', name)
sc.slow = True
# ---- map: globe intro + play
sc = add(Scene('map-globe', 'map-animator', patch=True)); sc.setup_ls = MA_LS.replace("stops: []", "stops: [{name:'Mumbai',mode:'plane'},{name:'Dubai',mode:'plane'},{name:'France',mode:'train'},{name:'Monza',mode:'car'}]").replace("'paper'", "'satellite'")
sc.camk(0, '#ma-globe', -420).camk(L('map-globe', 0, 2.0), 'PANEL0', -20)
sc.at(L('map-globe', 0, .6), 'check', '#ma-globe'); sc.at(L('map-globe', 0, .62), 'label', 'Globe intro: on')
PLAY = L('map-globe', 1, -.3); sc.at(PLAY, 'ripple', '#ma-play'); sc.at(PLAY + .05, 'js', "document.getElementById('ma-play').textContent='Stop'")
async def drive(pg, t, f, ev):
    if t >= PLAY:
        T = (t - PLAY) * 2.0
        await pg.evaluate(f"(() => {{ const m = window.__ma; m.draw(Math.min({T}, m.total())); document.getElementById('ma-bar').style.width = Math.min(100, {T} / m.total() * 100) + '%'; }})()")
sc.tick = drive; sc.slow = True; sc.pre = "new Promise(r => { const i = new Image(); i.onload = r; i.src = 'vendor/blue-marble-5400.jpg'; })"
# ---- map: export formats
sc = add(Scene('map-export', 'map-animator', patch=True)); sc.setup_ls = MA_LS.replace("stops: []", "stops: [{name:'Mumbai',mode:'plane'},{name:'Dubai',mode:'plane'},{name:'France',mode:'train'},{name:'Monza',mode:'car'}]").replace("'paper'", "'satellite'")
sc.camk(0, 'PANEL0', -20)
sc.at(L('map-export', 0, 1.4), 'set', '#ma-ratio', '9:16', 'pop', 'Format: 9:16 for Reels and Shorts'); sc.at(L('map-export', 0, 3.4), 'set', '#ma-ratio', '1:1', 'pop', 'Format: 1:1 for the feed')
sc.at(L('map-export', 1, -.2), 'set', '#ma-ratio', '16:9', 'pop', 'Format: 16:9 for YouTube'); sc.at(L('map-export', 1, .9), 'ripple', '#ma-rec'); sc.at(L('map-export', 1, 1.0), 'label', 'Exports MP4 · no watermark')
sc.slow = True
# ---- tools
sc = add(Scene('script-timer', 'script-timer')); sc.camk(0, 'PANEL0', -90).camk(L('script-timer', 2, .2), 'PANEL2', -90)
sc.at(L('script-timer', 0, .3), 'clear', '#st-text')
sc.typer('#st-text', "A Formula 1 race is about 300 kilometres long.\n\nThe car finishes it without adding a single drop of fuel. Refuelling was banned in 2010.\n\nSo every car starts the race carrying all the fuel it will ever need.", L('script-timer', 0, .5), L('script-timer', 1, .2))
sc.at(L('script-timer', 1, .9), 'tap', '[data-wpm="120"]'); sc.at(L('script-timer', 1, 1.8), 'tap', '[data-wpm="170"]')
sc = add(Scene('title-preview', 'title-preview', files=('#tp-file', ['thumb.jpg']))); sc.camk(0, 'PANEL0', -90).camk(L('title-preview', 1, 0), 'PANEL1', 120)
sc.at(L('title-preview', 0, .3), 'clear', '#tp-title'); sc.typer('#tp-title', 'I Spent 24 Hours Living Like a Formula 1 Driver (It Was Brutal)', L('title-preview', 0, .5), L('title-preview', 0, 3.0))
sc.at(L('title-preview', 1, 2.6), 'tap', '#tp-light'); sc.at(L('title-preview', 1, 4.6), 'tap', '#tp-dark')
sc = add(Scene('safe-zones', 'safe-zones', files=('#sz-file', ['vert.jpg']))); sc.camk(0, 'PANEL0', -90)
for t, p in zip([L('safe-zones', 0, 1.2), L('safe-zones', 0, 2.6), L('safe-zones', 1, .1), L('safe-zones', 1, 1.6)], ['tiktok', 'reels', 'shorts', 'all']): sc.at(t, 'tap', f'[data-p="{p}"]')
sc = add(Scene('frame-extractor', 'frame-extractor', files=('#fx-file', ['clip.webm']))); sc.camk(0, 'PANEL0', -90).camk(L('frame-extractor', 1, 1.6), 'PANEL2', -90)
sc.at(L('frame-extractor', 1, .8), 'tap', '#fx-go'); sc.slow = True
sc = add(Scene('youtube-earnings', 'youtube-earnings')); sc.camk(0, 'PANEL0', -90)
for k, v in enumerate([20000, 60000, 150000, 400000]): sc.at(L('youtube-earnings', 0, .5 + k * .55), 'set', '#ye-views', v, 'tick')
sc.at(L('youtube-earnings', 1, .3), 'set', '#ye-niche', 1, 'pop', 'Niche changed'); sc.at(L('youtube-earnings', 1, 1.8), 'set', '#ye-geo', 1, 'pop', 'Viewers: United States')
sc = add(Scene('image-resizer', 'image-resizer', files=('#ir-file', ['thumb.jpg']))); sc.camk(0, 'PANEL0', -90)
sc.at(L('image-resizer', 1, .1), 'set', '#ir-preset', 2, 'pop'); sc.at(L('image-resizer', 1, 1.4), 'set', '#ir-preset', 4, 'pop'); sc.at(L('image-resizer', 1, 2.6), 'set', '#ir-preset', 6, 'pop')
sc.at(L('image-resizer', 1, 4.4), 'set', '#ir-kb', '200', 'tick', 'Max 200 KB')
sc = add(Scene('caption-formatter', 'caption-formatter')); sc.camk(0, 'PANEL0', -90)
sc.at(L('caption-formatter', 0, .2), 'clear', '#cf-text')
sc.typer('#cf-text', "POV: you found the free tool site #creator\n\nthat does it all in seconds. #youtube #creator\n\nSave this for later.", L('caption-formatter', 0, .3), L('caption-formatter', 0, 2.6))
sc.at(L('caption-formatter', 1, .5), 'tap', '#cf-tags-end'); sc.at(L('caption-formatter', 1, 1.9), 'tap', '#cf-dedupe')
sc = add(Scene('youtube-chapters', 'youtube-chapters')); sc.camk(0, 'PANEL0', -90)
sc.at(L('youtube-chapters', 0, .2), 'clear', '#yc-in'); sc.typer('#yc-in', 'Intro | 0:30\nThe problem | 1:20\nThe fix | 2:05\nResults | 1:10', L('youtube-chapters', 0, .3), L('youtube-chapters', 0, 2.8))
sc.at(L('youtube-chapters', 1, .2), 'tap', '[data-m="check"]')
sc = add(Scene('srt-subtitles', 'srt-subtitles')); sc.camk(0, 'PANEL0', -90)
sc.at(L('srt-subtitles', 0, .2), 'clear', '#sr-in'); sc.typer('#sr-in', 'Most people think F1 cars stop for fuel. They do not. Since 2010 every car starts the race with all the fuel it needs.', L('srt-subtitles', 0, .3), L('srt-subtitles', 0, 2.6))
sc.at(L('srt-subtitles', 1, .3), 'tap', '[data-m="shift"]')
sc = add(Scene('word-counter', 'word-counter')); sc.camk(0, 'PANEL0', -90)
sc.at(.2, 'clear', '#wc-text'); sc.typer('#wc-text', 'Write once, check every limit. YouTube titles, Instagram captions, TikTok bios and X posts, all counted live as you type.', .3, 5.4)
sc = add(Scene('case-converter', 'case-converter')); sc.camk(0, 'PANEL0', -90)
sc.at(0, 'set', '#cc-text', 'how f1 cars finish a race without refuelling', 'none')
for t, n in zip([1.6, 2.6, 3.6, 4.6], ['Title Case', 'UPPERCASE', 'Sentence case', 'camelCase']): sc.at(t, 'tapname', n)
sc = add(Scene('qr-code', 'qr-code')); sc.camk(0, 'PANEL0', -90)
sc.at(L('qr-code', 0, .2), 'clear', '#qr-url'); sc.typer('#qr-url', 'https://creatorbenchtool.com/map-animator', L('qr-code', 0, .3), L('qr-code', 0, 2.2))
sc.at(L('qr-code', 0, 2.9), 'tap', '[data-t="wifi"]'); sc.at(L('qr-code', 1, .6), 'tap', '[data-t="url"]'); sc.at(L('qr-code', 1, 2.0), 'ripple', '#qr-png')
sc = add(Scene('pdf-tools', 'pdf-tools', files=('#pf-file', ['thumb.jpg', 'thumb2.jpg', 'vert.jpg']))); sc.camk(0, 'PANEL0', -90)
sc.at(L('pdf-tools', 0, 2.2), 'set', '#pf-size', 1, 'pop'); sc.at(L('pdf-tools', 0, 3.6), 'tap', '#pf-go'); sc.at(L('pdf-tools', 0, 6.0), 'tap', '[data-m="merge"]')

async def main():
    only = sys.argv[1:]
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/opt/pw-browsers/chromium-1194/chrome-linux/chrome')
        for sc in SCENES:
            if not only or sc.sid in only: await record(b, sc)
        await b.close()
    old = json.load(open(OUT / 'events.json')) if (OUT / 'events.json').exists() else {}
    old.update(EVENTS); json.dump(old, open(OUT / 'events.json', 'w'))
asyncio.run(main())
