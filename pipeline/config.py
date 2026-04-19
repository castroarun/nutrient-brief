"""
Shared config + .env loader for the pipeline.

Reads credentials from the .env file that lives OUTSIDE the repo (so it can't
be committed even accidentally). Default location is
`<workspace>/projects/project_13_nutrition_titbit/.env`, but override with
`NB_ENV_PATH` environment variable.
"""
from __future__ import annotations
import os
from pathlib import Path
from dotenv import load_dotenv


# Resolve .env location
_default_env = Path.home() / ".nutrient-brief" / ".env"
_env_path = Path(os.environ.get("NB_ENV_PATH", _default_env))

if _env_path.is_file():
    load_dotenv(_env_path)
else:
    # Fall back to repo-local .env (dev only)
    repo_env = Path(__file__).resolve().parents[1] / ".env"
    if repo_env.is_file():
        load_dotenv(repo_env)


def require(name: str) -> str:
    val = os.environ.get(name)
    if not val:
        raise RuntimeError(
            f"Missing required env var: {name}. "
            f"Set it in {_env_path} or via NB_ENV_PATH."
        )
    return val


# --- Twilio ---
TWILIO_ACCOUNT_SID  = require("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN   = require("TWILIO_AUTH_TOKEN")
TWILIO_FROM_WHATSAPP = require("TWILIO_FROM_WHATSAPP")
ARUN_WHATSAPP       = require("ARUN_WHATSAPP")

# --- Repo / site ---
GITHUB_USER = os.environ.get("GITHUB_USER", "castroarun")
GITHUB_REPO = os.environ.get("GITHUB_REPO", "nutrient-brief")
SITE_BASE_URL = os.environ.get("SITE_BASE_URL", "https://nutrientbrief.in")

# --- Derived URLs ---
def raw_github_url(edition_id: str, slug: str, filename: str) -> str:
    return (
        f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/main/"
        f"content/editions/{edition_id}_{slug}/{filename}"
    )


def github_blob_url(edition_id: str, slug: str, filename: str) -> str:
    return (
        f"https://github.com/{GITHUB_USER}/{GITHUB_REPO}/blob/main/"
        f"content/editions/{edition_id}_{slug}/{filename}"
    )


def site_deep_dive_url(edition_id: str, slug: str) -> str:
    return f"{SITE_BASE_URL}/editions/{edition_id}-{slug}"
