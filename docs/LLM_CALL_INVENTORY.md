# LLM Call Inventory

**Purpose:** Complete enumeration of every model API call made from this repo, with provider, model, parameters, and prompt source. Written against the actual code (not against the spec docs, which have drifted). Verify against `git show` when things look stale.

**Scope:** All LLM / AI API calls initiated by code in this repo — runtime flows (transcription, researcher, provocateur) and the persona pipeline. External-facing manual steps (the human Claude DR session at claude.ai) are noted for completeness but are not code-initiated.

**Last read against the code:** 2026-04-19. Models and parameters update frequently; re-verify before quoting for budgeting.

---

## 0. Providers and models at a glance

| Provider | SDK | Models used | Where |
|---|---|---|---|
| Anthropic | `anthropic` Python SDK (`==0.94.1` in both venvs) | `claude-opus-4-7`, `claude-sonnet-4-6` | Everywhere Claude is called |
| AssemblyAI | `assemblyai==0.59.0` | `universal-3-pro` | Transcription ASR + diarization |
| Perplexity | Raw HTTP via `requests` | `sonar-deep-research` | Persona Pass 1a |
| Google Gemini | `google-genai` | `gemini-2.5-pro` | Persona Pass 1b, 7a fallback, 7c primary |
| OpenAI | `openai` Python SDK | `o3` (preferred), `gpt-4o` (fallback) | Persona Pass 7a primary |
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
| 10 | Personas · Pass 0a Voice Config | Anthropic | `claude-opus-4-7` | via `call_claude` (streams because max_tokens≥16384) | 24000 | **Off** (see §6.1) | 1.0 | 1× retry on `RateLimitError`/`APIError`/`JSONDecodeError`/`IncompleteResponse` (wait 15s) | 1 per voice |
| 11 | Personas · Pass 1a Perplexity | Perplexity | `sonar-deep-research` (env: `PERPLEXITY_MODEL`) | `POST /chat/completions` (REST) | — | — | 0.0 | None; 900s timeout | 1 per voice |
| 12 | Personas · Pass 1b Gemini | Google | `gemini-2.5-pro` (env: `GEMINI_MODEL`) | `generate_content` | 16384 (max_output_tokens) | Model default (2.5-pro requires thinking) | 0.2 | None | 1 per voice |
| 13 | Personas · Pass 0b DR render | — | — | Jinja2 template only (no API) | — | — | — | — | 1 per voice |
| 14 | Personas · Pass 1a-DR (manual) | Anthropic (claude.ai UI) | `claude-opus-4-7` + Extended Thinking + Deep Research | **Human paste-and-wait** | — | — | — | — | 1 per voice, ~60–180 min wall time |
| 15 | Personas · Pass 1-merge | Anthropic | `claude-opus-4-7` | via `call_claude` (streams because max_tokens≥16384) | 16000 | Off | 0.0 | 1× retry on failure | 1 per voice |
| 16 | Personas · Pass 1c-extract | Anthropic | `claude-sonnet-4-6` | via `call_claude` (non-streaming) | 4096 | Off | 0.0 | 1× retry | 1 per voice (unless manual override) |
| 17 | Personas · Pass 1c fetch | — | — | HTTP fetch of primary texts | — | — | — | per-URL exception handling, no retry | N URLs per voice |
| 18 | Personas · Pass 1d Excerpt Selection | Anthropic | `claude-sonnet-4-6` | via `call_claude` (non-streaming) | 4096 | Off | 0.0 | 1× retry | 1 per voice |
| 19 | Personas · Pass 2 Identity | Anthropic | `claude-opus-4-7` | via `call_claude` (streams) | 24000 | Adaptive | 1.0 | 1× retry | 1 per voice (+ up to 2 in revision loop) |
| 20 | Personas · CT Pass 2 | Anthropic | `claude-sonnet-4-6` | via `call_claude` (non-streaming) | 2048 | Off | 0.0 | 1× retry | 1 per voice |
| 21 | Personas · Pass 3 Intellectual Core | Anthropic | `claude-opus-4-7` | via `call_claude` (streams) | 24000 | Adaptive | 1.0 | 1× retry | 1 per voice (+ revisions) |
| 22 | Personas · CT Pass 2+3 | Anthropic | `claude-sonnet-4-6` | via `call_claude` (non-streaming) | 2048 | Off | 0.0 | 1× retry | 1 per voice |
| 23 | Personas · Pass 4a Voice | Anthropic | `claude-opus-4-7` | via `call_claude` (streams) | 24000 | Adaptive | 1.0 | 1× retry | 1 per voice (+ revisions) |
| 24 | Personas · CT Pass 2+3+4a | Anthropic | `claude-sonnet-4-6` | via `call_claude` (non-streaming) | 2048 | Off | 0.0 | 1× retry | 1 per voice |
| 25 | Personas · Pass 4b Artifact | Anthropic | `claude-sonnet-4-6` | via `call_claude` (non-streaming) | 6144 | Off | 0.2 | 1× retry | 1 per voice (+ revisions) |
| 26 | Personas · CT Pass 2+3+4 | Anthropic | `claude-sonnet-4-6` | via `call_claude` (non-streaming) | 2048 | Off | 0.0 | 1× retry | 1 per voice |
| 27 | Personas · Pass 5 Engagement | Anthropic | `claude-opus-4-7` | via `call_claude` (streams) | 16000 | Adaptive | 1.0 | 1× retry | 1 per voice (+ revisions) |
| 28 | Personas · Pass 6 Corpus Curation | Anthropic | `claude-sonnet-4-6` | via `call_claude` (non-streaming) | 8000 | Off | 0.1 | 1× retry | 1 per voice (+ revisions) |
| 29 | Personas · Pass 7-pre Citation | Anthropic | `claude-sonnet-4-6` | via `call_claude` (streams) | 24000 | Off | 0.0 | 1× retry | 1 per voice |
| 30a | Personas · Pass 7a Cross-Model primary | OpenAI | `o3` (tried first) | `chat.completions.create` (reasoning mode: `max_completion_tokens`, no temp) | 8192 | — | omitted | 1× retry | 1 per voice |
| 30b | Personas · Pass 7a Cross-Model secondary | OpenAI | `gpt-4o` | `chat.completions.create` | 8192 | — | 0.0 | 1× retry | Only if o3 fails |
| 30c | Personas · Pass 7a Cross-Model fallback | Google | `gemini-2.5-pro` | `generate_content` | 16384 | Model default | 0.0 | None | Only if both OpenAI attempts fail |
| 31 | Personas · Pass 7b Worked Provocations | Anthropic | `claude-opus-4-7` | via `call_claude` (streams) | 24000 | Adaptive | 1.0 | 1× retry | 1 per voice |
| 32a | Personas · Pass 7c Negative Constraints primary | Google | `gemini-2.5-pro` | `generate_content` | 16384 | Model default | 0.0 | None | 1 per voice |
| 32b | Personas · Pass 7c Negative Constraints fallback | Anthropic | `claude-sonnet-4-6` | via `call_claude` (non-streaming) | 8192 | Off | 0.0 | 1× retry | Only if Gemini fails |
| 33 | Personas · Derive | Anthropic | `claude-sonnet-4-6` | via `call_claude` (non-streaming) | 8192 | Off | 0.1 | 1× retry | 1 per voice |
| 34 | Personas · Wikipedia | Wikipedia | — | REST (opensearch + page summary) | — | — | — | None | 1–6 per Pass 0a interactive run |

**Runtime call count per night (12 voices, ~20 themes, ~40 assigned pairs):** ASR 6–9 · Speaker ID 6–9 · Cleaning 6–9 · Extraction 6–9 · Clustering 1 · Theming 1 · Triage Voice 12 · Triage Flags 1 · Formulation ~40 → **~80–90 total LLM calls per night**.

**Personas call count per voice:** 0a 1 · 1a 1 · 1b 1 · 1-merge 1 · 1c-extract 1 · 1d 1 · Pass 2 1 + CT 1 · Pass 3 1 + CT 1 · Pass 4a 1 + CT 1 · Pass 4b 1 + CT 1 · Pass 5 1 · Pass 6 1 · 7-pre 1 · 7a 1 · 7b 1 · 7c 1 · Derive 1 → **~20 calls per voice, plus up to 2× extra through Passes 2–6 in a revision loop**. 12 voices → ~240–280 calls for the full pre-Athens build.

---

## 2. Runtime pipeline calls (detail)

### 2.1 Transcription — `runtime/flows/transcription_flow.py`

#### 2.1.1 AssemblyAI ASR — `transcribe_with_assemblyai` (L302-360)
- **Provider:** AssemblyAI
- **Model:** `universal-3-pro` (injected via `config.raw.speech_models`)
- **Config:**
  - `speaker_labels=True`
  - `speakers_expected = expected_speaker_count + 2` (from `session.json`)
  - `language_detection=True`
  - `keyterms_prompt = build_vocabulary(session)` (roster proper nouns)
- **Retry:** Prefect `@task(retries=3, retry_delay_seconds=exponential_backoff(backoff_factor=10), retry_jitter_factor=0.3)`
- **Cache:** Optional dev-only via `TRANSCRIPTION_CACHE=1` env → enables `cache_key_fn=task_input_hash` with 30-day expiration. **Off in prod** (every session is fresh).
- **Notes:** SDK 0.59.0 drift forces `config.raw.speech_model=None` and `config.raw.speech_models=["universal-3-pro"]`. `keyterms_prompt` and `prompt` cannot both be set.

#### 2.1.2 Speaker Identification — `identify_speakers` (L368-419)
- **Provider:** Anthropic
- **Model resolution:** `SPEAKER_ID_MODEL = os.environ.get("TRANSCRIPTION_SPEAKER_ID_MODEL", CLAUDE_MODEL)`. `CLAUDE_MODEL` defaults to `claude-sonnet-4-6`. Override to `claude-opus-4-7` for hard sessions.
- **Method:** `client.messages.create` (non-streaming). Output is small (mappings + flags, ~2K tokens).
- **Parameters:**
  - `max_tokens=4096`
  - `system=SPEAKER_ID_SYSTEM` (loaded from `runtime/flows/shared/prompts/transcription_speaker_id.md`)
  - Temperature: not set (SDK default)
  - No thinking (spec: thinking not used in transcription even on Opus)
- **Retry:** Prefect `@task(retries=2, retry_delay_seconds=exponential_backoff(backoff_factor=5))`
- **Output parsed via:** `extract_json(resp.content[0].text)`

#### 2.1.3 Cleaning — `clean_transcript` (L427-469)
- **Provider:** Anthropic
- **Model:** `CLAUDE_MODEL` (default `claude-sonnet-4-6`)
- **Method:** `client.messages.stream` as context manager. **Streaming is mandatory** — SDK refuses non-streaming requests above ~21K max_tokens.
- **Parameters:**
  - `max_tokens=64000` (CLAUDE_MAX_TOKENS)
  - `system=CLEANING_SYSTEM` (loaded from `runtime/flows/shared/prompts/transcription_cleaning.md`)
- **Retry:** Prefect `@task(retries=2, retry_delay_seconds=exponential_backoff(backoff_factor=5))`
- **Observability:** Warns if `final.usage.output_tokens > CLAUDE_MAX_TOKENS * 0.8`.

### 2.2 Researcher — `runtime/flows/researcher_flow.py`

All three tasks share:
- Provider: Anthropic
- Model: `CLAUDE_MODEL` (env-overridable; default `claude-opus-4-7`)
- Thinking: adaptive via `_thinking_kwargs(budget)` if `RESEARCHER_THINKING` env ≠ `"0"` (default on). `type: "adaptive"`, `temperature: 1.0`
- Retry: Prefect `@task(retries=2, retry_delay_seconds=exponential_backoff(backoff_factor=5))`
- Method: `client.messages.stream` (non-negotiable when thinking on)
- Resume: per-session extraction files cached; clustering/theming re-run every invocation

#### 2.2.1 Extraction — `extract_session` (L261-315)
- `max_tokens=40000` (EXTRACTION_MAX_TOKENS; budget includes thinking tokens)
- System: `EXTRACTION_SYSTEM` from `runtime/flows/shared/prompts/researcher_extraction.md`
- User: `build_extraction_user_prompt(pkg, session_id)` — title/description/roster/speakers_present/turns/verify_markers
- Warning: if `out_tokens > 40000 * 0.8`

#### 2.2.2 Clustering Round 1 — `cluster_extractions` (L323-444)
- `max_tokens=40000` (CLUSTERING_MAX_TOKENS)
- System: `CLUSTERING_SYSTEM` from `researcher_clustering.md`
- **Input stripped to `{ref, extraction, context}`** — real namespaced IDs and provenance metadata withheld so Opus can't use session prefix as a grouping shortcut. Shuffled with `random.Random(42)`.
- Post-call: validate with `_validate_clusters` (dedup, prune empties, append orphans to isolates, detect hallucinated refs)

#### 2.2.3 Theming Round 2 — `group_clusters_into_themes` (L452-520)
- `max_tokens=24000` (THEMING_MAX_TOKENS)
- System: `THEMING_SYSTEM` from `researcher_theming.md`
- **Input is cluster-level only**: `{cluster_id, cluster_title, cluster_abstract}` — no raw extractions. Shuffled with same seed 42.
- Post-call: `_validate_themes` (dedup cluster_ids, prune empty themes, promote orphan clusters to single-cluster themes)

### 2.3 Provocateur — `runtime/flows/provocateur_flow.py`

All three LLM tasks go through `_stream_and_parse` (L195-256):
- Provider: Anthropic
- Model: `CLAUDE_MODEL` (default `claude-opus-4-7`)
- Thinking: adaptive if `PROVOCATEUR_THINKING=1` (default on). `_thinking_kwargs()` returns `{"thinking": {"type": "adaptive"}}`
- Temperature: not set by `_stream_and_parse` (SDK default with thinking enabled is 1.0)
- Method: `client.messages.stream`
- Empty-stream guard: if `full_text.strip()` is empty, raises ValueError blaming thinking eating the budget
- JSON parse via `extract_json`; on JSONDecodeError, includes first-500-char preview
- Retry: Prefect `@task(retries=5, retry_delay_seconds=exponential_backoff(backoff_factor=15))` — longer than runtime's 2× because rate-limit at Opus 4.7's tier is the primary failure mode

#### 2.3.1 Triage Voice — `triage_voice` (L287-351)
- `max_tokens=40000` (TRIAGE_MAX_TOKENS)
- System: `TRIAGE_VOICE_SYSTEM` from `provocateur_triage_voice.md`, Jinja-filled with `voice_profile`, `collective_landscape`, `audience`, `themes_with_clusters`
- **Runs 12 times in parallel** (one per council member) via Prefect `.submit()`
- Per-voice checkpoint at `triage_voices/{voice_slug}.json` — written atomically before return; resumed automatically on restart

#### 2.3.2 Triage Flags — `triage_flags` (L354-404)
- Same parameters as Triage Voice
- System: `TRIAGE_FLAGS_SYSTEM` from `provocateur_triage_flags.md`
- **1 call per night**, runs in parallel with the 12 Triage Voice calls
- Checkpoint: `triage_flags.json`

#### 2.3.3 Formulation — `formulate_for_member` (L741-821)
- `max_tokens=40000` (FORMULATION_MAX_TOKENS)
- System: `FORMULATION_SYSTEM` from `provocateur_formulation.md`, Jinja-filled with `collective_landscape`, `member_profile`, `audience`, `theme_friction_level`, `theme_fault_line_description_or_none`, `theme_material`
- **Runs N times** where N = number of (theme, voice) pairs from Selection (≈40 on dev_msc_test)
- Batched: `PROVOCATEUR_FORMULATION_BATCH` (default 4) concurrent submissions per batch; `PROVOCATEUR_BATCH_WAIT_S` (default 20) sleep between batches. Final batch has no trailing sleep.
- Per-pair checkpoint: `formulations/{theme_id}__{voice_slug}.json`

### 2.4 Selection — pure Python, no LLM

`python_select` in `provocateur_flow.py` L414-697 is deterministic. Nine-step algorithm over the Triage outputs + `selection_parameters` from `council_config.json`. Listed here to make clear it is **not** an LLM call despite living in the same flow.

---

## 3. Persona Pipeline calls (detail)

All personas calls flow through `personas/flows/shared/clients.py`. See §6.1 for wrapper behavior.

### 3.1 Phase 0 — Intake

#### 3.1.1 Pass 0a Voice Config — `personas/run_pass0a_voice_config.py` L179-216
- **Provider:** Anthropic (via `call_claude`)
- **Model:** `"claude-opus-4-7"` (hardcoded)
- **Parameters:**
  - `max_tokens=24000` → triggers streaming in `call_claude` because ≥16384
  - `temperature=1.0`
  - `thinking=True` → adaptive thinking enabled (see §6.1)
  - `response_format_json=True`
- **System prompt:** `personas/flows/shared/prompts/pass_0a_voice_config.md` (140 lines, hardcoded file read)
- **User:** `VOICE_INPUT` JSON with `name`, `conference_context`, optional `wikipedia_extract`/`wikipedia_description`/`wikipedia_url` or `disambiguation_hint`
- **Retry:** `_call_with_retry` — 1 attempt + 15s wait + 1 retry. Catches `RuntimeError`, `json.JSONDecodeError`, `anthropic.APIError`, `anthropic.RateLimitError`, `IncompleteResponse`
- **Critique retry:** On `InputRejected` after parse (validation failure on enum fields), retries once with critique appended
- **Output:** `{voice_config, review_doc}` — voice config written to `inputs/voices/<slug>.json`, review to `<slug>_pass0a_review.md`

#### 3.1.2 Wikipedia search + summary — `personas/flows/shared/wikipedia.py`
- Not an LLM; REST calls for Pass 0a grounding.
- OpenSearch: `https://en.wikipedia.org/w/api.php` with `action=opensearch`, `limit=5`
- Summary: `https://en.wikipedia.org/api/rest_v1/page/summary/{title}`
- Timeout 10s, no retry

### 3.2 Phase 0.5 — Pre-DR Research

`personas/run_phase0_1_research.py` runs 1a and 1b in a `ThreadPoolExecutor(max_workers=2)`.

#### 3.2.1 Pass 1a Perplexity — `call_perplexity` (clients.py L118-182)
- **Provider:** Perplexity
- **Model:** `sonar-deep-research` via env `PERPLEXITY_MODEL` or SDK default
- **Method:** `requests.post("https://api.perplexity.ai/chat/completions", ...)` — OpenAI-compatible endpoint
- **Parameters:**
  - `temperature=0.0`
  - `return_citations=True`
  - `timeout=900` (15 min)
- **System prompt:** none (user-only)
- **User prompt:** rendered from `persona_pass_1a_research_human.md` (75 lines). Variants for non-human / fictional exist in the spec but the extant prompt file is human-oriented; branching by `type` happens inside the Jinja render per `hostile_sources` flag.
- **Think-block stripping:** response body's `<think>...</think>` chain-of-thought is stripped from `text` into `think` field before return

#### 3.2.2 Pass 1b Gemini — `call_gemini` (clients.py L187-232)
- **Provider:** Google Gemini
- **Model:** `gemini-2.5-pro` via env `GEMINI_MODEL`
- **Method:** `client.models.generate_content` (google-genai SDK)
- **Parameters:**
  - `temperature=0.2`
  - `max_output_tokens=16384`
  - `thinking_budget=None` — lets the model's own default apply. gemini-2.5-pro requires thinking mode.
- **Prompt:** rendered from `persona_pass_1b_broad_scan.md` (14 lines)

#### 3.2.3 Pass 0b DR Render — no API call
- Jinja2 template render only. Output: `inputs/dossiers/_dr_prompts/<slug>_dr_prompt.md` for manual paste into claude.ai.

### 3.3 Phase 1a-DR — Manual paste

Human pastes the rendered DR prompt into claude.ai with **Claude Opus 4.7 + Extended Thinking + Deep Research** enabled. Not a code-initiated call. Produces a ~15–25K word markdown dossier saved to `inputs/dossiers/<slug>_claude_dr.md`, validated by `personas/flows/shared/dr_validation.py` (checks 6 required section headings + ≥5,000 word floor).

### 3.4 Phase 1 — Research Merge (`run_persona_pipeline.py`)

#### 3.4.1 Pass 1-merge — L126-141
- **Model:** `claude-opus-4-7`
- `max_tokens=16000`
- `temperature=0.0`
- `thinking=False`
- `response_format_json=True`
- **System:** `persona_pass_1merge_contradiction_system.md` (1 line)
- **User:** `persona_pass_1merge_three_way_user.md` — renders Perplexity + optional Claude DR + Gemini sources for contradiction detection
- Uses streaming because max_tokens ≥ 16384

#### 3.4.2 Pass 1c-extract — L206-225
- **Model:** `claude-sonnet-4-6`
- `max_tokens=4096`, `temperature=0.0`, `thinking=False`, `response_format_json=True`
- **System:** inline string "You extract primary text URLs from a merged research dossier. Return only valid JSON, no preamble."
- **User:** renders `persona_pass_1c_extract_urls.md` + appends `MERGED DOSSIER: {merged_dossier}`
- Skipped if `voice_input.primary_text_sources` is non-empty (backward compat manual override)

#### 3.4.3 Pass 1c fetch — no LLM
- `fetch_all(primary_text_urls)` in `personas/flows/shared/node1c_fetch.py`
- HTTP fetch of Project Gutenberg / Perseus / archive.org URLs
- SSRF protection: scheme whitelist + RFC 1918 block + 5 MB cap
- Gated by human review flag `primary_texts_reviewed.flag`

#### 3.4.4 Pass 1d Excerpt Selection — L408-430
- **Model:** `claude-sonnet-4-6`
- `max_tokens=4096`, `temperature=0.0`, `thinking=False`, `response_format_json=True`
- **System:** inline string "You are a textual scholar curating excerpt selections for an AI persona's primary-text grounding."
- **User:** renders `persona_pass_1d_excerpt_selection.md` — dossier + structural index of fetched sources
- Skipped if no primary texts fetched

### 3.5 Phase 2 — Section-by-section Generation

All Phase 2 generation passes go through `_claude_pass` (L345-351), which wraps `call_claude` with:
- `thinking=True` enables adaptive thinking (no budget argument needed)
- `max_tokens=24000` default
- `temperature=1.0` default
- `response_format_json=True`

Coherence Threading (CT) compressions run through `_ct_compress` (L354-368):
- **Model:** `claude-sonnet-4-6`
- `max_tokens=2048`, `temperature=0.0`, `thinking=False`
- System: inline "You compress persona fields into a tight summary."
- User: `persona_coherence_threading.md` + prior-pass JSON

#### 3.5.1 Pass 2 Identity & Boundaries — `_pass_2` L372-383
- **Model:** `claude-opus-4-7`
- `max_tokens=24000`, `temperature=1.0`, `thinking=True` (adaptive)
- System: `persona_pass_2_identity_boundaries.md` (131 lines, Jinja-filled with `name`, `type`, `subtype`, `voice_mode`, `hostile_sources`)
- User: `persona_pass_2_user.md` + merged_dossier + optional critique suffix
- Output: 9 fields

#### 3.5.2 CT Pass 2 — called inline L383
- Compresses `pass2["fields"]` → `pass_2_summary`

#### 3.5.3 Pass 3 Intellectual Core — `_pass_3` L387-398
- Same config as Pass 2
- System: `persona_pass_3_intellectual_core.md` (98 lines)
- User: includes `pass_2_summary`
- Output: 5 fields

#### 3.5.4 CT Pass 2+3 — L400
- Compresses merged `pass2 ∪ pass3` fields

#### 3.5.5 Pass 4a Voice — `_pass_4a` L433-446
- Same config as Pass 2/3
- System: `persona_pass_4a_voice.md` (71 lines)
- User: includes `primary_texts` block (from Pass 1d curated excerpts) + `pass_2_3_summary`
- Output: 7 voice fields + `voice_basis` metadata ("corpus-based" or "training-data")
- Requires: `pass1c.passages` non-empty for "corpus-based" quality

#### 3.5.6 CT Pass 2+3+4a — L451
- Compresses merged fields through 4a

#### 3.5.7 Pass 4b Artifact — `_pass_4b` L455-465
- **Model:** `claude-sonnet-4-6` (NOT Opus — lighter task)
- `max_tokens=6144`, `thinking=False`, `temperature=0.2`
- System: `persona_pass_4b_artifact.md` (49 lines)
- User: `persona_pass_4b_user.md` + Pass 4a voice fields
- Output: 8 artifact fields

#### 3.5.8 CT Pass 2+3+4 — L470
- Compresses merged fields through 4b

#### 3.5.9 Pass 5 Engagement — `_pass_5` L474-486
- **Model:** `claude-opus-4-7`
- `max_tokens=16000`, `thinking=True` (adaptive), `temperature=1.0`
- System: `persona_pass_5_engagement.md` (67 lines)
- User: `persona_pass_5_user.md` + full `constitution` + full `reasoning_method` (not compressed — spec wants full)
- Output: 4 engagement fields

#### 3.5.10 Pass 6 Corpus Curation — `_pass_6` L493-518
- **Model:** `claude-sonnet-4-6`
- `max_tokens=8000`, `thinking=False`, `temperature=0.1`
- `response_format_json=True`
- System: `persona_pass_6_corpus.md` (44 lines)
- User: `persona_pass_6_user.md` with `primary_texts`, `merged_dossier`, `constitution`, `concept_lexicon`, `reasoning_method`, Pass 4a voice fields
- Output: 1 field (`curated_corpus_passages`). HALTS if no primary texts.

### 3.6 Phase 3 — Validation

#### 3.6.1 Pass 7-pre Citation Verification — `_pass_7pre` L528-543
- **Model:** `claude-sonnet-4-6`
- `max_tokens=24000`, `temperature=0.0`, `thinking=False`
- `response_format_json=True`
- Streams because max_tokens ≥ 16384
- System: `persona_pass_7pre_citation.md` (93 lines, Jinja-filled with `type`, `voice_mode`, `hostile_sources`)
- User: `persona_pass_7pre_citation_user.md` + assembled card (Passes 2-6) + primary_texts + merged_dossier

#### 3.6.2 Pass 7a Cross-Model Validation — `_pass_7a` L559-592
**Triple fallback chain:**

**Attempt 1: OpenAI `o3` (preferred, reasoning model)**
- Method: `client.chat.completions.create` via `call_openai`
- `max_completion_tokens=8192` (not `max_tokens` — reasoning models require this field)
- Temperature omitted (reasoning models require temp=1.0 or omitted)
- `response_format={"type": "json_object"}`
- System: `persona_pass_7a_cross_model.md` (73 lines)
- User: `persona_pass_7a_cross_model_user.md` + assembled card

**Attempt 2: OpenAI `gpt-4o` (fallback)**
- `max_tokens=8192`, `temperature=0.0`, `response_format={"type": "json_object"}`

**Attempt 3: Gemini `gemini-2.5-pro` (final fallback)**
- `call_gemini(user=sysp + "\n\n" + userp, temperature=0.0, max_output_tokens=16384)`
- Parses JSON out of `r["text"]` manually (strips ```json fences)

**If all fail:** returns `{"validator": "skipped", "result": {"overall": "SKIPPED", ...}}` — non-blocking

#### 3.6.3 Revision loop — L632-743
If Pass 7a returns `overall: "REVISION_NEEDED"`, up to **2 loops** re-run flagged passes (2/3/4a/4b/5/6) with critique appended, invalidate downstream cache files, re-run Pass 7-pre + Pass 7a. Max 2 loops before flagging for human review.

#### 3.6.4 Pass 7b Worked Provocations — `_pass_7b` L749-761
- **Model:** `claude-opus-4-7`
- `max_tokens=24000`, `thinking=True` (adaptive), `temperature=1.0`
- System: `persona_pass_7b_smoke_test.md` (88 lines, Jinja-filled with `conference_context`, `voice_mode`)
- User: `persona_pass_7b_smoke_test_user.md` + full assembled card

#### 3.6.5 Pass 7c Negative Constraints — `_pass_7c` L772-801
**Primary: Gemini `gemini-2.5-pro`** (preferred — avoids self-preference bias)
- `call_gemini(user=sysp_gemini + "\n\n" + userp, temperature=0.0, max_output_tokens=16384)`
- System rendered with `claude_fallback=False`

**Fallback: Claude `claude-sonnet-4-6`**
- `max_tokens=8192`, `temperature=0.0`, `thinking=False`, `response_format_json=True`
- System rendered with `claude_fallback=True` (prepends bias-awareness instruction)

### 3.7 Phase 4 — Derive

#### 3.7.1 Derive — `_derive` L815-834
- **Model:** `claude-sonnet-4-6`
- `max_tokens=8192`, `temperature=0.1`, `thinking=False`
- `response_format_json=True`
- System: `persona_derive.md` (81 lines)
- User: `persona_derive_user.md` + full assembled card
- Output: `provocateur_profile` (8 fields) + `evaluation_rubric` (9 test prompts). Written to separate files at `runs/<slug>/provocateur_profile.json` and `runs/<slug>/evaluation_rubric.json`.

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

`_archive/` contains 4 superseded v1/v2-draft prompts (kept for historical reference): `provocateur_triage_v1_combined.md`, `provocateur_selection_v1_llm.md`, `provocateur_formulation_v1_per_theme.md`, `provocateur_formulation_v2_per_pair_draft.md`.

### 4.2 Personas prompts — `personas/flows/shared/prompts/`

32 files totaling ~2,450 lines. Jinja2 template syntax throughout (`{% if %}`, `{{ var }}`). Loaded via `render()` in `personas/flows/shared/prompt_render.py` (StrictUndefined — fails fast on missing variables).

| Phase | System prompt | User prompt |
|---|---|---|
| Pass 0a | `pass_0a_voice_config.md` | (inline in runner) |
| Pass 0b | `pass_0b_dr_prompt.md` | — (template, not LLM) |
| Pass 1a (Perplexity) | — | `persona_pass_1a_research_human.md` |
| Pass 1b (Gemini) | — | `persona_pass_1b_broad_scan.md` |
| Pass 1-merge | `persona_pass_1merge_contradiction_system.md` | `persona_pass_1merge_three_way_user.md` (or `_contradiction_user.md` for 2-way) |
| Pass 1c-extract | (inline) | `persona_pass_1c_extract_urls.md` + dossier |
| Pass 1d | (inline) | `persona_pass_1d_excerpt_selection.md` |
| Pass 2 | `persona_pass_2_identity_boundaries.md` | `persona_pass_2_user.md` |
| Pass 3 | `persona_pass_3_intellectual_core.md` | `persona_pass_3_user.md` |
| Pass 4a | `persona_pass_4a_voice.md` | `persona_pass_4a_user.md` |
| Pass 4b | `persona_pass_4b_artifact.md` | `persona_pass_4b_user.md` |
| Pass 5 | `persona_pass_5_engagement.md` | `persona_pass_5_user.md` |
| Pass 6 | `persona_pass_6_corpus.md` | `persona_pass_6_user.md` |
| Pass 7-pre | `persona_pass_7pre_citation.md` | `persona_pass_7pre_citation_user.md` |
| Pass 7a | `persona_pass_7a_cross_model.md` | `persona_pass_7a_cross_model_user.md` |
| Pass 7b | `persona_pass_7b_smoke_test.md` | `persona_pass_7b_smoke_test_user.md` |
| Pass 7c | `persona_pass_7c_negative.md` | `persona_pass_7c_negative_user.md` |
| Coherence Threading | (inline) | `persona_coherence_threading.md` |
| Derive | `persona_derive.md` | `persona_derive_user.md` |

---

## 5. Environment variables that affect LLM call behavior

### 5.1 Runtime

| Variable | Default | Effect |
|---|---|---|
| `ANTHROPIC_API_KEY` | — | Required. Read at task time from `os.environ`. |
| `ASSEMBLYAI_API_KEY` | — | Required. Set at runtime: `aai.settings.api_key = os.environ["ASSEMBLYAI_API_KEY"]`. |
| `CLAUDE_MODEL` | Sonnet in transcription, Opus elsewhere | Shared across flows. Transcription defaults to `claude-sonnet-4-6`; Researcher and Provocateur default to `claude-opus-4-7`. |
| `TRANSCRIPTION_CLAUDE_MODEL` | `CLAUDE_MODEL` | Per-flow override for transcription (cleaning + drift verification). Falls through to CLAUDE_MODEL if unset. |
| `RESEARCHER_CLAUDE_MODEL` | `CLAUDE_MODEL` | Per-flow override for researcher extraction/clustering/theming. |
| `PROVOCATEUR_CLAUDE_MODEL` | `CLAUDE_MODEL` | Per-flow override for provocateur triage/formulation. |
| `TRANSCRIPTION_SPEAKER_ID_MODEL` | `CLAUDE_MODEL` | Per-run override for Speaker ID only. Flip to `claude-opus-4-7` for hard sessions. |
| `TRANSCRIPTION_CACHE` | unset | Set to `"1"` in dev to enable Prefect AssemblyAI cache (30-day). **Keep off in prod.** |
| `RESEARCHER_THINKING` | `"1"` | Set to `"0"` to disable adaptive thinking across all 3 Researcher tasks. |
| `PROVOCATEUR_THINKING` | `"1"` | Set to `"0"` to disable adaptive thinking across all 3 Provocateur LLM tasks. |
| `PROVOCATEUR_FORMULATION_BATCH` | `4` | Parallel Formulation calls per batch. |
| `PROVOCATEUR_BATCH_WAIT_S` | `20` | Seconds between Formulation batches. |
| `INGEST_FLOW_CMD` | computed | Overridable for ingest tests (points at fake flow). Does not affect direct CLI runs of `transcription_flow.py`. |

### 5.2 Personas

| Variable | Default | Effect |
|---|---|---|
| `ANTHROPIC_API_KEY` | — | Required. |
| `PERPLEXITY_API_KEY` | — | Required for Pass 1a. |
| `GOOGLE_API_KEY` | — | Required for Pass 1b + Pass 7a fallback + Pass 7c primary. |
| `OPENAI_API_KEY` | — | Required for Pass 7a primary (o3 → gpt-4o). |
| `CLAUDE_MODEL` | `claude-opus-4-7` | Only read by `call_claude` when `model` arg is None — most persona passes hardcode the model, so this env var has limited effect in personas. |
| `PERPLEXITY_MODEL` | `sonar-deep-research` | Override via `call_perplexity`. |
| `GEMINI_MODEL` | `gemini-2.5-pro` | Override via `call_gemini`. |
| `OPENAI_MODEL` | `gpt-4o` | Override via `call_openai` — but Pass 7a hardcodes the fallback chain `o3` → `gpt-4o`, overriding this env. |
| `PERSONA_THINKING_BUDGET` | — | Documented in `.env.example` but not currently consumed by any code path. |
| `PERSONA_VOICE_BATCH` | — | Documented in `.env.example` but not currently consumed. |

---

## 6. Shared wrapper behavior

### 6.1 `call_claude` (`personas/flows/shared/clients.py` L20-113)

The personas pipeline's only Claude wrapper. Behavior controlled by three parameters:

- **`thinking: bool`** — `thinking=True` enables adaptive thinking (`{"type": "adaptive"}`); `thinking=False` (default) disables it. No budget argument needed — adaptive mode sets its own budget.
- **Streaming heuristic** — automatic. `use_streaming = max_tokens >= 16384 or thinking`. Threshold matches Anthropic SDK's non-streaming cutoff (SDK refuses non-streaming when `3600 * max_tokens / 128_000 > 600` sec, i.e. `max_tokens > 21333`). 16384 is conservative.
- **JSON extraction when `response_format_json=True`** — strips \`\`\`json fences and trailing content. On `json.JSONDecodeError`, if `stop_reason == "max_tokens"` raises `RuntimeError` blaming budget; otherwise re-raises with diagnostics.

**Streaming collection:** iterates `content_block_delta` events with `delta.type == "text_delta"`. Thinking tokens are not collected (filtered out by the iteration). `stream.get_final_message()` provides usage totals.

### 6.2 `call_perplexity` (clients.py L118-182)

REST POST to `https://api.perplexity.ai/chat/completions`. OpenAI-compatible request format. Splits the response on `<think>...</think>` — `text` is the deliverable, `think` is the chain-of-thought trace.

### 6.3 `call_gemini` (clients.py L187-232)

`google.genai.Client(...).models.generate_content(...)`. `thinking_budget=None` (default) lets the model's own default apply — required for gemini-2.5-pro, which only operates in thinking mode and rejects budget=0.

### 6.4 `call_openai` (clients.py L237-289)

`client.chat.completions.create(...)`. Auto-detects reasoning models (`o1`, `o3`, `o4` prefixes) and switches to `max_completion_tokens` + omits temperature.

---

## 7. Historical parameter discrepancies (all resolved)

### 7.1 Pass 0a "adaptive thinking" comment is misleading *(resolved 2026-04-18)*

K.0 refactor (`commit 4666fa1`) renamed the `call_claude` thinking parameter to `thinking: bool`. `run_pass0a_voice_config.py` L174 now correctly sets `thinking=True` with comment `# enables Anthropic adaptive thinking`. Parameter and comment are consistent.

### 7.2 Formulation `flavor` field — spec ↔ code mismatch *(resolved 2026-04-18)*

`docs/AI_Assembly_Provocateur_Pipeline.md` L334-347 documents `flavor` as the `lens` value (`assertion|reframing|open_question`). Actual prompt (`provocateur_formulation.md` L75-97) specifies stage-direction text (`"speaking with intensity"`, `"pushing back"`, `"with weight"`). Run artifacts match the prompt. Spec doc is wrong.

### 7.3 `briefing_narrative` points at `structured` but JSON key is `full_theme_record` *(resolved 2026-04-18)*

`_render_narrative_briefing` in `provocateur_flow.py` L832-868 emits a markdown footer that reads `[Full structured supporting material ... is available in the 'structured' field of this briefing entry for deeper inspection.]` — but the actual JSON key is `full_theme_record`. Voice Pipeline consumers reading the markdown hint will look for the wrong field.

### 7.4 Anthropic SDK version docs ≠ reality *(resolved 2026-04-18)*

CLAUDE.md claims runtime=`0.95.0`, personas=`0.94.1`. CURRENT_STATE.md claims the flipped version. Both `runtime/requirements.txt` and the personas venv are pinned to `0.94.1`. Separate venvs are real but their version-mismatch justification is fictional.

### 7.5 DR validation floor vs prompt ask *(resolved 2026-04-18)*

`pass_0b_dr_prompt.md` L1086 asks for "Minimum 15,000 words". `personas/flows/shared/dr_validation.py` L20 floor is 5,000. Error message at L53 says "expected 15,000-25,000". A 5,001-word dossier passes `VALID`.

### 7.6 Personas pipeline_version drift *(resolved 2026-04-18)*

Previously four sources disagreed (doc header v3.10, example JSON v3.7, runner v3.9, Plato artifact v3.7). Fixed:
- `docs/AI_Assembly_Persona_Pipeline_v3_9.md` renamed to `AI_Assembly_Persona_Pipeline_v3_10.md`
- Example JSON at L781 updated to `"pipeline_version": "3.10"`
- `run_persona_pipeline.py` L963 updated to `"3.10"`
- Plato artifact left as-is (historical record of what actually ran)

### 7.7 Transcription intentionally omits thinking even on Opus

Speaker ID (§2.1.2) and Cleaning (§2.1.3) are exempted from the
"thinking ON for every Opus 4.7 call" rule per
`docs/AI_Assembly_Transcription_Pipeline.md` "Model selection" section:
Speaker ID's output is too small (<2K tokens) for thinking's latency
cost to be worth it; Cleaning's work is per-turn-local, not
cross-turn synthesis. If someone sets `TRANSCRIPTION_SPEAKER_ID_MODEL`
or `CLAUDE_MODEL` to Opus, thinking stays off intentionally.

---

## 8. What is NOT an LLM call

For completeness:

- **Selection** (Provocateur Stage 2) — pure Python, deterministic 9-step algorithm
- **Packaging** (Provocateur Stage 4) — pure Python, assembles two-view briefings
- **Merge-clusters-and-themes** (Researcher) — pure Python, post-theming step
- **FFmpeg normalize + ffprobe validate** (Ingest) — subprocess, not LLM
- **Pass 0b DR Prompt render** — Jinja2 only
- **Pass 1c fetch** — HTTP + SSRF guards
- **Wikipedia search + summary** — REST
- **Coherence Threading IS an LLM call** — counted in §1 despite its wrapper shape (it's a Sonnet 4.6 call, 2048 tokens, temp 0)

---

*Verify against the code before making cost or routing decisions. All line numbers reference the repo state as of 2026-04-18.*
