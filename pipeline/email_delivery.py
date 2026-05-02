"""Email delivery for The Nutrient Brief.

Two modes:
    1. broadcast_to_subscribers(manifest, urls)  — send the daily edition to data/subscribers.json
    2. notify_self(subject, body)                — admin alert on success/failure

Default backend: Gmail SMTP (free, ~500/day on personal Gmail). The class is
designed so a future swap to Resend/Buttondown/MailerLite is one method,
not a rewrite.

Secrets read from env (GitHub Secrets in CI):
    EMAIL_FROM            — sender address (your Gmail)
    EMAIL_APP_PASSWORD    — Gmail App Password (2FA required, 16-char string)
    EMAIL_TO_SELF         — where to send admin alerts (usually = EMAIL_FROM)

If creds are missing, every call becomes a no-op + log line. Pipeline never crashes
just because email isn't configured yet.
"""
from __future__ import annotations

import json
import os
import smtplib
import ssl
from dataclasses import dataclass
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate, make_msgid
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).parent.parent
SUBSCRIBERS_PATH = REPO_ROOT / "data" / "subscribers.json"

GMAIL_HOST = "smtp.gmail.com"
GMAIL_PORT = 465  # SSL


@dataclass
class EmailResult:
    sent: int
    failed: int
    skipped_reason: Optional[str] = None


# ============== SMTP backend ==============
def _smtp_send(
    from_addr: str,
    app_password: str,
    to_addrs: list[str],
    subject: str,
    html_body: str,
    text_body: Optional[str] = None,
    bcc: bool = True,
) -> tuple[int, int]:
    """Returns (sent_count, failed_count). Uses BCC for broadcasts to protect privacy."""
    if not to_addrs:
        return 0, 0

    msg = MIMEMultipart("alternative")
    msg["From"] = f"The Nutrient Brief <{from_addr}>"
    msg["Subject"] = subject
    msg["Date"] = formatdate(localtime=False)
    msg["Message-ID"] = make_msgid(domain="nutrientbrief.in")
    if bcc:
        msg["To"] = from_addr            # primary header is sender; recipients are envelope-only
    else:
        msg["To"] = ", ".join(to_addrs)

    if text_body:
        msg.attach(MIMEText(text_body, "plain", "utf-8"))
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    sent = 0
    failed = 0
    ctx = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL(GMAIL_HOST, GMAIL_PORT, context=ctx, timeout=30) as srv:
            srv.login(from_addr, app_password)
            # Single SMTP call: envelope_to includes ALL recipients (Gmail handles BCC fan-out)
            try:
                srv.sendmail(from_addr, to_addrs, msg.as_string())
                sent = len(to_addrs)
            except smtplib.SMTPRecipientsRefused as e:
                # Some recipients refused; fall back to per-addr send
                for addr in to_addrs:
                    try:
                        srv.sendmail(from_addr, [addr], msg.as_string())
                        sent += 1
                    except Exception:
                        failed += 1
    except Exception as e:
        print(f"[email] SMTP error: {e}")
        return 0, len(to_addrs)
    return sent, failed


# ============== HTML rendering ==============
def render_broadcast_html(manifest: dict, urls) -> tuple[str, str]:
    """Returns (html_body, plain_body). urls is a publish.EditionURLs dataclass."""
    accent = manifest.get("accent_color", "#c7462d")
    edition_id = manifest["edition_id"]
    eyebrow = manifest["eyebrow_label"]
    title = manifest["title"]
    anchor = manifest["memory_anchor"]
    primary_url = urls.primary
    pages_url = urls.github_pages
    pdf_url = urls.share_card_pdf_raw

    html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#faf7f2;font-family:Georgia,'Times New Roman',serif;color:#141623">
<table width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#faf7f2">
  <tr><td align="center" style="padding:32px 16px">
    <table width="560" cellpadding="0" cellspacing="0" border="0" style="max-width:560px;background:#ffffff;border:1px solid #e5e1d8;border-radius:4px">
      <tr><td style="padding:32px 36px 8px">
        <div style="font-family:system-ui,-apple-system,sans-serif;font-size:11px;letter-spacing:2.2px;color:{accent};text-transform:uppercase;font-weight:700;margin-bottom:8px">
          The Nutrient Brief · Edition {edition_id}
        </div>
        <div style="font-family:system-ui,-apple-system,sans-serif;font-size:11px;letter-spacing:2px;color:#5a5d6a;text-transform:uppercase;margin-bottom:18px">
          {eyebrow}
        </div>
        <h1 style="margin:0 0 16px;font-size:28px;line-height:1.18;letter-spacing:-0.4px;font-weight:700">{title}</h1>
        <blockquote style="margin:18px 0 22px;padding:14px 18px;border-left:3px solid {accent};background:#faf7f2;font-style:italic;color:#3a3d4a;font-size:16px;line-height:1.5">
          "{anchor}"
        </blockquote>
        <p style="margin:24px 0 8px;font-size:15px;line-height:1.55;color:#3a3d4a">
          The 3-minute deep-dive — mechanism, the evidence, who tends to benefit, who should think twice — is on the site:
        </p>
        <p style="margin:14px 0 28px">
          <a href="{primary_url}" style="display:inline-block;background:{accent};color:#ffffff;text-decoration:none;padding:12px 22px;border-radius:4px;font-family:system-ui,-apple-system,sans-serif;font-size:14px;letter-spacing:0.4px;font-weight:600">
            Read full deep-dive →
          </a>
        </p>
        <p style="margin:0 0 6px;font-size:12px;color:#5a5d6a">
          Always-up backup link: <a href="{pages_url}" style="color:{accent}">{pages_url}</a>
        </p>
        <p style="margin:6px 0 0;font-size:12px;color:#5a5d6a">
          Prefer a printable card? <a href="{pdf_url}" style="color:{accent}">PDF version</a>
        </p>
      </td></tr>
      <tr><td style="padding:18px 36px 28px;border-top:1px solid #e5e1d8;font-family:system-ui,-apple-system,sans-serif;font-size:11px;color:#5a5d6a;line-height:1.6">
        <em>Not medical advice. Educational content only. Not intended to diagnose, treat, cure, or prevent any disease.
        Consult a qualified medical professional before starting, changing, or stopping any supplement.</em>
        <br><br>
        You're receiving this because you subscribed to The Nutrient Brief. Reply with "unsubscribe" to be removed.
      </td></tr>
    </table>
  </td></tr>
</table>
</body></html>"""

    plain = f"""The Nutrient Brief · Edition {edition_id}
{eyebrow}

{title}

"{anchor}"

Read full deep-dive (3 min): {primary_url}
Always-up backup: {pages_url}
PDF: {pdf_url}

Not medical advice. Educational content only. Reply with "unsubscribe" to be removed.
"""
    return html, plain


# ============== Public API ==============
def _load_subscribers() -> list[str]:
    if not SUBSCRIBERS_PATH.exists():
        return []
    data = json.loads(SUBSCRIBERS_PATH.read_text(encoding="utf-8"))
    return [s["email"] for s in data.get("subscribers", [])
            if s.get("status", "active") == "active"]


def _creds() -> tuple[Optional[str], Optional[str], Optional[str]]:
    return (
        os.environ.get("EMAIL_FROM"),
        os.environ.get("EMAIL_APP_PASSWORD"),
        os.environ.get("EMAIL_TO_SELF"),
    )


def broadcast_to_subscribers(manifest: dict, urls) -> EmailResult:
    """Send the daily edition to every active subscriber. BCC for privacy."""
    sender, pw, _ = _creds()
    if not (sender and pw):
        print("[email] EMAIL_FROM / EMAIL_APP_PASSWORD missing — skipping broadcast")
        return EmailResult(0, 0, "credentials_missing")

    subs = _load_subscribers()
    if not subs:
        print("[email] no active subscribers — skipping broadcast")
        return EmailResult(0, 0, "no_subscribers")

    subject = f"Edition {manifest['edition_id']} — {manifest['title']}"
    html, text = render_broadcast_html(manifest, urls)
    sent, failed = _smtp_send(sender, pw, subs, subject, html, text, bcc=True)
    print(f"[email] broadcast · sent={sent} failed={failed} (of {len(subs)} subs)")
    return EmailResult(sent, failed)


def notify_self(subject: str, body: str, html: bool = False) -> EmailResult:
    """Admin notification — used for run success/failure pings."""
    sender, pw, to_self = _creds()
    if not (sender and pw and to_self):
        print(f"[email] self-notify skipped (creds missing) · {subject}")
        return EmailResult(0, 0, "credentials_missing")

    full_subject = f"[The Nutrient Brief] {subject}"
    if html:
        html_body = body
        text_body = None
    else:
        html_body = f"<pre style='font-family:monospace;font-size:13px'>{body}</pre>"
        text_body = body

    sent, failed = _smtp_send(sender, pw, [to_self], full_subject, html_body, text_body, bcc=False)
    return EmailResult(sent, failed)


if __name__ == "__main__":
    # Quick smoke test
    print("Subscribers:", _load_subscribers())
    print("Has creds:", all(_creds()[:2]))
