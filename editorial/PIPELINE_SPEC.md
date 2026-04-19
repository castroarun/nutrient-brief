# Project 13 — Pipeline Spec

*The auto-generation contract. Every scheduled run of this pipeline reads this file and produces output that conforms exactly to it. Editorial framework (`editorial_framework.md`) defines what goes *into* the content. This file defines what comes *out* and where it lands.*

*Last updated: 2026-04-19*

---

## 1. How the pipeline runs

- **Trigger:** scheduled task, 05:00 IST daily (Mon-Sat publishing; Sun prep-only).
- **Entry:** a fresh Claude conversation, instructed to "run the next edition per `PIPELINE_SPEC.md`."
- **Input state:** reads `research/topic_backlog.md` (next unpublished topic), `drafts/anchor_library.md` (to avoid anchor reuse), `research/doctor_registry.md` (doctor selection).
- **Output state:** writes edition files into the content repo; publishes to destinations; logs the run.

Zero user action required once scheduled — per the hard autonomy constraint.

---

## 2. Inputs (read by the pipeline)

| File | Purpose |
|---|---|
| `research/topic_backlog.md` | Ordered list of upcoming topics, tagged by day-of-week category |
| `research/trending_report.md` | Written every Sunday — candidate nutrients surfacing from trend signals |
| `research/doctor_registry.md` | Whitelist of citable clinicians with specialty + institution |
| `drafts/anchor_library.md` | Used anchors (prevents repetition) + unused-but-drafted anchors |
| `editorial_framework.md` | Source tier rules, credential rules, red-flag list |
| `compliance_notes.md` | DMRA/FSSAI/ASCI guardrails |
| `TOPIC_SELECTION.md` | The two-lane selection system (curated backlog + trending override) |

---

## 3. The edition ID + file naming convention

Every edition has a **zero-padded 3-digit ID** (001-999) and a **URL slug**.

```
NNN_<kebab-topic>
```

Examples:
- `001_magnesium-glycinate`
- `002_vitamin-d3-k2`
- `003_ashwagandha`

This ID is used as the folder name, prefix, and URL slug. Never reused, never changed.

---

## 4. Outputs — three artifacts per edition

Every edition produces **three** artifacts from a single research pass. Same sources, same doctor, same anchor — different rendering.

### Artifact A — Deep-Dive (Markdown)

- **Path:** `content/editions/NNN_<slug>/deep-dive.md`
- **Length:** 500-600 words editorial body
- **Frontmatter:** edition_number, category, topic, date, doctor_cited, anchor, sources[], pipeline_status
- **Structure (fixed 9 sections):**
  1. Hook (1 sentence, surprising)
  2. What it is (2-3 sentences, plain language)
  3. How your body uses it (3-4 sentences, mechanism)
  4. What the evidence actually says (1-2 cited studies, strength-explicit)
  5. Who tends to benefit most (the 6 groups, paragraph form)
  6. Forms and absorption rates (numerical % for every form)
  7. Amounts (RDA ranges + trial protocol ranges — passive voice)
  8. Who should think twice (caution groups)
  9. Expert context (paraphrased; Indian clinician preferred)
  10. Memory anchor (one sentence, bold-italic)
  11. Sources (numbered)
  12. Standard disclaimer block

**Publishes to:** Substack article body (full text) + own static site as prose page.

### Artifact B — Share Card (HTML)

- **Path:** `content/editions/NNN_<slug>/share-card.html`
- **Dimensions:** mobile-first, max-width 640px
- **Self-contained:** no external fonts, CDNs, or images. All SVGs inline. One CSS block.
- **Canonical template:** `drafts/template_share_v1.html` (promoted from `drafts/test_001_magnesium_glycinate_share.html`).

**Locked visual system:**

| Property | Value |
|---|---|
| Background | `#faf7f2` (warm cream) — solid, no pattern (keep the page quiet; let content carry) |
| Ink | `#141623` |
| Accent per-edition | Varies — default `#c7462d` (coral). Chosen per topic. |
| Navy (eyebrow + dots) | `#1e3a8a` |
| Headline font | Georgia / Iowan Old Style serif |
| Body font | system sans (-apple-system, SF Pro Text, Inter) |
| Evidence-bar colours | `--ok #3f7d58` (strong), `--mid #d1932c` (mixed), `--weak #a36f6f` (weak) |

**Locked structure (11 sections):**

1. **Masthead** — "The Nutrient Brief" · Edition NN · category. *Single horizontal rule (top black border only — no bottom line). Clean page; no background pattern.*
2. **Category eyebrow** — navy pill, uppercase tracked text (e.g. "MINERAL OF THE WEEK", "RESEARCH SPOTLIGHT")
3. **Title + deck** — serif H1 with italic accent word, one-sentence deck below
4. **Stat block** — one large number (~50, 48%, 1-in-3 style) paired with one supporting sentence
5. **Mechanism pills** — two-column "Accelerator / Brake" or equivalent binary framing
6. **Evidence bars** — 5 outcome rows, 5-dot scale each (strong / mid / weak coloring)
7. **Who tends to benefit most** — 2×3 card grid (six groups)
8. **Forms, absorption, amounts** — 4-row forms table, *every form shows numerical absorption % AND a dot-bar* (no asymmetry — if one row has a number, every row has one), plus an amounts callout with RDA range + trial-dose range
9. **Who should think twice** — 2-4 small caution cards
10. **Doctor's voice** — paraphrased blockquote in tinted callout; attribution with degree, institution, pub-count
11. **Memory anchor** — dark-background callout; inline SVG icon (topical); one italic serif line
12. **Footer** — compressed sources + standard disclaimer

**Publishes to:** own static site as `/editions/NNN-<slug>` standalone page + embedded inline in Substack article.

### Artifact C — Instagram Carousel (4 slides, 1080×1350)

- **Path:** `content/editions/NNN_<slug>/carousel/slide_01.html ... slide_04.html` + `carousel_preview.html` (all-slides view)
- **Per-slide dimensions:** 1080 × 1350 (4:5 IG portrait).
- **Canonical template:** `drafts/instagram_carousel/carousel_4slide_preview.html` (promoted once chosen).
- **Export:** pipeline uses headless Chrome to render each slide → PNG. PNGs land in `/assets/NNN/` for IG scheduler pickup (Buffer / Later / Meta Business Suite).

**Locked slide sequence (4 slides — max, poster-style):**

| # | Purpose | Content anchor |
|---|---|---|
| 01 | Hook | One sentence + one visual. Max 15 words. Thumb-stopper. |
| 02 | The stat | One oversized number + one 6-12 word caption. Nothing else. |
| 03 | Mechanism poster | Two colored cards (brake/accelerator binary). One summary line. |
| 04 | Memory anchor + CTA | Dark background. Anchor line big and italic. Minimal follow prompt. |

*Hard cap at 4 slides — readers won't swipe past that on IG. Every slide must stand alone. Each slide **must** be poster-style, not article-style: one idea, large type, 2-4 lines max. If the point needs more than 4 lines on a slide, split the idea or cut it — do not cram. The Share Card carries the dense detail; the carousel earns the click.*

**Publishes to:** Instagram (via Buffer or Meta Business Suite scheduler).

---

## 5. Consistency rules — what the pipeline must enforce

These are the hard-coded rules that produce editorial consistency across hundreds of editions.

### Content rules

- **Every form with numerical absorption has all forms with numerical absorption.** No asymmetry within a forms table.
- **Benefit grid is 6 cards (2×3).** If fewer than 6 groups are defensible from literature, drop cards rather than fill with speculation. Never go below 4.
- **Section is called "Who tends to benefit most"** — never "who should take this," never "who needs to supplement" (positive framing without prescription).
- **Doctor is Indian by default.** Only fall back to international when no Indian clinician with verifiable specialty-topic match exists in `research/doctor_registry.md`.
- **Every doctor quote is paraphrased, not verbatim.** Pipeline verifies source-work exists; adds "Paraphrased from published work of…" attribution.
- **Memory anchor is novel per edition.** Pipeline checks `anchor_library.md` — if collision, regenerate.
- **Every claim links to a Tier 1-2 source.** Tier 3 allowed but must be tagged "preliminary."
- **No buy / take / dose-for-you language.** Passive voice: "Trials used…," "Ranges sit between…"
- **Disclaimer block appears unmodified** at the bottom of every Deep-Dive and as compressed footer on Share Card.

### Visual rules

- **Navy eyebrow is category-coded:**
  - Monday → `MACRO OF THE WEEK`
  - Tuesday → `MINERAL OF THE WEEK`
  - Wednesday → `VIRAL CLAIM, AUDITED`
  - Thursday → `TRADITIONAL / AYURVEDIC`
  - Friday → `RESEARCH SPOTLIGHT`
  - Saturday → `READER DIGEST`
- **Accent colour varies per edition** (pulled from a 20-color curated palette). Base coral is default.
- **Memory anchor SVG is unique per edition** — topical, simple, single-path preferred.
- **All three artifacts carry the same accent colour + eyebrow label + memory-anchor line** for the edition. Visual continuity across Deep-Dive/Share Card/Carousel is a brand rule.

---

## 6. Compliance check (pipeline runs before publish)

Every edition must pass these checks automatically:

- [ ] No "buy," "cure," "prevent," or disease-treatment claims in any artifact
- [ ] No specific product brands mentioned
- [ ] No personal dosing prescription (passive voice on doses)
- [ ] Doctor attribution verified against `doctor_registry.md`
- [ ] All sources resolve in PubMed / journal URLs
- [ ] Disclaimer block present on Deep-Dive + Share Card + final carousel slide
- [ ] Memory anchor not a duplicate

Failure on any check → edition is held in `content/drafts/pending_review/` instead of published.

---

## 7. Publishing destinations

| Artifact | Destination | Method |
|---|---|---|
| Deep-Dive | Substack | Substack API (auth via long-lived token) |
| Deep-Dive | Own static site | `git push` → Vercel auto-deploy |
| Share Card | Own static site (embedded in deep-dive page + standalone at `/editions/NNN-slug/share`) | Part of same git push |
| Share Card | Substack (embedded in article) | HTML block inside Substack post |
| Share Card PDF | Arun's WhatsApp (review notification) | Twilio WhatsApp API — `MediaUrl=raw.githubusercontent.com/castroarun/nutrient-brief/main/content/editions/NNN_<slug>/share-card.pdf` (GitHub-direct; no website dependency) |
| Carousel PNGs | Instagram | Buffer API (or Meta Business Suite API) with 9am-IST schedule |
| All artifacts | Obsidian vault | iCloud sync (Markdown auto-appears; no pipeline step needed) |

All destinations use long-lived tokens. No daily login anywhere. Twilio Account SID + Auth Token stored in a pipeline-runner `.env` file, never committed to git.

### Twilio notification payload (per edition)

```
To:       whatsapp:+919941022034          # Arun (env: ARUN_WHATSAPP)
From:     whatsapp:+14155238886           # Twilio sandbox → production ("The Nutrient Brief") after Meta verification
Body:     Edition NNN: <topic>.
          Deep-dive: <resolved_deep_dive_url>    # see URL resolution below
          Memory anchor: "<one-line italic>"
MediaUrl: https://raw.githubusercontent.com/castroarun/nutrient-brief/main/content/editions/NNN_<slug>/share-card.pdf
```

**Sent as the final pipeline step** after `git push` completes. Pipeline HEAD-checks the GitHub raw URL (expects HTTP 200) before firing Twilio — if GitHub hasn't propagated yet (usually <60s after push), pipeline retries with 10s backoff up to 3 times.

**Deep-dive URL resolution (graceful degradation):** before composing the Body, pipeline tries `HEAD https://nutrientbrief.in/editions/NNN-<slug>` with a 5s timeout.

- **200 OK** → use the branded URL (`https://nutrientbrief.in/editions/NNN-<slug>`) in the Body.
- **non-200 / timeout / DNS failure** → fall back to the GitHub blob URL (`https://github.com/castroarun/nutrient-brief/blob/main/content/editions/NNN_<slug>/deep-dive.md`). WhatsApp still fires, reader still gets the deep-dive, edition is still "published."

Website failure is therefore **never fatal**. The branded URL is a convenience layer; the canonical publish is git.

**Why GitHub-raw over nutrientbrief.in for MediaUrl:** decouples the WhatsApp notification pipe from Vercel deploys. If Vercel is down or a build fails, WhatsApp still fires. The Deep-dive *link* in the Body can degrade to the GitHub blob fallback; the Share Card PDF always travels via GitHub-raw regardless.

**Repo visibility requirement:** `nutrient-brief` repo must be **public** for Twilio to fetch (no auth header support in Twilio's media fetcher). Research/drafts live on a `research` branch; only published editions get merged to `main`.

### Credentials

All in `projects/project_13_nutrition_titbit/.env`, git-ignored:

```
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=<live token>
TWILIO_FROM_WHATSAPP=whatsapp:+14155238886
ARUN_WHATSAPP=whatsapp:+919941022034
GITHUB_USER=castroarun
GITHUB_REPO=nutrient-brief
SITE_BASE_URL=https://nutrientbrief.in
```

`.env` is read at pipeline-run time only. Token is never logged, never echoed, never committed.

---

## 8. Failure isolation & graceful degradation

The pipeline has many moving parts. The rule is: **a single downstream failure never cancels the edition.** Only the canonical publish step (git) can halt a run.

### 8.1 Failure tiers

| Tier | Examples | Pipeline behavior |
|---|---|---|
| **Fatal** | Content generation errors, compliance check fails, git commit/push fails, doctor-registry lookup fails with no fallback | Abort. Edition held in `content/drafts/pending_review/`. Run logged `❌`. **This is the only class that halts subsequent scheduled runs until manually cleared.** |
| **Degraded (delivery)** | Twilio 5xx, Twilio rate limit, GitHub-raw propagation timeout | Retry 3x with exponential backoff (10s → 30s → 60s). If all fail, log `⚠ whatsapp_delivery_failed`, continue. Tomorrow's run notices the gap and re-attempts yesterday's send as part of the morning sequence. |
| **Degraded (website)** | Vercel build failed, `nutrientbrief.in` DNS not yet propagated, 404 at `/editions/NNN-slug`, 5xx from host | Do nothing special. Deep-dive URL resolver falls back to the GitHub blob URL automatically (see §7). Edition still publishes, WhatsApp still fires, IG still queues. Log `⚠ site_degraded` on the run line. |
| **Degraded (Substack)** | Substack API error, auth expired | Queue in `content/pending_substack/NNN.yaml`. Tomorrow's run re-attempts all pending Substack posts before the new edition. |
| **Degraded (Instagram)** | Buffer/Meta API error, token expired | Queue in `content/pending_ig/NNN/`. PNGs remain ready for manual upload. Log `⚠ ig_queue_stalled`. |

### 8.2 The pipeline's publish ordering

Order matters — fail-fast on canonical steps, fail-soft on delivery steps.

```
1. generate_content       → fatal if fails
2. compliance_check       → fatal if fails
3. git_commit_push        → fatal if fails     ← canonical "published" state
4. head_check_github_raw  → retry 3x, degraded if fails
5. head_check_site_url    → degraded if fails (triggers URL fallback)
6. send_whatsapp          → retry 3x, degraded if fails
7. post_substack          → degraded if fails (queues for retry)
8. schedule_ig            → degraded if fails (queues for retry)
9. log_run                → always runs last, even on degraded paths
```

Once step 3 succeeds the edition is considered **published**. Every subsequent step is best-effort.

### 8.3 Retry-and-forget vs retry-until-manual

- **Retry-and-forget:** Twilio sends, Substack posts, IG schedules. Tomorrow's run re-attempts silently. Arun is notified only if 3 consecutive days fail for the same destination.
- **Retry-until-manual:** only the fatal tier. If pipeline halts, Arun gets a WhatsApp that reads `⚠ Pipeline halted: <reason>. Edition NNN in pending_review. Ack to resume.`

### 8.4 What Arun sees

- **Happy path:** one WhatsApp per morning. Edition NNN, deep-dive link, PDF attached.
- **Website down but everything else works:** exactly the same WhatsApp, except the Deep-dive link is a GitHub URL instead of `nutrientbrief.in`. No other visible difference.
- **WhatsApp fails:** nothing in the morning, but tomorrow's WhatsApp will open with "Catch-up: Edition NNN (yesterday)." plus the usual line for today.
- **Fatal halt:** one WhatsApp saying the pipeline is paused + the reason. No further auto-runs until ack.

---

## 9. Run log

Every pipeline run appends one line to `run_log.md`:

```
2026-06-07 05:00 IST | Edition 001 | magnesium-glycinate | ✅ published | deep-dive:4m | share:1m | carousel:2m | subs:published | site:push:ok | ig:queued:09:00 | wa:sent
2026-06-08 05:00 IST | Edition 002 | vitamin-d3-k2      | ⚠ published_degraded | ... | site:degraded(fallback:github) | wa:sent
2026-06-09 05:00 IST | Edition 003 | —                  | ❌ halted | reason: git_push_auth_failed | held:pending_review/
```

Only `❌ halted` blocks subsequent scheduled runs. `⚠ published_degraded` does not — the next day's run proceeds normally.
