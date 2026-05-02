"""Free LLM client for The Nutrient Brief.

Default backend: GitHub Models (free, OpenAI-compatible, auth via GITHUB_TOKEN
already present in our Actions runner — no extra secret needed).

Optional fallback: Google Gemini free tier via GEMINI_API_KEY.

Usage:
    client = LLMClient()                     # auto-pick backend
    text = client.complete(system="...", user="...", max_tokens=1200)
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

GH_MODELS_URL = "https://models.inference.ai.azure.com/chat/completions"
GH_MODELS_DEFAULT = "gpt-4o-mini"   # cheapest/fastest free tier; quality is plenty for editorial drafts

GEMINI_URL_TMPL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "{model}:generateContent?key={key}"
)
GEMINI_DEFAULT = "gemini-1.5-flash"


@dataclass
class LLMResponse:
    text: str
    backend: str
    model: str
    tokens_in: Optional[int] = None
    tokens_out: Optional[int] = None


class LLMClient:
    """Single client, picks backend based on env at construction time."""

    def __init__(self, prefer: str = "auto"):
        # prefer: "auto" | "github" | "gemini"
        self.gh_token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_MODELS_TOKEN")
        self.gemini_key = os.environ.get("GEMINI_API_KEY")

        if prefer == "github" and not self.gh_token:
            raise RuntimeError("GITHUB_TOKEN not set; cannot use GitHub Models")
        if prefer == "gemini" and not self.gemini_key:
            raise RuntimeError("GEMINI_API_KEY not set; cannot use Gemini")

        if prefer == "github" or (prefer == "auto" and self.gh_token):
            self.backend = "github"
        elif self.gemini_key:
            self.backend = "gemini"
        else:
            raise RuntimeError(
                "No free LLM credentials found. Set GITHUB_TOKEN (preferred) "
                "or GEMINI_API_KEY in env."
            )

    # --------------- public API ---------------
    def complete(
        self,
        system: str,
        user: str,
        max_tokens: int = 1500,
        temperature: float = 0.4,
        model: Optional[str] = None,
    ) -> LLMResponse:
        if self.backend == "github":
            return self._github_complete(system, user, max_tokens, temperature, model)
        return self._gemini_complete(system, user, max_tokens, temperature, model)

    # --------------- GitHub Models ---------------
    def _github_complete(self, system, user, max_tokens, temperature, model) -> LLMResponse:
        m = model or GH_MODELS_DEFAULT
        body = json.dumps({
            "model": m,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }).encode("utf-8")
        req = Request(
            GH_MODELS_URL,
            data=body,
            method="POST",
            headers={
                "Authorization": f"Bearer {self.gh_token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )
        try:
            with urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except HTTPError as e:
            err_body = e.read().decode("utf-8", errors="ignore")
            raise RuntimeError(f"GitHub Models {e.code}: {err_body[:300]}")
        except URLError as e:
            raise RuntimeError(f"GitHub Models network error: {e}")

        text = data["choices"][0]["message"]["content"]
        usage = data.get("usage", {}) or {}
        return LLMResponse(
            text=text.strip(),
            backend="github",
            model=m,
            tokens_in=usage.get("prompt_tokens"),
            tokens_out=usage.get("completion_tokens"),
        )

    # --------------- Gemini ---------------
    def _gemini_complete(self, system, user, max_tokens, temperature, model) -> LLMResponse:
        m = model or GEMINI_DEFAULT
        url = GEMINI_URL_TMPL.format(model=m, key=self.gemini_key)
        body = json.dumps({
            "systemInstruction": {"parts": [{"text": system}]},
            "contents": [{"role": "user", "parts": [{"text": user}]}],
            "generationConfig": {
                "maxOutputTokens": max_tokens,
                "temperature": temperature,
            },
        }).encode("utf-8")
        req = Request(
            url, data=body, method="POST",
            headers={"Content-Type": "application/json"},
        )
        try:
            with urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except HTTPError as e:
            err_body = e.read().decode("utf-8", errors="ignore")
            raise RuntimeError(f"Gemini {e.code}: {err_body[:300]}")

        text = data["candidates"][0]["content"]["parts"][0]["text"]
        usage = data.get("usageMetadata", {}) or {}
        return LLMResponse(
            text=text.strip(),
            backend="gemini",
            model=m,
            tokens_in=usage.get("promptTokenCount"),
            tokens_out=usage.get("candidatesTokenCount"),
        )


def complete_json(client: LLMClient, system: str, user: str, **kwargs) -> dict:
    """Helper: ask for strict JSON, parse, return dict. Raises on bad JSON."""
    sys2 = system + "\n\nReturn ONLY valid JSON. No prose, no markdown fences."
    resp = client.complete(system=sys2, user=user, **kwargs)
    raw = resp.text.strip()
    # Strip ``` fences if the model added them anyway
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1] if "\n" in raw else raw
        raw = raw.rsplit("```", 1)[0] if raw.endswith("```") else raw
        raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)


if __name__ == "__main__":
    c = LLMClient()
    r = c.complete(
        system="You are a terse assistant.",
        user="In one sentence, name the most absorbed form of magnesium and why.",
        max_tokens=80,
    )
    print(f"[{r.backend}/{r.model}] {r.text}")
    if r.tokens_in:
        print(f"tokens: in={r.tokens_in} out={r.tokens_out}")
