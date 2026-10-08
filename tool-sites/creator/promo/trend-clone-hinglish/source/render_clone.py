import sys, os, base64, subprocess, asyncio, json
from playwright.async_api import async_playwright
FF = sys.argv[1]; PORT = sys.argv[2]; N = int(sys.argv[3]); FPS = 30
async def chunk(pw, i, f0, f1):
    b = await pw.chromium.launch(executable_path='/opt/pw-browsers/chromium-1194/chrome-linux/chrome'); p = await b.new_page(viewport={'width': 1080, 'height': 1920})
    p.on('pageerror', lambda e: print('PAGEERROR', e)); await p.goto(f'http://localhost:{PORT}/clone.html'); await p.evaluate('window.ready')
    pr = subprocess.Popen([FF, '-loglevel', 'error', '-y', '-f', 'image2pipe', '-framerate', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', f'seg{i}.mp4'], stdin=subprocess.PIPE)
    for f in range(f0, f1): pr.stdin.write(base64.b64decode((await p.evaluate(f"(async () => {{ await render({f / FPS}); return document.getElementById('c').toDataURL('image/jpeg', .93); }})()")).split(',')[1]))
    pr.stdin.close(); pr.wait(); await b.close()
async def main():
    dur = json.load(open('meta.json'))['dur']; total = int(round(dur * FPS)); step = -(-total // N)
    async with async_playwright() as pw: await asyncio.gather(*[chunk(pw, i, i * step, min(total, (i + 1) * step)) for i in range(N)])
    open('segs.txt', 'w').write(''.join(f"file 'seg{i}.mp4'\n" for i in range(N)))
    subprocess.run([FF, '-loglevel', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', 'segs.txt', '-c', 'copy', 'silent.mp4'], check=True)
    for i in range(N): os.remove(f'seg{i}.mp4')
asyncio.run(main())
