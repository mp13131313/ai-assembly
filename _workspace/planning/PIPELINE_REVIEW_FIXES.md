# Pipeline Review — Fixes Tracker

**Status:** In progress. Step-by-step review of every LLM call and Jinja render in the persona pipeline, following the task description in-session (Phase M review, post-merge).

## Pipeline step map (naming reference)

The current numbering mixes two schemes in the same phases. This legend maps which step does what. A coordinated renumbering is a separate follow-up — see note at the end.

### Phase 0 — Intake
- **`0a`** — voice_config generation (LLM: Claude Opus 4.7 + thinking)

### Phase 0.5 — Pre-DR research (runs AFTER Pass 0a signoff)
- **`1a`** — Perplexity `sonar-deep-research` (4 voice-type variants)
- **`1b`** — Gemini `gemini-2.5-pro` broad scan (4 voice-type variants)
- **`0b render`** — Jinja DR-prompt composition (wrapper + header + voice-type body + footer)
- **`0b tailor`** — Claude Opus 4.7 hybrid tailoring (injects voice-specific follow-up questions at placeholders)
- *(manual)* — Operator pastes 6 section prompts into claude.ai → Claude DR → saves 6 section dossier files

### Phase 1 — Chunked merge (reads Perplexity + Gemini + Claude DR; produces merged_dossier)
- **`1.1`** — BIOGRAPHICAL (Opus 4.7 + thinking, per-section DR auto-detect)
- **`1.2`** — INTELLECTUAL
- **`1.3`** — REASONING
- **`1.4`** — VOICE
- **`1.5`** — BOUNDARIES
- **`1.6`** — CORPUS (outputs `urls[]` + `passages[]` chunks)
- **`1.7`** — COHERENCE (produces final `merged_dossier`)

### Post-merge primary-text acquisition (runs AFTER Phase 1 merge, BEFORE Phase 2 generation)
- **`1c-extract`** — reads `merged_dossier.urls.urls[]` deterministically (no LLM — v3.10 had a Sonnet call here; Phase B dropped it)
- **`1c-fetch`** — HTTP download of URLs (deterministic, no LLM)
- **`1c-review-gate`** — operator confirms fetched texts before pipeline continues
- **`1d`** — excerpt selection from fetched texts, guided by `merged_dossier` (Claude Sonnet LLM call)

**Naming note — why `1c`/`1d` feel misplaced:** they bear a `1` prefix (implying Phase 1) but actually run AFTER Phase 1 merge completes. The name reflects historical research-acquisition family (1a/1b/1c/1d were all "research sources"), but the execution order is: Phase 1 merge first → Pass 1.6 extracts URLs from the 3 research sources → Pass 1c fetches those URLs → Pass 1d selects excerpts from fetched text. The chunked merge (1.1-1.6) never sees primary-text content; it only sees descriptions/quotes of primary texts in the 3 research sources' dossier output.

### Phase 2 — Generation
- **`2`** — Identity & Boundaries · **`CT after 2`** · **`3`** — Intellectual Core · **`CT after 2+3`** · **`4a`** — Voice · **`CT after 2+3+4a`** · **`4b`** — Artifact · **`CT after 2+3+4`** · **`5`** — Engagement · **`6`** — Corpus Curation

### Phase 3 — Validation
- **`7pre`** — Citation verification · **`7-anach`** — Anachronism check · **`7a`** — Cross-model validation · **`7b`** — Smoke test chains · **`7c`** — Negative constraints

### Phase 4 — Derive
- **Derive** — Provocateur Profile + Evaluation Rubric

### Naming note

The `1a/1b/1c/1d` family and the `1.1-1.7` family collide in the same phase numerically. The `0b` label sits between `1a/1b` and `1c/1d` because it's Phase 0.5 DR-prep. Renumbering proposal (deferred to separate follow-up):
- Phase 0.5 steps → `0.5a` Perplexity / `0.5b` Gemini / `0.5c` DR render / `0.5d` DR tailor / `0.5e` primary fetch / `0.5f` excerpt select
- Phase 1 merge steps → `1.1-1.7` (unchanged)
- Phase 2+ steps → unchanged

Not renaming during this review: rename touches ~30 files (runners, schemas, path helpers, directory layout, tests, docs, telemetry). Coordinated refactor out of review scope.

---

**Convention:**
- Each step gets a section.
- Each fix gets a row: **ID** · **Severity** · **File:line** · **Change** · **Status**
- Severity: `CRITICAL` (breaks pipeline) · `HIGH` (quality regression risk) · `MEDIUM` (leftover / tune) · `LOW` (cosmetic / polish)
- Status: `PROPOSED` → `APPROVED` → `APPLIED` → `VERIFIED` · or `DEFERRED` / `REJECTED`

**Workflow:**
1. Review surfaces fixes → `PROPOSED`
2. User approves/defers/rejects → `APPROVED` | `DEFERRED` | `REJECTED`
3. Implementation pass (separate) applies → `APPLIED`
4. Pipeline re-run verifies → `VERIFIED`

When all steps reviewed and fixes categorised, a consolidated "by file" and "by severity" tally lives at the bottom. That drives the implementation pass.

---

## Cross-pass architectural proposals

These are **structural changes** that span multiple passes, not prompt tunes or single-file fixes. Tracked separately because implementation requires coordinated edits across ~5-7 files + schema changes.

### 1-arch-01 — `curated_corpus_passages` should come from Pass 1d, not Pass 1.6

**Severity:** HIGH (quality ceiling, not blocker)
**Status:** PROPOSED (post-Phase-N implementation)
**Scope:** Pass 1.6 prompt + schema; Pass 1d schema + prompt; Pass 6 refactor; `merged_dossier.py` schema

**Problem:**

Current architecture has **two parallel flows** for primary-text excerpts into the final card:

1. **Flow A (current for `curated_corpus_passages` text):** 3 research sources (Perplexity / Claude DR / Gemini) → quote excerpts in their §6 dossier output → Pass 1.6 `passages[].text` → Pass 6 Corpus Curation → `curated_corpus_passages` in assembled card.
2. **Flow B (current for Pass 4a voice context):** Pass 1c fetches full primary texts → Pass 1d Sonnet selects ~30K chars → `primary_block` → Pass 4a voice analysis.

Flow A limitation: passage text is **budget-constrained by research-source quote space**. A research source's §6 has ~100-300 words per passage; Pass 6 can't expand beyond that. Flow A never sees fetched primary texts.

Example (Dostoevsky card): `curated_corpus_passages` has Ivan's "return the ticket" at ~100 words. Full Rebellion chapter is ~15,000 words. Pass 4a sees broader context via Flow B; Pass 6 only had the 100-word Claude-DR-extracted quote for the card.

**Proposed architecture:**

| Pass | Current role | Proposed role |
|---|---|---|
| Pass 1.6 | Produces `passages[]` with verbatim `text` field (ceiling-bound by research sources) | Produces passage METADATA (`canonical_reference`, `purpose_tag`, `why_selected`, `anchor_phrase` — NO text field) |
| Pass 1c | HTTP fetch primary texts | Same |
| Pass 1d | Sonnet selects excerpts from fetched texts for Pass 4a voice analysis only | **Fuzzy-match Pass 1.6 metadata against fetched texts; extract verbatim + surrounding context (~500-2000 chars per passage). Emit dual output: `primary_block` for Pass 4a AND `curated_corpus_passages_text` for Pass 6.** Sonnet fallback for unmatched. |
| Pass 6 | Composes `curated_corpus_passages.text` from Pass 1.6 text | Composes from Pass 1d text + Pass 1.6 metadata — cull / order / enrich with scholarly context |

**Benefits:**

1. **Verbatim from fetched source** — no hallucination risk, no paraphrase leakage
2. **Right-sized context** — 500-2000 chars per passage (vs. 100-300 ceiling from research-source quotes)
3. **Edition-aligned** — `curated_corpus_passages.text` and `primary_block` both draw from same fetched translation tradition (currently can mismatch: Claude DR quoted Haddawy Scheherazade, Pass 1c fetched Burton)
4. **Single source of truth** — one fuzzy-match + one curation; not two parallel excerpt flows
5. **Cost-neutral or cheaper** — Pass 1.6 becomes lighter (metadata only, less text generation); Pass 1d grows slightly but Sonnet fallback is rare; Pass 6 shrinks

**Cost of the refactor (implementation effort):**

- `pass_1_6_merge.md` prompt: ~20-line change (drop text generation, emphasize metadata + anchor_phrase)
- `schemas/pass_1_6.py`: `Passage.text` field optional or removed; add `anchor_phrase`, `canonical_reference`, `purpose_tag` if not present
- `persona_pass_1d_excerpt_selection.md` + `node1d_excerpt_selection.py`: extend output to include `curated_corpus_passages_text`
- `persona_pass_6_corpus_curation.md`: refactor to consume Pass 1d text + Pass 1.6 metadata
- `schemas/merged_dossier.py` + `schemas/_conventions.py`: verify passage structure
- Tests + migration plan
- Integration testing on 1-2 voices before Phase N re-runs

Estimated: 1-2 days focused engineering + testing.

**Why not now:**

- Current pipeline works — canonical passages ARE in the card (just shorter than optimal)
- Phase N is about to fire; refactor would delay voice builds
- Quality ceiling is real but not blocking

**Why do it post-Phase-N:**

- Biggest single architectural lever in the merge layer for voice quality
- Once 11 more voices run on current architecture, the ceiling manifests at scale
- Post-Phase-N review of all 12 cards will make the gap visible and motivate the refactor

**Dependency on 1d-06 (fuzzy-match):**

1d-06 (Pass 1d fuzzy-match primary-path) is a prerequisite for 1-arch-01. The fuzzy-match infrastructure that 1d-06 proposes is exactly what 1-arch-01 needs for the curated-corpus-passages extraction. **Implement 1d-06 first; 1-arch-01 extends it.**

**Cross-references:**
- Depends on: 1d-06 (Pass 1d fuzzy-match)
- Affects: Pass 1.6 prompt + schema · Pass 1d prompt + code · Pass 6 prompt + logic · merged_dossier schema
- Validates via: card `curated_corpus_passages` text being verifiably verbatim from fetched primary texts (deterministic check)

---

## Cross-template patterns to harmonize

Observations that cut across multiple prompts — these are NOT individual fixes but structural patterns one template does well that others could lift. **Implementation pass should coordinate these rather than working file-by-file**, otherwise good patterns in one variant get silently left out of the others.

### Pass 1a family (4 voice-type variants)

| XREF ID | Pattern observed in | Worth lifting to | Detail |
|---|---|---|---|
| 1a-XREF1 | `persona_pass_1a_non_human_organism.md` (§4 tradition-note, lines 197-201) | `persona_pass_1a_human.md` (§4) | Organism variant explicitly names the scientific-literature scholar the voice is tradition-channelled through (Godfrey-Smith for cephalopods, de Waal for primates, Marzluff for corvids). Human variant's §4 tradition-note is thinner — for tradition-embedded human voices (Marley's Rastafari, Scheherazade's 1001 Nights recension tradition), parallel named-interlocutor framing would harden §4 coverage. |
| 1a-XREF2 | `persona_pass_1a_non_human_system.md` (§5 closest-analog discipline) | `persona_pass_1a_human.md` (§5) | System variant's closest-analog discipline is concrete: "democracy [none — distributed activity without a centre is ontology, not polity]" demonstrates the pattern crisply. Human variant's equivalent section could borrow this shape. |
| 1a-XREF3 | `persona_pass_1a_non_human_system.md` (CARE + IPAI framing) | `persona_pass_1a_human.md` (hostile-sources block) | System variant's "synthesis of published Indigenous governance philosophy" + community-specificity + named-scholar preference is the most ethically-rigorous of the 4 templates. For hostile-sourced human voices (Cleopatra — Egyptian / Ptolemaic context mediated through Roman sources), community-specificity and named-scholar discipline could partially transfer. |
| 1a-XREF4 | `persona_pass_1a_non_human_system.md` (`[oral_tradition: <source>]` tag) | `persona_pass_1a_human.md` (for oral-tradition voices) | System variant's `[oral_tradition]` tag is specific to system voices; organism variant doesn't need it; human variant might benefit for oral-tradition-grounded voices (Marley's Rastafari reasoning; Scheherazade within 1001 Nights oral recension). |
| 1a-XREF5 | `persona_pass_1a_fictional.md` (`[narrative_function]` tag) | — (already parallel to human's `[experiential_reconstruction]`) | Architectural parallel: `[narrative_function]` (fictional interiority is attributed) mirrors `[experiential_reconstruction]` (human experience is biocultural reconstruction). Both prevent different kinds of projection. Documented parallelism; no change needed, noted for coherence. |
| 1a-XREF6 | `persona_pass_1a_fictional.md` ("Do not invent biography") | `persona_pass_1a_human.md` (hostile-sources handling) | Fictional variant's "do not invent biography" discipline could partially inform human-template hostile-sources handling — Cleopatra reconstruction carries risk of inventing internal life the Roman sources don't document. Similar boundary-discipline concern, different context. |

### Pass 1b family (4 voice-type variants)

| XREF ID | Pattern observed in | Worth lifting to | Detail |
|---|---|---|---|
| 1b-XREF1 | `persona_pass_1b_non_human_system.md` (line 8: "respect CARE + IPAI data-governance norms") | `persona_pass_1b_non_human_organism.md` (via fix 1b-08) | System variant already references CARE + IPAI explicitly; organism variant uses vague "appropriate epistemic framing." When implementing 1b-08, lift the system variant's wording rather than introducing new phrasing — consistent standards-citation across voice-type variants where applicable. |
| 1b-XREF2 | `persona_pass_1b_fictional.md` (lines 20-21: "Surface non-Western scholarship... as PRIMARY rather than supplementary") | `persona_pass_1b_human.md`, `_non_human_organism.md`, `_non_human_system.md` | Fictional variant has the strongest non-Anglophone framing of any Pass 1b variant — "PRIMARY rather than supplementary" inverts the default hierarchy, stronger than "prioritize" or "cite original language." Worth lifting to the other 3 variants where non-Anglophone scholarship is structurally load-bearing: all 3 to varying degrees (human for non-Anglophone figures; organism for non-Anglophone ethology field sites; system for Indigenous-language scholarship). |

### Sequencing note

When the implementation pass fires, these XREF items should drive a **pattern-harmonization sub-pass** run before or alongside the per-file fix application:

1. First pass: individual file fixes (0a-01 through 0a-04, 1a-01 through 1a-14, 1b-02 through 1b-14).
2. Coordinated pass: apply XREF lifts — lift organism's §4 tradition-note structure to human; lift system's CARE+IPAI wording to organism; lift fictional's "PRIMARY rather than supplementary" framing to the other 3 Pass 1b variants.
3. Final consistency check: all 4 variants of each family (Pass 1a, Pass 1b) use harmonized wording where they share a structural pattern.

This prevents the fragmentation where voice-type variants drift apart on the same structural dimension.

---

## Step 1 — Pass 0a (Voice Config)

**Mechanism:** LLM call · Anthropic `claude-opus-4-7` · adaptive thinking · max_tokens=24000 · temperature=1.0
**Prompt:** `personas/flows/shared/prompts/pass_0a_voice_config.md` (130 lines)
**Verdict:** TUNE — 3 fixes, none urgent, ~10 min total edit time. Model + config stay as-is.

| ID | Severity | File:line | Change | Status |
|---|---|---|---|---|
| 0a-01 | MEDIUM | `pass_0a_voice_config.md:115` | Update "Paste each of the 6 section prompts into claude.ai (Opus 4.7 + Extended Thinking + Deep Research)" to reflect the model-per-section policy finalized in Phase L: §1-§5 on Opus 4.6, §6 on Opus 4.7. | PROPOSED |
| 0a-02 | MEDIUM | `pass_0a_voice_config.md:117` | Stale runner reference: change `run_pass_1_all.py "<Display Name>"` to `run_persona_pipeline.py "<Display Name>"`. Phase B restructure (Phase K commit) folded chunked Pass 1 orchestration into `run_persona_pipeline.py`; `run_pass_1_all.py` no longer exists. | PROPOSED |
| 0a-03 | LOW | `pass_0a_voice_config.md:107` | Tighten "What a domain expert should look at" spec: "3-5 bullets, one per proposed field where the confidence call was genuinely close, naming the alternative that was ruled out and why." Currently under-specified → inconsistent curator-review utility per voice. | PROPOSED |
| 0a-04 | LOW | `pass_0a_voice_config.md:48` | Tighten `manual_grounding` echo rule from "verbatim or lightly normalized" to "verbatim." Curated non-human grounding files (Godfrey-Smith excerpt, Te Awa Tupua Act text) need verbatim preservation; normalization is easy post-hoc if ever needed. | PROPOSED |

---

## Step 2 — Pass 1a Perplexity (human variant)

**Mechanism:** LLM call · Perplexity `sonar-deep-research` · temperature=0.0 · return_citations=True · 15-min timeout · 2× retry with backoff
**Prompt:** `personas/flows/shared/prompts/persona_pass_1a_human.md` (250 lines)
**Verdict:** TUNE — 5 fixes, none urgent. Core architecture sound. Model + config stay as-is.

| ID | Severity | File:line | Change | Status |
|---|---|---|---|---|
| 1a-01 | MEDIUM | `persona_pass_1a_human.md:19-20` | **Internal contradiction.** Delete the per-section 2,000-word floor ("Each of the 6 sections: 2,000+ words."). It conflicts with the depth-not-breadth framing (line 24-26) which permits §1+§3+§6 thorough and §2+§4 shorter. Keep the 15K total-word floor. | PROPOSED |
| 1a-02 | MEDIUM | `persona_pass_1a_human.md:110-113` | **Dostoevsky-anchored leftover.** "Pochvennichestvo-equivalent specificity" references Russian-Intelligentsia-movement disambiguation as a Dostoevsky-specific example. The underlying pattern (figure's position within a tradition they're often conflated with) is general; rephrase the instruction in general terms and move Slavophile/pochvennichestvo to an e.g. clause with parallel examples (Socratic/Platonist/Academic; Rastafari/Garveyite/Pan-Africanist; etc.). | PROPOSED |
| 1a-03 | LOW | `persona_pass_1a_human.md:121` | **§3 step-ordered enumeration pressure.** "5-8 cognitive / dialectical / narratival / scenic steps in order" forces ordering that's artificial for scenic/aphoristic/parabolic reasoners. Change to "5-8 cognitive moves or reasoning stages, step-ordered where the figure's actual method has ordered structure, else clustered/thematic — prefer the figure's own native structure." | PROPOSED |
| 1a-04 | MEDIUM | `persona_pass_1a_human.md:150` | **§4 tradition-note under-specified.** Single bullet "if voice is tradition-embedded, name it, else null" is thin for tradition-embedded voices (Marley, Scheherazade). Expand to sub-section: tradition name, structural constraints on expression (genre/register/performance context), how tradition authority sits above individual authorship, tradition's own verification rules. | PROPOSED |
| 1a-05 | LOW | `persona_pass_1a_human.md:168` | **§5 framing awkward for contemporary voices.** "What was known and available in the figure's period" reads as historical-exclusion frame; for Audrey Tang / Thiel / Lovelace (partly), reframe as engagement-horizon + explicit out-of-scope + contested-in-current-debate. Add conditional paragraph. | PROPOSED |

*Additional notes (not fixes — observations for Wave 3):*
- Pass 1a produces 15-30K words. Whether Pass 1.1-1.6 merge actually reads the full corpus is a Wave 3 verification item.
- §2 "10-20 commitments" → Pass 1.2 merge → card's 17-commitment constitution: this is where the selection-ratio question lives. Wave 3 to confirm.

---

## Step 3 — Pass 1a Perplexity (non_human_organism variant)

**Mechanism:** LLM call · Perplexity `sonar-deep-research` · temperature=0.0 · (identical to Step 2)
**Prompt:** `personas/flows/shared/prompts/persona_pass_1a_non_human_organism.md` (327 lines)
**Verdict:** TUNE — 4 fixes. Better calibrated than human template in several ways (§4 tradition-note, §5 closest-analog discipline, anti-anthropomorphism block, `[speculation]` tag, `condition_of_being`). Same internal contradiction as human template on per-section floor. Model + config stay.

| ID | Severity | File:line | Change | Status |
|---|---|---|---|---|
| 1a-06 | MEDIUM | `persona_pass_1a_non_human_organism.md:25` | **Internal contradiction inherited from shared pattern.** Delete the per-section 2,000-word floor. Keep 15K total-word floor. Mirror of 1a-01. | PROPOSED |
| 1a-07 | MEDIUM | `persona_pass_1a_non_human_organism.md:151-155` | **§3 step-ordered enumeration pressure, worse here than in human template.** "5-8 step PERCEPTUAL-RESPONSE PROCESS (full-field reception → salience assessment → exploratory contact → bodily-display → spatial-navigability read → decisive orientation)" forces sequential stages that contradict documented parallel / distributed cognition in octopuses. Soften to: "5-8 perceptual-response stages, sequential where the ethology documents ordering, parallel/distributed where the organism's actual cognition runs that way." | PROPOSED |
| 1a-08 | LOW | `persona_pass_1a_non_human_organism.md:151-155` | **Step-process example is cephalopod-specific but unlabeled.** The 6 named stages transfer to octopus cleanly but not to other non-human organisms (a corvid's problem-solve cycle, a cetacean's echolocation-exploration cycle have different shapes). Mark the example as "for cephalopods; adapt to taxon" or provide 2-3 taxon-varying examples as alternatives. | PROPOSED |
| 1a-09 | LOW | `persona_pass_1a_non_human_organism.md:40-52` | **Non-Anglophone examples are cephalopod-research-site heavy** (OIST, Stazione Zoologica Napoli, Iberian marine biology). Good for Octopus voice; less useful for hypothetical non-cephalopod organism voices. Reshape as: generic principle ("prioritize original-language research tradition for this organism's primary field-site base") + cephalopod-specific examples in an "e.g." clause. | PROPOSED |

*Cross-template observation (not a fix per se):*
- 1a-XREF: The §4 tradition-note in THIS template (lines 197-201) explicitly names the scientific-literature scholar the voice is tradition-channelled through (Godfrey-Smith / de Waal / Marzluff). The human template's §4 tradition-note is thinner. **Consider lifting this structure to the human template** — for tradition-embedded human voices (Marley, Scheherazade), the parallel named-interlocutor framing would harden §4 coverage. Cross-references 1a-04.

*Additional monitoring note (not a fix):*
- §1 sub-ask ordering buries philosophical asks (Umwelt, selfhood, anachronisms, formative candidates) at positions 6-11 after the scientific-biological asks 1-5. Perplexity tends to front-load attention; if the Octopus run shows thin philosophical coverage, reorder philosophical asks earlier.

---

## Step 4 — Pass 1a Perplexity (non_human_system variant)

**Mechanism:** LLM call · Perplexity `sonar-deep-research` · temperature=0.0 · (identical to Step 2)
**Prompt:** `personas/flows/shared/prompts/persona_pass_1a_non_human_system.md` (379 lines)
**Verdict:** KEEP with minor tuning — 2 fixes. **Most ethically-engineered of all 4 Pass 1a templates.** CARE Principles + IPAI grounding + "synthesis of published Indigenous governance philosophy" framing is exemplary. Model + config stay.

| ID | Severity | File:line | Change | Status |
|---|---|---|---|---|
| 1a-10 | MEDIUM | `persona_pass_1a_non_human_system.md:28` | **Internal contradiction inherited from shared pattern.** Delete the per-section 2,000-word floor. Keep 15K total-word floor. Mirror of 1a-01 / 1a-06. | PROPOSED |
| 1a-11 | LOW | `persona_pass_1a_non_human_system.md:194-199` | **§3 step-ordered enumeration pressure, lighter touch than organism variant.** "5-8 step ASSESSMENT CYCLE (relational-condition read → breach-or-reciprocity assessment → kin-implication → hara naming → remedy invocation)" — legal reasoning is legitimately sequential so the ordering is defensible, but still soften to: "5-8 assessment stages, sequential where the legal method documents ordered structure, clustered where the framework's reasoning is holistic/systemic." | PROPOSED |

*Cross-template observations (not fixes — noted for later):*
- 1a-XREF3: The CARE + IPAI + "synthesis of published governance philosophy" framing here could partially inform hostile-sources handling in the human template (Cleopatra Egyptian/Ptolemaic context) — named-community-specificity and community-scholarship preference would transfer.
- 1a-XREF4: Tag convention addition `[oral_tradition: <source>]` is specific to system voices; the organism variant doesn't need it; the human variant might benefit for oral-tradition-grounded voices (Marley's Rastafari reasoning tradition, Scheherazade as narrator within 1001 Nights oral recension tradition).

*Monitoring notes (not fixes — for future Andean/Pachamama or other non-Whanganui system voices):*
- Scholar lists for non-Whanganui communities are thinner (line 64 "Catherine Walsh, Eduardo Gudynas" for Andean vs. 4 named community scholars for Whanganui). Other relevant Andean/Latin American scholars of ontological turn and political ontology (Viveiros de Castro, de la Cadena, Blaser, Escobar) aren't named. Operator-adaptation burden is real if the panel ever expands beyond Whanganui on the system-subtype.
- No voice-name-conditional Jinja branching. Acceptable since Whanganui is the only non_human_system voice in the panel; scale issue only if panel expands.

---

## Step 5 — Pass 1a Perplexity (fictional variant)

**Mechanism:** LLM call · Perplexity `sonar-deep-research` · temperature=0.0 · (identical to Step 2)
**Prompt:** `personas/flows/shared/prompts/persona_pass_1a_fictional.md` (421 lines — longest Pass 1a variant)
**Verdict:** KEEP with minor tuning — 2 fixes. **Most textual-tradition-sophisticated** of the 4 Pass 1a templates. Translation-tradition awareness, "do not invent biography" boundary, `[narrative_function]` tag, and `[projection_warning]` for anachronistic literary-critical terms all well-engineered. Model + config stay.

| ID | Severity | File:line | Change | Status |
|---|---|---|---|---|
| 1a-12 | MEDIUM | `persona_pass_1a_fictional.md:25` | **Internal contradiction inherited from shared pattern.** Delete the per-section 2,000-word floor. Keep 15K total-word floor. Mirror of 1a-01 / 1a-06 / 1a-10. | PROPOSED |
| 1a-13 | LOW | `persona_pass_1a_fictional.md:225-284` | **§4 has 10 sub-asks — densest section in any Pass 1a template.** Sub-ask 8 ("Translation choice and its implications") partially overlaps with the TRANSLATION TRADITION block at lines 54-59. Consider consolidating: either drop the §4 sub-ask or make the §54-59 block structurally subordinate. Not critical (Perplexity handled Dostoevsky's similarly-dense §4 adequately) but reduces prompt load. | PROPOSED |

*Cross-template observations (not fixes — noted for later):*
- 1a-XREF5: `[narrative_function]` tag here is the fictional-template analog to `[experiential_reconstruction]` in the human template. Both prevent different kinds of projection (psychologising fictional interiority vs. importing modern therapeutic vocabulary onto historical figures). Parallel architectural move.
- 1a-XREF6: The "do not invent biography" discipline for fictional voices could partially inform hostile-sources handling in the human template (Cleopatra's hostile-source reconstruction risks inventing internal life the Roman sources don't document).

*Monitoring note (not a fix — for future non-Scheherazade fictional voices):*
- Scheherazade-specific concrete examples dominate throughout (scholar names, translator references, period-vocabulary, narrative moves). For any future fictional voice in panel (no others currently beyond Scheherazade), operator-adaptation burden is high. Not urgent given current panel.

---

## Step 6 — Pass 1b Gemini (human variant) — REVISED AFTER RESEARCH SANITY-CHECK

**Mechanism:** LLM call · Google `gemini-2.5-pro` · temperature=0.2 · max_output_tokens=16384 · thinking=model-default (2.5-pro requires) · 2× retry with backoff
**Prompt:** `personas/flows/shared/prompts/persona_pass_1b_human.md` (26 lines)
**Verdict (final, 2026-04-21):** TUNE. Keep `gemini-2.5-pro` per user. Keep "broad scan" role per baseline research findings. Narrower prompt improvements only.

### Research sanity-check outcome

Original proposal (previous iteration of this step) was to elevate Pass 1b to 8-12K words, 6-section structure matching Pass 1a, cross-disciplinary synthesis. **Research flags this as unsafe.**

From `research/baseline_research/compass_artifact_wf-865974da` (File 4):
> "Gemini Deep Research fills a useful but narrower role... However, an academic researcher testing it on Buddhist philosophy found it 'unusable for basic humanities research' due to unreliable sourcing — outputs looked authoritative but contained errors only a domain expert would catch. **Use Gemini for breadth-first discovery, not for philosophical depth.**"

File 4's tool-section table assigns Gemini only to S1: Identity & Framing as a **secondary** tool (Gemini broad scan), never as primary for any humanities research section.

**Implication:** Asking Gemini for the kind of structured cross-disciplinary humanities synthesis Pass 1a asks of Perplexity pushes Gemini into its documented failure mode — authoritative-looking but expert-detectable errors. The Athens audience includes the domain experts who would catch this (Quarch on Plato, Tsinorema on bioethics, Erinakis on authenticity-and-AI, etc.).

**Research-aligned role:** Gemini stays in "breadth-first discovery / catches what Perplexity under-weights" lane. Distinctive strengths to lean into:
- Breadth of adjacent-thinker / lineage / affinity connections (cross-reference strength)
- Multilingual scholarship index coverage (Russian / Japanese / Arabic / Sanskrit / Spanish / German / Portuguese)
- Unusual primary-text passages Perplexity's canonical-first search misses
- Recent reassessments surfacing (2020-2026 — Gemini sees academic publication breadth Perplexity search may not yet weight)

None of these require the structured-depth shape I was originally proposing.

### Revised fixes (narrower scope)

| ID | Severity | File | Change | Status |
|---|---|---|---|---|
| 1b-01 | REJECTED | `.env` | ~~Switch `GEMINI_MODEL` default to `gemini-2.5-flash`.~~ Rejected per user 2026-04-21 — preference is to keep Pro-tier. | REJECTED |
| 1b-02 | MEDIUM | `persona_pass_1b_human.md` (new block, ~10 lines) | **Add `{% if hostile_sources %}` block.** For hostile-sourced human voices (Cleopatra), direct Gemini at counter-tradition scholars and minority readings where multilingual + cross-reference strengths pay off. Parallel to Pass 1a's hostile-source block but retained in Gemini's breadth lane (surface counter-tradition sources, don't synthesize them). | PROPOSED |
| 1b-03 | LOW | `persona_pass_1b_human.md` (after line 18) | **Add soft length target:** "3-6K words; depth over length; do not pad but produce substantive breadth." Anchors Gemini to a useful range without pushing into depth-synthesis territory research flags as unreliable. | PROPOSED |
| 1b-04 | LOW | `persona_pass_1b_human.md:5-7` | **Reframe bullet 1 Boddice integration.** Keep Gemini in breadth-surfacing mode: "History-of-emotions and biocultural-history scholarship — surface Rosenwein (emotional communities), Reddy (emotional regimes), Stearns (emotionology), Boddice (biocultural critique) as scholarly-anchor points where applicable to the figure's period. Non-English sources prioritised. Name scholars; do not synthesize their readings in depth (that's Claude DR's job)." Sharper direction without pushing into synthesis territory. | PROPOSED |
| 1b-05 | LOW | `persona_pass_1b_human.md:5-18` | **Sharpen the 6 bullets to pull harder on Gemini's distinctive strengths per research:** (a) cross-disciplinary *connections* (not synthesis — adjacency-surfacing); (b) non-Anglophone scholarship *indexing* (names + publication pointers; Claude DR handles interpretation); (c) recent reassessments 2020-2026 — surface + brief what-changes framing; (d) unusual primary-text passages not in canonical surveys; (e) lineage/affinity connections across traditions not self-identified by the figure. Re-wording, not restructuring. | PROPOSED |

**NOT doing (rejected from earlier proposal):**
- ~~6-section structure matching Pass 1a~~ — pushes Gemini into depth-synthesis territory research flags as unreliable
- ~~8-12K word target~~ — same
- ~~Reframe as "parallel research tier"~~ — contradicts tool-section research guidance
- ~~Cross-disciplinary synthesis via thinking mode~~ — documented Gemini failure mode for humanities
- ~~`pass_0b_tailor.md` relabeling Gemini as PARALLEL~~ — Gemini staying SECONDARY matches research

**Downstream implications (simplified from earlier proposal):**

| Implication | Change needed |
|---|---|
| Pass 0b tailoring framing | None — keeps current PRIMARY/SECONDARY labelling per research |
| Pass 1.1-1.6 merge | None — already reads all 3 sources |
| Cost impact | Near-zero — prompt tightening, not expansion |
| Wall time | Unchanged |

---

## Step 7 — Pass 1b Gemini (non_human_organism variant)

**Mechanism:** LLM call · Google `gemini-2.5-pro` · identical config to Step 6
**Prompt:** `personas/flows/shared/prompts/persona_pass_1b_non_human_organism.md` (19 lines)
**Verdict:** TUNE. Same narrow-tuning pattern as 1b human. Voice-type-tailored cross-disciplinary set is well-chosen (philosophy of mind + ethology + cognitive neuroscience + comparative psychology + animal ethics). Anthropomorphism-critique ask mirrors Pass 1a organism discipline correctly.

| ID | Severity | File | Change | Status |
|---|---|---|---|---|
| 1b-06 | MEDIUM | `persona_pass_1b_non_human_organism.md` (new block) | **Add `{% if hostile_sources %}` block.** For organisms with hostile cultural-history records (bestiary demonization of cephalopods; predator-eradication discourse for wolves/sharks; bounty-era sporting literature), direct Gemini at counter-tradition ethological scholarship. Parallel to 1b-02 for human variant. ~10 lines. | PROPOSED |
| 1b-07 | LOW | `persona_pass_1b_non_human_organism.md` (after line 15) | **Add soft length target:** "3-6K words; depth over length; substantive breadth." Parallel to 1b-03. | PROPOSED |
| 1b-08 | LOW | `persona_pass_1b_non_human_organism.md:13-14` | **Strengthen TEK / Indigenous ethical framing.** "With appropriate epistemic framing" is vague. Reference CARE Principles + IPAI (Lewis et al. 2020) standards explicitly, or point at "community-authorised publications where TEK has been documented with permission" — staying in surface-this-material lane, not synthesis. | PROPOSED |
| 1b-09 | LOW | `persona_pass_1b_non_human_organism.md:9-10` | **Name scholars for the anthropomorphism-critique literature.** "Scholarly critiques of anthropomorphism" is directionally right; naming 2-3 well-known anti-anthropomorphism voices (Frans de Waal, Peter Godfrey-Smith, Elliott Sober on philosophy of biology, Jonathan Birch on edge of sentience) anchors Gemini in the right interpretive neighbourhood. Also: tighten overlap with bullet 1 (philosophy of mind) by reframing as "specifically the anti-anthropomorphism literature within philosophy of mind + ethology." | PROPOSED |

---

## Step 8 — Pass 1b Gemini (non_human_system variant)

**Mechanism:** LLM call · Google `gemini-2.5-pro` · identical config to Step 6
**Prompt:** `personas/flows/shared/prompts/persona_pass_1b_non_human_system.md` (18 lines)
**Verdict:** TUNE — lightest touch of all 4 Pass 1b variants. **Cleanest variant of the 4.** CARE + IPAI reference, "Do NOT speak FOR community" ethical boundary, comparative jurisdictions ask, and community-scholarship preference all already present. Mirror-pattern reflects the same high-engineering quality as Pass 1a non_human_system.

| ID | Severity | File | Change | Status |
|---|---|---|---|---|
| 1b-10 | LOW | `persona_pass_1b_non_human_system.md` (after line 15) | **Add soft length target:** "3-6K words; depth over length; substantive breadth." Mirror of 1b-03 / 1b-07. | PROPOSED |
| 1b-11 | LOW | `persona_pass_1b_non_human_system.md:13-14` | **Hostile-sources conditioning consistency.** Bullet 5 hard-codes colonial-administrative records as assumption regardless of `voice_config.hostile_sources` flag. Pass 1a non_human_system conditions its hostile-source block via `{% if hostile_sources %}`. Two options: (a) wrap bullet 5 in `{% if hostile_sources %}` for pipeline-consistency; (b) leave as-is but document as intentional design (non_human_system voices implicitly assume hostile records regardless of flag). Empirically Option B matches reality (legal-personhood entities almost always have colonial-administrative hostile records); Option A gives pipeline-level consistency. User call. | PROPOSED |
| 1b-12 | LOW | `persona_pass_1b_non_human_system.md:9-10` | **Complete comparative-jurisdictions list.** Bullet 3 names Ecuador, Bolivia, New Zealand, Colombia. Add: India (Uttarakhand 2017 Ganga/Yamuna + Supreme Court stay), Spain (Law 19/2022 Mar Menor), United States (Yurok Tribal Council 2019 Klamath). Aligns with Pass 1a non_human_system's line 280-283 list. | PROPOSED |

*Cross-reference note:*
- 1b-XREF: The CARE + IPAI reference here (line 8) is what 1b-08 proposed adding to the organism variant. **When implementing 1b-08, lift this variant's wording rather than introducing new phrasing** — standard-citation pattern should be consistent across all voice-type variants where applicable.

*Observation (not a fix):*
- This variant is the best-engineered of the 4 Pass 1b files. Reflects deliberate care in the non_human_system ethical space.

---

## Step 9 — Pass 1b Gemini (fictional variant)

**Mechanism:** LLM call · Google `gemini-2.5-pro` · identical config to Step 6
**Prompt:** `personas/flows/shared/prompts/persona_pass_1b_fictional.md` (21 lines)
**Verdict:** TUNE — light touch. Second-cleanest Pass 1b variant (after non_human_system). Voice-type tailoring is precise: philology + narratology + feminist literary theory + postcolonial critique + reception history cross-disciplinary set; textual-critical scholarship ask; orientalist-reception 2020-2026 critique target; "non-Western scholarship as PRIMARY rather than supplementary" is the strongest non-Anglophone framing of any Pass 1b variant.

| ID | Severity | File | Change | Status |
|---|---|---|---|---|
| 1b-13 | LOW | `persona_pass_1b_fictional.md` (after line 16) | **Add soft length target:** "3-6K words; depth over length; substantive breadth." Mirror of 1b-03 / 1b-07 / 1b-10. | PROPOSED |
| 1b-14 | LOW | `persona_pass_1b_fictional.md` (new bullet between current 3 and 4) | **Add translation-tradition-reception ask.** Currently bullet 3 covers textual-critical scholarship (stemma / variants / interpolations) but there's no dedicated ask for comparative-translation-reception criticism. These are different dimensions: stemma is manuscript genealogy; translation reception is how translator choices shape reader reception. For Scheherazade: Burton's Victorian-orientalist register vs. Haddawy's measured prose vs. Lyons's modern; for Russian characters: Garnett vs. Pevear-Volokhonsky vs. Ready. Gemini's cross-reference strength fits. New bullet text: "Comparative-translation-reception scholarship — how different translation traditions (translator, period, publisher) materially shape how the character has been received. Distinct from textual-critical philology (bullet 3)." | PROPOSED |

*Cross-template observation (not a fix):*
- 1b-XREF2: The "PRIMARY rather than supplementary" non-Anglophone framing (lines 20-21) is stronger than parallel wording in the other 3 Pass 1b variants. **Pattern worth lifting** to human / organism / system variants where non-Anglophone scholarship is structurally load-bearing.

---

## Step 10 — Pass 0b wrapper (`pass_0b_dr_prompt.md`)

**Mechanism:** Jinja2 `{% include %}` orchestration (no LLM call). Composes header + voice-type body + footer.
**Prompt:** `personas/flows/shared/prompts/pass_0b_dr_prompt.md` (17 lines)
**Verdict:** TUNE — light touch. Core architecture correct (clean header/body/footer decomposition with voice-type routing). Two small defensive improvements.

| ID | Severity | File:line | Change | Status |
|---|---|---|---|---|
| 0b-01 | MEDIUM | `pass_0b_dr_prompt.md:12` | **Make non_human subtype branching explicit.** Current line 12 `{% elif type == "non_human" %}` catches everything non_human that didn't match line 10's `subtype == "system"` — relies on elif ordering. If a future subtype is added (e.g. `cosmic`, `biome`), it would silently fall through to organism. Change to `{% elif type == "non_human" and subtype == "organism" %}` for explicit matching. | PROPOSED |
| 0b-02 | MEDIUM | `pass_0b_dr_prompt.md` (new `{% else %}` branch before line 16) | **Add defensive `{% else %}` fallback** for unrecognized type/subtype combinations. Currently silent-fallthrough: if `type` is None or an unexpected value, only header + footer render. Upstream `validate_input` catches enum violations but wrapper has no defence-in-depth. Emit a visible error string that will fail downstream validation loudly — e.g. `{% else %}\n{{ "ERROR: unrecognized type=" ~ type ~ " subtype=" ~ (subtype|default('null')) }}\n{% endif %}`. Jinja doesn't natively support raise, so emit-and-detect-downstream is the pragmatic path. | PROPOSED |
| 0b-03 | LOW | `pass_0b_dr_prompt.md:2-5` | **Consider updating or removing the pre-decomposition reference to commit 84cf26f.** Now ~30 commits deep in git history; archaeological note has limited ongoing value. Either remove the reference entirely (simplest) or update the comment to reference the Phase B restructure era rather than a specific commit hash that ages poorly. LOW priority. | PROPOSED |

*Observation (not a fix):*
- Runner-level `undefined=jinja2.Undefined` (not `StrictUndefined`) in `run_phase0_1_research.py:228` is a silent-failure risk for variable typos in any of the included templates. Tracked separately as an environment-config issue, not added here.

---

## Step 11 — Pass 0b header (`pass_0b_header.md`)

**Mechanism:** Jinja include template, no LLM call. Provides operator preamble + RESEARCH DISCIPLINE block, branches on `section_mode`.
**Prompt:** `personas/flows/shared/prompts/pass_0b_header.md` (83 lines)
**Verdict:** TUNE. 4 fixes — 1 MEDIUM load-bearing (model-per-section policy), 3 maintenance-level.

| ID | Severity | File:line | Change | Status |
|---|---|---|---|---|
| 0b-04 | MEDIUM | `pass_0b_header.md:8` (section_mode branch) | **MODEL-PER-SECTION POLICY NOT REFLECTED.** Current line 8 instructs "Claude Opus 4.6" for all sections. Phase L finalized policy: §1-§5 on Opus 4.6, §6 on Opus 4.7 (per `_workspace/planning/OPEN_ITEMS.md` §"PHASE L COMPLETE"). Add conditional: `{% if section_index == 6 %}Claude Opus 4.7 (required for §6 — Phase L empirical finding: 4.6 produced reader's-intro rather than corpus-gateway output on §6){% else %}Claude Opus 4.6 (Phase B empirically validated for §1-§5){% endif %}`. **Cross-references 0a-01 — should land as coordinated edit.** | PROPOSED |
| 0b-05 | MEDIUM | `pass_0b_header.md` (lines 50-83, monolithic-mode branch) | **Monolithic branch needs investigation + likely removal or consolidation.** Phase B made per-section default, but the runner renders with `section_mode` unset → monolithic branch fires during base render. `split_tailored_prompt.py` then re-renders with `section_mode=true` per section. Question: does the monolithic preamble survive the tailor → split pipeline or is it orphan content? **Action**: trace flow before deciding delete vs. keep. If monolithic preamble is orphan, remove branch entirely (~33 lines saved). If still needed for edge-case monolithic paths, also update its model instruction (line 53) to match model-per-section policy (instruct 4.6 as primary since monolithic mode doesn't differentiate §6). | PROPOSED |
| 0b-06 | LOW | `pass_0b_header.md` (lines 30-45 + 63-77) | **DRY the duplicate RESEARCH DISCIPLINE blocks.** Two near-identical 6-bullet lists with wording drift between them (synthesis-trigger, scholars-examples, depth — all slightly different). Maintenance risk: fix to one may not land in the other. Extract to a shared `pass_0b_research_discipline.md` partial and `{% include %}` from both branches, or use a Jinja macro. If 0b-05 deletes the monolithic branch, this fix partially obsoletes. | PROPOSED |
| 0b-07 | LOW | `pass_0b_header.md:25` | **Section-mode final-step pipeline command doesn't mention `--project` flag.** Monolithic branch line 59 includes `(add --project <path> to override the env-var default)`. Section-mode line 25 omits it. Consistency fix. | PROPOSED |

*Observations (not fixes):*
- **Step-renumbering fragility** (lines 16/18/20/22/24 use `{{ (N if section_index == 1 else N-1) }}`). If early steps change, manual update needed on subsequent step numbers. Works but maintenance-fragile. Not a fix — more a "watch when editing" flag.
- **Cross-references 0a-01 + 0b-04:** same model-per-section fix needed in two files. Should be applied as a coordinated edit so operator instructions don't drift.

---

## Step 12 — Pass 0b human body (`pass_0b_human.md`)

**Mechanism:** Jinja include, no LLM call. Voice-type-specific body for `type == "human"`. Thematic-questions research prompt for Claude DR.
**Prompt:** `personas/flows/shared/prompts/pass_0b_human.md` (148 lines)
**Verdict:** TUNE — most thoroughly-engineered of the 4 Pass 0b voice-type bodies. Phase B thematic-questions rewrite is sound; Boddice integration live; SWAP TEST + Khanmigo anchor load-bearing. 3 fixes.

| ID | Severity | File:line | Change | Status |
|---|---|---|---|---|
| 0b-08 | MEDIUM | `pass_0b_human.md:74-76` | **§4 primary-text-access reality clarification.** Current line 76 says "Voice lives in the primary texts, not in scholarly summary. Ground every observation in specific passages from the figure's own writing." Correct principle but Claude DR can't read primary texts directly — it surfaces scholarly analyses + paraphrased quotes. Add clarifying sentence after line 76: "Your job here is to surface scholarly readings of the voice AND point to the primary passages where scholars ground their readings; primary-text-based voice construction happens at Pass 4a drawing on Pass 1c fetches." Makes expectation honest and prevents DR from hallucinating primary-text analysis. | PROPOSED |
| 0b-09 | LOW | `pass_0b_human.md:70` | **§3 step-ordered enumeration pressure.** "Produce a step-by-step process grounded in how the figure actually handled novelty in documented cases" forces sequential shape that's artificial for scenic-incarnational reasoners (Dostoevsky), aphoristic (Nietzsche), parable-driven. Mirror of fix 1a-03. Soften to: "a process (step-ordered where the figure's actual method has ordered structure, clustered/thematic where the figure's reasoning is scenic/aphoristic/parabolic)." | PROPOSED |
| 0b-10 | LOW | `pass_0b_human.md:30` | **§1 last question duplicates Pass 0a editorial territory.** "What perspective does this figure bring that no other panel voice brings — the ONE thing the panel would lose if this voice were dropped?" is `editorial_rationale` / `unique_contribution` — Pass 0a curator territory, not DR research. Reframe to research territory: "What scholarly framing of the figure's unique contribution has scholarship converged on? (e.g., Arendt's labor/work/action distinction as a contribution no other 20th-C political theorist made.)" Keeps the value-add (scholarly uniqueness framing) without duplicating editorial decision. | PROPOSED |
| 0b-11 | LOW | `pass_0b_human.md:8` | **Sharpen opening paragraph's prose-vs-extraction boundary.** Current: "substantive, cited, period-vocabulary-imbued narrative, not structured output." Add: "Prose, not JSON. Narrative, not bullet-list. If you find yourself producing 'Field N: ...' lines, stop — that's the downstream merge's job." Stronger anti-extraction-mode boundary (Phase B rewrite's core concern). | PROPOSED |
| 0b-21 | MEDIUM | `pass_0b_human.md` (new `{% if hostile_sources %}` block before §1, ~15-25 lines) | **Add top-positioned RECONSTRUCTION DISCIPLINE block** for hostile-sourced human voices — **applies to Cleopatra in current panel**. Parallels the system body's INDIGENOUS REPRESENTATION ETHICAL FRAMING and the fictional body's NARRATIVE-FUNCTION FRAMING (see 0b-XREF1, 0b-XREF2). Block contents: "Primary material is fragmentary; hostile sources (enemies, colonisers, rival powers) dominate the record; lead with [reconstruction] scholarship; name what hostile sources were motivated to distort; surface counter-traditions; do not invent interior life the sources don't document (parallels fictional body's 'do not invent biography' discipline — see 1a-XREF6)." Jinja-conditional on `hostile_sources=true`. The footer has a hostile-sources block but it's placed AFTER the body questions; positioning this RECONSTRUCTION DISCIPLINE block BEFORE §1 shapes all section answers, matching the pattern of the system + fictional variants. | PROPOSED |

*Observations (not fixes):*
- §4 has 9 sub-questions + SWAP TEST block — densest section. For well-documented figures this earns the density; for less-documented (Lovelace, Ibn Battuta's intellectual-range), coverage may thin. Acceptable.
- No `{% if hostile_sources %}` branching in body. Hostile-source discipline handled via footer + Pass 0b tailor's voice-specific follow-up injection. Defensible design — body stays voice-type-generic.
- No `voice_mode` branching (philosophical / observational / narratival). Appropriate at research stage; downstream generation branches on it.
- **Cross-reference to Pass 1a human (Step 2):** thematic structure parallels Pass 1a's 6 sections exactly. Complementary research tiers hitting same 6 areas from different directions (Perplexity citation-density + Claude DR narrative synthesis).

---

## Step 13 — Pass 0b non_human_organism body (`pass_0b_non_human_organism.md`)

**Mechanism:** Jinja include, no LLM call. Voice-type-specific body for `type == "non_human"` + `subtype in ("organism", null)`. Thematic-questions research prompt, science-grounded.
**Prompt:** `personas/flows/shared/prompts/pass_0b_non_human_organism.md` (147 lines)
**Verdict:** TUNE — rigorous voice-type transposition of human body. Anti-anthropomorphism explicit, Umwelt + hard-problem-of-consciousness well-referenced, body-level disagreement protocol elegantly reframed. 5 fixes.

| ID | Severity | File:line | Change | Status |
|---|---|---|---|---|
| 0b-12 | MEDIUM | `pass_0b_non_human_organism.md:9-11` | **Mirror 0b-11: sharpen opening paragraph's prose-vs-extraction boundary.** Add after line 11: "Prose, not JSON. Narrative, not bullet-list. If you find yourself producing 'Field N:...' lines, stop — that's the downstream merge's job." Cross-template consistency with human body; same anti-extraction-mode concern. | PROPOSED |
| 0b-13 | LOW | `pass_0b_non_human_organism.md:75` | **§3 last question misplaced.** "What cannot be determined from current research — the open questions, where scientists disagree, where observation is insufficient?" sits at end of RELATIONAL PATTERNS but is really about scientific unknowns. Move to §2 PERCEPTUAL WORLD (where cognitive debates live) OR §5 PHILOSOPHICAL AND LEGAL FRAMEWORKS (where epistemic limits already appear). §2 is better fit. | PROPOSED |
| 0b-14 | LOW | `pass_0b_non_human_organism.md:111` | **§5 philosophical moral-status literature is Anglophone-heavy.** Current list (Singer, Regan, Nussbaum, Gruen, Donaldson-Kymlicka, Birch) misses non-Anglophone philosophy-of-animals tradition. Add: Vinciane Despret (*What Would Animals Say If We Asked the Right Questions?*), Dominique Lestel (*Les Origines Animales de la Culture*), Derrida's *The Animal That Therefore I Am*. Broadens the literature ask and uses Gemini's multilingual-scholarship strength (cross-ref to Pass 1b organism's non-Anglophone fix 1b-09). | PROPOSED |
| 0b-15 | LOW | `pass_0b_non_human_organism.md:113` | **§5 Indigenous perspectives guardrail doesn't cite CARE Principles / IPAI standards.** non_human_system variant references CARE + IPAI (Carroll et al. 2020; Lewis et al. 2020) explicitly; organism variant doesn't. Same ethical concern applies. Add references to align cross-template discipline. Cross-references 1a-XREF3 and 1b-XREF. | PROPOSED |
| 0b-16 | LOW | `pass_0b_non_human_organism.md:29` | **§1 "ONE formative condition" sharpening.** Current framing is correct ("NOT trauma; the condition itself") but could add explicit Boddice §14 non-human variant schema-vocabulary. Add: "— this becomes the voice's `condition_of_being` per Pass 1.1 schema." Aligns with downstream handoff. | PROPOSED |

*Observations (not fixes):*
- **Cephalopod-specific examples throughout** (lines 21, 31, 49, 71, 85, 95, 109, 113, 121, 141) with "For other organisms: the equivalent" guidance. Operator-adaptation burden high if panel expands beyond Octopus. Current panel has only Octopus, so acceptable.
- **§4 characteristic stance (line 101)** uses voice-type-generic descriptors (curious/withdrawing/alert-then-still). For Octopus specifically: attending-distributed-across-body / exploring-via-arms / display-rich. Not a fix — observational.
- **Same architectural parallel with Pass 1a non_human_organism:** 6 sections mapping onto Pass 1.1-1.6 chunks, voice-type-specific section names. Complementary research tiers.

---

## Step 14 — Pass 0b non_human_system body (`pass_0b_non_human_system.md`)

**Mechanism:** Jinja include, no LLM call. Voice-type-specific body for `type == "non_human" and subtype == "system"`. Thematic-questions research prompt with Indigenous Representation Ethical Framing.
**Prompt:** `personas/flows/shared/prompts/pass_0b_non_human_system.md` (185 lines — longest of the 4 voice-type bodies)
**Verdict:** TUNE — **lightest touch of the 4 Pass 0b bodies.** This is the **most ethically-engineered** of the voice-type bodies. CARE + IPAI referenced operationally throughout; 5 explicit ethical rules; ontological framing ("system has no cognition") correctly anchors voice construction; dual-register vocabulary explicit. 2 fixes.

| ID | Severity | File:line | Change | Status |
|---|---|---|---|---|
| 0b-17 | MEDIUM | `pass_0b_non_human_system.md:15-17` | **Mirror 0b-11 / 0b-12: sharpen opening paragraph's prose-vs-extraction boundary.** Add after line 17: "Prose, not JSON. Narrative, not bullet-list. If you find yourself producing 'Field N:...' lines, stop — that's the downstream merge's job." Cross-template consistency. | PROPOSED |
| 0b-18 | LOW | `pass_0b_non_human_system.md:63 + 85` | **§1 and §2 last questions partially duplicate system-specificity ask.** Both ask "what distinguishes this system from others in the same category" (§1 line 63 focuses on legal-framework differentiation: "Te Awa Tupua is not the Ganges"; §2 line 85 focuses on ecological-category differentiation: "any NZ river vs. Whanganui specifically"). Minor redundancy — could consolidate into one section-level ask, or make the distinction explicit. | PROPOSED |

*Cross-template observation (GOLD-STANDARD PATTERN TO LIFT):*
- **0b-XREF1:** The **INDIGENOUS REPRESENTATION ETHICAL FRAMING block** at lines 21-41 (CARE + IPAI explicit citations + 5 operational rules + "synthesis of published Indigenous governance philosophy" framing) is the **most thorough ethical framing pattern** anywhere in the pipeline. Positioned BEFORE Section 1 starts — structural move unique to this variant.
  - **Lift to organism variant** (`pass_0b_non_human_organism.md`): abbreviated version applies to Indigenous TEK handling at §5 line 113 (already targeted by fix 0b-15 for CARE/IPAI references; this XREF identifies the structural pattern — a dedicated framing block before Section 1 rather than inline mention).
  - **Partial lift to human variant** (`pass_0b_human.md`): for community-scholarship-sensitive voices (Marley's Rastafari community; Ibn Battuta's Islamic-jurist community; potentially Scheherazade's 1001 Nights oral tradition via fictional variant), a subset of the "name specific community / prefer community-authored scholarship / surface internal disagreements" rules would harden scholarly-sourcing discipline.

*Observations (not fixes):*
- **§3 Andean scholar list** (line 33 + context) is thin beyond Whanganui specifics. Walsh, Gudynas named. Other relevant ontological-turn / political-ontology scholars (Viveiros de Castro, de la Cadena, Blaser, Escobar) missing. **Not a fix for current Whanganui-only panel** — monitoring note for future system-voice expansion. Same gap also flagged in Step 4 observations (Pass 1a non_human_system).
- **§5 philosophical literature list** (line 149) Western-legal-tradition-heavy. Indigenous legal theory (line 151) covers community-internal; Western-philosophy bin stays Western. Acceptable separation.
- **§4 characteristic stance examples are Whanganui + Pachamama only.** Acceptable for current panel.

---

## Step 15 — Pass 0b fictional body (`pass_0b_fictional.md`)

**Mechanism:** Jinja include, no LLM call. Voice-type-specific body for `type == "fictional"`. Thematic-questions research prompt with Narrative-Function Framing.
**Prompt:** `personas/flows/shared/prompts/pass_0b_fictional.md` (180 lines — second-longest of the 4 voice-type bodies)
**Verdict:** TUNE — light touch. **Second-most-ethically-engineered** of the 4 bodies (after non_human_system). Translation-tradition awareness is sharp; narrative-function framing is gold-standard; §4 "voice is text-as-rendered-in-translation-tradition" is the most honest framing across all 4 bodies. 2 fixes.

| ID | Severity | File:line | Change | Status |
|---|---|---|---|---|
| 0b-19 | MEDIUM | `pass_0b_fictional.md:12-17` | **Mirror 0b-11 / 0b-12 / 0b-17: sharpen opening paragraph's prose-vs-extraction boundary.** Add after line 17: "Prose, not JSON. Narrative, not bullet-list. If you find yourself producing 'Field N:...' lines, stop — that's the downstream merge's job." Cross-template consistency. | PROPOSED |
| 0b-20 | LOW | `pass_0b_fictional.md:56` | **§1 last question on unique panel contribution — framing is already good (narrative-function research territory, not editorial) but could be marginally sharper.** Current: "What perspective does this character bring that no other panel voice brings..." Rephrase opening phrase to "What scholarly framing identifies the character's unique narrative function...?" Tighter research-territory framing. Mirror of 0b-10 for human body but lighter touch since the framing here is already more defensible. | PROPOSED |

*Cross-template observation (GOLD-STANDARD PATTERN PAIR):*
- **0b-XREF2:** The **NARRATIVE-FUNCTION FRAMING block** (lines 20-33) is the fictional-variant parallel to the system body's **INDIGENOUS REPRESENTATION ETHICAL FRAMING** (see 0b-XREF1). Both are positioned BEFORE Section 1; both establish structural discipline for the entire body; both have 5 explicit operational rules defining what the voice CAN'T do (not biography for fictional; not speaking-for-community for system). **These two blocks are the "gold-standard framing pattern" in the pipeline.**
  - For the **human body**: no equivalent top-positioned block exists. For **hostile-sourced human voices (Cleopatra — IN CURRENT PANEL)**, a similar RECONSTRUCTION DISCIPLINE block would be valuable ("primary material is fragmentary; lead with [reconstruction] scholarship; hostile Roman sources require reading-against-grain"). **Promoted to a concrete proposed fix: 0b-21 below.**
  - For the **organism body**: §5 already has CARE+IPAI guardrails for Indigenous TEK handling (fix 0b-15 proposes strengthening). Could consider a top-positioned ANTI-ANTHROPOMORPHISM DISCIPLINE block that consolidates the scattered anti-anthropomorphism language currently spread across lines 11, 13-18, 33, 55. Would require restructuring — flagged for future-rewrite consideration, not immediate fix.

*Observations (not fixes):*
- **§4 "voice is text-as-rendered-in-a-translation-tradition"** (line 106) is the most honest framing of voice-source across all 4 Pass 0b bodies. Human body's equivalent ("voice lives in primary texts, not scholarly summary") is cleaner-sounding but less honest — DR can't read primary texts directly. Fictional body's framing is better and should probably inform a rewording of the human body's §4 opener.
- **Scheherazade-specific examples dominate** throughout, with parenthetical alternatives (Hamlet, Antigone, Aeneas, Anansi, Sun Wukong, Ariadne) consistently provided — good template-scalability design. Acceptable for current panel.
- **§1 last question (unique panel contribution)** framing here is RESEARCH-territory (narrative-function uniqueness as scholarly reading) better than human body's equivalent (which was editorial-adjacent). Worth noting the good pattern.

---

## Step 16 — Pass 0b footer (`pass_0b_footer.md`)

**Mechanism:** Jinja include, no LLM call. Shared tail appended to all 4 voice-type bodies: hostile-sources conditional + musical-voice conditional + OUTPUT FORMAT (shared).
**Prompt:** `personas/flows/shared/prompts/pass_0b_footer.md` (45 lines)
**Verdict:** KEEP. Well-constructed. 1 observation about potential simplification once 0b-21 lands; no urgent fixes.

**No new fixes proposed.** Footer is structurally correct:
- Hostile-sources block has right 3-tier tag discipline (`[hostile_source: <bias>]` / `[reconstruction: <scholar>]` / `[own_voice]`) with "LEAD with reconstructed + own-voice" order-inversion
- Musical-voice block handles Marley's `corpus_constraint == "lyrics_patterns_only"` correctly with two-tier corpus design + HANDOFF.md contract reference
- OUTPUT FORMAT has anti-extraction-mode boundary ("NOT a persona card") + `dr_validation.py` reference + tag discipline + depth-over-length
- Section-mode conditional correctly differentiates per-section vs. monolithic heading organisation

*Observation (not a fix):*
- **0b-FOOTER-OBS:** Once fix 0b-21 lands (top-positioned RECONSTRUCTION DISCIPLINE block in human body), the footer's hostile-sources block (lines 3-20) becomes partially duplicated for human voices. **Recommend keeping footer block as-is** — it's a belt-and-braces post-body tag-reminder and still handles non-human organism/fictional voices with `hostile_sources=true` (not currently triggered in panel but architecturally possible). Simplification would require voice-type-conditional logic that's not worth the complexity. Defensible either way; keep-as-is is simpler.

*Other observations:*
- Cross-reference with 0b-21: footer + top block are complementary. Top block shapes question-answering; footer reminds at tag-application time.
- Marley is the only panel voice triggering the MUSICAL VOICE block.
- Line 30 "two-tier corpus design" reference could add HANDOFF.md path for operator convenience, but low-priority maintenance note.

---

## Step 17 — Pass 0b tailor (`pass_0b_tailor.md`)

**Mechanism:** LLM call · Anthropic `claude-opus-4-7` · adaptive thinking · max_tokens=40000 · temperature=1.0 · response_format_json=True · streaming
**Prompt:** `personas/flows/shared/prompts/pass_0b_tailor.md` (166 lines)
**Verdict:** KEEP — most architecturally well-engineered of the Phase 0.5 prompts. Phase B rewrite from coverage-notes to targeted follow-up questions is architecturally sound; guardrail set (0-2 scholars/question cap, 2-3 questions/section, voice-specific not generic, don't invent gaps) directly counters documented DR failure modes. Dostoevsky worked example is rich and demonstrative. Empirically validated by Phase L run. 2 low-priority fixes.

| ID | Severity | File:line | Change | Status |
|---|---|---|---|---|
| 0b-22 | LOW | `pass_0b_tailor.md:98` | **Add `voice_mode` to voice_config flag respect rule.** Current: "for `hostile_sources=true`... `corpus_constraint=lyrics_patterns_only`... `type=non_human` or `fictional`." Missing voice_mode. For Dostoevsky (narratival), tailor should emphasize narrative-structural questions (scenic collision / porog / vdrug) differently from philosophical-human voices (Plato, Arendt, Audrey Tang) or observational human voices (Ibn Battuta). Add: "for `voice_mode=narratival`, questions may emphasize narrative-structural dimensions (scenic units, characteristic moves at narrative level); for `voice_mode=observational`, questions may emphasize perception-and-description over argument." 1-2 line addition. | PROPOSED |
| 0b-23 | LOW | `pass_0b_tailor.md:68-76` | **Consider adding 1-2 additional worked examples beyond Dostoevsky §1.** Current single example is for Russian-literary narratival human voice with hostile_sources=false. For Whanganui (non_human system with CARE+IPAI concerns), Cleopatra (hostile_sources=true), or Octopus (non_human organism), the example doesn't directly transfer. Operator/Opus 4.7 must extrapolate. Adding one worked example for a non_human voice (Octopus §1 ECOLOGICAL FOUNDATION) and one for a hostile-sourced voice (Cleopatra §1 BIOGRAPHICAL FOUNDATION) would demonstrate the pattern range. Trade-off: 30-50 more lines. Low-priority — Opus 4.7 with strong instruction-following should extrapolate from one rich example. | PROPOSED |

*Observations (not fixes):*
- **This is the Phase 0.5 capstone LLM call** — only Opus 4.7 synthesis pass in the research-generation workflow. Quality here directly determines whether DR gets voice-specific depth or generic coverage.
- **Cost sweet-spot:** $1.50-3.00/voice × 12 = ~$18-36 total for voice-specific depth injection. Proportional to value.
- **Hybrid Jinja+LLM is the right architecture** for this task — Jinja assembles context, LLM does synthesis. Neither alone would work.
- **Empirically validated** by Phase L Dostoevsky run (12 substantive per-voice edits produced).
- **Gemini-labeled-SECONDARY** (line 152) stays correct per research sanity-check (Step 6) — Gemini remains breadth-scan tier, no relabeling needed since Pass 1b elevation was rejected.
- **Line 94 "Do NOT rewrite the section asks"** is the load-bearing boundary between tailoring and regeneration. Could be promoted to more prominent position but works as-is.
- **tailoring_notes[] audit log** has no Pydantic validation downstream — soft-JSON only. Not load-bearing since it's audit-only, not pipeline input.

---

## WAVE 1 COMPLETE — SUMMARY

**Coverage:** Phase 0 + Phase 0.5 — 17 steps reviewed. Pass 0a (voice config) · Pass 1a (4 Perplexity variants) · Pass 1b (4 Gemini variants) · Pass 0b wrapper · Pass 0b header · 4 Pass 0b body variants · Pass 0b footer · Pass 0b tailor.

**Totals:**
- **53 fixes logged** across 17 steps
- **1 rejection** (1b-01 — user preference: keep gemini-2.5-pro)
- **3 retracted** (1b-R1/R2/R3 — research-misaligned elevation proposal)
- **Several XREF observations** (cross-template patterns: 1a-XREF1 through 1a-XREF6; 1b-XREF1, 1b-XREF2; 0b-XREF1, 0b-XREF2)

**Severity distribution:** 0 CRITICAL · 0 HIGH · ~22 MEDIUM · ~28 LOW. No blockers.

**Key findings across Wave 1:**

1. **Phase B thematic-questions rewrite is architecturally sound** — the convergence-trap countermeasure holds up across all variants.

2. **Ethical-framing quality varies by voice-type body:** non_human_system (Indigenous Representation Ethical Framing) + fictional (Narrative-Function Framing) are gold-standard; human + organism bodies lack equivalent top-positioned blocks. Fix 0b-21 adds RECONSTRUCTION DISCIPLINE block to human body for Cleopatra.

3. **4 mirror fixes across Pass 1a variants** for internal contradiction (per-section floor vs. depth-not-breadth). Should land as one coordinated edit.

4. **4 mirror fixes across Pass 0b bodies** for anti-extraction-mode boundary sharpening. Should land as one coordinated edit.

5. **Model-per-section policy not reflected in prompts** (0a + 0b header) — 2 coordinated fixes across Pass 0a line 115 and Pass 0b header line 8.

6. **Pass 0b tailor is the architectural high point** of Phase 0.5 — well-engineered hybrid. Minor fixes only.

7. **Gemini stays in breadth-scan lane** per research sanity-check — 4 Pass 1b variants get narrow tuning (hostile-sources block, soft length target, Boddice framing, sharpened bullets). Total 13 fixes across Pass 1b family.

8. **Cross-template XREF harmonization** identified 8 patterns where one variant's approach should inform others. Implementation pass should run a pattern-harmonization sub-pass alongside file-by-file edits.

**Phase 1 (merge) and Phase 2+ (generation / validation / derive) remain unreviewed.** This is the end of Wave 1 scope.

---

# WAVE 2 — Phase 1 merge + fetch + excerpt selection

## Step 18 — Pass 1c (Primary Text Fetch)

**Mechanism:** Pure deterministic Python — no LLM. Three sub-steps: URL harvest (from merged_dossier) → HTTP fetch → human review gate.
**Code:** `flows/shared/node1c_fetch.py` (97 lines) + `run_persona_pipeline.py:186-313` (orchestration)
**Verdict:** KEEP with low-priority tuning. Core design sound: no-LLM deterministic fetch with SSRF protection, Gutenberg stripping, review gate. Phase B improvement over v3.10 (dropped Sonnet URL-extraction call). 6 fixes, all LOW.

| ID | Severity | File | Change | Status |
|---|---|---|---|---|
| 1c-01 | LOW | `flows/shared/node1c_fetch.py:87-96` | **Parallelize `fetch_all`.** Currently sequential loop. For ~22 URLs × 2-5s each = ~1-2 min wall. Parallelize with `ThreadPoolExecutor(max_workers=4)` (same pattern as Pass 1a/1b) → ~15-30s. Perf only; not critical-path. | PROPOSED |
| 1c-02 | LOW | `flows/shared/node1c_fetch.py:87-96` | **Add one-retry-on-transient-error.** Current: first failure → record as error. Many URL failures are transient (network hiccup, server load spike). One retry with 10s backoff would catch easy cases. Pass 1a/1b have 2× retry; Pass 1c has 0 — inconsistent. Could have reduced Dostoevsky's 4-dead-URL count if some were transient. | PROPOSED |
| 1c-03 | LOW | `flows/shared/node1c_fetch.py:61-67` | **Expand boilerplate stripping beyond Gutenberg.** Perseus XML, Wikisource HTML, Internet Archive pages have their own consistent boilerplate. Currently comes through raw. Downstream Pass 1d handles curation → not a bug, but adding Perseus / Wikisource strippers would clean the intermediate corpus for easier operator review. Low priority. | PROPOSED |
| 1c-04 | LOW | `flows/shared/node1c_fetch.py:70-84` | **Add Content-Type inspection + HTML→text conversion.** Current: raw bytes decoded as UTF-8-ignore, regardless of whether Content-Type is HTML or plaintext. HTML URLs save with tags intact. Use BeautifulSoup when `Content-Type: text/html`. Also honour declared charset (Latin-1 older Gutenberg editions drop characters silently). | PROPOSED |
| 1c-05 | MEDIUM | `flows/shared/node1c_fetch.py:9-17 + 45-58` | **SSRF TOCTOU vulnerability is latent.** Docstring correctly flags: `gethostbyname` resolves hostname once, `urlopen` resolves again — DNS rebinding could return a private IP between calls. Acceptable for current vetted URL set (Wikipedia/Gutenberg/academic). **Becomes urgent if pipeline ever accepts user-provided URLs.** Fix: switch to `getaddrinfo` + pin resolved IP in a custom opener. Not immediate — monitoring note until URL-source policy changes. | PROPOSED |
| 1c-06 | LOW | `flows/shared/node1c_fetch.py:87-96` | **Add politeness rate limit.** `time.sleep(0.5)` between requests would reduce block risk on academic mirrors (Perseus, ФЭБ, Al-Maktaba). Current: fires as fast as Python loops. If parallelizing per 1c-01, apply per-domain rather than per-request. Minor. | PROPOSED |

*Observations (not fixes):*
- **Phase B architectural win:** v3.10 had a Sonnet LLM call for URL extraction (6-section markdown prose → URL list). Phase B's Pass 1.6 CORPUS chunk outputs structured URLs directly → extraction is now pure dict transformation. Saves ~$0.10-0.30/voice + ~30s wall + complexity.
- **Integration with Pass 1.6:** Pass 1c's input quality depends on Pass 1.6's URL output quality. Reviewed at Step 25.
- **Chain dependency:** Pass 4a (voice construction) ← Pass 1d (excerpt selection) ← Pass 1c (fetch) ← Pass 1.6 (URL list) ← Perplexity §6 + Claude DR §6 + Gemini §6. The chain matters for voice quality.
- **Review-gate pause is correct architectural choice** — LLMs can't validate correct-edition, correct-translation, copyright-compliance, paywall-status. Human-in-the-loop at this point is the right call.
- **No prompt file to review** — this is pure code. Review structure departs from prompt-review pattern.

---

## Step 19 — Pass 1d (Excerpt Selection)

**Mechanism:** LLM call · Anthropic `claude-sonnet-4-6` · max_tokens=4096 · temperature=0.0 · thinking=False · response_format_json=True
**Code:** `flows/shared/node1d_excerpt_selection.py` (51 lines) + `run_persona_pipeline.py:405-433` (orchestration)
**Prompt:** `persona_pass_1d_excerpt_selection.md` (46 lines)
**Verdict:** KEEP with low-priority polish. Clever peek-index + range-select architecture (Sonnet picks `char_start/char_end` from 200-char-per-5K-chars peek; deterministic Python applies). Sonnet is the right model (lookup task, not synthesis). ~$0.03-0.08/voice. 5 LOW fixes.

**SEVERITY RE-CALIBRATION (2026-04-21, post-review-challenge):** User pushed back on LOW verdicts. Honest re-examination found a real architectural weakness: Pass 1d uses char-offset indexing but dossier uses structural references (BK II.iv, §12-14, Act I scene 2). Sonnet has to translate structural-ref → char-range guess, without seeing full text. This is genuinely hard.

**Mitigating factor:** canonical voice-exemplars (`curated_corpus_passages` in assembled card) flow through Pass 1.6 `passages[]` + Pass 6 curation, NOT through Pass 1d. Pass 1d feeds Pass 4a (voice analysis, register, metaphorical repertoire, preferred vocabulary) — which needs broader primary-text context. So Pass 1d imprecision degrades voice-register-analysis input but doesn't lose canonical quotes. Upgrading severities from LOW but not to CRITICAL.

| ID | Severity | File | Change | Status |
|---|---|---|---|---|
| 1d-01 | **MEDIUM** (⬆ from LOW) | `flows/shared/node1d_excerpt_selection.py:18` | **Increase `INDEX_PEEK_CHARS` from 200 to 400-500.** 200 chars shows genre/register but not thematic content — mid-chapter peeks lack chapter markers, making structural-ref→char-range translation nearly impossible for Sonnet. Cost: ~2× index size (still fits Sonnet context). Materially better selection quality for dossier-named passages. | PROPOSED |
| 1d-02 | **MEDIUM** (⬆ from LOW) | `flows/shared/node1d_excerpt_selection.py:38-51` | **Add boundary-snapping in `apply_selections`.** If Sonnet picks `char_start=42000`, selection splits mid-paragraph. Mid-sentence splits degrade voice-analysis input (Pass 4a sees fractured register). Snap `char_start` back to nearest paragraph break; snap `char_end` forward to nearest paragraph break. ~10 lines. | PROPOSED |
| 1d-03 | LOW | `persona_pass_1d_excerpt_selection.md` | **Consider voice-type branching in prompt.** Current selection rules are voice-agnostic. For Octopus (scientific papers — abstract/methods/results), Whanganui (legislation — section structure), Scheherazade (frame-narrative — dawn-breaks), rules differ from human-literary voices. Add `{% if type %}` conditional rules. | PROPOSED |
| 1d-04 | LOW | `run_persona_pipeline.py:420` | **Bump `max_tokens` from 4096 to 8192.** For voices with 15+ selections × ~200 JSON tokens each = ~3K output, cuts close to 4096 ceiling. Bump has zero cost and prevents truncation. | PROPOSED |
| 1d-05 | LOW | `run_persona_pipeline.py:410-413` | **Verify Marley `lyrics_patterns_only` path.** Current SKIPPED behavior returns marker text. Marley's HANDOFF.md contract specifies two-tier corpus (public passages + `reference_only_passages`). Pass 1d currently skips entirely — private-reference corpus must come from elsewhere. Test before Phase N. | PROPOSED |
| **1d-06** | **HIGH (ARCHITECTURAL)** | `flows/shared/node1d_excerpt_selection.py` + runner | **Replace Sonnet range-select with fuzzy-match on Pass 1.6 quoted passages as PRIMARY path; fall back to current Sonnet approach for unmatched.** Pass 1.6 CORPUS output contains `passages[]` with verbatim `text` field (e.g., "Love in action is a harsh and dreadful thing compared with love in dreams..."). For each passage: (1) fuzzy-match against fetched primary_text via `difflib.SequenceMatcher` or normalized substring search; (2) when found, expand ±2000 chars for context; (3) deduplicate overlapping ranges; (4) cap at 30K chars prioritising by passage `purpose_tag` / tier. For passages where fuzzy-match fails (translator mismatch, paraphrase-only), fall back to Sonnet range-select. **Result:** canonical dossier-identified passages GUARANTEED present (no Sonnet guessing); surrounding context preserved; Sonnet call becomes optional fallback. ~50-100 lines of code. **This is the biggest quality-to-effort lever in Pass 1d.** The Sonnet call is doing work that deterministic string matching can do better, using data (verbatim quotes) that Pass 1.6 already produced. | PROPOSED |

**Why 1d-06 matters (expanded):**

Pass 1d exists because Pass 4a needs broader primary-text context than the 8-10 curated quotes — register analysis needs to see sentence cadence, paragraph-level structure, syntactic patterns across representative passages. But the CHOICE of which passages to expand context around is already encoded in the dossier: Pass 1.6 has picked the verbatim `passages[]`. The current design asks Sonnet to re-do that choice from a peek-index (lossy, error-prone) instead of using Pass 1.6's already-made decision as anchors.

The fuzzy-match approach treats Pass 1.6's passages as "seed points," expands context around each seed, and stops. Sonnet only runs when a seed can't be located (edition mismatch, paraphrase-only quote). This preserves the upstream effort (45-min DR session + Pass 1.6 merge) all the way through to Pass 4a voice construction.

*Observations (not fixes):*
- **Phase B improvement over v3.10:** pre-B was naive "first 80K chars" slice. Current is dossier-guided curated subset. Real quality lift over naive slice; BUT architectural weakness (char-offset vs. structural-ref mismatch) limits how well it can leverage upstream research.
- **Integration chain clarified:** Pass 1.6 passages → Pass 6 curated_corpus_passages (canonical voice-exemplars land here). Pass 1d → primary_block → Pass 4a voice analysis (register, metaphors, vocabulary extraction). Two separate flows. Pass 1d imprecision degrades the second but doesn't lose canonical quotes.
- **Cost sweet-spot:** Sonnet + peek-index is ~15-20× cheaper than full text. Fuzzy-match approach is ~∞× cheaper ($0 per voice) for matched passages, same Sonnet cost for unmatched fallback.
- **User's concern was valid:** 45min DR × 6 sections + Opus 4.7 tailoring + Pass 1.6 merge = substantial upstream investment. Pass 1d was the chokepoint where that investment could leak. 1d-06 closes that leak.

---

## Consolidated totals (updating live)

**By severity:**
- CRITICAL: 0
- HIGH: 2 (1d-06 fuzzy-match + 1-arch-01 curated_corpus_passages-from-Pass-1d architectural proposal)
- MEDIUM: 25
- LOW: 39
- REJECTED: 1 (1b-01 `GEMINI_MODEL` downgrade — user preference); earlier 1b-R1/R2/R3 elevation proposal retracted after research sanity-check

**By file:**
- `pass_0a_voice_config.md`: 4 fixes
- `persona_pass_1a_human.md`: 5 fixes
- `persona_pass_1a_non_human_organism.md`: 4 fixes
- `persona_pass_1a_non_human_system.md`: 2 fixes
- `persona_pass_1a_fictional.md`: 2 fixes
- `persona_pass_1b_human.md`: 4 narrow-tune fixes (1b-02 through 1b-05)
- `persona_pass_1b_non_human_organism.md`: 4 narrow-tune fixes (1b-06 through 1b-09)
- `persona_pass_1b_non_human_system.md`: 3 narrow-tune fixes (1b-10 through 1b-12)
- `persona_pass_1b_fictional.md`: 2 narrow-tune fixes (1b-13, 1b-14)
- `pass_0b_dr_prompt.md` (wrapper): 3 fixes (0b-01, 0b-02, 0b-03)
- `pass_0b_header.md`: 4 fixes (0b-04, 0b-05, 0b-06, 0b-07)
- `pass_0b_human.md`: 5 fixes (0b-08, 0b-09, 0b-10, 0b-11, 0b-21)
- `pass_0b_non_human_organism.md`: 5 fixes (0b-12, 0b-13, 0b-14, 0b-15, 0b-16)
- `pass_0b_non_human_system.md`: 2 fixes (0b-17, 0b-18)
- `pass_0b_fictional.md`: 2 fixes (0b-19, 0b-20)
- `pass_0b_footer.md`: 0 fixes (KEEP verdict)
- `pass_0b_tailor.md`: 2 fixes (0b-22, 0b-23)
- `flows/shared/node1c_fetch.py`: 6 fixes (1c-01 through 1c-06)
- `flows/shared/node1d_excerpt_selection.py` + `persona_pass_1d_excerpt_selection.md`: 6 fixes (1d-01 through 1d-06 — includes 1d-06 architectural fuzzy-match proposal; severity re-calibrated post review-challenge)

**🎯 WAVE 1 COMPLETE.** All 17 steps reviewed. Phase 0 + Phase 0.5 coverage.
**Wave 2 in progress.** Steps 18-19 reviewed.

**Panel composition confirmed (12 voices):** Scheherazade (fictional), Cleopatra (human, hostile_sources=true), Whanganui (non_human, system), Audrey Tang (human), Ibn Battuta (human), Fyodor Dostoevsky (human — Phase L validated), Hannah Arendt (human), Plato (human — Phase N first voice), Ada Lovelace (human), Peter Thiel (human, legal-risk-flagged), Bob Marley (human, corpus_constraint=lyrics_patterns_only), Octopus (non_human, organism).

**By status:**
- PROPOSED: 66 (incl. 1-arch-01 architectural refactor)
- APPROVED: 0
- REJECTED: 1
- RETRACTED: 3 (prior 1b-R1/R2/R3 elevation items — research-misaligned)
- APPLIED: 0
- DEFERRED: 0

---

*This doc grows with each reviewed step. When the review is complete, it's the single source of truth for the implementation pass.*
