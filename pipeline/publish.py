"""URL-resolution + manifest-update layer for The Nutrient Brief.

Delivery to channels (email, WhatsApp) is handled by separate modules
(`email_delivery.py`, `whatsapp_delivery.py`) — this module's only job is to
figure out which URLs are reachable right now and stamp them into the manifest.

Graceful degradation (§8 of PIPELINE_SPEC.md):
  Tier 1  branded site   https://nutrientbrief.in/editions/NNN-slug
  Tier 2  GitHub Pages   https://castroarun.github.io/nutrient-brief/...
  Tier 3  GitHub blob    https://github.com/castroarun/nutrient-brief/...

Tier 2 is always available because the repo push triggers a Pages redeploy —
editions are live at a predictable URL within ~60s of commit.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from urllib.error import URLError
from urllib.request import Request, urlopen

REPO = "castroarun/nutrient-brief"
BRANDED_HOST = "nutrientbrief.in"
PAGES_HOST = "castroarun.github.io"


@dataclass
class EditionURLs:
    """Full URL set for a published edition. Callers pick which to share."""
    branded_site: str          # Tier 1 (may be offline)
    github_pages: str          # Tier 2 (always up after push)
    github_blob_md: str        # Tier 3 (raw deep-dive markdown view)
    share_card_pdf_raw: str    # Direct PDF download
    primary: str               # Best URL we could verify right now


def _edition_folder(edition_id: str, slug: str) -> str:
    """Canonical folder name: 001_magnesium-glycinate"""
    return f"{edition_id}_{slug}"


def _is_reachable(url: str, timeout: float = 3.0) -> bool:
    try:
        req = Request(url, method="HEAD")
        with urlopen(req, timeout=timeout) as resp:
            return 200 <= resp.status < 400
    except (URLError, TimeoutError, Exception):
        return False


def resolve_urls(edition_id: str, slug: str) -> EditionURLs:
    """Build the full URL set; pick best currently-reachable as primary."""
    folder = _edition_folder(edition_id, slug)
    branded = f"https://{BRANDED_HOST}/editions/{edition_id}-{slug}"
    pages = f"https://{PAGES_HOST}/nutrient-brief/content/editions/{folder}/share-card.html"
    blob_md = f"https://github.com/{REPO}/blob/main/content/editions/{folder}/deep-dive.md"
    pdf_raw = f"https://raw.githubusercontent.com/{REPO}/main/content/editions/{folder}/share-card.pdf"

    if _is_reachable(branded):
        primary = branded
    elif _is_reachable(pages):
        primary = pages
    else:
        primary = blob_md

    return EditionURLs(
        branded_site=branded,
        github_pages=pages,
        github_blob_md=blob_md,
        share_card_pdf_raw=pdf_raw,
        primary=primary,
    )


def update_manifest_urls(manifest_path: Path, urls: EditionURLs) -> None:
    """Stamp resolved URLs into manifest.json (preserving everything else)."""
    m = json.loads(manifest_path.read_text(encoding="utf-8"))
    m["urls"] = {
        "site": urls.branded_site,
        "github_pages": urls.github_pages,
        "github_blob": urls.github_blob_md,
        "share_card_pdf_raw": urls.share_card_pdf_raw,
        "primary_resolved": urls.primary,
    }
    m.setdefault("published_to", {})
    m["published_to"]["github_pages"] = urls.github_pages
    manifest_path.write_text(json.dumps(m, indent=2, ensure_ascii=False), encoding="utf-8")


def publish_edition(edition_dir: Path, whatsapp_to: Optional[str] = None) -> EditionURLs:
    """Entry point used by run_edition.py. Resolves URLs and updates manifest.

    The `whatsapp_to` arg is kept for backwards compatibility with older callers
    but is intentionally ignored — WhatsApp is now handled by whatsapp_delivery.py.
    """
    manifest_path = edition_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    urls = resolve_urls(manifest["edition_id"], manifest["slug"])
    print(f"[publish] primary URL → {urls.primary}")
    update_manifest_urls(manifest_path, urls)
    print(f"[publish] manifest updated · {manifest_path}")
    return urls


if __name__ == "__main__":
    import sys
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("content/editions/001_magnesium-glycinate")
    publish_edition(target)
