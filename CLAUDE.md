# AI Assembly — Claude context

## Current branch state (2026-05-29, Athens Nights 1–3 ALL PUBLISHED)

Active branch (runtime-thread): **`main`** at **`563f3ef`** (dashboard
status-color + upload-error-flash + `.json`→render-redirect fixes; ingest
suite 114/114). Athens-2026 at **`3dc4e16`**. **All three Athens nights
are PUBLISHED**: 13 dossiers + 30 per-voice pages across Nights 1–3,
committed + pushed to both repos 2026-05-29.

**Athens Night 2 production results (2026-05-08 panels → published 05-09):**
- ✅ Transcription: 7 sessions — 6 audio + 1 vendor reflection (Dance and
  Dissent). 3 sessions were captured across two recordings, transcribed as
  `__audio2` session duplicates (Act Two / Act Three / The Reality Tunnels)
  → 9 audio files. 1,065 turns / 74,252 words. C49 manual speaker_id
  passthrough on Reality Tunnels primary (many-speaker map).
- ✅ Researcher: 199 extractions / 35 clusters / 8 themes. Wifi-drop
  mid-clustering → resumed from on-disk `all_extractions.json` by calling
  `cluster_extractions.fn()` + `group_clusters_into_themes.fn()` directly
  (`.fn` bypasses the Prefect task wrapper).
- ✅ Provocateur: 46 formulations / 10 briefings.
- ✅ Voice: 46 Step 1 / 10 Step 2. Final validation: 2 PASS, 8 WARN, 0 HOLD.
- ✅ Editor: 5 dossiers · lead = dossier_001 (*WHOSE MOUTH IS MOVING*,
  3 voices). Default framing preserved; Night-1 discipline rules carried
  forward.
- ✅ Publish: `dossiers/night_2/` (5) + `nights/night_2/` (10 voice pages).

**Athens Night 3 — CLOSING EDITION (2026-05-09 panels → published 05-11):**
- ✅ Transcription: 6 sessions — 5 audio + 1 vendor reflection (Make
  Politics Great Again). 2 sessions double-captured → `__audio2` for Act
  Four + Act Five → 7 audio files. 652 turns / 54,038 words. C49 manual
  passthrough ×2 (Long Game, Act Five primary).
- ✅ Researcher: 125 extractions / 14 clusters / 5 themes.
- ✅ Provocateur: 36 formulations / 10 briefings.
- ✅ Voice: 36 Step 1 / 10 Step 2. Final validation: 2 PASS (Battuta +
  Octopus → auto-cleared, no operator gate), 7 WARN, 1 HOLD (Whanganui).
  All 8 WARN/HOLD voices operator-released; the HOLD was a C42 validator
  misfire (`ai_self_acknowledgment` / `first_person_presence_leak` on the
  sacred-grammar rerun), not a content defect. **FINAL-NIGHT notice**
  injected into all 10 `continuity_night_3.json` (gitignored): closing-
  edition *awareness*, not *register*.
- ✅ Editor: 3 dossiers · lead = dossier_002 (*THE BODY OFF THE LEDGER* —
  Lovelace + Marley + Dostoevsky, 3 voices). Tim used ~41K thinking tokens
  across the edition (dossier_002 alone 19,117; trace preserved at each
  dossier's TOP LEVEL — `d['thinking_trace']` — not in `metadata`).
- ✅ Publish: `dossiers/night_3/` (3) + `nights/night_3/` (10 voice pages).
  **Caveat:** the original run published only the 4 late-rerun voice pages
  (cleopatra / plato / scheherazade / whanganui); the other 6 were
  republished 2026-05-29 via `publish_voice_artifacts_for_night(night=3)`.
  Root cause + fix filed as `runtime/OPEN_ITEMS.md` C50.

**Night 2 + Night 3 deployment_context rules** (gitignored at
`runs/athens_night_<N>/_dossier_deployment_context.md` — transcribed here
so they survive the gitignored run dirs). Both nights carry forward Night
1's three rules verbatim (Provotypist anonymization · voices-interleave ·
sacred-grammar discipline for Marley + Whanganui). Per-night additions:
- **N2** — default framing PRESERVED (the panels happened today); cross-
  night threading to Night 1 enabled (≤1 sentence/article, only where N2's
  argument picks up an open Night-1 line).
- **N3 (closing)** — cross-night threading to N1+N2 (9 prior dossiers).
  Load-bearing rule: **"closing-edition AWARENESS, not closing-edition
  REGISTER."** Final night; the voices conclude their service after
  tonight; there is no Night 4. Name an arc's completion ONCE, in-body
  (never in kicker/close). Carry a voice's *own* closing register (a
  riddim coda, a prostagma's seal, a dawn-cut, the riḥla halt's final
  dispatch) into the headnote where the voice authored it — but do NOT
  impose closure on a voice that didn't. Not a retrospective; each dossier
  still bridges its own panels.

**Athens Night 1 production results (2026-05-07 → 2026-05-08):**
- ✅ Transcription: 12/12 sessions landed (9 audio via AssemblyAI + 3
  vendor reflection JSONs via reflection preprocessor + vendor_intake).
  1,454 turns / 80,082 words. Two Act One sessions used manual
  speaker_id passthrough (Sonnet + Opus both produced malformed JSON
  on 47-speaker output; operator-fix path: write passthrough out_02 →
  resume from cleaning-only).
- ✅ Researcher: 205 extractions / 37 clusters / 11 themes (clustering
  hit 40K ceiling on 215-extraction first-pass; bumped CLUSTERING_MAX_TOKENS
  to 64K, retry succeeded at 38K/64K = 59% utilization).
- ✅ Provocateur: 46 formulations across 10 voices (8 themes selected,
  3 dropped); per-voice coverage 5/5 for 7 voices, 4/5 for Whanganui +
  Octopus, 3/5 for Ada (per natural Triage activation distribution).
- ✅ Voice: 46 Step 1 / 10 Step 2 outputs. Two fires — full 10-voice
  (12:00–12:26) + 3-voice rerun (12:55–13:00) for Battuta/Whanganui/
  Cleopatra to remove AI-self-acknowledgment from their artifacts
  (operator decision: only Hannah engages with synthesis as
  load-bearing meta-frame). Final validation: 4 PASS, 6 WARN, 0 HOLD.
- ✅ Editor: 5 dossiers · all 10 voices · lead = dossier_001 (theme_002
  paideia, 4 voices Ada+Hannah+Battuta+Plato, score 190 — best piece
  of writing in the edition per operator). Three editor fires:
  v1 (12:45) initial 7-voice composition · v2 (13:18) full re-fire with
  voices-interleave rule · v2.1 (13:26+13:29) single-dossier fires for
  Marley + Whanganui-pair under sacred-grammar discipline.
- ✅ Publish: `published_artifacts/dossiers/night_1/` + `nights/night_1/`
  committed at `87abdf2` and pushed to GitHub.

**Athens Night 1 deployment_context discipline rules (gitignored at
`runs/athens_night_1/_dossier_deployment_context.md`):**
1. **Provotypist anonymization** — Matthias Peschel does not appear in
   any publishable surface text; his interventions attribute to "the
   Voice of X, channelled into the room from the Assembly."
2. **Voices interleave, do not sequence** — voices appear inside Tim's
   argumentative paragraphs as evidence, not as section-headed
   sequenced exhibits. Quote-floor satisfied by interleaving.
3. **Sacred-grammar discipline** — Rastafari (`I-and-I`, `dawta`,
   `sufferah`, `livity`, `chanting-down`) and te-reo / Tupua-te-Kawa
   (`ea`, `mana`, `tupuna`, `kawa`, `whakapapa`, `mātauranga`) terms
   appear ONLY inside attributed quotation; editor narrative voice
   uses English equivalents. English-naturalized nouns (`iwi`,
   `marae`) and proper nouns (`Wai 167`, `Ruakā Marae`,
   `Te Awa Tupua`) remain as journalistic citation. Applies to Marley
   + Whanganui dossiers (the two voices carrying load-bearing sacred
   grammar in their cards).

**Night 2 + Night 3 carried these rules forward** (the per-night
deployment_context additions are summarized in the state block at the top
of this file). Voice cards stayed stable across all three nights. Pickup
on Nights 2–3 was **manual per-stage fires, not the orchestrator** — once
direct fires are in flight, do NOT also start the orchestrator (it sees
`normalized` state and dispatches duplicate transcriptions on top).

**v4.1 follow-ups filed in `runtime/OPEN_ITEMS.md`** (C42–C52):
C42 safeguards-validator alignment with voice_temporal_stance.default;
C43 validator JSON parse robustness; C44 researcher per-session
extraction caching; C45 editor dossier file-existence caching;
C46 `--single-dossier` index preservation; C47 editorial discipline
rules → permanent prompt patches; C48 voice-pipeline deployment-context
(shelved on branch); **C49 many-speaker speaker_id structured-output
JSON-decode → manual passthrough (recurring transcription failure:
N1 ×2 + N2 ×1 + N3 ×2); C50 `nights/_index.json` clobbered by
single-voice publish (surfaced Athens N3 — left 6 voice pages
unpublished); C51 per-theme published artifacts (`themes/night_N/`)
never generated for any night; C52 event-agnostic config externalization
(Athens-isms hardcoded in `code` — not a zero-edit redeploy).** C42 + C43 both RECURRED in Nights 2–3
(C42 forced the Whanganui N3 operator-release; C43 validator
parse-fallback on Marley N2 + Whanganui N3) — recurrence notes appended
to each entry.

**Architectural validation (Athens-confirmed):** the
`voice_temporal_stance.default` rewrite (athens-2026 `25ec751` +
`5cc04ad` + `3fd94e6`) IS WORKING — voices meta-frame their own
synthesis as an object of critique rather than uncritically extending
it; the §31 Gap-J / Memo §A.9 collision is empirically resolved.

**Pre-Athens build narrative** — the content-seed dryruns (mthd +
wbbf26), the external-reader review on wbbf26 voices, the 5-voice
dryrun + Whanganui kawa finding, and the 2026-05-05→06 runtime commit
log are preserved in the archived handoffs at
`_workspace/archive/runtime-handoffs/` + git history. External-reader
card patches (B-list of 9) tracked in
`_workspace/planning/voices/MEMO_2026_05_07_card_patches_from_external_reader.md`.

**Editor `deployment_context` override mechanism** (this-session new):
`runtime/flows/editor/dossier_generation.py` reads optional
`<run_dir>/_dossier_deployment_context.md` and injects its content as
a `deployment_context` field in the per-dossier user prompt; the
editor prompt at `runtime/flows/shared/prompts/editor_dossier.md`
honours it as override of the default panels-happened-today contract
(translates "the panels said" → "the programme promises" / etc.).
Default behavior unchanged when the override file is absent.

**IMPORTANT for future Claude sessions firing the editor on a non-
Athens-night-N run:** check whether `_dossier_deployment_context.md`
exists at the run_dir root, and if the run's content type is unclear
(panel transcripts vs programme blurbs vs reflections vs other-seed),
**ASK the operator before firing** what the run is reading and
what register Tim should compose in. Do not assume the panel-
happened-today default for non-canonical runs. (See cross-cutting
DON'T in `_workspace/planning/ONBOARDING.md`.)

**Vendor reflection preprocessor** (this-session new):
`runtime/scripts/reflections_to_session_package.py` converts vendor
reflection JSON (per operator's `Reflection Import Format` spec) into
a `session_package.json` shape that `runtime/flows/vendor_intake.py`
validates and lands at `01_transcription/<session_id>/` — same
contract as audio-vendor sessions; downstream Researcher reads
identically. Each `reflections[i]` becomes one turn with
`speaker="Participant {i+1}"`, `role=audience`, `confidence=high`,
preserving original `participant_id`/`duration_seconds` as
`_vendor_*` diagnostic fields. Tested on operator-supplied demo
(10 German reflections, marketing/Nachhaltigkeit topic).

Persona pipeline at **v4** (`docs/AI_Assembly_Persona_Pipeline_v4.md`);
`pipeline_version` string in code: `"4.0"`. v3.10 archived at
`docs/_archive/`. Pipeline architecture includes chunked Pass 1.1–1.7
merge, Phase B per-voice folder layout, Tier 3 code/project separation,
and the FU#1–62 follow-up family (closed/frozen as of 2026-05-01). v4
prompt-architecture extensions:
- 2026-05-04: `corpus_constraint == "lyrics_patterns_only"` conditional
  blocks in Pass 2 / Pass 4a / Pass 4b implementing the SACRED-GRAMMAR
  DEPLOYMENT LIMIT + prose-yard-reasoning artifact spec (Marley v2;
  generalizes to any future musical-corpus voice carrying living sacred
  grammar). See voices/OPEN_ITEMS.md §24.
- 2026-05-05: `mediation_stance == "transmission_witness"` conditional
  blocks in Pass 2 + 3 + 4a + 4b + 5 + 6 implementing the
  TRANSMISSION-WITNESS DEPLOYMENT LIMIT + per-field discipline for
  witness-stance register (Whanganui v2; generalizes to any future
  rights-of-nature legal personalities, treaty-codified positions,
  ancestor-voices). See voices/OPEN_ITEMS.md §28. v4.1 architectural
  cleanup post-Athens captured at voices/OPEN_ITEMS.md §31 (six gaps:
  A coverage gaps ✅ FIXED / B grammar bug ✅ FIXED / C smoke-test
  process gap / D Pass 4a under-covers lexicon-repertoire / E
  per-field discipline incompleteness / F v1 baseline drift on
  uncovered fields).

Voice-build state for athens-2026 (2026-05-05 evening): **10 of 10 panel
voices shipped + promoted + uniformly named** ("Voice of X" convention
across persona_card.voice_name + provocateur_profile.name +
council_config.members[].name + panel_roster.panel_members_final). Voice
of Plato, Voice of Cleopatra, Voice of Fyodor Dostoevsky, Voice of Ibn
Battuta, Voice of the Octopus, Voice of Hannah Arendt, Voice of Ada
Lovelace, **Voice of the Whanganui River v2 (witness-translator
architectural restructure shipped + ATHENS-CLEAN 2026-05-05 evening,
`663dc8f` + `f6afe2c`)**, Voice of Scheherazade, Voice of Bob Marley (v2
Option-3 restructure shipped 2026-05-04 afternoon). council_config.json
fully wired with all 10 pipeline-built provocateur_profiles.

**Architectural updates 2026-05-05 evening (athens-2026 main):**
- All 10 voice_temporal_stance.default fields shifted to assembly-fiction
  ("voice present at the assembly that gathers in Athens, observes
  panels, responds when consulted") per runtime-thread memo
  _workspace/archive/session-artifacts/MEMO_2026_05_05_voice_temporal_stance_assembly_fiction.md;
  shipped `64e9b08`. See voices/OPEN_ITEMS.md §30.
- Length-cap card surgery (operator decision: NO max_tokens enforcement):
  Dostoevsky 350-750w + Hannah Arendt 350-750w + Octopus 350-500w
  prose-channel front-loaded; shipped `9dae9b9`. Closes
  voices/OPEN_ITEMS.md §27 + cross-refs runtime/OPEN_ITEMS.md C38.

13th persona **Tim Leberecht (Assembly editor)** — SHIPPED 2026-05-05
evening. Card placed at `athens-2026/editor/tim_leberecht/` (`799aeb1`).
Runtime `EDITOR_CARD_SUBPATH` renamed `claudia_pinchbeck` →
`tim_leberecht` (`dcff216`); 31/31 runtime tests pass post-rename.
Source-of-truth working tree at `current-tests/editors/tim_leberecht/`.
Tim is editor, NOT panel — not in `panel_roster.json`. Earlier Claudia
Pinchbeck DRAFT card (operator-direct-author placeholder for runtime
dryrun) DEPRECATED on Tim ship. See voices/OPEN_ITEMS.md §29.

**Pre-Athens voice-build work is COMPLETE.**

Pre-Athens follow-ups (operator-side):
- D1 internal position paragraph for Marley appropriation readiness
  (drafts in voices/MARLEY_READINESS_PARAGRAPHS_2026-05-04.md)
- E1 Athens intro paragraph publish-or-hold decision with Till
- Whanganui D1+E1 parallel paragraphs (analogous to Marley)
- Post-Athens Rastafari-orbit + iwi-orbit reader gates calendared

Post-Athens follow-ups (voices/OPEN_ITEMS.md §31):
- v4.1 architectural cleanup: gap E (per-field discipline incompleteness
  in conditional blocks) + gap F (v1 baseline drift on uncovered fields)
  + smoke-test process change + Pass 1 chunked merge audit
- Pass 1c fetch audit follow-ups: Plato Perseus 6 short-fetches + Bob
  Marley voiceofthesufferers.free.fr SSL cert mismatch + Tim
  timleberecht.com SSL TLS errors. Neither affects shipped voice
  runtime; rebuild-only fixes. See voices/OPEN_ITEMS.md §25.

**Pickup pattern:** two workstreams, two subfolders.
- For voice-build work: `_workspace/planning/voices/{ONBOARDING,OPEN_ITEMS,HANDOFF}.md`
- For runtime work: `_workspace/planning/runtime/{ONBOARDING,OPEN_ITEMS,HANDOFF*}.md`
- For cross-cutting rules + DON'Ts: `_workspace/planning/ONBOARDING.md` (thin index)
- Frozen FU# ledger: `_workspace/planning/FOLLOW_UPS.md` (no new entries)

## Filesystem layout (umbrella — Tier 3)

Everything lives under `~/Desktop/AI Assembly/`:

```
~/Desktop/AI Assembly/
├── code/                   # THE GIT REPO — only what's here pushes to GitHub.
│   ├── .env                # shared secrets (gitignored at code/.env)
│   ├── personas/           # persona-pipeline code (v4)
│   ├── runtime/            # runtime-pipeline code
│   ├── docs/               # specs + briefings (current)
│   │   └── _archive/       # historical specs (e.g. v3.10 pipeline)
│   │   └── research/       # preserved baseline Deep Research artifacts (under docs/)
│   └── _workspace/
│       ├── planning/       # active: ONBOARDING (thin index) + FOLLOW_UPS (frozen)
│       │   ├── runtime/    #   runtime-thread workstream (HANDOFF + ONBOARDING + OPEN_ITEMS)
│       │   └── voices/     #   voice-build workstream (HANDOFF + ONBOARDING + OPEN_ITEMS)
│       └── archive/        # historical fix-plans, session-artifacts, consolidations
├── projects/               # NEVER pushed to GitHub — active project data
│   ├── current-tests/      # container for two active test surfaces (NOT itself a PROJECT_ROOT)
│   │   ├── dev_msc_test/   # Researcher/Provocateur dryrun reference data (relocated from archive 2026-05-01)
│   │   └── voice-pipeline-dryrun/   # Voice Pipeline sandbox PROJECT_ROOT (Cleopatra v1/v3, Plato dryruns)
│   └── athens-2026/        # production instance — own git repo (private):
│                           # `mp13131313/ai-assembly-athens2026-voices`
└── archive/                # frozen historical runs + dormant working projects — NEVER pushed
    ├── runs/{personas,runtime}/  # v3.10 baseline + historical runs
    ├── phase-l-plato/      # dormant: Plato shipped to athens-2026 2026-04-26
    ├── phase-l-dostoevsky/ # dormant: Dostoevsky shipped to athens-2026 2026-04-30
    ├── arch_03_baseline_snapshot/, sentinel_baselines/, personas_prompts_PRE_582af96_REVERT_*/  # dev artifacts
```

Project-level files at `<PROJECT_ROOT>/` root (NOT under `inputs/`):
`conference_facts.json`, `audience_profile.json`, `panel_roster.json`.
Runtime artifacts: `reference/sessions.json`, `speakers.json`,
`council_config.json`.

## Repo layout (inside `code/`)

Four categories:

- `docs/`, `runtime/`, `personas/` — **production** slice. Current specs,
  running code, canonical pipeline. In scope for every code review and VM
  deploy.
- `docs/research/` — **preserved grounding**. Deep Research artifacts
  that ground architecture decisions. Not deletable. (Relocated from
  top-level `research/` to `docs/research/` 2026-05-01 to consolidate
  documentation under one tree.)
- `_workspace/planning/` — **forward-looking design + active workstream
  trackers**. Two-workstream structure (see §"Planning / tracking
  conventions" below): `runtime/{HANDOFF, ONBOARDING, OPEN_ITEMS}.md`,
  `voices/{HANDOFF, ONBOARDING, OPEN_ITEMS}.md`, plus a thin root
  `ONBOARDING.md` (cross-cutting DON'Ts + calibration), `FOLLOW_UPS.md`
  (frozen historical ledger of FU#1–62), and dated session handoffs.
- `_workspace/archive/` — **historical docs only** (executed fix plans,
  stale specs, session artifacts, planning consolidation). Run data
  (persona + runtime runs from v3.10 + dev_msc_test rehearsal) and
  development snapshots (arch_03_baseline_snapshot, sentinel_baselines)
  live at the umbrella level under `~/Desktop/AI Assembly/archive/`
  (Tier 3, 2026-04-20). **Out of scope for code reviews and VM deploys
  by default — mention it explicitly if you want Claude to look here.**
- `.env` — shared secrets at `code/.env` (not committed). Both sub-trees
  load from `../.env`.

## Planning / tracking conventions

The `_workspace/planning/` folder splits into two workstream-specific
subfolders + a thin index + a frozen historical FU# ledger:

```
_workspace/planning/
├── ONBOARDING.md              thin index + cross-cutting DON'Ts + calibration
├── FOLLOW_UPS.md              FROZEN historical ledger of FU#1–62 (no new entries)
├── runtime/
│   ├── HANDOFF_<DATE>.md      session-state-of-the-moment
│   ├── ONBOARDING.md          durable runtime onboarding
│   └── OPEN_ITEMS.md          authoritative runtime open items
├── voices/
│   ├── HANDOFF.md             session-state-of-the-moment
│   ├── ONBOARDING.md          durable voices onboarding
│   └── OPEN_ITEMS.md          authoritative voice-build open items
└── HANDOFF_2026_04_27.md … _NIGHT.md (6 dated)  persona-thread historical handoffs
```

**For NEW items, file in the relevant subfolder OPEN_ITEMS:**

- Runtime workstream → `runtime/OPEN_ITEMS.md` (sections A gating / B
  Athens-blocking / C hygiene / D existing FU# index / E docs pending)
- Voices workstream → `voices/OPEN_ITEMS.md` (per its structure)
- Cross-cutting **items** (affect both threads) → file in BOTH subfolder
  OPEN_ITEMS with mutual cross-references
- Cross-cutting **rules / calibration** → root `ONBOARDING.md`
  §"Cross-cutting DON'Ts" or §"Cross-cutting calibration"

**No new FU# numbering.** The FU#1–62 ledger is closed as of 2026-05-01.
Existing FU# references in code, commits, prompts, and docs remain valid;
they resolve to entries in `FOLLOW_UPS.md`. Cross-cutting FUs that
affected both threads (FU#42, 60, 61, 62) stay there as canonical entries.

**Where to file commit references:** for new items, cite the OPEN_ITEMS
section (e.g. `runtime/OPEN_ITEMS.md C9` or `voices/OPEN_ITEMS.md §4`)
rather than coining a FU#. For pre-existing items, FU# references stay
authoritative.

## Code / project separation (Tier 3)

As of 2026-04-20, per-project data lives **outside** this code repo under
a `PROJECT_ROOT` directory. Both the personas pipeline and the runtime
pipeline resolve PROJECT_ROOT via the same shared module
(`flows/shared/project_root.py` in each sub-tree).

Precedence:

1. `--project <path>` CLI arg (personas runners; runtime CLI flows take
   explicit paths)
2. `AI_ASSEMBLY_PROJECT_ROOT` environment variable (typically set in the
   shared `code/.env`)
3. **No fallback** — exits with a clear message. With multiple projects
   active, a silent default risks writing to the wrong one.

Per-voice subfolder layout (under `<PROJECT_ROOT>/voices/<slug>/`) is
documented in `docs/CURRENT_STATE.md` §0.1 and `personas/README.md`.

The athens-2026 production project has its own private backup git repo
(`mp13131313/ai-assembly-athens2026-voices`) for backup of per-project
data; the code repo never touches per-project data.

## Orientation reading order

For a fresh Claude session that needs to understand the project:

1. `CLAUDE.md`, `README.md` (this file + top-level — repo conventions)
2. `_workspace/planning/ONBOARDING.md` (thin index — workstream split +
   cross-cutting DON'Ts + calibration)
3. **For voice-build work:** `voices/ONBOARDING.md` → `voices/OPEN_ITEMS.md`
   → `voices/HANDOFF.md` (~25 min to working knowledge)
4. **For runtime work:** `runtime/ONBOARDING.md` → `runtime/OPEN_ITEMS.md`
   → latest `runtime/HANDOFF_*.md`
5. `_workspace/planning/FOLLOW_UPS.md` (frozen historical ledger of
   FU#1–62; consult only when chasing a specific FU# reference)
6. `docs/README.md` (staleness index for canonical specs)
7. `docs/CURRENT_STATE.md` (gap analysis snapshot)
8. `docs/AI_Assembly_Briefing_v3_1.md` (project source of truth)
9. `docs/AUDIENCE_BRIEF.md` (audience characterization)
10. `docs/AI_Assembly_Persona_Pipeline_v4.md` (current persona pipeline
    spec)
11. Other `docs/AI_Assembly_*_Pipeline.md` and `runtime/` + `personas/`
    code by area, as the task requires

Stop after step 3 (or 4 for runtime work) unless the task demands more
— that's ~25–30 min of working knowledge. Then ask the user for the
specific task.

If a session-artifact references a fix-plan, run artifact, or
consolidation snapshot in `_workspace/archive/`, read it then. Otherwise
treat `_workspace/archive/` as cold storage per the §"Repo layout" rule.

## Separate venvs

Runtime and personas each have their own venv:

- `runtime/venv/` — runtime dependencies (FastAPI, Prefect, AssemblyAI,
  anthropic)
- `personas/venv/` — personas dependencies (Perplexity SDK, google-genai,
  openai, anthropic)

Both currently pin `anthropic==0.94.1`. Separate venvs are for dependency
isolation; if at some point they need to diverge (e.g., to test a new SDK
release against one pipeline without touching the other), the split is
already in place.

Always activate the correct venv for the sub-tree you're working in.

## load_dotenv pattern

All scripts load `.env` from the **monorepo root**
(`REPO_ROOT.parent / ".env"` or `_REPO_ROOT.parent / ".env"`).
Exception: `personas/flows/shared/clients.py` uses bare `load_dotenv()`
intentionally — it walks up from CWD and finds the root `.env`
automatically when scripts are run from the monorepo root or the
`personas/` dir.

## Cross-repo handoff (personas → runtime)

Per voice, the persona pipeline produces three runtime-relevant artifacts:

- **Provocateur Profile** (8 fields) at
  `voices/<slug>/06_derive/01_provocateur_profile.json` → wires into
  `runtime/flows/shared/council/council_config.json` `members[]`.
- **Persona Card** (35 generated + 2 continuity null + metadata) at
  `voices/<slug>/07_persona_card_assembled.json` → loaded as Voice
  Pipeline system prompt (when built). Runtime MUST drop `metadata`,
  `smoke_test_chains`, and (for Step 2 only) `reference_only_passages`.
- **Chat artifact** at `voices/<slug>/06_derive/03_chat_system_prompt.json`
  → operator paste-target for Claude project custom instructions; not
  consumed by runtime pipelines.

See `personas/HANDOFF.md` for the full contract.

## Where specs live

All canonical pipeline specs are in `docs/`:

- `AI_Assembly_Briefing_v3_1.md` — authoritative project briefing (target
  state)
- `AI_Assembly_Persona_Card_v2.md` — 35+2 field card schema (with v2.1
  amendments section, 2026-04-27)
- `AI_Assembly_Persona_Pipeline_v4.md` — persona build pipeline (current,
  2026-04-27)
- `AI_Assembly_Researcher_Pipeline.md` — researcher extraction and
  grouping
- `AI_Assembly_Provocateur_Pipeline.md` — triage, selection, formulation,
  packaging
- `AI_Assembly_Transcription_Pipeline.md` — audio to clean transcript
  pipeline
- `AI_Assembly_Voice_Pipeline.md` — Voice Pipeline Steps 1+2+3 (v2.1,
  updated 2026-05-01; cost figures corrected 2026-05-02 with Opus 4.7
  $5/$25 pricing). **Step 3 SKIPPED for Athens** per OPEN_ITEMS A1
  decision 2026-05-01 (Option A). Validation diagnostic-only (FU#62
  path B); Athens policy Night 1 ON / Nights 2+3 OFF. Athens production
  CLI: `voice_flow.py <run_dir> --night N --skip-step3 [--skip-validation
  if Night 2/3]`. Routing refactor + prompt rewrites + prefix caching +
  cache token tracking landed 2026-05-02 PM (commits `d9ca3f9` + `dfb46f7`);
  synthesis-bias structurally addressed; Test 3 validated. Athens 3-night
  cost ~$60-80 (was claimed $540-700 under deprecated $15/$75 pricing).
- `AI_Assembly_Editor_Pipeline.md` — Editor Pipeline **v2** (refinements
  landed 2026-05-03 PM; v1 was 2026-05-02). Implements Frame Concept v1's
  broadsheet surface as a runtime contract. **Editor as 13th Assembly
  member** (Claudia Pinchbeck) with full persona card; system prompt
  assembled same way as panel voices. **Unit of publication is the dossier**,
  organized by theme. **Substack bridge dropped**, micro-site only.
  **Self-reportage recursion** — *The Assembly* (panel) ≡ *The Assembly*
  (publication). One Anthropic call per dossier on Opus 4.7. Marathon-distance
  issue numbering (Vol. CXVI . No. 42,193 → 42,195 across Athens; Night 3 =
  marathon distance in metres). Athens cost ~$3-5 across 3 nights.
  **v2 contract refinements** (single source family — Provocateur briefings
  + Voice Step 2 artifacts; no Researcher direct read; article-first output
  with shared kicker/headline; no in_brief cross-references; lead-vs-grid
  is publish concern; closing prompt rewrite pending). Predecessor memo at
  `_workspace/archive/MEMO_2026_05_03_editor_flow_input_output_contract.md`
  is **archived** (folded into v2 spec). **Implementation shipped
  2026-05-03 PM** (commit `1437dfc`): `runtime/flows/editor_flow.py` +
  `runtime/flows/editor/*.py` (routing/card_assembly/dossier_generation/
  publish) + `/admin/tonight/editor` drilldown + 38 tests. Pending:
  Claudia's full 35-field card (voices thread), closing prompt rewrite
  to v2 contract. See OPEN_ITEMS A2 (✅ fully resolved) + B1 (🟢
  implementation shipped).
- `AI_Assembly_Runtime_Lifecycle.md` — what happens during an Athens
  night, end to end (v1, 2026-05-02). Stage-by-stage anatomy (trigger,
  reads, writes, sentinel), full filesystem layout, cross-night threading,
  failure modes, manual intervention, Athens 2026 specifics. Read this
  first if you need to understand the runtime as a whole.
- `AI_Assembly_Infrastructure.md` — Athens 2026 deployment spec (v1
  draft, 2026-05-02). Supersedes archived `Infrastructure_Setup.md`.
  Three reasons for VM (ingest + safety + operator-detachment); three
  systemd units (ingest + orchestrator + prefect-server) plus interactive
  Claude Code via mosh+tmux; Hetzner CX22 + Ubuntu 24.04; PROJECT_ROOT
  = clone of athens-2026 private repo at `/opt/ai-assembly-athens2026/`;
  total event cost ~€110-150 + €10-15 VM. Open decisions: domain,
  microsite hosting, backup strategy, Claude-Code-on-VM auth. See
  OPEN_ITEMS B10 (🟡 specified, awaiting operator input on items 1+2).
- `AUDIENCE_BRIEF.md` — audience characterization
- `LLM_CALL_INVENTORY.md` — call inventory (needs update for new
  passes since 2026-04-21)
- `_archive/AI_Assembly_Persona_Pipeline_v3_10.md` — archived (preceding
  pipeline spec)
- `_workspace/archive/specs/AI_Assembly_Architecture_v1.md` — STALE
  (archived; n8n vs Prefect)
- `_workspace/archive/specs/AI_Assembly_Infrastructure_Setup.md` — STALE
  (archived; rclone/Drive vs FastAPI upload). **Superseded** by
  `AI_Assembly_Infrastructure.md` 2026-05-02. Do not consult.

Forward-looking design + active tracking lives in
`_workspace/planning/`. Executed fix plans and prior session artifacts
are in `_workspace/archive/`.
