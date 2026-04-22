"""Pass 1.7 COHERENCE — offline-compose + narrow LLM audit + Python edit apply.

Under 1-arch-03 (as of 2026-04-22 amendment), Pass 1.7 is split into three
stages. Pass 1.1-1.6 have already done the additive cross-source merge;
Pass 1.7's remaining job — composition + coherence audit — separates cleanly
into a deterministic step and a judgment step:

    Stage A (Python): load the 6 chunk outputs and assemble them into a
        MergedDossier-shaped dict. Zero LLM, zero re-compression risk.
        Pydantic-validate before the LLM sees anything.

    Stage B (LLM, narrow output): send the composed dossier + 9 coherence
        checks + edit-scope discipline. Expect only a
        `CoherenceAuditResult` — flags + resolutions + a list of targeted
        edits. The LLM never re-emits the dossier; max_tokens drops from
        100000 to 24000 because the output is small.

    Stage C (Python): apply edits to the composed dict, attach flags +
        resolutions, re-validate against MergedDossier, write.

This replaces the prior shape where Pass 1.7 was a single ~100K-output
Opus call that re-emitted the entire MergedDossier. That shape relied on
prompt-level "edit-scope discipline" to prevent the LLM from re-compressing
what Pass 1.1-1.6 had preserved; the split architecture removes the
surface entirely by keeping composition out of the LLM.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path
from typing import Any, Literal

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))

from dotenv import load_dotenv
load_dotenv(REPO_ROOT.parent / ".env", override=True)

import anthropic as _anthropic
from pydantic import BaseModel, Field

from flows.shared import paths as _paths
from flows.shared.clients import call_claude
from flows.shared.io import voice_slug, write_json_atomic
from flows.shared.project_root import add_project_arg, resolve_project_root
from flows.shared.prompt_render import render
from schemas._entry import ValidationError, validate_chunk_output, generate_json_schemas
from schemas.merged_dossier import CoherenceFlag, CoherenceResolution, MergedDossier


_RETRYABLE = (RuntimeError, json.JSONDecodeError, _anthropic.APIError, _anthropic.RateLimitError)


def _stamp(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


# ── Stage A: load chunks + offline compose ────────────────────────────────────

def _load_chunk_outputs(project_root: Path, slug: str) -> dict:
    """Load the 6 chunk outputs written by Passes 1.1-1.6.

    Returns a flat dict keyed by chunk-output name (life_scaffold,
    formative_candidates, ..., reference_only_passages) — matches the
    top-level MergedDossier field layout (modulo the register↔voice_register
    alias, which Pydantic handles via populate_by_name).
    """
    base = _paths.merge_dir(slug, project_root)
    out: dict = {}
    layout = {
        "pass_1_1": ["life_scaffold", "formative_candidates"],
        "pass_1_2": ["commitments", "concepts", "tensions"],
        "pass_1_3": ["reasoning_method", "textures", "analytical_context_reasoning"],
        "pass_1_4": ["moves", "register", "vocabulary", "analytical_context_voice"],
        "pass_1_5": ["knowledge_boundary", "sensitive_topics", "hard_limits"],
        "pass_1_6": ["works", "passages", "urls", "reference_only_passages"],
    }
    # Optional keys: sensible defaults when chunk didn't populate.
    # - reference_only_passages: empty for public-domain corpora (Plato, Whanganui)
    # - analytical_context_reasoning: empty for thinly-documented voices
    # - analytical_context_voice: null for voices without voice-level scholarly material
    optional_keys = {
        "reference_only_passages",
        "analytical_context_reasoning",
        "analytical_context_voice",
    }
    for chunk_dir, keys in layout.items():
        for key in keys:
            path = base / chunk_dir / f"{key}.json"
            if not path.exists():
                if key in optional_keys:
                    if key == "reference_only_passages":
                        out[key] = {"passages": []}
                    elif key == "analytical_context_reasoning":
                        out[key] = {
                            "structural_patterns": [],
                            "worked_demonstrations": [],
                            "scholarly_debates": [],
                        }
                    elif key == "analytical_context_voice":
                        out[key] = None
                    continue
                sys.exit(
                    f"Missing chunk output {path}. Run Pass "
                    f"{chunk_dir.replace('pass_','').replace('_','.')} first."
                )
            out[key] = json.loads(path.read_text())
    return out


def _compose_dossier(chunks: dict[str, Any]) -> dict[str, Any]:
    """Pure dict-assembly: build a MergedDossier-shaped dict.

    Pass 1.1-1.6 already performed the cross-source additive merge. This
    step just glues the six chunk outputs into one object under the
    top-level MergedDossier layout, with empty coherence metadata ready
    for Stage B to populate.

    No LLM. No semantic work. No re-compression can happen here.
    """
    return {
        # Chunk 1.1 — BIOGRAPHICAL
        "life_scaffold": chunks["life_scaffold"],
        "formative_candidates": chunks["formative_candidates"],
        # Chunk 1.2 — INTELLECTUAL
        "commitments": chunks["commitments"],
        "concepts": chunks["concepts"],
        "tensions": chunks["tensions"],
        # Chunk 1.3 — REASONING
        "reasoning_method": chunks["reasoning_method"],
        "textures": chunks["textures"],
        "analytical_context_reasoning": chunks["analytical_context_reasoning"],
        # Chunk 1.4 — VOICE (JSON key stays "register" per MergedDossier alias)
        "moves": chunks["moves"],
        "register": chunks["register"],
        "vocabulary": chunks["vocabulary"],
        "analytical_context_voice": chunks["analytical_context_voice"],
        # Chunk 1.5 — BOUNDARIES
        "knowledge_boundary": chunks["knowledge_boundary"],
        "sensitive_topics": chunks["sensitive_topics"],
        "hard_limits": chunks["hard_limits"],
        # Chunk 1.6 — CORPUS
        "works": chunks["works"],
        "passages": chunks["passages"],
        "urls": chunks["urls"],
        "reference_only_passages": chunks["reference_only_passages"],
        # Pass 1.7 coherence metadata — populated by Stage B/C.
        "coherence_flags": [],
        "coherence_resolutions": [],
    }


# ── Stage B/C: audit-result schema + edit application ─────────────────────────

class DossierEdit(BaseModel):
    """One edit emitted by the LLM audit, applied in Python at Stage C.

    Kept intentionally narrow: only `append` (to a list) and `set` (at a
    scalar/field path). Any cross-chunk reconciliation that needs more
    than these two ops should be escalated, not inlined — that is the
    edit-scope discipline from plan §5 (1.7-02).
    """

    op: Literal["append", "set"] = Field(
        ...,
        description="`append` appends `value` to the list at `path`. "
        "`set` assigns `value` at `path` (scalar or sub-object).",
    )
    path: str = Field(
        ...,
        description="Dot+bracket path into the composed dossier, e.g. "
        "`concepts` (for append) or `commitments[3].operational_note` "
        "(for set). Indices are 0-based.",
    )
    value: Any = Field(
        None,
        description="Value to append/set. For append to a typed list, must "
        "satisfy the item's schema.",
    )
    note: str | None = Field(
        None,
        description="Optional one-line explanation of why this edit is "
        "safe within 1.7-02 edit-scope discipline. Not applied, just logged.",
    )


class CoherenceAuditResult(BaseModel):
    """Narrow output of Stage B. Python applies `edits` to the composed dossier."""

    coherence_flags: list[CoherenceFlag] = Field(default_factory=list)
    coherence_resolutions: list[CoherenceResolution] = Field(default_factory=list)
    edits: list[DossierEdit] = Field(default_factory=list)


_PATH_TOKEN = re.compile(r"([a-zA-Z_][a-zA-Z0-9_]*)|\[(\d+)\]")


def _parse_path(path: str) -> list[str | int]:
    """'commitments[3].operational_note' → ['commitments', 3, 'operational_note']."""
    tokens: list[str | int] = []
    pos = 0
    while pos < len(path):
        if path[pos] == ".":
            pos += 1
            continue
        m = _PATH_TOKEN.match(path, pos)
        if not m:
            raise ValueError(f"Invalid path syntax at pos {pos}: {path!r}")
        if m.group(1) is not None:
            tokens.append(m.group(1))
        else:
            tokens.append(int(m.group(2)))
        pos = m.end()
    if not tokens:
        raise ValueError(f"Empty path: {path!r}")
    return tokens


def _resolve(obj: Any, tokens: list[str | int]) -> Any:
    for t in tokens:
        obj = obj[t]
    return obj


def _apply_edit(dossier: dict[str, Any], edit: DossierEdit) -> None:
    """Apply one edit in-place. Raises on invalid path / wrong op-to-type."""
    tokens = _parse_path(edit.path)
    if edit.op == "append":
        target = _resolve(dossier, tokens)
        if not isinstance(target, list):
            raise ValueError(
                f"append requires list target; {edit.path} resolved to "
                f"{type(target).__name__}"
            )
        target.append(edit.value)
    elif edit.op == "set":
        parent = _resolve(dossier, tokens[:-1]) if len(tokens) > 1 else dossier
        key = tokens[-1]
        parent[key] = edit.value
    else:  # pragma: no cover — Literal constrains op
        raise ValueError(f"Unknown edit op: {edit.op!r}")


# ── Orchestration ─────────────────────────────────────────────────────────────

def run_pass_1_7(*, name: str, project_root: Path | None = None,
                  project: str | None = None) -> dict:
    slug = voice_slug(name)
    _stamp(f"Pass 1.7 COHERENCE: '{name}' (slug={slug})")

    if project_root is None:
        project_root = resolve_project_root(project, repo_root=REPO_ROOT)

    # Stage A.1 — load 6 chunks
    chunks = _load_chunk_outputs(project_root, slug)

    # Stage A.2 — offline compose (Python, deterministic)
    composed = _compose_dossier(chunks)
    composed_json = json.dumps(composed, ensure_ascii=False, indent=2)
    _stamp(f"  composed dossier: {len(composed_json)} chars pre-audit")

    # Stage A.3 — Pydantic-validate composed before LLM sees it.
    # Catches schema drift from Pass 1.1-1.6 early; LLM never audits
    # an invalid dossier.
    generate_json_schemas()
    try:
        composed_model = MergedDossier.model_validate(composed)
    except ValidationError as exc:
        sys.exit(
            f"Composed dossier failed MergedDossier validation (Pass 1.1-1.6 "
            f"schema drift):\n{exc}"
        )
    # Re-serialize via model_dump(by_alias=True) so the dossier the LLM
    # sees matches the wire shape downstream consumers will read.
    composed = composed_model.model_dump(by_alias=True)
    composed_json = json.dumps(composed, ensure_ascii=False, indent=2)

    # Stage B — LLM coherence audit (narrow output)
    audit_schema = json.dumps(
        CoherenceAuditResult.model_json_schema(), indent=2, ensure_ascii=False
    )
    system = render(
        "pass_1_7_coherence",
        name=name,
        composed_dossier_json=composed_json,
        audit_result_schema=audit_schema,
    )
    user = (
        "Run the 9 cross-chunk coherence checks on the composed "
        "merged_dossier. Emit a CoherenceAuditResult JSON with keys "
        "`coherence_flags`, `coherence_resolutions`, `edits`. Do NOT "
        "re-emit the dossier — only your audit output. JSON only, no "
        "preamble, no markdown fences."
    )

    # max_tokens drops from 100000 to 24000: output is audit-only, not
    # full dossier re-emit. 24K gives ample headroom for flag-heavy voices
    # while keeping streaming time modest.
    call_kwargs = dict(
        system=system,
        model="claude-opus-4-7",
        max_tokens=24000,
        temperature=1.0,
        thinking=True,
        response_format_json=True,
    )

    def _call_audit(user_msg: str) -> CoherenceAuditResult:
        r = call_claude(user=user_msg, **call_kwargs)
        _stamp(
            f"  tokens in={r['usage']['input_tokens']} "
            f"out={r['usage']['output_tokens']} model={r.get('model','?')}"
        )
        return validate_chunk_output(CoherenceAuditResult, r["json"])

    try:
        audit = _call_audit(user)
    except ValidationError as exc:
        _stamp("  VALIDATION FAIL on attempt 1; retrying with critique…")
        critique = (
            f"\n\nYour previous response failed CoherenceAuditResult validation:\n"
            f"{exc}\n\nFix and return valid JSON only."
        )
        try:
            audit = _call_audit(user + critique)
        except ValidationError as exc2:
            sys.exit(f"Pass 1.7 audit failed after retry: {exc2}")
    except _RETRYABLE as exc:
        _stamp(f"  Retryable error ({exc}); retrying in 15 s…")
        time.sleep(15)
        audit = _call_audit(user)

    _stamp(
        f"  audit: flags={len(audit.coherence_flags)} "
        f"resolutions={len(audit.coherence_resolutions)} "
        f"edits={len(audit.edits)}"
    )

    # Stage C — apply edits in Python. Skipped edits are logged, not fatal:
    # the dossier stays valid via the final re-validation below.
    applied = 0
    skipped: list[tuple[int, str]] = []
    for i, edit in enumerate(audit.edits):
        try:
            _apply_edit(composed, edit)
            applied += 1
        except (KeyError, IndexError, ValueError, TypeError) as exc:
            skipped.append((i, f"{edit.op} {edit.path}: {exc}"))
    if skipped:
        _stamp(f"  applied {applied}/{len(audit.edits)} edits; {len(skipped)} skipped:")
        for idx, reason in skipped:
            _stamp(f"    edit[{idx}]: {reason}")

    # Attach coherence metadata.
    composed["coherence_flags"] = [f.model_dump() for f in audit.coherence_flags]
    composed["coherence_resolutions"] = [r.model_dump() for r in audit.coherence_resolutions]

    # Re-validate — edits must leave the dossier schema-valid.
    try:
        final = MergedDossier.model_validate(composed).model_dump(by_alias=True)
    except ValidationError as exc:
        sys.exit(
            f"Post-edit merged_dossier failed validation (LLM emitted an "
            f"edit that breaks the schema):\n{exc}"
        )

    # Write.
    out_path = _paths.merged_dossier(slug, project_root)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    write_json_atomic(out_path, final)
    _stamp(
        f"  merged_dossier written ({len(json.dumps(final, ensure_ascii=False))} chars). "
        f"coherence_flags={len(final.get('coherence_flags', []))} "
        f"coherence_resolutions={len(final.get('coherence_resolutions', []))}"
    )
    return final


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Pass 1.7 COHERENCE")
    p.add_argument("name")
    add_project_arg(p)
    args = p.parse_args()
    run_pass_1_7(name=args.name, project=args.project)
