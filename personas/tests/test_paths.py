"""Tests for flows/shared/paths.py — per-voice path accessors."""
import sys
from pathlib import Path
import pytest

# Add personas/ to sys.path so imports work when run from repo root.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from flows.shared import paths


FAKE_ROOT = Path("/tmp/fake_project")
SLUG = "test_voice"


class TestVoiceRootAndSubdirs:
    def test_voice_root_under_project(self):
        p = paths.voice_root(SLUG, FAKE_ROOT)
        assert p == FAKE_ROOT / "voices" / SLUG

    def test_intake_dir(self):
        p = paths.intake_dir(SLUG, FAKE_ROOT)
        assert p == FAKE_ROOT / "voices" / SLUG / "00_intake"

    def test_research_dir(self):
        p = paths.research_dir(SLUG, FAKE_ROOT)
        assert p == FAKE_ROOT / "voices" / SLUG / "01_research"

    def test_merge_dir(self):
        p = paths.merge_dir(SLUG, FAKE_ROOT)
        assert p == FAKE_ROOT / "voices" / SLUG / "02_merge"

    def test_corpus_dir(self):
        p = paths.corpus_dir(SLUG, FAKE_ROOT)
        assert p == FAKE_ROOT / "voices" / SLUG / "03_corpus"

    def test_generation_dir(self):
        p = paths.generation_dir(SLUG, FAKE_ROOT)
        assert p == FAKE_ROOT / "voices" / SLUG / "04_generation"

    def test_validation_dir(self):
        p = paths.validation_dir(SLUG, FAKE_ROOT)
        assert p == FAKE_ROOT / "voices" / SLUG / "05_validation"

    def test_derive_dir(self):
        p = paths.derive_dir(SLUG, FAKE_ROOT)
        assert p == FAKE_ROOT / "voices" / SLUG / "06_derive"


class TestIntakeFiles:
    def test_voice_config(self):
        p = paths.voice_config(SLUG, FAKE_ROOT)
        assert p.name == "02_voice_config.json"
        assert p.parent == paths.intake_dir(SLUG, FAKE_ROOT)

    def test_review_doc(self):
        p = paths.review_doc(SLUG, FAKE_ROOT)
        assert p.name == "03_review_doc.md"

    def test_non_human_grounding(self):
        p = paths.non_human_grounding(SLUG, FAKE_ROOT)
        assert p.name == "01_non_human_grounding.md"


class TestResearchFiles:
    def test_perplexity_dossier(self):
        p = paths.perplexity_dossier(SLUG, FAKE_ROOT)
        assert p.name == "01_perplexity_dossier.json"
        assert p.parent == paths.research_dir(SLUG, FAKE_ROOT)

    def test_gemini_broad_scan(self):
        p = paths.gemini_broad_scan(SLUG, FAKE_ROOT)
        assert p.name == "02_gemini_broad_scan.json"

    def test_dr_prompts_dir(self):
        p = paths.dr_prompts_dir(SLUG, FAKE_ROOT)
        assert p.name == "03_dr_prompts"
        assert p.parent == paths.research_dir(SLUG, FAKE_ROOT)

    def test_monolithic_dr_prompt(self):
        p = paths.monolithic_dr_prompt(SLUG, FAKE_ROOT)
        assert p.name == "01_monolithic_dr_prompt.md"
        assert p.parent == paths.dr_prompts_dir(SLUG, FAKE_ROOT)

    def test_tailoring_notes(self):
        p = paths.tailoring_notes(SLUG, FAKE_ROOT)
        assert p.name == "02_tailoring_notes.json"

    def test_section_dr_prompt_numbering(self):
        # §1 → prefix 3 → 03_section_1_dr_prompt.md
        assert paths.section_dr_prompt(SLUG, 1, FAKE_ROOT).name == "03_section_1_dr_prompt.md"
        # §2 → prefix 4 → 04_section_2_dr_prompt.md
        assert paths.section_dr_prompt(SLUG, 2, FAKE_ROOT).name == "04_section_2_dr_prompt.md"
        # §3 → 05_section_3_dr_prompt.md
        assert paths.section_dr_prompt(SLUG, 3, FAKE_ROOT).name == "05_section_3_dr_prompt.md"
        # §6 → prefix 8 → 08_section_6_dr_prompt.md
        assert paths.section_dr_prompt(SLUG, 6, FAKE_ROOT).name == "08_section_6_dr_prompt.md"

    def test_section_dr_prompt_invalid_index(self):
        with pytest.raises(AssertionError):
            paths.section_dr_prompt(SLUG, 0, FAKE_ROOT)
        with pytest.raises(AssertionError):
            paths.section_dr_prompt(SLUG, 7, FAKE_ROOT)

    def test_dr_dossier_dir(self):
        p = paths.dr_dossier_dir(SLUG, FAKE_ROOT)
        assert p.name == "04_dr_dossier"
        assert p.parent == paths.research_dir(SLUG, FAKE_ROOT)

    def test_section_dr_dossier_numbering(self):
        assert paths.section_dr_dossier(SLUG, 1, FAKE_ROOT).name == "01_section_1.md"
        assert paths.section_dr_dossier(SLUG, 6, FAKE_ROOT).name == "06_section_6.md"

    def test_concat_claude_dr(self):
        p = paths.concat_claude_dr(SLUG, FAKE_ROOT)
        assert p.name == "07_concat_claude_dr.md"
        assert p.parent == paths.dr_dossier_dir(SLUG, FAKE_ROOT)


class TestCorpusFiles:
    def test_primary_text_urls(self):
        """CC#1 2026-04-26: relocated from research_dir to corpus_dir."""
        p = paths.primary_text_urls(SLUG, FAKE_ROOT)
        assert p.name == "00_primary_text_urls.json"
        assert p.parent == paths.corpus_dir(SLUG, FAKE_ROOT)

    def test_primary_texts(self):
        p = paths.primary_texts(SLUG, FAKE_ROOT)
        assert p.name == "01_primary_texts.json"
        assert p.parent == paths.corpus_dir(SLUG, FAKE_ROOT)

    def test_excerpt_selections(self):
        p = paths.excerpt_selections(SLUG, FAKE_ROOT)
        assert p.name == "02_excerpt_selections.json"

    def test_primary_texts_reviewed_flag(self):
        p = paths.primary_texts_reviewed_flag(SLUG, FAKE_ROOT)
        assert p.name == "03_primary_texts_reviewed.flag"
        assert p.parent == paths.corpus_dir(SLUG, FAKE_ROOT)

    def test_primary_texts_review(self):
        p = paths.primary_texts_review(SLUG, FAKE_ROOT)
        assert p.name == "04_primary_texts_review.md"
        assert p.parent == paths.corpus_dir(SLUG, FAKE_ROOT)


class TestMergeFiles:
    def test_merge_chunk_biographical(self):
        p = paths.merge_chunk(SLUG, 1, FAKE_ROOT)
        assert p.name == "01_pass_1_1_biographical.json"
        assert p.parent == paths.merge_dir(SLUG, FAKE_ROOT)

    def test_merge_chunk_corpus(self):
        p = paths.merge_chunk(SLUG, 6, FAKE_ROOT)
        assert p.name == "06_pass_1_6_corpus.json"

    def test_merge_coherence(self):
        p = paths.merge_coherence(SLUG, FAKE_ROOT)
        assert p.name == "07_pass_1_7_coherence.json"

    def test_merged_dossier(self):
        p = paths.merged_dossier(SLUG, FAKE_ROOT)
        assert p.name == "08_merged_dossier.json"
        assert p.parent == paths.merge_dir(SLUG, FAKE_ROOT)


class TestGenerationFiles:
    def test_pass_2(self):
        p = paths.pass_2(SLUG, FAKE_ROOT)
        assert p.name == "01_pass_2_identity_boundaries.json"
        assert p.parent == paths.generation_dir(SLUG, FAKE_ROOT)

    def test_pass_6(self):
        p = paths.pass_6(SLUG, FAKE_ROOT)
        assert p.name == "10_pass_6_corpus.json"


class TestValidationFiles:
    def test_pass_7_pre(self):
        p = paths.pass_7_pre(SLUG, FAKE_ROOT)
        assert p.name == "01_pass_7_pre_citation.json"
        assert p.parent == paths.validation_dir(SLUG, FAKE_ROOT)

    def test_pass_7c(self):
        p = paths.pass_7c(SLUG, FAKE_ROOT)
        assert p.name == "05_pass_7c_negative.json"


class TestDeriveFiles:
    def test_derive_raw(self):
        p = paths.derive_raw(SLUG, FAKE_ROOT)
        assert p.name == "00_derive_raw.json"
        assert p.parent == paths.derive_dir(SLUG, FAKE_ROOT)

    def test_provocateur_profile(self):
        p = paths.provocateur_profile(SLUG, FAKE_ROOT)
        assert p.name == "01_provocateur_profile.json"
        assert p.parent == paths.derive_dir(SLUG, FAKE_ROOT)

    def test_evaluation_rubric(self):
        p = paths.evaluation_rubric(SLUG, FAKE_ROOT)
        assert p.name == "02_evaluation_rubric.json"


class TestVoiceRootFiles:
    def test_assembled_card(self):
        p = paths.assembled_card(SLUG, FAKE_ROOT)
        assert p.name == "07_persona_card_assembled.json"
        assert p.parent == paths.voice_root(SLUG, FAKE_ROOT)

    def test_manifest(self):
        p = paths.manifest(SLUG, FAKE_ROOT)
        assert p.name == "_manifest.json"
        assert p.parent == paths.voice_root(SLUG, FAKE_ROOT)


class TestProjectLevelFiles:
    def test_conference_facts(self):
        p = paths.conference_facts(FAKE_ROOT)
        assert p == FAKE_ROOT / "conference_facts.json"

    def test_audience_profile(self):
        p = paths.audience_profile(FAKE_ROOT)
        assert p == FAKE_ROOT / "audience_profile.json"

    def test_panel_roster(self):
        p = paths.panel_roster(FAKE_ROOT)
        assert p == FAKE_ROOT / "panel_roster.json"


class TestEnsureVoiceDirs:
    def test_creates_all_subdirs(self, tmp_path):
        paths.ensure_voice_dirs(SLUG, tmp_path)
        expected = [
            tmp_path / "voices" / SLUG / "00_intake",
            tmp_path / "voices" / SLUG / "01_research",
            tmp_path / "voices" / SLUG / "02_merge",
            tmp_path / "voices" / SLUG / "03_corpus",
            tmp_path / "voices" / SLUG / "04_generation",
            tmp_path / "voices" / SLUG / "05_validation",
            tmp_path / "voices" / SLUG / "06_derive",
            tmp_path / "voices" / SLUG / "01_research" / "03_dr_prompts",
            tmp_path / "voices" / SLUG / "01_research" / "04_dr_dossier",
        ]
        for d in expected:
            assert d.is_dir(), f"Expected directory not created: {d}"

    def test_idempotent(self, tmp_path):
        paths.ensure_voice_dirs(SLUG, tmp_path)
        paths.ensure_voice_dirs(SLUG, tmp_path)  # second call should not error
        assert (tmp_path / "voices" / SLUG / "00_intake").is_dir()

    def test_all_subdirs_under_voice_root(self, tmp_path):
        paths.ensure_voice_dirs(SLUG, tmp_path)
        voice = tmp_path / "voices" / SLUG
        for name in ["00_intake", "01_research", "02_merge", "03_corpus",
                     "04_generation", "05_validation", "06_derive"]:
            assert (voice / name).is_dir()
