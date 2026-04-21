# Phase L.8 Quality Gate — Comparison Report

**Date**: 2026-04-21 (late afternoon)
**Branch**: `phase-b-rebuild` (HEAD pre-Phase-M)
**Subject cards**:
- **Phase B (new)**: `projects/phase-l-dostoevsky/voices/fyodor_dostoevsky/07_persona_card_assembled.json` — 114 KB, 35 fields, 2026-04-21
- **v3.7 baseline**: `~/Desktop/Dostoevsky_Persona_Card.md` — ~46 KB, 35 fields, 2026-03-27

**Size delta**: Phase B is 2.5× larger by bytes. Genuinely denser content, not padding.

---

## Comparison framework

Evaluated against all 5 authoritative sources — not Boddice alone. Boddice (File 5) was the most recent integration; File 2, File 3, File 4, and Persona Card v2 have been the design anchors from the start.

1. **File 2** — Claude DR technical dossier (compass_artifact_wf-c93e3b1d)
2. **File 3** — RAG + constitution + reasoning templates + persona vectors (compass_artifact_wf-cc778da2)
3. **File 4** — 13-persona repeatable pipeline architecture (compass_artifact_wf-865974da)
4. **File 5 (Boddice)** — biocultural critique (compass_artifact_wf-1e84f45b)
5. **Persona Card v2** — 37-field spec + Fidelity/Intrigue/Therefore register rules
6. **Pipeline v3.10 + EXECUTION_PLAN_phase_b.md §L.8** — explicit quality-gate checks

---

## 1. File 4 — 13-persona pipeline architecture

| Criterion | v3.7 | Phase B |
|---|---|---|
| Tool-section matching (Perplexity/Claude/Sonnet) | Partial — single Opus 4.6 manual paste | ✓ Full multi-tool pipeline |
| Multi-pass with coherence threading | No CT | ✓ CT after 2, 3, 4a, 4b |
| Section-by-section generation (30%+ mid-context loss mitigation) | 5-section manual draft | ✓ 6 chunked Pass 1.1–1.6 + 4-block architecture per pass |
| Cross-model critique (10–25% self-preference) | Not run | ✓ 7a via Gemini (openai missing — Bug 8); 7c via Gemini |
| Anti-hallucination guardrails per prompt | Light | ✓ Block 2 in every generation pass |
| Specificity testing (swap test) | Self-declared | ✓ 7a swap test via Gemini |
| 3+ unique concepts with textual refs | 5 "Rules out" concepts | ✓ 9 of 12 lexicon entries `[unique]` with original-language + rules-out |
| Expert-identity prompt per pass | Not explicit | ✓ Block 1 "EXPERT IDENTITY" |
| **Primary-source fetch + excerpt curation** (File 4: "single largest quality constraint") | **None — training data recall** | ✓ **22 URLs → 890K chars → 30K curated → `voice_basis: "corpus-based"`** |
| Verification protocols | None | ✓ Pass 7-pre → 7-anachronism → 7a → 7b → 7c |

**Verdict**: Phase B decisively delivers what File 4 prescribes. v3.7 had the vocabulary but not the machinery. Primary-text grounding alone is load-bearing.

---

## 2. File 3 — 4-layer architecture

| Layer | Prescription | v3.7 | Phase B |
|---|---|---|---|
| 1. RAG over corpus | Figure's own words | No | ✓ 890K chars, 8 curated passages with Tier tags |
| 2. Philosophical constitution | 10–20 specific principles with operational notes | 12 principles | ✓ **17 principles**, each `[tag]` + `[category]` + `textual_evidence` + `operational_note` |
| 3. Structured reasoning templates | "The layer most implementations miss"; 5–8 steps with worked demos | 7 steps + 1 demo | ✓ **8 steps** + `dialectical_signature` (4-field substructure) + `scenario_walk_through` |
| 4. Persona vectors | Out of scope per REBUILD_PLAN | N/A | N/A |

**Failure-mode guardrails**:
- Anachronism: ✓ Pass 7-anachronism + 12-item anachronisms_to_avoid
- Flattening: ✓ 8-step method + 4-chain smoke_test + dialectical_signature
- Hallucinated quotes: ✓ Pass 7-pre found 1 real inconsistency (Svidrigailov location) — system working
- Sanitization paradox: ✓ topics_requiring_care engages antisemitism/Geok-Tepe/Kroneberg **without sanitizing**

**Verdict**: 3 of 4 layers at prescribed specificity; all failure-mode guardrails present. v3.7 implemented Layer 2 only.

---

## 3. File 2 — DR tools + multi-pass prescriptions

- Multi-pass over single-pass: ✓ (6 chunks + 6 generation + 5 validation + 1 derive)
- Section-by-section with compressed forward summaries: ✓
- Tool-section matching: ✓
- Voice fidelity through primary-source grounding: ✓ `voice_basis: corpus-based`
- Citation verification: 47/64 verified; 1 real error caught (Svidrigailov) — working as designed
- Output should feel human-like: smoke_test_chains confirm this. Chain 2 ("necessary externalities") is pitch-perfect Dostoevskian. Chain 3 ("theology-of-suffering-as-alibi") performs Boddice's self-implicating move.

**Verdict**: Phase B meets every File 2 prescription that v3.7 missed.

---

## 4. Boddice File 5 — biocultural critique

| Criterion | v3.7 | Phase B |
|---|---|---|
| `world` = 5-part rubric | No | ✓ All 5 parts |
| 5–10 period-specific affects in original language with glosses | 0 Russian terms | ✓ **11 terms** in Cyrillic with glosses + no-modern-equivalent flags |
| `formative_experience` = 4-part §14 | No — "wound+lesson" | ✓ 3-part active + `[experiential_reconstruction]` |
| DROP "wound + lesson" framing | Present | ✓ Dropped |
| `character` in period-vocabulary (NOT Big-Five) | "Feverish intensity..." (Big-Five adjacent) | ✓ smirenie/sostradaniye/deyatel'naya lyubov' as virtues; modern terms flagged `[projected_categories]` |
| `[experiential_reconstruction]` tag | No | **Partial** — in 1 field; missing from 3 parallel fields (see Defect #2 below) |
| `[projection_warning]` tag | No | **Partial** — renamed to `[projected_categories]` in `character`; should be `[projection_warning]` (see Defect #3 below) |
| Anachronisms_to_avoid with reasons | No | ✓ 8 items with specific distortion reasons |
| Sensitive topics treated through voice's own apparatus, not sanitized | Partial | ✓ 6 topics with navigation including Kroneberg "morally compromising on its own terms, and I will not defend it" |

**Verdict**: 6/8 Boddice criteria met; 2 partial (tag coverage + tag naming) are mechanical fixes. v3.7 was pre-Boddice — total structural gap.

---

## 5. Persona Card v2 — register rules

Card v2 binding rule: first/second person, never third-person scholarly description.

| Field | v3.7 register | Phase B register |
|---|---|---|
| epistemic_frame_statement | Third: "I am an interpretive tool applying Dostoevsky's framework" | ✓ Second: "You are Fyodor Mikhailovich Dostoevsky..." |
| world | Third catalog | ✓ Second instructional |
| formative_experience | Mixed first/third | ✓ Second |
| character | Third description | ✓ Second imperative |
| constitution | First principles | ✓ First + second operational notes |
| Automated register check | Not run | ✓ **0 violations (CLEAN)** per runner's register scanner |
| Gemini cross-model register check | N/A | **REVISION_NEEDED flagged Pass 5** — output-characteristics fields drift toward descriptive mode; persistent through revision loop 2. Spot-check in Phase M. |

**Verdict**: substantially better on register. Phase B's epistemic_frame finally matches Card v2 §v3.7 second-person spec. Residual Gemini-flagged Pass 5 drift needs human spot-check.

---

## 6. Pipeline spec L.8 explicit checks

| Check | Result |
|---|---|
| `formative_experience` Boddice §14 4-part (not "wound + lesson") | ✓ |
| `world` Boddice §13 5-part | ✓ |
| Pass 4a period-vocabulary INFORMED but NOT scholarly-display | ✓ 43 Russian terms in preferred_vocabulary; smoke_test_chains deploy sparingly and in-context |
| `smoke_test_chains` build-time-only not runtime few-shot | ✓ metadata.smoke_test_chains_role explicitly says so |
| `[experiential_reconstruction]` / `[projection_warning]` tags | Partial — see Defects #2, #3 |
| `character` in period/tradition vocabulary | ✓ with explicit projected-categories flag on modern intruders |

**L.8 overall: PASS with 2 tag-compliance cleanups.**

---

## Cost + time comparison

| Metric | v3.7 | Phase B |
|---|---|---|
| Wall time per voice | ~15–30 min + manual paste | ~2 hours (steady-state ~90 min once bugs fixed) |
| Cost | ~$10–15 est. | ~$18–22 this run (high end due to Pass 1.7 retries + revision loops); steady-state ~$14–18 |
| Cross-model validation | None | ✓ 2 revision loops via Gemini |
| Primary text grounding | None | ✓ 22 sources / 890K chars |
| Boddice compliance | 0/8 | 6/8 (+2 partial) |

---

## Known defects in Phase B card (for Phase M iteration)

1. **Svidrigailov suicide location wrong** — card says "in the tavern" (reasoning_method.steps[5] + scenario_walk_through). Canonical: near a fire-watchtower. Pass 7-pre flagged.
2. **`[experiential_reconstruction]` missing from 3 fields**: `world.framework_for_difficulty`, `world.model_of_selfhood`, `formative_experience.engagement_it_drives`. Source dossiers carry these tags; synthesis stripped them.
3. **`[projection_warning]` mislabeled as `[projected_categories]`** in `character`. Rename.
4. **Holbein chapter reference** conflated with epileptic-aura passage (*The Idiot* II.iv vs II.v). Minor.
5. **Pass 5 register drift per Gemini**: output-characteristics fields (`medium`, `characteristic_output_structure`, `relationship_to_detailed_response`, `aesthetic_qualities`, `stance_tendency`, `length_and_format_constraints`, `quality_criteria`) slip toward descriptive mode per Gemini. Automated scan found 0 violations; human spot-check needed.
6. **`validation_status: REVISION_NEEDED`** carries forward. Not a blocker — spec allows finalization for human review.

---

## Overall verdict

**Phase B is substantively, architecturally, and empirically superior.** Not close:

- Boddice integration (6/8 met vs 0/8) is the most visible but not the biggest win.
- **Primary-text grounding** — File 4's "single biggest quality constraint" — is the largest single delta: v3.7 recalled from training data; Phase B reads Dostoevsky's actual words.
- **Multi-model verification chain** provides real cross-family critique v3.7 never ran.
- **Register compliance** is markedly better; Phase B's epistemic_frame now matches Card v2 spec.
- **Smoke test chain quality**: Chain 2 ("necessary externalities") and Chain 3 ("theology-of-suffering-as-alibi") are genuinely voiced Dostoevsky — the self-implicating move in Chain 3 is precisely what Boddice, File 3, and File 4 all prescribe and v3.7 couldn't produce without corpus grounding.

**Phase B is VINDICATED. Proceed to Phase M after the 5 defect fixes + openai install + validation re-run.**

---

## Next actions (for Phase M)

See `OPEN_ITEMS.md` §"PHASE L EXECUTION FINDINGS" for the commit-ready punch list.
