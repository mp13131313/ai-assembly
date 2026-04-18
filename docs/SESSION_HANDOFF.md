# Session handoff — AI Assembly

**Written:** 2026-04-18 by a Claude Opus 4.7 session that had spent several turns doing a full line-by-line review of the repo.
**Refreshed:** 2026-04-18 after Sonnet executed the fix plan (commits 2df11df, 18ed209) and after the audience-brief integration landed (commit 9010ab3). §3 findings marked FIXED, §5 forward plan trimmed, §7 subprompts reduced to what's still open.
**Audience:** a fresh Claude session tasked with continuing this work.
**Goal:** rebuild ~90% of the prior session's working knowledge in ~30–60 minutes instead of the 3+ hours it took the first time.

Read this top-to-bottom before touching code.

---

## 0. One-minute orientation

**Project:** *The AI Assembly.* A provotype for the World Beautiful Business Forum (WBBF) in Athens, May 7–10, 2026. Twelve non-human voices (a river, an octopus, Plato, Hannah Arendt, and eight others) read the day's conference transcripts overnight and produce written responses — provocations, queries, reflections — that re-enter the human conversation the following morning via Substack read-throughs.

**Two sub-trees in one monorepo:**
- `runtime/` — overnight Prefect flows (transcription, researcher, provocateur, eventually voice) + FastAPI ingest app. Runs at Athens.
- `personas/` — pre-conference pipeline that builds the 37-field Persona Cards + 8-field Provocateur Profiles. Runs on a local machine weeks before the event.

**Current state in one sentence:** transcription/researcher/provocateur pipelines built and validated; voice pipeline not built; persona pipeline built and working, ~5 of 12 voice cards produced; council_config.json is still stubs; Athens is in ~3 weeks.

**Orchestration:** Prefect (not n8n — earlier docs say n8n; those are stale). Single monorepo `.env` at root, loaded via `REPO_ROOT.parent / ".env"` pattern in every script. Two venvs (`runtime/venv`, `personas/venv`), both on `anthropic==0.94.1` despite what `CLAUDE.md` and `docs/CURRENT_STATE.md` each claim.

---

## 1. The reading plan (staged — don't read everything)

At 0% context, reading every file in this repo would consume 40–60% of your window. Stage the reads. Stop at the stage where you have enough to do the specific task in front of you.

### Stage 1 — Orient in 30 minutes (~5,500 lines)

1. **`CLAUDE.md`** (40 lines) — repo layout, venv pattern, env pattern. ⚠ claims different Anthropic versions — ignore that claim; both are 0.94.1.
2. **`README.md`** (50 lines) — quick structural intro.
3. **`docs/README.md`** (25 lines) — **critical** staleness index. Tells you which specs to trust.
4. **`docs/CURRENT_STATE.md`** (690 lines) — authoritative status snapshot. What's built, what's specified-but-not-built, what's not-yet-specified, known gaps. Read in full. ⚠ line 520 lies about Anthropic versions.
5. **`docs/AI_Assembly_Briefing_v3_1.md`** (350 lines) — project source of truth. Why, what, success criteria, four-day arc.
6. **`docs/SESSION_HANDOFF.md`** (this file) — re-read this with the above as context; gotchas will resonate more.
7. **`docs/LLM_CALL_INVENTORY.md`** (this session's artifact) — complete enumeration of every LLM call made from the repo. Skim first; reference later when you need a specific parameter.

After Stage 1 you know what the project is, where it is, and how it's structured. You can't write code yet.

### Stage 2 — Pipeline specs (60 minutes, ~4,500 lines)

Read in this order (later specs assume earlier context):

8. **`docs/AI_Assembly_Transcription_Pipeline.md`** (722 lines, v2.1)
9. **`docs/AI_Assembly_Researcher_Pipeline.md`** (640 lines, v3)
10. **`docs/AI_Assembly_Provocateur_Pipeline.md`** (527 lines, v2 — spec v2, architecture v3 internally; see delta doc)
11. **`docs/AI_Assembly_Voice_Pipeline.md`** (666 lines, v1 — covers Steps 1+2; Step 3 unspecified)
12. **`docs/AI_Assembly_Persona_Card_v2.md`** (870 lines) — the 37-field schema
13. **`docs/AI_Assembly_Persona_Pipeline_v3_9.md`** (2141 lines — the big one) — pre-conference persona build

Skip at this stage: `AI_Assembly_Architecture_v1.md` and `AI_Assembly_Infrastructure_Setup.md` are both marked **STALE** in docs/README.md — they describe n8n + rclone + Google Drive; actual pipeline is Prefect + FastAPI upload. Read only if doing archaeology.

### Stage 3 — Code by area

Read only the area relevant to your task. Each area has shared + entry points.

**Runtime flows:**
- `runtime/flows/transcription_flow.py` (619 lines) — Stage 0
- `runtime/flows/researcher_flow.py` (805 lines) — Stage 1
- `runtime/flows/provocateur_flow.py` (1365 lines — largest module) — Stage 1b
- `runtime/flows/shared/io.py` (277 lines) — `load_session_package`, `write_json_atomic`, `load_council_config`, `load_prompt`, `extract_json`, `member_slug`, `get_logger`, `get_member_by_name`. Read this first — most things import from here.
- `runtime/flows/shared/council/council_config.json` (159 lines) — 12-member stub profiles + `selection_parameters`. ⚠ version is `dev_stub_v2_with_selection_params`; real profiles not yet wired in.
- `runtime/flows/shared/council/README.md` (hot-swap semantics)

**Runtime ingest (FastAPI + systemd/Caddy):**
- `runtime/ingest/app.py` (409 lines) — routes, lifespan, upload
- `runtime/ingest/pipeline.py` (466 lines) — normalize + spawn + status machine
- `runtime/ingest/sessions.py` (228 lines) — `sessions.json` + `speakers.json` join
- `runtime/ingest/auth.py` (87 lines) — HTTP Basic + IP rate limit
- `runtime/ingest/config.py` (113 lines) — paths + env + knobs
- `runtime/ingest/deploy/{Caddyfile, ingest.service, README.md}` — production deploy
- `runtime/ingest/templates/*.html` (4 files) + `runtime/ingest/static/{app.js, style.css}`
- `runtime/ingest/tests/{test_app.py, test_pipeline.py, test_sessions.py, fake_transcription_flow.py}`

**Personas (entry points, then shared, then prompts):**
- `personas/run_pass0a_voice_config.py` (264 lines) — intake
- `personas/run_phase0_1_research.py` (192 lines) — Perplexity + Gemini in parallel, renders DR prompt
- `personas/run_pass0b_dr_prompt.py` (116 lines) — DR prompt renderer (no API)
- `personas/run_persona_pipeline.py` (1052 lines — largest module) — main pipeline from Pass 1-merge through Derive. ⚠ executes at module scope; uses `globals()[...]=result` in the revision loop. Works but un-importable for testing.
- `personas/flows/shared/clients.py` (290 lines) — `call_claude`, `call_perplexity`, `call_gemini`, `call_openai`. Read this to understand the streaming/thinking heuristics.
- `personas/flows/shared/io.py` (96 lines) — atomic writes, prompt loader, voice input loader
- `personas/flows/shared/node0_validation.py` (143 lines) — Pass 0 enum gates
- `personas/flows/shared/node1c_fetch.py` (87 lines) — SSRF-hardened primary text fetch
- `personas/flows/shared/node1d_excerpt_selection.py` (52 lines)
- `personas/flows/shared/prompt_render.py` (34 lines) — Jinja2, `StrictUndefined`
- `personas/flows/shared/dr_validation.py` (63 lines) — DR dossier 6-section + word-count check
- `personas/flows/shared/perplexity_split.py` (47 lines) — splits Perplexity output into 6 sections
- `personas/flows/shared/wikipedia.py` (61 lines) — REST search+summary for Pass 0a grounding
- `personas/scripts/validate_dr_dossier.py` (26 lines) — standalone validator

**Runtime prompts (8 files, 687 lines total, in `runtime/flows/shared/prompts/`):**
- `transcription_speaker_id.md` (81), `transcription_cleaning.md` (35)
- `researcher_extraction.md` (39), `researcher_clustering.md` (109), `researcher_theming.md` (90)
- `provocateur_triage_voice.md` (73), `provocateur_triage_flags.md` (66), `provocateur_formulation.md` (194)
- `_archive/` contains 4 superseded v1/v2-draft prompts (historical only)

**Persona prompts (32 files, 2450 lines total, in `personas/flows/shared/prompts/`):**
Full list in `docs/LLM_CALL_INVENTORY.md` §4.2. The big one is `pass_0b_dr_prompt.md` (1086 lines — Jinja template for the Claude DR prompt). All prompts internally claim `v3.7 Node N` in header comments even though spec is v3.10.

### Stage 4 — Optional deep dives

Read only if a specific task requires it:

- **`docs/AUDIENCE_BRIEF.md`** (this session's artifact) — three-part audience brief for Athens 2026 (HoBB org → Forum program → 7-faction audience profile). Required reading if you're touching `council_config.json`'s audience paragraph or anything audience-modeling.
- **`personas/notes/baseline_research/`** — 4 Deep Research artifacts that grounded the architecture. Read when you're wondering "why is the pipeline like this?". See `baseline_research/README.md` for the index.
- **`runtime/notes/updated_specs/`** — 3 delta docs (Transcription v2→v2.1, Researcher v2→v3, Provocateur v1→v2). Redundant with the main specs; read only for archaeological purposes.
- **`personas/notes/`** — operational plans (`SONNET_EXECUTION_PLAN*.md`, `WALKTHROUGH_FIXES_PENDING.md`, `IMPLEMENTATION_AUDIT_v3_7.md`, `ARCHITECTURE_NEXT_PHASE_HANDOFF.md`, `FIX_34_SECTION_BULLETS_DRAFT.md`). Mostly historical; `ARCHITECTURE_NEXT_PHASE_HANDOFF.md` is the only forward-looking one — it sketches a planned Phase B rewrite (chunked Pass 1 merge, structured JSON) that is **not yet built**.
- **`personas/HANDOFF.md`** — cross-repo handoff contract. Important if you're building the Voice Pipeline (not built yet).

---

## 2. Artifacts this session produced

All committed and pushed to `origin/main`.

- **`docs/LLM_CALL_INVENTORY.md`** (~280 lines) — every LLM call site, provider, model, parameters, thinking state, retry policy, prompt source, env-var overrides. **The canonical parameter reference.** Commit `2ee2dd7`.

- **`docs/AUDIENCE_BRIEF.md`** (~256 lines) — canonical three-part audience brief (HoBB organisation, Forum program, 7-faction audience profile). Source for the `council_config.json` audience paragraph. Commit `e01bac3`.

- **`personas/notes/baseline_research/compass_artifact_wf-109ac10a-*.md`** (~127 lines) — the Deep Research grounding underneath `AUDIENCE_BRIEF.md`. Same location/pattern as the three prior Deep Research artifacts. Commit `e01bac3`.

- **`personas/notes/baseline_research/README.md`** (updated) — indexes all four research artifacts (3 persona-pipeline + 1 audience). Commit `e01bac3`.

- **`personas/notes/SONNET_EXECUTION_PLAN_repo_audit.md`** (~1765 lines) — the fix plan Sonnet executed, migrated from the user's Desktop into the repo in commit `18ed209`. Dual role: (a) historical record of what landed 2026-04-18 across 8 commits, (b) template for future "AI writes plan → Claude executes" workflows — preamble at the top documents the structural features worth reusing.

- **`docs/SESSION_HANDOFF.md`** (this file) — reading plan + accumulated findings digest for future Claude sessions. Originally commit `a9842ee`; refreshed 2026-04-18 with post-fix-plan state (§3 findings marked FIXED with commit refs, §5 forward plan trimmed, §7 subprompts reduced to what's still open).

### Previously in this list, now removed

- **`docs/FIX_PLAN_ADDITIONS.md`** — net-new findings from this session that were folded into Sonnet's fix plan. Removed in commit `90cd71a` after all its findings landed (items §1, §3.1, §3.3, §3.4, §2, §4.13 landed in code; K.0 preserved in the migrated fix plan). Content recoverable via `git show 2ee2dd7:docs/FIX_PLAN_ADDITIONS.md` if ever needed.

---

## 3. Accumulated findings (what you can't learn just from reading files)

This is the dense knowledge that took the prior session hours to build up. A fresh read won't produce all of it.

### 3.1 Spec ↔ code mismatches — all resolved 2026-04-18

All mismatches the prior session flagged landed in Sonnet's fix plan execution. Kept here as historical diagnostic — a fresh session needs none of these fixed. If a grep below returns a different result than stated, flag it rather than silently re-fixing.

- ~~**`pipeline_version` drifts across 4 sources.**~~ → **FIXED** (commit `7550965`). Spec file renamed to `AI_Assembly_Persona_Pipeline_v3_10.md`; `run_persona_pipeline.py` writes `"3.10"`; historical card files on disk still show `"3.7"` (don't touch).
- ~~**`flavor` field in Formulation output.**~~ → **FIXED** (commit `ac25bd7`). Spec doc updated to match prompt; prompt is the authoritative definition.
- ~~**Briefing markdown footer references wrong JSON key (`structured` vs `full_theme_record`).**~~ → **FIXED** (commit `ac25bd7`).
- ~~**DR word-count floor mismatch (5k vs 15k).**~~ → **FIXED** (commit `ac25bd7`). Floor raised to 15,000.
- ~~**Anthropic SDK version fiction.**~~ → **FIXED** (commit `7550965`). Both docs now truthfully state both venvs are on `0.94.1`. See `CLAUDE.md` §"Separate venvs".
- ~~**Stale pointer `runtime/flows/voice/README.md`.**~~ → **FIXED** (commit `ac25bd7`). Pointers redirected to `personas/HANDOFF.md` + the Pass 7b prompt header.
- ~~**Persona prompt internal version tags (v3.7 → v3.10).**~~ → **FIXED** (commit `883a0a1`). All 32 prompts now carry v3.10 in their header comments.

### 3.2 Bugs that existed before 2026-04-18 — all fixed

All four bugs the prior session found landed in commit `2df11df`. Kept here so a fresh session doesn't mistake these for open issues.

- ~~**Critical:** `runtime/flows/provocateur_flow.py` — `_REPO_ROOT` used before assignment; `out_path` undefined in `package_voice_briefings`.~~ → **FIXED**. Module imports cleanly.
- ~~**Silent quality:** Pass 0a runs Opus 4.7 with thinking OFF despite the code comment.~~ → **FIXED**. Now uses `thinking=True` (see K.0 refactor below).
- ~~**Silent quality:** Pass 1-merge runs Opus 4.7 with thinking OFF.~~ → **FIXED**. Now `thinking=True`, `temperature=1.0`.

Plus one follow-up that eliminates the bug class:

- ~~**K.0 root cause:** `call_claude`'s `thinking_budget: int | None = None` parameter was misleadingly named — adaptive mode ignores the budget; only truthy/falsy matters.~~ → **REFACTORED** (commit `4666fa1`). Parameter renamed to `thinking: bool = False`. All 9 call sites in personas/ updated. `call_gemini`'s unrelated `thinking_budget` parameter (Gemini SDK native) preserved.

**Verification (should all return the post-fix state):**
```bash
# All should be 0 or as noted
grep -rn "thinking_budget" personas/ --include="*.py" | grep -v "call_gemini\|google-genai"  # 0 hits outside call_gemini
grep -c "out_path" runtime/flows/provocateur_flow.py  # 0
python3 -c "import sys; sys.path.insert(0, 'runtime'); import flows.provocateur_flow"  # should succeed
```

### 3.3 Design decisions that aren't obvious from specs

- **Two separate venvs** exist because runtime and personas *could* pin different Anthropic SDK versions, not because they currently do. Docs overstate this. If you ever need to pin them differently (e.g. test a new SDK against one pipeline first), the split is already set up.
- **Checkpoints-as-cache.** The Provocateur and Personas pipelines use per-call JSON files as the cache. No `CACHE=1` env var. Delete the specific checkpoint to force re-run. Listed in `council/README.md` and the Provocateur spec §"Runtime" section.
- **Researcher Round 1 sees minimal input** (`{ref, extraction, context}` only) because Opus was using the namespace prefix in real IDs as a grouping shortcut. v2.3→v2.4 fix. Temp `ref`s are translated back to real IDs after the call.
- **Deterministic shuffle seed 42** in Researcher Round 1 + Round 2 breaks session-ordered reading-order bias.
- **Provocateur Selection is pure Python** (not LLM) because the task is combinatorial scoring, not editorial judgment. An earlier LLM-based Selection was slow + non-reproducible + opaque. Python is instant, deterministic, every knob tunable in `council_config.json#selection_parameters`.
- **`worked_provocations` is NOT a runtime few-shot exemplar.** It's a build-time smoke test. Loading it into Voice Pipeline's Step 1 prompt would collapse the voice's range. Documented in `personas/HANDOFF.md`, the `persona_pass_7b_provocations.md` header, and `provocateur_flow.py` L901-906.
- **Adaptive thinking requires `temperature=1.0`** per Anthropic SDK constraint. This is why Pass 1-merge's thinking-off state is entangled with its `temperature=0.0` — turning thinking on forces temp to 1.0, which may destabilize the JSON output.
- **Speaker ID + Cleaning explicitly don't use thinking on Opus** per Transcription spec's "Model selection" section, even when `CLAUDE_MODEL` or `TRANSCRIPTION_SPEAKER_ID_MODEL` is set to Opus 4.7. Speaker ID output is too small (<2K tokens); Cleaning's work is per-turn-local not cross-turn synthesis. Intentional carve-out from the "thinking everywhere Opus 4.7" directive. Sonnet's plan item 4.11 makes this explicit in code comments.

### 3.4 Audience model — sharper than the Briefing and council_config currently carry

From `docs/AUDIENCE_BRIEF.md`:

- **Seven identifiable factions** in the Athens audience, engineered to collide:
  1. Cognitive Sovereignty Hawks (Véliz, Giussani, Kasket, Edwards, Jackson)
  2. Sovereign AI Builders (White, Bhattacharya, Giacomelli, Sethumadhavan, Lappas)
  3. Posthumanist Reframers (Akomolafe, Bridle, Johar, Hamzaçebi)
  4. Anti-Capitalist / Collapse-Aware Economists (Mattei, Kemp, Linn, Kouloumpi, Gelles)
  5. Democratic Institutionalists (Chwalisz, Alexander, Mulgan, Witter, Berkowitz, Papandreou)
  6. Re-Enchantment / Spiritual (Burton, Matsumoto, Quarch, Trott, Everett)
  7. Security / Geopolitics Realists (Braw, Dolev, Kiyaei, Katsos)
- **The actual center of gravity is agency** (who acts, who decides, what happens when machines share or seize those functions) — even though marketing foregrounds beauty/care/belonging.
- **Ten hardest-to-please voices:** Mattei, Véliz, Kasket, Akomolafe, Giussani, Kemp, Bridle, Arora, Pahina, Berkowitz. These are the audience's sharpest internal critics; formulations that wouldn't survive their critique probably won't land.
- **Deepest audience vulnerability:** *"their well-curated openness is itself the failure mode — they are too good at performing reception to know when they are not actually being changed."* Sharper than the current council_config.json audience paragraph's "comfortable paradox" framing.
- **Four engineered curator tensions already live in the room:** Véliz×White on Act Two, Kasket×Bhattacharya in Agentic Agora, Braw alongside Dolev+Kiyaei, Mattei in Ministry of Regeneration on the Athens Stock Exchange floor.

These findings are **not yet integrated** into `council_config.json` or Briefing v3.1. There's a planned edit in §5 below.

### 3.5 Gaps in the current pipeline

- **Voice Pipeline Steps 1 + 2: not built** (spec exists). Blocks everything downstream of Provocateur. Highest-value unfinished work.
- **Voice Pipeline Step 3 (Amendment): not spec'd** (mentioned in Briefing v3.1 but no prompt/schema).
- **Microsite: not built.** Astro/Next.js static site planned; required before Night 1.
- **Substack read-through curation: not built.** Claude Opus call generating HoBB-voiced newsletter.
- **Closing show pipelines: not built** (theme identification, per-theme mapping, video pipeline).
- **Admin console: not built** (would let operators kick off stages, view logs, sync council_config from persona runs).
- **Night 2/3 plumbing: not plumbed** (Provocateur's `(theme_id, member)` exclusion filter; Voice Pipeline's continuity block generation).
- **Council config members are stubs.** `dev_stub_v2_with_selection_params` — 12 hand-written member profiles, not derived from completed Persona Cards. Pre-Athens blocker.
- **Speaker bios empty.** `runtime/reference/speakers.json` has 202 speakers, all `bio: ""`. Speaker ID Pass 3 accuracy drops from 70–85% to 40–50% without them. Pre-Athens blocker.
- **7 of 12 persona cards missing.** Built: Plato, Cleopatra, Hannah Arendt, Octopus, Ibn Battuta (partial). Missing: Scheherazade, Ada Lovelace, Dostoevsky, Bob Marley, Audrey Tang, Peter Thiel, Whanganui River.

### 3.6 What's in the research but NOT in the current pipeline

From `personas/notes/baseline_research/` — deliberate omissions, flagged as potential future work:
- **GraphRAG with Neo4j + Weaviate.** Baseline research calls it "the single most impactful architectural choice." Current pipeline uses plain RAG.
- **Persona vectors / LoRA activation steering** (Anthropic's Persona Vector Distillation). Current pipeline is prompt-engineering only — deliberate per the prosumer framing in Briefing v3.1.
- **Benchmark-based automated eval** (CharacterBench / TimeChara / RoleKE-Bench). Current Pass 7a is freeform cross-model critique.
- **Phase B chunked Pass 1 merge architecture** (described in `personas/notes/ARCHITECTURE_NEXT_PHASE_HANDOFF.md`). A planned rewrite from 6-section markdown dossier to chunked structured JSON. Not yet started.

---

## 4. Repo file tree — annotated inventory

This is the full list of every file a Claude session might read. Anything not in here is either a run artifact (skip), a venv internal (skip), or unimportant.

```
ai-assembly/
├── CLAUDE.md                         ⚠ version claim wrong; read for structure
├── README.md                         top-level orientation
├── .env.example                      shared secrets template
├── .gitignore
│
├── docs/                             ★ canonical spec tree
│   ├── README.md                     ★ staleness index — read first
│   ├── CURRENT_STATE.md              ★ authoritative status snapshot
│   ├── AI_Assembly_Briefing_v3_1.md  ★ project briefing
│   ├── AI_Assembly_Transcription_Pipeline.md    v2.1
│   ├── AI_Assembly_Researcher_Pipeline.md       v3
│   ├── AI_Assembly_Provocateur_Pipeline.md      v2
│   ├── AI_Assembly_Voice_Pipeline.md            v1, Steps 1+2 only
│   ├── AI_Assembly_Persona_Card_v2.md           37-field schema
│   ├── AI_Assembly_Persona_Pipeline_v3_10.md    v3.10
│   ├── AI_Assembly_Architecture_v1.md           STALE — n8n era
│   ├── AI_Assembly_Infrastructure_Setup.md      STALE — rclone/Drive era
│   ├── AUDIENCE_BRIEF.md             ★ Athens audience brief (source for council_config audience)
│   ├── LLM_CALL_INVENTORY.md         ★ every LLM call parameterized
│   ├── SESSION_HANDOFF.md            ★ this file
│   └── design/
│       ├── AI_Assembly_DesignPrinciples.md  visual + aesthetic principles
│       └── Nine_Modes_of_Implication.md     media-engagement taxonomy
│
├── runtime/                          overnight pipeline
│   ├── README.md                     rewritten 2026-04-18 as pointer to top-level README
│   ├── requirements.txt
│   ├── .env.example
│   ├── .gitignore
│   │
│   ├── ingest/                       FastAPI upload app
│   │   ├── __init__.py
│   │   ├── app.py                    routes, lifespan, upload
│   │   ├── config.py                 paths, env, knobs
│   │   ├── auth.py                   HTTP Basic + IP rate limit
│   │   ├── pipeline.py               normalize + spawn + status machine
│   │   ├── sessions.py               sessions.json/speakers.json join
│   │   ├── templates/
│   │   │   ├── base.html
│   │   │   ├── index.html
│   │   │   ├── session_detail.html
│   │   │   ├── status.html
│   │   │   └── overview.html
│   │   ├── static/
│   │   │   ├── app.js                cache-bust now via STATIC_VERSION (commit 1c30285)
│   │   │   └── style.css
│   │   ├── deploy/
│   │   │   ├── Caddyfile             ⚠ ingest.example.com placeholder (warned in comment)
│   │   │   ├── ingest.service        systemd, KillMode=process
│   │   │   └── README.md             venv path corrected (commit 963f1b9)
│   │   └── tests/
│   │       ├── __init__.py
│   │       ├── test_app.py
│   │       ├── test_pipeline.py
│   │       ├── test_sessions.py
│   │       └── fake_transcription_flow.py
│   │
│   ├── flows/                        Prefect flows
│   │   ├── __init__.py
│   │   ├── transcription_flow.py     Stage 0
│   │   ├── researcher_flow.py        Stage 1
│   │   ├── provocateur_flow.py       Stage 1b — bugs fixed commit 2df11df
│   │   └── shared/
│   │       ├── __init__.py
│   │       ├── io.py                 ★ read first
│   │       ├── council/
│   │       │   ├── council_config.json   ⚠ still stubs for members[]; audience now sharpened (v3_audience_sharpened, commit 9010ab3)
│   │       │   └── README.md             hot-swap semantics
│   │       └── prompts/              8 active + 4 archived
│   │           ├── transcription_speaker_id.md
│   │           ├── transcription_cleaning.md
│   │           ├── researcher_extraction.md
│   │           ├── researcher_clustering.md
│   │           ├── researcher_theming.md
│   │           ├── provocateur_triage_voice.md
│   │           ├── provocateur_triage_flags.md
│   │           ├── provocateur_formulation.md
│   │           └── _archive/         4 historical prompts
│   │
│   ├── reference/                    frozen inputs
│   │   ├── sessions.json             ⚠ 202 speakers with empty bios
│   │   ├── speakers.json             ⚠ all bios empty — pre-Athens blocker
│   │   ├── sessions.skipped.json     2 TBC-venue sessions
│   │   └── session_template.json
│   │
│   ├── scripts/
│   │   ├── generate_sessions_json.py
│   │   └── generate_speakers_json.py
│   │
│   ├── notes/
│   │   ├── PROPOSED_pipeline_doc_change.md       historical
│   │   └── updated_specs/
│   │       ├── TRANSCRIPTION_v2_to_v2_1_delta.md  historical — Opus 4.6 era (banner added ac25bd7)
│   │       ├── RESEARCHER_v2_to_v3_delta.md       historical (banner added ac25bd7)
│   │       └── PROVOCATEUR_v1_to_v2_delta.md      historical (banner added ac25bd7)
│   │
│   ├── runs/                         run artifacts — DO NOT EDIT
│   │   └── dev_msc_test/             MSC 2026 test validation
│   │
│   └── .claude/
│       └── launch.json
│
├── personas/                         pre-conference persona pipeline
│   ├── README.md
│   ├── HANDOFF.md                    ★ cross-repo handoff contract (worked_provocations rule)
│   ├── .env.example
│   │
│   ├── run_pass0a_voice_config.py    thinking=True (fixed 2df11df; refactored param name 4666fa1)
│   ├── run_phase0_1_research.py      Pass 1a + 1b + DR render
│   ├── run_pass0b_dr_prompt.py       DR prompt re-render (no API)
│   ├── run_persona_pipeline.py       ★ main pipeline (1052 lines); _pass_1merge now thinking=True
│   │
│   ├── flows/
│   │   ├── __init__.py
│   │   └── shared/
│   │       ├── __init__.py
│   │       ├── clients.py            ★ call_claude(thinking: bool) + wrappers — read first
│   │       ├── io.py
│   │       ├── node0_validation.py
│   │       ├── node1c_fetch.py       SSRF-hardened (TOCTOU documented, commit 963f1b9)
│   │       ├── node1d_excerpt_selection.py
│   │       ├── prompt_render.py      Jinja2, StrictUndefined
│   │       ├── dr_validation.py      word-count floor raised to 15k (commit ac25bd7)
│   │       ├── perplexity_split.py
│   │       ├── wikipedia.py
│   │       └── prompts/              32 files, all v3.10 headers (commit 883a0a1) — see LLM_CALL_INVENTORY §4.2
│   │
│   ├── scripts/
│   │   ├── __init__.py
│   │   └── validate_dr_dossier.py
│   │
│   ├── inputs/
│   │   ├── conference_context.json   project metadata
│   │   ├── voices/                   5/12 voice configs present
│   │   │   ├── plato.json
│   │   │   ├── cleopatra.json
│   │   │   ├── hannah_arendt.json
│   │   │   ├── octopus.json
│   │   │   ├── ibn_battuta.json
│   │   │   ├── ibn_battuta_pass0a_review.md
│   │   │   └── _archive/
│   │   └── dossiers/
│   │       ├── CLAUDE_DR_BRIEFING.md           manual paste-into-claude.ai instructions
│   │       ├── README.md
│   │       ├── _dr_prompts/                    generated DR prompts (paste-ready)
│   │       └── _archive/
│   │
│   ├── notes/
│   │   ├── ARCHITECTURE_NEXT_PHASE_HANDOFF.md            ★ planned Phase B rewrite — not built
│   │   ├── IMPLEMENTATION_AUDIT_v3_7.md                  historical
│   │   ├── WALKTHROUGH_FIXES_PENDING.md                  historical (banner added ac25bd7)
│   │   ├── SONNET_EXECUTION_PLAN*.md                     4 older execution plans
│   │   ├── SONNET_EXECUTION_PLAN_repo_audit.md           ★ 2026-04-18 fix plan + template for future AI-writes-plan workflows (commit 18ed209)
│   │   ├── FIX_34_SECTION_BULLETS_DRAFT.md               historical
│   │   └── baseline_research/
│   │       ├── README.md                                  ★ indexes 4 research artifacts
│   │       └── compass_artifact_wf-*.md                   4 Deep Research artifacts
│   │
│   ├── runs/                         per-voice build outputs — DO NOT EDIT
│   │   ├── plato/                    full pipeline completed
│   │   ├── hannah_arendt/             partial
│   │   └── ibn_battuta/                partial
│   │
│   └── .claude/ (not in tree; gitignored)
│
└── .claude/
    └── settings.local.json           scoped permissions (Phase A allowlist)
```

Symbols:
- ★ = read first / critical reference
- ⚠ = known issue or outdated content at time of writing

---

## 5. Forward plan — tasks queued up

### Done 2026-04-18 — no action needed by fresh session

- Fix plan (Categories 1–5 + K.0) executed across commits `2df11df`–`5b6005f` + `883a0a1` + `4666fa1`. See `personas/notes/SONNET_EXECUTION_PLAN_repo_audit.md` for the full list with commit attribution.
- `FIX_PLAN_ADDITIONS.md` findings all landed; doc removed in `90cd71a`.
- Audience brief integrated into `council_config.json` (v3_audience_sharpened) and Briefing v3.1 pointer added, commit `9010ab3`.

### Medium-term: Voice Pipeline Steps 1+2 build

Largest remaining build item. Spec exists: `docs/AI_Assembly_Voice_Pipeline.md`. Requires:
- New Prefect flow `runtime/flows/voice_flow.py`
- System prompts per step (foundational + reasoning+engagement for Step 1; foundational + voice+artifact for Step 2)
- Per-voice parallel execution, per-formulation parallel within a voice
- Optional validation (anachronism check + constitutional check)
- Schema: `detailed_responses[]` + artifact per voice per night
- Cross-repo read: loads `persona_card_assembled.json` from `personas/runs/<slug>/` — must drop `metadata` and `worked_provocations` before using as prompt per `personas/HANDOFF.md`

### Medium-term: Voice Pipeline Step 3 spec

Briefing v3.1 describes the Amendment step but doesn't spec it. Needs: system prompt template, input format, output format, integration with theme-graph, timing.

### Longer-term: Closing-show pipelines (3 passes) + microsite + admin console + downstream (render/publish/curate/deliver)

All specified but unbuilt. See `docs/CURRENT_STATE.md` §3 for scope.

### Not on the plan: Phase B chunked Pass 1 merge rewrite

Described in `personas/notes/ARCHITECTURE_NEXT_PHASE_HANDOFF.md`. A planned rewrite of the persona pipeline's Phase 1 from 6-section markdown to chunked structured JSON per section. Deliberately deferred — current pipeline works.

---

## 6. What NOT to touch

Anything in these locations is a historical record or deliberate artifact. Edits would rewrite history or break provenance.

- **`runtime/runs/**/*`** — run artifacts. Records of what transcription/researcher/provocateur actually produced. Edit only if you want to lose traceability.
- **`personas/runs/**/*`** — per-voice build outputs. Plato's full card + partial Arendt/Ibn Battuta. Same rule.
- **`personas/notes/baseline_research/compass_artifact_*.md`** — commissioned Deep Research that predated the pipeline. Historical reference.
- **`runtime/flows/shared/prompts/_archive/`** — 4 superseded prompts (v1 Triage combined, v1 Selection LLM, v1 per-theme Formulation, v2-draft per-pair Formulation). Preserved for architectural history.
- **`personas/inputs/voices/_archive/`** + **`personas/inputs/dossiers/_archive/`** — historical voice configs + an archived Plato dossier that was written in the wrong shape (persona card instead of DR dossier).
- **`runtime/notes/updated_specs/*_delta.md`** — 3 delta docs describing pipeline transitions that happened on Opus 4.6. Historical; the main specs are current.
- **`personas/notes/SONNET_EXECUTION_PLAN*.md`, `WALKTHROUGH_FIXES_PENDING.md`, `IMPLEMENTATION_AUDIT_v3_7.md`, `FIX_34_SECTION_BULLETS_DRAFT.md`** — operational plans, mostly executed. Leave.

If you find yourself wanting to edit one of these, stop and flag it first.

---

## 7. Suggested first-message prompt for a fresh Claude session

Paste this as the user's first message (or use it as a `CLAUDE.md` prelude, or prepend it to a `.claude/context/*.md` file):

```
You're continuing work on the AI Assembly project — a provotype for the
World Beautiful Business Forum in Athens, May 7-10, 2026. Twelve
non-human voices read conference transcripts overnight and produce
written responses that re-enter the human conversation at breakfast.

A prior Claude session did a full review of this repo and compressed its
understanding into docs/SESSION_HANDOFF.md. Read that first — in full —
before touching anything else. It contains:

- One-minute orientation (what the project is, what state it's in)
- A staged reading plan (stop when you have enough for the task)
- An inventory of recent artifacts (LLM_CALL_INVENTORY, AUDIENCE_BRIEF,
  this handoff itself, plus the Sonnet execution plan as a template)
- Accumulated findings — most already FIXED, with commit refs (§3)
- The full repo file tree, annotated, with ★ for critical and ⚠ for
  known issues
- Forward plan (Voice Pipeline build, Step 3 spec, closing show)
- What NOT to touch (run artifacts, archives, historical notes)

After reading SESSION_HANDOFF.md, skim:

- docs/LLM_CALL_INVENTORY.md — every LLM call's parameters (reference)
- docs/CURRENT_STATE.md — authoritative status
- docs/AI_Assembly_Briefing_v3_1.md — project source of truth

Then tell me what you're about to do and wait for confirmation before
making any edits. I'll give you the specific task from there.

A few meta rules for this project:
- Don't touch files under any /runs/ directory or /_archive/ directory.
- Prefer editing specs in docs/ over editing delta docs in notes/.
- If you find a spec ↔ code mismatch, flag it before deciding which is
  wrong.
- If a doc references a file that doesn't exist (stale pointer), flag
  rather than creating the file to match.

Current working directory: /Users/aienvironment/Desktop/ai-assembly/
Current branch: main
```

Tune the prompt to the specific task. For a *Voice Pipeline build* session:

```
Your specific task: begin building runtime/flows/voice_flow.py per
docs/AI_Assembly_Voice_Pipeline.md. Start by reading the spec + the
relevant handoff doc personas/HANDOFF.md. Propose the Prefect flow
structure (file layout, task decomposition, parameters) before writing
any code. Key constraint: must drop `metadata` and `worked_provocations`
from the persona card before using as Step 1/2 system prompt.
```

---

## 8. Things this handoff can't transfer

Knowledge that takes actual working-through, not just reading:

- **Feel for which specs to trust when they conflict.** Rule of thumb: trust the code, then Briefing v3.1, then the individual pipeline specs, then CURRENT_STATE.md, then notes. But sometimes a pipeline spec has a detail the briefing doesn't — read both.
- **When Provocateur output looks "too Sonnet".** Generic formulations that could be sent to any voice with a word change. The prior session's instinct was: re-run on Opus + thinking on (default), not prompt-tuning.
- **When a Pass N output looks "training-data" instead of "corpus-based".** Pass 4a's `voice_basis` field records this. If it says `training-data`, the primary texts didn't get fetched at Pass 1c.
- **When to HALT vs when to degrade gracefully.** Pass 6 HALTs on missing primary_texts because corpus curation is the only step that absolutely requires them; Pass 4a degrades to training-data with a warning. The pattern "hard-fail the one step that needs it, soft-fail the rest" is the right template for new pipeline stages.

---

*Written 2026-04-18 by a Claude Opus 4.7 session at ~87% context. If this doc is out of date, it's been drifting at a rate of roughly one commit per finding. Re-verify the "Accumulated findings" section (§3) against the actual code state before trusting it.*
