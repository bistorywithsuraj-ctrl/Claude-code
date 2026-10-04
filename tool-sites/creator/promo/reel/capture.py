"""Drive the real Creator Bench pages frame by frame and save JPEG frames + an event log (keys, taps, cuts)."""
import asyncio, json, pathlib, re
from playwright.async_api import async_playwright
D = pathlib.Path('.').resolve(); OUT = D / 'live'; OUT.mkdir(exist_ok=True)
BASE = 'http://localhost:8790'
CW, CH, DPR = 430, 582, 2.5          # CSS clip -> 1075 x 1455 px, shown in a 960 x 1300 card
N = 42                               # frames per tool demo (1.4 s)
MAPN = 192                           # map render frames (6.4 s)
ease = lambda p: p * p * (3 - 2 * p)
events = {}                          # scene -> list of [frame, kind]

def text_typer(sel, text, f0, f1, clear=True):
    """type `text` into sel between frames f0..f1"""
    def act(f):
        if f < f0 or f > f1 + 1: return None
        n = len(text) if f > f1 else int(len(text) * (f - f0) / max(1, f1 - f0))
        return ('type', sel, text[:n])
    return act

TOOLS = [
 ('script-timer', dict(files=None, acts=[text_typer('#st-text', 'A Formula 1 race is about 300 km.\n\nThe car finishes it without a single drop of refuelling. Here is why.', 1, 22)],
   cam=[(0, '.panel:nth-of-type(1)', 0), (16, '.panel', 0), (32, 'PANEL1', 0)])),
 ('title-preview', dict(files=('#tp-file', ['thumb.jpg']), acts=[text_typer('#tp-title', 'I Spent 24 Hours Living Like an F1 Driver', 1, 20)],
   cam=[(0, 'PANEL0', 30), (18, 'PANEL0', 30), (32, 'PANEL1', 210)])),
 ('safe-zones', dict(files=('#sz-file', ['vert.jpg']), acts=[('click', '[data-p="tiktok"]', 6), ('click', '[data-p="reels"]', 18), ('click', '[data-p="shorts"]', 30)],
   cam=[(0, 'PANEL1', -40)])),
 ('frame-extractor', dict(files=('#fx-file', ['clip.webm']), acts=[('click', '#fx-go', 4)], slow=True,
   cam=[(0, 'PANEL1', 0), (8, 'PANEL1', 0), (22, 'PANEL2', -20)])),
 ('youtube-earnings', dict(files=None, acts=[('val', '#ye-views', v, f) for v, f in ((25000, 4), (80000, 9), (200000, 14), (450000, 19), (900000, 24), (2000000, 30))],
   cam=[(0, '#ye-views', -140), (12, '#ye-views', -140), (26, 'PANEL1', -10)])),
 ('image-resizer', dict(files=('#ir-file', ['thumb.jpg']), acts=[('opt', '#ir-preset', i, f) for i, f in ((2, 8), (4, 18), (6, 28))],
   cam=[(0, 'PANEL0', 0), (20, 'PANEL0', 0), (36, 'PANEL1', 140)])),
 ('caption-formatter', dict(files=None, acts=[text_typer('#cf-text', 'POV: you found the free tool site\n\nthat does it all in seconds.\n\nSave this for later.\n\n#creator #youtube #reels', 1, 24)],
   cam=[(0, 'PANEL0', 0), (20, 'PANEL0', 0), (34, 'PANEL1', -10)])),
 ('youtube-chapters', dict(files=None, acts=[text_typer('#yc-in', 'Intro | 0:30\nThe problem | 1:20\nThe fix | 2:05\nResults | 1:10', 1, 22)],
   cam=[(0, 'PANEL0', 60), (18, 'PANEL0', 60), (32, 'PANEL1', -10)])),
 ('srt-subtitles', dict(files=None, acts=[text_typer('#sr-in', 'Most people think F1 cars stop for fuel. They do not. Since 2010 every car starts with all the fuel it needs.', 1, 22)],
   cam=[(0, 'PANEL0', 0), (18, 'PANEL0', 0), (32, 'PANEL1', -10)])),
 ('word-counter', dict(files=None, acts=[text_typer('#wc-text', 'Write once, check every limit. YouTube titles, Instagram captions, TikTok bios and X posts, all counted live as you type.', 1, 22)],
   cam=[(0, 'PANEL0', 0), (16, 'PANEL0', 0), (30, 'PANEL1', -10)])),
 ('case-converter', dict(files=None, acts=[('type', '#cc-text', 'how f1 cars finish a race without refuelling', 0)] + [('btn', name, f) for name, f in (('Title Case', 6), ('UPPERCASE', 15), ('camelCase', 24), ('snake_case', 33))],
   cam=[(0, 'PANEL0', -10)])),
 ('qr-code', dict(files=None, acts=[text_typer('#qr-url', 'https://creatorbenchtool.com/map-animator', 1, 24)],
   cam=[(0, 'PANEL0', 60), (10, 'PANEL0', 60), (24, 'PANEL1', -10)])),
 ('pdf-tools', dict(files=('#pf-file', ['thumb.jpg', 'thumb2.jpg', 'vert.jpg']), acts=[('opt', '#pf-size', 1, 12), ('click', '#pf-go', 26)],
   cam=[(0, 'PANEL0', -10), (16, 'PANEL0', -10), (30, 'PANEL0', 120)])),
]

async def ypos(pg, target, off):
    if target.startswith('PANEL'): sel = f"document.querySelectorAll('main .panel')[{int(target[5:])}]"
    else: sel = f"document.querySelector({json.dumps(target)})"
    return await pg.evaluate(f"(() => {{ const e = {sel}; if (!e) return 0; const r = e.getBoundingClientRect(); return r.top + scrollY; }})()") + off

async def cam_y(pg, cam, f):
    if len(cam) == 1: return await ypos(pg, *cam[0][1:])
    for (fa, ta, oa), (fb, tb, ob) in zip(cam, cam[1:]):
        if f <= fb:
            a, b = await ypos(pg, ta, oa), await ypos(pg, tb, ob); return a + (b - a) * ease(max(0, min(1, (f - fa) / max(1, fb - fa))))
    return await ypos(pg, *cam[-1][1:])

async def do(pg, a, f, ev, y):
    if callable(a):
        r = a(f)
        if r: _, sel, txt = r
        else: return
        prev = await pg.evaluate(f"document.querySelector({json.dumps(sel)}).value")
        if prev != txt:
            await pg.evaluate("([s, t]) => { const e = document.querySelector(s); e.focus({preventScroll: true}); e.value = t; try { e.setSelectionRange(t.length, t.length) } catch (x) {} e.dispatchEvent(new Event('input', {bubbles: true})); }", [sel, txt])
            if len(txt) > len(prev): ev.append([f, 'key'])
        return
    kind = a[0]
    if kind == 'type' and a[3] == f:
        await pg.evaluate("([s, t]) => { const e = document.querySelector(s); e.value = t; e.dispatchEvent(new Event('input', {bubbles: true})); }", [a[1], a[2]])
    elif kind in ('click', 'btn') and a[-1] == f:
        loc = pg.locator(a[1]) if kind == 'click' else pg.get_by_role('button', name=a[1], exact=True)
        box = await loc.first.bounding_box()
        sy = await pg.evaluate('scrollY')
        if box: ev.append([f, 'tap', (box['x'] + box['width'] / 2) / CW, (box['y'] + sy + box['height'] / 2 - y) / CH])
        await loc.first.click(no_wait_after=True)
    elif kind == 'val' and a[3] == f:
        await pg.evaluate("([s, v]) => { const e = document.querySelector(s); e.value = v; e.dispatchEvent(new Event('input', {bubbles: true})); e.dispatchEvent(new Event('change', {bubbles: true})); }", [a[1], a[2]]); ev.append([f, 'tick'])
    elif kind == 'opt' and a[3] == f:
        await pg.evaluate("([s, i]) => { const e = document.querySelector(s); e.selectedIndex = i; e.dispatchEvent(new Event('input', {bubbles: true})); e.dispatchEvent(new Event('change', {bubbles: true})); }", [a[1], a[2]]); ev.append([f, 'pop'])

async def tool_scene(b, slug, spec):
    pg = await b.new_page(viewport={'width': CW, 'height': 1400}, device_scale_factor=DPR, accept_downloads=True)
    await pg.goto(f'{BASE}/{slug}.html'); await pg.evaluate('localStorage.clear()'); await pg.reload()
    await pg.add_style_tag(content='.topbar,.ad-slot,.ad,.crumbs{display:none!important} *{caret-color:#E5157A}')
    if spec['files']: await pg.set_input_files(spec['files'][0], [str(D / f) for f in spec['files'][1]]); await pg.wait_for_timeout(1500)
    await pg.wait_for_timeout(400)
    d = OUT / slug; d.mkdir(exist_ok=True); ev = []
    for f in range(N):
        y = await cam_y(pg, spec['cam'], f)
        for a in spec['acts']: await do(pg, a, f, ev, y)
        if spec.get('slow'): await pg.wait_for_timeout(90)
        await pg.screenshot(path=str(d / f'{f:03d}.jpg'), type='jpeg', quality=88, clip={'x': 0, 'y': max(0, y), 'width': CW, 'height': CH}, full_page=True)
    events[slug] = ev; await pg.close(); print(slug, len(ev))

PATCH = "  window.__ma = { draw: T => draw(T), total: () => total(), cv };\n  setRatio(); renderStops();"
async def map_scenes(b):
    pg = await b.new_page(viewport={'width': CW, 'height': 1400}, device_scale_factor=DPR)
    async def patch(route):
        r = await route.fetch(); body = (await r.text()).replace('  setRatio(); renderStops();', PATCH, 1); await route.fulfill(response=r, body=body)
    await pg.route('**/map-animator.html', patch)
    await pg.goto(f'{BASE}/map-animator.html'); await pg.evaluate('localStorage.clear()'); await pg.reload()
    await pg.add_style_tag(content='.topbar,.ad-slot,.ad,.crumbs{display:none!important} *{caret-color:#E5157A}')
    await pg.wait_for_timeout(2500)
    await pg.evaluate("document.getElementById('ma-clear').click(); document.getElementById('ma-title').value=''; document.getElementById('ma-hl').checked=false; document.getElementById('ma-leg').value='1.8';"
                      "['ma-title','ma-hl','ma-leg'].forEach(i=>document.getElementById(i).dispatchEvent(new Event('input')))")
    # scene A: typing the stops, then ticking the globe box (stops panel -> style panel)
    d = OUT / 'map-stops'; d.mkdir(exist_ok=True); ev = []
    cities = [('Mumbai', 2, 9), ('Dubai', 12, 18), ('Paris', 21, 27)]
    for f in range(N):
        for i, (c, f0, f1) in enumerate(cities):
            if f == f0 - 1:
                box = await pg.locator('#ma-add').bounding_box(); sy = await pg.evaluate('scrollY'); y = await ypos(pg, 'PANEL1', -10)
                ev.append([f, 'tap', (box['x'] + box['width'] / 2) / CW, (box['y'] + sy + box['height'] / 2 - y) / CH]); await pg.click('#ma-add')
            if f0 <= f <= f1:
                await pg.evaluate("([i, t]) => { const e = document.querySelectorAll('#ma-stops li input')[i]; e.focus({preventScroll:true}); e.value = t; e.dispatchEvent(new Event('input', {bubbles: true})); }", [i, c[:max(1, round(len(c) * (f - f0 + 1) / (f1 - f0 + 1)))]]); ev.append([f, 'key'])
        y = await ypos(pg, 'PANEL1', -10) if f < 30 else (await ypos(pg, 'PANEL1', -10)) + ((await ypos(pg, '#ma-globe', -300)) - (await ypos(pg, 'PANEL1', -10))) * ease(min(1, (f - 30) / 8))
        if f == 39:
            box = await pg.locator('#ma-globe').bounding_box(); sy = await pg.evaluate('scrollY')
            ev.append([f, 'tap', (box['x'] + box['width'] / 2) / CW, (box['y'] + sy + box['height'] / 2 - y) / CH]); await pg.check('#ma-globe')
        await pg.screenshot(path=str(d / f'{f:03d}.jpg'), type='jpeg', quality=88, clip={'x': 0, 'y': max(0, y), 'width': CW, 'height': CH}, full_page=True)
    events['map-stops'] = ev
    # scene B: the real renderer, 1080 x 1080, with live toggles
    await pg.evaluate("(() => { const m = window.__ma; m.cv.width = 1080; m.cv.height = 1080; })()")
    await pg.evaluate("new Promise(r => { const i = new Image(); i.onload = r; i.src = 'vendor/blue-marble-5400.jpg'; })")
    T = await pg.evaluate('window.__ma.total()'); spd = T / (MAPN / 30); print('map total', T, 'speed', spd)
    d = OUT / 'map-render'; d.mkdir(exist_ok=True); ev = []
    TOG = {50: "s=document.getElementById('ma-style'); s.value='satellite'; s.dispatchEvent(new Event('input'))",
           100: "h=document.getElementById('ma-hl'); h.checked=true; h.dispatchEvent(new Event('input'))",
           138: "t=document.getElementById('ma-title'); t.value='Road to Paris'; t.dispatchEvent(new Event('input'))"}
    for f in range(MAPN):
        if f in TOG:
            await pg.evaluate(TOG[f]); ev.append([f, 'toggle'])
            if f == 50: await pg.wait_for_timeout(1500)   # imagery decode
        url = await pg.evaluate(f"(() => {{ const m = window.__ma; m.cv.width = 1080; m.cv.height = 1080; m.draw({f / 30 * spd}); return m.cv.toDataURL('image/jpeg', .9); }})()")
        import base64; (d / f'{f:03d}.jpg').write_bytes(base64.b64decode(url.split(',')[1]))
    events['map-render'] = ev; print('map done')
    await pg.close()

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/opt/pw-browsers/chromium-1194/chrome-linux/chrome')
        import sys
        only = sys.argv[1:]
        if not only or 'map' in only: await map_scenes(b)
        for slug, spec in TOOLS:
            if not only or slug in only or ('from:' + slug) in only: await tool_scene(b, slug, spec)
        await b.close()
    old = json.load(open(OUT / 'events.json')) if (OUT / 'events.json').exists() else {}
    old.update(events); json.dump(old, open(OUT / 'events.json', 'w'))
asyncio.run(main())
