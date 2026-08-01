#!/usr/bin/env python3
"""
Static site generator for blueline-iq.com (Blueline Travels — Mosul branch).

Reads page copy from ../reference/site-mirror/ (the company's own site text,
migrated verbatim per the owner's instruction) and emits a dependency-free
static site into ../site/ with clean URLs (folder/index.html).

Re-run after editing CONFIG (e.g. when the real contact details arrive):
    python3 tools/build.py
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MIRROR = ROOT / "reference" / "site-mirror"
OUT = ROOT / "site"

# ----------------------------------------------------------------------------
# CONFIG — everything that will change when the real details arrive lives here
# ----------------------------------------------------------------------------
CONFIG = {
    "domain": "https://blueline-iq.com",
    "brand": "Blueline Travels — Mosul",
    "brand_long": "Blueline Travels — Mosul, Iraq",
    "phone_display": "+964 750 248 0360",  # TODO(owner): confirm this is still the right number for Blueline/Mosul
    "phone_tel": "+9647502480360",
    "whatsapp": "https://wa.me/9647502480360",
    "email": "info@blueline-iq.com",
    "address_lines": ["Al-Muhandisin St.", "Mosul", "Iraq"],
    "registration": "Blueline Travels — Mosul branch, proudly serving corporate and leisure travelers across Iraq.",  # TODO(owner): swap for a formal registration line if/when you want one
    "social": {
        # TODO(owner): the old CTW social links were dropped (they pointed to a
        # different, unrelated business's real accounts) — paste Blueline's own
        # Instagram/LinkedIn/Facebook URLs here once they exist.
        "instagram": "#",
        "linkedin": "#",
        "facebook": "#",
    },
    # Contact form: create a free form at https://formspree.io and paste its
    # endpoint here, then re-run this script. Until then the form falls back
    # to opening a pre-filled e-mail draft.
    "form_action": "https://formspree.io/f/YOUR_FORM_ID",
    "dev_name": "Harith",
    "dev_url": "https://harithx.dev",
}

# ----------------------------------------------------------------------------
# Inline SVG icons (Feather Icons, MIT license — https://feathericons.com)
# ----------------------------------------------------------------------------
def icon(name, cls=""):
    body = ICONS[name]
    c = f' class="{cls}"' if cls else ""
    return (f'<svg{c} viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
            f'aria-hidden="true">{body}</svg>')

ICONS = {
    "phone": '<path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>',
    "mail": '<rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 6-10 7L2 6"/>',
    "pin": '<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/>',
    "send": '<path d="m22 2-11 11"/><path d="m22 2-7 20-4-9-9-4z"/>',
    "building": '<path d="M3 21h18"/><path d="M5 21V7l7-5 7 5v14"/><path d="M9 21v-4h6v4"/><path d="M9 10h.01M15 10h.01M9 14h.01M15 14h.01"/>',
    "users": '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    "user": '<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>',
    "tag": '<path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.83z"/><path d="M7 7h.01"/>',
    "award": '<circle cx="12" cy="8" r="7"/><path d="M8.21 13.89 7 23l5-3 5 3-1.21-9.12"/>',
    "dollar": '<path d="M12 1v22"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>',
    "heart": '<path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>',
    "smile": '<circle cx="12" cy="12" r="10"/><path d="M8 14s1.5 2 4 2 4-2 4-2"/><path d="M9 9h.01M15 9h.01"/>',
    "star": '<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>',
    "menu": '<path d="M3 12h18M3 6h18M3 18h18"/>',
    "chevron": '<polyline points="6 9 12 15 18 9"/>',
    "arrow-up": '<path d="M12 19V5"/><polyline points="5 12 12 5 19 12"/>',
    "instagram": '<rect x="2" y="2" width="20" height="20" rx="5"/><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"/><path d="M17.5 6.5h.01"/>',
    "linkedin": '<path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4V9h4v1.5"/><rect x="2" y="9" width="4" height="12"/><circle cx="4" cy="4" r="2"/>',
    "facebook": '<path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z"/>',
    "whatsapp": '<path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/>',
}

# ----------------------------------------------------------------------------
# Mirror extraction helpers — page copy comes verbatim from the mirror
# ----------------------------------------------------------------------------
def read_mirror(name):
    p = MIRROR / "pages" / name if name != "index.html" else MIRROR / name
    s = p.read_text(encoding="utf-8")
    # decode Cloudflare-obfuscated e-mails back to plain text, then swap in
    # the new placeholder e-mail (old address must not ship on the new site)
    def decode(m):
        b = bytes.fromhex(m.group(1)); k = b[0]
        return "".join(chr(c ^ k) for c in b[1:])
    s = re.sub(r'<a href="/cdn-cgi/l/email-protection[^>]*>.*?</a>', lambda m: CONFIG["email"], s, flags=re.S)
    s = re.sub(r'<span class="__cf_email__[^>]*data-cfemail="([0-9a-f]+)"[^>]*>.*?</span>', decode, s, flags=re.S)
    s = s.replace("ops@ctw-travels.co.uk", CONFIG["email"])
    s = s.replace("info@ctw-travels.co.uk", CONFIG["email"])
    # production typo fixes (flagged to owner)
    s = s.replace("Cross The Wrold", "Cross The World")
    return s

def paragraphs_between(src, start_marker, stop_marker=None):
    """All <p>…</p> blocks after start_marker (up to stop_marker if given)."""
    i = src.find(start_marker)
    if i < 0:
        raise SystemExit(f"marker not found: {start_marker!r}")
    seg = src[i:]
    if stop_marker:
        j = seg.find(stop_marker)
        if j > 0:
            seg = seg[:j]
    return re.findall(r"<p[^>]*>.*?</p>", seg, re.S)

def clean_p(p):
    """Normalise a mirror paragraph: drop inline styles, keep <b>/<br>."""
    p = re.sub(r'\s*style="[^"]*"', "", p)
    p = re.sub(r"\s+", " ", p).strip()
    return p

def banner_of(src):
    h5 = re.search(r'<div class="banner-header.*?<h5>(.*?)</h5>', src, re.S)
    h1 = re.search(r'<div class="banner-header.*?<h1>(.*?)</h1>', src, re.S)
    return (h5.group(1).strip() if h5 else "", h1.group(1).strip() if h1 else "")

# ----------------------------------------------------------------------------
# Shared chrome
# ----------------------------------------------------------------------------
SERVICES = [
    ("global-travel-management", "Global Travel Management"),
    ("technology", "Technology"),
    ("dedicated-team", "Dedicated Team"),
    ("business-flights", "Business Flights"),
    ("hotels", "Hotels"),
    ("car", "Business Car Hire & Rental"),   # typo fixed ("Hair" → "Hire")
    ("implementation", "Implementation"),
    ("reporting", "Management Information Reporting"),
    ("groups", "Blueline Groups, Conferences and Incentives"),
]

def head(title, desc, path, og_image="/img/slider/hero-citadel-walls.webp",
         lcp_image="/img/banner-erbil.webp"):
    # lcp_image is the above-the-fold background for this page; preloading it
    # lets the browser fetch it in parallel with the CSS instead of after it.
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{CONFIG['domain']}{path}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{CONFIG['brand']}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{CONFIG['domain']}{path}">
<meta property="og:image" content="{CONFIG['domain']}{og_image}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/png" href="/img/favicon.png">
<link rel="preload" href="{lcp_image}" as="image" fetchpriority="high">
<link rel="preload" href="/fonts/poppins-700.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/fonts/barlow-400.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/css/style.css">
</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>
"""

def navbar(active):
    def cur(slug):
        return ' aria-current="page"' if active == slug else ""
    sub = "\n".join(
        f'      <li><a href="/{slug}/">{html.escape(label)}</a></li>'
        for slug, label in SERVICES)
    sub_active = any(active == slug for slug, _ in SERVICES)
    return f"""<header class="site-header">
  <div class="bar">
    <a class="logo" href="/"><img src="/img/logo-light.png" alt="Blueline Travels" width="58" height="58"></a>
    <button class="nav-toggle" aria-expanded="false" aria-controls="nav" aria-label="Menu">{icon('menu')}</button>
    <ul class="nav" id="nav">
      <li><a href="/"{cur('home')}>Home</a></li>
      <li><a href="/about/"{cur('about')}>About</a></li>
      <li class="has-sub">
        <a href="/global-travel-management/" aria-expanded="false"{' aria-current="page"' if sub_active else ''}>What We Do <span class="chev">{icon('chevron')}</span></a>
        <ul class="sub">
{sub}
        </ul>
      </li>
      <li><a href="/contact-us/"{cur('contact')}>Contact</a></li>
      <li class="cta"><a href="/contact-us/">Get in Touch</a></li>
    </ul>
  </div>
</header>
"""

def footer():
    addr = "<br>".join(html.escape(x) for x in CONFIG["address_lines"])
    return f"""<footer class="footer">
  <div class="container">
    <div class="footer-contact">
      <div class="item">
        <div class="icon">{icon('phone')}</div>
        <div><h4>Call us</h4><p><a href="tel:{CONFIG['phone_tel']}">{CONFIG['phone_display']}</a></p></div>
      </div>
      <div class="item">
        <div class="icon">{icon('mail')}</div>
        <div><h4>Write to us</h4><p><a href="mailto:{CONFIG['email']}">{CONFIG['email']}</a></p></div>
      </div>
      <div class="item">
        <div class="icon">{icon('pin')}</div>
        <div><h4>Address</h4><p>{addr}</p></div>
      </div>
    </div>
    <div class="footer-mid">
      <div class="flogo">
        <img src="/img/logo-light.png" alt="Blueline Travels" width="74" height="74">
        <ul class="social">
          <li><a href="{CONFIG['social']['instagram']}" aria-label="Instagram" rel="external noopener" target="_blank">{icon('instagram')}</a></li>
          <li><a href="{CONFIG['social']['linkedin']}" aria-label="LinkedIn" rel="external noopener" target="_blank">{icon('linkedin')}</a></li>
          <li><a href="{CONFIG['social']['facebook']}" aria-label="Facebook" rel="external noopener" target="_blank">{icon('facebook')}</a></li>
        </ul>
      </div>
      <div>
        <h3>Quick Links</h3>
        <ul>
          <li><a href="/">Home</a></li>
          <li><a href="/about/">About Us</a></li>
          <li><a href="/contact-us/">Contact Us</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <p>© <span id="year"></span> {html.escape(CONFIG['brand'])}. All rights reserved. · <a href="/credits/">Photo credits</a></p>
      <p class="dev-credit">Developed &amp; Designed by <a href="{CONFIG['dev_url']}" rel="external noopener" target="_blank">{html.escape(CONFIG['dev_name'])}</a></p>
    </div>
  </div>
</footer>
<button class="progress-ring" aria-label="Back to top">
  <svg class="ring" viewBox="0 0 46 46"><circle cx="23" cy="23" r="20"/></svg>
  {icon('arrow-up', 'arrow')}
</button>
<script src="/js/main.js" defer></script>
</body>
</html>
"""

def page_banner(eyebrow, title):
    return f"""<div class="page-banner" style="background-image:url('/img/banner-erbil.webp')">
  <div class="container">
    <div class="eyebrow">{eyebrow}</div>
    <h1>{title}</h1>
  </div>
</div>
"""

def write(path, content):
    p = OUT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print(f"  {path}")

# ----------------------------------------------------------------------------
# Home page
# ----------------------------------------------------------------------------
def build_home():
    src = read_mirror("index.html")

    about_ps = paragraphs_between(src, 'CROSS THE <span>WORLD</span>', "phone-call")
    # drop the stray editing artifact that shipped on the original site
    about_ps = [p for p in about_ps if "further assistance" not in p]

    faq_ps = [clean_p(p) for p in paragraphs_between(
        src, "Common Corporate Travel Questions", "</section>")]

    sus = re.findall(r'<h3 class="mt-0 font-600">(.*?)</h3>\s*<p[^>]*>(.*?)</p>', src, re.S)
    sus_cols = "\n".join(
        f'      <div><h3>{h.strip()}</h3><p>{" ".join(p.split())}</p></div>'
        for h, p in sus[:2])

    inc_ps = [clean_p(p) for p in paragraphs_between(
        src, "Comprehensive Incentive Travel Planning Services",
        "<b>What Is A Business Travel Agent?")]  # skip FAQ trio duplicated in the original

    feats = re.findall(
        r'<i class="(ti-[a-z-]+) white-color"></i>\s*</div>\s*'
        r'<h3 class="mt-0 font-600">(.*?)</h3>\s*<div class="dis mb-4">\s*(.*?)\s*</div>',
        src, re.S)
    fmap = {"ti-crown": "award", "ti-money": "dollar", "ti-heart": "heart",
            "ti-face-smile": "smile", "ti-wand": "star", "ti-user": "user"}
    feat_html = "\n".join(
        f"""      <div class="feature fade-up">
        <div class="icon">{icon(fmap.get(i, 'star'))}</div>
        <h3>{t.strip()}</h3>
        <p>{' '.join(d.split())}</p>
      </div>""" for i, t, d in feats)

    partners = re.findall(r'<img src="/img/partners/([^"]+)" alt="([^"]*)"', src)
    logos = "\n".join(
        f'        <img src="/img/partners/{f}" alt="{a or f.rsplit(".",1)[0]}" height="64" loading="lazy">'
        for f, a in partners)

    body = f"""{navbar('home')}
<main id="main">
<section class="hero" aria-label="Blueline Travels — Mosul">
  <div class="slide active" style="background-image:url('/img/slider/hero-citadel-walls.webp')"></div>
  <div class="slide" data-bg="/img/slider/hero-skyline-night.webp"></div>
  <div class="slide" data-bg="/img/slider/hero-citadel.webp"></div>
  <div class="caption">
    <div class="eyebrow">Embark on Unmatched Journeys</div>
    <h1>Discover Excellence in Travel with <span class="outline">Blueline</span></h1>
  </div>
</section>

<section class="section" id="about">
  <div class="container split">
    <div class="fade-up">
      <div class="eyebrow">About Us</div>
      <h2 class="section-title">About <span>Blueline</span> Travels</h2>
      {chr(10).join('      ' + clean_p(p) for p in about_ps)}
      <div class="phone-call">
        <div class="icon">{icon('whatsapp')}</div>
        <div>
          <p>For information</p>
          <a href="{CONFIG['whatsapp']}">{CONFIG['phone_display']}</a>
        </div>
      </div>
    </div>
    <div class="fade-up img-badge">
      <div class="about-img"><img src="/img/about.webp" alt="Traveler reviewing a flight itinerary at the airport" width="900" height="600" loading="lazy"></div>
      <svg class="roundel" viewBox="0 0 300 300">
        <defs><path id="cp" d="M 150,150 m -60,0 a 60,60 0 0,1 120,0 a 60,60 0 0,1 -120,0"/></defs>
        <text><textPath href="#cp"> - BLUELINE - BLUELINE - BLUELINE - BLUELINE</textPath></text>
      </svg>
    </div>
  </div>
</section>

<section class="stats section" data-bg-section="/img/banner-erbil.webp">
  <div class="container">
    <div class="stats-grid">
      <div class="stat fade-up"><div class="icon">{icon('send')}</div><h3 data-count="250">+250</h3><h4>Airlines</h4></div>
      <div class="stat fade-up"><div class="icon">{icon('building')}</div><h3 data-count="5000">+5,000</h3><h4>Hotels</h4></div>
      <div class="stat fade-up"><div class="icon">{icon('users')}</div><h3 data-count="5500">+5,500</h3><h4>Happy Customers</h4></div>
      <div class="stat fade-up"><div class="icon">{icon('tag')}</div><h3 data-count="987000">+987,000</h3><h4>Social Visitors Monthly</h4></div>
    </div>
  </div>
</section>

<section class="section">
  <div class="container split split--rev">
    <div class="fade-up about-img">
      <img src="/img/corporate.webp" alt="Corporate travel consultant assisting business clients" width="900" height="600" loading="lazy">
    </div>
    <div class="fade-up">
      <div class="eyebrow">FAQ</div>
      <h2 class="section-title">Common Corporate Travel Questions</h2>
      {chr(10).join('      ' + p for p in faq_ps)}
    </div>
  </div>
</section>

<section class="band section" data-bg-section="/img/green-plane.webp">
  <div class="container">
    <div class="band-cols">
{sus_cols}
    </div>
  </div>
</section>

<section class="section section--tint">
  <div class="container">
    <h2 class="section-title center">Comprehensive Incentive Travel Planning Services</h2>
    <div class="split split--rev" style="margin-top:50px">
      <div class="fade-up">
        <img src="/img/corporate-travel-1.webp" alt="Business team on an incentive trip" width="900" height="600" loading="lazy" style="margin-bottom:30px">
        <img src="/img/corporate-travel-2.webp" alt="Colleagues travelling together for a corporate event" width="900" height="600" loading="lazy" style="margin-bottom:30px">
        <img src="/img/corporate-travel-3.webp" alt="Corporate group at a conference venue" width="900" height="600" loading="lazy">
      </div>
      <div class="fade-up">
        {chr(10).join('        ' + p for p in inc_ps)}
      </div>
    </div>
  </div>
</section>

<section class="section partners">
  <div class="container">
    <h2 class="section-title">Our Partners</h2>
  </div>
  <div class="partners-track">
{logos}
{logos}
  </div>
</section>

<section class="section">
  <div class="container">
    <h2 class="section-title">Why Choose <span>Us</span>?</h2>
    <div class="features">
{feat_html}
    </div>
  </div>
</section>
</main>
{footer()}"""

    write("index.html", head(
        "Blueline Travels Mosul | Corporate Travel Agency",
        "Blueline Travels Mosul — corporate travel management, business flights, hotels and group travel from Mosul, Iraq.",
        "/", lcp_image="/img/slider/hero-citadel-walls.webp") + body)

# ----------------------------------------------------------------------------
# About page
# ----------------------------------------------------------------------------
def build_about():
    src = read_mirror("about.html")
    eyebrow, h1 = banner_of(src)

    intro_ps = [clean_p(p) for p in paragraphs_between(
        src, '<section class="about cover section-padding">', "</section>")]
    offer_ps = [clean_p(p) for p in paragraphs_between(
        src, "WHAT CAN WE", "img-exp")]
    offer_ps = [re.sub(r'\s*class="white-color"', "", p) for p in offer_ps]

    testi_seg = src.split('class="testimonials"', 1)[1]
    testi_h5 = re.search(r'<h5>(.*?)</h5>', testi_seg, re.S).group(1).strip()
    testi_lis = re.findall(r'<li class="white-color">(.*?)</li>', testi_seg)

    faq_ps = [clean_p(p) for p in paragraphs_between(
        src, "Common Corporate Travel Questions", "</section>")]

    body = f"""{navbar('about')}
<main id="main">
{page_banner(eyebrow, h1)}
<section class="section">
  <div class="container split">
    <div class="fade-up">
      {chr(10).join('      ' + p for p in intro_ps)}
    </div>
    <div class="fade-up about-img">
      <img src="/img/about.webp" alt="Blueline travel consultant planning an itinerary" width="900" height="600" loading="lazy">
    </div>
  </div>
</section>

<section class="section section--navy">
  <div class="container split">
    <div class="fade-up">
      <h2 class="section-title" style="color:#fff">What Can We <span>Offer</span> You?</h2>
      {chr(10).join('      ' + p for p in offer_ps)}
    </div>
    <div class="fade-up about-img">
      <img src="/img/about1.webp" alt="Business traveller boarding a flight" width="900" height="600" loading="lazy">
    </div>
  </div>
</section>

<section class="band section" data-bg-section="/img/banner-erbil.webp">
  <div class="container">
    <div class="stars" aria-hidden="true">★★★★★</div>
    <h3 style="max-width:760px">{testi_h5}</h3>
    <ul class="checklist">
      {chr(10).join('      <li>' + li + '</li>' for li in testi_lis)}
    </ul>
  </div>
</section>

<section class="section">
  <div class="container split split--rev">
    <div class="fade-up about-img">
      <img src="/img/corporate.webp" alt="Corporate travel consultant assisting business clients" width="900" height="600" loading="lazy">
    </div>
    <div class="fade-up">
      <div class="eyebrow">FAQ</div>
      <h2 class="section-title">Common Corporate Travel Questions</h2>
      {chr(10).join('      ' + p for p in faq_ps)}
    </div>
  </div>
</section>
</main>
{footer()}"""

    write("about/index.html", head(
        "About Us | Blueline Travels Mosul — Dedicated Corporate Travel Agency",
        "A dedicated corporate travel agency, 100% focused on delivering the highest quality services and support to your company and your business travellers.",
        "/about/") + body)

# ----------------------------------------------------------------------------
# Service pages
# ----------------------------------------------------------------------------
SERVICE_IMG = {
    "global-travel-management": ("service-8.webp", "World map with global travel connections"),
    "technology": ("service-7.webp", "Travel booking technology on a laptop"),
    "dedicated-team": ("service-6.webp", "Dedicated travel support team at work"),
    "business-flights": ("service-5.webp", "Aircraft cabin on a business flight"),
    "hotels": ("service-1.webp", "Modern hotel room prepared for a business guest"),
    "car": ("service-2.webp", "Executive rental car ready for pickup"),
    "implementation": ("service-11.webp", "Travel programme implementation planning"),
    "reporting": ("service-9.webp", "Travel management reports and analytics"),
    "groups": ("service-77.webp", "Conference hall prepared for a corporate group event"),
}
SERVICE_DESC = {
    "global-travel-management": "Tailor-made corporate travel services that are truly global — for multinationals and growing businesses alike.",
    "technology": "Cutting-edge travel technology combined with personal service, so your business travels smarter.",
    "dedicated-team": "A dedicated account manager and an experienced team of travel specialists for your business.",
    "business-flights": "A price promise on business flights, with access to global airfare availability and negotiated rates.",
    "hotels": "Hotel and accommodation booking through an extensive network of international chains and boutique options.",
    "car": "Business car hire and rental with leading vehicle brands, arranged end-to-end by our team.",
    "implementation": "Smooth implementation of your corporate travel programme, handled by experienced specialists.",
    "reporting": "Customisable management information reporting for full visibility of your travel spend.",
    "groups": "Groups, conferences and incentives — organised end-to-end by our expert group travel department.",
}

def build_services():
    for slug, label in SERVICES:
        src = read_mirror(f"{slug}.html")
        eyebrow, h1 = banner_of(src)
        ps = [clean_p(p) for p in paragraphs_between(
            src, '<section class="about cover section-padding">', "</section>")]
        # first paragraph is an all-caps lead-in — style it as an eyebrow
        lead, rest = ps[0], ps[1:]
        lead_txt = re.sub(r"</?[a-z][^>]*>", "", lead)
        img, alt = SERVICE_IMG[slug]

        body = f"""{navbar(slug)}
<main id="main">
{page_banner(eyebrow, h1)}
<section class="section">
  <div class="container split">
    <div class="fade-up">
      <div class="eyebrow">{lead_txt}</div>
      {chr(10).join('      ' + p for p in rest)}
      <a class="btn" href="/contact-us/"><span>Get in Touch</span></a>
    </div>
    <div class="fade-up about-img">
      <img src="/img/{img}" alt="{alt}" width="1000" height="667" loading="lazy">
    </div>
  </div>
</section>
</main>
{footer()}"""

        write(f"{slug}/index.html", head(
            f"{label} | Blueline Travels Mosul",
            SERVICE_DESC[slug],
            f"/{slug}/") + body)

# ----------------------------------------------------------------------------
# Contact page
# ----------------------------------------------------------------------------
def build_contact():
    addr = "<br>".join(html.escape(x) for x in CONFIG["address_lines"])
    body = f"""{navbar('contact')}
<main id="main">
{page_banner('Blueline Travels', 'Contact Us')}
<section class="section">
  <div class="container split">
    <div class="fade-up">
      <h2 class="section-title">Blueline Travels <span>Mosul</span></h2>
      <p>{html.escape(CONFIG['registration'])}</p>
      <div class="phone-call">
        <div class="icon">{icon('phone')}</div>
        <div><p>Phone</p><a href="tel:{CONFIG['phone_tel']}">{CONFIG['phone_display']}</a></div>
      </div>
      <div class="phone-call">
        <div class="icon">{icon('mail')}</div>
        <div><p>Email Address</p><a href="mailto:{CONFIG['email']}">{CONFIG['email']}</a></div>
      </div>
      <div class="phone-call">
        <div class="icon">{icon('pin')}</div>
        <div><p>Location</p><strong>{addr}</strong></div>
      </div>
    </div>
    <div class="fade-up">
      <h2 class="section-title" style="font-size:30px">Get in touch</h2>
      <form class="contact-form" method="POST" action="{CONFIG['form_action']}" data-mailto="{CONFIG['email']}">
        <p class="form-status" role="status"></p>
        <div class="form-grid">
          <input name="name" type="text" placeholder="Your Name *" required aria-label="Your name">
          <input name="email" type="email" placeholder="Your Email *" required aria-label="Your e-mail">
          <input name="phone" type="tel" placeholder="Your Number *" required aria-label="Your phone number">
          <input name="subject" type="text" placeholder="Subject *" required aria-label="Subject">
          <textarea class="wide" name="message" rows="5" placeholder="Message *" required aria-label="Message"></textarea>
          <div class="wide"><button class="btn" type="submit"><span>Send Message</span></button></div>
        </div>
      </form>
    </div>
  </div>
</section>
</main>
{footer()}"""

    write("contact-us/index.html", head(
        "Contact Us | Blueline Travels Mosul",
        "Get in touch with Blueline Travels in Mosul, Iraq — phone, e-mail, or the contact form.",
        "/contact-us/") + body)

# ----------------------------------------------------------------------------
# Credits, 404, robots, sitemap
# ----------------------------------------------------------------------------
def build_credits():
    photos = json.load(open(Path(__file__).parent / "erbil-photos.json"))
    used = {
        "cand-citadel-pano.jpg": "Homepage hero — Erbil Citadel walls",
        "cand-night2025.png": "Homepage hero — Erbil skyline at night",
        "cand-citadel-day.jpg": "Homepage hero — aerial view of Erbil Citadel",
        "cand-skyline-night.jpg": "Page banners — Erbil by night",
    }
    rows = []
    for title, m in photos.items():
        if m["file"] in used:
            artist = re.sub(r"<[^>]+>", "", m["artist"]).strip() or "Unknown"
            rows.append(
                f'      <li>{used[m["file"]]}: '
                f'<a href="{m["page"]}" rel="external noopener" target="_blank">'
                f'{html.escape(title.replace("File:", ""))}</a> '
                f'by {html.escape(artist)}, licensed {m["lic"]} via Wikimedia Commons.</li>')
    body = f"""{navbar('')}
<main id="main">
{page_banner('Blueline Travels', 'Photo Credits')}
<section class="section">
  <div class="container">
    <p>Photographs of Erbil used on this site are the work of the following photographers, used under their respective free licenses:</p>
    <ul class="checklist">
{chr(10).join(rows)}
    </ul>
    <p>Licenses: <a href="https://creativecommons.org/licenses/by/4.0/" rel="external noopener" target="_blank">CC BY 4.0</a> ·
       <a href="https://creativecommons.org/licenses/by-sa/2.0/" rel="external noopener" target="_blank">CC BY-SA 2.0</a> ·
       <a href="https://creativecommons.org/licenses/by-sa/4.0/" rel="external noopener" target="_blank">CC BY-SA 4.0</a> ·
       <a href="https://creativecommons.org/publicdomain/zero/1.0/" rel="external noopener" target="_blank">CC0</a></p>
  </div>
</section>
</main>
{footer()}"""
    write("credits/index.html", head(
        "Photo Credits | Blueline Travels Mosul",
        "Attribution for the openly licensed photographs of Erbil used on this website.",
        "/credits/") + body)

def build_404():
    body = f"""{navbar('')}
<main id="main">
{page_banner('Blueline Travels', 'Page Not Found')}
<section class="section center">
  <div class="container">
    <p>The page you are looking for doesn't exist or has moved.</p>
    <a class="btn" href="/"><span>Back to Home</span></a>
  </div>
</section>
</main>
{footer()}"""
    write("404.html", head(
        "Page Not Found | Blueline Travels Mosul",
        "The page you are looking for could not be found.",
        "/404.html") + body)

def build_seo():
    urls = ["/", "/about/", "/contact-us/", "/credits/"] + [f"/{s}/" for s, _ in SERVICES]
    entries = "\n".join(
        f"  <url><loc>{CONFIG['domain']}{u}</loc></url>" for u in urls)
    write("sitemap.xml",
          '<?xml version="1.0" encoding="UTF-8"?>\n'
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
          f"{entries}\n</urlset>\n")
    write("robots.txt",
          f"User-agent: *\nAllow: /\n\nSitemap: {CONFIG['domain']}/sitemap.xml\n")

# ----------------------------------------------------------------------------
if __name__ == "__main__":
    print("Building site/ …")
    build_home()
    build_about()
    build_services()
    build_contact()
    build_credits()
    build_404()
    build_seo()
    print("Done.")
