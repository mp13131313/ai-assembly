"""C49: Speaker ID JSON-decode auto-passthrough fallback.

`transcription_flow.py::identify_speakers` (Claude structured output, the
5-pass Speaker ID) occasionally returns malformed JSON on large-roster
sessions. The task already retries (see its `@task(retries=2, ...)`
decorator); these tests cover what happens after those retries are
exhausted:

  - A JSON decode failure degrades gracefully: `process_session` writes an
    all-"Unidentified Speaker N" mapping (preserving the out_01 diarization
    label boundaries — one number per LABEL, not per turn) and continues
    to Cleaning instead of halting the session. The degraded state is
    flagged in `flags`, which lands in session_package.json's
    `review_queue.diarization_flags`.
  - Any other failure (auth, network, ...) is NOT degraded — it still
    raises and halts the session, same as before this fix.

No real Anthropic/AssemblyAI calls are made: `Anthropic` is monkeypatched
at the transcription_flow module level, and Step 1 (AssemblyAI) + Step 4
(Cleaning) are bypassed (pre-seeded `out_01_diarized.json` / a stubbed
`clean_transcript`) so only the Speaker ID code path under test runs.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_RUNTIME = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_RUNTIME))

import flows.transcription_flow as tf  # noqa: E402


# --- Fixtures ----------------------------------------------------------

def _malformed_response() -> MagicMock:
    resp = MagicMock()
    resp.usage = MagicMock(input_tokens=1200, output_tokens=900)
    # Deliberately unparseable — no closing brace, trailing garbage.
    resp.content = [MagicMock(text='{"mappings": [ this is not valid json')]
    return resp


def _seed_session_dir(tmp_path: Path) -> tuple[Path, Path, list[dict]]:
    """Write audio placeholder + session.json + out_01_diarized.json.

    Returns (audio_path, session_path, turns). Turns use 3 distinct
    anonymous_labels in a deliberately non-alphabetical first-appearance
    order (b, a, c) so the fallback's numbering can be checked against
    *appearance* order rather than sort order.
    """
    audio_path = tmp_path / "audio.m4a"
    audio_path.write_bytes(b"fake-audio")

    session = {
        "session_id": "s1",
        "session_title": "Test Panel",
        "session_description": "A test panel",
        "session_format": "panel",
        "roster": [{"name": "Ada Lovelace", "affiliation": "Analytical Engine Co"}],
    }
    session_path = tmp_path / "session.json"
    session_path.write_text(json.dumps(session))

    label_sequence = ["speaker_b", "speaker_a", "speaker_c", "speaker_b", "speaker_a"]
    turns = [
        {
            "index": i,
            "anonymous_label": label,
            "start_ms": i * 1000,
            "end_ms": i * 1000 + 900,
            "text": f"turn {i} from {label}",
        }
        for i, label in enumerate(label_sequence)
    ]
    (tmp_path / "out_01_diarized.json").write_text(json.dumps(turns))

    return audio_path, session_path, turns


@pytest.fixture(autouse=True)
def _env(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test-fake")
    monkeypatch.setenv("ASSEMBLYAI_API_KEY", "aai-test-fake")
    monkeypatch.delenv("OUTPUT_DIR", raising=False)


# --- build_speaker_id_fallback (unit) -----------------------------------

class TestBuildSpeakerIdFallback:
    def test_shape_and_label_ordering(self):
        turns = [
            {"anonymous_label": "speaker_b", "text": "x"},
            {"anonymous_label": "speaker_a", "text": "y"},
            {"anonymous_label": "speaker_c", "text": "z"},
            {"anonymous_label": "speaker_b", "text": "w"},
        ]
        out = tf.build_speaker_id_fallback(turns, ValueError("boom"))

        assert set(out.keys()) == {"mappings", "flags"}
        assert [m["anonymous_label"] for m in out["mappings"]] == [
            "speaker_b", "speaker_a", "speaker_c",
        ]
        assert [m["identified_name"] for m in out["mappings"]] == [
            "Unidentified Speaker 1", "Unidentified Speaker 2", "Unidentified Speaker 3",
        ]
        for m in out["mappings"]:
            assert m["confidence"] == "low"
            assert m["role"] == "unknown"
            assert m["evidence"]

        assert len(out["flags"]) == 1
        flag = out["flags"][0]
        assert flag["type"] == "speaker_id_auto_passthrough"
        assert flag["labels"] == ["speaker_b", "speaker_a", "speaker_c"]
        assert "boom" in flag["note"]


# --- process_session integration ----------------------------------------

class TestProcessSessionSpeakerIdFallback:
    def test_decode_failure_falls_back_without_raising(self, tmp_path, monkeypatch):
        audio_path, session_path, turns = _seed_session_dir(tmp_path)

        fake_client = MagicMock()
        fake_client.messages.create.side_effect = lambda **kw: _malformed_response()
        monkeypatch.setattr(tf, "Anthropic", lambda *a, **kw: fake_client)
        # Avoid real retry sleeps (backoff_factor=5) without weakening the
        # retry count itself.
        monkeypatch.setattr(
            tf, "identify_speakers",
            tf.identify_speakers.with_options(retry_delay_seconds=0),
        )
        # Step 4 (Cleaning) is out of scope for this test — stub it so no
        # second Anthropic surface (streaming) needs mocking.
        monkeypatch.setattr(
            tf, "clean_transcript",
            lambda named_turns, session, vocab: named_turns,
        )

        result = tf.process_session(str(audio_path), str(session_path))

        # Retries exhausted: 1 initial + 2 retries = 3 calls.
        assert fake_client.messages.create.call_count == 3

        out02 = json.loads((tmp_path / "out_02_speaker_id.json").read_text())
        distinct_labels = ["speaker_b", "speaker_a", "speaker_c"]
        assert [m["anonymous_label"] for m in out02["mappings"]] == distinct_labels
        assert [m["identified_name"] for m in out02["mappings"]] == [
            "Unidentified Speaker 1", "Unidentified Speaker 2", "Unidentified Speaker 3",
        ]
        assert len(out02["flags"]) == 1
        assert out02["flags"][0]["type"] == "speaker_id_auto_passthrough"

        # Flag must be visible in the most-downstream-visible surface:
        # session_package.json's review_queue.diarization_flags.
        assert result["review_queue"]["diarization_flags"] == out02["flags"]

        # Session package still assembled — pipeline did not halt.
        session_package = json.loads((tmp_path / "session_package.json").read_text())
        assert session_package["review_queue"]["diarization_flags"][0]["type"] == (
            "speaker_id_auto_passthrough"
        )
        # merge_speaker_ids applied the fallback mapping consistently per
        # label (not per turn) — same label -> same Unidentified name.
        speakers_by_turn = [t["speaker"] for t in session_package["transcript"]["turns"]]
        assert speakers_by_turn == [
            "Unidentified Speaker 1",  # speaker_b (turn 0)
            "Unidentified Speaker 2",  # speaker_a (turn 1)
            "Unidentified Speaker 3",  # speaker_c (turn 2)
            "Unidentified Speaker 1",  # speaker_b (turn 3) — same as turn 0
            "Unidentified Speaker 2",  # speaker_a (turn 4) — same as turn 1
        ]

    def test_non_decode_error_still_raises(self, tmp_path, monkeypatch):
        audio_path, session_path, turns = _seed_session_dir(tmp_path)

        fake_client = MagicMock()
        fake_client.messages.create.side_effect = RuntimeError("simulated auth/network failure")
        monkeypatch.setattr(tf, "Anthropic", lambda *a, **kw: fake_client)
        monkeypatch.setattr(
            tf, "identify_speakers",
            tf.identify_speakers.with_options(retry_delay_seconds=0),
        )

        with pytest.raises(RuntimeError, match="simulated auth/network failure"):
            tf.process_session(str(audio_path), str(session_path))

        # No fallback written — the session halted as it did before C49.
        assert not (tmp_path / "out_02_speaker_id.json").exists()
        assert not (tmp_path / "session_package.json").exists()
