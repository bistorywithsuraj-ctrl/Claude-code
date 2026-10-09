"""Renders each motion piece: stills for checking, or a 6 s looping MP4 + poster."""
import sys, asyncio, base64, subprocess, os
from playwright.async_api import async_playwright
IDS = ['slam', 'type', 'split', 'notif', 'search', 'price', 'bars', 'line', 'particles', 'orbit', 'character', 'flow']
FF = os.environ.get('FF', 'ffmpeg'); PORT = os.environ.get('PORT', '8777')
async def one(pw, i, mode, outdir):
    b = await pw.chromium.launch(executable_path='/opt/pw-browsers/chromium-1194/chrome-linux/chrome'); p = await b.new_page(viewport={'width': 540, 'height': 540})
    p.on('pageerror', lambda e: print('PAGEERROR', i, e)); await p.goto(f'http://localhost:{PORT}/motion.html?id={i}'); await p.evaluate('window.ready')
    grab = lambda t: p.evaluate(f"(() => {{ render({t}); return document.getElementById('c').toDataURL('image/jpeg', .9); }})()")
    if mode == 'stills':
        for t in (0.8, 2.0, 3.6):
            open(f'{outdir}/{i}_{t}.jpg', 'wb').write(base64.b64decode((await grab(t)).split(',')[1]))
    else:
        pr = subprocess.Popen([FF, '-loglevel', 'error', '-y', '-f', 'image2pipe', '-framerate', '30', '-i', '-', '-vf', 'scale=720:720', '-c:v', 'libx264', '-profile:v', 'main', '-preset', 'slow', '-crf', '27', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', '-an', f'{outdir}/{i}.mp4'], stdin=subprocess.PIPE)
        for f in range(180): pr.stdin.write(base64.b64decode((await grab(f / 30)).split(',')[1]))
        pr.stdin.close(); pr.wait()
        subprocess.run([FF, '-loglevel', 'error', '-y', '-ss', '2.4', '-i', f'{outdir}/{i}.mp4', '-frames:v', '1', '-vf', 'scale=480:480', '-q:v', '4', f'{outdir}/{i}.jpg'], check=True)
    await b.close()
async def main():
    mode, outdir = sys.argv[1], sys.argv[2]; os.makedirs(outdir, exist_ok=True); ids = sys.argv[3:] or IDS
    async with async_playwright() as pw:
        for k in range(0, len(ids), 4): await asyncio.gather(*[one(pw, i, mode, outdir) for i in ids[k:k + 4]])
asyncio.run(main())
