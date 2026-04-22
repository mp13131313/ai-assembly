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

### 1-arch-03 — Additive merge architecture (supersedes 1-arch-02; reshapes Wave 3)

**Severity:** HIGH architectural — pivot point
**Status:** PROPOSED → implementation plan at `_workspace/planning/ARCH_03_ADDITIVE_MERGE_PLAN.md`
**Scope:** Pass 1.1-1.7 merge layer redesign; modest Pass 2-6 tuning; no Runtime side changes
**Effort:** ~2-3 days focused engineering + testing
**Recommended timing:** Before Phase N (avoid running 11 more voices on lossy architecture)

**Problem (2-paragraph summary):**

Current Pass 1.1-1.6 chunk schemas are **tight recipes** (`ReasoningMethod.steps[5-8]`, `Moves[3-6]`, `HardLimits[3-5]`, etc.). The LLM at merge must fit full per-section research (Perplexity §N + Claude DR §N + Gemini full) into these shapes. Content that doesn't fit gets dropped, not compressed-and-stored-elsewhere. Phase L Dostoevsky empirical measurement: 60-70% of Claude DR §3/§4/§5 analytical content is silently lost at merge. Carnivalization analysis, 14-item Menippean checklist, 4-of-5 scandal-scene instances, 3 worked demonstrations connecting life-events to novels, Holbein Basel 1867 formative-pressure-point, Williams-vs-Frank interpretive contrast — all in DR, none in merged_dossier, none surfaced at Pass 2-6.

This is a design error. The merge was positioned as "structure the research as near-card-field shape." It should be "consolidate three source dossiers into one coherent per-section dossier — additively, with redundancies stripped, contradictions reconciled, all unique content preserved." Pass 2-6 should do the synthesis-to-card-field work on rich source material.

**The architectural pivot:**

Two compression points → one compression point.

- **Current:** Raw research (412K) → Pass 1.1-1.6 compress to schema shapes (162K merged, loses 60-70% of §3/§4/§5) → Pass 2-6 synthesize to card fields
- **1-arch-03:** Raw research (412K) → Pass 1.1-1.6 additive consolidation (~350K merged, preserves all non-redundant content) → Pass 2-6 synthesize to card fields from richer source

Merge becomes: dedupe + reconcile + organize. Not compress-to-recipe. Rich merged_dossier preserves Claude DR investment ($30-60 operator labor × 6 sessions × 12 voices).

**Supersedes 1-arch-02:** the "Gemini lane-filter" concern in 1-arch-02 dissolves under additive merge — Gemini becomes full contributor alongside Perplexity + DR, with no per-chunk-filtering burden. Mark 1-arch-02 as RESOLVED-VIA-1-ARCH-03.

**Preserves 1-arch-01:** curated_corpus_passages routing is orthogonal; 1-arch-01 stays post-Phase-N deferred, composes cleanly.

**Implementation overview (full detail in plan doc):**
- Redesign Pydantic schemas as permissive containers (Boddice structure preserved, content capacity expanded, new AnalyticalContext containers capture scholarly-interpretive material)
- Rewrite 6 merge prompts with additive-merge discipline
- Update Pass 1.7 coherence with preservation-checks
- Bump Pass 2/3/4a/6 max_tokens to 32K (from 24K); Pass 1.7 to 100K (from 64K)
- Test on Dostoevsky Phase L fixtures; compare card quality; merge if ≥baseline

**Per-voice cost delta:** +$6-9. **Wall-time delta:** +5-10 min. **Quality hypothesis:** richer card fields (especially voice/engagement/reasoning); Pass 5 Gemini-flagged register drift hypothesized to resolve via richer CT upstream.

**Scope of Wave 3 fix triage under 1-arch-03** (full table at `ARCH_03_ADDITIVE_MERGE_PLAN.md` §9):

- **Wave 1 (53 fixes):** all SURVIVE. Pre-merge research layer unchanged.
- **Wave 2 (12 fixes + 1d-06 + 1-arch-01):** all SURVIVE. Post-merge primary-text layer unchanged.
- **Wave 3 (30 fixes + 2 SRIs):**
  - 6 Gemini-filtering MEDIUMs (1.1-01, 1.2-01, 1.3-01, 1.4-01, 1.5-01, 1.6-01): **OBSOLETE**
  - SRI-1 Gemini-noise-leakage watch: **OBSOLETE**
  - SRI-2 corpus-utilisation depth: **ABSORBED** (becomes preservation-rate metric, target ≥85%)
  - 1.1-05 ContestedReading prompt-schema mismatch: **OBSOLETE** (schema redesign resolves)
  - 1-arch-02: **SUPERSEDED**
  - Worked-example additions (1.1-02, 1.2-03, 1.3-02, 1.4-02, 1.4-03, 1.5-02, 1.6-02, 1.6-03, 1.6-04): all **ABSORBED** into 1-arch-03 new Block 4 structures
  - voice_mode disposition fixes (1.1-03, 1.4-04, 1.5-04, 1.6-06): **SURVIVES** independently
  - Period-vocabulary gradation (1.1-04, 1.3-03): **SURVIVES** as coordinated patch across 1.1/1.2/1.3
  - Fictional null-discipline (1.1-06, 1.5-03): **ABSORBED** into 1-arch-03
  - Pass 1.7 fixes (1.7-01/02/03/04): all **SURVIVES** per §5.3
- **Step 27 (Pass 2) fixes:**
  - 2-01 stale user prompt: **SURVIVES** (drift bug independent of architecture)
  - 2-02 voice_temporal_stance: **SURVIVES** (NEEDS-DECISION still)
  - 2-03 formative-candidate commit-to-ONE: **RESHAPED** (concern valid; fix reworded to reference 1-arch-03 preserved candidates + cross-refs)
  - 2-04 max_tokens monitor: **SUPERSEDED** (1-arch-03 bumps to 32K)

**Decisions needed before implementation:**
1. 2-02 voice_temporal_stance REWRITE/KEEP/DELETE (user call)
2. Wave 1 + 2 fix landing timing (Option A recommended: Wave 1+2 first on main, 1-arch-03 on branch after)
3. Implementation-session scope + merge-to-main authority

---

### 1-arch-02 — Gemini's per-chunk role is wrong-lane; re-route to either sectioned-per-chunk or coherence-only [SUPERSEDED by 1-arch-03]

**Severity:** HIGH (quality ceiling, not blocker)
**Status:** ~~PROPOSED~~ **RESOLVED-VIA-1-ARCH-03** — the underlying concern (Gemini's per-chunk lane-mismatch) dissolves under additive merge; Gemini becomes full contributor alongside Perplexity + DR without per-chunk-filtering burden.
**Scope:** `chunk_runner._load_sources()` + `pass_1_b_*.md` prompts (to require section headings if sectioned variant adopted) + Pass 1.7 prompt + token-budget on Pass 1.7 + PB#3 decision-log reversal/refinement

**Problem:**

Current architecture (per `chunk_runner.py:79-128`):
- Perplexity: section-N per chunk (via `perplexity_split.split_dossier()`)
- Claude DR: section-N per chunk (per-section mode, Phase-L-validated default)
- **Gemini: full, handed to every chunk**

Gemini is the only full-corpus feed per chunk. Each of chunks 1.1-1.6 reads the same ~15-50KB Gemini breadth-scan and must self-filter relevance — the per-chunk prompts carry an implicit relevance-filtering task on top of their main synthesis task.

**This is wrong-lane for Gemini per baseline File 4:**
- File 4 documents Gemini as "unusable for basic humanities research" at depth — strong at *breadth-first discovery, adjacency surfacing, multilingual-scholarship indexing, lineage connections*.
- File 4's tool-section table places Gemini as secondary for S1 (Identity) only, never as primary for any humanities section.
- Breadth/adjacency/cross-cutting material is **structurally a coherence-pass concern**, not a per-section synthesis concern.

The per-chunk relevance-filtering burden is real and unmeasured. Every chunk spends attention-budget filtering Gemini noise from its §N focus. Opus 4.7 filters well enough that we haven't seen catastrophic leakage on Dostoevsky — but the cost is invisible, and may surface as diffuse "off-register" material (Gemini-flavored phrasings, off-topic scholar name-drops) that's hard to trace back to its cause.

**Two variants, in order of conservatism:**

**Variant A — Gemini sectioned per chunk (like Perplexity + DR).**
- Apply `perplexity_split`-style section-heading logic to Gemini output.
- **Prerequisite:** `pass_1_b_*.md` prompts must mandate the same 6-section heading format Perplexity uses (`## 1. BIOGRAPHICAL FOUNDATION` etc.) — currently they don't.
- Preserves PB#3 three-way triangulation per chunk.
- Drops Gemini-noise-burden from 6 chunks to 1 topical slice per chunk.
- Implementation: ~1 hour prompt edits (Pass 1b family, 4 voice-type variants) + `flows/shared/gemini_split.py` mirroring `perplexity_split.py` + wiring in `chunk_runner._load_sources()`.

**Variant B — Gemini only at Pass 1.7 coherence.**
- Chunks 1.1-1.6 merge from Perplexity §N + Claude DR §N only (2 sources per chunk).
- Gemini (full) becomes an input to Pass 1.7 alongside the 6 chunk outputs.
- **Matches Gemini's actual documented strength** — cross-cutting / adjacency / lineage belongs structurally in coherence, not per-section synthesis.
- Violates PB#3 "each chunk reads ALL 3 sources" — requires a decision-log-level reversal, not a prompt tweak.
- Cost: Pass 1.7 token-budget pressure (currently 64K max_tokens post-Bug-5; adding full Gemini input may force another bump and input-side context pressure).
- Benefit: cleaner per-chunk focus (each chunk has 2 topical sources, not 2 topical + 1 full); Pass 1.7 gets the triangulation role it's already structured for (it edits chunk outputs to resolve flags).

**Variant A is the correct first move.** Less radical, preserves PB#3, addresses the main cost (per-chunk noise). Variant B is worth holding open as a second step if Variant A still shows evidence of Gemini lane-mismatch.

**Empirical test during voices 2-12:**

Add a standing review item to Steps 21-26 per-prompt reads: **watch chunk outputs for Gemini-noise-leakage signatures** — off-topic scholar mentions that trace to Gemini §X, phrasings that carry Gemini's register rather than Perplexity/DR depth, adjacent-topic material intruding into §N synthesis. If present on 1-2 voices beyond Dostoevsky, 1-arch-02 is empirically vindicated and Variant A lands post-Phase-N. If absent across 3-4 voices, current architecture's "Opus filters Gemini well" trust is vindicated and 1-arch-02 closes as REJECTED.

**Why not now:**
- Phase N is about to fire; Gemini re-routing would delay voice builds.
- Dostoevsky ran on current architecture to validation-complete — evidence of a leak is plausible but not blocking.
- Variant A's prerequisite (Pass 1b section-heading mandate) is a prompt edit that should run alongside the Wave-1 Pass 1b fixes (`1b-02` through `1b-14`), not separately.

**Why do it post-Phase-N:**
- At scale (12 voices × 6 chunks), the relevance-filtering burden compounds. If Variant A saves 5-10% of per-chunk attention, that's 60-120 chunks × small quality lift = measurable.
- Post-Phase-N cross-card review of all 12 voices will surface Gemini-leakage signatures if they exist; blind-spot-to-scale failure modes become visible with comparison.

**Cross-references:**
- Depends on: Wave-1 Pass 1b prompt fixes landing first (Variant A's section-heading prerequisite)
- Affects: `chunk_runner._load_sources()` · `pass_1_b_*.md` (4 variants) · `pass_1_7_coherence.md` (Variant B only) · PB#3 in REBUILD_PLAN (Variant B only)
- Validates via: empirical Gemini-noise-leakage signatures during voices 2-12 review

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
- HIGH: 3 (1d-06 fuzzy-match · 1-arch-01 curated_corpus_passages-from-Pass-1d · **1-arch-03 additive-merge architecture** — the pivot; supersedes 1-arch-02 which is now RESOLVED-VIA-1-ARCH-03)
- MEDIUM: 34 (+3 at Pass 2: 2-01 stale user prompt · 2-02 voice_temporal_stance REWRITE NEEDS-DECISION · 2-03 formative-candidate anchor-concentration)
- LOW: 62 (no change at Pass 2 — 2-04 is MONITOR only, not fix)
- **NEEDS-DECISION**: 1 (2-02 voice_temporal_stance keep/rewrite/delete — decision-gate before Phase N)
- **MONITOR**: 1 (2-04 max_tokens=24000 at Pass 2)
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
- `pass_1_1_merge.md`: 6 fixes (1.1-01 through 1.1-06; 1.1-01 MEDIUM feeds 1-arch-02 empirical test; 1.1-05 is a prompt-schema mismatch on `ContestedReading`; 1.1-06 closes null-discipline gap for fictional voices)
- `pass_1_2_merge.md`: 3 fixes (1.2-01 MEDIUM Gemini-filtering mirror with stronger positive framing; 1.2-02 makes voice_mode load-bearing for commitment-extraction; 1.2-03 Scheherazade fictional worked example)
- `pass_1_3_merge.md`: 3 fixes (1.3-01 MEDIUM Gemini-filtering mirror; 1.3-02 Dostoevsky narratival worked example — lift from Phase-L-validated card; 1.3-03 period-vocabulary gradation ripple coordinating with 1.1-04)
- `pass_1_4_merge.md`: 4 fixes (1.4-01 MEDIUM Gemini-filtering mirror; 1.4-02 Marley worked example completion — missing `moves`; 1.4-03 Octopus non-human organism worked example; 1.4-04 voice_mode load-bearing at register level)
- `pass_1_5_merge.md`: 4 fixes (1.5-01 MEDIUM Gemini-filtering mirror; 1.5-02 Cleopatra hostile-source worked example — high-stakes before Cleopatra Phase N build; 1.5-03 fictional-voice general_frame rule; 1.5-04 voice_mode drop — follows 1.1-03 irrelevant-here pattern)
- `pass_1_6_merge.md`: 5 fixes + 1 merged (1.6-01 MEDIUM Gemini-filtering with strongest positive framing — Gemini actively preferred for URL surfacing; 1.6-02 Octopus non-human organism example; 1.6-03 Scheherazade fictional multi-translator example — also resolves 1.6-05 translation_anchor; 1.6-04 Marley reference_only_passages private-tier demonstration; 1.6-05 resolved-via-1.6-03; 1.6-06 voice_mode drop completing cross-chunk policy). **1-arch-01 architecturally restructures this chunk if adopted post-Phase-N.**
- `pass_1_7_coherence.md`: 4 fixes, all LOW (1.7-01 add BLOCK 4 WORKED EXAMPLES — pattern-break repair; 1.7-02 edit-scope discipline; 1.7-03 escalation-pathway documentation; 1.7-04 productive-tension criteria). **Genuinely not rubber-stamp** — 7 operational checks + 3-category resolution policy + real chunk-output edits + Phase-L-validated. Wave 3 architecture verdict vindicated at per-prompt level.
- `persona_pass_2_identity_boundaries.md` + `persona_pass_2_user.md`: 3 MED fixes + 1 MONITOR (2-01 stale user prompt — drift bug, 1-min edit; 2-02 voice_temporal_stance REWRITE as deployment-configurable — NEEDS-DECISION, decision-gate before Phase N; 2-03 formative-candidate commit-to-ONE anchor-concentration reword; 2-04 max_tokens=24K monitor). Phase M learnings baked in; Phase-L-validated on Dostoevsky.

**🎯 WAVE 1 COMPLETE.** All 17 steps reviewed. Phase 0 + Phase 0.5 coverage.
**Wave 2 complete.** Steps 18-19 reviewed.
**🎯 WAVE 3 COMPLETE.** Steps 20-26 reviewed. Phase 1 chunked merge + coherence coverage done.
**Wave 4 in progress.** Step 27 Pass 2 reviewed.

---

## Forward-references parked for later waves

Observations surfaced during Waves 1-3 that can't be resolved at their originating step but need to be re-examined when the relevant later-wave step fires. Checked at the opening of each wave.

### For Wave 4 (Pass 2-6 + Coherence Threading)

- **Zosima-overanchoring risk at Pass 2 (commits-to-one).** Pass 1.1 surfaces 2-5 formative candidates ranked by `scholarly_support_score: strong|moderate|contested`. Pass 2 commits to ONE. For well-documented voices (Dostoevsky: 6 major candidates), the compression from "breadth surfaced" to "one chosen" is where anchor-concentration risk concentrates downstream. *Originated at Step 20 (1.1).* **Ask at Pass 2 review:** does the Pass 2 prompt direct the LLM to weigh competing candidates against voice-function (engagement_it_drives) rather than defaulting to highest scholarly_support_score? Is there anti-anchor guidance?
- **Zosima-overanchoring at Pass 2 commitment selection.** Pass 1.2 surfaces 10-20 commitments with specificity-rule discipline; Pass 2 then produces a persona card `constitution` with 10-20 principles. 1:1 mapping means selection happens at synthesis, not generation. *Originated at Step 21 (1.2).* **Ask at Pass 2/3 review:** how does the compression actually happen — does Pass 2 preserve breadth or does it silently narrow to anchor-themes?
- **`coherence_flags[]` + `coherence_resolutions[]` downstream use.** Pass 1.7 emits these as first-class audit fields on `merged_dossier.json`. Do Pass 2-6 prompts actually read and respond to them, or are they ignored at synthesis? *Originated at architecture confirmation (Step 20 preamble).* **Ask at each Pass 2-6 review:** does the prompt reference `coherence_flags` from the merged_dossier or bypass them?
- **Merged dossier size vs. Pass 2-6 consumption.** Dostoevsky's `merged_dossier.json` is the sole input to Pass 2-6 synthesis (plus `primary_block` to Pass 4a). Whether Pass 2-6 prompts actually read the full dossier or short-circuit on a few fields is the symmetric concern to "is research used well at merge." *Originated at Q5 (architecture preamble).*
- **`voice_temporal_stance` field — keep/rewrite/delete decision.** Added during Phase M from chat-test learning (Dostoevsky "twenty-eight years after Sonya" error). Athens deployment brief is "impossible participants take the floor while you sleep" — fluid-across-time. The 1881 anchor may be over-specified for runtime. *Originated at task description.* **Decision must land before Phase N voice builds.** Wave 3/4 boundary. **LANDED AT STEP 27 (2-02)** — recommended REWRITE to deployment-configurable (default=fluid for Voice Pipeline, anchored_override=death-threshold for chat/project). AWAITING USER DECISION.
- **"Reference, not display" boundary at Pass 4a.** Pass 1.4's guardrails explicitly name the discipline: 1.4 collects vocabulary as reference material; **Pass 4a decides deployment**. Output that reads as scholarly exhibition fails Layer 2 of the provotype test (philosophically literate audience, NOT classics-vocabulary-literate). *Originated at Step 23 (1.4).* **Ask at Pass 4a review:** does the prompt actually respect this boundary, or does it direct period-vocabulary-exhibition in output? If the latter, the 1.4→4a handoff is broken and the Dostoevsky card's gloss-in-parens register ("the lik — the face — of Christ") failure mode will recur.
- **1.4's guardrail-level voice-type awareness as meta-pattern.** Pass 1.4 names 4 tradition-channelled panel voices directly in Block 1 (not via worked examples). This achieves voice-type coverage more efficiently than the 1.1-02/1.2-03/1.3-02 worked-example additions. *Originated at Step 23; confirmed at Step 24* (1.5 also uses guardrail-level voice-type awareness in general_frame rule). **Consider during implementation pass:** could some worked-example fixes at 1.1/1.2/1.3 be replaced by guardrail-level voice-type callouts following 1.4/1.5's pattern? Would reduce prompt-length growth.
- **CT prompt carries Boddice-deprecated language.** `persona_coherence_threading.md:5-6` says "Preserve: ...the wound and its lesson..." — Pass 2 Block 2 explicitly DROPS "core wound + lesson" framing per Boddice §14. CT prompt is v3.10-language-stale. *Originated at Step 27 (Pass 2 review).* **Ask at CT review (post-Pass-6):** reword to "Preserve: key identity facts, the formative emotional community + apparatus + engagement (Boddice §14 3-part), the 3 most important constitutional principles, the core reasoning mode, and the dominant voice register." Boddice-align the CT threading summary.
- **Pass 2 revision-loop behavior on Pass 7a escalation.** `run_persona_pipeline.py:713-715` documents Pass 2/4a/5 as revision-loop targets when Pass 7-anachronism flags `world`-field anachronisms → Pass 2 re-runs with `_critique_suffix("2")`. Behavior of critique-suffix injection + how Pass 2 re-integrates with prior Pass 2 output (replace? merge?) forward-referenced for Wave 5. *Originated at Step 27.* **Ask at Pass 7a review:** verify revision-loop's Pass 2 rerun mechanism (full replace vs. field-patch) and whether multiple revision loops compound critique-suffixes coherently.
- **Pass 1.5 → Pass 7c handoff — `hard_limits` vs `banned_language` drift risk.** Pass 1.5 explicitly scopes HardLimits as character-level; Pass 7c produces expression-level banned_language. Independent synthesis paths — overlap + drift observed empirically on Dostoevsky (hard_limit "Never speak in the clinical-psychological register" near-mirrors banned_language "clinical-diagnostic vocabulary"). *Originated at Step 24 observation.* **Ask at Pass 7c review:** does Pass 7c's prompt actually read `hard_limits` as input and build banned_language compatibly, or synthesized independently with drift? If independent, drift is real; either cross-wire the two or accept as acceptable belt-and-braces redundancy.
- **Voice_mode disposition cross-chunk policy (1.1-1.5 mapped).** Voice_mode is: **dead/drop** at 1.1 (biographical) + 1.5 (boundaries); **load-bearing by design** at 1.3 (reasoning); **make-load-bearing** at 1.2 (commitments) + 1.4 (voice). *Originated across Steps 20-24.* **Implementation pass:** apply coherent policy in one coordinated edit across all 6 merge prompts; verify 1.6 disposition at Step 25.

### For Wave 5 (Pass 7 validation + Derive + Orchestration + Card-size)

- **Pass 1.7 coherence prompt depth.** Does the 7-check pattern have enough teeth, or does it lean on LLM charity? 1.7 edits chunk outputs itself in single LLM pass — reconciliation quality bounded by Opus 4.7's in-context reasoning across 6 chunks simultaneously. *Originated at Step 20 preamble.* **Ask at Step 26:** is the coherence discipline operationally enforceable, or are flags gestural?
- **Card-size question.** Dostoevsky assembled card is 114KB. Right allocation vs. tighter 60-80KB card with sharper selection? Runtime cost matters — Voice Pipeline Step 1 loads full card into system prompt every night. Compare to File 2's GPT-Lister study (~40KB, rated "strong fidelity"). *Originated at task description.* Surface during Wave 5 after validation-chain review.
- **`scholarly_support_score` calibration.** Pass 1.1 FormativeCandidate schema requires `Literal["strong","moderate","contested"]`. Prompt doesn't direct how to calibrate — Opus likely defaults to "strong" for well-documented candidates. If Pass 2's commit-to-one logic leans on this score, miscalibration propagates. *Originated at Step 20 self-review.* **Ask at Step 27 (Pass 2):** does Pass 2 use scholarly_support_score for selection; if yes, is 1.1's calibration guidance adequate?

### For Phase N strategy (across waves)

- **`unique_to_this_voice` flag wired to Pass 7 cross-persona QC.** 1.2's `unique_to_this_voice` flag is declared as anti-flattening mechanism with downstream enforcement. *Originated at Step 21.* **Verify at Wave 5:** does Pass 7 (specifically 7a cross-model or 7b smoke test) actually read this flag, or is it declared but not consumed?

---

## Wave 3 architecture confirmation (preamble to Steps 20-26)

Before per-prompt reviews fire, the chunked-merge architecture was confirmed against the 5 Wave-3 questions from the task description. Findings:

**Q1 — Chunked LLM calls + LLM coherence, or Jinja doing structural work?** Chunked LLM calls. Jinja handles prompt assembly only (conditional branching + schema inlining via `{{ <model>_schema }}`). No Jinja-based structural merging. User's working assumption ("Jinja + LLM coherence check") correct on the coherence half; over-weighted Jinja. Pass 1.7 is NOT a rubber-stamp — it edits chunk outputs to resolve flags AND composes the full MergedDossier in a single LLM call.

**Q2 — Full 3-source dossier per chunk, or pre-filtered slices?** Mixed by design. Perplexity: section-N per chunk (via `perplexity_split`). Claude DR: section-N per chunk in per-section mode (Phase-L-validated default) / full in monolithic fallback. **Gemini: always full, every chunk** — the only full-corpus feed in the per-section path.

**Q3 — Does merge ingest FULL corpus or is relevance-filtering silently shedding material?** Full per-chunk ingest of Gemini; sectioned on Perplexity + DR. Opus 4.7 1M context has headroom (~400KB max input). **Risk point: Gemini-full-to-every-chunk** means every chunk must self-filter Gemini's breadth-scan for §N relevance. Whether each chunk's prompt actually directs this filtering is Step 20-25 per-prompt territory (see SRI-1 below).

**Q4 — Pass 1.7 genuinely reconciling, or rubber-stamp?** Genuine. Prompt runs 7 named cross-chunk checks (formative/commitment alignment · concept usage · voice/reasoning register · anachronism/boundary · passage/work orphans · hard-limits/commitments · period-vocabulary consistency). Three resolution categories: resolve-by-edit · accept-as-productive-tension · escalate-for-human. Output carries `coherence_flags[]` + `coherence_resolutions[]` as first-class audit trail. One caveat to check at Step 26: 1.7 edits chunk outputs itself in a single LLM pass, so reconciliation quality is bounded by Opus 4.7's in-context reasoning over all 6 chunks simultaneously.

**Q5 — Merged dossier right size for Pass 2-6, or bottleneck?** Deferred to Wave 4 — we'll size Dostoevsky's `merged_dossier.json` when Pass 2 opens. Symmetric to Wave 3's "is research used well at merge" lives "is merge used well downstream."

**Architecture-level verdict:** **KEEP.** Zero architectural fixes against the chunked-merge mechanism. The design correctly realizes PB#3 (chunked merge) · PB#4 (structured JSON not markdown) · PB#5 (no per-chunk human review; Pydantic as gate) · PB#7 (meta-conventions frozen after 1.1+1.2) · PB#8 (Opus 4.7 1M context for 3-source input). Phase L bugs (1-5 in OPEN_ITEMS, committed `f1ebf6a`) were path-migration + max_tokens issues, not architectural flaws.

**Latent concerns parked:**
1. Gemini's per-chunk role is wrong-lane per File 4 → **1-arch-02** (below, HIGH, post-Phase-N revisit); empirical test via SRI-1 during Steps 20-26 per-prompt reads.
2. Pass 1.7 coherence prompt depth — does it have enough teeth? Parked for Step 26.
3. `coherence_flags[]` downstream use — does Pass 2 actually read them, or ignore? Parked for Wave 4.
4. Merged-dossier size vs. Pass 2-6 consumption — Wave 4 / 5 bleed.

---

## Wave 3 standing review items (applied to every Step 20-26 per-prompt block)

In addition to the per-step block format, Wave 3 carries two standing review criteria applied to every chunked-merge prompt (1.1-1.6 for all; 1.7 for the coherence-specific variant).

### SRI-1 — Gemini-noise-leakage watch

Per 1-arch-02, Gemini is the only full-corpus feed per chunk in current architecture. The per-chunk prompts carry an implicit relevance-filtering task. For each of Steps 20-25, assess:

- Does the prompt explicitly direct Gemini-relevance-filtering for this chunk's §N focus? Or does it hand Gemini in as an equal-weighted third source and trust the LLM to filter silently?
- Are there worked-example signatures where Gemini material has leaked into a chunk's output where it shouldn't (off-topic scholar mentions, adjacent-topic intrusions)?
- Does the prompt mention Gemini's breadth-scan role explicitly, or treat all 3 sources as interchangeable depth-sources?

Findings feed 1-arch-02's empirical test. If 3+ of 6 chunks show explicit leakage signatures or weak filter-directives, Variant A (Gemini sectioned) becomes post-Phase-N priority. If absent, Variant A remains deferred and current architecture is empirically vindicated.

### SRI-2 — Corpus utilisation depth

The Wave 3 lead question: is the merge extracting breadth from the dossier or narrowing to anchor-themes? For each chunk prompt, assess:

- Does the prompt direct the LLM to use the FULL section-N material, or does it let the LLM shortcut to a few salient passages?
- Does the prompt's guardrails language prevent Zosima-overanchoring (where a few dossier passages dominate downstream because the chunk crystallized around them)?
- Do the worked examples demonstrate breadth-across-material or depth-on-one-theme?

Findings inform whether the merge layer is the right size for Pass 2-6 to draw from (Wave 4 bleed).

---

# WAVE 3 — Phase 1 chunked merge + coherence

## Step 20 — Pass 1.1 BIOGRAPHICAL merge

**Mechanism:** LLM call · Anthropic `claude-opus-4-7` · adaptive thinking · streaming · max_tokens=32000 · temperature=1.0 · response_format_json=True · Pydantic validation · 1-retry-with-critique
**Prompt:** `personas/flows/shared/prompts/pass_1_1_merge.md` (340 lines)
**Does:** Merges Perplexity §1 + Claude DR §1 + full Gemini into Boddice §13-shaped `LifeScaffold` + 2-5 §14-shaped `FormativeCandidate[]`. Pass 2 later commits to ONE candidate.
**Verdict:** TUNE — 6 fixes, 1 MEDIUM + 5 LOW. Core architecture sound, Phase-L-validated. Not a Phase-N blocker but fixes should land before voices 2-12 if feasible.

| ID | Severity | File:lines | Change | Status |
|---|---|---|---|---|
| 1.1-01 | MEDIUM | `pass_1_1_merge.md:73-82` (Block 2 Reconciliation rule) | Add Gemini-filtering directive: name Gemini as breadth-scan tier (not equal-weighted depth); prefer Perplexity/DR for biographical-fact precedence; Gemini as cross-check only. Concrete wording: "Gemini is breadth-scan (per Pass 1b role): use for adjacency surfacing, multilingual-scholarship indexing, recent-reassessment pointers. Prefer Perplexity and Claude DR for §1 biographical depth; treat Gemini as a third-source cross-check, not an equal-weighted depth source. Where Gemini contradicts Perplexity/DR on a biographical fact, prefer the latter absent explicit scholarly citation." **Feeds 1-arch-02 empirical test — if this fix cleans up Gemini-noise across voices 2-12, Variant A (Gemini sectioned) becomes less urgent.** Mirror to Pass 1.2-1.6 merge prompts (expect same fix to propagate to Steps 21-25). | PROPOSED |
| 1.1-02 | LOW | `pass_1_1_merge.md` (new Example D, ~line 292) | Add hostile-sourced human worked example — Cleopatra: Ptolemaic divine-kingship ontological_furniture, philadelphia/timē pathē, reconstruction-from-hostile-sources handling, condition-of-being framing (divine-royal corporate body). ~40 lines. Extends worked-example coverage from 3 to 4 of 5 panel voice-type branches. Current coverage (Plato/Octopus/Whanganui) leaves hostile-sourced + fictional + musical voices to extrapolation; Cleopatra is the highest-leverage addition for current panel. | PROPOSED |
| 1.1-03 | LOW | `pass_1_1_merge.md:298` (Block 5 INPUT) | `voice_mode` rendered as LLM-visible context but no directive in Blocks 1-4 or 6 references it. Not "dead" — functions as silent context (LLM can use as implicit metadata) — but intent is ambiguous. Resolve either direction: (a) drop from Block 5 (cleaner template; chunks 1.3-1.4 need voice_mode, this chunk structurally doesn't), OR (b) add one-line Block 2 guidance naming voice_mode's role explicitly (e.g. "for `narratival` voices, prefer passages-as-incarnations in §14 framing; for `observational`, favor practice-driven formative candidates"). Recommend (a) for consistency with the 4-block-prompt's explicit-guidance style; (b) acceptable if silent-context is the intent. | PROPOSED |
| 1.1-04 | LOW | `pass_1_1_merge.md:49-52` (Block 2 Period-vocabulary rule) | Reword the binary pre-1820 cutoff to gradate. The 6 voice-type exemplar lists at lines 52-68 already include Arendt (1906-1975) and Marley (1945-1981) — post-1820 — both correctly carrying tradition-specific native lexicons. Reword: "For any voice with a tradition-specific lexicon (Russian Orthodox, Rastafari, Arendtian German-Jewish, Confucian civic-tech, etc.), prefer the voice's own terms over generic English emotion-vocabulary — regardless of period. For pre-1820 voices especially, do NOT use 'emotion' as organizing category." More permissive floor, same discipline on the common failure mode. | PROPOSED |
| 1.1-05 | LOW | `pass_1_1_merge.md:77` (Block 2 Reconciliation rule) | **Prompt-schema mismatch.** Prompt says "surface contested scholarly interpretations as `ContestedReading`" but `ContestedReading` (defined in `schemas/_conventions.py:55`) is NOT imported into `schemas/pass_1_1.py` — LifeScaffold has no field typed `ContestedReading` or `list[ContestedReading]`. The LLM cannot emit this type in 1.1 output. Three resolutions: (a) add `contested_readings: list[ContestedReading]` field to LifeScaffold (semantically awkward — biographical contested readings are thin); (b) reword to match existing mechanism: "flag contested scholarly readings inline with both interpretations cited via `evidence_tag: inference`, per the reconciliation convention"; (c) verify this is a cross-chunk forward-reference and accept as documentation-only — `ContestedReading` belongs more naturally in Pass 1.2 `commitments[]` / `tensions[]`. Recommend (b) — reword, drop the phantom type reference from this chunk's prompt. | PROPOSED |
| 1.1-06 | LOW | `pass_1_1_merge.md:120-124` (Block 3 STRICT RULES) | **Null-discipline rule silent on fictional voices.** Current rule covers human (populate `lived_through_own_apparatus`) and non-human/cosmic (populate `condition_of_being`). Schema enum `type: Literal["human", "non_human", "fictional"]` includes fictional; Scheherazade is the only fictional voice in the Athens panel. Opus must extrapolate without guidance. Add explicit rule: "For fictional voices, populate `condition_of_being` (the narratorial / frame-tale condition — e.g. Scheherazade speaking under threat of execution within 1001 Nights, with `evidence_tag: experiential_reconstruction` per §14 attributed-by-narrative-function discipline); leave `lived_through_own_apparatus` null. The voice's 'lived apparatus' is attributed by narrative function, not direct biographical event-plus-framework." Cross-reference 1.1-02 (Scheherazade worked example would demonstrate this). | PROPOSED |

**Review — model + config:** KEEP. Opus 4.7 + adaptive thinking + 32K max_tokens correctly calibrated. Cross-source biographical reconciliation + Boddice §13/§14 rubric + 5-tag evidence discipline is judgment-heavy; Sonnet would regress on tag discipline (Phase L showed gaps on Opus itself). No config changes.

**Review — prompt (strengths):** 4-block-prompt + 3 voice-type worked examples is the right shape per File 2/3. PB#7 meta-convention establishment is here (5-tag vocabulary gets frozen after chunk 1.2). Period-vocabulary primary rule with 6 voice-type exemplar lists is operationally sharp. Formative-candidates non-commit rule (2-5; Pass 2 commits) separates "what's supported" from "what we're choosing" cleanly. "Never invent" anti-hallucination rule is right. Human vs. non-human null-discipline on `lived_through_own_apparatus` vs `condition_of_being` is explicit and Pydantic-enforced. Empirically Phase-L-validated on Dostoevsky — 11 pathē terms, 8 anachronisms, 6 formative candidates output.

**Review — research utilisation (SRI-1 + SRI-2):**
- **SRI-1:** No Gemini-filtering directive in prompt. All 3 sources framed as equal-weighted depth in Block 2 Reconciliation rule + Block 5 INPUT. Gemini's breadth-scan role (per File 4) not named. Primary driver of fix 1.1-01. Feeds 1-arch-02 empirical vindication.
- **SRI-2:** Task step 1 directs cross-source reading; 2-5 formative candidate range is right (Dostoevsky had 6 major candidates in dossier, 5-max was acceptable constraint). Worked examples demonstrate breadth within §13 (multiple pathē + anachronisms + furniture per voice). Zosima-overanchoring risk lives at Pass 2 (commits-to-one), not 1.1 — parked for Wave 4.

*Observations (not fixes):*
- **Empirically validated.** Dostoevsky Phase L output was strong on breadth.
- **Phase-N blocker?** No. Fixes are quality improvements, not blockers. Current architecture produces Phase-N-acceptable output.
- Cross-reference 1.1-01 forward: expect SRI-1 pattern to repeat in Steps 21-25; propose mirror fix at each if prompt doesn't already surface Gemini-filtering.

---

## Step 21 — Pass 1.2 INTELLECTUAL merge

**Mechanism:** LLM call · Anthropic `claude-opus-4-7` · adaptive thinking · streaming · max_tokens=32000 · temperature=1.0 · response_format_json=True · Pydantic validation · 1-retry-with-critique
**Prompt:** `personas/flows/shared/prompts/pass_1_2_merge.md` (253 lines)
**Does:** Merges Perplexity §2 + Claude DR §2 + full Gemini into `Commitment[]` (10-20 with operational_note + `unique_to_this_voice` flag) + `Concept[]` (5-10 with mandatory `what_it_rules_out`) + `Tension[]` (2-6, unflattened). Chunk 1.2 is the PB#7 convention-lock point — conventions FROZEN after this lands.
**Verdict:** TUNE — 3 fixes, 1 MEDIUM + 2 LOW. **Best-engineered merge prompt in the family** (specificity-rule two-voice swap test + mandatory `what_it_rules_out` + tensions-not-resolved + `unique_to_this_voice` anti-flattening flag + Phase-L-validated 17-commitment Dostoevsky output). Not a Phase-N blocker.

| ID | Severity | File:lines | Change | Status |
|---|---|---|---|---|
| 1.2-01 | MEDIUM | `pass_1_2_merge.md:74-82` (Block 2 cross-source guidance) | Add Gemini-filtering directive with 1.2-specific right-lane framing: "Gemini is breadth-scan — lean into it for cross-disciplinary scholarship indexing, non-Anglophone tradition surfacing, and lineage connections between this voice's commitments and adjacent thinkers. Prefer Perplexity and Claude DR for commitment-extraction depth (primary-text anchored); treat Gemini as adjacency scanner, not equal-weighted source." Unlike 1.1, Gemini has genuine right-lane value for 1.2 — the fix unlocks that value while preventing noise. Mirror of 1.1-01 with stronger positive framing. Feeds 1-arch-02 empirical test. | PROPOSED |
| 1.2-02 | LOW | `pass_1_2_merge.md:219` (Block 5 INPUT) + new line ~90 (Block 2) | Make `voice_mode` load-bearing in this chunk (unlike 1.1 where it's structurally irrelevant). Add Block 2 guidance: "For `narratival` voices (Dostoevsky, Scheherazade), commitments are often enacted-in-story rather than declared; operational_note should name the scene/passage where the commitment becomes visible. For `philosophical` voices, commitments are stated; operational_note extends them to novel applications. For `observational` voices, commitments are inferred from practice; tag as `experiential` or `inference`, not `stated`." | PROPOSED |
| 1.2-03 | LOW | `pass_1_2_merge.md` (new Example D after line 216) | Add fictional voice worked example (Scheherazade) showing `[attributed_by_narrative_function]` tag on a Commitment. Block 1 names fictional voices explicitly; Block 4 doesn't demonstrate. Concrete shape: commitment "narrative as stay of execution" with operational_note "every proposition answered by a tale that defers judgment; abstract arguments treated as the Shah's power-to-command rather than claims to be refuted." ~30 lines. Hostile-sourced (Cleopatra) + musical (Marley) extensions are lower priority — fictional is the prompt's named-but-undemonstrated case. | PROPOSED |

**Review — model + config:** KEEP. Opus 4.7 + adaptive thinking + 32K max_tokens is correctly fit. 10-20 specificity-tested commitments + 5-10 exclusion-bearing concepts + 2-6 unflattened tensions demands judgment-heavy cross-source synthesis; Sonnet would under-specify or fabricate operational notes. Dostoevsky empirical output ~18K tokens, well under 32K ceiling.

**Review — prompt (strengths):** Best-engineered merge prompt.
- **Specificity rule with two-voice swap test** at line 46-49 operationalizes File 3's "fine-grained constitutional principles" prescription. LLM self-applies the test during synthesis.
- **`what_it_rules_out` mandatory + 3 worked exclusion examples** (episteme / ibtilā' / mauri) directly addresses File 3 Failure 3 (generic philosophical positions).
- **Tensions-not-resolved discipline** with 4 cross-voice concrete cues (Plato Republic-vs-Laws, Arendt on Heidegger, Marley on violence, Ibn Battuta on non-Maliki women). File 3 Failure 5 addressed at prompt-discipline level.
- **`unique_to_this_voice` flag** wired to downstream Pass 7 cross-persona QC — anti-flattening has enforcement loop.
- **PB#7 freeze explicit** in prompt comment — Opus sees chunk 1.2 as convention-locking.
- **"Never invent" with specific anti-hallucination discipline** (no citation-free quotes, no implied attributions, no "Plato said" without work + passage).
- **Phase-L-validated.** Dostoevsky's 17-commitment constitution visibly respected specificity rule (each principle operationally specific, textually anchored).

**Review — research utilisation (SRI-1 + SRI-2):**
- **SRI-1:** No Gemini-filtering directive; all 3 sources framed equal-weighted. 1.2-01 resolves. Gemini has genuine right-lane value for commitment-extraction (cross-disciplinary adjacency) — naming the lane unlocks that value.
- **SRI-2:** Specificity rule IS the breadth-protecting mechanism at 1.2. Forces 10-20 operationally-distinct commitments, not collapse to famous positions. **Breadth well-defended at 1.2 layer.** Zosima-overanchoring risk shifts to Pass 2 (commits-to-fewer-fields) — Wave 4 concern, not 1.2's.

*Observations (not fixes):*
- **1.2 is best-engineered chunk of family.** 1.1's fixes (1.1-02, -04, -05, -06) mostly don't repeat — 1.2's prompt architecture is tighter, more explicit, fewer gaps.
- **Expect 1.2-01 Gemini-filtering pattern to mirror across 1.3, 1.4, 1.5, 1.6.** If confirmed at each, a single coordinated 6-file prompt-patch lands the Gemini-lane fix simultaneously.
- **`ContestedReading` not referenced in 1.2 prompt** — 1.1-05 prompt-schema mismatch doesn't repeat. 1.2's contested-readings mechanism is `Tension[]` with `conflicting_commitments: list[str]` + `passage_citations` — real schema, real field, cleanly serializable.

---

## Step 22 — Pass 1.3 REASONING merge

**Mechanism:** LLM call · Anthropic `claude-opus-4-7` · adaptive thinking · streaming · max_tokens=32000 · temperature=1.0 · response_format_json=True · Pydantic validation · 1-retry-with-critique
**Prompt:** `personas/flows/shared/prompts/pass_1_3_merge.md` (167 lines)
**Does:** Merges Perplexity §3 + Claude DR §3 + full Gemini into `ReasoningMethod` (5-8 voice-mode-branched steps with name+description+example) + `Textures` (`finds_compelling[]` + `resists[]` as **textures of argument not topics**, 4-8 each). File 3's "the layer most implementations miss."
**Verdict:** TUNE — 3 fixes, 1 MEDIUM + 2 LOW. **voice_mode is load-bearing here** (5-way branch) — contrast with 1.1 (dead context) and 1.2 (silent context). Specificity self-test + texture-vs-topic discrimination both sharp. Narratival worked example is the most impactful missing piece for Phase N.

| ID | Severity | File:lines | Change | Status |
|---|---|---|---|---|
| 1.3-01 | MEDIUM | `pass_1_3_merge.md:22-33` (Block 2) | Add Gemini-filtering directive with reasoning-method-specific right-lane framing: "Gemini is breadth-scan — use for cross-disciplinary parallels to the voice's reasoning method (Arendt's judgment has Kantian lineage; Dostoevsky's scenic-collision shares shape with Kierkegaard's dialectic-of-existence). Prefer Perplexity and Claude DR for reasoning-method depth (primary-text grounded). Treat Gemini as adjacency scanner." Mirror of 1.1-01/1.2-01. Feeds 1-arch-02 empirical test. | PROPOSED |
| 1.3-02 | LOW | `pass_1_3_merge.md` (new Example C after line 140) | Add narratival worked example — Dostoevsky, showing 6-8 steps of "reason by incarnation and scenic collision." Lift-from-Phase-L-card: incarnate-idea-in-person → stage-at-porog → follow-logic-to-body → surface-zhivaya-zhizn' → offer-image-not-argument → split-across-doubles → hold-vdrug-open → open-toward-resurrection. Textures drawn from assembled Dostoevsky card. ~45 lines. **Highest-leverage addition — narratival is the most-extrapolation-dependent of 5 branches** named in Block 1 (Scheherazade, Marley voices will need it). | PROPOSED |
| 1.3-03 | LOW | `pass_1_3_merge.md:30` | Period-vocabulary gradation ripple — same fix as 1.1-04. **Land as coordinated single-patch across 1.1 + 1.2 + 1.3 + (verify) 1.4/1.5** — uniform wording in all merge prompts. | PROPOSED |

**Review — model + config:** KEEP. Reasoning-method extraction is File 3's "most implementations miss this" layer — judgment-heavy synthesis of *how* voice moves through problem. Sonnet would generic-dialectic the philosophical voices and miss perceptual-response / narratival shapes. Opus earns its keep. Output ~3-6K tokens well within 32K ceiling; cost ~$0.80-1.20/voice proportional.

**Review — prompt (strengths):**
- **voice_mode load-bearing** — Block 1 branches 5 ways (philosophical / observational / organism / system / narratival). This chunk is where voice_mode does real work.
- **Specificity self-test** (line 25-26): "if two different provocations run through this method, do the results sound like THIS voice engaging differently, or like a generic responder?" Analogous to 1.2's two-voice swap test.
- **Texture-vs-topic discrimination** (line 27-29) operationally sharp. Prevents the common failure mode where `finds_compelling` lists subjects-the-voice-cares-about instead of argument-shapes-the-voice-responds-to.
- **Plato worked example textures are exemplary** — "arguments from principle rather than from data", "procedural solutions that avoid the question of what the procedure is FOR" — textures with voice-specific resonance, not topics.
- **Octopus worked example correctly recasts** reasoning as perceptual-response cycle, ban on "thinks/believes" vocabulary — right anti-anthropomorphization move.
- **Short prompt (167 lines)** — doesn't over-explain; branching + self-test + discrimination + worked examples do the work economically.

**Review — research utilisation (SRI-1 + SRI-2):**
- **SRI-1:** No explicit Gemini-filtering directive. 1.3-01 resolves. Gemini's right-lane for reasoning-method is thinner than for 1.2 but not nil (cross-disciplinary parallels on method shape).
- **SRI-2:** Specificity self-test is the breadth-protecting mechanism. Forces generalizing method, not 3-step summary of one famous argument. 5-8 step range prevents thinning and padding. Worked examples demonstrate breadth-within-method (Plato's 7 steps = full dialectical cycle, not just "ask questions"). **Zosima-overanchoring well-defended at 1.3.**

*Observations (not fixes):*
- **voice_mode load-bearing at 1.3** validates 1.2-02 direction and reinforces 1.1-03 (drop from 1.1 where irrelevant). Pattern clarifies: voice_mode matters at reasoning (1.3), commitments (1.2), likely voice (1.4) — but not biographical foundation (1.1).
- **1.3-02 Dostoevsky narratival example is lift-from-Phase-L-card** — `reasoning_method.steps` in assembled Dostoevsky card IS the right shape. Implementation is template-selection, not drafting.
- **Expect 1.4 (VOICE) to again branch on voice_mode.**
- **1.3-03 coordinated patch across 1.1 + 1.2 + 1.3** lands period-vocabulary gradation in one edit cycle.

---

## Step 23 — Pass 1.4 VOICE merge

**Mechanism:** LLM call · Anthropic `claude-opus-4-7` · adaptive thinking · streaming · max_tokens=32000 · temperature=1.0 · response_format_json=True · Pydantic validation · 1-retry-with-critique
**Prompt:** `personas/flows/shared/prompts/pass_1_4_merge.md` (150 lines)
**Does:** Merges Perplexity §4 + Claude DR §4 + full Gemini into `Moves` (3-6 signature patterns) + `Register` (rhetorical_mode + register_and_tone + `tradition_note` for oral/ritual/performative voices per Boddice §15) + `Vocabulary` (15-30 preferred_vocabulary + 3-8 metaphorical_repertoire families).
**Verdict:** TUNE — 4 fixes, 1 MEDIUM + 3 LOW. **Several design improvements over 1.1/1.2/1.3:** guardrail-level voice-type awareness (names 4 tradition-channelled panel voices); Boddice §13 pathē carryover wired at prompt level; negative-boundary register_and_tone rule; "reference, not display" discipline naming Pass 4a handoff; period-vocabulary rule already gradated. Not a Phase-N blocker.

| ID | Severity | File:lines | Change | Status |
|---|---|---|---|---|
| 1.4-01 | MEDIUM | `pass_1_4_merge.md:23-39` (Block 2) | Add Gemini-filtering directive with 1.4-specific right-lane framing: "Gemini is breadth-scan — lean into it for multilingual-scholarship on voice-signature (Russian scholarship on Dostoevsky's scenic form, Sanskrit-adjacent analysis of Rastafari Iyaric origins, German Kantian-tradition lineage for Arendt's register), stylistic-reception history in non-Anglophone traditions, and translator-tradition criticism for fictional voices. Prefer Perplexity and Claude DR for primary-text stylistic depth. Treat Gemini as adjacency scanner." Mirror of 1.1-01/1.2-01/1.3-01. Feeds 1-arch-02 empirical test. | PROPOSED |
| 1.4-02 | LOW | `pass_1_4_merge.md:99-121` (Block 4 Marley example) | **Complete the Marley worked example** — currently shows register + vocabulary but omits `moves` entirely. Add 3-5 moves demonstrating tradition-channelled pattern: refrain-as-prophetic-injunctive / witness-narrative-verse / Garveyite-compression / reasoning-as-communal-speech-act / imperative-second-person-interleaved-with-first-person-communal. ~15 lines. Closes the 2-of-3-output-keys gap. | PROPOSED |
| 1.4-03 | LOW | `pass_1_4_merge.md` (new Example C after line 121) | Add non-human organism worked example — Octopus. Moves = [full-body-registration / arm-probe / chromatic-display / environmental-assessment / decisive-movement-or-stillness]; register = ["non-propositional; displays rather than argues; alien but not hostile"; tradition_note: null]; vocabulary = [tactile-visual-spatial lexicon 15-25 terms]. ~30 lines. **Highest-leverage missing example — non-human voice-signature is the hardest extrapolation from Plato + Marley.** | PROPOSED |
| 1.4-04 | LOW | `pass_1_4_merge.md:~28` (Block 2 new line) | Make voice_mode load-bearing at 1.4: "Voice_mode as prior: for `narratival` voices, rhetorical_mode defaults to scenic-confessional; for `philosophical`, declarative-dialectical; for `observational`, descriptive-witnessing. The voice_mode is a prior; the corpus evidence is final — naming the prior prevents generic-register drift." Parallel to 1.3's voice_mode-load-bearing pattern. | PROPOSED |

**Review — model + config:** KEEP. Output ~3-5K tokens; cost ~$0.80-1.20/voice. 32K headroom large.

**Review — prompt (strengths):**
- **Voice-type awareness in guardrails directly** (Block 1 names Scheherazade, Marley, Whanganui-via-Te-Pou-Tupua, Cleopatra-Isis-register as tradition-channelled). This achieves what 1.1-02/1.2-03/1.3-02 worked-example fixes target — **pattern worth lifting back** to 1.1/1.2/1.3.
- **Boddice §13 pathē carryover** — explicit cross-chunk coherence wiring at prompt level.
- **Negative-boundary rule** on register_and_tone — "what IS and what is NOT." Prevents default to academic register.
- **"Reference, not display" discipline** (lines 36-41) names Athens-audience constraint; draws clean 1.4 → Pass 4a handoff. **Sophisticated prompt-level systems thinking.**
- **Period-vocabulary rule already gradated** — "Pre-1820 voices: period language primary. Modern voices: tradition-specific terms." 1.1-04 ripple doesn't need to propagate here.

**Review — research utilisation (SRI-1 + SRI-2):**
- **SRI-1:** No Gemini-filtering directive. Pattern consistent. 1.4-01 resolves.
- **SRI-2:** "Reference, not display" IS the anti-Zosima-overanchoring mechanism for 1.4. Forces 15-30 vocabulary (not 5 most-used words), 3-8 metaphorical families (not one famous metaphor). **Breadth well-defended at 1.4.** Compression risk shifts to Pass 4a — parked for Wave 4.

*Observations (not fixes):*
- **1.4's guardrail-level voice-type awareness is a meta-pattern worth lifting back to 1.1/1.2/1.3** during coordinated implementation — more efficient than worked-example additions.
- **"Reference, not display" boundary** is Pass 4a deployment-discipline naming. Forward-referenced for Wave 4.
- **Period-vocabulary already gradated at 1.4** — 1.3-03 coordinated patch targets 1.1 + 1.2 + 1.3 only, not 1.4.

---

## Step 24 — Pass 1.5 BOUNDARIES merge

**Mechanism:** LLM call · Anthropic `claude-opus-4-7` · adaptive thinking · streaming · max_tokens=32000 · temperature=1.0 · response_format_json=True · Pydantic validation · 1-retry-with-critique
**Prompt:** `personas/flows/shared/prompts/pass_1_5_merge.md` (174 lines)
**Does:** Merges Perplexity §5 + Claude DR §5 + full Gemini into `KnowledgeBoundary` (general_frame + temporal/geographic/conceptual exclusions) + `SensitiveTopics` (3-6 topics with substantive what_the_voice_actually_thought + navigation_guidance) + `HardLimits` (3-5 catastrophic character-level prohibitions, expression-level deferred to Pass 7c). **Directly addresses File 3 Failure 4 (sanitisation paradox) at prompt-discipline level.**
**Verdict:** TUNE — 4 fixes, 1 MEDIUM + 3 LOW. **Sanitisation-paradox naming + expression-vs-character-level boundary + voice-type-aware general_frame rule** are best-of-class design elements. Gap: hostile-sourced + fictional voice-type coverage. 1.5-02 Cleopatra example high-value before Cleopatra Phase N build.

| ID | Severity | File:lines | Change | Status |
|---|---|---|---|---|
| 1.5-01 | MEDIUM | `pass_1_5_merge.md:19-35` (Block 2) | Add Gemini-filtering directive with 1.5-specific right-lane framing: "Gemini is breadth-scan — lean into it for scholarly debates about the voice's contested territory (orientalist-reception debates on Scheherazade, Roman-propaganda-vs-scholarly-reconstruction on Cleopatra, competing interpretations of Dostoevsky's Jewish-question writing), comparative boundary-cases across traditions. Prefer Perplexity and Claude DR for primary-text depth and explicit voice-thought-on-topic. Treat Gemini as adjacency scanner for scholarly debate surrounding the topic." Mirror of 1.1-01/1.2-01/1.3-01/1.4-01. Feeds 1-arch-02 empirical test. | PROPOSED |
| 1.5-02 | LOW | `pass_1_5_merge.md` (new Example C after line 145) | Add hostile-sourced human worked example — Cleopatra. Demonstrates **reconstruction-against-hostile-sources navigation pattern** (different from Plato's stated-in-primary-text pattern). 3 sensitive_topics: (1) Hostile Roman characterizations with lead-with-scholarly-reconstruction navigation; (2) Ptolemaic divine kingship vs modern secular leadership; (3) Mixed Egyptian/Greek identity in colonial-reception discourse. ~40 lines. **High-stakes extrapolation — Cleopatra Phase N build depends on this navigation pattern.** | PROPOSED |
| 1.5-03 | LOW | `pass_1_5_merge.md:21-23` (Block 2 general_frame rule) | Close fictional-voice gap in general_frame rule. Currently covers pre-modern / non-human organism / non-human system; omits fictional. Add: "For fictional voices, a narrative-internal + translation-tradition boundary — the voice knows what the text includes; conceptual exclusions follow narrative coherence. Sensitive_topics may include translation-tradition-reception controversies (Burton's orientalist register vs. Haddawy's vs. Lyons's — the character's voice is tradition-shaped)." Cross-reference 1.1-06 parallel fictional null-discipline fix. | PROPOSED |
| 1.5-04 | LOW | `pass_1_5_merge.md:148` (Block 5 INPUT) | Drop `voice_mode` — structurally irrelevant at 1.5 (boundaries = type+period+subtype; voice_mode's weak purchase at sensitive_topics is redundantly covered by voice_mode's effect on reasoning-method and register at 1.3/1.4). Follows 1.1-03 drop-where-irrelevant pattern. | PROPOSED |

**Review — model + config:** KEEP. Sensitive-topic navigation_guidance is File 3 Failure 4 territory where generic-AI fails catastrophically (Khanmigo). Sonnet would default to safer-but-flatter guidance; Opus earns its keep. Output small; cost ~$0.80-1.20/voice.

**Review — prompt (strengths):**
- **Sanitisation paradox named directly in Block 1** with File 3 Failure 4 cited and navigation_guidance designated as the load-bearing field. **Best-of-prompt meta-design across the chunk family** — Khanmigo failure mode prevented at prompt-discipline level.
- **Voice-type-aware general_frame rule** at guardrail level (pre-modern/organism/system branched). 1.4-originated meta-pattern confirmed here.
- **Expression vs. character-level boundary explicit** — HardLimits = catastrophic character only; banned_language deferred to Pass 7c. Clean downstream handoff.
- **Conceptual exclusions tagged with REASON** — downstream Pass 2's translation_protocol benefits.
- **Phase-L-validated.** Dostoevsky's 6-topic topics_requiring_care (Jewish question / imperial mission / anti-Catholicism / women + sexual violence / theology of suffering / faith-and-doubt) is among the richest content on the assembled card — sanitisation-paradox discipline working empirically.

**Review — research utilisation (SRI-1 + SRI-2):**
- **SRI-1:** No Gemini-filtering directive. Gemini's right-lane for 1.5 is thinner than 1.2/1.4 but real — scholarly-debate-about-contested-territory surfaces well. 1.5-01 resolves.
- **SRI-2:** Navigation_guidance discipline IS the anti-flattening mechanism. Forces substantive what-voice-thought + specific-how-to-engage, not safe-avoidance. 3-6 topics range prevents both under-coverage and over-coverage. **Breadth well-defended at 1.5.** No Zosima-overanchoring risk at boundary layer (exclusionary by design).

*Observations (not fixes):*
- **Voice_mode disposition pattern now clarified across 1.1-1.5:** dead/drop at 1.1 + 1.5 (biographical + boundaries); load-bearing by design at 1.3 (reasoning); make-load-bearing at 1.2 (commitments) + 1.4 (voice). One coherent policy, different per-chunk applications — log as cross-chunk coordination insight for implementation pass.
- **Guardrail-level voice-type awareness** (1.4 meta-pattern) appears here too — Block 2's general_frame rule branches on type. 1.5-03 extends to fictional. **Confirms 1.4-originated pattern is a general design principle across the chunk family**, not 1.4-unique.
- **Pass 1.5 → Pass 7c handoff explicit** — expression-level constraints deferred to Pass 7c. Forward-referenced for Wave 5.

---

## Step 25 — Pass 1.6 CORPUS merge

**Mechanism:** LLM call · Anthropic `claude-opus-4-7` · adaptive thinking · streaming · max_tokens=32000 · temperature=1.0 · response_format_json=True · Pydantic validation · 1-retry-with-critique
**Prompt:** `personas/flows/shared/prompts/pass_1_6_merge.md` (191 lines)
**Does:** Merges Perplexity §6 + Claude DR §6 + full Gemini into `Works[]` (5-20+) + `Passages[]` (8-15 with purpose trichotomy) + `URLs[]` (Pass 1c fetch targets) + `ReferenceOnlyPassages` (optional two-tier for musical voices). **Most structurally-complex merge prompt** — 4 output keys, 5 corpus-variant branches.
**Verdict:** TUNE — 6 fixes, 1 MEDIUM + 5 LOW (1.6-05 merged into 1.6-03). Two-tier musical corpus runtime contract is **best-of-class systems-engineering**; most voice-type branches mean most worked-example gaps. Not a Phase-N blocker but 1.6-02/1.6-03/1.6-04 all high-value before their respective voice builds. **MAJOR cross-reference: 1-arch-01 directly restructures this chunk if adopted post-Phase-N.**

| ID | Severity | File:lines | Change | Status |
|---|---|---|---|---|
| 1.6-01 | MEDIUM | `pass_1_6_merge.md:44-57` (Block 2) | Add Gemini-filtering directive with **strongest positive framing in the family** — for corpus work, Gemini is actively preferred over Perplexity/DR for URL surfacing + translator-tradition breadth (multilingual archives, non-Anglophone translations, recent-digitization 2020-2026). Concrete wording: "Gemini is breadth-scan — for corpus work, lean into it hard: multilingual primary-text URLs (Cyrillic archives for Russian, Arabic for Islamic, Sanskrit for Buddhist), non-Anglophone translator traditions, comparative translation-reception scholarship, unusual canonical-passage surfacing, recent-digitization announcements. Prefer Perplexity and Claude DR for canonical-text depth + scholarly interpretation; treat Gemini as primary source for URL surfacing + translator-tradition breadth." Feeds 1-arch-02 empirical test with highest-positive-value-framing of the 6 Gemini-filtering fixes. | PROPOSED |
| 1.6-02 | LOW | `pass_1_6_merge.md` (new Example C after line 162) | Add non-human organism worked example — Octopus. Works: Godfrey-Smith 2016 + Hanlon/Messenger + Mather + Amodio (all tier_2_scholarly, scientific_literature). 3-4 passages on distributed cognition / chromatic display with purpose=intellectual_substance. URLs: JSTOR + Current Biology open-access. ~25 lines. Closes non-human-organism branch gap. | PROPOSED |
| 1.6-03 | LOW | `pass_1_6_merge.md` (new Example D after 1.6-02) | Add fictional worked example — Scheherazade. Demonstrates **multiple-translator-tradition corpus shape** unique to fictional voices. Works: Galland 1704 + Burton 1885 + Haddawy 1990 + Lyons 2008. Passages include at least one with `purpose=translation_anchor` (register-shift across translators). URLs: Gutenberg Burton + publisher pages. ~30 lines. **Also resolves 1.6-05** — translation_anchor purpose tag demonstrated. | PROPOSED |
| 1.6-04 | LOW | `pass_1_6_merge.md:129-160` (Block 4 Marley example) | Extend Marley example with `reference_only_passages` private-tier demonstration. Currently shows PUBLIC tier only; PRIVATE tier structure is the unique corpus_constraint=lyrics_patterns_only feature, undemonstrated. Add 2-3 schematic reference_only_passages entries: one direct-lyric-quotation stub + copyright attribution + runtime_contract_note. ~15 lines. | PROPOSED |
| 1.6-05 | LOW | (merged into 1.6-03) | `translation_anchor` purpose_tag defined line 51 but never demonstrated in Block 4. Resolved by 1.6-03 Scheherazade example. **Merged — no separate fix.** | RESOLVED-VIA-1.6-03 |
| 1.6-06 | LOW | `pass_1_6_merge.md:166` (Block 5 INPUT) | Drop `voice_mode` — structurally irrelevant at 1.6. Bibliographic shape = corpus_constraint + type + subtype + hostile_sources; voice_mode doesn't affect works/passages/urls extraction. Follows 1.1-03 / 1.5-04 pattern. **Completes voice_mode cross-chunk policy:** dropped at 1.1 + 1.5 + 1.6; load-bearing at 1.3; make-load-bearing at 1.2 + 1.4. | PROPOSED |

**Review — model + config:** KEEP. Bibliographic synthesis + 5-branch discrimination + two-tier musical contract + URL-fabrication discipline requires judgment-heavy Opus-level work. Sonnet would plausibly catalogue but miss two-tier handling and hostile-source bias-flag. Output ~6-12K (larger than 1.3/1.4/1.5; passages carry verbatim text) — 32K headroom fine. Cost ~$1.20-1.80/voice.

**Review — prompt (strengths):**
- **Two-tier musical corpus with runtime contract** (public pattern-descriptions + private direct-quotation loaded into Step 1 only, runtime drops before Step 2, cross-repo contract to HANDOFF.md). **Architecturally sophisticated** — resolves copyright/voice-fidelity tradeoff cleanly at prompt-discipline level.
- **5 corpus-variant branches named in guardrails** (Block 1 lines 15-42). Same 1.4/1.5 guardrail-level voice-type awareness pattern — no reliance on extrapolation for branch identification.
- **Anti-URL-fabrication discipline explicit** — "Never fabricate URLs. If uncertain, omit." Phase L Dostoevsky 18/22 fetch success confirms working empirically.
- **Purpose-tag trichotomy** (intellectual_substance / voice_exemplar / translation_anchor) gives passages clear downstream function.
- **Tier system properly applied** (tier_1_primary / tier_2_scholarly / tier_3_contested) — `_conventions.py` single-source-of-truth.
- **`reference_only_passages` default** prevents optional-field confusion.
- **Phase-L-validated.** Dostoevsky output + 18/22 URL fetch success = working as designed under real pressure.

**Review — research utilisation (SRI-1 + SRI-2):**
- **SRI-1:** No Gemini-filtering directive. **1.6's Gemini right-lane is the richest in the chunk family** — multilingual URLs + translator-tradition scholarship + recent digitization. 1.6-01 resolves with largest positive-value framing (Gemini actively preferred for URL surfacing).
- **SRI-2:** "Complete-as-possible catalogue" directive + 5-20 works + 8-15 passages + 3-purpose-tag discrimination is the breadth-protecting mechanism at 1.6. Forces comprehensive bibliography, not "3 most famous works." **Breadth well-defended at 1.6.** Compression risk shifts to Pass 6 curation (5-10 curated_corpus_passages) — Wave 4 concern.

*Observations (not fixes):*
- **1-arch-01 directly affects this chunk.** Current 6 fixes apply to current-architecture prompt; become partial-rewrite scope under 1-arch-01. **Cost-benefit:** land current fixes for voices 2-12; decide 1-arch-01 post-Phase-N based on card-quality calibration.
- **SRI-1 Gemini-filtering 6/6** at Pass 1.1-1.6. Coordinated cross-chunk patch is the efficient implementation path.
- **Voice_mode cross-chunk policy complete.** Dropped at 1.1 + 1.5 + 1.6; load-bearing at 1.3; make-load-bearing at 1.2 + 1.4. Land in one coordinated 6-file edit.
- **Two-tier runtime contract forward-referenced to Voice Pipeline Step 1/2 assembly** (separate workstream per REBUILD_PLAN) — verify enforcement when that work starts.

---

## Step 26 — Pass 1.7 COHERENCE

**Mechanism:** LLM call · Anthropic `claude-opus-4-7` · adaptive thinking · streaming · **max_tokens=64000** (bumped from 40K per Bug 5) · temperature=1.0 · response_format_json=True · Pydantic MergedDossier validation · 1-retry-with-critique · `by_alias=True` on model_dump. **NOT shared chunk_runner harness** — runs own orchestrator (`run_pass_1_7.py`).
**Prompt:** `personas/flows/shared/prompts/pass_1_7_coherence.md` (183 lines)
**Does:** Reads all 6 chunk outputs (1.1-1.6), runs 7 named cross-chunk consistency checks, **edits chunk outputs to resolve flags** (not rubber-stamp), emits final composed `MergedDossier` with `coherence_flags[]` + `coherence_resolutions[]`. Single input to Pass 2-6 synthesis.
**Verdict:** TUNE — 4 fixes, all LOW. **Genuinely not rubber-stamp** — 7 operational checks + 3-category resolution policy + real chunk-output edits + Phase-L-validated. Fixes are prompt-discipline refinements, not structural defects. **Wave 3 architecture-level verdict on coherence pass: working as designed.**

| ID | Severity | File:lines | Change | Status |
|---|---|---|---|---|
| 1.7-01 | LOW | `pass_1_7_coherence.md` (new Block 4 after line 72) | Add 3 worked examples — pattern-break repair (1.1-1.6 all have Block 4 WORKED EXAMPLES; 1.7 skips). Examples: (a) **resolve-by-edit** — concept-undefined flag, chunk 1.2 gets new Concept appended; (b) **accept-productive-tension** — Plato Republic-vs-Laws with scholarly-consensus justification + criteria-satisfaction check; (c) **escalate** — META-frozen convention question (rare per PB#7). ~40 lines. **Highest-leverage fix for 1.7.** Reduces extrapolation burden on Opus for trickiest prompt-discipline decision. | PROPOSED |
| 1.7-02 | LOW | `pass_1_7_coherence.md:63-65` (Block 3 resolve-by-edit) | Add edit-scope discipline: "Edit scope: prefer minimal edits — append clarifying phrases, add missing terms to lists, tighten operational_notes. Do NOT rewrite entire commitments, reshape reasoning steps, or synthesize new content. If reconciliation requires more than minor edits, escalate instead." Keeps coherence pass focused on reconciliation, not re-synthesis. | PROPOSED |
| 1.7-03 | LOW | `pass_1_7_coherence.md:71-72` (Block 3 escalate) | Document escalation downstream pathway: "Escalation-flagged items surface at the post-Pass-2 human review gate per PB#5; until reviewed, Pass 3-6 synthesis proceeds on unresolved chunk outputs (productive-tension-acceptance is default for unresolved-but-escalated flags). Operator has final say at human gate." Cross-reference operator-review-gate at Pass 2 (Wave 4). | PROPOSED |
| 1.7-04 | LOW | `pass_1_7_coherence.md:66-68` (Block 3 accept-productive-tension) | Sharpen productive-tension criteria against escape-hatch usage: "Productive-tension criteria (ALL must hold): (a) both poles have primary-text or scholarly-consensus support; (b) tension drives rather than derails the voice's thinking; (c) scholarly tradition names the tension explicitly (not invented by the merge). If ANY unmet, it's a real contradiction — resolve by edit." | PROPOSED |

**Review — model + config:** KEEP. Opus 4.7 + adaptive thinking + **64K max_tokens** correctly calibrated post-Bug-5. Reconciliation requires simultaneously holding all 6 chunks (~80-120K input tokens), running 7 checks, editing outputs, composing final dossier in single LLM pass. Sonnet would drop checks under context pressure. **by_alias=True on model_dump** correctly preserves "register" JSON key for downstream. Cost ~$3.00-5.00/voice — largest single-call cost in family; input volume dominates. No config changes.

**Review — prompt (strengths):**
- **7 named operational checks** — each specific and mechanically runnable. Check 5 (passage-work orphan) is deterministic schema-validator-like. Check 7 (pathē carryover) directly honors Pass 1.4's Boddice §13 carryover directive — cross-chunk handoff wiring.
- **3-category resolution policy** preserves productive tensions — anti-flattening at coherence layer.
- **Explicit stake-naming** ("every inconsistency you miss becomes a silent contradiction propagated to the persona card") — real consequence-of-failure language.
- **Edits chunk outputs in place** — material reconciliation work, not flagging-only.
- **Cross-chunk handoff wiring.** Check 6 (hard_limits/commitments) enforces 1.2↔1.5 consistency. Check 7 (pathē→vocabulary) enforces 1.1→1.4 carryover. Coherence pass operationalizes discipline individual chunks set up but can't enforce alone.
- **Phase-L-validated.** Dostoevsky merged_dossier composed successfully; coherence_flags[] + coherence_resolutions[] both populated with real reconciliation entries.

**Review — research utilisation:** **Not applicable at 1.7** — SRI-1 + SRI-2 both concern how upstream research is used; 1.7 operates on already-merged chunk outputs (no dossier inputs). **SRI-1 pattern locked at 6/6 across Pass 1.1-1.6.** SRI-2 concentration remains at chunk level — forward-referenced Wave 4 compression concern.

*Observations (not fixes):*
- **max_tokens=64K may be tight for voices with large chunks.** Phase L Dostoevsky fit. If any Phase N voice hits max_tokens before JSON completes, bump to 80K. Related OPEN_ITEMS.md follow-up: retry-path should bump max_tokens on max_tokens-specific retry.
- **`coherence_flags` downstream use at Pass 2-6 forward-referenced to Wave 4** — verify whether synthesis reads flags (especially productive-tensions) or ignores them.
- **No BLOCK 4 WORKED EXAMPLES** in this prompt — pattern-break from 1.1-1.6. Resolved by 1.7-01.
- **SRI-1 Gemini-filtering not applicable here** — 1.7 has no dossier inputs. Pattern 6/6 at Pass 1.1-1.6 holds.
- **Pass 1.7 closes Wave 3.** Steps 20-26 all reviewed.

---

# WAVE 4 — Phase 2 Generation (Pass 2-6 + CT)

CT mechanism confirmed from `run_persona_pipeline.py:357-370`: `_ct_compress()` uses **Sonnet 4.6** (max_tokens=2048, temperature=0.0, thinking=False) on `persona_coherence_threading.md` template → ~500-token summary threaded forward into each Pass 3/4a/4b/5 user prompt via `{{ pass_N_summary }}` variable. CT as standalone review fires after Pass 6 (Step TBD).

## Step 27 — Pass 2 Identity & Boundaries

**Mechanism:** LLM call · Anthropic `claude-opus-4-7` · adaptive thinking · streaming · **max_tokens=24000** · temperature=1.0 · response_format_json=True · `_claude_pass()` wrapper in `run_persona_pipeline.py:338`
**System prompt:** `personas/flows/shared/prompts/persona_pass_2_identity_boundaries.md` (216 lines — Jinja branches on type/subtype/voice_mode/hostile_sources)
**User prompt:** `personas/flows/shared/prompts/persona_pass_2_user.md` (9 lines — reads merged_dossier)
**Does:** First generation pass. Reads `merged_dossier.json` → produces 10 persona-card Identity & Boundary fields including Phase-M-added `voice_temporal_stance`. Boddice §13/§14/§15 integration + Card v2 register-compliance + post-Phase-M chat-test learnings (hyphenated-virtue-signaling clause, [experiential_reconstruction] tag mandates, [projection_warning] on modern clinical terms).
**Verdict:** TUNE (with NEEDS-DECISION inside). 3 MED fixes + 1 LOW observation. **2-02 voice_temporal_stance is decision-gate before Phase N.**

| ID | Severity | File:lines | Change | Status |
|---|---|---|---|---|
| 2-01 | MEDIUM | `persona_pass_2_user.md:4-7` | **Stale user prompt — drift bug.** System prompt produces 10 fields (includes `voice_temporal_stance` added Phase M per commit `84e2b6b`); user prompt says "9 Persona Card fields" and lists 9 names. Pipeline contradiction. Phase L Opus 4.7 bridged empirically (Dostoevsky card has field populated) but future voices + model versions may not. **1-minute edit.** Update to "10 Persona Card fields" + add `voice_temporal_stance` to the field-name list. | PROPOSED |
| 2-02 | MEDIUM · **NEEDS-DECISION** | `persona_pass_2_identity_boundaries.md:139-159` + schema + runtime Voice Pipeline Step 1/2 | **Rewrite `voice_temporal_stance` as deployment-configurable** (Wave 3/4 boundary decision per task description). Current field hardcodes death-threshold anchor — chat-test-driven, **over-specified** for Voice Pipeline Step 2 which needs fluid-across-time framing per Athens brief "impossible participants take the floor while you sleep." **Proposed REWRITE:** `voice_temporal_stance.default` = fluid-across-time (Voice Pipeline artifact generation) + `voice_temporal_stance.anchored_override` = optional death-threshold anchor (chat/project deployments; preserves current Phase M content). Runtime Voice Pipeline Step 1/2 assembly respects override flag per deployment mode. Alternatives: KEEP (hardcoded 1881 anchor — under-serves Voice Pipeline); DELETE (loses chat-test bug fix). **Decision-gate before Phase N voice builds.** | PROPOSED — AWAITING USER DECISION |
| 2-03 | MEDIUM | `persona_pass_2_identity_boundaries.md:20-22` (Block 2 formative_experience guidance) | **Formative-candidate commit-to-ONE is anchor-concentration at Pass 2** — addresses forward-referenced Zosima-overanchoring concern. Current: "COMMIT to ONE candidate — the one with highest `scholarly_support_score` and cleanest fit to the voice's engagement." For well-documented voices (Dostoevsky: 6 formative candidates in dossier), commits to one and drops the rest — Phase L Dostoevsky card commits to Semenovsky-execution; Petrashevsky/katorga/Optina/Alyosha-death/Snitkina scattered across other fields, absent from `formative_experience`. **Reword:** "Commit to ONE PRIMARY formative candidate for narrative coherence. In `formative_emotional_community` and `engagement_it_drives`, explicitly reference 1-2 SUPPORTING formative candidates as biographical context — the primary formative doesn't exist in isolation. The formative is what drives engagement; the supporting candidates texture the engagement's specific shape." Preserves narrative-clean output while preventing formative-multiplicity loss. | PROPOSED |
| 2-04 | LOW (monitor) | `run_persona_pipeline.py:338` (`_claude_pass` default `max_tokens=24000`) | 10 fields with Boddice-rich content — Phase L Dostoevsky fit (~12-14K estimated output) but 4K lower than chunk-merge's 32K. **Monitor during voices 2-12.** If any voice hits max_tokens before JSON completes, bump to 32K (align with chunk family). Not fix-now. | MONITOR |

**Review — model + config:** KEEP model. Opus 4.7 + adaptive thinking correct for 10-field Boddice-rich synthesis from merged_dossier. Sonnet would regress on Boddice tag discipline (Phase L showed gaps on Opus itself) and register-compliance (Pass 7a flagged Pass 5 register violations even on Opus). **max_tokens=24K tight but fit** — 2-04 monitors. Streaming + temperature=1.0 + thinking=True SDK-forced.

**Review — prompt (strengths):**
- **Phase M learnings baked in** — `[experiential_reconstruction]` tag mandates on specific sub-fields (Pass 7-pre flag origin), `[projection_warning]` on modern clinical terms, hyphenated-virtue-signaling clause in `topics_requiring_care` (post-Phase-M chat-test). Prompt evolves with empirical findings.
- **OUTPUT REGISTER rule** (first/second person never third) stated directly with Card v2 citation. Load-bearing per "register of fields overwhelms register of frame" principle.
- **Boddice §13/§14/§15 integration thorough** — "DROP 'core wound + lesson' framing" explicit; character-grammar native-to-period explicit; `[projection_warning]` discipline explicit.
- **Voice-category variant patterns** in epistemic_frame_statement give Opus concrete shape for 7 voice configurations.
- **Conditional `{% if hostile_sources %}` block** handles Cleopatra-class voices correctly.
- **Phase-L-validated** on Dostoevsky — world/formative_experience/character Boddice-shaped with tags + register discipline applied.

**Review — research utilisation:**
- **SRI-1 N/A** — input is merged_dossier, not raw dossiers. SRI-1 locked at 6/6 Pass 1.1-1.6.
- **SRI-2 mixed.** Per-field specs direct substantive extraction (10-20 anachronisms, 3-6 sensitive topics with full navigation, Boddice-shaped world) — anti-narrowing mechanisms present. **BUT** `formative_experience.commits-to-ONE` is explicit anchor-concentration. **2-03 resolves this.** Zosima-overanchoring at Pass 2 is real and addressable; the prompt names the mechanism.

*Observations (not fixes):*
- **CT prompt carries Boddice-deprecated language.** `persona_coherence_threading.md:5-6` says "the wound and its lesson" — Pass 2 Block 2 explicitly DROPS this framing. CT review step (post-Pass-6) will land the fix.
- **Pass 2 → Pass 3 CT handoff** — CT compresses Pass 2 to ~500 tokens for Pass 3. What's preserved vs. dropped affects Pass 3 constitutional extraction. Evaluate during CT review.
- **`voice_temporal_stance` REWRITE affects Voice Pipeline Step 1/2 assembly** — out of scope per REBUILD_PLAN but field-level change creates implementation debt for that workstream. Flag at REBUILD_PLAN level.
- **Pass 2 revision-loop target per Pass 7a escalation** — forward-referenced for Wave 5 Pass 7a review: `_critique_suffix("2")` behavior on revision rerun.

---

## 🎯 Wave 3 summary — Phase 1 chunked merge + coherence, reviewed end-to-end

**Coverage:** 7 steps (20-26). Pass 1.1 BIOGRAPHICAL / 1.2 INTELLECTUAL / 1.3 REASONING / 1.4 VOICE / 1.5 BOUNDARIES / 1.6 CORPUS / 1.7 COHERENCE.

**Fixes logged:** 30 fixes across 7 steps (6 MEDIUM Gemini-filtering + 23 LOW refinements + 1 merged). Plus 1-arch-02 HIGH architectural proposal (Gemini re-route; post-Phase-N revisit). Plus 2 standing review items (SRI-1 Gemini-noise-leakage watch, SRI-2 corpus-utilisation depth).

### Architectural verdict (from Wave 3 preamble)

**KEEP.** Zero architectural fixes against the chunked-merge mechanism. PB#3/4/5/7/8 correctly realized. Shared chunk_runner harness + Pydantic validation + retry-with-critique + atomic writes + parallel 1.1-1.6 + sequential 1.7 + Phase-L-validated. Phase L bugs (1-5) were path-migration + max_tokens issues, not architectural flaws.

### Top 3 issues found

1. **SRI-1 Gemini-filtering absent 6/6 across Pass 1.1-1.6.** Fixes 1.1-01, 1.2-01, 1.3-01, 1.4-01, 1.5-01, 1.6-01 — all MEDIUM. **Coordinated cross-chunk patch is the efficient implementation path.** Feeds 1-arch-02 empirical test during voices 2-12: if the 6-file Gemini-lane-naming patch cleans up Gemini-noise signatures, Variant A (Gemini sectioned per-chunk) becomes less urgent. If noise persists, Variant A is vindicated.

2. **Worked-example coverage thin across 1.1/1.2/1.3/1.4/1.5/1.6** — 2-3 examples cover 5+ voice-type branches per chunk. Most impactful gaps: Cleopatra hostile-source (1.1-02 + 1.5-02), Scheherazade fictional (1.2-03 + 1.6-03), Dostoevsky narratival (1.3-02), Octopus non-human-organism (1.4-03 + 1.6-02), Marley `reference_only_passages` private tier (1.6-04). **All are lifts-from-Phase-L or small additions — low implementation cost.**

3. **1-arch-02 architectural refactor (HIGH, deferred).** Single largest open architectural question in Wave 3. Two variants (A: Gemini sectioned per-chunk; B: Gemini-only-at-1.7). Empirical test via SRI-1 during voices 2-12 determines urgency.

### Top 3 "keep as-is" endorsements

1. **Chunked merge architecture itself.** 6 parallel chunks + 1 sequential coherence + shared harness + Pydantic-validated + Opus 4.7 1M context + PB#7 convention-freeze discipline. **Zero architectural fixes.**

2. **Pass 1.2's specificity-rule two-voice swap test** (line 46-49) — File 3 "fine-grained constitutional principles" prescription operationalized at prompt-discipline level. "If two voices with different frameworks could both honestly assert this commitment, it is too generic — tighten it." Best-engineered merge prompt in the family.

3. **Pass 1.5's sanitisation-paradox naming + expression-vs-character-level boundary** — Khanmigo failure mode (File 3 Failure 4) named directly in prompt; `navigation_guidance` designated load-bearing; `hard_limits` scope cleanly bounded to catastrophic character failure with expression-level constraints deferred to Pass 7c. Best-of-prompt meta-design across the chunk family.

### Cross-chunk coordination insights (for implementation pass)

- **SRI-1 Gemini-filtering (6 files):** single coordinated edit cycle, per-chunk right-lane framing. Each chunk gets tailored wording (1.6's "actively preferred for URL surfacing" ≠ 1.5's "adjacency scanner on contested territory") but structural fix is uniform.
- **Voice_mode cross-chunk disposition policy:**
  - **Dropped** at 1.1 + 1.5 + 1.6 (biographical / boundaries / corpus) — where voice_mode doesn't affect extracted-material shape.
  - **Load-bearing by design** at 1.3 (reasoning) — Block 1 branches 5 ways.
  - **Make-load-bearing** at 1.2 + 1.4 (commitments / voice) — where reasoning-mode inflects extracted content.
  - One coherent policy; land in single coordinated 6-file edit.
- **Period-vocabulary gradation ripple (1.1-04 / 1.3-03):** coordinated patch targets **1.1 + 1.2 + 1.3 only** — 1.4 already has gradated wording; 1.5 + 1.6 don't use period-vocabulary rule.
- **1.4/1.5's guardrail-level voice-type awareness** (naming panel voices directly in Block 1 guardrails) is a **meta-pattern worth lifting back to 1.1/1.2/1.3** — more efficient than worked-example additions at resolving voice-type coverage gaps. Consider during implementation whether some 1.1-02/1.2-03/1.3-02 worked-example fixes can be replaced by guardrail-level callouts.
- **1-arch-01 + 1-arch-02 deferred post-Phase-N.** Both are architectural refactors that would restructure merge chunks substantially (1-arch-01: Pass 1.6 metadata-only + Pass 1d fuzzy-match; 1-arch-02: Gemini re-route). Both would partially invalidate Wave 3 fixes if landed before Phase N. **Correct sequencing:** land Wave 3 prompt fixes + run voices 2-12 on current architecture + review empirical output + decide arch refactors post-Phase-N based on calibration.

### Phase N strategy implications

- **NOT a Phase-N blocker.** Current architecture produced Phase-L-acceptable Dostoevsky output. Voices 2-12 can run on current prompts without Wave 3 fixes.
- **High-value-before-Phase-N fixes** (land before voice builds start):
  - 6 Gemini-filtering MEDIUM fixes (1.x-01) as coordinated patch — ~2 hours prompt edits, highest SRI-1 leverage
  - Cleopatra worked example at 1.1-02 + 1.5-02 (before Cleopatra Phase N build)
  - Scheherazade worked example at 1.2-03 + 1.6-03 (before Scheherazade build)
  - Marley `reference_only_passages` demonstration at 1.6-04 (before Marley build)
  - Dostoevsky narratival worked example at 1.3-02 (lift-from-Phase-L-card; cheap)
  - Octopus non-human worked example at 1.4-03 + 1.6-02 (before Octopus build)
- **Post-Phase-N decisions** (need empirical voices-2-12 data):
  - 1-arch-01 (curated_corpus_passages from Pass 1d) — calibrate based on passage-quality gap observed
  - 1-arch-02 (Gemini re-route) — calibrate based on Gemini-noise-leakage signatures under SRI-1 watch
  - Card-size question (Wave 5 concern; Dostoevsky 114KB vs. File 2 Lister 40KB) — surfaces after all 12 cards built

### Decisions needing input before Wave 4

1. **Implementation-pass timing.** Land Wave 3 fixes before Phase N starts, during Phase N, or after all 12 voices built? Coordinated 6-file Gemini-filtering patch alone is ~2 hours of prompt edits. Other Wave 3 fixes total ~10-15 hours.

2. **Wave 4 scope and sequencing.** Pass 2 / 3 / 4a / 4b / 5 / 6 + CT threading. **Temporal-stance keep/rewrite/delete verdict lands here** (Wave 3/4 boundary decision per task description). Forward-referenced Wave 4 items in registry above.

---

**Panel composition confirmed (12 voices):** Scheherazade (fictional), Cleopatra (human, hostile_sources=true), Whanganui (non_human, system), Audrey Tang (human), Ibn Battuta (human), Fyodor Dostoevsky (human — Phase L validated), Hannah Arendt (human), Plato (human — Phase N first voice), Ada Lovelace (human), Peter Thiel (human, legal-risk-flagged), Bob Marley (human, corpus_constraint=lyrics_patterns_only), Octopus (non_human, organism).

**By status:**
- PROPOSED: 99 (Wave 1-3 proposals + 3 Step 27 Pass 2 fixes; 1.6-05 resolved-via-merge; 2-02 awaiting user decision; 2-04 monitor-not-fix)
- **SUPERSEDED-VIA-1-ARCH-03**: 1 (1-arch-02)
- **OBSOLETE-UNDER-1-ARCH-03**: 8 (1.1-01, 1.2-01, 1.3-01, 1.4-01, 1.5-01, 1.6-01 Gemini-filtering MEDIUMs; 1.1-05 ContestedReading; SRI-1 Gemini-noise-leakage watch)
- **ABSORBED-INTO-1-ARCH-03**: 9 (1.1-02, 1.2-03, 1.3-02, 1.4-02, 1.4-03, 1.5-02, 1.6-02, 1.6-03, 1.1-06/1.5-03 fictional null-discipline, SRI-2 corpus-utilisation → preservation-rate metric)
- **RESHAPED-UNDER-1-ARCH-03**: 1 (2-03 formative-candidate reword)
- **SURVIVES independently**: Wave 1 (53) + Wave 2 (12) + voice_mode disposition fixes + period-vocabulary gradation + Pass 1.7 fixes + 2-01 + 2-02
- APPROVED: 0
- REJECTED: 1
- RETRACTED: 3 (prior 1b-R1/R2/R3 elevation items — research-misaligned)
- APPLIED: 0
- DEFERRED: 0

---

*This doc grows with each reviewed step. When the review is complete, it's the single source of truth for the implementation pass.*
