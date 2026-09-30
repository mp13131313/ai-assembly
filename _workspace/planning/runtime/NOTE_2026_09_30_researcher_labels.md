# Researcher cluster and theme labels: inventories, not headlines

**Date:** 2026-09-30 · **Author:** main session (Opus 5.5), with the operator · **Filed as:** runtime OPEN_ITEMS C69 · **Related:** `REVIEW_2026_09_28_stage_output_quality.md` Part A (the stage-quality review; this note answers its checkpoint)

## The operator's complaint

Browsing Athens in the data explorer, the Researcher's output felt "boring / general". The operator does **not** want to change the clustering. The KJ affinity grouping is the right place for neutrality. The problem is how the clusters and themes are *titled and summarised*: they could be "a really cool map", and they aren't.

## 1. The Researcher is KJ, deliberately (CONFIRMED)

- Briefing: grouping is "affinity-diagrammed themes via modified KJ Method"; the Researcher is unbiased (`docs/AI_Assembly_Briefing_v3_1.md:156`).
- Two rounds: statements into clusters (`runtime/flows/shared/prompts/researcher_clustering.md`), clusters into themes (`researcher_theming.md`).
- Neutrality was engineered in spec v3 (April 2026, `docs/AI_Assembly_Researcher_Pipeline.md` changelog §D, §E, §G):
  - content-only input: no speaker, session or type;
  - a fixed-seed shuffle of the input order;
  - summaries rewritten from the v2.2 "declarative finding" style into "why these belong together".
- The April validation measured **structure only**: cluster size and cross-session ratio (spec §H, :632). No measure covered how the labels read.

## 2. What is off: the labels are inventories, not headlines

The statements are sharp and arguable; the labels turn them into topics. The mechanism is **nominalization**: a claim with a verb and an edge becomes a noun phrase, losing who argues against what and the stakes.

| Statement (inside the cluster) | What the label made of it |
|---|---|
| "Idiocy has no witnesses, only accomplices" (N1 cluster_019) | "reframing idiocy from individual deficit to interactional or systemic property" |
| "Most corporate layoffs framed as AI-driven are … an excuse for companies that previously over-hired" (N2 cluster_019) | "prior over-hiring as the actual cause (152)" |
| "Progressives undermine themselves by always asking 'who's not in the room?'" (N3 cluster_013) | "the willingness to take rather than dissolve power" |
| "We are making culture … on a river of frozen tears" (N3 cluster_013) | "interior healing of generational trauma" |

Titles name an area: "Affective stances toward the future", "How a better future arrives", "AI in creative practice". The few titles with an edge restate a single session's shared view, e.g. "AI-driven layoffs as cover, not transition".

## 3. Why the prompts produce this

1. **Titles are told to be topics.** "Plain and topical … do not try to cram the binding into the title" (`researcher_clustering.md:83`). Kawakita's original KJ asks for the opposite: a group label is a short sentence that keeps the essence of its cards. *(Main session's knowledge of the method; not checked against a source here.)*
2. **The summary is written for an auditor.** Its three jobs are territory, proof that the grouping is valid, and a size test (`:43-46`). None of them is "tell a reader what was said". So summaries open "Nine items reframe…" and list them.
3. **One sentence has to cover every item.** Athens clusters average 5.5 / 5.6 / 8.7 items (Nights 1–3; max 25), against 4.1 in the MSC run the prompt was tuned on. 28 of 35 Night-2 summaries are lists of four or more items.
4. **The ban on "declarative findings" is too broad** (`:57-59`). It was meant to stop the Researcher asserting an answer. It also stops it *reporting what the speakers claimed*, which is faithful, not editorial.
5. **Themes are built from the inventories.** The theme round sees only cluster titles and summaries, never statements (`researcher_theming.md:3`). Its own good examples are findings (`:57-61`), and the cluster prompt calls findings "the theme-level move" (`:57`), but no claims reach it. Theme summaries end up routing between cluster ids.

**Also: the pipeline stops halfway through KJ.** The full method continues with a chart of relations between groups (cause, opposition, dependence; "A-type") and a written narrative through the chart ("B-type"). That is where KJ produces findings, and they stay neutral because they come from the map. *(Main session's knowledge of the method.)* The "map" the operator pictures is that missing chart.

## 4. The neutral line, and what would change

**Report, don't judge.** "Speakers said X, one countered Y, it was left open whether Z" is neutral. "X is true" is not.

What would change (the cluster memberships stay the same):
- **Title:** a sentence that states the cluster's core claim, or its question with the sides.
- **Summary:** what was said, attributed to speakers: the sharpest claims near-verbatim, the split inside the cluster, what stayed open. It may run longer than one sentence.
- **Key statements:** one or two verbatim statements per cluster, chosen as the most representative.
- **Binding:** the "why grouped" sentence moves to its own audit field.
- **Theme round:** it also sees each cluster's key statements.
- **Optional:** a relations step between clusters (contradicts / answers / builds on), which gives the map.

Illustrative rewrites. These are the main session's drafts, untested:
- **N3 cluster_013** ("How a better future arrives"): title *"Crisis, healing, or taking power: how does a better future come?"*; summary *"The Beastopia panel split three ways: coming crises will force reinvention; collective healing of generational trauma must come first ('a river of frozen tears'); progressives dissolve the power already in the room by asking who is missing. The panel asked, and left open, whether these compete or are one path."*
- **N1 cluster_013** ("Modern democracy bent or hollowed"): title *"Democracy has drifted from its purpose; renewal may need a collapse"*; summary *"Speakers agreed modern democracy now serves the few and has lost Athens' patient wrestling; they split on the cure: civic education, institutionalized reminders of purpose, or, for two of them, a period of destruction like the chaos democracy was born from."*

## 5. Test: rewrite the labels only, on fixed Athens memberships

The Athens cluster and theme memberships are kept exactly as they are; only the labels are regenerated. Outputs go to a sandbox, e.g. `projects/current-tests/researcher-relabel/`, never into athens-2026, which stays read-only. The operator compares old and new side by side in the explorer.

**Sizes (measured 2026-09-30):**
- The relabel input, statements plus context, is ≈ 22.8K / 22.7K / 14.0K tokens (Nights 1–3), 59K in total.
- 86 clusters and 24 themes.

**Assumptions (not measured):**
- ≈ 3K tokens of prompt per call.
- A theme-call input of ≈ 34K: new labels plus two key statements per cluster.
- ≈ 250 visible output tokens per label, and thinking about equal to the visible output.
- Together, ≈ 110K input and ≈ 55K output per draw, all three nights.

**Prices** (per MTok, input/output): Opus 4.7 $5/$25, Opus 5.5 $4/$20, Sonnet 5 $2/$10, Fable 5.1 $10/$50.

| Component | Cost (estimate) |
|---|---|
| One draw, Opus 4.7 (the likely Athens model, so a difference comes from the prompt) | ≈ $1.9 |
| One draw, Opus 5.5 | ≈ $1.6 |
| One draw, Sonnet 5 (new tokenizer, ~30% more tokens) | ≈ $1.0 |
| One draw, Fable 5.1 | ≈ $3.9 |
| Support check of one label set (Opus 5.5: is every attributed claim in the cited statements?) | ≈ $1.0 |
| Relations map, three nights (Opus 5.5) | ≈ $0.6 |

**Best value, ≈ $2:** the new label prompt on Opus 4.7, one draw, all three nights, clusters and themes. The operator reads it in the explorer. It answers "does the label instruction fix the complaint?" with no model confound.

**Best quality, ≈ $11 (≈ $15 with a Fable arm):**
1. A control: the *current* label prompt re-run on the fixed memberships (Opus 4.7), to separate run-to-run noise from the prompt effect. ≈ $1.9.
2. The new prompt on Opus 4.7, two draws, for variance. ≈ $3.8.
3. The new prompt on Opus 5.5, one draw, for the forward model (C62). ≈ $1.6.
4. A support check on all three new label sets. ≈ $3.0.
5. The relations map on the best set. ≈ $0.6.
6. Optional: a Fable 5.1 arm. ≈ $3.9.

**Not in these numbers:** the engineering. That is a relabel script and prompt plus a way to show both label sets in the explorer, which is Sonnet-shaped work. The operator's own reading time.

## Status

Filed 2026-09-30 as runtime C69, 🔵 operator decision: whether to run the test, and which package. The stage-quality session received this reading as the operator's checkpoint answer. Its Part B grades the other stages on the same axis: does each stage keep the edge of what was said?
