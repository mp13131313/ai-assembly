"""Static guard: no hardcoded model-selection literals outside model_routing.json.

Every persona LLM call site should get its model from
`flows.shared.model_routing.step_config(...)` (directly, or via a helper that
forwards `step=`) rather than a literal string. This test greps the source
tree for quoted literals shaped like a model id — `"claude-opus-4-7"`,
`"gpt-5.4"`, `"gemini-2.5-pro"`, `"sonar-deep-research"`, `"o3"` — and fails if
any turn up outside the known exemptions.

Excluded from the scan entirely (per the routing-refactor ground rules):
  - flows/shared/model_routing.py — the source of truth; full of literals by
    design.
  - tests/ — this directory; fixtures and golden tables legitimately name
    models.
  - The two dev/QC scripts (phase_5_cross_persona_qc.py,
    scripts/standalone_pass4b_test.py) — explicitly left unconverted; they
    call the API wrappers with hardcoded models directly.

A handful of pre-existing lines are NOT model *selection* literals — they're
vendor-family/request-shape gates (e.g. "is this an o-series reasoning
model?", "does this rung want reasoning_effort=high?") where the model
itself already came from config. Those are marked inline with
`MODEL-LITERAL-OK` and skipped here; see the comment on each such line for
the specific justification.
"""
from __future__ import annotations

import re
from pathlib import Path

_PERSONAS_ROOT = Path(__file__).resolve().parent.parent

_EXCLUDED_FILES = {
    _PERSONAS_ROOT / "flows" / "shared" / "model_routing.py",
    _PERSONAS_ROOT / "phase_5_cross_persona_qc.py",
    _PERSONAS_ROOT / "scripts" / "standalone_pass4b_test.py",
}
_EXCLUDED_DIR_PARTS = {"tests", "venv", "__pycache__"}

_MODEL_LITERAL_RE = re.compile(
    r"""["'](?:claude-(?:opus|sonnet|haiku|fable)-[\w.]*|gpt-[\w.]+|gemini-[\w.]+|sonar-[\w.]+|o3)["']"""
)

_EXEMPT_MARKER = "MODEL-LITERAL-OK"


def _source_files():
    for path in sorted(_PERSONAS_ROOT.rglob("*.py")):
        rel_parts = path.relative_to(_PERSONAS_ROOT).parts
        if any(part in _EXCLUDED_DIR_PARTS for part in rel_parts[:-1]):
            continue
        if path in _EXCLUDED_FILES:
            continue
        yield path


def test_no_hardcoded_model_literals():
    offenders = []
    for path in _source_files():
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if _EXEMPT_MARKER in line:
                continue
            if _MODEL_LITERAL_RE.search(line):
                offenders.append(f"{path.relative_to(_PERSONAS_ROOT)}:{lineno}: {line.strip()}")
    assert not offenders, (
        "Hardcoded model-selection literal(s) found outside model_routing.json "
        "— route through flows.shared.model_routing.step_config() instead "
        "(or add a MODEL-LITERAL-OK-marked justification if it's genuinely not "
        "a model-selection literal):\n" + "\n".join(offenders)
    )


def test_scan_actually_covers_the_converted_call_sites():
    """Sanity check on the scanner itself: make sure it isn't accidentally
    excluding the files this refactor touched (a bug here would make the
    test above pass vacuously)."""
    scanned = set(_source_files())
    for rel in (
        "run_persona_pipeline.py",
        "run_pass0a_voice_config.py",
        "run_pass_0b_tailor.py",
        "run_pass_1_7.py",
        "run_phase0_1_research.py",
        "flows/shared/clients.py",
        "flows/shared/chunk_runner.py",
        "flows/shared/pass_7pre_chunked.py",
    ):
        assert _PERSONAS_ROOT / rel in scanned, f"expected {rel} to be scanned"
