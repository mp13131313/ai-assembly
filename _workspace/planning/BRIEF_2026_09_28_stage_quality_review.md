# Brief: judge each stage's output against what the provotype is for (starting with the Researcher)

**For:** one fresh session on **Fable 5.1** (`claude-fable-5-1`).
**Written:** 2026-09-28 by the main working session, at the operator's request.
**Archive this brief** once its findings are filed (`_workspace/planning/WAYS_OF_WORKING.md` §11).

---

## The operator's observation (start here)

In the operator's words, after browsing the Athens Researcher output in the data explorer:

> "the researcher was … somewhat boring / general — like, no finding in itself … the cluster and themes didn't really have a 'position'."

**Your first job is to understand what they mean, precisely, from the data.** Don't argue them out of it, and don't just agree. The operator hasn't fully articulated it yet, so part of your value is naming it.

The main session's first glance, to test rather than assume:
- An extraction is a neutral summary of one speaker's claim (`lens: assertion`, `engagement: reinforced`).
- Clusters are topic labels (e.g. "AI as ontological break from human").
- Themes read like conference-report headings (e.g. "Critical reframings of AI's dominant narrative").
- Nothing at any level states a finding, a tension, what is at stake, or what the Researcher itself noticed that nobody on stage said.

## What the provotype is for

Judge against the project's own goals, not generic quality. Read these first:
- `docs/AI_Assembly_Briefing_v3_1.md`: the project source of truth.
- `docs/design/AI_Assembly_DesignPrinciples.md` and `docs/design/Nine_Modes_of_Implication.md`.
- `docs/AI_Assembly_Frame_Concept_v1.md` and `docs/AUDIENCE_BRIEF.md`.

Name the specific goals you are judging against, with quotes, before you judge.

## Setup and rules

- **Checkout:** you're in your own git worktree. Run `git checkout --detach phase0-fixes`.
- **You write one file, your deliverable, and don't commit it.** No other edits.
- **No real API calls.** Don't re-run any pipeline stage or anything that calls a model. Offline scripts that read, count or sample the data are encouraged; mention them.
- **`/Users/aienvironment/Desktop/AI Assembly/projects/athens-2026` is read-only.** Everything you need is there:
  - `runs/athens_night_{1,2,3}/`:
    - `01_transcription/`
    - `02_researcher/` (`<session>_extractions.json`, `all_extractions.json`, `clusters.json`, `grouping.json`)
    - `03_provocateur/` (triage, selection, formulations, briefings)
    - `04_voice/` (Step 1 detailed responses, Step 2 artifacts, validation)
    - `05_editor/`
  - `published_artifacts/`: the published record, including the data explorer the operator used (`data_views/view_by_theme.html` + `athens_data_graph.json`, built by `code/runtime/scripts/build_athens_data_graph.py`). Also `EDITORIAL_ASSESSMENT.md` (2026-05-29, one reader's assessment of the dossiers: build on it, don't repeat it) and `DATA_INVENTORY.md`.
- **Label claims** CONFIRMED (seen in the data or code) or PLAUSIBLE. Label inferences as inferences. Design decisions are the operator's: present options with trade-offs and recommend one.
- **Quote real examples,** with ids (extraction id, cluster_id, theme_id, file), for every judgment.

## Part A: the Researcher, in depth

1. **See it.**
   - Read a substantial sample of all three nights' Researcher output: extractions across different session types, all clusters and themes of at least one night, and the data explorer view.
   - Read `docs/AI_Assembly_Researcher_Pipeline.md` and the three prompts (`runtime/flows/shared/prompts/researcher_{extraction,clustering,theming}.md`), plus how `runtime/flows/researcher_flow.py` assembles them.
2. **Name what the operator means.**
   - Write down, concretely, what "no finding in itself" and "no position" look like in this data, with examples.
   - Then show the contrast: rewrite 2–3 real clusters or themes as a positioned version, meaning what the Researcher could have said. Label these clearly as illustrations, not proposals for the prompt text.
3. **Why it's like this.**
   - Trace it to the design: which spec decisions and which prompt instructions produce the flatness (neutral-reporter instructions, the lens taxonomy, clustering by topic, abstracts that summarize).
   - Was neutrality **intended**, e.g. the Researcher reports and the Provocateur supplies the edge? Check the Provocateur spec and prompts.
   - Then follow the effect downstream: did the flatness carry into the Provocateur's formulations and the voices' responses, or did later stages recover the edge? Use evidence.
4. **What could be different.** Give options, each with what changes (spec, prompt, schema, or a new layer), an example of the output it would produce, the risks, and a recommendation. Examples of options:
   - extraction that also captures what is at stake or where the tension lies;
   - clustering by disagreement or fault line instead of by topic;
   - themes stated as propositions, or as questions with named sides;
   - a separate "Researcher's finding" field that keeps the neutral layer intact.

   Watch the main risk: a Researcher that takes positions could pre-empt the voices' own reading and flatten the plurality the Assembly exists for. Say how each option handles that.

**Checkpoint:** after Part A, write it into your deliverable. Then give the operator a short summary, asking whether your reading matches what they meant. **Wait for their answer before starting Part B.**

## Part B: every other stage, same lens

For each stage (Transcription, Provocateur, Voice Step 1 and Step 2, Editor, and the published surface):
- **What the provotype needs from this stage.** Quote the goals.
- **What it actually produced at Athens,** with real examples.
- **A grade:** strong, adequate or weak, with the reason. Where value is created, and where it is lost.
- **For the Editor,** start from `EDITORIAL_ASSESSMENT.md` and add only what it misses.

Then the synthesis: **which stage is the bottleneck for the provotype's goals?** If you could change one stage's design, which would it be and why? Keep this consistent with the roadmap (`_workspace/planning/PLAN_2026_06_12_post_athens_roadmap.md`): say where a proposal fits (Stage 4 prompt backport, Stage 5 designs, Stage 6), or that it's new.

## Deliverable

Write `_workspace/planning/runtime/REVIEW_2026_09_28_stage_output_quality.md`, uncommitted. Lead with a one-paragraph summary, then Part A, then Part B, then the synthesis and open operator decisions. Plain language, examples over adjectives, no praise.
