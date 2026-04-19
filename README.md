# The Nutrient Brief

*One nutrient a day. Mechanism-first, not prescription. Indian clinicians where available.*

This repo is the canonical source of every edition. Substack, `nutrientbrief.in`, Instagram, and WhatsApp are all renderings of what lives here.

## What gets published, when

| Day | Category | Example topics |
|---|---|---|
| Mon | Macro of the week | Protein, fiber, omega-3, carbs |
| Tue | Mineral / Micro | Magnesium, zinc, iron, iodine |
| Wed | Viral claim, audited | Creatine, ashwagandha, seed oils |
| Thu | Traditional / Ayurvedic | Turmeric, ashwagandha, triphala |
| Fri | Research spotlight | One recent peer-reviewed paper |
| Sat | Reader digest | Q&A / recap |
| Sun | Prep only — no publish |

## Three artifacts per edition

Every edition produces three rendered forms from one research pass:

1. **Deep-Dive** — 500-600 word markdown with cited sources (`deep-dive.md`)
2. **Share Card** — mobile-first HTML, one screen (`share-card.html` + rendered PDF)
3. **Instagram Carousel** — 4 poster-style slides at 1080x1350 (`carousel/slide_01.html`...`slide_04.html`)

All three share the same accent colour, memory anchor, and disclaimer — visual continuity is a brand rule.

## Editorial stance

- We teach *how* nutrients work, not *what* to take.
- Claims are tagged by evidence strength; weak claims are labeled weak.
- Indian clinicians quoted where available; international when no Indian specialist fits.
- No brand coverage, ever. No "buy / take / dose-for-you" language.

See [`editorial/editorial_framework.md`](editorial/editorial_framework.md) for the full stance and source-tier rules.

## Directory layout

```
content/editions/NNN_<slug>/          - the publishable artifacts per edition
content/drafts/pending_review/        - edition held pending manual review
content/pending_substack/             - retry queue for Substack posts
content/pending_ig/                   - retry queue for IG scheduling
research/topic_backlog.md             - curated upcoming topics
research/trending_report.md           - weekly output of trend-detection script
research/doctor_registry.md           - whitelisted clinicians
drafts/anchor_library.md              - used memory-anchor log
drafts/instagram_carousel/            - templates + rendering assets
editorial/                            - pipeline contracts (framework, spec, compliance)
pipeline/                             - the automation scripts
assets/NNN/                           - generated PNGs for IG
run_log.md                            - one line per pipeline run
manifest.json                         - meta
```

## How it runs

A scheduled task fires once a day at 05:00 IST. It reads `editorial/PIPELINE_SPEC.md`, picks a topic via the rules in `editorial/TOPIC_SELECTION.md`, produces the three artifacts, compliance-checks them, commits them here, then pushes to Substack / IG / WhatsApp. Zero daily user action.

See [`editorial/PIPELINE_SPEC.md`](editorial/PIPELINE_SPEC.md) for the full contract.

## Failure isolation

A single downstream failure never cancels the edition. Only the canonical publish step (git commit + push) can halt a run. Website failures degrade to a GitHub blob fallback. WhatsApp / Substack / IG failures retry silently. See `editorial/PIPELINE_SPEC.md` section 8.

## Licensing

Content under CC BY-NC 4.0 (share with attribution, non-commercial). Code under MIT. Medical disclaimers apply to all content — this is educational material, not medical advice.

## Disclaimer

The Nutrient Brief is educational. It is not a substitute for personal medical advice, diagnosis, or treatment. Always consult a qualified clinician before starting any supplement or changing medication.
