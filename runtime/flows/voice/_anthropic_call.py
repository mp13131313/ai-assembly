"""Shared Anthropic streaming helper for Voice Pipeline Steps 1/2/3.

Encapsulates the streaming pattern + 1-retry-on-transient-failure
discipline (per spec §"Constraints" → "Error handling: 1 retry on
failure"). Extracts text and thinking blocks from final.content.

The orchestrator (voice_flow.py) catches exceptions thrown by this
helper after the retry budget is spent and logs the failure into
manifest.validation_failures or manifest.skipped — a missing detailed
response is better than a stalled pipeline.

Thinking-token computation: Anthropic's API does NOT expose thinking
tokens separately. `usage.output_tokens` is the BILLED total
(thinking + response tokens combined). To recover the thinking-only
count for observability, we subtract the response token count
(measured via the free `messages.count_tokens` API) from the total.
This gives accurate billed thinking tokens — necessary because the
SDK's Usage object has no `thinking_tokens` field (verified empirically
on SDK 0.94.1 + Anthropic docs Apr 2026).
"""

from __future__ import annotations

import logging
import time
from typing import Any


def _estimate_thinking_tokens(client: Any, model: str, response_text: str, output_tokens: int, logger: logging.Logger | None = None) -> int:
    """Compute billed thinking tokens via subtraction.

    Anthropic's `Usage.output_tokens` includes both thinking + response
    tokens, with no separation. This function uses the free
    `messages.count_tokens` API to count tokens in the response text,
    then subtracts from output_tokens. The remainder is the billed
    thinking-token count (matches Anthropic's billing tokenizer).

    Returns 0 on failure — telemetry should never break the pipeline.
    """
    if not response_text or not output_tokens:
        return 0
    try:
        count = client.messages.count_tokens(
            model=model,
            messages=[{"role": "assistant", "content": response_text}],
        )
        response_tokens = count.input_tokens
        return max(0, output_tokens - response_tokens)
    except Exception as e:  # noqa: BLE001 — telemetry must not break pipeline
        if logger:
            logger.warning(f"thinking-token estimate failed: {type(e).__name__}: {e}")
        return 0


def stream_voice_call(
    client: Any,
    *,
    model: str,
    max_tokens: int,
    system: str,
    user: str,
    thinking_kwargs: dict | None = None,
    retry_backoff_s: int = 5,
    logger: logging.Logger | None = None,
) -> tuple[str, str, Any, int]:
    """Stream a messages call; extract text + thinking from final.content.

    Returns: (detailed_text, thinking_trace, final_message, thinking_tokens).

    `final_message` is the Anthropic Message object — caller can read
    `.usage.input_tokens / .output_tokens` for accounting (the SDK does
    not expose `.thinking_tokens` separately; use the returned
    `thinking_tokens` int instead, which is computed via subtraction
    against `count_tokens(response)`).

    Behaviour:
      - First attempt streams normally.
      - On any exception (network, rate limit, 5xx, JSON parse failure
        in the SDK), waits `retry_backoff_s` seconds and retries once.
      - If the retry also fails, re-raises the second exception. The
        orchestrator handles the failure (logs, skips the pair/voice,
        adds to manifest).

    Spec §"Constraints" requires 1 retry on failure. This function
    implements exactly that — no more, no less. Distinguishing
    transient vs permanent errors would be nice but Anthropic's error
    classes are not all clearly transient/permanent and the cost of
    retrying a permanent error once is one wasted call, which is
    acceptable.
    """
    if thinking_kwargs is None:
        thinking_kwargs = {}
    last_err: Exception | None = None
    for attempt in range(2):  # initial + 1 retry
        try:
            with client.messages.stream(
                model=model,
                max_tokens=max_tokens,
                system=system,
                messages=[{"role": "user", "content": user}],
                **thinking_kwargs,
            ) as stream:
                for _ in stream.text_stream:
                    pass  # consume; final assembly via final.content below
                final = stream.get_final_message()
            text_parts: list[str] = []
            thinking_parts: list[str] = []
            for block in final.content:
                btype = getattr(block, "type", None)
                if btype == "text":
                    text_parts.append(block.text)
                elif btype == "thinking":
                    thinking_parts.append(block.thinking)
            detailed_text = "".join(text_parts)
            thinking_tokens = _estimate_thinking_tokens(
                client, model, detailed_text, final.usage.output_tokens, logger
            )
            return (
                detailed_text,
                "".join(thinking_parts),
                final,
                thinking_tokens,
            )
        except Exception as e:  # noqa: BLE001 — retry is intentional
            last_err = e
            if attempt == 0:
                if logger:
                    logger.warning(
                        f"Anthropic call failed (attempt 1/2): {type(e).__name__}: {e}. "
                        f"Retrying in {retry_backoff_s}s."
                    )
                time.sleep(retry_backoff_s)
                continue
            if logger:
                logger.error(
                    f"Anthropic call failed (attempt 2/2): {type(e).__name__}: {e}. "
                    f"Re-raising."
                )
            raise
    # Unreachable, but satisfies the type checker.
    raise last_err  # type: ignore[misc]
