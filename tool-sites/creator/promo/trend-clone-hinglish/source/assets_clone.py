"""Builds the footage variants and UI captures for clone.html using the live Cartoon Characters tool (local build)."""
import asyncio, json, sys, base64, pathlib, subprocess
from playwright.async_api import async_playwright
sys.path.insert(0, sys.argv[1] + '/actest'); from spki import ARGS
FF = sys.argv[1] + '/ffmpeg'; BASE = 'http://localhost:8790/cartoon-characters.html'
CHARS = [dict(kind=0, col=0, anim='dance', x=.17, y=.80, size=27, flip=False, seed=1), dict(kind=2, col=2, anim='wave', x=.47, y=.75, size=19, flip=False, seed=4),
         dict(kind=1, col=1, anim='flail', x=.8, y=.82, size=31, flip=True, seed=7)]
VARIANTS = {'plain': (0, 0, False, False), 'match': (65, 0, False, False), 'shadow': (65, 10, True, False), 'final': (65, 10, True, True)}
INIT = "(() => { let vt = 0; performance.now = () => vt; window.__adv = ms => { vt += ms; }; })();"
async def page(b, vp=(1280, 900), init=False, state=None):
    pg = await b.new_page(viewport={'width': vp[0], 'height': vp[1]}, accept_downloads=True)
    if init: await pg.add_init_script(INIT)
    await pg.goto(BASE)
    if state is not None: await pg.evaluate("s => localStorage.setItem('cc-v1', JSON.stringify(s))", state); await pg.reload()
    await pg.add_style_tag(content='.topbar,.ad-slot,.crumbs{display:none!important}'); await pg.wait_for_timeout(800); return pg
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args=ARGS)
        # 1. footage variants through the real exporter
        for name, (m, bl, sh, gr) in VARIANTS.items():
            if len(list(pathlib.Path(f'assets/fv/{name}').glob('*.jpg'))) >= 300: continue
            pg = await page(b, state=dict(chars=CHARS, match=str(m), blur=str(bl), shadow=sh, ground=gr, res='720'))
            await pg.set_input_files('#cc-file', 'fsrc.webm'); await pg.wait_for_timeout(2500)
            async with pg.expect_download(timeout=600000) as d: await pg.click('#cc-export')
            await (await d.value).save_as(f'{name}.mp4'); print(name, await pg.inner_text('#cc-msg'), flush=True); await pg.close()
            out = pathlib.Path(f'assets/fv/{name}'); out.mkdir(parents=True, exist_ok=True)
            subprocess.run([FF, '-v', 'error', '-y', '-i', f'{name}.mp4', '-vf', 'scale=960:540', '-q:v', '3', str(out / '%04d.jpg')], check=True)
        # 2. character stickers (transparent PNG from the picker canvases)
        if len(list(pathlib.Path('assets/kinds').glob('*.png'))) < 8:
          pg = await page(b, init=True); await pg.evaluate("new Promise(r => { window.__adv(400); requestAnimationFrame(() => requestAnimationFrame(r)); })")
          urls = await pg.evaluate("[...document.querySelectorAll('#cc-pick canvas')].map(c => c.toDataURL('image/png'))")
          for i, u in enumerate(urls[:8]): pathlib.Path(f'assets/kinds/{i}.png').write_bytes(base64.b64decode(u.split(',')[1]))
          await pg.close()
        # 3. site screenshot for the browser window
        pg = await page(b, vp=(1280, 960), state=dict(chars=CHARS, match='65', blur='10', shadow=True, ground=True))
        await pg.set_input_files('#cc-file', 'still.jpg'); await pg.wait_for_timeout(1500); await pg.screenshot(path='assets/site.jpg', type='jpeg', quality=88, clip=dict(x=0, y=0, width=1280, height=960)); await pg.close()
        # 4. animated character grid (60 frames, virtual clock)
        pg = await page(b, vp=(1280, 900), init=True); await pg.evaluate("document.getElementById('cc-pick').scrollIntoView({block: 'center'})"); box = await pg.locator('#cc-pick').bounding_box(); pad = 30
        clip = dict(x=box['x'] - pad, y=box['y'] - pad - 40, width=box['width'] + pad * 2, height=(box['width'] + pad * 2) * 540 / 900)
        for f in range(60):
            await pg.evaluate("new Promise(r => { window.__adv(1000 / 30); requestAnimationFrame(() => requestAnimationFrame(r)); })")
            await pg.screenshot(path=f'assets/pick/{f:04d}.jpg', type='jpeg', quality=88, clip=clip)
        await pg.close()
        # 5. drag demo on a still of the footage (stage only)
        pg = await page(b, vp=(1280, 1000), init=True, state=dict(chars=CHARS[:2], match='65', blur='10', shadow=True, ground=False))
        await pg.set_input_files('#cc-file', 'still.jpg'); await pg.wait_for_timeout(1500)
        await pg.locator('#cc-pick button').nth(1).click(); await pg.evaluate("v => { const e = document.getElementById('cc-size'); e.value = v; e.dispatchEvent(new Event('input')); }", 31)
        st = await pg.locator('#cc-c').bounding_box(); await pg.evaluate(f"window.scrollTo(0, {st['y'] - 20})"); st = await pg.locator('#cc-c').bounding_box()
        clip = dict(x=st['x'], y=st['y'], width=st['width'], height=st['width'] * 529 / 940); n = 80
        # the new character appears at its default spot; drag it to the right
        await pg.evaluate("new Promise(r => { window.__adv(200); requestAnimationFrame(() => requestAnimationFrame(r)); })")
        c = await pg.evaluate("(() => { const b = document.getElementById('cc-c'); return null })()")
        sx, sy = st['x'] + st['width'] * .5, st['y'] + st['height'] * .8
        for f in range(n):
            u = f / n
            if f == 8: await pg.mouse.move(sx, sy); await pg.mouse.down()
            if 8 < f <= 60: k = (f - 8) / 52; k = k * k * (3 - 2 * k); await pg.mouse.move(sx + st['width'] * .3 * k, sy + st['height'] * .03 * k)
            if f == 61: await pg.mouse.up()
            await pg.evaluate("new Promise(r => { window.__adv(1000 / 30); requestAnimationFrame(() => requestAnimationFrame(r)); })")
            await pg.screenshot(path=f'assets/drag/{f:04d}.jpg', type='jpeg', quality=88, clip=clip)
        await pg.close(); await b.close()
    K = {0: (74, 70, 26), 1: (50, 96, 30), 2: (64, 60, 34)}
    boxes = [[c['x'] - (K[c['kind']][0] + 40) / (K[c['kind']][1] + K[c['kind']][2] + 20) * c['size'] / 100 * 9 / 16 / 2, c['y'] - c['size'] / 100,
              (K[c['kind']][0] + 40) / (K[c['kind']][1] + K[c['kind']][2] + 20) * c['size'] / 100 * 9 / 16, c['size'] / 100] for c in CHARS]
    frames = min(len(list(pathlib.Path(f'assets/fv/{v}').glob('*.jpg'))) for v in ['raw', *VARIANTS])
    json.dump(dict(frames=frames, dragFrames=80, boxes=boxes), open('assets/assets.json', 'w')); print('frames', frames)
asyncio.run(main())
