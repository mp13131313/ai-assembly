"""call_validator_ladder — the cross-model validator ladder shared by
Passes 7-anachronism, 7a and 7a FINAL (mocked API wrappers, no network).

Each rung must be routed by its vendor in model_routing.json, not by its
position (the old code sent every rung but the last to OpenAI and the last
to Gemini, whatever they were).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_PERSONAS_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PERSONAS_ROOT))

from flows.shared import clients  # noqa: E402
from flows.shared import model_routing as mr  # noqa: E402

VERDICT = {"overall": "PASS", "field_issues": []}


@pytest.fixture
def ladder_config(tmp_path, monkeypatch):
    """Point the loader at a temp config whose one step has the given ladder."""
    def _set(ladder: list[str]) -> str:
        base = json.loads(mr.CONFIG_PATH.read_text(encoding="utf-8"))
        p = tmp_path / "model_routing.json"
        p.write_text(json.dumps({"models": base["models"],
                                 "steps": {"v": {"model": ladder[0], "ladder": ladder}}}))
        monkeypatch.setattr(mr, "CONFIG_PATH", p)
        return "v"
    return _set


def _openai_ok(**kw):
    return {"model": kw["model"], "usage": {"input_tokens": 1}, "json": VERDICT}


def _gemini_ok(**kw):
    return {"model": kw["model"], "usage": {}, "text": "```json\n" + json.dumps(VERDICT) + "\n```"}


def _fail(**kw):
    raise RuntimeError("boom")


def test_routes_by_vendor_not_position(ladder_config, monkeypatch):
    step = ladder_config(["gemini-2.5-pro", "gpt-4.1"])
    monkeypatch.setattr(clients, "call_gemini", _gemini_ok)
    monkeypatch.setattr(clients, "call_openai", _fail)  # must not be reached

    v = clients.call_validator_ladder(step, system="s", user="u", warn=lambda m: None)

    assert v == {"validator": "google:gemini-2.5-pro", "model": "gemini-2.5-pro",
                 "usage": {}, "result": VERDICT}


def test_failed_rung_falls_through_with_per_model_effort(ladder_config, monkeypatch):
    step = ladder_config(["gpt-5.4", "gpt-4o"])
    calls = []

    def fake_openai(**kw):
        calls.append((kw["model"], kw["reasoning_effort"]))
        return _fail() if kw["model"] == "gpt-5.4" else _openai_ok(**kw)

    monkeypatch.setattr(clients, "call_openai", fake_openai)
    warnings = []

    v = clients.call_validator_ladder(step, system="s", user="u", warn=warnings.append)

    assert calls == [("gpt-5.4", "high"), ("gpt-4o", None)]
    assert v["validator"] == "openai:gpt-4o" and v["result"] == VERDICT
    assert len(warnings) == 1 and "gpt-5.4 failed" in warnings[0]


def test_every_rung_failing_returns_none(ladder_config, monkeypatch):
    step = ladder_config(["gpt-4o", "gemini-2.5-pro"])
    monkeypatch.setattr(clients, "call_openai", _fail)
    monkeypatch.setattr(clients, "call_gemini", _fail)
    warnings = []

    assert clients.call_validator_ladder(step, system="s", user="u", warn=warnings.append) is None
    assert len(warnings) == 2


def test_claude_rung_is_refused_before_any_call(ladder_config, monkeypatch):
    step = ladder_config(["gpt-5.4", "claude-sonnet-4-6"])
    monkeypatch.setattr(clients, "call_openai", _fail)  # would be swallowed if reached
    with pytest.raises(mr.ModelRoutingError, match="cross-model"):
        clients.call_validator_ladder(step, system="s", user="u")


def test_shipped_ladders_are_openai_then_google():
    for step in ("personas.pass_7_anachronism", "personas.pass_7a", "personas.pass_7a_final"):
        vendors = [mr.model_vendor(m) for m in mr.step_config(step).ladder]
        assert vendors == ["openai"] * 4 + ["google"], step
