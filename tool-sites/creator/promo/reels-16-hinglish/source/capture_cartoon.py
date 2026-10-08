"""Live demo of Cartoon Characters for the Hinglish reel. Page time is virtual so animation runs at true speed."""
import asyncio, json, sys, pathlib
from playwright.async_api import async_playwright
sys.path.insert(0, sys.argv[1] + '/actest'); from spki import ARGS
BASE = 'http://localhost:8790'; CW, CH, DPR, FPS = 430, 520, 2, 30
CSS = '.topbar,.ad-slot,.ad,.crumbs,h1,.lede{display:none!important}'
M = json.load(open('out/cartoon-characters/meta.json')); D0, D1 = M['scenes']['demo']; N = int(round((D1 - D0) * FPS))
INIT = "(() => { let vt = 0; performance.now = () => vt; window.__adv = ms => { vt += ms; }; })();"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args=ARGS)
        pg = await b.new_page(viewport={'width': CW, 'height': CH}, device_scale_factor=DPR); await pg.add_init_script(INIT)
        async def patch(route):
            r = await route.fetch(); await route.fulfill(response=r, body=(await r.text()).replace('if (!chars.length) chars = [', 'if (false) chars = [', 1))
        await pg.route('**/cartoon-characters.html', patch)
        await pg.goto(f'{BASE}/cartoon-characters.html'); await pg.evaluate('localStorage.clear()'); await pg.reload(); await pg.add_style_tag(content=CSS)
        await pg.set_input_files('#cc-file', 'field.jpg'); await pg.wait_for_timeout(1200)
        y0 = await pg.evaluate("document.getElementById('cc-stage').getBoundingClientRect().top + scrollY - 12")
        out = pathlib.Path('out/cartoon-characters/cap'); out.mkdir(parents=True, exist_ok=True); ev = []; done = set()
        async def tap(loc, f):
            bb = await loc.bounding_box(); sy = await pg.evaluate('scrollY'); ev.append([f, 'tap', (bb['x'] + bb['width'] / 2) / CW, (bb['y'] + sy + bb['height'] / 2 - y0) / CH]); await loc.click()
        async def stage_xy(fx, fy):
            bb = await pg.locator('#cc-c').bounding_box(); return bb['x'] + bb['width'] * fx, bb['y'] + bb['height'] * fy
        drag_from = None
        for f in range(N):
            t = f / FPS
            for i, tk in enumerate((.5, 1.5, 2.5)):
                if t >= tk and ('add', i) not in done: done.add(('add', i)); await tap(pg.locator('#cc-pick button').nth([0, 1, 2][i]), f); await pg.evaluate("v => { const e = document.getElementById('cc-size'); e.value = v; e.dispatchEvent(new Event('input')); }", [42, 48, 36][i])
            if 3.3 <= t <= 4.6:   # drag the last character to the left side of the field
                c = await pg.evaluate("(() => { const b = document.getElementById('cc-c'); return null })()")
                if drag_from is None:
                    drag_from = await stage_xy(.5, .78); await pg.mouse.move(*drag_from); await pg.mouse.down(); ev.append([f, 'pop'])
                k = (t - 3.3) / 1.3; k = k * k * (3 - 2 * k); x, y = await stage_xy(.5 - .38 * k, .78 + .06 * k); await pg.mouse.move(x, y)
            if t > 4.6 and 'up' not in done: done.add('up'); await pg.mouse.up()
            if t >= 5.4 and 'anim' not in done: done.add('anim'); await pg.select_option('#cc-anim', 'jump'); ev.append([f, 'pop'])
            if t >= 6.6 and 'ground' not in done: done.add('ground'); await pg.check('#cc-ground'); ev.append([f, 'tick'])
            await pg.evaluate(f'window.scrollTo(0, {y0})')
            await pg.evaluate("new Promise(r => { window.__adv(1000 / 30); requestAnimationFrame(() => requestAnimationFrame(r)); })")
            await pg.screenshot(path=str(out / f'{f:04d}.jpg'), type='jpeg', quality=86)
        json.dump(dict(events=ev, frames=N), open('out/cartoon-characters/cap.json', 'w')); print('frames', N, 'events', len(ev)); await b.close()
asyncio.run(main())
