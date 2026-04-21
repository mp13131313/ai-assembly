#!/usr/bin/env python3
"""Standalone validator for Claude DR dossier files.

Auto-detects input type:
  - Directory → validate as 6-section directory
  - File named NN_section_N.md → per-section validation (1,500-word floor)
  - Any other file → monolithic validation (8,000-word floor)

Usage: python3 scripts/validate_dr_dossier.py <path_to_dossier.md|directory>
Exit codes: 0 = valid, 1 = invalid (with diagnostic message on stderr).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from flows.shared.dr_validation import validate_dr_dossier

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 validate_dr_dossier.py <path|directory>", file=sys.stderr)
        sys.exit(2)
    target = Path(sys.argv[1])
    try:
        validate_dr_dossier(target)
        if target.is_dir():
            print("VALID: all 6 section files meet per-section contract")
        else:
            print("VALID: dossier meets word-count floor and structural checks")
        sys.exit(0)
    except Exception as e:
        print(f"INVALID: {e}", file=sys.stderr)
        sys.exit(1)
