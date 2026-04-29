# Onboarding — fresh-session pickup

**Living document.** Maintained going forward as the permanent fresh-session entry point. The dated `HANDOFF_<DATE>.md` files capture session state-of-the-moment; this doc captures the standing project shape.

---

## What this project is

A provotype for the **World Beautiful Business Forum** AI Democracy Marathon, Athens, **May 7–10, 2026**. Twelve non-human voices (a river, an octopus, Plato, Hannah Arendt, and 8 others) read the day's human panel transcripts overnight and produce written responses — provocations, queries, reflections — that re-enter the human conversation the following morning via Substack read-throughs.

This is a **civic-design artifact**, not a product. Visible construction is a feature. The voices are honest constructions; the audience encounters them alongside their construction notes.

## What "ready for Athens" means (operator priority, 2026-04-27)

**Athens needs the full runtime stack ready, not just the 12 persona cards.** The cards are necessary inputs but not sufficient. When planning work or recommending what's next, weigh runtime workstreams as equally critical to Athens, not "post-Athens deferred." Specifically the Athens-blockers beyond cards:

- **Voice Pipeline Steps 1+2** — NOT BUILT. Without it, no card produces overnight artifacts. Highest single Athens blocker after voice cards complete.
- **Voice Pipeline Step 3 Amendment** — UNSPECIFIED (FU#49E). Reviewer-flagged as conceptually load-bearing for the deliberative-character claim. Spec needed pre-Athens; build can be post-Athens IF Steps 1+2 ship and operator accepts a Step-3-less Athens.
- **Downstream pipeline** (Render → Publish → Curate → Deliver) — UNBUILT. Marley artifact → Suno API; Octopus → client-side shader params; Substack delivery via HoBB newsletter blurb.
- **Microsite** — UNBUILT. What 750 attendees actually see.
- **Admin console** — UNBUILT. Operator infrastructure for orchestrating overnight pipelines + council sync + log tail.
- **Closing-show pipelines** (theme ID + Matrix A/B mapping + video) — UNSPECIFIED, UNBUILT. Day 3 afternoon.

Don't frame "12 voice cards complete" as the Athens completion line. When recommending build-side improvements (LLM-as-judge, FU#50(1) Pydantic enforcement, FU#42 split-card, etc.), check whether they delay runtime work that's already on the critical path. Surface runtime gaps proactively in "what's next" recommendations.

---

## First 30 minutes

Read in this order:

1. **This doc** — you're here.
2. **`_workspace/planning/HANDOFF_<latest>.md`** — current session pickup. As of writing: `HANDOFF_2026_04_27.md`. Read it for the present state-of-the-moment.
3. **`_workspace/planning/FOLLOW_UPS.md`** — active follow-up tracker (FU#1–50 family). Single source of truth for what's open.
4. **`docs/CURRENT_STATE.md`** — gap analysis + architectural rationale. §0 quick map, §1 what exists, §5 architectural decisions.
5. **`docs/AI_Assembly_Briefing_v3_1.md`** — project source of truth (target state).
6. **`docs/AUDIENCE_BRIEF.md`** — audience characterization + contributors-vs-audience distinction (load-bearing).

Stop after this unless the task demands more. ~30–45 min of working knowledge.

For specific tasks, see §"Reading order for specific tasks" below.

---

## Project orientation

### Tier 3 code/project separation (2026-04-20)

Code lives in `code/` (this git repo, `mp13131313/ai-assembly`). Per-project data lives in `projects/` **outside the code repo**. Both pipelines resolve `PROJECT_ROOT` via:

1. `--project <path>` CLI flag (personas runners), or
2. `AI_ASSEMBLY_PROJECT_ROOT` env var, or
3. **Hard fail** — no silent default.

### Active projects (siblings to `code/`)

- `projects/test/` — sandbox (Dostoevsky lives here from earlier work)
- `projects/phase-l-plato/` — Plato Phase L working project (carry-over source for athens-2026)
- `projects/phase-l-dostoevsky/` — Dostoevsky Phase L working project
- `projects/athens-2026/` — **production**. Has its own private backup git repo: `mp13131313/ai-assembly-athens2026-voices`. Back up there after voice CARD COMPLETE.

### Two pipelines, two venvs, one .env

- `personas/` (pre-conference) — produces 35-field voice cards. Pipeline v4 (2026-04-27).
- `runtime/` (overnight) — transcribes, researches, formulates provocations, produces voice artifacts.

Each has its own venv (`personas/venv/`, `runtime/venv/`); both load secrets from `code/.env`. Activate the correct venv for the sub-tree you're in.

---

## Common operations

### Build a single voice's persona card

```bash
cd code/personas
set -a && source ../.env && set +a
export AI_ASSEMBLY_PROJECT_ROOT="../../projects/athens-2026"

# 1. Pass 0a (voice config + review doc)
venv/bin/python run_pass0a_voice_config.py "Voice Name"

# 2. Phase 0.5 (Perplexity + Gemini parallel + DR prompt assembly + 6-section split)
venv/bin/python run_phase0_1_research.py "Voice Name"

# 3. [Manual: 6 claude.ai sessions per voice with Extended Thinking + Deep Research]
#    §1–§5: Opus 4.6
#    §6:    Opus 4.7  (Phase L empirical: 4.6 produces reader's-intro on §6)
#    Save each as $PROJECT_ROOT/voices/<slug>/01_research/04_dr_dossier/0N_section_N.md

# 4. Main pipeline (chunked merge → generation → validation → derive → assembly)
venv/bin/python run_persona_pipeline.py "Voice Name"
```

ETA: ~2h API time after DR dossiers complete. Cost: ~$18–22/voice.

### Batch multiple voices' DR prompts (pre-DR)

```bash
cd code/personas
scripts/batch_pre_dr.sh "$AI_ASSEMBLY_PROJECT_ROOT/voices_batch.txt" --parallel 3
```

### Batch full pipeline runs (after DR data lands per voice)

When 6 manual claude.ai DR sessions are saved for one or more voices, run
the full pipeline via the batch wrapper. **Always passes `--project`
explicitly — refuses env-var fallback to avoid wrong-folder accidents
during unattended runs.**

```bash
cd code/personas
scripts/run_pipeline_batch.sh \
    --project /Users/aienvironment/Desktop/AI\ Assembly/projects/athens-2026 \
    --parallel 3 \
    "Cleopatra" "Octopus" "Bob Marley"
```

Per-voice logs land at `$PROJECT/batch_logs/<slug>.pipeline.log`; summary
at `_batch_results_<timestamp>.txt`. Each voice resumes from cache on
re-run, so failed voices can be retried individually.

### Wrong-folder safety harness

Every runner prints a startup banner showing `PROJECT_ROOT` + `SOURCE`
(`--project` / env-var / default). When resolution targets a production
project (basename contains `athens-2026` or `phase-l-`) via env-var
fallback (no explicit `--project` flag), the banner escalates with ⚠
markers and a "production target via env-var fallback" warning.
Operator can abort with Ctrl-C if unintended. Sandbox env-var
resolution stays quiet.

**Operator habit:** for production runs (athens-2026), always pass
`--project` explicitly — even on single ad-hoc invocations. The env-var
default in `code/.env` points at `projects/test` by design.

### Run a runtime stage on test data

```bash
cd code/runtime
venv/bin/python flows/transcription_flow.py path/to/audio.mp4 path/to/session.json
venv/bin/python flows/researcher_flow.py path/to/session_package.json
venv/bin/python flows/provocateur_flow.py path/to/researcher_output.json
```

### Sentinel regen for prompt edits (FU#29)

```bash
# Snapshot pre-edit
mkdir -p _workspace/sentinel_baselines/2026-MM-DD-pre-X/<slug>
cp <PROJECT_ROOT>/voices/<slug>/04_generation/<file>.json \
   _workspace/sentinel_baselines/2026-MM-DD-pre-X/<slug>/

# Edit prompt, then:
python scripts/sentinel_regen.py regen \
  --pass <PASS_NAME> --voices <slug> \
  --baseline-snapshot _workspace/sentinel_baselines/2026-MM-DD-pre-X
```

### Run tests

```bash
cd code/personas && venv/bin/python -m pytest tests/   # 212 tests as of 2026-04-27
```

---

## Key files (by task surface)

### Persona pipeline orchestrator

- `personas/run_persona_pipeline.py` — main orchestrator (1838 lines)
- `personas/run_pass_1_all.py` — chunked merge driver (Pass 1.1–1.6 parallel)
- `personas/run_pass_1_7.py` — narrow coherence audit
- `personas/run_pass0a_voice_config.py` — Pass 0a
- `personas/run_phase0_1_research.py` — Phase 0.5

### Shared libraries

- `personas/flows/shared/paths.py` — path conventions (always go through this)
- `personas/flows/shared/clients.py` — model API wrappers (Claude/Perplexity/Gemini/OpenAI)
- `personas/flows/shared/chunk_runner.py` — Pass 1.1–1.6 runner
- `personas/flows/shared/bracket_strip.py` — Pass 6.5-clean (FU#33 P1)
- `personas/flows/shared/pass_7pre_chunked.py` — Pass 7-pre 3-stage (FU#2)
- `personas/flows/shared/patch_walker.py` — FU#13 patcher
- `personas/flows/shared/chat_prompt_builder.py` — FU#41 chat artifact
- `personas/flows/shared/url_extract.py` — Pass 1c-extract (1-arch-07)
- `personas/flows/shared/perplexity_split.py` — section-aware dossier split

### Schemas (Pydantic source of truth)

- `personas/schemas/voice_config.py`
- `personas/schemas/pass_1_1.py` … `pass_1_6.py` (chunk schemas)
- `personas/schemas/_frames.py` (1-arch-06: InterpretiveFrame)
- `personas/schemas/_analytical.py` (1-arch-04: AnalyticalContext)
- `personas/schemas/merged_dossier.py`

### Prompts

`personas/flows/shared/prompts/` — every system + user prompt. Naming convention: `persona_pass_<N>_<name>.md` for system, `_user.md` suffix for user. Pass 0b template family is named `pass_0b_*.md`. Chunk merge prompts are `pass_1_<N>_merge.md` + `pass_1_7_coherence.md`.

### Specs

- `docs/AI_Assembly_Briefing_v3_1.md` — target state (project source of truth)
- `docs/AI_Assembly_Persona_Pipeline_v4.md` — current persona pipeline
- `docs/AI_Assembly_Persona_Card_v2.md` — 35+2 field schema (with v2.1 amendments)
- `docs/CURRENT_STATE.md` — gap analysis + architectural rationale
- `docs/AUDIENCE_BRIEF.md` — audience characterization
- `personas/HANDOFF.md` — cross-repo runtime contract

### Active tracking

- `_workspace/planning/HANDOFF_<latest>.md` — session pickup
- `_workspace/planning/FOLLOW_UPS.md` — active FU# tracker
- `_workspace/planning/ONBOARDING.md` — this doc

---

## DON'Ts

Standing rules. Operator-level ones come from CLAUDE.md (global) and the project's calibration history; project-level ones come from session learnings.

- **No Plato re-run without explicit ask.** Card shipped per chat-test 2026-04-26.
- **No Dostoevsky full re-run.** Phase 2 + G10 Derive re-fire on disk in `phase-l-dostoevsky/`.
- **No deletion of athens-2026 contents** without explicit operator confirmation per item.
- **No `--no-verify` / hook bypass.** If a hook fails, fix the underlying issue.
- **No push to `origin/main` without explicit operator confirmation.**
- **No Opus 4.6 for §6 of any voice's DR.** Per model-per-section policy: §6 uses Opus 4.7. (Phase L empirical: 4.6 produces reader's-intro on §6.)
- **No xattr / ACL / system-attribute modification** without explicit operator instruction.
- **No commits with `--allow-empty`.**
- **No real-person names in the 4 deployment-context JSONs** (`conference_facts.json`, `audience_profile.json`, `panel_roster.json`, `council_config.json`). Use generic descriptions ("a former PM," "a leading cognitive-warfare theorist").
- **No hand-authoring voice_configs bypassing Pass 0a.** Pass 0a is operator-trusted; if review disagrees, edit and re-run Pass 0a (do NOT hand-edit downstream).
- **Voices 3–12 should NOT need manual chat-artifact curation.** Pipeline produces clean shipped artifacts. If a voice's chat-test fails, diagnose specifically; don't fall back to Plato-style hand-editing.
- **Never optimize FOR chat-test.** Voice Pipeline (runtime) consumes specific card fields via API per-step; that's the production target. Chat-test is a development feedback instrument.
- **Reflections are vendor JSON, not audio.** (Operator standing memory — Stage 0 transcription does not apply.)

---

## Persona pipeline architecture (v4 summary)

```
Pass 0a (voice_config + review_doc)
   ↓
Phase 0.5: Pass 1a (Perplexity) ‖ Pass 1b (Gemini) → Pass 0b base render
           → Pass 0b tailor (LLM splice) → split into 6 per-section DR prompts
   ↓
[MANUAL: 6 claude.ai DR sessions per voice — §1–§5 Opus 4.6, §6 Opus 4.7]
   ↓
Pass 1.1–1.6 chunked merge (parallel; Pydantic-validated per chunk)
   1.1 BIOGRAPHICAL  → life_scaffold + formative_candidates
   1.2 INTELLECTUAL  → commitments + concepts + tensions + interpretive_frames
   1.3 REASONING     → reasoning_method + textures + analytical_context_reasoning
   1.4 VOICE         → moves + register + vocabulary + analytical_context_voice
   1.5 BOUNDARIES    → knowledge_boundary + sensitive_topics + hard_limits
   1.6 CORPUS        → works + passages + reference_only_passages
   ↓
Pass 1.7 narrow coherence audit (emits flags + resolutions + edits[];
                                  Python applies edits to chunk files;
                                  chunks are SoT, 08_merged_dossier.json is snapshot)
   ↓
Pass 1c-extract → Pass 1c fetch (SSRF-hardened) → Pass 1c REVIEW GATE (manual flag)
   ↓
Pass 1d (Opus + thinking, 60K char budget; corpus-grounded excerpt selection)
   ↓
Pass 2 (Identity & Boundaries) → CT compress
Pass 3 (Intellectual Core) → CT compress
Pass 4a (Voice — corpus-grounded) → CT compress
Pass 4b (Artifact) → CT compress
Pass 5 (Engagement — audience-primed via FU#12-B)
Pass 6 (Corpus Curation)
   ↓
Pass 6.5-clean (FU#33 P1 bracket-tag residue strip — preserves Boddice tags)
   ↓
Pass 7-pre (FU#2 chunked: extract → parallel verify → boddice → aggregate)
Pass 7-anachronism (gpt-5.4 high → fallbacks)
Pass 7a (Cross-Model Validation; merges anach + INCONSISTENT into field_issues)
   ↓
[Pass 7a-FIX (FU#13 linear patcher — Opus + thinking; replaces revision loop)
 if REVISION_NEEDED]
   ↓
Pass 7b (Worked Provocations — build-time diagnostic, NOT runtime few-shot)
Pass 7c (Negative Constraints — Gemini → Sonnet bias-aware fallback)
   ↓
Derive (Provocateur Profile + Evaluation Rubric — 8 + 9 fields)
   ↓
Card Assembly (35 fields + 2 continuity null + reference_only_passages + metadata)
   ↓
FU#41 chat artifact (chat_prompt_builder.py — strips 11 items)
   ↓
CARD COMPLETE summary (FU#7 operator triage block)
```

Per-voice on disk: see `personas/README.md` §"Per-voice subfolder layout".

---

## After CARD COMPLETE — operator review checklist (FU#52, 2026-04-29)

**The pipeline's CARD COMPLETE summary is advisory, not a gate.** The runtime card + chat artifact are written to disk before validators' residuals get human review. **Operator runs this checklist BEFORE any commit/push/ship of voice outputs.** Empirical case study (Plato 2026-04-28): 25 minutes of operator-side review caught ~13 ship-quality improvements that would otherwise have shipped baked into the chat prompt.

The 6 manual checks (per-voice, after every pipeline run):

1. **Read `05_validation/01_pass_7_pre_citation.json`** — scan items where `status` ∈ {`INCONSISTENT`, `UNVERIFIED`}. Decide per-item: fix, accept-with-rationale, or accept-as-defensible. (`DOSSIER_ONLY` and `INTERPRETIVE` are typically defensible.)

2. **Read `05_validation/02_pass_7_anachronism.json`** — scan `anachronism_flags`. Cross-reference `02_merge/_fix_log.json` patches to see which were addressed by 7a-fix. Apply manual edits for unaddressed flags using the upstream-pass-file + assembled-card dual-write pattern.

3. **Read `05_validation/03_pass_7a_cross_model.json`** — scan residual `field_issues`. Decide per-issue: fix, accept-with-rationale, or accept-as-defensible (e.g., protective references like banned_modes naming TED-talk register may be operationally useful even if temporally leaky).

4. **Optional: re-fire Pass 7a against the FULL post-7c card** to catch issues in Pass 7c additions that the cached Pass 7a (run pre-7c) missed. See `/tmp/plato_pass7a_full_validation.py` from 2026-04-29 session for a reusable script template.

5. **After any manual edits:** regenerate the chat artifact:
   ```python
   from flows.shared.chat_prompt_builder import write_chat_system_prompt
   write_chat_system_prompt(card_dict, chat_path)
   ```

6. **Audit the assembled card for voice-architecture-specific collisions** (e.g., for mediated voices like Plato/Scheherazade: first-person speaker collapses into corpus-internal speakers).

**On pipeline-side gate:** a pipeline-side review-gate between post-fix re-validate and Pass 7b is proposed but post-Athens (FU#52 in FOLLOW_UPS.md). For now the operator-side checklist is the gate.

---

## Reading order for specific tasks

**"I need to make a prompt edit":**
1. `_workspace/planning/FOLLOW_UPS.md` §FU#29 sentinel_regen pattern
2. The target prompt file under `personas/flows/shared/prompts/`
3. `personas/scripts/sentinel_regen.py` CLI
4. Snapshot baseline → edit → regen → diff → restore (if smoke-test)

**"I need to debug a Pass N output":**
1. `personas/run_persona_pipeline.py:<line>` for the relevant pass (use the v4 spec table to find it)
2. The pass's prompt file under `personas/flows/shared/prompts/`
3. The pass's schema (if Pass 1.x) under `personas/schemas/`
4. The voice's data on disk under `<PROJECT_ROOT>/voices/<slug>/` for inputs + outputs

**"I need to add a follow-up":**
1. `_workspace/planning/FOLLOW_UPS.md` tail
2. Pick severity tier (P0/P1/P2 or by-letter)
3. Write entry per existing format (status, what, where, why, blocked-by, etc.)

**"I need to update a doc":**
1. `docs/README.md` staleness index → identify the right doc
2. Read the doc + briefing for target state
3. Read code for actual current state (don't trust handoffs over code)
4. Write update; add to commit alongside the code change that triggered it

**"I need to add a new voice":**
1. `docs/AI_Assembly_Persona_Pipeline_v4.md` §"Phase 0: Intake" + Phase 0.5
2. `personas/run_pass0a_voice_config.py` CLI
3. Add voice to `<PROJECT_ROOT>/voices_batch.txt` if running in batch
4. Verify Pass 0a produces sensible voice_config (especially `voice_mode`, `subtype`, `hostile_sources`, `corpus_constraint`)
5. **Pipeline-fidelity audit principle (CURRENT_STATE §5.25):** if voice_config changes after Phase 0.5 ran, three fields affect template selection (`type`/`subtype`/`hostile_sources`); if any flipped, dossier was generated WITHOUT the right warning blocks → re-run Phase 0.5 from scratch. If only `voice_mode`/`corpus_constraint` changed, only the tailor needs to re-run.

**"I need to understand why X was decided":**
1. `docs/CURRENT_STATE.md` §5 (architectural decisions, §5.16–5.28 are the v4-era ones)
2. `_workspace/planning/FOLLOW_UPS.md` for the relevant FU# entry
3. Git log for the commit message (`git log --grep=<FU#>`)

**"I need to onboard someone new":**
1. Point them at this doc.
2. Then `HANDOFF_<latest>.md`.
3. Then `FOLLOW_UPS.md`.

---

## Project state references

| Doc | Where | Purpose |
|---|---|---|
| Briefing v3.1 | `docs/AI_Assembly_Briefing_v3_1.md` | Target state |
| Audience brief | `docs/AUDIENCE_BRIEF.md` | Audience + contributors distinction |
| Current state | `docs/CURRENT_STATE.md` | What exists / what's not / decisions |
| Pipeline v4 spec | `docs/AI_Assembly_Persona_Pipeline_v4.md` | Current persona pipeline |
| Card v2 + v2.1 | `docs/AI_Assembly_Persona_Card_v2.md` | 35+2 field schema with amendments |
| Cross-repo handoff | `personas/HANDOFF.md` | Production runtime contract |
| Active follow-ups | `_workspace/planning/FOLLOW_UPS.md` | FU# tracker |
| Latest pickup | `_workspace/planning/HANDOFF_<DATE>.md` | Session state-of-the-moment |
| Onboarding | `_workspace/planning/ONBOARDING.md` | This doc |

---

## Calibration

- **Operator preference is direct.** When pushed back ("are you sure?", "reason through each again"), the instinct is usually right even when work has been declared done. Re-investigate before bulldozing.
- **Provotype framing is load-bearing.** Civic-design artifact for WBBF Athens 2026, not a product. Visible construction is a feature.
- **Voice Pipeline first, chat-test as instrument.** Voice Pipeline (runtime) consumes specific card fields via API per-step; that's the production target. Chat-test is a development feedback tool — don't optimize FOR it.
- **Model/effort economy.** Per-voice pipeline operation + chat-test paste-and-assess is Sonnet-shaped. Architectural decisions and complex code reading are Opus-shaped.
- **Pass 0a is operator-trusted.** Don't hand-author bypassing it.

---

## When this doc goes stale

- After major architectural shifts: update §"Persona pipeline architecture" + §"Project orientation".
- After new operations or runners: update §"Common operations".
- After new files become load-bearing: update §"Key files".
- After new DON'Ts emerge from session learnings: append to §"DON'Ts".
- After new tasks become common: append to §"Reading order for specific tasks".

The dated `HANDOFF_<DATE>.md` files are session-state snapshots. This doc is the durable scaffolding.

---

*End of ONBOARDING.md.*
