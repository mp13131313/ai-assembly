"""Editor Pipeline — synthesis-routing helper.

When a voice's Step 2 artifact is a synthesis ("woven across all", "synthesise
across", etc.), Step 2 leaves `lineage.primary_theme_id` null because no
single Response-N anchors the artifact. The editor's Stage 1 router used to
fall through to a lowest-numbered tiebreaker on `themes_covered` — arbitrary
and weighted nothing about the synthesis itself.

This module replaces that tiebreaker with one Anthropic call: read the
artifact alongside each candidate theme's display title + Researcher
abstract + the formulation the voice received for that theme, and decide
which theme this artifact primarily lands on. Returns the chosen theme_id
and a one-sentence rationale for audit.

Cost envelope:
  - Sonnet 4.6, no thinking (this is a routing decision, not a composition
    task — extended reasoning isn't earning its keep here).
  - Per call: ~3-6K input tokens, ~50 output tokens. ~$0.05/voice.
  - Synthesis voices per night ≈ 0-2; ~$0.10/night ceiling.
  - System prompt is constant per night so it caches; effective cost lower.

Failure mode: if the call errors after retry, OR the response can't be
parsed, the caller falls back to lowest-numbered (the old Case 2 behavior)
so routing always lands somewhere — synthesis voices never get dropped on
the floor over a transient API error.
"""
from __future__ import annotations

import json
import logging
import os
import re
from typing import Any

# Sonnet 4.6 is sufficient — small comprehension task, deterministic-ish
# pick from a list. Adaptive thinking off (no extended reasoning needed
# for this pattern-matching call); keeps it cheap and fast.
SYNTHESIS_ROUTER_MODEL = os.environ.get(
    "SYNTHESIS_ROUTER_MODEL", "claude-sonnet-4-6"
)
SYNTHESIS_ROUTER_MAX_TOKENS = int(
    os.environ.get("SYNTHESIS_ROUTER_MAX_TOKENS", "500")
)

_SYSTEM_PROMPT = """You are a deterministic routing helper for a multi-voice editorial pipeline.

You receive ONE synthesis artifact a voice wrote across multiple themes, plus the candidate themes (each with its display title, Researcher's abstract, and the formulation that voice received for that theme). Decide which single theme the artifact primarily lands on — the theme whose dossier should carry this artifact for the reader.

Decide by emphasis: which theme's question does the artifact most fully answer? Which theme's clusters and speakers does the artifact most concretely engage? When the artifact reframes one theme through another, the reframed-toward theme is primary. The reader who picks up the chosen theme's dossier should find this artifact illuminating their theme's question — not feel it belongs elsewhere.

Output exactly two labelled lines, no preamble, no markdown chrome:

chosen_theme_id: theme_NNN
rationale: <one short sentence — why this theme over the others>

Do not output anything else."""


_CHOSEN_RE = re.compile(
    r"^\s*chosen[_\s]*theme[_\s]*id\s*[:=]\s*(\S+)\s*$",
    re.IGNORECASE | re.MULTILINE,
)
_RATIONALE_RE = re.compile(
    r"^\s*rationale\s*[:=]\s*(.+?)\s*$",
    re.IGNORECASE | re.MULTILINE,
)


def _build_user_prompt(
    voice_slug: str,
    artifact_text: str,
    candidates: list[dict[str, Any]],
) -> str:
    payload = {
        "voice_slug": voice_slug,
        "artifact_text": artifact_text,
        "candidate_themes": [
            {
                "theme_id": c["theme_id"],
                "theme_display_title": c.get("theme_display_title", ""),
                "theme_abstract_from_researcher": c.get(
                    "theme_abstract_from_researcher", ""
                ),
                "narrative_briefing_received_by_this_voice": c.get(
                    "narrative_briefing", ""
                ),
                "cluster_titles": c.get("cluster_titles", []),
            }
            for c in candidates
        ],
    }
    return (
        "Decide which theme this synthesis artifact primarily lands on.\n\n"
        f"```json\n{json.dumps(payload, indent=2, ensure_ascii=False)}\n```"
    )


def route_synthesis_voice(
    *,
    voice_slug: str,
    artifact_text: str,
    candidates: list[dict[str, Any]],
    client: Any,
    logger: logging.Logger | None = None,
) -> tuple[str, str]:
    """Run the synthesis-routing call. Returns (theme_id, rationale).

    `candidates` is a list of dicts with keys:
        theme_id, theme_display_title, theme_abstract_from_researcher,
        narrative_briefing, cluster_titles[].

    On any failure (API error after retry, parser failure, model returns
    a theme_id not in candidates), returns the lowest-numbered candidate
    with a rationale string explaining the fallback. Caller can log it.
    """
    log = logger or logging.getLogger("synthesis_router")
    candidate_ids = [c["theme_id"] for c in candidates]
    if not candidate_ids:
        return ("", "synthesis-router: no candidates")
    fallback_id = sorted(candidate_ids)[0]

    user_prompt = _build_user_prompt(voice_slug, artifact_text, candidates)

    try:
        message = client.messages.create(
            model=SYNTHESIS_ROUTER_MODEL,
            max_tokens=SYNTHESIS_ROUTER_MAX_TOKENS,
            system=_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )
    except Exception as exc:
        log.warning(
            f"synthesis_router({voice_slug}): API call failed "
            f"({type(exc).__name__}: {exc}); falling back to "
            f"lowest-numbered={fallback_id}"
        )
        return (fallback_id, f"synthesis-router fallback (API error): {type(exc).__name__}")

    try:
        text = "".join(
            getattr(b, "text", "") for b in (message.content or [])
            if getattr(b, "type", "") == "text"
        )
    except Exception:
        text = ""

    chosen = (_CHOSEN_RE.search(text) or [None, ""])
    chosen_id = chosen[1].strip() if chosen and chosen[1] else ""
    rationale = (_RATIONALE_RE.search(text) or [None, ""])
    rationale_str = rationale[1].strip() if rationale and rationale[1] else ""

    if chosen_id not in candidate_ids:
        log.warning(
            f"synthesis_router({voice_slug}): model returned "
            f"chosen_theme_id={chosen_id!r} not in candidates {candidate_ids}; "
            f"falling back to lowest-numbered={fallback_id}. "
            f"Raw response: {text[:200]!r}"
        )
        return (fallback_id, "synthesis-router fallback (model returned unknown theme_id)")

    log.info(
        f"synthesis_router({voice_slug}): chose {chosen_id} — {rationale_str}"
    )
    return (chosen_id, rationale_str or "synthesis-router (no rationale captured)")
