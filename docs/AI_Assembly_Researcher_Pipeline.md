# THE RESEARCHER PIPELINE
## AI Assembly — Role Specification

**Project:** The AI Assembly · World Beautiful Business Forum · Athens · May 7–10, 2026
**Status:** Conceptual briefing — working draft (v3, post-dev_msc_test v2.4 validation)
**Purpose:** This document specifies the Researcher's function, process, and design constraints in enough detail that a technical team could build and prompt it.

---

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

---

## Changelog (v2 — Apr 14 2026)

This revision applies one surgical change from `PROPOSED_pipeline_doc_change.md`:

- **§12 Part B** → Node 1 (Extraction) system prompt and user prompt gain explicit handling for `review_queue.verify_markers` so that the Researcher degrades extraction confidence when the substance of an extraction hinges on a word the cleaning pass flagged as uncertain. The paired upstream fix (§11 — per-turn re-attribution of diarization-contaminated turns) lives in `AI_Assembly_Transcription_Pipeline.md`; together they close the "`review_queue` is orphaned" gap identified in Level 2 testing.

Model reference updated from "Claude Sonnet 4" to "Claude Sonnet 4.6" throughout. Everything else in this document is preserved verbatim from v1.

---

# Overview

The Researcher is the first agent in the overnight reasoning chain. It receives **session packages** from the Transcription Pipeline — each containing the program metadata (title, description, format, roster with bios), a clean, named transcript, and a review queue — and produces two things: an **extraction table** (atomic positions, reframings, and questions pulled from each session) and a **themed grouping** (those extractions clustered into themes by affinity). Together, these form a faithful, rigorous map of what the day's conversations contained. The output feeds the Provocateur, who formulates questions and assigns them to council members.

The Researcher is unbiased. It does not know the council's composition, the audience's profile, or the governance matrices used downstream. It captures what was discussed and flags which extractions carried high energy in the room — nothing more. It is a design research instrument, not an editorial voice.

Session packages arrive ready to consume — the Transcription Pipeline has already handled audio, diarization, speaker attribution, and cleaning. A human editorial decision upstream determines which sessions feed the experiment each night. Sessions may be keynotes (single speaker), panels (multiple speakers), workshops (participatory), or walking sessions; any of these may arrive as a primary recording or as a participant reflection.

The Researcher works in two steps:

1. **Extraction** — per session: pull assertions, reframings, and open questions from each transcript
2. **Grouping** — once: cluster all extractions into themes by affinity, in two sequential rounds

Step 2 is implemented as two separate API calls with an intermediate artifact. Round 1 (`cluster_extractions`) groups atomic extractions into clusters and writes `clusters.json`. Round 2 (`group_clusters_into_themes`) reads only the cluster-level metadata produced by Round 1 — titles and abstracts, no raw extractions — and groups those clusters into themes. A Python merge step reassembles the final `grouping.json` with the themes→clusters→extractions nesting. This two-call structure forces genuine second-level abstraction at Round 2: the model cannot re-group raw items, it can only reason about the Round 1 findings.

---

## Step 1: Extraction

**Input:** One session package from the Transcription Pipeline: metadata block (title, description, format, roster with bios), transcript (speakers_present, turns), and review queue (verify markers). Runs once per session.

**Relevance boundary.** The session title and description tell you what the conversation was intended to be about. Extract what the conversation actually produced, including where it departed from its intended subject. The roster bios are reference material for understanding who is speaking from what background — not a source of extractions in their own right.

**Granularity.** Extract assertions that constitute positions — claims that commit the speaker to something that a reasonable person could disagree with. Do not extract statements of fact that no one would contest, procedural remarks, or pleasantries.

**Substance, not manner.** The extraction is always a position, a redirection, or an unresolved question — what was asserted, where the discussion shifted, what remained open. Do not extract observations about group dynamics, tone, or process as findings in their own right. But do notice these as signals for the energy flag — if a position drew extended engagement or shifted the room's direction, that's high energy on the extraction, not a separate observation.

**Uncertainty from upstream.** The Transcription Pipeline flags two kinds of uncertainty that the Researcher must respect. First, per-turn **speaker confidence** — if the upstream pipeline was not fully confident which roster member said a given turn, the confidence level is recorded on that turn and the Researcher passes the flag through on any extraction attributed to that speaker. Second, per-turn **verify markers** — if the cleaning pass flagged specific words as uncertain (typically proper names, acronyms, or policy terms that the ASR could plausibly have misheard), those turns appear in `review_queue.verify_markers` with a back-reference to the turn index. When the substance of an extraction depends on one of those flagged words, the extraction itself is uncertain and must be marked so that a human editor can verify.

### Three Extraction Lenses

The Researcher looks for three things in each transcript through simultaneous lenses applied in a single reading. Every extraction is atomic: one position, redirection, or question per extraction, one to two sentences. The argument must be specific enough that someone who wasn't in the session can understand it.

**Assertions** — All positions taken. One extraction per position. Some assertions respond to other assertions — the Responds-to field tracks which. The Engagement field on the original tracks what happened to it: challenged, reinforced, or unengaged.

**Reframings** — Someone changed what the conversation was about — not a position within the discussion but a redirection of the discussion itself. Like assertions, reframings track Engagement: was the reframing picked up, built on, or ignored?

**Open questions** — What remained unresolved. Explicitly asked questions nobody answered AND tensions between assertions that the room didn't close, articulated as questions even if nobody literally asked them. Both are gaps the day produced but didn't fill.

### Energy

For each extraction, note whether it carried **high energy** in the transcript — extended engagement from multiple speakers, follow-up discussion, or a visible shift in the room's direction. The Researcher does not interpret why something had energy — it flags that it did.

### Step 1 Output

A structured table of extractions, one row per extraction, accumulating across all sessions:

| Column | Description |
|---|---|
| **ID** | Session-namespaced extraction identifier in the format `{session_id}:NNN` where session_id is the short identifier of the source session (e.g. `breaking_point`, `vox_populi`) and NNN is a zero-padded sequential integer starting at 001 within that session. Example: `breaking_point:014`. Per-session files and the combined `all_extractions.json` carry identical IDs — there is no renumbering. This allows parallel per-session extraction without collisions and makes the provenance of any extraction self-documenting from its ID alone. |
| **Session** | Session title |
| **Speaker** | Named individual who took the position, made the reframing, or asked the question. Pass through the speaker label from the transcript. If the speaker confidence from the upstream pipeline is medium or low, append the flag (e.g. `Jon Alexander [medium]`, `Unidentified Speaker 3 [low]`). For open questions that emerged from an exchange rather than from a single utterance, leave empty and note the source in Context. |
| **Lens** | assertion / reframing / open question |
| **Extraction** | The position, redirection, or question, stated crisply. One to two sentences. |
| **Context** | The evidence that accompanied the position — references, examples, case studies, stories. For open questions and reframings: what prompted it. May be empty. If the extraction's substance hinges on a word flagged as uncertain in `review_queue.verify_markers`, append `[word uncertain in source]` to the Context. |
| **Engagement** | Challenged / Reinforced / Unengaged. Assertions and reframings only. |
| **Responds to** | ID of the assertion this responds to, if applicable. Assertions only. |
| **Energy** | High / Normal. |

*Examples (using namespaced IDs from the v2.4 canonical format):*

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

| | **opening_assembly:002** |
|---|---|
| **Speaker** | Roger Berkowitz |
| **Lens** | assertion |
| **Extraction** | Calling democracy a "design challenge" smuggles in the assumption that it can be engineered — but democratic life is a practice, not a product. |
| **Context** | Grounded in Arendt's distinction between making and acting. |
| **Engagement** | reinforced |
| **Responds to** | opening_assembly:001 |
| **Energy** | high |

| | **opening_assembly:003** |
|---|---|
| **Speaker** | Nicole Miller |
| **Lens** | assertion |
| **Extraction** | Nature already governs through feedback loops — what we call governance is just the human version of something biomimicry shows us is universal. |
| **Context** | Cited mycorrhizal networks redistributing nutrients between trees as a governance model. |
| **Engagement** | unengaged |
| **Responds to** | null |
| **Energy** | normal |

| | **opening_assembly:004** |
|---|---|
| **Speaker** | Payal Arora |
| **Lens** | reframing |
| **Extraction** | The question is not whether AI should have a seat at the table — the question is whether the table is the right metaphor at all. |
| **Context** | — |
| **Engagement** | unengaged |
| **Responds to** | null |
| **Energy** | normal |

| | **opening_assembly:005** |
|---|---|
| **Speaker** | null |
| **Lens** | open_question |
| **Extraction** | If citizens' assemblies work because participants are randomly selected and have no agenda — what happens when one of the participants is an algorithm that was built with an agenda? |
| **Context** | Arose in exchange between the deliberative democracy and AI inclusion panelists after discussing AI as proxy representative. |
| **Engagement** | null |
| **Responds to** | null |
| **Energy** | normal |

---

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

### Why Round 1 sees a minimal input — design rationale

The v2.3 iteration of this pipeline (Opus 4.6 + adaptive thinking, same prompts, full extraction records as input) produced clusters averaging 2.08 extractions and a cross-session theme ratio of only 25%. Diagnostic work identified two root causes:

**The namespace prefix was acting as a grouping shortcut.** With extractions labeled `breaking_point:014`, `vox_populi:007`, etc., the model could reason "items with the same prefix come from the same conversation and are likely to cluster together". This is correct at a structural level — within-session extractions do have tighter argumentative connections via `responds_to` edges and shared moderator framing — but it produces session-local clusters where the spec wants content-based affinity that spans sessions.

**The `responds_to` field was a within-session attractor.** Every `responds_to` edge is by definition a within-session link. The model reading the input saw these edges as "these two items are clearly related" and formed clusters around them, reinforcing the session-local bias.

The v2.4 fix is data-level: strip both signals at the API boundary. Round 1 sees only `{ref, extraction, context}`. All other fields — including the namespace-bearing real ID and the `responds_to` links — are withheld from the model and re-joined by the orchestration code after the call returns. This is stricter than prompt-level exhortation ("don't let session structure organize the clustering") because the structural attractors are simply invisible.

**The `ref` field is temporary and call-scoped.** It is assigned sequentially at call time, translated back to real namespaced IDs via a Python lookup table after the call, and never persists to disk. The orchestration code handles all of this transparently; the downstream artifacts (`clusters.json`, `grouping.json`) carry full namespaced IDs exactly as before.

**This design does not affect Round 2.** Round 2 already sees only cluster-level metadata by the spec's canonical requirement.

### Step 2 Output

A nested reference layer on top of the Step 1 extraction table:

```
Theme: "working title"
  Abstract: "why these clusters belong together"
  ├── Cluster A: "working title" — "why these extractions belong together" [session_id:001, session_id:003]
  ├── Cluster B: "working title" — "why these extractions belong together" [session_id:004, session_id:008]
  └── Cluster C: "working title" — "why these extractions belong together" [session_id:005, session_id:012]
```

Each theme contains:

| Field | Description |
|---|---|
| **Theme ID** | Unique theme identifier (e.g. theme_001) |
| **Title** | Working label for the theme |
| **Abstract** | One to three sentences — why these clusters belong together |
| **Clusters** | List of clusters, each with its own title, abstract, and extraction IDs |

Plus: a list of **isolate** extraction IDs.

*Example (from the dev_msc_test v2.4 canonical run):*

```
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

This output — the extraction table plus the themed grouping — is the Researcher's complete deliverable. It feeds the Provocateur Pipeline.

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

---

# Constraints

**Time window.** The Researcher runs first in the overnight pipeline. It must complete fast enough that the Provocateur, the council, and all downstream processing can finish before breakfast.

**Unbiased.** The Researcher does not know the council's composition, the audience's profile, or the governance matrices. It captures what the day's conversations contained, faithfully and without strategic shaping.

**Night 2.** On Night 2, the Researcher processes Day 2's session transcripts. It does not receive Night 1's output — it works fresh on the new material. Night 1 awareness belongs to the Provocateur.

---

# Scope

The Researcher does not choose which sessions to process — that's a human editorial decision upstream. It does not formulate questions or propositions — that's the Provocateur. It does not know or care who will respond to the material — it captures what was discussed.

The Researcher's sole function is to turn a messy day of human conversation into a rigorous, structured set of themes ready for downstream use.

---

# Implementation Draft

Prompt instructions for each node. Step 1 (`extract_session`) runs in a per-session loop. Step 2 runs as two sequential API calls (`cluster_extractions` then `group_clusters_into_themes`) plus a Python merge step. See the model and thinking configuration note at the end of this section for the canonical model assignments.

---

### Node 1: Extraction (loop — once per session)

**System prompt:**

You are extracting positions, reframings, and open questions from a conference session transcript.

The session title and description tell you what the conversation was intended to be about. Extract what the conversation actually produced, including where it departed from its intended subject.

The roster gives you each speaker's background and affiliation. Use it to understand where a position is coming from — but do not extract bios as findings, and do not infer positions speakers might hold based on their bios. Only extract what was actually said in the transcript.

Only extract positions that commit the speaker to something a reasonable person could disagree with. Do not extract uncontested facts, procedural remarks, or pleasantries.

Do not extract observations about group dynamics, tone, or process as findings. But notice these as signals for the energy flag — if a position drew extended engagement or shifted the room's direction, flag it as high energy.

One position, redirection, or question per extraction. One to two sentences. Apply three lenses simultaneously:

ASSERTIONS — All positions taken. One extraction per position. Some assertions respond to other assertions — use the responds_to field to track which. Use the engagement field on the original to track what happened to it: challenged, reinforced, or unengaged.

REFRAMINGS — Someone changed what the conversation was about — not a position within the discussion but a redirection of the discussion itself. Track engagement: was the reframing picked up, built on, or ignored?

OPEN QUESTIONS — What remained unresolved. Explicitly asked questions nobody answered AND tensions between assertions that the room didn't close, articulated as questions even if nobody literally asked them. Both are gaps.

For each extraction, provide:
- The speaker who took the position, made the reframing, or asked the question — pass through the named speaker label from the transcript exactly. If the transcript marks the speaker confidence as medium or low, append it as a flag (e.g. "Jon Alexander [medium]"). For open questions that emerged from an exchange between multiple speakers rather than from a single utterance, leave speaker as null and explain the source in context.
- A paraphrase of what was said, specific enough that someone who wasn't in the session can understand the argument (one to two sentences)
- The evidence that accompanied the position — references, examples, case studies, stories. For open questions and reframings: what prompted it. (May be empty.)
- The lens (assertion / reframing / open question)
- For assertions and reframings: engagement (challenged / reinforced / unengaged), and for assertions: what it responds to if applicable
- Energy: high if the transcript shows extended engagement, multiple speakers responding, or a visible shift in direction. Normal otherwise.

UNCERTAIN WORDS FROM UPSTREAM CLEANING. The session package includes a `review_queue.verify_markers` field listing turn indices where the cleaning pass flagged words as uncertain — commonly proper names, acronyms, or policy-specific terms that the ASR could plausibly have misheard. A `[verify]` marker appears inline in the turn text at the uncertain word. When you are extracting an assertion, reframing, or open question whose substance hinges on a `[verify]`-tagged word — for example, the extraction is centrally about that specific entity, person, or policy term — append `[word uncertain in source]` to the Context field so a human editor can verify before downstream use. When the extraction's substance does not depend on the uncertain word (e.g., the uncertainty is in an incidental aside, or the argument stands regardless of which specific name was used), extract normally and ignore the marker. The goal is faithful coverage: don't silently drop extractions because a tangential word is uncertain, and don't silently propagate extractions whose core claim depends on a word the pipeline couldn't verify.

Return as JSON array. Each object must have: id, session, speaker (null if synthesized from an exchange), lens, extraction, context, engagement (null for open questions), responds_to (null if not a response to another assertion), energy.

The `id` field must be a string in the format `{session_id}:NNN` where:
- `{session_id}` is the session_id value provided in the user message header below — NOT the session title, the short identifier like `vox_populi` or `breaking_point`
- `NNN` is a zero-padded three-digit integer starting at `001` for the first extraction from this session and incrementing sequentially

So if the user message says `session_id: vox_populi`, your first extraction's id is `"vox_populi:001"`, your second is `"vox_populi:002"`, and so on.

When an extraction's `responds_to` field references a prior extraction from the same session, use the full prefixed id (e.g. `"vox_populi:001"`). Both `id` and `responds_to` must always be strings, never integers. You will only ever see extractions from one session at a time, so `responds_to` can only reference another extraction from this same session.

**User prompt:**

session_id: {{session_id}}
Session: {{session_title}}
Description: {{session_description}}
Format: {{session_format}}

Roster (scheduled contributors with bios):
{{for each contributor in roster: name, title, affiliation, bio}}

Speakers present (who actually spoke):
{{speakers_present}}

Transcript (each turn has turn_index, speaker, role, confidence, text — confidence reflects how certain the upstream pipeline was about the speaker attribution; treat low-confidence speaker labels with appropriate caution):
{{turns}}

Review queue — turns containing words the cleaning pass flagged as uncertain (proper names, acronyms, policy terms). Each entry references a turn by its turn_index. When an extraction's substance hinges on one of these flagged words, mark the extraction's context with "[word uncertain in source]":
{{review_queue.verify_markers}}

---

### Node 2a: Clustering (Claude Opus 4.6 — once, after all sessions extracted)

**Loaded from:** `flows/shared/prompts/researcher_clustering.md`

**Runtime config:** `model="claude-opus-4-6"`, `thinking.type=adaptive`, `max_tokens=40000`, **streaming required**.

**System prompt:**

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

**User prompt:**

{{shuffled_minimal_extraction_array_as_json}}

---

### Node 2b: Theming (Claude Opus 4.6 — once, after clustering)

**Loaded from:** `flows/shared/prompts/researcher_theming.md`

**Runtime config:** `model="claude-opus-4-6"`, `thinking.type=adaptive`, `max_tokens=24000`, **streaming required**.

**System prompt:**

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

**User prompt:**

{{shuffled_cluster_metadata_array_as_json}}

---

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
