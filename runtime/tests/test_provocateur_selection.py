"""Tests for python_select() — focused on C9 cross-night exclusion filter.

Spec §"Night 2 is different from Night 1": on Night 2/3, the Provocateur
must avoid repeating (theme, member) pairs already assigned on prior
nights. Theme_ids are NOT stable across Researcher runs (each run
generates fresh sequential IDs), so the implementation matches by
normalized theme title.

These tests exercise the filter in isolation — synthetic triage_voice +
triage_flags + grouping + council, no LLM involvement, no file I/O
(except the loader test, which uses tmp_path).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

# Make flows importable
_RUNTIME_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_RUNTIME_ROOT / "flows"))

from provocateur_flow import (  # noqa: E402
    _normalize_theme_title,
    load_prior_assignments_by_member,
    python_select,
)


# --- Fixtures (shared synthetic data) -----------------------------------

def _make_council(min_per_theme: int = 2):
    """Three-voice council. Default min_per_theme=2 so excluding one
    voice from a theme doesn't cascade-drop the theme — keeps the
    exclusion-filter signal isolated from the quorum cascade for
    unit-testing the filter behavior directly. Production default
    (3) would conflate the two effects in 3-voice tests."""
    return {
        "version": "test",
        "members": [
            {"name": "Alpha", "speaks_from": "x", "core_commitment": "x",
             "activates_on": "x", "goes_flat_on": "x", "stretch": "x",
             "translation_range": "wide", "stance_tendency": "asks",
             "medium": "essay"},
            {"name": "Beta", "speaks_from": "x", "core_commitment": "x",
             "activates_on": "x", "goes_flat_on": "x", "stretch": "x",
             "translation_range": "wide", "stance_tendency": "asks",
             "medium": "essay"},
            {"name": "Gamma", "speaks_from": "x", "core_commitment": "x",
             "activates_on": "x", "goes_flat_on": "x", "stretch": "x",
             "translation_range": "wide", "stance_tendency": "asks",
             "medium": "essay"},
        ],
        "selection_parameters": {
            "activation_threshold": 2,
            "min_members_per_theme": min_per_theme,
            "min_formulations_per_voice": 1,
            "target_formulations_per_voice": 5,
            "hard_cap_per_voice": 5,
            "friction_multiplier": {"low": 1.0, "moderate": 1.3, "high": 1.7},
            "fault_line_multiplier": {"absent": 1.0, "present": 1.5},
            "stretch_swap_enabled": False,
        },
    }


def _make_grouping(themes: list[tuple[str, str]]):
    """Build a grouping.json shape from (theme_id, title) pairs."""
    return {
        "themes": [
            {"theme_id": tid, "title": title, "abstract": "abstract", "clusters": []}
            for tid, title in themes
        ]
    }


def _make_triage_voice_results(voices: list[str], themes: list[str]):
    """Each voice ranks all themes as `strong` activation by default."""
    return [
        {
            "voice": v,
            "ranked_themes": [
                {"theme_id": tid, "activation": "strong", "is_stretch": False, "reason": "x"}
                for tid in themes
            ],
            "flat_themes": [],
        }
        for v in voices
    ]


def _make_triage_flags(theme_ids: list[str]):
    """All themes worth_surfacing=true, low friction, no fault line."""
    return {
        "theme_flags": [
            {"theme_id": tid, "worth_surfacing": True,
             "audience_friction": "low",
             "fault_line_present": False, "fault_line_description": ""}
            for tid in theme_ids
        ]
    }


# --- Tests --------------------------------------------------------------

class TestNormalizeTitle:
    def test_basic_lowercase(self):
        assert _normalize_theme_title("Foo Bar") == "foo bar"

    def test_whitespace_collapsing(self):
        assert _normalize_theme_title("  Foo   Bar  ") == "foo bar"
        assert _normalize_theme_title("Foo\nBar\tBaz") == "foo bar baz"

    def test_empty(self):
        assert _normalize_theme_title("") == ""
        assert _normalize_theme_title("   ") == ""

    def test_punctuation_preserved(self):
        # Punctuation kept — only case + whitespace normalized
        assert _normalize_theme_title("Foo, Bar!") == "foo, bar!"


class TestPythonSelectNoPriorNights:
    """Behavior when prior_assignments_by_member is None or empty —
    should be identical to the legacy v3 algorithm pre-C9."""

    def test_no_prior_param(self):
        council = _make_council()
        themes = [("theme_001", "Algorithmic Governance"),
                  ("theme_002", "Public Withdrawal"),
                  ("theme_003", "Recognition")]
        result = python_select(
            triage_voice_results=_make_triage_voice_results(
                ["Alpha", "Beta", "Gamma"],
                ["theme_001", "theme_002", "theme_003"],
            ),
            triage_flags_result=_make_triage_flags(
                ["theme_001", "theme_002", "theme_003"]
            ),
            grouping=_make_grouping(themes),
            council=council,
        )
        # All voices get all themes (3 voices × 3 themes, all strong, hard_cap=5)
        for v in ["Alpha", "Beta", "Gamma"]:
            assert set(result["assignments_by_member"][v]) == {
                "theme_001", "theme_002", "theme_003"
            }
        assert result["prior_exclusions_applied"] == []
        assert result["prior_exclusions_blocked"] == []
        assert result["prior_nights_consumed"] == 0

    def test_empty_prior_dict(self):
        council = _make_council()
        themes = [("theme_001", "X"), ("theme_002", "Y"), ("theme_003", "Z")]
        result = python_select(
            triage_voice_results=_make_triage_voice_results(
                ["Alpha", "Beta", "Gamma"],
                ["theme_001", "theme_002", "theme_003"],
            ),
            triage_flags_result=_make_triage_flags(
                ["theme_001", "theme_002", "theme_003"]
            ),
            grouping=_make_grouping(themes),
            council=council,
            prior_assignments_by_member={},
        )
        assert result["prior_exclusions_applied"] == []
        assert result["prior_nights_consumed"] == 0


class TestPythonSelectWithExclusions:
    """C9 exclusion filter behavior."""

    def test_exact_title_match_excludes(self):
        council = _make_council()
        # Night 2 has fresh themes (different IDs); one shares title with N1
        themes = [
            ("theme_001", "Algorithmic Governance"),  # NEW
            ("theme_002", "The Withdrawal from Public Life"),  # CARRIED FORWARD per Alpha's prior
            ("theme_003", "Recognition in Automated Decisions"),  # NEW
        ]
        # Alpha had "The Withdrawal from Public Life" on prior night (matches title)
        prior = {"Alpha": [_normalize_theme_title("The Withdrawal from Public Life")]}
        result = python_select(
            triage_voice_results=_make_triage_voice_results(
                ["Alpha", "Beta", "Gamma"],
                ["theme_001", "theme_002", "theme_003"],
            ),
            triage_flags_result=_make_triage_flags(
                ["theme_001", "theme_002", "theme_003"]
            ),
            grouping=_make_grouping(themes),
            council=council,
            prior_assignments_by_member=prior,
        )
        # Alpha should NOT have theme_002 (matches prior); other voices unaffected
        assert "theme_002" not in result["assignments_by_member"]["Alpha"]
        assert set(result["assignments_by_member"]["Alpha"]) == {
            "theme_001", "theme_003"
        }
        # Beta + Gamma are unaffected
        for v in ["Beta", "Gamma"]:
            assert set(result["assignments_by_member"][v]) == {
                "theme_001", "theme_002", "theme_003"
            }
        # Diagnostic: one exclusion applied
        assert len(result["prior_exclusions_applied"]) == 1
        excl = result["prior_exclusions_applied"][0]
        assert excl["voice"] == "Alpha"
        assert excl["theme_id"] == "theme_002"
        assert excl["title"] == "The Withdrawal from Public Life"

    def test_normalization_handles_case_and_whitespace(self):
        """Prior title in different case/whitespace still matches."""
        council = _make_council()
        themes = [
            ("theme_001", "Algorithmic Governance"),
            ("theme_002", "Recognition in Automated Decisions"),
            ("theme_003", "The Withdrawal from Public Life"),
        ]
        # Prior assignment uses different casing + extra whitespace
        prior = {
            "Alpha": [_normalize_theme_title("  algorithmic   GOVERNANCE  ")]
        }
        result = python_select(
            triage_voice_results=_make_triage_voice_results(
                ["Alpha", "Beta", "Gamma"],
                ["theme_001", "theme_002", "theme_003"],
            ),
            triage_flags_result=_make_triage_flags(
                ["theme_001", "theme_002", "theme_003"]
            ),
            grouping=_make_grouping(themes),
            council=council,
            prior_assignments_by_member=prior,
        )
        # theme_001 ("Algorithmic Governance") should be excluded for Alpha
        assert "theme_001" not in result["assignments_by_member"]["Alpha"]
        assert set(result["assignments_by_member"]["Alpha"]) == {
            "theme_002", "theme_003"
        }

    def test_force_fit_blocked_when_all_excluded(self):
        """When ALL of a voice's surviving themes are excluded, force-fit
        stays away from prior territory; voice ends with zero rather than
        re-deploying."""
        council = _make_council()
        # Only 1 theme; voice Alpha had it on prior night.
        # min_per_theme=3 means theme_001 needs 3 voices; we'll set up 3.
        # But Alpha's exclusion means after filter Alpha has 0; force-fit
        # would normally pick Alpha's only theme. C9 says don't.
        themes = [("theme_001", "X"), ("theme_002", "Y"), ("theme_003", "Z")]
        # Alpha had ALL 3 of these as Night 1 assignments
        prior = {
            "Alpha": [
                _normalize_theme_title("X"),
                _normalize_theme_title("Y"),
                _normalize_theme_title("Z"),
            ]
        }
        result = python_select(
            triage_voice_results=_make_triage_voice_results(
                ["Alpha", "Beta", "Gamma"],
                ["theme_001", "theme_002", "theme_003"],
            ),
            triage_flags_result=_make_triage_flags(
                ["theme_001", "theme_002", "theme_003"]
            ),
            grouping=_make_grouping(themes),
            council=council,
            prior_assignments_by_member=prior,
        )
        # Alpha should be blocked entirely
        assert result["assignments_by_member"]["Alpha"] == []
        assert len(result["prior_exclusions_blocked"]) == 1
        assert result["prior_exclusions_blocked"][0]["voice"] == "Alpha"
        # Beta + Gamma still get assignments
        for v in ["Beta", "Gamma"]:
            assert len(result["assignments_by_member"][v]) >= 1

    def test_multiple_prior_nights_cumulative(self):
        """When loading from multiple prior nights, exclusions accumulate."""
        council = _make_council()
        themes = [
            ("theme_001", "A"),
            ("theme_002", "B"),
            ("theme_003", "C"),
        ]
        # Simulating Night 3 with priors from N1 (had A) + N2 (had B) for Alpha
        prior = {
            "Alpha": [
                _normalize_theme_title("A"),
                _normalize_theme_title("B"),
            ]
        }
        result = python_select(
            triage_voice_results=_make_triage_voice_results(
                ["Alpha", "Beta", "Gamma"],
                ["theme_001", "theme_002", "theme_003"],
            ),
            triage_flags_result=_make_triage_flags(
                ["theme_001", "theme_002", "theme_003"]
            ),
            grouping=_make_grouping(themes),
            council=council,
            prior_assignments_by_member=prior,
        )
        # Alpha gets only theme_003 (C)
        assert result["assignments_by_member"]["Alpha"] == ["theme_003"]
        assert len(result["prior_exclusions_applied"]) == 2

    def test_unrelated_member_not_affected(self):
        """If only Alpha has prior assignments, Beta + Gamma run
        unconstrained."""
        council = _make_council()
        themes = [("theme_001", "X"), ("theme_002", "Y"), ("theme_003", "Z")]
        prior = {"Alpha": [_normalize_theme_title("X")]}
        result = python_select(
            triage_voice_results=_make_triage_voice_results(
                ["Alpha", "Beta", "Gamma"],
                ["theme_001", "theme_002", "theme_003"],
            ),
            triage_flags_result=_make_triage_flags(
                ["theme_001", "theme_002", "theme_003"]
            ),
            grouping=_make_grouping(themes),
            council=council,
            prior_assignments_by_member=prior,
        )
        # Alpha excluded from theme_001 only
        assert "theme_001" not in result["assignments_by_member"]["Alpha"]
        # Beta + Gamma still get all 3
        for v in ["Beta", "Gamma"]:
            assert set(result["assignments_by_member"][v]) == {
                "theme_001", "theme_002", "theme_003"
            }


class TestLoadPriorAssignments:
    """End-to-end loader: read selection.json + grouping.json from disk."""

    def test_loads_from_run_dir(self, tmp_path: Path):
        # Build a synthetic prior run_dir
        run_dir = tmp_path / "athens_2026_2026_05_07_night1"
        researcher_dir = run_dir / "02_researcher"
        provocateur_dir = run_dir / "03_provocateur"
        researcher_dir.mkdir(parents=True)
        provocateur_dir.mkdir(parents=True)

        (researcher_dir / "grouping.json").write_text(json.dumps({
            "themes": [
                {"theme_id": "theme_001", "title": "Algorithmic Governance"},
                {"theme_id": "theme_002", "title": "Public Withdrawal"},
                {"theme_id": "theme_003", "title": "Recognition"},
            ]
        }))
        (provocateur_dir / "selection.json").write_text(json.dumps({
            "assignments_by_member": {
                "Plato": ["theme_001", "theme_002"],
                "Cleopatra": ["theme_001", "theme_003"],
            }
        }))

        result = load_prior_assignments_by_member([run_dir])
        # Plato had theme_001 + theme_002 → titles "algorithmic governance" + "public withdrawal"
        assert "Plato" in result
        assert _normalize_theme_title("Algorithmic Governance") in result["Plato"]
        assert _normalize_theme_title("Public Withdrawal") in result["Plato"]
        # Cleopatra had theme_001 + theme_003
        assert _normalize_theme_title("Algorithmic Governance") in result["Cleopatra"]
        assert _normalize_theme_title("Recognition") in result["Cleopatra"]

    def test_multiple_run_dirs_accumulate(self, tmp_path: Path):
        for night, themes in [
            (1, [("theme_001", "Alpha N1"), ("theme_002", "Beta N1")]),
            (2, [("theme_001", "Alpha N2"), ("theme_002", "Beta N2")]),
        ]:
            rd = tmp_path / f"night{night}"
            (rd / "02_researcher").mkdir(parents=True)
            (rd / "03_provocateur").mkdir(parents=True)
            (rd / "02_researcher" / "grouping.json").write_text(json.dumps({
                "themes": [{"theme_id": t, "title": title} for t, title in themes]
            }))
            (rd / "03_provocateur" / "selection.json").write_text(json.dumps({
                "assignments_by_member": {"V": [t for t, _ in themes]}
            }))
        result = load_prior_assignments_by_member([
            tmp_path / "night1", tmp_path / "night2"
        ])
        # V should have 4 distinct titles accumulated across both nights
        assert len(result["V"]) == 4
        for title in ["alpha n1", "beta n1", "alpha n2", "beta n2"]:
            assert title in result["V"]

    def test_missing_selection_raises(self, tmp_path: Path):
        rd = tmp_path / "broken"
        (rd / "02_researcher").mkdir(parents=True)
        (rd / "02_researcher" / "grouping.json").write_text("{}")
        # missing 03_provocateur/selection.json
        with pytest.raises(SystemExit, match="selection.json not found"):
            load_prior_assignments_by_member([rd])

    def test_missing_grouping_raises(self, tmp_path: Path):
        rd = tmp_path / "broken"
        (rd / "03_provocateur").mkdir(parents=True)
        (rd / "03_provocateur" / "selection.json").write_text("{}")
        # missing 02_researcher/grouping.json
        with pytest.raises(SystemExit, match="grouping.json not found"):
            load_prior_assignments_by_member([rd])
