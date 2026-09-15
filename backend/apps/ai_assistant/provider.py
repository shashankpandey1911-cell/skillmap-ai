"""AI provider abstraction.

Supports OpenAI when OPENAI_API_KEY is set; falls back to rule-based logic
otherwise.  All AI calls go through this module so the rest of the codebase
never touches the API key directly.
"""

import json
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)


def _get_api_key() -> str | None:
    return os.environ.get("OPENAI_API_KEY")


def _get_model() -> str:
    return os.environ.get("OPENAI_MODEL", "gpt-4o-mini")


def ai_available() -> bool:
    """Return True if an AI provider is configured."""
    return bool(_get_api_key())


def _call_openai(system_prompt: str, user_prompt: str, temperature: float = 0.7) -> str:
    """Call OpenAI chat completions and return the assistant message."""
    import openai

    client = openai.OpenAI(api_key=_get_api_key())
    response = client.chat.completions.create(
        model=_get_model(),
        temperature=temperature,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response.choices[0].message.content or ""


def _parse_json(text: str) -> dict:
    """Try to extract JSON from an LLM response, tolerating markdown fences."""
    text = text.strip()
    if text.startswith("```"):
        # Strip markdown code fences
        lines = text.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines)
    return json.loads(text)
