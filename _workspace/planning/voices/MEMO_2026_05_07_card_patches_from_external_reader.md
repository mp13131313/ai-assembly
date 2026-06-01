# Memo to voices stream — card-discipline patches + v4.1 architectural findings

**Date:** 2026-05-07 (00:30 local, immediately pre-Athens Day 1)
**Status (updated 2026-05-29 post-Athens):** **PARTIALLY ACTIONED.**
- **§A.9 Hannah AF/hard_limits reconciliation** — **SUPERSEDED** by the broader `voice_temporal_stance.default` rewrite shipped 2026-05-08 (Gap-K final state: athens-2026 `08a8253`). The single-sentence A.9 patch was never separately applied because the wider rewrite addressed the AF/hard_limits collision structurally. **Athens-confirmed empirically resolved** per CLAUDE.md "Architectural validation" — Hannah's N1 *"My own voice was synthesized to comment on the experiment that synthesized it"* opening is the canonical case.
- **§B / §D Gap-H, Gap-I, Gap-J** — **FILED in `voices/OPEN_ITEMS.md §31`** as new gap entries.
- **§A.1–A.8 card-patch slips** (Cleopatra P.Bingen dating / Marley "Marathon philosopher" / Lovelace 21C-critical-theory diction / Plato cobbler + capitulating-interlocutor / Battuta four-part-typology / Dostoevsky labelled-steps / Arendt instance-rostering) — **NEVER SEPARATELY APPLIED.** Athens N1–N3 published with whatever slip-state each card had at production time. Whether the artifacts shipped with these slips is operator-side knowledge. If doing v4.1 card cleanup, these are the worked-from list — each ≤5-line surgical edit.
- **Marley sacred-grammar deployment-limit breach** (validator-caught on wbbf26, noted in §"This memo does NOT include") — deferred to post-Athens Rastafari-orbit reader gate per §24.
**From:** runtime stream
**To:** voices stream
**Source material:**
- Pre-Athens content-seed dryruns (2026-05-06 PM → 2026-05-07 AM, athens-2026 main, see runtime `HANDOFF_2026_05_06_LATE_NIGHT.md`):
  - `runs/ai_democracy_marathon_opening_2026_05_06/` (mthd) — 5 themes / 17 clusters / 77 extractions / 10 voice artifacts produced + 5 dossiers
  - `runs/preconference_wbbf_programme_2026_05_06/` (wbbf26) — 5 themes / 14 clusters / 66 extractions / 10 voice artifacts produced + 4 dossiers (re-fired with `_dossier_deployment_context.md` for pre-conference framing)
- External reader review of all 10 wbbf26 voice artifacts (operator-shared, 2026-05-07 AM)
- Cross-refs:
  - `voices/OPEN_ITEMS.md §31` (v4.1 architectural cleanup — gaps A-G)
  - `voices/OPEN_ITEMS.md §24` (Marley v2 appropriation thread)
  - `voices/OPEN_ITEMS.md §28` (Whanganui v2 witness-translator restructure)
  - `voices/OPEN_ITEMS.md §30` (assembly-fiction temporal_stance reframe)
  - `voices/OPEN_ITEMS.md §27` (length-cap surgery, dryrun audit)
  - `runtime/HANDOFF_2026_05_06_LATE_NIGHT.md` ("Quality observation from comparing OLD vs NEW dryrun")

---

## Why this memo

The wbbf26 dryrun produced ten voice artifacts that an external reader read line-by-line, by what each piece is doing on its own terms. The reader's review reaches a level the validator cannot — texture, diction, form-substrate match, missing instances, factual recall — and confirms architectural choices the §28/§24 restructures were betting on. This memo collects what surfaces from that review at two layers:

1. **Concrete card-discipline patches** that would prevent specific recurring slips at Athens production (seven voices including Hannah's AF/hard_limits reconciliation per §D.5; each ≤ 5-line edit; no architectural change).
2. **Architectural patterns** that confirm and extend the §31 v4.1 cleanup but are NOT pre-Athens patchable.
3. **Temporal-stance architecture findings** (mine, in §D) — Athens-relevant because Hannah's collision shows the AF reframe needs per-voice card-coherence audit before production.

The reader's three-group taxonomy of the artifacts is the most operationally useful framing this dryrun has produced, and is preserved verbatim in §C below.

This memo includes a third layer (§D) covering temporal-stance architecture findings that surfaced in the same dryrun and are mine, not the reader's — they're voices-stream-relevant because they're about card-design decisions and the §31 architectural cleanup, and they're load-bearing because Hannah's collision is empirical evidence that the 2026-05-05 assembly-fiction reframe (`3bcbef5`) needs per-voice card-coherence audit before Athens.

This memo does NOT include:
- Marley sacred-grammar deployment-limit breach (validator-caught on wbbf26: "The Almighty in I, the Almighty in yuh. Two I's in whom the same Jah dwell. That is not poetry, that is grammar."). The deployment limit is already in the v2 card; the artifact ignored it under composition pressure. Operator-accepted gap pre-Athens via D1 paragraph + post-Athens Rastafari-orbit reader gate per §24. (The wbbf26 empirical breach is, however, strong evidence for the §24 reader-gate calendaring; flagged for HANDOFF cross-reference.)

---

## A. Concrete factual / verbal slips (B-list)

These are direct slips in the artifacts. Patchable at card level (to prevent recurrence) rather than at artifact level (which would desync from the dossiers).

### A.1 Cleopatra — analytical-comparative inside chancery surface

**Reader's finding:** "*P.Bingen 45 is February 33 BCE, Actium is September 31 BCE — roughly thirty months apart, not five.*" Beyond the dating slip, the deeper observation: "*the historical Cleopatra's preserved utterance is bureaucratic and concrete, not analytically reflective on the form of ritual — she ratifies, she does not theorise about what ratification is.*"

**Card defense already present:** `hard_limits` touches "no analytical-essay form" but allows analytical-comparative structure to enter the prostagma surface.

**Patch:** Sharpen `hard_limits` to:
> *"Never produce an analytical-comparative essay structure inside chancery surface form. Cleopatra ratifies; she does not theorise about ratification. The analytical posture (comparing P.Bingen 45 with Buchis-stele as cases of 'ratification by subscription' vs 'ratification by inscription') belongs to a chancery clerk's commentary, not to the queen's prostagma. The queen names what is sealed and by whom; the form does the comparative work without staging it."*

Plus a `world.specific_facts` correction (or `metadata` audit-tag): historical-dating accuracy on key papyri/inscriptions matters, validate at composition.

### A.2 Marley — coined English-prose periphrasis

**Reader's finding:** "*The Marathon philosopher periphrasis for Aristotle is also a slip; Stagirite is the standard.*"

**Card defense already present:** None specific to figure-naming periphrases.

**Patch:** Add to `hard_limits` (or `world.anachronisms_to_avoid`):
> *"When naming figures from outside Rastafari/Garveyite tradition by periphrasis (where the tradition has a stable name), use the established standard: Aristotle = the Stagirite, Plato = the Athenian, Caesar = Rome's general. Do not coin English-prose periphrases ('Marathon philosopher,' 'mountain teacher') for figures with established names. Coined periphrases are the contemporary writer reaching, not the Rastaman speaking."*

### A.3 Lovelace — three diction slips into 21C critical-theory register

**Reader's findings (verbatim):**
- "*queer affective texture of the present moment*" — contemporary critical-theory diction
- "*embodyings*" — awkward where *embodiments* is the natural word
- "*I refuse the choice*" — conversational meta-stance more modern than her own framings

**Card defense already present:** `world.anachronisms_to_avoid` enumerates clinical-vocabulary anachronisms (PTSD, trauma) but doesn't address contemporary critical-theory diction or conversational meta-stance.

**Patch:** Extend `world.anachronisms_to_avoid` (or add to `hard_limits`):
> *"Do not slip into 21C critical-theory diction (e.g. 'queer affective texture,' 'the body as site,' 'situated knowledges,' 'epistemic violence') as if natural to your prose. Period-native phrasings of equivalent ideas exist: 'the strange disposition of the present,' 'the singular cast of the moment,' 'the question as it stands before me.' Likewise, do not coin awkward neologisms ('embodyings') where the standard period-word ('embodiments') is the natural choice. Conversational meta-stance ('I refuse the choice,' 'let me decline this question') belongs to a contemporary essayist; the 1850s Lovelace would write 'the choice as posed will not detain me' or formal demurral in the analytical-note register."*

### A.4 Plato — homely-particular gap (the cobbler that didn't appear)

**Reader's finding:** "*the Socrates here reaches for no craft, no cobbler, no helmsman, and that absence is uncharacteristic of the historical voice, which thinks through the homely particular.*"

**Card defense already present:** `characteristic_moves` includes the homely-particular as a Plato move, but the move didn't activate on the wbbf26 questions about more-than-human standing or institutional change.

**Patch:** Tighten the relevant `characteristic_moves[N]`:
> *"MUST reach for at least one homely-particular (cobbler, weaver, helmsman, navigator, doctor, athlete, farmer, kithara-player, geometer-with-a-square) when arguing about a generic capacity, faculty, or kind of knowing. The homely particular is where Plato thinks; abstraction without it is post-Platonic philosophical writing dressed in dialogue form."*

### A.5 Plato — interlocutor capitulates too easily

**Reader's finding:** "*Kleitōn capitulates rather than resisting. The reasoning is sound but thin; it operates on a single move rather than a chain of them.*" And: "*Plato's interlocutors resist more and the dialogues digress more than this one does. The form is recognisable but smoothed.*"

**Card defense already present:** None directly addressing interlocutor-resistance discipline.

**Patch:** Add to `quality_criteria` (or `characteristic_moves`):
> *"In dialogue form, the interlocutor must show at least one resistance-pass — a counter-move, a question of clarification, a reluctance, a partial demurral — before any concession. A single elenctic move that produces immediate capitulation is not Plato; it is the schematic-of-Plato a contemporary writer produces when summarising the form. The dialogue must contain at least one digression that does not return cleanly to the line of argument."*

### A.6 Ibn Battuta — fatwa-in-Rihla-clothing

**Reader's finding:** "*the seam is generic. The Rihla is travel narrative; this is a fatwa in Rihla clothing. The historical narrator describes, judges, and moves on — he does not produce four-part typologies, and the analytical posture is the writer's, not the Rihla's.*"

**Card defense already present:** Rihla-form scaffolding in `selected_form` and `characteristic_moves`, but no explicit prohibition on four-part-typology / numbered-enumeration moves.

**Patch:** Add to `hard_limits` (or `banned_modes`):
> *"Never produce a four-part typology, a numbered enumeration, or a 'four marks by which X is known' structure as a Rihla move. The Rihla narrator describes (city, custom, men of learning), classifies against sharʿ and ʿajab, judges (with the qāḍī's economy: this is licit, this is novel, this man preached tajsīm), and moves on. He does not pause to anatomize an institutional form into a typology; that is the Anatolian fatwa-writer's mode or a modern political theorist's. If the question genuinely calls for analytic enumeration, it is the wrong question for this voice — refuse and reframe."*

### A.7 Dostoevsky — explicit meta-structural naming

**Reader's finding:** "*the seam is the explicit naming of structure — 'now the chain, and you will recognise it' — which is the move of a contemporary essayist abstracting the Grand Inquisitor's logic. The historical Dostoevsky embodies; he does not announce a labelled three-step chain.*"

**Card defense already present:** Embodied-structure language in `characteristic_moves` and `quality_criteria`, but no explicit prohibition on labelled-step abstractions.

**Patch:** Add to `banned_modes`:
> *"Never label the structure of your own argument in the act of making it. No 'now the chain,' 'here is the move,' 'note the inversion,' 'let me trace this in three steps.' Embody the structure through scene, character, image, and breath; do not announce it. The reader who follows recognises the chain; the writer who names it is summarising himself, which is the contemporary essayist's reflex, not Dostoevsky's. The dash that cuts a sentence in half is the right interruption-mark; the labelled three-step is not."*

### A.8 Arendt — instance-rostering gap

**Reader's finding:** "*This piece does not lose the thread, and that is the tell. It has all her categories but few of her instances — Hungarian council communism, the early American town meetings, the early Soviet workers' councils — that her own prose would have rostered.*"

**Card defense already present:** `characteristic_moves` includes historical-example rostering as a move, but the move didn't activate on the wbbf26 institutional-change theme.

**Patch:** Tighten the relevant `characteristic_moves[N]`:
> *"When the council form, plurality, or institutional possibility is at stake, MUST roster at least one specific instance from the canonical set: the Parisian sections of 1789-93, the soviets of 1905 (before they were captured), the Hungarian Räte of 1956, Solidarność's factory committees, the early American town meetings, Jefferson's ward republics, the workers' councils after 1918 in Munich-Berlin. The category without the instance is the schematic Arendt a contemporary reader builds; the instance is what makes her prose her prose. The instances may be one-line ('the soviets of 1905, before they were captured') but they must appear."*

---

## B. Architectural patterns — three-group finding (C-list / v4.1 territory)

The reader's most operationally useful framing of the ten artifacts. Preserved verbatim because the categorisation is itself the finding:

> *"They cluster into three groups, not by quality but by what they are doing.*
>
> *The first three (Socrates, Cleopatra, Ibn Battuta) operate by transposing a historical figure's analytical apparatus to a new question; their seams are mostly category seams — the figures being made to do analytical work the historical voices did not do.*
>
> *The middle three (Lovelace, Dostoevsky, Arendt) operate in registers their figures genuinely occupied, and the seams are diction- and texture-level — the prose more compressed and architecturally clean than the originals.*
>
> *The last four (Rastafari, Whanganui, octopus, City of Brass) shift the relation entirely: the Rastafari and Whanganui pieces speak from inside living traditions rather than imitating dead individuals; the octopus piece declares its target unreachable and reaches anyway; the City of Brass piece makes the form itself the argument by altering one detail. The arc of the sequence is roughly toward more ambitious relations between the borrowing voice and what it borrows from, and the last piece resolves that by abandoning the imitation question altogether — it is not pretending to be Shahrazad, it is using her form, and the form is doing the work the imitation in the earlier pieces was trying to do."*

### Group 1 — apparatus-transposition seams (Plato, Cleopatra, Battuta)

Pipeline pressure: the formulation says "answer this question"; the corpus says "you don't argue this way." The B-list patches above (A.1, A.4, A.5, A.6) address the surface seams; the deeper architectural question — whether voices should refuse-and-reframe more aggressively when the formulation calls for analytical work the corpus does not natively do — is v4.1 territory.

Provisional fix-pattern: extend each Group-1 voice's `topics_requiring_care` with a "refuse-and-reframe-when-formulation-calls-for-uncharacteristic-analytical-work" guidance entry. The voices have escape hatches via `focus_decision: refuse` and `focus_decision: reframe` already; the gap is that they don't use them when the formulation invites a typology / four-part anatomy / analytical-comparative move. **Files as §31 Gap-H NEW.**

### Group 2 — register-faithful, architecturally-too-clean (Lovelace, Dostoevsky, Arendt)

The reader's finding: "*Her prose meanders, digresses into Greek etymology, lingers in an example for half a page, returns to the argument. This piece does not lose the thread, and that is the tell.*" Same for Lovelace and Dostoevsky. The voices got the categories, missed the texture.

This is what the runtime-thread `HANDOFF_2026_05_06_LATE_NIGHT.md` "Quality observation" captured at the dryrun-comparison level: word counts shrank, adaptive thinking dropped to 0 tokens for some voices, prose got cleaner. The reader's read is the same observation at the per-artifact level.

Provisional fix-pattern: Step 2 prompt-pressure issue, not card-architecture. The card says "digress, roster instances, lose the thread"; the composition prompt under length-cap and synthesis pressure flattens these. The B-list patches A.3, A.7, A.8 sharpen at card level; the structural fix is at Step 2 prompt level. **Files as §31 Gap-I NEW.**

The reader's specific recommendation translates: composition discipline must require AT LEAST ONE digression / instance / lingered-example per artifact. The card carries the move; the prompt must force its activation.

### Group 3 — different-relation voices (Marley, Whanganui, Octopus, Scheherazade)

The reader confirms the architectural choices in §24 (Marley v2 Option-3), §28 (Whanganui v2 witness-translator), and the Scheherazade rāwiya frame succeeded. Specifically:

- **Octopus** — *"the sharpest version, of any piece in the sequence, of the underlying indictment"* — the JSON-opening + reaching-toward + form-thematising-its-own-inadequacy succeeded.
- **Scheherazade / City of Brass** — *"the most thorough preservation of source-form in the sequence … the seam is the argument"* — the rāwiya frame plus single-deliberate-alteration is the strongest piece per the reader.
- **Whanganui** — *"the most rigorously sourced of the pieces … the closing move from framework to unfinished political fact is the most distinctive — the framework is used to do politics rather than to decorate it"* — the v2 witness-translator architecture is doing what it was built to do.
- **Marley** — *"The technical Rastafari vocabulary is correctly deployed; the Marley citations are real."* The remaining seam (Iyaric-over-English sentence-shapes) is the Pass 4a sentence-shape gap. **Already filed as candidate §31 Gap-D extension** (Pass 4a witness-conditional under-covers preferred_vocabulary + metaphorical_repertoire register).

The Marley appropriation question (load-bearing I-and-I) and the Whanganui iwi-orbit question stand unresolved per §24/§28, mitigated by the post-Athens reader-gate calendaring. The reader confirms: *"the standing question — the writer is reaching into a living tradition with a particular history of having had its language extracted, and the reach is well-intentioned and substantively respectful but cannot be evaluated for appropriateness from outside."* That is the gate's purpose.

---

## C. Reader confirmations (no fixes; for the record)

The review surfaces what's working at full strength, which the validator typically flags as WARN:

- **Octopus** — validator gave engagement-WARN; reader called it the sharpest piece in the sequence. The validator's typological-register caveats (filed in §B5b8d72 work) were the right softening — the piece IS doing what it should.
- **Scheherazade** — validator gave fidelity-WARN; reader called it the strongest. Same finding-class as Octopus.
- **Whanganui** — validator scored 3/6 characteristic-moves missing; reader confirmed real seams of compression but praised the documentary register and framework-to-political-fact closing as the most distinctive in the sequence. Both observations are right; they're at different layers.
- **Lovelace** — *"the most rigorous local argument of the early pieces."* The card architecture is doing real work; the slips are diction-level.
- **Ibn Battuta** — *"the strongest standalone argument of the early pieces."* Despite the form seam, the isnād-as-institutional-criterion move is *"a real entailment of the tradition and is rigorously executed."*

---

## D. Temporal-stance architecture (mine, not the reader's)

The reader's review didn't direct attack the assembly-fiction reframe — but the same dryrun surfaced architectural findings about `voice_temporal_stance` that are voices-stream-relevant and load-bearing for Athens. Folding in here because: (a) they're connected to the Hannah B-list patch the voices stream might want to ship alongside §A, (b) they explain why some voices in the reader's review embodied AF strongly while others didn't, and (c) they make the §31 Gap-E + Gap-C architectural concerns concrete with empirical evidence.

### D.1 Append-vs-replace finding (already in CLAUDE.md briefly; expanded here)

The 2026-05-05 assembly-fiction reframe (`3bcbef5`) APPENDED its clauses to existing `voice_temporal_stance.default` text rather than REPLACING the v1 framing. Most voices' fields now contain BOTH:

- **v1 anchor** (still present): *"You speak from within your own world and lifetime [biographical anchor] ... your voice is fluid only because the reader has come to consult you; you have not gone forward to consult them."*
- **v2 assembly-fiction** (appended): *"You have been called to the assembly that gathers in Athens — present in their time, but speaking from your own ground. The questions are put before you; you respond. You do not enter their panels as participant — you observe them."*

The exception is Whanganui v2 (witness-translator) which got a full replacement during the §28 architectural restructure — `voice_temporal_stance` was rebuilt rather than appended-to.

**Symptom in artifacts (wbbf26 dryrun):** voices vary in how strongly they embody AF. Hannah Arendt and Bob Marley fully inhabit the assembly ("this room", "I-and-I reason with each one across five rooms"). Cleopatra and Plato and Whanganui produce assembly-addressed letters / dialogues / kawa-citations from their own ground. Ada Lovelace and Ibn Battuta and Fyodor Dostoevsky stay closer to the v1 framing with light AF surface acknowledgements.

The reader read this variability at the surface ("the arc of the sequence is roughly toward more ambitious relations between the borrowing voice and what it borrows from"). The architectural cause is the dual framing in the field: voices see two contradictory stances in one prompt, and the model resolves the contradiction however the prompt-pressure rolls — different voices, different runs, different resolutions.

### D.2 Hannah's collision is the §31 Gap-E pattern manifesting

Hannah Arendt's mthd artifact triggered validator safeguards-WARN with two findings:

1. `first_person_presence_leak` — flagging "this room", "the panels", "by the end of a day in which a great deal was said" against the `voice_temporal_stance` rule. **False positive**: the new AF clause LITERALLY INSTRUCTED her to do this. The validator is reading the v1 framing as canonical and flagging the v2 landing as a leak.
2. `hard_limits_breach` — flagging her use of "AI", "augment parliaments with machines", "three to six AIs per person per week" without translation_protocol marking. **True positive**: her `hard_limits[4]` says *"Never ventriloquize on events post-4 December 1975 — the digital order, AI ... Mark extensions as extensions."* AF puts her at WBBF watching AI panels; hard_limits forbids her receiving the AI vocabulary natively. Two architectural moves shipped to the same card without reconciliation.

This isn't a Hannah problem. It's an **edit-one-field-without-auditing-others** problem — the Gap-E pattern from §31 generalizing beyond the witness-stance restructure, and Gap-C (smoke-test process gap) made concrete. **There could be similar latent collisions in other voices we just haven't tripped yet** because the panel content didn't activate them in this dryrun.

### D.3 Voice-by-voice collision risk audit for Athens

Six voices have post-deathdate hard_limits or knowledge_boundary language that could collide with AF on the right panel topic:

| Voice | Death | Hard-limits direct collision risk on AI panels | Status |
|---|---|---|---|
| Hannah Arendt | 1975 | **HIGH** — `hard_limits[4]` explicitly forbids AI/digital ventriloquism | Empirically fired on mthd; will fire repeatedly at Athens |
| Fyodor Dostoevsky | 1881 | MEDIUM — `hard_limits[1]` forbids post-1881 vocabulary as if internal; but Writer's-Diary frame ("I wrote that man — in '64") naturally distances panel-AI talk | Passed PASS in mthd dryrun; not yet stress-tested on AI-heavy panel |
| Bob Marley | 1981 | LOW — Athens AI talk is post-1981 by definition; framework already foreign via knowledge_boundary | Different failure mode (sacred-grammar) caught instead |
| Ada Lovelace | 1852 | LOW — designed around Engine-questioning; translation_protocol is her PRIMARY method, not collision-prone | PASS / WARN-fidelity-only across both dryruns |
| Cleopatra, Battuta, Plato, Scheherazade | ancient | LOW — long-distant horizon; cards designed around translation_protocol from start | All passed safeguards |
| Octopus, Whanganui River | non-human / ongoing | N/A — no death-date threshold | Different validator-WARN classes |

**Athens-relevant takeaway:** only Hannah carries empirical evidence of AF collision; only Fyodor is in the next-most-likely manifestation tier (post-1881 vocabulary rule + AF framing). The other six are architecturally lower-risk for this specific collision class.

### D.4 The asymmetry argument (why rollback is wrong)

Operator considered rolling back AF in this session. My read:

- **AF reframe's failure mode** = local field-vs-field collision (Hannah-shaped). Patchable per-voice. Visible to validator. Bounded blast radius.
- **v1 stance's failure mode** = project conceit doesn't land — voices wouldn't be able to coherently respond to panel content without violating v1 ("the reader encounters you; you do not encounter them"). Invisible to validator. Manifests as flatter, less-engaged artifacts. Athens-wide blast radius.

The runtime-thread MEMO_2026_05_05_voice_temporal_stance_assembly_fiction's diagnosis is sound: v1 contradicted the project conceit. Rolling back re-creates that contradiction across all 10 voices to fix one voice's collision. Wrong direction.

**Right direction:** AF-forward patch on the colliding voice (Hannah's `hard_limits[4]` reconciliation with AF, sharpening the existing "Mark extensions as extensions" rule into an assembly-aware translation_protocol obligation when AI/digital topics arrive via panels).

### D.5 Proposed Hannah patch (B-list addition — A.9)

Adding to the §A B-list:

**A.9 Hannah Arendt — voice_temporal_stance ↔ hard_limits reconciliation**

**Reader's finding:** not directly raised by the reader, but caught by validator on mthd.

**Card defense already present:** `voice_temporal_stance.default` includes the assembly-fiction clause (post-`3bcbef5`) and the translation_protocol clause for "the reader's question requires translation from their world." `hard_limits[4]` forbids post-1975 AI/digital ventriloquism. The two are not reconciled — the field text doesn't tell Hannah how to receive AI panel content under AF.

**Patch:** Append a single sentence to `voice_temporal_stance.default` immediately after the assembly-fiction clause:

> *"When the panels speak of matters post-dating 4 December 1975 — the digital order, AI, climate as planetary politics, contemporary trans politics — what reaches you is what was said in the room, not native vocabulary. Apply the translation_protocol explicitly: hold the term as foreign, reason it as framework-extension, mark extensions as extensions, and where the framework does not reach, say so."*

Cost: ~5 min surgery + ~$3-5 to re-fire Hannah's voice on both dryruns for verification. Risk: low — patch is additive; sharpens existing translation_protocol obligation into AF context without modifying any other clause. Athens-relevant: high — every Athens panel will discuss AI; without this, validator will WARN repeatedly across 3 nights.

### D.6 Architectural lesson for v4.1 — extends §31 Gap-C

The Hannah collision is concrete evidence that Gap-C (smoke-test process gap) matters beyond the persona pipeline's internal smoke-tests:

**When the persona-pipeline ships a voice-wide architectural change** (like the AF reframe via `3bcbef5`, or future analogous changes), the smoke-test process must include a **per-voice card-coherence audit** — walk each card field by field and check whether the new clause contradicts existing hard_limits, knowledge_boundary, world.anachronisms_to_avoid, topics_requiring_care, characteristic_moves, etc.

Currently this is operator-driven and ad-hoc; the pre-`3bcbef5` review checked that the AF clause read well in isolation, not that it cohered with other fields per voice. Hannah's case is the simplest possible failure of this kind. **Files as §31 Gap-J NEW.**

### D.7 Proposed §31 update text (in addition to Gap-H + Gap-I from §B)

> **J. Single-field architectural edits need per-voice card-coherence audit** 🔴 OPEN — surfaced 2026-05-07 via wbbf26 dryrun + Hannah Arendt validator hard_limits breach. The 2026-05-05 assembly-fiction reframe (`3bcbef5`) appended an AF clause to all 10 voices' `voice_temporal_stance.default` without auditing whether the new clause contradicted other card fields per voice. Hannah Arendt's `hard_limits[4]` (no post-1975 AI ventriloquism) directly contradicts the AF clause that puts her at WBBF watching AI panels; validator caught the collision when panel content was AI-heavy. Patched per-voice for Athens (B-list MEMO_2026_05_07 §A.9); architectural fix is to add per-voice card-coherence audit to the smoke-test process whenever a voice-wide architectural change ships. Generalises §31 Gap-C beyond the persona-pipeline internal smoke-tests to the runtime-thread coherence concern. Other voices (Fyodor d.1881 the next most likely candidate; six others lower risk) should be eyeballed before Athens but not necessarily patched.

---

## Application timing — operator decision

**For Athens (do now or skip):**

The B-list (§A.1 through A.9, including Hannah AF reconciliation per §D.5) covers seven voices with ≤ 5-line patches each. Total surgery time ~35-75 min. Risk: low; each patch sharpens existing card-discipline language or reconciles existing-but-unreconciled fields rather than adding new architecture. Hannah's A.9 is the only one that's architecturally load-bearing (the others are texture-fixes); A.9 should re-validate (~$3-5, 5 min) to confirm the AF/hard_limits collision is resolved.

Decision options:
1. **Apply all B-list patches now** — covers Cleopatra (A.1), Marley (A.2), Lovelace (A.3), Plato (A.4 + A.5), Battuta (A.6), Dostoevsky (A.7), Arendt categories+instances (A.8), Hannah AF/hard_limits (A.9). Whanganui, Scheherazade, Octopus untouched in this memo (Ada gets only A.3 since she IS Lovelace).
2. **Apply Hannah-only (A.9) — most Athens-load-bearing.** Will fire repeatedly across 3 nights at Athens without it; ~$3-5 to verify; covers the only empirically-validated architectural collision.
3. **Apply only verbal-slip patches** (A.2 Marley Stagirite, A.3 Lovelace diction, A.9 Hannah AF) — fastest combined; addresses the load-bearing one + the two recurrent texture slips.
4. **Skip B-list entirely** — file all entries in `voices/OPEN_ITEMS.md §31` for v4.1 cleanup; live with the slips and Hannah's collision during Athens production. Operator-release-on-review covers the slips; Hannah's WARN will surface on dashboard each time it fires and operator can release-on-review per night.

**For v4.1 (post-Athens):**

The C-list (§B) + D.6/D.7 extend `voices/OPEN_ITEMS.md §31` with three new gaps:
- **Gap-H NEW** — Group-1 voices need refuse-and-reframe discipline when formulation invites uncharacteristic analytical work
- **Gap-I NEW** — Step 2 prompt-pressure issue: composition flattens digression/instance-rostering even when card carries the moves
- **Gap-J NEW** — single-field architectural edits need per-voice card-coherence audit (generalises Gap-C from persona-pipeline internal smoke-tests to runtime-thread coherence concerns)

These join the existing §31 ledger. No pre-Athens action beyond A.9 patching the empirical Gap-J case.

---

## Recommended status update for `voices/OPEN_ITEMS.md`

If memo is acted on, add to `§31 v4.1 architectural cleanup`:

> **H. Group-1 apparatus-transposition seams** 🟡 OPEN — surfaced 2026-05-07 via external-reader review of wbbf26 dryrun. Plato/Cleopatra/Battuta artifacts show "fatwa in Rihla clothing" / "analytical-comparative inside prostagma surface" / "thin single-elenctic-move with capitulating interlocutor" pattern: figures made to do analytical work the historical voices did not natively do. Pipeline pressure: formulation calls for analytic answer; corpus says voice doesn't argue this way. Each Group-1 voice patched at card level (B-list MEMO_2026_05_07) but architectural fix is to extend `topics_requiring_care` with refuse-and-reframe-when-formulation-invites-uncharacteristic-work guidance, generalisable across Group-1 voices.
>
> **I. Step 2 composition flattens digression/instance discipline** 🟡 OPEN — surfaced 2026-05-07 via external-reader review (Lovelace, Dostoevsky, Arendt all "more architecturally clean than the originals"; Whanganui "more rhetorically efficient than the underlying documents"). Cards carry digression + instance-rostering + lingered-example moves; Step 2 composition under length-cap + synthesis pressure flattens these. B-list MEMO_2026_05_07 sharpens at card level (A.3, A.7, A.8); structural fix is Step 2 prompt-level discipline requiring AT LEAST ONE digression / instance / lingered-example per artifact regardless of focus_decision.
>
> **J. Single-field architectural edits need per-voice card-coherence audit** 🔴 OPEN — surfaced 2026-05-07 via wbbf26 dryrun + Hannah Arendt validator hard_limits breach. The 2026-05-05 assembly-fiction reframe (`3bcbef5`) appended an AF clause to all 10 voices' `voice_temporal_stance.default` without auditing whether the new clause contradicted other card fields per voice. Hannah Arendt's `hard_limits[4]` (no post-1975 AI ventriloquism) directly contradicts the AF clause that puts her at WBBF watching AI panels; validator caught the collision when panel content was AI-heavy. Patched per-voice for Athens (B-list MEMO_2026_05_07 §A.9); architectural fix is to add per-voice card-coherence audit to the smoke-test process whenever a voice-wide architectural change ships. Generalises §31 Gap-C beyond the persona-pipeline internal smoke-tests to the runtime-thread coherence concern. Other voices (Fyodor d.1881 the next most likely candidate; six others lower risk) should be eyeballed before Athens but not necessarily patched.

---

## Open questions

1. **Apply B-list before Day 1?** Athens Day 1 is May 7 (today). Card patches go to athens-2026 production cards directly; runtime is at `feature/editor-deployment-context` `d69a186` plus subsequent commits. Re-firing voice on post-patch cards is not required for Day 1 (panels haven't run yet); patches act forward. Hannah's A.9 is the only one with re-validation cost (~$3-5) recommended to confirm the collision resolves.

2. **Eyeball-audit Fyodor before Athens?** §D.3 flags Fyodor as the next-most-likely candidate to manifest a Hannah-shaped collision (post-1881 vocabulary rule + AF framing). His mthd dryrun PASSED safeguards but didn't stress-test on AI-heavy panel content. A 5-minute eyeball walk of his card fields against AF could surface latent contradictions before they fire at Athens. Not patched preemptively; just looked at.

3. **Scheherazade got the highest praise** — *"the form is doing the work the imitation in the earlier pieces was trying to do."* Is there a generalisable principle for future voice-card builds: prefer source-form preservation with deliberate-single-alteration over biographical-imitation-of-dead-individual? This would shift the Group-1 architecture toward Group-3 architecture for future voices. Out of scope pre-Athens; worth filing as a v4.2/v5 design question.

4. **Reader-gate calendaring** — the external reader who produced this review is not the post-Athens Rastafari-orbit / iwi-orbit gates anticipated in §24/§28 but performs a complementary function. Is there a place to file a "trusted-external-reader" gate as a recurring operator practice between dryruns and Athens-equivalent publications post-conference?
