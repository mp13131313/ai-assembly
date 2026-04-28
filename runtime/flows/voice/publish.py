"""Voice Pipeline — publish-ready artifact handoff.

After Step 3 + continuity for a night settle, write per-voice publish-
ready files to <PROJECT_ROOT>/published_artifacts/nights/night_<N>/
that downstream consumers (micro-site, Edition Pipeline, Substack
curation, closing-show pipelines) read from.

Per-voice file shape (one per voice per night) — themes referenced by
ID, not inlined. Per-theme files are produced by the separate
publish_flow.py (which can read across multiple upstream pipelines).

This module's contract:
  - Reads:   <run_dir>/04_voice/step3_amended_artifacts/<slug>.json
  - Writes:  <PROJECT_ROOT>/published_artifacts/nights/night_<N>/<slug>.json
             <PROJECT_ROOT>/published_artifacts/nights/night_<N>/_index.json

The published file is the SAME artifact as the run-dir Step 3 file but:
  - Stripped of telemetry, lineage paths, and thinking_trace
  - Re-shaped for downstream consumers (artifact / themes_addressed /
    deliberation grouped logically)
  - Named with stable URL paths (/night-N/<slug>)
  - Themes referenced by theme_id (joins to per-theme files in
    <PROJECT_ROOT>/published_artifacts/themes/<theme_id>.json)

The run-dir Step 3 files remain on disk as the audit / debug surface
(full lineage, thinking_trace, telemetry). The published files are
the read surface.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from flows.shared.io import get_logger, write_json_atomic
from flows.shared.project_root import resolve_project_root


def _to_publish_per_voice(
    step3_output: dict[str, Any],
    night: int,
) -> dict[str, Any]:
    """Re-shape one Step 3 output into a publish-ready file.

    Stripped of:
      - lineage block (run_id, file paths, extraction_ids, session_ids)
      - thinking_trace (audit only)
      - telemetry (model, tokens, wall_clock_s)
      - amendments[].cited_first_draft_path / cited_theme_id /
        cited_formulation_id (internal joins; URL path derived instead)

    Renamed:
      - amended_artifact_title → artifact.title
      - amended_artifact_subtitle → artifact.subtitle
      - amended_artifact_text → artifact.text
      - council_member → voice_name

    Added:
      - url_path (derived from voice_slug + night)
      - generated_at (ISO timestamp)

    Themes referenced by ID; full theme metadata lives at
    <PROJECT_ROOT>/published_artifacts/themes/<theme_id>.json (produced
    by publish_flow.py — separate stage that reads across pipelines).
    """
    voice_slug = step3_output["lineage"]["voice_slug"]
    voice_name = step3_output.get("council_member") or voice_slug
    url_path = f"/night-{night}/{voice_slug}"

    # themes_addressed comes from Step 2's themes_covered, propagated via
    # Step 3 lineage's own_first_draft_themes_covered.
    themes_addressed = step3_output["lineage"].get(
        "own_first_draft_themes_covered", []
    )

    # Build deliberation block — strip pipeline-internal join fields.
    deliberation = {
        "decision": step3_output.get("decision", "amend"),
        "decision_rationale": step3_output.get("decision_rationale", ""),
        "voices_read": [
            {
                "voice_name": v.get("council_member") or v.get("voice_slug"),
                "voice_slug": v["voice_slug"],
                "url_path": f"/night-{night}/{v['voice_slug']}",
                "shared_themes": v.get("shared_themes", []),
            }
            for v in step3_output["lineage"].get("voices_read", [])
        ],
        "amendments": [
            {
                "cited_voice_name": a.get("cited_voice")
                or a.get("cited_voice_slug", ""),
                "cited_voice_slug": a.get("cited_voice_slug", ""),
                "cited_url_path": (
                    f"/night-{night}/{a['cited_voice_slug']}"
                    if a.get("cited_voice_slug")
                    else ""
                ),
                "cited_passage": a.get("cited_passage", ""),
                "amendment_type": a.get("amendment_type", ""),
                "rationale": a.get("rationale", ""),
                "cited_theme_id": a.get("cited_theme_id", ""),
            }
            for a in step3_output.get("amendments", [])
        ],
    }

    return {
        "voice_name": voice_name,
        "voice_slug": voice_slug,
        "night": night,
        "url_path": url_path,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "artifact": {
            "title": step3_output.get("amended_artifact_title", ""),
            "subtitle": step3_output.get("amended_artifact_subtitle", ""),
            "text": step3_output.get("amended_artifact_text", ""),
            "selected_form": step3_output.get("selected_form", ""),
            "stance": "",  # Step 2's stance — populated below if Step 2 file is at hand
            "focus_decision": "",
            "word_count": step3_output.get("word_count", 0),
        },
        "themes_addressed": themes_addressed,
        "deliberation": deliberation,
    }


def _enrich_with_step2_metadata(
    publish_entry: dict[str, Any],
    step2_output: dict[str, Any] | None,
) -> dict[str, Any]:
    """Pull stance + focus_decision from Step 2 (Step 3 doesn't carry them
    explicitly; Step 2 records them as the voice's craft choices for the
    artifact). Mutates and returns the publish_entry.
    """
    if step2_output is None:
        return publish_entry
    publish_entry["artifact"]["stance"] = step2_output.get("stance", "")
    publish_entry["artifact"]["focus_decision"] = step2_output.get(
        "focus_decision", ""
    )
    # If Step 3 selected_form is empty (didn't change), inherit from Step 2.
    if not publish_entry["artifact"]["selected_form"]:
        publish_entry["artifact"]["selected_form"] = step2_output.get(
            "selected_form", ""
        )
    return publish_entry


def _load_step3(run_dir: Path, voice_slug: str) -> dict[str, Any] | None:
    p = run_dir / "04_voice" / "step3_amended_artifacts" / f"{voice_slug}.json"
    if not p.exists():
        return None
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def _load_step2(run_dir: Path, voice_slug: str) -> dict[str, Any] | None:
    p = run_dir / "04_voice" / "step2_first_draft_artifacts" / f"{voice_slug}.json"
    if not p.exists():
        return None
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def publish_voice_artifacts_for_night(
    run_dir: Path,
    night: int,
    project_root: Path | None = None,
    voice_slugs: list[str] | None = None,
) -> dict[str, Any]:
    """Publish per-voice artifact files + per-night index for one night.

    Idempotent: per-voice files are overwritten if they exist (cheap
    deterministic transform of the source Step 3 / Step 2 files).

    Returns: summary dict {voices_published, index_path, output_dir}.

    Per-night `_index.json` lists every voice that published a file
    that night, with summary metadata for index-page rendering.
    """
    logger = get_logger("voice_publish")
    if project_root is None:
        project_root = resolve_project_root(None)

    publish_dir = (
        project_root / "published_artifacts" / "nights" / f"night_{night}"
    )
    publish_dir.mkdir(parents=True, exist_ok=True)

    # If voice_slugs not provided, walk the Step 3 output dir.
    if voice_slugs is None:
        step3_dir = run_dir / "04_voice" / "step3_amended_artifacts"
        if not step3_dir.exists():
            logger.warning(
                f"  Publish: no Step 3 outputs at {step3_dir}; skipping."
            )
            return {"voices_published": [], "index_path": None, "output_dir": str(publish_dir)}
        voice_slugs = sorted(p.stem for p in step3_dir.glob("*.json"))

    voices_published: list[dict[str, Any]] = []

    for slug in voice_slugs:
        step3 = _load_step3(run_dir, slug)
        if step3 is None:
            logger.warning(f"  Publish: no Step 3 file for {slug}; skipping.")
            continue
        step2 = _load_step2(run_dir, slug)
        publish_entry = _to_publish_per_voice(step3, night)
        publish_entry = _enrich_with_step2_metadata(publish_entry, step2)

        out_path = publish_dir / f"{slug}.json"
        write_json_atomic(out_path, publish_entry)
        voices_published.append({
            "voice_slug": slug,
            "voice_name": publish_entry["voice_name"],
            "url_path": publish_entry["url_path"],
            "title": publish_entry["artifact"]["title"],
            "subtitle": publish_entry["artifact"]["subtitle"],
            "selected_form": publish_entry["artifact"]["selected_form"],
            "stance": publish_entry["artifact"]["stance"],
            "themes_addressed": publish_entry["themes_addressed"],
            "decision": publish_entry["deliberation"]["decision"],
            "amendment_count": len(publish_entry["deliberation"]["amendments"]),
            "word_count": publish_entry["artifact"]["word_count"],
        })

    # Per-night _index.json — surface for the micro-site index pages
    # ("Tonight's Edition", "Voice Index" per Frame Concept v1).
    index = {
        "night": night,
        "url_path": f"/night-{night}",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "voices": voices_published,
        "voice_count": len(voices_published),
    }
    index_path = publish_dir / "_index.json"
    write_json_atomic(index_path, index)

    logger.info(
        f"  Publish: night {night} — {len(voices_published)} voices to "
        f"{publish_dir.relative_to(project_root)}"
    )
    return {
        "voices_published": [v["voice_slug"] for v in voices_published],
        "index_path": str(index_path),
        "output_dir": str(publish_dir),
    }
