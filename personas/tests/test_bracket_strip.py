"""test_bracket_strip.py — Tests for FU#33 P1 bracket-tag residue strip.

Covers:
  1. Single-string strip — tag patterns matched, count returned
  2. Allowlist enforcement — non-allowlisted bracketed text is preserved
  3. Idempotency — second call on cleaned text is a no-op
  4. Nested-structure walk — dict / list / mixed shapes
  5. Cosmetic cleanups — multispace collapse, space-before-punct repair
  6. File-level strip — strip_chunks_in_place reads/writes atomically
"""
from __future__ import annotations

import json
from pathlib import Path

from flows.shared.bracket_strip import (
    _SCAFFOLDING_TAG_NAMES,
    strip_chunks_in_place,
    strip_inline_tags,
    strip_inline_tags_recursive,
)


# ── single-string strip ─────────────────────────────────────────────────────

def test_strip_simple_tag():
    cleaned, n = strip_inline_tags("Plato held this principle [ontological]")
    assert cleaned == "Plato held this principle"
    assert n == 1


def test_strip_tag_with_content():
    cleaned, n = strip_inline_tags(
        "The body is sōma-sēma [projection_warning: avoid clinical-trauma framing]; the soul"
    )
    assert "[projection_warning" not in cleaned
    assert "sōma-sēma; the soul" in cleaned
    assert n == 1


def test_strip_multiple_tags_in_one_string():
    cleaned, n = strip_inline_tags(
        "Principle 1 [unique] [ontological] is load-bearing [stated]"
    )
    assert "[" not in cleaned
    assert "Principle 1 is load-bearing" in cleaned
    assert n == 3


def test_unknown_bracketed_text_preserved():
    """Allowlist is closed: bracketed text that isn't a known scaffolding
    tag stays intact."""
    cleaned, n = strip_inline_tags(
        "Plato (427-347 BCE) wrote [Republic 327a] and other dialogues"
    )
    assert cleaned == "Plato (427-347 BCE) wrote [Republic 327a] and other dialogues"
    assert n == 0


def test_no_brackets_short_circuit():
    """Strings without `[` should pass through unchanged with zero work."""
    cleaned, n = strip_inline_tags("plain prose, no scaffolding")
    assert cleaned == "plain prose, no scaffolding"
    assert n == 0


def test_idempotent():
    """Calling twice should not double-strip or double-collapse spaces."""
    once, n1 = strip_inline_tags("First [unique] sentence. Second [stated] sentence.")
    twice, n2 = strip_inline_tags(once)
    assert once == twice
    assert n2 == 0
    assert n1 == 2


def test_cosmetic_multispace_collapse():
    """Stripping a mid-sentence tag shouldn't leave double-spaces."""
    cleaned, _ = strip_inline_tags("the soul [unique] is tripartite")
    assert "  " not in cleaned
    assert cleaned == "the soul is tripartite"


def test_cosmetic_space_before_punct_repair():
    """Stripping a tag right before punctuation shouldn't leave a space."""
    cleaned, _ = strip_inline_tags("dialectic ascends to the Good [unique].")
    assert cleaned == "dialectic ascends to the Good."


def test_non_string_pass_through():
    """Non-string scalars must round-trip unchanged."""
    cleaned, n = strip_inline_tags_recursive(42)
    assert cleaned == 42
    assert n == 0
    cleaned, n = strip_inline_tags_recursive(None)
    assert cleaned is None
    assert n == 0
    cleaned, n = strip_inline_tags_recursive(True)
    assert cleaned is True
    assert n == 0


# ── nested-structure walk ───────────────────────────────────────────────────

def test_dict_recursion():
    payload = {
        "principle": "Plato held X [ontological]",
        "meta": {"note": "second-level [unique]"},
        "evidence": ["a [stated] claim", "another [scholarly_consensus]"],
    }
    cleaned, n = strip_inline_tags_recursive(payload)
    assert n == 4
    # No scaffolding tags remain in any string field (JSON array syntax `[…]`
    # is not a scaffolding tag and survives serialization).
    assert "[ontological]" not in cleaned["principle"]
    assert "[unique]" not in cleaned["meta"]["note"]
    assert "[stated]" not in cleaned["evidence"][0]
    assert "[scholarly_consensus]" not in cleaned["evidence"][1]


def test_recursion_does_not_mutate_input():
    payload = {"a": "X [unique] Y", "b": ["Z [stated]"]}
    snapshot = json.dumps(payload, sort_keys=True)
    _ = strip_inline_tags_recursive(payload)
    assert json.dumps(payload, sort_keys=True) == snapshot


def test_recursion_count_aggregates_across_branches():
    payload = [
        {"a": "[unique]"},
        {"b": "[stated] and [inference]"},
        "[ontological]",
    ]
    _, n = strip_inline_tags_recursive(payload)
    assert n == 4


# ── allowlist coverage ──────────────────────────────────────────────────────

def test_allowlist_covers_known_scaffolding():
    """Known scaffolding tag families should all be stripped."""
    families = [
        "[experiential_reconstruction]",
        "[projection_warning: any inner text]",
        "[ontological]",
        "[epistemological]",
        "[ethical-political]",
        "[unique]",
        "[stated]",
        "[scholarly_consensus]",
        "[inference]",
        "[contested]",
        "[curator_note]",
        "[pedagogical_note]",
        "[editorial_note]",
    ]
    for tag in families:
        cleaned, n = strip_inline_tags(f"prose {tag} more prose")
        assert tag not in cleaned, f"Tag {tag!r} not stripped"
        assert n == 1, f"Tag {tag!r} expected 1 strip, got {n}"


def test_allowlist_size_matches_constant():
    """Sanity: the constant tuple in the module matches what tests assume."""
    assert "experiential_reconstruction" in _SCAFFOLDING_TAG_NAMES
    assert "projection_warning" in _SCAFFOLDING_TAG_NAMES
    assert "stated" in _SCAFFOLDING_TAG_NAMES
    assert len(_SCAFFOLDING_TAG_NAMES) >= 20  # current spec; extensible upward


# ── file-level strip ────────────────────────────────────────────────────────

def test_strip_chunks_in_place_handles_dirty_files(tmp_path: Path):
    gen_dir = tmp_path / "04_generation"
    gen_dir.mkdir()
    dirty = {
        "field_a": "Plato held that [ontological] reality stands still.",
        "field_b": ["a [unique] move", "no tag here"],
        "field_c": {"sub": "deep [stated] claim"},
    }
    (gen_dir / "01_dirty.json").write_text(json.dumps(dirty, ensure_ascii=False, indent=2))

    summary = strip_chunks_in_place(gen_dir)
    assert summary["tags_removed"] == 3
    assert summary["files_touched"] == 1
    assert summary["files_scanned"] == 1

    reread = json.loads((gen_dir / "01_dirty.json").read_text())
    assert "[ontological]" not in reread["field_a"]
    assert "[unique]" not in reread["field_b"][0]
    assert "[stated]" not in reread["field_c"]["sub"]


def test_strip_chunks_in_place_skips_clean_files(tmp_path: Path):
    """A file with no scaffolding tags should not be rewritten."""
    gen_dir = tmp_path / "04_generation"
    gen_dir.mkdir()
    clean = {"field_a": "Plain prose. No tags. References (Plato 427-347 BCE) preserved."}
    out = gen_dir / "01_clean.json"
    out.write_text(json.dumps(clean, ensure_ascii=False, indent=2))
    mtime_before = out.stat().st_mtime_ns

    summary = strip_chunks_in_place(gen_dir)
    assert summary["tags_removed"] == 0
    assert summary["files_touched"] == 0
    assert summary["files_scanned"] == 1
    # File was not rewritten — mtime preserved.
    assert out.stat().st_mtime_ns == mtime_before


def test_strip_chunks_in_place_missing_dir(tmp_path: Path):
    """A non-existent generation_dir returns an empty summary, not an error."""
    summary = strip_chunks_in_place(tmp_path / "does_not_exist")
    assert summary == {"tags_removed": 0, "files_touched": 0, "files_scanned": 0}


def test_strip_chunks_in_place_invalid_json(tmp_path: Path):
    """A file with unparseable JSON is skipped, not crashed on."""
    gen_dir = tmp_path / "04_generation"
    gen_dir.mkdir()
    (gen_dir / "01_clean.json").write_text(json.dumps({"x": "[unique]"}))
    (gen_dir / "02_broken.json").write_text("{not json")
    summary = strip_chunks_in_place(gen_dir)
    assert summary["tags_removed"] == 1  # only the clean file got stripped
    assert summary["files_touched"] == 1
    assert summary["files_scanned"] == 2  # both scanned, broken skipped


def test_strip_chunks_in_place_preserves_unicode(tmp_path: Path):
    """Period vocabulary (gordost', sōma-sēma, eidos) must survive intact."""
    gen_dir = tmp_path / "04_generation"
    gen_dir.mkdir()
    (gen_dir / "01_unicode.json").write_text(json.dumps(
        {"vocab": "gordost' nadryv smirenie [unique] sōma-sēma εἶδος"},
        ensure_ascii=False,
    ))
    strip_chunks_in_place(gen_dir)
    cleaned = json.loads((gen_dir / "01_unicode.json").read_text(encoding="utf-8"))
    assert "gordost'" in cleaned["vocab"]
    assert "sōma-sēma" in cleaned["vocab"]
    assert "εἶδος" in cleaned["vocab"]
    assert "[unique]" not in cleaned["vocab"]
