"""pass_7pre_chunked.py — Chunked Pass 7-pre citation verification (FU#2).

Replaces the single-shot Pass 7-pre that hits Sonnet 4.6's 128K hard
output ceiling on rich cards (empirically hit twice during 2026-04-24
Dostoevsky re-run on FU#32 prompts).

Three-stage architecture:

  Stage 1 (extract):   1 Sonnet call reads card-only (no primary_texts,
                       no dossier), emits list of verifiable claim items.
                       Small output (~20-40K tokens), well under ceiling.

  Stage 2 (verify):    N parallel Sonnet calls, each receiving ~20-25
                       claim items + primary_texts + merged_dossier,
                       fill in status + evidence per item. max_tokens
                       16K per call, well under ceiling.

  Stage 3 (boddice):   1 small Sonnet call checks boddice_tag_flags
                       across the card. Small output (~2-5K tokens).
                       Runs in parallel with Stage 2.

Aggregation is pure Python: combines items from all verify batches,
computes summary counts, determines overall verdict, composes review_notes.

Preserves the Pass 7-pre output schema exactly as Pass 7a reads it —
NO downstream contract change. Drop-in replacement for the single-shot
call in run_persona_pipeline.py.

Cost vs single-shot:
  Current (ceiling-hit): ~$3 + 25-30 min wall (timeout)
  Chunked:               ~$2.50-3.50 + 3-5 min wall (parallel)
  Savings: 25+ min wall, produces actual verification output instead
  of skipping when ceiling hit.
"""
from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

from flows.shared.clients import call_claude
from flows.shared.prompt_render import render

# ── configuration ────────────────────────────────────────────────────────────

_EXTRACT_MODEL = "claude-sonnet-4-6"
_EXTRACT_MAX_TOKENS = 32000  # Card-only input, claim-list output; plenty of headroom.

_VERIFY_MODEL = "claude-sonnet-4-6"
_VERIFY_MAX_TOKENS = 16000  # Per-batch verification; ~20-25 items in, same items + status + evidence out.
_VERIFY_BATCH_SIZE = 25     # Empirical sweet spot: balance between output size + batch count.
_VERIFY_MAX_WORKERS = 4     # Parallelism cap to respect rate limits.

_BODDICE_MODEL = "claude-sonnet-4-6"
_BODDICE_MAX_TOKENS = 8000  # Small output (flag list only).


# ── stage 1: extraction ──────────────────────────────────────────────────────

def extract_claims(
    persona_card: dict[str, Any],
    voice_type: str,
    voice_mode: str | None,
    hostile_sources: bool,
) -> dict[str, Any]:
    """Stage 1: extract verifiable claim items from the persona card.

    Returns:
        {
            "verification_mode": "standard" | "observational" | "fictional",
            "hostile_source_check": bool,
            "items": [{"claim", "source_fields", "claim_type"}, ...],
        }
    """
    sysp = render(
        "persona_pass_7pre_extract",
        type=voice_type,
        voice_mode=voice_mode,
        hostile_sources=hostile_sources,
    )
    userp = render(
        "persona_pass_7pre_extract_user",
        persona_card_json=json.dumps(persona_card, ensure_ascii=False, indent=2),
    )
    r = call_claude(
        system=sysp,
        user=userp,
        model=_EXTRACT_MODEL,
        max_tokens=_EXTRACT_MAX_TOKENS,
        temperature=0.0,
        thinking=False,
        response_format_json=True,
    )
    result = r["json"]
    # Defensive: ensure shape
    result.setdefault("verification_mode", "standard")
    result.setdefault("hostile_source_check", hostile_sources)
    result.setdefault("items", [])
    return result


# ── stage 2: batched verification ────────────────────────────────────────────

def _batch(items: list[dict], size: int) -> list[list[dict]]:
    return [items[i : i + size] for i in range(0, len(items), size)]


def verify_batch(
    claim_items: list[dict[str, Any]],
    primary_texts: str,
    merged_dossier: str,
    verification_mode: str,
    hostile_source_check: bool,
) -> list[dict[str, Any]]:
    """Stage 2 single batch: verify ~20-25 pre-extracted claims.

    Returns: list of items with status + evidence filled in.
    """
    sysp = render(
        "persona_pass_7pre_verify_batch",
        verification_mode=verification_mode,
        hostile_source_check=hostile_source_check,
    )
    userp = render(
        "persona_pass_7pre_verify_batch_user",
        claim_items_json=json.dumps(claim_items, ensure_ascii=False, indent=2),
        primary_texts=primary_texts,
        merged_dossier=merged_dossier,
    )
    r = call_claude(
        system=sysp,
        user=userp,
        model=_VERIFY_MODEL,
        max_tokens=_VERIFY_MAX_TOKENS,
        temperature=0.0,
        thinking=False,
        response_format_json=True,
    )
    batch_result = r["json"]
    verified_items = batch_result.get("items", [])

    # Defensive: if the LLM dropped any items, pad with UNVERIFIED to preserve
    # the input count (schema invariant promised to Pass 7a aggregator).
    if len(verified_items) < len(claim_items):
        by_claim = {i.get("claim", ""): i for i in verified_items}
        filled: list[dict[str, Any]] = []
        for src in claim_items:
            match = by_claim.get(src.get("claim", ""))
            if match is not None:
                filled.append(match)
            else:
                filled.append({
                    **src,
                    "status": "UNVERIFIED",
                    "evidence": "Verifier dropped item from batch output; preserved as UNVERIFIED.",
                })
        verified_items = filled
    return verified_items


def _verify_batch_with_retry(
    batch: list[dict[str, Any]],
    primary_texts: str,
    merged_dossier: str,
    verification_mode: str,
    hostile_source_check: bool,
) -> list[dict[str, Any]]:
    """Wraps verify_batch with 1 retry on transient JSON/API failures.

    FU#2 follow-up 2026-04-24: Sonnet occasionally emits partially-invalid JSON
    on a batch (observed on Dostoevsky FU#32 re-run: 1 batch of 3 items got a
    missing-comma JSON parse error). Retry once with a short backoff before
    falling back to UNVERIFIED-with-error-explanation.
    """
    import time as _time
    try:
        return verify_batch(
            batch, primary_texts, merged_dossier, verification_mode, hostile_source_check
        )
    except RuntimeError as first_err:
        # Transient JSON parse / API error — retry after brief backoff.
        _time.sleep(5)
        try:
            return verify_batch(
                batch, primary_texts, merged_dossier, verification_mode, hostile_source_check
            )
        except Exception as retry_err:
            # Preserve batch with UNVERIFIED fallback + both error traces.
            return [
                {
                    **item,
                    "status": "UNVERIFIED",
                    "evidence": (
                        f"Batch verification failed after 1 retry: "
                        f"{type(retry_err).__name__}: {str(retry_err)[:150]} "
                        f"(first attempt: {type(first_err).__name__}: {str(first_err)[:100]})"
                    ),
                }
                for item in batch
            ]


def verify_all_batches(
    claim_items: list[dict[str, Any]],
    primary_texts: str,
    merged_dossier: str,
    verification_mode: str,
    hostile_source_check: bool,
    batch_size: int = _VERIFY_BATCH_SIZE,
    max_workers: int = _VERIFY_MAX_WORKERS,
) -> list[dict[str, Any]]:
    """Stage 2 orchestrator: parallel verify across batches."""
    if not claim_items:
        return []
    batches = _batch(claim_items, batch_size)

    # Execute in parallel, preserving original order. Each batch wrapped with
    # 1-retry on transient JSON/API failures (FU#2 follow-up 2026-04-24).
    results_by_idx: dict[int, list[dict[str, Any]]] = {}
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_idx = {
            executor.submit(
                _verify_batch_with_retry,
                batch,
                primary_texts,
                merged_dossier,
                verification_mode,
                hostile_source_check,
            ): idx
            for idx, batch in enumerate(batches)
        }
        for future in as_completed(future_to_idx):
            idx = future_to_idx[future]
            try:
                results_by_idx[idx] = future.result()
            except Exception as exc:
                # Belt-and-braces: _verify_batch_with_retry should not raise,
                # but if something unexpected escapes (e.g. ExecutorError),
                # still pad items with UNVERIFIED so aggregate stays honest.
                batch = batches[idx]
                results_by_idx[idx] = [
                    {
                        **item,
                        "status": "UNVERIFIED",
                        "evidence": f"Batch future raised: {type(exc).__name__}: {str(exc)[:200]}",
                    }
                    for item in batch
                ]

    # Flatten in original batch order
    all_items: list[dict[str, Any]] = []
    for idx in sorted(results_by_idx.keys()):
        all_items.extend(results_by_idx[idx])
    return all_items


# ── stage 3: boddice tag check ───────────────────────────────────────────────

def check_boddice_tags(persona_card: dict[str, Any]) -> list[dict[str, Any]]:
    """Stage 3: narrow Boddice evidence-tag verification.

    Small dedicated call preserving the boddice_tag_flags[] schema from
    the original single-shot Pass 7-pre. Returns [] if all tags applied.
    """
    sysp = render("persona_pass_7pre_boddice_check")
    userp = render(
        "persona_pass_7pre_boddice_check_user",
        persona_card_json=json.dumps(persona_card, ensure_ascii=False, indent=2),
    )
    r = call_claude(
        system=sysp,
        user=userp,
        model=_BODDICE_MODEL,
        max_tokens=_BODDICE_MAX_TOKENS,
        temperature=0.0,
        thinking=False,
        response_format_json=True,
    )
    flags = r["json"].get("boddice_tag_flags", [])
    return flags if isinstance(flags, list) else []


# ── aggregation (pure Python) ────────────────────────────────────────────────

def _compute_summary(items: list[dict[str, Any]]) -> dict[str, int]:
    """Count per-status occurrences for the summary field."""
    counts = {
        "verified": 0,
        "unverified": 0,
        "dossier_only": 0,
        "interpretive": 0,
        "inconsistent": 0,
        "hostile_flagged": 0,
    }
    for item in items:
        status = item.get("status", "").upper()
        if status == "VERIFIED":
            counts["verified"] += 1
        elif status == "UNVERIFIED":
            counts["unverified"] += 1
        elif status == "DOSSIER_ONLY":
            counts["dossier_only"] += 1
        elif status == "INTERPRETIVE":
            counts["interpretive"] += 1
        elif status == "INCONSISTENT":
            counts["inconsistent"] += 1
        elif status == "HOSTILE_FLAGGED":
            counts["hostile_flagged"] += 1
    return counts


def _determine_overall(
    summary: dict[str, int],
    boddice_flags: list[dict[str, Any]],
) -> str:
    """PASS if no UNVERIFIED / INCONSISTENT / HOSTILE_FLAGGED items and no
    missing Boddice tags; REVIEW_NEEDED otherwise."""
    if (
        summary["unverified"] == 0
        and summary["inconsistent"] == 0
        and summary["hostile_flagged"] == 0
        and not boddice_flags
    ):
        return "PASS"
    return "REVIEW_NEEDED"


def _compose_review_notes(
    summary: dict[str, int],
    boddice_flags: list[dict[str, Any]],
    items: list[dict[str, Any]],
) -> str:
    """Short paragraph describing the most important issues."""
    if (
        summary["unverified"] == 0
        and summary["inconsistent"] == 0
        and summary["hostile_flagged"] == 0
        and not boddice_flags
    ):
        return "No issues"
    parts: list[str] = []
    if summary["inconsistent"]:
        inconsistent = [i for i in items if i.get("status") == "INCONSISTENT"]
        parts.append(
            f"{summary['inconsistent']} INCONSISTENT claim(s): "
            + "; ".join(i.get("claim", "")[:80] for i in inconsistent[:3])
        )
    if summary["unverified"]:
        unverified = [i for i in items if i.get("status") == "UNVERIFIED"]
        parts.append(
            f"{summary['unverified']} UNVERIFIED claim(s): "
            + "; ".join(i.get("claim", "")[:80] for i in unverified[:3])
        )
    if summary["hostile_flagged"]:
        parts.append(f"{summary['hostile_flagged']} HOSTILE_FLAGGED claim(s).")
    if boddice_flags:
        parts.append(
            f"{len(boddice_flags)} Boddice tag flag(s): "
            + "; ".join(f.get("missing_tag", "") + " at " + f.get("field_path", "") for f in boddice_flags[:3])
        )
    return " | ".join(parts) if parts else "Review needed — see items + boddice_tag_flags."


# ── orchestrator ─────────────────────────────────────────────────────────────

def run_chunked_pass_7pre(
    persona_card: dict[str, Any],
    primary_texts: str,
    merged_dossier: str,
    voice_type: str,
    voice_mode: str | None,
    hostile_sources: bool,
) -> dict[str, Any]:
    """Run the full chunked Pass 7-pre pipeline.

    Returns the Pass 7-pre output matching the original schema Pass 7a reads:
      {
        verification_mode, hostile_source_check,
        items: [...],
        summary: {verified, unverified, dossier_only, interpretive, inconsistent, hostile_flagged},
        overall: "PASS" | "REVIEW_NEEDED",
        review_notes: "<short paragraph>",
        boddice_tag_flags: [...],
      }
    """
    # Stage 1: extract claims from card
    extracted = extract_claims(persona_card, voice_type, voice_mode, hostile_sources)
    verification_mode = extracted["verification_mode"]
    hostile_source_check = extracted["hostile_source_check"]
    claim_items = extracted["items"]

    # Stages 2 + 3 run in parallel (verify batches + boddice check).
    with ThreadPoolExecutor(max_workers=2) as top_executor:
        boddice_future = top_executor.submit(check_boddice_tags, persona_card)
        verify_future = top_executor.submit(
            verify_all_batches,
            claim_items,
            primary_texts,
            merged_dossier,
            verification_mode,
            hostile_source_check,
        )
        verified_items = verify_future.result()
        boddice_flags = boddice_future.result()

    # Stage 4: aggregate (pure Python)
    summary = _compute_summary(verified_items)
    overall = _determine_overall(summary, boddice_flags)
    review_notes = _compose_review_notes(summary, boddice_flags, verified_items)

    return {
        "verification_mode": verification_mode,
        "hostile_source_check": hostile_source_check,
        "items": verified_items,
        "summary": summary,
        "overall": overall,
        "review_notes": review_notes,
        "boddice_tag_flags": boddice_flags,
    }
