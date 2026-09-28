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

from flows.shared.io import (  # noqa: E402
    member_slug,
    voice_display_name,
    write_json_atomic,
)
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


def _step2_output_with_corrupted_council_member(
    voice_slug: str, theme_id: str = "theme_001"
) -> dict:
    """C53 regression fixture: `council_member` shaped like the REAL
    production field — the voice card's long identity-prefix opening
    line — not the clean short name the pre-fix tests used. Clean
    fixtures are exactly why the corruption bug slipped through."""
    out = _step2_output(voice_slug, theme_id)
    out["council_member"] = (
        "I am Augusta Ada King, Countess of Lovelace, daughter of the "
        "poet and the mathematician, and I set down here what I have "
        "found in the Analytical Engine."
    )
    return out


def _step3_output_with_corrupted_council_member(
    voice_slug: str, theme_id: str = "theme_001"
) -> dict:
    out = _step3_output(voice_slug, theme_id)
    out["council_member"] = (
        "I am Augusta Ada King, Countess of Lovelace, daughter of the "
        "poet and the mathematician, and I set down here what I have "
        "found in the Analytical Engine."
    )
    return out


_CORRUPTED_ADA_IDENTITY = (
    "I am Augusta Ada King, Countess of Lovelace, daughter of the "
    "poet and the mathematician, and I set down here what I have "
    "found in the Analytical Engine."
)


def _step3_output_with_corrupted_nested_names(
    voice_slug: str, theme_id: str = "theme_001"
) -> dict:
    """C53 residual fixture: the NESTED `voices_read[].council_member`
    and `amendments[].cited_voice` fields carry the long card
    identity-prefix opening line — the same corruption already fixed at
    the top-level `voice_name` in e01eb84, but this time on the OTHER
    voice's fields (the ones a voice cites/reads at Step 3). The
    existing `_step3_output` fixture uses a short "Other Voice" name for
    these fields, which is exactly why the nested corruption slipped
    through — it never looked like the real production shape.

    Second amendment has NO `cited_voice_slug` at all: `run_step3_for_
    voice`'s resolver only `setdefault`s that field on a successful
    lookup match against the model's free-text `cited_voice`; when the
    model cites something unresolvable, the slug key is genuinely
    absent (not empty) on the real artifact.
    """
    out = _step3_output(voice_slug, theme_id)
    out["lineage"]["voices_read"] = [
        {
            "voice_slug": "ada_lovelace",
            "council_member": _CORRUPTED_ADA_IDENTITY,
            "shared_themes": [theme_id],
        },
    ]
    out["amendments"] = [
        {
            "cited_voice": _CORRUPTED_ADA_IDENTITY,
            "cited_voice_slug": "ada_lovelace",
            "cited_passage": "passage cited",
            "amendment_type": "agreement",
            "rationale": "I concur",
            "cited_theme_id": theme_id,
        },
        {
            # Unresolved citation — no cited_voice_slug key at all.
            "cited_voice": "an unnamed interlocutor",
            "cited_passage": "passage cited 2",
            "amendment_type": "disagreement",
            "rationale": "I push back",
            "cited_theme_id": theme_id,
        },
    ]
    return out


def _write_council_config(project_root: Path, members: list[dict]) -> None:
    """Minimal council_config.json at <project_root>/council_config.json
    (project ROOT, not reference/ — matches the real athens-2026 layout
    and `flows.shared.io.load_council_name_by_slug`'s resolution)."""
    write_json_atomic(
        project_root / "council_config.json", {"members": members}
    )


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
        """C53: voice_name resolves from the voice's SLUG (via
        council_config, with a slug-derived fallback), never from the
        raw `council_member` field — that field carries the long card
        identity-prefix in production, not a clean name. No
        project_root supplied here, so this exercises the fallback:
        "Voice of " + title-cased slug (the 2026-05-02 "Voice of X"
        standardization — see voices/OPEN_ITEMS.md ~line 643), NOT
        `_step2_output`'s "Test Voice" council_member value.
        """
        out = _to_publish_per_voice_from_step2(_step2_output("plato"), night=1)
        assert out["voice_name"] == "Voice of Plato"


class TestVoiceNameResolutionC53:
    """C53 regression coverage on BOTH publish surfaces, using a
    realistic long-identity-prefix `council_member` (the actual shape
    production artifacts carry) rather than the clean short names the
    other fixtures above use — clean fixtures are exactly why this bug
    shipped. Covers both the council_config-present (real lookup
    exercised) and council_config-absent (fallback) paths.

    Per the 2026-05-02 "Voice of X" standardization, council_config's
    `name` field is used VERBATIM as the per-voice-page `voice_name` —
    including the article for members that take one ("Voice of the
    Octopus", "Voice of the Whanganui River"). It is NOT stripped down
    to a bare name.
    """

    def test_step2_surface_resolves_via_council_config(self, tmp_path):
        project_root = tmp_path / "project"
        _write_council_config(
            project_root, [{"name": "Voice of Ada Lovelace"}]
        )
        out = _to_publish_per_voice_from_step2(
            _step2_output_with_corrupted_council_member("ada_lovelace"),
            night=1,
            project_root=project_root,
        )
        assert out["voice_name"] == "Voice of Ada Lovelace"
        assert "Countess of Lovelace" not in out["voice_name"]
        assert "Analytical Engine" not in out["voice_name"]

    def test_step3_surface_resolves_via_council_config(self, tmp_path):
        project_root = tmp_path / "project"
        _write_council_config(
            project_root, [{"name": "Voice of Ada Lovelace"}]
        )
        out = _to_publish_per_voice(
            _step3_output_with_corrupted_council_member("ada_lovelace"),
            night=1,
            project_root=project_root,
        )
        assert out["voice_name"] == "Voice of Ada Lovelace"
        assert "Countess of Lovelace" not in out["voice_name"]

    def test_step2_surface_resolves_article_bearing_name(self, tmp_path):
        """Regression for the article-drop bug: council_config members
        whose name takes 'the' ("Voice of the Octopus") must keep the
        article verbatim, not get stripped down and re-composed without
        it."""
        project_root = tmp_path / "project"
        _write_council_config(
            project_root, [{"name": "Voice of the Octopus"}]
        )
        out = _to_publish_per_voice_from_step2(
            _step2_output("octopus"), night=1, project_root=project_root,
        )
        assert out["voice_name"] == "Voice of the Octopus"

    def test_step2_surface_falls_back_when_council_config_missing(self, tmp_path):
        """No council_config.json at all under project_root — degrade
        gracefully to the "Voice of X" convention derived from the
        slug, never crash, never leak the corrupted council_member."""
        project_root = tmp_path / "project"  # does not exist on disk
        out = _to_publish_per_voice_from_step2(
            _step2_output_with_corrupted_council_member("ada_lovelace"),
            night=1,
            project_root=project_root,
        )
        assert out["voice_name"] == "Voice of Ada Lovelace"

    def test_step3_surface_falls_back_when_council_config_lacks_slug(self, tmp_path):
        """council_config.json exists but has no entry for this voice's
        slug — falls back rather than crashing or using council_member."""
        project_root = tmp_path / "project"
        _write_council_config(project_root, [{"name": "Voice of Plato"}])
        out = _to_publish_per_voice(
            _step3_output_with_corrupted_council_member("ada_lovelace"),
            night=1,
            project_root=project_root,
        )
        assert out["voice_name"] == "Voice of Ada Lovelace"

    def test_end_to_end_publish_resolves_clean_name_on_disk(self, tmp_path):
        """Full orchestrator path: council_config.json at the project
        ROOT (not reference/) is picked up and the published per-voice
        file on disk carries the clean "Voice of X" name verbatim, not
        the identity-prefix council_member."""
        run_dir = _seed_run_dir(tmp_path, step2_voices=["ibn_battuta"])
        # Overwrite with the corrupted-council_member fixture.
        write_json_atomic(
            run_dir / "04_voice" / "step2_first_draft_artifacts" / "ibn_battuta.json",
            _step2_output_with_corrupted_council_member("ibn_battuta"),
        )
        project_root = tmp_path / "project"
        _write_council_config(
            project_root, [{"name": "Voice of Ibn Battuta"}]
        )
        publish_voice_artifacts_for_night(
            run_dir=run_dir, night=1, project_root=project_root,
        )
        published = json.loads(
            (project_root / "published_artifacts" / "nights" / "night_1" / "ibn_battuta.json").read_text()
        )
        assert published["voice_name"] == "Voice of Ibn Battuta"


class TestNestedVoiceNameResolutionC53:
    """C53 residual: `deliberation.voices_read[].voice_name` and
    `deliberation.amendments[].cited_voice_name` carried the SAME
    council_member / cited_voice corruption as the top-level
    `voice_name` (fixed in e01eb84) — the Step-3 path is dormant
    (Step 3 was skipped at Athens) but must not corrupt names if it
    ever runs. Locks in resolution via `voice_display_name` off the
    slug fields already present on these nested entries.
    """

    def test_voices_read_voice_name_resolves_via_council_config(self, tmp_path):
        project_root = tmp_path / "project"
        _write_council_config(
            project_root, [{"name": "Voice of Ada Lovelace"}]
        )
        out = _to_publish_per_voice(
            _step3_output_with_corrupted_nested_names("plato"),
            night=1,
            project_root=project_root,
        )
        read = out["deliberation"]["voices_read"][0]
        assert read["voice_name"] == "Voice of Ada Lovelace"
        assert "Countess of Lovelace" not in read["voice_name"]
        assert "Analytical Engine" not in read["voice_name"]

    def test_voices_read_voice_name_falls_back_when_council_config_missing(self, tmp_path):
        """No council_config at all — degrade to the slug-derived
        "Voice of X" convention, never leak the corrupted council_member
        text onto the published surface."""
        project_root = tmp_path / "project"  # does not exist on disk
        out = _to_publish_per_voice(
            _step3_output_with_corrupted_nested_names("plato"),
            night=1,
            project_root=project_root,
        )
        read = out["deliberation"]["voices_read"][0]
        assert read["voice_name"] == "Voice of Ada Lovelace"
        assert "Countess of Lovelace" not in read["voice_name"]

    def test_amendment_cited_voice_name_resolves_via_council_config(self, tmp_path):
        project_root = tmp_path / "project"
        _write_council_config(
            project_root, [{"name": "Voice of Ada Lovelace"}]
        )
        out = _to_publish_per_voice(
            _step3_output_with_corrupted_nested_names("plato"),
            night=1,
            project_root=project_root,
        )
        amendment = out["deliberation"]["amendments"][0]
        assert amendment["cited_voice_name"] == "Voice of Ada Lovelace"
        assert "Countess of Lovelace" not in amendment["cited_voice_name"]

    def test_amendment_without_cited_voice_slug_falls_back_to_raw_citation(self, tmp_path):
        """When Step 3's own resolver couldn't match the model's
        free-text citation to a known voice, `cited_voice_slug` is
        genuinely absent (not just empty) — there's no slug to resolve
        against council_config, so `cited_voice_name` falls back to the
        model's raw `cited_voice` text rather than fabricating one."""
        project_root = tmp_path / "project"
        _write_council_config(
            project_root, [{"name": "Voice of Ada Lovelace"}]
        )
        out = _to_publish_per_voice(
            _step3_output_with_corrupted_nested_names("plato"),
            night=1,
            project_root=project_root,
        )
        amendment = out["deliberation"]["amendments"][1]
        assert amendment["cited_voice_slug"] == ""
        assert amendment["cited_voice_name"] == "an unnamed interlocutor"


class TestProductionCouncilNamesC53:
    """Sanity check against the REAL athens-2026 council_config.json
    `name` values (verified read-only against
    projects/athens-2026/council_config.json; only the ten `name`
    strings are reproduced here, not the file). The hand-picked
    fixtures used elsewhere in this file are short/simple; this locks
    in that `member_slug` / `voice_display_name` actually round-trip
    correctly against every production voice, INCLUDING the two whose
    name takes an article ("Voice of the Whanganui River", "Voice of
    the Octopus") — if `member_slug`'s key derivation ever stops
    matching one of these, this fails loudly instead of silently
    mis-resolving that voice's display name in production.
    """

    PRODUCTION_NAME_TO_SLUG = {
        "Voice of Plato": "plato",
        "Voice of Cleopatra": "cleopatra",
        "Voice of Ibn Battuta": "ibn_battuta",
        "Voice of Scheherazade": "scheherazade",
        "Voice of Ada Lovelace": "ada_lovelace",
        "Voice of Fyodor Dostoevsky": "fyodor_dostoevsky",
        "Voice of Hannah Arendt": "hannah_arendt",
        "Voice of Bob Marley": "bob_marley",
        "Voice of the Whanganui River": "whanganui_river",
        "Voice of the Octopus": "octopus",
    }

    def test_member_slug_matches_real_voice_folder_slugs(self):
        for name, expected_slug in self.PRODUCTION_NAME_TO_SLUG.items():
            actual = member_slug(name)
            assert actual == expected_slug, (
                f"member_slug({name!r}) == {actual!r}, expected "
                f"{expected_slug!r} — this would silently break "
                f"voice_display_name's lookup for this voice."
            )

    def test_voice_display_name_resolves_every_production_voice_verbatim(self, tmp_path):
        project_root = tmp_path / "project"
        _write_council_config(
            project_root,
            [{"name": name} for name in self.PRODUCTION_NAME_TO_SLUG],
        )
        for name, slug in self.PRODUCTION_NAME_TO_SLUG.items():
            assert voice_display_name(slug, project_root) == name


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

    def test_held_voice_dropped_from_index_but_page_file_stays(self, tmp_path):
        """C67 #4 report scenario: voice_flow publishes all voices right
        after Step 2 (before the operator gate), the operator then holds
        one, and a full republish must drop it from `_index.json` again —
        `_rebuild_index_from_disk` (C50) was reading every <slug>.json on
        disk, including a held voice's file from the earlier pre-hold
        publish, undoing what `main` did for free. The page file itself is
        not deleted (index ['octopus', 'plato'] -> ['plato'] after hold)."""
        run_dir = _seed_run_dir(tmp_path, step2_voices=["octopus", "plato"])
        project_root = tmp_path / "project"
        night_dir = project_root / "published_artifacts" / "nights" / "night_1"

        publish_voice_artifacts_for_night(
            run_dir=run_dir, night=1, project_root=project_root
        )
        index = json.loads((night_dir / "_index.json").read_text())
        assert index["voice_count"] == 2
        assert {v["voice_slug"] for v in index["voices"]} == {"octopus", "plato"}

        dec_dir = run_dir / "04_voice" / "operator_decisions"
        dec_dir.mkdir(parents=True)
        write_json_atomic(
            dec_dir / "octopus.json",
            {"voice_slug": "octopus", "decision": "hold_for_regen"},
        )

        result = publish_voice_artifacts_for_night(
            run_dir=run_dir, night=1, project_root=project_root
        )
        assert result["voices_published"] == ["plato"]
        index_after_hold = json.loads((night_dir / "_index.json").read_text())
        assert index_after_hold["voice_count"] == 1
        assert [v["voice_slug"] for v in index_after_hold["voices"]] == ["plato"]
        # Not deleted — only excluded from the index.
        assert (night_dir / "octopus.json").exists()


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


class TestIndexRebuildFromDisk:
    """C50: `_index.json` must always reflect every voice actually on
    disk for the night, not just the voices touched by the most recent
    publish call. Reproduces the Athens Night 3 incident — sequential
    single-voice publish reruns left the index showing only the last
    voice, even though 10 per-voice files were on disk."""

    def test_sequential_single_voice_publishes_index_lists_both(self, tmp_path):
        run_dir = _seed_run_dir(
            tmp_path, step2_voices=["plato", "cleopatra"]
        )
        project_root = tmp_path / "project"
        night_dir = project_root / "published_artifacts" / "nights" / "night_1"

        result1 = publish_voice_artifacts_for_night(
            run_dir=run_dir, night=1, project_root=project_root,
            voice_slugs=["plato"],
        )
        index_after_first = json.loads((night_dir / "_index.json").read_text())
        assert index_after_first["voice_count"] == 1
        assert result1["voices_published"] == ["plato"]

        result2 = publish_voice_artifacts_for_night(
            run_dir=run_dir, night=1, project_root=project_root,
            voice_slugs=["cleopatra"],
        )
        assert result2["voices_published"] == ["cleopatra"]

        index_after_second = json.loads((night_dir / "_index.json").read_text())
        assert index_after_second["voice_count"] == 2
        slugs = {v["voice_slug"] for v in index_after_second["voices"]}
        assert slugs == {"plato", "cleopatra"}
        # Both per-voice files remain on disk.
        assert (night_dir / "plato.json").exists()
        assert (night_dir / "cleopatra.json").exists()

    def test_index_schema_unchanged_after_rebuild(self, tmp_path):
        """Rebuilt index keeps the same per-voice entry schema as before
        (title/subtitle/selected_form/stance/themes_addressed/decision/
        amendment_count/word_count/was_step3/voice_name/url_path)."""
        run_dir = _seed_run_dir(tmp_path, step2_voices=["plato"])
        project_root = tmp_path / "project"
        publish_voice_artifacts_for_night(
            run_dir=run_dir, night=1, project_root=project_root,
        )
        index = json.loads(
            (project_root / "published_artifacts" / "nights" / "night_1" / "_index.json").read_text()
        )
        entry = index["voices"][0]
        assert set(entry.keys()) == {
            "voice_slug", "voice_name", "url_path", "title", "subtitle",
            "selected_form", "stance", "themes_addressed", "decision",
            "amendment_count", "word_count", "was_step3",
        }
        assert set(index.keys()) == {
            "night", "url_path", "generated_at", "voices", "voice_count",
        }
