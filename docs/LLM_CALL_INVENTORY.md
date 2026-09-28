# LLM Call Inventory

**Purpose:** Complete enumeration of every model API call made from this repo, with provider, model, parameters, prompt source, and (since the 2026-09-28 model-config refactor) the `model_routing.json` step key that resolves the call's model/thinking/effort. Written against the actual code (not against the spec docs, which drift) — accuracy per call site is the point; treat prose as secondary.

**Scope:** All LLM / AI API calls initiated by code in this repo — runtime flows (transcription, researcher, provocateur, voice, editor) and the persona pipeline. External-facing manual steps (the human Claude DR sessions at claude.ai) are noted for completeness but are not code-initiated. Ad-hoc dev/QC scripts that fire live calls when run manually are catalogued separately in §9 so they don't get confused with the automated per-night / per-voice pipelines.

**Regenerated: 2026-09-28, from code on branch `phase0-fixes` (after the model-config refactor, `f5de9db`).** Since the 2026-09-27 edition, every LLM call site in both pipelines was refactored (`f818767` personas, `8fb718d` runtime, `f5de9db` validator-ladder vendor routing) to resolve its model/thinking/effort from the new root-level `model_routing.json`, via `flows/shared/model_routing.py` (byte-identical copy in `runtime/` and `personas/`) — this moved most call-site line numbers and changed several call signatures (`call_claude(step=...)`, `stream_voice_call(cfg=...)`, the new `call_validator_ladder`). `model_routing.json` is now the single source of truth for which model/thinking/effort each step uses; this doc's job is to say *where* each step is called and *what it actually sends*, not to restate the file's contents — check `model_routing.json` itself for current defaults.

---

## 0. Providers and models at a glance

**Source of truth for "which model runs which step" is `model_routing.json` (repo root) — this table is a snapshot of its `models` block plus what's actually wired up today. Do not hand-edit a model name in code; edit the JSON (loader rejects any model not listed in its `models` block).**

| Provider | SDK (runtime venv / personas venv) | Models listed in `model_routing.json` | Where |
|---|---|---|---|
| Anthropic | `anthropic==0.94.1` (both) | `claude-opus-4-7` (`sampling_params:false, thinking_can_disable:true, default_effort:high`), `claude-sonnet-4-6` (`sampling_params:true, thinking_can_disable:true, default_effort:high`), `claude-opus-5-5` (`sampling_params:false, thinking_can_disable:false, default_effort:medium` — listed, not currently the default for any step), `claude-sonnet-5` (`sampling_params:false, thinking_can_disable:true, default_effort:high` — listed, not currently default) | Everywhere Claude is called (Transcription, Researcher, Provocateur, Voice, Editor, Personas) |
| AssemblyAI | `assemblyai==0.59.0` (runtime) | `universal-3-pro` (now itself a `model_routing.json` step, `runtime.transcription.asr`) | Transcription ASR + diarization |
| Perplexity | Raw HTTP via `requests` (personas) | `sonar-deep-research` | Persona Pass 1a |
| Google Gemini | `google-genai==1.73.1` (runtime) / `google-genai==1.47.0` (personas — **version drift between the two venvs, pre-existing, not part of this refactor**) | `gemini-2.5-pro` | Persona Pass 1b, validator-ladder last resort (personas 7-anach/7a/7a-FINAL and runtime Voice Step 1 validation), 7c primary |
| OpenAI | `openai==2.31.0` (both venvs; not pinned in `personas/requirements.txt` but installed) | `gpt-5.4`, `gpt-4.1`, `o3`, `gpt-4o` | Persona Pass 7-anachronism / 7a / 7a-FINAL (5-rung ladder); Voice Step 1 validation (separately-implemented copy of the same ladder) | 
| Wikipedia | REST (`requests`) | — | Persona Pass 0a (not LLM; grounding lookup) |

Anthropic dominates call volume. Per the commit messages, the refactor touched **17 runtime steps** and **33 persona call sites** — every one of them now resolves via `step_config(<key>)` or `call_claude(step=<key>)` except the two exempt dev/QC scripts in §9.

**Every Anthropic call site in the repo, no exceptions found (re-verified this pass):** no `tool_choice` (forced or otherwise), no `top_p`/`top_k`, no `budget_tokens` actually sent, and no assistant-turn prefill for generation (the `role: assistant` messages that exist — `runtime/flows/voice/_anthropic_call.py:52-55` and `personas/flows/shared/clients.py:41-44` — are payloads to the free `messages.count_tokens` endpoint for thinking-token telemetry, not prefill on a generation call).

---

## 1. Summary tables — one row per call site

Model/thinking/effort columns below are **snapshots of the current `model_routing.json` defaults** (with the loader's legacy env-var overrides noted where one exists — see §5). If this table and the JSON ever disagree, the JSON wins; re-run `python -c "from flows.shared.model_routing import all_steps; ..."` or just read the file.

### 1.1 Runtime pipelines

N = expected invocations per Athens-scale night (rough; panel is currently 10 voices per `_workspace/planning/FOLLOW_UPS.md`, ~15-25 sessions/night, ~15-25 themes/night on the researcher side).

| # | Pipeline · Call site | file:function(line) | `model_routing.json` step | Model (current default; legacy env still overrides) | Streaming | Thinking | Temp actually sent | Structured output |
|---|---|---|---|---|---|---|---|---|
| R1 | Transcription · ASR | `transcription_flow.py:397 transcribe_with_assemblyai` → `step_config(...).model` at `:420` | `runtime.transcription.asr` | `universal-3-pro` | poll | — | — | — |
| R2 | Transcription · Speaker ID (5-pass) | `transcription_flow.py:464 identify_speakers` → `step_config` `:500` → call `:520-533` | `runtime.transcription.speaker_id` | `claude-sonnet-4-6`, thinking off | No (`messages.create`) | Off (config; intentional, §7) | **not sent** (no key in request) | JSON-in-text, `extract_json` |
| R3 | Transcription · Cleaning | `transcription_flow.py:546 clean_transcript` → `step_config` `:560` → stream `:581-594` | `runtime.transcription.cleaning` | `claude-sonnet-4-6`, thinking off | Yes (required, 64K) | Off (config) | **not sent** | plain text |
| R4 | Researcher · Extraction | `researcher_flow.py:266 extract_session` → `step_config` `:271` → stream `:303-310` | `runtime.researcher.extraction` | `claude-opus-4-7`, thinking adaptive | Yes | Adaptive (config; legacy `RESEARCHER_THINKING`) | **not sent** (docstring at `_thinking_kwargs`, `:121-124`, still explains why: Opus 4.7 400s if temperature is set on a thinking call) | JSON-in-text |
| R5 | Researcher · Clustering | `researcher_flow.py:343 cluster_extractions` → `step_config` `:365` → stream `:403-410` | `runtime.researcher.clustering` | same | Yes | Adaptive | not sent | JSON-in-text |
| R6 | Researcher · Theming | `researcher_flow.py:474 group_clusters_into_themes` → `step_config` `:485` → stream `:522-529` | `runtime.researcher.theming` | same | Yes | Adaptive | not sent | JSON-in-text |
| R7 | Provocateur · Triage Voice (per-voice) | `provocateur_flow.py:501 triage_voice` → shared helper `_stream_and_parse` (`:349-465`, stream at `:405-412`) | `runtime.provocateur.triage_voice` | `claude-opus-4-7`, thinking adaptive | Yes | Adaptive (legacy `PROVOCATEUR_THINKING`) | not sent | JSON-in-text |
| R8 | Provocateur · Triage Flags | `provocateur_flow.py:578 triage_flags` → same shared helper | `runtime.provocateur.triage_flags` | same | Yes | Adaptive | not sent | JSON-in-text |
| R9 | Provocateur · Formulation (per-pair) | `provocateur_flow.py:1081 formulate_for_member` → same shared helper, `cfg` at `:1147` | `runtime.provocateur.formulation` | same | Yes | Adaptive | not sent | JSON-in-text |
| V1 | Voice · Step 1 Private Reasoning (per voice×formulation pair) | `voice/step1_private_reasoning.py:118 run_step1_for_pair` → `step_config` `:147` → `stream_voice_call` `:157-164` | `runtime.voice.step1` | `claude-opus-4-7`, thinking adaptive | Yes | Adaptive, `display:"summarized"` (legacy `VOICE_MODEL`/`VOICE_THINKING`) | **never sent** (`stream_voice_call` has no temperature parameter) | prose + label parse (bookkeeping tail line only) |
| V2 | Voice · Step 2 First-Draft Artifact (per voice) | `voice/step2_first_draft_artifact.py:299 run_step2_for_voice` → `step_config` `:332` → `stream_voice_call` `:342-349` | `runtime.voice.step2` | same as V1 | Yes | Adaptive, summarized | never sent | prose + regex label parse |
| V2b | Voice · Step 2 synthesis-router (0-2/night, only on ambiguous synthesis) | `voice/step2_first_draft_artifact.py:196 _resolve_primary_theme_id` → call `:280-286` → `editor/synthesis_router.py:106 route_synthesis_voice` → `step_config` `:131` → `messages.create` `:138-145` | `runtime.synthesis_router` | `claude-sonnet-4-6`, thinking off | No | Off (config) | never sent (no key in request) | plain-text 2-line label parse |
| V3 | Voice · Step 3 Amended Artifact (per voice) | `voice/step3_amended_artifact.py:202 run_step3_for_voice` → `step_config` `:232` → `stream_voice_call` `:244-251` | `runtime.voice.step3` | same as V1 | Yes | Adaptive, summarized | never sent | prose + regex label parse |
| V4 | Voice · Step 1 Validation — anachronism (opt-in, off by default; per Step 1 output) | `voice/step1_validation.py:185 check_anachronism` → ladder at `:51-129 _call_openai_with_fallback`, ladder pulled from `step_config(...).ladder` at `:66` | `runtime.voice.step1_validation` | ladder `gpt-5.4 → gpt-4.1 → o3 → gpt-4o → gemini-2.5-pro`, each rung routed by `model_vendor()` at `:71` (legacy `VOICE_VALIDATION_MODELS`) | No | `reasoning_effort="high"` on reasoning rungs only (gpt-5.x, o-series; `:95`) — gpt-4.1/gpt-4o take the plain shape (fixed 2026-09-28) | 0.0 on non-reasoning-path rungs only | plain text, `PASS`/other prefix check |
| V5 | Voice · Step 1 Validation — constitution (opt-in, off by default; per Step 1 output) | `voice/step1_validation.py:210 check_constitution` → same ladder | same | same | No | same | same | same |
| V6 | Voice · Step 2 Validation — Safeguards pillar (default ON; per voice) | `voice/step2_validation.py:134 check_safeguards` → `_call_anthropic` `:78-108` (`step_config` `:86`, `messages.create` `:93-100`) | `runtime.voice.step2_validation` | `claude-sonnet-4-6`, thinking off | No | Off (no `thinking` kwarg built at all) | **not sent** | JSON-in-text (fenced or bare) |
| V7 | Voice · Step 2 Validation — Engagement pillar | `voice/step2_validation.py:228 check_engagement` → same `_call_anthropic` | same | same | No | Off | not sent | JSON-in-text |
| V8 | Voice · Step 2 Validation — Voice-fidelity pillar | `voice/step2_validation.py:285 check_voice_fidelity` → same | same | same | No | Off | not sent | JSON-in-text |
| V9 | Voice · Step 2 Validation — Cross-night echo (Night 2/3 only, if prior artifact exists) | `voice/step2_validation.py:317 check_cross_night_echo` → same | same | same | No | Off | not sent | JSON-in-text |
| V10 | Voice · Continuity (per voice, after Step 3 completes) | `voice/continuity.py:124 generate_continuity` → `step_config` `:157` → `stream_voice_call` `:169-177` | `runtime.voice.continuity` | `claude-sonnet-4-6`, thinking adaptive | Yes | Adaptive, summarized (legacy `VOICE_CONTINUITY_MODEL`/`VOICE_CONTINUITY_THINKING`) | never sent | JSON-in-text (`extract_json`) |
| E1 | Editor · Stage 1 synthesis-router safety net (0-2/night) | `editor/routing.py:112 _parse_focus_to_primary_theme` → call `:211` → same `route_synthesis_voice` as V2b | `runtime.synthesis_router` | `claude-sonnet-4-6`, thinking off | No | Off | never sent | plain-text 2-line label parse |
| E2 | Editor · Stage 2 per-dossier generation (~3-5/night, one per engaged theme) | `editor/dossier_generation.py:537 generate_dossier` → `step_config` `:569` → `stream_voice_call` `:574-581` | `runtime.editor.dossier` | `claude-opus-4-7`, thinking adaptive | Yes | Adaptive, summarized (legacy `EDITOR_MODEL`/`EDITOR_THINKING`) | never sent | prose + regex label parse |

**Not an LLM call (verified — no `Anthropic`/`OpenAI`/`genai` import, no client construction):** `runtime/flows/editor/edition.py`, `runtime/flows/editor/publish.py`, `runtime/flows/editor/card_assembly.py`, `runtime/flows/voice/card_assembly.py`, `runtime/flows/voice/publish.py`, the `voice_flow.py`/`editor_flow.py` orchestrators themselves (they instantiate the `Anthropic` client and pass it down; the `.messages.*` calls live in the modules above), `runtime/scripts/**`.

### 1.2 Persona Pipeline

| # | Pass | file:function(line) | `model_routing.json` step | Model (current default) | Thinking | Temp sent | max_tokens | Structured output | N/voice |
|---|---|---|---|---|---|---|---|---|---|
| P1 | 0a Voice Config | `run_pass0a_voice_config.py:224-233 _call_kwargs` via `_call_with_retry`→`call_claude` (`:55-64`) | `personas.pass_0a_voice_config` | `claude-opus-4-7`, adaptive | True, adaptive (from config) | dropped (thinking=True) | 24000 | JSON-in-text | 1 |
| P2 | 1a Perplexity | `run_phase0_1_research.py:128-144 _pass_1a` → `call_perplexity`, `model=step_config("personas.pass_1a_perplexity").model` `:134` | `personas.pass_1a_perplexity` | `sonar-deep-research` | — | 0.0 sent (REST body) | — (no cap) | prose, `<think>` stripped | 1 |
| P3 | 1b Gemini broad scan | `run_phase0_1_research.py:147-160 _pass_1b` → `call_gemini`, `model=step_config("personas.pass_1b_gemini").model` `:153` | `personas.pass_1b_gemini` | `gemini-2.5-pro` | model-forced on | 0.2 sent | 16384 | prose | 1 |
| P4 | 0b tailor | `run_pass_0b_tailor.py:236-241` | `personas.pass_0b_tailor` | `claude-opus-4-7`, adaptive | True, adaptive | dropped | 16000 | JSON-in-text | 1 |
| P5-10 | 1.1-1.6 chunked merge | `flows/shared/chunk_runner.py:210 run_chunk` (`call_kwargs` `:305-311`, call `:314`) | `personas.pass_1_merge` | `claude-opus-4-7`, adaptive | True, adaptive | dropped | 48000 | Pydantic-validated JSON | 1 each (6 total, parallel ×3) |
| P11 | 1.7 Coherence audit | `run_pass_1_7.py:428 run_pass_1_7` (`call_kwargs` `:481-487`, call `:490`) | `personas.pass_1_7_coherence` | `claude-opus-4-7`, adaptive | True, adaptive | dropped | 24000 | Pydantic-validated JSON | 1 |
| P12 | 1d Excerpt Selection | `run_persona_pipeline.py:544 _pass_1d` → call `:590-593` | `personas.pass_1d_excerpts` | `claude-opus-4-7`, adaptive | True, adaptive | `temperature=None` passed (moot) | 16000 | JSON-in-text | 1 (skipped if no primary texts) |
| P13 | 2 Identity & Boundaries | `run_persona_pipeline.py:484 _pass_2` → `_claude_pass` helper `:438-443` → call `:501` | `personas.pass_2` | `claude-opus-4-7`, adaptive | True (config default), adaptive | dropped | 32000 (helper default) | JSON-in-text | 1 |
| P14 | CT after Pass 2 | `run_persona_pipeline.py:456 _ct_compress` → call `:475-477` | `personas.ct_compress` | `claude-sonnet-4-6`, adaptive | **True** (from config), adaptive | dropped — code passes `temperature=1.0` but it never reaches the API since thinking is on | 16000 | plain text | 1 |
| P15 | 3 Intellectual Core | `run_persona_pipeline.py:511 _pass_3` → `_claude_pass` `:530` | `personas.pass_3` | `claude-opus-4-7`, adaptive | True, adaptive | dropped | 32000 | JSON-in-text | 1 |
| P16 | CT after Pass 3 | same `_ct_compress` | `personas.ct_compress` | `claude-sonnet-4-6`, adaptive | True, adaptive | dropped | 16000 | plain text | 1 |
| P17 | 4a Voice | `run_persona_pipeline.py:668 _pass_4a` → `_claude_pass` `:692-693` | `personas.pass_4a` | `claude-opus-4-7`, adaptive | True, adaptive | dropped | 24000 | JSON-in-text | 1 |
| P18 | CT after Pass 4a | same `_ct_compress` | `personas.ct_compress` | `claude-sonnet-4-6`, adaptive | True, adaptive | dropped | 16000 | plain text | 1 |
| P19 | 4b Artifact | `run_persona_pipeline.py:705 _pass_4b` → `_claude_pass` `:722-723` | `personas.pass_4b` | `claude-opus-4-7`, adaptive | True, adaptive | dropped | 24000 | JSON-in-text | 1 |
| P20 | CT after Pass 4b | same `_ct_compress` | `personas.ct_compress` | `claude-sonnet-4-6`, adaptive | True, adaptive | dropped | 16000 | plain text | 1 |
| P21 | 5 Engagement | `run_persona_pipeline.py:734 _pass_5` → `_claude_pass` `:755-756` | `personas.pass_5` | `claude-opus-4-7`, adaptive | True, adaptive | dropped | 16000 | JSON-in-text | 1 |
| P22 | 6 Corpus Curation | `run_persona_pipeline.py:765 _pass_6` → `_claude_pass` `:802-803` | `personas.pass_6` | `claude-opus-4-7`, adaptive | True, adaptive | dropped | 24000 | JSON-in-text | 1 (HALTS if no primary texts) |
| P23 | 7-pre Stage 1 extract | `flows/shared/pass_7pre_chunked.py:59 extract_claims` → call `:84-91` | `personas.pass_7pre_extract` | `claude-sonnet-4-6`, thinking off | **False** (from config) | **0.0 sent** | 32000 | JSON-in-text | 1 |
| P24 | 7-pre Stage 2 verify (N batches, ~25 claims each, ≤4 parallel) | `pass_7pre_chunked.py:106 verify_batch` → call `:128-135` | `personas.pass_7pre_verify` | `claude-sonnet-4-6`, thinking off | **False** | **0.0 sent** | 16000 | JSON-in-text | N≈3-6 |
| P25 | 7-pre Stage 3 boddice check | `pass_7pre_chunked.py:256 check_boddice_tags` → call `:267-274` | `personas.pass_7pre_boddice` | `claude-sonnet-4-6`, thinking off | **False** | **0.0 sent** | 8000 | JSON-in-text | 1 |
| P26a | 7-anachronism (5-rung cross-vendor ladder) | `run_persona_pipeline.py:1038 _pass_7_anachronism` → `call_validator_ladder("personas.pass_7_anachronism", ...)` `:1064-1065` | `personas.pass_7_anachronism` | ladder `gpt-5.4 → gpt-4.1 → o3 → gpt-4o → gemini-2.5-pro`, each rung routed by `model_vendor()` inside `call_validator_ladder` (`clients.py:546-563`) | OpenAI rungs: `reasoning_effort="high"` **only when the rung name starts with `gpt-5`** (`clients.py:550` — fixed in this refactor, see §7); Gemini: model-forced | OpenAI reasoning path: omitted; non-reasoning rungs (gpt-4.1/gpt-4o/o3) via `call_openai`'s own o-series/`reasoning_effort` gate; Gemini 0.0 | 16384 | JSON-in-text | 1 (1-5 attempts) |
| P27a | 7a Cross-Model (same ladder) | `run_persona_pipeline.py:1087 _pass_7a` → `call_validator_ladder("personas.pass_7a", ...)` `:1103` | `personas.pass_7a` | same ladder | same | same | 16384 | JSON-in-text | 1 (1-5 attempts) |
| P28 | 7a-FIX linear patcher | `run_persona_pipeline.py:1268 _pass_7a_fix` → call `:1392-1394` | `personas.pass_7a_fix` | `claude-opus-4-7`, adaptive | True, adaptive | dropped | 32000 | JSON-in-text | 0 or 1 |
| P29 | 7b Worked Provocations | `run_persona_pipeline.py:1539 _pass_7b` → `_claude_pass` `:1548-1549` | `personas.pass_7b` | `claude-opus-4-7`, adaptive | True, adaptive | dropped | 24000 | JSON-in-text | 1 |
| P30a | 7c Negative Constraints — Gemini primary | `run_persona_pipeline.py:1562 _pass_7c` → `step_config` `:1571` → `call_gemini` `:1576-1577` | `personas.pass_7c` | `gemini-2.5-pro` | model-forced | 0.0 sent | 16384 | JSON-in-text | 1 |
| P30b | 7c fallback | same function → `cfg.fallback` at `:1590` → `call_claude(step=fb, ...)` `:1591-1593` | `personas.pass_7c.fallback` (not a top-level key — resolved via `step_config("personas.pass_7c").fallback`) | `claude-sonnet-4-6`, thinking off | **False** | **0.0 sent** | 8192 | JSON-in-text | only if Gemini fails |
| P31a | 7a FINAL post-assembly (5-rung ladder) | `run_persona_pipeline.py:1894 _pass_7a_final` → `call_validator_ladder("personas.pass_7a_final", ...)` `:1934` | `personas.pass_7a_final` | same ladder as P26/P27 | same | same | 16384 | JSON-in-text | 1 (1-5 attempts; re-fires on operator-patch loop) |
| P32 | Derive | `run_persona_pipeline.py:1998 _derive` → call `:2025-2027` | `personas.derive` | `claude-opus-4-7`, adaptive | True, adaptive | dropped | 24000 | JSON-in-text | 1 |
| P32' | Derive (path-b fast exit, mutually exclusive with P32) | `run_persona_pipeline.py:913 _derive_fast` (inline dup of P32) → call `:926-928` | `personas.derive` (same key) | `claude-opus-4-7`, adaptive | True, adaptive | dropped | 24000 | JSON-in-text | 0 or 1 |

Pure-Python / non-LLM personas steps (confirmed by import-grep, unchanged from before): Pass 0b base render (Jinja2), split tailored prompt, Pass 1c-extract (`url_extract.py`), Pass 1c fetch, Pass 6.5-clean (`bracket_strip.py`), FU#33 P2 INCONSISTENT merge, path-to-pass mapping, card assembly, chat artifact (`chat_prompt_builder.py`), Wikipedia REST. Also verified pure-Python with no LLM imports: `dr_validation.py`, `research_validation.py`, `node0_validation.py`, `node1d_excerpt_selection.py`, `node1c_fetch.py`.

---

## 2. Runtime pipeline calls (detail)

### 2.1 Transcription — `runtime/flows/transcription_flow.py`

Function names current as of this read: `transcribe_with_assemblyai` (:397), `identify_speakers` (:464, 5-pass Speaker ID), `clean_transcript` (:546). Model resolution for all three now goes through `step_config()`:

- **ASR** (`:420`): `step_config("runtime.transcription.asr").model` is injected into the AssemblyAI `TranscriptionConfig.raw.speech_models` list — this is the one step in the repo where a `model_routing.json` entry names a non-Anthropic model literally (`universal-3-pro`) purely for config-plumbing convenience; there's no thinking/effort concept for AssemblyAI.
- **Speaker ID** (`:500` `step_config`, `:520-533` `client.messages.create`): model resolves via the step, legacy override still `TRANSCRIPTION_SPEAKER_ID_MODEL` → `CLAUDE_MODEL`; `max_tokens=4096`; system wrapped in `cache_control` (ephemeral, C19c); **no `temperature` key in the request at all**; thinking off per `model_routing.json` (`"thinking": "off"`). Comment at `:73-79` still documents overriding to `claude-opus-4-7` for hard sessions — if this override is exercised via the legacy env var, thinking stays off by design, which is fine on Opus 4.7 today but **the loader itself now refuses `TRANSCRIPTION_SPEAKER_ID_MODEL=claude-opus-5-5`** (thinking can't disable there) before any API call is made — see §10.
- **Cleaning** (`:560` `step_config`, `:581-594` `client.messages.stream`, required — max_tokens 64000 exceeds the SDK's non-streaming estimate threshold): same no-temperature, thinking-off pattern; legacy override `TRANSCRIPTION_CLAUDE_MODEL` → `CLAUDE_MODEL`; system cache-wrapped.

### 2.2 Researcher — `runtime/flows/researcher_flow.py`

`_thinking_kwargs(cfg)` at `:107-127` now takes the caller's `StepConfig` instead of a `budget_tokens` int, and returns `{"thinking": {"type": "adaptive", "display": "summarized"}}` when `cfg.thinking_on`, else `{}`. No call in this file passes `temperature` under any circumstance; the docstring still cites Opus 4.7's 400 on `temperature` + thinking as the reason.

- `extract_session` (:266, `step_config` :271, stream :303-310): step `runtime.researcher.extraction`, legacy `RESEARCHER_CLAUDE_MODEL`/`CLAUDE_MODEL`/`RESEARCHER_THINKING`, `max_tokens=40000`, system cache-wrapped (ephemeral).
- `cluster_extractions` (:343, `step_config` :365, stream :403-410): step `runtime.researcher.clustering`, `max_tokens=64000`. Deterministic shuffle seed 42; inputs deliberately minimal (`{ref, extraction, context}` only).
- `group_clusters_into_themes` (:474, `step_config` :485, stream :522-529): step `runtime.researcher.theming`, `max_tokens=24000`; cluster-level inputs only.
- `RESEARCHER_NODE1_BATCH` (default 6, env-configurable, unrelated to model choice) parallelizes `extract_session` calls via `ThreadPoolExecutor`.

### 2.3 Provocateur — `runtime/flows/provocateur_flow.py`

All three LLM tasks funnel through one shared helper, `_stream_and_parse` (:349-465), which is the single Anthropic call site (`client.messages.stream` at `:405-412`) for the whole pipeline. `_stream_and_parse` now takes a required keyword-only `cfg: StepConfig` — each caller resolves its own step (`triage_voice`/`triage_flags`/`formulate_for_member` each call `step_config("runtime.provocateur.<step>")` independently, per the docstring at `:366-372`, so an env override or a future per-step JSON split can differ between them even though today all three resolve to the same model/thinking via the shared `PROVOCATEUR_CLAUDE_MODEL`/`CLAUDE_MODEL`/`PROVOCATEUR_THINKING` legacy env vars). No `temperature` key is ever constructed — `_stream_and_parse` has no temperature parameter at all.

- `triage_voice` (:501, step `runtime.provocateur.triage_voice`, `cfg` at `:555`, `max_tokens=TRIAGE_MAX_TOKENS`=40000): per-voice ranking, ~10-25 calls/night. `cache_system=True` (C19c).
- `triage_flags` (:578, step `runtime.provocateur.triage_flags`, `cfg` at `:609`, same max_tokens): single post-aggregation call, `cache_system=False`.
- `formulate_for_member` (:1081, step `runtime.provocateur.formulation`, `cfg` at `:1147`, `max_tokens=FORMULATION_MAX_TOKENS`=40000): per-pair, `cache_system=True` (C19a) — batched via `PROVOCATEUR_FORMULATION_BATCH` (**default now 6**, was 4) with `PROVOCATEUR_BATCH_WAIT_S` (**default now 5**, was 20) between batches — both env-configurable, both changed since the last doc edition, neither part of the model-routing refactor.
- `python_select` (:637) and `package_voice_briefings` (:1220) are pure-Python — no LLM.

### 2.4 Voice Pipeline — `runtime/flows/voice/**`

All streaming calls in this pipeline funnel through one shared helper, **`stream_voice_call`** (`runtime/flows/voice/_anthropic_call.py:65-197`), used identically by Steps 1/2/3, Continuity, and (via reuse) the Editor's dossier generation. It now takes `cfg: StepConfig` (keyword-only) instead of a raw model string + hand-built thinking kwargs — callers no longer carry their own `_thinking_kwargs()` copy; `stream_voice_call` is the one place `{"type": "adaptive", "display": "summarized"}` and `cfg.output_config_kwargs()` are applied for every Voice/Editor call. Its defining property for migration purposes is unchanged: **it never constructs or sends a `temperature` key, under any configuration** (`:150-157`).

`stream_voice_call` still implements the shared 1-retry-on-any-exception policy (5s backoff, `:147-194`) and the prompt-caching scheme described in the prior edition (tuple `(prefix, tail)` system gets a cache breakpoint on each block, 1h TTL; plain string + `cache_system=True` gets one breakpoint; `cache_system=False` disables caching for single-call flows). It also computes `thinking_tokens` via subtraction against the free `messages.count_tokens` endpoint (`:39-62`).

#### 2.4.1 Step 1 — Private Reasoning (`voice/step1_private_reasoning.py`)

`run_step1_for_pair` (:118), `step_config("runtime.voice.step1")` at `:147`, call at `:157-164`. One call per (voice, formulation) pair. Legacy override `VOICE_MODEL`/`CLAUDE_MODEL`/`VOICE_THINKING`; `max_tokens` from `VOICE_STEP1_MAX_TOKENS` (default 64000, `:44`). Output is prose; the only structured extraction is the regex-stripped bookkeeping tail line (`extractions_engaged: id1, id2, ...`). Batched by `voice_flow.py` via `_run_step1_batch` (:167) at `VOICE_STEP1_BATCH` (default 6) concurrency, `VOICE_BATCH_WAIT_S` (default 5) between batches.

#### 2.4.2 Step 2 — First-Draft Artifact (`voice/step2_first_draft_artifact.py`)

`run_step2_for_voice` (:299), `step_config("runtime.voice.step2")` at `:332`, call at `:342-349`. One call per voice per night. `VOICE_STEP2_MAX_TOKENS` default 64000 (`:38`). Output parsed by `_parse_step2_output` (:58-153).

**Embedded synthesis-router call**: `_resolve_primary_theme_id` (:196-296) — when the voice's own words indicate synthesis across themes and there's more than one candidate, it calls `editor/synthesis_router.route_synthesis_voice` (call at `:280-286`) using the same `Anthropic()` client instance Step 2 already created — this is call site V2b / E1's shared implementation (§2.5.1). Fires 0-2 times per night.

#### 2.4.3 Step 3 — Amended Artifact (`voice/step3_amended_artifact.py`)

`run_step3_for_voice` (:202), `step_config("runtime.voice.step3")` at `:232`, call at `:244-251`. Runs after **all** voices complete Step 2. `VOICE_STEP3_MAX_TOKENS` default 64000. Per `voice_flow.py:351`'s default (`skip_step3: bool = False`), Step 3 **runs by default** in the current code — this is unchanged from the prior edition and still worth flagging against the CLAUDE.md-era claim that Step 3 was skipped for Athens production (a time-bound `--skip-step3` production decision, not the code's default).

#### 2.4.4 Voice Step 1 Validation — `voice/step1_validation.py` (opt-in, **off by default**)

Default policy is unchanged: `voice_flow.py:350` sets `skip_validation: bool = True` (C28, 2026-05-04 — "Step 1 validation has no actionable consumer; replaced by C28b Step 2 validator"); CLI re-enables via `--enable-step1-validation`.

When it does run: `check_anachronism` (:185) and `check_constitution` (:210), each calling `_call_openai_with_fallback` (:51-129). The ladder itself now comes from `model_routing.json` — `step_config("runtime.voice.step1_validation").ladder` at `:66` (legacy override still `VOICE_VALIDATION_MODELS`), and **each rung is routed by `model_vendor(model)`** (`:71`) rather than by string-prefix matching or ladder position (the old implementation guessed "Gemini" by name prefix; this is the `f5de9db` fix, applied identically on the personas side — see §7). Both callers pass `reasoning_effort="high"` (`:198`, `:220`); the helper sends it only to reasoning models (`use_reasoning` = gpt-5.x or o-series, `:95`). Until 2026-09-28 it was sent to every rung, so the `gpt-4.1`/`gpt-4o` fallback rungs could only fail (they reject `reasoning_effort`); fixed alongside `f5de9db`.

#### 2.4.5 Voice Step 2 Validation — `voice/step2_validation.py` (default **ON**)

Three pillars always, a fourth conditionally, each through the shared `_call_anthropic` (:78-108, `step_config("runtime.voice.step2_validation")` at `:86`, `client.messages.create` at `:93-100`). Distinct wrapper from `stream_voice_call`: **no `thinking` key, no `temperature` key** are ever constructed. `max_tokens=4096` (`VOICE_STEP2_VALIDATION_MAX_TOKENS`).

- `check_safeguards` (:134), `check_engagement` (:228, plus mechanical `_check_length_compliance` at :186, pure Python), `check_voice_fidelity` (:285), `check_cross_night_echo` (:317, Night 2/3 only).

Run in parallel per voice via `ThreadPoolExecutor(max_workers=STEP2_VALIDATION_PILLAR_BATCH)` (default 6) inside `run_step2_validation` (:406). Orchestrator gate: `step2_validate: bool = True` default in `voice_flow.py:355`, disable via `--skip-step2-validation`. Halt-on-any-flag remains an **operator gate**, not an auto-regen mechanism.

#### 2.4.6 Continuity — `voice/continuity.py`

`generate_continuity` (:124), `step_config("runtime.voice.continuity")` at `:157`, call at `:169-177`. One call per voice, after Night N's Step 3. Legacy `VOICE_CONTINUITY_MODEL`/`VOICE_CONTINUITY_THINKING`; `max_tokens` from `VOICE_CONTINUITY_MAX_TOKENS` (default 8000); `cache_system=False` explicitly.

### 2.5 Editor Pipeline — `runtime/flows/editor/**`

`editor_flow.py` instantiates one `Anthropic()` client, shared across Stage 1's synthesis-router safety net and every Stage 2 dossier call. `_dossier_cfg = step_config("runtime.editor.dossier")` is resolved once at `:225` for logging/manifest purposes; each `generate_dossier` call resolves its own `cfg` too (`dossier_generation.py:569`).

#### 2.5.1 Stage 1 — Routing (`editor/routing.py`) — mostly pure Python, one conditional LLM call

Theme routing (Cases A/B/C/D) is deterministic Python inside `_parse_focus_to_primary_theme` (:112-233ish). The one LLM call, `route_synthesis_voice` (`editor/synthesis_router.py:106-179`), fires as a **safety net** at `routing.py:211` for any voice whose `lineage.primary_theme_id` is still null after Step 2's own attempt — same function, same model, so it never double-charges a voice Step 2 already resolved. Model resolution: `step_config("runtime.synthesis_router")` at `synthesis_router.py:131`; `client.messages.create` at `:138-145` — **no `temperature`, no `thinking` key sent by default** (config says `thinking: "off"`); `max_tokens=500` (`SYNTHESIS_ROUTER_MAX_TOKENS`). Output is a fixed 2-line label format, parsed by regex; on any failure it falls back to the lowest-numbered candidate.

`gating_status` (`routing.py:280`) — pure Python; unchanged.

#### 2.5.2 Stage 2 — Per-dossier generation (`editor/dossier_generation.py`)

`generate_dossier` (:537), `step_config("runtime.editor.dossier")` at `:569`, call via `stream_voice_call` at `:574-581` (same shared helper as Voice — no `temperature` ever sent). One call per engaged theme per night. `max_tokens` from `EDITOR_MAX_TOKENS` (default 32000). System prompt is a `(prefix, tail)` tuple from `card_assembly.assemble_system_prompt` (`editor/card_assembly.py:286`) — identical prefix across a night's dossier calls, so calls 2-N hit the 1h prefix cache. Calls run in parallel via `ThreadPoolExecutor(max_workers=EDITOR_BATCH)` (default 6, `editor_flow.py:231`). A second `step_config` call inside `stamp_runtime_fields`'s default argument (`:441-448`) exists only so direct unit-test calls without a real `cfg` still get a live model value — not a second API call.

#### 2.5.3 Stage 3 — Edition (`editor/edition.py`) and Publish (`editor/publish.py`, `voice/publish.py`)

Confirmed pure Python — no `Anthropic`/`client`/`openai`/`genai` reference anywhere in any of these three files, re-verified this pass. `finalize_edition` does lead-theme picking and index-writing algorithmically.

---

## 3. Persona Pipeline calls (detail)

Same pipeline shape as the prior edition (Phase 0 intake → 0.5 pre-DR research → 0.7 manual DR → Phase 1 chunked merge → Phase 2 section generation → 2.5 cleanup → Phase 3 validation → Phase 4 derive), re-verified line-by-line against the post-refactor code. §1.2's table has the authoritative per-call-site line numbers and step keys; this section calls out what the refactor actually changed in each call site's *shape*, not just its line number.

**Confirmed unchanged in substance (still call through the same helpers, only the model-resolution plumbing changed):** Pass 0a, 1a/1b parallel research, 0b tailor, chunked merge 1.1-1.7, Pass 1c (pure Python), Pass 1d, Pass 2/3/4a/4b/5/6 (all via `_claude_pass` at `run_persona_pipeline.py:438-443`), Pass 6.5-clean (pure Python), Pass 7-pre 3-stage chunked, Pass 7a-FIX linear patcher, Pass 7b, Derive, chat artifact (pure Python).

**What the refactor actually changed here:**

1. **Every `call_claude` invocation now passes `step=` instead of a hardcoded `model=` literal.** `call_claude`'s signature (`clients.py:80-94`) gained `step: str | StepConfig | None`; when given, it resolves `model`/`thinking`/`effort` from `model_routing.json` before any explicit `model=`/`thinking=`/`effort=` argument is applied as an override. Passing neither `step` nor `model` now raises `ValueError` — there is no more implicit `CLAUDE_MODEL` env fallback inside `call_claude` itself (see §5.2 for what this means for that env var).
2. **The three cross-vendor validator ladders (7-anachronism, 7a, 7a FINAL) are no longer copy-pasted loops.** They were consolidated into `clients.py:528-564 call_validator_ladder(step, ...)`, called from `run_persona_pipeline.py:1064` (`_pass_7_anachronism`), `:1103` (`_pass_7a`), and `:1934` (`_pass_7a_final`). Each rung is now routed by `model_vendor(model)` — a real dictionary lookup in `model_routing.json`'s `models` block — instead of "OpenAI for every rung but the last, Gemini for the last" (which happened to work only because the ladder always ended in a Gemini model). This is the `f5de9db` commit and it also **fixed** the `reasoning_effort` bug: `call_validator_ladder` (`:550`) sets `reasoning_effort="high"` only when the rung name starts with `gpt-5`, not unconditionally — see §7 for why this now diverges from the runtime Step 1 validation copy.
3. **CT (coherence-threading) compression** (`_ct_compress`, `run_persona_pipeline.py:456-480`) still calls `call_claude(step="personas.ct_compress", ..., temperature=1.0)` without an explicit `thinking=` — thinking comes from the step's config (`"adaptive"`), so, same as before the refactor, `temperature=1.0` is passed but dropped before the request is built. Net effect unchanged from the prior edition's correction: **CT calls carry zero temperature risk on any future model**, because the drop is thinking-gated, not model-gated.
4. **Two Derive implementations, not one**, unchanged in shape: canonical `_derive()` (`:1998`, call `:2025-2027`) and the inline `_derive_fast()` (`:913`, call `:926-928`) inside the "PATH-(b) DERIVE-ONLY FAST EXIT" branch. Both now resolve `step="personas.derive"` identically (previously both hardcoded the same model string) — still one logical call site for migration purposes, both keyed to the same `model_routing.json` entry.
5. **Function/line numbers moved** throughout `run_persona_pipeline.py` — every reference in §1.2 above is current as of this read; do not carry forward line numbers from the 2026-09-27 edition.

**Pass 7c** (`_pass_7c`, `:1562-1596`) is structurally different from the other passes: it's the one step whose `model_routing.json` entry (`personas.pass_7c`) carries a `"fallback"` object instead of being purely Anthropic. `step_config("personas.pass_7c")` at `:1571` returns a `StepConfig` whose `.model` is `gemini-2.5-pro` (used directly in `call_gemini(..., model=cfg.model)` at `:1576-1577`) and whose `.fallback` is itself a nested `StepConfig` for the Sonnet bias-aware fallback (`:1590`, `call_claude(step=fb, ...)` at `:1591-1593` — `call_claude`'s `step` parameter accepts an already-built `StepConfig` for exactly this case, per its docstring at `clients.py:97-99`).

**Not re-verified in full depth this pass (unchanged structurally, low migration relevance):** the exact prompt-file inventory (§4 carries it forward), the manifest-recording gap (`chunk_runner.py`/`pass_7pre_chunked.py` pass `slug`/`pass_name` telemetry kwargs, most `run_persona_pipeline.py` call sites still don't), `paths.merge_chunk()` dead code.

---

## 4. Prompt file inventory

Unchanged in location/shape from the prior edition; carried forward for completeness rather than re-verified word-for-word (prompt *content* doesn't bear on model/parameter compatibility, and none of the prompt files were touched by the model-routing refactor — confirmed by `git show --stat` on all three refactor commits, none of which touch `flows/shared/prompts/`).

### 4.1 Runtime prompts — `runtime/flows/shared/prompts/`

Speaker ID / Cleaning / Researcher (extraction/clustering/theming) / Provocateur (triage voice/flags/formulation) prompts, plus Voice (`voice_step1_*.md`, `voice_step2_artifact.md`, `voice_step3_amendment.md`, `voice_step1_validation_anachronism.md`, `voice_step1_validation_constitution.md`, `voice_step2_validation_{safeguards,engagement,voice_fidelity,cross_night_echo}.md`, `voice_continuity.md`) and `editor_dossier.md`.

### 4.2 Personas prompts — `personas/flows/shared/prompts/`

~50 files, Jinja2, loaded via `flows/shared/io.load_prompt()` — structure unchanged from the prior edition's table.

---

## 5. Where models are chosen: `model_routing.json` (+ legacy env overrides)

**`model_routing.json` (repo root) is the single source of truth for which model, thinking mode, and effort each step uses.** It is loaded by the byte-identical `runtime/flows/shared/model_routing.py` and `personas/flows/shared/model_routing.py` (a test in each suite checks the copies match). Every call site in §1 asks for its step via `step_config(<key>)` (or, in `call_claude`, `step=<key>`) and gets back a `StepConfig` with `.model`, `.thinking`/`.thinking_on`, `.effort`, `.sampling_params`, and — for the three validator passes — `.ladder`. **Do not hand-edit a model name in code** — the persona and runtime test suites both scan for hardcoded model literals and fail the build on one (`personas/tests/test_no_hardcoded_models.py`, `runtime/tests/test_model_routing_call_sites.py`'s AST scan); change `model_routing.json` instead.

### 5.1 Legacy env-var overrides

These still work (call sites don't need to change to pick up an override) because `step_config()` checks them **before** falling back to the JSON's value, per `_MODEL_ENV` / `_THINKING_ENV` / `_LADDER_ENV` in `model_routing.py`. **An empty env value counts as unset** (`_env()` strips and treats `""` as `None` — the Claude Code shell pre-sets some vars to `""`, which used to be a footgun before this normalization).

| Legacy env var | Step(s) it overrides (model, unless noted) | Notes |
|---|---|---|
| `TRANSCRIPTION_SPEAKER_ID_MODEL` → `CLAUDE_MODEL` | `runtime.transcription.speaker_id` | |
| `TRANSCRIPTION_CLAUDE_MODEL` → `CLAUDE_MODEL` | `runtime.transcription.cleaning` | |
| `RESEARCHER_CLAUDE_MODEL` → `CLAUDE_MODEL` | `runtime.researcher.*` (all three: extraction, clustering, theming — prefix match) | |
| `PROVOCATEUR_CLAUDE_MODEL` → `CLAUDE_MODEL` | `runtime.provocateur.*` (all three) | |
| `VOICE_MODEL` → `CLAUDE_MODEL` | `runtime.voice.step1` / `.step2` / `.step3` | |
| `VOICE_CONTINUITY_MODEL` | `runtime.voice.continuity` | no `CLAUDE_MODEL` fallback for this one |
| `VOICE_STEP2_VALIDATION_MODEL` | `runtime.voice.step2_validation` | no `CLAUDE_MODEL` fallback |
| `SYNTHESIS_ROUTER_MODEL` | `runtime.synthesis_router` | no `CLAUDE_MODEL` fallback; shared by V2b and E1 |
| `EDITOR_MODEL` → `CLAUDE_MODEL` | `runtime.editor.dossier` | |
| `RESEARCHER_THINKING` | `runtime.researcher.*` (thinking on/off) | `"0"`/`"false"`/`"off"`/`"no"` (case-insensitive) = off, anything else set = adaptive |
| `PROVOCATEUR_THINKING` | `runtime.provocateur.*` (thinking) | same |
| `VOICE_THINKING` | `runtime.voice.step1`/`.step2`/`.step3` (thinking) | same |
| `VOICE_CONTINUITY_THINKING` | `runtime.voice.continuity` (thinking) | same |
| `EDITOR_THINKING` | `runtime.editor.dossier` (thinking) | same |
| `VOICE_VALIDATION_MODELS` | `runtime.voice.step1_validation` (**whole ladder**, comma-separated) | the only ladder-level env override in the repo — there is no persona-side equivalent (see below) |
| `PERPLEXITY_MODEL` | `personas.pass_1a_perplexity` | |
| `GEMINI_MODEL` | `personas.pass_1b_gemini` | **also** consulted as `call_gemini`'s own internal default (`clients.py:407`) when a caller doesn't pass `model=` at all — the only production caller that omits `model=` is the dev-only `phase_5_cross_persona_qc.py`'s Gemini-fallback evaluator (§9) |

**Not overridable by any environment variable (verified — grepped for every var name across both trees):**

- **`CLAUDE_MODEL` has no effect on any `personas.*` step.** It only appears in `_MODEL_ENV` paired with runtime steps (transcription, researcher, provocateur, voice step1-3, editor dossier). Every persona Claude call site resolves via `step_config(step=...)`, and `call_claude` itself no longer has an implicit `CLAUDE_MODEL` fallback (it raises if neither `step` nor `model` is given — `clients.py:124-125`). To change a persona pass's model, edit `model_routing.json`; there is no env-var shortcut.
- **`OPENAI_MODEL` is fully dead.** It is not read anywhere in the current codebase (`grep -rn "OPENAI_MODEL"` across both trees returns nothing outside this doc). The prior edition described it as "overridable, but bypassed by the hardcoded ladders" — it is now not read at all, by anything.
- **The persona validator ladders (`personas.pass_7_anachronism`, `personas.pass_7a`, `personas.pass_7a_final`) have no env override.** Only the runtime Voice Step 1 validation ladder does (`VOICE_VALIDATION_MODELS`, above). To change a persona ladder's rungs or order, edit `model_routing.json`.

### 5.2 Loader safety refusals

`model_routing.py`'s `_build()` validates every step **at load time** (both when the JSON is first read and again whenever `step_config()`/`all_steps()` resolves an env override), and raises `ModelRoutingError` — a clear message, before any API call — rather than letting a bad combination reach the vendor as a 400:

- **Thinking off on a model that can't disable it.** `claude-opus-5-5` has `thinking_can_disable: false` in the `models` block; any step (or env override) that sets `thinking: "off"` while resolving to that model is refused outright.
- **No explicit effort on a model whose default effort isn't `"high"`.** `claude-opus-5-5`'s `default_effort` is `"medium"`; any step that leaves `effort: null` while resolving to that model is refused — this is a deliberate guard against the exact silent-quality-drop scenario the 2026-09-27 edition's migration notes flagged as the highest-impact risk of an Opus 4.7 → 5.5 swap (§10 below).
- **A validator-ladder rung that isn't an OpenAI or Google model.** `_LADDER_VENDORS = {"openai", "google"}`; a ladder is a cross-model check of Claude's own output, so a Claude rung would be same-family and defeat the point — the loader rejects it.

### 5.3 Other env vars (call parameters unrelated to model choice)

These affect `max_tokens`/concurrency/batching, not which model or thinking mode is used, and were not touched by the refactor. Re-verified this pass:

**Runtime:**

| Variable | Default | Effect |
|---|---|---|
| `ANTHROPIC_API_KEY` / `ASSEMBLYAI_API_KEY` | — | Required. |
| `RESEARCHER_NODE1_BATCH` | `6` | Per-session extraction concurrency. |
| `PROVOCATEUR_FORMULATION_BATCH` | `6` (changed from `4`) | Formulation batching. |
| `PROVOCATEUR_BATCH_WAIT_S` | `5` (changed from `20`) | Wait between Formulation batches. |
| `VOICE_STEP{1,2,3}_MAX_TOKENS` | `64000` each | Per-step ceiling. |
| `VOICE_STEP1_BATCH` / `VOICE_CONTINUITY_BATCH` | `6` each | Concurrency caps. |
| `VOICE_BATCH_WAIT_S` | `5` | Wait between Step 1 batches. |
| `VOICE_VALIDATION_MAX_TOKENS` | `8192` | Step 1 validation cap (opt-in feature, off by default). |
| `VOICE_CONTINUITY_MAX_TOKENS` | `8000` | Continuity cap. |
| `VOICE_STEP2_VALIDATION_MAX_TOKENS` | `4096` | Per-pillar cap. |
| `VOICE_STEP2_VALIDATION_PILLAR_BATCH` | `6` | Pillar concurrency. |
| `SYNTHESIS_ROUTER_MAX_TOKENS` | `500` | Router cap. |
| `EDITOR_MAX_TOKENS` | `32000` | Dossier cap. |
| `EDITOR_BATCH` | `6` | Dossier-call concurrency. |
| `AI_ASSEMBLY_PROJECT_ROOT` | — | Tier 3 PROJECT_ROOT resolution (not a call parameter; kept here for continuity with the prior edition). |

**Personas:**

| Variable | Default | Effect |
|---|---|---|
| `ANTHROPIC_API_KEY` / `PERPLEXITY_API_KEY` / `GOOGLE_API_KEY` / `OPENAI_API_KEY` | — | Required per provider used. |

No persona-side `max_tokens`/batch env vars exist — every chunked-merge/validator batch size (`_VERIFY_BATCH_SIZE=25`, `_VERIFY_MAX_WORKERS=4` in `pass_7pre_chunked.py`; `max_tokens` per pass in `run_persona_pipeline.py`) is a hardcoded module constant, unchanged from the prior edition.

---

## 6. Shared wrapper behavior

### 6.1 `call_claude` — `personas/flows/shared/clients.py:80-300`

The persona pipeline's only Claude wrapper. Signature now: `call_claude(*, system, user, step: str | StepConfig | None = None, model=None, max_tokens=8192, temperature=0.2, thinking=None, effort=None, response_format_json=False, slug=None, pass_name=None, project_root=None)`.

- **Model/thinking/effort resolution** (`:119-127`): if `step` is given (a string, resolved via `step_config()`, or an already-built `StepConfig` — used by Pass 7c's fallback), its `.model`/`.thinking_on`/`.effort` populate the call *unless* the caller also passed an explicit `model=`/`thinking=`/`effort=`, which wins for that one field. Passing neither `step` nor `model` raises `ValueError` — no more implicit `CLAUDE_MODEL` fallback (§5.2).
- **Temperature policy** (`:134`, `:158-159`): `sampling_params_ok = cfg.sampling_params if cfg is not None else True`; then `if temperature is not None and not thinking and sampling_params_ok: kwargs["temperature"] = temperature`. This is new since the last edition and is the load-bearing safety net for a future model swap: **a call site that resolves via `step=` to a model marked `sampling_params: false` in `model_routing.json` (the Opus-5.x family today) will never have temperature sent, even if the caller passes an explicit non-null `temperature`.** The one gap: a call site that passes a raw `model=` string *without* `step=` gets `cfg is None` → `sampling_params_ok` defaults to `True` — this is exactly the dev-only `phase_5_cross_persona_qc.py:_invoke_voice` path (§9), which stays a real risk if its hardcoded model were ever bumped to a `sampling_params:false` model.
- **Thinking**: `thinking=True` → `kwargs["thinking"] = {"type": "adaptive", "display": "summarized"}` (`:171`). No `budget_tokens` in any code path.
- **Effort**: `if effort: kwargs["output_config"] = {"effort": effort}` (`:143-144`) — omitted entirely when falsy, so the model's own default effort applies. Today every step's `effort` is `null` in `model_routing.json`, so this is a no-op everywhere in production; it's live plumbing waiting for a future step that needs a non-default effort (e.g. an Opus-5.5 migration that wants to force `"high"`).
- **Streaming heuristic**: `use_streaming = max_tokens >= 16384 or thinking` (`:176`), plus the 1-retry-with-15s-backoff on `httpx.RemoteProtocolError`/`ReadError`/`ReadTimeout` (`:196-212`).
- **Structured output**: `response_format_json=True` strips ```` ```json ```` fences then `json.loads`; on failure with `stop_reason == "max_tokens"` raises blaming the budget, otherwise re-raises with diagnostics (`:280-297`).
- **Manifest recording**: only when `slug` + `pass_name` are passed (`:50-75`) — unchanged gap, still `chunk_runner.py`/`pass_7pre_chunked.py` only.

### 6.2 `stream_voice_call` — `runtime/flows/voice/_anthropic_call.py:65-197`

Shared by Voice Steps 1/2/3, Continuity, and Editor Stage 2. Signature now takes `cfg: StepConfig` (keyword-only) instead of a raw model string — `stream_voice_call` itself turns `cfg.thinking_on` into the adaptive/summarized payload and forwards `cfg.output_config_kwargs()` (`:109-114`). Still has **no temperature parameter of any kind** — structurally absent from both the function signature and the `client.messages.stream(...)` call (`:150-157`) — immune to the temperature-400 class of migration break regardless of model choice.

### 6.3 `_stream_and_parse` — `runtime/flows/provocateur_flow.py:349-465`

Provocateur's equivalent shared helper. Now takes `cfg: StepConfig` (keyword-only, `:358`). Same no-temperature-parameter property as `stream_voice_call`. Adds the empty-text-stream and JSON-parse-failure diagnostics, plus per-result usage/cache-token stamping (C37).

### 6.4 `_call_anthropic` — `runtime/flows/voice/step2_validation.py:78-108`

Non-streaming, single-purpose helper for the four Step 2 validation pillars. Resolves `step_config("runtime.voice.step2_validation")` internally (`:86`) rather than taking a `cfg` parameter (it's a single fixed step, unlike the multi-step helpers above). `client.messages.create(model=..., max_tokens=..., system=..., messages=..., **thinking_kwargs, **cfg.output_config_kwargs())` — no `thinking`/`temperature` key constructed when the config says thinking off (today's default). Structurally the safest call site in the repo for a model swap since it sends nothing that any target model rejects, *and* it self-resolves its own step so there's no risk of a caller passing a stale `cfg`.

### 6.5 `call_validator_ladder` — `personas/flows/shared/clients.py:528-564` (NEW)

Replaces what used to be three copy-pasted OpenAI/Gemini fallback loops inside `run_persona_pipeline.py` (Pass 7-anachronism, 7a, 7a FINAL). `call_validator_ladder(step, *, system, user, max_tokens=16384, warn=print)`: iterates `step_config(step).ladder`, routes each rung to `call_openai` or `call_gemini` by `model_vendor(model)` (not by position), and returns `{"validator": "<vendor>:<model>", "model", "usage", "result"}` on the first success or `None` if every rung fails. For OpenAI rungs it sets `reasoning_effort = "high" if model.startswith("gpt-5") else None` (`:550`) — this is the fix that makes gpt-4.1/gpt-4o correctly skip the reasoning-API code path inside `call_openai` (see §7). **This function has no direct counterpart shared with the runtime tree** — the runtime Voice Step 1 validation ladder (`voice/step1_validation.py:_call_openai_with_fallback`) is a separately-maintained implementation of the same pattern, and it was *not* given the same `gpt-5`-only-effort fix (§2.4.4/§7).

### 6.6 `_call_openai_with_fallback` — `runtime/flows/voice/step1_validation.py:51-129`

Runtime's independent (not shared with personas) copy of the OpenAI/Gemini fallback pattern. Now pulls its ladder from `step_config("runtime.voice.step1_validation").ladder` (`:66`) instead of a hardcoded `_DEFAULT_LADDER` tuple, and routes each rung by `model_vendor(model)` (`:71`) instead of guessing Google-by-name. `reasoning_effort` goes only to reasoning models (gpt-5.x, o-series — `use_reasoning` at `:95`); gpt-4.1/gpt-4o get the plain `temperature=0.0` + `max_tokens` shape. One remaining difference from the persona helper: o3 receives `reasoning_effort="high"` here but no effort (model default) there — unchanged behavior on both sides.

### 6.7 `call_perplexity` / `call_gemini` / `call_openai` — `personas/flows/shared/clients.py:305-515`

Unchanged in their own bodies from the prior edition. `call_gemini` (`:380-436`) keeps its own `GEMINI_MODEL` env fallback for callers that don't pass `model=` (only the dev QC script does this today, §9). `call_openai` (`:441-515`) auto-detects reasoning models (`o1`/`o3`/`o4` prefixes, or explicit `reasoning_effort`) and switches to `max_completion_tokens` + drops `temperature` + forwards `reasoning_effort`.

---

## 7. Historical + newly-found parameter notes

Carrying forward only the still-relevant items from the prior edition's §7, plus what this regeneration found:

1. **Validator ladders: fixed on both sides (2026-09-28).** Both used to pick "Gemini" by position (personas) or name prefix (runtime); `f5de9db` routes each rung by `model_vendor()` instead. The runtime ladder also sent `reasoning_effort="high"` to every rung, so its `gpt-4.1`/`gpt-4o` fallback rungs could only fail — it now sends it to reasoning models only, as the persona side always did (§2.4.4, §6.6).
2. **`CLAUDE_MODEL` is now completely inert for the persona pipeline** (§5.1) — a clean resolution of the prior edition's "mostly decorative" finding. It still works for runtime.
3. **`OPENAI_MODEL` is dead code as an env var** — not read anywhere (§5.1). Worth removing from any run-command documentation that still mentions it.
4. **`call_claude`'s new `sampling_params_ok` gate (§6.1) retroactively defuses most of the previous edition's Sonnet-4.6→Sonnet-5 temperature-400 predictions** for production call sites (Pass 7-pre ×3, Pass 7c fallback) — see §10 for the updated migration read. It does **not** protect the one dev-script call site that bypasses `step=` entirely (§9).
5. **The loader's effort-default refusal (§5.2) retroactively defuses the previous edition's single highest-impact finding** — the silent Opus-5.5 effort drop from implicit `high` to implicit `medium` can no longer happen by just editing `model_routing.json`'s `"model"` field; the loader raises immediately if `"effort"` isn't also set. See §10.
6. **CT temperature** — unchanged from the prior edition's correction: `temperature=1.0` is passed but always dropped because `thinking=True`, regardless of what env or step config later does to the model.
7. **Voice Step 1 Validation docstring vs. orchestrator default** — unchanged: docstring says default-on, `voice_flow.py`'s actual default is off (C28).
8. **Transcription intentionally omits thinking even on Opus** — unchanged; still the shape that the loader's thinking-refusal rule (§5.2) now catches *before* the API does, when this override path is exercised against `claude-opus-5-5`.
9. **Manifest recording incomplete on the main orchestrator** — unchanged, telemetry gap.
10. **`paths.merge_chunk()` dead code** — unchanged, cosmetic.
11. **Orphaned legacy Pass 7-pre prompts** — unchanged, not imported anywhere.
12. **No `tool_choice`, no `top_p`/`top_k`, no `budget_tokens` sent, no generation-time prefill anywhere in the repo** — re-verified fresh this regeneration (§0).
13. **No Anthropic call site anywhere sets an explicit thinking `effort`** — every step's `model_routing.json` entry has `"effort": null` today. This is no longer a silent risk the way it was in the prior edition, because the loader would refuse `effort: null` outright the moment a step's model defaulted to something other than `"high"` (§5.2) — the risk has moved from "silent quality regression" to "loud `ModelRoutingError` at config-load time," which is exactly the intended effect of this refactor.
14. **A stale hardcoded model list survives in one metadata string, not a call site**: `run_persona_pipeline.py:1777`'s assembled-card `metadata.tools_used` field is a literal list (`["...claude-opus-4-7", "...claude-sonnet-4-6", ...]`) describing which vendors/models built the card, for human-readable provenance. It is not read by `step_config()` or used to make a call — just worth knowing it will silently go stale the next time a step's model changes in `model_routing.json`, since nothing regenerates it from the config.

---

## 8. What is NOT an LLM call

**Manual model choices (no API call):** the six claude.ai Deep Research sessions per voice are done by the operator. Their model is still set in `model_routing.json` (steps `personas.dr_sections_1_5`, `personas.dr_section_6`, `"manual": true`) and rendered into the section-prompt preambles by `prompt_render.model_name()` (voices OPEN_ITEMS §36).

Runtime: `python_select`/Provocateur Stage 2 selection, `package_voice_briefings`/Stage 4 packaging, Researcher's `merge_clusters_and_themes`, FFmpeg normalize/ffprobe (Ingest), Voice `card_assembly.py`, Voice `publish.py`, Editor `card_assembly.py`, Editor `edition.py`, Editor `publish.py`, `runtime/scripts/**`, Voice Step 2 Validation's mechanical length check (`_check_length_compliance`).

Personas: Pass 0b base render (Jinja2), split tailored prompt, Pass 1c-extract + fetch, Pass 6.5-clean, FU#33 P2 INCONSISTENT merge, path-to-pass mapping, card assembly, CARD COMPLETE summary, chat artifact, Wikipedia REST, `dr_validation.py`/`research_validation.py`/`node0_validation.py`/`node1d_excerpt_selection.py`/`node1c_fetch.py` (all confirmed import-clean this pass).

---

## 9. Dev / QC tooling that fires live API calls (not part of the automated per-night / per-voice build)

Flagged separately so these don't get miscounted as production call sites in a cost or migration audit — they only fire when an operator runs them by hand. **Both scripts below are the explicitly exempt call sites that don't go through `step_config`/`call_claude(step=...)`** (per the regeneration brief); everything else in the repo does.

- **`personas/phase_5_cross_persona_qc.py`** — cross-persona QC harness. `_call_evaluator` (:118-141) tries OpenAI `o3` (`call_openai` at `:126-128`, `temperature=0.0`) → Gemini fallback (`:141`, `call_gemini(user=..., temperature=0.0, max_output_tokens=8192)` with **no `model=` passed** — this is the one production-adjacent caller that relies on `call_gemini`'s own internal `GEMINI_MODEL`-env-or-`gemini-2.5-pro` default, §5.1); `_invoke_voice` (:296-315, call `:310-314`) calls `claude-sonnet-4-6` directly with `thinking=False, temperature=0.7` — hardcoded `model=`, bypasses `step=` entirely, so `call_claude`'s new `sampling_params_ok` safety net does not apply here (§6.1, §7 item 4): if this script's model literal were ever bumped to a `sampling_params:false` model, it would still try to send `temperature=0.7` and 400.
- **`personas/scripts/standalone_pass4b_test.py`** — one-off empirical Pass 4b re-run tool, writes to `/tmp/`. Call at `:70-76`: `model="claude-opus-4-7"`, `thinking=True`, `temperature=1.0` (dropped, same as production Pass 4b) — safe under the same logic as every other `thinking=True` Opus call, and also bypasses `step=`.

---

## 10. Migration notes (C62 → superseded by C63's model-config refactor)

**A model migration is now primarily an edit to `model_routing.json`** — change the relevant step's (or steps') `"model"` field, add `"effort"` if the target model's own default isn't `"high"`, and adjust `"thinking"` if the target can't run the current mode. Then: (1) update the golden table in `runtime/tests/test_model_routing.py` (`GOLDEN` dict, `:21`) so `test_model_routing_call_sites.py`'s per-step tests pass against the new expected `(model, thinking)` pairs; (2) re-run the persona/runtime test suites (`personas/tests/test_no_hardcoded_models.py`, `test_step_keys_exist.py`, `test_call_claude_config.py`, `test_validator_ladder.py`; `runtime/tests/test_model_routing.py`, `test_model_routing_call_sites.py`); (3) **re-validate the voices** (sentinel regen) before relying on a Voice/Editor-pipeline model swap in production — per `model_routing.json`'s own `_doc` note, switching a voice-writing step's model changes how the voices write. This is a much smaller and safer operation than the file-by-file literal hunt the 2026-09-27 edition described.

Scope below: precisely which call sites still break or change behavior under **(a)** Opus 4.7 → Opus 5.5 and **(b)** Sonnet 4.6 → Sonnet 5, given what the loader now catches automatically vs. what still requires a code change.

### 10.0 Live-bug check (today, on current defaults) — unchanged from the prior edition

**No call site currently sends an explicit `temperature`, `top_p`, `top_k`, or `budget_tokens` to `claude-opus-4-7`.** Re-verified: every Opus-4.7-targeting call site either goes through `stream_voice_call`/`_stream_and_parse` (no temperature parameter at all) or through `call_claude` with `thinking=True` (temperature dropped structurally). No live bug on this axis.

### 10.1 (a) Opus 4.7 → Opus 5.5 — now mostly a config-time refusal, not a runtime break

**Formerly "conditional breaks," now caught by the loader before any API call:**

- `runtime/flows/transcription_flow.py` (Speaker ID `:520-533`, Cleaning `:581-594`) — pointing `TRANSCRIPTION_SPEAKER_ID_MODEL`/`TRANSCRIPTION_CLAUDE_MODEL`/`CLAUDE_MODEL` at `claude-opus-5-5` while `model_routing.json` still says `"thinking": "off"` for these steps now raises `ModelRoutingError` at `step_config()` time (§5.2) — **was** a silent 400 from Anthropic in the prior edition's analysis, **is now** a loud, pre-flight Python exception with a clear message. Still has to be fixed before the override is usable on Opus 5.5 (add an explicit `"thinking": "adaptive"` override, or restrict the override to Sonnet 5), but it can no longer reach the API in a broken state.
- `runtime/flows/voice/step2_validation.py:93-100` (`_call_anthropic`, all 4 pillars), `runtime/flows/editor/synthesis_router.py:138-145` and `voice/step2_first_draft_artifact.py:280-286` (shared `route_synthesis_voice`) — same shape: `VOICE_STEP2_VALIDATION_MODEL`/`SYNTHESIS_ROUTER_MODEL` pointed at Opus 5.5 with the JSON's `"thinking": "off"` left in place now fails fast at config-resolution time.
- `personas/phase_5_cross_persona_qc.py:310-314` — this one is **not** caught by the loader, because it bypasses `step_config` entirely (hardcoded `model=`). If someone hardcodes `claude-opus-5-5` into `_invoke_voice`'s `model=` argument, it will still reach the API with no `thinking` key and 400. Dev-only tool, not live today.

**No longer possible to do silently — formerly the single highest-impact item:**

The prior edition's top finding was that every Opus adaptive-thinking call site relies on the model's *implicit* default reasoning depth (none sets `effort` explicitly), so moving to Opus 5.5 (`default_effort: "medium"`) would silently halve the effective reasoning depth from the current implicit `"high"` with no error — a quality regression invisible without a side-by-side eval. **`model_routing.json`'s loader now refuses this outright**: any step whose `"model"` is set to `claude-opus-5-5` while `"effort"` stays `null` raises `ModelRoutingError` immediately (§5.2), for every one of the ~20+ affected call sites (personas Pass 0a/0b-tailor/1.1-1.7/1d/2/3/4a/4b/5/6/7a-FIX/7b/Derive, Voice Step 1/2/3, Editor dossier, Researcher extraction/clustering/theming, Provocateur triage/formulation). A migration to Opus 5.5 is now forced to make an explicit choice about `effort` — it cannot happen by accident.

### 10.2 (b) Sonnet 4.6 → Sonnet 5 — most previously-flagged breaks are now defused by `call_claude`'s sampling-params gate

Sonnet 5 accepts thinking disabled (no break there) but rejects `temperature`/`top_p`/`top_k` (`sampling_params: false` in `model_routing.json`, same family as Opus 5.x). The prior edition flagged four explicit-temperature call sites as certain 400s on a Sonnet-5 swap. Re-checked against the new `call_claude` (`sampling_params_ok` gate, §6.1):

- `personas/flows/shared/pass_7pre_chunked.py:84-91` (Stage 1 extract), `:128-135` (Stage 2 verify), `:267-274` (Stage 3 boddice check) — all three resolve via `step="personas.pass_7pre_extract"`/`"_verify"`/`"_boddice"`. **If `model_routing.json` repoints any of these steps at `claude-sonnet-5`, `call_claude` will see `cfg.sampling_params == False` and silently drop the explicit `temperature=0.0` before it reaches the API — no 400.** This is a real behavior change from the prior edition's prediction (was: certain break; now: silently safe, because the loader-plus-wrapper combination was specifically built to make this swap safe). Worth flagging as a discrepancy the reader should know about: the *2026-09-27* migration notes for this exact call site are now wrong, in the safe direction.
- `personas/run_persona_pipeline.py:1591-1593` (`_pass_7c` Sonnet fallback, via `cfg.fallback`) — same protection: resolves through `step=`, so `sampling_params_ok` gates it.
- `personas/phase_5_cross_persona_qc.py:310-314` — **still a real break.** This call passes `model="claude-sonnet-4-6"` directly, not via `step=`, so `cfg is None` inside `call_claude` and `sampling_params_ok` defaults to `True` (§6.1). If this script's hardcoded model were bumped to `claude-sonnet-5`, `temperature=0.7` would still be sent and 400. Dev-only, not live today, but the one place this class of break is still real.

**Not a break — verified safe, unchanged from the prior edition:** `runtime/flows/voice/continuity.py` (routes through `stream_voice_call`, no temperature parameter ever), `voice/step2_validation.py`/`editor/synthesis_router.py`/`voice/step2_first_draft_artifact.py` (no temperature sent at all), `_ct_compress` (thinking=True drops it), every other `thinking=True` `call_claude` site.

### 10.3 Summary punch list

| Migration leg | Breaks (400) | Caught by the loader pre-flight (was: silent break) | Silent behavior change |
|---|---|---|---|
| Opus 4.7 → Opus 5.5 | none in default config; `phase_5_cross_persona_qc.py` if hardcoded to 5.5 | 4 call sites' thinking-off-on-5.5 trap now raises `ModelRoutingError` instead of a runtime 400 (transcription speaker-id/cleaning, voice step2-validation, synthesis-router) | **none possible by accident anymore** — the effort-default drop (formerly the top finding) now requires an explicit, loud config choice (§5.2, §10.1) |
| Sonnet 4.6 → Sonnet 5 | 1 call site: `phase_5_cross_persona_qc.py:_invoke_voice` (bypasses `step=`) | pass_7pre_chunked ×3 + pass_7c fallback — `call_claude`'s `sampling_params_ok` gate now drops their explicit `temperature=0.0` automatically instead of 400ing | none identified |
| Live bug today (pre-migration) | none found | — | — |

Everything routed through `step_config`/`call_claude(step=...)` — which is everything except the two §9 dev scripts — now migrates far more safely than the prior edition's file-by-file literal-hunt implied: model choice is centralized, temperature-sending is model-aware, and the two highest-impact silent risks (effort drop, thinking-disabled-on-5.5) are now hard config-time errors instead of runtime 400s or silent quality regressions. The residual risk is entirely in the two dev/QC scripts that hardcode `model=` directly (§9) — fix those before ever pointing them at a `sampling_params:false` or `thinking_can_disable:false` model.

---

*Regenerated 2026-09-28 from repo state on branch `phase0-fixes`, after the model-config refactor (`f818767`, `8fb718d`, `f5de9db`, tracked as runtime `OPEN_ITEMS.md` C63). `model_routing.json` is the source of truth for current model/thinking/effort defaults — this doc reasons from the loader's actual behavior and each call site's actual code, not from the JSON's contents restated. Verify against `git show`/`git blame` before quoting for budgeting, and re-check §10 against the actual Opus 5.5 / Sonnet 5 API surface at migration time.*
