"""Build the Creator Bench website (plain static files, no backend).

  SITE_URL=https://creatorbenchtool.com CONTACT_EMAIL=hello@creatorbenchtool.com python3 build.py   # live site -> dist/
  PREVIEW=1 SITE_URL=https://creatorbenchtool.com python3 build.py                                 # Claude preview -> preview_dist/ (+ ad placeholders)
  ADSENSE_CLIENT=ca-pub-XXXXXXXXXXXXXXXX ... python3 build.py                                      # after AdSense approval

Each tool lives in src/<slug>.html with a <!--meta ... --> header. Add a file there and rebuild:
it gets its own page, sidebar link, homepage card, sitemap entry and structured data.
"""
import os, re, json, html, math, random, datetime, pathlib

HERE = pathlib.Path(__file__).parent
PREVIEW = os.environ.get('PREVIEW', '0') == '1'
DIST = HERE / ('preview_dist' if PREVIEW else 'dist')
NAME = os.environ.get('SITE_NAME', 'Creator Bench')
TAGLINE = 'Tools for better uploads'
SITE_URL = os.environ.get('SITE_URL', 'https://example.com').rstrip('/')
CLIENT = os.environ.get('ADSENSE_CLIENT', '').strip()
EMAIL = os.environ.get('CONTACT_EMAIL', 'hello@example.com')
AUTHOR = os.environ.get('AUTHOR_NAME', 'Suraj Shukla')
AUTHOR_URL = os.environ.get('AUTHOR_URL', 'https://bistorywithsuraj.com')
AUTHOR_SHORT = AUTHOR_URL.replace('https://', '')
PLACEHOLDERS = PREVIEW and not CLIENT  # live site hides ad boxes until AdSense is connected
TODAY = datetime.date.today()
CUR = ' aria-current="page"'
BASE_CSS = (HERE / 'shared' / 'base.css').read_text()
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,500;0,6..72,600;1,6..72,500;1,6..72,600'
         '&family=Geist:wght@400;500;600&family=Geist+Mono:wght@500&family=Caveat:wght@600&display=swap">')
ORDER = ['youtube-earnings', 'script-timer', 'title-preview', 'image-resizer', 'word-counter', 'safe-zones', 'frame-extractor', 'caption-formatter', 'youtube-chapters', 'srt-subtitles', 'case-converter', 'qr-code', 'pdf-tools']
SHORT = {'script-timer': 'Script Timer', 'title-preview': 'Title & Thumbnail', 'safe-zones': 'Safe Zone Checker', 'caption-formatter': 'Caption Formatter', 'frame-extractor': 'Frame Extractor', 'youtube-earnings': 'YouTube Earnings', 'image-resizer': 'Image Resizer', 'word-counter': 'Word Counter', 'qr-code': 'QR Code', 'youtube-chapters': 'YouTube Chapters', 'srt-subtitles': 'Text to SRT', 'case-converter': 'Case Converter', 'pdf-tools': 'JPG to PDF'}
CARD_TITLE = {'script-timer': 'Script Timer', 'title-preview': 'Title & Thumbnail Preview', 'safe-zones': 'Shorts & Reels Safe Zones', 'caption-formatter': 'Instagram Caption Formatter', 'frame-extractor': 'Video Frame Extractor', 'youtube-earnings': 'YouTube Earnings Calculator', 'image-resizer': 'Image Resizer & Compressor', 'word-counter': 'Word & Character Counter', 'qr-code': 'QR Code Generator', 'youtube-chapters': 'YouTube Chapters Generator', 'srt-subtitles': 'Text to SRT & Subtitle Fixer', 'case-converter': 'Case Converter', 'pdf-tools': 'JPG to PDF & Merge PDF'}
BLURB = {'script-timer': 'Speaking time, paragraph timestamps and words to target.',
         'title-preview': 'See where your title gets cut off in every feed.',
         'safe-zones': 'Check what TikTok, Reels and Shorts buttons cover.',
         'caption-formatter': 'Line breaks that stick, plus every Instagram limit.',
         'frame-extractor': 'Save frames from any video as JPG or PNG, or a ZIP.',
         'youtube-earnings': 'Estimate ad income from views, niche and country.', 'image-resizer': 'Exact sizes for thumbnails, posts and Shorts, compressed.',
         'word-counter': 'Words, characters and every platform limit, live.', 'qr-code': 'Links, text or WiFi. PNG or SVG, never expires.',
         'youtube-chapters': 'Build timestamps or check them against YouTube rules.', 'srt-subtitles': 'Script to subtitles, or fix out-of-sync SRT files.',
         'case-converter': 'Title Case, Sentence case, UPPER and 7 more.', 'pdf-tools': 'Images to PDF or merge PDFs, nothing uploaded.'}
CATEGORY = {'script-timer': 'Scripts & Voiceover', 'title-preview': 'Titles & Thumbnails', 'safe-zones': 'Vertical Video', 'caption-formatter': 'Captions & Text', 'frame-extractor': 'Video Frames', 'youtube-earnings': 'Money & Growth', 'image-resizer': 'Images', 'word-counter': 'Text', 'qr-code': 'Links & Sharing', 'youtube-chapters': 'YouTube SEO', 'srt-subtitles': 'Subtitles', 'case-converter': 'Text Formatting', 'pdf-tools': 'PDF'}

# ---------- icons (simple stroke icons drawn for this site) ----------
P = {
 'home': '<path d="M3 11l9-7 9 7"/><path d="M5 10v10h14V10"/><path d="M10 20v-6h4v6"/>',
 'grid': '<rect x="4" y="4" width="6" height="6" rx="1.5"/><rect x="14" y="4" width="6" height="6" rx="1.5"/><rect x="4" y="14" width="6" height="6" rx="1.5"/><rect x="14" y="14" width="6" height="6" rx="1.5"/>',
 'info': '<circle cx="12" cy="12" r="9"/><path d="M12 11v5"/><path d="M12 8h.01"/>',
 'mail': '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/>',
 'shield': '<path d="M12 3l8 3v6c0 4.5-3.4 8.2-8 9-4.6-.8-8-4.5-8-9V6z"/><path d="M9 12l2 2 4-4"/>',
 'sun': '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
 'menu': '<path d="M4 7h16M4 12h16M4 17h16"/>',
 'share': '<circle cx="18" cy="5" r="2.5"/><circle cx="6" cy="12" r="2.5"/><circle cx="18" cy="19" r="2.5"/><path d="M8.3 10.8l7.4-4.4M8.3 13.2l7.4 4.4"/>',
 'search': '<circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4"/>',
 'arrow': '<path d="M5 12h14"/><path d="M13 6l6 6-6 6"/>',
 'clock': '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
 'title': '<rect x="3" y="5" width="18" height="11" rx="2"/><path d="M7 20h10"/><path d="M8 9h8M8 12h5"/>',
 'phone': '<rect x="7" y="2.5" width="10" height="19" rx="2.5"/><path d="M7 6.5h10M7 17.5h10"/><path d="M14.5 9.5v5"/>',
 'caption': '<path d="M4 5h16v11H9l-5 4z"/><path d="M8 9h8M8 12h5"/>',
 'chart': '<path d="M3 17l6-6 4 4 8-8"/><path d="M15 7h6v6"/>',
 'zap': '<path d="M13 2L4 14h7l-1 8 9-12h-7z"/>',
 'key': '<rect x="4" y="10" width="16" height="10" rx="2"/><path d="M8 10V7a4 4 0 018 0v3"/>',
 'heart': '<path d="M12 20s-7-4.4-7-10a4 4 0 017-2.6A4 4 0 0119 10c0 5.6-7 10-7 10z"/>',
 'check': '<path d="M5 12l5 5 9-10"/>',
 'film': '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M7 4v16M17 4v16M3 9h4M3 15h4M17 9h4M17 15h4"/>',
 'money': '<circle cx="12" cy="12" r="9"/><path d="M15 9.5c-.5-1-1.6-1.5-3-1.5-1.7 0-3 .9-3 2.2 0 3 6 1.6 6 4.6 0 1.3-1.3 2.2-3 2.2-1.5 0-2.6-.6-3.1-1.6M12 6.5v11"/>',
 'image': '<rect x="3" y="5" width="18" height="14" rx="2"/><circle cx="9" cy="10" r="1.6"/><path d="M21 16l-5-5-8 8"/>',
 'type': '<path d="M4 7V5h16v2M12 5v14M9 19h6"/>',
 'qr': '<rect x="4" y="4" width="6" height="6" rx="1"/><rect x="14" y="4" width="6" height="6" rx="1"/><rect x="4" y="14" width="6" height="6" rx="1"/><path d="M14 14h2v2h-2zM18 18h2v2h-2zM14 18h2M18 14h2"/>',
 'list': '<path d="M9 6h11M9 12h11M9 18h11"/><circle cx="4.5" cy="6" r="1"/><circle cx="4.5" cy="12" r="1"/><circle cx="4.5" cy="18" r="1"/>',
 'cc': '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M10 10.5a2 2 0 100 3M16 10.5a2 2 0 100 3"/>',
 'aa': '<path d="M3 18l4-11 4 11M4.5 14h5"/><circle cx="17" cy="15" r="3"/><path d="M20 12v6"/>',
 'file': '<path d="M14 3H7a2 2 0 00-2 2v14a2 2 0 002 2h10a2 2 0 002-2V8z"/><path d="M14 3v5h5M9 13h6M9 17h4"/>',
 'leaf': '<path d="M5 19c0-8 6-14 15-14 0 9-6 15-14 15"/><path d="M5 19l7-7"/>',
}
ICON = {'script-timer': 'clock', 'title-preview': 'title', 'safe-zones': 'phone', 'caption-formatter': 'caption', 'frame-extractor': 'film', 'youtube-earnings': 'money', 'image-resizer': 'image', 'word-counter': 'type', 'qr-code': 'qr', 'youtube-chapters': 'list', 'srt-subtitles': 'cc', 'case-converter': 'aa', 'pdf-tools': 'file'}
def ic(name, cls='i'): return f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true">{P[name]}</svg>'
def cur(flag): return CUR if flag else ''

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

# ---------- original landscape scene for the hero (procedural SVG) ----------
def scene_svg():
    rnd = random.Random(7); W, H = 1200, 420
    def ridge(base, amp, rough, shift, step=24):
        pts = []
        for x in range(0, W + step, step):
            y = base + amp * math.sin(x / 210 + shift) + amp * .45 * math.sin(x / 73 + shift * 2) + rnd.uniform(-rough, rough)
            pts.append(f'{x},{y:.1f}')
        return f'M0,{H} L' + ' L'.join(pts) + f' L{W},{H} Z'
    layers = [(170, 70, 10, 1.2, 'var(--sc1)'), (215, 55, 8, 2.6, 'var(--sc2)'), (265, 40, 6, 4.1, 'var(--sc3)'), (305, 22, 4, 5.3, 'var(--sc4)')]
    paths = ''.join(f'<path d="{ridge(b, a, r, s)}" fill="{c}"/>' for b, a, r, s, c in layers)
    return (f'<svg class="scene" viewBox="0 0 {W} {H}" preserveAspectRatio="xMaxYMid slice" aria-hidden="true">'
            '<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="var(--sky1)"/><stop offset="1" stop-color="var(--sky2)"/></linearGradient>'
            '<linearGradient id="fade" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="var(--surface-2)"/><stop offset=".42" stop-color="var(--surface-2)"/><stop offset=".7" stop-color="var(--surface-2)" stop-opacity="0"/></linearGradient></defs>'
            f'<rect width="{W}" height="{H}" fill="url(#sky)"/><circle cx="930" cy="110" r="46" fill="var(--sun)"/>{paths}'
            f'<rect y="330" width="{W}" height="90" fill="var(--lake)"/><path d="M700,352 h160 M760,368 h120 M820,384 h90" stroke="var(--shine)" stroke-width="3" stroke-linecap="round"/>'
            f'<rect width="{W}" height="{H}" fill="url(#fade)"/></svg>')
SCENE_CSS = '''<style>
:root { --sky1: #E7EEDF; --sky2: #F3F2EA; --sun: #F6E7A8; --sc1: #C9D6C1; --sc2: #A9BFA4; --sc3: #7FA083; --sc4: #4F7A5C; --lake: #B9CDBE; --shine: #E8F0E6 }
:root[data-theme="dark"] { --sky1: #142019; --sky2: #1B2720; --sun: #5D5A33; --sc1: #22352B; --sc2: #2A4334; --sc3: #33563F; --sc4: #3D6A4B; --lake: #1F3329; --shine: #3B5546 }
</style>'''

# ---------- shell ----------
def sidebar(active):
    tools = ''.join(f'<a href="{t["slug"]}.html"{cur(active == t["slug"])}>{ic(ICON.get(t["slug"], "grid"))}{html.escape(SHORT.get(t["slug"], t["name"]))}</a>' for t in TOOLS)
    res = ''.join(f'<a href="{s}.html"{cur(active == s)}>{ic(i)}{l}</a>' for s, l, i in [('about', 'About', 'info'), ('contact', 'Contact', 'mail'), ('privacy', 'Privacy', 'shield')])
    return (f'<aside class="side" id="side" aria-label="Site navigation"><a class="brand" href="index.html"><span class="mark">{ic("leaf", "")}</span>'
            f'<span><b>{html.escape(NAME)}</b><small>{TAGLINE}</small></span></a>'
            f'<nav><a href="index.html"{cur(active == "home")}>{ic("home")}Home</a></nav><h6>Tools</h6><nav>{tools}</nav><h6>Resources</h6><nav>{res}</nav>'
            '<div class="note"><b>Small tools.<br>Big creative freedom.</b><span>Check, fix and ship your videos faster.</span></div></aside>')

def topbar(active):
    def tab(href, label, icon, key, cls=''):
        return f'<a class="tab {cls}" href="{href}"{cur(active == key)}>{ic(icon)}{label}</a>'
    return ('<header class="topbar"><button class="icon-btn menu-btn" id="menu" aria-label="Open menu" aria-controls="side">' + ic('menu') + '</button>'
            + tab('index.html', 'Home', 'home', 'home') + tab('index.html#tools', 'All tools', 'grid', 'all', 'hide-sm') + tab('about.html', 'About', 'info', 'about', 'hide-sm') +
            '<span class="sp"></span><button class="icon-btn" id="theme" aria-label="Switch light or dark mode">' + ic('sun') + '</button>'
            '<button class="btn-primary" id="share">' + ic('share') + '<span>Share</span></button></header>')

SHELL_JS = '''<script>
(() => {
  const root = document.documentElement;
  document.getElementById('theme')?.addEventListener('click', () => {
    const dark = root.dataset.theme === 'dark';
    root.dataset.theme = dark ? 'light' : 'dark'; try { localStorage.setItem('cb-theme', root.dataset.theme); } catch (e) {}
  });
  document.getElementById('menu')?.addEventListener('click', () => document.body.classList.toggle('drawer'));
  document.addEventListener('click', e => { if (document.body.classList.contains('drawer') && !e.target.closest('#side') && !e.target.closest('#menu')) document.body.classList.remove('drawer'); });
  const share = document.getElementById('share'), label = share?.querySelector('span');
  share?.addEventListener('click', async () => {
    try { if (navigator.share) { await navigator.share({ title: document.title, url: location.href }); return; }
          await navigator.clipboard.writeText(location.href); label.textContent = 'Link copied'; }
    catch (e) { label.textContent = 'Copy the address bar'; }
    setTimeout(() => label.textContent = 'Share', 2000);
  });
})();
</script>'''

FOOT = (f'<footer class="site-foot"><span>© {TODAY.year} {html.escape(NAME)} · Made by <a href="{AUTHOR_URL}">{html.escape(AUTHOR)}</a> · Not affiliated with YouTube, Instagram or TikTok.</span>'
        '<nav><a href="about.html">About</a><a href="privacy.html">Privacy</a><a href="terms.html">Terms</a><a href="contact.html">Contact</a></nav></footer>')

def ad(kind):
    """kind: leader (banner), inline (in-content), rect (300x250 rail), tower (300x600 rail)."""
    if CLIENT:
        fixed = {'rect': (300, 250), 'tower': (300, 600)}
        if kind in fixed:
            w, h = fixed[kind]; ins = f'<ins class="adsbygoogle" style="display:inline-block;width:{w}px;height:{h}px" data-ad-client="{CLIENT}"></ins>'
        else:
            ins = f'<ins class="adsbygoogle" style="display:block" data-ad-client="{CLIENT}" data-ad-format="auto" data-full-width-responsive="true"></ins>'
        return f'<div class="ad {kind}"><div class="box">{ins}<script>(adsbygoogle = window.adsbygoogle || []).push({{}});</script></div></div>'
    if PLACEHOLDERS:
        size = {'leader': '728 × 90 · responsive', 'inline': '336 × 280 · responsive', 'rect': '300 × 250', 'tower': '300 × 600'}[kind]
        return f'<div class="ad {kind}"><div class="box ph">Ad slot<br>{size}</div></div>'
    return ''

def rail(kind='rect'):
    stats = ''.join(f'<div><i>{ic(i)}</i><span><b>{b}</b><span>{s}</span></span></div>' for i, b, s in
                    [('grid', f'{len(TOOLS)}+', 'Useful tools'), ('heart', '100%', 'Free to use'), ('zap', 'Instant', 'Results'), ('key', 'No signup', 'Required')])
    checks = ''.join(f'<li>{ic("check")}{c}</li>' for c in ['Simple and fast', 'No account needed', 'Works on every device', 'Nothing gets uploaded'])
    return (f'<aside class="rail" aria-label="Sidebar">{ad(kind)}'
            f'<div class="card"><h3>{ic("chart")}Quick stats</h3><div class="stats-list">{stats}</div></div>'
            f'<div class="card"><h3>{ic("heart")}Why creators use it</h3><ul class="checks">{checks}</ul></div>'
            '<div class="card"><p class="quote" style="margin:0">“Good tools don\'t just save time. They give you back your creative energy.”<cite>— Creator Bench</cite></p></div></aside>')

def head(title, desc, path, extra=''):
    ads = (f'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={CLIENT}" crossorigin="anonymous"></script>' if CLIENT else '')
    robots = '<meta name="robots" content="noindex">' if path == '/404' else ''
    return f'''<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">{robots}
<link rel="canonical" href="{SITE_URL}{path}">
<meta property="og:title" content="{html.escape(title)}"><meta property="og:description" content="{html.escape(desc)}">
<meta property="og:type" content="website"><meta property="og:url" content="{SITE_URL}{path}">
<meta property="og:image" content="{SITE_URL}/og.png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:image" content="{SITE_URL}/og.png">
<meta name="theme-color" content="#1F4D3A">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='16' fill='%231F4D3A'/%3E%3Cpath d='M18 46c0-16 12-28 30-28 0 18-12 30-28 30M18 46l14-14' stroke='%23DCEF80' stroke-width='5' fill='none' stroke-linecap='round'/%3E%3C/svg%3E">
<script>try{{const t=localStorage.getItem('cb-theme');if(t)document.documentElement.dataset.theme=t}}catch(e){{}}</script>
{FONTS}{ads}
<style>{BASE_CSS}</style>{extra}'''

def full(title, desc, path, content, extra='', active=None, rail_html=None):
    rail_part = rail_html if rail_html is not None else rail()
    return (f'<!doctype html>\n<html lang="en">\n<head>\n{head(title, desc, path, extra)}\n</head>\n<body>\n<div class="app">{sidebar(active)}'
            f'<div class="main">{topbar(active)}<div class="wrap"><main class="content">{content}</main>{rail_part}</div>{FOOT}</div></div>\n{SHELL_JS}\n</body>\n</html>\n')

def clean_links(doc):
    if PREVIEW: return doc
    doc = re.sub(r'href="index\.html(#[a-z-]+)?"', lambda m: f'href="/{m.group(1) or ""}"', doc)
    return re.sub(r'href="([a-z0-9-]+)\.html"', r'href="/\1"', doc)
def write(name, doc): (DIST / name).write_text(clean_links(doc))
def ld(obj): return f'<script type="application/ld+json">{json.dumps(obj)}</script>'
def crumbs(items):
    vis = '<nav class="crumbs" aria-label="Breadcrumb"><a href="index.html">Home</a>' + ''.join(
        ' <span aria-hidden="true">/</span> ' + (f'<a href="{p}.html">{html.escape(l)}</a>' if p else f'<span aria-current="page">{html.escape(l)}</span>') for l, p in items) + '</nav>'
    data = {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement':
            [{'@type': 'ListItem', 'position': 1, 'name': 'Home', 'item': SITE_URL + '/'}] +
            [{'@type': 'ListItem', 'position': i + 2, 'name': l, **({'item': f'{SITE_URL}/{p}'} if p else {})} for i, (l, p) in enumerate(items)]}
    return vis, ld(data)
def card(t, flag=False, search=False):
    q = f' data-q="{html.escape((t["name"] + " " + t["desc"]).lower())}"' if search else ''
    badge = '<span class="flag">Most popular</span>' if flag else ''
    return (f'<a class="tool-card" href="{t["slug"]}.html"{q}>{badge}<span class="tile">{ic(ICON.get(t["slug"], "grid"))}</span>'
            f'<h3>{html.escape(CARD_TITLE.get(t["slug"], t["name"]))}</h3><p>{html.escape(BLURB.get(t["slug"], t["desc"]))}</p><span class="go">{ic("arrow")}</span></a>')

DIST.mkdir(exist_ok=True)
for f in DIST.glob('*.html'): f.unlink()

# ---------- tool pages ----------
for t in TOOLS:
    bc_vis, bc_ld = crumbs([(t['name'], None)])
    body = re.sub(r'<h1>', f'{bc_vis}<span class="eyebrow">{ic(ICON.get(t["slug"], "grid"))} Free tool · No sign-up</span><h1>', t['body'], count=1)
    body = body.replace('<div class="ad-slot" data-slot="top"></div>', ad('leader'))
    body = body.replace('<div class="ad-slot" data-slot="mid"></div>', ad('inline'))
    others = [o for o in TOOLS if o is not t]
    body += '<div class="sec-head"><h2>More free tools</h2><a href="index.html#tools">View all</a></div><div class="tools">' + ''.join(card(o) for o in others) + '</div>'
    extra = bc_ld + ld({'@context': 'https://schema.org', '@type': 'WebApplication', 'name': t['name'], 'url': f'{SITE_URL}/{t["slug"]}',
                        'applicationCategory': 'MultimediaApplication', 'operatingSystem': 'Any', 'description': t['desc'],
                        'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'USD'}})
    if t['faq']:
        extra += ld({'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
            {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in t['faq']]})
    write(f'{t["slug"]}.html', full(t['title'], t['desc'], f'/{t["slug"]}', body, extra, active=t['slug'], rail_html=rail('tower')))

# ---------- homepage ----------
popular = ''.join(f'<a href="{t["slug"]}.html">{html.escape(SHORT.get(t["slug"], t["name"]))}</a>' for t in TOOLS[:6])
cards = ''.join(card(t, flag=(i == 0), search=True) for i, t in enumerate(TOOLS))
cats = ''.join(f'<a href="{t["slug"]}.html"><i>{ic(ICON.get(t["slug"], "grid"))}</i>{html.escape(CATEGORY.get(t["slug"], t["name"]))}</a>' for t in TOOLS)
HOME_JS = '''<script>
(() => { const q = document.getElementById('q'), cards = [...document.querySelectorAll('#cards .tool-card')], none = document.getElementById('nomatch');
  q.addEventListener('input', () => { const v = q.value.trim().toLowerCase(); let n = 0;
    cards.forEach(c => { const hit = !v || v.split(/\\s+/).every(w => c.dataset.q.includes(w)); c.hidden = !hit; n += hit; }); none.hidden = n > 0; });
  q.addEventListener('keydown', e => { if (e.key === 'Enter') { const first = cards.find(c => !c.hidden); if (first) location.href = first.href; } }); })();
</script>'''
home = (f'<section class="hero">{scene_svg()}<p class="hand" aria-hidden="true">Better tools<br>for bigger ideas</p>'
        '<div class="copy"><span class="badge">Free creator tools</span><h1>Create more.<br><em>Worry less.</em></h1>'
        '<p class="lede">Simple, fast tools for scripts, titles, thumbnails, safe zones and captions. Everything runs in your browser, with no sign-up.</p>'
        f'<label class="search" for="q">{ic("search")}<input id="q" type="search" placeholder="Search for a tool…" autocomplete="off" aria-label="Search tools"></label>'
        f'<div class="chips">Popular: {popular}</div></div></section>'
        '<div class="sec-head" id="tools"><h2>Popular tools</h2><a href="#cats">Browse by category</a></div>'
        f'<div class="tools" id="cards">{cards}</div><p class="no-match" id="nomatch" hidden>No tool matches that yet. Try "script", "title", "reels" or "caption".</p>'
        f'{ad("leader")}<div class="sec-head" id="cats"><h2>Browse by category</h2></div><div class="cats">{cats}</div>'
        '<section class="copy"><h2>Why Creator Bench</h2><p>Each tool answers a question creators ask before every upload: how long is this script, will my title get cut off, '
        'is my text hidden behind the buttons, will my caption keep its spacing. No accounts, no watermarks, no uploads. Your work stays on your device.</p></section>' + HOME_JS)
HOME_DESC = 'Free tools for creators: YouTube earnings calculator, image resizer, word counter, frame extractor, subtitles, QR codes, PDF tools and more. No sign-up.'
write('index.html', full(f'{NAME}: free tools for video creators', HOME_DESC, '/', home,
      SCENE_CSS + ld({'@context': 'https://schema.org', '@type': 'WebSite', 'name': NAME, 'url': SITE_URL + '/'}), active='home'))

# ---------- trust pages ----------
def page(slug, title, desc, inner):
    bc_vis, bc_ld = crumbs([(title, None)])
    main = f'<section class="copy">{bc_vis}<span class="eyebrow">{html.escape(NAME)}</span><h1>{title}</h1>{inner}<p class="hint">Last updated {TODAY.isoformat()}</p></section>'
    write(f'{slug}.html', full(f'{title} · {NAME}', desc, f'/{slug}', main, bc_ld, active=slug))
page('about', 'About', f'{NAME} is a free set of browser-based tools for YouTube, Shorts, Reels and TikTok creators, made by {AUTHOR}. No sign-up, nothing uploaded.', f'''
<p>{html.escape(NAME)} is a set of free, simple tools for people who make videos for YouTube, Shorts, Reels and TikTok. Each tool does one job well and runs entirely in your browser.</p>
<p>We don't ask for an account, and your scripts, images and videos are never uploaded. The site is supported by ads.</p>
<p>{html.escape(NAME)} is independent and is not affiliated with YouTube, Google, Instagram, Meta or TikTok. Their names are trademarks of their owners.</p>
<h2>Who makes it</h2>
<p><b>{html.escape(AUTHOR)}</b> is a data analyst and documentary filmmaker who runs YouTube channels and builds tools for his own video workflow. Every tool here started as something he needed before an upload. More of his work: <a href="{AUTHOR_URL}">{html.escape(AUTHOR_SHORT)}</a>.</p>''')
page('privacy', 'Privacy policy', f'How {NAME} handles your data, cookies and Google ads. Your scripts, images and videos stay in your browser and are never uploaded.', f'''
<p><b>Your content stays on your device.</b> Scripts, captions, images and videos you use in our tools are processed in your browser and are never sent to our servers. Some tools remember your last input in your browser's local storage; you can clear it in your browser settings.</p>
<p><b>Advertising.</b> This site may show ads from Google AdSense. Google and its partners use cookies to serve ads based on your visits to this and other websites. You can turn off personalised ads in <a href="https://adssettings.google.com">Google Ads Settings</a> and read <a href="https://policies.google.com/technologies/ads">how Google uses information from sites that use its services</a>.</p>
<p><b>Analytics.</b> If enabled, analytics record anonymous usage such as page views and device type. We don't sell personal information.</p>
<p><b>EEA, UK and Switzerland.</b> Where the law requires it, you are asked for consent before advertising cookies are used.</p>
<p><b>Contact:</b> {html.escape(EMAIL)}</p>''')
page('terms', 'Terms of use', f'Terms for using the free {NAME} creator tools: results are estimates, provided as is, free for personal and commercial projects.', '''
<p>The tools are free and provided "as is", without warranties. Results such as timings, previews and safe-zone guides are estimates; platforms change their apps, so always check before you publish.</p>
<p>You may use the tools for personal and commercial projects. Please don't copy the site's code or content to republish as your own.</p>
<p>We may update these terms; continuing to use the site means you accept the current version.</p>''')
page('contact', 'Contact', f'Contact {NAME} to report a bug, suggest a new creator tool, or ask how one of our calculations works. We reply by email.',
     f'<p>Bug, idea or a tool you wish existed? Email us:</p><p style="font:600 20px var(--mono);color:var(--ink)">{html.escape(EMAIL)}</p>')
write('404.html', full(f'Page not found · {NAME}', 'This page does not exist. Try one of the free creator tools instead.', '/404',
      '<section class="copy"><span class="eyebrow">404 · Nothing here</span><h1>This page <em>doesn\'t exist.</em></h1><p>The link may be old or mistyped. Try one of the tools instead:</p><ul>' +
      ''.join(f'<li><a href="{t["slug"]}.html">{html.escape(t["name"])}</a></li>' for t in TOOLS) + '</ul></section>'))

# ---------- self-hosted libraries ----------
import shutil
(DIST / 'vendor').mkdir(exist_ok=True)
for f in (HERE / 'shared' / 'vendor').glob('*.js'): shutil.copy(f, DIST / 'vendor' / f.name)

# ---------- crawl files ----------
if not PREVIEW and 'example.com' not in SITE_URL: (DIST / 'CNAME').write_text(SITE_URL.split('://', 1)[1] + '\n')
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
print('built', len(TOOLS), 'tools ->', DIST.name, '| ads', 'ON' if CLIENT else ('placeholders' if PLACEHOLDERS else 'off'))
