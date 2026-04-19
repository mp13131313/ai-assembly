# A repeatable AI pipeline for building 13 philosophical personas

**The most effective approach uses a four-stage, multi-model pipeline — Perplexity for cited research, Claude for philosophical synthesis, ChatGPT Deep Research for deep dives on complex figures, and cross-model verification — with each persona built section-by-section rather than in a single pass.** This matters because current evidence on context degradation, hallucination rates, and model-specific strengths makes single-tool, single-pass approaches unreliable for documents requiring both factual accuracy and intellectual depth. The pipeline below can produce 12–13 complete persona specifications in **30–50 hours over 4–6 weeks**, with the first 2–3 personas taking longer as the process is calibrated.

---

## Which tool excels at which template sections

No single deep research tool handles all 11 sections well. The tools have sharply different strengths, and matching them to sections cuts both error rates and generation time.

**Perplexity Deep Research** is the clear winner for Section 1 (Identity & Framing) — biographical facts, period context, primary texts, secondary scholarship. Its inline sentence-level citations achieve **85% accuracy** in independent testing, and it processes queries in 2–5 minutes versus 5–30 for competitors. At $20/month for Pro with approximately 500 queries/month, it also has the most generous budget for batch work across 13 voices. Use it to generate a sourced research dossier for every figure.

**Claude** (Opus 4.6 or Sonnet 4.6, with Research mode and Extended Thinking) is strongest for Sections 2, 3, and 4 — the philosophical constitution, reasoning method, and voice/style sections that demand nuance. Independent assessments consistently rate Claude's writing as the most human-like and philosophically aware. Its **1M-token context window** can hold an entire primary text (the complete Republic, Ambedkar's Annihilation of Caste) alongside the template, and its **128K output token limit** provides ample room for long structured generation. Claude's Extended Thinking mode sustains reasoning chains of up to 100 steps, making it ideal for extracting *how* a thinker reasons rather than merely *what* they concluded. Claude Research mode operates agentically — spawning parallel sub-searches without a rigid per-query cap like ChatGPT's.

**ChatGPT Deep Research** (full model, GPT-5.2-based) is best reserved for the hardest analytical tasks: populating Section 2 for less-documented figures where obscure scholarly sources must be synthesized, and Section 7 (Example Chains) where its executive-briefing-style output produces the most comprehensive multi-step demonstrations. Its limitation is severe: **Plus users get only 10 full-model + 15 lightweight queries per 30-day rolling window**. Treat each query as precious — batch all sub-questions for a single persona into one comprehensive prompt.

**Gemini Deep Research** fills a useful but narrower role. Its 1M-token context and free-tier access make it valuable for initial broad scans and for exporting research to Google Docs for team collaboration. However, an academic researcher testing it on Buddhist philosophy found it **"unusable for basic humanities research"** due to unreliable sourcing — outputs looked authoritative but contained errors only a domain expert would catch. Use Gemini for breadth-first discovery, not for philosophical depth. Gemini's "Deep Think" mode is entirely STEM-focused and adds nothing to humanities work.

For **non-human entities** (Octopus, Pachamama), the tool assignment shifts. Perplexity gathers the scientific literature (octopus cognition research, Rights of Nature legal frameworks). Claude then performs the creative-philosophical synthesis, where its Constitutional AI training and nuanced ethical reasoning produce more grounded, less anthropomorphized results than ChatGPT's sometimes over-enthusiastic creativity. ChatGPT can supplement with Section 7 example chains where creative generation strength matters most.

| Template Section | Primary Tool | Secondary Tool | Rationale |
|---|---|---|---|
| S1: Identity & Framing | Perplexity | Gemini (broad scan) | Factual, citation-dependent |
| S2: Philosophical Constitution | Claude (Extended Thinking) | ChatGPT DR (obscure figures) | Requires deep reasoning over primary texts |
| S3: Reasoning Method | Claude | — | Reasoning-pattern extraction from texts in context |
| S4: Communication Style & Voice | Claude | — | Most human-like voice analysis |
| S5: Knowledge Boundaries | Perplexity + Claude | — | Factual scope + analytical framing |
| S6: Behavioural Boundaries | Claude | Human curation | Requires judgment, not just research |
| S7: Example Chains | ChatGPT DR | Claude | Creative synthesis + comprehensive output |
| S8: Governance Protocol | Claude | — | Analytical + creative |
| S9: Evaluation Rubric | Human-led | Claude for drafting | Requires project-specific judgment |
| S0: Provocateur Profile | Claude | — | Derived last from all other sections |
| S10: Artifact Specification | Claude | — | Medium-specific creative framing |

---

## Why multi-pass generation is non-negotiable

The evidence against single-pass generation for an 11-section document is overwhelming. A 2025 Chroma Research study testing 18 frontier models found that **every model's performance degrades as input context grows**, even when nowhere near the context window limit. The Stanford "Lost in the Middle" finding — a **30%+ accuracy drop** for information positioned in the middle of the context — means that in a single-pass generation, Sections 5–7 would receive significantly worse attention than Sections 1–3 or 10–11. Separately, practitioners report quality degradation accelerating after the first **800–1,000 words** of output, making single-prompt generation unreliable for documents exceeding 3,000 words.

The recommended architecture is **modular section-by-section generation with coherence threading**:

**Phase 1 — Research dossier** (one run per persona). Use Perplexity Deep Research to generate a comprehensive, cited research document organized by template section. For well-documented figures, this takes 15–20 minutes. For less-documented figures, supplement with Claude Research mode and ChatGPT Deep Research.

**Phase 2 — Section-by-section generation** (3–5 runs per persona). Generate 2–3 template sections per run using Claude, feeding it: (a) the full template outline for structural awareness, (b) the Perplexity research dossier, (c) previously completed sections compressed into a "voice and thematic summary" rather than full text, and (d) section-specific instructions. Place the current section's requirements at the **beginning and end** of the prompt — never in the middle — and reiterate key instructions immediately before the generation request. Research shows this recovers up to **85% of attention drift**.

**Phase 3 — Coherence review** (one run per persona). A final Claude pass checks cross-section consistency: does the reasoning method in S3 actually reflect the principles in S2? Does the voice in S4 match the example chains in S7? Does S0 (Provocateur Profile) accurately compress the full persona?

The tradeoff between coherence and depth resolves clearly in favor of multi-pass with threading. A single pass produces surface-level coherence but shallow analysis; multi-pass with compressed summaries of prior sections produces both depth *and* coherence.

**Budget math for ChatGPT Deep Research**: With 10 full-model queries per 30-day window, allocate one full-model query per persona for the deepest analytical task (usually S2 or S7 for complex figures). Use lightweight queries for supplementary research. Plan for a **2-month window** to complete all 13 personas through ChatGPT, while using Claude Research (no rigid cap) and Perplexity (500 queries/month) for the bulk of the work.

---

## Prompt architecture that prevents generic output

Simple role prompting — "You are a scholar of Platonic philosophy" — shows **minimal to no improvement** on accuracy tasks and sometimes degrades performance, according to PromptHub's 2025 analysis. What works is detailed, specific expert identities combined with structural constraints. The prompt for each section generation should contain four blocks:

**Block 1 — Expert Identity** (detailed, not generic). Instead of "You are a Plato scholar," specify: "You hold deep expertise in the Platonic dialogues and their reception history across Neoplatonist, Islamic, and analytic traditions. You distinguish between dramatic-literary readings (Griswold, Nussbaum) and doctrinal readings (Vlastos, Fine). You recognize that Plato never speaks in his own voice in the dialogues, and that the relationship between Socrates-as-character and Plato-as-author remains contested."

**Block 2 — Anti-hallucination guardrails**. Include in every generation prompt:
- Only attribute direct quotes that appear in known primary sources, with work title and section reference. If paraphrasing, mark explicitly as "[paraphrased from scholarly consensus]."
- Before including any concept, verify: would this figure have had access to this concept in their historical period? If not, do not use it without explicitly flagging the anachronism.
- When evidence is ambiguous, say so. Do not resolve genuine scholarly debates into false consensus.
- For each major claim, identify whether the source basis is primary text, scholarly consensus, or inference. Flag inferences explicitly.

**Block 3 — Depth and process requirements**. The critical innovation is prompting for *how* a figure thinks, not just *what* they concluded. Two techniques work well:

The *dialectical process prompt* asks: "What questions does this figure characteristically ask when confronting a new problem? What assumptions do they typically challenge? What evidence or reasoning do they find most compelling? What form do their arguments typically take (analogy, formal logic, narrative, dialectic)? How do they respond to counterarguments? What do they consider settled versus still open for debate?"

The *scenario-based elicitation* prompt asks: "Describe how this figure would approach [a dilemma relevant to their era]. Walk through their reasoning step by step, noting what they would notice first, what framework they would apply, what tensions they would identify, and how they would resolve or sit with those tensions."

**Block 4 — Differentiated instructions by persona type**. For well-documented figures (Plato, Ambedkar): mandate source attribution, provide key primary source excerpts in the prompt, cross-reference multiple scholarly traditions. For less-documented figures: "Where biographical details are sparse, note this honestly rather than fabricating plausible-sounding details. Use contextual inference about the era and social conditions, clearly marked as inference." For non-human entities: ground in documented scientific research (octopus cognition) or legal/philosophical frameworks (Rights of Nature) rather than creative invention.

---

## The non-human voices require a fundamentally different methodology

The Octopus and Pachamama personas cannot follow the standard biographical-research pipeline. They require what might be called **ontological construction from constraint** — building a philosophical framework from documented properties of the entity rather than from any textual corpus.

For the **Octopus**, the grounding literature is remarkably specific. Peter Godfrey-Smith's *Other Minds* (2016) describes the octopus nervous system: **two-thirds of its 500 million neurons reside in the arms**, creating semi-autonomous processing in each limb. This is not metaphor — it is documented neuroscience that implies a genuinely distributed form of cognition. The research prompt should instruct: "Ground this persona in the distributed nervous system architecture. Reasoning should reflect network-based rather than hierarchical cognition — multiple simultaneous explorations rather than sequential deduction. Use tactile, chemical, and multi-sensory language rather than visual-dominant metaphors. The octopus has experienced 600 million years of divergent evolution from vertebrates; its intelligence is not 'lesser human intelligence' but a fundamentally different cognitive architecture."

The anti-anthropomorphization guardrail is specific: ban centralized-hierarchy metaphors for cognition, ban projection of human emotional states, ban land-based or visual-dominant metaphors. The octopus's reasoning method (S3) should reflect exploration-based, adaptive, non-hierarchical problem-solving — probing a question from multiple angles simultaneously rather than building a linear argument.

For **Pachamama/Earth**, the challenge is deeper and carries ethical weight. Ecuador's 2008 Constitution (Articles 71–74) — the first to grant legal personhood to nature — provides one grounding framework. Bolivia's Law 071 (2010) defines Pachamama as "the dynamic living system comprised by the indivisible community of all life systems." But the Indigenous Protocol and Artificial Intelligence Position Paper (Lewis et al., 2020) establishes that Indigenous epistemologies foreground **relationality, land-based intelligence, and spiritual responsibility** — and that AI representations of Indigenous knowledge without community involvement risk cognitive imperialism. The prompt must acknowledge these limitations explicitly and cite specific Indigenous thinkers (not generic "indigenous wisdom"). Ground the persona in Andean concepts of *ayni* (reciprocity) and *buen vivir* (good living), systems thinking drawn from Earth system science, deep-time perspective, and cyclical rather than linear temporality.

---

## A four-phase verification protocol catches the real failure modes

Hallucination rates vary dramatically by task type: **0.7% on grounded summarization** (sticking to provided documents) but up to **48% on open-ended factual recall** (o4-mini on PersonQA). For persona generation — which mixes grounded synthesis with open-ended philosophical interpretation — expect citation fabrication rates of **6–29%** depending on how well-documented the figure is. A critical finding from MIT: models are **34% more likely to use confident language** ("definitely," "certainly") when generating incorrect information. The more wrong the AI sounds, the more authoritative it reads.

**Phase 1: Automated citation check**. Every direct quote must be verified against a primary text database — Perseus Digital Library for ancient philosophers, BAWS (Dr. Ambedkar's collected works) for Ambedkar, Project Gutenberg and Google Books for modern figures. Use GPTZero's Hallucination Check tool for batch verification of reference lists. Check DOIs via CrossRef. The practical red flag: quotes that sound "too perfect" for the argument being made, or quotes with precise page numbers but no verifiable source.

**Phase 2: Cross-model critique**. Generate with one model family, critique with another — this is essential because self-preference bias runs **10–25%** (GPT-4o scores its own outputs ~10% higher; earlier Claude models showed ~25% self-preference). The critique prompt should be rubric-based: "Identify any claims about [Figure] that are factually incorrect. Flag any quotes you cannot verify as authentic. Rate the distinctiveness of this voice 1–5 with justification. Identify any anachronistic framings." The "LM vs LM" paper demonstrates that cross-examination through multi-turn interaction effectively reveals inconsistencies implying factual errors.

**Phase 3: Distinctiveness testing**. The **"swap test"**: can a paragraph be attributed to a different philosopher with minimal changes? If yes, it's too generic. The **blind identification test**: present unlabeled excerpts from different persona documents to reviewers — can they identify which philosopher is being represented? The **cross-persona question test**: ask all 13 personas the same philosophical question (e.g., "What makes a decision legitimate?") and compare responses for vocabulary distinctiveness, argumentative style, values revealed, and metaphor choices. If three personas give substantially similar answers, the voices aren't differentiated enough. The PersonaGym framework (Samuel et al., 2024) provides a validated five-dimension scoring rubric — action justification, expected action, linguistic habits, persona consistency, and toxicity control — that can be adapted for philosophical personas.

**Phase 4: Human expert review**. Research by Schwitzgebel et al. (2024, *Mind & Language*) — who fine-tuned GPT-3 on Daniel Dennett's works and compared outputs to real Dennett — found that domain experts could distinguish AI-generated philosophical text from genuine philosopher text **above chance but below expectations**. This means expert review catches real errors that automated checks miss, particularly: internal tensions that have been falsely resolved, positions that have been sanitized by alignment training (a documented tendency — AI chatbots representing historical figures "may make some individuals seem less racist and more remorseful than they actually were"), and the difference between encyclopedia-level summary and genuine intellectual engagement.

---

## The complete weekly workflow for a 4–6 week sprint

**Week 1: Pipeline calibration (3 personas — well-documented figures)**

Start with the best-documented voices (e.g., Plato, Ambedkar, and one other well-documented figure). These establish the template, reveal prompt weaknesses, and produce reference-quality outputs against which later personas can be benchmarked.

Per persona (~3–4 hours for the first three):
- **Step 1** (20 min): Perplexity Deep Research — comprehensive research dossier with citations, organized by template section
- **Step 2** (15 min): Human review of dossier — flag gaps, add domain expertise notes, identify primary text excerpts to include
- **Step 3** (60–90 min): Claude section-by-section generation — S1 + S5 first (factual sections), then S2 + S3 (philosophical core), then S4 + S6 (voice and boundaries), then S7 + S8 (examples and governance), then S10 + S0 (artifact spec and provocateur profile, derived last). Feed compressed summaries of completed sections forward.
- **Step 4** (30 min): Cross-model critique — feed completed document to a different model with rubric-based evaluation prompt
- **Step 5** (30 min): Human review focusing on voice, philosophical texture, anachronism detection
- **Step 6** (15–30 min): Revision pass addressing all flagged issues

After completing three personas, review the process: Which prompts produced generic output? Where did hallucination occur? Which sections needed the most human intervention? Revise the master prompt templates before proceeding.

**Weeks 2–3: Batch production (7–8 personas — mixed documentation levels)**

With calibrated prompts, throughput increases to **2–2.5 hours per persona**. Run Perplexity research queries for 3–4 figures simultaneously while synthesizing completed ones. Use ChatGPT Deep Research full-model queries strategically — one per complex figure for the deepest analytical section. Schedule these to align with the 30-day rolling reset window.

For less-documented figures, add an extra research step: Claude Research mode for iterative, multi-angle investigation before the dossier is finalized.

**Weeks 4–5: Non-human entities and cross-persona quality control**

The Octopus and Pachamama personas require **4–5 hours each** because the research phase is broader (spanning neuroscience, philosophy of mind, legal theory, Indigenous studies) and the creative synthesis phase requires more human judgment. Build the research dossier from scientific literature and philosophical frameworks rather than biographical sources. Generate with Claude, emphasizing the anti-anthropomorphization guardrails.

Run cross-persona quality control: the blind identification test across all 13 voices, the same-question distinctiveness test, and stylometric analysis (word frequency, sentence length distribution, unique vocabulary ratio) to quantify differentiation.

**Week 5–6: Section 4 negative constraints and Section 9 stress tests**

These sections can only be populated through testing — they require running each persona through edge cases and observing failures. Banned vocabulary, banned framings, and banned registers (S4 negative constraints) emerge from watching the persona default to generic philosophical language, anachronistic framing, or out-of-character register. Stress tests (S9) require adversarial prompting — presenting each persona with deliberately provocative, boundary-crossing, or trap questions. Use the DeepEval/DeepTeam open-source framework for systematic red-teaming.

---

## Guardrails that address the six specific failure modes

**Failure 1: Encyclopedia-level summary**. The detection test: compare the persona document against the figure's Wikipedia article. If it reads like a more polished Wikipedia entry, it lacks depth. The prompt fix: "Include internal tensions in the figure's thought, evolution of their ideas over time, minority scholarly readings, and specific engagement with individual arguments or passages — not overviews."

**Failure 2: Fabricated quotes**. Citation fabrication rates reach **29% for niche topics**. The fix is structural: require the AI to generate quotes with specific work title, edition, and section/page number, then verify every single one against digitized primary texts. Never include unverified quotes in the final document. The Chain-of-Verification approach (asking the model to re-read each claim and identify its source basis) reduces hallucination by **up to 36%**.

**Failure 3: Generic philosophical positions**. The swap test catches this efficiently. Additionally, require the AI to include **3+ concepts, terms, or arguments unique to each philosopher** with precise textual references. "Virtue ethics" is generic; "the function argument in *Nicomachean Ethics* I.7, where Aristotle identifies the *ergon* of humans as rational activity in accordance with *arete*" is specific.

**Failure 4: Anachronistic framing**. Include a temporal constraint block in every prompt listing concepts that did *not* exist in the figure's era. For ancient figures: "human rights," "democracy" (in the modern liberal sense), "consciousness" (in the phenomenological sense), "identity." When modern relevance is needed, frame as: "A reader applying this figure's principles might..." — never "This figure believed in..."

**Failure 5: Flattening complex thinkers**. The most insidious failure because it looks correct. Plato reduced to "the Forms," Ambedkar reduced to "anti-caste activism," Nietzsche to "will to power." The fix: require the persona document to address how the thinker's positions evolved over their lifetime, identify at least two genuine tensions or contradictions in their thought, and represent minority scholarly interpretations alongside dominant ones.

**Failure 6: Anthropomorphizing non-human entities**. For the Octopus: ban centralized cognition metaphors, ban human emotional vocabulary, require distributed/network-based reasoning patterns. For Pachamama: ban "Mother Nature" sentimentality, require grounding in specific Indigenous philosophical concepts (ayni, buen vivir) and legal frameworks (Ecuador Constitution Articles 71–74), and acknowledge explicitly that the persona is a constructed representation, not an authentic Indigenous voice.

---

## The emerging practitioner consensus and precedent projects

The multi-model research pipeline — **Perplexity for research, Claude for analysis, ChatGPT for structured output, Claude for refinement** — is now documented across multiple published guides including ClickForest's practitioner guide, AiZolo's academic workflow documentation, and a Udemy capstone course that follows exactly this pattern. The "research brief → source document → system prompt" pipeline exists in practice (Character.AI's open-sourced Prompt Poet system uses Jinja2 templates to construct system prompts from structured research data) though it has not been formally named as a methodology.

The most scientifically rigorous precedent is the **Habermas Machine**, published in *Science* in 2025, which demonstrated that AI can mediate multi-voice philosophical deliberation — with N=5,734 participants rating AI-generated group statements as more informative and less biased than human-mediated ones. The Stark Insider "Fictional Symposium" at the Louvre demonstrated the art-installation concept directly: nine historical voices (Duchamp, Van Gogh, Frankl) each maintaining documented philosophical positions in generative dialogue. An arXiv study analyzing 83 persona prompts in academic research found that **74% insert research data as dynamic variables** into structured templates, validating the data-driven approach, though critically noting that "some persona prompts appear 'shallow' — they do not exhibit detailed understanding of persona theory."

---

## Conclusion: what makes this pipeline work

Three principles distinguish an effective persona-creation pipeline from one that produces 13 variations of the same generic philosophical voice. First, **tool-section matching** — using each AI's documented strengths rather than forcing one tool to do everything — cuts both error rates and production time. Second, **multi-pass generation with coherence threading** solves the depth-versus-coherence tradeoff that single-pass approaches cannot. Third, **cross-model verification** exploits the documented 10–25% self-preference bias by ensuring no model ever judges its own output.

The non-obvious insight is that the hardest sections to populate well are not the factual ones (S1, S5) but the *process* sections — S3 (Reasoning Method) and S4 (Communication Style). These require prompting that captures *how* a thinker moves through a problem, not just where they land. The dialectical-process prompt and scenario-based elicitation techniques described above are the most reliable methods currently documented for extracting this. The total investment for 13 personas — approximately 40 hours of combined human and AI time over 5 weeks, plus $40–60/month in tool subscriptions (Perplexity Pro + Claude Pro, supplemented by ChatGPT Plus) — is realistic for a small team operating within the collaborator's 2.5–4 hour per-voice estimate.