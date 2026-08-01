# blueline-iq.com — Blueline Travels (Mosul branch)

Static portfolio website for Blueline Travels' Mosul branch. No backend, no build
tools, no frameworks — plain HTML + CSS + vanilla JS, deployable on any free
static host.

```
site/     ← THE WEBSITE. Deploy this folder (and only this folder).
tools/    build.py regenerates site/ from the CONFIG block inside it;
          erbil-photos.json holds the photo license/attribution records
          used to render /credits/.
```

`site/` is generated output — edit `tools/build.py` (and re-run it), not the
HTML files in `site/` directly, or your changes will be overwritten on the
next build.

> A `reference/` folder exists locally alongside this repo (research notes +
> an offline mirror of the original ctw-travels.co.uk used during the
> rebuild). It's git-ignored on purpose — it's someone else's site content
> (their photos, logo, exact copy), not something to publish.

## Deploy (pick one, all free)

**Cloudflare Pages** (recommended — fastest in/near Iraq):
1. pages.cloudflare.com → Create project → Direct upload → drag the `site/` folder.
2. Custom domains → add `blueline-iq.com` (the domain's DNS moves to Cloudflare).

**Netlify**: app.netlify.com/drop → drag the `site/` folder → Domain settings → add custom domain.

**Vercel / GitHub Pages** also work — the site is plain files with folder-based
clean URLs (`/about/index.html` → `/about/`), which every static host supports.
`404.html` is picked up automatically by Cloudflare Pages, Netlify and GitHub Pages.

## Editing content or contact details

Everything lives in ONE place: the `CONFIG` dict at the top of `tools/build.py`
(phone, WhatsApp, e-mail, address, social URLs, Formspree ID, dev credit).
Edit it, then regenerate and redeploy:

```bash
python3 tools/build.py
```

Live contact details: `+964 773 096 8898` · `contact@blueline-iq.com` ·
Al-Muhandisin St., Mosul, Iraq. Instagram/Facebook are live; LinkedIn is
still a placeholder (`#`) pending a real profile URL.

## Contact form

`/contact-us/` intentionally has no backend: on submit it opens the visitor's
own e-mail app with a pre-filled draft (name/email/phone/message) addressed
to `contact@blueline-iq.com` — they hit send once from there. Zero cost, zero
accounts, works on any host, forever. (If a real one-click submit is ever
wanted instead, swap in a free Formspree endpoint via `CONFIG["form_action"]`
in `tools/build.py` — the JS already supports it, just unused for now.)

## Preview locally

```bash
cd site && python3 -m http.server 8900
```

then open http://localhost:8900/ (root-absolute paths — don't open the files directly).

## Notes

- Total site weight ≈ 3 MB; heaviest page ≈ 1 MB.
- Erbil photos are CC-licensed from Wikimedia Commons — attribution lives on
  `/credits/` and in `tools/erbil-photos.json`. Keep the credits page.
- The Ken Burns hero, counters, scroll ring etc. are all in `site/js/main.js`
  (~5 KB, dependency-free).
- Design tokens (colours, fonts, spacing) are CSS custom properties at the top
  of `site/css/style.css`.
