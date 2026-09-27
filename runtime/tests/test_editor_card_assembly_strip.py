"""Regression test for C56 — editor's FU#41 `corpus_metadata` nested-strip.

`_strip_nested_corpus_metadata` checked `isinstance(curated, list)`, but
`curated_corpus_passages` is a dict shaped `{corpus_metadata, passages}`
(docs/AI_Assembly_Persona_Card_v2.md) — so the strip silently no-op'd on
every real card, leaking build-time provenance into the editor's system
prompt. Reference (correct) twins: `runtime/flows/voice/card_assembly.py`
`_strip_nested_corpus_metadata` and
`personas/flows/shared/chat_prompt_builder.py::_strip_nested` (both
dict-based).
"""
from __future__ import annotations

import sys
from pathlib import Path

_RUNTIME_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_RUNTIME_ROOT / "flows"))

from editor.card_assembly import (  # noqa: E402
    _strip_nested_corpus_metadata,
    assemble_system_prompt,
)

# Realistic dict-shaped curated_corpus_passages, modeled on
# _workspace/archive/reference-cards/dostoevsky_chat_v2_2026_04_24.json.
CURATED_CORPUS_PASSAGES = {
    "corpus_metadata": {
        "voice_basis": "Your own essays and letters are the Tier 1 primary basis.",
        "source_count": 9,
        "total_passages": 8,
        "notes": "Build-time provenance notes — never for runtime consumption.",
    },
    "passages": [
        {"source": "Essay I", "text": "A passage the voice may draw on."},
    ],
}


def test_strip_removes_corpus_metadata_keeps_passages():
    stripped = _strip_nested_corpus_metadata(CURATED_CORPUS_PASSAGES)
    assert "corpus_metadata" not in stripped
    assert stripped["passages"] == CURATED_CORPUS_PASSAGES["passages"]


def test_strip_is_noop_on_non_dict_input():
    # Defensive: unexpected shapes pass through unchanged rather than crash.
    assert _strip_nested_corpus_metadata([1, 2, 3]) == [1, 2, 3]
    assert _strip_nested_corpus_metadata(None) is None


def test_assembled_prompt_omits_corpus_metadata_provenance():
    """End-to-end: a realistic dict-shaped corpus_metadata must not leak
    into the rendered system prompt (previously it always did, because the
    strip no-op'd against dict input)."""
    card = {
        "council_member_name": "Test Editor",
        "constitution": "stub constitution",
        "concept_lexicon": "stub lexicon",
        "curated_corpus_passages": CURATED_CORPUS_PASSAGES,
    }
    prefix, _tail = assemble_system_prompt(card, night=1)
    assert "corpus_metadata" not in prefix
    assert "Build-time provenance notes" not in prefix
    assert "A passage the voice may draw on." in prefix
