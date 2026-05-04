#!/usr/bin/env bash
#
# Regenerate the designer package bundle from canonical sources.
#
# By default re-copies:
#   - DESIGNER_BRIEFING_2026-05-04.md (sibling planning/) → DESIGNER_BRIEFING.md
#   - <PROJECT_ROOT>/published_artifacts/                  → sample_data/
#
# With --include-chromatophore, ALSO copies:
#   - docs/runtime_assets/octopus_chromatophore/{jsx,html,md,...} → chromatophore/
#
# The chromatophore files normally stay at their canonical source path
# to avoid drift. Use --include-chromatophore for a self-contained
# zippable handoff to a designer who doesn't have repo access.
#
# Usage:
#   ./rebuild.sh                       # briefing + sample_data only
#   ./rebuild.sh --include-chromatophore  # also copy renderer files
#   AI_ASSEMBLY_PROJECT_ROOT=<path> ./rebuild.sh   # override sample_data source
#
# Idempotent — safe to re-run.

set -euo pipefail

# --- Resolve paths ---
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BUNDLE_DIR="$SCRIPT_DIR"
REPO_ROOT="$( cd "$BUNDLE_DIR/../../.." && pwd )"

PLANNING_DIR="$REPO_ROOT/_workspace/planning"
BRIEFING_SRC="$PLANNING_DIR/DESIGNER_BRIEFING_2026-05-04.md"
CHROMA_SRC="$REPO_ROOT/docs/runtime_assets/octopus_chromatophore"

# PROJECT_ROOT for sample_data — env-overridable.
# Default to the older COMPLETE dryrun (dev_msc_dryrun_1777840771) so
# rebuild produces a usable sample even mid-fresh-run. Once a fresh
# dryrun completes, override:
#   AI_ASSEMBLY_PROJECT_ROOT=/path/to/new_complete_dryrun ./rebuild.sh
DEFAULT_PROJECT_ROOT="/Users/aienvironment/Desktop/AI Assembly/projects/current-tests/dev_msc_dryrun_1777840771"
PROJECT_ROOT="${AI_ASSEMBLY_PROJECT_ROOT:-$DEFAULT_PROJECT_ROOT}"
SAMPLE_SRC="$PROJECT_ROOT/published_artifacts"

INCLUDE_CHROMA=0
for arg in "$@"; do
    case "$arg" in
        --include-chromatophore) INCLUDE_CHROMA=1 ;;
        --help|-h)
            grep '^#' "$0" | grep -v '^#!'
            exit 0
            ;;
        *)
            echo "Unknown arg: $arg" >&2
            echo "Try --help" >&2
            exit 2
            ;;
    esac
done

echo "Rebuilding designer package: $BUNDLE_DIR"
echo "  briefing source:    $BRIEFING_SRC"
echo "  sample data source: $SAMPLE_SRC"
[ "$INCLUDE_CHROMA" -eq 1 ] && echo "  chromatophore src:  $CHROMA_SRC"
echo ""

# --- Briefing ---
if [ ! -f "$BRIEFING_SRC" ]; then
    echo "ERROR: briefing source not found at $BRIEFING_SRC" >&2
    exit 1
fi
cp "$BRIEFING_SRC" "$BUNDLE_DIR/DESIGNER_BRIEFING.md"
echo "  ✓ briefing copied ($(wc -l < "$BUNDLE_DIR/DESIGNER_BRIEFING.md" | tr -d ' ') lines)"

# --- Sample data ---
if [ ! -d "$SAMPLE_SRC" ]; then
    echo "  ⚠ sample_data source not found at $SAMPLE_SRC; skipping sample data"
else
    rm -rf "$BUNDLE_DIR/sample_data"
    mkdir -p "$BUNDLE_DIR/sample_data"
    cp -aR "$SAMPLE_SRC"/* "$BUNDLE_DIR/sample_data/" 2>/dev/null || true
    n_files=$(find "$BUNDLE_DIR/sample_data" -type f | wc -l | tr -d ' ')
    echo "  ✓ sample_data refreshed ($n_files files)"
fi

# --- Chromatophore (opt-in) ---
if [ "$INCLUDE_CHROMA" -eq 1 ]; then
    if [ ! -d "$CHROMA_SRC" ]; then
        echo "ERROR: chromatophore source not found at $CHROMA_SRC" >&2
        exit 1
    fi
    rm -rf "$BUNDLE_DIR/chromatophore"
    mkdir -p "$BUNDLE_DIR/chromatophore"
    cp "$CHROMA_SRC"/octopus_artifact_finaldraft.jsx "$BUNDLE_DIR/chromatophore/"
    cp "$CHROMA_SRC"/octopus_artifact_finaldraft.html "$BUNDLE_DIR/chromatophore/"
    cp "$CHROMA_SRC"/AI_Assembly_Chromatophore_Display_Engine.md "$BUNDLE_DIR/chromatophore/"
    cp "$CHROMA_SRC"/chat_test_artifact_2026_05_02.md "$BUNDLE_DIR/chromatophore/"
    echo "  ✓ chromatophore renderer + spec copied (4 files)"
else
    if [ -d "$BUNDLE_DIR/chromatophore" ]; then
        echo "  ℹ chromatophore folder exists in bundle but --include-chromatophore not passed; left in place"
        echo "    (delete manually if you want it gone, or rebuild with --include-chromatophore to refresh)"
    fi
fi

echo ""
echo "Rebuild complete. Bundle ready at:"
echo "  $BUNDLE_DIR"
