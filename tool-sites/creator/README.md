# Creator Bench: free tools for video creators

Four browser-only tools on one website. **No backend, no database, no server.** You need a domain and free static hosting.

| Page | What it does | Search it targets |
|---|---|---|
| `/script-timer` | Script → speaking time, per-paragraph timestamps, words to target length; skips [notes] | "script length calculator", "words to minutes" |
| `/title-preview` | Title + thumbnail in home feed, search, sidebar, phone; light/dark; real cut-off | "youtube title length checker", "thumbnail preview" |
| `/safe-zones` | TikTok / Reels / Shorts UI overlay on your frame or video | "reels safe zone", "shorts safe zone checker" |
| `/caption-formatter` | Instagram line breaks that stick, "… more" preview, 2,200 / 30-hashtag checks | "instagram line break", "caption formatter" |

## Costs
- Domain: ~$10–15 a year (the only real cost)
- Hosting: free (Cloudflare Pages, GitHub Pages or Netlify), HTTPS included
- AdSense, Search Console, Cloudflare email forwarding: free

## Put it online (about 20 minutes)
1. **Pick and buy a domain.** Use a short brandable name, not one with "youtube", "instagram" or "tiktok" in it (trademarks). Buying it on Cloudflare Registrar is cheapest and keeps everything in one place.
2. **Build with your details:**
   ```bash
   cd tool-sites/creator
   SITE_NAME="Creator Bench" SITE_URL=https://yourdomain.com CONTACT_EMAIL=hello@yourdomain.com python3 build.py
   ```
3. **Host it:** Cloudflare dashboard → Workers & Pages → Create → Pages → upload the `dist` folder (or connect this GitHub repo with build output `tool-sites/creator/dist`). Then add your custom domain.
4. **Email:** Cloudflare → Email Routing → forward `hello@yourdomain.com` to your inbox.
5. **Google Search Console:** add the domain, verify it, and submit `https://yourdomain.com/sitemap.xml`.
6. **AdSense** (apply after the site is live and has a few weeks of real visits): sign up, add the site, then rebuild with
   `ADSENSE_CLIENT=ca-pub-XXXXXXXXXXXXXXXX python3 build.py` and upload `dist` again. `ads.txt` is generated automatically. Turn on Google's consent message for EEA/UK visitors in AdSense → Privacy & messaging.

## Launch checklist
- [ ] Share each tool in your own videos, descriptions and pinned comments
- [ ] Make 1 Short per tool showing the problem it solves
- [ ] Post in creator communities (follow each group's self-promo rules)
- [ ] List on Product Hunt, AlternativeTo and "free creator tools" lists
- [ ] After 4–8 weeks: check Search Console → Pages → which tool gets impressions, then build more tools like it

## Add a new tool
Create `src/<slug>.html` with a `<!--meta ... -->` header (copy one of the existing files), then run `python3 build.py`. It gets its own page, a homepage card, a nav link, FAQ structured data and a sitemap entry automatically.
