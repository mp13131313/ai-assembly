# Review: each stage's Athens output against what the provotype is for

**Date:** 2026-09-28, revised 2026-09-29 and 2026-09-30 · **Reviewer:** Claude Fable 5.1 (`claude-fable-5-1`), one session, read-only
**Brief:** `_workspace/planning/BRIEF_2026_09_28_stage_quality_review.md`
**Checkout:** `phase0-fixes` at `3b185f2` (detached).
**Status:** complete. Part A (Researcher) is revised for the operator's checkpoint answer of 2026-09-30. Part B (every other stage) and the synthesis are new. The change log is at the end of Part A.
**Commit state:** this worktree copy is uncommitted. The main session committed the first version as `0910a66`. No API calls; `athens-2026` was only read.

---

## Summary

**The operator's complaint, settled at the checkpoint:** the Researcher's clustering is fine and stays neutral. Its **labels** are the problem. Cluster and theme titles and summaries describe the pile instead of saying what is in it: a claim with a verb and an edge becomes a noun phrase. The fix is "report, don't judge": labels that say what was said, by whom, where the cluster splits, and what stayed open. The analysis and a priced test are in `NOTE_2026_09_30_researcher_labels.md` (runtime C69). This review agrees with it and adds six points (A.6).

**Graded on one axis — does the stage keep the edge of what was said?**

| Stage | Grade | In one line |
|---|---|---|
| Transcription | adequate | The words are kept verbatim. Who said them is lost in six audio captures (26% of audio words), and the vendor reflections arrive already compressed to a third of speech and mislabelled as a panel. |
| Researcher: extraction | strong | Specific, attributed claims; 58 synthesized open questions that say what a session left open. |
| Researcher: labels | weak | Inventories. Part A. |
| Provocateur: triage and selection | weak | Flags that don't discriminate (24 of 24 worth surfacing), read off the flat labels. The most contested themes were dropped. |
| Provocateur: formulation | strong | Quotes the claims, names the split, says what went unanswered. But once per voice, and 94 of 128 use one template: "the room said X and missed Y". |
| Voice Step 1 | strong | 125 committed positions that name speakers and answer them. The pipeline's most plural layer, and unpublished. |
| Voice Step 2 | strong as writing, narrow by design | 30 artifacts, 25 of them on one of the voice's three to five themes. Speaker names mostly drop out (8 of 30). One form per voice on all three nights. |
| Editor | adequate | Reports the room well and writes real headlines. But all eight multi-voice dossiers present the voices as converging; none sets two voices against each other. |
| Published surface | weak, as far as the repo shows | No matrices, no Step 3, no side-by-side of positions. The microsite was built outside this repo and is not assessed. |

**The bottleneck is not the Researcher.** Its flat labels cost the record and the triage, and the C69 fix is cheap to test. The larger loss is between Voice Step 1 and the published surface:
- 128 voice-and-theme pairs were formulated; 29 reached a dossier.
- On Night 3 all ten voices reasoned about consent and imposed good (theme_002); none was published on it.
- On Night 1 seven voices answered the question of non-human standing, the Assembly's own included; two were published on it.
- The briefing's "mapped disagreement space" was never built.

**If one stage's design changed, it should be the Editor's:** build each dossier from every voice's Step 1 position on the theme, and lead with where the voices split. That is the same "report, don't judge" move as C69, applied to the Assembly instead of the room.

**Order:** the C69 label test first (about $3), then a two-theme test of the position map (about $1).

---

## The goals this review judges against

| Label | Goal | Source |
|---|---|---|
| **G0 The operator's axis** | Does the stage "keep the edge of what was said (the claims, the splits, what stayed open), or flatten it into topics and inventories?" | Checkpoint answer, 2026-09-30 |
| **G1 Not a summary** | "The default behaviour of any LLM system is to summarise; this Assembly is designed to do the opposite." | Briefing v3.1, "What it is not" |
| **G2 Tensions, not consensus** | "Not a consensus machine. The Assembly exposes tensions rather than resolving them. The closing show maps disagreement as a feature, not a failure." | Briefing, "What it is not" |
| **G3 Generative** | "could the humans in the room have arrived here without this voice? If yes, the provotype has failed." | Briefing, Design principles |
| **G4 Opinion demands response** | "An opinion demands agreement, disagreement, or reckoning with why you're dismissing it." | Briefing, Design principles |
| **G5 Construction visible** | "Every layer of translation — from human discussion to Researcher extraction, from extraction to Provocateur formulation … — is visible somewhere." | Briefing, Design principles |
| **G6 Layer 3 evidence** | "Attendees reference the Assembly's artifacts in the day's human sessions … The Researcher captures these references". | Briefing, "What success looks like" |
| **G7 Against hospitality** | The audience activates on "Specific named individuals taking specific named positions" and "Naming of contradictions the room holds but rarely articulates." It goes flat on "Standard progressive talking points without edge". | AUDIENCE_BRIEF |
| **G8 Specificity** | "Caption-style labels, precise attributions, explicit disagreement markers … choose the forensic over the evocative." | DesignPrinciples §7 |
| **G9 Friction first, and comparing** | "Lead every visual with a collision, not a voice." / "Two positions, pick which is closer to yours". | DesignPrinciples §3; Nine Modes §1 |
| **G10 The Researcher's contract** | "The Researcher is unbiased … a design research instrument, not an editorial voice." | Researcher spec |
| **G11 The decided invariant** | "Disagreement preserved — the headline output is selection/juxtaposition, never a synthesized consensus." And: "A collective moment — the voices meet on the same material in one visible surface." | `PRODUCT_assembly_hub.md` §11.5, decided 2026-09-28 |

---

## Method and evidence base

**Read in full:** the Briefing, Design Principles, Nine Modes, Frame Concept, AUDIENCE_BRIEF; the Researcher spec and prompts; the Provocateur spec and its formulation and triage-flags prompts; `DATA_INVENTORY.md`; `EDITORIAL_ASSESSMENT.md`; `STATE.md`; the C69 note; the independent review of the first Part A. Read in part: the Transcription, Editor and roadmap documents, runtime OPEN_ITEMS (C49, C68, B2, B5), `PRODUCT_assembly_hub.md` §11.5.

**Athens data read directly:**
- Researcher: all 24 themes and 86 clusters; whole-session extraction sets from five session types.
- Transcription: all 30 session packages profiled; two review files; one transcript passage checked against its extraction.
- Provocateur: all 46 Night-1 formulations, the nine Night-3 theme_003 formulations, selected Night-2 narratives, one triage-voice file, the triage flags and selection files of all nights.
- Voice: opening and closing of 14 Step 1 responses; three Step 2 artifacts in full; the stance and closing lines of all 30.
- Editor: the ten Night-1 and Night-2 dossiers in full; Night 3's titles, abstracts and index (its bodies were deep-read by `EDITORIAL_ASSESSMENT.md`).
- Published surface: the 30 voice pages, the 24 theme files, the dossier index, and the explorer's renderers.

**Not available to this review:**
- the microsite as the audience saw it (built outside this repo; `STATE.md` lists B2 as "External, not built");
- any reception data (click-through, reads);
- the audio.

**Models.** MSC v2.4 ran on Opus 4.6 (its manifest). The Athens Researcher's model is not recorded; the code default at the time was Opus 4.7 (`394029f`). The Athens Provocateur files record `claude-opus-4-7`.

**Session format matters.** Five of the 30 ingested sessions are vendor reflection takeaways, not panels (103 of 529 extractions). Per runtime C68 A1 they reached the Researcher with a blank title and format "panel". Reflection material is named as such wherever it appears.

**Counts** are reproducible from Appendix A. Claims are CONFIRMED unless marked PLAUSIBLE or "inference".

**Session short-names used in ids.** Every id is `<night> <short-name>:NNN`.

| Short name | Full `session_id` | Kind |
|---|---|---|
| `hdid_audio` | `day_one_demos_ai_democracy_marathon_human_democracy_is_dead_1330__audio` | panel |
| `hdid_refl` | `day_one_demos_ai_democracy_marathon_human_democracy_is_dead_1330` | reflections |
| `mthd` | `day_one_mikro_pallas_ai_democracy_marathon_the_more_than_human_democracy_1445` | panel with audience vote |
| `birthplace` | `day_one_demos_ai_democracy_marathon_departme_birthplace_of_democracy_tour_1000` | reflections |
| `act_one` | `day_one_theatre_main_stage_act_one_the_story_of_us_2000` | main stage |
| `idiot` | `day_one_museum_department_of_depth_how_to_meet_an_idiot_1530` | panel |
| `clash`, `clash_a2` | `day_two_theatre_main_stage_act_three_clash_of_the_titans_1045` (+ `__audio2`) | staged board meeting |
| `nightwalk2` | `day_two_demos_ai_democracy_marathon_dance_and_dissent_a_nightwalk_2230` | reflections |
| `citizen` | `day_three_demos_ai_democracy_marathon_citizen_assembly_with_ai_1400` | scored workshop |
| `mpga` | `day_three_demos_ai_democracy_marathon_make_politics_great_again_1600` | reflections |
| `beastopia` | `day_three_theatre_main_stage_act_five_beastopia_2000` | main stage |

---

# Part A — The Researcher

## A.0 The operator's answer (2026-09-30)

The first two versions of Part A read the complaint as "the Researcher states no finding about the room" and recommended a separate "room reading". The operator's answer corrects that reading:

1. **Not a room reading, and not the Researcher taking sides.** The KJ affinity clustering stays neutral and stays as it is.
2. **The labels are what's off.** Titles and summaries are inventories, not headlines. The mechanism is nominalization.
3. **The direction is "report, don't judge".** Labels say what was said, attributed to speakers, with the split inside the cluster and what stayed open. Titles become sentences. Each cluster gets one or two key statements. The "why grouped" sentence moves to an audit field. The theme round sees the key statements. Optionally, a relations step gives the map.
4. **The target is mainly the record:** a map to read on its own in the explorer.

The full analysis is `NOTE_2026_09_30_researcher_labels.md` (runtime C69). Part A now cites it and adds to it.

**What this changes in Part A:**
- The diagnosis of the grouping layer stands, and the grammar evidence returns as the *mechanism* (A.2).
- The three illustrations are rewritten as labels (A.3).
- The "room reading" (Option 4) is withdrawn as a recommendation (A.6).

## A.1 The data at a glance

| | Extractions | challenged | reinforced | unengaged | Clusters | single-session clusters | Themes | Isolates |
|---|---|---|---|---|---|---|---|---|
| Night 1 | 205 | 14 (7%) | 74 | 87 | 37 | 18 | 11 | 0 |
| Night 2 | 199 | 13 (7%) | 73 | 84 | 35 | 29 | 8 | 2 |
| Night 3 | 125 | 5 (4%) | 46 | 55 | 14 | 8 | 5 | 3 |
| **Athens** | **529** | **32 (6.0%)** | 193 | 226 | 86 | **55** | 24 | 5 |
| Athens panels only | 426 | 28 (6.6%) | 155 | 180 | | | | |
| Athens reflections only | 103 | 4 (3.9%) | 38 | 46 | | | | |
| MSC test (v2.4, Opus 4.6) | 106 | 34 (32%) | 21 | 38 | 25 | 21 | 6 | 4 |

- Open questions carry no engagement label.
- **The extractions are good:** specific, attributed, with context.
- **58 of the 78 open questions are synthesized by the Researcher** (`speaker: null`). They state what a session left open, with the sides named. Example, `beastopia:026`: *"Does protopia arrive through patient civic memory-work … (Petros), through the catalysing force of converging crises (Indy), or through interior collective healing of trauma (Amy) — and are these alternatives, sequence, or different vocabularies for the same thing?"* Context: *"the panel did not adjudicate among them."*
- **The flatness sets in at the labels.**

## A.2 What the operator means: the labels nominalize

### The mechanism, in the data

A claim with a verb and an owner goes in; a noun phrase comes out. Three panel examples, beside the note's own table:

| Statement in the cluster | What the label made of it |
|---|---|
| Johar: *"Progressives undermine themselves by always asking 'who's not in the room?'"* (`beastopia:014`) | "the willingness to take rather than dissolve power" (N3 cluster_013) |
| White: layoffs framed as AI-driven are *"an excuse for companies that previously over-hired"* (`clash:010`) | "prior over-hiring as the actual cause (152)" (N2 cluster_019) |
| The Assembly's octopus voice: personhood goes to entities that *"cannot show up to claim power"* (`mthd:007`) | "whether non-human entities … can or should be granted voice" (N1 cluster_008) |

### The grammar that carries it

- **Cluster summaries:** 86 of 86 take "the items" as their subject ("Items …", "All …", "Eight items …", "Arc …"). 74 of 86 contain an em-dash, most of them lists.
- **Theme summaries:** 24 of 24 route between cluster ids. Typical, N1 theme_001: *"cluster_001, cluster_005, and cluster_006 together challenge the prevailing framings of AI from three different angles — … (cluster_001), … (cluster_005), … (cluster_006)."*
- **Titles** name an area: "Myth as analytical lens", "Late-life flourishing reframed", "Inhabiting the future". None could be disagreed with.
- **MSC labels share this grammar** (25 of 25 items-as-subject, by the independent review's recount). So it is the prompt's house style, not an Athens regression. The second version of this Part withdrew these counts as evidence that Athens is *worse* than MSC, and that stands. But the operator's complaint does not need Athens to be worse: the house style is the thing complained about. The April validation measured structure only, never how the labels read (C69 note §1).

### What is lost, by the operator's three measures

**The claims.** See the table above.

**The splits.**
- N3 cluster_002 says its 25 items take *"positions across the 1–5 spectrum"*. The on-stage split was specific: Chwalisz for sortition that *"fundamentally restructure[s] power — a near-5"* (`citizen:003`); Alexander *"(~4)"* for assemblies that complement elections (`citizen:004`).
- N3 cluster_013 lists nine mechanisms for a better future. The Researcher's own `beastopia:026` had already stated the three-way split with names.

**What stayed open.**
- The synthesized open questions are filed as one item among many. N1 cluster_002 ends *"— with one item flagging selection-effect worries about the optimistic finding"*. That item is `hdid_audio:011`, the sharpest observation in its session.
- `beastopia:027` records that Goslins's call to imagine what could go right and Akomolafe's refusal of any call to action were both applauded, *"without resolving the tension"*. Its two halves sit in different themes (theme_004 and theme_002), and no label connects them.

### Where labels do carry an edge

Only where a cluster is one speaker's talk: "Civilization as Goliath" (N2 cluster_028, Kemp), "Predictions and surveillance as veiled commands" (N2 cluster_025, Véliz), "AI-driven layoffs as cover, not transition" (N2 cluster_019). 55 of 86 clusters draw on a single session.

### What is not the complaint

The first versions also argued that the Researcher never says what the room settled or what nobody challenged. That is true of the data, but the operator does not want the Researcher to say it. Two facts from that work still matter downstream:
- no triage signal measures whether the room disagreed (A.5);
- no attendee referenced an Assembly artifact on stage in the recorded sessions (A.5).

## A.3 The contrast: three labels rewritten

**These are illustrations, not prompt text.** They follow the C69 form: a sentence title, an attributed summary, key extractions, and the old "why grouped" sentence kept as an audit field. Cluster memberships are unchanged. Quoted words are the extraction's wording, which is the Researcher's paraphrase of the speaker, not a transcript quote.

### Illustration 1: N2 cluster_019 (8 items, one staged panel)

**As produced**
> **AI-driven layoffs as cover, not transition** — Eight items diagnose the proposed AI-driven layoffs as a symptom of broken incentives or prior management failure rather than a real productivity transition — naming short-term reactivity (145), deterministic logic (146), HR neglect (147), customer-intimacy failure (153), prior over-hiring as the actual cause (152), external shocks weaponized as cover (158), and the broken incentive system itself (143) — with the constructive counter that investment in critical-thinking employees is the right response (144).

**Rewritten as a label (illustration)**
> **Title:** The Clash board: layoffs blamed on AI are cover for over-hiring and management's own failures.
> **Summary:** In a staged board meeting on an interns' plan to cut 5,000 jobs, every board voice rejected the plan. Sean White: most layoffs framed as AI-driven are "an excuse for companies that previously over-hired." Jessica Orkin: boards use external shocks "as cover to do things they had wanted to do anyway"; invest in people who can think instead. Grant Toups: the headcount debate is "a red herring" for products that aren't selling. Pinar Akiskalioglu: leadership ignored HR's warnings for years. No board member argued for the cuts.
> **Key extractions:** `clash:010`, `clash:011`.
> **Why grouped (audit):** eight items that diagnose the proposed layoffs as a symptom of prior failure rather than a productivity transition.

Evidence: `clash:001`, `:002` (contexts: fictional board, interns' pitch); `:003`, `:004`, `:005`, `:010`, `:011`, `:016`.

**The borderline to decide:** "No board member argued for the cuts" reports an absence. It is a fact about what was said, not a judgement of it. The operator should say whether absence counts as "report".

### Illustration 2: N3 cluster_002 (25 items: a workshop, a reportback, and separate reflections)

**As produced**
> **Sortition and citizens' assemblies** — Twenty-five items engage the prompt of whether to expand sortition-based democracy beyond elected representation, taking positions across the 1–5 spectrum, specifying success conditions …, probing scope and limits …, proposing AI as deliberation aid, and asking whether sortition presupposes or builds the democratic culture it requires.

**Rewritten as a label (illustration)**
> **Title:** Sortition: restructure power, or complement elections — and does it need a democratic culture first?
> **Summary:** In the Citizen Assembly workshop, Claudia Chwalisz argued for sortition bodies that "fundamentally restructure power" ("a near-5"); Jon Alexander for assemblies that complement elected institutions ("~4"). A participant said sortition needs civic competence cultivated first; Alexander answered that the claim citizens can't deliberate "is bullshit." Small groups asked who chooses the question, whether the disenfranchised will opt in, and what happens when a government ignores the result, as in Paris — that last one the panel did not address. In separate reflections recorded after a later session, participants added payment by income, subsidiarity in place of sortition, and the worry that it only works in mature democracies.
> **Left open:** whether sortition presupposes a democratic culture or builds one.
> **Key extractions:** `citizen:003`, `citizen:014`.
> **Why grouped (audit):** 25 items that engage whether to expand sortition beyond elected representation.

Evidence: `citizen:003`, `:004`, `:006`, `:007`, `:009`, `:014`, `:015`; `mpga:003`, `:012`, `:013`, `:023`.

**What this one shows:** the summary has to change its verbs when the source changes kind. "Answered" is true of the workshop. For the reflections only "added" is true: they were recorded separately.

### Illustration 3: N1 cluster_008 (8 items: a panel with a vote, the main stage, and reflections)

**As produced**
> **Non-human standing in deliberation** — Items wrestling with whether non-human entities — rivers, forests, AI, octopus voices, AI-generated Cleopatras and Platos — can or should be granted voice in democratic deliberation, including the rights-based pushback that any commons requires curated values rather than indiscriminate inclusion.

**Rewritten as a label (illustration)**
> **Title:** Personhood for rivers but not for AI: the room voted, and the Assembly's octopus voice said why.
> **Summary:** After the audience granted legal personhood to rivers and forests and withheld it from AI, the Assembly's octopus voice, spoken in the room, said personhood goes to entities that "cannot show up to claim power"; the room took the point up. The Assembly's Cleopatra voice added that keeping democracy's visible forms while hidden hands close the decisions is "monarchy made deniable." In separate reflections, one participant wanted AI included as "a new family member"; another said democracy is "a rights-based, value-curated commons."
> **Left open:** on what principle AI is granted or denied standing.
> **Key extractions:** `mthd:007`, `hdid_refl:017`.
> **Why grouped (audit):** eight items on whether non-human entities can be given a voice in democratic deliberation.

Evidence: `mthd:007` (reinforced, high energy), `mthd:020`, `mthd:021` (context: *"Never resolved"*), `hdid_refl:012`, `:017`.

**What this one shows:** three of the eight items are the Assembly's own voices, spoken by its operator. A label "attributed to speakers" needs a rule for them. The Night-1 deployment rule already has one: attribute to "the Voice of X, channelled into the room", never to the operator by name.

## A.4 Why the labels come out this way

The C69 note §3 gives five prompt-level causes, with line references: titles told to be topical; a summary written for an auditor; one sentence per cluster; a ban on "declarative findings" that is too broad; themes built from the inventories. This review confirms all five. It adds:

1. **The blind input and the ban are one decision.** Round 1 sees only `{ref, extraction, context}`: no speaker, no session (`researcher_flow.py:383-385`). A clusterer that cannot say *who* can only state a claim in its own voice, and that is what the ban forbids. With attribution impossible, "Items argue that …" is the only neutral sentence left. So nominalization is forced by the input, not only invited by the prompt.
2. **The extraction prompt bans the raw material for "what stayed open" from being first-class.** *"Do not extract observations about group dynamics, tone, or process as findings."* The Researcher gets round this with synthesized open questions, which is why they are the best material for labels.
3. **Cluster size.** Athens clusters average 5.5, 5.6 and 8.7 items across the three nights, against 4.1 at MSC (note §3). On Night 3, three clusters hold 57 of 125 extractions. One sentence cannot state one claim for 25 items.
4. **Theme level was invited to do better and mostly didn't.** The theme prompt's first good example is a finding (*"together reveal that the administration's position fails on its own terms"*). MSC themes on Opus 4.6 ended on claims about the debate; Athens themes on (probably) Opus 4.7 routed between ids. Whether the model, the larger clusters or the material explains the difference is untested. It matters less now that the labels are being changed anyway.
5. **Reflections were labelled as a conversation.** Per C68 A1 the takeaways arrived as a "panel". The Researcher linked separate recordings with `responds_to` and "reinforced". Any label that says "speakers agreed" or "one countered" about that material reports an exchange that did not happen in the record.

**Neutrality was intended** (Briefing Stage 1; Researcher spec; Provocateur spec: *"Unlike the Researcher (content-faithful, council-unaware)"*). "Report, don't judge" keeps that intention. It changes what "faithful" means: faithful to what was *said*, not only to what it was *about*.

## A.5 Downstream: did the flatness carry, or was the edge recovered?

**Both.**

### Carried: triage and selection, which read only the labels

- The flags don't discriminate: 24 of 24 themes `worth_surfacing`, 22 of 24 `fault_line_present`, 17 of 24 `audience_friction: high`.
- By prompt definition a fault line is *"where the council's traditions would visibly diverge"*. So nothing measures whether the room itself disagreed.
- All 22 fault lines start "Whether …". Several restate the theme's cluster list (N1 theme_001: *"Whether AI's problem is ontological …, political …, or economic"*).
- Dropped below voice quorum: N1 theme_008 (5 of Night 1's 14 challenged extractions, all from panels), N2 theme_006 (3 of 13), N2 theme_004 (the Clash).

### Recovered: formulation, which reads the extractions

- The Provocateur's context narratives do what C69 asks of a label. N3 `theme_003__cleopatra`: *"participants surfaced the same unresolved worry — that in Paris, an assembly had done substantial work and the government had simply chosen not to adopt the recommendations — and the panel never addressed it."*
- N2 `theme_003__octopus`: *"the architectural question, the one about access points and centres, never quite got asked."*
- Its theme display titles are already headlines, though angled at one voice: "The Funeral for Something the Sufferah Never Had".

### What the recovery costs

1. It is done per voice, up to ten times per theme, and never stated once.
2. It is invisible on the explorer's Conference Data page, which is what the operator read.
3. It is lost for dropped themes.
4. The inventory label still reaches every voice, as `theme_abstract_from_researcher`.
5. Where the source was reflections, the recovery invents a room (Part B.5 has a published case).

### The Layer-3 fact

A search of every Night 2 and Night 3 transcript for references to the Assembly finds one turn: the operator himself retelling the Night-1 octopus moment (`beastopia`, turn 56; extracted as `beastopia:006`, an isolate). **No attendee referenced an Assembly artifact on stage in the recorded sessions.** That is G6 data, and no stage reports it.

## A.6 What could be different

### Lead option: the C69 label test

**What it is** (note §5): keep the Athens cluster and theme memberships exactly; regenerate only the labels; write to a sandbox; compare old and new in the explorer. This review recommends running it.

**Six additions and disagreements.**

1. **The label call must see what the clustering call must not.** Attribution needs speaker and session, and "the split" needs `engagement` and `responds_to`. So in production Round 1 becomes two calls: group (blind, as now) and label (sighted). The test already has this shape; the note should say so.
2. **Session kind has to be an input.** The note's second illustration (N1 cluster_013) says *"Speakers agreed … they split on the cure"*. Nine of that cluster's ten items are reflection takeaways (seven `birthplace`, two from the Night-1 nightwalk). They were recorded separately; nobody agreed or split with anyone. The relabel script can read the kind from the session package (`source == "vendor"`) without waiting for the C68 A1 fix.
3. **Build the split from the Researcher's own open questions.** The note's first illustration (N3 cluster_013) says the Beastopia panel *"split three ways"*: crises, healing, and progressives dissolving power. Two of those three are the same speaker (Johar: `beastopia:013` and `:014`), and Apostolakis's position is missing. `beastopia:026`, inside the same cluster, states the split correctly. The 58 synthesized open questions should be the label step's first source for "the split" and "what stayed open".
4. **Add the support check to the cheap package.** Three hand-written drafts have now carried attribution errors: two in this review's earlier versions and one in the note. That is the expected error rate of this kind of sentence. The support check costs about $1 (note's estimate) and belongs in every package.
5. **"Verbatim" is not available.** The key statements are extraction text, which is the Researcher's paraphrase. "Idiocy has no witnesses, only accomplices" sits inside a paraphrase of Maxime Rovere (`idiot:002`). Extractions carry no turn index, so the explorer cannot link to the transcript. Either call them "key extractions", or add a turn reference to the extraction schema.
6. **Attribution is only as good as the transcript.** In six audio captures the transcription stage named nobody, and the names in the extractions are the Researcher's own inference (Part B.1). Labels that name speakers inherit that.

**Agreed without change:** the diagnosis; the five causes; the neutral line; the audit field; feeding key statements to the theme round.

**Not checked by either session:** the claims about Kawakita's original KJ method (sentence labels; the relations chart and narrative). They match this reviewer's recollection, but no source was consulted. PLAUSIBLE.

**If the labels go to production, three consumers need a look:**
- Triage reads theme and cluster titles and summaries.
- Every voice receives the theme summary.
- The cross-night exclusion (C9) matches themes by normalized title. It matched nothing at Athens (`prior_exclusions_applied: []` on both nights); sentence titles will match even less.

### The relations step (the map)

The note lists it as optional. This review recommends including it in the test: it is what the operator called the map, and the note prices it at about $0.6.

Two real relations that no current label shows:
- **Within Night 3:** Goslins's call to imagine what could go right (cluster_013, theme_004) against Akomolafe's refusal of the call to action (cluster_014, theme_002). `beastopia:027` records that the room applauded both.
- **Across nights:** Larry Irving on Night 2, *"ask who isn't at the table"* (`clash:018`), against Indy Johar on Night 3, asking who's not in the room *"dissolves the power that is in the room"* (`beastopia:014`). Both were on the main stage. A per-night run cannot see this; it needs one pass across all three nights.

A relation between two clusters is a claim nobody in the room made, so it needs the same support check and the same attribution.

### The earlier options, restated relative to C69

| Option | Status | What stands, what changes |
|---|---|---|
| **0a** Deterministic statistics in the explorer | **Stands, as the display half of C69.** | Show under each label: the key extractions, the synthesized open questions, the session kind, the challenged count, and the isolates (today stored and never drawn). No model call. |
| **0b** Test the theme prompt on another model | **Folds into C69's control arm.** | The note's best-quality package already re-runs the current label prompt on fixed memberships. Whether Opus 4.6 would have written better theme labels is now of historical interest only. If Opus 4.6 is still served, one extra arm costs about one draw (≈ $2, assuming it is priced like Opus 4.7; not verified). |
| **4** A separate "room reading" | **Withdrawn as a recommendation.** | The operator does not want it. Two of its five fields move into the label summary: the split, and what stayed open. "Unchallenged" and "unsaid" are dropped; the challenged count in 0a shows the first without a sentence. The support check and the session-kind input carry over to C69. |
| **1** Extraction records what is at stake | Not needed. | The edge is already in the extractions. |
| **2** Cluster by fault line | Declined. | The operator keeps the clustering. |
| **3** Themes as propositions | **Absorbed into C69.** | "Titles become sentences" is this option, with attribution added. |

### Paid test: packages and cost

Prices and token sizes are the C69 note's; this review has not verified them.

- **Best value, about $3:** the note's $2 package (new label prompt, Opus 4.7, one draw, three nights) plus the support check (≈ $1). Inputs extended with speaker, session kind and the synthesized open questions.
- **Best quality, about $12–16:** the note's $11 package (control; two draws on Opus 4.7; one on Opus 5.5; support check on all three; relations map), plus a cross-night relations pass (≈ $0.6), plus the optional Fable arm (≈ $3.9).

### Recommendation

1. **Run the C69 test** with additions 1–5 above.
2. **Build 0a alongside it**, since the explorer has to show both label sets anyway.
3. **Decide the absence question** (Illustration 1) before the prompt is written.
4. **Fix C68 A1** forward; the test itself does not need to wait for it.

**Roadmap fit:** C69 is a new runtime item, outside Stages 4–6. It changes a prompt and adds a call and two fields; under the net-complexity gate the operator's decision to build counts.

---

## Change log

### 2026-09-30 (checkpoint answer; Part B added)

1. **A.0 added:** the operator's answer. The reading "no finding about the room" is replaced by "the labels nominalize".
2. **A.2 rewritten** around the mechanism. The grammar counts return as the mechanism, not as an Athens-versus-MSC comparison.
3. **A.3:** the three illustrations rewritten as C69-form labels (sentence title, attributed summary, key extractions, audit field).
4. **A.4:** aligned with the note's five causes; added the point that blind input forces nominalization.
5. **A.6:** C69 is the lead option, with six additions and disagreements; Options 0a, 0b and 4 restated; Option 4 withdrawn; costs given as best-value and best-quality packages.
6. **Part B and the synthesis written.**
7. **Summary and goals table** rewritten for the whole review (G0 and G11 added).

### 2026-09-29 (after the independent review)

1. **Model:** "same model" removed. MSC ran on Opus 4.6; the Athens Researcher's model is unrecorded (code default Opus 4.7).
2. **C68 A1** stated; examples rebuilt on panel sessions.
3. **Illustrations 1–3** replaced or corrected (theme_005 was 24 of 28 reflections; "the room settled sortition" contradicted `mpga:025`; the octopus explanation *was* taken up).
4. **`beastopia:006`** reclassified as the operator's own retelling.
5. **Grammar statistics** withdrawn as evidence that Athens is worse than MSC.
6. **"Zero findings"** changed to "a few relational claims, none about the room".
7. **Causal claim** ("mirrors the room") downgraded to PLAUSIBLE.
8. **Fault lines:** 12 of 22 offer three or more options; they measure council divergence by definition.
9. **Option 4** given a support check; Options 0a and 0b added.
10. **Small fixes:** MSC isolates are 4; `hdid_audio:010` quoted exactly; `birthplace:008` is `unengaged`; counting methods published.

---

# Part B — every other stage

## B.0 The funnel

All counts CONFIRMED (Appendix A).

| Step | What exists | What goes on |
|---|---|---|
| Recorded | 30 session captures, 208,372 words | |
| Extracted | 529 extractions | |
| Themed | 24 themes | 18 kept by selection; 6 dropped |
| Formulated | 128 voice-and-theme pairs | 253 distinct extractions quoted (48%) |
| Reasoned (Step 1) | 125 responses, about 144,000 words | 307 distinct extractions engaged (58%) |
| Written (Step 2) | 30 artifacts, about 18,500 words | 25 focus on one response; 5 synthesise |
| Edited | 13 dossiers on 13 themes | 29 voice-and-theme pairs (23% of 128) |

Two readings of this table run through Part B:
- **The room's edge survives.** Each stage after the Researcher's labels goes back to the extractions and names what was claimed.
- **The Assembly's own edge does not.** Step 1 holds four times as many positions as are published, and the published ones are framed as agreeing.

## B.1 Transcription

**What the provotype needs.**
- *"Speaker identification runs through multi-pass LLM attribution against pre-loaded rosters and session metadata."* (Briefing, Stage 0)
- The audience activates on *"Specific named individuals taking specific named positions."* (AUDIENCE_BRIEF) That needs the names.
- G6 needs attendee references to the Assembly to be capturable.

**What it produced.**
- **The words are kept.** A spot check: Indy Johar's Beastopia turn reads *"the number one conversation is, who's not in the room? … what you've also done is dissolve the power in the room"*. `beastopia:014` paraphrases it faithfully.
- **The names are not, in six captures.** In both Act One captures, the first Reality Tunnels capture, Building Belonging, The Long Game and Beastopia, every turn is labelled "Unidentified Speaker N" at low confidence. That is 51,670 of about 199,600 audio words (26%).
  - Five of the six are the C49 failure: the speaker-ID call returned broken JSON on many-speaker sessions, and the operator passed the labels through by hand (`review.md`: *"Manual passthrough — speaker_id failed on JSON decode"*).
  - In Building Belonging the diarizer produced three labels for a session with at least ten distinct speakers (`review.md`: *"a composite label that appears to cover multiple speakers"*).
- **The Researcher then named the speakers itself.** Beastopia's extractions carry "Indy Johar", "Rachel Goslins", "Amy Elizabeth Fox". The extraction prompt says to *"pass through the named speaker label from the transcript exactly."* So the names are the Researcher's inference from what was said on stage. It carries no confidence flag and no audit trail. The inference is often good: it separated ten speakers in Building Belonging. But nothing checks it. In the Beastopia transcript even the operator is "Unidentified Speaker 16"; the extraction names him.
- **The reflections arrive already flattened.** The five vendor sessions hold 8,811 words from 176 recorded minutes: about 50 words a minute, a third of the rate of speech. `metadata._reflection_source` is `takeaway_export`. A 130-second recording reaches the pipeline as four bullet points (`nightwalk2`, Participant 12). The edge was reduced before the pipeline saw it, and then the result was labelled a panel (C68 A1).

**Grade: adequate.**
- *Value created:* a verbatim, readable record of 25 audio captures.
- *Value lost:* attribution in a quarter of the audio, and the speech behind the reflections.
- *Roadmap:* C49 is fixed as a graceful fallback, which still yields unnamed speakers. C68 A1 is open. An audit of the Researcher's inferred names is **new** and small.

## B.2 Provocateur

**What the provotype needs.**
- *"The Provocateur is strategic and editorial … It decides what gets asked, how, and who answers."* (Briefing, Stage 1b)
- A question should send a voice *"somewhere the day's conversations couldn't"*; a proposition needs *"a sharp, debatable CLAIM … NOT ADEQUATELY CONTESTED in the room"*. (Provocateur spec)
- *"Two different members on the same theme should receive genuinely different formulations."* (Provocateur spec)

**What it produced.**

*Triage flags and selection: weak.*
- The flags are the same for nearly every theme (A.5), so selection ran on voice quorum alone.
- The dropped themes include Night 1's most contested one (theme_008, the survivorship-bias dispute about "beautiful business") and the Clash.
- The triage reads only the Researcher's labels. Better labels (C69) are the cheapest way to give it something to rank.
- The fault-line sentence is the one place a theme's split is named. It does not travel: all 18 published theme files that flag a fault line carry `fault_line_description: null`. PLAUSIBLE cause: the briefing's `theme_flags` block holds only the friction level, the boolean and the quality score.

*Formulation: strong on the axis.*
- It quotes claims with owners: *"One voice in the room said AI pessimism is a privilege of the free world … Another voice in the same room called using these tools a Faustian pact"* (N1 `theme_001__bob_marley`).
- It names what went unanswered (A.5).
- It turns the Assembly on itself. On Night 1 theme_004 it asked Dostoevsky: *"you have been given standing as a voice precisely because, like the river, you cannot rise from the page to refuse the use being made of you."* And Ibn Battuta: *"a voice produced without chain is not testimony but fabrication dressed in the robe of testimony."*
- The proposition test held: 21 propositions in 128.

*Two limits.*
- **One template.** 94 of 128 formulations make the room or the panel their subject; 43 open with the words "The room". The shape is: the room said X and did not examine Y; what does your tradition say about Y? The ten voices are aimed at ten different Ys, but at one move. That move comes back in Step 2 and in the dossiers (B.4, B.5). Inference: the convergence the Editor reports is seeded here.
- **It inherits the reflection mislabel.** N1 `theme_005__plato` says four meanings of democracy were *"each … reinforced rather than examined"*. Six of its seven grounding items are separately recorded takeaways.

**Grade: formulation strong; triage and selection weak.**
- *Value created:* the room's claims and gaps, put as questions a voice can answer. This is where the edge lost in the labels comes back.
- *Value lost:* it comes back once per voice and stays in the briefings; contested themes are dropped.
- *Roadmap:* no item covers triage discrimination. It would ride with C69 if the new labels go to production.

## B.3 Voice Step 1 (private reasoning)

**What the provotype needs.**
- The voice *"produces a detailed response — reasoning through the question, landing on a committed position"*. (Briefing, Stage 2)
- G3 and G4: generative, and an opinion that demands a response.

**What it produced.** 125 responses, averaging about 1,150 words. Each engages six to seven extractions.

- **They name speakers and answer them.** 78 of 125 name a panel speaker.
  - Arendt: *"Roger Berkowitz is right that politics is, among other things, a matter of friendship — though I would say plurality, which is cooler and more exact."* (N1 theme_004)
  - Cleopatra, on Véliz: *"The philosopher's frame, then, kept by all means; her tools, where they cut."* (N2 theme_008)
  - Lovelace: *"I refute the proposition's framing and defend Ms Posner's experience, which are not the same operation."* (N3 theme_001)
- **They land.** Cleopatra: *"What this conference owes itself, before philosophy and before stories, is the harder labor of building the chancery that makes the prophet sign his name."*
- **They split from one another.** On Night 1 theme_004, the Assembly's own legitimacy:
  - Arendt: *"Rivers cannot promise. Synthesized voices cannot be held to account. The dead cannot consent to the use of their names … If you would seat anyone new at the table, seat the children."*
  - Dostoevsky: *"a kindly inclusion that costs nothing is bezobrazie wearing a kind face … The river cannot [refuse]. I cannot."*
  - The Whanganui River, against the Octopus's framing: *"rivers safe because non-threatening, AI unsafe because threatening — flattens both poles. The river is not safe; the iwi were not non-threatening."*
  - Plato: the river's silence is *"not … at all the same kind of silence as the silence of one whose fluent speech does not move him."*
  - The Octopus: opening the room *"would require not adding more chairs but changing what a chair is for."*

  Five positions, on the question the provotype exists to ask, that do not agree.

**Grade: strong.**
- *Value created:* this is the layer where the Assembly has opinions about named people's claims and disagrees with itself. It is the raw material of the briefing's *"mapped disagreement space"*.
- *Value lost:* all of it that Step 2 does not pick up. Step 1 is described as *"scratchwork: internal, not published"* (`DATA_INVENTORY.md`) and is visible only in the explorer.

## B.4 Voice Step 2 (the artifact)

**What the provotype needs.**
- *"one artifact compressing across them — the voice's public expression"*; *"the voice decides what matters most to express publicly."* (Briefing, Stage 2)
- Layer 2: *"something where the attribution to a non-human voice matters … If the content could have come from a well-read human essayist, the provotype has reduced to an art project"*.
- *"The medium of each voice matters … Form is already content."*
- The audience returns to artifacts *"not because they were beautiful but because they were unresolved."*

**What it produced.** 30 artifacts, averaging about 615 words.

- **They keep the claim they answer, without the name.** Plato: *"One of their makers said the centralized kind is a tyrant's instrument, and the cure is that each citizen should have his own."* That is Sean White, unnamed. 8 of 30 artifacts name a panel speaker, against 78 of 125 Step 1 responses. The voice's fiction explains it, and the dossier restores the names. A reader of the artifact alone does not learn whose claim is being refused.
- **They take a position on the room.**
  - Marley: *"the moment the rester make the sufferah the reason for the rest, the sufferah become the alibi."* (N3)
  - Cleopatra: *"The loss is not friendship. The loss is the column."* (N1)
  - Ibn Battuta: the room *"that received the testimony and did not classify it has become a chamber adjacent to Busmantsi — smaller, cleaner, with better chairs."* (N2)
- **They answer other speakers and voices.** Marley to Johar: *"me sight half him fire. The half him missing: the taking of power by a mind still colonised is the same loom with new tenants."* (N3)
- **They narrow.** 25 of 30 focus on one of the voice's three to five responses; 5 synthesise. The brief asks for this. The cost is three quarters of each voice's positions. Arendt's Night-1 artifact carries her synthesized-voice critique; her *"seat the children"* conclusion stayed behind.
- **They share a move.** 19 of 30 stance fields describe refusing, withholding or not settling. The common shape is: refuse the room's binary, name the prior question, leave it open. The voices differ in grammar more than in move. Inference: this follows from the formulation template (B.2). It bears on an uncertainty the Briefing names itself: *"Whether the detailed responses produce enough variance across the matrices per theme."*
- **One form each.** Every voice used the same form on all three nights: ten forms across 30 artifacts. This supports the decided family-of-forms build (roadmap 1.2, Stage 5).

**On Layer 2.** Whether a well-read essayist could have written these is a judgement for the reader gates and the operator, not for this review. What the data shows is where attribution does work that a generic essayist could not: the River correcting the Octopus from the settlement record; Ibn Battuta classing the detention centre under his own legal categories; the Octopus declining "the advocacy verb".

**Grade: strong as writing, narrow by design.**
- *Value created:* the published substance. Positions with an edge, in ten grammars.
- *Value lost:* breadth (one theme of three to five), the names, and any view of where the voices differ, since each artifact stands alone.

## B.5 Editor

**What the provotype needs.**
- G2: *"exposes tensions rather than resolving them."*
- G11: *"the headline output is selection/juxtaposition, never a synthesized consensus."*
- *"Constitute the collective at specific moments"*: at Step 3 and the closing show (Briefing). Neither happened at Athens, so the dossier is the only place the voices meet.

**Starting point.** `EDITORIAL_ASSESSMENT.md` (2026-05-29) judges the dossiers *"Strong"* as craft, names the signature as voices *"converging on a single finding stated in each tradition's own grammar"*, and notes that *"The room mostly speaks to be refused"* and that five-voice dossiers give each voice about 250 characters. It deep-read Night 3 only. This review read the ten Night-1 and Night-2 bodies and adds five things.

**1. The dossier's opening paragraph is the best report of the room in the pipeline.** It does what C69 asks of a label: names, roles, claims, the split, and what stayed open.
> *"Sean White, who runs one of the seven frontier labs, had called centralised AGI authoritarian and offered a personal AI in every citizen's hand. Helen Edwards, of the Artificiality Institute, reframed the machine as thinking partner … The room split tool against partner, centralised against personal."* (N1 dossier_001)

Its theme abstracts are report-style too: *"Two vocabularies for inhabiting 2050, applauded equally and never adjudicated"* (N3 theme_004). They exist for 13 themes and are angled at each dossier's argument, so they are a comparison set for the C69 test, not a gold standard. Its theme titles are still noun phrases ("The Verdict Inside Belonging").

**2. Convergence is structural, not only a style.**
- All eight multi-voice dossiers frame the voices as making one move: *"four different grammars that turned out to be one move"* (N1 d001); *"Three traditions, one finding"* (N2 d001); *"arriving at the same finding by different roads"* (N1 d002).
- Two of the eight also name a difference: N1 d003 (*"Two voices refuse the same verb differently"*, with the River's correction of the Octopus) and N3 d003.
- **No dossier sets two voices against each other.**
- The cause is upstream of the prose. Routing puts *"each routed voice in exactly one dossier"*, by the theme its artifact focused on (Editor spec). So a dossier's cast is whoever happened to focus there, and its input is their artifacts, not Step 1. The Editor never sees the five-way split on Night 1 theme_004 (B.3). It gets Scheherazade and the River, who agree.
- Against G11 this is the sharpest finding of Part B: the headline output of the only collective surface reads as consensus among the voices.

**3. A published claim about the room that the record does not support.** N2 dossier_005: *"one participant mentioned those held in detention centres who lack body freedom altogether, and the circle walked past it. The fragment fell into the square. No one bent to pick it up."* The chain behind it:
- the vendor's takeaway, one bullet of four from a 130-second recording: *"People in detention centers around the world lack access to body freedom and movement."*
- the extraction `nightwalk2:007`, labelled `reinforced`;
- the Provocateur's narrative: *"ended in a circle … The thread was not picked up"*;
- the dossier's scene.

The reflections were recorded one by one. Whether anyone heard this one, or passed it by, is not in the data. Here the edge was not flattened but invented. C68 A1 reaches the published surface.

**4. Coverage.** 13 of the 18 kept themes got a dossier. The five without:
- N1 theme_003 (myth), theme_005 and theme_006 (democracy; mostly reflections);
- N2 theme_002, the human role in work, the most contested kept theme of Night 2 (4 of 13 challenged);
- N3 theme_002, agency versus imposed good.

On N3 theme_002 **all ten voices** wrote a Step 1 response. Its fault line: *"Whether good ends can ever justify imposition"*. None focused an artifact there, so nothing was published on it.

**5. The construction is partly hidden on its own subject (G5).** On Night 1 theme_004 the Provocateur put the Assembly's own standing to nine voices. `STATE.md` records a rerun *"to remove AI-self-acknowledgment"* from three artifacts, by operator decision: *"only Hannah engages with synthesis as load-bearing meta-frame"*. That is a legitimate editorial call. It is noted here because those responses are the provotype's first condition speaking about itself.

**Grade: adequate against the provotype's goals.** The craft verdict of `EDITORIAL_ASSESSMENT.md` stands.
- *Value created:* the room reported with names and gaps; real headlines; the voices made readable together.
- *Value lost:* the splits among the voices. The only collective surface shows agreement.
- *Roadmap:* the prompt side belongs to **Stage 6** (C57, editor prompt made card-driven; C47, interleave rule made permanent). The routing side is **new**.

## B.6 The published surface

**What the provotype needs.**
- *"Promote [the matrices] from closing-show payoff to governing visual motif across all surfaces."* (DesignPrinciples §2)
- *"Lead every visual with a collision, not a voice."* (§3)
- *"Show the Researcher's theme alongside the Provocateur's formulation."* (§4)
- *"The empty quadrant is a visual statement."* (§8)
- The mapped read-through *"shows that the Assembly produced a mapped disagreement space"*. (Briefing)

**What exists in the repo.**
- **Dossier files (13).** Complete. `panel_speakers` lists 4 to 40 names per dossier; the Night-1 and Night-2 bodies name one to five. The field is the theme's roster, not the speakers cited.
- **Voice pages (30).** The artifact text, form, stance and focus. The title is empty on all 30: by decision C7 the editor's title lives in the dossier headnote, so a voice page reached directly has none. `themes_addressed` lists two to five themes, while 25 of 30 artifacts focus on one.
- **Theme files (24).** `abstract` is the Researcher's inventory summary. `display_title` is one voice's angled formulation title ("Originate or Execute" for N1 theme_001). The fault-line sentence is null in all 18 that flag one. The per-voice formulations are included, which serves §4.
- **The explorer.** Every entity and every field, with cross-links. Its Conference Data page is the Researcher's labels; its Assembly Output page holds the formulations, artifacts and dossiers. Nothing sets two positions side by side. Isolates are not drawn.

**What does not exist.** Step 3 (skipped by decision A1). The closing-show passes: theme identification, per-theme mapping, the matrices (B5, unbuilt). The Day-4 goodbye (B6). The Marley audio render (B7). So no surface shows where ten voices stand relative to each other, and there is no empty quadrant to show.

**What this review cannot see.** The microsite was designed and built outside this repo. How it rendered friction, construction or the overnight gap is not assessed. There is no reception data, so Layer 1 (encounter) cannot be judged at all.

**Grade: weak against the design principles, as far as the repo shows.**
- *Value created:* a complete, inspectable record (G5 is served better here than anywhere).
- *Value lost:* the comparison. The principles ask for a landscape of positions; the record offers a list of pieces.

---

# Synthesis

## Which stage is the bottleneck?

**Not the Researcher.** Its labels are the weakest single output, and they cost two things: the record the operator reads, and the triage's ability to rank. But every later stage that matters goes back to the extractions, and the room's edge reaches the voices and the dossiers largely intact. Testing the C69 fix costs a few dollars.

**The bottleneck is the step from Voice Step 1 to the published surface.**
- Step 1 holds 125 positions, several of them opposed.
- 30 artifacts and 13 dossiers are published. 29 of the 128 voice-and-theme pairs reach a dossier.
- Those that do are framed as converging.
- The stages meant to show disagreement, Step 3 and the closing-show mapping, were not run or not built.

Against the provotype's own tests:
- **G2 and G11:** the published Assembly looks more unanimous than the Assembly that reasoned.
- **The briefing's "three-layer test", Layer 3:** the recorded sessions contain no attendee reference to an artifact. Why is not knowable from this data: there is no reception record. The claim here is narrower: the pipeline produced disagreement and did not publish it.

**A caveat on cause.** The same "refuse the room's binary" move runs through 94 of 128 formulations, 19 of 30 artifact stances and all eight multi-voice dossiers. Some of the published agreement is real, and it is seeded at formulation. A position map would show how much.

## If one stage's design changed

**The Editor.** Today: one dossier per theme, cast from the voices whose artifact focused there, written from their artifacts, framed as one move. Proposed: one dossier per theme, built from **every voice's Step 1 position on that theme**, leading with where they split.

In practice that is two pieces:
1. **A position map per theme** (new): each voice's position in one attributed sentence; where the voices part; what none of them answered. It is "report, don't judge" applied to the Assembly. It is also the briefing's unbuilt *"per-theme mapping"* pass without the matrices.
2. **A dossier prompt that leads with the split** and receives the map (a change to the existing editor prompt).

**Why the Editor and not a new stage.** It exists, it already writes the room well, and it is the only collective surface. The change is mostly to its input. It needs no Step 3 and no closing show.

**The risk.** A map can overstate a split, as the first drafts of this review overstated the room's. It needs the same support check as C69, and the voices' own artifacts must stay untouched.

**Roadmap fit.**
- The dossier prompt change: **Stage 6**, with C57 and C47.
- The position map: **new as a build**. It is specified in outline as B5's per-theme mapping, and it bears on operator decision #9 (the shape of Step 3, C61) and on invariant §11.5 part 4: it is the "collective moment" in its minimum form, juxtaposition.
- It is additive, so it sits under the net-complexity gate: the operator decides.

## Paid tests, with two packages each

Prices per million tokens are the C69 note's (Opus 4.7 $5/$25, Opus 5.5 $4/$20, Fable 5.1 $10/$50), not verified here. Token sizes are this review's estimates from the measured word counts.

| Test | Best value | Best quality |
|---|---|---|
| **T1. C69 labels** (A.6) | ≈ $3: new label prompt on Opus 4.7, one draw, three nights, plus the support check. | ≈ $12–16: the note's full package, plus a cross-night relations pass and the optional Fable arm. |
| **T2. Position map from Step 1** | ≈ $1: two themes (N1 theme_004, seven responses; N3 theme_002, ten), Opus 5.5, plus a support check. Roughly 20K tokens in and 3K out per theme. | ≈ $11: all 18 kept themes on Opus 5.5 (≈ $2.5) and on Fable 5.1 (≈ $6), with a support check on both (≈ $2). |
| **T3. Dossier that leads with the split** (needs T2's output) | ≈ $1–2: two dossiers on the current editor model. Basis: the editor's own estimate of about $3–5 for Athens's 13 dossiers, plus the larger input. | ≈ $10: all 18 kept themes once, and a second draw on five. |
| **T4. Triage on the new labels** (needs T1's output) | ≈ $0.5: the one flags call per night, three nights, compared with the Athens flags. | ≈ $16: per-voice triage and flags on old and new labels, two draws each, then the deterministic selection. About 33 calls per label set per draw. |

**Order:** T1, then T2. T3 and T4 only if their inputs look worth it.

**Not in these numbers:** the engineering (a relabel script, a map script, explorer views) and the operator's reading time.

## Open operator decisions

1. **C69: run the label test, and which package** (A.6). Recommended: best value with the support check, relations map included.
2. **Does a label report an absence?** ("No board member argued for the cuts.") Recommended: yes, as a plain fact without comment; otherwise the Clash reads as a debate.
3. **How are reflections to be narrated?** Recommended: always as separate reflections, never with verbs of exchange. Fix C68 A1 forward.
4. **How are the Assembly's own interventions attributed in labels?** Recommended: "the Voice of X, channelled into the room", as the Night-1 rule already does for dossiers.
5. **Key extractions, or true quotes?** A true quote needs a turn reference in the extraction schema. Recommended: call them key extractions now; add the turn reference when the extraction prompt is next touched.
6. **Audit the Researcher's inferred speaker names** in the six unnamed captures before labels carry them. Recommended: a one-time human pass for Athens.
7. **The position map (T2): test it?** Recommended: yes, on two themes.
8. **The dossier's cast and framing.** Keep "each voice in exactly one dossier, by focus theme", or let a dossier draw on every voice's Step 1 position? Recommended: the second, after T2 and T3.
9. **Step 1's status.** It is "scratchwork: internal, not published". A position map publishes sentences derived from it. Recommended: decide this with decision 7; it also touches the voices' reader gates.
10. **N2 dossier_005's "the circle walked past it".** The published record is otherwise being left as it is. Recommended: note it in the record's known issues; don't rewrite the dossier.

---

## Appendix A — how the counts were made

All counts come from reading JSON under `runs/athens_night_{1,2,3}/` and `published_artifacts/` with offline scripts (scratchpad only).

| Count | Method |
|---|---|
| Panel vs reflection | A session is a reflection if its `session_package.json` has `metadata.source == "vendor"` (5 sessions). |
| Challenged per theme | Sum of `engagement == "challenged"` over the theme's clusters' `extraction_ids`. |
| Single-session cluster | The set of `id.split(":")[0]` over a cluster's `extraction_ids` has size 1. |
| Synthesized open questions | `lens == "open question"` and `speaker` is null: 25 of 30, 20 of 29, 13 of 19. |
| Cluster-summary grammar | Opening word matched against `All\|Items\|These\|Arc\|<number word>\|Practical\|Prescriptive`; presence of "—". |
| Unnamed audio captures | Share of words in turns whose `speaker` matches `^(Unidentified\|Audience Member)`; six captures at 100%. |
| Reflection compression | Words per session against the sum of `_vendor_duration_seconds`. |
| Distinct extractions quoted / engaged | Union of `selected_quotes[].extraction_id` over formulations; union of `extractions_engaged` over Step 1 files. |
| Formulation template | Regex `\b[Tt]he (room\|panel\|marathon\|assembly\|circle\|gathering\|day)\b` on `formulation`; first two words counted. |
| Names in Step 1 and Step 2 | Surnames of non-anonymous extraction speakers for the night, matched as substrings in the text. A rough measure. |
| Focus decisions | `focus_decision` begins "Focus on Response" (25) or "Synthesise" (5). |
| Stance | Regex `refus\|neither\|withhold\|not settle` on `stance` (19 of 30). |
| Dossier convergence | Read by hand for Nights 1–2. Cross-checked with the regex `one move\|one finding\|same finding\|same verb\|same refusal\|both voices\|converg\|…` on body, headline and subline. Night 3 by regex and `EDITORIAL_ASSESSMENT.md`. |
| Dossier coverage | `dossiers/_index.json` theme ids against `selection.json` kept themes. |
| Voice-and-theme pairs published | Sum of `headnotes` over the 13 dossiers (29). |
| Published-surface fields | `artifact.title`, `themes_addressed`, `fault_line_description` read from all voice pages and theme files. |
| Assembly references in N2/N3 transcripts | Regex over every turn for the Assembly and its voices' names; hits read by hand. |
