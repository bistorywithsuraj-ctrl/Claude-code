"""Mobile live demos for the 16 reels. Times are fractions u of each reel's demo span."""
import asyncio, json, pathlib, sys, base64
from playwright.async_api import async_playwright
from spki import ARGS
D = pathlib.Path('.').resolve(); BASE = 'http://localhost:8790'; CW, CH, DPR, FPS = 430, 520, 2, 30
CSS = '.topbar,.ad-slot,.ad,.crumbs{display:none!important} *{caret-color:#E5157A}'
ease = lambda p: p * p * (3 - 2 * p)
def T(sel, text, u0, u1): return ('typer', sel, text, u0, u1)
SPEC = {
 'script-timer': dict(acts=[('clear', '#st-text', 0), T('#st-text', 'A Formula 1 race is about 300 km.\n\nThe car finishes it without a single drop of refuelling. Here is why.', .02, .5), ('tap', '[data-wpm="120"]', .62), ('tap', '[data-wpm="170"]', .85)], cam=[(0, 'PANEL0', -10), (.5, 'PANEL1', -10)]),
 'title-preview': dict(files=('#tp-file', ['thumb.jpg']), acts=[('clear', '#tp-title', 0), T('#tp-title', 'I Spent 24 Hours Living Like an F1 Driver (It Was Brutal)', .02, .5)], cam=[(0, 'PANEL0', 30), (.55, 'PANEL1', 210)]),
 'safe-zones': dict(files=('#sz-file', ['vert.jpg']), acts=[('tap', '[data-p="tiktok"]', .12), ('tap', '[data-p="reels"]', .42), ('tap', '[data-p="shorts"]', .72)], cam=[(0, 'PANEL1', -40)]),
 'frame-extractor': dict(files=('#fx-file', ['clip.webm']), acts=[('tap', '#fx-go', .1)], cam=[(0, 'PANEL1', 0), (.3, 'PANEL2', -20)], slow=True),
 'youtube-earnings': dict(acts=[('val', '#ye-views', v, u) for v, u in ((25000, .1), (80000, .22), (200000, .34), (450000, .46), (900000, .58), (2000000, .7))], cam=[(0, '#ye-views', -140), (.35, 'PANEL1', -10)]),
 'image-resizer': dict(files=('#ir-file', ['thumb.jpg']), acts=[('opt', '#ir-preset', 2, .18), ('opt', '#ir-preset', 4, .42), ('opt', '#ir-preset', 6, .62), ('val', '#ir-kb', 200, .85)], cam=[(0, 'PANEL0', 0), (.5, 'PANEL1', 140)]),
 'word-counter': dict(acts=[('clear', '#wc-text', 0), T('#wc-text', 'Write once, check every limit. YouTube titles, Instagram captions, TikTok bios and X posts, all counted live as you type.', .02, .6)], cam=[(0, 'PANEL0', 0), (.45, 'PANEL1', -10)]),
 'caption-formatter': dict(acts=[('clear', '#cf-text', 0), T('#cf-text', 'POV: you found the free tool site #creator\n\nthat does it all in seconds. #youtube #creator\n\nSave this for later.', .02, .5), ('tap', '#cf-tags-end', .62), ('tap', '#cf-dedupe', .78)], cam=[(0, 'PANEL0', 0), (.82, 'PANEL1', -10)]),
 'youtube-chapters': dict(acts=[('clear', '#yc-in', 0), T('#yc-in', 'Intro | 0:30\nThe problem | 1:20\nThe fix | 2:05\nResults | 1:10', .02, .5)], cam=[(0, 'PANEL0', 60), (.55, 'PANEL1', -10)]),
 'srt-subtitles': dict(acts=[('clear', '#sr-in', 0), T('#sr-in', 'Most people think F1 cars stop for fuel. They do not. Since 2010 every car starts with all the fuel it needs.', .02, .45)], cam=[(0, 'PANEL0', 0), (.5, 'PANEL1', -10)]),
 'case-converter': dict(acts=[('set', '#cc-text', 'how f1 cars finish a race without refuelling', 0)] + [('btn', n, u) for n, u in (('Title Case', .2), ('UPPERCASE', .4), ('Sentence case', .6), ('camelCase', .8))], cam=[(0, 'PANEL0', -10)]),
 'qr-code': dict(acts=[('clear', '#qr-url', 0), T('#qr-url', 'https://creatorbenchtool.com/map-animator', .02, .45), ('tap', '[data-t="wifi"]', .82)], cam=[(0, 'PANEL0', 60), (.4, 'PANEL1', -10)]),
 'pdf-tools': dict(files=('#pf-file', ['thumb.jpg', 'thumb2.jpg', 'vert.jpg']), acts=[('opt', '#pf-size', 1, .3), ('tap', '#pf-go', .6)], cam=[(0, 'PANEL0', -10), (.5, 'PANEL0', 120)]),
 'video-to-mp3': dict(files=('#vm-file', ['speech.webm']), acts=[('val', '#vm-start', '1.0', .2), ('opt', '#vm-kbps', 2, .42), ('tap', '#vm-go', .62)], cam=[(0, 'PANEL0', -10), (.7, 'PANEL1', -10)], slow=True),
 'auto-captions': dict(files=('#ac-file', ['speech.webm']), acts=[('tap', '#ac-go', .08)], cam=[(0, 'PANEL0', -10)], special='captions'),
 'map-animator': dict(special='map'),
}
async def ypos(pg, target, off):
    js = f"document.querySelectorAll('main .panel')[{int(target[5:])}]" if target.startswith('PANEL') else f"document.querySelector({json.dumps(target)})"
    return await pg.evaluate(f"(() => {{ const e = {js}; if (!e) return 0; return e.getBoundingClientRect().top + scrollY; }})()") + off
async def camy(pg, cam, u):
    y = await ypos(pg, *cam[0][1:])
    for (uk, tg, off) in cam[1:]:
        if u < uk: break
        y2 = await ypos(pg, tg, off); y = y + (y2 - y) * ease(min(1, (u - uk) / .12))
    return y
async def tapev(pg, loc, ev, f, y):
    bb = await loc.bounding_box(); sy = await pg.evaluate('scrollY')
    if bb: ev.append([f, 'tap', (bb['x'] + bb['width'] / 2) / CW, (bb['y'] + sy + bb['height'] / 2 - y) / CH])
async def act(pg, a, u, f, ev, y, state):
    k = a[0]
    if k == 'typer':
        _, sel, text, u0, u1 = a
        if u0 <= u <= u1 + .02:
            n = len(text) if u >= u1 else int(len(text) * (u - u0) / (u1 - u0)); prev = await pg.evaluate(f"document.querySelector({json.dumps(sel)}).value")
            if prev != text[:n]:
                await pg.evaluate("([s, t]) => { const e = document.querySelector(s); e.focus({preventScroll: true}); e.value = t; try { e.setSelectionRange(t.length, t.length) } catch (x) {} e.dispatchEvent(new Event('input', {bubbles: true})); }", [sel, text[:n]]); ev.append([f, 'key'])
        return
    if id(a) in state: return
    if u < a[-1]: return
    state.add(id(a))
    if k == 'clear': await pg.evaluate("s => { const e = document.querySelector(s); e.value = ''; e.dispatchEvent(new Event('input', {bubbles: true})); }", a[1])
    elif k == 'set': await pg.evaluate("([s, v]) => { const e = document.querySelector(s); e.value = v; e.dispatchEvent(new Event('input', {bubbles: true})); }", [a[1], a[2]])
    elif k in ('tap', 'btn'):
        loc = (pg.locator(a[1]) if k == 'tap' else pg.get_by_role('button', name=a[1], exact=True)).first; await tapev(pg, loc, ev, f, y); await loc.click(no_wait_after=True)
    elif k in ('val', 'opt'):
        await pg.evaluate("([s, v, o]) => { const e = document.querySelector(s); if (o) e.selectedIndex = v; else e.value = v; e.dispatchEvent(new Event('input', {bubbles: true})); e.dispatchEvent(new Event('change', {bubbles: true})); }", [a[1], a[2], k == 'opt']); ev.append([f, 'tick' if k == 'val' else 'pop'])
async def newpage(b):
    pg = await b.new_page(viewport={'width': CW, 'height': CH}, device_scale_factor=DPR); return pg
async def tool(b, rid, N):
    sp = SPEC[rid]; d = D / 'out' / rid / 'cap'; d.mkdir(exist_ok=True); ev = []; state = set()
    pg = await newpage(b); await pg.goto(f'{BASE}/{rid}.html'); await pg.evaluate('localStorage.clear()'); await pg.reload(); await pg.add_style_tag(content=CSS)
    if sp.get('files'): await pg.set_input_files(sp['files'][0], [str(D / f) for f in sp['files'][1]]); await pg.wait_for_timeout(1500)
    await pg.wait_for_timeout(500); done_f = None
    for f in range(N):
        u = f / N; y = await camy(pg, sp['cam'], u)
        for a in sp['acts']: await act(pg, a, u, f, ev, y, state)
        if sp.get('special') == 'captions':
            st = await pg.text_content('#ac-status')
            if done_f is None and st.startswith('Done'): done_f = f; ev.append([f, 'pop'])
            if done_f is None and u > .08: await pg.wait_for_timeout(350)
            if done_f is not None:
                y = y + ((await ypos(pg, 'PANEL1', -10)) - y) * ease(min(1, (f - done_f) / 10))
                await pg.evaluate(f"(() => {{ const v = document.getElementById('ac-video'); v.pause(); v.currentTime = {max(0, (f - done_f) / FPS)}; }})()"); await pg.wait_for_timeout(60)
        if sp.get('slow'): await pg.wait_for_timeout(70)
        await pg.evaluate(f'window.scrollTo(0, {max(0, y)})'); y = await pg.evaluate('scrollY')
        await pg.screenshot(path=str(d / f'{f:04d}.jpg'), type='jpeg', quality=86)
    await pg.close(); return ev
async def mapdemo(b, rid, N, split):
    """first part: typing stops; second part: the real renderer (globe + satellite) drawn frame by frame"""
    d = D / 'out' / rid / 'cap'; d.mkdir(exist_ok=True); ev = []
    pg = await newpage(b)
    async def patch(route):
        r = await route.fetch(); body = (await r.text()).replace('  setRatio(); renderStops();', "  window.__ma = { draw: T => draw(T), total: () => total(), cv };\n  setRatio(); renderStops();", 1); await route.fulfill(response=r, body=body)
    await pg.route('**/map-animator.html', patch)
    await pg.goto(f'{BASE}/map-animator.html'); await pg.evaluate("localStorage.setItem('ma-v1', JSON.stringify({stops: [], hl: true, globe: true, 'ma-title': '', 'ma-style': 'paper', 'ma-ratio': '16:9', 'ma-cam': 'follow', 'ma-leg': '1.8', 'ma-color': '#D6453D', 'ma-hi': '#F3D54E'}))"); await pg.reload()
    await pg.add_style_tag(content=CSS); await pg.wait_for_timeout(2500)
    cities = [('Mumbai', .04, .14), ('Dubai', .2, .3), ('Paris', .36, .46)]; NS = int(N * split)
    for f in range(NS):
        u = f / NS; y = await ypos(pg, 'PANEL1', -10)
        for i, (c, u0, u1) in enumerate(cities):
            if abs(u - (u0 - .04)) < .5 / NS:
                await tapev(pg, pg.locator('#ma-add'), ev, f, y); await pg.click('#ma-add')
            if u0 <= u <= u1:
                await pg.evaluate("([i, t]) => { const e = document.querySelectorAll('#ma-stops li input')[i]; e.focus({preventScroll:true}); e.value = t; e.dispatchEvent(new Event('input', {bubbles: true})); }", [i, c[:max(1, round(len(c) * (u - u0) / (u1 - u0)))]]); ev.append([f, 'key'])
        if abs(u - .6) < .5 / NS: await pg.evaluate("s=document.querySelectorAll('#ma-stops li select')[2]; s.value='train'; s.dispatchEvent(new Event('change'))"); ev.append([f, 'pop'])
        await pg.evaluate(f'window.scrollTo(0, {y})'); await pg.screenshot(path=str(d / f'{f:04d}.jpg'), type='jpeg', quality=86)
    await pg.evaluate("new Promise(r => { const i = new Image(); i.onload = r; i.src = 'vendor/blue-marble-5400.jpg'; })")
    NR = N - NS; Tt = await pg.evaluate('window.__ma.total()'); spd = Tt / (NR / FPS); sat_f = int(NR * .22)
    for k in range(NR):
        if k == sat_f: await pg.evaluate("s=document.getElementById('ma-style'); s.value='satellite'; s.dispatchEvent(new Event('input'))"); await pg.wait_for_timeout(1200); ev.append([NS + k, 'toggle'])
        url = await pg.evaluate(f"(() => {{ const m = window.__ma; m.cv.width = 1080; m.cv.height = 1080; m.draw({k / FPS * spd}); return m.cv.toDataURL('image/jpeg', .88); }})()")
        (d / f'{NS + k:04d}.jpg').write_bytes(base64.b64decode(url.split(',')[1]))
    await pg.close(); return ev, NS, sat_f + NS
async def main():
    only = sys.argv[1:]
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args=['--autoplay-policy=no-user-gesture-required'] + ARGS)
        for rid in SPEC:
            if only and rid not in only: continue
            m = json.load(open(f'out/{rid}/meta.json')); N = int(round((m['scenes']['demo'][1] - m['scenes']['demo'][0]) * FPS))
            if rid == 'map-animator':
                ev, ns, sat = await mapdemo(b, rid, N, .36); extra = dict(map_split=ns, sat_f=sat)
            else: ev = await tool(b, rid, N); extra = {}
            json.dump(dict(events=ev, frames=N, **extra), open(f'out/{rid}/cap.json', 'w')); print(rid, N, len(ev), flush=True)
        await b.close()
asyncio.run(main())
