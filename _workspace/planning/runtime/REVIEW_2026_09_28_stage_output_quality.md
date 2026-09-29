# Review: each stage's Athens output against what the provotype is for

**Date:** 2026-09-28 · **Reviewer:** Claude Fable 5.1 (`claude-fable-5-1`), one session, read-only
**Brief:** `_workspace/planning/BRIEF_2026_09_28_stage_quality_review.md`
**Checkout:** `phase0-fixes` at `3b185f2` (detached). The two commits after the brief (`02006f5`, `3b185f2`) touch no Researcher prompt or spec.
**Status:** Part A (Researcher) is written. **Part B and the synthesis wait for the operator's answer at the checkpoint.**
**Uncommitted.** No API calls. `athens-2026` was only read.

---

## Summary

The operator's reading holds, and it can be stated precisely: **the Researcher's clusters and themes are inventories, not findings.** All 86 cluster abstracts make "the items" their grammatical subject, and 74 of them are em-dash lists. All 24 theme abstracts are routing tables that cite cluster ids. Nothing at cluster or theme level says what the room settled, what nobody challenged, or what nobody said.

The flatness is designed, not accidental:
- The spec calls the Researcher "unbiased … not an editorial voice".
- The v2.4 clustering prompt explicitly bans "declarative findings".
- The clustering call is never shown who disagreed with whom.

It shows most at Athens because Athens barely argued. Only 6% of the 529 extractions were `challenged`. On the Munich Security Conference test set the prompts were validated on, the figure was 32%, and there the same prompts produced positioned themes.

The edge is not lost. The extractions carry it, especially the Researcher's own synthesized open questions, and the Provocateur's formulations recover it by reading raw extractions. But three things are wrong with how it is recovered:
- It happens per voice, up to nine times per theme, and never reaches the record the operator browsed.
- Triage and selection read only the flat abstracts, so they cannot tell a contested theme from a consensual one. All 22 fault lines have the form "whether A, B or C", and the most contested theme of Night 1 was dropped.
- The one Night-3 report that the Assembly had "visibly shifted the room" ended as an isolate.

**Recommendation:** add a separate "room reading" per theme and per night, with evidence ids for every sentence: what the room settled, what stayed open, what went unchallenged, what nobody said. Keep it apart from the neutral layer, and send it first to Provocateur triage and the record, not to the voices.

**Part B follows the checkpoint.**

---

## The goals this review judges against

The review measures against these goals, quoted from the project's own documents. Short labels are used below.

| Label | Goal | Source |
|---|---|---|
| **G1 Not a summary** | "The default behaviour of any LLM system is to summarise; this Assembly is designed to do the opposite. If the artifacts merely reorganise the day's discussions into pretty prose, the provotype has failed." | Briefing v3.1, "What it is not" |
| **G2 Tensions, not consensus** | "Not a consensus machine. The Assembly exposes tensions rather than resolving them." / "Expose tensions, don't resolve them." | Briefing, "What it is not" + Design principles |
| **G3 Generative** | "could the humans in the room have arrived here without this voice? If yes, the provotype has failed." | Briefing, Design principles |
| **G4 Opinion demands response** | "An opinion demands agreement, disagreement, or reckoning with why you're dismissing it." | Briefing, Design principles |
| **G5 Construction visible** | "Every layer of translation — from human discussion to Researcher extraction, from extraction to Provocateur formulation … — is visible somewhere." | Briefing, Design principles |
| **G6 Layer 3 evidence** | "Attendees reference the Assembly's artifacts in the day's human sessions … The Researcher captures these references in Night 2 and Night 3's transcripts, which means Night 2 and Night 3 can respond to them." | Briefing, "What success looks like" |
| **G7 Against hospitality** | "their well-curated openness is itself the failure mode: they are too good at performing reception to know when they are not actually being changed." It goes flat on "Standard progressive talking points without edge". It activates on "Naming of contradictions the room holds but rarely articulates." | AUDIENCE_BRIEF, Activation and failure conditions |
| **G8 Specificity and disagreement** | "Caption-style labels, precise attributions, explicit disagreement markers … When in doubt, choose the forensic over the evocative." Also: "Empty quadrants are more provocative than populated ones." | DesignPrinciples §7, §8 |
| **G9 Comparing** | "Two positions, pick which is closer to yours … Kills it: a neutral/both option." | Nine Modes §1 |
| **G10 The Researcher's own contract** | "The Researcher is unbiased … It captures what was discussed and flags which extractions carried high energy in the room — nothing more. It is a design research instrument, not an editorial voice." | Researcher spec, Overview |

**G10 pulls against G1, G2 and G7.** The project as a whole is designed against summary and against hospitable absorption. The Researcher is the one stage that is told to summarise faithfully and add nothing. Part A is mostly about what that tension produced.

---

## Method and evidence base

**Read in full:**
- the Briefing, the Design Principles, the Nine Modes, the Frame Concept and the AUDIENCE_BRIEF;
- the Researcher spec;
- the three Researcher prompts, which are byte-identical to the spec except for two closure sentences, and whose git history shows no change since 2026-04-16, so Athens ran the validated v2.4 prompts;
- `researcher_flow.py` prompt assembly (`build_extraction_user_prompt`, `cluster_extractions`, `group_clusters_into_themes`);
- the Provocateur spec (overview, triage, formulation);
- `DATA_INVENTORY.md` and `EDITORIAL_ASSESSMENT.md`;
- the data explorer's Conference Data renderer in `build_athens_data_graph.py`.

**Athens data read directly:**
- all 24 themes and 86 clusters of all three nights, with abstracts;
- whole-session extraction sets from five different session types: a two-speaker panel (N1 *Human Democracy Is Dead* audio), audience reflections (N1 *Birthplace of Democracy Tour*), a staged board meeting (N2 *Clash of the Titans*, both captures), a workshop with scoring (N3 *Citizen Assembly with AI*) and a main-stage closing (N3 *Beastopia*);
- all extractions inside the clusters rewritten below;
- all 46 Night-1 formulations, all nine Night-3 theme_003 formulations and narratives, one full briefing (Plato N1), one Step 1 response and one Step 2 artifact.

**Offline scripts** (scratchpad only; they read JSON and count, nothing else):
- `stats.py`: lens, engagement and energy counts per night;
- `themes.py`, `clustersess.py`: theme and cluster dumps, plus how many sessions feed each cluster;
- `sess.py`: whole-session extraction dumps;
- `assembly_refs.py`: every extraction mentioning the Assembly or a voice, and where it landed;
- `flags.py`: triage flags and selection per night;
- `forms.py`: formulation texts, and the lens/engagement mix of each formulation's grounding;
- `textstats.py`: abstract grammar, fault-line form, and challenged items per theme.

The MSC comparison uses `projects/current-tests/dev_msc_test/02_researcher/`, the v2.4 validation run the spec cites.

**Session short-names used in ids below.** Every id is `<night> <short-name>:NNN`, where NNN is the extraction's number within its session.

| Short name | Full `session_id` |
|---|---|
| `hdid_audio` | `day_one_demos_ai_democracy_marathon_human_democracy_is_dead_1330__audio` |
| `hdid_refl` | `day_one_demos_ai_democracy_marathon_human_democracy_is_dead_1330` (reflections) |
| `mthd` | `day_one_mikro_pallas_ai_democracy_marathon_the_more_than_human_democracy_1445` |
| `birthplace` | `day_one_demos_ai_democracy_marathon_departme_birthplace_of_democracy_tour_1000` (reflections) |
| `act_one` | `day_one_theatre_main_stage_act_one_the_story_of_us_2000` |
| `clash`, `clash_a2` | `day_two_theatre_main_stage_act_three_clash_of_the_titans_1045` (+ `__audio2`) |
| `citizen` | `day_three_demos_ai_democracy_marathon_citizen_assembly_with_ai_1400` |
| `mpga` | `day_three_demos_ai_democracy_marathon_make_politics_great_again_1600` (reflections) |
| `beastopia` | `day_three_theatre_main_stage_act_five_beastopia_2000` |

---

# Part A — The Researcher

## A.1 See it: the data at a glance

All figures below are CONFIRMED, counted by the scripts above.

| | Extractions | challenged | reinforced | unengaged | Clusters | single-session clusters | Themes | Isolates |
|---|---|---|---|---|---|---|---|---|
| Night 1 | 205 | 14 (7%) | 74 | 87 | 37 | 18 | 11 | 0 |
| Night 2 | 199 | 13 (7%) | 73 | 84 | 35 | 29 | 8 | 2 |
| Night 3 | 125 | 5 (4%) | 46 | 55 | 14 | 8 | 5 | 3 |
| **Athens** | **529** | **32 (6%)** | 193 | 226 | 86 | **55** | 24 | 5 |
| MSC test (v2.4 validation) | 106 | **34 (32%)** | 21 | 38 | 25 | 21 | 6 | — |

**Notes on the table:**
- The remaining extractions are open questions, which carry no engagement label.
- On Athens audio panels alone, 7% were challenged; on reflections, 4%. So the low rate is not an artifact of the reflection format.
- **The extractions are good.** They are specific, attributed and carry their context. The Researcher's own synthesized open questions (`speaker: null`) often carry the sharpest observation in a session. Example, N1 `hdid_audio:011`: *"does the optimistic finding generalize beyond a self-selected sample?"* with context *"the room did not interrogate this."*
- **The flatness sets in at clustering.**

## A.2 Name what the operator means

"No finding in itself" and "no position" come down to six concrete things in this data.

### 1. No verdict on the room

No cluster or theme says what the day **settled**, what it **left open**, or what went **unchallenged**. The information needed is in the data; the grouping layer never uses it.

- **N1 theme_005 "Diagnosing modern democracy's hollowness".** 28 extractions from six sessions; **0 challenged**. The abstract: *"These clusters wrestle with what modern democracy is for and whether it is dying — cluster_009 takes the obituary frame seriously, cluster_013 diagnoses drift…, cluster_014 argues for active defense…"*. Twenty-eight positions and not one contested: that is the finding, and the abstract doesn't state it.
- **N2 *Clash of the Titans* (30 extractions across both captures): 0 challenged.** No speaker defended the layoff plan; the only case for it was the scripted "interns' pitch" (`clash:002`, context: *"Responding to the interns' pitch to cut 5,000 FTEs"*). The Researcher's theme_004 abstract calls this *"a coherent governance argument"*. It adopts the stage's consensus as a structure instead of noticing that the clash had no second side.

### 2. Consensus is recorded as "convergence", or erased

The binding vocabulary turns agreement into a neutral pattern. Fifteen cluster abstracts open with "All …" (e.g. N1 cluster_010, *"All argue democracy's organizing aspiration should be aliveness…"*).

In one case, the abstract **misstates** where the room stood:
- N3 cluster_002 (25 items, the largest cluster of the run) says the items *"engage the prompt …, taking positions across the 1–5 spectrum"*.
- The extractions say otherwise: *"nearly the whole room scored 4 or 5 out of 5"* (`beastopia:005`), *"a unanimous-5 group"* (`citizen:013`), *"Takes a softer position (~4) than Claudia"* (`citizen:004`).

The room was near-unanimous. "Across the spectrum" is the neutral reporter's habit of making every room look plural (inference, but the ids above show the gap).

### 3. The grammar of the abstracts is an inventory

CONFIRMED from `textstats.py`:
- **Cluster abstracts:** 86 of 86 take the items as subject ("Items …", "All …", "Eight items …", "Arc …"). 74 of 86 carry an em-dash list, and 17 contain a trailing qualifier ("with one item …", "while …", "without resolving …"). Typical: N1 cluster_002, *"All argue or test the claim that AI can be designed … as a thinking partner … — with one item flagging selection-effect worries about the optimistic finding."* The one sharp item (`hdid_audio:011`, above) survives as a trailing clause.
- **Theme abstracts:** 24 of 24 cite cluster ids inline. Only 5 contain any claim verb ("reveal", "argue that", "show that"), and in those the claim is the speakers' claim restated. Typical: N1 theme_001, *"cluster_001, cluster_005, and cluster_006 together challenge the prevailing framings of AI from three different angles — … (cluster_001), … (cluster_005), … (cluster_006)."* That is a table of contents with the cluster ids in brackets.
- **Titles:** read like conference-report headings: "Myth as analytical lens", "Late-life flourishing reframed", "Inhabiting the future", "Democracy's deeper conditions". None could be disagreed with.

### 4. The Researcher's own noticing doesn't survive grouping

- The clustering prompt names a **"shared blind spot"** binding: items that *"all assume something without arguing it"*. **0 of 86 Athens clusters use it** (CONFIRMED: every regex hit for "assum/blind spot/never/nobody" was a content word, not the binding).
- Yet the extraction layer does notice. For example:
  - N3 `mpga:025`: *"The session contains both diagnoses but no engagement between proponents of each path."*
  - N1 `hdid_audio:010`: the many-AIs claim was *"never tested against the structural reality of AI market concentration."*
- These synthesized open questions are where the Researcher already does what the operator is asking for. Clustering files them as one item among many.

### 5. Where positions appear, they are borrowed from one speaker

The only cluster titles with a position in them restate a single speaker's thesis, because the cluster *is* that speaker's talk:
- "Civilization as Goliath: collapse and inequality" (N2 cluster_028; nine items from Luke Kemp's talk);
- "Predictions and surveillance as veiled commands" (N2 cluster_025; *"Véliz's frame"*);
- "AI-driven layoffs as cover, not transition" (N2 cluster_019; the Clash panel's shared view).

55 of 86 clusters draw on a single session. On Night 2 the dominant session supplies 94% of a cluster's items on average. So a cluster is mostly **one session's digest on one topic**, and a theme is a list of session digests under a heading. That is why the output reads like a conference report: structurally, it is one.

**Caveat:** the MSC validation run also had 21 of 25 single-session clusters. This is how the method works, not an Athens regression.

### 6. The sharpest thing in the room gets flattened or dropped

- **N1 `mthd:007`** (high energy, reinforced), the Assembly's octopus voice spoken into the room by its operator: *"the audience granted personhood to rivers and nature precisely because they cannot show up to claim power, and withheld it from AI because AI threatens to actually claim a position."* It is the most-cited extraction of Night 1 downstream (see A.4). Cluster_008 absorbs it as *"Items wrestling with whether non-human entities — rivers, forests, AI, octopus voices, AI-generated Cleopatras and Platos — can or should be granted voice"*: the diagnosis of the room's bias becomes a topic.
- **N3 `beastopia:006`** (high energy): the report that *"An AI Assembly artifact, speaking in the voice of an octopus, intervened in a game show vote and visibly shifted the room."* It is **an isolate**. The Provocateur "does not process isolates" (spec), so it never reached a voice or the editor. In the explorer it is visible only inside its session's extraction list: `build_athens_data_graph.py` stores `theme_isolates` but draws no isolates section, and the theme view never shows it. This is the one piece of Layer-3 evidence (G6) in three nights of transcripts. A keyword search of every Night 2 and Night 3 transcript found no other audience reference to an Assembly artifact (CONFIRMED; the search script is inline in this session).

### Operational definition

The six points above add up to one test. **A finding is a sentence about the day that a participant could dispute.** "Twenty-eight defences of democracy and not one was challenged" is disputable: someone could point to a challenge. "These clusters wrestle with what modern democracy is for" is not.

By that test, the Researcher's grouping layer produced **zero findings of its own** across 24 themes. This is an inference from reading all 24 abstracts; the five that contain a claim restate the speakers' claims. The extraction layer produced several, all in synthesized open questions.

## A.3 The contrast: what the Researcher could have said

**These are illustrations, not proposals for prompt text.** Each is written only from the extractions in that cluster or theme; the evidence is listed so each sentence can be checked.

### Illustration 1: N1 theme_005 (5 clusters, 28 extractions)

**As produced:**
> **Diagnosing modern democracy's hollowness** — These clusters wrestle with what modern democracy is for and whether it is dying — cluster_009 takes the obituary frame seriously, cluster_013 diagnoses drift and hollowing, cluster_014 argues for active defense as still the best system, and cluster_010 and cluster_011 redirect the underlying purpose toward aliveness and the productive holding of tension rather than resolution by vote.

**Positioned (illustration):**
> **The day agreed democracy is worth saving without agreeing what it is.** Twenty-eight extractions across six sessions defend or diagnose democracy; none was challenged. They use the word for at least four things — a procedure that settles tension by vote (cluster_011), aliveness and flourishing (cluster_010), the holding of opposing views (cluster_011), and a regime under attack that must be defended (cluster_014). The one objection to the day's own premise — that "human democracy is dead" presumes a democracy Black women in the U.S. never had — drew no response. At stake: a defence that has not said what it defends cannot tell reform from replacement.

**Evidence:**
- engagement counts from `textstats.py`;
- N1 `hdid_refl:003` (Participant 15, `unengaged`);
- N1 `birthplace:010` (aliveness, picked up by `:011`, `:012`);
- N1 `birthplace:005` and `:007` (harmony as holding);
- cluster_014 (defend democracy).

**Note:** the Provocateur independently wrote nearly this finding twice:
- for Plato: *"each was reinforced rather than examined"*, formulation `theme_005__plato`;
- for Marley: *"one sister said plain that democracy was never in full effect for Black women in America, and the room moved on"*, `theme_005__bob_marley`.

### Illustration 2: N3 cluster_002 in theme_003 (25 extractions, 3 sessions)

**As produced:**
> **Sortition and citizens' assemblies** — Twenty-five items engage the prompt of whether to expand sortition-based democracy beyond elected representation, taking positions across the 1–5 spectrum, specifying success conditions (paideia, payment design, disenfranchised opt-in, government commitment to outcomes), probing scope and limits (…), proposing AI as deliberation aid, and asking whether sortition presupposes or builds the democratic culture it requires.

**Positioned (illustration):**
> **Sortition won the room; its hard questions came from the floor and went unanswered.** A session led by two of sortition's best-known advocates ended with nearly everyone scoring 4 or 5 out of 5. The objections came from small groups and the later reflection session, not the stage: that it may only work in mature democracies, that elected officials still choose the question, that governments can ignore the result as in Paris. The panel answered none of them. The live fault line is no longer sortition versus election, which the room settled, but whether sortition presupposes the democratic culture it is supposed to build.

**Evidence:**
- `beastopia:005` (context: *"nearly the whole room scored 4 or 5"*);
- `citizen:013`;
- `mpga:003` (the one `challenged` reflection);
- `citizen:009`;
- `citizen:014` (context: *"never directly addressed by the panelists"*);
- `mpga:023`.

### Illustration 3: N1 cluster_008 in theme_004 (8 extractions)

**As produced:**
> **Non-human standing in deliberation** — Items wrestling with whether non-human entities — rivers, forests, AI, octopus voices, AI-generated Cleopatras and Platos — can or should be granted voice in democratic deliberation, including the rights-based pushback that any commons requires curated values rather than indiscriminate inclusion.

**Positioned (illustration):**
> **The room's own vote is the finding: personhood for rivers, not for AI.** Asked in turn, the Marathon room granted legal personhood to rivers and forests easily and withheld it from AI. The only explanation offered — standing goes to what cannot claim it — came from the Assembly's own octopus voice, and nobody took it up or answered it. Nor did anyone answer the one objection to the expansion case: that a commons without curated, rights-based values collapses into people talking past each other. Half of this cluster's eight items are the Assembly speaking, or the room asking about the Assembly.

**Evidence:**
- `mthd:007`, `mthd:021` (context: *"Never resolved"*);
- `hdid_refl:017` (high energy, `unengaged`);
- `hdid_refl:023`;
- `mthd:020`, `act_one:015`, `act_one:021` (the three other Assembly-voice or Assembly-about items).

### What the three have in common

Each positioned version:
- states what the room did (settled, split, voted, moved on);
- names what nobody answered;
- says what is at stake.

**None says who is right about democracy, sortition or personhood.** That distinction is the key to handling the plurality risk in A.5.

## A.4 Why it's like this

### Neutrality was intended, explicitly and at every level (CONFIRMED)

- **Briefing, Stage 1:** *"The Researcher is unbiased — it does not know the council's composition, the audience's profile, or the closing-show matrices. It captures faithfully what the day's sessions contained."*
- **Researcher spec:** *"It is a design research instrument, not an editorial voice."* And under Scope: *"It does not formulate questions or propositions — that's the Provocateur."*
- **Provocateur spec:** *"The Provocateur is the strategic, editorial agent in the pipeline. Unlike the Researcher (content-faithful, council-unaware) … It makes choices designed to produce the strongest possible artifacts."*
- **`DATA_INVENTORY.md`** adds a second job: stages 1–2 are *"general-purpose conference data"*, *"a clean record of what was said on stage and what positions were taken"*, usable for archive and research.

So the division of labour is deliberate: the Researcher reports, the Provocateur supplies the edge.

**The operator's complaint is about the Researcher output read on its own**, as the "conference record" and in the explorer's Conference Data page. There the design gives it nothing to say.

### The specific decisions that produce the flatness

1. **Clusters are forbidden from stating findings** (CONFIRMED).
   - Spec: the cluster abstract is *"not a caption, not a summary, and not a 'declarative finding' that states the answer the cluster points to."*
   - Prompt, BAD examples: *"Declarative findings (state an answer, not the binding — this is the theme-level move, not the cluster-level move)."*
   - Changelog §G: v2.4 is *"replacing the v2.2 'declarative finding' framing."*
   - So a finding layer existed in v2.2 and was removed on purpose.
2. **The question asked is a classification question.**
   - Both grouping prompts ask *"why these belong together"*. On agreeable material the honest answer is "they agree" or "they're about the same thing", and that is what 86 abstracts say.
   - The theme prompt allows a finding in principle; its good examples include *"reveal that the administration's position fails on its own terms"*. But it frames the job as naming the binding and rewards inline cluster citations. The result is 24 of 24 routing tables.
   - PLAUSIBLE, from the method's literature, not from this repo: Kawakita's original KJ method asks each group label to state the gist of its cards as a sentence rather than name a category. The spec kept KJ's grouping and dropped its statement.
3. **Round 1 is blind to disagreement by construction** (CONFIRMED, `cluster_extractions`).
   - The clusterer sees only `{ref, extraction, context}`. Speaker, lens, `engagement`, `responds_to` and `energy` are stripped.
   - It cannot tell a contested exchange from five people agreeing. It cannot see that `mthd:007` was high energy, or that `hdid_refl:017` went unanswered. It only knows a claim was disputed if the `context` text happens to say so.
   - This was a sound fix for v2.3's session-local clustering. At Athens, clusters are session-local anyway (55 of 86), because Athens sessions were topically distinct. So the stripping cost the disagreement signal without buying cross-session clusters.
4. **Round 2 sees only Round 1's abstracts.** An inventory of inventories can only be a heading.
5. **Engagement is the only position signal, and it is thin.**
   - `challenged / reinforced / unengaged` records whether the room responded, not what was at stake.
   - On reflections it is inferred between separately recorded contributions: `birthplace:006`, `:007` and `:008` are all `responds_to: birthplace:005` and "reinforced", though each is a separate vendor recording. That the participants did not hear one another is PLAUSIBLE, not verified from the vendor format.
6. **The method was validated on an argumentative conference and deployed at a hospitable one.** This is the central causal point.
   - The same prompts (unchanged since 2026-04-16) and the same model (`claude-opus-4-7`, adaptive thinking, per `model_routing.json`) produced positioned themes on MSC material with 32% challenged items. For example: *"These clusters form a multi-sided contest over Western identity that no participant can stabilize"*; *"cluster_021's direct challenge to the EU's democratic legitimacy undermines the center's institutional ground for resistance"*.
   - At Athens (6% challenged) they produced headings.
   - **Inference, strongly supported:** the method mirrors the room. It is exactly as positioned as the room's own disagreements, and it adds nothing of its own. In a room built on intellectual hospitality (G7), a faithful mirror reproduces the hospitality: every position gets a seat, none is weighed, agreement reads as convergence. The Researcher performs the failure mode the rest of the project is designed against.
7. **The Researcher does not know the Assembly exists.**
   - Being council-unaware, it has no reason to treat *"our AI Assembly … chimed in in the voice of the octopus"* as special. `beastopia:006` fitted no cluster, so it became an isolate.
   - The Briefing's success criterion (G6) assumes the Researcher captures these references so later nights can respond. Nothing in any prompt looks for them.

## A.5 Downstream: did the flatness carry, or did later stages recover the edge?

**Both.** It depends on which part of the Provocateur reads the Researcher, and what it reads.

### Carried: Triage Part B and Selection, which read abstracts only (CONFIRMED)

**The flags don't discriminate:**
- 24 of 24 themes flagged `worth_surfacing`;
- 22 of 24 `fault_line_present`;
- 17 of 24 `audience_friction: high`.

**All 22 fault-line descriptions start "Whether …", and 21 are "A, B or C" menus that restate the theme's clusters.** For example, N1 theme_001's fault line, *"Whether AI's problem is ontological …, political …, or economic …"*, is the theme abstract's three clusters in the same order.

**So Selection's multipliers are nearly constant**, and Selection runs on voice-profile quorum alone. The spec already calls the multipliers *"symbolic in expressing editorial priority more than numerically load-bearing."*

**The cost shows in what was dropped:**
- **N1 theme_008** ("Business and leadership reframed…") held **5 of Night 1's 14 challenged extractions**, the most contested theme of the night: the survivorship-bias dispute in cluster_023, and values frame versus business case in cluster_024. It was dropped as *"below quorum"*.
- **N2 theme_006** (late life) held 3 of Night 2's 13 challenged items. Dropped.
- **N2 theme_004** (the no-clash board meeting). Dropped.

**Caveat:** quorum, not the Researcher, is the proximate cause. But flat abstracts gave triage no way to rank the material itself.

### Recovered: Formulation, which reads raw extractions (CONFIRMED)

- The formulations and context narratives state findings the Researcher's abstracts don't. A regex for explicit room-gap phrases ("moved on", "never addressed", "rather than examined", "no one asked", …) hits **23 of 128** formulation-plus-narrative texts; this is a lower bound. Examples:
  - N1 `theme_005__plato`: *"each was reinforced rather than examined"*.
  - N1 `theme_006__bob_marley`: *"When one voice mentioned that the whole thing rested on slave labour, the room moved on"*.
  - N3 `theme_003__cleopatra` narrative: *"participants surfaced the same unresolved worry … and the panel never addressed it"*.
  - N3 `theme_003__ibn_battuta` narrative: *"The room scored near-unanimous 4s and 5s. But the small-group reportbacks kept surfacing a different question underneath the enthusiasm"*.
  - N3 `theme_003__whanganui_river`: the Marathon's deliberations *"never reasoned from a river, a mountain, or a catchment as a tupuna with standing"*. This is a finding about the whole event that the Researcher, reading the same extractions, did not make.
- **The voices then develop it.** Plato's N1 Step 1 on theme_005: *"The word was passed around the table like a torch in a relay, and no one asked: torch of what?"*

### What the recovery costs

1. **The finding is re-derived per voice and never stated once.**
   - N3 theme_003 has nine context narratives, each a partial reading angled at its voice.
   - N1 theme_004: eight of nine formulations open with the same octopus reframing (`mthd:007`); only Cleopatra's does not. One finding pushed to eight voices; the rest of the cluster (the rights-based objection `hdid_refl:017`, Miller's life-conditions test) is secondary in most.
2. **It is invisible in the record.** The explorer's Conference Data page shows the Researcher layer; the findings sit inside per-voice briefings on the Assembly Output page. Someone reading "what the conference said" sees headings. This is the operator's exact experience.
3. **Findings in dropped themes are lost**, e.g. the survivorship-bias dispute.
4. **The flat abstract still reaches every voice**, as `theme_abstract_from_researcher` in `full_theme_record`.
5. **Recursion is hidden (G5).**
   - Night 1's most-used "finding of the room" was the Assembly's own live intervention, attributed to "Matthias Peschel" and fed back to eight voices as what "the room" said.
   - That may be the Assembly entering the conversation (G6), or the pipeline reading its own echo. Nothing in the data marks which, because the Researcher cannot tell.

### Verdict for the Researcher (scoped to Part A)

- The flatness is intended.
- It is mostly recovered for the voices, at Formulation.
- It is lost in three places: the record, the triage and selection of themes, and the capture of Layer-3 evidence.
- **Whether the Researcher is the bottleneck overall is Part B's synthesis.**

Side note, CONFIRMED and harmless: extractions store `lens: "open question"` with a space, while the spec, the interface contract and `provocateur_flow.py`'s `LENS_ORDER` expect `open_question`. Real briefings still sort open questions last, apparently through the unknown-key fallback. Worth a one-line spec or prompt fix, not a finding.

## A.6 What could be different

**The main risk throughout:** a Researcher that takes positions could pre-empt the voices' reading and flatten the plurality the Assembly exists for.

**The principle that manages the risk**, visible in A.3: **position the Researcher on the room, never on the question.**
- "The room settled X, left Y open, never answered Z" is a claim about the material, checkable against extraction ids.
- "X is right" is a claim about the world, and belongs to the voices.

Each option below is judged against that line.

### Option 1: extraction also records what is at stake

**What changes:** extraction schema and prompt. Three fields per extraction:
- `at_stake`: what follows if this is right;
- `contested_by`: extraction ids, or `"no one"`;
- `assumes`: the premise it doesn't argue.

**Example output**, for N1 `hdid_refl:003`:
- `at_stake`: *"if true, the day's obituary mourns a privilege; the remedy is extension, not restoration"*;
- `contested_by`: *"no one"*;
- `assumes`: *"that the 'human democracy' being mourned was the same thing for everyone."*

**Risks:**
- 529 interpretive fields a night, each a place to hallucinate.
- Speakers' positions get glossed item by item.
- The voices, who read raw extractions, would read the Researcher's gloss as part of what was said.

**Plurality:** medium risk. The glosses are local, but they sit inside the evidence the voices treat as the room.

**Verdict:** useful only for `contested_by`. That one is nearly deterministic, can be filled from `engagement` and `responds_to` in Python, and is what clustering currently can't see.

### Option 2: cluster by fault line instead of by topic

**What changes:** the Round 1 prompt and input. Round 1 would see lens, engagement and energy (speaker and session stay hidden). It would group items into disagreements with named sides, or into consensus, labelled as such.

**Example output:** *"Personhood by vote — expansion (Participant 12; Miller `mthd:001`) vs curated commons (Participant 17, unanswered); the octopus explanation offered, not taken up."*

**Risks:**
- At 6% challenged, most clusters would have one side. A fault-line method on hospitable material either **manufactures controversy** or collapses back to topics.
- Re-adding metadata re-opens the v2.3 session-local problem the minimal input fixed.
- It re-validates the whole grouping, and the MSC baseline no longer applies.

**Plurality:** medium. The Researcher picks the axis, not the winner. But choosing the axis frames every voice's reading of the theme.

**Verdict:** not as the primary change. Its one good idea, "consensus is a valid and reportable cluster state", belongs in Option 4.

### Option 3: themes stated as propositions, or as questions with named sides

**What changes:** the theme prompt. The title becomes a sentence (the KJ move). The abstract gives the claim, the strongest counter in the material, and what is untested.

**Example output:** *"Sortition won the room; its hard questions came from the floor and went unanswered"* (Illustration 2, compressed).

**Risks:**
- Round 2 still sees only cluster abstracts, which are inventories, so the propositions would be built on summaries. PLAUSIBLE that they come out generic ("tensions remain over…").
- Titles are what every downstream reader sees first. A tilted title tilts triage, the explorer and, via `full_theme_record`, the voices.

**Plurality:** medium to high. It's the highest-visibility slot.

**Verdict:** worth doing cheaply for titles only if Option 4 is declined.

### Option 4 (recommended): a separate "room reading", with the neutral layer untouched

**What changes:** a new Round 3 call after theming, plus a schema addition. `grouping.json` stays exactly as it is; the v2.4 validation and the "faithful map" contract hold.

**What Round 3 reads:** themes, cluster abstracts and **raw extractions with full metadata** (engagement, responds_to, energy, speaker, lens).

**What it writes:** `room_reading.json`.

- **Per theme**, five short statements, each with required evidence ids:
  - `settled`: what the room agreed on, including "nobody argued against X";
  - `open`: what was asked and not answered;
  - `unchallenged`: strong claims nobody contested;
  - `unsaid`: what the material assumes and nobody named (the "shared blind spot" move, relocated);
  - `at_stake`: one sentence.
- **Per night**, three to five statements about the day as a whole, plus `assembly_in_the_room`: every extraction where the Assembly or a voice is quoted, reported or answered.

**Example output:** Illustrations 1–3, in fields. For N3 theme_003:
- `settled`: *"sortition over election (near-unanimous 4–5s; `beastopia:005`, `citizen:013`)"*;
- `open`: *"what happens when governments ignore the result (`citizen:014`); who picks the question (`citizen:009`)"*;
- `unsaid`: *"no speaker reasoned from a non-human participant in the Marathon's own democracy session"*. This one the Provocateur found for Whanganui; it would now be found once, for everyone.

**Routing, in order of risk:**
1. **The record.** The explorer's Conference Data page shows the room reading beside each theme, typographically distinct, labelled "the Researcher's reading — contestable, with evidence". This answers the operator's complaint directly and serves G5.
2. **Provocateur Triage Part B.** It reads the room reading instead of, or as well as, the abstracts. Fault lines come from `open`, not from cluster lists. `unchallenged` feeds the proposition test, whose condition 3 is literally "NOT ADEQUATELY CONTESTED in the room"; today that is judged per formulation from raw extractions. Friction and fault flags gain a basis to discriminate on.
3. **Formulation**, optionally: as input the Provocateur may use or ignore.
4. **The voices: not in a first trial.** They already get the Provocateur's angled reading; adding the Researcher's would give them two framings of one room.

**Risks:**
- one more Opus call per night (small next to the Researcher's ~$15–25 per night estimate in the spec);
- a new artifact and prompt, which is additive surface under the net-complexity gate;
- the room reading can be wrong about the room. Required evidence ids make that checkable by script, since every cited id must exist and support the statement, which is the same integrity pattern as `_validate_clusters`;
- it may anchor the Provocateur's nine readings into one. Arguably that is the fix; arguably it costs variety. Measure it (below).

**Plurality:** lowest of the four. It claims only what the room did. It never reaches the voices directly, and the neutral layer stays for anyone who wants the map without the reading.

**Deterministic companion (no LLM):** a Python flag on every extraction whose text or context mentions the Assembly or a voice (the regex from `assembly_refs.py`), exempting it from isolate-dropping and listing it in the night record. This alone would have kept `beastopia:006` alive. It bends "council-unaware" only as far as knowing the Assembly exists, not who is on it.

**A free benchmark already exists:**
- The 128 Athens context narratives are the Provocateur's per-voice room readings of the same material.
- A Round-3 trial on Athens Night 1 (with a spend cap, when the operator allows API calls) can be scored against them: does one room reading cover what the nine narratives found? Compare against Illustrations 1–3, which were written from the same ids.
- Measure plurality before and after: do formulations on the same theme diverge less once triage reads a single room reading?

### Recommendation

**Option 4 plus the deterministic Assembly-reference flag.** Route it to the record and Triage Part B first, and not to the voices. Keep Option 1's `contested_by` as a Python-filled field if cheap. Decline Option 2 as the primary change.

**Roadmap fit:** this is **new**, not part of Stage 4 (voice-card prompt backport) or Stage 5 (family of forms, split-card). The nearest home is Phase 2's "stage routing as function of input shape". It is additive, so under the net-complexity gate it is design-and-shelve unless the operator decides to build (the gate amendment of 2026-09-28 lets the operator's own decision count). Part B's synthesis will say whether it should outrank other stages' changes.

---

## Checkpoint (Part A → Part B)

Part B (Transcription, Provocateur, Voice Step 1 and Step 2, Editor, published surface) and the synthesis follow **after the operator confirms or corrects the reading above.**

# Part B — every other stage

*Pending the checkpoint.*

# Synthesis and open operator decisions

*Pending Part B.*
