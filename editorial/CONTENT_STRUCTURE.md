# Content Source & Output Structure

*How the raw research becomes published artifacts, what gets stored where, and what the final repo + site + archive look like. Read alongside `PIPELINE_SPEC.md`.*

*Last updated: 2026-04-19*

---

## The journey of one edition — end to end

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  RESEARCH    │ ──▶ │   DRAFT      │ ──▶ │   RENDER     │ ──▶ │   PUBLISH    │
│              │     │              │     │              │     │              │
│ topic pick   │     │ single MD    │     │ 3 artifacts  │     │ 4 surfaces   │
│ source pull  │     │ with         │     │ (MD, HTML,   │     │ (Substack,   │
│ doctor pick  │     │ frontmatter  │     │  8 slides)   │     │  site, IG,   │
│ anchor draft │     │ + prose body │     │              │     │  Obsidian)   │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
      ~4 min              ~1 min               ~2 min             ~1 min
```

Total wall-clock: ~8-10 minutes per edition. Entirely unattended.

---

## Layer 1 — the source repository (what the pipeline reads and writes)

A single git repo — `nutrient-brief` — hosted on GitHub (private during build, public-able later if useful).

```
nutrient-brief/
│
├── PIPELINE_SPEC.md           ← runtime contract (authoritative for auto-gen)
├── editorial_framework.md      ← content rules (source tiers, doctors, anchors)
├── compliance_notes.md         ← regulatory guardrails
├── CONTENT_STRUCTURE.md        ← this file
│
├── research/                   ← pipeline INPUTS
│   ├── topic_backlog.md        ← ordered list: topic, category, scheduled date
│   ├── doctor_registry.md      ← whitelist of citable clinicians
│   ├── anchor_library.md       ← used anchors (collision check) + drafts
│   ├── palette.md              ← 20-colour curated accent palette + topic→colour mapping
│   └── svg_library/            ← reusable memory-anchor SVG seeds
│
├── drafts/                     ← pipeline SCRATCH (one folder per in-progress edition)
│   ├── templates/              ← canonical templates
│   │   ├── deep-dive.md.tpl
│   │   ├── share-card.html.tpl
│   │   └── carousel/slide_NN.html.tpl  (one tpl per slide)
│   └── pending_review/         ← editions that failed a compliance check
│       └── NNN_<slug>/
│
├── content/                    ← pipeline OUTPUT (what gets deployed)
│   └── editions/
│       ├── 001_magnesium-glycinate/
│       │   ├── deep-dive.md
│       │   ├── share-card.html
│       │   ├── carousel/
│       │   │   ├── slide_01.html
│       │   │   ├── slide_02.html
│       │   │   ├── ...
│       │   │   ├── slide_08.html
│       │   │   └── preview.html
│       │   ├── assets/
│       │   │   ├── anchor.svg
│       │   │   ├── og-image.png          (1200×630, for link previews)
│       │   │   ├── slide_01.png          (1080×1350, for IG upload)
│       │   │   ├── ...
│       │   │   └── slide_08.png
│       │   └── manifest.json             (metadata: date, sources, doctor, accent colour)
│       │
│       ├── 002_vitamin-d3-k2/
│       │   └── (same structure)
│       │
│       └── ...
│
├── site/                       ← Astro (or Hugo) site source
│   ├── astro.config.mjs
│   ├── src/
│   │   ├── layouts/            ← page shell (masthead, nav, footer, RSS)
│   │   ├── pages/
│   │   │   ├── index.astro     ← homepage — latest editions grid
│   │   │   ├── archive.astro   ← full archive, filterable by category
│   │   │   ├── editions/
│   │   │   │   └── [slug].astro   ← renders content/editions/NNN_<slug>/
│   │   │   ├── about.astro
│   │   │   └── disclaimer.astro
│   │   └── components/
│   │       └── ShareEmbed.astro   ← embeds share-card.html as iframe or inline
│   └── public/
│       └── (static files — favicon, robots.txt)
│
├── pipeline/                   ← the automation code itself
│   ├── run.py                  ← entrypoint; orchestrates research → render → publish
│   ├── research.py             ← pulls PubMed abstracts, validates doctor
│   ├── render_md.py            ← deep-dive MD from template
│   ├── render_html.py          ← share-card HTML from template
│   ├── render_carousel.py      ← 8 slide HTMLs + PNG export via headless Chrome
│   ├── publish_substack.py     ← Substack API
│   ├── publish_ig.py           ← Buffer / Meta Business Suite API
│   └── checks.py               ← compliance + anchor-freshness + source resolution
│
├── run_log.md                  ← append-only record of every pipeline run
└── .github/workflows/
    └── deploy.yml              ← auto-deploy to Cloudflare Pages on push
```

**What lives where, in one line each:**
- `research/` = inputs humans (or the pipeline) prepare.
- `drafts/` = scratchpad + canonical templates.
- `content/` = the final published artifacts. One immutable folder per edition.
- `site/` = the static-site source (reads from `content/` to render pages).
- `pipeline/` = the code that makes it all happen.

---

## Layer 2 — the live site (what readers see)

**Domain:** `nutrientbrief.in` (or similar — register at Week 3).

**URL scheme:**

| URL | What it shows |
|---|---|
| `/` | Homepage — latest 6 editions grid + manifesto + email signup |
| `/editions/` | Full archive — filterable by category, searchable |
| `/editions/001-magnesium-glycinate/` | Edition page — deep-dive prose at top, share-card embedded below, forward/share buttons |
| `/editions/001-magnesium-glycinate/share` | Standalone share card (the HTML file, as-is) — this is the URL forwarded on WhatsApp |
| `/editions/001-magnesium-glycinate/carousel` | Standalone carousel preview (all 8 slides scrollable) |
| `/categories/minerals/` | Category archive |
| `/about/` | About the project |
| `/disclaimer/` | Standing legal / compliance page |
| `/rss.xml` | RSS feed (auto-generated from `content/editions/`) |

**Deployment:** each `git push` to main triggers Cloudflare Pages build. ~30-second deploy. Zero manual step.

**Reader paths:**
- Email subscriber → clicks Substack link → lands on Substack article (embedded share card).
- WhatsApp forward → opens `/editions/NNN-slug/share` directly → clean visual, no distractions, with a "read the full edition →" link.
- Instagram swipe → bio link goes to `/` → latest edition.
- Google search → lands on edition page → reads deep-dive → subscribes.

---

## Layer 3 — Obsidian vault (your private study archive)

Obsidian is pointed at `content/editions/` as its vault root.

What you get:
- Every `deep-dive.md` becomes a searchable note automatically (as they get written, they just appear).
- `[[magnesium]]` links created during drafting resolve as backlinks.
- Tags inside frontmatter (`#mineral #sleep #indian-dietary-context #t2d`) filter the whole library.
- Obsidian graph view shows how topics cluster.

Nothing extra to build — it's just a folder on disk synced via iCloud/Dropbox.

---

## What a single edition's `manifest.json` looks like

This is the one machine-readable file that travels with each edition. Downstream tools (RSS generator, site build, IG scheduler, compliance audit) all read it.

```json
{
  "edition_id": "001",
  "slug": "magnesium-glycinate",
  "title": "Magnesium Glycinate — your nervous system's volume knob",
  "category": "mineral",
  "day_of_week": "Tuesday",
  "eyebrow_label": "MINERAL OF THE WEEK",
  "accent_color": "#c7462d",
  "published_at": "2026-06-09T05:00:00+05:30",
  "memory_anchor": "Magnesium is your nervous system's volume knob — turn it too low, and everything feels louder than it is.",
  "doctor": {
    "name": "Dr. V. Mohan",
    "institution": "Madras Diabetes Research Foundation",
    "specialty_match": "diabetes & nutrition",
    "paraphrase_source": "MDRF published research",
    "verified": true
  },
  "sources": [
    { "id": 1, "citation": "Abbasi B et al., J Res Med Sci 2012", "pubmed_id": "23853635", "tier": 2 },
    { "id": 2, "citation": "de Baaij et al., Physiol Rev 2015", "pubmed_id": "25540137", "tier": 1 }
  ],
  "tags": ["mineral", "sleep", "anxiety", "t2d", "indian-dietary-context"],
  "compliance_checks": {
    "no_disease_claims": true,
    "no_product_brands": true,
    "no_personal_dosing": true,
    "doctor_verified": true,
    "sources_resolved": true,
    "anchor_unique": true,
    "disclaimer_present": true
  },
  "published_to": {
    "substack": "https://nutrientbrief.substack.com/p/001-magnesium-glycinate",
    "site": "https://nutrientbrief.in/editions/001-magnesium-glycinate",
    "instagram_post_id": "...",
    "instagram_scheduled_at": "2026-06-09T09:00:00+05:30"
  }
}
```

---

## What builds up over time

After 6 months (~150 editions), you own:

- **~150 deep-dive Markdown files** — each ~550 words, structured, sourced. Total ~85k words of nutrition reference prose, organized and searchable. This is a *book* by volume.
- **~150 share-card HTML pages** — one visual per nutrient, at permanent URLs, forwardable indefinitely.
- **~1,200 IG carousel slides** — massive library of visual assets you can re-cut for YouTube Shorts, reels, LinkedIn carousels.
- **~150 memory anchors** — your *signature IP*. These are original analogies, attributable to you. The most shareable unit.
- **A tagged, backlinked Obsidian vault** — you can query your own thinking: "every time I wrote about sleep" → 14 editions; "everything on insulin resistance" → 22 editions.
- **A search-indexed static site** — Google starts surfacing you on specific queries ("magnesium glycinate vs citrate absorption") and traffic compounds.

None of this is lost to a platform change — the content repo is the truth. Substack, Instagram, the static site — all are renderings of the same underlying `content/` folder.

---

## First-month concrete milestones

- **Week 1:** research folder populated (20 topics queued, 10 doctors registered, palette locked).
- **Week 2:** first 3 editions produced manually using the templates (quality calibration pass).
- **Week 3:** domain registered; Astro project scaffolded; Cloudflare Pages deploy working. First 3 editions live on `nutrientbrief.in/editions/001…003`.
- **Week 4:** Substack connected via API; Obsidian pointed at repo; pipeline runs first fully-automated edition (004).
- **Week 5-7:** cadence locks to 3 editions/week while pipeline stabilizes.
- **Week 8:** move to 6 editions/week (the full Mon-Sat schedule).

---

## The one-line version

**Source of truth = the git repo.** Everything downstream (Substack, static site, Instagram, Obsidian) is a rendering of it. You own the repo; platforms come and go.
