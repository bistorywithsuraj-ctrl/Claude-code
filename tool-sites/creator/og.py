"""Render the 1200x630 social share image (og.png) into dist/ and preview_dist/."""
import asyncio, pathlib, shutil
from playwright.async_api import async_playwright
HERE = pathlib.Path(__file__).parent
CARD = """<html><head><link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,800&family=Geist+Mono:wght@500&display=swap" rel="stylesheet">
<style>body{margin:0;width:1200px;height:630px;background:#F6F5F2;font-family:'Bricolage Grotesque',sans-serif;display:grid;align-content:center;padding:0 90px;box-sizing:border-box;position:relative;overflow:hidden}
.e{font:500 22px 'Geist Mono',monospace;letter-spacing:.14em;color:#8C8E96;text-transform:uppercase}.e b{color:#F0452F}
h1{font-size:92px;line-height:1;letter-spacing:-.035em;margin:22px 0;color:#111216}h1 em{font-style:normal;color:#F0452F}
.d{font:500 24px 'Geist Mono',monospace;color:#5D5F68}.dot{position:absolute;right:90px;top:80px;width:90px;height:90px;border-radius:50%;background:#F0452F;box-shadow:0 0 0 22px #FDE7E3}</style></head>
<body><i class="dot"></i><div class="e"><b>● REC</b> creatorbenchtool.com</div><h1>Free tools for<br><em>video creators</em></h1><div class="d">Script timer · Title preview · Safe zones · Captions</div></body></html>"""
async def main():
    async with async_playwright() as pw:
        b = await pw.chromium.launch(executable_path='/opt/pw-browsers/chromium-1194/chrome-linux/chrome')
        p = await b.new_page(viewport={'width': 1200, 'height': 630}); await p.set_content(CARD); await p.wait_for_timeout(2500)
        await p.screenshot(path=str(HERE / 'dist' / 'og.png')); await b.close()
    if (HERE / 'preview_dist').exists(): shutil.copy(HERE / 'dist' / 'og.png', HERE / 'preview_dist' / 'og.png')
asyncio.run(main()); print('og.png written')
