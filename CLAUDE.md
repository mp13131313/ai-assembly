# AI Assembly — Claude context

## Current branch state (2026-05-07 early Day 1)

Active branch (runtime-thread): `feature/editor-deployment-context`,
last push **`bad8e33`** plus this-session changes pending commit (editor
deployment_context mechanism + reflection preprocessor + voices-stream
memo + doc updates). Athens-2026 at `82a0af9` plus this-session
`published_artifacts/` from the two pre-Athens production-equivalent
runs pending commit.

**Pre-Athens content-seed dryruns FIRED end-to-end** (production-
equivalent; operator ruled them as production runs):
- `athens-2026/runs/ai_democracy_marathon_opening_2026_05_06/` (mthd
  source — 5 themes / 17 clusters / 77 extractions / 15/15 speakers
  in reference). Provocateur → Voice (Step 1+2) → Editor with default
  panel-content framing. 10/10 voice artifacts. 5/5 dossiers; edition
  lead = dossier_001 (*Standing for the more-than-human*; score 180).
- `athens-2026/runs/preconference_wbbf_programme_2026_05_06/` (wbbf26
  source — programme blurbs; 5 themes / 14 clusters / 66 extractions
  / 29/30 speakers). Provocateur → Voice → Editor v1 (default), then
  re-fired Editor v2 with `_dossier_deployment_context.md` reframing
  the run as the assembly reading the WBBF programme **before** the
  conference opens. 10/10 voice artifacts. 4/4 dossiers; edition lead
  = dossier_001 (*The more-than-human horizon*; score 200).

Total dryrun spend ~$16. Bug fixes shipped during dryrun execution:
Voice-of-X naming mismatch in Provocateur (Triage `f733be3` +
Formulation `a6be256`), Fyodor Dostoevsky folder-slug rename in
athens-2026 (`35336f1`).

**External-reader review** on the wbbf26 voice artifacts (operator-
shared 2026-05-07 AM) produced a 3-group taxonomy of voice-craft
seams (apparatus-transposition / register-faithful-but-too-clean /
different-relation), 2 concrete factual errors (Cleopatra P.Bingen
45 dating; Marley "Marathon philosopher" coinage), 3 diction slips
(Lovelace), and confirmation that the §28/§24 architectural choices
succeeded for Octopus + Scheherazade + Whanganui.

Findings consolidated at
`_workspace/planning/voices/MEMO_2026_05_07_card_patches_from_external_reader.md`
(B-list of 9 per-voice card patches incl. Hannah Arendt AF/hard_limits
reconciliation; C-list architectural patterns; D-list temporal-stance
findings). Card patches will be applied by voice stream.

See `_workspace/planning/runtime/DRYRUN_PLAN_2026_05_06_pre_athens_seeds.md`
for the original ready-to-fire commands + decision points.

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

**Key finding from inspecting the May-5 5-voice dryrun outputs**:
the assembly-fiction reframe (athens-2026 `64e9b08`) APPENDED
assembly clauses to existing `voice_temporal_stance.default` text
rather than replacing it. Four of the five voices in that dryrun
still OPEN with "You speak from within your own world and lifetime
[biographical anchor]" — the v1 framing — with assembly-presence
clauses appended later in the field. Whanganui v2 (witness-translator)
is the exception with full replacement. Net: voices see two framings
in the same field; adaptive thinking under structured-output pressure
may default to the stronger biographical anchor. **Not a caching
propagation issue (Anthropic cache is content-keyed); a prompt-
content design issue.** Filed as a `voices/OPEN_ITEMS §31` Gap-E
candidate for v4.1 cleanup post-Athens. If you want assembly-fiction
to fully bite, the field text needs to LEAD with assembly-presence,
not append it.

**Late-session work (2026-05-05 PM → 2026-05-06 AM, runtime branch):**

| Commit | What landed |
|---|---|
| `1de4081` | Tim's closing prompt rebuilt to mirror voice Step 1+2 merged structure (14 blocks); newspaper/edition framing dropped; three-pole bridge task; "the Voice of X" naming; quote rule with floor + multi-voice ≥2 voices; Beauty-Shot aphoristic close direction. |
| `2a80e8e` | Synthesis routing — Sonnet router replaces lowest-numbered tiebreaker (closes B1 TODO); pushed UPSTREAM into voice Step 2's `_resolve_primary_theme_id` so new artifacts land authoritative `lineage.primary_theme_id` at write-time even for synthesis cases. Editor's Cases 2/B retained as safety nets. Newspaper masthead chrome retired (ATHENS_VOLUME / ATHENS_BASE_ISSUE constants + NIGHT_TO_PUB_DATE map + issue_no/vol/publication_date/edition_label fields stripped end-to-end). thinking_trace + thinking_tokens captured in dossier metadata. Dashboard render shows trace collapsibly; voice-routing + dossiers sections always render with empty-state. |
| `419fcac` | Panel-speaker attribution end-to-end — dossier_generation joins `reference/speakers.json` into `panel_speakers[]`; Tim's prompt cites by name + role/title; dashboard quote audit splits voice-quote vs panel-speaker with per-quote attribution. Provocateur deployment context — `THE GATHERING` + `THE SPEAKERS` blocks injected into all three Provocateur system prompts (triage_voice + triage_flags + formulation), no new LLM calls. |
| `48f4c9d` | Validator field-name bug — `step2_validation.py` was reading `lineage.grounding_extraction_ids` but Step 2 writes the union as `lineage.all_grounding_extraction_ids`. Fix reads `all_*` with bare-name fallback. Re-validation flipped 2 voices WARN→PASS (false positives removed). |
| `b5b8d72` | Editor per-voice review gate (closes 1b/1c) — `gating_status()` classifies voices PASS / released / held / pending-review; `editor_flow.run_editor_pipeline` refuses to run if any pending; CLI `--bypass-gating` for tests. Dashboard auto-fire — `_maybe_auto_fire_editor()` after release/hold writes; idempotent via lockfile + manifest. **Edition Pipeline B3 SHIPPED** — algorithmic lead-theme picker (n_voices×10 + audience_friction_score + fault_line bonus); writes per-night `_index.json` with `edition_lead.lead_dossier_no` + rebuilds root index. Single-response phrasing canonicalized in `voice_step2_artifact.md`. Validator engagement prompt softened (typological-register caveats added). |
| `0e2a897` | **Thinking config FU#60 RESTORED across all 8 LLM-call sites.** Earlier in this session I had drifted voice + editor `_thinking_kwargs` to `{"thinking": {"type": "adaptive"}, "effort": "high"}` — wrong on two counts: (a) `effort` belongs in `output_config={"effort":...}` not top level (was being silently dropped); (b) `high` IS the API default per spec. Reverted everywhere to FU#60 form `{"thinking": {"type": "adaptive", "display": "summarized"}}`. Now identical at: voice/step1 + step2 + step3 + continuity + editor/dossier_generation + researcher_flow + provocateur_flow + personas/clients. |
| `f733be3` | **Provocateur Voice-of-X naming fix #1 (Triage stage).** Model was emitting `voice: "Scheherazade"` (stripped prefix) while runtime kept the council member's full `"Voice of Scheherazade"` name; `setdefault` was no-op and `fresh_voice_by_name` lookup keyed by stripped form. Re-keyed on input `to_run[i]["name"]` and normalized both fresh + cached results. Closes the KeyError that had silently dropped Hannah Arendt's briefing during dryrun firing. |
| `a6be256` | **Provocateur Voice-of-X naming fix #2 (Formulation stage).** Same pattern as Triage: Hannah's formulation files had `"member": "Hannah Arendt"` (stripped) while Plato's had `"Voice of Plato"`; `formulation_by_pair` lookup missed for Hannah → 0 formulations packaged into briefing → no Step 1/2 outputs. Fixed at both cached-load and fresh-collect points in the loop. After both fixes, Provocateur re-pack produces Hannah's complete 5-formulation briefing. |
| (unpushed) | **Editor `deployment_context` override mechanism shipped.** `runtime/flows/editor/dossier_generation.py` reads optional `<run_dir>/_dossier_deployment_context.md` and injects content as `deployment_context` field in user prompt; `runtime/flows/shared/prompts/editor_dossier.md` documents it as override of default panels-happened-today contract. Tested on wbbf26 dryrun: v1 with default contract staged a fictional panel "vote" that hadn't happened ("RECOGNISED, NOT GRANTED / The vote found a flip"); v2 with deployment_context = pre-conference reading correctly framed all 4 dossiers as reading-the-programme ("WHO STAYS AWAKE / What the more-than-human programme delegates"). Validates the architectural patch end-to-end. |
| (unpushed) | **Vendor reflection preprocessor shipped.** `runtime/scripts/reflections_to_session_package.py` per operator's Reflection Import Format spec. Validates reflection-side contract, maps to vendor_intake's session_package.json shape with `Participant {i+1}` turns at role=audience confidence=high, preserves vendor diagnostic metadata. Tested on operator-supplied demo (10 German reflections). End-to-end pass: vendor JSON → preprocessor → vendor_intake → 01_transcription/<sid>/session_package.json (0 warnings). |

**5-voice end-to-end dryrun (2026-05-06 ~00:00–00:12):** isolated
project root `current-tests/dev_5voice_dryrun_2026_05_05/` exercised
Provocateur → Voice (Step 1+2) → Editor for theme_002 (populism)
across Plato + Ibn Battuta + Hannah Arendt + Bob Marley + Whanganui
River. Provocateur produced per-voice reframings ("The Office and
the Soul" for Plato; "The People, Singular" for Arendt; etc.).
Editor composed 1 dossier (562w body, 5 headnotes). Validation
post-fix: 2 PASS (Arendt, Marley), 3 WARN with real findings (Plato,
Ibn Battuta, Whanganui). Total cost ~$10-15. Outputs preserved at
`projects/current-tests/dev_5voice_dryrun_2026_05_05/` for inspection.

**Whanganui kawa-opening finding** (caught during dryrun): voice thread
shipped fix in athens-2026 commit `8c3e9a7` — 3 card patches
(hard_limits forbids unframed cited-te-reo first-person;
characteristic_moves[0] tightened; quality_criteria adds
BILINGUAL-CITATION SPEAKER-FRAME). Note: 5-voice dryrun used the
PRE-patch card (timing — pipeline ran 20 min before 8c3e9a7 landed).
Future voice runs against athens-2026 main use the new discipline.
Generalizable architectural fix (Pass 4b te-reo discipline for cited
first-person sacred-grammar) deferred to v4.1 post-Athens — filed as
voices/OPEN_ITEMS §31 Gap G NEW.

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
