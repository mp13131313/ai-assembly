# AI Assembly — Claude context

## Current branch state (2026-04-27)

Active branch: `arch-03-additive-merge` (~136 commits ahead of `main`, PR
#2 open). The persona pipeline has been substantially re-engineered under
arch-03 (chunked Pass 1.1–1.7) + Phase B (per-voice folder layout) + Tier
3 (code/project separation) + the FU#1–50 follow-up family. **Pipeline
v4** is now the current spec (`docs/AI_Assembly_Persona_Pipeline_v4.md`,
2026-04-27). v3.10 archived at `docs/_archive/`.

`pipeline_version` string in code: `"4.0"` (was `"3.10"`).

Plato shipped + chat-test validated 2026-04-26 → Phase L sign-off. Voice
3–12 buildout for athens-2026 is at Phase 0.5 complete (12 voice_configs
+ Phase 0.5 research for all 12); 11 × 6 = 66 manual claude.ai DR
sessions outstanding. 212/212 tests passing.

**Pickup doc:** `_workspace/planning/HANDOFF_2026_04_27.md` (authoritative
session pickup). On any fresh session, read that first.
**Permanent onboarding:** `_workspace/planning/ONBOARDING.md`.

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
│   ├── research/           # preserved baseline research
│   └── _workspace/
│       ├── planning/       # active: HANDOFF_2026_04_27, FOLLOW_UPS, ONBOARDING
│       └── archive/        # historical fix-plans, session-artifacts, specs
├── projects/               # NEVER pushed to GitHub — active project data
│   ├── test/               # sandbox / experimentation (Dostoevsky lives here)
│   │   └── voices/<slug>/  # 00_intake/ 01_research/ 02_merge/ … 06_derive/ 07_persona_card_assembled.json
│   ├── phase-l-plato/      # Plato Phase L working project
│   ├── phase-l-dostoevsky/ # Dostoevsky Phase L working project
│   └── athens-2026/        # production instance — own git repo (private):
│                           # `mp13131313/ai-assembly-athens2026-voices`
└── archive/                # frozen historical runs — NEVER pushed
    └── runs/{personas,runtime}/  # v3.10 baseline + dev_msc_test rehearsal
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
- `research/` — **preserved grounding**. Deep Research artifacts that
  ground architecture decisions. Not deletable.
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
2. `_workspace/planning/HANDOFF_2026_04_27.md` (current session pickup —
   READ FIRST on any fresh session)
3. `_workspace/planning/ONBOARDING.md` (permanent fresh-session pickup;
   maintained going forward)
4. `_workspace/planning/FOLLOW_UPS.md` (active follow-up tracker — single
   source of truth for FU#1–50)
5. `docs/README.md` (staleness index for canonical specs)
6. `docs/CURRENT_STATE.md` (gap analysis snapshot — what's built, what's
   not, architectural decisions)
7. `docs/AI_Assembly_Briefing_v3_1.md` (project source of truth — target
   state)
8. `docs/AUDIENCE_BRIEF.md` (audience characterization +
   contributors-vs-audience distinction)
9. `docs/AI_Assembly_Persona_Pipeline_v4.md` (current persona pipeline
   spec)
10. Other `docs/AI_Assembly_*_Pipeline.md` and `runtime/` + `personas/`
    code by area, as the task requires

Stop after step 4 unless the task demands more — that's ~30–45 min of
working knowledge. Then ask the user for the specific task.

If a session-artifact references a fix-plan or run artifact in
`_workspace/archive/`, read it then. Otherwise treat `_workspace/archive/`
as cold storage per the §"Repo layout" rule.

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
- `AI_Assembly_Voice_Pipeline.md` — Voice Pipeline Steps 1+2 (Step 3
  unspecified — FU#49E flagged as highest-impact post-Athens item)
- `AUDIENCE_BRIEF.md` — audience characterization
- `LLM_CALL_INVENTORY.md` — call inventory (needs update for new
  passes since 2026-04-21)
- `_archive/AI_Assembly_Persona_Pipeline_v3_10.md` — archived (preceding
  pipeline spec)
- `_workspace/archive/specs/AI_Assembly_Architecture_v1.md` — STALE
  (archived; n8n vs Prefect)
- `_workspace/archive/specs/AI_Assembly_Infrastructure_Setup.md` — STALE
  (archived; rclone/Drive vs FastAPI upload)

Forward-looking design + active tracking lives in
`_workspace/planning/`. Executed fix plans and prior session artifacts
are in `_workspace/archive/`.
