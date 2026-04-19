"""
Delivery layer: WhatsApp (Twilio), Substack, Instagram.

All functions here follow the failure-isolation rule from PIPELINE_SPEC.md section 8:
- Website-related failures degrade silently and fall back to GitHub URLs.
- Delivery failures retry-then-queue-for-next-run; they never abort the edition.
- Only the canonical git push (in commit.py) is allowed to be fatal.
"""
from __future__ import annotations
import time
import requests
from typing import Optional
from . import config


# Deep-dive URL resolver: tries the branded site, falls back to GitHub blob.
def resolve_deep_dive_url(edition_id: str, slug: str, timeout: float = 5.0) -> str:
    """HEAD-check the branded URL. Fall back to GitHub blob if non-200."""
    branded = config.site_deep_dive_url(edition_id, slug)
    try:
        r = requests.head(branded, timeout=timeout, allow_redirects=True)
        if r.status_code == 200:
            return branded
    except requests.RequestException:
        pass
    # Fallback - always works because git push already succeeded
    return config.github_blob_url(edition_id, slug, "deep-dive.md")


# GitHub-raw propagation wait: after a push, the raw URL takes a few seconds
# to become fetchable by Twilio's media fetcher.
def wait_for_raw_availability(
    edition_id: str, slug: str, filename: str = "share-card.pdf",
    attempts: int = 3, backoff_seconds: int = 10,
) -> bool:
    url = config.raw_github_url(edition_id, slug, filename)
    for i in range(attempts):
        try:
            r = requests.head(url, timeout=10, allow_redirects=True)
            if r.status_code == 200:
                return True
        except requests.RequestException:
            pass
        if i < attempts - 1:
            time.sleep(backoff_seconds * (i + 1))
    return False


# WhatsApp send via Twilio. Retry up to 3x with exponential backoff.
# Returns (ok, sid_or_error).
def send_whatsapp(
    edition_id: str, slug: str, topic: str, anchor_line: str,
) -> tuple[bool, str]:
    deep_dive_url = resolve_deep_dive_url(edition_id, slug)
    media_url     = config.raw_github_url(edition_id, slug, "share-card.pdf")

    body = (
        f"Edition {edition_id}: {topic}.\n"
        f"Deep-dive: {deep_dive_url}\n"
        f"Memory anchor: \"{anchor_line}\""
    )

    endpoint = (
        f"https://api.twilio.com/2010-04-01/Accounts/"
        f"{config.TWILIO_ACCOUNT_SID}/Messages.json"
    )
    payload = {
        "From":     config.TWILIO_FROM_WHATSAPP,
        "To":       config.ARUN_WHATSAPP,
        "Body":     body,
        "MediaUrl": media_url,
    }
    auth = (config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN)

    for attempt in range(3):
        try:
            r = requests.post(endpoint, auth=auth, data=payload, timeout=30)
            if r.status_code in (200, 201):
                return True, r.json().get("sid", "")
            err = f"HTTP {r.status_code}: {r.text[:200]}"
        except requests.RequestException as e:
            err = str(e)
        if attempt < 2:
            time.sleep(10 * (2 ** attempt))   # 10s, 30s, 60s
    return False, err  # type: ignore[return-value]


# Stubs - implement when wiring Substack + Buffer/Meta.
def post_to_substack(edition_id: str, slug: str) -> tuple[bool, str]:
    # TODO: call Substack API with deep-dive.md body + embedded share-card.
    # On failure -> queue file in content/pending_substack/<edition_id>.yaml
    return False, "not_implemented"


def schedule_instagram(edition_id: str, slug: str) -> tuple[bool, str]:
    # TODO: call Buffer/Meta API with 4 PNGs from assets/<edition_id>/.
    # On failure -> queue in content/pending_ig/<edition_id>/
    return False, "not_implemented"
