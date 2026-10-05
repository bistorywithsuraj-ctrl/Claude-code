import sys, os, base64, subprocess, asyncio, json
from playwright.async_api import async_playwright
FF = '/tmp/claude-0/-home-user-Claude-code/b8e4b5b5-0315-5db7-bd49-a5dfd041999d/scratchpad/ffmpeg'; FPS = 30
async def page(pw, rid):
    b = await pw.chromium.launch(executable_path='/opt/pw-browsers/chromium-1194/chrome-linux/chrome')
    p = await b.new_page(viewport={'width': 1080, 'height': 1920}); p.on('pageerror', lambda e: print('PAGEERROR', rid, e))
    await p.goto(f'http://localhost:8774/reel.html?id={rid}'); await p.evaluate('window.ready'); return b, p
async def grab(p, t): return await p.evaluate(f"(async () => {{ await render({t}); return document.getElementById('c').toDataURL('image/jpeg', .93); }})()")
async def stills(rid, ts):
    async with async_playwright() as pw:
        b, p = await page(pw, rid); os.makedirs(f'out/{rid}/stills', exist_ok=True)
        for t in ts: open(f'out/{rid}/stills/{float(t):05.1f}.jpg', 'wb').write(base64.b64decode((await grab(p, float(t))).split(',')[1]))
        await b.close()
async def chunk(pw, rid, i, f0, f1):
    b, p = await page(pw, rid)
    pr = subprocess.Popen([FF, '-loglevel', 'error', '-y', '-f', 'image2pipe', '-framerate', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', f'out/{rid}/seg{i}.mp4'], stdin=subprocess.PIPE)
    for f in range(f0, f1): pr.stdin.write(base64.b64decode((await grab(p, f / FPS)).split(',')[1]))
    pr.stdin.close(); pr.wait(); await b.close()
async def video(rid, n):
    dur = json.load(open(f'out/{rid}/meta.json'))['dur']; total = int(round(dur * FPS)); step = -(-total // n)
    async with async_playwright() as pw: await asyncio.gather(*[chunk(pw, rid, i, i * step, min(total, (i + 1) * step)) for i in range(n)])
    open(f'out/{rid}/segs.txt', 'w').write(''.join(f"file 'seg{i}.mp4'\n" for i in range(n)))
    subprocess.run([FF, '-loglevel', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', f'out/{rid}/segs.txt', '-c', 'copy', f'out/{rid}/silent.mp4'], check=True)
    for i in range(n): os.remove(f'out/{rid}/seg{i}.mp4')
if sys.argv[1] == 'stills': asyncio.run(stills(sys.argv[2], sys.argv[3:]))
else:
    for rid in sys.argv[3:]: asyncio.run(video(rid, int(sys.argv[2]))); print('rendered', rid, flush=True)
