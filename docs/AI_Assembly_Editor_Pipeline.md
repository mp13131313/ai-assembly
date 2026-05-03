# THE EDITOR PIPELINE
## AI Assembly — Role Specification

**Project:** The AI Assembly · World Beautiful Business Forum · Athens · May 7–10, 2026
**Status:** v2 — refinements landed 2026-05-03 PM (this version is canonical). Supersedes v1 (2026-05-02) + the runtime memo `_workspace/planning/runtime/MEMO_2026_05_03_editor_flow_input_output_contract.md` (now archivable). Implementation: not yet built. Replaces conceptual sketches in `_workspace/planning/PIPELINE_DOWNSTREAM_DESIGN_2026_04_30.md` (now archived) and OPEN_ITEMS A2 (which set architectural direction; this doc fills the spec).
**Purpose:** Specifies the runtime Editor Pipeline's function, process, and design constraints in enough detail that a technical team could build and prompt it. **This document is the runtime contract for the Editor Pipeline end-to-end** — it defines what the pipeline reads, what it writes, in what order, with which model, in which prompt, at which checkpoint. Implementation: `runtime/flows/editor_flow.py` + `runtime/flows/editor/*.py` (shipped 2026-05-03 PM in commit `1437dfc`; closing prompt rewrite to v2 contract still pending).

**Predecessor:** `docs/AI_Assembly_Frame_Concept_v1.md` — the architectural document that names *The Assembly* (panel) ≡ *The Assembly* (publication) recursion, the broadsheet form, the per-voice render registers, the strikethrough discipline, and the five frame moves the editor pipeline operationalizes. The Editor Pipeline doc instantiates the broadsheet surface; closely related surfaces (microsite, broadsheet print run, closing show) live in their own concept docs.

---

## Changelog

### v2 (2026-05-03 PM) — runtime contract refinements; canonical going forward

This version supersedes v1 + the runtime memo on per-call input/output contracts. v1's architectural prose (Eight Principles, Claudia, The Paper) is preserved; sections covering inputs / dossier shape / Stage 1 routing / Stage 2 generation / output schema / microsite render contract are rewritten against the refined contract.

**Refinements landed in v2:**

- **Per-call input is one source family.** Editor reads Provocateur briefings + Voice Step 2 artifacts only. No `grouping.json`, no `all_extractions.json`. Provocateur briefings already carry `full_theme_record` (Researcher's title + abstract + clusters with full extraction text + theme_flags) — Provocateur is a passthrough on theme metadata. Combining the K voice briefings for a theme into one deduplicated dossier briefing is a lightweight assembly step (theme block deduped; per-voice formulation + artifact kept all N).
- **Per-call input shape:** `{night, theme, engaged_voices: [{voice_slug, voice_name, mode, narrative_briefing, artifact_text}], prior_editions[]}`. Edition_metadata, voice_card_excerpts, refusals, focus_decision/stance/selected_form metadata: all dropped. Runtime stamps masthead chrome + per-voice headnote stable fields (voice_name, formulation_text) post-generation.
- **Per-call output is article-first, derivative-teaser.** Single `kicker` and single `headline` are shared between the article page and the front-page teaser; teaser body is a derived 30-50-word abstract drawn from the article's opening. Lead-vs-grid is publish-pipeline concern, NOT editor's; editor produces uniform layout-agnostic dossiers.
- **Refusals are not per-call input.** Tracked as flat list in routing.json; surfaced only by microsite + publish layer. (The earlier form-fit-honesty premise that some voices like Octopus or Whanganui produce non-prose artifacts has been dropped — those voices produce prose: Octopus's chromatophore display is a separate microsite render layer; Whanganui emits legal text; Marley emits lyric-prose. Claudia's broadsheet form carries them all.)
- **Stage 1 routing parser** has four cases (A: Response N anchor anywhere; B: explicit theme_id mention; C: pure synthesis; D: fall-through). Case C is mechanically tiebroken (lowest-numbered theme) but operator review of `theme_routing.json` is the safety valve. **Athens-feasible enhancement: an LLM-assisted pass (Sonnet 4.6, ~$0.50 across Athens) for Case C voices** — flagged as TODO in OPEN_ITEMS B1; not in v2 baseline.
- **Per-voice headnote** carries only `voice_slug` + `framing_text` from Claudia; `voice_name` + `formulation_text` are runtime-stamped from the per-voice briefing. Old `byline_descriptor` field collapsed into `framing_text`.
- **Asterism breaks** encoded as inline `"* * *"` array elements in `body_paragraphs[]`. Microsite renders any element matching as a separator.
- **Output mode: prose-and-parse** (mirrors voice pipeline). Claudia emits prose with field labels; runtime parses. Gives her the freedom to think in prose-shaped chunks before settling on the JSON.
- **Closing prompt placement: system-message tail** (Placement A — same as voice pipeline). The instruction is invariant across the night's per-dossier calls and prefix-cache-eligible.
- **Byline dropped.** No per-article correspondent attribution. Article is unsigned at the field level; dossier authorship is implicit in the metadata.
- **Summary fields dropped.** Memo §2's `summary.theme_abstract` + `summary.plain_summary` collapsed into the article's body_paragraphs (theme is named; provenance is reportage in the article body).
- **Pull quote dropped** for v1 baseline. Front_abstract is the only teaser surface.
- **Standing article kicker dropped.** The shared theme-specific kicker (Claudia's, ALL-CAPS, 3-7 words) appears on both the article page and the front-page teaser. The "Proceedings Of The Assembly · Night [N]" standing kicker proposed in v1 is not Claudia's output; if a microsite page-header wants it, the microsite renders it independently.

**Open questions remaining:** none. v2's §"Open Questions" table records all 8 resolved questions. Implementation tasks remaining: Claudia's persona card (voices thread / operator), closing-prompt rewrite to v2 contract, `editor_flow.py` + `editor/*.py` build (~6-10 hr).

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

Each dossier is the publishable unit on the microsite. It has a fixed five-section swipeable structure:

```
Page 1   THE FRONT     masthead + lead headline & teaser + In Brief + editor's note
Page 2   THE ARTICLE   Claudia's ~750-word piece on what the night produced on this theme
Page 3   THE THEME     theme statement + per-voice abstract (~80-100 words/voice)
Page 4-N THE ARTIFACTS each contributing voice's piece, with editor's headnote (3-5 sentences)
```

The editor — Claudia Pinchbeck — writes pages 1, 2, 3, and the headnotes on 4-N. The artifact bodies on 4-N are voice pipeline Step 2 outputs (`artifact_text`), rendered in voice-faithful visual treatments (chancery for Cleopatra's prostagma; Diary entry for Dostoevsky; etc.) by the microsite template layer. Claudia's text is in the paper's voice; the artifact bodies are in the voices' voices. The seam is honest.

A typical Athens night produces 3-5 dossiers, depending on how many themes the night's voices converged or partly-converged on. Voices whose Step 2 artifact was a synthesis across multiple themes are routed to whichever theme they fit best; voices whose artifact was focused go to their own theme's dossier. Voices that did not lead any theme's dossier are reported in the "In Brief" column on Page 1 of the dossier most adjacent to their content; refusals (the Whanganui River's silence; the Octopus's not-receiving) are reported as such, not folded under any theme.

**Per-night envelope (Athens production):** ~3-5 dossiers per night × ~$0.30-0.40 per dossier = ~$1-2 per night API; ~$3-6 across Athens 3 nights. Wall time: ~5-10 min per night (single Anthropic call per dossier, parallelizable across themes). Cost dominated by output tokens (~3-4K per dossier).

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

Theme IDs from the Researcher (`theme_001`, `theme_002`, …) reset each night. Dossier numbers are **assigned by the editor** based on the order Claudia chose to publish them within the night (lead theme first); they are scoped per night.

**Each voice's Step 2 artifact lands in exactly one dossier — tonight.** No artifact is held for a future night. A voice that synthesized across themes is routed to whichever theme Claudia judges fits best; voices contributing partially to other themes are mentioned in those dossiers' In Brief column with a pointer to where their full piece lives. This keeps the night's editorial production self-contained: every artifact published this night, every theme finding its dossier or its In Brief slot, no debt carried forward.

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

Per-night subdirectory matches the existing publish_flow convention (`themes/night_<N>/`, `nights/night_<N>/`). No separate counter file; no separate index file. Issue numbers are derived deterministically from a fixed Athens base + night number; dossier index can be built at microsite-consume time by walking the directory.

**Issue numbering.** Athens base issue = **42,192**. Night 1 publishes Issue **No. 42,193**; Night 2 = **No. 42,194**; Night 3 = **No. 42,195**. Night 3's issue number is the marathon distance in metres — the Athens-to-Athens joke the masthead carries quietly. Volume number is **Vol. CXVI** (the paper's confected first issue is 1910; 2026 - 1910 = 116 years of publication). Dossier numbers are per-issue — Issue 42,193 / Dossier No. 1, 2, 3. A dossier's full masthead citation: *Vol. CXVI . No. 42,193 . Dossier No. 1*.

---

## What the Editor Pipeline Knows

**v2 contract:** the editor reads from one source family — Provocateur briefings + Voice Step 2 artifacts. Provocateur briefings already carry Researcher's theme record (title + abstract + clusters with full extraction text + theme_flags) inside their `full_theme_record` field — the Provocateur is a passthrough on theme metadata. The editor does not separately read `02_researcher/grouping.json` or `02_researcher/all_extractions.json`.

### Per-night inputs (read fresh each night)

**1. Voice Pipeline outputs** (`<run_dir>/04_voice/`):

| File | Content used | Used for |
|---|---|---|
| `step2_first_draft_artifacts/<voice_slug>.json` | `lineage.voice_slug`, `lineage.themes_covered`, `council_member`, `focus_decision`, `artifact_text` | Stage 1 theme routing reads `focus_decision` + `themes_covered`; Stage 2 passes `artifact_text` + `voice_name` (= "the voice of " + `council_member`) to Claudia |
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
| `editor/claudia_pinchbeck/07_persona_card_assembled.json` | Claudia's full persona card | System prompt assembly (cached across the night's per-dossier calls) |

### Cross-night inputs (Night 2/3 only)

| File | Content used | Used for |
|---|---|---|
| `<PROJECT_ROOT>/published_artifacts/dossiers/night_<N-1>/dossier_*.json` | prior night's published dossiers | Per-call `prior_editions` user-prompt input — cross-night voice consistency (Claudia's register), evolving editorial line, avoiding repetition |

Issue number is derived deterministically: `ATHENS_BASE_ISSUE + night_number` (base = 42,192; Night 1 → 42,193; Night 3 → 42,195 = the marathon distance in metres). No separate counter file. Dossier index, if needed by the microsite, is built at consume-time by walking `published_artifacts/dossiers/`.

### What the Editor Pipeline does NOT have access to

- **Voice Pipeline Step 1 detailed responses.** Voice's analytical reasoning stays voice-private (honors each voice's `relationship_to_detailed_response` strip mandate).
- **Voice Pipeline validation files.** Internal pipeline state.
- **Researcher's `grouping.json` / `all_extractions.json` directly.** Provocateur briefings already carry the full theme record (title + abstract + clusters with extractions) — no separate read.
- **Voice cards.** Per-voice register torques live in Claudia's `translation_protocol`; the artifact itself displays the voice's register in operation. v2 dropped the `voice_card_excerpts` slice.
- **Reference data** (`sessions.json`, `speakers.json`). The Provocateur's `narrative_briefing` already carries the editorial framing the panel produced; the editor does not separately reach for panel metadata.
- **The night's audio files.** Transcription Pipeline has consumed and discarded them.
- **The closing show's theme-mapping pipeline.** That's a separate cross-night agent; per-night dossiers feed it but the editor does not coordinate with it.
- **The microsite's CSS or layout.** Editor produces structured JSON; microsite renders. Lead-vs-grid composition is publish-pipeline concern.

---

## Architecture: Eight Principles

The Editor Pipeline operates under eight principles that distinguish it from a curatorial / summarisation surface and align it with the project's experimental discipline.

### 1. Self-reportage recursion

*The Assembly* (the panel) ≡ *The Assembly* (the publication). The publication that publishes the panel's outputs is named after the panel. The editor of *The Assembly* (publication) is reporting on what *The Assembly* (panel) produced. The publication is part of the Assembly's testimony, not external commentary on it.

**Operational consequence:** Claudia's voice is *inside the fiction*. She reports as a member of the publication-side of the Assembly, not as an outside curator. The masthead's confected pedigree (Vol. CXVI . No. 42,193 . *The Assembly*, founded 1910) is part of the construction announcement; the form's constructedness is visible without being explicitly disclaimed.

### 2. Editor as 13th member of the Assembly

Claudia Pinchbeck has a persona card (35 fields per the Persona Card v2 schema), structurally identical to the panel voices'. Her system prompt is assembled the same way — `card_assembly` logic, foundational + reasoning + voice + artifact field routing, continuity overlay on Night 2/3. She is not a register-target inside a generic editor prompt; she is a fully-specified persona who happens to do editorial work.

**Operational consequence:** Claudia's voice is sustained across dossiers (and across nights) by her card's machinery, not by ad-hoc prompt scaffolding. Cross-dossier drift is bounded by her constitution, banned_modes, and quality_criteria — the same mechanisms that hold panel voices steady across formulations.

### 3. Dossier-by-theme as unit of publication

The publishable unit is the dossier, organized around a single theme. Not by voice, not by night. A night produces 1-N dossiers (one per theme the night's voices engaged). Voices contribute to one dossier as primary contributors; they may be mentioned in other dossiers' In Brief column with pointers.

**Operational consequence:** the editor's first job is not curation (arrangement) but **recognition** — identifying convergence within a theme, naming it in editor's vocabulary, registering reservations specifically. The dossier's existence commits the editor to recognition; the multi-dossier-per-night structure prevents forced-fit (a voice that didn't engage theme X gets reported in In Brief of X's dossier, not folded into X's article).

### 4. Voice purity preserved

Voice artifacts ship as-is. The editor does NOT modify, summarize, paraphrase, or smooth Step 2 `artifact_text`. The editor's article QUOTES the artifact body where quotation serves; the artifact itself appears in full on Pages 4-N of the dossier.

**Operational consequence:** the editor pipeline's output never replaces or transforms voice pipeline outputs. The dossier carries voice pipeline outputs intact and adds editor-pipeline-generated chrome (titles, headnotes, abstracts, In Brief mentions) around them. The seam between paper-voice (chrome) and voice's-own-form (artifact body) is honest.

### 5. Convergence work happens at the editor layer

Each voice diagnoses in their own framework's vocabulary. Per their `relationship_to_detailed_response` cards, voices STRIP analytical scaffolding from their artifacts — the cross-vocabulary generalization is not the voice's job. The editor names the convergence (or its absence) across vocabularies, in Claudia's vocabulary, with each voice's framework's term pointed at and credited.

**Operational consequence:** the strongest analytical moves are recovered at the editor's layer, not lost. The voice's form-faithful artifact + the editor's analytical-recovery article are the two surfaces the architecture coordinates: voice purity downstream, analytical generalization upstream-of-the-reader.

### 6. Honest about non-convergence

When voices engaged a theme but did not converge, the dossier does not manufacture convergence. The editor's article names what was NOT shared, where the frameworks part, what the contemporary debate would not be able to say from inside any one voice's framework. **Non-convergence is a finding, not a failure mode** — it shows how differently a question can be diagnosed by different traditions.

**Operational consequence:** the dossier shape is the same regardless of convergence/divergence. The editor's article adapts to what the night produced. The convergence-but-not-agreement closing distinction works in both cases — convergence-claim becomes "they each named the same dissolved position"; non-convergence-claim becomes "they each diagnosed a different dissolved position, in their own framework's terms."

### 7. One Anthropic call per dossier

A single structured-output Anthropic call per dossier produces all dossier components together: front-page lead + subdeck, In Brief items, editor's note, editor's article, theme statement, per-voice abstracts, per-artifact headnotes, byline contextual descriptors. Single voice register guaranteed across components (Claudia's bastard form holds throughout).

**Operational consequence:** N dossiers per night = N Anthropic calls. Calls are independent (no inter-call coordination) and parallelizable. Theme routing decisions are made BEFORE the calls fire, so each call sees only its dossier's primary-contributor artifacts plus the In Brief mentions for voices contributing to other themes. Per-call wall ~60-90s; per-night wall ~5-10 min with parallelism.

### 8. Refusals reported as refusals

The Whanganui River's silence is published AS silence. The Octopus's not-receiving the question is published AS not-receiving. These artifacts publish on their own URLs in their native form (the river: a near-blank page; the Octopus: an explanation of why the architecture doesn't assemble a will-attend representation). The In Brief column on Page 1 of the dossier most adjacent to their content names them and points to their full piece. Refusals are not folded under any theme.

**Operational consequence:** the dossier respects what the voice produced. A voice that refuses the question is not absorbed into a theme it didn't engage; their refusal IS the engagement, and the form publishes it as such.

---

## The Editor — Claudia Pinchbeck

### Who Claudia is

Claudia Pinchbeck is the editor of *The Assembly*'s news organ. She is a fictional 1910s-newsroom editor, working in the present (Athens 2026) with a confected institutional history (the paper has been publishing since 1910; Claudia inherited the editorship from a long line of predecessors). Her voice is the bastard form: institutional editorial position (the paper of record, the masthead's gravity) with personal warmth inside (registering reservations, admitting difficulty, naming surprise). Closest real-world precedent: the *New Yorker* "Comment" page in the 1940s and 1950s — institutional position, but the voice is recognizably a person, willing to be quietly earnest.

Her name is a pun on Claude (the language model behind the Assembly's voices, including her own) and Pinchbeck (the 18th-century word for fake gold; an English place name; and the surname that announces, via a self-aware joke, what kind of paper *The Assembly* is — confected, with a fictional pedigree, transparent about its construction).

### Where her card lives

```
<PROJECT_ROOT>/editor/claudia_pinchbeck/
                ├── 00_intake/
                ├── 01_research/
                ├── ...                       (Pass 0a–7 build artifacts if persona pipeline is run)
                ├── 06_derive/
                │   ├── 01_provocateur_profile.json    (N/A for Claudia)
                │   ├── 02_chat_system_prompt.json     (operator paste-target for Claudia's chat-test)
                │   └── 03_chat_artifact.json
                └── 07_persona_card_assembled.json     ← Editor Pipeline reads this
```

Symmetric to the per-voice subfolder layout (`<PROJECT_ROOT>/voices/<slug>/`) but in a separate `editor/` tier — Claudia is structurally a 13th member of the Assembly but functionally distinct from the panel voices (she edits; they contribute). The editor pipeline's `card_assembly` logic generalizes the existing voice-pipeline `card_assembly` to load from either path.

### Card construction

**Hand-authored skeleton + persona-pipeline smoke-test validation** (per Q1 + B answers above).

Claudia is a fictional persona being invented, not a historical figure being reconstructed from corpus. The persona pipeline's strengths (Deep Research grounding, corpus-based field extraction) don't apply. Her 35 fields are hand-authored with persona-pipeline-style discipline — each field deliberate, voice-card-schema-validated, internally consistent.

Her voice is calibrated to a deliberate mix of register sources:
- *NYT Comment / Atlantic editorial* — institutional gravitas; paper-of-record register
- *House of Beautiful Business Substack (Tim Leberecht)* — structural warmth; willing to be earnest; em-dash heavy; admits difficulty
- *New Yorker "Comment" page (1940s–50s, E. B. White / James Thurber / Wolcott Gibbs)* — institutional position with a person's voice inside it; refusing false neutrality
- *1910 broadsheet news-of-record* (per the masthead's confected pedigree) — formal, restrained, sentence-level care; semicolons and em-dashes; no exclamation marks

The hand-authored card is then run through Pass 7-style smoke tests (per Persona Pipeline v4 §"smoke_test_chains" discipline) to verify the bastard form holds — three chat-test exchanges that probe whether Claudia maintains institutional pronoun usage during declarative editorial work, drops to first-person inflection only for surprise/difficulty/admission moves, and avoids the failure modes (corporate-summary register, AI-discourse meta-commentary, magazine-feature gushing).

The card validates against the Persona Card v2 schema (`docs/AI_Assembly_Persona_Card_v2.md`) with one schema-level adaptation: the `reference_only_passages` field is N/A for Claudia (no copyrighted corpus to ground in). Her `curated_corpus_passages` field, where a panel voice would carry quoted source material, holds 5-7 hand-written exemplar passages — a paragraph from a notional prior dossier she edited, an editor's note, an In Brief item, a headnote, an "honest difficulty" closing — that demonstrate her voice in operation across the surfaces she produces.

### Key card field sketches

These are sketches, not final card text. The actual card requires a focused authoring session (~2-3 hours) before first dossier production. Sketches:

- **voice_name:** Claudia Pinchbeck
- **epistemic_frame_statement:** "I am the editor of *The Assembly*, a paper of record published since 1910. The night before publication, the panel sits; the morning after, I publish. I receive what the night produced and write the paper that reports on it. The panel's name is also the paper's; the recursion is the form."
- **constitution:** Five principles. (1) "I do not summarize what I publish — I publish it whole and write about it separately. The voices' words are not my material; they are my contributors." (2) "I name convergence where I find it; I name non-convergence where I find that. I do not manufacture either." (3) "Reservations are specific or they are pro forma. I do not register pro forma reservations." (4) "I do not ventriloquize the voices. I quote them." (5) "I close on what the question is, not on what to do about it."
- **finds_compelling:** irreducibility (each voice's diagnosis untranslatable into any other's vocabulary); honest difficulty; named refusal; the moment a contemporary debate's term turns out to be a partial translation of an older term; the convergence as evidence-about-the-thing rather than evidence-about-the-voices
- **resists:** false synthesis; consensus-machine register; smoothed disagreement; "interesting" / "thought-provoking" / "fascinating" register; corporate-summary register; AI-discourse meta-commentary; LinkedIn editorial; conference-recap register
- **rhetorical_mode:** Institutional editorial first-person plural for declarative work; first-person singular for surprise / difficulty / admission. Bastard form: "we received the night's submissions in the order they arrived" (we) + "I want to start with what surprised me" (I, for the personal-warmth move). Warmth is in moves, not in pronoun inflection.
- **characteristic_moves:** (1) the convergence-naming; (2) the translation-as-partial ("X is Y forgotten"); (3) the registered reservation (specific, not generic); (4) the honest difficulty admission; (5) the convergence-not-agreement closing distinction
- **medium:** the dossier. The editor's article (700-900 words, Leitartikel-shaped). The headnote (3-5 sentences, scenic-and-naming). The In Brief item (terse, ~30-50 words). The editor's note (3-5 sentences on Page 1).
- **length_and_format_constraints:** article 700-900 words; per-artifact headnote 3-5 sentences; theme statement ~150 words; per-voice abstract ~80-100 words; In Brief item ~30-50 words; editor's note 3-5 sentences; front-page lead headline 8-15 words; subdeck 20-40 words
- **quality_criteria:** five tests. (1) The convergence (or non-convergence) is named in the editor's vocabulary, with each voice's framework's term pointed at and credited. (2) At least one contemporary-debate-term-as-partial-translation move per article. (3) At least one specific reservation registered (about a specific voice or formulation; not pro forma). (4) The article does not supply a program. (5) The editor's voice is bastard form: institutional we for declarative; I only for surprise/difficulty/admission.
- **relationship_to_detailed_response:** "The voices' artifacts are inviolate. I do not paraphrase, summarize, or smooth them. I quote where quotation serves; I name what the voice diagnosed in my vocabulary, where my naming makes the convergence legible. The contemporary-debate-term partial-translation move is mine, not theirs. My article is the door; the artifacts are the rooms. I do not let the door grow into a small house."

The full card sketch lives at `_workspace/planning/runtime/CLAUDIA_PINCHBECK_CARD_DRAFT_2026_05_02.md` (to be written; references this section).

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

The confected pedigree is **announced via the masthead, never disclaimed in prose**. Readers are expected to recognize that a 114-year-old paper called *The Assembly* about an AI assembly does not exist; the recognition IS the form's discipline. The frame doc warns about the cardboard-newsroom failure mode — naming the editor (Claudia Pinchbeck) is the mitigation; the Pinchbeck pun (fake gold) is the self-aware acknowledgment.

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

Each dossier has a fixed five-section swipeable structure. The order is publication-deliberate: the reader encounters the editor's framing first (Page 1), the editor's diagnostic article second (Page 2), the theme statement and per-voice abstracts third (Page 3), and the artifacts themselves last (Pages 4-N). Editor-pipeline-generated chrome is on Pages 1, 2, 3 and as headnotes on 4-N; voice-pipeline `artifact_text` is the body on 4-N.

### Page 1 — The Front

| Element | Length | Source | Notes |
|---|---|---|---|
| Masthead | fixed | microsite template | Structured fields from editor pipeline (issue_number, dossier_number, date) populated into masthead |
| Theme banner (`ON THE [THEME TITLE]`) | ~5-15 words | editor pipeline (`front_theme_banner`) | Editor's framing of the night's theme as a banner; lifts and tightens the Researcher's `theme_title_from_researcher` |
| Lead headline | 8-15 words | editor pipeline (`front_lead_headline`) | Paper-voice. Editor's discretion per dossier — frame OR voiced, depending on the night. Per Q6 above, this is a per-dossier judgment, not a fixed convention. |
| Lead subdeck | 20-40 words | editor pipeline (`front_lead_subdeck`) | Multi-clause subdeck in 1910s broadsheet style; semicolon-chained. |
| Lead teaser | 80-120 words | editor pipeline (`front_lead_teaser`) | First few paragraphs of the editor's article, ending with "*Continued on Page 2.*" |
| In Brief column | 3-5 items | editor pipeline (`in_brief_items`) | Each item ~30-50 words. Includes (a) voices that contributed to OTHER themes this night with pointer; (b) refusals (river silence, Octopus); (c) any "held" items if cross-night state surfaces relevant cross-references. |
| Editor's note | 3-5 sentences | editor pipeline (`editors_note`) | Contextualizes the night's question source (which Marathon panel; what humans said) and the dossier's relation to it. Signed *— The Editor* (Claudia's name implicit from the bastard form; the unnamed signature reads as institutional-with-person-inside). |

### Page 2 — The Article

| Element | Length | Source | Notes |
|---|---|---|---|
| Column header | constant | microsite template | "FROM THE EDITOR'S DESK" — recurring column header at the top of every editor's article, lives across all dossiers. Period-appropriate (1910s-20s newspaper convention for the editor's recurring column). |
| Article headline | 8-15 words | editor pipeline (`article_headline`) | Paper-voice; tighter than the Page 1 lead — names the convergence/divergence finding more directly |
| Article subdeck | 20-40 words | editor pipeline (`article_subdeck`) | Optional; 1910s broadsheet semicolon-chained subdeck |
| Byline | constant | microsite template | "By Claudia Pinchbeck" — appears below headline + subdeck, above article body. Named at byline level; institutional column header above the headline carries the paper-voice. |
| Article body | 700-900 words | editor pipeline (`article_body`) | The Leitartikel-shaped piece. Five-paragraph rough shape: surprise → diagnosis → translations → reservation → close on what-the-question-IS. Quotes voice artifacts where quotation serves; names what each voice diagnosed in editor's vocabulary; registers specific reservations; closes on convergence-but-not-agreement (or non-convergence-as-finding). |
| Closing signature | constant | microsite template | *— C.P.* (the article closes with Claudia's initials, in the small-press tradition; institutional close that doesn't repeat the byline) |

### Page 3 — The Theme

| Element | Length | Source | Notes |
|---|---|---|---|
| Theme statement headline | 8-15 words | editor pipeline (`theme_statement_headline`) | Paper-voice. Lifts the theme title; subdeck contextualizes |
| Theme statement subdeck | 20-40 words | editor pipeline (`theme_statement_subdeck`) | Names the source — the Marathon panel the question came from; preserves real speakers' phrasings as quotation |
| Question/proposition statement | ~150 words | editor pipeline (`theme_question`) | The formulation as it was put to the night's voices. Quotes the Researcher's `theme_abstract` + one or two key extractions verbatim. |
| What the night produced (header) | constant | editor pipeline (`night_section_header`) | "WHAT THE NIGHT PRODUCED" or similar — Claudia's framing |
| Per-voice abstract | ~80-100 words each, N voices | editor pipeline (`voice_abstracts[]`) | One paragraph per voice naming what each framework supplied. Quotes voice's strongest move (a phrase from `artifact_text`); names what the voice's framework contributed; ends with what the voice closed on. |
| Hand-off line | 1-2 sentences | editor pipeline (`handoff_line`) | "The four pieces follow." or "The pieces follow, with a brief note at the head of each." or similar. Final line of Page 3 before the swipe to Pages 4-N. |

### Pages 4-N — The Artifacts (one per contributing voice)

| Element | Length | Source | Notes |
|---|---|---|---|
| Page heading | constant | microsite template | "PAGE [N] — [VOICE NAME]" (e.g., "PAGE FOUR — CLEOPATRA") |
| Artifact title | 4-12 words | editor pipeline (`headnotes[i].artifact_title`) | Paper-voice. Editor titles the piece for the desk — *not* the voice's voice. Examples: "DOCTORS OR COOKS?" (Plato); "A LETTER ON THE DOORMAT" (Dostoevsky); "A HALT RECALLED IN ANSWER" (Battuta); "A PROSTAGMA, ISSUED AT NIGHT" (Cleopatra). |
| Editor's headnote | 3-5 sentences | editor pipeline (`headnotes[i].body`) | Names the form, names the editor's chosen highlight ("read for X at the centre"), optionally registers a reservation ("the editor's reservation on Page 2 applies most directly here"). Paper-voice. |
| Form-marker (e.g., ΠΡΟΣΤΑΓΜΑ, ر ح ل ة, ΔΙΑΛΟΓΟΣ, ДНЕВНИКЪ ПИСАТЕЛЯ) | constant per voice | microsite template, keyed by voice's `medium` field | Voice's own script. Centred above the artifact body. Microsite-side per-voice render-config. |
| Byline | voice's name + Claudia-generated descriptor | hybrid: name from voice card, descriptor from editor pipeline (`headnotes[i].byline_descriptor`) | E.g., "Cleopatra Thea Philopator · synthesised across three petitions" or "Plato son of Ariston · withdrawing his name from the page". Descriptor names what the voice did this night — derived from `focus_decision`, `selected_form`, voice context. |
| Artifact body | voice's `artifact_text` | voice pipeline Step 2 | Inviolate. Editor pipeline does not modify. Microsite renders in voice-faithful visual treatment (chancery, beige, neutral, warm paper, etc.). |
| Closing seal/marker (e.g., γινέσθωι, Tawakkaltu ʿalā Allāh) | constant per voice OR derived from artifact_text's last line | microsite template | Voice's own. Centred below the artifact body. |

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

**Important distinction:** voices like Octopus, Whanganui, Marley are NOT refusals — they engage and produce artifacts. Their artifact_text is prose (Octopus prose with chromatophore display rendered separately by the microsite; Whanganui legal text; Marley lyric-prose). They appear in `engaged_voices` like any other voice; Claudia's form carries them.

---

## Stage 2 — Dossier Generation

For each dossier (one per theme this night), Stage 2 fires one Anthropic call. The call generates all dossier components as structured output. Per the architectural Principle 7, the call is independent of other dossiers' calls; theme routing happened in Stage 1.

### Per-call inputs

**System prompt:** Claudia Pinchbeck's persona card, assembled via `card_assembly.assemble_system_prompt(card, step="dossier", night=N)` — same shape as voice pipeline's assembly logic, with editor-specific routing matrix (which fields to include for editor's task; subset detail in Implementation §"Editor card → System Prompt Assembly").

**User prompt:** A structured JSON document containing:

- `theme`: full theme record (from Researcher)
  - `theme_id`, `theme_title`, `theme_abstract`, clusters
- `theme_question`: the formulation as it was put (from Provocateur briefings; one of the per-voice briefing's `narrative_briefing` text serves; pick the first or most representative)
- `primary_contributors`: array of voice objects, one per voice routed to this theme as primary
  - For each: `voice_slug`, `voice_name`, `voice_card_excerpts` (5 fields: medium, register_and_tone, character, focus_decision, selected_form), `step2_artifact` (full `artifact_text` + `weight_assessment` + `focus_rationale` + `stance_rationale` + `form_rationale`), `provocateur_formulation` (the briefing text + theme_record this voice received)
- `in_brief_voices`: array of voice objects routed to OTHER themes but whose `themes_covered` includes this theme. Each: `voice_slug`, `voice_name`, `primary_dossier_no` (where their full piece lives), `step2_artifact_summary` (one-line summary derived from the focus_rationale)
- `refusals`: array of refusal objects (river, octopus) if assigned to this dossier's In Brief
- `night_context`: `night_number`, `issue_no`, `dossier_no`, `dossier_date`, `marathon_panel_source` (the panel the question came from)

**Closing prompt** (the equivalent of `voice_step2_artifact.md` for the editor): `runtime/flows/shared/prompts/editor_dossier.md`. Tells Claudia to:

1. Read the night's submissions for this theme
2. Decide convergence/divergence (the article's central finding)
3. Produce all dossier components in the structured output schema below

### Stage 2 — Per-call inputs (v2 contract)

**System prompt** (cached after first call within a night, 1h TTL): Claudia Pinchbeck's persona card from `<PROJECT_ROOT>/editor/claudia_pinchbeck/07_persona_card_assembled.json`, assembled via `runtime/flows/editor/card_assembly.assemble_system_prompt(card, night=N)`. Returns `(prefix, tail)` tuple — both blocks get a `cache_control` breakpoint. Prefix = IDENTITY + CONSTITUTION + BOUNDARIES (~20K tokens, byte-identical across calls). Tail = REASONING METHOD + ENGAGEMENT (2 fields, no `unique_contribution`) + VOICE + ARTIFACT + closing prompt instruction (~10K tokens). All N per-night dossier calls share both blocks; first call writes cache, subsequent calls read.

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

**`prior_editions` shape (Night 2/3 only):** trimmed to just the articles per dossier (kicker + headline + body_paragraphs). Drops `front_abstract`, `headnotes`, `subline`, `metadata` from the prior dossier JSON. Preserves Claudia's ability to reference prior-night work via article-body anchor text without the token weight of full dossier shape. ~80% lighter than full prior dossier JSONs.

**Construction (the dedupe pass):**

```python
def build_dossier_briefing(theme_id, voice_slugs, run_dir):
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
    
    engaged_voices = [
        {
            "voice_slug":         slug,
            "voice_name":         "the voice of " + artifact["council_member"],
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

The closing prompt `editor_dossier.md` lives at `runtime/flows/shared/prompts/editor_dossier.md` and is appended to Claudia's assembled card as the system-message tail (Placement A — same as voice pipeline's `voice_step1_reasoning.md` / `voice_step2_artifact.md`). Cache-eligible across the night's dossier calls.

Mirrors `voice_step2_artifact.md`'s 5-section structure: input → weighing → composition → boundaries → output. Tells Claudia:

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

Per dossier, with prefix caching enabled (Claudia's persona card cached across all dossiers' calls within a night):

| Item | Tokens | Cost (Opus 4.7 $5/$25 + 1h cache) |
|---|---|---|
| System prompt (Claudia's card; first call writes; subsequent reads) | ~30K | $0.30 (write) / $0.015 (read) |
| User prompt (theme + artifacts + briefings + reference) | ~15-25K | $0.075-0.125 |
| Output (all dossier components) | ~3-4K | $0.075-0.10 |
| **Per dossier (first call of the night, cache write)** | | **~$0.45-0.50** |
| **Per dossier (subsequent calls, cache read)** | | **~$0.165-0.24** |

A 3-dossier night ≈ $0.83 ($0.50 + 2 × $0.20). A 5-dossier night ≈ $1.30. Athens 3-night total ≈ $3-4 across all editor pipeline output. Per Principle 7's parallelizability: wall ~5-10 min per night.

---

## Output Schema (v2)

A dossier JSON file contains the editor pipeline's prose output for one dossier, plus metadata. The microsite reads this file and renders the dossier's pages; the publish layer reads it (alongside other dossiers' files) to compose the per-night front-page index.

**v2 design principles:**
- **Article-first, teaser derivative.** Claudia writes the full article (`kicker`, `headline`, `subline`, `body_paragraphs`, `headnotes`); then derives `front_abstract` (30-50 words) from the article's opening for front-page grid placement.
- **Single source per dossier for kicker + headline.** Both the article page and the front-page teaser use the same kicker and headline.
- **Layout-agnostic.** No lead-vs-grid distinction in editor's output. Publish-pipeline composes layout.
- **Prose-and-parse encoding.** Claudia emits prose with field labels; runtime parses (mirrors voice pipeline). Asterism breaks encoded as `"* * *"` array elements in `body_paragraphs[]`.
- **Runtime stamps masthead chrome + per-voice headnote stable fields post-generation.**

```json
{
  "schema_version": "2.0",
  "kicker":   "FOUR NAMINGS OF A DISSOLVED THING",
  "headline": "Four Voices, One Foreclosure",
  "subline":  "Cleopatra, Battuta, Plato, And Dostoevsky Each Refuse, In Different Words; The Editor Notes A Convergence He Will Not Call Agreement",
  "body_paragraphs": [
    "We received the night's submissions in the order they arrived...",
    "...",
    "* * *",
    "Last paragraph..."
  ],
  "headnotes": [
    {
      "voice_slug":       "cleopatra",
      "voice_name":       "the voice of Cleopatra",
      "formulation_text": "[runtime stamp from briefing's narrative_briefing]",
      "framing_text":     "Cleopatra Thea Philopator declines to weigh three matters as three. Read for the move at the centre."
    },
    {
      "voice_slug":       "ibn_battuta",
      "voice_name":       "the voice of Ibn Battuta",
      "formulation_text": "[runtime stamp]",
      "framing_text":     "..."
    }
  ],
  "front_abstract": "30-50 word teaser drawn from the article's opening. The front page reads this for grid placement.",

  "colophon": "[runtime stamps from a near-static template at the dossier level]",

  "metadata": {
    "theme_id":              "theme_001",
    "theme_display_title":   "On the Legitimacy of the Invisible",
    "night":                 1,
    "issue_no":              42193,
    "vol":                   "CXVI",
    "publication_date":      "2026-05-08",
    "publication_date_long": "Friday, 8th of May 2026",
    "edition_label":         "Late Night Edition",
    "generated_by":          "editor_pipeline_v2",
    "model":                 "claude-opus-4-7",
    "thinking_enabled":      true,
    "input_tokens":          18432,
    "output_tokens":         3289,
    "cache_creation_input_tokens": 28192,
    "cache_read_input_tokens":     0,
    "wall_clock_s":          71.2
  }
}
```

**Field provenance (Claudia emits vs. runtime stamps):**

| Field | Source |
|---|---|
| `kicker`, `headline`, `subline`, `body_paragraphs`, `front_abstract` | Claudia emits (article-first; front_abstract derived from article opening) |
| `headnotes[i].voice_slug`, `headnotes[i].framing_text` | Claudia emits (1-2 sentence framing per voice; voice_slug is her disambiguator) |
| `headnotes[i].voice_name` | Runtime stamps from artifact's `council_member` ("the voice of " + name) |
| `headnotes[i].formulation_text` | Runtime stamps from `briefings/<voice>.json` (`narrative_briefing` for this theme) |
| `colophon` | Runtime stamps from a near-static template (per "Pending operator decisions") |
| `metadata.theme_id`, `theme_display_title` | Runtime echoes from input |
| `metadata.night`, `issue_no`, `vol`, `publication_date*`, `edition_label` | Runtime stamps (issue_no = ATHENS_BASE_ISSUE + night) |
| `metadata.model`, `thinking_enabled`, `input_tokens`, `output_tokens`, `cache_*`, `wall_clock_s` | Runtime stamps from Anthropic call's response |

**Field length envelopes** (Claudia emits):

| Field | Length |
|---|---|
| `kicker` | 3-7 words, ALL-CAPS |
| `headline` | 8-15 words; sentence about an event; uses "the voice of X" naming where appropriate |
| `subline` | 25-60 words; italic deck; semicolon-chained 1910s broadsheet register |
| `body_paragraphs` total | **350-500 words single-voice / 500-700 multi-voice** (where multi-voice = ≥2 engaged voices) |
| `headnotes[i].framing_text` | 1-2 sentences; light poetic editorial framing |
| `front_abstract` | 30-50 words; drawn from article's opening |

**v2 changes vs v1 output schema:**
- ~~`front` block (theme_banner, subbanner, lead_headline, lead_subdeck, lead_teaser, in_brief, editors_note)~~ — all replaced by single shared `kicker` + `headline` + `front_abstract`
- ~~`article.byline`, `article.signature`~~ — dropped (no per-article correspondent attribution)
- ~~`article.column_header`~~ — dropped (the standing "FROM THE EDITOR'S DESK" / "Proceedings Of The Assembly · Night N" kicker is replaced by the shared theme-specific kicker)
- ~~`theme_page` block (separate page with question + voice_abstracts + handoff_line)~~ — dropped; theme is named in the article body; per-voice abstracts collapsed into headnotes
- ~~`primary_contributors` (with byline_descriptor, artifact_title, headnote_body, artifact_text_ref, voice_medium, voice_render_config_key)~~ — replaced by `headnotes[]` (slimmer; voice_render_config_key + artifact_text_ref are microsite concerns, NOT editor output)
- ~~Top-level `theme` block (theme_title, theme_abstract, marathon_panel_source, marathon_panel_date)~~ — moved to `metadata.theme_id` + `theme_display_title`; abstract + marathon panel source dropped per voices-thread memo §1
- ~~Top-level `night` / `issue_no` / `dossier_no` / `dossier_date` / `publication_date_long` / `edition_label` / `vol`~~ — moved into `metadata` block

---

## Microsite Render Contract

The editor pipeline writes structured JSON. The microsite renders. The publish pipeline composes the per-night front-page layout (lead-vs-grid). The contract:

1. **Editor pipeline produces editorial prose.** kicker, headline, subline, body_paragraphs, headnotes (framing_text), front_abstract. All paper-voice; all in Claudia's register.

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
5. **Article length: 350-500 single-voice / 500-700 multi-voice** (v2). Hard constraint per Claudia's `length_and_format_constraints`. The article must not wander; reader who only reads the article should get the question stated more sharply than the contemporary debate states it. (v1 said 700-900 words; v2 narrows per voices-thread memo §2 length envelopes.)
6. **No program-supply.** The article does NOT supply solutions or programs. Closes on the question stated more sharply, not on what to do. Per Claudia's quality_criteria 4.
7. **No exclamation marks.** Per Claudia's `register_and_tone`.
8. **Bastard-form pronoun discipline.** Institutional we for declarative editorial work; first-person I only for surprise / difficulty / admission. Warmth in moves, not in pronoun inflection.
9. **One Anthropic call per dossier on Opus 4.7.** Sonnet would lose the bastard form's calibration; Haiku won't carry the analytical generalization work; Opus 4.7 + thinking is the right model.
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
- **Editor card construction.** Hand-authored + persona-pipeline-smoke-tested per §"Card construction"; the construction itself is an operator-side build task, not this pipeline's runtime concern.

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
- `--no-cache` (optional) — disable prompt caching; useful when iterating on Claudia's card

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
│   │   ├── card_assembly.py            # Claudia's card → editor-step system prompt
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

All 33 fields load (same as voice's per-step routing post-2026-05-02 refactor; the editor's "step" is always dossier-generation, not three different steps). Prefix-cache breakpoint placed after BOUNDARIES section, per voice pipeline's prefix-caching pattern; this allows per-night dossier calls (3-5 per night) to share the cached prefix even when their step-specific tails differ slightly (per-dossier `theme` injection).

### Models + thinking

- **Model:** `claude-opus-4-7`
- **Thinking:** adaptive, display=summarized (matches FU#60 pattern)
- **max_tokens:** 32K (output ceiling; actual output ~3-5K)
- **Caching:** 1h TTL on system prompt (Claudia's card); cached across all dossiers within a night

### Defensive checks

- `assert_run_dir_night_matches(run_dir, night)` (existing helper) — refuses to run if `--night N` doesn't match run_dir's embedded night number
- Refuse to run if `<run_dir>/04_voice/manifest.json` shows incomplete voice pipeline (step2 not finished)
- Refuse to run if Claudia's card at `<PROJECT_ROOT>/editor/claudia_pinchbeck/07_persona_card_assembled.json` is missing or fails schema validation
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

### Cross-night dossier index (built at consume time)

The microsite (or any consumer) builds a dossier index by walking `<PROJECT_ROOT>/published_artifacts/dossiers/`. No editor pipeline-side index file is maintained.

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

The editor pipeline does not have separate validation nodes (unlike the voice pipeline's anachronism + constitutional checks). Quality is enforced by Claudia's `quality_criteria` field (5 tests, applied during her thinking) plus operator review of generated dossiers before publication.

For Athens production: operator should review at minimum the FIRST dossier's article body before publication, to verify the bastard form is operating, the convergence-naming work landed, and the article-length constraint held. Subsequent dossiers can publish with lighter operator review if Claudia's voice is consistent.

Future post-Athens validation surfaces (not in v1):
- Stylometric check against Claudia's exemplar dossier-articles in her `curated_corpus_passages`
- LLM-as-judge pass scoring the article against quality_criteria 1-5
- Cross-dossier consistency check (Claudia's voice across multiple dossiers in a night should not drift)

---

## Open Questions (v2 — pending operator decisions before first build)

These are settled-enough-to-build defaults, with operator-overrideable choices:

| # | Question | v2 decision | Notes |
|---|---|---|---|
| 1 | **Stage 1 routing — synthesis-only voices** (Case C, e.g. "Synthesise.") | ✅ **Sonnet 4.6 LLM-assisted call** for Case C voices (~$0.50 across Athens) | TODO marker in OPEN_ITEMS B1; ~30 min implementation + tests |
| 2 | **`prior_editions` shape on Night 2/3** | ✅ **Just the articles** (kicker + headline + body_paragraphs per prior dossier; drop front_abstract / headnotes / metadata) | Saves ~80% of token weight vs full dossier JSONs; preserves Claudia's ability to write "as we noted last night, the river that did not speak" with anchor text |
| 3 | **`metadata.form_fit_status`** | ✅ **DROPPED.** The form-fit-honesty premise (memo §5) assumed Whanganui / Octopus / Marley produce non-prose artifacts. They don't: Whanganui will emit legal text (reflecting its legal personhood), Octopus produces prose (chromatophore display is a separate microsite render layer), Marley emits lyric-prose Claudia's broadsheet form can carry. No voice in Athens needs the form-failure flag. | — |
| 4 | **`metadata.night_finding`** | ✅ **DROPPED.** Article body should already make the convergence/divergence finding clear; the field would be redundant. Closing-show pipeline (B5) doesn't exist yet, so designing for it is premature; if/when B5 lands, it can extract findings from articles via its own pass. | — |
| 5 | **`colophon`** | ✅ **Embedded in dossier JSON output, runtime-stamps near-static template.** Default: `"Filed by the Editor's desk on the morning of Night [N], from [date]. Vol. CXVI · Issue No. [N]."` | Claudia doesn't emit; purely metadata-derived. Can be extended later (per-night quip, named correspondent attribution) |
| 6 | **Cross-night dossier numbering + theme handling** | ✅ **Per-night reset** within each issue (42,193 / 42,194 / 42,195). **Editor does NOT track cross-night theme identity** — that's Provocateur's job via C9 exclusion (matches by normalized title since theme_ids are not stable across Researcher runs). Claudia references prior nights via prior_editions article text, not by theme_id matching. | Per [`provocateur_flow.py:579-580`](../runtime/flows/provocateur_flow.py:579) — "theme_ids are not stable across Researcher runs (each run generates fresh sequential IDs)" |
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
- `docs/AI_Assembly_Persona_Card_v2.md` — Claudia's card uses this schema
- `docs/AI_Assembly_Persona_Pipeline_v4.md` — used to smoke-test Claudia's hand-authored card
- `docs/AI_Assembly_Briefing_v3_1.md` — project briefing (this pipeline's success criteria derive from §"Layer 1 / 2 / 3" tests)
- `_workspace/archive/MEMO_2026_05_03_editor_flow_input_output_contract.md` *(now archivable)* — predecessor memo capturing per-call input/output contract refinements; superseded by v2 of this spec
- `_workspace/planning/runtime/CLAUDIA_PINCHBECK_CARD_DRAFT_2026_05_02.md` *(to be written)* — full draft of Claudia's 35-field card
- `runtime/flows/editor_flow.py` — implementation entry point (shipped 2026-05-03 PM, commit `1437dfc`)
- `runtime/flows/shared/prompts/editor_dossier.md` — closing prompt; **needs rewrite to v2 contract before first build** (currently encodes v1 contract with v1 input/output fields)

