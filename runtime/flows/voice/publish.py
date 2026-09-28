"""Voice Pipeline — publish-ready artifact handoff.

After Step 3 (or, under Athens `--skip-step3`, after Step 2) + continuity
for a night settle, write per-voice publish-ready files to
<PROJECT_ROOT>/published_artifacts/nights/night_<N>/ that downstream
consumers (micro-site, Edition Pipeline, closing-show pipelines) read from.

Per-voice file shape (one per voice per night) — themes referenced by
ID, not inlined. Per-theme files are produced by the separate
publish_flow.py (which can read across multiple upstream pipelines).

This module's contract:
  - Reads:   <run_dir>/04_voice/step3_amended_artifacts/<slug>.json
             (preferred — when Step 3 ran)
             <run_dir>/04_voice/step2_first_draft_artifacts/<slug>.json
             (fallback — when Step 3 was skipped per A1)
  - Writes:  <PROJECT_ROOT>/published_artifacts/nights/night_<N>/<slug>.json
             <PROJECT_ROOT>/published_artifacts/nights/night_<N>/_index.json

The published file carries `was_step3` (true/false) so consumers can
distinguish amended artifacts (deliberation block populated) from
first-draft artifacts (deliberation.voices_read + amendments empty).

The published file is the SAME artifact as the source run-dir file but:
  - Stripped of telemetry, lineage paths, and thinking_trace
  - Re-shaped for downstream consumers (artifact / themes_addressed /
    deliberation grouped logically)
  - Named with stable URL paths (/night-N/<slug>)
  - Themes referenced by theme_id (joins to per-theme files in
    <PROJECT_ROOT>/published_artifacts/themes/night_<N>/<theme_id>.json)

The run-dir source files remain on disk as the audit / debug surface
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

from flows.shared.io import get_logger, voice_display_name, write_json_atomic
from flows.shared.project_root import resolve_project_root


def _to_publish_per_voice(
    step3_output: dict[str, Any],
    night: int,
    project_root: Path | None = None,
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

    Added:
      - voice_name — C53: resolved from council_config.json via the
        voice's slug (see `flows.shared.io.voice_display_name`), NOT
        from `council_member`. That field on Step 3 artifacts is the
        long card identity-prefix opening line ("I am Augusta Ada
        King, Countess of Lovelace…"), not a clean display name — it
        was previously stamped straight onto this published surface.
        The resolved value is council_config's `name` VERBATIM, e.g.
        "Voice of Ada Lovelace" / "Voice of the Octopus" (2026-05-02
        "Voice of X" standardization — the construction stays visible).
        `project_root` is optional (defaults to a slug-derived
        fallback in the same convention, e.g. "ada_lovelace" ->
        "Voice of Ada Lovelace") so this function stays usable
        standalone/in tests without a real council_config.json on disk.
      - url_path (derived from voice_slug + night)
      - generated_at (ISO timestamp)

    Themes referenced by ID; full theme metadata lives at
    <PROJECT_ROOT>/published_artifacts/themes/night_<N>/<theme_id>.json
    (produced by publish_flow.py — separate stage that reads across
    pipelines; per-night subdir disambiguates Night 2 + Night 3 themes
    from Night 1's, since theme_ids are not stable across Researcher
    runs).
    """
    voice_slug = step3_output["lineage"]["voice_slug"]
    voice_name = voice_display_name(voice_slug, project_root)
    url_path = f"/night-{night}/{voice_slug}"

    # themes_addressed comes from Step 2's themes_covered, propagated via
    # Step 3 lineage's own_first_draft_themes_covered.
    themes_addressed = step3_output["lineage"].get(
        "own_first_draft_themes_covered", []
    )

    # Build deliberation block — strip pipeline-internal join fields.
    #
    # C53 residual (nested names): `voices_read[].voice_name` and
    # `amendments[].cited_voice_name` had the SAME corruption as the
    # top-level `voice_name` fixed in e01eb84 — they were being stamped
    # from the OTHER voice's `council_member` / `cited_voice` field,
    # which on Step 1/2/3 artifacts is the long card identity-prefix
    # opening line ("I am Augusta Ada King, Countess of Lovelace…"), not
    # a clean display name. Resolved the same way as the top-level fix:
    # `voice_display_name(slug, project_root)` off the slug fields
    # already present on these entries.
    #   - `voices_read[].voice_slug` is always present — stamped by
    #     `step3_amended_artifact.build_step3_user_prompt` from the other
    #     voice's own `lineage.voice_slug` — so no fallback is needed.
    #   - `amendments[].cited_voice_slug` is only present when
    #     `run_step3_for_voice` could resolve the model's free-text
    #     `cited_voice` citation to a known voice (it `setdefault`s the
    #     slug only on a successful lookup match). When it's absent, there
    #     is no slug to resolve — fall back to the raw `cited_voice` text
    #     rather than fabricate one.
    deliberation = {
        "decision": step3_output.get("decision", "amend"),
        "decision_rationale": step3_output.get("decision_rationale", ""),
        "voices_read": [
            {
                "voice_name": voice_display_name(v["voice_slug"], project_root),
                "voice_slug": v["voice_slug"],
                "url_path": f"/night-{night}/{v['voice_slug']}",
                "shared_themes": v.get("shared_themes", []),
            }
            for v in step3_output["lineage"].get("voices_read", [])
        ],
        "amendments": [
            {
                "cited_voice_name": (
                    voice_display_name(a["cited_voice_slug"], project_root)
                    if a.get("cited_voice_slug")
                    else a.get("cited_voice", "")
                ),
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
        "was_step3": True,
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


def _to_publish_per_voice_from_step2(
    step2_output: dict[str, Any],
    night: int,
    project_root: Path | None = None,
) -> dict[str, Any]:
    """Re-shape one Step 2 output into a publish-ready file (Step 3 absent).

    Used under Athens `--skip-step3` (per A1, Step 3 dormant for Athens).
    Same published shape as the Step 3 path, with:
      - `was_step3` = False so consumers can distinguish first-draft vs.
        amended artifacts
      - `deliberation.decision` = "first_draft" (no amend/no-change choice
        was made — Step 3 didn't run)
      - `deliberation.voices_read` = []  (Step 3 reads other voices; Step 2
        reads only its own Step 1 outputs)
      - `deliberation.amendments` = []   (Step 3 produces these)

    `voice_name` — C53: resolved from council_config.json via the voice's
    slug (`flows.shared.io.voice_display_name`), NOT from `council_member`
    (the long card identity-prefix opening line, unsuitable as a display
    name). The resolved value is council_config's `name` VERBATIM, e.g.
    "Voice of Ada Lovelace" / "Voice of the Octopus" (2026-05-02 "Voice
    of X" standardization). `project_root` is optional (defaults to a
    slug-derived fallback in the same convention) so this stays usable
    standalone/in tests.

    `themes_addressed` comes from Step 2's `lineage.themes_covered`
    (Step 3 propagates this verbatim; Step 2 derives it deterministically
    from focus_decision + the voice's Step 1 theme_ids).
    """
    voice_slug = step2_output["lineage"]["voice_slug"]
    voice_name = voice_display_name(voice_slug, project_root)
    url_path = f"/night-{night}/{voice_slug}"
    themes_addressed = step2_output["lineage"].get("themes_covered", [])

    return {
        "voice_name": voice_name,
        "voice_slug": voice_slug,
        "night": night,
        "url_path": url_path,
        "was_step3": False,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "artifact": {
            "title": step2_output.get("artifact_title", ""),
            "subtitle": step2_output.get("artifact_subtitle", ""),
            "text": step2_output.get("artifact_text", ""),
            "selected_form": step2_output.get("selected_form", ""),
            "stance": step2_output.get("stance", ""),
            "focus_decision": step2_output.get("focus_decision", ""),
            "word_count": step2_output.get("word_count", 0),
        },
        "themes_addressed": themes_addressed,
        "deliberation": {
            "decision": "first_draft",
            "decision_rationale": "",
            "voices_read": [],
            "amendments": [],
        },
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


def _load_held_voices(run_dir: Path) -> set[str]:
    """C28b: voices the operator marked hold_for_regen at the validation
    gate. Excluded from per-voice publish."""
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


def _rebuild_index_from_disk(
    publish_dir: Path, night: int, held: set[str] | None = None
) -> dict[str, Any]:
    """Rebuild the per-night `_index.json` from every `<slug>.json` file
    actually on disk under `publish_dir` — NOT from whatever subset of
    voices this particular publish call happened to touch.

    C50 fix: the index used to be built from only `voices_published`
    (this invocation's voices), so a sequence of single-voice publish
    reruns left `_index.json` reflecting only the last voice published,
    even though every voice's per-voice file was still sitting on disk
    from earlier calls. Source of truth is now the directory listing —
    every publish call (full batch or single-voice rerun) ends with an
    index that lists every voice file currently present for that night.

    C67 #4 fix: on `main`, held voices (C28b `hold_for_regen`) were
    excluded from the index for free because it was built from
    `voices_published`, which the hold filter already ran on. This
    rebuild-from-disk approach re-introduced them (the per-voice file
    from an earlier, pre-hold publish is still on disk). `held` — the
    same set `publish_voice_artifacts_for_night` filters `voice_slugs`
    with — is skipped here too, by slug, so a held voice drops out of
    the index while its page file stays on disk (not deleted; an
    operator decision can be reversed, and a direct link should still
    resolve). Callers with no `run_dir` context (e.g. the restamp
    script, which only ever touches published data) pass nothing and
    get the old disk-only behavior.

    Per-voice files that fail to parse are skipped (defensive; should
    not happen for files this module itself wrote via
    `write_json_atomic`). Sorted by voice_slug for a deterministic
    index across repeated rebuilds.
    """
    held = held or set()
    voices: list[dict[str, Any]] = []
    for p in sorted(publish_dir.glob("*.json")):
        if p.name == "_index.json":
            continue
        if p.stem in held:
            continue
        try:
            with p.open(encoding="utf-8") as f:
                entry = json.load(f)
        except (OSError, json.JSONDecodeError):
            continue
        artifact = entry.get("artifact", {}) or {}
        deliberation = entry.get("deliberation", {}) or {}
        voices.append({
            "voice_slug": entry.get("voice_slug", p.stem),
            "voice_name": entry.get("voice_name", p.stem),
            "url_path": entry.get("url_path", f"/night-{night}/{p.stem}"),
            "title": artifact.get("title", ""),
            "subtitle": artifact.get("subtitle", ""),
            "selected_form": artifact.get("selected_form", ""),
            "stance": artifact.get("stance", ""),
            "themes_addressed": entry.get("themes_addressed", []),
            "decision": deliberation.get("decision", ""),
            "amendment_count": len(deliberation.get("amendments", []) or []),
            "word_count": artifact.get("word_count", 0),
            "was_step3": entry.get("was_step3", False),
        })
    return {
        "night": night,
        "url_path": f"/night-{night}",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "voices": voices,
        "voice_count": len(voices),
    }


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

    Per-night `_index.json` lists every voice that has a published
    `<slug>.json` file on disk for that night — rebuilt from the
    directory on every call (C50), not just the voices this particular
    call published. This means a single-voice rerun still leaves the
    index listing every previously-published voice, and `voice_count`
    always reflects what's actually publishable on disk.

    Voices marked hold_for_regen via `04_voice/operator_decisions/<voice>.json`
    are EXCLUDED from THIS call's publish (C28b operator gate) AND from the
    rebuilt index (C67 #4) — matching `main`'s behavior, where a full
    republish naturally dropped a held voice because the index was built
    from this call's already-filtered `voices_published`. A file already on
    disk from an earlier, pre-hold publish of that voice is not deleted —
    only excluded from the index — so a direct link to it still resolves.
    """
    logger = get_logger("voice_publish")
    if project_root is None:
        project_root = resolve_project_root(None)

    publish_dir = (
        project_root / "published_artifacts" / "nights" / f"night_{night}"
    )
    publish_dir.mkdir(parents=True, exist_ok=True)

    # If voice_slugs not provided, walk the Step 3 output dir, falling back
    # to Step 2 when Step 3 wasn't run (Athens --skip-step3 per A1).
    if voice_slugs is None:
        step3_dir = run_dir / "04_voice" / "step3_amended_artifacts"
        step2_dir = run_dir / "04_voice" / "step2_first_draft_artifacts"
        slug_set: set[str] = set()
        if step3_dir.exists():
            slug_set.update(p.stem for p in step3_dir.glob("*.json"))
        if step2_dir.exists():
            slug_set.update(p.stem for p in step2_dir.glob("*.json"))
        if not slug_set:
            logger.warning(
                f"  Publish: no Step 3 or Step 2 outputs under {run_dir / '04_voice'}; skipping."
            )
            return {"voices_published": [], "index_path": None, "output_dir": str(publish_dir)}
        voice_slugs = sorted(slug_set)

    # C28b: filter out voices the operator held for regen.
    held = _load_held_voices(run_dir)
    if held:
        before = len(voice_slugs)
        voice_slugs = [s for s in voice_slugs if s not in held]
        logger.info(
            f"  Publish: held {sorted(held)} per operator decisions "
            f"({before - len(voice_slugs)} excluded; {len(voice_slugs)} remain)"
        )

    voices_published: list[dict[str, Any]] = []
    step2_only_count = 0

    for slug in voice_slugs:
        step3 = _load_step3(run_dir, slug)
        step2 = _load_step2(run_dir, slug)
        if step3 is not None:
            publish_entry = _to_publish_per_voice(step3, night, project_root)
            publish_entry = _enrich_with_step2_metadata(publish_entry, step2)
        elif step2 is not None:
            publish_entry = _to_publish_per_voice_from_step2(step2, night, project_root)
            step2_only_count += 1
        else:
            logger.warning(
                f"  Publish: no Step 3 or Step 2 file for {slug}; skipping."
            )
            continue

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
            "was_step3": publish_entry["was_step3"],
        })

    # Per-night _index.json — surface for the micro-site index pages
    # ("Tonight's Edition", "Voice Index" per Frame Concept v1). C50:
    # rebuilt from the on-disk <slug>.json set, not from `voices_published`
    # (this call's voices only) — see `_rebuild_index_from_disk`. C67 #4:
    # `held` is passed through so a held voice's page can stay on disk
    # while dropping out of the index, same as `voices_published` above.
    index = _rebuild_index_from_disk(publish_dir, night, held)
    index_path = publish_dir / "_index.json"
    write_json_atomic(index_path, index)

    if step2_only_count:
        logger.info(
            f"  Publish: night {night} — {step2_only_count}/{len(voices_published)} "
            f"voice(s) published from Step 2 (Step 3 absent; was_step3=false)"
        )

    logger.info(
        f"  Publish: night {night} — {len(voices_published)} voices to "
        f"{publish_dir.relative_to(project_root)}"
    )
    return {
        "voices_published": [v["voice_slug"] for v in voices_published],
        "index_path": str(index_path),
        "output_dir": str(publish_dir),
    }
