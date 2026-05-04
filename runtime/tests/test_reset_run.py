"""Reset script — `--from-stage X` deletes the right per-stage subtrees +
per-night published paths. Idempotent; respects --include-transcription.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_RUNTIME = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_RUNTIME))
_SCRIPTS = _RUNTIME / "scripts"
sys.path.insert(0, str(_SCRIPTS))

from reset_run import (  # noqa: E402
    _STAGE_ORDER,
    _stages_from,
    collect_paths_to_delete,
)


def _seed_run_dir(tmp_path: Path) -> tuple[Path, Path]:
    project_root = tmp_path / "project"
    run_dir = project_root / "runs" / "athens_night_1"
    # Per-stage run_dir subtrees
    for sub in (
        "01_transcription/sess_a",
        "02_researcher",
        "03_provocateur",
        "04_voice",
        "05_editor",
    ):
        d = run_dir / sub
        d.mkdir(parents=True)
        (d / "marker.txt").write_text("x")
    # Per-night published paths
    pub = project_root / "published_artifacts"
    for sub in (
        "themes/night_1",
        "nights/night_1",
        "dossiers/night_1",
        "extractions",
        "voices",
        "traces",
    ):
        d = pub / sub
        d.mkdir(parents=True)
        (d / "marker.txt").write_text("x")
    (pub / "traces" / "lineage_graph_night_1.json").write_text("{}")
    (pub / "traces" / "publish_manifest_night_1.json").write_text("{}")
    (pub / "dossiers" / "_index.json").write_text("{}")
    return run_dir, project_root


# --- Stage walking ----------------------------------------------------

class TestStagesFrom:
    def test_provocateur_includes_downstream(self):
        out = _stages_from("provocateur")
        assert out == ["provocateur", "voice", "editor", "publish"]

    def test_publish_alone(self):
        assert _stages_from("publish") == ["publish"]

    def test_editor_includes_publish(self):
        assert _stages_from("editor") == ["editor", "publish"]

    def test_unknown_raises(self):
        with pytest.raises(ValueError):
            _stages_from("nonexistent")


# --- Per-stage path collection ----------------------------------------

class TestCollectPathsToDelete:
    def test_provocateur_collects_pro_voice_editor_publish(self, tmp_path):
        run_dir, project_root = _seed_run_dir(tmp_path)
        paths = collect_paths_to_delete(run_dir, project_root, "provocateur")
        names = {str(p.relative_to(project_root)) for p in paths}
        assert "runs/athens_night_1/03_provocateur" in names
        assert "runs/athens_night_1/04_voice" in names
        assert "runs/athens_night_1/05_editor" in names
        # Publish surfaces
        assert "published_artifacts/nights/night_1" in names
        assert "published_artifacts/dossiers/night_1" in names
        # Transcription + researcher untouched
        assert "runs/athens_night_1/01_transcription" not in names
        assert "runs/athens_night_1/02_researcher" not in names
        assert "published_artifacts/themes/night_1" not in names

    def test_editor_collects_only_editor_and_publish(self, tmp_path):
        run_dir, project_root = _seed_run_dir(tmp_path)
        paths = collect_paths_to_delete(run_dir, project_root, "editor")
        names = {str(p.relative_to(project_root)) for p in paths}
        assert "runs/athens_night_1/05_editor" in names
        assert "published_artifacts/dossiers/night_1" in names
        # Voice untouched
        assert "runs/athens_night_1/04_voice" not in names
        assert "published_artifacts/nights/night_1" not in names

    def test_publish_only(self, tmp_path):
        run_dir, project_root = _seed_run_dir(tmp_path)
        paths = collect_paths_to_delete(run_dir, project_root, "publish")
        names = {str(p.relative_to(project_root)) for p in paths}
        # publish-stage owned: extractions, voices, lineage graph file,
        # cross-night dossier index
        assert "published_artifacts/extractions" in names
        assert "published_artifacts/voices" in names
        assert "published_artifacts/traces/lineage_graph_night_1.json" in names
        assert "published_artifacts/dossiers/_index.json" in names
        # Editor untouched
        assert "runs/athens_night_1/05_editor" not in names

    def test_transcription_excluded_by_default(self, tmp_path):
        run_dir, project_root = _seed_run_dir(tmp_path)
        paths = collect_paths_to_delete(run_dir, project_root, "transcription")
        names = {str(p.relative_to(project_root)) for p in paths}
        assert "runs/athens_night_1/01_transcription" not in names
        # but downstream stages still get cleared
        assert "runs/athens_night_1/02_researcher" in names
        assert "runs/athens_night_1/03_provocateur" in names

    def test_transcription_included_when_flag_set(self, tmp_path):
        run_dir, project_root = _seed_run_dir(tmp_path)
        paths = collect_paths_to_delete(
            run_dir, project_root, "transcription",
            include_transcription=True,
        )
        names = {str(p.relative_to(project_root)) for p in paths}
        assert "runs/athens_night_1/01_transcription" in names

    def test_idempotent_after_partial_state(self, tmp_path):
        # Pre-delete editor; verify reset --from-stage editor still
        # collects the publish-stage paths but skips the missing editor dir.
        run_dir, project_root = _seed_run_dir(tmp_path)
        import shutil
        shutil.rmtree(run_dir / "05_editor")
        paths = collect_paths_to_delete(run_dir, project_root, "editor")
        names = {str(p.relative_to(project_root)) for p in paths}
        assert "runs/athens_night_1/05_editor" not in names  # already gone
        assert "published_artifacts/dossiers/night_1" in names  # still there

    def test_run_dir_without_night_number_skips_per_night_paths(self, tmp_path):
        # run_dir folder doesn't match athens_night_<N> → skip per-night
        # published paths but still hit run_dir subtrees.
        project_root = tmp_path / "project"
        run_dir = project_root / "runs" / "ad_hoc_run"
        for sub in ("03_provocateur", "04_voice"):
            (run_dir / sub).mkdir(parents=True)
        paths = collect_paths_to_delete(run_dir, project_root, "provocateur")
        names = {str(p.relative_to(project_root)) for p in paths}
        assert "runs/ad_hoc_run/03_provocateur" in names
        assert "runs/ad_hoc_run/04_voice" in names
        # No per-night published paths since the night number didn't parse
        assert not any("/night_" in n for n in names)


# --- Stage order constant ---------------------------------------------

class TestStageOrder:
    def test_canonical_order(self):
        assert _STAGE_ORDER == (
            "transcription", "researcher", "provocateur",
            "voice", "editor", "publish",
        )
