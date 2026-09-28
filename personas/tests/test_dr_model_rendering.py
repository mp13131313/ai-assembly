"""The claude.ai Deep Research preambles name the model from model_routing.json
(manual steps personas.dr_sections_1_5 / personas.dr_section_6; voices
OPEN_ITEMS §36) — so changing the file changes what the operator is told to pick.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

_PERSONAS_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PERSONAS_ROOT))

from flows.shared import model_routing as mr  # noqa: E402
from scripts.split_tailored_prompt import wrap_section  # noqa: E402

_VOICE_CONFIG = {"name": "Test Voice", "type": "human", "subtype": None,
                 "voice_mode": "philosophical", "corpus_constraint": "full",
                 "hostile_sources": False}
_PROMPTS = _PERSONAS_ROOT / "flows" / "shared" / "prompts"


def _preamble(section_index: int) -> str:
    text = wrap_section(f"## Section {section_index}\n\nContent.\n", section_index=section_index,
                        slug="test_voice", voice_config=_VOICE_CONFIG, wikipedia_url=None)
    return text.split("---", 1)[0]  # the operator instructions above the first rule


def _display(step: str) -> str:
    return mr.model_display_name(mr.step_config(step).model)


def test_sections_name_the_configured_models():
    s15 = _display("personas.dr_sections_1_5")
    assert s15 in _preamble(1)
    assert s15 in _preamble(3)
    assert _display("personas.dr_section_6") in _preamble(6)


def test_changing_the_config_changes_the_instructions(tmp_path, monkeypatch):
    base = json.loads(mr.CONFIG_PATH.read_text(encoding="utf-8"))
    base["steps"]["personas.dr_sections_1_5"]["model"] = "claude-sonnet-4-6"
    p = tmp_path / "model_routing.json"
    p.write_text(json.dumps(base))
    monkeypatch.setattr(mr, "CONFIG_PATH", p)

    assert "Claude Sonnet 4.6" in _preamble(1)


def test_no_model_names_written_into_the_dr_instructions():
    header = (_PROMPTS / "pass_0b_header.md").read_text(encoding="utf-8")
    pass_0a = (_PROMPTS / "pass_0a_voice_config.md").read_text(encoding="utf-8")
    to_proceed = pass_0a[pass_0a.index("## To proceed"):]
    pattern = re.compile(r"\b(Opus|Sonnet|Haiku)\s+\d")
    assert not pattern.search(header), "pass_0b_header.md names a model — use model_name(step)"
    assert not pattern.search(to_proceed[:1500]), "Pass 0a's 'To proceed' names a model"
