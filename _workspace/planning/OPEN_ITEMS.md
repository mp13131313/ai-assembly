# Open Items — post-Phase B aftermath (2026-04-19)

**Branch**: `phase-b-rebuild` (31 commits, pushed). HEAD = `6ad03d1`.

**Phases A–K landed + cleanups + deferrals + Position C + bias scrub + 5 quality fixes + Pass 1a Perplexity prompt rewrite (post-Dostoevsky-thinness diagnosis).**

This doc is a fresh-session recovery point capturing every loose end from the long session that produced commits `7ce1e92` through `7458d9d`. Read top-to-bottom for full context, or jump by section.

---

## CRITICAL — do before Phase L Plato run

### Code / project separation (Tier 3)

**Problem**: the codebase currently conflates code with project-specific data. `personas/inputs/conference_facts.json`, `personas/inputs/audience_profile.json`, `personas/inputs/panel_roster.json`, `personas/inputs/non_human_grounding/`, and `personas/inputs/voices/<slug>.json` all describe Athens 2026 specifically. `personas/runs/<slug>/...` also lives inside the code repo (gitignored, but still file-system-coupled). Per-voice runtime artifacts (review docs, DR prompts, tailoring notes) are tracked, polluting the repo on every test run.

**Right architecture**: code/project separation with `PROJECT_ROOT` distinct from the code repo.

```
ai-assembly/                    # CODE REPO (in git)
├── personas/
│   ├── flows/                  # Code
│   ├── schemas/                # Code
│   ├── run_*.py                # Code
│   └── flows/shared/prompts/   # Prompt templates
├── runtime/                    # Code
└── tests/fixtures/             # Pinned test fixtures (code-level)

athens-2026/                    # PROJECT DATA (separate dir, possibly own git repo or VM-mounted volume)
├── inputs/
│   ├── conference_facts.json
│   ├── audience_profile.json
│   ├── panel_roster.json
│   ├── non_human_grounding/
│   └── voices/<slug>.json      # curator-edited
├── runs/<slug>/                # All pipeline runtime outputs
└── dossiers/<slug>_claude_dr.md
```

Runners take `--project /path/to/athens-2026/` or read env `AI_ASSEMBLY_PROJECT_ROOT`. Default = `./project/` in cwd, or whatever convention.

**Three tiers**:

| Tier | What | Cost | Status |
|---|---|---|---|
| 1 | Gitignore regenerable bits (review docs, DR prompts, tailoring notes). Voice configs stay tracked. | 5 min | **Probably do before Dostoevsky test run** |
| 2 | Move all runtime outputs to `personas/_generated/` (single gitignored hierarchy). | ~30–45 min | Skip — superseded by Tier 3 |
| 3 | Extract `PROJECT_ROOT` from code repo. All project data lives outside the code repo. Runners take `--project`. | ~2 hours | **Do this before Phase L Plato run** — Plato will produce a real persona card you'll want clean separation for |

**Tier 3 implementation checklist** (when this lands):

- New constant / env var pattern: `PROJECT_ROOT` resolved from `--project` arg, then `AI_ASSEMBLY_PROJECT_ROOT` env, then `./project/` default.
- Update runners to read inputs from + write outputs to `PROJECT_ROOT`:
  - `run_pass0a_voice_config.py` — VOICES_DIR + non_human_grounding paths
  - `run_phase0_1_research.py` — DR_PROMPTS_DIR + runs path
  - `run_pass_0b_tailor.py`
  - `run_pass_1_1.py` through `run_pass_1_7.py` (via `chunk_runner.py`)
  - `run_pass_1_all.py` (inherits from chunk_runner)
  - `run_persona_pipeline.py`
  - `phase_5_cross_persona_qc.py`
- `flows/shared/chunk_runner.py` already takes `repo_root` — extend to accept `project_root` separately.
- Move `personas/inputs/conference_facts.json`, `audience_profile.json`, `panel_roster.json`, `non_human_grounding/` to a new `athens-2026/inputs/` dir (separate from code repo).
- Update `.gitignore` to exclude `personas/runs/`, `personas/inputs/voices/`, `personas/inputs/dossiers/_dr_prompts/` (those move to project data).
- Remove the now-empty `personas/inputs/voices/` and `personas/inputs/dossiers/_dr_prompts/` from tracking (`git rm`).
- Update `CLAUDE.md`, `docs/CURRENT_STATE.md`, `personas/README.md` to document the new layout.
- Update `EXECUTION_PLAN_phase_b.md` Phase L commands to use `--project`.

**Enables**: multiple projects on one codebase (Athens 2026 + Berlin 2027 + scratch sandbox); VM-friendly deployment; trivially isolated test runs; git-clean by definition; curator/operator role separation.

---

## Walkthrough still in progress

User asked for a step-by-step walkthrough of the 25-pass pipeline. Steps 1–5 covered:

1. ✅ Pass 0a (voice config) — covered with full architecture
2. ✅ Pass 1a (Perplexity sonar-deep-research) — covered
3. ✅ Pass 1b (Gemini broad scan) — covered
4. ✅ Pass 0b base render + tailoring — covered (including Position C correction)
5. ✅ Pass 1a-DR (manual claude.ai session) — covered

Remaining steps:

6. Pass 1.1 BIOGRAPHICAL chunked merge
7. Pass 1.2 INTELLECTUAL
8. Pass 1.3 REASONING
9. Pass 1.4 VOICE
10. Pass 1.5 BOUNDARIES
11. Pass 1.6 CORPUS (including the two-tier `reference_only_passages`)
12. Pass 1.7 COHERENCE
13. Pass 2 (Identity & Boundaries)
14. Pass 3 (Intellectual Core)
15. Pass 4a (Voice)
16. Pass 4b (Artifact)
17. Pass 5 (Engagement)
18. Pass 6 (Corpus Curation)
19. Pass 7-pre (Citation Verification + Boddice tag check)
20. Pass 7-anachronism (TimeChara-style)
21. Pass 7a (Cross-Model Validation)
22. Pass 7b (Card Smoke Test — `smoke_test_chains`)
23. Pass 7c (Negative Constraints — `banned_language` + `projection_warnings`)
24. Phase 4 Derive (Provocateur Profile + Evaluation Rubric)
25. Phase 5 Cross-Persona QC

User can resume this in any future session. The pattern of each step is: name + phase + cost + wall-time + model + why-it's-there + input + what-happens + output + anything-else.

---

## Phase L — first-voice Plato test (gated, ~$50–70)

Per `EXECUTION_PLAN_phase_b.md`. The single explicit stop-and-ask trigger from the original plan. Requires:

- ~$50–70 across Pass 0a + Phase 0.5 + chunked Pass 1 + Pass 2–6 + Pass 7.x + Derive
- Manual human-in-the-loop step at L.3 (paste tailored DR prompt into claude.ai, wait 30–60 min, save dossier)
- Manual quality review at L.8 against `_workspace/archive/runs/personas/plato/persona_card_assembled.json` baseline

**Should land AFTER Tier 3 architecture work** — Plato is the first real Phase B persona card; clean code/project separation matters more for it than for Dostoevsky test runs.

---

## Phase M — verify + push + PR (gated on L passing)

Per `EXECUTION_PLAN_phase_b.md`. Final verification + GitHub PR. Already mostly green (29/29 runtime tests + clean stale-ref greps as of HEAD), but should re-verify post-L.

---

## Pass 1a Perplexity prompt revision — commit `6ad03d1` (2026-04-19 23:30)

**Diagnosis** from two consecutive Dostoevsky test runs: Perplexity sonar-deep-research returned 3,265 words then 1,258 words (floor 8,000; well-documented voices 15-30K). For one of the most-documented figures in Russian literary history, that's a prompt-side issue, not a Perplexity-tier issue.

**Five fixes shipped in `persona_pass_1a_human.md`**:

1. **Explicit length target** at top of prompt: "minimum 15,000 words total; each section 2,000+ words." Brevity defeats the downstream synthesis pipeline.
2. **Exact section heading format** specified: `## 1. BIOGRAPHICAL FOUNDATION`, `## 2. INTELLECTUAL FRAMEWORK`, etc. The downstream `perplexity_split` parser depends on this exact format. Previous "organise findings under these six headings" let Perplexity invent variations — that's why we kept seeing "WARN: Perplexity output could not be split by section — falling back to single-block scaffolding".
3. **Non-English scholarship load-bearing block**: Russian for Russian writers (Бахтин / Касаткина / Лотман); Arabic for Islamic figures; Sanskrit/Pali for Buddhist; Spanish for Latin American; etc. Cite scholars in original-language transliteration. Documented sonar-deep-research failure mode is Anglophone-only default.
4. **Depth-not-breadth framing**: better to do §1/3/6 thoroughly than all six shallowly.
5. **Softened tag asks**: previous prompt asked Perplexity to apply 5 Boddice tags — heavy structural ask Perplexity has no canonical training on. Pass 1a now asks for `[primary]`/`[consensus]`/`[contested]` only, with substance + sources as priority. Tag rigor moved to chunked merge prompts (Opus reads, can apply).

**Plus**: moved "cite all claims" instruction upfront; added pochvennichestvo-equivalent specificity bullet in §2; per-section word targets (2,500 / 2,500 / 2,000 / 1,500 / 2,000 / 2,000).

**Follow-up needed**: same fixes likely needed for `persona_pass_1a_non_human_organism.md`, `_non_human_system.md`, `_fictional.md`. Defer until human-template revision is validated by a clean Dostoevsky run. ~20 min per template if human-template fix proves out.

**Validation test**: re-run Dostoevsky from clean state. Watch for:
- Perplexity word count crossing the 8,000 floor (target 15K+)
- `perplexity_split` succeeds (no "falling back to single-block" warning)
- Russian-language scholarship cited (Бахтин, Касаткина, Volgin, Borisov, Эткинд, etc.) without needing tailoring LLM to compensate

If validated → apply same pattern to other 3 voice-type templates. If not → Perplexity-tier issue is real and we may need to switch tiers (sonar-pro) or rethink the Pass 1a/Pass 1a-DR division of labor.

---

## Dostoevsky test run (operator action)

Voice configs cleared from prior aborted run. Tree clean. To run:

```bash
cd /Users/aienvironment/Desktop/ai-assembly/personas
venv/bin/python run_pass0a_voice_config.py "Fyodor Dostoevsky" \
    --wiki https://en.wikipedia.org/wiki/Fyodor_Dostoevsky
# read review doc; leave editorial_rationale: null
venv/bin/python run_phase0_1_research.py "Fyodor Dostoevsky"
# tailored DR prompt at inputs/dossiers/_dr_prompts/fyodor_dostoevsky_dr_prompt.md
# paste into claude.ai (Opus 4.7 + Extended Thinking + Deep Research)
```

Cost ~$12–20. Wall ~10–20 min for Phase 0.5 + 30–60 min wait for claude.ai DR.

**Purpose**: compare the resulting Claude DR dossier against whatever the user got when they pasted the v3.7 pipeline spec into claude.ai. Tests whether the Position C tailored prompt produces meaningfully better DR output.

**If you do Tier 1 first**: review docs + DR prompts won't pollute git. Recommended.

---

## Deferred items from today's quality review

Five mechanical fixes landed in commit `7458d9d`. Two deferred:

### Item 6 — reframe "feeds downstream" lines without internal field names

Each section opens with `- world (...)` `- formative_experience (...)` etc. — internal Pydantic field names DR doesn't need to see. Could be reframed as plain English. ~30 min. Cosmetic; not blocking.

### Item 8 — clean non-human/fictional templates of panel-voice anchoring

`pass_0b_non_human_organism.md` uses Octopus + Hochner + Godfrey-Smith + Mather as worked examples (22 mentions). `pass_0b_non_human_system.md` uses Whanganui + Te Pou Tupua + iwi-specific scholars (22 mentions). `pass_0b_fictional.md` uses Scheherazade extensively (20 mentions).

Self-anchoring is harmless as long as the panel stays at 12. If the panel ever expands to add a second non-human-organism / non-human-system / fictional voice, those new voices' DR runs would be subtly anchored to the existing panel voice. ~1 hour to swap each panel-voice example for a parallel non-panel exemplar.

---

## Smaller improvements (non-blocking)

### Perplexity retry: retry-twice instead of retry-once

`flows/shared/research_validation.py` and `_with_retry()` in `run_phase0_1_research.py` give one retry. Two retries with exponential backoff (15s, 60s) would catch more transient failures. ~10 min.

### `perplexity_split.split_dossier()` per-section fallback

REBUILD_PLAN flagged: today's all-or-nothing returns `None` if any one of the 6 section headings fails to match. Should recover per-section and warn loudly on the missing ones. ~20 min.

### `_manifest.json` per-pass cost telemetry

Decisions log #4: "No cost cap; quality-first. Track per-pass cost in `_manifest.json` retrospectively but no alarms." Not implemented. ~30 min — wrap each `call_claude` / `call_perplexity` / `call_gemini` / `call_openai` to append usage to a per-voice manifest. Useful for actual cost analysis after a few real voice runs.

### Runtime enforcement of `reference_only_passages` Step 1/Step 2 contract

The two-tier corpus design (Marley lyrics in private reasoning only) is documented in `personas/HANDOFF.md`. The runtime Voice Pipeline Step 2 assembly code MUST drop the field before rendering. The runtime Voice Pipeline doesn't exist yet (out of scope per REBUILD_PLAN — separate workstream). When that workstream starts, this contract needs to land in code, not just docs.

### MergedDossier.register / voice_register Pydantic alias verification

Cleanup-deferral-B fixed the Pydantic warning by renaming the attribute to `voice_register` with `alias="register"` + `populate_by_name=True` + `serialization_alias="register"`. The primary site (`run_pass_1_7.py` → `model_dump(by_alias=True)`) is updated. Not audited across all consumers. Low probability of breakage but worth verifying if Pass 1.7 ever produces unexpected output.

### Dead Pass 1-merge prompts already removed

Cleanup-deferral-C removed `persona_pass_1merge_contradiction_system.md` + `persona_pass_1merge_three_way_user.md` + `persona_pass_1c_extract_urls.md`. They're in git history if resurrection is ever needed.

---

## Lessons learned (architectural insights from this session)

For a fresh session reading this doc cold, these inform how the prompts were designed:

### Position C: DR prompt does NOT inline Perplexity + Gemini

We considered three architectures for the DR prompt:
- **A**: Inline Perplexity + Gemini in full (the v3.10 / original PB#2 design; ~120 KB tailored prompt). Problem: lost-in-the-middle on the Boddice asks; anchoring DR to Perplexity's frame; degraded triangulation at merge.
- **B**: Compact pointer notes summarizing coverage. Better but tailoring LLM has to do harder synthesis.
- **C** (chosen): DR prompt has 6 placeholders; tailoring LLM (Opus 4.7) reads Perplexity + Gemini + voice_config and writes 2–6-sentence coverage notes per section. DR sees only the synthesized notes, not the raw research. Keeps three sources independent for genuine cross-source triangulation at Pass 1.1–1.7 merge. Matches baseline File 2's "compressed summaries > full text" recommendation.

### Tailoring ALWAYS runs (not gated on editorial_rationale)

Per REBUILD_PLAN PB#2 "replaces pure Jinja". Earlier cleanup-3 incorrectly gated the whole tailoring pass on `editorial_rationale` being non-null. Fixed in cleanup-7. Now tailoring fires for every voice; `editorial_rationale` is an optional fourth signal (thematic note injection), not the trigger.

### Boddice / Rosenwein / Bradshaw / van der Kolk attributions stripped from base DR prompts

Claude DR doesn't need to know we're using Boddice's framework. The asks (4-part formative rubric, period character-grammar, overlapping communities, [experiential_reconstruction] tags) are preserved verbatim; the scholar-attributions are dropped. Internal scaffolding (the tailoring LLM's system prompt) keeps the attributions for Opus's contextual understanding.

### Negative-prompt strips ("don't think of pink elephant")

Removed: "Drop the 'core wound + lesson' framing" and "Do NOT use Big-Five-adjacent adjectives" — by naming the thing-to-avoid we plant the frame in DR's attention. Kept the positive instructions ("use the voice's own framework — Buddhist dukkha, Islamic ibtilā', etc." and the period-character-grammar list) which do the work without anchoring DR on what to avoid.

### Pipeline-leak strips

Removed `NOTE: ...AI-default failure modes is NOT your job. That happens downstream in Pass 7c...` paragraphs from Section 4 + Section 5 of all 4 templates. DR doesn't need to know our internal pass naming. The positive instruction (scholarly anti-patterns only) remains.

### Unified evidence-tag convention (today's commit)

Across 4 voice-type templates + footer, at least 5 different tag schemes existed (`[paraphrased from scholarly consensus]` / `[hostile source]` / `[stated in text]` / `[attributed by narrative function]` / etc.). Chunked merge expects exactly the 5 frozen `EvidenceTag` values from `personas/schemas/_conventions.py`: `stated`, `scholarly_consensus`, `inference`, `experiential_reconstruction`, `projection_warning`. All templates now reference the canonical 5 + 3 hostile-source addenda.

### Three missing card-field asks added

`unique_contribution`, `stance_tendency`, `aesthetic_qualities` — all three card fields had no explicit prompt asks. Now have explicit bullets in §1 / §4 across all 4 voice-type templates.

---

## Recommended next-session order

1. **Tier 1** (5 min): gitignore the regenerable per-voice artifacts. Eliminates immediate pollution risk.
2. **Run Dostoevsky** (~$12–20, ~10–20 min + 30–60 min claude.ai paste): validates the new Pass 1a Perplexity prompt (commit `6ad03d1`) AND tests the full Phase 0.5 + Position C tailoring. Compare DR output against the v3.7-spec-upload baseline. Watch for Perplexity word count crossing 8,000 floor + `perplexity_split` succeeding + Russian-language scholarship surfaced without tailoring-LLM compensation.
3. **If Pass 1a validation passes**: apply same prompt-tightening pattern to `persona_pass_1a_non_human_organism.md`, `_non_human_system.md`, `_fictional.md` (~20 min per template).
4. **Tier 3** (~2 hours): code/project separation. Right architecture for Phase L + multi-project + VM deployment.
5. **Phase L** (~$50–70, ~2–4 hours including manual paste + L.8 quality review): first-voice Plato rebuild.
6. **Phase M** (~30 min): verify + push + open PR.

Optional in any order: walkthrough remaining steps (6–25), deferred items 6 + 8, smaller improvements.

---

## Where this session ended

- 31 commits on `phase-b-rebuild`, all pushed (HEAD `6ad03d1`)
- Tree clean (no uncommitted work)
- Dostoevsky artifacts cleared (twice — once for the Position C re-test, once after the Pass 1a prompt revision)
- 29/29 runtime tests green
- M.3 stale-ref greps clean
- All Boddice / Rosenwein / negative-prompt / pipeline-leak / scholar-attribution patterns stripped from base DR prompts
- Tag conventions unified
- 3 missing field asks added (unique_contribution / stance_tendency / aesthetic_qualities)
- Position C architecture in place
- Pass 1a Perplexity prompt rewritten for depth + non-English scholarship + exact heading format + softer tag asks (commit `6ad03d1`); validation pending fresh Dostoevsky run

**Pass 1a prompt changes pending validation on other voice-types** (organism / system / fictional templates not yet tightened — fix only validated for human variant if Dostoevsky run shows improvement).

Next operator action: do Tier 1 + run Dostoevsky fresh + observe Perplexity word count + section-split success. If Pass 1a fix works, apply to other 3 templates. Then schedule focused session for Tier 3 + Phase L.
