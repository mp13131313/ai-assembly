"""personas copy of flows/shared/model_routing.py — full behavior is tested in
runtime/tests/test_model_routing.py; here: the copy loads the shared file and
matches the runtime copy byte-for-byte."""
from __future__ import annotations

import sys
from pathlib import Path

_PERSONAS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PERSONAS))

from flows.shared import model_routing as mr  # noqa: E402


def test_runtime_copy_is_identical():
    twin = _PERSONAS.parent / "runtime" / "flows" / "shared" / "model_routing.py"
    assert twin.read_bytes() == Path(mr.__file__).read_bytes()


def test_loads_shared_config():
    assert mr.CONFIG_PATH == _PERSONAS.parent / "model_routing.json"
    assert mr.step_config("personas.pass_2").model == "claude-opus-4-7"
