#!/usr/bin/env bash
# batch_pre_dr.sh — Pass 0a + Phase 0.5 for several voices in parallel.
#
# The claude.ai Deep Research step is the real wall-time bottleneck
# (~60–180 min per voice). This script runs everything UP TO that step
# for N voices concurrently, so you can paste N DR prompts into N
# browser tabs and have claude.ai researching in parallel.
#
# Usage:
#     personas/scripts/batch_pre_dr.sh <voices.txt> [--parallel N] [--project PATH]
#
# voices.txt — one voice per line, "name | wiki_url" (or "name | NON_HUMAN"
# for voices that use non_human_grounding/<slug>.md instead of Wikipedia).
# Comments (# ...) and blank lines are ignored. Example:
#     # Athens panel, human voices first
#     Plato              | https://en.wikipedia.org/wiki/Plato
#     Hannah Arendt      | https://en.wikipedia.org/wiki/Hannah_Arendt
#     Octopus            | NON_HUMAN
#     Whanganui River    | NON_HUMAN
#
# Defaults: --parallel 3 (Perplexity rate limits cap real throughput
# regardless; 3 concurrent is a reasonable starting point).
#
# Outputs (all under PROJECT_ROOT, resolved via AI_ASSEMBLY_PROJECT_ROOT
# or --project):
#     inputs/voices/<slug>.json                  (Pass 0a config)
#     inputs/voices/<slug>_pass0a_review.md      (Pass 0a review doc)
#     inputs/dossiers/_dr_prompts/<slug>_*.md    (Phase 0.5 DR prompt)
#     batch_logs/<slug>.log                      (combined stdout/stderr)
#
# Idempotent: the underlying runners cache Pass 1a (Perplexity) and
# Pass 1b (Gemini) JSON outputs; re-running a failed voice resumes from
# the last completed step.

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV_PY="$REPO_ROOT/venv/bin/python"

[ -x "$VENV_PY" ] || { echo "No Python venv at $VENV_PY" >&2; exit 1; }

VOICES_FILE="${1:-}"
if [ -z "$VOICES_FILE" ] || [ ! -f "$VOICES_FILE" ]; then
    sed -n '3,40p' "$0" >&2
    exit 2
fi
shift

PARALLEL=3
while [ $# -gt 0 ]; do
    case "$1" in
        --parallel) PARALLEL="$2"; shift 2 ;;
        --project)  export AI_ASSEMBLY_PROJECT_ROOT="$2"; shift 2 ;;
        -h|--help)  sed -n '3,40p' "$0"; exit 0 ;;
        *) echo "Unknown arg: $1" >&2; exit 2 ;;
    esac
done

# Fall back to the .env's AI_ASSEMBLY_PROJECT_ROOT if not already set.
if [ -z "${AI_ASSEMBLY_PROJECT_ROOT:-}" ] && [ -f "$REPO_ROOT/../.env" ]; then
    _project_line=$(grep '^AI_ASSEMBLY_PROJECT_ROOT=' "$REPO_ROOT/../.env" \
                    | head -1 | cut -d= -f2- || true)
    # Strip surrounding quotes if present.
    _project_line="${_project_line%\"}"; _project_line="${_project_line#\"}"
    [ -n "$_project_line" ] && export AI_ASSEMBLY_PROJECT_ROOT="$_project_line"
fi
: "${AI_ASSEMBLY_PROJECT_ROOT:?set AI_ASSEMBLY_PROJECT_ROOT or pass --project <path>}"
[ -d "$AI_ASSEMBLY_PROJECT_ROOT" ] || {
    echo "PROJECT_ROOT does not exist: $AI_ASSEMBLY_PROJECT_ROOT" >&2; exit 1; }

LOG_DIR="$AI_ASSEMBLY_PROJECT_ROOT/batch_logs"
mkdir -p "$LOG_DIR"

# Slug function matches personas/flows/shared/io.py::voice_slug
# (lowercase, collapse non-alphanumeric runs to `_`, strip ends).
slug_of() {
    echo "$1" | tr '[:upper:]' '[:lower:]' \
        | sed -E 's/[^a-z0-9]+/_/g; s/^_//; s/_$//'
}

# Per-voice driver. Args: name, wiki_url_or_NON_HUMAN.
# Writes full output to $LOG_DIR/<slug>.log; echoes brief start/end
# lines to stdout so the user can watch the batch progress.
run_one() {
    local name="$1" wiki="$2"
    local slug; slug="$(slug_of "$name")"
    local log="$LOG_DIR/${slug}.log"
    : >"$log"
    echo "[$(date +%H:%M:%S)] START   $name  (slug=$slug)"

    local wiki_args=()
    [ "$wiki" != "NON_HUMAN" ] && wiki_args+=(--wiki "$wiki")

    if ! "$VENV_PY" "$REPO_ROOT/run_pass0a_voice_config.py" "$name" \
            "${wiki_args[@]}" >>"$log" 2>&1; then
        echo "[$(date +%H:%M:%S)] FAIL 0a $name  — see $log"
        return 1
    fi
    if ! "$VENV_PY" "$REPO_ROOT/run_phase0_1_research.py" "$name" \
            >>"$log" 2>&1; then
        echo "[$(date +%H:%M:%S)] FAIL 0.5 $name  — see $log"
        return 1
    fi

    local prompt="$AI_ASSEMBLY_PROJECT_ROOT/inputs/dossiers/_dr_prompts/${slug}_dr_prompt.md"
    local size="?"
    [ -f "$prompt" ] && size="$(wc -c <"$prompt" | tr -d ' ')"
    echo "[$(date +%H:%M:%S)] DONE    $name  — DR prompt: $size chars"
}
export -f run_one slug_of
export VENV_PY REPO_ROOT LOG_DIR

# Parse voices file.
SPECS=()
while IFS= read -r line || [ -n "$line" ]; do
    line="${line%%#*}"
    line="$(echo "$line" | sed -E 's/^[[:space:]]+|[[:space:]]+$//g')"
    [ -z "$line" ] && continue
    name="$(echo "$line" | awk -F'|' '{sub(/^[[:space:]]+/,"",$1); sub(/[[:space:]]+$/,"",$1); print $1}')"
    wiki="$(echo "$line" | awk -F'|' '{sub(/^[[:space:]]+/,"",$2); sub(/[[:space:]]+$/,"",$2); print $2}')"
    [ -n "$name" ] || continue
    [ -n "$wiki" ] || { echo "Missing wiki URL (or NON_HUMAN) for '$name' in $VOICES_FILE" >&2; exit 1; }
    SPECS+=("${name}|${wiki}")
done < "$VOICES_FILE"

[ "${#SPECS[@]}" -gt 0 ] || { echo "No voices parsed from $VOICES_FILE" >&2; exit 1; }

echo "Batch Pass 0a + Phase 0.5 for ${#SPECS[@]} voices (parallel=$PARALLEL)"
echo "  PROJECT_ROOT: $AI_ASSEMBLY_PROJECT_ROOT"
echo "  Logs:         $LOG_DIR/"
echo ""

# Dispatch. xargs -P caps concurrency; each sub-shell runs one voice.
printf '%s\n' "${SPECS[@]}" \
    | xargs -I {} -P "$PARALLEL" bash -c '
        spec="$1"
        name="${spec%%|*}"
        wiki="${spec#*|}"
        run_one "$name" "$wiki"
    ' _ {}

# Summary.
echo ""
echo "=== SUMMARY ==="
fails=0
for spec in "${SPECS[@]}"; do
    name="${spec%%|*}"
    slug="$(slug_of "$name")"
    prompt="$AI_ASSEMBLY_PROJECT_ROOT/inputs/dossiers/_dr_prompts/${slug}_dr_prompt.md"
    if [ -f "$prompt" ]; then
        echo "  ✓ $name  →  inputs/dossiers/_dr_prompts/${slug}_dr_prompt.md"
    else
        echo "  ✗ $name  —  see $LOG_DIR/${slug}.log"
        fails=$((fails + 1))
    fi
done

echo ""
if [ "$fails" -gt 0 ]; then
    echo "$fails voice(s) failed. Inspect logs and re-run the script (cached outputs resume)."
    exit 1
fi

echo "All $((${#SPECS[@]})) DR prompts ready."
echo ""
echo "Next: open claude.ai (Opus 4.7 + Extended Thinking + Deep Research),"
echo "one tab per voice, paste each DR prompt, wait ~90 min, save to:"
echo "  \$AI_ASSEMBLY_PROJECT_ROOT/inputs/dossiers/<slug>_claude_dr.md"
echo "Then run: venv/bin/python run_persona_pipeline.py \"<voice>\""
