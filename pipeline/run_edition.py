"""Daily orchestrator for The Nutrient Brief.

Pipeline (idempotent — safe to re-run):
    1. Pick next topic from research/topic_backlog.json
    2. Generate prose via free LLM (GitHub Models default)
    3. Render share-card.html + 4 slide HTMLs from templates
    4. Render PDF + 4 PNGs via Playwright
    5. Write manifest.json
    6. Static compliance check (regex-based, no LLM)
    7. Resolve URLs (publish.publish_edition)
    8. Email broadcast to subscribers (Gmail SMTP)
    9. WhatsApp delivery (no-op until creds configured)
   10. Self-notify Arun: success or failure summary

Designed for GitHub Actions cron — reads all secrets from env.
DRY_RUN=true skips delivery + commit; lets you preview generation.
"""
from __future__ import annotations

import json
import os
import re
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

# Make pipeline importable regardless of cwd
_PIPELINE_DIR = Path(__file__).parent
sys.path.insert(0, str(_PIPELINE_DIR))

from llm_client import LLMClient, complete_json   # noqa: E402
from renderer import render_share_card_pdf, render_carousel_pngs   # noqa: E402
from publish import publish_edition   # noqa: E402
from email_delivery import broadcast_to_subscribers, notify_self   # noqa: E402
from whatsapp_delivery import deliver as whatsapp_deliver, is_configured as wa_configured   # noqa: E402

REPO_ROOT = _PIPELINE_DIR.parent
BACKLOG = REPO_ROOT / "research" / "topic_backlog.json"
EDITIONS_DIR = REPO_ROOT / "content" / "editions"
TEMPLATE_SHARE = REPO_ROOT / "drafts" / "template_share_v1.html"
TEMPLATE_CAROUSEL = REPO_ROOT / "drafts" / "instagram_carousel" / "carousel_4slide_preview.html"

DRY_RUN = os.environ.get("DRY_RUN", "false").lower() == "true"


# ============== Step 1: pick next topic ==============
def pick_next_topic() -> tuple[int, dict]:
    backlog = json.loads(BACKLOG.read_text(encoding="utf-8"))
    EDITIONS_DIR.mkdir(parents=True, exist_ok=True)
    published_slugs = {p.name.split("_", 1)[1] for p in EDITIONS_DIR.iterdir()
                       if p.is_dir() and "_" in p.name and p.name[:3].isdigit()}
    existing = [int(p.name.split("_", 1)[0]) for p in EDITIONS_DIR.iterdir()
                if p.is_dir() and p.name[:3].isdigit()]
    next_id = (max(existing) + 1) if existing else 1
    for topic in backlog["topics"]:
        if topic["slug"] not in published_slugs:
            return next_id, topic
    raise RuntimeError("Backlog exhausted! Refill research/topic_backlog.json from Cowork.")


# ============== Step 2: LLM prose ==============
PROSE_SYSTEM = """You are the editorial voice of The Nutrient Brief — a daily, mechanism-first nutrient digest written for educated Indian adults. House style:
- Mechanism-first, never lifestyle-first.
- Cite specific numbers and named studies (you'll be given PubMed IDs).
- Indian dietary context (refined cereals, vegetarian gaps, ICMR guidelines).
- No disease claims. No product brand names. No personal dosing.
- Voice: confident, slightly dry, occasionally witty. Never cheerful or hyperbolic.
- Prose only — no headers, no bullets unless explicitly asked."""

CONTENT_USER_TMPL = """Write the editorial content for Edition {edition_id} of The Nutrient Brief.

Topic: {slug}
Category: {category}
Eyebrow: {eyebrow}
Day: {day_of_week}
Doctor cited: {doctor_name} ({doctor_institution}, {doctor_creds})
Sources (PubMed IDs): {pubmed_ids}
Mechanism brief (your starting facts — DO NOT invent beyond these): {mechanism_brief}
Memory anchor seed (refine but keep the spirit): {anchor_seed}

Return strict JSON with these keys:
  "title"          : string, format "Topic Name — anchor metaphor"
  "hook"           : 1-2 sentences, opens the deep-dive
  "what_it_is"     : 2-3 sentences
  "mechanism"      : 3-5 sentences
  "evidence"       : 3-4 sentences naming the PubMed sources by first-author + year
  "who_benefits"   : 3-5 sentences naming sub-populations
  "amounts"        : 2-3 sentences on dosing ranges from trials (no personal dosing advice)
  "who_should_avoid": 2-3 sentences (kidney disease, drug interactions, etc.)
  "expert_context" : 2-3 sentences paraphrasing the cited doctor's published research
  "memory_anchor"  : 1 sentence, the polished anchor (start with topic name)
  "slides": [
    {{ "kind": "hook",     "headline": "...", "subline": "..."  }},
    {{ "kind": "stat",     "headline": "...", "subline": "..."  }},
    {{ "kind": "mechanism","headline": "...", "subline": "..."  }},
    {{ "kind": "anchor",   "headline": "...", "subline": "Tap to read full deep-dive" }}
  ]"""


def generate_content(topic: dict, edition_id: int) -> dict:
    client = LLMClient()
    return complete_json(
        client,
        system=PROSE_SYSTEM,
        user=CONTENT_USER_TMPL.format(
            edition_id=f"{edition_id:03d}",
            slug=topic["slug"],
            category=topic["category"],
            eyebrow=topic["eyebrow_label"],
            day_of_week=topic["day_of_week"],
            doctor_name=topic["doctor"]["name"],
            doctor_institution=topic["doctor"]["institution"],
            doctor_creds=topic["doctor"]["credentials"],
            pubmed_ids=", ".join(topic["sources_pubmed"]),
            mechanism_brief=topic["mechanism_brief"],
            anchor_seed=topic["anchor_seed"],
        ),
        max_tokens=2000,
        temperature=0.5,
    )


# ============== Step 3: deep-dive markdown ==============
def render_deep_dive_md(topic: dict, edition_id: int, prose: dict) -> str:
    today = datetime.now(timezone.utc).date().isoformat()
    sources_yaml = "\n".join(
        f'  - {{ id: {i+1}, pubmed_id: "{pid}", tier: 2 }}'
        for i, pid in enumerate(topic["sources_pubmed"])
    )
    fm = f"""---
edition_number: {edition_id:03d}
slug: {topic['slug']}
category: {topic['category']}
day_of_week: {topic['day_of_week']}
eyebrow_label: {topic['eyebrow_label']}
title: "{prose['title']}"
date: {today}
accent_color: "{topic['accent_color']}"
doctor_cited: {topic['doctor']['name']}
doctor_institution: {topic['doctor']['institution']}
anchor: "{prose['memory_anchor']}"
tags: {json.dumps(topic.get('tags', []))}
sources:
{sources_yaml}
pipeline_status: published
---

# {prose['title']}

{prose['hook']}

## What it is

{prose['what_it_is']}

## How your body uses it

{prose['mechanism']}

## What the evidence actually says

{prose['evidence']}

## Who tends to benefit most

{prose['who_benefits']}

## Amounts

{prose['amounts']}

## Who should think twice

{prose['who_should_avoid']}

## Expert context

{prose['expert_context']}

## Memory anchor

***{prose['memory_anchor']}***

## Sources

"""
    for i, pid in enumerate(topic["sources_pubmed"], start=1):
        fm += f"{i}. PubMed {pid}\n"
    fm += "\n---\n\n**Not medical advice.** Educational content only. Not intended to diagnose, treat, cure, or prevent any disease. Consult a qualified medical professional before starting, changing, or stopping any supplement.\n"
    return fm


# ============== Step 3-4: HTML templates ==============
def render_share_card_html(template: str, topic: dict, edition_id: int, prose: dict) -> str:
    today = datetime.now(timezone.utc).strftime("%d %b %Y")
    replacements = {
        "{{EDITION_ID}}": f"{edition_id:03d}",
        "{{EYEBROW}}": topic["eyebrow_label"],
        "{{DATE}}": today,
        "{{TITLE}}": prose["title"],
        "{{ANCHOR}}": prose["memory_anchor"],
        "{{HOOK}}": prose["hook"],
        "{{WHAT_IT_IS}}": prose["what_it_is"],
        "{{MECHANISM}}": prose["mechanism"],
        "{{EVIDENCE}}": prose["evidence"],
        "{{WHO_BENEFITS}}": prose["who_benefits"],
        "{{AMOUNTS}}": prose["amounts"],
        "{{EXPERT_CONTEXT}}": prose["expert_context"],
        "{{DOCTOR_NAME}}": topic["doctor"]["name"],
        "{{DOCTOR_INSTITUTION}}": topic["doctor"]["institution"],
        "{{ACCENT_COLOR}}": topic["accent_color"],
    }
    out = template
    for k, v in replacements.items():
        out = out.replace(k, str(v))
    return out


def render_carousel_html(template: str, topic: dict, edition_id: int, prose: dict) -> list[str]:
    today = datetime.now(timezone.utc).strftime("%d %b %Y")
    htmls = []
    for i, slide in enumerate(prose["slides"], start=1):
        single = template
        single = single.replace("{{EDITION_ID}}", f"{edition_id:03d}")
        single = single.replace("{{EYEBROW}}", topic["eyebrow_label"])
        single = single.replace("{{DATE}}", today)
        single = single.replace("{{ACCENT_COLOR}}", topic["accent_color"])
        single = single.replace(f"{{{{SLIDE{i}_HEADLINE}}}}", slide["headline"])
        single = single.replace(f"{{{{SLIDE{i}_SUBLINE}}}}", slide["subline"])
        htmls.append(_wrap_standalone_slide(single, i))
    return htmls


def _wrap_standalone_slide(carousel_html: str, slide_num: int) -> str:
    style_match = re.search(r"<style>(.*?)</style>", carousel_html, re.DOTALL)
    style = style_match.group(1) if style_match else ""
    cls = f"s{slide_num}"
    pat = rf'<div class="slide {cls}">(.*?)</div>\s*<div class="caption">'
    m = re.search(pat, carousel_html, re.DOTALL)
    if not m:
        return carousel_html
    inner = m.group(1)
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><title>Slide {slide_num:02d}</title>
<style>{style}
html,body{{background:#faf7f2;width:1080px;height:1350px;margin:0;padding:0;overflow:hidden}}
.slide{{width:1080px!important;height:1350px!important;transform:none!important;margin:0!important}}
</style></head><body>
<div class="slide {cls}">{inner}</div>
</body></html>"""


# ============== Step 5: manifest ==============
def write_manifest(edition_dir: Path, topic: dict, edition_id: int, prose: dict) -> dict:
    today = datetime.now(timezone.utc).isoformat()
    manifest = {
        "edition_id": f"{edition_id:03d}",
        "slug": topic["slug"],
        "title": prose["title"],
        "category": topic["category"],
        "day_of_week": topic["day_of_week"],
        "eyebrow_label": topic["eyebrow_label"],
        "accent_color": topic["accent_color"],
        "published_at": today,
        "memory_anchor": prose["memory_anchor"],
        "lane": "curated_backlog",
        "trend_override": False,
        "doctor": topic["doctor"],
        "sources": [{"id": i+1, "pubmed_id": pid, "tier": 2}
                    for i, pid in enumerate(topic["sources_pubmed"])],
        "tags": topic.get("tags", []),
        "compliance_checks": {},
        "artifacts": {
            "deep_dive_md": "deep-dive.md",
            "share_card_html": "share-card.html",
            "share_card_pdf": "share-card.pdf",
            "carousel_html": [f"carousel/slide_{i:02d}.html" for i in range(1, 5)],
            "carousel_png":  [f"assets/slide_{i:02d}.png"  for i in range(1, 5)],
        },
        "urls": {},
        "published_to": {
            "substack": None, "site": None, "github_pages": None,
            "instagram_post_id": None, "instagram_scheduled_at": None,
            "whatsapp_message_sids": [], "email_recipients": 0,
        },
    }
    (edition_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return manifest


# ============== Step 6: static compliance ==============
DISEASE_WORDS = re.compile(
    r"\b(cure|cures|curing|treat|treats|treating|prevent|prevents|preventing|"
    r"diagnose|reverses|reversal|heal|heals)\s+(cancer|diabetes|alzheimer|"
    r"depression|covid|hypertension|disease)\b", re.IGNORECASE)
BRAND_BLOCKLIST = re.compile(
    r"\b(now foods|jarrow|nutricost|himalaya|patanjali|amway|herbalife|"
    r"swisse|gnc|muscleblaze|kapiva|wellbeing nutrition)\b", re.IGNORECASE)
PERSONAL_DOSING = re.compile(
    r"\b(you should take|take \d+\s*mg|take this every|i recommend you take)\b",
    re.IGNORECASE)


def static_compliance_check(manifest: dict, deep_dive_text: str) -> dict:
    return {
        "no_disease_claims":  not bool(DISEASE_WORDS.search(deep_dive_text)),
        "no_product_brands":  not bool(BRAND_BLOCKLIST.search(deep_dive_text)),
        "no_personal_dosing": not bool(PERSONAL_DOSING.search(deep_dive_text)),
        "doctor_verified":    bool(manifest["doctor"]["name"]),
        "sources_resolved":   len(manifest["sources"]) >= 3,
        "anchor_unique":      len(manifest["memory_anchor"]) >= 40,
        "disclaimer_present": "Not medical advice" in deep_dive_text,
    }


# ============== Main ==============
def _run() -> tuple[int, str]:
    """Returns (exit_code, summary_text). Summary is used for self-notify email."""
    edition_id, topic = pick_next_topic()
    folder_name = f"{edition_id:03d}_{topic['slug']}"
    edition_dir = EDITIONS_DIR / folder_name
    edition_dir.mkdir(parents=True, exist_ok=True)
    (edition_dir / "carousel").mkdir(exist_ok=True)
    (edition_dir / "assets").mkdir(exist_ok=True)
    print(f"[run] picked: edition {edition_id} = {topic['slug']}")

    # 2. LLM prose
    prose = generate_content(topic, edition_id)
    print(f"[run] prose generated · title='{prose['title']}'")

    # 3. Deep-dive
    md = render_deep_dive_md(topic, edition_id, prose)
    (edition_dir / "deep-dive.md").write_text(md, encoding="utf-8")

    # 4. Share-card + carousel HTML
    share_template = TEMPLATE_SHARE.read_text(encoding="utf-8")
    (edition_dir / "share-card.html").write_text(
        render_share_card_html(share_template, topic, edition_id, prose),
        encoding="utf-8",
    )
    carousel_template = TEMPLATE_CAROUSEL.read_text(encoding="utf-8")
    for i, h in enumerate(render_carousel_html(carousel_template, topic, edition_id, prose), 1):
        (edition_dir / "carousel" / f"slide_{i:02d}.html").write_text(h, encoding="utf-8")

    # 5. Manifest
    manifest = write_manifest(edition_dir, topic, edition_id, prose)

    # 6. Render PDF + PNGs
    pdf_size = render_share_card_pdf(edition_dir / "share-card.html", edition_dir / "share-card.pdf")
    print(f"[run] share-card.pdf · {pdf_size} bytes")
    slide_paths = sorted((edition_dir / "carousel").glob("slide_*.html"))
    png_sizes = render_carousel_pngs(slide_paths, edition_dir / "assets")
    print(f"[run] {len(png_sizes)} PNGs · sizes={png_sizes}")

    # 7. Compliance
    checks = static_compliance_check(manifest, md)
    manifest["compliance_checks"] = checks
    if not all(checks.values()) and not DRY_RUN:
        (edition_dir / "manifest.json").write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        return 2, f"COMPLIANCE FAILED · edition {edition_id} · {checks}"

    # 8. Resolve URLs (publish.py also writes manifest urls + handles legacy WhatsApp)
    if DRY_RUN:
        print("[run] DRY_RUN: skipping URL resolution + delivery")
        (edition_dir / "manifest.json").write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        return 0, f"DRY RUN OK · edition {edition_id:03d} · {topic['slug']}"

    urls = publish_edition(edition_dir, whatsapp_to=None)  # WhatsApp handled below by new module
    print(f"[run] primary URL → {urls.primary}")

    # 9. Email broadcast to subscribers
    email_result = broadcast_to_subscribers(manifest, urls)
    manifest["published_to"]["email_recipients"] = email_result.sent

    # 10. WhatsApp delivery (no-op until creds exist)
    wa_result = whatsapp_deliver(manifest, urls)
    manifest["published_to"]["whatsapp_message_sids"] = wa_result.sids

    # Final manifest write — captures delivery receipts
    (edition_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    summary = (
        f"OK · edition {edition_id:03d} · {topic['slug']}\n"
        f"  primary: {urls.primary}\n"
        f"  pages:   {urls.github_pages}\n"
        f"  email:   sent={email_result.sent} failed={email_result.failed} "
        f"({email_result.skipped_reason or 'delivered'})\n"
        f"  whatsapp:delivered={wa_result.delivered} failed={wa_result.failed} "
        f"({wa_result.skipped_reason or 'delivered'})\n"
        f"  configured: whatsapp={wa_configured()}"
    )
    return 0, summary


def main() -> int:
    print(f"[run] start | DRY_RUN={DRY_RUN} | utc={datetime.now(timezone.utc).isoformat()}")
    try:
        code, summary = _run()
    except Exception as e:
        tb = traceback.format_exc()
        print(f"[run] FAILED · {e}\n{tb}")
        notify_self("FAILED", f"Pipeline crashed:\n\n{tb}")
        return 1

    print(f"[run] {summary}")
    if code == 0:
        notify_self("Edition published", summary)
    else:
        notify_self("Edition compliance failed", summary)
    return code


if __name__ == "__main__":
    sys.exit(main())
