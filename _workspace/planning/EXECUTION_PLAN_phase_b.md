# Phase B Execution Plan — status + Phase L pickup

**Branch:** `phase-b-rebuild` (19 commits, pushed). **Phases A–K landed +
pre-L cleanup landed.** **Phase L is the next action.**

## Cleanup pass (2026-04-19, commits `fix(phase-b/cleanup-1..6)`)

After an honest audit, 6 integration / scaffold items surfaced as gaps
between "marked done" and "actually closed". All six closed before
Phase L runs:

- **cleanup-1**: `run_persona_pipeline.py` now calls `run_pass_1_all()`
  (chunked Pass 1 orchestrator) instead of the v3.10 contradiction-check
  merge. Pass 2–6 prompts get the Boddice-chunked JSON shape they asked
  for; `merged_dossier.json` filename collision resolved. Pass 1c-extract
  simplified to read URLs directly from the Pass 1.6 CORPUS chunk (no
  Sonnet call needed).
- **cleanup-2**: Pass 7-anachronism wired into the revision loop. `o3 →
  gpt-4o → Gemini` fallback; anachronism flags translate to Pass 2 / 3 /
  4a / 5 revision targets by `field_path` prefix. Escalates `pass7a.overall`
  to REVISION_NEEDED if 7-anach flags fire and 7a alone said PASS.
- **cleanup-3**: G.4 hybrid Jinja+LLM tailoring (PB#2) shipped.
  `run_pass_0b_tailor.py` + `pass_0b_tailor.md` + wired into
  `run_phase0_1_research.py` — auto-invokes if `editorial_rationale` is
  populated; skips cleanly if null. `editorial_rationale` now has a real
  consumer.
- **cleanup-4**: G.3 `pass_0b_dr_prompt.md` decomposed into 5 sub-templates
  + a 13-line wrapper. `FileSystemLoader` added to runner so `{% include %}`
  resolves. Organism/system subtype split kept inline (risk > benefit).
- **cleanup-5+6**: K Phase 5 QC now fully live. `_same_question_test`
  invokes all 12 voices; swap + blind_id use strict JSON parsing; unified
  `_parse_json_from_text()` handles fenced / preamble-wrapped evaluator
  output; `_call_evaluator()` cascades o3 → gpt-4o → Gemini.

This doc is the single source of truth for what's done vs. what's next on the
persona-pipeline rebuild. When Phase L runs, it produces the first Boddice-
shaped persona card; that run is the quality gate that triggers Phase M
(merge to main). If Phase L reveals regressions, iterate here before M.

---

## Snapshot — what's landed (Phases A–K)

All commits tagged `feat(phase-b/<letter>)`. Run `git log --oneline phase-b-rebuild ^main` for the full list.

### A — Infrastructure

- `personas/schemas/` created with Pydantic source-of-truth per decisions
  log #1. `_conventions.py` holds EvidenceTag / Tier / SourceCitation /
  ContestedReading / ProjectionWarning; **FROZEN** after B + C both landed
  cleanly per PB#7.
- `personas/inputs/conference_context.json` split 3-way into
  `conference_facts.json` + `audience_profile.json` + `panel_roster.json`
  per decisions log #2. Pass 0a consumes facts + roster only; Pass 7b reads
  all three.
- Battuta test fixtures migrated from `_workspace/archive/` into
  `personas/tests/fixtures/ibn_battuta/`. README documents refresh cost
  (~$5–10 Perplexity) + trigger conditions.

### B — Chunk 1.1 BIOGRAPHICAL (proof of architecture)

- `personas/schemas/pass_1_1.py`: LifeScaffold + FormativeCandidate per
  Boddice §13 (5-part world rubric) + §14 (4-part formative with human /
  non-human branches).
- `personas/flows/shared/prompts/pass_1_1_merge.md`: 4-block prompt (role /
  guardrails / schema / worked examples / input / task) per baseline
  research File 2. Three worked examples — Plato, Octopus, Whanganui — per
  decisions log #4.
- `personas/run_pass_1_1.py`: runner loads 3 sources, inlines generated
  JSON Schema, calls Opus 4.7 streaming + adaptive thinking, validates via
  Pydantic, retries once with critique on ValidationError.
- **Live-tested on Battuta fixtures**: 45K in / 9K out; LifeScaffold with
  14 fields; 5 formative candidates; genuinely Boddice-shaped output
  (ṣabr / tawakkul / ibtilā' period vocabulary, anachronisms flagged with
  distortion explanations).

### C — Chunk 1.2 INTELLECTUAL + convention freeze

- `personas/schemas/pass_1_2.py`: Commitment + Concept + Tension.
  `operational_note` + `what_it_rules_out` are load-bearing specificity
  enforcers.
- `personas/flows/shared/chunk_runner.py`: shared harness extracted so
  chunks 1.2-1.6 become thin wrappers.
- `_conventions.py` **FROZEN** header comment added after this chunk
  landed cleanly on Battuta.
- **Live-tested**: 16 commitments / 10 concepts / 6 tensions.

### D — Chunks 1.3–1.6 (pattern replication)

- `pass_1_3.py` + merge prompt: ReasoningMethod (5–8 step cognitive /
  perceptual-response / narratival) + Textures.
- `pass_1_4.py` + merge prompt: Moves + Register (with `tradition_note`
  for oral / ritual / performative voices per Boddice §15) + Vocabulary.
- `pass_1_5.py` + merge prompt: KnowledgeBoundary + SensitiveTopics
  (sanitization-paradox-aware) + HardLimits.
- `pass_1_6.py` + merge prompt: Works + Passages + URLs. Variant rules for
  musical (lyrics-patterns-only), hostile-source, non-human-system corpora.
- **Live-tested 1.3 on Battuta**; 1.4–1.6 import + prompt-render verified
  (same harness as 1.1–1.3).

### E — Chunk 1.7 coherence + orchestrator

- `personas/schemas/merged_dossier.py`: MergedDossier composes all 6 chunks
  + CoherenceFlag / CoherenceResolution (severity + category enums).
- `pass_1_7_coherence.md`: 7 cross-chunk checks (formative/commitment
  alignment, concept usage in reasoning, voice/reasoning register match,
  anachronism boundary, passage/works orphans, hard-limits/commitments,
  period-vocabulary consistency). Three resolution outcomes: edit / accept
  as productive tension / escalate.
- `run_pass_1_7.py`: validates composite; writes `merged_dossier.json`.
- `run_pass_1_all.py`: orchestrator — chunks 1.1–1.6 in ThreadPoolExecutor
  (max_workers=3 default) then 1.7 sequentially.

### F — Pass 0a redesign

- `personas/schemas/voice_config.py`: VoiceConfig with new fields
  (`editorial_rationale`, `manual_grounding`) and dropped
  `conference_context`. `extra="ignore"` allows legacy v3.10 configs to
  load without breaking.
- `flows/shared/io.py`: enum values normalized to underscore form
  (`non_human` / `lyrics_patterns_only` / `hostile_read_against_grain`).
- `pass_0a_voice_config.md`: full rewrite. Drops INJECTED_BY_RUNNER
  placeholder; `editorial_rationale` always null (curator writes
  post-review); review-doc disposition tightened (only `name` is `auto`).
- `run_pass0a_voice_config.py`: loads split configs, resolves
  `non_human_grounding/<slug>.md` first then Wikipedia, `--choose N`
  always exits on out-of-range per decisions log #5.
- `personas/inputs/non_human_grounding/`: curated Octopus (Godfrey-Smith)
  + Whanganui (Te Awa Tupua Act) grounding files + README.

### G — Phase 0.5 redesign

- 4 voice-type-specific Pass 1a prompts (human / non_human_organism /
  non_human_system / fictional) replacing the single-file v3.10 template.
  Each carries Boddice rubric asks (period-vocabulary primary, 5-part
  world, §14 formative candidates).
- 4 voice-type-specific Pass 1b prompts (lighter touch; non-English
  scholarship + period-vocabulary rule).
- `run_phase0_1_research.py` routes via `_pick_template` on
  `vi["type"]` + `vi["subtype"]`.
- `pass_0b_dr_prompt.md` focused edits: Boddice §14 4-part replaces
  "ONE formative wound + lesson"; §15 character-in-period-vocabulary
  replaces Big-Five personality traits; enum values normalized.
- `dr_validation.py` relaxed per PB#9: no rigid 6-section markdown;
  keeps 15000-word total floor + persona-card-shape detection + soft
  per-thematic-area coverage check (warns at <4/6).

**Deferred from G (noted, not blocking):**

- Full 5-way decomposition of `pass_0b_dr_prompt.md` (1086 lines → per-type
  sub-templates). Current monolithic form with Jinja branches is functional;
  Boddice integration is inline.
- Pass 0b hybrid Jinja+LLM tailoring pass (PB#2 full implementation).
  Chunked Pass 1.1-1.6 already handles per-voice content variation;
  tailoring is optimization, not architectural requirement.

### H — Pass 2–6 generation prompts

- Pass 2 (Identity & Boundaries): `world` via Boddice §13 5-part rubric
  (ontological_furniture / available_pathe in original language /
  framework_for_difficulty / model_of_selfhood / anachronisms_to_avoid);
  `formative_experience` commits to one `formative_candidate` from Pass 1.1
  with §14 4-part shape; `character` via §15 period character-grammar (four
  humours / tripartite soul / nafs-stations / four Rasta virtues / Buddhist
  śīla) — NOT Big-Five adjectives. "Core wound + lesson" framing dropped
  throughout.
- Pass 4a (Voice): **critical "reference not display" guardrail added** —
  period-vocabulary is reference material for the voice's reasoning, NOT
  required output; scholarly-exhibition output fails Layer 2.
- Pass 3 / 4b / 5 / 6: header mapping doc updated (persona-card field ←
  merged_dossier chunk); `corpus_constraint` enum normalized.

### I — Pass 7 redesign

- Pass 7-pre extended with Boddice tag verification: emits
  `boddice_tag_flags[]` for missing `[experiential_reconstruction]` or
  `[projection_warning]` tags.
- NEW `persona_pass_7_anachronism.md`: TimeChara + RoleKE-Bench S²RD
  temporal-anachronism check. Cross-family evaluator (OpenAI o3 /
  Gemini, not Claude). Emits `anachronism_flags[]` + PASS/REVISION_NEEDED.
  **Prompt scaffolded; pipeline orchestration wiring deferred to Phase L
  integration.**
- Pass 7b renamed throughout: prompt files, pipeline code, Pass 7c user
  consumer, HANDOFF.md, docs/CURRENT_STATE.md, docs/AI_Assembly_Persona_
  Pipeline_v3_10.md, docs/AI_Assembly_Persona_Card_v2.md,
  docs/AI_Assembly_Voice_Pipeline.md, docs/LLM_CALL_INVENTORY.md,
  runtime/flows/voice/README.md → `smoke_test_chains`. Runtime
  `_REQUIRED_MEMBER_FIELDS` does not include this field → no runtime
  cascade.
- Pass 7c two-list output per decisions log #16: `banned_language[]`
  unchanged semantic role + NEW `projection_warnings[]` structured entries
  per `ProjectionWarning` schema.

### J — Derive

- Reads Boddice-shaped card fields explicitly (`speaks_from` ← world §13
  distillation; `core_commitment` + `activates_on` ← formative_experience
  §14 engagement_it_drives).
- **9-field Provocateur Profile contract** made explicit — plan/spec said
  "8 fields" but runtime validator at
  `runtime/flows/shared/io.py:_REQUIRED_MEMBER_FIELDS` enforces 9. Missing
  any field → `ValueError` at council_config load. Names + count locked.
- `stance_tendency` constrained to `{asserts | reframes | asks}` per the
  Provocateur Formulation stage's branching (free-text v3.10 behaviour
  would pass existence-validator but fail runtime branch).

### K — Cross-Persona QC (Phase 5) new flow

- `personas/phase_5_cross_persona_qc.py`: gates on 12 assembled cards; 3
  sub-tests (swap / blind_id / same_question_distinctiveness);
  cross-family evaluator (o3 → Gemini fallback, never Claude).
- Revision recommendations feed Pass 3 (constitution similarity) or Pass
  4a (voice/register similarity) re-runs with cross-card critique. Max 2
  rounds per voice.
- **Same-question sub-test is scaffolded**: picks a shared provocation,
  records structure; live 12-voice invocation + pairwise similarity
  scoring lands after Phase L proves the individual-voice pipeline.

---

## Phase L — first-voice end-to-end test (DEFERRED — NEXT SESSION)

**Pick: Plato.** Well-documented, philosophical, covers the common case
well. Validates the full rebuilt pipeline end-to-end.

**Expected cost: ~$50–70** across Pass 0a → Phase 0.5 → Pass 1 chunked →
Pass 2–6 → Pass 7 sub-passes → Derive. One mandatory manual human-in-the-
loop step at L.3 (paste into claude.ai).

### L.0 Preflight when you restart

```bash
cd /Users/aienvironment/Desktop/ai-assembly
git checkout phase-b-rebuild
git pull --ff-only
cd runtime && venv/bin/python -m pytest ingest/tests/ -v   # expect 29/29
```

Verify `.env` at repo root has ANTHROPIC_API_KEY, PERPLEXITY_API_KEY,
GOOGLE_API_KEY, and OPENAI_API_KEY (Pass 7a cross-model).

### L.1 Pass 0a on Plato

```bash
cd personas && venv/bin/python -c "
import sys; sys.path.insert(0, '.')
from run_pass0a_voice_config import main
main('Plato', wiki_url='https://en.wikipedia.org/wiki/Plato')
"
```

Expected: `$PROJECT_ROOT/inputs/voices/plato.json` with new schema fields
(`editorial_rationale: null`, `manual_grounding: <Wikipedia extract>`,
no `conference_context`); `plato_pass0a_review.md` with CURATOR ACTION
block alongside it. Fill in `editorial_rationale` by hand before L.2.
(Tier 3: `PROJECT_ROOT` defaults to sibling `../athens-2026/`; pass
`--project <path>` to override.)

### L.2 Phase 0.5

```bash
cd personas && venv/bin/python run_phase0_1_research.py "Plato"
```

Expected: fresh Perplexity + Gemini outputs. The Jinja-only Pass 0b
template renders to `$PROJECT_ROOT/inputs/dossiers/_dr_prompts/plato_dr_prompt.md`;
hybrid LLM tailoring (PB#2) fires automatically after the base render
and overwrites the tailored prompt in place.

### L.3 Manual Claude DR session ← HUMAN STEP

1. Open claude.ai with Opus 4.7 + Extended Thinking + Deep Research.
2. Paste contents of `plato_dr_prompt.md`.
3. Wait (~10–45 min).
4. Save the dossier as
   `$PROJECT_ROOT/runs/plato/01_research/claude_dr_dossier.md`.

Then validate:

```bash
cd personas && venv/bin/python scripts/validate_dr_dossier.py \
  "$AI_ASSEMBLY_PROJECT_ROOT/runs/plato/01_research/claude_dr_dossier.md"
```

### L.4 Chunked Pass 1

```bash
cd personas && venv/bin/python -c "
import sys; sys.path.insert(0, '.')
from run_pass_1_all import run_pass_1_all
run_pass_1_all(name='Plato', voice_type='human', voice_mode='philosophical')
"
```

Expected: 6 chunk outputs + `merged_dossier.json` with coherence_flags +
coherence_resolutions. Parallel; ~3-6 min wall.

### L.5 Phase 2–6 generation

Closed in cleanup-1: `run_persona_pipeline.py` already calls
`run_pass_1_all()` and feeds the chunked `merged_dossier.json` to Pass
2–6. Just run:

```bash
cd personas && venv/bin/python run_persona_pipeline.py "Plato"
```

### L.6 Phase 3 validation

Closed in cleanup-2: Pass 7-anachronism is wired between 7-pre and 7a
with revision-loop integration (flags translate to Pass 2 / 3 / 4a / 5
targets by `field_path` prefix). The full Phase 3 chain inside
`run_persona_pipeline.py` is now: Pass 7-pre (+ Boddice tag check) →
Pass 7-anachronism (o3 cross-family) → Pass 7a (multi-family) → revision
loop (max 2 rounds) → Pass 7b (smoke_test_chains) → Pass 7c
(banned_language + projection_warnings).

### L.7 Phase 4 Derive

Runs inside `run_persona_pipeline.py`. Emits `provocateur_profile.json`
+ `evaluation_rubric.json`. Verify the 9-field contract holds.

### L.8 Review output quality ← **HUMAN QUALITY GATE**

Read `$PROJECT_ROOT/runs/plato/persona_card_assembled.json`. Is it BETTER than
v3.10 Plato (at `_workspace/archive/runs/personas/plato/persona_card_assembled.json`)?

Checks:
- Does `formative_experience` use Boddice §14 4-part structure (not "one wound + lesson")?
- Does `world` reflect Boddice §13 5-part rubric?
- Is Pass 4a output period-vocabulary-INFORMED but NOT scholarly-display?
- Do `smoke_test_chains` make sense as build-time diagnostic (not runtime few-shot material)?
- Do `[experiential_reconstruction]` / `[projection_warning]` tags appear appropriately?
- Is `character` in period/tradition vocabulary (not Big-Five adjectives)?

### L.9 Iterate if needed

Quality issues feed back into Phase H (Pass 2-6 prompts) or Phase I
(Pass 7 prompts). Re-run affected phases, re-test L. If after 3
iterations the quality still regresses vs. v3.10, **stop and report** —
that's the explicit Phase L.8 stop-and-ask trigger.

### L.10 Commit L (once the quality gate passes)

```
feat(phase-b/L): first-voice end-to-end test — Plato rebuilt under Phase B

Complete pipeline run from new Pass 0a through Phase 4 Derive. Plato's
rebuilt card at $PROJECT_ROOT/runs/plato/persona_card_assembled.json; review
against _workspace/archive/runs/personas/plato/ baseline recorded in
$PROJECT_ROOT/runs/plato/rebuild_review.md.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```

---

## Phase M — verification + PR (AFTER L passes)

### M.1 All runtime tests pass

```bash
cd runtime && venv/bin/python -m pytest ingest/tests/ -v
```

**Already green at commit K** (29/29). Re-run after L lands.

### M.2 Schema round-trip

```bash
cd personas && venv/bin/python -c "
import sys; sys.path.insert(0, '.')
from schemas._entry import generate_json_schemas
for p in generate_json_schemas():
    print(p.name)
"
```

### M.3 No stale refs outside archive

```bash
grep -rn "worked_provocations" docs/ personas/ runtime/ --include="*.md" --include="*.py" | grep -v "_workspace/archive" | grep -v "smoke_test_chains"
grep -rn "conference_context.json" docs/ personas/ runtime/ --include="*.md" --include="*.py" | grep -v "_workspace/archive"
```

Both already run clean as of the pre-L cleanup commit.

### M.4 Push + PR

Branch already pushed. To open the PR:

```bash
gh pr create --base main --head phase-b-rebuild --title "feat: Phase B persona pipeline rebuild" --body "..."
```

Body outline in the prior version of this plan; regenerate from the commit
log on final open.

---

## Stop-and-ask rules (carry forward)

- Phase A/B/C Pydantic validation fails consistently → stop; schema design wrong.
- Phase C.5 conventions freeze reveals META gap → stop.
- Phase D chunks can't reuse frozen conventions → stop.
- **Phase L.8 first-voice review shows quality regression vs v3.10 Plato → stop; prompt tuning needed before Phase M.**
- Any runtime test fails at M.1 → stop; Phase B should not have touched runtime.
- M.3 grep finds unexpected stale refs → update before pushing.

---

## Out of scope

- Voice Pipeline Steps 1+2+3 (separate workstream).
- Runtime changes beyond the council_config.json sync (Phase B doesn't touch runtime code; we did rename one doc file in `runtime/flows/voice/README.md` for consistency, nothing else).
- Briefing v3.1 sentence on flagged-projection (Till/Matthias decision).
- §15 field renames beyond smoke_test_chains (defer to Card v3 sweep).
- Rebuilding voices 2–12 (separate sessions after Phase M merges; follow Phase L pattern per voice).

---

## Model + effort (next session)

**Opus 4.7 (1M context), medium effort** — same as the landed work. Phase L
is end-to-end integration + human quality review, both of which benefit
from 1M context (card under review + v3.10 baseline + ~6 chunk outputs).
After L.8 validates, M is mechanical and could drop to Sonnet.

---

*This plan is live; update it as Phase L progresses. When L passes and M
merges, move this file to `_workspace/archive/fix-plans/` as executed.*
