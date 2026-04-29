"""Canonical paths for the persona pipeline.

Every path reference goes through a function in this module. Runners call
paths.voice_config(slug) — not string concatenation. Changes to layout
conventions live here alone.

See _workspace/planning/SONNET_EXECUTION_PHASE_B_RESTRUCTURE.md for the
full layout spec.
"""

from __future__ import annotations
from pathlib import Path
from .project_root import get_project_root


# ==== Voice root + subfolder roots ====

def voice_root(slug: str, project_root: Path | None = None) -> Path:
    """$PROJECT_ROOT/voices/<slug>/"""
    return _resolve(project_root) / "voices" / slug


def intake_dir(slug: str, project_root: Path | None = None) -> Path:
    """voices/<slug>/00_intake/"""
    return voice_root(slug, project_root) / "00_intake"


def research_dir(slug: str, project_root: Path | None = None) -> Path:
    """voices/<slug>/01_research/"""
    return voice_root(slug, project_root) / "01_research"


def merge_dir(slug: str, project_root: Path | None = None) -> Path:
    return voice_root(slug, project_root) / "02_merge"


def corpus_dir(slug: str, project_root: Path | None = None) -> Path:
    return voice_root(slug, project_root) / "03_corpus"


def generation_dir(slug: str, project_root: Path | None = None) -> Path:
    return voice_root(slug, project_root) / "04_generation"


def validation_dir(slug: str, project_root: Path | None = None) -> Path:
    return voice_root(slug, project_root) / "05_validation"


def derive_dir(slug: str, project_root: Path | None = None) -> Path:
    return voice_root(slug, project_root) / "06_derive"


# ==== Intake files ====

def non_human_grounding(slug: str, project_root: Path | None = None) -> Path:
    return intake_dir(slug, project_root) / "01_non_human_grounding.md"


def voice_config(slug: str, project_root: Path | None = None) -> Path:
    return intake_dir(slug, project_root) / "02_voice_config.json"


def review_doc(slug: str, project_root: Path | None = None) -> Path:
    return intake_dir(slug, project_root) / "03_review_doc.md"


# ==== Research files ====

def primary_text_urls(slug: str, project_root: Path | None = None) -> Path:
    """Synthetic cache entry written by Pass 1c-extract (URL list from dossier).

    CC#1 2026-04-26: relocated from `01_research/05_primary_text_urls.json` to
    `03_corpus/00_primary_text_urls.json`. Historical-layout vestige: in v3.10
    the URL list came directly from Perplexity research; 1-arch-07 (2026-04-22)
    changed the source — URLs are now derived post-merge from `02_merge/pass_1_6/
    works.json` + `passages.json`. The file is no longer a research output.
    Belongs in `03_corpus/` alongside the fetched primary texts.
    """
    return corpus_dir(slug, project_root) / "00_primary_text_urls.json"


def perplexity_dossier(slug: str, project_root: Path | None = None) -> Path:
    return research_dir(slug, project_root) / "01_perplexity_dossier.json"


def gemini_broad_scan(slug: str, project_root: Path | None = None) -> Path:
    return research_dir(slug, project_root) / "02_gemini_broad_scan.json"


def dr_prompts_dir(slug: str, project_root: Path | None = None) -> Path:
    return research_dir(slug, project_root) / "03_dr_prompts"


def monolithic_dr_prompt(slug: str, project_root: Path | None = None) -> Path:
    return dr_prompts_dir(slug, project_root) / "01_monolithic_dr_prompt.md"


def tailoring_notes(slug: str, project_root: Path | None = None) -> Path:
    return dr_prompts_dir(slug, project_root) / "02_tailoring_notes.json"


def section_dr_prompt(slug: str, n: int, project_root: Path | None = None) -> Path:
    assert 1 <= n <= 6, f"section_index must be 1-6, got {n}"
    # §1 → 03_section_1_dr_prompt.md, §2 → 04_..., ... §6 → 08_...
    prefix = n + 2  # 1→3, 2→4, ..., 6→8
    return dr_prompts_dir(slug, project_root) / f"{prefix:02d}_section_{n}_dr_prompt.md"


def dr_dossier_dir(slug: str, project_root: Path | None = None) -> Path:
    return research_dir(slug, project_root) / "04_dr_dossier"


def section_dr_dossier(slug: str, n: int, project_root: Path | None = None) -> Path:
    assert 1 <= n <= 6, f"section_index must be 1-6, got {n}"
    return dr_dossier_dir(slug, project_root) / f"{n:02d}_section_{n}.md"


def concat_claude_dr(slug: str, project_root: Path | None = None) -> Path:
    """Monolithic fallback — concatenation of 6 section files."""
    return dr_dossier_dir(slug, project_root) / "07_concat_claude_dr.md"


# ==== Merge files (Pass 1.1–1.7) ====

_MERGE_CHUNK_NAMES = {
    1: "biographical", 2: "intellectual", 3: "reasoning",
    4: "voice", 5: "boundaries", 6: "corpus",
}


def merge_chunk(slug: str, chunk_num: int, project_root: Path | None = None) -> Path:
    assert 1 <= chunk_num <= 6
    name = _MERGE_CHUNK_NAMES[chunk_num]
    return merge_dir(slug, project_root) / f"{chunk_num:02d}_pass_1_{chunk_num}_{name}.json"


def merge_coherence(slug: str, project_root: Path | None = None) -> Path:
    return merge_dir(slug, project_root) / "07_pass_1_7_coherence.json"


def merged_dossier(slug: str, project_root: Path | None = None) -> Path:
    return merge_dir(slug, project_root) / "08_merged_dossier.json"


# ==== Corpus files ====

def primary_texts(slug: str, project_root: Path | None = None) -> Path:
    return corpus_dir(slug, project_root) / "01_primary_texts.json"


def excerpt_selections(slug: str, project_root: Path | None = None) -> Path:
    return corpus_dir(slug, project_root) / "02_excerpt_selections.json"


def primary_texts_reviewed_flag(slug: str, project_root: Path | None = None) -> Path:
    return corpus_dir(slug, project_root) / "03_primary_texts_reviewed.flag"


def primary_texts_review(slug: str, project_root: Path | None = None) -> Path:
    return corpus_dir(slug, project_root) / "04_primary_texts_review.md"


# ==== Generation files (Pass 2–6 + CT) ====

def pass_2(slug: str, project_root: Path | None = None) -> Path:
    return generation_dir(slug, project_root) / "01_pass_2_identity_boundaries.json"


def ct_after_pass_2(slug: str, project_root: Path | None = None) -> Path:
    return generation_dir(slug, project_root) / "02_ct_after_pass_2.json"


def pass_3(slug: str, project_root: Path | None = None) -> Path:
    return generation_dir(slug, project_root) / "03_pass_3_intellectual_core.json"


def ct_after_pass_3(slug: str, project_root: Path | None = None) -> Path:
    return generation_dir(slug, project_root) / "04_ct_after_pass_3.json"


def pass_4a(slug: str, project_root: Path | None = None) -> Path:
    return generation_dir(slug, project_root) / "05_pass_4a_voice.json"


def ct_after_pass_4a(slug: str, project_root: Path | None = None) -> Path:
    return generation_dir(slug, project_root) / "06_ct_after_pass_4a.json"


def pass_4b(slug: str, project_root: Path | None = None) -> Path:
    return generation_dir(slug, project_root) / "07_pass_4b_artifact.json"


def ct_after_pass_4b(slug: str, project_root: Path | None = None) -> Path:
    return generation_dir(slug, project_root) / "08_ct_after_pass_4b.json"


def pass_5(slug: str, project_root: Path | None = None) -> Path:
    return generation_dir(slug, project_root) / "09_pass_5_engagement.json"


def pass_6(slug: str, project_root: Path | None = None) -> Path:
    return generation_dir(slug, project_root) / "10_pass_6_corpus.json"


# ==== Validation files (Pass 7.*) ====

def pass_7_pre(slug: str, project_root: Path | None = None) -> Path:
    return validation_dir(slug, project_root) / "01_pass_7_pre_citation.json"


def pass_7_anachronism(slug: str, project_root: Path | None = None) -> Path:
    return validation_dir(slug, project_root) / "02_pass_7_anachronism.json"


def pass_7a(slug: str, project_root: Path | None = None) -> Path:
    return validation_dir(slug, project_root) / "03_pass_7a_cross_model.json"


def pass_7b(slug: str, project_root: Path | None = None) -> Path:
    return validation_dir(slug, project_root) / "04_pass_7b_smoke_test.json"


def pass_7c(slug: str, project_root: Path | None = None) -> Path:
    return validation_dir(slug, project_root) / "05_pass_7c_negative.json"


def pass_7a_final(slug: str, project_root: Path | None = None) -> Path:
    """Pass 7a FINAL: cross-model validation against the fully assembled card
    (post-7b/7c). FU#53 review-gate refactor (2026-04-29). Catches cross-pass
    contradictions invisible to the per-pass 7a (e.g., banned_language
    rejecting Jowett while curated_corpus_passages uses Jowett)."""
    return validation_dir(slug, project_root) / "06_pass_7a_final.json"


def operator_review_flag(slug: str, project_root: Path | None = None) -> Path:
    """Operator-review-passed touch flag. Created by operator after manually
    reviewing Pass 7a FINAL residuals and either patching the assembled card
    or accepting them; absent → pipeline hard-stops at the gate."""
    return voice_root(slug, project_root) / "_operator_review_passed.flag"


# ==== Derive files ====

def derive_raw(slug: str, project_root: Path | None = None) -> Path:
    """Combined derive call output (cache); split into provocateur_profile + evaluation_rubric."""
    return derive_dir(slug, project_root) / "00_derive_raw.json"


def provocateur_profile(slug: str, project_root: Path | None = None) -> Path:
    return derive_dir(slug, project_root) / "01_provocateur_profile.json"


def evaluation_rubric(slug: str, project_root: Path | None = None) -> Path:
    return derive_dir(slug, project_root) / "02_evaluation_rubric.json"


# ==== Voice root files ====

def assembled_card(slug: str, project_root: Path | None = None) -> Path:
    return voice_root(slug, project_root) / "07_persona_card_assembled.json"


def manifest(slug: str, project_root: Path | None = None) -> Path:
    return voice_root(slug, project_root) / "_manifest.json"


# ==== Project-level files (NOT per-voice) ====

def conference_facts(project_root: Path | None = None) -> Path:
    return _resolve(project_root) / "conference_facts.json"


def audience_profile(project_root: Path | None = None) -> Path:
    return _resolve(project_root) / "audience_profile.json"


def panel_roster(project_root: Path | None = None) -> Path:
    return _resolve(project_root) / "panel_roster.json"


# ==== Helpers ====

def _resolve(project_root: Path | None) -> Path:
    if project_root is None:
        project_root = get_project_root()
    return Path(project_root)


def ensure_voice_dirs(slug: str, project_root: Path | None = None) -> None:
    """Create the 7 pass-group subfolders + dr_prompts/ + dr_dossier/."""
    for mk in [intake_dir, research_dir, merge_dir, corpus_dir,
               generation_dir, validation_dir, derive_dir]:
        mk(slug, project_root).mkdir(parents=True, exist_ok=True)
    dr_prompts_dir(slug, project_root).mkdir(parents=True, exist_ok=True)
    dr_dossier_dir(slug, project_root).mkdir(parents=True, exist_ok=True)
