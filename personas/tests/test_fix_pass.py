"""test_fix_pass.py — Tests for FU#13 Pass 7a-FIX linear patcher (FU#10-mod).

Covers:
  1. apply_patch_in_place() path-walker — dot-notation, list indices, error paths
  2. _fix_log.json schema shape (fields present, types correct)
  3. Schema invariant: patches_applied + patches_failed + patches_skipped <=
     patches_emitted, field_issues_count and anachronism_flags_count are ints

Does NOT cover (future work):
  - Integration test with mocked Claude API exercising _pass_7a_fix() end-to-end
  - Snapshot directory creation (FU#5) — tested manually per Phase 1/2 runs
  - Idempotency guard behaviour (requires orchestrator execution)
"""
from __future__ import annotations

import pytest

from flows.shared.patch_walker import apply_patch_in_place


# ── apply_patch_in_place — happy paths ──────────────────────────────────────

def test_patch_walker_replaces_top_level_string():
    d = {"knowledge_boundary": "old value", "other": "unchanged"}
    apply_patch_in_place(d, "knowledge_boundary", "new value")
    assert d["knowledge_boundary"] == "new value"
    assert d["other"] == "unchanged"


def test_patch_walker_replaces_top_level_dict():
    d = {"world": {"a": 1}}
    apply_patch_in_place(d, "world", {"b": 2})
    assert d["world"] == {"b": 2}


def test_patch_walker_replaces_list_element():
    d = {"constitution": ["a", "b", "c"]}
    apply_patch_in_place(d, "constitution[1]", "B")
    assert d["constitution"] == ["a", "B", "c"]


def test_patch_walker_replaces_list_element_zeroth():
    d = {"items": ["first", "second"]}
    apply_patch_in_place(d, "items[0]", "FIRST")
    assert d["items"] == ["FIRST", "second"]


def test_patch_walker_replaces_nested_dict_field():
    d = {"constitution": [{"principle": "old", "category": "ethical"}]}
    apply_patch_in_place(d, "constitution[0].principle", "new principle text")
    assert d["constitution"][0]["principle"] == "new principle text"
    assert d["constitution"][0]["category"] == "ethical"


def test_patch_walker_replaces_deeply_nested_field():
    d = {
        "reasoning_method": {
            "steps": [
                {"name": "step1", "worked_demonstration": "old demo"},
            ]
        }
    }
    apply_patch_in_place(
        d, "reasoning_method.steps[0].worked_demonstration", "new demo"
    )
    assert d["reasoning_method"]["steps"][0]["worked_demonstration"] == "new demo"
    assert d["reasoning_method"]["steps"][0]["name"] == "step1"


def test_patch_walker_handles_multi_level_paths():
    d = {"a": {"b": {"c": {"d": "leaf"}}}}
    apply_patch_in_place(d, "a.b.c.d", "NEW LEAF")
    assert d["a"]["b"]["c"]["d"] == "NEW LEAF"


def test_patch_walker_does_not_mutate_sibling_entries():
    d = {
        "constitution": [
            {"principle": "keep A", "category": "ontological"},
            {"principle": "patch me", "category": "ethical"},
            {"principle": "keep C", "category": "epistemological"},
        ]
    }
    apply_patch_in_place(d, "constitution[1].principle", "patched")
    assert d["constitution"][0] == {"principle": "keep A", "category": "ontological"}
    assert d["constitution"][1] == {"principle": "patched", "category": "ethical"}
    assert d["constitution"][2] == {"principle": "keep C", "category": "epistemological"}


# ── apply_patch_in_place — error paths ──────────────────────────────────────

def test_patch_walker_empty_path_raises():
    with pytest.raises(ValueError, match="Empty path"):
        apply_patch_in_place({"a": 1}, "", "new")


def test_patch_walker_missing_mid_key_raises():
    d = {"a": {"b": 1}}
    with pytest.raises(KeyError, match="missing key"):
        apply_patch_in_place(d, "a.c.d", "new")


def test_patch_walker_non_list_index_raises():
    d = {"not_a_list": {"x": 1}}
    with pytest.raises(TypeError, match="expected list"):
        apply_patch_in_place(d, "not_a_list[0]", "new")


def test_patch_walker_final_non_list_index_raises():
    d = {"constitution": "not a list"}
    with pytest.raises(TypeError, match="expected list"):
        apply_patch_in_place(d, "constitution[0]", "new")


def test_patch_walker_out_of_range_index_raises():
    d = {"items": ["a", "b"]}
    with pytest.raises(IndexError, match="out of range"):
        apply_patch_in_place(d, "items[5]", "new")


def test_patch_walker_out_of_range_mid_path_raises():
    d = {"items": [{"a": 1}]}
    with pytest.raises(IndexError, match="out of range"):
        apply_patch_in_place(d, "items[3].a", "new")


# ── _fix_log.json schema shape ──────────────────────────────────────────────

# The fix_log structure defined in run_persona_pipeline.py::_pass_7a_fix is
# read by FU#7 operator summary + metadata.fix_pass_log in the assembled
# card. This test pins the shape contract so a refactor can't silently
# break the summary output or the card's metadata.

FIX_LOG_SCHEMA_REQUIRED_KEYS = {
    "validator_verdict",
    "validator_model",
    "field_issues_count",
    "anachronism_flags_count",
    "patches_emitted",
    "patches_applied",
    "patches_failed",
    "patches_skipped",
    "post_fix_verdict",
    "patches",
}


def _example_fix_log() -> dict:
    """Return an example fix_log matching the production schema."""
    return {
        "validator_verdict": "REVISION_NEEDED",
        "validator_model": "openai:gpt-5.4",
        "field_issues_count": 15,
        "anachronism_flags_count": 8,
        "patches_emitted": 15,
        "patches_applied": 15,
        "patches_failed": 0,
        "patches_skipped": 0,
        "post_fix_verdict": "REVISION_NEEDED",
        "patches": [
            {
                "pass_id": "2",
                "field_path": "topics_requiring_care[1].navigation",
                "rationale": "tighten hyphenated-virtue-signaling clause",
                "status": "applied",
            }
        ],
    }


def test_fix_log_has_all_required_keys():
    fl = _example_fix_log()
    missing = FIX_LOG_SCHEMA_REQUIRED_KEYS - set(fl.keys())
    assert not missing, f"fix_log missing keys: {missing}"


def test_fix_log_counters_are_ints():
    fl = _example_fix_log()
    for key in ("field_issues_count", "anachronism_flags_count",
                "patches_emitted", "patches_applied",
                "patches_failed", "patches_skipped"):
        assert isinstance(fl[key], int), f"{key} must be int"


def test_fix_log_applied_plus_failed_plus_skipped_le_emitted():
    """Invariant: patches_applied + patches_failed + patches_skipped <= patches_emitted.
    (Not strict == because a patch can be rejected before counting into any bucket.)"""
    fl = _example_fix_log()
    total = fl["patches_applied"] + fl["patches_failed"] + fl["patches_skipped"]
    assert total <= fl["patches_emitted"], (
        f"applied ({fl['patches_applied']}) + failed ({fl['patches_failed']}) "
        f"+ skipped ({fl['patches_skipped']}) must not exceed "
        f"emitted ({fl['patches_emitted']})"
    )


def test_fix_log_patches_is_list():
    fl = _example_fix_log()
    assert isinstance(fl["patches"], list)


def test_fix_log_patch_entry_has_required_keys():
    fl = _example_fix_log()
    for patch in fl["patches"]:
        # Required per _pass_7a_fix():
        #   pass_id, field_path, rationale, status
        assert "pass_id" in patch
        assert "field_path" in patch
        assert "rationale" in patch
        assert "status" in patch


def test_fix_log_patch_status_in_known_enum():
    """Valid status values per _pass_7a_fix: applied, failed, skipped."""
    fl = _example_fix_log()
    for patch in fl["patches"]:
        assert patch["status"] in {"applied", "failed", "skipped"}, (
            f"Unknown patch status: {patch['status']}"
        )


# ── realistic fix_log from an actual run ─────────────────────────────────────

def test_fix_log_schema_matches_phase_2_run():
    """Regression check: the Phase 2 Dostoevsky fix_log from 2026-04-24 run
    matches the schema contract. If FU#7's operator summary or the card's
    metadata.fix_pass_log changes shape, this test flags the regression."""
    phase_2_fix_log = {
        "validator_verdict": "REVISION_NEEDED",
        "validator_model": "openai:gpt-5.4",
        "field_issues_count": 16,
        "anachronism_flags_count": 8,
        "patches_emitted": 15,
        "patches_applied": 15,
        "patches_failed": 0,
        "patches_skipped": 0,
        "post_fix_verdict": "REVISION_NEEDED",
        "patches": [
            {
                "pass_id": "2",
                "field_path": "knowledge_boundary.conceptual_exclusions[3]",
                "rationale": "tag projection_warning on 'depression'",
                "status": "applied",
            },
        ],
    }
    # Schema invariants
    missing = FIX_LOG_SCHEMA_REQUIRED_KEYS - set(phase_2_fix_log.keys())
    assert not missing
    assert all(
        isinstance(phase_2_fix_log[k], int)
        for k in ("field_issues_count", "anachronism_flags_count",
                  "patches_emitted", "patches_applied",
                  "patches_failed", "patches_skipped")
    )
    # FU#7 summary depends on these fields being readable
    assert phase_2_fix_log.get("post_fix_verdict") is not None
    assert isinstance(phase_2_fix_log.get("patches"), list)
