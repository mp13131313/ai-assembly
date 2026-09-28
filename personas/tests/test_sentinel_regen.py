"""sentinel_regen.py — the Stage 4 quality gate (voices OPEN_ITEMS §37 A5).

Every subprocess is mocked: nothing here re-runs the pipeline or calls a model.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts import sentinel_regen as sr  # noqa: E402


def _project(root: Path, slugs: list[str], git: bool = False) -> Path:
    root.mkdir(parents=True)
    (root / "conference_facts.json").write_text("{}")
    (root / "audience_profile.json").write_text("{}")
    for s in slugs:
        (root / "voices" / s / "04_generation").mkdir(parents=True)
        (root / "voices" / s / "00_intake").mkdir(parents=True)
    if git:
        (root / ".git").mkdir()
    return root


def test_sandbox_copies_project_json_and_named_voices_only(tmp_path):
    src = _project(tmp_path / "prod", ["plato", "cleopatra", "octopus"])
    dst = tmp_path / "sandbox"

    sr.make_sandbox(src, dst, ["plato", "octopus"])

    assert sorted(p.name for p in dst.glob("*.json")) == ["audience_profile.json", "conference_facts.json"]
    assert sorted(p.name for p in (dst / "voices").iterdir()) == ["octopus", "plato"]


def test_sandbox_refuses_non_empty_target_and_target_inside_source(tmp_path):
    src = _project(tmp_path / "prod", ["plato"])
    busy = tmp_path / "busy"
    busy.mkdir()
    (busy / "x").write_text("x")
    with pytest.raises(SystemExit, match="not empty"):
        sr.make_sandbox(src, busy, ["plato"])
    with pytest.raises(SystemExit, match="inside the source"):
        sr.make_sandbox(src, src / "sandbox", ["plato"])
    with pytest.raises(SystemExit, match="No voices"):
        sr.make_sandbox(src, tmp_path / "new", ["ghost"])


def test_regen_refuses_a_git_project_before_running_anything(tmp_path, monkeypatch):
    prod = _project(tmp_path / "athens", ["plato"], git=True)
    calls = []
    monkeypatch.setattr(sr.subprocess, "run", lambda *a, **k: calls.append(a))

    with pytest.raises(SystemExit, match="own git repository"):
        sr.main(["regen", "--pass", "4a", "--project", str(prod),
                 "--baseline-project", str(prod), "--voices", "plato"])
    assert calls == []


def test_regen_runs_in_sandbox_and_diffs_against_baseline_project(tmp_path, monkeypatch, capsys):
    from flows.shared import paths as _paths

    prod = _project(tmp_path / "athens", ["plato"], git=True)
    sandbox = tmp_path / "sandbox"
    sr.make_sandbox(prod, sandbox, ["plato"])
    regen_file = _paths.pass_4a("plato", sandbox.resolve())
    base_file = _paths.pass_4a("plato", prod.resolve())
    base_file.parent.mkdir(parents=True, exist_ok=True)
    base_file.write_text(json.dumps({"fields": {"register_and_tone": "old", "moves": "same"}}))

    cmds = []

    def fake_run(cmd, check):
        cmds.append(cmd)
        if "run_persona_pipeline.py" in cmd[1]:  # the "pipeline" writes the regenerated pass
            regen_file.parent.mkdir(parents=True, exist_ok=True)
            regen_file.write_text(json.dumps({"fields": {"register_and_tone": "new", "moves": "same"}}))

    monkeypatch.setattr(sr.subprocess, "run", fake_run)

    rc = sr.main(["regen", "--pass", "4a", "--project", str(sandbox),
                  "--baseline-project", str(prod), "--voices", "plato"])

    assert rc == 0
    assert cmds[0][-4:] == ["--project", str(sandbox.resolve()), "--pass", "4a"]  # invalidate
    assert cmds[1][2:] == ["plato", "--project", str(sandbox.resolve())]          # pipeline, by slug
    out = capsys.readouterr().out
    assert "fields_changed: ['register_and_tone']" in out


def test_baseline_snapshot_prefers_per_voice_then_flat(tmp_path):
    regen = tmp_path / "sb" / "voices" / "plato" / "04_generation" / "p.json"
    snap = tmp_path / "snap"
    (snap / "plato").mkdir(parents=True)
    assert sr.resolve_baseline(regen, tmp_path / "sb", "plato", None, snap) == snap / "plato" / "p.json"
    (snap / "p.json").write_text("{}")
    assert sr.resolve_baseline(regen, tmp_path / "sb", "plato", None, snap) == snap / "p.json"
    (snap / "plato" / "p.json").write_text("{}")
    assert sr.resolve_baseline(regen, tmp_path / "sb", "plato", None, snap) == snap / "plato" / "p.json"


def test_regen_requires_a_known_pass_and_exactly_one_baseline(tmp_path):
    with pytest.raises(SystemExit):
        sr.build_parser().parse_args(["regen", "--pass", "9", "--project", "x", "--baseline-project", "y"])
    with pytest.raises(SystemExit):
        sr.build_parser().parse_args(["regen", "--pass", "4a", "--project", "x"])
