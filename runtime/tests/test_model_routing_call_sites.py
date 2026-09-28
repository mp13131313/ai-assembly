"""Model-routing wiring tests for every runtime LLM call site.

Companion to test_model_routing.py (which tests model_routing.py /
model_routing.json in isolation). These tests verify the OTHER half of
the contract: that each call site in runtime/flows actually asks
step_config() for its own step, sends the resulting model (and thinking
on/off) to the client, and that legacy env var overrides still change
the outcome — with no real Anthropic/OpenAI/AssemblyAI/Gemini calls.

Two patterns, applied per call site:
  - direct: fake the client, run the real call-site code, inspect the
    kwargs the client received (transcription, researcher, provocateur,
    voice step1/2/3 + continuity + editor dossier, step1_validation
    ladder, step2_validation, synthesis_router).
  - a source-literal scan (TestNoHardcodedModelLiterals) enforcing that
    no runtime/flows module (other than shared/model_routing.py) hardcodes
    a model name outside a docstring/comment.

GOLDEN values are imported from test_model_routing.py so the two files
can't silently drift apart.
"""
from __future__ import annotations

import ast
import json
import re
import sys
import types
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_RUNTIME = Path(__file__).resolve().parent.parent
if str(_RUNTIME) not in sys.path:
    sys.path.insert(0, str(_RUNTIME))

from flows.shared import model_routing as mr  # noqa: E402
from flows.shared.io import write_json_atomic  # noqa: E402
from tests.test_model_routing import GOLDEN, OPUS, SONNET, LADDER  # noqa: E402

FLOWS_ROOT = _RUNTIME / "flows"
MODEL_ROUTING_PY = FLOWS_ROOT / "shared" / "model_routing.py"


# --- Shared env isolation (mirrors test_model_routing.py) -----------------

LEGACY_ENV = sorted(
    {n for names in mr._MODEL_ENV.values() for n in names}
    | set(mr._THINKING_ENV.values()) | set(mr._LADDER_ENV.values())
)


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch):
    for name in LEGACY_ENV:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test-fake")


# ===========================================================================
# 1. Source scan — no hardcoded model literals outside model_routing.py
# ===========================================================================

_LITERAL_PATTERNS = [
    re.compile(r"claude-(opus|sonnet|haiku|fable)-"),
    re.compile(r"gpt-"),
    re.compile(r"gemini-"),
    re.compile(r"\bo3\b"),
    re.compile(r"universal-3-pro"),
]
_ALLOW_MARKER = "model-scan: allow"


def _docstring_node_ids(tree: ast.AST) -> set[int]:
    """id()s of Constant nodes that are module/function/class docstrings."""
    ids: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            body = getattr(node, "body", [])
            if body and isinstance(body[0], ast.Expr):
                val = body[0].value
                if isinstance(val, ast.Constant) and isinstance(val.value, str):
                    ids.add(id(val))
    return ids


def _scan_file_for_model_literals(path: Path) -> list[tuple[int, str]]:
    """Return [(lineno, snippet), ...] for hardcoded model literals in
    real code (not docstrings, not lines carrying the allow marker)."""
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    skip_ids = _docstring_node_ids(tree)
    source_lines = source.splitlines()
    violations: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Constant) and isinstance(node.value, str)):
            continue
        if id(node) in skip_ids:
            continue
        if not any(p.search(node.value) for p in _LITERAL_PATTERNS):
            continue
        lineno = getattr(node, "lineno", 0)
        line_text = source_lines[lineno - 1] if 0 < lineno <= len(source_lines) else ""
        if _ALLOW_MARKER in line_text:
            continue
        violations.append((lineno, node.value[:80]))
    return violations


class TestNoHardcodedModelLiterals:
    def test_no_flows_module_hardcodes_a_model(self):
        offenders: list[str] = []
        for path in sorted(FLOWS_ROOT.rglob("*.py")):
            if path.resolve() == MODEL_ROUTING_PY.resolve():
                continue
            for lineno, snippet in _scan_file_for_model_literals(path):
                offenders.append(f"{path.relative_to(_RUNTIME)}:{lineno}: {snippet!r}")
        assert not offenders, (
            "Hardcoded model literal(s) found outside flows/shared/model_routing.py "
            "— route through step_config() instead:\n" + "\n".join(offenders)
        )


# ===========================================================================
# Fake-client helpers
# ===========================================================================

class _FakeMessageStream:
    """Mimics the `with client.messages.stream(...) as stream:` protocol.

    Two call-site shapes exist in this repo: `voice/_anthropic_call.
    stream_voice_call` reassembles text from `final.content` blocks
    (ignoring `stream.text_stream` other than draining it), while
    researcher/provocateur/transcription-cleaning build the text
    directly from `stream.text_stream`. This fake serves both by
    streaming the same text `final.content` carries.
    """

    def __init__(self, final, text: str):
        self._final = final
        self._text = text

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    @property
    def text_stream(self):
        return iter([self._text])

    def get_final_message(self):
        return self._final


def _final_message(text: str = "OK") -> MagicMock:
    final = MagicMock()
    final.content = [MagicMock(type="text", text=text)]
    final.usage = MagicMock(
        input_tokens=10, output_tokens=5,
        cache_creation_input_tokens=0, cache_read_input_tokens=0,
    )
    return final


def _make_stream_client(text: str = "OK") -> MagicMock:
    """A fake Anthropic client whose .messages.stream(...) is inspectable
    via client.messages.stream.call_args, and whose .messages.create(...)
    is inspectable via client.messages.create.call_args."""
    final = _final_message(text)
    client = MagicMock()
    client.messages.stream = MagicMock(side_effect=lambda **kw: _FakeMessageStream(final, text))
    client.messages.create = MagicMock(return_value=final)
    client.messages.count_tokens = MagicMock(return_value=MagicMock(input_tokens=1))
    return client


def _stream_kwargs(client: MagicMock) -> dict:
    return client.messages.stream.call_args.kwargs


def _create_kwargs(client: MagicMock) -> dict:
    return client.messages.create.call_args.kwargs


# ===========================================================================
# 2. Transcription — runtime.transcription.{asr,speaker_id,cleaning}
# ===========================================================================

import flows.transcription_flow as tf  # noqa: E402


class TestTranscriptionASR:
    def test_asr_model_matches_golden_and_has_no_env_override(self, monkeypatch):
        expected_model, expected_thinking = GOLDEN["runtime.transcription.asr"]
        assert expected_thinking is None  # non-Anthropic step

        captured: dict[str, object] = {}

        class _FakeConfig:
            def __init__(self, **kwargs):
                self.raw = types.SimpleNamespace()

        class _FakeTranscript:
            status = "completed"
            utterances: list = []

        class _FakeTranscriber:
            def __init__(self, config):
                captured["config"] = config

            def transcribe(self, path):
                return _FakeTranscript()

        monkeypatch.setenv("ASSEMBLYAI_API_KEY", "aai-test-fake")
        monkeypatch.setattr(tf.aai, "TranscriptionConfig", _FakeConfig)
        monkeypatch.setattr(tf.aai, "Transcriber", _FakeTranscriber)

        session = {"roster": []}
        tf.transcribe_with_assemblyai.fn(Path("audio.m4a"), session)

        assert captured["config"].raw.speech_models == [expected_model]


class TestTranscriptionSpeakerID:
    def _turns(self):
        return [{"index": 0, "anonymous_label": "speaker_a", "text": "hi"}]

    def _session(self):
        return {"session_title": "T", "session_format": "panel",
                "session_description": "", "roster": []}

    def test_matches_golden_with_env_unset(self, monkeypatch):
        expected_model, expected_thinking = GOLDEN["runtime.transcription.speaker_id"]
        client = _make_stream_client('{"mappings": [], "flags": []}')
        client.messages.create = MagicMock(return_value=_final_message(
            '{"mappings": [], "flags": []}'
        ))
        monkeypatch.setattr(tf, "Anthropic", lambda *a, **kw: client)

        tf.identify_speakers.fn(self._turns(), self._session())

        kwargs = client.messages.create.call_args.kwargs
        assert kwargs["model"] == expected_model
        assert ("thinking" in kwargs) == (expected_thinking == "adaptive")

    def test_env_override_changes_model(self, monkeypatch):
        client = _make_stream_client()
        client.messages.create = MagicMock(return_value=_final_message(
            '{"mappings": [], "flags": []}'
        ))
        monkeypatch.setattr(tf, "Anthropic", lambda *a, **kw: client)
        monkeypatch.setenv("TRANSCRIPTION_SPEAKER_ID_MODEL", OPUS)

        tf.identify_speakers.fn(self._turns(), self._session())

        assert client.messages.create.call_args.kwargs["model"] == OPUS


class TestTranscriptionCleaning:
    def test_matches_golden_with_env_unset(self, monkeypatch):
        expected_model, expected_thinking = GOLDEN["runtime.transcription.cleaning"]
        client = _make_stream_client("[]")
        monkeypatch.setattr(tf, "Anthropic", lambda *a, **kw: client)

        tf.clean_transcript.fn([{"speaker": "A", "confidence": "high", "text": "hi"}],
                                {"session_title": "T", "session_description": ""}, [])

        kwargs = _stream_kwargs(client)
        assert kwargs["model"] == expected_model
        assert ("thinking" in kwargs) == (expected_thinking == "adaptive")

    def test_env_override_changes_model(self, monkeypatch):
        client = _make_stream_client("[]")
        monkeypatch.setattr(tf, "Anthropic", lambda *a, **kw: client)
        monkeypatch.setenv("TRANSCRIPTION_CLAUDE_MODEL", OPUS)

        tf.clean_transcript.fn([{"speaker": "A", "confidence": "high", "text": "hi"}],
                                {"session_title": "T", "session_description": ""}, [])

        assert _stream_kwargs(client)["model"] == OPUS


# ===========================================================================
# 3. Researcher — extraction / clustering / theming
# ===========================================================================

import flows.researcher_flow as rf  # noqa: E402


class TestResearcherExtraction:
    def _pkg_path(self, tmp_path: Path) -> Path:
        p = tmp_path / "s1" / "session_package.json"
        p.parent.mkdir(parents=True, exist_ok=True)
        write_json_atomic(p, {
            "metadata": {"session_title": "T", "session_description": "", "roster": []},
            "transcript": {"speakers_present": [], "turns": []},
            "review_queue": {"verify_markers": []},
        })
        return p

    def test_matches_golden_with_env_unset(self, tmp_path, monkeypatch):
        expected_model, expected_thinking = GOLDEN["runtime.researcher.extraction"]
        client = _make_stream_client("[]")
        monkeypatch.setattr(rf, "Anthropic", lambda *a, **kw: client)

        rf.extract_session.fn(str(self._pkg_path(tmp_path)))

        kwargs = _stream_kwargs(client)
        assert kwargs["model"] == expected_model
        assert ("thinking" in kwargs) == (expected_thinking == "adaptive")

    def test_env_override_changes_model_and_thinking(self, tmp_path, monkeypatch):
        client = _make_stream_client("[]")
        monkeypatch.setattr(rf, "Anthropic", lambda *a, **kw: client)
        monkeypatch.setenv("RESEARCHER_CLAUDE_MODEL", SONNET)
        monkeypatch.setenv("RESEARCHER_THINKING", "0")

        rf.extract_session.fn(str(self._pkg_path(tmp_path)))

        kwargs = _stream_kwargs(client)
        assert kwargs["model"] == SONNET
        assert "thinking" not in kwargs


class TestResearcherClustering:
    def test_matches_golden_with_env_unset(self, monkeypatch):
        expected_model, expected_thinking = GOLDEN["runtime.researcher.clustering"]
        client = _make_stream_client('{"clusters": [], "isolates": []}')
        monkeypatch.setattr(rf, "Anthropic", lambda *a, **kw: client)

        rf.cluster_extractions.fn([{"id": "s1:001", "extraction": "x", "context": ""}])

        kwargs = _stream_kwargs(client)
        assert kwargs["model"] == expected_model
        assert ("thinking" in kwargs) == (expected_thinking == "adaptive")

    def test_env_override_changes_model(self, monkeypatch):
        client = _make_stream_client('{"clusters": [], "isolates": []}')
        monkeypatch.setattr(rf, "Anthropic", lambda *a, **kw: client)
        monkeypatch.setenv("CLAUDE_MODEL", SONNET)

        rf.cluster_extractions.fn([{"id": "s1:001", "extraction": "x", "context": ""}])

        assert _stream_kwargs(client)["model"] == SONNET


class TestResearcherTheming:
    def test_matches_golden_with_env_unset(self, monkeypatch):
        expected_model, expected_thinking = GOLDEN["runtime.researcher.theming"]
        client = _make_stream_client('{"themes": []}')
        monkeypatch.setattr(rf, "Anthropic", lambda *a, **kw: client)

        rf.group_clusters_into_themes.fn({"clusters": []})

        kwargs = _stream_kwargs(client)
        assert kwargs["model"] == expected_model
        assert ("thinking" in kwargs) == (expected_thinking == "adaptive")

    def test_env_override_changes_model(self, monkeypatch):
        client = _make_stream_client('{"themes": []}')
        monkeypatch.setattr(rf, "Anthropic", lambda *a, **kw: client)
        monkeypatch.setenv("RESEARCHER_CLAUDE_MODEL", SONNET)

        rf.group_clusters_into_themes.fn({"clusters": []})

        assert _stream_kwargs(client)["model"] == SONNET


# ===========================================================================
# 4. Provocateur — triage_voice / triage_flags / formulation
# ===========================================================================

import flows.provocateur_flow as pf  # noqa: E402

_PV_MEMBER = {
    "name": "Plato", "speaks_from": "x", "core_commitment": "x",
    "activates_on": "x", "goes_flat_on": "x", "stretch": "x",
    "translation_range": "x", "stance_tendency": "x", "medium": "x",
}
_PV_COUNCIL = {
    "version": "v1", "collective_landscape": "L", "audience": "A",
    "members": [_PV_MEMBER],
}
_PV_THEMES = [{"theme_id": "theme_001", "title": "T", "abstract": "A", "clusters": []}]


class TestProvocateurTriageVoice:
    def test_matches_golden_with_env_unset(self, monkeypatch):
        expected_model, expected_thinking = GOLDEN["runtime.provocateur.triage_voice"]
        client = _make_stream_client("{}")
        monkeypatch.setattr(pf, "Anthropic", lambda *a, **kw: client)

        pf.triage_voice.fn(_PV_MEMBER, _PV_THEMES, _PV_COUNCIL, out_dir=None)

        kwargs = _stream_kwargs(client)
        assert kwargs["model"] == expected_model
        assert ("thinking" in kwargs) == (expected_thinking == "adaptive")

    def test_env_override_changes_model(self, monkeypatch):
        client = _make_stream_client("{}")
        monkeypatch.setattr(pf, "Anthropic", lambda *a, **kw: client)
        monkeypatch.setenv("PROVOCATEUR_CLAUDE_MODEL", SONNET)

        pf.triage_voice.fn(_PV_MEMBER, _PV_THEMES, _PV_COUNCIL, out_dir=None)

        assert _stream_kwargs(client)["model"] == SONNET


class TestProvocateurTriageFlags:
    def test_matches_golden_with_env_unset(self, monkeypatch):
        expected_model, expected_thinking = GOLDEN["runtime.provocateur.triage_flags"]
        client = _make_stream_client("{}")
        monkeypatch.setattr(pf, "Anthropic", lambda *a, **kw: client)

        pf.triage_flags.fn(_PV_THEMES, _PV_COUNCIL)

        kwargs = _stream_kwargs(client)
        assert kwargs["model"] == expected_model
        assert ("thinking" in kwargs) == (expected_thinking == "adaptive")

    def test_env_override_changes_model(self, monkeypatch):
        client = _make_stream_client("{}")
        monkeypatch.setattr(pf, "Anthropic", lambda *a, **kw: client)
        monkeypatch.setenv("CLAUDE_MODEL", SONNET)

        pf.triage_flags.fn(_PV_THEMES, _PV_COUNCIL)

        assert _stream_kwargs(client)["model"] == SONNET


class TestProvocateurFormulation:
    def test_matches_golden_with_env_unset(self, monkeypatch):
        expected_model, expected_thinking = GOLDEN["runtime.provocateur.formulation"]
        client = _make_stream_client("{}")
        monkeypatch.setattr(pf, "Anthropic", lambda *a, **kw: client)

        pf.formulate_for_member.fn(
            _PV_THEMES[0], "Plato", {}, _PV_COUNCIL, theme_flags=None, out_dir=None,
        )

        kwargs = _stream_kwargs(client)
        assert kwargs["model"] == expected_model
        assert ("thinking" in kwargs) == (expected_thinking == "adaptive")

    def test_env_override_changes_model(self, monkeypatch):
        client = _make_stream_client("{}")
        monkeypatch.setattr(pf, "Anthropic", lambda *a, **kw: client)
        monkeypatch.setenv("PROVOCATEUR_CLAUDE_MODEL", SONNET)

        pf.formulate_for_member.fn(
            _PV_THEMES[0], "Plato", {}, _PV_COUNCIL, theme_flags=None, out_dir=None,
        )

        assert _stream_kwargs(client)["model"] == SONNET


# ===========================================================================
# 5. Voice Step 1 / Step 2 / Step 3 / Continuity + Editor dossier
#    (all funnel through voice/_anthropic_call.stream_voice_call)
# ===========================================================================

import flows.voice.step1_private_reasoning as v1  # noqa: E402
import flows.voice.step2_first_draft_artifact as v2  # noqa: E402
import flows.voice.step3_amended_artifact as v3  # noqa: E402
import flows.voice.continuity as vcont  # noqa: E402
import flows.editor.dossier_generation as edg  # noqa: E402


def _write_card(project_root: Path, slug: str = "plato") -> None:
    d = project_root / "voices" / slug
    d.mkdir(parents=True, exist_ok=True)
    write_json_atomic(d / "07_persona_card_assembled.json", {"council_member_name": "Plato"})


class TestVoiceStep1:
    def test_matches_golden_with_env_unset(self, tmp_path, monkeypatch):
        expected_model, expected_thinking = GOLDEN["runtime.voice.step1"]
        _write_card(tmp_path)
        client = _make_stream_client("some detailed response")
        monkeypatch.setattr(v1, "Anthropic", lambda *a, **kw: client)

        v1.run_step1_for_pair(
            "plato", {"theme_id": "theme_001"}, night=1,
            run_dir=tmp_path / "run", project_root=tmp_path,
        )

        kwargs = _stream_kwargs(client)
        assert kwargs["model"] == expected_model
        assert ("thinking" in kwargs) == (expected_thinking == "adaptive")

    def test_env_override_changes_model_and_thinking(self, tmp_path, monkeypatch):
        _write_card(tmp_path)
        client = _make_stream_client("some detailed response")
        monkeypatch.setattr(v1, "Anthropic", lambda *a, **kw: client)
        monkeypatch.setenv("VOICE_MODEL", SONNET)
        monkeypatch.setenv("VOICE_THINKING", "0")

        v1.run_step1_for_pair(
            "plato", {"theme_id": "theme_001"}, night=1,
            run_dir=tmp_path / "run", project_root=tmp_path,
        )

        kwargs = _stream_kwargs(client)
        assert kwargs["model"] == SONNET
        assert "thinking" not in kwargs


class TestVoiceStep2:
    def test_matches_golden_with_env_unset(self, tmp_path, monkeypatch):
        expected_model, expected_thinking = GOLDEN["runtime.voice.step2"]
        _write_card(tmp_path)
        client = _make_stream_client("weight_assessment: x\nartifact_text: body")
        monkeypatch.setattr(v2, "Anthropic", lambda *a, **kw: client)
        step1_outputs = [{
            "lineage": {"theme_id": "theme_001", "formulation_id": "f1",
                        "grounding_extraction_ids": [], "session_ids": []},
            "theme_display_title": "T", "mode": "question",
            "formulation_text": "F", "detailed_response": "D",
        }]

        v2.run_step2_for_voice(
            "plato", step1_outputs, night=1,
            run_dir=tmp_path / "run", project_root=tmp_path,
        )

        kwargs = _stream_kwargs(client)
        assert kwargs["model"] == expected_model
        assert ("thinking" in kwargs) == (expected_thinking == "adaptive")

    def test_env_override_changes_model(self, tmp_path, monkeypatch):
        _write_card(tmp_path)
        client = _make_stream_client("artifact_text: body")
        monkeypatch.setattr(v2, "Anthropic", lambda *a, **kw: client)
        monkeypatch.setenv("VOICE_MODEL", SONNET)
        step1_outputs = [{
            "lineage": {"theme_id": "theme_001", "formulation_id": "f1",
                        "grounding_extraction_ids": [], "session_ids": []},
            "theme_display_title": "T", "mode": "question",
            "formulation_text": "F", "detailed_response": "D",
        }]

        v2.run_step2_for_voice(
            "plato", step1_outputs, night=1,
            run_dir=tmp_path / "run", project_root=tmp_path,
        )

        assert _stream_kwargs(client)["model"] == SONNET


class TestVoiceStep3:
    def test_matches_golden_with_env_unset(self, tmp_path, monkeypatch):
        expected_model, expected_thinking = GOLDEN["runtime.voice.step3"]
        _write_card(tmp_path)
        client = _make_stream_client("decision: stand-pat\namended_artifact_text: body")
        monkeypatch.setattr(v3, "Anthropic", lambda *a, **kw: client)
        own_first_draft = {
            "lineage": {"themes_covered": ["theme_001"],
                        "all_grounding_extraction_ids": [], "all_session_ids": []},
            "artifact_text": "body", "selected_form": "essay",
            "focus_decision": "Focus on Response 1", "stance": "x",
        }

        v3.run_step3_for_voice(
            "plato", own_first_draft, [], night=1,
            run_dir=tmp_path / "run", project_root=tmp_path,
        )

        kwargs = _stream_kwargs(client)
        assert kwargs["model"] == expected_model
        assert ("thinking" in kwargs) == (expected_thinking == "adaptive")

    def test_env_override_changes_model(self, tmp_path, monkeypatch):
        _write_card(tmp_path)
        client = _make_stream_client("decision: stand-pat\namended_artifact_text: body")
        monkeypatch.setattr(v3, "Anthropic", lambda *a, **kw: client)
        monkeypatch.setenv("VOICE_MODEL", SONNET)
        own_first_draft = {
            "lineage": {"themes_covered": ["theme_001"],
                        "all_grounding_extraction_ids": [], "all_session_ids": []},
            "artifact_text": "body", "selected_form": "essay",
            "focus_decision": "Focus on Response 1", "stance": "x",
        }

        v3.run_step3_for_voice(
            "plato", own_first_draft, [], night=1,
            run_dir=tmp_path / "run", project_root=tmp_path,
        )

        assert _stream_kwargs(client)["model"] == SONNET


class TestVoiceContinuity:
    def _run_dir_with_step2(self, tmp_path: Path) -> Path:
        run_dir = tmp_path / "run"
        s2 = run_dir / "04_voice" / "step2_first_draft_artifacts"
        s2.mkdir(parents=True)
        write_json_atomic(s2 / "plato.json", {
            "lineage": {"voice_slug": "plato", "night": 1},
            "council_member": "Plato", "focus_decision": "x",
            "stance": "x", "selected_form": "essay", "artifact_text": "body",
        })
        return run_dir

    def test_matches_golden_with_env_unset(self, tmp_path, monkeypatch):
        expected_model, expected_thinking = GOLDEN["runtime.voice.continuity"]
        run_dir = self._run_dir_with_step2(tmp_path)
        client = _make_stream_client('{"continuity_block_if_night_2": "x", '
                                      '"continuity_block_artifact_if_night_2": "x"}')
        monkeypatch.setattr(vcont, "Anthropic", lambda *a, **kw: client)

        vcont.generate_continuity("plato", 1, run_dir, project_root=tmp_path)

        kwargs = _stream_kwargs(client)
        assert kwargs["model"] == expected_model
        assert ("thinking" in kwargs) == (expected_thinking == "adaptive")

    def test_env_override_changes_model(self, tmp_path, monkeypatch):
        run_dir = self._run_dir_with_step2(tmp_path)
        client = _make_stream_client('{"continuity_block_if_night_2": "x", '
                                      '"continuity_block_artifact_if_night_2": "x"}')
        monkeypatch.setattr(vcont, "Anthropic", lambda *a, **kw: client)
        monkeypatch.setenv("VOICE_CONTINUITY_MODEL", OPUS)

        vcont.generate_continuity("plato", 1, run_dir, project_root=tmp_path)

        assert _stream_kwargs(client)["model"] == OPUS


class TestEditorDossier:
    def _run_dir_with_briefing(self, tmp_path: Path) -> Path:
        run_dir = tmp_path / "run"
        bp = run_dir / "03_provocateur" / "briefings" / "plato.json"
        bp.parent.mkdir(parents=True, exist_ok=True)
        write_json_atomic(bp, {"formulations": [{
            "theme_id": "theme_001", "theme_display_title": "T", "mode": "question",
            "narrative_briefing": "<briefing>",
            "full_theme_record": {
                "theme_title_from_researcher": "T", "theme_abstract_from_researcher": "A",
                "clusters": [], "theme_flags": {},
            },
        }]})
        ap = run_dir / "04_voice" / "step2_first_draft_artifacts" / "plato.json"
        ap.parent.mkdir(parents=True, exist_ok=True)
        write_json_atomic(ap, {
            "lineage": {"voice_slug": "plato", "themes_covered": []},
            "council_member": "Plato", "focus_decision": "x", "artifact_text": "<artifact>",
        })
        return run_dir

    def test_matches_golden_with_env_unset(self, tmp_path, monkeypatch):
        expected_model, expected_thinking = GOLDEN["runtime.editor.dossier"]
        run_dir = self._run_dir_with_briefing(tmp_path)
        client = _make_stream_client("**kicker:** K\n**headline:** H\n**body_paragraphs:**\np1\n")

        edg.generate_dossier(
            theme_id="theme_001", voice_slugs=["plato"], run_dir=run_dir, night=1,
            system_prompt=("PREFIX", "TAIL"), client=client,
        )

        kwargs = _stream_kwargs(client)
        assert kwargs["model"] == expected_model
        assert ("thinking" in kwargs) == (expected_thinking == "adaptive")

    def test_env_override_changes_model(self, tmp_path, monkeypatch):
        run_dir = self._run_dir_with_briefing(tmp_path)
        client = _make_stream_client("**kicker:** K\n**headline:** H\n**body_paragraphs:**\np1\n")
        monkeypatch.setenv("EDITOR_MODEL", SONNET)

        edg.generate_dossier(
            theme_id="theme_001", voice_slugs=["plato"], run_dir=run_dir, night=1,
            system_prompt=("PREFIX", "TAIL"), client=client,
        )

        assert _stream_kwargs(client)["model"] == SONNET


# ===========================================================================
# 6. Voice Step 1 validation (OpenAI/Gemini ladder)
# ===========================================================================

import flows.voice.step1_validation as v1v  # noqa: E402


class TestVoiceStep1ValidationLadder:
    def test_ladder_matches_golden_with_env_unset(self, monkeypatch):
        expected_model, _ = GOLDEN["runtime.voice.step1_validation"]
        assert expected_model == LADDER[0] == "gpt-5.4"

        fake_openai_client = MagicMock()
        fake_openai_client.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="PASS"))],
            usage=MagicMock(prompt_tokens=1, completion_tokens=1),
        )
        fake_openai_module = types.SimpleNamespace(OpenAI=lambda *a, **kw: fake_openai_client)
        monkeypatch.setitem(sys.modules, "openai", fake_openai_module)

        result = v1v._call_openai_with_fallback(
            system="sys", user="usr", max_tokens=100, reasoning_effort="high",
        )

        assert result["model"] == expected_model
        assert fake_openai_client.chat.completions.create.call_args.kwargs["model"] == expected_model

    def test_env_override_changes_ladder(self, monkeypatch):
        monkeypatch.setenv("VOICE_VALIDATION_MODELS", "gpt-4o,gemini-2.5-pro")

        fake_openai_client = MagicMock()
        fake_openai_client.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="PASS"))],
            usage=MagicMock(prompt_tokens=1, completion_tokens=1),
        )
        fake_openai_module = types.SimpleNamespace(OpenAI=lambda *a, **kw: fake_openai_client)
        monkeypatch.setitem(sys.modules, "openai", fake_openai_module)

        result = v1v._call_openai_with_fallback(
            system="sys", user="usr", max_tokens=100, reasoning_effort="high",
        )

        assert result["model"] == "gpt-4o"


# ===========================================================================
# 7. Voice Step 2 validation (4 pillars, shared _call_anthropic)
# ===========================================================================

import flows.voice.step2_validation as v2v  # noqa: E402


class TestVoiceStep2Validation:
    def test_matches_golden_with_env_unset(self, monkeypatch):
        expected_model, expected_thinking = GOLDEN["runtime.voice.step2_validation"]
        fake_client = MagicMock()
        fake_client.messages.create.return_value = MagicMock(
            content=[MagicMock(text='{"verdict": "PASS"}')],
            usage=MagicMock(input_tokens=1, output_tokens=1),
        )
        monkeypatch.setattr(
            "anthropic.Anthropic", lambda *a, **kw: fake_client,
        )

        v2v._call_anthropic(system="sys", user="usr")

        kwargs = fake_client.messages.create.call_args.kwargs
        assert kwargs["model"] == expected_model
        assert ("thinking" in kwargs) == (expected_thinking == "adaptive")

    def test_env_override_changes_model(self, monkeypatch):
        fake_client = MagicMock()
        fake_client.messages.create.return_value = MagicMock(
            content=[MagicMock(text='{"verdict": "PASS"}')],
            usage=MagicMock(input_tokens=1, output_tokens=1),
        )
        monkeypatch.setattr("anthropic.Anthropic", lambda *a, **kw: fake_client)
        monkeypatch.setenv("VOICE_STEP2_VALIDATION_MODEL", OPUS)

        v2v._call_anthropic(system="sys", user="usr")

        assert fake_client.messages.create.call_args.kwargs["model"] == OPUS


# ===========================================================================
# 8. Synthesis router (shared by Voice Step 2 + Editor Stage 1)
# ===========================================================================

import flows.editor.synthesis_router as sr  # noqa: E402


class TestSynthesisRouter:
    def test_matches_golden_with_env_unset(self, monkeypatch):
        expected_model, expected_thinking = GOLDEN["runtime.synthesis_router"]
        client = MagicMock()
        client.messages.create.return_value = MagicMock(content=[MagicMock(
            type="text", text="chosen_theme_id: theme_001\nrationale: because",
        )])

        chosen, _ = sr.route_synthesis_voice(
            voice_slug="plato", artifact_text="x",
            candidates=[{"theme_id": "theme_001"}], client=client,
        )

        assert chosen == "theme_001"
        kwargs = client.messages.create.call_args.kwargs
        assert kwargs["model"] == expected_model
        assert ("thinking" in kwargs) == (expected_thinking == "adaptive")

    def test_env_override_changes_model(self, monkeypatch):
        client = MagicMock()
        client.messages.create.return_value = MagicMock(content=[MagicMock(
            type="text", text="chosen_theme_id: theme_001\nrationale: because",
        )])
        monkeypatch.setenv("SYNTHESIS_ROUTER_MODEL", OPUS)

        sr.route_synthesis_voice(
            voice_slug="plato", artifact_text="x",
            candidates=[{"theme_id": "theme_001"}], client=client,
        )

        assert client.messages.create.call_args.kwargs["model"] == OPUS
