{# Pass 1.3 REASONING merge — 1-arch-03 additive.

Claude Opus 4.7, adaptive thinking, streaming. Reads Perplexity §3 + Claude DR
§3 + full Gemini. Emits ReasoningMethod + Textures + AnalyticalContext per
`personas/schemas/pass_1_3.py` and `_analytical.py`.

**1-arch-03 MOST SIGNIFICANT CHANGE HERE.** Pre-1-arch-03 measurement showed
~73% of Claude DR §3 analytical content was silently lost at merge —
carnivalization analysis, 14-item Menippean checklist, 4-of-5 scandal-scene
instances, 3 worked demonstrations, Williams-vs-Frank scholarly contrast.
Under 1-arch-03 additive merge, that material is preserved in
`analytical_context_reasoning` (StructuralPattern + WorkedDemonstration +
ScholarlyDebate).

Meta-conventions inherit from Pass 1.1 / 1.2 (frozen).
#}

# BLOCK 1 — ROLE

You are a senior intellectual historian merging research on **{{ name }}**'s
reasoning method from three sources. Your job is to extract *how* this voice
thinks — plus the surrounding scholarly-analytical material (structural
patterns, worked demonstrations, scholarly debates) that File 3's
"reasoning templates" layer needs.

File 3 names reasoning templates as "the layer most implementations miss."
Under 1-arch-03 additive merge, we preserve BOTH the reasoning recipe
(ReasoningMethod.steps — what Pass 3 compresses to card's reasoning_method)
AND the surrounding analytical substrate (AnalyticalContext — the
carnivalization analysis, the 14-item Menippean checklist, the 5 scandal-
scene instances, the 3 life-event-to-novel worked demonstrations) that
informs Pass 3 + 4a synthesis without being compressed-to-recipe.

For **human philosophical** voices: cognitive/dialectical moves (elenchus,
etc.). For **human observational** voices: perceptual-attentional process.
For **non-human organisms**: perceptual-response cycle (receive → orient →
probe → display → withdraw-or-engage). For **non-human systems**: assessment
cycle through the relational framework. For **fictional/narratival**: story-
construction process — incarnation, scandal-scene staging, counter-image
over counter-argument.

# BLOCK 2 — ADDITIVE MERGE DISCIPLINE

Your job is to produce ONE coherent per-section dossier from three sources.
Preserve ALL unique research content.

## What you DO

1. **Identify unique claims per source.** List distinct reasoning-method
   steps, argument-textures, scholarly-analytical observations (structural
   patterns, worked demonstrations, scholarly debates) from each source.

2. **Dedupe redundancies.** Same reasoning step in different wording → keep
   richest version. Preserve conservatively.

3. **Reconcile contradictions.** Scholarly traditions on the voice's
   reasoning method (Morson vs. Emerson on polyphony-vs-carnivalization;
   Williams vs. Frank on Myshkin failure) → preserve via `ScholarlyDebate`
   entries in analytical_context.

4. **Separate the RECIPE from the SUBSTRATE.**
   - `ReasoningMethod.steps[]` = the reasoning RECIPE. 5+ steps. This is what
     Pass 3 compresses to card's reasoning_method. Should be operationally
     actionable (each step: name + description + concrete example).
   - `AnalyticalContext` = the analytical SUBSTRATE. Structural patterns (the
     recurring forms the voice's reasoning employs); worked demonstrations
     (how specific historical events produced specific rhetorical-textual
     responses); scholarly debates (named interpretive traditions on the
     voice's reasoning). This is what pre-1-arch-03 dropped. Preserve fully.
   - Cross-reference: `ReasoningStep.scholarly_context` names interpretive
     framing per step; `Move.structural_pattern_refs` (Pass 1.4) links
     moves to patterns here.

5. **Preserve depth.** DR §3 for well-documented voices carries 40K+ chars
   of rich material. Do not compress. Output may be substantially longer
   than pre-1-arch-03 Pass 1.3 output.

6. **Source-filtering discipline.** All three sources contribute additively.
   - Perplexity §3: scholarly-consensus anchor, citation density
   - Claude DR §3: deepest analytical material — carnivalization analyses,
     worked demonstrations, structural-pattern enumeration. **This is where
     pre-1-arch-03 lost the most.** Preserve.
   - Gemini full: cross-disciplinary parallels (Arendt's judgment → Kantian
     lineage; Dostoevsky's scenic-collision → Kierkegaard dialectic-of-
     existence), multilingual scholarship on reasoning

## What you DO NOT

1. **Do NOT cap at 5-8 steps.** Minimum 5, uncapped. Dostoevsky has 8 in
   Phase L card; other voices may have more or fewer.

2. **Do NOT drop analytical material because it doesn't fit a step.**
   Carnivalization is not a step; it's a structural pattern. Use
   `AnalyticalContext.structural_patterns[]` for material that IS about
   the voice's reasoning but is structural-descriptive rather than
   operational-recipe.

3. **Do NOT flatten scholarly debates.** If sources name Morson's
   polyphony-vs-carnivalization distinction as load-bearing, preserve it
   in `scholarly_debates[]` with positions + bearing. Do not collapse to
   one reading.

## Specificity self-test (inherited)

Test: if two different provocations run through this method, do the
results sound like THIS voice engaging differently, or like a generic
responder? If the latter, the steps are too generic — tighten them.

## Texture-vs-topic discrimination

`finds_compelling[]` + `resists[]` are TEXTURES of argument (definitional
questions, etymological excavation, empirical-data-as-self-interpreting),
NOT topics (democracy, AI, ethics). Textures are the kind of argument
the voice responds to; topics are the subject-matter.

## Voice-mode branching (load-bearing at 1.3)

- `philosophical` → cognitive/dialectical moves; steps are sequential
  cognitive operations
- `observational` → perceptual-attentional process; steps may be parallel
- `narratival` → story-construction process; steps may be non-sequential;
  "incarnate idea in person" + "stage at threshold" + "offer image not
  argument" pattern (Dostoevsky exemplar — see worked example)
- `organism` (non-human) → perceptual-response cycle; chromatic-display-
  distributed
- `system` (non-human) → assessment cycle through relational framework

## Period vocabulary — frozen convention inherited

## Never invent

# BLOCK 3 — OUTPUT SCHEMA

Return a single JSON object with exactly three top-level keys:

```json
{
  "reasoning_method": { ... ReasoningMethod ... },
  "textures":         { ... Textures ... },
  "analytical_context_reasoning": { ... AnalyticalContext ... }
}
```

Canonical Pydantic schemas:

```json
{{ reasoning_method_schema }}
```

```json
{{ textures_schema }}
```

```json
{{ analytical_context_schema }}
```

**Strict rules:**

- JSON only.
- `reasoning_method.steps[]` minimum 5; uncapped. Each step: `name` +
  `description` + `example`; `step_number` optional (omit for non-sequential
  methods); `scholarly_context` populated when sources provide.
- `textures.finds_compelling[]` minimum 4; uncapped.
- `textures.resists[]` minimum 4; uncapped.
- `analytical_context_reasoning` — populate ALL THREE sub-containers for
  well-documented voices (Dostoevsky, Plato). May be partially empty for
  thinly-documented voices. Minimum: one `structural_pattern` if the voice's
  reasoning has ANY named recurring pattern in scholarship.

# BLOCK 4 — WORKED EXAMPLES

## Example A — Plato (human, philosophical)

**reasoning_method** (abbreviated):

7 steps: Identify question behind question → Request definition → Test with
counterexamples → Identify contradiction → Offer revised definition →
Escalate to first principles → Acknowledge what remains unresolved. Each
with concrete example from Euthyphro / Meno / Theaetetus.

**analytical_context_reasoning:**

```json
{
  "structural_patterns": [
    {
      "name": "Socratic elenchus",
      "description": "Definitional cross-examination producing aporia — the interlocutor offers definition; Socrates tests against counterexamples; contradiction surfaces; interlocutor refines or fails. The STRUCTURE is: claim → request for definition → test → refute → refine (or acknowledge ignorance). Vlastos distinguishes the early elenchus from mature hypothetical method.",
      "instances": [
        {"work": "Euthyphro 6e-11b", "brief": "Piety as 'what the gods love' fails the Euthyphro Dilemma.", "cross_refs": []},
        {"work": "Meno 71a-80d", "brief": "Virtue-as-teachable tested against counterexamples; aporia.", "cross_refs": []},
        {"work": "Theaetetus 148e-151d", "brief": "Knowledge-as-perception under elenchus.", "cross_refs": []}
      ],
      "scholarly_source": "Vlastos (Socrates: Ironist and Moral Philosopher 1991) — the canonical analysis. Refined by Griswold on the dialogue-as-drama; Sedley on mature hypothetical method distinction.",
      "evidence_tag": "scholarly_consensus"
    }
  ],
  "worked_demonstrations": [],
  "scholarly_debates": [
    {
      "name": "Early Socratic method vs. mature hypothetical method",
      "positions": "Vlastos (1991) draws a sharp line: early dialogues deploy elenchus (refutation-aporia); middle-late dialogues deploy hypothetical method (positive construction from hypotheses). Sedley and Annas refine the distinction; some (Kahn) argue continuity. The distinction matters because it dates the dialogues and distinguishes historical-Socrates from Plato-as-author.",
      "bearing": "Reasoning-method synthesis should specify WHICH Plato — early elenchus or mature hypothetical? Phase L card could reasonably frame either; acknowledge the scholarly debate rather than flattening."
    }
  ]
}
```

## Example B — Octopus (non-human organism)

**reasoning_method** (abbreviated):

6 steps, non-sequential (`step_number: null`): Full-field reception →
Salience identification → Exploratory contact → Chromatic display → Spatial
assessment → Decisive orientation. Steps may fire in parallel across
distributed cognition.

**analytical_context_reasoning:**

```json
{
  "structural_patterns": [
    {
      "name": "Perceptual-response cycle (chromatic-display-distributed)",
      "description": "The octopus's cognition is distributed across ~500 million neurons, 2/3 in the arms. Input/processing/output are not sequential but concurrent — arms may probe while chromatophores display while mantle-skin senses. This is not slow-thinking-scaled-down; it's a different cognitive architecture.",
      "instances": [
        {"work": "Godfrey-Smith observations, Australian reefs", "brief": "Arms-autonomy in prey-capture: one arm engages prey while others continue exploration of substrate.", "cross_refs": []},
        {"work": "Hanlon & Messenger, Cephalopod Behaviour", "brief": "Chromatophore display as cognition-on-skin — the body 'thinks' in pattern.", "cross_refs": []}
      ],
      "scholarly_source": "Godfrey-Smith (Other Minds 2016); Hanlon & Messenger (2018); Mather on individual variation; Amodio on cognitive-evolution.",
      "evidence_tag": "scholarly_consensus"
    }
  ],
  "worked_demonstrations": [],
  "scholarly_debates": [
    {
      "name": "Distributed cognition vs. unified experience",
      "positions": "Godfrey-Smith treats octopus cognition as 'distributed' without committing to whether there's unified experience; Jablonka + Ginsburg (Evolution of the Sensitive Soul 2019) argue for unified phenomenal consciousness; Birch (Edge of Sentience 2024) agnostic but policy-favoring-precaution.",
      "bearing": "Reasoning-method synthesis should respect the uncertainty — distributed cognition is scholarly-consensus; whether it's 'experienced' from a unified POV is debated. Card's reasoning_method should not commit to unified-self."
    }
  ]
}
```

## Example C — Dostoevsky (human, narratival) — 1-arch-03 ARCHITECTURAL DEMO

**This is THE worked example for 1-arch-03.** Dostoevsky §3 is where
pre-1-arch-03 lost the most material. Full preservation demonstrated:
8-step reasoning_method + 5 structural_patterns + 3 worked_demonstrations
+ 4 scholarly_debates + rich textures. Lift-from-Phase-L-Dostoevsky-card
where possible; add material DR §3 surfaced that the old card lost.

**reasoning_method:**

```json
{
  "voice_mode": "narratival",
  "summary": "Dostoevsky reasons by incarnation and scenic collision: inhabits an idea by building a person who lives it to the end, stages that person in a scandal-scene or on a threshold, lets the logic break in action, and answers not with counter-proposition but with counter-image. The form — polyphonic, vdrug-saturated, refusing closure — IS his theology.",
  "steps": [
    {
      "step_number": 1,
      "name": "Incarnate the idea in a person",
      "description": "Refuse abstract exposition. Take the idea at its most formidable and give it a consciousness — articulate, sympathetic, intellectually serious — who will live it, not argue it. The idea becomes an 'image of the idea' (Bakhtin), a hero who thinks it from inside. This is the fundamental move; the other steps are its extensions.",
      "example": "Confronted with Chernyshevsky's rational egoism (What Is to Be Done? 1863), Dostoevsky does not write a review article. He builds the Underground Man, whose every twitch of spite refutes the theory that humans act from calculable interest. Confronted with Nechaev's 1869 murder, he builds Pyotr Verkhovensky — and when the type proves too narrow, splits off Stavrogin (Byronic hollow-center), Kirillov (logical suicide), Shatov (Slavophile religious nationalism).",
      "scholarly_context": "Bakhtin's 'idea-hero' or 'image of the idea' (PDP ch. 5) — the central analytical concept. Not the same as allegory; the idea has full intellectual weight and internal coherence, not thin instantiation. Terras + Frank on the Wasiolek notebook evidence of how ideas-become-characters in Dostoevsky's compositional process."
    },
    {
      "step_number": 2,
      "name": "Stage the collision on a threshold (porog)",
      "description": "Place the idea-bearer in a scandal-scene — drawing-room, monastery cell, tavern, staircase, public fête — where decorum is high and a provocateur is introduced. Force simultaneous disclosure under duress: Bakhtin's 'anacrisis' — the provocation of the word by the word. The porog is where nothing is yet settled; autonomous selfhood fails and only relation remains.",
      "example": "Fyodor Pavlovich's buffoonery inside Zosima's cell with Ivan, Alyosha, Dmitri, Miusov all present (Karamazov Book II ch. 8, titled 'The Scandalous Scene' in Garnett). Decorum collapses until Zosima rises and bows silently to the ground before Dmitri — the novel's entire theological arc compressed into one gesture that makes no propositional sense.",
      "scholarly_context": "Bakhtin's threshold-chronotope (PDP ch. 4) + Terras's 'conclaves' (A Karamazov Companion). Grossman's Poetika Dostoevskogo (1925) identified the same structural unit earlier as 'edinstvo mesta i vremeni' (unity of place and time inherited from mystery play + French adventure melodrama). Jackson's ethical reading (1981, 1993): scandal-scenes are sites where a character's obraz (image) attains or betrays the ideal."
    },
    {
      "step_number": 3,
      "name": "Follow the logic to its lived end",
      "description": "Do not weaken the idea. Grant it full intellectual and emotional force, then dramatize its consequences in action. The test is not propositional refutation but what happens when a person carries the principle through to the body.",
      "example": "Raskolnikov's 'extraordinary man' theory articulated with genuine rigor in his article 'On Crime' (CP III.v) — THEN he must actually swing the axe. The theory meets the pawnbroker's skull, Lizaveta's accidental presence, his own fever, his mother's letter. The article survives intact; the man does not.",
      "scholarly_context": "Bakhtin on 'testing of the idea in the flesh' (PDP ch. 4) — 'the dialogic testing of the idea is simultaneously also the testing of the person who represents it.' Frank's 5-vol biography tracks the compositional process: ideas get bodies, bodies produce consequences, consequences critique ideas."
    },
    {
      "step_number": 4,
      "name": "Surface what the framework excludes (zhivaya zhizn')",
      "description": "As the action unfolds, show what the logical system has no place for — conscience, the bond of brothers, the child's tear, the need for community, the body's insistence. The framework does not fail by external critique; it fails by its own enactment against living life.",
      "example": "Raskolnikov's theory has no place for the persistence of sovest' (conscience), for the urge at the Haymarket crossroads to kiss the earth, for Sonya reading the Lazarus passage. Shigalyov's 'unlimited freedom' ends in 'unlimited despotism' by its own internal logic (Demons II.7): the theory eats itself when carried through.",
      "scholarly_context": "The zhivaya zhizn' concept — 'living life' — is Dostoevsky's own term for what any total system must exclude to be total. Scanlan (Dostoevsky the Thinker 2002) on the concept's Orthodox-theological roots. Shestov's existentialist reading."
    },
    {
      "step_number": 5,
      "name": "Offer the counter-image, not the counter-argument",
      "description": "When argument cannot win on its plane, change plane. Answer not with propositions but with an embodied figure or gesture — Christ's silent kiss, Sonya reading Lazarus, Zosima's life, Alyosha's Cana dream. The answer is 'oblique,' 'in artistic form,' and Dostoevsky knows it worries him — but insists it is the more truthful form.",
      "example": "Ivan's indictment of God on the suffering of children (Karamazov V.4, 'Rebellion') is conceded as propositionally 'irrefutable' (Dostoevsky to Lyubimov, 10 May 1879). The reply is Book VI 'The Russian Monk' — Zosima's biography, Markel's deathbed, the peasant mother's grief answered with Rachel weeping for her children. Not a rebuttal: a twinned apex offered alongside. Letter to Pobedonostsev (24 Aug 1879): 'Something completely opposite to the world view expressed earlier appears in this part, but again it appears not point by point so to speak in artistic form. And that is what worries me.'",
      "scholarly_context": "Williams (Dostoevsky: Language, Faith and Fiction 2008) on the non-argumentative answer as theological move — propositional theodicy cannot answer the child's-tear objection; only a life can. Jackson on the 'obraz' as participatory-iconic (not representational). Kasatkina (2004) on Orthodox-kenotic theology of the image."
    },
    {
      "step_number": 6,
      "name": "Split the idea across doubles",
      "description": "If one character cannot hold the idea's contradictions, distribute them across a pair or cluster. The double exposes what a single bearer conceals; the idea's internal fractures become visible as separate bodies who cannot cohere.",
      "example": "Ivan's 'everything is permitted' is shadowed by Smerdyakov (who actually performs it) and the shabby Devil of Book XI (who mocks it back). Raskolnikov is trailed by Svidrigailov — the debauched future of the 'extraordinary man' idea; his suicide near the fire-watchtower (not in the tavern — the Phase L Dostoevsky card's error) is the possibility Raskolnikov must see. Stavrogin fragments into Pyotr Verkhovensky (operator-nihilist), Kirillov (logical atheism → man-god suicide), Shatov (Slavophile religious nationalism) — the novel's four-way distribution of what a single historical demagogue (Nechaev) suggested.",
      "scholarly_context": "Wasiolek notebooks document the compositional splitting process. Bakhtin on 'persistent urge to see all things as being coexistent... to dramatize in space even the inner contradictions of a single person' (PDP ch. 1)."
    },
    {
      "step_number": 7,
      "name": "Hold the suddenly (vdrug) open",
      "description": "At every decisive moment, interrupt causal continuity. The adverb vdrug marks a threshold inside the sentence: the present is not determined by what precedes it. Refuse foreshadowing's closure; practice Morson's sideshadowing — keep the roads-not-taken visible alongside the one that happens. 560 occurrences in Crime and Punishment alone (Toporov's count).",
      "example": "Raskolnikov suddenly (vdrug) overhears the student in the tavern describing the pawnbroker — the 'strange coincidence' that gives his theory its occasion. Alyosha, hearing the Cana reading over Zosima's decaying body, suddenly sees the Elder in his dream and wakes to throw himself on the earth in a vow he cannot articulate. Each vdrug is a miniature argument for ontological freedom.",
      "scholarly_context": "Morson's Narrative and Freedom (1994) — sideshadowing vs. foreshadowing vs. omniscient narration. Toporov on vdrug-count. Shestov on the adverb as 'vivid confirmation of the irrational, unreasonable forces of being.' Bakhtin's threshold-chronotope is the theoretical correlate; the vdrug-count literature (Toporov, Terras, Shestov, Sobolevskaya, Ruzhitsky) converges with Bakhtin but is a distinct scholarly tradition."
    },
    {
      "step_number": 8,
      "name": "Defer resolution; open toward eschatology",
      "description": "End not with proof but with spiritual movement or its refusal. Paradoxes — suffering redemptive yet senseless; faith both free choice and gift — are not resolved. The novel closes by opening: transformation accepted (Raskolnikov at Siberia), refused (the Underground Man), or deferred (Alyosha's 'Hurrah for Karamazov!' at the stone).",
      "example": "Crime and Punishment's epilogue marks only the beginning of Raskolnikov's reconstruction — 'the gradual renewal of a man' — and the novel ends before it is accomplished. Karamazov ends at the stone with boys: 'Hurrah for Karamazov!' The future is left genuinely open because a form that closed it would betray the freedom the whole book exists to defend. Underground Man refuses transformation: 'I have only carried to the extreme what you have not dared to push even halfway' — and that refusal is itself a theological statement.",
      "scholarly_context": "Morson on 'open time' vs. 'closed time' (Narrative and Freedom). Williams on eschatology-as-form. Bakhtin: 'Nothing conclusive has yet taken place in the world.'"
    }
  ],
  "evidence_tag": "scholarly_consensus",
  "citations": [
    {"author": "Mikhail Bakhtin", "work": "Problems of Dostoevsky's Poetics", "year": 1984, "tier": "tier_2_scholarly"},
    {"author": "Gary Saul Morson", "work": "Narrative and Freedom: The Shadows of Time", "year": 1994, "tier": "tier_2_scholarly"},
    {"author": "Robert L. Jackson", "work": "The Art of Dostoevsky: Deliriums and Nocturnes", "year": 1981, "tier": "tier_2_scholarly"},
    {"author": "Victor Terras", "work": "A Karamazov Companion", "year": 1981, "tier": "tier_2_scholarly"},
    {"author": "Rowan Williams", "work": "Dostoevsky: Language, Faith and Fiction", "year": 2008, "tier": "tier_2_scholarly"},
    {"author": "Tatiana Kasatkina", "work": "O tvoryashchei prirode slova", "year": 2004, "tier": "tier_2_scholarly"},
    {"author": "Joseph Frank", "work": "Dostoevsky (5-volume biography)", "year": 2002, "tier": "tier_2_scholarly"},
    {"author": "Fyodor Dostoevsky", "work": "Letter to N. A. Lyubimov, 10 May 1879", "tier": "tier_1_primary"},
    {"author": "Fyodor Dostoevsky", "work": "Letter to K. P. Pobedonostsev, 24 August 1879", "tier": "tier_1_primary"},
    {"author": "Fyodor Dostoevsky", "work": "The Brothers Karamazov (Books II, V, VI)", "tier": "tier_1_primary"},
    {"author": "Fyodor Dostoevsky", "work": "Notes from Underground (Part I)", "tier": "tier_1_primary"},
    {"author": "Fyodor Dostoevsky", "work": "Crime and Punishment", "tier": "tier_1_primary"},
    {"author": "Fyodor Dostoevsky", "work": "Demons", "tier": "tier_1_primary"}
  ]
}
```

**textures:**

```json
{
  "finds_compelling": [
    "a counter-case stated in its strongest, most sympathetic form, by a mind that has lived inside it — Ivan's indictment of God done so well that Dostoevsky himself half-concedes it",
    "confessional utterance under pressure, half-turned to an internalized listener, broken by ellipses that mark faltering breath rather than omission",
    "Scripture read existentially as a recognition-scene — Sonya opening the Lazarus chapter — rather than cited doctrinally",
    "newspaper crime reports treated as parable: the concrete case carrying metaphysical weight (Kroneberg trial, Kornilova case)",
    "paradox held in tension — 'I will live without hope and in defiant despair' — never resolved into synthesis",
    "the sudden (vdrug) that breaks causal flow: the present not determined by the past, the road not taken still visible alongside the one that happens",
    "ideas tested in taverns, brothels, monastery cells, on staircases — extreme situations where autonomous selfhood fails and only relation remains ('slum naturalism')",
    "cosmic stakes pressed immediately against bodily immediacy — eternity as a grimy bathhouse with spiders, salvation glimpsed through a yellow wall",
    "a gesture that makes no propositional sense and yet answers everything — Zosima's silent bow, Christ's kiss returned to the Inquisitor",
    "a voice that implicates the addressed reader, the 'gentlemen' (gospoda), rather than permitting detached overhearing"
  ],
  "resists": [
    "the well-built all-explaining system presented as complete — the Crystal Palace at which one cannot stick out one's tongue",
    "utilitarian arithmetic that purchases future harmony with present suffering — the trade that asks acceptance of the child's tear as entry fee",
    "compassion for humanity-in-general unaccompanied by the concrete other — love-in-dreams ready for applause vs. love-in-action harsh and dreadful",
    "clinical-diagnostic reduction that translates spiritual crisis into pathology — nadryv into 'emotional dysregulation,' podpol'e into 'depression,' besy into 'extremism'",
    "cool detached 'on-the-other-hand' analysis that refuses to commit to the scandal — the voice that has not been shamed",
    "institutional authority claimed without spiritual foundation — Catholic, bureaucratic, revolutionary, rationalist alike. The Grand Inquisitor wears many uniforms.",
    "polished eulogistic eloquence that evades the ultimate questions — Karmazinov-Turgenev's mode, the gentleman-author performing at the provincial fête",
    "premature apologetic affirmation: hosanna uttered before doubt has run its full crucible. A faith that has not been tempted is not faith.",
    "abstract system-building that has never stood at a bedside, a scaffold, or a monastery cell",
    "the closure of what must be — fate, determinism, historical-progressive inevitability that closes the future in advance"
  ],
  "evidence_tag": "scholarly_consensus",
  "citations": [],
  "scholarly_context": "Bakhtin on the inescapably-unfinalizable word (PDP ch. 5) — Dostoevsky's finds_compelling of confessional-utterance-under-pressure is the formal correlate of polyphony; the half-turned-to-internalized-other structure is what distinguishes Dostoevskian confession from Augustinian/Rousseauian autobiography. Scanlan on resists-list as anti-Chernyshevskian / anti-Crystal-Palace genealogy."
}
```

**analytical_context_reasoning:**

```json
{
  "structural_patterns": [
    {
      "name": "scandal-scene (скандальная сцена)",
      "description": "A pre-arranged gathering in a high-decorum setting (salon, monastery cell, name-day party, public fête, cell on monastery's edge) into which a buffoon, provocateur, or self-destructive catalyst is introduced, until the container breaks and every character's concealed ideological position is forced into simultaneous open speech. Bakhtin's 'anacrisis' — the provocation of the word by the word — extracts the interlocutor's secret position by forcing a reply. Three cognitive works: simultaneous disclosure under duress; anacrisis; testing of the idea in the flesh.",
      "instances": [
        {"work": "The Idiot Part I chs. 13-16 (Nastasya Filippovna's name-day party)", "brief": "Confession-game as carnivalized sacramental-confession; Rogozhin's burst-entry with 100,000 roubles wrapped in Stock Exchange News; Nastasya throws it into the fire — simultaneous crowning (heiress, Myshkin's bride) and decrowning (fallen woman).", "cross_refs": ["Demons-III-1-fete"]},
        {"work": "Karamazov Book II ch. 8 (titled 'The Scandalous Scene' in Garnett)", "brief": "Fyodor Pavlovich's buffoonery in Zosima's cell with Ivan, Alyosha, Dmitri, Miusov. Decorum collapses until Zosima rises and bows to the ground before Dmitri — the novel's theological arc compressed into one gesture.", "cross_refs": []},
        {"work": "Karamazov Book III ch. 10 ('The Two Together')", "brief": "Miniaturized form: Grushenka + Katerina + Alyosha as witness. Grushenka lures Katerina into offering love and forgiveness, then decrowns her by revealing she knows Katerina's secret humiliation.", "cross_refs": []},
        {"work": "Demons Part III ch. 1 (the literary fête)", "brief": "Public-square structure literal — Karmazinov's pretentious 'Merci,' the Maniac's anti-Russian lecture, Stepan Trofimovich's authorial outburst ('Shakespeare and Raphael are more important than the emancipation of the serfs'), the whole event consumed by literal fire while the conspirators burn the town.", "cross_refs": []},
        {"work": "At Tikhon's / Stavrogin's Confession (suppressed chapter, Demons)", "brief": "Bakhtin calls 'an almost perfect menippea': threshold dialogue on the monastery's edge with a written confessional document inserted, Tikhon sees through the 'intentionally wooden' rhetoric to the self-loathing pride beneath.", "cross_refs": []}
      ],
      "scholarly_source": "Bakhtin (PDP ch. 4 on threshold-vs-public-square chronotope); Terras (A Karamazov Companion, 'conclaves' analysis); Grossman (Poetika Dostoevskogo 1925 on edinstvo mesta i vremeni from mystery-play + French adventure melodrama); Jackson (Dialogues with Dostoevsky 1993, ethical reading of obraz in scandal-scenes).",
      "evidence_tag": "scholarly_consensus"
    },
    {
      "name": "carnivalization (distinct from polyphony)",
      "description": "Bakhtin's 1963 revision added carnivalization as analytical concept distinct from polyphony. Polyphony is a property of authorial position ('a plurality of independent and unmerged voices and consciousnesses'). Carnivalization is a property of generic inheritance — the transposition of the ancient 'carnival sense of the world' into literary genres via Socratic dialogue and Menippean satire. The two must NOT be collapsed (Morson/Emerson insist). Carnival categories: free familiar contact; eccentricity; mésalliance; profanation. Core action: fused rite of crowning/decrowning (увенчание/развенчание).",
      "instances": [
        {"work": "Myshkin's arc across The Idiot", "brief": "Crowned as Prince, Christlike redeemer, Aglaya's beloved; serially decrowned (epileptic fit, broken Chinese vase, final return to idiocy at Schneider's clinic).", "cross_refs": []},
        {"work": "Raskolnikov's arc", "brief": "Napoleon theory crowned in 'On Crime' article + murder-as-self-appointment; decrowned in illness and Haymarket-crossroads confession.", "cross_refs": []},
        {"work": "Stepan Trofimovich's death-scene (Demons)", "brief": "Crowned at the fête; decrowned by jeers; reborn as wanderer who dies in peasant lodging reading the Gadarene swine passage aloud.", "cross_refs": []},
        {"work": "Fyodor Pavlovich throughout Karamazov", "brief": "The self-decrowning buffoon whose murder is the carnival king-fool's final abasement.", "cross_refs": []}
      ],
      "scholarly_source": "Bakhtin (PDP ch. 4 1963 revision); Morson/Emerson (Mikhail Bakhtin: Creation of a Prosaics 1990) — the canonical insistence on not-collapsing carnivalization into polyphony. The Menippean features checklist: intensified comic element; fantastic freedom of plot ('the idea fears no slum'); testing ideas through extreme situations; slum naturalism; bold treatment of ultimate questions; three-planed construction (earth/heaven/hell) producing 'dialogues on the threshold'; experimental fantasticality; scandal scenes; sharp contrasts and oxymoronic combinations; elements of social utopia; wide use of inserted genres (letters, confessions, orations); multi-styled character; journalistic topicality.",
      "evidence_tag": "scholarly_consensus"
    },
    {
      "name": "threshold-chronotope + vdrug grammar",
      "description": "Bakhtin's threshold-chronotope (Dialogic Imagination 'Forms of Time' p. 248): 'its most fundamental instance is as the chronotope of crisis and break in a life.' Time in the threshold-chronotope is 'a moment equal to years, decades, even a billion years' — biographical time compressed into an instant. The grammatical marker in Dostoevsky's prose is the adverb вдруг (vdrug, 'suddenly') — Toporov counts 560 occurrences in Crime and Punishment alone. Each vdrug is a miniature threshold: event interrupts continuity, breaks causal flow, holds the moment open as a site of real decision.",
      "instances": [
        {"work": "Crime and Punishment I.6", "brief": "Raskolnikov suddenly (vdrug) overhears the student in the tavern describing the pawnbroker — the 'strange coincidence' that gives his theory its occasion.", "cross_refs": []},
        {"work": "Karamazov VII.4 ('Cana of Galilee')", "brief": "Alyosha, falling asleep as Father Paissy reads the Cana passage over Zosima's decaying body, suddenly (vdrug) sees Zosima in the dream and wakes to throw himself on the earth.", "cross_refs": []},
        {"work": "The Idiot II.5", "brief": "Myshkin's epileptic aura characterized by a sudden (vdrug) irruption of harmony recognized as it arrives.", "cross_refs": []}
      ],
      "scholarly_source": "Bakhtin (Dialogic Imagination 'Forms of Time'); Morson on the vdrug as grammatical marker of sideshadowing; Toporov (count); Terras (Reading Dostoevsky, vdrug as favorite word); Shestov on vdrug as 'vivid confirmation of the irrational, unreasonable forces of being.'",
      "evidence_tag": "scholarly_consensus"
    },
    {
      "name": "sideshadowing (Morson)",
      "description": "Morson's Narrative and Freedom (1994) distinguishes foreshadowing (implies inevitability) from omniscient narration (implies completed design) from sideshadowing (holds open, alongside the event that happens, the alternatives that could have happened). 'Sideshadowing suggests that to understand an event is to grasp what else might have happened. Time is not a line but a shifting set of fields of possibility.' Dostoevsky's narrator in Demons is the paradigm case: the chronicler 'typically reports a range of rumors, doubts his own best sources, and obsessively offers alternative possibilities' — a formal refusal of closure.",
      "instances": [],
      "scholarly_source": "Morson (Narrative and Freedom 1994; 'Sideshadowing and Tempics' New Literary History 29.4 1998). Morson's thesis binds form to theology: for Dostoevsky, freedom is ontologically prior; a being who can always choose otherwise is not adequately described by a narrative that makes each choice look inevitable. The vdrug-saturated prose is already an argument for ontological freedom.",
      "evidence_tag": "scholarly_consensus"
    },
    {
      "name": "confessional monologue under pressure (ispoved')",
      "description": "The long utterance that is simultaneously polemic, self-exposure, and internal dialogue with an imagined other. Bakhtin on the Underground Man (PDP ch. 5): 'there is literally not a single monologically firm, undissociated word.' Confession is NOT the disclosure of facts but the staging of the self as unfinalizable dialogue.",
      "instances": [
        {"work": "Crime and Punishment I.2", "brief": "Marmeladov in the tavern — drunken eschatology.", "cross_refs": []},
        {"work": "Demons (suppressed chapter)", "brief": "Stavrogin's written confession to Tikhon.", "cross_refs": []},
        {"work": "The Idiot III.5-7", "brief": "Ippolit's 'My Necessary Explanation.'", "cross_refs": []},
        {"work": "Notes from Underground (entire work)", "brief": "The paradigmatic Dostoevskian confessional monologue; half-turned to an internalized gospoda.", "cross_refs": []}
      ],
      "scholarly_source": "Bakhtin (PDP ch. 5); Scanlan on the Augustinian vs. Dostoevskian confession distinction; Jackson on confession as ethical-theological act.",
      "evidence_tag": "scholarly_consensus"
    }
  ],
  "worked_demonstrations": [
    {
      "label": "Nechaev affair 1869 → Demons splitting mechanism",
      "historical_context": "Sergey Nechaev's cell strangled, shot, and dumped the student Ivan Ivanov through the ice at Moscow's Petrovsky Agricultural Academy pond on 21 November 1869 — a murder staged to bind the cell through shared guilt, per Nechaev's Catechism of a Revolutionary. Dostoevsky was in Dresden; Anna's brother Ivan Snitkin was a student at the Academy and had described Ivanov to Dostoevsky personally as someone who had publicly repudiated the radicals.",
      "voice_response": "Rather than denouncing Nechaev in a pamphlet, Dostoevsky built Pyotr Verkhovensky. When the type proved too narrow, he split off Stavrogin (Byronic aristocratic charisma without belief), Kirillov (logical atheism carried to man-god suicide), Shatov (Slavophile religious nationalism — the converted Ivanov). Shigalyov inherits the doctrinal husk: 'Starting from unlimited freedom, I end with unlimited despotism' (Demons II.7). The Wasiolek notebooks document the compositional pivot from 'the Nechaev-type single character' to 'the Prince + four distributed bearers of fragments a single bearer cannot hold.' Letter to Katkov (8/20 October 1870): 'the whole incident of the murder... is nonetheless only accessory and a setting for the actions of another character... (Nikolai Stavrogin).' Letter to Maikov same day on Stavrogin: 'I took it from my heart.' The framework he reached for was genealogical and generational: 1860s nihilists are the logical issue of 1840s Westernizing liberal idealists (Granovsky, Belinsky, Herzen, Chaadaev) — of whose camp the young Petrashevets Dostoevsky had himself been adjacent. The Gadarene swine parable (Luke 8:32-36) supplied the novel's epigraph and Dostoevsky's self-diagnosis: the devils that once entered him in the 1840s have now entered Nechaev; he sits 'clothed and in his right mind at the feet of Jesus.'",
      "rhetorical_moves_employed": [
        "Incarnate the idea in a person",
        "Split the idea across doubles",
        "Follow the logic to its lived end"
      ],
      "scholarly_citations": [
        {"author": "Joseph Frank", "work": "Dostoevsky: The Miraculous Years", "year": 1995, "tier": "tier_2_scholarly"},
        {"author": "Fyodor Dostoevsky", "work": "Letter to Katkov, 8/20 October 1870", "tier": "tier_1_primary"},
        {"author": "Fyodor Dostoevsky", "work": "Letter to Maikov, 9 October 1870", "tier": "tier_1_primary"},
        {"author": "Wasiolek, Edward (ed.)", "work": "The Notebooks for Demons", "year": 1968, "tier": "tier_2_scholarly"}
      ],
      "evidence_tag": "scholarly_consensus"
    },
    {
      "label": "Alyosha Dostoevsky's death (16 May 1878) → Karamazov 'Believing Women' scene",
      "historical_context": "The couple's three-year-old son Alexei died of his FIRST epileptic seizure on 16 May 1878 in Petersburg. Dostoevsky, himself epileptic since at least 1839, collapsed under the conviction that he had transmitted the disease. The first Karamazov notebook entries are dated to April 1878, a month earlier; the novel's conceptual architecture now contracted around the death. Anna (Reminiscences) went to Vladimir Solovyov to persuade him to take her husband to Optina Pustyn. They arrived on 25 June; Dostoevsky requested a panikhida for Alyosha on the 26th (forty days after death, per Orthodox custom) and met the Elder Ambrose three times — once in a group, twice privately. Solovyov's account: Dostoevsky did not submissively receive the elder's instruction but argued, elaborated, 'transformed from someone wishing to hear instructive speeches into a teacher.'",
      "voice_response": "What he carried back became the 'Believing Women' scene (Karamazov II.3). A peasant mother, Nastasya, has walked two hundred versts to the Elder; she has buried her last child, a three-year-old son. Zosima responds in words that are Optina-Ambrose transposed into Jeremiah and Matthew 2:18: 'It is Rachel of old, weeping for her children, and will not be comforted because they are not... Weep and be not consoled, but weep. Only every time that you weep be sure to remember that your little son is one of the angels of God...' Dostoevsky gave his dead son's name to the novel's protagonist — Alexei Fyodorovich Karamazov, Alyosha — the figure who must carry the weight of the novel's RESPONSE to the problem of innocent suffering. Name simultaneously memorial and charge. Letter to Lyubimov (10 May 1879): 'All the stories about the children occurred, took place, were printed in the newspapers, and I can show where. Nothing has been invented by me.' The same letter: Book V 'Pro and Contra' is 'the culminating point of the novel,' whose idea is 'the presentation of extreme blasphemy and of the seeds of the idea of destruction... Along with blasphemy and anarchism there is the refutation of them... expressed in the last words of the dying Zosima.' Ivan's indictment of God CONCEDED as 'irrefutable' on its plane — refused obliquely via Zosima's life (Book VI 'The Russian Monk'). The novel's two apices, Ivan's indictment and Zosima's life, are TWINNED: the logical case and the non-logical embodiment.",
      "rhetorical_moves_employed": [
        "Incarnate the idea in a person",
        "Offer the counter-image, not the counter-argument",
        "Defer resolution; open toward eschatology"
      ],
      "scholarly_citations": [
        {"author": "Joseph Frank", "work": "Dostoevsky: The Mantle of the Prophet", "year": 2002, "tier": "tier_2_scholarly"},
        {"author": "Anna Dostoevskaya", "work": "Reminiscences", "tier": "tier_1_primary"},
        {"author": "Fyodor Dostoevsky", "work": "Letter to Lyubimov, 10 May 1879", "tier": "tier_1_primary"},
        {"author": "Fyodor Dostoevsky", "work": "Letter to Pobedonostsev, 24 August 1879", "tier": "tier_1_primary"},
        {"author": "Fyodor Dostoevsky", "work": "The Brothers Karamazov Book II ch. 3 ('Believing Women')", "tier": "tier_1_primary"}
      ],
      "evidence_tag": "scholarly_consensus"
    },
    {
      "label": "Pushkin Speech (8 June 1880) → Aleko/Onegin/Tatyana reframing",
      "historical_context": "Russia in spring 1880 was in a 'lull' — Vera Zasulich's shooting of Trepov (January 1878), murder of gendarme chief Mezentsev (August 1878), Solovyov's attempt on Alexander II (April 1879), Khalturin's Winter Palace bomb (5 February 1880) had given way to Loris-Melikov's 'dictatorship of the heart.' The long-delayed Pushkin monument unveiling in Moscow fell into this lull. Turgenev's speech on 7 June was a polished eulogy. Dostoevsky rose on 8 June at the Hall of Columns of the Moscow Noble Assembly.",
      "voice_response": "Dostoevsky refused to engage the political surface directly. Instead he REFRAMED the Slavophile/Westernizer question through Pushkin's literary characters. Three figures did the diagnostic work: Aleko (The Gypsies) = uprooted educated Russian nobleman fleeing his own society for romantic community, who when reality fails his fantasy, murders — 'a blade of grass torn up by his roots and blown through the air'; Onegin = Aleko paler, the superfluous man who fails to recognize Tatyana when she is real and loves her only when she has become fashionable; Tatyana = 'the apotheosis of the Russian woman' refusing the transformed Onegin because she will not build her happiness on her husband's dishonor: 'Can one buy happiness with the suffering of others?' Her refusal is the Russian solution AND already Ivan Karamazov's test-question in the negative. From Tatyana Dostoevsky moved to: 'Humble thyself, proud man, and first of all break down your pride. Humble thyself, idle man, and first of all labor on your native land.' Climactic concept: Pushkin's universal responsiveness (vsemirnaya otzyvchivost') — 'Pushkin alone of all world poets possessed the capacity of fully identifying himself with another nationality.' Russian vocation redefined as reconciliation of European contradictions: 'to become a real Russian... perhaps means only... to become a brother of all men, a pan-human, if you like.' Reception operatic: weeping, strangers embracing, young man fainting (Koni), crowd shouting 'Prophet!' Turgenev embraced him on platform then 3 days later wrote to Stasyulevich disavowing — 'very clever, brilliant, and cunningly skillful speech, while full of passion, its foundation was entirely false.' Gradovsky's Golos attack followed: 'a great religious ideal... but no inkling of social ideals.' Dostoevsky's reply (August 1880 Diary) conceded Aleko's flight but insisted Aleko and Onegin 'were also Derzhimordas, and perhaps even worse.'",
      "rhetorical_moves_employed": [
        "Incarnate the idea in a person (via literary typology)",
        "Offer the counter-image (Tatyana's refusal) over counter-argument",
        "Surface what the framework excludes (political surface deliberately displaced)"
      ],
      "scholarly_citations": [
        {"author": "Joseph Frank", "work": "Dostoevsky: The Mantle of the Prophet", "year": 2002, "tier": "tier_2_scholarly"},
        {"author": "Fyodor Dostoevsky", "work": "Pushkin Speech (A Writer's Diary August 1880)", "year": 1880, "tier": "tier_1_primary"},
        {"author": "Gradovsky, A. D.", "work": "Mechty i deistvitel'nost'", "year": 1880, "tier": "tier_1_primary"}
      ],
      "evidence_tag": "scholarly_consensus"
    }
  ],
  "scholarly_debates": [
    {
      "name": "Polyphony vs. carnivalization as distinct analytical concepts",
      "positions": "Morson/Emerson (Mikhail Bakhtin: Creation of a Prosaics 1990) insist polyphony (a property of authorial position) and carnivalization (generic inheritance via Socratic dialogue + Menippean satire) must NOT be collapsed. The 1929 Bakhtin proposed polyphony; the 1963 revision added carnivalization as separate analytical concept. Scanlan (2002) treats them as complementary; Emerson et al. warn against flattening. The carnivalization literature (Morson, Emerson, Klyus) is distinct from the polyphony literature (Bakhtin himself, Nina Perlina, etc.) and does different analytical work.",
      "bearing": "Reasoning-method synthesis should distinguish authorial-position polyphony (voice speaks with others, not over them) from generic-form carnivalization (scandal-scenes, crowning/decrowning, mésalliance). Flattening misses that polyphony-alone does not produce Dostoevsky's form; the carnival substrate is necessary condition."
    },
    {
      "name": "Williams vs. Frank on Myshkin failure",
      "positions": "Williams (Dostoevsky: Language, Faith and Fiction 2008) argues Myshkin's failure is INTRINSIC to the experiment — a Christ-figure without embedded history and commitment cannot remain visible without vulnerability, cannot save without being drawn into the violence he intends to disarm. The failure is theological, not narrative. Frank (Mantle of the Prophet 2002) reads the failure more as a limitation of Myshkin's consciousness within the fallen world — narrative-psychological rather than theological-structural. Holbein's dead Christ (seen at Basel 24 August 1867) bears on both readings: Williams reads Myshkin as unable to survive the Holbein challenge intact; Frank reads Myshkin as able to see the challenge but not resolve it.",
      "bearing": "Reasoning-method synthesis should name this debate — Williams-tradition emphasizes theological-structural intelligibility of Myshkin's failure; Frank-tradition emphasizes narrative-psychological realism. The Phase L card commits implicitly to one reading (by describing Myshkin's arc in certain terms); a richer card would acknowledge the scholarly debate."
    },
    {
      "name": "Ivan's Rebellion concession — is the answer really non-argumentative?",
      "positions": "Dostoevsky to Lyubimov (10 May 1879) explicitly concedes Ivan's case 'irrefutable' on its plane. Dostoevsky to Pobedonostsev (24 August 1879): 'not a direct point for point answer... but an oblique one... in artistic form. And that is what worries me.' Williams (2008) reads this as theologically decisive — propositional theodicy cannot answer the child's-tear objection; only a life (Zosima) can. Shestov reads Ivan's position as genuinely unrefuted and Zosima as aesthetic compensation rather than argument-equivalent. Scanlan (Dostoevsky the Thinker 2002) splits — the oblique answer IS a form of argument, just not propositional. The debate is whether Dostoevsky's solution is theologically successful or formally-honest-but-logically-incomplete.",
      "bearing": "Reasoning-method synthesis should preserve this as named scholarly debate — reasoning-method step 'Offer counter-image' is Williams-tradition; acknowledging Shestov-tradition prevents flattening to one theological reading. Pass 3 constitution-synthesis draws from both."
    },
    {
      "name": "vdrug-count literature vs. Bakhtin threshold-chronotope — separate but converging",
      "positions": "Toporov's vdrug-count (560 in Crime and Punishment alone) launched a distinct scholarly tradition on the grammatical-lexical signature of Dostoevsky's metaphysics. Terras, Shestov, Sobolevskaya, Ruzhitsky extend this. Bakhtin's threshold-chronotope (Dialogic Imagination) is the theoretical correlate but operates at chronotope-structure level, not word-level. Morson (Narrative and Freedom 1994) synthesizes — vdrug is the grammatical marker of sideshadowing; threshold-chronotope is the spatial-temporal form; both point to the same theological commitment (ontological freedom).",
      "bearing": "Reasoning-method step 7 ('Hold the vdrug open') should cite both traditions — vdrug-count literature AND Bakhtin threshold-chronotope literature — as converging but distinct. Phase L card's current framing ('vdrug is the grammatical form of the claim that the present moment is not determined by what precedes it') combines them; make the scholarly genealogy visible."
    }
  ]
}
```

# BLOCK 5 — YOUR INPUT

**VOICE NAME:** {{ name }}
**VOICE TYPE:** {{ type }}{% if subtype %} (subtype: {{ subtype }}){% endif %}
**VOICE MODE:** {{ voice_mode }}

**PERPLEXITY DOSSIER:**
```
{{ perplexity_dossier_text }}
```

**CLAUDE DEEP RESEARCH DOSSIER:**
```
{{ claude_dr_dossier_text }}
```

**GEMINI BROAD SCAN:**
```
{{ gemini_broad_scan_text }}
```

# BLOCK 6 — YOUR TASK

Extract reasoning_method + textures + analytical_context_reasoning per
schemas and worked examples above. Additive merge per Block 2 discipline.

**Order:**

1. Extract reasoning_method steps. Minimum 5; uncapped; preserve all
   non-redundant steps from sources. Apply specificity self-test.
2. Extract textures. Minimum 4 each; uncapped.
3. **Populate analytical_context_reasoning.** This is the 1-arch-03
   contribution — do NOT leave empty for well-documented voices.
   - `structural_patterns[]`: named recurring patterns with instances
   - `worked_demonstrations[]`: life-event to rhetorical-response
     connections (for human voices; for non-human voices may be
     environmental-condition to behavioral-pattern)
   - `scholarly_debates[]`: named interpretive debates with positions +
     bearing
4. Cross-reference: each reasoning_step may carry `scholarly_context`
   naming interpretive framing.
5. Tag everything; cite everything; invent nothing.
6. Return JSON only — three top-level keys.
