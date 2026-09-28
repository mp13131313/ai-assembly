"""model_routing.json + flows/shared/model_routing.py — the per-step model config."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_RUNTIME = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_RUNTIME))

from flows.shared import model_routing as mr  # noqa: E402

OPUS, SONNET = "claude-opus-4-7", "claude-sonnet-4-6"
LADDER = ("gpt-5.4", "gpt-4.1", "o3", "gpt-4o", "gemini-2.5-pro")

# What production actually ran on 2026-09-28 (docs/LLM_CALL_INVENTORY.md §1,
# env vars unset). Changing a default is a deliberate act: update this table
# in the same commit.
GOLDEN = {
    "runtime.transcription.asr": ("universal-3-pro", None),
    "runtime.transcription.speaker_id": (SONNET, "off"),
    "runtime.transcription.cleaning": (SONNET, "off"),
    "runtime.researcher.extraction": (OPUS, "adaptive"),
    "runtime.researcher.clustering": (OPUS, "adaptive"),
    "runtime.researcher.theming": (OPUS, "adaptive"),
    "runtime.provocateur.triage_voice": (OPUS, "adaptive"),
    "runtime.provocateur.triage_flags": (OPUS, "adaptive"),
    "runtime.provocateur.formulation": (OPUS, "adaptive"),
    "runtime.voice.step1": (OPUS, "adaptive"),
    "runtime.voice.step2": (OPUS, "adaptive"),
    "runtime.voice.step3": (OPUS, "adaptive"),
    "runtime.voice.continuity": (SONNET, "adaptive"),
    "runtime.voice.step1_validation": ("gpt-5.4", None),
    "runtime.voice.step2_validation": (SONNET, "off"),
    "runtime.synthesis_router": (SONNET, "off"),
    "runtime.editor.dossier": (OPUS, "adaptive"),
    "personas.pass_0a_voice_config": (OPUS, "adaptive"),
    "personas.pass_0b_tailor": (OPUS, "adaptive"),
    "personas.dr_sections_1_5": (OPUS, None),   # manual (claude.ai Deep Research)
    "personas.dr_section_6": (OPUS, None),      # manual
    "personas.pass_1a_perplexity": ("sonar-deep-research", None),
    "personas.pass_1b_gemini": ("gemini-2.5-pro", None),
    "personas.pass_1_merge": (OPUS, "adaptive"),
    "personas.pass_1_7_coherence": (OPUS, "adaptive"),
    "personas.pass_1d_excerpts": (OPUS, "adaptive"),
    "personas.pass_2": (OPUS, "adaptive"),
    "personas.pass_3": (OPUS, "adaptive"),
    "personas.pass_4a": (OPUS, "adaptive"),
    "personas.pass_4b": (OPUS, "adaptive"),
    "personas.pass_5": (OPUS, "adaptive"),
    "personas.pass_6": (OPUS, "adaptive"),
    "personas.ct_compress": (SONNET, "adaptive"),
    "personas.pass_7pre_extract": (SONNET, "off"),
    "personas.pass_7pre_verify": (SONNET, "off"),
    "personas.pass_7pre_boddice": (SONNET, "off"),
    "personas.pass_7_anachronism": ("gpt-5.4", None),
    "personas.pass_7a": ("gpt-5.4", None),
    "personas.pass_7a_fix": (OPUS, "adaptive"),
    "personas.pass_7a_final": ("gpt-5.4", None),
    "personas.pass_7b": (OPUS, "adaptive"),
    "personas.pass_7c": ("gemini-2.5-pro", None),
    "personas.derive": (OPUS, "adaptive"),
}

LEGACY_ENV = sorted(
    {n for names in mr._MODEL_ENV.values() for n in names}
    | set(mr._THINKING_ENV.values()) | set(mr._LADDER_ENV.values())
)


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch):
    for name in LEGACY_ENV:
        monkeypatch.delenv(name, raising=False)


def _config(tmp_path: Path, steps: dict, models: dict | None = None) -> Path:
    base = json.loads(mr.CONFIG_PATH.read_text(encoding="utf-8"))
    p = tmp_path / "model_routing.json"
    p.write_text(json.dumps({"models": models or base["models"], "steps": steps}))
    return p


# --- the shipped file ---------------------------------------------------

def test_shipped_defaults_match_production():
    steps = mr.all_steps()
    assert {s: (c.model, c.thinking) for s, c in steps.items()} == GOLDEN


def test_no_step_sends_effort_by_default():
    assert all(c.effort is None for c in mr.all_steps().values())


def test_ladders_and_fallback():
    assert mr.step_config("personas.pass_7a").ladder == LADDER
    fb = mr.step_config("personas.pass_7c").fallback
    assert (fb.model, fb.thinking) == (SONNET, "off")


def test_sampling_params_flags():
    assert mr.step_config("personas.pass_7pre_verify").sampling_params is True   # Sonnet 4.6
    assert mr.step_config("runtime.voice.step1").sampling_params is False        # Opus 4.7


def test_unknown_step_raises():
    with pytest.raises(mr.ModelRoutingError):
        mr.step_config("runtime.nope")


def test_personas_copy_is_identical():
    twin = _RUNTIME.parent / "personas" / "flows" / "shared" / "model_routing.py"
    assert twin.read_bytes() == Path(mr.__file__).read_bytes()


# --- legacy env overrides ----------------------------------------------

def test_step_env_beats_file(monkeypatch):
    monkeypatch.setenv("RESEARCHER_CLAUDE_MODEL", SONNET)
    assert mr.step_config("runtime.researcher.clustering").model == SONNET


def test_claude_model_applies_only_where_it_did(monkeypatch):
    monkeypatch.setenv("CLAUDE_MODEL", SONNET)
    assert mr.step_config("runtime.researcher.extraction").model == SONNET
    assert mr.step_config("runtime.editor.dossier").model == SONNET
    assert mr.step_config("personas.pass_2").model == OPUS          # never honored it


def test_speaker_id_falls_through_transcription_claude_model(monkeypatch):
    # C67 #1: on main, Speaker ID fell back to TRANSCRIPTION_CLAUDE_MODEL (via
    # the module's shared CLAUDE_MODEL) before CLAUDE_MODEL itself. The branch
    # chain dropped that middle rung — restore it.
    monkeypatch.setenv("TRANSCRIPTION_CLAUDE_MODEL", OPUS)
    assert mr.step_config("runtime.transcription.speaker_id").model == OPUS
    assert mr.step_config("runtime.transcription.cleaning").model == OPUS
    monkeypatch.setenv("TRANSCRIPTION_SPEAKER_ID_MODEL", SONNET)
    assert mr.step_config("runtime.transcription.speaker_id").model == SONNET   # most specific wins
    assert mr.step_config("runtime.transcription.cleaning").model == OPUS       # unaffected


def test_empty_env_counts_as_unset(monkeypatch):
    monkeypatch.setenv("VOICE_MODEL", "")
    assert mr.step_config("runtime.voice.step2").model == OPUS


def test_thinking_env(monkeypatch):
    monkeypatch.setenv("PROVOCATEUR_THINKING", "0")
    assert mr.step_config("runtime.provocateur.formulation").thinking == "off"
    monkeypatch.setenv("PROVOCATEUR_THINKING", "1")
    assert mr.step_config("runtime.provocateur.formulation").thinking == "adaptive"


def test_ladder_env(monkeypatch):
    monkeypatch.setenv("VOICE_VALIDATION_MODELS", "gpt-4o, gemini-2.5-pro")
    cfg = mr.step_config("runtime.voice.step1_validation")
    assert cfg.ladder == ("gpt-4o", "gemini-2.5-pro") and cfg.model == "gpt-4o"


def test_empty_ladder_env_raises(monkeypatch):
    monkeypatch.setenv("VOICE_VALIDATION_MODELS", ",")
    with pytest.raises(mr.ModelRoutingError, match="empty model list"):
        mr.step_config("runtime.voice.step1_validation")


def test_model_vendor():
    assert mr.model_vendor(OPUS) == "anthropic"
    assert mr.model_vendor("gemini-2.5-pro") == "google"
    with pytest.raises(mr.ModelRoutingError, match="not listed"):
        mr.model_vendor("claude-made-up-9")


def test_ladder_rung_must_be_openai_or_google(tmp_path, monkeypatch):
    p = _config(tmp_path, {"s": {"model": "gpt-5.4", "ladder": ["gpt-5.4", SONNET]}})
    with pytest.raises(mr.ModelRoutingError, match="cross-model"):
        mr.step_config("s", path=p)
    monkeypatch.setenv("VOICE_VALIDATION_MODELS", f"gpt-4o,{OPUS}")  # env path too
    with pytest.raises(mr.ModelRoutingError, match="cross-model"):
        mr.step_config("runtime.voice.step1_validation")


def test_manual_steps_skip_api_rules(tmp_path):
    # A manual step is instructions for a person: Opus 5.5 without an explicit
    # effort would be refused for an API step, but is fine here.
    p = _config(tmp_path, {"personas.dr_extra": {"model": "claude-opus-5-5", "manual": True}})
    cfg = mr.step_config("personas.dr_extra", path=p)
    assert cfg.manual and cfg.thinking is None
    assert mr.step_config("personas.dr_section_6").manual
    assert not mr.step_config("personas.pass_2").manual


def test_manual_refused_outside_dr_steps(tmp_path):
    # "manual": true skips the thinking/effort safety rules below — only
    # personas.dr_* (claude.ai Deep Research, done by the operator) may use it.
    p = _config(tmp_path, {"runtime.voice.step1": {"model": OPUS, "manual": True}})
    with pytest.raises(mr.ModelRoutingError, match="personas.dr_"):
        mr.step_config("runtime.voice.step1", path=p)


def test_model_display_name():
    assert mr.model_display_name(OPUS) == "Claude Opus 4.7"
    assert mr.model_display_name("gpt-5.4") == "gpt-5.4"   # no display_name → id


def test_env_to_unknown_model_raises(monkeypatch):
    monkeypatch.setenv("EDITOR_MODEL", "claude-made-up-9")
    with pytest.raises(mr.ModelRoutingError, match="not listed"):
        mr.step_config("runtime.editor.dossier")


# --- safety rules ------------------------------------------------------

def test_thinking_off_on_model_that_cannot_disable(tmp_path):
    p = _config(tmp_path, {"s": {"model": "claude-opus-5-5", "thinking": "off", "effort": "low"}})
    with pytest.raises(mr.ModelRoutingError, match="cannot run with thinking off"):
        mr.step_config("s", path=p)


def test_lower_default_effort_must_be_explicit(tmp_path):
    p = _config(tmp_path, {"s": {"model": "claude-opus-5-5", "thinking": "adaptive", "effort": None}})
    with pytest.raises(mr.ModelRoutingError, match="set effort explicitly"):
        mr.step_config("s", path=p)
    (tmp_path / "ok").mkdir()
    ok = _config(tmp_path / "ok", {"s": {"model": "claude-opus-5-5", "thinking": "adaptive", "effort": "high"}})
    cfg = mr.step_config("s", path=ok)
    assert cfg.output_config_kwargs() == {"output_config": {"effort": "high"}}


def test_bad_effort_value(tmp_path):
    p = _config(tmp_path, {"s": {"model": SONNET, "thinking": "off", "effort": "extreme"}})
    with pytest.raises(mr.ModelRoutingError, match="effort must be"):
        mr.step_config("s", path=p)


def test_whole_file_validated_on_load(tmp_path):
    p = _config(tmp_path, {
        "good": {"model": SONNET, "thinking": "off", "effort": None},
        "bad": {"model": "claude-opus-5-5", "thinking": "off", "effort": "low"},
    })
    with pytest.raises(mr.ModelRoutingError):
        mr.step_config("good", path=p)
