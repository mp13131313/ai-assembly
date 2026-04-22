"""Shared harness for the chunked Pass 1 merge passes (1.1-1.6).

Each chunk pass follows the same shape:

1. Load 3 source dossiers (Perplexity + Claude DR + Gemini) for a voice.
2. Render a 4-block merge prompt with inlined JSON Schemas.
3. Call Opus 4.7 streaming + adaptive thinking, max_tokens=32000.
4. Validate JSON output against per-chunk Pydantic models.
5. On ValidationError, retry once with the critique appended.
6. Atomically write per-chunk JSON outputs.

`run_chunk()` here holds all that machinery. Per-chunk runners
(`run_pass_1_N.py`) become thin wrappers specifying:

- `chunk_name` (e.g. "1.2", "1.3")
- `template_name` (the `.md` file under `flows/shared/prompts/`)
- `output_keys` — a dict mapping top-level JSON key → Pydantic model
  (used for validation + per-key atomic writes under
  `<project_root>/runs/<slug>/01_research/pass_<chunk>/<key>.json`).

Per Tier 3 code/project separation, `runs/` lives under `project_root`
(distinct from the code repo). `repo_root` is retained only for test
fixtures (`personas/tests/fixtures/...`), which are code-level.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any, Callable

import anthropic as _anthropic
import httpx as _httpx
import httpcore as _httpcore
from pydantic import BaseModel

from flows.shared import paths as _paths
from flows.shared import perplexity_split as _perp_split
from flows.shared.clients import call_claude
from flows.shared.io import voice_slug, write_json_atomic
from flows.shared.prompt_render import render
from schemas._entry import ValidationError, validate_chunk_output, generate_json_schemas


# Streaming calls can drop mid-response on transient network flakes — the
# peer closing the chunked connection before the JSON body completes surfaces
# as httpx.RemoteProtocolError (wrapping httpcore.RemoteProtocolError), which
# the anthropic SDK does not translate into its own APIError hierarchy. A
# single bounce on these is always the right move; they are independent of
# prompt content. See first Stage 1 run under arch-03 where Pass 1.4 died on
# "peer closed connection without sending complete message body".
_RETRYABLE = (
    RuntimeError,
    json.JSONDecodeError,
    _anthropic.APIError,
    _anthropic.RateLimitError,
    _httpx.RemoteProtocolError,
    _httpx.ReadError,
    _httpx.ConnectError,
    _httpx.ReadTimeout,
    _httpcore.RemoteProtocolError,
    _httpcore.ReadError,
    _httpcore.ConnectError,
    _httpcore.ReadTimeout,
)


def _stamp(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def detect_dr_mode(slug: str, project_root: Path) -> str:
    """Auto-detect per-section vs monolithic DR mode from filesystem state.

    Returns "per_section" if all 6 section files exist, "monolithic" if the
    concat file exists. Raises RuntimeError on partial state or no DR found.
    """
    section_files = [_paths.section_dr_dossier(slug, n, project_root) for n in range(1, 7)]
    monolithic = _paths.concat_claude_dr(slug, project_root)

    n_sections = sum(1 for p in section_files if p.exists())
    if n_sections == 6:
        return "per_section"
    if n_sections == 0 and monolithic.exists():
        return "monolithic"
    if n_sections > 0:
        missing = [n for n, p in enumerate(section_files, 1) if not p.exists()]
        raise RuntimeError(
            f"Partial DR state for {slug}: {n_sections}/6 section files present. "
            f"Missing: sections {missing}. Complete DR for these before running pipeline."
        )
    raise RuntimeError(
        f"No DR dossier found for {slug}. Expected either:\n"
        f"  (a) 6 section files at {_paths.dr_dossier_dir(slug, project_root)}/\n"
        f"  (b) monolithic at {monolithic}"
    )


def _load_sources(
    repo_root: Path,
    project_root: Path,
    slug: str,
    chunk_num: int,
    mode: str,
    use_test_fixtures: bool,
) -> tuple[str, str, str]:
    """Return (perplexity_text, claude_dr_text, gemini_text).

    Test fixtures: repo_root/tests/fixtures/<slug>/01_research/{perplexity,gemini,dr_dossier/}
    Live runs: project_root/voices/<slug>/01_research/{...} via paths module.

    Perplexity: split by section (chunk_num), fall back to full dossier if missing.
    Claude DR: per-section file if mode=per_section, monolithic concat if mode=monolithic.
    Gemini: always full (not sectioned — cross-cutting material by design).
    """
    if use_test_fixtures:
        res = repo_root / "tests/fixtures" / slug / "01_research"
        perp = json.loads((res / "01_perplexity_dossier.json").read_text())
        gem = json.loads((res / "02_gemini_broad_scan.json").read_text())
        dr_dossier = res / "04_dr_dossier"
        dr_candidates = sorted(dr_dossier.glob(f"*_section_{chunk_num}.md"))
        if dr_candidates:
            dr_text = dr_candidates[0].read_text(encoding="utf-8")
        else:
            dr_text = (
                f"[MOCK DR DOSSIER — fixtures mode, section {chunk_num}]\n\n"
                "Phase B test harness placeholder. Treat Perplexity + Gemini as primary "
                "grounding; flag missing material with evidence_tag=inference."
            )
    else:
        perp = json.loads(_paths.perplexity_dossier(slug, project_root).read_text())
        gem = json.loads(_paths.gemini_broad_scan(slug, project_root).read_text())
        if mode == "per_section":
            dr_path = _paths.section_dr_dossier(slug, chunk_num, project_root)
        else:
            dr_path = _paths.concat_claude_dr(slug, project_root)
        if not dr_path.exists():
            sys.exit(
                f"Missing Claude DR dossier at {dr_path}. Phase 0.5 + manual DR must "
                f"complete before Pass 1.{chunk_num} runs."
            )
        dr_text = dr_path.read_text(encoding="utf-8")

    perp_text_full = perp.get("text") or json.dumps(perp, ensure_ascii=False, indent=2)
    perp_sections = _perp_split.split_dossier(perp_text_full)
    perp_text = perp_sections.get(chunk_num, perp_text_full)  # fall back to full if missing
    gem_text = gem.get("text") or json.dumps(gem, ensure_ascii=False, indent=2)
    return perp_text, dr_text, gem_text


def _inline_schemas(output_keys: dict[str, type[BaseModel] | tuple[type[BaseModel], bool]]) -> dict[str, str]:
    """Return {schema_var_name: json_schema_string} for all unique chunk models.

    Regenerates generated/ files as a side effect.
    """
    import re
    generate_json_schemas()
    out: dict[str, str] = {}
    for key, spec in output_keys.items():
        model = spec[0] if isinstance(spec, tuple) else spec
        # Template vars follow convention `<model_name_snake>_schema`. E.g. LifeScaffold → life_scaffold_schema.
        # Acronym special case: ALL-CAPS + lowercase suffix (URLs → urls, not u_r_ls).
        cls_name = model.__name__
        if re.match(r'^[A-Z]{2,}[a-z]+$', cls_name):
            name = cls_name.lower()
        else:
            name = "".join("_" + c.lower() if c.isupper() else c for c in cls_name).lstrip("_")
        out[f"{name}_schema"] = json.dumps(
            model.model_json_schema(), indent=2, ensure_ascii=False
        )
    return out


def _validate(
    data: Any,
    output_keys: dict[str, type[BaseModel] | tuple[type[BaseModel], bool]],
) -> dict[str, Any]:
    """Validate the LLM output against output_keys. Spec is either:

    - a Pydantic class (single item output)
    - (Pydantic class, is_list: bool) — a list of items
    """
    if not isinstance(data, dict):
        raise ValidationError.from_exception_data(
            "chunk output", [{"type": "dict_type", "loc": (), "msg": "expected object", "input": data}]
        )
    missing = set(output_keys) - set(data.keys())
    if missing:
        raise ValidationError.from_exception_data(
            "chunk output",
            [{"type": "missing", "loc": tuple(missing), "msg": f"expected keys {sorted(output_keys)}", "input": data}],
        )
    validated: dict[str, Any] = {}
    for key, spec in output_keys.items():
        model, is_list = (spec, False) if not isinstance(spec, tuple) else spec
        value = data[key]
        if is_list:
            if not isinstance(value, list):
                raise ValidationError.from_exception_data(
                    "chunk output", [{"type": "list_type", "loc": (key,), "msg": f"{key} must be list", "input": value}]
                )
            validated[key] = [validate_chunk_output(model, item).model_dump() for item in value]
        else:
            validated[key] = validate_chunk_output(model, value).model_dump()
    return validated


def run_chunk(
    *,
    repo_root: Path,
    project_root: Path,
    chunk_name: str,  # e.g. "1.2"
    template_name: str,  # e.g. "pass_1_2_merge"
    name: str,
    voice_type: str = "human",
    subtype: str | None = None,
    voice_mode: str = "philosophical",
    output_keys: dict[str, type[BaseModel] | tuple[type[BaseModel], bool]],
    output_subdir: str | None = None,
    use_test_fixtures: bool = False,
    user_prompt: str | None = None,
    max_tokens: int = 48000,
    mode: str = "auto",  # "per_section", "monolithic", or "auto"
) -> dict[str, Any]:
    """Run a single chunked-merge pass end-to-end. Returns the validated dict.

    Under 1-arch-03 additive merge, per-chunk outputs are larger (preservation
    discipline). max_tokens default raised from 32000 → 48000 after Pass 1.1
    hit 32000 on rich Dostoevsky biographical output. Downstream chunks with
    smaller outputs still fit comfortably.
    """
    slug = voice_slug(name)
    chunk_num = int(chunk_name.split(".")[1])  # "1.2" → 2
    _stamp(f"Pass {chunk_name} merge: '{name}' (slug={slug}, fixtures={use_test_fixtures})")

    # Skip-if-already-run. When all per-key JSON outputs exist under the
    # chunk directory (from a prior successful run), load + validate them
    # from disk and return — no LLM call, no cost. This lets restarts after
    # transient failures (e.g. one chunk's streaming connection drops)
    # avoid re-running already-completed chunks. Delete the chunk's output
    # directory to force a re-run.
    out_dir_preview = _paths.merge_dir(slug, project_root) / (
        output_subdir or f"pass_{chunk_name.replace('.', '_')}"
    )
    existing_files = {k: out_dir_preview / f"{k}.json" for k in output_keys}
    if all(p.exists() for p in existing_files.values()):
        _stamp(f"  skip: all outputs present at {out_dir_preview.relative_to(project_root)}")
        cached = {k: json.loads(p.read_text()) for k, p in existing_files.items()}
        try:
            validated = _validate(cached, output_keys)
        except ValidationError as exc:
            _stamp(f"  cached outputs failed validation; re-running: {exc}")
        else:
            validated["_usage"] = {"input_tokens": 0, "output_tokens": 0, "cached": True}
            validated["_model"] = "cached"
            return validated

    if not use_test_fixtures and mode == "auto":
        mode = detect_dr_mode(slug, project_root)
        _stamp(f"  DR mode: {mode}")

    perp_text, dr_text, gem_text = _load_sources(
        repo_root, project_root, slug, chunk_num, mode, use_test_fixtures
    )
    schema_vars = _inline_schemas(output_keys)

    # Load voice_config for hostile_sources + corpus_constraint (referenced
    # by arch-03 pre-seed prompts 1.1, 1.5, 1.6). Fixtures mode: default
    # both to falsey/"full" since fixtures don't ship a voice_config.
    if use_test_fixtures:
        hostile_sources = False
        corpus_constraint = "full"
    else:
        vc_path = _paths.voice_config(slug, project_root)
        if vc_path.exists():
            vc = json.loads(vc_path.read_text())
            hostile_sources = bool(vc.get("hostile_sources", False))
            corpus_constraint = vc.get("corpus_constraint", "full") or "full"
        else:
            hostile_sources = False
            corpus_constraint = "full"

    system = render(
        template_name,
        name=name,
        type=voice_type,
        subtype=subtype,
        voice_mode=voice_mode,
        hostile_sources=hostile_sources,
        corpus_constraint=corpus_constraint,
        perplexity_dossier_text=perp_text,
        claude_dr_dossier_text=dr_text,
        gemini_broad_scan_text=gem_text,
        **schema_vars,
    )
    expected = ", ".join(f"`{k}`" for k in output_keys)
    user = user_prompt or (
        f"Produce the Pass {chunk_name} merge for the voice specified in the "
        f"system prompt. Return the single JSON object with keys {expected} "
        f"as described. JSON only — no preamble, no markdown fences."
    )

    call_kwargs = dict(
        system=system,
        model="claude-opus-4-7",
        max_tokens=max_tokens,
        temperature=1.0,
        thinking=True,
        response_format_json=True,
    )

    def _call_and_validate(user_msg: str) -> dict[str, Any]:
        r = call_claude(user=user_msg, **call_kwargs)
        _stamp(
            f"  tokens in={r['usage']['input_tokens']} out={r['usage']['output_tokens']} "
            f"model={r.get('model','?')}"
        )
        validated = _validate(r["json"], output_keys)
        validated["_usage"] = r["usage"]
        validated["_model"] = r.get("model")
        return validated

    try:
        result = _call_and_validate(user)
    except ValidationError as exc:
        _stamp(f"  VALIDATION FAIL on attempt 1; retrying with critique…")
        critique = (
            "\n\nYour previous response failed Pydantic validation. Critique:\n"
            f"{exc}\n\nFix the schema mismatch and return valid JSON only."
        )
        try:
            result = _call_and_validate(user + critique)
        except ValidationError as exc2:
            sys.exit(f"Pass {chunk_name} failed after retry: {exc2}")
    except _RETRYABLE as exc:
        _stamp(f"  Retryable error on attempt 1 ({exc}); retrying in 15 s…")
        time.sleep(15)
        try:
            result = _call_and_validate(user)
        except _RETRYABLE as exc2:
            sys.exit(f"Pass {chunk_name} failed after retry: {exc2}")

    out_dir = _paths.merge_dir(slug, project_root) / (output_subdir or f"pass_{chunk_name.replace('.', '_')}")
    out_dir.mkdir(parents=True, exist_ok=True)
    for key in output_keys:
        write_json_atomic(out_dir / f"{key}.json", result[key])
    _stamp(f"  Wrote {', '.join(f'{k}.json' for k in output_keys)} under {out_dir.relative_to(project_root)}")
    return result
