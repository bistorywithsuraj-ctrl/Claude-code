"""`stills t1 t2 ...` -> st/*.jpg, `video N` -> silent.mp4 (N parallel browsers)."""
import sys, os, base64, subprocess, asyncio
from playwright.async_api import async_playwright
FF = os.environ.get('FF', 'ffmpeg'); PORT = os.environ.get('PORT', '8781'); FPS = int(os.environ.get('FPS', '60')); DUR = 244.2
async def page(pw):
    b = await pw.chromium.launch(**({'executable_path': os.environ['CHROME']} if os.environ.get('CHROME') else {})); p = await b.new_page(viewport={'width': 1920, 'height': 1080})
    p.on('pageerror', lambda e: print('PAGEERROR', e)); p.on('console', lambda m: m.type == 'error' and print('CONSOLE', m.text)); await p.goto(f'http://localhost:{PORT}/mv.html'); await p.evaluate('window.ready'); return b, p
grab = lambda p, t, q=.92: p.evaluate(f"(() => {{ render({t}); return document.getElementById('c').toDataURL('image/jpeg', {q}); }})()")
async def chunk(pw, i, f0, f1):
    b, p = await page(pw)
    pr = subprocess.Popen([FF, '-loglevel', 'error', '-y', '-f', 'image2pipe', '-framerate', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-pix_fmt', 'yuv420p', f'seg{i}.mp4'], stdin=subprocess.PIPE)
    for f in range(f0, f1):
        pr.stdin.write(base64.b64decode((await grab(p, f / FPS)).split(',')[1]))
        if (f - f0) % 300 == 0: print(f'chunk {i}: {f - f0}/{f1 - f0}', flush=True)
    pr.stdin.close(); pr.wait(); await b.close()
async def main():
    async with async_playwright() as pw:
        if sys.argv[1] == 'stills':
            b, p = await page(pw); os.makedirs('st', exist_ok=True)
            for t in sys.argv[2:]: open(f'st/{float(t):06.2f}.jpg', 'wb').write(base64.b64decode((await grab(p, float(t), .8)).split(',')[1]))
            await b.close(); return
        n = int(sys.argv[2]); a = float(sys.argv[3]) if len(sys.argv) > 3 else 0; z = float(sys.argv[4]) if len(sys.argv) > 4 else DUR
        f0, total = int(a * FPS), int(z * FPS); step = -(-(total - f0) // n)
        await asyncio.gather(*[chunk(pw, i, f0 + i * step, min(total, f0 + (i + 1) * step)) for i in range(n)])
    open('segs.txt', 'w').write(''.join(f"file 'seg{i}.mp4'\n" for i in range(n)))
    subprocess.run([FF, '-loglevel', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', 'segs.txt', '-c', 'copy', 'silent.mp4'], check=True)
asyncio.run(main())
