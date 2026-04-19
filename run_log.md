# Run log

One line per pipeline run. Appended by `pipeline/run_edition.py`.

**Format:**

```
YYYY-MM-DD HH:MM IST | Edition NNN | slug | <status> | wa:<status> | site:<status> | subs:<status> | ig:<status>
```

**Status values:**

- `published` — all steps succeeded
- `published_degraded` — canonical (git) succeeded, >=1 delivery channel degraded; next run proceeds normally
- `halted` — canonical step failed; edition held in `content/drafts/pending_review/`; future runs paused until ack

---

*(no runs yet)*
