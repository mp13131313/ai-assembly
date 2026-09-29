# Review of `_workspace/planning/voices/MEMO_2026_09_28_validation_track.md`

## Verdict
1. **Quality:** the memo is well built and even-handed in framing. Its quotes, card and corpus counts, the validator tally and the cost arithmetic check out (30 of 57 claims verified). The shape of the validation designs is right.
2. **How far to trust it:** trust its quotes, counts, pricing and the core P4 mechanism (the Provocateur sets the angle). Do not trust the evidence-for list as classified, P5's reading of Plato, or decision 7's example. Correct these before the operator decides.
3. **Biggest issue:** it did not apply its own P4 check to its own evidence.
   - Three of the eleven "real perspective" moves were supplied by the Provocateur's formulation: E4 (Ada's "third operation"), E5 (Cleopatra's sealed act) and E7 (the Octopus's "bounded-narrative-self").
   - Most of P1's "shared verdicts" are already stated in the formulations for each voice.
   - So the convergence is largely authored upstream, not "undecidable". A seeding audit costing nothing should come before Design A.

## Findings, one by one
How I checked:
- Read all 30 Step-2 artifacts in full (the published `nights/*` text is byte-identical to `runs/*/04_voice/step2_first_draft_artifacts`).
- Read about 30 formulations, the Plato N1 theme_005 Step-1 record and its trace, cards, `council_config.json`, the published theme and dossier JSON, and the trackers.
- Wrote term-count and n-gram scripts in my scratchpad (`rr/work10/`). No API calls.

| ID | Claim (short) | Verdict | Evidence / reason |
|---|---|---|---|
| BL1a | Voices differ in how they argue, not in what they conclude; no voice reached a conclusion a contemporary critic would reject | VERIFIED | Full read of the 30 artifacts agrees. "(the base model's own default)" is an unlabelled inference. |
| BL1b | "The Athens data cannot tell these apart" (triangulation vs one model in costumes) | DOUBTFUL | The focus formulations already state the verdicts, so the record puts the convergence upstream (see P1c). |
| BL2a | The Provocateur co-authors the angle | VERIFIED | Confirmed, and understated (see E4, E5, E7, P1c). |
| BL2b | Step 1 holds non-default positions that Step 2 dropped | DOUBTFUL | Rests on P5, which mischaracterises its only case. The bottom line generalises beyond P5's own "single case" label. |
| §1a | Briefing quotes ("no authentic version"; "well-read human essayist") | VERIFIED | `docs/AI_Assembly_Briefing_v3_1.md:25,51`. |
| §1b | FU#49G "provotype test", filed 2026-04-27, never closed | VERIFIED | voices OPEN_ITEMS §11, lines 345–349. |
| §1c | PRODUCT §11.3 "distinct-but-wrong" | VERIFIED | `PRODUCT_assembly_hub.md:181`. |
| §1d | voice_fidelity pillar: 10 PASS / 20 WARN; scores characteristic moves | VERIFIED | Tallied all 30 `step2_validation/*.json`. The pillar also carries `quality_criteria_results`. |
| §1e | Card is 38–44K tokens | PLAUSIBLE | Step-1 cached prefix: median 43K, range 37–51K. |
| E1 | Arendt N2 "optional somebody": 0 card / 0 corpus | VERIFIED | Quotes and counts reproduced; 0 in formulations too. **Caveat:** the formulation supplied "moral crumple zone" and "the human can shrug and say the machine did it" (the disowning half). "A generalist would reach for" is an unlabelled inference. |
| E2 | Dostoevsky N1 nadryv counter-prediction | VERIFIED | nadryv: 13 hits + 9 Cyrillic. The empty chair was seeded; the prediction is not in the formulation. |
| E3 | Ada N1 operation-card / number-card | VERIFIED | Counts 7 / 3. **Caveat:** the formulation offered the "originating into forming" frontier the artifact lands on. |
| E4 | Ada N2 is "the clearest case of a voice revising because a panelist persuaded it" | **WRONG** | N2 `theme_008__ada_lovelace` asks for "something that is neither execution nor origination… how would your Notes name and bound that third operation?", using the word "constitutive". "A self-discovered slip is gain" is the card's `disagreement_protocol`. The move is the Provocateur's request, executed with a disposition the card scripts. |
| E5 | Cleopatra N1 "closest to a non-liberal position" | **WRONG** (as evidence) | This is the Provocateur's own proposition (N1 `theme_007__cleopatra`, mode=proposition): "conversation around a common table is too thin a substitute for the sealed act". The artifact lifts "both quarrel inside a category mistake", "one body of many tongues" and "obliges in public". Only "garland" is new (0 in card ✓). hostile:true ✓ (voices §1 table). |
| E6 | Marley N2 capture sequence not in the formulation; card has no "speaker-tag" | VERIFIED | **Caveat:** the speaker-tag mechanism came from the panel (the Step-1 text says "the brother explained… the tags drop out"). The formulation supplied the old-captivity-or-new binary. |
| E7 | Octopus N1: "the coinage is new" | **WRONG** | N1 `theme_001__octopus` asks: "or at the bounded-narrative-self boundary". It also lists Sumbre, who is not cited in N1, and omits Crook 2021. |
| E8 | Battuta N1 wijāda / tazkiyya 0/0 | VERIFIED | **Caveat:** the proposition supplied wakīl, ijāza, ʿadāla and the envoy, and invited a licence ("if you would license such an agent…"). |
| E9 | Scheherazade's tales are new | VERIFIED | Wāsiṭ 0/0; "three old men" 8 card hits. |
| E10 | Refusals in character | VERIFIED | Whanganui N2's silence was offered by its formulation ("or… the honest answer is silence?"). Cleopatra N3 withheld the seal against three "Defend or refute" propositions pushing for it. That is strong evidence for the real-perspective reading, and the memo underuses it. |
| E11 | Tic self-monitoring in the form notes | VERIFIED | In the `selected_form` fields. |
| Lex | "ledger" 2 voices, "load-bearing" 2, "grammar" 3 | VERIFIED | Reproduced. The three-word sample flatters: "register" appears in 7 voices, "architecture" 4, "substrate" 3, "costume" 3. |
| P1a | Convergence table (themes, voices, routes) | VERIFIED | Focus themes match `focus_decision` and lineage. |
| P1b | No voice sided with the room against the critic | VERIFIED | Full read. |
| P1c | Confound: the apparatus instructs refusal | PLAUSIBLE, **understated** | The focus formulations state the shared verdicts:<br>- Battuta N1 (proposition)<br>- Arendt N1 ("the unit at risk…", lifted verbatim)<br>- Plato N3 ("the turning performed for us…")<br>- Scheherazade N3 ("the tale arriving before the teller")<br>- Marley N3 ("speaking about the sufferah, not from him")<br>- Dostoevsky N2 and N3<br>The formulation prompt's third target is "AUDIENCE FRICTION" (`provocateur_formulation.md` §THREE TARGETS). |
| P1d | Briefing's variance risk; closing-show mapping never built | VERIFIED | Briefing:317; STATE:300 ("B5 closing-show pipelines", not built). |
| P2a | Regex beat counts | PLAUSIBLE | The scripts were not preserved and cannot be reproduced. |
| P2b | Plato N2 / Cleopatra N2 are one move in two registers | VERIFIED (minor overstatement) | Cleopatra does not *close* on the audience member. Both theme_007 formulations invite the concession. |
| P2c | Beats "installed by the build: FU#49H" | **WRONG** | FU#49H was reverted in `3feb2b2` (2026-04-28); it is "NOT in current prompts" (voices OPEN_ITEMS:239–241). FU#49D was re-applied ✓. The beat more likely comes from `translation_protocol` ("name the gap") and the FU#49C directive in conference_facts. |
| P3a | New moves are contemporary concepts in costume | PLAUSIBLE | Labelled as inference. The Arendt analogue only paraphrases the artifact; the closer analogue, "moral crumple zone", was in the formulation. |
| P3b | Battuta N2 ẓālim is "the verdict the model would give anyway" | DOUBTFUL | The N2 `theme_008` formulation demanded it: "what is the verdict on a host-king…". The artifact says "I am asked, and I will give one". |
| P4a | Six seeding rows (Dostoevsky, Battuta, Whanganui, Cleopatra, Arendt, Marley) | VERIFIED | All quotes found verbatim. "Rule by Nobody" is absent from the N2 transcripts and extractions, so Arendt's credit to "the room" is misattribution. |
| P4b | Seeding "not found in either tracker" | DOUBTFUL | voices §31 Gap-H: "Pipeline pressure: formulation calls for analytic answer". The memo cites Gap-H in P3. |
| P4c | 17 artifacts share a 6-word run with their formulations | VERIFIED | Reproduced: 17. |
| P4d | Median content-trigram share is 1.5% | PLAUSIBLE | My replica gives 0.6% (tokenisation-dependent). Same order. |
| P4e | The shared runs are "mostly panel quotes" | **WRONG** | 98 of 104 shared 6-grams appear in neither the transcripts nor the extractions. They are the Provocateur's own phrasing. |
| P4f | Published dossiers credit the voices with Provocateur moves, a gap against "make the construction visible" | **WRONG** | The formulations are published verbatim: `published_artifacts/themes/night_N/theme_*.json` (`formulations_per_voice.formulation_text`) and dossier `headnotes[].formulation_text`. "Recognised, not granted" is the Whanganui voice's own `core_commitment` in `council_config.json` and is in the card. The real defect: many formulations break the spec's "Leading — contains its own answer" failure mode (`docs/AI_Assembly_Provocateur_Pipeline.md:335`; prompt lines 21, 28). |
| P5a | Plato N1 theme_005 Step-1 quotes; absent from all three Plato artifacts | VERIFIED | All three quotes are in `plato__theme_005.json`. |
| P5b | This is Plato's "case against democracy", which "never reached print" | DOUBTFUL | The response is a ti-esti (Euthyphro) definitional challenge:<br>- Its Republic VIII paragraph *agrees* with a speaker ("He spoke truly").<br>- "do you give that politeia the name democracy? I think you do not" is about naming the kallipolis, lifted from the definitional argument.<br>- The trace says "I won't use my Republic VIII account as a final word".<br>- The text and trace have been in `published_artifacts/data_views/` since 2026-06-04 (`40f1da5`). |
| P6a | Fixed repertoire; card hits 39 / 25 / 25 | VERIFIED | Tongariro 39, "144" 25, Hikuroa 25. |
| P6b | "144 years" and P.Bingen 45 appear every night | **WRONG** (detail) | Whanganui N2 has no "144"; Cleopatra N3 has no "P.Bingen 45". |
| P7 | 117 of 125 traces in planner stance; "banned_language" is the field most named | PLAUSIBLE | 5 empty traces (consistent). My flexible count: 45 traces mention "banned …". The direction matches; the numbers were not reproduced. |
| P8 | Arendt N1 states H0 about itself | VERIFIED | Quote found. The scene was set up by N1 `theme_004__hannah_arendt`. |
| §4 | Best C2 candidates are refusals of stock mappings (E1–E3) | PLAUSIBLE | Labelled. But "refuse the binary, coin a third" is exactly P2's beat 2 (see Problems). |
| §5.1a | Pricing $5/$25, cache writes 2× (1h), reads 0.1×; full Step 1 $0.45–0.60, Step 2 $0.28–0.38; $72 total | VERIFIED | `Voice_Pipeline.md:342,1266,1280`. My per-call medians: Step 1 $0.54, Step 2 $0.37. |
| §5.1b | Thin-card Step 1 ≈ $0.21 (8.4K in / 6.6K out); Step 2 ≈ $0.18 | VERIFIED | Athens medians 8,380 / 6,583 give $0.207. Step-2 thin median $0.181. |
| §5.1c | Binomial p ≈ 0.055 (8/10), 0.011 (9/10) | VERIFIED | 56/1024 and 11/1024. |
| §5.1d | Runtime can run the thin card in the sandbox | PLAUSIBLE | `card_assembly.py:285–299` skips missing fields. L2 and G0 need variant user prompts, so "no prompt changes" is slightly overstated. |
| §5.1e | `phase_5_cross_persona_qc.py` paths are stale | VERIFIED | Roadmap:89. The file exists. |
| §5.2a | For Marley "no candidates are named" | DOUBTFUL | Right for §24, but `voices/HANDOFF.md:84` names a Rastafari-orbit candidate pool. |
| §5.2b | No reader-gate scheduling record | VERIFIED | No dates in STATE, voices HANDOFF or runtime OPEN_ITEMS. |
| §6a | A costs ≈ $32 (80 Step-1 + 40 Step-2 calls) | VERIFIED (arithmetic) | 20×0.54 + 60×0.20 + 10×0.37 + 30×0.18 ≈ $32. |
| §6b | Cap of $50 | DOUBTFUL | $32 means one sample per L1/L2/G0 cell, against the memo's own pitfall ("≥2 samples per condition"). Complying costs about $49.5, leaving no headroom under the cap. |
| §6c | A's decision rule: L1 matches Full in ≥70% of pairs | DOUBTFUL | The threshold is absolute. It ignores the Full-vs-Full re-roll agreement the design pays to measure. |
| §6d | B needs about 3 h per expert (≈26K words) | DOUBTFUL | That is about 145 words a minute *including* the ratings. Step-1 median is 1,106 words × 20 texts. 4–6 h is more realistic. |
| §6e | B costs ≈ $8 per voice; C ≈ $5 | PLAUSIBLE | Arithmetic is consistent. |
| §6f / §7 | A gates Stage 5 | DOUBTFUL (scope) | The memo's own §4 and decision rule bear only on split-card (2.1), not family of forms. Family of forms is already an operator BUILD decision (roadmap 1.2, 2026-06-13), which the memo does not mention. |
| §8.3 | "Stage 4's cap is still unset" | **STALE** | USD 10 set 2026-09-28 (roadmap:251; CONTEXT). |
| §9 | 125 Step-1 files vs 128 formulations | VERIFIED | The N1 files missing a Step 1 are Whanganui theme_002, Cleopatra theme_004 and Battuta theme_004. DATA_INVENTORY also claims 46 N1 reasoning notes; only 43 are on disk. |

**Counts:** VERIFIED 30 · PLAUSIBLE 9 · DOUBTFUL 10 · STALE 1 · WRONG 7 (57 rows).

## Problems with the document
- **The seeding check is applied unevenly.**
  - P4 checks six artifacts against their formulations, but the evidence-for rows were never checked. E4, E5 and E7 are Provocateur theses; E1, E3, E6, E8 and E10 are partly seeded.
  - P1 and P4 are presented as independent evidence. Yet P1's convergence is largely P4: one Opus call writes each voice's angle with the verdict built in, and the voices mostly accept it.
- **The two sides contradict each other.** §4's best C2 candidates (E1–E3) are instances of P2's template beat 2: reject the framing and split it into two.
- **Overreach.**
  - Bottom line 2(b) generalises P5 ("positions") beyond P5's own "single case" label.
  - The bottom line says the Provocateur co-authors "each voice's angle"; P4 says "often".
  - Decision 7 rests on a misattribution: the phrase is the Whanganui voice's own `core_commitment`.
- **Inferences stated as fact.**
  - "(the base model's own default)"
  - E1: "a generalist would reach for"
  - E4: the causal claim "because a panelist persuaded it"
- **Evidence it didn't check, though the data was on disk.**
  - The published theme and dossier files, which carry the formulation text.
  - The `data_views` files, which carry the Step-1 text.
  - The council_config profiles.
  - The dossiers were read only through `EDITORIAL_ASSESSMENT` (its §9 admits this), yet P4 makes claims about them.
- **Wrong citation.** FU#49H was reverted before most Athens builds.
- **Missed, and decision-relevant.**
  - The formulations break the Provocateur spec's "Leading" failure mode. That points to a cheap fix (a check on formulations, or prompt enforcement) regardless of the validation-track decision.
  - The formulation prompt's AUDIENCE FRICTION target is a concrete cause of uniformly critical direction.
  - The strongest counter-seeding case, Cleopatra N3 withholding the seal against three propositions, is underused.
- **Reproducibility.** Scripts A–D were kept in a session scratchpad and not preserved, so the P2 and P7 counts cannot be reproduced. My replica of script C matches on the 17-artifact count but not on the median.
- **Rules.** No evidence of a breach: the athens-2026 working tree is clean, the memo says no model calls were made, and the deliverable is at the briefed path (committed in `0910a66`). It stayed within the brief. It names only programme speakers and Till (already named in voices §24).

## Questions for the originating session
1. **Did script C's "prefigured special terms" flag "bounded-narrative" (Octopus N1), "third operation" / "constitutive" (Ada N2) and the sealed-act proposition (Cleopatra N1)?**
   - Why it matters: this decides whether the E-list must be re-scored and whether script C can serve as the P4 audit.
   - What would change: if the script missed these, the audit design needs thesis-level checks, not term checks.
2. **Across the 30 artifacts, what share of final verdicts were already stated or strongly implied by the focus formulation?**
   - Why it matters: if the share is high, Bottom line 1 changes from "undecidable" to "authored upstream". The seeding audit, which costs nothing, then runs before any API spend, and L2 (no formulation) becomes Design A's primary condition.
3. **What supports reading Plato's theme_005 Step 1 as a "case against democracy"?** Its trace declines to make Republic VIII the final word, and the text has been in `data_views` since June. Was any other Step-1 record found with a genuinely non-default position that Step 2 dropped?
   - Why it matters: P5 is one of the two reasons (with P4) given for choosing option 2 over option 1.
4. **Did you check the published `themes/*/theme_*.json` and dossier `headnotes` (which carry `formulation_text`), and Whanganui's `core_commitment`?**
   - What would change: if the construction is already visible, decision 7 should be reframed from "credit the Provocateur" to "stop leading formulations".
5. **Design A budget and scope.** Is $32 meant with one sample per L1/L2/G0 cell? Should the ≥70% rule be relative to Full-vs-Full re-roll agreement? Why gate all of Stage 5, when the decision rule only bears on split-card and family of forms is already approved?
   - Why it matters: this sets the cap and what the gate actually blocks.

## Operator decisions it asks for
1. **Validation track yes or no, and which designs.** Recommends yes, staged: A as a gate, with B and C in parallel. Stage 4 is not held.
2. **Placement of A.** Recommends a gate before Stage 5; the alternative is running it in parallel.
3. **Spend cap for A.** Recommends $50. Its note that Stage 4's cap is unset is stale: USD 10 was set on 2026-09-28.
4. **Who codes A blind.** Operator + Till, or an outside assistant. No firm recommendation; it notes the outside assistant is less biased but costs money.
5. **Design B.** Which 3 voices (suggests Plato, Arendt, and Dostoevsky or Lovelace), expert names and honoraria. No amounts given.
6. **Design C.** Reader names and dates (existing decision point 4). Implied recommendation: schedule now, it's overdue.
7. **Construction visibility.** Whether to credit the Provocateur where a formulation supplied a voice's image or thesis. Implied recommendation: yes. The review finds the premise weak: formulations are already published, and the example phrase is card-originated.
