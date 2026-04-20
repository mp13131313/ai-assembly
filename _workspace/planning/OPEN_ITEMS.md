# Open Items — post-Phase B aftermath (updated 2026-04-20)

**Branch**: `phase-b-rebuild` (42 commits, pushed). HEAD = `4dd58c8`.

**Phases A–K landed + cleanups + deferrals + Position C + bias scrub + 5 quality fixes + Pass 1a Perplexity prompt rewrite + Pass 1a validation (Dostoevsky 17K-word dossier) + two parser/validator catch-up fixes + 2026-04-20 DR-failure-diagnosis commits (see §"Session 2026-04-20" below).**

This doc is a fresh-session recovery point capturing every loose end from the long session that produced commits `7ce1e92` through `7458d9d`, updated 2026-04-20 with the DR-failure-diagnosis session (commits `3ad1e83` through `4dd58c8`). Read top-to-bottom for full context, or jump by section.

---

## Session 2026-04-20 — DR-failure diagnosis + prompt hygiene

9 commits landed responding to the Dostoevsky Claude DR failure ("something went wrong" after 90 min / 612 sources on the tailored prompt). HEAD `4dd58c8`, all pushed.

### DR-failure diagnosis

**Symptom**: Dostoevsky tailored DR prompt (50 KB, pasted into claude.ai with Opus 4.7 + Extended Thinking + Deep Research) failed twice with generic "something went wrong" backend error. 90 min wall time, 612 tool-calls / sources accumulated before fail.

**Hypothesis**: tool-call cap exhaustion from compound prompt pressure — (a) `Minimum 15,000 words` floor pushing DR to keep researching, (b) `What this section feeds downstream` blocks leaking Pydantic field names that biased DR toward field-shaped output instead of 6-section dossier, (c) density of named scholars per section triggering recursive verification searches, (d) `Cite every factual claim` + `non-English scholarship` each multiplying tool calls per claim.

612 sources is pathological — scholarly dossiers synthesise from 50-150 sources. The research phase never transitioned to synthesis.

**Mitigations landed (all commits pushed)**:

| Commit | Change | Effect |
|---|---|---|
| `e4d1bd7` | Stripped 24 `What this section feeds downstream` blocks from all 4 pass_0b voice-type templates | Removes Pydantic-field-name leak that biased DR output shape |
| `91b3851` | Dropped `Minimum 15,000 words` from `pass_0b_footer.md` + lowered `dr_validation._TOTAL_WORD_FLOOR` 15000 → 8000 | Removes the signal that pushed DR to keep researching |
| `6ff25b3` | Dropped 3 dead `perplexity_findings` / `gemini_findings` context vars from `run_phase0_1_research.py` base render | Cleanup — Position A → Position C transition artifact, no functional change |
| `a316081` | Stripped `(→ feeds Pass 1.N chunked merge)` header annotations + inline `Feeds X` refs from all 4 pass_1a templates | Extends feeds-downstream strip philosophy to the Perplexity prompts |
| `d073ad4` | Applied the 5 Dostoevsky-validated Pass 1a fixes to organism / system / fictional templates | Closes the "follow-up needed" item; all 4 pass_1a templates now carry the same validated pattern |
| `4dd58c8` | Closed 3 parity gaps: hostile_sources block in organism; recent-reassessments bullet in human + fictional | All 4 pass_1a templates now fully parity-aligned |

Plus infrastructure:

| Commit | Change |
|---|---|
| `3ad1e83` | `CLAUDE.md` top-note documenting the active `phase-b-rebuild` branch state |
| `d3e3647` | Tier 1 gitignore (regenerable per-voice artifacts: `_pass0a_review.md`, `_dr_prompts/`) |

**Regeneration result**: re-ran `run_phase0_1_research.py "Fyodor Dostoevsky"` after the strip + floor-drop landed. Cached Perplexity + Gemini outputs reused (unchanged by template edits); base DR prompt re-rendered against stripped templates (31.8 KB, down from 34.6 KB); Opus 4.7 tailoring pass re-ran (359.8s wall, ~55K input / 19K output tokens, ~$0.50). Produced fresh 43 KB tailored prompt with 12 coverage-note / figure-swap / SWAP-TEST edits. Ready to paste.

**Pending verification**: does the regen resolve the "something went wrong" failure? Third paste pending. If it still fails, fallback options (ordered least-disruptive to most):
1. Paste the base (pre-tailoring) prompt instead — 31.8 KB; fewer named scholars per section.
2. Use the 2-week-old v3.7-spec-paste Dostoevsky card as the Claude DR dossier — place it at `personas/inputs/dossiers/fyodor_dostoevsky_claude_dr.md` and proceed. Loses clean-slate Phase B lineage but unblocks.
3. Modify `chunk_runner.py` to accept a missing DR dossier and 2-source-merge (Perplexity + Gemini). Quality impact real but measurable.

### Item 6 retrospective — "cosmetic, not blocking" was wrong

The 2026-04-19 quality review tagged the `What this section feeds downstream` blocks (later `Item 6 — reframe 'feeds downstream' lines without internal field names`) as **cosmetic, not blocking**. The Dostoevsky DR failure and the 612-source pathological-depth run suggest that assumption was wrong: the pipeline-field-name leaks plausibly steered DR toward field-shaped verification loops rather than a clean 6-section dossier. The strip (both pass_0b and pass_1a) is now done; the retrospective lesson is that **pipeline-internal jargon in LLM-facing prompts is load-bearing unless proven otherwise**.

### Phase L first-voice switch: Plato → Dostoevsky

Original plan (`EXECUTION_PLAN_phase_b.md` §L.8): compare rebuilt Plato against `_workspace/archive/runs/personas/plato/persona_card_assembled.json` as the v3.10 baseline. Current plan: Dostoevsky instead, with baseline = 2-week-old persona card the user generated by pasting the v3.7 pipeline spec into claude.ai (saved on user's Desktop, not in repo yet). Rationale: Dostoevsky's tailored DR prompt already exists; starting Plato from scratch costs an additional $10-15 and 20 min of Phase 0.5. Loses direct regression comparison against the v3.10 archived Plato card but keeps the two-week-old v3.7-paste card as a meaningful Phase L baseline. If the Dostoevsky DR completes, the Phase L.8 quality gate becomes: Boddice-shape check (§13 5-part `world`, §14 4-part `formative_experience`, §15 period character-grammar, evidence tags in place, `smoke_test_chains` build-time-only, period-vocabulary-informed-not-displayed Pass 4a) + v3.7-baseline comparison on what Phase B produces differently.

Plato as Phase L is still available if the Dostoevsky run falls through — the v3.10 archived baseline is there.

### Items still carrying forward (from pre-2026-04-20 review)

- **Item 8** (clean panel-voice anchoring from non-human / fictional Pass 0b templates) — still pending (~1h per template). Not blocking Dostoevsky's run because Dostoevsky is a human voice.
- **Apply the Pass 1a fix to 3 other voice-type templates** — ✅ **DONE** in `d073ad4` + parity closure `4dd58c8`.
- **Tier 1 gitignore** — ✅ **DONE** in `d3e3647`. Dostoevsky voice config + review doc + `_dr_prompts/` no longer pollute git.
- **Item 6** (reframe feeds-downstream lines) — ✅ **DONE** via strip in `e4d1bd7` + `a316081`; retrospective note above.

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

**Tier 3 implementation checklist** — ✅ **LANDED 2026-04-20** (full umbrella + both pipelines):

**Filesystem (umbrella restructure):**
- ✅ Moved `~/Desktop/ai-assembly/` → `~/Desktop/AI Assembly/code/`
- ✅ Moved `~/Desktop/athens-2026/` → `~/Desktop/AI Assembly/projects/athens-2026/`
- ✅ Created `~/Desktop/AI Assembly/projects/test/` with baseline project context copied from Athens.
- ✅ Split Dostoevsky (in-progress voice, runs, DR prompts) out of athens-2026 into test/ so production stays clean.

**Personas pipeline:**
- ✅ `flows/shared/project_root.py` — precedence: `--project` → `AI_ASSEMBLY_PROJECT_ROOT` env → **hard failure** (no silent default; multiple projects make fallback dangerous).
- ✅ All 13 runners updated (0a, 0b standalone, 0b tailor, Phase 0.5, 1.1-1.7, 1_all, persona_pipeline, phase_5_qc).
- ✅ `chunk_runner.py` takes both `repo_root` (test fixtures) and `project_root` (live runs).
- ✅ `io.py::load_voice_input` takes `project_root`.

**Runtime pipeline:**
- ✅ `flows/shared/project_root.py` — same module, copied per venv isolation.
- ✅ `ingest/config.py` resolves `PROJECT_ROOT` after `load_dotenv`; `RUNS_DIR` / `REFERENCE_DIR` / `SESSIONS_PATH` / `SPEAKERS_PATH` derived from it.
- ✅ `flows/shared/io.py::load_council_config` defaults to `$PROJECT_ROOT/council_config.json`.
- ✅ `scripts/generate_sessions_json.py` + `generate_speakers_json.py` defaults to `$PROJECT_ROOT/reference/*.json`.
- ✅ `INGEST_FLOW_CMD` uses `shlex.join` so paths with spaces (e.g. "AI Assembly") survive `shlex.split` in pipeline.py.

**Config / secrets:**
- ✅ `.env` at `code/.env` (zero dotenv code change).
- ✅ `AI_ASSEMBLY_PROJECT_ROOT` set in `.env` to `projects/test` — bare invocations land in test; pass `--project` for athens-2026.

**Hygiene:**
- ✅ `.gitignore` cleaned (personas + runtime). All moved tracked files staged as deletions.
- ✅ 29/29 runtime tests pass; personas smoke tests (import + resolver + voice load + prompt render) pass from both test and athens-2026 projects.

**Docs updated:** `CLAUDE.md`, `runtime/README.md`, `personas/README.md`, `docs/CURRENT_STATE.md`, `EXECUTION_PLAN_phase_b.md`, `docs/AUDIENCE_BRIEF.md`.

**Enables**: multiple projects on one codebase (test + athens-2026 today; berlin-2027 etc. later); VM-friendly deployment (mount a project volume, point env var at it); trivially isolated test runs; git-clean by definition; curator/operator role separation; cross-pipeline handoff via shared PROJECT_ROOT.

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

**Validation result (2026-04-19 23:20)**: ✅ ALL FOUR signals passed on the Dostoevsky re-run:
- Perplexity word count: **15,325 words** (vs prior 1,258 / 3,265; floor 8,000; target 15-30K). 113K chars total.
- `perplexity_split` succeeds: 6 sections cleanly split (30K / 17K / 15K / 12K / 12K / 22K chars).
- Period vocabulary surfaced: 362 non-ASCII Cyrillic chars + 22 gloss markers.
- Evidence tags: 17 tags emitted (lighter `[primary]/[consensus]/[contested]` set, as the new prompt asks for).

The fix is validated. **Apply the same pattern to the 3 other voice-type templates** (`persona_pass_1a_non_human_organism.md`, `_non_human_system.md`, `_fictional.md`) — should be ~20 min per template. Same five fixes: explicit length floor, exact `## N. SECTION_NAME` heading format, non-English scholarship load-bearing block, depth-not-breadth framing, softened tag set.

## Two follow-up parser/validator fixes — commit `062d47a` (2026-04-19 23:25)

The first successful Dostoevsky run (17K-word Perplexity dossier, post-prompt-fix) surfaced two downstream catch-up bugs:

1. **`perplexity_split.py` §5 regex**: the new prompt ships `## 5. HISTORICAL + CONCEPTUAL BOUNDARIES` (more accurate than the legacy `HISTORICAL BOUNDARIES`). The "+ CONCEPTUAL" infix broke the regex's word-boundary anchor; §5 wasn't recognized; full split failed. Fixed by accepting optional `+ CONCEPTUAL` infix.
2. **`research_validation.py` evidence-tag regex**: smoke-test was checking for the OLD 5-Boddice-tag set; new Pass 1a prompt asks Perplexity for `[primary]/[consensus]/[contested]` only. False-positive `evidence_tags: 0` warning. Updated regex to accept BOTH tag families.

Both fixes verified against the actual Dostoevsky dossier — split now finds 6 sections cleanly, smoke-test now 4/4 pass.

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
2. **Apply Pass 1a fix to the other 3 voice-type templates** (~20 min each = ~1 hr total). Pattern validated by Dostoevsky run; same five fixes (length floor + exact heading format + non-English scholarship + depth-not-breadth + softer tag set) needed for `_non_human_organism.md`, `_non_human_system.md`, `_fictional.md`.
3. **Tier 3** (~2 hours): code/project separation. Right architecture for Phase L + multi-project + VM deployment.
4. **Phase L** (~$50–70, ~2–4 hours including manual paste + L.8 quality review): first-voice Plato rebuild. Plato is human-type, so already benefits from the validated Pass 1a fix.
5. **Phase M** (~30 min): verify + push + open PR.

Optional in any order: walkthrough remaining steps (6–25), deferred items 6 + 8, smaller improvements.

**Note**: the Dostoevsky test run is mid-flight as of HEAD `062d47a` — the tailoring Opus call started at 23:20:49. When it completes, the operator will compare the resulting Position C tailored DR prompt against the v3.7-spec-upload baseline. If the comparison shows Position C wins on the architectural axes (6-section structure, period-vocabulary, formative candidates, evidence tags, Russian scholarship), the Pass 1a + Position C combination is fully validated.

---

## Where this session ended

- 33 commits on `phase-b-rebuild`, all pushed (HEAD `062d47a`)
- Tree clean (no uncommitted work)
- Dostoevsky test run mid-flight: Pass 1a + 1b complete (15K-word Perplexity dossier ✓ all 4 smoke-tests pass after follow-up fixes); Pass 0b base render complete (34K chars); Pass 0b tailoring Opus call in progress
- 29/29 runtime tests green
- M.3 stale-ref greps clean
- All Boddice / Rosenwein / negative-prompt / pipeline-leak / scholar-attribution patterns stripped from base DR prompts
- Tag conventions unified (5 Boddice tags in chunked merge; 3 lighter tags in Pass 1a Perplexity)
- 3 missing field asks added (unique_contribution / stance_tendency / aesthetic_qualities)
- Position C architecture in place + tailoring fires unconditionally
- **Pass 1a Perplexity prompt rewritten + VALIDATED on Dostoevsky** (commit `6ad03d1`); two parser/validator catch-up fixes shipped (commit `062d47a`)

**Pass 1a fix pattern proven; 3 other voice-type templates still need the same treatment** (organism / system / fictional). Estimated ~20 min per template.

Next operator action when this session resumes:
1. Confirm tailoring completed and the tailored DR prompt is rich (compare to first-run-tailoring-notes.json)
2. Paste tailored prompt into claude.ai for Position C vs v3.7 baseline comparison
3. Apply Pass 1a pattern to the other 3 voice-type templates
4. Tier 3 + Phase L
