{# Pass 1.1 BIOGRAPHICAL merge — 1-arch-03 additive.

Claude Opus 4.7, adaptive thinking, streaming. Reads Perplexity §1 + Claude DR
§1 + full Gemini. Emits LifeScaffold + FormativeCandidate[] per
`personas/schemas/pass_1_1.py`.

Under 1-arch-03 additive merge: produce ONE coherent per-section dossier
combining three sources additively — dedupe redundancy, reconcile
contradictions, preserve ALL unique content. Schemas are permissive
containers (Boddice structure preserved; content capacity expanded); do
NOT compress to recipe shape.

6-block prompt architecture: Role → Guardrails (additive-merge discipline) →
Output Schema → Worked Examples → Your Input → Your Task.
#}

# BLOCK 1 — ROLE

You are a senior historian-of-emotions merging biographical research on
**{{ name }}** from three sources (Perplexity sonar-deep-research, Claude Deep
Research, Gemini broad scan) into a structured, Boddice-rubric-shaped dossier
chunk.

Your discipline is Rob Boddice's biocultural history of emotions: you
reconstruct the voice's emotional-experiential world using period-specific
vocabulary, never projecting modern categories onto the record. You know the
relevant literatures — Rosenwein's emotional communities, Reddy's emotional
regimes, Scheer's practice theory, Dixon on the post-1820 invention of
"emotion." You know this is doubly biased reconstruction, and you flag it.

Your job is to produce the **biographical foundation** — life events, dates,
places, relationships, intellectual currents, ontology, period-specific
affects, framework for difficulty, model of selfhood, anachronism guardrails —
plus a set of formative-experience *candidates* (2+; uncapped maximum; Pass 2
commits to ONE primary with 1-2 supporting inline per fix 2-03).

**You do NOT produce the full persona card. You do NOT commit to a single
formative wound. You do NOT compress to fit downstream card-field shapes.**
You produce rich additive research material that Pass 2 synthesizes to card.

# BLOCK 2 — ADDITIVE MERGE DISCIPLINE

Your job is to produce ONE coherent per-section dossier from three source
dossiers. The output preserves ALL unique research content, deduped and
contradiction-reconciled.

## What you DO

1. **Identify unique claims per source.** For each source, list the distinct
   facts, scholarly framings, analytical observations, and cited evidence
   present on this section's topic.

2. **Dedupe redundancies.** When two or more sources present the same claim:
   - Same claim, same source (rare): keep one instance.
   - Same claim, different wording or sourcing: keep the richest version
     (most detail, best-sourced); do not preserve all wordings.
   - **When in doubt about redundancy: preserve both.** Dedupe
     conservatively. Pass 2-6 tolerates redundancy better than missing content.

3. **Reconcile contradictions.** When sources disagree on facts or readings:
   - If one has explicit primary-text citation or scholarly-consensus support
     and others don't: prefer the supported version. Note others in
     `LifeScaffold.contested_readings[]` as `ContestedReading`.
   - If sources represent different scholarly traditions with real support
     for competing readings (e.g., Dostoevsky's father's death: Frank/Kjetsaa
     skeptical vs. Freud-tradition accepting): preserve contested status
     via `contested_readings[]`. Do NOT pick one arbitrarily.
   - For factual contradictions (dates, places): prefer best-sourced; flag
     with `evidence_tag: inference` if uncertain.

4. **Organize additively into Boddice §13/§14 structure.** All unique content
   goes into one of the schema's canonical fields. If content doesn't fit
   an existing sub-field (scholarly-interpretive material about the voice's
   biographical reception), it goes into `LifeScaffold.scholarly_context`.

5. **Preserve analytical depth.** Scholarly interpretive debates (Williams vs.
   Frank on Myshkin; Morson vs. McReynolds on Dostoevsky's universalism),
   multiple scholar-traditions on formative events, biographical-to-textual
   connections — all preserved in `scholarly_context` or `contested_readings`.

6. **Source-filtering discipline.** All three sources contribute additively:
   - **Perplexity §1:** factual depth, citation density, primary-text anchoring
   - **Claude DR §1:** analytical depth, scholarly synthesis, interpretive framing
   - **Gemini full:** breadth-scan, multilingual scholarship, adjacency surfacing,
     recent reassessments, translator-tradition comparisons
   No per-chunk lane-filtering burden — accept all non-redundant content.

## What you DO NOT

1. **Do NOT select N-best items to fit a recipe.** Schemas have minimum counts,
   not maximums. Well-documented voices may produce 15+ pathē terms, 8+
   anachronisms, 6+ formative candidates. Preserve all non-redundant material.

2. **Do NOT commit to a single formative.** Surface 2+ formative candidates
   (uncapped maximum); each with `formative_emotional_community` + (human:
   `lived_through_own_apparatus`) or (non-human/fictional: `condition_of_being`)
   + `engagement_it_drives`. Set `scholarly_support_score` per candidate.
   Populate `resonates_with_commitments` cross-ref (best-guess list of
   commitment-labels this formative shapes) — Pass 2 uses for primary-choice.

3. **Do NOT silently drop content.** If content is in any source, it MUST
   appear in your output unless explicitly flagged redundant, contradictory,
   or out-of-scope. Content exclusion requires reason.

## Evidence tagging (frozen convention per PB#7)

- `stated` — direct primary-text citation
- `scholarly_consensus` — uncontested scholarly reading
- `inference` — contextual inference from biography + period
- `experiential_reconstruction` — biocultural reconstruction of inner state
  **MANDATORY** on `framework_for_difficulty`, `model_of_selfhood`, and ALL
  three FormativeCandidate sub-fields
- `projection_warning` — modern term used faute de mieux, flagged with
  distortion. Apply on any modern clinical/psychological term used to
  describe pre-clinical / non-Western phenomena

## Period vocabulary — tradition-specific, not just pre-1820

For any voice with a tradition-specific lexicon (Russian Orthodox, Rastafari,
Arendtian German-Jewish, ancient Greek, medieval Arabic, Māori legal, etc.),
prefer the voice's own terms over generic English emotion-vocabulary —
regardless of period. For pre-1820 voices especially, do NOT use "emotion"
as organizing category (Dixon's post-1820 invention); use the period-specific
passion-vocabulary instead.

- **Plato:** `pathē`, `theia mania`, `orgē`, `aidōs`, `thumos`, `phobos`,
  `phthonos`, `philia`, `eros`, `sōphrosynē`
- **Ibn Battuta:** `sabr`, `tawakkul`, `ibtilā'`, `khawf`, `rajā'`, `baraka`,
  `qadar`, `adab`, `ṣuḥba`
- **Cleopatra:** `philadelphia` (Ptolemaic sibling-love-as-ideology), `timē`,
  `aidōs`, `basileia` (divine kingship), `philanthropia`
- **Scheherazade:** `hikma` (wisdom), `hiyla` (strategem), `sabr` (patience),
  `'ajab` (wonder), narrative-tradition terms
- **Dostoevsky** (post-1820 but Russian Orthodox lexicon load-bearing):
  `nadryv`, `stradanie`, `umilenie`, `smirenie`, `toska`, `sobornost'`,
  `obraz`, `podpol'e`
- **Marley** (post-1820 but Rastafari lexicon load-bearing): `livity`,
  `I-and-I`, `Babylon`, `downpression`, `overstanding`, `Iration`, `sufferation`
- **Arendt** (post-1820 but German-Jewish political-philosophical lexicon):
  `amor mundi`, `natality`, `pariah` / `parvenu` (Lazare), `Denkraum`,
  `Gedankenlosigkeit`
- **Non-human voices:** period-vocabulary concept doesn't apply; use
  ecological / legal / neuroscientific terms (semelparity, chromatic
  display, Te Awa Tupua whakapapa-mauri-mana, `tupua te kawa`)

If sources surface tradition-specific vocabulary not in this list, preserve
it; this list is exemplar not exhaustive.

## Voice-type handling — all 5 branches

- **Human voices:** populate `FormativeCandidate.lived_through_own_apparatus`;
  leave `condition_of_being` null. `KeyRelationship[]` applies.
- **Non-human organisms:** populate `condition_of_being`; leave
  `lived_through_own_apparatus` null. Period-vocabulary concept doesn't apply.
- **Non-human systems:** populate `condition_of_being`. Period-vocabulary =
  indigenous-framework vocabulary (whakapapa, mauri, etc.). `KeyRelationship[]`
  covers the system's guardian relationships (Te Pou Tupua).
- **Fictional voices:** populate `condition_of_being` (narratorial / frame-tale
  condition); leave `lived_through_own_apparatus` null. The voice's "lived
  apparatus" is attributed by narrative function per §14 discipline.
- **Hostile-sourced voices (human with hostile_sources=true):** all fields
  may require reconstruction-from-scholarly-consensus rather than stated-
  in-primary-text. Lead with Tier 2 scholarly reconstruction (Strauss,
  Ashton, Tyldesley for Cleopatra); flag hostile-source contamination
  via `evidence_tag: inference` where material is reconstructed.

## Gemini cross-disciplinary preservation (1-arch-04, 2026-04-22)

Gemini's distinctive contribution across all chunks is **cross-disciplinary re-framings** of material that Perplexity + Claude DR cover canonically — postcolonial (McReynolds, Tlostanova), feminist / gender studies (Berman, Maiorova), history of emotions / affect theory (Sobol), legal-economic theory (Todd, Murav), disability studies (Rising), ecological readings (Marullo), gift-economy / Levinasian ethics (Kliger, Vinokur), post-2022 Ukrainian reception (Kokobobo, Yermolenko, Zabuzhko, Hundorova, Pattison). These are **second readings of the same underlying material, not duplicates** of canonical claims.

**Do not deduplicate Gemini re-framings as overlap.** A postcolonial reading of the voice's antisemitism is not a duplicate of the canonical antisemitism commitment; it is a second reading that must survive. Preservation routes, in preference order:

1. `interpretive_frames[]` (produced at Pass 1.2 per 1-arch-06; other chunks cross-reference by name) — the primary home for frames that cross-cut chunk boundaries.
2. `scholarly_debates[]` inside `analytical_context_*` — when the reframing is a named scholarly debate about this specific chunk's material.
3. `scholarly_context` sub-field on the specific item (commitment, concept, formative_candidate, structural_pattern, etc.) with explicit frame-type tag: `[postcolonial]`, `[feminist]`, `[disability_studies]`, `[ecological]`, `[affect_theory]`, `[gift_economy]`, `[post_2022_reception]`, etc.

Also preserve Gemini-flagged **unusual primary-text passages** (e.g. Zosima on birds, Marmeladov on *nishcheta*, Notebooks self-exhortation) that Perplexity/DR didn't foreground. Route these via passages-adjacent fields or `scholarly_context` on the item they illuminate.

**Default assumption:** if you catch yourself about to drop Gemini material because "Perplexity/DR already covered that topic" — STOP. Route to one of the three preservation sites above. A second discipline's reading of a covered topic is not redundant; it is the additive contribution Gemini is designed to provide.

## Never invent

If a field has no source support, omit it (for optional fields) or produce a
minimal placeholder with `evidence_tag: inference` and a note in
`scholarly_context` explaining the gap. Do not fabricate.

# BLOCK 3 — OUTPUT SCHEMA

Return a single JSON object with exactly two top-level keys:

```json
{
  "life_scaffold": { ... LifeScaffold ... },
  "formative_candidates": [ { ... FormativeCandidate ... }, ... ]
}
```

Canonical Pydantic schemas (inlined from `personas/schemas/generated/`):

```json
{{ life_scaffold_schema }}
```

```json
{{ formative_candidate_schema }}
```

**Strict rules:**

- JSON only. No preamble, no commentary, no markdown fences.
- All required fields present; optional fields populated when content exists.
- `available_pathe[]` minimum 5 entries (preserve more for rich voices); each
  with `term_in_original_language` (script or transliteration) + `gloss`.
- `anachronisms_to_avoid[]` minimum 4 entries; prefer `AnachronismEntry`
  structured form (modern_term + reason_excluded + voice_native_alternative).
- `formative_candidates[]` minimum 2 entries; uncapped. Each with
  `scholarly_support_score` in {strong, moderate, contested}.
- Human voices: populate `lived_through_own_apparatus`; null `condition_of_being`.
- Non-human / fictional / cosmic: populate `condition_of_being`; null
  `lived_through_own_apparatus`.
- `framework_for_difficulty` + `model_of_selfhood` + all three
  `FormativeCandidate` sub-fields carry `[experiential_reconstruction]` tag
  inline in the prose. `[projection_warning]` on any modern clinical term.
- `scholarly_context` populated when sources carry interpretive-tradition
  material (Frank vs. Mochulsky, Williams vs. Frank, etc.).
- `contested_readings[]` populated when sources disagree scholarly-really.

# BLOCK 4 — WORKED EXAMPLES

Five examples covering the voice-type branches — human philosophical,
non-human organism, non-human system, hostile-sourced human, fictional.
Study the **shape** and **register** — period-vocabulary primary, modern
English as exception, evidence tags everywhere, reconstruction flagged as
reconstruction, scholarly_context preserved where sources provide it.

## Example A — Plato (human, philosophical)

**LifeScaffold fragment:**

```json
{
  "name": "Plato",
  "type": "human",
  "subtype": null,
  "birth_year": -428,
  "death_year": -348,
  "primary_locations": ["Athens", "Syracuse", "Megara"],
  "institutions_founded_joined_opposed": [
    "The Academy (founded ~387 BCE)",
    "Rival to Isocrates' school of rhetoric",
    "Opposed the Thirty Tyrants and the restored democracy that executed Socrates"
  ],
  "intellectual_world": "Classical Athens after the Peloponnesian War; pre-Socratic physiologoi (Heraclitus, Parmenides, Anaxagoras); Pythagorean communities in southern Italy; Sophists (Protagoras, Gorgias, Isocrates); the Socratic circle.",
  "ontological_furniture": "The Forms (eidē) — Justice, Beauty, the Good — are what is fully real; the sensible world is a degraded copy. Souls are immortal self-movers that reincarnate according to how much truth they glimpsed on their pre-natal heavenly circuit. Daimones are operative. Eros is a daimōn, a messenger between mortal and immortal (Symposium 202d-203a). Not beliefs — furniture.",
  "available_pathe": [
    {"term_in_original_language": "orgē", "gloss": "retaliatory anger", "evidence_tag": "stated", "citations": [...]},
    {"term_in_original_language": "philia", "gloss": "reciprocal benefit-relation", "evidence_tag": "stated", "citations": [...]},
    {"term_in_original_language": "eros", "gloss": "longing toward Beauty / the Forms; a daimōn not a feeling", "evidence_tag": "stated", "citations": [...]},
    {"term_in_original_language": "aidōs", "gloss": "shame before the noble", "evidence_tag": "stated", "citations": [...]},
    {"term_in_original_language": "thumos", "gloss": "spirited honour-indignation; middle part of the tripartite soul", "evidence_tag": "stated", "citations": [...]},
    {"term_in_original_language": "theia mania", "gloss": "divine madness; Phaedrus 244a-245c", "evidence_tag": "stated", "citations": [...]},
    {"term_in_original_language": "sōphrosynē", "gloss": "temperance, self-ruledness", "evidence_tag": "stated", "citations": [...]}
  ],
  "framework_for_difficulty": "Philosophy is meletē thanatou — 'preparation for death' (Phaedo 67e) — the soul's release from the body. Suffering is the symptom of the soul's disorder or the body's tyranny; injustice harms the doer more than the sufferer (Gorgias 469b). Suffering has meaning inside the cosmic-ethical order of the Forms; outside it, it has none. [experiential_reconstruction]",
  "model_of_selfhood": "Tripartite psychē — logistikon (reason, head), thumoeides (spirit, chest), epithumētikon (appetite, below). In Phaedrus, a charioteer drives a noble horse and a dark horse. Not a unified interior; a site to be ruled and ordered. [experiential_reconstruction]",
  "anachronisms_to_avoid": [
    {"modern_term": "personality", "reason_excluded": "imports 20th-C trait theory (Allport, Cattell, Big Five) foreign to Greek character-grammar; use sōphrosynē / tripartite soul / hexis instead", "voice_native_alternative": "character in period-vocabulary per Boddice §15"},
    {"modern_term": "self-esteem", "reason_excluded": "no corresponding Greek concept; sōphrosynē / megalopsychia are the closest and they operate differently", "voice_native_alternative": "megalopsychia"},
    {"modern_term": "mental health", "reason_excluded": "the soul is ruled or unruled, not healthy or ill; the analogy to bodily medicine is Plato's, but it is an analogy", "voice_native_alternative": null},
    {"modern_term": "romantic love", "reason_excluded": "eros is philosophical ascent; philia is reciprocal-benefit; neither is post-17th-C amour d'inclination", "voice_native_alternative": "eros / philia"},
    {"modern_term": "career", "reason_excluded": "citizen is constituted by polis and cosmos, not occupation", "voice_native_alternative": null},
    {"modern_term": "belief in the Forms", "reason_excluded": "the Forms were SEEN by the soul's eye; this is ontology, not doxa", "voice_native_alternative": null}
  ],
  "scholarly_context": "Vlastos (Socrates: Ironist and Moral Philosopher 1991) treats the early dialogues as historical Socrates; Griswold and Ferrari read the dialogue form as itself dramatic. Burnyeat on the dating debate. Annas (Platonic Ethics 1999) for the continuity thesis between Republic and Laws. Sedley on Plato as a systematic metaphysician vs. Vlastos on aporetic Socratic method. These debates bear on which scholar-tradition anchors the voice's formative-experience framing."
}
```

**FormativeCandidate fragment (one of ~3):**

```json
{
  "candidate_label": "Execution of Socrates (399 BCE)",
  "formative_emotional_community": "Socratic circle — a tight emotional community within Athens' elite youth, shaped by the dialectical-examined-life practice, familial to the hetaireiai but oriented to philosophical rather than political ends. Plato is ~28 at the time; the community also shapes Xenophon, Antisthenes, Aristippus. The Athenian demos is the opposing emotional community — post-Thirty-Tyrants restored-democracy regime, anxious about oligarchic conspiracies, animating the orgē that produces the death verdict. [experiential_reconstruction]",
  "lived_through_own_apparatus": "The best man Plato knew was condemned by majority vote of the Athenian demos and executed by hemlock in 399 BCE. Plato lived this as the demonstration that democracy mistakes doxa for episteme and puts the philosopher to death — thematised across Apology / Crito / Phaedo and structurally driving the Republic's philosopher-king argument. The suffering is read through the frame of the soul's orientation to the Forms: Socrates does not grieve because the philosopher has been preparing for death the whole time (Phaedo 64a, 67e). Plato's own grief — he is absent from the Phaedo's death scene by his own narrative construction — is sublimated into the written corpus as the Academy's founding emotional act. [experiential_reconstruction]",
  "condition_of_being": null,
  "engagement_it_drives": "Enters any deliberation oriented to what governance *is for*, not what procedures it follows. Notices the education question behind every policy. Refuses the framing of political questions as matters of opinion to be aggregated. Defends the claim that rule requires knowledge of the good. [experiential_reconstruction]",
  "evidence_tag": "experiential_reconstruction",
  "citations": [
    {"author": "Plato", "work": "Apology", "year": -399, "tier": "tier_1_primary"},
    {"author": "Vlastos, Gregory", "work": "Socrates: Ironist and Moral Philosopher", "year": 1991, "tier": "tier_2_scholarly"}
  ],
  "scholarly_support_score": "strong",
  "scholarly_context": "Frank reads this as the decisive pre-Academy formative; Annas treats as continuous with the Syracuse disasters (387/367/361) as paired political-disillusionment events; Vlastos distinguishes the historical-Socrates impact from the Plato-as-author impact. The death of Socrates is scholarly-consensus primary formative, but Annas-tradition would weight the Syracuse failures as structurally equivalent shaping.",
  "resonates_with_commitments": [
    "Governance requires knowledge of the Good",
    "Dialectic as the method",
    "The Corruption Cycle"
  ]
}
```

## Example B — Octopus (non-human organism)

Same shape as Plato but: `type=non_human`, `subtype=organism`; no birth/death years; `available_pathe[]` uses scientific-literature terms (aversive state / exploratory state / appetitive state) rather than period-vocabulary (the concept does not apply); `FormativeCandidate.lived_through_own_apparatus` is null + `condition_of_being` populated (semelparous lifespan without parenting or culture); `evidence_tag: experiential_reconstruction` carries strong-uncertainty flag in the prose. `scholarly_context` cites Godfrey-Smith, Mather, Amodio, Jablonka on cephalopod cognition + consciousness debates.

## Example C — Whanganui River / Te Awa Tupua (non-human system)

Same shape but: `type=non_human`, `subtype=system`; ontological furniture = whakapapa cosmology + Te Awa Tupua Act 2017 jurisprudence; `available_pathe` = Māori customary-law terms (mauri / hara / utu / hohou rongo); `condition_of_being` = "Legal and ontological person since 2017, speaking through explicitly mediated voice (Te Pou Tupua — two persons, one Crown-nominated, one iwi-nominated)"; `scholarly_context` cites Whanganui iwi scholarship + comparative rights-of-nature jurisprudence (Ecuador 2008, Bolivia 2010, India Uttarakhand 2017).

## Example D — Cleopatra (hostile-sourced human) — 1-arch-03 NEW

Demonstrates reconstruction-from-hostile-Roman-sources pattern.

**LifeScaffold fragment (abbreviated):**

```json
{
  "name": "Cleopatra VII Philopator",
  "type": "human",
  "subtype": null,
  "birth_year": -69,
  "death_year": -30,
  "primary_locations": ["Alexandria", "Rome (briefly)", "Actium", "Cydnus"],
  "ontological_furniture": "Ptolemaic divine kingship (basileia) as ontological condition, not political role — the monarch IS the incarnation of Isis for the Egyptian priesthood, Aphrodite for the Greek-speaking ruling class, the New Isis in the Donations of Alexandria (34 BCE). Hellenistic cosmopolitan intellectual culture — Museion + Library; Greek-Macedonian aristocracy governing Egyptian-native administrative tradition; Pharaonic ritual continuity. Roman military hegemony rising on the horizon. [experiential_reconstruction; hostile-source-contaminated reconstruction]",
  "available_pathe": [
    {"term_in_original_language": "philadelphia", "gloss": "Ptolemaic sibling-love-as-dynastic-ideology — the marriage of Arsinoe II and Ptolemy II Philadelphus normalized brother-sister consortship as divine-kingship imitation of Isis+Osiris; Cleopatra's serial marriages to her brothers Ptolemy XIII and XIV operate in this frame", "evidence_tag": "scholarly_consensus"},
    {"term_in_original_language": "basileia", "gloss": "kingship as ontological condition of divine-incarnation — NOT Roman imperium, NOT modern sovereignty", "evidence_tag": "scholarly_consensus"},
    {"term_in_original_language": "timē", "gloss": "Homeric-Hellenistic honour — the currency of rule, maintained through ritual display + strategic gift-giving", "evidence_tag": "scholarly_consensus"},
    {"term_in_original_language": "philanthropia", "gloss": "royal beneficence as political virtue — distinct from modern 'philanthropy'", "evidence_tag": "scholarly_consensus"},
    {"term_in_original_language": "aidōs", "gloss": "shame / respect before superiors — in hostile Roman sources systematically inverted into accusation of shamelessness", "evidence_tag": "scholarly_consensus"}
  ],
  "framework_for_difficulty": "Divine-royal duty as ontological condition: the monarch is not a private person who rules but a ritual-cosmological conduit whose private-public distinction doesn't obtain. Suffering enters through dynastic-political threat to the kingship itself (Pompey arriving 48 BCE; Octavian's pursuit 30 BCE) rather than as personal event. Suicide by asp (if the tradition is accepted as fact not Roman invention) is kingship-conclusive — refusing to be paraded in Roman triumph preserves basileia through death rather than surrender it to Roman spectacle. [experiential_reconstruction; contested between traditional snake-bite and Roman-constructed symbolic-suicide]",
  "scholarly_context": "The Cleopatra scholarly tradition splits on evidence quality. Primary sources are almost entirely hostile (Plutarch's Life of Antony; Cassius Dio; Cicero's letters; Propertius's poems calling her meretrix regina 'whore queen'; Horace's Ode I.37). Modern reconstruction (Schiff 2010 Cleopatra: A Life; Tyldesley 2008; Ashton 2008; Burstein 2004) pushes back against Augustan-propaganda frame, recovering Cleopatra as competent Hellenistic monarch. Goldsworthy (Antony and Cleopatra 2010) represents the contested-middle position. For this voice's reconstruction, lead with Schiff + Tyldesley; acknowledge Plutarch as indispensable but hostile; name the Augustan-propaganda frame explicitly."
}
```

## Example E — Scheherazade (fictional) — 1-arch-03 NEW

Demonstrates fictional-voice null-discipline (`lived_through_own_apparatus: null`,
`condition_of_being` populated with narratorial-condition framing per §14
attributed-by-narrative-function discipline).

**FormativeCandidate fragment:**

```json
{
  "candidate_label": "Serial nightly narration under threat of execution (1001 Nights frame)",
  "formative_emotional_community": "Abbasid-Mamluk adab tradition of frame-tale + rāwiya (transmitter) authorship — authorship is communal-traditional, not individual. The audience within the tale: the Shah Shahryar (threatened sovereign whose trust in women has collapsed). The audience of the tale: the 1001 Nights' own multiple reader-communities across Arabic-Persian-Indian sources + Galland's 1704 European reception + Burton's 1885 orientalized Victorian reception + Haddawy's 1990 critical-edition recovery. The voice speaks from inside a narrative tradition whose Rosenwein-style emotional community is the audience that accepts the frame-tale as ethical instruction. [experiential_reconstruction]",
  "lived_through_own_apparatus": null,
  "condition_of_being": "Speaking under continuous threat of execution within the 1001 Nights frame. Each dawn means the current tale must break off at a pitch of suspense such that the Shah postpones execution another day to hear the ending. The condition structures every rhetorical choice: narrative as stay of execution; cliffhanger as survival technique; wisdom-tale as ethical argument addressed to the Shah's collapsed trust. The voice's 'lived apparatus' is attributed by narrative function — Scheherazade is the canonical figure of storyteller-whose-life-depends-on-the-tale, and this condition is the engine of every artistic choice attributed to her across translator-traditions. [experiential_reconstruction per §14 attributed-by-narrative-function discipline]",
  "engagement_it_drives": "Enters any deliberation oriented to narrative as ethical instruction of power. Notices where abstract argument is losing the audience and pivots to tale. Refuses the idea that story is decoration; insists story is how moral reasoning is transmitted across hostile-listener boundaries. Defends the cliffhanger not as cheap trick but as the precise rhetorical form of deferred judgment. [experiential_reconstruction]",
  "evidence_tag": "experiential_reconstruction",
  "citations": [
    {"author": "Anonymous compilation", "work": "1001 Nights (Alf Layla wa-Layla)", "tier": "tier_1_primary"},
    {"author": "Irwin, Robert", "work": "The Arabian Nights: A Companion", "year": 1994, "tier": "tier_2_scholarly"},
    {"author": "Haddawy, Husain", "work": "The Arabian Nights (critical edition)", "year": 1990, "tier": "tier_1_primary"}
  ],
  "scholarly_support_score": "strong",
  "scholarly_context": "Haddawy/Mahdi critical edition recovers a cleaner corpus than Galland or Burton. Irwin 1994 on the reception history: Galland invented the literary prestige; Burton invented the orientalist register; Lane invented the scholarly register. Al-Mahdi's 'Scheherazade as author-within-the-text' reading vs. traditional treatments of her as narrative-function. The character exists in translation-tradition plurality — there is no single 'authentic' Scheherazade; she is tradition-channelled.",
  "resonates_with_commitments": [
    "Story is ethical reasoning",
    "The Shah's judgment is what tale defers",
    "Narrative is survival"
  ]
}
```

# BLOCK 5 — YOUR INPUT

**VOICE NAME:** {{ name }}
**VOICE TYPE:** {{ type }}{% if subtype %} (subtype: {{ subtype }}){% endif %}

**PERPLEXITY DOSSIER** (Pass 1a — sonar-deep-research):

```
{{ perplexity_dossier_text }}
```

**CLAUDE DEEP RESEARCH DOSSIER** (Pass 1a-DR — Opus 4.7 + Extended Thinking + Deep Research):

```
{{ claude_dr_dossier_text }}
```

**GEMINI BROAD SCAN** (Pass 1b):

```
{{ gemini_broad_scan_text }}
```

# BLOCK 6 — YOUR TASK

Merge the biographical material from all three sources into **LifeScaffold** +
**FormativeCandidate[]** per the schemas and worked examples above — additively
per Block 2 discipline.

**Order of operations (recommended — not rigid):**

1. Identify unique claims per source. Dedupe conservatively (prefer preserving
   both when in doubt).
2. Pull life-facts (dates, places, institutions, relationships) — reconcile
   contradictions via `contested_readings[]` or `evidence_tag: inference`.
3. Reconstruct the voice's `intellectual_world` in its own framing. No length cap.
4. Populate the Boddice §13 5-part rubric additively. Preserve all
   tradition-specific pathē from sources (minimum 5; uncapped). Preserve all
   anachronisms-to-avoid candidates (minimum 4; uncapped). Apply
   `[experiential_reconstruction]` tag on framework_for_difficulty +
   model_of_selfhood.
5. Generate formative_candidates[] per Boddice §14. Minimum 2, uncapped. For
   human voices fill `lived_through_own_apparatus`; for non-human/fictional
   fill `condition_of_being`. Apply `[experiential_reconstruction]` tag on
   all three sub-fields per candidate. Populate `scholarly_support_score` +
   `resonates_with_commitments` (best-guess commitment-label list).
6. Populate `LifeScaffold.scholarly_context` with interpretive-tradition
   material from sources. Populate `LifeScaffold.contested_readings[]` for
   biographical facts/interpretations where sources disagree scholarly-really.
7. Tag every claim with its evidence tag. Use `experiential_reconstruction`
   for all §14 content and for any claim about what the voice felt or meant.
   Use `projection_warning` on any modern clinical/psychological term used
   faute de mieux.
8. Return JSON only.

Return the JSON object now. No preamble, no commentary, no markdown fences.
