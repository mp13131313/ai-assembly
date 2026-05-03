"""Read-only state collection for the /admin/tonight meta view.

Mirrors the orchestrator's filesystem-as-state pattern (see
runtime/scripts/overnight_orchestrator.py). Reads the same sentinel
files + per-stage manifests; does not mutate anything.

Per docs/AI_Assembly_Runtime_Lifecycle.md, the canonical sentinels are:

    Stage 1+2 (transcription)  <run_dir>/01_transcription/<sid>/status.json
    Stage 3 (researcher)       <run_dir>/02_researcher/grouping.json
    Stage 4 (provocateur)      <run_dir>/03_provocateur/manifest.json
    Stage 5 (voice)            <run_dir>/04_voice/manifest.json
    Stage 6 (editor)           <run_dir>/05_editor/manifest.json (if built)
    Stage 7 (publish)          <PROJECT_ROOT>/published_artifacts/nights/
                                 night_<N>/_index.json
    Orchestrator state         <run_dir>/_orchestrator_logs/status.json
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT, RUNS_DIR


# Athens night → run_dir naming, matching DAY_TO_RUN in config.py.
ATHENS_NIGHTS = (1, 2, 3)


def run_dir_for_night(night: int) -> Path:
    """Per ingest/config.py:80-87 DAY_TO_RUN: run_dir = athens_night_<N>."""
    return RUNS_DIR / f"athens_night_{night}"


def published_index_for_night(night: int) -> Path:
    return PROJECT_ROOT / "published_artifacts" / "nights" / f"night_{night}" / "_index.json"


def _read_json_or_none(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _file_mtime_iso(path: Path) -> str | None:
    if not path.exists():
        return None
    return datetime.fromtimestamp(
        path.stat().st_mtime, tz=timezone.utc,
    ).isoformat(timespec="seconds")


def _stage_summary(state: str, label: str = "", **extras: Any) -> dict[str, Any]:
    """Uniform stage row shape consumed by admin_tonight.html."""
    return {"state": state, "label": label, **extras}


def _transcription_summary(run_dir: Path) -> dict[str, Any]:
    """Aggregate per-session transcription state into a stage row.

    States across the per-session status.json files:
        received | normalizing | transcribing* | done | error
    Aggregate logic:
        * any in error           → state="error"
        * all in done            → state="done"
        * any in transcribing*   → state="running" (transcription substate)
        * any in normalizing     → state="running"
        * any in received        → state="running"
        * none                   → state="pending"
    """
    tdir = run_dir / "01_transcription"
    if not tdir.exists():
        return _stage_summary("pending", "no transcription dir yet")

    sessions = sorted(p for p in tdir.iterdir() if p.is_dir())
    if not sessions:
        return _stage_summary("pending", "no sessions uploaded yet")

    counts = {"done": 0, "error": 0, "transcribing": 0, "normalizing": 0,
              "received": 0, "unknown": 0}
    # Per-source totals so the admin dashboard can show "X audio · Y vendor"
    # at a glance. Vendor sessions land via flows/vendor_intake.py with
    # status.json source: "vendor"; everything else (including pre-vendor
    # session_packages without a source field) defaults to "audio".
    by_source = {"audio": 0, "vendor": 0}
    by_source_done = {"audio": 0, "vendor": 0}
    last_done_mtime: str | None = None
    error_sessions: list[str] = []

    for sdir in sessions:
        status = _read_json_or_none(sdir / "status.json")
        st = (status or {}).get("state", "unknown")
        source = (status or {}).get("source", "audio")
        if source not in by_source:
            source = "audio"  # defensive — unknown source treated as audio
        by_source[source] += 1
        # Substates start with "transcribing"; collapse to the parent.
        bucket = "transcribing" if st.startswith("transcribing") else st
        counts[bucket] = counts.get(bucket, 0) + 1
        if bucket == "error":
            error_sessions.append(sdir.name)
        if bucket == "done":
            by_source_done[source] += 1
            mt = _file_mtime_iso(sdir / "status.json")
            if mt and (last_done_mtime is None or mt > last_done_mtime):
                last_done_mtime = mt

    total = len(sessions)
    if counts["error"]:
        state = "error"
    elif counts["done"] == total:
        state = "done"
    elif counts["transcribing"] or counts["normalizing"] or counts["received"]:
        state = "running"
    else:
        state = "pending"

    label = f"{counts['done']}/{total} done"
    if by_source["vendor"]:
        # Always surface vendor count when present so operators can tell at
        # a glance how many sessions arrived via flows/vendor_intake.py.
        label += (
            f" ({by_source_done['audio']}/{by_source['audio']} audio · "
            f"{by_source_done['vendor']}/{by_source['vendor']} vendor)"
        )
    if counts["error"]:
        label += f" · {counts['error']} error"
    if counts["transcribing"]:
        label += f" · {counts['transcribing']} transcribing"
    if counts["normalizing"]:
        label += f" · {counts['normalizing']} normalizing"
    if counts["received"]:
        label += f" · {counts['received']} received"

    return _stage_summary(
        state,
        label,
        counts=counts,
        by_source=by_source,
        by_source_done=by_source_done,
        total=total,
        last_done_mtime=last_done_mtime,
        error_sessions=error_sessions,
    )


def _researcher_summary(run_dir: Path) -> dict[str, Any]:
    grouping = _read_json_or_none(run_dir / "02_researcher" / "grouping.json")
    if grouping is None:
        return _stage_summary("pending")
    themes = grouping.get("themes", [])
    n_themes = len(themes)
    n_clusters = sum(len(t.get("clusters", [])) for t in themes)
    n_extractions = sum(
        len(c.get("extraction_ids", []))
        for t in themes
        for c in t.get("clusters", [])
    )
    n_isolates = len(grouping.get("isolates", []))
    label = (
        f"{n_extractions} extractions · {n_clusters} clusters · "
        f"{n_themes} themes"
    )
    if n_isolates:
        label += f" · {n_isolates} isolates"
    return _stage_summary(
        "done", label,
        mtime=_file_mtime_iso(run_dir / "02_researcher" / "grouping.json"),
        themes=n_themes, clusters=n_clusters, extractions=n_extractions,
    )


def _provocateur_summary(run_dir: Path) -> dict[str, Any]:
    manifest = _read_json_or_none(run_dir / "03_provocateur" / "manifest.json")
    if manifest is None:
        # Was Researcher already done? If so, Provocateur is "running" (it should
        # have started); if not, "pending".
        if (run_dir / "02_researcher" / "grouping.json").exists():
            return _stage_summary("running")
        return _stage_summary("pending")
    out = manifest.get("outputs", {})
    n_themes = out.get("selected_themes", 0)
    n_dropped = out.get("dropped_themes", 0)
    n_formulations = out.get("formulations", 0)
    n_forced = out.get("forced_fits", 0)
    n_swap = out.get("stretch_swaps", 0)
    label = (
        f"{n_themes} themes selected · {n_formulations} pairs · "
        f"{n_forced} forced-fits · {n_swap} stretch-swaps"
    )
    if n_dropped:
        label += f" · {n_dropped} dropped"
    return _stage_summary(
        "done", label,
        mtime=_file_mtime_iso(run_dir / "03_provocateur" / "manifest.json"),
        themes=n_themes, formulations=n_formulations,
    )


def _voice_summary(run_dir: Path) -> dict[str, Any]:
    manifest = _read_json_or_none(run_dir / "04_voice" / "manifest.json")
    if manifest is None:
        if (run_dir / "03_provocateur" / "manifest.json").exists():
            return _stage_summary("running")
        return _stage_summary("pending")
    counts = manifest.get("counts", {})
    n_pairs = counts.get("step1_pairs_succeeded", 0)
    n_attempts = counts.get("step1_pairs_attempted", 0)
    n_step2 = counts.get("step2_voices_succeeded", 0)
    n_step3 = counts.get("step3_voices_succeeded", 0)
    n_continuity = counts.get("continuity_voices_succeeded", 0)
    n_flagged = counts.get("validation_flagged", 0)
    label = (
        f"Step 1: {n_pairs}/{n_attempts} · Step 2: {n_step2} voices · "
        f"continuity: {n_continuity}"
    )
    if n_step3:
        label += f" · Step 3: {n_step3}"
    if n_flagged:
        label += f" · ⚠ {n_flagged} validation flags"
    return _stage_summary(
        "done", label,
        mtime=_file_mtime_iso(run_dir / "04_voice" / "manifest.json"),
        validation_flagged=n_flagged,
    )


def _editor_summary(run_dir: Path) -> dict[str, Any]:
    """Editor is post-B1; absent editor_flow.py → orchestrator skips."""
    manifest_path = run_dir / "05_editor" / "manifest.json"
    if not manifest_path.exists():
        # Heuristic: if Voice is done and editor_flow.py doesn't exist in
        # the deployed code tree, the orchestrator will have cleanly skipped.
        # We don't probe the code tree here — just report pending and let
        # the operator infer from the orchestrator status.json + lifecycle doc.
        if (run_dir / "04_voice" / "manifest.json").exists():
            return _stage_summary(
                "skipped" if not _editor_flow_built() else "running",
            )
        return _stage_summary("pending")
    manifest = _read_json_or_none(manifest_path) or {}
    n_dossiers = len(manifest.get("dossiers", []))
    label = f"{n_dossiers} dossier(s)"
    return _stage_summary(
        "done", label,
        mtime=_file_mtime_iso(manifest_path),
        dossiers=n_dossiers,
    )


def _editor_flow_built() -> bool:
    """Is editor_flow.py present in the deployed code tree?"""
    from .config import REPO_ROOT
    return (REPO_ROOT / "flows" / "editor_flow.py").exists()


def _publish_summary(run_dir: Path, night: int) -> dict[str, Any]:
    index_path = published_index_for_night(night)
    if not index_path.exists():
        if (run_dir / "04_voice" / "manifest.json").exists():
            return _stage_summary("running")
        return _stage_summary("pending")
    idx = _read_json_or_none(index_path) or {}
    voices = idx.get("voices") or idx.get("voice_slugs") or []
    label = f"{len(voices)} voice(s) published"
    return _stage_summary(
        "done", label,
        mtime=_file_mtime_iso(index_path),
        voices=len(voices),
    )


def _orchestrator_summary(run_dir: Path) -> dict[str, Any]:
    """Read the orchestrator's own status.json, the script's self-report."""
    status = _read_json_or_none(run_dir / "_orchestrator_logs" / "status.json")
    if status is None:
        return {"state": None, "detail": "no orchestrator state on disk yet"}
    return status


def collect_night_state(night: int) -> dict[str, Any]:
    """Top-level helper: assemble the dashboard payload for one night."""
    run_dir = run_dir_for_night(night)
    run_exists = run_dir.exists()

    payload: dict[str, Any] = {
        "night": night,
        "run_id": run_dir.name,
        "run_dir": str(run_dir),
        "run_exists": run_exists,
        "orchestrator": _orchestrator_summary(run_dir) if run_exists else
                        {"state": None, "detail": "run dir not created yet"},
        "stages": {},
        "polled_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }

    if not run_exists:
        # Stage rows still rendered (all "pending") so the meta view shows
        # the night layout even before audio uploads start.
        for s in ("transcription", "researcher", "provocateur", "voice",
                  "editor", "publish"):
            payload["stages"][s] = _stage_summary("pending")
        return payload

    payload["stages"]["transcription"] = _transcription_summary(run_dir)
    payload["stages"]["researcher"] = _researcher_summary(run_dir)
    payload["stages"]["provocateur"] = _provocateur_summary(run_dir)
    payload["stages"]["voice"] = _voice_summary(run_dir)
    payload["stages"]["editor"] = _editor_summary(run_dir)
    payload["stages"]["publish"] = _publish_summary(run_dir, night)

    return payload


# --- Voice Pipeline detail view (C23 Phase B, 2026-05-03) -------------------
#
# Reads files under <run_dir>/04_voice/ and <PROJECT_ROOT>/voices/<slug>/ to
# build the per-pair Step 1 grid + validation grid + per-voice Step 2 +
# continuity list. Athens working envelope: 30-60 (voice, theme) pairs for
# Step 1; 60-120 (pair × {anachronism, constitution}) cells for validation;
# 10 voices for Step 2 + continuity.


def _step1_pair_state(path: Path) -> dict[str, Any]:
    """Extract a compact cell record from one step1_detailed_responses/*.json."""
    data = _read_json_or_none(path) or {}
    lineage = data.get("lineage", {}) or {}
    voice_slug = lineage.get("voice_slug") or ""
    theme_id = lineage.get("theme_id") or ""
    if not voice_slug or not theme_id:
        # Fall back to filename (voice__theme.json)
        stem = path.stem
        if "__" in stem:
            voice_slug, theme_id = stem.split("__", 1)
    return {
        "voice_slug": voice_slug,
        "theme_id": theme_id,
        "council_member": data.get("council_member", voice_slug),
        "theme_display_title": data.get("theme_display_title", theme_id),
        "mode": data.get("mode"),
        "state": "done" if data else "missing",
        "model": data.get("model"),
        "input_tokens": data.get("input_tokens"),
        "output_tokens": data.get("output_tokens"),
        "thinking_tokens": data.get("thinking_tokens"),
        "wall_clock_s": data.get("wall_clock_s"),
        "mtime": _file_mtime_iso(path),
        "extractions_engaged": data.get("extractions_engaged", []) or [],
    }


def voice_step1_grid(run_dir: Path) -> list[dict[str, Any]]:
    """Return one cell record per (voice, theme) Step 1 file on disk.

    Cells with no file yet are not returned; the renderer fills the grid
    by cross-joining voices × themes and looking up cells by (voice, theme).
    Sorted by voice_slug, theme_id for stable rendering.
    """
    s1_dir = run_dir / "04_voice" / "step1_detailed_responses"
    if not s1_dir.exists():
        return []
    cells = [_step1_pair_state(p) for p in sorted(s1_dir.glob("*.json"))]
    return cells


def voice_validation_grid(run_dir: Path) -> list[dict[str, Any]]:
    """One cell record per validated (voice, theme) pair.

    Each record carries both anachronism + constitution sub-states. The
    final_status is the orchestrator's roll-up (`flagged` if either failed).
    """
    val_dir = run_dir / "04_voice" / "validation"
    if not val_dir.exists():
        return []
    out = []
    for p in sorted(val_dir.glob("*.json")):
        data = _read_json_or_none(p) or {}
        stem = p.stem  # voice__theme
        voice_slug, _, theme_id = stem.partition("__")
        anach = data.get("anachronism", {}) or {}
        const = data.get("constitution", {}) or {}
        out.append({
            "voice_slug": voice_slug,
            "theme_id": theme_id,
            "anachronism_status": anach.get("status"),  # "PASS" | "ISSUES" | None
            "constitution_status": const.get("status"),
            "final_status": data.get("final_status"),    # "clean" | "flagged"
            "regen_count": data.get("regen_count", 0),
            "anachronism_text": (anach.get("text") or "").strip(),
            "constitution_text": (const.get("text") or "").strip(),
            "mtime": _file_mtime_iso(p),
        })
    return out


def voice_step2_list(run_dir: Path) -> list[dict[str, Any]]:
    """One row per voice that wrote a Step 2 first-draft artifact."""
    s2_dir = run_dir / "04_voice" / "step2_first_draft_artifacts"
    if not s2_dir.exists():
        return []
    out = []
    for p in sorted(s2_dir.glob("*.json")):
        data = _read_json_or_none(p) or {}
        lineage = data.get("lineage", {}) or {}
        out.append({
            "voice_slug": lineage.get("voice_slug") or p.stem,
            "council_member": data.get("council_member", p.stem),
            "focus_decision": data.get("focus_decision"),
            "focus_rationale": data.get("focus_rationale"),
            "stance": data.get("stance"),
            "stance_rationale": data.get("stance_rationale"),
            "selected_form": data.get("selected_form"),
            "form_rationale": data.get("form_rationale"),
            "themes_covered": lineage.get("themes_covered", []) or [],
            "word_count": data.get("word_count"),
            "wall_clock_s": data.get("wall_clock_s"),
            "input_tokens": data.get("input_tokens"),
            "output_tokens": data.get("output_tokens"),
            "mtime": _file_mtime_iso(p),
        })
    return out


def voice_continuity_list(
    project_root: Path, night: int, voice_slugs: list[str],
) -> list[dict[str, Any]]:
    """Per-voice continuity-overlay status for the NEXT night (N+1).

    Continuity flow runs after Night N completes and writes
    `<PROJECT_ROOT>/voices/<slug>/continuity_night_<N+1>.json` for each
    voice that finished Night N. (Skipped on Night 3 — no Night 4.)
    """
    out = []
    next_night = night + 1
    for slug in voice_slugs:
        cont_path = (
            project_root / "voices" / slug
            / f"continuity_night_{next_night}.json"
        )
        out.append({
            "voice_slug": slug,
            "for_night": next_night,
            "written": cont_path.exists() if next_night <= 3 else False,
            "skipped_last_night": next_night > 3,  # Night 3 is the last
            "mtime": _file_mtime_iso(cont_path),
            "path": str(cont_path),
        })
    return out


def collect_voice_detail(night: int) -> dict[str, Any]:
    """Top-level payload for /admin/tonight/voice.

    Combines Step 1 grid + validation grid + Step 2 list + continuity list.
    Cross-joins voice × theme dimensions so the renderer can build a stable
    matrix even when cells are missing.
    """
    run_dir = run_dir_for_night(night)
    if not run_dir.exists():
        return {
            "night": night,
            "run_id": run_dir.name,
            "run_exists": False,
            "voices": [],
            "themes": [],
            "step1_cells": [],
            "validation_cells": [],
            "step2_voices": [],
            "continuity_voices": [],
            "polled_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }

    s1_cells = voice_step1_grid(run_dir)
    val_cells = voice_validation_grid(run_dir)
    s2_voices = voice_step2_list(run_dir)

    # Voices and themes — derived from Step 1 cells (most complete view) +
    # Step 2 voices (in case Step 2 ran for more voices than Step 1 cells
    # we picked up). Order: voices alphabetically by slug; themes by id.
    voices_set: set[str] = set()
    themes_set: set[str] = set()
    voice_council: dict[str, str] = {}
    theme_titles: dict[str, str] = {}
    for c in s1_cells:
        voices_set.add(c["voice_slug"])
        themes_set.add(c["theme_id"])
        voice_council[c["voice_slug"]] = c["council_member"]
        theme_titles[c["theme_id"]] = c["theme_display_title"]
    for v in s2_voices:
        voices_set.add(v["voice_slug"])
        voice_council[v["voice_slug"]] = v["council_member"]
        for tid in v["themes_covered"]:
            themes_set.add(tid)

    voices = [
        {"voice_slug": s, "council_member": voice_council.get(s, s)}
        for s in sorted(voices_set)
    ]
    themes = [
        {"theme_id": t, "theme_display_title": theme_titles.get(t, t)}
        for t in sorted(themes_set)
    ]

    cont_list = voice_continuity_list(
        PROJECT_ROOT, night, [v["voice_slug"] for v in voices],
    )

    # Manifest for top-line counts (validation_failures, etc.).
    manifest = _read_json_or_none(run_dir / "04_voice" / "manifest.json") or {}

    return {
        "night": night,
        "run_id": run_dir.name,
        "run_dir": str(run_dir),
        "run_exists": True,
        "voices": voices,
        "themes": themes,
        "step1_cells": s1_cells,
        "validation_cells": val_cells,
        "step2_voices": s2_voices,
        "continuity_voices": cont_list,
        "manifest": {
            "counts": manifest.get("counts", {}),
            "validation_failures_count": len(
                manifest.get("validation_failures", [])
            ),
            "wall_clock_s": manifest.get("wall_clock_s"),
        },
        "polled_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def latest_active_night() -> int:
    """Pick the right night to default to.

    Heuristic: latest night whose run_dir exists AND publish hasn't completed.
    Falls back to night 1 if nothing exists yet.
    """
    for n in reversed(ATHENS_NIGHTS):
        rd = run_dir_for_night(n)
        if rd.exists() and not published_index_for_night(n).exists():
            return n
    # Either nothing started, or all 3 nights complete. Default to whichever
    # exists; otherwise night 1.
    for n in reversed(ATHENS_NIGHTS):
        if run_dir_for_night(n).exists():
            return n
    return 1
