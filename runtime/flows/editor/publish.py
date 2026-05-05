"""Editor Pipeline — write/mirror dossier outputs.

Per spec v2 §"Outputs":

  Per-night under <run_dir>/05_editor/:
    theme_routing.json                   (Stage 1; written by routing.py)
    dossiers/dossier_<NNN>.json          (Stage 2 outputs)
    manifest.json                        (run metadata)

  Per-dossier published copy at <PROJECT_ROOT>/published_artifacts/dossiers/night_<N>/:
    dossier_<NNN>.json                   (canonical microsite + cross-night reference)

Both copies are byte-identical at production time. The run_dir copy lives
with the night's other run artifacts; the published copy is the canonical
reference for downstream consumers (microsite + cross-night Editor reads
on Night 2/3).
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from flows.shared.io import write_json_atomic  # noqa: E402


def _dossier_filename(dossier_no: int) -> str:
    return f"dossier_{dossier_no:03d}.json"


def write_dossier(
    dossier: dict[str, Any],
    *,
    run_dir: Path,
    project_root: Path,
    night: int,
    dossier_no: int,
) -> tuple[Path, Path]:
    """Write the dossier to BOTH the run_dir copy and the published copy.

    Returns (run_dir_path, published_path) for the caller's manifest.
    """
    filename = _dossier_filename(dossier_no)

    run_dir_path = run_dir / "05_editor" / "dossiers" / filename
    published_path = (
        project_root / "published_artifacts" / "dossiers"
        / f"night_{night}" / filename
    )

    write_json_atomic(run_dir_path, dossier)
    write_json_atomic(published_path, dossier)
    return run_dir_path, published_path


def load_prior_editions(
    project_root: Path,
    night: int,
) -> list[dict[str, Any]]:
    """Read prior nights' published dossiers, trim to just the articles
    per spec v2 Q2 (kicker + headline + body_paragraphs only).

    Returns a list of {night, dossiers: [{kicker, headline,
    body_paragraphs}]} entries — one per prior night, in chronological order.

    Empty list on Night 1 (no prior nights).
    """
    if night <= 1:
        return []

    import json
    out: list[dict[str, Any]] = []
    for prior_night in range(1, night):
        prior_dir = project_root / "published_artifacts" / "dossiers" / f"night_{prior_night}"
        if not prior_dir.exists():
            continue
        dossiers_trimmed = []
        for path in sorted(prior_dir.glob("dossier_*.json")):
            try:
                with path.open(encoding="utf-8") as f:
                    full = json.load(f)
            except (OSError, json.JSONDecodeError):
                continue
            dossiers_trimmed.append({
                "kicker":          full.get("kicker", ""),
                "headline":        full.get("headline", ""),
                "body_paragraphs": full.get("body_paragraphs", []),
            })
        if dossiers_trimmed:
            out.append({
                "night":    prior_night,
                "dossiers": dossiers_trimmed,
            })
    return out
