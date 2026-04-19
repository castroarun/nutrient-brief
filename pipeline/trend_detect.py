"""
trend_detect.py - weekly trend aggregator.

Runs Sundays 04:00 IST. Reads the nutrient watchlist, polls four signals,
z-scores each, composes a ranked table, writes research/trending_report.md.

Signals (see TOPIC_SELECTION.md section 4):
- Google Trends  (pytrends)        weight 0.35
- Reddit heat    (public JSON)     weight 0.25
- PubMed spike   (E-utilities)     weight 0.20
- News mentions  (Google News RSS) weight 0.20

Threshold for override: composite_z >= 2.5 (max 2 overrides per week).
Evidence gate: must have >= 2 Tier-1/2 sources to qualify.
"""
from __future__ import annotations
import datetime as dt
from pathlib import Path


WATCHLIST: list[str] = [
    # Subset - expand to the full ~200 when wiring up.
    "magnesium", "creatine", "ashwagandha", "vitamin d", "vitamin k2",
    "omega-3", "zinc", "iron", "iodine", "selenium", "b12", "folate",
    "choline", "turmeric", "curcumin", "triphala", "ghee", "neem",
    "moringa", "giloy", "cinnamon", "green tea", "caffeine", "vitamin c",
    "vitamin e", "vitamin a", "calcium", "potassium", "collagen",
    "glycine", "taurine", "l-theanine", "probiotics", "inulin",
]


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT    = REPO_ROOT / "research" / "trending_report.md"


def fetch_google_trends(terms: list[str]) -> dict[str, float]:
    # TODO: pytrends.TrendReq, .build_payload(terms, timeframe='now 7-d'), .interest_over_time()
    # Return dict of term -> week-over-week % change
    return {}


def fetch_reddit_heat(terms: list[str]) -> dict[str, int]:
    # TODO: GET https://www.reddit.com/r/{sub}/top.json?t=week&limit=25 for each of
    # r/Supplements, r/Nootropics, r/Nutrition, r/AskDocs. Count term mentions in titles+selftext.
    return {}


def fetch_pubmed_new_papers(terms: list[str], days: int = 30) -> dict[str, int]:
    # TODO: Biopython Entrez.esearch on each term with date range filter
    return {}


def fetch_news_mentions(terms: list[str]) -> dict[str, int]:
    # TODO: feedparser on Google News RSS per term
    return {}


def zscore(values: dict[str, float]) -> dict[str, float]:
    if not values:
        return {}
    xs = list(values.values())
    mean = sum(xs) / len(xs)
    var  = sum((x - mean) ** 2 for x in xs) / max(len(xs) - 1, 1)
    std  = var ** 0.5 or 1.0
    return {k: (v - mean) / std for k, v in values.items()}


def composite(tz: dict, rz: dict, pm: dict, nw: dict) -> dict[str, float]:
    result = {}
    for term in set(tz) | set(rz) | set(pm) | set(nw):
        result[term] = (
            0.35 * tz.get(term, 0.0) +
            0.25 * rz.get(term, 0.0) +
            0.20 * pm.get(term, 0.0) +
            0.20 * nw.get(term, 0.0)
        )
    return result


def write_report(ranked: list[tuple[str, float, dict]]) -> None:
    lines = [
        "# Trending Report",
        "",
        f"*Auto-generated {dt.datetime.now().isoformat()}.*",
        "",
        "## This week's composite ranking",
        "",
        "| rank | nutrient | composite_z | evidence_status |",
        "|---|---|---|---|",
    ]
    for i, (term, score, _meta) in enumerate(ranked[:25], start=1):
        status = "ok" if score < 2.5 else "override_candidate"
        lines.append(f"| {i} | {term} | {score:.2f} | {status} |")
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    tz = zscore(fetch_google_trends(WATCHLIST))
    rz = zscore(fetch_reddit_heat(WATCHLIST))
    pm = fetch_pubmed_new_papers(WATCHLIST)       # raw count, not z
    nw = fetch_news_mentions(WATCHLIST)           # raw count, not z
    scores = composite(tz, rz, pm, nw)
    ranked = sorted(scores.items(), key=lambda kv: -kv[1])
    write_report([(k, v, {}) for k, v in ranked])
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
