#!/usr/bin/env python3
"""arch_03_synthesis_audit.py — Layer 2 preservation audit (chunks → 04_generation synthesis).

Layer 1 (arch_03_preservation_audit.py) measures DR §N → merge chunks.
Layer 2 (this script) measures merge chunks → 04_generation per-pass synthesis.

Empirical question: does Pass 2-6 synthesis preserve the merge-layer enriched
content (interpretive_frames, anachronism_discipline, contested-tag claims,
Gemini cross-disciplinary frames), or does it silently drop content?

Per (chunk, consumer-pass) pair:
  (a) density: pass-output-chars / chunk-chars (size ratio, informational)
  (b) vocab_recall: fraction of chunk's unique content words appearing in pass output
  (c) citation_survival: authors cited in chunk → authors in pass output
  (d) frame_type_survival (1-arch-06 specific): per-frame-type preservation rate
      into Pass 2/3/4a

CONSUMPTION MAP MIRRORS _per_chunk_vars() and render() calls in
run_persona_pipeline.py (1-arch-05 Part A). If that changes, update here.

Usage (from personas/ directory):
  venv/bin/python scripts/arch_03_synthesis_audit.py \\
      --voice fyodor_dostoevsky \\
      --project ../../projects/phase-l-dostoevsky

  # Audit a specific snapshot instead of the live card:
  venv/bin/python scripts/arch_03_synthesis_audit.py \\
      --voice fyodor_dostoevsky \\
      --project ../../projects/phase-l-dostoevsky \\
      --snapshot-path _workspace/arch_03_baseline_snapshot/phase_1_complete_20260423_2251

  # A/B compare two snapshots (or snapshot vs live):
  venv/bin/python scripts/arch_03_synthesis_audit.py \\
      --voice fyodor_dostoevsky \\
      --project ../../projects/phase-l-dostoevsky \\
      --compare-snapshot _workspace/arch_03_baseline_snapshot/phase_1_complete_20260423_2251
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from flows.shared.project_root import resolve_project_root

# Reuse Layer 1 helpers
from scripts.arch_03_preservation_audit import (
    _normalize,
    _STOP_WORDS,
    _dossier_to_text,
    extract_merged_authors,
    char_overlap,
    _AUTHOR_HINTS,
)


# ── authoritative consumption map (mirrors run_persona_pipeline.py) ──────────
# Source of truth: _per_chunk_vars() at personas/run_persona_pipeline.py:234
# + per-pass render() calls (Pass 2 L487, Pass 3 L513, Pass 4a L610, Pass 6 L709).
# If those change, update here.

CHUNK_FILE_MAP: dict[str, tuple[str, str]] = {
    # chunk_key → (pass_1_N subdir, filename) relative to 02_merge/
    "life_scaffold":                 ("pass_1_1", "life_scaffold.json"),
    "formative_candidates":          ("pass_1_1", "formative_candidates.json"),
    "commitments":                   ("pass_1_2", "commitments.json"),
    "concepts":                      ("pass_1_2", "concepts.json"),
    "tensions":                      ("pass_1_2", "tensions.json"),
    "interpretive_frames":           ("pass_1_2", "interpretive_frames.json"),
    "reasoning_method":              ("pass_1_3", "reasoning_method.json"),
    "textures":                      ("pass_1_3", "textures.json"),
    "analytical_context_reasoning":  ("pass_1_3", "analytical_context_reasoning.json"),
    "moves":                         ("pass_1_4", "moves.json"),
    "register":                      ("pass_1_4", "register.json"),
    "vocabulary":                    ("pass_1_4", "vocabulary.json"),
    "analytical_context_voice":      ("pass_1_4", "analytical_context_voice.json"),
    "knowledge_boundary":            ("pass_1_5", "knowledge_boundary.json"),
    "sensitive_topics":              ("pass_1_5", "sensitive_topics.json"),
    "hard_limits":                   ("pass_1_5", "hard_limits.json"),
    "works":                         ("pass_1_6", "works.json"),
    "passages":                      ("pass_1_6", "passages.json"),
    "reference_only_passages":       ("pass_1_6", "reference_only_passages.json"),
}

# Per-pass consumption — which chunks each generation pass actually reads.
# Pass 4b (L639) + Pass 5 (L675) are CT-only (no chunk reads); listed for completeness.
PASS_CONSUMPTION: dict[str, dict[str, Any]] = {
    "2_identity_boundaries": {
        "output_file": "01_pass_2_identity_boundaries.json",
        "chunks": [
            "life_scaffold", "formative_candidates",
            "knowledge_boundary", "sensitive_topics", "hard_limits",
        ],
        "frame_subsets": ["voice_level_debate"],
    },
    "3_intellectual_core": {
        "output_file": "03_pass_3_intellectual_core.json",
        "chunks": [
            "commitments", "concepts", "tensions", "interpretive_frames",
            "reasoning_method", "textures", "analytical_context_reasoning",
        ],
        "frame_subsets": None,  # reads full interpretive_frames
    },
    "4a_voice": {
        "output_file": "05_pass_4a_voice.json",
        "chunks": [
            "moves", "register", "vocabulary", "analytical_context_voice",
        ],
        "frame_subsets": ["cross_disciplinary_reframing"],
        "sub_slices": ["available_pathe", "reasoning_method_summary"],
    },
    "4b_artifact": {
        "output_file": "07_pass_4b_artifact.json",
        "chunks": [],
        "note": "CT-only: no chunk reads (reads pass_2_3_4a_summary + card-field refs from 4a)",
    },
    "5_engagement": {
        "output_file": "09_pass_5_engagement.json",
        "chunks": [],
        "note": "CT + card-fields: reads pass_2_3_4_summary + constitution + reasoning_method "
                "card fields + deployment priming (conference_facts + audience_profile)",
    },
    "6_corpus": {
        "output_file": "10_pass_6_corpus.json",
        "chunks": ["works", "passages", "reference_only_passages"],
    },
}


# ── loaders ──────────────────────────────────────────────────────────────────

def load_chunks(merge_dir: Path) -> dict[str, Any]:
    """Load all 19 chunk files from 02_merge/pass_1_*/. Returns {chunk_key: data}."""
    chunks: dict[str, Any] = {}
    for chunk_key, (subdir, filename) in CHUNK_FILE_MAP.items():
        path = merge_dir / subdir / filename
        if not path.exists():
            chunks[chunk_key] = {"_missing": True, "_path": str(path)}
            continue
        with open(path) as f:
            chunks[chunk_key] = json.load(f)
    return chunks


def load_pass_outputs(generation_dir: Path) -> dict[str, Any]:
    """Load per-pass outputs from 04_generation/. Returns {pass_name: data}."""
    outputs: dict[str, Any] = {}
    for pass_name, spec in PASS_CONSUMPTION.items():
        path = generation_dir / spec["output_file"]
        if not path.exists():
            outputs[pass_name] = {"_missing": True, "_path": str(path)}
            continue
        with open(path) as f:
            outputs[pass_name] = json.load(f)
    return outputs


# ── citation extraction (chunk-aware) ────────────────────────────────────────

def extract_chunk_authors(chunk_data: Any) -> set[str]:
    """Chunk files have citations[] at various depths with 'author' fields.
    Reuses Layer 1's extract_merged_authors (walks whole structure for 'author' keys).
    Also scans scholarly_context free-text for author-hint names."""
    authors = extract_merged_authors(chunk_data) if isinstance(chunk_data, (dict, list)) else set()

    # Also catch author-hints appearing in scholarly_context / description free-text
    flat_text = _dossier_to_text(chunk_data).lower()
    for hint in _AUTHOR_HINTS:
        if hint.lower() in flat_text:
            authors.add(hint.lower())
    return authors


# ── frame-type survival (1-arch-06 specific) ─────────────────────────────────

def audit_frame_type_survival(
    frames_chunk: dict[str, Any],
    pass_outputs: dict[str, Any],
) -> dict[str, Any]:
    """For each frame_type in interpretive_frames, check how many frames survive
    into Pass 2/3/4a outputs by checking their name + primary_scholars in output text.

    Pass 2 consumes voice_level_debate frames.
    Pass 3 consumes all frame types.
    Pass 4a consumes cross_disciplinary_reframing frames.
    """
    frames = frames_chunk.get("interpretive_frames", [])
    if not frames and isinstance(frames_chunk, list):
        # Schema variation: top-level list
        frames = frames_chunk

    by_type: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for f in frames:
        if not isinstance(f, dict):
            continue
        by_type[f.get("frame_type", "unknown")].append(f)

    # For each pass that consumes frames, flatten its output text
    consumer_text: dict[str, str] = {}
    for pass_name in ("2_identity_boundaries", "3_intellectual_core", "4a_voice"):
        out = pass_outputs.get(pass_name, {})
        if out.get("_missing"):
            consumer_text[pass_name] = ""
        else:
            consumer_text[pass_name] = _dossier_to_text(out).lower()

    def _frame_present(frame: dict[str, Any], text: str) -> bool:
        """Heuristic: frame counts as present if its name OR ≥1 primary_scholar
        OR any 'what_it_re_reads' anchor appears in pass output text."""
        if not text:
            return False
        name = (frame.get("name") or "").lower().strip()
        if name and len(name) >= 4 and name in text:
            return True
        for scholar in frame.get("primary_scholars", []) or []:
            # Scholar may be "Kasatkina 2022" — take first token
            token = scholar.split()[0].lower() if scholar else ""
            if token and len(token) >= 5 and token in text:
                return True
        for anchor in frame.get("what_it_re_reads", []) or []:
            token = (anchor or "").lower().strip()
            if token and len(token) >= 6 and token in text:
                return True
        return False

    # Build per-frame-type × per-consumer survival table
    survival: dict[str, dict[str, Any]] = {}
    consumer_map = {
        "interpretive_method": ["3_intellectual_core"],
        "cross_disciplinary_reframing": ["3_intellectual_core", "4a_voice"],
        "voice_level_debate": ["2_identity_boundaries", "3_intellectual_core"],
    }

    for frame_type, frame_list in by_type.items():
        consumers = consumer_map.get(frame_type, ["3_intellectual_core"])
        per_consumer: dict[str, Any] = {}
        for consumer in consumers:
            text = consumer_text.get(consumer, "")
            present = sum(1 for f in frame_list if _frame_present(f, text))
            per_consumer[consumer] = {
                "frames_total": len(frame_list),
                "frames_present_in_output": present,
                "rate": round(present / len(frame_list), 4) if frame_list else 1.0,
            }
        survival[frame_type] = {
            "frames_total": len(frame_list),
            "frames_labels": [f.get("name", "<unnamed>") for f in frame_list],
            "by_consumer": per_consumer,
        }

    return survival


# ── per-pair audit ───────────────────────────────────────────────────────────

def audit_pair(
    chunk_key: str,
    chunk_data: Any,
    pass_name: str,
    pass_output: dict[str, Any],
) -> dict[str, Any]:
    """Audit one (chunk, consumer-pass) pair."""
    if isinstance(chunk_data, dict) and chunk_data.get("_missing"):
        return {"chunk_missing": True, "path": chunk_data.get("_path")}
    if pass_output.get("_missing"):
        return {"pass_output_missing": True, "path": pass_output.get("_path")}

    chunk_text = _dossier_to_text(chunk_data)
    pass_text = _dossier_to_text(pass_output)

    # Metric (a): density
    density = {
        "chunk_chars": len(chunk_text),
        "pass_output_chars": len(pass_text),
        "density_ratio": round(len(pass_text) / len(chunk_text), 4) if chunk_text else 0.0,
    }

    # Metric (b): vocab_recall
    recall = char_overlap(chunk_text, pass_text)

    # Metric (c): citation_survival
    chunk_authors = extract_chunk_authors(chunk_data)
    pass_authors = extract_chunk_authors(pass_output)
    missing = sorted(chunk_authors - pass_authors)
    cite_rate = (
        round((len(chunk_authors) - len(missing)) / len(chunk_authors), 4)
        if chunk_authors
        else 1.0
    )

    return {
        "density": density,
        "vocab_recall": {
            "ratio": recall["ratio"],
            "source_unique_terms": recall.get("source_unique_terms", 0),
            "terms_found_in_output": recall.get("terms_found_in_merged", 0),
        },
        "citation_survival": {
            "chunk_authors_count": len(chunk_authors),
            "chunk_authors": sorted(chunk_authors),
            "missing_from_output": missing,
            "rate": cite_rate,
        },
    }


# ── main audit ───────────────────────────────────────────────────────────────

def run_audit(
    voice: str,
    project_root: Path,
    snapshot_path: Path | None = None,
) -> dict[str, Any]:
    voice_dir = project_root / "voices" / voice
    merge_dir = voice_dir / "02_merge"

    if snapshot_path:
        # Snapshot layouts: either <snapshot>/04_generation/ OR <snapshot>/<voice>/04_generation/
        snap = snapshot_path.resolve()
        if not snap.is_absolute():
            snap = (project_root.parent.parent / snapshot_path).resolve()
        candidate_a = snap / "04_generation"
        candidate_b = snap / voice / "04_generation"
        if candidate_a.exists():
            generation_dir = candidate_a
        elif candidate_b.exists():
            generation_dir = candidate_b
        else:
            sys.exit(f"Snapshot generation dir not found at {candidate_a} or {candidate_b}")
    else:
        generation_dir = voice_dir / "04_generation"

    if not merge_dir.exists():
        sys.exit(f"Merge dir not found: {merge_dir}")
    if not generation_dir.exists():
        sys.exit(f"Generation dir not found: {generation_dir}")

    chunks = load_chunks(merge_dir)
    pass_outputs = load_pass_outputs(generation_dir)

    # Per-pass audit
    pass_audits: dict[str, Any] = {}
    for pass_name, spec in PASS_CONSUMPTION.items():
        pass_out = pass_outputs.get(pass_name, {"_missing": True})

        if pass_out.get("_missing"):
            pass_audits[pass_name] = {
                "output_missing": True,
                "chunks_consumed": spec.get("chunks", []),
            }
            continue

        if not spec.get("chunks"):
            # CT-only passes (4b, 5)
            pass_audits[pass_name] = {
                "ct_only": True,
                "note": spec.get("note", ""),
                "output_chars": len(_dossier_to_text(pass_out)),
            }
            continue

        # Per-chunk pairs
        per_chunk: dict[str, Any] = {}
        for chunk_key in spec["chunks"]:
            chunk_data = chunks.get(chunk_key, {"_missing": True})
            per_chunk[chunk_key] = audit_pair(chunk_key, chunk_data, pass_name, pass_out)

        # Aggregate density across all consumed chunks (to the same pass output)
        total_chunk_chars = sum(
            r.get("density", {}).get("chunk_chars", 0)
            for r in per_chunk.values()
            if "density" in r
        )
        pass_output_chars = len(_dossier_to_text(pass_out))
        # Aggregate vocab recall + citation survival
        valid = [r for r in per_chunk.values() if "vocab_recall" in r]
        avg_recall = (
            round(sum(r["vocab_recall"]["ratio"] for r in valid) / len(valid), 4)
            if valid else 0.0
        )
        avg_cite = (
            round(sum(r["citation_survival"]["rate"] for r in valid) / len(valid), 4)
            if valid else 1.0
        )

        pass_audits[pass_name] = {
            "chunks_consumed": spec["chunks"],
            "aggregate": {
                "total_chunk_chars": total_chunk_chars,
                "pass_output_chars": pass_output_chars,
                "density_ratio": round(pass_output_chars / total_chunk_chars, 4)
                if total_chunk_chars else 0.0,
                "avg_vocab_recall": avg_recall,
                "avg_citation_survival": avg_cite,
            },
            "per_chunk": per_chunk,
        }

    # Frame-type survival (1-arch-06)
    frames_chunk = chunks.get("interpretive_frames", {})
    if isinstance(frames_chunk, dict) and not frames_chunk.get("_missing"):
        frame_survival = audit_frame_type_survival(frames_chunk, pass_outputs)
    else:
        frame_survival = {"_skipped": "interpretive_frames chunk missing"}

    # Red flags: chunks consumed by a pass with 0% vocab recall (silent drop)
    red_flags: list[dict[str, Any]] = []
    for pass_name, audit in pass_audits.items():
        if "per_chunk" not in audit:
            continue
        for chunk_key, result in audit["per_chunk"].items():
            if "vocab_recall" in result and result["vocab_recall"]["ratio"] < 0.15:
                red_flags.append({
                    "pass": pass_name,
                    "chunk": chunk_key,
                    "vocab_recall": result["vocab_recall"]["ratio"],
                    "chunk_chars": result["density"]["chunk_chars"],
                })

    return {
        "voice": voice,
        "merge_dir": str(merge_dir),
        "generation_dir": str(generation_dir),
        "snapshot_path": str(snapshot_path) if snapshot_path else None,
        "summary": {
            "passes_audited": [p for p, a in pass_audits.items() if not a.get("output_missing") and not a.get("ct_only")],
            "passes_ct_only": [p for p, a in pass_audits.items() if a.get("ct_only")],
            "passes_missing": [p for p, a in pass_audits.items() if a.get("output_missing")],
            "red_flags_count": len(red_flags),
        },
        "pass_audits": pass_audits,
        "frame_type_survival": frame_survival,
        "red_flags": red_flags,
    }


def print_summary(audit: dict[str, Any]) -> None:
    print(f"\n{'='*70}")
    print(f"Layer 2 synthesis audit — {audit['voice']}")
    print(f"{'='*70}")
    print(f"merge_dir:       {audit['merge_dir']}")
    print(f"generation_dir:  {audit['generation_dir']}")
    if audit.get("snapshot_path"):
        print(f"snapshot:        {audit['snapshot_path']}")
    print()

    # Per-pass summary table
    print(f"{'Pass':<25} {'chunks':<7} {'density':<10} {'vocab_recall':<14} {'cite_survival':<14}")
    print("-" * 70)
    for pass_name, a in audit["pass_audits"].items():
        if a.get("output_missing"):
            print(f"  {pass_name:<23} MISSING")
            continue
        if a.get("ct_only"):
            print(f"  {pass_name:<23} CT-only ({a.get('note', '')[:40]}...)")
            continue
        agg = a["aggregate"]
        print(
            f"  {pass_name:<23} "
            f"{len(a['chunks_consumed']):<7} "
            f"{agg['density_ratio']:<10} "
            f"{agg['avg_vocab_recall']:<14} "
            f"{agg['avg_citation_survival']:<14}"
        )

    # Frame-type survival
    frame = audit.get("frame_type_survival", {})
    if isinstance(frame, dict) and "_skipped" not in frame:
        print(f"\n{'-'*70}")
        print("Frame-type survival (1-arch-06)")
        print(f"{'-'*70}")
        for ft, data in frame.items():
            print(f"  {ft}: {data['frames_total']} frames total")
            for consumer, stats in data.get("by_consumer", {}).items():
                print(f"    → {consumer}: "
                      f"{stats['frames_present_in_output']}/{stats['frames_total']} "
                      f"({stats['rate']:.0%})")

    # Red flags
    red = audit.get("red_flags", [])
    if red:
        print(f"\n{'-'*70}")
        print(f"RED FLAGS ({len(red)}) — chunks with <15% vocab recall (silent drop?)")
        print(f"{'-'*70}")
        for flag in red:
            print(f"  [{flag['pass']}] {flag['chunk']}: "
                  f"recall={flag['vocab_recall']:.0%}, chunk_chars={flag['chunk_chars']:,}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Layer 2 preservation audit for 1-arch-03 additive merge (chunks → synthesis)."
    )
    parser.add_argument("--voice", required=True, help="Voice slug (e.g. fyodor_dostoevsky)")
    parser.add_argument("--project", default=None, help="Project root path")
    parser.add_argument(
        "--snapshot-path", default=None,
        help="Audit a snapshot directory instead of live 04_generation/ "
             "(path to snapshot dir or to <snapshot>/<voice>/)"
    )
    parser.add_argument(
        "--compare-snapshot", default=None,
        help="Run audit twice — live + snapshot — and print delta."
    )
    args = parser.parse_args()

    project_root = resolve_project_root(args.project)

    if args.compare_snapshot:
        print(">>> LIVE AUDIT")
        live = run_audit(args.voice, project_root, snapshot_path=None)
        print_summary(live)
        print("\n\n>>> SNAPSHOT AUDIT")
        snap = run_audit(args.voice, project_root, snapshot_path=Path(args.compare_snapshot))
        print_summary(snap)

        # Delta summary
        print(f"\n\n{'='*70}")
        print("DELTA (live − snapshot)")
        print(f"{'='*70}")
        for pass_name in PASS_CONSUMPTION:
            la = live["pass_audits"].get(pass_name, {})
            sa = snap["pass_audits"].get(pass_name, {})
            if "aggregate" not in la or "aggregate" not in sa:
                continue
            d_recall = la["aggregate"]["avg_vocab_recall"] - sa["aggregate"]["avg_vocab_recall"]
            d_cite = la["aggregate"]["avg_citation_survival"] - sa["aggregate"]["avg_citation_survival"]
            d_density = la["aggregate"]["density_ratio"] - sa["aggregate"]["density_ratio"]
            arrow = lambda d: "↑" if d > 0.005 else "↓" if d < -0.005 else "≈"
            print(f"  {pass_name:<25} "
                  f"recall {arrow(d_recall)}{abs(d_recall):+.3f}  "
                  f"cite {arrow(d_cite)}{abs(d_cite):+.3f}  "
                  f"density {arrow(d_density)}{abs(d_density):+.3f}")

        audit = live  # Save the live audit as the canonical output
    else:
        audit = run_audit(args.voice, project_root, snapshot_path=Path(args.snapshot_path) if args.snapshot_path else None)
        print_summary(audit)

    out_path = project_root / "voices" / args.voice / "_synthesis_audit.json"
    with open(out_path, "w") as f:
        json.dump(audit, f, indent=2)
    print(f"\nAudit written to: {out_path}")


if __name__ == "__main__":
    main()
