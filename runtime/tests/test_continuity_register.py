"""C20a: cross-night signature_moves_deployed register.

Tests the continuity overlay's new register field (per-voice, accumulated
across nights), the cross-night merge in continuity.py, and Step 2's
prompt-rendering of the register via card_assembly.

The Anthropic call inside generate_continuity is mocked — we test the
wrapper's parse-and-merge logic, not the model's output.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

_RUNTIME = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_RUNTIME))

from flows.shared.io import write_json_atomic  # noqa: E402
from flows.voice.card_assembly import (  # noqa: E402
    _render_continuity,
    load_persona_card,
)
from flows.voice.continuity import generate_continuity  # noqa: E402


# --- Renderer (pure, no I/O) ------------------------------------------

def _move(summary: str, where: str, quote: str = "") -> dict:
    return {"move_summary": summary, "where_used": where, "short_quote": quote}


class TestRenderContinuityRegister:
    def test_night_1_returns_empty(self):
        card = {"signature_moves_deployed": [_move("X", "night_1")]}
        assert _render_continuity(card, night=1, step=2) == ""

    def test_step_1_does_not_render_register(self):
        card = {"signature_moves_deployed": [_move("X", "night_1", "x quote")]}
        out = _render_continuity(card, night=2, step=1)
        assert "MOVES YOU HAVE ALREADY DEPLOYED" not in out

    def test_step_3_does_not_render_register(self):
        card = {"signature_moves_deployed": [_move("X", "night_1", "x quote")]}
        out = _render_continuity(card, night=2, step=3)
        assert "MOVES YOU HAVE ALREADY DEPLOYED" not in out

    def test_step_2_night_2_renders_register(self):
        card = {
            "signature_moves_deployed": [
                _move("Theuth/Thamus reach", "night_1", "the script cannot defend itself"),
            ]
        }
        out = _render_continuity(card, night=2, step=2)
        assert "MOVES YOU HAVE ALREADY DEPLOYED THIS CONFERENCE" in out
        assert "Theuth/Thamus reach" in out
        assert "night_1" in out
        assert "the script cannot defend itself" in out

    def test_step_2_night_3_renders_full_register(self):
        card = {
            "signature_moves_deployed": [
                _move("Theuth/Thamus", "night_1", "q1"),
                _move("Stranger from Elea interrupting", "night_2", "q2"),
            ]
        }
        out = _render_continuity(card, night=3, step=2)
        assert "Theuth/Thamus" in out
        assert "Stranger from Elea interrupting" in out
        assert "night_1" in out
        assert "night_2" in out

    def test_empty_register_renders_no_section(self):
        card = {"signature_moves_deployed": []}
        out = _render_continuity(card, night=2, step=2)
        assert "MOVES YOU HAVE ALREADY DEPLOYED" not in out

    def test_missing_register_renders_no_section(self):
        card = {}  # no signature_moves_deployed at all
        out = _render_continuity(card, night=2, step=2)
        assert "MOVES YOU HAVE ALREADY DEPLOYED" not in out

    def test_quote_is_optional(self):
        card = {"signature_moves_deployed": [_move("X", "night_1", "")]}
        out = _render_continuity(card, night=2, step=2)
        assert "X" in out
        # Smart-quoted dash with empty quote should not render the quote line.
        assert "“”" not in out and "“ ”" not in out

    def test_non_dict_entry_skipped(self):
        # Defensive: bad entry shape doesn't break rendering.
        card = {"signature_moves_deployed": [_move("Good", "night_1"), "bad"]}
        out = _render_continuity(card, night=2, step=2)
        assert "Good" in out
        assert "bad" not in out


# --- load_persona_card carries register through override --------------

class TestLoadPersonaCardCarriesRegister:
    def test_register_in_override_lands_on_card(self, tmp_path):
        voices_dir = tmp_path / "voices" / "plato"
        voices_dir.mkdir(parents=True)
        write_json_atomic(
            voices_dir / "07_persona_card_assembled.json",
            {"council_member_name": "Plato"},
        )
        write_json_atomic(
            voices_dir / "continuity_night_2.json",
            {
                "voice_slug": "plato",
                "from_night": 1,
                "for_night": 2,
                "continuity_block_if_night_2": "I argued...",
                "continuity_block_artifact_if_night_2": "I wrote a dialogue...",
                "signature_moves_deployed": [_move("X", "night_1", "q")],
            },
        )
        card = load_persona_card("plato", night=2, project_root=tmp_path)
        assert card.get("signature_moves_deployed") == [_move("X", "night_1", "q")]

    def test_no_override_no_register(self, tmp_path):
        voices_dir = tmp_path / "voices" / "plato"
        voices_dir.mkdir(parents=True)
        write_json_atomic(
            voices_dir / "07_persona_card_assembled.json",
            {"council_member_name": "Plato"},
        )
        # No continuity file; register simply absent.
        card = load_persona_card("plato", night=2, project_root=tmp_path)
        assert "signature_moves_deployed" not in card

    def test_night_1_does_not_load_register(self, tmp_path):
        voices_dir = tmp_path / "voices" / "plato"
        voices_dir.mkdir(parents=True)
        write_json_atomic(
            voices_dir / "07_persona_card_assembled.json",
            {"council_member_name": "Plato"},
        )
        # Even if a stray continuity_night_1.json existed, Night 1 path
        # never reads it.
        card = load_persona_card("plato", night=1, project_root=tmp_path)
        assert "signature_moves_deployed" not in card


# --- Cross-night merge in generate_continuity --------------------------

def _mock_anthropic_response(parsed_json: dict, *, input_tokens: int = 100, output_tokens: int = 50):
    """Build a mock final.usage object compatible with continuity.py's
    accounting reads."""
    usage = MagicMock()
    usage.input_tokens = input_tokens
    usage.output_tokens = output_tokens
    usage.cache_creation_input_tokens = 0
    usage.cache_read_input_tokens = 0
    final = MagicMock()
    final.usage = usage
    raw_text = json.dumps(parsed_json)
    return raw_text, "", final, 0


class TestCrossNightMerge:
    def _seed_voice(self, tmp_path: Path, voice_slug: str = "plato"):
        run_dir = tmp_path / "athens_night_1"
        s2 = run_dir / "04_voice" / "step2_first_draft_artifacts"
        s2.mkdir(parents=True)
        write_json_atomic(
            s2 / f"{voice_slug}.json",
            {
                "lineage": {"voice_slug": voice_slug, "night": 1},
                "council_member": "Plato",
                "focus_decision": "Focus on Response 1",
                "stance": "skeptical",
                "selected_form": "dialogue",
                "artifact_text": "body " * 30,
            },
        )
        return run_dir

    def test_night_2_merge_with_no_prior_uses_only_new_moves(self, tmp_path):
        run_dir = self._seed_voice(tmp_path)
        new_moves = [_move("Theuth/Thamus", "night_1", "q")]
        with patch("flows.voice.continuity.stream_voice_call") as mock_call:
            mock_call.return_value = _mock_anthropic_response({
                "continuity_block_if_night_2": "I argued...",
                "continuity_block_artifact_if_night_2": "I wrote...",
                "signature_moves_deployed_last_night": new_moves,
            })
            with patch("flows.voice.continuity.Anthropic"):
                out = generate_continuity(
                    voice_slug="plato",
                    night_just_completed=1,
                    run_dir=run_dir,
                    project_root=tmp_path,
                )
        assert out["signature_moves_deployed"] == new_moves

    def test_night_3_merge_carries_forward_night_1_register(self, tmp_path):
        # Seed Night 2's continuity file with Night 1's register already there.
        run_dir = tmp_path / "athens_night_2"
        s2 = run_dir / "04_voice" / "step2_first_draft_artifacts"
        s2.mkdir(parents=True)
        write_json_atomic(
            s2 / "plato.json",
            {
                "lineage": {"voice_slug": "plato", "night": 2},
                "council_member": "Plato",
                "focus_decision": "Focus on Response 2",
                "stance": "didactic",
                "selected_form": "dialogue",
                "artifact_text": "body " * 30,
            },
        )
        # Prior night's continuity (consumed BEFORE Night 2) carries Night 1's moves.
        voices_dir = tmp_path / "voices" / "plato"
        voices_dir.mkdir(parents=True)
        write_json_atomic(
            voices_dir / "continuity_night_2.json",
            {
                "voice_slug": "plato",
                "from_night": 1,
                "for_night": 2,
                "signature_moves_deployed": [_move("Theuth/Thamus", "night_1", "q1")],
            },
        )
        # Night 2's call returns ONLY Night 2's new moves.
        new_moves = [_move("Stranger from Elea", "night_2", "q2")]
        with patch("flows.voice.continuity.stream_voice_call") as mock_call:
            mock_call.return_value = _mock_anthropic_response({
                "continuity_block_if_night_3": "I argued...",
                "continuity_block_artifact_if_night_3": "I wrote...",
                "signature_moves_deployed_last_night": new_moves,
            })
            with patch("flows.voice.continuity.Anthropic"):
                out = generate_continuity(
                    voice_slug="plato",
                    night_just_completed=2,
                    run_dir=run_dir,
                    project_root=tmp_path,
                )
        # Result must carry Night 1's prior + Night 2's new (Night 3 will see both).
        assert out["signature_moves_deployed"] == [
            _move("Theuth/Thamus", "night_1", "q1"),
            _move("Stranger from Elea", "night_2", "q2"),
        ]

    def test_defensive_dict_wrapped_to_list(self, tmp_path):
        run_dir = self._seed_voice(tmp_path)
        # Model returns a single object instead of a list — wrapper coerces.
        with patch("flows.voice.continuity.stream_voice_call") as mock_call:
            mock_call.return_value = _mock_anthropic_response({
                "continuity_block_if_night_2": "x",
                "continuity_block_artifact_if_night_2": "x",
                "signature_moves_deployed_last_night": _move("Solo", "night_1"),
            })
            with patch("flows.voice.continuity.Anthropic"):
                out = generate_continuity(
                    voice_slug="plato",
                    night_just_completed=1,
                    run_dir=run_dir,
                    project_root=tmp_path,
                )
        assert out["signature_moves_deployed"] == [_move("Solo", "night_1")]

    def test_defensive_garbage_dropped(self, tmp_path):
        run_dir = self._seed_voice(tmp_path)
        # Model returns a string — wrapper drops to empty list.
        with patch("flows.voice.continuity.stream_voice_call") as mock_call:
            mock_call.return_value = _mock_anthropic_response({
                "continuity_block_if_night_2": "x",
                "continuity_block_artifact_if_night_2": "x",
                "signature_moves_deployed_last_night": "garbage",
            })
            with patch("flows.voice.continuity.Anthropic"):
                out = generate_continuity(
                    voice_slug="plato",
                    night_just_completed=1,
                    run_dir=run_dir,
                    project_root=tmp_path,
                )
        assert out["signature_moves_deployed"] == []

    def test_missing_register_field_returns_empty_list(self, tmp_path):
        run_dir = self._seed_voice(tmp_path)
        with patch("flows.voice.continuity.stream_voice_call") as mock_call:
            mock_call.return_value = _mock_anthropic_response({
                "continuity_block_if_night_2": "x",
                "continuity_block_artifact_if_night_2": "x",
                # signature_moves_deployed_last_night absent
            })
            with patch("flows.voice.continuity.Anthropic"):
                out = generate_continuity(
                    voice_slug="plato",
                    night_just_completed=1,
                    run_dir=run_dir,
                    project_root=tmp_path,
                )
        assert out["signature_moves_deployed"] == []
