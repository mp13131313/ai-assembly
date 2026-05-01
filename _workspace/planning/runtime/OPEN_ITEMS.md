# Runtime — open items, authoritative

**Date created:** 2026-05-01
**Scope:** Everything pertaining to the runtime pipeline (`runtime/flows/*` + downstream Athens-facing surfaces) that is open. Includes items from the Step 3 redesign session, FU#61/62 work, prior FOLLOW_UPS.md entries, prior HANDOFF docs, OPEN_ITEMS_VOICE_PIPELINE_2026_04_29.md, and the PIPELINE_DOWNSTREAM_DESIGN architectural doc.
**Replaces (for runtime scope only):** OPEN_ITEMS_VOICE_PIPELINE_2026_04_29.md (which can be archived). Persona-pipeline FUs in FOLLOW_UPS.md remain there as the persona thread's source of truth.
**Authority:** This is the runtime authoritative truth going forward. Changes to runtime scope land here.

---

## What "runtime" means here

`runtime/flows/*` — the overnight pipeline:

```
Stage 0  Transcription      transcription_flow.py
Stage 1  Researcher          researcher_flow.py
Stage 1b Provocateur         provocateur_flow.py
Stage 2  Voice Pipeline      voice_flow.py + voice/{step1,step1_validation,step2,step3,continuity,card_assembly,publish}.py
Stage 3  Publish             publish_flow.py
```

**Plus downstream of Voice Pipeline** (most not yet built):

```
Editor / Frame layer        editor_flow.py (NOT BUILT)
Edition Pipeline             edition_flow.py / broadsheet (NOT BUILT)
Microsite                    static site consumer (NOT BUILT)
Substack draft pass          substack_flow.py (NOT BUILT)
Closing show                 theme ID + Matrix mapping + video (UNSPECIFIED)
Day 4 goodbye                (UNSPECIFIED)
Render layer                 Marley → Suno; Octopus → shader (PARTIAL)
Admin console                operator infra (NOT BUILT)
```

**Out of scope here:** persona pipeline (`personas/`), card-build internals (Pass 1-7), per-voice persona-card content. Those live in FOLLOW_UPS.md.

---

## TL;DR — runtime state, May 1 2026

**Built and validated:**
- Voice Pipeline Steps 1+2+3 + validation + continuity + publish (commits `180a18f`, `aca0e4c`, `fa88db7`, `ddec38a`, plus 04-29/04-30 hardening)
- Validated end-to-end on dryrun #2 (Plato solo) + dryrun #4 (Plato + Cleopatra dual)
- FU#61 voice-card quality_criteria pattern landed on Cleopatra (athens-2026 commit `c89d186`) + Dostoevsky (`5088d67`); persona Pass 4b prompt addition committed (`91947a7`) so future card builds get the pattern automatically

**Built but never exercised:**
- `publish_flow.py` end-to-end against real Researcher/Provocateur outputs (only against hand-authored briefings)

**Currently being redesigned:**
- Step 3 — original FU#49E correspondence-shape produces letter-back artifacts; user dropped that framing; B+ recommended (metadata + optional postscript) but no decision yet

**Designed conceptually, not yet built:**
- Editor / Frame layer (the missing connective tissue between Voice Pipeline and audience surfaces)
- Microsite, broadsheet, Substack draft pipelines
- Closing-show pipelines, Day 4 goodbye, render layer for non-text artifacts, admin console

**Spec/impl divergences worth knowing:**
- Voice Pipeline validation regen-on-flag is unimplemented (FU#62) — diagnostic flag only
- Validation wall-time is ~20-40 min/night actual vs spec's 3-5 min claim

---

## Section A — Gating design decisions (open, blocking implementation)

These need operator answers before implementation can proceed.

### A1. Step 3 architectural shape 🔴 GATING

**Question:** what does Step 3 produce, and how does cross-voice deliberation become visible?

**Four options on the table:**

| Option | Step 3 output | Artifact body | Cross-voice visibility | Layer 1 risk | Cost/night |
|---|---|---|---|---|---|
| **A** Skip entirely | (no Step 3) | Step 2 only | Editor narrates third-party | None | $0 |
| **B** Metadata-only | engaged_peers[] notes | Step 2 unchanged | Metadata footer + editor + Substack | None | ~$5 (Sonnet read-only) |
| **B+** Metadata + postscript | engaged_peers[] + optional postscript paragraph | Step 2 + postscript appended | Postscript visible in artifact + metadata + editor + Substack | None (body unchanged) | ~$10-20 |
| **C** Full body regeneration | engaged_peers[] + amended artifact | Regenerated | Visible in artifact body | Real (regen risks Step 2 calibration) | ~$50 (Opus + thinking) |

**Briefing line 177 (load-bearing):**
> *"Each voice reads the artifacts of the other voices it shares at least one theme with… The voice decides whether to amend: sharpen a disagreement, integrate a stronger framing, or leave its artifact unchanged. Amendments are visible — they reference the other voice so the amendment reads as responsive. A metadata flag records who amended in response to whom."*

**Briefing line 179:**
> *"This is where the Assembly's collective character is constituted overnight. Constrained — voices respond at the artifact layer, not the reasoning layer, and only within shared-theme territory — but real deliberation. The published set is responsive to itself."*

**Recommendation: B+** (metadata + optional postscript). Reasons:
- Voices DO read each other and decide (briefing 177 honored at the reading level; "leave artifact unchanged" is the briefing's third valid outcome and becomes the default body-state)
- The postscript IS visible engagement — voice's response to peers, in voice's own grammar (briefing 177's "amendments are visible" satisfied without putting Step 2's careful calibration at regen risk)
- Layer 1 surface protected (body untouched; postscript is additive)
- Honest about temporal sequence (artifact written first, postscript added after reading peers)
- Cheap (~$10-20/night vs C's ~$50)

**Last operator query:** *"Does B+ reach what you were after with the catch? Or does it still feel structurally off?"* — awaiting answer.

**Files affected when this decides:**
- `runtime/flows/shared/prompts/voice_step3_amendment.md` — full rewrite (drop FU#49E correspondence framing)
- `runtime/flows/voice/step3_amended_artifact.py` — output schema overhaul (engaged_peers replaces amendments)
- `runtime/flows/voice_flow.py:_build_responded_to_graph` — refactor to derive from engaged_peers
- `docs/AI_Assembly_Voice_Pipeline.md` — Step 3 section rewrite
- One-shot migration script for old `amendments[]`-shape Step 3 files in dryrun directories

---

### A2. Editor / Frame layer architecture (decisions A-F from PIPELINE_DOWNSTREAM_DESIGN)

**Question:** does an Editor / Frame layer exist as a separate pipeline pass, and what does it produce?

The PIPELINE_DOWNSTREAM_DESIGN doc surfaced six decisions:

| | Decision | Recommendation | Status |
|---|---|---|---|
| **A** | Approve a separate editor / frame pipeline pass between Step 3 and audience surfaces | **Yes** — three converging needs (Layer 1 for hard-form voices, title/subtitle generation, cross-voice contrast text) | NOT DECIDED |
| **B** | Editor runs per-voice (one call per artifact) producing title + subtitle + curatorial preamble + pull-quotes + cross-voice contrast block | **Yes** — voice-register awareness is local; broadsheet does deterministic assembly | NOT DECIDED |
| **C** | AI-drafted, operator-polished (~5 min/artifact, ~2.5 hr/night for editorial pass) — not pure AI, not pure human | **Yes** — matches existing Substack pattern; realistic for 1-person editorial budget | NOT DECIDED |
| **D** | Microsite strip rule becomes voice-register-conditional (curatorial preamble appears for hard-form voices, stripped for dialogue voices) | **Yes** — already surfaced as FU#61 finding | NOT DECIDED |
| **E** | Cross-voice visibility distributed: microsite footer (structural reference), broadsheet (typographic contrast), Substack (narrative — primary carrier) | **Yes** — surfaces complement; no single carrier | NOT DECIDED |
| **F** | Build order: editor design first, then Step 3 redesign against editor's input contract | **Yes** — Step 3 output shape is constrained by what editor consumes | NOT DECIDED |

**A is the gating decision** — if no editor layer, Step 3 collapses to either correspondence (FU#49E) or no cross-voice visibility, and Frame Concept's three-surface architecture loses connective tissue.

**Important nuance from FU#61:** the persona thread explicitly RULED OUT the museum-label-frame approach for Layer 1 ("the form historically had public-readability built in… frame layer remains useful for cross-voice surfacing, chrome, and the rest of what Frame Concept doc scopes; it's not load-bearing for Layer 1 carry once the criterion is in place"). This **reduces** one of three editor-layer justifications: voice-card patches now carry Layer 1 directly. The editor layer is still needed for **#2 title/subtitle generation** and **#3 cross-voice contrast text** — those don't go away. But the "Layer 1 for hard-form voices" pillar is replaced by FU#61 Pass 4b prompt-driven approach (already shipped on Cleopatra + Dostoevsky).

**Files implicated when this decides:**
- New: `runtime/flows/editor_flow.py` + `runtime/flows/voice/editor.py` (~per-voice pass)
- New: `runtime/flows/shared/prompts/editor_*.md` (per-register templates)
- Updates: `docs/AI_Assembly_Frame_Concept_v1.md` (strip rule voice-register-conditional; add the editor layer)
- Updates: `docs/AI_Assembly_Voice_Pipeline.md` (downstream consumer reference)

---

### A3. FU#62 — validation regen-on-flag: implement or update spec? 🔵

**Status:** Filed in FOLLOW_UPS.md FU#62; needs decision.

**Background:** Voice Pipeline spec (`docs/AI_Assembly_Voice_Pipeline.md` §"Regeneration policy") promises *"First failure: regenerate the Step 1 call with the validator's critique appended… Second failure: ship the regenerated output AND flag in the run-level manifest."* Implementation reality: orchestrator collects flagged results into `validation_failures[]`, hardcodes `regen_count: 0`, proceeds to Step 2 unchanged. **No regen ever fires.**

**Two paths:**
- **A — Implement regen** (~half-day's work). Orchestrator reads validation result; if flagged, re-runs Step 1 with critique appended; re-validates; ships regen + flag if second pass fails. Makes validation autonomous.
- **B — Update spec** (~30 min doc patch). Match implementation: validation = diagnostic flag only. Pair with Athens validation policy: ON Night 1 only, OFF Nights 2/3.

**Recommendation: B (spec update).** Operator presence at Athens makes morning-review the natural correction loop; regen has limited additional value before Athens; matches "validation Night 1 only" policy which already aligns with diagnostic-only framing.

---

### A4. Frame Concept doc revision (FU#61 propagation + editor layer)

**Status:** Open.

`docs/AI_Assembly_Frame_Concept_v1.md` was written before:
- FU#61 finding that strip rule needs to be voice-register-conditional (curatorial preamble for hard-form voices)
- The realization that an editor layer is needed (a layer not in the current Frame Concept doc; Frame Concept assumed broadsheet + Substack pull-quotes were sufficient frame mechanisms)
- The Cairo-encounter pattern argument (museum label as the right inheritance for hard-form voices, not journalism-genre headline)

**Revision scope:**
- Strip rule becomes voice-register-conditional (artifact pages for hard-form voices include curatorial preamble; dialogue-form voices stay stripped per current spec)
- Add editor / frame layer as a pipeline pass between Step 3 and the audience surfaces
- Per-voice frame register taxonomy (museum-label for Cleopatra; pull-quote for Plato; liner-notes for Marley; etc.)
- Cross-voice visibility distribution rule (footer + broadsheet + Substack)

Trigger: A2 (editor layer approval) decided. Doc revision follows.

---

## Section B — Athens-blocking items not yet built

### B1. Editor / Frame layer 🔴 (NEW — see A2)

**State:** unspecified; conceptual reasoning in `_workspace/planning/PIPELINE_DOWNSTREAM_DESIGN_2026_04_30.md`. **No code; no detailed spec.**

**Triggers on:** A2 decision approving editor as separate pass.

**Implementation scope:**
- `runtime/flows/editor_flow.py` — orchestrator
- `runtime/flows/voice/editor.py` — per-voice editor pass (Sonnet recommended; reads amended artifact + engaged_peers metadata + Provocateur briefing + persona-card headline poetics)
- `runtime/flows/shared/prompts/editor_*.md` — register templates (museum-label / pull-quote / liner-notes / wall-text)
- Output: per-voice editorial JSON (title, subtitle, curatorial preamble, pull-quotes, cross-voice contrast block)
- Estimated: ~6-10 hr build for v1; per-voice cost ~$0.50 per artifact

**Per-voice frame register taxonomy (from FU#61 work):**
- Plato (dialogue): pull-quote / brisk headline
- Cleopatra (prostagma): museum label / curatorial
- Whanganui River (proclamation): legal-explanation wall text
- Marley (song): liner notes
- Octopus (sensory prose): exhibition wall text / scientific gloss
- Arendt (essay): pull-quote / argumentative summary
- Ada Lovelace (computational): documentation / readme
- Dostoevsky (confession): epigraph / framing note
- Scheherazade (frame tale): teller-introduces-the-tale
- Ibn Battuta (travelogue): excerpt with travel-context note

### B2. Microsite 🔴

**State:** UNBUILT. Per-artifact pages, edition pages, index pages, footer rendering, shader/audio support.

**Per Frame Concept:** Astro or Next.js static site, GitHub content repo, Vercel/Netlify hosting. Stays live after Athens.

**Per FU#61 + the Step 3 + editor design:** artifact pages for hard-form voices include curatorial preamble above artifact; dialogue-form voices stay stripped. Footer below artifact lists engaged peers (per Step 3 metadata). Shader (Octopus) runs client-side. Audio (Marley) plays inline.

**Triggers on:** Step 3 shape (A1) + editor (A2) decided. Microsite consumes their output schemas.

**Per Frame Concept §"production implications":** mini-concept doc needed before build (`docs/AI_Assembly_Microsite_Concept.md`).

### B3. Broadsheet / Edition Pipeline 🔴

**State:** UNBUILT. Front-page broadsheet per night.

**Per Frame Concept §"newspaper":** one of N artifacts per night (NOT the wrapper); Caslon-style typography; ten voice headlines + short reportage paragraphs; wire-service unavailability paragraph (≤1 per edition); strikethrough as signature visual move (≤1 per edition); masthead with incrementing issue number.

**Implementation:** likely deterministic Python pass + visual production (HTML/CSS template + per-night content fill, possibly screenshot for share). **NOT an LLM pass** if editor layer (B1) produces enough material.

**Triggers on:** A2 (editor layer) + B1 (editor implementation). Broadsheet consumes editor output.

**Per Frame Concept:** `docs/AI_Assembly_Broadsheet_Concept.md` mini-concept needed.

### B4. Substack draft pipeline pass 🔴

**State:** UNBUILT. AI-drafted HoBB-voice walkthrough ready for editor polish.

**Per Frame Concept §"substack":** Real HoBB voice; engages substance directly; pull-quotes from artifacts (NOT from broadsheet); deep-links to microsite per-artifact pages. Day 2 + Day 3 mornings: read-through previous night. Day 4: Night 3 read-through + goodbye.

**Implementation:** Sonnet pass running overnight (after broadsheet writes); reads amended artifacts + editor pull-quotes + cross-voice contrast blocks + previous broadsheet (referenced not routed-through). Produces draft for HoBB editor 5-15 min polish before publish.

**Triggers on:** B1 (editor) so pull-quotes + contrast text are available.

### B5. Closing-show pipelines 🔴

**State:** UNSPECIFIED + UNBUILT. Day 3 evening.

Per Briefing v3.1 §"closing show":
- **Theme identification pass** — reads across all 3 nights' Researcher themes + Provocateur formulations + voice detailed responses; identifies 3-5 throughlines
- **Per-theme mapping pass** — extracts per-voice positions; plots on Matrix A (Power & Agency: human↔nonhuman / many↔one) and Matrix B (Change & Actor: rupture↔progression / individual↔collective); identifies clusters / divergences / empty quadrants; generates read-through script segment
- **Video pipeline pass** — per-voice spoken-dialogue fragments (15-45 sec each), referencing other voices/humans/the Marathon. Editorial polish 1-2 hr by human.
- **Visual deliverables** — matrix-pair template + 3-5 populated instances + animated reveal sequence + video asset

**Triggers on:** post-Athens-Night-3 ideally; spec work pre-Athens.

**Per Briefing:** "Step 3 specification, Theme identification pipeline, Per-theme mapping pipeline, Video pipeline pass, Closing-show visualisation" all listed as new work required before Athens.

### B6. Day 4 goodbye spec 🔴

**State:** UNSPECIFIED.

Per Frame Concept §"Day 4 goodbye": HoBB editorial voice + one panel voice's final line. Decided Day 3 evening based on Night 3 artifacts. Lands on phones in motion (Community Picnic, airport, Aegean Passage boat). Frame does NOT follow the audience out — Day 4 is bridge-only, no fictional Assembly News surface.

**Per Frame Concept §"production implications":** `docs/AI_Assembly_Day4_Goodbye_Concept.md` mini-concept needed; can be written closer to date.

### B7. Render layer for non-text artifacts ⚠️ PARTIAL

**State:** Publish layer handles structured handoff, but rendering itself not implemented:
- **Marley → Suno API** — text artifact → audio file (Suno API call; needs audio hosting on microsite)
- **Octopus → client-side shader params** — chromatophore shader JSON → Three.js or similar in browser

**Triggers on:** voice cards finalized (Marley, Octopus); microsite (B2) able to play audio + render shader.

### B8. Admin console 🔴

**State:** UNBUILT. Operator infrastructure for orchestrating overnight pipelines + council sync + log tail.

**Per ONBOARDING.md:** essential for Athens execution; operator needs:
- Per-stage launch + retry buttons (transcription, researcher, provocateur, voice, publish, editor)
- Live log tail
- Council sync (operator approves/edits Provocateur briefings before voice runs?)
- Validation flag review (Night 1 morning workflow per FU#62 recommendation)

**Spec status:** undocumented. Needs operator product decisions on workflow.

### B9. Per-voice headline poetics 🟡

**State:** Per Frame Concept §"production implications" — needs spec. Either lives in persona card (new field) or in editor's per-voice config.

**Per Frame Concept §"newspaper" headlines paragraph:**
- Plato: Gorgias-style rhetorical questions
- Dostoevsky: affectionate-toward-suffering compound headlines, occasionally with strikethrough
- Whanganui River: wire-service terseness ("WHANGANUI RIVER ARRIVES; SAYS NOTHING")
- Marley: song-title-grammar
- Octopus: chromatic or sensory description

**Each headline = 9-word substance test (Quarch-clearance).**

**Implementation:** one-paragraph specification per voice with 3-5 examples. Build-side (persona-pipeline-adjacent) or editor-config — operator decision when A2 lands.

---

## Section C — Smaller open items / hygiene

### C1. researcher_flow.py cross-pipeline compliance 🟡

**Source:** `OPEN_ITEMS_VOICE_PIPELINE_2026_04_29.md` §"Cross-pipeline status" + FU#60 alignment.

`runtime/flows/researcher_flow.py` `_thinking_kwargs`:
- Drop `temperature: 1.0` (incompatible with thinking per Anthropic docs §"Feature compatibility")
- Add `display: "summarized"` (matches FU#60 + voice pipeline pattern landed in `0381278`)

**Estimated:** ~3 lines, ~30 min.

**Trigger:** before Athens. Opus 4.7 returns 400 BadRequestError on `temperature` parameter — confirmed by persona pipeline empirical observation.

### C2. provocateur_flow.py cross-pipeline compliance 🟡

**Source:** Same as C1.

`runtime/flows/provocateur_flow.py` `_thinking_kwargs`:
- Add `display: "summarized"`
- (Doesn't currently set `temperature` — only one fix needed)

**Estimated:** ~1 line, ~15 min.

### C2a. researcher_flow.py + provocateur_flow.py load_dotenv override=True 🟢

**Source:** `OPEN_ITEMS_VOICE_PIPELINE_2026_04_29.md` §"High priority".

Voice Pipeline hit the shell-empty-env bug (Claude Code agent shell pre-sets API keys to empty strings; `load_dotenv` without `override=True` keeps the empty string). Fixed in Voice Pipeline (commit `f68bc3f`) with `load_dotenv(override=True)`. Same fix not yet landed for `runtime/flows/researcher_flow.py` + `runtime/flows/provocateur_flow.py`.

**Empirical caveat:** may only matter when run from the same Claude Code agent shell environment; operator's normal terminal may not exhibit. But cheap fix worth landing for symmetry.

**Estimated:** ~2 lines, ~5 min total.

### C3. publish_flow.py end-to-end exercise 🔴

**Source:** `OPEN_ITEMS_VOICE_PIPELINE_2026_04_29.md` §"High priority — Athens-blocking-eligible".

`runtime/flows/publish_flow.py` (per-theme + per-extraction reverse index + lineage graph) has **never run end-to-end against real Researcher/Provocateur outputs**. Either:
- Re-run `dev_msc_test` through researcher_flow + provocateur_flow + voice_flow + publish_flow, OR
- Hand-author fixtures matching the briefing schema

**Pre-Athens-must-do.** Publish layer is what hands off to microsite + editor + Substack downstream.

### C4. Multi-night sequence dry-run 🔴

**Source:** `OPEN_ITEMS_VOICE_PIPELINE_2026_04_29.md` + `HANDOFF_VOICE_PIPELINE_DUAL_DRYRUN_2026_04_29.md`.

**Continuity flow + Convention A never end-to-end exercised.** Need:
- Plato + Cleopatra Night 1 → Night 2 sequence
- Convention A: separate run_dirs per night (`athens_2026_2026_05_07_night1`, `_night2`)
- Continuity flow runs after Night 1 Step 3 completes; Night 2's voice system prompts load from `voices/<slug>/continuity_night_2.json`
- Verify cross-night state at PROJECT_ROOT (per `docs/AI_Assembly_Voice_Pipeline.md` §"Multi-night convention")

**Pre-Athens-must-do.** Continuity is a 3-night architecture; running Night 1 only doesn't test it.

### C5. Multi-voice 3+ dry-run 🟡

**Source:** Same.

Step 3 cross-voice engagement only exercised on 2 voices (Plato + Cleopatra). 3+ would test:
- Multi-peer engagement vocabulary (engaged_peers[] with 2+ entries per voice)
- Editor layer scaling across more voices' outputs
- Closing-show theme-mapping across more positions

**Trigger:** more voices finalized (Octopus + 1-2 more).

### C6. Naming inconsistency cleanup 🟡

**Source:** `OPEN_ITEMS_VOICE_PIPELINE_2026_04_29.md` §"Medium priority".

Three names for the same field:
- `council_member_name` (persona card)
- `council_member` (voice output)
- `voice_name` (publish output)

Could harmonize in a single rename pass. Low priority but cosmetically jarring across logs and downstream consumers.

**Estimated:** ~30-60 min including grep + rename + test.

### C7. Title source pipeline 🟡

**Source:** `OPEN_ITEMS_VOICE_PIPELINE_2026_04_29.md` §"Medium priority" + decided 2026-04-29.

**Decision:** voice no longer produces title/subtitle (downstream concern; baked into voice prompts in commit `f6ee392`).

**Open:** where do they come from for the microsite?
- **Resolved by editor layer (B1)** — editor produces title + subtitle as part of its per-voice pass. This is the recommended path under PIPELINE_DOWNSTREAM_DESIGN.
- Alternative: standalone auto-titler step (small Sonnet call reads artifact_text → emits title + subtitle)
- Alternative: human editorial (operator authors per artifact)
- Alternative: empty-title path through Athens + post-hoc

Triggers on A2 (editor layer) decision.

### C8. Voice-side artifact tuning items from real validation findings 🟡

**Source:** `OPEN_ITEMS_VOICE_PIPELINE_2026_04_29.md` §"Medium priority".

From dryrun #2 (Plato solo) validator findings:
- Plato underused `translation_protocol` in Step 1 (modern terms left raw — operator: keep as-is, voice-side artifact)
- "our condition" / first-person-presence-in-room slips in theme_001 Step 1 prose (validator correctly caught these)
- Theme_002 constitution slip (Plato gave thymos logos's job; shifted to monologic assertion vs elenchus)

**None blocking.** Could sharpen via Plato card patches OR via Step 1 closing-instruction guards. Operator-side judgment call.

### C9. Provocateur Night 2 / Night 3 (theme_id, member) exclusion filter 🔴

**Source:** archive `session-artifacts/SESSION_HANDOFF.md` line 210 ("Night 2/3 plumbing: not plumbed"). Confirmed by `docs/AI_Assembly_Provocateur_Pipeline.md` §"Night 2 is different from Night 1" — flagged as pending implementation.

**Problem:** Provocateur Selection on Night 2 must avoid repeating per-voice (theme_id, member) pairs already assigned on Night 1. Night 3 must avoid pairs from Nights 1 + 2. Per Briefing v3.1 §"Stage 1b": *"On Night 2, the Provocateur receives Night 1's assignments to avoid repeating territory. On Night 3, both previous nights."*

**Status:** unimplemented in `runtime/flows/provocateur_flow.py` Selection stage. The filter logic does not currently load prior nights' selections.

**Pre-Athens-must-do.** Without it, Night 2 + Night 3 risk repeating territory assigned on Night 1 + 2. Athens runs are 3 nights — this fires twice.

**Estimated:** ~2-3 hr (load prior `selection.json` files from previous nights' run_dirs; add exclusion filter to the deterministic Python Selection stage; tests).

### C10. Council config: replace `dev_stub_v2_with_selection_params` with real Provocateur Profiles 🔴

**Source:** archive `session-artifacts/SESSION_HANDOFF.md` line 211 ("Council config members are stubs… Pre-Athens blocker").

**Problem:** `runtime/flows/shared/council/council_config.json` `members[]` are still hand-written stubs (`dev_stub_v2_with_selection_params`), not derived from completed Persona Cards' Provocateur Profile artifacts.

**Per cross-repo handoff contract (`personas/HANDOFF.md`):** each finalized voice's `voices/<slug>/06_derive/01_provocateur_profile.json` (8 fields) wires into `council_config.json` `members[]`.

**Current state:** Plato + Cleopatra + Dostoevsky have shipped Provocateur Profiles in athens-2026; runtime council_config has not yet been updated to consume them.

**Pre-Athens-must-do.** Provocateur Triage + Selection both consume `council_config.json` — mismatched member profiles produce wrong assignments.

**Estimated:** ~30 min once profiles are ready (mostly mechanical concatenation + selection_parameters preserved). Re-runs as more voices ship.

### C11. Speaker bios empty in `runtime/reference/speakers.json` 🟡

**Source:** archive `session-artifacts/SESSION_HANDOFF.md` line 212 ("Speaker bios empty… Speaker ID Pass 3 accuracy drops from 70-85% to 40-50% without them. Pre-Athens blocker.").

**Problem:** `runtime/reference/speakers.json` has 202 speakers, all with `bio: ""`. Transcription Pipeline Pass 3 (multi-pass speaker attribution) uses bios as one of its disambiguation signals; empty bios degrade accuracy materially.

**Per Transcription Pipeline spec:** Speaker ID Pass 3 is a 5-pass attribution (cue → role → expertise → confidence → per-turn sanity check); the role/expertise pass relies on speaker bios.

**Estimated:** ~3-4 hr operator wall time to populate from program materials + speaker page sources. Or accept the accuracy drop and rely on Pass 4 manual review (15-30 min per night per Architecture v1).

### C12. HoBB email tool integration 🟡

**Source:** `docs/AI_Assembly_Briefing_v3_1.md` §"Operational workstreams" + archive `specs/AI_Assembly_Architecture_v1.md` §"Stage D — Deliver to HoBB email tool".

**Problem:** Substack / newsletter delivery requires API access to HoBB's email tool (Mailchimp / Campaign Monitor / HubSpot / Substack / Beehiiv / Ghost — most have REST APIs; some have native Prefect/n8n nodes).

**Open:** which tool HoBB actually uses + obtaining API credentials. Architecture v1 flagged as "30-minute investigation."

**Fallback:** manual paste from a shared folder if API integration isn't possible.

**Pre-Athens-eligible.** Needs operator-side conversation with whoever runs HoBB's list.

### C13. Recording protocol pre-Athens 🟡

**Source:** `docs/AI_Assembly_Briefing_v3_1.md` §"Operational workstreams" + archive `specs/AI_Assembly_Architecture_v1.md` §"Recording Protocol".

Three procedural items raise transcription accuracy from ~50% to 70-85%:
1. Moderators introduce all panelists by full name at the start of every session
2. Walking-session participants state their names at the start of each reflection recording
3. All panelist names + affiliations + session-specific terminology pre-loaded into AssemblyAI custom vocabulary before the conference

**Operator-side / WBBF coordination.** Out of strict runtime-code scope but pre-Athens infrastructure.

### C14. Runtime doc-hygiene minor gaps 🟢

**Source:** archive `planning_2026_04_consolidation/RUNTIME_REVIEW_2026_04_20.md` §"Minor doc-hygiene gaps".

Four small items flagged 2026-04-20; not yet closed:
- `runtime/flows/shared/prompts/_archive/` has no README stating retirement reason for archived prompts
- `runtime/scripts/generate_sessions_json.py` + `runtime/scripts/generate_speakers_json.py` lack module docstrings
- `runtime/ingest/pipeline.py` writes `status.json` consumed by UI templates; schema not documented near the writer (no dataclass, no comment block)
- `runtime/flows/shared/download_session.sh` (yt-dlp + ffmpeg dev utility) is mis-located in `flows/shared/` — natural home is `runtime/scripts/`

**Estimated:** ~30-60 min to close all four. Anytime; risk-free.

---

## Section D — Existing FU#s, runtime-relevant

These are open FU# entries from `_workspace/planning/FOLLOW_UPS.md` that pertain to runtime. Cross-referenced; full text in FOLLOW_UPS.md. (Persona-internal FUs not listed here.)

**Note (2026-05-01):** FOLLOW_UPS.md is **FROZEN** as of 2026-05-01 — no new FU# entries will be added. The list below is closed at FU#62. New runtime items file directly in this OPEN_ITEMS doc (Section A/B/C/E as appropriate); no FU# numbering required. See `code/CLAUDE.md` §"Planning / tracking conventions" for the full workflow.

| FU# | Description | Status | Trigger |
|---|---|---|---|
| FU#21 | Runtime enforcement of `reference_only_passages` Step 1/Step 2 contract | ✅ LANDED 2026-04-28 | Done — preserved here for reference |
| FU#23 | Cross-repo handoff timing (rebuild → runtime integration) | Open — **trigger condition met** (Phase L Plato shipped 2026-04-26 + 04-28-04-29 finalization); now actionable | Was gated behind first-voice-shipped Phase L sign-off; that has happened. Decision needed: integration model (continuous merge / batch handoff / parallel-systems window) |
| FU#24 | Settings allowlist tightening | Open | Anytime |
| FU#25 | Split provocateur_flow.py into 5 stage files | Open | Code-hygiene anytime; risk-free |
| FU#26 | Typed PROMPTS registry for `load_prompt(name)` | Open | Code-hygiene anytime |
| FU#27 | Runtime flow-level unit tests | Open | Pre-Athens-eligible (currently runtime has no unit tests) |
| FU#42 | Split-card architecture (voice-card / deployment-card) | 🔵 POST-ATHENS | Deferred |
| FU#47 | Voice Pipeline Step 1 mode-switching for non-analytical voices | Open — runtime infrastructure **does not exist yet**; current Step 1 prompt is single-mode (`analytical_workshop`); voice-config carries `voice_mode` but Step 1 doesn't branch on it | When non-analytical voice (Octopus, Whanganui, Dostoevsky, Marley, Scheherazade, Ibn Battuta — ~6/12 voices) dry-run-tested; estimated ~2-3 days build (4 mode variants: analytical_workshop / scenic_drafting / lyric_recall / observational_witnessing + orchestrator branch logic) |
| FU#49B | Step 2 generativity teeth (anti-premature-closure pressure) | 🔵 POST-ATHENS — runtime; **reviewer pass-3 specific Step 2 wrapper text drafted** ("compose, do not compress smooth… read your reasoning trace before composing and identify, explicitly, the moves it contained that the artifact form will be tempted to drop…"). Ready-to-paste prompt material in FU#49 entry of FOLLOW_UPS.md | Deferred; revisit if Athens artifacts ship over-settled. Material to land lives in `runtime/flows/shared/prompts/voice_step2_artifact.md` |
| FU#49E | Step 3 amendment | **REOPENED — A1** (was effectively closed; design framing dropped 2026-04-29) | A1 decision |
| FU#49F | Per-voice framework-strain log on micro-site | 🔵 POST-ATHENS — runtime + microsite | Microsite (B2) build + post-Athens decision |
| FU#49M | `strain_markers[]` runtime artifact contract (Step 2 schema constraint) | 🔵 POST-ATHENS | Deferred |
| FU#54 | Smoke test runtime-fidelity refactor (Pass 7b) | 🔵 POST-ATHENS | Deferred |
| FU#57 | Drop `bold_engagement_topics` from runtime system prompts | ✅ LANDED 2026-04-29 | Done |
| FU#60 | Adaptive thinking observability + temperature compatibility | ✅ LANDED 2026-04-29 (voice + persona); ⚠️ NOT YET on researcher/provocateur (see C1, C2) | C1+C2 close it for runtime |
| FU#61 | Voice-side Layer-1 quality_criteria for low-Layer-1-surface forms | 🟡 IMPORTANT — v3 LANDED on Cleopatra + Dostoevsky; persona Pass 4b prompt addition committed; **propagation to Whanganui / Marley / Octopus pending those builds** | Per-voice on next builds |
| FU#62 | Voice Pipeline validation regen-on-flag is unimplemented | 🔵 NEW (filed today) — see A3 | A3 decision |

---

## Section E — Documentation pending

### E1. `docs/AI_Assembly_Voice_Pipeline.md` 🟡

**State:** v2.1, last touched 2026-04-29. Stale on:
- **Step 3 section** — written assuming FU#49E correspondence-shape; needs rewrite once A1 decides (probably to B+ shape with engaged_peers metadata + optional postscript)
- **Validation policy + cost/wall-time** — spec claims 3-5 min wall, $30-50 cost; reality is 20-40 min wall, $3-15 cost (per code audit + dryrun observation). Update §"Cost & Envelope" validation row.
- **Regeneration policy** — per FU#62, spec promises regen but code doesn't implement; either implement or update spec to "diagnostic flag only" (A3 decides)

### E2. `docs/AI_Assembly_Frame_Concept_v1.md` 🟡

See A4 above. Needs:
- Strip rule voice-register-conditional
- Add editor / frame layer
- Per-voice frame register taxonomy
- Cross-voice visibility distribution rule

Triggers on A2 decision.

### E3. `docs/LLM_CALL_INVENTORY.md` 🔵

**State:** stale since 2026-04-27.

**Needs updates for:**
- FU#52 / FU#53 / FU#57 / FU#58 / FU#59 / FU#60 / FU#61 / FU#62
- Voice Pipeline rows added (currently missing — was "NOT YET BUILT" when inventory was written)
- Once FU#60 lands: `effort` + `display` columns + observed `thinking_tokens` per pass

**Estimated:** ~1-2 hr.

### E4. PIPELINE_DOWNSTREAM_DESIGN — archived ✅ 2026-05-01

**State:** moved to `_workspace/archive/runtime_consolidation_2026_05_01/PIPELINE_DOWNSTREAM_DESIGN_2026_04_30.md` in commit `ab2c082`. Architectural content folded into runtime/OPEN_ITEMS.md A2 + runtime/ONBOARDING.md architecture sections.

**Action:** none. Resolved.

### E5. New mini-concept docs needed (per Frame Concept §"production implications")

When B1 (editor) lands, these mini-concepts should be drafted:
- `docs/AI_Assembly_Broadsheet_Concept.md` — front-page layout, masthead, headline placement, wire-service/strikethrough discipline
- `docs/AI_Assembly_Edition_Pipeline.md` — generation specification
- `docs/AI_Assembly_Headline_Poetics.md` — per-voice headline grammar (B9)
- `docs/AI_Assembly_Microsite_Concept.md` — IA, chrome, per-artifact rendering, deep-link conventions
- `docs/AI_Assembly_Closing_Show_Concept.md` — beat sheet, B-roll inventory, anchor briefs
- `docs/AI_Assembly_Substack_Concept.md` — HoBB voice calibration, pull-quote convention
- `docs/AI_Assembly_Day4_Goodbye_Concept.md` — brief spec, can be written closer to date

---

## Section F — Recently landed (for context)

These items closed within the last 2 weeks. Listed here so the runtime onboarding has context for the current state.

| Date | Item | Location |
|---|---|---|
| 2026-04-30 | FU#61 v3 (5-criteria reshape) on Cleopatra | athens-2026 commit `c89d186` |
| 2026-04-30 | FU#61-fresh pattern propagated to Dostoevsky | athens-2026 commit `5088d67` |
| 2026-04-30 | FU#61 Pass 4b prompt addition (panel-wide propagation) | code commit `91947a7` |
| 2026-04-30 | FU#62 filed (validation regen gap) | FOLLOW_UPS.md |
| 2026-04-29 | Voice Pipeline v2.1 alignment with persona-prompt revert | branch `voice-pipeline-v2.1-align-revert` (commits `fb33bb9` + `30a38eb`) |
| 2026-04-29 | Post-dryrun tuning: validator (c) soften, extraction-ID bookkeeping, load_dotenv override | commit `f68bc3f` |
| 2026-04-29 | Title/subtitle dropped from voice prompts; themes_covered derived deterministically; Convention A documented | commit `f6ee392` |
| 2026-04-29 | FU#60 voice side: drop temperature, add display: summarized | commit `0381278` |
| 2026-04-29 | responded_to_graph derivation refactored (post-dryrun #4) | commit `e89dfc4` |
| 2026-04-28 | Voice Pipeline Steps 1+2+3 implementation v2 | commits `180a18f` + `aca0e4c` |
| 2026-04-28 | Voice Pipeline v2 spec landed | `docs/AI_Assembly_Voice_Pipeline.md` |
| 2026-04-28 | Publish layer landed | commit `ddec38a` (`runtime/flows/voice/publish.py` + `runtime/flows/publish_flow.py`) |
| 2026-04-28 | FU#21 (reference_only_passages Step 1/2 contract) | LANDED |
| 2026-04-28 | Panel reduced 12 → 10 voices (Tang + Thiel removed) | branch state |

---

## Section G — Athens timeline / what blocks what

Working back from May 7 2026 (Athens Day 1 evening; Night 1 runs overnight).

**Must land before Athens Night 1:**
- A1 (Step 3 shape) decided + implemented
- A2 (editor layer) decided + B1 (editor implementation) complete
- B2 (microsite) built and deployed
- B3 (broadsheet / Edition Pipeline) built
- B4 (Substack draft pass) built
- **C9 (Provocateur Night 2/3 exclusion filter)** — fires twice during Athens
- **C10 (council_config.json populated from real Provocateur Profiles)** — runtime infrastructure
- C1 + C2 (cross-pipeline compliance) landed
- C3 (publish_flow.py end-to-end exercise) completed
- C4 (multi-night sequence dry-run) completed
- A3 / FU#62 path decided (probably spec update + Athens Night 1 only validation policy)
- All 10 persona cards finalized (persona thread; not in scope here but blocks runtime end-to-end testing)

**Should land before Athens (high-value, not strictly blocking):**
- B5 (closing-show pipelines) at least specified; build can land Day 1-3
- B6 (Day 4 goodbye) specified
- B9 (per-voice headline poetics) specified
- A4 (Frame Concept doc revision)
- E1 (Voice Pipeline doc Step 3 + cost/wall-time updates)
- E3 (LLM_CALL_INVENTORY refresh)
- C5 (multi-voice 3+ dry-run)
- C6 (naming inconsistency cleanup) — quality-of-life for ops
- **C11 (speaker bios populated)** — transcription accuracy
- **C12 (HoBB email tool API investigation)** — newsletter delivery
- **C13 (recording protocol coordination)** — operator/WBBF side; raises ASR accuracy

**Can land during/after Athens:**
- B7 (render layer) — only matters when Marley/Octopus voices ship
- B8 (admin console) — operator infra; can be improvised with command-line for Athens
- C8 (voice-side artifact tuning) — operator-side; per-voice judgment
- **C14 (runtime doc-hygiene minor gaps)** — anytime; risk-free

**Post-Athens deferred:**
- FU#42, FU#47, FU#49M, FU#54

---

*End of runtime open items. Authoritative for runtime work going forward. Replaces OPEN_ITEMS_VOICE_PIPELINE_2026_04_29.md (which can be archived).*
