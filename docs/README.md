# docs/ — Pipeline specs and briefing documents

> **Read this first.** Not all files here are current. This index tells you which to trust.

## Current (authoritative as of 2026-06-01, post-Athens)

| File | Status | Notes |
|------|--------|-------|
| `AI_Assembly_Briefing_v3_1.md` | **Current** | Project source of truth. Supersedes Briefing v2 (deleted). Adds prosumer/infrastructure second-order provotype condition. |
| `AI_Assembly_Persona_Card_v2.md` | **Current** (v2 schema; v2.1 amendments 2026-04-27) | 35-generated + 2-continuity-null + metadata-block schema. v2.1 amendments section near top covers FU#41 chat artifact, FU#49 universal patterns, Boddice tag preservation, Position B vs C, updated `metadata` block. |
| `AI_Assembly_Persona_Pipeline_v4.md` | **Current** (2026-04-27) | Persona build pipeline v4 — what shipped. Replaces v3.10. Reflects arch-03 chunked merge (Pass 1.1–1.7), Phase B per-voice layout, Tier 3 separation, Pass 6.5-clean (FU#33 P1), FU#2 chunked Pass 7-pre, FU#13 linear patcher, FU#41 chat artifact, FU#49 universal patterns. v4 prompt-architecture extensions (2026-05-04 sacred-grammar-deployment-limit + 2026-05-05 transmission-witness register-overrides) tracked in `_workspace/planning/voices/OPEN_ITEMS.md` §24 + §28. |
| `AI_Assembly_Researcher_Pipeline.md` | **Current** | Researcher extraction and grouping (v3). Validated on dev_msc_test + ran in all three Athens nights. |
| `AI_Assembly_Provocateur_Pipeline.md` | **Current** | Triage, selection, formulation, packaging (v2). Validated on dev_msc_test + ran in all three Athens nights. Deployment-context block (`cbcdf82`) landed pre-Athens. |
| `AI_Assembly_Transcription_Pipeline.md` | **Current** with caveat | v2.1. Audio flow current. The reflection-handling §7 is **stale** — reflections come in as vendor JSON, not audio; use `runtime/scripts/reflections_to_session_package.py` (v2.2 changelog notes this). |
| `AI_Assembly_Voice_Pipeline.md` | **Current** (v2.1 2026-05-01) | Steps 1+2+3 + validation + continuity end-to-end. Field-routing matrix for all 36 generated card fields. Step 3 SKIPPED for Athens per OPEN_ITEMS A1 (Option A); module preserved for post-Athens re-add. **Voice-stage deployment_context retired as superseded 2026-06-01** — see `_workspace/planning/runtime/DESIGN_voice_deployment_context.md`. **Ran in all three Athens nights.** |
| `AI_Assembly_Editor_Pipeline.md` | **Current** (v2.1 with deployment_context override) | Tim Leberecht as 13th Assembly member. Dossier-by-theme architecture. Marathon-distance issue numbering. Shipped 2026-05-03 PM (commit `fc5c2fb`); deployment_context override mechanism added 2026-05-07. **Composed 13 dossiers across Athens Nights 1–3.** |
| `AI_Assembly_Runtime_Lifecycle.md` | **Current** (v1 2026-05-02) | What happens during an Athens night, end to end. Stage-by-stage anatomy (trigger, reads, writes, sentinel), full filesystem layout, cross-night threading, failure modes, manual intervention. Authoritative operational picture. |
| `AI_Assembly_Infrastructure.md` | **Current** (v1 draft 2026-05-02) | Athens 2026 deployment spec. Three reasons for VM (ingest + safety + operator-detachment); three systemd units; Hetzner CX22 + Ubuntu 24.04; PROJECT_ROOT = clone of athens-2026 private repo. Supersedes archived `Infrastructure_Setup.md`. **VM not actually provisioned for Athens 2026 — operator ran from laptop.** |
| `AI_Assembly_Frame_Concept_v1.md` | **Current** (with caveat) | Frame layer (broadsheet / microsite / Substack / closing show). Voice Pipeline produces artifacts that the frame layer wraps. Strip rule needs to be voice-register-conditional per FU#61 finding — see `_workspace/planning/runtime/OPEN_ITEMS.md`. |
| `AUDIENCE_BRIEF.md` | **Current** (refreshed 2026-04-26 for athens-2026 deployment) | Audience characterization + contributors-vs-audience distinction. |
| `LLM_CALL_INVENTORY.md` | **Current** (rewritten 2026-04-27) with caveat | Updated for arch-03 chunked merge, Pass 0b tailor, Pass 6.5-clean, Pass 7-pre 3-stage (FU#2), Pass 7-anachronism, Pass 7a-FIX linear patcher (FU#13), FU#41 chat builder. 5-model fallback ladder for Pass 7-anach + Pass 7a (gpt-5.4 high → gpt-4.1 → o3 → gpt-4o → Gemini 2.5 Pro). **Does not yet include Voice Pipeline + Editor Pipeline calls** — both shipped post-write; refresh pending. |

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
