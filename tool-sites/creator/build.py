"""Build the creator-tools website into ./dist (plain static files, no backend).

  python3 build.py
  SITE_NAME="Creator Bench" SITE_URL=https://yourdomain.com CONTACT_EMAIL=hello@yourdomain.com \
  ADSENSE_CLIENT=ca-pub-1234567890123456 python3 build.py     # after AdSense approval

Each tool lives in src/<slug>.html with a <!--meta ... --> header. Add a file there and rebuild
to add a tool: it gets its own page, a card on the homepage, a nav link and a sitemap entry.
"""
import os, re, json, html, datetime, pathlib

HERE = pathlib.Path(__file__).parent
DIST = HERE / 'dist'
NAME = os.environ.get('SITE_NAME', 'Creator Bench')
SITE_URL = os.environ.get('SITE_URL', 'https://example.com').rstrip('/')
CLIENT = os.environ.get('ADSENSE_CLIENT', '').strip()
EMAIL = os.environ.get('CONTACT_EMAIL', 'hello@example.com')
TODAY = datetime.date.today()
BASE_CSS = (HERE / 'shared' / 'base.css').read_text()
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@112,800;118,900;125,900&family=Public+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@500;600&display=swap">')
ORDER = ['script-timer', 'title-preview', 'safe-zones', 'caption-formatter']

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
BRAND = f'<a class="brand" href="index.html">{html.escape(first)}<span>{html.escape(rest)}</span></a>'
NAV = '<nav class="nav" aria-label="Tools">' + ''.join(f'<a href="{t["slug"]}.html">{html.escape(t["name"])}</a>' for t in TOOLS) + '</nav>'
FOOT = (f'<footer class="foot"><span>© {TODAY.year} {html.escape(NAME)} · Free tools for creators. Not affiliated with YouTube, Instagram or TikTok.</span>'
        '<span><a href="about.html">About</a> · <a href="privacy.html">Privacy</a> · <a href="terms.html">Terms</a> · <a href="contact.html">Contact</a></span></footer>')

def ad_unit():
    if not CLIENT: return ''
    return (f'<ins class="adsbygoogle" style="display:block" data-ad-client="{CLIENT}" data-ad-format="auto" data-full-width-responsive="true"></ins>'
            '<script>(adsbygoogle = window.adsbygoogle || []).push({});</script>')

def head(title, desc, path, extra=''):
    ads = (f'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={CLIENT}" crossorigin="anonymous"></script>' if CLIENT else '')
    return f'''<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{SITE_URL}{path}">
<meta property="og:title" content="{html.escape(title)}"><meta property="og:description" content="{html.escape(desc)}">
<meta property="og:type" content="website"><meta property="og:url" content="{SITE_URL}{path}">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='12' fill='%235B3FD9'/%3E%3Cpath d='M22 18l26 14-26 14z' fill='white'/%3E%3C/svg%3E">
{FONTS}{ads}
<style>{BASE_CSS}</style>{extra}'''

def full(title, desc, path, content, extra=''):
    return f'<!doctype html>\n<html lang="en">\n<head>\n{head(title, desc, path, extra)}\n</head>\n<body>\n<div class="wrap">\n<header class="top">{BRAND}{NAV}</header>\n{content}\n{FOOT}\n</div>\n</body>\n</html>\n'

def ld(obj): return f'<script type="application/ld+json">{json.dumps(obj)}</script>'

DIST.mkdir(exist_ok=True)
# ---------- tool pages ----------
for t in TOOLS:
    body = t['body'].replace('<div class="ad-slot" data-slot="top"></div>', f'<div class="ad-slot">{ad_unit()}</div>')
    body = body.replace('<div class="ad-slot" data-slot="mid"></div>', f'<div class="ad-slot">{ad_unit()}</div>')
    others = [o for o in TOOLS if o is not t]
    body += ('<section class="copy"><h2>More free tools</h2><ul>' +
             ''.join(f'<li><a href="{o["slug"]}.html">{html.escape(o["name"])}</a>: {html.escape(o["desc"].split(".")[0])}.</li>' for o in others) + '</ul></section>')
    extra = ld({'@context': 'https://schema.org', '@type': 'WebApplication', 'name': t['name'], 'url': f'{SITE_URL}/{t["slug"]}',
                'applicationCategory': 'MultimediaApplication', 'operatingSystem': 'Any', 'description': t['desc'],
                'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'USD'}})
    if t['faq']:
        extra += ld({'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
            {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in t['faq']]})
    (DIST / f'{t["slug"]}.html').write_text(full(t['title'], t['desc'], f'/{t["slug"]}', body, extra))

# ---------- homepage ----------
cards = ''.join(f'''<a class="panel tool-card" href="{t["slug"]}.html"><h2>{html.escape(t["name"])}</h2><p>{html.escape(t["desc"].split(". ")[0])}.</p><span class="go">Open tool →</span></a>''' for t in TOOLS)
home = f'''<style>.tools{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,230px),1fr));gap:14px}}
.tool-card{{text-decoration:none;color:inherit;align-content:start}} .tool-card:hover{{border-color:var(--accent)}}
.tool-card p{{margin:0;color:var(--ink-2);font-size:15px}} .tool-card .go{{color:var(--accent);font-weight:700;font-size:14px}}</style>
<div><h1>Free tools for <em>video creators</em></h1>
<p class="lede">Small, fast tools for the jobs you do before every upload: timing your script, checking your title and thumbnail, keeping text out of the buttons, and formatting captions. Everything runs in your browser. No sign-up, nothing uploaded.</p></div>
<div class="tools">{cards}</div>
<div class="ad-slot">{ad_unit()}</div>
<section class="copy"><h2>Why these tools</h2><p>Each one answers a question creators ask every week, without an account or a paywall. Your scripts, thumbnails and videos stay on your own device.</p></section>'''
HOME_DESC = 'Free tools for YouTube, Shorts, Reels and TikTok creators: script timer, title and thumbnail preview, safe zone checker and Instagram caption formatter.'
(DIST / 'index.html').write_text(full(f'{NAME}: free tools for video creators', HOME_DESC, '/', home,
     ld({'@context': 'https://schema.org', '@type': 'WebSite', 'name': NAME, 'url': SITE_URL + '/'})))

# ---------- trust pages ----------
def page(slug, title, desc, inner):
    (DIST / f'{slug}.html').write_text(full(f'{title} · {NAME}', desc, f'/{slug}',
        f'<section class="copy"><h1 style="font-size:40px">{title}</h1>{inner}<p class="hint">Last updated {TODAY.isoformat()}</p></section>'))
page('about', 'About', f'About {NAME}.', f'''<p>{html.escape(NAME)} is a set of free, simple tools for people who make videos for YouTube, Shorts, Reels and TikTok. Each tool does one job well and runs entirely in your browser.</p>
<p>We don't ask for an account, and your scripts, images and videos are never uploaded. The site is supported by ads.</p>
<p>{html.escape(NAME)} is independent and is not affiliated with YouTube, Google, Instagram, Meta or TikTok. Their names are trademarks of their owners.</p>''')
page('privacy', 'Privacy policy', f'How {NAME} handles data, cookies and ads.', f'''<p><b>Your content stays on your device.</b> Scripts, captions, images and videos you use in our tools are processed in your browser and are never sent to our servers. Some tools remember your last input in your browser's local storage; you can clear it in your browser settings.</p>
<p><b>Advertising.</b> This site may show ads from Google AdSense. Google and its partners use cookies to serve ads based on your visits to this and other websites. You can turn off personalised ads in <a href="https://adssettings.google.com">Google Ads Settings</a> and read <a href="https://policies.google.com/technologies/ads">how Google uses information from sites that use its services</a>.</p>
<p><b>Analytics.</b> If enabled, analytics record anonymous usage such as page views and device type. We don't sell personal information.</p>
<p><b>EEA, UK and Switzerland.</b> Where the law requires it, you are asked for consent before advertising cookies are used.</p>
<p><b>Contact:</b> {html.escape(EMAIL)}</p>''')
page('terms', 'Terms of use', f'Terms for using {NAME}.', '''<p>The tools are free and provided "as is", without warranties. Results such as timings, previews and safe-zone guides are estimates; platforms change their apps, so always check before you publish.</p>
<p>You may use the tools for personal and commercial projects. Please don't copy the site's code or content to republish as your own.</p>
<p>We may update these terms; continuing to use the site means you accept the current version.</p>''')
page('contact', 'Contact', f'Contact {NAME}.', f'<p>Bug, idea or a tool you wish existed? Email us:</p><p style="font:600 18px var(--mono);color:var(--ink)">{html.escape(EMAIL)}</p>')

urls = ['/'] + [f'/{t["slug"]}' for t in TOOLS] + ['/about', '/privacy', '/terms', '/contact']
(DIST / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
    ''.join(f'  <url><loc>{SITE_URL}{u}</loc><lastmod>{TODAY.isoformat()}</lastmod></url>\n' for u in urls) + '</urlset>\n')
(DIST / 'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n')
(DIST / 'ads.txt').write_text(f'google.com, {CLIENT.replace("ca-pub-", "pub-") if CLIENT else "pub-0000000000000000"}, DIRECT, f08c47fec0942fa0\n')

# ---------- preview copy of the homepage for the Claude artifact viewer (no doctype/head; tool pages are linked files) ----------
prev = re.sub(r'^<!doctype html>\n<html lang="en">\n<head>\n', '', (DIST / 'index.html').read_text())
prev = prev.replace('\n</head>\n<body>\n', '\n').replace('\n</body>\n</html>\n', '\n')
prev = re.sub(r'<meta charset="utf-8">\n<meta name="viewport"[^>]*>\n', '', prev)
(HERE / 'preview_index.html').write_text(prev)
print('built', len(TOOLS), 'tools:', ', '.join(t['slug'] for t in TOOLS), '| ads', 'ON' if CLIENT else 'off')
