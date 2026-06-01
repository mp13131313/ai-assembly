# SPEC: The Assembly's Annotated Response to *Magnifica Humanitas*

**Date:** 2026-05-27
**Status:** Design spec, pre-build
**Author:** Operator (Matthias) + Claude Code session
**Project root:** `projects/vatican-2026/` (new, parallel to athens-2026)

---

## 1. What we're building

A run of the AI Assembly pipeline against Pope Leo XIV's encyclical *Magnifica Humanitas* (released 2026-05-25, ~42K-50K words, 213+ numbered paragraphs across 5 chapters), producing as the headline published artifact **an annotated version of the encyclical** — Leo's text with marginalia from each of the ten voices, structured the way a Supreme Court ruling is structured: a majority opinion (the Pope) carrying the document, with concurring opinions, dissenting opinions, and refusals to engage from the panel.

The annotations are the artifact. Voices do not address each other directly; they address the document. The structural property of "agreement and dissent visible at the paragraph level" replaces the visible-deliberation architecture I had been proposing earlier — it's a simpler design that delivers the polyphony the Assembly's Briefing claims without requiring inter-voice address rhetoric.

This is the third major output mode the Assembly has shipped:
- Athens N1–N3: **dossiers** (synthesized articles by Tim, per-theme)
- Closing show (Athens): **matrix-mapped read-through** (positions plotted across two axes)
- This run: **annotated document** (per-paragraph stance + rationale, per voice)

---

## 2. The Supreme Court analogy as architectural primitive

Each substantive paragraph of the encyclical receives, from each of ten voices, one of:

| Stance | Meaning | Voice card precedent |
|---|---|---|
| `concur` | This voice agrees with the paragraph's substance | Voice's `core_commitment` is consonant |
| `concur_in_reasoning` | Voice agrees with the conclusion but reaches it differently | Voice's `reasoning_method` differs from Leo's |
| `concur_in_part` | Voice agrees with some of the paragraph, disputes other parts | Mixed engagement |
| `dissent` | Voice fundamentally disagrees | Voice's `core_commitment` contradicts |
| `dissent_in_part` | Voice disputes some of the paragraph but not all | Selective engagement |
| `qualify` | Voice would not affirm or refuse — would add a condition | Voice's `stance_tendency` is reframe |
| `refuse_engagement` | The paragraph's apparatus doesn't translate to this voice's tradition | Voice's `goes_flat_on` matches |
| `silent` | No annotation (default for paragraphs the voice doesn't substantively engage) | — |

A voice's `silent` status on a paragraph is itself information — it tells the reader "this voice did not have ground to stand on here." We do not force voices to annotate every paragraph; coverage emerges from voice character.

The annotation itself is 1-3 short paragraphs in the voice's natural register, marked with the voice's stance, calibrated confidence (0.0-1.0), and optional cross-references to other voices' annotations (without addressing them directly — references are like Supreme Court footnotes, not dialogue).

---

## 3. Data model

```json
{
  "paragraph_id": "§71",
  "paragraph_text": "Major tech platforms monopolise expertise, data and decision-making authority…",
  "annotations": [
    {
      "voice_slug": "ibn_battuta",
      "voice_display_name": "the Voice of Ibn Battuta",
      "stance": "concur_in_reasoning",
      "calibrated_confidence": 0.75,
      "annotation_text": "The platforms have the form of transmission without the chain. The qādī's authority depends on the chain having been witnessed; the platforms claim the form without the witness. Leo's diagnosis arrives at the right destination through a different road than mine — but it arrives.",
      "cross_references": ["cleopatra:§71"]
    },
    {
      "voice_slug": "cleopatra",
      "voice_display_name": "the Voice of Cleopatra",
      "stance": "concur",
      "calibrated_confidence": 0.85,
      "annotation_text": "γινέσθωι. The chancery cannot ratify what no body has authorised to ratify. Leo names the form that has captured the office.",
      "cross_references": []
    },
    {
      "voice_slug": "whanganui_river",
      "voice_display_name": "the Voice of the Whanganui River",
      "stance": "refuse_engagement",
      "calibrated_confidence": 0.9,
      "annotation_text": "The grammar of monopoly addresses an apparatus I am not. ko au te awa, ko te awa ko au. The question that reaches me through §83 — costs and burdens shifted onto others — is the question I have ground to answer.",
      "cross_references": []
    },
    {
      "voice_slug": "the_octopus",
      "voice_display_name": "the Voice of the Octopus",
      "stance": "silent",
      "calibrated_confidence": null,
      "annotation_text": null,
      "cross_references": []
    }
  ]
}
```

The published artifact is the encyclical text rendered with annotations in margin or footnote position per paragraph, organised by stance (concur first, then concur_in_reasoning, then qualify, then dissent_in_part, then dissent, then refuse_engagement — Supreme Court reading order).

---

## 4. Pipeline integration

| Stage | Role in this run |
|---|---|
| **Preprocessor** (`scripts/encyclical_to_session_package.py`) | Parse encyclical into paragraph-keyed structure. Each §-paragraph becomes one turn. Speaker = "Pope Leo XIV". Land via vendor_intake. |
| **Researcher** | *Skipped.* No need to extract positions from a position document. The Researcher's value (clustering atomic positions, surfacing themes) is wrong-shape for a single-speaker encyclical. We go directly to per-voice annotation. |
| **Provocateur** | *Replaced with per-voice paragraph routing.* A lightweight Python pass identifies which paragraphs each voice has ground to annotate, based on `activates_on` / `goes_flat_on` / `stretch` from each voice's profile. Output: per-voice paragraph candidate lists (~30-60 paragraphs per voice). No LLM call. |
| **Voice** (annotation mode) | New mode for `voice_flow.py`. Each voice receives: (a) the encyclical's full text; (b) its candidate paragraph list from routing; (c) its persona card. Voice produces annotations for ~20-40 paragraphs from its candidate list, choosing where it has the strongest engagement. Single LLM call per voice (model varies — see §5). |
| **Editor** (annotation mode) | Tim's role shrinks. Selection-based, not synthesis-based. Tim writes (1) an editor's preface for the annotated document; (2) per-chapter introductory notes ("the assembly's response to Chapter 3 clusters here…"); (3) chooses the lead annotations to feature in a separate "salient disagreements" surface. Tim does **not** rewrite voice annotations or weave them into composed paragraphs. |
| **Publish** | Render the annotated encyclical as the headline artifact. Each paragraph + its voice annotations side by side, with stance icons and confidence indicators. Cross-references hyperlinked. Also publish a "salient disagreements" digest where voices land in interesting opposition. |

The Researcher + Provocateur skip is significant: we cut two stages because the encyclical's input shape doesn't activate what those stages do. This is **stage routing as a function of input shape** — exactly the kind of decision an agentic pipeline would make on its own. We're making it manually for this run.

---

## 5. Multi-vendor base model assignment

Per the diversity-collapse literature (Wright et al. 2025, Yun et al. 2025, Zhu et al. 2026) and Maryanskyy's selection-bottleneck framing: heterogeneous base models are the strongest single anti-collapse defense.

### Proposed mapping (5 vendors across 10 voices)

| Voice | Model | Rationale |
|---|---|---|
| Plato | Anthropic Opus 4.7 | Dialectical reasoning, structured argument, dense conceptual work |
| Cleopatra | Anthropic Opus 4.7 | Terse prostagma discipline, Greek-Latin-Aramaic grammar handling |
| Fyodor Dostoevsky | Anthropic Opus 4.7 | Dense psychological prose, moral interiority |
| Hannah Arendt | Anthropic Opus 4.7 | Conceptual depth, Augustinian-Arendtian apparatus |
| Ada Lovelace | Anthropic Sonnet 4.6 | Mathematical precision; doesn't require Opus reasoning depth; cost-efficient |
| Ibn Battuta | OpenAI GPT-5 | Strong handling of Arabic transliteration + travel-witness narrative |
| Scheherazade | OpenAI GPT-5 | Narrative tradition, Persian/Arabic dialect handling, frame-tale grammar |
| Bob Marley | Google Gemini 2.x | Differentiation through different vendor's training distribution; musical/dialect register robustness varies by model |
| Whanganui River | Google Gemini 2.x | Multilingual fluency (te reo Māori); Gemini's broader Indo-Pacific representation |
| Octopus | Open-weights via OpenRouter (Qwen, Llama, or similar) | Maximum divergence from the dominant-vendor distribution for the panel's most non-human voice |

**Distribution:** 4 Opus, 1 Sonnet, 2 GPT-5, 2 Gemini, 1 open-weights.

### Why this mapping (and the assignable criteria)

Three factors weigh on each assignment:

1. **Voice-model fit.** Some voices have characteristics that suit specific model strengths. Dostoevsky's dense interior monologue suits Opus's extended reasoning. Scheherazade's frame-tale grammar is well-served by GPT's narrative training. Whanganui's te reo bilingual citation discipline benefits from Gemini's Indo-Pacific corpus exposure.

2. **Diversity spread.** Per Page's diversity prediction theorem (cited in supermind doc §7): collective error = average individual error − prediction diversity. The 5-vendor spread maximizes vendor-level diversity within budget.

3. **Cost.** Opus is most expensive; Sonnet and Gemini cheaper; open-weights cheapest. Total run cost target: ~$100-150. The cost-sensitive voices (Ada, the open-weights Octopus) are placed on cheaper models without quality compromise because the voices' characteristic outputs don't require Opus-grade reasoning.

### Per-voice temperature variation (new)

Currently all voices use adaptive thinking with the same effective sampling temperature. For diversity-defense:

| Voice register | Temperature |
|---|---|
| Assertive / declarative (Plato, Cleopatra, Marley) | 0.7 |
| Reasoning-deliberative (Hannah, Ada, Battuta) | 1.0 |
| Generative-divergent (Scheherazade, Octopus, Whanganui, Dostoevsky) | 1.2 |

This per-voice temperature lives as new metadata on the voice card (`generation_parameters.temperature`).

### Engineering implication

This requires:
- A vendor abstraction layer at `flows/shared/vendor_clients.py` (new) — wraps Anthropic, OpenAI, Google, OpenRouter clients with a uniform `call(model, system, user, temperature, structured_output_schema)` interface
- Per-vendor structured-output handling (different vendors support JSON-mode differently)
- Per-vendor thinking/reasoning configuration (Opus has adaptive thinking; o-series has reasoning_effort; Gemini has thinkingConfig; open-weights typically no thinking)
- Cost tracking per vendor in manifest
- Rate limiting per vendor (Anthropic + OpenAI + Google have different RPM limits)

**Realistic build time for vendor abstraction: 3-4 days, plus 1-2 days per-voice quality regression.**

---

## 6. Per-voice card extensions

Two new card fields for annotation-mode:

### 6.1 `annotation_register`

How this voice marks consent and dissent. Voice-specific because the rhetoric of agreement-and-refusal varies dramatically by tradition. Examples:

- **Cleopatra** marks consent with `γινέσθωι` (let it be sealed); marks dissent with `μή` (no/refused); refusals to engage with the absence of a seal at all
- **Ibn Battuta** marks consent with `naʿam, hādhā ḥaqq` (yes, this is right); concurrence-in-reasoning with `ka-dhālika fī kitābinā…` (so it is in our books); dissent with `lā, wa-llāhu aʿlam` (no, and God knows best)
- **Whanganui River** marks engagement only on paragraphs where the kawa translates; refusal is the default for paragraphs that address an apparatus the river is not
- **The Octopus** has no inherited rhetoric of consent; its annotations may need to invent new stance vocabulary (e.g. "the eight arms incline toward" / "the eight arms withdraw from")
- **Bob Marley** marks consent through musical-prophetic register; dissent through chanting-down formulas
- **Hannah Arendt** marks consent + dissent in essayistic English; her annotations are the closest to standard concurring/dissenting opinions in form

This is real editorial labor — perhaps 1-2 hours per voice. Total: ~1-2 days.

### 6.2 `silent_threshold`

How willing this voice is to leave paragraphs unannotated. Some voices (Hannah, Plato, Ada) will want to engage broadly. Others (Octopus, Whanganui, Marley) should be encouraged to mark `silent` on most paragraphs and engage only where their tradition has real ground. A simple scalar 0.0-1.0 indicating "fraction of candidate paragraphs this voice is expected to actually annotate." Defaults to 0.5 if unset.

---

## 7. The selection-vs-synthesis discipline (Maryanskyy 2026)

The annotated-encyclical is structurally selection-based:

- Voices **select** which paragraphs to annotate (not assigned, chosen from candidates)
- Voices **select** their stance per paragraph (not synthesized from a canonical position)
- Editor **selects** which annotations to feature in the salient-disagreements digest (not rewriting them)
- No synthesis layer; no Tim composition that weaves voices into a single argument
- The annotated document publishes each voice's exact words

This satisfies Maryanskyy's diversity-preservation prescription end-to-end.

---

## 8. Diversity defenses (audit against the framework)

| Defense | Status in this design |
|---|---|
| 1. Heterogeneous base models | ✅ 5 vendors |
| 2. Parametric persona injection | ⚠️ Prompt-based only — not addressing this in v1 (deferred) |
| 3. Different lenses/mental models per persona | ✅ 10 voices' existing card differentiation |
| 4. Different temperatures per persona | ✅ 3-tier per-voice temperature variation |
| 5. Different information feeders per persona | ✅ Per-card `curated_corpus_passages` |
| 6. Selection-based aggregation, not synthesis | ✅ Annotations published as-is; no synthesis layer |
| 7. Avoiding correlated priors | ✅ Voices' priors are uncorrelated by construction |
| 8. Calibrated confidence per move (Zhu et al. 2026) | ✅ Required field on each annotation |

7 of 8 defenses fully implemented. Parametric persona injection is deferred — it requires research-grade engineering (identity-vector injection into hidden states) that isn't accessible through any vendor's public API.

---

## 9. Build sequence

| Phase | Work | Days | Dependencies |
|---|---|---|---|
| **1. Encyclical ingestion + scaffolding** | Fetch full text, write preprocessor, set up `projects/vatican-2026/`, configure metadata, symlink voices | 1 | — |
| **2. Multi-vendor abstraction layer** | `vendor_clients.py` with Anthropic, OpenAI, Google, OpenRouter wrappers; structured output handling per vendor; cost tracking | 4 | — |
| **3. Voice card extensions** | Add `annotation_register` + `silent_threshold` + `generation_parameters` fields to all 10 cards; editorial work for `annotation_register` per voice | 2 | — |
| **4. Annotation-mode voice runtime** | New mode in `voice_flow.py`: annotation generation per voice. Includes per-voice paragraph routing (lightweight Python). Test with 2 voices first. | 4 | Phases 2, 3 |
| **5. Editor annotation-mode** | Tim's preface + per-chapter notes + salient-disagreements selection. Selection-only, no synthesis. | 2 | Phase 4 outputs |
| **6. Publication renderer** | Annotated-encyclical HTML/JSON renderer for microsite. Side-by-side paragraph + annotations layout. Stance icons. | 2 | Phase 5 outputs |
| **7. Agentic validation triage** | Pre-Editor C28b replacement. Reads voice annotations against `hard_limits`, auto-releases or escalates. | 2 | Phase 4 outputs |
| **8. Full run + diversity measurement** | Run end-to-end. Measure cross-voice annotation similarity (Yun et al. methodology) to validate diversity defenses. | 2 | All above |

**Total: ~19 days engineering + ~5 days regression and tuning = ~4-5 weeks calendar.**

Compressible to ~3 weeks if Phase 2 (vendor abstraction) is scoped tightly (only Anthropic + 1 other vendor for v1, expanded later) and Phase 3 editorial work is parallel.

---

## 10. Cost estimate

Per-vendor pricing (May 2026):

| Vendor | Input ($/1M) | Output ($/1M) |
|---|---|---|
| Anthropic Opus 4.7 | $5 | $25 |
| Anthropic Sonnet 4.6 | $3 | $15 |
| OpenAI GPT-5 | ~$5 | ~$15 |
| Google Gemini 2.x | ~$2 | ~$8 |
| Open-weights (OpenRouter, Qwen-class) | ~$0.50 | ~$1.50 |

Per voice run estimate:
- Encyclical input (~50K tokens) + persona card (~40K tokens) + routing context (~5K tokens) = ~95K input tokens
- Annotation output (30 paragraphs × ~500 tokens each) = ~15K output tokens

Total per-voice cost at blended ~$4/$15 averages:
- 4 Opus voices: ~$1.90 input + $9.40 output = ~$11/voice × 4 = $44
- 1 Sonnet voice: ~$1.15 input + $5.60 output = ~$6.75
- 2 GPT-5 voices: ~$0.95 input + $3.40 output = ~$4.35 × 2 = $8.70
- 2 Gemini voices: ~$0.38 input + $1.80 output = ~$2.18 × 2 = $4.36
- 1 open-weights voice: ~$0.10 input + $0.34 output = ~$0.44

**Total per run: ~$64.** With Editor + Publish + validation triage + iteration budget: ~$100-150 per complete run. Re-run budget: $300 total across 2-3 iterations.

This is **substantially cheaper than an Athens night** (~$30-70/night × 3 = $90-210 for Athens), because:
- No Researcher/Provocateur LLM cost (skipped)
- No Voice Step 2/Step 3 (annotation is one call per voice)
- No multi-stage validator
- Mixed vendors with cheap voices on cheap models

---

## 11. Open questions

Tagged for resolution before build starts:

1. **Encyclical text source.** Vatican.va has the canonical English HTML. NCR has a parseable version. Need to verify the §-numbering is consistent across sources. Spot-check on first day.

2. **Paragraph-level vs section-level annotation granularity.** Some encyclical paragraphs are 1 sentence; others are 8-10 sentences. Per-paragraph might be too granular. Alternative: voices annotate at *section* level (named sub-headings, ~50-80 across the encyclical) and reference specific paragraphs from within annotations. Probably the right call. **Decision pending.**

3. **Cross-references between annotations.** Voices can reference each other's annotations (Supreme Court footnote style). Do they see each other's annotations during generation, or are they retrofitted by Tim during Editor stage? Either works. The latter is simpler. **Tentative: retrofit by Tim.**

4. **Living-voice constraint on Pope Leo XIV.** The 10 council voices are dead/non-human. Pope Leo XIV is a living human, whose canonical life is in flux (no completion-anchor — same reason Audrey Tang + Peter Thiel were removed from the original 12). For this run, Leo's text is the input, not a participant. The encyclical's author is treated as the source document, not a voice. No persona-card representation of Leo needed.

5. **Provocateur replacement.** I propose skipping Provocateur entirely and using a lightweight Python paragraph-routing pass (matching voice profile fields against paragraph extractions). Alternative: run a stripped-down Provocateur (Triage A only, no Formulation) to identify per-voice paragraph activations. **Decision pending.**

6. **Tim's role.** Selection-only editor preface + chapter notes + salient-disagreements digest. Is that enough Tim-work to justify keeping him in the pipeline, or do we publish raw annotations without Tim? **Tentative: keep Tim, but with shrunk scope. The editor's preface is the published context.**

7. **Reflection on the encyclical's Tolkien Gandalf quote.** The encyclical apparently includes a Gandalf reference. Worth a footnote in Tim's editor preface; possibly an annotation-worthy moment for some voice. Cosmetic but interesting.

8. **Living-publication question.** Magnifica Humanitas was published 2 days ago. The Assembly's annotated response would appear ~5-6 weeks later. That timing is editorially appropriate — not breaking-news, considered. Worth noting in Tim's preface.

---

## 12. What this delivers

**Headline artifact:** the annotated *Magnifica Humanitas* — Leo's encyclical with marginalia from 10 voices, organised by stance, side by side with the text. Reads like an annotated text edition, not a newspaper. Publishable at a microsite URL.

**Secondary artifact:** salient-disagreements digest — Tim's selection of ~5-8 paragraphs where the voices land in interesting opposition. Frames the diversity for a reader who wants the highlights.

**Tertiary artifact:** diversity-measurement report — post-hoc Yun-et-al-style measurement of cross-voice annotation similarity, published alongside the artifact. Demonstrates the architecture's anti-collapse defenses are working (or surfaces that they aren't).

**Architectural artifact:** the multi-vendor abstraction layer, persistable for future Assembly runs. The annotation-mode voice runtime, persistable. These are reusable infrastructure.

---

## 13. What this does *not* deliver

- It is **not** visible deliberation. Voices do not address each other; they address the document.
- It is **not** a dossier-style Tim composition. The encyclical is the article; voices are the marginalia.
- It is **not** an Athens-night-shaped artifact. The audience is broader public, not WBBF attendees.
- It is **not** a full agentic pipeline. Most agentic fixes are deferred. Only the validation triage is included in this build (because validator over-triggering on theological material is high-risk).

---

## 14. Acceptance criteria

Before publishing:

1. **Diversity**: mean cross-voice annotation similarity (embedding cosine) below the threshold established by Yun et al.'s methodology adapted to this corpus.
2. **Coverage**: each voice annotates ≥10 paragraphs (no voice trivialised by the routing).
3. **Stance distribution**: across the full corpus, all 7 stances appear; refuse_engagement is not >40% of any voice's annotations (otherwise the routing is wrong).
4. **Editorial coherence**: Tim's preface and per-chapter notes read as a coherent editorial framing, not a recap.
5. **Calibrated confidence distribution**: per-voice confidence scores span ≥0.3 range (otherwise the voice is being uniform, which means the confidence calibration isn't doing work).
6. **No validator releases that would have been holds**: agentic validation triage's decisions match a sample of operator decisions on Athens N1+N3 data within 90% agreement.

---

## 15. References

- Anthropic, *Building Effective Agents* (2024)
- Anthropic Engineering, *How we built our multi-agent research system* (2025-06-13)
- Wright et al., *Epistemic Diversity and Knowledge Collapse in LLMs*, arXiv:2510.04226v3 (2025-10)
- Yun et al., *The Price of Format: Diversity Collapse in LLMs*, arXiv:2505.18949 (2025-05)
- Zhu et al., *Demystifying Multi-Agent Debate* (2026)
- Li et al., *Rethinking Mixture-of-Agents*, arXiv:2502.00674 (2025)
- Maryanskyy, *When Agents Disagree*, arXiv:2603.20324 (2026-03)
- Giacomelli, *Augmented Collective Intelligence* v.11.6 (2022-08)
- MIT CCI, *Supermind Design Primer* (2021-06)
- Rick, Giacomelli, Malone et al., *Supermind Ideator*, arXiv:2311.01937
- Heyman et al., *Supermind Ideator user study*, CI'24 doi:10.1145/3643562.3672611

Internal:
- `code/docs/AI_Assembly_Briefing_v3_1.md` (esp. "Constitute the collective at specific moments" + "Make the construction visible")
- `code/docs/AI_Assembly_Voice_Pipeline.md` (current Step 3 spec; needs replacement for annotation mode)
- `code/CLAUDE.md` Athens production state (validator misfire data, deployment_context mechanism)
- Audit notes from 2026-05-27 session (in conversation history)

---

## 16. Decisions still pending operator approval

1. **Granularity**: paragraph-level vs. section-level annotation (§11 item 2).
2. **Cross-references between annotations**: pre-generation or Tim-retrofit (§11 item 3).
3. **Provocateur replacement**: Python-only routing vs. stripped Provocateur (§11 item 5).
4. **Vendor abstraction scope for v1**: all 5 vendors at launch, or 2-3 with expansion later.
5. **Build sequencing**: serial through phases 1-8, or some parallelism (Phase 2 abstraction + Phase 3 card editorial can run in parallel, for example).

Spec to be reviewed and signed off before Phase 1 starts.
