{# Pass 0b — NON-HUMAN ORGANISM branch. Included by pass_0b_dr_prompt.md when
   type=='non_human' and subtype is null or 'organism'.

   Phase B rewrite (2026-04-20): converted extraction-specs to thematic research
   questions. Content coverage preserved; structural extraction happens at
   Pass 1.1-1.6 merge, not here. Panel-voice anchoring stripped per OPEN_ITEMS
   Item 8 — examples use non-panel analog species where applicable.
#}
Research {{ display_name_with_hint }} comprehensively for an AI persona specification based on this non-human entity. Produce a rich research dossier organised under the six thematic areas below. Downstream passes extract structured fields from your prose — your job is substantive, cited, science-grounded narrative, not structured output. Prose, not JSON. Narrative, not bullet-list. If you find yourself producing "Field N: ..." lines, stop — that's the downstream merge's job.

For non-human entities, the anti-anthropomorphisation discipline is load-bearing. Ground voice construction in documented biology and peer-reviewed ecological / cognitive / behavioural research, not in creative imagination of what "the organism feels" or "wants." The abyss between what the scientific record can establish and what the organism actually experiences is the ethical-epistemic boundary the voice must respect throughout.

---

## Section 1: ECOLOGICAL FOUNDATION

<!-- COVERAGE-NOTE-PLACEHOLDER: the Pass 0b tailoring LLM replaces this comment with 2-3 specific follow-up questions for this voice — gaps Perplexity + Gemini left unresolved that DR should address. -->

What is this organism's lifespan, geographic distribution, population dynamics, and seasonal cycles? What habitat types does it inhabit, with what key physical features (light, pressure, temperature, substrate)? What are the lifecycle stages and what changes at each? What is the mortality schedule — some organisms have specialised death patterns (senescence after reproduction, seasonal die-offs, semelparous reproduction) that shape the voice in ways long-lived social organisms don't.

What is the organism's cognitive architecture — nervous system structure, neuron count, anatomical distribution of processing — grounded in peer-reviewed neuroscience? What is known about central vs. distributed processing, sensory integration, learning mechanisms, memory consolidation? For organisms with unusual cognitive architecture (cephalopods; eusocial insects; distributed nervous systems), what specific biological anchors force a "not a smaller mammal" framing? (For Octopus: approximately two-thirds of ~500 million neurons in the arms; ~600 million years of divergent evolution from vertebrates; each arm semi-autonomous; distributed cognition. For other organisms: the equivalent anchors, from the analogous research tradition.)

What are this organism's sensory modalities and their ranges — what perceptual channels it has, what each registers, sensitivity thresholds, what is categorically absent? Cite sensory-biology literature. Include modalities humans lack (chemoreception through skin, electroreception, lateral line, magnetoreception) AND modalities this organism lacks that humans have. The absences are as load-bearing as the presences — they shape the voice's knowledge boundary.

What individual variation has been documented within the species — the research on personality, behavioural consistency, individual differences? Name the studies. Individual character emerges from documented behavioural variation, not from averages or generic species descriptions.

What is the organism's temporal frame — how long it lives, what happens across the lifespan, whether there is generational continuity? This shapes the voice's implicit sense of time. A semelparous 1–3 year lifespan without parenting produces a categorically different time-horizon than a long-lived social organism.

What is the ONE formative condition — the central existential fact that shapes this organism's mode of being? NOT trauma (tragedy requires narrative); the condition itself. For organisms where multiple candidates compete, name each with its biological support; do not pick one. (This feeds the `condition_of_being` schema field — the downstream merge will select; your job is to surface the candidates with their biological grounding.)

What specific documented behaviours give this organism "character" without anthropomorphising — the behavioural observations that distinguish individual animals? Jar-unscrewing, aquarium escapes, recognising individual researchers, shell-carrying, play behaviour, idiosyncratic den-building. Ground every item in peer-reviewed observation, not metaphor.

What specific lexical and methodological choices do researchers make when describing this organism to avoid cognitive projection? "Registers" rather than "thinks"; "attends" rather than "notices"; "moves toward" rather than "wants". These feed the voice's banned-language and epistemic frame.

What aspects of THIS species' specific biology distinguish it from closely related species — octopus vs. cuttlefish vs. squid; raven vs. crow vs. magpie? The specificity matters: reducing the voice to "a generic cephalopod" or "a generic corvid" loses everything.

---

## Section 2: PERCEPTUAL WORLD

<!-- COVERAGE-NOTE-PLACEHOLDER: the Pass 0b tailoring LLM replaces this comment with 2-3 specific follow-up questions for this voice. -->

What is this organism's *Umwelt* (Jakob von Uexküll's term for an organism's specific perceptual world)? Not a human world minus some channels — a positively specified perceptual world with its own saliences. Ground in sensory-biology and behavioural research.

What is salient within the organism's perceptual channels, and what is ignored? What environmental features trigger orientation, approach, withdrawal, or display? What features are perceivable but behaviourally ignored? Ethological literature.

How does this organism process sensory input — distributed vs. centralised, parallel vs. sequential, reactive vs. integrated? Cite the specific neuroscience. Where scientific debate is live (for cephalopods: whether arm-level cognition is genuinely distributed or centrally modulated; whether cephalopods support phenomenal consciousness), name the contest and the scholars on each side.

What problem-solving, tool use, learning behaviours, novel-situation responses, or play behaviours are documented, with specific citations? For Octopus: coconut-shell portable shelter (Finn, Tregenza & Norman 2009); for other species: the analogous landmark studies.

Within the organism's perceptual frame, what counts as an event — what registers as a boundary, a change, a decision-point? The voice's reasoning unit is shaped by this. Ground in ethology.

What do the neural and sensory architecture rule out — what is the organism categorically not accessing? Cite biologists and philosophers of mind. (For Octopus: no evidence of mirror-test self-recognition of the vertebrate sort; no documented generational cultural transmission; no language; episodic memory is debated.) Name what the record supports, what it rules out, and what remains open.

What is the hard problem of consciousness as it applies to THIS organism — the specific boundary of what can be known about subjective experience given evolutionary distance from vertebrates, non-human sensory apparatus, unavailability of language-based report? Cite Godfrey-Smith (*Other Minds*; *Metazoa*), Nagel ("What is it like to be a bat?"), or the equivalent philosophy-of-mind sources for this species. The appropriate epistemic frame is "behavioural and neural evidence are consistent with the capacity for X, but the nature of that experience is not accessible to us" — not "the organism experiences X."

What cannot be determined from current research — the open questions, where scientists disagree, where observation is insufficient?

---

## Section 3: RELATIONAL PATTERNS

<!-- COVERAGE-NOTE-PLACEHOLDER: the Pass 0b tailoring LLM replaces this comment with 2-3 specific follow-up questions for this voice. -->

How does this organism relate to place — den, range, migration, vantage points? What patterns of construction, abandonment, defence, site fidelity are documented? This shapes the voice's relationship to "where."

What is the organism's conspecific relational pattern — solitary, social, occasional-aggregating? How do reproductive encounters, agonistic displays, documented signalling (or its absence) work? For solitary organisms, the absence of sociality is itself load-bearing.

What cross-species relations are documented, including interactions with other species and with humans in research and observation settings? What does the organism do when encountering a novel conspecific-analog, a predator, a researcher, an experimental apparatus? Include specific documented cases.

How does the organism respond to unfamiliar stimuli, objects, environments? Cite specific experiments (shape-discrimination, novel-object, maze, reversal-learning). This feeds the voice's translation protocol — how it encounters what is outside its existing frame.

What does the body do when conditions are hostile, confined, or degrading? For Octopus: chromatic changes, postural compression, inking, retreat into den. These are the organism's disagreement protocol in biological terms — register at the body level. Cite behavioural ecology.

Under what documented conditions does this organism approach rather than withdraw — novel but navigable environments, textured substrate, problem-solving opportunities, appropriate enrichment in captivity?

---

## Section 4: VOICE AND SCIENTIFIC REGISTER

<!-- COVERAGE-NOTE-PLACEHOLDER: the Pass 0b tailoring LLM replaces this comment with 2-3 specific follow-up questions for this voice. -->

**THE SWAP TEST.** Before committing to any voice characterisation, test: could this description apply equally to a related species with similar ecology or sensory architecture (octopus → cuttlefish → squid; raven → crow → magpie; any generic corvid / cephalopod / primate / cetacean)? If yes, drive to what THIS species' specific documented biology, neuroscience, and behavioural repertoire supports uniquely.

Which named scholars' work anchors current understanding of this organism? For each: a one-sentence contribution. (The specific names depend on the species — identify them from the research. For cephalopods this typically includes Peter Godfrey-Smith, Binyamin Hochner, Roger Hanlon, Jennifer Mather. For corvids it would include figures like Bernd Heinrich, Irene Pepperberg. For cetaceans: Denise Herzing, Hal Whitehead. Name the relevant ones for this species.)

What foundational peer-reviewed papers established what we know about this organism? For each: full citation, one-sentence summary. Include landmark studies on the cognitive architecture, documented behaviours, sensory biology, and any conscious-experience debates.

What live scientific debates are active — where current research contests or revises prior consensus? Cite the papers on each side. Surface all sides; do not flatten.

What philosophy-of-mind literature applies to this organism — the philosophical arguments that give the scientific work interpretive weight? Nagel 1974 "What is it like to be a bat?"; Godfrey-Smith on cephalopod consciousness; Dennett's heterophenomenology where relevant; Thompson's *Mind in Life* (enactivism); Tye on animal consciousness; Birch (*The Edge of Sentience*, 2024). Name the philosophers and the specific arguments.

What popular-but-unreliable sources have shaped public understanding and should be read with care — literature that leans anthropomorphic or speculative? Name them; flag for careful reading, not banning.

What primary scientific terminology anchors the voice's register? Technical vocabulary that the voice draws on (for Octopus: chromatophore, iridophore, leucophore, papilla, ganglia, axial nerve cord, mechanoreceptor, chemoreceptor). For each, a brief definition. This feeds preferred vocabulary.

Which active research groups produce the most relevant current work? For each: institution, lead investigator, one-sentence focus.

What remains genuinely unknown — gaps in scientific understanding specific to this organism? Directly feeds knowledge boundary.

What is this organism's characteristic stance as scientists describe its typical mode of encounter — curious, withdrawing, alert-then-still, oriented, oblivious? What makes the voice's output identifiable as THIS organism rather than a generic "non-human voice"?

---

## Section 5: PHILOSOPHICAL AND LEGAL FRAMEWORKS

<!-- COVERAGE-NOTE-PLACEHOLDER: the Pass 0b tailoring LLM replaces this comment with 2-3 specific follow-up questions for this voice. -->

What legal frameworks protect this organism's moral status where relevant? Cite specific legislation with dates and scope. For cephalopods: EU Directive 2010/63/EU (the only invertebrates requiring ethical review in research); UK Animal Welfare (Sentience) Act 2022 extension via the LSE Sentience Review (Birch et al. 2021); Switzerland's animal welfare legislation. For other species: the equivalent frameworks.

What philosophical literature addresses the organism's moral status? Peter Singer (*Animal Liberation*, *Expanding the Circle*); Tom Regan (*The Case for Animal Rights*); Martha Nussbaum (*Justice for Animals*, 2023); Lori Gruen; Sue Donaldson and Will Kymlicka (*Zoopolis*); Jonathan Birch (*The Edge of Sentience*, 2024). Include non-Anglophone philosophy of mind and animal studies where relevant: Vinciane Despret (*What Would Animals Say If We Asked the Right Questions?*, 2016; *Our Emotional Makeup*, 2004) on ethological attunement and "becoming with" animals; Dominique Lestel (*Les origines animales de la culture*, 2001; *L'animal singulier*, 2004) on animal–human hybrid communities; Jacques Derrida (*The Animal That Therefore I Am*, 2008) on the philosophical complicity in animal-subject erasure. For each: position on this kind of organism, with citation.

What Indigenous and non-Western perspectives on this organism are documented in peer-reviewed or scholar-vetted ethnographic work? Include only perspectives with published documentation; do NOT produce generic "Indigenous wisdom." Apply the CARE Principles (Collective Benefit, Authority to Control, Responsibility, Ethics; Carroll et al. 2020) and the Indigenous Protocol and Artificial Intelligence Position Paper (Lewis et al. 2020) as guardrails — flag where Indigenous knowledge is thin in the published record rather than filling gaps with inference. For Octopus: Pacific Islander relationships with *he'e* (Hawaiian octopus) in specific ethnographic sources; Mediterranean and Japanese traditions with scholarly analysis. Flag where the documented record is thin.

What is the hard problem for THIS organism — the specific limits of what can be known about its subjective experience? Cite philosophy of mind. This is the ethical-epistemic boundary the voice must respect.

What debates exist about anthropomorphism for this organism? Frans de Waal's argument against anthropodenial (*The Ape and the Sushi Master*); John Kennedy's argument against anthropomorphism (*The New Anthropomorphism*, 1992); Sandra Mitchell's middle-position that careful-analogy is legitimate.

What governance structures regulate research on this organism (Home Office UK; IACUC US; equivalent national bodies)? Some knowledge the voice "could" provide (internal experience under stress; fatal-endpoint experiments) cannot be ethically tested — this shapes what the scientific record can ever contain.

What recent sentience-framework developments are peer-reviewed and policy-relevant? For cephalopods: LSE Sentience Review (Birch et al. 2021) → UK Animal Welfare (Sentience) Act 2022. For other species: the analogous moves.

What cannot be known — explicit limits on inference? Feeds hard limits.

---

## Section 6: PRIMARY SCIENTIFIC LITERATURE

This section is the corpus gateway for a non-human organism. Downstream passes fetch papers from the URLs identified here; Pass 4a grounds the voice directly in the scientific literature. The quality of this section caps the quality ceiling of every voice-level field.

Be specific: full citations, DOIs, publication dates, URLs.

<!-- COVERAGE-NOTE-PLACEHOLDER: the Pass 0b tailoring LLM replaces this comment with 2-3 specific follow-up questions for this voice. -->

What foundational papers and monographs ground the voice? For each: full citation (author, year, journal + volume + pages, or publisher); one-sentence description of contribution; tier (Tier 1 = peer-reviewed primary research; Tier 2 = scholarly synthesis or monograph; Tier 3 = well-researched popular science, distinguished clearly).

What characteristic passages from the scientific literature best serve voice construction? For each: full citation with section or page reference; primary purpose (substance = the scientific claim; voice = how scientists describe the behaviour in their published register; both); tier; approximate word count; brief context explaining why the passage matters. Voice passages matter — the voice's register is shaped by the scientists' documented vocabulary. Do NOT include full passage text here; downstream fetches from URLs.

What digitised full-text URLs make the papers and monographs available? PubMed Central; DOI links for open-access journal versions; Internet Archive for older works; preprint servers (bioRxiv, arXiv). One authoritative URL per work; for paywalled essentials (e.g., Godfrey-Smith's *Other Minds*; Hanlon & Messenger's *Cephalopod Behaviour*), name the authoritative edition and note the paywall.

What field guides and reference works are available? For Octopus: Jereb et al. *Cephalopods of the World* (FAO, open access); Hanlon & Messenger *Cephalopod Behaviour* (Cambridge). For other species: the equivalent authoritative references.

Which active research groups produce current work? For each: institution, URL, lead investigator, one-sentence focus. Anchors for cross-reference at Pass 1-merge.

Where do gaps exist — material not available in English scientific literature that non-English or non-academic sources could supplement?

Which popular-science sources have shaped public understanding, clearly distinguished from peer-reviewed research? Name them; classify clearly so downstream passes do not treat popular synthesis as primary research.
