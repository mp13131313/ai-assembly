"""C32: voice/publish.py step3 → step2 fallback path.

Tests the per-voice publish module's ability to fall back from Step 3
to Step 2 (Athens --skip-step3 mode), the `was_step3` marker, and the
operator-hold filter.

No real Anthropic calls — these are pure file-shape transforms.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_RUNTIME = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_RUNTIME))

from flows.shared.io import write_json_atomic  # noqa: E402
from flows.voice.publish import (  # noqa: E402
    _to_publish_per_voice,
    _to_publish_per_voice_from_step2,
    publish_voice_artifacts_for_night,
)


# --- Fixture builders --------------------------------------------------

def _step3_output(voice_slug: str, theme_id: str = "theme_001") -> dict:
    return {
        "lineage": {
            "voice_slug": voice_slug,
            "night": 1,
            "own_first_draft_themes_covered": [theme_id],
            "voices_read": [
                {"voice_slug": "other", "council_member": "Other Voice", "shared_themes": [theme_id]},
            ],
        },
        "council_member": "Test Voice",
        "decision": "amend",
        "decision_rationale": "minor refinement",
        "amended_artifact_title": "Amended Title",
        "amended_artifact_subtitle": "Amended Subtitle",
        "amended_artifact_text": "amended body text " * 50,
        "selected_form": "essay",
        "word_count": 100,
        "amendments": [
            {
                "cited_voice": "Other Voice",
                "cited_voice_slug": "other",
                "cited_passage": "passage cited",
                "amendment_type": "agreement",
                "rationale": "I concur",
                "cited_theme_id": theme_id,
            }
        ],
    }


def _step2_output(voice_slug: str, theme_id: str = "theme_001") -> dict:
    return {
        "lineage": {
            "run_id": "athens_night_1",
            "night": 1,
            "voice_slug": voice_slug,
            "themes_covered": [theme_id],
            "primary_theme_id": theme_id,
        },
        "council_member": "Test Voice",
        "weight_assessment": "balanced",
        "focus_decision": "Focus on Response 1.",
        "focus_rationale": "the first one mattered most",
        "stance": "skeptical",
        "stance_rationale": "the claim deserves pressure",
        "selected_form": "essay",
        "form_rationale": "fits the question",
        "artifact_title": "First-Draft Title",
        "artifact_subtitle": "First-Draft Subtitle",
        "artifact_text": "first draft body " * 50,
        "word_count": 100,
        "model": "claude-opus-4-7",
    }


def _seed_run_dir(
    tmp_path: Path,
    *,
    step3_voices: list[str] | None = None,
    step2_voices: list[str] | None = None,
    held_voices: list[str] | None = None,
) -> Path:
    """Build a minimal run_dir with optional Step 3 / Step 2 / hold files."""
    run_dir = tmp_path / "athens_night_1"
    voice_dir = run_dir / "04_voice"
    if step3_voices:
        s3 = voice_dir / "step3_amended_artifacts"
        s3.mkdir(parents=True)
        for slug in step3_voices:
            write_json_atomic(s3 / f"{slug}.json", _step3_output(slug))
    if step2_voices:
        s2 = voice_dir / "step2_first_draft_artifacts"
        s2.mkdir(parents=True)
        for slug in step2_voices:
            write_json_atomic(s2 / f"{slug}.json", _step2_output(slug))
    if held_voices:
        dec_dir = voice_dir / "operator_decisions"
        dec_dir.mkdir(parents=True)
        for slug in held_voices:
            write_json_atomic(
                dec_dir / f"{slug}.json",
                {"voice_slug": slug, "decision": "hold_for_regen"},
            )
    return run_dir


# --- Shape transform tests --------------------------------------------

class TestStep3Shape:
    def test_was_step3_true(self):
        out = _to_publish_per_voice(_step3_output("plato"), night=1)
        assert out["was_step3"] is True

    def test_decision_propagates(self):
        out = _to_publish_per_voice(_step3_output("plato"), night=1)
        assert out["deliberation"]["decision"] == "amend"
        assert len(out["deliberation"]["amendments"]) == 1


class TestStep2Shape:
    def test_was_step3_false(self):
        out = _to_publish_per_voice_from_step2(_step2_output("plato"), night=1)
        assert out["was_step3"] is False

    def test_decision_is_first_draft(self):
        out = _to_publish_per_voice_from_step2(_step2_output("plato"), night=1)
        assert out["deliberation"]["decision"] == "first_draft"

    def test_voices_read_and_amendments_empty(self):
        out = _to_publish_per_voice_from_step2(_step2_output("plato"), night=1)
        assert out["deliberation"]["voices_read"] == []
        assert out["deliberation"]["amendments"] == []

    def test_artifact_fields_from_step2(self):
        out = _to_publish_per_voice_from_step2(_step2_output("plato"), night=1)
        assert out["artifact"]["title"] == "First-Draft Title"
        assert out["artifact"]["subtitle"] == "First-Draft Subtitle"
        assert out["artifact"]["stance"] == "skeptical"
        assert out["artifact"]["focus_decision"] == "Focus on Response 1."
        assert out["artifact"]["selected_form"] == "essay"

    def test_themes_addressed_from_lineage(self):
        out = _to_publish_per_voice_from_step2(_step2_output("plato"), night=1)
        assert out["themes_addressed"] == ["theme_001"]

    def test_url_path_uses_voice_slug(self):
        out = _to_publish_per_voice_from_step2(_step2_output("plato"), night=1)
        assert out["url_path"] == "/night-1/plato"

    def test_voice_name_from_council_member(self):
        out = _to_publish_per_voice_from_step2(_step2_output("plato"), night=1)
        assert out["voice_name"] == "Test Voice"


# --- Orchestrator-level tests ------------------------------------------

class TestPublishStep3Path:
    def test_step3_present_uses_step3_shape(self, tmp_path):
        run_dir = _seed_run_dir(tmp_path, step3_voices=["plato"], step2_voices=["plato"])
        project_root = tmp_path / "project"
        result = publish_voice_artifacts_for_night(
            run_dir=run_dir, night=1, project_root=project_root
        )
        assert result["voices_published"] == ["plato"]
        published = json.loads(
            (project_root / "published_artifacts" / "nights" / "night_1" / "plato.json").read_text()
        )
        assert published["was_step3"] is True
        assert published["deliberation"]["decision"] == "amend"


class TestPublishStep2Fallback:
    def test_step2_only_falls_back(self, tmp_path):
        run_dir = _seed_run_dir(tmp_path, step2_voices=["plato"])
        project_root = tmp_path / "project"
        result = publish_voice_artifacts_for_night(
            run_dir=run_dir, night=1, project_root=project_root
        )
        assert result["voices_published"] == ["plato"]
        published = json.loads(
            (project_root / "published_artifacts" / "nights" / "night_1" / "plato.json").read_text()
        )
        assert published["was_step3"] is False
        assert published["deliberation"]["decision"] == "first_draft"
        assert published["artifact"]["title"] == "First-Draft Title"

    def test_index_records_was_step3(self, tmp_path):
        run_dir = _seed_run_dir(tmp_path, step2_voices=["plato"])
        project_root = tmp_path / "project"
        publish_voice_artifacts_for_night(
            run_dir=run_dir, night=1, project_root=project_root
        )
        index = json.loads(
            (project_root / "published_artifacts" / "nights" / "night_1" / "_index.json").read_text()
        )
        assert index["voice_count"] == 1
        assert index["voices"][0]["was_step3"] is False

    def test_mixed_step3_and_step2(self, tmp_path):
        # plato has step3, cleopatra has step2 only.
        run_dir = _seed_run_dir(
            tmp_path, step3_voices=["plato"], step2_voices=["plato", "cleopatra"]
        )
        project_root = tmp_path / "project"
        result = publish_voice_artifacts_for_night(
            run_dir=run_dir, night=1, project_root=project_root
        )
        assert sorted(result["voices_published"]) == ["cleopatra", "plato"]
        plato_pub = json.loads(
            (project_root / "published_artifacts" / "nights" / "night_1" / "plato.json").read_text()
        )
        cleo_pub = json.loads(
            (project_root / "published_artifacts" / "nights" / "night_1" / "cleopatra.json").read_text()
        )
        assert plato_pub["was_step3"] is True
        assert cleo_pub["was_step3"] is False


class TestPublishHoldFilter:
    def test_held_voice_excluded_under_step2_fallback(self, tmp_path):
        run_dir = _seed_run_dir(
            tmp_path,
            step2_voices=["plato", "cleopatra"],
            held_voices=["cleopatra"],
        )
        project_root = tmp_path / "project"
        result = publish_voice_artifacts_for_night(
            run_dir=run_dir, night=1, project_root=project_root
        )
        assert result["voices_published"] == ["plato"]
        assert not (
            project_root / "published_artifacts" / "nights" / "night_1" / "cleopatra.json"
        ).exists()


class TestPublishEmpty:
    def test_no_step3_or_step2_returns_empty(self, tmp_path):
        run_dir = tmp_path / "athens_night_1"
        (run_dir / "04_voice").mkdir(parents=True)
        project_root = tmp_path / "project"
        result = publish_voice_artifacts_for_night(
            run_dir=run_dir, night=1, project_root=project_root
        )
        assert result["voices_published"] == []
        assert result["index_path"] is None
