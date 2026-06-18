# START HERE (for Claude Code)

This folder is the complete **Warrenville Proud** website (`warrenvilleproud.com`): a free Warrenville, Illinois community events hub with an auto-updating calendar and blog, sponsored by Sound & Fury Print Shop. It is built and SEO/GEO optimized. It just needs to be pushed live and have its domain connected.

**If you are Claude Code: your job is to help Matt finish launching this and keep it running.** Matt is new to this, so explain plainly and do the parts you can. Run shell commands from this folder. Read `PUBLISH.md` (full launch guide), `WEEKLY_TASK.md` (content automation), and `CLAUDE.md` (project rules) for detail.

Folder path: `/Users/mattmarcotte/CLAUDE/warrenville-proud`

---

## Current status (2026-06-17)

- Site is fully built (`index.html`, `events.html`, `about.html`, `blog/`, assets, SEO/GEO files). Regenerate anytime with `python3 scripts/build_site.py`.
- GitHub repo is created and EMPTY: `https://github.com/marcotteink/warrenville-proud` (account `marcotteink`, same as marcotte.ink).
- NOT yet pushed. Pages NOT enabled. DNS NOT set.
- A broken `.git` folder from the Cowork sandbox is present and must be removed before pushing (it has stale locks; on Matt's Mac `rm -rf .git` works fine).
- Two Cowork scheduled tasks already update the content weekly (`warrenville-proud-monday`, `warrenville-proud-thursday`).

---

## The launch, step by step

### Step 1: push the code (you can do this; uses Matt's local git auth)

```bash
cd "/Users/mattmarcotte/CLAUDE/warrenville-proud"
rm -rf .git
git init
git add -A
git commit -m "Launch Warrenville Proud"
git branch -M main
git remote add origin https://github.com/marcotteink/warrenville-proud.git
git push -u origin main
```

If the push asks for credentials, Matt signs in (do not enter his password yourself). Verify it worked:

```bash
git ls-remote https://github.com/marcotteink/warrenville-proud.git   # should now list refs/heads/main
```

### Step 2: turn on GitHub Pages

If the GitHub CLI is installed and authenticated (`gh auth status`), you can do it directly:

```bash
gh api --method POST /repos/marcotteink/warrenville-proud/pages \
  -f "source[branch]=main" -f "source[path]=/"
gh api --method PUT /repos/marcotteink/warrenville-proud/pages \
  -f cname=warrenvilleproud.com -F https_enforced=true
```

If `gh` is not set up, guide Matt through the web UI instead: repo **Settings, then Pages**, Source = "Deploy from a branch", Branch = `main`, folder = `/ (root)`, Save. Under Custom domain enter `warrenvilleproud.com` (the repo already contains the matching `CNAME` file). Turn on Enforce HTTPS once available.

### Step 3: connect the domain in GoDaddy (Matt does this in GoDaddy; give him these exact values)

In GoDaddy for `warrenvilleproud.com`, Manage DNS. Remove the parked record on `@`, then add:

| Type | Name | Value |
|------|------|-------|
| A | @ | 185.199.108.153 |
| A | @ | 185.199.109.153 |
| A | @ | 185.199.110.153 |
| A | @ | 185.199.111.153 |
| CNAME | www | marcotteink.github.io |

DNS can take minutes to a few hours.

### Step 4: redirect the other Warrenville domains (GoDaddy, optional but recommended)

301-forward each of these to `https://warrenvilleproud.com` (GoDaddy Forwarding, permanent, masking OFF): `mywarrenville.com`, `visitwarrenville.com`, `warrenville-arts.com`, `mycity.ink`. Keep `warrenvilletees.com` for a future merch store.

### Step 5: verify it is live

```bash
curl -sI https://warrenvilleproud.com | head -1        # expect HTTP/2 200 once DNS + Pages are ready
curl -s https://warrenvilleproud.com/sitemap.xml | head -3
```

Until DNS resolves, the temporary address `https://marcotteink.github.io/warrenville-proud/` will work after Step 2.

### Step 6: help it get found (optional, high value)

Add the site to Google Search Console and Bing Webmaster Tools and submit `sitemap.xml`. IndexNow is already wired (key file `68c7972b0a66be6b99c4c407989d94cf.txt`); the weekly task pings it. See `PUBLISH.md` Step 5.

---

## Ongoing: how to update the site

Edit the data, never the generated HTML:

```bash
# edit data/events.json, data/posts.json, or data/sponsors.json
python3 scripts/build_site.py        # rebuild (add --rotate to advance the sponsor spotlight)
git add -A && git commit -m "Update" && git push
```

The weekly content automation is described in `WEEKLY_TASK.md`. The Cowork scheduled tasks run it; once the git remote is connected, updates can publish automatically.

---

## Rules for this project (please follow)

- No em dashes anywhere (use periods, commas, parentheses, colons). The build strips them as a backstop.
- Sound & Fury sponsorship stays on every page (ribbon, footer, per-post line). Never ship without it.
- Every event links to its official source; never copy descriptions word for word.
- Warm, local, neighborly voice. Useful to the town first, promotional second.

## File map

- `PUBLISH.md` full launch guide (plain English).
- `WEEKLY_TASK.md` content automation runbook + public event sources.
- `CLAUDE.md` project memory and writing rules.
- `scripts/build_site.py` site generator. `scripts/make_assets.py` brand images.
- `data/` content (events, posts, sponsors). `assets/` css + images.
- `_INDEX.md` full file index.
