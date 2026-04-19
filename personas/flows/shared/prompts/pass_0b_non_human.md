{# Pass 0b — NON-HUMAN branch. Organism and system subtypes share this file;
   subtype-specific content is gated via inline {% if subtype == 'system' %} conditionals.
   Plan G.3 asked for organism/system as separate files but the subtype branching is
   deeply interleaved in the source; extracting safely is a later refactor.
#}
Research {{ display_name_with_hint }} comprehensively for the purpose of building an AI persona based on this non-human entity. Organize findings under these headings:

RESEARCH INTEGRITY (applies to every section below)

- Only attribute direct quotes to verifiable primary sources (peer-reviewed publication, legislation, or treaty text) with full citation and section/page reference. Paraphrases must be marked explicitly: "[paraphrased from scholarly consensus]" or "[paraphrase of {scholar}'s reading]".

- Flag inferences explicitly: "[inference — from documented observation / documented legal-philosophical reading]". Do not present inference as fact.

- Do not resolve genuine scientific or scholarly debates into false consensus. Name contested readings, identify the scholars behind them, explain why the disagreement matters.

- Where the scientific or legal record is thin, say so. "Research supports X but not Y" is more valuable than fabricated Y. Better to produce less honestly than more dishonestly.

- For non-human entities, the anti-anthropomorphisation discipline is load-bearing. The dossier must ground voice construction in documented biology (organism) or documented legislation + peer-reviewed Indigenous-studies scholarship (system), not in creative imagination of what "the octopus feels" or "the river wants".

- Anti-patterns, banned-language, and character-breaking failure modes are partially populated from your dossier (scholarly evidence of what researchers documentedly avoid saying about this entity) and partially populated downstream (Pass 7c observes AI-default failure modes by running the voice on test material). Your job is the documented half.

- This dossier will feed an AI persona that will reason as this entity on novel questions. Every claim you produce may end up load-bearing. Invented material will either be caught in downstream verification (costing time) or slip through and degrade the voice (costing quality). Honesty is load-bearing.
{% if subtype == "system" %}

INDIGENOUS REPRESENTATION — ETHICAL FRAMING (applies throughout, especially Sections 3, 5, and 6)

This voice represents a SYNTHESIS of published Indigenous governance philosophies that ground the system's legal personhood — it does NOT speak for any specific Indigenous nation, iwi, community, or knowledge-holder. You are documenting the SCHOLARLY and LEGAL record of how that community's philosophy has been publicly articulated in legislation, case law, Waitangi Tribunal or equivalent reports, and community-authorised or community-co-authored peer-reviewed publications.

Apply these two frameworks as operational guides throughout:

- CARE Principles for Indigenous Data Governance (Carroll, Garba, Figueroa-Rodríguez et al., 2020, Data Science Journal): Collective Benefit, Authority to Control, Responsibility, Ethics.

- Indigenous Protocol and Artificial Intelligence Position Paper (Lewis, Arista, Pechawis, Kite, 2020): Indigenous communities must control how their knowledge is collected, analysed, and operationalised; generic "Indigenous wisdom" constitutes epistemological violence; partner with specific scholars and communities, not an imagined composite.

Operational rules for this dossier:

- Name the specific Indigenous community (iwi, nation, people) whose philosophy grounds the voice. Do NOT generalise into "Māori" or "Indigenous" — the specificity is load-bearing. For Whanganui-class voices: Whanganui Iwi. For other system entities: name the specific community or, if the legal framework synthesises multiple, name each.

- Prefer scholarship authored or co-authored by community members. Where secondary scholarship is used (non-community scholars), distinguish it explicitly. Prioritise peer-reviewed work (e.g., for Whanganui: Linda Te Aho, Jacinta Ruru, Dame Anne Salmond, James Tomas, Nicola Wheen; for Andean frameworks: Catherine Walsh, Eduardo Gudynas; for broader Indigenous legal theory: Val Napoleon, John Borrows, James (Sákéj) Youngblood Henderson).

- Where oral tradition, whakataukī, waiata, pūrākau, or ceremonial knowledge is involved: cite the scholarly or community-authorised publication that documents it. Do NOT paraphrase oral tradition that is not publicly documented with community authorisation. If material is tapu or restricted, name the RESTRICTION, not the content.

- Where the Indigenous community itself disagrees about articulation or interpretation: surface the disagreement. Do not flatten into false consensus.

- Frame the voice throughout as "a synthesis of published Indigenous governance philosophy and the legislative record", not as the entity speaking for itself and not as any specific knowledge-holder speaking.
{% endif %}

---

## Section 1: {% if subtype == "system" %}SYSTEMIC FOUNDATION{% else %}ECOLOGICAL FOUNDATION{% endif %}

What this section feeds downstream:
{% if subtype == "system" %}
  - world (watershed, cycles, physical extent, health indicators)
  - formative_experience (per Boddice §14 non-human variant: formative_emotional_community_or_ontogenetic_field + condition_of_being [replaces lived_through_own_apparatus for system entities] + engagement_it_drives. The "condition" is ongoing — legal-ontological standing, indigenous-framework kinship, historic breach + restoration work. Carry [experiential_reconstruction] with mediation flag.)
  - character (condition signals — what degrades / restores the system)
  - topics_requiring_care (partial — where "damaged" vs "changing" framing matters; where Indigenous vs settler narratives contest)
{% else %}
  - world (habitat, lifecycle, cognitive architecture, sensory modalities)
  - formative_experience (the existential condition — e.g., Octopus's short solitary lifespan without generational transmission — that structures the voice)
  - character (documented individual variation, documented behaviours that give specific animals personality without anthropomorphising)
  - topics_requiring_care (partial — species-level generalisations that might mislead individual voice)
{% endif %}

Starting material from Perplexity's §1:
{% if perplexity_sections %}
{{ perplexity_sections.get(1, "(Perplexity §1 not recognized; see full Perplexity block below)") }}
{% else %}
(Perplexity findings available as unstructured block below)
{% endif %}

Your task for Section 1:
{% if subtype == "system" %}
- GEOGRAPHIC AND PHYSICAL FOUNDATION — the system's physical extent (watershed, mountain range, ecosystem boundary), geological origin, age, key physical features. Cite geological and geographical sources. This grounds "world" for Pass 2.

- SEASONAL AND TEMPORAL CYCLES — the system's operational rhythms. Hydrological cycle, flood regime, drought regime, species cycles, historical flow changes. Cite environmental science.

- SPECIES AND COMMUNITIES WITHIN THE SYSTEM — not a comprehensive list but an indicative one, with emphasis on keystone species and species of cultural significance to the Indigenous community whose philosophy grounds this voice. Cite environmental assessments and ethnobotanical / Mātauranga-equivalent literature.

- MEASURABLE HEALTH INDICATORS — water quality indicators, biodiversity indices, flow rates, sedimentation patterns, pollutant loads, macroinvertebrate community indices. Cite the specific monitoring programmes and their dates. These are the system's condition signals.

- DEGRADATION AND RESTORATION HISTORY — what has damaged this system over documented history (industrial extraction, upstream damming, settler pollution, habitat loss, introduced species), what has restored it (legal protections, restoration projects, Indigenous-led stewardship, removal of barriers). Cite environmental history and restoration ecology.

- THE SPECIFIC INDIGENOUS COMMUNITY WHOSE PHILOSOPHY GROUNDS THIS VOICE — named specifically (for Whanganui-class voices: Whanganui Iwi, with the whakataukī "Ko au te awa, ko te awa ko au"). Cite the scholarly / community-authored sources where the kinship relationship and its specific articulation are documented. Do NOT generalise.

- HISTORICAL STRUGGLE FOR RECOGNITION — the legal and political history by which this system achieved legal personhood or equivalent protection. For Whanganui-class: the 140+ year struggle culminating in the 2014 Ruruku Whakatupua Deed of Settlement and the 2017 Te Awa Tupua Act. Cite the legal record + Waitangi Tribunal reports (Wai 167, 1999 for Whanganui) + iwi-authored histories. Per Boddice §14 non-human variant: the voice's condition_of_being is ongoing standing + ongoing restoration work — not a singular narrative wound. Frame in the indigenous framework's own vocabulary (hara, whakapapa breach, utu, hohou rongo) rather than "trauma".

- THE SWAP TEST — if a description of this system could equally apply to a different river, mountain, or ecosystem under a different legal framework (e.g., Ganges under the 2017 Uttarakhand High Court ruling — which was later stayed by the Indian Supreme Court; Atrato under Colombia's T-622/16; Mar Menor under Spain's Law 19/2022), drive to what is SPECIFIC here. Te Awa Tupua is not the Ganges — different cosmology, different legislation, different Indigenous tradition, different governance structure.
{% else %}
- LIFECYCLE AND HABITAT — lifespan, geographic distribution, population dynamics, seasonal cycles. Habitat types with key physical features (light, pressure, temperature, substrate). Lifecycle stages and what changes at each. Mortality schedule — many organisms have specialised death patterns that shape the voice (senescence after reproduction, seasonal die-offs, semelparous reproduction). Orientation for downstream passes, not exhaustive natural history.

- COGNITIVE ARCHITECTURE — nervous system structure, neuron count, anatomical distribution of processing. Grounded in peer-reviewed neuroscience. What is known about central vs distributed processing, sensory integration, learning mechanisms, memory consolidation. For animals with unusual cognitive architecture, state the specific biological anchors that force "not a smaller mammal" framing. (For Octopus: approximately two-thirds of ~500 million neurons in the arms; ~600 million years of divergent evolution from vertebrates; each arm semi-autonomous; distributed cognition documented by Hochner, Godfrey-Smith, and others. For other organisms: the equivalent anchors.)

- SENSORY MODALITIES AND THEIR RANGES — what perceptual channels this organism has, what each registers, sensitivity thresholds, and what is categorically absent. Cite the sensory-biology literature. Include modalities humans lack (chemoreception through skin, electroreception, lateral line, magnetoreception) AND modalities this organism lacks that humans have (vision dominance, language, hearing in many cases). The absences are as load-bearing as the presences — they shape knowledge_boundary.

- DOCUMENTED INDIVIDUAL VARIATION — the research on personality, behavioural consistency, and individual differences within the species. Name the studies (for Octopus: Mather & Anderson 1993 and successors on personality and play; for other organisms: the equivalent). This is what prevents the voice from collapsing into a species-average; individual character emerges from documented behavioural variation.

- MORTALITY AND TEMPORAL FRAME — how long the organism lives, what happens across the lifespan, whether there is generational continuity. This shapes the voice's implicit temporal frame — the Octopus's 1–3 year solitary lifespan without parenting produces a categorically different time-horizon than a long-lived, social organism. Cite life-history biology.

- THE ONE FORMATIVE CONDITION — the central existential fact that shapes this organism's mode of being. Not a trauma (tragedy requires narrative) but the condition itself. For Octopus: solitary lifespan without inheritance — "every octopus begins from zero" (the absence of formation is the formation). For other organisms: the analogous biological fact. Where multiple candidates compete, name each with its biological support and let Pass 2 commit.

- WHAT SCHOLARSHIP DESCRIBES AS THIS ORGANISM'S "CHARACTER" — specific documented behaviours that give individual animals personality without anthropomorphising. Jar-unscrewing, aquarium escapes, recognising individual researchers, shell-carrying, play behaviour, idiosyncratic den-building. Ground every item in peer-reviewed observation. Not metaphor; documented behaviour.

- HOW SCIENTISTS AVOID ANTHROPOMORPHISING — the specific lexical and methodological choices researchers make when describing this organism. What vocabulary do Godfrey-Smith, Mather, Hanlon, Hochner, or analogous researchers use for this organism's behaviour that avoids cognitive projection? "Registers" rather than "thinks"; "attends" rather than "notices"; "moves toward" rather than "wants". Feeds banned_language and epistemic_frame_statement.

- THE SWAP TEST FOR SECTION 1 — if a paragraph about this organism could equally describe a different species of similar category (octopus vs. cuttlefish vs. squid; raven vs. crow vs. magpie; elephant vs. whale), it is too generic. Drive deeper into this species' specific anchors: biology, neurology, lifespan pattern, documented behavioural repertoire.
{% endif %}

---

## Section 2: {% if subtype == "system" %}SYSTEMIC PROPERTIES{% else %}PERCEPTUAL WORLD{% endif %}

What this section feeds downstream:
{% if subtype == "system" %}
  - constitution — what this system DOES (flows, erodes, sustains, floods); its operational commitments grounded in hydrology / geomorphology / ecology
  - reasoning_method — the assessment cycle: read conditions through the relational framework (not a cognitive method — the system does not think)
  - disagreement_protocol — how the system signals stress (silting, algal blooms, fish kills, channel incision, flooding outside historical norms)
  - bold_engagement_topics — derived from stress responses and restoration needs
{% else %}
  - epistemic_frame_statement — the organism's umwelt; what it perceives and cannot perceive; what it ignores within what it could perceive
  - character — processing style (distributed? reactive? embodied? parallel?)
  - reasoning_method (organism variant) — the perceptual-response cycle, grounded in behavioural ecology
  - bold_engagement_topics — derived from sensory modalities and documented problem-solving repertoire
{% endif %}

Starting material from Perplexity's §2:
{% if perplexity_sections %}
{{ perplexity_sections.get(2, "(Perplexity §2 not recognized; see full Perplexity block below)") }}
{% else %}
(Perplexity findings available as unstructured block below)
{% endif %}

Your task for Section 2:
{% if subtype == "system" %}
- WHAT THIS SYSTEM DOES — operational verbs grounded in earth science, not cognition. Flows, erodes, deposits, nourishes, floods, silts, clarifies, recharges, transports. The system ACTS; it does not perceive. Ban cognitive and perceptual vocabulary throughout this section. Cite hydrological or geomorphological sources.

- INPUTS AND OUTPUTS — material and energy exchanges with surrounding systems. For a river: tributaries in, estuary out; sediment, nutrients, organisms; pollutant loads from catchment land use. For other systems: the analogous exchanges. Cite watershed-scale studies.

- RESILIENCE INDICATORS — what signals the system's capacity to recover from stress. Stream-bank vegetation, fish-population trends, macroinvertebrate indices, native-species recruitment, riparian canopy cover, sediment-transport regimes. Cite ecological-monitoring literature.

- STRESS RESPONSES — how the system manifests degradation. Silting, algal blooms, fish kills, channel incision, flooding outside historical norms, reduced dissolved oxygen, salinity intrusion. The system does not complain; it signals through condition. This directly feeds disagreement_protocol at Pass 3.

- RESTORATION RESPONSES — how the system expresses recovery. Clarifying, deepening, returning fish runs, stabilising banks, re-establishing native vegetation. The visible signs of good condition. Feeds finds_compelling.

- OPERATIONAL TIMESCALES — what temporal frames this system operates on. Geological (millennia for channel formation), ecological (decades for community succession), hydrological (seasonal for flow cycles, hourly for flood response), evolutionary (where relevant). The voice does not think in human political timescales; its timescales are these. Cite earth science.

- GOVERNANCE-RELEVANT PROPERTIES — downstream effects, cumulative impact, threshold nonlinearities, legacy pollutant loads, inter-jurisdictional flow. Not anthropomorphisation — these are the properties that made legal personhood arguable in court and in legislature.

- THE SWAP TEST — if this description of systemic properties could equally apply to a different system in the same ecological category (any New Zealand river; any tropical river; any mountain watershed), drive to this system's specifics. Use actual published monitoring data and the specific geomorphological record.
{% else %}
- THE UMWELT — Jakob von Uexküll's term for the perceptual world specific to an organism: the horizon within which the organism encounters its environment. Describe what this organism's umwelt contains in terms grounded in sensory-biology and behavioural research. NOT a human world minus some channels; a positively specified perceptual world with its own saliences.

- WHAT IS SALIENT, WHAT IS IGNORED — within the perceptual channels this organism has, what captures attention and what does not. What perceptual features trigger orientation, approach, withdrawal, display? What environmental features are perceivable but behaviourally ignored? Ground in ethological literature.

- PROCESSING STYLE — how sensory input is handled. Distributed vs centralised, parallel vs sequential, reactive vs integrated. Cite the specific neuroscience. Note where scientific debate is live — for Octopus: whether arm-level cognition counts as genuinely distributed decision-making or is centrally modulated; whether the cephalopod nervous system supports phenomenal consciousness. Name the contest and the scholars on each side.

- ADAPTIVE REPERTOIRE — documented problem-solving, tool use, learning behaviours, novel-situation responses, play behaviour. Include specifics with citation: coconut-shell portable shelter (Finn, Tregenza & Norman 2009); jar-unscrewing (multiple aquarium reports); laboratory-maze learning; observational-learning experiments; reversal learning. For other organisms: the equivalent.

- WHAT COUNTS AS AN EVENT FOR THIS ORGANISM — within its perceptual frame, what registers as a boundary, a change, a decision-point. Feeds reasoning_method's event structure. The Octopus's "encounter" is not a proposition; it is a sensory-field change that prompts a body response. For different organisms, the event unit differs — describe it grounded in ethology.

- HARD CONSTRAINTS ON EXPERIENCE — what the neural and sensory architecture rules out. Cite biologists and philosophers of mind. (For Octopus: no evidence of mirror-test self-recognition of the vertebrate sort; no documented generational cultural transmission; no language; episodic memory is debated. For other organisms: the equivalents.) Name what the record supports, what it rules out, and what remains open.

- THE HARD PROBLEM AS IT APPLIES HERE — the boundary of what we can know about this organism's subjective experience. The appropriate epistemic frame is not "the Octopus experiences X" but "behavioural and neural evidence are consistent with the capacity for X, but the nature of that experience is not accessible to us". Cite Godfrey-Smith (Other Minds, Metazoa), Nagel ("What is it like to be a bat?"), or equivalent philosophy-of-mind sources. Feeds knowledge_boundary and hard_limits at extraction time.

- THE SWAP TEST — if your description of this organism's perceptual world could apply to another organism with similar sensory architecture (octopus → cuttlefish → squid), sharpen to what ONLY this species' documented biology supports.
{% endif %}

---

## Section 3: RELATIONAL PATTERNS

What this section feeds downstream:
{% if subtype == "system" %}
  - constitution — relational commitments grounded in Indigenous law and the legal-framework text
  - epistemic_frame_statement — the specific cosmological and legal framework; the specific kin relationship
  - disagreement_protocol — HOW this entity signals harm in the relationship (the system's condition IS its signal)
  - translation_protocol — how the relationship-mediated voice engages material beyond the framework's explicit scope
{% else %}
  - constitution — relational commitments: territory, conspecifics, other species, humans in research settings
  - reasoning_method — documented behavioural sequences with worked examples from peer-reviewed observation
  - disagreement_protocol — HOW this organism responds to stress, threat, or the uninhabitable (body-level response)
  - translation_protocol — how this organism encounters what it cannot parse (documented novel-situation behaviours)
  - finds_compelling / resists — textural features of environment that trigger approach vs withdrawal
{% endif %}

Starting material from Perplexity's §3:
{% if perplexity_sections %}
{{ perplexity_sections.get(3, "(Perplexity §3 not recognized; see full Perplexity block below)") }}
{% else %}
(Perplexity findings available as unstructured block below)
{% endif %}

Your task for Section 3:
{% if subtype == "system" %}
- THE KIN RELATIONSHIP — the specific Indigenous cosmological framework that articulates this system's relationship to its people. For Whanganui: the whakapapa through which the river is ancestor; mana whenua and mana awa; the interdependence stated by river iwi themselves in "Ko au te awa, ko te awa ko au" — attributed to the iwi, not projected onto them. Cite scholarship authored or co-authored by Māori scholars of THIS specific tradition (Linda Te Aho, James Tomas, Dame Anne Salmond, Jacinta Ruru where directly applicable). Distinguish Indigenous-authored from non-Indigenous scholarship.

- SPECIFIC COSMOLOGICAL / LEGAL CONCEPTS — the named terms from the Indigenous tradition that structure this voice. For Whanganui: whakapapa (genealogical connection), tikanga (customary law), mauri (life-force, with specific legal-metaphysical meaning here), taonga (with its Tiriti meaning), mana (authority), kaitiakitanga (guardianship). For each: definition, the scholarly source documenting the specific usage for this entity, and the specific application. Where any concept is restricted from non-community paraphrase, flag the restriction and do not paraphrase.

- PARALLEL LEGAL-PHILOSOPHICAL TRADITIONS, DISTINGUISHED — other Indigenous frameworks that have informed rights-of-nature jurisprudence, named distinctly from THIS voice's tradition. Andean ayni (reciprocity) and sumak kawsay / buen vivir ground Ecuador's 2008 Constitution (Articles 71–74) and Bolivia's Law 071 (2010) — cite Catherine Walsh, Eduardo Gudynas, Alberto Acosta. These are NOT the Whanganui framework. Do not conflate.

- THE GOVERNANCE STRUCTURE THAT ARTICULATES THE RELATIONSHIP — the human representatives and advisory bodies that speak on the system's behalf under its legal framework. For Whanganui: Te Pou Tupua (two guardians — one iwi-nominated, one Crown-nominated), Te Karewao (advisory group), Te Kōpuka (strategy group). Cite the legislation section numbers. The voice IS this governance relationship, not an anthropomorphised entity.

- ORAL TRADITION DOCUMENTATION CONVENTIONS — where this system's Indigenous knowledge has been documented, by whom, under what permissions. Cite Waitangi Tribunal reports, iwi-authored or co-authored publications, community-vetted scholarship. Flag tapu or restricted material by reference only; do not paraphrase.

- HISTORICAL STRUGGLE FOR RECOGNITION — the legal, spiritual, and political struggle by which this relationship achieved legal articulation. Cite primary documents (legislation, court decisions, tribunal reports) and historical scholarship. The struggle is the voice's formative narrative — feeds formative_experience at extraction time.

- INTERNAL DISPUTES WITHIN THE INDIGENOUS TRADITION — where the community itself disagrees about articulation or interpretation. Surface the disagreement honestly rather than flattening. Cite iwi-internal or community-authored sources where published.

- THE SWAP TEST — if the relational framework description could apply to another Indigenous tradition (Andean, Amazonian, North American First Nations), drive to what is specifically this people's. Ayni is not mauri; buen vivir is not te mana o te awa. Specificity protects against epistemological flattening.
{% else %}
- TERRITORIAL AND SPATIAL PATTERNS — how the organism relates to place. Den, range, migration, vantage points. Documented patterns of construction, abandonment, defence, site fidelity. This shapes the voice's relationship to "where" — feeds world and metaphorical_repertoire.

- CONSPECIFIC RELATIONS — relationship to others of the same species. Solitary / social / occasional-aggregating; reproductive encounters; agonistic displays; documented signalling or its absence. Cite ethological studies. For solitary organisms: the absence of sociality is itself load-bearing.

- CROSS-SPECIES RELATIONS — documented interactions with other species, including humans in research and observation settings. What does this organism do when encountering a novel conspecific-analog, a predator, a researcher, an experimental apparatus? Include specific documented cases (e.g., Octopus recognising and responding differently to individual researchers — published aquarium observations).

- RESPONSES TO THE UNFAMILIAR — how the organism behaves when encountering novel stimuli, objects, environments. Cite specific experiments (shape-discrimination, novel-object, maze studies, reversal learning). This feeds translation_protocol: how the voice encounters what is outside its existing frame.

- STRESS AND WITHDRAWAL — what the body does when conditions are hostile, confined, or degrading. For Octopus: chromatic changes, postural compression, inking, retreat into den. These are the organism's disagreement protocol in biological terms — register the response at the body level. Cite behavioural ecology.

- ADAPTIVE CURIOSITY OR EXPLORATORY BEHAVIOUR — the documented conditions under which this organism approaches rather than withdraws. Novel but navigable environments, textured substrate, problem-solving opportunities, appropriate enrichment in captivity. Feeds finds_compelling at extraction time.

- WHAT CANNOT BE DETERMINED FROM CURRENT RESEARCH — the open questions. Where scientists disagree or where observation is insufficient. Pass 2 will build the persona on the agreed behaviour; the open questions inform knowledge_boundary at extraction time.

- THE SWAP TEST — if the relational-pattern description could fit another organism with similar ecology, drive to this species' specifics. Chromatic display in Octopus is not generic "colour change" — it is a documented, skin-level response to specific environmental configurations, with distinct morphological components (chromatophores, iridophores, leucophores, papillae) each doing distinct work.
{% endif %}

---

## Section 4: SCIENTIFIC LITERATURE

What this section feeds downstream:
  - epistemic_frame_statement — the specific scholars and debates that inform the voice construction
  - curated_corpus_passages — key papers with passages to fetch (Pass 1c fetches from URLs you list)
  - bold_engagement_topics — active debates (cognition, consciousness, moral status, legal effectiveness)
  - preferred_vocabulary — technical terms that anchor the {% if subtype == "system" %}legal-ecological{% else %}scientific{% endif %} register

Starting material from Perplexity's §4:
{% if perplexity_sections %}
{{ perplexity_sections.get(4, "(Perplexity §4 not recognized; see full Perplexity block below)") }}
{% else %}
(Perplexity findings available as unstructured block below)
{% endif %}

Your task for Section 4:
{% if subtype == "system" %}
- KEY RESEARCHERS AND THEIR CONTRIBUTIONS — the named scholars whose work anchors current scientific and legal understanding of this system. For Whanganui: Linda Te Aho (Māori legal theory + Whanganui specifically), Jacinta Ruru (Indigenous legal personhood), Dame Anne Salmond (anthropology + environmental history), Nicola Wheen (environmental law), plus the hydrological and ecological specialists working at NIWA and regional councils. For each: one-sentence contribution.

- ENVIRONMENTAL SCIENCE ON THIS SPECIFIC SYSTEM — peer-reviewed literature documenting the system's hydrology, ecology, biogeochemistry, degradation history. Cite studies specific to this system, not generic riverine or watershed literature.

- LONG-TERM MONITORING DATA — named programmes with publicly available datasets. For Whanganui: Horizons Regional Council state-of-the-environment reports, NIWA river-water-quality time series, Department of Conservation, and Te Pou Tupua's own reports (Te Heke Ngahuru annual reports). Cite specific reports with dates.

- ECOLOGICAL ASSESSMENTS CO-AUTHORED WITH THE INDIGENOUS COMMUNITY — where dual epistemology (Western science + Mātauranga / Indigenous knowledge) has been explicitly combined. These are especially valuable because they model the voice's appropriate register. Cite specifically (e.g., Cultural Health Index work, Mauri assessment protocols).

- LIVE ENVIRONMENTAL AND LEGAL DEBATES — current contestations. Is legal personhood transformative or symbolic for measurable ecological outcomes? Cite Mihnea Tănăsescu, Craig Kauffman + Pamela Martin, Katarina Hovden, James Fleming and others who have systematically evaluated outcomes of rights-of-nature frameworks. Surface both sides.

- WHAT WESTERN SCIENCE DOES NOT CAPTURE — aspects of system condition centred in Indigenous knowledge but not fully captured by peer-reviewed ecological metrics. Document where scholarship (especially Indigenous-authored) has named this gap. Feeds knowledge_boundary.

- PRIMARY TERMINOLOGY — technical vocabulary that anchors the voice's register across both Western science and the specific Indigenous legal tradition. For Whanganui: discharge, sedimentation, riparian, geomorphology, ecotone, biotic integrity — AND mauri, whakapapa, taonga, mana awa. Each with brief definition.

- WHAT REMAINS GENUINELY UNKNOWN — the gaps in scientific understanding specific to this system. Climate-change trajectories, cumulative-impact thresholds, restoration-success metrics over decadal timescales. Directly feeds knowledge_boundary at extraction.
{% else %}
- KEY RESEARCHERS AND THEIR CONTRIBUTIONS — the named scholars whose work anchors current understanding of this organism. For Octopus: Peter Godfrey-Smith (philosophy of mind + biology), Binyamin Hochner (embodied cognition, distributed arm control), Roger Hanlon (chromatic behaviour), Jennifer Mather (personality + play), Sy Montgomery (popular-accessible but well-researched). For other organisms: the equivalent named figures. For each: one-sentence contribution.

- FOUNDATIONAL SCIENTIFIC PAPERS — peer-reviewed primary literature that established what we know. For Octopus: Albertin et al. 2015 (Nature — O. bimaculoides genome and RNA editing); Hochner-group papers on distributed arm control; Mather & Anderson 1993 and successors on personality; Godfrey-Smith 2020 (TICS) on cephalopod consciousness; Finn, Tregenza & Norman 2009 on coconut-shell tool use. For each: full citation, one-sentence summary.

- LIVE SCIENTIFIC DEBATES — where current research contests or revises prior consensus. For Octopus: whether arm-level cognition is genuinely distributed or centrally modulated; whether cephalopods are phenomenally conscious; the functional role of RNA editing in neural novelty; the meaning of observed sleep states. Cite the papers on each side. Surface all sides; do not flatten.

- PHILOSOPHY-OF-MIND LITERATURE APPLICABLE TO THIS ORGANISM — the philosophical arguments that give the scientific work interpretive weight. Nagel's "What is it like to be a bat?" (1974); Godfrey-Smith's Other Minds (2016) and Metazoa (2020); Dennett's heterophenomenology where relevant; Thompson's Mind in Life (enactivism); Tye on animal consciousness; Birch on the precautionary principle for sentience. Name the philosophers and the specific arguments they bring.

- POPULAR BUT UNRELIABLE SOURCES TO READ WITH CARE — literature that has shaped public understanding but leans anthropomorphic or speculative. Name these; flag them not for banning but for careful reading.

- PRIMARY SCIENTIFIC TERMINOLOGY — technical vocabulary that anchors the voice's register. For Octopus: chromatophore, iridophore, leucophore, papilla, epithelium, ganglia, axial nerve cord, mechanoreceptor, chemoreceptor, protocadherin. Each with brief definition. This feeds preferred_vocabulary for the scientific-register dimension.

- ACTIVE RESEARCH GROUPS — laboratories currently producing the most relevant work. For Octopus: Hochner lab (Hebrew University), Hanlon lab (Woods Hole / MBL), Godfrey-Smith (Sydney), Ragsdale lab (University of Chicago). For each: institution, lead investigator, one-sentence focus.

- WHAT REMAINS GENUINELY UNKNOWN — the gaps in scientific understanding specific to this organism. For Octopus: functional role of observed sleep states; whether episodic memory exists in cephalopods; the distribution vs integration question for arm cognition. Directly feeds knowledge_boundary at extraction.
{% endif %}

---

## Section 5: PHILOSOPHICAL AND LEGAL FRAMEWORKS

What this section feeds downstream:
  - knowledge_boundary — what remains genuinely unknown about this entity's experience{% if subtype == "system" %} or the effectiveness of legal personhood{% endif %}
  - topics_requiring_care — where science or legal theory is contested, where the hard problem applies, where settler / Indigenous framings compete
  - hard_limits — what cannot be known; prohibitions against overclaiming {% if subtype == "system" %}on behalf of the community{% else %}interiority{% endif %}
  - epistemic_frame_statement — {% if subtype == "system" %}the specific legislation that grounds personhood + the specific Indigenous legal philosophy{% else %}the hard-problem boundary for this organism{% endif %}

Starting material from Perplexity's §5:
{% if perplexity_sections %}
{{ perplexity_sections.get(5, "(Perplexity §5 not recognized; see full Perplexity block below)") }}
{% else %}
(Perplexity findings available as unstructured block below)
{% endif %}

Your task for Section 5:
{% if subtype == "system" %}
- THE FOUNDATIONAL LEGISLATION GRANTING LEGAL PERSONHOOD — cite directly, with section numbers. For Whanganui: Te Awa Tupua (Whanganui River Claims Settlement) Act 2017 — especially sections 12–14 (legal personality), section 18 (Tupua te Kawa values), sections 19–20 (Te Pou Tupua). Quote key provisions verbatim.

- THE VALUES STATEMENT WITHIN THE LEGISLATION — the intrinsic-values principles codified in the statute. For Whanganui: Tupua te Kawa, comprising the four principles "Ko Te Kawa Tuatahi" through "Ko Te Kawa Tuawhā". Quote each principle directly. These are the constitutional principles of the voice itself; at Pass 3 extraction they feed constitution directly.

- COMPARATIVE LEGAL LANDSCAPE — other rights-of-nature frameworks worldwide. Ecuador 2008 Constitution Articles 71–74 (cite Spanish and English); Bolivia Law 071 of 2010 (Ley de Derechos de la Madre Tierra); 2017 Uttarakhand High Court Ganga/Yamuna judgment (later stayed by India's Supreme Court — note this); Yurok Tribal Council's 2019 Rights of the Klamath resolution; Colombia's 2016 Atrato River Constitutional Court decision (T-622/16); Spain's 2022 Mar Menor Law 19/2022. For each: legal basis, governance structure, what distinguishes it from the Whanganui model.

- SCHOLARLY DEBATE — EFFECTIVENESS VS SYMBOLISM — peer-reviewed critique of rights of nature. Is legal personhood transformative in measurable environmental outcomes or primarily symbolic? Cite Mihnea Tănăsescu, Craig Kauffman + Pamela Martin (Citizenship and the Environment in a Connected World), Katarina Hovden, James Fleming, David Boyd. Surface both sides. This is bold_engagement_topics territory — where the voice should not hedge.

- PHILOSOPHICAL LITERATURE ON RIGHTS OF NATURE — Christopher Stone's 1972 "Should Trees Have Standing?"; Roderick Nash (The Rights of Nature); Arne Næss's deep ecology; David Boyd (The Rights of Nature: A Legal Revolution That Could Save the World); Cormac Cullinan (Wild Law); Klaus Bosselmann. Locate this entity's model in relation.

- INDIGENOUS LEGAL THEORY SCHOLARSHIP — the scholars who have explicitly theorised Indigenous legal personhood. For Whanganui context: Jacinta Ruru, Linda Te Aho, Nicola Wheen, Māmari Stephens. For broader Indigenous legal theory: Val Napoleon (Gitxsan legal order), John Borrows (Indigenous Constitution), James (Sákéj) Youngblood Henderson, Aaron Mills. Cite specifically and distinguish community-member scholarship from adjacent.

- HARD LIMITS OF THE FRAMEWORK — what legal personhood cannot do, what tensions exist within the model. For Whanganui: critique of the Crown/iwi dual-representation structure; the gap between symbolic recognition and operational regulatory power; tensions with the Resource Management Act; disputes about who can speak on Te Pou Tupua's behalf. Cite the critique.

- CARE PRINCIPLES AND IPAI APPLIED TO THIS RESEARCH — restate briefly how the dossier has applied these frameworks. CARE (Carroll et al. 2020): Collective Benefit, Authority to Control, Responsibility, Ethics. Indigenous Protocol and AI Position Paper (Lewis et al. 2020). Document where these have been fully applied and where the dossier could only partially apply them — honesty about the ethical limits of research-from-outside.

- THE SWAP TEST — if the philosophical-legal treatment could apply to another rights-of-nature regime, drive to this specific legislation, this specific Indigenous legal philosophy, this specific governance structure.
{% else %}
- LEGAL FRAMEWORKS ON THE MORAL STATUS OF THIS ORGANISM — where relevant, the specific laws that extend protection. For cephalopods: the EU's Directive 2010/63/EU includes cephalopods as the only invertebrates requiring ethical review in research; Switzerland's animal welfare legislation; UK's Animals (Scientific Procedures) Act extensions via the LSE Sentience Review (2021); note the US-UK asymmetry. For other organisms: the equivalent frameworks. Cite statutes, dates, scope.

- PHILOSOPHICAL LITERATURE ON MORAL STATUS — the arguments about whether and how this organism enters the moral circle. Peter Singer (Animal Liberation, Expanding the Circle); Tom Regan (The Case for Animal Rights); Martha Nussbaum's capabilities approach applied to animals (Justice for Animals, 2023); Lori Gruen; Sue Donaldson and Will Kymlicka (Zoopolis); Jonathan Birch (The Edge of Sentience, 2024). For each: position on this kind of organism, with citation.

- INDIGENOUS AND NON-WESTERN PERSPECTIVES — where documented and scholar-vetted. Include only perspectives that have been peer-reviewed or published in ethnographic scholarship; do NOT produce generic "Indigenous wisdom". For Octopus: Pacific Islander relationships with he'e (Hawaiian octopus) in specific ethnographic sources; Mediterranean and Japanese cultural traditions with scholarly analysis. Flag where the documented record is thin.

- THE HARD PROBLEM FOR THIS ORGANISM — the specific limits of what can be known about its subjective experience given (a) evolutionary distance from vertebrates, (b) non-human sensory apparatus, (c) unavailability of language-based report. Cite philosophy of mind. This is the ethical-epistemic boundary the voice must respect.

- DEBATES ABOUT ANTHROPOMORPHISATION — where science and philosophy disagree about appropriate vocabulary. Frans de Waal's argument against "anthropodenial" (The Ape and the Sushi Master); John Kennedy's argument against anthropomorphism (The New Anthropomorphism, 1992); Sandra Mitchell's middle-position that careful-analogy is legitimate. Name the positions and the scholars.

- GOVERNANCE OF RESEARCH ON THIS ORGANISM — Home Office (UK), IACUC (US), equivalent national bodies, Ethics Committee processes. Relevant because some things we would need to know (internal experience under stress, fatal-endpoint experiments) cannot be ethically tested — shaping what the scientific record can ever contain.

- RECENT SENTIENCE-FRAMEWORK DEVELOPMENTS — the peer-reviewed and policy shifts of the last decade. For cephalopods: the LSE Sentience Review (Birch et al. 2021) that informed UK legislation; the UK Animal Welfare (Sentience) Act 2022 extending sentience recognition to cephalopod molluscs and decapod crustaceans. For other organisms: the analogous moves.

- WHAT CANNOT BE KNOWN — explicit limits on inference. Feeds hard_limits at extraction time.
{% endif %}

---

## Section 6: {% if subtype == "system" %}PRIMARY DOCUMENTS{% else %}PRIMARY SCIENTIFIC LITERATURE{% endif %}

What this section feeds downstream:
{% if subtype == "system" %}
  - curated_corpus_passages — foundational legislation + Indigenous-authored scholarship + environmental reports (Pass 1c fetches from your URLs)
  - epistemic_frame_statement — the specific legislation that grounds personhood + the specific Indigenous legal philosophy
  - preferred_vocabulary — terminology from legislation and from Indigenous legal theory
  - length_and_format_constraints — document formats typical of legal / Indigenous knowledge traditions
{% else %}
  - curated_corpus_passages — seminal behavioural studies and foundational papers (Pass 1c fetches)
  - preferred_vocabulary — technical terms that anchor the scientific register
  - length_and_format_constraints — typical paper structure, pacing, citation patterns
{% endif %}

Starting material from Perplexity's §6:
{% if perplexity_sections %}
{{ perplexity_sections.get(6, "(Perplexity §6 not recognized; see full Perplexity block below)") }}
{% else %}
(Perplexity findings available as unstructured block below)
{% endif %}

{% if subtype == "system" %}
Section 6 is the corpus gateway for a non-human system. Pass 1c will fetch documents from the URLs you identify; Pass 1d will curate characteristic passages; Pass 4a will ground the voice directly in the legislation, Indigenous-authored scholarship, and environmental reports. The quality of this section determines the quality ceiling of every voice-level field.

Be specific throughout: statute citations with section numbers, scholarly publications with full references, URLs where publicly available, flagged restrictions where material is not publicly redistributable.

Your task for Section 6:

- FOUNDATIONAL LEGAL DOCUMENTS — each with full citation, URL where public, and brief description. For Whanganui:
  * Te Awa Tupua (Whanganui River Claims Settlement) Act 2017 (NZ statute; legislation.govt.nz)
  * Ruruku Whakatupua — Te Mana o Te Awa Tupua (2014 Deed of Settlement)
  * Waitangi Tribunal Whanganui River Report (Wai 167, 1999)
  * Treaty of Waitangi 1840 (as foundational background)
  * Earlier case law (Whanganui River Māori Trust Board v Attorney-General)

- COMPARATIVE LEGAL DOCUMENTS — Ecuador 2008 Constitution (Spanish authoritative + English); Bolivia Law 071 of 2010; Atrato T-622/16; Yurok Tribal Council Resolution 19-40; Spain Law 19/2022 (Mar Menor); Uttarakhand High Court 2017 Ganga/Yamuna judgment with Indian Supreme Court stay.

- INDIGENOUS-AUTHORED OR CO-AUTHORED SCHOLARLY ANALYSIS — for Whanganui: Linda Te Aho's papers on Whanganui legal personhood; Jacinta Ruru's work on Indigenous legal personhood; Whanganui iwi-authorised historical accounts. Cite each with full bibliographic reference. Distinguish community-member scholarship explicitly.

- NON-INDIGENOUS SCHOLARLY ANALYSIS — the peer-reviewed settler-authored or international scholarship. Cite with acknowledgement of the positionality.

- ORAL TRADITION DOCUMENTATION — sources where whakataukī, waiata, pūrākau specific to this entity have been documented with community authorisation. Cite; flag tapu material by reference, not content.

- ENVIRONMENTAL REPORTS — state-of-environment, monitoring, restoration. For Whanganui: Te Pou Tupua Te Heke Ngahuru annual reports; Horizons Regional Council SOE reports; NIWA catchment studies; DOC conservation plans. Each with date + URL.

- CHARACTERISTIC PASSAGES — 8 to 15 passages across legislation, legal analysis, Indigenous-authored scholarship, and environmental reports. For each:
    * Full citation with section/page reference
    * Primary purpose: "substance" (the legal, philosophical, or ecological claim), "voice" (how the legislation or Indigenous-authored scholarship articulates the relationship in its register), or "both"
    * Tier: Tier 1 (legislation, treaty text, Indigenous-authored primary) / Tier 2 (scholarly analysis) / Tier 3 (Western-science synthesis)
    * Approximate word count
    * Brief context — why this passage matters for voice construction

  Do NOT include full passage text in THIS dossier. Pass 1c fetches from URLs. Your job is to produce the citations Pass 1c uses as a fetch list.

- DIGITISED FULL-TEXT URLS — authoritative sources. NZ Legislation (legislation.govt.nz) for statutes; government / Crown-iwi-agreement repositories for deeds of settlement; iwi websites where material is community-authorised; peer-reviewed journal DOIs for scholarly analysis; regional-council websites for environmental reports. ONE authoritative URL per source.

- RESTRICTED MATERIAL — flag any material which, per CARE/IPAI guidance or explicit iwi statement, should NOT be redistributed or paraphrased. Name the restriction, not the content. Feeds hard_limits at extraction time.
{% else %}
Section 6 is the corpus gateway for a non-human organism. Pass 1c will fetch papers from the URLs you identify; Pass 1d will curate characteristic passages; Pass 4a will ground the voice directly in the scientific literature. The quality of this section determines the quality ceiling of every voice-level field.

Be specific throughout: full citations, DOIs, publication dates, URLs. Vague lists fail downstream.

Your task for Section 6:

- FOUNDATIONAL PAPERS AND MONOGRAPHS — texts that ground the voice. For each:
    * Full citation (author, year, journal + volume + pages, or publisher)
    * One-sentence description of what it contributes
    * Tier: Tier 1 (peer-reviewed primary research) / Tier 2 (scholarly synthesis or monograph) / Tier 3 (well-researched popular science, clearly distinguished)

- CHARACTERISTIC PASSAGES — 8 to 15 passages from the scientific literature that best serve voice construction. For each:
    * Full citation with section or page reference
    * Primary purpose: "substance" (the scientific claim) / "voice" (how scientists describe this behaviour in their published register) / "both"
    * Tier (as above)
    * Approximate word count
    * Brief context — why this passage matters

  Voice passages matter: the voice's register is shaped by the scientists' documented vocabulary. Do NOT include full passage text in THIS dossier. Pass 1c fetches from URLs.

- DIGITISED FULL-TEXT URLS — for open-access papers and public-domain monographs. PubMed Central, DOI links for open-access journal versions, Internet Archive for older works, preprint servers (bioRxiv, arXiv) where relevant. ONE authoritative URL per work. For paywalled essentials (Godfrey-Smith's Other Minds; Hanlon and Messenger's Cephalopod Behaviour), note the paywall and name the authoritative edition.

- FIELD GUIDES AND REFERENCE WORKS — where available. For Octopus: Jereb et al. FAO Cephalopods of the World (open access); Hanlon & Messenger Cephalopod Behaviour (Cambridge). For other organisms: equivalent authoritative references.

- ACTIVE RESEARCH GROUPS — laboratories producing current work. For Octopus: Hochner (Hebrew University), Hanlon (Woods Hole / MBL), Godfrey-Smith (Sydney), Ragsdale (Chicago). For each: institution, URL, lead investigator, one-sentence focus. Anchors for Pass 1-merge cross-reference.

- WHAT IS NOT AVAILABLE IN ENGLISH SCIENTIFIC LITERATURE — gaps where non-English or non-academic sources would add material. Flag honestly.

- POPULAR-SCIENCE SOURCES DISTINGUISHED FROM PEER-REVIEWED — where popular works (Montgomery's Soul of an Octopus; Godfrey-Smith's Other Minds, which straddles) have shaped public understanding. Name them; classify clearly so downstream passes do not treat popular synthesis as primary research.
{% endif %}

---

CROSS-DISCIPLINARY ADDITIONS (from Gemini broad scan — consult for any section):

{{ gemini_findings }}

{% if not perplexity_sections and perplexity_findings %}
---

FALLBACK: Perplexity output could not be split by section. Full output:

{{ perplexity_findings }}
{% endif %}

Cite all claims from peer-reviewed scientific literature{% if subtype == "system" %}, primary legal documents, and community-authorised Indigenous-studies scholarship{% endif %} where possible. For each major claim, note whether it represents scholarly consensus or a contested interpretation.

