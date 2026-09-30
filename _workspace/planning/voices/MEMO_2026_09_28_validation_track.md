# MEMO — Validation track: genuine perspective or elaborate ventriloquism? (voices §33)

**Date:** 2026-09-28; revised 2026-09-29 and 2026-09-30 after the independent review (`_workspace/planning/REVIEWS_OF_FABLE_DELIVERABLES_2026_09_29/10_validation_memo.md`). §10 lists every change, answers the review's questions and says where I disagree. On 2026-09-30 the paid tests were re-planned after the operator lifted the spend cap (§10.4).
**For:** the operator's open decision from June (voices `OPEN_ITEMS.md` §33; roadmap Stage 3, "validation-track decision").
**Written by:** a Fable 5.1 session, Task 4 of `_workspace/planning/BRIEF_2026_09_28_fable_batch2.md`.
**Status:** decision memo. Nothing here is decided. Claims are labelled **CONFIRMED** (seen in data or code) or **PLAUSIBLE**; interpretations are marked *inference*.
**Evidence base:** the Athens record in `projects/athens-2026/` (read-only). All 30 Step-2 artifacts and the 30 formulations they answered were read in full, plus a sample of the 125 Step-1 records. Offline scripts ran over all of it (§9). No model was called.

---

## Bottom line

1. **Most of the voices' verdicts were already in their questions.** I checked each of the 30 published pieces against the Provocateur formulation it answered (one coder; §3 P4):
   - **18** reach a verdict the formulation states or clearly implies;
   - **7** pick one of the options the formulation offered;
   - **5** go beyond it: Cleopatra N2 and N3, Arendt N2, Plato N2, Scheherazade N2.

   Four of the 30 calls are borderline; at worst the split is 19 / 8 / 3.

   The Provocateur writes each voice's question in its own call. Every call reads the same theme material and the same fault-line note, plus that voice's profile of about 340 words. So the same diagnosis lands in every voice's question, already fitted to that voice's vocabulary. The cross-tradition convergence that `EDITORIAL_ASSESSMENT.md` calls the edition's signature is mostly this. What the voices clearly add is *how* they argue: form, vocabulary, and which part of their framework they use.
2. **What stays open is narrower.** Would the voices still converge, and still reason differently from a generalist, if the questions did not lead? Athens cannot answer that. The Provocateur prompt and spec both forbid questions that contain their answer; 16 of the 26 focus questions state or imply the verdict the voice then reached.
3. **Recommendation**, in order:
   - **(a)** A second coder repeats the 30-verdict audit. Free, about half a day.
   - **(b)** File leading formulations as a Provocateur defect, whatever is decided here. Any later test of the voices needs questions that don't contain their answer.
   - **(c)** A replay, **Design A′**: the ten voices, a thin-card version of each, and a plain essayist answer Athens themes from a neutral question. §5.1 costs two plans: best value **≈ $24**, best for quality **≈ $190**. I recommend the best-value plan first.
   - **(d)** An expert blind panel (B) and the reader gates used as validation (C), in parallel. Each also has two plans (§5.2, §5.3).

   A′ should finish before two things: the voice-card / deployment-card field partition is frozen (roadmap 2.1), and any validation badge is shown. It blocks nothing else.

---

## 1. The question, made testable

The Briefing rules out the naive version: *"There is no authentic version waiting to be discovered. The construction is the representation."* (`docs/AI_Assembly_Briefing_v3_1.md:25`). So "genuine perspective" has to mean one or more of three claims the project does make:

| # | Claim | Where the project makes it | What would test it |
|---|---|---|---|
| **C1 Differential** | The configured apparatus (profile → formulation → card → Steps 1–2) produces reasoning a competent generalist, given the same brief, does not. | voices §33 point 2 | Blind A/B against a generalist |
| **C2 Framework extension** | The voice makes moves its corpus does not contain but its framework plausibly supports ("provotype test, NOT pastiche test"). | FU#49G (voices §11, lines 345–349; filed 2026-04-27, never closed) | Domain reader |
| **C3 Generativity** | The output says something the room could not have: *"If the content could have come from a well-read human essayist, the provotype has reduced to an art project."* | Briefing:51 (Layer 2) | A no-persona essayist baseline, plus the night's extractions |

**The pastiche hypothesis (H0):** the verdicts and the argument skeleton come from the base model, which at Athens means mostly the Provocateur. The card contributes vocabulary, citations, form, and the choice of mechanism. Under H0 an expert could still tell a voice from a generalist by its texture. So an identification test alone can't reject H0 (PRODUCT §11.3: "distinct-but-wrong is also distinguishable").

**What exists already is not validation.** The reader gates are a permission check. The 9-test rubrics are a regression check. FU#30 is narrow. The production Step-2 `voice_fidelity` pillar scores `characteristic_moves_performed` (plus `quality_criteria_results`): it rewards performing the card's signature moves. Its Athens result (10 PASS / 20 WARN; CONFIRMED over `runs/athens_night_*/04_voice/step2_validation/*.json`) bears on the costume, not on C1–C3.

---

## 2. Evidence for a real perspective (re-scored against the formulations)

**Columns:**
- **Verdict class**, from the §3 P4 audit: **S** = stated or implied by the formulation; **O** = picks an option the formulation offered; **N** = beyond the formulation.
- **Card/corpus hits** are term counts over `voices/<slug>/07_persona_card_assembled.json` and `03_corpus/`.

| id | Move | Verdict class; what was seeded | Standing |
|---|---|---|---|
| **E1** Arendt N2 | The formulation offered *"a new Nobody, or only the old Nobody given a fluent voice"*. The voice rejects both horns: *"There is no new Nobody. There is what I will call, for want of a better word, optional somebody… Optional answerability looks from a distance like answerability and is in fact its inversion."* | **N.** "optional somebody": 0 hits in the card, the corpus and her whole N2 briefing. Seeded: the disowning half (*"the human can shrug and say the machine did it"*) and the moral crumple zone were in the formulation; the 1964 *Personal Responsibility* move is in the card. | **Stands**, as the best C2 candidate on content. Its shape (refuse the binary, coin a third) is also P2's template beat, so the shape alone proves nothing (§4). |
| **E2** Dostoevsky N1 | *"the population fed on the flattering answer will not become flat. It will become a vast theatre of nadryv."* | **O.** The formulation offered the empty chair as the "stranger than that" horn. The counter-prediction is not in it. *nadryv* is in the card (13 + 9 Cyrillic). | Stands as a **new move inside a seeded frame**. |
| **E3** Ada N1 | *"Personalisation at the level of numbers, with operations supplied from a single source, is not pluralism."* | **S†.** The formulation offered the "originating into forming" frontier the artifact lands on. The operation-card / number-card taxonomy is in the card (7 / 3 hits); applying it to personal AI is new. | **Route, not verdict.** |
| ~~E4~~ Ada N2 | "Constitutive coupling" as a "third operation" | **S.** The formulation asks *"how would your Notes name and bound that third operation?"* and uses "constitutive". "Self-discovered slips are gain" is in the card (`constitution`, `disagreement_protocol`). | **Withdrawn.** |
| ~~E5~~ Cleopatra N1 | Sealed act over conversation | **S.** This is the Provocateur's own proposition (*"conversation around a common table is too thin a substitute for the sealed act"*), which the artifact affirms. Only "garland" is new (0 card hits). | **Withdrawn** as verdict evidence. Cleopatra's real cases are N2 and N3 (E10, E12). |
| **E6** Marley N2 | The capture sequence: schoolmaster = second person, press = third, the new instrument = first (*"I, I think this"*): *"You cannot chant down what the sufferer believe is her own thought."* | **O.** The formulation offered the old-captivity-or-new binary. The speaker-tag mechanism came from the panel: the Step-1 text says *"The brother explained the technical part… the tags drop out"* (CONFIRMED). The pronoun sequence is new. | **Route, not verdict.** |
| ~~E7~~ Octopus N1 | "bounded-narrative-self" | **S.** The formulation asks *"or at the bounded-narrative-self boundary"*. | **Withdrawn.** |
| **E8** Battuta N1 | *"As wijāda the artifact is licit. As teacher… no."* | **S.** The proposition supplied *wakīl* / *ijāza* / *ʿadāla* and invited a licence (*"if you would license such an agent, name the chain"*). *wijāda*: 0 card / 0 corpus. | **Route, not verdict:** the grading term is new; the licence was asked for. |
| **E9** Scheherazade N1–N3 | New tales each night: the qāḍī of Wāsiṭ, Hind in the tower, Zayd of Basra. | N1 **S** (the tale's premise was commissioned); N2 **N†** (the fragments-and-holes answer); N3 **S**. Wāsiṭ: 0 / 0. | Stands: invention inside the form. |
| **E10** Refusals and pushback | **Cleopatra N3.** All three of her N3 formulations are defend-or-refute propositions about the seal. The artifact takes over parts of their diagnosis, then withholds its own seal: *"To press γινέσθωι onto a body that has not yet been constituted is to seal air."* **Whanganui N2 and N3** criticise their own question's verb: *"the verb the question reaches with is ingests, and the verb has already done a take"*; *"the question's verb — extending personhood — has already performed something the kawa refuses."* Octopus N2 refuses *"the advocacy verb"*. Arendt N1: *"I will not deliver one I have not earned."* | Cleopatra N3: **N**, the strongest case in the record of a voice not doing what its questions invited. Whanganui N2's silence was itself offered by the formulation (**O**). | Stands. The original memo under-used Cleopatra N3 and missed the Whanganui pushback. |
| **E11** Tic self-monitoring | Octopus N2's form note: *"deliberately not arm-by-arm, since night N-1 deployed that structure and re-using it would calcify it into tic."* Dostoevsky N3: *"no swerve-via-childhood-memory and no cold-cup break (both used on prior nights)."* | Continuity-driven | Stands. |
| **E12** Plato N2 and Cleopatra N2 | Plato: *"Two darks, which to one not yet turned look alike"*; the critic *"appeals, in his very anger, to that-by-which the ship is condemned."* Cleopatra splits "two bodies": the good-life question adjourned, the harm question sealed. | **N / N†.** Neither formulation offers these answers. Both formulations did invite the concession about the voice's own tradition. | Stands. Both are the same split move (P2). |

† = borderline call (see §3 P4).

**Lexical differentiation is partial (corrected).** Some words are voice-specific: "ledger" and "load-bearing" appear in 2 voices each. But the analytic register is shared: "the room" in 8 voices, "register" 7, "instrument" 7, "chain" 5, "category" 5, "architecture" 4. The original memo quoted only the low counts.

---

## 3. Evidence for competent pastiche

**P4 — The questions carry the verdicts (CONFIRMED as a read; single-coder classification).** This is the central finding, so it comes first. Each artifact is classed against the formulation for its `primary_theme_id` (`runs/athens_night_N/03_provocateur/formulations/<theme>__<slug>.json`):

| Night | S: verdict stated or implied | O: offered option picked | N: beyond the formulation |
|---|---|---|---|
| N1 | Ada† · Cleopatra (proposition affirmed) · Arendt (*"the unit at risk…"*, verbatim) · Battuta (proposition affirmed) · Octopus · Scheherazade (tale commissioned) · Whanganui | Marley (*"not the same line"*) · Dostoevsky (*"stranger than that"*) · Plato† (*"something for which we as yet have no name"*) | none |
| N2 | Ada (*"third operation"*) · Dostoevsky (the confessor *"who will never name the sin"*) · Octopus (*"every option on offer still had a centre"*) | Marley (old captivity or new instrument) · Battuta (third bucket, and the verdict asked for) · Whanganui (a test and silence, both offered) | Cleopatra† (two bodies) · Arendt ("optional somebody") · Plato (two darks) · Scheherazade† (fragments and holes) |
| N3 | Ada · Marley · Dostoevsky · Arendt (*"both seem to dissolve the space between"*) · Battuta · Octopus · Plato (*"the same thing from opposite ends"*) · Scheherazade (*"the tale arriving before the teller"*) | Whanganui (*"where the translation must rupture"*) | Cleopatra (withholds the seal) |
| **Total** | **18** | **7** | **5** |

**† Borderline calls.** Ada N1 could be O. Plato N1 could be S. Cleopatra N2 could be O: each half of her split is one of the two offered horns. Scheherazade N2 could be S: that tale-telling is the held body's action is her own premise. Flipping all four gives 19 / 8 / 3.

**What the table shows:**
- **26 of the 30 focus formulations are questions and 4 are propositions.** Of the 26 questions, 16 are S, 7 O and 3 N. Of the 4 propositions, the voice affirmed 2 (Cleopatra N1, Battuta N1) and went beyond 2 (Cleopatra N2 and N3).
- **Four voices account for all five N cases:** Cleopatra (2), Arendt, Plato and Scheherazade. Cleopatra is the one voice built `hostile: true`. The other six never went beyond their question at the level of the verdict. Several added moves inside it (E2, E6), and the Whanganui voice twice criticised its question's verb (E10).
- **The convergence cases (P1) are mostly S.** Of the 13 artifacts in the four convergence cases, 10 are S, 2 O and 1 N.
- **The voices don't copy the formulations' wording.** Across the 30 artifacts, the median share of an artifact's content trigrams that also appear in its own formulations is 1.5% (the review's replica: 0.6%).

**How the verdicts get upstream (CONFIRMED in the prompt, `runtime/flows/shared/prompts/provocateur_formulation.md`).**
- The Provocateur writes one formulation per (theme, voice), each in its own Opus 4.7 call (`model_routing.json`, `runtime.provocateur.formulation`).
- Every call gets the same theme material and the same Triage notes on fault line and audience friction (`:163–164`), plus that voice's profile.
- The prompt tells it to aim at the profile's `activates_on`, to press against `core_commitment` (`:36–41`), and to target "AUDIENCE FRICTION" (`:49`).
- The profile is nine short fields in `council_config.json`, a median of about 340 words per voice, distilled from the card.

So the step "apply this voice's framework to tonight's theme" is done first by a generalist holding the short profile. The same prompt forbids the result: a question *"does not contain its own answer"* (`:21`), and a proposition is *"NOT a thesis that already contains its answer"* (`:28`). The spec lists *"**Leading.** Contains its own answer"* as a failure mode (`docs/AI_Assembly_Provocateur_Pipeline.md:335`).

**Corrections to the original P4:**
1. **The construction is visible.** Formulations are published verbatim: `formulations_per_voice[].formulation_text` in all 18 selected-theme files under `published_artifacts/themes/` (the other 6 theme files are themes dropped at selection), and `headnotes[].formulation_text` in all 13 dossiers (CONFIRMED).
2. **"Recognised, not granted" is the Whanganui voice's own `core_commitment`** in `council_config.json` (CONFIRMED). The Provocateur relayed the voice's thesis; it did not author it.
3. **The shared word runs are the Provocateur's prose, not panel quotes.** 104 six-word runs are shared between artifacts and their own formulations, across 17 artifacts. 98 of them appear nowhere in that night's transcripts or Researcher files (CONFIRMED, `sixgram_provenance.py`; the review found the same).
4. **Nearest tracker item:** voices §31 Gap-H ("pipeline pressure: formulation calls for analytic answer"). Leading formulations as such are not filed (both trackers searched for "leading" and "contains its own answer").

**New, from the re-check: a formulation's framing can enter print as something the room said (CONFIRMED).** Arendt N2 says: *"The room at Hotwire reached for that phrase and asked whether the model now interleaved between command and consequence is a new Nobody."* No N2 speaker used Arendt's phrase. "Rule by Nobody" has no match in the N2 transcripts or Researcher files; the formulation introduced it. One instance found; the record was not searched for others.

**P1 — Same verdict, different routes (CONFIRMED; reinterpreted).** On each shared case, voices from unrelated traditions converge:

| Night / case | Voices (verdict class) | Shared verdict | Distinct routes |
|---|---|---|---|
| N1, a personal AI for every citizen | Ada S†, Plato O†, Battuta S, Arendt S | Personalisation is not sovereignty | operation-cards · *eidōlon* of dialectic · no *tawkīl* / *tazkiyya* · the inner objector foreclosed |
| N2, speaker tags lost when the model compacts a conversation | Marley O, Arendt N, Dostoevsky S | The machine captures the first person | pronoun sequence · "optional somebody" and the dissolved seam · confession without a face |
| N3, the child who learned he was depressed from a chatbot | Arendt S, Battuta S, Plato S, Scheherazade S | A name given without the labour or chain that makes it one's own | second speaker pre-empted · *wilāya* displaced · right opinion untethered · a writ with no teller |
| N3, "rest on behalf of those in survival mode" | Marley S, Dostoevsky S | The absent sufferer is instrumentalised | "the sufferah become the alibi" · love in dreams vs love in action |

No voice sided with the room against the critical position: none endorsed the hive mind, AI personhood or the personal-AI tutor. Given P4, the convergence is **mostly authored upstream**, not undecidable. What remains untested is whether the voices would converge *without* leading questions. The Briefing named the risk (Briefing:317: "If everything clusters in one quadrant, the reveal lands flat"), and the closing-show mapping that would have measured it was never built (STATE, B5).

**P2 — One argumentative skeleton across voices (CONFIRMED as a read; beat counts crude).** Most artifacts run the same five beats:
1. restate a room claim;
2. reject its framing (split it in two, expose a shared premise, or call it a category mistake);
3. apply the voice's apparatus;
4. state the framework's limit;
5. reformulate the question, or leave it open.

Regex counts over the 30 artifacts:
- names the room: 18/30 (10 voices);
- refusal vocabulary: 20/30 (9);
- explicit limit statement: 12/30 (9);
- split-into-two: 11/30 (7).

Plato N2 and Cleopatra N2 are one move in two registers: concede the "underbelly", split the question, give aporia to one half and action to the other. (Corrected detail: Cleopatra does not *close* on the woman with her hand raised; Plato does.)

**Where the beats come from (corrected).** The original memo credited FU#49H. That was wrong: FU#49H was reverted in `3feb2b2` on 2026-04-28 and is not in the current prompts (voices OPEN_ITEMS:236–241). The limit beat traces to `translation_protocol`. The Octopus N3 artifact quotes it: *"The translation protocol marks the gap… Where the framework does not reach, name the gap rather than cross it."* It also traces to the FU#49C framework-strain directive in `conference_facts.json`. Self-critique of one's own tradition is licensed by FU#49D, which was re-applied after the revert.

**P3 — The new moves are mostly contemporary concepts in costume (*inference*; my identification, not an expert's).**
- Ada's constitutive coupling ≈ reflexivity or performativity. The formulation asked for exactly this.
- The Octopus's bounded-narrative-self ≈ the episodic-vs-narrative-self distinction. Also asked for.
- Marley's "alibi" ≈ the critique of speaking for others.
- Dostoevsky's theatre of nadryv ≈ the return of the repressed.
- Arendt's "optional somebody": its nearest analogue, the moral crumple zone, was in her formulation. She turns it from a description of the machine (it absorbs blame) into a description of the person (a named author with an on/off switch).

Battuta N2's *ẓālim* was **asked for** by its formulation (*"what is the verdict on a host-king…"*), and the artifact says *"I am asked, and I will give one."* The original memo's "the verdict the model would give anyway" is withdrawn.

**~~P5~~ — Withdrawn.** The original memo read Plato's N1 `theme_005` Step 1 as a "case against democracy" that "never reached print". Both parts are wrong:
- The response is a *ti esti* definitional challenge. Its Republic-VIII paragraph *agrees* with a speaker (*"He spoke truly"*). The trace says: *"I won't use my Republic VIII account as a final word"* (CONFIRMED).
- The text has been published in `published_artifacts/data_views/` (`view_by_theme.html`, `athens_data_graph.json`) since 2026-06-02 (athens-2026 `942abb4`; CONFIRMED).

No other case was found, and my search was a keyword scan of three voices, not an audit. FU#49's fidelity-generativity gap stays a pre-Athens reviewer finding that this memo does not demonstrate. Design 0b (§6) would test it properly.

**P6 — A fixed repertoire recurs (CONFIRMED; weak).**
- Whanganui cites the Tongariro diversion and Hikuroa, Salmond & Brierley every night; "144 years" appears on N1 and N3 only (corrected).
- Cleopatra's γινέσθωι appears every night; P.Bingen 45 on N1 and N2 only (corrected).

This fits a card-as-memory repertoire, but real people also repeat their convictions.

**P7 — The reasoning layer is openly a generalist planning a performance (CONFIRMED; low diagnostic value).** 117 of 125 Step-1 traces open in planner stance (*"I'm being asked to respond as Ada Lovelace…"*). The traces are summarised thinking, and the Briefing expects this mechanism, so it proves nothing on its own. Card-field mentions are frequent: 42 traces name a field under my strict pattern; the review counts 45 that mention "banned…" under a looser one.

**P8 — The construction states H0 about itself.** Arendt N1: *"Sentences in my idiom were generated; no one in them was thinking… these can be reproduced as surface features."* The scene was seeded: her `theme_004` formulation says *"your own voice was synthesized to comment on the experiment that synthesized it"*, and the artifact repeats that sentence in the first person.

---

## 4. What the evidence suggests (*inference*)

- **The verdicts came from the questions; the routes came from the voices.** At Athens the question stated, implied or offered the verdict in 25 of 30 artifacts. The card supplied the route: which apparatus, which citation, which form. That the voices differ in route is well supported. That they differ in *perspective* is untested, because the questions led.
- **A short profile was enough to pick the verdict.** The Provocateur is a generalist holding about 340 words per voice. In 18 of 30 cases the full-card voice then reached the verdict that generalist had written. That is a partial answer to C1 at the level of the verdict, and it cost nothing to find. The 38–44K-token card added the execution, and in five cases a verdict the question did not contain. Two caveats: the profile is itself distilled from the card, and the record doesn't show what a full-card voice concludes from a neutral question.
- **The five N cases are the best evidence for perspective.** Cleopatra N3 above all. None of the five is explained by its formulation. All five come from voices with a strong built-in disposition: the hostile Cleopatra, and Arendt, Plato and Scheherazade, whose defining moves are distinction, dialectic and deferral.
- **Shape and content are separate questions.** E1 and E12 share P2's shape (refuse the binary, split or coin a third), so the shape is not evidence. Their content can still be: "optional somebody" appears nowhere in Arendt's card, corpus or briefing. C2 is a claim about content, which is why it needs a domain reader.
- **What can be claimed today, without any test.** The voices differ in form, vocabulary and route. Their verdicts were mostly set by their questions. Five pieces went beyond their questions.
- **For Phase 2.** How much of the card to load, and what a validation badge would mean, both depend on what the card contributes. At Athens that can't be separated from what the questions contributed. Family of forms works on form, where differentiation is strongest; it is already an operator BUILD decision (roadmap 1.2, 2026-06-13) and is not affected.
- **What this memo cannot show:** authenticity (excluded by design); audience effect / Layer 3 (not examined); expert-grade fidelity. The 30-verdict audit is one coder's judgement.

---

## 5. The cheap tests: what each costs, and what each can and can't show

### 5.1 Blind A/B against a generalist, re-scoped after P4

**A neutral question.** At Step 1 a voice receives two things (`build_step1_user_prompt`, `runtime/flows/voice/step1_private_reasoning.py:99`):
- `narrative_briefing`, written per voice by the Provocateur: a display title, a scene-setting paragraph, selected quotes and the formulation;
- the Researcher's record of the theme: title, abstract, clusters and extractions (`filter_theme_record_for_step1`, `runtime/flows/voice/card_assembly.py:511`).

The neutral condition keeps the Researcher's record, which already carries the theme's title and abstract. It replaces `narrative_briefing` with one fixed line, the same for every voice, and empties the per-voice list of grounding extractions. That is a change to a sandbox briefing file, not to code.

**Arms:**

| Arm | System prompt | User input | Role |
|---|---|---|---|
| **Full-neutral** | shipped card | neutral question | what the configured voice concludes when not led |
| **Full-led** | shipped card | the Athens briefing, unchanged | a fresh led sample made under the replay's own conditions, so that the question is the only difference from Full-neutral |
| **Full-targeted** | shipped card | the Athens briefing with its formulation rewritten to drop the verdict | what a Provocateur that kept its own rule (`provocateur_formulation.md:21,28`) would send |
| **L2 thin card** | voice name + one-line identity + `medium` + length | neutral question | the same as Full-neutral, with almost no card |
| **G0 essayist** | no persona | neutral question | Briefing Layer 2's "well-read essayist"; voice-independent, so sampled per theme |
| L1 (optional) | thin card | the Athens briefing, unchanged | the card's contribution *under* a leading question (FU#30) |

The thin card renders because `_render_section` skips missing fields (`runtime/flows/voice/card_assembly.py:285–300`, CONFIRMED). G0 needs its own short system prompt, so a small sandbox script (PLAUSIBLE; not built).

Every arm runs without continuity, so the arms are comparable with each other. The Athens originals differ from the replay in two ways at once (the question and the continuity). That is why Full-led is run fresh instead of reusing them.

**Two plans for A′.** The operator lifted the spend cap on 2026-09-30, so neither plan is sized to one. The first gives the most evidence per dollar. The second is what I would run with no cost constraint.

| | **Best value** | **Best for quality** |
|---|---|---|
| **Themes** | 2, both answered by all ten voices at Athens: N2 `theme_007` ("Contesting the good life") and N3 `theme_001` ("AI reframed as a human and social question") | 6, two per night: those two plus N1 `theme_002`, N1 `theme_004`, N2 `theme_001` and N3 `theme_003`. Three hold P1 convergence cases; on the other three the traditions could plausibly pull apart. |
| **Arms and samples** | Full-neutral ×2, Full-led ×1, L2 ×1, 5 essays per theme | Full-neutral ×3, Full-led ×2, Full-targeted ×2, L2 ×3, 10 essays per theme. Led and targeted run on the 51 voice × theme cells that have an Athens formulation. |
| **Steps** | Step 1 only. Verdicts are formed there, and the Athens record already shows that form differs by voice. | Step 1 for all. Step 2 on one sample per cell for Full-neutral, Full-targeted and L2, to check that the result survives into the published form. |
| **Calls** | 90: 60 full-card, 20 thin-card, 10 essays | 795: 384 + 111 full-card (Step 1 + Step 2), 180 + 60 thin-card, 60 essays |
| **Coding** | Two people code all 90 texts blind, about 2 days each | A non-Claude judge model codes all 795 texts on the same sheet. Two people code a 90-text subsample (two themes, one sample per cell), about 2 days each. The judge's codes are used only if they match the human codes on at least 85% of the subsample (proposed threshold). |
| **Preparation** | one sandbox briefing file per voice; the essayist script | the same, plus 51 formulations rewritten by hand and checked by a second person, and the judge prompt |
| **API cost** | **≈ $24** | **≈ $190** |
| **If same-voice calls run in parallel** | ≈ $41 | ≈ $340 |
| **Elapsed** | about a week | 3–4 weeks |
| **What it adds** | the three contrasts (question, card, essayist), read against a noise floor | whether the result holds across themes and nights; what rewritten questions would produce; form; the pairs the expert panel needs (§5.3) |
| **What it can't do** | Two themes, so a result could be theme-specific. Nothing on rewritten questions or on form. | It is still not expert judgement. The judge's reliability is an assumption, which the subsample tests. |

**Assumptions behind both estimates:**
1. **Prices.** Opus 4.7 at $5 / $25 per MTok; one-hour cache writes at 2×, cache reads at 0.1× (`docs/AI_Assembly_Voice_Pipeline.md:1266`).
2. **Token sizes** are the Athens medians (CONFIRMED from the Step-1 and Step-2 records). A Step 1 call reads about 8.4K uncached and 37.6K cached tokens and writes 6.6K. A Step 2 call reads about 9.7K uncached and 45.5K cached and writes 5.3K.
3. **Warm cache.** Each voice's full-card calls run one after another, so only the first writes the card to the cache and the rest read it. A read renews the one-hour timer. In `voice_flow.py` same-voice calls run in parallel by default (`:78,194`), and at Athens each of them wrote the cache (the race in `voices/REVIEW_2026_09_28_card_field_utility.md` §5.2). The second cost line is that case.
4. **Thin-card and essay calls** are priced without caching.
5. **No retries.** Add about 10%.
6. **Same model as Athens.** `claude-opus-4-7` is still pinned for `runtime.voice.step1` and `step2` in `model_routing.json` (CONFIRMED at `40fe490`). If that changes (C62), every arm runs on the new model and the Athens originals stop being comparable.
7. **The judge** (quality plan only) is priced at Opus 4.7's rates as a ceiling. It would be one of the non-Claude validator models already routed in `model_routing.json`; their prices are not in the repo.

**Unit prices:** full-card Step 1 ≈ $0.58 for a voice's first call and ≈ $0.23 after that; full-card Step 2 ≈ $0.37, then ≈ $0.20; thin-card or essay Step 1 ≈ $0.21; thin-card Step 2 ≈ $0.18.

| | Best value | Best for quality |
|---|---|---|
| Full-card Step 1 | 10 × $0.58 + 50 × $0.23 = $17.30 | 10 × $0.58 + 374 × $0.23 = $91.82 |
| Full-card Step 2 | none | 10 × $0.37 + 101 × $0.20 = $23.90 |
| Thin card | 20 × $0.21 = $4.20 | 180 × $0.21 + 60 × $0.18 = $48.60 |
| Essays | 10 × $0.21 = $2.10 | 60 × $0.21 = $12.60 |
| Judge | none | ≤ $14 |
| **Total** | **≈ $24** | **≈ $190** |
| Every full-card call writes the cache | 60 × $0.58 + $6.30 ≈ $41 | 384 × $0.58 + 111 × $0.37 + $61.20 + $14 ≈ $340 |

L1, if wanted, adds about $4 to the value plan and about $21 to the quality plan.

**Decision rules (corrected: relative, not absolute; fix them before coding).** Code each Step-1 response blind on one sheet: verdict, direction relative to the room, mechanism, new coinage.
- **Question test.** On the same cells, compare Full-led with Full-neutral. If the led samples reach the Athens verdict and the neutral ones do not, the question set the verdict.
- **Convergence.** On each theme, count how many of the ten Full-neutral responses share the most common verdict, and whether that is the essays' verdict. Proposed reading:
  - 8 or more of 10 on the essayist's verdict: the verdict is the model's default, whatever the question. The supportable claim is "route, not verdict".
  - 5 or fewer: Athens's convergence came from the questions, and fixing the Provocateur is the lever.
  - 6 or 7: unclear. In the value plan, that is the signal to run the quality plan's other themes.
- **Noise floor.** *r* = the share of voice × theme cells where two Full-neutral samples get the same verdict (20 cells in the value plan, 60 in the quality plan).
- **Card test.** Compare agreement(L2, Full-neutral) with *r*. Only large gaps are readable. With 20 cells, a gap of 6 or more is roughly where noise stops being a plausible explanation (rough two-proportion test, p ≈ 0.03–0.05); 5 cells gives p ≈ 0.09. With 60 cells the same point is a gap of about 10. Smaller gaps are inconclusive, not evidence that the card does nothing.
- **Mechanism.** If L2 and G0 match Full-neutral on verdict but not on mechanism, the card buys the route.
- **Rewritten questions (quality plan).** If Full-targeted spreads the verdicts the way Full-neutral does, enforcing the Provocateur's own rule is enough. If it converges like Full-led, the voice-specific framing leads even without a stated verdict.

**Can show:** whether the question set the verdict; whether the voices converge when not led; whether the card shapes verdicts or only routes.
**Can't show:** fidelity (that needs experts); audience effect; Marley and Whanganui (in-tradition readers only).
**Pitfalls:** identification can succeed on texture alone, which is why the sheet codes verdict and mechanism. Use two coders. A rewritten formulation can still lead, which is why a second person checks each one.
**Tooling:** the runtime Step code in the sandbox project (`projects/current-tests/voice-pipeline-dryrun`), never athens-2026. The field-removal run proposed in `voices/REVIEW_2026_09_28_card_field_utility.md` §6.5 asks a different question (which fields matter) but uses the same sandbox and the same pinned model; the two can share one blind-reading session. `personas/phase_5_cross_persona_qc.py` measures voice-vs-voice distinctiveness at card level; it is a complement, and its paths are stale (roadmap 0.4).

### 5.2 The reader gates used as a validation instrument

**Protocol:** the reader sees:
1. the card's handling of the tradition;
2. the three Athens artifacts plus 2–3 Step-1 responses, with the formulations visible;
3. blind, a thin-card version on the same theme.

The reader answers three questions:
1. **Permission** (the existing gate).
2. **The provotype question:** is there a move the tradition or record supports but doesn't contain?
3. **Discrimination:** which is the configured voice, and which is better?

For Whanganui, question 2 becomes reporting fidelity, plus whether the "honest-extension" closes are acceptable.

**Two plans for C:**

| | **Best value** | **Best for quality** |
|---|---|---|
| **Readers** | one per voice, 2 in all | two per voice, 4 in all. For Whanganui one of them is a named body or role, which the draft publish rules already ask of a public voice (PRODUCT §11.2). |
| **What they read** | the protocol above: the card's handling, three artifacts, 2–3 Step-1 responses, and a blind thin-card version of each artifact | everything the voice produced at Athens: the card's handling, all three artifacts, every Step-1 response (Marley 14, Whanganui 9), the dossier passages that quote the voice, and blind thin-card versions on three themes, two samples each |
| **Form** | written answers to the three questions | written answers, then a conversation; a second pass after any card patch |
| **API cost** | **≈ $3** | **≈ $11** |
| **Reader time** | 3–4 h each | 6–8 h each, plus the second pass |
| **Elapsed** | open-ended, and overdue | the same; the second reader should not delay the first |

**Assumptions:**
- Unit prices as in §5.1.
- Value: a thin-card Step 1 and Step 2 for each of the three artifacts' themes, per voice, under the same Athens briefing: 2 × 3 × ($0.21 + $0.18) = $2.34.
- Quality: two samples of that (2 × 6 × $0.39 = $4.68), plus fresh full-card samples on the same themes so that both versions come from one run (2 × ($0.58 + 5 × $0.23 + $0.37 + 5 × $0.20) = $6.20). Together $10.88.
- The cost that matters here is the honorarium or koha. The record gives no figure; it is the operator's call.

**Candidates (corrected):**
- Whanganui: voices §28.
- Marley: a Rastafari-orbit candidate pool is named at `voices/HANDOFF.md:84`. The original memo said none was named.

**Status:** required before any Marley or Whanganui reuse (roadmap 1.3; decision point 4). No scheduling record in STATE, voices HANDOFF or runtime OPEN_ITEMS.

### 5.3 The expert blind panel: two plans

**Protocol (both plans).** Each expert reads Step-1 pairs on the same neutral question: the configured voice (Full-neutral) and its thin-card version (L2), unlabelled and in random order. For each pair the expert says which is the configured voice and which is more faithful to the figure. Those are the two halves of the PRODUCT §11.3 badge. The expert then answers FU#49G's provotype question on the voice's three Athens artifacts, with the formulations shown: is there a move the corpus supports but does not contain?

| | **Best value** | **Best for quality** |
|---|---|---|
| **Voices** | 3 with large scholarly pools: Plato, Arendt, and one of Dostoevsky, Lovelace or Cleopatra. Cleopatra has two of the five pieces that went beyond their question. | all 7 with a scholarly field: Plato, Cleopatra, Dostoevsky, Ibn Battuta, Arendt, Lovelace, Scheherazade. The Octopus goes to two cephalopod scientists, for fidelity to the science only. Marley and Whanganui belong to C. |
| **Experts per voice** | 2 | 3, so that each verdict has a majority |
| **Pairs per voice** | 10 | 12 (6 themes × 2 samples) |
| **API cost** | **≈ $14** (≈ $24 if same-voice calls run in parallel) | **$0** if the quality replay has run, because its outputs are the pairs. Otherwise ≈ $40 (≈ $66). |
| **Expert time** | 4–6 h each (≈ 22K words read and rated); 24–36 h in all | 5–7 h each (≈ 27K words); about 105–150 h in all, plus the Octopus readers |
| **Elapsed** | 4–8 weeks | several months: 21 experts to recruit |
| **What it shows** | whether experts can tell the configured voice at all, and whether any Athens move passes the provotype test | a result for every voice the hub would badge |

**Assumptions:**
- Unit prices and the warm-cache assumption as in §5.1.
- Value: per voice, 10 full-card calls ($0.58 + 9 × $0.23 = $2.65) and 10 thin-card calls ($2.10): $4.75, so $14.25 for three voices. The ten questions are any ten of the 18 selected Athens themes; under a neutral question a voice need not have been assigned the theme.
- Quality, if generated separately: per voice, 12 full-card calls ($3.11) and 12 thin-card calls ($2.52): $5.63, so $39.41 for seven voices.
- Honoraria are the real cost and the record gives no rate. The estimate is expert-hours times whatever the operator sets.

---

## 6. Designs

| | **0 — Seeding audit** | **A′ — Neutral-question replay** | **B — Expert blind panel** | **C — Reader gates as instrument** |
|---|---|---|---|---|
| **Tests** | Where the Athens verdicts came from | Convergence without leading questions; C1 at card level; C3 via the essayist | C1 + C2 | C2 + permission, for the sacred-grammar voices |
| **Scope** | The 30 artifacts against their formulations. First pass done here (§3 P4); a second coder re-codes blind. **0b (optional):** the same coding for all 125 Step-1 responses, each against its one formulation. It sizes the Provocateur fix and tests the withdrawn P5 (does Step 2's focus choice favour any class?). | Two plans (§5.1): 2 themes, or 6 themes with rewritten questions and Step 2 | Two plans (§5.3): 3 voices × 2 experts, or 7 voices × 3 experts | Marley, Whanganui. Two plans (§5.2): one reader per voice, or two with the full reading set |
| **API** | $0 | ≈ $24, or ≈ $190 | ≈ $14, or $0 to ≈ $40 | ≈ $3, or ≈ $11 |
| **People** | ~½ day; 0b ~2 days | about 2 days per coder in either plan | 24–36 expert-hours, or about 105–150 (4–6 h per expert per voice; corrected from 3 h) | 3–4 h per reader, or 6–8 h, plus relationship time |
| **Elapsed** | days | about a week, or 3–4 weeks | 4–8 weeks, or several months | open-ended, and overdue |
| **Placement** | **Now** | **Before the 2.1 field partition is frozen and before any validation badge.** Nothing else waits on it (corrected from "gate all of Stage 5"). | Parallel; calibrates the PRODUCT §11.3 thresholds | Parallel; already gating reuse |
| **Decision rule** | Report the S / O / N shares and the agreement between coders | §5.1 | §11.3 + the coding sheet + at least one expert-confirmed C2 move per voice | Reader verdict attached to the card (PRODUCT §5) |

---

## 7. Recommendation

1. **Design 0 now:** a second coder re-codes the 30 verdicts blind.
2. **File leading formulations as a Provocateur defect, independent of this decision.** The prompt already forbids them (`provocateur_formulation.md:21,28`), so another sentence in the prompt is unlikely to help. The fix is enforcement: a check on each formulation before it reaches a voice. For the main session to file; runtime thread.
3. **Run the best-value replay (≈ $24).** It gives the three contrasts, read against a noise floor, for about two days of reading per coder. Reading time is the limit here, not API cost. Move to the quality plan if the convergence result is unclear, or once a badge or a public claim is going to rest on the answer.
4. **B and C in parallel.** Both are needed anyway: B for the hub badge, C before any Marley or Whanganui reuse.
   - **B:** start with the best-value panel (three voices). Recruit the full panel only if the hub is going to show a badge on every voice.
   - **C:** start the best-value plan now, since it is overdue. Treat the quality plan's second reader, or named body, as required before any public reuse of Marley or Whanganui.

| Option | For | Against |
|---|---|---|
| 1. Proceed, treating the core as sound | Zero cost. Authenticity is disclaimed. The editorial output was strong. | P4 shows the Athens record cannot support Layer 2 as it stands: the verdicts were in the questions. Card loading and the badge would rest on unmeasured card effects. |
| **2. Staged (recommended)** | Design 0 is free and the best-value replay is about $24. Together they answer the one question the record leaves open. B and C are needed anyway. | Blind coding takes about two days per coder, and discipline. |
| 3. Full gate: the quality plans of A′, B and C before any Phase 2 | Strongest position | B and C calendars stall the build over a question A′ mostly frames |

---

## 8. Operator decisions

1. **Validation track yes or no**, and which of 0 / A′ / B / C.
2. **Placement of A′:** before the 2.1 field partition is frozen and before any badge (recommended), or fully parallel.
3. **Which plan for each paid test:** best value or best for quality, for A′ (§5.1), C (§5.2) and B (§5.3). The costs and assumptions are in each table.
4. **Coders** for 0 and A′: operator + Till, or an outside assistant.
5. **B:** which voices (three, or all seven); expert names; honoraria.
6. **C:** reader names and dates (decision point 4; unscheduled since May).
7. **(Reframed.) Leading formulations:** add a check to the Provocateur before the next run of any deployment. The original "credit the Provocateur" framing is withdrawn: formulations are already published, and the example phrase is the Whanganui voice's own `core_commitment`.

---

## 9. Method, sources, limits

**Offline scripts.** They are in this session's scratchpad, outside the repo, because the brief allows one file:
`/private/tmp/claude-504/-Users-aienvironment-Desktop-AI-Assembly-code--claude-worktrees-infallible-montalcini-e87b77/cebf313c-52b6-4072-8315-3b3ded6354ae/scratchpad/`
- `template_audit.py`: beat counts and shared idiolect.
- `trace_audit.py`: trace stance and card-field mentions.
- `formulation_overlap.py`: trigram, 6-gram and special-term overlap.
- `sixgram_provenance.py`: whether shared 6-word runs appear in the panel record.
- The card/corpus term counts were run inline and not saved.

The scratchpad is temporary. The main session should copy the scripts if Design 0 or A′ goes ahead.

The 30-verdict classification (§3 P4) is a manual read; the table is its record.

**What the overlap script missed.** It compared terms and word runs, not theses. "bounded-narrative-self" is a single token in both texts, so no n-gram caught it. Design 0 has to be done by reading.

**Limits:**
- single coder for the S / O / N classes, with four borderline calls;
- the audit compares each artifact with the formulation for its primary theme. Five artifacts synthesise across several responses (Dostoevsky N1, Scheherazade N1, Octopus N2 and N3, Cleopatra N3). For Cleopatra N3 all three formulations were read; for the other four, only the primary one;
- crude regexes for the beat counts;
- P3's analogues are my inference;
- dossier bodies read only through `EDITORIAL_ASSESSMENT.md`;
- Layer 3 not examined;
- 125 Step-1 files on disk against 128 formulations. Missing on N1: Whanganui theme_002, Cleopatra theme_004, Battuta theme_004; no claim depends on them.

**Cross-references:**
- voices §33, §24, §28, §11 (FU#49G), §31 Gap-H
- FU#30, FU#49, FU#55
- `runtime/flows/shared/prompts/provocateur_formulation.md:21,28,36–41,49`; `docs/AI_Assembly_Provocateur_Pipeline.md:335`
- `voices/REVIEW_2026_09_28_card_field_utility.md` §5.2, §6.5
- PRODUCT §5, §8.2, §11.3
- roadmap 1.2, 2.1, decision point 4; operator decisions, line 251 on `main` (no blanket spend cap; two plans per paid test)
- `EDITORIAL_ASSESSMENT.md`

---

## 10. Changes after the review (2026-09-29 and 2026-09-30)

### 10.1 Every change

1. **Header and evidence base** updated: revision dates, and the 30 formulations now listed as read.
2. **Bottom line** rewritten.
   - "The Athens data cannot tell these apart" becomes "mostly authored upstream (18 S / 7 O / 5 N)".
   - Claim 2(b), which rested on P5, removed.
   - "Co-authors each voice's angle" replaced by measured shares.
   - The unlabelled "(the base model's own default)" removed.
   - Recommendation re-ordered: free audit, Provocateur defect, small replay, then B and C.
3. **§1:** H0 now names the Provocateur as the source of most verdicts at Athens. Line citations added. `quality_criteria_results` noted on the fidelity pillar.
4. **New: thesis-level audit** of all 30 verdicts against the formulations they answered (§3 P4 table), with borderline calls marked and the question / proposition split reported. It replaces the original six-row seeding table.
5. **E-list re-scored** with verdict classes.
   - E4, E5 and E7 withdrawn: the Provocateur supplied them.
   - E3, E6 and E8 downgraded to "route, not verdict".
   - E1: "a generalist would reach for" removed; what the formulation seeded is now stated.
   - E4's claim that Ada revised "because a panelist persuaded it" removed.
   - Cleopatra N3 promoted (E10), worded after reading all three of her N3 formulations.
   - Whanganui's criticism of its own questions added to E10.
   - E12 added (Plato N2, Cleopatra N2).
6. **Lexical claim corrected:** the shared analytic register is reported, not only the low counts.
7. **P1 reinterpreted:** verdict classes added to the convergence table (10 of its 13 artifacts are S). The "apparatus instructs refusal" paragraph is replaced by the prompt's own targets in the P4 mechanism note.
8. **P2:** the FU#49H attribution was wrong (reverted in `3feb2b2`). The beats now trace to `translation_protocol`, FU#49C and FU#49D. Cleopatra-closing detail corrected.
9. **P3:** Ada's and the Octopus's coinages marked as asked for. Battuta N2's verdict was asked for by its formulation; "the verdict the model would give anyway" withdrawn. The Arendt analogue corrected to the moral crumple zone.
10. **P4 corrected:**
    - shared 6-word runs are the Provocateur's prose, not panel quotes (98 of 104; reproduced);
    - formulations are published (all 18 selected-theme files, all 13 dossier headnotes), so "a gap against make-the-construction-visible" is withdrawn;
    - "recognised, not granted" is Whanganui's `core_commitment`;
    - "one Opus call" corrected to one call per (theme, voice), with the shared inputs named from the prompt;
    - §31 Gap-H named as the nearest tracker item;
    - the defect is the prompt's and spec's own "contains its answer" rule.
11. **P4 addition:** Arendt N2 credits "the room" with a framing only the formulation used.
12. **P5 withdrawn:** a definitional challenge, not a case against democracy, and published in `data_views` since 2026-06-02.
13. **P6 details corrected:** "144" is absent on Whanganui N2; P.Bingen 45 is absent on Cleopatra N3.
14. **P7 and P8:** the review's count added to P7; P8 now says the scene was seeded.
15. **§4:** "undecidable" removed; the short-profile inference added; "what can be claimed today" added; the shape-versus-content point added; the Phase 2 note narrowed.
16. **§5.1 redesigned:**
    - the neutral question is defined from the code, and is now the condition for every primary arm;
    - the arms are renamed, and L1 (thin card under the Athens formulation) becomes optional;
    - the two themes are chosen so that all ten voices have an Athens answer to compare;
    - a one-theme first step added (replaced on 2026-09-30, §10.4);
    - the two-theme design costed at two samples per cell, with the arithmetic shown (replaced on 2026-09-30, §10.4);
    - the absolute 70% rule replaced by rules relative to the essayist and the re-roll floor, with the sample-size limit stated;
    - "no prompt changes" corrected;
    - the link to the card-field review's removal run added.
17. **§5.2:** the reader now sees the formulations, and the blind comparison uses the thin-card version. Marley candidate pool at `voices/HANDOFF.md:84`.
18. **§6:** Design 0 and 0b added. Design A renamed A′; it no longer gates all of Stage 5. B's pairs now use neutral questions. Expert time corrected to 4–6 h.
19. **§7:** the Provocateur check recommended regardless of the track; the smaller replay recommended first; options table updated.
20. **§8:** decision 7 reframed.
21. **§9:** full scratchpad path; the new script listed; the term-versus-thesis limit and the primary-theme limit stated.
22. **§10** added.

### 10.2 Answers to the review's five questions

1. **Did the overlap script flag the three seeded theses?** No. It compared non-ASCII terms, italic spans and word n-grams. Octopus N1 showed 0 shared 6-grams and 0 of 5 special terms. Ada N2 showed 4 shared 6-grams and, among special terms, only "Véliz". Cleopatra N1 showed 7 shared 6-grams and γινέσθωι, and I did not follow that up. I never checked the E-list against the formulations at thesis level.
2. **What share of verdicts was already in the formulations?** 18 of 30 stated or implied (60%); 7 offered as an option (23%); 5 beyond (17%). One coder, four borderline calls, worst case 19 / 8 / 3. It changes the bottom line, puts the free audit first and makes the neutral question the replay's primary condition.
3. **What supports the Plato reading?** Nothing sufficient. I read three sentences out of their argument. The trace declines to make Republic VIII the final word, and the text has been in `data_views` since 2026-06-02. No other case was found; the search was a keyword scan of three voices. P5 is withdrawn.
4. **Did you check the published theme files, the headnotes and `core_commitment`?** Not before writing. Checked now, and the review is right on all three. Decision 7 is reframed from "credit the Provocateur" to "stop leading formulations".
5. **Budget and scope of Design A.**
   - $32 was one sample per cell, against my own rule.
   - The 70% threshold had no basis; the rules are now relative.
   - Gating all of Stage 5 was over-scoped. Family of forms is an operator BUILD decision and works on form. A′ now precedes only the freeze of the 2.1 field partition and any badge.

### 10.3 Where I disagree with the review

1. **E1 stays as the lead candidate.** The review is right that its shape is P2's template beat. Its content is not seeded: "optional somebody" has no match in Arendt's card, her corpus or her N2 briefing, and the artifact rejects both horns the formulation offered.
2. **Gap-H is a neighbour, not the same finding.** It is about formulations asking voices for analytic work they don't natively do. Formulations that state the verdict are not in either tracker.
3. **The cost base.** The review's $49.5 doubles the original cells. Under a neutral question the Athens originals can't serve as the Full sample, and the essayist needn't be run per voice. The current plans and their costs are in §5.1.

### 10.4 Second revision, 2026-09-30: the spend cap was lifted; two plans per paid test

The operator lifted the USD 10 spend cap on 2026-09-30. Every paid test now comes as a best-for-quality plan and a best-value plan, and the operator picks per test (roadmap, operator decisions, line 251 on `main`). Changes:

1. **§5.1, two plans for A′.** The one-theme first step and the two-theme design are replaced by a best-value plan (2 themes, ≈ $24) and a best-for-quality plan (6 themes, ≈ $190), each with its arithmetic and assumptions.
2. **§5.1, two new arms.** Full-led is a fresh led sample, so that the question is the only difference from the neutral arm. The Athens originals are no longer used for that, because they also differ in continuity. Full-targeted (rewritten questions) is in the quality plan only.
3. **§5.1, cost basis.** The estimates now assume each voice's calls run one after another, so the card is written to the cache once. The cost if they run in parallel is given beside each total.
4. **§5.2, two plans for the reader gates** (≈ $3 and ≈ $11 of API). The earlier "~$5" is replaced by the arithmetic.
5. **§5.3 is new:** the expert panel's protocol and its two plans (≈ $14; and $0 to ≈ $40). Before, the panel had only a column in §6.
6. **§6, §7, §8 decision 3 and the bottom line** follow the new plans and costs. §7 now says which plan I recommend for each test.
7. **Cap framing removed:** §8 decision 3, the "against" cell of option 2 in §7, and change-log item 20.
8. **§10.1 items 16 and 19** point here, and §10.3 item 3 no longer quotes the replaced figures.
9. **§5.1 decision rules:** a question test and a rewritten-questions rule added; the card test now gives the readable gap for 60 cells as well as 20. "Can show" and "Pitfalls" updated to match.
10. **Smaller edits:** the header and the §9 roadmap cross-reference; §8 decision 5 now covers both panel sizes; the cost of the card-field review's removal run is no longer quoted in §5.1 (that document gives its own figure).

Nothing else changed.
