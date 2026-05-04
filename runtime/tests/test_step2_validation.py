"""C28b: Step 2 validator + operator gate + editor/publish hold integration.

Tests the validation module's mechanics (length compliance, AI-slop filter,
overall verdict computation, file shape) WITHOUT making real Anthropic calls.
The actual prompts are exercised in dryruns, not unit tests — these focus
on contract + dispatch logic.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

_RUNTIME = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_RUNTIME))

from flows.voice.step2_validation import (  # noqa: E402
    _AI_SLOP_LEXICON,
    _check_length_compliance,
    _load_prior_artifact,
    _overall_verdict,
    run_step2_validation,
)


# --- Mechanical length check (no LLM) ----------------------------------

class TestLengthCompliance:
    def test_within_range(self):
        card = {"length_and_format_constraints": {"min_words": 400, "max_words": 600}}
        text = "word " * 500
        assert _check_length_compliance(text, card) is None

    def test_under_floor(self):
        card = {"length_and_format_constraints": {"min_words": 400, "max_words": 600}}
        text = "word " * 100
        result = _check_length_compliance(text, card)
        assert result is not None
        assert result["verdict"] == "under"
        assert result["actual_words"] == 100
        assert result["declared_range"] == [400, 600]

    def test_over_ceiling(self):
        card = {"length_and_format_constraints": {"min_words": 400, "max_words": 600}}
        text = "word " * 1000
        result = _check_length_compliance(text, card)
        assert result is not None
        assert result["verdict"] == "over"
        assert result["actual_words"] == 1000

    def test_no_constraints_returns_none(self):
        assert _check_length_compliance("word " * 500, {}) is None

    def test_string_constraints_returns_none(self):
        # Some cards have free-form prose constraints
        card = {"length_and_format_constraints": "around 500 words is right"}
        assert _check_length_compliance("word " * 500, card) is None

    def test_alt_range_shape(self):
        # Some cards use "range": [min, max]
        card = {"length_and_format_constraints": {"range": [400, 600]}}
        result = _check_length_compliance("word " * 100, card)
        assert result is not None
        assert result["verdict"] == "under"


# --- Overall verdict computation ---------------------------------------

class TestOverallVerdict:
    def test_all_pass(self):
        v, r = _overall_verdict(
            {"verdict": "PASS"}, {"verdict": "PASS"}, {"verdict": "PASS"}, None
        )
        assert v == "PASS" and r == "publish"

    def test_any_warn(self):
        v, r = _overall_verdict(
            {"verdict": "PASS"}, {"verdict": "WARN"}, {"verdict": "PASS"}, None
        )
        assert v == "WARN" and r == "review"

    def test_any_hold_wins(self):
        v, r = _overall_verdict(
            {"verdict": "WARN"}, {"verdict": "PASS"}, {"verdict": "HOLD"}, None
        )
        assert v == "HOLD" and r == "hold_for_regen"

    def test_cross_night_echo_included(self):
        v, r = _overall_verdict(
            {"verdict": "PASS"}, {"verdict": "PASS"}, {"verdict": "PASS"},
            {"verdict": "HOLD"},
        )
        assert v == "HOLD"


# --- AI-slop lexicon ---------------------------------------------------

class TestAISlopLexicon:
    def test_lexicon_has_canonical_tells(self):
        for tell in ["fascinating", "interesting", "thought-provoking",
                     "important to note", "crucial", "innovative", "delve"]:
            assert tell in _AI_SLOP_LEXICON


# --- Prior artifact loader ---------------------------------------------

class TestLoadPriorArtifact:
    def test_night_1_returns_none(self, tmp_path):
        assert _load_prior_artifact(tmp_path, 1, "plato") is None

    def test_missing_prior_returns_none(self, tmp_path):
        assert _load_prior_artifact(tmp_path, 2, "plato") is None

    def test_loads_artifact_text(self, tmp_path):
        prior_dir = tmp_path / "published_artifacts" / "nights" / "night_1"
        prior_dir.mkdir(parents=True)
        (prior_dir / "plato.json").write_text(json.dumps({
            "artifact_text": "first night response",
            "voice_name": "Plato",
        }))
        assert _load_prior_artifact(tmp_path, 2, "plato") == "first night response"

    def test_falls_back_to_body_field(self, tmp_path):
        prior_dir = tmp_path / "published_artifacts" / "nights" / "night_1"
        prior_dir.mkdir(parents=True)
        (prior_dir / "plato.json").write_text(json.dumps({
            "body": "alt body field",
        }))
        assert _load_prior_artifact(tmp_path, 2, "plato") == "alt body field"


# --- Orchestrator-shape integration ------------------------------------

class TestRunStep2Validation:
    """Verify run_step2_validation writes the correct file shape + skips
    re-runs when output already exists. Mocks all 3 (or 4) pillar LLM calls."""

    def test_resumes_from_disk_if_present(self, tmp_path):
        # Pre-stage an existing validation output
        out_dir = tmp_path / "04_voice" / "step2_validation"
        out_dir.mkdir(parents=True)
        existing = {"voice_slug": "plato", "overall_verdict": "PASS",
                    "schema_version": "1.0"}
        (out_dir / "plato.json").write_text(json.dumps(existing))

        artifact = {"lineage": {"voice_slug": "plato"}, "artifact_text": "x"}
        result = run_step2_validation(
            artifact, {}, tmp_path,
            night=1, project_root=tmp_path,
        )
        assert result == existing  # short-circuit returned the on-disk file

    def test_writes_combined_file_with_all_pillars(self, tmp_path):
        artifact = {
            "lineage": {"voice_slug": "plato"},
            "artifact_text": "test artifact text",
        }
        card = {"length_and_format_constraints": {"min_words": 1, "max_words": 100}}

        with patch("flows.voice.step2_validation.check_safeguards") as ms, \
             patch("flows.voice.step2_validation.check_engagement") as me, \
             patch("flows.voice.step2_validation.check_voice_fidelity") as mv:
            ms.return_value = {"verdict": "PASS", "_call": {}}
            me.return_value = {"verdict": "PASS", "_call": {}}
            mv.return_value = {"verdict": "PASS", "_call": {}}
            result = run_step2_validation(
                artifact, card, tmp_path,
                night=1, project_root=tmp_path,
            )

        assert result["voice_slug"] == "plato"
        assert result["overall_verdict"] == "PASS"
        assert result["operator_recommendation"] == "publish"
        assert "safeguards" in result
        assert "engagement" in result
        assert "voice_fidelity" in result
        assert result["cross_night_echo"] is None  # Night 1, no cross-night
        # File written to disk
        out_path = tmp_path / "04_voice" / "step2_validation" / "plato.json"
        assert out_path.exists()
        assert json.loads(out_path.read_text())["voice_slug"] == "plato"

    def test_warn_verdict_propagates(self, tmp_path):
        artifact = {
            "lineage": {"voice_slug": "plato"},
            "artifact_text": "test artifact text",
        }
        with patch("flows.voice.step2_validation.check_safeguards") as ms, \
             patch("flows.voice.step2_validation.check_engagement") as me, \
             patch("flows.voice.step2_validation.check_voice_fidelity") as mv:
            ms.return_value = {"verdict": "PASS", "_call": {}}
            me.return_value = {"verdict": "WARN", "_call": {},
                               "form_fidelity": {"declared": "dialogue",
                                                 "observed": "monologue"}}
            mv.return_value = {"verdict": "PASS", "_call": {}}
            result = run_step2_validation(
                artifact, {}, tmp_path,
                night=1, project_root=tmp_path,
            )
        assert result["overall_verdict"] == "WARN"
        assert result["operator_recommendation"] == "review"

    def test_hold_verdict_propagates(self, tmp_path):
        artifact = {
            "lineage": {"voice_slug": "plato"},
            "artifact_text": "test artifact text",
        }
        with patch("flows.voice.step2_validation.check_safeguards") as ms, \
             patch("flows.voice.step2_validation.check_engagement") as me, \
             patch("flows.voice.step2_validation.check_voice_fidelity") as mv:
            ms.return_value = {"verdict": "HOLD", "_call": {},
                               "ai_self_acknowledgment": {"text": "as a language model",
                                                          "why": "AI self-ack"}}
            me.return_value = {"verdict": "PASS", "_call": {}}
            mv.return_value = {"verdict": "PASS", "_call": {}}
            result = run_step2_validation(
                artifact, {}, tmp_path,
                night=1, project_root=tmp_path,
            )
        assert result["overall_verdict"] == "HOLD"
        assert result["operator_recommendation"] == "hold_for_regen"

    def test_cross_night_echo_runs_on_night_2(self, tmp_path):
        """Night 2 with prior artifact present → cross_night_echo is invoked."""
        # Stage prior night artifact
        prior_dir = tmp_path / "published_artifacts" / "nights" / "night_1"
        prior_dir.mkdir(parents=True)
        (prior_dir / "plato.json").write_text(json.dumps({
            "artifact_text": "first night response",
        }))

        artifact = {
            "lineage": {"voice_slug": "plato"},
            "artifact_text": "second night response",
        }
        with patch("flows.voice.step2_validation.check_safeguards") as ms, \
             patch("flows.voice.step2_validation.check_engagement") as me, \
             patch("flows.voice.step2_validation.check_voice_fidelity") as mv, \
             patch("flows.voice.step2_validation.check_cross_night_echo") as mc:
            ms.return_value = {"verdict": "PASS", "_call": {}}
            me.return_value = {"verdict": "PASS", "_call": {}}
            mv.return_value = {"verdict": "PASS", "_call": {}}
            mc.return_value = {"verdict": "PASS", "echo_level": "mild", "_call": {}}
            result = run_step2_validation(
                artifact, {}, tmp_path,
                night=2, project_root=tmp_path,
            )
        # Cross-night was invoked + result captured
        mc.assert_called_once()
        assert result["cross_night_echo"]["echo_level"] == "mild"


# --- Orchestrator validation_gate_state -------------------------------

class TestOrchestratorGateState:
    def test_no_validation_dir_means_open_gate(self, tmp_path):
        from scripts import overnight_orchestrator as orch
        gate = orch.validation_gate_state(tmp_path)
        assert gate["state"] == "all_clear"
        assert gate["n_total"] == 0

    def test_all_pass_voices_open_gate(self, tmp_path):
        from scripts import overnight_orchestrator as orch
        val_dir = tmp_path / "04_voice" / "step2_validation"
        val_dir.mkdir(parents=True)
        (val_dir / "plato.json").write_text(json.dumps({
            "voice_slug": "plato", "overall_verdict": "PASS",
        }))
        gate = orch.validation_gate_state(tmp_path)
        assert gate["state"] == "all_clear"
        assert gate["n_total"] == 1
        assert gate["n_flagged"] == 0

    def test_undecided_warn_halts_gate(self, tmp_path):
        from scripts import overnight_orchestrator as orch
        val_dir = tmp_path / "04_voice" / "step2_validation"
        val_dir.mkdir(parents=True)
        (val_dir / "plato.json").write_text(json.dumps({
            "voice_slug": "plato", "overall_verdict": "WARN",
        }))
        gate = orch.validation_gate_state(tmp_path)
        assert gate["state"] == "awaiting_operator"
        assert gate["n_flagged"] == 1
        assert gate["undecided"] == ["plato"]

    def test_decided_warn_opens_gate(self, tmp_path):
        from scripts import overnight_orchestrator as orch
        val_dir = tmp_path / "04_voice" / "step2_validation"
        val_dir.mkdir(parents=True)
        (val_dir / "plato.json").write_text(json.dumps({
            "voice_slug": "plato", "overall_verdict": "WARN",
        }))
        dec_dir = tmp_path / "04_voice" / "operator_decisions"
        dec_dir.mkdir(parents=True)
        (dec_dir / "plato.json").write_text(json.dumps({
            "voice_slug": "plato", "decision": "release",
        }))
        gate = orch.validation_gate_state(tmp_path)
        assert gate["state"] == "all_clear"
        assert gate["n_decided"] == 1


# --- Editor + publish: hold filtering ---------------------------------

class TestEditorRespectsHold:
    def test_held_voice_excluded_from_step2_artifacts(self, tmp_path):
        from flows.editor.routing import _load_step2_artifacts
        s2_dir = tmp_path / "04_voice" / "step2_first_draft_artifacts"
        s2_dir.mkdir(parents=True)
        for slug in ("plato", "cleopatra", "octopus"):
            (s2_dir / f"{slug}.json").write_text(json.dumps({
                "lineage": {"voice_slug": slug},
                "artifact_text": f"{slug} artifact",
            }))

        # No decisions yet → all 3 included
        all_three = _load_step2_artifacts(tmp_path)
        assert len(all_three) == 3
        slugs = {a["lineage"]["voice_slug"] for a in all_three}
        assert slugs == {"plato", "cleopatra", "octopus"}

        # Hold octopus → 2 returned
        dec_dir = tmp_path / "04_voice" / "operator_decisions"
        dec_dir.mkdir(parents=True)
        (dec_dir / "octopus.json").write_text(json.dumps({
            "voice_slug": "octopus", "decision": "hold_for_regen",
        }))
        two = _load_step2_artifacts(tmp_path)
        assert len(two) == 2
        slugs = {a["lineage"]["voice_slug"] for a in two}
        assert slugs == {"plato", "cleopatra"}

    def test_release_decision_doesnt_filter(self, tmp_path):
        from flows.editor.routing import _load_step2_artifacts
        s2_dir = tmp_path / "04_voice" / "step2_first_draft_artifacts"
        s2_dir.mkdir(parents=True)
        (s2_dir / "plato.json").write_text(json.dumps({
            "lineage": {"voice_slug": "plato"},
            "artifact_text": "x",
        }))
        dec_dir = tmp_path / "04_voice" / "operator_decisions"
        dec_dir.mkdir(parents=True)
        (dec_dir / "plato.json").write_text(json.dumps({
            "voice_slug": "plato", "decision": "release",
        }))
        # release doesn't filter
        result = _load_step2_artifacts(tmp_path)
        assert len(result) == 1


class TestPublishRespectsHold:
    def test_held_voices_loader(self, tmp_path):
        from flows.voice.publish import _load_held_voices
        dec_dir = tmp_path / "04_voice" / "operator_decisions"
        dec_dir.mkdir(parents=True)
        (dec_dir / "plato.json").write_text(json.dumps({
            "voice_slug": "plato", "decision": "hold_for_regen",
        }))
        (dec_dir / "cleopatra.json").write_text(json.dumps({
            "voice_slug": "cleopatra", "decision": "release",
        }))
        held = _load_held_voices(tmp_path)
        assert held == {"plato"}
