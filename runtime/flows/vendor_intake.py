#!/usr/bin/env python3
"""Vendor intake — validate and land vendor-supplied session_package.json.

Five Athens 2026 sessions (the AI Democracy Marathon mobile / nightwalk
sessions tagged ``audio_source: "vendor"`` in reference/sessions.json) are
delivered as JSON in our session_package schema by an external production
vendor. They skip Stage 0 (audio normalization) and Stage 1 (ASR + speaker
ID + cleaning) entirely — the vendor does the equivalent work and hands us
a finished session_package.

This script is the gate. It validates the payload against the schema in
docs/AI_Assembly_Transcription_Pipeline.md §"Step 5 Output", normalizes a
few warn-and-accept drift cases (vendor reality wins on roster, defaults
on missing review_queue), and lands two files at the canonical Stage 1
output boundary:

    <run_dir>/01_transcription/<session_id>/session_package.json
    <run_dir>/01_transcription/<session_id>/status.json   {state=done, source=vendor}
    <run_dir>/01_transcription/<session_id>/vendor.flag   {source_path, ingested_at}

The orchestrator's transcription gate (overnight_orchestrator.py) reads
status.json with state=done and counts vendor sessions exactly the same as
audio sessions; the Researcher reads session_package.json via
``*/session_package.json`` glob — both are agnostic to source.

On validation failure, writes ``vendor.error`` (the schema diff) and
status.json with state=error so the dashboard surfaces the failure the
same way as a transcription error.

Usage
-----
Single-file mode (one session at a time):

    python -m flows.vendor_intake \\
        /path/to/vendor_session_007.json \\
        --run-dir runs/athens_night_1 \\
        --session-id day_one_demos_ai_democracy_marathon_human_democracy_is_dead_1330

Sweep mode (all vendor sessions for a night in one shot):

    python -m flows.vendor_intake --night 1 --sweep [--inbox <dir>]

Sweep reads PROJECT_ROOT/reference/sessions.json, finds every session with
``audio_source: "vendor"`` AND ``day`` mapping to ``--night``, and for each
looks for ``<inbox>/<session_id>.json`` (default inbox:
``<PROJECT_ROOT>/vendor_inbox``). Each found file is validated + landed via
the same path as single-file mode; missing files are reported but don't
abort the sweep.

If --run-dir is relative, it is resolved under PROJECT_ROOT.

Validation strictness
---------------------
**Hard fail** (vendor.error, status=error, exit 2):
    - file not parseable as JSON
    - missing top-level metadata or transcript
    - metadata.session_id != --session-id arg
    - transcript.turns[] empty or missing
    - any turn missing speaker / role / text
    - confidence value outside {high, medium, low} after lowercase

**Warn-and-accept** (vendor.warnings written, status=done, exit 0):
    - review_queue missing → empty stub injected
    - turn_index missing → injected via load_session_package normalizer
    - metadata.roster differs from sessions.json → vendor wins, warning logged
    - speakers_present differs from distinct turn speakers → recomputed
    - role outside {moderator, panelist, audience} → defaulted to "panelist"
    - whitespace artifacts in text → silent strip
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from flows.shared.io import load_session_package, write_json_atomic  # noqa: E402
from flows.shared.project_root import resolve_project_root  # noqa: E402


VALID_CONFIDENCES = {"high", "medium", "low"}
VALID_ROLES = {"moderator", "panelist", "audience"}

# Athens night → "day" string in sessions.json + run_dir name. Matches
# DAY_TO_RUN in runtime/ingest/config.py and the orchestrator. Kept inline
# rather than imported so flows/ doesn't depend on ingest/.
NIGHT_TO_DAY = {1: "Day One", 2: "Day Two", 3: "Day Three"}
NIGHT_TO_RUN_DIR = {1: "athens_night_1", 2: "athens_night_2", 3: "athens_night_3"}


# --- Validation outcome types ------------------------------------------------


class HardFail(Exception):
    """Raised on a schema violation that we cannot recover from."""

    def __init__(self, reasons: list[str]):
        self.reasons = reasons
        super().__init__("; ".join(reasons))


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# --- Core validation ---------------------------------------------------------


def validate_and_normalize(
    payload: dict[str, Any],
    *,
    expected_session_id: str,
    sessions_json_roster: list[dict[str, str]] | None = None,
) -> tuple[dict[str, Any], list[str]]:
    """Validate payload against session_package schema, normalize drift.

    Returns (normalized_payload, warnings). Raises HardFail on unrecoverable
    schema violations.

    `sessions_json_roster` is the roster from reference/sessions.json for
    this session_id; if provided and differs from payload metadata.roster,
    a warning is recorded but vendor reality wins (per operator default).
    """
    reasons: list[str] = []
    warnings: list[str] = []

    if not isinstance(payload, dict):
        raise HardFail(["top-level payload is not a JSON object"])

    metadata = payload.get("metadata")
    if not isinstance(metadata, dict):
        reasons.append("missing or non-dict metadata")
    transcript = payload.get("transcript")
    if not isinstance(transcript, dict):
        reasons.append("missing or non-dict transcript")
    if reasons:
        raise HardFail(reasons)

    if metadata.get("session_id") != expected_session_id:
        raise HardFail([
            f"metadata.session_id={metadata.get('session_id')!r} does not "
            f"match --session-id {expected_session_id!r}"
        ])

    turns = transcript.get("turns")
    if not isinstance(turns, list) or len(turns) == 0:
        raise HardFail(["transcript.turns missing or empty"])

    # Hard-validate each turn. Collect ALL reasons before raising, so the
    # operator gets one clear vendor.error file rather than one-fix-at-a-time.
    for i, turn in enumerate(turns):
        if not isinstance(turn, dict):
            reasons.append(f"turn[{i}] is not a dict")
            continue
        for required in ("speaker", "role", "text"):
            v = turn.get(required)
            if v is None or (isinstance(v, str) and not v.strip()):
                reasons.append(f"turn[{i}] missing required field {required!r}")
        conf = turn.get("confidence")
        if conf is not None:
            conf_norm = str(conf).strip().lower()
            if conf_norm not in VALID_CONFIDENCES:
                reasons.append(
                    f"turn[{i}] confidence={conf!r} not in {sorted(VALID_CONFIDENCES)}"
                )
    if reasons:
        raise HardFail(reasons)

    # Normalization pass — mutates a deep-copy via JSON round-trip so the
    # caller's payload isn't surprised in-place.
    pkg: dict[str, Any] = json.loads(json.dumps(payload))
    pkg_meta = pkg["metadata"]
    pkg_transcript = pkg["transcript"]
    pkg_turns = pkg_transcript["turns"]

    for i, turn in enumerate(pkg_turns):
        # Confidence: lowercase or default to "high".
        conf = turn.get("confidence")
        if conf is None:
            turn["confidence"] = "high"
            warnings.append(f"turn[{i}] confidence missing — defaulted to 'high'")
        else:
            turn["confidence"] = str(conf).strip().lower()

        # Role: snap to known set or default to panelist.
        role = str(turn.get("role", "")).strip().lower()
        if role not in VALID_ROLES:
            warnings.append(
                f"turn[{i}] role={turn.get('role')!r} not in {sorted(VALID_ROLES)} — "
                f"defaulted to 'panelist'"
            )
            turn["role"] = "panelist"
        else:
            turn["role"] = role

        # Whitespace-strip text (silent — drift not worth surfacing).
        if isinstance(turn.get("text"), str):
            turn["text"] = turn["text"].strip()

    # speakers_present: recompute from turns if absent or mismatched. The
    # transcription pipeline contract says this is "named individuals who
    # actually spoke" — a subset/superset of the roster including audience
    # members (Audience Member 1, 2, ...).
    distinct_speakers = sorted({turn["speaker"] for turn in pkg_turns})
    declared = pkg_transcript.get("speakers_present")
    if declared is None:
        pkg_transcript["speakers_present"] = distinct_speakers
        warnings.append(
            f"transcript.speakers_present missing — recomputed from turns: "
            f"{distinct_speakers}"
        )
    elif sorted(declared) != distinct_speakers:
        warnings.append(
            f"transcript.speakers_present={sorted(declared)} differs from "
            f"distinct turn speakers={distinct_speakers} — recomputed"
        )
        pkg_transcript["speakers_present"] = distinct_speakers

    # review_queue: inject empty stub if absent. The Researcher reads
    # review_queue.verify_markers; missing key is functionally identical to
    # an empty list, but having the structure makes downstream code
    # cleaner and matches the Step 5 schema in the transcription pipeline doc.
    if "review_queue" not in pkg:
        pkg["review_queue"] = {
            "low_confidence_attributions": [],
            "verify_markers": [],
            "diarization_flags": [],
        }
        # Don't warn — vendor not supplying an empty review_queue is the
        # normal case for clean vendor output (no [verify] markers, no
        # diarization corrections to log).

    # Roster cross-check — vendor wins on drift, warn for the operator.
    if sessions_json_roster is not None:
        vendor_names = sorted({m.get("name", "") for m in pkg_meta.get("roster") or []})
        sessions_names = sorted({m.get("name", "") for m in sessions_json_roster})
        if vendor_names != sessions_names:
            warnings.append(
                f"metadata.roster differs from sessions.json — "
                f"vendor: {vendor_names} | sessions.json: {sessions_names}. "
                f"Vendor reality wins; vendor.roster preserved in session_package."
            )

    # Source attestation — record on the package so downstream auditing can
    # trace where this transcript came from. Non-load_session_package code
    # paths in the codebase are unaffected (extra metadata key is benign).
    pkg_meta.setdefault("source", "vendor")

    return pkg, warnings


# --- Lander ------------------------------------------------------------------


def land(
    *,
    vendor_file: Path,
    run_dir: Path,
    session_id: str,
    sessions_json_roster: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    """Validate vendor_file and write session_package.json + sentinels.

    Returns a result dict with at least {"state", "session_dir"}; on
    success state="done", on failure state="error". Always writes
    status.json so the orchestrator's gate sees a definitive outcome.
    """
    session_dir = run_dir / "01_transcription" / session_id
    session_dir.mkdir(parents=True, exist_ok=True)
    status_path = session_dir / "status.json"
    package_path = session_dir / "session_package.json"
    flag_path = session_dir / "vendor.flag"
    error_path = session_dir / "vendor.error"
    warnings_path = session_dir / "vendor.warnings"

    # Clear previous vendor sidecars so re-runs leave a clean state. We do
    # NOT remove session_package.json — if the previous run left a valid
    # package and the new validation fails, we'd rather keep the older
    # valid package than leave the orchestrator stuck. The status.json
    # write below will flip state appropriately.
    for sidecar in (flag_path, error_path, warnings_path):
        if sidecar.exists():
            sidecar.unlink()

    started_at = _now_iso()

    # Read + parse.
    try:
        payload = json.loads(vendor_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        error_text = f"failed to read/parse vendor file: {e}"
        write_json_atomic(error_path, {"reasons": [error_text]})
        write_json_atomic(status_path, {
            "session_id": session_id,
            "state": "error",
            "source": "vendor",
            "started_at": started_at,
            "completed_at": _now_iso(),
            "error": error_text,
            "vendor_file": str(vendor_file),
        })
        return {"state": "error", "session_dir": session_dir, "error": error_text}

    # Validate + normalize.
    try:
        pkg, warnings = validate_and_normalize(
            payload,
            expected_session_id=session_id,
            sessions_json_roster=sessions_json_roster,
        )
    except HardFail as e:
        write_json_atomic(error_path, {
            "reasons": e.reasons,
            "vendor_file": str(vendor_file),
            "validated_at": _now_iso(),
        })
        write_json_atomic(status_path, {
            "session_id": session_id,
            "state": "error",
            "source": "vendor",
            "started_at": started_at,
            "completed_at": _now_iso(),
            "error": str(e),
            "vendor_file": str(vendor_file),
        })
        return {"state": "error", "session_dir": session_dir, "error": str(e)}

    # Write the normalized package, then re-load via the canonical
    # normalizer so turn_index gets injected if the vendor omitted it.
    write_json_atomic(package_path, pkg)
    try:
        load_session_package(package_path)  # validates turn_index alignment
    except ValueError as e:
        # turn_index out of order — bail with a hard failure, since this
        # would cascade into a corrupt Researcher run.
        error_text = f"turn_index alignment check failed: {e}"
        write_json_atomic(error_path, {
            "reasons": [error_text], "vendor_file": str(vendor_file),
        })
        write_json_atomic(status_path, {
            "session_id": session_id,
            "state": "error",
            "source": "vendor",
            "started_at": started_at,
            "completed_at": _now_iso(),
            "error": error_text,
            "vendor_file": str(vendor_file),
        })
        return {"state": "error", "session_dir": session_dir, "error": error_text}

    if warnings:
        write_json_atomic(warnings_path, {
            "warnings": warnings,
            "vendor_file": str(vendor_file),
            "validated_at": _now_iso(),
        })

    # Success: write the flag + status.
    write_json_atomic(flag_path, {
        "source_path": str(vendor_file),
        "ingested_at": _now_iso(),
        "n_turns": len(pkg["transcript"]["turns"]),
        "n_warnings": len(warnings),
    })
    write_json_atomic(status_path, {
        "session_id": session_id,
        "state": "done",
        "source": "vendor",
        "started_at": started_at,
        "completed_at": _now_iso(),
        "vendor_file": str(vendor_file),
        "n_turns": len(pkg["transcript"]["turns"]),
        "n_warnings": len(warnings),
    })
    return {
        "state": "done",
        "session_dir": session_dir,
        "warnings": warnings,
        "n_turns": len(pkg["transcript"]["turns"]),
    }


# --- CLI ---------------------------------------------------------------------


def _vendor_sessions_for_night(
    project_root: Path, night: int
) -> list[str]:
    """Return session_ids of all audio_source=='vendor' sessions for `night`,
    by reading PROJECT_ROOT/reference/sessions.json.

    Empty list if none match (or if sessions.json is missing/malformed —
    sweep callers see "0 vendor sessions for night N" rather than a crash).
    """
    sessions_path = project_root / "reference" / "sessions.json"
    if not sessions_path.exists():
        return []
    try:
        sessions = json.loads(sessions_path.read_text(encoding="utf-8")).get("sessions", [])
    except (OSError, json.JSONDecodeError):
        return []
    target_day = NIGHT_TO_DAY.get(night)
    if target_day is None:
        return []
    return [
        s["session_id"]
        for s in sessions
        if s.get("audio_source") == "vendor"
        and s.get("day") == target_day
        and s.get("ai_assembly")
        and "session_id" in s
    ]


def sweep(
    *,
    project_root: Path,
    night: int,
    inbox_dir: Path,
    run_dir: Path | None = None,
) -> dict[str, Any]:
    """Land every vendor session for `night` whose file is present in `inbox_dir`.

    Convention: each vendor file is named ``<session_id>.json`` at the top
    of inbox_dir. Sessions whose file is missing are reported as "missing"
    but do not abort the sweep.

    Returns a summary dict with per-session outcome and aggregate counts.
    Uses the same `land()` function as single-file mode, so validation
    semantics, sidecar files, and status.json shape are all identical.
    """
    if run_dir is None:
        run_dir = project_root / "runs" / NIGHT_TO_RUN_DIR[night]

    session_ids = _vendor_sessions_for_night(project_root, night)
    landed: list[dict[str, Any]] = []
    missing: list[str] = []
    errors: list[dict[str, Any]] = []
    warnings_total = 0

    for sid in session_ids:
        candidate = inbox_dir / f"{sid}.json"
        if not candidate.exists():
            missing.append(sid)
            continue
        sessions_json_roster = _load_sessions_json_roster(project_root, sid)
        result = land(
            vendor_file=candidate,
            run_dir=run_dir,
            session_id=sid,
            sessions_json_roster=sessions_json_roster,
        )
        if result["state"] == "error":
            errors.append({"session_id": sid, "error": result.get("error")})
        else:
            landed.append({
                "session_id": sid,
                "n_turns": result.get("n_turns"),
                "n_warnings": len(result.get("warnings", [])),
            })
            warnings_total += len(result.get("warnings", []))

    return {
        "night": night,
        "inbox_dir": str(inbox_dir),
        "run_dir": str(run_dir),
        "expected_count": len(session_ids),
        "landed": landed,
        "missing": missing,
        "errors": errors,
        "warnings_total": warnings_total,
    }


def _load_sessions_json_roster(
    project_root: Path, session_id: str
) -> list[dict[str, str]] | None:
    """Look up the roster for `session_id` from PROJECT_ROOT/reference/sessions.json
    and join speakers.json bios. Returns None if not found (downstream
    validation skips the cross-check rather than hard-failing)."""
    sessions_path = project_root / "reference" / "sessions.json"
    speakers_path = project_root / "reference" / "speakers.json"
    if not sessions_path.exists():
        return None
    try:
        sessions = json.loads(sessions_path.read_text(encoding="utf-8")).get("sessions", [])
    except (OSError, json.JSONDecodeError):
        return None
    sess = next((s for s in sessions if s.get("session_id") == session_id), None)
    if sess is None:
        return None
    speakers_by_name: dict[str, dict] = {}
    if speakers_path.exists():
        try:
            speakers_by_name = {
                s.get("name"): s
                for s in json.loads(speakers_path.read_text(encoding="utf-8")).get("speakers", [])
                if s.get("name")
            }
        except (OSError, json.JSONDecodeError):
            pass
    roster = []
    for name in sess.get("speakers", []):
        sp = speakers_by_name.get(name, {})
        roster.append({
            "name": name,
            "title": sp.get("title", ""),
            "affiliation": sp.get("affiliation", ""),
            "bio": sp.get("bio", ""),
        })
    return roster


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("vendor_file", nargs="?", type=Path, default=None,
                    help="Path to the vendor-supplied session_package JSON "
                         "(single-file mode). Omit when using --sweep.")
    ap.add_argument("--run-dir", type=Path, default=None,
                    help="Run directory (e.g. runs/athens_night_1). "
                         "Required for single-file mode; in sweep mode, "
                         "defaults to runs/athens_night_<N> under PROJECT_ROOT. "
                         "Resolved under PROJECT_ROOT if relative.")
    ap.add_argument("--session-id", default=None,
                    help="Expected session_id; must match metadata.session_id. "
                         "Required for single-file mode; ignored in sweep mode.")
    ap.add_argument("--project", default=None,
                    help="PROJECT_ROOT override (else AI_ASSEMBLY_PROJECT_ROOT).")
    ap.add_argument("--no-roster-check", action="store_true",
                    help="Skip the roster cross-check against sessions.json.")
    ap.add_argument("--sweep", action="store_true",
                    help="Sweep mode: read sessions.json, find every vendor "
                         "session for --night, look for <session_id>.json "
                         "files in --inbox, and land each one. Misses are "
                         "reported but don't abort the sweep.")
    ap.add_argument("--night", type=int, choices=(1, 2, 3), default=None,
                    help="Athens night (1, 2, 3). Required with --sweep.")
    ap.add_argument("--inbox", type=Path, default=None,
                    help="Vendor inbox dir (sweep mode). Defaults to "
                         "<PROJECT_ROOT>/vendor_inbox/.")
    args = ap.parse_args(argv)

    project_root = resolve_project_root(args.project)

    if args.sweep:
        if args.night is None:
            ap.error("--sweep requires --night")
        if args.vendor_file is not None or args.session_id is not None:
            ap.error("--sweep is mutually exclusive with positional vendor_file "
                     "and --session-id (sweep discovers files via convention)")
        inbox_dir = args.inbox if args.inbox else (project_root / "vendor_inbox")
        if args.run_dir is not None:
            run_dir = args.run_dir if args.run_dir.is_absolute() else (project_root / args.run_dir)
        else:
            run_dir = None  # sweep() picks the convention path
        summary = sweep(
            project_root=project_root,
            night=args.night,
            inbox_dir=inbox_dir,
            run_dir=run_dir,
        )
        # Human-readable report.
        print(f"sweep night={summary['night']} inbox={summary['inbox_dir']}")
        print(f"  expected: {summary['expected_count']} vendor session(s)")
        print(f"  landed:   {len(summary['landed'])} "
              f"({summary['warnings_total']} warning(s) total)")
        for item in summary["landed"]:
            warn_note = f", {item['n_warnings']} warning(s)" if item["n_warnings"] else ""
            print(f"    OK {item['session_id']} ({item['n_turns']} turns{warn_note})")
        if summary["missing"]:
            print(f"  missing:  {len(summary['missing'])} "
                  f"(no <session_id>.json in inbox)")
            for sid in summary["missing"]:
                print(f"    -- {sid}")
        if summary["errors"]:
            print(f"  errors:   {len(summary['errors'])}")
            for e in summary["errors"]:
                print(f"    !! {e['session_id']}: {e['error']}")
        # Exit code: non-zero only if any session in the sweep had an
        # error. Missing files are normal (vendor hasn't sent yet) — they
        # don't fail the sweep.
        return 2 if summary["errors"] else 0

    # Single-file mode
    if args.vendor_file is None or args.session_id is None or args.run_dir is None:
        ap.error("single-file mode requires vendor_file (positional), "
                 "--session-id, and --run-dir. For batch mode, use --sweep --night N.")

    run_dir = args.run_dir if args.run_dir.is_absolute() else (project_root / args.run_dir)

    if not args.vendor_file.exists():
        print(f"vendor file not found: {args.vendor_file}", file=sys.stderr)
        return 2

    sessions_json_roster = (
        None if args.no_roster_check
        else _load_sessions_json_roster(project_root, args.session_id)
    )

    result = land(
        vendor_file=args.vendor_file,
        run_dir=run_dir,
        session_id=args.session_id,
        sessions_json_roster=sessions_json_roster,
    )

    if result["state"] == "error":
        print(f"FAIL: {result['error']}", file=sys.stderr)
        print(f"see {result['session_dir'] / 'vendor.error'}", file=sys.stderr)
        return 2

    print(f"OK: {result['session_dir'] / 'session_package.json'}")
    print(f"    {result['n_turns']} turns, {len(result['warnings'])} warning(s)")
    if result["warnings"]:
        print(f"    see {result['session_dir'] / 'vendor.warnings'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
