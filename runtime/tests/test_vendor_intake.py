"""Tests for flows/vendor_intake.py.

Vendor intake is the gate for the 5 athens-2026 sessions where the vendor
delivers a finished session_package.json instead of audio. The pipeline
boundary is the per-session 01_transcription/<sid>/ dir: status.json gates
the orchestrator, session_package.json gates the Researcher.

These tests cover:
  - Hard-fail surfaces: bad JSON, missing keys, session_id mismatch, empty
    turns, missing required turn fields, bad confidence values.
  - Warn-and-accept paths: missing review_queue, missing speakers_present,
    missing/lowercase confidence, role outside known set, roster drift vs
    sessions.json.
  - Successful land: status.json state=done + source=vendor, vendor.flag
    written, session_package.json produces a valid load_session_package
    (turn_index injected).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_RUNTIME_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_RUNTIME_ROOT))

from flows import vendor_intake  # noqa: E402
from flows.shared.io import load_session_package  # noqa: E402


# --- Fixtures ---------------------------------------------------------------


@pytest.fixture
def good_payload() -> dict:
    """Minimum valid session_package per docs/AI_Assembly_Transcription_Pipeline.md."""
    return {
        "metadata": {
            "session_id": "session_007",
            "session_title": "Test Session",
            "session_description": "",
            "session_format": "walking",
            "track": "AI DEMOCRACY MARATHON",
            "date_time": "2026-05-07T10:00:00+03:00",
            "venue": "Demos · Meeting Point",
            "roster": [
                {"name": "Christoph Quarch", "title": "", "affiliation": "", "bio": ""},
            ],
        },
        "transcript": {
            "speakers_present": ["Christoph Quarch"],
            "turns": [
                {
                    "turn_index": 0,
                    "speaker": "Christoph Quarch",
                    "role": "moderator",
                    "confidence": "high",
                    "text": "Welcome to the Pnyx.",
                },
                {
                    "turn_index": 1,
                    "speaker": "Christoph Quarch",
                    "role": "moderator",
                    "confidence": "high",
                    "text": "This is where Athenian democracy began.",
                },
            ],
        },
        "review_queue": {
            "low_confidence_attributions": [],
            "verify_markers": [],
            "diarization_flags": [],
        },
    }


@pytest.fixture
def run_dir(tmp_path: Path) -> Path:
    rd = tmp_path / "athens_night_1"
    rd.mkdir()
    return rd


def _write_vendor_file(tmp_path: Path, payload: dict) -> Path:
    p = tmp_path / "vendor.json"
    p.write_text(json.dumps(payload), encoding="utf-8")
    return p


# --- Happy path -------------------------------------------------------------


class TestSuccessfulLand:
    def test_writes_session_package_status_and_flag(
        self, tmp_path, run_dir, good_payload
    ):
        vfile = _write_vendor_file(tmp_path, good_payload)
        result = vendor_intake.land(
            vendor_file=vfile,
            run_dir=run_dir,
            session_id="session_007",
        )
        assert result["state"] == "done"
        sdir = result["session_dir"]
        assert (sdir / "session_package.json").exists()
        assert (sdir / "status.json").exists()
        assert (sdir / "vendor.flag").exists()
        assert not (sdir / "vendor.error").exists()
        assert not (sdir / "vendor.warnings").exists()

    def test_status_json_orchestrator_compat(
        self, tmp_path, run_dir, good_payload
    ):
        # Orchestrator (overnight_orchestrator.transcription_state) reads
        # status.json and looks for state == "done". This contract MUST
        # hold or vendor sessions never gate-open the Researcher.
        vfile = _write_vendor_file(tmp_path, good_payload)
        result = vendor_intake.land(
            vendor_file=vfile, run_dir=run_dir, session_id="session_007",
        )
        st = json.loads((result["session_dir"] / "status.json").read_text())
        assert st["state"] == "done"
        assert st["source"] == "vendor"
        assert st["session_id"] == "session_007"

    def test_session_package_loads_via_normalizer(
        self, tmp_path, run_dir, good_payload
    ):
        vfile = _write_vendor_file(tmp_path, good_payload)
        result = vendor_intake.land(
            vendor_file=vfile, run_dir=run_dir, session_id="session_007",
        )
        pkg = load_session_package(result["session_dir"] / "session_package.json")
        assert pkg["transcript"]["turns"][0]["turn_index"] == 0
        assert pkg["transcript"]["turns"][1]["turn_index"] == 1


# --- Hard-fail paths --------------------------------------------------------


class TestHardFails:
    def test_unparseable_json(self, tmp_path, run_dir):
        vfile = tmp_path / "bad.json"
        vfile.write_text("{not valid json", encoding="utf-8")
        result = vendor_intake.land(
            vendor_file=vfile, run_dir=run_dir, session_id="session_007",
        )
        assert result["state"] == "error"
        assert (result["session_dir"] / "vendor.error").exists()
        st = json.loads((result["session_dir"] / "status.json").read_text())
        assert st["state"] == "error"

    def test_session_id_mismatch(self, tmp_path, run_dir, good_payload):
        good_payload["metadata"]["session_id"] = "session_999"
        vfile = _write_vendor_file(tmp_path, good_payload)
        result = vendor_intake.land(
            vendor_file=vfile, run_dir=run_dir, session_id="session_007",
        )
        assert result["state"] == "error"
        err = json.loads((result["session_dir"] / "vendor.error").read_text())
        assert any("session_id" in r for r in err["reasons"])

    def test_missing_metadata(self, tmp_path, run_dir, good_payload):
        del good_payload["metadata"]
        vfile = _write_vendor_file(tmp_path, good_payload)
        result = vendor_intake.land(
            vendor_file=vfile, run_dir=run_dir, session_id="session_007",
        )
        assert result["state"] == "error"

    def test_empty_turns(self, tmp_path, run_dir, good_payload):
        good_payload["transcript"]["turns"] = []
        vfile = _write_vendor_file(tmp_path, good_payload)
        result = vendor_intake.land(
            vendor_file=vfile, run_dir=run_dir, session_id="session_007",
        )
        assert result["state"] == "error"

    def test_turn_missing_text(self, tmp_path, run_dir, good_payload):
        good_payload["transcript"]["turns"][0]["text"] = ""
        vfile = _write_vendor_file(tmp_path, good_payload)
        result = vendor_intake.land(
            vendor_file=vfile, run_dir=run_dir, session_id="session_007",
        )
        assert result["state"] == "error"

    def test_invalid_confidence(self, tmp_path, run_dir, good_payload):
        good_payload["transcript"]["turns"][0]["confidence"] = "uncertain"
        vfile = _write_vendor_file(tmp_path, good_payload)
        result = vendor_intake.land(
            vendor_file=vfile, run_dir=run_dir, session_id="session_007",
        )
        assert result["state"] == "error"

    def test_hard_fail_collects_all_reasons(self, tmp_path, run_dir, good_payload):
        # Two violations in two different turns — vendor.error should list both.
        good_payload["transcript"]["turns"][0]["text"] = ""
        good_payload["transcript"]["turns"][1]["confidence"] = "yikes"
        vfile = _write_vendor_file(tmp_path, good_payload)
        result = vendor_intake.land(
            vendor_file=vfile, run_dir=run_dir, session_id="session_007",
        )
        err = json.loads((result["session_dir"] / "vendor.error").read_text())
        assert len(err["reasons"]) >= 2


# --- Warn-and-accept paths --------------------------------------------------


class TestWarnAndAccept:
    def test_missing_review_queue_silently_injected(
        self, tmp_path, run_dir, good_payload
    ):
        del good_payload["review_queue"]
        vfile = _write_vendor_file(tmp_path, good_payload)
        result = vendor_intake.land(
            vendor_file=vfile, run_dir=run_dir, session_id="session_007",
        )
        assert result["state"] == "done"
        # No warning surfaced — review_queue absence is normal for clean output.
        assert not (result["session_dir"] / "vendor.warnings").exists()
        pkg = json.loads((result["session_dir"] / "session_package.json").read_text())
        assert pkg["review_queue"]["verify_markers"] == []

    def test_confidence_uppercase_normalized(
        self, tmp_path, run_dir, good_payload
    ):
        good_payload["transcript"]["turns"][0]["confidence"] = "HIGH"
        vfile = _write_vendor_file(tmp_path, good_payload)
        result = vendor_intake.land(
            vendor_file=vfile, run_dir=run_dir, session_id="session_007",
        )
        assert result["state"] == "done"
        pkg = json.loads((result["session_dir"] / "session_package.json").read_text())
        assert pkg["transcript"]["turns"][0]["confidence"] == "high"

    def test_confidence_missing_defaults_to_high(
        self, tmp_path, run_dir, good_payload
    ):
        del good_payload["transcript"]["turns"][0]["confidence"]
        vfile = _write_vendor_file(tmp_path, good_payload)
        result = vendor_intake.land(
            vendor_file=vfile, run_dir=run_dir, session_id="session_007",
        )
        assert result["state"] == "done"
        warnings = json.loads(
            (result["session_dir"] / "vendor.warnings").read_text()
        )["warnings"]
        assert any("confidence missing" in w for w in warnings)

    def test_unknown_role_defaults_to_panelist(
        self, tmp_path, run_dir, good_payload
    ):
        good_payload["transcript"]["turns"][0]["role"] = "facilitator"
        vfile = _write_vendor_file(tmp_path, good_payload)
        result = vendor_intake.land(
            vendor_file=vfile, run_dir=run_dir, session_id="session_007",
        )
        assert result["state"] == "done"
        pkg = json.loads((result["session_dir"] / "session_package.json").read_text())
        assert pkg["transcript"]["turns"][0]["role"] == "panelist"

    def test_roster_drift_vendor_wins(
        self, tmp_path, run_dir, good_payload
    ):
        # sessions.json says the roster is [Alice]; vendor says [Christoph
        # Quarch]. Vendor reality wins, but warning is surfaced.
        sessions_roster = [{"name": "Alice", "title": "", "affiliation": "", "bio": ""}]
        vfile = _write_vendor_file(tmp_path, good_payload)
        result = vendor_intake.land(
            vendor_file=vfile,
            run_dir=run_dir,
            session_id="session_007",
            sessions_json_roster=sessions_roster,
        )
        assert result["state"] == "done"
        warnings = json.loads(
            (result["session_dir"] / "vendor.warnings").read_text()
        )["warnings"]
        assert any("roster differs" in w for w in warnings)
        pkg = json.loads((result["session_dir"] / "session_package.json").read_text())
        # Vendor's roster is what's preserved.
        assert pkg["metadata"]["roster"][0]["name"] == "Christoph Quarch"

    def test_speakers_present_recomputed(self, tmp_path, run_dir, good_payload):
        good_payload["transcript"]["speakers_present"] = ["Wrong Name"]
        vfile = _write_vendor_file(tmp_path, good_payload)
        result = vendor_intake.land(
            vendor_file=vfile, run_dir=run_dir, session_id="session_007",
        )
        assert result["state"] == "done"
        pkg = json.loads((result["session_dir"] / "session_package.json").read_text())
        assert pkg["transcript"]["speakers_present"] == ["Christoph Quarch"]
        warnings = json.loads(
            (result["session_dir"] / "vendor.warnings").read_text()
        )["warnings"]
        assert any("speakers_present" in w for w in warnings)


# --- Re-run cleanliness -----------------------------------------------------


class TestReRun:
    def test_rerun_clears_old_error(self, tmp_path, run_dir, good_payload):
        # First, a failing run leaves a vendor.error.
        bad = dict(good_payload)
        bad["metadata"] = dict(bad["metadata"])
        bad["metadata"]["session_id"] = "wrong"
        vfile = _write_vendor_file(tmp_path, bad)
        result1 = vendor_intake.land(
            vendor_file=vfile, run_dir=run_dir, session_id="session_007",
        )
        assert result1["state"] == "error"
        sdir = result1["session_dir"]
        assert (sdir / "vendor.error").exists()

        # Now re-run with the good payload. vendor.error should be cleaned up.
        good_file = _write_vendor_file(tmp_path / "good_dir", good_payload)
        result2 = vendor_intake.land(
            vendor_file=good_file, run_dir=run_dir, session_id="session_007",
        )
        assert result2["state"] == "done"
        assert not (sdir / "vendor.error").exists()

    def test_rerun_clears_old_warnings(self, tmp_path, run_dir, good_payload):
        # First run with a warning-triggering payload.
        warned = dict(good_payload)
        warned["transcript"] = dict(warned["transcript"])
        warned["transcript"]["speakers_present"] = ["Wrong"]
        vfile = _write_vendor_file(tmp_path, warned)
        result1 = vendor_intake.land(
            vendor_file=vfile, run_dir=run_dir, session_id="session_007",
        )
        assert (result1["session_dir"] / "vendor.warnings").exists()

        # Second run with the clean payload — warnings file should be cleared.
        good_file = _write_vendor_file(tmp_path / "good_dir", good_payload)
        result2 = vendor_intake.land(
            vendor_file=good_file, run_dir=run_dir, session_id="session_007",
        )
        assert not (result2["session_dir"] / "vendor.warnings").exists()


# --- _write_vendor_file helper needs unique parent for re-run dir
@pytest.fixture(autouse=True)
def _ensure_subdir_parents(tmp_path):
    """Some tests write a second vendor file at tmp_path/<subdir>/vendor.json;
    pre-create the subdirs so write doesn't ENOENT."""
    (tmp_path / "good_dir").mkdir(exist_ok=True)
