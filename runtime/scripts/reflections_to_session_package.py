#!/usr/bin/env python3
"""Reflection import → session_package.json preprocessor.

Per AI Assembly Reflection Import Format spec (operator-authored, 2026-05-07):

    {
      "source": "vendor_name_v1",
      "session_id": "session_017",
      "collected_at": "2026-05-08T18:42:00+03:00",
      "reflections": [{participant_id, duration_seconds, text, language?}, ...]
    }

→ session_package.json shape vendor_intake.py expects:

    {
      "metadata": {session_id, ...session_metadata_we_hold},
      "transcript": {
        "turns": [{speaker, role, confidence, text}, ...],
        "speakers_present": [...]
      }
    }

Mapping per spec:
- Each reflections[i] → one turn
- speaker = "Participant {i+1}" (1-indexed, array order preserved)
- role = "audience"
- confidence = "high"
- text = reflections[i].text (no re-cleaning)
- Original participant_id + duration_seconds preserved as turn metadata
  (non-required fields; vendor_intake doesn't reject extra fields).

Session-side metadata merge: looks up session_id in
PROJECT_ROOT/reference/sessions.json. If found, copies title, day, etc.
into metadata. If not found (e.g. demo / test sessions), uses placeholder
metadata derived from the reflection JSON itself (session_id from
payload, no title) — vendor_intake will accept this since only
metadata.session_id is hard-required.

Output location:
- If --out PATH given: write there.
- Else: write next to the input file as <input_stem>.session_package.json

Usage:
    python -m flows.scripts.reflections_to_session_package \\
        /path/to/{session_id}.reflections.json \\
        [--out /path/to/output.json]

Or via direct script:
    runtime/scripts/reflections_to_session_package.py <input> [--out <output>]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any


def _load_session_metadata(project_root: Path | None, session_id: str) -> dict[str, Any]:
    """Look up session in PROJECT_ROOT/reference/sessions.json. Returns
    metadata dict suitable for session_package.metadata, or a minimal
    placeholder if not found / no project_root."""
    base: dict[str, Any] = {"session_id": session_id}
    if project_root is None:
        return base
    sessions_path = project_root / "reference" / "sessions.json"
    if not sessions_path.exists():
        return base
    try:
        sessions = json.loads(sessions_path.read_text(encoding="utf-8")).get("sessions", [])
    except (OSError, json.JSONDecodeError):
        return base
    sess = next((s for s in sessions if s.get("session_id") == session_id), None)
    if sess is None:
        return base
    # Copy metadata fields we hold session-side; vendor sees none of this
    # in their format — we merge it in here.
    base.update({
        k: sess[k] for k in (
            "title", "day", "track_or_program", "venue",
            "start_time", "end_time", "audio_source",
            "ai_assembly", "panelists", "moderator", "host",
            "roster", "expected_participant_count",
        ) if k in sess
    })
    return base


def reflections_to_session_package(
    reflection_payload: dict[str, Any],
    *,
    project_root: Path | None = None,
) -> dict[str, Any]:
    """Convert a vendor reflection JSON payload to a session_package shape.

    Validates the spec contract on the reflection side:
    - top-level session_id, collected_at, reflections required
    - reflections non-empty list
    - each reflections[i] has participant_id + duration_seconds + text

    Raises ValueError on contract violations.
    """
    if not isinstance(reflection_payload, dict):
        raise ValueError("reflection payload is not a JSON object")

    session_id = reflection_payload.get("session_id")
    if not session_id or not isinstance(session_id, str):
        raise ValueError("missing or non-string session_id")

    reflections = reflection_payload.get("reflections")
    if not isinstance(reflections, list) or len(reflections) == 0:
        raise ValueError("reflections is missing, empty, or not a list")

    turns = []
    for i, r in enumerate(reflections):
        if not isinstance(r, dict):
            raise ValueError(f"reflections[{i}] is not a dict")
        for required in ("participant_id", "duration_seconds", "text"):
            if r.get(required) is None or (
                isinstance(r.get(required), str) and not r.get(required).strip()
            ):
                raise ValueError(f"reflections[{i}] missing required field {required!r}")

        speaker_label = f"Participant {i + 1}"
        turn: dict[str, Any] = {
            "speaker": speaker_label,
            "role": "audience",
            "confidence": "high",
            "text": r["text"].strip(),
        }
        # Preserve vendor-side metadata as non-required turn fields.
        # vendor_intake.py's validator allows extra fields per turn.
        if "language" in r and r["language"]:
            turn["language"] = r["language"]
        # The participant_id + duration_seconds are diagnostic only per spec.
        turn["_vendor_participant_id"] = r["participant_id"]
        turn["_vendor_duration_seconds"] = r["duration_seconds"]
        turns.append(turn)

    metadata = _load_session_metadata(project_root, session_id)
    # Tag the import provenance so we know where this came from at audit time.
    metadata["_reflection_source"] = reflection_payload.get("source", "unknown")
    metadata["_collected_at"] = reflection_payload.get("collected_at", "")

    speakers_present = sorted({t["speaker"] for t in turns})
    return {
        "metadata": metadata,
        "transcript": {
            "turns": turns,
            "speakers_present": speakers_present,
        },
        "review_queue": [],  # vendor_intake injects empty stub if missing; pre-fill
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("input", help="Path to vendor reflection JSON")
    ap.add_argument("--out", help="Output path for session_package.json")
    ap.add_argument("--project-root", help="PROJECT_ROOT for session metadata merge")
    args = ap.parse_args()

    inp = Path(args.input).resolve()
    if not inp.exists():
        print(f"ERROR: {inp} not found", file=sys.stderr)
        sys.exit(2)

    payload = json.loads(inp.read_text(encoding="utf-8"))

    project_root = None
    if args.project_root:
        project_root = Path(args.project_root).resolve()
    elif os.environ.get("AI_ASSEMBLY_PROJECT_ROOT"):
        project_root = Path(os.environ["AI_ASSEMBLY_PROJECT_ROOT"]).resolve()

    pkg = reflections_to_session_package(payload, project_root=project_root)

    if args.out:
        out = Path(args.out).resolve()
    else:
        # Default: sibling of input with .session_package.json extension
        out = inp.with_suffix(".session_package.json")

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(pkg, indent=2, ensure_ascii=False), encoding="utf-8")

    n_turns = len(pkg["transcript"]["turns"])
    n_speakers = len(pkg["transcript"]["speakers_present"])
    has_meta = bool({k for k in pkg["metadata"] if not k.startswith("_") and k != "session_id"})
    print(f"WROTE: {out}")
    print(f"  session_id:        {pkg['metadata']['session_id']}")
    print(f"  turns:             {n_turns}")
    print(f"  speakers_present:  {n_speakers}")
    print(f"  metadata merged:   {'yes' if has_meta else 'no (session not in sessions.json)'}")


if __name__ == "__main__":
    main()
