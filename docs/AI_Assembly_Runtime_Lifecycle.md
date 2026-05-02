# AI ASSEMBLY — RUNTIME LIFECYCLE
## What happens during a night, end to end

**Project:** The AI Assembly · World Beautiful Business Forum · Athens · May 7–10, 2026
**Status:** v1 — 2026-05-02
**Purpose:** A single document describing what the runtime does between an audio file landing and a published dossier. Complementary to the per-pipeline specs (Transcription, Researcher, Provocateur, Voice, Editor, Publish), which detail *how* each pipeline works internally — this doc describes *when* each fires, *what* it reads and writes, and *where* on disk to find every artifact at every moment of the night. If you're new to the project and want to understand the runtime as a whole, start here.

---

## 1. The big picture

```
┌─────────────────────────────────────────────────────────────────────┐
│  PANEL (live, 1-2 hr)                                               │
│   ▼                                                                  │
│  HoBB A/V uploads recordings via web UI    ──►  ingest service       │
│                                                  │ (per-session,     │
│                                                  │  fires on upload) │
│                                                  ▼                   │
│                                              transcription           │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
                                                  │ (all sessions
                                                  │  state=done)
┌─────────────────────────────────────────────────▼───────────────────┐
│  ORCHESTRATOR (overnight, 4-8 hr)                                    │
│                                                                      │
│   researcher  ─►  provocateur  ─►  voice  ─►  editor  ─►  publish    │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
                                                  │
┌─────────────────────────────────────────────────▼───────────────────┐
│  MORNING                                                             │
│   Operator opens microsite. Dossiers are live.                       │
│   Goes back to bed. Or to the conference.                            │
└─────────────────────────────────────────────────────────────────────┘
```

**Start trigger:** the first audio file lands at the ingest endpoint via HTTP POST. Ingest spawns a per-session normalize+transcribe subprocess immediately; it does not wait for other sessions.

**End state:** `<PROJECT_ROOT>/published_artifacts/nights/night_<N>/_index.json` exists. The microsite render reads from `published_artifacts/`; once `_index.json` is present, the night is publishable.

**Time budget per night:** transcription parallel with ingest (~5-15 min after panel ends, depending on session count). Then orchestrator: Researcher (~30-60 min), Provocateur (~30-60 min), Voice (~2-4 hr), Editor (~30 min when built), Publish (~5 min). Total: ~4-8 hours. Designed to complete overnight without operator attention.

**Operator's role during the night:** none, by design. Orchestrator runs unattended; halts cleanly on stage failure with logs at `<run_dir>/_orchestrator_logs/`. Operator wakes up to either ✅ complete or ❌ a failure that needs investigation before the day's panel.

---

## 2. The eight stages, in order

Each stage section describes:
- **Trigger** — what condition causes this stage to fire
- **Reads** — input files
- **Writes** — output files (with the **sentinel** marked ★ — the file the next stage's trigger checks for)
- **Done detection** — how the orchestrator (or you) knows this stage finished

### Stage 1 — Audio upload (per session)

- **Trigger:** HoBB A/V producer uploads via the ingest web UI (`https://<vm-hostname>/`). One POST per session.
- **Reads:** none from disk; payload is the audio file.
- **Writes:**
  - `<run_dir>/01_transcription/<session_id>/<original_filename>` — raw upload
  - `<run_dir>/01_transcription/<session_id>/status.json` with `state="received"` ★
- **Fired by:** `runtime/ingest/app.py` on POST to `/upload/<session_id>`.

### Stage 2 — Per-session transcription (fires automatically per upload)

- **Trigger:** upload completes. Spawned synchronously by ingest.
- **Reads:** the uploaded audio file from Stage 1.
- **Writes (state lifecycle):** `<run_dir>/01_transcription/<session_id>/status.json`:
  - `state="normalizing"` → ffmpeg converts to mono 96kbps M4A
  - `state="transcribing"` → AssemblyAI ASR + Anthropic speaker-ID + cleanup
  - `state="done"` ★ (success) **or** `state="error"` (failure with `error` field set)
- **Also writes:**
  - `<run_dir>/01_transcription/<session_id>/audio.m4a` — normalized audio
  - `<run_dir>/01_transcription/<session_id>/pipeline.log` — detailed log
  - `<run_dir>/01_transcription/<session_id>/session_package.json` ★★ — **the per-session artifact downstream consumes** (transcript text, speaker assignments, metadata)
- **Fired by:** `runtime/ingest/pipeline.py:_launch_stage0` → subprocess of `runtime/flows/transcription_flow.py`.
- **Independent across sessions** — each session normalizes/transcribes in its own subprocess. A failure in one session does not block others.

### Stage 3 — Researcher (fires once when all transcriptions done)

- **Trigger:** every session in tonight's scope (`sessions.json` filtered by `day == NIGHT_TO_DAY[night]` AND `ai_assembly == true`) has `status.json` with `state="done"`. If any session has `state="error"`, orchestrator halts and escalates.
- **Reads:** `<run_dir>/01_transcription/*/session_package.json` (all of tonight's).
- **Writes:**
  - `<run_dir>/02_researcher/<session_id>_extractions.json` — per-session Node 1 extractions
  - `<run_dir>/02_researcher/all_extractions.json` — concatenated + namespaced
  - `<run_dir>/02_researcher/clusters.json` — Node 2 Round 1 clustering
  - `<run_dir>/02_researcher/grouping.json` ★ — Node 2 Round 2 themes (the *handoff* artifact)
- **Fired by:** orchestrator runs `python runtime/flows/researcher_flow.py <run_dir>`.
- **Done detection:** `02_researcher/grouping.json` exists.
- **Cost:** ~$5-15 in Anthropic Opus 4.7 calls.

### Stage 4 — Provocateur (fires when Researcher done)

- **Trigger:** `02_researcher/grouping.json` exists.
- **Reads:**
  - `02_researcher/grouping.json` + `02_researcher/all_extractions.json`
  - `<PROJECT_ROOT>/reference/council_config.json` — panel members
  - `<PROJECT_ROOT>/voices/<slug>/06_derive/01_provocateur_profile.json` — per-voice 8-field profile
  - For Night 2/3: `<prior_run_dir>/03_provocateur/selection.json` (C9 cross-night exclusion)
- **Writes:**
  - `<run_dir>/03_provocateur/triage_voices/<member_name_snake>.json` — per-voice triage
  - `<run_dir>/03_provocateur/triage_flags.json`
  - `<run_dir>/03_provocateur/selection.json` — (theme, voice) assignments
  - `<run_dir>/03_provocateur/formulations/<theme_id>__<member_name_snake>.json` — per (theme, voice) formulation
  - `<run_dir>/03_provocateur/briefings/<voice_slug>.json` ★★ — **the per-voice briefing Voice consumes** (one file per council member)
  - `<run_dir>/03_provocateur/manifest.json` ★ — sentinel
- **Fired by:** orchestrator runs `python runtime/flows/provocateur_flow.py <run_dir> [--prior-nights P1,P2]`.
- **Done detection:** `03_provocateur/manifest.json` exists.
- **Cost:** ~$5-15.

### Stage 5 — Voice (fires when Provocateur done)

- **Trigger:** `03_provocateur/manifest.json` exists.
- **Reads:**
  - `03_provocateur/briefings/<voice_slug>.json` (all voices)
  - `<PROJECT_ROOT>/voices/<slug>/07_persona_card_assembled.json` — full 35-field persona card
  - For Night 2/3: `<PROJECT_ROOT>/voices/<slug>/continuity_night_<N-1>.json` — voice's prior-night continuity overlay
- **Writes:**
  - `<run_dir>/04_voice/step1_detailed_responses/<voice_slug>__<theme_id>.json` — per (voice, theme) Step 1 reasoning
  - `<run_dir>/04_voice/validation/<voice_slug>__<theme_id>.json` — Step 1 validation (Night 1 only per FU#62)
  - `<run_dir>/04_voice/step2_first_draft_artifacts/<voice_slug>.json` — per-voice Step 2 artifact
  - `<run_dir>/04_voice/step3_amended_artifacts/<voice_slug>.json` — per-voice Step 3 amendment (skipped for Athens per A1)
  - `<run_dir>/04_voice/responded_to_graph_night_<N>.json` — provenance graph
  - `<run_dir>/04_voice/themes_to_voices_night_<N>.json` — theme/voice assignment record
  - `<run_dir>/04_voice/step3_complete.flag` — continuity sentinel (written even when Step 3 skipped)
  - `<run_dir>/04_voice/manifest.json` ★ — stage sentinel
  - `<PROJECT_ROOT>/voices/<voice_slug>/continuity_night_<N+1>.json` — next-night overlay (cross-night state)
- **Fired by:** orchestrator runs `python runtime/flows/voice_flow.py <run_dir> --night N --skip-step3 [--skip-validation]` (the `--skip-validation` flag added for Night 2/3 only).
- **Done detection:** `04_voice/manifest.json` exists.
- **Cost:** ~$15-30 (the largest stage).

### Stage 6 — Editor (fires when Voice done; SKIP if not built)

- **Trigger:** `04_voice/manifest.json` exists AND `runtime/flows/editor_flow.py` exists.
- **If editor_flow.py does NOT exist:** orchestrator skips this stage cleanly and proceeds to Publish.
- **Reads:**
  - `04_voice/step2_first_draft_artifacts/<voice_slug>.json` (all voices) — voice artifacts
  - `04_voice/manifest.json` — to count + identify what shipped
  - `02_researcher/grouping.json` — themes (for dossier organization)
  - `<PROJECT_ROOT>/editor/claudia_pinchbeck/07_persona_card_assembled.json` — Claudia's persona card
- **Writes:**
  - `<run_dir>/05_editor/dossiers/dossier_<NN>.json` — per-dossier (one per theme) with editor's article + theme page + headnotes
  - `<run_dir>/05_editor/manifest.json` ★ — stage sentinel
- **Fired by:** orchestrator runs `python runtime/flows/editor_flow.py <run_dir> --night N`.
- **Done detection:** `05_editor/manifest.json` exists.
- **Cost:** ~$1-2 across one night (~10 dossiers × Opus 4.7).
- **Status (2026-05-02):** specified, not built. See [Editor Pipeline](AI_Assembly_Editor_Pipeline.md).

### Stage 7 — Publish (fires when Editor done, OR Voice done if no editor)

- **Trigger:** `05_editor/manifest.json` exists (when editor present), OR `04_voice/manifest.json` exists (when not).
- **Reads:** all stage artifacts above.
- **Writes (under `<PROJECT_ROOT>/published_artifacts/`, NOT under `<run_dir>/`):**
  - `published_artifacts/nights/night_<N>/<voice_slug>.json` — per-voice publishable artifact
  - `published_artifacts/nights/night_<N>/_index.json` ★ — night sentinel + manifest
  - `published_artifacts/themes/night_<N>/<theme_id>.json` — per-theme record
  - `published_artifacts/extractions/<extraction_id>.json` — flat extractions
  - `published_artifacts/traces/lineage_graph_night_<N>.json` — provenance
  - `published_artifacts/traces/publish_manifest_night_<N>.json` — publish run record
  - `published_artifacts/voices/<voice_slug>.json` — cross-night per-voice aggregation (rebuilt each publish)
- **Fired by:** orchestrator runs `python runtime/flows/publish_flow.py <run_dir> --night N`.
- **Done detection:** `published_artifacts/nights/night_<N>/_index.json` exists.
- **Cost:** $0 (no LLM calls; pure file shaping).

### Stage 8 — Microsite render (operator-side, separate concern)

- **Trigger:** human or CI/CD picks up changes in `published_artifacts/`.
- **Reads:** `published_artifacts/nights/night_<N>/_index.json` and friends.
- **Writes:** static site → CDN.
- **Status:** out of orchestrator scope; tracked separately as runtime [OPEN_ITEMS B2](../_workspace/planning/runtime/OPEN_ITEMS.md). Could be Vercel, GitHub Pages, etc. The orchestrator's `published_artifacts/` is the contract.

---

## 3. The orchestrator

`runtime/scripts/overnight_orchestrator.py`. Polls the filesystem at 1-min cadence; fires the next stage as soon as its trigger condition is met. **Stops at the failure of any stage** rather than retrying — overnight failures are usually real issues (rate limits, missing data, prompt errors), and auto-retry burns API budget without resolving the cause. Idempotent: restart picks up where the last poll left off, because the trigger conditions are filesystem checks, not in-memory state.

**Stages it does NOT fire:**

- Per-session transcription (auto-fired by ingest at upload time)
- Microsite render (operator-side)

**Stages it does fire:**

Researcher, Provocateur, Voice, Editor (if built), Publish.

**CLI:**

```bash
python runtime/scripts/overnight_orchestrator.py --night N [--project PATH]
                                                 [--once]
                                                 [--poll-s 60]
                                                 [--deadline-h 14]
                                                 [--skip-publish]

# Or by date:
python runtime/scripts/overnight_orchestrator.py --date 2026-05-07 [--project PATH]
```

**Operational queries** (works on laptop or VM, anytime):

```bash
# What state is tonight in?
cat <PROJECT_ROOT>/runs/athens_night_<N>/_orchestrator_logs/status.json

# What does the orchestrator see for each session?
ls <PROJECT_ROOT>/runs/athens_night_<N>/01_transcription/*/status.json | \
    xargs -I{} sh -c 'echo "{}: $(jq -r .state {})"'

# Where in the chain are we?
test -f <PROJECT_ROOT>/runs/athens_night_<N>/02_researcher/grouping.json && echo "researcher done"
test -f <PROJECT_ROOT>/runs/athens_night_<N>/03_provocateur/manifest.json && echo "provocateur done"
test -f <PROJECT_ROOT>/runs/athens_night_<N>/04_voice/manifest.json && echo "voice done"
test -f <PROJECT_ROOT>/published_artifacts/nights/night_<N>/_index.json && echo "publish done"

# What's in the latest stage log?
ls -lt <PROJECT_ROOT>/runs/athens_night_<N>/_orchestrator_logs/*.log | head -3
```

---

## 4. Filesystem layout (full per-night)

The whole runtime contract lives under `<PROJECT_ROOT>` (set via `AI_ASSEMBLY_PROJECT_ROOT` env var or `--project` arg). Everything *for one night* lives under one `runs/athens_night_<N>/` subtree, plus published artifacts at the top level and per-voice continuity overlays.

```
<PROJECT_ROOT>/
├── reference/
│   ├── sessions.json              # input — which sessions to record per day
│   ├── speakers.json              # input — speaker bios + IDs
│   └── council_config.json        # input — panel members
│
├── voices/
│   └── <voice_slug>/
│       ├── 07_persona_card_assembled.json     # input — full 35-field card
│       ├── 06_derive/
│       │   └── 01_provocateur_profile.json    # input — 8-field profile for Provocateur
│       ├── continuity_night_1.json            # written by Voice after Night 1
│       ├── continuity_night_2.json            # written by Voice after Night 2
│       └── continuity_night_3.json            # written by Voice after Night 3
│
├── editor/
│   └── claudia_pinchbeck/
│       └── 07_persona_card_assembled.json     # input — Claudia's card (when authored)
│
├── runs/
│   ├── athens_night_1/                        # ★ ONE DIRECTORY PER NIGHT ★
│   │   ├── _orchestrator_logs/
│   │   │   ├── status.json                    # current orchestrator state
│   │   │   ├── researcher.<unix-ts>.log
│   │   │   ├── provocateur.<unix-ts>.log
│   │   │   ├── voice.<unix-ts>.log
│   │   │   ├── editor.<unix-ts>.log           # (when editor is built)
│   │   │   └── publish.<unix-ts>.log
│   │   │
│   │   ├── 01_transcription/                  # ingest writes here, per-session
│   │   │   └── <session_id>/
│   │   │       ├── status.json                # state machine
│   │   │       ├── <original>.m4a             # raw upload
│   │   │       ├── audio.m4a                  # normalized
│   │   │       ├── pipeline.log
│   │   │       └── session_package.json       # ← Researcher reads this
│   │   │
│   │   ├── 02_researcher/                     # researcher_flow writes here
│   │   │   ├── <session_id>_extractions.json
│   │   │   ├── all_extractions.json
│   │   │   ├── clusters.json
│   │   │   └── grouping.json                  # ← Provocateur reads this; SENTINEL
│   │   │
│   │   ├── 03_provocateur/                    # provocateur_flow writes here
│   │   │   ├── triage_voices/<voice_slug>.json
│   │   │   ├── triage_flags.json
│   │   │   ├── selection.json                 # ← later nights' Provocateur reads this for C9
│   │   │   ├── formulations/<theme_id>__<voice>.json
│   │   │   ├── briefings/<voice_slug>.json    # ← Voice reads these
│   │   │   └── manifest.json                  # SENTINEL
│   │   │
│   │   ├── 04_voice/                          # voice_flow writes here
│   │   │   ├── step1_detailed_responses/<voice>__<theme>.json
│   │   │   ├── validation/<voice>__<theme>.json    # Night 1 only
│   │   │   ├── step2_first_draft_artifacts/<voice>.json   # ← Editor reads these
│   │   │   ├── step3_amended_artifacts/<voice>.json       # skipped Athens (A1)
│   │   │   ├── responded_to_graph_night_1.json
│   │   │   ├── themes_to_voices_night_1.json
│   │   │   ├── step3_complete.flag             # continuity-write sentinel
│   │   │   └── manifest.json                   # SENTINEL
│   │   │
│   │   └── 05_editor/                          # editor_flow writes here (when built)
│   │       ├── dossiers/dossier_<NN>.json
│   │       └── manifest.json                   # SENTINEL
│   │
│   ├── athens_night_2/                         # same structure, Night 2
│   └── athens_night_3/                         # same structure, Night 3
│
└── published_artifacts/                       # publish_flow writes here
    ├── nights/
    │   ├── night_1/
    │   │   ├── <voice_slug>.json              # per-voice publishable artifact
    │   │   └── _index.json                    # ← microsite reads this; SENTINEL
    │   ├── night_2/...
    │   └── night_3/...
    ├── themes/night_<N>/<theme_id>.json
    ├── extractions/<extraction_id>.json
    ├── traces/lineage_graph_night_<N>.json
    ├── traces/publish_manifest_night_<N>.json
    └── voices/<voice_slug>.json               # cross-night per-voice rollup
```

**Key navigation rules:**

- "Where are tonight's voice artifacts?" → `<PROJECT_ROOT>/runs/athens_night_<N>/04_voice/step2_first_draft_artifacts/`
- "Where's the published version?" → `<PROJECT_ROOT>/published_artifacts/nights/night_<N>/`
- "What's the current state of tonight's pipeline?" → `<PROJECT_ROOT>/runs/athens_night_<N>/_orchestrator_logs/status.json`
- "What did stage X do?" → `<PROJECT_ROOT>/runs/athens_night_<N>/_orchestrator_logs/<stage>.<ts>.log`
- "What's persistent across nights for voice X?" → `<PROJECT_ROOT>/voices/<voice_slug>/continuity_night_<N>.json`

---

## 5. Cross-night threading

Three things cross night boundaries:

1. **Voice continuity overlays.** After Voice completes for Night N, it writes `<PROJECT_ROOT>/voices/<slug>/continuity_night_<N+1>.json` for each voice. Voice on Night N+1 reads these to honor cross-night progression (don't re-deploy the same moves; honor what voice already said).

2. **Provocateur cross-night exclusion (C9).** When firing Provocateur for Night 2 or 3, the orchestrator passes `--prior-nights <run_dir_1>[,<run_dir_2>]`. Provocateur reads each prior `selection.json` and excludes (theme, voice) pairs already covered.

3. **Publish cross-night aggregation.** Each Publish run rebuilds `published_artifacts/voices/<voice_slug>.json` to include all nights this voice has shipped through. This is additive — Night 2's Publish doesn't damage Night 1's per-night dossier files.

**Each `runs/athens_night_<N>/` tree is otherwise self-contained** — no artifact written under one night's run_dir is ever read by another night's pipeline.

---

## 6. Failure modes + recovery

| Failure | Detection | Recovery |
|---|---|---|
| One session never gets uploaded | Orchestrator stays "idle" past expected time | Operator uploads it. Orchestrator picks up on next poll. |
| One session transcription errors | Orchestrator returns `failed:transcription` with the failed session_id | Investigate the per-session `pipeline.log`. Common causes: AssemblyAI rate limit, malformed audio, unicode glitch. Fix → re-trigger transcription via ingest UI or directly. Restart orchestrator. |
| Researcher / Provocateur / Voice / Editor / Publish stage fails | Orchestrator returns `failed:<stage>`; log at `_orchestrator_logs/<stage>.<ts>.log` | Read the log. Each flow has internal checkpointing — fixing the issue and re-running the orchestrator (which re-fires the stage) skips work already done. |
| Orchestrator script crashes | systemd restarts it (`Restart=on-failure`) OR operator runs again | Idempotent: filesystem-as-state means it picks up where it left off. |
| VM reboots mid-pipeline | Same as orchestrator crash | systemd restarts on boot. |
| Wrong `--night` flag | `assert_run_dir_night_matches` (in `runtime/flows/shared/io.py`) refuses to run | Defensive check, 9 unit tests in `runtime/tests/test_run_dir_night_check.py`. Catches the silent cross-night corruption failure mode. |
| Pipeline doesn't complete within `--deadline-h` (default 14h) | Orchestrator exits 2 | Investigate which stage was running per `status.json`. Resume manually or restart orchestrator. |

**Operator's morning ritual after any failure:**

1. `cat <run_dir>/_orchestrator_logs/status.json` — last known state
2. `ls -lt <run_dir>/_orchestrator_logs/` — find the most recent stage log
3. `tail -100 <run_dir>/_orchestrator_logs/<stage>.<ts>.log` — read the failure
4. Fix the cause (could be code, data, or external service)
5. `systemctl restart orchestrator@<N>.service` (VM) or re-run the orchestrator script (laptop)

---

## 7. Manual intervention — running stages by hand

If you want to skip the orchestrator entirely or rerun a single stage:

```bash
# All flows take a run_dir as positional argument and a --project that
# resolves PROJECT_ROOT. They're individually idempotent — each has
# internal checkpointing, so re-running picks up where the last left off.

python runtime/flows/researcher_flow.py <PROJECT_ROOT>/runs/athens_night_<N>

python runtime/flows/provocateur_flow.py <PROJECT_ROOT>/runs/athens_night_<N> \
    [--prior-nights <PROJECT_ROOT>/runs/athens_night_1,...]

python runtime/flows/voice_flow.py <PROJECT_ROOT>/runs/athens_night_<N> \
    --night <N> --skip-step3 [--skip-validation]   # --skip-validation for Night 2/3

python runtime/flows/editor_flow.py <PROJECT_ROOT>/runs/athens_night_<N> \
    --night <N>     # when editor is built

python runtime/flows/publish_flow.py <PROJECT_ROOT>/runs/athens_night_<N> \
    --night <N>
```

**To re-run a single stage from scratch** (rather than resume), delete its sentinel:

```bash
# Re-run Voice from scratch
rm <PROJECT_ROOT>/runs/athens_night_<N>/04_voice/manifest.json
# Now voice_flow will start fresh (existing checkpoints in subdirs may still be picked up)
```

**To force a full re-run of a stage** including its checkpoints:

```bash
rm -rf <PROJECT_ROOT>/runs/athens_night_<N>/04_voice
# Voice runs cleanly from scratch. Costs full API budget.
```

---

## 8. Athens 2026 specifics

| Date | Night | Day | Sessions | Run dir |
|---|---|---|---|---|
| 2026-05-07 | 1 | Day One | 10 | `runs/athens_night_1/` |
| 2026-05-08 | 2 | Day Two | 9 | `runs/athens_night_2/` |
| 2026-05-09 | 3 | Day Three | 6 | `runs/athens_night_3/` |
| **Total** | | | **25** | |

(Counts derived from `<PROJECT_ROOT>/reference/sessions.json` filtered by `day == NIGHT_TO_DAY[night]` AND `ai_assembly == true`.)

**Operator commands per night, on the VM:**

```bash
# Before Night 1, evening of May 7:
sudo systemctl start orchestrator@1.service
sudo journalctl -u orchestrator@1 -f

# Before Night 2, evening of May 8:
sudo systemctl start orchestrator@2.service

# Before Night 3, evening of May 9:
sudo systemctl start orchestrator@3.service
```

**Expected timing for a typical night** (assuming all sessions clean, no rate limits):

| Stage | Wall time |
|---|---|
| Panel | 1-2 hr (live) |
| Last upload → all transcriptions done | 5-15 min |
| Researcher | 30-60 min |
| Provocateur | 30-60 min |
| Voice | 2-4 hr |
| Editor (when built) | 30 min |
| Publish | 5 min |
| **Total: panel end → publish complete** | **4-8 hours** |

**Estimated cost per night (Opus 4.7 $5/$25):**

| Stage | Cost |
|---|---|
| Transcription (AssemblyAI + Anthropic speaker-ID) | $5-10 |
| Researcher | $5-15 |
| Provocateur | $5-15 |
| Voice | $15-30 |
| Editor | $1-2 |
| Publish | $0 |
| **Total per night** | **~$30-70** |
| **Total Athens (3 nights)** | **~$90-210** |

---

## 9. Cross-references

- [Voice Pipeline](AI_Assembly_Voice_Pipeline.md) — Stage 5 internals
- [Editor Pipeline](AI_Assembly_Editor_Pipeline.md) — Stage 6 internals (specified, not built)
- [Researcher Pipeline](AI_Assembly_Researcher_Pipeline.md) — Stage 3 internals
- [Provocateur Pipeline](AI_Assembly_Provocateur_Pipeline.md) — Stage 4 internals
- [Transcription Pipeline](AI_Assembly_Transcription_Pipeline.md) — Stage 2 internals
- [Infrastructure spec](AI_Assembly_Infrastructure.md) — VM layout, deployment, services
- [Ingest deploy README](../runtime/ingest/deploy/README.md) — provisioning checklist
- [Orchestrator script](../runtime/scripts/overnight_orchestrator.py) — implementation
- [Orchestrator design doc](../_workspace/planning/runtime/AUTOMATION_ORCHESTRATOR_DESIGN_2026_05_02.md) — design decisions + corrections
- [Orchestrator tests](../runtime/tests/test_orchestrator.py) — 22 trigger-path tests
