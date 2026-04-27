# LLM Call Inventory

**Purpose:** Complete enumeration of every model API call made from this repo, with provider, model, parameters, and prompt source. Written against the actual code (not against the spec docs, which have drifted). Verify against `git show` when things look stale.

**Scope:** All LLM / AI API calls initiated by code in this repo — runtime flows (transcription, researcher, provocateur) and the persona pipeline. External-facing manual steps (the human Claude DR sessions at claude.ai) are noted for completeness but are not code-initiated.

**Last read against the code:** 2026-04-27. Major rewrite covering arch-03 chunked merge (Pass 1.1–1.7), Phase B per-voice layout, FU#2 chunked Pass 7-pre, FU#13 linear patcher (replaces revision loop), FU#41 chat artifact, FU#33 P1 bracket-strip (Pass 6.5-clean), Pass 7-anachronism added, Pass 0b tailor LLM call added. Models and parameters update frequently; re-verify before quoting for budgeting.

---

## 0. Providers and models at a glance

| Provider | SDK | Models used | Where |
|---|---|---|---|
| Anthropic | `anthropic` Python SDK (`==0.94.1` in both venvs) | `claude-opus-4-7`, `claude-sonnet-4-6` | Everywhere Claude is called |
| AssemblyAI | `assemblyai==0.59.0` | `universal-3-pro` | Transcription ASR + diarization |
| Perplexity | Raw HTTP via `requests` | `sonar-deep-research` | Persona Pass 1a |
| Google Gemini | `google-genai==1.73.1` | `gemini-2.5-pro` | Persona Pass 1b, 7-anach + 7a fallback, 7c primary |
| OpenAI | `openai==2.31.0` Python SDK | `gpt-5.4` (high reasoning), `gpt-4.1`, `o3`, `gpt-4o` | Persona Pass 7-anachronism + Pass 7a (5-model ladder) |
| Wikipedia | REST (`requests`) | — | Persona Pass 0a (not LLM; grounding lookup) |

Anthropic dominates call volume. Everything else is pre-Athens (personas) or upstream-only (AssemblyAI during transcription).

---

## 1. Summary table — one row per call site

Grouped by pipeline; N = expected invocations per run. Cost rough-cuts per the spec docs' validation runs (dev_msc_test for runtime, Plato build for personas).

| # | Pipeline · Call site | Provider | Model | Method | max_tokens | Thinking | Temp | Retry | N per run |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Transcription · ASR | AssemblyAI | `universal-3-pro` | `Transcriber.transcribe` (synchronous poll) | — | — | — | Prefect 3× expbo factor 10 + jitter | 1 per session |
| 2 | Transcription · Speaker ID | Anthropic | `SPEAKER_ID_MODEL` (default Sonnet 4.6) | `messages.create` (non-streaming) | 4096 | Off | SDK default | Prefect 2× expbo factor 5 | 1 per session |
| 3 | Transcription · Cleaning | Anthropic | `CLAUDE_MODEL` (default Sonnet 4.6) | `messages.stream` (streaming required) | 64000 | Off | SDK default | Prefect 2× expbo factor 5 | 1 per session |
| 4 | Researcher · Extraction | Anthropic | `CLAUDE_MODEL` (default Opus 4.7) | `messages.stream` | 40000 | Adaptive (default on) | 1.0 | Prefect 2× expbo factor 5 | 1 per session |
| 5 | Researcher · Clustering (Round 1) | Anthropic | `CLAUDE_MODEL` (default Opus 4.7) | `messages.stream` | 40000 | Adaptive | 1.0 | Prefect 2× expbo factor 5 | 1 per night |
| 6 | Researcher · Theming (Round 2) | Anthropic | `CLAUDE_MODEL` (default Opus 4.7) | `messages.stream` | 24000 | Adaptive | 1.0 | Prefect 2× expbo factor 5 | 1 per night |
| 7 | Provocateur · Triage Voice | Anthropic | `CLAUDE_MODEL` (default Opus 4.7) | `messages.stream` | 40000 | Adaptive | SDK default | Prefect 5× expbo factor 15 | 12 per night (one per voice) |
| 8 | Provocateur · Triage Flags | Anthropic | `CLAUDE_MODEL` (default Opus 4.7) | `messages.stream` | 40000 | Adaptive | SDK default | Prefect 5× expbo factor 15 | 1 per night |
| 9 | Provocateur · Formulation | Anthropic | `CLAUDE_MODEL` (default Opus 4.7) | `messages.stream` | 40000 | Adaptive | SDK default | Prefect 5× expbo factor 15 | N per night (≈40 on dev_msc_test; batched 4/min) |
| 10 | Personas · Pass 0a Voice Config | Anthropic | `claude-opus-4-7` | via `call_claude` (streams) | 24000 | Adaptive | 1.0 | 1× retry on `RateLimitError`/`APIError`/`JSONDecodeError`/`IncompleteResponse` (wait 15s) | 1 per voice |
| 11 | Personas · Pass 1a Perplexity | Perplexity | `sonar-deep-research` (env: `PERPLEXITY_MODEL`) | `POST /chat/completions` (REST) | — | — | 0.0 | None; 900s timeout | 1 per voice |
| 12 | Personas · Pass 1b Gemini | Google | `gemini-2.5-pro` (env: `GEMINI_MODEL`) | `generate_content` | 16384 | Model default (2.5-pro requires thinking) | 0.2 | None | 1 per voice |
| 13 | Personas · Pass 0b base render | — | — | Jinja2 template only (no API) | — | — | — | — | 1 per voice |
| **14** | **Personas · Pass 0b tailor** *(NEW v4)* | Anthropic | `claude-opus-4-7` | via `call_claude` (streams) | 16000 | Adaptive | 1.0 | 1× retry | 1 per voice |
| **15** | **Personas · Pass 1.1 BIOGRAPHICAL** *(NEW v4 — replaces v3.10 Pass 1-merge)* | Anthropic | `claude-opus-4-7` | via `chunk_runner.run_chunk()` (streams) | 48000 | Adaptive | 1.0 | 1× retry on `ValidationError` with critique; transient retries on network | 1 per voice |
| **16** | **Personas · Pass 1.2 INTELLECTUAL** | Anthropic | `claude-opus-4-7` | via `chunk_runner.run_chunk()` (streams) | 48000 | Adaptive | 1.0 | as #15 | 1 per voice |
| **17** | **Personas · Pass 1.3 REASONING** | Anthropic | `claude-opus-4-7` | via `chunk_runner.run_chunk()` (streams) | 48000 | Adaptive | 1.0 | as #15 | 1 per voice |
| **18** | **Personas · Pass 1.4 VOICE** | Anthropic | `claude-opus-4-7` | via `chunk_runner.run_chunk()` (streams) | 48000 | Adaptive | 1.0 | as #15 | 1 per voice |
| **19** | **Personas · Pass 1.5 BOUNDARIES** | Anthropic | `claude-opus-4-7` | via `chunk_runner.run_chunk()` (streams) | 48000 | Adaptive | 1.0 | as #15 | 1 per voice |
| **20** | **Personas · Pass 1.6 CORPUS** | Anthropic | `claude-opus-4-7` | via `chunk_runner.run_chunk()` (streams) | 48000 | Adaptive | 1.0 | as #15 | 1 per voice |
| **21** | **Personas · Pass 1.7 Coherence audit (narrow)** *(NEW v4)* | Anthropic | `claude-opus-4-7` | via `call_claude` (streams) | 24000 | Adaptive | 1.0 | 1× retry | 1 per voice (sequential after 1.1–1.6) |
| 22 | Personas · Pass 1c-extract *(now Python-only)* | — | — | Deterministic regex via `flows/shared/url_extract.py` | — | — | — | — | 1 per voice (skipped if `primary_text_sources` populated) |
| 23 | Personas · Pass 1c fetch | — | — | HTTP fetch of primary texts (SSRF-hardened) | — | — | — | per-URL exception handling, no retry | N URLs per voice |
| **24** | **Personas · Pass 1d Excerpt Selection** *(model upgraded)* | Anthropic | `claude-opus-4-7` | via `call_claude` (streams) | 16000 | Adaptive | 1.0 | 1× retry | 1 per voice (skipped if no primary texts) |
| **25** | **Personas · Pass 2 Identity & Boundaries** *(max_tokens raised)* | Anthropic | `claude-opus-4-7` | via `call_claude` (streams) | 32000 | Adaptive | 1.0 | 1× retry | 1 per voice |
| **26** | **Personas · CT after Pass 2** *(model upgraded)* | Anthropic | `claude-sonnet-4-6` | via `call_claude` (streams) | 16000 | Adaptive | 0.0 | 1× retry | 1 per voice |
| **27** | **Personas · Pass 3 Intellectual Core** | Anthropic | `claude-opus-4-7` | via `call_claude` (streams) | 32000 | Adaptive | 1.0 | 1× retry | 1 per voice |
| **28** | **Personas · CT after Pass 3** | Anthropic | `claude-sonnet-4-6` | via `call_claude` (streams) | 16000 | Adaptive | 0.0 | 1× retry | 1 per voice |
| 29 | Personas · Pass 4a Voice (corpus-grounded) | Anthropic | `claude-opus-4-7` | via `call_claude` (streams) | 24000 | Adaptive | 1.0 | 1× retry | 1 per voice |
| **30** | **Personas · CT after Pass 4a** | Anthropic | `claude-sonnet-4-6` | via `call_claude` (streams) | 16000 | Adaptive | 0.0 | 1× retry | 1 per voice |
| **31** | **Personas · Pass 4b Artifact** *(model upgraded Sonnet→Opus + thinking)* | Anthropic | `claude-opus-4-7` | via `call_claude` (streams) | 24000 | Adaptive | 1.0 | 1× retry | 1 per voice |
| **32** | **Personas · CT after Pass 4b** | Anthropic | `claude-sonnet-4-6` | via `call_claude` (streams) | 16000 | Adaptive | 0.0 | 1× retry | 1 per voice |
| 33 | Personas · Pass 5 Engagement | Anthropic | `claude-opus-4-7` | via `call_claude` (streams) | 16000 | Adaptive | 1.0 | 1× retry | 1 per voice |
| **34** | **Personas · Pass 6 Corpus Curation** *(model upgraded Sonnet→Opus + thinking)* | Anthropic | `claude-opus-4-7` | via `call_claude` (streams) | 24000 | Adaptive | 1.0 | 1× retry | 1 per voice (HALTS if no primary texts) |
| **35** | **Personas · Pass 6.5-clean** *(NEW v4 FU#33 P1)* | — | — | Deterministic regex via `flows/shared/bracket_strip.py` | — | — | — | — | 1 per voice |
| **36** | **Personas · Pass 7-pre Stage 1 (extract claims)** *(NEW v4 FU#2)* | Anthropic | `claude-sonnet-4-6` | via `call_claude` (streams) | 32000 | Off | 0.0 | 1× retry on transient JSON failures | 1 per voice |
| **37** | **Personas · Pass 7-pre Stage 2 (verify batch)** *(NEW v4 FU#2)* | Anthropic | `claude-sonnet-4-6` | via `call_claude` (streams), max 4 parallel workers | 16000 | Off | 0.0 | 1× retry | **N batches per voice (~3–6, ~25 claims each)** |
| **38** | **Personas · Pass 7-pre Stage 3 (boddice tag check)** *(NEW v4 FU#2)* | Anthropic | `claude-sonnet-4-6` | via `call_claude` (non-streaming) — parallel with Stage 2 | 8000 | Off | 0.0 | 1× retry | 1 per voice |
| **39a** | **Personas · Pass 7-anachronism** *(NEW v4)* — primary | OpenAI | `gpt-5.4` | `chat.completions.create` (`reasoning_effort="high"`) | 16384 | — | omitted | 1× retry per attempt | 1 per voice |
| **39b** | Pass 7-anach fallback 1 | OpenAI | `gpt-4.1` | `chat.completions.create` | 16384 | — | 0.0 | per-attempt | only if 39a fails |
| **39c** | Pass 7-anach fallback 2 | OpenAI | `o3` | `chat.completions.create` (reasoning) | 16384 | — | omitted | per-attempt | only if 39b fails |
| **39d** | Pass 7-anach fallback 3 | OpenAI | `gpt-4o` | `chat.completions.create` | 16384 | — | 0.0 | per-attempt | only if 39c fails |
| **39e** | Pass 7-anach fallback 4 | Google | `gemini-2.5-pro` | `generate_content` | 16384 | Model default | 0.0 | None | only if all OpenAI attempts fail |
| **40a** | **Personas · Pass 7a Cross-Model** — primary *(ladder updated v4)* | OpenAI | `gpt-5.4` (high) | `chat.completions.create` | 16384 | — | omitted | per-attempt | 1 per voice |
| 40b | Pass 7a fallback 1 | OpenAI | `gpt-4.1` | `chat.completions.create` | 16384 | — | 0.0 | per-attempt | only if 40a fails |
| 40c | Pass 7a fallback 2 | OpenAI | `o3` | `chat.completions.create` (reasoning) | 16384 | — | omitted | per-attempt | only if 40b fails |
| 40d | Pass 7a fallback 3 | OpenAI | `gpt-4o` | `chat.completions.create` | 16384 | — | 0.0 | per-attempt | only if 40c fails |
| 40e | Pass 7a fallback 4 | Google | `gemini-2.5-pro` | `generate_content` | 16384 | Model default | 0.0 | None | only if all OpenAI attempts fail (writes SKIPPED sentinel if all fail) |
| **41** | **Personas · Pass 7a-FIX (linear patcher)** *(NEW v4 FU#13 — replaces revision loop)* | Anthropic | `claude-opus-4-7` | via `call_claude` (streams) | 32000 | Adaptive | 1.0 | 1× retry | 0 or 1 per voice (only if Pass 7a `overall == REVISION_NEEDED`); on apply, re-fires #36+#39+#40 once |
| 42 | Personas · Pass 7b Worked Provocations | Anthropic | `claude-opus-4-7` | via `call_claude` (streams) | 24000 | Adaptive | 1.0 | 1× retry | 1 per voice |
| 43a | Personas · Pass 7c Negative Constraints — primary | Google | `gemini-2.5-pro` | `generate_content` | 16384 | Model default | 0.0 | None | 1 per voice |
| 43b | Pass 7c fallback | Anthropic | `claude-sonnet-4-6` (bias-aware variant) | via `call_claude` (non-streaming) | 8192 | Off | 0.0 | 1× retry | only if Gemini fails |
| **44** | **Personas · Derive** *(model upgraded Sonnet→Opus + thinking)* | Anthropic | `claude-opus-4-7` | via `call_claude` (streams) | 24000 | Adaptive | 1.0 | 1× retry | 1 per voice |
| **45** | **Personas · Chat artifact (FU#41)** | — | — | Pure Python via `flows/shared/chat_prompt_builder.py` | — | — | — | — | 1 per voice |
| 46 | Personas · Wikipedia | Wikipedia | — | REST (opensearch + page summary) | — | — | — | None | 1–6 per Pass 0a interactive run |
| — | Personas · Pass 1a-DR (manual claude.ai) | Anthropic (claude.ai UI) | `claude-opus-4-6` for §1–§5; `claude-opus-4-7` for §6 | **Human paste-and-wait, Extended Thinking + Deep Research** | — | — | — | — | **6 per voice**, ~60–180 min per session wall time |

**Runtime call count per night** (12 voices, ~20 themes, ~40 assigned pairs): ASR 6–9 · Speaker ID 6–9 · Cleaning 6–9 · Extraction 6–9 · Clustering 1 · Theming 1 · Triage Voice 12 · Triage Flags 1 · Formulation ~40 → **~80–90 LLM calls per night**.

**Personas call count per voice (v4):** 0a 1 · 1a 1 · 1b 1 · 0b tailor 1 · Pass 1.1–1.7 (7) · 1d 1 · Pass 2+CT 2 · Pass 3+CT 2 · Pass 4a+CT 2 · Pass 4b+CT 2 · Pass 5 1 · Pass 6 1 · 7-pre 3-stage (1+N+1, where N≈3–6) · 7-anach 1 (1–5 attempts) · 7a 1 (1–5 attempts) · 7a-FIX 0 or 1 (with 3 re-fires of pre/anach/7a if it runs) · 7b 1 · 7c 1 (1–2 attempts) · Derive 1 → **~28–35 LLM calls per voice (more if 7a-FIX fires; the verify-batches and the model-ladder fallbacks are the variable parts)**. 12 voices → **~340–420 calls for the full pre-Athens build.**

Add to that **66 manual claude.ai DR sessions** (11 voices × 6 sections; Plato done) — these are operator-paid against the claude.ai subscription, not API.

---

## 2. Runtime pipeline calls (detail)

### 2.1 Transcription — `runtime/flows/transcription_flow.py`

#### 2.1.1 AssemblyAI ASR — `transcribe_with_assemblyai` (L302-360)
- `Transcriber.transcribe(audio_url, config)`
- `config.raw.speech_models = ["universal-3-pro"]` (SDK 0.59.0 workaround); `speech_model = None`
- `speaker_diarization=True`, `language_detection=True`, `keyterms_prompt=[panel_member_full_names]`
- Timeout: 30 min (uvicorn polls)

#### 2.1.2 Speaker ID — `assign_speakers_with_claude` (L412-466), 5-pass
- Model: `os.environ["TRANSCRIPTION_SPEAKER_ID_MODEL"]` (default `CLAUDE_MODEL`, default `claude-sonnet-4-6`)
- Pass 1: rough assignment (full transcript, all candidates)
- Pass 2: critique (Claude evaluates Pass 1 result)
- Pass 3: bio-grounded refinement (uses speakers.json bios)
- Pass 4: final assignment + critique
- Pass 5: per-turn reassignment (catches drift; uses session-final assignment)
- All passes: `messages.create` (non-streaming), `max_tokens=4096`, `thinking=False` (intentional per §7.7)

#### 2.1.3 Cleaning — `clean_transcript_with_claude` (L513-588)
- Streaming: `messages.stream` (required: 64K tokens)
- Model: `os.environ["TRANSCRIPTION_CLAUDE_MODEL"]` (falls back to `CLAUDE_MODEL`)
- `max_tokens=64000`, `thinking=False` (intentional)
- 80% budget warning: emit warning if assembled output exceeds 51200 tokens

### 2.2 Researcher — `runtime/flows/researcher_flow.py`

#### 2.2.1 Extraction — `extract_session` (L97-136)
- Model: `os.environ["RESEARCHER_CLAUDE_MODEL"]` (default `CLAUDE_MODEL`, default Opus 4.7)
- `messages.stream`, `max_tokens=40000`
- `thinking={"type": "adaptive"}` if `RESEARCHER_THINKING != "0"`, else `thinking=None`
- Temp 1.0
- Per-session

#### 2.2.2 Clustering Round 1 — `cluster_round_1` (L173-217)
- Same config as extraction
- Inputs: minimal `{ref, extraction, context}` only — NO session/lens/responds_to/engagement (deliberate; v2.4 → v3 fix)
- Shuffled with seed 42 (deterministic)

#### 2.2.3 Theming Round 2 — `theme_round_2` (L259-298)
- Same config but `max_tokens=24000`
- Inputs: cluster-level only (`cluster_id`, `abstract_text`)
- Shuffled with seed 42

### 2.3 Provocateur — `runtime/flows/provocateur_flow.py`

#### 2.3.1 Stage 1A Triage Voice (per-voice) — `triage_voice` (L289-319)
- Model: `os.environ["PROVOCATEUR_CLAUDE_MODEL"]`
- `messages.stream`, `max_tokens=40000`, `thinking` controlled by `PROVOCATEUR_THINKING` env var (default on)
- 12 calls per night, parallel-executed by Prefect

#### 2.3.2 Stage 1B Triage Flags (theme flags) — `triage_flags` (L373-407)
- Same config
- 1 call per night (post-aggregation)

#### 2.3.3 Stage 3 Formulation (per-pair) — `formulate_pair` (L646-694)
- Same config
- Parallel-batched: `PROVOCATEUR_FORMULATION_BATCH=4` (default), `PROVOCATEUR_BATCH_WAIT_S=20`
- ~40 calls per night

### 2.4 Selection (Provocateur Stage 2) — pure Python, no LLM

`select_assignments` (L539-611). Pure Python deterministic 9-step algorithm. No LLM.

---

## 3. Persona Pipeline calls (detail)

### 3.1 Phase 0 — Intake

#### 3.1.1 Pass 0a Voice Config — `run_pass0a_voice_config.py:175`
- Model: `claude-opus-4-7` hardcoded
- `call_claude(thinking=True)` — adaptive thinking
- `max_tokens=24000`, `temperature=1.0`, `response_format_json=True`
- System: `pass_0a_voice_config.md` (129 lines)
- User: inline (renders voice name + Wikipedia grounding + conference_facts.json + panel_roster.json)
- Output: `02_voice_config.json` (validated against `schemas/voice_config.py`) + `03_review_doc.md`
- Validation retry: 1× retry with critique on `InputRejected.reason`; logs `VALIDATION FAIL: field=X, value=Y`

#### 3.1.2 Wikipedia Search + Summary
- REST opensearch + page summary
- Interactive picker (or `--wiki URL` direct, or `--hint TEXT` fallback)
- 1–6 calls depending on candidate count

### 3.2 Phase 0.5 — Pre-DR Research (`run_phase0_1_research.py`)

#### 3.2.1 Pass 1a Perplexity — `call_perplexity` (clients.py:118)
- Model: `os.environ.get("PERPLEXITY_MODEL", "sonar-deep-research")`
- POST `https://api.perplexity.ai/chat/completions`
- `temperature=0.0`, no max_tokens
- 900s timeout
- System: one of `persona_pass_1a_{human, fictional, non_human_organism, non_human_system}.md` selected by `voice_input.type`
- Hostile-source appendix injected when `hostile_sources=true`
- Output: 6-section structured dossier (auto-split via `flows/shared/perplexity_split.py` for downstream chunk passes)

#### 3.2.2 Pass 1b Gemini Broad Scan — `call_gemini`
- Model: `gemini-2.5-pro` (env: `GEMINI_MODEL`)
- `generate_content` with `max_output_tokens=16384`, `temperature=0.2`
- System: one of `persona_pass_1b_{human, fictional, non_human_organism, non_human_system}.md`
- Cross-disciplinary breadth — NOT sectioned

#### 3.2.3 Pass 1a + Pass 1b run in parallel
`ThreadPoolExecutor(max_workers=2)` in `run_phase0_1_research.py`.

#### 3.2.4 Pass 0b base render — Jinja2, no API
- Assembles `01_monolithic_dr_prompt.md` from `pass_0b_header.md` + type-specific body (`pass_0b_{human, fictional, non_human_organism, non_human_system}.md`) + `pass_0b_footer.md` + research-discipline include `_pass_0b_research_discipline.md`
- Conditional blocks: hostile-source appendix, `lyrics_patterns_only`, system-entity grounding
- Pure template render, no LLM

#### 3.2.5 Pass 0b tailor — `run_pass0b_dr_prompt.py` *(NEW v4)*
- Model: `claude-opus-4-7`
- `call_claude(thinking=True)`, `max_tokens=16000`, `temperature=1.0`
- System: `pass_0b_tailor.md` (208 lines)
- **Structured injections only** — splices voice-specific guidance into the monolithic prompt at marked sections (PB#2 base preservation enforced architecturally); does NOT full-rewrite
- Output: tailored monolithic + `02_tailoring_notes.json`

#### 3.2.6 Split tailored prompt — `scripts/split_tailored_prompt.py`, no API
- Pure Python text split into 6 per-section prompts: `03_section_1_dr_prompt.md` … `08_section_6_dr_prompt.md`

### 3.3 Phase 0.7 — Manual claude.ai DR sessions

**6 sessions per voice** at claude.ai with Extended Thinking + Deep Research. Save each as `01_research/04_dr_dossier/0N_section_N.md`. Per-section model:

- §1–§5: `claude-opus-4-6`
- §6: `claude-opus-4-7` (Phase L empirical: 4.6 produces reader's-intro on §6; 4.7 required)

DR mode detection (`flows/shared/chunk_runner.py:74–98`): per-section files → `per_section`; falls back to `07_concat_claude_dr.md` → `monolithic`; errors on partial state.

### 3.4 Phase 1 — Chunked Merge (`run_pass_1_all.py` → `chunk_runner.run_chunk` → `run_pass_1_7.py`) *(NEW v4 — replaces v3.10 monolithic Pass 1-merge)*

#### 3.4.1 Pass 1.1 BIOGRAPHICAL — `chunk_runner.run_chunk(chunk_id="1.1", ...)`
- Model: `claude-opus-4-7`
- `call_claude(thinking=True)`, `max_tokens=48000`, `temperature=1.0`, `response_format_json=True`
- System: `pass_1_1_merge.md` (427 lines)
- User: synthesized inline ("Produce the Pass 1.1 merge for…")
- Inputs: relevant Perplexity section (auto-split) + full Gemini scan + per-section Claude DR dossier file
- Output: Pydantic-validated against `schemas/pass_1_1.py` (`LifeScaffold`, `FormativeCandidate[]`)
- Writes per-key JSONs: `02_merge/pass_1_1/{life_scaffold, formative_candidates}.json`
- Retry: 1× on `ValidationError` with critique; transient retries on network

#### 3.4.2–6 Pass 1.2 INTELLECTUAL through Pass 1.6 CORPUS
Same config as 1.1, with prompt + schema swapped. Pass 1.2: `pass_1_2_merge.md` + `schemas/pass_1_2.py` (Commitment[], Concept[], Tension[], InterpretiveFrame[]). Pass 1.3: `pass_1_3_merge.md` + ReasoningMethod + Textures + AnalyticalContext. Pass 1.4: `pass_1_4_merge.md` + Moves + Register + Vocabulary. Pass 1.5: `pass_1_5_merge.md` + KnowledgeBoundary + SensitiveTopics + HardLimits. Pass 1.6: `pass_1_6_merge.md` + Works + Passages + ReferenceOnlyPassages. (URLs chunk REMOVED under 1-arch-07 — derived deterministically by `url_extract.py`.)

**Parallelism:** `run_pass_1_all.py` runs 1.1–1.6 in parallel via `ThreadPoolExecutor(max_parallel=3)`.

#### 3.4.7 Pass 1.7 Coherence audit (narrow) — `run_pass_1_7.py`
- Sequential after 1.1–1.6 complete
- Stage A: Python composes audit prompt from 6 chunks
- Stage B: `call_claude(model="claude-opus-4-7", thinking=True)`, `max_tokens=24000`, `temperature=1.0`
  - System: `pass_1_7_coherence.md` (371 lines)
  - Output: `CoherenceAuditResult` Pydantic — `coherence_flags[]` + `coherence_resolutions[]` + `edits[]` (each edit = `{path, op: append|set, value, rationale}`)
- Stage C: Python applies `edits[]` to per-key chunk JSONs (chunks are SoT per 1-arch-05 Part B)
- Output: `02_merge/07_pass_1_7_coherence.json` (audit metadata) + `02_merge/08_merged_dossier.json` (convenience snapshot rebuilt from chunks)

#### 3.4.8 Pass 1c-extract — Python, no LLM *(downgraded from LLM in v4 — was Sonnet in v3.10)*
- `flows/shared/url_extract.extract_urls()` walks `passages[].citation` + `works[]` for primary-text URLs
- Canonicalizes Gutenberg landing pages → raw text URLs
- Output: `03_corpus/00_primary_text_urls.json`
- Skipped if `voice_config.primary_text_sources` populated (manual override)

#### 3.4.9 Pass 1c fetch — no LLM
- `flows/shared/node1c_fetch.fetch_all()`
- SSRF-hardened: scheme restriction (http/https), RFC1918 block, 5MB cap
- Gated by `03_primary_texts_reviewed.flag` (manual review gate)

#### 3.4.10 Pass 1d Excerpt Selection — `run_persona_pipeline.py:540–601` *(model upgraded v4)*
- Model: `claude-opus-4-7` *(was `claude-sonnet-4-6` in v3.10)*
- `call_claude(thinking=True)`, `max_tokens=16000`, `temperature=1.0`, `response_format_json=True`
- **60K char budget** (FU#46 raised from 30K for richer-corpus voices)
- System+user: `persona_pass_1d_excerpt_selection.md` (116 lines)
- Inputs: `build_structural_index()` of fetch results + chunk vars (passages, works, reasoning_method_chunk, register, moves)
- Output: `03_corpus/02_excerpt_selections.json` + sets `voice_basis = "corpus-based"`; SKIPPED if no primary texts → sets `voice_basis = "training-data"`
- **Runs late in code order:** between Pass 3 CT compress (line 534) and Pass 4a (line 634)

### 3.5 Phase 2 — Section-by-section Generation

All Phase 2 generation passes use Opus 4.7 + adaptive thinking, `temperature=1.0`, `response_format_json=True`. Coherence Threading (CT) compressions now use Sonnet 4.6 + adaptive thinking, `max_tokens=16000`, `temperature=0.0` (upgraded from v3.10's `max_tokens=2048`, `thinking=False`).

#### 3.5.1 Pass 2 Identity & Boundaries — `_pass_2`
- `max_tokens=32000` *(was 24000 in v3.10)*
- System: `persona_pass_2_identity_boundaries.md` (599 lines, Jinja-filled with `name`, `type`, `subtype`, `voice_mode`, `hostile_sources`)
- User: `persona_pass_2_user.md` (61 lines) — renders chunk vars (life_scaffold, formative_candidates, knowledge_boundary_chunk, sensitive_topics, hard_limits_chunk, voice_level_debate_frames)
- **FU#49 universal patterns:** structural-strain licensing in `epistemic_frame_statement` (49H); two-aporia distinction in `translation_protocol` (49I); phenomena-outside-corpus in `topics_requiring_care` (49J); Position B corpus-accurate softening in `hard_limits` (49D)
- Output: `04_generation/01_pass_2_identity_boundaries.json`

#### 3.5.2 CT after Pass 2 — `04_generation/02_ct_after_pass_2.json`
- Sonnet 4.6 + thinking, 16K
- System: inline; User: `persona_coherence_threading.md` (17 lines)

#### 3.5.3 Pass 3 Intellectual Core — `_pass_3`
- `max_tokens=32000`
- System: `persona_pass_3_intellectual_core.md` (232 lines)
- User: `persona_pass_3_user.md` (70 lines) — renders commitments, concepts, tensions, full interpretive_frames[] (1-arch-06), reasoning_method_chunk, textures, analytical_context_reasoning + pass_2_summary
- Output: `04_generation/03_pass_3_intellectual_core.json`

#### 3.5.4 CT after Pass 3 — `04_generation/04_ct_after_pass_3.json`

#### 3.5.5 Pass 4a Voice (corpus-grounded) — `_pass_4a`
- `max_tokens=24000`
- System: `persona_pass_4a_voice.md` (243 lines, Jinja with `name`, `type`, `subtype`, `voice_mode`, `hostile_sources`, `corpus_constraint`)
- User: `persona_pass_4a_user.md` (67 lines) — moves, register, vocabulary, analytical_context_voice, available_pathe, reasoning_method_summary, cross_disciplinary_frames + `primary_block` (from Pass 1d) + pass_2_3_summary
- Output: `04_generation/05_pass_4a_voice.json` + sets `voice_basis`

#### 3.5.6 CT after Pass 4a — `04_generation/06_ct_after_pass_4a.json`

#### 3.5.7 Pass 4b Artifact — `_pass_4b` *(model upgraded Sonnet→Opus + thinking)*
- Model: `claude-opus-4-7` *(was `claude-sonnet-4-6` in v3.10)*
- `call_claude(thinking=True)`, `max_tokens=24000`, `temperature=1.0` *(was 6144, 0.2, thinking=False)*
- System: `persona_pass_4b_artifact.md` (207 lines)
- User: `persona_pass_4b_user.md` (16 lines) — renders pass_2_3_4a_summary + Pass 4a fields
- **FU#49A:** generativity-permitting prompt + length variance 350–1500. **FU#49J:** don't-silently-complete-incomplete-translation universal entry
- Output: `04_generation/07_pass_4b_artifact.json`

#### 3.5.8 CT after Pass 4b — `04_generation/08_ct_after_pass_4b.json`

#### 3.5.9 Pass 5 Engagement — `_pass_5`
- `max_tokens=16000`
- System: `persona_pass_5_engagement.md` (141 lines)
- User: `persona_pass_5_user.md` (48 lines) — pass_2_3_4_summary + full constitution + full reasoning_method (NOT compressed) + deployment priming (FU#12-B from `conference_facts.json` + `audience_profile.json`)
- **FU#49K:** premature-closure-of-either-kind in `banned_modes`; 5 fidelity + 2 generativity `quality_criteria`; framework-strain closer in `unique_contribution`
- Output: `04_generation/09_pass_5_engagement.json`

#### 3.5.10 Pass 6 Corpus Curation — `_pass_6` *(model upgraded Sonnet→Opus + thinking)*
- Model: `claude-opus-4-7` *(was `claude-sonnet-4-6` in v3.10)*
- `call_claude(thinking=True)`, `max_tokens=24000`, `temperature=1.0` *(was 8000, 0.1, thinking=False)*
- System: `persona_pass_6_corpus.md` (124 lines, Jinja with `name`, `corpus_constraint`)
- User: `persona_pass_6_user.md` (59 lines) — primary_block + works + passages + reference_only_passages + pass_2_3_4a_summary + constitution + concept_lexicon + reasoning_method + Pass 4a voice fields
- **HALTS** if no primary texts (writes BLOCKED sentinel to fields)
- `corpus_constraint=lyrics_patterns_only` variant: structural/thematic descriptions, NO actual lyrics
- Output: `04_generation/10_pass_6_corpus.json`

### 3.6 Phase 2.5 — Pass 6.5-clean (FU#33 P1) *(NEW v4)*

`flows/shared/bracket_strip.strip_chunks_in_place()`. **No LLM.** Deterministic regex on `04_generation/*.json`.

**Strips:** `[ontological]`, `[epistemological]`, `[ethical-political]`/`[ethical_political]`, `[unique]`, `[metaphysical]`, `[psychological]`, `[political]`, `[aesthetic]`, `[cosmological]`, `[epistemic]`, `[ethical]`, `[stated]`, `[scholarly_consensus]`, `[inference]`, `[contested]`, `[curator_note]`/`[curator-note]`, `[pedagogical_note]`, `[editorial_note]`.

**PRESERVES:** `[experiential_reconstruction]`, `[projection_warning: ...]` — Boddice biocultural tags that Pass 7-pre Stage 3 looks for.

If files touched: reloads pass2–pass6 from disk into in-memory vars (lines 772–783 of orchestrator). Placement before validators ensures reports reflect shipped state.

### 3.7 Phase 3 — Validation

#### 3.7.1 Pass 7-pre — Citation Verification (FU#2 chunked, 3 stages) *(REPLACES v3.10 single-shot)*

`flows/shared/pass_7pre_chunked.run_chunked_pass_7pre()`. Replaces v3.10's single-shot Sonnet call (which hit 128K output ceiling on rich cards).

**Stage 1: Extract claims**
- Model: `claude-sonnet-4-6`
- `call_claude(thinking=False)`, `max_tokens=32000`, `temperature=0.0`, `response_format_json=True`
- System: `persona_pass_7pre_extract.md` (96 lines)
- User: `persona_pass_7pre_extract_user.md` (6 lines, wraps card JSON)
- Emits verifiable-claim items list (in-memory)

**Stage 2: Verify claim batches**
- Model: `claude-sonnet-4-6`
- `call_claude(thinking=False)`, `max_tokens=16000`, `temperature=0.0`
- **N parallel batches (~25 claims each), max 4 workers**
- System: `persona_pass_7pre_verify_batch.md` (88 lines)
- User: `persona_pass_7pre_verify_batch_user.md` (14 lines) — claim batch + primary_texts + dossier
- 1 retry on transient JSON failures

**Stage 3: Boddice tag check**
- Model: `claude-sonnet-4-6`
- `call_claude(thinking=False)`, `max_tokens=8000`, `temperature=0.0`
- **Parallel with Stage 2**
- System: `persona_pass_7pre_boddice_check.md` (55 lines)
- User: `persona_pass_7pre_boddice_check_user.md` (5 lines, wraps card JSON)

**Aggregation:** Python unions Stage 2 + Stage 3 → `05_validation/01_pass_7_pre_citation.json`.

**On any-stage failure:** writes `VERIFICATION_SKIPPED` sentinel.

**Orphaned files:** `persona_pass_7pre_citation.md` + `_user.md` are the legacy single-shot prompts — superseded by FU#2, kept on disk but not called. Eligible for deletion.

#### 3.7.2 Pass 7-anachronism — TimeChara temporal check *(NEW v4)*

5-model fallback ladder:

**Attempt 1: OpenAI `gpt-5.4` (high reasoning)**
- `chat.completions.create` with `reasoning_effort="high"`
- `max_tokens=16384`, temperature omitted

**Attempt 2: OpenAI `gpt-4.1`** — `max_tokens=16384`, `temperature=0.0`
**Attempt 3: OpenAI `o3` (reasoning)** — `max_tokens=16384`, temperature omitted
**Attempt 4: OpenAI `gpt-4o`** — `max_tokens=16384`, `temperature=0.0`
**Attempt 5: Google `gemini-2.5-pro`** — `max_output_tokens=16384`, `temperature=0.0`

System: `persona_pass_7_anachronism.md` (94 lines). User: inline.

**On all-fail:** writes SKIPPED sentinel.

**Output:** `05_validation/02_pass_7_anachronism.json` with `anachronism_flags[]` (each: `category`, `field_path`, `problematic_text`, `reason`, `suggested_fix`, `severity`) + `overall ∈ {PASS, REVISION_NEEDED}`.

**Post-hook (`run_persona_pipeline.py:980–1011`):** if `overall == REVISION_NEEDED`, merges `anachronism_flags` as `field_issues` into Pass 7a result with field-path → pass mapping; escalates 7a `overall` to REVISION_NEEDED if not already.

#### 3.7.3 Pass 7a — Cross-Model Validation *(ladder updated v4)*

Same 5-model fallback ladder as Pass 7-anachronism:

- Attempt 1: gpt-5.4 (high)
- Attempt 2: gpt-4.1
- Attempt 3: o3 (reasoning)
- Attempt 4: gpt-4o
- Attempt 5: Gemini 2.5 Pro
- All fail: writes SKIPPED sentinel — non-blocking

System: `persona_pass_7a_cross_model.md` (74 lines). User: `persona_pass_7a_cross_model_user.md` (5 lines, renders card as JSON).

`max_tokens=16384`, `temperature=0.0`.

**FU#33 P2 INCONSISTENT merge** (`run_persona_pipeline.py:1013–1078`): finds INCONSISTENT items from Pass 7-pre, maps field paths to passes, injects into 7a `field_issues`. Path-to-pass mapping covers passes 2/3/4a/4b/5/6.

Output: `05_validation/03_pass_7a_cross_model.json` with `field_issues[]` + `overall` + `revision_target_passes`.

#### 3.7.4 Pass 7a-FIX — Linear patcher (FU#13) *(NEW v4 — REPLACES v3.10 revision loop)*

Fires only if `pass7a.result.overall == REVISION_NEEDED` AND `_fix_log.json` doesn't exist (idempotent).

**Pre-hook (FU#5):** snapshots `04_generation/` + `05_validation/` → `04_generation/_snapshots/pre_fix_pass/`.

- Model: `claude-opus-4-7`
- `call_claude(thinking=True)`, `max_tokens=32000`, `temperature=1.0`
- System: `persona_pass_7a_fix.md` (147 lines)
- User: `persona_pass_7a_fix_user.md` (47 lines) — `field_issues` + `relevant_pass_outputs` + voice context (`rhetorical_mode`, `register_and_tone`, `characteristic_moves`, `translation_protocol`, `knowledge_boundary` for FU#44 register-drift + internal-contradiction guardrails)

**Single call** — not a loop. `flows/shared/patch_walker.apply_patch_in_place()` applies each patch (`{pass_id, field_path, new_value, rationale}`) to in-memory dict + writes cache file.

After applying: invalidates pass7pre/7anach/7a/7b/7c/derive_raw/assembled_card/provocateur/rubric caches; **re-fires validators once** (Pass 7-pre, 7-anachronism, 7a → +3 calls). Fix log: `02_merge/_fix_log.json`.

**Cost:** ~$1 per voice vs ~$5–10 per loop in v3.10.

**Why this works better than v3.10's revision loop:** writer Opus + thinking + critique tends to expand rather than trim; surgical patches operate on field paths only, no rewriter context.

#### 3.7.5 Pass 7b — Worked Provocations
- Model: `claude-opus-4-7`
- `call_claude(thinking=True)`, `max_tokens=24000`, `temperature=1.0`
- System: `persona_pass_7b_smoke_test.md` (88 lines, Jinja with `conference_context`, `voice_mode`, `subtype`)
- User: `persona_pass_7b_smoke_test_user.md` (6 lines, wraps card JSON)
- Output: `05_validation/04_pass_7b_smoke_test.json` (`smoke_test_chains` field)

#### 3.7.6 Pass 7c — Negative Constraints
**Primary: Gemini `gemini-2.5-pro`** (preferred — avoids self-preference bias)
- `call_gemini`, `max_output_tokens=16384`, `temperature=0.0`
- System rendered with `claude_fallback=False`

**Fallback: Claude `claude-sonnet-4-6`** (bias-aware variant)
- `call_claude(thinking=False)`, `max_tokens=8192`, `temperature=0.0`
- System rendered with `claude_fallback=True` (prepends bias-awareness instruction)

System: `persona_pass_7c_negative.md` (102 lines). User: `persona_pass_7c_negative_user.md` (21 lines).

**Output:** `05_validation/05_pass_7c_negative.json`. **Overwrites** `banned_language` + `banned_modes` from Pass 4a seeds.

### 3.8 Phase 4 — Derive *(model upgraded Sonnet→Opus + thinking)*

#### 3.8.1 Derive — `_derive`
- Model: `claude-opus-4-7` *(was `claude-sonnet-4-6` in v3.10)*
- `call_claude(thinking=True)`, `max_tokens=24000`, `temperature=1.0` *(was 8192, 0.1, thinking=False)*
- System: `persona_derive.md` (100 lines)
- User: `persona_derive_user.md` (6 lines, wraps full card JSON)
- Output: `provocateur_profile` (8 fields) + `evaluation_rubric` (9 test prompts)
- Files: `06_derive/{00_derive_raw, 01_provocateur_profile, 02_evaluation_rubric}.json`

#### 3.8.2 Chat artifact (FU#41) *(NEW v4)*

`flows/shared/chat_prompt_builder.write_chat_system_prompt()`. **No LLM.** Pure Python.

**Strips 11 items** from assembled card:
- 5 chat-incompatible top-level: `metadata`, `smoke_test_chains`, `reference_only_passages`, 2 continuity blocks
- 5 spec-shell meta top-level: `voice_name`, `voice_mode`, `pipeline_version`, `generated_date`, `council_member_name`
- 1 nested: `curated_corpus_passages.corpus_metadata`

Output: `06_derive/03_chat_system_prompt.json`. Operator paste-target for Claude project custom instructions.

---

## 4. Prompt file inventory

### 4.1 Runtime prompts — `runtime/flows/shared/prompts/`

| Call site | Prompt file | Lines |
|---|---|---|
| Speaker ID | `transcription_speaker_id.md` | 81 |
| Cleaning | `transcription_cleaning.md` | 35 |
| Researcher Extraction | `researcher_extraction.md` | 39 |
| Researcher Clustering | `researcher_clustering.md` | 109 |
| Researcher Theming | `researcher_theming.md` | 90 |
| Provocateur Triage Voice | `provocateur_triage_voice.md` | 73 |
| Provocateur Triage Flags | `provocateur_triage_flags.md` | 66 |
| Provocateur Formulation | `provocateur_formulation.md` | 194 |

`_archive/` contains 4 superseded v1/v2-draft prompts (kept for historical reference).

### 4.2 Personas prompts — `personas/flows/shared/prompts/`

~50 files. Jinja2 template syntax throughout. Loaded via `flows/shared/io.load_prompt()`.

| Phase | System prompt | User prompt |
|---|---|---|
| Pass 0a | `pass_0a_voice_config.md` | (inline) |
| Pass 0b base | `pass_0b_header.md` + `pass_0b_{human, fictional, non_human_organism, non_human_system}.md` + `pass_0b_footer.md` + `_pass_0b_research_discipline.md` | — (template, no LLM) |
| Pass 0b dispatcher | `pass_0b_dr_prompt.md` | — |
| **Pass 0b tailor** *(NEW v4)* | `pass_0b_tailor.md` | (inline) |
| Pass 1a (Perplexity) | `persona_pass_1a_{human, fictional, non_human_organism, non_human_system}.md` (4 variants) | — |
| Pass 1b (Gemini) | `persona_pass_1b_{human, fictional, non_human_organism, non_human_system}.md` (4 variants) | — |
| **Pass 1.1 BIOGRAPHICAL** *(NEW v4)* | `pass_1_1_merge.md` | (synthesized inline) |
| **Pass 1.2 INTELLECTUAL** | `pass_1_2_merge.md` | (synthesized inline) |
| **Pass 1.3 REASONING** | `pass_1_3_merge.md` | (synthesized inline) |
| **Pass 1.4 VOICE** | `pass_1_4_merge.md` | (synthesized inline) |
| **Pass 1.5 BOUNDARIES** | `pass_1_5_merge.md` | (synthesized inline) |
| **Pass 1.6 CORPUS** | `pass_1_6_merge.md` | (synthesized inline) |
| **Pass 1.7 Coherence** *(NEW v4)* | `pass_1_7_coherence.md` | (synthesized inline) |
| Pass 1d Excerpt Selection | (inline) | `persona_pass_1d_excerpt_selection.md` |
| Pass 2 | `persona_pass_2_identity_boundaries.md` | `persona_pass_2_user.md` |
| Pass 3 | `persona_pass_3_intellectual_core.md` | `persona_pass_3_user.md` |
| Pass 4a | `persona_pass_4a_voice.md` | `persona_pass_4a_user.md` |
| Pass 4b | `persona_pass_4b_artifact.md` | `persona_pass_4b_user.md` |
| Pass 5 | `persona_pass_5_engagement.md` | `persona_pass_5_user.md` |
| Pass 6 | `persona_pass_6_corpus.md` | `persona_pass_6_user.md` |
| CT (after each pass 2/3/4a/4b) | (inline) | `persona_coherence_threading.md` |
| **Pass 7-pre Stage 1 extract** *(NEW v4)* | `persona_pass_7pre_extract.md` | `persona_pass_7pre_extract_user.md` |
| **Pass 7-pre Stage 2 verify** *(NEW v4)* | `persona_pass_7pre_verify_batch.md` | `persona_pass_7pre_verify_batch_user.md` |
| **Pass 7-pre Stage 3 boddice** *(NEW v4)* | `persona_pass_7pre_boddice_check.md` | `persona_pass_7pre_boddice_check_user.md` |
| Pass 7-pre legacy *(ORPHANED)* | `persona_pass_7pre_citation.md` | `persona_pass_7pre_citation_user.md` |
| **Pass 7-anachronism** *(NEW v4)* | `persona_pass_7_anachronism.md` | (inline) |
| Pass 7a | `persona_pass_7a_cross_model.md` | `persona_pass_7a_cross_model_user.md` |
| **Pass 7a-FIX** *(NEW v4)* | `persona_pass_7a_fix.md` | `persona_pass_7a_fix_user.md` |
| Pass 7b | `persona_pass_7b_smoke_test.md` | `persona_pass_7b_smoke_test_user.md` |
| Pass 7c | `persona_pass_7c_negative.md` | `persona_pass_7c_negative_user.md` |
| Derive | `persona_derive.md` | `persona_derive_user.md` |

---

## 5. Environment variables that affect LLM call behavior

### 5.1 Runtime

| Variable | Default | Effect |
|---|---|---|
| `ANTHROPIC_API_KEY` | — | Required. |
| `ASSEMBLYAI_API_KEY` | — | Required. |
| `CLAUDE_MODEL` | Sonnet in transcription, Opus elsewhere | Shared. Transcription default `claude-sonnet-4-6`; Researcher + Provocateur default `claude-opus-4-7`. |
| `TRANSCRIPTION_CLAUDE_MODEL` | `CLAUDE_MODEL` | Per-flow override for transcription cleaning. |
| `RESEARCHER_CLAUDE_MODEL` | `CLAUDE_MODEL` | Per-flow override. |
| `PROVOCATEUR_CLAUDE_MODEL` | `CLAUDE_MODEL` | Per-flow override. |
| `TRANSCRIPTION_SPEAKER_ID_MODEL` | `CLAUDE_MODEL` | Per-run override for Speaker ID. Flip to `claude-opus-4-7` for hard sessions. |
| `TRANSCRIPTION_CACHE` | unset | `"1"` enables Prefect AssemblyAI cache (30-day) — dev only. |
| `RESEARCHER_THINKING` | `"1"` | `"0"` disables adaptive thinking across Researcher tasks. |
| `PROVOCATEUR_THINKING` | `"1"` | `"0"` disables adaptive thinking across Provocateur tasks. |
| `PROVOCATEUR_FORMULATION_BATCH` | `4` | Parallel Formulation calls per batch. |
| `PROVOCATEUR_BATCH_WAIT_S` | `20` | Seconds between batches. |

### 5.2 Personas

| Variable | Default | Effect |
|---|---|---|
| `ANTHROPIC_API_KEY` | — | Required. |
| `PERPLEXITY_API_KEY` | — | Required for Pass 1a. |
| `GOOGLE_API_KEY` | — | Required for Pass 1b + Pass 7-anach/7a fallback + Pass 7c primary. |
| `OPENAI_API_KEY` | — | Required for Pass 7-anach + Pass 7a (5-model ladder primary). |
| `CLAUDE_MODEL` | `claude-opus-4-7` | Read by `call_claude` only when `model` arg is None — most v4 passes hardcode the model. |
| `PERPLEXITY_MODEL` | `sonar-deep-research` | Override via `call_perplexity`. |
| `GEMINI_MODEL` | `gemini-2.5-pro` | Override via `call_gemini`. |
| `OPENAI_MODEL` | `gpt-4o` | Override via `call_openai` — but Pass 7-anach + Pass 7a hardcode the 5-model ladder, overriding this env. |
| `AI_ASSEMBLY_PROJECT_ROOT` | — | Tier 3 PROJECT_ROOT env-var resolution path (precedence: CLI `--project` > this env > hard fail). |

---

## 6. Shared wrapper behavior

### 6.1 `call_claude` (`personas/flows/shared/clients.py`)

The personas pipeline's only Claude wrapper. Behavior controlled by:

- **`thinking: bool`** — `thinking=True` enables adaptive thinking via `{"type": "adaptive"}`. **No budget argument needed** — adaptive mode sets its own budget. (v3.10 used the older `"enabled"` + `budget_tokens` pattern; refactored to adaptive.)
- **Streaming heuristic** — automatic. `use_streaming = max_tokens >= 16384 or thinking`. Threshold matches Anthropic SDK's non-streaming cutoff.
- **JSON extraction when `response_format_json=True`** — strips ```json fences and trailing content. On `json.JSONDecodeError`, if `stop_reason == "max_tokens"` raises `RuntimeError` blaming budget; otherwise re-raises with diagnostics.
- **Manifest recording (FU#9):** if `slug` + `pass_name` kwargs are passed, records per-call `{model, input_tokens, output_tokens, wall_seconds, thinking_tokens}` to `voices/<slug>/_manifest.json`. The chunk_runner uses these; the main orchestrator does not consistently pass them — see §7.8.

**Streaming collection:** iterates `content_block_delta` events with `delta.type == "text_delta"`. Thinking tokens are not collected (filtered out). `stream.get_final_message()` provides usage totals.

**FU#9 max_tokens monitoring:** `clients.py:146–152` logs to stderr on `stop_reason == "max_tokens"`.

### 6.2 `call_perplexity` (clients.py)

REST POST to `https://api.perplexity.ai/chat/completions`. OpenAI-compatible request format. Splits the response on `<think>...</think>` — `text` is the deliverable, `think` is the chain-of-thought trace.

### 6.3 `call_gemini` (clients.py)

`google.genai.Client(...).models.generate_content(...)`. `thinking_budget=None` (default) lets the model's own default apply — required for gemini-2.5-pro, which only operates in thinking mode and rejects budget=0.

### 6.4 `call_openai` (clients.py)

`client.chat.completions.create(...)`. Auto-detects reasoning models (`o1`, `o3`, `o4`, `gpt-5.4` prefixes) and switches to `max_completion_tokens` + omits temperature + accepts `reasoning_effort` parameter.

---

## 7. Historical parameter discrepancies

### 7.1 Pass 0a "adaptive thinking" comment is misleading *(resolved 2026-04-18)*
K.0 refactor (`commit 4666fa1`) renamed the `call_claude` thinking parameter to `thinking: bool`. Parameter and comment are consistent.

### 7.2 Formulation `flavor` field — spec ↔ code mismatch *(resolved 2026-04-18)*
Spec doc fixed to match code (stage-direction text, not lens value).

### 7.3 `briefing_narrative` points at `structured` but JSON key is `full_theme_record` *(resolved 2026-04-18)*

### 7.4 Anthropic SDK version docs ≠ reality *(resolved 2026-04-18)*
Both venvs pinned `0.94.1`. Separate venvs are real but their version-mismatch justification is fictional.

### 7.5 DR validation floor vs prompt ask *(resolved 2026-04-18)*

### 7.6 Personas pipeline_version drift *(resolved 2026-04-18, re-resolved 2026-04-27)*
2026-04-18: v3.10 string aligned across spec doc, runner, and example JSON.
**2026-04-27 (v4):** `pipeline_version` bumped `"3.10"` → `"4.0"` in `run_persona_pipeline.py:1587`. Plato (shipped 2026-04-26) carries `"3.10"`; cards generated thereafter carry `"4.0"`. Schema unchanged; the bump names what the implementation has actually been since arch-03 + Phase B + FU#1–50 landed.

### 7.7 Transcription intentionally omits thinking even on Opus
Speaker ID (§2.1.2) and Cleaning (§2.1.3) exempted from "thinking ON for every Opus 4.7 call" rule per `docs/AI_Assembly_Transcription_Pipeline.md`: Speaker ID's output is too small (<2K tokens) for thinking's latency cost to be worth it; Cleaning is per-turn-local. If `TRANSCRIPTION_SPEAKER_ID_MODEL` or `CLAUDE_MODEL` is set to Opus, thinking stays off intentionally.

### 7.8 Manifest recording incomplete on main orchestrator *(open, low priority)*
`call_claude` records to `_manifest.json` only when `slug` + `pass_name` kwargs are passed. `chunk_runner.py` passes them; `run_persona_pipeline.py` calls do NOT consistently pass them. Result: manifest captures Pass 1.1–1.7 telemetry, but Pass 2/3/4a/4b/5/6/7-* telemetry is absent from `_manifest.json`. Not fixed because the data is also captured in per-pass JSON output files. Worth fixing for cost analytics if the manifest becomes the canonical telemetry.

### 7.9 `paths.merge_chunk()` not used by chunk_runner *(internal inconsistency, low priority)*
`paths.merge_chunk(slug, n)` returns flat-file path `02_merge/0N_pass_1_N_<name>.json` but `chunk_runner.run_chunk()` writes to subdirectory `02_merge/pass_1_N/<key>.json`. The function exists in paths.py but isn't called by chunk_runner. May be used by migration scripts or tests. Two surfaces should converge.

### 7.10 Orphaned legacy Pass 7-pre prompts *(open, cleanup candidate)*
`persona_pass_7pre_citation.md` (112 lines) and `persona_pass_7pre_citation_user.md` (13 lines) are the v3.10 single-shot Pass 7-pre prompts. Superseded by FU#2 3-stage architecture (extract/verify/boddice). Not imported or referenced in any `.py` file. Eligible for deletion.

### 7.11 Hardcoded paths NOT in `paths.py` *(open, cleanup candidate)*
- `02_merge/_fix_log.json` hardcoded at `run_persona_pipeline.py:1253`. No `paths.fix_log()` helper.
- `04_generation/_snapshots/pre_fix_pass/` hardcoded inside `_pass_7a_fix()` at line 1149.
- `06_derive/03_chat_system_prompt.json` hardcoded at line 1697. No `paths.chat_system_prompt()` helper.
Worth promoting to `paths.py` for consistency with the rest of the path conventions.

---

## 8. What is NOT an LLM call

For completeness:

- **Selection** (Provocateur Stage 2) — pure Python, deterministic 9-step algorithm
- **Packaging** (Provocateur Stage 4) — pure Python, two-view briefings
- **Merge-clusters-and-themes** (Researcher post-theming) — pure Python
- **FFmpeg normalize + ffprobe validate** (Ingest) — subprocess
- **Pass 0b base render** — Jinja2 only
- **Pass 0b tailor** *is* an LLM call (NEW v4) — see #14
- **Split tailored prompt** — pure Python text split
- **Pass 1c-extract** — pure Python regex via `url_extract.py` (NEW: was Sonnet in v3.10)
- **Pass 1c fetch** — HTTP + SSRF guards
- **Wikipedia search + summary** — REST
- **Pass 1.7 Coherence** *(Stage A + Stage C are Python; Stage B is an LLM call — see #21)*
- **Pass 6.5-clean** — pure Python regex (NEW v4)
- **FU#33 P2 INCONSISTENT merge** — pure Python (line 1013–1078)
- **Path-to-pass mapping in 7-anach merge** — pure Python (line 980–1011)
- **Card assembly** — pure Python (line 1583–1681)
- **CARD COMPLETE summary (FU#7)** — pure Python (line 1702–1838)
- **Chat artifact (FU#41)** — pure Python via `chat_prompt_builder.py`
- **Sentinel regen (FU#29)** — `scripts/sentinel_regen.py` is a CLI tool, not pipeline-internal; uses `call_claude` under the hood when running passes
- **Coherence Threading IS an LLM call** — counted in §1 (Sonnet 4.6 + thinking, 16K tokens, temp 0)

---

*Verify against the code before making cost or routing decisions. All line numbers reference the repo state as of 2026-04-27.*
