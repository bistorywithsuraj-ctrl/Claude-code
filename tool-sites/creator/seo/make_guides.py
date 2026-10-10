"""Write the Hindi guides in guides_hi_*.py to src_guides/ (overwrites only those files)."""
import pathlib, sys
HERE = pathlib.Path(__file__).parent; OUT = HERE.parent / 'src_guides'
sys.path.insert(0, str(HERE))
import guides_hi_2  # noqa: F401  (part 2 appends to part 1's list)
from guides_hi_1 import G
for x in G:
    meta = '\n'.join(f'{k}: {x[k]}' for k in ('slug', 'title', 'h1', 'desc', 'tools'))
    (OUT / f'{x["slug"]}.html').write_text(f'<!--meta\n{meta}\ndate: 2026-10-10\nlang: hi\n-->\n{x["body"].strip()}\n')
print(f'wrote {len(G)} Hindi guides')
