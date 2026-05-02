# Delivery Setup — Email + WhatsApp

Two delivery channels feed each edition. Email is **needed for launch**.
WhatsApp is **infrastructure-ready** — drop in 4 secrets when you have a
Meta WABA account, no code change needed.

All secrets live at:
**https://github.com/castroarun/nutrient-brief/settings/secrets/actions**

---

## 1. Email (Gmail SMTP — free, do this today)

### One-time Gmail setup (5 min)

1. Make sure 2-Step Verification is on for your Google account
   → https://myaccount.google.com/security
2. Create an App Password specifically for this pipeline
   → https://myaccount.google.com/apppasswords
   - Select app: "Mail"
   - Select device: "Other (Custom name)" → name it `nutrient-brief-bot`
   - Copy the 16-character password Google shows you (looks like `abcd efgh ijkl mnop`).
     **You only see it once. Save immediately.**

### GitHub Secrets to add (3 secrets)

Open the secrets page above, click **New repository secret** for each:

| Name                  | Value                                                   |
|-----------------------|---------------------------------------------------------|
| `EMAIL_FROM`          | `arun.castromin@gmail.com`                              |
| `EMAIL_APP_PASSWORD`  | The 16-char app password from step 2 (no spaces needed) |
| `EMAIL_TO_SELF`       | `arun.castromin@gmail.com` (where admin alerts go)      |

That's it. The very next cron run will:
- Email the new edition to everyone in `data/subscribers.json`
- Email you a one-line success or failure summary

### Adding subscribers

Edit `data/subscribers.json`, append a new object:

```json
{
  "email": "newperson@example.com",
  "name": "First Last",
  "joined_at": "2026-05-02",
  "status": "active",
  "source": "twitter"
}
```

Commit + push. Next cron run picks it up automatically. No re-deploy.

To unsubscribe someone, set their `status` to `"unsubscribed"` (don't delete —
preserves history).

### Volume limits

Personal Gmail allows ~500 outbound emails/day. At our publication cadence
(1 edition/day × N subscribers), that means up to ~500 subscribers on Gmail
SMTP. When you outgrow it, swap to Resend (free 3000/month) or MailerLite
(free 12,000/month for ≤1000 subs) by replacing one function in
`pipeline/email_delivery.py`.

---

## 2. WhatsApp (Meta WABA — do later, infra ready)

The code is in place (`pipeline/whatsapp_delivery.py`). Until secrets exist,
it logs a one-line "skipped — credentials missing" and the rest of the
pipeline continues.

### When you're ready (~2 hour setup)

1. **Create a Meta Business account**
   → https://business.facebook.com
2. **Create a WhatsApp Business app**
   → https://developers.facebook.com → My Apps → Create App → Business
   → Add the "WhatsApp" product
3. **Add a phone number**
   - Test number is free (limited to 5 recipients)
   - Real number requires Meta verification + business profile
4. **Generate a long-lived access token**
   - Meta dashboard → System Users → Add → assign WABA permissions
   - Token from System User is permanent (the temporary 24h one in the
     setup wizard is *not* what you want)
5. **Add 3 secrets to GitHub**

| Name                       | Value                                                  |
|----------------------------|--------------------------------------------------------|
| `WHATSAPP_TOKEN`           | Long-lived access token from System User               |
| `WHATSAPP_PHONE_NUMBER_ID` | The number's ID (NOT the phone number itself)          |
| `WHATSAPP_TO`              | Comma-separated E.164 numbers, e.g. `+919876543210`    |

Next cron run starts delivering. Same body format as the email; same
mechanism-first voice; carries primary URL + always-up Pages URL.

### Free tier

Meta gives you **1000 service conversations/month free** on WABA. A
"conversation" is a 24h window with one recipient, so 1000/month easily
covers a 100-recipient broadcast list publishing daily.

---

## 3. Verifying it all works

After you add the email secrets:

1. Go to: https://github.com/castroarun/nutrient-brief/actions
2. Click `daily-edition` → **Run workflow** → leave `dry_run` as `false`
3. Wait ~3 minutes
4. Check your Gmail inbox for:
   - The Edition 002 email (sent to subscribers list)
   - The `[The Nutrient Brief] Edition published` admin email

If both arrive, you're live. The 5 AM IST cron takes over from there.

---

## Channel summary

| Channel       | Status              | Cost       | Setup time |
|---------------|---------------------|------------|------------|
| GitHub Pages  | Live (after step 1 of `_ship_edition_001.ps1`) | ₹0 forever | done |
| Email (Gmail) | Ready to activate   | ₹0 (≤500/day)  | 5 min |
| WhatsApp      | Code in, awaiting secrets | ₹0 (≤1000 conv/month) | 2 hours when ready |
| Substack      | Not yet wired       | ₹0          | future phase |
| Instagram     | PNGs render, posting not yet wired | ₹0 | future phase |
