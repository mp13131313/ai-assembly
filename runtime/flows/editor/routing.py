"""Editor Pipeline — Stage 1: deterministic theme routing.

Per docs/AI_Assembly_Editor_Pipeline.md §"Stage 1 — Theme Routing", with
contract refinements from `_workspace/planning/runtime/MEMO_2026_05_03_editor_flow_input_output_contract.md`:

  - Each voice's Step 2 artifact is routed to ONE dossier (its primary_theme).
  - "In Brief" cross-dossier mentions DROPPED per memo §1 — each theme's
    dossier shows only its engaged voices; no cross-references.
  - Lead-theme is operator/layout decision per memo §8.1 — runtime computes
    a deterministic default order (most-contributors first, theme_id tiebreak)
    that operator can override by hand-editing theme_routing.json before
    Stage 2 fires.
  - Refusals are tracked as a flat list (microsite index surface), NOT routed
    to a per-dossier In Brief column.

Inputs (read fresh each night):
  <run_dir>/04_voice/step2_first_draft_artifacts/*.json
  <run_dir>/03_provocateur/briefings/<voice>.json (ordered formulations)

Output:
  <run_dir>/05_editor/theme_routing.json

Algorithm (per voice's Step 2 artifact):
  Case 1 — "Focus on Response N":
      primary_theme = the Nth theme_id in voice's briefings (1-indexed)
  Case 2 — "synthesise / synthesize / weave across all":
      primary_theme = lowest-numbered theme_id in voice's themes_covered
  Case 3 — anything else:
      primary_theme = lowest-numbered theme_id in voice's themes_covered
      log warning; flag for operator review

Refusals (silence, refusal-of-receiving) are detected by:
  - empty themes_covered, OR
  - focus_decision matching refusal markers
Refusals do NOT receive a primary_theme; they're collected separately.

This module is purely deterministic — no LLM call. Operator overrides are
honored by hand-editing the resulting theme_routing.json.
"""

from __future__ import annotations

import json
import logging
import re
import sys
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from flows.shared.io import write_json_atomic  # noqa: E402


REFUSAL_MARKERS = (
    "refused",
    "silence",
    "decline",
    "declines",
    "not-receiving",
    "not receiving",
    "refusal-of-receiving",
    "refusal of receiving",
)


def _is_refusal(focus_decision: str, themes_covered: list[str]) -> bool:
    """A voice has refused if its themes_covered is empty OR its
    focus_decision text contains a refusal marker."""
    if not themes_covered:
        return True
    fd = (focus_decision or "").lower().strip()
    return any(marker in fd for marker in REFUSAL_MARKERS)


# v2 regex: matches "Response N" ANYWHERE in focus_decision text. Catches
# "Focus on Response 3", "Focus on response 2 (algorithmic governance)",
# AND "synthesise around Response 2's threshold-scene" (synthesis-anchored
# hybrid). Per spec v2 §"Stage 1 — Theme Routing".
_RESPONSE_N_RE = re.compile(
    r"response\s*(\d+)",
    re.IGNORECASE,
)

SYNTHESIS_MARKERS = (
    "synthesise",
    "synthesize",
    "weave across all",
    "weave",
    "across all",
    "synthesis",
)

# Single-response markers — voices that received exactly one Step 1 output
# may write "Single focus on this response" or "Focus on the single
# response" rather than "Focus on Response 1", because there's no Response 2
# to disambiguate against. When themes_covered has length 1, this resolves
# without ambiguity.
_SINGLE_RESPONSE_MARKERS = (
    "single focus on this response",
    "focus on the single response",
    "single response",
    "the single response",
    "this response",
    "the only response",
    "the lone response",
)


def _parse_focus_to_primary_theme(
    focus_decision: str,
    briefings: list[dict[str, Any]] | None,
    themes_covered: list[str],
    *,
    artifact_lineage: dict[str, Any] | None = None,
    artifact_text: str = "",
    synthesis_client: Any | None = None,
    voice_slug: str = "",
    logger: logging.Logger | None = None,
) -> tuple[str, str]:
    """Returns (primary_theme_id, source_label).

    Authoritative path (post-2026-05-04): if Step 2 wrote `lineage.
    primary_theme_id` (resolved at write time using the actual order the
    voice saw step1_outputs), use that directly. Falls back to the
    Response-N parser against briefings[] for older artifacts that
    pre-date the resolved field.

    Synthesis path (Case 2): if focus_decision matches synthesis markers
    AND the voice covered >=2 themes AND `synthesis_client` is provided,
    delegate to synthesis_router.route_synthesis_voice — one Sonnet call
    that reads the artifact + each candidate theme's title/abstract/
    formulation and decides which theme this synthesis lands on. If the
    client is None (unit-test path) or the call fails, falls back to
    lowest-numbered.
    """
    fd = (focus_decision or "").strip()
    fd_lower = fd.lower()

    # Authoritative resolution from Step 2's write-time mapping.
    if artifact_lineage:
        ptid = artifact_lineage.get("primary_theme_id")
        if ptid:
            return ptid, "Case A — Step 2 resolved primary_theme_id (authoritative)"

    # Legacy fallback: parse "Response N" against briefings[N-1] order.
    # Fragile because briefings[] order may not match the order the voice
    # saw — kept only for back-compat with pre-resolved-field artifacts.
    m = _RESPONSE_N_RE.search(fd_lower)
    if m and briefings:
        n = int(m.group(1))
        if 1 <= n <= len(briefings):
            theme_id = briefings[n - 1].get("theme_id")
            if theme_id:
                return theme_id, "Case A (legacy) — Response N parsed against briefings order"

    # Case B — single-response session: the voice received exactly one
    # Step 1 output and wrote "Single focus on this response" /
    # "Focus on the single response" / similar. Unambiguous because
    # themes_covered has length 1.
    if (
        len(themes_covered) == 1
        and any(marker in fd_lower for marker in _SINGLE_RESPONSE_MARKERS)
    ):
        return (
            themes_covered[0],
            "Case B — single-response session (only one theme covered)",
        )

    is_synthesis = any(marker in fd_lower for marker in SYNTHESIS_MARKERS)

    if is_synthesis and themes_covered:
        # Single theme covered → no choice to make; skip the LLM call.
        if len(themes_covered) == 1:
            return themes_covered[0], "Case 2 — synthesis, single theme covered"
        if synthesis_client is not None:
            from flows.editor.synthesis_router import route_synthesis_voice
            candidates = []
            for tid in themes_covered:
                # Find the briefing entry for this theme to pull display
                # title / abstract / formulation. briefings[] is the per-
                # voice list of formulations; each entry's theme_id matches
                # one candidate. Skip themes the voice never saw a briefing
                # for (defensive — should not happen).
                bf = next(
                    (b for b in (briefings or []) if b.get("theme_id") == tid),
                    None,
                )
                if not bf:
                    continue
                ftr = bf.get("full_theme_record", {}) or {}
                candidates.append({
                    "theme_id": tid,
                    "theme_display_title": (
                        bf.get("theme_display_title")
                        or ftr.get("theme_display_title")
                        or ""
                    ),
                    "theme_abstract_from_researcher": ftr.get(
                        "theme_abstract_from_researcher", ""
                    ),
                    "narrative_briefing": bf.get("narrative_briefing", ""),
                    "cluster_titles": [
                        c.get("cluster_title", "")
                        for c in (ftr.get("clusters") or [])
                    ],
                })
            if candidates:
                chosen, rationale = route_synthesis_voice(
                    voice_slug=voice_slug,
                    artifact_text=artifact_text,
                    candidates=candidates,
                    client=synthesis_client,
                    logger=logger,
                )
                if chosen:
                    return chosen, f"Case 2 — synthesis (LLM-routed): {rationale}"
        # synthesis_client is None (unit-test path) OR the router fell
        # through with no chosen — keep deterministic lowest-numbered.
        return (
            sorted(themes_covered)[0],
            "Case 2 — synthesis, lowest-numbered tiebreaker (no router available)",
        )

    if themes_covered:
        return (
            sorted(themes_covered)[0],
            "Case 3 — fall-through (parser couldn't extract); operator review",
        )

    return ("", "Case 3 — no themes_covered; refusal handling expected")


def _load_held_voices(run_dir: Path) -> set[str]:
    """Voices the operator marked `hold_for_regen` per C28b. Excluded
    from dossier composition + publish."""
    dec_dir = run_dir / "04_voice" / "operator_decisions"
    if not dec_dir.exists():
        return set()
    held: set[str] = set()
    for p in sorted(dec_dir.glob("*.json")):
        try:
            with p.open(encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError):
            continue
        if data.get("decision") == "hold_for_regen":
            held.add(data.get("voice_slug") or p.stem)
    return held


def _load_step2_artifacts(run_dir: Path) -> list[dict[str, Any]]:
    s2_dir = run_dir / "04_voice" / "step2_first_draft_artifacts"
    if not s2_dir.exists():
        return []
    held = _load_held_voices(run_dir)
    out = []
    for p in sorted(s2_dir.glob("*.json")):
        with p.open(encoding="utf-8") as f:
            artifact = json.load(f)
        slug = artifact.get("lineage", {}).get("voice_slug") or p.stem
        if slug in held:
            continue  # C28b: operator held this voice for regen — skip
        out.append(artifact)
    return out


def _load_briefings(run_dir: Path) -> dict[str, list[dict[str, Any]]]:
    """voice_slug → ordered list of formulations for that voice."""
    bdir = run_dir / "03_provocateur" / "briefings"
    if not bdir.exists():
        return {}
    out = {}
    for p in sorted(bdir.glob("*.json")):
        with p.open(encoding="utf-8") as f:
            data = json.load(f)
        out[p.stem] = data.get("formulations", []) or []
    return out


def _theme_titles_from_briefings(
    briefings_by_voice: dict[str, list[dict[str, Any]]],
) -> dict[str, str]:
    """theme_id → display title, populated from any briefing that touched it."""
    out: dict[str, str] = {}
    for forms in briefings_by_voice.values():
        for f in forms:
            tid = f.get("theme_id")
            title = f.get("theme_display_title") or f.get("theme_title")
            if tid and title and tid not in out:
                out[tid] = title
    return out


def _voice_name_lookup(artifacts: list[dict[str, Any]]) -> dict[str, str]:
    """voice_slug → council_member_name from Step 2 artifacts."""
    out = {}
    for a in artifacts:
        slug = a.get("lineage", {}).get("voice_slug")
        name = a.get("council_member") or slug
        if slug:
            out[slug] = name
    return out


def route_themes(
    run_dir: Path,
    night: int,
    *,
    dossier_lead_order: list[str] | None = None,
    synthesis_client: Any | None = None,
    logger: logging.Logger | None = None,
) -> dict[str, Any]:
    """Build the theme_routing.json payload for one night.

    `dossier_lead_order`: optional explicit list of theme_ids in publication
    order (lead dossier first). If None, the deterministic default is
    most-contributors-first with theme_id ascending tiebreak. Operator can
    override by hand-editing the resulting manifest before Stage 2 fires.

    `synthesis_client`: optional Anthropic client used by the synthesis
    router (Case 2). If None, synthesis voices fall back to the legacy
    lowest-numbered tiebreaker — kept that way so unit tests don't need
    a mocked client.

    Returns the routing manifest dict.
    """
    log = logger or logging.getLogger("editor_routing")

    artifacts = _load_step2_artifacts(run_dir)
    briefings_by_voice = _load_briefings(run_dir)
    voice_names = _voice_name_lookup(artifacts)
    theme_titles = _theme_titles_from_briefings(briefings_by_voice)

    voices_routing: list[dict[str, Any]] = []
    refusals: list[dict[str, Any]] = []

    # Pass 1 — classify each artifact as primary-routed or refusal.
    for a in artifacts:
        lineage = a.get("lineage", {}) or {}
        slug = lineage.get("voice_slug")
        if not slug:
            log.warning(
                f"Step 2 artifact missing lineage.voice_slug — skipping: {a}"
            )
            continue
        themes_covered = lineage.get("themes_covered", []) or []
        focus_decision = a.get("focus_decision", "") or ""

        if _is_refusal(focus_decision, themes_covered):
            refusals.append({
                "voice_slug": slug,
                "voice_name": voice_names.get(slug, slug),
                "form": a.get("selected_form") or "refusal",
                "focus_decision": focus_decision,
            })
            continue

        primary_theme, source_label = _parse_focus_to_primary_theme(
            focus_decision,
            briefings_by_voice.get(slug),
            themes_covered,
            artifact_lineage=lineage,
            artifact_text=a.get("artifact_text", "") or "",
            synthesis_client=synthesis_client,
            voice_slug=slug,
            logger=log,
        )
        if not primary_theme:
            log.warning(
                f"Could not determine primary_theme for {slug}; "
                f"focus_decision={focus_decision!r}, themes_covered={themes_covered}"
            )
            continue
        if source_label.startswith("Case 3"):
            log.warning(
                f"{slug}: parser fall-through; primary={primary_theme}; "
                f"focus_decision={focus_decision!r}"
            )

        voices_routing.append({
            "voice_slug": slug,
            "voice_name": voice_names.get(slug, slug),
            "primary_theme": primary_theme,
            "focus_decision_parsed": focus_decision,
            "primary_theme_source": source_label,
        })

    # Pass 2 — assemble themes_to_dossiers + dossier_lead_order default.
    contributors_by_theme: dict[str, int] = {}
    for v in voices_routing:
        contributors_by_theme[v["primary_theme"]] = (
            contributors_by_theme.get(v["primary_theme"], 0) + 1
        )

    if dossier_lead_order is None:
        dossier_lead_order = [
            tid for tid, _ in sorted(
                contributors_by_theme.items(),
                key=lambda kv: (-kv[1], kv[0]),
            )
        ]
    else:
        missing = [
            tid for tid in sorted(contributors_by_theme.keys())
            if tid not in dossier_lead_order
        ]
        if missing:
            log.warning(
                f"dossier_lead_order missed contributing themes: {missing} "
                f"— appending in default order"
            )
            dossier_lead_order = list(dossier_lead_order) + sorted(
                missing, key=lambda t: (-contributors_by_theme.get(t, 0), t)
            )

    themes_to_dossiers = []
    theme_to_dossier_no: dict[str, int] = {}
    for i, tid in enumerate(dossier_lead_order, start=1):
        themes_to_dossiers.append({
            "theme_id": tid,
            "dossier_no": i,
            "theme_title": theme_titles.get(tid, tid),
            "n_engaged_voices": contributors_by_theme.get(tid, 0),
        })
        theme_to_dossier_no[tid] = i

    # Stamp dossier_no on each voice routing entry.
    for v in voices_routing:
        v["primary_dossier"] = theme_to_dossier_no.get(v["primary_theme"], 0)

    voices_routing.sort(key=lambda v: (v["primary_dossier"], v["voice_slug"]))

    return {
        "schema_version": "1.0",
        "night": night,
        "themes_to_dossiers": themes_to_dossiers,
        "voices_routing": voices_routing,
        "refusals": refusals,
        "dossier_lead_order_default": [
            t["dossier_no"] for t in themes_to_dossiers
        ],
    }


def write_routing_manifest(
    run_dir: Path,
    night: int,
    *,
    dossier_lead_order: list[str] | None = None,
    synthesis_client: Any | None = None,
    logger: logging.Logger | None = None,
) -> dict[str, Any]:
    """Compute + write theme_routing.json. Returns the manifest dict.

    `synthesis_client`: optional Anthropic client for synthesis routing.
    Pass-through to route_themes; see its docstring.
    """
    manifest = route_themes(
        run_dir, night,
        dossier_lead_order=dossier_lead_order,
        synthesis_client=synthesis_client,
        logger=logger,
    )
    out_dir = run_dir / "05_editor"
    out_dir.mkdir(parents=True, exist_ok=True)
    write_json_atomic(out_dir / "theme_routing.json", manifest)
    return manifest
