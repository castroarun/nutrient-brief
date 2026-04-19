# Project 13 — Topic Selection & Trending Coverage

*How the pipeline decides what to write about each day, without user input.*

*Last updated: 2026-04-19*

---

## 1. The two-lane system

Every edition slot gets filled from one of two lanes:

| Lane | Source | When it fires |
|---|---|---|
| **A — Curated backlog** | `research/topic_backlog.md` | Default for 5 of 6 weekdays |
| **B — Trend-triggered** | Trend-detection script output | Wednesday by default; can override any other day if signal is strong |

The weekly category rhythm sets the *type* of content each day; the two lanes decide the *specific topic*.

---

## 2. Weekly category rhythm (the skeleton)

| Day | Category | Typical topic shape |
|---|---|---|
| Mon | **Macro of the week** | Protein, fiber, omega-3, carbs, etc. |
| Tue | **Mineral / Micro of the week** | Magnesium, zinc, iron, iodine, etc. |
| Wed | **Viral claim, audited** ← *trending lane lives here* | Creatine for women, ashwagandha + cortisol, TikTok-viral seed oil debate |
| Thu | **Traditional / Ayurvedic** | Turmeric, ashwagandha, triphala, ghee, neem |
| Fri | **Research spotlight** | A single recent peer-reviewed paper explained |
| Sat | **Reader digest** | Q&A / recap / reader-submitted question |
| Sun | **Prep only** | Pipeline queues next week, no publish |

Six editions per week, ~312 per year.

---

## 3. The curated backlog — `research/topic_backlog.md`

A single markdown file, ordered queue. Each entry:

```
| slug | category | priority | source_strength | last_touched | notes |
|---|---|---|---|---|---|
| magnesium-glycinate | micro | 1 | Tier-1 | — | Sleep+anxiety angle |
| vitamin-d3-k2 | micro | 1 | Tier-1 | — | Synergy explanation |
| creatine-monohydrate | macro | 1 | Tier-1 | — | Safe default; pull if trending lane activates |
| ashwagandha | traditional | 2 | Tier-2 | — | Cortisol claims |
| ...
```

**How it's built (once, then topped up):**

- Initial seed: ~120 nutrients/compounds drawn from ICMR, NIH ODS, EFSA lists — gives 6 months of runway.
- Weekly top-up (Sunday prep run): pipeline reads PubMed for the last 30 days and appends any nutrient with >= 3 new high-quality papers where we don't already have coverage scheduled in the next 30 days.
- Editorial override: Arun can drop topics into the backlog manually at any time. Pipeline never removes manually-added entries without a flag.

**How the pipeline picks:** reads the backlog, filters by category for the day, picks the highest-priority entry where `last_touched` is blank or older than 180 days.

---

## 4. The trending lane — how creatine (or whatever is hot) gets covered

This is the zero-touch "what is the internet talking about *this week*" channel.

### 4.1 Signals the pipeline watches (all polled automatically, no user action)

| Signal | Source | What it measures | Refresh |
|---|---|---|---|
| **Google Trends rise** | `pytrends` (unofficial Python API) | Week-over-week search interest in a watchlist of ~200 nutrient/compound terms | Weekly, Sun 04:00 IST |
| **Reddit heat** | `r/Supplements`, `r/Nootropics`, `r/Nutrition`, `r/AskDocs` top-of-week posts via Reddit public JSON feed | Which nutrient names appear in the top 25 posts this week | Weekly |
| **PubMed publication spike** | NCBI E-utilities `esearch` | Nutrients with >= 3 new human-trial papers in last 30 days | Weekly |
| **News / press mentions** | Google News RSS for nutrient watchlist | Mainstream coverage (Times of India, Indian Express, BBC, NYT, Guardian) | Weekly |

Four independent signals → one ranked `trending_report.md` written every Sunday.

### 4.2 Scoring & the Wednesday slot

Each candidate nutrient gets a composite score:

```
score = 0.35 * trends_zscore
      + 0.25 * reddit_mentions_zscore
      + 0.20 * pubmed_new_papers
      + 0.20 * news_mentions
```

The **top-scoring nutrient with a defensible evidence base** fills Wednesday's "Viral claim, audited" slot. "Defensible evidence base" means >= 2 Tier-1 or Tier-2 sources exist — if the trending topic has no real literature to cite, it's flagged as `hype_only` and Wednesday falls back to the curated backlog.

### 4.3 Override — when trending jumps any other day's slot

If a nutrient's composite score crosses **z ≥ 2.5** (a hard spike — something genuinely blowing up in the week), it gets an **override flag**. The pipeline can then:

- Swap it into the next matching category slot (e.g., creatine is a macro → Monday)
- Or run a second Wednesday-style audit within the same week if two trending topics are hot simultaneously

Hard-capped: **maximum 2 trend-overrides per week** so the publication isn't whipsawed by algorithms.

### 4.4 Creatine example — how this would actually run

> **Scenario:** creatine usage spikes on Instagram + TikTok among women + older adults. Reddit `r/Supplements` has 8 of the top-25 posts mentioning creatine. Google Trends shows +180% YoY.

**Sunday prep run (pipeline):**

1. Trend script outputs `trending_report.md` with creatine at top, composite z-score = 3.1 (above override threshold).
2. PubMed check: creatine has 40+ years of literature, Tier-1 RCTs for strength/cognition/sarcopenia. ✅ Defensible.
3. Anchor library check: creatine anchor slot is available. ✅
4. Doctor registry check: Dr. Darshan Shah (Holistic nutrition, Mumbai) + backup Dr. Shawn Arent (international). ✅
5. Pipeline queues:
   - **Wednesday** → creatine edition under "Viral claim, audited" framing: *"Creatine isn't just for lifters — here's what the research actually shows for women, older adults, and cognition."*
   - Curated backlog entry gets pushed down one slot.

**Wednesday 05:00 IST:** standard pipeline runs. Produces deep-dive MD + share card HTML + 4-slide IG carousel. All three carry the same "viral claim audited" eyebrow, same coral accent, same memory anchor. No user action.

**Post-publish:** `run_log.md` records "triggered by trending-lane override, composite z=3.1." `topic_backlog.md` marks creatine as `last_touched: 2026-XX-XX` so it doesn't repeat within 180 days.

---

## 5. Editorial anti-repeat rules

- **Per-nutrient cooldown:** 180 days. A nutrient covered in April doesn't reappear as a headline topic until October. Can be referenced in passing (e.g., in a digest or a synergy mention).
- **Per-category cadence:** a category (e.g., "mineral") fills its day slot weekly, but the nutrient rotates.
- **Anchor library check:** `drafts/anchor_library.md` logs every used memory-anchor metaphor. New editions check for collision before generating.
- **Source diversity check:** if 4 consecutive editions cite the same single journal or same single researcher, pipeline flags for manual review.

---

## 6. What the pipeline does NOT decide

- **Editorial positioning.** The "mechanism-first, not prescription" stance is fixed in `editorial_framework.md` and `PIPELINE_SPEC.md`. Trending topics are still covered through the mechanism lens, not as product recommendations.
- **Sensational angles.** If creatine is trending because of a TikTok claim that's not supported by literature, the pipeline either (a) runs it under "Viral claim, audited" with the debunk framing, or (b) skips it.
- **Brand coverage.** Never. No brand-specific editions regardless of trend signals.

---

## 7. Files this spec touches

| File | Role |
|---|---|
| `research/topic_backlog.md` | Curated queue — read every weekday |
| `research/trending_report.md` | Written every Sunday by trend-detection script |
| `research/doctor_registry.md` | Whitelist — consulted per edition |
| `drafts/anchor_library.md` | Used-anchor log — prevents repetition |
| `run_log.md` | Records which lane (curated vs trending) fired each day |

---

## 8. First-month concrete setup

| Week | Action |
|---|---|
| 1 | Seed `topic_backlog.md` with 120-nutrient initial list (done via one research pass) |
| 2 | Build `trend-detect.py` — four-signal aggregator, writes `trending_report.md` weekly |
| 3 | Wire trend-detect into the Sunday prep run; dry-run for 2 weeks before it's allowed to override |
| 4 | Unlock override: trending can now displace curated when z ≥ 2.5 |

Until Week 4, Wednesday runs from the curated "viral/audit" sub-queue (hand-picked trending claims from the last 6 months — green tea + metabolism, apple cider vinegar, seed oils, etc.).

---

## 9. TL;DR

- **Default:** the curated backlog fills the week, one topic per day, categorized by weekday.
- **Trending:** a zero-touch script watches Google Trends + Reddit + PubMed + News every Sunday, ranks candidate nutrients, and fills Wednesday. Hard spikes (z ≥ 2.5) can override another weekday.
- **Creatine scenario:** exactly this pipeline would catch a creatine surge and produce a full edition on Wednesday, no user action, still mechanism-first.
- **Hard caps:** max 2 trend-overrides per week, 180-day per-nutrient cooldown, anchor-library no-duplicate check, doctor-registry verification, Tier-1/2 source requirement.
