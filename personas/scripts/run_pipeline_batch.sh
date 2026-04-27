#!/usr/bin/env bash
# run_pipeline_batch.sh — batch wrapper for run_persona_pipeline.py
#
# Concentrates the --project flag in one place to avoid the wrong-folder
# accident when DR data lands per voice. REQUIRES --project explicitly;
# does NOT fall back to AI_ASSEMBLY_PROJECT_ROOT env var (env-var fallback
# is fine for single ad-hoc runs but dangerous for batches that may run
# unattended for hours).
#
# Usage:
#   scripts/run_pipeline_batch.sh \
#       --project /path/to/athens-2026 \
#       [--parallel N]                      # default 1 (sequential)
#       [--from-file path/to/voices.txt]    # one voice name per line, # ignored
#       [voice_name ...]                    # or pass voices as positional args
#
# Examples:
#   # Single voice:
#   scripts/run_pipeline_batch.sh --project ../../projects/athens-2026 "Cleopatra"
#
#   # Multiple voices in parallel (3 at a time):
#   scripts/run_pipeline_batch.sh --project ../../projects/athens-2026 \
#       --parallel 3 "Cleopatra" "Octopus" "Whanganui River"
#
#   # From a file:
#   scripts/run_pipeline_batch.sh --project ../../projects/athens-2026 \
#       --from-file ../../projects/athens-2026/voices_pipeline_queue.txt
#
# Per-voice logs land at $PROJECT_ROOT/batch_logs/<slug>.pipeline.log.
# Each run resumes from cache (FU#5 + FU#13) — failed voices can be re-run.

set -euo pipefail

PROJECT=""
PARALLEL=1
FROM_FILE=""
VOICES=()

usage() {
    sed -n '2,30p' "$0" | sed 's/^# //; s/^#//'
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --project) PROJECT="$2"; shift 2 ;;
        --parallel) PARALLEL="$2"; shift 2 ;;
        --from-file) FROM_FILE="$2"; shift 2 ;;
        --help|-h) usage; exit 0 ;;
        --*) echo "Unknown flag: $1" >&2; usage; exit 2 ;;
        *) VOICES+=("$1"); shift ;;
    esac
done

if [[ -z "$PROJECT" ]]; then
    echo "ERROR: --project PATH is required for batch runs." >&2
    echo "       (Env-var fallback is intentionally disabled here to prevent" >&2
    echo "        wrong-folder accidents during unattended batches.)" >&2
    echo "" >&2
    usage >&2
    exit 2
fi

# Resolve project to absolute path; fail loudly if it doesn't exist.
if [[ ! -d "$PROJECT" ]]; then
    echo "ERROR: --project does not exist or is not a directory: $PROJECT" >&2
    exit 2
fi
PROJECT_ABS="$(cd "$PROJECT" && pwd)"

# Read voices from --from-file if provided.
if [[ -n "$FROM_FILE" ]]; then
    if [[ ! -f "$FROM_FILE" ]]; then
        echo "ERROR: --from-file not found: $FROM_FILE" >&2
        exit 2
    fi
    while IFS= read -r line; do
        # Strip whitespace; skip blank lines and # comments.
        trimmed=$(echo "$line" | sed 's/^[[:space:]]*//; s/[[:space:]]*$//')
        [[ -z "$trimmed" || "$trimmed" == \#* ]] && continue
        # Each line may be "<name>" or "<name> | <wiki_url>" — take just the name.
        name=$(echo "$trimmed" | awk -F'|' '{print $1}' | sed 's/[[:space:]]*$//')
        VOICES+=("$name")
    done < "$FROM_FILE"
fi

if [[ ${#VOICES[@]} -eq 0 ]]; then
    echo "ERROR: no voice names provided (positional args or --from-file)." >&2
    usage >&2
    exit 2
fi

# Locate personas dir from this script's location (scripts/ is sibling).
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PERSONAS_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PERSONAS_DIR"

# Load shared .env if present (sources API keys; PROJECT_ROOT will be
# overridden per-call by --project flag).
[[ -f ../.env ]] && { set -a; source ../.env; set +a; }

LOGDIR="$PROJECT_ABS/batch_logs"
mkdir -p "$LOGDIR"

START_TS=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
echo "======================================================================"
echo "BATCH RUN — $START_TS"
echo "  PROJECT:  $PROJECT_ABS"
echo "  PARALLEL: $PARALLEL"
echo "  VOICES:   ${#VOICES[@]} voices: ${VOICES[*]}"
echo "  LOGDIR:   $LOGDIR"
echo "======================================================================"

# Track results.
RESULTS_FILE="$LOGDIR/_batch_results_${START_TS//:/-}.txt"
echo "voice|exit_code|log_path|wall_seconds" > "$RESULTS_FILE"

run_one() {
    local voice="$1"
    local slug
    slug=$(echo "$voice" | tr '[:upper:] ' '[:lower:]_')
    local log="$LOGDIR/$slug.pipeline.log"
    local t0
    t0=$(date +%s)
    echo "[batch] $voice → $log (started $(date -u +%H:%M:%SZ))"

    if venv/bin/python run_persona_pipeline.py "$voice" \
            --project "$PROJECT_ABS" >"$log" 2>&1; then
        local t1=$(date +%s)
        echo "[batch] ✓ DONE: $voice (wall: $((t1-t0))s)"
        echo "$voice|0|$log|$((t1-t0))" >> "$RESULTS_FILE"
        return 0
    else
        local rc=$?
        local t1=$(date +%s)
        echo "[batch] ✗ FAIL: $voice (exit $rc, wall: $((t1-t0))s, log: $log)"
        echo "$voice|$rc|$log|$((t1-t0))" >> "$RESULTS_FILE"
        return 1
    fi
}

if [[ "$PARALLEL" -le 1 ]]; then
    # Sequential. Continue on failure so all voices get a try.
    for v in "${VOICES[@]}"; do
        run_one "$v" || true
    done
else
    # Parallel via background jobs + wait. Limit concurrency by counting
    # active jobs.
    active=0
    for v in "${VOICES[@]}"; do
        run_one "$v" &
        active=$((active + 1))
        if [[ "$active" -ge "$PARALLEL" ]]; then
            wait -n  # wait for any one job to finish
            active=$((active - 1))
        fi
    done
    wait
fi

END_TS=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
echo "======================================================================"
echo "BATCH COMPLETE — $END_TS"
echo ""
echo "Results: $RESULTS_FILE"
column -t -s'|' "$RESULTS_FILE"
echo "======================================================================"

# Exit non-zero if any voice failed, so CI / wrappers see the failure.
if grep -qE '^[^|]*\|[^0]' "$RESULTS_FILE" 2>/dev/null; then
    exit 1
fi
