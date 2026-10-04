import sys, os, base64, subprocess, asyncio, json
from playwright.async_api import async_playwright
FF = '/tmp/claude-0/-home-user-Claude-code/b8e4b5b5-0315-5db7-bd49-a5dfd041999d/scratchpad/ffmpeg'
URL = 'http://localhost:8771/yt.html'; FPS = 30; _S = json.load(open('scenes.json')); DUR = _S[-1]['t0'] + _S[-1]['dur']
async def page(pw):
    b = await pw.chromium.launch(executable_path='/opt/pw-browsers/chromium-1194/chrome-linux/chrome')
    p = await b.new_page(viewport={'width': 1920, 'height': 1080}); p.on('pageerror', lambda e: print('PAGEERROR', e))
    await p.goto(URL); await p.evaluate('window.ready'); return b, p
async def grab(p, t, fmt='jpeg'): return await p.evaluate(f"(async () => {{ await render({t}); return document.getElementById('c').toDataURL('image/{fmt}', .95); }})()")
async def stills(ts):
    async with async_playwright() as pw:
        b, p = await page(pw); os.makedirs('stills', exist_ok=True)
        for t in ts: open(f'stills/{float(t):06.2f}.jpg', 'wb').write(base64.b64decode((await grab(p, float(t))).split(',')[1]))
        await b.close()
async def chunk(pw, i, f0, f1):
    b, p = await page(pw)
    pr = subprocess.Popen([FF, '-loglevel', 'error', '-y', '-f', 'image2pipe', '-framerate', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p', f'yseg{i}.mp4'], stdin=subprocess.PIPE)
    for f in range(f0, f1):
        pr.stdin.write(base64.b64decode((await grab(p, f / FPS)).split(',')[1]))
        if f % 150 == 0: print('w', i, f, flush=True)
    pr.stdin.close(); pr.wait(); await b.close()
async def video(n):
    total = int(round(DUR * FPS)); step = -(-total // n)
    async with async_playwright() as pw: await asyncio.gather(*[chunk(pw, i, i * step, min(total, (i + 1) * step)) for i in range(n)])
    open('ysegs.txt', 'w').write(''.join(f"file 'yseg{i}.mp4'\n" for i in range(n)))
    subprocess.run([FF, '-loglevel', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', 'ysegs.txt', '-c', 'copy', 'yt_silent.mp4'], check=True)
if sys.argv[1] == 'stills': asyncio.run(stills(sys.argv[2:]))
else: asyncio.run(video(int(sys.argv[2])))
