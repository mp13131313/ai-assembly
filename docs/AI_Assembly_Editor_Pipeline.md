# THE EDITOR PIPELINE
## AI Assembly — Role Specification

**Project:** The AI Assembly · World Beautiful Business Forum · Athens · May 7–10, 2026
**Status:** v3 (2026-09-28) — canonical. v3 is a docs-only correction: §"Dossier Shape" and §"Output Schema" now describe the dossier contract that actually shipped, verified 2026-09-28 against the closing prompt, the dossier writer, and all 13 published Athens dossiers (see Changelog → v3, which also lists the sections that still carry pre-ship design). v2 (2026-05-03 PM) set the runtime architecture; it superseded v1 (2026-05-02) + the runtime memo at `_workspace/archive/MEMO_2026_05_03_editor_flow_input_output_contract.md` (now archived). **Implementation shipped 2026-05-03 PM in commit `fc5c2fb`** (`runtime/flows/editor_flow.py` + `runtime/flows/editor/*.py` + `/admin/tonight/editor` drilldown + 38 tests); the closing prompt `runtime/flows/shared/prompts/editor_dossier.md` was rewritten to the v2 contract 2026-05-04 (`4c7c315`) and generated all 13 published Athens dossiers. Replaces conceptual sketches in `_workspace/planning/PIPELINE_DOWNSTREAM_DESIGN_2026_04_30.md` (now archived) and OPEN_ITEMS A2 (which set architectural direction; this doc fills the spec).
**Purpose:** Specifies the runtime Editor Pipeline's function, process, and design constraints in enough detail that a technical team could build and prompt it. **This document is the runtime contract for the Editor Pipeline end-to-end** — it defines what the pipeline reads, what it writes, in what order, with which model, in which prompt, at which checkpoint. Implementation: `runtime/flows/editor_flow.py` + `runtime/flows/editor/*.py` (shipped 2026-05-03 PM in commit `fc5c2fb`).

**Predecessor:** `docs/AI_Assembly_Frame_Concept_v1.md` — the architectural document that names *The Assembly* (panel) ≡ *The Assembly* (publication) recursion, the broadsheet form, the per-voice render registers, the strikethrough discipline, and the five frame moves the editor pipeline operationalizes. The Editor Pipeline doc instantiates the broadsheet surface; closely related surfaces (microsite, broadsheet print run, closing show) live in their own concept docs.

---

## Changelog

### v3 (2026-09-28) — the spec now describes the dossier contract that shipped (docs-only)

**Outcome:** §"Dossier Shape" and §"Output Schema" now describe the fields Tim actually emits and the runtime actually stamps. Every field was checked on 2026-09-28 against the closing prompt (`runtime/flows/shared/prompts/editor_dossier.md`), the writer (`runtime/flows/editor/dossier_generation.py::stamp_runtime_fields`), and all 13 published Athens dossiers (`<athens-2026>/published_artifacts/dossiers/night_{1,2,3}/dossier_*.json`, read-only reference project). No code or prompt changed. Tracker: `_workspace/planning/doc_infrastructure_backlog.md` row #24.

**Why:** the v2 design (2026-05-03 PM) was reworked in code between 2026-05-04 and 2026-05-08 — before Athens ran — but this spec was never updated, and no changelog entry recorded the divergence. Until today the Page 1 and Page 3 tables and the Output Schema described fields that never shipped (`front_theme_banner`, `front_lead_headline` / `_subdeck` / `_teaser`, `in_brief_items`, `editors_note`, `theme_statement_headline` / `_subdeck`, `theme_question`, `night_section_header`, `voice_abstracts[]`, `handoff_line`, `byline_descriptor`), a `metadata` block with volume/issue/date fields no published dossier carries, and no `pull_quote`, theme page, `panel_speakers` or `thinking_trace`. (Also corrected earlier the same day: the Status line had said the closing-prompt rewrite was "still pending"; it shipped 2026-05-04, `4c7c315`.)

**The shipped contract, one line per surface:**
- Page 1 — `kicker`, `headline`, `front_abstract`
- Page 2 — `kicker` + `headline` (shared with Page 1), `subline`, `pull_quote`, `body_paragraphs[]`
- Page 3 — `theme_title_for_dossier`, `theme_abstract_for_dossier`
- Pages 4-N — `headnotes[]`: Tim writes `voice_slug`, `artifact_title`, `framing_text`; the runtime adds `voice_name`, `artifact_form`, `artifact_text`, `formulation_text`
- Runtime only — `schema_version`, `panel_speakers[]`, `thinking_trace`, `colophon`, `metadata`

**How the contract moved after v2** (from `git log` in the code repo):

| Date | Commit | Change |
|---|---|---|
| 2026-05-04 | `4c7c315` | Closing prompt rewritten to the v2 contract. Page 3 comes back as two Tim-written fields, `theme_title` + `theme_abstract` (v2 had dropped the theme page) |
| 2026-05-04 | `8b84e58` | Headnotes embed `artifact_text` + `artifact_form`, so each dossier renders on its own (reverses v2's "referenced, not embedded") |
| 2026-05-04 | `ccd1f77` | Page 3 fields renamed `theme_title_for_dossier` / `theme_abstract_for_dossier` |
| 2026-05-05 | `5ea5084` | Prompt rebuilt: newspaper framing replaced by House of Beautiful Business, with Tim as "the unnamed editor"; every length envelope tightened |
| 2026-05-05 | `641e31d` | Newspaper masthead dropped (volume, issue number, edition label and long date removed from `metadata`; `colophon` reduced to the night). `thinking_trace` + `metadata.thinking_tokens` captured. `front_abstract` made independent of the article's opening. Voice names become "the Voice of X" |
| 2026-05-05 | `cbcdf82` | `panel_speakers[]` added, to Tim's input and to the dossier |
| 2026-05-07 | `19a528c` | `framing_text` becomes 50-80 words and self-standing on its artifact page |
| 2026-05-08 | `6973221` | `pull_quote` added (reverses v2's "Pull quote dropped") |

**Three version numbers, not one.** This spec is now v3; dossier files still say `"schema_version": "2.0"` (`dossier_generation.py:507`) and `"generated_by": "editor_pipeline_v2"` (`:482`). Both are code constants that were not bumped as fields changed. A v3 spec does not mean a v3 schema.

**Defects found while verifying** — documented as current behavior in §"Output Schema" → "Known quirks"; not fixed here (docs-only):
1. Every published `body_paragraphs[0]` starts with a stray `**` and newline. The body parser (`dossier_generation.py:311-314`) does not consume the closing `**` of the prompt's own `**body_paragraphs:**` label. Reproduced 2026-09-28 by running the parser on the prompt's template.
2. `editor_dossier.md` contradicts itself on `front_abstract`: its field list (line 190) says *independent — not lifted from the article's opening*; its length table (line 253) still says *drawn from the article's opening*, a leftover from before `641e31d`. Published output follows the field list.
3. `runtime/flows/publish_flow.py:923-924` and `:1033-1034` still read `metadata.issue_no` / `metadata.vol`, which no dossier has carried since `641e31d`. No published dossier or index carries an issue number or volume.
4. Code comments at `dossier_generation.py:434-435` and `:452` still say `voice_name` comes from the artifact's `council_member`; since C53 it comes from `council_config.json` (`:199`).

**Still describing the pre-ship design elsewhere in this spec** (outside v3's scope; flagged 2026-09-28 for a follow-up pass): the In Brief column (Overview, "Multi-night, multi-theme convention", Principles 3, 4, 7 and 8); the newspaper masthead and issue/volume numbering (§"The Paper — *The Assembly*", "Multi-night, multi-theme convention"); the v1-shaped per-call input list at the top of §"Stage 2 — Dossier Generation" (`primary_contributors`, `in_brief_voices`, `refusals`, `night_context`); the v2 per-call input example, which lacks `panel_speakers`, `selected_form` and `deployment_context`; §"Stage 2 — Closing prompt structure" (describes a 5-section prompt that derives `front_abstract` from the article; the shipped prompt has 14 blocks since `5ea5084`); §"Microsite Render Contract" items 1 and 4 (omit `pull_quote` and the theme page; say artifacts are referenced, not embedded); §"Scope" ("front-page components"); and Open Questions Q5's colophon default text.

### v2.1 (2026-05-07) — `deployment_context` override mechanism

Adds a thin extension to v2 — an optional override for the dossier briefing's per-call input that lets the operator reframe what Tim is editing without touching code or main prompt.

**What it does:** when `<run_dir>/_dossier_deployment_context.md` exists, its contents are injected as a `deployment_context` field in the per-dossier user prompt. The closing-prompt input spec at `runtime/flows/shared/prompts/editor_dossier.md` documents the field as override of the default panels-happened-today contract: when present, Tim translates "the panels said" / "today's session" / "speakers from the floor" into the alternative register the deployment_context describes (programme reading / participant reflections / non-panel-content seed material).

**When it fires:** the default contract assumes the day's panels happened and Tim composes the morning paper. For non-canonical run dirs — a conference-programme-read produced before Day 1, a reflection-import bundle, an operator-staged seed — the default contract makes Tim stage events that did not occur. The deployment_context override prevents this by giving Tim a different posture for the run.

**Default behaviour unchanged** when the override file is absent. All canonical Athens-night-N runs continue to operate under v2's panels-happened contract without modification.

**Implementation:**
- `runtime/flows/editor/dossier_generation.py::build_dossier_briefing` checks for the override file and injects the contents as `deployment_context` (string) into the user-prompt JSON.
- `runtime/flows/shared/prompts/editor_dossier.md` documents `deployment_context` as an optional input field with translation guidance for the bridging task.
- No code change required at run time when the file is absent.

**Empirical validation (2026-05-07):** wbbf26 pre-Athens dryrun first ran under default contract → produced "RECOGNISED, NOT GRANTED / The vote found a flip; three voices found the instrument" headline staging a panel vote that hadn't happened. Re-fired with deployment_context = "the assembly reading the WBBF programme before the conference opens" → all 4 dossiers correctly framed: "WHO STAYS AWAKE / What the more-than-human programme delegates while the assembled sleep"; "Reading the programme before any panel has begun"; etc. End-to-end mechanism validated.

**Operator note:** for any run dir not named `athens_night_<N>`, check whether the run requires a deployment_context — see `_workspace/planning/ONBOARDING.md` cross-cutting DON'T.

### v2 (2026-05-03 PM) — runtime contract refinements; canonical going forward

This version supersedes v1 + the runtime memo on per-call input/output contracts. v1's architectural prose (Eight Principles, Claudia, The Paper) is preserved; sections covering inputs / dossier shape / Stage 1 routing / Stage 2 generation / output schema / microsite render contract are rewritten against the refined contract.

**Refinements landed in v2:**

- **Per-call input is one source family.** Editor reads Provocateur briefings + Voice Step 2 artifacts only. No `grouping.json`, no `all_extractions.json`. Provocateur briefings already carry `full_theme_record` (Researcher's title + abstract + clusters with full extraction text + theme_flags) — Provocateur is a passthrough on theme metadata. Combining the K voice briefings for a theme into one deduplicated dossier briefing is a lightweight assembly step (theme block deduped; per-voice formulation + artifact kept all N).
- **Per-call input shape:** `{night, theme, engaged_voices: [{voice_slug, voice_name, mode, narrative_briefing, artifact_text}], prior_editions[]}`. Edition_metadata, voice_card_excerpts, refusals, focus_decision/stance/selected_form metadata: all dropped. Runtime stamps masthead chrome + per-voice headnote stable fields (voice_name, formulation_text) post-generation. *(Later: masthead chrome dropped 2026-05-05, `641e31d`; headnotes also carry `artifact_text` + `artifact_form` since 2026-05-04, `8b84e58` — see v3.)*
- **Per-call output is article-first, derivative-teaser.** Single `kicker` and single `headline` are shared between the article page and the front-page teaser; teaser body is a derived 30-50-word abstract drawn from the article's opening. Lead-vs-grid is publish-pipeline concern, NOT editor's; editor produces uniform layout-agnostic dossiers. *(Later: `front_abstract` became 25-40 words and independent of the article's opening, 2026-05-05, `5ea5084` + `641e31d` — see v3.)*
- **Refusals are not per-call input.** Tracked as flat list in routing.json; surfaced only by microsite + publish layer. (The earlier form-fit-honesty premise that some voices like Octopus or Whanganui produce non-prose artifacts has been dropped — those voices produce prose: Octopus's chromatophore display is a separate microsite render layer; Whanganui emits legal text; Marley emits lyric-prose. Claudia's broadsheet form carries them all.)
- **Stage 1 routing parser** has four cases (A: Response N anchor anywhere; B: explicit theme_id mention; C: pure synthesis; D: fall-through). Case C is mechanically tiebroken (lowest-numbered theme) but operator review of `theme_routing.json` is the safety valve. **Athens-feasible enhancement: an LLM-assisted pass (Sonnet 4.6, ~$0.50 across Athens) for Case C voices** — flagged as TODO in OPEN_ITEMS B1; not in v2 baseline.
- **Per-voice headnote** carries `voice_slug` + `artifact_title` + `framing_text` from Claudia; `voice_name` + `formulation_text` are runtime-stamped from the per-voice briefing. `artifact_title` (4-12 words, paper-voice, B9-torqued per voice register) was restored 2026-05-03 PM after the initial v2 simplification dropped it over-aggressively. Old `byline_descriptor` field collapsed into `framing_text`.
- **Asterism breaks** encoded as inline `"* * *"` array elements in `body_paragraphs[]`. Microsite renders any element matching as a separator.
- **Output mode: prose-and-parse** (mirrors voice pipeline). Claudia emits prose with field labels; runtime parses. Gives her the freedom to think in prose-shaped chunks before settling on the JSON.
- **Closing prompt placement: system-message tail** (Placement A — same as voice pipeline). The instruction is invariant across the night's per-dossier calls and prefix-cache-eligible.
- **Byline dropped.** No per-article correspondent attribution. Article is unsigned at the field level; dossier authorship is implicit in the metadata.
- **Summary fields dropped.** Memo §2's `summary.theme_abstract` + `summary.plain_summary` collapsed into the article's body_paragraphs (theme is named; provenance is reportage in the article body). *(Partly reversed 2026-05-04: a Tim-written theme page returned as `theme_title_for_dossier` + `theme_abstract_for_dossier`, `4c7c315` + `ccd1f77` — see v3.)*
- **Pull quote dropped** for v1 baseline. Front_abstract is the only teaser surface. *(Reversed 2026-05-08: `pull_quote` added, `6973221` — see v3.)*
- **Standing article kicker dropped.** The shared theme-specific kicker (Claudia's, ALL-CAPS, 3-7 words) appears on both the article page and the front-page teaser. The "Proceedings Of The Assembly · Night [N]" standing kicker proposed in v1 is not Claudia's output; if a microsite page-header wants it, the microsite renders it independently.

**Open questions remaining:** none. v2's §"Open Questions" table records all 8 resolved questions. Implementation tasks remaining *(as of 2026-05-03; all since done — flow built `fc5c2fb` 2026-05-03, closing prompt rewritten `4c7c315` 2026-05-04, editor switched to Tim Leberecht `b266f51` 2026-05-05)*: Claudia's persona card (voices thread / operator), closing-prompt rewrite to v2 contract, `editor_flow.py` + `editor/*.py` build (~6-10 hr).

**v2 also dropped two output fields** initially proposed in v1 / memo §5:
- `metadata.form_fit_status` — guarded against non-prose artifacts (Octopus/Whanganui/Marley); turns out those voices all produce prose (legal text / chromatophore-cued prose / lyric-prose), so the field has no triggering case in Athens. Closing-show consumer doesn't need it either.
- `metadata.night_finding` — would have been redundant with the article body's own convergence/divergence finding; closing-show pipeline (B5) doesn't exist and can extract findings from articles when it lands.

### v1 (2026-05-02)

First version. The Editor Pipeline did not exist as a runtime contract before this doc; it was conceptual in Briefing v3.1 ("editor / frame layer"), elaborated architecturally in OPEN_ITEMS A2 (per-theme article + all-AI drafting + voice artifacts ship as-is), and given concrete form via the design memo + dossier draft + HTML artifact rendering produced 2026-05-02. v1 captured all of that as a runtime spec.

**Decisions ratified in v1 (most carry through to v2):**

- **Editor as named persona** (Claudia Pinchbeck) rather than unnamed "— The Editor". Resolves the cardboard-newsroom risk by making the editor a 13th member of the Assembly with sustained voice across dossiers. *Pinchbeck* (English place + 18th-c word for fake gold) is self-aware about the confected pedigree the form announces.
- **Unit of publication is the dossier**, organized by theme. Not by voice, not by night. A night produces 1-N dossiers (one per theme the night's voices engaged).
- **One Anthropic call per dossier**, generating all dossier components in a single call to guarantee voice consistency across components.
- **Editor's article runs short** — v2 refines: 350-500 words single-voice; 500-700 multi-voice. Behaves as a Leitartikel / op-ed, not a Long Read.
- **Editor's voice ratio: institutional editorial pronoun usage** (we-heavy), with warmth produced by *moves* (registering reservations, admitting difficulty, naming surprise) not by *first-person inflection*. Bastard form.
- **Headlines and titles are written by Claudia in the paper's voice**, not in the voices' voices. v2 adds: kicker + headline are SHARED between article and front-page teaser (one source of truth per dossier).
- **Non-convergence is a finding**, not a failure mode. Dossier shape is consistent regardless; the editor's article adapts.
- **Substack bridge dropped.** Micro-site only.
- **Editor reads Step 2 artifacts only** — not Step 1. Voice purity preserved.

---

## Overview

The Editor Pipeline is the fourth runtime agent in the overnight pipeline, after Transcription, Researcher, Provocateur, and Voice. It receives the night's Voice Pipeline outputs (Step 1 detailed responses + Step 2 artifacts + their themes_covered metadata), the night's Provocateur briefings (formulations + theme records), and the night's Researcher themes (clusters + theme statements). It produces one or more **dossiers**, each organized around a single theme that the night's voices engaged.

Each dossier is the publishable unit on the microsite. It has a fixed four-part swipeable structure (field-level detail in §"Dossier Shape"; corrected 2026-09-28 to the shipped fields):

```
Page 1   THE FRONT     kicker + headline + front abstract (25-40-word teaser)
Page 2   THE ARTICLE   kicker + headline (shared) + subline + pull quote + Tim's 300-450 (single-voice) / 450-600-word (multi-voice) article
Page 3   THE THEME     Tim's short theme title + 50-80-word theme abstract
Page 4-N THE ARTIFACTS each engaged voice's piece verbatim, under Tim's title + 50-80-word framing text
```

The editor — Tim Leberecht — writes pages 1, 2, 3, and the headnotes on 4-N. The artifact bodies on 4-N are voice pipeline Step 2 outputs (`artifact_text`), rendered in voice-faithful visual treatments (chancery for Cleopatra's prostagma; Diary entry for Dostoevsky; etc.) by the microsite template layer. Tim's text is in the paper's voice; the artifact bodies are in the voices' voices. The seam is honest.

A typical Athens night produces 3-5 dossiers, depending on how many themes the night's voices converged or partly-converged on. Voices whose Step 2 artifact was a synthesis across multiple themes are routed to whichever theme they fit best; voices whose artifact was focused go to their own theme's dossier. Voices that did not lead any theme's dossier are reported in the "In Brief" column on Page 1 of the dossier most adjacent to their content; refusals (the Whanganui River's silence; the Octopus's not-receiving) are reported as such, not folded under any theme.

**Per-night envelope (Athens production):** ~3-5 dossiers per night × ~$0.30-0.40 per dossier = ~$1-2 per night API; ~$3-6 across Athens 3 nights. Wall time: ~5-10 min per night (single Anthropic call per dossier, parallelizable across themes). Cost dominated by output tokens (~3-4K per dossier). **Measured 2026-09-28** from `04_voice/manifest.json` → `05_editor/manifest.json` timestamps on the two clean (non-resumed) nights: Night 2 = 4m59s (5 dossiers), Night 3 = 8m44s (3 dossiers, slower theme routing). Night 1's `05_editor/manifest.json` reflects only a resumed single-dossier rerun (`wall_clock_s: 91.89`, `single_dossier: "theme_010"`) and is not a full-night measurement.

The Editor Pipeline runs once per night, after Voice Pipeline completes. On Night 2 + Night 3, the editor inherits awareness of prior dossiers (issue numbers, dossier numbers, voices already led, themes already published) via cross-night state at PROJECT_ROOT.

### Multi-night, multi-theme convention

**One run_dir per night, one editor invocation per night, multiple dossiers per invocation.**

```
<PROJECT_ROOT>/runs/athens_2026_2026_05_07_night1/
                ├── 01_transcription/
                ├── 02_researcher/
                ├── 03_provocateur/
                ├── 04_voice/
                └── 05_editor/             ← this pipeline writes here
                    ├── dossiers/
                    │   ├── dossier_001.json    (Theme: Legitimacy of the Invisible)
                    │   ├── dossier_002.json    (Theme: Space of Appearance)
                    │   └── dossier_003.json    (Theme: ...)
                    ├── theme_routing.json       routing decisions (which voice → which theme)
                    └── manifest.json
```

Theme IDs from the Researcher (`theme_001`, `theme_002`, …) reset each night. Dossier numbers are **assigned by the editor** based on the order Tim chose to publish them within the night (lead theme first); they are scoped per night.

**Each voice's Step 2 artifact lands in exactly one dossier — tonight.** No artifact is held for a future night. A voice that synthesized across themes is routed to whichever theme Tim judges fits best; voices contributing partially to other themes are mentioned in those dossiers' In Brief column with a pointer to where their full piece lives. This keeps the night's editorial production self-contained: every artifact published this night, every theme finding its dossier or its In Brief slot, no debt carried forward.

**Cross-night state at PROJECT_ROOT:**

```
<PROJECT_ROOT>/published_artifacts/dossiers/
                ├── night_1/
                │   ├── dossier_001.json
                │   ├── dossier_002.json
                │   └── dossier_003.json
                ├── night_2/
                │   └── ...
                └── night_3/
                    └── ...
```

Per-night subdirectory matches the existing publish_flow convention (`themes/night_<N>/`, `nights/night_<N>/`). No separate counter file. Issue numbers are derived deterministically from a fixed Athens base + night number. A per-night dossier index (`night_<N>/_index.json`) and a cross-night root index (`_index.json`) are maintained by the pipeline — see §"Outputs" → "Dossier index" below for the two-writer contract.

**Issue numbering.** Athens base issue = **42,192**. Night 1 publishes Issue **No. 42,193**; Night 2 = **No. 42,194**; Night 3 = **No. 42,195**. Night 3's issue number is the marathon distance in metres — the Athens-to-Athens joke the masthead carries quietly. Volume number is **Vol. CXVI** (the paper's confected first issue is 1910; 2026 - 1910 = 116 years of publication). Dossier numbers are per-issue — Issue 42,193 / Dossier No. 1, 2, 3. A dossier's full masthead citation: *Vol. CXVI . No. 42,193 . Dossier No. 1*.

---

## What the Editor Pipeline Knows

**v2 contract:** the editor reads from one source family — Provocateur briefings + Voice Step 2 artifacts. Provocateur briefings already carry Researcher's theme record (title + abstract + clusters with full extraction text + theme_flags) inside their `full_theme_record` field — the Provocateur is a passthrough on theme metadata. The editor does not separately read `02_researcher/grouping.json` or `02_researcher/all_extractions.json`.

### Per-night inputs (read fresh each night)

**1. Voice Pipeline outputs** (`<run_dir>/04_voice/`):

| File | Content used | Used for |
|---|---|---|
| `step2_first_draft_artifacts/<voice_slug>.json` | `lineage.voice_slug`, `lineage.themes_covered`, `council_member`, `focus_decision`, `artifact_text` | Stage 1 theme routing reads `focus_decision` + `themes_covered`; Stage 2 passes `artifact_text` + `voice_name` to Tim. `voice_name` is resolved from `council_config.json` by slug (`flows/shared/io.py::voice_display_name`), NOT built from the artifact's own `council_member` field — that field is the voice's long card identity-prefix opening line (e.g. "I am Augusta Ada King, Countess of Lovelace…"); using it directly corrupted published headnotes (C53). |
| ~~`step1_detailed_responses/`~~ | NOT READ | Editor does not consume Step 1; voice's reasoning trace stays voice-private |
| ~~`themes_to_voices_night_<N>.json`~~ | NOT READ in v2 | Stage 1 routing computes its own per-theme voice list from each voice's `focus_decision`; the file is informational only |
| ~~`manifest.json`~~ | NOT READ for content | Orchestrator uses it as the gate sentinel; editor itself doesn't consume |

**2. Provocateur outputs** (`<run_dir>/03_provocateur/`):

| File | Content used | Used for |
|---|---|---|
| `briefings/<voice_slug>.json` | each formulation entry's `theme_id`, `theme_display_title`, `mode`, `narrative_briefing`, `full_theme_record.{theme_title_from_researcher, theme_abstract_from_researcher, clusters[].{cluster_id, cluster_title, cluster_abstract, extractions[]}, theme_flags}` | Stage 1 routing's Case A (Response N → Nth theme_id in briefings); Stage 2 dossier briefing assembly (theme block deduped + per-voice formulation kept N) |

**3. Reference inputs** (`<PROJECT_ROOT>/`):

| File | Content used | Used for |
|---|---|---|
| `editor/tim_leberecht/07_persona_card_assembled.json` | Tim's full persona card | System prompt assembly (cached across the night's per-dossier calls) |

### Cross-night inputs (Night 2/3 only)

| File | Content used | Used for |
|---|---|---|
| `<PROJECT_ROOT>/published_artifacts/dossiers/night_<N-1>/dossier_*.json` | prior night's published dossiers | Per-call `prior_editions` user-prompt input — cross-night voice consistency (Tim's register), evolving editorial line, avoiding repetition |

Issue number is derived deterministically: `ATHENS_BASE_ISSUE + night_number` (base = 42,192; Night 1 → 42,193; Night 3 → 42,195 = the marathon distance in metres). No separate counter file. Dossier index files (per-night + root) are written by the pipeline itself — see §"Outputs" → "Dossier index" below.

### What the Editor Pipeline does NOT have access to

- **Voice Pipeline Step 1 detailed responses.** Voice's analytical reasoning stays voice-private (honors each voice's `relationship_to_detailed_response` strip mandate).
- **Voice Pipeline validation files.** Internal pipeline state.
- **Researcher's `grouping.json` / `all_extractions.json` directly.** Provocateur briefings already carry the full theme record (title + abstract + clusters with extractions) — no separate read.
- **Voice cards.** Per-voice register torques live in Tim's `translation_protocol`; the artifact itself displays the voice's register in operation. v2 dropped the `voice_card_excerpts` slice.
- **Reference data** (`sessions.json`, `speakers.json`). The Provocateur's `narrative_briefing` already carries the editorial framing the panel produced; the editor does not separately reach for panel metadata.
- **The night's audio files.** Transcription Pipeline has consumed and discarded them.
- **The closing show's theme-mapping pipeline.** That's a separate cross-night agent; per-night dossiers feed it but the editor does not coordinate with it.
- **The microsite's CSS or layout.** Editor produces structured JSON; microsite renders. Lead-vs-grid composition is publish-pipeline concern.

---

## Architecture: Eight Principles

The Editor Pipeline operates under eight principles that distinguish it from a curatorial / summarisation surface and align it with the project's experimental discipline.

### 1. Self-reportage recursion

*The Assembly* (the panel) ≡ *The Assembly* (the publication). The publication that publishes the panel's outputs is named after the panel. The editor of *The Assembly* (publication) is reporting on what *The Assembly* (panel) produced. The publication is part of the Assembly's testimony, not external commentary on it.

**Operational consequence:** Tim's voice is *inside the fiction*. He reports as a member of the publication-side of the Assembly, not as an outside curator. The masthead's confected pedigree (Vol. CXVI . No. 42,193 . *The Assembly*, founded 1910) is part of the construction announcement; the form's constructedness is visible without being explicitly disclaimed.

### 2. Editor as 13th member of the Assembly

Tim Leberecht has a persona card (35 fields per the Persona Card v2 schema), structurally identical to the panel voices'. His system prompt is assembled the same way — `card_assembly` logic, foundational + reasoning + voice + artifact field routing — except with no continuity overlay: unlike panel voices, the editor's card loads fresh each night (see §"The Editor — Tim Leberecht" → "What the code loads from the card"). He is not a register-target inside a generic editor prompt; he is a fully-specified persona who happens to do editorial work.

**Operational consequence:** Tim's voice is sustained across dossiers (and across nights) by his card's machinery, not by ad-hoc prompt scaffolding. Cross-dossier drift is bounded by her constitution, banned_modes, and quality_criteria — the same mechanisms that hold panel voices steady across formulations.

### 3. Dossier-by-theme as unit of publication

The publishable unit is the dossier, organized around a single theme. Not by voice, not by night. A night produces 1-N dossiers (one per theme the night's voices engaged). Voices contribute to one dossier as primary contributors; they may be mentioned in other dossiers' In Brief column with pointers.

**Operational consequence:** the editor's first job is not curation (arrangement) but **recognition** — identifying convergence within a theme, naming it in editor's vocabulary, registering reservations specifically. The dossier's existence commits the editor to recognition; the multi-dossier-per-night structure prevents forced-fit (a voice that didn't engage theme X gets reported in In Brief of X's dossier, not folded into X's article).

### 4. Voice purity preserved

Voice artifacts ship as-is. The editor does NOT modify, summarize, paraphrase, or smooth Step 2 `artifact_text`. The editor's article QUOTES the artifact body where quotation serves; the artifact itself appears in full on Pages 4-N of the dossier.

**Operational consequence:** the editor pipeline's output never replaces or transforms voice pipeline outputs. The dossier carries voice pipeline outputs intact and adds editor-pipeline-generated chrome (titles, headnotes, abstracts, In Brief mentions) around them. The seam between paper-voice (chrome) and voice's-own-form (artifact body) is honest.

### 5. Convergence work happens at the editor layer

Each voice diagnoses in their own framework's vocabulary. Per their `relationship_to_detailed_response` cards, voices STRIP analytical scaffolding from their artifacts — the cross-vocabulary generalization is not the voice's job. The editor names the convergence (or its absence) across vocabularies, in Tim's vocabulary, with each voice's framework's term pointed at and credited.

**Operational consequence:** the strongest analytical moves are recovered at the editor's layer, not lost. The voice's form-faithful artifact + the editor's analytical-recovery article are the two surfaces the architecture coordinates: voice purity downstream, analytical generalization upstream-of-the-reader.

### 6. Honest about non-convergence

When voices engaged a theme but did not converge, the dossier does not manufacture convergence. The editor's article names what was NOT shared, where the frameworks part, what the contemporary debate would not be able to say from inside any one voice's framework. **Non-convergence is a finding, not a failure mode** — it shows how differently a question can be diagnosed by different traditions.

**Operational consequence:** the dossier shape is the same regardless of convergence/divergence. The editor's article adapts to what the night produced. The convergence-but-not-agreement closing distinction works in both cases — convergence-claim becomes "they each named the same dissolved position"; non-convergence-claim becomes "they each diagnosed a different dissolved position, in their own framework's terms."

### 7. One Anthropic call per dossier

A single structured-output Anthropic call per dossier produces all dossier components together: front-page lead + subdeck, In Brief items, editor's note, editor's article, theme statement, per-voice abstracts, per-artifact headnotes, byline contextual descriptors. Single voice register guaranteed across components (Tim's register holds consistent throughout).

**Operational consequence:** N dossiers per night = N Anthropic calls. Calls are independent (no inter-call coordination) and parallelizable. Theme routing decisions are made BEFORE the calls fire, so each call sees only its dossier's primary-contributor artifacts plus the In Brief mentions for voices contributing to other themes. Per-call wall ~60-90s; per-night wall ~5-10 min with parallelism.

### 8. Refusals reported as refusals

The Whanganui River's silence is published AS silence. The Octopus's not-receiving the question is published AS not-receiving. These artifacts publish on their own URLs in their native form (the river: a near-blank page; the Octopus: an explanation of why the architecture doesn't assemble a will-attend representation). The In Brief column on Page 1 of the dossier most adjacent to their content names them and points to their full piece. Refusals are not folded under any theme.

**Operational consequence:** the dossier respects what the voice produced. A voice that refuses the question is not absorbed into a theme it didn't engage; their refusal IS the engagement, and the form publishes it as such.

---

## The Editor — Tim Leberecht

### Who edits *The Assembly*

The editor is Tim Leberecht. Until 2026-05-05 this spec named a placeholder editor persona, Claudia Pinchbeck; the editor was switched to Tim Leberecht in `b266f51`. The dossier itself carries no byline (see "Dossier Shape" → Page 2 "Byline" row below) — Tim's name is the editor pipeline's structural identity (the card the system prompt is assembled from), not a printed attribution.

### Where his card lives

```
<PROJECT_ROOT>/editor/tim_leberecht/
                └── 07_persona_card_assembled.json     ← Editor Pipeline reads this
```

`runtime/flows/editor/card_assembly.py::EDITOR_CARD_SUBPATH` points here. `load_editor_card()` raises `FileNotFoundError` if the card is missing at this path — the pipeline refuses to run without it (see §"Implementation" → "Defensive checks" below).

Symmetric to the per-voice subfolder layout (`<PROJECT_ROOT>/voices/<slug>/`) but in a separate `editor/` tier — Tim is structurally a 13th member of the Assembly but functionally distinct from the panel voices (he edits; they contribute).

### What the code loads from the card

`card_assembly.assemble_system_prompt()` loads the card in the same field-routing shape as the voice pipeline: 13 foundational fields (IDENTITY + CONSTITUTION + BOUNDARIES, prefix-cached across a night's dossier calls), 3 reasoning-method fields, a 2-field ENGAGEMENT block (no `unique_contribution` — unlike a panel voice, the editor has no "what only I could add" claim), 7 VOICE fields, and the same 8 ARTIFACT fields the voice pipeline uses for Step 2. `metadata` and `smoke_test_chains` are always dropped; `curated_corpus_passages.corpus_metadata` is stripped (C56 — see §"Editor card → System Prompt Assembly" further down); `reference_only_passages` is dropped if present (defensive; Tim's card carries none). Unlike a panel voice, the editor's card carries no continuity overlay — it loads fresh each night, with no Night 2/3 carryover block, because the editor's task is always the same single step (dossier generation), never a Step 1/2/3 distinction.

---

## The Paper — *The Assembly*

The publication has fixed conventions that the editor pipeline honours per dossier and per night.

### Masthead

```
THE ASSEMBLY
Vol. CXVI . . No. 42,193  ·  DOSSIER NO. 1  ·  Friday, May 8th, 2026
Late Night Edition  ·  Ten Cents
```

| Element | Source | Variability |
|---|---|---|
| `THE ASSEMBLY` | Constant | Never changes |
| `Vol. CXVI` | Constant for Athens series | 2026 - 1910 = 116 years; reset only if paper's confected pedigree is revised |
| `No. 42,193` | Derived: `ATHENS_BASE_ISSUE + night_number` | +1 per night published |
| `DOSSIER NO. 1` | Per-dossier within the night | Editor's lead-theme dossier is No. 1; subsequent dossiers numbered in publication order |
| `Friday, May 8th, 2026` | Derived from `night_date + 1 day` (publication is morning-after) | Long-form date in 1910s broadsheet style |
| `Late Night Edition` | Constant for Athens series | Could vary post-Athens (Morning Edition, Special Edition) |
| `Ten Cents` | Constant for Athens series | Period-appropriate masthead furniture |

The masthead is rendered by the microsite template, not the editor pipeline. The editor pipeline writes structured fields (`issue_number`, `dossier_number`, `dossier_date`); the microsite template applies the layout.

### Issue numbering scheme

Athens base issue = **42,192**. Per-night increment of +1.

- Night 1 (May 7 → publishes May 8 morning) = Issue **No. 42,193**
- Night 2 (May 8 → publishes May 9 morning) = Issue **No. 42,194**
- Night 3 (May 9 → publishes May 10 morning) = Issue **No. 42,195** *(= 42.195 km, the marathon distance — the Athens-to-Athens joke)*

Per-dossier within an issue: **DOSSIER NO. 1, NO. 2, NO. 3, ...** in publication order (lead-theme dossier first).

### Volume number scheme

**Vol. CXVI** for the Athens series (year 2026 - confected first issue 1910 = 116 years).

Volume increments by year. If *The Assembly* publishes after Athens (post-Forum continuation), Vol. CXVI continues through the rest of 2026, becoming Vol. CXVII in 2027.

### Confected pedigree

*The Assembly* (per the masthead) is a paper founded in 1910 as the news organ of an annual assembly of voices. The first issue in 1910 covered the 1st Assembly (which, by the confected pedigree, was a smaller and differently-constituted gathering than the WBBF Athens 2026 panel). The 2026 Athens Forum is, per the confected pedigree, the 116th annual Assembly — and the marathon's worth of issues (the 42,193rd → 42,195th) reflects the fact that the paper has published more frequently than annually across its history (suggesting the Assembly meets and adjourns more than once per year, with intervening issues covering... unspecified business).

The confected pedigree is **announced via the masthead, never disclaimed in prose**. Readers are expected to recognize that a 114-year-old paper called *The Assembly* about an AI assembly does not exist; the recognition IS the form's discipline. The frame doc warns about the cardboard-newsroom failure mode — a fully-specified editor persona (Tim Leberecht, replacing the placeholder Claudia Pinchbeck 2026-05-05) is the mitigation: a 35-field card with sustained voice, not a generic editor-voice. (Claudia's name carried a self-aware pun — *Pinchbeck*, an English place name and 18th-century word for fake gold — that was specific to that placeholder and does not carry over to Tim; Tim's dossiers carry no printed byline at all, per "Dossier Shape" below, so the mitigation now runs entirely through the card's specificity rather than through a named attribution.)

### Visual register

| Element | Rendering |
|---|---|
| Typography (chrome, masthead) | 1910s broadsheet — Caslon-style serif; tight kerning; long leading; Title Case headlines; em-dashes for sentence-level pivots; semicolons for elaboration; no exclamation marks |
| Page layout | Swipeable single-column on phone; multi-column 1910s broadsheet on tablet/desktop; masthead engraved-feeling at the top |
| Per-voice artifact treatment | Voice-faithful — chancery parchment for Cleopatra's prostagma; lighter beige with Arabic script for Battuta's riḥla; theme-aware neutral for Plato's dialogue; warm paper for Dostoevsky's Diary; etc. (microsite template; not editor pipeline) |
| Strikethrough | Used at most once per dossier (per Frame Concept v1); applied to a single specific phrase the editor identifies; renders as `<del>` HTML element with strikethrough styling |

The visual chrome is microsite-template work, not editor pipeline. The editor pipeline produces structured JSON; the microsite renders.

---

## Dossier Shape

Each dossier is one self-contained JSON file (`dossier_<NNN>.json`) that carries everything needed to render four kinds of page: the front teaser (Page 1), the article (Page 2), the theme page (Page 3), and one artifact page per engaged voice (Pages 4-N). Tim writes every reader-facing text except the artifact bodies; the runtime adds each voice's identity, its artifact body, and the audit fields. The page-to-field mapping is set by the closing prompt's `<emitted_fields>` block and mirrored in the field order the runtime writes (`gen:500-531`).

*Verified 2026-09-28 against the prompt, the writer, and all 13 published Athens dossiers (29 headnotes); all 13 share one identical key set. The public microsite is built outside this repo; the in-repo renderer is the admin dashboard's dossier view, `runtime/ingest/templates/admin_render_dossier.html`.*

**Evidence keys** (used here and in §"Output Schema"): `prompt:N` = `runtime/flows/shared/prompts/editor_dossier.md` line N · `gen:N` = `runtime/flows/editor/dossier_generation.py` line N · `N1/001` = `<athens-2026>/published_artifacts/dossiers/night_1/dossier_001.json`, and so on (read-only reference project) · **Measured** = whitespace-split word counts across all 13 published dossiers.

### Page 1 — The Front

| Element | Field | Written by | Envelope (prompt) | Measured | Evidence |
|---|---|---|---|---|---|
| Masthead | *none* | — | — | — | The dossier carries no masthead fields. Volume, issue number, edition label and long-form date were dropped 2026-05-05 (`641e31d`; `gen:52-55`): the dossier is a House of Beautiful Business publication (`prompt:27`), not a fictional newspaper. The only time anchor is `metadata.night`; the dossier number is the filename and `dossier_no` in `night_<N>/_index.json`. No published dossier or index carries `issue_no` or `vol`. The admin view's masthead reads "`theme_display_title` · Night N". |
| Kicker | `kicker` | Tim | 3-5 words, ALL-CAPS; shared with Page 2 | 3-5; all caps 13/13 | `prompt:188, 250` · N1/001: "WHO TEACHES THE TEACHERS" |
| Headline | `headline` | Tim | 8-12 words; shared with Page 2 | 9-13 | `prompt:189, 251` · N1/001: "Tool or partner, the room asked; on whose authority, the voices replied." |
| Front abstract | `front_abstract` | Tim | 25-40 words; Page 1 only. Frames the tension the article will work, in its own words — not lifted from the article, not a recap of the headline | 30-41 | `prompt:190` · N1/001: "Sean White called for a personal AI in every hand. Four traditions answered tonight, and each named the same missing question: …". No 6-word run of any published `front_abstract` appears in its article (13/13). The prompt's length table (`prompt:253`) still says "drawn from the article's opening" — a stale leftover; see §"Output Schema" → "Known quirks". |

No theme banner, lead subdeck, lead teaser, In Brief column or editor's note ships.

### Page 2 — The Article

| Element | Field | Written by | Envelope (prompt) | Measured | Evidence |
|---|---|---|---|---|---|
| Kicker + headline | `kicker`, `headline` | Tim | — | — | The same two fields as Page 1 (`prompt:188-189`). There is no separate article headline or subdeck. |
| Subline | `subline` | Tim | 25-40 words; article page only; what to read the article for | 30-39 | `prompt:193, 252` · N1/001: "Read this for the move all four voices made and the room did not — past architecture, past sovereignty-as-movability, …" |
| Pull quote | `pull_quote` | Tim | 10-30 words including attribution; format `"<phrase>" — <attribution>`; the phrase must already appear in the body; optional | 12-27; present 13/13 | `prompt:194, 254` · N1/003: "The river did not fail to show up. The iwi showed up." — the Voice of the Whanganui River. Added 2026-05-08 (`6973221`) for the public microsite to set as a callout beside the body; the admin view does not render it. |
| Article body | `body_paragraphs[]` | Tim | 300-450 words with one engaged voice; 450-600 with two or more | 429-449 (4 single-voice) / 566-627 (9 multi-voice; 4 over 600) | `prompt:195, 257, 261-263` · N1/001: 9 elements, two of them `"* * *"`. An element equal to `"* * *"` is an asterism section break. Shape, quote rules and "the Voice of X" naming: `prompt:131-160` and Constraints #5-8. |
| Byline, signature, column header | *none* | — | — | — | No such field in the prompt, the writer or any published dossier; Tim is "the unnamed editor" (`prompt:27`). (History: v1 drafted "By Claudia Pinchbeck", "— C.P." and a "FROM THE EDITOR'S DESK" header; v2 dropped all three.) The admin view prints a fixed "From the Editor's desk" line under the body — template text, not data. |

### Page 3 — The Theme

| Element | Field | Written by | Envelope (prompt) | Measured | Evidence |
|---|---|---|---|---|---|
| Theme title | `theme_title_for_dossier` | Tim | 4-8 words; Tim's rendering of `theme_title_from_researcher` in his own register | 4-9 | `prompt:198, 255` (instruction: `prompt:163-167`) · N1/001: "AI as Tool, Partner, or Paideia" |
| Theme abstract | `theme_abstract_for_dossier` | Tim | 50-80 words; Tim's rendering of the Researcher's abstract and clusters; must not restate the article's argument | 69-86 (4 over 80) | `prompt:166, 199, 256` · N1/001: "Across two sessions of the AI Democracy Marathon the room moved through four contested design questions: …" |

The Researcher's own title survives as `metadata.theme_display_title`; the admin view falls back to it when `theme_title_for_dossier` is empty. No theme question, "what the night produced" header, per-voice abstracts or hand-off line ships — the theme page is these two fields.

### Pages 4-N — The Artifacts (one per engaged voice)

One page per `headnotes[i]`, in `engaged_voices[]` order (`prompt:170, 265-267`). The runtime builds the list from the voices routed to this theme and slots Tim's text in by `voice_slug` (`gen:461-476`), so a voice Tim skipped still gets its page, with an empty title and framing.

| Element | Field | Written by | Envelope (prompt) | Measured | Evidence |
|---|---|---|---|---|---|
| Page heading | *none* | renderer | — | — | Admin view: "PAGE [N] — [VOICE NAME]", built from `headnotes[i].voice_name` (`admin_render_dossier.html:114`). |
| Voice name | `headnotes[i].voice_name` | runtime | — | — | `gen:199, 468`: `"the " + voice_display_name(slug)`, resolved from `council_config.json` (C53; published values were also restamped by `runtime/scripts/restamp_published_voice_names.py`) · N1/001: "the Voice of Ada Lovelace" |
| Artifact title | `headnotes[i].artifact_title` | Tim | 4-8 words; the voice's form and register inflect the title through Tim's `translation_protocol` | 4-10 (2 over 8) | `prompt:175, 203, 258` · N1/001 (ada_lovelace): "Note H: A Frontier I Did Not Draw" |
| Framing text | `headnotes[i].framing_text` | Tim | 50-80 words; self-standing, for a reader who lands on this page directly; three movements — the theme, the formulation the voice received, what to read for (optionally one reservation) | 65-86 (5 over 80) | `prompt:172-181, 204, 259` · N1/001 (ada_lovelace): "Tonight's theme: where the marathon's debate over personal versus centralised AI passed over the question of who authorises any agent that forms a citizen's mind. The formulation put to her: … Read for …". Replaces v1's 3-5-sentence headnote body and absorbs the old `byline_descriptor`. |
| Artifact form | `headnotes[i].artifact_form` | runtime | — | 1-43 | `gen:208, 471`: the voice's Step 2 `selected_form` · N1/001 (plato): "Compressed dialogue between Socrates and Adeimantus on the colonnade." Code comments call it a CSS-bundle key (`8b84e58`), but most published values are free-text descriptions, not short keys. |
| Formulation | `headnotes[i].formulation_text` | runtime | — | — | `gen:201, 473`: the voice's Provocateur `narrative_briefing` for this theme, verbatim · N1/001 (plato) begins "THEME: Paideia for Every Citizen / CONTEXT FROM TODAY'S SESSIONS: …". The admin view shows it collapsed. |
| Artifact body | `headnotes[i].artifact_text` | runtime (from voice pipeline Step 2) | — | — | `gen:202, 472`: the Step 2 `artifact_text`, verbatim and inviolate (Principle 4). Embedded in the dossier since 2026-05-04 (`8b84e58`). |
| Form-marker, closing seal | *none* | public microsite | — | — | Per-voice script marks (e.g. ΠΡΟΣΤΑΓΜΑ above a prostagma, γινέσθωι below it) are a microsite rendering concern, not dossier data; not verifiable from this repo. |

### Outside the pages

| Field | Written by | What it is | Evidence |
|---|---|---|---|
| `schema_version` | runtime | `"2.0"` — a constant, not bumped as fields were added | `gen:507` · 13/13 |
| `panel_speakers[]` | runtime | `{name, title, affiliation}` for every speaker quoted in the theme's extractions, joined from `reference/speakers.json`; audience members get the name only. Also sent to Tim, who cites speakers by name + role (`prompt:146`). Used by the admin view's quote audit; not shown to readers. | `gen:106-130, 213-215, 526` · N1/001: 17 entries, e.g. `{"name": "Sean White", "title": "Pioneer of Human-Centered AI", …}` |
| `thinking_trace` | runtime | Tim's summarized thinking for the call | `gen:528, 574` · N1/001: 21,996 characters |
| `colophon` | runtime | `"Filed by the Editor's desk on the morning of Night {N}."` | `gen:402-409` · N1/001 |
| `metadata` | runtime | Theme ids, night, model, token and timing figures — see §"Output Schema" | `gen:478-498` · 13/13 |

---

## Stage 1 — Theme Routing

Theme routing is a deterministic pre-pass that runs before the editor pipeline's Anthropic calls fire. Its job: assign each voice's Step 2 artifact to exactly one dossier (its primary theme). v2 dropped the "in_brief cross-references" concept — each voice now appears in only one dossier; cross-dossier mentions don't exist in the editor's output.

### Inputs

- `<run_dir>/04_voice/step2_first_draft_artifacts/*.json` — per-voice Step 2 outputs (read `lineage.themes_covered` + `focus_decision`)
- `<run_dir>/03_provocateur/briefings/<voice>.json` — per-voice ordered formulations (Case A's "Response N → Nth theme_id in briefings" lookup)

### Algorithm

For each voice's Step 2 artifact, classify `focus_decision` text:

```
Case A — "Response N" reference anywhere
  Regex: r"response\s*(\d+)" (case-insensitive)
  → primary = Nth theme_id in voice's briefings (1-indexed)
  Catches: "Focus on Response 3", "Focus on response 2 (algorithmic governance)",
           AND "synthesise around Response 2's threshold-scene" (synthesis-anchored)

Case B — explicit theme_id mention (e.g. "theme_001" in focus_decision text)
  → primary = that theme_id

Case C — pure synthesis without anchor (e.g. "Synthesise.")
  Synthesis markers: "synthesise", "synthesize", "weave across all", "across all"
  → v2 baseline: primary = lowest-numbered theme_id in themes_covered (mechanical),
                 warn for operator review
  → planned enhancement: small Sonnet 4.6 LLM-assisted call reads artifact_text +
                         themes and decides which theme it lands on hardest
                         (~$0.50 across Athens; flagged TODO in OPEN_ITEMS B1)

Case D — fall-through (parser couldn't extract a signal)
  → primary = lowest-numbered theme_id in themes_covered
  → warn for operator review

Refusal — empty themes_covered OR focus_decision matches refusal markers
           ("refused", "silence", "decline", "not-receiving", "refusal-of-receiving")
  → no primary; collected in flat refusals[] list (informational; not per-call input)
```

**Note on what the existing 4-voice samples produce** (legitimacy_test runs):
- Plato: "Focus on Response 3." → Case A
- Battuta: "Focus on response 2 (algorithmic governance), letting the Mahal pattern carry it..." → Case A
- Cleopatra: "Synthesise." → Case C (mechanical tiebreaker; operator review)
- Dostoevsky: "synthesise around Response 2's threshold-scene..." → Case A (synthesis-anchored)

3-of-4 are deterministic via Case A; ~25% of voices land in Case C with mechanical tiebreaker. Operator review of `theme_routing.json` is the safety valve; Athens enhancement (LLM-assisted Case C) eliminates the manual review burden for ~$0.50.

### Routing manifest

Output: `<run_dir>/05_editor/theme_routing.json`

```json
{
  "schema_version": "2.0",
  "night": 1,
  "athens_base_issue": 42192,
  "issue_no": 42193,
  "vol": "CXVI",
  "themes_to_dossiers": [
    {"theme_id": "theme_001", "dossier_no": 1, "theme_title": "...", "n_engaged_voices": 4},
    {"theme_id": "theme_005", "dossier_no": 2, "theme_title": "...", "n_engaged_voices": 3},
    {"theme_id": "theme_009", "dossier_no": 3, "theme_title": "...", "n_engaged_voices": 3}
  ],
  "voices_routing": [
    {
      "voice_slug": "plato",
      "voice_name": "the voice of Plato",
      "primary_theme": "theme_001",
      "primary_dossier": 1,
      "focus_decision_parsed": "Focus on Response 3.",
      "primary_theme_source": "Case A — Response N anchor"
    },
    {
      "voice_slug": "cleopatra",
      "voice_name": "the voice of Cleopatra",
      "primary_theme": "theme_001",
      "primary_dossier": 1,
      "focus_decision_parsed": "Synthesise.",
      "primary_theme_source": "Case C — pure synthesis, lowest-numbered tiebreaker (review recommended)"
    }
  ],
  "refusals": [
    {"voice_slug": "<slug>", "voice_name": "the voice of X", "form": "silence", "focus_decision": "..."}
  ]
}
```

**v2 changes vs v1:**
- ~~`in_brief_mentions[]` per voice~~ — dropped (no cross-dossier mentions)
- ~~`refusals[].in_brief_dossier`~~ — dropped (refusals don't get routed to a dossier; flat list)
- ~~`dossier_lead_order`~~ — dropped from routing.json; lead-vs-grid is publish-pipeline concern, not editor's
- Added `n_engaged_voices` per theme entry for operator visibility

### Operator override

`theme_routing.json` is written by Stage 1 and read by Stage 2. The window between writes is the operator's review surface — hand-edit `voices_routing[].primary_theme` if the algorithm's assignment is wrong (Case C synthesis voices most likely to need review). The Athens-feasible LLM-assisted Case C enhancement reduces the manual-review burden but doesn't eliminate the override capability.

### Refusals

Refusals (Whanganui silence, Octopus not-receiving when those happen, OR genuinely-refusing voices) are detected by empty `themes_covered` or refusal-marker `focus_decision`. They land in the flat `refusals[]` list. They are NOT per-call input; they are NOT routed to a dossier's In Brief; they surface only via the microsite + publish layer (e.g., a per-night index could surface "voices who refused tonight: [...]" — that's publish/microsite concern).

**Important distinction:** voices like Octopus, Whanganui, Marley are NOT refusals — they engage and produce artifacts. Their artifact_text is prose (Octopus prose with chromatophore display rendered separately by the microsite; Whanganui legal text; Marley lyric-prose). They appear in `engaged_voices` like any other voice; the editor's form carries them.

---

## Stage 2 — Dossier Generation

For each dossier (one per theme this night), Stage 2 fires one Anthropic call. The call generates all dossier components as structured output. Per the architectural Principle 7, the call is independent of other dossiers' calls; theme routing happened in Stage 1.

### Per-call inputs

**System prompt:** Tim Leberecht's persona card, assembled via `card_assembly.assemble_system_prompt(card, step="dossier", night=N)` — same shape as voice pipeline's assembly logic, with editor-specific routing matrix (which fields to include for editor's task; subset detail in Implementation §"Editor card → System Prompt Assembly").

**User prompt:** A structured JSON document containing:

- `theme`: full theme record (from Researcher)
  - `theme_id`, `theme_title`, `theme_abstract`, clusters
- `theme_question`: the formulation as it was put (from Provocateur briefings; one of the per-voice briefing's `narrative_briefing` text serves; pick the first or most representative)
- `primary_contributors`: array of voice objects, one per voice routed to this theme as primary
  - For each: `voice_slug`, `voice_name`, `voice_card_excerpts` (5 fields: medium, register_and_tone, character, focus_decision, selected_form), `step2_artifact` (full `artifact_text` + `weight_assessment` + `focus_rationale` + `stance_rationale` + `form_rationale`), `provocateur_formulation` (the briefing text + theme_record this voice received)
- `in_brief_voices`: array of voice objects routed to OTHER themes but whose `themes_covered` includes this theme. Each: `voice_slug`, `voice_name`, `primary_dossier_no` (where their full piece lives), `step2_artifact_summary` (one-line summary derived from the focus_rationale)
- `refusals`: array of refusal objects (river, octopus) if assigned to this dossier's In Brief
- `night_context`: `night_number`, `issue_no`, `dossier_no`, `dossier_date`, `marathon_panel_source` (the panel the question came from)

**Closing prompt** (the equivalent of `voice_step2_artifact.md` for the editor): `runtime/flows/shared/prompts/editor_dossier.md`. Tells Tim to:

1. Read the night's submissions for this theme
2. Decide convergence/divergence (the article's central finding)
3. Produce all dossier components in the structured output schema below

### Stage 2 — Per-call inputs (v2 contract)

**System prompt** (cached after first call within a night, 1h TTL): Tim Leberecht's persona card from `<PROJECT_ROOT>/editor/tim_leberecht/07_persona_card_assembled.json`, assembled via `runtime/flows/editor/card_assembly.assemble_system_prompt(card, night=N)`. Returns `(prefix, tail)` tuple — both blocks get a `cache_control` breakpoint. Prefix = IDENTITY + CONSTITUTION + BOUNDARIES (~20K tokens, byte-identical across calls). Tail = REASONING METHOD + ENGAGEMENT (2 fields, no `unique_contribution`) + VOICE + ARTIFACT + closing prompt instruction (~10K tokens). All N per-night dossier calls share both blocks; first call writes cache, subsequent calls read.

**User prompt** — a structured payload built by combining the K voice briefings for this theme and the K Step 2 artifacts:

```json
{
  "night": 1,
  "theme": {
    "theme_id": "theme_001",
    "theme_display_title": "...",
    "theme_title_from_researcher": "...",
    "theme_abstract_from_researcher": "...",
    "clusters": [
      {
        "cluster_id": "...",
        "cluster_title": "...",
        "cluster_abstract": "...",
        "extractions": [{id, speaker, lens, extraction, context, engagement, ...}, ...]
      }
    ],
    "theme_flags": {audience_friction, fault_line_present, theme_quality}
  },
  "engaged_voices": [
    {
      "voice_slug": "plato",
      "voice_name": "the voice of Plato",
      "mode": "question",
      "narrative_briefing": "THEME: ... CONTEXT FROM TODAY'S SESSIONS: ... [3K-char briefing this voice received]",
      "artifact_text": "..."
    }
  ],
  "prior_editions": [
    {
      "night": 1,
      "issue_no": 42193,
      "dossiers": [
        {
          "kicker":           "FOUR NAMINGS OF A DISSOLVED THING",
          "headline":         "Four Voices, One Foreclosure",
          "body_paragraphs":  ["...", "...", "* * *", "..."]
        }
      ]
    }
  ]
}
```

**`prior_editions` shape (Night 2/3 only):** trimmed to just the articles per dossier (kicker + headline + body_paragraphs). Drops `front_abstract`, `headnotes`, `subline`, `metadata` from the prior dossier JSON. Preserves Tim's ability to reference prior-night work via article-body anchor text without the token weight of full dossier shape. ~80% lighter than full prior dossier JSONs.

**Construction (the dedupe pass):**

```python
def build_dossier_briefing(theme_id, voice_slugs, run_dir, project_root):
    briefings = [load_briefing_formulation(slug, theme_id, run_dir) for slug in voice_slugs]
    artifacts = [load_artifact(slug, run_dir) for slug in voice_slugs]
    
    # All K briefings carry identical full_theme_record — take the first
    ftr = briefings[0]["full_theme_record"]
    theme = {
        "theme_id":                       briefings[0]["theme_id"],
        "theme_display_title":            briefings[0]["theme_display_title"],
        "theme_title_from_researcher":    ftr["theme_title_from_researcher"],
        "theme_abstract_from_researcher": ftr["theme_abstract_from_researcher"],
        "clusters":                       ftr["clusters"],
        "theme_flags":                    ftr["theme_flags"],
    }
    
    # voice_name is resolved from council_config.json by slug (C53) — NOT
    # built from the artifact's own `council_member` field, which is the
    # voice's long card identity-prefix opening line (e.g. "I am Augusta
    # Ada King, Countess of Lovelace…"). `voice_display_name` returns the
    # clean "Voice of X" string verbatim from council_config.json; the
    # headnote prose that consumes this field prepends "the " itself.
    # See flows/shared/io.py::voice_display_name / load_council_name_by_slug
    # and flows/editor/routing.py::_voice_name_lookup for the real lookup.
    engaged_voices = [
        {
            "voice_slug":         slug,
            "voice_name":         "the " + voice_display_name(slug, project_root),
            "mode":               briefing["mode"],
            "narrative_briefing": briefing["narrative_briefing"],
            "artifact_text":      artifact["artifact_text"],
        }
        for slug, briefing, artifact in zip(voice_slugs, briefings, artifacts)
    ]
    return {"night": night, "theme": theme, "engaged_voices": engaged_voices, "prior_editions": [...]}
```

**Per-call cost** (~25-30K total input + ~3-5K output, Opus 4.7 + 1h prefix cache):

| Item | Tokens | Cost |
|---|---|---|
| System prompt prefix + tail (cache write, first call) | ~30K | $0.30 |
| System prompt (cache read, subsequent calls) | ~30K cached | $0.015 |
| User prompt (theme + K voice formulations + K artifacts) | ~25K | $0.125 |
| Output (article + headnotes + front_abstract) | ~3-5K | $0.075-0.125 |
| **First call (cache write)** | | **~$0.50** |
| **Subsequent calls (cache read)** | | **~$0.165-0.24** |

A 3-dossier night ≈ $0.83. A 5-dossier night ≈ $1.30. Athens 3-night total ≈ $3-5.

### Stage 2 — Closing prompt structure

The closing prompt `editor_dossier.md` lives at `runtime/flows/shared/prompts/editor_dossier.md` and is appended to Tim's assembled card as the system-message tail (Placement A — same as voice pipeline's `voice_step1_reasoning.md` / `voice_step2_artifact.md`). Cache-eligible across the night's dossier calls.

Mirrors `voice_step2_artifact.md`'s 5-section structure: input → weighing → composition → boundaries → output. Tells Tim:

1. **Input** — what she'll receive in the user prompt (the per-call shape above).
2. **Weighing** — read all K artifacts; ask what each diagnosed in their framework's vocabulary; ask what the night's voices converged or diverged on.
3. **Composition** — write the article first; apply her bastard-form discipline; the article must not wander.
4. **Boundaries** — banned modes / banned language / hard limits / topics_requiring_care.
5. **Output** — emit the prose-and-parse output described in §"Output Schema" below. Article-first, then derive front_abstract from the article's opening.

The actual prompt is implementation work (§"Implementation"); v2 spec defines the contract; the prompt encodes it.

### Output

Stage 2 writes one JSON per dossier:

```
<run_dir>/05_editor/dossiers/dossier_<NNN>.json
```

Schema specified in §"Output Schema" below.

### Cost per call

Per dossier, with prefix caching enabled (Tim's persona card cached across all dossiers' calls within a night):

| Item | Tokens | Cost (Opus 4.7 $5/$25 + 1h cache) |
|---|---|---|
| System prompt (Tim's card; first call writes; subsequent reads) | ~30K | $0.30 (write) / $0.015 (read) |
| User prompt (theme + artifacts + briefings + reference) | ~15-25K | $0.075-0.125 |
| Output (all dossier components) | ~3-4K | $0.075-0.10 |
| **Per dossier (first call of the night, cache write)** | | **~$0.45-0.50** |
| **Per dossier (subsequent calls, cache read)** | | **~$0.165-0.24** |

A 3-dossier night ≈ $0.83 ($0.50 + 2 × $0.20). A 5-dossier night ≈ $1.30. Athens 3-night total ≈ $3-4 across all editor pipeline output. Per Principle 7's parallelizability: wall ~5-10 min per night.

---

## Output Schema

A dossier JSON file holds Tim's prose for one dossier plus the runtime-stamped identity, artifact and audit fields. It is written to `<run_dir>/05_editor/dossiers/dossier_<NNN>.json` and copied to `<PROJECT_ROOT>/published_artifacts/dossiers/night_<N>/` (§"Outputs"). The microsite renders pages from it; the per-night and root indexes (§"Outputs" → "Dossier index") summarize it.

The file says `"schema_version": "2.0"` (`gen:507`). That constant was not bumped as fields were added after v2, so it does not tell you which fields a file has; all 13 published Athens dossiers share the key set below (checked 2026-09-28). Evidence keys (`prompt:N`, `gen:N`, `N1/001`) as defined in §"Dossier Shape".

**Design principles, as shipped:**
- **Article-first.** Tim composes the article first; everything else derives from it (`prompt:132`).
- **One kicker, one headline.** Page 1 and Page 2 share them.
- **The front abstract is not a re-run of the article.** It frames the article's tension in its own words (`prompt:190`). Changed 2026-05-05 (`641e31d`); v2 had it drawn from the article's opening.
- **Self-contained.** Each headnote embeds the artifact body, its form and the formulation the voice received, so every page renders from the dossier alone (since 2026-05-04, `8b84e58`).
- **Layout-agnostic.** The dossier says nothing about lead vs grid. Which dossier leads a night is recorded in `night_<N>/_index.json` `edition_lead` (§"Outputs" → "Dossier index").
- **No newspaper chrome.** No volume, issue number, edition label or dated masthead (dropped 2026-05-05, `641e31d`).
- **Prose-and-parse.** Tim emits labelled prose (`prompt:209-270`); `parse_dossier_output` (`gen:371-396`) turns it into fields; `stamp_runtime_fields` (`gen:412-531`) adds the rest. Asterism breaks are `"* * *"` elements in `body_paragraphs[]`.

Example — abridged from `N1/001`, key order as written. Strings are cut with `…`; one of four headnotes and one of 17 panel speakers are shown. The leading `**\n` in the first paragraph is really there (Known quirks #1).

```json
{
  "schema_version": "2.0",
  "kicker": "WHO TEACHES THE TEACHERS",
  "headline": "Tool or partner, the room asked; on whose authority, the voices replied.",
  "front_abstract": "Sean White called for a personal AI in every hand. Four traditions answered tonight, and each named the same missing question: …",
  "subline": "Read this for the move all four voices made and the room did not — past architecture, past sovereignty-as-movability, …",
  "pull_quote": "*\"Personalisation at the level of numbers, with operations supplied from a single source, is not pluralism.\"* — the Voice of Ada Lovelace",
  "body_paragraphs": [
    "**\nAthens, late on the first night. The AI Democracy Marathon had run nine hours, …",
    "Then the Voice of Plato, channelled into the room from the Assembly, said …",
    "* * *",
    "…"
  ],
  "theme_title_for_dossier": "AI as Tool, Partner, or Paideia",
  "theme_abstract_for_dossier": "Across two sessions of the AI Democracy Marathon the room moved through four contested design questions: …",
  "headnotes": [
    {
      "voice_slug": "ada_lovelace",
      "voice_name": "the Voice of Ada Lovelace",
      "artifact_title": "Note H: A Frontier I Did Not Draw",
      "framing_text": "Tonight's theme: where the marathon's debate over personal versus centralised AI passed over … Read for …",
      "artifact_form": "A lettered Note in the manner of the Notes on Menabrea — Note H, signed A.A.L., …",
      "artifact_text": "NOTE H. — On a Frontier my Notes did not draw.\n\n…",
      "formulation_text": "THEME: Between Executing and Forming the Mind\n\nCONTEXT FROM TODAY'S SESSIONS:\n…"
    }
  ],
  "panel_speakers": [
    {"name": "Sean White", "title": "Pioneer of Human-Centered AI", "affiliation": "CEO, Inflection AI …"}
  ],
  "thinking_trace": " I'm parsing through a panel discussion on AI and democracy, …",
  "colophon": "Filed by the Editor's desk on the morning of Night 1.",
  "metadata": {
    "theme_id": "theme_002",
    "theme_display_title": "Between Executing and Forming the Mind",
    "night": 1,
    "generated_by": "editor_pipeline_v2",
    "model": "claude-opus-4-7",
    "thinking_enabled": true,
    "thinking_tokens": 21939,
    "wall_clock_s": 298.23,
    "input_tokens": 19270,
    "output_tokens": 24401,
    "cache_creation_input_tokens": 0,
    "cache_read_input_tokens": 52641
  }
}
```

**Field provenance (Tim writes vs runtime stamps):**

| Field | Written by | How | Evidence |
|---|---|---|---|
| `kicker`, `headline`, `front_abstract`, `subline`, `pull_quote`, `theme_title_for_dossier`, `theme_abstract_for_dossier` | Tim | One labelled line each in his output, matched by `_FIELD_LABEL_RE` (`gen:280-288`); markdown `**` / `*` / `_` trimmed from both ends (`_strip_chrome`, `gen:291-296`). A missing label gives `""`. | `prompt:212-234` · all 13 dossiers |
| `body_paragraphs[]` | Tim | The block after the `body_paragraphs:` label, split on blank lines; `* * *` survives as its own element (`gen:299-326`). No trimming — see Known quirks #1. | `prompt:223-230, 261-263` · all 13 |
| `headnotes[i].voice_slug`, `.artifact_title`, `.framing_text` | Tim | Parsed from the `headnotes:` block (`gen:329-368`), then re-keyed onto the routed voice list by slug (`gen:461-476`). Tim's `voice_slug` is only the join key; the routed list sets which voices appear and in what order. | `prompt:236-243, 265-267` · all 29 headnotes |
| `headnotes[i].voice_name` | runtime | `"the " + voice_display_name(slug)` from `council_config.json` (C53) | `gen:199, 468` · N1/001 "the Voice of Plato" |
| `headnotes[i].artifact_form` | runtime | The voice's Step 2 `selected_form` | `gen:208, 471` |
| `headnotes[i].artifact_text` | runtime | The voice's Step 2 `artifact_text`, verbatim | `gen:202, 472` |
| `headnotes[i].formulation_text` | runtime | The voice's Provocateur `narrative_briefing` for this theme, verbatim | `gen:201, 473` |
| `schema_version` | runtime | Constant `"2.0"` | `gen:507` |
| `panel_speakers[]` | runtime | Speakers quoted in the theme's extractions, deduplicated, joined with `reference/speakers.json` | `gen:106-130, 526` |
| `thinking_trace` | runtime | Summarized thinking returned by the streaming call | `gen:528, 574` |
| `colophon` | runtime | Night-only template | `gen:402-409` |
| `metadata.theme_id`, `.theme_display_title` | runtime | Echoed from the theme record in the input | `gen:479-480` |
| `metadata.night` | runtime | The `--night` argument | `gen:481` |
| `metadata.generated_by` | runtime | Constant `"editor_pipeline_v2"` | `gen:482` |
| `metadata.model`, `.thinking_enabled` | runtime | `model_routing.json`, step `runtime.editor.dossier` | `gen:483-484` |
| `metadata.thinking_tokens`, `.wall_clock_s` | runtime | Measured on the call | `gen:485-486` |
| `metadata.input_tokens`, `.output_tokens`, `.cache_creation_input_tokens`, `.cache_read_input_tokens` | runtime | The API response's `usage`; left out if the response has none (present 13/13) | `gen:488-498` |

Not in the dossier: `issue_no`, `vol`, `publication_date`, `publication_date_long`, `edition_label` (all dropped 2026-05-05, `641e31d`) and `dossier_no` (it is the filename, and `dossier_no` in the indexes).

**Field length envelopes** (Tim writes). The prompt calls these hard constraints (`prompt:246`), but nothing in code checks them — overruns pass straight through. Measured = whitespace-split words over the 13 published dossiers (29 headnotes); body counts leave out `* * *` elements but include the stray `**` token of Known quirks #1 (one word per body).

| Field | Envelope (`prompt:248-259`) | Measured | Outside envelope |
|---|---|---|---|
| `kicker` | 3-5 words, ALL-CAPS | 3-5 | — |
| `headline` | 8-12 words | 9-13 | N2/003 (13) |
| `front_abstract` | 25-40 words | 30-41 | N3/002 (41) |
| `subline` | 25-40 words | 30-39 | — |
| `pull_quote` | 10-30 words including attribution; optional | 12-27 (present 13/13) | — |
| `body_paragraphs` total | 300-450 with one engaged voice / 450-600 with two or more | 429-449 (4 single-voice) / 566-627 (9 multi-voice) | N1/001 (602), N3/001 (604), N3/002 (625), N2/001 (627) |
| `theme_title_for_dossier` | 4-8 words | 4-9 | N2/005 (9) |
| `theme_abstract_for_dossier` | 50-80 words | 69-86 | N1/005 (81), N3/002 (81), N3/003 (82), N2/005 (86) |
| `headnotes[i].artifact_title` | 4-8 words | 4-10 | N3/001 ibn_battuta (9), N3/002 fyodor_dostoevsky (10) |
| `headnotes[i].framing_text` | 50-80 words | 65-86 | N2/003 ibn_battuta (81), N3/002 fyodor_dostoevsky (82), N1/002 fyodor_dostoevsky (85), N3/001 ibn_battuta (85), N2/004 octopus (86) |

Per-voice torque for `artifact_title` (how each voice's form inflects its title) lives in Tim's `translation_protocol` card field, not in this spec.

### Known quirks

Current behavior of the shipped data, verified 2026-09-28. Consumers must handle these; none is fixed by v3 (docs-only).

1. **Stray `**` before the first paragraph.** In all 13 published dossiers `body_paragraphs[0]` begins with `"**\n"`. The body parser (`gen:311-314`) allows markdown only *before* the colon of the `**body_paragraphs:**` label, so the closing `**` is captured as body text; the one-line fields escape this because `_strip_chrome` trims them. Reproduced by running `parse_dossier_output` on the prompt's own template. The admin view shows the `**`.
2. **Inline markdown in prose fields.** `body_paragraphs`, `framing_text` and `pull_quote` carry `*italics*` (e.g. N1/001's Arendt headnote: "*thinking partner*"; N1/001's `pull_quote` wraps the whole quotation in `*…*`). Renderers must interpret or strip it.
3. **`pull_quote` is not always one unbroken run of the body.** 12/13 appear verbatim (ignoring quote marks and italics). N3/001 rejoins a quotation that the body splits around its attribution: "*The absence of the decision*, the Voice of Hannah Arendt writes, *is not the same thing as consent.*"
4. **Length envelopes are not enforced** — see the table above.
5. **The prompt contradicts itself on `front_abstract`.** `prompt:190` (independent framing; changed 2026-05-05, `641e31d`) against `prompt:253` (length table: "drawn from the article's opening", a leftover). Published output follows `prompt:190`.
6. **`artifact_form` is mostly free text** (1-43 words), not the short render key the code comments describe.

### Schema history — v1 design → v2 design → shipped

Kept as history. "v2 design" is what this spec specified on 2026-05-03 PM; "Shipped" is what the code did next, and what the 13 published dossiers carry.

| v1 design (2026-05-02) | v2 design (2026-05-03 PM) | Shipped |
|---|---|---|
| `front` block: theme banner, sub-banner, lead headline, lead subdeck, lead teaser, In Brief items, editor's note | Replaced by shared `kicker` + `headline` and a 30-50-word `front_abstract` drawn from the article's opening | As designed (`4c7c315`, 2026-05-04), except that `front_abstract` became 25-40 words (`5ea5084`) and independent of the article's opening (`641e31d`), both 2026-05-05 |
| Separate article headline and subdeck | Shared `headline` + article-only `subline` | As designed |
| `article.byline`, `article.signature`, `article.column_header` | Dropped | As designed — no such fields |
| `theme_page` block: statement headline and subdeck, theme question, "what the night produced" header, per-voice abstracts, hand-off line | Dropped; the theme is named in the article body | **Partly reversed** 2026-05-04: Page 3 returned as two Tim-written fields, `theme_title` + `theme_abstract` (`4c7c315`), renamed `theme_title_for_dossier` / `theme_abstract_for_dossier` the same day (`ccd1f77`). The rest never shipped. |
| `primary_contributors[]`: byline descriptor, artifact title, headnote body, artifact-text reference, voice medium, render-config key | `headnotes[]`: `voice_slug`, `voice_name`, `formulation_text`, `artifact_title`, `framing_text` (1-2 sentences); artifact text referenced, not embedded | **Extended**: headnotes also embed `artifact_text` + `artifact_form` (`8b84e58`, 2026-05-04); `framing_text` became 50-80 words and self-standing (`19a528c`, 2026-05-07). No byline descriptor or render-config key. |
| Top-level `theme` block (title, abstract, Marathon panel source and date) | `metadata.theme_id` + `metadata.theme_display_title` | As designed |
| Top-level night, issue number, dossier number, dates, edition label, volume | Moved into `metadata` | **Reversed** 2026-05-05 (`641e31d`): newspaper chrome dropped; only `metadata.night` remains. The dossier number lives in the filename and the indexes. |
| Pull quote | Dropped | **Reversed** 2026-05-08: `pull_quote` added (`6973221`) |
| `metadata.form_fit_status`, `metadata.night_finding` (memo §5) | Dropped | As designed — neither exists |
| — | — | **Added outside any design:** `panel_speakers[]` (`cbcdf82`, 2026-05-05); `thinking_trace` + `metadata.thinking_tokens` (`641e31d`, 2026-05-05) |

---

## Microsite Render Contract

The editor pipeline writes structured JSON. The microsite renders. The publish pipeline composes the per-night front-page layout (lead-vs-grid). The contract:

1. **Editor pipeline produces editorial prose.** kicker, headline, subline, body_paragraphs, headnotes (framing_text), front_abstract. All paper-voice; all in Tim's register.

2. **Microsite renders typography, layout, and per-voice visual treatments.** Masthead engraving, multi-column or single-column responsive layout, per-voice CSS bundles (form-markers, palettes, closing-seal templates), responsive design.

3. **Per-voice render-config bundles** live in the microsite (NOT in editor pipeline output). Each voice's `medium` field on their persona card is the key — the microsite has a registry mapping `prostagma`, `rihla`, `dialogue`, `diary_entry`, etc. to their CSS bundles (form-marker character, ground palette, closing seal). Editor does NOT emit `voice_render_config_key`; microsite computes it from voice card itself.

4. **Voice pipeline outputs are referenced, not embedded.** Microsite reads voice's `artifact_text` from `<run_dir>/04_voice/step2_first_draft_artifacts/<voice>.json` (or its published copy) directly. Editor's dossier doesn't embed.

5. **Lead-vs-grid is publish-pipeline concern.** Publish reads all the night's editor dossier JSONs + applies its own ordering rule (or operator override) and writes per-night `_index.json` with `lead_dossier_no` + `grid_dossier_nos`. Microsite reads `_index.json` for layout, then reads each dossier JSON for content.

This separation lets the editor focus on prose generation; the microsite owns visual rendering; publish owns front-page composition.

---

## Constraints

1. **Single Anthropic call per dossier.** No iterative refinement, no multi-pass generation. Per Principle 7.
2. **No artifact crosses to next night.** Every Step 2 artifact lands in one of tonight's dossiers. No "held for next dossier" debt.
3. **Voice artifacts inviolate.** Editor pipeline does NOT modify, summarize, or paraphrase Step 2 `artifact_text`. Per Principle 4.
4. **Editor reads Step 2 only.** Voice's Step 1 detailed responses stay voice-private. Per the §"What the Editor Pipeline Knows" architectural decision.
5. **Article length: 300-450 single-voice / 450-600 multi-voice.** Hard constraint per `runtime/flows/shared/prompts/editor_dossier.md`'s `body_paragraphs` envelope (corrected 2026-09-28 from "350-500 / 500-700," which matched neither the shipped prompt nor Tim's card). The article must not wander; a reader who only reads the article should get the question stated more sharply than the contemporary debate states it. (History: v1 said 700-900 words; v2's changelog narrowed to 350-500/500-700 per a voices-thread memo, but the prompt that shipped narrowed further to 300-450/450-600. Measured Athens output: 429-449 words single-voice, 566-627 multi-voice — see Constraints table above.) Tim's own card field `length_and_format_constraints` states a general "350–550 words" without the single/multi-voice split; the closing prompt's more specific per-voice-count envelope is what's actually enforced at generation time.
6. **No program-supply.** The article does NOT supply solutions or programs. Closes on the question stated more sharply, not on what to do. Per Tim's `quality_criteria` closing test (item 4) and `hard_limits` (no tactical/operational advice in self-help register).
7. **No "in conclusion" / bulleted takeaway close.** Per Tim's `quality_criteria` closing test: essays end on a vow, an aphoristic refusal, a small self-revision, or someone else's poem — never on "in conclusion," "ultimately," or a list. (Corrected 2026-09-28: v1/Claudia's card specified "no exclamation marks" under `register_and_tone`; that literal rule does not appear anywhere in Tim's card or in `editor_dossier.md`, so it is dropped rather than carried over unverified.)
8. **Bastard-form pronoun discipline.** Institutional we for declarative editorial work; first-person I only for surprise / difficulty / admission. Warmth in moves, not in pronoun inflection.
9. **One Anthropic call per dossier** (model set in `model_routing.json`, step `runtime.editor.dossier` — see "Models + thinking" below; current default Opus 4.7). Sonnet would lose the bastard form's calibration; Haiku won't carry the analytical generalization work; Opus 4.7 + thinking is the right model.
10. **No retry on failure beyond 1.** Same as voice pipeline's `stream_voice_call` retry budget.

---

## Scope

### In scope (this pipeline)

- Reading voice pipeline Step 2 artifacts + Provocateur briefings + Researcher themes + reference data
- Routing voices to dossiers (Stage 1)
- Generating per-dossier prose (Stage 2): front-page components, editor's article, theme page, per-artifact headnotes
- Persisting structured dossier JSON to `<run_dir>/05_editor/dossiers/`
- Cross-night state at `<PROJECT_ROOT>/published_artifacts/dossiers/night_<N>/`
- Token cost / wall accounting

### Out of scope (other pipelines + microsite + post-Athens)

- **Voice pipeline outputs.** This pipeline reads them; voice pipeline produces them.
- **Microsite rendering.** Per-voice CSS bundles, masthead typography, swipeable layout, responsive design. Microsite owns this.
- **Closing show theme-mapping.** Cross-night theme identification across all 3 nights' dossiers + voice artifacts. Separate pipeline; not yet built.
- **Substack draft pass.** Dropped per architectural decision (memo + this doc); Substack bridge does not exist.
- **Broadsheet print run.** A separate surface (frame doc spec'd it as one of N artifacts per night); could consume editor pipeline output but is its own pipeline.
- **Editor card construction.** How Tim's card is built is an operator-side / voices-thread concern, not this pipeline's runtime concern — this spec documents what the runtime loads from the card (§"The Editor — Tim Leberecht"), not how the card was authored.

---

## Implementation

### CLI

```bash
python flows/editor_flow.py <run_dir> --night N
```

With current options:
- `<run_dir>` — the per-night run directory (e.g., `<PROJECT_ROOT>/runs/athens_2026_2026_05_07_night1`)
- `--night N` — explicit night number; defensive `assert_run_dir_night_matches()` enforces consistency with run_dir naming
- `--skip-routing` (optional) — skip Stage 1; assume `theme_routing.json` is hand-written
- `--single-dossier <theme_id>` (optional) — generate only one dossier for testing/iteration
- `--no-cache` (optional) — disable prompt caching; useful when iterating on Tim's card

Athens production CLI (typical):
```bash
python flows/editor_flow.py <run_dir> --night N
```
(Stage 1 routing runs automatically; all dossiers generate in parallel.)

### File layout

```
runtime/
├── flows/
│   ├── editor_flow.py                  # orchestrator (entry point)
│   ├── editor/
│   │   ├── card_assembly.py            # Tim's card → editor-step system prompt
│   │   ├── routing.py                  # Stage 1 — theme routing
│   │   ├── dossier_generation.py       # Stage 2 — per-dossier Anthropic call
│   │   └── publish.py                  # write to <PROJECT_ROOT>/published_artifacts/dossiers/
│   └── shared/
│       ├── prompts/
│       │   ├── editor_dossier.md       # closing prompt for Stage 2
│       │   └── ...
│       └── ...
```

### Editor card → System Prompt Assembly

`runtime/flows/editor/card_assembly.py` mirrors `runtime/flows/voice/card_assembly.py` with editor-specific routing:

- **Foundational (13 fields, all calls):** identity + constitution + boundaries (same as voice pipeline)
- **Reasoning + engagement (5 fields, all calls):** reasoning_method, finds_compelling, resists, default_questions, disagreement_protocol
- **Voice / expression (7 fields, all calls):** rhetorical_mode, characteristic_moves, register_and_tone, metaphorical_repertoire, preferred_vocabulary, banned_language, banned_modes
- **Artifact (8 fields, all calls):** medium, technical_capabilities, characteristic_output_structure, relationship_to_detailed_response, aesthetic_qualities, stance_tendency, length_and_format_constraints, quality_criteria

All 33 fields load (same as voice's per-step routing post-2026-05-02 refactor; the editor's "step" is always dossier-generation, not three different steps). `metadata` and `smoke_test_chains` are always dropped, and `curated_corpus_passages.corpus_metadata` is stripped out (nested strip, C56 — mirrors the FU#41 strip on the voice pipeline side); `reference_only_passages` is dropped if present, defensively (Tim's card carries none). Prefix-cache breakpoint placed after BOUNDARIES section, per voice pipeline's prefix-caching pattern; this allows per-night dossier calls (3-5 per night) to share the cached prefix even when their step-specific tails differ slightly (per-dossier `theme` injection).

### Models + thinking

Model and thinking mode are set in `model_routing.json` (step `runtime.editor.dossier`) — that file is the source of truth, not this spec. The legacy `EDITOR_MODEL` / `CLAUDE_MODEL` env vars still override the model; `EDITOR_THINKING` overrides the thinking mode the same way.

- **Model (current default):** `claude-opus-4-7`
- **Thinking (current default):** adaptive, display=summarized (matches FU#60 pattern)
- **max_tokens:** 32K (output ceiling; actual output ~3-5K)
- **Caching:** 1h TTL on system prompt (Tim's card); cached across all dossiers within a night

### Defensive checks

- `assert_run_dir_night_matches(run_dir, night)` (existing helper) — refuses to run if `--night N` doesn't match run_dir's embedded night number
- Refuse to run if `<run_dir>/04_voice/manifest.json` shows incomplete voice pipeline (step2 not finished)
- Refuse to run if Tim's card at `<PROJECT_ROOT>/editor/tim_leberecht/07_persona_card_assembled.json` is missing or fails schema validation
- Issue number consistency check — derived `ATHENS_BASE_ISSUE + night_number` must match what's already published in prior nights' `published_artifacts/dossiers/night_<N-1>/dossier_*.json` (catches +1-off errors)

---

## Outputs

### Per-night under `<run_dir>/05_editor/`:

```
05_editor/
├── theme_routing.json              Stage 1 output; routing decisions
├── dossiers/
│   ├── dossier_001.json            Stage 2 output per dossier
│   ├── dossier_002.json
│   └── dossier_003.json
└── manifest.json                    pipeline run metadata (timings, token counts, status)
```

### Per-dossier published copy at `<PROJECT_ROOT>/published_artifacts/dossiers/night_<N>/`:

```
published_artifacts/dossiers/
├── night_1/
│   ├── dossier_001.json            published copy (microsite consumer)
│   ├── dossier_002.json
│   └── dossier_003.json
├── night_2/
│   └── ...
└── night_3/
    └── ...
```

Both copies are identical at production time. The `<run_dir>` copy lives with the night's other run artifacts (transcript, researcher output, provocateur briefings, voice artifacts) and represents what was generated; the `<PROJECT_ROOT>/published_artifacts/dossiers/` copy is the canonical published reference for the microsite + cross-night editorial review + closing show pipeline.

### Dossier index

Two index files are maintained under `<PROJECT_ROOT>/published_artifacts/dossiers/` — both written by the pipeline itself, not built lazily by a consumer:

- **Per-night index** — `night_<N>/_index.json`. Written by two independent code paths with different schemas: the editor (`flows/editor/edition.py::finalize_edition`, run as Stage 3 after each night's dossier calls) and `publish_flow.py::_build_per_night_dossier_index`. Each writer reads back whatever is already on disk and merges rather than overwrites, via a shared helper (`flows/editor/edition.py::merge_night_index`) — the rule is "each writer keeps the fields it doesn't own." The editor owns `NIGHT_INDEX_OWNED_TOP_LEVEL_KEYS` (`night`, `url_path`, `generated_at`, `dossier_count`, `edition_lead`, `dossiers`) and, per dossier entry, `NIGHT_INDEX_OWNED_DOSSIER_KEYS` (`dossier_no`, `filename`, `url_path`, `kicker`, `headline`, `subline`, `theme_id`, `theme_display_title`, `voice_count`, `voices_routed`). Publish owns its own top-level set (`night`, `url_path`, `generated_at`, `dossier_count`, `dossiers`, `voices_in_night`) plus per-dossier `issue_no`/`vol` on top of the same content fields — it deliberately never claims `edition_lead`, so the editor's lead-dossier pick survives a publish rerun, and the editor's rewrite likewise leaves publish's `issue_no`/`vol`/`voices_in_night` alone. The editor's write always rebuilds from every `dossier_*.json` file actually on disk for the night (`_rebuild_dossiers_from_disk`), not just the dossier(s) a `--single-dossier` rerun regenerated.
- **Root index** — `published_artifacts/dossiers/_index.json`, aggregating every night present. Rebuilt by `flows/editor/edition.py::update_root_index` at the end of every `finalize_edition` call, by walking each `night_<N>/_index.json` on disk; `publish_flow.py::_build_cross_night_dossier_index` also rebuilds an equivalent root index during publish.

Tracker refs: runtime OPEN_ITEMS C46 (per-night index dual-writer clobber fix) and PLAN 0.1.2.

---

## Cost & Envelope

Per the per-call cost above, scaled to Athens 3 nights:

| Stage | Calls/night | Per-call | Per-night | Athens total |
|---|---|---|---|---|
| Stage 1 (theme routing) | deterministic, no API call | $0 | $0 | $0 |
| Stage 2 (dossier generation, first call) | 1 | $0.45-0.50 | $0.45-0.50 | $1.35-1.50 |
| Stage 2 (dossier generation, subsequent calls per night, cache reads) | 2-4 | $0.165-0.24 | $0.33-0.96 | $0.99-2.88 |
| **Total Stage 2** | 3-5 | | **~$0.78-1.46** | **~$2.34-4.38** |

Plus prefix-cache write penalty on first call per night: ~$0.30 each = ~$0.90 across Athens.

**Athens 3-night editor pipeline total: ~$3-5.** Modest in absolute terms; cost dominated by output tokens (which prefix caching does not affect).

Wall time per night: ~5-10 min. The 3-5 dossier calls run in parallel; per-call wall is ~60-90s (Opus 4.7 + thinking on 30K input + 3-5K output). Single-threaded fallback wall ~3-5 × 75s ≈ 4-6 min.

---

## Validation Notes

The editor pipeline does not have separate validation nodes (unlike the voice pipeline's anachronism + constitutional checks). Quality is enforced by Tim's `quality_criteria` field (5 tests — opening, third-term, earned-uplift, closing, breakfast-table — verified present on his card 2026-09-28) applied during his thinking, plus operator review of generated dossiers before publication.

For Athens production: operator should review at minimum the FIRST dossier's article body before publication, to verify the bastard form is operating, the convergence-naming work landed, and the article-length constraint held. Subsequent dossiers can publish with lighter operator review if Tim's voice is consistent.

Future post-Athens validation surfaces (not in v1):
- Stylometric check against Tim's exemplar dossier-articles in his `curated_corpus_passages`
- LLM-as-judge pass scoring the article against quality_criteria 1-5
- Cross-dossier consistency check (Tim's voice across multiple dossiers in a night should not drift)

---

## Open Questions (v2 — pending operator decisions before first build)

These are settled-enough-to-build defaults, with operator-overrideable choices:

| # | Question | v2 decision | Notes |
|---|---|---|---|
| 1 | **Stage 1 routing — synthesis-only voices** (Case C, e.g. "Synthesise.") | ✅ **Sonnet 4.6 LLM-assisted call** for Case C voices (~$0.50 across Athens) | TODO marker in OPEN_ITEMS B1; ~30 min implementation + tests |
| 2 | **`prior_editions` shape on Night 2/3** | ✅ **Just the articles** (kicker + headline + body_paragraphs per prior dossier; drop front_abstract / headnotes / metadata) | Saves ~80% of token weight vs full dossier JSONs; preserves Tim's ability to write "as we noted last night, the river that did not speak" with anchor text |
| 3 | **`metadata.form_fit_status`** | ✅ **DROPPED.** The form-fit-honesty premise (memo §5) assumed Whanganui / Octopus / Marley produce non-prose artifacts. They don't: Whanganui will emit legal text (reflecting its legal personhood), Octopus produces prose (chromatophore display is a separate microsite render layer), Marley emits lyric-prose the editor's broadsheet form can carry. No voice in Athens needs the form-failure flag. | — |
| 4 | **`metadata.night_finding`** | ✅ **DROPPED.** Article body should already make the convergence/divergence finding clear; the field would be redundant. Closing-show pipeline (B5) doesn't exist yet, so designing for it is premature; if/when B5 lands, it can extract findings from articles via its own pass. | — |
| 5 | **`colophon`** | ✅ **Embedded in dossier JSON output, runtime-stamps near-static template.** Default: `"Filed by the Editor's desk on the morning of Night [N], from [date]. Vol. CXVI · Issue No. [N]."` | Tim doesn't emit it; purely metadata-derived. Confirmed against published dossiers (e.g. `night_1/dossier_001.json`: `"colophon": "Filed by the Editor's desk on the morning of Night 1."`) — `editor_dossier.md`'s emitted-fields list does not include `colophon`. Can be extended later (per-night quip, named correspondent attribution) |
| 6 | **Cross-night dossier numbering + theme handling** | ✅ **Per-night reset** within each issue (42,193 / 42,194 / 42,195). **Editor does NOT track cross-night theme identity** — that's Provocateur's job via C9 exclusion (matches by normalized title since theme_ids are not stable across Researcher runs). Tim references prior nights via prior_editions article text, not by theme_id matching. | Per [`provocateur_flow.py:579-580`](../runtime/flows/provocateur_flow.py:579) — "theme_ids are not stable across Researcher runs (each run generates fresh sequential IDs)" |
| 7 | **Operator-trigger vs auto-fire** | ✅ **Auto** — orchestrator polls `04_voice/manifest.json` and fires editor as soon as voice pipeline completes | Editor is just another stage in the chain |
| 8 | **Per-voice render-config bundles** (form-markers, palettes, closing seals) | ✅ **Microsite-side concern**, not editor-pipeline output. Microsite computes from voice's `medium` field. | — |

Q1, Q2, Q5, Q6, Q7, Q8 are settled. Q3 + Q4 deferred for separate reasoning.

**Items that previously appeared as open in v1 and are now CLOSED in v2:**

- ~~Strikethrough placement discipline per voice~~ → microsite render-config concern, not editor pipeline
- ~~Whether the editor pipeline runs auto or manual trigger~~ → see Q7 above (default auto)
- ~~Lead-theme decision~~ → publish-pipeline concern, not editor's
- ~~Byline split (Option A unified vs B correspondent/desk)~~ → byline dropped from output; colophon (Q5) handles desk attribution if needed
- ~~Asterism break encoding~~ → inline `"* * *"` array elements in `body_paragraphs[]`
- ~~Per-night cross-theme summary on front page~~ → no (front shows themes; reader connects)
- ~~Output mode (structured-output vs prose-and-parse)~~ → prose-and-parse, mirror voice pipeline
- ~~Closing prompt placement (system tail vs user prompt)~~ → system tail (Placement A)

---

## See also

- `docs/AI_Assembly_Voice_Pipeline.md` — Voice Pipeline (this pipeline's primary input source via Step 2 artifacts)
- `docs/AI_Assembly_Provocateur_Pipeline.md` — Provocateur Pipeline (per-voice briefings = editor's other primary input source)
- `docs/AI_Assembly_Researcher_Pipeline.md` — Researcher Pipeline (theme records that ride inside Provocateur briefings; v2 editor does NOT read Researcher outputs directly)
- `docs/AI_Assembly_Frame_Concept_v1.md` — frame architecture document (this pipeline operationalizes the broadsheet surface)
- `docs/AI_Assembly_Persona_Card_v2.md` — Tim's card uses this schema (Claudia Pinchbeck's deprecated draft card also used it)
- `docs/AI_Assembly_Persona_Pipeline_v4.md` — the standard persona pipeline Tim's card was built through (operator's Claude.ai Deep Research sessions + Beauty Shot operational supplement, merged); previously used to smoke-test Claudia's hand-authored draft card
- `docs/AI_Assembly_Briefing_v3_1.md` — project briefing (this pipeline's success criteria derive from §"Layer 1 / 2 / 3" tests)
- `_workspace/archive/MEMO_2026_05_03_editor_flow_input_output_contract.md` *(now archivable)* — predecessor memo capturing per-call input/output contract refinements; superseded by v2 of this spec
- `_workspace/archive/session-artifacts/CLAUDIA_PINCHBECK_PERSONA_PREP_2026-05-03.md` — Claudia Pinchbeck persona-construction reasoning (dead link fixed 2026-09-28: this doc previously cited a `_workspace/planning/runtime/CLAUDIA_PINCHBECK_CARD_DRAFT_2026_05_02.md` that was never written; this is the actual historical prep doc, marked 🟫 DEPRECATED in its own header since Tim Leberecht shipped as editor 2026-05-05). The draft 44-field card itself lives at `projects/current-tests/voices/claudia_pinchbeck/07_persona_card_assembled.json` (historical only; not used at runtime)
- `runtime/flows/editor_flow.py` — implementation entry point (shipped 2026-05-03 PM, commit `fc5c2fb`)
- `runtime/flows/shared/prompts/editor_dossier.md` — closing prompt. Rewritten to the v2 contract 2026-05-04 (`4c7c315`); last changed 2026-05-08 (`6973221`, `pull_quote`); generated all 13 published Athens dossiers. Its `<emitted_fields>` block is the ground truth for §"Dossier Shape" and §"Output Schema", which were rewritten against it on 2026-09-28 (v3). It contradicts itself on `front_abstract` — see §"Output Schema" → "Known quirks" #5.
- `runtime/flows/editor/dossier_generation.py` — parses Tim's output and stamps the runtime fields (`parse_dossier_output`, `stamp_runtime_fields`).
- `runtime/ingest/templates/admin_render_dossier.html` — the in-repo dossier renderer (admin dashboard); the public microsite lives outside this repo.

