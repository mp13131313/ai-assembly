"""End-to-end tests for the overnight orchestrator's trigger logic.

Each test builds a synthetic PROJECT_ROOT + run_dir filesystem state, calls
poll_once, and asserts the returned state. fire_stage is monkeypatched to
write the next stage's sentinel without actually invoking subprocesses, so
the test is fast (~1s for the suite) and burns no API credits.

Together these tests exercise every branch in poll_once + every CLI shape
the orchestrator hands to downstream flows.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_RUNTIME_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_RUNTIME_ROOT / "scripts"))

import overnight_orchestrator as orch  # noqa: E402


# --- Fixtures ---------------------------------------------------------------


@pytest.fixture
def project_root(tmp_path: Path) -> Path:
    """Minimal PROJECT_ROOT with sessions.json (2 sessions Night 1, 1 Night 2)."""
    sessions = {
        "sessions": [
            {"session_id": "s1", "day": "Day One", "ai_assembly": True},
            {"session_id": "s2", "day": "Day One", "ai_assembly": True},
            {"session_id": "s3", "day": "Day Two", "ai_assembly": True},
            {"session_id": "skipped", "day": "Day One", "ai_assembly": False},
        ]
    }
    ref = tmp_path / "reference"
    ref.mkdir()
    (ref / "sessions.json").write_text(json.dumps(sessions))
    (tmp_path / "runs").mkdir()
    return tmp_path


def _set_state(run_dir: Path, session_id: str, state: str) -> None:
    d = run_dir / "01_transcription" / session_id
    d.mkdir(parents=True, exist_ok=True)
    (d / "status.json").write_text(json.dumps({"state": state}))


def _make_sentinel(run_dir: Path, subdir: str, fname: str) -> None:
    p = run_dir / subdir / fname
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("{}")


class _StubFire(list):
    """List of captured invocations with a `side_effects` dict attached.

    Tests can pre-register per-stage sentinel side-effects via
    `stub_fire.side_effects[stage_name] = callable` to simulate a stage
    that completes and writes its output file.
    """

    def __init__(self):
        super().__init__()
        self.side_effects: dict[str, callable] = {}


@pytest.fixture
def stub_fire(monkeypatch):
    """Monkeypatch fire_stage to capture invocations and run side-effects."""
    captured = _StubFire()

    def fake_fire(cmd, name, log_dir):
        captured.append({"name": name, "cmd": list(cmd)})
        if name in captured.side_effects:
            captured.side_effects[name]()
        return (True, log_dir / f"{name}.log")

    monkeypatch.setattr(orch, "fire_stage", fake_fire)
    return captured


# --- Tests: per-trigger state classification --------------------------------


class TestSessionScoping:
    """sessions_for_tonight filters correctly."""

    def test_night_1_picks_day_one_only(self, project_root):
        ids = orch.sessions_for_tonight(project_root, 1)
        assert ids == ["s1", "s2"]  # `skipped` excluded by ai_assembly=false

    def test_night_2_picks_day_two(self, project_root):
        ids = orch.sessions_for_tonight(project_root, 2)
        assert ids == ["s3"]

    def test_night_3_empty_when_no_day_three_sessions(self, project_root):
        ids = orch.sessions_for_tonight(project_root, 3)
        assert ids == []


class TestTranscriptionState:
    """transcription_state classifier."""

    def test_all_pending_when_run_dir_empty(self, project_root):
        run_dir = project_root / "runs" / "athens_night_1"
        run_dir.mkdir()
        ts = orch.transcription_state(run_dir, ["s1", "s2"])
        assert ts["all_done"] is False
        assert ts["any_error"] is False
        assert set(ts["pending_sessions"]) == {"s1", "s2"}

    def test_partial_done(self, project_root):
        run_dir = project_root / "runs" / "athens_night_1"
        run_dir.mkdir()
        _set_state(run_dir, "s1", "done")
        _set_state(run_dir, "s2", "transcribing")
        ts = orch.transcription_state(run_dir, ["s1", "s2"])
        assert ts["done_count"] == 1
        assert ts["all_done"] is False
        assert ts["pending_sessions"] == ["s2"]

    def test_error_flagged(self, project_root):
        run_dir = project_root / "runs" / "athens_night_1"
        run_dir.mkdir()
        _set_state(run_dir, "s1", "done")
        _set_state(run_dir, "s2", "error")
        ts = orch.transcription_state(run_dir, ["s1", "s2"])
        assert ts["any_error"] is True
        assert ts["error_sessions"] == ["s2"]

    def test_corrupted_status_json_counts_as_pending(self, project_root):
        run_dir = project_root / "runs" / "athens_night_1"
        d = run_dir / "01_transcription" / "s1"
        d.mkdir(parents=True)
        (d / "status.json").write_text("not valid json")
        ts = orch.transcription_state(run_dir, ["s1"])
        assert ts["pending_sessions"] == ["s1"]

    def test_all_done(self, project_root):
        run_dir = project_root / "runs" / "athens_night_1"
        run_dir.mkdir()
        _set_state(run_dir, "s1", "done")
        _set_state(run_dir, "s2", "done")
        ts = orch.transcription_state(run_dir, ["s1", "s2"])
        assert ts["all_done"] is True
        assert ts["any_error"] is False


# --- Tests: poll_once across the full chain ---------------------------------


class TestPollOnce:
    """End-to-end trigger paths through poll_once."""

    def test_run_dir_missing_returns_idle(self, project_root):
        status = orch.poll_once(project_root, 1)
        assert status["state"] == "idle"
        assert "does not exist yet" in status["detail"]

    def test_no_transcriptions_returns_idle(self, project_root):
        (project_root / "runs" / "athens_night_1").mkdir()
        status = orch.poll_once(project_root, 1)
        assert status["state"] == "idle"
        assert status["transcription"]["done_count"] == 0

    def test_partial_transcriptions_idle(self, project_root):
        run_dir = project_root / "runs" / "athens_night_1"
        run_dir.mkdir()
        _set_state(run_dir, "s1", "done")
        _set_state(run_dir, "s2", "transcribing")
        status = orch.poll_once(project_root, 1)
        assert status["state"] == "idle"
        assert status["transcription"]["done_count"] == 1

    def test_transcription_error_halts(self, project_root):
        run_dir = project_root / "runs" / "athens_night_1"
        run_dir.mkdir()
        _set_state(run_dir, "s1", "done")
        _set_state(run_dir, "s2", "error")
        status = orch.poll_once(project_root, 1)
        assert status["state"] == "failed:transcription"
        assert "s2" in status["detail"]

    def test_all_transcriptions_done_fires_researcher(self, project_root, stub_fire):
        run_dir = project_root / "runs" / "athens_night_1"
        run_dir.mkdir()
        _set_state(run_dir, "s1", "done")
        _set_state(run_dir, "s2", "done")
        status = orch.poll_once(project_root, 1)
        assert status["state"] == "fired:researcher"
        assert stub_fire[-1]["name"] == "researcher"
        # CLI shape: [python, /…/researcher_flow.py, <run_dir>]
        assert stub_fire[-1]["cmd"][1].endswith("researcher_flow.py")
        assert stub_fire[-1]["cmd"][2] == str(run_dir)

    def test_researcher_done_fires_provocateur_no_prior_for_night_1(
        self, project_root, stub_fire
    ):
        run_dir = project_root / "runs" / "athens_night_1"
        run_dir.mkdir()
        _set_state(run_dir, "s1", "done")
        _set_state(run_dir, "s2", "done")
        _make_sentinel(run_dir, "02_researcher", "grouping.json")
        status = orch.poll_once(project_root, 1)
        assert status["state"] == "fired:provocateur"
        assert "--prior-nights" not in stub_fire[-1]["cmd"]

    def test_provocateur_for_night_2_includes_prior_nights(
        self, project_root, stub_fire
    ):
        # Night 1 run_dir exists (marks prior); Night 2 ready to fire provocateur.
        (project_root / "runs" / "athens_night_1").mkdir()
        run_dir2 = project_root / "runs" / "athens_night_2"
        run_dir2.mkdir()
        _set_state(run_dir2, "s3", "done")
        _make_sentinel(run_dir2, "02_researcher", "grouping.json")
        status = orch.poll_once(project_root, 2)
        assert status["state"] == "fired:provocateur"
        cmd_str = " ".join(stub_fire[-1]["cmd"])
        assert "--prior-nights" in cmd_str
        assert "athens_night_1" in cmd_str

    def test_provocateur_done_fires_voice_with_skip_step3_only_for_night_1(
        self, project_root, stub_fire
    ):
        run_dir = project_root / "runs" / "athens_night_1"
        run_dir.mkdir()
        _set_state(run_dir, "s1", "done")
        _set_state(run_dir, "s2", "done")
        _make_sentinel(run_dir, "02_researcher", "grouping.json")
        _make_sentinel(run_dir, "03_provocateur", "manifest.json")
        status = orch.poll_once(project_root, 1)
        assert status["state"] == "fired:voice"
        cmd = stub_fire[-1]["cmd"]
        assert "--night" in cmd and "1" in cmd
        assert "--skip-step3" in cmd
        assert "--skip-validation" not in cmd  # validation ON for Night 1

    def test_voice_for_night_2_includes_skip_validation(self, project_root, stub_fire):
        run_dir2 = project_root / "runs" / "athens_night_2"
        run_dir2.mkdir()
        _set_state(run_dir2, "s3", "done")
        _make_sentinel(run_dir2, "02_researcher", "grouping.json")
        _make_sentinel(run_dir2, "03_provocateur", "manifest.json")
        status = orch.poll_once(project_root, 2)
        assert status["state"] == "fired:voice"
        cmd = stub_fire[-1]["cmd"]
        assert "--skip-validation" in cmd

    def test_voice_done_skips_editor_when_not_built(
        self, project_root, stub_fire, monkeypatch
    ):
        monkeypatch.setattr(orch, "editor_flow_exists", lambda: False)
        run_dir = project_root / "runs" / "athens_night_1"
        run_dir.mkdir()
        _set_state(run_dir, "s1", "done")
        _set_state(run_dir, "s2", "done")
        _make_sentinel(run_dir, "02_researcher", "grouping.json")
        _make_sentinel(run_dir, "03_provocateur", "manifest.json")
        _make_sentinel(run_dir, "04_voice", "manifest.json")
        status = orch.poll_once(project_root, 1)
        assert status["state"] == "fired:publish"
        assert stub_fire[-1]["cmd"][1].endswith("publish_flow.py")

    def test_voice_done_fires_editor_when_built(
        self, project_root, stub_fire, monkeypatch
    ):
        monkeypatch.setattr(orch, "editor_flow_exists", lambda: True)
        run_dir = project_root / "runs" / "athens_night_1"
        run_dir.mkdir()
        _set_state(run_dir, "s1", "done")
        _set_state(run_dir, "s2", "done")
        _make_sentinel(run_dir, "02_researcher", "grouping.json")
        _make_sentinel(run_dir, "03_provocateur", "manifest.json")
        _make_sentinel(run_dir, "04_voice", "manifest.json")
        # editor_flow.py doesn't exist in flows/ at runtime; the check is
        # monkeypatched. fire_stage is also stubbed so no real exec.
        status = orch.poll_once(project_root, 1)
        assert status["state"] == "fired:editor"

    def test_publish_done_returns_complete(self, project_root):
        run_dir = project_root / "runs" / "athens_night_1"
        run_dir.mkdir()
        _set_state(run_dir, "s1", "done")
        _set_state(run_dir, "s2", "done")
        for sub, fn in [
            ("02_researcher", "grouping.json"),
            ("03_provocateur", "manifest.json"),
            ("04_voice", "manifest.json"),
        ]:
            _make_sentinel(run_dir, sub, fn)
        publish_dir = project_root / "published_artifacts" / "nights" / "night_1"
        publish_dir.mkdir(parents=True)
        (publish_dir / "_index.json").write_text("{}")
        status = orch.poll_once(project_root, 1)
        assert status["state"] == "complete"

    def test_skip_publish_completes_after_voice_when_no_editor(
        self, project_root, monkeypatch
    ):
        monkeypatch.setattr(orch, "editor_flow_exists", lambda: False)
        run_dir = project_root / "runs" / "athens_night_1"
        run_dir.mkdir()
        _set_state(run_dir, "s1", "done")
        _set_state(run_dir, "s2", "done")
        for sub, fn in [
            ("02_researcher", "grouping.json"),
            ("03_provocateur", "manifest.json"),
            ("04_voice", "manifest.json"),
        ]:
            _make_sentinel(run_dir, sub, fn)
        # No publish sentinel; --skip-publish should still report complete.
        status = orch.poll_once(project_root, 1, skip_publish=True)
        assert status["state"] == "complete"


class TestStageProgression:
    """Run multiple poll_once calls to walk the full chain end-to-end."""

    def test_full_chain_night_1_no_editor(self, project_root, stub_fire, monkeypatch):
        monkeypatch.setattr(orch, "editor_flow_exists", lambda: False)
        run_dir = project_root / "runs" / "athens_night_1"
        run_dir.mkdir()
        _set_state(run_dir, "s1", "done")
        _set_state(run_dir, "s2", "done")

        # Each fake_fire writes the next stage's sentinel as a side effect.
        stub_fire.side_effects["researcher"] = lambda: _make_sentinel(
            run_dir, "02_researcher", "grouping.json"
        )
        stub_fire.side_effects["provocateur"] = lambda: _make_sentinel(
            run_dir, "03_provocateur", "manifest.json"
        )
        stub_fire.side_effects["voice"] = lambda: _make_sentinel(
            run_dir, "04_voice", "manifest.json"
        )

        def _publish_sentinel():
            d = project_root / "published_artifacts" / "nights" / "night_1"
            d.mkdir(parents=True, exist_ok=True)
            (d / "_index.json").write_text("{}")

        stub_fire.side_effects["publish"] = _publish_sentinel

        # Drive the chain via repeated polls.
        seen = []
        for _ in range(10):  # bounded; chain is 4 stages + complete
            status = orch.poll_once(project_root, 1)
            seen.append(status["state"])
            if status["state"] in {"complete"} or status["state"].startswith("failed:"):
                break

        assert seen == [
            "fired:researcher",
            "fired:provocateur",
            "fired:voice",
            "fired:publish",
            "complete",
        ]
