"""Render intro.html frame-by-frame with headless Chromium and pipe to ffmpeg.
usage: python3 render.py stills t1 t2 ...   |   python3 render.py video [workers]
"""
import sys, os, base64, subprocess, asyncio
import imageio_ffmpeg
from playwright.async_api import async_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
FF = imageio_ffmpeg.get_ffmpeg_exe()
URL = 'file://' + os.path.join(HERE, 'intro.html')
FPS, DUR = 30, 72

async def page_for(pw):
    b = await pw.chromium.launch(executable_path='/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
                                 args=['--disable-web-security', '--allow-file-access-from-files'])
    p = await b.new_page(viewport={'width': 1920, 'height': 1080})
    p.on('console', lambda m: print('console:', m.text))
    p.on('pageerror', lambda e: print('PAGEERROR:', e))
    await p.goto(URL); await p.evaluate('window.ready')
    return b, p

async def grab(p, t, fmt='jpeg', q=0.95):
    return await p.evaluate(f"(render({t}), document.getElementById('c').toDataURL('image/{fmt}', {q}))")

async def stills(ts):
    async with async_playwright() as pw:
        b, p = await page_for(pw)
        os.makedirs(os.path.join(HERE, 'stills'), exist_ok=True)
        for t in ts:
            d = await grab(p, float(t), 'png')
            open(os.path.join(HERE, 'stills', f't{float(t):05.1f}.png'), 'wb').write(base64.b64decode(d.split(',')[1]))
        await b.close()

async def chunk(pw, i, f0, f1):
    b, p = await page_for(pw)
    out = os.path.join(HERE, f'seg{i}.mp4')
    proc = subprocess.Popen([FF, '-loglevel', 'error', '-y', '-f', 'image2pipe', '-framerate', str(FPS), '-i', '-',
                             '-c:v', 'libx264', '-preset', 'slow', '-crf', '15', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    for f in range(f0, f1):
        d = await grab(p, f / FPS)
        proc.stdin.write(base64.b64decode(d.split(',')[1]))
        if f % 150 == 0: print(f'worker {i}: frame {f}', flush=True)
    proc.stdin.close(); proc.wait(); await b.close()
    return out

async def video(n):
    total = FPS * DUR; step = -(-total // n)
    async with async_playwright() as pw:
        segs = await asyncio.gather(*[chunk(pw, i, i * step, min(total, (i + 1) * step)) for i in range(n)])
    lst = os.path.join(HERE, 'segs.txt')
    open(lst, 'w').write(''.join(f"file '{s}'\n" for s in segs))
    subprocess.run([FF, '-loglevel', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy',
                    os.path.join(HERE, 'video_silent.mp4')], check=True)

if __name__ == '__main__':
    if sys.argv[1] == 'stills': asyncio.run(stills(sys.argv[2:]))
    elif sys.argv[1] == 'seg':  # re-render one segment: seg <i> <f0> <f1>
        async def one():
            async with async_playwright() as pw: await chunk(pw, *map(int, sys.argv[2:5]))
        asyncio.run(one())
    else: asyncio.run(video(int(sys.argv[2]) if len(sys.argv) > 2 else 4))
