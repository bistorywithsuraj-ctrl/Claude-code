# Put creatorbenchtool.com live (domain at Hostinger, hosting free on Cloudflare)

The ready-to-upload site is the `tool-sites/creator/dist` folder on the `claude/quirky-feynman-4ribkf` branch.
Total time: about 20–30 minutes. Everything below works from a laptop browser; most of it also works on a phone.

## 1. Create the free Cloudflare Pages site
1. Sign up at **dash.cloudflare.com** (free plan).
2. **Workers & Pages → Create → Pages → Connect to Git** → choose GitHub → allow access to `bistorywithsuraj-ctrl/Claude-code`.
3. Settings:
   - Production branch: `claude/quirky-feynman-4ribkf` (or `main` once you merge)
   - Framework preset: **None**
   - Build command: *(leave empty)*
   - Build output directory: `tool-sites/creator/dist`
4. **Save and Deploy**. You get a free `*.pages.dev` address. Open it and check the site works.
   From now on, every push to that branch redeploys the site automatically.

## 2. Connect your Hostinger domain
1. In Cloudflare: **Add a site** → `creatorbenchtool.com` → Free plan. Cloudflare shows you **two nameservers** (like `xxx.ns.cloudflare.com`).
2. In **Hostinger hPanel → Domains → creatorbenchtool.com → DNS / Nameservers → Change nameservers** → choose "custom" and paste the two Cloudflare nameservers. Save.
   (It can take from a few minutes up to 24 hours to switch.)
3. Back in Cloudflare: **Workers & Pages → your project → Custom domains → Set up a domain** → add `creatorbenchtool.com`, then add `www.creatorbenchtool.com` too.
4. **Redirect www to the main domain** (one hop, no redirect chains): Cloudflare → creatorbenchtool.com → **Rules → Redirect Rules → Create** → "Redirect from WWW to root" template → Save.

## 3. Free email: hello@creatorbenchtool.com
Cloudflare → **Email → Email Routing** → enable → add a rule forwarding `hello@` to your Gmail. Verify the email Cloudflare sends you.

## 4. Google Search Console (so Google finds the site)
1. **search.google.com/search-console** → Add property → **Domain** → `creatorbenchtool.com`.
2. Google gives a TXT record. Add it in Cloudflare → **DNS → Add record → TXT** (name `@`). Click Verify.
3. **Sitemaps** → submit `sitemap.xml`.
4. **URL inspection** → paste each tool page URL → **Request indexing** (homepage + the 4 tools).

## 5. AdSense (after 2–4 weeks of real visits)
1. Apply at **adsense.google.com** with `creatorbenchtool.com`.
2. When you get your publisher id (`ca-pub-…`), ask Claude to rebuild with it. The ads and `ads.txt` switch on automatically.
3. AdSense → **Privacy & messaging** → turn on the consent message for EEA/UK visitors.

## What's already done in the code (SEO checklist)
| Item | Status |
|---|---|
| Real HTML on every page (Google can read it without running JS) | ✅ |
| `sitemap.xml` and `robots.txt` that allows Googlebot | ✅ |
| No `noindex` except the 404 page | ✅ |
| Clean links (`/script-timer`, no `.html`), so no redirect chains | ✅ |
| Custom 404 page | ✅ |
| Canonical tag on every page | ✅ |
| Meta descriptions under ~155 characters | ✅ |
| Exactly one H1 per page | ✅ |
| FAQ, WebApplication and Breadcrumb structured data | ✅ |
| Visible breadcrumbs | ✅ |
| No orphan pages (every page linked from nav or footer) | ✅ |
| Alt text on images | ✅ |
| Social share image (og.png) and preview tags | ✅ |
| Ad space reserved, so the layout doesn't jump | ✅ |
| Fast: every page is 15–28 KB, no heavy images or frameworks | ✅ |
| Original, human-useful content (no mass-produced AI pages) | ✅ |
| Author bio (About page + footer credit) | ✅ |
| Submit to Search Console | ⏳ You (step 4) |
| Backlinks | ⏳ Earn them: your channels, creator communities, directories (see README) |
