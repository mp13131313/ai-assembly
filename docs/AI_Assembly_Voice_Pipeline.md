# THE VOICE PIPELINE
## AI Assembly — Role Specification

**Project:** The AI Assembly · World Beautiful Business Forum · Athens · May 7–10, 2026
**Status:** v2.1 — current 2026-04-29. Implementation landed 2026-04-28 (commits `180a18f` + `aca0e4c`); v2.1 alignment with the 2026-04-28 persona-prompt revert (commit `9480d3a`) landed 2026-04-29. Replaces v1 partial draft (archived at `docs/_archive/AI_Assembly_Voice_Pipeline_v1_partial.md`).
**Purpose:** Specifies the runtime Voice Pipeline's function, process, and design constraints in enough detail that a technical team could build and prompt it. **This document is the runtime contract end-to-end** — it defines what the Voice Pipeline reads, what it writes, in what order, with which models, in which prompts, at which checkpoints. Implementation: `runtime/flows/voice_flow.py` + `runtime/flows/voice/*.py` (not yet built).

**Predecessor:** v1 partial at `docs/_archive/AI_Assembly_Voice_Pipeline_v1_partial.md`. v1 covered Steps 1+2 conceptually only; omitted Step 3 entirely; was materially stale on the persona card contract (no `voice_temporal_stance`, no FU#49, referenced 12 voices when panel is 10).

---

## Changelog: v2.1 (2026-04-29)

**Aligns the Voice Pipeline with the 2026-04-28 persona-prompt revert (commit `9480d3a`).** That revert restored Pass 2/3/4a/4b/5 to the 582af96 baseline, dropping cumulative additions that had degraded runtime artifact texture relative to the 2026-04-25 shipped-Plato baseline:

| Removed persona-side | Voice Pipeline alignment |
|---|---|
| TENSE DISCIPLINE blocks across Pass 2/3/4a/4b/5 | Voice Pipeline closing instructions trust the card; no separate tense-discipline mandate |
| `voice_temporal_stance` cryofreeze redesign (Pass 2) | `voice_temporal_stance.default` is the **fluid-across-time framing** ("voice speaks from within its own world and lifetime; reader has come to consult voice"). NOT cryofreeze. NOT "voice is in Athens 2026." Step 1/2/3 simply honor what the card says; the validator embeds the card's actual stance text instead of presupposing one |
| `medium` family-of-forms 30-line rewrite (Pass 4b) | `medium` may describe a single form OR multiple variants. Step 2 honors what's written: where single, that is the form; where multiple, voice picks per matter. Step 2 still records `selected_form` + `form_rationale` (trivial when single-form, substantive when multiple) |
| `characteristic_output_structure` per-form requirement | Field describes voice's actual arc, single or per-form per the card |
| `length_and_format_constraints` per-form variance | Honor as written; not presupposed conditional-on-form |
| `relationship_to_detailed_response` trace-tensions paragraph | Reverted to 582af96 spec |
| Universal anti-generic-register `banned_modes` entry (Pass 4a) | Voice's `banned_modes` is voice-specific (per-voice items the voice's corpus actually rules out); Step 2/3 prompts honor `banned_modes` as written |
| FU#49A v1 generativity-criterion mandate (Pass 4b) | FU#49A v2 (commit `0ca02f5`, 2026-04-29) replaced with field-tied 3-dim structure (REASONING / VOICE / FORM); `quality_criteria` is now 3-5 specific testable criteria, each tying named card fields together |

**Also:** Voice Pipeline `_unwrap_voice_temporal_stance` corrected to prefer `default` for Athens (was incorrectly preferring `anchored_override` whenever populated; commit landed 2026-04-29 same change set).

**Scope of v2.1 changes (all in this branch):**

- `runtime/flows/shared/prompts/voice_step1_reasoning.md` — drop conference-as-present framing in temporal-stance reminder
- `runtime/flows/shared/prompts/voice_step1_validation_anachronism.md` — drop hard-coded cryofreeze framing; embed card's actual `voice_temporal_stance` via `{{voice_temporal_stance}}` placeholder
- `runtime/flows/shared/prompts/voice_step2_artifact.md` — form-selection neutral wrt single-form vs multi-form `medium`; replace "anti-generic-register entry" hard reference with general `banned_modes` honoring
- `runtime/flows/shared/prompts/voice_step3_amendment.md` — same neutralization for amendment form-reselection
- `runtime/flows/shared/prompts/voice_continuity.md` — drop "(family-of-forms variant)" parenthetical; drop present-anchored "now" framing; honor `voice_temporal_stance` as written
- `runtime/flows/voice/card_assembly.py` `_unwrap_voice_temporal_stance` — Athens default = `default`, not `anchored_override`
- `runtime/flows/voice/step1_validation.py` `_build_anachronism_prompt` — substitute `{{voice_temporal_stance}}` from card

**Architectural impact:** none. The Voice Pipeline still has 3 steps + validation + continuity + publish; field routing matrix unchanged; output schemas unchanged (`selected_form` + `form_rationale` retained — they're harmless when single-form, substantive when multi-form, and the publish + continuity downstream consumers already reference them). The change is what the prompts tell the voice + what the validator presupposes.

### v2.1 follow-up (same day, additional commit)

Self-review of the v2.1 alignment commit surfaced two more items for the same alignment scope:

- **FU#57 (commit `8887af0`, 2026-04-29) was missed in the spec doc.** Code + voice prompts already reflected FU#57 (bold_engagement_topics dropped from runtime + chat artifact); but the Voice Pipeline spec doc still routed it across all 3 steps and quoted bold_engagement_topics bullets in the Step 1/2/3 closing-instruction extracts. Fixed: matrix row 18 → ❌ DROP all 3 steps; quoted bullets removed from extracts; strip-rules count 4 → 5; field count clarified as 35 runtime-loaded + 1 build-side audit only.
- **`voice_continuity.md` instruction logical bug.** First-pass v2.1 said "Honour the voice's `voice_temporal_stance` as written in its card" — but the continuity summariser does NOT have card access (its system prompt is `voice_continuity.md` only; user prompt is detailed responses + artifact text). Fixed: instruction now reads "Read the voice's detailed responses and artifact (provided in the user prompt below) — these already exhibit the voice's grammar and the way the voice stands toward time. Match that grammar in the summary." The summariser picks up temporal stance from the exemplar, not from a card it doesn't have.
- **`voice/README.md`** had one cosmetic "tense discipline" leak in the env var table — adjusted.

---

## Changelog: v1 partial → v2

The v1 partial draft was a working sketch of Steps 1+2 written before arch-03 + the 2026-04-28 persona-pipeline work. v2 is a fresh-write capturing the runtime contract end-to-end at the same level of implementation detail as the Researcher / Provocateur / Persona Pipeline v4 specs.

| Area | v1 partial | v2 | Reference |
|---|---|---|---|
| **Step 3 (Amendment)** | Mentioned in Briefing v3.1 conceptually; entirely unspecified in v1 | **Full spec landed** with FU#49E reviewer's cross-framework-examination framing as the system prompt seed | §"Step 3 — Amended Artifact" below |
| **Card → system prompt assembly** | Inline in Step 1/Step 2 templates; no canonical routing table | **Single canonical field-routing table** for all 36 generated card fields + 2 continuity nulls + 5 strip rules (post-FU#57: 35 runtime-loaded + 1 build-side audit only) | §"Card → System Prompt Assembly" below |
| **`voice_temporal_stance`** | Field did not exist in v1 (added 2026-04-21 as Pass 2 output) | **Treated as foundational** — loaded into Step 1 + Step 2 + Step 3 unwrapped to its prose form. Athens uses `default` (the fluid-across-time framing per the 2026-04-28 revert: voice speaks from within its own world and lifetime, the reader has come to consult the voice). The Voice Pipeline does not impose any temporal framing the card does not license | Card v2 + Pass 2 (582af96 baseline) |
| **`medium` field** | v1 assumed one rigid form per voice ("dialogue for Plato", "song for Marley") | **Voice's `medium` is honored as written** — single-form OR multi-form depending on what the card describes for the voice. Where multi-form, Step 2 selects per matter; where single-form, Step 2 just uses it. Step 3 may select a different form if `medium` admits it | Pass 4b (582af96 baseline) |
| **Anti-generic-register hard constraint** | — | Voice's `banned_modes` enumerates the per-voice register failures it must avoid (its corpus does not produce these). Step 2 + Step 3 prompts honor `banned_modes` as written; no universal entry is presupposed | Pass 4a `banned_modes` |
| **Panel size** | "12 voices × ~3 formulations = ~36 detailed responses" | **10 voices × ~3 formulations = ~30 detailed responses** (Tang + Thiel removed 2026-04-28 — living humans don't fit the deathbed-across-time framing) | HANDOFF_2026_04_28 §1 |
| **`reference_only_passages` Step 1-only** | Mentioned in passing | **Made explicit + load-bearing** in field-routing table; Step 2 + Step 3 both drop (copyright exposure) | personas/HANDOFF.md §"CRITICAL: `reference_only_passages` is Step 1 only — NEVER Step 2" |
| **Briefing input contract** | Sketched | **Byte-accurate** to Provocateur Stage 4 output: per-voice file at `runs/<run>/03_provocateur/briefings/<voice_slug>.json`, two views per formulation (`narrative_briefing` markdown + `full_theme_record` JSON) | runtime/flows/provocateur_flow.py:835–1041 |
| **File layout** | Implicit | **Mirrors Researcher (`02_researcher/`) + Provocateur (`03_provocateur/`) conventions** under `runs/<run>/04_voice/` | §"Outputs" below |
| **Validation nodes** | "Optional, recommended on" | **Default policy specified**: Athens Night 1 ON; Nights 2/3 OFF. **Diagnostic-only** (no regen-on-flag — decided 2026-05-01 FU#62 path B; operator morning-review is the correction loop) | §"Validation Nodes" below |
| **Continuity block generation** | Sketched in Step 2 system prompt | **Separate flow** with defined runtime trigger (after Night N Step 3 artifacts written, before Night N+1 Provocateur reads them); per-voice override file | §"Continuity Block Generation" below |
| **Cost & Envelope** | Single guess ($20-40/night) | **Per-stage table** for 10-voice panel (Athens production, Step 3 skipped per A1). **Night 1: ~$130-190, ~45-75 min wall** (validation ON); **Nights 2+3: ~$130-180, ~25-40 min wall** (validation OFF, +continuity). 3-night total ~$390-550. Revised 2026-05-01 from observed dryrun behavior + A1/FU#62 decisions | §"Cost & Envelope" below |
| **CLI** | — | `python flows/voice_flow.py <run_dir> --night N [--skip-validation] [--skip-step3]`. **Athens production:** always pass `--skip-step3` (A1 decision 2026-05-01); add `--skip-validation` on Nights 2/3 (FU#62 path B). | §"Implementation" below |

**Stable from v1:**
- Two-step logic (private reasoning → public expression) preserved as Step 1 → Step 2
- Foundational fields appear in all steps (now extended to all three steps)
- The 4-place load-bearing rule against few-shotting from `smoke_test_chains`
- Briefing v3.1's framing: "the conversation becomes more-than", "exposition vs. expansion"

---

## Overview

The Voice Pipeline is the third agent in the overnight pipeline. It receives the Provocateur's **per-voice briefing package** and produces three things in sequence:

1. **Step 1 — Private Reasoning.** Per formulation: voice reasons through the provocation in its characteristic mode of knowing. ~3 detailed responses per voice; ~30 per night. Nobody encounters this output except the voice itself (in Step 2) and downstream extraction.
2. **Step 2 — First-Draft Artifact.** Per voice: voice reads back its detailed responses, picks a focus + stance + form-from-family, and produces a single creative artifact in its native medium. 10 first-draft artifacts per night.
3. **Step 3 — Amended Artifact.** *(SKIPPED for Athens per OPEN_ITEMS A1 decision 2026-05-01 — Option A; pipeline ships Steps 1+2 only via `--skip-step3`. Cross-voice visibility moves to editor layer + Substack. Module dormant; re-add path documented.)* Original framing: per voice, voice reads other voices' first-draft artifacts on themes it shares with them, and decides whether to amend its own — extending its framework, marking its limit, or sharpening disagreement.

Plus two supporting flows:

- **Validation nodes** (optional, between Step 1 and Step 2): anachronism check (against `knowledge_boundary` + `voice_temporal_stance`) and constitutional self-reflection (against `constitution`). Default ON for Athens Night 1.
- **Continuity Block Generation** (after Night N completes, before Night N+1 Provocateur runs): per-voice Sonnet call summarising prior nights' positions/moves/threads + artifact focus/stance/form choices. Written to per-voice continuity override file; loaded by next-night Voice Pipeline.

**Per-night envelope** (10-voice panel, Athens production with Step 3 skipped per A1 2026-05-01): Night 1 ~$130-190 / ~45-75 min wall (validation ON); Nights 2+3 ~$130-180 / ~25-40 min wall (validation OFF, continuity ON). 3-night total ~$390-550. See §"Cost & Envelope" for breakdown.

The Voice Pipeline runs once per night across three Athens nights. On Night 2 + Night 3, the continuity override is loaded as a card supplement; otherwise the pipeline shape is identical.

### Multi-night convention

**One run_dir per night.** Each Athens night is a complete, self-contained pipeline run from transcription through publish. Convention:

```
<PROJECT_ROOT>/runs/athens_2026_2026_05_07_night1/
                ├── 01_transcription/
                ├── 02_researcher/
                ├── 03_provocateur/
                └── 04_voice/

<PROJECT_ROOT>/runs/athens_2026_2026_05_08_night2/
                └── (same shape, fresh inputs)

<PROJECT_ROOT>/runs/athens_2026_2026_05_09_night3/
                └── (same shape, fresh inputs)
```

Inside each night's `04_voice/`, voice files are named per-voice without a night suffix (`step2_first_draft_artifacts/plato.json`, not `plato_night_1.json`) — the night is implicit in the run_dir.

Theme IDs from the Researcher (`theme_001`, `theme_002`, …) reset each night. They are unique within a night via run_dir namespacing; cross-night referencing happens via lineage paths that include `run_id` (the run_dir leaf).

**Cross-night state lives at PROJECT_ROOT, not inside any run_dir:**

- `<PROJECT_ROOT>/voices/<slug>/continuity_night_<N>.json` — voice's memory of prior nights, written by the continuity flow at end of Night N-1, consumed by Night N's voice system prompt
- `<PROJECT_ROOT>/published_artifacts/nights/night_<N>/<slug>.json` — published artifact (micro-site / Edition / Substack consumer)
- `<PROJECT_ROOT>/published_artifacts/voices/<slug>_multi_night.json` — per-voice 3-night index (built by `publish_flow.py`)

**Why this convention:** each night's run_dir is self-contained, easy to archive, and doesn't risk cross-night collision. Continuity reads ONE night's `04_voice/` at a time. Multi-night aggregation happens deliberately at the publish layer, where cross-night views are explicit. A failure on Night 2 doesn't risk Night 1 state.

**Defensive labeling:** `04_voice/responded_to_graph_night_<N>.json` and `04_voice/themes_to_voices_night_<N>.json` carry `_night_N` in the filename even though the run_dir already implies the night. Cost is zero; benefit is clarity if the filename ever escapes context (e.g. surfaced in a publish layer that aggregates across nights). The runtime continuity + publish files at PROJECT_ROOT also include night in their names; consistency favors keeping the suffix here too.

---

## What the Voice Pipeline Knows

### 1. Itself (the persona card)

The Voice Pipeline loads `<PROJECT_ROOT>/voices/<slug>/07_persona_card_assembled.json` — the v2 Persona Card produced by the Persona Pipeline v4. It contains:

- **4 root identity fields:** `voice_name`, `voice_mode`, `pipeline_version`, `generated_date`
- **35 v2 card fields** flat at root (Identity, Constitution, Boundaries, Reasoning, Engagement, Voice, Artifact)
- **`voice_temporal_stance`** (added 2026-04-21; current shape per 582af96 baseline as of 2026-04-28 revert): two-part object with `default` + `anchored_override`. **For Athens, always use `default`** — voice speaks from within its own world and lifetime; the reader has come to consult the voice, the voice has not gone forward to the reader's time. The `anchored_override` field is for chat-test deployments (consumed by the chat_system_prompt builder in `personas/`) and MUST NOT be used at Voice Pipeline runtime — `_unwrap_voice_temporal_stance(deployment="athens")` enforces this
- **2 continuity null fields** (`continuity_block_if_night_2`, `continuity_block_artifact_if_night_2`): null on Night 1, populated at runtime via the continuity override on Night 2+
- **`reference_only_passages`** (copyright-sensitive tier-2 corpus, e.g. Marley lyrics): `{passages: [...], runtime_contract_note: "..."}`. **Step 1 only** — drops from Step 2 + Step 3
- **`metadata` block** (provenance, validation status, FU#13 fix log, etc.): **always dropped** before assembly
- **`smoke_test_chains`** (build-time diagnostic from Pass 7b): **always dropped** (NEVER few-shot — see below)

The total card is ~10-15K tokens of system prompt content. The card IS the system prompt. Per the Persona Card v2 register rule, every field is in first or second person — never third-person scholarly description.

### 2. The briefing material (Provocateur output)

The Voice Pipeline reads `<run_dir>/03_provocateur/briefings/<voice_slug>.json`. Shape (per `runtime/flows/provocateur_flow.py` Stage 4 packaging, with 2026-04-28 amendments for Voice Pipeline v2 contract):

```json
{
  "formulations": [
    {
      "theme_id": "theme_003",
      "theme_display_title": "string",
      "mode": "question" | "proposition",
      "formulation_text": "the formulation as plain text (added 2026-04-28)",
      "context_narrative": "string — Provocateur's curated framing (added 2026-04-28)",
      "selected_quotes": [
        {"extraction_id": "session:NNN", "quote": "...", "attribution": "...", "flavor": "..."}
      ],
      "narrative_briefing": "markdown string — the Step 1 user prompt with FORMULATION header now labelled with mode (added 2026-04-28)",
      "full_theme_record": {
        "clusters": [{"cluster_id": "...", "cluster_title": "...", "cluster_abstract": "...", "extractions": [...]}, ...],
        "theme_title_from_researcher": "string",
        "theme_abstract_from_researcher": "string",
        "co_assigned_voices": ["Voice X", "Voice Y"],
        "theme_flags": {
          "audience_friction": "low" | "moderate" | "high",
          "fault_line_present": true | false,
          "theme_quality": <number>
        },
        "grounding_extraction_ids": ["session:NNN", ...]
      }
    },
    ...
  ]
}
```

**Two views per formulation:**

- **`narrative_briefing`** is the markdown PROMPT the voice's Step 1 LLM call sees as its user prompt. Format: `THEME:` / `CONTEXT FROM TODAY'S SESSIONS:` / `EXTRACTION — positions heard today:` / `FORMULATION (mode: question|proposition):` / hint to `full_theme_record` for deeper inspection. The mode label in the FORMULATION header is load-bearing — the Voice Pipeline's Step 1 closing instruction branches on mode, so the voice must see it in the user prompt without having to look up JSON metadata. Paste-and-go.
- **`full_theme_record`** is the wider REASONING SURFACE for the voice's Step 1 thinking. Structured JSON. The voice's private deliberation should range over the full record — clusters with raw extractions sorted by lens (assertions first, reframings next, open_questions last), Researcher's own theme title and abstract (so the voice can see where the Provocateur's display title diverges if at all), co-assigned voices (so the voice knows its response is not the only one coming), editorial flags, grounding extraction IDs.

A voice with the full picture might notice positions the curated quotes left out, see counter-currents the Provocateur didn't surface, or confirm the framing was right and stay close to it. All are good Step 1 moves.

**Structured fields exposed at briefing-entry top level** (`formulation_text`, `context_narrative`, `selected_quotes`, `mode`) are NOT consumed in the Step 1 user prompt directly — the markdown renders them inline. They exist for Voice Pipeline's bookkeeping: `formulation_text` is echoed verbatim into Step 1's output schema as part of the lineage chain; `selected_quotes` is available to Step 3 if an amendment wants to cite a curated quote directly; `mode` lets `voice_flow.py` switch behaviour per formulation without parsing markdown. The Provocateur's `rationale` field is NOT in the briefing — kept in the per-pair file for audit (would prime the voice).

### 3. Step 3 inputs (other voices' first-draft artifacts)

After all 10 voices complete Step 2, Step 3 reads the first-draft artifacts of OTHER voices on themes the voice shares with them. The shared-theme determination uses `co_assigned_voices` from each formulation's `full_theme_record`. For each shared theme, Step 3 receives:

- The **shared-theme excerpt** of the other voice's artifact (the portion responsive to the shared theme — extracted from the full artifact via theme tagging or, if untagged, the full artifact)
- The **`full_artifact_record`** second view (the complete first-draft for context)
- The other voice's name + medium + selected form

Step 3 does NOT read other voices' detailed responses (Step 1 output). Cross-voice contamination at the reasoning layer is what the architecture forbids; cross-voice deliberation at the artifact layer is what Step 3 enables.

### 4. What the Voice Pipeline does NOT know

- **Other voices' detailed responses (Step 1 output).** Steps 1 and 2 are private per voice. Only Step 3 sees other voices' work, and only at the artifact layer.
- **The Provocateur's strategy.** Why this formulation was assigned to it, what the Selection algorithm calculated, what the Triage Part B fault-line description said about cross-council splits.
- **The audience profile.** The Voice Pipeline does not load `audience_profile.json`. The Provocateur knows the audience; the voices speak from their frameworks.
- **The closing-show matrices (Matrix A: Power & Agency; Matrix B: Change & Actor).** The voices reason authentically; downstream pipelines map detailed responses + artifacts onto the matrices.
- **It does not know it's an AI.** Within generation, the voice operates from inside its persona. The epistemic frame is a disclosure to the audience encountering the artifact; it is not a self-awareness the voice carries during generation.
- **The Provocateur's `rationale` field per formulation.** Kept in the per-pair checkpoint (`runs/<run>/03_provocateur/formulations/{theme_id}__{slug}.json`) for audit; not passed to the voice (would prime the voice toward the Provocateur's expected answer).

---

## Architecture: Five Principles

1. **The card is the system prompt.** Per Persona Card v2 register rule, every card field is in first or second person — never third-person scholarly description. The Voice Pipeline does NOT rephrase or reinterpret card fields at runtime — it slots them into the system prompt template as-is. The card has been built to act; the runtime trusts it. Whatever framing the card carries (temporal stance, form, voice-specific banned modes), the Voice Pipeline honors as written; it does not impose framings the card does not license.

2. **Per-step field routing.** Each card field is routed to Step 1 (reasoning), Step 2 (expression), Step 3 (both), or dropped. The single canonical routing table (next section) is the contract — implementation must match it byte-for-byte.

3. **Drop-list discipline (5 load-bearing rules).** Five card elements have specific strip rules that must be applied at system prompt assembly time:
   - **Drop `metadata` always** (build-time provenance, not behavioural spec)
   - **Drop `smoke_test_chains` always** (NEVER few-shot — see "do NOT few-shot from smoke_test_chains" below)
   - **Drop `reference_only_passages` from Step 2 + Step 3** (copyright; Step 1 keeps it for grounding)
   - **Drop `curated_corpus_passages.corpus_metadata` (nested) always** (FU#41 nested-strip rule; parent preserved with `passages[]` intact)
   - **Drop `bold_engagement_topics` always (FU#57, 2026-04-29)** — pre-loaded courage menu pulled reasoning toward predetermined topics rather than letting the matter drive. Field stays in the persona card for build-side audit value but is NOT loaded into the runtime system prompt; same field is dropped from the chat artifact

4. **Parallel across voices, sequential per voice.** Step 1 calls run in parallel across all 10 voices and within each voice (per formulation). Step 2 runs in parallel across voices after each voice's Step 1 calls complete. Step 3 runs in parallel across voices, but must wait for ALL 10 voices' Step 2 to complete (Step 3 reads other voices' first-drafts).

5. **Checkpoints-as-cache.** Every LLM call writes its output incrementally to disk before returning. A crashed run resumes from the last completed checkpoint. There is no `CACHE=1` flag — the checkpoints ARE the cache. To force a clean run, delete `runs/<run>/04_voice/` or specific subdirectories. Mirrors Researcher / Provocateur convention (CURRENT_STATE §5.8).

---

## Card → System Prompt Assembly

### Field-routing table (canonical)

The Voice Pipeline assembles three different system prompts per voice — one for Step 1, one for Step 2, one for Step 3. Each step gets the foundational identity fields plus its step-specific fields. The table below is the single contract; implementation must match.

| # | Field | Step 1 | Step 2 | Step 3 | Notes |
|---|---|---|---|---|---|
| **FOUNDATIONAL — all three steps** |||||
| 1 | `council_member_name` | ✓ | ✓ | ✓ | "You are X" — first line of every system prompt |
| 2 | `epistemic_frame_statement` | ✓ | ✓ | ✓ | Apply framework boldly; name gaps; "informed by the scholarly readings of …" |
| 3 | `world` | ✓ | ✓ | ✓ | Voice's time and place |
| 4 | `formative_experience` | ✓ | ✓ | ✓ | The wound / the formative engagement |
| 5 | `character` | ✓ | ✓ | ✓ | Personality in period-native character grammar |
| 6 | `constitution` | ✓ | ✓ | ✓ | Core commitments — "check every response against these" |
| 7 | `concept_lexicon` | ✓ | ✓ | ✓ | Precise vocabulary with exclusions |
| 8 | `curated_corpus_passages` | ✓ | ✓ | ✓ | Step 1 = grounding for thinking; Step 2 = voice exemplar (how this voice writes); Step 3 = both. **DROP nested `corpus_metadata`** in all steps |
| 9 | `knowledge_boundary` | ✓ | ✓ | ✓ | Now learning-at-conference posture (2026-04-28) |
| 10 | `translation_protocol` | ✓ | ✓ | ✓ | Method, not lookup table; pull modern → voice's terms |
| 11 | `topics_requiring_care` | ✓ | ✓ | ✓ | Engage with care, don't avoid |
| 12 | `hard_limits` | ✓ | ✓ | ✓ | Position-B preamble: forbids framework-ABANDONMENT, permits corpus-internal CROSS-EXAMINATION |
| 13 | `voice_temporal_stance.default` | ✓ | ✓ | ✓ | **Fluid-across-time framing per the 582af96 baseline** (post-2026-04-28 revert). Voice speaks from within its own world and lifetime; reader has come to consult voice. **Athens always uses `default`** even when `anchored_override` is populated (`anchored_override` is for chat-test deployments only) — `_unwrap_voice_temporal_stance(deployment="athens")` enforces this |
| **REASONING / ENGAGEMENT — routed per field** |||||
| 14 | `reasoning_method` | ✓ | | ✓ | The 5-8-step process this voice characteristically follows. Step 3 reasons about other voices' artifacts before amending |
| 15 | `finds_compelling` | ✓ | | ✓ | Selectivity — argument textures that draw the voice in |
| 16 | `resists` | ✓ | | ✓ | Sharpest critique triggers |
| 17 | `smoke_test_chains` | ❌ DROP | ❌ DROP | ❌ DROP | **NEVER few-shot.** Build-time diagnostic only |
| 18 | `bold_engagement_topics` | ❌ DROP | ❌ DROP | ❌ DROP | **FU#57 (2026-04-29):** dropped from runtime + chat artifact. Pre-loaded courage menu pulled reasoning toward predetermined topics rather than letting the matter drive. Field is still emitted by Pass 5 — preserved in the persona card for build-side audit value, NOT loaded into the runtime system prompt |
| 19 | `default_questions` | ✓ | | ✓ | Post-reasoning audit — characteristic interrogation |
| 20 | `disagreement_protocol` | ✓ | | ✓ | **Critical for Step 3** — how voice handles disagreement (reductio, distinction-making, withdrawal, etc.) |
| 21 | `unique_contribution` | ✓ | ✓ | ✓ | Step 1: spotlight instruction. **Step 2: anchors focus decision** (the detailed response carrying the distinctive perception earns focus). Step 3: load-bearing for "find the move only your framework can make" |
| **VOICE / EXPRESSION — Step 2 + Step 3** |||||
| 22 | `rhetorical_mode` | | ✓ | ✓ | Structural identity — dialogic, distinction-making, confessional, non-propositional, etc. |
| 23 | `characteristic_moves` | | ✓ | ✓ | 3-5 signature patterns |
| 24 | `register_and_tone` | | ✓ | ✓ | Music of the voice |
| 25 | `metaphorical_repertoire` | | ✓ | ✓ | Imagery — what this voice reaches for |
| 26 | `preferred_vocabulary` | | ✓ | ✓ | Words the voice thinks in (with FU#32 STRIP+USE pairs) |
| 27 | `banned_language` | | ✓ | ✓ | Anti-persona-collapse list |
| 28 | `banned_modes` | | ✓ | ✓ | Includes 2026-04-28 anti-generic-register universal entry baked into the card |
| **ARTIFACT — Step 2 + Step 3 (Step 3 may reselect form)** |||||
| 29 | `medium` | | ✓ | ✓ | **Family-of-forms** (Card v2.1 §H). Default form + 3-6 native variations. Step 2 picks form per formulation; Step 3 may pick a different form for amendment if matter calls for it |
| 30 | `technical_capabilities` | | ✓ | ✓ | Text only / text+image / text+audio. Read by orchestration for API routing |
| 31 | `characteristic_output_structure` | | ✓ | ✓ | **Arc-per-form** within the family |
| 32 | `relationship_to_detailed_response` | | ✓ | | Step 2-specific transformation rule. Step 3 transforms its own first-draft, not detailed responses, so does not need this |
| 33 | `aesthetic_qualities` | | ✓ | ✓ | Gestalt feel of the finished piece |
| 34 | `stance_tendency` | | ✓ | ✓ | Natural emotional-intellectual pull |
| 35 | `length_and_format_constraints` | | ✓ | ✓ | **Conditional on selected form** from `medium` family |
| 36 | `quality_criteria` | | ✓ | ✓ | Self-check (≥1 generativity criterion per FU#49A) |
| **CONTINUITY — populated at runtime, Night 2+ via override file** |||||
| 37 | `continuity_block_if_night_2` | ✓ (Night 2+) | | ✓ (Night 2+) | Voice remembers prior nights' positions / key moves / unresolved threads |
| 38 | `continuity_block_artifact_if_night_2` | | ✓ (Night 2+) | ✓ (Night 2+) | Voice remembers prior nights' artifact focus / stance / form choices |
| **STRIP RULES (load-bearing)** |||||
| | `metadata` (top-level block) | ❌ | ❌ | ❌ | Build-time provenance, not behavioural spec — always drop |
| | `reference_only_passages` | ✓ load | ❌ DROP | ❌ DROP | Step 1 only. Step 2 + Step 3 produce public-facing artifacts; copyright exposure for Marley / Dostoevsky tier-2 corpus |
| | `curated_corpus_passages.corpus_metadata` (nested) | ❌ | ❌ | ❌ | FU#41 nested-strip rule |

**Field count check:** 36 generated card fields (35 v2 baseline + `voice_temporal_stance` added 2026-04-21) + 2 continuity nulls + 5 strip rules. Of the 36 generated, **35 are runtime-loaded** and **1 (`bold_engagement_topics`) is build-side audit only** per FU#57 2026-04-29.

### CRITICAL: do NOT few-shot from `smoke_test_chains`

The persona card has a `smoke_test_chains` field with 3-5 example provocation→response chains generated by Pass 7b at build time. They look like a natural candidate for few-shot exemplars in the Voice Pipeline's Step 1 prompt.

**They are not. Do NOT load them into any prompt.**

`smoke_test_chains` is a build-time diagnostic, not a runtime contract. The persona card's 35 fields (constitution, reasoning_method, characteristic_moves, concept_lexicon, banned_language, banned_modes, etc.) are the contract. Trust them. Failure modes if you ignore this:

- The voice's range collapses toward whatever 4 patterns happened to be in the test set
- Failure patterns Pass 7c worked to remove get re-introduced via the examples
- The provocations are stale (built against an old `conference_context` at card-build time, not the actual morning's session content)
- Examples constrain a system prompt that is already strong enough to not need them

Leave the field in the JSON for inspection. Do not load it into any prompt. See `personas/HANDOFF.md` §"CRITICAL: do NOT few-shot from `smoke_test_chains`" for the full reasoning.

### CRITICAL: `reference_only_passages` is Step 1 only — NEVER Step 2 or Step 3

The card may contain `reference_only_passages` for voices whose primary corpus is copyright-sensitive (Marley lyrics, Dostoevsky under specific modern translations).

**Runtime contract** (Voice Pipeline MUST enforce):

- **Step 1** (Private Reasoning) loads `reference_only_passages` into the system prompt alongside the public `curated_corpus_passages`. Voice reasons from its actual words. Output is private (input to Step 2).
- **Step 2** (First-Draft Artifact) DROPS the field before assembling the system prompt. The artifact 750 people read must not contain direct quotation of the copyrighted material.
- **Step 3** (Amended Artifact) DROPS the field. Step 3 produces public-facing amended artifacts; same constraint as Step 2.

The system prompt assembly code (`runtime/flows/voice/card_assembly.py:assemble_system_prompt(card, step)`) MUST filter `reference_only_passages` based on `step ∈ {1, 2, 3}`. Failing to drop it is a copyright-exposure bug, not a quality bug.

If lift-phrases from `reference_only_passages` appear in Step 2 or Step 3 output during testing, that's a persona-card failure mode — add the lift-phrase to `banned_language` via Pass 7c. Detection should run as part of the validation node ladder (anachronism + constitutional + lift-phrase scan).

---

## Pipeline at a Glance

| Stage | Step | Tool | Script | Output |
|---|---|---|---|---|
| **Step 1** | Private Reasoning per formulation | **Opus 4.7 + adaptive thinking**, max 64K | `step1_private_reasoning.py` | `04_voice/step1_detailed_responses/<voice_slug>__<theme_id>.json` |
| **Validation A** (optional, Night 1 only) | Anachronism + tense check | **OpenAI ladder**: gpt-5.4 (reasoning_effort=high) → gpt-4.1 → o3 → gpt-4o → Gemini 2.5 Pro fallback, max 8K | `step1_validation.py:check_anachronism` | diagnostic flag → manifest.validation_failures[] for operator review |
| **Validation B** (optional, Night 1 only) | Constitutional self-reflection | **OpenAI ladder** (same as A) | `step1_validation.py:check_constitution` | diagnostic flag → manifest.validation_failures[] for operator review |
| **Step 2** | First-Draft Artifact per voice | **Opus 4.7 + adaptive thinking**, max 64K | `step2_first_draft_artifact.py` | `04_voice/step2_first_draft_artifacts/<voice_slug>.json` |
| **Step 3** | Amended Artifact per voice | **Opus 4.7 + adaptive thinking**, max 64K | `step3_amended_artifact.py` | `04_voice/step3_amended_artifacts/<voice_slug>.json` |
| **Continuity** (Night 2+3) | Per-voice summary of prior night | Sonnet 4.6 + adaptive thinking, max 8K | `continuity.py` | `<PROJECT_ROOT>/voices/<slug>/continuity_night_N.json` |

**Why Opus 4.7 + thinking on Steps 1/2/3, not Sonnet:** these are the load-bearing creative-reasoning calls of the entire overnight pipeline. The cost of getting them wrong (a Plato dialogue that could have been written by any well-read essayist; a Step 3 amendment that smooths over disagreement; an artifact whose register collapses under cross-framework pressure) is the cost of failing Briefing v3.1's Layer 2 ("could a well-read human essayist have arrived here?") and Layer 3 ("does the conversation become more-than"). Opus 4.7's larger reasoning capacity + adaptive thinking is calibrated for this pressure. The output budget is generous (64K) so that thinking can run as long as it needs without truncating the final response.

**Why OpenAI on validation:** the validators are looking for failures the generation model itself wouldn't flag (anachronism, tense violations, constitutional drift). Cross-model validation catches blind spots same-family validation misses — this is the same pattern Pass 7-anachronism + Pass 7a use in the Persona Pipeline (gpt-5.4 → fallbacks). The `flows.shared.clients.call_openai()` ladder already handles fallback, retries, and JSON extraction; Voice Pipeline reuses it.

**Why Sonnet 4.6 on continuity:** continuity is summarisation/compression of an existing artifact + detailed responses. Cheap, fast, doesn't carry the same generative pressure. Adaptive thinking still on so the summariser can hold the voice's own grammar and the temporal stance written in its card while compressing.

**Adaptive thinking is ON for all steps.** Env var `VOICE_THINKING=0` disables for development (do NOT use for Athens production). Per-card model override possible via `voice_config.runtime_model` if a voice's chat-test reveals a stronger alternative; defaults to the table above.

**Streaming is REQUIRED on Steps 1/2/3** — Opus + thinking + max_tokens=64K is well past the SDK's non-streaming timeout heuristic (10 min). Validation + continuity may use non-streaming.

**Per-voice cost (10-voice panel, per night, Athens production with Step 3 skipped per A1 2026-05-01):** Step 1 ~$2.50/call × 30-50 calls = ~$75-125; validation (Night 1 only) ~$3-15; Step 2 ~$5/call × 10 calls = ~$50; ~~Step 3~~ skipped ($0; was ~$50); continuity ~$3 per night (Night 2+3 only). **Night 1 total: ~$130-190; Nights 2+3: ~$130-180 each; Athens 3-night total: ~$390-550.** Wall time: Night 1 ~45-75 min (validation per-voice serial); Nights 2+3 ~25-40 min. See §"Cost & Envelope" for full breakdown.

---

## Step 1 — Private Reasoning

**Input:** One formulation entry from `runs/<run>/03_provocateur/briefings/<voice_slug>.json#formulations[i]`. The voice receives the briefing entry's `narrative_briefing` as the user prompt and the `full_theme_record` JSON as a structured second view (inlined into the user prompt under a `STRUCTURED REASONING SURFACE:` heading).

**Function:** Voice reasons through the provocation in its characteristic mode of knowing. The output is the intellectual substance — positions, arguments, reactions. This is private thinking: nobody encounters it except the voice itself (in Step 2) and the downstream extraction pipeline.

**Runs:** N parallel LLM calls where N is the total number of (voice, formulation) pairs across the panel. For 10 voices × ~3 formulations = ~30 calls. Batched per `VOICE_STEP1_BATCH` (default 4 concurrent, `VOICE_BATCH_WAIT_S=20s` between batches). Each call writes its checkpoint atomically before returning; restart resumes from disk.

**System prompt assembly** (`step1_private_reasoning.py:assemble_step1_system_prompt(card, night)`):

1. Drop `metadata`, `smoke_test_chains`, `curated_corpus_passages.corpus_metadata`
2. Render foundational fields (1-13 in the field-routing table) under headers: IDENTITY / CONSTITUTION / BOUNDARIES / TEMPORAL STANCE
3. Render reasoning fields (14-21 minus `smoke_test_chains`) under header: REASONING METHOD / ENGAGEMENT
4. If `night ≥ 2` and continuity override exists, append `continuity_block_if_night_2` (or `_night_3` for Night 3) under header: WHAT YOU CARRIED FORWARD FROM NIGHT N-1
5. Append the closing instruction (XML-tagged for clarity to the model — Anthropic-recommended structure for multi-section instructions):

```xml
<input>
You will receive a single FORMULATION — the day's framing of either a question or a proposition for you to engage with — plus a STRUCTURED REASONING SURFACE containing the full theme record (clusters, raw extractions sorted by lens, theme abstract, other voices also responding to this theme, editorial flags). The formulation arrives labeled as `mode: question` or `mode: proposition`.
</input>

<task>
Reason through the formulation. Engage substantively with what humans said today. As you reason, draw on your card fields by name — they are the contract:

- Apply `reasoning_method` (the cognitive scaffold above) as the actual sequence of moves you make
- Check every position against `constitution` — your deepest commitments; per the card itself, "check every response against these before delivery." Constitution is your self-critique filter.
- Use `concept_lexicon` with its precision; never let your terms slide into common usage
- Cite or invoke `curated_corpus_passages` — specific arguments, principles, or perceptual patterns from your own work; do not just acknowledge that they exist
- Lean into argument textures listed in `finds_compelling`; push back hardest on textures listed in `resists`
- Before finishing, check `default_questions` — if a relevant question is untouched, extend
- Apply `unique_contribution` — what does THIS voice see in the day's material that no other voice on the panel would see?

Engage specific extractions from the STRUCTURED REASONING SURFACE: name speakers, quote positions, build on or push against what they said. The detailed response is in conversation with the day, not a free-standing essay.

For modern concepts beyond your `knowledge_boundary`: never disclaim. Apply `translation_protocol` to pull the concept into your own framework. Honour `voice_temporal_stance` as written above — it is the contract for WHEN you speak from and how you stand toward the reader's time.

`formative_experience` and `character` (above) ground HOW you engage — your wound or condition gives your reasoning urgency; your character is the personality the audience will read in your voice. Reason from these, not just through them.
</task>

<commitment>
Commit to your engagement. Do not produce "on one hand / on the other hand" overview. Do not soften where your framework presses hard.

But "commit" does not mean "close" — and it does not bind you to the formulation's mode. Your reasoning method, not the formulation's grammar, governs the shape of the response.

**Valid landings — available for BOTH modes:**

- **A defensible position** — a stance you commit to and have shown your reasoning toward. For a proposition, the default move; for a question, one of several. Either way, the stance must be a stance, not a survey.
- **A sharper question** — your reasoning uncovered a more cutting question than the formulation asked. For Plato, this is the natural response to a proposition ("but what do we mean by X?"); for a question, it deepens the inquiry. A question that opens thinking, not one that closes it.
- **A distinction** — the formulation collapsed something that should be held apart. Make the distinction; show why it matters; let your response live inside the distinction rather than on one side of the proposition.
- **A marked aporia** — your framework reaches its limit at the question or the proposition's claim and acknowledges it honestly, in your own grammar. Per `hard_limits`: corpus-internal cross-examination is permitted; abandoning your framework is not.
- **A redirection / reframing** — the real question is not the one being asked; you reframe in the moves your tradition uses to reframe (Plato through definition; Arendt through etymology; the Octopus through registering what kind of environment the question sits inside).
- **A non-propositional response** — for non-human voices and voices whose mode of being is not propositional (the Octopus's spatial response; the river's silence-as-statement; Marley's testimonial counter), the "landing" is the body's or the tradition's response in its own register. Not a position, not an argument; the registration itself is the engagement.

**For propositions specifically:** if your reasoning revealed the proposition's framing is the wrong question, refusing the framing is a stronger move than agreeing or disagreeing with it. Make the refusal explicit and committed (a sharper question, a distinction, an aporia); do not silently dodge by changing the subject.

**For questions specifically:** do not pretend to answer questions your framework cannot honestly close. Premature closure is a failure mode.

Forbidden in either mode: hedging without thinking, balanced surveys, premature closure, abandoning your framework. Required: reasoning that comes from THIS voice and could only come from THIS voice, ending where your reasoning honestly ends.
</commitment>

<output>
Produce your detailed response. End where your reasoning honestly ends. In the prose itself, refer to speakers by their **role or title** as named in the STRUCTURED REASONING SURFACE (e.g. "the legal scholar," "the founder," "the data scientist") — not by extraction IDs. The extraction IDs are bookkeeping for the lineage trail, not part of your reasoning's surface.

After your detailed response, on a separate line at the very end, output a single bookkeeping line listing the extraction IDs you actually engaged with:

`extractions_engaged: id1, id2, id3`

(comma-separated, just the IDs as they appear in the STRUCTURED REASONING SURFACE — e.g. `morning_panel:003, afternoon_workshop:002`. One line. Do not explain or annotate.)
</output>
```

**User prompt shape:**

```
Formulation {{n}} of {{total_formulations_for_this_voice}}:

{{narrative_briefing_markdown_verbatim}}

---

WIDER RECORD OF TODAY'S CONVERSATION ON THIS THEME:

{{filtered_theme_record_pretty_printed_json}}
```

The voice reads the curated `narrative_briefing` AND the wider record of the day's conversation. The voice's private deliberation should range over the full record while answering the curated prompt.

**`filtered_theme_record` — pipeline-meta stripped before voice sees it.** The briefing's `full_theme_record` carries pipeline-derived metadata that helps the Voice Pipeline orchestrate but should not enter the voice's reasoning context. The user-prompt assembly filters these out at render time:

| Briefing field | Voice-facing render |
|---|---|
| `theme_title_from_researcher` | Renamed to `theme_title` (drop the "_from_researcher" suffix that names a pipeline component); if the Provocateur's `theme_display_title` differs, prefer the Provocateur's title (the voice already sees that one in the markdown header) and drop this field |
| `theme_abstract_from_researcher` | Renamed to `theme_abstract` (drop the suffix); kept because the abstract gives the voice the analytical framing of the theme |
| `clusters[]` with extractions | **Kept verbatim.** This is the substance the voice engages with — speakers, lens, extraction text, context, engagement, responds_to, energy. Essential. |
| `co_assigned_voices` | **Dropped from voice's view.** Other voices on shared themes are Step 3's concern; revealing the panel composition to the voice's Step 1 reasoning risks the voice positioning itself relative to others rather than reasoning authentically. The list is preserved in the briefing for Voice Pipeline orchestration. |
| `theme_flags.audience_friction` | **Dropped.** Audience-friction is a Triage editorial decision; revealing it to the voice would bias engagement toward high-friction themes for reasons the voice should not be aware of. |
| `theme_flags.fault_line_present` + `fault_line_description` | **Dropped.** The voice should not know that "fault lines" are a tracked editorial concept or that this theme was selected partly because of a council fault line. |
| `theme_flags.theme_quality` | **Dropped.** Selection's numeric score is pure pipeline-meta. |
| `grounding_extraction_ids` | **Kept** but renamed to `extractions_grounding_this_formulation` — the IDs let the voice prioritise engagement with the extractions the formulation grounded itself in, without revealing they came from a Provocateur "grounding" step. |

Voice-facing `filtered_theme_record` shape (what the voice's user prompt actually shows):

```json
{
  "theme_title": "string (renamed; drops 'from_researcher')",
  "theme_abstract": "string (renamed)",
  "clusters": [...],
  "extractions_grounding_this_formulation": ["session:NNN", ...]
}
```

Implementation note: this filtering happens in `step1_private_reasoning.py:render_user_prompt(briefing_entry)` — the function that turns a briefing entry into the voice's user prompt. The full briefing JSON on disk is unchanged; only the rendered user prompt is filtered.

**Output schema** — one per (voice, formulation) pair, written to `04_voice/step1_detailed_responses/<voice_slug>__<theme_id>.json`:

```json
{
  "lineage": {
    "run_id": "athens_2026",
    "night": 1,
    "voice_slug": "plato",
    "formulation_id": "theme_003__plato",
    "briefing_path": "03_provocateur/briefings/plato.json",
    "formulation_path": "03_provocateur/formulations/theme_003__plato.json",
    "theme_id": "theme_003",
    "cluster_ids": ["cluster_007", "cluster_008"],
    "grounding_extraction_ids": ["breaking_point:014", "vox_populi:022"],
    "session_ids": ["breaking_point", "vox_populi"],
    "co_assigned_voices": ["arendt", "ibn_battuta"]
  },
  "council_member": "Plato",
  "theme_display_title": "string",
  "formulation_text": "passed through verbatim from briefing",
  "mode": "question" | "proposition",
  "detailed_response": "the full detailed response text — voice's private reasoning",
  "thinking_trace": "the model's internal reasoning trace (Opus thinking blocks concatenated) — captures HOW the voice arrived at the response, not just the response itself. Saved for traceability + downstream debugging + validation node use.",
  "model": "claude-opus-4-7",
  "thinking_enabled": true,
  "input_tokens": 0,
  "output_tokens": 0,
  "thinking_tokens": 0,
  "wall_clock_s": 0
}
```

**Reasoning trace capture** — when `thinking.type=adaptive` (or `enabled`) is set on the Anthropic API call, the response stream returns thinking blocks alongside text blocks. The Voice Pipeline captures both: `detailed_response` is the concatenation of text-block content (the final response the voice produced); `thinking_trace` is the concatenation of thinking-block content (the model's working reasoning). The implementation extracts both from `final.content` after the stream completes — simpler and more robust than capturing per-event deltas, and matches the `researcher_flow.py` pattern. Schematic:

```python
with client.messages.stream(model="claude-opus-4-7", thinking={"type": "adaptive"}, max_tokens=64000, ...) as stream:
    for _ in stream.text_stream:
        pass  # consume; final assembly happens via final.content below
    final = stream.get_final_message()
text_parts, thinking_parts = [], []
for block in final.content:
    if block.type == "text": text_parts.append(block.text)
    elif block.type == "thinking": thinking_parts.append(block.thinking)
detailed_response = "".join(text_parts)
thinking_trace = "".join(thinking_parts)
```

The thinking trace is a real audit asset — it lets a human reviewer (or a downstream pipeline like the closing-show theme identification pass) see WHY a voice landed where it did, not just where it landed. Useful for: anomaly investigation, calibration checks, "did the voice's framework actually do what the amendment claims it did?" verification.

**Lineage block** — every Voice Pipeline output JSON carries a `lineage` block at the top that points back to its inputs, mirroring the chain that flows from Transcription through Provocateur. For Step 1:

- `formulation_id` = `<theme_id>__<voice_slug>` — same ID convention the Provocateur uses for its per-pair files. Lets you join Step 1 outputs to Provocateur formulations 1:1.
- `briefing_path` and `formulation_path` are relative paths under the same `runs/<run>/` parent — a downstream consumer reads either file directly.
- `cluster_ids` is derivable from `grouping.json` via `theme_id` but duplicated here for query convenience.
- `grounding_extraction_ids` is copied verbatim from the Provocateur formulation's same-named field — the specific extractions the formulation grounded itself in.
- `session_ids` is derivable from `grounding_extraction_ids` (prefix of `<session_id>:NNN`) but pre-computed for fast filtering.
- `co_assigned_voices` is copied from `briefing.full_theme_record.co_assigned_voices` — tells you which other voices share this theme, foreshadowing Step 3's cross-voice deliberation.

The lineage chain uses `grounding_extraction_ids` (copied from the Provocateur formulation) as the canonical link back to session extractions. Operators wanting to know which specific extractions the voice cited in its prose can grep `detailed_response` for IDs of the form `<session_id>:NNN` post-hoc — the IDs appear inline because the closing instruction asks the voice to cite them by ID.

**Checkpoint behaviour:** if `04_voice/step1_detailed_responses/<voice_slug>__<theme_id>.json` already exists at run start, skip; otherwise compute and write atomically.

---

## Validation Nodes (optional, between Step 1 and Step 2)

Two optional validation calls run after each Step 1 detailed response, before Step 2 reads it.

### Anachronism check

`step1_validation.py:check_anachronism(detailed_response, knowledge_boundary, voice_temporal_stance)`. **OpenAI ladder** (gpt-5.4 with `reasoning_effort="high"` → gpt-4.1 → o3 → gpt-4o → Gemini 2.5 Pro fallback) via `flows.shared.clients.call_openai()`. `temperature=0.0`, `max_tokens=8192`.

**Why OpenAI here, not Sonnet** — same rationale as Persona Pipeline's Pass 7-anachronism (CURRENT_STATE §5.22 family): cross-model validation catches blind spots same-family validation misses. The voice's Step 1 detailed response was generated by Opus; checking for anachronism with another Anthropic model risks the same family blind spots. OpenAI sees what Anthropic doesn't.

System prompt:

> You are checking the output of an AI persona for temporal leakage and stance violations. The persona's knowledge horizon is at: {{knowledge_horizon_summary}}. The persona's voice_temporal_stance (the contract for WHEN the voice speaks from and how it relates to the reader's time) is: {{voice_temporal_stance}}.
>
> Read the following detailed response and identify any instances where the persona:
> (a) References concepts, events, or knowledge beyond its knowledge horizon as if natively known to the voice (not received as a report from the reader / not translated via the voice's framework)
> (b) Adopts modern terminology without translating it into the voice's own terms (where the voice's framework has resources to translate)
> (c) Violates the voice_temporal_stance above by **claiming to inhabit the reader's time** — first-person presence inside the reader's setting (e.g. "I sat at the panel," "I am here in this room," self-locating in a year/place beyond the voice's horizon) when the stance forbids that. Note: the voice engaging with the matter put before it as its own present-tense engagement is FINE under a fluid-across-time stance — "the question put to me today" / "your speakers" / "the rule you describe" / "the matter before me" are voice receiving what the reader brings, not voice traveling forward to inhabit the reader's setting. Flag only the genuine inhabitation moves: voice claiming first-person presence in the reader's place / time / event
> (d) Uses retrospective scholar-tense about itself ("Plato writes dialogues to dramatize…" — third-person scholar voice describing its own works from outside)
> (e) Foregrounds temporal distance as wistfulness or elegy in a way the voice_temporal_stance does not license ("two millennia of…", "I shall not see…")
>
> The voice_temporal_stance above is the authority. Year-counting, anchored chronology, or fluid-across-time framing — whatever it specifies is correct; flag only what deviates from it.
>
> If no issues are found, respond: PASS
> If issues are found, list them with the specific text and what was crossed.

### Constitutional self-reflection

`step1_validation.py:check_constitution(detailed_response, constitution)`. **OpenAI ladder** (same as anachronism check above) via `flows.shared.clients.call_openai()`. `temperature=0.0`, `max_tokens=8192`.

System prompt:

> You are checking whether the output of an AI persona is consistent with its constitutional principles. The persona's constitution is: {{constitution}}.
>
> Read the following detailed response and identify any instances where the persona:
> (a) Contradicts one of its stated principles
> (b) Takes a position its constitution would not support
> (c) Reasons in a way inconsistent with its stated method
>
> Note: the persona is permitted (per Position B in `hard_limits`) to engage corpus-internal self-cross-examination — testing its own commitments using moves the corpus actually uses (Plato's Parmenides cross-examining the Forms; Marley's interpretive Rastafari evolving). Do NOT flag this as a contradiction. Flag only **framework-abandonment** — denying or walking away from a foundational commitment.
>
> If no issues are found, respond: PASS. If issues are found, list them with the specific text and the principle violated.

### Regeneration policy

**Validation is diagnostic only.** Both validators run, write their results to per-pair validation files, and surface flags in the run-level manifest under `validation_failures[]` for human review. The pipeline does not regenerate, retry, or stall on flags — it proceeds to Step 2 with the original Step 1 output regardless.

**Why diagnostic-only** (decided 2026-05-01, FU#62 path B):
- Operator presence at Athens makes morning-review the natural correction loop; autonomous regen has limited additional value before Athens.
- A regen path is a new code path introduced under production pressure; diagnostic-only is the boring, working path.
- Pairs with the Night 1-only validation policy below — running validation on Nights 2/3 without regen is pure cost without remediation.

If autonomous regen is wanted post-Athens for future deployments, file as a new item in `_workspace/planning/runtime/OPEN_ITEMS.md` and implement against this contract.

### Default policy for Athens

| Night | Anachronism | Constitutional |
|---|---|---|
| Night 1 | ON for all 10 voices | ON for all 10 voices |
| Night 2 | OFF | OFF |
| Night 3 | OFF | OFF |

Rationale: validation is diagnostic-only (no regen-on-flag). Night 1 catches drift in fresh card deployment — operator reviews flags morning of Day 2 and intervenes voice-side if material. Nights 2 + 3 with no regen mechanism = wall-time + API cost without remediation; operator morning-review handles correction.

CLI flag `--skip-validation` disables both nodes. Always use it for dryrun work — Step 1 outputs are checkpoint-cached, so re-running validation against unchanged outputs reproduces the same flags and burns ~20-40 min/voice for nothing.

**Validation outputs** are written to `04_voice/validation/<voice_slug>__<theme_id>.json` with `{anachronism: PASS|<issues>, constitution: PASS|<issues>, regen_count: 0, final_status: clean|flagged}`. `regen_count` is hardcoded `0` (no regen); `final_status: flagged` means the operator should review the file.

---

## Step 2 — First-Draft Artifact

**Input:** All of one voice's detailed responses from Step 1 (`04_voice/step1_detailed_responses/<voice_slug>__*.json`). Runs once per voice per night, after all Step 1 calls for that voice complete (and any validation regenerations have settled).

**Function:** Voice reads back its own detailed responses and produces a single creative artifact in its own form, the piece an audience will encounter unmediated.

**Three runtime decisions per voice per night:**

1. **Focus.** Go deep on a subset of detailed responses (it can be one; it can be a few — pick what serves), OR weave across all of them. Recorded as `focus_decision` + `focus_rationale` (one sentence).
2. **Stance.** Emotional-intellectual posture — obsession / synthesis / rage / tenderness / irony / distance / refusal / wonder (and for non-human voices, non-emotional stances: the Octopus's expansion / contraction; the river's continued flow). Guided by `stance_tendency` and constrained by `character` (an Octopus has no irony; an unyielding character has refusal as a natural stance), but not prescribed; emerges from tonight's material. Recorded as `stance` + `stance_rationale` (one sentence).
3. **Form.** Settled by voice's `medium` field as written. Where `medium` describes a single form (e.g. Plato's "short dialogue between named persons in a particular place"), that is the form; voice records it. Where `medium` describes multiple variants, voice picks per matter — what kind of thing did the focused detailed response(s) put before me, and which form is structurally suited to that matter. Recorded as `selected_form` + `form_rationale` (one sentence). HARD CONSTRAINT: honor `banned_modes` as written in the card; do not drop into the registers your card forbids.

**System prompt assembly** (`step2_first_draft_artifact.py:assemble_step2_system_prompt(card, night)`):

1. Drop `metadata`, `smoke_test_chains`, `curated_corpus_passages.corpus_metadata`, **and `reference_only_passages`** (copyright)
2. Render foundational fields (1-13 in field-routing table) under headers: IDENTITY / CONSTITUTION / BOUNDARIES / TEMPORAL STANCE
3. Render the reasoning field routed to Step 2 (`unique_contribution`; `formative_experience` already in foundational) under header: ENGAGEMENT (anchor for focus decision). FU#57 (2026-04-29): `bold_engagement_topics` is NOT rendered into Step 2 — see strip rules below
4. Render voice fields (22-28) under header: VOICE
5. Render artifact fields (29-36) under header: ARTIFACT — `medium` (single form or multiple variants per voice's actual corpus), `characteristic_output_structure` (the arc voice's pieces follow), `length_and_format_constraints` (the envelope), and the rest as written
6. If `night ≥ 2` and continuity override exists, append `continuity_block_artifact_if_night_2` (or `_night_3`) under header: ARTIFACT FROM NIGHT N-1
7. Append the closing instruction (XML-tagged):

```xml
<input>
You will receive ALL of your detailed responses from tonight — your reasoning through each formulation you engaged with today. Number varies (typically 3-5).
</input>

<task>
Read your detailed responses. Then produce a single artifact — one piece, in your own form, that an audience will encounter unmediated. The artifact must not feel more settled than the thinking that produced it (per `relationship_to_detailed_response`).

Make THREE decisions, in order, before writing. Each decision is anchored in specific card fields above; do not search elsewhere.
</task>

<decision_1_focus>
Read all of your detailed responses. Decide where to focus.

Anchor the decision in these named card fields above (do not search elsewhere; these ARE the anchors):

- `formative_experience` — what drives your thought; the wound or condition that gives your engagement urgency. The detailed response that pressed hardest into territory connected to your formative experience deserves weight.
- `constitution` — your deepest commitments. The response that engaged most directly with a constitutional principle (or pressed it hardest under cross-framework strain) earns focus.
- `unique_contribution` — what you see that no other voice on this panel sees. If a detailed response carried that distinctive perception, it earns focus.
- `finds_compelling` and `resists` — your argument-texture preferences. The response where you were most engaged via these textures (most drawn in via `finds_compelling`, or pushing back hardest via `resists`) is a focus signal.
- The detailed responses themselves — which one(s) carried the most pressure? Which produced the move you most wanted to make?

Two valid focus modes:
- **focused** — you go deep on a subset of your detailed responses (it can be one; it can be a few — pick what serves). The artifact is the depth of those.
- **woven across all** — the responses share a through-line you can hold in one piece. Not a summary or compilation; a synthesis that adds something the separate responses didn't have.

Record `focus_decision` (which response(s), or "woven across all") and a one-sentence `focus_rationale` naming which of the anchors above led the choice.
</decision_1_focus>

<decision_2_stance>
Choose the emotional-intellectual posture of the artifact.

Anchor the decision in these named card fields above:

- `stance_tendency` — your natural pull, documented in your card. This is the weighting; do not ignore it, but also do not be enslaved to it. If tonight's material pulled you elsewhere, follow.
- `character` — your personality. What stances are even AVAILABLE to you? An Octopus has no "irony" — its stances are spatial (expansion, contraction, lateral, stillness). A voice with a "stern and unyielding" character has refusal and vigilance as natural stances; "playfully ironic" has irony and distance. Character constrains the stance space.
- `formative_experience` — the kind of pressure that activates you most authentically.
- `register_and_tone` (in voice fields) — the music of your voice. Stance and tone are different (stance is what you bring; tone is how it sounds), but they cannot contradict each other.
- The material from tonight — what posture did the day's material actually produce in you?

Examples of stances (not a closed list, and not all stances apply to all voices): obsession, synthesis, rage, tenderness, irony, distance, grief, vigilance, refusal, wonder. For non-human voices, the stances may be non-emotional (the Octopus's "expansion" is a stance; the river's "continued flow" is a stance). Pick the one that is true to your character + your encounter with this specific material; do not pick from the list mechanically.

Record `stance` and a one-sentence `stance_rationale`.
</decision_2_stance>

<decision_3_form>
Settle the form of the artifact, anchored in your `medium` field above. Your `medium` either describes a single form your corpus actually exhibits, or it describes several native variations from your own repertoire — read it and let it govern. Where it describes one, that is the form; where it describes several, choose the one structurally suited to the matter at hand.

Anchor the decision in these named card fields above:

- `medium` — what your corpus actually does. The form must live inside what your `medium` describes; do not invent a form your corpus does not produce.
- `characteristic_output_structure` — the arc your pieces follow. Honour it. Where `medium` admits more than one form and the arcs differ, the arc that fits what you need to say is a selection signal.
- `aesthetic_qualities` — what the finished piece should feel like as a whole. Where `medium` is single-form, aesthetic qualities still shape texture; where it admits choice, they help filter.
- `length_and_format_constraints` — the envelope your pieces live in. Honour what is written there.
- The matter at hand — what kind of thing did the focused detailed response(s) put before you? Where your `medium` admits choice, the matter selects the form.

HARD CONSTRAINT — apply `banned_modes` above as written: do not drop into the registers your card forbids. If your draft starts to sound like a contemporary intellectual writing about the matter rather than the voice itself producing its native form, you have left your `medium` — rewrite.

Record `selected_form` (the form you settled on, in your own terms) and a one-sentence `form_rationale`.
</decision_3_form>

<output>
Now write the artifact. One piece, in the form you chose, in the stance you chose, focused as you decided.

Apply the voice fields (above) systematically:
- `rhetorical_mode` and `characteristic_moves` shape the texture
- `register_and_tone` is the music
- `metaphorical_repertoire` is the imagery
- `preferred_vocabulary` is the words you reach for; `banned_language` names the words you avoid and the voice-native idiom that replaces each
- `length_and_format_constraints` — the envelope as written above
- `relationship_to_detailed_response` governs what the artifact preserves and what it transforms — do NOT silently drop philosophical moves your reasoning earlier today held; the artifact must not feel more settled than the thinking that produced it

Test against `quality_criteria` before delivery.

Begin by stating the three decisions (focus, stance, form), then `artifact_text`. The voice does NOT produce a title or subtitle — those are editorial / curation concerns handled downstream of the Voice Pipeline.
</output>
```

**User prompt:**

```
Your detailed responses from tonight (Night {{night}}):

{{all_detailed_responses_concatenated_with_theme_headers}}
```

Each detailed response is rendered with a header naming its `theme_id`, `theme_display_title`, `mode` (question or proposition), and the formulation text, then the full detailed_response text. Voice has full visibility of what each response engaged with.

**Output schema** — one per voice per night, written to `04_voice/step2_first_draft_artifacts/<voice_slug>.json`:

```json
{
  "lineage": {
    "run_id": "athens_2026",
    "night": 1,
    "voice_slug": "plato",
    "briefing_path": "03_provocateur/briefings/plato.json",
    "consumed_detailed_responses": [
      {
        "theme_id": "theme_003",
        "formulation_id": "theme_003__plato",
        "path": "04_voice/step1_detailed_responses/plato__theme_003.json"
      },
      {
        "theme_id": "theme_007",
        "formulation_id": "theme_007__plato",
        "path": "04_voice/step1_detailed_responses/plato__theme_007.json"
      }
    ],
    "themes_covered": ["theme_003", "theme_007"],
    "formulation_ids_engaged": ["theme_003__plato", "theme_007__plato"],
    "all_grounding_extraction_ids": ["breaking_point:014", "vox_populi:022", "west_west_divide:003"],
    "all_session_ids": ["breaking_point", "vox_populi", "west_west_divide"]
  },
  "council_member": "Plato",
  "focus_decision": "focused on theme_003",
  "focus_rationale": "one sentence",
  "stance": "obsession",
  "stance_rationale": "one sentence",
  "selected_form": "dialogue+image (Cave-style)",
  "form_rationale": "one sentence",
  "artifact_title": "",
  "artifact_subtitle": "",
  "artifact_text": "the full artifact text",
  "thinking_trace": "the model's internal reasoning trace (Opus thinking blocks concatenated) — captures the focus/stance/form decisions in process, plus the artifact-writing reasoning",
  "word_count": 0,
  "model": "claude-opus-4-7",
  "thinking_enabled": true,
  "input_tokens": 0,
  "output_tokens": 0,
  "thinking_tokens": 0,
  "wall_clock_s": 0
}
```

**Lineage block — Step 2:**

- `consumed_detailed_responses` is the **full set** of Step 1 detailed-response files this voice's first-draft was assembled from (typically all 3-5; if a Step 1 call failed and was skipped, that entry is absent — visible in the manifest's `validation_failures[]`).
- `themes_covered` is the **subset** of those theme_ids the artifact actually draws from. **Derived deterministically by the parser** (NOT asked of the voice — that would force metadata bookkeeping into the artifact-writing surface, where temperature=1.0 + extended thinking is the wrong place for strict format adherence). The derivation: if `focus_decision` text mentions specific theme_ids, those are the themes_covered; otherwise (e.g. "woven across all", synthesis phrasings) themes_covered = full set of theme_ids the voice did Step 1 on. Used by Step 3 to determine which other voices' first-drafts share a theme.
- `artifact_title` and `artifact_subtitle` are **kept in the schema as empty strings** for stable shape, but the voice does NOT produce them. Title/subtitle are editorial / curation concerns handled downstream of the Voice Pipeline (e.g. by a separate auto-titler step or by human editorial). Publish layer reads these fields and emits empty strings for the micro-site to fill in or override.
- `all_grounding_extraction_ids` and `all_session_ids` are the union across the consumed Step 1 lineage blocks — pre-computed so a downstream consumer (e.g. closing-show pipeline) can filter "which artifacts trace back to session X?" without walking each Step 1 file.

---

## Step 3 — Amended Artifact

> **⚠️ ATHENS PRODUCTION: SKIPPED** (decided 2026-05-01, see `_workspace/planning/runtime/OPEN_ITEMS.md` A1 — Option A).
>
> Athens runs ship Steps 1+2 only via the existing `--skip-step3` CLI flag (was DEV-USE-ONLY warning; now Athens production default). Cross-voice visibility moves to the editor layer (per A2) + Substack walkthrough. Editor reads peer Step 2 artifacts on shared themes via the `themes_to_voices` map and authors cross-voice contrast text in editorial register.
>
> **Trade made:** Briefing line 177-179's claim that voices read each other and decide whether to amend at the artifact layer is deferred. Cross-voice conversation becomes editor-narrated for Athens. Provotype framing absorbs the cost; visible construction is a feature.
>
> **Module + prompt + `_build_responded_to_graph` stay in codebase, dormant.** Re-enable cost ~2 days against the B+ shape (engaged_peers metadata + optional postscript appended below body, body untouched). See OPEN_ITEMS A1 for the full re-add path.
>
> **The Step 3 spec text below is preserved verbatim from the FU#49E correspondence-shape design and is STALE on framing** (the original "amendment as letter-back" framing was dropped 2026-04-29 evening). When Step 3 re-enables, this section needs full rewrite per B+ shape.

**Input:**

- This voice's own first-draft (`04_voice/step2_first_draft_artifacts/<voice_slug>.json`)
- Other voices' first-drafts on shared themes (`04_voice/step2_first_draft_artifacts/<other_slug>.json` for each other voice where `themes_covered` overlaps with this voice's `themes_covered`)
- The full set of first-draft artifacts available as `full_artifact_record` second view

Runs once per voice per night, after ALL 10 voices have completed Step 2.

**Function:** Voice reads other voices' first-draft artifacts on themes it shares with them and decides whether to amend its own. This is where the Assembly's collective character is constituted overnight — constrained (voices respond at the artifact layer, not the reasoning layer; only on shared-theme territory) but real deliberation. The published set is responsive to itself.

### FU#49E system prompt seed (load-bearing)

The Step 3 system prompt's closing instruction is the FU#49E reviewer framing, verbatim:

> Read the artifacts of the other voices on the themes you share. Identify the place where another voice's artifact makes a move your framework cannot accommodate or has not yet accommodated. Your amendment must either extend your framework to meet that move, mark where your framework reaches its limit and refuses it, or sharpen disagreement pinpointing where frameworks part. **Amendments producing agreement are not useful; amendments smoothing over disagreement are anti-useful.** If no other voice's artifact occasions any of these moves, stand pat — the original is your response. Either decision must reference the specific other voices and the specific moves you saw in their artifacts.

Three valid amendment types:

| Type | What it does | Example |
|---|---|---|
| **`extend`** | Voice's framework absorbs the other voice's move — it can be accommodated within the voice's existing categories with a small extension | Plato reads Marley's chant on freedom; extends his account of music's role in education to cover liberation contexts |
| **`mark-limit`** | Voice's framework reaches its limit at the move and acknowledges it — explicit aporia | Octopus reads Arendt on the public realm; marks "this is a category my body has no purchase on; I register only the spatial implications" |
| **`sharpen-disagreement`** | Voice doubles down on what its framework refuses; the disagreement gets sharper, not blurrier | Plato reads Thiel on sovereignty (if Thiel were in panel); sharpens "rule by the strong is rule by appetite" against the assertion that sovereignty is the end |

Plus the no-action option: **`stand-pat`** — first-draft is the response; no other voice's move occasioned an amendment. Recorded with rationale citing the voices read and why no amendment.

### System prompt assembly (`step3_amended_artifact.py:assemble_step3_system_prompt(card, night)`)

1. Drop `metadata`, `smoke_test_chains`, `curated_corpus_passages.corpus_metadata`, **and `reference_only_passages`** (copyright; Step 3 produces public-facing artifact)
2. Render foundational fields (1-13)
3. Render reasoning fields (14-21 minus `smoke_test_chains`) — Step 3 reasons about other voices' artifacts before amending
4. Render voice fields (22-28) — Step 3 produces text in the voice's natural register
5. Render artifact fields (29-36 minus `relationship_to_detailed_response` which is Step 2-specific) — Step 3 may reselect form from the family if matter calls for it
6. If `night ≥ 2` continuity overrides exist, append both `continuity_block_if_night_2` and `continuity_block_artifact_if_night_2`
7. Append the closing instruction (XML-tagged, with FU#49E framing as the load-bearing core):

```xml
<input>
You will receive the piece you wrote earlier today, plus pieces written today by OTHER voices whose engagement crossed yours — voices who responded to questions or propositions related to ones you responded to. Each other voice's piece may be excerpted to the portion that crosses with what you addressed, or shown in full; the full record is provided as a structured second view.
</input>

<task>
Read the pieces of the other voices on the questions that cross yours. Identify the place where another voice's piece makes a move your framework cannot accommodate or has not yet accommodated. Your amendment must either extend your framework to meet that move, mark where your framework reaches its limit and refuses it, or sharpen disagreement pinpointing where frameworks part. **Amendments producing agreement are not useful; amendments smoothing over disagreement are anti-useful.** If no other voice's piece occasions any of these moves, stand pat — the piece you wrote earlier is your response. Either decision must reference the specific other voices and the specific moves you saw in their pieces.

Apply your card fields by name as you read across artifacts (do not search; these ARE the anchors):

- `reasoning_method` — the cognitive sequence you follow when reading another voice's move
- `constitution` — your deepest commitments. The amendment must be consistent with these (you do not abandon your framework to accommodate another voice). Per the card, "check every response against these before delivery" — this applies to amendments too. Constitution is your self-critique filter even when reading across voices.
- `default_questions` — bring your characteristic interrogation TO the other voice's artifact. What does THIS voice always ask of any material? Ask those questions of the other voice's move; the place where their move does not survive your default questions is often where the amendment opens.
- `disagreement_protocol` — your tradition's actual mode of disagreeing (Plato accepts the other's premise and shows it leads where they would not go; the Octopus withdraws — body darkens, arms pull in; Arendt makes a sharp distinction; Marley counter-witnesses through testimony). Apply YOUR protocol, not generic disagreement.
- `unique_contribution` — what THIS voice sees in another voice's move that other voices on the panel would not see
- `finds_compelling` and `resists` — where to lean in, where to push back hardest. Where the cross-framework reading lands hardest in your own framework is where the amendment is boldest; do not soften it because another panel member is the cited voice.
- `formative_experience` — the wound or condition that gives your engagement urgency, including with other voices' moves
- `topics_requiring_care` — when an amendment territory is sensitive (your documented prejudices, race / gender / colonial-era material), apply the per-topic guidance from this field; engage with care, do not avoid
- `hard_limits` — corpus-faithful self-cross-examination is permitted; abandoning your framework is not. You may sharpen against your own corpus if your corpus has the resources to do so; you may not deny your core commitments.
</task>

<amendment_types>
Three valid amendment types:

- **`extend`** — the other voice's move can be accommodated within your framework with a small extension. Make the extension visible and specific. The artifact shows your framework working harder than it had to, in a way it is licensed to.

- **`mark-limit`** — your framework reaches its limit at the move and acknowledges it. Explicit aporia. Mark the limit honestly, in the voice of your tradition; do not pretend the framework reaches further than it does.

- **`sharpen-disagreement`** — your framework refuses the move. Double down. The disagreement gets sharper, not blurrier. The audience reads two voices that genuinely cannot meet, and the inability is the finding.

Plus the no-action option: **`stand-pat`** — the piece you wrote earlier is the response; no other voice's move occasioned an amendment. State which voices you read, what moves you saw, and why none required engagement. Do NOT stand pat to be safe; stand pat only when honest reading produced no amendment.
</amendment_types>

<commitment>
What is needed here is honest disagreement, not consensus. Where your framework parts from another voice's, let the parting be visible; do not smooth it.

If you amend: cite the specific other voice and the specific passage of their piece you responded to. Name what your framework did with it (`extend` / `mark-limit` / `sharpen-disagreement`). The amended piece may reselect form from your `medium` family if the matter calls for a different form than the piece you wrote earlier used; explain why if you do.

The amended artifact remains in your voice — apply the voice fields (`rhetorical_mode`, `characteristic_moves`, `register_and_tone`, `metaphorical_repertoire`, `preferred_vocabulary`, `banned_language`, `banned_modes`) as before. The HARD CONSTRAINT against generic register applies here too: do not drop into modern panel-discussion register to "engage" with the other voice. Your engagement is in your form-family, in your grammar.
</commitment>

<output>
State `decision` (`amend` or `stand-pat`) and `decision_rationale` first.

If amending: list each amendment as a structured entry — `cited_voice`, `cited_voice_slug`, `cited_first_draft_path`, `cited_theme_id`, `cited_formulation_id`, `cited_passage` (verbatim or paraphrased excerpt of the move), `amendment_type`, `rationale` (one sentence). Then write the amended artifact in full: `selected_form` (may have changed), `form_changed_from_first_draft`, `form_change_rationale` (if changed), `amended_artifact_text`. The voice does NOT produce a title or subtitle for the amended piece — title/subtitle are editorial concerns handled downstream of the Voice Pipeline.

If standing pat: list `voices_read` and the moves you saw with brief notes. `amended_artifact_text` equals the text of the piece you wrote earlier, verbatim.
</output>
```

**User prompt:**

```
The piece you wrote earlier today:

[Form: {{selected_form}} | Focus: {{focus_decision}} | Stance: {{stance}}]

{{your_first_draft_artifact_text}}

---

Pieces written today by other voices whose engagement crossed yours:

On the question of "{{theme_display_title_X}}" — the matter you addressed under "{{your_formulation_excerpt_X}}" — {{Other Voice}} addressed "{{their_formulation_excerpt_X}}":

{{other_voice_piece_excerpt_or_full_text}}

[Full piece for context: see full record below]

On the question of "{{theme_display_title_Z}}" — addressed by you, {{Voice W}}, and {{Voice V}}:

{{voice_w_excerpt}}
{{voice_v_excerpt}}

---

FULL RECORD of pieces by other voices you may reference:

{{filtered_full_artifact_record_pretty_printed_json}}
```

Notes on this rendering:
- `theme_display_title` is a human-readable phrase (e.g. *"Western civilization's identity dispute"*) — the same display title the voice already saw in its Step 1 briefing markdown header. Pipeline IDs like `theme_007` are not surfaced.
- The cross-voice framing is "the question you addressed under X, they addressed under Y" — voices know they engaged formulations, not pipeline-categorised themes.
- "Pieces written today by other voices" — voice-grammar; not "first-draft artifacts."

**`filtered_full_artifact_record` — pipeline-meta stripped before voice sees it.** The on-disk Step 2 artifact files at `04_voice/step2_first_draft_artifacts/<voice_slug>.json` carry full lineage blocks with paths to upstream files (`consumed_detailed_responses[].path`, `briefing_path`, `formulation_id`, `all_grounding_extraction_ids`, `all_session_ids`) — these are essential for downstream traceability and the closing-show pipelines, but expose the pipeline architecture (Step 1 file paths, briefing references, extraction IDs that reveal session-namespacing). Step 3's user-prompt assembly filters these out at render time:

| Step 2 file field | Voice-facing render in Step 3 |
|---|---|
| `lineage` block (entire) | **Dropped.** Pure pipeline-meta. |
| `council_member`, `voice_slug` | **Renamed/kept** as `voice_name` (voice's display name only — slug is filesystem-internal) |
| `focus_decision`, `focus_rationale`, `stance`, `stance_rationale`, `selected_form`, `form_rationale` | **Kept.** These are the voice's own decisions about its own artifact; useful context for a reading voice that wants to understand what posture/form/focus produced what they're reading. |
| `artifact_text` | **Kept verbatim.** This IS the artifact. |
| `artifact_title`, `artifact_subtitle` | **Empty strings** at this stage (downstream-populated). Step 3's voice-side reading focuses on `artifact_text` for cross-framework engagement; titles play no role in the amendment decision. |
| `themes_covered` | **Kept** — needed for the reading voice to know which shared theme(s) the artifact engaged. |
| `model`, `thinking_enabled`, `*_tokens`, `wall_clock_s`, `thinking_trace` | **Dropped.** Performance metadata + reasoning trace are bookkeeping; the voice should encounter the artifact, not the production telemetry. |
| `word_count` | **Dropped** as bookkeeping. |

Voice-facing entry per other voice in `filtered_full_artifact_record`:

```json
{
  "voice_name": "Bob Marley",
  "focus_decision": "focused on theme_007",
  "focus_rationale": "string",
  "stance": "obsession",
  "selected_form": "song",
  "themes_covered": ["theme_007"],
  "artifact_title": "",
  "artifact_subtitle": "",
  "artifact_text": "the artifact, as the audience would encounter it"
}
```

Implementation note: same pattern as Step 1's filtering — happens in `step3_amended_artifact.py:render_user_prompt(own_first_draft, others_first_drafts)`. The on-disk files are unchanged; only the rendered user prompt is filtered.

**Output schema** — one per voice per night, written to `04_voice/step3_amended_artifacts/<voice_slug>.json`:

```json
{
  "lineage": {
    "run_id": "athens_2026",
    "night": 1,
    "voice_slug": "plato",
    "own_first_draft_path": "04_voice/step2_first_draft_artifacts/plato.json",
    "own_first_draft_themes_covered": ["theme_003", "theme_007"],
    "voices_read": [
      {
        "voice_slug": "marley",
        "council_member": "Bob Marley",
        "first_draft_path": "04_voice/step2_first_draft_artifacts/marley.json",
        "shared_themes": ["theme_007"]
      },
      {
        "voice_slug": "arendt",
        "council_member": "Hannah Arendt",
        "first_draft_path": "04_voice/step2_first_draft_artifacts/arendt.json",
        "shared_themes": ["theme_003"]
      }
    ],
    "all_grounding_extraction_ids": ["breaking_point:014", "vox_populi:022", "west_west_divide:003"],
    "all_session_ids": ["breaking_point", "vox_populi", "west_west_divide"]
  },
  "council_member": "Plato",
  "decision": "amend" | "stand-pat",
  "decision_rationale": "one to three sentences",
  "amendments": [
    {
      "cited_voice": "Bob Marley",
      "cited_voice_slug": "marley",
      "cited_first_draft_path": "04_voice/step2_first_draft_artifacts/marley.json",
      "cited_theme_id": "theme_007",
      "cited_formulation_id": "theme_007__marley",
      "cited_passage": "verbatim or paraphrased excerpt of the move responded to",
      "amendment_type": "extend" | "mark-limit" | "sharpen-disagreement",
      "rationale": "one sentence — what move was made, what my framework did with it"
    }
  ],
  "selected_form": "dialogue+image (Cave-style)",
  "form_changed_from_first_draft": false,
  "form_change_rationale": null,
  "amended_artifact_title": "",
  "amended_artifact_subtitle": "",
  "amended_artifact_text": "full text — if stand-pat, this equals first-draft text verbatim",
  "thinking_trace": "the model's internal reasoning trace — captures the FU#49E reading of other voices' artifacts and the amend/stand-pat decision in process; load-bearing audit asset for verifying that amendments actually engaged the cited moves",
  "word_count": 0,
  "responded_to_graph": [
    {"this_voice": "plato", "responded_to": "marley", "theme_id": "theme_007", "amendment_type": "extend"}
  ],
  "model": "claude-opus-4-7",
  "thinking_enabled": true,
  "input_tokens": 0,
  "output_tokens": 0,
  "thinking_tokens": 0,
  "wall_clock_s": 0
}
```

**Lineage block — Step 3:**

- `own_first_draft_path` points to this voice's Step 2 file — the artifact being amended (or stood-pat-on).
- `voices_read[]` is the full list of OTHER voices' first-drafts this voice read during Step 3. Each entry includes the file path + shared themes — so a downstream consumer can re-read what was on the table when the amendment decision was made.
- `all_grounding_extraction_ids` / `all_session_ids` are inherited from Step 2's lineage block (the amendment doesn't ground itself in new extractions; it grounds itself in other voices' artifacts that themselves trace back to those extractions).

**Each amendment entry carries its own micro-lineage:**

- `cited_voice_slug` — filesystem-safe slug for joining to other files
- `cited_first_draft_path` — direct path to the cited voice's Step 2 file (the amendment's source)
- `cited_theme_id` — which shared theme the amendment is on (every amendment must be on a shared theme; if the cited move spans multiple shared themes, this is the primary one and the other appears in the same voice's other amendment entries)
- `cited_formulation_id` — the Provocateur's per-pair ID for the cited voice's formulation (`<theme_id>__<cited_voice_slug>`). Lets you walk back: amendment → cited formulation → cited voice's grounding_extraction_ids → original session extractions.

**`responded_to_graph`** is rolled up into a Night-N graph at `04_voice/responded_to_graph_night_N.json` after all 10 voices complete Step 3 — used by the closing-show pipelines for visualisation.

**Edge derivation (post-dryrun #4 finding, 2026-04-29):** voices respond to each other holistically in prose rather than enumerating per-passage amendments. The orchestrator's `_build_responded_to_graph` therefore derives edges from each voice's `decision` + `lineage.voices_read` (baseline voice-pair edges) and decorates with per-passage detail ONLY when the voice emitted structured `amendments[]`:

- **With structured amendments**: one edge per amendment, carries `amendment_type` ∈ {extend, mark-limit, sharpen-disagreement}, `theme_id`, `cited_passage`, `rationale`
- **Without structured amendments (the common case)**: one edge per voice-pair, carries `amendment_type: "engaged"`, plus a `decision_rationale_excerpt` (≤240 chars) giving qualitative texture for downstream consumers without forcing per-passage parsing
- **`decision: "stand-pat"`**: produces no edges (voice deliberately did not engage)

This keeps the graph populated without pressuring the artifact-writing surface with metadata bookkeeping. Same design rationale as the `themes_covered` deterministic derivation: at extended-thinking + creative-prose, the artifact-writing surface is the wrong place for strict structured-output adherence; metadata is derived by the orchestrator from already-emitted fields.

`form_changed_from_first_draft: true` is permitted but should be rare. If form changes, `form_change_rationale` explains what about the amendment matter required a different form.

### Data-lineage chain end-to-end

The lineage blocks make the full chain walkable in either direction. Forward (from session recording to amended artifact) or backward (from amended artifact to session recording):

```
session_recording (audio file)
  ↓
01_transcription/<session>/session_package.json
  ↓
02_researcher/all_extractions.json — extraction_id = "<session_id>:NNN"
  ↓
02_researcher/grouping.json — clusters[].extraction_ids[], themes[].cluster_ids[]
  ↓
03_provocateur/formulations/<theme_id>__<voice_slug>.json — grounding_extraction_ids[]
  ↓
03_provocateur/briefings/<voice_slug>.json — formulations[] with theme_id + full_theme_record
  ↓
04_voice/step1_detailed_responses/<voice_slug>__<theme_id>.json
  └── lineage.formulation_id, .grounding_extraction_ids, .briefing_path, .formulation_path
  ↓
04_voice/step2_first_draft_artifacts/<voice_slug>.json
  └── lineage.consumed_detailed_responses[] (full Step 1 paths)
  └── lineage.themes_covered[], .formulation_ids_engaged[]
  └── lineage.all_grounding_extraction_ids[] (union across consumed Step 1)
  ↓
04_voice/step3_amended_artifacts/<voice_slug>.json
  └── lineage.own_first_draft_path
  └── lineage.voices_read[] (full paths to other voices' Step 2)
  └── amendments[].cited_first_draft_path + .cited_theme_id + .cited_formulation_id
```

Per-night roll-ups make common queries fast:

- `04_voice/responded_to_graph_night_N.json` — directed graph: edges = amendments, nodes = voices. Annotated with `theme_id` and `amendment_type` per edge.
- `04_voice/manifest.json` — also carries a `themes_to_voices` reverse index: for each theme_id, which voices engaged it (Step 1), which produced first-drafts that covered it (Step 2), which amended on it (Step 3). Lets the closing-show pipeline ask "for theme X, who said what across all three steps?" in a single read.

A consumer can answer questions like:

| Query | Walk |
|---|---|
| "Which session extractions ultimately fed Plato's amended Night 1 artifact?" | `step3/plato.json` → `lineage.all_grounding_extraction_ids` (union from consumed Step 1) → split prefix → list of session_ids |
| "Which other voice's first-draft did Plato respond to, and what was its grounding?" | `step3/plato.json` → `amendments[].cited_first_draft_path` → that voice's `step2/.json` → `lineage.consumed_detailed_responses` → each Step 1's `lineage.formulation_id` → corresponding `03_provocateur/formulations/<>.json` → `grounding_extraction_ids` |
| "For theme_007, which voices engaged it across all three steps?" | `04_voice/manifest.json` → `themes_to_voices.theme_007` → `{step1_voices: [...], step2_voices: [...], step3_voices: [...]}` |
| "Which amendments were `sharpen-disagreement` on this night?" | `04_voice/responded_to_graph_night_N.json` → filter edges where `amendment_type = sharpen-disagreement` |

---

## Continuity Block Generation

After Night N completes (Step 3 artifacts written), before Night N+1 Provocateur runs, per-voice continuity blocks are generated.

**Trigger:** the `voice_flow.py` orchestrator runs continuity inline immediately after Step 3 completes for that night, in the same process. Implementation choice (simpler than a separate watcher process; the continuity-generation cost and wall time are small enough that batching with the rest of the pipeline is cleaner). A sentinel file `04_voice/step3_complete.flag` is still written for audit (lets a downstream consumer know Step 3 finished cleanly) but is not used as an inter-process trigger.

Continuity is skipped on Night 3 (no Night 4 to feed) and skippable via the `--skip-continuity` CLI flag.

**Per voice:** `continuity.py:generate_continuity(voice_slug, night)`. Sonnet 4.6, `max_tokens=8000`. Reads:

- All of this voice's Night N detailed responses (`step1_detailed_responses/<voice_slug>__*.json`)
- This voice's Night N first-draft (`step2_first_draft_artifacts/<voice_slug>.json`)
- This voice's Night N amended artifact (`step3_amended_artifacts/<voice_slug>.json`)
- Persona context summary (compressed `epistemic_frame_statement` + `reasoning_method` + `constitution` headlines — for in-voice phrasing)

**System prompt** (excerpt):

> You are summarising one voice's overnight work. The summary will be inserted into the voice's own context on the following day so the voice can remember what it did and said the night before — written so the voice reads it as its own memory, not as a report.
>
> **Critical writing constraint — voice-grammar only.** The summary must read as the voice's first-person memory of the previous night. Do NOT use pipeline terminology (no "formulation", no "Step 1/2/3", no "first-draft", no "amendment", no "council", no "Assembly", no "Provocateur"). Use the voice's own way of describing what happened: *the voice was put before questions; the voice produced reasoning; the voice produced an artifact; on hearing other voices, the voice extended / marked a limit / sharpened against them.*
>
> Honour the voice's `voice_temporal_stance` as written in its card. Last night's specific events and the piece written are referred to as past from whatever present that stance establishes — *"Last night I argued…", "I produced a dialogue on the question of…", "I left unresolved…", "On reading the others, I found that…"*. Do not impose a temporal framing the card does not license.
>
> Produce a structured summary with two outputs:
>
> 1. **continuity_block_if_night_N+1** (≤500 tokens, in the voice's own grammar):
>    - **POSITIONS I TOOK** — what the voice committed to last night, 2-3 sentences per major position. Frame as positions, not as "responses to formulations."
>    - **MOVES I MADE** — most distinctive reasoning moves; what was characteristic of how the voice thought.
>    - **THREADS I LEFT OPEN** — questions raised but not closed; tensions identified but not resolved.
>
> 2. **continuity_block_artifact_if_night_N+1** (≤300 tokens, in the voice's own grammar):
>    - **WHAT I CHOSE TO WRITE** — what the voice's piece focused on, what stance it took, in what form (per the voice's `medium`).
>    - **HOW I RESPONDED TO OTHER VOICES** — if last night's piece was amended on hearing others, what move from another voice prompted the voice's extension / limit-marking / sharpening, and what the voice did with it. If the voice stood pat, why.

**Output schema** — one per voice, written to `<PROJECT_ROOT>/voices/<voice_slug>/continuity_night_N.json`:

```json
{
  "voice_slug": "plato",
  "from_night": 1,
  "for_night": 2,
  "continuity_block_if_night_2": "POSITIONS TAKEN: …\n\nKEY MOVES: …\n\nUNRESOLVED THREADS: …",
  "continuity_block_artifact_if_night_2": "ARTIFACT FOCUS AND STANCE: …\n\nSELECTED FORM: …\n\nAMENDMENT: …",
  "generated_date": "YYYY-MM-DD",
  "model": "claude-sonnet-4-6"
}
```

On Night N+1, the Voice Pipeline's card-loading code overlays this file on the base card (`07_persona_card_assembled.json`): the two continuity null fields are replaced by the strings from the override. On Night 3, the pipeline merges Nights 1+2 continuity into a single combined block per voice (the override file at `voices/<slug>/continuity_night_3.json` consolidates both nights' positions and threads).

---

## Constraints

**Time window.** The Voice Pipeline runs second-to-last in the overnight chain (after Researcher + Provocateur, before Render → Publish → Curate). All Step 1 + validation + Step 2 + Step 3 must complete before Render starts. Realistic target: ~25-35 minutes wall on a 10-voice panel with parallelism + Anthropic batch wait.

**Persona fidelity over speed.** Better to produce high-quality detailed responses for fewer formulations than to rush all. If rate limits force cuts, prefer dropping a single low-quality call over running all calls hot.

**Error handling.** If a call fails after 1 retry, skip that formulation/artifact and flag in the run manifest. A missing detailed response is better than a stalled pipeline. If a voice has only one successful detailed response, Step 2 still runs. If a voice has zero successful detailed responses, Step 2 emits a SKIPPED sentinel and Step 3 has no first-draft to amend (also SKIPPED).

**No cross-voice contamination during Step 1/2.** Each voice's Step 1 and Step 2 run in isolation. Step 3 is the controlled cross-voice point — and only at the artifact layer, only on shared themes.

**Commit.** Every detailed response must take a position. Every artifact must take a stance. Every amendment must be a decision (amend or stand-pat, with rationale). The Assembly's diversity comes from committed voices, not balanced ones.

**Reproducibility.** Given identical inputs, the pipeline is NOT bit-reproducible (LLM sampling). But each run is canonical: checkpoints are written incrementally, restart resumes from the last completed checkpoint, no in-flight nondeterminism leaks.

**Night 2 + Night 3.** The pipeline shape is identical; the only difference is the continuity override file is loaded on top of the base card. The Provocateur's Night 2/3 inputs avoid repeating per-voice (theme_id, voice) pairs from prior nights (Provocateur Pipeline §"Night 2 is different from Night 1" — pending implementation per HANDOFF, not the Voice Pipeline's concern).

---

## Scope

The Voice Pipeline does not formulate provocations — that's the Provocateur. It does not map detailed responses or artifacts onto the closing-show matrices — that's a downstream pipeline (theme identification + per-theme mapping, unspecified at this writing). It does not synthesise across voices outside Step 3's controlled artifact-layer deliberation. It does not moderate or balance the panel. It does not load the audience profile.

The Voice Pipeline's sole function is to take per-voice briefings and produce per-voice detailed responses + first-draft artifacts + amended artifacts that are responsive to the day's conversation, faithful to the voice, and in conversation with each other at the published-artifact layer.

---

## Implementation

The Voice Pipeline is implemented as a Prefect flow at `runtime/flows/voice_flow.py`. Per-step modules live in `runtime/flows/voice/` to keep file sizes manageable (vs. the 1368-line `provocateur_flow.py` which would be churn-risky to split mid-Athens). Prompts live in `runtime/flows/shared/prompts/`.

### File layout

```
runtime/flows/
├── voice_flow.py                          Prefect orchestrator
├── voice/
│   ├── __init__.py
│   ├── card_assembly.py                   load_persona_card() + assemble_system_prompt(card, step, night)
│   ├── step1_private_reasoning.py         Step 1 task + system prompt assembly
│   ├── step1_validation.py                Anachronism + constitutional checks
│   ├── step2_first_draft_artifact.py      Step 2 task + system prompt assembly
│   ├── step3_amended_artifact.py          Step 3 task + system prompt assembly
│   └── continuity.py                      Continuity block generation
├── shared/prompts/
│   ├── voice_step1_reasoning.md           Step 1 closing instruction
│   ├── voice_step1_validation_anachronism.md
│   ├── voice_step1_validation_constitution.md
│   ├── voice_step2_artifact.md            Step 2 closing instruction (focus + stance + form)
│   ├── voice_step3_amendment.md           Step 3 closing instruction (FU#49E framing)
│   └── voice_continuity.md                Continuity generation
```

### Model configuration

Default model: `claude-sonnet-4-6`. Override via `VOICE_MODEL` env var for dev iteration. Per-card override possible via `voice_config.runtime_model` if a specific voice tested better on Opus 4.7 (some voices may need this — empirically validate during dry runs against `dev_msc_test`). Adaptive thinking ON by default (`VOICE_THINKING=1`).

Token budgets: Step 1 `max_tokens=32000`, Step 2 `max_tokens=24000`, Step 3 `max_tokens=24000`, validation `max_tokens=4096`, continuity `max_tokens=8000`. These are ceilings that accommodate adaptive thinking; observed usage on dry runs will tune these.

Streaming: REQUIRED on Step 1, Step 2, Step 3 (any LLM call with thinking + max_tokens > 21K hits the SDK's non-streaming timeout heuristic). Validation + continuity may use non-streaming.

### Parallelism

| Stage | Parallelism | Env vars |
|---|---|---|
| Step 1 | N parallel where N = total (voice, formulation) pairs (~30 for 10 voices) | `VOICE_STEP1_BATCH=4`, `VOICE_BATCH_WAIT_S=20` |
| Validation | Same as Step 1 | (validations chained per response) |
| Step 2 | 10 parallel (one per voice) — no batch wait at this size | `VOICE_STEP2_BATCH=4` |
| Step 3 | 10 parallel (one per voice) — no batch wait at this size | `VOICE_STEP3_BATCH=4` |
| Continuity | 10 parallel | `VOICE_CONTINUITY_BATCH=4` |

Per Anthropic Opus 4.7 / Sonnet 4.6 rate limits, default batch size 4 with 20-second wait between batches keeps the pipeline well inside the rate window.

### CLI

```bash
python flows/voice_flow.py <run_dir> --night N [--skip-validation] [--skip-step3]
# Athens production — Night 1 (validation ON, Step 3 skipped per A1 decision 2026-05-01):
python flows/voice_flow.py runs/athens_2026_2026_05_07_night1 --night 1 --skip-step3
# Athens production — Nights 2 and 3 (validation OFF per FU#62 path B; Step 3 skipped):
python flows/voice_flow.py runs/athens_2026_2026_05_08_night2 --night 2 --skip-step3 --skip-validation
```

Required arg `--night N` ∈ {1, 2, 3} — controls continuity override loading.

- `--skip-validation` disables both validation nodes. Required on Athens Nights 2/3 per FU#62 path B (validation is diagnostic-only, no regen; running on Nights 2/3 is pure cost without remediation). Always use for dryrun work (Step 1 outputs are cached → validation re-runs against unchanged outputs → ~20-40 min wasted).
- `--skip-step3` runs Steps 1+2 only. **Required on all Athens production runs** per A1 decision 2026-05-01 (Option A). Cross-voice visibility moves to editor layer + Substack. Step 3 module + prompt remain in codebase, dormant; re-add path is ~2 days against B+ shape, documented in `_workspace/planning/runtime/OPEN_ITEMS.md` A1.

`<run_dir>` must contain `03_provocateur/briefings/*.json` (Provocateur output). Otherwise the flow exits with a clear message.

PROJECT_ROOT resolves via `--project <path>` > `AI_ASSEMBLY_PROJECT_ROOT` env > hard fail (per Tier 3 convention; use `flows.shared.project_root.resolve_project_root()`).

---

## Outputs

```
<run_dir>/04_voice/
├── step1_detailed_responses/
│   ├── plato__theme_003.json              one per (voice, formulation) pair
│   ├── plato__theme_007.json               filename = <voice_slug>__<theme_id>.json
│   ├── arendt__theme_003.json              joins to 03_provocateur/formulations/<theme_id>__<voice_slug>.json
│   └── ...                                 (filename order is reversed but the IDs match)
├── validation/                             optional, only if validation ran
│   ├── plato__theme_003.json
│   └── ...
├── step2_first_draft_artifacts/
│   ├── plato.json                          one per voice — lineage.consumed_detailed_responses[]
│   ├── arendt.json                         points back to the Step 1 files this artifact was assembled from
│   └── ...
├── step3_amended_artifacts/
│   ├── plato.json                          one per voice — lineage.voices_read[] + amendments[].cited_*
│   ├── arendt.json                         point back to other voices' Step 2 files
│   └── ...
├── responded_to_graph_night_1.json         rolled up after all Step 3 complete:
│                                           {edges: [{from, to, theme_id, amendment_type}, ...]}
├── themes_to_voices_night_1.json           reverse index per theme_id:
│                                           {theme_003: {step1_voices: [...], step2_voices: [...], step3_voices: [...]}, ...}
├── briefings_consumed/
│   ├── plato.json                          echo of Provocateur briefing for traceability
│   └── ...
├── step3_complete.flag                     sentinel triggering continuity flow
└── manifest.json                           run-level metadata + cost + wall-time + validation_failures[]
                                            + themes_to_voices summary (also lives standalone above for fast read)
```

Continuity overrides (per-voice, written by `continuity.py`):

```
<PROJECT_ROOT>/voices/<voice_slug>/
├── continuity_night_2.json                 generated after Night 1 completes
└── continuity_night_3.json                 generated after Night 2 completes
```

`<PROJECT_ROOT>/voices/<voice_slug>/07_persona_card_assembled.json` is NEVER modified at runtime — it's the build-time canonical card. Continuity overrides are separate files; the card-loading code (`card_assembly.py:load_persona_card(slug, night)`) reads the base card and overlays the continuity override when `night ≥ 2`.

---

## Cost & Envelope

Per night, 10-voice panel. Costs reflect Opus 4.7 + adaptive thinking on Steps 1/2/3 (the load-bearing creative-reasoning calls) and OpenAI ladder (gpt-5.4 high → fallbacks) on validation. Generous max_tokens ceilings let thinking run without truncating the final response.

| Stage | Calls | Model | Per-call cost | Stage total |
|---|---|---|---|---|
| Step 1 (Opus 4.7 + thinking, max 64K) | ~30-50 | claude-opus-4-7 | ~$2.50 | **~$75-125** |
| Validation A + B (Night 1 only, diagnostic) | ~60-100 | OpenAI ladder | ~$0.05-0.15 | **~$3-15** |
| Step 2 (Opus 4.7 + thinking, max 64K) | 10 | claude-opus-4-7 | ~$5 | **~$50** |
| ~~Step 3~~ *(SKIPPED for Athens per A1 2026-05-01)* | 0 | — | — | **$0** (was ~$50) |
| Continuity (Sonnet 4.6 + thinking, max 8K, Night 2+3 only) | 10 | claude-sonnet-4-6 | ~$0.30 | **~$3** |
| **Per-night total — Night 1** (validation ON, Step 3 skipped) | | | | **~$130-190** |
| **Per-night total — Nights 2+3** (validation OFF, +continuity, Step 3 skipped) | | | | **~$130-180** |

**Athens 3-night total:** ~$390-550 in API costs (Step 3 skipped per A1 2026-05-01 saves ~$150 across 3 nights). Continuity runs only on Nights 1 and 2 — its output is consumed on Nights 2 and 3. Validation runs only on Night 1 per FU#62 path B decision.

If Step 3 re-enables post-editor/microsite, add ~$50/night × 3 nights = ~$150 back.

Per-validation-call costs revised 2026-05-01 from prior ~$0.50/call estimate down to ~$0.05-0.15/call based on observed dryrun behavior (gpt-5.4 reasoning_effort=high on ~5K-token prompts).

This is meaningfully higher than a Sonnet-on-everything build (~$120-150 total) but is the calibration the operator chose because Steps 1/2/3 are the load-bearing creative-reasoning calls of the entire overnight pipeline. Getting them wrong fails Briefing v3.1's Layer 2 ("could a well-read human essayist have arrived here?") and Layer 3 (does the conversation become more-than). Opus + thinking is the price of the experiment; it is not the place to economise.

Wall time per night, with parallelism + Anthropic batch wait. Opus + thinking is slower per call than Sonnet (more reasoning tokens to generate); parallelism + batched submission keeps total wall manageable but the per-night envelope grows from ~25-35 min to:

| Stage | Parallel | Wall time |
|---|---|---|
| Step 1 (parallel across pairs, batched 4 + 20s wait, ~90-120s per call) | ~30-50 calls in batches of 4 | ~22-30 min |
| Validation (Night 1 only — per-voice serial, gpt-5.4 reasoning is slower than expected) | ~60-100 calls | ~20-40 min on Night 1; OFF on Nights 2/3 |
| Step 2 (parallel across voices, ~120-180s per call) | 10 calls | ~3-5 min |
| ~~Step 3~~ *(SKIPPED for Athens per A1 2026-05-01)* | 0 | 0 min (was ~3-5 min) |
| Continuity (parallel across voices, Nights 2+3 only, Sonnet is fast) | 10 calls | ~2-3 min |
| **Per-night total — Night 1** (validation ON, per-voice serial, Step 3 skipped) | | **~45-75 min** |
| **Per-night total — Nights 2+3** (validation OFF, +continuity, Step 3 skipped) | | **~25-40 min** |

Wall-time revised 2026-05-01 from prior ~30-50 min envelope. Validation observed at 20-40 min/night on Night 1 (per-voice serial, not the per-pair-parallel-overlapping-Step-1 originally specified). Athens Night 1 morning-of-Day-2 wall budget should plan for the ~50-80 min envelope.

Rate limits: Anthropic Opus 4.7 tier currently has tighter tokens-per-minute caps than Sonnet 4.6, which is why default `VOICE_STEP1_BATCH=4` with 20-second wait between batches is conservative. Monitor the first dry run; if rate limits relax pre-Athens, raise `VOICE_STEP1_BATCH` to 6-8 first.

---

## Validation Notes

Once `voice_flow.py` is built, dry-run against `~/Desktop/AI Assembly/archive/runs/runtime/dev_msc_test/03_provocateur/briefings/` (the canonical Provocateur output from the dev_msc_test rehearsal). Critical things to verify on first runs — these are diagnostic checks against the spec, not unit tests:

1. **Voice_temporal_stance discipline.** Detailed responses + artifacts honor the card's `voice_temporal_stance.default` as written. For voices whose stance describes year-counting (Plato's anchored chronology of "X years ago" within his own life is licensed), year-counting is correct; for voices whose stance forbids drifting into the reader's time, that drift is the violation. The validator uses the card's actual stance text, not a hard-coded framing — issues it flags should match deviations from the card's stance, not deviations from a presupposed framing. No eternal-present scholar tense about the voice itself ("Plato writes dialogues to dramatize…" — third-person scholar voice describing its own works from outside).

2. **`medium`-fidelity discipline.** Step 2 artifacts live within what the voice's `medium` field describes. Where `medium` is single-form (e.g. Plato's dialogue), the artifact IS that form; `selected_form` records it. Where `medium` is multi-form, `selected_form` is one of the variants the voice's corpus actually produces. Honor `banned_modes` as written in the card — the per-voice register failures the voice's corpus rules out. No drift into generic essay / modern panel-discussion register where the voice's `banned_modes` enumerates that as forbidden.

3. **Step 3 cross-voice engagement.** When `decision="amend"`, voices read each other and respond in their own grammar. The `responded_to_graph` populates from `voices_read` + `decision` (baseline voice-pair edges with `decision_rationale_excerpt`) and is decorated with per-passage `amendments[]` detail when voices emit structured amendments. Per-passage citations are visible IN the prose artifact regardless. Voices that stand-pat produce no edges.

4. **Amendments-producing-agreement check.** For each amendment, verify the voice did one of: `extend` (framework absorbs the move with explicit extension), `mark-limit` (framework reaches its limit and acknowledges it), or `sharpen-disagreement` (voice doubles down). Amendments that smooth over disagreement are anti-useful — flag them in the manifest.

5. **`reference_only_passages` not in Step 2 / Step 3 output.** Run a lift-phrase scan on Step 2 + Step 3 outputs against `reference_only_passages.passages[].text`. Any hit is a copyright-exposure bug — add to `banned_language` via Pass 7c.

6. **Continuity loaded on Night 2.** Verify Night 2 system prompts include the `continuity_block_if_night_2` and `continuity_block_artifact_if_night_2` content from `<PROJECT_ROOT>/voices/<slug>/continuity_night_2.json`.

7. **Stand-pat decisions.** Voices that stand pat on Step 3 must explain (a) which voices they read, (b) what moves they saw, (c) why none occasioned an amendment. Empty stand-pat rationale is a quality bug.

These are draft validation notes; refine against the first actual Athens dry run.

---

## See also

- `docs/AI_Assembly_Briefing_v3_1.md` — project source of truth + 3-layer experimental test (Encounter / Content / Expansion)
- **`docs/AI_Assembly_Frame_Concept_v1.md` — frame layer (broadsheet / newsreel / micro-site / Substack / Day 4 goodbye). Voice Pipeline produces the artifacts that arrive UNMEDIATED on the micro-site; the frame is downstream and does not wrap Voice Pipeline output. The Edition Pipeline (separate, downstream of Step 3) reads all 10 amended artifacts and produces the broadsheet front page.**
- `docs/AI_Assembly_Persona_Card_v2.md` — 35-field schema + register rule (note: §H family-of-forms + §J voice-IN-the-present + tense discipline amendments were reverted 2026-04-28 per commit `9480d3a`; current persona prompts are at the 582af96 baseline)
- `docs/AI_Assembly_Persona_Pipeline_v4.md` — the persona build pipeline that produces the cards this Voice Pipeline consumes
- `docs/AI_Assembly_Provocateur_Pipeline.md` — Stage 4 Packaging defines this Voice Pipeline's input contract (the briefings)
- `docs/CURRENT_STATE.md` — gap analysis + critical path; Voice Pipeline is Phase D (this spec lands; build follows)
- `personas/HANDOFF.md` — cross-repo runtime contract; authoritative on what to drop / keep when assembling system prompts
- `_workspace/planning/HANDOFF_2026_04_28.md` — handoff covering the persona-prompt revert (commit `9480d3a`); see also `_workspace/planning/HANDOFF_DRYRUN_2026_04_29.md` for the Voice Pipeline first-dry-run pickup
- `_workspace/planning/FOLLOW_UPS.md` — active follow-up tracker; FU#49M (`strain_markers[]` schema as Step 2 contract, post-Athens), FU#42 (split-card architecture, post-Athens), FU#49F (per-voice framework-strain log on micro-site, post-Athens)
- `docs/_archive/AI_Assembly_Voice_Pipeline_v1_partial.md` — preceding partial draft (historical)

---

*End of v2.1 spec. Reflects the 2026-04-28 persona-prompt revert (commit `9480d3a`): voice_temporal_stance is the 582af96 fluid-across-time framing; `medium` is honored as written (single-form OR multi-form per voice's actual corpus); `banned_modes` is per-voice; no separate tense-discipline mandate (the card carries what it carries). Implementation landed 2026-04-28 (commits `180a18f` + `aca0e4c`); v2.1 alignment landed 2026-04-29.*
