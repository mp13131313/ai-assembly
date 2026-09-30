# Review: each stage's Athens output against what the provotype is for

**Date:** 2026-09-28, revised 2026-09-29 · **Reviewer:** Claude Fable 5.1 (`claude-fable-5-1`), one session, read-only
**Brief:** `_workspace/planning/BRIEF_2026_09_28_stage_quality_review.md`
**Checkout:** `phase0-fixes` at `3b185f2` (detached). The two commits after the brief (`02006f5`, `3b185f2`) touch no Researcher prompt or spec.
**Status:** Part A (Researcher) is written and **revised** after an independent review (`REVIEWS_OF_FABLE_DELIVERABLES_2026_09_29/06_stage_quality_partA.md`). The changes are listed at the end of Part A. **Part B and the synthesis wait for the operator's answer at the checkpoint.**
**Commit state:** this worktree copy is uncommitted. The main session committed the first version as `0910a66`. No API calls; `athens-2026` was only read.

---

## Summary

The operator's reading holds for the grouping layer: **the Researcher's clusters and themes are inventories, not findings.** No cluster or theme says what the room settled, what nobody challenged, or what nobody said. A few theme abstracts relate clusters to one another; none reports where the room stood.

This holds on panel sessions alone. Several large panel-only themes contain zero or one challenged extraction:
- N2 theme_004, the *Clash of the Titans* board meeting: 15 extractions, 0 challenged;
- N3 theme_001: 26 extractions, 0 challenged;
- N2 theme_007 "Contesting the good life": 33 extractions, 1 challenged.

Two causes are established:
- **Neutrality is designed in.** The spec says the Researcher is "not an editorial voice". The clustering prompt bans "declarative findings". The clustering call never sees who disagreed with whom.
- **Athens argued little.** On panels, 6.6% of extractions were challenged, against 32% in the Munich Security Conference (MSC) test run.

The first version claimed "the method mirrors the room". That is now only **PLAUSIBLE**, because three confounds stand in the way:
- MSC ran on Opus 4.6, Athens (by code default) on Opus 4.7;
- the 103 reflection extractions reached the Researcher mislabelled as a panel (runtime C68 A1);
- the control is one run of three MSC panels.

The Provocateur's formulations recover the edge by reading raw extractions. But they do it per voice, never in the record the operator browsed. And no triage signal measures whether the room itself disagreed.

**Recommendation, now sequenced cheapest first:**
1. Fix C68 A1.
2. Add deterministic room statistics to the explorer.
3. Run a capped test of whether the theme prompt's existing invitation to findings works on another model.
4. Only then consider a separate evidence-linked "room reading", with a support check.

**Part B follows the checkpoint.**

---

## The goals this review judges against

The review measures against these goals, quoted from the project's own documents. Short labels are used below.

| Label | Goal | Source |
|---|---|---|
| **G1 Not a summary** | "The default behaviour of any LLM system is to summarise; this Assembly is designed to do the opposite. If the artifacts merely reorganise the day's discussions into pretty prose, the provotype has failed." | Briefing v3.1, "What it is not" |
| **G2 Tensions, not consensus** | "Not a consensus machine. The Assembly exposes tensions rather than resolving them." | Briefing, "What it is not" |
| **G3 Generative** | "could the humans in the room have arrived here without this voice? If yes, the provotype has failed." | Briefing, Design principles |
| **G4 Opinion demands response** | "An opinion demands agreement, disagreement, or reckoning with why you're dismissing it." | Briefing, Design principles |
| **G5 Construction visible** | "Every layer of translation — from human discussion to Researcher extraction, from extraction to Provocateur formulation … — is visible somewhere." | Briefing, Design principles |
| **G6 Layer 3 evidence** | "Attendees reference the Assembly's artifacts in the day's human sessions … The Researcher captures these references in Night 2 and Night 3's transcripts, which means Night 2 and Night 3 can respond to them." | Briefing, "What success looks like" |
| **G7 Against hospitality** | "their well-curated openness is itself the failure mode: they are too good at performing reception to know when they are not actually being changed." It goes flat on "Standard progressive talking points without edge". It activates on "Naming of contradictions the room holds but rarely articulates." | AUDIENCE_BRIEF |
| **G8 Specificity and disagreement** | "Caption-style labels, precise attributions, explicit disagreement markers … When in doubt, choose the forensic over the evocative." | DesignPrinciples §7 |
| **G9 Comparing** | "Two positions, pick which is closer to yours … Kills it: a neutral/both option." | Nine Modes §1 |
| **G10 The Researcher's own contract** | "The Researcher is unbiased … It captures what was discussed and flags which extractions carried high energy in the room — nothing more. It is a design research instrument, not an editorial voice." | Researcher spec, Overview |

**G10 pulls against G1, G2 and G7.** The project is designed against summary and against hospitable absorption. The Researcher is the one stage that is told to summarise faithfully and add nothing.

---

## Method and evidence base

**Read in full:**
- the Briefing, the Design Principles, the Nine Modes, the Frame Concept and the AUDIENCE_BRIEF;
- the Researcher spec and its three prompts;
- the prompt assembly in `researcher_flow.py`;
- the Provocateur spec, and `provocateur_triage_flags.md` for the fault-line definition;
- `DATA_INVENTORY.md` and `EDITORIAL_ASSESSMENT.md`;
- the explorer's renderers in `build_athens_data_graph.py`;
- runtime OPEN_ITEMS C68 A1.

**Prompts and models:**
- The Researcher prompts have not changed since the subtree add (`bd3e27d`, 2026-04-16).
- **The two runs used different models.**
  - MSC v2.4 ran on **Opus 4.6** with adaptive thinking: `dev_msc_test/_manifest.json`, *"claude-opus-4-6 with thinking.type=adaptive"*.
  - The Athens Researcher's model is **not recorded in the run data**. The code Athens ran had the default `claude-opus-4-7` with thinking on: `researcher_flow.py` at `394029f` (2026-05-08); the switch from 4.6 is `37e883b` (2026-04-17). An environment override is possible but unrecorded. The Provocateur files from the same nights record `claude-opus-4-7`.
  - `model_routing.json` postdates both runs (2026-09-28), so it documents neither.
  - Athens Researcher = Opus 4.7 is therefore **PLAUSIBLE (strongly)**, not CONFIRMED.

**Athens data read directly:**
- all 24 themes and 86 clusters, with abstracts;
- whole-session extraction sets from five session types: a two-speaker panel, audience reflections, a staged board meeting (both captures), a scored workshop, and a main-stage closing;
- every extraction in the clusters rewritten below;
- all 46 Night-1 formulations, the nine Night-3 theme_003 formulations and narratives, selected Night-2 narratives, one briefing, one Step 1 response and one Step 2 artifact;
- the Beastopia turn quoted below, from the transcript itself.

**Offline scripts** (scratchpad; they read JSON and count). The exact patterns behind every count are in Appendix A, so the counts can be reproduced.

**Session format matters.** Five of the 30 ingested sessions are **vendor reflection takeaways**, not panels:
- `birthplace`;
- `hdid_refl`;
- the N1 and N2 nightwalks;
- `mpga`.

Together they hold 103 of 529 extractions (19%). Each is a separately recorded summary by one participant, and per C68 A1 all reached the Researcher **with a blank title and format "panel"**. Engagement labels on them (`reinforced`, `responds_to`) were inferred by the Researcher across contributions that were not a conversation. **All examples in this Part are now built from panel (audio) sessions.** Reflection material is named as such where it appears.

**Session short-names used in ids.** Every id is `<night> <short-name>:NNN`.

| Short name | Full `session_id` | Kind |
|---|---|---|
| `hdid_audio` | `day_one_demos_ai_democracy_marathon_human_democracy_is_dead_1330__audio` | panel |
| `hdid_refl` | `day_one_demos_ai_democracy_marathon_human_democracy_is_dead_1330` | reflections |
| `mthd` | `day_one_mikro_pallas_ai_democracy_marathon_the_more_than_human_democracy_1445` | panel (with audience vote) |
| `birthplace` | `day_one_demos_ai_democracy_marathon_departme_birthplace_of_democracy_tour_1000` | reflections |
| `act_one` | `day_one_theatre_main_stage_act_one_the_story_of_us_2000` | main stage |
| `clash`, `clash_a2` | `day_two_theatre_main_stage_act_three_clash_of_the_titans_1045` (+ `__audio2`) | staged board meeting |
| `tunnels`, `tunnels_a2` | `day_two_mikro_pallas_agentic_agora_ai_democracy_mar_the_reality_tunnels_1400` (+ `__audio2`) | panel |
| `citizen` | `day_three_demos_ai_democracy_marathon_citizen_assembly_with_ai_1400` | scored workshop |
| `mpga` | `day_three_demos_ai_democracy_marathon_make_politics_great_again_1600` | reflections |
| `beastopia` | `day_three_theatre_main_stage_act_five_beastopia_2000` | main stage, track reportbacks |

---

# Part A — The Researcher

## A.1 See it: the data at a glance

All figures CONFIRMED (Appendix A).

| | Extractions | challenged | reinforced | unengaged | Clusters | single-session clusters | Themes | Isolates |
|---|---|---|---|---|---|---|---|---|
| Night 1 | 205 | 14 (7%) | 74 | 87 | 37 | 18 | 11 | 0 |
| Night 2 | 199 | 13 (7%) | 73 | 84 | 35 | 29 | 8 | 2 |
| Night 3 | 125 | 5 (4%) | 46 | 55 | 14 | 8 | 5 | 3 |
| **Athens** | **529** | **32 (6.0%)** | 193 | 226 | 86 | **55** | 24 | 5 |
| Athens panels only | 426 | 28 (6.6%) | 155 | 180 | | | | |
| Athens reflections only | 103 | 4 (3.9%) | 38 | 46 | | | | |
| MSC test (v2.4, **Opus 4.6**) | 106 | **34 (32%)** | 21 | 38 | 25 | 21 | 6 | 4 |

**Notes on the table:**
- Open questions carry no engagement label.
- **The extractions are good.** They are specific, attributed and carry their context. The Researcher's own synthesized open questions (`speaker: null`) often carry the sharpest observation in a session. Examples:
  - N1 `hdid_audio:011` asks whether an optimistic finding *"generalize[s] beyond a self-selected sample?"*, with context *"the room did not interrogate this."*
  - N1 `hdid_audio:010` records that two panellists' claims were *"neither … tested against the structural reality of AI market concentration."*
- **The flatness sets in at clustering.**

## A.2 Name what the operator means

"No finding in itself" and "no position" come down to five concrete things. All examples are from panels.

### 1. No verdict on the room

No cluster or theme says what the day **settled**, what it **left open**, or what went **unchallenged**. The data to say it is there, but the grouping layer doesn't use it.

- **N2 *Clash of the Titans*** (30 extractions across both captures, **0 challenged**). The session was a fictional board meeting (`clash:001`, context: *"setting up the fictional Mighty Titan board meeting"*). It was called on an interns' plan to cut 5,000 jobs (`clash:002`, context). Every board voice rejected the plan, and no extraction argues for it.
  - The Researcher's theme_004 abstract calls this *"a coherent governance argument"*. It adopts the stage's consensus as a structure instead of noticing that the clash had one side.
- **N3 theme_001 "AI reframed as a human and social question"** (26 panel extractions, **0 challenged**). Abstract: *"… converge on moving AI's hard problems off the technical layer"*.
  - Convergence is reported as a pattern, never as a question ("why did no one on stage defend the technical framing?").

### 2. Where the room did split, the abstract blurs the split

- **N3 cluster_002** (25 items from three sessions) says the items engage the prompt *"taking positions across the 1–5 spectrum"*.
- The panel extractions show a clear on-stage split about **how far**, not whether:
  - Chwalisz argued for sortition models that *"fundamentally restructure power — a near-5 endorsement"* (`citizen:003`, challenged, high energy);
  - Alexander *"Takes a softer position (~4)"*: sortition that complements elected institutions (`citizen:004`).
- The abstract loses that split.
- **Correction from the first version:** "misstates the room" overstated it. The cluster also pools 10 reflection items, e.g. `mpga:013`, which prefers subsidiarity to sortition. The claim that "nearly the whole room scored 4 or 5" is a second-hand report at Beastopia (`beastopia:005`). "Across the 1–5 spectrum" is loose, not false.

### 3. The Researcher's own noticing doesn't survive grouping

- The clustering prompt names a **"shared blind spot"** binding: items that *"all assume something without arguing it"*. **0 of 86 Athens clusters use it** (CONFIRMED; every regex hit was a content word).
- The extraction layer does notice, in its synthesized open questions: `hdid_audio:010` and `:011`, above; `clash:021`, *"the panel does not specify what would falsify that diagnosis"*; `act_one:021`, *"all presented in close succession without direct dialogue."*
- Clustering files these as one item among many. Example: N1 cluster_002 ends *"— with one item flagging selection-effect worries about the optimistic finding"*. That one item is `hdid_audio:011`.

### 4. Positions appear only where they are borrowed from one speaker

- The only cluster titles with a position in them restate a single speaker's thesis, because the cluster *is* that speaker's talk:
  - "Civilization as Goliath: collapse and inequality" (N2 cluster_028, Luke Kemp's talk);
  - "Predictions and surveillance as veiled commands" (N2 cluster_025, *"Véliz's frame"*);
  - "AI-driven layoffs as cover, not transition" (N2 cluster_019, the Clash panel's shared view).
- 55 of 86 clusters draw on a single session. On Night 2 the dominant session supplies 94% of a cluster's items on average. So a cluster is mostly one session's digest on one topic. (MSC also had 21 of 25 single-session clusters: this is how the method works, not an Athens regression.)
- **Theme level.** Reading all 24 abstracts, only about five make a claim of the Researcher's own, and every one is about **how clusters relate**:
  - N3 theme_004: clusters 012 and 013 *"are two vocabularies for the same practice"*, which settles a question the speakers left open;
  - N3 theme_002: cluster_014 *"supplies the structural answer"* to cluster_009;
  - N3 theme_003: a "progressive-depth" ordering;
  - N3 theme_005: the technology is *"more ready than the discourse admits"*;
  - N1 theme_011: *"does not directly converse with the other clusters"*.
- **None says what the room settled, avoided or left unanswered.** (Correction: the first version said "zero findings". There are a few, all of this relational kind.)
- **Contrast with MSC.** Its six theme abstracts each end on a claim about the debate:
  - *"no participant can stabilize"*;
  - *"undermines the center's institutional ground for resistance"*;
  - *"an unexamined left-right convergence on critique that neither conventional side has confronted"*, which is a blind-spot finding at theme level;
  - *"exposing a widening gap"*.
- This is the real difference between the runs: **content, not grammar.** See point 5.

### 5. The grammar is the prompt's house style, not the symptom

- The first version counted items-as-subject (86/86), em-dash lists and inline cluster ids (24/24) as evidence of flatness.
- **MSC does the same**: 25 of 25 items-as-subject, 21 of 25 with an em-dash, 6 of 6 inline ids (review, recounted).
- These counts describe the house style the prompts ask for. They explain why every abstract *reads* like a table of contents, but they do not show Athens is worse. **Withdrawn as a diagnostic.**
- What does differ is compliance. Three Athens abstracts open *"Items articulating …"* (N1 cluster_001, _025, _030). That is the clustering prompt's own BAD "topic metadata" form (*"Items arguing that powerful states aren't held accountable"*). Part of the flatness is non-compliance, not design (CONFIRMED). Whether the model change contributes is untested.

### 6. The Assembly in the room, and the Layer-3 question

- The sharpest single moment of Night 1 was the Assembly itself: the octopus voice, spoken into the room by its operator after the audience vote (`mthd:007`, reinforced, high energy): *"the audience granted personhood to rivers and nature precisely because they cannot show up to claim power, and withheld it from AI because AI threatens to actually claim a position."*
- Cluster_008 absorbs it as a topic: *"whether non-human entities — rivers, forests, AI, octopus voices … — can or should be granted voice"*.
- **Correction:** `beastopia:006` is **not attendee evidence** for G6. It is the operator (transcript: *"Unidentified Speaker 16"*, confidence low, introduced as Matthias) retelling that same Night-1 moment on Night 3. His words were *"people appreciated it for a second, it shifted the conversation a little bit"*. The extraction's context, *"visibly shifted the room"*, is the Researcher's gloss.
- It is still an isolate, so the Provocateur never passed it on. In the explorer it appears only inside its session's list: the stored isolates list is never rendered.
- **What stands for G6:** a search of every Night 2 and Night 3 transcript for references to the Assembly or its artifacts finds only this operator turn (CONFIRMED by the independent review too).
- So **no attendee referenced an Assembly artifact on stage** in the recorded sessions. That absence is itself Layer-3 data. **The Researcher cannot report it, because nothing tells it to look.**

### Operational definition

**A finding is a sentence about the day that a participant could dispute.**
- "The board meeting was called to reject a plan that nobody on stage defended" is disputable: someone could point to a defender.
- "These four clusters build a coherent governance argument" is not.

By that test, the grouping layer produced a few relational findings and **no findings about the room.** The extraction layer produced several, in its synthesized open questions.

## A.3 The contrast: what the Researcher could have said

**These are illustrations, not proposals for prompt text.** Each is written only from panel extractions, with every supporting id listed.

**Revision note:** the first version's Illustrations 1 and 2 rested on reflection material, and Illustration 3 contradicted `mthd:007`'s own label. All three are rebuilt. The error behind Illustration 3 is explained in the change list. **Each illustration is a checkable claim about the room, so each must be checked**; see the support-check requirement in A.6.

### Illustration 1: N2 theme_004 plus cluster_019 (*Clash of the Titans*, 30 panel extractions)

**As produced (theme_004):**
> **Board governance for the long term** — These four clusters build a coherent governance argument: cluster_020 establishes that boards owe duty to non-shareholder stakeholders, cluster_022 supplies the public narrative for justifying long-horizon decisions, cluster_021 names the operational practices needed under crisis pressure, and cluster_023 surfaces the unresolved dilemmas …

**Positioned (illustration):**
> **The Clash of the Titans staged a board fight with one side missing.** The session was a fictional board meeting called on an interns' plan to cut 5,000 jobs with AI. Every board voice rejected it — as short-termism, as unevidenced, as management's own failure, as cover for over-hiring, as a red herring for a product problem — and no one on stage argued for it: 30 extractions, none challenged. The case for the cuts existed only as the script the panel had been asked to reject. What the consensus left open is what would make it testable: how a board holds out when capital markets reward fast cuts, and how outsiders could tell a real productivity transition from cover.

**Evidence:**
- `clash:001` (context: fictional board meeting);
- `clash:002` (context: the interns' pitch);
- the rejections: `clash:003`, `:004`, `:005`, `clash:010`, `:011`;
- engagement recount: 0 challenged;
- `clash:020`, `clash:021` (context: *"the panel does not specify what would falsify that diagnosis"*), `clash_a2:008` (Gelles *"explicitly says he doesn't have the answer"*).

**Downstream:** theme_004 was dropped below quorum. The one Night-2 narrative that mentions the session calls it a place where *"speakers converged on a defense of human work"* (`theme_002__octopus`); none notes the missing side.

### Illustration 2: the Citizen Assembly workshop (N3 `citizen`, 15 panel extractions, 3 challenged)

**As produced (cluster_002, pooled from three sessions):**
> **Sortition and citizens' assemblies** — Twenty-five items engage the prompt of whether to expand sortition-based democracy beyond elected representation, taking positions across the 1–5 spectrum, specifying success conditions …, probing scope and limits …, proposing AI as deliberation aid, and asking whether sortition presupposes or builds the democratic culture it requires.

**Positioned (illustration):**
> **On stage, sortition's advocates split on how far, not whether; the hard questions came from the small groups.** Chwalisz argued for sortition bodies that restructure power ("a near-5"); Alexander for assemblies that complement elected institutions ("~4"). A participant's challenge — that sortition needs civic competence cultivated first — was answered with a flat rebuttal that the contrary view "is bullshit." The small groups' reportbacks raised who chooses the question, cultures of obedience, and whether the disenfranchised opt in at all; the one the record marks as never addressed by the panelists is what happens when a government ignores an assembly's work, as in Paris. Scores reported in-session: one unanimous-5 group, one that started at 3+.

**Evidence:**
- `citizen:003` (challenged, high);
- `citizen:004`;
- `citizen:006`, `:007` (both challenged, high);
- `citizen:009`, `:010`, `:015`;
- `citizen:014` (context: *"never directly addressed by the panelists"*);
- `citizen:013`.

**What it no longer claims:** that "the room settled sortition versus election". Across the day it plainly did not: `mpga:013` and `mpga:025` (reflections) record a subsidiarity-and-reform camp with *"no engagement between proponents of each path."*

### Illustration 3: N1 cluster_008, panel items only (5 of 8)

**As produced:**
> **Non-human standing in deliberation** — Items wrestling with whether non-human entities — rivers, forests, AI, octopus voices, AI-generated Cleopatras and Platos — can or should be granted voice in democratic deliberation, including the rights-based pushback that any commons requires curated values rather than indiscriminate inclusion.

**Positioned (illustration, corrected):**
> **The room's vote is the material: personhood for rivers, not for AI — and the explanation that landed came from the Assembly itself.** After the audience granted legal personhood to rivers and forests and withheld it from AI, the Assembly's octopus voice, spoken by its operator, named the asymmetry: standing is given to what cannot claim it. The room took the point up. What it left open was the principle: on what ground AI should be granted or denied standing. Of the five panel items in this cluster, three are the Assembly's own voices, spoken by its operator, and two are the Researcher's questions about them.

**Evidence:**
- `mthd:007` (context: *"Delivered after a vote …"*; reinforced, high energy);
- `mthd:021` (context: *"Never resolved"*);
- `mthd:020` (Cleopatra channelled);
- `act_one:015` (Arendt channelled);
- `act_one:021` (context: *"presented in close succession without direct dialogue"*);
- the operator's own account, which agrees: *"people appreciated it for a second"* (`beastopia` transcript, turn 56).
- The reflection items in this cluster (`hdid_refl:012`, `:017`, `:023`) are left out.

### What the three have in common

Each positioned version:
- states what the room did (rejected, split, voted, took up);
- names what nobody answered;
- says what is at stake.

None says who is right about layoffs, sortition or personhood. **Position the Researcher on the room, never on the question** (A.6).

## A.4 Why it's like this

### Neutrality was intended (CONFIRMED)

- **Briefing, Stage 1:** *"The Researcher is unbiased … It captures faithfully what the day's sessions contained."*
- **Researcher spec:** *"a design research instrument, not an editorial voice."* Under Scope: *"It does not formulate questions or propositions — that's the Provocateur."*
- **Provocateur spec:** *"the strategic, editorial agent … Unlike the Researcher (content-faithful, council-unaware)"*.
- **`DATA_INVENTORY.md`** adds a second job: stages 1–2 are *"general-purpose conference data"*.

So the division of labour is deliberate: the Researcher reports, the Provocateur supplies the edge. **The operator's complaint is about the Researcher output read on its own**, as the record, and there the design gives it nothing to say.

### The specific decisions and conditions behind the flatness

1. **Extraction is told not to record room dynamics.**
   - The extraction prompt: *"Do not extract observations about group dynamics, tone, or process as findings."* Such signals may only raise the energy flag.
   - This is the most direct prompt-level ban on what a room reading does. (Added in revision; the first version missed it.)
2. **Clusters are forbidden from stating findings.**
   - The spec: the cluster abstract is *"not a 'declarative finding'"*.
   - The prompt's BAD examples: *"Declarative findings (state an answer, not the binding — this is the theme-level move, not the cluster-level move)."*
   - Changelog §G: v2.4 replaced the earlier "declarative finding" framing. The spec calls that framing v2.2; the MSC manifest calls it v2.3.
3. **The theme prompt invites findings, and Athens mostly didn't deliver them.**
   - Its first GOOD example is a finding: *"cluster_001 and cluster_004 together reveal that the administration's position fails on its own terms"*.
   - MSC (Opus 4.6) delivered such findings in 6 of 6 themes. Athens (Opus 4.7 by default) delivered relational claims in about 5 of 24 and room claims in none (A.2.4).
   - So **"designed" is right for clusters and only partly right for themes.** At theme level it looks like non-compliance, and the model change is a candidate cause. PLAUSIBLE; untested.
4. **Round 1 is blind to disagreement.**
   - The clusterer sees only `{ref, extraction, context}` (`researcher_flow.py:383-385`). Speaker, lens, engagement, `responds_to` and energy are stripped.
   - It cannot tell a contested exchange from five people agreeing, unless `context` happens to say so.
   - This fixed v2.3's session-local clustering. At Athens clusters are session-local anyway (55 of 86), because the sessions were topically distinct.
5. **Round 2 sees only Round 1's abstracts**, so it summarises summaries.
6. **Engagement labels on reflections are not observations.**
   - Per C68 A1 the takeaways arrived labelled as a panel with a blank title. The Researcher then linked separate recordings with `responds_to` and "reinforced": `birthplace:006` and `:007` both respond to `:005` as "reinforced" (`:008` responds to it as "unengaged").
   - Any finding built on reflection engagement, including the first version's theme_005 "0 of 28", is an artifact of that format.
7. **The contestation contrast, with its confounds.**
   - On panels alone, Athens has 6.6% challenged; MSC has 32%. The gap is real in the data.
   - Whether it *causes* the flat themes is **PLAUSIBLE only**, for three reasons:
     - the model differs (4.6 vs 4.7);
     - 19% of Athens extractions are mislabelled reflections;
     - the control is a single run of three MSC panels.
   - The MSC manifest itself describes Opus 4.6 themes, compared with Sonnet's, as *"taxonomic/architectural … structuring the disagreement without taking sides"*. So even the control was not strongly positioned. It just contained more of the room's own conflict to transmit.
   - Withdrawn from the first version: "same model", and "strongly supported".
8. **The Researcher does not know the Assembly exists.** It has no reason to mark the Assembly speaking in the room (`mthd:007`, `:020`, `act_one:015`), or to note that no attendee quoted it later (G6).

## A.5 Downstream: did the flatness carry, or did later stages recover the edge?

**Both.** It depends on which part of the Provocateur reads the Researcher, and what it reads.

### Carried: Triage Part B and Selection, which read abstracts only (CONFIRMED)

- **The flags don't discriminate:** 24 of 24 themes are flagged `worth_surfacing`, 22 of 24 `fault_line_present`, and 17 of 24 `audience_friction: high`.
- **No signal measures whether the room disagreed.** This is by design, not by accident: `provocateur_triage_flags.md` defines FAULT_LINE as *"territory where the council's traditions would visibly diverge"*. Friction is about the audience.
- All 22 fault lines start "Whether …". 12 offer three or more options; 10 are binary. (Correction: the first version said 21 were "A, B or C" menus.)
- Some mirror the theme's cluster list. N1 theme_001: *"Whether AI's problem is ontological …, political …, or economic"*, the abstract's three clusters in order.
- **The cost shows in what was dropped** (proximate cause: voice quorum):
  - **N1 theme_008** held **5 of Night 1's 14 challenged extractions**, all from panels, including the survivorship-bias dispute (cluster_023). It was the night's most contested theme. Dropped.
  - **N2 theme_006** held 3 of 13. Dropped.
  - **N2 theme_004**, the one-sided Clash. Dropped. Some of its items still reached voices through N2 theme_002 (cluster_019).

### Recovered: Formulation, which reads raw extractions (CONFIRMED)

The formulations and context narratives state findings the Researcher's abstracts don't. By my regex (Appendix A), 23 of 128 formulation-plus-narrative texts name a room gap explicitly; the review's narrower regex finds 16.

**Examples grounded in panels:**
- N3 `theme_003__cleopatra` narrative: participants raised the Paris worry *"and the panel never addressed it"* (`citizen:014`).
- N2 `theme_003__octopus` narrative, on the Reality Tunnels panel: *"the architectural question, the one about access points and centres, never quite got asked"* (grounded in `tunnels` and `tunnels_a2` items).
- N3 `theme_003__whanganui_river`: the Marathon's deliberations *"never reasoned from a river, a mountain, or a catchment as a tupuna with standing."*

**Examples grounded mostly in reflections** (named as such, per the review):
- N1 `theme_005__plato`: *"each was reinforced rather than examined"*. 6 of its 7 grounding ids are reflections.
- N1 `theme_006__bob_marley`: *"the room moved on"*. 5 of 6 grounding ids are reflections.
- Plato's Step 1 *"torch of what?"* develops the first of these. The Provocateur here reads a "room" that was, in fact, separate takeaways. The C68 A1 mislabel propagates this far.

### What the recovery costs

1. **The finding is re-derived per voice and never stated once.** N1 theme_004: eight of nine formulations open with the same octopus reframing (`mthd:007`); only Cleopatra's does not.
2. **It is invisible in the record.** The explorer's Conference Data page shows only the Researcher layer. The findings sit inside per-voice briefings.
3. **Findings in dropped themes are lost**, e.g. the survivorship-bias dispute and the one-sided Clash.
4. **The flat abstract still reaches every voice**, as `theme_abstract_from_researcher` (`provocateur_flow.py:1386`).
5. **Recursion is hidden (G5).** Night 1's most-used "finding of the room" was the Assembly's own intervention, attributed to "Matthias Peschel". It was fed back to eight voices as what the room said. Nothing in the data marks it as the Assembly hearing itself.

### Verdict for the Researcher (scoped to Part A)

- Flat by design at cluster level; at theme level, apparently by non-compliance.
- Mostly recovered for the voices at Formulation.
- Lost in the record, in theme triage and selection, and in any account of the Assembly's presence in the room.
- **Whether the Researcher is the overall bottleneck is Part B's synthesis.**

Side note, CONFIRMED and harmless: Athens extractions store `lens: "open question"`; MSC and `LENS_ORDER` use `open_question`. Sorting still works through the `.get(…, 99)` fallback.

## A.6 What could be different

**Principle for every option:** position the Researcher **on the room, never on the question**. "The room settled X, left Y open, never answered Z" is a claim about the material. "X is right" belongs to the voices.

**Two risks to manage:**
- **Plurality:** a positioned Researcher could pre-empt the voices' reading.
- **Accuracy** (added in revision): the first version's own illustrations contained one wrong and two doubtful claims about the room. A room reading can be wrong, and a check that cited ids exist would not catch it.

**Preconditions for any room-level option:**
- **C68 A1 fixed**, so the session format reaches the Researcher.
- **Session-kind awareness**: reflection takeaways, a staged meeting with a scripted pitch, a scored workshop, an operator channelling the Assembly.
- **An operator decision** to lift or bypass the extraction prompt's ban on group-dynamics observations (A.4 #1).

### Option 0a (new): deterministic room statistics in the explorer, no LLM

**What changes:** only `build_athens_data_graph.py`. Per theme and per cluster, show:
- the challenged, unengaged and high-energy counts, split by panel versus reflection;
- the Researcher's own synthesized open questions (`speaker: null`), listed rather than buried;
- extraction isolates;
- items where the Assembly is channelled (context mentions "Channeling" or "AI Assembly").

**Example:** "N2 theme_004 · 15 panel extractions · 0 challenged · 4 open questions: …".

**Risks:** none to the pipeline. It shows the evidence for a finding without stating it.

**Plurality:** none.

### Option 0b (new): test whether the theme prompt's existing invitation works

**What changes:** nothing permanent. A capped API trial re-runs Researcher Rounds 1–2 on Athens Night 2 panel extractions under Opus 4.6 and under the current model. Compare how many themes state a finding of the MSC kind.
- If findings return, the fix is a model choice or a prompt nudge, with no new layer.
- If not, the room hypothesis gains weight.

**Risks:** API cost (small). It needs the operator's spend cap.

### Option 1: extraction also records what is at stake

**What changes:** extraction fields `at_stake`, `contested_by` and `assumes`.

**Risks:**
- 529 interpretive fields a night, each a place to hallucinate;
- the voices read raw extractions as the room.

**Plurality:** medium.

**Verdict:** only a `contested_by` field is worth considering. Note that `responds_to` has no polarity and links only within a session, so filling it in Python is only partial.

### Option 2: cluster by fault line instead of by topic

**What changes:** Round 1 sees lens, engagement and energy, and groups items into disagreements with named sides, or into labelled consensus.

**Risks:**
- At 6.6% challenged on panels, it would mostly produce one-sided clusters or invent controversy.
- It re-opens the v2.3 session-local problem.

**Plurality:** medium, because choosing the axis frames every voice's reading.

**Verdict:** not as the primary change. Its one good idea, "consensus is a reportable state", goes into Option 4.

### Option 3: themes as propositions, or questions with named sides

**What changes:** the theme prompt. Titles become sentences; abstracts give the claim, the strongest counter, and what is untested.

**Risks:** built on inventory abstracts, likely generic. Titles are the most visible slot.

**Plurality:** medium to high.

**Verdict:** superseded by 0b. If 0b shows the model can do theme-level findings, a prompt nudge in this direction is the cheapest fix.

### Option 4: a separate "room reading", neutral layer untouched

**What changes:** a new Round 3 call after theming. It reads themes plus raw extractions with full metadata **and session kind**, and writes `room_reading.json`:
- **per theme**: `settled`, `open`, `unchallenged`, `unsaid` and `at_stake`, each with required evidence ids;
- **per night**: three to five statements about the day, plus `assembly_in_the_room`, which lists every item where the Assembly speaks or is spoken about.

**Example:** Illustrations 1–3, in fields.

**Routing, in order of risk:**
1. **The explorer**, labelled "the Researcher's reading — contestable, with evidence".
2. **Provocateur Triage Part B**, as a **new, separate `room_contested` signal**. `fault_line_present` stays a measure of council divergence, as its prompt defines it; reusing it would silently change its meaning. (Corrected from the first version, which routed `open` into the fault lines.)
3. **Formulation**, optionally.
4. **Not to the voices** in a first trial.

**Risks:**
- Accuracy. A **support check** is needed: an LLM judge or a human pass that confirms each statement is supported by its cited ids. `_validate_clusters`-style checks only confirm the ids exist. (Corrected from the first version, which said this was checkable by script.)
- One more Opus call per night. The spec's ~$15–25 per night estimate is for six sessions; Athens nights had 8–12.
- Additive surface, under the net-complexity gate.

**Plurality:** lowest of the positioned options. It claims only what the room did, and it doesn't reach the voices directly.

**The deterministic Assembly flag, revised:** its value is marking channelled-Assembly items so the recursion is visible (G5), not catching attendee references. Its one "hit" at Athens was the operator's own retelling. A regex on voice names over-matches: Plato, Arendt and Cleopatra appear as topics.

### Recommendation (revised: sequenced cheapest first)

1. **Fix C68 A1.** It is a precondition for any room-level claim and is already filed.
2. **Option 0a**, deterministic room statistics in the explorer. No LLM. It partly answers the operator's complaint about the record.
3. **Option 0b**, a capped trial under the operator's spend cap. It separates "model drift" from "hospitable room".
4. **Option 4, only if 0a and 0b don't answer the complaint.** Build it with a support check, session-kind input and a separate `room_contested` flag, and after an operator decision on the group-dynamics ban.

**Decline Option 2** as the primary change.

**Roadmap fit:**
- 0a is small explorer work.
- 0b is a trial, like Stage 4's sentinel regens, needing a spend cap.
- Option 4 is **new** and additive. Under the net-complexity gate it is design-and-shelve unless the operator decides to build.
- Nothing here belongs to Stage 4 (voice-card backport) or Stage 5.

---

## Changes in the 2026-09-29 revision

1. **Model.** Removed "same model". MSC ran on Opus 4.6 (manifest). The Athens Researcher is not recorded; the code default was Opus 4.7 (`394029f`, `37e883b`). `model_routing.json` postdates both.
2. **C68 A1** stated in the Method section and in A.4 #6; examples rebuilt on panel sessions only.
3. **Illustration 1** replaced: theme_005 (24 of 28 items were reflections) became the *Clash of the Titans* (30 panel items, 0 challenged).
4. **Illustration 2** rebuilt on the `citizen` workshop only. The "room settled sortition vs election" claim was removed; it contradicted `mpga:025` and `mpga:013`.
5. **Illustration 3** corrected. The octopus explanation *was* taken up (`mthd:007`, reinforced); what stayed open was the principle (`mthd:021`). Reflection items were dropped.
6. **`beastopia:006`** reclassified: the operator's retelling, not attendee evidence. G6 now rests on the absence of any attendee reference.
7. **Grammar statistics** withdrawn as a diagnostic, since MSC shares the house style. The difference is now located in content (A.2.4) and compliance (A.2.5).
8. **"Zero findings"** changed to "about five relational claims, none about the room".
9. **Causal claim** ("mirrors the room") downgraded to PLAUSIBLE, with its three confounds.
10. **"Designed"** qualified: true for clusters; at theme level, non-compliance (the "Items articulating…" abstracts).
11. **Added** the extraction prompt's ban on group-dynamics observations (A.4 #1).
12. **Fault lines** corrected: 12 of 22 have three or more options. By prompt definition they measure council divergence, so no signal measures room contestedness.
13. **Recovery examples** split into panel-grounded and reflection-grounded.
14. **Option 4:** a support check is now required; a separate `room_contested` flag; session-kind input.
15. **Options 0a and 0b added**, and the recommendation re-sequenced cheapest first.
16. **Small fixes:** MSC isolates are 4; `hdid_audio:010` is quoted exactly ("neither … tested"); `birthplace:008` is `unengaged`; the regexes are published (Appendix A).

## Checkpoint (Part A → Part B)

Part B (Transcription, Provocateur, Voice Step 1 and Step 2, Editor, published surface) and the synthesis follow **after the operator confirms or corrects the reading above.**

# Part B — every other stage

*Pending the checkpoint.*

# Synthesis and open operator decisions

*Pending Part B.*

---

## Appendix A — how the counts were made (reproducible)

All counts come from reading `runs/athens_night_{1,2,3}/02_researcher/{all_extractions,grouping}.json`, `03_provocateur/{triage_flags,selection}.json`, `03_provocateur/formulations/*.json` and `01_transcription/*/session_package.json`.

| Count | Method |
|---|---|
| Panel vs reflection | Session is a reflection if its `session_package.json` has `metadata.source == "vendor"` or `metadata.audio_source == "vendor"` (5 sessions). |
| Challenged per theme | Sum of `engagement == "challenged"` over the theme's clusters' `extraction_ids`, optionally restricted to panel sessions. |
| Single-session cluster | The set of `id.split(":")[0]` over a cluster's `extraction_ids` has size 1. |
| Shared-blind-spot use | Regex `blind spot\|assum\|without arguing\|nobody\|no one\|never\|unchallenged\|uncontested\|consensus\|agree` over cluster abstracts; every hit read by hand (all were content words). |
| Theme-level claims | Read by hand, all 24 Athens and 6 MSC theme abstracts; classified as list-only, speakers' claim restated, relational claim of the Researcher's own, or claim about the room (A.2.4). No regex. |
| Room-gap formulations (23 of 128) | Regex, case-insensitive, over `formulation + " " + context_narrative`: `moved on\|never (resolved\|answered\|asked\|addressed\|met\|examined)\|unanswered\|no one (asked\|answered\|named)\|nobody\|without meeting\|passed each other\|rather than examined\|went unasked\|left (open\|unasked\|unanswered)\|did not (answer\|ask\|notice)`. |
| Fault-line options | All 22 `fault_line_description` values read by hand. 12 name three or more alternatives; 10 are binary. |
| Assembly references in N2/N3 transcripts | Regex `\b(AI ?Assembly\|AIssembly\|the assembly\|octopus\|Scheherazade\|Cleopatra\|Whanganui\|Lovelace\|Dostoevsky\|Ibn Battuta\|Marley\|dossier\|newspaper\|broadsheet)\b` over every turn. Hits were read by hand; only `beastopia` turn 56 refers to the Assembly. |
