"""Build the deployable static site into ./dist.

Usage:
  python3 build.py                       # no ads (safe while waiting for AdSense approval)
  SITE_URL=https://yourdomain.com ADSENSE_CLIENT=ca-pub-1234567890123456 \
  CONTACT_EMAIL=hello@yourdomain.com python3 build.py

Settings come from environment variables:
  SITE_URL        your domain (used in canonical tags + sitemap)
  ADSENSE_CLIENT  your AdSense publisher id (ca-pub-...). Leave empty until approved.
  ADSENSE_SLOT_TOP / ADSENSE_SLOT_MID   ad unit ids from AdSense (optional; auto ads work without them)
  CONTACT_EMAIL   address shown on the contact page
"""
import os, re, json, html, datetime, pathlib

HERE = pathlib.Path(__file__).parent
DIST = HERE / 'dist'
SITE_URL = os.environ.get('SITE_URL', 'https://example.com').rstrip('/')
CLIENT = os.environ.get('ADSENSE_CLIENT', '').strip()
SLOT_TOP = os.environ.get('ADSENSE_SLOT_TOP', '').strip()
SLOT_MID = os.environ.get('ADSENSE_SLOT_MID', '').strip()
EMAIL = os.environ.get('CONTACT_EMAIL', 'hello@example.com')
NAME = 'Hours of Work'
DESC = ('Free calculator that turns any price into the hours you have to work to pay for it, '
        'using your real take-home pay and commute. Works for one-off buys and subscriptions.')
TODAY = datetime.date.today().isoformat()

src = (HERE / 'src' / 'tool.html').read_text()
title_m = re.search(r'<title>(.*?)</title>', src)
body = re.sub(r'<title>.*?</title>\s*', '', src, count=1)
# pull <link>/<style> into <head>, the rest into <body>
head_bits = ''.join(re.findall(r'<link[^>]*>\s*', body)) + ''.join(re.findall(r'<style>.*?</style>', body, flags=re.S))
body_only = re.sub(r'<link[^>]*>\s*', '', body)
body_only = re.sub(r'<style>.*?</style>\s*', '', body_only, flags=re.S)

def ad_unit(slot):
    if not CLIENT:
        return ''
    slot_attr = f' data-ad-slot="{slot}"' if slot else ''
    return (f'<ins class="adsbygoogle" style="display:block" data-ad-client="{CLIENT}"{slot_attr} '
            f'data-ad-format="auto" data-full-width-responsive="true"></ins>'
            f'<script>(adsbygoogle = window.adsbygoogle || []).push({{}});</script>')

body_only = body_only.replace('<div class="ad-slot" data-slot="top"></div>', f'<div class="ad-slot" data-slot="top">{ad_unit(SLOT_TOP)}</div>')
body_only = body_only.replace('<div class="ad-slot" data-slot="mid"></div>', f'<div class="ad-slot" data-slot="mid">{ad_unit(SLOT_MID)}</div>')

# FAQ structured data, taken from the page's own <details> so they never drift apart
faq = [{'@type': 'Question', 'name': html.unescape(q),
        'acceptedAnswer': {'@type': 'Answer', 'text': html.unescape(a)}}
       for q, a in re.findall(r'<summary>(.*?)</summary><p>(.*?)</p>', src)]
ld = [
    {'@context': 'https://schema.org', '@type': 'WebApplication', 'name': NAME, 'url': SITE_URL + '/',
     'applicationCategory': 'FinanceApplication', 'operatingSystem': 'Any', 'description': DESC,
     'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'USD'}},
    {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': faq},
]

adsense_head = (f'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={CLIENT}" '
                f'crossorigin="anonymous"></script>\n') if CLIENT else ''

def page(title, desc, path, head_extra, content):
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{SITE_URL}{path}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{SITE_URL}{path}">
<meta name="theme-color" content="#23784D">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='10' fill='%2323784D'/%3E%3Ctext x='32' y='44' font-family='Arial' font-weight='900' font-size='32' fill='white' text-anchor='middle'%3EH%3C/text%3E%3C/svg%3E">
{adsense_head}{head_extra}
</head>
<body>
{content}
</body>
</html>
'''

DIST.mkdir(exist_ok=True)
index_head = head_bits + '\n' + ''.join(f'<script type="application/ld+json">{json.dumps(x)}</script>\n' for x in ld)
(DIST / 'index.html').write_text(page('Hours of Work: what does it cost in hours of your life?', DESC, '/', index_head, body_only))

# ---------- trust pages (needed for AdSense review) ----------
STYLE = head_bits  # reuse fonts + tokens
def doc(title, path, desc, inner):
    content = f'''<div class="wrap">
<header class="top"><a class="brand" href="index.html" style="color:inherit;text-decoration:none">Hours<span>of</span>Work</a>
<nav class="nav" aria-label="Site"><a href="index.html">Calculator</a><a href="about.html">About</a><a href="privacy.html">Privacy</a><a href="terms.html">Terms</a><a href="contact.html">Contact</a></nav></header>
<section class="copy"><h2 style="font-size:34px">{title}</h2>{inner}<p class="hint">Last updated {TODAY}</p></section>
<footer class="foot"><span>© {datetime.date.today().year} Hours of Work</span><span><a href="index.html">Back to the calculator</a></span></footer></div>'''
    (DIST / path.lstrip('/')).write_text(page(f'{title} · {NAME}', desc, path, STYLE, content))

doc('About', '/about.html', 'Why Hours of Work exists and how it calculates.', '''
<p>Prices are written in money, but we pay for things with time. Hours of Work turns any price into the hours you need to work to afford it, using your take-home pay and the time your job really takes, commute included.</p>
<p>The calculator runs entirely in your browser. It does not ask for your name, email or any account, and your inputs are never sent to a server.</p>
<p>The results are estimates for personal reflection. They are not financial, tax or investment advice.</p>''')

doc('Privacy policy', '/privacy.html', 'How Hours of Work handles data, cookies and advertising.', f'''
<p><b>What you type stays on your device.</b> Calculations happen in your browser. Your last inputs are stored in your browser's local storage so the form is filled in next time. You can clear this at any time in your browser settings.</p>
<p><b>Advertising.</b> This site may show ads served by Google AdSense. Google and its partners use cookies to serve ads based on your visits to this and other websites. You can opt out of personalised advertising at <a href="https://adssettings.google.com">Google Ads Settings</a>, and learn more at <a href="https://policies.google.com/technologies/ads">How Google uses information from sites that use its services</a>.</p>
<p><b>Analytics.</b> If analytics are enabled, they collect anonymous usage data such as page views and device type. No personal information is sold.</p>
<p><b>Visitors in the EEA, UK and Switzerland</b> are shown a consent message for cookies where the law requires it.</p>
<p><b>Contact.</b> Questions about privacy: {html.escape(EMAIL)}</p>''')

doc('Terms of use', '/terms.html', 'Terms for using the Hours of Work calculator.', '''
<p>Hours of Work is a free tool provided "as is", without warranties of any kind. Results are estimates based on the numbers you enter and simple assumptions, and may not match your real situation.</p>
<p>Nothing on this site is financial, tax, legal or investment advice. Speak to a qualified professional before making financial decisions.</p>
<p>You may use the calculator and share its results freely. Please don't copy the site's code or content to republish it as your own.</p>
<p>We may update these terms. Continuing to use the site means you accept the current version.</p>''')

doc('Contact', '/contact.html', 'Get in touch with Hours of Work.', f'''
<p>Found a bug, have an idea, or want a calculation explained? Email us and we'll reply as soon as we can.</p>
<p class="formula">{html.escape(EMAIL)}</p>''')

(DIST / 'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n')
urls = ['/', '/about.html', '/privacy.html', '/terms.html', '/contact.html']
(DIST / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
    ''.join(f'  <url><loc>{SITE_URL}{u}</loc><lastmod>{TODAY}</lastmod></url>\n' for u in urls) + '</urlset>\n')
pub = CLIENT.replace('ca-pub-', 'pub-') if CLIENT else 'pub-0000000000000000'
(DIST / 'ads.txt').write_text(f'google.com, {pub}, DIRECT, f08c47fec0942fa0\n')
print('built', sorted(p.name for p in DIST.iterdir()), '| ads:', 'ON' if CLIENT else 'off')
