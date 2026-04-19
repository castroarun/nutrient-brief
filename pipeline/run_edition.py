"""
run_edition.py - entry point for the daily pipeline.

Invoked by the scheduled task at 05:00 IST. Reads topic_backlog.md +
trending_report.md, picks a topic per TOPIC_SELECTION.md rules, generates
the three artifacts, compliance-checks, commits + pushes, fires delivery.

Failure tiers (see PIPELINE_SPEC.md section 8):
- Fatal     -> abort, log halted, halt future runs until ack
- Degraded  -> log degraded, continue next run
"""
from __future__ import annotations
import sys
import datetime as dt
from pathlib import Path
from . import publish


REPO_ROOT   = Path(__file__).resolve().parents[1]
RUN_LOG     = REPO_ROOT / "run_log.md"
PENDING_DIR = REPO_ROOT / "content" / "drafts" / "pending_review"


# Placeholders - each returns True/False for success and raises on fatal.
def pick_topic() -> dict:
    """Read topic_backlog + trending_report, return the selected topic dict."""
    # TODO: implement selection per TOPIC_SELECTION.md sections 2-4
    raise NotImplementedError("pick_topic")


def generate_artifacts(topic: dict) -> dict:
    """Produce deep-dive.md, share-card.html, carousel slides.
    Returns paths dict. Raises on generation failure (fatal).
    """
    # TODO: call Claude via anthropic SDK with editorial_framework + spec as system prompt.
    raise NotImplementedError("generate_artifacts")


def compliance_check(paths: dict) -> list[str]:
    """Return list of compliance violations. Empty list = pass."""
    # TODO: run checks from PIPELINE_SPEC.md section 6
    return []


def render_share_card_pdf(paths: dict) -> Path:
    """HTML -> PDF via playwright or weasyprint. Writes share-card.pdf."""
    # TODO: implement
    raise NotImplementedError("render_share_card_pdf")


def render_carousel_pngs(paths: dict) -> list[Path]:
    """Each carousel slide HTML -> 1080x1350 PNG."""
    # TODO: implement
    return []


def git_commit_and_push(edition_id: str, slug: str) -> None:
    """Canonical publish step. Raises on failure (fatal tier)."""
    # TODO: GitPython: add content/editions/NNN_slug/, commit, push origin main.
    raise NotImplementedError("git_commit_and_push")


# Run-log appenders
def _log_line(line: str) -> None:
    RUN_LOG.parent.mkdir(parents=True, exist_ok=True)
    with RUN_LOG.open("a", encoding="utf-8") as f:
        f.write(line.rstrip() + "\n")


def log_success(edition_id: str, slug: str, marks: dict) -> None:
    ts = dt.datetime.now().strftime("%Y-%m-%d %H:%M IST")
    flag = "published_degraded" if marks.get("degraded") else "published"
    parts = [
        ts, f"Edition {edition_id}", slug, flag,
        f"wa:{marks.get('wa', '?')}",
        f"site:{marks.get('site', '?')}",
        f"subs:{marks.get('subs', '?')}",
        f"ig:{marks.get('ig', '?')}",
    ]
    _log_line(" | ".join(parts))


def log_halt(edition_id: str, slug: str, reason: str) -> None:
    ts = dt.datetime.now().strftime("%Y-%m-%d %H:%M IST")
    _log_line(f"{ts} | Edition {edition_id} | {slug or '-'} | halted | reason: {reason} | held:pending_review/")


def main() -> int:
    topic = {"id": "???", "slug": "???"}
    try:
        topic = pick_topic()                         # fatal if this fails
        paths = generate_artifacts(topic)            # fatal
        violations = compliance_check(paths)
        if violations:
            # Hold, don't publish. Fatal to run.
            log_halt(topic["id"], topic["slug"], f"compliance:{','.join(violations)}")
            return 1


        render_share_card_pdf(paths)                 # fatal if renderer breaks
        render_carousel_pngs(paths)                  # degraded only (IG can retry)
        git_commit_and_push(topic["id"], topic["slug"])  # fatal - canonical publish
    except Exception as e:
        log_halt(topic.get("id", "???"), topic.get("slug", "???"), f"{type(e).__name__}: {e}")
        return 2

    # From here on, every failure is degraded, not fatal.
    marks: dict = {}

    # Wait for GitHub raw propagation (needed by Twilio media fetch).
    raw_ok = publish.wait_for_raw_availability(topic["id"], topic["slug"])
    marks["site"] = "push:ok" if raw_ok else "raw:pending(degraded)"

    # WhatsApp: retry-and-forget
    ok, info = publish.send_whatsapp(
        topic["id"], topic["slug"], topic.get("title", topic["slug"]),
        topic.get("anchor_line", ""),
    )
    marks["wa"] = f"sent:{info}" if ok else f"failed:{info}"
    if not ok:
        marks["degraded"] = True


    # Substack + IG - queue on failure
    subs_ok, _ = publish.post_to_substack(topic["id"], topic["slug"])
    marks["subs"] = "published" if subs_ok else "queued"
    if not subs_ok:
        marks["degraded"] = True

    ig_ok, _ = publish.schedule_instagram(topic["id"], topic["slug"])
    marks["ig"] = "queued:09:00" if ig_ok else "stalled"
    if not ig_ok:
        marks["degraded"] = True

    log_success(topic["id"], topic["slug"], marks)
    return 0


if __name__ == "__main__":
    sys.exit(main())
