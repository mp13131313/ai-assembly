"""Pass 1.7 COHERENCE — offline-compose + narrow LLM audit + Python edits-to-chunks.

Under 1-arch-03 (2026-04-22 split amendment) + 1-arch-05 (2026-04-23 edits-
to-chunks amendment), Pass 1.7 has three stages:

    Stage A (Python): load the 6 chunk outputs and assemble them into a
        MergedDossier-shaped dict (in-memory only). Zero LLM. Pydantic-
        validate before the LLM sees anything.

    Stage B (LLM, narrow output): send the composed dossier + 9 coherence
        checks + edit-scope discipline. Expect only a `CoherenceAuditResult`
        — flags + resolutions + a list of targeted edits. The LLM never
        re-emits the dossier; max_tokens=24000.

    Stage C (Python): route each edit to its owning chunk file under
        02_merge/pass_1_N/<key>.json; apply append/set op; re-validate
        chunk against its Pydantic model; atomic write back. Chunk files
        are the SOURCE OF TRUTH under 1-arch-05. Coherence metadata writes
        to a separate 02_merge/_coherence_audit.json file. Merged dossier
        snapshot 02_merge/08_merged_dossier.json is rebuilt from post-edit
        chunk files (convenience artifact for human review; not consumed
        as authoritative by downstream passes once Pass 2-6 migrates to
        per-chunk reads per 1-arch-05 Part A).

Architectural invariants under 1-arch-05:
- pass_1_N/<key>.json files ARE the source of truth end-to-end
- Pass 1.7 edits change those files (not just the composed in-memory copy)
- _coherence_audit.json holds flags + resolutions as a separate artifact
- 08_merged_dossier.json is a snapshot rebuilt from chunks post-edit
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

# Chunk models for edit routing + re-validation (1-arch-05 Part B).
from schemas._frames import InterpretiveFrame
from schemas._analytical import AnalyticalContext
from schemas.pass_1_1 import FormativeCandidate, LifeScaffold
from schemas.pass_1_2 import Commitment, Concept, Tension
from schemas.pass_1_3 import ReasoningMethod, Textures
from schemas.pass_1_4 import Moves, Register, Vocabulary
from schemas.pass_1_5 import HardLimits, KnowledgeBoundary, SensitiveTopics
from schemas.pass_1_6 import Passages, ReferenceOnlyPassages, Works


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
        "pass_1_2": ["commitments", "concepts", "tensions", "interpretive_frames"],
        "pass_1_3": ["reasoning_method", "textures", "analytical_context_reasoning"],
        "pass_1_4": ["moves", "register", "vocabulary", "analytical_context_voice"],
        "pass_1_5": ["knowledge_boundary", "sensitive_topics", "hard_limits"],
        "pass_1_6": ["works", "passages", "reference_only_passages"],
    }
    # Optional keys: sensible defaults when chunk didn't populate.
    # - reference_only_passages: empty for public-domain corpora (Plato, Whanganui)
    # - analytical_context_reasoning: empty for thinly-documented voices
    # - analytical_context_voice: null for voices without voice-level scholarly material
    optional_keys = {
        "reference_only_passages",
        "analytical_context_reasoning",
        "analytical_context_voice",
        "interpretive_frames",  # 1-arch-06: empty for thinly-documented voices
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
                    elif key == "interpretive_frames":
                        out[key] = []  # default empty list
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
        # 1-arch-06: new top-level container for cross-cutting scholarly material
        "interpretive_frames": chunks.get("interpretive_frames", []),
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
        # Chunk 1.6 — CORPUS (`urls` removed per 1-arch-07; derived at render-time)
        "works": chunks["works"],
        "passages": chunks["passages"],
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
    """Apply one edit in-place on the in-memory composed dict.

    DEPRECATED under 1-arch-05 Part B (2026-04-23). Retained for fallback
    testing + migration; production Stage C uses `_route_edit_to_chunk_file`
    which writes to chunk files (source of truth) rather than the composed
    copy.
    """
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


# ── 1-arch-05 Part B: chunk-file routing for Stage C edits ────────────────────
#
# Each chunk-key maps to (chunk_dir, filename, Pydantic model, is_list). On
# an edit with path like "commitments[3].operational_note":
#   1. Parse full path: ["commitments", 3, "operational_note"]
#   2. First token "commitments" is chunk_key → route to pass_1_2/commitments.json
#   3. Remaining tokens [3, "operational_note"] are the within-chunk path
#   4. Load chunk file (which is a list because is_list=True for commitments)
#   5. Apply op at within-chunk path
#   6. Re-validate chunk against Commitment (per-item, since is_list=True)
#   7. Atomic write back
#
# Special cases handled by callers:
#   - edit.path="commitments" with op="append" → within-chunk path is empty,
#     target IS the file's root list
#   - edit.path="life_scaffold.available_pathe" with op="append" → within-chunk
#     path is ["available_pathe"], target is the nested list
#   - edits targeting coherence_flags/coherence_resolutions are NOT routed to
#     chunk files (those live in _coherence_audit.json now) — caller skips them

# chunk_key → (chunk_dir_name, filename, pydantic_model, is_list)
_CHUNK_ROUTING: dict[str, tuple[str, str, type, bool]] = {
    # Chunk 1.1 — BIOGRAPHICAL
    "life_scaffold":                 ("pass_1_1", "life_scaffold.json",                 LifeScaffold,       False),
    "formative_candidates":          ("pass_1_1", "formative_candidates.json",          FormativeCandidate, True),
    # Chunk 1.2 — INTELLECTUAL
    "commitments":                   ("pass_1_2", "commitments.json",                   Commitment,         True),
    "concepts":                      ("pass_1_2", "concepts.json",                      Concept,            True),
    "tensions":                      ("pass_1_2", "tensions.json",                      Tension,            True),
    "interpretive_frames":           ("pass_1_2", "interpretive_frames.json",           InterpretiveFrame,  True),
    # Chunk 1.3 — REASONING
    "reasoning_method":              ("pass_1_3", "reasoning_method.json",              ReasoningMethod,    False),
    "textures":                      ("pass_1_3", "textures.json",                      Textures,           False),
    "analytical_context_reasoning":  ("pass_1_3", "analytical_context_reasoning.json",  AnalyticalContext,  False),
    # Chunk 1.4 — VOICE
    "moves":                         ("pass_1_4", "moves.json",                         Moves,              False),
    "register":                      ("pass_1_4", "register.json",                      Register,           False),
    "vocabulary":                    ("pass_1_4", "vocabulary.json",                    Vocabulary,         False),
    "analytical_context_voice":      ("pass_1_4", "analytical_context_voice.json",      AnalyticalContext,  False),
    # Chunk 1.5 — BOUNDARIES
    "knowledge_boundary":            ("pass_1_5", "knowledge_boundary.json",            KnowledgeBoundary,  False),
    "sensitive_topics":              ("pass_1_5", "sensitive_topics.json",              SensitiveTopics,    False),
    "hard_limits":                   ("pass_1_5", "hard_limits.json",                   HardLimits,         False),
    # Chunk 1.6 — CORPUS (urls removed per 1-arch-07)
    "works":                         ("pass_1_6", "works.json",                         Works,              False),
    "passages":                      ("pass_1_6", "passages.json",                      Passages,           False),
    "reference_only_passages":       ("pass_1_6", "reference_only_passages.json",       ReferenceOnlyPassages, False),
}

# Edit paths starting with these keys are NOT routed to chunk files; they
# belong in _coherence_audit.json and are handled separately by the caller.
_COHERENCE_METADATA_KEYS = {"coherence_flags", "coherence_resolutions"}


def _apply_edit_to_chunk_data(chunk_data: Any, within_tokens: list[str | int],
                               op: str, value: Any) -> Any:
    """Apply one edit within a single chunk file's data structure (in-memory).

    `chunk_data` is the loaded JSON of the chunk file. For is_list=True
    chunks, it's a list at root; for is_list=False, it's a dict.
    `within_tokens` is the path relative to the chunk's root (after
    stripping the chunk_key root token).

    Returns the (possibly unchanged-reference) chunk_data post-edit.
    """
    if op == "append":
        target = _resolve(chunk_data, within_tokens) if within_tokens else chunk_data
        if not isinstance(target, list):
            raise ValueError(
                f"append requires list target; within-chunk path resolved to "
                f"{type(target).__name__}"
            )
        target.append(value)
    elif op == "set":
        if not within_tokens:
            raise ValueError(
                "set requires non-empty within-chunk path (can't replace the "
                "entire chunk file root via a single edit)"
            )
        parent = _resolve(chunk_data, within_tokens[:-1]) if len(within_tokens) > 1 else chunk_data
        key = within_tokens[-1]
        parent[key] = value
    else:  # pragma: no cover — Literal constrains op
        raise ValueError(f"Unknown edit op: {op!r}")
    return chunk_data


def _route_edit_to_chunk_file(edit: DossierEdit, project_root: Path, slug: str) -> str:
    """Route one edit to its owning chunk file; apply; re-validate; atomic write.

    Returns a short description of what was modified (for logging). Raises
    on: unknown chunk_key, coherence_metadata_key (caller should filter),
    chunk file missing, apply failure, post-edit Pydantic validation
    failure.

    Under 1-arch-05 Part B (2026-04-23): this is the production path that
    makes chunk files the source of truth. Edits to the in-memory composed
    copy (legacy _apply_edit) are no longer used at Stage C.
    """
    tokens = _parse_path(edit.path)
    if not tokens or not isinstance(tokens[0], str):
        raise ValueError(
            f"edit path must start with a chunk-key string; got {edit.path!r}"
        )
    chunk_key = tokens[0]

    if chunk_key in _COHERENCE_METADATA_KEYS:
        raise ValueError(
            f"edit targets coherence metadata '{chunk_key}' — these live in "
            f"_coherence_audit.json, not chunk files. Caller should filter."
        )
    if chunk_key not in _CHUNK_ROUTING:
        raise ValueError(
            f"unknown chunk key '{chunk_key}' in path {edit.path!r}. "
            f"Known keys: {sorted(_CHUNK_ROUTING)}"
        )

    chunk_dir_name, filename, model, is_list = _CHUNK_ROUTING[chunk_key]
    chunk_file = _paths.merge_dir(slug, project_root) / chunk_dir_name / filename

    if not chunk_file.exists():
        raise FileNotFoundError(
            f"chunk file not found: {chunk_file}. Run Pass "
            f"{chunk_dir_name.replace('pass_', '').replace('_', '.')} first."
        )

    within_tokens = tokens[1:]
    chunk_data = json.loads(chunk_file.read_text())
    chunk_data = _apply_edit_to_chunk_data(chunk_data, within_tokens, edit.op, edit.value)

    # Re-validate post-edit against the chunk's Pydantic model. For is_list=True
    # chunks, validate each item; for is_list=False, validate the whole dict.
    if is_list:
        if not isinstance(chunk_data, list):
            raise ValueError(
                f"post-edit chunk data for {chunk_key} is not a list "
                f"(is_list=True expected); got {type(chunk_data).__name__}"
            )
        validated_items = [validate_chunk_output(model, item).model_dump() for item in chunk_data]
        chunk_data_normalized = validated_items
    else:
        if not isinstance(chunk_data, dict):
            raise ValueError(
                f"post-edit chunk data for {chunk_key} is not a dict "
                f"(is_list=False expected); got {type(chunk_data).__name__}"
            )
        chunk_data_normalized = validate_chunk_output(model, chunk_data).model_dump()

    # Atomic write — chunk file IS the source of truth under 1-arch-05 Part B.
    write_json_atomic(chunk_file, chunk_data_normalized)

    return f"{chunk_dir_name}/{filename} ({edit.op} @ {edit.path})"


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

    # ── Stage C (1-arch-05 Part B, 2026-04-23) ──
    # Edits route to chunk files (source of truth). Coherence metadata writes
    # to separate _coherence_audit.json. Merged dossier is rebuilt from
    # post-edit chunks as a convenience snapshot.

    applied = 0
    skipped: list[tuple[int, str]] = []
    edit_log: list[str] = []
    for i, edit in enumerate(audit.edits):
        # Coherence-metadata edits are not applied to chunk files; the LLM
        # shouldn't emit them (its schema gives flags/resolutions separately),
        # but defensive skip in case it does.
        first_token = _parse_path(edit.path)[0] if edit.path else None
        if first_token in _COHERENCE_METADATA_KEYS:
            skipped.append((i, f"{edit.op} {edit.path}: targets coherence metadata "
                              f"— skip (flags/resolutions are audit-result, not edit-target)"))
            continue
        try:
            desc = _route_edit_to_chunk_file(edit, project_root, slug)
            edit_log.append(desc)
            applied += 1
        except (KeyError, IndexError, ValueError, TypeError, FileNotFoundError) as exc:
            skipped.append((i, f"{edit.op} {edit.path}: {exc}"))
        except ValidationError as exc:
            skipped.append((i, f"{edit.op} {edit.path}: post-edit chunk validation failed: {exc}"))

    _stamp(f"  Stage C: applied {applied}/{len(audit.edits)} edits to chunk files")
    for desc in edit_log:
        _stamp(f"    → {desc}")
    if skipped:
        _stamp(f"  {len(skipped)} edits skipped:")
        for idx, reason in skipped:
            _stamp(f"    edit[{idx}]: {reason}")

    # Write coherence metadata to its own file (1-arch-05 Part B).
    coherence_audit_path = _paths.merge_dir(slug, project_root) / "_coherence_audit.json"
    coherence_audit_data = {
        "voice_name": name,
        "voice_slug": slug,
        "coherence_flags": [f.model_dump() for f in audit.coherence_flags],
        "coherence_resolutions": [r.model_dump() for r in audit.coherence_resolutions],
        "edits_applied": applied,
        "edits_skipped": len(skipped),
        "edit_log": edit_log,
    }
    write_json_atomic(coherence_audit_path, coherence_audit_data)
    _stamp(f"  _coherence_audit.json written: {coherence_audit_path.relative_to(project_root)}")

    # Rebuild merged_dossier.json as convenience snapshot from POST-EDIT chunks.
    # Under 1-arch-05 Part A, downstream Pass 2-6 will read chunk files directly;
    # until Part A lands, they still render {{ merged_dossier }} → the snapshot
    # must reflect post-edit state so behavior is unchanged.
    chunks_post_edit = _load_chunk_outputs(project_root, slug)
    composed_post_edit = _compose_dossier(chunks_post_edit)
    # Attach coherence metadata to the snapshot (not the chunk files).
    composed_post_edit["coherence_flags"] = coherence_audit_data["coherence_flags"]
    composed_post_edit["coherence_resolutions"] = coherence_audit_data["coherence_resolutions"]
    try:
        final = MergedDossier.model_validate(composed_post_edit).model_dump(by_alias=True)
    except ValidationError as exc:
        sys.exit(
            f"Post-edit merged_dossier snapshot failed MergedDossier validation "
            f"(edits corrupted chunk files? each chunk passed its own Pydantic "
            f"re-validate but composed form fails):\n{exc}"
        )

    out_path = _paths.merged_dossier(slug, project_root)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    write_json_atomic(out_path, final)
    _stamp(
        f"  merged_dossier snapshot written ({len(json.dumps(final, ensure_ascii=False))} chars) "
        f"— rebuilt from post-edit chunks; chunks are source of truth (1-arch-05 Part B)"
    )
    return final


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Pass 1.7 COHERENCE")
    p.add_argument("name")
    add_project_arg(p)
    args = p.parse_args()
    run_pass_1_7(name=args.name, project=args.project)
