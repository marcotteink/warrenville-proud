#!/usr/bin/env python3
"""
Warrenville Proud - static site generator.

Reads data/events.json, data/posts.json, data/sponsors.json and writes:
  index.html, events.html, blog/index.html, blog/<slug>.html

No third-party dependencies. Run from the repo root:
    python3 scripts/build_site.py
Optional: set REF_DATE=YYYY-MM-DD to control which events count as "upcoming"
(defaults to today). Used so previews look right regardless of machine clock.
"""
import json, os
from datetime import date, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
SITE_NAME = "Warrenville Proud"
SITE_TAG = "Good things happening in our town"
SITE_URL = "https://warrenvilleproud.com"

def load(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as f:
        return json.load(f)

def ref_date():
    v = os.environ.get("REF_DATE")
    return datetime.strptime(v, "%Y-%m-%d").date() if v else date.today()

def parse(d):
    return datetime.strptime(d, "%Y-%m-%d").date()

def nice_date(d):
    dt = parse(d)
    return dt.strftime("%A, %B %-d, %Y")

def short_date(d):
    dt = parse(d)
    return dt.strftime("%b %-d, %Y")

def ribbon(sp):
    f = sp["founding"]
    return (f'<div class="ribbon">Founding sponsor: '
            f'<a href="{f["url"]}">{f["name"]}</a> . {f["short"]}</div>')

def header(base, active, sp):
    def cls(name): return ' style="color:var(--prairie)"' if name == active else ''
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{title}}</title>
<meta name="description" content="{{desc}}">
<link rel="stylesheet" href="{base}assets/style.css">
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
    <a href="{base}blog/index.html"{cls('blog')}>Blog</a>
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
      <a href="{base}blog/index.html">Blog</a><br>
      <a href="{base}index.html#sponsor">Become a sponsor</a></p>
    </div>
    <div style="max-width:300px">
      <h4>Founding sponsor</h4>
      <p><a href="{f['url']}">{f['name']}</a><br>{f['short']}</p>
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

def event_card(e):
    dt = parse(e["date"])
    end = ""
    if e.get("enddate") and e["enddate"] != e["date"]:
        end = f' - {parse(e["enddate"]).strftime("%b %-d")}'
    det = " . ".join(x for x in [e.get("time", ""), e.get("location", "")] if x)
    src = e.get("source", "")
    url = e.get("url", "#")
    return f"""<div class="event">
  <div class="when"><div class="mo">{dt.strftime('%b').upper()}</div><div class="day">{dt.strftime('%-d')}</div><div class="dow">{dt.strftime('%a')}{end}</div></div>
  <div class="body">
    <span class="pill">{e.get('category','Event')}</span>
    <h3>{e['title']}</h3>
    <div class="det">{det}</div>
    <p>{e.get('blurb','')}</p>
    <a class="more" href="{url}">Details via {src} &rarr;</a>
  </div>
</div>"""

def post_card(p, base):
    return f"""<div class="card">
  <span class="meta">{p.get('kicker','Post')} . {short_date(p['date'])}</span>
  <h3><a href="{base}blog/{p['slug']}.html" style="color:inherit">{p['title']}</a></h3>
  <p>{p['excerpt']}</p>
  <a class="more" href="{base}blog/{p['slug']}.html">Read more &rarr;</a>
</div>"""

def spotlight_block(sp):
    rot = sp["spotlight_rotation"]
    idx = sp.get("spotlight_index", 0) % len(rot)
    s = rot[idx]
    founding_line = '<div class="founding">Founding sponsor of Warrenville Proud</div>' if s.get("founding") else ""
    btn = f'<a class="btn" href="{s["url"]}">Visit {s["name"]}</a>' if s["url"] != "#sponsor" else '<a class="btn" href="#sponsor">Become a sponsor</a>'
    return f"""<div class="spotlight">
  <div class="kicker">Local Business Spotlight</div>
  <h3>{s['name']}</h3>
  <p>{s['blurb']}</p>
  {btn}
  {founding_line}
</div>"""

def sponsor_cta():
    return """<div id="sponsor" class="sponsor-cta">
  <h3>Keep Warrenville Proud free. Sponsor it.</h3>
  <p>This site is read by neighbors looking for what to do and where to go in town. A sponsorship puts your business in front of them and helps keep local info free for everyone.</p>
  <a class="btn" href="mailto:hello@warrenvilleproud.com?subject=Sponsoring%20Warrenville%20Proud">Become a sponsor</a>
</div>"""

def write(path, html):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    # safety: the workspace bans em dashes (U+2014) and en dashes used as separators
    html = html.replace(chr(0x2014), ".").replace(chr(0x2013), "-")
    with open(full, "w", encoding="utf-8") as f:
        f.write(html)
    print("wrote", path)

def rotate_spotlight():
    """Advance the Local Business Spotlight to the next sponsor in the rotation."""
    path = os.path.join(DATA, "sponsors.json")
    sp = load("sponsors.json")
    n = len(sp["spotlight_rotation"])
    sp["spotlight_index"] = (sp.get("spotlight_index", 0) + 1) % n
    with open(path, "w", encoding="utf-8") as f:
        json.dump(sp, f, indent=2, ensure_ascii=False)
    print("rotated spotlight to index", sp["spotlight_index"])

def write_seo(posts):
    pages = ["index.html", "events.html", "blog/index.html"] + [f"blog/{p['slug']}.html" for p in posts]
    urls = "".join(f"  <url><loc>{SITE_URL}/{pg}</loc></url>\n" for pg in pages)
    sm = ('<?xml version="1.0" encoding="UTF-8"?>\n'
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
          f"{urls}</urlset>\n")
    write("sitemap.xml", sm)
    write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n")

def build():
    import sys
    if "--rotate" in sys.argv:
        rotate_spotlight()
    events_data = load("events.json")
    posts_data = load("posts.json")
    sp = load("sponsors.json")
    today = ref_date()

    upcoming = sorted(
        [e for e in events_data["events"] if parse(e.get("enddate", e["date"])) >= today],
        key=lambda e: e["date"]
    )
    posts = sorted(posts_data["posts"], key=lambda p: p["date"], reverse=True)

    # ---------- index.html ----------
    home_events = "".join(event_card(e) for e in upcoming[:6]) or "<p class='lead'>No upcoming events listed right now. Check back soon.</p>"
    home_posts = "".join(post_card(p, "") for p in posts[:3])
    h = header("", "home", sp).replace("{title}", f"{SITE_NAME} . Warrenville, IL events & community").replace("{desc}", "Your local guide to events, news, and good things happening in Warrenville, Illinois. Free, community-run, and proudly local.")
    body = f"""
<section class="hero"><div class="wrap">
  <h1>Everything happening in Warrenville, in one place.</h1>
  <p>A free, community-run guide to the events, people, and good things that make Warrenville, Illinois worth showing up for.</p>
  <a class="cta" href="events.html">See this week's events</a>
</div></section>

<section><div class="wrap">
  <div class="sec-head"><h2>Coming up around town</h2><a href="events.html">Full calendar &rarr;</a></div>
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
  {sponsor_cta()}
</div></section>
"""
    write("index.html", h + body + footer("", sp))

    # ---------- events.html ----------
    all_ev = "".join(event_card(e) for e in upcoming) or "<p class='lead'>No upcoming events listed right now.</p>"
    h = header("", "events", sp).replace("{title}", f"Warrenville Events Calendar . {SITE_NAME}").replace("{desc}", "Upcoming events in Warrenville, Illinois: festivals, music, family activities, and community happenings. Updated weekly.")
    body = f"""
<section><div class="wrap">
  <div class="sec-head"><h2>Warrenville Event Calendar</h2></div>
  <p class="lead">Updated {short_date(events_data.get('updated', today.isoformat()))}. Pulled from public listings, always linked to the official source. Confirm times before you go.</p>
  <div class="events-list">{all_ev}</div>
  <div style="margin-top:24px">{spotlight_block(sp)}</div>
</div></section>
"""
    write("events.html", h + body + footer("", sp))

    # ---------- blog/index.html ----------
    cards = "".join(post_card(p, "../") for p in posts)
    h = header("../", "blog", sp).replace("{title}", f"Blog . {SITE_NAME}").replace("{desc}", "Local guides, event roundups, and stories from around Warrenville, Illinois.")
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
        note = (f'<div class="sponsor-note"><b>Brought to you by {sponsor_name}.</b> '
                f'{founding["blurb"]} <a href="{founding["url"]}">{founding["cta"]} &rarr;</a></div>')
        h = header("../", "blog", sp).replace("{title}", f"{p['title']} . {SITE_NAME}").replace("{desc}", p["excerpt"])
        body = f"""
<section><div class="wrap"><article class="article">
  <span class="kicker">{p.get('kicker','Post')}</span>
  <h1>{p['title']}</h1>
  <div class="byline">By {p.get('author', SITE_NAME)} . {nice_date(p['date'])}</div>
  {p['body_html']}
  {note}
  <p style="margin-top:26px"><a href="index.html">&larr; Back to the blog</a></p>
</article></div></section>
"""
        write(f"blog/{p['slug']}.html", h + body + footer("../", sp))

    write_seo(posts)
    print(f"\nDone. {len(upcoming)} upcoming events, {len(posts)} posts.")

if __name__ == "__main__":
    build()
