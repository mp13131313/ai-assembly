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

**Step 3 status (resolved 2026-05-01):**
- ✅ A1 RESOLVED: Step 3 SKIPPED for Athens (Option A). Athens runs ship Steps 1+2 only via existing `--skip-step3` CLI flag. Cross-voice visibility moves to editor layer + Substack. B+ shape preserved as the re-add path post-Athens (~2 days). Module + prompt + `_build_responded_to_graph` stay in codebase, dormant.

**Designed conceptually, not yet built:**
- Editor / Frame layer — A2 architecture settled 2026-05-01 (per-theme article, all-AI drafting, voice artifacts ship as-is); editor output schema gated on microsite design
- Microsite (operator designing) — drives editor output schema per A2 F
- Broadsheet, Substack draft pipelines — consume editor + voice outputs
- Closing-show pipelines, Day 4 goodbye, render layer for non-text artifacts, admin console

**Spec/impl divergences worth knowing:**
- ~~Voice Pipeline validation regen-on-flag is unimplemented (FU#62) — diagnostic flag only~~ ✅ RESOLVED 2026-05-01: spec updated to match implementation (validation is diagnostic-only; Athens policy Night 1 ON / Nights 2+3 OFF)
- ~~Validation wall-time is ~20-40 min/night actual vs spec's 3-5 min claim~~ ✅ RESOLVED 2026-05-01: spec updated; Night 1 envelope ~50-80 min, Nights 2+3 ~30-45 min documented

---

## Section A — Gating design decisions (open, blocking implementation)

These need operator answers before implementation can proceed.

### A1. Step 3 architectural shape ✅ RESOLVED 2026-05-01 (Option A — skip for Athens; re-add post-editor/microsite if budget permits)

**Resolution:** Athens runs ship Steps 1+2 only. Step 3 skipped via existing `--skip-step3` CLI flag (was DEV-USE-ONLY warning; now Athens production default). Cross-voice visibility moves entirely to the editor layer (A2) + Substack walkthrough — editor reads peer Step 2 artifacts on shared themes via `themes_to_voices` map and authors cross-voice contrast text in editorial register.

**Trade made (with eyes open):**
- *Lost:* Briefing line 177-179's claim that voices themselves read each other and decide whether to amend at the artifact layer. Cross-voice conversation becomes editor-narrated (third-party register), not voice-in-its-own-grammar.
- *Preserved:* `themes_to_voices` structural map; editor cross-voice contrast text; Substack walkthrough; continuity flow (reads Step 2 + Step 1 detailed responses, doesn't depend on Step 3).
- *Reversible:* Step 3 prompt + module + `_build_responded_to_graph` stay in codebase, dormant. Re-enable cost ~2 days.

**Why Option A over B+:** Six days to Athens; editor + microsite + broadsheet + Substack draft pass all unbuilt. Pragmatic triage — ship the surfaces that aren't built, defer Step 3 (mechanically validated but framing-in-flux) until those land. Provotype framing absorbs the cost: visible construction is a feature, and an editor-mediated cross-voice surface is honest about what happened (voices wrote in parallel; editor reads across).

**For background — the four options that were on the table:**

| Option | Step 3 output | Artifact body | Cross-voice visibility | Layer 1 risk | Cost/night |
|---|---|---|---|---|---|
| **A** Skip entirely *(CHOSEN for Athens)* | (no Step 3) | Step 2 only | Editor narrates third-party | None | $0 |
| **B** Metadata-only | engaged_peers[] notes | Step 2 unchanged | Metadata footer + editor + Substack | None | ~$5 (Sonnet read-only) |
| **B+** Metadata + postscript *(originally recommended)* | engaged_peers[] + optional postscript paragraph | Step 2 + postscript appended | Postscript visible in artifact + metadata + editor + Substack | None (body unchanged) | ~$10-20 |
| **C** Full body regeneration | engaged_peers[] + amended artifact | Regenerated | Visible in artifact body | Real (regen risks Step 2 calibration) | ~$50 (Opus + thinking) |

**Re-add path (post-Athens, or pre-Athens if editor + microsite + broadsheet land fast):**

Adopt B+ shape: `engaged_peers[]` metadata + optional voice-written postscript paragraph appended below Step 2 body. Body untouched (no regen risk).

Files to change:
- `runtime/flows/shared/prompts/voice_step3_amendment.md` — full rewrite (drop FU#49E correspondence framing; new B+ prompt; ~1 day)
- `runtime/flows/voice/step3_amended_artifact.py` — output schema overhaul: `engaged_peers[{peer_voice, peer_artifact_focus, took, rejected, decision}] + postscript_text + postscript_form` (~half-day)
- `runtime/flows/voice_flow.py:_build_responded_to_graph` — derive from `engaged_peers[].decision`
- Editor schema update — additive `engaged_peers` + `postscript_text` consumer fields (~30 min)
- Microsite footer update — show responded_to_graph (~30 min)
- Substack walkthrough update — cite voice's own engaged_peers material (~30 min)
- `docs/AI_Assembly_Voice_Pipeline.md` Step 3 section rewrite
- One-shot migration script for old `amendments[]`-shape Step 3 files in dryrun directories (or just regenerate — only Plato + Cleopatra dryrun #4 has the old shape)

**Estimate:** ~2 days total to add back.

---

### A2. Editor / Frame layer architecture ✅ RESOLVED 2026-05-01 (mostly — D deferred, microsite output schema TBD)

**Resolution per operator 2026-05-01:**

| | Decision | Resolution |
|---|---|---|
| **A** | Separate editor pipeline pass between Step 2 and audience surfaces | ✅ **YES** |
| **B** | Editor unit of work — per-voice OR per-theme | ✅ **PER-THEME**. Editor reads all voices on a single theme + their Step 2 artifacts + per-voice Provocateur formulations, and writes a **theme-level article** that frames the theme and surveys positions across voices. **Voice artifacts ship as-is** (untouched), with their Provocateur formulation as a micro-header above each artifact. *Different from the per-voice "editorial chrome" model originally proposed.* |
| **C** | Drafting model — AI-drafted operator-polished vs all-AI | ✅ **ALL AI**. No operator polish phase. AI output ships directly. Implications: editor model needs to produce reader-ready prose without human pass; argues for Sonnet 4.6 + thinking minimum, possibly Opus 4.7 if quality observation warrants escalation. Substack-pattern operator polish does NOT apply here. |
| **D** | Strip rule (curatorial preamble for hard-form voices) | 🟡 **DEFERRED — operator not sure**. Largely moot under B's per-theme restructure: the theme article carries cross-voice framing; per-voice artifacts ship as-is with formulation. Re-open if microsite design surfaces a need. |
| **E** | Cross-voice visibility distribution across surfaces | 🔵 **DESIGNED ELSEWHERE** by operator (microsite + broadsheet + Substack design docs). Editor's job is just to produce an output schema those surfaces consume. Out of A2 scope going forward. |
| **F** | Build order: editor first vs surfaces first | ✅ **PARALLEL BUILD; microsite specifies editor output**. Microsite design drives editor schema. Microsite says "I need fields X, Y, Z"; editor produces those fields. Editor build proceeds in parallel with microsite design once microsite output schema is settled. |

**Architectural shape (per A + B + C + F):**

- **Unit:** per-theme. Roughly 3-5 themes per night × 1 editor call per theme = ~3-5 calls/night (vs 10/night for per-voice).
- **Input:** one theme record + all voices' Step 2 artifacts on that theme + each voice's Provocateur formulation for that theme + audience context.
- **Output:** a theme-level article. Schema TBD — **gated on microsite design output** (per F). Editor build cannot finalize prompts until microsite specifies what fields it consumes.
- **Drafting:** all-AI, no polish. Sonnet 4.6 + adaptive thinking as v1 default; flag for Opus 4.7 escalation if quality observation suggests.
- **Voice artifacts:** ship as-is from Step 2. Formulation appears above the artifact on display surfaces as a micro-header.

**Cost estimate (revised under per-theme + Sonnet):**
- ~3-5 themes/night × ~$2/call = ~$6-10/night editor cost
- Across 3 Athens nights: ~$20-30 added to total
- Wall: ~2-3 min/night (parallel across themes)

**Files implicated when this fully decides + microsite design lands:**
- New: `runtime/flows/editor_flow.py` (per-theme orchestrator, parallel across themes)
- New: `runtime/flows/voice/editor.py` (single per-theme editor call) — naming may change since editor is per-theme not per-voice
- New: `runtime/flows/shared/prompts/editor_theme_article.md` (single template; per-voice register taxonomy not needed under per-theme)
- Updates: `docs/AI_Assembly_Frame_Concept_v1.md` (per-theme article framing; strip rule deferred per D)
- Updates: `docs/AI_Assembly_Voice_Pipeline.md` (downstream consumer reference)

**Status of editor build:**
- ✅ Architecture settled (A + B + C + F decided 2026-05-01)
- 🔵 Editor output schema gated on microsite design (operator working elsewhere per E + F)
- 🔵 D (curatorial preamble) deferred; re-open if microsite design surfaces a need
- ⏳ Once microsite design specifies editor output schema → editor build proceeds (~6-10 hr engineering + 5 register prompts collapsed to 1 theme-article prompt = simpler than originally scoped)

---

### A3. FU#62 — validation regen-on-flag: implement or update spec? ✅ RESOLVED 2026-05-01 (path B)

**Resolution:** Path B chosen and applied.

`docs/AI_Assembly_Voice_Pipeline.md` updated:
- §"Regeneration policy" rewritten — validation is diagnostic-only; no regen, no retry; flagged outputs ship to Step 2 with manifest entries for operator review
- §"Default policy for Athens" — Night 1 ON for all 10 voices; **Nights 2+3 OFF** (no regen → pure cost on Nights 2+3 without remediation; operator morning-review handles correction)
- §"Cost & Envelope" — split into Night 1 (~$180-240, ~50-80 min wall — validation per-voice serial) vs Nights 2+3 (~$180-230, ~30-45 min wall, validation OFF, continuity ON). 3-night Athens total ~$540-700.
- v1→v2.1 changes table + Overview envelope statement updated to match.

**Background (preserved for context):** Voice Pipeline spec previously promised *"First failure: regenerate the Step 1 call with the validator's critique appended… Second failure: ship the regenerated output AND flag in the run-level manifest."* Implementation reality: orchestrator collects flagged results into `validation_failures[]`, hardcodes `regen_count: 0`, proceeds to Step 2 unchanged. **No regen ever fires.** Spec now matches implementation.

**Future post-Athens:** if autonomous regen is wanted for unattended runs, file as a new item in this OPEN_ITEMS doc against the contract documented in the spec. ~half-day implementation against `runtime/flows/voice_flow.py:337-363` + `runtime/flows/voice/step1_validation.py`.

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

**Triggers on:** Microsite design specifying editor output schema (per A2 F decision 2026-05-01 — parallel build, microsite specifies).

**Architecture (per A2 decisions 2026-05-01 — A + B + C + F):**
- **Per-theme** (not per-voice). One editor call per theme that has voices on it.
- **All-AI** drafting; no operator polish phase.
- **Voice artifacts ship as-is** (Step 2 untouched). Voice's Provocateur formulation appears as micro-header above the artifact on display surfaces.
- **Cross-voice work happens in the theme article**, not in per-voice editorial chrome.

**Implementation scope (revised under per-theme):**
- `runtime/flows/editor_flow.py` — orchestrator (parallel across themes)
- `runtime/flows/voice/editor.py` — per-theme editor call (~3-5/night). Naming may change from `voice/editor.py` to `theme/editor.py` since unit is theme not voice.
- `runtime/flows/shared/prompts/editor_theme_article.md` — single template (not per-register taxonomy; voice register is now carried by voice's own as-is artifact)
- **Input:** one theme record + all voices' Step 2 artifacts on that theme + each voice's Provocateur formulation + audience context
- **Output:** theme-level article. **Schema TBD — gated on microsite design output (per F).**
- **Model:** Sonnet 4.6 + adaptive thinking v1 default; flag for Opus 4.7 if quality observation suggests escalation (since all-AI with no polish raises the quality bar on the model output).
- **Estimated:** ~6-10 hr build for v1 once microsite output schema lands; ~$2/call × 3-5 themes/night = ~$6-10/night; ~$20-30 across 3 Athens nights.

**Per-voice frame register taxonomy (originally proposed):** REMOVED under per-theme architecture. Voice artifacts ship in their native form with their Provocateur formulation as micro-header — no per-voice editorial chrome. Headline poetics may still matter for broadsheet display of voice names; that's a broadsheet/microsite concern, not editor's.

### B2. Microsite 🔴

**State:** UNBUILT. Operator currently designing (per A2 E decision 2026-05-01 — designed elsewhere).

**Two page types under per-theme editor architecture:**
- **Theme page:** editor's theme-level article + the voices' as-is artifacts (each with formulation as micro-header) on that theme
- **Per-voice artifact page:** voice's Step 2 artifact as-is, with Provocateur formulation as header context. No editor-authored title/subtitle/preamble (per A2 B 2026-05-01 — artifact lands as is).

**Per Frame Concept:** Astro or Next.js static site, GitHub content repo, Vercel/Netlify hosting. Stays live after Athens.

**Triggers / blocks:**
- 🔵 Operator-designed; design output **specifies editor output schema** (per A2 F 2026-05-01)
- Once microsite design completes → editor build (B1) unblocks; broadsheet (B3) and Substack (B4) consume same outputs

**Per Frame Concept §"production implications":** `docs/AI_Assembly_Microsite_Concept.md` mini-concept landing as part of operator's design work.

### B3. Broadsheet / Edition Pipeline 🔴

**State:** UNBUILT. Front-page broadsheet per night.

**Per Frame Concept §"newspaper":** one of N artifacts per night (NOT the wrapper); Caslon-style typography; ten voice headlines + short reportage paragraphs; wire-service unavailability paragraph (≤1 per edition); strikethrough as signature visual move (≤1 per edition); masthead with incrementing issue number.

**Implementation:** likely deterministic Python pass + visual production (HTML/CSS template + per-night content fill, possibly screenshot for share). **NOT an LLM pass** if editor layer (B1) produces enough material — under per-theme editor, broadsheet consumes theme articles + voice artifacts directly; headline grammar still needs solving (per-voice headline poetics may matter for broadsheet voice-name display).

**Triggers on:** A2 (editor layer) decisions settled ✅; microsite output schema (B2) → editor build (B1) → broadsheet consumes editor + voice outputs.

**Per Frame Concept:** `docs/AI_Assembly_Broadsheet_Concept.md` mini-concept needed.

### B4. Substack draft pipeline pass 🔴

**State:** UNBUILT.

**Per A2 C decision 2026-05-01 (all-AI):** still TBD whether Substack inherits all-AI mode or keeps its existing AI-drafted-operator-polished pattern. The original Frame Concept positioned Substack as HoBB editorial voice with operator polish; A2 C only resolved the editor layer's drafting model, not Substack's. Decision pending — operator owns.

**Per Frame Concept §"substack":** Real HoBB voice; engages substance directly; pull-quotes from artifacts (NOT from broadsheet); deep-links to microsite per-artifact pages. Day 2 + Day 3 mornings: read-through previous night. Day 4: Night 3 read-through + goodbye.

**Implementation:** Sonnet pass running overnight; reads voice artifacts + editor theme articles + previous Substack post (referenced not routed-through).

**Triggers on:** B1 (editor) so theme articles are available; B2 (microsite) so deep-links resolve.

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

### C1. researcher_flow.py cross-pipeline compliance ✅ LANDED 2026-05-01

**Source:** `OPEN_ITEMS_VOICE_PIPELINE_2026_04_29.md` §"Cross-pipeline status" + FU#60 alignment.

`runtime/flows/researcher_flow.py` `_thinking_kwargs`:
- ✅ Dropped `temperature: 1.0` (incompatible with thinking per Anthropic docs §"Feature compatibility")
- ✅ Added `display: "summarized"` (matches FU#60 + voice pipeline pattern landed in `0381278`)
- Docstring updated to reflect feature-compatibility constraint
- Verified: `researcher_flow._thinking_kwargs(0)` returns `{'thinking': {'type': 'adaptive', 'display': 'summarized'}}` matching voice-pipeline shape

### C2. provocateur_flow.py cross-pipeline compliance ✅ LANDED 2026-05-01

**Source:** Same as C1.

`runtime/flows/provocateur_flow.py` `_thinking_kwargs`:
- ✅ Added `display: "summarized"`
- (Didn't set `temperature` — only one fix needed)
- Docstring updated to reflect FU#60 alignment
- Verified: `provocateur_flow._thinking_kwargs()` returns `{'thinking': {'type': 'adaptive', 'display': 'summarized'}}` matching voice-pipeline shape

### C2a. load_dotenv override=True (researcher + provocateur + transcription) ✅ LANDED 2026-05-01

**Source:** `OPEN_ITEMS_VOICE_PIPELINE_2026_04_29.md` §"High priority".

Voice Pipeline hit the shell-empty-env bug (Claude Code agent shell pre-sets API keys to empty strings; `load_dotenv` without `override=True` keeps the empty string). Fixed in Voice Pipeline (commit `f68bc3f`) with `load_dotenv(override=True)`.

✅ Same fix landed 2026-05-01 on:
- `runtime/flows/researcher_flow.py:47`
- `runtime/flows/provocateur_flow.py:92` (with explanatory comment about the empty-env bug)
- `runtime/flows/transcription_flow.py:56` (extended scope per operator request — transcription also hits this if run from Claude Code agent shell)

All three flow entry-points now consistent with voice + persona pipeline patterns.

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

### C6. Naming inconsistency cleanup ✅ CLOSED 2026-05-01 (misdiagnosed at filing — three names mark domain boundaries by design, not duplicate fields)

**Source:** `OPEN_ITEMS_VOICE_PIPELINE_2026_04_29.md` §"Medium priority" (original filing, since superseded).

**Resolution 2026-05-01:** investigated and closed as misdiagnosed. The three names are not redundant — they mark deliberate domain boundaries:

```
persona card        →  voice pipeline        →  publish layer
council_member_name →  council_member        →  voice_name
(ceremonial,           (internal Provocateur-    (audience-facing
 full identity)         domain identifier)        display name)
```

Evidence: `runtime/flows/voice/card_assembly.py:476-497` — the publish-layer rename is documented:
```python
"""Keep: voice_name (renamed from council_member),"""
...
if k == "council_member":
    out["voice_name"] = first_draft[k]
```

The rename at the publish-assembly boundary is a deliberate architectural transition, not an oversight. Harmonizing would collapse meaningful distinctions (audience-facing display name vs internal Provocateur-domain identifier vs persona-card ceremonial identity), break 4 shipped athens-2026 voice cards in a separate private repo, and update the Persona Card v2 spec — all for a "cosmetic logs readability" win that doesn't justify the cost.

**If post-Athens we want a smaller logs-readability win,** file a separate item scoped narrowly to log-line normalization without touching field names.

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

**Estimated:** ~30 min once profiles are ready (mostly mechanical concatenation + selection_parameters preserved).

**Sequencing decision 2026-05-01 (operator):** wait until all 10 voices are shipped, then do single-pass population. Operator confirmed all 10 will be ready pre-Athens, so partial-now + re-run-later isn't worth the churn — single mechanical pass when voices track is complete. Currently 4 shipped (Plato, Cleopatra, Dostoevsky, Battuta) + Octopus paused at FU#53 review; 5 unbuilt (Arendt, Lovelace, Marley, Whanganui, Scheherazade).

### C11. Speaker bios in `projects/athens-2026/reference/speakers.json` ✅ FULLY CLOSED 2026-05-01 (219/224 active enriched 97.8%; remaining 5 are not in any recording session — no transcription impact)

**Source:** archive `session-artifacts/SESSION_HANDOFF.md` line 212 ("Speaker bios empty… Speaker ID Pass 3 accuracy drops from 70-85% to 40-50% without them. Pre-Athens blocker.").

**File location:** `projects/athens-2026/reference/speakers.json` (Tier 3 — at PROJECT_ROOT, not in code repo).

**Resolution 2026-05-01 (multi-step):**

1. **Built `runtime/scripts/populate_speakers_from_program_html.py`** — extracts the `const SPEAKERS = {...}` JS object embedded in the WBBF program HTML and merges (`oneliner` → title, first attribute → affiliation, all attributes joined → bio) into the existing scaffold. Falls back to `oneliner` for bio + affiliation when `attributes` is empty (one-line speakers like dancers, DJs). Accent-tolerant fuzzy name matching for cases where SESSIONS and SPEAKERS spellings drift in source HTML. Merge-safe: preserves manually-curated values.

2. **Source HTML stashed at** `projects/athens-2026/reference/_source/program_index.html` (May 1 export, 226 speakers). Re-runnable when WBBF updates the program.

3. **Refreshed sessions.json scaffold** via `generate_sessions_json.py` to pick up new sessions + speakers (132 → 146 sessions; preserves `ai_assembly=true` operator flags by `session_id`; 19 of 31 prior flags preserved automatically; 10 more re-applied by exact-title-match against new sessions; 4 remain ambiguous + 1 dropped — see below).

4. **Refreshed speakers.json scaffold** via `generate_speakers_json.py` to pick up 30 new speakers from new sessions; 7 dropped-from-program speakers retained with `_dropped_from_program: true` for bio preservation.

5. **Re-ran enrichment** to populate the new 30 speakers + the 2 renames (Kosmopolou typo, Goudouna honorific) — 217/224 active enriched.

6. **Normalized name typos** in both sessions.json and speakers.json: `Angeliki Kosmopolou` → `Angeliki Kosmopoulou`; `Dr. Sozita Goudouna` → `Sozita Goudouna`. Removed duplicate entries created when scaffold regen pulled SESSIONS' typo names.

**Final coverage:**
- speakers.json: 224 active + 7 dropped = 231 entries; 217 with bios populated (96.9%)
- sessions.json: 146 sessions; 29 flagged for AI Assembly transcription
- **Speaker ID Pass 3 accuracy:** restored from 40-50% (all-empty) into 70-85% target band per Transcription Pipeline spec

**Operator decisions resolved 2026-05-01 (final):**

| Speaker | In recording sessions? | Decision | Action |
|---|---|---|---|
| `Dave` | 4 sessions | Path B — copy HTML duo bio to both | ✅ Applied: title="Artificiality Researchers", bio="Founders of Artificiality Institute · Visiting Researchers at the UC Berkeley Center for Human-Compatible AI" |
| `Helen Edwards` | 4 sessions | Path B — copy HTML duo bio to both | ✅ Same as Dave (preserves Pass 3 disambiguation between Dave/Helen and other speakers) |
| `Giorgos Panagiotopoulos` | 1 session (Act One — 40+ panel) | Leave empty — single missing bio in 40-speaker panel has negligible Pass 3 impact | ✅ |
| `Leon Schmit` | 0 | Leave empty — not in transcription scope | ✅ |
| `Meg Syme` | 0 | Leave empty — not in transcription scope | ✅ |
| `Cloud District` (collective) | 0 | Leave empty — not in transcription scope | ✅ |
| `Launch Pad Teens` (collective) | 0 | Leave empty — not in transcription scope | ✅ |

5 speakers in HTML but not in any session (`Alexandros Maganiotis`, `Clara E. Mattei`, `Dave and Helen Edwards` merged entry, `Leonⁿ MonoSerieⁿ`, `Meryem Lahrichi`): not added to speakers.json — they're program-only mentions, not in any session WBBF has linked.

**Final coverage: 219/224 active speakers populated (97.8%); the 5 remaining are not in any of the 25 recording sessions, so transcription Pass 3 accuracy is unaffected. C11 fully closed.**

~~*4 ambiguous ai_assembly flag re-applications + 1 dropped session*~~ ✅ RESOLVED 2026-05-01 by operator-provided authoritative CSV (`projects/athens-2026/reference/_source/recording_sessions.csv`). Built `runtime/scripts/apply_ai_assembly_flags_from_csv.py` (handles strikethrough markup normalization between CSV `~text~` and sessions.json `<s>text</s>`). All 25 CSV rows matched; ai_assembly=true set on those 25, false on the other 121 (CSV is authoritative source-of-truth going forward).

**Final ai_assembly schedule (25 sessions across 3 nights):**
- **Night 1 (Day One):** 10 sessions — Birthplace of Democracy Tour (10:00), Leading Under Fire (11:15), Human Democracy Is Dead (13:30), New Myths (13:30), The More-Than-Human Democracy (14:45), How to Meet an Idiot (15:30), Rooting the Next Generation (17:30), What Makes Us Human (18:00), Act One (20:00), The Dark Side of Democracy Nightwalk (22:30)
- **Night 2 (Day Two):** 9 sessions — Act Two (8:45), Act Three (10:45), What Is a Good Life (13:30), The Reality Tunnels (14:00), Agents with the License to… (16:30), Aegean Intelligence (16:30), From Lifespan to Joyspan (17:30), Intelligence After Intelligence (18:00), Dance and Dissent Nightwalk (22:30)
- **Night 3 (Day Three):** 6 sessions — Act Four (10:00), Citizen Assembly With AI (14:00), The Long Game (14:00), Building Belonging (14:30), Make Politics Great Again (16:00), Act Five (20:00)

*5 speakers in HTML but not in speakers.json (`Alexandros Maganiotis`, `Clara E. Mattei`, `Dave and Helen Edwards`, `Leonⁿ MonoSerieⁿ`, `Meryem Lahrichi`):* These don't appear in any session in the current sessions.json. Either they're appearing in sessions WBBF hasn't yet linked, or they're program-only mentions. Operator review.

**Per Transcription Pipeline spec:** Speaker ID Pass 3 is a 5-pass attribution (cue → role → expertise → confidence → per-turn sanity check); the role/expertise pass relies on speaker bios. AssemblyAI custom vocabulary (per C13 Recording Protocol) also benefits from populated affiliations + names.

### ~~C11a. Sessions.json + speakers.json scaffold refresh~~ ✅ FOLDED INTO C11 RESOLUTION 2026-05-01

The follow-up was completed inline as part of C11. Sessions.json regenerated from latest HTML; speakers.json scaffold refreshed; new speakers enriched; name typos normalized across both files. Re-runnable: stash refreshed HTML at `projects/athens-2026/reference/_source/program_index.html` and re-run `generate_sessions_json.py` → `generate_speakers_json.py` → `populate_speakers_from_program_html.py` chain.

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

### C16. Thinking-tokens-always-0 bugfix (Voice + Persona Pipelines) ✅ LANDED 2026-05-01

**Surfaced 2026-05-01** by inspecting test artifacts after the legitimacy test (Section F). Operator noted thinking_tokens=0 across all artifacts despite thinking_enabled=True + populated thinking_trace text.

**Root cause:** Anthropic SDK 0.94.1's `Usage` object has NO `thinking_tokens` field — verified by [official docs](https://platform.claude.com/docs/en/build-with-claude/extended-thinking) and live SDK probe. Anthropic's API does not expose thinking tokens separately; `output_tokens` is the BILLED total (thinking + response, undifferentiated). LiteLLM and other wrappers don't expose it either; no SDK version has ever surfaced it. The codebase had `getattr(final.usage, "thinking_tokens", 0)` calls in 6 places (Voice 4 + Persona 2) that ALL fell through to default 0.

**Fix landed:** introduced `_estimate_thinking_tokens()` / `_estimate_anthropic_thinking_tokens()` helpers in both pipelines that compute via subtraction:

```python
billed_thinking_tokens = output_tokens - count_tokens(response_text)
```

`count_tokens` is the free Anthropic API; uses Anthropic's billing tokenizer; ~100-300ms per call.

**Files changed:**
- `runtime/flows/voice/_anthropic_call.py` — added `_estimate_thinking_tokens` helper; `stream_voice_call` returns 4-tuple including computed value
- `runtime/flows/voice/step1_private_reasoning.py` — read from new return shape
- `runtime/flows/voice/step2_first_draft_artifact.py` — same
- `runtime/flows/voice/step3_amended_artifact.py` — same
- `personas/flows/shared/clients.py` — added `_estimate_anthropic_thinking_tokens` helper; `call_claude` (both streaming + non-streaming branches) populates `usage["thinking_tokens"]`

**Coverage gap left as-is:** Researcher + Provocateur don't track thinking_tokens at all (never had broken code, no observability either). Adding to those is FU#60-style observability extension; defer until needed.

**Tests:** 223/223 passing on personas after fix; runtime smoke imports clean. Will be exercised on the next Voice/Persona Pipeline run.

**Existing artifacts:** the legitimacy-test outputs (Section F) have thinking_tokens=0 — those were generated before this fix landed. The bug is fixed forward; existing artifacts unchanged.

### C15. Step 2 `consumed_detailed_responses` field — ✅ CLOSED 2026-05-01 (misdiagnosed; field IS populated, just under `lineage.consumed_detailed_responses`)

**Initial filing 2026-05-01** flagged this as unpopulated based on Test 2 inspection. **External review reframed as cartography concern.** **On verification: misdiagnosis, like C6 and C17 before.**

The runtime DOES populate this field correctly — it lives at `artifact.lineage.consumed_detailed_responses`, not at the top-level `artifact.consumed_detailed_responses`. The original Test 2 inspection script read from the wrong location.

Per `step2_first_draft_artifact.py:251-274`: the field is built as a list of `{theme_id, formulation_id, path}` dicts and stored under `lineage`. Verified empirically on Test 2 outputs — all 4 voices have 3-entry lineage lists with full path references back to their Step 1 detailed responses.

**Lineage IS fully auditable from the artifact alone** — operator/journalist/researcher can trace exactly which Step 1 responses fed each Step 2 by reading `artifact.lineage.consumed_detailed_responses[].path`. The cartography claim is preserved.

No code change needed. Closing.

### C17. Legitimacy-test report renderer bug ✅ FIXED 2026-05-01

External reviewer caught: the report's "Continuity → Night 3" section showed `continuity_block_if_night_2 — POSITIONS: (none)` for all 4 voices, suggesting either (a) renderer bug or (b) regression where N3 continuity actually empty. **Diagnosis: (a) renderer bug.** Actual N3 continuity files have field `continuity_block_if_night_3` (not `_if_night_2`); the renderer hardcoded `_if_night_2` for all continuity sections. Fixed in `/tmp/build_report.py` to use `f"continuity_block_if_night_{for_night}"`. Report regenerated; N3 continuity blocks now render correctly with rich content (2.5-4.2K chars per voice). Bugfix verification of `ccc6229` stands — Dostoevsky N3's *"I wrote that pause yesterday"* reference IS legitimate; he had a populated continuity overlay loaded onto his Night 3 card.

### C18. Test 2 confound — focus-on-one branch untested 🟡 (filed 2026-05-01 from external review; refined by Test 2 v2 same day)

External reviewer pushback on Test 2's "all 4 voices wove across all 3" finding: the 3 formulations were all variations on one theme (legitimacy of the invisible), so weaving was the natural choice.

**Test 2 v2 attempted partial fix (2026-05-01):** re-ran with 3 distinct `theme_display_title`s ("Algorithmic Governance and Public Reason" / "Recognition in Automated Decisions" / "The Withdrawal from Public Life") but same formulation bodies. **All 4 voices STILL wove.** Each voice's `focus_rationale` actively articulated a unifying through-line in their own grammar:

- Plato: "three scales — soul, agora, magistrate — bound by a single diagnosis"
- Cleopatra: "the apparatus continues to issue after the subscribing hand has been removed"
- Dostoevsky: "the porog dissolved, the obraz unrendered, the face engineered out of the room"
- Battuta: "isnād — the chain of named guarantors — is what makes a thing addressable"

**Diagnosis:** the title was not the load-bearing variable. The substantive content of the 3 formulations converges conceptually (all about legitimacy / recognition / public-realm questions), and voices have rich enough conceptual machinery to find unity in any 3 inputs that share territory.

**To truly test the focus-on-one branch:** Test 3 needs formulations on **substantively different conceptual territories** — not 3 angles on the same one. Reviewer's structural recommendation ("legitimacy + funeral march + Pnyx walks") was correct; my Test 2 v2 attempt at title-only differentiation was insufficient.

**Status:** Test 2 v2 artifacts at `runs/legitimacy_test2_v2_divergent_titles/`. Side-validation: confirmed `thinking_tokens` fix from `8c47e1f` works (values 2286-4828 across the 4 voices).

**Recommended:** Test 3 with 3 truly-divergent formulations (different conceptual territories). Operator-authored or me-drafted from the 25 Athens recording-session topics. ~7 min wall + ~$15 API.

### C19. Token economics audit — completed 2026-05-01 ✅ + C19a filed for action

**Audit run 2026-05-01.** Tokenized all 4 voices' Step 2 inputs (system + user prompts) via Anthropic `count_tokens` API.

**Findings:**

| Voice | Total input | System (card) | User (Step 1 responses) | System % |
|---|---|---|---|---|
| Plato | 41,643 | 35,468 | 6,175 | 85.2% |
| Cleopatra | 44,437 | 39,153 | 5,284 | 88.1% |
| Dostoevsky | 49,768 | 43,740 | 6,028 | 87.9% |
| Battuta | 49,616 | 42,475 | 7,141 | 85.6% |

**85-88% of Step 2 input is the persona card (system prompt).** User prompt (Step 1 responses) is only 5-7K — small and reasonable.

**Reviewer's $400-600/night estimate was high.** Voice Pipeline doc's current $130-190/night Night 1 forecast is closer; with prompt caching enabled (see C19a), it would drop further to ~$70-120/night Night 1. Athens 3-night total: ~$200-300 with caching vs ~$390-550 currently.

### C19a. Anthropic prompt caching not enabled — Athens-eligible optimization 🟡 (filed 2026-05-01 from C19 audit)

**Surfaced 2026-05-01 by C19 audit.** No `cache_control` calls anywhere in `runtime/flows/`. Each voice's identical 40K-token system prompt is paid at full price across ~5-7 calls per voice per night (Step 1 ×3-5 + Step 2 ×1 + Step 3 ×1 when enabled).

**With Anthropic prompt caching:**
- Add `"cache_control": {"type": "ephemeral"}` on system prompt blocks
- Cache write: 1.25× normal input price (one-time per voice per night)
- Cache reads: 0.1× normal input price (5-min TTL; subsequent calls within window)
- **Net: ~87% savings on system-prompt portion across reads 2-N**

**Athens projection:**

| Stage | Without cache (current) | With cache |
|---|---|---|
| Step 1 input (3 nights) | ~$50-70 | ~$10-15 |
| Step 2 input (3 nights) | ~$22 | ~$5-7 |
| Step 3 input | $0 (skipped per A1) | $0 |
| Continuity | ~$3 | ~$1 |
| **Total input** | **~$75-95** | **~$16-23** |

Plus output tokens (~$50-100 across 3 nights) which caching doesn't affect.

**Estimated:** ~1-2 hr engineering — add `cache_control` headers to system blocks in `_anthropic_call.py` (Voice) + `clients.py` (Persona, if same pattern); verify with one Step 1 call that `cache_creation_input_tokens` + `cache_read_input_tokens` populate correctly. ~1 hr testing on a Plato dryrun to confirm savings materialize.

**Risk:** small. Anthropic prompt caching is a documented stable feature. Only failure mode is if cache TTL (5 min default; 1 hr available with `ephemeral_1h` tier) is too short for a multi-call sequence — but our Step 1 calls are batched + parallel within ~2-3 min total wall, well inside 5 min.

**Pre-Athens-eligible** — saves ~$60-75 across 3 nights (input) and de-risks the cost forecast. Could also be deferred post-Athens since current cost is already in Voice Pipeline doc's stated envelope.

**Decision needed:** land before Athens (low-risk + concrete savings) OR defer to post-Athens (current cost is acceptable).

### C20. Voice-side recurrence patterns + Plato Socrates-death anachronism (handoff to persona thread) 🟡 (filed 2026-05-01)

External reviewer flagged three voice-side moves that recurred across Test 1 nights. Operator added a fourth on inspection: a Plato anachronism that --skip-validation didn't catch.

**1. Plato — Theuth/Thamus reach.** Phaedrus / writing-cannot-answer-when-questioned appears in N1, N2, AND Test 2 synthesis. Canonical Plato, but at Athens with 9-12 briefings landing on him across the conference, if 6+ reach for Theuth/Thamus the audience will notice.

**2. Plato — Socrates referencing his own death (anachronism, found 2026-05-01 inspection).** Test 1 N3 artifact has Plato writing a Socrates ↔ Charmides dialogue with **Socrates as the first-person narrator**. Socrates then asks: *"Charmides — the assembly that voted Socrates' death, was that public life?"* And later: *"by mine it was the day the most just man I knew was killed by counted opinion"* — Socrates calling himself the most just man he knew, in past tense, after his own death. Pattern observed: when Plato writes Socrates as narrator (not as a character encountered by another narrator), Plato fuses his post-Socrates authorial vantage with Socrates' first-person voice. Other 4 Plato artifacts (N1, N2, Test 2, Test 2 v2) avoid the trap by having a non-Socrates narrator encounter Socrates. **The anachronism validator on Night 1 would catch this** (the entire purpose of Pass 7-anachronism). Athens production CLI per A1 has validation ON Night 1 / OFF Nights 2+3 — operator morning review of N1 flags is the correction loop, but **this WOULD ship if it occurred on Night 2/3 without operator catching it.**

**3. Ibn Battuta — Tughluq beard-plucking.** Shaykh Shihāb al-Dīn beard-plucking appears in both N1 and N2 Step 1 with very similar phrasing. Same recurrence concern.

**4. Dostoevsky — closing on suspended judgment.** N2 ends *"they have not yet earned the right to answer it"*; Test 2 synthesis ends *"any justice was ever made."* Close enough that the move-shape may calcify into a verbal tic across more nights.

**Resolution paths (per-voice-card):**
- **Path A:** flag in voice cards. For Plato: `banned_modes` or `quality_criteria` constraint forbidding first-person Socrates referencing his own death; tighten `voice_temporal_stance` enforcement when Socrates is the narrator. For Battuta: stock-anecdote register entry. For Dostoevsky: closing-phrase variation guard.
- **Path B:** continuity overlay carries a "stock examples / closing phrases already deployed" register so voices don't lean on the same moves night after night.
- **Path C:** accept some moves as deliberately-recognized canonical tics; voice-card the others.

**Belongs to persona thread for voice-card resolution.** Filed here (runtime workstream) as a cross-thread observation. Memo for persona thread: `_workspace/planning/voices/MEMO_2026_05_01_recurrence_patterns_from_legitimacy_test.md` (next).

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
| FU#60 | Adaptive thinking observability + temperature compatibility | ✅ FULLY LANDED — voice + persona 2026-04-29; researcher + provocateur + transcription 2026-05-01 (C1+C2+C2a) | Done across all four runtime flow entry-points |
| FU#61 | Voice-side Layer-1 quality_criteria for low-Layer-1-surface forms | 🟡 IMPORTANT — v3 LANDED on Cleopatra + Dostoevsky; persona Pass 4b prompt addition committed; **propagation to Whanganui / Marley / Octopus pending those builds** | Per-voice on next builds |
| FU#62 | Voice Pipeline validation regen-on-flag is unimplemented | ✅ RESOLVED 2026-05-01 (path B — spec updated to match diagnostic-only impl; Nights 2+3 validation OFF) | Done — see A3 |

---

## Section E — Documentation pending

### E1. `docs/AI_Assembly_Voice_Pipeline.md` 🟡

**State:** v2.1, last touched 2026-05-01. Remaining staleness:
- **Step 3 section** — written assuming FU#49E correspondence-shape; needs rewrite once A1 decides (probably to B+ shape with engaged_peers metadata + optional postscript)
- ~~**Validation policy + cost/wall-time**~~ ✅ updated 2026-05-01 (FU#62 path B): Night 1 ~$180-240/~50-80 min wall; Nights 2+3 ~$180-230/~30-45 min wall; Athens 3-night total ~$540-700.
- ~~**Regeneration policy**~~ ✅ updated 2026-05-01: rewritten to "diagnostic only"; if post-Athens autonomous regen wanted, file new item against the contract documented in spec.

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
| 2026-05-01 | C6 CLOSED — misdiagnosed at filing; three names mark intentional domain boundaries (persona-card / voice-internal / publish-audience-facing), not duplicate fields | this doc C6 |
| 2026-05-01 | **Legitimacy-test verification** — operator-driven 4-voice test (Plato/Cleopatra/Dostoevsky/Battuta) on 3 mock formulations of "The Legitimacy of the Invisible." Two tests: (T1) 3-night sequence, 1 formulation/night → verified continuity flow + Convention A end-to-end; cross-night memory observed (Dostoevsky N3: *"I wrote that pause yesterday"*). (T2) Single night, 4×3 formulations → all 4 voices chose `focus_decision: "woven across all three"`, each finding a unifying through-line in their own grammar. All 16 Step 2 artifacts in correct native register (Plato dialogue, Cleopatra prostagma w/ full Greek titulary + γινέσθωι, Dostoevsky Writer's Diary w/ вдруг, Battuta Riḥla w/ Tawakkaltu ʿalā Allāh). Total ~$50-60 API + ~18 min wall. Artifacts: `projects/current-tests/voice-pipeline-dryrun/runs/legitimacy_test1_night{1,2,3}/` + `legitimacy_test2_single_night/`. Briefing template + scripts: `runtime/scripts/` (none new) + voice-pipeline-dryrun/`_legitimacy_test_briefing_template.json`. | runtime test artifacts |
| 2026-05-01 | **Continuity-after-Step-2 bugfix** (Athens-blocking, surfaced by Test 1 design) — under A1 (`--skip-step3` for Athens production), `voice_flow.py:458` had `not skip_step3` in the continuity gate, silently disabling continuity. Fixed: continuity now fires whenever Step 2 completes, regardless of Step 3 status. Verified end-to-end across 3-night sequence in legitimacy test (above). Without this, Athens Nights 2+3 would have launched with no continuity carried forward. `continuity.py` already tolerated `step3_output=None`; only the orchestrator gate was wrong. | runtime/flows/voice_flow.py |
| 2026-05-01 | C11 FULLY CLOSED — Dave + Helen Edwards bios applied (Path B); all other empty-bio speakers verified out-of-recording-scope; 219/224 active populated (97.8%); the 5 still-empty are not in any of the 25 recording sessions | projects/athens-2026/reference/speakers.json |
| 2026-05-01 | ai_assembly schedule LANDED — operator-provided CSV (`recording_sessions.csv`) drove `apply_ai_assembly_flags_from_csv.py`; all 25 sessions matched cleanly (10 N1 + 9 N2 + 6 N3); CSV is now authoritative source-of-truth for transcription scope | projects/athens-2026/reference/sessions.json + runtime/scripts/apply_ai_assembly_flags_from_csv.py + projects/athens-2026/reference/_source/recording_sessions.csv |
| 2026-05-01 | C11 + C11a LANDED — built `populate_speakers_from_program_html.py` (HTML extractor with oneliner-fallback + accent-tolerant name match); refreshed sessions.json (132→146; preserved/re-applied 29 of 31 ai_assembly flags); refreshed speakers.json scaffold (added 30 new speakers, 7 dropped); 217/224 active speakers enriched with title + affiliation + bio (96.9%). Restores Speaker ID Pass 3 accuracy from 40-50% (all-empty) into 70-85% target band. Source HTML stashed at PROJECT_ROOT/reference/_source/program_index.html — re-runnable | projects/athens-2026/reference/{speakers,sessions}.json + runtime/scripts/populate_speakers_from_program_html.py |
| 2026-05-01 | C1 + C2 + C2a LANDED — researcher + provocateur drop temperature/add display:summarized; researcher + provocateur + transcription load_dotenv override=True. All three flows brought into FU#60 + voice-pipeline-pattern compliance | runtime/flows/researcher_flow.py + provocateur_flow.py + transcription_flow.py |
| 2026-05-01 | A2 RESOLVED (mostly — A+B+C+F decided; D deferred; E designed elsewhere). Per-theme editor architecture (not per-voice); all-AI drafting (no polish phase); voice artifacts ship as-is with Provocateur formulation as micro-header; parallel build with microsite specifying editor output schema | this doc A2 + B1/B2/B3/B4 |
| 2026-05-01 | A1 RESOLVED (Option A — Step 3 skipped for Athens; pipeline ships Steps 1+2 only via existing `--skip-step3` flag; cross-voice visibility moves to editor layer + Substack; re-add path documented as ~2-day post-Athens task) | this doc A1 + voice pipeline doc Step 3 §|
| 2026-05-01 | FU#62 RESOLVED (path B — Voice Pipeline spec updated to match diagnostic-only validation impl; Nights 2+3 OFF; cost/wall-time envelope corrected) | docs/AI_Assembly_Voice_Pipeline.md + FOLLOW_UPS.md + this doc A3 |
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
- ~~A1 (Step 3 shape) decided + implemented~~ ✅ done 2026-05-01 (Option A — skipped for Athens)
- ~~A2 (editor layer) architecture decided~~ ✅ done 2026-05-01 (per-theme; all-AI; D deferred; E elsewhere; parallel build per F)
- B1 (editor implementation) — gated on microsite output schema landing
- B2 (microsite) — operator designing; specifies editor output schema
- B2 (microsite) built and deployed
- B3 (broadsheet / Edition Pipeline) built
- B4 (Substack draft pass) built
- **C9 (Provocateur Night 2/3 exclusion filter)** — fires twice during Athens
- **C10 (council_config.json populated from real Provocateur Profiles)** — runtime infrastructure
- ~~C1 + C2 (cross-pipeline compliance) landed~~ ✅ done 2026-05-01 (also C2a load_dotenv override on all three flows including transcription)
- C3 (publish_flow.py end-to-end exercise) completed
- C4 (multi-night sequence dry-run) completed
- ~~A3 / FU#62 path decided~~ ✅ done 2026-05-01 (path B; Athens Night 1 only validation policy)
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
- ~~**C11 (speaker bios populated)** — transcription accuracy~~ ✅ largely done 2026-05-01 (193/202 enriched; 13 name mismatches for operator review). C11a follow-up open for 33 new speakers + sessions.json scaffold refresh
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
