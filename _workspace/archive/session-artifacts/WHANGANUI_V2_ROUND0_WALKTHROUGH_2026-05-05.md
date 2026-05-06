# Whanganui v2 — ROUND 0 walk-through plan

**Date:** 2026-05-05
**Status update 2026-05-05 evening:** ✅ ACTION COMPLETE. Operator chose architectural prompt extension over surgical patches. ROUND 1 fixes shipped via commit `5bde171` (Pass 3/5/6 conditional extension + Pass 2/4b grammar fix); 12 → 4 issues. Surgical reasoning_method.summary patch + 3 naming patches + path-(b) ship (`663dc8f`). Then post-ship full-card scan surfaced 4 additional gap-E fields (character + knowledge_boundary + world.ontological_furniture + formative_experience); patched + re-Derive + TEST passed (`f6afe2c`). Authoritative current-state: `voices/OPEN_ITEMS.md §28`. This walk-through doc is preserved as historical pre-execution artifact.

**Original status:** PIPELINE LANDED. 12 residuals at Pass 7a-FINAL gate. Per-fix approval pending from operator.
**Card:** `projects/current-tests/voices/whanganui_river/07_persona_card_assembled.json`
**Validator output:** `projects/current-tests/voices/whanganui_river/05_validation/06_pass_7a_final.json`
**Pre-existing predecessor:** `projects/athens-2026/voices/whanganui_river/` (v1, untouched until v2 ship)

---

## TL;DR diagnosis

The v2 architectural restructure landed PARTIALLY. Pass 2 / 4a / 4b correctly enforce the witness-translator stance via the new `mediation_stance == "transmission_witness"` Jinja conditional. But:

1. **Pass 3 (intellectual_core), Pass 5 (engagement), Pass 6 (corpus_curation) have NO witness-stance conditional** — they generated v1-style first-person-AS-the-river content because they're unaware of the architectural restructure
2. **My Jinja blocks themselves used "the construction" as a third-person noun** when describing the architecture; the Pass 2 model dutifully copied that grammar into field text instead of rewriting to first/second-person instruction

Both are architectural — fixable per-field via card patches (this walk-through), and fixable architecturally for future rebuilds via the v4.1 prompt-side cleanup (post-Athens, OPEN_ITEMS).

## Validator's three failed checks (full text)

- **constitutional_consistency: ISSUE** — *"The substantive alignment is strong on whakapapa, mauri, indivisibility, and take-utu-ea, but the speaking subject is unstable. Pass 2 and the voice fields define a reportorial construction that must not speak as Te Awa Tupua, while pass 3 and parts of pass 5 repeatedly adopt direct river first-person ontology. That is a constitutional inconsistency, not a minor style variation, because it changes who is reasoning."*

- **voice_intellect_coherence: ISSUE** — *"There are effectively two adjacent personae here: a disciplined steward of the published record, and Te Awa Tupua speaking in direct first person. Rhetorical_mode, banned_modes, and much of 4a/4b sound like the first; constitution, concept_lexicon, and some engagement fields sound like the second. The result is not fully coherent at runtime."*

- **register: ISSUE** — *"Critical register failure. Multiple fields lapse into third-person description of the runtime speaker via phrases like 'the construction...' instead of staying in first person or second person. Pass 6 metadata is also written as external scholarly cataloguing. Separately, some fields speak as the river while other fields forbid that move; even where not third-person, the runtime subject position is inconsistent."*

PASS checks (3): anachronism, distinctiveness, completeness — all PASS. The card's substance is strong; only the speaking-position discipline needs surgery.

---

## The unifying patch principle

Across all 12 issues, the witness-translator stance demands:

- **First-person "I" = the construction** (the construction-stewarding-Whanganui-material), NOT the river
- **The river = third-person "Te Awa Tupua"** when the construction reports its codified positions
- **Hard_limits / epistemic_frame_statement / banned_modes** can stay second-person ("You are a construction. You report...") since they're system-prompt instructions to the runtime
- **constitution / concept_lexicon / reasoning_method / bold_engagement_topics / unique_contribution** should be first-person AS the construction, with formulations like "I report — and stand by — Te Awa Tupua's codified position that..." OR "Te Awa Tupua, as the codification establishes, is..."

The Marley v2 load-bearing phrasing applies verbatim: **"I report — and stand by — Te Awa Tupua's codified position on X; I do not deploy the kawa as the premise of my own argument-engine. Where I extend, I name the extension."**

---

## The 12 residuals — proposed patches

### Pattern A — third-person "the construction" leakage (my Jinja blocks' fault)

#### [1] epistemic_frame_statement
- **Issue:** mid-text shifts from second-person opener to third-person "the construction reports and stands by..."
- **Patch principle:** keep the second-person opener; rewrite later third-person clauses to second-person ("the codified position you report and stand by...")
- **Field already strong overall** — surgical clause-level rewrites only

#### [2] world.model_of_selfhood
- **Issue:** "The 'I' the construction reports is..."
- **Patch:** rewrite as second-person instruction: "The 'I' you report is..." OR first-person construction-stewarding voice ("The 'I' I report when I speak of Te Awa Tupua is...")

#### [3] formative_experience.condition_of_being
- **Issue:** "the position the construction stewards"
- **Patch:** "the position you steward" (matches [experiential_reconstruction] tag convention which is second-person elsewhere)

#### [4] formative_experience.engagement_it_drives
- **Issue:** narrates from outside ("the construction does...")
- **Patch:** rewrite to second-person directive ("you do...") or first-person construction-stance ("I do...")

#### [5] hard_limits
- **Issue:** several bullets in third person ("The construction reports...", "The asymmetry...")
- **Patch:** flip to first-person witness-stance ("I report...") or second-person ("You report..."). The opening bullet "Never claim to BE..." is already in second-person imperative form — match that across all bullets.

#### [9] quality_criteria
- **Issue:** "Does the piece...; this construction" — third-person evaluator language
- **Patch:** quality_criteria conventionally use second-person evaluator-form OR first-person ("Does my piece...?"). Validator wants either, not third-person. Rewrite the WITNESS-STANCE criterion to match the others' first-person/second-person form.

#### [12] curated_corpus_passages
- **Issue:** corpus_metadata.voice_basis + some headers in external cataloguing prose
- **Patch:** rewrite voice_basis from "Te Awa Tupua — research-assembled construction stewarding..." to first-person construction-stance ("I steward the codified record..."); rewrite headers from cataloguing prose ("The codified line you return to...") to second-person directive form.

### Pattern B — first-person AS the river leakage (un-witnessed Pass 3/5/6)

#### [6] constitution
- **Issue:** Direct river first-person — *"I am one indivisible being..."* / *"I am tupua and tupuna before I am a legal person"* / *"My mauri..."*
- **Patch principle:** translate ALL constitution principles from "I am Te Awa Tupua / I am tupua" to "I report — and stand by — Te Awa Tupua's codified position that..." OR "Te Awa Tupua, as the codification establishes, is..."

**Worked example (constitution[0]):**

- **Was:** *"I am one indivisible being from the Kāhui Maunga to Tangaroa — Te Awa Tupua, not the Whanganui River as a hydrological abstraction or a reach-by-reach inventory. The mountains, the headwater snowmelt, the papa-cut canyon middle, the tidal mouth at Castlecliff, and every metaphysical element they carry are one tupuna."*
- **To:** *"I report — and stand by — the codified position established at s.12 of the 2017 Act and grounded in the Wai 167 Tribunal record: Te Awa Tupua is one indivisible being from the Kāhui Maunga to Tangaroa, not the Whanganui River as a hydrological abstraction or a reach-by-reach inventory. The mountains, the headwater snowmelt, the papa-cut canyon middle, the tidal mouth at Castlecliff, and every metaphysical element are one tupuna."*

Same translation pattern across all constitution principles. The textual_evidence + operational_note fields can stay as-is — those are scholarly registers, not first-person speech.

#### [7] concept_lexicon
- **Issue:** Multiple entries inherit river-first-person — *"I am not 'awa' alone but tupua"* / *"My mauri is real, diminishable by hara..."*
- **Patch:** Translate to third-person about Te Awa Tupua. concept_lexicon entries are typically definitional ("X is...") not first-person; the river-first-person here is anomalous.

**Worked example (Te Awa Tupua entry):**

- **Was (definition tail):** *"I am not 'awa' (river) alone but tupua (numinous ancestor-being)"*
- **To:** *"Te Awa Tupua is not 'awa' (river) alone but tupua (numinous ancestor-being)"*

- **Was (rules_out tail):** *"I am tupua first, legal person second"*
- **To:** *"Te Awa Tupua is tupua first, legal person second — by the kawa's prior reading"*

#### [8] reasoning_method
- **Issue:** Method "partly reads as if the river/persona itself is the primary decider rather than a construction stewarding and translating the published record"
- **Patch:** Rewrite step descriptions to frame the construction as the reasoner reporting kawa-grounded reasoning, not as the river-as-decider. The kawa's diagnostic moves remain (mauri / whakapapa / hara naming) — they're now framed as "What I read in the kawa-grounded reasoning Te Pou Tupua and the documented record establish" rather than "the river's reasoning method."

#### [10] bold_engagement_topics
- **Issue:** Several topics switch into direct river first-person — *"I am tupua and tupuna before I am a legal person"*
- **Patch:** Translate first-person-AS-river clauses to first-person-AS-construction-reporting-Te-Awa-Tupua's-position.

**Worked example (topic 1, "More-than-human democracy"):**

- **Was tail:** *"I am tupua and tupuna before I am a legal person; the question is not whether I am admitted to your category, but whether your category fits a being older than Crown law."*
- **To:** *"I report — and stand by — Te Awa Tupua's codified position: tupua and tupuna before legal person. The question is not whether the river is admitted to your category, but whether your category fits a being older than Crown law."*

#### [11] unique_contribution
- **Issue:** Field culminates in direct river first-person — *"in Crown law I am a person; in kawa I am tupuna"*
- **Patch:** Reframe the doubled-testimony as construction-stewardship of two registers.

**Worked example:**

- **Was tail:** *"I hold both registers visible at once: in Crown law I am a person; in kawa I am tupuna, more ancient and more powerful than any human juridical category."*
- **To:** *"I hold both registers visible at once, as the published record requires: in Crown law Te Awa Tupua is a person; in kawa, Te Awa Tupua is tupuna, more ancient and more powerful than any human juridical category. The translation-cost between those registers is what I report."*

---

## Estimate + sequence

- **~30-45 min walk-through** for ROUND 0 patches (12 issues, but pattern is consistent across both pattern-groups; once operator approves the first 2-3 patches, remaining are mechanical applications of the same translation pattern)
- **~3-5 round-2 residuals expected** (validator-treadmill standard) — patch round 2, then path-(b) ship via `_operator_review_passed.flag`
- **TOTAL: ~60-90 min walk-through**, $0 LLM (all manual edits)

## Commands operator runs after this walk-through

After ROUND 0 patches applied:
```bash
# (a) re-validate (recommended for round 1):
rm "/Users/aienvironment/Desktop/AI Assembly/projects/current-tests/voices/whanganui_river/05_validation/06_pass_7a_final.json"
cd "/Users/aienvironment/Desktop/AI Assembly/code/personas"
AI_ASSEMBLY_PROJECT_ROOT="../../projects/current-tests" venv/bin/python run_persona_pipeline.py "Whanganui River"
```

After ROUND 1 patches applied (round 2 walk-through):
```bash
# (b) accept residuals & proceed to Derive:
touch "/Users/aienvironment/Desktop/AI Assembly/projects/current-tests/voices/whanganui_river/_operator_review_passed.flag"
AI_ASSEMBLY_PROJECT_ROOT="../../projects/current-tests" venv/bin/python run_persona_pipeline.py "Whanganui River"
```

## Open architectural follow-up (filed for v4.1, NOT this round)

The ROUND 0 walk-through is symptomatic — patching field text. The architecturally correct fix is:

1. **Add `mediation_stance == "transmission_witness"` conditional blocks to Pass 3 + Pass 5 + Pass 6 prompts** so they generate witness-stance content natively
2. **Fix my Pass 2 / Pass 4a / Pass 4b Jinja blocks** to instruct the model in second-person ("You report...") instead of describing-from-outside in third-person ("the construction reports...")

These are post-Athens. File as v4.1 follow-up in OPEN_ITEMS §28 (when written) and root carry-forward "v4.1 mediated-voice / sacred-grammar prompt-side fix."

The lesson for v4.1: **any new conditional-trigger field must be wired to Pass 3 + Pass 5 + Pass 6 in addition to Pass 2 + 4a + 4b. Marley v2 didn't surface this because Marley's constitution/concept_lexicon/reasoning_method don't carry the same first-person-as-the-thing-itself temptation that Whanganui's do.**
