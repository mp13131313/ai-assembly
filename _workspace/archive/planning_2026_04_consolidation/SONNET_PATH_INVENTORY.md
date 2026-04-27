# Phase B Restructure — Path Inventory

**Session:** 2026-04-21 Sonnet execution session
**Purpose:** Every hardcoded path reference in `personas/` that Phase B's `paths.py` must replace.

---

## OLD PATHS → NEW PATHS mapping

### Voice config / intake

| File:Line | Old pattern | New `paths.*` function |
|---|---|---|
| `io.py:87` | `project_root / "inputs" / "voices"` | `paths.intake_dir(slug)` |
| `io.py:89-92` | `voices_dir / f"{slug}.json"` | `paths.voice_config(slug)` |
| `run_pass0a_voice_config.py:189` | `project_root / "inputs/voices"` | `paths.intake_dir(slug)` |
| `run_pass0a_voice_config.py:85` | `project_root / "inputs/non_human_grounding"` | (use `paths.non_human_grounding(slug).parent`) |
| `run_pass0a_voice_config.py:71,181` | `project_root / "inputs/conference_facts.json"` | `paths.conference_facts()` |
| `run_pass0a_voice_config.py:72,182` | `project_root / "inputs/panel_roster.json"` | `paths.panel_roster()` |
| `run_pass_0b_tailor.py:55` | `project_root / "inputs" / "voices" / f"{slug}.json"` | `paths.voice_config(slug)` |

### Research outputs (Perplexity + Gemini)

| File:Line | Old pattern | New `paths.*` function |
|---|---|---|
| `run_phase0_1_research.py:153` | `RUN / "01_research/perplexity_dossier.json"` | `paths.perplexity_dossier(slug)` |
| `run_phase0_1_research.py:154` | `RUN / "01_research/gemini_broad_scan.json"` | `paths.gemini_broad_scan(slug)` |
| `run_pass_0b_tailor.py:56` | `project_root / "runs" / slug / "01_research" / "perplexity_dossier.json"` | `paths.perplexity_dossier(slug)` |
| `run_pass_0b_tailor.py:57` | `project_root / "runs" / slug / "01_research" / "gemini_broad_scan.json"` | `paths.gemini_broad_scan(slug)` |
| `run_persona_pipeline.py:108` | `RUN / "01_research/perplexity_dossier.json"` | `paths.perplexity_dossier(slug)` |
| `run_persona_pipeline.py:109` | `RUN / "01_research/gemini_broad_scan.json"` | `paths.gemini_broad_scan(slug)` |
| `chunk_runner.py:60` | `fixtures / "perplexity_dossier.json"` | (fixtures path — keep as repo_root-based) |
| `chunk_runner.py:70` | `project_root / "runs" / slug / "01_research"` | `paths.research_dir(slug)` |

### DR prompts (Phase 0.5 outputs)

| File:Line | Old pattern | New `paths.*` function |
|---|---|---|
| `run_phase0_1_research.py:100` | `project_root / "inputs/dossiers/_dr_prompts"` | `paths.dr_prompts_dir(slug)` |
| `run_phase0_1_research.py:251` | `DR_PROMPTS_DIR / f"{slug}_dr_prompt.md"` | `paths.monolithic_dr_prompt(slug)` |
| `run_pass_0b_tailor.py:58` | `project_root / "inputs/dossiers/_dr_prompts" / f"{slug}_dr_prompt.md"` | `paths.monolithic_dr_prompt(slug)` |
| `run_pass_0b_tailor.py:59` | `project_root / "inputs/dossiers/_dr_prompts" / f"{slug}_dr_prompt.base.md"` | (no canonical fn — inline in tailor script) |
| `run_pass_0b_tailor.py:61` | `project_root / "inputs/dossiers/_dr_prompts" / f"{slug}_tailoring_notes.json"` | `paths.tailoring_notes(slug)` |

### DR dossier (manually saved claude.ai outputs)

| File:Line | Old pattern | New `paths.*` function |
|---|---|---|
| `run_phase0_1_research.py:282` | `project_root / f"inputs/dossiers/{slug}_claude_dr.md"` | `paths.concat_claude_dr(slug)` (monolithic fallback) |
| `run_persona_pipeline.py:132` | `PROJECT_ROOT / f"inputs/dossiers/{SLUG}_claude_dr.md"` | `paths.concat_claude_dr(slug)` |
| `chunk_runner.py:73` | `research / "claude_dr_dossier.md"` | `paths.concat_claude_dr(slug)` |

### Merge outputs (Pass 1.1-1.7)

| File:Line | Old pattern | New `paths.*` function |
|---|---|---|
| `run_pass_1_7.py:39` | `project_root / "runs" / slug / "01_research"` | `paths.merge_dir(slug)` |
| `run_pass_1_7.py:127` | `project_root / "runs" / slug / "01_research" / "merged_dossier.json"` | `paths.merged_dossier(slug)` |
| `run_persona_pipeline.py:158` | `RUN / "01_research/merged_dossier.json"` | `paths.merged_dossier(slug)` |
| `chunk_runner.py:217` | `project_root / "runs" / slug / "01_research" / output_subdir` | (per-chunk; maps to `paths.merge_chunk(slug, n)`) |

### Corpus (Pass 1c, 1d)

| File:Line | Old pattern | New `paths.*` function |
|---|---|---|
| `run_persona_pipeline.py:228` | `RUN / "01_research/primary_texts.json"` | `paths.primary_texts(slug)` |
| `run_persona_pipeline.py:420` | `RUN / "01_research/excerpt_selections.json"` | `paths.excerpt_selections(slug)` |

### Generation passes (2-6 + CT)

| File:Line | Old pattern | New `paths.*` function |
|---|---|---|
| `run_persona_pipeline.py:373` | `RUN / "02_passes/pass2_identity_boundaries.json"` | `paths.pass_2(slug)` |
| `run_persona_pipeline.py:389` | `RUN / "02_passes/pass3_intellectual_core.json"` | `paths.pass_3(slug)` |
| `run_persona_pipeline.py:440` | `RUN / "02_passes/pass4a_voice.json"` | `paths.pass_4a(slug)` |
| `run_persona_pipeline.py:459` | `RUN / "02_passes/pass4b_artifact.json"` | `paths.pass_4b(slug)` |
| `run_persona_pipeline.py:480` | `RUN / "02_passes/pass5_engagement.json"` | `paths.pass_5(slug)` |
| `run_persona_pipeline.py:512` | `RUN / "02_passes/pass6_corpus.json"` | `paths.pass_6(slug)` |
| `run_persona_pipeline.py:347-360` | `RUN / "02_passes/_ct_*.json"` | (CT paths: `paths.ct_after_pass_2(slug)` etc.) |

### Validation passes (7.*)

| File:Line | Old pattern | New `paths.*` function |
|---|---|---|
| `run_persona_pipeline.py:537` | `RUN / "02_passes/pass7pre_citation.json"` | `paths.pass_7_pre(slug)` |
| `run_persona_pipeline.py:600` | `RUN / "02_passes/pass7_anachronism.json"` | `paths.pass_7_anachronism(slug)` |
| `run_persona_pipeline.py:646` | `RUN / "02_passes/pass7a_cross_model.json"` | `paths.pass_7a(slug)` |
| `run_persona_pipeline.py:857` | `RUN / "02_passes/pass7b_smoke_test.json"` | `paths.pass_7b(slug)` |
| `run_persona_pipeline.py:897` | `RUN / "02_passes/pass7c_negative.json"` | `paths.pass_7c(slug)` |

### Derive + assembled card

| File:Line | Old pattern | New `paths.*` function |
|---|---|---|
| `run_persona_pipeline.py:930` | `RUN / "02_passes/derive.json"` | (interim; maps to derive outputs) |
| `run_persona_pipeline.py:940` | `RUN / "provocateur_profile.json"` | `paths.provocateur_profile(slug)` |
| `run_persona_pipeline.py:941` | `RUN / "evaluation_rubric.json"` | `paths.evaluation_rubric(slug)` |
| `run_persona_pipeline.py:1065` | `RUN / "persona_card_assembled.json"` | `paths.assembled_card(slug)` |

### Project-level (shared)

| File:Line | Old pattern | New `paths.*` function |
|---|---|---|
| `run_persona_pipeline.py:64` | `PROJECT_ROOT / "inputs/conference_facts.json"` | `paths.conference_facts()` |

---

## Key discrepancies from plan

1. **`get_project_root()` missing** — `project_root.py` only has `resolve_project_root()`. Need to add `get_project_root()` that reads from env (no-arg version). Phase B adds this.

2. **`render_prompt()` doesn't exist** — actual function is `render()` in `prompt_render.py`. Phase F code must call `render()` not `render_prompt()`.

3. **`StrictUndefined` already in place** — `prompt_render.py:10-20` already uses `StrictUndefined`. Phase M.3 is already partially done; still need header/footer guards.

4. **ibn_battuta fixture** — exists at `tests/fixtures/ibn_battuta/` with `perplexity_dossier.json` + `gemini_broad_scan.json`. Phase D deletes both.

5. **CT output files** — currently named `_ct_pass*.json` under `02_passes/`. New layout has `paths.ct_after_pass_2(slug)` etc. under `04_generation/`.

---

*Written by Sonnet execution session 2026-04-21. Updated when Phase N migration executes.*
