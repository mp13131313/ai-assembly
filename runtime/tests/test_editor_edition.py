"""C46: editor `--single-dossier` must not clobber the night's dossier index.

Background (`_workspace/planning/runtime/OPEN_ITEMS.md` C46):
`editor_flow.py --single-dossier theme_X` regenerates one dossier, but
Stage 3 (`finalize_edition` / `build_night_index`) used to rewrite
`published_artifacts/dossiers/night_<N>/_index.json` from only the
dossier(s) processed in THAT run, dropping every other dossier from the
index. Same bug class as C50 (`voice/publish.py::_rebuild_index_from_disk`).

Fix: the per-night index's dossier list is now rebuilt from every
`dossier_<NNN>.json` actually on disk for that night
(`_rebuild_dossiers_from_disk`), not from the in-memory
`dossiers_by_theme` this call happened to (re)generate. The edition-lead
pick was already immune to the bug — it sources from the full-night
`routing["themes_to_dossiers"]` + `_load_theme_flags(run_dir)`, neither
of which is filtered by `--single-dossier` — these tests lock that in
too.

No real Anthropic calls — pure file-shape transforms over seeded
run_dir / project_root pairs.
"""
from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

_RUNTIME = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_RUNTIME))

from flows.shared.io import write_json_atomic  # noqa: E402
from flows.editor.edition import (  # noqa: E402
    _rebuild_dossiers_from_disk,
    finalize_edition,
)


# --- Fixture builders ------------------------------------------------------


def _dossier(theme_id: str, dossier_no: int, kicker: str = "K") -> dict:
    return {
        "schema_version": "2.0",
        "kicker": kicker,
        "headline": f"Headline {dossier_no}",
        "subline": "",
        "body_paragraphs": ["p1"],
        "headnotes": [],
        "metadata": {
            "theme_id": theme_id,
            "theme_display_title": f"Theme {dossier_no}",
            "night": 1,
        },
    }


def _write_published_dossier(
    project_root: Path, night: int, dossier_no: int, dossier: dict
) -> Path:
    p = (
        project_root / "published_artifacts" / "dossiers"
        / f"night_{night}" / f"dossier_{dossier_no:03d}.json"
    )
    write_json_atomic(p, dossier)
    return p


def _routing(themes_to_dossiers: list[dict], voices_routing: list[dict]) -> dict:
    return {
        "schema_version": "1.0",
        "night": 1,
        "themes_to_dossiers": themes_to_dossiers,
        "voices_routing": voices_routing,
        "refusals": [],
    }


# --- _rebuild_dossiers_from_disk -------------------------------------------


class TestRebuildDossiersFromDisk:
    def test_returns_empty_when_dir_missing(self, tmp_path):
        assert _rebuild_dossiers_from_disk(tmp_path, night=1) == []

    def test_reads_every_dossier_file_and_injects_dossier_no(self, tmp_path):
        _write_published_dossier(tmp_path, 1, 1, _dossier("theme_001", 1))
        _write_published_dossier(tmp_path, 1, 2, _dossier("theme_002", 2))
        out = _rebuild_dossiers_from_disk(tmp_path, night=1)
        assert {d["dossier_no"] for d in out} == {1, 2}
        by_no = {d["dossier_no"]: d for d in out}
        assert by_no[1]["metadata"]["theme_id"] == "theme_001"
        assert by_no[2]["metadata"]["theme_id"] == "theme_002"

    def test_skips_unparseable_file(self, tmp_path):
        night_dir = tmp_path / "published_artifacts" / "dossiers" / "night_1"
        night_dir.mkdir(parents=True)
        (night_dir / "dossier_001.json").write_text("{not json")
        _write_published_dossier(tmp_path, 1, 2, _dossier("theme_002", 2))
        out = _rebuild_dossiers_from_disk(tmp_path, night=1)
        assert [d["dossier_no"] for d in out] == [2]

    def test_ignores_index_json(self, tmp_path):
        _write_published_dossier(tmp_path, 1, 1, _dossier("theme_001", 1))
        idx_path = (
            tmp_path / "published_artifacts" / "dossiers" / "night_1" / "_index.json"
        )
        write_json_atomic(idx_path, {"night": 1})
        out = _rebuild_dossiers_from_disk(tmp_path, night=1)
        assert len(out) == 1


# --- finalize_edition: the C46 scenario ------------------------------------


class TestSingleDossierRerunPreservesIndex:
    """Full run (2 dossiers) then a `--single-dossier` rerun of just one
    theme must leave BOTH dossiers indexed, with the lead re-computed
    across the full night — not just the reprocessed dossier."""

    THEMES_TO_DOSSIERS = [
        {"theme_id": "theme_001", "dossier_no": 1, "theme_title": "T1", "n_engaged_voices": 5},
        {"theme_id": "theme_002", "dossier_no": 2, "theme_title": "T2", "n_engaged_voices": 1},
    ]
    VOICES_ROUTING = [
        {"voice_slug": "plato", "voice_name": "Voice of Plato",
         "primary_theme": "theme_001", "primary_dossier": 1},
        {"voice_slug": "cleopatra", "voice_name": "Voice of Cleopatra",
         "primary_theme": "theme_002", "primary_dossier": 2},
    ]

    def _routing(self) -> dict:
        return _routing(self.THEMES_TO_DOSSIERS, self.VOICES_ROUTING)

    def test_full_run_then_single_dossier_rerun_keeps_both_indexed(self, tmp_path):
        run_dir = tmp_path / "athens_night_1"
        project_root = tmp_path / "project"
        routing = self._routing()

        # --- "Full run": both dossiers generated + written to disk (as
        # editor_flow.py's write_dossier() does in Stage 2), then Stage 3
        # runs once with both in dossiers_by_theme.
        d1 = _dossier("theme_001", 1)
        d2 = _dossier("theme_002", 2)
        _write_published_dossier(project_root, 1, 1, d1)
        _write_published_dossier(project_root, 1, 2, d2)
        audit_full = finalize_edition(
            run_dir=run_dir, project_root=project_root, night=1,
            routing=routing,
            dossiers_by_theme={"theme_001": d1, "theme_002": d2},
        )
        # theme_001 has 5 engaged voices vs theme_002's 1 -> theme_001 leads.
        assert audit_full["lead_dossier_no"] == 1

        idx_path = (
            project_root / "published_artifacts" / "dossiers" / "night_1" / "_index.json"
        )
        idx_full = json.loads(idx_path.read_text())
        assert idx_full["dossier_count"] == 2
        assert {d["dossier_no"] for d in idx_full["dossiers"]} == {1, 2}
        assert idx_full["edition_lead"]["lead_dossier_no"] == 1

        # --- "--single-dossier theme_002" rerun: only theme_002's dossier
        # is regenerated + rewritten to disk (write_dossier already ran by
        # the time Stage 3 fires, matching editor_flow.py's ordering);
        # dossier_001 is untouched on disk from the full run above.
        d2_v2 = _dossier("theme_002", 2, kicker="REGENERATED")
        _write_published_dossier(project_root, 1, 2, d2_v2)
        audit_rerun = finalize_edition(
            run_dir=run_dir, project_root=project_root, night=1,
            routing=routing,
            dossiers_by_theme={"theme_002": d2_v2},
        )
        # Lead is unchanged — still computed off the FULL routing manifest,
        # not just the reprocessed dossier.
        assert audit_rerun["lead_dossier_no"] == 1

        idx_rerun = json.loads(idx_path.read_text())
        # C46: dossier_001 must still be indexed even though this call
        # only reprocessed dossier_002.
        assert idx_rerun["dossier_count"] == 2
        assert {d["dossier_no"] for d in idx_rerun["dossiers"]} == {1, 2}
        assert idx_rerun["edition_lead"]["lead_dossier_no"] == 1
        by_no = {d["dossier_no"]: d for d in idx_rerun["dossiers"]}
        assert by_no[2]["kicker"] == "REGENERATED"
        assert by_no[1]["kicker"] == "K"  # untouched from the full run

    def test_lead_pick_recoverable_even_when_leading_dossier_not_reprocessed(self, tmp_path):
        """The dossier that WINS the lead-pick doesn't have to be the one
        this call reprocessed — proves the lead-pick isn't sourced from
        `dossiers_by_theme` (the in-memory reprocessed subset)."""
        run_dir = tmp_path / "athens_night_1"
        project_root = tmp_path / "project"
        routing = self._routing()

        d1 = _dossier("theme_001", 1)  # 5 engaged voices — the eventual lead
        d2 = _dossier("theme_002", 2)  # 1 engaged voice
        _write_published_dossier(project_root, 1, 1, d1)
        _write_published_dossier(project_root, 1, 2, d2)

        # Single-dossier rerun of theme_002 ONLY — dossiers_by_theme never
        # sees theme_001 at all in this call.
        audit = finalize_edition(
            run_dir=run_dir, project_root=project_root, night=1,
            routing=routing,
            dossiers_by_theme={"theme_002": d2},
        )
        assert audit["lead_dossier_no"] == 1
        assert audit["scoring_audit"]["audit"][0]["theme_id"] == "theme_001"

    def test_missing_dossier_on_disk_warns_and_is_absent_from_index(self, tmp_path, caplog):
        """Defensive path: if `dossiers_by_theme` claims a theme was
        processed but its file never landed on disk (write_dossier
        failing silently, or a caller misuse), finalize_edition warns
        instead of silently indexing a phantom entry."""
        run_dir = tmp_path / "athens_night_1"
        project_root = tmp_path / "project"
        routing = self._routing()

        d1 = _dossier("theme_001", 1)
        _write_published_dossier(project_root, 1, 1, d1)
        # theme_002's dossier is NOT written to disk, unlike the normal
        # editor_flow.py ordering (write_dossier always runs first).

        with caplog.at_level(logging.WARNING, logger="editor_edition"):
            audit = finalize_edition(
                run_dir=run_dir, project_root=project_root, night=1,
                routing=routing,
                dossiers_by_theme={
                    "theme_001": d1,
                    "theme_002": {"metadata": {"theme_id": "theme_002"}},
                },
            )

        assert any("theme_002" in rec.message for rec in caplog.records)
        idx_path = (
            project_root / "published_artifacts" / "dossiers" / "night_1" / "_index.json"
        )
        idx = json.loads(idx_path.read_text())
        assert idx["dossier_count"] == 1
        assert idx["dossiers"][0]["dossier_no"] == 1
        # Lead-pick is unaffected by the missing file — still scored off
        # routing, not off what actually landed on disk.
        assert audit["lead_dossier_no"] == 1
