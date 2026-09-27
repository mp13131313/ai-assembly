"""Editor Pipeline — Stage 3: edition lead picker + per-night index.

Per spec (`runtime/OPEN_ITEMS.md` B3): the "edition" concept is per-night
and currently does ONE thing — pick which dossier is tonight's lead so
the microsite knows what to feature in the lead-vs-grid layout.

This module implements **option 2 — algorithmic** (deterministic, no LLM
call). Score each dossier by a small set of theme-flag signals and pick
the highest-scoring as lead. Operator can override after the fact by
hand-editing `published_artifacts/dossiers/night_<N>/_index.json` (the
microsite reads `edition_lead.lead_dossier_no` directly; runtime won't
clobber it on subsequent runs unless the dossier set changes).

Scoring (deterministic, tunable via constants):

    score =
        n_engaged_voices         × ENGAGEMENT_WEIGHT
      + audience_friction_value  × FRICTION_WEIGHT
      + (FAULT_LINE_BONUS if theme_flags.fault_line_present else 0)

Tiebreak: lowest theme_id (stable, deterministic across reruns).

Side-effects:
- writes `published_artifacts/dossiers/night_<N>/_index.json` with the
  full per-dossier roll-up + `edition_lead.lead_dossier_no`
- rebuilds `published_artifacts/dossiers/_index.json` aggregating the
  per-night indices into `editions_by_night` + a flat `dossiers` list
"""
from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from flows.shared.io import write_json_atomic  # noqa: E402


# Scoring weights — tunable. Defaults tuned so a 5-voice high-friction
# fault-line theme decisively beats a 2-voice low-friction theme.
ENGAGEMENT_WEIGHT = 10
FRICTION_VALUES = {"high": 100, "moderate": 50, "low": 10}
FAULT_LINE_BONUS = 50


def _load_theme_flags(run_dir: Path) -> dict[str, dict[str, Any]]:
    """Read all per-voice briefings and return theme_id → theme_flags map.

    The same theme appears in multiple voice briefings carrying identical
    `full_theme_record.theme_flags` (Provocateur is passthrough on theme
    metadata). We take the first non-empty flags object per theme_id.
    """
    out: dict[str, dict[str, Any]] = {}
    briefings_dir = run_dir / "03_provocateur" / "briefings"
    if not briefings_dir.exists():
        return out
    for path in sorted(briefings_dir.glob("*.json")):
        try:
            with path.open(encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError):
            continue
        for fmt in data.get("formulations") or []:
            tid = fmt.get("theme_id")
            if not tid or tid in out:
                continue
            ftr = fmt.get("full_theme_record", {}) or {}
            flags = ftr.get("theme_flags", {}) or {}
            if flags:
                out[tid] = flags
    return out


def _score_dossier(dossier_meta: dict[str, Any], theme_flags: dict[str, Any]) -> int:
    """Score one dossier for lead-pick competition. Higher = more likely
    to lead. See module docstring for the formula."""
    n_voices = int(dossier_meta.get("n_engaged_voices", 0) or 0)
    friction = (theme_flags.get("audience_friction") or "low").lower()
    fault = bool(theme_flags.get("fault_line_present"))
    return (
        n_voices * ENGAGEMENT_WEIGHT
        + FRICTION_VALUES.get(friction, FRICTION_VALUES["low"])
        + (FAULT_LINE_BONUS if fault else 0)
    )


def pick_lead_dossier(
    themes_to_dossiers: list[dict[str, Any]],
    theme_flags_by_theme: dict[str, dict[str, Any]],
) -> tuple[int, dict[str, Any]]:
    """Pick the lead dossier_no.

    Returns (lead_dossier_no, scoring_audit) where scoring_audit is a
    list of {dossier_no, theme_id, score, n_voices, friction, fault_line}
    so the operator can see why a given dossier won (and override if
    they disagree).

    Returns (0, ...) if there are no dossiers — caller handles.
    """
    if not themes_to_dossiers:
        return 0, {"audit": [], "winner_dossier_no": 0}

    audit = []
    for d in themes_to_dossiers:
        flags = theme_flags_by_theme.get(d.get("theme_id"), {})
        score = _score_dossier(d, flags)
        audit.append({
            "dossier_no":  d.get("dossier_no"),
            "theme_id":    d.get("theme_id"),
            "theme_title": d.get("theme_title", ""),
            "n_voices":    d.get("n_engaged_voices", 0),
            "audience_friction": flags.get("audience_friction"),
            "fault_line_present": bool(flags.get("fault_line_present")),
            "score": score,
        })
    # Sort: highest score first; tiebreak by lowest theme_id (deterministic).
    audit.sort(key=lambda x: (-x["score"], x["theme_id"] or ""))
    winner = audit[0]["dossier_no"]
    return winner, {"audit": audit, "winner_dossier_no": winner}


def build_night_index(
    night: int,
    dossiers: list[dict[str, Any]],
    lead_dossier_no: int,
    voices_routing: list[dict[str, Any]],
) -> dict[str, Any]:
    """Build the per-night `_index.json` payload.

    `dossiers` is the list of full dossier dicts (after stamp_runtime).
    `voices_routing` is `theme_routing.voices_routing` so we can list
    each dossier's engaged voices in the index without re-reading files.
    """
    by_dossier_no: dict[int, list[dict[str, Any]]] = {}
    for v in voices_routing:
        dno = v.get("primary_dossier", 0)
        by_dossier_no.setdefault(dno, []).append({
            "voice_slug":    v.get("voice_slug"),
            "voice_name":    v.get("voice_name"),
            "primary_theme": v.get("primary_theme"),
            "url_path":      f"/night-{night}/{v.get('voice_slug')}",
        })

    items = []
    for d in sorted(dossiers, key=lambda x: x.get("metadata", {}).get("theme_id", "")):
        meta = d.get("metadata") or {}
        dno = _dossier_no_from_metadata(meta, d)
        items.append({
            "dossier_no":           dno,
            "filename":             f"dossier_{dno:03d}.json",
            "url_path":             f"/dossiers/night-{night}/dossier_{dno:03d}",
            "kicker":               d.get("kicker", ""),
            "headline":             d.get("headline", ""),
            "subline":              d.get("subline", ""),
            "theme_id":             meta.get("theme_id"),
            "theme_display_title":  meta.get("theme_display_title"),
            "voice_count":          len(by_dossier_no.get(dno, [])),
            "voices_routed":        by_dossier_no.get(dno, []),
        })
    items.sort(key=lambda x: x["dossier_no"])

    return {
        "night":          night,
        "url_path":       f"/dossiers/night-{night}",
        "generated_at":   datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "dossier_count":  len(items),
        "edition_lead":   {"lead_dossier_no": lead_dossier_no} if lead_dossier_no else None,
        "dossiers":       items,
    }


def _dossier_no_from_metadata(meta: dict, dossier: dict) -> int:
    """The dossier_no isn't on the dossier dict directly; we derive it
    from the filename when called from finalize_edition. Caller passes
    the dossier_no in via a metadata-shim if it knows it."""
    if "dossier_no" in meta:
        return int(meta["dossier_no"])
    if "dossier_no" in dossier:
        return int(dossier["dossier_no"])
    return 0


def update_root_index(project_root: Path) -> dict[str, Any]:
    """Rebuild `published_artifacts/dossiers/_index.json` aggregating all
    nights present. Reads each `night_<N>/_index.json` and stitches.
    Idempotent — safe to call after every editor run."""
    dossiers_dir = project_root / "published_artifacts" / "dossiers"
    if not dossiers_dir.exists():
        return {}

    nights_present: list[int] = []
    editions_by_night: dict[str, dict[str, Any]] = {}
    flat_dossiers: list[dict[str, Any]] = []
    total = 0
    for night_dir in sorted(dossiers_dir.glob("night_*")):
        # Skip backup directories like night_1.baseline_pre_*
        if "." in night_dir.name:
            continue
        try:
            n = int(night_dir.name.removeprefix("night_"))
        except ValueError:
            continue
        idx_path = night_dir / "_index.json"
        if not idx_path.exists():
            continue
        try:
            with idx_path.open(encoding="utf-8") as f:
                night_idx = json.load(f)
        except (OSError, json.JSONDecodeError):
            continue
        nights_present.append(n)
        if night_idx.get("edition_lead"):
            editions_by_night[str(n)] = night_idx["edition_lead"]
        for d in night_idx.get("dossiers", []):
            flat_dossiers.append({
                "night":       n,
                "dossier_no":  d.get("dossier_no"),
                "filename":    d.get("filename"),
                "url_path":    d.get("url_path"),
                "kicker":      d.get("kicker", ""),
                "headline":    d.get("headline", ""),
                "theme_id":    d.get("theme_id"),
                "theme_display_title": d.get("theme_display_title"),
            })
            total += 1

    payload = {
        "generated_at":      datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "nights_present":    sorted(nights_present),
        "dossier_count":     total,
        "editions_by_night": editions_by_night,
        "dossiers":          flat_dossiers,
    }
    write_json_atomic(dossiers_dir / "_index.json", payload)
    return payload


def _rebuild_dossiers_from_disk(
    project_root: Path, night: int
) -> list[dict[str, Any]]:
    """Read every dossier actually on disk for this night, not just the
    one(s) the current Editor Pipeline call regenerated.

    C46 fix — same bug class as C50 (`voice/publish.py::
    _rebuild_index_from_disk`): mirror its approach. An `--single-dossier`
    rerun only passes this call's freshly-generated dossier(s) via
    `finalize_edition`'s `dossiers_by_theme`, but every dossier previously
    published for the night is still sitting at
    `published_artifacts/dossiers/night_<N>/dossier_<NNN>.json`
    (`write_dossier` in `flows/editor/publish.py` writes there
    unconditionally, and has already run for THIS call's dossier(s) by
    the time Stage 3 fires — see `editor_flow.py`). Source of truth for
    the night index is therefore the directory listing, so a
    single-dossier rerun still leaves every other dossier indexed.

    `dossier_no` is parsed from the filename (`dossier_NNN.json`) rather
    than trusted from the dossier's own `metadata` — reliable regardless
    of what a given dossier's metadata carries, and matches the filename
    convention `_dossier_filename()` writes in `flows/editor/publish.py`.

    Files that fail to parse are skipped (defensive; should not happen
    for files this pipeline itself wrote via `write_json_atomic`).
    Returns `[]` if the night's published dossiers directory doesn't
    exist yet (nothing to index).
    """
    dossiers_dir = (
        project_root / "published_artifacts" / "dossiers" / f"night_{night}"
    )
    if not dossiers_dir.exists():
        return []
    out: list[dict[str, Any]] = []
    for path in sorted(dossiers_dir.glob("dossier_*.json")):
        try:
            dossier_no = int(path.stem.removeprefix("dossier_"))
        except ValueError:
            continue
        try:
            with path.open(encoding="utf-8") as f:
                dossier = json.load(f)
        except (OSError, json.JSONDecodeError):
            continue
        # shallow copy with dossier_no injected (don't mutate the parsed dict
        # in place — harmless here, but matches the no-mutation convention
        # the old in-memory enrichment used).
        d = dict(dossier)
        d["dossier_no"] = dossier_no
        out.append(d)
    return out


def finalize_edition(
    *,
    run_dir: Path,
    project_root: Path,
    night: int,
    routing: dict[str, Any],
    dossiers_by_theme: dict[str, dict[str, Any]],
    logger: logging.Logger | None = None,
) -> dict[str, Any]:
    """Stage 3: lead-pick + index writes. Returns the audit payload.

    `dossiers_by_theme` maps theme_id → full dossier dict for the
    dossier(s) THIS call regenerated (already written to disk by the
    caller before Stage 3 runs). It is used here only as a sanity check
    that those writes actually landed — the night index itself is
    rebuilt from every dossier file on disk (C46; see
    `_rebuild_dossiers_from_disk`), NOT from this dict, so a
    `--single-dossier` rerun doesn't drop the dossiers it didn't touch.

    The lead-pick (`pick_lead_dossier`) was already immune to the C46
    bug: it scores off `routing["themes_to_dossiers"]` and
    `_load_theme_flags(run_dir)`, both of which are read fresh from the
    FULL night's Stage 1 routing manifest and Provocateur briefings on
    disk. Neither is filtered by `--single-dossier` — that flag only
    narrows which dossier(s) Stage 2 regenerates (see `editor_flow.py`'s
    `dossier_specs` filtering vs. the unfiltered `routing` it passes
    through here). So the lead is always picked across every dossier
    routed for the night, never just the one(s) reprocessed in this
    call — no recovery-from-disk was needed for the lead-pick itself.
    """
    log = logger or logging.getLogger("editor_edition")

    themes_to_dossiers = routing.get("themes_to_dossiers", []) or []
    voices_routing = routing.get("voices_routing", []) or []
    theme_flags = _load_theme_flags(run_dir)

    lead_no, audit = pick_lead_dossier(themes_to_dossiers, theme_flags)
    log.info(
        f"  Edition lead: dossier_{lead_no:03d} "
        f"(theme={audit['audit'][0]['theme_id'] if audit['audit'] else '?'}; "
        f"score={audit['audit'][0]['score'] if audit['audit'] else 0})"
    )

    # Per-night index — rebuilt from every dossier on disk (C46), so a
    # `--single-dossier` rerun still leaves the full night indexed.
    all_dossiers = _rebuild_dossiers_from_disk(project_root, night)

    # Defensive: confirm this call's own dossier(s) actually made it to
    # disk before we index off the directory listing. Should never fire
    # (write_dossier already ran and raises on failure) — a warning here
    # would mean the index is missing something the caller thinks it wrote.
    processed_theme_ids = set(dossiers_by_theme.keys())
    on_disk_theme_ids = {
        d.get("metadata", {}).get("theme_id") for d in all_dossiers
    }
    missing = processed_theme_ids - on_disk_theme_ids
    if missing:
        log.warning(
            f"  dossier(s) processed this call not found on disk under "
            f"published_artifacts/dossiers/night_{night}/: {sorted(missing)} "
            f"— index will be missing them too"
        )

    if all_dossiers:
        night_idx = build_night_index(night, all_dossiers, lead_no, voices_routing)
        idx_path = (
            project_root / "published_artifacts" / "dossiers"
            / f"night_{night}" / "_index.json"
        )
        idx_path.parent.mkdir(parents=True, exist_ok=True)
        write_json_atomic(idx_path, night_idx)
        log.info(
            f"  wrote {idx_path.name} ({len(all_dossiers)} dossier(s) on disk; "
            f"{len(processed_theme_ids)} regenerated this call)"
        )

    # Aggregate root index across all nights present
    update_root_index(project_root)
    log.info("  rebuilt root _index.json")

    return {
        "lead_dossier_no": lead_no,
        "scoring_audit":   audit,
    }
