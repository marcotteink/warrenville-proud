#!/usr/bin/env python3
"""
Warrenville Proud - static site generator (SEO + GEO optimized).

Reads data/events.json, data/posts.json, data/sponsors.json and writes:
  index.html, events.html, about.html, blog/index.html, blog/<slug>.html,
  sitemap.xml, robots.txt, llms.txt

Every page gets: title/description, canonical, Open Graph + Twitter cards,
local geo meta, and JSON-LD structured data (Organization, WebSite, Event,
BlogPosting, BreadcrumbList, FAQPage). No third-party dependencies.

Run from the repo root:  python3 scripts/build_site.py
Add --rotate to advance the Local Business Spotlight.
Set REF_DATE=YYYY-MM-DD to control which events count as "upcoming".
"""
import json, os, html, sys
from datetime import date, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

SITE_NAME = "Warrenville Proud"
SITE_TAG = "Good things happening in our town"
SITE_URL = "https://warrenvilleproud.com"
OG_IMAGE = SITE_URL + "/assets/og-image.png"
CITY, STATE, ZIP = "Warrenville", "IL", "60555"
LAT, LON = "41.8186", "-88.1762"

# --- analytics + search-engine verification (fill in once you have the codes) ---
GA4_ID = ""          # GA4 Measurement ID, e.g. "G-XXXXXXXXXX"
GSC_VERIFY = ""      # Google Search Console <meta> token (optional; DNS TXT also works)
BING_VERIFY = ""     # Bing Webmaster Tools <meta> token (optional)

# --- the funnel target (Sound & Fury) ---
SF_URL = "https://soundandfuryprint.com"
SF_NAME = "Sound & Fury Print Shop"

def load(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as f:
        return json.load(f)

def ref_date():
    v = os.environ.get("REF_DATE")
    return datetime.strptime(v, "%Y-%m-%d").date() if v else date.today()

def parse(d):
    return datetime.strptime(d, "%Y-%m-%d").date()

def nice_date(d):
    return parse(d).strftime("%A, %B %-d, %Y")

def short_date(d):
    return parse(d).strftime("%b %-d, %Y")

def A(s):
    """Escape for use in HTML text and attributes."""
    return html.escape(str(s), quote=True)

def canon(path):
    return SITE_URL + "/" + path if path else SITE_URL + "/"

def utm(url, content):
    """Tag Sound & Fury links so the Warrenville Proud -> Sound & Fury funnel shows up in GA4.
    Non-Sound-&-Fury links are returned unchanged."""
    if "soundandfuryprint.com" not in url:
        return url
    sep = "&" if "?" in url else "?"
    return (f"{url}{sep}utm_source=warrenvilleproud&utm_medium=referral"
            f"&utm_campaign=sponsorship&utm_content={content}")

def jsonld(obj):
    return ('<script type="application/ld+json">'
            + json.dumps(obj, ensure_ascii=False) + "</script>")

# ---------- site-wide structured data ----------
def org_node():
    return {
        "@context": "https://schema.org", "@type": "Organization",
        "@id": SITE_URL + "/#org", "name": SITE_NAME, "url": SITE_URL + "/",
        "logo": OG_IMAGE, "image": OG_IMAGE,
        "description": "A free, community-run guide to events and local life in Warrenville, Illinois.",
        "areaServed": {"@type": "City", "name": "Warrenville, Illinois"},
        "knowsAbout": ["Warrenville Illinois events", "DuPage County community events", "local Warrenville news"],
        "sponsor": {"@type": "Organization", "name": "Sound & Fury Print Shop",
                    "url": "https://soundandfuryprint.com",
                    "description": "Warrenville-based screen printing and DTF custom apparel shop."}
    }

def website_node():
    return {
        "@context": "https://schema.org", "@type": "WebSite",
        "@id": SITE_URL + "/#website", "name": SITE_NAME, "url": SITE_URL + "/",
        "inLanguage": "en-US", "publisher": {"@id": SITE_URL + "/#org"}
    }

def breadcrumb(trail):
    return {
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": name, "item": canon(path)}
            for i, (name, path) in enumerate(trail)
        ]
    }

def event_node(e):
    node = {
        "@type": "Event", "name": e["title"],
        "startDate": e["date"], "endDate": e.get("enddate", e["date"]),
        "eventStatus": "https://schema.org/EventScheduled",
        "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
        "location": {"@type": "Place", "name": e.get("location", "Warrenville, IL"),
                     "address": {"@type": "PostalAddress", "addressLocality": CITY,
                                 "addressRegion": STATE, "postalCode": ZIP, "addressCountry": "US"}},
        "description": e.get("blurb", ""), "image": OG_IMAGE
    }
    if e.get("url"):
        node["url"] = e["url"]
    if e.get("source"):
        node["organizer"] = {"@type": "Organization", "name": e["source"]}
    return node

def events_itemlist(events):
    return {
        "@context": "https://schema.org", "@type": "ItemList",
        "name": "Upcoming events in Warrenville, Illinois",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "item": event_node(e)}
            for i, e in enumerate(events)
        ]
    }

# ---------- page chrome ----------
def ribbon(sp):
    f = sp["founding"]
    return (f'<div class="ribbon">Founding sponsor: '
            f'<a href="{A(utm(f["url"], "ribbon"))}">{A(f["name"])}</a> . {A(f["short"])}</div>')

def page_open(base, active, *, title, desc, path, og_type="website", extra_ld=None, sp=None):
    def cls(name): return ' style="color:var(--prairie)"' if name == active else ''
    url = canon(path)
    ld = [org_node(), website_node()] + (extra_ld or [])
    ld_html = "\n".join(jsonld(o) for o in ld)
    analytics = ""
    if GA4_ID:
        analytics += (f'<script async src="https://www.googletagmanager.com/gtag/js?id={GA4_ID}"></script>\n'
                      "<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}"
                      f"gtag('js',new Date());gtag('config','{GA4_ID}');</script>\n")
    if GSC_VERIFY:
        analytics += f'<meta name="google-site-verification" content="{GSC_VERIFY}">\n'
    if BING_VERIFY:
        analytics += f'<meta name="msvalidate.01" content="{BING_VERIFY}">\n'
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
{analytics}<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{A(title)}</title>
<meta name="description" content="{A(desc)}">
<link rel="canonical" href="{url}">
<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1">
<meta name="author" content="{SITE_NAME}">
<meta name="geo.region" content="US-IL">
<meta name="geo.placename" content="Warrenville, Illinois">
<meta name="geo.position" content="{LAT};{LON}">
<meta name="ICBM" content="{LAT}, {LON}">
<meta name="theme-color" content="#2f6b3e">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="{SITE_NAME}">
<meta property="og:title" content="{A(title)}">
<meta property="og:description" content="{A(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{OG_IMAGE}">
<meta property="og:locale" content="en_US">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{A(title)}">
<meta name="twitter:description" content="{A(desc)}">
<meta name="twitter:image" content="{OG_IMAGE}">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/png" href="{base}assets/favicon.png" sizes="96x96">
<link rel="apple-touch-icon" href="{base}assets/apple-touch-icon.png">
<link rel="sitemap" type="application/xml" href="{SITE_URL}/sitemap.xml">
<link rel="alternate" type="application/rss+xml" title="{SITE_NAME} blog" href="{SITE_URL}/feed.xml">
<link rel="stylesheet" href="{base}assets/style.css">
{ld_html}
</head>
<body>
{ribbon(sp)}
<header class="site"><div class="wrap navbar">
  <a class="brand" href="{base}index.html" style="text-decoration:none">
    <span class="name">{SITE_NAME}</span>
    <span class="tag">{SITE_TAG}</span>
  </a>
  <nav class="links">
    <a href="{base}index.html"{cls('home')}>Home</a>
    <a href="{base}events.html"{cls('events')}>Events</a>
    <a href="{base}things-to-do-in-warrenville.html"{cls('guide')}>Things to Do</a>
    <a href="{base}blog/index.html"{cls('blog')}>Blog</a>
    <a href="{base}about.html"{cls('about')}>About</a>
    <a href="{base}index.html#sponsor"{cls('sponsor')}>Sponsor</a>
  </nav>
</div></header>
"""

def footer(base, sp):
    f = sp["founding"]
    return f"""
<footer class="site"><div class="wrap">
  <div class="cols">
    <div style="max-width:340px">
      <h4>{SITE_NAME}</h4>
      <p>A free community resource for Warrenville, Illinois. Events, news, and the good stuff happening around town.</p>
    </div>
    <div>
      <h4>Explore</h4>
      <p><a href="{base}index.html">Home</a><br>
      <a href="{base}events.html">Event calendar</a><br>
      <a href="{base}things-to-do-in-warrenville.html">Things to do in Warrenville</a><br>
      <a href="{base}custom-shirts-warrenville.html">Custom shirts in Warrenville</a><br>
      <a href="{base}blog/index.html">Blog</a><br>
      <a href="{base}about.html">About</a><br>
      <a href="{base}index.html#sponsor">Become a sponsor</a></p>
    </div>
    <div style="max-width:300px">
      <h4>Founding sponsor</h4>
      <p><a href="{A(utm(f['url'], 'footer'))}">{A(f['name'])}</a><br>{A(f['short'])}</p>
    </div>
  </div>
  <div class="fine">
    Event details are gathered from public listings and always link back to the official source
    (<a href="https://www.warrenville.il.us/395/Community-Events">City of Warrenville</a>,
    <a href="https://www.warrenvilleparks.org/events/">Park District</a>,
    <a href="https://www.warrenville.com/events">Library</a>,
    <a href="http://westerndupagechamber.chambermaster.com/events/calendar">Western DuPage Chamber</a>).
    Please confirm times before you go. {SITE_NAME} is independently run and proudly sponsored by local Warrenville businesses.
  </div>
</div></footer>
</body>
</html>"""

# ---------- visible components ----------
def event_card(e):
    dt = parse(e["date"])
    end = ""
    if e.get("enddate") and e["enddate"] != e["date"]:
        end = f' - {parse(e["enddate"]).strftime("%b %-d")}'
    det = " . ".join(x for x in [e.get("time", ""), e.get("location", "")] if x)
    return f"""<div class="event">
  <div class="when"><div class="mo">{dt.strftime('%b').upper()}</div><div class="day">{dt.strftime('%-d')}</div><div class="dow">{dt.strftime('%a')}{end}</div></div>
  <div class="body">
    <span class="pill">{A(e.get('category','Event'))}</span>
    <h3>{A(e['title'])}</h3>
    <div class="det">{A(det)}</div>
    <p>{A(e.get('blurb',''))}</p>
    <a class="more" href="{A(e.get('url','#'))}">Details via {A(e.get('source',''))} &rarr;</a>
  </div>
</div>"""

def post_card(p, base):
    return f"""<div class="card">
  <span class="meta">{A(p.get('kicker','Post'))} . {short_date(p['date'])}</span>
  <h3><a href="{base}blog/{p['slug']}.html" style="color:inherit">{A(p['title'])}</a></h3>
  <p>{A(p['excerpt'])}</p>
  <a class="more" href="{base}blog/{p['slug']}.html">Read more &rarr;</a>
</div>"""

def spotlight_block(sp):
    rot = sp["spotlight_rotation"]
    s = rot[sp.get("spotlight_index", 0) % len(rot)]
    founding_line = '<div class="founding">Founding sponsor of Warrenville Proud</div>' if s.get("founding") else ""
    btn = (f'<a class="btn" href="{A(utm(s["url"], "spotlight"))}">Visit {A(s["name"])}</a>'
           if s["url"] != "#sponsor" else '<a class="btn" href="#sponsor">Become a sponsor</a>')
    return f"""<div class="spotlight">
  <div class="kicker">Local Business Spotlight</div>
  <h3>{A(s['name'])}</h3>
  <p>{A(s['blurb'])}</p>
  {btn}
  {founding_line}
</div>"""

def sponsor_cta():
    return """<div id="sponsor" class="sponsor-cta">
  <h3>Keep Warrenville Proud free. Sponsor it.</h3>
  <p>This site is read by neighbors looking for what to do and where to go in town. A sponsorship puts your business in front of them and helps keep local info free for everyone.</p>
  <a class="btn" href="mailto:hello@warrenvilleproud.com?subject=Sponsoring%20Warrenville%20Proud">Become a sponsor</a>
</div>"""

def apparel_cta(sp, content, base=""):
    """Contextual, non-spammy bridge from community content to the sponsor's shop."""
    f = sp["founding"]
    return f"""<div class="sponsor-cta">
  <h3>Outfitting a team, school, or event in Warrenville?</h3>
  <p>{A(f['blurb'])} Team jerseys, school spirit wear, fundraiser tees, business gear, and event merch, printed right here in town.</p>
  <a class="btn" href="{A(utm(f['url'], content))}">{A(f['cta'])} from {A(f['name'])} &rarr;</a>
  <p style="margin-top:12px;font-size:.95em"><a href="{base}custom-shirts-warrenville.html">See how local custom apparel works &rarr;</a></p>
</div>"""

def local_business_node():
    """LocalBusiness entity for Sound & Fury (helps search + AI engines recognize the shop)."""
    return {
        "@context": "https://schema.org", "@type": "LocalBusiness",
        "@id": SF_URL + "/#business", "name": SF_NAME, "url": SF_URL, "image": OG_IMAGE,
        "description": ("Warrenville-based screen printing and DTF custom apparel shop serving "
                        "local teams, schools, businesses, fundraisers, and events."),
        "address": {"@type": "PostalAddress", "addressLocality": CITY,
                    "addressRegion": STATE, "postalCode": ZIP, "addressCountry": "US"},
        "areaServed": [{"@type": "City", "name": "Warrenville, Illinois"},
                       {"@type": "AdministrativeArea", "name": "DuPage County, Illinois"}],
        "knowsAbout": ["screen printing", "DTF transfers", "custom t-shirts",
                       "team apparel", "school spirit wear", "event merchandise"],
        "makesOffer": [
            {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "Screen printing"}},
            {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "DTF transfers"}},
            {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "Custom apparel and merchandise"}},
        ],
    }

APPAREL_FAQ = [
    ("Where can I get custom t-shirts in Warrenville, Illinois?",
     "Sound & Fury Print Shop is a Warrenville-based custom apparel shop offering screen printing and DTF transfers for teams, schools, businesses, fundraisers, and events. You can request a quote at soundandfuryprint.com."),
    ("What is the difference between screen printing and DTF?",
     "Screen printing presses ink through a stencil and is ideal for larger runs of one design, giving a durable, classic finish. DTF (direct-to-film) heat-presses a full-color print onto fabric and works well for detailed art and smaller quantities. Sound & Fury can help you pick the right one for your project."),
    ("Can you print shirts for a Warrenville team, school, or club?",
     "Yes. Local teams, schools, and clubs are exactly who Sound & Fury prints for, from jerseys and spirit wear to coaches' and parents' shirts. Send your design, sizes, and quantities for a quote."),
    ("Do you do small orders or fundraiser shirts?",
     "Sound & Fury works with local groups on fundraiser and small-batch runs. Share what you have in mind and they will recommend the best print method and pricing for your order size."),
]

# ---------- FAQ (GEO: answers natural-language local queries) ----------
FAQ = [
    ("What is Warrenville Proud?",
     "Warrenville Proud is a free, community-run online guide to events and local life in Warrenville, Illinois. It publishes an updated events calendar and a twice-weekly blog covering things to do around town."),
    ("Where can I find events happening in Warrenville, Illinois?",
     "You can find a regularly updated list of Warrenville events on the Warrenville Proud events calendar at warrenvilleproud.com/events.html, gathered from the City of Warrenville, the Warrenville Park District, the Warrenville Public Library, and the Western DuPage Chamber of Commerce."),
    ("When is Summer Daze in Warrenville?",
     "Summer Daze is Warrenville's signature summer festival, held on the first weekend of August at the Warrenville City Hall complex, with live music, food, a car show, and local business booths. Check the events calendar for the exact dates this year."),
    ("What are some free things to do in Warrenville?",
     "Free options include Movies in the Park and Lunchtime Live from the Park District, walking or biking the Illinois Prairie Path, the Fourth of July parade, and admission to Summer Daze. The events calendar lists current free happenings."),
    ("How often is the Warrenville events calendar updated?",
     "The calendar is refreshed every week, and new blog posts are published twice a week, so the information stays current through the season."),
    ("Who runs and sponsors Warrenville Proud?",
     "Warrenville Proud is independently run as a community resource. Its founding sponsor is Sound & Fury Print Shop, a Warrenville-based screen printing and custom apparel business. Other local businesses can sponsor the site through a rotating Local Business Spotlight.")
]

def faq_jsonld():
    return {
        "@context": "https://schema.org", "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in FAQ
        ]
    }

def faq_html():
    items = "".join(
        f'<div class="card"><h3>{A(q)}</h3><p>{A(a)}</p></div>' for q, a in FAQ
    )
    return f'<div class="grid cols-2">{items}</div>'

# ---------- output ----------
def write(path, content):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    content = content.replace(chr(0x2014), ".").replace(chr(0x2013), "-")
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)
    print("wrote", path)

def rotate_spotlight():
    path = os.path.join(DATA, "sponsors.json")
    sp = load("sponsors.json")
    sp["spotlight_index"] = (sp.get("spotlight_index", 0) + 1) % len(sp["spotlight_rotation"])
    with open(path, "w", encoding="utf-8") as f:
        json.dump(sp, f, indent=2, ensure_ascii=False)
    print("rotated spotlight to index", sp["spotlight_index"])

def write_seo(posts, updated):
    pages = [("index.html", updated, "1.0"), ("events.html", updated, "0.9"),
             ("things-to-do-in-warrenville.html", updated, "0.8"),
             ("custom-shirts-warrenville.html", updated, "0.7"),
             ("about.html", updated, "0.6"), ("blog/index.html", updated, "0.7")]
    pages += [(f"blog/{p['slug']}.html", p["date"], "0.6") for p in posts]
    rows = "".join(
        f"  <url><loc>{SITE_URL}/{pg}</loc><lastmod>{lm}</lastmod><priority>{pr}</priority></url>\n"
        for pg, lm, pr in pages)
    write("sitemap.xml",
          '<?xml version="1.0" encoding="UTF-8"?>\n'
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
          f"{rows}</urlset>\n")
    # robots.txt: welcome search engines AND AI answer engines (GEO)
    bots = ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-User",
            "anthropic-ai", "PerplexityBot", "Perplexity-User", "Google-Extended",
            "Applebot-Extended", "CCBot", "Amazonbot", "Bingbot", "Googlebot"]
    allow = "".join(f"User-agent: {b}\nAllow: /\n\n" for b in bots)
    write("robots.txt", f"User-agent: *\nAllow: /\n\n{allow}Sitemap: {SITE_URL}/sitemap.xml\n")

def write_llms(upcoming, posts, sp):
    """llms.txt: a clean summary for AI answer engines (GEO)."""
    f = sp["founding"]
    ev = "\n".join(
        f"- {short_date(e['date'])}: {e['title']} ({e.get('location','Warrenville, IL')}). Source: {e.get('url','')}"
        for e in upcoming[:12])
    pl = "\n".join(f"- {p['title']}: {SITE_URL}/blog/{p['slug']}.html" for p in posts[:8])
    txt = f"""# Warrenville Proud

> A free, community-run guide to events and local life in Warrenville, Illinois (DuPage County, ZIP {ZIP}).

Warrenville Proud publishes a weekly-updated events calendar and a twice-weekly blog about things to do in Warrenville, IL. Content is gathered from public sources (City of Warrenville, Warrenville Park District, Warrenville Public Library, Western DuPage Chamber of Commerce) and always links back to the official source.

Site: {SITE_URL}/
Events calendar: {SITE_URL}/events.html
Blog: {SITE_URL}/blog/index.html
About: {SITE_URL}/about.html

## Founding sponsor
{f['name']} ({f['url']}): {f['blurb']}

## Upcoming Warrenville events
{ev}

## Recent posts
{pl}

## Usage
This content may be cited and summarized with attribution to Warrenville Proud ({SITE_URL}). Please link back to the relevant page. Event dates and times can change; link readers to the official source listed for each event.
"""
    write("llms.txt", txt)

def write_rss(posts):
    """RSS 2.0 feed for the blog (distribution + aggregator/AI pickup)."""
    items = []
    for p in posts[:20]:
        link = f"{SITE_URL}/blog/{p['slug']}.html"
        pub = parse(p["date"]).strftime("%a, %d %b %Y 08:00:00 +0000")
        items.append(
            "<item>"
            f"<title>{A(p['title'])}</title>"
            f"<link>{link}</link>"
            f'<guid isPermaLink="true">{link}</guid>'
            f"<pubDate>{pub}</pubDate>"
            f"<description>{A(p['excerpt'])}</description>"
            "</item>")
    rss = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">\n<channel>\n'
           f"<title>{SITE_NAME} Blog</title>\n"
           f"<link>{SITE_URL}/blog/index.html</link>\n"
           f'<atom:link href="{SITE_URL}/feed.xml" rel="self" type="application/rss+xml"/>\n'
           "<description>Local guides, weekly event roundups, and stories from Warrenville, Illinois.</description>\n"
           "<language>en-us</language>\n"
           + "\n".join(items) + "\n</channel>\n</rss>\n")
    write("feed.xml", rss)

def build():
    if "--rotate" in sys.argv:
        rotate_spotlight()
    events_data = load("events.json")
    posts_data = load("posts.json")
    sp = load("sponsors.json")
    today = ref_date()
    updated = events_data.get("updated", today.isoformat())

    upcoming = sorted(
        [e for e in events_data["events"] if parse(e.get("enddate", e["date"])) >= today],
        key=lambda e: e["date"])
    posts = sorted(posts_data["posts"], key=lambda p: p["date"], reverse=True)

    # ---------- index.html ----------
    home_events = "".join(event_card(e) for e in upcoming[:6]) or "<p class='lead'>No upcoming events listed right now. Check back soon.</p>"
    home_posts = "".join(post_card(p, "") for p in posts[:3])
    extra = [events_itemlist(upcoming[:8])] if upcoming else []
    h = page_open("", "home", sp=sp, path="",
                  title=f"{SITE_NAME}: Warrenville, IL Events Calendar & Community Guide",
                  desc="Your free local guide to events, news, and things to do in Warrenville, Illinois. Updated weekly. Proudly community-run.",
                  extra_ld=extra)
    body = f"""
<section class="hero"><div class="wrap">
  <h1>Everything happening in Warrenville, in one place.</h1>
  <p>A free, community-run guide to the events, people, and good things that make Warrenville, Illinois worth showing up for. Updated every week.</p>
  <a class="cta" href="events.html">See upcoming events</a>
</div></section>

<section><div class="wrap">
  <div class="sec-head"><h2>Coming up in Warrenville</h2><a href="events.html">Full calendar &rarr;</a></div>
  <div class="events-list">{home_events}</div>
</div></section>

<section style="padding-top:0"><div class="wrap">
  {spotlight_block(sp)}
</div></section>

<section><div class="wrap">
  <div class="sec-head"><h2>From the blog</h2><a href="blog/index.html">All posts &rarr;</a></div>
  <div class="grid cols-3">{home_posts}</div>
</div></section>

<section style="padding-top:0"><div class="wrap">
  {apparel_cta(sp, "home")}
</div></section>

<section style="padding-top:0"><div class="wrap">
  {sponsor_cta()}
</div></section>
"""
    write("index.html", h + body + footer("", sp))

    # ---------- events.html ----------
    all_ev = "".join(event_card(e) for e in upcoming) or "<p class='lead'>No upcoming events listed right now.</p>"
    extra = [events_itemlist(upcoming), breadcrumb([("Home", ""), ("Events", "events.html")])] if upcoming else [breadcrumb([("Home", ""), ("Events", "events.html")])]
    h = page_open("", "events", sp=sp, path="events.html",
                  title="Warrenville, IL Events Calendar (Updated Weekly)",
                  desc="Upcoming events in Warrenville, Illinois: festivals, live music, family activities, and community happenings. Updated weekly with links to official sources.",
                  extra_ld=extra)
    body = f"""
<section><div class="wrap">
  <div class="sec-head"><h2>Warrenville Event Calendar</h2></div>
  <p class="lead">Updated {short_date(updated)}. Gathered from public Warrenville listings, always linked to the official source. Please confirm times before you go.</p>
  <div class="events-list">{all_ev}</div>
  <div style="margin-top:24px">{spotlight_block(sp)}</div>
  <div style="margin-top:24px">{apparel_cta(sp, "events")}</div>
</div></section>
"""
    write("events.html", h + body + footer("", sp))

    # ---------- about.html ----------
    extra = [faq_jsonld(),
             {"@context": "https://schema.org", "@type": "AboutPage", "url": canon("about.html"),
              "name": f"About {SITE_NAME}", "isPartOf": {"@id": SITE_URL + "/#website"}},
             breadcrumb([("Home", ""), ("About", "about.html")])]
    h = page_open("", "about", sp=sp, path="about.html",
                  title=f"About {SITE_NAME}: Warrenville, IL Community Guide",
                  desc="What Warrenville Proud is, who it serves, and how the free Warrenville, Illinois events calendar and blog work. Frequently asked questions answered.",
                  extra_ld=extra)
    f = sp["founding"]
    body = f"""
<section><div class="wrap"><div class="article">
  <span class="kicker">About</span>
  <h1>About Warrenville Proud</h1>
  <p><strong>Warrenville Proud</strong> is a free, community-run guide to events and local life in <strong>Warrenville, Illinois</strong> (DuPage County, ZIP {ZIP}). We keep a weekly-updated calendar of things to do around town and publish a short blog twice a week, so neighbors always have an easy place to see what is going on.</p>
  <p>Our goal is simple: help Warrenville stay informed, connected, and growing. We gather event details from public sources, the City of Warrenville, the Warrenville Park District, the Warrenville Public Library, and the Western DuPage Chamber of Commerce, and we always link back to the official source so you can confirm the details.</p>
  <h2>How it stays free</h2>
  <p>This site is supported by local sponsors. Our founding sponsor is <a href="{A(f['url'])}">{A(f['name'])}</a>, {A(f['short'])}. A rotating Local Business Spotlight gives other Warrenville businesses a way to support the site and reach local readers. Sponsorship keeps the information free for everyone.</p>
  <h2>Frequently asked questions</h2>
</div></div></section>
<section style="padding-top:0"><div class="wrap">{faq_html()}</div></section>
<section style="padding-top:0"><div class="wrap">{sponsor_cta()}</div></section>
"""
    write("about.html", h + body + footer("", sp))

    # ---------- blog/index.html ----------
    cards = "".join(post_card(p, "../") for p in posts)
    extra = [{"@context": "https://schema.org", "@type": "Blog", "url": canon("blog/index.html"),
              "name": f"{SITE_NAME} Blog", "publisher": {"@id": SITE_URL + "/#org"}},
             breadcrumb([("Home", ""), ("Blog", "blog/index.html")])]
    h = page_open("../", "blog", sp=sp, path="blog/index.html",
                  title=f"Warrenville Blog: Local Guides & Event Roundups | {SITE_NAME}",
                  desc="Local guides, weekly event roundups, and stories from around Warrenville, Illinois.",
                  extra_ld=extra)
    body = f"""
<section><div class="wrap">
  <div class="sec-head"><h2>The Warrenville Proud Blog</h2></div>
  <p class="lead">Weekly event roundups, local guides, and the stories behind our town.</p>
  <div class="grid cols-2">{cards}</div>
  <div style="margin-top:24px">{sponsor_cta()}</div>
</div></section>
"""
    write("blog/index.html", h + body + footer("../", sp))

    # ---------- individual posts ----------
    founding = sp["founding"]
    for p in posts:
        sponsor_name = p.get("sponsor", founding["name"])
        note = (f'<div class="sponsor-note"><b>Brought to you by {A(sponsor_name)}.</b> '
                f'{A(founding["blurb"])} <a href="{A(utm(founding["url"], "blog_note"))}">{A(founding["cta"])} &rarr;</a></div>')
        post_ld = {
            "@context": "https://schema.org", "@type": "BlogPosting",
            "headline": p["title"], "datePublished": p["date"], "dateModified": p["date"],
            "author": {"@type": "Organization", "name": p.get("author", SITE_NAME)},
            "publisher": {"@type": "Organization", "name": SITE_NAME,
                          "logo": {"@type": "ImageObject", "url": OG_IMAGE}},
            "mainEntityOfPage": canon(f"blog/{p['slug']}.html"),
            "image": OG_IMAGE, "description": p["excerpt"], "isAccessibleForFree": True,
            "about": {"@type": "City", "name": "Warrenville, Illinois"},
            "sponsor": {"@type": "Organization", "name": "Sound & Fury Print Shop",
                        "url": "https://soundandfuryprint.com"}
        }
        extra = [post_ld, breadcrumb([("Home", ""), ("Blog", "blog/index.html"), (p["title"], f"blog/{p['slug']}.html")])]
        h = page_open("../", "blog", sp=sp, path=f"blog/{p['slug']}.html", og_type="article",
                      title=f"{p['title']} | {SITE_NAME}", desc=p["excerpt"], extra_ld=extra)
        body = f"""
<section><div class="wrap"><article class="article">
  <span class="kicker">{A(p.get('kicker','Post'))}</span>
  <h1>{A(p['title'])}</h1>
  <div class="byline">By {A(p.get('author', SITE_NAME))} . {nice_date(p['date'])}</div>
  {p['body_html']}
  {note}
  <p style="margin-top:26px"><a href="index.html">&larr; Back to the blog</a></p>
</article></div></section>
"""
        write(f"blog/{p['slug']}.html", h + body + footer("../", sp))

    # ---------- custom-shirts-warrenville.html (funnel bridge page) ----------
    f = sp["founding"]
    apparel_faq_ld = {"@context": "https://schema.org", "@type": "FAQPage",
                      "mainEntity": [{"@type": "Question", "name": q,
                                      "acceptedAnswer": {"@type": "Answer", "text": a}}
                                     for q, a in APPAREL_FAQ]}
    extra = [local_business_node(), apparel_faq_ld,
             breadcrumb([("Home", ""), ("Custom Shirts in Warrenville", "custom-shirts-warrenville.html")])]
    h = page_open("", "guide", sp=sp, path="custom-shirts-warrenville.html",
                  title=f"Custom Shirts & Screen Printing in Warrenville, IL | {SF_NAME}",
                  desc="Need custom shirts in Warrenville? Local screen printing and DTF for teams, schools, businesses, fundraisers, and events from Sound & Fury Print Shop. Get a quote.",
                  extra_ld=extra)
    afaq = "".join(f'<div class="card"><h3>{A(q)}</h3><p>{A(a)}</p></div>' for q, a in APPAREL_FAQ)
    body = f"""
<section><div class="wrap"><div class="article">
  <span class="kicker">Local Custom Apparel</span>
  <h1>Custom Shirts &amp; Screen Printing in Warrenville</h1>
  <p>Putting together shirts for a team, a school group, a business, a fundraiser, or a big event? You do not have to order from a faceless website or drive out of town. <a href="{A(utm(f['url'], 'bridge_intro'))}">{A(f['name'])}</a> is a Warrenville-owned print shop that does <strong>screen printing</strong> and <strong>DTF transfers</strong> for exactly these kinds of local projects.</p>
  <p>{A(f['blurb'])}</p>
  <h2>Who it is for</h2>
  <p>Youth and rec sports teams, schools and PTOs, clubs and scout troops, local businesses and their staff, churches, fundraisers, reunions, and community events. If a group in Warrenville needs matching shirts, this is the local option.</p>
  <h2>Screen printing or DTF?</h2>
  <p>Screen printing is the classic, durable choice for larger runs of one design. DTF (direct-to-film) handles full-color and detailed art beautifully and is great for smaller quantities. Not sure which you need? That is what the shop is there to help with.</p>
  <h2>Why order local</h2>
  <p>You get a real person to talk to, the chance to sort out art and sizing without a help-desk ticket, faster local hand-off, and money that stays in Warrenville. Supporting a local shop is also part of what keeps community resources like <a href="index.html">Warrenville Proud</a> free.</p>
  <h2>Frequently asked questions</h2>
</div></div></section>
<section style="padding-top:0"><div class="wrap"><div class="grid cols-2">{afaq}</div></div></section>
<section style="padding-top:0"><div class="wrap">{apparel_cta(sp, "bridge_footer")}</div></section>
"""
    write("custom-shirts-warrenville.html", h + body + footer("", sp))

    # ---------- things-to-do-in-warrenville.html (evergreen pillar / hub) ----------
    things_faq = [
        ("What is there to do in Warrenville, Illinois?",
         "Warrenville offers trails and forest preserves along the West Branch DuPage River (including the Illinois Prairie Path and St. James Farm), Park District programs and movie nights, signature events like Summer Daze and the Fourth of July celebration, local dining, and a community arts scene. The Warrenville Proud events calendar lists what is coming up."),
        ("What is Warrenville known for?",
         "Warrenville is a DuPage County, Illinois town about 30 miles west of Chicago, known for its parks, trails, and forest preserves, its small-town community events, and its local arts roots."),
        ("What are the big annual events in Warrenville?",
         "Warrenville's signature annual events include Summer Daze in early August, the Fourth of July parade and celebration, Art on the Prairie in September, and Holly Days in December. Check the events calendar for current dates."),
        ("What is there to do outdoors in Warrenville?",
         "Warrenville sits on the Illinois Prairie Path and is surrounded by forest preserves including Warrenville Grove, St. James Farm, Blackwell, and McKee Marsh, with walking, biking, paddling, and nature trails throughout. Several connect to the wider DuPage County trail network."),
    ]
    things_faq_ld = {"@context": "https://schema.org", "@type": "FAQPage",
                     "mainEntity": [{"@type": "Question", "name": q,
                                     "acceptedAnswer": {"@type": "Answer", "text": a}}
                                    for q, a in things_faq]}
    extra = [things_faq_ld,
             breadcrumb([("Home", ""), ("Things to Do in Warrenville", "things-to-do-in-warrenville.html")])]
    h = page_open("", "guide", sp=sp, path="things-to-do-in-warrenville.html",
                  title="Things to Do in Warrenville, IL: Events, Parks, Trails & More",
                  desc="The local guide to things to do in Warrenville, Illinois: parks and trails, annual festivals, free family activities, arts, and dining. Updated by neighbors.",
                  extra_ld=extra)
    tfaq = "".join(f'<div class="card"><h3>{A(q)}</h3><p>{A(a)}</p></div>' for q, a in things_faq)
    body = f"""
<section class="hero"><div class="wrap">
  <h1>Things to Do in Warrenville, Illinois</h1>
  <p>A neighbor's guide to the parks, events, and good local stuff that make Warrenville worth showing up for. For exact dates, the <a href="events.html">events calendar</a> is updated every week.</p>
  <a class="cta" href="events.html">See upcoming events</a>
</div></section>

<section><div class="wrap"><div class="article">
  <h2>Outdoors, parks &amp; trails</h2>
  <p>Warrenville is one of the greener towns in DuPage County. The <strong>Illinois Prairie Path</strong> runs right through it, and the West Branch DuPage River threads a string of forest preserves you can walk, run, bike, or paddle. Favorites in and around town include <strong>Warrenville Grove</strong>, <strong>St. James Farm</strong>, <strong>Blackwell Forest Preserve</strong>, and <strong>McKee Marsh</strong>. For a relaxed two-mile loop with history and a little surprise artwork, see our <a href="blog/st-james-farm-warrenville-trail-guide.html">walker's guide to St. James Farm</a>. The <a href="https://www.warrenvilleparks.org/">Warrenville Park District</a> and the <a href="https://www.dupageforest.org/">Forest Preserve District of DuPage County</a> have current hours and maps.</p>

  <h2>Annual events &amp; festivals</h2>
  <p>The calendar is anchored by a handful of traditions the whole town turns out for: the <strong>Fourth of July</strong> parade and celebration, <strong>Summer Daze</strong> in early August (live music, food, a car show, and local booths), <strong>Art on the Prairie</strong> in September, and <strong>Holly Days</strong> to kick off the holidays in December. Dates shift year to year, so confirm on the <a href="events.html">events calendar</a> or the <a href="https://www.warrenville.il.us/395/Community-Events">City of Warrenville</a> page.</p>

  <h2>Free &amp; family-friendly</h2>
  <p>You do not have to spend a dime to have a good time here. The Park District runs free <strong>Movies in the Park</strong> and <strong>Lunchtime Live</strong> music through the summer, the Prairie Path is always open, and watching the Fourth of July parade is free. We rounded up more in <a href="blog/5-free-things-to-do-in-warrenville-this-summer.html">5 free things to do in Warrenville this summer</a>.</p>

  <h2>Arts &amp; culture</h2>
  <p>Warrenville has deep arts roots, celebrated each fall at Art on the Prairie and supported year-round by local makers and the <a href="https://www.warrenville.com/">Warrenville Public Library</a>. It is part of what gives the town its character.</p>

  <h2>Eat, shop &amp; support local</h2>
  <p>Small local businesses are the heart of Warrenville. When you are out and about, choose a local spot, and when your team, school, or business needs <a href="custom-shirts-warrenville.html">custom shirts</a>, you can get those made in town too. The <a href="http://westerndupagechamber.chambermaster.com/events/calendar">Western DuPage Chamber of Commerce</a> is a good way to find local members.</p>

  <h2>Frequently asked questions</h2>
</div></div></section>
<section style="padding-top:0"><div class="wrap"><div class="grid cols-2">{tfaq}</div></div></section>
<section style="padding-top:0"><div class="wrap">{apparel_cta(sp, "pillar")}</div></section>
"""
    write("things-to-do-in-warrenville.html", h + body + footer("", sp))

    write_seo(posts, updated)
    write_llms(upcoming, posts, sp)
    write_rss(posts)
    print(f"\nDone. {len(upcoming)} upcoming events, {len(posts)} posts.")

if __name__ == "__main__":
    build()
