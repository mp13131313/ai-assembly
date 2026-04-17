#!/usr/bin/env python3
"""Standalone validator for Claude DR dossier files.

Usage: python3 scripts/validate_dr_dossier.py <path_to_dossier.md>
Exit codes: 0 = valid, 1 = invalid (with diagnostic message on stderr).
"""
import sys
from pathlib import Path

# Add personas/ to path so flows.shared imports work
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from flows.shared.dr_validation import validate_dr_dossier

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 validate_dr_dossier.py <path>", file=sys.stderr)
        sys.exit(2)
    try:
        validate_dr_dossier(Path(sys.argv[1]))
        print("VALID: dossier meets six-section contract and word-count floor")
        sys.exit(0)
    except Exception as e:
        print(f"INVALID: {e}", file=sys.stderr)
        sys.exit(1)
