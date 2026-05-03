# Dev MSC Dryrun Plan (2026-05-03 PM)

End-to-end smoke test of the runtime pipeline against fresh inputs (3 MSC panel audios from YouTube). Tests wiring + dashboard observability + cost calibration. Does NOT cover live concurrency at Athens scale, cross-night state, or vendor pipeline.

## Goal

Confirm the runtime pipeline (Stages 0/1 → 2 → 3 → 4) runs end-to-end against fresh inputs with real Anthropic + AssemblyAI calls, while operator observes live via the admin dashboard.

## Scope decisions (locked)

| Decision | Choice | Rationale |
|---|---|---|
| Voices | **3** — `plato`, `cleopatra`, `hannah_arendt` | Three distinct artifact forms: dialogue / prostagma / essay |
| Panels | **3** — breaking_point, vox_populi, west_west_divide | Existing dev_msc_test panels with rich session.json metadata + roster |
| Stages | **0/1 → 2 → 3 → 4** | Skip editor (closing prompt is v1; can't produce v2-shaped output cleanly); skip publish (downstream of editor) |
| Step 3 | skipped | Athens default per OPEN_ITEMS A1 |
| Validation Night 1 | ON | Athens default; exercises full chain |
| Continuity | skipped | Single-night dryrun; no Night 2 to feed |
| Caching pre-work | skip | Post-Athens C19c hygiene; ~$3 Athens savings doesn't justify ~80 min implementation |

## Cost + wall

- ~$25-30 total
- ~30-50 min wall (transcription + voice pipeline dominate)

Per-stage estimate:

| Stage | Wall | Cost |
|---|---|---|
| Stage 0/1 transcription (3 panels parallel) | ~5-10 min | ~$3-5 (AssemblyAI ~$1 + Claude $2-4) |
| Stage 2 Researcher | ~5-10 min | ~$5-10 |
| Stage 3 Provocateur (3-voice subset of council) | ~5-10 min | ~$5-10 (formulation cached) |
| Stage 4 Voice (3 voices) | ~10-15 min | ~$8-12 (Step 1 + validation N1 + Step 2; prefix-cached) |

## Setup

Fresh ephemeral PROJECT_ROOT under `/tmp` to avoid polluting athens-2026 or current-tests trees:

```
/tmp/dev_msc_dryrun_<timestamp>/
├── voices/                                    ← symlink to athens-2026/voices/
│   (only plato, cleopatra, hannah_arendt are referenced; others present but unused)
├── council_config.json                        ← custom: only the 3 test voices' Provocateur Profiles
├── reference/
│   └── speakers.json                          ← MSC panelist bios (derived from session.json roster blocks)
└── runs/
    └── athens_night_1/                        ← name matches dashboard.run_dir_for_night(1)
        └── 01_transcription/
            ├── breaking_point/
            │   ├── audio.m4a                  ← yt-dlp downloads here (96 kbps mono AAC)
            │   └── session.json               ← copied from dev_msc_test/01_transcription/<panel>/
            ├── vox_populi/
            │   ├── audio.m4a
            │   └── session.json
            └── west_west_divide/
                ├── audio.m4a
                └── session.json
```

Setup script writes:
1. `mkdir` the layout
2. Symlink `voices/` to athens-2026
3. Compose subset `council_config.json` with only Plato, Cleopatra, Hannah Arendt provocateur_profiles (read from athens-2026's council_config.json, filter to those 3)
4. Compose `reference/speakers.json` from the per-panel session.json roster blocks
5. Copy session.json files from dev_msc_test into the run_dir transcription subdirs

## Operator hands

1. **Paste 3 YouTube URLs** for the MSC 2026 panels:
   - Breaking Point: The International Order Between Reform and Destruction
   - Vox Populi? Responding to the Rise of Populism
   - The West-West Divide: What Remains of Common Values

2. **Open browser** to `http://127.0.0.1:8765/admin/tonight?night=1` once uvicorn is up (admin / adminmoo). Observe live as stages flip done.

## Execution sequence

### 1. Setup (instant)

Setup script constructs the PROJECT_ROOT layout above.

### 2. yt-dlp fetch × 3 (~5-10 min, free)

```bash
runtime/flows/shared/download_session.sh "<url1>" /tmp/.../runs/athens_night_1/01_transcription/breaking_point/audio.m4a
runtime/flows/shared/download_session.sh "<url2>" /tmp/.../runs/athens_night_1/01_transcription/vox_populi/audio.m4a
runtime/flows/shared/download_session.sh "<url3>" /tmp/.../runs/athens_night_1/01_transcription/west_west_divide/audio.m4a
```

Re-encodes to 96 kbps mono AAC (transcription pipeline's normalization target; ASR quality flat from 256 down to 64 kbps).

### 3. Spin up uvicorn for live observation (instant)

```bash
AI_ASSEMBLY_PROJECT_ROOT=/tmp/dev_msc_dryrun_<ts> \
  ADMIN_APP_PASSWORD=adminmoo UPLOAD_APP_PASSWORD=preview \
  ANTHROPIC_API_KEY=x ASSEMBLYAI_API_KEY=x \
  runtime/venv/bin/python -m uvicorn ingest.app:app --host 127.0.0.1 --port 8765 --log-level warning
```

Operator opens browser to `/admin/tonight?night=1`. Pipeline overview empty initially; lights up as stages run.

### 4. Stage 0/1 transcription × 3 panels (~5-10 min, ~$3-5)

```bash
for panel in breaking_point vox_populi west_west_divide; do
  runtime/venv/bin/python flows/transcription_flow.py \
    /tmp/.../runs/athens_night_1/01_transcription/$panel/audio.m4a \
    /tmp/.../runs/athens_night_1/01_transcription/$panel/session.json &
done
wait
```

Per panel: AssemblyAI Universal-3 Pro → diarized + speaker-attributed → cleaned → `session_package.json` lands. Dashboard's Transcription column ticks up.

### 5. Stage 2 Researcher (~5-10 min, ~$5-10)

```bash
runtime/venv/bin/python flows/researcher_flow.py \
  /tmp/.../runs/athens_night_1
```

Reads all session_packages → Node 1 extraction (per-session) → Node 2 clustering → Node 3 theming → `02_researcher/grouping.json`. Dashboard's Researcher column flips done.

### 6. Stage 3 Provocateur (~5-10 min, ~$5-10)

```bash
runtime/venv/bin/python flows/provocateur_flow.py \
  /tmp/.../runs/athens_night_1
```

Triage flags + per-voice triage (3 voices) + selection + formulation per (voice, theme) pair. Provocateur reads council_config from PROJECT_ROOT (which has only 3 members). Dashboard's Provocateur column flips done.

### 7. Stage 4 Voice (~10-15 min, ~$8-12)

```bash
runtime/venv/bin/python flows/voice_flow.py \
  /tmp/.../runs/athens_night_1 \
  --night 1 \
  --skip-step3 \
  --skip-continuity \
  --voices plato,cleopatra,hannah_arendt
```

Step 1 per (voice, theme) pair → validation (Night 1 ON: anachronism + constitution per pair) → Step 2 per voice. Voice drilldown is the most kinetic surface — Step 1 grid fills cell-by-cell; validation grid fills alongside; Step 2 row appears per voice as Step 2 calls complete.

## Observation surface (live)

Operator watches `/admin/tonight` while pipeline runs. Stage columns flip done left-to-right. Drilldowns light up cell-by-cell.

Concrete observable artifacts:
- **Transcription drilldown** (`/admin/tonight/transcription?night=1`): 3 sessions hit `state=done`. Per-row file links to `session_package.json`.
- **Researcher drilldown**: theme tree (probably 3-5 themes from MSC content), cluster tables, isolates list.
- **Provocateur drilldown**: 3 voices × 3-5 themes triage matrix, formulation grid, theme flags table.
- **Voice drilldown**: Step 1 grid (3 voices × 3-5 themes ≈ 9-15 cells), validation grid (×2 cells per pair), Step 2 row per voice with focus_decision, stance, selected_form, word count.

## Failure modes watched for

| Symptom | Cause | Action |
|---|---|---|
| `download_session.sh` fails | YouTube URL gone / region-locked / age-restricted | Pause; ask operator for alt URL |
| AssemblyAI transcription error | API key / rate limit / file format | Surface error, halt at Stage 1 |
| Voice card load failure | Card schema drift in athens-2026 | Surface error, halt at Stage 4 |
| Anachronism validation fails on a (voice, theme) | Voice card boundary mismatch with MSC content | Continue; log to manifest; document for review |
| Voice pipeline times out on 1 voice | One bad call (network / token limit) | Other voices still complete; manifest records failure |
| Dashboard 401 from operator's browser | Browser cached old creds | Hit `/logout` or close tab |

## Output artifacts (operator can inspect after)

```
/tmp/dev_msc_dryrun_<ts>/runs/athens_night_1/
├── 01_transcription/<panel>/{session_package.json, review.md, out_*.json}
├── 02_researcher/{grouping.json, all_extractions.json, *_extractions.json, clusters.json}
├── 03_provocateur/{manifest.json, selection.json, triage_flags.json,
│                   triage_voices/<voice>.json, briefings/<voice>.json,
│                   formulations/<theme>__<voice>.json}
└── 04_voice/
    ├── step1_detailed_responses/<voice>__<theme>.json
    ├── validation/<voice>__<theme>.json
    ├── step2_first_draft_artifacts/<voice>.json    ← the 3 final artifacts
    └── manifest.json
```

Three voice artifacts:
- `step2_first_draft_artifacts/plato.json` — dialogue form on MSC theme
- `step2_first_draft_artifacts/cleopatra.json` — prostagma on MSC theme
- `step2_first_draft_artifacts/hannah_arendt.json` — essay on MSC theme

Editorially interesting: WBBF-tuned voice cards responding to MSC content. May surface anachronism issues; surfaces voice fidelity in operation against off-domain inputs.

## What this dryrun validates

✅ Cross-stage wiring with REAL data
✅ Dashboard observability against a live-ish run
✅ Cost calibration (1-night smoke gives concrete data point for Athens extrapolation)
✅ Stage 0/1 + Researcher + Provocateur + Voice end-to-end
✅ Anachronism validation behavior on out-of-domain content

## What this dryrun does NOT validate

❌ Concurrency at Athens scale (25 sessions; this test is 3 panels)
❌ Disk space at scale
❌ Cross-night state (continuity, prior_editions, C9 cross-night theme exclusion)
❌ Vendor pipeline integration during a live run
❌ Producer ingest UI workflow (we drive CLI directly)
❌ Editor pipeline (gated on closing-prompt rewrite)
❌ Athens-specific reference data (using MSC content)

For those, B10 T-2 (May 5) full dry-run on the VM with the actual orchestrator is the load-test.

## Cleanup

Demo `/tmp/dev_msc_dryrun_<ts>/` stays around for inspection until operator deletes. uvicorn killed via `pkill -f "uvicorn ingest.app"`.

## Decision gate before starting

1. Confirm 3 voices: plato, cleopatra, hannah_arendt — or different selection?
2. Cost tolerance ~$25-30 confirmed?
3. Operator pastes 3 YouTube URLs

Once those land, setup script + chain executes.

## Cross-references

- `docs/AI_Assembly_Editor_Pipeline.md` v2 (canonical)
- `runtime/OPEN_ITEMS.md` B1 (🟢 implementation shipped) + C19c (🔵 post-Athens caching)
- `runtime/flows/shared/download_session.sh` (yt-dlp fetcher)
- `runtime/flows/transcription_flow.py` / `researcher_flow.py` / `provocateur_flow.py` / `voice_flow.py`
- `runtime/ingest/templates/admin_*.html` (dashboard surfaces — Phase A+B+C all live)
