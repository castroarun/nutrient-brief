# Trending Report

*Auto-written by `pipeline/trend_detect.py` every Sunday at 04:00 IST. Human-readable summary of the week's trend signals across the nutrient watchlist.*

**Last auto-run:** — (not yet run)

---

## This week's composite ranking

Ranked by composite z-score:

| rank | nutrient | composite_z | trends_z | reddit_z | pubmed_n | news_n | evidence_status | action |
|---|---|---|---|---|---|---|---|---|
| — | (awaiting first run) | — | — | — | — | — | — | — |

**Composite formula:**

```
score = 0.35 * trends_zscore
      + 0.25 * reddit_mentions_zscore
      + 0.20 * pubmed_new_papers
      + 0.20 * news_mentions
```

**Override threshold:** any nutrient with `composite_z >= 2.5` is flagged for override (max 2 overrides per week). Threshold < 2.5 fills Wednesday only.

**Evidence gate:** nutrient must have >= 2 Tier-1 or Tier-2 sources available to qualify. `hype_only` means high trend signal but no defensible literature — pipeline skips.

---

## Raw signals (last 7 days)

### Google Trends (pytrends)

Watchlist: the 200 nutrients + compounds tracked. Week-over-week rise.

*(Table populated on first run.)*

### Reddit (r/Supplements, r/Nootropics, r/Nutrition, r/AskDocs)

Top-25 posts each, scanned for nutrient-name occurrences.

*(Populated on first run.)*

### PubMed (E-utilities esearch)

New papers published in last 30 days, filtered by human trials. Nutrients with >= 3 new papers surface here.

*(Populated on first run.)*

### Google News

RSS feeds from Times of India, Indian Express, BBC, NYT, Guardian. Nutrient-name occurrences.

*(Populated on first run.)*

---

## History

| week_ending | top_3_nutrients | overrides_triggered | wednesday_pick |
|---|---|---|---|
| — | — | — | — |
