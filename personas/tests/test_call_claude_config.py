"""Unit tests for call_claude's model_routing integration (mocked Anthropic
client — no network, no API key needed).

Covers the three behaviors the routing refactor added to call_claude:
  (i)   a thinking-off Sonnet-4.6 step still sends temperature
  (ii)  the same call, but the step's model has sampling_params: false in
        model_routing.json, sends NO temperature
  (iii) an explicit effort in the step's config is sent as `output_config`
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

_PERSONAS_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PERSONAS_ROOT))

from flows.shared import model_routing as mr  # noqa: E402
from flows.shared.clients import call_claude  # noqa: E402


def _write_config(tmp_path: Path, steps: dict, models: dict | None = None) -> Path:
    base = json.loads(mr.CONFIG_PATH.read_text(encoding="utf-8"))
    p = tmp_path / "model_routing.json"
    p.write_text(json.dumps({"models": models or base["models"], "steps": steps}))
    return p


def _mock_client_for_create(text: str = "hi", output_tokens: int = 5) -> MagicMock:
    """A mocked anthropic.Anthropic() client for the non-streaming (create) path."""
    client = MagicMock()
    msg = SimpleNamespace(
        content=[SimpleNamespace(type="text", text=text)],
        usage=SimpleNamespace(input_tokens=10, output_tokens=output_tokens),
        stop_reason="end_turn",
    )
    client.messages.create.return_value = msg
    # _estimate_anthropic_thinking_tokens calls count_tokens; let it raise so
    # the function's own except-Exception-return-0 path handles it cleanly.
    client.messages.count_tokens.side_effect = RuntimeError("not needed for this test")
    return client


def test_thinking_off_sonnet_sends_temperature(tmp_path):
    """(i) A thinking-off Sonnet-4.6 step still sends the caller's temperature."""
    cfg_path = _write_config(tmp_path, {
        "s": {"model": "claude-sonnet-4-6", "thinking": "off", "effort": None},
    })
    cfg = mr.step_config("s", path=cfg_path)
    assert cfg.sampling_params is True  # Sonnet 4.6 accepts sampling params

    client = _mock_client_for_create()
    with patch("anthropic.Anthropic", return_value=client):
        call_claude(step=cfg, system="sys", user="usr", max_tokens=100, temperature=0.0)

    kwargs = client.messages.create.call_args.kwargs
    assert kwargs["model"] == "claude-sonnet-4-6"
    assert kwargs["temperature"] == 0.0
    assert "thinking" not in kwargs


def test_sampling_params_false_drops_temperature(tmp_path):
    """(ii) Same shape as above, but the model's config says sampling_params:
    false — temperature must NOT be sent even though thinking is off."""
    cfg_path = _write_config(tmp_path, {
        # claude-opus-4-7 is sampling_params: false in the real models table,
        # and its thinking_can_disable is true, so thinking="off" is valid.
        "s": {"model": "claude-opus-4-7", "thinking": "off", "effort": None},
    })
    cfg = mr.step_config("s", path=cfg_path)
    assert cfg.sampling_params is False

    client = _mock_client_for_create()
    with patch("anthropic.Anthropic", return_value=client):
        call_claude(step=cfg, system="sys", user="usr", max_tokens=100, temperature=0.0)

    kwargs = client.messages.create.call_args.kwargs
    assert kwargs["model"] == "claude-opus-4-7"
    assert "temperature" not in kwargs
    assert "thinking" not in kwargs


def test_effort_sent_as_output_config(tmp_path):
    """(iii) An effort set in the step's config is forwarded as output_config."""
    cfg_path = _write_config(tmp_path, {
        "s": {"model": "claude-sonnet-4-6", "thinking": "off", "effort": "high"},
    })
    cfg = mr.step_config("s", path=cfg_path)
    assert cfg.effort == "high"

    client = _mock_client_for_create()
    with patch("anthropic.Anthropic", return_value=client):
        call_claude(step=cfg, system="sys", user="usr", max_tokens=100, temperature=0.0)

    kwargs = client.messages.create.call_args.kwargs
    assert kwargs["output_config"] == {"effort": "high"}
    assert kwargs["temperature"] == 0.0  # sampling_params True + thinking off — unaffected by effort


def test_explicit_model_overrides_step():
    """Explicit model=/thinking= arguments override the step's resolved values."""
    cfg = mr.step_config("personas.pass_7pre_extract")  # sonnet-4.6, thinking off
    client = _mock_client_for_create()
    with patch("anthropic.Anthropic", return_value=client):
        call_claude(step=cfg, system="sys", user="usr", model="claude-opus-4-7",
                    max_tokens=100, temperature=0.0)
    kwargs = client.messages.create.call_args.kwargs
    assert kwargs["model"] == "claude-opus-4-7"


def test_neither_step_nor_model_raises():
    with pytest.raises(ValueError):
        call_claude(system="sys", user="usr")
