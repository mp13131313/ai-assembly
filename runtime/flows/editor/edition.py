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

    `dossiers_by_theme` maps theme_id → full dossier dict (already
    written to disk). We also need each dossier's `dossier_no`, which
    we get from the routing manifest's `themes_to_dossiers`.
    """
    log = logger or logging.getLogger("editor_edition")

    themes_to_dossiers = routing.get("themes_to_dossiers", []) or []
    voices_routing = routing.get("voices_routing", []) or []
    theme_flags = _load_theme_flags(run_dir)

    # Inject dossier_no into each dossier dict's metadata-shim for index building.
    dno_by_theme = {d["theme_id"]: d["dossier_no"] for d in themes_to_dossiers}
    enriched_dossiers = []
    for tid, dossier in dossiers_by_theme.items():
        # shallow copy with dossier_no injected (don't mutate caller's dict).
        d = dict(dossier)
        d["dossier_no"] = dno_by_theme.get(tid, 0)
        enriched_dossiers.append(d)

    lead_no, audit = pick_lead_dossier(themes_to_dossiers, theme_flags)
    log.info(
        f"  Edition lead: dossier_{lead_no:03d} "
        f"(theme={audit['audit'][0]['theme_id'] if audit['audit'] else '?'}; "
        f"score={audit['audit'][0]['score'] if audit['audit'] else 0})"
    )

    # Per-night index (only if there are dossiers)
    if enriched_dossiers:
        night_idx = build_night_index(night, enriched_dossiers, lead_no, voices_routing)
        idx_path = (
            project_root / "published_artifacts" / "dossiers"
            / f"night_{night}" / "_index.json"
        )
        idx_path.parent.mkdir(parents=True, exist_ok=True)
        write_json_atomic(idx_path, night_idx)
        log.info(f"  wrote {idx_path.name}")

    # Aggregate root index across all nights present
    update_root_index(project_root)
    log.info("  rebuilt root _index.json")

    return {
        "lead_dossier_no": lead_no,
        "scoring_audit":   audit,
    }
