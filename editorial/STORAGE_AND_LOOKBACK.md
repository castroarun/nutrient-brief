# Storage & Lookback — where Edition artifacts live

*Written: 2026-04-19*

Every edition produces three kinds of artifact. Each has a different ideal home. Slack is a bad fit for all of them (channels bury old content; no search over HTML; no URL-per-edition). Here's the recommended setup — all of it zero-touch after initial configuration.

---

## The three artifact types

| Artifact | Purpose | Where it should live |
|---|---|---|
| **Deep-Dive (Markdown)** | Your own study reference; also the Substack article body | Substack (public) + Obsidian vault (private) |
| **Share Card (HTML)** | Forwarded on WhatsApp, embedded in LinkedIn/Substack, viewable in browser | Your own static site (permanent URL per edition) |
| **IG Carousel (images)** | Posted on Instagram | Instagram (obviously) — plus backup copies in the static site's `/assets/` |

---

## Recommended stack — three layers

### 1. Substack — the public front door (already decided)

- Every edition's **Deep-Dive** publishes here as the email + article.
- Substack gives you: email delivery, public archive at `nutrientbrief.substack.com/archive`, search, comments, paid-tier option later, RSS.
- The Share Card HTML can be **embedded** inside the Substack article (Substack supports arbitrary HTML blocks), so readers see the visual first, then the prose.
- Archive is browsable — readers can scroll back through every edition.

### 2. Your own static site — the long-term reference library

Substack is good but it's rented land. You want a **permanent address** — `nutrientbrief.in/editions/001-magnesium` — that survives any platform change, and where each Share Card HTML is a standalone page (shareable in one tap).

**Stack: Astro or Hugo → deployed on Cloudflare Pages (or Netlify).**

Why this specifically:
- **Free.** Cloudflare Pages has a generous free tier; Netlify similar.
- **Zero-touch after setup.** Push Markdown + HTML to a GitHub repo → auto-deploys in ~30 seconds. Your pipeline already produces both files; adding a `git commit` step is trivial.
- **Clean URLs.** `/editions/001-magnesium`, `/editions/002-vitamin-d-k2`. Permanent, shareable, indexable by Google.
- **Both artifacts live there.** Deep-Dive rendered as prose page; Share Card embedded as-is (it's already a self-contained HTML).
- **Search + tags.** You can add a simple search box (Pagefind works with Astro/Hugo) to filter by nutrient class, evidence strength, etc.
- **Your brand.** Your domain name, your look, your archive. Substack is the acquisition funnel; the static site is the library.

**One-time setup cost:** ~90 minutes. After that, the pipeline writes files to the repo, git push deploys the site, done. Literally zero ongoing maintenance.

Rough structure:
```
nutrientbrief.in/
  /                           -> landing + latest 10 editions
  /editions/001-magnesium     -> deep-dive prose + embedded share card
  /editions/001-magnesium.png -> auto-rendered preview image (for sharing)
  /categories/micronutrients  -> filtered archive
  /about                      -> about the project
  /disclaimer                 -> standing legal/compliance page
```

### 3. Obsidian vault (on iCloud/Dropbox) — your private study archive

The Deep-Dive Markdown files are already structured for this. Point Obsidian at a folder, and you get:
- **Full-text search** across every edition you've written — answer "what did I say about magnesium?" in 2 seconds, even 2 years later.
- **Backlinks** — when Edition 087 references magnesium, Obsidian links back to Edition 001.
- **Tags** — `#micronutrient #sleep #indian-dietary-context` — filter your entire library by any combination.
- **Graph view** — visual map of how nutrients interconnect. Great for spotting content gaps.
- **Private by default** — this is *your* reference library, not a public one. Different use case from the static site.

Setup: Obsidian is free. Vault is a folder on your disk, synced via iCloud or Dropbox so it's on all devices. Zero-touch.

---

## What each layer does for which use case

| Use case | Substack | Static site | Obsidian |
|---|---|---|---|
| "Send today's edition to my cousin" | yes forward email | yes share URL | no |
| "Embed this in a LinkedIn post" | yes (Substack link) | yes (your domain - looks more owned) | no |
| "What did I write about vitamin D 6 months ago?" | slow search | slow search | instant |
| "All editions I've written tagged #sleep" | no | yes if you build it | yes already free |
| "A permanent archive even if Substack changes terms" | no rented | yes owned | yes local files |
| "Share on WhatsApp - the prettier version, not a wall of text" | shares link to article | yes shares URL of the Share Card page directly | no |
| "The pipeline writes here automatically" | yes via Substack API | yes via git push | yes it's just saving MD files |

---

## Why NOT Slack (or similar)

You asked about Slack — worth being direct about why it's the wrong fit:

- **No search over HTML.** Share Card HTML gets posted as an attachment; you can't grep the content.
- **No URL-per-edition.** Can't point someone to "Edition 14" — can only link to a message that'll eventually scroll off.
- **Buries fast.** A channel with 300 editions is essentially unsearchable.
- **Not public.** Defeats the purpose of a publication.
- **Not portable.** Can't export your archive cleanly.

Slack is great for *real-time communication*, bad for *long-term archival*. Same reason a library isn't a group chat.

---

## Recommended rollout

**Week 0 (now):** Keep writing to `drafts/` in this folder. That's fine short-term.

**Week 2:** Once 3-4 editions exist, set up Substack. Start publishing Deep-Dives there. This is the reader-facing launch.

**Week 3:** Register domain (`.in` domains with any Indian registrar, ~₹500/yr). Set up Astro project in a GitHub repo. Deploy to Cloudflare Pages. Pipeline starts writing to the repo as it publishes. ~1 evening of work.

**Week 4:** Install Obsidian. Point it at the `drafts/` folder (now also in the repo). Everything you've ever written becomes searchable/tag-filterable in your pocket.

**Ongoing:** Pipeline pushes both Markdown + HTML to the repo → site auto-rebuilds → email goes via Substack → Instagram carousel posted via Buffer (separately scheduled). All zero-touch.

---

## The one-line version

**Substack** is where readers find you.
**Your own static site** is where *anything* — deep-dive, share card, future podcast transcripts — lives permanently and shareably.
**Obsidian** is where *you* go to look back at your own thinking.

Three layers, zero daily maintenance once set up.
