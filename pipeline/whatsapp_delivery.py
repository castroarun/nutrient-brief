"""WhatsApp delivery for The Nutrient Brief.

Backend: Meta WhatsApp Business Cloud API (free tier: 1000 service conversations/month).
This module is built so that the day you finish WABA approval, you just paste 4 secrets
into GitHub and the next cron run starts delivering — no code change.

Until creds exist, every call is a clean no-op + log line. The pipeline never
fails just because WhatsApp isn't wired yet.

Secrets (env / GitHub Secrets):
    WHATSAPP_TOKEN              — long-lived access token from Meta Business Suite
    WHATSAPP_PHONE_NUMBER_ID    — the phone number ID Meta assigns
    WHATSAPP_TO                 — comma-separated E.164 numbers (e.g. "+91987...,+91876...")
    WHATSAPP_BROADCAST_LIST     — optional: name of a Meta WABA broadcast list (later)

Setup path (when ready, ~2 hours):
    1. Create Meta Business account → developers.facebook.com
    2. Create a WhatsApp Business app → add "WhatsApp" product
    3. Add a phone number (test number is free, real number needs Meta verification)
    4. Generate a long-lived access token (System User → permanent)
    5. Paste the 4 secrets above into github.com/.../settings/secrets/actions
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

WABA_VERSION = "v20.0"


@dataclass
class WhatsAppResult:
    delivered: int
    failed: int
    sids: list[str]
    skipped_reason: Optional[str] = None


def _creds() -> tuple[Optional[str], Optional[str], list[str]]:
    token = os.environ.get("WHATSAPP_TOKEN")
    phone_id = os.environ.get("WHATSAPP_PHONE_NUMBER_ID")
    to_raw = os.environ.get("WHATSAPP_TO", "")
    to_list = [n.strip() for n in to_raw.split(",") if n.strip()]
    return token, phone_id, to_list


def build_message_body(manifest: dict, urls) -> str:
    """Markdown-style WhatsApp body. Carries primary URL + always-up Pages URL."""
    title = manifest["title"]
    anchor = manifest["memory_anchor"]
    eyebrow = manifest["eyebrow_label"]
    edition_id = manifest["edition_id"]

    lines = [
        f"*The Nutrient Brief · Edition {edition_id}*",
        f"_{eyebrow}_",
        "",
        f"*{title}*",
        "",
        f"_{anchor}_",
        "",
        f"Read (3 min): {urls.primary}",
    ]
    if urls.primary != urls.github_pages:
        lines.append(f"Always-up link: {urls.github_pages}")
    lines += [
        "",
        "_Not medical advice. Educational content only._",
    ]
    return "\n".join(lines)


def _send_one(token: str, phone_id: str, to: str, body: str, timeout: float = 10.0) -> Optional[str]:
    """Send to a single E.164 number. Returns Meta message ID on success, None on fail."""
    url = f"https://graph.facebook.com/{WABA_VERSION}/{phone_id}/messages"
    payload = json.dumps({
        "messaging_product": "whatsapp",
        "to": to.lstrip("+"),  # Meta accepts with or without +
        "type": "text",
        "text": {"body": body, "preview_url": True},
    }).encode("utf-8")
    req = Request(
        url, data=payload, method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            sid = data.get("messages", [{}])[0].get("id")
            return sid
    except HTTPError as e:
        err_body = e.read().decode("utf-8", errors="ignore")[:300]
        print(f"[whatsapp] HTTP {e.code} for {to}: {err_body}")
        return None
    except (URLError, TimeoutError) as e:
        print(f"[whatsapp] network error for {to}: {e}")
        return None


def deliver(manifest: dict, urls) -> WhatsAppResult:
    """Send the daily edition to every recipient in WHATSAPP_TO. No-op if creds missing."""
    token, phone_id, to_list = _creds()
    if not (token and phone_id):
        print("[whatsapp] WHATSAPP_TOKEN / WHATSAPP_PHONE_NUMBER_ID missing — skipping (degraded)")
        return WhatsAppResult(0, 0, [], "credentials_missing")
    if not to_list:
        print("[whatsapp] WHATSAPP_TO is empty — skipping")
        return WhatsAppResult(0, 0, [], "no_recipients")

    body = build_message_body(manifest, urls)
    delivered, failed, sids = 0, 0, []
    for recipient in to_list:
        sid = _send_one(token, phone_id, recipient, body)
        if sid:
            delivered += 1
            sids.append(sid)
            print(f"[whatsapp] delivered to {recipient} · sid={sid}")
        else:
            failed += 1
    return WhatsAppResult(delivered, failed, sids)


def is_configured() -> bool:
    token, phone_id, to_list = _creds()
    return bool(token and phone_id and to_list)


if __name__ == "__main__":
    print("WhatsApp configured:", is_configured())
    if is_configured():
        token, phone_id, to_list = _creds()
        print(f"  token: {'*' * 8}{token[-4:] if token else ''}")
        print(f"  phone_id: {phone_id}")
        print(f"  recipients: {to_list}")
