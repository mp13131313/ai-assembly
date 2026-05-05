"""Editor Pipeline — Stage 2: per-dossier Anthropic call.

Per spec v2 §"Stage 2 — Per-call inputs". For each engaged theme, fire one
Anthropic call. The call:

  1. System prompt: Claudia's persona card + closing prompt (cached across
     the night's per-dossier calls; 1h TTL).
  2. User prompt: structured JSON with the deduped theme block +
     engaged_voices (each with mode + narrative_briefing + artifact_text)
     + prior_editions on Night 2/3.
  3. Output: prose-and-parse — Claudia emits fields with labels; runtime
     parses into the v2 dossier schema.

Per-dossier briefing assembly combines K voice briefings into one
deduplicated dossier briefing (theme block deduped; per-voice formulation +
artifact kept all N) — the voices' briefings each carry an identical
`full_theme_record`, so Provocateur is a passthrough on theme metadata.

This module reuses `voice/_anthropic_call.stream_voice_call` for the actual
streaming + retry-once + prefix-cache wiring (same infrastructure as voice
pipeline).

Note: the closing prompt at `runtime/flows/shared/prompts/editor_dossier.md`
is currently v1-shaped. Until it's rewritten to v2 (per OPEN_ITEMS B1), the
output parser will not extract clean v2 fields from real model responses.
Tests use mocked Anthropic responses to validate the parser independently.
"""

from __future__ import annotations

import json
import logging
import os
import re
import sys
import time
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from flows.shared.io import write_json_atomic  # noqa: E402
from flows.voice._anthropic_call import stream_voice_call  # noqa: E402


EDITOR_MODEL = os.environ.get(
    "EDITOR_MODEL",
    os.environ.get("CLAUDE_MODEL", "claude-opus-4-7"),
)
EDITOR_THINKING = os.environ.get("EDITOR_THINKING", "1") != "0"
EDITOR_MAX_TOKENS = int(os.environ.get("EDITOR_MAX_TOKENS", "32000"))


# Newspaper-masthead chrome (Vol. CXVI / Issue No. 42,193 / Late Night
# Edition / publication_date_long) was dropped 2026-05-05 — the dossier
# is published under House of Beautiful Business, not as a fictional
# newspaper. Night number is the only temporal anchor that survives.


def _thinking_kwargs() -> dict:
    """Adaptive thinking, summarized display. Mirrors voice pipeline pattern."""
    if not EDITOR_THINKING:
        return {}
    return {"thinking": {"type": "adaptive", "display": "summarized"}}


# --- Dossier briefing assembly --------------------------------------------


def _read_briefing_formulation(
    voice_slug: str,
    theme_id: str,
    run_dir: Path,
) -> dict[str, Any]:
    """Open the voice's briefing file; return the formulation entry whose
    theme_id matches. Raises StopIteration if no match (a routing bug)."""
    path = run_dir / "03_provocateur" / "briefings" / f"{voice_slug}.json"
    with path.open(encoding="utf-8") as f:
        briefing = json.load(f)
    return next(
        f for f in briefing.get("formulations", [])
        if f.get("theme_id") == theme_id
    )


def _read_artifact(voice_slug: str, run_dir: Path) -> dict[str, Any]:
    path = run_dir / "04_voice" / "step2_first_draft_artifacts" / f"{voice_slug}.json"
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def build_dossier_briefing(
    theme_id: str,
    voice_slugs: list[str],
    run_dir: Path,
    *,
    night: int,
    prior_editions: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Combine K voice briefings + K Step 2 artifacts into ONE deduplicated
    dossier briefing per spec v2 §"Stage 2 — Per-call inputs".

    Theme block (deduped from briefings): theme_id, theme_display_title,
    theme_title_from_researcher, theme_abstract_from_researcher, clusters
    (with full extraction text), theme_flags. Identical across the K
    briefings since Provocateur is a passthrough on theme metadata.

    Per-voice (kept all K): voice_slug, voice_name, mode, narrative_briefing,
    artifact_text. The artifact is what Claudia frames; the formulation is
    the question that voice received; the mode distinguishes question /
    proposition framings.

    Caller (`run_editor_dossier`) is responsible for passing voice_slugs
    consistent with `theme_routing.json.voices_routing[].primary_theme`.
    """
    if not voice_slugs:
        raise ValueError(
            f"No voices routed to theme_id={theme_id}; can't build briefing"
        )

    briefings = [_read_briefing_formulation(slug, theme_id, run_dir) for slug in voice_slugs]
    artifacts = [_read_artifact(slug, run_dir) for slug in voice_slugs]

    # All briefings carry identical full_theme_record — take the first.
    ftr = briefings[0]["full_theme_record"]
    theme = {
        "theme_id":                       briefings[0]["theme_id"],
        "theme_display_title":            briefings[0]["theme_display_title"],
        "theme_title_from_researcher":    ftr.get("theme_title_from_researcher", ""),
        "theme_abstract_from_researcher": ftr.get("theme_abstract_from_researcher", ""),
        "clusters":                       ftr.get("clusters", []),
        "theme_flags":                    ftr.get("theme_flags", {}),
    }

    engaged_voices = [
        {
            "voice_slug":         slug,
            "voice_name":         "the Voice of " + artifact.get("council_member", slug),
            "mode":               briefing.get("mode", "question"),
            "narrative_briefing": briefing.get("narrative_briefing", ""),
            "artifact_text":      artifact.get("artifact_text", ""),
            # selected_form (the night's chosen form — "prostagma", "rihla",
            # "dialogue", etc.) → microsite uses this as the CSS-bundle key
            # for per-voice rendering of the artifact body. Threaded through
            # to stamp_runtime_fields → dossier headnote so the dossier is
            # self-contained.
            "selected_form":      artifact.get("selected_form", ""),
        }
        for slug, briefing, artifact in zip(voice_slugs, briefings, artifacts)
    ]

    return {
        "night": night,
        "theme": theme,
        "engaged_voices": engaged_voices,
        "prior_editions": prior_editions or [],
    }


def build_user_prompt(dossier_briefing: dict[str, Any]) -> str:
    """Render the dossier briefing as a JSON-shaped user prompt.

    The closing instruction (in `editor_dossier.md`, in the system tail)
    explains the schema to Claudia. Voice pipeline uses a similar
    JSON-in-user-prompt pattern.
    """
    return (
        "You are receiving the materials for one dossier. Read them and write "
        "the dossier per the instructions in your system message.\n\n"
        f"```json\n{json.dumps(dossier_briefing, indent=2, ensure_ascii=False)}\n```"
    )


# --- Output parsing -------------------------------------------------------


# v2 output schema: kicker, headline, subline, front_abstract,
# theme_title_for_dossier, theme_abstract_for_dossier, body_paragraphs[],
# headnotes[]. Parser uses the same `**Label:** value` pattern as voice
# pipeline; multi-line fields (body_paragraphs) parse as one block then
# split on a separator.
#
# theme_title_for_dossier + theme_abstract_for_dossier added 2026-05-04 PM:
# Claudia reads the Researcher's theme record and writes a publishing-
# register short title + abstract specifically for the dossier's Page 3.
# The `_for_dossier` suffix follows the convention pattern
# (`theme_title_from_researcher` etc.) — names the field by what it's
# FOR rather than where it CAME FROM, so a future consumer reading both
# Researcher's source theme + Editor's dossier-render version side-by-
# side won't confuse the two.

_FIELD_LABEL_RE = {
    "kicker":                     re.compile(r"^\s*[*_#\-]*\s*kicker\s*[*_]*\s*[:=]\s*(.+?)(?=\n\s*[*_#\-]+\s*[a-z][a-z_]+|\Z)", re.I | re.M | re.S),
    "headline":                   re.compile(r"^\s*[*_#\-]*\s*headline\s*[*_]*\s*[:=]\s*(.+?)(?=\n\s*[*_#\-]+\s*[a-z][a-z_]+|\Z)", re.I | re.M | re.S),
    "subline":                    re.compile(r"^\s*[*_#\-]*\s*subline\s*[*_]*\s*[:=]\s*(.+?)(?=\n\s*[*_#\-]+\s*[a-z][a-z_]+|\Z)", re.I | re.M | re.S),
    "front_abstract":             re.compile(r"^\s*[*_#\-]*\s*front[_\s]*abstract\s*[*_]*\s*[:=]\s*(.+?)(?=\n\s*[*_#\-]+\s*[a-z][a-z_]+|\Z)", re.I | re.M | re.S),
    "theme_title_for_dossier":    re.compile(r"^\s*[*_#\-]*\s*theme[_\s]*title[_\s]*for[_\s]*dossier\s*[*_]*\s*[:=]\s*(.+?)(?=\n\s*[*_#\-]+\s*[a-z][a-z_]+|\Z)", re.I | re.M | re.S),
    "theme_abstract_for_dossier": re.compile(r"^\s*[*_#\-]*\s*theme[_\s]*abstract[_\s]*for[_\s]*dossier\s*[*_]*\s*[:=]\s*(.+?)(?=\n\s*[*_#\-]+\s*[a-z][a-z_]+|\Z)", re.I | re.M | re.S),
}


def _strip_chrome(value: str) -> str:
    """Strip leading/trailing markdown chrome (`**`, `*`, `_`)."""
    value = value.strip()
    value = re.sub(r"^[*_]+\s*", "", value).strip()
    value = re.sub(r"\s*[*_]+$", "", value).strip()
    return value


def _parse_body_paragraphs(raw_text: str) -> list[str]:
    """Extract body_paragraphs from the model output.

    Two parsing strategies, in order:
      1. Look for a `body_paragraphs:` label followed by a fenced-or-bare
         block; split on `\\n\\n`.
      2. Look for an `article body:` or `body:` heading and split everything
         after it on blank lines.

    Asterism breaks (`* * *`) survive as their own array elements.
    """
    # Strategy 1
    rx = re.compile(
        r"^\s*[*_#\-]*\s*body[_\s]*paragraphs\s*[*_]*\s*[:=]\s*\n?(.+?)(?=\n\s*[*_#\-]+\s*[a-z][a-z_]+\s*[:=]|\Z)",
        re.I | re.M | re.S,
    )
    m = rx.search(raw_text)
    if not m:
        return []
    body_block = m.group(1).strip()

    # Strip code-fence wrapping if present
    if body_block.startswith("```"):
        body_block = re.sub(r"^```\w*\n?", "", body_block)
        body_block = re.sub(r"\n?```\s*$", "", body_block)

    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", body_block) if p.strip()]
    return paragraphs


def _parse_headnotes(raw_text: str) -> list[dict[str, str]]:
    """Extract headnotes[] — each headnote has voice_slug + artifact_title +
    framing_text.

    Closing prompt format (when rewritten to v2): a `headnotes:` block with,
    per voice, three labelled lines in this order:
        voice_slug:     <slug>
        artifact_title: <4-8 words; voice's register inflects via translation_protocol>
        framing_text:   <1-2 sentences>

    Defensive: missing fields → empty strings, no crash. Pairing is by
    interleaved alternation (slugs / titles / framings parallel arrays).
    """
    rx = re.compile(
        r"^\s*[*_#\-]*\s*headnotes\s*[*_]*\s*[:=]\s*\n?(.+?)(?=\n\s*[*_#\-]+\s*[a-z][a-z_]+\s*[:=]|\Z)",
        re.I | re.M | re.S,
    )
    m = rx.search(raw_text)
    if not m:
        return []
    block = m.group(1)

    slugs = re.findall(r"voice[_\s]*slug\s*[:=]\s*(.+?)(?:\n|$)", block, re.I)
    titles = re.findall(
        r"artifact[_\s]*title\s*[:=]\s*(.+?)(?:\n|$)",
        block, re.I,
    )
    framings = re.findall(
        r"framing[_\s]*text\s*[:=]\s*(.+?)(?=\n\s*voice[_\s]*slug|\n\s*artifact[_\s]*title|\Z)",
        block, re.I | re.S,
    )
    out = []
    n = len(slugs)
    for i, slug in enumerate(slugs):
        out.append({
            "voice_slug":     _strip_chrome(slug),
            "artifact_title": _strip_chrome(titles[i]) if i < len(titles) else "",
            "framing_text":   _strip_chrome(framings[i]) if i < len(framings) else "",
        })
    return out


def parse_dossier_output(raw_text: str) -> dict[str, Any]:
    """Parse Claudia's prose-and-parse output into the v2 dossier schema.

    Returns a dict with: kicker, headline, subline, front_abstract,
    theme_title_for_dossier, theme_abstract_for_dossier, body_paragraphs[],
    headnotes[]. Missing fields default to empty strings or empty lists
    rather than crashing.
    """
    out: dict[str, Any] = {
        "kicker": "",
        "headline": "",
        "subline": "",
        "front_abstract": "",
        "theme_title_for_dossier": "",
        "theme_abstract_for_dossier": "",
        "body_paragraphs": [],
        "headnotes": [],
    }
    for field, rx in _FIELD_LABEL_RE.items():
        m = rx.search(raw_text)
        if m:
            out[field] = _strip_chrome(m.group(1))
    out["body_paragraphs"] = _parse_body_paragraphs(raw_text)
    out["headnotes"] = _parse_headnotes(raw_text)
    return out


# --- Runtime stamping -----------------------------------------------------


def _colophon_for_night(night: int) -> str:
    """Minimal colophon — Editor's desk + night number only.

    The earlier Vol/Issue/edition-label chrome was newspaper fiction and
    has been retired (2026-05-05); the dossier is a House of Beautiful
    Business publication, not a fictional newspaper.
    """
    return f"Filed by the Editor's desk on the morning of Night {night}."


def stamp_runtime_fields(
    parsed: dict[str, Any],
    *,
    night: int,
    theme_id: str,
    theme_display_title: str,
    voice_slugs: list[str],
    voice_name_by_slug: dict[str, str],
    formulation_by_slug: dict[str, str],
    artifact_text_by_slug: dict[str, str] | None = None,
    artifact_form_by_slug: dict[str, str] | None = None,
    final_message: Any | None = None,
    wall_clock_s: float = 0.0,
    thinking_trace: str = "",
    thinking_tokens: int = 0,
) -> dict[str, Any]:
    """Stamp runtime fields onto the parsed dossier. Returns the full
    v2 dossier dict ready to write to disk.

    Per spec v2 field provenance:
      - voice_name + formulation_text per headnote: runtime fills from
        artifact's council_member + briefing's narrative_briefing
      - colophon: minimal night-only template (Vol/Issue/edition chrome
        was retired 2026-05-05)
      - metadata: theme_id + display_title echoed; night + token counts
        + wall from the call
    """
    # Enrich headnotes with all runtime-stamped fields so each headnote is
    # self-contained for the microsite — no separate per-voice file fetch
    # needed to render an artifact page. Stamps:
    #   voice_name        — from per-voice artifact's council_member
    #   formulation_text  — from briefing's narrative_briefing for this theme
    #   artifact_text     — from per-voice Step 2 artifact_text (the body)
    #   artifact_form     — from per-voice selected_form (CSS bundle key)
    # Claudia's emitted fields (artifact_title + framing_text) slot in by
    # matching voice_slug. Voices Claudia missed get empty values but still
    # appear in the list (no silent drops).
    artifact_text_by_slug = artifact_text_by_slug or {}
    artifact_form_by_slug = artifact_form_by_slug or {}
    parsed_by_slug = {
        h.get("voice_slug", ""): h
        for h in parsed.get("headnotes", [])
    }
    enriched_headnotes = [
        {
            "voice_slug":       slug,
            "voice_name":       voice_name_by_slug.get(slug, slug),
            "artifact_title":   parsed_by_slug.get(slug, {}).get("artifact_title", ""),
            "framing_text":     parsed_by_slug.get(slug, {}).get("framing_text", ""),
            "artifact_form":    artifact_form_by_slug.get(slug, ""),
            "artifact_text":    artifact_text_by_slug.get(slug, ""),
            "formulation_text": formulation_by_slug.get(slug, ""),
        }
        for slug in voice_slugs
    ]

    metadata: dict[str, Any] = {
        "theme_id":              theme_id,
        "theme_display_title":   theme_display_title,
        "night":                 night,
        "generated_by":          "editor_pipeline_v2",
        "model":                 EDITOR_MODEL,
        "thinking_enabled":      EDITOR_THINKING,
        "thinking_tokens":       thinking_tokens,
        "wall_clock_s":          round(wall_clock_s, 2),
    }
    if final_message is not None:
        usage = getattr(final_message, "usage", None)
        if usage is not None:
            metadata.update({
                "input_tokens":  getattr(usage, "input_tokens", 0) or 0,
                "output_tokens": getattr(usage, "output_tokens", 0) or 0,
                "cache_creation_input_tokens":
                    getattr(usage, "cache_creation_input_tokens", 0) or 0,
                "cache_read_input_tokens":
                    getattr(usage, "cache_read_input_tokens", 0) or 0,
            })

    # Field order follows surface-by-surface render order:
    #   Page 1:      kicker + headline + front_abstract
    #   Page 2:      kicker + headline (shared) + subline + body_paragraphs
    #   Page 3:      theme_title + theme_abstract
    #   Pages 4-N:   headnotes (each self-contained — see stamp logic)
    #   Audit/stamp: colophon + metadata (not render content)
    return {
        "schema_version":  "2.0",
        # Page 1 + shared with Page 2 article header
        "kicker":          parsed.get("kicker", ""),
        "headline":        parsed.get("headline", ""),
        "front_abstract":  parsed.get("front_abstract", ""),
        # Page 2 (article only)
        "subline":         parsed.get("subline", ""),
        "body_paragraphs": parsed.get("body_paragraphs", []),
        # Page 3 (theme)
        "theme_title_for_dossier":    parsed.get("theme_title_for_dossier", ""),
        "theme_abstract_for_dossier": parsed.get("theme_abstract_for_dossier", ""),
        # Pages 4-N (artifacts)
        "headnotes":       enriched_headnotes,
        # Audit / stamp
        "thinking_trace":  thinking_trace,
        "colophon":        _colophon_for_night(night),
        "metadata":        metadata,
    }


# --- Per-dossier orchestration --------------------------------------------


def generate_dossier(
    *,
    theme_id: str,
    voice_slugs: list[str],
    run_dir: Path,
    night: int,
    system_prompt: tuple[str, str],
    client: Any,
    prior_editions: list[dict[str, Any]] | None = None,
    logger: logging.Logger | None = None,
) -> dict[str, Any]:
    """Run one dossier-generation call. Returns the full v2 dossier dict.

    Caller is responsible for: (a) building system_prompt via
    `card_assembly.assemble_system_prompt`; (b) constructing `client`
    (Anthropic instance); (c) writing the result to disk; (d) handling
    errors at the orchestrator level.
    """
    log = logger or logging.getLogger("editor_dossier_generation")

    briefing = build_dossier_briefing(
        theme_id, voice_slugs, run_dir,
        night=night, prior_editions=prior_editions,
    )
    user_prompt = build_user_prompt(briefing)

    voice_name_by_slug = {v["voice_slug"]: v["voice_name"] for v in briefing["engaged_voices"]}
    formulation_by_slug = {v["voice_slug"]: v["narrative_briefing"] for v in briefing["engaged_voices"]}
    artifact_text_by_slug = {v["voice_slug"]: v["artifact_text"] for v in briefing["engaged_voices"]}
    artifact_form_by_slug = {v["voice_slug"]: v.get("selected_form", "") for v in briefing["engaged_voices"]}
    theme_display_title = briefing["theme"]["theme_display_title"]

    log.info(
        f"  dossier call: theme={theme_id} voices={len(voice_slugs)} model={EDITOR_MODEL}"
    )
    t0 = time.time()
    raw_text, thinking_trace, final_message, thinking_tokens = stream_voice_call(
        client,
        model=EDITOR_MODEL,
        max_tokens=EDITOR_MAX_TOKENS,
        system=system_prompt,
        user=user_prompt,
        thinking_kwargs=_thinking_kwargs(),
        logger=log,
    )
    wall = time.time() - t0

    parsed = parse_dossier_output(raw_text)
    dossier = stamp_runtime_fields(
        parsed,
        night=night,
        theme_id=theme_id,
        theme_display_title=theme_display_title,
        voice_slugs=voice_slugs,
        voice_name_by_slug=voice_name_by_slug,
        formulation_by_slug=formulation_by_slug,
        artifact_text_by_slug=artifact_text_by_slug,
        artifact_form_by_slug=artifact_form_by_slug,
        final_message=final_message,
        wall_clock_s=wall,
        thinking_trace=thinking_trace,
        thinking_tokens=thinking_tokens,
    )
    log.info(
        f"  dossier done: theme={theme_id} "
        f"({len(dossier['body_paragraphs'])} paragraphs, "
        f"{dossier['metadata'].get('output_tokens', 0)} output tokens, "
        f"{dossier['metadata']['wall_clock_s']}s)"
    )
    return dossier
