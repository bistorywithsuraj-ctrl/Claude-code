"""Build the creator-tools website into ./dist (plain static files, no backend).

  python3 build.py
  SITE_NAME="Creator Bench" SITE_URL=https://yourdomain.com CONTACT_EMAIL=hello@yourdomain.com \
  ADSENSE_CLIENT=ca-pub-1234567890123456 python3 build.py     # after AdSense approval

Ads: with ADSENSE_CLIENT set, real ad units are placed in every slot. Without it, slots are left out
of the live site; the Claude preview (preview_index.html + dist) shows labelled placeholders so you
can judge the layout.

Each tool lives in src/<slug>.html with a <!--meta ... --> header. Add a file there and rebuild
to add a tool: it gets its own page, a card on the homepage, a nav link and a sitemap entry.
"""
import os, re, json, html, datetime, pathlib

HERE = pathlib.Path(__file__).parent
PREVIEW = os.environ.get('PREVIEW', '0') == '1'   # PREVIEW=1: .html links + ad placeholders, for the Claude preview
DIST = HERE / ('preview_dist' if PREVIEW else 'dist')
NAME = os.environ.get('SITE_NAME', 'Creator Bench')
SITE_URL = os.environ.get('SITE_URL', 'https://example.com').rstrip('/')
CLIENT = os.environ.get('ADSENSE_CLIENT', '').strip()
EMAIL = os.environ.get('CONTACT_EMAIL', 'hello@example.com')
PLACEHOLDERS = PREVIEW and not CLIENT
AUTHOR = os.environ.get('AUTHOR_NAME', 'Suraj Shukla')
AUTHOR_URL = os.environ.get('AUTHOR_URL', 'https://bistorywithsuraj.com')
TODAY = datetime.date.today()
BASE_CSS = (HERE / 'shared' / 'base.css').read_text()
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,700;12..96,800&family=Geist:wght@400;500;600;700&family=Geist+Mono:wght@500;600&display=swap">')
ORDER = ['script-timer', 'title-preview', 'safe-zones', 'caption-formatter']
SHORT = {'script-timer': 'Script Timer', 'title-preview': 'Title Preview', 'safe-zones': 'Safe Zones', 'caption-formatter': 'Captions'}

def load_tools():
    tools = []
    for f in sorted((HERE / 'src').glob('*.html')):
        s = f.read_text()
        m = re.match(r'<!--meta\n(.*?)\n-->\n', s, re.S)
        meta = dict(l.split(': ', 1) for l in m.group(1).splitlines())
        meta['body'] = s[m.end():]
        meta['faq'] = [(html.unescape(re.sub('<[^>]+>', '', q)), html.unescape(re.sub('<[^>]+>', '', a)))
                       for q, a in re.findall(r'<summary>(.*?)</summary><p>(.*?)</p>', s)]
        tools.append(meta)
    tools.sort(key=lambda t: ORDER.index(t['slug']) if t['slug'] in ORDER else 99)
    return tools

TOOLS = load_tools()
first, rest = NAME.split(' ', 1) if ' ' in NAME else (NAME, '')

def header(active=None):
    cur = ' aria-current="page"'
    nav = ''.join(f'<a href="{t["slug"]}.html"{cur if t["slug"] == active else ""}>{html.escape(SHORT.get(t["slug"], t["name"]))}</a>' for t in TOOLS)
    return (f'<header class="site-head"><div class="in"><a class="brand" href="index.html"><i class="dot" aria-hidden="true"></i>{html.escape(first)}<span>{html.escape(rest)}</span></a>'
            f'<nav class="nav" aria-label="Tools">{nav}</nav></div></header>')

FOOT = f'''<footer class="site-foot"><div class="in">
<div><a class="brand" href="index.html"><i class="dot" aria-hidden="true"></i>{html.escape(first)}<span>{html.escape(rest)}</span></a>
<p>Free tools for YouTube, Shorts, Reels and TikTok creators. Everything runs in your browser. Not affiliated with YouTube, Instagram or TikTok.</p></div>
<div><h4>Tools</h4>{''.join(f'<a href="{t["slug"]}.html">{html.escape(t["name"])}</a>' for t in TOOLS)}</div>
<div><h4>Site</h4><a href="about.html">About</a><a href="privacy.html">Privacy</a><a href="terms.html">Terms</a><a href="contact.html">Contact</a><p>© {TODAY.year} {html.escape(NAME)} · Made by <a href="{AUTHOR_URL}" style="display:inline">{html.escape(AUTHOR)}</a></p></div>
</div></footer>'''

def ad(kind):
    """kind: leader (banner), inline (in-content), tower (300x600 rail)."""
    if CLIENT:
        fmt = 'data-ad-format="auto" data-full-width-responsive="true"' if kind != 'tower' else 'style="display:inline-block;width:300px;height:600px"'
        style = '' if kind == 'tower' else ' style="display:block"'
        return (f'<div class="ad {kind}"><div class="box"><ins class="adsbygoogle"{style} data-ad-client="{CLIENT}" {fmt}></ins>'
                '<script>(adsbygoogle = window.adsbygoogle || []).push({});</script></div></div>')
    if PLACEHOLDERS:
        size = {'leader': '728 × 90 / responsive', 'inline': '336 × 280 / responsive', 'tower': '300 × 600'}[kind]
        return f'<div class="ad {kind}"><div class="box ph">Ad slot · {size}</div></div>'
    return ''

def head(title, desc, path, extra=''):
    ads = (f'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={CLIENT}" crossorigin="anonymous"></script>' if CLIENT else '')
    return f'''<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{SITE_URL}{path}">
<meta property="og:title" content="{html.escape(title)}"><meta property="og:description" content="{html.escape(desc)}">
<meta property="og:type" content="website"><meta property="og:url" content="{SITE_URL}{path}">
<meta property="og:image" content="{SITE_URL}/og.png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:image" content="{SITE_URL}/og.png">
<meta name="theme-color" content="#F0452F">{'<meta name="robots" content="noindex">' if path == "/404" else ""}
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='16' fill='%23111216'/%3E%3Ccircle cx='32' cy='32' r='12' fill='%23F0452F'/%3E%3C/svg%3E">
{FONTS}{ads}
<style>{BASE_CSS}</style>{extra}'''

def full(title, desc, path, main, extra='', active=None):
    return (f'<!doctype html>\n<html lang="en">\n<head>\n{head(title, desc, path, extra)}\n</head>\n<body>\n{header(active)}\n'
            f'<div class="wrap">{main}</div>\n{FOOT}\n</body>\n</html>\n')

def write(path, doc): (DIST / path).write_text(clean_links(doc))

def clean_links(doc):
    if PREVIEW: return doc
    doc = re.sub(r'href="index\.html"', 'href="/"', doc)
    return re.sub(r'href="([a-z0-9-]+)\.html"', r'href="/\1"', doc)

def crumbs(items):
    """items: [(label, path or None)] -> visible breadcrumb + BreadcrumbList JSON-LD"""
    vis = '<nav class="crumbs" aria-label="Breadcrumb"><a href="index.html">Home</a>' + ''.join(
        f' <span aria-hidden="true">/</span> ' + (f'<a href="{p}.html">{html.escape(l)}</a>' if p else f'<span aria-current="page">{html.escape(l)}</span>') for l, p in items) + '</nav>'
    data = {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement':
            [{'@type': 'ListItem', 'position': 1, 'name': 'Home', 'item': SITE_URL + '/'}] +
            [{'@type': 'ListItem', 'position': i + 2, 'name': l, **({'item': f'{SITE_URL}/{p}'} if p else {})} for i, (l, p) in enumerate(items)]}
    return vis, ld(data)

def ld(obj): return f'<script type="application/ld+json">{json.dumps(obj)}</script>'

DIST.mkdir(exist_ok=True)
# ---------- tool pages: content column + sticky ad rail ----------
for t in TOOLS:
    body = t['body']
    bc_vis, bc_ld = crumbs([(t['name'], None)])
    body = re.sub(r'<h1>', f'{bc_vis}<span class="eyebrow"><b>●</b> Free tool · No sign-up</span><h1>', body, count=1)
    body = body.replace('<div class="ad-slot" data-slot="top"></div>', ad('leader'))
    body = body.replace('<div class="ad-slot" data-slot="mid"></div>', ad('inline'))
    others = [o for o in TOOLS if o is not t]
    body += ('<section class="copy"><h2>More free tools</h2><ul>' +
             ''.join(f'<li><a href="{o["slug"]}.html">{html.escape(o["name"])}</a>: {html.escape(o["desc"].split(".")[0])}.</li>' for o in others) + '</ul></section>')
    rail = (f'<aside class="rail" aria-label="Sidebar">{ad("tower")}<div class="more"><h3>Other tools</h3>' +
            ''.join(f'<a href="{o["slug"]}.html">{html.escape(o["name"])}</a>' for o in others) + '</div></aside>')
    main = f'<div class="layout"><main class="content">{body}</main>{rail}</div>'
    extra = bc_ld + ld({'@context': 'https://schema.org', '@type': 'WebApplication', 'name': t['name'], 'url': f'{SITE_URL}/{t["slug"]}',
                'applicationCategory': 'MultimediaApplication', 'operatingSystem': 'Any', 'description': t['desc'],
                'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'USD'}})
    if t['faq']:
        extra += ld({'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
            {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in t['faq']]})
    write(f'{t["slug"]}.html', full(t['title'], t['desc'], f'/{t["slug"]}', main, extra, active=t['slug']))

# ---------- homepage ----------
# small code-drawn previews of each tool (no images needed)
VIS = {
 'script-timer': '<div class="vis v-script"><i style="width:92%"></i><i style="width:74%"></i><i style="width:86%"></i><i style="width:40%"></i><b>4:12</b></div>',
 'title-preview': '<div class="vis"><div class="v-title"><div class="th"><span>14:07</span></div><div class="ln"></div><div class="ln short"></div><div class="cut">…</div></div></div>',
 'safe-zones': '<div class="vis v-safe"><div class="ph9"><i class="t"></i><i class="r"></i><i class="b"></i><em></em></div></div>',
 'caption-formatter': '<div class="vis v-cap"><div class="bub"><b>yourhandle</b> Your phone costs more than you think.<br><br>We did the maths<span>… more</span></div><div class="cnt">147 / 2,200</div></div>',
}
cards = ''.join(f'''<a class="tool-card" href="{t["slug"]}.html">{VIS.get(t["slug"], "")}<div class="tc-body"><h3>{html.escape(t["name"])}</h3><p>{html.escape(t["desc"].split(". ")[0])}.</p><span class="go">Open tool <span aria-hidden="true">→</span></span></div></a>''' for t in TOOLS)
HOME_CSS = '''<style>
.home-hero { padding-block: 72px 32px; display: grid; gap: 18px; max-width: 900px }
.home-hero h1 { font-size: clamp(44px, 7.4vw, 92px) }
.home-hero .tc { display: flex; flex-wrap: wrap; gap: 8px 18px; margin-top: 6px; font: 500 13px var(--mono); color: var(--ink-3) }
.home-hero .tc span::before { content: "✓ "; color: var(--ok) }
.tools { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 260px), 1fr)); gap: 18px }
.tool-card { background: var(--surface); border: 1px solid var(--line); border-radius: 20px; overflow: hidden; text-decoration: none; color: inherit; display: grid; grid-template-rows: auto 1fr; box-shadow: var(--shadow); transition: transform .2s, box-shadow .2s, border-color .2s }
.tool-card:hover { transform: translateY(-3px); box-shadow: var(--shadow-lg); border-color: var(--line-2) }
.tc-body { padding: 18px 20px 20px; display: grid; gap: 8px; align-content: start }
.tc-body h3 { margin: 0; font: 700 21px/1.15 var(--display); letter-spacing: -.02em }
.tc-body p { margin: 0; color: var(--ink-2); font-size: 15px }
.tc-body .go { font-weight: 600; font-size: 14px; color: var(--rec); margin-top: 4px }
.vis { height: 150px; background: var(--bg-2); border-bottom: 1px solid var(--line); position: relative; overflow: hidden; display: grid; place-items: center }
.v-script { place-items: start; align-content: center; gap: 9px; padding: 0 22px }
.v-script i { display: block; height: 8px; border-radius: 4px; background: var(--line-2) }
.v-script b { position: absolute; right: 18px; bottom: 14px; font: 800 34px var(--display); letter-spacing: -.03em; color: var(--rec) }
.v-title { width: 70%; display: grid; gap: 7px; justify-items: start; position: relative }
.v-title .th { width: 100%; aspect-ratio: 16/9; max-height: 82px; border-radius: 8px; background: linear-gradient(135deg, var(--ink) 0%, var(--ink-2) 100%); position: relative }
.v-title .th span { position: absolute; right: 5px; bottom: 5px; background: #000; color: #fff; font: 500 9px var(--mono); padding: 1px 4px; border-radius: 3px }
.v-title .ln { height: 7px; width: 100%; border-radius: 4px; background: var(--line-2) } .v-title .ln.short { width: 70% }
.v-title .cut { position: absolute; right: 22%; bottom: -6px; font: 700 18px var(--body); color: var(--rec) }
.v-safe .ph9 { width: 68px; aspect-ratio: 9/16; border-radius: 10px; background: linear-gradient(180deg, var(--ink-2), var(--ink)); position: relative; overflow: hidden; box-shadow: var(--shadow) }
.v-safe i { position: absolute; background: color-mix(in srgb, var(--rec) 55%, transparent) }
.v-safe .t { left: 0; right: 0; top: 0; height: 12% } .v-safe .b { left: 0; right: 0; bottom: 0; height: 22% } .v-safe .r { right: 0; width: 14%; top: 40%; bottom: 22% }
.v-safe em { position: absolute; left: 6%; right: 18%; top: 14%; bottom: 25%; border: 1.5px dashed #4ADE80; border-radius: 4px }
.v-cap { gap: 6px; justify-items: center }
.v-cap .bub { width: 78%; background: var(--surface); border: 1px solid var(--line); border-radius: 12px; padding: 10px 12px; font-size: 11px; line-height: 1.4; color: var(--ink) }
.v-cap .bub span { color: var(--ink-3) }
.v-cap .cnt { font: 500 10px var(--mono); color: var(--ink-3) }
.trust { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 18px; padding-block: 12px }
@media (max-width: 760px) { .trust { grid-template-columns: 1fr } }
.trust div { border-top: 2px solid var(--ink); padding-top: 14px; display: grid; gap: 6px }
.trust h3 { margin: 0; font: 700 19px var(--display); letter-spacing: -.01em }
.trust p { margin: 0; color: var(--ink-2); font-size: 15px }
</style>'''
home = f'''{HOME_CSS}<main class="content">
<section class="home-hero"><span class="eyebrow"><b>● REC</b> 00:00:00:00 · tools for creators</span>
<h1>Ship better videos, <em>before</em> you hit upload.</h1>
<p class="lede">Fast, free tools for the checks you make on every video: script timing, title cut-offs, safe zones and caption formatting. No account. Nothing leaves your device.</p>
<div class="tc"><span>100% free</span><span>No sign-up</span><span>Runs in your browser</span></div></section>
<div class="tools">{cards}</div>
{ad('leader')}
<section class="trust" aria-label="Why use these tools">
<div><h3>Private by design</h3><p>Scripts, thumbnails and videos are processed on your device and never uploaded.</p></div>
<div><h3>Built for real workflows</h3><p>Timestamps for B-roll, cut-off checks at real font sizes, safe zones for three apps at once.</p></div>
<div><h3>Instant, every time</h3><p>No queues, no watermarks, no limits. Open a tool and get the answer.</p></div>
</section></main>'''
HOME_DESC = 'Free tools for YouTube, Shorts, Reels and TikTok creators: script timer, title and thumbnail preview, safe zone checker and Instagram caption formatter.'
write('index.html', full(f'{NAME}: free tools for video creators', HOME_DESC, '/', home,
     ld({'@context': 'https://schema.org', '@type': 'WebSite', 'name': NAME, 'url': SITE_URL + '/'})))

# ---------- trust pages ----------
def page(slug, title, desc, inner):
    bc_vis, bc_ld = crumbs([(title, None)])
    main = f'<main class="content"><section class="copy" style="padding-top:40px">{bc_vis}<span class="eyebrow"><b>●</b> {html.escape(NAME)}</span><h1 style="font-size:clamp(36px,5vw,56px)">{title}</h1>{inner}<p class="hint">Last updated {TODAY.isoformat()}</p></section></main>'
    write(f'{slug}.html', full(f'{title} · {NAME}', desc, f'/{slug}', main, bc_ld))
page('about', 'About', f'{NAME} is a free set of browser-based tools for YouTube, Shorts, Reels and TikTok creators, made by {AUTHOR}. No sign-up, nothing uploaded.', f'''<p>{html.escape(NAME)} is a set of free, simple tools for people who make videos for YouTube, Shorts, Reels and TikTok. Each tool does one job well and runs entirely in your browser.</p>
<p>We don't ask for an account, and your scripts, images and videos are never uploaded. The site is supported by ads.</p>
<p>{html.escape(NAME)} is independent and is not affiliated with YouTube, Google, Instagram, Meta or TikTok. Their names are trademarks of their owners.</p>
<h2>Who makes it</h2>
<p><b>{html.escape(AUTHOR)}</b> is a data analyst and documentary filmmaker who runs YouTube channels and builds tools for his own video workflow. Every tool here started as something he needed before an upload. More of his work: <a href="{AUTHOR_URL}">{html.escape(AUTHOR_URL.replace('https://', ''))}</a>.</p>''')
page('privacy', 'Privacy policy', f'How {NAME} handles your data, cookies and Google ads. Your scripts, images and videos stay in your browser and are never uploaded.', f'''<p><b>Your content stays on your device.</b> Scripts, captions, images and videos you use in our tools are processed in your browser and are never sent to our servers. Some tools remember your last input in your browser's local storage; you can clear it in your browser settings.</p>
<p><b>Advertising.</b> This site may show ads from Google AdSense. Google and its partners use cookies to serve ads based on your visits to this and other websites. You can turn off personalised ads in <a href="https://adssettings.google.com">Google Ads Settings</a> and read <a href="https://policies.google.com/technologies/ads">how Google uses information from sites that use its services</a>.</p>
<p><b>Analytics.</b> If enabled, analytics record anonymous usage such as page views and device type. We don't sell personal information.</p>
<p><b>EEA, UK and Switzerland.</b> Where the law requires it, you are asked for consent before advertising cookies are used.</p>
<p><b>Contact:</b> {html.escape(EMAIL)}</p>''')
page('terms', 'Terms of use', f'Terms for using the free {NAME} creator tools: results are estimates, provided as is, free for personal and commercial projects.', '''<p>The tools are free and provided "as is", without warranties. Results such as timings, previews and safe-zone guides are estimates; platforms change their apps, so always check before you publish.</p>
<p>You may use the tools for personal and commercial projects. Please don't copy the site's code or content to republish as your own.</p>
<p>We may update these terms; continuing to use the site means you accept the current version.</p>''')
page('contact', 'Contact', f'Contact {NAME} to report a bug, suggest a new creator tool, or ask how one of our calculations works. We reply by email.', f'<p>Bug, idea or a tool you wish existed? Email us:</p><p style="font:600 20px var(--mono);color:var(--ink)">{html.escape(EMAIL)}</p>')

write('404.html', full(f'Page not found · {NAME}', 'This page does not exist. Try one of the free creator tools instead.', '/404',
    '<main class="content"><section class="hero"><span class="eyebrow"><b>● 404</b> Nothing recorded here</span><h1>This page <em>doesn\'t exist.</em></h1>'
    '<p class="lede">The link may be old or mistyped. Try one of the tools instead:</p><ul>' +
    ''.join(f'<li><a href="{t["slug"]}.html">{html.escape(t["name"])}</a></li>' for t in TOOLS) + '</ul></section></main>'))

urls = ['/'] + [f'/{t["slug"]}' for t in TOOLS] + ['/about', '/privacy', '/terms', '/contact']
(DIST / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
    ''.join(f'  <url><loc>{SITE_URL}{u}</loc><lastmod>{TODAY.isoformat()}</lastmod></url>\n' for u in urls) + '</urlset>\n')
(DIST / 'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n')
(DIST / 'ads.txt').write_text(f'google.com, {CLIENT.replace("ca-pub-", "pub-") if CLIENT else "pub-0000000000000000"}, DIRECT, f08c47fec0942fa0\n')

# ---------- preview copy of the homepage for the Claude artifact viewer ----------
if PREVIEW:
  prev = re.sub(r'^<!doctype html>\n<html lang="en">\n<head>\n', '', (DIST / 'index.html').read_text())
  prev = prev.replace('\n</head>\n<body>\n', '\n').replace('\n</body>\n</html>\n', '\n')
  prev = re.sub(r'<meta charset="utf-8">\n<meta name="viewport"[^>]*>\n', '', prev)
  (HERE / 'preview_index.html').write_text(prev)
print('built', len(TOOLS), 'tools | ads', 'ON' if CLIENT else ('placeholders' if PLACEHOLDERS else 'off'))
