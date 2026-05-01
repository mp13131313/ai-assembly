"""Thin wrappers around the four model APIs used by the Persona Pipeline.

Each function takes a fully-rendered prompt and returns plain text or parsed
JSON. Retries, timeouts, and rate-limit handling live in the calling Prefect
task — these wrappers do exactly one thing: make the call.

Each wrapper accepts optional slug/pass_name/project_root kwargs. When slug
is provided, a telemetry entry is recorded to voices/<slug>/_manifest.json
via flows.shared.manifest.record().
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

load_dotenv()


def _estimate_anthropic_thinking_tokens(client: Any, model: str, response_text: str, output_tokens: int) -> int:
    """Compute billed thinking tokens via subtraction.

    Anthropic's `Usage.output_tokens` is the BILLED total (thinking +
    response, undifferentiated). The SDK has no `Usage.thinking_tokens`
    field at any version (verified empirically on SDK 0.94.1 +
    Anthropic docs Apr 2026). To recover the thinking-only count for
    observability, we subtract the response-text token count (measured
    via the free `messages.count_tokens` API) from the total.

    Returns 0 on failure — telemetry must not break the pipeline.
    """
    if not response_text or not output_tokens:
        return 0
    try:
        count = client.messages.count_tokens(
            model=model,
            messages=[{"role": "assistant", "content": response_text}],
        )
        return max(0, output_tokens - count.input_tokens)
    except Exception:  # noqa: BLE001 — never break pipeline on telemetry
        return 0


def _record(
    slug: str | None,
    pass_name: str | None,
    provider: str,
    model: str,
    usage: dict,
    wall_seconds: float,
    project_root: Path | None,
) -> None:
    if not slug or not pass_name:
        return
    try:
        from flows.shared.manifest import record
        record(
            slug=slug,
            pass_name=pass_name,
            model=model,
            provider=provider,
            input_tokens=usage.get("input_tokens", 0) or 0,
            output_tokens=usage.get("output_tokens", 0) or 0,
            thinking_tokens=usage.get("thinking_tokens", 0) or 0,
            wall_seconds=wall_seconds,
            project_root=project_root,
        )
    except Exception:
        pass  # never let telemetry failures break the pipeline


# --- Anthropic / Claude --------------------------------------------------

def call_claude(
    *,
    system: str,
    user: str,
    model: str | None = None,
    max_tokens: int = 8192,
    temperature: float | None = 0.2,
    thinking: bool = False,
    response_format_json: bool = False,
    slug: str | None = None,
    pass_name: str | None = None,
    project_root: Path | None = None,
) -> dict[str, Any]:
    """One Claude call. Returns dict with `text` (str) and `usage` (dict).

    `thinking=True` enables Anthropic's adaptive thinking mode (the model
    decides how much to think; no budget parameter is passed). Adaptive
    thinking requires `temperature=1.0` per the SDK.

    If `response_format_json` is True, also returns parsed `json` field.
    """
    import anthropic  # lazy import so missing keys don\'t break import

    model = model or os.environ.get("CLAUDE_MODEL", "claude-opus-4-7")
    client = anthropic.Anthropic()

    kwargs: dict[str, Any] = {
        "model": model,
        "max_tokens": max_tokens,
        "system": system,
        "messages": [{"role": "user", "content": user}],
    }
    # FU#60 2026-04-29 — temperature/thinking compatibility.
    # Anthropic's extended-thinking docs (platform.claude.com §"Feature
    # compatibility") state: "Thinking isn't compatible with temperature
    # or top_k modifications as well as forced tool use." For newer models
    # (Opus 4.7), non-default temperature returns 400. The SDK default is
    # 1.0; setting temperature=1.0 explicitly currently works but is
    # technically a "modification" per the docs.
    # Policy: when thinking=True, DROP temperature from the API call to
    # match Anthropic's example code (which omits temperature entirely
    # in adaptive-thinking samples) and future-proof against API tightening.
    # When thinking=False (e.g. Pass 7-pre Sonnet verifiers, Pass 7c
    # bias-aware fallback), pass temperature through as caller specified.
    if temperature is not None and not thinking:
        kwargs["temperature"] = temperature
    if thinking:
        # Anthropic recommends thinking.type="adaptive" over the deprecated
        # "enabled" mode. Adaptive does NOT take budget_tokens — the model
        # decides how much to think based on the task.
        # FU#60 2026-04-29: explicit `display: "summarized"`. On Opus 4.7
        # the default is `omitted` — thinking blocks still come back in the
        # response stream but with EMPTY `thinking` content (only signature).
        # We're billed for the thinking either way; setting summarized makes
        # it visible so we can audit whether adaptive actually engaged on
        # any given call. See `personas/flows/shared/clients.py` thinking_trace
        # field in the returned dict.
        kwargs["thinking"] = {"type": "adaptive", "display": "summarized"}

    # Anthropic SDK refuses non-streaming for requests it estimates will take
    # >10 min. With max_tokens >= 16384 + adaptive thinking, the estimate
    # crosses that threshold. Use streaming and accumulate text + thinking.
    use_streaming = max_tokens >= 16384 or thinking
    _t0 = time.time()
    if use_streaming:
        # FU#60 cleanup 2026-04-29: drain text_stream + read final.content
        # rather than walking streaming events manually. With
        # display="summarized" thinking blocks land in final.content alongside
        # text blocks, so a single content walk captures everything we need
        # (text, thinking_trace, block_types). Matches runtime/flows/voice/
        # _anthropic_call.py pattern. ~15 lines of event-walk code removed;
        # observable behaviour identical.
        # 2026-04-30: streaming-stability retry. Empirically attested 3x
        # consecutive Pass 4a failures on Octopus voice (107K corpus excerpts,
        # large response near ceiling) with httpx.RemoteProtocolError "peer
        # closed connection without sending complete message body". 1-retry
        # with 15s backoff; non-deterministic flake usually passes second time.
        # Mirrors FU#2 retry-on-JSONDecodeError pattern but for transport-side
        # stream drops.
        import httpx as _httpx
        import sys as _sys
        last_stream_err = None
        for _attempt in range(2):
            try:
                with client.messages.stream(**kwargs) as stream:
                    for _ in stream.text_stream:
                        pass  # drain; final assembly via final.content below
                    final = stream.get_final_message()
                break  # success
            except (_httpx.RemoteProtocolError, _httpx.ReadError, _httpx.ReadTimeout) as _e:
                last_stream_err = _e
                if _attempt == 0:
                    _sys.stderr.write(
                        f"[call_claude WARN] {type(_e).__name__} on attempt 1: {str(_e)[:120]}. "
                        f"Retrying in 15s.\n"
                    )
                    time.sleep(15)
                    continue
                raise
        text_parts: list[str] = []
        thinking_parts: list[str] = []
        block_types: list[str] = []
        for block in final.content:
            btype = getattr(block, "type", "?")
            block_types.append(btype)
            if btype == "text":
                text_parts.append(getattr(block, "text", "") or "")
            elif btype == "thinking":
                thinking_parts.append(getattr(block, "thinking", "") or "")
        text = "".join(text_parts)
        thinking_trace = "".join(thinking_parts)

        # Thinking tokens via subtraction: Anthropic SDK Usage exposes only
        # output_tokens (the BILLED total = thinking + response, undifferentiated).
        # We use the free `messages.count_tokens` API on the response text to
        # recover the response-only count, then subtract. Verified against
        # Anthropic docs (Apr 2026) + SDK 0.94.1 empirical probe — there is
        # no `usage.thinking_tokens` field at any SDK version.
        thinking_tokens = _estimate_anthropic_thinking_tokens(
            client, model, text, final.usage.output_tokens
        )
        out: dict[str, Any] = {
            "text": text,
            "usage": {
                "input_tokens": final.usage.input_tokens,
                "output_tokens": final.usage.output_tokens,
                "thinking_tokens": thinking_tokens,
            },
            "model": model,
            "stop_reason": final.stop_reason,
            # FU#60: thinking-trace observability. Additive; existing callers
            # ignore. New callers can inspect block_types + thinking_trace
            # to verify adaptive thinking is actually firing on their prompts.
            "thinking_trace": thinking_trace,
            "block_types": block_types,
        }
    else:
        msg = client.messages.create(**kwargs)
        text_parts = [b.text for b in msg.content if b.type == "text"]
        text = "".join(text_parts)
        thinking_tokens = _estimate_anthropic_thinking_tokens(
            client, model, text, msg.usage.output_tokens
        )
        out = {
            "text": text,
            "usage": {
                "input_tokens": msg.usage.input_tokens,
                "output_tokens": msg.usage.output_tokens,
                "thinking_tokens": thinking_tokens,
            },
            "model": model,
            "stop_reason": msg.stop_reason,
        }
    # FU#9 2026-04-24: proactive max_tokens monitoring. `stop_reason == "max_tokens"`
    # means output was truncated. If JSON parsing fails we raise immediately
    # (existing behaviour below); if JSON happens to parse (rare — usually
    # truncation produces invalid JSON — but can happen with partial lists),
    # print a warning so operators see the ceiling issue before it manifests
    # as missing content downstream.
    if out.get("stop_reason") == "max_tokens":
        import sys as _sys
        _sys.stderr.write(
            f"[call_claude WARN] stop_reason=max_tokens on {model} "
            f"(max_tokens={max_tokens}, output_tokens={out['usage']['output_tokens']}). "
            f"Output was truncated — consider bumping max_tokens for this call site.\n"
        )
    if response_format_json:
        # Trim ```json fences if present
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1].rsplit("```", 1)[0]
        try:
            out["json"] = json.loads(cleaned)
        except json.JSONDecodeError as e:
            out["json"] = None
            out["json_parse_error"] = f"{type(e).__name__}: {e}"
            out["raw_text"] = text
            # If the model hit max_tokens, that's almost certainly why
            if out.get("stop_reason") == "max_tokens":
                raise RuntimeError(
                    f"Claude hit max_tokens ({max_tokens}) before completing JSON. "
                    f"Bump max_tokens and retry. Raw text len: {len(text)}"
                ) from e
            raise RuntimeError(f"Claude returned invalid JSON: {e}") from e
    out["_wall_seconds"] = time.time() - _t0
    _record(slug, pass_name, "anthropic", out["model"], out["usage"], out["_wall_seconds"], project_root)
    return out


# --- Perplexity (sonar-deep-research) -----------------------------------

def call_perplexity(
    *,
    user: str,
    model: str | None = None,
    temperature: float = 0.0,
    return_citations: bool = True,
    slug: str | None = None,
    pass_name: str | None = None,
    project_root: Path | None = None,
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

    _t0_perp = time.time()
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
    try:
        raw_text = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as e:
        raise RuntimeError(
            f"Perplexity response missing expected structure: {e}. "
            f"Response: {json.dumps(data)[:500]}"
        ) from e

    # Split <think>...</think> block from deliverable
    m = re.search(r"<think>(.*?)</think>\s*", raw_text, flags=re.DOTALL)
    if m:
        think = m.group(1).strip()
        text = raw_text[m.end():].strip()
    else:
        think = ""
        text = raw_text.strip()

    out_perp = {
        "text": text,
        "think": think,
        "raw_text": raw_text,
        "citations": data.get("citations", []),
        "search_results": data.get("search_results", []),
        "usage": data.get("usage", {}),
        "model": model,
        "_wall_seconds": time.time() - _t0_perp,
    }
    _record(slug, pass_name, "perplexity", model, out_perp["usage"], out_perp["_wall_seconds"], project_root)
    return out_perp


# --- Gemini -------------------------------------------------------------

def call_gemini(
    *,
    user: str,
    model: str | None = None,
    temperature: float = 0.2,
    max_output_tokens: int = 16384,
    thinking_budget: int | None = None,
    slug: str | None = None,
    pass_name: str | None = None,
    project_root: Path | None = None,
) -> dict[str, Any]:
    """One Gemini call. Uses google-genai SDK (the supported library; the
    older google-generativeai package is deprecated as of late 2025).

    `thinking_budget=None` (default) leaves the model's own default in place.
    For gemini-2.5-pro this is required — the model only operates in thinking
    mode and rejects budget=0. Set to a positive int to override.
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

    _t0_gem = time.time()
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
    out_gem = {"text": text, "model": model_name, "usage": usage, "_wall_seconds": time.time() - _t0_gem}
    _record(slug, pass_name, "google", model_name, usage, out_gem["_wall_seconds"], project_root)
    return out_gem


# --- OpenAI (gpt-5.4 primary for cross-model validation) ----------------

def call_openai(
    *,
    system: str,
    user: str,
    model: str | None = None,
    temperature: float = 0.0,
    max_tokens: int = 8192,
    response_format_json: bool = False,
    reasoning_effort: str | None = None,
    slug: str | None = None,
    pass_name: str | None = None,
    project_root: Path | None = None,
) -> dict[str, Any]:
    """One OpenAI call. Uses openai SDK.

    reasoning_effort: 'none' | 'low' | 'medium' | 'high' | 'xhigh'. When set
    (or when model is o-series), the call uses the reasoning-API path:
    max_completion_tokens, no temperature, and the reasoning_effort kwarg is
    forwarded. GPT-5.x accepts reasoning_effort; older o1/o3/o4 models set it
    implicitly by model choice.
    """
    from openai import OpenAI

    client = OpenAI()
    model = model or os.environ.get("OPENAI_MODEL", "gpt-5.4")

    # Reasoning path applies when:
    #   - model is an o-series reasoning model (o1/o3/o4), OR
    #   - caller explicitly requested reasoning_effort (e.g. gpt-5.4 high)
    # Both require max_completion_tokens instead of max_tokens and drop
    # temperature (reasoning models reject non-default temperature).
    is_o_series = any(model.startswith(p) for p in ("o1", "o3", "o4"))
    use_reasoning_path = is_o_series or reasoning_effort is not None

    kwargs: dict[str, Any] = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }
    if use_reasoning_path:
        kwargs["max_completion_tokens"] = max_tokens
        if reasoning_effort is not None:
            kwargs["reasoning_effort"] = reasoning_effort
    else:
        kwargs["temperature"] = temperature
        kwargs["max_tokens"] = max_tokens
    if response_format_json:
        kwargs["response_format"] = {"type": "json_object"}

    _t0_oai = time.time()
    resp = client.chat.completions.create(**kwargs)
    if not resp.choices:
        raise RuntimeError(f"OpenAI returned no choices for model {model}")
    text = resp.choices[0].message.content or ""
    oai_usage = {
        "input_tokens": resp.usage.prompt_tokens,
        "output_tokens": resp.usage.completion_tokens,
    }
    out: dict[str, Any] = {
        "text": text,
        "usage": oai_usage,
        "model": model,
        "_wall_seconds": time.time() - _t0_oai,
    }
    if response_format_json:
        try:
            out["json"] = json.loads(text)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"OpenAI ({model}) returned invalid JSON: {e}") from e
    _record(slug, pass_name, "openai", model, oai_usage, out["_wall_seconds"], project_root)
    return out
