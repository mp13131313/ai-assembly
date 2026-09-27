# LLM Call Inventory

**Purpose:** Complete enumeration of every model API call made from this repo, with provider, model, parameters, and prompt source. Written against the actual code (not against the spec docs, which drift). This edition exists specifically to support the model-migration decision at `_workspace/planning/runtime/OPEN_ITEMS.md` **C62** (Opus 4.7 → Opus 5.5, Sonnet 4.6 → Sonnet 5) — accuracy per call site is the point; treat prose as secondary.

**Scope:** All LLM / AI API calls initiated by code in this repo — runtime flows (transcription, researcher, provocateur, voice, editor) and the persona pipeline. External-facing manual steps (the human Claude DR sessions at claude.ai) are noted for completeness but are not code-initiated. Ad-hoc dev/QC scripts that fire live calls when run manually are catalogued separately in §9 so they don't get confused with the automated per-night / per-voice pipelines.

**Regenerated: 2026-09-27, from code on branch `phase0-fixes`.** The prior edition (dated against 2026-05-01 code) was stale for everything landed since — principally the entire **Voice Pipeline** (`runtime/flows/voice/**`: Steps 1/2/3, Step 1 + Step 2 validation, continuity) and **Editor Pipeline** (`runtime/flows/editor/**`: routing + synthesis-router, dossier generation, edition, publish), neither of which existed in the repo as of the last regeneration. Those are new major sections below (§2.4, §2.5). Personas-side content has been re-verified line-by-line against current code; a few things the old doc got subtly wrong are corrected in §7 (notably: coherence-threading calls do **not** actually send `temperature: 0.0` — they pass `1.0` but it is dropped by `call_claude` because `thinking=True`, same as every other adaptive-thinking call).

---

## 0. Providers and models at a glance

| Provider | SDK | Models used | Where |
|---|---|---|---|
| Anthropic | `anthropic` Python SDK (`==0.94.1` in both venvs) | `claude-opus-4-7`, `claude-sonnet-4-6` | Everywhere Claude is called (Transcription, Researcher, Provocateur, Voice, Editor, Personas) |
| AssemblyAI | `assemblyai==0.59.0` | `universal-3-pro` | Transcription ASR + diarization |
| Perplexity | Raw HTTP via `requests` | `sonar-deep-research` | Persona Pass 1a |
| Google Gemini | `google-genai==1.73.1` | `gemini-2.5-pro` | Persona Pass 1b, 7-anach/7a/7a-FINAL last-resort fallback, 7c primary; Voice Step 1 validation ladder last resort |
| OpenAI | `openai==2.31.0` Python SDK | `gpt-5.4` (reasoning_effort=high), `gpt-4.1`, `o3`, `gpt-4o` | Persona Pass 7-anachronism / 7a / 7a-FINAL (5-model ladder); Voice Step 1 validation (same ladder, independently implemented) |
| Wikipedia | REST (`requests`) | — | Persona Pass 0a (not LLM; grounding lookup) |

Anthropic dominates call volume and is the entire subject of the C62 migration question. Status check against the live Models API (2026-09-27, per OPEN_ITEMS C62): `claude-opus-4-7` and `claude-sonnet-4-6` are still available, as are `claude-opus-5-5` and `claude-sonnet-5`. Nothing forces a migration; this doc exists to make the tradeoffs legible.

**Every Anthropic call site in the repo, no exceptions found:** no `tool_choice` (forced or otherwise), no `top_p`/`top_k`, no `budget_tokens` actually sent (the string appears only in comments explaining why adaptive mode doesn't need it), and no assistant-turn prefill for generation (the two `role: assistant` messages that exist — `runtime/flows/voice/_anthropic_call.py:45` and `personas/flows/shared/clients.py:41` — are payloads to the free `messages.count_tokens` endpoint for thinking-token telemetry, not prefill on a generation call). This matters directly for C62: the prefill-400 and forced-tool_choice-400 rules do not apply to anything in this repo.

---

## 1. Summary tables — one row per call site

### 1.1 Runtime pipelines

N = expected invocations per Athens-scale night (rough; panel is currently 10 voices per `_workspace/planning/FOLLOW_UPS.md`, ~15-25 sessions/night, ~15-25 themes/night on the researcher side).

| # | Pipeline · Call site | file:function(line) | Model (default → env override) | Streaming | Thinking | Temp actually sent | Structured output |
|---|---|---|---|---|---|---|---|
| R1 | Transcription · ASR | `transcription_flow.py:405 transcribe_with_assemblyai` | AssemblyAI `universal-3-pro` | poll | — | — | — |
| R2 | Transcription · Speaker ID (5-pass) | `transcription_flow.py:471 identify_speakers` → call at `:522` | `TRANSCRIPTION_SPEAKER_ID_MODEL` → `CLAUDE_MODEL` → `claude-sonnet-4-6` | No (`messages.create`) | Off (intentional, §7.7) | **not sent** (no key in request) | JSON-in-text, `extract_json` |
| R3 | Transcription · Cleaning | `transcription_flow.py:546 clean_transcript` → call at `:576` | `TRANSCRIPTION_CLAUDE_MODEL` → `CLAUDE_MODEL` → `claude-sonnet-4-6` | Yes (required, 64K) | Off (intentional) | **not sent** | plain text |
| R4 | Researcher · Extraction | `researcher_flow.py:278 extract_session` → stream at `:314` | `RESEARCHER_CLAUDE_MODEL` → `CLAUDE_MODEL` → `claude-opus-4-7` | Yes | Adaptive (`RESEARCHER_THINKING`, default on) | **not sent** (dropped by design — see code comment at `:130-136`) | JSON-in-text |
| R5 | Researcher · Clustering | `researcher_flow.py:353 cluster_extractions` → stream at `:412` | same | Yes | Adaptive | not sent | JSON-in-text |
| R6 | Researcher · Theming | `researcher_flow.py:482 group_clusters_into_themes` → stream at `:529` | same | Yes | Adaptive | not sent | JSON-in-text |
| R7 | Provocateur · Triage Voice (per-voice) | `provocateur_flow.py:506 triage_voice` → shared helper `_stream_and_parse` (`:369`, stream at `:411`) | `PROVOCATEUR_CLAUDE_MODEL` → `CLAUDE_MODEL` → `claude-opus-4-7` | Yes | Adaptive (`PROVOCATEUR_THINKING`, default on) | not sent | JSON-in-text |
| R8 | Provocateur · Triage Flags | `provocateur_flow.py:582 triage_flags` → same shared helper | same | Yes | Adaptive | not sent | JSON-in-text |
| R9 | Provocateur · Formulation (per-pair) | `provocateur_flow.py:1084 formulate_for_member` → same shared helper | same | Yes | Adaptive | not sent | JSON-in-text |
| V1 | Voice · Step 1 Private Reasoning (per voice×formulation pair) | `voice/step1_private_reasoning.py:148 run_step1_for_pair` → `stream_voice_call` at `:186` | `VOICE_MODEL` → `CLAUDE_MODEL` → `claude-opus-4-7` | Yes | Adaptive, `display:"summarized"` (`VOICE_THINKING`, default on) | **never sent** (`stream_voice_call` never includes a `temperature` key, regardless of `thinking`) | prose + label parse (bookkeeping tail line only) |
| V2 | Voice · Step 2 First-Draft Artifact (per voice) | `voice/step2_first_draft_artifact.py:313 run_step2_for_voice` → `stream_voice_call` at `:355` | same as V1 | Yes | Adaptive, summarized | never sent | prose + regex label parse |
| V2b | Voice · Step 2 synthesis-router (0-2/night, only on ambiguous synthesis) | `voice/step2_first_draft_artifact.py:294` (calls `editor/synthesis_router.py:98 route_synthesis_voice` → `messages.create` at `:125`) | `SYNTHESIS_ROUTER_MODEL` → `claude-sonnet-4-6` | No | Off | never sent (no key in request) | plain-text 2-line label parse |
| V3 | Voice · Step 3 Amended Artifact (per voice) | `voice/step3_amended_artifact.py:214 run_step3_for_voice` → `stream_voice_call` at `:255` | same as V1 | Yes | Adaptive, summarized | never sent | prose + regex label parse |
| V4 | Voice · Step 1 Validation — anachronism (opt-in, off by default; per Step 1 output) | `voice/step1_validation.py:183 check_anachronism` → ladder at `:57 _call_openai_with_fallback` | OpenAI `gpt-5.4`→`gpt-4.1`→`o3`→`gpt-4o`→Gemini `gemini-2.5-pro` (`VOICE_VALIDATION_MODELS`) | No | `reasoning_effort="high"` forced on every ladder rung (see §7.12) | 0.0 on non-reasoning-path rungs only | plain text, `PASS`/other prefix check |
| V5 | Voice · Step 1 Validation — constitution (opt-in, off by default; per Step 1 output) | `voice/step1_validation.py:208 check_constitution` → same ladder | same | No | same | same | same |
| V6 | Voice · Step 2 Validation — Safeguards pillar (default ON; per voice) | `voice/step2_validation.py:129 check_safeguards` → `_call_anthropic` at `:81` (`messages.create` `:90`) | `VOICE_STEP2_VALIDATION_MODEL` → `claude-sonnet-4-6` | No | Off (no `thinking` kwarg at all) | **not sent** | JSON-in-text (fenced or bare) |
| V7 | Voice · Step 2 Validation — Engagement pillar | `voice/step2_validation.py:223 check_engagement` → same `_call_anthropic` | same | No | Off | not sent | JSON-in-text |
| V8 | Voice · Step 2 Validation — Voice-fidelity pillar | `voice/step2_validation.py:280 check_voice_fidelity` → same | same | No | Off | not sent | JSON-in-text |
| V9 | Voice · Step 2 Validation — Cross-night echo (Night 2/3 only, if prior artifact exists) | `voice/step2_validation.py:312 check_cross_night_echo` → same | same | No | Off | not sent | JSON-in-text |
| V10 | Voice · Continuity (per voice, after Step 3 completes) | `voice/continuity.py:136 generate_continuity` → `stream_voice_call` at `:180` | `VOICE_CONTINUITY_MODEL` → `claude-sonnet-4-6` | Yes | Adaptive, summarized (`VOICE_CONTINUITY_THINKING`, default on) | never sent | JSON-in-text (`extract_json`) |
| E1 | Editor · Stage 1 synthesis-router safety net (0-2/night) | `editor/routing.py:211` → `synthesis_router.py:125` | `SYNTHESIS_ROUTER_MODEL` → `claude-sonnet-4-6` | No | Off | never sent | plain-text 2-line label parse |
| E2 | Editor · Stage 2 per-dossier generation (~3-5/night, one per engaged theme) | `editor/dossier_generation.py:541 generate_dossier` → `stream_voice_call` at `:577` | `EDITOR_MODEL` → `CLAUDE_MODEL` → `claude-opus-4-7` | Yes | Adaptive, summarized (`EDITOR_THINKING`, default on) | never sent | prose + regex label parse |

**Not an LLM call (verified — no `Anthropic`/`OpenAI`/`genai` import, no client construction):** `runtime/flows/editor/edition.py` (Stage 3 lead-pick + indices — pure Python), `runtime/flows/editor/publish.py` (pure Python), `runtime/flows/editor/card_assembly.py` (prompt/text assembly only), `runtime/flows/voice/card_assembly.py` (same), `runtime/flows/voice/publish.py` (pure Python), `runtime/flows/voice_flow.py`/`editor_flow.py` orchestrators themselves (they instantiate the `Anthropic` client and pass it down, but the actual `.messages.*` calls live in the modules above), `runtime/scripts/**` (verified — zero LLM-call imports across all 9 scripts).

### 1.2 Persona Pipeline

| # | Pass | file:function(line) | Model (hardcoded unless noted) | Thinking | Temp sent | max_tokens | Structured output | N/voice |
|---|---|---|---|---|---|---|---|---|
| P1 | 0a Voice Config | `run_pass0a_voice_config.py` kwargs `:224`, call via `_call_with_retry`→`call_claude` `:57` | `claude-opus-4-7` | True, adaptive | dropped (thinking=True) | 24000 | JSON-in-text | 1 |
| P2 | 1a Perplexity | `clients.py:269 call_perplexity` | `sonar-deep-research` (env `PERPLEXITY_MODEL`) | — | 0.0 sent (REST body) | — (no cap) | prose, `<think>` stripped | 1 |
| P3 | 1b Gemini broad scan | `clients.py:345 call_gemini` | `gemini-2.5-pro` (env `GEMINI_MODEL`) | model-forced on | 0.2 sent | 16384 | prose | 1 |
| P4 | 0b tailor | `run_pass_0b_tailor.py:236` | `claude-opus-4-7` | True, adaptive | dropped | 16000 | JSON-in-text | 1 |
| P5-10 | 1.1-1.6 chunked merge | `flows/shared/chunk_runner.py:315` (`call_kwargs` built `:302-309`) | `claude-opus-4-7` (hardcoded, no env override) | True, adaptive | dropped | 48000 | Pydantic-validated JSON | 1 each (6 total, parallel ×3) |
| P11 | 1.7 Coherence audit | `run_pass_1_7.py` `call_kwargs` `:479-486`, call `:491` | `claude-opus-4-7` | True, adaptive | dropped | 24000 | Pydantic-validated JSON | 1 |
| P12 | 1d Excerpt Selection | `run_persona_pipeline.py:544 _pass_1d` → call `:592` | `claude-opus-4-7` | True, adaptive | `temperature=None` passed (moot) | 16000 | JSON-in-text | 1 (skipped if no primary texts) |
| P13 | 2 Identity & Boundaries | `run_persona_pipeline.py:484 _pass_2` → `_claude_pass` helper `:437` → call `:501` | `claude-opus-4-7` | True (helper default), adaptive | dropped | 32000 | JSON-in-text | 1 |
| P14 | CT after Pass 2 | `run_persona_pipeline.py:456 _ct_compress` → call `:475` | `claude-sonnet-4-6` (hardcoded) | **True**, adaptive (see §7.1 correction) | dropped — code passes `1.0` but it never reaches the API | 16000 | plain text | 1 |
| P15 | 3 Intellectual Core | `run_persona_pipeline.py:511 _pass_3` → `_claude_pass` `:530` | `claude-opus-4-7` | True, adaptive | dropped | 32000 | JSON-in-text | 1 |
| P16 | CT after Pass 3 | same `_ct_compress` | `claude-sonnet-4-6` | True, adaptive | dropped | 16000 | plain text | 1 |
| P17 | 4a Voice | `run_persona_pipeline.py:668 _pass_4a` → `_claude_pass` `:692` | `claude-opus-4-7` | True, adaptive | dropped | 24000 | JSON-in-text | 1 |
| P18 | CT after Pass 4a | same `_ct_compress` | `claude-sonnet-4-6` | True, adaptive | dropped | 16000 | plain text | 1 |
| P19 | 4b Artifact | `run_persona_pipeline.py:705 _pass_4b` → `_claude_pass` `:722` | `claude-opus-4-7` | True, adaptive | dropped | 24000 | JSON-in-text | 1 |
| P20 | CT after Pass 4b | same `_ct_compress` | `claude-sonnet-4-6` | True, adaptive | dropped | 16000 | plain text | 1 |
| P21 | 5 Engagement | `run_persona_pipeline.py:734 _pass_5` → `_claude_pass` `:755` | `claude-opus-4-7` | True, adaptive | dropped | 16000 | JSON-in-text | 1 |
| P22 | 6 Corpus Curation | `run_persona_pipeline.py:765 _pass_6` → `_claude_pass` `:802` | `claude-opus-4-7` | True, adaptive | dropped | 24000 | JSON-in-text | 1 (HALTS if no primary texts) |
| P23 | 7-pre Stage 1 extract | `flows/shared/pass_7pre_chunked.py` call `:88` | `_EXTRACT_MODEL = "claude-sonnet-4-6"` (hardcoded, no env) | **False** | **0.0 sent** | 32000 | JSON-in-text | 1 |
| P24 | 7-pre Stage 2 verify (N batches, ~25 claims each, ≤4 parallel) | `pass_7pre_chunked.py` call `:133` | `_VERIFY_MODEL = "claude-sonnet-4-6"` | **False** | **0.0 sent** | 16000 | JSON-in-text | N≈3-6 |
| P25 | 7-pre Stage 3 boddice check | `pass_7pre_chunked.py` call `:273` | `_BODDICE_MODEL = "claude-sonnet-4-6"` | **False** | **0.0 sent** | 8000 | JSON-in-text | 1 |
| P26a | 7-anachronism (5-model ladder) | `run_persona_pipeline.py:1037 _pass_7_anachronism` → `call_openai` `:1064`, `call_gemini` `:1075` | `gpt-5.4`(high)→`gpt-4.1`→`o3`→`gpt-4o`→`gemini-2.5-pro` | OpenAI: `reasoning_effort` per model; Gemini: model-forced | OpenAI reasoning path: omitted; non-reasoning rungs 0.0; Gemini 0.0 | 16384 | JSON-in-text | 1 (1-5 attempts) |
| P27a | 7a Cross-Model (same ladder) | `run_persona_pipeline.py:1102 _pass_7a` → calls `:1119`, `:1131` | same ladder | same | same | 16384 | JSON-in-text | 1 (1-5 attempts) |
| P28 | 7a-FIX linear patcher | `run_persona_pipeline.py:1300 _pass_7a_fix` → call `:1424` | `claude-opus-4-7` | True, adaptive | dropped | 32000 | JSON-in-text | 0 or 1 |
| P29 | 7b Worked Provocations | `run_persona_pipeline.py:1571 _pass_7b` → `_claude_pass` `:1580` | `claude-opus-4-7` | True, adaptive | dropped | 24000 | JSON-in-text | 1 |
| P30a | 7c Negative Constraints — Gemini primary | `run_persona_pipeline.py:1594 _pass_7c` → `call_gemini` `:1607` | `gemini-2.5-pro` | model-forced | 0.0 sent | 16384 | JSON-in-text | 1 |
| P30b | 7c fallback | same function, call `:1618` | `claude-sonnet-4-6` | **False** | **0.0 sent** | 8192 | JSON-in-text | only if Gemini fails |
| P31a | 7a FINAL post-assembly (5-model ladder) | `run_persona_pipeline.py:1921 _pass_7a_final` → calls `:1963`, `:1975` | same ladder as P26/P27 | same | same | 16384 | JSON-in-text | 1 (1-5 attempts; re-fires on operator-patch loop) |
| P32 | Derive | `run_persona_pipeline.py:2043 _derive` → call `:2070` | `claude-opus-4-7` | True, adaptive | dropped | 24000 | JSON-in-text | 1 |
| P32' | Derive (path-b fast exit, mutually exclusive with P32) | `run_persona_pipeline.py:913 _derive_fast` (inline dup of P32) → call `:926` | `claude-opus-4-7` | True, adaptive | dropped | 24000 | JSON-in-text | 0 or 1 |

Pure-Python / non-LLM personas steps (confirmed by import-grep, unchanged from before): Pass 0b base render (Jinja2), split tailored prompt, Pass 1c-extract (`url_extract.py`), Pass 1c fetch, Pass 6.5-clean (`bracket_strip.py`), FU#33 P2 INCONSISTENT merge, path-to-pass mapping, card assembly, chat artifact (`chat_prompt_builder.py`), Wikipedia REST. Also verified pure-Python with no LLM imports: `dr_validation.py`, `research_validation.py`, `node0_validation.py`, `node1d_excerpt_selection.py`, `node1c_fetch.py`.

---

## 2. Runtime pipeline calls (detail)

### 2.1 Transcription — `runtime/flows/transcription_flow.py`

Function names current as of this read: `transcribe_with_assemblyai` (:405), `identify_speakers` (:471, 5-pass Speaker ID), `clean_transcript` (:546). Unchanged in substance from the prior edition:

- **Speaker ID** (`:522` `client.messages.create`): model resolves `TRANSCRIPTION_SPEAKER_ID_MODEL` → `CLAUDE_MODEL` → `claude-sonnet-4-6`; `max_tokens=4096`; system wrapped in `cache_control` (ephemeral, C19c); **no `temperature` key in the request at all** (not "SDK default 1.0 sent" — literally absent); no `thinking` kwarg either. Comment at `:80` explicitly documents overriding to `claude-opus-4-7` for hard sessions "for difficult sessions where the extra reasoning capacity helps" — if this override is exercised, thinking stays off by design (§7.7), which is fine on Opus 4.7 today but **would 400 on Opus 5.5** (thinking cannot be disabled there).
- **Cleaning** (`:576` `client.messages.stream`, required — max_tokens 64000 exceeds the SDK's non-streaming estimate threshold): model resolves `TRANSCRIPTION_CLAUDE_MODEL` → `CLAUDE_MODEL` → `claude-sonnet-4-6`; same no-temperature, no-thinking pattern; system cache-wrapped.

### 2.2 Researcher — `runtime/flows/researcher_flow.py`

`_thinking_kwargs(budget_tokens)` at `:116` returns `{"thinking": {"type": "adaptive", "display": "summarized"}}` when `RESEARCHER_THINKING != "0"` (default on), else `{}`. The `budget_tokens` argument is accepted for API symmetry but never used (adaptive ignores it) — confirms no `budget_tokens` is ever sent. No call in this file passes `temperature` under any circumstance; the docstring at `:130-136` explicitly cites "Opus 4.7 returns 400 BadRequestError if `temperature` is set on a thinking call" as the reason it's omitted outright, rather than conditionally dropped like the personas wrapper does.

- `extract_session` (:278, stream :314): `RESEARCHER_CLAUDE_MODEL`→`CLAUDE_MODEL`→`claude-opus-4-7`, `max_tokens=40000`, system cache-wrapped (ephemeral).
- `cluster_extractions` (:353, stream :412): same model resolution, `max_tokens=64000` (raised from 40000 on 2026-05-08 after Athens Night 1 hit the ceiling on 215 extractions — see inline comment `:100-104`). Deterministic shuffle seed 42; inputs deliberately minimal (`{ref, extraction, context}` only).
- `group_clusters_into_themes` (:482, stream :529): `max_tokens=24000`; cluster-level inputs only.
- `RESEARCHER_NODE1_BATCH` (default 6) parallelizes `extract_session` calls via `ThreadPoolExecutor` (C25, 2026-05-04).

### 2.3 Provocateur — `runtime/flows/provocateur_flow.py`

All three LLM tasks funnel through one shared helper, `_stream_and_parse` (:369-462), which is the single Anthropic call site (`client.messages.stream` at `:411`) for the whole pipeline. Model: `PROVOCATEUR_CLAUDE_MODEL`→`CLAUDE_MODEL`→`claude-opus-4-7`. Thinking: `_thinking_kwargs()` at `:134`, same adaptive+summarized shape, gated on `PROVOCATEUR_THINKING` (default on). No `temperature` key ever constructed or passed — `_stream_and_parse` has no temperature parameter at all.

- `triage_voice` (:506, `max_tokens=40000`): per-voice ranking, ~10-25 calls/night depending on panel size. `cache_system=True` (C19c) — voice profile moved out of system into the user message so the system prompt is now identical across all voices' triage calls, so calls 2-N hit cache.
- `triage_flags` (:582, same max_tokens): single post-aggregation call, `cache_system=False`.
- `formulate_for_member` (:1084, same max_tokens): per-pair, `cache_system=True` (C19a) — batched via `PROVOCATEUR_FORMULATION_BATCH` (default 4) with `PROVOCATEUR_BATCH_WAIT_S` (default 20) between batches.
- `python_select` (:640) and `package_voice_briefings` (:1222) are pure-Python (Stage 2 selection, Stage 4 packaging) — no LLM.

### 2.4 Voice Pipeline — `runtime/flows/voice/**` (NEW since last edition)

All streaming calls in this pipeline funnel through one shared helper, **`stream_voice_call`** (`runtime/flows/voice/_anthropic_call.py:55-174`), used identically by Steps 1/2/3, Continuity, and (via reuse) the Editor's dossier generation. Its defining property for migration purposes: **it never constructs or sends a `temperature` key, under any configuration** — the `client.messages.stream(...)` call at `:129` passes only `model`, `max_tokens`, `system`, `messages`, and `**thinking_kwargs`. This makes every one of its callers immune to the temperature-400 risk regardless of which model they resolve to.

`stream_voice_call` also implements the shared 1-retry-on-any-exception policy (5s backoff, `:126-172`) and the prompt-caching scheme: a `(prefix, tail)` tuple system prompt gets `cache_control: {"type": "ephemeral", "ttl": "1h"}` on **both** blocks so Steps 1/2/3 for the same voice/night share a cache-read; a plain-string system gets one breakpoint; `cache_system=False` (used by Continuity) disables caching outright because a single-call flow pays the 2× cache-write premium with no reads to amortize it. It also computes `thinking_tokens` via subtraction against the free `messages.count_tokens` endpoint (`:29-52`) — this is the source of the two `role: assistant` messages noted in §0; it is telemetry, not prefill.

#### 2.4.1 Step 1 — Private Reasoning (`voice/step1_private_reasoning.py`)

`run_step1_for_pair` (:148), call at `:186`. One call per (voice, formulation) pair — this is the largest-volume Voice call site (roughly one per Provocateur-Formulation output, i.e. the same N≈"formulations per night" as Provocateur R9 above). `VOICE_MODEL`→`CLAUDE_MODEL`→`claude-opus-4-7`; `thinking_kwargs()` (:51-74) is `{"thinking": {"type": "adaptive", "display": "summarized"}}` when `VOICE_THINKING` (default on), else `{}`; `max_tokens` from `VOICE_STEP1_MAX_TOKENS` (default 64000). Output is prose; the only structured extraction is a regex-stripped bookkeeping tail line (`extractions_engaged: id1, id2, ...`) via `_extract_engaged_tail` (:83-126), falling back to the briefing's `grounding_extraction_ids` if unparseable.

Batched by `voice_flow.py` via `_run_step1_batch` (:166) at `VOICE_STEP1_BATCH` (default 6) concurrency, `VOICE_BATCH_WAIT_S` (default 5) between batches.

#### 2.4.2 Step 2 — First-Draft Artifact (`voice/step2_first_draft_artifact.py`)

`run_step2_for_voice` (:313), call at `:355`. One call per voice per night. Same model/thinking/max_tokens resolution pattern (`VOICE_STEP2_MAX_TOKENS`, default 64000). Output is prose parsed by label regex (`_parse_step2_output`, :72-165) into `weight_assessment`/`focus_decision`/`stance`/`selected_form`/`artifact_text` etc.; `themes_covered` is derived deterministically, not asked of the model (:168-195).

**Embedded synthesis-router call** (`_resolve_primary_theme_id`, :210-310): when `focus_decision` names a specific "Response N" or is a single-response session, resolution is pure Python. When the voice's own words indicate synthesis across themes (`_SYNTHESIS_MARKERS` match) and there's more than one candidate, it calls `editor/synthesis_router.route_synthesis_voice` (imported at `:266`) using the same `Anthropic()` client instance Step 2 already created — this is call site V2b / E1's shared implementation (see §2.5.1). Fires 0-2 times per night per the module's own cost-envelope comment.

#### 2.4.3 Step 3 — Amended Artifact (`voice/step3_amended_artifact.py`)

`run_step3_for_voice` (:214), call at `:255`. One call per voice per night, runs after **all** voices complete Step 2 (cross-voice read). `VOICE_STEP3_MAX_TOKENS` default 64000; same model/thinking pattern. Per the orchestrator's default (`skip_step3: bool = False` in `voice_flow.py:348`), Step 3 **runs by default** in the current code — note this against the CLAUDE.md-era claim that Step 3 was skipped for Athens production; that was a time-bound production decision (OPEN_ITEMS A1, `--skip-step3` flag), not the code's current default.

#### 2.4.4 Voice Step 1 Validation — `voice/step1_validation.py` (opt-in, **off by default**)

**This is the one place where the file's own docstring is stale relative to the code.** The module docstring (`:1-25`) still says "Default policy: Athens Night 1 ON; Night 2/3 ON for voices flagged on prior nights." The orchestrator disagrees: `voice_flow.py:348` sets `skip_validation: bool = True` with an explicit comment — *"C28 (2026-05-04): default-OFF — Step 1 validation has no actionable consumer; replaced by C28b Step 2 validator"* — and the CLI (`voice_flow.py:696-699`) only re-enables it via `--enable-step1-validation`. Treat the docstring as historical, the orchestrator default as current truth.

When it does run: two checks per Step 1 output, `check_anachronism` (:183) and `check_constitution` (:208), each calling `_call_openai_with_fallback` (:57-127) — an **independently-implemented** copy of the same OpenAI/Gemini fallback ladder used by Personas Pass 7-anachronism/7a (`_DEFAULT_LADDER = ("gpt-5.4", "gpt-4.1", "o3", "gpt-4o", "gemini-2.5-pro")`, override via `VOICE_VALIDATION_MODELS`). **Documentation note, not an Anthropic-migration issue but worth recording for accuracy:** both callers pass `reasoning_effort="high"` unconditionally (`:196`, `:218`); inside the ladder helper, `use_reasoning = is_o_series or reasoning_effort is not None` (`:93`) is then `True` for every rung including `gpt-4.1` and `gpt-4o`, which are not reasoning models — so those rungs get routed onto the `max_completion_tokens` + `reasoning_effort` code path rather than the plain `temperature=0.0` path the ladder's own `else` branch was clearly written for. This is pre-existing OpenAI-side behavior, out of scope for C62, flagged here only because the task asked for exact per-call-site fidelity.

#### 2.4.5 Voice Step 2 Validation — `voice/step2_validation.py` (default **ON**)

Three pillars always, a fourth conditionally, each **its own separate non-streaming Anthropic call** through one shared helper `_call_anthropic` (:81-103, `client.messages.create` at `:90`). This is a distinct wrapper from `stream_voice_call` — worth noting because it means Voice Step 2 Validation's temperature/thinking behavior has to be checked independently rather than inherited: **no `thinking` key, no `temperature` key** are ever constructed in `_call_anthropic`'s `resp = client.messages.create(model=..., max_tokens=..., system=..., messages=...)` call. Model: `VOICE_STEP2_VALIDATION_MODEL`→`claude-sonnet-4-6`; `max_tokens=4096` (`VOICE_STEP2_VALIDATION_MAX_TOKENS`).

- `check_safeguards` (:129) — AI-self-acknowledgment / defamation / `topics_requiring_care` / `hard_limits` / `banned_modes` / AI-slop subset of `banned_language`.
- `check_engagement` (:223) — form fidelity + grounding fidelity (LLM) + mechanical length compliance (`_check_length_compliance`, :181, pure Python, no LLM).
- `check_voice_fidelity` (:280) — `characteristic_moves` + `quality_criteria`.
- `check_cross_night_echo` (:312) — Night 2/3 only, gated on a prior published artifact existing (`_load_prior_artifact`, :374).

Run in parallel per voice via `ThreadPoolExecutor(max_workers=STEP2_VALIDATION_PILLAR_BATCH)` (default 6) inside `run_step2_validation` (:401). Orchestrator gate: `step2_validate: bool = True` default in `voice_flow.py:349`, disable via `--skip-step2-validation`. Halt-on-any-flag is an **operator gate**, not an auto-regen mechanism (design principle per OPEN_ITEMS C28b) — this is unlike every other validator in the repo, which either auto-fixes (Pass 7a-FIX) or is diagnostic-only.

Per-night volume: 3 pillars × N voices (Night 1), 4 × N voices (Night 2/3, cross-night echo added) — e.g. ~30-40 Sonnet calls/night at a 10-voice panel.

#### 2.4.6 Continuity — `voice/continuity.py`

`generate_continuity` (:136), call at `:180`. One call per voice, fires after Night N's Step 3 completes, writes the override consumed by Night N+1. `VOICE_CONTINUITY_MODEL`→`claude-sonnet-4-6`; thinking adaptive+summarized by default (`VOICE_CONTINUITY_THINKING`); `max_tokens` from `VOICE_CONTINUITY_MAX_TOKENS` (default 8000); `cache_system=False` explicitly (single-call flow, cache-write penalty isn't amortized). Output parsed via `extract_json` for two prose fields (`continuity_block_if_night_N+1`, `continuity_block_artifact_if_night_N+1`) plus a `signature_moves_deployed_last_night` array that gets accumulated across nights (:213-238).

### 2.5 Editor Pipeline — `runtime/flows/editor/**` (NEW since last edition)

`editor_flow.py` (:38-348) is the orchestrator. One `Anthropic()` client is instantiated once (`:152-153`) and shared across Stage 1's synthesis-router safety net and every Stage 2 dossier call (the SDK is thread-safe with internal pooling, per the inline comment).

#### 2.5.1 Stage 1 — Routing (`editor/routing.py`) — mostly pure Python, one conditional LLM call

Theme routing itself (Cases A/B/C/D on `focus_decision`) is deterministic Python. The one LLM call, `route_synthesis_voice` (`editor/synthesis_router.py:98-164`), fires as a **safety net** at `routing.py:211` for any voice whose `lineage.primary_theme_id` is still null after Step 2's own attempt (§2.4.2) — same function, same model, so it never double-charges a voice that Step 2 already resolved. `SYNTHESIS_ROUTER_MODEL`→`claude-sonnet-4-6`; `client.messages.create` at `synthesis_router.py:125` — **no `temperature`, no `thinking` key** in the request; `max_tokens=500` (`SYNTHESIS_ROUTER_MAX_TOKENS`). Output is a fixed 2-line label format (`chosen_theme_id:` / `rationale:`), parsed by regex; on any failure (API error, unparseable, or the model naming a theme_id outside the candidate list) it falls back to the lowest-numbered candidate rather than dropping the voice.

`gating_status` (`routing.py:280`) — pure Python; Stage 0 of `editor_flow.py` refuses to proceed if any voice with a Step 2 artifact lacks either a PASS validation verdict or an explicit operator decision.

#### 2.5.2 Stage 2 — Per-dossier generation (`editor/dossier_generation.py`)

`generate_dossier` (:541), call via `stream_voice_call` at `:577` (same shared helper as Voice — see §2.4 preamble, so again **no `temperature` ever sent**). One call per engaged theme per night; `editor_flow.py`'s own docstring estimates 3-5 dossiers/night. `EDITOR_MODEL`→`CLAUDE_MODEL`→`claude-opus-4-7`; `EDITOR_THINKING` (default on) → adaptive+summarized; `max_tokens` from `EDITOR_MAX_TOKENS` (default 32000). System prompt is a `(prefix, tail)` tuple from `card_assembly.assemble_system_prompt` (`editor/card_assembly.py:286`) — identical prefix across all of a night's dossier calls, so calls 2-N hit the 1h prefix cache. Calls run in parallel via `ThreadPoolExecutor(max_workers=EDITOR_BATCH)` (default 6, `editor_flow.py:232`). Output is prose, parsed by `parse_dossier_output` (`dossier_generation.py:384-409`) into `kicker`/`headline`/`body_paragraphs[]`/`headnotes[]` etc.

#### 2.5.3 Stage 3 — Edition (`editor/edition.py`) and Publish (`editor/publish.py`, `voice/publish.py`)

Confirmed pure Python — no `Anthropic`/`client`/`openai`/`genai` reference anywhere in any of these three files. `finalize_edition` (called from `editor_flow.py:258`) does lead-theme picking and index-writing algorithmically, not via an LLM call. **Both `editor/edition.py` and `voice/publish.py` are being edited concurrently by another agent as of this regeneration** — they were read-only inspected here to confirm they carry no LLM call sites, not modified, and this doc doesn't depend on their current diff (nothing in them is call-site-relevant).

---

## 3. Persona Pipeline calls (detail)

This section is materially the same pipeline as the prior edition (Phase 0 intake → Phase 0.5 pre-DR research → Phase 0.7 manual DR → Phase 1 chunked merge → Phase 2 section generation → Phase 2.5 cleanup → Phase 3 validation → Phase 4 derive), re-verified line-by-line. Rather than restate every prompt-file/schema mapping from the previous edition (still structurally accurate), this section calls out what changed or was corrected on re-verification; §1.2's table has the authoritative per-call-site line numbers.

**Confirmed unchanged in substance:** Pass 0a, 1a/1b parallel research, 0b tailor, chunked merge 1.1-1.7 (via `chunk_runner.py` / `run_pass_1_7.py`), Pass 1c (pure Python), Pass 1d, Pass 2/3/4a/4b/5/6 (all via the `_claude_pass` helper at `run_persona_pipeline.py:437`, all `claude-opus-4-7` + adaptive thinking), Pass 6.5-clean (pure Python), Pass 7-pre 3-stage chunked (`pass_7pre_chunked.py`), Pass 7-anachronism / 7a / 7a-FINAL (5-model ladder, `_pass_7_anachronism`/`_pass_7a`/`_pass_7a_final`), Pass 7a-FIX linear patcher, Pass 7b, Pass 7c (Gemini-primary/Sonnet-fallback), Derive, chat artifact (pure Python).

**Corrected on re-verification:**

1. **CT (coherence-threading) compression temperature — the old doc was wrong.** `_ct_compress` (`run_persona_pipeline.py:456`) calls `call_claude(..., model="claude-sonnet-4-6", max_tokens=16000, temperature=1.0, thinking=True)` (`:475-476`). Because `thinking=True`, `call_claude`'s own logic (`clients.py:122`, `if temperature is not None and not thinking:`) **drops temperature from the request entirely** — it is never sent, at any value. The prior inventory's summary table listed CT calls as sending `temperature: 0.0`, which was never true; the code passes `1.0` (required-by-convention for thinking calls per the inline comment) and it's discarded before the API call is made either way. Net effect for migration purposes: CT calls carry zero temperature risk on Sonnet 5, same as everything else with `thinking=True`.
2. **Two Derive implementations, not one.** The canonical `_derive()` (`:2043`, call `:2070`) runs in the normal pipeline path. A second, functionally-identical inline copy, `_derive_fast()` (`:913`, call `:926`), exists only inside the "PATH-(b) DERIVE-ONLY FAST EXIT" branch (`:898-911`) — taken when an operator has already accepted the assembled card and only a fresh Derive is needed (surgical patches make the old one stale). The two never both fire in the same run; both share identical model/thinking/temperature/max_tokens config, so they're one logical call site for migration purposes.
3. **Function names in `run_persona_pipeline.py` moved since the last regeneration** — line numbers in the old doc (e.g. "Pass 4a at L668-700ish") are close but the exact call-site lines shifted; §1.2 above has current numbers as of this read.

**Not re-verified in full depth this pass (unchanged structurally, low migration relevance):** the exact prompt-file inventory (§4 below carries it forward), the manifest-recording gap (§7.8 in the old doc — `chunk_runner.py` passes `slug`/`pass_name` telemetry kwargs, `run_persona_pipeline.py` calls mostly don't), and `paths.merge_chunk()` dead code (old §7.9).

---

## 4. Prompt file inventory

Unchanged in location/shape from the prior edition; carried forward for completeness rather than re-verified word-for-word (prompt *content* doesn't bear on the C62 migration question — model/parameter compatibility does).

### 4.1 Runtime prompts — `runtime/flows/shared/prompts/`

Speaker ID / Cleaning / Researcher (extraction/clustering/theming) / Provocateur (triage voice/flags/formulation) prompts as before, plus **new since last edition**: `voice_step1_*.md`, `voice_step2_artifact.md`, `voice_step3_amendment.md`, `voice_step1_validation_anachronism.md`, `voice_step1_validation_constitution.md`, `voice_step2_validation_{safeguards,engagement,voice_fidelity,cross_night_echo}.md`, `voice_continuity.md`, `editor_dossier.md` (per `dossier_generation.py:23`, still v1-shaped pending the v2 closing-prompt rewrite tracked at OPEN_ITEMS B1 — this affects prose quality/parseability, not model compatibility).

### 4.2 Personas prompts — `personas/flows/shared/prompts/`

~50 files, Jinja2, loaded via `flows/shared/io.load_prompt()` — structure unchanged from the prior edition's table (Pass 0a through Derive, all system/user pairs as previously catalogued). Not re-transcribed here; see prior edition or `personas/flows/shared/prompts/` directly if the file listing itself is needed.

---

## 5. Environment variables that affect LLM call behavior

### 5.1 Runtime

| Variable | Default | Effect |
|---|---|---|
| `ANTHROPIC_API_KEY` | — | Required. |
| `ASSEMBLYAI_API_KEY` | — | Required. |
| `CLAUDE_MODEL` | Sonnet in transcription, Opus elsewhere | Shared fallback. Transcription default `claude-sonnet-4-6`; Researcher/Provocateur/Voice/Editor default `claude-opus-4-7`. |
| `TRANSCRIPTION_CLAUDE_MODEL` | `CLAUDE_MODEL` | Cleaning override. |
| `TRANSCRIPTION_SPEAKER_ID_MODEL` | `CLAUDE_MODEL` | Speaker ID override — flip to Opus for hard sessions; thinking stays off either way (§7.7; **breaks on Opus 5.5**, see §10). |
| `RESEARCHER_CLAUDE_MODEL` / `PROVOCATEUR_CLAUDE_MODEL` | `CLAUDE_MODEL` | Per-flow override. |
| `RESEARCHER_THINKING` / `PROVOCATEUR_THINKING` | `"1"` (on) | `"0"` disables adaptive thinking. |
| `PROVOCATEUR_FORMULATION_BATCH` / `PROVOCATEUR_BATCH_WAIT_S` | `4` / `20` | Formulation batching. |
| `VOICE_MODEL` | `CLAUDE_MODEL` → `claude-opus-4-7` | Steps 1/2/3 model. |
| `VOICE_THINKING` | `"1"` (on) | Gates adaptive thinking for Steps 1/2/3. |
| `VOICE_STEP{1,2,3}_MAX_TOKENS` | `64000` each | Per-step ceiling. |
| `VOICE_STEP{1,2,3}_BATCH` / `VOICE_CONTINUITY_BATCH` | `6` each | Concurrency caps. |
| `VOICE_BATCH_WAIT_S` | `5` | Wait between Step 1 batches. |
| `VOICE_VALIDATION_MODELS` | `gpt-5.4,gpt-4.1,o3,gpt-4o,gemini-2.5-pro` | Step 1 validation ladder (opt-in feature, off by default — §2.4.4). |
| `VOICE_VALIDATION_MAX_TOKENS` | `8192` | Step 1 validation cap. |
| `VOICE_CONTINUITY_MODEL` | `claude-sonnet-4-6` | Continuity model. |
| `VOICE_CONTINUITY_THINKING` | `"1"` (on) | Continuity thinking gate. |
| `VOICE_CONTINUITY_MAX_TOKENS` | `8000` | Continuity cap. |
| `VOICE_STEP2_VALIDATION_MODEL` | `claude-sonnet-4-6` | All 4 Step 2 validation pillars. |
| `VOICE_STEP2_VALIDATION_MAX_TOKENS` | `4096` | Per-pillar cap. |
| `VOICE_STEP2_VALIDATION_PILLAR_BATCH` | `6` | Pillar concurrency. |
| `SYNTHESIS_ROUTER_MODEL` | `claude-sonnet-4-6` | Shared by Voice Step 2's embedded call and Editor Stage 1's safety net. |
| `SYNTHESIS_ROUTER_MAX_TOKENS` | `500` | Router cap. |
| `EDITOR_MODEL` | `CLAUDE_MODEL` → `claude-opus-4-7` | Dossier generation model. |
| `EDITOR_THINKING` | `"1"` (on) | Dossier thinking gate. |
| `EDITOR_MAX_TOKENS` | `32000` | Dossier cap. |
| `EDITOR_BATCH` | `6` | Dossier-call concurrency. |
| `AI_ASSEMBLY_PROJECT_ROOT` | — | Tier 3 PROJECT_ROOT resolution. |

### 5.2 Personas

| Variable | Default | Effect |
|---|---|---|
| `ANTHROPIC_API_KEY` / `PERPLEXITY_API_KEY` / `GOOGLE_API_KEY` / `OPENAI_API_KEY` | — | Required per provider used. |
| `CLAUDE_MODEL` | `claude-opus-4-7` | Read by `call_claude` only when the caller's `model` arg is `None` — in practice almost every v4 pass hardcodes its model string directly (see §1.2), so this env var has little live effect except on Pass 0a/0b-tailor/chunk_runner/1.7/1d/2/3/4a/4b/5/6/7b/7a-FIX/Derive if their hardcoded `model="claude-opus-4-7"` literals were ever changed to `model=None`. Currently every one of those call sites hardcodes the string, so **this env var does not currently control the Opus call sites** despite being documented as if it does. |
| `PERPLEXITY_MODEL` | `sonar-deep-research` | — |
| `GEMINI_MODEL` | `gemini-2.5-pro` | — |
| `OPENAI_MODEL` | `gpt-4o` | Overridable default, but Pass 7-anach/7a/7a-FINAL and Voice Step 1 validation all hardcode their own 5-rung ladders, bypassing this var entirely. |

---

## 6. Shared wrapper behavior

### 6.1 `call_claude` — `personas/flows/shared/clients.py:78-264`

The persona pipeline's only Claude wrapper.

- **Model resolution:** `model or os.environ.get("CLAUDE_MODEL", "claude-opus-4-7")` (`:101`) — but as noted in §5.2, essentially every caller passes an explicit `model=`, so this fallback rarely engages.
- **Temperature policy** (`:110-123`, FU#60 2026-04-29): `if temperature is not None and not thinking: kwargs["temperature"] = temperature`. Default `temperature: float | None = 0.2` (`:84`). So: **thinking=True → temperature never sent, regardless of value**; **thinking=False → whatever `temperature` was passed (or the 0.2 default) is sent as-is.** This is the one branch in the whole repo where a call site's model/thinking/temperature combination has to be checked together rather than assumed safe — see §10 for the exhaustive per-site check.
- **Thinking:** `thinking=True` → `kwargs["thinking"] = {"type": "adaptive", "display": "summarized"}` (`:135`). No `budget_tokens` in any code path.
- **Streaming heuristic:** `use_streaming = max_tokens >= 16384 or thinking` (`:140`) — matches the SDK's own non-streaming timeout-estimate cutoff. Includes a 1-retry-with-15s-backoff on `httpx.RemoteProtocolError`/`ReadError`/`ReadTimeout` (`:157-176`, added 2026-04-30 after empirically-attested stream drops on large-corpus voices).
- **Structured output:** `response_format_json=True` strips ```` ```json ```` fences then `json.loads`; on `JSONDecodeError` with `stop_reason == "max_tokens"` raises blaming the budget, otherwise re-raises with diagnostics (`:244-261`).
- **Manifest recording:** only when `slug` + `pass_name` are passed (`:48-73`) — `chunk_runner.py` and `pass_7pre_chunked.py` pass them; most `run_persona_pipeline.py` call sites do not (carried-forward gap, §3).

### 6.2 `stream_voice_call` — `runtime/flows/voice/_anthropic_call.py:55-174`

Shared by Voice Steps 1/2/3, Continuity, and Editor Stage 2. See §2.4 preamble for the full behavior. The critical difference from `call_claude`: **it has no temperature parameter of any kind** — not conditionally dropped, structurally absent from the function signature and the `client.messages.stream(...)` call. This makes the entire Voice + Editor call surface immune to the temperature-400 class of migration break regardless of model choice; the only exposure for that surface is the thinking-related ones (§10).

### 6.3 `_stream_and_parse` — `runtime/flows/provocateur_flow.py:369-462`

Provocateur's equivalent shared helper. Same no-temperature-parameter property as `stream_voice_call` (it has no `temperature` kwarg either). Adds the empty-text-stream and JSON-parse-failure diagnostics described in §2.3, plus per-result usage/cache-token stamping (C37).

### 6.4 `_call_anthropic` — `runtime/flows/voice/step2_validation.py:81-103`

Non-streaming, single-purpose helper for the four Step 2 validation pillars. `client.messages.create(model=..., max_tokens=..., system=..., messages=...)` — no `thinking`, no `temperature` key constructed anywhere in the function. Structurally the safest call site in the repo for migration purposes since it sends nothing that any target model rejects.

### 6.5 `call_perplexity` / `call_gemini` / `call_openai` — `personas/flows/shared/clients.py`

Unchanged from the prior edition. `call_openai` (`:401-473`) auto-detects reasoning models (`o1`/`o3`/`o4`/`gpt-5.4` prefixes, or explicit `reasoning_effort`) and switches to `max_completion_tokens` + drops `temperature` + forwards `reasoning_effort`; `runtime/flows/voice/step1_validation.py:_call_openai_with_fallback` reimplements this same logic independently (not imported from `clients.py`) with the `reasoning_effort`-always-passed nuance noted in §2.4.4.

---

## 7. Historical + newly-found parameter notes

Carrying forward only the still-relevant items from the prior edition's §7, plus what this regeneration found:

1. **CT temperature — see §3, correction 1.** The old doc's claim that CT calls send `temperature: 0.0` was never accurate; corrected here.
2. **Voice Step 1 Validation docstring vs. orchestrator default — see §2.4.4.** Docstring says default-on; `voice_flow.py`'s actual default is off (C28, 2026-05-04). This is the one place in the repo where a module's own header comment is stale relative to the orchestrator that drives it.
3. **`CLAUDE_MODEL` env var is mostly decorative for personas Opus calls — see §5.2.** Nearly every Opus-targeting call site in `run_persona_pipeline.py`, `chunk_runner.py`, `run_pass_1_7.py`, `run_pass0a_voice_config.py`, and `run_pass_0b_tailor.py` hardcodes `model="claude-opus-4-7"` as a string literal rather than reading the env var. A global model swap via env var alone would **not** move these call sites — each hardcoded literal has to be edited individually (this is directly relevant to how a C62 migration would actually be executed: it's a find-and-replace across ~12 files' literals plus `clients.py`'s and the runtime flows' env-var defaults, not a single env-var flip).
4. **Transcription intentionally omits thinking even on Opus** (unchanged from prior edition, §7.7 there) — Speaker ID and Cleaning both stay thinking-off by design even if their model env vars are pointed at Opus. Now load-bearing for C62: this is exactly the shape that 400s on Opus 5.5.
5. **Manifest recording incomplete on the main orchestrator** (unchanged, prior §7.8) — telemetry gap, not a migration blocker.
6. **`paths.merge_chunk()` dead code** (unchanged, prior §7.9) — cosmetic.
7. **Orphaned legacy Pass 7-pre prompts** (unchanged, prior §7.10) — `persona_pass_7pre_citation.md`/`_user.md`, superseded, not imported anywhere, still on disk.
8. **Hardcoded paths not in `paths.py`** (unchanged, prior §7.11).
9. **No `tool_choice`, no `top_p`/`top_k`, no `budget_tokens` sent, no generation-time prefill anywhere in the repo** — verified fresh this regeneration (§0). Directly resolves the corresponding open questions in the OPEN_ITEMS C62 note.
10. **New finding — Step 1 Validation's `reasoning_effort="high"` is unconditional** (§2.4.4) — documentation-accuracy note, not an Anthropic-migration item.
11. **New finding — no Anthropic call site anywhere in the repo sets an explicit thinking `effort`/`output_config.effort`.** Every adaptive-thinking call relies on the API's own default. This is dormant today (Opus 4.7's implicit default reasoning depth) but becomes live behavior-change risk under Opus 5.5 — see §10.

---

## 8. What is NOT an LLM call

Runtime: `python_select`/Provocateur Stage 2 selection, `package_voice_briefings`/Stage 4 packaging, Researcher's `merge_clusters_and_themes`, FFmpeg normalize/ffprobe (Ingest), Voice `card_assembly.py`, Voice `publish.py`, Editor `card_assembly.py`, Editor `edition.py` (Stage 3 lead-pick + indices), Editor `publish.py`, `runtime/scripts/**` (all 9 scripts, verified import-clean of every LLM client this pass), Voice Step 2 Validation's mechanical length check (`_check_length_compliance`).

Personas: Pass 0b base render (Jinja2), split tailored prompt, Pass 1c-extract + fetch, Pass 6.5-clean, FU#33 P2 INCONSISTENT merge, path-to-pass mapping, card assembly, CARD COMPLETE summary, chat artifact, Wikipedia REST, `dr_validation.py`/`research_validation.py`/`node0_validation.py`/`node1d_excerpt_selection.py`/`node1c_fetch.py` (all confirmed import-clean this pass).

---

## 9. Dev / QC tooling that fires live API calls (not part of the automated per-night / per-voice build)

Flagged separately so these don't get miscounted as production call sites in a cost or migration audit — they only fire when an operator runs them by hand.

- **`personas/phase_5_cross_persona_qc.py`** — cross-persona QC harness. `_call_evaluator` (:116) tries OpenAI `o3`→`gpt-4o`→Gemini fallback (`temperature=0.0`); `_invoke_voice` (:301, call `:310`) calls `claude-sonnet-4-6` directly with `thinking=False, temperature=0.7` — this is the one place in the whole repo outside the Sonnet-4.6-hardcoded production call sites where a non-zero, non-dropped temperature is sent to Anthropic, and it would break unmodified on a Sonnet-5 swap same as the production Sonnet call sites in §10.
- **`personas/scripts/standalone_pass4b_test.py`** — one-off empirical Pass 4b re-run tool, writes to `/tmp/`. `claude-opus-4-7`, `thinking=True`, `temperature=1.0` (dropped, same as production Pass 4b) — safe under the same logic as every other thinking=True Opus call.

---

## 10. Migration notes (C62)

Scope: precisely which call sites break or change behavior under **(a)** Opus 4.7 → Opus 5.5 and **(b)** Sonnet 4.6 → Sonnet 5, using only what this regeneration found in code plus the stated API facts (temperature/top_p/top_k → 400 on Opus 4.7/4.8, Opus 5.x, and Sonnet 5; `budget_tokens` → 400 on those same families; thinking cannot be disabled at all on Opus 5.5 — 400 at every effort; Sonnet 5 accepts thinking disabled; Opus 5.5's default effort is `medium`, not `high`; assistant prefill → 400 on the 4.6+ family; forced `tool_choice` any/tool → 400 on Opus 5.5).

### 10.0 Live-bug check (today, on current Opus 4.7 / Sonnet 4.6 — not a future-migration question)

**No call site currently sends an explicit `temperature`, `top_p`, `top_k`, or `budget_tokens` to `claude-opus-4-7`.** This was checked exhaustively, not sampled: every Opus-4.7-targeting call site in the repo either (a) goes through `stream_voice_call` or `_stream_and_parse`, neither of which has a temperature parameter at all (Voice, Editor, Provocateur, Researcher, Transcription-when-overridden-to-Opus), or (b) goes through `call_claude` with `thinking=True` (every personas Opus call site — Pass 0a, 0b-tailor, 1.1-1.7, 1d, 2, 3, 4a, 4b, 5, 6, 7a-FIX, 7b, Derive/Derive-fast), which structurally drops temperature before the request is built (`clients.py:122`). **There is no live bug to flag here** — the codebase is already clean on this axis, which is itself worth stating plainly since the alternative (a silent 400 in production) is exactly what this audit was checking for.

### 10.1 (a) Opus 4.7 → Opus 5.5 — breaks / behavior changes, by file:line

**Breaks (400) — thinking cannot be disabled on Opus 5.5:**

- `runtime/flows/transcription_flow.py:522` (Speaker ID) and `:576` (Cleaning) — **only if** an operator points `TRANSCRIPTION_SPEAKER_ID_MODEL` or `CLAUDE_MODEL` at `claude-opus-5-5`. Both calls run with no `thinking` kwarg by design (§7.7/§2.1). Not a default-config break (default model there is Sonnet), but a real trap: the documented "flip to Opus for hard sessions" escape hatch (`transcription_flow.py:78-82`) would 400 outright on Opus 5.5 rather than degrading gracefully. **Fix before migrating this override path:** either add `thinking={"type":"adaptive"}` when the resolved model is a 5.5-family Opus, or restrict the hard-session override to Sonnet 5 (which does accept thinking disabled).
- `runtime/flows/voice/step2_validation.py:90` (`_call_anthropic`, all 4 pillars) — conditional on `VOICE_STEP2_VALIDATION_MODEL` being pointed at Opus 5.5. No `thinking` key is ever built here (§2.4.5/§6.4). Same fix shape as above.
- `runtime/flows/editor/synthesis_router.py:125` and `voice/step2_first_draft_artifact.py:294` (shared `route_synthesis_voice`) — conditional on `SYNTHESIS_ROUTER_MODEL` being pointed at Opus 5.5. No `thinking` key ever built (§2.5.1).
- `personas/phase_5_cross_persona_qc.py:310` — conditional on someone hardcoding Opus 5.5 into `_invoke_voice`'s `model=` argument (currently hardcoded to Sonnet, so not live today, but flagged since it's a `thinking=False` call).

None of the *default-configuration* Opus call sites break this way — every default-path Opus call in Researcher/Provocateur/Voice Steps 1-3/Editor dossier/all personas passes runs with thinking on by default. This entire break category is conditional on an env-var or hardcoded-literal override that isn't exercised in normal operation today.

**Behavior change, not a break — effort defaults from `high` to `medium`:**

Every single Opus adaptive-thinking call site in the repo relies on the model's implicit default reasoning depth; none sets `effort` explicitly (verified by grep, §0/§7.11). That is every row in §1.2 marked "True, adaptive" (Pass 0a/0b-tailor/1.1-1.7/1d/2/3/4a/4b/5/6/7a-FIX/7b/Derive — 15+ personas call sites) plus every Voice Step 1/2/3 call (`voice/step1_private_reasoning.py:186`, `step2_first_draft_artifact.py:355`, `step3_amended_artifact.py:255`) and the Editor dossier call (`editor/dossier_generation.py:577`), plus Researcher extraction/clustering/theming (`researcher_flow.py:314/412/529`) and Provocateur triage/formulation (`provocateur_flow.py:411`, shared). **Moving any of these to Opus 5.5 without adding an explicit effort parameter silently drops the reasoning depth from the current implicit `high` to the new implicit `medium`** — no error, just a quality regression that would be easy to miss without a side-by-side eval. Given the reasoning-depth-sensitive nature of several of these (Pass 4a voice-modeling, Pass 6 corpus curation, Voice Step 2's focus/stance/form judgment, Editor's dossier framing), this is arguably the single highest-impact item in this migration for anyone moving the *default* configuration rather than an override.

### 10.2 (b) Sonnet 4.6 → Sonnet 5 — breaks / behavior changes, by file:line

Sonnet 5 accepts thinking disabled (no break there), but **rejects `temperature`/`top_p`/`top_k`** same as the Opus 5.x family. Every Sonnet-4.6 call site that currently sends an explicit, non-dropped temperature will 400 on Sonnet 5:

- `personas/flows/shared/pass_7pre_chunked.py:88` (Stage 1 extract), `:133` (Stage 2 verify), `:273` (Stage 3 boddice check) — all three hardcode `claude-sonnet-4-6`, `thinking=False`, `temperature=0.0` explicit. **These are the highest-volume break** — Stage 2 alone fires N≈3-6 batched calls per voice, every voice, every build. **Fix:** drop the `temperature=0.0` kwarg (or gate it on model family) before repointing `_EXTRACT_MODEL`/`_VERIFY_MODEL`/`_BODDICE_MODEL` at Sonnet 5.
- `personas/run_persona_pipeline.py:1618` (`_pass_7c` Sonnet fallback) — `claude-sonnet-4-6`, `thinking=False`, `temperature=0.0` explicit. Only fires when the Gemini primary call fails, but would 400 on Sonnet 5 when it does.
- `personas/phase_5_cross_persona_qc.py:311` — dev tool, `claude-sonnet-4-6`, `thinking=False`, `temperature=0.7` explicit. Would break if this script's hardcoded model were bumped to Sonnet 5 without also dropping the temperature kwarg.

**Not a break — verified safe:**

- `runtime/flows/voice/continuity.py:180` — Sonnet 4.6 default, but routes through `stream_voice_call`, which never sends temperature regardless of the `thinking` setting. Safe to repoint at Sonnet 5 as-is (and thinking-disabled would also be fine on Sonnet 5 if `VOICE_CONTINUITY_THINKING=0` were ever set).
- `runtime/flows/voice/step2_validation.py:90`, `runtime/flows/editor/synthesis_router.py:125`, `voice/step2_first_draft_artifact.py:294` — none of these send temperature at all (§10.0/§6.4/§6.3); safe on Sonnet 5 for the temperature axis specifically (they were flagged above only for the Opus-5.5-thinking-disabled axis, which doesn't apply to a Sonnet-5 target).
- `run_persona_pipeline.py:456 _ct_compress` (all 4 CT calls) — `thinking=True`, so temperature is dropped before the request is built (§3 correction 1, §6.1). Safe on Sonnet 5 as-is.
- `chunk_runner.py`, `run_pass_1_7.py`, and every other `thinking=True` call in the repo — not Sonnet-targeted today, but included for completeness: would remain safe if ever repointed at Sonnet 5, same logic.

Sonnet 5's `effort` default was not stated as changing in the given API facts (only Opus 5.5's was) — no equivalent behavior-change item is recorded for the Sonnet 4.6 → Sonnet 5 leg beyond the temperature breaks above.

### 10.3 Summary punch list

| Migration leg | Breaks (400) | Conditional-only breaks | Silent behavior change |
|---|---|---|---|
| Opus 4.7 → Opus 5.5 | none in default config | 4 call sites, only if an env-var/model override is exercised (transcription speaker-id/cleaning, voice step2-validation, synthesis-router ×2 call sites, QC-script) | **every** adaptive-thinking Opus call site (~20+) silently drops from effort=high to effort=medium unless `effort` is set explicitly |
| Sonnet 4.6 → Sonnet 5 | 4 call sites, all default-config, all explicit `temperature=0.0`/`0.7` + `thinking=False` (pass_7pre_chunked ×3, pass_7c fallback, QC-script) | — | none identified |
| Live bug today (pre-migration) | **none found** — no call site currently sends temperature to Opus 4.7 | — | — |

Everything not listed above (the `stream_voice_call`/`_stream_and_parse`/`_call_anthropic` families, and every `thinking=True` `call_claude` site) migrates cleanly on the temperature axis for both legs; the only work required there is the Opus-5.5 effort-default item if reasoning depth needs to be preserved.

---

*Regenerated 2026-09-27 from repo state on branch `phase0-fixes`. Verify against `git show`/`git blame` before quoting for budgeting, and re-check §10 against the actual Opus 5.5 / Sonnet 5 API surface at migration time — this doc reasons from the API facts supplied for this regeneration, not from a live test against those endpoints.*
