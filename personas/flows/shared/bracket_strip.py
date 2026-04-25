"""bracket_strip.py — FU#33 P1 universal bracket-tag residue strip.

Walks all string fields in the per-pass generation outputs (Pass 2-6
artifacts under 04_generation/) and strips inline scaffolding tags that
leaked from curator-side merge dossiers / Pass 7-pre annotations into
runtime prose. Pass 2-6 prompts (FU#12-A + FU#32 + FU#38) explicitly
prohibit these tags but the patcher (FU#13) only rewrites flagged
issues per-field; systemic-pattern cleanup is out of scope.

This is a deterministic regex pass — no LLM call — intended to run after
Pass 7c (so the validators have already checked the un-stripped state)
and before Derive (so derive products + assembled card + chat artifact
all see clean prose).

Tag allowlist (only these names are stripped; any other bracketed text
in the prose is preserved):

  Boddice biocultural tags (per Pass 7-pre boddice schema):
    [experiential_reconstruction]
    [projection_warning: ...]

  Schema taxonomy markers (Pass 4a constitution categorization):
    [ontological] [epistemological] [ethical-political] [ethical_political]
    [unique] [metaphysical] [psychological] [political] [aesthetic]
    [cosmological] [epistemic] [ethical]

  EvidenceTag values that should not appear in runtime prose
  (Pass 2-6 prompts strip these per FU#12-A):
    [stated] [scholarly_consensus] [inference] [contested]

  Curator-side annotations (Pass 6 corpus passages):
    [curator_note] [curator-note] [pedagogical_note] [editorial_note]

What this module does NOT touch:
  - Anything outside the tag allowlist (legitimate bracketed text:
    "[Plato 427-347 BCE]", "[Republic, 327a]", etc.)
  - Fields outside 04_generation/ (the merge chunks at 02_merge/ keep
    their evidence_tags as legitimate metadata; the corpus at 03_corpus/
    is raw fetched text)
  - Provocateur Profile / Evaluation Rubric / Chat artifact (those are
    Derive-side outputs; Derive will see cleaned prose by virtue of
    consuming cleaned chunks)
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


# Tag-name allowlist. Order does not matter; the regex constructor builds
# a single alternation from this tuple.
_SCAFFOLDING_TAG_NAMES = (
    # Boddice biocultural tags
    "experiential_reconstruction",
    "projection_warning",
    # Schema taxonomy markers
    "ontological",
    "epistemological",
    "ethical-political",
    "ethical_political",
    "unique",
    "metaphysical",
    "psychological",
    "political",
    "aesthetic",
    "cosmological",
    "epistemic",
    "ethical",
    # EvidenceTag values
    "stated",
    "scholarly_consensus",
    "inference",
    "contested",
    # Curator-side annotations
    "curator_note",
    "curator-note",
    "pedagogical_note",
    "editorial_note",
)

# Match `[tag]` or `[tag: optional inner content]`. The leading `\s?` lets
# us absorb a single space before the tag so we don't leave double-spaces
# after stripping mid-sentence tags.
_TAG_PATTERN = re.compile(
    r"\s?\[(?:" + "|".join(re.escape(t) for t in _SCAFFOLDING_TAG_NAMES) + r")(?::[^\]]*)?\]"
)

# Post-strip cosmetic cleanups: collapse multi-spaces, repair " ." / " ," /
# " ;" left behind when an inline tag sat just before punctuation.
_MULTISPACE_RE = re.compile(r"  +")
_SPACE_BEFORE_PUNCT_RE = re.compile(r" ([.,;:!?])")


def strip_inline_tags(text: str) -> tuple[str, int]:
    """Strip scaffolding tags from a single string. Returns (cleaned_text,
    tags_removed_count). Idempotent: a second call on the result is a no-op."""
    if not isinstance(text, str) or "[" not in text:
        return text, 0
    new = _TAG_PATTERN.sub("", text)
    removed = (text.count("[") - new.count("[")) - (text.count("[[") - new.count("[["))
    if new == text:
        return text, 0
    new = _MULTISPACE_RE.sub(" ", new)
    new = _SPACE_BEFORE_PUNCT_RE.sub(r"\1", new)
    return new, max(removed, 0)


def strip_inline_tags_recursive(node: Any) -> tuple[Any, int]:
    """Walk a JSON-shaped structure (dict/list/str/scalar). Returns
    (cleaned_structure, total_tags_removed). Non-mutating: returns a
    new structure for any branch that contained string-level changes."""
    if isinstance(node, str):
        return strip_inline_tags(node)
    if isinstance(node, list):
        out = []
        total = 0
        for v in node:
            cleaned, n = strip_inline_tags_recursive(v)
            out.append(cleaned)
            total += n
        return out, total
    if isinstance(node, dict):
        out = {}
        total = 0
        for k, v in node.items():
            cleaned, n = strip_inline_tags_recursive(v)
            out[k] = cleaned
            total += n
        return out, total
    return node, 0


def strip_chunks_in_place(generation_dir: Path) -> dict[str, int]:
    """Walk every .json file in generation_dir, strip scaffolding tags from
    string fields, write back atomically if anything changed.

    Returns a summary dict: {tags_removed, files_touched, files_scanned}.
    """
    if not generation_dir.exists() or not generation_dir.is_dir():
        return {"tags_removed": 0, "files_touched": 0, "files_scanned": 0}

    total_tags = 0
    touched = 0
    scanned = 0
    for path in sorted(generation_dir.glob("*.json")):
        scanned += 1
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        cleaned, n = strip_inline_tags_recursive(data)
        if n > 0:
            total_tags += n
            touched += 1
            tmp = path.with_suffix(path.suffix + ".tmp")
            tmp.write_text(json.dumps(cleaned, ensure_ascii=False, indent=2), encoding="utf-8")
            tmp.replace(path)
    return {"tags_removed": total_tags, "files_touched": touched, "files_scanned": scanned}
