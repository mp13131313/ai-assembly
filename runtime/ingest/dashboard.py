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

    States across the per-session status.json files (post-C26 2026-05-04):
        received | normalizing | normalized | transcribing* | done | error
    Aggregate logic:
        * any in error           → state="error"
        * all in done            → state="done"
        * any in transcribing*   → state="running" (transcription substate)
        * any in normalizing     → state="running"
        * any in normalized      → state="awaiting_dispatch"  (orchestrator hasn't picked up yet)
        * any in received        → state="running"
        * none                   → state="pending"

    `normalized` is the post-C26 happy-path state where ffmpeg has
    completed but the orchestrator hasn't yet spawned transcription.
    Surfaced distinctly so operators can tell whether the bottleneck is
    on ffmpeg, the orchestrator dispatcher, or AssemblyAI itself.
    """
    tdir = run_dir / "01_transcription"
    if not tdir.exists():
        return _stage_summary("pending", "no transcription dir yet")

    sessions = sorted(p for p in tdir.iterdir() if p.is_dir())
    if not sessions:
        return _stage_summary("pending", "no sessions uploaded yet")

    counts = {"done": 0, "error": 0, "transcribing": 0, "normalizing": 0,
              "normalized": 0, "received": 0, "unknown": 0}
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
    elif counts["normalized"]:
        # C26: ffmpeg finished but orchestrator hasn't spawned transcription
        # yet. Up to ~60s lag (default poll interval); operator may want to
        # check the orchestrator is alive.
        state = "awaiting_dispatch"
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
    if counts["normalized"]:
        label += f" · {counts['normalized']} awaiting dispatch"
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
    rsr_dir = run_dir / "02_researcher"
    grouping = _read_json_or_none(rsr_dir / "grouping.json")
    if grouping is None:
        # Detect mid-flight states: per-session *_extractions.json files
        # appear during Node 1; all_extractions.json after Node 1 finishes
        # for all sessions; clusters.json after Node 2; grouping.json
        # after Node 3. Surface progress so operator isn't staring at grey.
        per_session_files = [
            p for p in rsr_dir.glob("*_extractions.json")
            if p.name != "all_extractions.json"
        ] if rsr_dir.exists() else []
        clusters_present = (rsr_dir / "clusters.json").exists()
        all_extractions_present = (rsr_dir / "all_extractions.json").exists()
        if clusters_present:
            return _stage_summary("running", "Node 3 (theming) in progress")
        if all_extractions_present:
            return _stage_summary("running", "Node 2 (clustering) in progress")
        if per_session_files:
            return _stage_summary(
                "running",
                f"Node 1 (extraction) {len(per_session_files)} session{'' if len(per_session_files) == 1 else 's'} done"
            )
        # Still pending — Researcher hasn't written anything yet, but if
        # transcription is done it should be running soon.
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
        mtime=_file_mtime_iso(rsr_dir / "grouping.json"),
        themes=n_themes, clusters=n_clusters, extractions=n_extractions,
    )


def _provocateur_summary(run_dir: Path) -> dict[str, Any]:
    prov_dir = run_dir / "03_provocateur"
    manifest = _read_json_or_none(prov_dir / "manifest.json")
    if manifest is None:
        if not (run_dir / "02_researcher" / "grouping.json").exists():
            return _stage_summary("pending")
        # Provocateur is running; report which sub-phase based on what files
        # exist on disk. Phases (in order, per provocateur_flow.py):
        #   1. triage_flags.json — global theme flags
        #   2. triage_voices/<slug>.json — per-voice triage (N files, one per
        #      council member, written in parallel)
        #   3. selection.json — kept/dropped + assignments
        #   4. briefings/<slug>.json — per-voice (one per voice)
        #   5. formulations/<theme>__<voice>.json — per (theme, voice) pair
        #   6. manifest.json — final, signals done
        formulations_done = (
            len(list((prov_dir / "formulations").glob("*.json")))
            if (prov_dir / "formulations").exists() else 0
        )
        if formulations_done > 0:
            return _stage_summary(
                "running",
                f"formulating ({formulations_done} pair{'' if formulations_done == 1 else 's'} done)"
            )
        briefings_done = (
            len(list((prov_dir / "briefings").glob("*.json")))
            if (prov_dir / "briefings").exists() else 0
        )
        if briefings_done > 0:
            return _stage_summary(
                "running",
                f"briefing voices ({briefings_done} written)"
            )
        if (prov_dir / "selection.json").exists():
            return _stage_summary("running", "selection complete; briefings starting")
        triage_voices_done = (
            len(list((prov_dir / "triage_voices").glob("*.json")))
            if (prov_dir / "triage_voices").exists() else 0
        )
        if triage_voices_done > 0:
            return _stage_summary(
                "running",
                f"triaging voices ({triage_voices_done}/{_council_size(run_dir)})"
            )
        if (prov_dir / "triage_flags.json").exists():
            return _stage_summary("running", "theme flags done; per-voice triage starting")
        return _stage_summary("running", "starting (theme flags pending)")
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
        mtime=_file_mtime_iso(prov_dir / "manifest.json"),
        themes=n_themes, formulations=n_formulations,
    )


def _build_coverage_by_slug(
    sel: dict, voices: list, *, council_name_to_slug: dict
) -> dict:
    """Build a {voice_slug: {got, target, below}} lookup from selection data.

    `sel.below_target` carries (voice_display_name, got, target) entries;
    `sel.coverage_per_member` carries (voice_display_name → got). Combine
    + map back to slugs so the Provocateur drilldown can render per-voice
    coverage without the operator having to scroll to the warning section.
    """
    target_default = 0
    for bt in sel.get("below_target", []) or []:
        if isinstance(bt, dict) and bt.get("target"):
            target_default = bt["target"]
            break

    out: dict = {}
    coverage = sel.get("coverage_per_member", {}) or {}
    below_set = {
        bt["voice"] for bt in (sel.get("below_target", []) or [])
        if isinstance(bt, dict) and bt.get("voice")
    }
    for voice_row in voices:
        slug = voice_row["voice_slug"]
        # Reverse-lookup display name from slug.
        display = None
        for nm, sl in council_name_to_slug.items():
            if sl == slug:
                display = nm
                break
        got = coverage.get(display, 0) if display else 0
        out[slug] = {
            "got": got,
            "target": target_default,
            "below": display in below_set if display else False,
        }
    return out


def _council_size(run_dir: Path) -> int:
    """Try to read the council member count from PROJECT_ROOT/council_config.json."""
    try:
        from .config import PROJECT_ROOT
        cfg = _read_json_or_none(PROJECT_ROOT / "council_config.json")
        if cfg and isinstance(cfg.get("members"), list):
            return len(cfg["members"])
    except Exception:
        pass
    return 0


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
    n_flagged_step1 = counts.get("validation_flagged", 0)
    label = (
        f"Step 1: {n_pairs}/{n_attempts} · Step 2: {n_step2} voices · "
        f"continuity: {n_continuity}"
    )
    if n_step3:
        label += f" · Step 3: {n_step3}"
    if n_flagged_step1:
        label += f" · {n_flagged_step1} Step 1 flag(s)"

    # C28b: surface awaiting-operator state if Step 2 validation has
    # undecided flagged voices.
    val_dir = run_dir / "04_voice" / "step2_validation"
    dec_dir = run_dir / "04_voice" / "operator_decisions"
    flagged: list[str] = []
    if val_dir.exists():
        for vf in sorted(val_dir.glob("*.json")):
            try:
                data = json.loads(vf.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if data.get("overall_verdict") in ("WARN", "HOLD"):
                flagged.append(data.get("voice_slug") or vf.stem)
    decided = set()
    if dec_dir.exists():
        for s in flagged:
            if (dec_dir / f"{s}.json").exists():
                decided.add(s)
    undecided = [s for s in flagged if s not in decided]
    if undecided:
        return _stage_summary(
            "running",
            f"⚠ AWAITING OPERATOR — {len(undecided)} voice(s) flagged: {', '.join(sorted(undecided))}",
            mtime=_file_mtime_iso(run_dir / "04_voice" / "manifest.json"),
            validation_flagged=n_flagged_step1,
            step2_validation_flagged=len(flagged),
            step2_validation_undecided=len(undecided),
            step2_validation_undecided_voices=undecided,
        )
    if flagged:
        label += f" · {len(flagged)} Step 2 flag(s) cleared"
    return _stage_summary(
        "done", label,
        mtime=_file_mtime_iso(run_dir / "04_voice" / "manifest.json"),
        validation_flagged=n_flagged_step1,
        step2_validation_flagged=len(flagged),
        step2_validation_undecided=0,
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
    counts = manifest.get("counts", {})
    n_succeeded = counts.get("dossiers_succeeded", 0)
    n_failed = counts.get("dossiers_failed", 0)
    n_themes = counts.get("themes_routed", 0)
    label = f"{n_succeeded}/{n_themes} dossier(s)"
    if n_failed:
        label += f" · ⚠ {n_failed} failed"
    return _stage_summary(
        "done" if n_failed == 0 else "error",
        label,
        mtime=_file_mtime_iso(manifest_path),
        dossiers_succeeded=n_succeeded,
        dossiers_failed=n_failed,
        themes_routed=n_themes,
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

    # Voices and themes — seed from upstream Provocateur (briefings/<slug>.json
    # one per voice; full_theme_record for each (voice, theme) pair). This
    # ensures the matrix shows ALL expected voices/themes from the start of
    # Step 1, not only the ones whose Step 1 outputs have already landed.
    # Step 1 / Step 2 cells overlay actual progress on top.
    voices_set: set[str] = set()
    themes_set: set[str] = set()
    voice_display: dict[str, str] = {}
    theme_titles: dict[str, str] = {}

    # Build a slug → council display name lookup from PROJECT_ROOT
    # council_config.json. The council uses display names ("Ada Lovelace");
    # voice slugs are folder names ("ada_lovelace"). Match by lowercased
    # name with underscores → spaces.
    from .config import PROJECT_ROOT
    council = _read_json_or_none(PROJECT_ROOT / "council_config.json") or {}
    council_name_by_slug: dict[str, str] = {}
    for m in council.get("members", []) or []:
        nm = m.get("name") or ""
        slug = nm.lower().replace(" ", "_").replace("'", "")
        if slug and nm:
            council_name_by_slug[slug] = nm

    # Seed voices from briefings/ directory + collect EXPECTED (voice, theme)
    # pairs (the ones the Provocateur selected for formulation). The Voice
    # pipeline only runs Step 1 for these pairs — every other cell in the
    # voice × theme matrix should render as "not selected" rather than
    # "pending forever".
    expected_pairs: set[tuple[str, str]] = set()
    briefings_dir = run_dir / "03_provocateur" / "briefings"
    if briefings_dir.exists():
        for bp in sorted(briefings_dir.glob("*.json")):
            slug = bp.stem
            voices_set.add(slug)
            voice_display[slug] = (
                council_name_by_slug.get(slug)
                or slug.replace("_", " ").title()
            )
            data = _read_json_or_none(bp) or {}
            for f in data.get("formulations", []) or []:
                tid = f.get("theme_id")
                if tid:
                    themes_set.add(tid)
                    expected_pairs.add((slug, tid))

    # Seed themes from Researcher's grouping.json — stable titles, one per
    # theme. Matches what we did for Provocateur drilldown.
    grouping = _read_json_or_none(run_dir / "02_researcher" / "grouping.json")
    if grouping is not None:
        for t in grouping.get("themes", []) or []:
            tid = t.get("theme_id")
            if tid:
                theme_titles[tid] = t.get("title") or tid

    # Overlay actual Step 1 / Step 2 progress. Don't overwrite voice_display
    # — council_member from Step 1/2 is the long identity-prefix opening
    # ("I am Augusta Ada King…") which is unsuitable as a display name.
    for c in s1_cells:
        voices_set.add(c["voice_slug"])
        themes_set.add(c["theme_id"])
        voice_display.setdefault(
            c["voice_slug"],
            council_name_by_slug.get(c["voice_slug"], c["voice_slug"].replace("_", " ").title()),
        )
        theme_titles.setdefault(c["theme_id"], c["theme_display_title"])
    for v in s2_voices:
        voices_set.add(v["voice_slug"])
        voice_display.setdefault(
            v["voice_slug"],
            council_name_by_slug.get(v["voice_slug"], v["voice_slug"].replace("_", " ").title()),
        )
        for tid in v["themes_covered"]:
            themes_set.add(tid)

    voices = [
        {"voice_slug": s, "council_member": voice_display.get(s, s)}
        for s in sorted(voices_set)
    ]
    themes = [
        {"theme_id": t, "theme_display_title": theme_titles.get(t, t)}
        for t in sorted(themes_set)
    ]

    cont_list = voice_continuity_list(
        PROJECT_ROOT, night, [v["voice_slug"] for v in voices],
    )

    # C28b: per-voice Step 2 validation results + operator decisions.
    step2_validation_by_slug = _load_step2_validation(run_dir)
    operator_decisions_by_slug = _load_operator_decisions(run_dir)
    # Compute the gate state inline so the dashboard banner doesn't need
    # to import from overnight_orchestrator.
    flagged_slugs = [
        s for s, v in step2_validation_by_slug.items()
        if v.get("overall_verdict") in ("WARN", "HOLD")
    ]
    undecided = [s for s in flagged_slugs if s not in operator_decisions_by_slug]
    validation_gate = {
        "step2_validation_present": len(step2_validation_by_slug) > 0,
        "n_total": len(step2_validation_by_slug),
        "n_flagged": len(flagged_slugs),
        "n_decided": len(flagged_slugs) - len(undecided),
        "undecided": undecided,
        "awaiting_operator": len(undecided) > 0,
    }

    # Manifest for top-line counts (validation_failures, etc.).
    manifest = _read_json_or_none(run_dir / "04_voice" / "manifest.json") or {}

    # Expose expected pairs as a flat list of "voice_slug|theme_id" strings
    # — Jinja2 lookups with tuple keys are awkward; strings work cleanly.
    expected_pairs_list = sorted(f"{v}|{t}" for v, t in expected_pairs)

    return {
        "night": night,
        "run_id": run_dir.name,
        "run_dir": str(run_dir),
        "run_exists": True,
        "voices": voices,
        "themes": themes,
        "expected_pairs": expected_pairs_list,
        "step1_cells": s1_cells,
        "validation_cells": val_cells,
        "step2_voices": s2_voices,
        "continuity_voices": cont_list,
        "step2_validation_by_slug": step2_validation_by_slug,  # C28b
        "operator_decisions_by_slug": operator_decisions_by_slug,  # C28b
        "validation_gate": validation_gate,  # C28b
        "manifest": {
            "counts": manifest.get("counts", {}),
            "validation_failures_count": len(
                manifest.get("validation_failures", [])
            ),
            "wall_clock_s": manifest.get("wall_clock_s"),
        },
        "polled_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


# C28b helpers — Step 2 validation files + operator decisions.

def _load_step2_validation(run_dir: Path) -> dict[str, dict[str, Any]]:
    """Load all per-voice Step 2 validation files. Returns {slug: payload}."""
    val_dir = run_dir / "04_voice" / "step2_validation"
    if not val_dir.exists():
        return {}
    out: dict[str, dict[str, Any]] = {}
    for p in sorted(val_dir.glob("*.json")):
        data = _read_json_or_none(p)
        if data is None:
            continue
        slug = data.get("voice_slug") or p.stem
        out[slug] = data
    return out


def _load_operator_decisions(run_dir: Path) -> dict[str, dict[str, Any]]:
    """Load all per-voice operator decision files. Returns {slug: payload}."""
    dec_dir = run_dir / "04_voice" / "operator_decisions"
    if not dec_dir.exists():
        return {}
    out: dict[str, dict[str, Any]] = {}
    for p in sorted(dec_dir.glob("*.json")):
        data = _read_json_or_none(p)
        if data is None:
            continue
        slug = data.get("voice_slug") or p.stem
        out[slug] = data
    return out


# --- Researcher Pipeline detail view (C23 Phase C, 2026-05-03) -------------
#
# Reads <run_dir>/02_researcher/grouping.json (canonical Researcher output)
# plus the per-session extraction inputs to render the theme/cluster tree
# and a per-session extraction summary. Athens working envelope: 200-400
# extractions, 25-50 clusters, 10-18 themes (revised up from 7-10 per
# v2.4 ratios applied to a 13-hour / 15-session night).


def collect_researcher_detail(night: int) -> dict[str, Any]:
    """Top-level payload for /admin/tonight/researcher.

    Renders themes (with their clusters and abstracts) plus the isolates list
    and a per-session extraction-count summary read from the per-session
    *_extractions.json files the Researcher writes alongside grouping.json.
    """
    run_dir = run_dir_for_night(night)
    base = {
        "night": night,
        "run_id": run_dir.name,
        "run_dir": str(run_dir),
        "polled_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    if not run_dir.exists():
        return {**base, "run_exists": False, "themes": [], "isolates": [],
                "per_session": [], "totals": {}}

    rsr_dir = run_dir / "02_researcher"
    grouping = _read_json_or_none(rsr_dir / "grouping.json")
    clusters_only = _read_json_or_none(rsr_dir / "clusters.json")

    # Helper: extraction IDs are namespaced `<session_slug>:<NNN>`. Count
    # distinct session_slug prefixes — exposes how many panels each cluster
    # or theme draws from (1 = single-panel cluster; >1 = cross-panel).
    def _n_sessions(ext_ids: list[str]) -> int:
        return len({eid.split(":", 1)[0] for eid in ext_ids if isinstance(eid, str) and ":" in eid})

    # Always-rendered clusters list — built from clusters.json (preferred,
    # raw Node 2 output) or grouping.json (fallback, when clusters.json is
    # absent but grouping.json reconstructs it). Shown in its own section so
    # the operator can see what Node 2 produced even after Node 3 has wrapped
    # the clusters into themes.
    all_clusters: list[dict[str, Any]] = []
    if clusters_only is not None:
        for c in clusters_only.get("clusters", []) or []:
            ext_ids = c.get("extraction_ids", []) or []
            all_clusters.append({
                "cluster_id": c.get("cluster_id"),
                "cluster_title": c.get("cluster_title"),
                "cluster_abstract": c.get("cluster_abstract"),
                "n_extractions": len(ext_ids),
                "n_sessions": _n_sessions(ext_ids),
            })
        cluster_isolates = clusters_only.get("isolates", []) or []
    elif grouping is not None:
        for t in grouping.get("themes", []):
            for c in t.get("clusters", []):
                ext_ids = c.get("extraction_ids", []) or []
                all_clusters.append({
                    "cluster_id": c.get("cluster_id"),
                    "cluster_title": c.get("cluster_title"),
                    "cluster_abstract": c.get("cluster_abstract"),
                    "n_extractions": len(ext_ids),
                    "n_sessions": _n_sessions(ext_ids),
                    "theme_id": t.get("theme_id"),
                })
        cluster_isolates = grouping.get("isolates", []) or []
    else:
        cluster_isolates = []

    # Themes are only knowable from grouping.json (Node 3 output).
    themes = []
    n_clusters_total = len(all_clusters)
    n_extractions_in_clusters = sum(c["n_extractions"] for c in all_clusters)
    if grouping is not None:
        for t in grouping.get("themes", []):
            clusters = []
            theme_ext_ids: list[str] = []
            for c in t.get("clusters", []):
                ext_ids = c.get("extraction_ids", []) or []
                theme_ext_ids.extend(ext_ids)
                clusters.append({
                    "cluster_id": c.get("cluster_id"),
                    "cluster_title": c.get("cluster_title"),
                    "cluster_abstract": c.get("cluster_abstract"),
                    "n_extractions": len(ext_ids),
                    "n_sessions": _n_sessions(ext_ids),
                })
            themes.append({
                "theme_id": t.get("theme_id"),
                "title": t.get("title"),
                "abstract": t.get("abstract"),
                "n_clusters": len(clusters),
                "n_extractions": sum(c["n_extractions"] for c in clusters),
                "n_sessions": _n_sessions(theme_ext_ids),
                "clusters": clusters,
            })
        isolates = grouping.get("isolates", []) or []
    else:
        isolates = cluster_isolates

    # Per-session extraction summary — pre-populate one row per upstream
    # transcription session_package.json so the operator sees the full
    # expected session list mid-Node-1, with each row's status flipping
    # from "pending" to extracted as <sid>_extractions.json files appear.
    per_session: list[dict[str, Any]] = []
    expected_sids: list[str] = []
    transcription_dir = run_dir / "01_transcription"
    if transcription_dir.exists():
        for sd in sorted(transcription_dir.iterdir()):
            if not sd.is_dir():
                continue
            if (sd / "session_package.json").exists():
                expected_sids.append(sd.name)

    for sid in expected_sids:
        per_session.append({
            "session_slug": sid,
            "filename": f"{sid}_extractions.json",
            "n_extractions": None,
            "mtime": None,
            "extracted": False,
        })

    # Overlay actual extraction file data when present.
    by_slug = {row["session_slug"]: row for row in per_session}
    for p in sorted(rsr_dir.glob("*_extractions.json")):
        if p.name == "all_extractions.json":
            continue
        data = _read_json_or_none(p) or {}
        if isinstance(data, list):
            n_ext = len(data)
        elif isinstance(data, dict):
            n_ext = len(data.get("extractions", []) or data.get("items", []) or [])
        else:
            n_ext = 0
        slug = p.stem.replace("_extractions", "")
        row = by_slug.get(slug)
        if row is None:
            row = {"session_slug": slug}
            per_session.append(row)
        row.update({
            "filename": p.name,
            "n_extractions": n_ext,
            "mtime": _file_mtime_iso(p),
            "extracted": True,
        })

    all_ext_path = rsr_dir / "all_extractions.json"
    n_extractions_total = None
    if all_ext_path.exists():
        all_data = _read_json_or_none(all_ext_path) or {}
        if isinstance(all_data, list):
            n_extractions_total = len(all_data)
        elif isinstance(all_data, dict):
            n_extractions_total = len(
                all_data.get("extractions", []) or all_data.get("items", []) or []
            )

    totals = {
        "n_themes": len(themes),
        "n_clusters": n_clusters_total,
        "n_extractions_in_clusters": n_extractions_in_clusters,
        "n_isolates": len(isolates),
        "n_extractions_total": n_extractions_total,
    }
    return {
        **base,
        "run_exists": True,
        "grouping_present": grouping is not None,
        "clusters_present": clusters_only is not None or grouping is not None,
        "grouping_mtime": (
            _file_mtime_iso(rsr_dir / "grouping.json") if grouping is not None else None
        ),
        "clusters_mtime": _file_mtime_iso(rsr_dir / "clusters.json"),
        "themes": themes,
        "all_clusters": all_clusters,
        "isolates": isolates,
        "per_session": per_session,
        "totals": totals,
    }


# --- Provocateur Pipeline detail view (C23 Phase C, 2026-05-03) ------------
#
# Reads <run_dir>/03_provocateur/{manifest.json, selection.json, triage_flags.json,
# triage_voices/<slug>.json, formulations/<theme>__<voice>.json, briefings/<slug>.json}
# to build:
#   - Triage matrix: voices × themes — activation strength + is_stretch
#   - Formulation grid: voices × themes — which pairs got assigned + written
#   - Theme flags table: per-theme worth_surfacing / audience_friction / fault_line
#   - Per-voice triage detail: ranked + flat themes with rationales
# Athens working envelope: 10 voices × 10-18 themes = 100-180 cells per matrix.


def _provocateur_triage_voices(prov_dir: Path) -> list[dict[str, Any]]:
    """One row per voice that wrote a triage_voices/<slug>.json."""
    tdir = prov_dir / "triage_voices"
    if not tdir.exists():
        return []
    out = []
    for p in sorted(tdir.glob("*.json")):
        data = _read_json_or_none(p) or {}
        out.append({
            "voice_slug": p.stem,
            "voice_name": data.get("voice", p.stem),
            "ranked_themes": data.get("ranked_themes", []) or [],
            "flat_themes": data.get("flat_themes", []) or [],
            "mtime": _file_mtime_iso(p),
        })
    return out


def _provocateur_triage_cells(
    triage_voices: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Flatten triage to a list of (voice, theme, activation, is_stretch, reason)
    cells suitable for matrix lookup."""
    cells = []
    for tv in triage_voices:
        for rt in tv["ranked_themes"]:
            cells.append({
                "voice_slug": tv["voice_slug"],
                "theme_id": rt.get("theme_id"),
                "kind": "ranked",
                "activation": rt.get("activation"),  # "strong" / "moderate" / "weak"
                "is_stretch": bool(rt.get("is_stretch")),
                "reason": rt.get("reason"),
            })
        for ft in tv["flat_themes"]:
            cells.append({
                "voice_slug": tv["voice_slug"],
                "theme_id": ft.get("theme_id"),
                "kind": "flat",
                "activation": "flat",
                "is_stretch": False,
                "reason": ft.get("reason"),
            })
    return cells


def _provocateur_formulation_cells(prov_dir: Path) -> list[dict[str, Any]]:
    """One cell per formulations/<theme>__<voice>.json on disk."""
    fdir = prov_dir / "formulations"
    if not fdir.exists():
        return []
    out = []
    for p in sorted(fdir.glob("*.json")):
        if "__" not in p.stem:
            continue
        theme_id, _, voice_slug = p.stem.partition("__")
        data = _read_json_or_none(p) or {}
        out.append({
            "voice_slug": voice_slug,
            "theme_id": theme_id,
            "mode": data.get("mode"),
            "council_member": data.get("member", voice_slug),
            "theme_display_title": data.get("theme_display_title", theme_id),
            "n_quotes": len(data.get("selected_quotes", []) or []),
            "n_grounding": len(data.get("grounding_extraction_ids", []) or []),
            "rationale": (data.get("rationale") or "").strip(),
            "mtime": _file_mtime_iso(p),
        })
    return out


def collect_provocateur_detail(night: int) -> dict[str, Any]:
    """Top-level payload for /admin/tonight/provocateur."""
    run_dir = run_dir_for_night(night)
    base = {
        "night": night,
        "run_id": run_dir.name,
        "run_dir": str(run_dir),
        "polled_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    if not run_dir.exists():
        return {**base, "run_exists": False}

    prov_dir = run_dir / "03_provocateur"
    manifest = _read_json_or_none(prov_dir / "manifest.json")
    selection = _read_json_or_none(prov_dir / "selection.json")
    triage_flags = _read_json_or_none(prov_dir / "triage_flags.json")

    if manifest is None and not (prov_dir.exists() and prov_dir.is_dir()):
        return {**base, "run_exists": True, "manifest_present": False}

    triage_voices = _provocateur_triage_voices(prov_dir)
    triage_cells = _provocateur_triage_cells(triage_voices)
    formulation_cells = _provocateur_formulation_cells(prov_dir)

    # Voices and themes — union from triage_voices + formulation_cells +
    # selection.assignments_by_member (in case some voice is in selection
    # but didn't write a triage_voices file, or vice versa).
    voices_set: set[str] = {tv["voice_slug"] for tv in triage_voices}
    voice_name: dict[str, str] = {tv["voice_slug"]: tv["voice_name"]
                                   for tv in triage_voices}
    themes_set: set[str] = set()
    theme_titles: dict[str, str] = {}
    for c in triage_cells:
        if c["theme_id"]:
            themes_set.add(c["theme_id"])
    for fc in formulation_cells:
        voices_set.add(fc["voice_slug"])
        voice_name.setdefault(fc["voice_slug"], fc["council_member"])
        if fc["theme_id"]:
            themes_set.add(fc["theme_id"])

    # Theme flags — list of per-theme metadata.
    theme_flags = (triage_flags or {}).get("theme_flags", []) or []
    for tf in theme_flags:
        if tf.get("theme_id"):
            themes_set.add(tf["theme_id"])

    # Use the Researcher's stable theme titles from grouping.json (one per
    # theme) for column headers — NOT the Provocateur's per-(voice, theme)
    # `theme_display_title` (which is a voice-flavored reframing that varies
    # by voice and would make the matrix headers inconsistent across rows).
    grouping = _read_json_or_none(run_dir / "02_researcher" / "grouping.json")
    if grouping is not None:
        for t in grouping.get("themes", []) or []:
            tid = t.get("theme_id")
            if tid:
                theme_titles[tid] = t.get("title") or tid
    # Fallback for any theme_id not in grouping (e.g. Provocateur dropped
    # or renamed) — use the Provocateur's title as a last resort.
    for fc in formulation_cells:
        if fc["theme_id"] and fc["theme_id"] not in theme_titles:
            theme_titles[fc["theme_id"]] = fc["theme_display_title"]

    voices = [
        {"voice_slug": s, "voice_name": voice_name.get(s, s)}
        for s in sorted(voices_set)
    ]
    themes = [
        {"theme_id": t, "theme_display_title": theme_titles.get(t, t)}
        for t in sorted(themes_set)
    ]

    # Selection — which themes got kept, dropped, and which voices fell short.
    sel = selection or {}
    counts = (manifest or {}).get("outputs", {})

    return {
        **base,
        "run_exists": True,
        "manifest_present": manifest is not None,
        "manifest_mtime": _file_mtime_iso(prov_dir / "manifest.json"),
        "voices": voices,
        "themes": themes,
        "triage_voices": triage_voices,
        "triage_cells": triage_cells,
        "formulation_cells": formulation_cells,
        "theme_flags": theme_flags,
        "selection": {
            "kept_themes": sel.get("kept_themes", []) or [],
            "dropped_themes": sel.get("dropped_themes", []) or [],
            "assignments_by_member": sel.get("assignments_by_member", {}) or {},
            "coverage_per_member": sel.get("coverage_per_member", {}) or {},
            "forced_fits": sel.get("forced_fits", []) or [],
            "stretch_swaps": sel.get("stretch_swaps", []) or [],
            "below_target": sel.get("below_target", []) or [],
        },
        # Per-voice {got, target} keyed by voice_slug — surfaces in the
        # Formulations grid row header so operator sees per-voice coverage
        # at a glance instead of having to scroll to the warning section.
        "coverage_by_slug": _build_coverage_by_slug(
            sel, voices, council_name_to_slug={
                m.get("name"): m.get("name", "").lower().replace(" ", "_").replace("'", "")
                for m in (_read_json_or_none(PROJECT_ROOT / "council_config.json") or {}).get("members", [])
            },
        ),
        "counts": {
            "n_themes_selected": counts.get("selected_themes", 0),
            "n_themes_dropped": counts.get("dropped_themes", 0),
            "n_formulations": counts.get("formulations", 0),
            "n_briefings_written": counts.get("briefings_written", 0),
            "n_forced_fits": counts.get("forced_fits", 0),
            "n_stretch_swaps": counts.get("stretch_swaps", 0),
            "n_voices_below_target": counts.get("voices_below_target", 0),
        },
    }


# --- Publish detail view (C23 Phase C, 2026-05-03) -------------------------
#
# Reads <PROJECT_ROOT>/published_artifacts/nights/night_<N>/{_index.json,
# <voice_slug>.json} for each voice. The index is the one Researcher /
# Provocateur / Voice all feed into via publish_flow.py.


def collect_publish_detail(night: int) -> dict[str, Any]:
    """Top-level payload for /admin/tonight/publish."""
    base = {
        "night": night,
        "run_id": run_dir_for_night(night).name,
        "polled_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    pub_dir = PROJECT_ROOT / "published_artifacts" / "nights" / f"night_{night}"
    index_path = pub_dir / "_index.json"
    if not index_path.exists():
        return {
            **base,
            "index_present": False,
            "voices": [],
            "totals": {"n_voices": 0},
        }

    idx = _read_json_or_none(index_path) or {}
    raw_voices = idx.get("voices", []) or []
    voices = []
    for vrow in raw_voices:
        slug = vrow.get("voice_slug")
        per_voice_path = pub_dir / f"{slug}.json"
        voices.append({
            "voice_slug": slug,
            "voice_name": vrow.get("voice_name") or slug,
            "url_path": vrow.get("url_path"),
            "title": vrow.get("title"),
            "subtitle": vrow.get("subtitle"),
            "selected_form": vrow.get("selected_form"),
            "stance": vrow.get("stance"),
            "themes_addressed": vrow.get("themes_addressed", []) or [],
            "decision": vrow.get("decision"),
            "amendment_count": vrow.get("amendment_count", 0),
            "word_count": vrow.get("word_count"),
            "has_per_voice_file": per_voice_path.exists(),
            "per_voice_mtime": _file_mtime_iso(per_voice_path),
        })
    return {
        **base,
        "index_present": True,
        "index_mtime": _file_mtime_iso(index_path),
        "url_path": idx.get("url_path"),
        "generated_at": idx.get("generated_at"),
        "voices": voices,
        "totals": {"n_voices": len(voices)},
    }


# --- Editor Pipeline detail view (post-B1, 2026-05-03 PM) ------------------
#
# Reads <run_dir>/05_editor/{theme_routing.json, dossiers/dossier_*.json,
# manifest.json}. Each dossier JSON is in the v2 schema (kicker, headline,
# subline, body_paragraphs[], headnotes[], front_abstract, colophon, metadata).


def collect_editor_detail(night: int) -> dict[str, Any]:
    """Top-level payload for /admin/tonight/editor.

    Renders:
      - top-line counts from manifest
      - theme_routing.json summary (voices_routing + refusals)
      - per-dossier rows (dossier_no, theme_id, kicker, headline, body word
        count, headnote count, file path)
    """
    run_dir = run_dir_for_night(night)
    base = {
        "night": night,
        "run_id": run_dir.name,
        "run_dir": str(run_dir),
        "polled_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    if not run_dir.exists():
        return {**base, "run_exists": False}

    editor_dir = run_dir / "05_editor"
    if not editor_dir.exists():
        return {**base, "run_exists": True, "editor_dir_present": False}

    manifest = _read_json_or_none(editor_dir / "manifest.json") or {}
    routing = _read_json_or_none(editor_dir / "theme_routing.json") or {}

    dossier_files = sorted((editor_dir / "dossiers").glob("dossier_*.json")) \
        if (editor_dir / "dossiers").exists() else []

    import re as _re
    _quote_re = _re.compile(r'(["“][^"”\n]{4,300}?["”])')
    dossiers = []
    for path in dossier_files:
        d = _read_json_or_none(path) or {}
        meta = d.get("metadata", {})
        body_paragraphs = d.get("body_paragraphs", []) or []
        word_count = sum(len((p or "").split()) for p in body_paragraphs if p != "* * *")
        body_text = "\n\n".join(p for p in body_paragraphs if p != "* * *")
        n_quotes = len(_quote_re.findall(body_text))
        dossiers.append({
            "dossier_no":         _extract_dossier_no(path),
            "theme_id":           meta.get("theme_id"),
            "theme_display_title": meta.get("theme_display_title"),
            "kicker":             d.get("kicker", ""),
            "headline":           d.get("headline", ""),
            "n_body_paragraphs":  len(body_paragraphs),
            "n_words":            word_count,
            "n_quotes":           n_quotes,
            "n_headnotes":        len(d.get("headnotes", []) or []),
            "filename":           path.name,
            "mtime":              _file_mtime_iso(path),
            "input_tokens":       meta.get("input_tokens"),
            "output_tokens":      meta.get("output_tokens"),
            "thinking_tokens":    meta.get("thinking_tokens"),
            "wall_clock_s":       meta.get("wall_clock_s"),
        })
    dossiers.sort(key=lambda x: (x["dossier_no"] or 0))

    return {
        **base,
        "run_exists": True,
        "editor_dir_present": True,
        "manifest_present": bool(manifest),
        "manifest_mtime": _file_mtime_iso(editor_dir / "manifest.json"),
        "routing_present": bool(routing),
        "counts": manifest.get("counts", {}),
        "dossier_failures": manifest.get("dossier_failures", []),
        "voices_routing": routing.get("voices_routing", []),
        "refusals": routing.get("refusals", []),
        "themes_to_dossiers": routing.get("themes_to_dossiers", []),
        "dossiers": dossiers,
    }


def _extract_dossier_no(path: Path) -> int | None:
    """Pull the integer N out of dossier_NNN.json filenames."""
    import re
    m = re.search(r"dossier_(\d+)", path.stem)
    return int(m.group(1)) if m else None


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
