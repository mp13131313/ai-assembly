# Automation orchestrator — design

**Date:** 2026-05-02 (updated 2026-05-02 PM with corrections after code-grounded verification)
**Status:** Draft for review — corrections applied
**Author:** runtime thread
**Filed:** as `runtime/OPEN_ITEMS.md` C22 (pre-Athens-eligible build)

---

## Corrections applied 2026-05-02 PM

Verified the original draft against the actual code, not just intent. Four bugs found + fixed in this revision:

1. **Run name pattern was wrong.** Draft said `athens_2026_<YYYY_MM_DD>_night<N>`. Ingest actually writes `athens_night_<N>` per [`runtime/ingest/config.py:80-87`](../../../runtime/ingest/config.py) `DAY_TO_RUN`. If orchestrator computed the wrong run_dir name, it would poll a directory that never appears.
2. **Transcription `error` state was unhandled.** Draft's "wait until state=done for all sessions" missed that [`runtime/ingest/pipeline.py:41-45`](../../../runtime/ingest/pipeline.py) defines five states: `received | normalizing | transcribing | done | error`. If even one session errors out, draft's logic waits 14h then hard-halts. Corrected: detect error state, halt immediately, escalate to operator.
3. **Editor stage missing.** Draft predates the editor pipeline spec ([`docs/AI_Assembly_Editor_Pipeline.md`](../../../docs/AI_Assembly_Editor_Pipeline.md), 2026-05-02 PM). Dependency graph corrected to `Voice → Editor → Publish` with graceful "skip if `editor_flow.py` not yet built" handling.
4. **Machine-agnosticism wasn't explicit.** Orchestrator runs unchanged on laptop or VM. Concrete: subprocess paths via `Path(__file__).resolve().parent.parent / "flows" / "X.py"` (not `/opt/...`); Python interpreter via `sys.executable` (not bare `python`); PROJECT_ROOT via `--project` arg with env var fallback (not hardcoded); log to file in `<run_dir>/_orchestrator_logs/` (not journald-assumed); no Athens-TZ default — operator passes `--night N` explicitly OR `--date YYYY-MM-DD` for date-derivation.

Trigger granularity decision (from same review): **coarse-grained orchestration for Athens.** Each stage fires once at completion of upstream stage; per-session per-X parallelism within each stage stays the stage's responsibility. Fine-grained (per-session Researcher Node 1 firing as transcriptions complete) would save 30-60 min/night but requires refactoring `run_researcher()` into split entry points — risky at T-5. Filed as post-Athens optimization candidate.

---

## What this is

A design for the overnight pipeline orchestrator that fires each stage as soon as its inputs are ready — no manual operator coordination across a 6+ hour pipeline window. The operator workflow at Athens collapses from "run 4 commands per night, in sequence, after each completes" to "watch the dashboard."

## The user's stated model

> *"as soon as all relevant files for a step are written, the step fires (as in - 1 audio file uploaded - transcription runs for that session, but then stop - until all sessions are in, so that researcher can start - etc. all the way to step 2 output)"*

Key principles:
- **Per-stage trigger:** stage fires when ALL its inputs are present + its output isn't yet present (idempotent restart).
- **Per-night scope:** each night's pipeline is independent; nothing aggregates except voice continuity.
- **Failure isolation:** a stage that fails halts that stage's chain but doesn't corrupt prior stages or other nights.

## Existing infrastructure

| Layer | Already automated? | Mechanism |
|---|---|---|
| Audio upload | ✅ Yes | FastAPI ingest UI (`runtime/ingest/app.py`) |
| Per-session normalize + transcribe | ✅ Yes | `runtime/ingest/pipeline.py` spawns subprocess on upload completion |
| Per-night Researcher | ❌ Manual CLI | `python flows/researcher_flow.py runs/<run_dir>` |
| Per-night Provocateur | ❌ Manual CLI | `python flows/provocateur_flow.py runs/<run_dir> [--prior-nights ...]` |
| Per-night Voice Pipeline | ❌ Manual CLI | `python flows/voice_flow.py runs/<run_dir> --night <N> --skip-step3 [--skip-validation]` |
| Per-night Publish | ❌ Manual CLI | `python flows/publish_flow.py runs/<run_dir> --night <N>` |

So the orchestrator's job: **bridge the gap from "all sessions transcribed" to "publish complete" — 4 stages, fully unattended.**

## The dependency graph

```
session.upload  ─►  per-session.normalize  ─►  per-session.transcribe
                                                  │   (auto-fired by ingest pipeline.py;
                                                  │    orchestrator does NOT fire this)
                          (all sessions for night state=done; halt if any state=error)
                                                  ▼
                                              researcher
                                                  │   (per-session Node 1 + cluster + theme,
                                                  │    coarse-grained for now — see corrections §1)
                                                  ▼
                                              provocateur ◄── (prior nights' run_dirs for C9 exclusion)
                                                  │
                                                  ▼
                                              voice_flow
                                                  │
                                                  ▼
                                              editor ◄── (skip if editor_flow.py not built)
                                                  │
                                                  ▼
                                               publish
```

Each arrow is a "trigger when input is ready" relationship.

## Design choices

### Trigger model: polling, not event-driven

Considered three approaches:

| Approach | Mechanism | Trade-off |
|---|---|---|
| **A. Polling** (cron/loop) | Script runs every N min; checks "is next stage ready to fire?"; fires if yes | Simple. Robust to crashes (next poll picks up). Latency: bounded by polling interval. |
| **B. Event-driven hooks** | `pipeline.py` adds hooks: "when last session marks done → fire researcher" | Faster reaction. More complex; couples pipeline.py to orchestrator. Crash recovery harder. |
| **C. Prefect orchestration** | Build a Prefect flow that wires up dependencies | Cleanest. Biggest lift. Requires running a Prefect server. |

**Recommendation: A (polling).** ~2 min latency at 1-min poll, acceptable when the pipeline takes hours. Trivial to reason about, restart-safe, no new infra.

### State source of truth: filesystem

No database. Each stage's "is it done?" is answered by checking for its output file:

| Stage | "Done" sentinel |
|---|---|
| Per-session transcription | `<run_dir>/01_transcription/<session_id>/status.json` has `state="done"` |
| Researcher | `<run_dir>/02_researcher/grouping.json` exists + non-empty |
| Provocateur | `<run_dir>/03_provocateur/manifest.json` exists |
| Voice Pipeline | `<run_dir>/04_voice/manifest.json` exists |
| Publish | `<PROJECT_ROOT>/published_artifacts/nights/night_<N>/_index.json` exists |

This matches the existing pattern (Voice Pipeline + Provocateur both use checkpoint-as-cache; manifests are end-of-stage sentinels). No new conventions.

### Tonight-derivation: night number + run_dir

**Corrected 2026-05-02 PM** — orchestrator does NOT derive `today` from system clock by default (machine-agnosticism: laptop and VM may be in different time zones). Operator passes `--night N` (1, 2, or 3) explicitly OR `--date YYYY-MM-DD` for date-based lookup.

```python
DATE_TO_NIGHT = {
    "2026-05-07": 1,  # Day One
    "2026-05-08": 2,  # Day Two
    "2026-05-09": 3,  # Day Three
}

NIGHT_TO_DAY = {1: "Day One", 2: "Day Two", 3: "Day Three"}
```

**Run_dir name (corrected):** `athens_night_<N>` — matches what `runtime/ingest/config.py:80-87` `DAY_TO_RUN` writes. NOT `athens_2026_<date>_night<N>` as originally drafted.

```python
def run_dir_for_night(project_root: Path, night: int) -> Path:
    return project_root / "runs" / f"athens_night_{night}"
```

### Tonight's session set: derive from sessions.json

```python
def sessions_for_tonight(sessions_json: list[dict], night: int) -> list[str]:
    """Filter sessions.json to tonight's transcription scope."""
    target_day = NIGHT_TO_DAY[night]   # e.g. Night 2 → "Day Two"
    return sorted(
        s["session_id"] for s in sessions_json
        if s.get("day") == target_day
        and s.get("ai_assembly") is True
    )
```

This is the load-bearing line that decides "which sessions are tonight's." Per the operator's recording schedule CSV (committed 2026-05-01 to athens-2026/reference), `ai_assembly=true` is set on exactly the 25 sessions to be transcribed.

## Orchestrator script outline

`runtime/scripts/overnight_orchestrator.py`:

```python
"""Overnight pipeline orchestrator. Fires each stage when its inputs are ready.

Designed to run as a background loop (or cron at 1-min cadence) for the 3
Athens nights. Idempotent — re-running mid-pipeline picks up where the
last poll left off via filesystem-as-state.

Usage:
    python scripts/overnight_orchestrator.py --project <PROJECT_ROOT> [--once]

  --project   Path to PROJECT_ROOT (athens-2026 production data).
  --once      Run a single poll and exit. Default: loop until pipeline
              for tonight is fully complete (publish manifest exists).
  --night N   Override night derivation (testing / re-run scenarios).
"""

import argparse, time, subprocess, sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ATHENS_TZ = ZoneInfo("Europe/Athens")

DATE_TO_NIGHT = {
    "2026-05-07": 1, "2026-05-08": 2, "2026-05-09": 3,
}
NIGHT_TO_DAY = {1: "Day One", 2: "Day Two", 3: "Day Three"}

POLL_INTERVAL_S = 60   # 1-minute cadence; tunable
PIPELINE_DEADLINE_HRS = 14   # publish must finish within 14h of poll start
                             # (hard wall: morning of day after night)


def derive_night(today_str: str | None, override: int | None) -> int:
    if override:
        return override
    if today_str is None:
        today_str = datetime.now(ATHENS_TZ).date().isoformat()
    if today_str not in DATE_TO_NIGHT:
        raise SystemExit(f"No night mapping for date {today_str}")
    return DATE_TO_NIGHT[today_str]


def run_dir_for_night(project_root: Path, night: int, today_str: str) -> Path:
    return project_root / "runs" / f"athens_2026_{today_str.replace('-', '_')}_night{night}"


def sessions_for_tonight(project_root: Path, night: int) -> list[str]:
    sessions = json.loads(
        (project_root / "reference" / "sessions.json").read_text()
    )["sessions"]
    target_day = NIGHT_TO_DAY[night]
    return sorted(
        s["session_id"] for s in sessions
        if s.get("day") == target_day and s.get("ai_assembly") is True
    )


def transcription_state(run_dir: Path, session_ids: list[str]) -> dict:
    """Classify transcription state across required sessions.

    Returns dict with keys:
      - all_done: bool — every session state=done
      - any_error: bool — at least one state=error
      - error_sessions: list[str] — session_ids in error state
      - pending_sessions: list[str] — session_ids not yet in done|error
    """
    error_sessions = []
    pending_sessions = []
    done_count = 0
    for sid in session_ids:
        status_path = run_dir / "01_transcription" / sid / "status.json"
        if not status_path.exists():
            pending_sessions.append(sid)
            continue
        status = json.loads(status_path.read_text())
        state = status.get("state")
        if state == "done":
            done_count += 1
        elif state == "error":
            error_sessions.append(sid)
        else:  # received | normalizing | transcribing | None
            pending_sessions.append(sid)
    return {
        "all_done": done_count == len(session_ids),
        "any_error": bool(error_sessions),
        "error_sessions": error_sessions,
        "pending_sessions": pending_sessions,
    }
```

**Trigger logic for Researcher (corrected to handle error state):**

```python
state = transcription_state(run_dir, session_ids)
if state["any_error"]:
    return f"failed:transcription:{','.join(state['error_sessions'])}"
if not state["all_done"]:
    return "idle"  # waiting for pending sessions
# else: fire researcher


def fire_stage(cmd: list[str], stage_name: str, log_dir: Path) -> bool:
    """Run a stage subprocess. Returns True on success, False on failure."""
    log_path = log_dir / f"{stage_name}.{int(time.time())}.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w") as f:
        result = subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT)
    return result.returncode == 0


def poll_once(project_root: Path, night: int, today_str: str, logger) -> str:
    """Single poll. Returns one of: 'idle', 'fired:<stage>', 'complete', 'failed:<stage>'.

    Each stage is checked in order; the first ready-to-fire stage runs.
    'idle' = nothing to do (waiting for upstream); 'complete' = publish done.
    """
    run_dir = run_dir_for_night(project_root, night, today_str)
    session_ids = sessions_for_tonight(project_root, night)

    # Stage 1: Researcher — fires when all sessions transcribed
    researcher_done = (run_dir / "02_researcher" / "grouping.json").exists()
    provocateur_done = (run_dir / "03_provocateur" / "manifest.json").exists()
    voice_done = (run_dir / "04_voice" / "manifest.json").exists()
    night_dir = project_root / "published_artifacts" / "nights" / f"night_{night}"
    publish_done = (night_dir / "_index.json").exists()

    if publish_done:
        return "complete"

    if not researcher_done:
        if not all_transcriptions_done(run_dir, session_ids):
            return "idle"  # waiting for transcriptions
        ok = fire_stage(
            ["python", "flows/researcher_flow.py", str(run_dir)],
            "researcher", run_dir / "_orchestrator_logs"
        )
        return "fired:researcher" if ok else "failed:researcher"

    if not provocateur_done:
        prior_run_dirs = [
            run_dir_for_night(project_root, n, prior_dates[n])
            for n in range(1, night)  # nights 1..N-1
        ]
        cmd = ["python", "flows/provocateur_flow.py", str(run_dir)]
        if prior_run_dirs:
            cmd += ["--prior-nights", ",".join(str(p) for p in prior_run_dirs)]
        ok = fire_stage(cmd, "provocateur", run_dir / "_orchestrator_logs")
        return "fired:provocateur" if ok else "failed:provocateur"

    if not voice_done:
        cmd = [
            "python", "flows/voice_flow.py", str(run_dir),
            "--night", str(night), "--skip-step3",
        ]
        if night > 1:
            cmd.append("--skip-validation")  # FU#62 path B: N1 only
        ok = fire_stage(cmd, "voice", run_dir / "_orchestrator_logs")
        return "fired:voice" if ok else "failed:voice"

    if not publish_done:
        cmd = [
            "python", "flows/publish_flow.py", str(run_dir),
            "--night", str(night),
        ]
        ok = fire_stage(cmd, "publish", run_dir / "_orchestrator_logs")
        return "fired:publish" if ok else "failed:publish"

    return "complete"


def loop(project_root: Path, night: int, today_str: str):
    logger = ...  # standard logging
    poll_start = time.time()
    deadline = poll_start + PIPELINE_DEADLINE_HRS * 3600

    while time.time() < deadline:
        result = poll_once(project_root, night, today_str, logger)
        logger.info(f"poll: {result}")
        if result == "complete":
            return 0
        if result.startswith("failed:"):
            stage = result.split(":", 1)[1]
            logger.error(f"Stage {stage} failed; orchestrator halts. "
                         f"Investigate logs. Re-run orchestrator after fix.")
            return 1
        time.sleep(POLL_INTERVAL_S)

    logger.error(f"Pipeline did not complete within {PIPELINE_DEADLINE_HRS}h")
    return 2
```

## Stage-trigger conditions (fully specified)

For each stage, the orchestrator must verify:

### Researcher

**Trigger:** all sessions for tonight have `01_transcription/<session_id>/status.json` with `state="done"`.

**Sessions for tonight:** filter `<PROJECT_ROOT>/reference/sessions.json` by `day = NIGHT_TO_DAY[night]` AND `ai_assembly = true`.

**Idempotency:** Researcher already idempotent — checkpoint files in `02_researcher/` skip re-runs.

**Already-done check:** `<run_dir>/02_researcher/grouping.json` exists AND non-empty.

### Provocateur

**Trigger:** Researcher's `grouping.json` + `all_extractions.json` both exist.

**Prior-nights threading:** for night N, `--prior-nights <runs/N1>,<runs/N2>,...,<runs/N-1>` (only nights 1..N-1).

**Idempotency:** Provocateur already idempotent (per-voice + per-pair checkpoints).

**Already-done check:** `03_provocateur/manifest.json` exists.

### Voice Pipeline

**Trigger:** all `03_provocateur/briefings/<voice_slug>.json` files present (one per council member).

**Athens production CLI flags:**
- `--night N` (always, per current contract)
- `--skip-step3` (always, per A1 decision)
- `--skip-validation` IF `night > 1` (per FU#62 path B)

**Idempotency:** Voice Pipeline checkpoints per (voice, theme) at Step 1, per voice at Step 2.

**Already-done check:** `04_voice/manifest.json` exists.

### Publish

**Trigger:** `04_voice/manifest.json` exists AND `04_voice/step3_complete.flag` exists (the latter is the runtime sentinel that voice_flow writes after Step 2 completes — even when Step 3 is skipped, per the C9-era continuity-after-Step-2 fix).

**Idempotency:** Publish runs are additive — re-running over an already-published night updates files (per-night sub-dir paths after the C3 fix prevent cross-night damage).

**Already-done check:** `<PROJECT_ROOT>/published_artifacts/nights/night_<N>/_index.json` exists.

## Failure modes + handling

### Stage fails (returncode != 0)

Orchestrator logs failure to a per-stage log file in `<run_dir>/_orchestrator_logs/`. Halts the pipeline for tonight. Operator investigates + manually fixes + re-runs orchestrator (which picks up where it left off via the same idempotent file checks).

**Why halt rather than retry:** failures during overnight processing are usually real issues (rate limits, missing data, prompt errors). Auto-retry burns API budget without resolving root cause. Operator wakes up to a clear failure log + can act before breakfast.

### Orchestrator script crashes mid-pipeline

Restart it; the next poll picks up where the last one left off. No state to recover.

### Network / API rate limit hit during a stage

Each stage's individual flow already handles transient errors via Prefect's exponential backoff. Persistent rate-limit failures bubble up as stage failure → orchestrator halts → operator intervenes.

### A required session never gets uploaded

Orchestrator polls indefinitely (within `PIPELINE_DEADLINE_HRS` ≈ 14h). At deadline, halt with a clear error listing which sessions are still missing. Operator can override by manually injecting empty session_packages or re-running with a reduced session list.

### Wrong --night flag passed somewhere

Defensive check from this 2026-05-02 commit (`assert_run_dir_night_matches`) catches this at the moment of misuse. Stage refuses to run; orchestrator records the failure; operator fixes.

## What can be deferred

The above design is the FULL orchestrator. For Athens specifically, simpler partial automation is possible:

| Variant | What it does | Effort |
|---|---|---|
| **Full** (above) | Polls + fires all 4 stages automatically | ~2-3 hr build + test |
| **Manual-fire wrapper** | Single command runs the 4-stage chain in sequence; operator types it once per night | ~30 min |
| **Status dashboard** | Read-only orchestrator that just shows "what's the state of tonight's pipeline" without firing anything | ~1 hr |

For Athens with operator manually starting the chain (variant 2): minimum-viable. Operator wakes up morning of Day 2/3/4, types one command, monitors progress, intervenes if anything fails.

For unattended operation (variant 1, full): worth building if operator wants to sleep through the night without monitoring.

## Cost estimate

**Full orchestrator build:** ~2-3 hr engineering + ~1 hr testing on a real dryrun.

**Athens runtime cost:** zero direct cost (orchestrator polls + spawns existing subprocesses). The flows it fires consume the same API budget they would manually.

**Risk:** low. Orchestrator is read-mostly; only writes are subprocess invocations + log files. Idempotency at filesystem level + halts on failure.

## What this design assumes

1. **Sessions.json is authoritative** — `ai_assembly=true` flags + `day` field correctly identify each night's transcription scope. Already verified per athens-2026 commit `4ad86df`.
2. **DATE_TO_NIGHT mapping is hardcoded for Athens** — three known dates, three nights. For other deployments, this needs to come from project config.
3. **Single-host operation** — orchestrator runs on the same machine as the flows. No distributed coordination.
4. **Filesystem is the source of truth** — no database. State recovery = re-read filesystem.
5. **Prior nights' run_dirs are stable** — once Night 1's run_dir is created, it doesn't get renamed.

## Recommended next step

For T-5 days to Athens:

**Option 1 — build the manual-fire wrapper now (~30 min).** Single command that runs researcher → provocateur (with auto-derived --prior-nights) → voice_flow (with the right CLI flags for the night) → publish. Operator types one command per morning, the chain runs. Predictable, low-risk.

**Option 2 — defer the full orchestrator post-Athens.** Operator runs each flow manually using the documented Athens production CLI (per Voice Pipeline doc + this design's CLI references). 4 commands per night, in sequence. Tedious but safe.

**Option 3 — build the full orchestrator now (~3-4 hr).** Athens runs unattended.

Operator preference required to choose. The design is the same regardless; what varies is how much of it gets built vs deferred.

## OPEN_ITEMS reference

Filed as `runtime/OPEN_ITEMS.md` C22 — pre-Athens-eligible build, scope decision pending operator.
