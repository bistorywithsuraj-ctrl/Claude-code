"""Inject SEO guide sections, extra FAQs and sharper titles into src/*.html. Safe to re-run:
blocks are wrapped in <!--seo-guide--> / <!--seo-faq--> markers and replaced each time."""
import re, pathlib, sys
HERE = pathlib.Path(__file__).parent; SRC = HERE.parent / 'src'
sys.path.insert(0, str(HERE))
from tools_a import C as A
from tools_b import C as B
C = {**A, **B}
esc = lambda s: s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
done = []
for slug, c in C.items():
    p = SRC / f'{slug}.html'; s = p.read_text()
    s = re.sub(r'\n?<!--seo-guide-->.*?<!--/seo-guide-->', '', s, flags=re.S); s = re.sub(r'\n?<!--seo-faq-->.*?<!--/seo-faq-->', '', s, flags=re.S)
    for k in ('title', 'desc'):
        if c.get(k): s = re.sub(rf'^{k}: .*$', f'{k}: {c[k]}', s, count=1, flags=re.M)
    guide = f'\n<!--seo-guide--><section class="copy" id="guide">\n{c["guide"]}\n</section><!--/seo-guide-->'
    i = s.find('<section class="copy" id="faq">'); assert i > 0, slug
    s = s[:i].rstrip('\n') + guide + '\n' + s[i:]
    have = {re.sub('<[^>]+>', '', q).strip().lower() for q in re.findall(r'<summary>(.*?)</summary>', s)}
    extra = ''.join(f'\n  <details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>' for q, a in c.get('faq', []) if q.lower() not in have)
    if extra:
        j = s.find('</section>', s.find('<section class="copy" id="faq">'))
        s = s[:j] + '<!--seo-faq-->' + extra + '\n<!--/seo-faq-->' + s[j:]
    p.write_text(s); done.append(slug)
missing = sorted(f.stem for f in SRC.glob('*.html') if f.stem not in C)
print(f'updated {len(done)} tools; without content: {missing or "none"}')
