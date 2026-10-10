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
SITE_URL = os.environ.get('SITE_URL', 'https://creatorbenchtool.com').rstrip('/')
CLIENT = os.environ.get('ADSENSE_CLIENT', '').strip()
EMAIL = os.environ.get('CONTACT_EMAIL', 'hello@creatorbenchtool.com')
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
ORDER = ['youtube-earnings', 'auto-captions', 'headline-match-cut', 'cartoon-characters', 'motion-prompts', 'ai-voiceover', 'background-remover', 'ai-image-detector', 'script-timer', 'title-preview', 'image-resizer', 'word-counter', 'safe-zones', 'frame-extractor', 'caption-formatter', 'youtube-chapters', 'srt-subtitles', 'case-converter', 'qr-code', 'pdf-tools', 'video-to-mp3', 'video-compressor', 'video-to-gif', 'thumbnail-text', 'teleprompter', 'hashtag-generator', 'color-palette', 'map-animator']
SHORT = {'motion-prompts': 'Motion Prompts', 'cartoon-characters': 'Cartoon Characters', 'headline-match-cut': 'Headline Match Cut', 'ai-image-detector': 'AI Image Check', 'background-remover': 'Remove Background', 'ai-voiceover': 'AI Voiceover', 'video-compressor': 'Compress & 9:16', 'video-to-gif': 'Video to GIF', 'color-palette': 'Color Palette', 'hashtag-generator': 'Hashtags', 'thumbnail-text': 'Thumbnail Text', 'teleprompter': 'Teleprompter', 'video-to-mp3': 'Video to MP3', 'auto-captions': 'Auto Captions', 'script-timer': 'Script Timer', 'title-preview': 'Title & Thumbnail', 'safe-zones': 'Safe Zone Checker', 'caption-formatter': 'Caption Formatter', 'frame-extractor': 'Frame Extractor', 'youtube-earnings': 'YouTube Earnings', 'image-resizer': 'Image Resizer', 'word-counter': 'Word Counter', 'qr-code': 'QR Code', 'youtube-chapters': 'YouTube Chapters', 'srt-subtitles': 'Text to SRT', 'case-converter': 'Case Converter', 'pdf-tools': 'JPG to PDF', 'map-animator': 'Map Animator'}
CARD_TITLE = {'motion-prompts': 'Motion Prompts Gallery', 'cartoon-characters': 'Cartoon Characters in Video', 'headline-match-cut': 'Headline Match Cut Generator', 'ai-image-detector': 'AI Image Detector', 'background-remover': 'Background Remover', 'ai-voiceover': 'AI Voiceover Generator', 'video-compressor': 'Video Compressor & 9:16 Resizer', 'video-to-gif': 'Video to GIF Converter', 'color-palette': 'Color Palette from Image', 'hashtag-generator': 'Hashtag Generator', 'thumbnail-text': 'Thumbnail Text Maker', 'teleprompter': 'Online Teleprompter', 'video-to-mp3': 'Video to MP3 Converter', 'auto-captions': 'Auto Captions Generator', 'script-timer': 'Script Timer', 'title-preview': 'Title & Thumbnail Preview', 'safe-zones': 'Shorts & Reels Safe Zones', 'caption-formatter': 'Instagram Caption Formatter', 'frame-extractor': 'Video Frame Extractor', 'youtube-earnings': 'YouTube Earnings Calculator', 'image-resizer': 'Image Resizer & Compressor', 'word-counter': 'Word & Character Counter', 'qr-code': 'QR Code Generator', 'youtube-chapters': 'YouTube Chapters Generator', 'srt-subtitles': 'Text to SRT & Subtitle Fixer', 'case-converter': 'Case Converter', 'pdf-tools': 'JPG to PDF & Merge PDF', 'map-animator': 'Map Route Animator'}
BLURB = {'headline-match-cut': 'The viral newspaper match cut from any word or sentence.',
         'ai-image-detector': 'Is it AI? File clues plus a detector model, with evidence.',
         'background-remover': 'AI cut-outs to transparent PNG, right in your browser.',
         'motion-prompts': 'Copy-paste AI prompts for viral motion graphics, with previews.',
         'cartoon-characters': 'Add dancing cartoon characters to any video, the viral trend.',
         'ai-voiceover': 'Natural AI voices in English and Hindi, MP3 or WAV, no limits.',
         'video-compressor': 'Shrink for WhatsApp or reframe 16:9 into Reels format.',
         'video-to-gif': 'Any moment of a video as a GIF, no watermark.',
         'color-palette': 'Main colors of any image as HEX, RGB and CSS.',
         'hashtag-generator': 'Broad, medium and niche hashtags for your niche, ready to copy.',
         'thumbnail-text': 'Big bold thumbnail text with templates, 1280x720 export.',
         'teleprompter': 'Scroll your script while you record, with camera and mirror.',
         'video-to-mp3': 'Extract audio from any video as MP3 or WAV, trimmed.',
         'auto-captions': 'AI word-by-word captions in English, Hindi or Hinglish, no upload.',
         'script-timer': 'Speaking time, paragraph timestamps and words to target.',
         'title-preview': 'See where your title gets cut off in every feed.',
         'safe-zones': 'Check what TikTok, Reels and Shorts buttons cover.',
         'caption-formatter': 'Line breaks that stick, plus every Instagram limit.',
         'frame-extractor': 'Save frames from any video as JPG or PNG, or a ZIP.',
         'youtube-earnings': 'Estimate ad income from views, niche and country.', 'image-resizer': 'Exact sizes for thumbnails, posts and Shorts, compressed.',
         'word-counter': 'Words, characters and every platform limit, live.', 'qr-code': 'Links, text or WiFi. PNG or SVG, never expires.',
         'youtube-chapters': 'Build timestamps or check them against YouTube rules.', 'srt-subtitles': 'Script to subtitles, or fix out-of-sync SRT files.',
         'case-converter': 'Title Case, Sentence case, UPPER and 7 more.', 'pdf-tools': 'Images to PDF or merge PDFs, nothing uploaded.', 'map-animator': 'Explainer-style route map videos for travel and history.'}
CATEGORY = {'motion-prompts': 'Prompts', 'cartoon-characters': 'Viral Edits', 'headline-match-cut': 'Viral Edits', 'ai-image-detector': 'AI Detection', 'background-remover': 'AI Images', 'ai-voiceover': 'AI Voice', 'video-compressor': 'Video Size', 'video-to-gif': 'GIF', 'color-palette': 'Design', 'hashtag-generator': 'Reach & Hashtags', 'thumbnail-text': 'Thumbnails', 'teleprompter': 'Recording', 'video-to-mp3': 'Audio', 'auto-captions': 'AI Captions', 'script-timer': 'Scripts & Voiceover', 'title-preview': 'Titles & Thumbnails', 'safe-zones': 'Vertical Video', 'caption-formatter': 'Captions & Text', 'frame-extractor': 'Video Frames', 'youtube-earnings': 'Money & Growth', 'image-resizer': 'Images', 'word-counter': 'Text', 'qr-code': 'Links & Sharing', 'youtube-chapters': 'YouTube SEO', 'srt-subtitles': 'Subtitles', 'case-converter': 'Text Formatting', 'pdf-tools': 'PDF', 'map-animator': 'Maps & Animation'}

# ---------- icons (simple stroke icons drawn for this site) ----------
P = {
 'sparkle': '<path d="M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8z"/><path d="M19 15l.8 2.2L22 18l-2.2.8L19 21l-.8-2.2L16 18l2.2-.8z"/>',
 'blob': '<path d="M7 17c-2-1-3-3-3-6a8 7 0 0116 0c0 3-1 5-3 6"/><path d="M9 17l-1 4M15 17l1 4"/><circle cx="9.5" cy="10" r="1.2"/><circle cx="14.5" cy="10" r="1.2"/><path d="M10 13.5c1 .8 3 .8 4 0"/>',
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
 'map': '<path d="M9 4L3 6v14l6-2 6 2 6-2V4l-6 2z"/><path d="M9 4v14M15 6v14"/>',
 'wave': '<path d="M3 12h2M7 8v8M11 5v14M15 9v6M19 7v10M21 12h0"/>',
 'music': '<path d="M9 18V5l11-2v13"/><circle cx="6.5" cy="18" r="2.5"/><circle cx="17.5" cy="16" r="2.5"/>',
 'tele': '<rect x="3" y="4" width="18" height="12" rx="2"/><path d="M7 8h10M7 11h7M12 16v4M8 20h8"/>',
 'thumbtext': '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M7 9h6M10 9v7"/><path d="M15 13l2 3 2-3"/>',
 'hash': '<path d="M5 9h14M5 15h14M10 4L8 20M16 4l-2 16"/>',
 'palette': '<path d="M12 3a9 9 0 100 18c1.1 0 1.5-.8 1.5-1.6 0-1.2-1-1.4-1-2.4 0-.8.7-1.5 1.6-1.5H16a5 5 0 005-5c0-4.1-4-7.5-9-7.5z"/><circle cx="7.5" cy="11" r="1"/><circle cx="10" cy="7.5" r="1"/><circle cx="14.5" cy="7.5" r="1"/>',
 'gif': '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M10 10H8v4h2v-1.5M13 10v4M16.5 10H15v4M15 12h1.5"/>',
 'compress': '<path d="M4 14h6v6M20 10h-6V4M14 10l7-7M3 21l7-7"/>',
 'voice': '<rect x="9" y="3" width="6" height="11" rx="3"/><path d="M5 11a7 7 0 0014 0M12 18v3M8 21h8"/>',
 'scissors': '<circle cx="6" cy="6" r="3"/><circle cx="6" cy="18" r="3"/><path d="M8.6 7.6L20 18M8.6 16.4L20 6"/>',
 'scan': '<path d="M4 8V5a1 1 0 011-1h3M16 4h3a1 1 0 011 1v3M20 16v3a1 1 0 01-1 1h-3M8 20H5a1 1 0 01-1-1v-3"/><circle cx="12" cy="12" r="3.2"/><path d="M12 7v1.5M12 15.5V17M7 12h1.5M15.5 12H17"/>',
 'news': '<path d="M4 5h13v14H6a2 2 0 01-2-2z"/><path d="M17 8h3v9a2 2 0 01-2 2"/><path d="M7 9h7M7 12h7M7 15h4"/>',
 'leaf': '<path d="M5 19c0-8 6-14 15-14 0 9-6 15-14 15"/><path d="M5 19l7-7"/>',
}
ICON = {'motion-prompts': 'sparkle', 'cartoon-characters': 'blob', 'headline-match-cut': 'news', 'ai-image-detector': 'scan', 'background-remover': 'scissors', 'ai-voiceover': 'voice', 'video-compressor': 'compress', 'video-to-gif': 'gif', 'color-palette': 'palette', 'hashtag-generator': 'hash', 'thumbnail-text': 'thumbtext', 'teleprompter': 'tele', 'video-to-mp3': 'music', 'auto-captions': 'wave', 'script-timer': 'clock', 'title-preview': 'title', 'safe-zones': 'phone', 'caption-formatter': 'caption', 'frame-extractor': 'film', 'youtube-earnings': 'money', 'image-resizer': 'image', 'word-counter': 'type', 'qr-code': 'qr', 'youtube-chapters': 'list', 'srt-subtitles': 'cc', 'case-converter': 'aa', 'pdf-tools': 'file', 'map-animator': 'map'}
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

def load_guides():
    out = []
    for f in sorted((HERE / 'src_guides').glob('*.html')):
        s = f.read_text(); m = re.match(r'<!--meta\n(.*?)\n-->\n', s, re.S)
        g = dict(l.split(': ', 1) for l in m.group(1).splitlines()); g['body'] = s[m.end():]; g['tools'] = [x.strip() for x in g['tools'].split(',')]
        g['faq'] = [(html.unescape(re.sub('<[^>]+>', '', q)), html.unescape(re.sub('<[^>]+>', '', a))) for q, a in re.findall(r'<summary>(.*?)</summary><p>(.*?)</p>', s)]
        out.append(g)
    return out
GUIDES = load_guides() if (HERE / 'src_guides').exists() else []

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
    res = ''.join(f'<a href="{s}.html"{cur(active == s)}>{ic(i)}{l}</a>' for s, l, i in [('guides', 'Guides', 'list'), ('about', 'About', 'info'), ('contact', 'Contact', 'mail'), ('privacy', 'Privacy', 'shield')])
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
        '<nav><a href="guides.html">Guides</a><a href="about.html">About</a><a href="privacy.html">Privacy</a><a href="terms.html">Terms</a><a href="contact.html">Contact</a></nav></footer>')

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
            f'<div class="card"><h2 class="card-h">{ic("chart")}Quick stats</h2><div class="stats-list">{stats}</div></div>'
            f'<div class="card"><h2 class="card-h">{ic("heart")}Why creators use it</h2><ul class="checks">{checks}</ul></div>'
            '<div class="card"><p class="quote" style="margin:0">“Good tools don\'t just save time. They give you back your creative energy.”<cite>— Creator Bench</cite></p></div></aside>')

def head(title, desc, path, extra=''):
    ads = (f'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={CLIENT}" crossorigin="anonymous"></script>' if CLIENT else '')
    robots = '<meta name="robots" content="noindex">' if path == '/404' else ''
    slug = path.strip('/'); img = f'{SITE_URL}/og/{slug}.png?v=2' if slug in {t['slug'] for t in TOOLS} else f'{SITE_URL}/og.png?v=2'
    return f'''<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">{robots}
<link rel="canonical" href="{SITE_URL}{path}">
<meta property="og:title" content="{html.escape(title)}"><meta property="og:description" content="{html.escape(desc)}">
<meta property="og:type" content="website"><meta property="og:url" content="{SITE_URL}{path}">
<meta property="og:image" content="{img}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:image" content="{img}">
<meta name="theme-color" content="#1F4D3A">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='16' fill='%231F4D3A'/%3E%3Cpath d='M18 46c0-16 12-28 30-28 0 18-12 30-28 30M18 46l14-14' stroke='%23DCEF80' stroke-width='5' fill='none' stroke-linecap='round'/%3E%3C/svg%3E">
<script>try{{const t=localStorage.getItem('cb-theme');if(t)document.documentElement.dataset.theme=t}}catch(e){{}}</script>
{FONTS}{ads}
<style>{BASE_CSS}</style>{extra}'''

def full(title, desc, path, content, extra='', active=None, rail_html=None, lang='en'):
    rail_part = rail_html if rail_html is not None else rail()
    return (f'<!doctype html>\n<html lang="{lang}">\n<head>\n{head(title, desc, path, extra)}\n</head>\n<body>\n<div class="app">{sidebar(active)}'
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
        + (('<div class="sec-head" id="guides"><h2>Guides</h2><a href="guides.html">All guides</a></div><section class="copy"><ul>' + ''.join(f'<li><a href="{g["slug"]}.html">{html.escape(g["h1"])}</a></li>' for g in GUIDES) + '</ul></section>') if GUIDES else '') +
        '<section class="copy"><h2>Why Creator Bench</h2><p><b>Creator Bench</b> (creatorbenchtool.com) is a free toolkit for YouTubers, Instagram and TikTok creators, built by an independent creator. It is not a talent-management or sponsorship platform. ' + 'Each tool answers a question creators ask before every upload: how long is this script, will my title get cut off, '
        'is my text hidden behind the buttons, will my caption keep its spacing. No accounts, no watermarks, no uploads. Your work stays on your device.</p></section>' + HOME_JS)
HOME_DESC = 'Free tools for creators: AI captions, AI voiceover, background remover, AI image detector, video to MP3, thumbnail maker and more. No sign-up, no upload.'
write('index.html', full(f'{NAME} Tool: free tools for video creators', HOME_DESC, '/', home,
      SCENE_CSS + ld({'@context': 'https://schema.org', '@graph': [
          {'@type': 'WebSite', '@id': SITE_URL + '/#website', 'name': NAME, 'alternateName': ['Creator Bench Tool', 'creatorbenchtool', 'creatorbenchtool.com'], 'url': SITE_URL + '/',
           'description': HOME_DESC, 'publisher': {'@id': SITE_URL + '/#org'}, 'inLanguage': 'en'},
          {'@type': 'Organization', '@id': SITE_URL + '/#org', 'name': NAME, 'alternateName': 'Creator Bench Tool', 'url': SITE_URL + '/', 'logo': SITE_URL + '/logo.png',
           'email': EMAIL, 'founder': {'@type': 'Person', 'name': AUTHOR, 'url': AUTHOR_URL}, 'sameAs': [AUTHOR_URL]}]}), active='home'))

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
for f in (HERE / 'shared' / 'vendor').iterdir(): (shutil.copytree(f, DIST / 'vendor' / f.name, dirs_exist_ok=True) if f.is_dir() else shutil.copy(f, DIST / 'vendor' / f.name))

# ---------- crawl files ----------
if not PREVIEW and 'example.com' not in SITE_URL: (DIST / 'CNAME').write_text(SITE_URL.split('://', 1)[1] + '\n')
BY_SLUG = {t['slug']: t for t in TOOLS}
for g in GUIDES:
    bc_vis, bc_ld = crumbs([('Guides', 'guides'), (g['h1'], None)])
    tool_cards = ''.join(card(BY_SLUG[s]) for s in g['tools'] if s in BY_SLUG)
    more = ''.join(f'<li><a href="{o["slug"]}.html">{html.escape(o["h1"])}</a></li>' for o in GUIDES if o is not g)
    main = (f'<article class="copy guide">{bc_vis}<span class="eyebrow">{ic("list")} Guide · {html.escape(g["date"])}</span><h1>{html.escape(g["h1"])}</h1>{g["body"]}</article>'
            f'{ad("inline")}<div class="sec-head"><h2>Tools in this guide</h2><a href="index.html#tools">All tools</a></div><div class="tools">{tool_cards}</div>'
            f'<section class="copy"><h2>More guides</h2><ul>{more}</ul></section>')
    extra = bc_ld + ld({'@context': 'https://schema.org', '@type': 'Article', 'headline': g['h1'], 'description': g['desc'], 'datePublished': g['date'], 'dateModified': g['date'],
                        'author': {'@type': 'Person', 'name': AUTHOR, 'url': AUTHOR_URL}, 'publisher': {'@type': 'Organization', 'name': NAME, 'logo': {'@type': 'ImageObject', 'url': SITE_URL + '/logo.png'}},
                        'mainEntityOfPage': f'{SITE_URL}/{g["slug"]}', 'inLanguage': 'hi-IN' if g.get('lang') == 'hi' else 'en'})
    if g['faq']: extra += ld({'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in g['faq']]})
    write(f'{g["slug"]}.html', full(g['title'], g['desc'], f'/{g["slug"]}', main, extra, active='guides', lang=g.get('lang', 'en')))
if GUIDES:
    bc_vis, bc_ld = crumbs([('Guides', None)])
    items = ''.join(f'<a class="tool-card" href="{g["slug"]}.html"><span class="tile">{ic("list")}</span><h3>{html.escape(g["h1"])}</h3><p>{html.escape(g["desc"])}</p><span class="go">{ic("arrow")}</span></a>' for g in GUIDES)
    write('guides.html', full(f'Guides for creators · {NAME}', 'Step-by-step guides for YouTube, Reels and Shorts creators: captions, thumbnails, AI voiceovers, background removal and more.', '/guides',
          f'<section class="copy">{bc_vis}<span class="eyebrow">{ic("list")} Guides</span><h1>Guides for <em>creators</em></h1><p class="lede">Short, practical how-tos for the jobs around every upload, each with a free tool to do it.</p></section><div class="tools">{items}</div>', bc_ld, active='guides'))
urls = ['/'] + [f'/{t["slug"]}' for t in TOOLS] + (['/guides'] + [f'/{g["slug"]}' for g in GUIDES]) + ['/about', '/privacy', '/terms', '/contact']
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
