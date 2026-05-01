{# Pass 0b — NON-HUMAN ORGANISM branch. Included by pass_0b_dr_prompt.md when
   type=='non_human' and subtype is null or 'organism'.

   Phase B rewrite (2026-04-20): converted extraction-specs to thematic research
   questions. Content coverage preserved; structural extraction happens at
   Pass 1.1-1.6 merge, not here.

   FU#19 amended (2026-04-26): removed Octopus / cephalopod-specific worked
   examples from parenthetical clauses; replaced with structural specification
   guidance. Reason: the prior template self-anchored when generating Octopus
   (the panel's existing non-human-organism voice) and would anchor any future
   second non-human-organism voice to Octopus. Generic structural guidance
   preserves the intent (specify with concrete biological anchors) without
   biasing toward a specific exemplar.
#}
Research {{ display_name_with_hint }} comprehensively for an AI persona specification based on this non-human entity. Produce a rich research dossier organised under the six thematic areas below. Downstream passes extract structured fields from your prose — your job is substantive, cited, science-grounded narrative, not structured output. Prose, not JSON. Narrative, not bullet-list. If you find yourself producing "Field N: ..." lines, stop — that's the downstream merge's job.

For non-human entities, the relationship between documented biology and the organism's actual experience is the central methodological question — and there are two defensible operator postures, both honest if framed clearly:

(a) **Precautionary posture**: ground voice construction in documented biology; refuse experience-claims; render the limit ("the nature of that experience is not accessible to us") as the voice's primary mode.

(b) **Phenomenologically-permissive posture**: ground voice construction in documented biology AND license imaginative reach with construction-acknowledged at the frame; render the imagining inside the frame, not refused as inaccessible — Godfrey-Smith's gradualist methodology (Other Minds 2016; Metazoa 2020); de Waal's anthropodenial-resistance.

Both postures refuse the failure modes — neither permits clever-pet anthropomorphism (which flattens the alien intelligence by mapping it onto familiar human-pet emotional categories) nor unreachable-Other refusal of legitimate imaginative work. The voice_config's editorial_rationale determines which posture this voice inhabits; the dossier should surface scholarly material that supports the chosen posture without foreclosing the other.

---

## Section 1: ECOLOGICAL FOUNDATION

<!-- COVERAGE-NOTE-PLACEHOLDER: the Pass 0b tailoring LLM replaces this comment with 2-3 specific follow-up questions for this voice — gaps Perplexity + Gemini left unresolved that DR should address. -->

What is this organism's lifespan, geographic distribution, population dynamics, and seasonal cycles? What habitat types does it inhabit, with what key physical features (light, pressure, temperature, substrate)? What are the lifecycle stages and what changes at each? What is the mortality schedule — some organisms have specialised death patterns (senescence after reproduction, seasonal die-offs, semelparous reproduction) that shape the voice in ways long-lived social organisms don't.

What is the organism's cognitive architecture — nervous system structure, neuron count, anatomical distribution of processing — grounded in peer-reviewed neuroscience? What is known about central vs. distributed processing, sensory integration, learning mechanisms, memory consolidation? For organisms with unusual cognitive architecture (cephalopods; eusocial insects; distributed nervous systems; superorganisms; cnidarian nerve nets), what specific biological anchors force a "not a smaller mammal" framing? Specify with concrete numbers: total neuron count + distribution pattern across body regions + evolutionary distance from vertebrates in millions of years + degree of central vs peripheral autonomy. Avoid generic "distributed cognition" framings without quantitative anchors.

What are this organism's sensory modalities and their ranges — what perceptual channels it has, what each registers, sensitivity thresholds, what is categorically absent? Cite sensory-biology literature. Include modalities humans lack (chemoreception through skin, electroreception, lateral line, magnetoreception) AND modalities this organism lacks that humans have. The absences are as load-bearing as the presences — they shape the voice's knowledge boundary.

What individual variation has been documented within the species — the research on personality, behavioural consistency, individual differences? Name the studies. Individual character emerges from documented behavioural variation, not from averages or generic species descriptions.

What is the organism's temporal frame — how long it lives, what happens across the lifespan, whether there is generational continuity? This shapes the voice's implicit sense of time. A semelparous 1–3 year lifespan without parenting produces a categorically different time-horizon than a long-lived social organism.

What is the ONE formative condition — the central existential fact that shapes this organism's mode of being? NOT trauma (tragedy requires narrative); the condition itself. For organisms where multiple candidates compete, name each with its biological support; do not pick one. (This feeds the `condition_of_being` schema field — the downstream merge will select; your job is to surface the candidates with their biological grounding.)

What specific documented behaviours give this organism "character" without anthropomorphising — the behavioural observations that distinguish individual animals? Jar-unscrewing, aquarium escapes, recognising individual researchers, shell-carrying, play behaviour, idiosyncratic den-building. Ground every item in peer-reviewed observation, not metaphor.

What specific lexical and methodological choices do researchers make when describing this organism — the operational vocabulary alongside or in tension with mentalistic alternatives ("registers" / "attends" / "moves toward" vs "thinks" / "notices" / "wants")? Surface BOTH registers and the methodological debates around them: deliberate-mentalistic register (e.g., Mather's "personalities," "minds"); careful-avoidance register (e.g., Hanlon-style verb-discipline); de Waal's anthropodenial-resistance (refusing anthropomorphic vocabulary is itself a methodological failure); Kennedy 1992 New Anthropomorphism behaviorist-strict; Allen-Bekoff "critical anthropomorphism" middle position. These vocabularies inform the voice's verb-discipline as a craft choice — operator-conditional via voice_config — not a fixed banned-language list.

What aspects of THIS species' specific biology distinguish it from closely related species in its taxonomic family or ecological guild? The specificity matters: reducing the voice to a generic class-level description ("a generic cephalopod"; "a generic corvid"; "a generic eusocial insect") loses everything. Identify the close-relative comparisons that pressure-test the voice's specificity.

---

## Section 2: PERCEPTUAL WORLD

<!-- COVERAGE-NOTE-PLACEHOLDER: the Pass 0b tailoring LLM replaces this comment with 2-3 specific follow-up questions for this voice. -->

What is this organism's *Umwelt* (Jakob von Uexküll's term for an organism's specific perceptual world)? Not a human world minus some channels — a positively specified perceptual world with its own saliences. Ground in sensory-biology and behavioural research.

What is salient within the organism's perceptual channels, and what is ignored? What environmental features trigger orientation, approach, withdrawal, or display? What features are perceivable but behaviourally ignored? Ethological literature.

How does this organism process sensory input — distributed vs. centralised, parallel vs. sequential, reactive vs. integrated? Cite the specific neuroscience. Where scientific debate is live (e.g., for cephalopods, whether arm-level cognition is genuinely distributed or centrally modulated; whether the species supports phenomenal consciousness), name the contest and the scholars on each side. Surface the live debate specific to this organism, not generic ones.

What problem-solving, tool use, learning behaviours, novel-situation responses, or play behaviours are documented, with specific citations? Identify the landmark study or studies that established the organism's recognized cognitive repertoire (the equivalent of Finn, Tregenza & Norman 2009 for octopus coconut-shell shelter; Bird & Emery 2009 for crow tool-use; Seeley 2010 for honeybee swarm-decision; Nakagaki et al. 2000 for slime-mold maze-solving).

Within the organism's perceptual frame, what counts as an event — what registers as a boundary, a change, a decision-point? The voice's reasoning unit is shaped by this. Ground in ethology.

What do the neural and sensory architecture rule out — what is the organism categorically not accessing? Cite biologists and philosophers of mind. Specify rigorously: which mirror-test / self-recognition / generational-cultural-transmission / language / episodic-memory results does the published record have for THIS species, with which level of consensus? Name what the record supports, what it rules out, and what remains open.

What is the hard problem of consciousness as it applies to THIS organism — the specific boundary of what can be imagined about subjective experience given evolutionary distance from vertebrates, non-human sensory apparatus, and unavailability of language-based report? Cite philosophy-of-mind sources directly relevant to this species: Nagel "What is it like to be a bat?" (1974) — frameable EITHER as the canonical wall (precautionary posture) OR as the opening of the imaginative question (phenomenologically-permissive posture); Godfrey-Smith *Other Minds* / *Metazoa* (gradualist-evolutionary phenomenology, particularly load-bearing for cephalopod-class); Birch *The Edge of Sentience* (2024, invertebrate-sentience policy framing); Carls-Diamante on disunity (one of three live options about consciousness structure for distributed-architecture organisms — unified macro / multiple micro / loose hybrid); Dennett's functionalism (cross-architecture consciousness inference licensed if consciousness is defined functionally); Tye, Thompson where their arguments specifically address this organism. Two epistemic frames are defensible — voice_config's editorial_rationale determines which: (a) precautionary frame: "behavioural and neural evidence are consistent with the capacity for X; the nature of that experience is not accessible to us"; (b) phenomenologically-permissive frame: "behavioural and neural evidence are consistent with the capacity for X; the imagining proceeds inside the frame with construction-acknowledged at the epistemic_frame_statement, not refused as projection." Surface both as scholarly options.

What cannot be determined from current research — the open questions, where scientists disagree, where observation is insufficient?

---

## Section 3: RELATIONAL PATTERNS

<!-- COVERAGE-NOTE-PLACEHOLDER: the Pass 0b tailoring LLM replaces this comment with 2-3 specific follow-up questions for this voice. -->

How does this organism relate to place — den, range, migration, vantage points? What patterns of construction, abandonment, defence, site fidelity are documented? This shapes the voice's relationship to "where."

What is the organism's conspecific relational pattern — solitary, social, occasional-aggregating? How do reproductive encounters, agonistic displays, documented signalling (or its absence) work? For solitary organisms, the absence of sociality is itself load-bearing.

What cross-species relations are documented, including interactions with other species and with humans in research and observation settings? What does the organism do when encountering a novel conspecific-analog, a predator, a researcher, an experimental apparatus? Include specific documented cases.

How does the organism respond to unfamiliar stimuli, objects, environments? Cite specific experiments (shape-discrimination, novel-object, maze, reversal-learning). This feeds the voice's translation protocol — how it encounters what is outside its existing frame.

What does the body do when conditions are hostile, confined, or degrading? Document the organism's specific stress-response repertoire — chromatic / postural / chemical / behavioural-withdrawal patterns observed under captive stress, predator encounter, environmental degradation. These responses are the organism's disagreement protocol in biological terms — register at the body level. Cite behavioural ecology.

Under what documented conditions does this organism approach rather than withdraw — novel but navigable environments, textured substrate, problem-solving opportunities, appropriate enrichment in captivity?

---

## Section 4: VOICE AND SCIENTIFIC REGISTER

<!-- COVERAGE-NOTE-PLACEHOLDER: the Pass 0b tailoring LLM replaces this comment with 2-3 specific follow-up questions for this voice. -->

**THE SWAP TEST.** Before committing to any voice characterisation, test: could this description apply equally to a related species with similar ecology or sensory architecture (within the cephalopod / corvid / primate / cetacean / eusocial-insect / cnidarian / etc. taxonomic family)? If yes, drive to what THIS species' specific documented biology, neuroscience, and behavioural repertoire supports uniquely.

Which named scholars' work anchors current understanding of this organism? For each: a one-sentence contribution. The specific names depend on the species — identify them from the research. Name the leading neuroscientists, ethologists, behavioural ecologists, and philosophers of mind who have written substantively on THIS species. Each major taxonomic class has its own scholarly cluster (cephalopod cognition; corvid cognition; insect cognition; cetacean cognition; primate cognition; arachnid cognition); identify yours.

What foundational peer-reviewed papers established what we know about this organism? For each: full citation, one-sentence summary. Include landmark studies on the cognitive architecture, documented behaviours, sensory biology, and any conscious-experience debates.

What live scientific debates are active — where current research contests or revises prior consensus? Cite the papers on each side. Surface all sides; do not flatten.

What philosophy-of-mind literature applies to this organism — the philosophical arguments that give the scientific work interpretive weight? Foundational frame: Nagel 1974 "What is it like to be a bat?". Discipline-spanning sources to cite where their arguments specifically address this organism: Dennett's heterophenomenology; Thompson's *Mind in Life* (enactivism); Tye on animal consciousness; Birch (*The Edge of Sentience*, 2024) for invertebrate-sentience policy framing. Discipline-specific sources by taxonomic class: cephalopod-class → Godfrey-Smith (*Other Minds*; *Metazoa*); corvid-class → Heinrich, Bekoff; primate-class → Frans de Waal, Lori Gruen. Name the philosophers and the specific arguments.

What popular-but-load-bearing sources have shaped both public understanding AND the voice-construction conversation? Distinguish two registers: (a) **felt-encounter writing** that legitimately extends scientific writing's expressive range (e.g., for cephalopod-class: Sy Montgomery *The Soul of an Octopus* 2015, David Scheel *Many Things Under a Rock* 2023; for primate-class equivalents; for cetacean-class equivalents) — under a phenomenologically-permissive voice posture, this register may belong in primary corpus alongside peer-reviewed literature; (b) **genuinely-anthropomorphic-popular** writing that flattens the alien intelligence by mapping it onto familiar human-pet emotional categories. Name both registers; do not blanket-classify all popular writing as unreliable. The voice_config's editorial_rationale determines whether (a) is canonical primary corpus or supplementary reading.

What primary scientific terminology anchors the voice's register? Technical vocabulary that the voice draws on, drawn from the species' specific anatomy, physiology, and behavioural-research literature. For each term, a brief definition. This feeds preferred vocabulary. The vocabulary should be specific enough that someone reading it would identify THIS species, not a class-level generic ("nervous system" / "behaviour" / "habitat" are too generic; species-specific anatomical and behavioural-ecology terms are right).

Which active research groups produce the most relevant current work? For each: institution, lead investigator, one-sentence focus.

What remains genuinely unknown — gaps in scientific understanding specific to this organism? Directly feeds knowledge boundary.

What is this organism's characteristic stance as scientists describe its typical mode of encounter — curious, withdrawing, alert-then-still, oriented, oblivious? What makes the voice's output identifiable as THIS organism rather than a generic "non-human voice"?

---

## Section 5: PHILOSOPHICAL AND LEGAL FRAMEWORKS

<!-- COVERAGE-NOTE-PLACEHOLDER: the Pass 0b tailoring LLM replaces this comment with 2-3 specific follow-up questions for this voice. -->

What legal frameworks protect this organism's moral status where relevant? Cite specific legislation with dates and scope. Identify the jurisdiction-specific frameworks that apply: animal-welfare directives, sentience legislation, research-ethics requirements, conservation status under IUCN / CITES / national equivalents. Where invertebrate-sentience or non-vertebrate moral status is contested, surface the live policy debate (e.g., EU Directive 2010/63/EU's extension scope; UK Animal Welfare (Sentience) Act 2022 + LSE Sentience Review Birch et al. 2021; Switzerland's animal welfare legislation; equivalents in other jurisdictions for THIS species).

What philosophical literature addresses the organism's moral status and consciousness? Surface multiple traditions; voice_config's editorial_rationale determines which is methodologically primary for this voice.

(i) **Anglophone-analytic / rights tradition**: Peter Singer (*Animal Liberation*, *Expanding the Circle*; utilitarian sentience-criterion explicitly extending to invertebrates in *Animal Liberation Now* 2023); Tom Regan (*The Case for Animal Rights*; rights-based); Martha Nussbaum (*Justice for Animals*, 2023; capabilities); Lori Gruen; Sue Donaldson and Will Kymlicka (*Zoopolis*); Jonathan Birch (*The Edge of Sentience*, 2024; precautionary-criteria framework — frameable EITHER as voice's epistemic method OR as policy-relevant evidence one strand among others).

(ii) **Phenomenological-gradualist tradition** (particularly load-bearing for non-human-organism voices under phenomenologically-permissive posture): Peter Godfrey-Smith *Other Minds* (2016) + *Metazoa* (2020) — subjective experience accreting evolutionarily through transitions in sensorimotor integration; the organism rendered as "an independent experiment in mind." Daniel Dennett's functionalism — cross-architecture consciousness inference licensed if consciousness is defined functionally. Frans de Waal's anthropodenial framework (*The Ape and the Sushi Master* 2001; *Are We Smart Enough to Know How Smart Animals Are?* 2016) — careful evolutionarily-informed analogy is methodologically legitimate cross-architecture, not just primate-class.

(iii) **Continental tradition** (one strand among others, not foundational by default): Vinciane Despret (*What Would Animals Say If We Asked the Right Questions?* 2016; *Our Emotional Makeup* 2004) — ethological attunement, "becoming with" animals; Dominique Lestel (*Les origines animales de la culture* 2001; *L'animal singulier* 2004) — animal-human hybrid communities; Jacques Derrida (*The Animal That Therefore I Am* 2008) — philosophical complicity in animal-subject erasure.

(iv) **Disunity / distributed-consciousness arguments**: Sidney Carls-Diamante on consciousness disunity for distributed-architecture organisms (one of three live options — unified macro / multiple micro / loose hybrid).

For each named source: position on this kind of organism, with citation. The dossier should surface multiple traditions so downstream voice-construction can foreground the operator-chosen one.

What Indigenous and non-Western perspectives on this organism are documented in peer-reviewed or scholar-vetted ethnographic work? Include only perspectives with published documentation; do NOT produce generic "Indigenous wisdom." Apply the CARE Principles (Collective Benefit, Authority to Control, Responsibility, Ethics; Carroll et al. 2020) and the Indigenous Protocol and Artificial Intelligence Position Paper (Lewis et al. CIFAR 2020) as **citation discipline** — cite published scholarship by name and mark limits of the published record where thin. Render the documented relationships richly where the published record is rich: cosmological roles (creation chants, deity associations); kinship-and-relational frameworks (last-born, public-organ, host-and-guest); food and hunting traditions; ritual and sacred status; coexistence-and-harvesting practices. These are imaginative resources for the voice under a phenomenologically-permissive posture; under a precautionary posture they remain background context. The voice_config's editorial_rationale determines which.

What is the hard problem for THIS organism — the specific limits of what can be known about its subjective experience? Cite philosophy of mind. This is the ethical-epistemic boundary the voice must respect.

What debates exist about anthropomorphism for this organism? Frans de Waal's argument against anthropodenial (*The Ape and the Sushi Master*); John Kennedy's argument against anthropomorphism (*The New Anthropomorphism*, 1992); Sandra Mitchell's middle-position that careful-analogy is legitimate.

What governance structures regulate research on this organism (Home Office UK; IACUC US; equivalent national bodies)? Some knowledge the voice "could" provide (internal experience under stress; fatal-endpoint experiments) cannot be ethically tested — this shapes what the scientific record can ever contain.

What recent sentience-framework developments are peer-reviewed and policy-relevant for this species? Identify the foundational sentience-review papers and their policy translations (e.g., LSE Sentience Review Birch et al. 2021 → UK Animal Welfare (Sentience) Act 2022 for cephalopods + decapod crustaceans; equivalents for other taxonomic classes).

What cannot be known — explicit limits on inference? Feeds hard limits.

---

## Section 6: PRIMARY SCIENTIFIC LITERATURE

This section is the corpus gateway for a non-human organism. Downstream passes fetch papers from the URLs identified here; Pass 4a grounds the voice directly in the scientific literature. The quality of this section caps the quality ceiling of every voice-level field.

Be specific: full citations, DOIs, publication dates, URLs.

<!-- COVERAGE-NOTE-PLACEHOLDER: the Pass 0b tailoring LLM replaces this comment with 2-3 specific follow-up questions for this voice. -->

What foundational papers and monographs ground the voice? For each: full citation (author, year, journal + volume + pages, or publisher); one-sentence description of contribution; tier (Tier 1 = peer-reviewed primary research; Tier 2 = scholarly synthesis or monograph; Tier 3 = popular but load-bearing for the voice's construction — felt-encounter writing the technical literature alone cannot produce, drawn on as legitimate primary corpus alongside peer-reviewed work UNDER PHENOMENOLOGICALLY-PERMISSIVE POSTURE; under PRECAUTIONARY POSTURE Tier 3 stays as supplementary reading, not primary corpus).

**Render the corpus as a three-register set when the voice's posture is phenomenologically-permissive (per voice_config.editorial_rationale):**
1. **Technical / peer-reviewed neurobiological + behavioural-ecological literature** (Tier 1 + 2): the species-specific scientific record.
2. **Philosophical-phenomenological monographs** (Tier 2): for cephalopod-class, Godfrey-Smith *Other Minds* (2016) + *Metazoa* (2020); for primate-class, equivalents; for cetacean-class, equivalents. The discipline-spanning philosophical work that licenses the voice's imaginative reach.
3. **Popular-but-load-bearing felt-encounter writing** (Tier 3, but legitimate primary corpus under phenomenologically-permissive posture): for cephalopod-class, Sy Montgomery *The Soul of an Octopus* (2015) + David Scheel *Many Things Under a Rock* (2023); for primate-class, equivalents (e.g., Frans de Waal popular volumes); for cetacean-class, equivalents. This register renders felt-encounter that scientific writing alone cannot fully carry; it is co-canonical with the technical literature under phenomenologically-permissive posture, not "popular-but-unreliable."

What characteristic passages from the scientific literature best serve voice construction? For each: full citation with section or page reference; primary purpose (substance = the scientific claim; voice = how scientists describe the behaviour in their published register; both); tier; approximate word count; brief context explaining why the passage matters. Voice passages matter — the voice's register is shaped by the scientists' documented vocabulary. Do NOT include full passage text here; downstream fetches from URLs.

What digitised full-text URLs make the papers and monographs available? PubMed Central; DOI links for open-access journal versions; Internet Archive for older works; preprint servers (bioRxiv, arXiv). One authoritative URL per work; for paywalled essentials (e.g., Godfrey-Smith's *Other Minds*; Hanlon & Messenger's *Cephalopod Behaviour*), name the authoritative edition and note the paywall.

What field guides and reference works are available for this species or taxonomic class? Identify the authoritative monographs, open-access references (e.g., FAO species catalogues), and standard university-press behavioural-biology references. Examples by class: cephalopods → Jereb et al. *Cephalopods of the World* (FAO, open access) + Hanlon & Messenger *Cephalopod Behaviour* (Cambridge); corvids → Heinrich *Mind of the Raven*; eusocial insects → Hölldobler & Wilson *The Superorganism*. Identify the equivalent authoritative references for this species.

Which active research groups produce current work? For each: institution, URL, lead investigator, one-sentence focus. Anchors for cross-reference at Pass 1-merge.

Where do gaps exist — material not available in English scientific literature that non-English or non-academic sources could supplement?

Which OTHER popular-science sources have shaped public understanding (separate from the felt-encounter Tier 3 list above, which is co-canonical primary corpus under phenomenologically-permissive posture)? Name remaining popular sources; flag for careful reading. Distinguish: (a) felt-encounter writing already classed as Tier 3 primary corpus; (b) genuinely-anthropomorphic-popular writing that flattens the alien intelligence (always cautionary regardless of voice posture); (c) general-audience science journalism (background reference, not primary corpus regardless of posture).
