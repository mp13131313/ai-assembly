# Review: which persona-card fields visibly shape the Athens output

**For:** the operator; inputs to Task 1 (split card + event config), runtime C59 ("Voice" row), cost planning, and Stage 4.
**Written:** 2026-09-28/29 by a Fable 5.1 session, Task 3 of `_workspace/planning/BRIEF_2026_09_28_fable_batch2.md`.
**Data:** `athens-2026` (read-only): the 10 cards, 125 Step 1 records, 30 Step 2 artifacts, 30 Step 2 validation files, and briefings. Offline scripts only; no model calls.
**Labels:** CONFIRMED = seen in data or code. PLAUSIBLE = consistent with the data but not proven. *Inference* = my reading. Decisions are the operator's.
**Revised 2026-09-29** after the independent review `REVIEWS_OF_FABLE_DELIVERABLES_2026_09_29/09_card_field_utility.md`: per-voice controls added; three verdicts downgraded; ablation redesigned for the USD 10 Stage 4 cap. §8 lists every change.

---

## Outcome

1. **About a third of the card does visible work, and it is mostly the expected third.** Strong, measurable effects:
   - `medium`: 30 of 30 `selected_form` values restate it;
   - `characteristic_moves`: 203 of 288 move checks performed; moves are planned by name in the traces;
   - `banned_language`: 202 of 213 banned items never appear in an artifact;
   - `banned_modes`: 0 list or heading lines in 155 texts;
   - `preferred_vocabulary` and `concept_lexicon` *terms*;
   - `curated_corpus_passages` (above both of its own controls in 8/10 voices);
   - the Night 2/3 continuity overlays.

   **Voice-dependent, measured against each voice's own controls:**
   - `constitution`: strong in 6/10 voices;
   - `formative_experience`: strong for Whanganui only (15.0%); the other nine voices pool to 0.55%, at control;
   - `unique_contribution`: thin (37 hits). Its "named in 21/30 weighings" is prompt-forced and doesn't count.
2. **About 15 loaded fields leave little or no visible trace.** Some have no effect we can see: `character`, `register_and_tone`, `aesthetic_qualities`, `relationship_to_detailed_response`, `technical_capabilities` (except Octopus). Others are fields whose job is to prevent something, so success leaves no trace (`hard_limits`, `knowledge_boundary`, `topics_requiring_care`, `world.anachronisms_to_avoid`). **This method cannot tell dead weight from insurance.** Only an ablation run can (§6.5).
3. **Card size is not the cost lever; caching is.**
   - The surviving Athens Voice Step 1+2 records cost **$67.40**. The system prompt (card + closing prompt) was **$36.17 of it (54%)**. CONFIRMED from token counts at Opus 4.7 prices.
   - **$67.40 is a lower bound.** Four voice-nights read caches that no surviving record wrote, so some calls are missing from disk (aborted or rerun).
   - **About $16 of that (24%) was avoidable:** same-voice Step 1 calls in the same batch all wrote the same cache, the pattern C66 fixed for the editor. The voice-side version is not filed.
   - Trimming every "none visible" field that isn't insurance saves about $0.6–1.4 per Athens.
4. **New defect, CONFIRMED and published: the Whanganui card's operator-facing `runtime_contract_note` leaked into the public Night 2 artifact.** The artifact says "I do not paraphrase these from public fragments at any pipeline step". Not in any tracker. See §5.1.
5. **Recommendation:**
   - fix the voice Step 1 cache race and the note leak now (both subtractive);
   - use the §3 table in Task 1's partition;
   - run a small removal test before any trimming or on-demand card loading. A Step-2-only arm fits the USD 10 Stage 4 cap (≈ $9); one full-rerun variant brings it to ≈ $13–15 (§6.5);
   - keep C59's `read_persona_card_section()` tool-use shelved: nothing here supports it, and it would put the strongest-effect fields at risk (§6.2).

---

## 1. Method

The input was 10 cards and every Voice output on disk:
- 125 Step 1 records (43 / 46 / 36 by night), each with `detailed_response` and `thinking_trace`;
- 30 Step 2 artifacts, each with `thinking_trace` and the decision fields (`weight_assessment`, `focus_*`, `stance*`, `selected_form`, `form_rationale`);
- 30 validation files.

Field routing was read from `runtime/flows/voice/card_assembly.py:82-152` (what loads at which step) and `runtime/flows/voice/step2_validation.py:154-300` (what the validators read).

| # | Method | What it catches |
|---|---|---|
| M1 | Field-name mentions (snake_case or spaced) in thinking traces and Step 2 decision fields | Explicit deliberation over a field |
| M2 | **Distinctive-phrase tracing.** Word 5-grams that occur in exactly one field of a card, in no other voice's card, in none of that voice's briefings (panel material) or the closing prompts, and in no other voice's outputs. Count how many reappear in that voice's outputs. **Negative controls:** the fields never loaded at runtime (`smoke_test_chains`, `bold_engagement_topics`, `metadata`) give the rate at which card-style phrasing turns up anyway. | Field-specific wording carried into output |
| M3 | **Item-level term tracing** for `preferred_vocabulary`, `concept_lexicon`, `banned_language` and `metaphorical_repertoire`. Each item's rate (per 10k words) in the voice's own text is compared with the other nine voices and with the voice's own panel input. For banned terms, the control is only voices whose cards do not ban the term. | Vocabulary adopted; bans obeyed |
| M4 | Verbatim quotation of `curated_corpus_passages` (longest shared run, ≥6 words) | Corpus use |
| M5 | Structural checks: `selected_form` vs `medium`; word counts vs `length_and_format_constraints`; list/heading lines; signature markers. Plus the voice-fidelity validator's per-move and per-criterion verdicts, an independent Sonnet reading whose reliability is Task 2's subject. | Fields that act on shape, not wording |

**Control baseline (M2, strict 5-grams).** Pooled, the three unloaded fields reappear at **0.8% / 0.8% / 0.0%** of their distinctive 5-grams. **The pooled figure hides per-voice spread:** `smoke_test_chains` ranges from 0.0% (Plato) to 3.5% (Whanganui). Field verdicts are therefore judged against **each voice's own two controls**: a field counts in a voice only if it beats both `smoke_test_chains` and `bold_engagement_topics` for that voice. CONFIRMED (`ngram_trace_5_1.json`).

| Voice | Control: smoke / bold | `formative_experience` | `constitution` | `unique_contribution` | corpus |
|---|---|---|---|---|---|
| Ada | 0.4 / 1.7% | 0.3% (2) | **4.1%** (59) | 2.0% (4) | 7.6% |
| Marley | 0.5 / 2.8% | 0.3% (2) | 0.2% (4) | 0.0% (0) | 2.2% |
| Cleopatra | 0.2 / 0.5% | 0.0% (0) | **1.3%** (27) | 2.9% (5) | 1.5% |
| Dostoevsky | 0.5 / 0.0% | 0.3% (2) | **1.6%** (39) | 1.0% (2) | 1.5% |
| Hannah | 0.4 / 0.3% | 0.0% (0) | **4.4%** (82) | 1.8% (3) | 3.5% |
| Battuta | 0.6 / 1.4% | 1.7% (10) | 1.2% (17) | 3.4% (5) | 2.9% |
| Octopus | 0.4 / 1.0% | 1.0% (6) | **3.8%** (72) | 3.6% (6) | 4.6% |
| Plato | 0.0 / 0.0% | 1.7% (9) | **0.8%** (16) | 0.0% (0) | 1.0% |
| Scheherazade | 2.4 / 0.7% | 0.2% (1) | 0.9% (18) | 1.7% (3) | 10.2% |
| Whanganui | 3.5 / 0.6% | **15.0%** (109) | 2.7% (58) | 4.3% (9) | 3.2% |
| **Voices above both own controls** | — | **3/10** (Whanganui, Battuta, Plato) | **6/10** | 7/10, on 0–9 hits each | **8/10** |

Pooled without Whanganui: `formative_experience` 0.55%, `constitution` 1.93%, `unique_contribution` 1.79%, controls 0.56% / 0.84%. Hit counts in brackets. Plato's controls are 0 on small samples, so his 0.8% `constitution` is only marginally meaningful.

**Scripts** are in this session's scratchpad (`load.py`, `mentions.py`, `ngram_trace.py`, `terms.py`, `banned2.py`, `corpus.py`, `metaphor.py`); they are not committed. Card prompt rendering used the real `card_assembly.assemble_system_prompt` offline.

## 2. What the method cannot show

- **Prevention leaves no trace.** `hard_limits`, `knowledge_boundary`, `topics_requiring_care` and `anachronisms_to_avoid` work by what does *not* appear. A low score is no evidence they are useless.
- **Overdetermination.** "No bullets" is in `banned_modes`, `length_and_format_constraints` and several `rhetorical_mode`s. "Translate modern concepts" is in `translation_protocol`, `constitution` and `concept_lexicon`. Credit can't be split between fields that say the same thing.
- **Model prior.** Some matches come from the model's own knowledge of the figure, or from paraphrase convergence, not from a specific field. Example: Battuta's outputs contain "beard hair by hair". Within his card that wording occurs only in the unloaded `bold_engagement_topics`. The Tughluq story itself is also in a corpus passage, so the model had the story but not those words. The 0.8% control measures this floor.
- **Prompt-driven naming.** The closing prompts (`voice_step1_reasoning.md`, `voice_step2_artifact.md`) list ~30 fields by name. When a trace says "carries the strongest unique_contribution", that shows the model complied with the prompt, not that the field content mattered.
- **Traces are summaries.** CONFIRMED: `_anthropic_call.py` requests `thinking: {"type": "adaptive", "display": "summarized"}`. Traces run 1.2–1.5 characters per billed thinking token in aggregate (per-record median 1.6, per the review). That is well under full-text density, so a field missing from a trace is weak evidence. `thinking_tokens` is itself estimated by subtraction.
- **Per-voice variance.** A field effect concentrated in one voice can look field-wide when pooled; `formative_experience` did (§1 table).
- **Verbatim is not use.** M4 counts ≥6-word quotations only. Plato quotes 1 of 8 passages verbatim but alludes to others throughout his Step 1 texts: "midwife" 6×, "philosopher-king" 7×, "unexamined" 3×. Other translations and the model's prior knowledge defeat a verbatim match.
- **Cost coverage.** Cost figures cover only the records on disk. Hannah N1/N2, Plato N1 and Marley N3 read Step 1 caches that no surviving record wrote. Ada, Marley and Cleopatra N2 read a prefix written earlier. So some calls are missing, and every dollar figure here is a lower bound.
- **No counterfactual.** Nothing was run without a field, so every "strong" below means *visibly present*, not *causally necessary*.
- **Matching limits.** Cleopatra's vocabulary is stored in Greek script while her text often transliterates it (e.g. `prostagma` 10×, `basilissa` 7×), so M3 undercounts her. Metaphor matching uses domain-name keywords.

## 3. Per-field utility table

Tokens are the mean rendered size per card, calibrated against the real cache-token counts (2.6–3.0 characters per token). The Step 1 system prompt is 37–51K tokens per voice. **Loaded:**
- P = shared prefix (Steps 1, 2 and 3);
- T = tail, all steps;
- S1 / S2 = that step only;
- — = never loaded.

**V** marks fields a Step 2 validator also reads.

M2 rates are strict 5-gram uptake in public text (Step 1 responses + artifacts). The pooled control is 0.8%, but verdicts use each voice's own controls (§1 table). "Named in N/30 Step 2 decisions" is prompt compliance where the closing prompt asks about that field, so it is not counted towards a verdict.

### Identity and constitution (prefix)

| Field | Load | ~Tok | Verdict | Evidence |
|---|---|---|---|---|
| `constitution` | P | 5,600 (largest) | **Strong in 6/10 voices; at control in 4** | M2 2.0% pooled. Above both own controls for Ada 4.1%, Hannah 4.4%, Octopus 3.8%, and moderately Cleopatra, Dostoevsky, Plato. At or below control for Marley 0.2%, Battuta, Scheherazade, Whanganui. Examples: Ada's engine vocabulary ("cards of operations", 52 Step 1 hits); Hannah's natality line. Not measured: which of its 12–19 principles are used. |
| `formative_experience` | P | 1,700 | **Strong for Whanganui only; weak elsewhere** | 109 of its 141 hits are Whanganui's (15.0% vs controls 3.5/0.6%). Also above own controls: Battuta 1.7% and Plato 1.7%, on 10 and 9 hits. The other seven are at control; pooled without Whanganui, 0.55%. "Named in 18/30 weighings" answers the prompt's own question (`voice_step2_artifact.md:16`), so it doesn't count. Dostoevsky's *mock-execution* move, drawn from this field, never appears (0/3). |
| `curated_corpus_passages` | P | 3,200 | **Strong in Step 1, weak in artifacts** | M2 3.8%, the highest; above both own controls in 8/10 voices; led by Scheherazade 10.2% and Ada 7.6%. **37/81 passages quoted verbatim in Step 1; 14/81 in artifacts, 7 of them Whanganui's.** 44/81 are never quoted verbatim, but allusion is not measured: Plato quotes only Phaedrus 275d yet alludes to the midwife 6× and the philosopher-king 7×. |
| `concept_lexicon` | P | 3,400 | **Terms strong, definitions none** | M3: 78/114 terms used in public text, 44/114 in artifacts, used ≥3× the other voices' rate. M2 on the definitions: 0.6%, at control. Weak voices: Dostoevsky 2/10 terms, Octopus 3/11. |
| `world` | P | 3,100 | **Weak** | M2 0.8% (control level). Visible only for Octopus (24 / 13 hits: "elicits multi-arm movement, never single-arm") and Hannah (11 / 4). `anachronisms_to_avoid` works by absence. |
| `epistemic_frame_statement` | P | 340 | **Weak** | Visible in 2/10 voices. Octopus reuses its facts ("some five hundred million neurons", "no somatotopic body map"). Never named. |
| `character` | P | 670 | **None visible** | M2 0.3%, 2/10 voices. Named in no trace except three generic uses of "character". |
| `council_member_name` | P | 120 | Not testable | Opens the prompt ("You are …"). |

### Boundaries (prefix; mostly prevention)

| Field | Load | ~Tok | Verdict | Evidence |
|---|---|---|---|---|
| `knowledge_boundary` | P, V | 1,300 | **None visible (prevention field)** | M2 0.1%. One trace mention. Read by the safeguards validator. |
| `translation_protocol` | P, V | 950 | **Weak by phrase; the behaviour is everywhere but can't be attributed** | M2 0.7%. Translation of AI into each framework is universal: Plato's "phantasmatopoiētikē apsychos" (`voices/plato/continuity_night_3.json`), Ada's operation/number cards, Battuta's *wakāla / ijāza*. The same instruction also lives in `constitution` and the closing prompts. |
| `topics_requiring_care` | P, V | 3,200 | **None visible (prevention field)** | M2 0.4%. Named in 2/30 Step 2 decisions. Acts only when a listed topic comes up; the safeguards pillar HOLDs on breach. |
| `hard_limits` | P, V | 1,150 | **None visible (prevention field)** | M2 0.4%. One trace mention. Behavioural effect is tracker-evidenced: the Hannah `hard_limits[4]` vs assembly-fiction collision (voices §31 Gap-J). |
| `voice_temporal_stance` | P, V | 230 | **Small, behaviourally visible** | Phrase trace thin (M2 1.2%, 2/10). The meta-framing it licenses is in the data: Hannah N1 artifact, "My own voice was synthesized to comment on the experiment that synthesized it". The causal claim is the tracker's (STATE "Architectural validation"; voices §31 Gap-K). |
| `reference_only_passages` | S1 | 580 (Marley 2,900) | **None visible; one leak** | 9/10 voices carry only the contract note (`passages: []`). Marley's 8 reference-only lyric passages: **0 verbatim 5-grams in any output (contract held)**. Whanganui's note leaked into public text (§5.1). |

### Reasoning and engagement (tail, all steps)

| Field | Load | ~Tok | Verdict | Evidence |
|---|---|---|---|---|
| `unique_contribution` | T | 450 | **Moderate, thin evidence** | M2 2.1% pooled, but only 37 hits: 0–9 per voice, 0 for Marley and Plato. Above both own controls in 7/10 voices, on counts too small to rank. "Named in 21/30 weighings" answers the prompt's question "Which carried `unique_contribution`?" (`voice_step2_artifact.md:19`), so it doesn't count. |
| `default_questions` | T | 370 | **Strong in Step 1, rare in artifacts** | M2 2.5%. Plato has 16 Step 1 hits (the craft-or-knack question: "aims at the body's health"); 6 artifact hits across all voices. Named by the Step 1 prompt only. |
| `reasoning_method` | T | 3,100 | **Moderate in Step 1, weak in artifacts** | M2 1.3%: 136 Step 1 hits vs 4 artifact hits (Hannah's "I question, I answer, I object, I concede"). **Named in 0 traces.** The Step 2 prompt never cites it, but it loads at Step 2. |
| `resists` | T | 860 | **Moderate, Step 1** | M2 2.0%: 61 Step 1 hits, 1 artifact hit. Named in 2/30 Step 2 decisions. |
| `finds_compelling` | T | 820 | **Weak** | M2 0.5% (control level). Named in 2/30 Step 2 decisions. |
| `disagreement_protocol` | T | 400 | **Weak** | M2 1.7%, 6/10 voices, Step 1 only. Named by no prompt and no trace. |
| `bold_engagement_topics` | — | 1,180 | **None (not loaded, FU#57)** | Control field: 0.8%. |

### Voice and expression (tail, all steps)

| Field | Load | ~Tok | Verdict | Evidence |
|---|---|---|---|---|
| `characteristic_moves` | T, V | 2,700 | **Strong** | Validator verdicts: **203/288 performed (70%)**. Traces plan moves by name: Scheherazade dawn-cut and ring-closure in 14/14 Step 1 traces; Plato *ti esti* in 13/13; Dostoevsky kiss-as-answer 13/14; Cleopatra's seal 12/12. M2 2.0%. **14 moves never performed in any scored artifact:** Ada ×5, Cleopatra ×4, Dostoevsky ×2, Hannah ×2 (only 2 artifacts scored; N1 failed to parse), Scheherazade ×1 (elevated parallelism for marvels). The Ada, Cleopatra and Dostoevsky moves are named in §4. |
| `banned_language` | T, V | 1,660 | **Strong** | **202/213 banned items never appear in an artifact** (155 never in any public text). Of the 123 items that occur in the voice's own panel input, 94 are used at under a third of the input rate; 74/112 are under a third of the rate in voices that don't ban them. **Named in 28/125 Step 1 traces, typically as a self-check**, e.g. Marley N1 `theme_010`: "no 'process,' no 'trauma,' no 'spirituality'…". Confound: register would suppress some of this anyway; 30 items are banned by at least 9 of the 10 cards (shared boilerplate). |
| `banned_modes` | T, V | 1,140 | **Strong but overdetermined** | 0 list or heading lines in 125 Step 1 responses and 30 artifacts. Three Step 1 texts use standalone bold lines as de facto headings (Whanganui N2 `theme_003` and `theme_007`, Plato N1 `theme_007`). Named in 11 Step 1 traces ("no bullet points, no cool detachment, no three-part essay structure", Dostoevsky N1 `theme_007`). |
| `preferred_vocabulary` | T | 2,530 | **Strong (terms)** | M3: **220/370 terms used in public text, 98/370 in artifacts**, almost all at ≥3× the other voices' rate. Strongest: Battuta 30/45, Whanganui 30/37 (25 in artifacts), Marley 26/34. **Position gradient:** 80% of first-quartile items used vs 43% of fourth-quartile (artifacts 37% → 18%). The builder's `loadbearing` flags cluster early (Ada: 16/20 flagged used vs 5/18 unflagged), so primacy and importance can't be separated. |
| `metaphorical_repertoire` | T | 1,160 | **Moderate** | 46/101 domains used at ≥2× the other voices' rate. **24 domains have zero keyword hits across 155 texts**: Hannah 6/13 (light/darkness, web, pearl-diving, desert, glass booth, wind); Plato 5/15 (rings/magnets, metals, hunting, mystery-cult, cosmos-as-animal); Scheherazade 4/10; Ada 3/9; Cleopatra 3/8; Whanganui 2/10; Dostoevsky 1/13. Position gradient 83% → 48%. |
| `rhetorical_mode` | T | 210 | **Weak as phrase; acts through `medium`** | M2 1.3%. The Plato criterion "honor rhetorical_mode" passed 3/3 in the validator's reading. |
| `register_and_tone` | T | 450 | **None visible separately** | M2 0.2%. Never named. Its content overlaps vocabulary, mode and corpus. |

### Artifact (Step 2 only)

| Field | Load | ~Tok | Verdict | Evidence |
|---|---|---|---|---|
| `medium` | S2, V | 180 | **Strong** | **30/30 `selected_form` restate it**: Ada "A Note in the Menabrea manner" + A.A.L. 3/3; Cleopatra prostagma 3/3; Dostoevsky Diary entry 3/3; Plato dialogue 3/3; Octopus JSON + prose 3/3; Marley riddim line 3/3. |
| `length_and_format_constraints` | S2, V | 240 | **Weak / partial** | **13/27 artifacts in range** (Octopus excluded: its counts include the JSON block). Over the range every night: Plato 589/614/745 and Whanganui 708/728/819 (vs 350–550), Marley 560–589 (vs 550). Word count or the envelope is referenced in 20/30 Step 2 traces. Compression is real: Step 1 medians are 856–1,318 words. The mechanical length check never fires (C38; PLAN 1.3 "dead length check"). |
| `stance_tendency` | S2 | 200 | **Weak** | Named in 5/30 stance rationales, e.g. Octopus N1: "exactly the stance_tendency posture". |
| `characteristic_output_structure` | S2, V | 290 | **Weak** | Named once. Read by the engagement validator. |
| `quality_criteria` | S2, V | 580 | **Weak for generation; its reader is the validator** | Named once in traces. Validator: 114/154 criteria passed. **9/10 cards phrase the criteria around an Athens breakfast reader** (FU#61), i.e. event content. |
| `aesthetic_qualities` | S2 | 230 | **None visible** | 0 phrase hits, never named. |
| `relationship_to_detailed_response` | S2 | 250 | **None visible** | 0 phrase hits. The "not more settled than the reasoning" rule is also in the closing prompt, which the traces echo instead ("the task asks me not to settle the artifact more than the reasoning settles it", Octopus N1 Step 2). |
| `technical_capabilities` | S2 | 190 | **None visible, except Octopus** | Octopus's JSON channel (3/3) is specified in both `medium` and this field. |

### Not loaded, and overlays

| Field | ~Tok | Note |
|---|---|---|
| `smoke_test_chains`, `metadata`, `bold_engagement_topics` | 5,300 + 5,700 + 1,200 | Never rendered. About 12K tokens per card that runtime never reads; zero runtime cost. |
| Continuity overlays (Night 2/3: `continuity_block_*`, `signature_moves_deployed`) | varies | **Strong.** Dostoevsky N3 form: "no swerve-via-childhood-memory and no cold-cup break (both used on prior nights)". Octopus N2: "deliberately not arm-by-arm, since night N-1 deployed that structure". Cleopatra's seal varies across nights: N1 "γινέσθωι — or do not", N2 terminal γινέσθωι, N3 "The seal is withheld". |

## 4. Per-voice highlights

- **Whanganui River: the most card-verbatim voice, by design.**
  - `formative_experience` 5-grams: 80 in Step 1, 29 in artifacts.
  - 7/8 corpus passages quoted in both Step 1 and artifacts; the Ruatipua whakataukī and the pepeha are carried as 23–24-word runs.
  - Matches the transmission-witness quality criterion.
  - Costs: the contract-note leak (§5.1), and length over range all three nights.
- **Octopus: highest move fidelity.**
  - 29/30 in the validator's reading; JSON channel 3/3.
  - Reuses `epistemic_frame_statement` facts.
  - Uses only 3/11 lexicon terms; its scientific idiom comes from moves and corpus (7/9 passages quoted in Step 1).
- **Plato: strong form and moves; corpus used by allusion, not quotation.**
  - Dialogue 3/3; moves 28/33; *ti esti* in every Step 1 trace.
  - Corpus: 1/8 passages quoted verbatim (Phaedrus 275d, Step 1 only), but others are alluded to (midwife 6×, philosopher-king 7×).
  - 5 of 15 metaphor domains carry the voice (cave, craft, light, ship of state, pharmakon).
  - Over length every night.
- **Cleopatra: the surface fields land; the deep form doesn't.**
  - Landed: prostagma 3/3, royal plural 3/3, seal used and varied.
  - Lowest move performance (8/24) and criteria (4/15) in the validator's reading.
  - Never performed: *standing as the goddess*, *speaking each people in its own tongue*, *coining a name for those who share my fate*, *staging the encounter as between equals*.
  - "Issues rather than argues" failed. This is voices §31 Gap-H ("analytical-comparative inside prostagma surface") showing up in production.
  - Corpus: 1/8 passages used.
- **Ada Lovelace: form and constitution strong.**
  - A.A.L. Note 3/3; engine-architecture vocabulary 110 uses.
  - 5 of 11 moves never performed although the traces mention them: cosmic-projective close, table-as-reasoning, triple-beat enumeration, confessional pivot, Latinate–Byronic interlace. Her four-beat criterion ("closed on cosmic sentence") failed every time it was scored.
- **Hannah Arendt: highest `constitution` uptake in artifacts (18 5-gram hits); 9/10 criteria passed.**
  - Cleanest ban/register effect: panel input uses "crisis" 15.8 per 10k words; her text 0. "Values": 5.8 vs 0. "Agency": 6.3 vs 0.
  - Her `quality_criteria` is a single string, not a list like the other nine (CONFIRMED; schema note for Task 1).
- **Fyodor Dostoevsky: continuity visibly steers form.**
  - Diary entry 3/3; kiss-as-answer planned in 13/14 Step 1 traces.
  - The *mock-execution sharpening* move is never performed or traced, although the execution scene is his `formative_experience`.
  - Uses 2/10 lexicon terms.
- **Ibn Battuta: strongest vocabulary uptake** (30/45 terms; 14 in artifacts).
  - Panel words "agency / empowerment / voice" occur at 33.6 per 10k in his input and 2.9 in his text.
  - Corpus quoted in Step 1 only (2/8), never in artifacts. Over length Nights 2–3.
- **Bob Marley: medium and metaphor strongest.**
  - Riddim line 3/3; 8/10 metaphor domains voice-lifted (Babylon/Zion 176 uses).
  - The reference-only lyric contract held: 0 verbatim reuse of its 8 passages.
  - Slightly over length every night.
- **Scheherazade: moves 31/39.**
  - Dawn-cut executed as the deferral ("If I live another night…") in 3/3, without the word "dawn".
  - 6/7 corpus passages quoted in Step 1, 2 in artifacts. Her `preferred_vocabulary` reaches artifacts only twice.

## 5. Findings outside the per-field question

### 5.1 Whanganui: operator-facing contract note published as voice text (CONFIRMED; not in the trackers)

- **The leak:**
  - `reference_only_passages` in `voices/whanganui_river/07_persona_card_assembled.json` has `passages: []` and a `runtime_contract_note` written for engineers. It ends: "restricted mātauranga… must NOT be paraphrased, synthesised, or 'filled in' from public fragments at any pipeline step."
  - `card_assembly.py:469-476` renders the whole field into Step 1, under the heading "REFERENCE-ONLY PASSAGES (your actual words; ground reasoning here)". That heading presents the engineering note as the voice's own words: a likely reason for the first-person echo (*inference*, from the review).
  - `runs/athens_night_2/04_voice/step1_detailed_responses/whanganui_river__theme_003.json` repeats it in the voice's first person.
  - The N2 artifact carries it into public text: "Restricted whakapapa, named-rapid karakia, urupā, specific-reach tapu… I do not paraphrase these from public fragments at any pipeline step."
- **Where it is published:** `published_artifacts/nights/night_2/whanganui_river.json`, `data_views/view_by_theme.html` and `data_views/athens_data_graph.json`. Night 2's Whanganui was held and is in no dossier; the voice page is published.
- **Same exposure on other cards:** every card carries a `runtime_contract_note`, rendered at Step 1 for all 10 voices. Only Whanganui's adds the restricted-knowledge sentence, and only Whanganui echoed its note.
- **Options:**
  - (a) render only `passages` at Step 1, drop the note, and skip the section when `passages` is empty. A few lines in `card_assembly`; subtractive. No rule is lost: Whanganui's `banned_modes` already carries the silence-and-naming-the-limit discipline.
  - (b) move the note to `metadata` at the split-card rewrite.
  - (c) also correct the published N2 page.
- **Recommendation:** (a) now, (b) in Task 1's design. (c) is the operator's editorial call.

### 5.2 Voice Step 1 cache-write race: ~$16 of $67 (CONFIRMED; not filed; C66 is the editor twin)

- **What happened:** in 12 of 30 voice-nights, *every* Step 1 call wrote the full system-prompt cache. Example: all 5 Dostoevsky Night 1 calls wrote 46,502 tokens; none read. In a 13th, Ada N2, every call wrote the tail but read the prefix.
- **The waste:** Step 1 wrote **3,028,612** cache tokens; one write per voice-night needs **~1,299,534**. The excess costs **~$16.4** (write minus read price), about 24% of the $67.40 on disk. Both figures are lower bounds (§2, cost coverage).
- **Cause:** CONFIRMED from code (`voice_flow.py:78, 194-207`) and, per the review, file mtimes.
  - Pairs are ordered voice by voice and run in sequential batches of `VOICE_STEP1_BATCH=6`.
  - Same-voice calls **within one batch** all write; same-voice calls in the next batch read.
  - The race is per batch, not per voice.
- **Tracker state:** not filed as a defect.
  - C36 names "cache write/read concurrency may interfere on first batch" as a risk.
  - C35 (batch 4→6) mentions cache-write collisions.
  - C19b foresaw the race on the personas side.
  - C66 (`d07e5cf`) fixed the same pattern for the editor.
- **Fix options:** run each voice's first call alone (the C66 pattern, adds wall time), or order pairs round-robin by voice so first calls of different voices share a batch. Round-robin is the review's *inference* and adds no wall time.

### 5.3 Thinking traces are summaries (CONFIRMED)

See §2. This matters for any trace-based evaluation, including Task 4's §33 memo: a trace shows what the summary kept, not what the model weighed.

## 6. Implications

### 6.1 For the split card (Task 1)

- **Strong fields are voice-card material:** `concept_lexicon`, `curated_corpus_passages`, `characteristic_moves`, `preferred_vocabulary`, `banned_language`, `banned_modes`, `metaphorical_repertoire`, and `constitution` (strong in 6/10). They are what makes a voice recognisable; none carries event wording except incidentally. `formative_experience` belongs on the voice card for identity reasons; this data shows it doing visible work only for Whanganui.
- **Event content found inside current card fields** (count of cards):
  - `quality_criteria`: breakfast-reader framing, 9/10;
  - `voice_temporal_stance`: names Athens, 9/10;
  - `unique_contribution`: "what no other voice on the panel sees", 6/10;
  - `length_and_format_constraints` / `quality_criteria`: "750 people", 3 cards.

  These belong in the deployment card, or in event config via the prompts. `unique_contribution` is council-relative, so make it council-scoped. Its measured effect is thin (§3), so this is a partition question, not a priority one.
- **Artifact-contract fields with no visible effect** (`aesthetic_qualities`, `relationship_to_detailed_response`, `technical_capabilities`, and `characteristic_output_structure` / `stance_tendency` with weak effect) should not all be carried into the deployment card by default. Candidates to merge into `medium` or drop, subject to §6.5. That nets out subtractive, per the roadmap gate.
- **The note and never-loaded fields go to `metadata`:** `runtime_contract_note` (§5.1), `smoke_test_chains`, `bold_engagement_topics`. That makes the "what runtime reads" boundary structural rather than a strip list.
- **Normalise shapes:** Hannah's string `quality_criteria` (§4).

### 6.2 For loading card sections only when needed (runtime C59, "Voice" row)

- **What the data supports is step-specific trimming, not tool-use.**
  - `reasoning_method` (3.1K), `default_questions` and `disagreement_protocol` show Step 1 uptake and almost none in artifacts, and the Step 2 prompt never cites them. Dropping them from Step 2 saves ~3.9K tokens per Step 2 call.
  - Keep `finds_compelling`, `resists` and `unique_contribution` at Step 2: the Step 2 weighing prompt cites them. That mismatch was the stated reason for the 2026-05-02 routing refactor (`ffad93f` + `9e1c987`; rationale in the `card_assembly.py:20-34` docstring).
- **Tool-use loading (`read_persona_card_section()`) is not supported by this evidence.**
  - The strongest effects come from content the model has in context and checks against: bans self-audited in 28 traces, moves planned by name in most traces.
  - A fetch-on-demand design makes those checks depend on the model deciding to fetch.
  - The fields tool-use would most naturally leave unloaded are the prevention fields (`topics_requiring_care`, `hard_limits`, `knowledge_boundary`, `world`: ~8.8K together), exactly the ones whose value this method can't see.
  - Keep C59 design-and-shelve.

### 6.3 For cost

- **Measured at Opus 4.7 prices** ($5 / $25; 1h cache write $10/MTok, read $0.50/MTok), records on disk only, so lower bounds:
  - Step 1: **$57.39**, of which cache writes $30.29 and output $20.75;
  - Step 2: **$10.01**;
  - system prompt: **$36.17 (54%)**.
- **Marginal cost of card size:** a 1K-token prefix field costs ≈ **$0.75 per Athens** today and ≈ **$0.35** once §5.2 is fixed (one write plus ~3 reads per voice-night, 30 voice-nights). The review gets ~$0.84 today by a different averaging; either way the conclusion holds.
- **Consequences:**
  - Trimming all visibly-dead, non-prevention fields (~1.8K tokens) saves ~$0.6–1.4.
  - The Step 2 trim in §6.2 saves ~$1.2.
  - Even halving the card (~20K) would save ~$7–15, less than the cache-race fix alone ($16) and at real quality risk.
  - **Card size is not where the money is.** Output tokens (Step 1 responses of 856–1,318 words, plus thinking) are the next-largest item.

### 6.4 For the Stage 4 prompt work

- **Lists are longer than the outputs use.** Examples: 14 moves never performed; 24 metaphor domains never touched; vocabulary use falls from 80% to 43% down the list. The corpus doesn't belong in this list: unquoted passages are often alluded to (§2).
  - *Inference:* Pass 4a could emit ranked lists marked core vs occasional instead of flat 30–45-item lists.
  - Don't cut on this evidence alone: three nights of one event's topics under-sample conditional use.
- **Some moves may be infeasible, not just unused.** Cleopatra's theological and Egyptian moves, Ada's cosmic close and Dostoevsky's mock-execution never appear in 350–550-word artifacts under analytical formulation pressure.
  - This is §31 Gap-H/I again. The Stage 4 fix belongs in the generator: a move-feasibility note, or a criterion requiring ≥2 moves as Plato's does.
  - Don't widen the cards.
- **Length is not held by card prose.** 3 voices overshot every night (Plato, Whanganui, Marley; Octopus excluded because its count includes JSON). A structured length field plus a code check (C38 / PLAN 1.2) is the fix; more card wording isn't.
- **Pass 6 / assembly:** never put operator-facing notes in a field the runtime renders (§5.1).
- **Prompt-level naming works:** the Step 2 weighing cites the fields the prompt lists. Deleting a field means also deleting its name from the closing prompts, or the model will reason about an absent field.

### 6.5 The honest test: a small removal run, sized to the Stage 4 cap (option; operator decision)

The operator's Stage 4 spend cap is **USD 10**. The estimates below:
- are from on-disk token counts at Opus 4.7 prices, so lower bounds;
- assume each voice's calls run sequentially (no §5.2 race);
- need the Athens model (`claude-opus-4-7`) pinned in `model_routing.json` for the run, or the Athens outputs stop being a valid comparison.

**Step 2 cost per voice-night, reusing the Athens Step 1 outputs:**
- the first call writes the shared prefix and its tail: ≈ $0.62;
- each further variant reads the prefix and writes only its own tail: ≈ $0.39;
- so three variants ≈ **$1.40 per voice-night**.

**Package 1, within USD 10: the Step 2-only arm (≈ $8.50).**
- 3 voices (Octopus, strong fidelity; Cleopatra, weak; Whanganui, sacred grammar) × Nights 1–2.
- Three variants:
  - a rerun of the shipped card, which measures run-to-run noise;
  - (b) the Step 2 reasoning trio removed;
  - (d) the no-visible-effect artifact fields removed.
- Judge by blind reading against the rerun and the Athens artifact.
- The existing validators add ≈ $0.10 per artifact (≈ $1.80 total) and would push it to about $10.30.
- This arm is also exactly the test Option B needs.

**Package 2, within USD 15: Package 1 plus (a) prevention fields removed (≈ $12–13).**
- (a) touches the shared prefix, so it needs full Step 1+2 reruns: 2 voices × Night 1 at ≈ $1.70–2.25 each, compared with the Athens outputs.

**Out of budget:** (c) every list cut to half. It also touches the prefix; it fits within USD 15 only as a replacement for (a).

**What it can show:** whether the Step 2 reasoning trio and the artifact descriptors matter (Package 1), and whether the prevention fields carry weight (Package 2).

**What it can't show:** effects on topics these formulations don't raise, or anything statistical at n = 2–3. It is also the cheapest instance of FU#30's card-richness question.

## 7. Options and recommendation

| Option | What | Cost | Net-complexity |
|---|---|---|---|
| **A** | Fix the §5.2 cache race (C66 pattern) and the §5.1 note rendering; hand the §3 table to Task 1 | ~2 h engineering; saves ~$16 per Athens-scale run | Subtractive |
| **B** | A + drop `reasoning_method`, `default_questions` and `disagreement_protocol` from Step 2 | ~$1 per run saved. Needs a paid Voice Step 2 rerun, which is §6.5 Package 1; the persona sentinel regen doesn't exercise runtime routing. It partly reverts the 2026-05-02 routing refactor | Subtractive, small |
| **C** | A + the §6.5 removal run before any Stage 4 list-length rule or card trim | Package 1 ≈ $8.50 (within the USD 10 cap); Package 2 ≈ $12–13 | Adds nothing permanent |
| **D** | C59 tool-use card loading | Weeks | Additive; not supported by this evidence |

**Recommendation: A now; C (Package 1, within the USD 10 cap) before Stage 4 touches list lengths or card size; B only if Package 1 shows no loss; D stays shelved.**

**To file** (for the main session; this review makes no tracker edits):
- §5.2 as a runtime C-item next to C66;
- §5.1 as a runtime item with a voices cross-reference (Pass 6 / split card);
- a pointer from runtime C59 "Voice" row and voices FU#30 to this review.

## 8. Revisions (2026-09-29, after the independent review)

**Accepted:**
1. **Per-voice controls:** table added to §1; verdicts now use each voice's own controls.
2. **`formative_experience`:** Strong → "strong for Whanganui only". 109/141 hits are Whanganui's; it is above both own controls in 3/10 voices.
3. **`unique_contribution`:** "Strong per token" → "Moderate, thin evidence". The prompt-forced "named 21/30" is no longer counted.
4. **`constitution`:** Strong → "strong in 6/10 voices".
5. **Prompt-forced naming:** excluded from all verdicts (§3 preamble).
6. **§2 limits added:** per-voice variance, verbatim vs allusion, and cost as a lower bound.
7. **Plato and the corpus:** allusion noted; the corpus leg is dropped from §6.4.
8. **Cache race:** 13 → 12 voice-nights (Ada N2 wrote only the tail). The cause is corrected to per-batch (`VOICE_STEP1_BATCH=6`). C35 and C19b are now cited, and round-robin ordering is added as a fix option.
9. **Leak cause:** §5.1 adds the section heading framing the note as "your actual words"; option (a) now also skips the empty section.
10. **Consistency:**
    - trim savings: one figure throughout ($0.6–1.4);
    - "4 voices overshot" → 3;
    - the duplicated length sentence is removed;
    - the C18/C20 citation is replaced by `ffad93f` + `9e1c987`.
11. **Option B:** needs a paid Voice Step 2 rerun, not the persona sentinel regen.
12. **Removal test:** redesigned for the USD 10 Stage 4 cap (§6.5, §7).
13. **Smaller corrections:** the bold-line quasi-headings are noted; the trace-density figure is corrected.

**Not changed, with reasons:**
- **Plato's `constitution`.** The review puts it at or below control. Against his own controls, which are 0.0% / 0.0%, his 0.8% is above them. It stays in the 6/10, flagged as marginal.
- **Marginal cost per 1K tokens.** $0.75 is kept; the review's ~$0.84 comes from a different averaging, and the conclusion doesn't change.

**Scripts:** still only in this session's scratchpad, since the brief allowed one deliverable file. The main session can copy them if the numbers are to be regenerated.
