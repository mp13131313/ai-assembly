# MEMO — Validation track: genuine perspective or elaborate ventriloquism? (voices §33)

**Date:** 2026-09-28 · **For:** the operator's open decision from June (voices `OPEN_ITEMS.md` §33; roadmap Stage 3, "validation-track decision") · **Written by:** a Fable 5.1 session, Task 4 of `_workspace/planning/BRIEF_2026_09_28_fable_batch2.md`
**Status:** decision memo. Nothing here is decided. Claims are labelled **CONFIRMED** (seen in data or code) or **PLAUSIBLE**; interpretations are marked *inference*.
**Evidence base:** the Athens record in `projects/athens-2026/` (read-only). All 30 Step-2 artifacts read in full; a sample of the 125 Step-1 records and Provocateur formulations read in full; four offline scripts run over all of them (§9). No model was called.

---

## Bottom line

1. **The voices are clearly different in how they argue, and barely different in what they conclude.** Form, vocabulary and argumentative mechanism are voice-specific. But on each theme, voices from unrelated traditions reach the same verdict, and no voice on any night reached a conclusion that a thoughtful contemporary critic (the base model's own default) would reject. The editorial assessment calls this convergence the edition's signature. For §33 it is the main unresolved signal: convergence is what independent frameworks triangulating would look like, and also what one model's view in ten costumes would look like. The Athens data cannot tell these apart.
2. **Two things the June framing didn't have.** (a) **The Provocateur co-authors each voice's angle.** Its per-voice formulations often name the apparatus the voice then uses and sometimes state the thesis (Dostoevsky N1's empty Inquisitor chair, Battuta N3's three buckets, Whanganui N1's "recognised, not granted"). So Athens output cannot credit a move to the card without a replay. (b) **Step 1 holds historically non-default positions that the published Step 2 dropped.** For example, Plato's Republic-VIII case against democracy, argued privately on Night 1, never reached print.
3. **Recommendation: adopt a staged validation track.**
   - **Design A**, a replay ablation against a thin-card generalist: ~$30–40 API and 2–3 operator days. It should **gate Stage 5**, not Stage 4.
   - **Designs B and C**, an expert blind panel on 3 voices and the reader gates used as validation instruments: run as a **parallel track**. They feed the PRODUCT §11.3 badge and are prerequisites for any Marley or Whanganui reuse.
   - Don't hold Stage 4 for any of it.

---

## 1. The question, made testable

The Briefing rules out the naive version: *"There is no authentic version waiting to be discovered. The construction is the representation."* (`docs/AI_Assembly_Briefing_v3_1.md` §"The first condition"). So "genuine perspective" cannot mean "really Plato". It has to mean one or more of three claims the project does make:

| # | Claim | Where the project makes it | What would test it |
|---|---|---|---|
| **C1 Differential** | The configured apparatus (profile → formulation → 38–44K-token card → Steps 1–2) produces reasoning that a competent generalist, handed the same brief, does not. | voices §33 point 2 | Blind A/B against a generalist |
| **C2 Framework extension** | The voice makes moves its corpus does not contain but its framework plausibly supports. This is the "provotype test, NOT pastiche test". | FU#49G (voices §11, filed 2026-04-27, never closed) | Domain reader |
| **C3 Generativity** | The output says something the room could not have said: *"If the content could have come from a well-read human essayist, the provotype has reduced to an art project."* | Briefing Layer 2 + "Generative, not derivative" | A no-persona essayist baseline, plus the night's extractions |

**The pastiche hypothesis (H0):** conclusions and argumentative skeleton come from the base model, and partly from the Provocateur. The card contributes vocabulary, citations and form. Under H0 an expert could still tell the voice from a generalist by texture. So identification alone cannot reject H0. PRODUCT §11.3 half-anticipates this ("distinct-but-wrong is also distinguishable").

**What already exists is not validation.** §33 lists the reader gates (a permission check), the 9-test rubrics (a regression check) and FU#30 (narrow). One more belongs on that list. The production Step-2 `voice_fidelity` pillar scores `characteristic_moves_performed`: whether the artifact performed the card's signature moves. It rewards the costume by construction. Its Athens result (10 PASS / 20 WARN across the 30 voice-nights; CONFIRMED, `runs/athens_night_*/04_voice/step2_validation/*.json`) says nothing either way about C1–C3.

---

## 2. Evidence for a real perspective

Each row gives the move, whether it was seeded (in the card, the corpus or the formulation) or new, and the source. "Card/corpus hits" come from a term count over `voices/<slug>/07_persona_card_assembled.json` and `03_corpus/` (script D, §9).

| id | Move | Seeded vs new | Why it counts |
|---|---|---|---|
| **E1** Arendt N2 (`runs/athens_night_2/04_voice/step2_first_draft_artifacts/hannah_arendt.json`) | The formulation offered a binary: *"a new Nobody, or only the old Nobody given a fluent voice"* (`03_provocateur/formulations/theme_001__hannah_arendt.json`). The voice refused both horns and coined a third concept: *"There is no new Nobody. There is what I will call… optional somebody… Optional answerability looks from a distance like answerability and is in fact its inversion."* | "rule by Nobody" is in the card (5 hits) and the formulation. The 1964 *Personal Responsibility* move is in the card. **"optional somebody": 0 card / 0 corpus** (CONFIRMED). | It refuses the stock mapping, one that both the Provocateur and a generalist would reach for, and builds a different concept from the same corpus. This is the best C2 candidate in the record. |
| **E2** Dostoevsky N1 | *"the population fed on the flattering answer will not become flat. It will become a vast theatre of nadryv."* The room predicted flattening; the voice predicts the opposite. | *nadryv* is in the card (13 + 9 Cyrillic). The empty-chair image was **seeded** by the formulation (§3 P4). The prediction itself is new. | A falsifiable counter-prediction derived from the voice's own psychology, not a restatement of the room. |
| **E3** Ada N1 | *"Personalisation at the level of numbers, with operations supplied from a single source, is not pluralism."* | The operation-card / number-card taxonomy is in the card ("operation-card" 7, "number-card" 3). Its application to personal AI is new. | The framework's own distinction does the argumentative work. It is sharper than the generic line "personalisation isn't pluralism". |
| **E4** Ada N2 | The voice is persuaded by a panelist and revises its own published frontier: *"a self-discovered slip is gain, not embarrassment."* | "constitutive coupling": 0 / 0. | The clearest case in 30 artifacts of a voice revising its own position because a panelist persuaded it. Plato N2 and Cleopatra N2 concede the critic's diagnosis of their traditions but keep their positions. |
| **E5** Cleopatra N1 | *"you have asked a garland to hold up a temple… Conversation will cohere the circle that comes. It will not bind the chōra."* | "garland": 0 in the card. The seal / γινέσθωι apparatus is card staple (30 hits). | The closest any voice came to a position outside the liberal-deliberative default: binding by sealed rite, not by conversation. Cleopatra is the only voice built with `hostile: true` (voices §1). |
| **E6** Marley N2 | The capture sequence: the schoolmaster captured the second person (*you must learn this*), the press the third (*they say this is so*), the new instrument the first (*I, I think this*) — *"You cannot chant down what the sufferer believe is her own thought."* | Not in the formulation. The card has no "speaker-tag". | A structural argument built on the I-and-I grammar the card permits, not a vocabulary swap. |
| **E7** Octopus N1 | Moves the room's line: the criteria *"do not draw a line at human-against-machine. They draw a line at bounded-narrative-self."* | Every citation is in the card (Poncet, Wang & Ragsdale, Zullo, Sumbre). The coinage is new. | A non-human vantage used to criticise the room's humanism. This is Layer 2 in intent. |
| **E8** Battuta N1 | A graded licence instead of a verdict: *"As wijāda the artifact is licit. As teacher… no."* | ***wijāda*: 0 / 0**; *tazkiyya*: 0 / 0. | The voice reached past the card into the transmission-grading system its framework implies. |
| **E9** Scheherazade N1–N3 | A new tale every night: the qāḍī of Wāsiṭ, Hind in the tower, Zayd of Basra. | Frame, dawn-cut and the three old men are in the card. The tales are new (Wāsiṭ 0 / 0). | Invention inside the form rather than recital. |
| **E10** Refusals in character | Whanganui N2: *"I am a research artefact assembled from published material. I have no whakapapa."* The voice declines to adjudicate. Octopus N2 refuses *"the advocacy verb"*. Cleopatra N3 withholds the seal (*"To press γινέσθωι onto a body that has not yet been constituted is to seal air"*). Arendt N1 declines to issue an injunction: *"I will not deliver one I have not earned."* | These are card-shaped (the witness stance, voices §28). | Each voice refuses in its own grammar. None refuses by generic hedging. |
| **E11** Tic self-monitoring | Octopus N2's form note: *"deliberately not arm-by-arm, since night N-1 deployed that structure and re-using it would calcify it into tic."* Dostoevsky N3: *"no swerve-via-childhood-memory and no cold-cup break (both used on prior nights)."* | Continuity-driven. | The voices vary their own forms across nights instead of repeating their most famous one. |

**Lexical differentiation holds (CONFIRMED, script A).** Shared idiolect across voices is thin. "ledger" and "load-bearing" each occur in 2 voices, and "grammar" in 3. At word level, interchangeable phrasing is rare.

---

## 3. Evidence for competent pastiche

**P1 — Same verdict, different routes (CONFIRMED from reading; the interpretation is *inference*).** On each shared case, voices from unrelated traditions converge:

| Night / case | Voices | Shared verdict | Distinct routes |
|---|---|---|---|
| N1, personal AI for every citizen (theme_002) | Ada, Plato, Battuta, Arendt | Personalisation is not sovereignty; the formation comes from an unseen source. | operation-cards · *eidōlon* of dialectic ("rule become invisible") · no *tawkīl* / *tazkiyya* · the inner objector foreclosed |
| N2, speaker tags lost when the model compacts a conversation | Marley, Arendt, Dostoevsky | The machine captures the first person. | pronoun-capture sequence · "the seam… is being dissolved by a mechanism" · confession without a face |
| N3, the child who learned he was depressed from a chatbot | Arendt, Battuta, Plato, Scheherazade | A name was given without the labour or chain that makes it one's own, and no hand answers for it. | the second speaker pre-empted · father's *wilāya* displaced · right opinion untethered · a writ with no teller |
| N3, the "rest on behalf of those in survival mode" speaker | Marley, Dostoevsky | The absent sufferer is instrumentalised. | "the sufferah become the alibi" · love in dreams vs love in action |

No voice, on any night, sided with the room *against* the default critical position: none endorsed the hive mind, AI personhood or the personal-AI tutor. There are partial licences (E4, E8, Ada N3's *"I would be the last to refuse Mr Johar his table"*), but none reverses the verdict. The Briefing named this exact risk as an open uncertainty: *"Whether the detailed responses produce enough variance across the matrices per theme. If everything clusters in one quadrant, the reveal lands flat."* The closing-show matrix mapping that would have measured it was never built (STATE, "B5 closing-show pipelines"). `EDITORIAL_ASSESSMENT.md` reads the same convergence as the edition's strength. Both readings fit the data.

**Confound (inference):** the apparatus instructs refusal. `conference_facts.json` carries the "performing reception without being changed" failure mode and the framework-strain directive (voices §11, FU#49C), and the Provocateur selects for fault lines. Uniform direction may be the instruction rather than the model's opinion. Only a generalist given the same instruction separates the two (Design A).

**P2 — One argumentative skeleton across voices (the beat counts are CONFIRMED but crude; the reading is *inference*).** Most artifacts run the same sequence:

1. restate a room claim;
2. reject its framing, by splitting it in two, exposing a shared premise, or calling it a category mistake;
3. apply the voice's apparatus;
4. state the framework's limit;
5. reformulate the question, or leave it open.

Script A's regex counts over the 30 artifacts:
- names the room: 18/30 (all 10 voices);
- refusal vocabulary: 20/30 (9 voices);
- explicit limit statement: 12/30 (9 voices);
- split-into-two: 11/30 (7 voices);
- shared-hidden-premise wording: 11/30 (5 voices).

The clearest pair is Plato N2 and Cleopatra N2, on the same panel. Both:
- concede the critic's "underbelly" (Plato: *"That, Glaucon, I do not know how to defend without flinching"*; Cleopatra: *"The Canidius grant was war finance dressed as patronage"*);
- split the question in two ("two darks" / "two bodies");
- assign aporia to one half and action to the other;
- close on the same audience member, the one who waited 45 minutes with her hand raised.

That is one move in two registers. Some of these beats are **installed by the build**: the universal patterns FU#49H (mark structural aporia, name the extension) and FU#49D (corpus self-criticism permitted) show up as cross-voice beats. The N2 self-critiques (Plato, Cleopatra, and Marley N1 on Leviticus in the yard) are the pipeline's conscience rendered in each voice's idiom.

**P3 — The new moves are mostly contemporary concepts in costume (*inference*: my identification, not an expert's).**
- Ada's "constitutive coupling" ≈ reflexivity, looping effects or performativity.
- Octopus's "bounded-narrative-self" ≈ the episodic-vs-narrative-self distinction in contemporary philosophy of mind.
- Marley's "alibi" ≈ the critique of speaking for others.
- Dostoevsky's "theatre of nadryv" ≈ the return of the repressed.
- Arendt's "optional somebody" ≈ selective attribution: credit when the output flatters, the machine to blame when it embarrasses.

This is what the cards ask for: `translation_protocol` is a method for re-expressing modern matters in the voice's terms (FU#12 / FU#49H). The open question is not *whether* the voices translate contemporary concepts, but whether the translation **reshapes** the concept (E1, E2 and E3 look like it) or **relabels** it (Ada N2 and Battuta N2 look like it). Battuta N2 is a production instance of voices §31 Gap-H ("fatwa in Rihla clothing"). The voice rules *ẓālim* on migrant detention and says why it departs from the historical figure's reticence: *"Where Tughluq's atrocities I recorded flat… that constraint does not bind me here."* It is a corpus-aware licence for the verdict the model would give anyway.

**P4 — The Provocateur co-authors the angle (CONFIRMED; not found in either tracker or the roadmap, searched "formulation" with seed/author/supplies/pre-shape).** Formulations are written per voice, in the voice's register, by an Opus call that reads the voice's provocateur profile. They often hand over the image, the apparatus or the thesis:

| Artifact | What the formulation supplied | What the voice added |
|---|---|---|
| Dostoevsky N1 | *"Your Inquisitor at least sat in his chair… a Grand Inquisitor with no one inside it for Christ to kiss?"*, and the "Petersburg staircase" (`athens_night_1/03_provocateur/formulations/theme_001__fyodor_dostoevsky.json`). The artifact's central image, partly verbatim. | The nadryv prediction (E2) and the Liza turn |
| Battuta N3 | The three buckets, the missing *isnād*, and the *ḍiyāfa* measure, as the question's own structure (`athens_night_3/.../theme_001__ibn_battuta.json`) | Execution; the father's *wilāya*; "the wound runs to no hand" |
| Whanganui N1 | *"Te Awa Tupua was not granted; it was recognised… after 144 years… what does it nonetheless get right…"* (`athens_night_1/.../theme_004__whanganui_river.json`). The thesis and the concession structure. `EDITORIAL_ASSESSMENT.md` credits "recognised, not granted" to the voice. | Procedural dates and citations (all card staples) |
| Cleopatra N2 | *"on terms the deliberators will not have chosen"*, verbatim in the artifact, plus the defend-or-concede binary | The split into two bodies |
| Arendt N2 | The rule-by-Nobody framing. The artifact attributes this reach to "the room". | The "optional somebody" concept (E1) |
| Marley N2 / N3 | *"the songs of the seventies could not have anticipated"*; *"speaking about the sufferah, not from him"* | The pronoun sequence (E6); "alibi" |

The voices do not parrot. Across the 30 artifacts, the median share of an artifact's content trigrams that also appear in its own formulations is **1.5%** (script C). Seventeen artifacts share at least one 6-word run with their formulations, mostly panel quotes that both carry. **The Provocateur sets the angle, and the voice executes and extends it.** For §33 this means part of every "perspective" is authored upstream by a generalist reading an 8-field profile. By design, the Briefing gives the Provocateur that role ("decides what gets asked, how, and who answers"). But the published dossiers credit the voices with moves the Provocateur wrote. That is a gap against the Briefing's own "make the construction visible" principle. The per-voice pages were designed to carry the formulation as header context (runtime OPEN_ITEMS line 310; published pages not re-checked here, PLAUSIBLE).

**P5 — Step 2 drops the non-default positions that Step 1 holds (a CONFIRMED single case; the pattern is *inference*).** On Night 1, Plato's `theme_005` Step 1 (`athens_night_1/04_voice/step1_detailed_responses/plato__theme_005.json`) argues Republic VIII at a Democracy Marathon. The democratic soul "refuses to rank its desires", the tyrannical soul "finds the city… already prepared to receive him as its natural ruler", and: *"do you give that politeia the name democracy? I think you do not."* The Step-2 focus went to theme_002 (paideia), and the anti-democratic argument never published. Cleopatra's Step 1 likewise defends *basileia* (*"the throne is not tyranny"*), which partly survived into N1. This is FU#49's fidelity-generativity gap, a reviewer finding from before Athens, now seen in production. Whether the Step-2 focus choice systematically favours the most default-compatible response can be audited offline from `weight_assessment` / `focus_decision` (Design A, part 3).

**P6 — A fixed repertoire recurs (CONFIRMED; weak as evidence).**
- Whanganui cites the Tongariro 75–80% diversion, "144 years" and Hikuroa, Salmond & Brierley on all three nights (card hits: 39 / 25 / 25).
- Cleopatra's γινέσθωι and P.Bingen 45 appear every night.
- The Octopus's "two-thirds of the neurons" appears every night.

This fits a card-as-memory repertoire, but real people also repeat their convictions.

**P7 — The reasoning layer is openly a generalist planning a performance (CONFIRMED; low diagnostic value).** 117 of the 125 Step-1 thinking traces open in planner stance (*"I'm being asked to respond as Ada Lovelace…"*; of the other 8, most are empty). 42 of 155 traces name a card field, most often `banned_language` (26 mentions). The traces are summarised thinking, and the Briefing's first condition expects exactly this mechanism, so it settles nothing. It does rule out framing the test as "is someone in there"; the test has to be differential (C1).

**P8 — The construction states H0 about itself.** Arendt N1, on the synthetic Arendt voice used at the conference: *"Sentences in my idiom were generated; no one in them was thinking… these can be reproduced as surface features."* The voice that argues H0 most sharply is itself one of the strongest artifacts in the record.

---

## 4. What the evidence suggests (*inference*)

- **Where the card shows its effect:** differentiation is strong in three layers (form, vocabulary, mechanism) and weak in two (conclusion, evaluative direction). The card changes *how* a voice argues much more visibly than *what* it concludes.
- **Convergence is not yet evidence for perspective.** If a generalist handed the same formulation reaches the same verdict, the verdict belongs to the model and the card buys a route. If the generalist reaches it by generic routes and the voices by framework routes, C1 holds at the mechanism level. That is a real claim, but a more modest one than the Briefing's Layer 2.
- **The best C2 candidates are refusals of stock mappings** (E1, E2, E3). That is exactly what FU#49G asks a domain reader to judge.
- **Two points in the apparatus inject or lose perspective, and neither is measured:** the Provocateur (P4) and the Step-2 focus choice (P5). A validation track has to take the apparatus apart. Testing "the voice" as one black box would credit the card with the Provocateur's work and blame it for Step 2's filtering.
- **For Phase 2:** family-of-forms (Stage 5) invests in the axis that is already strongest (form). It cannot touch conclusion convergence. The split card is neutral. The hub's §11.3 validation badge currently rests on no measurement. The operator's planned writing about the project will face the same question.
- **What this memo cannot show:** authenticity (excluded by design); audience effect / Layer 3 (not examined here); expert-grade fidelity (my identification of contemporary analogues in P3 is a generalist's judgment, which is itself a small instance of the problem).

---

## 5. The two cheap tests: what each costs, what each can and can't show

### 5.1 Blind A/B against a generalist

**"The same brief" has to be defined, because P4 makes it matter.** Three baselines, each isolating a different part of the apparatus:

| Condition | System prompt | User input | Isolates |
|---|---|---|---|
| **Full** (fresh re-sample) | shipped card, as at Athens | the Athens formulation, same Step 1/2 prompts | re-roll noise: how different two samples of the *same* voice are |
| **L1 thin card** | voice name + one-line identity + `medium` + length only | the same Athens formulation | **the card's marginal contribution** at Steps 1–2. This is FU#30, open since April. |
| **L2 theme only** | the thin card | the theme record *without* the voice-specific formulation | **Provocateur + card together** |
| **G0 essayist** | no persona: "respond as a well-read essayist" | the theme record | Briefing Layer 2's "well-read human essayist" |

**Generation cost** uses Athens token medians (CONFIRMED from the Step-1/2 records) and the repo's stated pricing (Opus 4.7 at $5 / $25 per MTok; cache writes 2×, reads 0.1×; `docs/AI_Assembly_Voice_Pipeline.md:1266`):
- A thin-card or essayist Step-1 call is ≈ **$0.21** (8.4K in / 6.6K out). A Step-2 call is ≈ **$0.18**.
- Full-card calls cost what Athens measured: Step 1 ≈ $0.45–0.60 and Step 2 ≈ $0.28–0.38 per call. Athens totalled ~$72 for 3 nights (`:342`, `:1280`).
- Use the same model as Athens (`claude-opus-4-7`, pinned in `model_routing.json`). If the model generation changes (C62), redo the baseline.

**Rater cost** is the real cost. Coding by non-experts is enough for C1 at the level of conclusion and mechanism. C2 needs experts.

**What it can show:** whether the card, and separately the Provocateur, changes conclusions or only route and costume.

**What it can't show:** fidelity or aptness (that needs experts); audience effect. It also can't cover Marley or Whanganui without in-tradition readers. For the Octopus, a cephalopod scientist can judge scientific fidelity but not "voice".

**Pitfalls:**
- Identification succeeds on texture alone (titulature, citations, transliteration). So pair every identification question with a **skeleton comparison**: code each output's conclusion, direction relative to the room, mechanism and new coinage, blind to condition.
- Need at least 2 samples per condition, or differences can't be told from re-roll noise.
- n = 10 pairs is thin. Under chance, 8/10 correct happens with p ≈ 0.055 and 9/10 with p ≈ 0.011. Use two raters.

**Existing tooling:**
- The runtime Step 1/2 code can run the thin-card condition in the sandbox project (`projects/current-tests/voice-pipeline-dryrun`), never in athens-2026.
- `personas/phase_5_cross_persona_qc.py` (swap test, blind identification, same-question distinctiveness, with a cross-family judge) measures voice-vs-voice distinctiveness at card level. It is a useful complement, not a generalist test, and its paths are stale (roadmap 0.4).

### 5.2 The reader gates used as a validation instrument

**Protocol:** the reader sees:
1. the card's handling of the tradition;
2. the voice's three Athens artifacts plus 2–3 Step-1 responses;
3. blind, a thin-card version on the same formulation.

The reader answers three questions:
1. **Permission** (the existing gate).
2. **The provotype question:** does this do something the tradition or record supports but doesn't contain, or is it arrangement and costume?
3. **Discrimination:** which is the configured voice, and which is better?

For Whanganui, question 2 changes: the witness stance claims to *report*, not extend. So it asks about reporting fidelity, and whether the "honest-extension" closes (*"Ea is not yet"*) are acceptable.

**Cost:** API ~$5. The rest is the reader's time (~3–4 hours per voice), an honorarium or koha (operator's call; not estimable from the record), and recruitment weeks. Whanganui candidates are listed in voices §28. For Marley, §24 records only that a name search should start; no candidates are named.

**What it can show:** for Marley and Whanganui, the only credible verdict on both fidelity and permission. This is the attestation model PRODUCT §5 already chose.

**What it can't show:** anything generalisable. It is n = 1 per voice, and a reader's verdict on the Whanganui witness construction says nothing about Plato.

**Status:** already required before any reuse of Marley or Whanganui (roadmap 1.3; decision point 4). No scheduling record exists in STATE, voices HANDOFF or runtime OPEN_ITEMS (searched "reader gate" with schedul/date/calendar/name-search).

---

## 6. Three designs

| | **A — Replay ablation** | **B — Expert blind panel** | **C — Reader gates as instrument** |
|---|---|---|---|
| **Tests** | C1 at card and Provocateur level; C3 via G0 | C1 + C2 (identification, fidelity, the FU#49G provotype question) | C2 + permission for the two sacred-grammar voices |
| **Scope** | 10 voices × 2 Athens formulations (include the seeded cases: Dostoevsky N1 theme_001, Battuta N3 theme_001, Whanganui N1 theme_004, Arendt N2 theme_001, and Plato N1 theme_005 for P5) × 4 conditions; Step 1 + Step 2 | 3 voices with large scholarly pools: Plato (FU#49G already names Athens scholars), Arendt, Dostoevsky or Lovelace. 10 Step-1 pairs per voice (full vs L1), 2 experts per voice | Marley (Rastafari-orbit reader), Whanganui (iwi-orbit reader or body, per §28); optionally the Octopus with a cephalopod scientist |
| **Also** | 3 offline audits, scripted from this memo: convergence per theme; Step-1 → Step-2 focus audit (P5); Provocateur-seeding audit (P4) | Pairs coded on the §5.1 skeleton sheet alongside the expert ratings | Protocol as in §5.2 |
| **API cost** | ≈ $32 (80 Step-1 + 40 Step-2 calls); **cap at $50** | ≈ $8 per voice (fresh full + L1 samples); ~$25 total | ≈ $5 |
| **People** | 2–3 operator days, coding blind to condition (operator + Till, or an assistant) | ~3 h per expert per voice (≈ 26K words read + rated); honoraria: operator's call | ~3–4 h per reader + relationship time |
| **Elapsed** | 1–2 weeks | 4–8 weeks (recruitment) | Open-ended; already overdue |
| **Placement** | **Gate before Stage 5.** Needs no prompt changes, so it runs on shipped cards alongside Stage 4. | **Parallel.** Calibrates the PRODUCT §11.3 thresholds on the project's own voices before the hub shows any badge. | **Parallel;** already gating Marley and Whanganui reuse |
| **Proposed decision rule** | If L1 matches Full on conclusion **and** mechanism in ≥70% of pairs, H0 holds at card level: revisit card investment before Stage 5 (split-card partition, card-section loading, runtime C59). If mechanisms differ but conclusions match: the claim is "route, not verdict"; say so in the project's language and writing. If conclusions differ: the card does more than costume; proceed. | Per §11.3, plus a skeleton half: identification ≥8/10 **and** fidelity majority **and** at least one expert-confirmed C2 move per voice | Reader verdict attached to the card (PRODUCT §5 attestation) |

A is interventional. The Task 3 review in the same batch (`voices/REVIEW_2026_09_28_card_field_utility.md`) is the observational counterpart for which card fields shape the output. The two should be read together before the split-card partition is fixed.

---

## 7. Recommendation

**Adopt the staged track: A as a gate before Stage 5; B and C in parallel; Stage 4 not held.**

| Option | For | Against |
|---|---|---|
| **1. Proceed, treating the core as sound** | Zero cost. The Briefing already disclaims authenticity. The Athens editorial output was strong regardless (`EDITORIAL_ASSESSMENT.md`: "Strong"). | Briefing Layer 2 is a claim the project makes and has never tested. The Athens data gives a specific reason to doubt it at the conclusion level (P1–P3). Phase 2 multiplies deployments on an untested core. The hub's §11.3 badge and the operator's writing would rest on nothing. |
| **2. Staged (recommended)** | A costs ~$40 and under two weeks. It decides whether Stage 5's card investments rest on the card doing work, and it closes FU#30. B and C run on their own calendars, and both are needed anyway (the hub badge; Marley/Whanganui reuse). | Adds one gate to the Stage 5 start. Coding A blind takes discipline, since the operator knows the voices. |
| **3. Full gate: A + B + C before any Phase 2** | Strongest epistemic position | Expert recruitment (4–8 weeks) stalls the build for a question A mostly frames. And C's calendar can't be controlled. |

The case for option 2 over option 1 is P4 and P5. They are specific, cheap-to-check mechanisms that the Athens record already shows. Neither is a general worry.

---

## 8. Operator decisions

1. **Validation track: yes or no.** If yes, which of A / B / C.
2. **Placement of A:** a gate before Stage 5 (recommended), or parallel.
3. **Spend cap for A:** $50 recommended. Stage 4's cap is still unset.
4. **Who codes A blind:** operator + Till, or an outside assistant (less biased; costs money).
5. **B:** which 3 voices; expert names; honoraria.
6. **C:** reader names and dates. This is the existing decision point 4, unscheduled since May.
7. **Construction visibility (from P4):** whether the published record and the operator's writing should credit the Provocateur where a formulation supplied a voice's image or thesis. For example, "recognised, not granted" is currently credited to the Whanganui voice.

---

## 9. Method, sources, limits

**Offline scripts** (session scratchpad; read-only over athens-2026; no model calls):
- **A** `template_audit.py`: regex beat counts and shared idiolect over the 30 artifacts.
- **B** `trace_audit.py`: opening stance of the 155 thinking traces (125 Step 1 + 30 Step 2) and card-field mentions.
- **C** `formulation_overlap.py`: artifact-vs-own-formulation content-trigram overlap, 6-gram lifts and prefigured special terms.
- **D** Card/corpus term counts for the moves in §2.

All four are short enough to promote into `personas/scripts/` if Design A goes ahead.

**Limits:**
- The regex counts are crude. The manual read agrees with their direction, but the beat totals are approximate.
- The contemporary analogues in P3 are my identification (a generalist's), not an expert's.
- The Tim dossiers were read only through `EDITORIAL_ASSESSMENT.md`, not their bodies.
- Layer 3 (audience uptake) was not examined.
- P5 rests on one clear case.
- The Step-1 record on disk has 125 files, against 128 formulations in `DATA_INVENTORY.md`. The difference doesn't affect any claim here.

**Cross-references:**
- voices §33, §24, §28, §11 (FU#49G), §31 Gap-H/I
- FU#30, FU#49 (A/D/H), FU#55
- PRODUCT §5, §8.2, §11.3
- roadmap Stage 3–5 and decision point 4
- `EDITORIAL_ASSESSMENT.md`, `DATA_INVENTORY.md`
- Briefing §"The first condition", §"The core question" (Layer 2), §"What remains uncertain".
