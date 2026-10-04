"""Render the 1200x630 social share cards: dist/og.png (home) and dist/og/<slug>.png (one per tool).
Run after build.py (it re-runs the build to read the tool list)."""
import asyncio, base64, html, pathlib, runpy, shutil
from playwright.async_api import async_playwright
HERE = pathlib.Path(__file__).parent
B = runpy.run_path(str(HERE / 'build.py'))
F = HERE / 'og_fonts'
def font(fam, file, w, style='normal'):
    return f"@font-face{{font-family:{fam};src:url(data:font/woff2;base64,{base64.b64encode((F / file).read_bytes()).decode()});font-weight:{w};font-style:{style}}}"
CSS = (font('NR', 'newsreader-latin-600-normal.woff2', 600) + font('NR', 'newsreader-latin-500-italic.woff2', 500, 'italic') +
       font('GS', 'geist-sans-latin-500-normal.woff2', 500) + font('GS', 'geist-sans-latin-600-normal.woff2', 600) + """
*{box-sizing:border-box}body{margin:0;width:1200px;height:630px;background:#F3F2EA;color:#1C2A21;font-family:GS,sans-serif;position:relative;overflow:hidden}
body:before{content:"";position:absolute;inset:0;background:radial-gradient(circle at 88% 20%,rgba(220,239,128,.55),transparent 42%)}
.brand{position:absolute;left:80px;top:64px;display:flex;align-items:center;gap:16px}
.mark{width:56px;height:56px;border-radius:15px;background:#1F4D3A;display:grid;place-items:center}
.mark svg{width:30px;height:30px;stroke:#DCEF80;fill:none;stroke-width:2.2;stroke-linecap:round;stroke-linejoin:round}
.brand b{font:600 32px NR,serif;letter-spacing:-.01em}.brand small{display:block;font-size:17px;color:#87918A;margin-top:2px}
.txt{position:absolute;left:80px;top:200px;width:720px}
.eye{font:600 17px GS;letter-spacing:.14em;text-transform:uppercase;color:#2E6A4E}
h1{font:600 84px/1 NR,serif;letter-spacing:-.025em;margin:18px 0 22px}h1 em{font-style:italic;font-weight:500;color:#1F4D3A}
p{font-size:28px;line-height:1.35;color:#56625A;margin:0}
.tile{position:absolute;right:90px;top:170px;width:270px;height:270px;border-radius:64px;background:#E4EBDC;border:2px solid #D3D3C5;display:grid;place-items:center;box-shadow:0 30px 60px -30px rgba(28,42,33,.35)}
.tile svg{width:150px;height:150px;stroke:#1F4D3A;fill:none;stroke-width:1.6;stroke-linecap:round;stroke-linejoin:round}
.foot{position:absolute;left:80px;right:80px;bottom:56px;display:flex;justify-content:space-between;align-items:center}
.chips{display:flex;gap:12px}.chips span{font:600 19px GS;padding:10px 18px;border-radius:99px;background:#FBFAF5;border:1.5px solid #E2E1D6;color:#56625A}
.url{font:600 22px GS;background:#1F4D3A;color:#FBFAF5;padding:13px 26px;border-radius:99px}
""")
def svg(name): return f'<svg viewBox="0 0 24 24">{B["P"][name]}</svg>'
def card(eye, title_html, blurb, icon):
    return (f'<html><head><style>{CSS}</style></head><body><div class="brand"><span class="mark">{svg("leaf")}</span><div><b>Creator Bench</b><small>Tools for better uploads</small></div></div>'
            f'<div class="txt"><div class="eye">{html.escape(eye)}</div><h1>{title_html}</h1><p>{html.escape(blurb)}</p></div>'
            f'<div class="tile">{svg(icon)}</div><div class="foot"><div class="chips"><span>Free</span><span>No sign-up</span><span>Private</span></div><span class="url">creatorbenchtool.com</span></div></body></html>')
def split_title(t):  # last word in green italic, like the site's headings
    w = html.escape(t).rsplit(' ', 1)
    return w[0] + ' <em>' + w[1] + '</em>' if len(w) == 2 else w[0]
async def main():
    out = HERE / 'dist' / 'og'; out.mkdir(parents=True, exist_ok=True)
    jobs = [(HERE / 'dist' / 'og.png', card(f'{len(B["TOOLS"])} free tools', 'Free tools for <em>video creators</em>',
                                           'Scripts, titles, thumbnails, captions, subtitles, frames and maps. All in your browser.', 'grid'))]
    for t in B['TOOLS']:
        s = t['slug']
        jobs.append((out / f'{s}.png', card(B['CATEGORY'].get(s, 'Free tool'), split_title(B['CARD_TITLE'].get(s, t['name'])),
                                            B['BLURB'].get(s, t['desc']), B['ICON'].get(s, 'grid'))))
    async with async_playwright() as pw:
        b = await pw.chromium.launch(executable_path='/opt/pw-browsers/chromium-1194/chrome-linux/chrome')
        p = await b.new_page(viewport={'width': 1200, 'height': 630})
        for path, doc in jobs:
            await p.set_content(doc); await p.evaluate('document.fonts.ready'); await p.screenshot(path=str(path))
        await b.close()
    prev = HERE / 'preview_dist'
    if prev.exists():
        shutil.copy(HERE / 'dist' / 'og.png', prev / 'og.png'); shutil.copytree(out, prev / 'og', dirs_exist_ok=True)
    print(len(jobs), 'share cards written')
asyncio.run(main())
