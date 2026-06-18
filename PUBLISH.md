# Launch Guide: warrenvilleproud.com

Plain-English, start to finish. You do not need to be a developer. Most of this is copy and paste. Do it once, and the site is live.

The site is a plain static website (HTML, CSS, and images), already built and SEO/GEO optimized. We will host it free on **GitHub Pages** and point your **GoDaddy** domain at it.

Folder on your Mac: `/Users/mattmarcotte/CLAUDE/warrenville-proud`

---

## Step 0: start the repo clean (1 minute)

This folder was first set up inside Cowork's sandbox, which left a broken hidden `.git` folder that the sandbox cannot remove. Delete it on your Mac so we start fresh:

- In Terminal: `cd "/Users/mattmarcotte/CLAUDE/warrenville-proud" && rm -rf .git`
- Or in Finder: press `Cmd+Shift+.` to show hidden files, drag the `.git` folder to the Trash.

Your actual site files are not touched by this.

---

## Step 1: push the code (repo already created)

Your empty repo is already created at **https://github.com/marcotteink/warrenville-proud** (same account as marcotte.ink). Just push to it from your Mac Terminal, exactly like marcotte.ink:

```bash
cd "/Users/mattmarcotte/CLAUDE/warrenville-proud"
rm -rf .git                 # clear the broken sandbox repo
git init
git add -A
git commit -m "Launch Warrenville Proud"
git branch -M main
git remote add origin https://github.com/marcotteink/warrenville-proud.git
git push -u origin main
```

After it pushes, tell Cowork and it will turn on GitHub Pages and connect the domain for you.

---

## Step 1 (alternate): get the code onto GitHub

Pick the path that sounds easiest. Both end with your code in a GitHub repo named `warrenville-proud`.

### Path A: GitHub Desktop (recommended, no terminal)

1. Install **GitHub Desktop** (desktop.github.com) and sign in with your GitHub account.
2. File, then "Add Local Repository," and choose the `warrenville-proud` folder. It will say it is not a git repository and offer to **create one**. Click "create a repository," then **Publish repository**.
3. Uncheck "Keep this code private" if you want it public (Pages works either way; public is simplest). Publish.
4. From now on, whenever the weekly content updates, open GitHub Desktop and click **Push origin** to put it live. One click.

### Path B: terminal (git)

```bash
cd "/Users/mattmarcotte/CLAUDE/warrenville-proud"
git init
git add -A
git commit -m "Launch Warrenville Proud"
git branch -M main
# create an empty repo named warrenville-proud on github.com first, then:
git remote add origin https://github.com/<your-github-username>/warrenville-proud.git
git push -u origin main
```

(If you have the GitHub CLI: `gh repo create warrenville-proud --public --source=. --push` does the create and push in one line.)

---

## Step 2: turn on GitHub Pages

In your repo on github.com: **Settings, then Pages**.

- Source: "Deploy from a branch."
- Branch: `main`, folder: `/ (root)`. Save.
- Under "Custom domain," enter `warrenvilleproud.com` and Save. (The repo already includes a `CNAME` file with this, so it may auto-fill.)
- Leave "Enforce HTTPS" checked once it becomes available (a few minutes after DNS is set).

You will get a temporary address like `https://<username>.github.io/warrenville-proud/` that works right away.

---

## Step 3: point the domain in GoDaddy (you do this part)

In GoDaddy: **My Products, find warrenvilleproud.com, DNS, Manage DNS**.

**Add these four A records** (Type A, Name `@`, each pointing to one IP, TTL default). If GoDaddy already has a parked `@` A record, edit/replace it.

| Type | Name | Value |
|------|------|-------|
| A | @ | 185.199.108.153 |
| A | @ | 185.199.109.153 |
| A | @ | 185.199.110.153 |
| A | @ | 185.199.111.153 |

**Add one CNAME for www:**

| Type | Name | Value |
|------|------|-------|
| CNAME | www | `<your-github-username>.github.io` |

That is it. DNS can take a few minutes to a few hours. Then `warrenvilleproud.com` shows your site.

(Optional, IPv6: you can also add four AAAA records on `@`: `2606:50c0:8000::153`, `2606:50c0:8001::153`, `2606:50c0:8002::153`, `2606:50c0:8003::153`.)

---

## Step 4: redirect your other Warrenville domains

So every name you own feeds the one real site (better for search). In GoDaddy, for each domain below: **DNS, then Forwarding**, forward to `https://warrenvilleproud.com`, type **Permanent (301)**, forwarding only (masking OFF).

- mywarrenville.com
- visitwarrenville.com
- warrenville-arts.com
- mycity.ink

Keep **warrenvilletees.com** aside for the future town-merch store.

---

## Step 5: tell search engines and AI engines about it (10 minutes, big payoff)

The site is already optimized (structured data, sitemap, AI-crawler access, an llms.txt summary). Two quick submissions help it get found faster:

1. **Google Search Console** (search.google.com/search-console): add `warrenvilleproud.com`, verify (the easiest is a DNS TXT record GoDaddy will let you paste), then under Sitemaps submit `sitemap.xml`.
2. **Bing Webmaster Tools** (bing.com/webmasters): add the site (you can import from Google), submit `sitemap.xml`. Bing also feeds ChatGPT search.

Then get one or two local backlinks (ask the Western DuPage Chamber and the library to link to it, post it in local Facebook groups). Local backlinks are the single biggest local-SEO booster.

---

## How updates publish after launch

The two scheduled tasks (Monday and Thursday) regenerate the calendar and blog in your folder automatically. To put each update live:

- **Path A (GitHub Desktop):** click **Push origin**. GitHub Pages redeploys in about a minute.
- **Path B (git):** the weekly task runs `git push` for you if the remote is connected, so it can be fully hands-off.

Want true zero-click autopilot (the site updates and deploys itself with no involvement)? That is a worthwhile phase-2 upgrade using GitHub Actions plus an Anthropic API key stored in GitHub's encrypted secrets. Ask Cowork to "set up the Warrenville Proud autopilot workflow" when you are ready.

---

## What is in this repo

Generated pages (`index.html`, `events.html`, `about.html`, `blog/`), the generator (`scripts/build_site.py`), brand images (`scripts/make_assets.py`), content data (`data/*.json`), SEO/GEO files (`sitemap.xml`, `robots.txt`, `llms.txt`, `CNAME`, `404.html`), and the automation runbook (`WEEKLY_TASK.md`). To change anything by hand, edit the files in `data/` and run `python3 scripts/build_site.py`, or just ask Cowork.
