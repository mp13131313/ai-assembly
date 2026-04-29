# Voice Pipeline — Implementation

The Voice Pipeline is the runtime component that runs each persona at
Athens. It loads a completed Persona Card (v2 schema, produced by the
Persona Pipeline v4) and produces three artifacts per voice per night:
detailed responses (Step 1), a first-draft artifact (Step 2), and an
amended artifact (Step 3).

**Status:** Implemented v2 (2026-04-28). Not yet dry-run end-to-end.

**Spec:** [`docs/AI_Assembly_Voice_Pipeline.md`](../../../docs/AI_Assembly_Voice_Pipeline.md) — runtime contract end-to-end. Read the spec before reading code; the spec carries the design rationale.

**Predecessor build notes:** the original "build notes" version of this
README (planning decisions, before the implementation landed) is preserved
in git history at commit `9b57bb7^`. The two load-bearing decisions it
captured (do not few-shot from `smoke_test_chains`; the persona card is
the system prompt) are now codified in the spec and enforced by
`card_assembly.py`.

---

## File layout

```
runtime/flows/voice/
├── __init__.py
├── README.md                       (this file)
├── _anthropic_call.py              shared streaming helper + 1-retry-on-failure;
│                                   used by step1/2/3/continuity to call Anthropic
│                                   API consistently. Extracts text + thinking
│                                   blocks from final.content (matches researcher_flow
│                                   pattern). Underscore prefix = internal to subpackage.
├── card_assembly.py                load_persona_card() + assemble_system_prompt(card,
│                                   step, night). The architectural core: applies the
│                                   field-routing matrix per spec §"Card → System Prompt
│                                   Assembly", enforces the 4 strip rules (metadata,
│                                   smoke_test_chains, reference_only_passages Step 2+3,
│                                   curated_corpus_passages.corpus_metadata nested),
│                                   unwraps voice_temporal_stance to the deployment-
│                                   appropriate text. Plus filter_theme_record_for_step1()
│                                   and filter_first_draft_for_step3() for stripping
│                                   pipeline-meta from upstream JSON before showing voice.
├── step1_private_reasoning.py      Step 1 task. One LLM call per (voice, formulation)
│                                   pair. Opus 4.7 + adaptive thinking, max 64K, streamed.
│                                   Output: 04_voice/step1_detailed_responses/<slug>__<theme_id>.json
├── step1_validation.py             Optional anachronism + constitutional checks via
│                                   OpenAI ladder (gpt-5.4 high → gpt-4.1 → o3 → gpt-4o
│                                   → gemini-2.5-pro fallback). Cross-model validation
│                                   pattern matching Persona Pipeline Pass 7-anachronism.
├── step2_first_draft_artifact.py   Step 2 task. One LLM call per voice. Voice reads
│                                   back its Step 1 outputs, makes focus/stance/form
│                                   decisions, produces the artifact text. Opus 4.7 +
│                                   adaptive thinking, max 64K, streamed.
├── step3_amended_artifact.py       Step 3 task. FU#49E cross-framework reading. Voice
│                                   reads other voices' first-drafts on shared themes,
│                                   decides amend (extend / mark-limit / sharpen-
│                                   disagreement) or stand-pat. Runs after ALL voices'
│                                   Step 2 complete. Opus 4.7 + adaptive thinking, max 64K.
└── continuity.py                   Continuity block generation. Per-voice Sonnet 4.6
                                    summariser writes voice-grammar memory of prior
                                    night, output to PROJECT_ROOT/voices/<slug>/
                                    continuity_night_<N+1>.json. Runs inline in
                                    voice_flow.py orchestrator after Step 3 completes
                                    (Nights 1+2 only; output consumed on Nights 2+3).

runtime/flows/voice_flow.py         Prefect orchestrator. CLI entry point.
                                    Wires Step 1 → optional validation → Step 2 →
                                    Step 3 → continuity. Parallelism per spec
                                    (VOICE_STEP1_BATCH=4, 20s wait between batches).
                                    Writes per-night roll-ups (responded_to_graph,
                                    themes_to_voices, manifest).

runtime/flows/shared/prompts/voice_*.md (6 files)
                                    Closing instructions + validation system prompts.
                                    Lifted verbatim from spec §"Step N — ..." XML-tagged
                                    blocks. Do NOT edit these as text; they were
                                    carefully engineered.
```

---

## Running it

```bash
cd runtime
python flows/voice_flow.py <run_dir> --night N \
    [--skip-validation]      # skip OpenAI cross-model validation
    [--skip-step3]           # DEV USE ONLY — Step 3 is load-bearing for Athens
    [--skip-continuity]      # skip continuity-block generation
    [--project PATH]         # PROJECT_ROOT override (or set $AI_ASSEMBLY_PROJECT_ROOT)
    [--voices SLUG[,SLUG...]]  # filter to subset of voices
```

`<run_dir>` must contain `03_provocateur/briefings/*.json` (Provocateur
Pipeline output).

PROJECT_ROOT must contain `voices/<slug>/07_persona_card_assembled.json`
for each voice.

### Environment variables

| Variable | Default | Notes |
|---|---|---|
| `VOICE_MODEL` | `claude-opus-4-7` | Override for dev iteration; per-card override possible via `voice_config.runtime_model` |
| `VOICE_THINKING` | `1` | Set to `0` to disable adaptive thinking (dev only — production uses thinking) |
| `VOICE_STEP1_MAX_TOKENS` | `64000` | Same for STEP2 / STEP3 |
| `VOICE_STEP1_BATCH` | `4` | Parallel concurrency for Step 1 calls |
| `VOICE_BATCH_WAIT_S` | `20` | Wait between Step 1 batches (Anthropic rate limits) |
| `VOICE_VALIDATION_MODELS` | `gpt-5.4,gpt-4.1,o3,gpt-4o,gemini-2.5-pro` | OpenAI ladder |
| `VOICE_VALIDATION_MAX_TOKENS` | `8192` | |
| `VOICE_CONTINUITY_MODEL` | `claude-sonnet-4-6` | Compression task; doesn't need Opus |
| `VOICE_CONTINUITY_THINKING` | `1` | Adaptive thinking on so the summariser holds the voice's grammar + temporal stance from the inputs |
| `VOICE_CONTINUITY_MAX_TOKENS` | `8000` | |

### Outputs

Per the spec's §"Outputs" tree, under `<run_dir>/04_voice/`:

```
04_voice/
├── step1_detailed_responses/<slug>__<theme_id>.json   one per (voice, formulation)
├── validation/<slug>__<theme_id>.json                 if validation ran
├── step2_first_draft_artifacts/<slug>.json            one per voice
├── step3_amended_artifacts/<slug>.json                one per voice
├── responded_to_graph_night_N.json                    directed amendment graph
├── themes_to_voices_night_N.json                      reverse index per theme
├── step3_complete.flag                                sentinel (audit only)
└── manifest.json                                      run-level metadata + cost
```

Continuity overrides (Nights 2+) live OUTSIDE the run dir, under
`<PROJECT_ROOT>/voices/<slug>/continuity_night_N.json` — they're part of
the persona card, not the run.

---

## Design notes (load-bearing decisions, preserved from build phase)

### `smoke_test_chains` is NEVER few-shot at runtime

The persona card has a `smoke_test_chains` field (3-5 example
provocation→response chains generated by Persona Pipeline Pass 7b). It
looks like a natural candidate for few-shot exemplars. **It is not.**

This is enforced architecturally — `card_assembly.assemble_system_prompt`
strips `smoke_test_chains` along with `metadata` before rendering. It's
one of the four load-bearing strip rules.

Failure modes if you ignore this (per `personas/HANDOFF.md`):
- Voice's range collapses toward whatever 4 patterns happened to be in
  the test set
- Failure patterns Pass 7c worked to remove get re-introduced
- Provocations are stale (built against old `conference_context`)
- Examples constrain a system prompt that is already strong enough

The chains live in the JSON for human inspection. Look at them. Don't
load them into a prompt.

### `reference_only_passages` is Step 1 only

Per the cross-repo runtime contract (`personas/HANDOFF.md` §"CRITICAL:
`reference_only_passages` is Step 1 only — NEVER Step 2 or Step 3"):

- **Step 1** loads the field for grounding (voice reasons from its actual
  words — Marley's lyrics, Dostoevsky under specific translation, etc.)
- **Step 2 and Step 3** drop it before assembling system prompt. The
  artifacts the audience reads must not contain copyrighted material.

Enforced architecturally in `card_assembly.assemble_system_prompt`:

```python
if step in (2, 3):
    filtered.pop("reference_only_passages", None)
```

### Pipeline-meta does not leak into voice prompts

The voice doesn't know it's in a pipeline. The card's foundational
commitment ("the voice IS the voice") is enforced through:

1. Card-side: `epistemic_frame_statement` is operational, not declarative
   (see Persona Card v2 spec).
2. Closing-instruction-side: spec §"Step N — ..." closing instructions
   are stripped of every reference to "Provocateur", "Assembly",
   "Layer 1/2/3", "micro-site", "breakfast", "750", FU# follow-up tags,
   "Position B" naming, etc. The voice receives directives in its own
   grammar.
3. User-prompt-side: `card_assembly.filter_theme_record_for_step1()`
   strips theme_flags / co_assigned_voices / pipeline-named fields from
   the briefing's `full_theme_record` before showing voice. Step 3 does
   the same with `filter_first_draft_for_step3()`.

If you add new fields to upstream pipelines (Provocateur briefing, Step
output schemas) that contain pipeline-meta, you must add filter
discipline before the voice sees them.

---

## See also

- [`docs/AI_Assembly_Voice_Pipeline.md`](../../../docs/AI_Assembly_Voice_Pipeline.md) — the spec
- [`docs/AI_Assembly_Briefing_v3_1.md`](../../../docs/AI_Assembly_Briefing_v3_1.md) — project source of truth
- [`docs/AI_Assembly_Persona_Card_v2.md`](../../../docs/AI_Assembly_Persona_Card_v2.md) — card schema (with v2.1 amendments)
- [`docs/AI_Assembly_Frame_Concept_v1.md`](../../../docs/AI_Assembly_Frame_Concept_v1.md) — frame layer (Edition Pipeline downstream of Step 3, not Voice Pipeline scope)
- [`personas/HANDOFF.md`](../../../personas/HANDOFF.md) — cross-repo runtime contract
- [`docs/CURRENT_STATE.md`](../../../docs/CURRENT_STATE.md) — gap analysis + critical path
