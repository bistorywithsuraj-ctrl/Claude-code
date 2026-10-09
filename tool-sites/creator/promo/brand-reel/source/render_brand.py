"""Brand reel renderer: `stills t1 t2 ...` or `video N` (N parallel browsers) -> silent.mp4."""
import sys, os, base64, subprocess, asyncio
from playwright.async_api import async_playwright
FF = os.environ.get('FF', 'ffmpeg'); PORT = os.environ.get('PORT', '8778'); FPS = 30; DUR = 60
async def page(pw):
    b = await pw.chromium.launch(executable_path='/opt/pw-browsers/chromium-1194/chrome-linux/chrome'); p = await b.new_page(viewport={'width': 1080, 'height': 1920})
    p.on('pageerror', lambda e: print('PAGEERROR', e)); await p.goto(f'http://localhost:{PORT}/brand.html'); await p.evaluate('window.ready'); return b, p
grab = lambda p, t: p.evaluate(f"(() => {{ render({t}); return document.getElementById('c').toDataURL('image/jpeg', .93); }})()")
async def chunk(pw, i, f0, f1):
    b, p = await page(pw)
    pr = subprocess.Popen([FF, '-loglevel', 'error', '-y', '-f', 'image2pipe', '-framerate', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p', f'seg{i}.mp4'], stdin=subprocess.PIPE)
    for f in range(f0, f1): pr.stdin.write(base64.b64decode((await grab(p, f / FPS)).split(',')[1]))
    pr.stdin.close(); pr.wait(); await b.close()
async def main():
    async with async_playwright() as pw:
        if sys.argv[1] == 'stills':
            b, p = await page(pw); os.makedirs('st', exist_ok=True)
            for t in sys.argv[2:]: open(f'st/{float(t):05.2f}.jpg', 'wb').write(base64.b64decode((await grab(p, float(t))).split(',')[1]))
            await b.close(); return
        n = int(sys.argv[2]); total = DUR * FPS; step = -(-total // n)
        await asyncio.gather(*[chunk(pw, i, i * step, min(total, (i + 1) * step)) for i in range(n)])
    open('segs.txt', 'w').write(''.join(f"file 'seg{i}.mp4'\n" for i in range(n)))
    subprocess.run([FF, '-loglevel', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', 'segs.txt', '-c', 'copy', 'silent.mp4'], check=True)
    for i in range(n): os.remove(f'seg{i}.mp4')
asyncio.run(main())
