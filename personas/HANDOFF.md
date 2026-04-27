# Persona Card Handoff to Runtime

This document describes how the runtime ai-assembly repo should consume the
Persona Cards produced by this pipeline.

## What the runtime gets per voice

A flat JSON file at `<PROJECT_ROOT>/voices/<slug>/07_persona_card_assembled.json` containing:

- 4 identity fields at root: `voice_name`, `voice_mode`, `pipeline_version`
  (currently `"4.0"`; pre-2026-04-27 cards carry `"3.10"`), `generated_date`
- 35 card fields at root (all v2-spec fields, flat)
- 2 null continuity fields: `continuity_block_if_night_2`,
  `continuity_block_artifact_if_night_2` (populated by Voice Pipeline at
  runtime if the voice carries something forward into Night 2)
- 1 `reference_only_passages` field (Step-1-only / copyright-sensitive
  tier; carries `runtime_contract_note` inline)
- 1 `metadata` block with provenance, validation status, and field role
  clarifications


## Derive artifacts per voice (written to `voices/<slug>/06_derive/`)

After Derive runs, the pipeline writes four files under `06_derive/`:

| File | Consumer | Purpose |
|---|---|---|
| `00_derive_raw.json` | pipeline internal | Raw Derive call output (provocateur_profile + evaluation_rubric combined). Kept for cache/resumability; not consumed downstream. |
| `01_provocateur_profile.json` | Provocateur Pipeline | 8-field profile (`speaks_from`, `core_commitment`, `activates_on`, `goes_flat_on`, `stretch`, `translation_range`, `stance_tendency`, `medium`). Wires into `runtime/flows/shared/council/council_config.json` under `members[]`. |
| `02_evaluation_rubric.json` | Voice Pipeline testing harness | 9 test prompts (3 identity + 3 reasoning + 3 stress) for ongoing voice-quality monitoring. |
| `03_chat_system_prompt.json` | Claude project custom instructions (operator paste-target) | FU#41 2026-04-24, amended 2x. Chat-ready persona-card JSON. Mechanical strip of assembled card — drops **11 items** (5 chat-incompatible: `metadata`, `smoke_test_chains`, `reference_only_passages`, 2 continuity blocks; 5 spec-shell meta: `voice_name`, `voice_mode`, `pipeline_version`, `generated_date`, `council_member_name`; 1 nested: `curated_corpus_passages.corpus_metadata`). Produced by `personas/flows/shared/chat_prompt_builder.py`. NOT consumed by Provocateur Pipeline or Voice Pipeline — standalone artifact for chat-test validation + Claude-project deployments. Coexists with `01_provocateur_profile.json`; they target different runtime channels. |

## Two consumers, two roles

The runtime ai-assembly repo has (or will have) two pipelines that consume
these cards:

### 1. Provocateur Pipeline → reads the Provocateur Profile only

The Provocateur derives an 8-field profile from the assembled card via
Phase 4 (Derive). That profile goes into `flows/shared/council/council_config.json`
under `members[]` and is what the Provocateur actually reads for Selection
and Formulation. The full persona card is not loaded into the Provocateur.

### 2. Voice Pipeline → loads the persona card as system prompt

The Voice Pipeline uses the assembled card directly as the system prompt
for the voice's runtime LLM call. All 35 card fields together ARE the
voice's instructions.

### 3. Chat deployments (operator) → paste `03_chat_system_prompt.json`

Out-of-band from the runtime pipelines. Operator pastes the chat artifact
into Claude project custom instructions (or a Claude API system prompt for
an agentic-chat deployment). Used for chat-test validation of voice quality
pre-ship and for chat-native deployments that bypass the Voice Pipeline's
two-step Private-Reasoning / Public-Expression protocol.

## CRITICAL: `reference_only_passages` is Step 1 only — NEVER Step 2

The assembled card may contain a `reference_only_passages` field (Phase B
two-tier corpus). This is populated for voices whose primary corpus is
copyright-sensitive — musical voices like Marley, possibly Dostoevsky
under a specific modern translation.

**Runtime contract** (Voice Pipeline MUST enforce):

- **Step 1 (Private Reasoning)** loads `reference_only_passages` into the
  system prompt alongside the public `curated_corpus_passages`. The voice
  reasons from its actual words.
- **Step 2 (Public Expression)** DROPS the field before assembling the
  system prompt. The artifact the audience reads must not contain direct
  quotation of the copyrighted material. Paraphrase that's identifiably
  sourced also counts as a violation.

The runtime's Voice Pipeline Step 2 system-prompt assembly code MUST
filter out `reference_only_passages` before rendering. Failing to do so is
a copyright-exposure bug, not a quality bug.

The `runtime_contract_note` field inside `reference_only_passages` carries
this warning inline so any consumer reading the JSON sees it without
reference to this document.

If lift-phrases from `reference_only_passages` appear in Step 2 output
during testing, that's a persona-card failure mode — add the lift-phrase
to `banned_language` via Pass 7c.

## CRITICAL: do NOT few-shot from `smoke_test_chains`

The `smoke_test_chains` field in the assembled card looks like a natural
candidate for few-shot exemplars in the Voice Pipeline's Step 1 prompt.
**It is not.**

`smoke_test_chains` is a build-time diagnostic, not a runtime contract:

- Generated by Pass 7b (Opus + adaptive thinking) reading the assembled
  card and producing 4 example chains
- Read by Pass 7c to surface failure patterns and tighten `banned_language`
  and `banned_modes`
- Saved into the card as a pre-runtime artifact so human reviewers can see
  the card act before approving it


If the Voice Pipeline few-shots from `smoke_test_chains`:

- Every Plato response will be shaped by 4 specific provocation patterns
  from a build-time test that has nothing to do with the actual conference
  question being answered
- The voice's range collapses toward whatever the test set happened to
  cover (translation through boundary, bold engagement, topics-requiring-
  care, general — but the runtime question may be none of those)
- Failure patterns Pass 7c was supposed to remove get re-introduced if
  the test provocations themselves contained those patterns
- The provocations get stale immediately — they were generated against
  the deployment context as it stood at build time, not the actual
  morning's session content

The persona card is the contract. Trust it. The 35 fields — constitution,
reasoning_method, characteristic_moves, concept_lexicon, banned_language,
banned_modes, etc. — are what tells the model how to behave. Few-shot
examples are a hack used when system prompts aren't strong enough; a
properly built v3.10 card doesn't need them.

## What to do with `smoke_test_chains` in the runtime

Leave them in the JSON for inspection. Do not load them into any prompt.
They serve the same function as a unit test: they prove the card was
working at the moment it was built. They are evidence, not exemplars.

## Metadata block contents

The `metadata` block in each assembled card contains:

- `passes_completed` — the actual pipeline steps that ran for this voice
- `validation_status` — Pass 7a's overall verdict (PASS or REVISION_NEEDED)
- `fix_pass_log` — FU#13 linear-patcher log if Pass 7a-FIX fired (replaces v3.10's `revision_loops` counter; the linear-patcher architecture supersedes the revision-loop architecture, ~$1 vs ~$5–10 per loop)
- `tools_used` — which models/APIs touched this card
- `voice_basis` — `corpus-based` or `training-data` (set by Pass 4a depending
  on whether Node 1c found primary texts)
- `hostile_sources`, `corpus_constraint`, `subtype` — input-derived flags
  that affect how downstream consumers should interpret the card
- `deployment_context` — the conference_context used to generate Pass 7b
  (re-run Pass 7b alone if redeploying to a different context)
- `human_review_status` — `pending` until a human signs off
- `approach_c` — true if a Claude Deep Research dossier was used in Pass 1a
- `citation_verification`, `cross_model_validation`,
  `negative_constraints_refinement` — Phase 3 results
- `smoke_test_chains_role` — the explicit "do not few-shot" notice
- `field_counts`, `register_violations` — diagnostic extras
