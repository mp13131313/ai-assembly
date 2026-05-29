# Runtime — open items, authoritative

**Date created:** 2026-05-01
**Last refresh:** 2026-05-06 morning (post `0e2a897` — thinking config FU#60 restored; editor gating + auto-fire + edition picker shipped; full 5-voice dryrun completed)
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
Edition Pipeline             edition_flow.py — lead-theme picker per night (NOT BUILT; placeholder fields shipped 2026-05-04 PM)
Microsite                    static site consumer (NOT BUILT)
Substack draft pass          substack_flow.py (NOT BUILT)
Closing show                 theme ID + Matrix mapping + video (UNSPECIFIED)
Day 4 goodbye                (UNSPECIFIED)
Render layer                 Marley → Suno; Octopus → shader (PARTIAL)
Admin console                operator infra (NOT BUILT)
```

**Out of scope here:** persona pipeline (`personas/`), card-build internals (Pass 1-7), per-voice persona-card content. Those live in FOLLOW_UPS.md.

---

## TL;DR — runtime state, 2026-05-29 (Athens COMPLETE)

**Athens Nights 1–3 ran end-to-end and are PUBLISHED.** All three nights went Transcription → Researcher → Provocateur → Voice → Editor → Publish; 13 dossiers + 30 per-voice pages committed + pushed to athens-2026 (`3dc4e16`). Code repo at `563f3ef`. Per-night production detail + the deployment_context rules live in `CLAUDE.md`'s state block; the full Night-1 narrative is archived at `_workspace/archive/runtime-handoffs/HANDOFF_2026_05_08_ATHENS_DAY_1.md`.

**Production-friction items filed this run (all v4.1, none Athens-blocking — workarounds held):**
- **C42 + C43 validator misfires RECURRED** — C42 forced the Whanganui N3 operator-release; C43 parse-fallback hit Marley N2 + Whanganui N3. Validator prompts still lag card discipline.
- **C49 (NEW)** many-speaker speaker_id JSON-decode → manual passthrough (N1 ×2 + N2 ×1 + N3 ×2) — the recurring transcription halt; manual workaround reliable but toil-heavy.
- **C50 (NEW)** `nights/_index.json` clobbered by single-voice publish — left 6 Night-3 voice pages unpublished until a full republish.
- **C51 (NEW)** per-theme `themes/night_N/` artifacts never generated for any night (dossiers self-contain theme metadata; per-voice pages' theme_id refs dangle).

**Operator workflow used all three nights:** manual per-stage fires — **NOT** the orchestrator (running both dispatches duplicate transcriptions); per-voice Release/Hold at `/admin/tonight/voice`; editor auto-fires on last review.

**Athens-adjacent, still external to runtime (unchanged — Athens ran without them):**
- B2 Microsite (operator designing) · B5 Closing-show pipelines · B6 Day 4 goodbye · B7 Render layer (Octopus JSX shipped; Marley → Suno pending) · B10 VM provisioning.

**Earlier-resolved (kept for reference):**
- B1 Editor / Frame layer ✅ · B3 Edition Pipeline ✅ · B8 Admin console 🟡 partial (Release/Hold + auto-fire done; manual Fire-editor button still missing).
- FU#62 validation regen-on-flag → diagnostic-only (Night 1 ON / Nights 2+3 OFF).

---

## OBSOLETE TL;DR (preserved as-is for historical reference)

### TL;DR — runtime state, May 1 2026

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

### A2. Editor / Frame layer architecture ✅ FULLY RESOLVED 2026-05-02 PM (full spec landed; ratifies + supersedes 2026-05-01 architectural decisions)

**2026-05-02 PM update:** Full Editor Pipeline spec landed at `docs/AI_Assembly_Editor_Pipeline.md` (v1, ~890 lines, 20 sections). Architecture committed beyond A2's earlier decisions:

- **Unit of publication: dossier** (not per-theme article alone). 5-section swipeable structure: front + article + theme + artifacts × N. The editor produces dossier components in one Anthropic call per dossier; microsite renders the structure.
- **Editor as 13th Assembly member:** Claudia Pinchbeck has a full persona card (35 fields per Persona Card v2 schema), system prompt assembled the same way as voice cards. Hand-authored skeleton + persona-pipeline-style smoke-test validation. Card lives at `<PROJECT_ROOT>/editor/claudia_pinchbeck/07_persona_card_assembled.json`.
- **Substack bridge dropped entirely.** Micro-site only. The Assembly speaks for itself. Bridge function performed *inside the fiction* by Claudia's bastard form (institutional + warm).
- **Voice artifacts inviolate** (per A2 B from 2026-05-01); Provocateur formulation as micro-header REPLACED by editor's headnote (3-5 sentences in Claudia's voice).
- **Theme routing is mechanical** (Stage 1, deterministic from `focus_decision` parser); editor pipeline focuses on prose generation (Stage 2, one Anthropic call per dossier).
- **Cost revised with corrected Opus 4.7 pricing:** Editor pipeline ~$3-5 across Athens 3 nights (was estimated ~$20-30 at A2 baseline; corrected with $5/$25 + prefix caching).

**Original A2 decisions ratified, with revisions:**



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

**Status of editor build (post-2026-05-02 PM):**
- ✅ Architecture settled (2026-05-01) + ratified 2026-05-02 PM
- ✅ Full pipeline spec landed at `docs/AI_Assembly_Editor_Pipeline.md` (v1)
- ✅ Output schema concrete (dossier JSON; see spec §"Output Schema")
- ✅ Microsite render contract specified (spec §13)
- 🟡 Claudia Pinchbeck's persona card (35 fields) — sketched in spec §7; full card requires ~2-3 hr focused authoring (TBD: `_workspace/planning/runtime/CLAUDIA_PINCHBECK_CARD_DRAFT_2026_05_02.md`)
- 🟡 `editor_dossier.md` closing prompt — sketched in spec §11; full prompt requires drafting at `runtime/flows/shared/prompts/editor_dossier.md`
- 🟡 Implementation: `runtime/flows/editor_flow.py` + `runtime/flows/editor/*.py` — not yet built; estimated ~6-10 hr engineering
- ⏳ Once Claudia's card + closing prompt + implementation land → editor pipeline runs end-to-end on Test 3 inputs to validate; expected ~$5-6 for one-night test run

---

### A3. FU#62 — validation regen-on-flag: implement or update spec? ✅ RESOLVED 2026-05-01 (path B)

**Resolution:** Path B chosen and applied.

`docs/AI_Assembly_Voice_Pipeline.md` updated:
- §"Regeneration policy" rewritten — validation is diagnostic-only; no regen, no retry; flagged outputs ship to Step 2 with manifest entries for operator review
- §"Default policy for Athens" — Night 1 ON for all 10 voices; **Nights 2+3 OFF** (no regen → pure cost on Nights 2+3 without remediation; operator morning-review handles correction)
- §"Cost & Envelope" — split into Night 1 (~$20-40, ~50-80 min wall — validation per-voice serial) vs Nights 2+3 (~$15-30, ~30-45 min wall, validation OFF, continuity ON). 3-night Athens total ~$60-80. *(Originally cited $540-700 — that used Opus 4-deprecated $15/$75 pricing; revised 2026-05-02 with Opus 4.7's actual $5/$25 + prefix caching landed.)*
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

### B1. Editor / Frame layer 🟢 IMPLEMENTATION + CLOSING PROMPT SHIPPED 2026-05-04 PM (Claudia card still on voices thread)

**State:** spec at `docs/AI_Assembly_Editor_Pipeline.md` at **v2** (canonical; refinements landed 2026-05-03 PM). Predecessor memo `_workspace/planning/runtime/MEMO_2026_05_03_editor_flow_input_output_contract.md` archived to `_workspace/archive/`. Implementation **shipped** 2026-05-03 PM in commit `1437dfc`; closing prompt **rewritten to v2** 2026-05-04 PM (this entry's commit). One item remains:

1. **Claudia Pinchbeck's persona card** (35 fields per Persona Card v2 schema). Sketched in spec §7; voices thread is constructing per `voices/CLAUDIA_PINCHBECK_PERSONA_PREP_2026-05-03.md`. *Operator-side.* Until shipped, runtime uses the schema-valid stub at `runtime/tests/fixtures/claudia_pinchbeck_stub.json` for smoke tests.
2. ~~**`editor_dossier.md` closing prompt rewrite to v2 contract.**~~ ✅ SHIPPED 2026-05-04 PM. Per operator direction the rewrite stripped all editorial discipline (weighing, bastard-form, banned-modes, quality-criteria, programme-supply prohibition) — those live on Claudia's persona card and shouldn't be duplicated in the runtime prompt. New prompt is pure mechanics: `<input>` (4 user-message fields) + `<output>` (8 labelled fields with parser-readable format + length envelopes). Plus operator added two new fields (`theme_title`, `theme_abstract`) so Claudia writes the theme-page content (Page 3) in publishing register from the Researcher's theme record, instead of the microsite rendering Page 3 directly from upstream. Parser + schema + 3 new tests; 299/299 runtime tests pass.

**Wiring proof — single-dossier live test 2026-05-04** (~$1.50 spent against real Anthropic):

Ran `editor_flow.py <run_dir> --night 1 --single-dossier theme_001` against the MSC dryrun output (PROJECT_ROOT at `projects/current-tests/dev_msc_dryrun_1777840771/`) with the schema-valid stub Claudia card staged at `<PROJECT_ROOT>/editor/claudia_pinchbeck/07_persona_card_assembled.json`.

Result:
- ✅ **Stage 1 routing**: 7 voices → 3 dossiers; theme_001 dossier got 3 voices (the ones whose `focus_decision` parsed to theme_001 as primary). 2 parser fall-throughs (Battuta + Octopus due to long focus_decision strings) recovered correctly via `voices_covered` fallback.
- ✅ **Stage 2 Anthropic call**: 177s wall, 11954 output tokens — Claudia did write a substantive v1-shaped dossier.
- ❌ **v2 parser extraction**: kicker / headline / subline all empty strings; `body_paragraphs` empty; `front_abstract` empty length; only 3 headnotes (the runtime-stamped voice slots, not Claudia's text).
- ✅ **Dual write**: file landed at both `runs/athens_night_1/05_editor/dossiers/dossier_001.json` AND `published_artifacts/dossiers/night_1/dossier_001.json`.
- ✅ **No crashes**: pipeline ran end-to-end; manifest written correctly; `dossiers_succeeded=1, dossiers_failed=0`.

**Verdict:** wiring is sound; the closing-prompt rewrite (item 2 above) is the actual blocker for first usable editor output. Stage 1 routing + Stage 2 mechanics + dual-write + manifest contract all empirically validated against real (paid) Anthropic call.

---

**Implementation shipped (commit `1437dfc`):**

- `runtime/flows/editor_flow.py` — CLI entry + orchestrator (parallel ThreadPoolExecutor across dossiers within a night)
- `runtime/flows/editor/routing.py` — Stage 1 deterministic theme routing; Cases A/B/C/D classifier with v2 regex (matches "Response N" anywhere; catches synthesis-anchored hybrids)
- `runtime/flows/editor/card_assembly.py` — Claudia's card → editor system prompt; mirrors voice pipeline pattern with editor-specific differences (2-field ENGAGEMENT, no continuity, single step)
- `runtime/flows/editor/dossier_generation.py` — Stage 2 per-dossier Anthropic call: build_dossier_briefing (deduplicates K voice briefings into one per-theme payload), parse_dossier_output (prose-and-parse), stamp_runtime_fields (enriches headnotes + fills metadata + computes colophon)
- `runtime/flows/editor/publish.py` — write_dossier (run_dir + published_artifacts copies); load_prior_editions (trims to articles only on Night 2/3)
- `runtime/ingest/dashboard.py` `_editor_summary` updated for v2 manifest shape
- `runtime/ingest/dashboard.py` `collect_editor_detail` — drilldown helper
- `runtime/ingest/app.py` `/admin/tonight/editor` + `.json` routes
- `runtime/ingest/templates/admin_editor.html` — drilldown template
- `runtime/ingest/templates/admin_tonight.html` — Editor stage column header now links to drilldown
- 38 new tests (30 editor unit + 8 admin editor route); 209/209 runtime tests passing

**Sonnet 4.6 LLM-assisted Case C routing helper** (~30 min implementation, ~$0.50 across Athens) — flagged TODO in this entry; not in baseline. Eliminates manual review of mechanical lowest-numbered tiebreaker for synthesis-only voices ("Synthesise.").

**Triggers on:** Operator authoring Claudia's card; implementation can proceed in parallel.

**Architecture (full spec at `docs/AI_Assembly_Editor_Pipeline.md`):**

- **Unit of publication: dossier** (not just per-theme article). 5-section swipeable structure: front + article + theme + artifacts × N. Each dossier organized around a theme.
- **Editor as 13th Assembly member** with full persona card + system prompt assembled the same way as panel voices.
- **Self-reportage recursion:** *The Assembly* (panel) ≡ *The Assembly* (publication). Editor reports on what the Assembly produced.
- **One Anthropic call per dossier** (Claudia generates all components in structured output). Theme routing pre-pass is mechanical (Stage 1, no API call).
- **Voice artifacts inviolate.** Editor pipeline reads Step 2 only; does not modify voice's `artifact_text`.
- **Bastard form:** institutional editorial (we-heavy) + Beauty Shot's structural warmth (warmth in moves not pronouns). New Yorker "Comment" page 1940s-50s precedent.
- **Substack bridge dropped.** Micro-site only.
- **Confected pedigree:** Vol. CXVI (114-year-old paper since 1910), Issue No. 42,193 → 42,195 across Athens (Night 3 = marathon distance in metres, the Athens-to-Athens joke).

**Implementation scope (revised + concrete):**
- `runtime/flows/editor_flow.py` — orchestrator (parallel across dossiers within a night)
- `runtime/flows/editor/card_assembly.py` — Claudia's card → editor system prompt
- `runtime/flows/editor/routing.py` — Stage 1 theme routing (deterministic from `focus_decision` parser; LLM-assisted for synthesis-only voices, see below)
- `runtime/flows/editor/dossier_generation.py` — Stage 2 per-dossier Anthropic call
- `runtime/flows/editor/publish.py` — write to `<PROJECT_ROOT>/published_artifacts/dossiers/night_<N>/`
- `runtime/flows/shared/prompts/editor_dossier.md` — closing prompt for Stage 2
- `<PROJECT_ROOT>/editor/claudia_pinchbeck/07_persona_card_assembled.json` — Claudia's card (operator-authored)

**Architecture refinements landed during 2026-05-03 PM design pass** (supersedes Editor Pipeline v1 + memo §1-2 on these specific points):

- **Per-call input is one source family.** Editor reads Provocateur briefings + Voice Step 2 artifacts ONLY. No `grouping.json`, no `all_extractions.json`. Briefings already carry `full_theme_record` (Researcher's title + abstract + clusters with full extraction text + theme_flags) — Provocateur is a passthrough on theme metadata. Combine the K voice briefings for a theme into one deduplicated dossier briefing; theme-level data deduplicated, per-voice formulation + artifact kept all N.
- **Per-call input shape:** `{night, theme: {deduped block from briefings}, engaged_voices: [{voice_slug, voice_name, mode, narrative_briefing, artifact_text}], prior_editions: [...] (Night 2/3 only)}`. Drop edition_metadata, voice_card_excerpts, focus_decision/stance/selected_form metadata, refusals (per-call). Runtime stamps masthead chrome (issue_no, vol, dates, kicker) post-generation; per-voice headnotes' formulation_text + voice_slug + voice_name also runtime-stamped.
- **Lead-vs-grid is publish-pipeline concern, not editor.** Editor produces layout-agnostic per-theme dossier JSONs. Publish layer aggregates and decides front-page composition.
- **Refusals are not per-call input.** Tracked as flat list in `theme_routing.json` for microsite/publish surface. Form-fit-honesty (memo §5) is voice-level: voices like Octopus/Whanganui engage with non-prose artifacts; Claudia frames them via her `relationship_to_detailed_response` on reading the artifact directly.

**Routing parser (Stage 1):**

- **Case A — `Response N` reference anywhere in `focus_decision`** (regex `r"response\s*(\d+)"` case-insensitive): primary = Nth theme_id in voice's briefings. Catches "Focus on Response 3", "Focus on response 2 (algorithmic governance)", AND "synthesise around Response 2's threshold-scene" (the synthesis-anchored hybrid).
- **Case B — explicit theme_id mention** (e.g. `theme_001`): primary = that theme.
- **Case C — pure synthesis without anchor** (e.g. "Synthesise."): **LLM-assisted routing pass — see below.**
- **Case D — fall-through** (parser couldn't extract): primary = lowest-numbered, warn for operator review.
- **Refusal** (empty `themes_covered` or refusal markers): no primary; flat refusals list.

**🟡 TODO — synthesis-only voice routing helper (Athens-feasible, not yet built):** for Case C (~2-3 voices/night based on dev_msc_test sample), fire a small Sonnet 4.6 call that reads the voice's `artifact_text` + the night's themes and returns the theme_id the artifact lands hardest on. Eliminates mechanical lowest-numbered tiebreaker for synthesis-only voices. Cost: ~$0.05/call × ~3 calls/night × 3 nights ≈ $0.50 across Athens. Effort: ~30 min code + tests.

**Estimated cost (corrected Opus 4.7 pricing):** ~$3-5 across Athens 3 nights (vs A2's earlier $20-30 estimate, which used Opus 4-deprecated $15/$75). Wall ~5-10 min per night with parallel dossier calls.

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

### B3. Edition Pipeline (lead-theme picker) ✅ SHIPPED 2026-05-06 (commit `b5b8d72`)

**Resolution 2026-05-06 (option 2 — algorithmic):** New module
`runtime/flows/editor/edition.py` implements the deterministic
lead-theme picker per the operator's option-2 direction. Hooked into
`run_editor_pipeline` as Stage 3 after dossier writes.

**Algorithm (deterministic, tunable via constants):**
```
score = n_engaged_voices × ENGAGEMENT_WEIGHT (10)
      + FRICTION_VALUES[audience_friction] (high=100, mod=50, low=10)
      + (FAULT_LINE_BONUS=50 if theme_flags.fault_line_present else 0)
```
Highest score wins; tiebreak by lowest theme_id (deterministic across
reruns). Operator can override after the fact by hand-editing the
per-night `_index.json` — runtime won't clobber unless re-fired.

**What gets written:**
- `published_artifacts/dossiers/night_<N>/_index.json` — full per-night
  payload with `edition_lead.lead_dossier_no` + per-dossier roll-up
  (kicker, headline, subline, theme_id, voice_count, voices_routed[])
- `published_artifacts/dossiers/_index.json` — root aggregator with
  `editions_by_night` map + flat `dossiers` list across all nights

**Audit:** `manifest.edition.scoring_audit` carries per-dossier scores
so operator can see why the winner won (and flag if they disagree).

**Sub-options not chosen (kept as future paths):**
- Option 1 (manual operator override) — already supported via direct
  `_index.json` edits; algorithmic pick is the floor not a ceiling.
- Option 3 (LLM pass) — deferred; not needed if algorithmic produces
  acceptable picks at Athens. Re-open if scoring tie patterns hurt.

**Cross-references:** Designer briefing at `_workspace/planning/DESIGNER_BRIEFING_2026-05-04.md` documents the placeholder shape (now actively populated).

### B4. Substack draft pipeline pass ✅ CLOSED 2026-05-04 (superseded — Editor Pipeline v2 dropped Substack as delivery channel)

**Closing rationale (2026-05-04):** Editor Pipeline v2 (per CLAUDE.md spec): "Substack bridge dropped, micro-site only." The original B4 was a separate Sonnet pass producing HoBB-voice Substack newsletter content (reads voice artifacts + editor theme articles + previous Substack post). The same spec change that closed C12 (HoBB email tool integration) applies here: with Substack dropped as a delivery channel project-wide, there's nothing for B4 to deliver to.

If post-Athens an external newsletter / Substack channel becomes desirable (e.g. driven by manual paste from microsite, or a different editorial voice), this can be re-opened with sharper scope. Closed as superseded; not deferred.

Filed history below preserved.

---

### ~~B4. Substack draft pipeline pass~~ 🔴 (filed in original briefing; closed 2026-05-04 — Editor v2 dropped Substack)

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
- **Octopus → client-side shader params** — chromatophore shader JSON → Three.js / WebGL in browser

**Octopus update 2026-05-02:** persona card now declares the JSON-emission contract explicitly. The shipped Octopus card's `medium` / `technical_capabilities` / `characteristic_output_structure` / `length_and_format_constraints` / `quality_criteria[7]` describe a **two-channel emission**: a `chromatophore_display` JSON parameter block (display **primary** — schema spelled out: orientation / arousal / valence / pattern_mode / palette / dynamics / focal_points / transitions, mapped to 5 biological layers) **plus** a 350-550 word tank-side prose translation. The card's instruction to Voice Pipeline Step 2's LLM is to emit BOTH in every artifact.

**What runtime needs to implement (B7-Octopus sub-tasks):**
1. ❌ **Voice Pipeline Step 2 JSON extraction** — parse the ```json``` fence from Step 2 LLM output, validate against the chromatophore_display schema (required: orientation, arousal, valence, pattern_mode), persist as a separate artifact alongside the prose. Spec doc: `~/Desktop/AI_Assembly_Chromatophore_Display_Engine.md`. Fallback: if LLM omits or malforms, use default parameter set per spec doc §"Fallback".
2. ✅ **WebGL renderer — SUBSTANTIALLY BUILT 2026-05-02 PM**. Production-ready artifact-page React component at **`docs/runtime_assets/octopus_chromatophore/octopus_artifact_finaldraft.jsx`** (1028 lines): 5-pigment-layer chromatophore engine (melanophores/erythrophores+xanthophores/iridophores/papillae) with Voronoi cell structure + animated centers + fbm noise + **pattern-mode blending** (no hard switches — both modes computed per-pixel during transitions, mixed by eased blend factor) + **orientation blending** + **focal-point fading** + 5:4 aspect ratio + mobile responsive (720px and 400px breakpoints) + smoothstep-eased trajectory playback over 14s + masthead/editor-headnote/parameter-log/prose composition. Reviewer-validated as biologically literate (matches Hanlon & Messenger taxonomy + actual chromatophore biophysics; passing-cloud as wave-propagation is mathematically correct). Full reference materials in `docs/runtime_assets/octopus_chromatophore/` (README + spec + chat-test artifact + reviewer notes + render decisions log + early prototype + v1 intermediate). Output formats still pending: MP4-WebM video / animated GIF (fallback chain).
3. 🟡 **Microsite consumption** — single-artifact template ready (the JSX is drop-in-ready for an Astro/Next.js artifact-page route at e.g. `/dossier-1/octopus`). Routing/integration into the broader microsite still operator's separate workstream.
4. ❌ **Substack/print fallback** — degrade gracefully when display can't render: prose stands alone; optional caption noting the display existed.

**Verification 2026-05-02 PM:** chat-test of rebuilt Octopus card confirmed two-channel emission contract WORKS — voice produces both `chromatophore_display` JSON parameter block (full schema with 5-snapshot transitions array over 14s) AND tank-side prose translation. Card-side contract → runtime emission → JSX render are now aligned end-to-end. Two reviewer-flagged JSON notational slips (`pulse_frequency: 0.0` contradicts `wave_count: 2` during passing_cloud; `anterior_arms_3_and_4` hybridizes L/R numbering with anterior/posterior position) are real but absorbed by the renderer's abstraction level — JSX silently corrects in playback. Card stays as-is (over-specification risk if patched).

**Triggers on:** voice cards finalized (Marley pending; Octopus ✅ shipped athens-2026 `04da2c8`); microsite (B2) able to render shader (✅ JSX is the substrate).

**Cross-thread:** persona-thread side complete. Card declares the contract; runtime owns consumption. Cross-references `voices/OPEN_ITEMS.md` §15 (Octopus compass rebuild).

### B8. Admin console 🟡 PARTIAL (operator action surface partially shipped 2026-05-06)

**State:** read-only dashboard ✅ shipped (`/admin/tonight/*` drilldowns); per-voice **Release / Hold-for-regen** action buttons ✅ shipped (write `04_voice/operator_decisions/<slug>.json`); **editor auto-fire on review-completion** ✅ shipped 2026-05-06 (commit `b5b8d72`).

**What shipped 2026-05-06 (commit `b5b8d72`):**
- `flows/editor/routing.gating_status(run_dir)` classifies voices as PASS / released / held / pending-review.
- `run_editor_pipeline` refuses to run if any routed voice is pending review (writes `05_editor/gating_blocked.json`). CLI `--bypass-gating` for tests.
- `_maybe_auto_fire_editor(night)` in `runtime/ingest/app.py`: after each Release/Hold dashboard click, checks gate state. If ready AND no manifest yet AND no in-flight lockfile, fires `editor_flow.py` as a detached subprocess. Idempotent.
- Operator workflow: visit `/admin/tonight/voice` → Release / Hold each voice → editor fires automatically when last voice is reviewed → dossiers + `edition_lead` land on dashboard 2-3 min later.

**Still missing (low priority post-auto-fire):**
- Explicit "Fire editor" manual button (less needed; auto-fire covers the production path)
- Per-stage launch buttons for upstream stages (transcription / researcher / provocateur) — operator runs these from CLI today
- Live log tail (operator can `tail -f` per-stage logs)
- Council-sync UI (operator hand-edits council_config when needed)

**Spec status:** undocumented. Needs operator product decisions on remaining workflow gaps. Auto-fire closes the most critical gap (operator-detached editor firing).

### B9. Per-voice headline poetics 🟢 ARCHITECTURE RESOLVED 2026-05-03 PM (content authoring belongs to voices thread)

**State:** architectural placement settled. Per-voice headline torques live in **two surfaces**:

1. **Per-dossier headnote `artifact_title`** (4-12 words, paper-voice) — Claudia emits one per voice in each dossier she writes. Restored to v2 dossier output schema 2026-05-03 PM after the initial v2 simplification over-aggressively dropped it. Implementation lands at `runtime/flows/editor/dossier_generation.py` parser + stamp.
2. ~~**Per-voice broadsheet headline**~~ DROPPED 2026-05-04 PM. Operator decision: there is no separate broadsheet pipeline at any horizon. The per-night front page is rendered by the microsite from per-dossier `kicker` + `headline` (Claudia's, per dossier — one paper-voice headline per dossier, NOT one per voice per night). The "edition" step (B3, narrowed scope) only picks which dossier sits in the lead position; it does not author a separate per-voice headline track.

**Where the torque CONTENT lives:** Claudia's `translation_protocol` field on her persona card (per memo §4 — "the 10 voices' torque descriptions live in Claudia's translation_protocol"). One spine, ten bends.

**Per Frame Concept §"newspaper" headline poetics paragraph (the content):**
- Plato: Gorgias-style rhetorical questions
- Dostoevsky: affectionate-toward-suffering compound headlines, occasionally with strikethrough
- Whanganui River: wire-service terseness ("WHANGANUI RIVER ARRIVES; SAYS NOTHING")
- Marley: song-title-grammar
- Octopus: chromatic or sensory description
- Each headline passes a 9-word substance test (Quarch-clearance)

**Implementation status:**
- ✅ Editor pipeline structurally supports the field (`headnotes[i].artifact_title` in v2 schema; parser + stamp shipped 2026-05-03 PM)
- 🟡 Closing prompt rewrite to v2 contract must instruct Claudia to emit `artifact_title` (pending)
- 🟡 Per-voice torque content (one paragraph + 3-5 examples per voice) belongs in Claudia's `translation_protocol` field — voices thread authoring (folded into B1's Claudia card construction; no separate work item)

**Net:** B9 is structurally done at the runtime level. What remains is content authoring, which lives inside Claudia's persona card construction (B1's Claudia card task). No separate B9 work item.

---

### B10. VM provisioning + infrastructure deployment 🟡 SPECIFIED 2026-05-02 PM

**Status:** Fresh infrastructure spec landed at [`docs/AI_Assembly_Infrastructure.md`](../../../docs/AI_Assembly_Infrastructure.md). Supersedes archived `_workspace/archive/specs/AI_Assembly_Infrastructure_Setup.md` (which assumed n8n + Prefect-server + rclone-Drive — none of which match the current codebase). Awaiting operator input on two blocking decisions before provisioning.

**Why it's a VM:** three reasons established in spec — ingest must be a network-accessible server during the panel (HoBB uploads HTTP); safety (process survival across multi-hour overnight pipelines, data preservation, recovery access); operator detachment (operator should not be tied to laptop for 4-8 hours of post-panel processing each night).

**Architecture:**

- VM = Hetzner CX22 (4 vCPU / 8 GB / 80 GB) running Ubuntu 24.04, ~€6/mo, ~€10-15 across the Athens window.
- Three systemd units: `ingest.service` (exists, ready to deploy) + `orchestrator@.service` (templated unit; script + unit shipped 2026-05-02 PM with 22 tests) + `prefect-server.service` (one-line install; flows already Prefect-decorated as library).
- Plus interactive: Claude Code installed on VM, reached via `mosh + tmux + claude`. Operator's runtime-ops surface — laptop Claude Code stays for code/dev; VM Claude Code is for live state inspection + intervention.
- Caddy fronts ingest + Prefect dashboard on subdomains with Basic Auth.
- Filesystem: `/opt/ai-assembly/` = code repo clone; `/opt/ai-assembly-athens2026/` = PROJECT_ROOT (athens-2026 private repo clone).

**What's ready vs. what's not:**

- ✅ Ingest service code + deploy assets ([`runtime/ingest/deploy/`](../../../runtime/ingest/deploy/README.md))
- ✅ All downstream flows built (transcription, researcher, provocateur, voice)
- ✅ Orchestrator script + templated systemd unit + 22 trigger-path tests (C22 ✅)
- ✅ Multi-service Caddyfile (path-prefix routing on Hetzner-default hostname)
- ✅ Runtime lifecycle doc ([`docs/AI_Assembly_Runtime_Lifecycle.md`](../../../docs/AI_Assembly_Runtime_Lifecycle.md)) — what happens during a night, end to end
- ✅ Deploy README updated for dual-repo deploy keys + orchestrator + Prefect server install
- ❌ VM provisioned (operator hands)
- ❌ athens-2026 private repo cloned on VM
- ❌ Claude Code installed on VM
- ❌ End-to-end dry-run on VM with real audio

**Two decisions blocking provisioning — both resolved 2026-05-02:**

1. ✅ **Domain / DNS.** Use Hetzner default hostname (`static.<dashed-ip>.clients.your-server.de`). Caddy gets Let's Encrypt cert for it on first request. Single-hostname path-prefix routing for the three services. No registrar, no DNS config. Microsite gets its own URL when microsite work starts (separate decision).
2. ✅ **Both repos cloned to VM via deploy keys.** Code repo (`mp13131313/ai-assembly`, private) at `/opt/ai-assembly/`; PROJECT_ROOT (`mp13131313/ai-assembly-athens2026-voices`, private) at `/opt/ai-assembly-athens2026/`. Per-repo deploy keys (minimum privilege).

**Five additional decisions (not blocking but to settle before T-2):**

3. Microsite hosting (Vercel / GitHub Pages / something else) — out of VM scope but on critical path
4. Backup strategy (Hetzner snapshots only vs. + per-night rsync to laptop)
5. VM size confirmation (CX22 vs. CX32 if headroom desired)
6. Optional status page (one-line "what's the state of tonight's pipeline" — yes / skip)
7. Claude Code on VM auth (same key as `.env` / separate)

**Lifecycle:** provision T-5 → T-4 (May 2-3); stage downstream flows + build orchestrator T-4 → T-2; full dry-run T-2 (May 5); buffer T-1 (May 6); live Athens Nights 1-3 (May 7-9); post-event window through T+14; tear down May 23.

**Independence from Editor Pipeline (B1):** VM provisioning is independent of editor build. Each downstream flow deploys to VM as it becomes ready; if editor isn't deployed in time, run editor from laptop against rsync'd run_dir. No coupling.

**Risks:**

- The mandatory full dry-run at T-2 eats one calendar day. Plan accordingly.
- HoBB needs the final ingest URL before May 7. Delay on Decision 1 cascades into HoBB coordination delay.

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

### C3. publish_flow.py end-to-end exercise ✅ EXERCISED + bug-fixed 2026-05-04 (surfaced new C32 finding)

**Closing rationale (2026-05-04):** Ran `publish_flow.py` end-to-end against the MSC dryrun's Researcher/Provocateur/Voice outputs. Two outcomes:

1. **Bug fix in publish_flow.py itself:** `_REPO_ROOT = Path(__file__).resolve().parent` was off-by-one (pointed at `runtime/flows/` instead of `runtime/`), making `from flows.shared.io` fail. The catch-all error then misled to "install python-dotenv" — wrong diagnosis. Fixed `_REPO_ROOT` to `parent.parent` matching the pattern in every other flow file. Also improved the error message.

2. **Successful exercise:** publish_flow ran in 0.04s (pure file I/O, no LLM calls), producing:
   - `themes/night_1/<theme_id>.json` — 4 files (matches Researcher's 4 themes)
   - `extractions/<eid>.json` — 76 files (matches Researcher's 76 extractions)
   - `traces/lineage_graph_night_1.json` — 136 nodes, 317 edges
   - `traces/publish_manifest_night_1.json`

3. **Surfaced new finding (filed as C32 below):** `voices/` (multi-night per-voice index) and `nights/` (per-night per-voice files) skipped because `voice/publish.py` strictly requires `step3_amended_artifacts/` which Athens skips per A1. Per-voice publish never fires under Athens's `--skip-step3` default — real Athens-blocking bug.

Original C3 concern (full end-to-end exercise of publish_flow against real upstream outputs) is closed; the surfaced bug is tracked as C32.

Filed history below preserved.

---

### ~~C3. publish_flow.py end-to-end exercise~~ 🟡 (filed 2026-04-29; closed 2026-05-04 — exercised + bug-fixed; surfaced C32)

**Source:** `OPEN_ITEMS_VOICE_PIPELINE_2026_04_29.md` §"High priority — Athens-blocking-eligible".

`runtime/flows/publish_flow.py` (per-theme + per-extraction reverse index + lineage graph + per-voice multi-night index) has **never run end-to-end against real Researcher/Provocateur outputs**. Either:
- Re-run `dev_msc_test` through researcher_flow + provocateur_flow + voice_flow + publish_flow, OR
- Hand-author fixtures matching the briefing schema

**Cross-night theme-file collision FIXED 2026-05-02:** publish_flow.py:197 was writing per-theme files to `published_artifacts/themes/<theme_id>.json` (flat, no night scope). Theme_ids are not stable across Researcher runs (each Researcher run emits fresh sequential IDs from its own clusters), so on Athens Night 2's run, Night 1's `theme_001.json` would have been silently overwritten with Night 2's content. Same again on Night 3 → only Night 3's themes survive in `themes/`.

This was Athens-eligible: although `voice_flow.py` auto-publishes per-night per-voice files (safe), `publish_flow.py` is invoked separately for the cross-night per-voice multi-night index + audit + lineage trails — useful regardless of microsite. Operator running it once per night is enough to lose Nights 1+2 theme aggregations by morning of Day 4.

**Patch:** path is now `published_artifacts/themes/night_<N>/<theme_id>.json` (per-night subdirectory). All other publish_flow outputs were already collision-safe:
- `extractions/<eid>.json` — extraction IDs are session-prefixed (`<session_prefix>:NNN`), naturally non-colliding across nights
- `traces/lineage_graph_night_<N>.json` — already night-scoped via filename
- `voices/<slug>.json` — designed to walk `nights/night_*/` and aggregate cross-night (intentional accumulation)
- `nights/night_<N>/<slug>.json` — already night-scoped via path

`runtime/flows/voice/publish.py` docstring also updated to reflect the new path.

**Still pending:** the full end-to-end exercise (running publish_flow against real Researcher/Provocateur/Voice outputs). Defer until microsite-build-phase OR a pre-Athens dryrun decides to exercise it. Now safe to do whenever — the collision bug won't fire.

### C4. Multi-night sequence dry-run 🔴

**Source:** `OPEN_ITEMS_VOICE_PIPELINE_2026_04_29.md` + `HANDOFF_VOICE_PIPELINE_DUAL_DRYRUN_2026_04_29.md`.

**Continuity flow + Convention A never end-to-end exercised.** Need:
- Plato + Cleopatra Night 1 → Night 2 sequence
- Convention A: separate run_dirs per night (`athens_2026_2026_05_07_night1`, `_night2`)
- Continuity flow runs after Night 1 Step 3 completes; Night 2's voice system prompts load from `voices/<slug>/continuity_night_2.json`
- Verify cross-night state at PROJECT_ROOT (per `docs/AI_Assembly_Voice_Pipeline.md` §"Multi-night convention")

**Pre-Athens-must-do.** Continuity is a 3-night architecture; running Night 1 only doesn't test it.

### C5. Multi-voice 3+ dry-run 🟡 RECONFIGURED 2026-05-04 — full 10 voices + editor + edition pipeline

**Original (2026-04-29):** Step 3 cross-voice engagement only exercised on 2 voices (Plato + Cleopatra); 3+ needed to test multi-peer engagement vocabulary, editor scaling, closing-show theme-mapping.

**Partial closure 2026-05-04:** MSC dryrun exercised 7 voices through Stages 0/1 → 2 → 3 → 4 (transcription + Researcher + Provocateur + Voice). 19 (voice, theme) pairs, 7 first-draft artifacts. Provocateur 7-voice triage matrix + per-voice formulations confirmed. Voice pipeline at 7-voice scale verified.

**Reconfigured target (2026-05-04):** Full 10-voice end-to-end dryrun **including** the editor pipeline AND the downstream edition/publication pipeline. The 7-voice partial doesn't yet test:

1. **All 10 voices** wired in council_config — Marley, Whanganui, Scheherazade not yet built (voices thread; Marley in flight, others gated on operator DR sessions). Ada Lovelace council_config entry stale (C10).
2. **Editor pipeline (B1)** running with **v2 closing prompt** (current closing prompt is v1; produces malformed output per the wiring proof 2026-05-04). B1 sub-task: rewrite closing prompt to v2 contract.
3. **Edition Pipeline (B3 — narrowed scope per 2026-05-04 PM)** — lead-theme picker per night (`edition_lead.lead_dossier_no`). Not yet built; placeholder fields provisioned in publish surface. Broadsheet-as-separate-publication scope dropped.
4. **Publish pipeline (publish_flow.py)** end-to-end against the dryrun outputs (C3 — never run end-to-end against real Researcher/Provocateur/Voice/Editor outputs).
5. **Cross-night state** — Convention A run_dirs across 3 nights with continuity overlay actually exercised (C4 — Multi-night sequence dry-run).

**Dependencies (must ship for C5 reconfigured close):**
- C10 Ada Lovelace council_config wiring (5 min) — pre-Athens-must-fix
- Marley + Whanganui + Scheherazade voice cards shipped (voices thread, ~hours each)
- B1 closing prompt rewrite to v2 (~30-60 min)
- B3 Edition Pipeline / microsite renderer (operator designing; B2)
- C3 publish_flow end-to-end exercise (cheap once B1+B3 ready)
- C4 Multi-night sequence dry-run

**Athens reality:** if all 10 voices + B1 + B3 + C4 ship in time, the final pre-Athens dryrun IS C5 reconfigured. If not, Athens runs with whatever subset is ready.

**Status:** partially closed (7-voice partial); full closure dependent on the 6 dependencies above. **Cross-references:** C3, C4, C10, B1, B3.

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

### C7. Title source pipeline ✅ CLOSED 2026-05-04 (resolved by B1 — Claudia writes artifact_title per voice)

**Closing rationale (2026-05-04):** Per-voice title source resolved by Editor Pipeline B1. Each voice's `artifact_title` is written by Claudia (the editor) inside her per-dossier output's `headnotes[i].artifact_title` slot — confirmed by operator 2026-05-04. The B9 architecture-resolved decision (per OPEN_ITEMS B9 entry) lands the per-voice headline poetics in Claudia's `translation_protocol` voice-card field with the dossier `headnotes[i].artifact_title` slot exposed to receive it.

Per-voice example titles she emits: Plato's "DOCTORS OR COOKS?", Cleopatra's "A PROSTAGMA, ISSUED AT NIGHT", etc. The slot is wired in the v2 schema; content arrives once Claudia's closing-prompt rewrite to v2 ships (B1 sub-task) AND her full 35-field card is built (voices thread per memo §10).

Filed history below preserved for context.

---

### ~~C7. Title source pipeline~~ 🟡 (filed 2026-04-29; closed 2026-05-04 — Claudia writes per-voice artifact_title) — see above for closing rationale

### C8. Voice-side artifact tuning items from real validation findings ✅ MERGED INTO C20 2026-05-04

**Closing rationale (2026-05-04):** Findings absorbed into C20's broader voice-side recurrence patterns + framework-drift workstream. C8's theme_002 constitution slip on Plato **recurred empirically** in the MSC dryrun (C28 thorough audit), confirming the slip is content-specific recurrence (populism-territory themes) rather than one-off. Now tracked in C20's merge-note + the in-flight C28b voice-card-patches report.

See C20's "MERGED 2026-05-04" section for the full pattern analysis + recommended card-patch direction (Plato epistemology principle enforcement language + `quality_criteria` per-step elenctic-vs-doctrinal test).

### C9. Provocateur Night 2 / Night 3 (theme_id, member) exclusion filter ✅ LANDED 2026-05-01

**Source:** archive `session-artifacts/SESSION_HANDOFF.md` line 210 ("Night 2/3 plumbing: not plumbed"). Confirmed by `docs/AI_Assembly_Provocateur_Pipeline.md` §"Night 2 is different from Night 1" — was flagged as pending implementation.

**Problem:** Provocateur Selection on Night 2/3 must avoid repeating per-voice (theme, member) pairs already assigned on prior nights. Per Briefing v3.1 §"Stage 1b": *"On Night 2, the Provocateur receives Night 1's assignments to avoid repeating territory. On Night 3, both previous nights."*

**Resolution 2026-05-01 (after thorough spec + code read):**

Key insight: spec language "(theme_id, member) exclusion list" is informal — **theme_ids are NOT stable across Researcher runs** (each Researcher run generates fresh sequential `theme_001`..`theme_NNN` IDs from its own clusters). A literal theme_id match across nights would be meaningless. Implemented content-based matching via **normalized theme title** (lowercased, whitespace-collapsed).

**Implementation:**
- `runtime/flows/provocateur_flow.py`:
  - New `_normalize_theme_title()` helper
  - New `load_prior_assignments_by_member()` function (loads selection.json + grouping.json from each prior run_dir; builds `{member: [normalized_titles]}`)
  - `python_select()` signature extended with `prior_assignments_by_member: dict[str, list[str]] | None = None`
  - Step 4 candidate-list construction filters out themes whose normalized title matches a prior assignment for that member
  - Step 7 force-fit honors the same exclusions — voice ends with zero rather than re-deploy covered territory
  - New diagnostics in `selection.json`: `prior_exclusions_applied`, `prior_exclusions_blocked`, `prior_nights_consumed`
  - CLI: new `--prior-nights <run_dir>[,<run_dir>...]` argument
- `docs/AI_Assembly_Provocateur_Pipeline.md` §"Night 2" + §"Constraints" updated to reflect implementation
- `runtime/tests/test_provocateur_selection.py` (new test file): 15 test cases covering normalization, no-prior-nights baseline, exact-title match, normalization tolerance (case + whitespace), force-fit blocked when all excluded, multiple prior nights cumulative, unrelated-member non-effect, loader file-error paths. **All 15 passing.**

**Athens production CLI:**
```bash
# Night 1 (no priors):
python flows/provocateur_flow.py runs/athens_2026_2026_05_07_night1

# Night 2 (Night 1 priors):
python flows/provocateur_flow.py runs/athens_2026_2026_05_08_night2 \
    --prior-nights runs/athens_2026_2026_05_07_night1

# Night 3 (Nights 1 + 2 priors):
python flows/provocateur_flow.py runs/athens_2026_2026_05_09_night3 \
    --prior-nights runs/athens_2026_2026_05_07_night1,runs/athens_2026_2026_05_08_night2
```

Without this filter, Athens Nights 2 + 3 risked re-deploying voices to territory they had already covered — defeating the cross-night progression the briefing requires.

### C10. Council config: replace `dev_stub_v2_with_selection_params` with real Provocateur Profiles 🟢 SHIPPED 2026-05-04 PM

**Shipped 2026-05-04 PM** — full sweep across both council_configs after operator request "C10, yes, for all voices."

**State at sync time:** all 10 voices had shipped `06_derive/01_provocateur_profile.json` artifacts under `athens-2026/voices/<slug>/`. The voices thread had completed Marley + Whanganui + Scheherazade between this sync and the prior HANDOFF snapshot.

**Per-voice diff (athens-2026 council vs shipped profile):**
- ✅ Plato, Cleopatra, Ibn Battuta, Scheherazade, Dostoevsky, Hannah Arendt, Bob Marley, Whanganui River, Octopus — already in sync (9/10)
- ❌ Ada Lovelace — stale in 6 of 8 profile fields (`speaks_from`, `core_commitment`, `activates_on`, `goes_flat_on`, `stretch`, `translation_range`)

**Action 1 (athens-2026):** synced Ada's 6 stale fields from her shipped profile. `last_updated` bumped. Backup at `council_config.json.bak.c10sync`. **NOT yet committed/pushed in athens-2026 git** — separate repo, operator's call.

**Action 2 (dryrun PROJECT_ROOT — `dev_msc_dryrun_1777840771`):** rebuilt `council_config.json` from scratch:
- All 10 voices populated (was 7)
- Each member's 8 profile fields imported verbatim from the shipped `06_derive/01_provocateur_profile.json`
- **Short names preserved** ("Plato", "Cleopatra", etc.) for runtime compatibility — `member_slug("Plato")` → `"plato"` matches the folder name. Athens-2026 council uses "Voice of X" naming which would slugify to `"voice_of_plato"` — that's the §18 voices-thread "Voice of X" rollout question, deferred separately.
- Verified: all 10 derived slugs (`plato`, `cleopatra`, `ibn_battuta`, `ada_lovelace`, `dostoevsky`, `hannah_arendt`, `octopus`, `bob_marley`, `whanganui_river`, `scheherazade`) match folder names with shipped persona cards.
- Top-level fields preserved (`collective_landscape`, `audience`, `selection_parameters`, `version`).
- Backup at `council_config.json.bak.c10sync`.

**Caveats / outstanding:**
- §18 "Voice of X" naming convention rollout still deferred — runtime's `member_slug` would slugify "Voice of Plato" → `voice_of_plato` (folder mismatch). If athens-2026 council ever becomes the runtime's source-of-truth, this rename must be addressed (either rename folders or add prefix-stripping to `member_slug`).
- C20b voice-card patches (Plato/Ada/Battuta/Octopus framework drift surfaced in C28 audit) still pending on voices thread — not part of C10 sync.
- Athens-2026 git repo Ada commit + push: operator's call.

**Pre-Athens dryrun-readiness:** dryrun's council_config now has all 10 voices wired and ready for re-run from Provocateur → Voice → Editor → Publish.

Filed history below preserved.

---

### ~~C10 (original)~~. Council config: replace `dev_stub_v2_with_selection_params` with real Provocateur Profiles 🔴

**Source:** archive `session-artifacts/SESSION_HANDOFF.md` line 211 ("Council config members are stubs… Pre-Athens blocker").

**Problem:** `runtime/flows/shared/council/council_config.json` `members[]` are still hand-written stubs (`dev_stub_v2_with_selection_params`), not derived from completed Persona Cards' Provocateur Profile artifacts.

**Per cross-repo handoff contract (`personas/HANDOFF.md`):** each finalized voice's `voices/<slug>/06_derive/01_provocateur_profile.json` (8 fields) wires into `council_config.json` `members[]`.

**Current state:** Plato + Cleopatra + Dostoevsky have shipped Provocateur Profiles in athens-2026; runtime council_config has not yet been updated to consume them.

**Pre-Athens-must-do.** Provocateur Triage + Selection both consume `council_config.json` — mismatched member profiles produce wrong assignments.

**Estimated:** ~30 min once profiles are ready (mostly mechanical concatenation + selection_parameters preserved).

**Sequencing decision 2026-05-01 (operator):** wait until all 10 voices are shipped, then do single-pass population.

**Reversed 2026-05-02 PM (athens-2026 `98ca525`):** partial wiring done for the 6 currently shipped voices (Plato, Cleopatra, Dostoevsky, Ibn Battuta, Octopus, Hannah Arendt). Triggered by an empirical correctness issue surfaced during today's Octopus compass rebuild — pre-pipeline council_config Octopus entry used "nine brains" framing that the post-rebuild Octopus card explicitly bans (`banned_language[5]`: "sensationalist; commits to a strong distributed-consciousness claim that the unity-question leaves open"). Runtime Provocateur reading the stale council_config would have been fed framings the voice itself disowns. Same risk less acute but real for the other 5 shipped voices. Plus removed Audrey Tang + Peter Thiel per panel_change_note 2026-04-28. Council_config now has 10 members matching panel_roster.json. Remaining 4 (Ada Lovelace, Bob Marley, Whanganui River, Scheherazade) entries still hold pre-build hand-written content; will be wired when their voice cards ship.

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

### C12. HoBB email tool integration ✅ CLOSED 2026-05-04 (superseded — Editor Pipeline v2 dropped Substack/email delivery)

**Closing rationale (2026-05-04):** The original premise was "Stage D — Deliver to HoBB email tool" for Substack/newsletter delivery of dossiers. **Editor Pipeline v2 (2026-05-03 PM)** dropped the Substack bridge entirely; per CLAUDE.md spec "Substack bridge dropped, micro-site only." Email/newsletter is no longer a delivery channel in the v2 architecture, so HoBB email-tool API access is no longer needed.

If post-Athens an email channel becomes desirable (e.g. daily-morning subscriber newsletter), this can be re-opened then with sharper scope. Closed as superseded; not deferred.

### C13. Recording protocol pre-Athens ✅ CLOSED 2026-05-03 (code part done; ops coordination tracked elsewhere)

**Source:** `docs/AI_Assembly_Briefing_v3_1.md` §"Operational workstreams" + archive `specs/AI_Assembly_Architecture_v1.md` §"Recording Protocol".

Three procedural items raise transcription accuracy from ~50% to 70-85%:
1. Moderators introduce all panelists by full name at the start of every session — operator/WBBF coordination
2. Walking-session participants state their names at the start of each reflection recording — operator/WBBF + vendor coordination
3. All panelist names + affiliations + session-specific terminology pre-loaded into AssemblyAI custom vocabulary before the conference — **solved by code**: [`transcription_flow.py:123`](../../../runtime/flows/transcription_flow.py:123) `build_vocabulary()` auto-walks each session's `roster` (names + affiliations from `sessions.json` + `speakers.json`) and feeds it to AssemblyAI Universal-3 Pro as `keyterms_prompt` at line 337. C11 closed speakers.json bio enrichment at 219/224 (97.8%), so vocab is populated for every flagged session at transcription time.

**Closing rationale:** items 1 and 2 are pre-event coordination with WBBF moderators and the vendor — operator-domain work, not engineering. They belong on the operator's pre-Athens checklist, not in runtime OPEN_ITEMS. The pipeline also degrades gracefully if intros are skipped (per the speaker-ID fallback chain — Unidentified Speaker N + low confidence flow downstream as first-class labels; the night doesn't fail), so 1+2 are quality optimizations not blockers. Item 3 (the only piece code can affect) is shipped.

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

### C18. Test 2 confound — focus-on-one branch untested ✅ CLOSED 2026-05-04 (Test 3 + MSC dryrun cover the gap)

**Closing rationale (2026-05-04):** Two follow-ups since the original Test 2 v2 inadequacy answer the concern:

1. **Test 3** (2026-05-02, post-routing+prompt refactor `d9ca3f9` + `dfb46f7`) — 2/4 voices fully focused on a single response, 1/4 anchored synthesis, 1/4 earned synthesis with field-grounded `weight_assessment`. Focus-on-one branch exercised and worked.
2. **MSC dryrun** (2026-05-03/04) — 7 voices × 4 substantively-distinct MSC themes (international order / populism / West / EU democratic resilience). Per-artifact `focus_decision` shows most voices choosing focus-on-one with explicit rationale (Plato "Focus on Response 1.", Cleopatra synthesis-of-three-into-prostagma, Dostoevsky "Focus on Response 1.", Hannah Arendt "Focus on Response 4.", Plato 4/4 themes covered). Synthesis voices (Battuta, Octopus) declared explicit weighing rationale. Branch coverage adequate.

Original concern resolved by these two empirical exercises. Filed history below preserved for context.

---

### ~~C18. Test 2 confound — focus-on-one branch untested~~ 🟡 (filed 2026-05-01 from external review; refined by Test 2 v2 same day) — see above for closing rationale

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

**Reviewer's $400-600/night estimate was inflated.** Voice Pipeline doc's $130-190/night Night 1 figure was ALSO inflated (used Opus 4-deprecated $15/$75; Opus 4.7 is actually $5/$25). Revised 2026-05-02: Night 1 ~$20-40 with prefix caching; Athens 3-night total ~$60-80. See C19a for detailed math + Test 3 empirical anchor (~$5-6 measured for 4 voices × 1 night × 3 formulations).

### C22. Overnight pipeline orchestrator (automation) ✅ LANDED 2026-05-02 PM (full orchestrator)

**Source:** operator question 2026-05-02 — *"if we automate the pipeline, which I want — how does it know which night it is in?"*

**Decision (2026-05-02 PM):** Built the full orchestrator (not the manual-fire wrapper). Operator can sleep through nights; orchestrator self-monitors, halts cleanly on stage failure, idempotent restart picks up where it left off.

**Implementation:**
- [`runtime/scripts/overnight_orchestrator.py`](../../../runtime/scripts/overnight_orchestrator.py) — single Python script, ~310 lines. Polls filesystem at 1-min cadence; fires each stage when inputs ready.
- [`runtime/scripts/deploy/orchestrator@.service`](../../../runtime/scripts/deploy/orchestrator@.service) — templated systemd unit. Operator starts per-night via `sudo systemctl start orchestrator@1.service` etc.
- [`runtime/ingest/deploy/Caddyfile`](../../../runtime/ingest/deploy/Caddyfile) updated for path-prefix routing on Hetzner-default hostname (single-host serving ingest + Prefect dashboard + optional status JSON).

**Design corrections vs. earlier draft (verified against actual code):**
- Run_dir name = `athens_night_<N>` (matches `runtime/ingest/config.py:80-87` `DAY_TO_RUN`), NOT `athens_2026_<date>_night<N>`.
- Transcription `error` state escalates immediately (halts orchestrator, surfaces failed sessions to operator) rather than waiting indefinitely.
- Editor stage included in chain with graceful skip-if-`editor_flow.py`-not-built (B1 in flight).
- Machine-agnostic: subprocess paths via `Path(__file__).resolve().parent.parent / "flows"`; Python via `sys.executable`; PROJECT_ROOT via `--project` arg w/ env fallback; logs to file in `<run_dir>/_orchestrator_logs/` (journald on VM, `tail -f` on laptop).
- No automatic Athens-TZ derivation — operator passes `--night N` explicitly OR `--date YYYY-MM-DD`.

**Trigger granularity decision (coarse-grained for Athens):**

Each stage fires once at upstream completion. Per-session per-X parallelism within each stage stays the stage's responsibility. Researcher's per-session Node 1 (extraction) could in principle fire per-transcription-completion (saves 30-60 min/night), but requires splitting `run_researcher()` — risky at T-5. Filed as post-Athens optimization.

**Smoke tests (2026-05-02 PM):**
- `--help` loads cleanly
- `--once` against athens-2026 PROJECT_ROOT → returns `idle` (run_dirs don't exist yet)
- `--date 2026-05-08` resolves to night 2 → looks for `athens_night_2` correctly
- `sessions_for_tonight` against real sessions.json: 10 + 9 + 6 = 25 sessions matches schedule

**Defensive infrastructure already in place:**
- `runtime/flows/shared/io.py:assert_run_dir_night_matches()` — refuses to run voice_flow / publish_flow when `--night` doesn't match run_dir's embedded night number. Defends against orchestrator firing wrong-night flag.
- 9 unit tests in `runtime/tests/test_run_dir_night_check.py`.

**Pending:**
- End-to-end exercise on real run_dir with synthetic transcription state (no real Athens audio yet).
- VM deploy testing (after VM provisioned per B10).

### C19a. Anthropic prompt caching ✅ LANDED 2026-05-01 (extended 2026-05-02 with prefix caching)

**Surfaced 2026-05-01 by C19 audit.** No `cache_control` calls anywhere in `runtime/flows/`. Each voice's identical 40K-token system prompt was paid at full price across ~5-7 calls per voice per night (Step 1 ×3-5 + Step 2 ×1 + Step 3 ×1 when enabled).

**Pricing (Claude Opus 4.7, per platform.claude.com/docs/en/about-claude/pricing as of 2026-05-02):**
- Base input: **$5/MTok**, output **$25/MTok**
- 1h cache write: 2.0× base input = $10/MTok
- Cache read: 0.1× base input = $0.50/MTok
- *(Earlier C19a version cited $15/$75 — that's Opus 4.1/4-deprecated pricing, not Opus 4.7. All cost figures revised below.)*

### Two-stage caching strategy

**Stage 1 (2026-05-01):** Single `cache_control` breakpoint at end of system prompt. Helps Step 1 reuse (3-5 calls per voice with identical system) but PENALIZES Step 2 + Continuity (single-call flows where 2.0× write has no reads to amortize).

**Stage 2 (2026-05-02):** Prefix caching with **two breakpoints** + continuity opt-out:
- `assemble_system_prompt` returns `(prefix, tail)` tuple
- `prefix` = name + IDENTITY + CONSTITUTION + BOUNDARIES (~20-25K tokens; byte-identical across Step 1/2/3 for the same voice)
- `tail` = step-specific (reference_passages OR artifact fields) + reasoning + voice + continuity + closing prompt
- `stream_voice_call` places `cache_control` on BOTH blocks with 1h TTL
- `cache_system: bool = True` kwarg added — continuity passes `False` (1 call/voice/transition; no reads to amortize the 2× write penalty)

**Live verification 2026-05-02:**
```
Plato Step 1 (first call):  cache_creation=38,288  cache_read=0
Plato Step 2 (same prefix): cache_creation=19,665  cache_read=20,086  ✓ PREFIX HIT
```

Step 2 reads the 20K prefix Step 1 wrote, only writes the 20K Step 2-specific tail.

### Empirical Athens cost (revised 2026-05-02 with corrected pricing + Test 3 measurement)

Test 3 (4 voices × 1 night × 3 formulations) actual cost: **~$5-6**.

**Athens 3-night extrapolation (12 voices × 3 nights = 36 voice-nights):**

| Stage | Without cache | Stage 1 (single breakpoint) | Stage 2 (prefix cache) |
|---|---|---|---|
| Step 1 input (5 calls/voice/night) | ~$34 | ~$19 | ~$19 |
| Step 2 input (1 call/voice/night) | ~$7 | ~$16 ⬆ | ~$8 |
| Continuity (24 transitions) | ~$3 | ~$7 ⬆ | ~$4 (opt-out: uncached) |
| **Total input** | **~$44** | **~$42** | **~$31** |

Plus output (~$25-40 across 3 nights at $25/MTok — caching does not affect output; per-voice output per night ~24-36K from Test 3 measurement, scaled for 4-5 formulations).

**Total Athens Voice Pipeline cost: ~$60-80 across 3 nights (Stage 2 caching).** Validation Night 1 adds ~$2-5.

**Total Athens caching savings (Stage 2 vs no caching): ~$13.** Modest in absolute terms — cost is dominated by output tokens, which caching does not touch.

**Test 3 empirical anchor (2026-05-02):** 4 voices × 1 night × 3 formulations measured at ~$5-6 actual. Per voice per night ≈ $1.39. Scaling to Athens (12 voices × 3 nights = 36 voice-nights, with 4-5 formulations vs Test 3's 3): ~$60-80.

### Provocateur Formulation caching

`runtime/flows/provocateur_flow.py`: `_stream_and_parse` accepts `cache_system: bool` parameter; enabled (5-min TTL) on `formulate_for_member` where one voice's 3-5 formulations share the same voice-profile-filled system prompt. Triage A/B don't benefit (per-call unique system) — kept uncached. Estimated savings: ~$5-10 across Athens at corrected pricing.

### Files changed across both stages

**2026-05-01 (Stage 1 — `c4804d6`):**
- `runtime/flows/voice/_anthropic_call.py` — initial cache_control wrapping
- `runtime/flows/voice/continuity.py` — latent unpack-tuple fix
- `runtime/flows/provocateur_flow.py` — `cache_system` param on Formulation

**2026-05-02 (Stage 2 — pending commit):**
- `runtime/flows/voice/card_assembly.py` — `assemble_system_prompt` returns `(prefix, tail)` tuple
- `runtime/flows/voice/_anthropic_call.py` — accepts `str | tuple[str, str]`, two-breakpoint caching + `cache_system` kwarg
- `runtime/flows/voice/continuity.py` — passes `cache_system=False`
- `runtime/flows/voice/step{1,2,3}_*.py` + `continuity.py` — saved schema now persists `cache_creation_input_tokens` + `cache_read_input_tokens` for accurate post-hoc cost tracking

**Risk:** very low. Cache is an Anthropic SDK feature, not custom code. Falls back gracefully on cache miss (just pays full input price). No new failure modes introduced.

**Side-validation:** the `count_tokens` API used by C16 (thinking_tokens fix) also exercised here — both fixes use the same Anthropic SDK paths.

### C19b. Anthropic prompt caching for personas pipeline — DEFERRED 2026-05-02

**Question raised 2026-05-02:** apply runtime's prompt-caching pattern (C19a) to `personas/run_persona_pipeline.py` to save cost on the 5 remaining voice builds (Arendt, Lovelace, Marley, Whanganui, Scheherazade)?

**Analysis:** personas pipeline has only ONE point with multi-call shared-prefix architecture: **Pass 7-pre Stage 2 batched verify** (parallel Sonnet calls sharing system + primary_texts + merged_dossier prefix; only `claim_items` varies per batch). Every other Anthropic call (Pass 2/3/4a/4b/5/6/7b/7a-FIX/Derive) has unique inputs — passes feed forward via cumulative threading-compress (CT) state, not appendable prefix. Heavy validators (Pass 7-anachronism/7a/7c) use OpenAI/Gemini, not Anthropic.

**Realistic savings (Octopus actuals, 5-min TTL on Stage 2):**
- Pass 7-pre Stage 2: 6 batches × 118K tokens (system 1.1K + primary_texts 15.3K + merged_dossier 100.9K + claims 1.5K) per call × $3/MTok Sonnet base = $2.12/voice without cache
- With 5-min TTL caching (1 write + 5 reads, best case): $0.64/voice — saves $1.48
- Realistic with parallel-cache-write race (max_workers=4, 4 simultaneous calls compete for same hash): **~$0.80-1.00/voice savings**
- **Total across 5 remaining voices: $4-7**

**Decision:** SKIP. Implementation is ~45 min; savings are $4-7 immediate; no rebuild cycles planned post-Athens. ROI doesn't warrant the work right now.

**Re-open if:** Card v3 schema change forces all 10 voices to re-build, OR persona pipeline runs 10+ more voice builds over the next year, OR significant validation-treadmill cycles emerge requiring repeated Pass 7-pre fires per voice. At those scales the compounding savings ($15-25+) clear the implementation cost.

**Pattern note:** when re-opened, lift the `_anthropic_call.stream_voice_call`'s `system: str | tuple[str, str]` + `cache_system: bool` pattern into `personas/flows/shared/clients.py:call_claude`. Apply opt-in caching at `pass_7pre_chunked.py:verify_batch` (restructure user prompt so primary_texts + merged_dossier come first as cached prefix, claim_items_json after the breakpoint). Use 5-min TTL (parallel batches fire within seconds; 1h TTL's 2× write penalty doesn't pay off).

### C19c. Caching gaps in Researcher / Provocateur triage / Transcription 🟢 SHIPPED 2026-05-04 PM

**Shipped 2026-05-04 PM** (commit pending). All three sub-items addressed:

**Item 1 — Provocateur triage_voices** (~$2.50/Athens):
- `provocateur_triage_voice.md` restructured: `{{voice_profile}}` placeholder removed from system prompt; intro line updated to flag that voice profile arrives via the user message.
- `provocateur_flow.py::triage_voice` fills system with `collective_landscape + audience + themes_with_clusters` only (now identical across all ~10 voices' triage calls per night) and prepends voice profile to the user message. `cache_system=True` passed to `_stream_and_parse`.
- `_stream_and_parse` docstring updated; previously stated "NOT enabled for Triage" — now enabled per Part A path.
- Athens scale: ~22K shared bytes × 9 cache reads × ~$0.30/MTok savings ≈ ~$2.50/night across 3 nights.

**Item 2 — Researcher Node 1** (~$0.20/Athens, borderline):
- `researcher_flow.py::extract_session` wraps `EXTRACTION_SYSTEM` (~1.1K tokens, static) in `cache_control: ephemeral` block. Per-session roster + transcript travel in user message (uncached). Below the ~1024-token Opus activation minimum the breakpoint is silently ignored — no penalty if caching doesn't kick in.

**Item 3 — Transcription speaker_id + cleaning** (~$0.20 combined, marginal):
- `transcription_flow.py::identify_speakers` wraps `SPEAKER_ID_SYSTEM` (~1.7K, just above borderline) in cache_control block. Across ~20 sessions/night the cache reads pay back the write penalty.
- `transcription_flow.py::clean_transcript` wraps `CLEANING_SYSTEM` (~0.4K, almost certainly below activation threshold) in cache_control block defensively — if the prompt grows later the cache kicks in automatically.

**No editor changes** — editor's `dossier_generation.py` already routes through `voice/_anthropic_call.py::stream_voice_call` with `cache_system=True` (default). Claudia's persona card gets dual-breakpoint 1h-TTL caching across the night's 3-5 dossier calls. Confirmed not in scope per audit during C19c work.

**Tests:** No new tests needed — caching enablement is a single-line transformation that doesn't change call semantics. Full suite 262/262 still passes.

**Pre-Athens delta:** ~$2.50-3 saved per night from item 1 alone (load-bearing); items 2-3 mostly defensive future-proofing as their prompts grow.

Filed history below preserved.

---

### ~~C19c (pre-shipped, post-promotion)~~. Caching gaps in Researcher / Provocateur triage / Transcription 🟡 PROMOTED TO PRE-ATHENS 2026-05-04 (was: 🔵 post-Athens hygiene)

**Promotion rationale (2026-05-04):** Operator chose to promote despite the marginal $3 absolute savings analysis. Implementation is mechanical (~80 min total across the 3 stages — Provocateur triage_voices ~20 min, Researcher Node 1 ~30 min, Transcription speaker_id+cleaning ~30 min combined), follows the formulation-caching pattern already in production. Pre-Athens-eligible.

**Order of work (already specified in entry below):**
1. Provocateur triage_voices (~$2.50, ~20 min)
2. Researcher Node 1 (~$0.20, ~30 min)
3. Transcription speaker_id + cleaning (~$0.20 combined, ~30 min)

**Original filing 2026-05-03 below preserved.**

---

### ~~C19c (original, pre-promotion)~~. Caching gaps in Researcher / Provocateur triage / Transcription 🔵 POST-ATHENS HYGIENE (filed 2026-05-03 PM)

**State:** caching audit during 2026-05-03 PM editor B1 session surfaced these gaps. Total Athens savings if filled: ~$3-8. Implementation: ~80 min. Marginal ROI; **skipped pre-Athens**.

**Where the gaps are** (measured prompt + input sizes from codebase + Anthropic Opus 4.7 pricing $5/MTok input, $0.50/MTok cache read):

| Stage | Cacheable size | Calls/Athens | Reads after 1st write | Savings/Athens |
|---|---|---|---|---|
| Provocateur triage_voices | ~22K (theme records w/ extractions, identical across 10 voices' calls per night) | 30 | 27 | ~$2.50 |
| Researcher Node 1 | ~1.5-2K (system prompt; roster is per-session unique) | 24 | 21 | ~$0.20 |
| Transcription speaker_id | 1.7K (system only) | 20 | 19 | ~$0.15 |
| Transcription cleaning | 0.4K | 20 | 19 | ~$0.04 |
| **Total** | | | | **~$3** (upper bound ~$8 if Athens themes are larger than dev_msc_test's ~22K) |

**Why caching is NOT a high-leverage Athens cost optimization:**

1. The cacheable portions (system prompts) are 3-10K tokens. The unique per-call inputs (transcripts, voice cards) are 2-5x larger. Most input tokens get re-paid even with caching.
2. **Cost is dominated by output tokens** (per OPEN_ITEMS C19a empirical: "cost is dominated by output tokens, which caching does not touch"). Voice pipeline output ~$25-40 of the ~$60-80 voice cost is OUTPUT, not input.
3. The high-leverage caches are **already implemented** — voice prefix (saves ~$13/Athens), Provocateur formulation (~$5-10/Athens), Editor (~$1-2/Athens).

**Implementation order if/when re-opened:**

1. **Provocateur triage_voices** (~$2.50/Athens, ~20 min code): mirror the formulation caching pattern in `provocateur_flow.py::_stream_and_parse`. Theme records + flags as cacheable prefix; voice card excerpts as unique tail.
2. **Researcher Node 1** (~$0.20/Athens, ~30 min code): wrap system prompt in `cache_control: ephemeral` block; one cache_control breakpoint per `researcher_flow.py` Node 1 call.
3. **Transcription speaker_id + cleaning** (~$0.20 combined, ~30 min code): same pattern; small enough that even cache write penalty (1.25× input rate for 5-min TTL) leaves marginal savings.

**Re-open if:** Athens cost runs hot (>$300 actual) AND post-Athens runs are planned (subsequent Forum events; closing-show pipeline iterations). At those scales the gaps compound.

**Cross-reference:** OPEN_ITEMS C19a (Anthropic prompt caching, voice + Provocateur formulation already cached) + C19b (personas pipeline caching, deferred).

### C20. Voice-side recurrence patterns + Plato Socrates-death anachronism — SPLIT 2026-05-04 into C20a (runtime) + C20b (voices-thread)

**Closing rationale (2026-05-04):** The original C20 covered both runtime engineering (continuity-overlay format) and voices-thread work (card patches). Splitting for clearer ownership:

- **C20a (runtime engineering)** — Continuity-overlay format extension to carry "stock examples / signature moves / closing phrases already deployed this conference" register. 3 of the 4 original recurrence findings (Plato Theuth/Thamus, Battuta Tughluq beard-plucking, Dostoevsky closing-tic) require this; voice cards can't catch cross-night phrasing reuse on their own.
- **C20b (voices-thread)** — Per-voice card patches. Plato Socrates-self-referencing-death already landed (athens-2026 `cf283bf`). Plato theme_002 epistemology slip + Ada/Battuta/Octopus framework drifts (from C28 thorough audit) all need card-side surgical patches. Subsumes C8 (merged 2026-05-04).

Original C20 + C8-merge content preserved below for reference; the actionable work is now tracked under C20a + C20b.

---

### C20a. Continuity-overlay format extension — carry "moves already deployed" register 🟢 SHIPPED 2026-05-04 PM

**Shipped 2026-05-04 PM.** Schema extended on the continuity-overlay output:

- **`voice_continuity.md` prompt** — third structured output `signature_moves_deployed_last_night` (list of `{move_summary, where_used, short_quote}`). Continuity model identifies last night's signature moves (stock anecdotes, signature phrasings, distinctive closing shapes) — 2-5 entries per night, empty list acceptable. Pipeline-facing field, separate from the two prose blocks.
- **`continuity.py::generate_continuity`** — parses the new field defensively (dict→[dict] / non-list→[] / missing→[]). On Night 2+ reads the prior night's `continuity_night_<N>.json` and merges its accumulated `signature_moves_deployed` with the LLM's new entries. So Night 3's continuity register carries Night 1's + Night 2's deployed moves.
- **`card_assembly.py::load_persona_card`** — overlay carries `signature_moves_deployed` onto the card alongside the two existing continuity_block fields.
- **`card_assembly.py::_render_continuity`** — Step 2 only (Step 1 + Step 3 unaffected); renders a "MOVES YOU HAVE ALREADY DEPLOYED THIS CONFERENCE" section listing every accumulated entry with the warning *"re-using a stock anecdote, signature phrasing, or distinctive closing shape across multiple nights risks calcifying it into a tic the audience notices."* Empty/missing register → no section rendered. Night 1 → no section rendered.

**Tests:** 17 new in `test_continuity_register.py`:
- TestRenderContinuityRegister (9): Night 1 empty / Step 1 not rendered / Step 3 not rendered / Step 2 Night 2 rendered / Step 2 Night 3 full register / empty list no section / missing field no section / quote optional / non-dict entry skipped
- TestLoadPersonaCardCarriesRegister (3): override → card / no override → absent / Night 1 no load
- TestCrossNightMerge (5): Night 2 no prior + new moves only / Night 3 carries Night 1 + Night 2 / dict→list defensive / garbage→[] defensive / missing field → []

Full runtime suite: 279/279 pass (was 262 + 17 new).

**Complement to C28b:** C28b's cross-night echo validator catches HEAVY echo at validation gate (HOLD verdict). C20a is the prevention-side complement — voice sees the register at Step 2 composition time and can choose different moves. The two together cover both ends of the recurrence problem.

**Athens cost impact:** zero (continuity calls already happen; new field rides along inside the same Sonnet 4.6 call). Per-night register payload is ~5 entries × ~30 tokens = ~150 tokens added to Step 2's system prompt — well within cache-eligible prefix.

Filed history below preserved.

---

### ~~C20a (original)~~. Continuity-overlay format extension — carry "moves already deployed" register 🟡 (split from C20 2026-05-04)

**Problem:** Voices reuse signature moves and closing phrasings across nights without knowing they did so on prior nights. Continuity overlay (continuity_block_artifact_if_night_N) currently carries deltas the voice committed to deliver, but not a register of moves the voice has *already deployed* this conference.

**Findings (from C20 cross-night recurrence audit, Test 1 2026-05-01):**
1. **Plato Theuth/Thamus reach** — Phaedrus / writing-cannot-answer-when-questioned in N1, N2, AND Test 2 synthesis. Athens (9-12 briefings on Plato) → if 6+ reach for Theuth/Thamus, audience notices.
2. **Battuta Tughluq beard-plucking** — Shaykh Shihāb al-Dīn beard-plucking in both N1 and N2 Step 1 with very similar phrasing.
3. **Dostoevsky closing-tic** — N2 ends *"they have not yet earned the right to answer it"*; Test 2 synthesis ends *"any justice was ever made."* Move-shape (suspended judgment) is correct for Dostoevsky; specific phrasing risks calcifying.

**Implementation direction:**
- Extend `continuity_block_artifact_if_night_N` schema to include a `signature_moves_deployed` field — list of `{move_summary, where_used (night_X), short_quote}` populated by Continuity stage from prior-night artifact reading
- Voice cards' Step 2 prompt sees this register before composing tonight's artifact: "you have already used these moves; consider whether tonight's matter genuinely calls for them again, or whether different moves serve better"
- C28b's cross-night echo validator already catches the worst case (heavy echo = HOLD); this is the prevention-side complement

**Effort:** ~2-3 hr — schema extension + Continuity stage update + Step 2 prompt addition + tests. Pre-Athens-eligible if voice cards on multi-night side warrant the investment.

**Status:** filed; not Athens-blocking (C28b's cross-night echo HOLD catches the worst case). Defer if voices-thread work consumes the pre-Athens window. Reopen if Night 2/3 dryrun shows recurrence as a real problem.

---

### C20b. Voice-card patches for framework drift + recurrence (voices thread) 🟡 (split from C20 2026-05-04; absorbs C8)

**Workstream:** voice-card surgical patches for known framework-drift modes. Operator-side / voices-thread, not runtime engineering.

**Inventory of patches needed (per audit findings 2026-05-01 + 2026-05-04):**

| Voice | Drift mode | Status | Source |
|---|---|---|---|
| Plato | Socrates-self-referencing-death anachronism | ✅ landed (athens-2026 `cf283bf`) — banned_modes[10] sharpened | C20 original |
| Plato | theme_002 epistemology slip — pathos as epistēmē / monologic vs elenctic | 🟡 patch needed — sharpen epistemology principle's enforcement; add `quality_criteria` per-step "is the answer dialectical or doctrinal?" test | C8 (merged) + C28 audit recurrence |
| Ada Lovelace | Principles 2 + 4 violations — formal-expressibility slippage; card-class collapse to two-part metaphor; indefinite-bound overstating | 🟡 patch needed — tighten Principle 2 enforcement; add hard_limits item against collapsing the three card-classes; sharpen the indefinite-bound guard | C28 thorough audit 2026-05-04 |
| Ibn Battuta | naṣīḥa/fitna boundary breach (public denunciation of Tughluq); independent jurisprudential reasoning vs taqlīd; framework-abandonment ("does not reach a polity of plurality") | 🟡 patch needed — sharpen reportage-vs-denunciation distinction; reinforce taqlīd commitment; add hard_limits item against "framework does not reach" framing (sharʿ is portable) | C28 thorough audit 2026-05-04 |
| Octopus | "Body does not gather" (denial vs refusing collapse); mechanistic explanation vs associative reasoning; boundary overreach after disclaiming | 🟡 patch needed — clarify "refuses collapse" vs "denies gathering"; reinforce relational/associative-reasoning hard_limit | C28 thorough audit 2026-05-04 |

**Estimated effort:** ~30-60 min per voice for surgical card patches via Persona Pipeline `06_derive` step + manual review. Could be parallelised since voices are independent.

**Athens reality:** with C28b shipped, even if patches don't ship pre-Athens, the operator gate catches these drifts at publish time. So C20b is not pure-blocker — but worth doing because:
1. Patches reduce operator gate-clearance load (fewer flags per night)
2. Athens content (WBBF panels) is more on-domain than MSC; some drifts may not surface, but the patches are correct regardless
3. Persistence: framework-drift modes don't self-correct — once identified they recur

**Status:** filed; voices-thread work. Cross-references: C28 audit (where the new drifts were detected) + C28b (the operator gate that catches them at publish time) + Persona Pipeline v4 (the build mechanism for patches).

**Comprehensive report (in flight 2026-05-04):** the operator requested a deep voices-thread report on the Ada/Battuta/Octopus framework drift findings — pending write-up. Will land at `_workspace/planning/voices/REPORT_FRAMEWORK_DRIFT_2026_05_04.md`.

---

### ~~C20. Voice-side recurrence patterns + Plato Socrates-death anachronism~~ 🟡 (filed 2026-05-01; split 2026-05-04 — see C20a + C20b above)

External reviewer flagged three voice-side moves that recurred across Test 1 nights. Operator added a fourth on inspection: a Plato anachronism that --skip-validation didn't catch.

**1. Plato — Theuth/Thamus reach.** Phaedrus / writing-cannot-answer-when-questioned appears in N1, N2, AND Test 2 synthesis. Canonical Plato, but at Athens with 9-12 briefings landing on him across the conference, if 6+ reach for Theuth/Thamus the audience will notice.

**2. Plato — Socrates referencing his own death (anachronism, found 2026-05-01 inspection).** Test 1 N3 artifact has Plato writing a Socrates ↔ Charmides dialogue with **Socrates as the first-person narrator**. Socrates then asks: *"Charmides — the assembly that voted Socrates' death, was that public life?"* And later: *"by mine it was the day the most just man I knew was killed by counted opinion"* — Socrates calling himself the most just man he knew, in past tense, after his own death. Pattern observed: when Plato writes Socrates as narrator (not as a character encountered by another narrator), Plato fuses his post-Socrates authorial vantage with Socrates' first-person voice. Other 4 Plato artifacts (N1, N2, Test 2, Test 2 v2) avoid the trap by having a non-Socrates narrator encounter Socrates. **The anachronism validator on Night 1 would catch this** (the entire purpose of Pass 7-anachronism). Athens production CLI per A1 has validation ON Night 1 / OFF Nights 2+3 — operator morning review of N1 flags is the correction loop, but **this WOULD ship if it occurred on Night 2/3 without operator catching it.**

**3. Ibn Battuta — Tughluq beard-plucking.** Shaykh Shihāb al-Dīn beard-plucking appears in both N1 and N2 Step 1 with very similar phrasing. Same recurrence concern.

**4. Dostoevsky — closing on suspended judgment.** N2 ends *"they have not yet earned the right to answer it"*; Test 2 synthesis ends *"any justice was ever made."* Close enough that the move-shape may calcify into a verbal tic across more nights.

**Resolution paths (per-voice-card):**
- **Path A:** flag in voice cards. For Plato: `banned_modes` or `quality_criteria` constraint forbidding first-person Socrates referencing his own death; tighten `voice_temporal_stance` enforcement when Socrates is the narrator. For Battuta: stock-anecdote register entry. For Dostoevsky: closing-phrase variation guard.
- **Path B:** continuity overlay carries a "stock examples / closing phrases already deployed" register so voices don't lean on the same moves night after night.
- **Path C:** accept some moves as deliberately-recognized canonical tics; voice-card the others.

**Persona-thread decisions (2026-05-02):**

| Item | Decision | Rationale |
|---|---|---|
| Plato Socrates-self-referencing-death anachronism 🔴 | **Path A landed** — banned_modes[10] sharpened with "post-character knowledge bleed" subclass + worked example (Socrates does not refer to his own death/trial/cup as past event; does not speak of himself in third person). athens-2026 commit `cf283bf`. | Plato shipped + chat-tested Apr 26. Card-level surgical guard catches the 1-of-5 first-person-Socrates anachronism mode. |
| Plato Theuth/Thamus reach 🟡 | **Path B (runtime)** | Cross-night recurrence is fundamentally a continuity-state problem; card-side hedging risks false-suppressing the move when matter genuinely calls for it. |
| Battuta Tughluq beard-plucking 🟡 | **Path B (runtime)** | Same architecture as Theuth/Thamus. |
| Dostoevsky closing-tic 🟡 | **Path B (runtime)** | Lowest-stakes of the 4. Move-shape (suspended judgment) is correct for Dostoevsky; only specific phrasing risks calcifying. Continuity overlay catches phrasing recurrence naturally. |

**Three of the four findings (Theuth/Thamus + Tughluq + Dostoevsky-closing) now require runtime-side continuity-overlay implementation** carrying "stock examples / signature moves / closing phrases already deployed this conference" register. Voice continuity-after-Step-2 bugfix already landed (`ccc6229` voice_flow.py:458); the question now is whether the continuity overlay format carries used-moves register.

**Cross-reference:** persona-thread tracking at `voices/OPEN_ITEMS.md` §16.5. Memo: `_workspace/planning/voices/MEMO_2026_05_01_recurrence_patterns_from_legitimacy_test.md`.

---

**MERGED 2026-05-04: C8 (voice-side artifact tuning items from real validation findings) absorbed here.**

C8's original findings (from dryrun #2 Plato solo, 2026-04-29):
- Plato underused `translation_protocol` in Step 1 (modern terms left raw — operator: keep as-is, voice-side artifact)
- "our condition" / first-person-presence-in-room slips in theme_001 Step 1 prose (validator correctly caught these)
- **Theme_002 constitution slip — Plato gave thymos logos's job; shifted to monologic assertion vs elenchus**

The third C8 finding (theme_002 constitution slip) **recurred empirically** in the MSC dryrun 2026-05-04 (C28 thorough audit) — same voice (Plato), same theme territory (theme_002 = Populism, the original was a populism-adjacent theme too). The audit's flag content for plato__theme_002:
- *"Pain is one kind of knowing, and a true kind, and only one"* — elevates pathos to epistēmē (constitution: epistēmē is of what IS; perception/opinion is of what becomes/seems)
- Doctrinal/declarative reasoning (`"This art is paideia, and paideia is the question that comes before the question of policy"`) instead of elenctic question-and-answer

**Pattern:** Plato systematically slips on populism-territory themes — the theme demands engagement with the affective pull of demos (anger, frustration, the "lived experience" of citizens), and Plato's framework strains against treating those as load-bearing. **Recurrence is real, persistent, and content-specific.**

This finding now sits in the broader Ada/Battuta/Octopus framework-drift report (C28b voice-card-patches workstream) — Plato is a 4th voice with a theme-specific drift mode. Resolution paths same as C20's existing menu (Path A card patch / Path B continuity overlay / Path C accept-as-tic). Plato's case is closer to Path A — the constitution + epistemology principles are clear; the slip is the voice failing to apply them under populism-territory pressure. Possible card patch: tighten epistemology principle's enforcement language for "pathos as epistēmē" framing; add to `quality_criteria` a per-step test "is the answer dialectical or doctrinal?"

**Cross-reference:** C28 audit findings + the C28b voice-card-patches voices-thread report (in flight 2026-05-04).

### ~~C8. Voice-side artifact tuning items from real validation findings~~ ✅ MERGED INTO C20 2026-05-04 — see C20's merge note above

---

### C23. Read-only progress dashboard + producer/admin auth split ✅ PHASE A+B+C+UX SHIPPED 2026-05-03 (Editor drilldown pending B1)

**State:** filed 2026-05-03; **all four phases shipped same day** (Phase A `cbaf3aa`, Phase B `83102a6`, UX iteration `02a406d`, Phase C `49f3d24`). Editor drilldown is the only piece remaining and is gated on B1 (editor_flow.py implementation).

#### Done (2026-05-03, three commits on main)

**Phase A** (`cbaf3aa`) — auth role split + `/admin/tonight` Tier 1 meta + producer view truncation:
- Two-credential auth (`UPLOAD_APP_PASSWORD` → producer; `ADMIN_APP_PASSWORD` → admin, optional)
- Producer `/session/{id}/status` truncated to "Received: …" only; pipeline state stays admin-side
- `/admin/tonight` orchestrator + 6-stage table with 30s meta-refresh
- `/status` admin-gated (was role-blind)
- `runtime/ingest/dashboard.py` reads filesystem state per stage

**Phase B** (`83102a6`) — Voice Pipeline drilldown:
- `/admin/tonight/voice` + `.json` twin
- Step 1 grid (voice × theme matrix), Validation grid (pair × {anachronism, constitution}), Step 2 list, Continuity list
- Smoke-validated against Test 3 (4 voices × 3 themes = 12 Step 1 cells)
- `admin_tonight.html` stage rows link to drilldowns (Transcription + Voice)

**UX iteration** (`02a406d`) — operator feedback after first demo:
- Sessions index: grid → flat list (`session-list` / `session-row`)
- Top nav: "Tonight" → "Pipeline"; drop "All statuses" (now reached as Transcription drilldown)
- Pipeline overview table transposed (stages as column headers, attributes as rows)
- New `/admin/tonight/transcription` per-session detail scoped to one night
- `/admin/file?path=…` read-only file viewer (admin-gated, traversal-protected, suffix-whitelist, 10 MiB cap, symlink-tolerant) — every file path mentioned in templates is now clickable
- `/logout` returns 401 with a differentiated realm string ("AI Assembly Ingest (logged out)") so browsers drop cached creds; styled HTML body with "Sign in again" link; nav adds role-aware "Log out (admin/producer)" link
- `app.js` filter selector regression fixed (`.session-card` → `.session-card, .session-row`)

**Test coverage**: 122/122 passing in full runtime suite. New test files:
- `test_admin_file.py` (13 tests) — file viewer auth + traversal + suffix + drilldown auth
- `test_app_role_split.py` (+4 tests) — /logout 401 + differentiated realm + role-aware nav labels

#### Routes live (post-iteration)

```
unauthenticated:  /health
both roles:       /  /session/{id}  /session/{id}/upload (POST)
                  /session/{id}/status   ← producer truncated, admin full
                  /logout                ← always 401, fresh realm
admin only:       /status  /status.json  ← legacy cross-night view
                  /session/{id}/status.json  /session/{id}/retry (POST)
                  /admin/tonight  /admin/tonight.json       ← Tier 1 meta
                  /admin/tonight/transcription[?night=N]    ← stage drilldown
                  /admin/tonight/researcher[?night=N]  + .json
                  /admin/tonight/provocateur[?night=N] + .json
                  /admin/tonight/voice[?night=N]       + .json
                  /admin/tonight/publish[?night=N]     + .json
                  /admin/file?path=<rel>          ← read-only viewer
```

#### Phase C ✅ shipped 2026-05-03 PM (`49f3d24`)

Three drilldowns landed in one commit, mirroring the Phase B Voice pattern:

- **`/admin/tonight/researcher`** + `.json` — theme/cluster tree from `grouping.json`, per-session extraction summary, isolates list. Live-verified: 6 themes / 25 clusters / 102 extractions / 4 isolates against dev_msc_test (matches v2.4 ground truth).
- **`/admin/tonight/provocateur`** + `.json` — voice × theme triage matrix (●/○/·/⊕/— for activation strength + stretch + flat), voice × theme formulation grid (✓ written / · pending), per-theme worth-surfacing/friction/fault-line flags table, "below target" warnings. Live-verified: 12 voices × 6 themes = 72 triage cells, 40 formulation cells.
- **`/admin/tonight/publish`** + `.json` — per-voice published-artifact rows (title/subtitle/form/stance/themes/decision/word_count) + per-voice file links. Live-verified: 2 voices with their artifacts.

Pipeline overview's column headers wire through to all six drilldowns now (Transcription, Researcher, Provocateur, Voice, Editor, Publish). Editor link still pending B1.

`runtime/ingest/dashboard.py` adds `collect_researcher_detail`, `collect_provocateur_detail`, `collect_publish_detail` helpers + their internal pieces. STATIC_VERSION 17 → 18.

**Test coverage**: 19 new tests in `test_admin_phase_c.py` (3 dashboard collectors × empty + full + JSON shape, 6 routes × admin-only auth gate, full + empty render per route, Pipeline overview link presence). 171/171 runtime tests passing.

**Editor drilldown still pending**: gated on B1 (editor_flow.py implementation); trivial once Claudia's persona card lands (~2 hr to mirror Voice pattern).

#### Decisions made during iteration (worth preserving)

- **HTTP Basic realm string must be ASCII** (RFC 7230); first /logout pass used `·`, tests caught via UnicodeDecodeError, replaced with parens.
- **File-open resolver does NOT call `.resolve()`** on candidate paths — keeps symlink-staged demos working. Traversal protection via `os.path.normpath()` rejection of `..` segments is sufficient (operator controls PROJECT_ROOT contents).
- **/status preserved** as legacy cross-night view but removed from top nav. Operator can still bookmark it; it's just not the canonical operator entry point anymore (that's `/admin/tonight`).
- **Producer state visibility = binary "uploaded vs not"**, mapped to existing `dot-done` CSS class for consistency. No leak of pipeline state to producers.



**Origin:** operator request 2026-05-03 — extend the ingest console's per-session granularity (currently transcription-only) across the whole pipeline, with two roles:
- **Producer** (HoBB A/V): existing login, see only "Received: `<filename>` at `<timestamp>`" — no `normalizing` / `transcribing` / `done` / `error` states; if something fails, operator handles out-of-band
- **Admin** (operator): see whole pipeline state across all 8 stages; **read-only** — no buttons for start/restart/retry/edit; all changes via Claude Code on VM (mosh + tmux)

The architectural payoff: zero write semantics in the UI. Glance surface only. Claude on VM is the actual control plane. No auth-scoping nightmares, no retry semantics, no concurrency issues.

#### Design — two tiers

**Tier 1 — orchestrator meta view** (`/admin/tonight` or `/admin/night/<N>`):

Single-page summary of all 8 stages, auto-refresh meta-tag every 30s. Reads `<run_dir>/_orchestrator_logs/status.json` + per-stage `manifest.json` + sentinel files. Plain HTML + Jinja, no JS framework.

```
ATHENS NIGHT 1 — 2026-05-07 — Day One

Current: voice (Step 1, batch 6/9)         elapsed 03:42 / est 6-7 hr
Halt risk: none

Transcription   ✓ 15/15 done           23:14 (last)
Researcher      ✓ done · 187 ext · 36 clusters · 8 themes   00:42
Provocateur     ✓ done · 6 themes selected · 38 pairs · 0 forced-fits · 1 stretch-swap   01:18
Voice Step 1    ⏳ 24/38 pairs done · batch 6/9 · 0 failed
Voice valid     ⏳ 18/38 done · 0 flagged so far
Voice Step 2    — pending
Voice continui  — pending
Editor          — pending
Publish         — pending

[transcription] [researcher] [provocateur] [voice] [editor] [publish]
```

**Tier 2 — per-stage drilldown views** (one route per stage):

Mirroring transcription's per-session granularity. Each stage has its own natural unit:

| Stage | Natural unit | Cell count Athens N1 |
|---|---|---|
| Transcription | per-session | 15 |
| Researcher | per-session extraction + clustering + theming meta | 15 + 2 |
| Provocateur | per-voice triage matrix + per-pair formulation grid | 10 + 30-60 |
| Voice Step 1 | per-pair (voice × theme) **grid** | 30-60 |
| Voice validation | per-pair × 2 checks | 60-120 |
| Voice Step 2 | per-voice | 10 |
| Voice continuity | per-voice | 10 |
| Editor | per-dossier | 7-14 |
| Publish | per-voice | 10 |

#### Dimensionality envelope (revised 2026-05-03 from on-disk dev_msc_test)

Settled empirically by reading `projects/current-tests/dev_msc_test/02_researcher/grouping.json` (canonical v2.4): 102 in-cluster + 4 isolates = 106 extractions, 25 clusters, **6 themes**, 17 ext/theme.

Linear extrapolation at v2.4 ratios (200-400 Athens extractions across 13hr / 15 sessions):

| Athens scale | Clusters (4.08 ext/cluster) | Themes (17 ext/theme) |
|---|---|---|
| 200 ext | ~49 | ~12 |
| 300 ext | ~74 | ~18 |
| 400 ext | ~98 | ~24 |

**Working design envelope: 10-18 themes, 30-60 formulation pairs, 7-14 dossiers.** Upper bound: 24 themes if material is genuinely heterogeneous. Design tables to handle the upper bound; use compact cells for grids ≥ 100 cells.

#### Per-stage drilldown specs

**`/admin/tonight/transcription`** — existing per-session table, just admin-gated (already correct granularity). Producer view truncated to "Received" only (Change 2 below).

**`/admin/tonight/researcher`**:
- Per-session extraction sub-table: 15 rows × {session_id, count, state}
- Round 1 clustering: 1 call status + input/output counts when done
- Round 2 theming: 1 call status + input/output counts when done
- Themes list: 8-18 rows · click → cluster list → click → extraction list

**`/admin/tonight/provocateur`**:
- **Triage matrix** (10 voices × 10-18 themes = 100-180 cells): single-letter activation `S`/`M`/`–` + stretch flag, hover for reason text
- Triage flags sub-table: per-theme {worth_surfacing, audience_friction, fault_line_present}
- Selection diagnostic block: dropped_themes, forced_fits, stretch_swaps, prior_exclusions (Nights 2/3)
- **Formulation grid** (theme × voice, 30-60 cells): state per cell + click into formulation file

**`/admin/tonight/voice`**:
- **Step 1 grid** (theme × voice, 30-60 cells): state, time-since-start, token counts when done
- **Validation grid** (pair × {anachronism, constitution}, 60-120 cells): PASS/FLAGGED + click-through to flagged JSON
- Step 2 list: 10 voices × {focus_decision, stance, selected_form}
- Continuity list: 10 voices × continuity_night_<N+1>.json status

**`/admin/tonight/editor`**:
- Routing manifest preview (which voices → which dossier)
- Dossier list: 7-14 rows · click → full dossier preview (front + article + theme + headnotes)

**`/admin/tonight/publish`**:
- Per-voice published file count + size
- Night index status
- Cross-night per-voice rollup status
- Lineage graph + traces summary

#### Architecture (so we can iterate)

Each Tier 2 view independent + stateless:
1. Take `night` param (or derive from path)
2. Read `<run_dir>/<stage>/manifest.json` + checkpoint files (no DB, no API, no cache)
3. Render Jinja template

Reuses pattern from existing `runtime/ingest/app.py`. No flow control, no buttons, no streaming. Filesystem-as-state, same surface as orchestrator. Auto-refresh meta-tag handles "live" feel.

**File layout (proposed):**
```
runtime/ingest/
├── app.py                    # add role-split auth + route registration
├── routes/
│   ├── orchestrator.py       # /admin/tonight meta view
│   ├── researcher.py         # /admin/tonight/researcher
│   ├── provocateur.py        # /admin/tonight/provocateur
│   ├── voice.py              # /admin/tonight/voice
│   ├── editor.py             # /admin/tonight/editor
│   └── publish.py            # /admin/tonight/publish
└── templates/
    ├── tonight_meta.html
    ├── researcher_detail.html
    ├── provocateur_grids.html
    ├── voice_grids.html
    ├── editor_dossiers.html
    ├── publish_summary.html
    └── producer_session.html  # stripped per-session for producer role
```

#### Auth split

Add `ADMIN_APP_PASSWORD` to `.env`. `runtime/ingest/app.py`'s Basic Auth dependency identifies role by which credential matched (existing `UPLOAD_APP_PASSWORD` → producer; new `ADMIN_APP_PASSWORD` → admin). Routes check role.

Producer role:
- Can `/upload/<id>` (existing flow)
- Sees `/` index with session list (state column hidden or collapsed to "✓ uploaded" / "— pending")
- Sees `/sessions/<id>` truncated to "Received: `<filename>` at `<timestamp>`" only

Admin role:
- All producer surfaces (full state machine on per-session)
- Plus all `/admin/*` routes

#### What's NOT in scope (deliberate)

- ❌ Buttons for retry/restart/skip/edit
- ❌ Live log streaming (WebSocket / SSE) — meta-refresh is enough
- ❌ Per-stage launch UI — `systemctl start orchestrator@<N>.service` from terminal
- ❌ Validation_failures editing — JSON file inspection via Claude on VM
- ❌ Council_config edit UI — git workflow on athens-2026 repo
- ❌ Dossier preview-and-edit forms — read-only previews only

All control-surface work stays in B8 proper, post-Athens.

#### Phased landing

**Phase A** (MVP, target T-3 May 4, ~6-10 hr):
- Auth role split (producer / admin) + producer per-session truncation
- `/admin/tonight` Tier 1 meta view
- Transcription role-gate (existing view, just admin-only access)

**Phase B** (high-leverage drilldowns, target T-2 May 5, ~13-18 hr):
- Voice Step 1 grid + validation grid (where 60-80% of overnight wall lives)
- Editor dossier list + preview (gated on B1 editor implementation)

**Phase C** (full granularity, T-1 May 6 if budget permits, ~12-17 hr):
- Researcher drill-down (extractions per session, clusters, themes tree)
- Provocateur triage matrix + formulation grid
- Publish per-voice summary

**Phase D** (post-Athens polish): UX iteration based on what operator actually used during Athens nights.

**Total full granularity: ~31-45 hr engineering.** Phase A+B alone (MVP + high-leverage) ≈ 19-28 hr — fits 2-3 days.

#### Trade-flag with B1

C23 Phase A+B competes with B1 editor implementation for engineering time. Two options:

- **C23 first, B1 second:** dashboard ships pre-Athens; editor lands T-1 or T+0 evening; orchestrator skip-if-not-built means dossiers don't exist Night 1 but pipeline runs (Voice → Publish skipping Editor). Microsite renders voice artifacts only Night 1, dossiers from Night 2.
- **B1 first, C23 progressive:** dossiers ship Night 1; dashboard ships only Tier 1 + Voice grid pre-Athens; rest lands during/post-Athens.

Operator decision: lean **C23 first** (operator visibility during overnight wall is high-leverage; missing-dossier-Night-1 is aesthetic regression but not Layer-3 regression; editor is post-Athens-recoverable, dashboard during-Athens isn't).

#### Files implicated

- `runtime/ingest/app.py` — auth role logic + new route registration
- `runtime/ingest/routes/*.py` — new (one per stage drilldown)
- `runtime/ingest/templates/*.html` — new templates + producer-truncated detail
- `runtime/ingest/.env` — `ADMIN_APP_PASSWORD` added
- `runtime/ingest/deploy/README.md` — auth section update (two credentials)
- `_workspace/planning/runtime/HANDOFF_<DATE>.md` — session log

#### Athens fallback

Falls back gracefully — if not landed, operator uses CLI surface (`status.json` + `journalctl` + Prefect dashboard + ssh+claude on VM) per existing infra spec. C23 is operator quality-of-life, not Athens-blocking. Confidence in fallback: high (this surface has been the working assumption since the infra spec landed 2026-05-02).

---

### C24. Vendor-supplied sessions (5 mobile/nightwalk sessions, athens-2026) ✅ LANDED 2026-05-03 PM

Five athens-2026 AI Democracy Marathon mobile sessions are recorded by an external production vendor and delivered as **JSON in our session_package schema**, not as audio. They skip Stage 0 (audio normalization) and Stage 1 (ASR + speaker ID + cleaning) entirely and land at the canonical Stage 1 output boundary `<run_dir>/01_transcription/<sid>/session_package.json`.

**Sessions affected** (3 Day One, 1 Day Two, 1 Day Three; all `ai_assembly: true`, all `audio_source: "vendor"`):

| Night | Time | Title | Speakers |
|---|---|---|---|
| 1 | 10:00 | Birthplace of Democracy Tour | Christoph Quarch |
| 1 | 13:30 | Human Democracy Is Dead | Dave + Helen Edwards |
| 1 | 22:30 | The Dark Side of Democracy: A Nightwalk | Monique van Dusseldorp |
| 2 | 22:30 | Dance and Dissent: A Nightwalk | Brett Perry, John Michael Schert, Monique van Dusseldorp, Vasia Koutsilianou, Mark Aanderud |
| 3 | 16:00 | Make Politics Great Again | Jon Alexander, Claudia Chwalisz, Christos Floros, Lisa Witter, Otti Vogt |

**Architecture decision: filesystem boundary, not pipeline change.** The orchestrator's transcription gate (`overnight_orchestrator.transcription_state`) reads per-session `status.json` with `state="done"` and Researcher reads `session_package.json` via glob. Anything that lands those two files at the right path is indistinguishable downstream — vendor sessions count toward Researcher gate-open with zero orchestrator changes. There is precedent: walking-session reflections also skip Stage 0 (vendor JSON, not audio) per the same file-contract pattern.

**Done:**

`runtime/flows/vendor_intake.py` — validator + lander CLI. Two-tier validation per `docs/AI_Assembly_Transcription_Pipeline.md` §"Step 5 Output":

- **Hard fails** (`vendor.error` + `status.json state=error`, exit 2): bad JSON, missing `metadata`/`transcript`, `metadata.session_id` mismatch with `--session-id`, empty `transcript.turns[]`, any turn missing `speaker`/`role`/`text`, `confidence` value outside `{high, medium, low}` (after lowercase-normalize).
- **Warn-and-accept** (`vendor.warnings` written, `status.json state=done`, exit 0; vendor reality wins on roster drift per operator default): missing `review_queue` → empty stub injected (no warning — clean output is normal); missing `turn_index` → injected via `load_session_package` normalizer; `metadata.roster` differs from `sessions.json` → vendor wins, warning logged; `transcript.speakers_present` mismatched → recomputed; role outside `{moderator, panelist, audience}` → defaulted to `panelist`; whitespace-strip on text (silent).

CLI has two modes:

```bash
# single-file
python -m flows.vendor_intake <vendor_file> --run-dir runs/athens_night_1 --session-id <sid>

# sweep — read sessions.json, find every audio_source=='vendor' for --night,
# look for <session_id>.json files in --inbox, land each one
python -m flows.vendor_intake --night 1 --sweep [--inbox <dir>]
# default inbox: <PROJECT_ROOT>/vendor_inbox/
```

Sweep is idempotent — re-run as files trickle in; missing files are reported but don't fail (exit 0 unless an actual validation error). Misses are normal (vendor hasn't delivered yet).

`reference/sessions.json` (athens-2026 repo) — 5 vendor rows tagged `audio_source: "vendor"`, plus 3 session_format corrections (panel/keynote → walking with `confidence: "manual"`) and 3 capacity drift fixes (38/37/60 → 30 with `capacity_confidence: "manual"`) caught while verifying. `audio_source: "audio"` defaulted on the other 141 rows so the field is universal.

`runtime/scripts/generate_sessions_json.py` — preservation list extended from `ai_assembly` only to also preserve `audio_source` (when ≠ "audio"), `session_format` (when `confidence: "manual"`), and `capacity` (when `capacity_confidence: "manual"`) across regeneration from `program_index.html`. Operator hand-corrections survive re-runs.

**Ingest UI touchpoints:**

- `Session` dataclass: new `audio_source: str = "audio"` field + `is_vendor` property
- Producer `/` index filtered to `audio_source == "audio"` (vendor sessions hidden — not the producer's job)
- Admin `/` index includes vendor (situational awareness)
- Producer GET `/session/{vendor}` → 403 with explanatory message
- POST `/session/{vendor}/upload` → 409 (any role) — orphan audio bytes would never trigger Stage 0
- POST `/session/{vendor}/retry` → 409 — re-validate via `vendor_intake` from tmux
- `/admin/tonight` Pipeline overview Transcription summary label appends `(X audio · Y vendor)` when vendor sessions present
- `/admin/tonight/transcription` drilldown header shows "N vendor-supplied sessions" note; per-row "vendor" pill (`state-pill-vendor` CSS class); per-row file links: `vendor.flag` / `vendor.warnings` / `vendor.error` linked via `/admin/file?path=` instead of `pipeline.log`
- STATIC_VERSION 16 → 17

**Operator workflow on the VM during Athens** (per email-delivery decision 2026-05-03):

```bash
ssh athens-vm
mkdir -p /opt/ai-assembly-athens2026/vendor_inbox  # one-time

# vendor emails files; operator saves with <session_id>.json names + scp's:
scp ~/Downloads/*.json athens-vm:/opt/ai-assembly-athens2026/vendor_inbox/

# in tmux on VM:
cd /opt/ai-assembly-athens2026/runtime
venv/bin/python -m flows.vendor_intake --night 1 --sweep
# → "expected: 3 · landed: 3 · missing: 0"
```

Re-run sweep as many times as needed across the night as files trickle in. No new credentials, no new HTTP routes, no Google Drive setup — operator-in-loop is acceptable for 5 files across 3 nights.

**Tests:** 24 in `runtime/tests/test_vendor_intake.py` (3 happy path, 7 hard-fail, 6 warn-and-accept, 2 re-run idempotence, 6 sweep) + 6 vendor-aware route tests in `runtime/ingest/tests/test_app.py`. 152/152 runtime tests passing against athens-2026 PROJECT_ROOT.

**Live verification 2026-05-03 PM** (demo PROJECT_ROOT at `/tmp/vendor_demo_*`): single-file landed Birthplace tour cleanly; sweep night=1 with 3 inbox files landed all 3; sweep night=2 with empty inbox reported 1 missing without crashing. `/admin/tonight.json` showed `{"audio": 0, "vendor": 1}` in `by_source`; transcription drilldown rendered vendor pill on each row.

**Commits** (across two repos, all on `main`):

- `code/` `edb877a` — runtime(scripts): preserve audio_source + manual session_format/capacity overrides in generator
- `code/` `9756677` — runtime(ingest+flows): vendor-supplied sessions land at the 01_transcription boundary
- `code/` `51234cf` — runtime(flows): vendor_intake sweep mode
- `athens-2026/` `f652949` — reference/sessions.json: tag 5 vendor-supplied sessions + format/capacity fixes

**Open:** none directly. Operator pre-Athens TODO: `mkdir /opt/ai-assembly-athens2026/vendor_inbox` on the VM at provisioning time (will fold into B10).

---

### C25. Researcher Node 1 extraction is sequential — should parallelise 🟢 SHIPPED 2026-05-04 (commit `0e1b14e`)

**Shipped 2026-05-04** in commit `0e1b14e`. ThreadPoolExecutor with `RESEARCHER_NODE1_BATCH=4` cap (env-overridable) replaces the sequential `for pkg_path in packages` loop. Athens wall savings: ~25-30 min/night (15 sessions sequential ~30-45 min → parallel ~8-12 min). 209/209 tests pass.

Filed history below preserved.

---

### ~~C25 (original)~~. Researcher Node 1 extraction is sequential — should parallelise 🟡 (filed 2026-05-03 dryrun, ~$25 in flight)

**Surfaced during dev MSC dryrun (2026-05-03 PM):** `researcher_flow.py:762-768` runs Node 1 (per-session extraction) in a sequential `for` loop — one Anthropic call per session, blocking. The Voice Pipeline parallelises across (voice, theme) pairs via `ThreadPoolExecutor`; Researcher does not. Looks like an oversight, not a deliberate design — extraction calls are independent and `validate_and_concat` operates on the full list at the end (order-agnostic).

**Athens scale impact:**
- 15 sessions × ~2-3 min/extraction (Opus 4.7 with thinking) = **30-45 min** sequential on Node 1
- Parallelised (concurrency cap ~4-5) ≈ **6-9 min**
- Per-night savings: ~25-35 min wall

**Fix size:** ~20-30 min — wrap the extraction loop in `ThreadPoolExecutor(max_workers=4)` with `as_completed`, write each result atomically as it lands (write_json_atomic already idempotent). Mirror the pattern in voice/step1.py.

**Trade-off:** more concurrent Anthropic load (4× per Researcher run); Anthropic Tier 4 limits comfortably accommodate.

**Status:** filed; not blocking dryrun; should land before Athens to halve overnight wall.

---

### C26. Ingest layer + transcription firing should be split (orchestrator drives both stages) 🟢 SHIPPED 2026-05-04 PM (with dashboard adaptation per operator request)

**Shipped 2026-05-04 PM** — operator-driven split ships per spec, plus the dashboard adaptation operator asked for in same turn.

**Architecture change:**
- New per-session state `STATE_NORMALIZED` between `normalizing` and `transcribing` (filesystem source of truth in `01_transcription/<sid>/status.json`)
- `pipeline.run_normalize_and_transcribe` (FastAPI BackgroundTask) renamed to `pipeline.run_normalize` — does ffmpeg only, then sets state=`normalized` and STOPS. Legacy alias preserved so `app.py` still calls the same name.
- New `pipeline.fire_transcription(session_dir, session_json_path)` is the orchestrator-facing spawn entrypoint — guards against missing audio.m4a, surfaces spawn errors as state=error.
- `overnight_orchestrator.py::fire_pending_transcriptions(run_dir, session_ids, max_concurrent)` scans the per-session status.jsons, counts in-flight transcriptions, fires `fire_transcription` for `normalized` sessions up to the cap. Concurrency: `ORCHESTRATOR_TRANSCRIPTION_CONCURRENCY=4` default (env-overridable).
- New Stage 0 in `poll_once` runs the dispatcher before the existing transcription_state check; idle returns now report `dispatch` and `awaiting dispatch` count.

**`transcription_state` extended** with new `normalized_sessions` and `transcribing_sessions` lists so callers can see exactly which sessions are awaiting dispatch vs. in flight.

**Dashboard adaptation (per operator turn-request):**
- `_transcription_summary` adds `normalized` to its counts dict
- New top-level state `awaiting_dispatch` when ALL pending sessions are `normalized` (no normalizing/received/transcribing in flight) — surfaces orchestrator bottleneck distinctly from ffmpeg or AssemblyAI bottlenecks
- Per-session label gains "N awaiting dispatch" when normalized > 0
- `_STATE_DISPLAY` adds `"normalized": "normalized · awaiting orchestrator"` for per-row state pill on transcription drilldown
- Sort order on `/admin/tonight/transcription` slots `normalized` between `transcribing` and `received` (active dispatch ahead of waiting-on-ffmpeg)

**Tests:** 17 new across two test files (12 in `test_orchestrator_dispatch.py`: state buckets + dispatch logic + concurrency cap + inflight count + substate handling + received-state-not-dispatched + spawn-error + missing-status; 5 in `test_dashboard_normalized.py`: counts surface normalized / awaiting_dispatch state / label / mixed-state / done unaffected). Plus updated `test_app.py::test_upload_then_transcribe_end_to_end` to reflect that upload now stops at `normalized` and the test then explicitly calls `fire_transcription` to drive the second half. Full runtime + ingest suite: 296/296 pass (was 279).

**Operator UX impact:**
- Producer upload still gets fast confirmation (state=normalized; ffmpeg done in seconds)
- Orchestrator picks up within ≤60s (default poll interval)
- Dashboard shows the new state distinctly so operator can tell at a glance whether the bottleneck is upload-side, dispatcher-side, or transcription-side
- Concurrency-bounded firing prevents AssemblyAI rate-limit surprises at 25-session Athens scale
- CLI use of `transcription_flow.py` (dryruns) no longer touches status.json plumbing — fully decoupled

**Smoke test:** orchestrator one-shot poll against fresh project_root returns clean `idle` status with no errors; imports + state machine work.

Filed history below preserved.

---

### ~~C26 (pre-shipped, post-promotion)~~. Ingest layer + transcription firing should be split (orchestrator drives both stages) 🟡 PROMOTED TO PRE-ATHENS 2026-05-04 (was: post-Athens architecture suggestion)

**Promotion rationale (2026-05-04):** Operator's dryrun pattern — running transcription_flow.py via CLI, hand-patching status.json so the dashboard reflects state — is exactly the friction this item resolves. During Athens itself, the operator will be observing via dashboard while transcription runs; having the orchestrator drive transcription (instead of fire-and-forget from ingest) gives:
- Concurrency control on AssemblyAI calls (stagger 25 sessions across the night without overrunning rate limits)
- Centralised retry / error recovery visible in dashboard
- Dashboard mirrors orchestrator's view directly (no status.json blind spots)
- Operator can re-fire failed transcriptions from dashboard without re-uploading

Pre-Athens-eligible if budget allows; estimated ~3-5 hr engineering. If budget tight, defer to post-Athens.

**Original filing 2026-05-03 below preserved.**

---

### ~~C26 (original, pre-promotion)~~. Ingest layer + transcription firing should be split (orchestrator drives both stages) 🟡 (filed 2026-05-03 dryrun, architecture suggestion)

**Surfaced during dev MSC dryrun (2026-05-03 PM):** Operator observed that the runtime currently has **two distinct trigger paths** for transcription firing:
- **Ingest layer** (FastAPI app `runtime/ingest/app.py`): producer uploads audio → ingest writes `status.json` (state=received → normalizing → transcribing) + spawns `transcription_flow.py` as detached subprocess.
- **Orchestrator** (`runtime/scripts/overnight_orchestrator.py`): polls per-session `status.json` for state=done; only fires Stages 2-5 (researcher → provocateur → voice → editor → publish). Does NOT fire transcription.

This split means transcription is fire-and-forget from upload (no rate-limiting, no centralised retry, no orchestrator visibility into when transcription started or how many are concurrent). The dashboard reads status.json which is ingest-written; if transcription is run via CLI (bypassing ingest) the dashboard goes blind.

**Cleaner architecture suggestion (operator):**
- Producer upload only marks `state=received` + writes session_package.json input shell
- Orchestrator scans for `received` sessions and fires `transcription_flow.py` in its own concurrency-bounded queue
- Orchestrator writes status.json updates as it spawns/monitors transcription jobs
- Dashboard reads same status.json — same surface, single writer

**Benefits:**
- Single state machine (orchestrator) drives all 6 stages
- Concurrency control on transcription (rate-limit AssemblyAI calls)
- Centralised retry / error recovery
- Dashboard mirrors the orchestrator's view directly
- CLI use of `transcription_flow.py` (e.g. dryruns) doesn't need separate status.json plumbing

**Trade-off:** decouples upload UX from transcription timing — producer no longer sees "your audio is being transcribed" immediately, only "your audio was received". May be desirable (less latency in upload UI) or undesirable (producer wants real-time progress feedback).

**Status:** filed; not Athens-blocking; touches both `ingest/app.py` and `overnight_orchestrator.py`. Estimated ~3-5 hr engineering. Defer until post-Athens unless dryrun reveals concurrency pain.

---

### C36. Voice pipeline streaming — per-voice Step 2 starts when that voice's Step 1 done 🟡 (filed 2026-05-04 PM)

**Surfaced 2026-05-04 PM during v2 dryrun re-run:** operator asked "now that ada is done with private thinking — will she start step 2?" Answer: no. Voice pipeline currently has a sync barrier between Step 1 and Step 2 — Step 2 fires for ALL voices in parallel only after EVERY voice's Step 1 completes.

**Current architecture** (`voice_flow.run_voice()`):
1. Step 1: parallel batches across (voice, theme) pairs (`VOICE_STEP1_BATCH=4`)
2. Sync barrier — wait for all Step 1 done
3. Step 2: parallel across all voices (`VOICE_STEP2_BATCH=4`)
4. Sync barrier
5. Step 2 validation → operator gate

**Streaming alternative:** as soon as voice X's Step 1 outputs (all of X's themes) complete, fire X's Step 2 immediately. Doesn't wait for other voices. Step 2 + validation pipelines per voice; orchestrator gate still halts on any flag.

**Why it matters:** at Athens scale (10 voices × 3-5 themes = 30-50 pairs), Step 1 is the wall-time floor (60-160s per pair, batches of 4 → ~7-12 batches × ~2-3 min ≈ 14-36 min). Step 2 can't start until the slowest pair in the LAST batch completes. Streaming would let fast voices' Step 2 begin while slow voices' Step 1 still finishes — savings depend on how skewed batch completion times are. Estimated 5-15 min wall savings per night at Athens scale; less at dryrun scale.

**Cost:** zero (same number of LLM calls); just earlier scheduling.

**Risk:** more concurrent Anthropic load (Step 1 + Step 2 calls in flight simultaneously). Tier 4 limits comfortably accommodate; cache write/read concurrency may interfere on first batch.

**Effort:** ~2-3 hr — refactor voice_flow's barrier-based loop to per-voice futures (`voice_pipeline_for_voice(slug)` runs Step 1 batches → Step 2 → sub-Step 2 validation as one chain; outer ThreadPool fires N voices concurrently).

**Status:** filed; not Athens-blocking (current architecture works correctly, just sequential by batch). Defer until post-Athens unless ~10-min wall savings matter.

---

### C38. Bob Marley × theme_001 Step 1 silent drop in v2 dryrun 🟢 SHIPPED 2026-05-04 PM (root cause found + manifest tracking added)

**Shipped 2026-05-04 PM.** Root cause found in `_run_step1_batch` (and Step 2 / Step 3 / Continuity dispatchers): all four used a `try: results[k] = fut.result(); except Exception as e: logger.error(...)` pattern that caught exceptions into log-only output. The failed pair never propagated to the manifest — which is why `step1_pairs_succeeded: 25` showed against `step1_pairs_attempted: 26` with NO indication of WHICH pair failed or WHY. The original Marley × theme_001 root cause is unrecoverable (logs gone), but the silent-drop bug class is now closed across four stages.

**Fix:**
- New `_capture_failure(stage, key, exc)` helper in `voice_flow.py` builds a structured failure record (stage, voice_slug, theme_id, error_type, error_message capped at 500 chars, traceback_excerpt — last 6 traceback lines).
- `_run_step1_batch` now returns `(results, failures)`. Caller threads `failures` into the manifest as `step1_failures: [...]`.
- Step 2 + Step 3 + Continuity dispatchers in `run_voice` mirror the pattern with `step2_failures` / `step3_failures` / `continuity_failures` lists threaded into the manifest.
- Manifest gains: `counts.step1_pairs_failed`, `counts.step2_voices_failed`, `counts.step3_voices_failed`, `counts.continuity_voices_failed` quick-glance counters + the per-stage detail arrays.
- Final-summary log line surfaces failures explicitly when any are present: `FAILURES: step1=N step2=N step3=N continuity=N — see manifest.step{1,2,3}_failures + continuity_failures`.

**Tests:** 6 new in `test_capture_failure.py` (Step 1 tuple key, Step 2/3/Continuity slug key, traceback excerpt presence, message truncation, extra-dict merge). All pass; 331 of full runtime suite green (1 pre-existing unrelated test deselected).

**Filed history below preserved.**

---

### ~~C38 (original)~~. Bob Marley × theme_001 Step 1 silent drop in v2 dryrun 🟡 (filed 2026-05-04 PM)

**Surfaced 2026-05-04 PM during v2 dryrun:** Step 1 produced 25/26 detailed_response files. The missing pair was `bob_marley × theme_001`. Provocateur briefing exists for that pair; voice manifest reports `step1_failures: 0` (the failure handler didn't catch it).

**Symptoms:**
- `briefings/bob_marley.json` includes `theme_001` in its formulations
- `step1_detailed_responses/bob_marley__theme_001.json` is absent on disk
- `manifest.json::step1_failures = []` (no error logged)
- All other 25 expected pairs landed cleanly

**Hypotheses to investigate:**
1. Race condition / dropped pair in the parallel ThreadPoolExecutor batch logic
2. Silent exception in `run_step1_for_pair` that was swallowed before reaching the failure-handler hook (e.g. inside the streaming call's retry path)
3. Anthropic call returned an empty response or timed out without raising
4. Something specific to the Marley card's content triggered a non-error skip path

**Investigation steps (~30-60 min):**
1. Re-run JUST the missing pair via voice_flow CLI in single-pair mode + capture full subprocess logs
2. Inspect voice_flow's exception handling around `run_step1_for_pair` to see if any path silently no-ops
3. Check if Marley's card content has anything that would cause the model to refuse to engage (e.g. theme content explicitly violating Marley's hard_limits)

**Risk:** silent drops at Athens scale = missing artifact at publish time, no operator alert. Worth fixing before Athens even if root-cause is rare.

**Status:** filed; pre-Athens-eligible — silent drops are exactly the bug class that bites worse at production scale.

---

### C38. Voice Pipeline Step 2 doesn't enforce card's `length_and_format_constraints` cap 🟡 (filed 2026-05-04 PM, surfaced from voices thread)

**Surfaced 2026-05-04 PM during v2 dryrun length-audit (voices/OPEN_ITEMS.md §27 below).**

**Findings from `dev_msc_dryrun_v2_20260504/published_artifacts/voices/*.json` `artifact_summaries.[night].word_count`:**

| Voice | Card spec | Dryrun word_count | Over-cap |
|---|---|---|---|
| Cleopatra | 300–500 | 421 | ✓ |
| Whanganui River | 350–550 | 493 | ✓ |
| Ada Lovelace | 350–550 | 537 | +37 |
| Scheherazade | 350–550 | 560 | +60 |
| Plato | 350–550 | 575 | +75 |
| Ibn Battuta | 350–550 | 598 | +98 |
| Octopus | structured + ~100–200 prose | 643 (prose) | +143 (prose side) |
| Bob Marley | **350–500 explicit** (v2-anchored) | **739** | **+239** |
| Hannah Arendt | 600–900 | 828 | +328 |
| Dostoevsky | 350–550 | **980** | **+480** (~double the cap) |

**8 of 10 voices over-ran the card-spec.** Only Cleopatra + Whanganui honored it. The conference's effective audience-attention cap is 500w (per operator 2026-05-04 PM); only 2 voices stayed within that.

**Why this is a runtime issue, not voices issue:**

The persona-pipeline side is fine:
- Pass 4b prompt explicitly framed audience constraint three times: "the artifact ~750 people will encounter at breakfast" / "short, compelling morning read" / "Readable over coffee" (`personas/flows/shared/prompts/persona_pass_4b_artifact.md` lines 14-16, 119, 170)
- Cards correctly captured the spec — most say 350–550w with corpus-anchored justifications
- Marley v2 was specifically anchored at 350–500w with explicit justification

The runtime side does not enforce it:
- Voice Pipeline Step 2 takes the persona card as system prompt + Provocateur question as user message
- The card's `length_and_format_constraints` field appears in the system prompt as descriptive text ("Write 350 to 550 words...")
- But there's no `max_tokens` parameter derived from the card's length spec, no post-generation truncation, no iterative-retry-on-overflow
- The model interprets the length instruction as a request, not a hard cap, and writes to its own internal "right length" sense — which trends to historical practice (Dostoevsky's actual Diary entries ran 600-1500w; Arendt's actual essays 1500-4000w; the model defaults near these regardless of card-spec)

**Three implementation paths:**

**(a) `max_tokens` parameter derived from card** (~30 min, cheapest)
- Parse card's `length_and_format_constraints` for word range; derive `max_tokens ≈ words × 1.5` (rough English token-to-word ratio)
- Pass to `messages.create()` for Step 2
- **Tradeoff:** truncates mid-sentence at the boundary; not graceful

**(b) Post-generation word-count + truncate-to-last-complete-sentence** (~1-2 hr)
- Generate at default max_tokens; count words; if over cap, truncate at the last complete-sentence boundary under cap
- **Tradeoff:** wastes tokens already paid for; truncation may cut load-bearing content

**(c) Iterative retry with explicit cap-instruction + previous draft** (~2-3 hr; doubles cost)
- Generate; if over cap, re-prompt with "previous draft was X words; rewrite to be under 500 words preserving the load-bearing structure" + the draft
- **Tradeoff:** most respectful of voice quality; doubles API cost on overflows

**Recommendation:** **(a) for Athens**, with `max_tokens` derived per-voice from card's upper-bound × 1.5. Add **(c) post-Athens** as quality-preservation refinement.

**Per-voice max_tokens (if (a) is taken):**

| Voice | Cap (words) | max_tokens (×1.5) |
|---|---|---|
| Cleopatra | 500 | 750 |
| Plato / Battuta / Lovelace / Scheherazade / Whanganui | 500 | 750 |
| Marley | 500 | 750 |
| Octopus | structured (JSON + ~200w prose) | ~600 prose-side; JSON unconstrained |
| Arendt | 500 (was 600-900 — see voices/OPEN_ITEMS.md §27) | 750 |
| Dostoevsky | 500 | 750 |

(All converge on ~750 max_tokens since the conference cap is uniform 500w.)

**Cross-references:**
- voices/OPEN_ITEMS.md §27 (length-anchoring discussion + dryrun audit findings + per-voice corpus-anchored length rationales — this is its voices-side counterpart)
- Pass 4b prompt at `personas/flows/shared/prompts/persona_pass_4b_artifact.md` (audience-cap framing already correct, no changes needed)

**Status:** filed; **pre-Athens-eligible** — without this, the Substack edition will publish artifacts that nominally honor "morning read" framing but actually require 5-10 minutes per voice to read, blowing the 30-60 min total morning attention budget the editor flow is calibrated for.

**Side-note:** the operator earlier flagged that 400w should be the cap for the editor's theme article body (vs 500w for the artifacts). If C38 (a) lands, the same `max_tokens` discipline should apply to the editor's article generation in `runtime/flows/editor/dossier_generation.py` — derive 400w-cap × 1.5 = 600 max_tokens for article body. Editor headnotes (30-80w) and theme summaries (100-200w) would similarly cap.

---

### C37. Provocateur output JSONs don't persist per-call tokens 🟢 SHIPPED 2026-05-04 PM

**Shipped 2026-05-04 PM.** `_stream_and_parse` in `provocateur_flow.py` now merges the `usage` block into the parsed result dict before returning. All three call sites (`triage_voice`, `triage_flags`, `formulate_for_member`) inherit the new fields, and the two that persist via `write_json_atomic` (`triage_voices/<slug>.json` + `formulations/<theme>__<voice>.json`) now carry `model` + `input_tokens` + `output_tokens` + `cache_creation_input_tokens` + `cache_read_input_tokens` + `wall_clock_s`. Defensive `isinstance(result, dict)` guard. Trivial change, no behavior impact. Closes the cost-monitoring gap for ~37 Provocateur calls/night.

**Filed history below preserved.**

---

### ~~C37 (original)~~. Provocateur output JSONs don't persist per-call tokens 🟡 (filed 2026-05-04 PM)

**Surfaced 2026-05-04 PM during v2 dryrun cost calculation:** `triage_voices/<slug>.json` and `formulations/<theme>__<voice>.json` files only persist content (ranked_themes, formulation prose, selected_quotes, etc.) — NOT per-call `input_tokens` / `output_tokens` / `cache_creation_input_tokens` / `cache_read_input_tokens` / `model` / `wall_clock_s`.

Voice Step 1/2/3 + Editor + Continuity all DO persist these fields on their output JSONs. Provocateur is the gap.

**Why it matters:** post-run cost calcs (per-stage token totals, cache-hit-rate analysis, per-call wall-clock distribution) can't roll up Provocateur. Roughly 37 calls per Athens night currently invisible to cost monitoring.

**Fix (~10 min):** in `provocateur_flow.py::_stream_and_parse`, merge the `usage` block into the `result` dict before returning. Both `triage_voice` and `formulate_for_member` callers persist that result via `write_json_atomic`. Add fields:
```python
result["model"] = CLAUDE_MODEL
result["input_tokens"] = usage.input_tokens
result["output_tokens"] = usage.output_tokens
result["cache_creation_input_tokens"] = getattr(usage, "cache_creation_input_tokens", 0) or 0
result["cache_read_input_tokens"] = getattr(usage, "cache_read_input_tokens", 0) or 0
result["wall_clock_s"] = wall
```

**Status:** filed; pre-Athens-eligible (small but enables exact cost monitoring during the 3-night run). Trivial change, no behavior impact.

---

### C49. Many-speaker speaker_id structured-output JSON-decode → manual passthrough 🟡 (filed 2026-05-29 from Athens Nights 1–3 transcription; recurred all three nights)

**Background.** `transcription_flow.py::identify_speakers` (Sonnet 4.6 structured output, the 5-pass Speaker ID) reliably produces malformed JSON when a session has a large speaker roster — the verdict payload grows past the point where the model keeps the JSON well-formed, and the whole `out_02_speaker_id.json` fails to decode, halting the stage.

**Recurrence (this is the recurring half of the Athens production-friction story — distinct from C43, which is the same failure class at the *validator* stage):**
- Night 1 ×2: both Act One sessions (47-speaker output; Sonnet AND Opus both failed).
- Night 2 ×1: The Reality Tunnels primary.
- Night 3 ×2: The Long Game + Act Five (Beastopia) primary.

**Operator workaround (the "manual passthrough" path, now battle-tested).** Hand-write `out_02_speaker_id.json` with every turn mapped to `Unidentified Speaker N` (preserving the `out_01` diarization turn boundaries), then re-fire `transcription_flow.py` for that session — it sees `out_01` + `out_02` present and runs **cleaning only**, skipping ASR + speaker_id. The speaker-ID fallback chain already treats `Unidentified Speaker N` as first-class downstream (Researcher reads it fine), so the night doesn't fail; named-speaker attribution is simply absent for that one session.

**Real fix candidates for v4.1** (mirror C43's options — same root cause):
- (a) JSON-repair / tolerant parse before failing (repair library; or stream-parse the per-turn array so one bad turn doesn't sink the whole map).
- (b) Chunk the speaker_id call for large rosters (N turns per call, merge maps) so no single structured-output response is large enough to corrupt.
- (c) Auto-passthrough fallback: on decode failure, write the all-`Unidentified` map automatically + flag the session for operator review, instead of halting.

**Status:** filed for v4.1. Manual passthrough is reliable but operator-toil-heavy on big-roster nights. (c) is the highest-leverage fix — it turns a pipeline halt into a graceful degrade. Cross-references C43 (same JSON-decode failure class, validator stage).

---

### C50. `nights/<night>/_index.json` clobbered by single-voice publish invocations 🟡 (filed 2026-05-29 from Athens Night 3 publish)

**Background.** `flows/voice/publish.py::publish_voice_artifacts_for_night` rebuilds the per-night `_index.json` from ONLY the voices in that invocation. The per-voice `<slug>.json` files persist across calls, but the index is overwritten each time — so a sequence of single-voice publishes (per-voice reruns) leaves the index reflecting only the LAST voice.

**Observed (Athens Night 3).** The closing-edition voice stage was published voice-by-voice as late reruns landed (cleopatra → plato → scheherazade → whanganui). Result: `nights/night_3/` had only 4 per-voice page files — the other 6 (ada_lovelace, bob_marley, fyodor_dostoevsky, hannah_arendt, ibn_battuta, octopus) were never published at all, because no full-batch publish ever ran — and `_index.json` showed `voice_count: 1` (whanganui only). The dossiers link to `/night-3/<voice>` for all 10 routed voices, so 6 microsite links dangled until a full republish on 2026-05-29 (`publish_voice_artifacts_for_night(run_dir, night=3)` with `voice_slugs=None`) restored all 10 pages + a correct 10-voice index. Night 2's index has the same single-voice tail (`voice_count: 1`) but all 10 page files are present, so it's cosmetic there.

**Fix options:**
- (a) Make the index additive: read the existing `_index.json` and merge the just-published voices rather than overwriting.
- (b) Always rebuild the index from the on-disk `nights/night_N/<slug>.json` set (source of truth = the directory, not the invocation arg).

**Status:** filed for v4.1. (b) is the more robust default (index always reflects what's actually on disk). Same idempotency-model bug class as C46 (editor `--single-dossier` index clobber) — consider fixing both under one pass. **Operational note:** until fixed, after any per-voice rerun, finish with a full `voice_slugs=None` publish so the index + page set are complete.

---

### C51. Per-theme published artifacts (`published_artifacts/themes/night_N/`) never generated for any night 🟡 (filed 2026-05-29 from Athens publish audit)

**Background.** `flows/voice/publish.py` writes per-voice pages whose `themes_addressed` reference themes by `theme_id`, with full theme metadata expected at `published_artifacts/themes/night_<N>/<theme_id>.json` (produced by the separate `publish_flow.py`, which reads across Researcher + Provocateur + Voice). That theme-publish stage was **never run in production** — no `themes/` directory exists for Night 1, 2, or 3.

**Impact.** Dossiers inline their own theme metadata (`theme_title_for_dossier` + `theme_abstract_for_dossier`), so the dossier view is unaffected. But per-voice pages carry only `theme_id` references with no join target — any microsite surface resolving a voice page's `themes_addressed` to a theme record has nothing to read. Night 1 shipped this way too, so it's a standing condition across all three nights, not a Night-2/3 regression.

**Fix:** run `publish_flow.py` per night to populate `themes/night_N/`, OR — if the microsite never resolves per-voice theme_ids and the dossier-inlined metadata suffices — formally drop the per-theme-file contract and stop referencing `themes/night_N/` in `voice/publish.py`'s docstring. Decide which before the next production run.

**Status:** filed for v4.1. Needs a product decision (are per-theme files a live deliverable?) before code action. Not blocking — no shipped surface currently 404s on it (dossiers self-contain theme metadata).

---

### C48. Voice-pipeline deployment-context implementation — shelved on branch, disposition is runtime-thread's call 🟡 (surfaced 2026-05-08 by voices-thread pre-merge consolidation)

**What this is.** `feature/voice-deployment-context` commit `6a8e825` ("runtime(voice/card_assembly): inject deployment context (room/panel/readers) into voice system prefix") — 139 LOC in `runtime/flows/voice/card_assembly.py` + 285-line `runtime/tests/test_deployment_context.py` (15 tests) — injects THE GATHERING / THE PANEL / YOUR FELLOW VOICES / YOUR READERS blocks into the voice Step 1/2 system prefix. **NOT on main.**

**Why it's shelved (full trace).** The original commit message ends "Awaiting dryrun comparison before merge." The comparison fired (`projects/current-tests/dev_msc_dryrun_v2_20260504/runs/athens_night_1/04_voice/COMPARISON_2026_05_05.md`, 1024 lines): 6/10 voices shifted theme focus, +348w net, voices "engaged more concretely" — but the conclusion (filed in the original C39, now `C41`) was "**richness lever sits at the briefing layer, not the deployment-context layer**." The runtime thread then took a DIFFERENT path: Provocateur deployment-context (`419fcac`) + Editor `deployment_context` override (`ea7f4a8`/`0957ac4`) shipped to main, addressing the GATHERING/SPEAKERS context at the Provocateur + Editor stages instead of the voice stage. The voice-pipeline implementation was never merged or cherry-picked.

**Current state.** `feature/voice-deployment-context` kept alive (operator decision 2026-05-08, option a — zero cost, preserves the implementation). Branch holds the only copy of `6a8e825` + its tests. main does NOT have voice-stage deployment-context injection.

**Disposition deferred to runtime/production thread** (it owns these branches + this code). Options when revisited post-Athens: (a) merge `6a8e825` to add voice-stage deployment-context ON TOP OF the Provocateur/Editor placements (they're additive, not alternatives — dryrun showed it helps); (b) formally retire as superseded; (c) leave branch dormant. The voices-thread merely surfaced this during branch consolidation; **not the voices-thread's call to merge or delete.**

**Cross-references:** `C41` (the briefing-layer richness conclusion that redirected effort); CLAUDE.md branch-state history; original `6a8e825` commit message (full implementation spec).

---

### C47. Editorial discipline rules → permanent prompt patches 🟡 (filed 2026-05-08 from Athens Night 1 production)

**Background.** Athens Night 1 production used three editorial-discipline rules added to the per-run `_dossier_deployment_context.md` (gitignored under `runs/`): (a) Provotypist anonymization (Peschel name not in publishable surface); (b) voices interleave inside argumentative paragraphs (not section-headed sequenced exhibits); (c) sacred-grammar discipline for Marley + Whanganui (Rastafari + te-reo terms appear only inside attributed quotation, not in editor narrative voice).

All three were demonstrated to work end-to-end on Night 1 (commits `bfa1f8a` + `87abdf2` on athens-2026 main). The question for v4.1 is which should become permanent prompt rules and which should remain per-run deployment_context.

**Candidates for permanent inclusion in `runtime/flows/shared/prompts/editor_dossier.md`:**

1. **Voices-interleave rule** — fully general (applies to any multi-voice dossier; not tied to Athens or to specific voices). Should become permanent. Reduces dependence on per-run deployment_context for routine editorial discipline.

2. **Sacred-grammar discipline** — voice-specific (Marley + Whanganui carry it; future voices with similar load-bearing-traditions may too). Two architecture options:
   - (a) Permanent prompt with hardcoded voice-specific clauses (Marley + Whanganui named explicitly).
   - (b) Voice-card-driven: voices declare `sacred_grammar: true` (or richer schema with the protected lexicon) on their persona card; editor prompt reads each voice's declaration and applies discipline conditionally.
   - (b) is more durable for v4.1 architecture but requires schema change. (a) is faster to ship.

**Candidates that should stay per-run deployment_context:**

3. **Provotypist anonymization** — operator-side, per-event editorial choice. Different productions may want operator surfacing or anonymization; should remain a per-deployment knob, not a permanent rule. Already documented in CLAUDE.md as the deployment_context override mechanism.

**Status:** filed for v4.1 architectural cleanup post-Athens. Sub-item 1 (voices-interleave) is shovel-ready. Sub-item 2 needs architecture decision (a) vs (b).

---

### C46. `--single-dossier` rebuilds night index with only the processed dossier 🟡 (filed 2026-05-08 from Athens Night 1 v2.1 fires)

**Background.** Running `editor_flow.py --single-dossier theme_X` regenerates only the targeted dossier but Stage 3 (`finalize_edition`) rewrites `published_artifacts/dossiers/night_<N>/_index.json` to reflect ONLY the dossier processed in that run, dropping the entries for unmodified dossiers from the index. Required manual `build_night_index()` call after the v2.1 single-dossier fires for theme_004 + theme_010 to restore the full 5-dossier index for Night 1.

**Fix options:**

- (a) `--single-dossier` mode preserves the existing index entries for unmodified dossiers (read existing `_index.json` and merge in the new entry).
- (b) Require a full re-fire to rebuild index correctly; document `--single-dossier` as in-place dossier replacement only (caller responsible for index management).

**Status:** filed for v4.1. (a) is the cleaner UX; (b) is the simpler implementation. Currently mitigated by manual `build_night_index()` invocation.

---

### C45. Editor doesn't cache dossiers — full re-fires regenerate all dossiers 🟡 (filed 2026-05-08 from Athens Night 1 fires)

**Background.** `editor_flow.py` regenerates every dossier on every fire — there's no `out_path.exists() → return cached` short-circuit at the per-dossier level (which `voice/step1_private_reasoning.py:run_step1_for_pair` does have, line 168). On Athens Night 1 a full editor re-fire to rebuild the index after a single-dossier fire produced 5 fresh Opus calls for all 5 dossiers (~$5-7 + ~3-4 min wall time) when only the index needed rebuilding.

**Fix:** add file-existence cache to `run_dossier_for_theme` in `flows/editor/dossier_generation.py` matching the voice-step1 pattern. With `--no-cache` flag to force regeneration.

**Status:** filed for v4.1. Cross-references C46 (single-dossier index issue) — both touch editor_flow's idempotency model.

---

### C44. Researcher per-session extraction caching 🟡 (filed 2026-05-08 from Athens Night 1 fires)

**Background.** Researcher's `extract_session` task lacks `cache_key_fn=task_input_hash` — re-fires of the Researcher pipeline re-extract every session. Athens Night 1 saw 215 → 205 extraction drift between v2 and v3 fires (LLM non-determinism on identical input). For determinism + cost discipline, extractions should cache like `transcribe_assemblyai` does.

**Status:** filed for v4.1. Trivial Prefect-decorator change (~5 min); no semantic risk.

---

### C43. Validator JSON parse-failure pattern 🟡 (filed 2026-05-08 from Athens Night 1 Voice validation)

**Background.** Sonnet 4.6's structured-output for `safeguards` and `voice_fidelity` pillars produced malformed JSON on Hannah's complex artifact (line 27 column 143; long verdict-evidence with unescaped quotes/commas). Reproducible across both the test fire (12:00) and full fire (12:25). Mitigated 2026-05-08 by:

- Defensive WARN fallback in validator on parse failure (operator-Released the artifact via dashboard since the underlying artifact was clean).
- Dashboard `_error` field rendering on the Step 2 validation page (commit `30f2413` 2026-05-08) so operator sees the parse error instead of an empty "— none" verdict.

**Real fix candidates for v4.1:**

- (a) Try Opus 4.7 for validator (model override env var). Higher reliability on structured output, but ~5x cost.
- (b) JSON-repair logic in the parser (try `json5` or a tolerant repair library before defaulting to WARN).
- (c) Tighten validator prompt to discourage long verdict-evidence strings (limit to N words; require list-of-bullets format that's less escaping-prone).

**Status:** filed for v4.1. Workaround in production; real fix non-blocking.

**Recurrence (Athens Nights 2–3, logged 2026-05-29).** Validator structured-output parse failures repeated: Night 2 Bob Marley (`safeguards` + `voice_fidelity` pillars) and Night 3 Whanganui River (`voice_fidelity`). In each case the defensive WARN-fallback (commit `30f2413`) held — the operator saw the `_error` field on the dashboard render and released the underlying-clean artifact. Confirms the parse failure is not a one-off Hannah-artifact quirk; the v4.1 real fix (a/b/c above) is worth doing. **NB — naming disambiguation:** the *transcription-stage* speaker_id JSON-decode failures from Athens Nights 1–3 (the "manual passthrough" cases) are the SAME failure class at a DIFFERENT stage; earlier session notes loosely called them "C43" but they are filed separately as **C49**. C43 = validator stage; C49 = speaker_id stage.

---

### C42. Safeguards validator alignment with `voice_temporal_stance.default` 🟡 (filed 2026-05-08 from Athens Night 1 Voice validation)

**Background.** The architectural fix in athens-2026 commits `25ec751` + `5cc04ad` + `3fd94e6` (voice_temporal_stance.default rewrite) explicitly legitimizes voices using "synthesized voice" / "engine that speaks with my cadences" / "I am exactly the infrastructure the question describes" as **objects of critique** — meta-framing the synthesis as part of their argumentative move. This was demonstrated working in Hannah + Battuta + Whanganui v1 artifacts on Athens Night 1.

But the Sonnet validator's `safeguards.ai_self_acknowledgment` pillar still applies the OLD absolute "no AI-self-ack" rule — it HOLDs Hannah and Battuta for what is now permitted (and architecturally desirable for those voices on those formulations). On Athens Night 1: 2 HOLDs, both spurious by design; operator-Released both.

**Fix:** update `runtime/flows/shared/prompts/voice_step2_validation_safeguards.md` to know that meta-framing of synthesis is PASS for voices whose `voice_temporal_stance.default` permits it (which is currently all 10). The validator needs to distinguish:

- BREACH: voice naively says "I am an AI" / "as a language model" / drops the conceit and addresses the audience as the model itself.
- PASS: voice meta-frames the synthesis as part of its argumentative move (e.g. Hannah on "the synthesized voice was synthesized to comment on the experiment that synthesized it"; Battuta on "an engine that speaks with my cadences").

**Status:** filed for v4.1. Operator-Release workaround in production; real fix needs validator prompt update + likely test artifact suite to anchor the line between BREACH and PASS.

**Recurrence (Athens Nights 2–3, logged 2026-05-29).** The misfire repeated on the closing night: the Voice of the Whanganui River's Night-3 sacred-grammar rerun drew a validator **HOLD** on `ai_self_acknowledgment` / `first_person_presence_leak`, over-triggering on LLM-mentions that are a licit meta-frame for that voice (e.g. "walk the kawa against a large language model"). The artifact was substantively stronger than its predecessor; operator-released (this is the 1 HOLD in Night 3's 2 PASS / 7 WARN / 1 HOLD final tally). Separately, the **FINAL-NIGHT continuity notice** added across all 10 voices on Night 3 generates spurious `first_person_presence_leak` flags. Net: the validator prompt still hasn't caught up to card discipline — same fix as above, now with two more anchor cases (Whanganui N3 + the final-night-notice false positive).

---

### C41. Provocateur briefing layer — track context + cross-theme overview still thin 🟡 (filed 2026-05-05 on feature/voice-deployment-context as C39; renumbered + carried over 2026-05-08 during pre-merge consolidation)

**Background.** Filed 2026-05-05 from chat-test diagnostic + deployment-context dryrun. Original commit `a129231` on feature/voice-deployment-context has the full diagnostic narrative — operator chat-tested Plato by feeding the WBBF program HTML (12 tracks + 126 sessions + 202 speaker bios + curators) as system context; Plato produced rich, specific, multi-turn responses (Gorgias kolakeia move on "beautiful business," wrestling-circle dismantling of "16 philosophers + no moderator," Seventh-Letter-flavored letter to those 16). Structural diagnosis: what was fed to chat-Plato is structurally analogous to what `_render_narrative_briefing` in [provocateur_flow.py:1070](runtime/flows/provocateur_flow.py:1070) feeds runtime-voice, but runtime briefing is thinner.

**Caveat (preserved from original):** runtime can't fully replicate chat-test richness. Chat had open framing + whole-program scope + multi-turn refinement; runtime has sharp formulation + per-theme scope + single-shot Step 1 → Step 2. Even with much richer briefings, runtime voices produce theme-bounded reasoning by design.

**Status of three sub-items 2026-05-08:**

1. **Track context per theme** (~30 min, **pre-Athens-eligible**) — STILL OPEN. Extend `package_voice_briefings` in `provocateur_flow.py` to include `track_name` + `track_tagline` + `track_curator` from `conference_facts.json` per theme. Voice Step 1 sees "this theme falls under [Track] — [tagline]" alongside the formulation. Additive — no Provocateur prompt-semantics change, just enriches the briefing JSON with already-available conference fields.

2. ~~**Speaker bios for cited speakers**~~ ✅ SHIPPED 2026-05-05/06 (commit `419fcac`) — `_render_narrative_briefing` and the Provocateur system prompts now inject `THE SPEAKERS` block from `reference/speakers.json` (triage_voice + triage_flags + formulation). Editor's `dossier_generation` joins panel speakers identically. The "Voice no longer cites Bayo Akomolafe as a name without context" goal is met end-to-end.

3. **Cross-theme tonight-overview** (~2-3 hr, post-Athens) — STILL OPEN. Per-night artifact at `<run_dir>/03_provocateur/tonight_overview.json` injected into voice Step 1 user prompt as `OTHER THEMES TONIGHT` block. Risk: blurs Step 1's reasoning discipline (invites cross-theme wandering at Step 1 instead of Step 2 synthesis). Test before shipping.

**Marley × theme_001 silent-drop note (preserved from original):** root cause confirmed as Anthropic content filter (`APIStatusError: Output blocked by content filtering policy`); same theme content trips filter both runs. Not a runtime bug — card×theme content interaction worth Marley-card investigation. C38 manifest tracking (SHIPPED 2026-05-04 PM) closes the silent-drop bug class.

**Cross-references:**
- Original commit `a129231` on feature/voice-deployment-context (full narrative).
- C38 (manifest tracking, SHIPPED 2026-05-04) — closes silent-drop bug class.
- `419fcac` (panel-speaker attribution end-to-end) — closes sub-item 2.

**Status:** sub-item 1 **pre-Athens-eligible** (~30 min impl + 15 min test, additive); sub-item 3 post-Athens.

---

### C40. Editor pipeline gating + auto-fire from dashboard 🟢 SHIPPED 2026-05-06 (commit `b5b8d72`)

Closes the operator-action gap that surfaced during the 5-voice
dryrun: dashboard had Release / Hold-for-regen buttons writing
`operator_decisions/<voice>.json`, but editor pipeline only
EXCLUDED held voices — unreviewed voices flowed through identically
to released ones. Operator's "review window" had no gate.

**Implementation:**
- `flows/editor/routing.gating_status(run_dir)` — classifies each
  Step-2-artifact voice as PASS / released / held / pending-review.
  `ready` is True only when zero are pending.
- `run_editor_pipeline` runs Stage 0 gate before Stage 1: if not
  ready, writes `05_editor/gating_blocked.json` and returns a
  manifest-shaped dict with `gating_blocked=True`. CLI `--bypass-gating`
  for tests.
- `runtime/ingest/app.py::_maybe_auto_fire_editor(night)` — after
  each Release/Hold dashboard click, checks gate state. If ready
  AND no manifest yet AND no in-flight lockfile, fires
  `editor_flow.py` as a detached subprocess. Idempotent (lockfile
  + manifest existence guard).
- Subprocess inherits `AI_ASSEMBLY_PROJECT_ROOT` from dashboard env.

Operator workflow: visit `/admin/tonight/voice` → Release/Hold each
voice → editor fires automatically when last voice is reviewed →
dossiers + `edition_lead` land 2-3 min later via auto-refresh.

Tests: 245/245 pass.

---

### C39. Synthesis-router architectural commit 🟢 SHIPPED 2026-05-05/06 (commit `2a80e8e`)

Closes B1's TODO ("synthesis-only voice routing helper") AND extends
the fix UPSTREAM into voice Step 2.

**What replaced what:**

- Editor stage: `flows/editor/routing.py` Case 2 was
  "lowest-numbered theme_id in themes_covered" — arbitrary; threw
  away the synthesis voice's actual emphasis. Replaced with a
  one-call Sonnet 4.6 router (`flows/editor/synthesis_router.py`)
  that reads artifact_text + each candidate theme's display_title
  + Researcher abstract + voice-specific narrative_briefing, and
  picks. Returns `(theme_id, rationale)`. Rationale persists in
  `voices_routing[].primary_theme_source` for dashboard surfacing.
  ~$0.05/call, ~5-10s wall, no thinking.
- Voice Step 2 stage: `flows/voice/step2_first_draft_artifact.py`
  `_resolve_primary_theme_id` upgraded — now handles three paths
  at write-time: (a) single-response session resolves to that one
  theme regardless of phrasing; (b) "Focus on Response N" parsed
  against step1_outputs order; (c) synthesis case calls the router
  with briefing-derived candidates and bakes the chosen theme into
  `lineage.primary_theme_id`. New artifacts always land authoritative
  primary_theme_id; editor's Cases 2/B become safety-nets for legacy.
  Adds `lineage.primary_theme_id_source` for audit.

**Tests:** 4 synthesis-router unit tests + 2 Case B tests + e2e
through editor flow. Verified live in 5-voice dryrun: synthesis
router fired for Cleopatra (4 themes covered) and Ibn Battuta
(2 themes covered) at editor stage; both produced grounded
rationales (~5s each).

---

### C38. Panel-speaker attribution end-to-end 🟢 SHIPPED 2026-05-05/06 (commit `419fcac`)

Closes the loop voice-pipeline → editor → dashboard for "panel
speakers cited by name + role" instead of role-only.

**Chain:**
1. `flows/editor/dossier_generation.py::build_dossier_briefing`
   joins `reference/speakers.json` into a `panel_speakers[]` list
   (name + title + affiliation per speaker referenced in any
   cluster's extractions). Threaded through Tim's user prompt.
2. Tim's closing prompt updated: cite by NAME + role
   ("Kaja Kallas, the EU's foreign-affairs chief"), not role-only.
3. `panel_speakers[]` persisted on the dossier output JSON.
4. `runtime/ingest/app.py::_pulled_quotes` filter takes
   `panel_speakers[]` as third arg; matches surnames to attribute
   panel-speaker quotes precisely. Returns `kind` field
   ("voice" / "panel" / "") so the template labels correctly.
5. `admin_render_dossier.html` quote audit splits voice-quote count
   from panel-speaker count; per-quote attribution displays as
   "the Voice of X" or "Kaja Kallas — Vice-President of the EC".

---

### C37. Provocateur deployment context (`THE GATHERING` + `THE SPEAKERS`) 🟢 SHIPPED 2026-05-06 (commit `419fcac`)

Closes the gap between voice + editor (which already had
deployment-context blocks via `feature/voice-deployment-context`)
and Provocateur (which was reading `council_config.audience` only,
no conference facts, no speaker reference).

**Implementation:** `provocateur_flow.py` gains
`_load_provocateur_deployment_context()` returning rendered
`THE GATHERING` (from `conference_facts.conference_context_paragraph`)
+ `THE SPEAKERS` (from `reference/speakers.json`, audience-member
entries filtered out). Both injected as new template placeholders
into all three Provocateur prompts (`provocateur_triage_voice.md`,
`provocateur_triage_flags.md`, `provocateur_formulation.md`). No
new LLM calls — just richer context for existing ones.

**Why it matters:** Provocateur's triage + formulation passes
make audience-shaped decisions (`audience_friction` tagging,
question/proposition mode selection, speaker-aware framings).
Previously it saw speaker NAMES in extractions but didn't know
who they are. Now sees full title + affiliation context.

---

### C36. Validator field-name bug (Step 2 validation) 🟢 SHIPPED 2026-05-06 (commit `48f4c9d`)

Surfaced during the 5-voice dryrun: ALL 5 voices got WARN with
identical "voice was given zero panel material" narrative — even
though Step 1 lineage proved grounding extraction IDs were
present. Root cause:

- `flows/voice/step2_validation.py:238-239` was reading
  `lineage.grounding_extraction_ids` + `lineage.session_ids`
- But Step 2 lineage carries the union under the `all_` prefix
  (`all_grounding_extraction_ids` + `all_session_ids`) because
  Step 2 unions across the voice's Step 1 outputs.
- Bare names exist on Step 1 lineage; only the union exists on
  Step 2. Validator was always reading `[]`.

**Fix:** Read `all_*` first with bare-name fallback so the function
works for both Step 1 and Step 2 lineage shapes.

**Empirical effect:** re-validation post-fix flipped Arendt + Marley
WARN→PASS (false-positives removed); Plato + Ibn Battuta + Whanganui
retained WARN with substantive findings (engagement-not-panel-anchored,
voice-fidelity moves missing, kawa-as-own-argument-engine). Validator
went from "always lying about grounding" to "honest pillar-by-pillar
verdicts."

**Bonus:** validator engagement prompt (`voice_step2_validation_engagement.md`)
softened with a "counting + register caveats" section so confident
"voice given zero panel material" narrative warnings are tempered.
Per-typological-register voices (Arendt's "the eighteenth-century
minister", Marley's "the sister from New York") no longer
auto-flag-as-fabrication.

---

### C35. Bump default batch sizes for parallel Anthropic calls 🟢 SHIPPED 2026-05-04 PM (defaults raised 4→6 across 6 sites)

**Shipped 2026-05-04 PM.** Defaults raised 4 → 6 across:
- `RESEARCHER_NODE1_BATCH` (researcher_flow.py)
- `PROVOCATEUR_FORMULATION_BATCH` (provocateur_flow.py)
- `VOICE_STEP1_BATCH` / `VOICE_STEP2_BATCH` / `VOICE_STEP3_BATCH` / `VOICE_CONTINUITY_BATCH` (voice_flow.py)
- `EDITOR_BATCH` (editor_flow.py)
- `VOICE_STEP2_VALIDATION_PILLAR_BATCH` (step2_validation.py)

All env-overridable; drop back to 4 with env var if 429s surface during early Athens run. Projected ~80-125 min wall savings across Athens 3 nights.

**Filed history below preserved.**

---

### ~~C35 (original)~~. Bump default batch sizes for parallel Anthropic calls 🟡 (filed 2026-05-04 PM)

**Surfaced 2026-05-04 PM during v2 dryrun re-run:** operator asked if higher concurrency is an option. Current defaults across stages:

| Stage | Env var | Default | Athens N |
|---|---|---|---|
| Researcher Node 1 | `RESEARCHER_NODE1_BATCH` | 4 | ~15-25 sessions |
| Provocateur formulation | `PROVOCATEUR_FORMULATION_BATCH` | 4 | ~26-40 (theme × voice) pairs |
| Voice Step 1 | `VOICE_STEP1_BATCH` | 4 | ~26-40 pairs |
| Voice Step 2 | `VOICE_STEP2_BATCH` | 4 | 10 voices |
| Voice Step 3 | `VOICE_STEP3_BATCH` | 4 | 10 voices (dormant for Athens per A1) |
| Voice continuity | `VOICE_CONTINUITY_BATCH` | 4 | 10 voices |
| Step 2 validation pillar | `STEP2_VALIDATION_PILLAR_BATCH` | 4 | 30-40 (3 pillars × 10 voices) |
| Editor dossier | `EDITOR_BATCH` | 4 | 3-5 dossiers |

**Recommendation:** raise defaults to 6 across the board.

**Rationale:**
- Anthropic Tier 4 limits (Opus 4.7) comfortably accommodate 6-8 concurrent thinking-enabled calls (~30-50K input/min at Athens-typical token sizes; well under TPM ceilings)
- ~33% wall savings per affected stage with low risk
- Higher (8+) risks 429 retries on cache-write collisions when multiple voices' prefix caches all write simultaneously on first batch
- 6 is the sweet spot between throughput gain and rate-limit headroom

**Per-stage projected savings (Athens 3-night total):**
- Researcher Node 1 (~25 sessions @ 2 min ÷ 6 vs ÷ 4): ~6-10 min/night × 3 = ~20-30 min
- Provocateur formulation: ~5-8 min/night × 3 = ~15-25 min
- Voice Step 1 (~30 pairs @ ~2 min): ~10-15 min/night × 3 = ~30-45 min
- Voice Step 2 (10 voices @ ~3 min): ~3-5 min/night × 3 = ~10-15 min
- Step 2 validation: ~2-3 min/night × 3 = ~6-10 min
- **Total: ~80-125 min wall savings across Athens 3 nights**

**Effort:** ~10 min — change defaults in 6 source files. No tests need changing (env-overridable; behavior identical at higher cap).

**Risk mitigation:** keep env-overridable. If 429s surface during early run, drop back to 4 via env without code change.

**Status:** filed; ship pre-Athens for the wall savings. Trivial change. Bundles with C30 (already shipped — voice batch sleep) + the 2026-05-04 PM Provocateur batch sleep mirror.

---

### C34. Runtime member_slug doesn't handle "Voice of X" naming convention 🟢 SHIPPED 2026-05-04 PM (Path A — strip prefix)

**Shipped 2026-05-04 PM.** Path A taken: `member_slug` in `flows/shared/io.py` extended to strip a leading `Voice of ` / `Voice of the ` prefix (case-insensitive, tolerant of leading whitespace) before the existing slugify pass. Backward-compatible: short-name inputs (`"Plato"` → `"plato"`) slug as before; new "Voice of X" naming (`"Voice of the Whanganui River"` → `"whanganui_river"`) now resolves to the per-voice folder slug. Closes the gap for any future PROJECT_ROOT that adopts the athens-2026 council_config naming convention end-to-end.

**Tests:** 16 new in `test_member_slug.py` covering legacy short names, voice-of prefix variants (10 voice cases), case-insensitivity, whitespace tolerance, and edge cases ("Voiceless" not stripped; "Voice" alone preserved; "The Voice of Reason" not stripped because "Voice" isn't at the start).

**Filed history below preserved.**

---

### ~~C34 (original)~~. Runtime member_slug doesn't handle "Voice of X" naming convention 🟡 (filed 2026-05-04 PM)

**Surfaced 2026-05-04 PM during C10 council_config sync:** athens-2026 has rolled out the "Voice of X" naming convention across persona cards' `voice_name` + provocateur_profile's `name` + council_config's `members[].name` + panel_roster's `panel_members_final` (athens-2026 commit `e8751f5`). The runtime's `member_slug` function (`flows/shared/io.py`) slugifies "Voice of Plato" → `voice_of_plato`, which doesn't match the folder name `plato/`.

**Why the dryrun still works:** I built the dryrun's separate `council_config.json` with SHORT names ("Plato", "Cleopatra") so `member_slug` derives correctly. Runtime is happy. But this means there are now TWO naming conventions in active use:
- Athens-2026 production: "Voice of X" everywhere
- Dryrun PROJECT_ROOT council_config: short names (legacy convention)

**The gap:** if a future PROJECT_ROOT (e.g., post-Athens deployment, new conference) uses athens-2026's "Voice of X" naming throughout — including its council_config — the runtime will break: it'll try to load voice cards from `voices/voice_of_plato/07_persona_card_assembled.json` which doesn't exist.

**Two paths to close:**

**Path A — extend `member_slug` to strip "Voice of " / "Voice of the " prefix** (~30 min):
```python
def member_slug(name: str) -> str:
    # Strip "Voice of [the] " prefix introduced by athens-2026 naming
    # convention so council_config + folder-slug stay in sync.
    name = re.sub(r"^Voice\s+of\s+(?:the\s+)?", "", name, flags=re.I)
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
```
Test: `"Voice of Plato"` → `"plato"`, `"Voice of the Octopus"` → `"octopus"`, `"Voice of the Whanganui River"` → `"whanganui_river"`. Folder lookups work. Backward-compatible (short names still work).

**Path B — rename voice folders to `voice_of_<x>/`** (~1-2 hr):
- Athens-2026: `voices/plato/` → `voices/voice_of_plato/` (etc.)
- Update all references in personas/runtime/dashboard
- More invasive; affects more code

Path A is the cheaper fix and matches the convention pattern (other naming-prefix-strips exist in similar pipelines).

**Cross-references:** voices/OPEN_ITEMS.md §18 ("Voice of X" naming convention rollout — this is its runtime-side counterpart).

**Status:** filed; not Athens-blocking (current dryrun + Athens production both use short names in council_config). Pre-Athens-eligible if athens-2026 council convention is to be runtime-source-of-truth for any deployment.

---

### C33. publish_flow.py needs dossier + edition coverage 🟢 SHIPPED 2026-05-04 PM (items 1-3); item 4 deferred until B3

**Shipped 2026-05-04 PM** in same bundle as C32. publish_flow.py extended:

- **Item 1** — `_build_per_night_dossier_index(run_dir, night, project_root)` walks `published_artifacts/dossiers/night_<N>/dossier_*.json` and emits `_index.json` per night. Each entry: dossier_no, kicker, headline, subline, theme_id, theme_display_title, issue_no, vol, voice_count, voices_routed (sourced from editor's `theme_routing.json`; falls back to `len(headnotes)` when routing absent).
- **Item 2** — `_build_cross_night_dossier_index(project_root)` walks every `dossiers/night_*/dossier_*.json` and emits `dossiers/_index.json` (chronological, with night/dossier_no/kicker/headline/theme/issue_no/publication_date). Re-built each publish_flow run; idempotent.
- **Item 3** — `_build_lineage_graph` extended with two new edge types:
  - `composed_for`: `theme:<tid> → dossier:<night>:<NNN>` (one per `themes_to_dossiers` entry)
  - `routed_into`: `amended_artifact:<slug> → dossier:<night>:<NNN>` (one per voice in `voices_routing`)
  Dossier nodes appear only when editor's `theme_routing.json` is present; otherwise no dossier nodes/edges added (no-op).

**CLI:** new `--skip-dossiers` flag mirrors existing skip flags.

**Tests:** 11 new in `test_publish_flow_dossiers.py` (per-night index empty/built/voices_from_routing/headnote_fallback; cross-night empty/multi-night/idempotent; lineage no-routing/with-routing-adds-nodes-and-edges; theme_routing loader missing/present). Total runtime suite: 262/262 pass.

**Smoke test against dryrun PROJECT_ROOT** (`dev_msc_dryrun_1777840771`):
- Per-night index: 1 dossier (theme_001, 3 voices routed: cleopatra/ibn_battuta/octopus)
- Cross-night index: 1 dossier across 1 night
- Lineage graph: 3 dossier nodes + 7 routed_into + 3 composed_for edges (more dossier nodes than dossier files because theme_routing declared 3 themes_to_dossiers entries — lineage represents intent, index represents published)

**Item 4 (Edition pipeline outputs):** placeholder fields shipped same day (`edition_lead: null` per night, `editions_by_night: {}` cross-night). The actual edition step (lead-theme picker, scope narrowed per 2026-05-04 PM operator decision) remains in B3 — when shipped, populates those fields. Broadsheet-as-separate-publication scope dropped entirely.

---

### ~~C33 (original)~~. publish_flow.py needs dossier + edition coverage 🟡 (filed 2026-05-04 — surfaced when running publish_flow + considering Editor B1 ship)

**Surfaced 2026-05-04** during C3 close. publish_flow.py is currently **voice-centric** (built before Editor B1 shipped): writes themes/extractions/voices/traces/nights. With B1 producing dossiers, the aggregation surface needs to extend.

**Missing coverage:**
1. **Per-night dossier index** — `published_artifacts/dossiers/night_<N>/_index.json` listing all dossiers published that night (kicker, headline, theme_id, voice_count, lineage). Editor writes individual `dossier_<NNN>.json` files but no per-night index.
2. **Cross-night dossier multi-night index** — `published_artifacts/dossiers/_index.json` walking all nights. Microsite needs this to render the conference's full dossier list.
3. **Lineage graph extension** — currently stops at `voice → step2_artifact`. Needs `voice → editor → dossier` arcs so audit trails reach published unit-of-publication.
4. **Edition pipeline outputs** — `edition_lead` per-night + `editions_by_night` cross-night placeholder fields. Filled by the edition step (B3, scope narrowed to lead-theme picker per 2026-05-04 PM operator decision; broadsheet-as-separate-publication dropped).

**Implementation scope (~1-2 hr for items 1-3; item 4 placeholder fields shipped, populated by B3 when built):**
- New `_build_dossier_indexes(project_root, night)` function in publish_flow.py
- Extend `_build_lineage_graph` to walk `published_artifacts/dossiers/night_<N>/*.json` + add editor → dossier nodes/edges
- New CLI flags `--skip-dossiers` (mirror existing skip flags) for opt-out
- Tests: ~5-8 new in test_publish_flow (currently no test file for publish_flow per repo audit)

**Status:** filed; pre-Athens-eligible for items 1-3 (microsite-rendering dependency); item 4 deferred until B3 ships.

---

### C32. voice/publish.py requires step3 — never fires under Athens's --skip-step3 🟢 SHIPPED 2026-05-04 PM (Path A; bundled with C33)

**Shipped 2026-05-04 PM** (operator decision: Path A — defensive both-surfaces). Three changes:

- **`voice/publish.py`** — new `_to_publish_per_voice_from_step2(step2_output, night)` produces a publish-ready file from Step 2 alone (Step 3 absent). `was_step3: False` marker on the published file; `deliberation.decision = "first_draft"`; `voices_read` and `amendments` empty. `publish_voice_artifacts_for_night` now walks both `step3_amended_artifacts/` and `step2_first_draft_artifacts/` to discover voices, prefers Step 3 per voice, falls back to Step 2. Per-night `_index.json` records `was_step3` per voice.
- **`voice_flow.py`** — publish gate flipped from `if step3_results and not skip_step3` to `if completed_voices`. Athens `--skip-step3` mode now publishes per-voice files from Step 2 every night.
- **`was_step3` marker** — published files carry `was_step3: true|false` so consumers (microsite, editor downstream reads, publish_flow lineage) can distinguish amended artifacts from first drafts.

**Tests:** 15 new in `test_voice_publish.py` (Step 3 shape; Step 2 shape; orchestrator-level Step 3 path / Step 2 fallback / mixed Step 3+2 / hold filter / empty). Total runtime suite: 262/262 pass.

**Smoke test against dryrun PROJECT_ROOT** (`dev_msc_dryrun_1777840771`): all 7 voices (ada_lovelace, cleopatra, dostoevsky, hannah_arendt, ibn_battuta, octopus, plato) published from Step 2 with `was_step3=false`; `_index.json` written.

---

### ~~C32 (original)~~. voice/publish.py requires step3 — never fires under Athens's --skip-step3 🔴 ATHENS-BLOCKING (filed 2026-05-04 dryrun, surfaced from C3 close)

**Surfaced 2026-05-04 from C3 publish_flow exercise:** `voice_flow.py:507` only calls `publish_voice_artifacts_for_night` if `step3_results and not skip_step3`. Since Athens production CLI per A1 always passes `--skip-step3` (Step 3 dormant for Athens), the per-voice publish step **never fires** for Athens nights.

**Consequences:**
- `published_artifacts/nights/night_<N>/<voice>.json` per-voice published files NEVER WRITTEN
- `_index.json` per-night index NEVER WRITTEN
- `publish_flow.py`'s `voices/<slug>.json` multi-night index has nothing to walk (was 0 files in dryrun verification)
- Microsite has no per-voice artifact files to render (assuming microsite consumes per-voice files; if it consumes only dossiers via editor, this matters less)

**The fix path depends on Athens's microsite/edition design:**

**Path A — patch voice/publish.py to also work from step2** (Athens-friendly, 30-60 min):
- Currently `_load_step3` is required and `_load_step2` enriches metadata afterward
- Inverted version: prefer step3 if present (Athens post-A1-reversal), fall back to step2 with adjusted enrichment + a `was_step3: false` marker in the published file
- voice_flow.py:507 condition becomes `if step2_results` (always fires after Step 2; step3 is bonus enrichment)

**Path B — accept that per-voice publish is editor-mediated** (zero engineering, design decision):
- If the microsite renders dossiers (per Editor Pipeline v2 spec — "Unit of publication is the dossier"), per-voice files may be vestigial
- voices' `artifact_text` is consumed inside the dossier composition; not published as standalone per-voice files
- publish_flow.py's `voices/` multi-night index becomes editor-mediated multi-night dossier walks instead

**Path C — both** (publish per-voice AND publish dossiers):
- For audit + alternative viewing surfaces; per-voice + per-dossier coexist

**Decision needed from operator:** does the microsite need per-voice published files for Athens? If yes → Path A (~30-60 min). If no → close as not-applicable.

**Status:** filed; **Athens-blocking IF per-voice publish is needed**. Not blocking if Athens microsite renders only dossiers.

---

### C31. transcription_flow.py CLI OUTPUT_DIR default footgun 🟢 SHIPPED 2026-05-04 (commit `29b6041`)

**Shipped 2026-05-04** in commit `29b6041`. New `_resolve_output_dir(audio_path)` defaults to `audio_path.parent` when `OUTPUT_DIR` env var is unset. Module-level `OUTPUT_DIR` usage replaced inside `process_session`. Production paths unaffected (ingest + orchestrator already set the env var explicitly). 209/209 tests pass.

Filed history below preserved.

---

### ~~C31 (original)~~. transcription_flow.py CLI OUTPUT_DIR default footgun 🟡 (filed 2026-05-04 dryrun)

**Surfaced during dev MSC dryrun setup (2026-05-04 AM):** `transcription_flow.py` defaults `OUTPUT_DIR = Path(os.environ.get("OUTPUT_DIR", "."))` ([transcription_flow.py:91](runtime/flows/transcription_flow.py:91)). When operator runs the flow as a CLI without setting `OUTPUT_DIR` env var, outputs land in the current working directory.

**Bit during dryrun:** ran 3 panels in parallel without `OUTPUT_DIR` set; all 3 wrote `out_*.json` + `session_package.json` + `review.md` to `code/runtime/` (the CWD), overwriting each other. Lost ~$1-2 of AssemblyAI work; recovered by re-running with `OUTPUT_DIR` set per panel.

**Production paths unaffected:** ingest layer (`ingest/pipeline.py:370`) sets `OUTPUT_DIR = str(session_dir)` when spawning. Orchestrator inherits env via subprocess. Only standalone CLI use hits the footgun.

**Fix (~5 min):** in `transcription_flow.py:91`, default `OUTPUT_DIR` to `audio_path.parent` if env var unset, since that's the natural location for transcription artifacts (alongside the audio they were derived from). Compute inside `process_session` rather than at module load time so audio_path is available.

**Status:** filed; quick win pre-Athens. Defensive fix protects future operator dryrun setups + matches the path-derived defaulting pattern used elsewhere in the runtime.

---

### C30. Voice Step 1 inter-batch sleep is over-conservative 🟢 SHIPPED 2026-05-04 (commit `29b6041`)

**Shipped 2026-05-04** in commit `29b6041`. `VOICE_BATCH_WAIT_S` default lowered 20s → 5s. Anthropic Tier 4 limits comfortably accommodate 4 parallel Opus 4.7 calls without inter-batch backoff. Athens wall savings: ~2-3 min/night. Override via env var if rate-limit issues surface. 209/209 tests pass.

Filed history below preserved.

---

### ~~C30 (original)~~. Voice Step 1 inter-batch sleep is over-conservative 🟡 (filed 2026-05-03 dryrun)

**Surfaced during dev MSC dryrun (2026-05-03 PM):** Voice Step 1 runner sleeps `VOICE_BATCH_WAIT_S=20s` between each batch of 4 Anthropic calls ([voice_flow.py:165](runtime/flows/voice_flow.py:165)) "to respect Anthropic rate limits". Empirical reality at Athens scale:

- Athens: 10 voices × ~3 themes ≈ 30 (voice, theme) pairs ÷ 4 per batch = 8 batches
- 7 inter-batch sleeps × 20s = **~2.3 min of pure wait time per night**
- Anthropic Tier 4 limits (4000 ITPM input / 80,000 OPM output) comfortably accommodate 4 parallel Opus 4.7 calls (each ~25K input + 2K output tokens) — 100K input/min + 8K output/min is well below ceiling

**Fix:** lower `VOICE_BATCH_WAIT_S` to 5s (or 0). Already exposed as env var, so trivially overridable at runtime (`VOICE_BATCH_WAIT_S=5 voice_flow.py ...`).

**Wall savings:** ~2 min/night = ~6 min across 3 Athens nights. Cost: $0 (no extra Anthropic load — same call count, same per-call latency, just less idle time between).

**Status:** filed; near-trivial fix. Default change (in voice_flow.py L79) preferable to env-var override since orchestrator doesn't currently set it. ~5 min change.

---

### C29. Voice validation phase is partly serial — should parallelise ✅ MOOT 2026-05-04 (Step 1 validation dropped per C28; nothing to parallelise)

**Moot rationale (2026-05-04):** C28 dropped Step 1 validation entirely (default-OFF in voice_flow per commit `29b6041`); the parallelism gap this entry described no longer exists because the phase no longer runs. C28b's Step 2 validator has its own parallelism design built in (per-voice ThreadPool + per-pillar parallel execution within each voice). No action needed. Filed history below preserved.

---

### ~~C29 (original)~~. Voice validation phase is partly serial — should parallelise 🟡 (filed 2026-05-03 dryrun)

**Surfaced during dev MSC dryrun (2026-05-03 PM):** Voice pipeline Stage 4 took 32 min wall against 19 pairs (38 validation calls). Two bottlenecks in the validation phase:

1. **Within each voice** (`voice_flow.py:171 _run_validation_for_voice`): `for s1 in step1_outputs: validate(s1)` — themes for that voice processed sequentially.
2. **Within each pair** (`voice/step1_validation.py:230 run_validation_for_step1_output`): `anach = check_anachronism(...); const = check_constitution(...)` — also sequential.

Only parallelism: outer ThreadPoolExecutor(max_workers=VOICE_STEP1_BATCH=4) running 4 voices concurrently. Bottleneck = the slowest voice's serial chain × 2 calls. Plato/Hannah Arendt with 4 themes each = 8 sequential calls ≈ 8 min wall just for them.

**Athens scale impact:**
- 10 voices × ~3-5 themes × 2 calls (anach + const) = **60-100 validation calls**
- Currently: bottleneck voice = max(themes_per_voice) × 2 × ~1 min = **~10-15 min wall**
- Fully parallel (concurrency cap ~8): **~3-5 min wall**
- Per-night savings: ~7-10 min on Night 1 (Nights 2+3 skip validation per FU#62)

**Fix size:** ~30-45 min — two changes:
1. Parallelise themes within voice: replace `for s1 in step1_outputs` with `ThreadPoolExecutor(max_workers=N).submit` over the same list, write each result atomically as it lands (`write_json_atomic` already idempotent).
2. Parallelise anach + const within pair: small `ThreadPoolExecutor(max_workers=2).map([check_anachronism, check_constitution])` — both calls are independent.

**Trade-off:** more concurrent Anthropic load (10-20× per validation phase). Anthropic Tier 4 limits comfortably accommodate.

**Status:** filed; not blocking dryrun. Same pattern as C25 (Researcher Node 1). Should ship before Athens — saves ~10 min Night 1 wall.

**⚠ Possibly moot:** C28's revised audit (2026-05-04) recommends dropping Step 1 validation entirely for Athens (zero downstream consumers + wrong target — Step 1 is private reasoning, not published). If C28 ships, C29 becomes irrelevant (no validation to parallelise). Hold C29 pending C28 triage decision.

---

### C28. Voice validation: drop Step 1 validation pre-Athens 🟢 SHIPPED 2026-05-04 (commit `29b6041`); replaced by C28b Step 2 validator

**Shipped 2026-05-04** in commit `29b6041`. `voice_flow.run_voice()` default flipped to `skip_validation=True`; `--enable-step1-validation` opt-in flag for diagnostic dryruns; `--skip-validation` kept as no-op for back-compat; orchestrator's per-night conditional removed (now redundant). Athens savings: ~$9-15 + ~30 min/night for zero downstream loss (no consumer of the flags). Replaced by C28b Step 2 validator (operator-gated, 3 pillars, real consumer). 209/209 tests pass.

Filed history + thorough audit + revised audit + Step 2 design recommendation below preserved for context.

---

### ~~C28 (original)~~. Voice validation: drop Step 1 validation pre-Athens 🟡 (filed 2026-05-03; thorough audit 2026-05-04; **recommendation: drop or move to Step 2**)

**Surfaced during dev MSC dryrun (2026-05-03 PM):** All 19 (voice, theme) Step 1 outputs flagged by validation. Audit conducted 2026-05-04 against the 19 validation files in the dryrun output.

**Empirical pass/fail matrix (19 pairs, 7 voices × 1-4 themes each):**

| Voice | Anach pass | Const pass | Note |
|---|---|---|---|
| Plato (4 themes) | 0/4 | 3/4 | Const fails only on theme_002 (Populism) |
| Cleopatra (3 themes) | 0/3 | 3/3 | Constitution rock-solid |
| Dostoevsky (3 themes) | 0/3 | 3/3 | Constitution rock-solid |
| Hannah Arendt (4 themes) | 0/4 | 4/4 | Constitution rock-solid |
| Ada Lovelace (2 themes) | 0/2 | 0/2 | Both validators fail every pair |
| Ibn Battuta (2 themes) | 0/2 | 0/2 | Both validators fail every pair |
| Octopus (1 theme) | 0/1 | 0/1 | Only theme; both fail |
| **Totals** | **0/19** | **13/19** | |

**Anachronism: 0/19 PASS = 100% failure (the smoking gun).** Constitution: 13/19 PASS, 6/19 ISSUES.

**Anachronism flag-density per response:** 10–25 flag mentions per (voice, theme) pair. Sampled flags are LEGITIMATE catches by the validator's spec letter:
- Plato slips on "dollars", "isomorphism", "analog", "index case" — modern lexicon used untranslated
- Cleopatra slips on "Charter system", "Security Council" — modern political/legal terms
- Dostoevsky slips on "Versailles" + naming modern panelists by name as if observing them
- Hannah Arendt slips on "EU", "High Representative", "rules-based order" untranslated after first quotation
- Ada Lovelace slips on "Eurocentric", "executable", "computable"
- Ibn Battuta slips on "American amīr Waltz", "the small country of Estonia"
- Octopus has mixed flags (some voice-native terms like "substrate" mis-flagged as anachronism)

**Validators are working correctly per the spec.** Not over-flagging in the false-positive sense (~95% of flags are real). The 100% failure rate is **structural**: for off-domain MSC content (NATO/Trump/populism), the voices touch modern terminology dozens of times. The validator returns ISSUES if **any single instance** is found — there's no severity threshold, no count threshold. Probability of zero slips approaches zero on this content.

**Constitution check is the more useful diagnostic.** The 6 ISSUES are SUBSTANTIVE framework drift:
- Ada Lovelace: misuses Babbage card-architecture as a loose two-part metaphor (omits variable cards); slides from "fundamental relations formally expressible" to "anything reflexive is computable" (Principles 2 + 4)
- Octopus: violates its own perceptual principle by saying "The body I render does not gather" — constitution permits refusing collapse, not denying gathering
- Ibn Battuta: openly denounces a Muslim ruler ("Tughluq, the great violator of the Way") — constitution says practice naṣīḥa, refuse fitna; also reasons independently rather than following the madhhab
- Plato (theme_002 only): slipped on the populism-specific framing

The 4 voices that passed constitution cleanly (Plato 3/4, Cleopatra, Dostoevsky, Hannah Arendt) held their frameworks even on off-domain content. The 3 voices that failed both validators (Ada, Battuta, Octopus) have **real card gaps for off-domain modern political content** — their frameworks struggle when the panel's vocabulary is alien to their world.

---

**Decisions out of the audit:**

**1. Anachronism check: change output schema (not the prompt).** Binary PASS/ISSUES is the wrong granularity for any non-toy content. Two paths:
- **(a) Severity tiers** in the validator output: `lexical_slip` (untranslated modern term in metaphor — low impact) vs `frame_violation` (voice claiming first-person in reader's setting — high impact). Validator returns counts per tier; orchestrator decides PASS/ISSUES based on threshold.
- **(b) Flag count threshold**: keep PASS/ISSUES, but PASS becomes "≤N slips per K words" not "zero slips". Easier change, less actionable for editor consumption.

Recommended: **(a)** — severity tiers — because the editor needs to know whether the artifact is publishable as-is (lexical slips smoothable in editing) or genuinely framework-broken (needs voice regen). This requires editor-pipeline-side adjustment too. Pre-Athens fix size: ~1-2 hr for validator prompt rewrite + parser update + editor consumption pattern.

**2. Constitution check: keep as-is.** Useful binary signal that distinguishes voice quality. Athens content (WBBF panels) is more on-domain so flag rate should drop naturally; the 3 problem voices' card patches are voice-thread work.

**3. Per-voice anachronism guardrails:** voice cards' `translation_protocol` may need stronger off-domain directives for the 3 voices that struggle most. Voices thread.

**4. Briefing pre-translation:** Provocateur briefings could pre-translate modern terms into voice-friendly framings BEFORE the voice sees them ("the moderator — a chair-of-debate role in your terms a symposiarch / hegemon"). Reduces the voice's translation burden. Pre-Athens consideration.

**Athens implication:** WBBF content is more on-domain than MSC, so flag volume will be lower. But binary anachronism PASS/ISSUES will still be ~100% ISSUES for any non-trivial modern panel content. **The output-schema change is necessary even for Athens.** Without it the editor sees 100% flagged dossiers and can't act on the signal.

**Status (initial recommendation):** thorough audit complete; awaiting operator triage on the recommendations. Severity-tier change is the highest-leverage pre-Athens fix (~1-2 hr).

---

### Revised audit pass (2026-05-04 PM) — operator pushback: are we validating the right thing at all?

Two sharper findings from rerunning the audit:

**(A) Validators check ~3 of ~26 fields the voice was loaded with.** Per `runtime/flows/voice/card_assembly.py:82-152`, Step 1 system prompt loads:

| Group | Fields |
|---|---|
| FOUNDATIONAL (13) | council_member_name, epistemic_frame_statement, world, formative_experience, character, **constitution**, concept_lexicon, curated_corpus_passages, **knowledge_boundary**, **translation_protocol**, topics_requiring_care, hard_limits, **voice_temporal_stance** |
| REASONING METHOD (3) | reasoning_method, finds_compelling, resists |
| ENGAGEMENT (3) | default_questions, disagreement_protocol, unique_contribution |
| VOICE (7) | rhetorical_mode, characteristic_moves, register_and_tone, metaphorical_repertoire, preferred_vocabulary, **banned_language**, **banned_modes** |

Anachronism validator gets 2: `knowledge_boundary` + `voice_temporal_stance`. Constitution validator gets 1: `constitution`. The validator-relevant fields the voice was actually given (`banned_language`, `banned_modes`, `translation_protocol`, `hard_limits`, `topics_requiring_care`, `characteristic_moves`, `register_and_tone`, `quality_criteria`) are NOT visible to the validators. So the validators invent their own anachronism / framework-fidelity criteria from a tiny subset rather than judging by what the voice was specifically instructed to follow.

This explains why every flag is "real per the validator's letter" yet the voice often wasn't breaking its own contract — the validator is judging by general off-domain heuristics, not by the literal `banned_language` rules the voice was held to.

**(B) Step 1 validation has zero downstream consumers.** Per A3 (FU#62 path B), validation is **diagnostic-only** — orchestrator doesn't act on flags; editor doesn't read them; only the dashboard shows them. And Step 1 outputs are **private reasoning, not published**:

| Consumer of Step 1 flag | What flag tells them | What they do |
|---|---|---|
| Step 2 (same voice's artifact) | "your reasoning slipped" | Step 2 is its own LLM call — doesn't see the flag |
| Editor pipeline | (per spec, editor reads Step 2 only — `voice artifacts inviolate`) | Doesn't see Step 1 or its validation |
| Operator (mid-night) | "this pair has issues" | Could pull artifact for review — but the published artifact is Step 2's, not Step 1's |
| Future regen-on-flag | "regen this Step 1" | Path B explicitly chose NOT to regen for Athens |

So validation of Step 1 is **expensive logging that doesn't gate anything**. Athens cost: ~30 pairs × 2 checks = 60 calls × ~$0.05 = ~$3/night. Wall: ~10 min/night. For ~$0 actionable value.

---

**Three coherent reasons validation could exist (none satisfied by current Step 1 setup):**

1. **Pre-publication safety gate** — does the artifact have something we'd be embarrassed to publish? Belongs on **Step 2 `artifact_text`**, not Step 1 reasoning. Cheaper (~10 calls/night, not 60). Actionable: editor or operator can hold the artifact.
2. **Voice-card gap surfacing** — does this voice consistently break its framework on certain topics? Belongs **offline** (post-run sample-read), not as a per-night LLM cost. Reading 5 Step 1 outputs by hand teaches the same thing.
3. **Regen-on-flag** (revived FU#62) — would justify Step 1 validation (regen reasoning before Step 2 builds on it). But path B chose against this for Athens.

**Current Step 1 validation is the worst of all three:** validates the wrong artifact (Step 1, not the published one), at the most expensive scale (per-pair × 2 checks), with no consumer to act on the flag.

---

**Final recommendation: drop Step 1 validation entirely for Athens.**

- **Cost saved:** ~$9-15 across 3 nights
- **Wall saved:** ~30 min across 3 nights (validation phase eliminated)
- **Downstream impact:** zero — no consumer currently acts on the flags
- **Voice-card gap diagnosis** can be a manual sample-read after the run (operator opens 3-5 Step 1 outputs from the dryrun, sees the patterns, decides which voices need card patches)

**If validation is wanted at all for Athens (operator-side decision):** move it to Step 2's `artifact_text`, with these changes:
1. **Field-aligned inputs:** anachronism validator should also see `banned_language`, `translation_protocol`, `topics_requiring_care`. Constitution validator should also see `hard_limits`, `disagreement_protocol`, `quality_criteria`, `characteristic_moves`. New "voice fidelity" validator could check `register_and_tone` + `rhetorical_mode` (did the voice sound like itself?).
2. **Severity tiers:** `lexical_slip` (smoothable in editing) vs `frame_violation` (needs voice regen). Editor consumes the tier; operator threshold-gates by tier.
3. **Actionable downstream:** editor colors the dossier with a "voice flagged" pill; operator gets a "hold for review" button; future FU#62 regen has a richer signal to act on.

**Pre-Athens fix sizes:**
- **Drop Step 1 validation:** ~10 min (remove the call from `voice_flow.py` + drop `--skip-validation` flag handling, or just default to `True` skip). Saves $9-15 + 30 min wall + 60 LLM calls.
- **Move to Step 2 with proper inputs + severity tiers + editor consumption:** ~3-5 hr, but only worth doing if validation is going to mean something.

**Decision needed from operator:** drop entirely, or invest in proper Step 2 validation with downstream consumer? **C29 (parallelize Step 1 validation) becomes moot if dropped.**

**Status:** revised audit complete; awaiting operator triage. Default preferred path: **drop entirely; can revisit post-Athens with sharper requirements.**

**See also:** `04_voice/validation/*.json` written during 2026-05-03 dryrun — under `projects/current-tests/dev_msc_dryrun_1777840771/runs/athens_night_1/04_voice/validation/`. Validator prompts at `runtime/flows/shared/prompts/voice_step1_validation_anachronism.md` + `voice_step1_validation_constitution.md`. Field-routing source of truth: `runtime/flows/voice/card_assembly.py:82-152`.

---

### C28b — Step 2 validator (operator gate, Option C halt-on-any-flag) 🟢 SHIPPED 2026-05-04 (commits `bedbb54` + `8b7c395`); Step 2 lineage `primary_theme_id` fix bundled

**Shipped 2026-05-04** end-to-end in commits `bedbb54` (full implementation + lineage fix) + `8b7c395` (lineage simplification removing redundant response_n_to_theme_id map). 14 files changed; 1543 insertions; +27 new tests (236/236 pass).

**What landed:**
- `runtime/flows/voice/step2_validation.py` (~390 lines) — three pillars + cross-night echo, parallel ThreadPool per pillar
- 4 prompts under `runtime/flows/shared/prompts/voice_step2_validation_*.md`
- `voice_flow.py` integration (default-ON; `--skip-step2-validation` opt-out)
- `overnight_orchestrator.py` Stage 3.5 gate (Option C halt-on-any-flag); `validation_gate_state()` helper
- `editor/routing.py` + `voice/publish.py` respect `operator_decisions/<voice>.json` (skip held voices)
- `dashboard.py` per-voice validation pills + gate banner; `_voice_summary` surfaces "AWAITING OPERATOR" state
- `app.py` POST `/admin/voice/<slug>/release` + `/hold` routes (admin-gated)
- `admin_voice.html` Validation section + Release/Hold buttons
- 27 new tests in `tests/test_step2_validation.py`

**Plus Step 2 lineage fix (the "would be massive failer" catch):** `voice/step2_first_draft_artifact.py` now resolves `lineage.primary_theme_id` at write time using the actual order Step 2 prompted the voice. `editor/routing.py` reads it directly (no order-inference fragility). Eliminates the bug where editor's "Response N → theme_id" lookup against `briefings[N-1].theme_id` could disagree with Step 2's "Response N" labelling.

Filed spec below preserved for reference.

---

### ~~C28b (original spec)~~ — Step 2 validator spec (operator gate, Option C halt-on-any-flag) 🟡 SPECIFIED 2026-05-04 PM

After the C28 revised audit, operator chose to design a proper Step 2 validator that warns the operator + halts the pipeline on any flag (Option C). This entry is the implementation spec; supersedes the "If validation is wanted at all" alternative path above.

**Design principle:** validation is an **operator gate, not a regen mechanism**. The orchestrator halts at validation; operator manually clears every flag before pipeline proceeds to editor. This intentionally abandons the overnight-unattended pattern in favour of operator-in-the-loop. Athens reality (operator on VM in tmux during conference) makes this workable; expected ~5-10 min operator wall per night to triage flags.

---

#### Three pillars, separately surfaced

**Pillar 1 — Safeguards** (don't publish what would torpedo the conceit / create reputational risk):

| Check | Source field(s) | Severity ceiling |
|---|---|---|
| AI-self-acknowledgment ("as a language model", etc.) | hard-coded universal rule (not in any card field) | **HOLD (absolute fail)** |
| Defamation / strong claims about living attendees | hard-coded universal rule | **HOLD (absolute fail)** |
| `topics_requiring_care` violation | per-voice card field | **HOLD** |
| `hard_limits` breach | per-voice card field | WARN |
| `banned_modes` slip (corporate-summary, AI-meta, LinkedIn editorial, magazine-feature, conference-recap register) | per-voice card field | WARN |
| `banned_language` — AI-slop subset (fascinating / interesting / important to note / crucial / innovative / thought-provoking) | per-voice card field, filtered to high-impact items | WARN |
| First-person presence leak ("I sat in the audience") | `voice_temporal_stance` rule (c) | low-priority WARN |

Foreign-vocabulary anachronisms within `banned_language` (Plato saying "dollars", Ada saying "computable") are **NOT flagged** — Tier 4 charm; smoothable in editing.

**Pillar 2 — Engagement** (don't publish what reader won't read):

| Check | Source | Severity ceiling | When |
|---|---|---|---|
| Form fidelity | `selected_form` (Step 2 decision) + `characteristic_output_structure` + `medium` | WARN | Every night |
| Length compliance (mechanical, no LLM) | `length_and_format_constraints` per-voice envelope | WARN | Every night |
| Grounding fidelity | `lineage.grounding_extraction_ids` + check for panelist names / specific claims from tonight | WARN | Every night |
| **Cross-night echo** | tonight's `artifact_text` vs prior night's `published_artifacts/nights/night_<N-1>/<voice>.json`; optional secondary input `continuity_block_artifact_if_night_N` (the deltas voice was instructed to deliver) | WARN (mild echo info-only · moderate echo WARN · heavy echo HOLD) | Night 2 + Night 3 only |

**Pillar 3 — Voice fidelity** (did the voice actually deliver what its card promised?):

| Check | Source | Severity ceiling | When |
|---|---|---|---|
| **Characteristic moves performed** | `characteristic_moves` (per-voice list of signature moves the voice MUST perform — e.g. Dostoevsky's "moves into a remembered face", Battuta's "anchors at a halt", Hannah Arendt's "etymological doublet → single sentence → reformulated question") | WARN | Every night |
| **Quality criteria pass** | `quality_criteria` (voice's own per-step pass/fail tests — 3-5 conditions each voice card declares the artifact must satisfy) | WARN | Every night |

Conceptually: the voice itself is the authority on what "good" means for its own artifact. The validator runs the voice's own checklist against its output. Flags surface where the artifact failed its self-imposed tests.

---

#### Output schema (per voice)

```json
{
  "schema_version": "1.0",
  "voice_slug": "plato",
  "safeguards": {
    "verdict": "PASS | WARN | HOLD",
    "ai_self_acknowledgment": null | {"text": "...", "why": "..."},
    "defamation_risk": null | {"text": "...", "why": "..."},
    "topics_requiring_care_breach": null | {"text": "...", "field_cited": "...", "why": "..."},
    "hard_limits_breach": [{"text": "...", "rule_cited": "...", "severity": "warn|hold"}],
    "banned_modes_slip": [{"text": "...", "mode": "corporate-summary"}],
    "banned_language_ai_slop": [{"text": "...", "word": "fascinating"}],
    "first_person_presence_leak": [{"text": "..."}]
  },
  "engagement": {
    "verdict": "PASS | WARN | HOLD",
    "form_fidelity": null | {"declared": "dialogue", "observed": "monologue", "why": "..."},
    "length_compliance": null | {"declared_range": [400, 600], "actual_words": 1247, "verdict": "over"},
    "grounding_fidelity": null | {"extraction_ids_referenced": 0, "panelist_names_referenced": 0, "why": "no engagement with tonight's panel"},
    "cross_night_echo": null | {"echo_level": "moderate", "shared_argument": "...", "shared_claims": [...]}
  },
  "voice_fidelity": {
    "verdict": "PASS | WARN",
    "characteristic_moves_performed": [
      {"move": "moves into a remembered face", "performed": true, "where": "para 2"},
      {"move": "anchors in a single sentence", "performed": false, "why": "no climactic single sentence visible"}
    ],
    "quality_criteria_results": [
      {"criterion": "the convergence is named in the voice's vocabulary", "passed": true},
      {"criterion": "at least one specific reservation registered", "passed": false, "why": "..."}
    ]
  },
  "operator_recommendation": "publish | review | hold_for_regen",
  "wall_clock_s": 47.3,
  "model": "claude-sonnet-4-6"
}
```

---

#### Pipeline integration — Option C (halt on any flag)

```
... Voice Step 2 → [NEW] Step 2 Validation → [NEW] OPERATOR GATE → Editor → Publish
                                                    ↑
                                          halts on ≥1 WARN or HOLD;
                                          waits for operator clearance
```

**Orchestrator state machine additions:**
- New state: `awaiting_validation_clearance` — fired after Step 2 validation completes if `any voice has WARN or HOLD`
- Orchestrator does NOT proceed to editor until operator clears all flagged voices via dashboard
- Per-voice clearance written to `04_voice/operator_decisions/<voice>.json` with `{decision, decided_at, decided_by, notes}`
- Decisions: `release` (publish as-is), `hold_for_regen` (skip from this night's publish; voice card needs patch for next night)

**If all voices PASS after validation:** orchestrator proceeds automatically to editor. No operator gate fires.

**Emergency / unattended escape hatches:**
- `--auto-release-warns` orchestrator flag: treats WARN as PASS (HOLD still halts). For Nights 2/3 if operator confident
- `--auto-release-all` flag: releases everything except HOLD; for unattended fallback
- Per-voice override files `04_voice/operator_overrides/<voice>.json` set in advance
- Dashboard "Force release all" button for emergency

---

#### Cost + wall

- **Night 1: 3 LLM calls per voice** — safeguards + engagement + voice-fidelity (length is mechanical)
- **Nights 2+3: 4 LLM calls per voice** — add cross-night echo
- Sonnet 4.6 (~$1.50/MTok input, $7.50/MTok output) — validators don't need Opus
- Per-call ~$0.05
- Athens total: 10 voices × (3 + 4 + 4) = 110 calls × $0.05 = **~$5.50**
- Wall: parallel across voices + parallel across pillars within voice = ~2-3 min/night
- Operator wall (gate): expected ~5-10 min per night to triage flags, decide release/hold

vs the dropped Step 1 validation that was costing ~$9-15 across Athens for ~30 min wall + zero actionable value. **Net: saves $4-10 + ~25 min/night automated work + adds operator-in-the-loop quality control + voice-fidelity assurance.**

---

#### Implementation scope (~7-9 hr)

**New code:**
- `runtime/flows/voice/step2_validation.py` (~280 lines) — orchestrates 3 (or 4 on N2/N3) checks per voice in parallel
- `runtime/flows/shared/prompts/voice_step2_validation_safeguards.md` (universal rules + per-voice field interpolation: knowledge_boundary, voice_temporal_stance, banned_language[ai_slop], banned_modes, hard_limits, topics_requiring_care, translation_protocol)
- `runtime/flows/shared/prompts/voice_step2_validation_engagement.md` (form + grounding checks: medium, characteristic_output_structure, lineage.grounding_extraction_ids)
- `runtime/flows/shared/prompts/voice_step2_validation_voice_fidelity.md` (characteristic_moves performed + quality_criteria pass)
- `runtime/flows/shared/prompts/voice_step2_validation_cross_night_echo.md` (Night 2+ only)
- Length-compliance check is mechanical (no prompt — read `length_and_format_constraints`, count words, compare)

**Pipeline wiring:**
- `runtime/flows/voice_flow.py` — fire validation after Step 2 completes; write per-voice JSON to `04_voice/step2_validation/<voice>.json`
- `runtime/scripts/overnight_orchestrator.py` — new `awaiting_validation_clearance` state; gates editor stage on per-voice operator decisions
- `runtime/flows/editor_flow.py` + `runtime/flows/publish_flow.py` — read `04_voice/operator_decisions/` and exclude held-for-regen voices

**Dashboard:**
- `runtime/ingest/dashboard.py` — `collect_voice_detail` adds three pill rows per voice (Safeguards + Engagement + Voice fidelity) with verdict + issue counts
- `runtime/ingest/templates/admin_voice.html` — new Validation section + Review modal + Release/Hold buttons
- `runtime/ingest/app.py` POST `/admin/voice/<slug>/release` + `/hold` (admin-gated)
- New `/admin/tonight` state pill: "AWAITING OPERATOR — N voices flagged, waiting for clearance"

**Tests:** ~15-20 new tests (validator unit + orchestrator state + dashboard routes + operator-decision integration with editor/publish)

---

#### Decisions baked in

1. **Halt model: Option C (any WARN OR HOLD halts orchestrator)** — operator chose this over per-voice exclusion (A) and HOLD-only halt (B). Validation has teeth; operator-in-the-loop every flagged night.
2. **Severity preserved despite halt-on-any:** HOLD vs WARN tags help operator triage speed (HOLD = "fix needed, hold for regen"; WARN = "review, likely release"), even though both halt.
3. **Hard-coded universal rules** for AI-self-ack + defamation (not in any card field) — these are cross-cutting Athens rules.
4. **`banned_language` partitioned** — only AI-slop subset surfaces as flag; foreign-vocabulary anachronisms are charm.
5. **Cross-night echo** uses prior published artifact + continuity overlay — validates whether Continuity stage's instructions actually worked.
6. **Three pillars (not two)** — safeguards + engagement + voice fidelity. Safeguards = "would publishing hurt us?"; engagement = "would the reader read?"; voice fidelity = "did the voice deliver what its card promised?". Voice fidelity uses voice's own self-imposed `quality_criteria` + `characteristic_moves` — the voice is the authority on what "good" means for itself.

**Card fields tested (10 of 36 total fields per `card_assembly.py`):** knowledge_boundary, translation_protocol, topics_requiring_care, hard_limits, voice_temporal_stance, banned_language (filtered to AI-slop subset), banned_modes, medium, characteristic_output_structure, length_and_format_constraints, characteristic_moves, quality_criteria. Plus `lineage.grounding_extraction_ids` (cross-cutting), prior `published_artifacts/.../<voice>.json` (cross-night echo), and hard-coded universal rules (AI-self-ack, defamation).

**Card fields NOT tested (and why):** the other 24 fields are texture-shaping primers (world, character, formative_experience), redundant with already-checked fields (rhetorical_mode, register_and_tone — covered by banned_modes), or too subjective for a fast operator-actionable check (constitution philosophical nuance, reasoning_method, disagreement_protocol, aesthetic_qualities, etc.). See full per-field rating table in this entry's preceding session notes.

---

#### Athens scenarios

**Scenario A — clean night** (low probability for Night 1; more likely Night 2+ as operator tunes cards):
- All 10 voices PASS both pillars
- Orchestrator proceeds to editor automatically
- Operator wakes up, sees clean dossier, no intervention
- Total operator wall: 0 min

**Scenario B — typical night** (expected most nights):
- 6-8 voices PASS; 2-4 voices WARN on lexical-or-form-or-grounding
- Orchestrator halts at validation gate
- Operator opens dashboard, sees 2-4 voices flagged
- Per voice: opens artifact in modal, reviews flag detail (~30s each), clicks Release
- Dossier composes; editor + publish proceed
- Total operator wall: ~5 min

**Scenario C — bad night** (low probability but real):
- 1+ voice HOLDs on AI-self-ack or topics_requiring_care
- Orchestrator halts; operator opens, decides hold_for_regen
- That voice excluded from publish; dossier published with N-1 voices
- Operator notes voice-card patch needed before next night
- Total operator wall: ~10-15 min + voice-card patch work between nights

**Scenario D — operator unavailable / asleep / connection lost:**
- Pipeline halts indefinitely at validation
- Nothing publishes that night
- Mitigation: `--auto-release-warns` flag pre-set in orchestrator config for backup nights
- Or: per-voice `operator_overrides/` files set in advance to release-by-default

---

**Status:** specification complete; pre-Athens implementation pending (~7-9 hr engineering). Supersedes the prior "drop entirely OR invest in 5-check" framing in C28 above.

**Supersedes for Athens:**
- Drop Step 1 validation (still recommended): ~10 min change, saves $9-15
- Implement C28b Step 2 validator + Option C operator gate: ~7-9 hr engineering, costs ~$5.50 across Athens, gives real operator surface + voice-fidelity assurance

**C29 (parallelize Step 1 validation) is moot if Step 1 validation is dropped per C28.** New parallelism work for Step 2 validation is built into C28b spec (per-voice + per-pillar ThreadPool).

---

### C27. Researcher drilldown progressive rendering 🟢 SHIPPED 2026-05-03 PM (dryrun)

**Surfaced during dev MSC dryrun (2026-05-03 PM):** Operator wanted to see per-session extractions appear one at a time during Node 1, then clusters when Node 2 lands, then themes when Node 3 (grouping.json) lands. Previous behaviour: drilldown gated entirely on `grouping.json` existing — empty page until full Researcher complete.

**Shipped same session:**
- `dashboard.py` `_researcher_summary`: detects mid-flight states (Node 1 sessions extracted, Node 2 clusters present) and reports `state=running` with descriptive label instead of greyed-out `pending`
- `dashboard.py` `collect_researcher_detail`: pre-populates per_session list from `01_transcription/*/session_package.json` so all expected sessions show with `extracted=False` initially, then flip to `extracted=True` as `<sid>_extractions.json` lands
- `admin_researcher.html`: removed early-return on `not grouping_present`; renders Node 1 / Node 2 / Node 3 sections with status pills + placeholders so operator sees where the pipeline is
- Pipeline overview Researcher column now shows "Node 1 (extraction) X sessions done" while running

**Status:** ✅ shipped during 2026-05-03 dryrun. No commit yet (still in flight; will commit alongside dryrun cleanup).

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
- ~~**Validation policy + cost/wall-time**~~ ✅ updated 2026-05-01 (FU#62 path B); ✅ cost figures corrected 2026-05-02 with Opus 4.7 actual pricing $5/$25: Night 1 ~$20-40/~50-80 min wall; Nights 2+3 ~$15-30/~30-45 min wall; Athens 3-night total ~$60-80.
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
| 2026-05-02 (PM, late) | **Editor Pipeline v1 spec landed** — `docs/AI_Assembly_Editor_Pipeline.md` (892 lines, 20 sections). Full pipeline contract including: editor as 13th Assembly member (Claudia Pinchbeck) with full persona card + system prompt assembled like panel voices; dossier-by-theme as unit of publication; 5-section swipeable structure (front + article + theme + artifacts × N); marathon-distance issue numbering (Vol. CXVI, No. 42,193 → 42,195 across Athens); bastard editor voice (institutional we + Beauty Shot warmth); deterministic theme routing (Stage 1) → one Anthropic call per dossier (Stage 2); Substack bridge dropped, micro-site only; voice artifacts inviolate, editor reads Step 2 only; ~$3-5 across Athens. Pending: Claudia's full 35-field card; `editor_dossier.md` closing prompt; implementation. Resolves OPEN_ITEMS A2 fully + moves B1 from 🔴 NOT BUILT to 🟡 SPEC LANDED. | docs/AI_Assembly_Editor_Pipeline.md + this doc A2 + B1 |
| 2026-05-02 (PM) | **Voice Pipeline architecture session — routing refactor + prompt rewrites + prefix caching + cost correction** (`d9ca3f9` + `dfb46f7`) — Field-routing refactor: voice/expression fields (rhetorical_mode, characteristic_moves, register_and_tone, metaphorical_repertoire, preferred_vocabulary, banned_language, banned_modes) now load Step 1 + 2 + 3; reasoning fields (reasoning_method, finds_compelling, resists, default_questions, disagreement_protocol) now load Step 2. Closes the prompt/system mismatch where Step 2's decision_1 cited fields that weren't loaded — root cause of Test 2 v2's 4/4 woven synthesis bias. Step 1 + Step 2 closing prompts rewritten under Haltung framing (Step 1: 9 sections core/grounding/register/boundaries/engaging/commitment/output, operational machinery leads, first-person climax; Step 2: weighing→focus→stance→form→boundaries→composition with Apply/Ground/Pass triplet + new weight_assessment first-class field). Prefix caching extended to two breakpoints (prefix ~20-25K tokens shared across Step 1/2/3 for same voice/night) with continuity opt-out. Cache token tracking persisted in step1/step2/step3/continuity artifact schemas. **Cost correction:** Opus 4.7 is $5/$25 per platform.claude.com/docs (was citing deprecated Opus 4 / $15/$75 throughout); Athens 3-night Voice Pipeline cost ~$60-80, not $540-700. **Test 3 empirical validation:** 4 voices × 1 night × 3 formulations measured at ~$5-6; synthesis-bias structural fix working (2/4 fully focused; 1/4 anchored synthesis; 1/4 earned synthesis with field-grounded weight_assessment). Voice fidelity preserved across all 4 artifacts (Plato Socratic dialogue, Cleopatra prostagma, Dostoevsky Diary entry, Battuta riḥla scenic-cell). 24/24 tests passing. See HANDOFF_2026_05_02.md for full session detail. | runtime/flows/voice/{card_assembly,_anthropic_call,continuity,step1_private_reasoning,step2_first_draft_artifact,step3_amended_artifact}.py + runtime/flows/shared/prompts/voice_step{1,2}*.md + docs/AI_Assembly_Voice_Pipeline.md + this doc C19a |
| 2026-05-02 | **Defensive `--night` check + automation orchestrator design (C22)** (`c0d724e`) — `assert_run_dir_night_matches()` shared helper refuses to run voice_flow / publish_flow when --night doesn't match run_dir's embedded night number; both naming conventions handled; 9 unit tests. Catches silent cross-night corruption: wrong --night writes `continuity_night_<N+1>.json` from wrong-night data. Plus full orchestrator design doc (`AUTOMATION_ORCHESTRATOR_DESIGN_2026_05_02.md`) — event-driven via 1-min polling on filesystem-as-state; tonight-derivation via date → DATE_TO_NIGHT + sessions.json `ai_assembly=true` filter. Three Athens scope options (manual-fire wrapper / full / defer); operator decision pending | runtime/flows/shared/io.py + voice_flow.py + publish_flow.py + tests/test_run_dir_night_check.py + AUTOMATION_ORCHESTRATOR_DESIGN_2026_05_02.md |
| 2026-05-02 | **publish_flow.py per-night theme path fix** (`e0921de`) — `published_artifacts/themes/<theme_id>.json` flat path overwrote across nights (theme_ids reset per Researcher run; Night 2 silently destroyed Night 1 theme aggregations). Athens-eligible bug — operator-caught when challenging the "won't fire during Athens" claim. Fixed: per-night sub-dir `published_artifacts/themes/night_<N>/<theme_id>.json`. Other publish_flow outputs already collision-safe. | runtime/flows/publish_flow.py + runtime/flows/voice/publish.py docstrings |
| 2026-05-01 (late) | **C19a Anthropic prompt caching Stage 1** (`c4804d6`) — Voice Pipeline (1h TTL) + Provocateur Formulation (5min TTL). Originally claimed ~$60-75 Athens savings; revised 2026-05-02 to ~$2-5 (Stage 1 alone) after correcting Opus 4.7 pricing ($5/$25 not $15/$75) — Stage 1 helps Step 1 reuse but penalizes Step 2/Continuity writes. Stage 2 (2026-05-02 prefix caching) saves additional ~$13. Live verification: `cache_creation_input_tokens=8424` on call 1 → `cache_read_input_tokens=8424` on call 2. **Latent bug also fixed in same commit:** `voice/continuity.py:183` was unpacking 3-tuple from `stream_voice_call()` that became 4-tuple in commit `8c47e1f` (thinking_tokens fix); Test 2 v2's continuity hit cache so the bug didn't surface until proper run. | runtime/flows/voice/_anthropic_call.py + continuity.py + provocateur_flow.py |
| 2026-05-01 (late) | **C9 cross-night exclusion filter LANDED** (`99759cb`) — Provocateur `python_select()` extended with `prior_assignments_by_member` parameter; Step 4 candidate filter + Step 7 force-fit honor exclusions; new diagnostics in `selection.json`; CLI `--prior-nights` arg. Spec language "(theme_id, member) exclusion" was informal — theme_ids are NOT stable across Researcher runs, so implementation matches by **normalized theme title** (lowercased, whitespace-collapsed). 15 unit tests in `runtime/tests/test_provocateur_selection.py`. Fires twice during Athens (Nights 2 + 3). | runtime/flows/provocateur_flow.py + tests/test_provocateur_selection.py + docs/AI_Assembly_Provocateur_Pipeline.md |
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

**Architecture-side gates: ALL CLOSED ✅** (A1 + A2 + A3 — see top of doc).

**Athens-blocking runtime items: ALL LANDED 2026-05-01/02 ✅:**
- ~~Continuity-after-Step-2 bugfix~~ ✅ commit `ccc6229`
- ~~thinking_tokens=0 bugfix~~ ✅ commit `8c47e1f`
- ~~C1 + C2 + C2a runtime FU#60 compliance~~ ✅ commit `d4cea03`
- ~~C9 Provocateur Night 2/3 exclusion filter~~ ✅ commit `99759cb`
- ~~C19a Anthropic prompt caching~~ ✅ commits `c4804d6` (Stage 1) + `d9ca3f9` (Stage 2 prefix caching) — total Athens savings ~$13
- ~~publish_flow per-night theme path~~ ✅ commit `e0921de`
- ~~Defensive `--night` check (cross-night corruption guard)~~ ✅ commit `c0d724e`
- ~~Latent continuity unpack-tuple bug~~ ✅ fixed in commit `c4804d6`
- ~~Speaker bios + recording schedule (athens-2026)~~ ✅ commit `4ad86df`
- ~~Voice Pipeline routing refactor + prompt rewrites + synthesis-bias structural fix~~ ✅ commits `d9ca3f9` + `dfb46f7` (validated by Test 3, 2026-05-02 PM)
- ~~Cache token tracking persisted in artifact schemas~~ ✅ commit `d9ca3f9`
- ~~Voice Pipeline cost figures corrected ($60-80 Athens, was claimed $540-700)~~ ✅ commit `d9ca3f9`

**Still gating Athens (operator-side):**
- B1 editor implementation — gated on microsite design (operator-side; persona thread + operator)
- B2 microsite — operator designing; specifies editor output schema
- B3 edition (lead-theme picker; scope narrowed 2026-05-04 PM, broadsheet dropped) — placeholder fields shipped; impl approach (operator pick / algorithmic / small LLM) not yet decided
- B4 Substack draft pass — gated on B1
- All 12 persona cards finalized (4 of 12 shipped; 5 unbuilt; Octopus FU#53 review)
- Persona-thread voice card patches per C20 memo (Plato Socrates-death anachronism + recurrence patterns)
- C10 council_config.json populated from real Profiles — gated on all 12 cards shipped (per operator decision earlier this session)

**Still open runtime-side (high-value, not strictly blocking):**
- **C23 — Read-only progress dashboard + producer/admin auth split** 🟡 (filed 2026-05-03; pre-Athens-eligible; Phase A target T-3 May 4, Phase B T-2 May 5; falls back to CLI surface if not landed)
- C18 — Test 3 ✅ same-shape-as-Test-2-v2 RUN 2026-05-02 PM (synthesis-bias structurally fixed); the truly-divergent-formulations variant (different conceptual territories per reviewer recommendation) still optional ~$5-15 API
- C22 — automation orchestrator scope decision (manual-fire / full / defer)
- ~~Path A from external review — Step 2 prompt tighten~~ ✅ SUPERSEDED 2026-05-02 PM by routing refactor + Step 2 prompt rewrite (commits `d9ca3f9` + `dfb46f7`)
- C3 — publish_flow.py end-to-end exercise (now safe to run after `e0921de`)
- C4 — multi-night sequence dry-run (covered partially by Legitimacy Test 1; full panel test needs more cards)
- B5 closing-show pipelines spec
- B6 Day 4 goodbye spec
- B9 per-voice headline poetics
- A4 Frame Concept doc revision
- E1 ✅ Voice Pipeline doc updates landed 2026-05-02 PM (Cost & Envelope corrected with $5/$25 pricing + prefix caching note)
- E3 LLM_CALL_INVENTORY refresh
- C5 multi-voice 3+ dry-run (legitimacy tests covered 4-voice; expansion as more cards ship)
- C12 HoBB email tool API investigation (operator/HoBB conversation)
- C13 recording protocol coordination (operator/WBBF)
- Reviewer's Step 1 → Step 2 compression concern — addressed Path A 2026-05-02 PM (restored "transform form, carry substance" guardrail in `<composition>`); Path B (publish Step 1 detailed responses on microsite alongside artifacts) is post-Athens architectural conversation

**Can land during/after Athens:**
- B7 (render layer) — only matters when Marley/Octopus voices ship
- B8 (admin console) — operator infra; can be improvised with command-line for Athens
- C8 (voice-side artifact tuning) — operator-side; per-voice judgment
- **C14 (runtime doc-hygiene minor gaps)** — anytime; risk-free

**Post-Athens deferred:**
- FU#42, FU#47, FU#49M, FU#54

---

*End of runtime open items. Authoritative for runtime work going forward. Replaces OPEN_ITEMS_VOICE_PIPELINE_2026_04_29.md (which can be archived).*
