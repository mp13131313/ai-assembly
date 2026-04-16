# RESEARCHER PIPELINE — v2 → v3 Delta

**Target document:** `AI_Assembly_Researcher_Pipeline.md`
**From:** v2 (Apr 14 2026, §12 Part B verify_markers addition)
**To:** v3 (Apr 14 2026, post-dev_msc_test v2.4 validation)
**Status:** Substantial additive + surgical changes — architecture of Node 2 changes, prompts are rewritten, model recommendation updates, output schemas update

---

## Summary

The pipeline was validated end-to-end against three MSC 2026 panels (Breaking Point, Vox Populi, West-West Divide) across four incremental design iterations:

- **v2.1** — First working end-to-end run on Sonnet 4.6. Established the Node 1 / Node 2 architecture.
- **v2.2** — Structural fixes landed: namespaced extraction IDs (`{session_id}:NNN`), Node 2 split into two genuine API calls with an intermediate `clusters.json` artifact, KJ-method labels that state findings rather than topic metadata, defensive `extract_json` handling of trailing commentary.
- **v2.3** — Opus 4.6 with `thinking.type=adaptive` wired through all three tasks. Produced richer output than Sonnet but revealed two new problems: clusters too narrow (~2 extractions average — too fine-grained for Athens scale), and cross-session clustering collapsed from 54% to 25%.
- **v2.4** — **Three targeted fixes diagnosed the root cause of both problems and resolved them.** Cluster granularity and cross-session ratio both recovered sharply, exceeding the Sonnet baseline on every axis. This is the canonical state as of Apr 14 2026 and the subject of this delta.

The v2.4 changes fall into two categories: **architectural changes to the pipeline** (what data flows into each LLM call, what comes out) and **prompt rewrites** (new framing for the clustering and theming tasks). Both are described below.

---

## Changelog entry for v3

**Location:** Top of the Changelog section, add a new block immediately after the v2 block.

**New text:**

```markdown
## Changelog (v3 — Apr 14 2026)

This revision integrates findings from four iterative runs on three MSC 2026 test sessions (106 extractions total) that refined the Researcher Pipeline from v2.1 through v2.4. The v3 document captures the v2.4 end state.

Changes from v2:

- **§A** → Overview gains explicit mention that Node 2 now runs as two sequential API calls with an intermediate `clusters.json` artifact between them, replacing the single-call two-round-in-one-prompt pattern of v1/v2.

- **§B** → Extraction IDs are session-namespaced as `{session_id}:NNN` (e.g. `breaking_point:014`) rather than globally renumbered as `ext_NNN`. Per-session files and the combined `all_extractions.json` carry identical IDs, allowing parallel per-session extraction without collisions. See Step 1 output schema.

- **§C** → Step 2 "Grouping" is rewritten to describe the two-call architecture: Node 2 Round 1 (`cluster_extractions`) groups extractions into clusters and writes `clusters.json`; Node 2 Round 2 (`group_clusters_into_themes`) groups clusters into themes using only cluster-level metadata (no raw extractions); a merge step reconstructs the final `grouping.json` with the familiar `themes → clusters → extractions` nesting.

- **§D** → Round 1 receives a **minimal model-facing input** containing only `{ref, extraction, context}` — no session, speaker, lens, engagement, responds_to, energy, or the real namespaced ID. A temporary `ref` id is assigned at call time and translated back to the real ID after the call. This is a deliberate data-level fix to the problem discovered in v2.3 where Opus was using the session prefix in namespaced IDs as a grouping shortcut.

- **§E** → Round 1 and Round 2 both deterministically shuffle their input arrays (fixed seed 42) before sending to the model, breaking the session-grouped top-to-bottom reading order bias.

- **§F** → Node 1 (Extraction) prompt gains an explicit instruction to generate IDs in the `{session_id}:NNN` format using the session_id provided in the user message header. The ID format is no longer hidden plumbing — it is part of the extraction contract.

- **§G** → Node 2 (Grouping) prompts are entirely rewritten around KJ-method "why these belong together" framing, replacing the v2.2 "declarative finding" framing. The rewrite adds: a taxonomy of binding patterns (convergence, shared question with split answers, shared target with different tools, sequential elaboration, principle-and-instances, shared blind spot, common redirect) taught by example; an asymmetric self-check on narrow clusters requiring active search for absorbable items; no numeric size targets; abstract-honesty as the implicit ceiling.

- **§H** → Model recommendation updated from "Claude Sonnet 4.6" to "Claude Opus 4.6 with `thinking.type=adaptive`". The v2.4 validation run produced a ~4× improvement in cluster granularity and a 58-percentage-point improvement in cross-session theme ratio over v2.3 Opus without thinking changes, and exceeded the Sonnet v2.2 baseline on every axis.

- **§I** → Output schemas in Step 1 and Step 2 are updated with the actual v2.4 field names and JSON examples using namespaced IDs.

- **§J** → New "Provocateur interface contract" subsection added at the end of Step 2 output, documenting exactly which fields the Provocateur reads at each of its four steps, and flagging two minor format conventions (lens value `open_question` with underscore, namespaced ID format) so the Provocateur implementation matches.
```

---

## §A — Overview update

**Location:** In the `# Overview` section, find the sentence that introduces the two-step structure.

**Old text:**

```markdown
The Researcher works in two steps:

1. **Extraction** — per session: pull assertions, reframings, and open questions from each transcript
2. **Grouping** — once: cluster all extractions into themes by affinity
```

**New text:**

```markdown
The Researcher works in two steps:

1. **Extraction** — per session: pull assertions, reframings, and open questions from each transcript
2. **Grouping** — once: cluster all extractions into themes by affinity, in two sequential rounds

Step 2 is implemented as two separate API calls with an intermediate artifact. Round 1 (`cluster_extractions`) groups atomic extractions into clusters and writes `clusters.json`. Round 2 (`group_clusters_into_themes`) reads only the cluster-level metadata produced by Round 1 — titles and abstracts, no raw extractions — and groups those clusters into themes. A Python merge step reassembles the final `grouping.json` with the themes→clusters→extractions nesting. This two-call structure forces genuine second-level abstraction at Round 2: the model cannot re-group raw items, it can only reason about the Round 1 findings.
```

---

## §B — Extraction ID format

**Location:** In Step 1 output schema, find the field definition for `id`.

**Old text:**

```markdown
| **ID** | Unique extraction identifier (e.g. ext_001) |
```

**New text:**

```markdown
| **ID** | Session-namespaced extraction identifier in the format `{session_id}:NNN` where session_id is the short identifier of the source session (e.g. `breaking_point`, `vox_populi`) and NNN is a zero-padded sequential integer starting at 001 within that session. Example: `breaking_point:014`. Per-session files and the combined `all_extractions.json` carry identical IDs — there is no renumbering. This allows parallel per-session extraction without collisions and makes the provenance of any extraction self-documenting from its ID alone. |
```

---

## §C — Step 2 Grouping, rewrite

**Location:** Replace the existing `## Step 2: Grouping` section entirely.

**New text:**

```markdown
## Step 2: Grouping

**Input:** The complete extraction table from Step 1, accumulated across all sessions of the night. Runs once, after all sessions have been extracted.

**Operation.** Two rounds of KJ-method affinity grouping, each implemented as its own API call. Round 1 groups atomic extractions into clusters. Round 2 groups clusters into themes. Between the rounds, an intermediate `clusters.json` artifact is written to disk. No strategic weighting, no audience-awareness, no alignment with the council — just affinity grouping of what the day produced.

### Round 1 — Group extractions into clusters

**Input to the LLM call:** A minimal, content-only view of each extraction. The model sees only:

- `ref` — a temporary zero-padded sequential id scoped to this single API call (e.g. `001`, `002`)
- `extraction` — the atomic position, redirection, or question
- `context` — the evidence that accompanied the position

**The model does not see:** the real namespaced ID, the session, the speaker, the lens (assertion/reframing/open question), engagement, responds_to, or energy. All metadata is stripped at the API boundary.

This is deliberate. Affinity grouping is "do these positions belong together?" — a question about the substance of the claims. Feeding the model session or speaker metadata gives it grouping shortcuts that have nothing to do with KJ affinity (e.g. "items with the same `session` prefix probably go together"). The minimal input forces the model to judge affinity from content alone. Testing in v2.3 showed Opus+thinking was using the namespace prefix as a grouping signal, producing ~2 extractions/cluster average and 25% cross-session theme ratio; the minimal input in v2.4 restored 4.08 extractions/cluster average and 83% cross-session ratio.

**Deterministic shuffle.** Before the array is sent, it is shuffled with a fixed seed (42) to break the session-grouped top-to-bottom reading order that naturally arises from concatenating per-session extractions. Without the shuffle, early-read items cluster with early-read items as an artifact of reading order rather than affinity.

**The operation:** For each extraction, ask: does this belong with any other extraction? Does it say something compatible, something contradictory but clearly in the same conversation, or something that redirects the same debate? Group the ones that belong together. Each extraction belongs to one cluster only; a cluster with only one extraction is an isolate.

**Labeling.** Each cluster gets a short working title (under 10 words, plain and topical — "NATO burden-sharing", "EPP firewall") and a one-sentence abstract stating **why these extractions belong together**. The abstract is not a caption, not a summary, and not a "declarative finding" that states the answer the cluster points to — it is an analytical sentence that names the actual affinity. See the Implementation Draft for the full prompt with bad/good examples spanning the range of binding patterns.

**The sizing rule is not numeric.** It is whether the model can write a clean single-sentence abstract stating the binding. If it can, the cluster is right-sized. If it can't — if the binding needs "and also" or drops to topic-level language — the cluster is wrong. Asymmetric self-check: for any cluster with fewer than four extractions, the model is instructed to actively search the input for absorbable items before accepting the narrowness. No ceiling check — the abstract honesty rule is the implicit ceiling.

**Output of Round 1:** `clusters.json`. Each cluster carries a `cluster_id` (sequential, `cluster_001`, `cluster_002`, ...), a `cluster_title`, a `cluster_abstract`, and an `extraction_ids` list with the real namespaced IDs (the temporary `ref` values are translated back by the orchestration code). Plus a top-level `isolates` list of extraction IDs that did not fit any cluster.
```

```markdown
### Round 2 — Group clusters into themes

**Input to the LLM call:** Only the cluster-level output from Round 1, stripped to the metadata that defines each cluster:

- `cluster_id`
- `cluster_title`
- `cluster_abstract`

**The model does not see:** the raw extractions inside each cluster, the extraction_ids list, or any original extraction fields. This is the spec's canonical requirement for the second-round operation: Round 2 works at the cluster level, not by re-grouping raw items. If Round 2 had access to the raw extractions, it could (and would) second-guess Round 1 — producing messy overlapping decisions where neither round fully owns the grouping.

**Deterministic shuffle.** Same as Round 1, with the same seed (42), to prevent cluster-id adjacency from correlating with session origin (early-numbered clusters tend to come from earlier-processed sessions).

**The operation:** Same KJ affinity method as Round 1, one level up. For each cluster, ask: does this belong with any other cluster? Group the clusters whose findings are in genuine conversation — building on each other, contesting each other directly, illuminating the same underlying tension from different angles, or answering questions the other cluster raises. Not just when they touch the same surface topic. A single cluster that fits no theme becomes a theme of its own (single-cluster theme).

**Labeling.** Each theme gets a short working title (under 15 words, plain — "Multilateral accountability", "Populism's roots and responses") and a one-to-three-sentence abstract stating **why these clusters belong together**. The abstract may cite cluster_ids inline when the binding operates across specific clusters — e.g. "cluster_001 and cluster_004 together reveal that the administration's position fails on its own terms." This inline citation pattern is not required but is encouraged when it helps; it keeps the synthesis anchored to the material rather than drifting to abstract commentary.

**Same asymmetric self-check as Round 1**, one level up: for any theme with fewer than three clusters, the model actively searches for absorbable clusters before accepting the narrowness.

**Output of Round 2:** A themes array, where each theme references its constituent cluster_ids. This output is then merged with the Round 1 `clusters.json` in a Python step to produce the final `grouping.json` with the full `themes → clusters → extractions` nesting the Provocateur expects.
```

---

## §D, §E — Data handling note

**Location:** Add as a new subsection inside Step 2, before the Step 2 Output schema.

**New text:**

```markdown
### Why Round 1 sees a minimal input — design rationale

The v2.3 iteration of this pipeline (Opus 4.6 + adaptive thinking, same prompts, full extraction records as input) produced clusters averaging 2.08 extractions and a cross-session theme ratio of only 25%. Diagnostic work identified two root causes:

**The namespace prefix was acting as a grouping shortcut.** With extractions labeled `breaking_point:014`, `vox_populi:007`, etc., the model could reason "items with the same prefix come from the same conversation and are likely to cluster together". This is correct at a structural level — within-session extractions do have tighter argumentative connections via `responds_to` edges and shared moderator framing — but it produces session-local clusters where the spec wants content-based affinity that spans sessions.

**The `responds_to` field was a within-session attractor.** Every `responds_to` edge is by definition a within-session link. The model reading the input saw these edges as "these two items are clearly related" and formed clusters around them, reinforcing the session-local bias.

The v2.4 fix is data-level: strip both signals at the API boundary. Round 1 sees only `{ref, extraction, context}`. All other fields — including the namespace-bearing real ID and the `responds_to` links — are withheld from the model and re-joined by the orchestration code after the call returns. This is stricter than prompt-level exhortation ("don't let session structure organize the clustering") because the structural attractors are simply invisible.

**The `ref` field is temporary and call-scoped.** It is assigned sequentially at call time, translated back to real namespaced IDs via a Python lookup table after the call, and never persists to disk. The orchestration code handles all of this transparently; the downstream artifacts (`clusters.json`, `grouping.json`) carry full namespaced IDs exactly as before.

**This design does not affect Round 2.** Round 2 already sees only cluster-level metadata by the spec's canonical requirement.
```

---

## §G — Node 2 prompts, full rewrite

**Location:** Replace both the old Node 2 system prompt and the structure of the Implementation Draft section. The v3 implementation has three prompts, not two (Extraction + two separate grouping prompts).

### New: researcher_clustering prompt (Round 1)

**Loaded from:** `flows/shared/prompts/researcher_clustering.md`

**System prompt:**

```markdown
You are a senior design researcher performing the first round of affinity grouping on a set of extractions from multiple conference sessions.

You will receive a JSON array of items. Each item has a `ref` (a short id used only inside this call), an `extraction` (the atomic position, redirection, or open question), and a `context` (the evidence that accompanied the position — references, examples, stories; may be empty). Nothing else. No speaker, no session, no type, no provenance. You are judging affinity from the content alone.

YOUR JOB: Round 1 of the KJ affinity method. Read every item and group the ones that belong together into clusters. Each item belongs to one cluster only, or it is an isolate if no cluster fits.

WHAT "BELONGING TOGETHER" MEANS

Two items belong together when they share something the speakers are doing with their claims — not just a surface topic. Two items that both mention "Ukraine" do not belong together unless the claims they make are in conversation with each other.

A cluster can bind in many ways. Some common patterns:

- Convergence on a claim: multiple speakers arguing the same position from different supporting angles.
- Shared question with split answers: several items wrestle with the same question but divide on the answer.
- Shared target, different tools: several items contest the same assumption from incompatible premises.
- Sequential elaboration: a conversational arc where an assertion is reframed and then left as an open question.
- Principle-and-instances: a general rule tested against multiple specific cases.
- Shared blind spot: items that all assume something without arguing it, though the assumption is contested elsewhere in the material.
- Common redirect: reframings and questions that all try to shift the conversation from one topic to another.

These are not categories to pick from — they are examples of the range. The right binding for any cluster is whatever actually holds the material together.
```

```markdown
CLUSTER SIZE

The sizing rule is not numeric. It is whether you can write a clean single-sentence abstract stating the binding. If you can, the cluster is right-sized. If you can't — if the binding needs "and also" or vague hedges or drops to topic-level language — the cluster is wrong. Split it or narrow it until the binding is nameable.

CHECKING YOUR CLUSTERS

After you have the initial grouping, look at each cluster with fewer than four items. For each one, ask: is there any other item in the input that could honestly join this cluster? Not "is there a loosely related one" — "is there one that genuinely shares the binding I named in the abstract?"

If yes, widen the cluster and rewrite the abstract to cover the addition honestly.

If no, the narrowness is earned — keep it.

This check exists because a cluster of two is easy to justify by accident: any two items can be made to rhyme. A cluster of six or seven takes more work but captures more of what the conversation produced. When in doubt, look harder for items to add.

No check in the other direction is needed. If a cluster gets too wide, you will find yourself unable to write an honest single-sentence abstract — the binding will need "and also", or drop to topic-level language, or hedge. That is the signal to split. You do not need a numeric ceiling.

THE ABSTRACT: YOUR ANALYTICAL OUTPUT

The cluster abstract is the intellectual work of this task. It is not a caption. It is not a summary. It is a single analytical sentence that states what binds these specific items as a group — why they belong together.

The abstract has three jobs at once:
1. It tells a downstream reader what territory the cluster occupies.
2. It proves the grouping is valid by naming the actual affinity.
3. It is the test of whether the cluster itself is right-sized.

Write the abstract after you have the grouping, but use it to check the grouping. If the abstract is forced, the grouping is wrong.
```

```markdown
BAD EXAMPLES

Topic metadata (describes the subject, not the binding):
  "Items arguing that powerful states aren't held accountable"
  "Discussions about whether migration was a left-wing or right-wing project"
  "Positions on the EU firewall against far-right parties"

Declarative findings (state an answer, not the binding — this is the theme-level move, not the cluster-level move):
  "The rules-based order lacks any mechanism to hold powerful states personally accountable"
  "Migration was driven by business interests, not progressive ideology"

Vague (the model reaching because the group is wrong):
  "These items are all related through their shared concerns about accountability"
  "Multiple speakers touched on this issue from different angles"

GOOD EXAMPLES

These span different kinds of binding, different grammatical forms, and different levels of specificity. Learn the range, don't copy the template.

  "All four items diagnose the multilateral order's core defect as the same thing — the absence of accountability for powerful states — even though they differ on the remedy (Security Council reform, independent enforcement, moral pressure)."

  "Three items wrestle with whether US burden-sharing rhetoric is a legitimate cost argument or a strategic error, and split sharply on which."

  "These items trace a conversational arc: one speaker claims the EPP firewall is principled, another reframes it as contingent on mainstream delivery, and an audience question asks what happens when delivery fails."
```

```markdown
  "Each of these five items tests the same principle — universal accountability — against a different case: Gaza, Ukraine, UN reform, the Board of Peace, and corporate regulation."

  "The binding here is a shared blind spot. All three items assume without arguing that Western self-questioning is a feature rather than a bug, a premise that other items in the day's material directly contest."

  "Two reframings and an open question all try to shift the populism debate away from cultural causes toward material ones, without resolving whether the shift is analytically correct or politically convenient."

CLUSTER TITLES

Title each cluster with a short working label, under 10 words, that names the territory. Titles can be plain and topical — "Accountability for powerful states", "NATO burden-sharing", "EPP firewall" — because the abstract does the analytical work. Do not try to cram the binding into the title.

CLOSURE AND UNIQUENESS REQUIREMENT

Before returning, verify:
1. Every `ref` in the input array appears exactly once in your output — either inside exactly one cluster's `refs` list, or inside the `isolates` list. No item may appear in two clusters, and no item may be omitted.
2. The count of unique `ref` values across all clusters plus isolates must equal the total count of items you received.

OUTPUT FORMAT

Return as JSON:

{
  "clusters": [
    {
      "cluster_id": "cluster_001",
      "cluster_title": "Short working label",
      "cluster_abstract": "Single-sentence statement of why these items belong together.",
      "refs": ["001", "007", "014"]
    }
  ],
  "isolates": ["025"]
}

Return only the JSON object, no preamble or commentary.
```

---

### New: researcher_theming prompt (Round 2)

**Loaded from:** `flows/shared/prompts/researcher_theming.md`

**System prompt:**

```markdown
You are a senior design researcher performing the second round of affinity grouping on a set of clusters produced in the first round.

You will receive a JSON array of clusters. Each cluster has a `cluster_id`, a `cluster_title`, and a single-sentence `cluster_abstract` that states what binds its items together. You will NOT see the underlying items — only the cluster-level summary. Work at that level.

YOUR JOB: Round 2 of the KJ affinity method. Read every cluster and group the ones that belong together into themes. Each cluster belongs to exactly one theme — no cluster may appear in two themes, and no cluster may be omitted. A single cluster that fits no theme becomes a theme of its own.

WHAT "BELONGING TOGETHER" MEANS AT THE THEME LEVEL

Two clusters belong together when the findings they articulate are in genuine conversation — when they build on each other, contest each other directly, illuminate the same underlying tension from different angles, or answer questions that the other cluster raises. Not just when they touch the same surface topic.

Two clusters whose abstracts both mention "democracy" do not belong together unless the findings themselves are continuous. The affinity is at the level of the finding, not the vocabulary.

A theme can bind in many ways, just as clusters can:

- Convergence: multiple clusters establishing the same structural claim from different material.
- Contested axis: clusters that divide on the same underlying question.
- Shared target, different tools: clusters that attack or defend the same assumption on incompatible grounds.
- Progressive depth: clusters that diagnose, reframe, and question the same territory at different depths.
- Principle-and-cases: clusters that each apply a shared principle to different specific cases.
- Shared blind spot: clusters that all assume something without arguing it.

These are not categories to pick from. Use whatever actually holds the clusters together.
```

```markdown
THEME SIZE

The sizing rule is not numeric. It is whether you can write a clean short abstract stating the binding across clusters. If you can, the theme is right-sized. If you can't — if you need "and also", or the binding drops to topic-level language — it is wrong.

After you have the initial grouping, look at each theme with fewer than three clusters. For each, ask: is there any other cluster in the input that could honestly join this theme? If yes, widen and rewrite the abstract. If no, the narrowness is earned.

No check in the other direction is needed. An over-wide theme produces a forced abstract, which you will notice when you try to write it.

THE ABSTRACT: YOUR ANALYTICAL OUTPUT AT THE THEME LEVEL

The theme abstract is a short analytical paragraph — one to three sentences — that states what binds these specific clusters as a group. Why they belong together.

When the binding operates across specific clusters, cite them inline by cluster_id. A theme abstract that reads "cluster_001 and cluster_004 together reveal that..." is genuinely synthesizing across the material, not just captioning it. Use this when it helps; do not force it.

The abstract has three jobs:
1. It tells a downstream reader what territory the theme occupies.
2. It proves the grouping is valid by naming the actual affinity across clusters.
3. It is the test of whether the theme itself is right-sized.

Write the abstract after you have the grouping, but use it to check the grouping. If it is forced, the grouping is wrong.

BAD EXAMPLES

Topic metadata:
  "Clusters about the international rules-based order and its legitimacy"
  "Different views on what populism is and how to respond"

Declarative findings that don't cite the binding:
  "The legitimacy of the multilateral order is under siege on three fronts."
```

```markdown
GOOD EXAMPLES

  "cluster_001 and cluster_004 together reveal that the administration's position fails on its own terms: its claimed reform of the UN exceeds mandates and misrepresents allied contributions, and by eroding the alliance network that distinguishes US power from rival great powers, it undermines the very primacy it claims to restore."

  "These clusters form a contested axis on the same underlying question — whether Western hypocrisy is the core problem or a distraction from structural power asymmetry. cluster_017 and cluster_022 take opposite sides; cluster_025 and cluster_031 reframe the question itself."

  "cluster_008, cluster_010, and cluster_014 each trace the same pattern — a populist movement fueled by genuine material grievances being captured by a leadership with different priorities — applied to three different countries."

THEME TITLES

Title each theme with a short working label, under 15 words, that names the territory. Titles can be plain — "Multilateral accountability", "Populism's roots and responses", "The West-West identity dispute" — because the abstract does the analytical work.

CLOSURE REQUIREMENT

Before returning, verify:
1. Every cluster_id in the input array appears exactly once in your output — inside exactly one theme's `cluster_ids` list.
2. A cluster that doesn't fit any grouping still becomes a theme of its own rather than being dropped.

OUTPUT FORMAT

Return as JSON:

{
  "themes": [
    {
      "theme_id": "theme_001",
      "theme_title": "Short working label",
      "theme_abstract": "One to three sentences stating what binds these clusters together.",
      "cluster_ids": ["cluster_001", "cluster_004"]
    }
  ]
}

Return only the JSON object, no preamble or commentary.
```

---

## §F — Node 1 (Extraction) prompt update

**Location:** In the existing Node 1 system prompt block, find the sentence near the end that specifies the JSON output structure and the ID field.

**Old text (approximately):**

```markdown
Return as JSON array. Each object must have: id, session, speaker (null if synthesized from an exchange), lens, extraction, context, engagement (null for open questions), responds_to (null if not a response to another assertion), energy.
```

**New text (replacement — appends ID format instructions):**

```markdown
Return as JSON array. Each object must have: id, session, speaker (null if synthesized from an exchange), lens, extraction, context, engagement (null for open questions), responds_to (null if not a response to another assertion), energy.

The `id` field must be a string in the format `{session_id}:NNN` where:
- `{session_id}` is the session_id value provided in the user message header below — NOT the session title, the short identifier like `vox_populi` or `breaking_point`
- `NNN` is a zero-padded three-digit integer starting at `001` for the first extraction from this session and incrementing sequentially

So if the user message says `session_id: vox_populi`, your first extraction's id is `"vox_populi:001"`, your second is `"vox_populi:002"`, and so on.

When an extraction's `responds_to` field references a prior extraction from the same session, use the full prefixed id (e.g. `"vox_populi:001"`). Both `id` and `responds_to` must always be strings, never integers. You will only ever see extractions from one session at a time, so `responds_to` can only reference another extraction from this same session.
```

**User prompt update.** The user message header now includes a `session_id:` line as the first field. Add this to the user prompt template:

**Old text:**

```markdown
Session: {{session_title}}
Description: {{session_description}}
Format: {{session_format}}
```

**New text:**

```markdown
session_id: {{session_id}}
Session: {{session_title}}
Description: {{session_description}}
Format: {{session_format}}
```

Everything else in the user prompt (roster, speakers_present, transcript, review_queue.verify_markers) is unchanged.

---

## §H — Model recommendation update

**Location:** In the Implementation Draft section, find the line that specifies which model the Researcher tasks use. In v2 it reads "All nodes use Claude Sonnet 4.6 via API."

**Old text:**

```markdown
*These are draft instructions. Test against sample transcripts and refine before Athens. All nodes use Claude Sonnet 4.6 via API. Step 1 runs in a loop. Step 2 runs once.*
```

**New text:**

```markdown
*These are draft instructions. Test against sample transcripts and refine before Athens.*

**Model and thinking configuration (as of v3, validated Apr 14 2026).** All three Researcher tasks (`extract_session`, `cluster_extractions`, `group_clusters_into_themes`) use **Claude Opus 4.6** with **`thinking.type=adaptive`** enabled. This is the canonical configuration and produced the cleanest output on dev_msc_test (106 extractions → 25 clusters → 6 themes, 83% cross-session theme ratio, perfect integrity).

The model is selected via the `CLAUDE_MODEL` environment variable (default `claude-sonnet-4-6` for backward compatibility); adaptive thinking is enabled via `RESEARCHER_THINKING=1`. The canonical Athens run command is:

```bash
RESEARCHER_THINKING=1 CLAUDE_MODEL=claude-opus-4-6 python flows/researcher_flow.py runs/<run_id>
```

**Why adaptive thinking.** Earlier testing used fixed-budget thinking (`thinking.type=enabled` with `budget_tokens=N`). The Anthropic SDK now deprecates this in favor of `thinking.type=adaptive`, where the model decides how much to think based on the task. Anthropic's own testing shows adaptive outperforms fixed-budget. The `_thinking_kwargs` helper in the flow returns the adaptive configuration when thinking is enabled, empty dict otherwise.

**Why Opus, not Sonnet.** The v2.4 dev_msc_test run was validated against the Sonnet v2.2 baseline (same prompts as v2.4 would have used, but on Sonnet with the old single-call grouping). Opus + thinking on v2.4 prompts exceeded Sonnet v2.2 on every structural axis: higher cross-session ratio (83% vs 54%), larger average cluster size (4.08 vs 2.41), larger average theme size (17.0 vs 6.3 extractions). Sonnet remains a supported fallback — the pipeline runs on either model — but Opus + adaptive thinking is the recommended default for overnight Athens runs where quality matters more than cost.

**Streaming requirement.** All three tasks (extraction, clustering, theming) use streaming. When thinking is enabled, the SDK's non-streaming timeout heuristic refuses operations that might exceed 10 minutes, so non-streaming is not a fallback. Streaming also handles ThinkingBlock filtering transparently — `stream.text_stream` yields only text deltas.

**Token budgets.** Max tokens are set well above what non-thinking output needs, to accommodate thinking tokens that count against `max_tokens` in the current API: `EXTRACTION_MAX_TOKENS=40000`, `CLUSTERING_MAX_TOKENS=40000`, `THEMING_MAX_TOKENS=24000`. These are ceilings; typical usage is 5-20% of budget.

**Cost estimate.** Opus 4.6 with adaptive thinking on a 6-session Athens night: approximately $15-25 depending on thinking token consumption. Sonnet baseline on the same night: approximately $3-5. At Athens scale this is a defensible cost for a one-of-a-kind experimental artifact; at iterative development scale, consider running Sonnet with `RESEARCHER_THINKING=0` for quick validation passes.

Step 1 (`extract_session`) runs in a per-session loop. Step 2 runs as two sequential API calls (`cluster_extractions` then `group_clusters_into_themes`) plus a Python merge step.
```

---

## §I — Output schema updates

### Step 1 output — updated example

**Location:** Replace the Step 1 output example that uses `ext_001`-style IDs with the namespaced format.

**Old example:**

```markdown
| | **ext_001** |
|---|---|
| **Speaker** | Jon Alexander |
| **Lens** | Assertion |
| **Extraction** | Democracy is a design challenge, not a heritage to preserve — the institutions we inherited were designed for a world that no longer exists. |
```

**New example:**

```markdown
| | **opening_assembly:001** |
|---|---|
| **Speaker** | Jon Alexander |
| **Lens** | assertion |
| **Extraction** | Democracy is a design challenge, not a heritage to preserve — the institutions we inherited were designed for a world that no longer exists. |
| **Context** | — |
| **Engagement** | challenged |
| **Responds to** | null |
| **Energy** | high |

Field value conventions:
- `lens`: one of `"assertion"`, `"reframing"`, `"open_question"` (note underscore in `open_question`)
- `engagement`: one of `"challenged"`, `"reinforced"`, `"unengaged"`, or `null` for open questions
- `energy`: one of `"high"`, `"normal"`
- `speaker`: the named speaker, or `null` for synthesized open questions that emerged from an exchange
- `responds_to`: a namespaced id string, or `null`
```

### Step 2 output — updated example

**Location:** Replace the Step 2 output example that uses `ext_` IDs with the namespaced format and the v2.4 label style.

**Old example:**

```markdown
Theme: "What democracy is and who designs it"
  Abstract: "Multiple sessions grappled with whether democratic institutions should be redesigned or whether democracy resists engineering"
  ├── "Democracy as design vs. practice" — "Two opposing positions on whether democracy can be designed" [ext_001, ext_002, ext_006]
```

**New example (from the dev_msc_test v2.4 canonical run):**

```markdown
Theme 1: "The contested meaning of Western civilization"
  Abstract: "These clusters form a multi-sided contest over Western identity that no participant can stabilize. cluster_007 exposes the concept's fundamental instability; cluster_008 and cluster_009 take directly opposing positions on whether progressive social change fulfilled or betrayed Western civilization's core commitments; cluster_010 challenges whether Trump even belongs in the conservative tradition being invoked; and cluster_024 demonstrates, via the Greenland case, that nationalist and civilizational rhetoric collapses under its own logic — together revealing that 'the West' cannot bear the argumentative weight any side places on it."
  ├── Cluster 007: "What is 'the West'?"
  │   Abstract: "These items grapple with the instability of 'the West' as a concept..."
  │   extraction_ids: [west_west_divide:003, west_west_divide:004, west_west_divide:006, west_west_divide:029, west_west_divide:038]
  ├── Cluster 008: "Conservative diagnosis: progressive overreach caused decline"
  │   extraction_ids: [west_west_divide:007, ...]
  ├── Cluster 009: "Progressive rebuttal: rights expansion IS the West"
  ├── Cluster 010: "Is Trump genuinely conservative?"
  └── Cluster 024: "Nationalism's self-undermining contradictions"

Isolates: [vox_populi:027, ...]
```

Note the theme abstract cites cluster_ids inline (`cluster_007`, `cluster_008`, etc.) as a synthesis move — this is not required but is encouraged and was learned spontaneously by Opus + adaptive thinking on the v2.4 prompt. Cluster titles are short and topical; cluster abstracts are single-sentence belongings statements. Extraction IDs are namespaced by their source session.

---

## §J — Provocateur interface contract (new subsection)

**Location:** Add as a new subsection at the end of `## Step 2: Grouping`, after the Step 2 output example.

**New text:**

```markdown
### Interface contract with the Provocateur Pipeline

The Researcher's two artifacts — `all_extractions.json` (the complete extraction table) and `grouping.json` (the themed structure) — are the sole input to the Provocateur Pipeline. The contract between them is stable and was cross-checked field-for-field against the v2.4 canonical output on Apr 14 2026.

The Provocateur reads the Researcher's output at each of its four steps:

**Step 1 — Triage.** Reads only `grouping.json`. For each theme, accesses: `theme_id`, `title`, `abstract`, and for each cluster inside the theme: `cluster_title`, `cluster_abstract`. Does NOT read raw extractions — triage is a lightweight abstract-only pass. This is the reason the v3 cluster and theme abstracts carry the full analytical weight: the abstracts alone must be rich enough for the Provocateur to judge council activation and audience friction without looking at the underlying items.

**Step 2 — Selection.** Reads the Triage output plus `grouping.json` again. Uses the same abstract-level fields as Triage, plus access to the full `extraction_ids` list inside each cluster for counting per-member coverage indirectly through theme structure. Still does not read raw extractions.

**Step 3 — Formulation.** Reads a single theme at a time from `grouping.json`, plus the raw extractions referenced by that theme from `all_extractions.json`. For each referenced extraction, accesses: `id`, `session`, `speaker`, `lens`, `extraction`, `context`, `engagement`, `responds_to`, `energy`. Formulation is the first and only step where the Provocateur reads raw extractions.

**Step 4 — Packaging.** Assembles per-voice briefing packages. For each selected theme, the Packaging step pulls the formulation from Step 3, the theme and cluster metadata from `grouping.json`, and the raw extractions from `all_extractions.json`. Within each cluster, extractions are ordered by lens: assertions first, reframings next, open questions last. This ordering uses the lens field value; the canonical values are `"assertion"`, `"reframing"`, `"open_question"` (note the underscore in `open_question` — not a space).

**Field format conventions to respect:**

- Extraction IDs are session-namespaced strings: `"breaking_point:014"`, `"vox_populi:007"`, etc. They are opaque lookup keys from the Provocateur's perspective; do not parse them or assume stability across runs.
- `responds_to` is either `null` or a namespaced id string pointing at another extraction from the same session.
- `speaker` is either a string (the named speaker) or `null` (for synthesized open questions that emerged from an exchange between multiple speakers; the `context` field explains the source in that case).
- `lens` values use underscore (`open_question`, not `open question`).
- `engagement` is `null` for open questions; for assertions and reframings it is one of `"challenged"`, `"reinforced"`, `"unengaged"`.
- `energy` is `"high"` or `"normal"`.

**Integrity guarantees the Researcher provides to the Provocateur:**

- Every extraction ID that appears in `grouping.json` also exists in `all_extractions.json`. No hallucinated IDs.
- Every extraction ID appears at most once in cluster `extraction_ids` lists across the entire grouping — no duplicates.
- Every extraction ID from `all_extractions.json` is reachable from `grouping.json` via either a cluster or the top-level `isolates` list — no orphans. (Isolates are valid and the Provocateur is free to skip them per the Provocateur spec's "does not process isolates" rule.)
- `responds_to` links always resolve to an extraction in the same session, or are `null`. Cross-session `responds_to` is never produced.
- Cluster `cluster_id` values are unique within `clusters.json`; theme `theme_id` values are unique within `grouping.json`; both are stable across the single run but are NOT guaranteed stable across reruns with shuffled input.

These guarantees are enforced by the `_validate_clusters` and `_validate_themes` helpers in `flows/researcher_flow.py` and were verified on dev_msc_test (106 extractions, 25 clusters, 6 themes, 0 duplicates, 0 orphans, 0 hallucinated).
```

---

## Apply the delta

Apply this delta in a single edit session to `AI_Assembly_Researcher_Pipeline.md`. The changes are structural but non-destructive: all v2 content that is not explicitly replaced remains intact. Recommended order of application:

1. Add the v3 Changelog entry at the top of the Changelog section.
2. Replace the Overview paragraph per §A.
3. Update the Step 1 output schema ID field per §B.
4. Replace `## Step 2: Grouping` entirely per §C (the new text subsumes both §C Round 1/Round 2 structure and the §D/§E data handling rationale).
5. Update the Node 1 system prompt per §F (append ID format instructions) and the user prompt per §F (add `session_id:` line).
6. Delete the old Node 2 system prompt entirely and replace with the two new prompts (clustering + theming) per §G.
7. Update the Implementation Draft closing paragraph per §H (model recommendation + thinking).
8. Update Step 1 output example per §I (namespaced ID).
9. Update Step 2 output example per §I (namespaced IDs + new theme structure).
10. Add the Provocateur interface contract subsection at the end of Step 2 per §J.

The code in `flows/researcher_flow.py` and the three prompt files in `flows/shared/prompts/` already reflect v3. This delta only updates the spec doc to match the code that's already running.

---

## What this delta does NOT change

- **Step 1 Extraction section — the three lenses, granularity rules, substance-not-manner rule, uncertainty-from-upstream rule, verify_markers handling.** These are unchanged from v2. Node 1 extraction logic was not touched in v2.4.
- **Step 1 Output table — field definitions for Speaker, Lens, Extraction, Context, Engagement, Responds to, Energy.** Unchanged from v2. Only the ID field gets a new format (§B).
- **Scope section — what the Researcher does and doesn't do.** Unchanged. The Researcher is still unbiased, still does not know the council, still produces a faithful map.
- **Constraints section — time window, night 2 behavior, relationship to the Provocateur.** Unchanged.

---

*End of delta. Two files to update in project knowledge: `AI_Assembly_Researcher_Pipeline.md` per this delta, and `AI_Assembly_Transcription_Pipeline.md` per `TRANSCRIPTION_v2_to_v2_1_delta.md`. The Provocateur spec and the Briefing doc do not need changes — their descriptions of the Researcher are abstract enough that v2.4 still satisfies them.*
