# Publishing Warrenville Proud (plain-English guide)

You do not need to be a developer for this. It is a one-time setup. After it, the site updates itself.

## What this site is

A plain static website (just HTML and CSS files). Static sites are cheap and reliable: there is no server to maintain, and free hosting like GitHub Pages works great. The folder is already set up as a git repo, which is just a tracked history of the files.

## Option A: GitHub Pages (free, recommended)

This matches how your other sites (freegangsheetmaker.com, marcotte.ink) are hosted.

1. **Make a GitHub repo.** On github.com, create a new empty repository named `warrenville-proud`. Do not add a README (the folder already has files).
2. **Connect this folder to it.** In Cowork, ask: "Push the warrenville-proud folder to my new GitHub repo." It will run the git commands. Or by hand:
   ```bash
   cd /Users/mattmarcotte/CLAUDE/warrenville-proud
   git remote add origin https://github.com/<your-username>/warrenville-proud.git
   git branch -M main
   git push -u origin main
   ```
3. **Turn on Pages.** In the repo on GitHub: Settings, then Pages. Set Source to "Deploy from a branch," branch `main`, folder `/ (root)`. Save. In a minute you get a temporary address like `https://<username>.github.io/warrenville-proud/`.
4. **Point your domain.** Two steps:
   - In the repo's Settings, Pages, "Custom domain," enter `warrenvilleproud.com` and save.
   - In GoDaddy (where the domain lives), add the DNS records GitHub asks for: four `A` records pointing to GitHub's IPs (`185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`) and one `CNAME` for `www` pointing to `<username>.github.io`. GitHub's Pages docs show the exact values.
   - Back on GitHub, check "Enforce HTTPS" once it is available.
   DNS can take a few minutes to a few hours to take effect.

## Option B: any static host

The whole folder (minus `scripts/` and `data/`, though leaving them is harmless) can be dropped on Netlify, Cloudflare Pages, or DigitalOcean App Platform. Point the host at the repo and set the build output to the repo root. No build command is required to serve (the HTML is already generated); if the host supports a build step, you can run `python3 scripts/build_site.py`.

## Pointing the other 5 domains at this one

You own `mywarrenville.com`, `visitwarrenville.com`, `warrenville-arts.com`, and `mycity.ink`. Set each to **redirect** to `warrenvilleproud.com` (a "301 redirect" in GoDaddy's Forwarding settings). That way every name you own feeds the one real site, which is better for search ranking. Keep `warrenvilletees.com` aside for a future town-merch store that links from here.

## After setup: how updates happen

- The two scheduled tasks (Monday and Thursday) refresh events and publish posts automatically, then push to GitHub, and Pages redeploys within a minute.
- To change anything by hand, edit the files in `data/` and run `python3 scripts/build_site.py`, or just ask Cowork.

## Local preview (optional)

Open `index.html` in a browser to see the site. Links and styles work locally. The only thing that needs the live host is the automatic deploy.
