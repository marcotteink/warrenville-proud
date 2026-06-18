# Warrenville Proud: Automation Runbook

This is the playbook the scheduled tasks follow to keep the site fresh. It is written so a Cowork/Claude session can run it start to finish with no extra context. Matt can also run any part of it by hand in Cowork.

**Repo:** `/Users/mattmarcotte/CLAUDE/warrenville-proud`
**Live site (once published):** https://warrenvilleproud.com
**Founding sponsor (always present):** Sound & Fury Print Shop, https://soundandfuryprint.com

There are two runs per week:

- **Monday run:** refresh the event calendar + publish the "Week Ahead" roundup post.
- **Thursday run:** publish one feature/local-guide post + rotate the Local Business Spotlight.

---

## Public sources to pull events from

Always gather from these, and always link each event back to its official source. Do not copy descriptions word for word. Write a short, friendly, original blurb. If a time or detail is unclear, leave it out and link to the source instead of guessing.

- City of Warrenville community events: https://www.warrenville.il.us/395/Community-Events and calendar https://www.warrenville.il.us/Calendar.aspx
- Warrenville Park District: https://www.warrenvilleparks.org/events/
- Warrenville Public Library: https://www.warrenville.com/events
- Western DuPage Chamber: http://westerndupagechamber.chambermaster.com/events/calendar
- Patch (cross-check only): https://patch.com/illinois/warrenville-il/calendar

Use `web_fetch` and/or `WebSearch` to read these. The city calendar already includes many Park District and Library events.

---

## MONDAY RUN: calendar refresh + Week Ahead post

1. Open the repo. Read `data/events.json`.
2. Fetch the public sources above. Build the current upcoming list:
   - Remove events whose date (or end date) is already in the past.
   - Add any new upcoming events you find. Each event needs: `date` (YYYY-MM-DD), optional `enddate`, `title`, `time`, `location`, `category`, `source`, `url`, and a 1 to 2 sentence original `blurb`.
   - Keep roughly the next 8 to 12 weeks of events.
   - Set `"updated"` to today's date.
3. Write the Week Ahead post. Add a new object to the top of the `posts` array in `data/posts.json`:
   - `slug`: `week-ahead-YYYY-MM-DD` (today's date)
   - `title`: `Your Week Ahead in Warrenville: [Mon D] - [Sun D]`
   - `date`: today
   - `kicker`: `Week Ahead`
   - `excerpt`: one inviting sentence
   - `sponsor`: `Sound & Fury Print Shop`
   - `body_html`: cover the events happening in the next 7 days in a warm, helpful tone, with `<h2>` per day or per event and links to sources. End by looking ahead to the next big thing. Genuinely useful first, promotional second.
4. Build: `python3 scripts/build_site.py`
5. Verify: no em dashes anywhere (`grep -rl $'—' .`), pages generated, links present.
6. Commit and push (see "Publishing" below).

## THURSDAY RUN: feature post + spotlight rotation

1. Open the repo. Read `data/events.json` and `data/posts.json` (and `pipeline/post-history.md` so you do not repeat a topic).
2. Write one feature/local-guide post. Append to `data/posts.json` with:
   - `slug`: a short kebab-case slug of the title
   - `kicker`: `Local Guide`, `Spotlight`, or `Warrenville Story`
   - `sponsor`: `Sound & Fury Print Shop`
   - `body_html`: a genuinely useful piece. Good evergreen angles: a guide to a park or trail, a season preview, a "best of" list, the story behind a local event, a how-to for residents (recycling, permits, school calendar), or a favorable feature on a local business. About every 4th feature can favorably highlight Sound & Fury directly (its work for local teams, schools, and events); the rest should spotlight the town so the site stays credible.
3. Rotate the spotlight and build: `python3 scripts/build_site.py --rotate`
   - This advances the Local Business Spotlight to the next sponsor. Sound & Fury stays the founding sponsor everywhere regardless.
4. Append a one-line entry to `pipeline/post-history.md` so future runs avoid repeats.
5. Verify (same as Monday step 5), then commit and push.

---

## Publishing (commit + deploy)

The site auto-deploys when changes are pushed to the connected GitHub repo (GitHub Pages). Each run ends with:

```bash
cd /Users/mattmarcotte/CLAUDE/warrenville-proud
git add -A
git commit -m "Weekly update: <date> (<what changed>)"
git push origin main   # only if a remote named origin exists
```

If `git push` reports no remote, the build and local commit still succeed; the site just is not connected yet. See `PUBLISH.md` for the one-time GitHub + domain setup. Do not treat a missing remote as a failure of the content work.

---

## Hard rules (every run)

- **No em dashes** anywhere. Use periods, commas, parentheses, or colons. The build script strips them as a backstop, but write clean.
- **Plain, warm, local voice.** Talk like a neighbor, not a press release.
- **Sound & Fury sponsorship is always present:** the ribbon, the footer, and a sponsor line on every post. Never ship a page without it.
- **Always link events to their official source.** Never copy text word for word.
- **Add a "confirm times before you go" spirit** to calendar content. Details change.
- **Useful to the town first.** The site earns trust by being genuinely helpful; the sponsorship works because of that trust.
