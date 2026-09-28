"""Static guard: every step_config("...")/step="..." key used in personas
source actually exists in model_routing.json.

Catches the class of bug where a call site is wired to a step name that was
typo'd or never added to the shared config — which would otherwise only
surface as a `ModelRoutingError` the first time that code path executes
(during a real, costly pipeline run).
"""
from __future__ import annotations

import json
import re
from pathlib import Path

_PERSONAS_ROOT = Path(__file__).resolve().parent.parent
_REPO_ROOT = _PERSONAS_ROOT.parent

_EXCLUDED_FILES = {
    _PERSONAS_ROOT / "flows" / "shared" / "model_routing.py",
}
_EXCLUDED_DIR_PARTS = {"tests", "venv", "__pycache__"}

# Two call shapes in the wild: `step_config("personas.foo")` (direct lookups,
# e.g. for ladders/fallbacks) and `step="personas.foo"` (the call_claude /
# _claude_pass calling convention). `step=<a variable>` (e.g. `step=fb` for a
# nested fallback StepConfig) isn't a string literal and is intentionally not
# matched — its origin step_config(...) call is matched separately.
_STEP_CONFIG_CALL_RE = re.compile(r'step_config\(\s*["\'](personas\.[\w.]+)["\']')
_STEP_KWARG_RE = re.compile(r'\bstep\s*=\s*["\'](personas\.[\w.]+)["\']')


def _source_files():
    for path in sorted(_PERSONAS_ROOT.rglob("*.py")):
        rel_parts = path.relative_to(_PERSONAS_ROOT).parts
        if any(part in _EXCLUDED_DIR_PARTS for part in rel_parts[:-1]):
            continue
        if path in _EXCLUDED_FILES:
            continue
        yield path


def _used_step_keys() -> set[str]:
    used: set[str] = set()
    for path in _source_files():
        text = path.read_text(encoding="utf-8")
        used.update(_STEP_CONFIG_CALL_RE.findall(text))
        used.update(_STEP_KWARG_RE.findall(text))
    return used


def test_all_used_step_keys_exist_in_model_routing_json():
    routing = json.loads((_REPO_ROOT / "model_routing.json").read_text(encoding="utf-8"))
    known_steps = set(routing["steps"])

    used = _used_step_keys()
    assert used, "expected to find step_config()/step= usage in personas source — scanner regression?"

    missing = used - known_steps
    assert not missing, (
        "step key(s) used in personas source but absent from model_routing.json: "
        f"{sorted(missing)}"
    )


def test_all_wired_steps_are_used_somewhere():
    """The inverse check: every personas.* step in model_routing.json should be
    referenced by at least one call site (a step defined but never used is
    dead config, likely a sign a call site was missed during conversion)."""
    routing = json.loads((_REPO_ROOT / "model_routing.json").read_text(encoding="utf-8"))
    personas_steps = {s for s in routing["steps"] if s.startswith("personas.")}

    used = _used_step_keys()
    unused = personas_steps - used
    assert not unused, f"personas.* step(s) defined in model_routing.json but never referenced: {sorted(unused)}"
