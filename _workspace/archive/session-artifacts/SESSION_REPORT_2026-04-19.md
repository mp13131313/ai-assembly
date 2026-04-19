# Session report — 2026-04-19 persona pipeline review

*Note: paths in this report reference the pre-reorganization layout (commit `d1b8a2c`).*

**Lead:** Claude Opus 4.7 (1M context).
**Scope:** Step-by-step review of the persona pipeline as preparation for the Phase B rebuild, paired with the integration analysis of a 5th baseline-research artifact (Boddice biocultural critique of Persona Card v2).
**Mode:** Review and design only. No code edits, no prompt edits, no schema edits. Output is plan documents, an updated index, and a moved research artifact.
**Branch:** `main`. Last upstream commit before this session: `2bff6c8` (docs: handoff — note conference_context sync + canonical-source convention).

---

## What this session produced

1. **`personas/notes/REBUILD_PLAN.md`** (new file). Living draft for the persona pipeline rebuild on the Phase B architecture — binding spec is `personas/notes/ARCHITECTURE_NEXT_PHASE_HANDOFF.md` §"Architectural decisions" 1–9 (referred to as `PB#1`..`PB#9` throughout the plan). Currently covers Phase 0 (Pass 0a + Pass 0b stubs), Phase 0.5 (Pass 1a + 1b + 0b + 1a-DR), and a Cross-cutting · Boddice integration block. Phases 1, 2, 3, 4, 5 are stubs to fill in as the review continues.

2. **`personas/notes/baseline_research/compass_artifact_wf-1e84f45b-…md`** (moved from `~/Desktop/`). The 5th baseline-research artifact: Rob Boddice's history-of-emotions framework applied voice-by-voice to the Card v2 schema.

3. **`personas/notes/baseline_research/README.md`** (updated). New 4-paragraph intro (was 2-paragraph), new 5th-file entry, updated use-case mapping, futures list extended with Boddice §15 deferred items.

4. **`personas/notes/SESSION_REPORT_2026-04-19.md`** (this file).

---

## What we did, in order

### Step 1 — Orient

Read `docs/SESSION_HANDOFF.md` in full + skimmed `docs/LLM_CALL_INVENTORY.md`, `docs/CURRENT_STATE.md`, `docs/AI_Assembly_Briefing_v3_1.md`. Confirmed baseline state: prior session's findings all FIXED with commit refs; no outstanding fixes warranted; persona pipeline at v3.10 working on 5/12 voices; Voice Pipeline not built; Athens ~3 weeks out.

### Step 2 — Walked Pass 0a (Voice Config)

Reviewed code, prompt, validator, sample voice configs ([`run_pass0a_voice_config.py`](../run_pass0a_voice_config.py), [`pass_0a_voice_config.md`](../flows/shared/prompts/pass_0a_voice_config.md), [`node0_validation.py`](../flows/shared/node0_validation.py), [`wikipedia.py`](../flows/shared/wikipedia.py), Plato + Ibn Battuta voice configs, `inputs/conference_context.json`).

Captured 7 plan items (see `REBUILD_PLAN.md` §"Phase 0 — Intake · Pass 0a"):
- Move "Why this voice is in the Assembly" out of Pass 0a (curation, not classification)
- Unify `wikipedia_extract` + `disambiguation_hint` → `manual_grounding`
- Decouple Pass 0a from full conference_context
- Domain-specific grounding for non-human voices
- Tighten `auto` / `proposed` confidence labels in the review doc
- Fix `--choose N` TTY inconsistency
- Make `conference_context` placeholder load-bearing (warn if model omits it)

### Step 3 — Drafted REBUILD_PLAN.md scaffold

Established conventions (tags `[schema]` / `[prompt]` / `[runner]` / `[ux]` / `[verify]`; status `☐` / `◐` / `☑`; Phase B link convention `→PB#N`). Placeholder sections for all phases. Cross-cutting block with 5 items: split conference_context.json; establish `personas/schemas/` directory; test-fixture lifecycle; cost / wall-clock budget; voice_mode 3-enum decision.

### Step 4 — Walked Phase 0.5 (Pre-DR Research)

Reviewed all three sub-passes plus the manual claude.ai gate ([`run_phase0_1_research.py`](../run_phase0_1_research.py), [`run_pass0b_dr_prompt.py`](../run_pass0b_dr_prompt.py), [`clients.py`](../flows/shared/clients.py) §`call_perplexity` + `call_gemini`, [`pass_0b_dr_prompt.md`](../flows/shared/prompts/pass_0b_dr_prompt.md) (1086 lines), [`perplexity_split.py`](../flows/shared/perplexity_split.py), [`dr_validation.py`](../flows/shared/dr_validation.py), Pass 1a + 1b prompt templates).

Captured 14 plan items across the three sub-passes (see `REBUILD_PLAN.md` §"Phase 0.5"). Headline items:
- Voice-type-specific Pass 1a + 1b prompts (today both hard-coded "human" — Octopus, Whanganui get the wrong-shaped scaffold)
- Decompose the 1086-line Pass 0b template into per-type sub-templates before Phase B's hybrid tailoring tries to operate on it
- Provenance header on the rendered DR prompt
- 1-retry on `call_perplexity` + `call_gemini`
- Per-section fallback in `split_dossier`
- Section-level word-count floors in `dr_validation.py`
- Plus an architectural seam flag: two paths for primary-text URLs into the pipeline (manual `voice_config.primary_text_sources` vs automated Pass 1c-extract)

### Step 5 — Reviewed 5th baseline artifact (Boddice biocultural critique)

User shared a new research dossier: "Reconstructing the world, not the feeling: Boddice's history of emotions for the Athens Persona Pipeline."

First-pass framing was wrong — claimed Boddice was on a "different axis" from Files 1–3. Corrected after user pushback: Boddice **extends** File 3's anti-projection program one ontological layer deeper (interrogates the categorical infrastructure used to organize the persona card itself, not just whether the persona is generic). Genuinely new contributions: the "core wound" critique, period-vocabulary requirements, two formal evidence tags, the field audit. Overlaps with File 3 on anti-anthropomorphisation, period-specific reasoning method, Indigenous representation specifics, anachronism handling.

Confirmed user's leverage intuition: Boddice's highest-leverage landing point is the research stage (Pass 0b template > Pass 1a/1b > Pass 2/4a synthesis > Pass 0a review-doc + voice_mode rethink > PB#7 conventions). The current Pass 0b template literally asks Claude DR for "the central biographical trauma — the ONE thing" — exactly the wound framing Boddice rejects.

### Step 6 — Final recommendation + plan section

Recommendation: treat Boddice as the content payload PB#2 carries (hybrid Jinja+LLM tailoring of the new Pass 0b template), plus PB#1 (voice-type-specific 1a/1b prompts), plus PB#7 (`_conventions.schema.json` evidence tags), plus Pass 2 + Pass 4a synthesis prompt revisions. Defer Boddice §15 field renames to a future Card v3 sweep. Defer Pass 7c reconciliation. Flag for Till/Matthias: a Briefing v3.1 sentence on flagged-projection-not-non-projection.

Initially proposed a v3.10 bridge patch for the 7 missing persona builds → corrected after user pushback. **No v3.10 patches.** All 12 cards (including the 5 with v3.10 partials) rebuild on Phase B per `ARCHITECTURE_NEXT_PHASE_HANDOFF.md` §"Other voices to build later"; existing v3.10 partials are archaeology. Captured the no-bridge rule explicitly in `REBUILD_PLAN.md` §"Cross-cutting · Boddice integration · Why no v3.10 bridge patch" so a future session doesn't re-suggest it.

---

## Memory updates this session

- **Refined** `project_persona_pipeline_rebuild.md` to remove the misleading "ship pre-Athens on v3.10" exception that kept tripping the bridge-patch reflex. New version makes explicit that all 12 cards (including 5 with v3.10 partials) rebuild on Phase B; no v3.10 prompt or schema patches are warranted for content reasons.
- **Added** `project_boddice_critique.md` — pointer to the 5th baseline artifact with integration framing.

---

## Files changed this session

- `personas/notes/REBUILD_PLAN.md` (new)
- `personas/notes/baseline_research/compass_artifact_wf-1e84f45b-0c9f-497a-84bc-88b7867c9a26_text_markdown.md` (moved from `~/Desktop/`)
- `personas/notes/baseline_research/README.md` (updated)
- `personas/notes/SESSION_REPORT_2026-04-19.md` (this file)

## Untracked files NOT touched this session

These were untracked when the session started; left for the user to decide:

- `docs/FRESH_REVIEW_2026_04_19.md`
- `personas/inputs/dossiers/_dr_prompts/ibn_battuta_dr_prompt.md`

---

## Pointers for the next session

The rebuild plan is half-walked. To continue the step-by-step review:

1. **Phase 1 — Research Merge (chunked per Phase B).** The heart of the architecture rewrite. Per handoff §B.1–B.6, design `personas/schemas/` + the first chunk schema (Pass 1.1 biographical → `life_scaffold.json` + `formative_candidates.json`). This is where Boddice's `formative_experience` rubric first gets baked into a schema rather than just a prompt.
2. **Phase 2 generation passes** (2, 3, 4a, 4b, 5, 6 + Coherence Threading). Boddice items affect Pass 2 (Identity & Boundaries — the `world` field) and Pass 4a (Voice).
3. **Phase 3 validation** (7-pre, 7a, 7b, 7c). Load-bearing per PB#6. Where Boddice's `[experiential reconstruction]` and `[projection warning]` tags get verified against the assembled card.
4. **Phase 4 derive + Phase 5 cross-persona QC** at the end.

After that, the cross-cutting block (which `voice_mode` enum, `conference_context.json` split, fixture lifecycle, cost budget) needs decisions before any code lands.

## What this session did NOT decide

- Whether to expand `voice_mode` enum (Boddice gives one reason; flagged in cross-cutting and in Boddice integration sections)
- Field-rename timing (Boddice §15 deferred to Card v3 sweep)
- Briefing v3.1 sentence on flagged projection (Till/Matthias decision)
- Whether to add Pass 7c-reconciliation as a blocking item
- The architectural seam between two paths for primary-text URLs
- Cost / wall-clock budget for the rebuild
