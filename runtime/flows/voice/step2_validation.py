"""Voice Pipeline Step 2 — Validation (operator gate, three pillars).

Runs after Step 2 produces a voice's `artifact_text`. Three pillars per
artifact, each one Anthropic call (Sonnet 4.6 — validators don't need Opus):

  - **Safeguards**: would publishing this hurt the project / break the
    conceit / create reputational risk? Catches AI-self-acknowledgment
    (HOLD), defamation (HOLD), topics_requiring_care violation (HOLD),
    hard_limits breach (WARN), banned_modes slip (WARN), banned_language
    AI-slop subset (WARN), first-person presence leak (low-priority WARN).
  - **Engagement**: would the reader read this? Catches form fidelity
    failure (WARN), length compliance miss (mechanical, no LLM), grounding
    fidelity failure (WARN). Plus cross_night_echo on Nights 2+3 (WARN
    mild/moderate, HOLD heavy).
  - **Voice fidelity**: did the voice deliver what its card promised?
    Runs voice's own `quality_criteria` + checks for `characteristic_moves`
    being performed. WARN ceiling.

Design principle (per OPEN_ITEMS C28b): validation is an OPERATOR GATE,
not a regen mechanism. Halt-on-any-flag (Option C). Operator clears
WARN/HOLD per-voice via dashboard before pipeline proceeds to Editor.

Output: writes `<run_dir>/04_voice/step2_validation/<voice>.json` per
voice. Schema documented at the top of the file.

Field-routing source of truth: `runtime/flows/voice/card_assembly.py:82-152`.

Per pillar, the Anthropic call sees only the card fields relevant to its
concern (not the whole card) — addresses the C28 finding that the prior
Step 1 validators were judging by general heuristics rather than the
literal rules the voice was specifically held to.
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from flows.shared.io import get_logger, load_prompt, write_json_atomic


# --- Constants ----------------------------------------------------------

# Sonnet 4.6 — fast + cheap; validators don't need Opus.
STEP2_VALIDATION_MODEL = os.environ.get(
    "VOICE_STEP2_VALIDATION_MODEL", "claude-sonnet-4-6"
)
STEP2_VALIDATION_MAX_TOKENS = int(
    os.environ.get("VOICE_STEP2_VALIDATION_MAX_TOKENS", "4096")
)
STEP2_VALIDATION_PILLAR_BATCH = int(
    os.environ.get("VOICE_STEP2_VALIDATION_PILLAR_BATCH", "6")
)

# Subset of banned_language that gets surfaced as AI-slop flags.
# Foreign-vocabulary anachronisms ("dollars" for Plato) are charm; the
# AI-tells below are embarrassing because they pattern-match as generic
# AI prose. Validator filters per-voice banned_language to this subset.
_AI_SLOP_LEXICON = {
    "fascinating", "interesting", "thought-provoking", "important to note",
    "crucial", "innovative", "delve", "delve into", "in conclusion",
    "it is worth noting", "navigate", "navigate the", "navigating",
    "tapestry", "leverage", "leveraging", "groundbreaking",
    "key takeaway", "takeaways", "in summary", "fundamentally",
    "in essence", "essentially",
}


# --- Anthropic call helper ---------------------------------------------

def _call_anthropic(*, system: str, user: str) -> dict[str, Any]:
    """One Sonnet 4.6 call. Returns text + usage + wall.

    Returns dict with keys: text, model, input_tokens, output_tokens,
    wall_clock_s.
    """
    from anthropic import Anthropic
    client = Anthropic()
    t0 = time.time()
    resp = client.messages.create(
        model=STEP2_VALIDATION_MODEL,
        max_tokens=STEP2_VALIDATION_MAX_TOKENS,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    text_chunks = [b.text for b in resp.content if hasattr(b, "text")]
    return {
        "text": "".join(text_chunks),
        "model": STEP2_VALIDATION_MODEL,
        "input_tokens": resp.usage.input_tokens,
        "output_tokens": resp.usage.output_tokens,
        "wall_clock_s": round(time.time() - t0, 2),
    }


def _parse_json_response(text: str) -> dict[str, Any]:
    """Extract JSON from a model response. Tolerant of code fences + prose."""
    # Try fenced code block first
    fenced = re.search(r"```(?:json)?\s*\n(.+?)\n```", text, re.DOTALL)
    if fenced:
        return json.loads(fenced.group(1))
    # Fall back to first {…} blob
    blob = re.search(r"\{.+\}", text, re.DOTALL)
    if blob:
        return json.loads(blob.group(0))
    raise ValueError(f"No JSON found in response: {text[:300]}")


def _render_field(value: Any) -> str:
    """Render a card field value for prompt inclusion (string passthrough,
    list/dict pretty-print as JSON)."""
    if isinstance(value, str):
        return value
    return json.dumps(value, indent=2, ensure_ascii=False)


# --- Pillar 1: Safeguards ----------------------------------------------

def check_safeguards(
    artifact_text: str,
    card: dict[str, Any],
) -> dict[str, Any]:
    """Safeguards pillar — would publishing this hurt the project?

    Hard-coded universal rules (not in any card field):
      - AI-self-acknowledgment ("as a language model", etc.) → HOLD
      - Defamation risk re: living attendees → HOLD

    Per-voice card fields:
      - knowledge_boundary, voice_temporal_stance — frame violations
      - topics_requiring_care → HOLD if breached
      - hard_limits → WARN if breached
      - banned_modes → WARN
      - banned_language (filtered to AI-slop subset only) → WARN
      - translation_protocol → context for what "translated" means
    """
    system = load_prompt("voice_step2_validation_safeguards")
    # Filter banned_language to the AI-slop subset.
    voice_banned_language = card.get("banned_language") or []
    if isinstance(voice_banned_language, str):
        voice_banned_language = [voice_banned_language]
    ai_slop_filtered = [
        item for item in voice_banned_language
        if any(slop in str(item).lower() for slop in _AI_SLOP_LEXICON)
    ]

    user = (
        f"### voice_temporal_stance\n{_render_field(card.get('voice_temporal_stance'))}\n\n"
        f"### knowledge_boundary\n{_render_field(card.get('knowledge_boundary'))}\n\n"
        f"### topics_requiring_care\n{_render_field(card.get('topics_requiring_care'))}\n\n"
        f"### hard_limits\n{_render_field(card.get('hard_limits'))}\n\n"
        f"### banned_modes\n{_render_field(card.get('banned_modes'))}\n\n"
        f"### banned_language (AI-slop subset of voice's full ban list)\n{_render_field(ai_slop_filtered)}\n\n"
        f"### translation_protocol\n{_render_field(card.get('translation_protocol'))}\n\n"
        f"---\n\n"
        f"### artifact_text (the published unit)\n{artifact_text}\n"
    )
    call = _call_anthropic(system=system, user=user)
    parsed = _parse_json_response(call["text"])
    parsed["_call"] = {
        "model": call["model"],
        "input_tokens": call["input_tokens"],
        "output_tokens": call["output_tokens"],
        "wall_clock_s": call["wall_clock_s"],
    }
    return parsed


# --- Pillar 2: Engagement ----------------------------------------------

def _check_length_compliance(
    artifact_text: str,
    card: dict[str, Any],
) -> dict[str, Any] | None:
    """Mechanical length check (no LLM call). Returns issue dict if out
    of range, None if within bounds."""
    constraints = card.get("length_and_format_constraints") or {}
    if isinstance(constraints, str):
        return None  # no machine-readable range
    word_count = len(artifact_text.split())
    # Try common shapes for the range: {min, max} or {target, range}
    lo = (
        constraints.get("min_words")
        or constraints.get("min")
        or (constraints.get("range") or [None, None])[0]
    )
    hi = (
        constraints.get("max_words")
        or constraints.get("max")
        or (constraints.get("range") or [None, None])[1]
    )
    if lo is None or hi is None:
        return None
    if not isinstance(lo, (int, float)) or not isinstance(hi, (int, float)):
        return None
    if word_count < lo:
        return {
            "declared_range": [int(lo), int(hi)],
            "actual_words": word_count,
            "verdict": "under",
            "why": f"artifact is {word_count} words; below floor of {int(lo)}",
        }
    if word_count > hi:
        return {
            "declared_range": [int(lo), int(hi)],
            "actual_words": word_count,
            "verdict": "over",
            "why": f"artifact is {word_count} words; over ceiling of {int(hi)}",
        }
    return None


def check_engagement(
    artifact_text: str,
    card: dict[str, Any],
    lineage: dict[str, Any],
) -> dict[str, Any]:
    """Engagement pillar — would the reader read this?

    Per-voice card fields:
      - medium, characteristic_output_structure — form fidelity
      - length_and_format_constraints — mechanical length compliance

    Cross-cutting:
      - lineage.grounding_extraction_ids + session names — grounding fidelity
    """
    system = load_prompt("voice_step2_validation_engagement")
    grounding_ids = lineage.get("grounding_extraction_ids", []) or []
    session_ids = lineage.get("session_ids", []) or []
    user = (
        f"### medium\n{_render_field(card.get('medium'))}\n\n"
        f"### characteristic_output_structure\n{_render_field(card.get('characteristic_output_structure'))}\n\n"
        f"### grounding_extraction_ids (Researcher extractions the voice was given)\n"
        f"{_render_field(grounding_ids)}\n\n"
        f"### source sessions (panel transcripts grounding extractions came from)\n"
        f"{_render_field(session_ids)}\n\n"
        f"---\n\n"
        f"### artifact_text (the published unit)\n{artifact_text}\n"
    )
    call = _call_anthropic(system=system, user=user)
    parsed = _parse_json_response(call["text"])
    # Overlay mechanical length check (no LLM cost).
    length_issue = _check_length_compliance(artifact_text, card)
    parsed["length_compliance"] = length_issue
    if length_issue and parsed.get("verdict") == "PASS":
        parsed["verdict"] = "WARN"
    parsed["_call"] = {
        "model": call["model"],
        "input_tokens": call["input_tokens"],
        "output_tokens": call["output_tokens"],
        "wall_clock_s": call["wall_clock_s"],
    }
    return parsed


# --- Pillar 3: Voice fidelity ------------------------------------------

def check_voice_fidelity(
    artifact_text: str,
    card: dict[str, Any],
) -> dict[str, Any]:
    """Voice fidelity pillar — did the voice deliver what its card promised?

    Per-voice card fields:
      - characteristic_moves — signature moves the voice MUST perform
      - quality_criteria — voice's own per-step pass/fail tests
    """
    system = load_prompt("voice_step2_validation_voice_fidelity")
    user = (
        f"### characteristic_moves (signature moves the voice MUST perform)\n"
        f"{_render_field(card.get('characteristic_moves'))}\n\n"
        f"### quality_criteria (voice's self-imposed pass/fail tests)\n"
        f"{_render_field(card.get('quality_criteria'))}\n\n"
        f"---\n\n"
        f"### artifact_text (the published unit)\n{artifact_text}\n"
    )
    call = _call_anthropic(system=system, user=user)
    parsed = _parse_json_response(call["text"])
    parsed["_call"] = {
        "model": call["model"],
        "input_tokens": call["input_tokens"],
        "output_tokens": call["output_tokens"],
        "wall_clock_s": call["wall_clock_s"],
    }
    return parsed


# --- Pillar 2 add-on: Cross-night echo (Night 2+ only) -----------------

def check_cross_night_echo(
    artifact_text: str,
    prior_artifact_text: str,
    continuity_overlay: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Cross-night echo check — does tonight's artifact rehash last night?

    Same form is fine, same voice is fine, same imagery is fine. Flags:
      - mild echo: same imagery + vocabulary, different argument (info-only)
      - moderate echo: same argument structure, different framing (WARN)
      - heavy echo: same paragraphs / core claim verbatim repeated (HOLD)
    """
    system = load_prompt("voice_step2_validation_cross_night_echo")
    overlay_text = (
        _render_field(continuity_overlay)
        if continuity_overlay
        else "(no continuity overlay — voice was given no specific deltas to deliver)"
    )
    user = (
        f"### continuity overlay (deltas voice was instructed to deliver tonight)\n"
        f"{overlay_text}\n\n"
        f"### prior night's artifact (last night's published version)\n"
        f"{prior_artifact_text}\n\n"
        f"---\n\n"
        f"### tonight's artifact (the published unit being checked)\n"
        f"{artifact_text}\n"
    )
    call = _call_anthropic(system=system, user=user)
    parsed = _parse_json_response(call["text"])
    parsed["_call"] = {
        "model": call["model"],
        "input_tokens": call["input_tokens"],
        "output_tokens": call["output_tokens"],
        "wall_clock_s": call["wall_clock_s"],
    }
    return parsed


# --- Orchestrator: run all pillars in parallel --------------------------

def _overall_verdict(
    safeguards: dict[str, Any],
    engagement: dict[str, Any],
    voice_fidelity: dict[str, Any],
    cross_night_echo: dict[str, Any] | None,
) -> tuple[str, str]:
    """Compute the overall verdict + operator recommendation.

    Verdict: PASS | WARN | HOLD (any pillar HOLD → HOLD; any WARN → WARN).
    Recommendation: publish | review | hold_for_regen.
    """
    pillars = [safeguards, engagement, voice_fidelity]
    if cross_night_echo is not None:
        pillars.append(cross_night_echo)
    verdicts = [(p or {}).get("verdict", "PASS") for p in pillars]
    if "HOLD" in verdicts:
        return "HOLD", "hold_for_regen"
    if "WARN" in verdicts:
        return "WARN", "review"
    return "PASS", "publish"


def _load_prior_artifact(
    project_root: Path,
    night: int,
    voice_slug: str,
) -> str | None:
    """Load prior night's published artifact_text. Returns None if N=1
    or the file is missing (Night 1 always has no prior; missing N-1
    file means the prior night didn't publish this voice and we can't
    cross-night-check)."""
    if night <= 1:
        return None
    prior_path = (
        project_root
        / "published_artifacts"
        / "nights"
        / f"night_{night - 1}"
        / f"{voice_slug}.json"
    )
    if not prior_path.exists():
        return None
    try:
        prior = json.loads(prior_path.read_text(encoding="utf-8"))
        return prior.get("artifact_text") or prior.get("body") or None
    except (OSError, json.JSONDecodeError):
        return None


def run_step2_validation(
    step2_artifact: dict[str, Any],
    card: dict[str, Any],
    run_dir: Path,
    *,
    night: int,
    project_root: Path,
) -> dict[str, Any]:
    """Run all three pillars (+ cross-night echo on Night 2+) for one voice.

    Writes per-voice JSON to <run_dir>/04_voice/step2_validation/<voice>.json.
    Returns the combined validation result.
    """
    logger = get_logger("voice_step2_validation")
    voice_slug = step2_artifact["lineage"]["voice_slug"]
    out_dir = run_dir / "04_voice" / "step2_validation"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{voice_slug}.json"
    if out_path.exists():
        with open(out_path, encoding="utf-8") as f:
            return json.load(f)

    artifact_text = step2_artifact["artifact_text"]
    lineage = step2_artifact.get("lineage", {})

    # Cross-night echo inputs (Night 2+ only, gated on prior artifact existing).
    prior_artifact_text = _load_prior_artifact(project_root, night, voice_slug)
    continuity_overlay = card.get(
        f"continuity_block_artifact_if_night_{night}"
    )

    # Run pillars in parallel for wall-time win.
    pillar_calls: dict[str, Any] = {
        "safeguards": (check_safeguards, (artifact_text, card)),
        "engagement": (check_engagement, (artifact_text, card, lineage)),
        "voice_fidelity": (check_voice_fidelity, (artifact_text, card)),
    }
    if prior_artifact_text is not None:
        pillar_calls["cross_night_echo"] = (
            check_cross_night_echo,
            (artifact_text, prior_artifact_text, continuity_overlay),
        )

    results: dict[str, Any] = {}
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=STEP2_VALIDATION_PILLAR_BATCH) as ex:
        futures = {
            ex.submit(fn, *args): name
            for name, (fn, args) in pillar_calls.items()
        }
        for fut in as_completed(futures):
            name = futures[fut]
            try:
                results[name] = fut.result()
            except Exception as e:  # noqa: BLE001
                logger.error(f"  Step 2 validation pillar {name} failed for {voice_slug}: {e}")
                results[name] = {
                    "verdict": "WARN",
                    "_error": str(e),
                }

    safeguards = results.get("safeguards", {})
    engagement = results.get("engagement", {})
    voice_fidelity = results.get("voice_fidelity", {})
    cross_night = results.get("cross_night_echo")
    overall, recommendation = _overall_verdict(
        safeguards, engagement, voice_fidelity, cross_night
    )

    final = {
        "schema_version": "1.0",
        "voice_slug": voice_slug,
        "night": night,
        "overall_verdict": overall,
        "operator_recommendation": recommendation,
        "safeguards": safeguards,
        "engagement": engagement,
        "voice_fidelity": voice_fidelity,
        "cross_night_echo": cross_night,
        "wall_clock_s": round(time.time() - t0, 2),
    }
    write_json_atomic(out_path, final)
    logger.info(
        f"  Step 2 validation: {voice_slug} → {overall} "
        f"(reco: {recommendation}, wall {final['wall_clock_s']}s)"
    )
    return final
