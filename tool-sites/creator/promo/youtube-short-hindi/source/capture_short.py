"""Live demo of the AI Voiceover tool for the Hindi Short, timed to the narration in meta.json."""
import asyncio, json, sys, pathlib
from playwright.async_api import async_playwright
sys.path.insert(0, sys.argv[1] + '/actest'); from spki import ARGS
BASE = 'http://localhost:8790'; CW, CH, DPR, FPS = 430, 520, 2, 30
CSS = '.topbar,.ad-slot,.ad,.crumbs{display:none!important} *{caret-color:#E5157A}'
SAMPLE = 'नमस्ते! मैं Creator Bench की AI आवाज़ हूँ। आपकी script, मेरी आवाज़, बिल्कुल free।'
ease = lambda p: p * p * (3 - 2 * p)
M = json.load(open('out/ai-voiceover/meta.json')); D0, D1 = M['scenes']['demo']
smp = next(l for l in M['lines'] if l.get('sample')); vo2 = [l for l in M['lines'] if l['key'] == 'demo' and not l.get('sample')][-1]
N = int(round((D1 - D0) * FPS)); T_SAMPLE = smp['t0'] - D0; T_DL = vo2['t0'] - D0 + 1.6
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args=ARGS)
        pg = await b.new_page(viewport={'width': CW, 'height': CH}, device_scale_factor=DPR, accept_downloads=True)
        await pg.goto(f'{BASE}/ai-voiceover.html'); await pg.evaluate('localStorage.clear()'); await pg.add_style_tag(content=CSS); await pg.wait_for_timeout(1500)
        # warm up: load the model once so the recorded run is quick, then reset the page
        await pg.click('#av-voices button[data-v="hf_alpha"]'); await pg.fill('#av-text', 'नमस्ते, ये test है।'); await pg.click('#av-go')
        await pg.wait_for_function("document.getElementById('av-status').textContent.startsWith('Done')", timeout=600000)
        await pg.evaluate("""() => { document.querySelector('#av-voices button[data-v="am_michael"]').click(); const a = document.getElementById('av-audio'); a.hidden = true; a.removeAttribute('src');
          document.getElementById('av-status').textContent = 'The voice model (about 90 MB) downloads once, then works offline.'; document.getElementById('av-bar').style.width = '0%'; document.getElementById('av-dl').disabled = true;
          const t = document.getElementById('av-text'); t.value = ''; t.dispatchEvent(new Event('input')); }""")
        async def top(sel, off=0): return await pg.evaluate(f"document.querySelector({json.dumps(sel)}).getBoundingClientRect().top + scrollY") + off
        cams = [(0, await top('#av-text', -60)), (2.7, await top('#av-voices button[data-v="hf_alpha"]', -240)), (3.9, await top('#av-go', -250))]
        out = pathlib.Path('out/ai-voiceover/cap'); out.mkdir(parents=True, exist_ok=True); ev = []; did = set(); done_f = None
        async def tap(sel, f, y):
            bb = await pg.locator(sel).bounding_box(); sy = await pg.evaluate('scrollY')
            ev.append([f, 'tap', (bb['x'] + bb['width'] / 2) / CW, (bb['y'] + sy + bb['height'] / 2 - y) / CH]); await pg.click(sel, no_wait_after=True)
        for f in range(N):
            t = f / FPS; y = cams[0][1]
            for (tk, yk) in cams[1:]:
                if t >= tk: y = y + (yk - y) * ease(min(1, (t - tk) / .5))
            if .2 <= t <= 2.6:   # type the script
                n = len(SAMPLE) if t > 2.4 else int(len(SAMPLE) * (t - .2) / 2.2)
                await pg.evaluate("t => { const e = document.getElementById('av-text'); e.value = t; e.dispatchEvent(new Event('input')); }", SAMPLE[:n]); ev.append([f, 'key'])
            if t >= 3.3 and 'v' not in did: did.add('v'); await tap('#av-voices button[data-v="hf_alpha"]', f, y)
            if t >= 4.4 and 'g' not in did: did.add('g'); await tap('#av-go', f, y)
            if 'g' in did and done_f is None:
                if t >= T_SAMPLE - .1: await pg.wait_for_function("document.getElementById('av-status').textContent.startsWith('Done')", timeout=600000)
                if (await pg.text_content('#av-status')).startswith('Done'): done_f = f; ev.append([f, 'pop'])
                else: await pg.wait_for_timeout(120)
            if done_f is not None:
                await pg.evaluate(f"(() => {{ const a = document.getElementById('av-audio'); a.pause(); a.currentTime = {max(0, t - T_SAMPLE)}; }})()")
            if t >= T_DL and 'd' not in did: did.add('d'); await tap('#av-dl', f, y)
            await pg.evaluate(f'window.scrollTo(0, {max(0, y)})'); y = await pg.evaluate('scrollY')
            await pg.wait_for_timeout(25); await pg.screenshot(path=str(out / f'{f:04d}.jpg'), type='jpeg', quality=86)
        json.dump(dict(events=ev, frames=N), open('out/ai-voiceover/cap.json', 'w')); print('frames', N, 'done at', done_f, 'events', len(ev))
        await b.close()
asyncio.run(main())
