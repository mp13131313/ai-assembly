# docs/ — Pipeline specs and briefing documents

> **Read this first.** Not all files here are current. This index tells you which to trust.

## Current specs — which to trust

**Last full check against code: 2026-09-28** (staleness sweep, `_workspace/planning/doc_infrastructure_backlog.md`). Re-check monthly or after any large batch of changes (`_workspace/planning/WAYS_OF_WORKING.md` §8). **Which model runs which step is never a spec's job:** it lives in `../model_routing.json`.

| File | Status | Last checked vs code | Notes |
|------|--------|---------------------|-------|
| `AI_Assembly_Briefing_v3_1.md` | **Current** | 2026-09-28 | Project source of truth (target state). |
| `AI_Assembly_Persona_Card_v2.md` | **Current** | 2026-09-28 | v2 schema + v2.1 amendments. 36 generated + 2 continuity + metadata (see `personas/CROSS_REPO_CONTRACT.md`). §H family of forms: BUILD decided, not built yet (FU#55). |
| `AI_Assembly_Persona_Pipeline_v4.md` | **Current** | 2026-09-28 | Persona build pipeline v4. The manual Deep Research step's model is set in `model_routing.json` (voices OPEN_ITEMS §36). |
| `AI_Assembly_Researcher_Pipeline.md` | **Current** | 2026-09-28 | Extraction and grouping (v3); ran all three Athens nights. |
| `AI_Assembly_Provocateur_Pipeline.md` | **Current** | 2026-09-28 | Triage, selection, formulation, packaging (v2); ran all three Athens nights. |
| `AI_Assembly_Transcription_Pipeline.md` | **Current** with caveat | 2026-09-28 | v2.1, audio flow, including the C49 speaker-ID auto-passthrough. **Caveat:** the reflection-handling §7 is stale. Reflections arrive as vendor JSON; use `runtime/scripts/reflections_to_session_package.py`. |
| `AI_Assembly_Voice_Pipeline.md` | **Current** | 2026-09-28 | Steps 1–3, validation, continuity; Step-1 validation off by default (C28), Step-2 validator is the operator gate. Cost and timing measured from the Athens runs (2026-09-28). |
| `AI_Assembly_Editor_Pipeline.md` | **Current** with caveat | 2026-09-28 | v3. Tim Leberecht as editor; dossier-by-theme; the shared dossier index and its merge rule. Dossier Shape + Output Schema rewritten 2026-09-28 to the shipped dossier fields, verified against `editor_dossier.md`, `dossier_generation.py` and all 13 published Athens dossiers (backlog row #24). **Caveat:** other sections still describe the pre-ship design (In Brief column, newspaper masthead and issue numbers, older per-call input lists, parts of the microsite render contract); the spec's v3 changelog lists them. |
| `AI_Assembly_Runtime_Lifecycle.md` | **Current** | 2026-09-28 | What happens during a night, end to end. |
| `AI_Assembly_Infrastructure.md` | **Current** (v1 draft) | 2026-09-28 | Deployment spec. The VM was never provisioned for Athens; the operator ran from a laptop. |
| `AI_Assembly_Frame_Concept_v1.md` | Not re-checked | 2026-06-01 | Frame layer (broadsheet / microsite / Substack / closing show). The strip rule needs to be voice-register-conditional (FU#61). |
| `AUDIENCE_BRIEF.md` | **Current** | 2026-09-28 | Audience characterization. |
| `LLM_CALL_INVENTORY.md` | **Current** (generated from code 2026-09-28) | 2026-09-28 | Every LLM call site in both pipelines with its parameters and its `model_routing.json` step key. Generated doc: regenerate when calls change (`WAYS_OF_WORKING.md` §6). |

## Archived / stale

| File | What's stale |
|------|-------------|
| `_archive/AI_Assembly_Persona_Pipeline_v3_10.md` | Superseded by v4 (2026-04-27). Body retained as historical record (changelog from v2.0 → v3.10 is preserved there). |
| `_archive/AI_Assembly_Voice_Pipeline_v1_partial.md` | Superseded by v2 (2026-04-28). v1 covered Steps 1+2 conceptually only; omitted Step 3; was stale on `voice_temporal_stance`, family-of-forms, tense discipline, and 10-voice panel. Body retained for historical context. |
| `_workspace/archive/specs/AI_Assembly_Architecture_v1.md` | Describes n8n orchestration; actual is pure Prefect. 2-step Voice Pipeline; actual has 3 steps. 2 nights; actual has 3 + Day 4 goodbye. Missing closing-show pipelines, Matrix A/B, Substack delivery model. |
| `_workspace/archive/specs/AI_Assembly_Infrastructure_Setup.md` | Describes rclone/Drive mount + n8n Docker + file watcher; actual is FastAPI upload + pure Prefect + status.json state machine. Superseded by `AI_Assembly_Infrastructure.md`. |

## Removed from canonical specs (2026-06-01)

| File | Where it went |
|------|--------------|
| `CURRENT_STATE.md` | **Archived** to `_workspace/archive/2026-04-27_current_state_snapshot/CURRENT_STATE.md`. Its function — current-state snapshot + gap analysis + architectural rationale — is now split across `STATE.md` (canonical current-state source), `CLAUDE.md` (scaffolding + Athens status pointer), `_workspace/planning/runtime/OPEN_ITEMS.md` (open items + TL;DR), and the per-spec changelog sections. The 2026-04-27 snapshot was pre-Athens and ~60% wrong post-Athens; better to remove than to chase. |

When archived/stale docs conflict with `AI_Assembly_Briefing_v3_1.md`, `CLAUDE.md`, or the code in `runtime/`+`personas/`, trust the current docs and the code.

## Also in `docs/` (preserved grounding + design)

- **`docs/research/`** — preserved grounding material (5 Deep Research compass artifacts). Not deletable. When you want to know *why* the pipeline is designed the way it is, look here. (Relocated from top-level `research/` to `docs/research/` 2026-05-01 to consolidate documentation under one tree.)
- **`docs/design/`** — conceptual design documents that ground the architecture, distinct from pipeline specs:
  - `AI_Assembly_DesignPrinciples.md` — project-wide design principles
  - `Nine_Modes_of_Implication.md` — typology of voice→audience implication modes
  These predate Athens and inform the Briefing + pipeline specs; consult when auditing methodology.
- **`docs/references.md`** — pointers from production specs into `docs/research/` and into archived planning docs.

## What's NOT in `docs/`

- **Current-state snapshot** — see `STATE.md` at the repo root (canonical current-state source) + `CLAUDE.md` (scaffolding).
- **`_workspace/planning/`** — forward-looking design + active workstream trackers. Two-workstream structure (`runtime/` + `voices/` subfolders) + thin root index + frozen historical FU# ledger. See `CLAUDE.md` §"Planning / tracking conventions" for the full workflow.
- **`_workspace/archive/`** — historical record (executed fix plans, stale specs, session artifacts, archived CURRENT_STATE). Out of scope for code reviews by default.
