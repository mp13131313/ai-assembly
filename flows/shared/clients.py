"""Thin wrappers around the four model APIs used by the Persona Pipeline.

Each function takes a fully-rendered prompt and returns plain text or parsed
JSON. Retries, timeouts, and rate-limit handling live in the calling Prefect
task — these wrappers do exactly one thing: make the call.
"""
from __future__ import annotations

import json
import os
from typing import Any

from dotenv import load_dotenv

load_dotenv()


# --- Anthropic / Claude --------------------------------------------------

def call_claude(
    *,
    system: str,
    user: str,
    model: str | None = None,
    max_tokens: int = 8192,
    temperature: float = 0.2,
    thinking_budget: int | None = None,
    response_format_json: bool = False,
) -> dict[str, Any]:
    """One Claude call. Returns dict with `text` (str) and `usage` (dict).

    If `response_format_json` is True, also returns parsed `json` field.
    """
    import anthropic  # lazy import so missing keys don\'t break import

    model = model or os.environ.get("CLAUDE_MODEL", "claude-opus-4-6")
    client = anthropic.Anthropic()

    kwargs: dict[str, Any] = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "system": system,
        "messages": [{"role": "user", "content": user}],
    }
    if thinking_budget:
        # Anthropic recommends thinking.type="adaptive" over the deprecated
        # "enabled" mode for better performance. Adaptive does NOT take
        # budget_tokens — the model decides how much to think. The
        # thinking_budget parameter here is kept for backwards-compat with
        # the rest of the codebase; a truthy value just switches thinking on.
        kwargs["thinking"] = {"type": "adaptive"}

    msg = client.messages.create(**kwargs)
    text_parts = [b.text for b in msg.content if b.type == "text"]
    text = "".join(text_parts)

    out: dict[str, Any] = {
        "text": text,
        "usage": {
            "input_tokens": msg.usage.input_tokens,
            "output_tokens": msg.usage.output_tokens,
        },
        "model": model,
        "stop_reason": msg.stop_reason,
    }
    if response_format_json:
        # Trim ```json fences if present
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1].rsplit("```", 1)[0]
        out["json"] = json.loads(cleaned)
    return out


# --- Perplexity (sonar-deep-research) -----------------------------------

def call_perplexity(
    *,
    user: str,
    model: str | None = None,
    temperature: float = 0.0,
    return_citations: bool = True,
) -> dict[str, Any]:
    """One Perplexity call. Uses OpenAI-compatible REST endpoint.

    sonar-deep-research can take 5-10 minutes for a single query — the
    Prefect task wrapping this should set timeout >= 15 min.

    sonar-deep-research embeds a <think>...</think> chain-of-thought block
    at the start of the response. We split it: returns `text` (clean
    deliverable, think stripped) and `think` (the reasoning trace, kept
    for audit).
    """
    import requests
    import re

    model = model or os.environ.get("PERPLEXITY_MODEL", "sonar-deep-research")
    api_key = os.environ["PERPLEXITY_API_KEY"]

    resp = requests.post(
        "https://api.perplexity.ai/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": [{"role": "user", "content": user}],
            "temperature": temperature,
            "return_citations": return_citations,
        },
        timeout=900,  # 15 min
    )
    resp.raise_for_status()
    data = resp.json()
    raw_text = data["choices"][0]["message"]["content"]

    # Split <think>...</think> block from deliverable
    m = re.search(r"<think>(.*?)</think>\s*", raw_text, flags=re.DOTALL)
    if m:
        think = m.group(1).strip()
        text = raw_text[m.end():].strip()
    else:
        think = ""
        text = raw_text.strip()

    return {
        "text": text,
        "think": think,
        "raw_text": raw_text,
        "citations": data.get("citations", []),
        "search_results": data.get("search_results", []),  # newer field name
        "usage": data.get("usage", {}),
        "model": model,
    }


# --- Gemini -------------------------------------------------------------

def call_gemini(
    *,
    user: str,
    model: str | None = None,
    temperature: float = 0.2,
    max_output_tokens: int = 16384,
    thinking_budget: int | None = 0,
) -> dict[str, Any]:
    """One Gemini call. Uses google-genai SDK (the supported library; the
    older google-generativeai package is deprecated as of late 2025).

    `thinking_budget=0` disables thinking on 2.5-series models so the
    output budget isn't consumed by hidden reasoning. Set to None to
    leave the model default in place, or to a positive int for a budget.
    """
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])
    model_name = model or os.environ.get("GEMINI_MODEL", "gemini-2.5-pro")

    config_kwargs: dict[str, Any] = {
        "temperature": temperature,
        "max_output_tokens": max_output_tokens,
    }
    if thinking_budget is not None:
        config_kwargs["thinking_config"] = types.ThinkingConfig(
            thinking_budget=thinking_budget
        )

    resp = client.models.generate_content(
        model=model_name,
        contents=user,
        config=types.GenerateContentConfig(**config_kwargs),
    )

    text = resp.text or ""
    usage = {}
    if getattr(resp, "usage_metadata", None):
        u = resp.usage_metadata
        usage = {
            "input_tokens": getattr(u, "prompt_token_count", None),
            "output_tokens": getattr(u, "candidates_token_count", None),
            "thoughts_tokens": getattr(u, "thoughts_token_count", None),
        }
    return {"text": text, "model": model_name, "usage": usage}


# --- OpenAI (GPT-4o for cross-model validation) -------------------------

def call_openai(
    *,
    system: str,
    user: str,
    model: str | None = None,
    temperature: float = 0.0,
    max_tokens: int = 8192,
    response_format_json: bool = False,
) -> dict[str, Any]:
    """One OpenAI call. Uses openai SDK."""
    from openai import OpenAI

    client = OpenAI()
    model = model or os.environ.get("OPENAI_MODEL", "gpt-4o")

    kwargs: dict[str, Any] = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if response_format_json:
        kwargs["response_format"] = {"type": "json_object"}

    resp = client.chat.completions.create(**kwargs)
    text = resp.choices[0].message.content or ""
    out: dict[str, Any] = {
        "text": text,
        "usage": {
            "input_tokens": resp.usage.prompt_tokens,
            "output_tokens": resp.usage.completion_tokens,
        },
        "model": model,
    }
    if response_format_json:
        out["json"] = json.loads(text)
    return out
