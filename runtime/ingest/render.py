"""Schema-aware artifact rendering for /admin/render route.

Detects artifact type by PROJECT_ROOT-relative path pattern and dispatches
to per-type templates that surface the prose-heavy fields nicely instead
of dumping raw JSON.
"""
from __future__ import annotations

import re
from typing import Optional

# Path patterns → template name + display label.
# Order matters: more specific first.
_PATTERNS: list[tuple[re.Pattern, str, str]] = [
    (re.compile(r"04_voice/step1_detailed_responses/.+\.json$"),
     "admin_render_step1.html", "Voice — Step 1 (private reasoning)"),
    (re.compile(r"04_voice/step2_first_draft_artifacts/.+\.json$"),
     "admin_render_step2.html", "Voice — Step 2 (first-draft artifact)"),
    # C28b Step 2 validation (3 pillars: Safeguards / Engagement /
    # Voice fidelity + cross-night echo). Distinct shape from old
    # Step 1 validation; gets its own template.
    (re.compile(r"04_voice/step2_validation/.+\.json$"),
     "admin_render_step2_validation.html", "Voice — Step 2 Validation"),
    (re.compile(r"04_voice/validation/.+\.json$"),
     "admin_render_validation.html", "Voice — Validation (Step 1, legacy)"),
    (re.compile(r"03_provocateur/formulations/.+\.json$"),
     "admin_render_formulation.html", "Provocateur — Formulation"),
    (re.compile(r"03_provocateur/briefings/.+\.json$"),
     "admin_render_briefing.html", "Provocateur — Briefing (per voice)"),
    (re.compile(r"03_provocateur/triage_voices/.+\.json$"),
     "admin_render_triage.html", "Provocateur — Per-voice triage"),
    # Editor dossier output — the publishing unit. Renders kicker/
    # headline/subline/body/theme page/headnotes nicely instead of raw
    # JSON. Matches the published copy AND the run_dir copy.
    (re.compile(r"(published_artifacts/dossiers/night_\d+|05_editor/dossiers)/dossier_\d+\.json$"),
     "admin_render_dossier.html", "Editor — Dossier"),
]


def detect_artifact(rel_path: str) -> tuple[str, str]:
    """Return (template_name, display_label) for a path.

    Falls back to ('admin_render_json.html', 'JSON file') for unmatched paths.
    """
    for pat, tpl, label in _PATTERNS:
        if pat.search(rel_path):
            return tpl, label
    return "admin_render_json.html", "JSON file (raw)"
