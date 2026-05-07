# Onboarding — planning folder index

**Living document.** Thin shell pointing at the two workstream subfolders + the cross-cutting rules that apply across both. The substantive onboarding content lives in the subfolder ONBOARDINGs.

---

## What this project is

A provotype for the **World Beautiful Business Forum** AI Democracy Marathon, Athens, **May 7–10, 2026**. Ten non-human voices (a river, an octopus, Plato, Hannah Arendt, and 6 others) read the day's human panel transcripts overnight and produce written responses — provocations, queries, reflections — that re-enter the human conversation the following morning via Substack read-throughs.

Civic-design artifact, not a product. Visible construction is a feature.

For project-wide context (filesystem layout, Tier 3 separation, two venvs, cross-repo handoff, where specs live, orientation reading order): **`code/CLAUDE.md`**.

---

## Two workstreams

The work splits cleanly into two parallel subfolders:

| Subfolder | What it covers | Owner thread |
|---|---|---|
| **`runtime/`** | overnight pipeline: transcription, researcher, provocateur, voice pipeline (steps 1+2+3 + validation + continuity), publish, downstream (editor / broadsheet / microsite / Substack / closing show / Day 4 goodbye) | runtime thread |
| **`voices/`** | persona-card pipeline: voice configs, deep research, chunked merge, generation passes, validation, derive, card assembly. The pre-Athens build that produces the cards runtime consumes | persona thread (also called "voices" thread) |

Each subfolder has the same shape:

```
<subfolder>/
├── HANDOFF*.md      session-state-of-the-moment (dated)
├── ONBOARDING.md    durable scaffolding (orientation, architecture, common operations)
└── OPEN_ITEMS.md    authoritative open-items tracker (gating decisions, blockers, hygiene)
```

**For runtime work:** read `runtime/ONBOARDING.md` first, then `runtime/OPEN_ITEMS.md`, then the latest dated `runtime/HANDOFF_*.md`.

**For voice-build work:** read `voices/ONBOARDING.md` first, then `voices/OPEN_ITEMS.md`, then `voices/HANDOFF.md`.

---

## Cross-cutting tracker (frozen)

**`FOLLOW_UPS.md`** at this folder root is the **frozen historical ledger** of FU#1–62 (as of 2026-05-01). Existing FU# references in code, commits, prompts, and docs resolve to entries there — no new entries are added.

**For NEW items going forward,** file in the relevant subfolder OPEN_ITEMS in the appropriate section:
- Runtime: `runtime/OPEN_ITEMS.md` (sections A gating / B Athens-blocking / C hygiene / E docs pending)
- Voices: `voices/OPEN_ITEMS.md` (per its structure)

Cross-cutting items file in BOTH subfolder OPEN_ITEMS with mutual cross-references. Cross-cutting **rules / calibration** (not items) file in this doc's §"Cross-cutting DON'Ts" or §"Cross-cutting calibration".

No new FU# numbering. See `code/CLAUDE.md` §"Planning / tracking conventions" for the full workflow.

---

## Cross-cutting DON'Ts (apply in both workstreams)

Standing rules. Operator-level ones come from `~/.claude/CLAUDE.md` (global) and the project's calibration history.

- **No `--no-verify` / hook bypass.** If a hook fails, fix the underlying issue.
- **No push to `origin/main`** without explicit operator confirmation.
- **No commits with `--allow-empty`.**
- **No xattr / ACL / system-attribute modification** without explicit operator instruction.
- **No deletion of athens-2026 contents** without explicit operator confirmation per item.
- **No real-person names in the 4 deployment-context JSONs** at `<PROJECT_ROOT>/`: `conference_facts.json`, `audience_profile.json`, `panel_roster.json`, `council_config.json`. Use generic descriptions ("a former PM," "a leading cognitive-warfare theorist").
- **No Plato re-run without explicit ask.** Card shipped per chat-test 2026-04-26.
- **No Dostoevsky full re-run.** Phase 2 + G10 Derive re-fire on disk in `~/Desktop/AI Assembly/archive/phase-l-dostoevsky/` (relocated from `projects/` 2026-05-01; voices shipped to athens-2026).
- **No Opus 4.6 for any DR section.** Use Opus 4.7 across §1-§6. (Older "§1-§5 use 4.6, §6 uses 4.7" spec is stale.)
- **No hand-authoring voice_configs bypassing Pass 0a.** If review disagrees, edit and re-run Pass 0a.
- **Reflections are vendor JSON, not audio.** Stage 0 transcription does not apply. Use `runtime/scripts/reflections_to_session_package.py` to convert vendor reflection JSON → session_package shape; then `vendor_intake.py` validates and lands at `01_transcription/<session_id>/`. (Spec: each `reflections[i]` becomes one turn, `speaker="Participant {i+1}"`, `role=audience`, `confidence=high`.) The Transcription Pipeline doc at `docs/AI_Assembly_Transcription_Pipeline.md` still describes a stale audio-flow for reflections; ignore that and use the preprocessor.
- **ASK what the editor's deployment_context is for non-canonical run dirs.** When firing `editor_flow.py` on a run dir whose name is NOT `athens_night_<N>` (the production naming) — e.g. `preconference_wbbf_programme_*`, `reflections_demo_*`, anything operator stages for a special-purpose run — check whether `<run_dir>/_dossier_deployment_context.md` exists. If absent AND the run's content type is unclear (panel transcript? programme blurbs? participant reflections? operator-seeded markdown?), **ASK the operator before firing** what the run is reading and what register Tim should compose in. The default editor contract assumes "the panels happened today and you compose the morning paper" — if that's not the case (e.g. a pre-conference programme read), Tim will stage fictional panel events that did not occur. Empirical evidence from wbbf26 v1 dryrun (2026-05-07): default contract produced "RECOGNISED, NOT GRANTED / The vote found a flip" headlines staging a vote that didn't happen; deployment_context override fixed this completely. See `runtime/flows/editor/dossier_generation.py` for the override-file mechanism + `runtime/flows/shared/prompts/editor_dossier.md` for the prompt-side spec of the field.
- **Never optimize FOR chat-test.** Voice Pipeline (runtime) consumes specific card fields via API per-step; that's the production target. Chat-test is a development feedback instrument.

Subfolder-specific DON'Ts live in the respective `runtime/ONBOARDING.md` and `voices/ONBOARDING.md`.

---

## Cross-cutting calibration

- **Operator preference is direct.** When pushed back ("are you sure?", "reason through each again"), the instinct is usually right even when work has been declared done. Re-investigate before bulldozing.
- **Provotype framing is load-bearing.** Civic-design artifact for WBBF Athens 2026, not a product. Visible construction is a feature.
- **Athens needs full runtime stack ready, not just cards.** When recommending build-side improvements (LLM-as-judge, FU#50(1) Pydantic enforcement, FU#42 split-card, etc.), check whether they delay runtime work that's already on the critical path. Surface runtime gaps proactively.
- **Voice Pipeline first, chat-test as instrument.** Voice Pipeline (runtime) consumes specific card fields via API per-step; that's the production target.
- **Model/effort economy.** Per-voice pipeline operation + chat-test paste-and-assess is Sonnet-shaped. Architectural decisions and complex code reading are Opus-shaped. Default to Sonnet 4.6 for execution, escalate to Opus 4.7 for design or cross-file reasoning.
- **Defaults to strips, defer additions, validate empirically.** Adding instructions has costs (prompt-density, instruction-competition, performance tics). Stripping doesn't. Per 2026-04-28 revert lesson.

Subfolder-specific calibration (e.g., "always `--skip-validation` for dryrun work" — runtime-specific) lives in the respective `<subfolder>/ONBOARDING.md`.

---

## What this folder root contains (besides the subfolders)

| File | Purpose |
|---|---|
| `ONBOARDING.md` | this doc — index + cross-cutting rules |
| `FOLLOW_UPS.md` | frozen historical ledger of FU#1–62 (cross-cutting reference; no new entries) |

The 6 dated persona-thread handoffs (`HANDOFF_2026_04_27.md … _NIGHT.md`) and `BRIEF_OPUS_4_7_THINKING_AUDIT_2026_04_29.md` were archived 2026-05-01 to `_workspace/archive/voices_consolidation_2026_05_01/` (commit `82e5a65`). Going forward, voices session-state lives in `voices/HANDOFF.md` (replaced each session).

**Sessions 2026-05-05 evening + 2026-05-06 archive sweep:** six superseded planning docs (their content migrated into authoritative `voices/OPEN_ITEMS.md` sections §27–§31 + status headers added before move) were archived to `_workspace/archive/session-artifacts/`: `WHANGANUI_V2_PLAN_2026-05-05.md`, `WHANGANUI_V2_ROUND0_WALKTHROUGH_2026-05-05.md`, `MEMO_2026_05_05_voice_temporal_stance_assembly_fiction.md`, `MEMO_2026_05_05_length_cap_card_surgery_after_runtime_fix.md`, `MEMO_2026_05_01_recurrence_patterns_from_legitimacy_test.md`, `CLAUDIA_PINCHBECK_PERSONA_PREP_2026-05-03.md`. Active `voices/` planning docs after sweep: `HANDOFF.md`, `ONBOARDING.md`, `OPEN_ITEMS.md`, `MARLEY_READINESS_PARAGRAPHS_2026-05-04.md` (active operator-refinement work), `VIDEO_TEAM_CONSTRAINT_SHEET_2026-05-04.md` (durable production constraint sheet), `TIM_LEBERECHT_CARD_REVIEW_2026-05-05.md` (recent reference review).

---

## Doc hygiene — what lives where, what gets archived

To keep this folder load-bearing rather than archival, follow these rules. They apply to both workstream subfolders.

**Stays here:**

- **One current HANDOFF per workstream.** Append within the day; spawn a new dated HANDOFF only when starting a fresh day's work. Within `runtime/`, name it `HANDOFF_<YYYY_MM_DD>.md`. Within `voices/`, single rolling `HANDOFF.md` is fine (different convention, both work).
- **OPEN_ITEMS.md** (per workstream) — authoritative, durable.
- **ONBOARDING.md** (per workstream + this root one) — durable; updates are surgical, not append-only.

**Gets archived (move to `_workspace/archive/session-artifacts/`):**

- **Yesterday's HANDOFF** when today's HANDOFF supersedes it via "Predecessor handoff:" header. Keep only the latest in `_workspace/planning/<workstream>/`.
- **Design docs** (e.g., `*_DESIGN_*.md`) once the thing they spec exists. Their content migrates to: implementation + a lifecycle/operations doc + an OPEN_ITEMS entry. The design doc itself becomes historical context.
- **One-off briefs / audits** (`BRIEF_*.md`, `*_AUDIT_*.md`) once their findings have been actioned.

**Stays under `docs/` (not here):**

- Canonical pipeline specs.
- Operational/lifecycle docs.

**Trigger:** when proposing a new doc, ask first whether the content can live in OPEN_ITEMS, ONBOARDING, or an existing pipeline doc. Default is no new top-level doc. Spec → archive once shipped.

---

## When this doc goes stale

- After workstream restructuring (third subfolder added, naming convention changes): update §"Two workstreams" + add new pointers.
- After new cross-cutting DON'Ts emerge from session learnings: append to §"Cross-cutting DON'Ts."
- After new cross-cutting calibration is articulated: append to §"Cross-cutting calibration."

If a rule is subfolder-specific, it goes in the subfolder ONBOARDING. Only genuinely-cross-cutting content lives here.

---

*End of planning/ONBOARDING.md (index version, 2026-05-01).*
