#!/usr/bin/env python3
"""arch_03_preservation_audit.py — Preservation-rate audit for 1-arch-03 additive merge.

Three metrics per plan §7.3 / §18a:

  (a) char-overlap: fraction of DR §N source characters covered by matching
      blocks in the merged chunk output (recall metric: source → merged).
      Target ≥85% on §3/§4/§5; §1/§2 Near-parity expected; §6 may expand.

  (b) citation preservation: author last-names referenced in DR §N source vs
      authors present in merged citations[] across all dossier citation fields.
      Target 100%.

  (c) named-structural-pattern preservation (§3 specific): canonical pattern
      names checked against analytical_context_reasoning.structural_patterns[]
      names and against full merged text.
      Target 100%.

Output: JSON audit file at <project>/voices/<slug>/_arch_03_audit.json
Prints summary to stdout.

Usage (from personas/ directory):
  venv/bin/python scripts/arch_03_preservation_audit.py \\
      --voice fyodor_dostoevsky \\
      --project ../../projects/phase-l-dostoevsky
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from flows.shared.project_root import resolve_project_root


# ── canonical structural patterns expected from DR §3 (per §18a spec) ─────────
STRUCTURAL_PATTERNS = [
    "scandal-scene",
    "carnivalization",
    "threshold-chronotope",
    "sideshadowing",
    "crowning/decrowning",
    "Menippean",
    "confession-under-pressure",
    "vdrug",
    "polyphony",
]

# section index → DR dossier file name stem
SECTION_FILES = {
    1: "01_section_1.md",
    2: "02_section_2.md",
    3: "03_section_3.md",
    4: "04_section_4.md",
    5: "05_section_5.md",
    6: "06_section_6.md",
}

# Sections where ≥85% overlap is the target
HIGH_COVERAGE_SECTIONS = {3, 4, 5}

# Known scholarly author last names embedded in DR section texts.
# These are mined once per section using regex; this list anchors the extraction
# heuristic for multi-word last names that the regex alone might split.
_AUTHOR_HINTS = [
    "Frank", "Bakhtin", "Morson", "Jackson", "Grossman", "Terras", "Williams",
    "Mochulsky", "Kasatkina", "Peace", "Jones", "Leatherbarrow", "Emerson",
    "Martinsen", "Knapp", "Miller", "Catteau", "Dalton-Brown", "Lantz",
    "Bojanowska", "Scanlan", "Leatherbarrow", "Natova", "Vetlovskaya",
    "Dostoevskaya", "Golosovker", "Perlina", "Reed", "Linner", "Holquist",
    "Lindenmeyr", "Murav", "Corrigan", "Thompson", "Girard", "Belknap",
    "Fusso", "Hale", "Iyer", "Rowan",
]


# ── text normalisation ─────────────────────────────────────────────────────────

def _normalize(text: str) -> str:
    """Strip markdown syntax and collapse whitespace for overlap comparison."""
    # Remove markdown headings, bold, italic markers
    text = re.sub(r"#{1,6}\s+", " ", text)
    text = re.sub(r"\*{1,3}([^*]+)\*{1,3}", r"\1", text)
    text = re.sub(r"`[^`]*`", " ", text)
    # Remove URLs
    text = re.sub(r"https?://\S+", " ", text)
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text.lower()


# ── char overlap metric ────────────────────────────────────────────────────────

_STOP_WORDS = {
    "the", "this", "that", "and", "for", "not", "his", "her", "was", "are",
    "with", "from", "have", "been", "were", "they", "will", "which", "when",
    "also", "into", "more", "than", "its", "but", "all", "had", "one", "who",
    "any", "can", "has", "him", "their", "there", "what", "each", "some",
    "does", "then", "over", "both", "such", "only", "even", "most",
}


def char_overlap(source_text: str, merged_text: str) -> dict[str, Any]:
    """Compute vocabulary recall: fraction of unique content words from DR source
    that appear in the merged chunk output.

    Uses keyword/vocabulary coverage rather than verbatim SequenceMatcher,
    because merged output is synthesized/paraphrased not verbatim-copied.

    Also reports raw size ratio (merged_chars / source_chars) as a secondary
    metric matching the plan §1.2 empirical table.

    Target ≥85% vocabulary recall on §3/§4/§5.
    """
    src_norm = _normalize(source_text)
    tgt_norm = _normalize(merged_text)

    if not src_norm:
        return {"ratio": 0.0, "source_unique_terms": 0, "merged_chars": len(tgt_norm),
                "source_chars": 0, "size_ratio": 0.0}

    # Extract unique significant terms (≥5 chars, not stop words)
    src_tokens = set(
        w for w in re.findall(r"\b[a-z]{5,}\b", src_norm)
        if w not in _STOP_WORDS
    )
    if not src_tokens:
        return {"ratio": 1.0, "source_unique_terms": 0, "merged_chars": len(tgt_norm),
                "source_chars": len(src_norm), "size_ratio": len(tgt_norm) / len(src_norm)}

    found = sum(1 for t in src_tokens if t in tgt_norm)
    ratio = found / len(src_tokens)
    size_ratio = len(tgt_norm) / len(src_norm) if src_norm else 0.0

    return {
        "ratio": round(ratio, 4),
        "source_unique_terms": len(src_tokens),
        "terms_found_in_merged": found,
        "merged_chars": len(tgt_norm),
        "source_chars": len(src_norm),
        "size_ratio": round(size_ratio, 4),
    }


# ── citation extraction from markdown source ───────────────────────────────────

def extract_source_authors(text: str) -> list[str]:
    """Extract author last names from inline scholar references in DR dossier.

    Matches patterns like:
      - "Bakhtin (1984)"  /  "Bakhtin (PDP, ch. 4)"
      - "Jackson, *The Art of Dostoevsky*"
      - "Morson's *Narrative and Freedom*"
      - Bare proper-noun runs like "Terras" when near a book title
    Returns deduplicated lowercase list.
    """
    found: set[str] = set()

    # Pattern A: LastName (year) or LastName, FirstName (year)
    for m in re.finditer(
        r"\b([A-Z][a-z]{2,}(?:\s+[A-Z][a-z]+)?)\s*(?:and\s+[A-Z][a-z]+)?\s*\(\d{4}",
        text,
    ):
        # Take last token of the name match as last name
        name = m.group(1).split()[-1].lower()
        found.add(name)

    # Pattern B: "in *Work Title* (year)"  preceded by a name
    for m in re.finditer(
        r"\b([A-Z][a-z]{2,}(?:\s+[A-Z][a-z]+)?)[,\s]+in\s+\*",
        text,
    ):
        name = m.group(1).split()[-1].lower()
        found.add(name)

    # Pattern C: possessive "Author's *Work*"
    for m in re.finditer(
        r"\b([A-Z][a-z]{2,}(?:\s+[A-Z][a-z]+)?)'s\s+\*",
        text,
    ):
        name = m.group(1).split()[-1].lower()
        found.add(name)

    # Pattern D: names from hint list that appear anywhere in text (belt + braces)
    text_lower = text.lower()
    for hint in _AUTHOR_HINTS:
        if hint.lower() in text_lower:
            found.add(hint.lower())

    # Filter out false positives (very short, common words)
    stop = {"the", "this", "that", "and", "for", "not", "his", "her", "was"}
    found -= stop
    return sorted(found)


def extract_merged_authors(dossier: dict[str, Any]) -> set[str]:
    """Collect all author last-name tokens from citations[] across the dossier."""
    authors: set[str] = set()

    def _walk(obj: Any) -> None:
        if isinstance(obj, dict):
            if "author" in obj and isinstance(obj["author"], str):
                # Author may be "Frank, Joseph" or "Mikhail Bakhtin" — take last token
                raw = obj["author"].strip()
                # Handle "Last, First" format
                if "," in raw:
                    last = raw.split(",")[0].strip().lower()
                else:
                    last = raw.split()[-1].lower()
                authors.add(last)
            for v in obj.values():
                _walk(v)
        elif isinstance(obj, list):
            for item in obj:
                _walk(item)

    _walk(dossier)
    return authors


# ── structural pattern check ───────────────────────────────────────────────────

def check_structural_patterns(
    dossier: dict[str, Any],
    full_merged_text: str,
) -> dict[str, Any]:
    """Verify canonical §3 structural patterns appear in merged output.

    Checks analytical_context_reasoning.structural_patterns[].name first;
    falls back to substring check in full merged text.
    """
    results: dict[str, str] = {}  # pattern → "schema" | "text" | "missing"

    # Collect names from analytical_context_reasoning if present
    acr = dossier.get("analytical_context_reasoning") or {}
    schema_names: set[str] = set()
    for sp in acr.get("structural_patterns", []):
        if isinstance(sp, dict) and "name" in sp:
            schema_names.add(sp["name"].lower())

    merged_lower = full_merged_text.lower()

    for pattern in STRUCTURAL_PATTERNS:
        pat_lower = pattern.lower()
        # Check schema first (exact or substring match in name)
        in_schema = any(pat_lower in n or n in pat_lower for n in schema_names)
        # Check full merged text (substring)
        in_text = pat_lower in merged_lower
        # Also check hyphen-free / slash variants
        if not in_text:
            alt = pat_lower.replace("-", " ").replace("/", " ")
            in_text = alt in merged_lower

        if in_schema:
            results[pattern] = "schema"
        elif in_text:
            results[pattern] = "text"
        else:
            results[pattern] = "missing"

    present = sum(1 for v in results.values() if v != "missing")
    return {
        "target": len(STRUCTURAL_PATTERNS),
        "found": present,
        "rate": round(present / len(STRUCTURAL_PATTERNS), 4),
        "details": results,
    }


# ── serialise dossier to flat text ────────────────────────────────────────────

def _dossier_to_text(obj: Any) -> str:
    """Recursively extract all string leaf values from dossier JSON."""
    parts: list[str] = []

    def _walk(o: Any) -> None:
        if isinstance(o, str):
            parts.append(o)
        elif isinstance(o, dict):
            for v in o.values():
                _walk(v)
        elif isinstance(o, list):
            for item in o:
                _walk(item)

    _walk(obj)
    return " ".join(parts)


# ── section-specific merged-text extraction ───────────────────────────────────

_SECTION_KEYS = {
    1: ["life_scaffold", "formative_candidates"],
    2: ["commitments", "concepts", "tensions"],
    3: ["reasoning_method", "textures", "analytical_context_reasoning"],
    4: ["moves", "register", "vocabulary", "analytical_context_voice"],
    5: ["knowledge_boundary", "sensitive_topics", "hard_limits"],
    6: ["works", "passages", "reference_only_passages"],  # `urls` removed per 1-arch-07
}


def section_merged_text(dossier: dict[str, Any], section: int) -> str:
    """Return flat text of the merged dossier fields corresponding to §N."""
    keys = _SECTION_KEYS.get(section, [])
    parts: list[Any] = []
    for k in keys:
        if k in dossier:
            parts.append(dossier[k])
    return _dossier_to_text(parts)


# ── main audit ─────────────────────────────────────────────────────────────────

def run_audit(voice: str, project_root: Path) -> dict[str, Any]:
    voice_dir = project_root / "voices" / voice
    dr_dir = voice_dir / "01_research" / "04_dr_dossier"
    merged_path = voice_dir / "02_merge" / "08_merged_dossier.json"

    if not dr_dir.exists():
        sys.exit(f"DR dossier directory not found: {dr_dir}")
    if not merged_path.exists():
        sys.exit(
            f"Merged dossier not found: {merged_path}\n"
            "Run Stage 1 (run_pass_1_all.py) first."
        )

    with open(merged_path) as f:
        dossier: dict[str, Any] = json.load(f)

    full_merged_text = _dossier_to_text(dossier)
    merged_authors = extract_merged_authors(dossier)

    section_results: dict[str, Any] = {}

    for section, filename in SECTION_FILES.items():
        src_path = dr_dir / filename
        if not src_path.exists():
            section_results[f"section_{section}"] = {"error": f"source file not found: {src_path}"}
            continue

        with open(src_path) as f:
            source_text = f.read()

        merged_section_text = section_merged_text(dossier, section)

        # (a) char overlap
        overlap = char_overlap(source_text, merged_section_text)
        target_met = (
            overlap["ratio"] >= 0.85
            if section in HIGH_COVERAGE_SECTIONS
            else None  # no strict target for §1/§2/§6
        )

        # (b) citation preservation
        source_authors = extract_source_authors(source_text)
        missing_authors = [a for a in source_authors if a not in merged_authors]
        cite_rate = (
            round((len(source_authors) - len(missing_authors)) / len(source_authors), 4)
            if source_authors
            else 1.0
        )
        cite_target_met = len(missing_authors) == 0

        section_result: dict[str, Any] = {
            "char_overlap": {
                **overlap,
                "target": "≥85%" if section in HIGH_COVERAGE_SECTIONS else "informational",
                "target_met": target_met,
            },
            "citation_preservation": {
                "source_authors": source_authors,
                "missing_from_merged": missing_authors,
                "rate": cite_rate,
                "target": "100%",
                "target_met": cite_target_met,
            },
        }

        # (c) structural patterns — §3 only
        if section == 3:
            section_result["structural_patterns"] = check_structural_patterns(
                dossier, full_merged_text
            )

        section_results[f"section_{section}"] = section_result

    # ── summary ──
    overlap_flags = {
        f"section_{s}": section_results[f"section_{s}"]["char_overlap"]["target_met"]
        for s in HIGH_COVERAGE_SECTIONS
        if f"section_{s}" in section_results
    }
    all_overlap_pass = all(v for v in overlap_flags.values() if v is not None)

    # Aggregate citation pass/fail across all sections
    all_cites_met = all(
        section_results.get(f"section_{s}", {})
        .get("citation_preservation", {})
        .get("target_met", True)
        for s in range(1, 7)
    )

    struct_patterns = section_results.get("section_3", {}).get("structural_patterns")
    struct_pass = struct_patterns is None or struct_patterns["found"] == struct_patterns["target"]

    overall_pass = all_overlap_pass and all_cites_met and struct_pass

    audit: dict[str, Any] = {
        "voice": voice,
        "merged_dossier_path": str(merged_path),
        "summary": {
            "overall_pass": overall_pass,
            "char_overlap_pass": all_overlap_pass,
            "overlap_by_section": {
                f"section_{s}": section_results.get(f"section_{s}", {})
                .get("char_overlap", {})
                .get("ratio")
                for s in range(1, 7)
            },
            "citation_preservation_pass": all_cites_met,
            "structural_patterns_pass": struct_pass,
        },
        "sections": section_results,
    }
    return audit


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Preservation-rate audit for 1-arch-03 additive merge."
    )
    parser.add_argument("--voice", required=True, help="Voice slug (e.g. fyodor_dostoevsky)")
    parser.add_argument("--project", default=None, help="Project root path")
    args = parser.parse_args()

    project_root = resolve_project_root(args.project)
    audit = run_audit(args.voice, project_root)

    output_path = project_root / "voices" / args.voice / "_arch_03_audit.json"
    with open(output_path, "w") as f:
        json.dump(audit, f, indent=2)

    # Print summary
    s = audit["summary"]
    print(f"\n{'='*60}")
    print(f"ARCH-03 PRESERVATION AUDIT — {args.voice}")
    print(f"{'='*60}")
    print(f"Overall: {'PASS ✓' if s['overall_pass'] else 'FAIL ✗'}")
    print()
    print("Char overlap (§3/§4/§5 target ≥85%):")
    for k, v in s["overlap_by_section"].items():
        flag = ""
        sec_num = int(k.split("_")[1])
        if sec_num in HIGH_COVERAGE_SECTIONS:
            flag = " ✓" if (v or 0) >= 0.85 else " ✗ (BELOW TARGET)"
        print(f"  {k}: {f'{v:.1%}' if v is not None else 'N/A'}{flag}")
    print()
    print(f"Citation preservation: {'PASS ✓' if s['citation_preservation_pass'] else 'FAIL ✗'}")
    sp = audit["sections"].get("section_3", {}).get("structural_patterns")
    if sp:
        print(
            f"Structural patterns (§3): {sp['found']}/{sp['target']} "
            f"{'PASS ✓' if s['structural_patterns_pass'] else 'FAIL ✗'}"
        )
        for pat, status in sp["details"].items():
            icon = "✓" if status != "missing" else "✗"
            print(f"  {icon} {pat} ({status})")
    print()
    print(f"Audit written to: {output_path}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
