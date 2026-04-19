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
  `runs/<slug>/01_research/pass_<chunk>/<key>.json`).
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any, Callable

import anthropic as _anthropic
from pydantic import BaseModel

from flows.shared.clients import call_claude
from flows.shared.io import voice_slug, write_json_atomic
from flows.shared.prompt_render import render
from schemas._entry import ValidationError, validate_chunk_output, generate_json_schemas


_RETRYABLE = (RuntimeError, json.JSONDecodeError, _anthropic.APIError, _anthropic.RateLimitError)


def _stamp(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def _load_sources(repo_root: Path, slug: str, use_test_fixtures: bool) -> tuple[str, str, str]:
    """Return (perplexity_text, claude_dr_text, gemini_text)."""
    if use_test_fixtures:
        fixtures = repo_root / "tests/fixtures" / slug
        perp = json.loads((fixtures / "perplexity_dossier.json").read_text())
        gem = json.loads((fixtures / "gemini_broad_scan.json").read_text())
        dr_text = (
            "[MOCK DEEP RESEARCH DOSSIER — fixtures mode.]\n\n"
            "Phase B test harness placeholder. Merge mechanics are exercised; "
            "Boddice-shape content depends on a real DR dossier and lands in "
            "Phase L. Treat Perplexity + Gemini as primary grounding; flag any "
            "field a real DR dossier would supply with evidence_tag=inference."
        )
    else:
        research = repo_root / "runs" / slug / "01_research"
        perp = json.loads((research / "perplexity_dossier.json").read_text())
        gem = json.loads((research / "gemini_broad_scan.json").read_text())
        dr_path = research / "claude_dr_dossier.md"
        if not dr_path.exists():
            sys.exit(
                f"Missing Claude DR dossier at {dr_path}. Phase 0.5 must complete "
                f"+ human must paste the claude.ai output before Pass {slug} chunk runs."
            )
        dr_text = dr_path.read_text()
    perp_text = perp.get("text") or json.dumps(perp, ensure_ascii=False, indent=2)
    gem_text = gem.get("text") or json.dumps(gem, ensure_ascii=False, indent=2)
    return perp_text, dr_text, gem_text


def _inline_schemas(output_keys: dict[str, type[BaseModel] | tuple[type[BaseModel], bool]]) -> dict[str, str]:
    """Return {schema_var_name: json_schema_string} for all unique chunk models.

    Regenerates generated/ files as a side effect.
    """
    generate_json_schemas()
    out: dict[str, str] = {}
    for key, spec in output_keys.items():
        model = spec[0] if isinstance(spec, tuple) else spec
        # Template vars follow convention `<model_name_snake>_schema`. E.g. LifeScaffold → life_scaffold_schema.
        name = "".join("_" + c.lower() if c.isupper() else c for c in model.__name__).lstrip("_")
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
    max_tokens: int = 32000,
) -> dict[str, Any]:
    """Run a single chunked-merge pass end-to-end. Returns the validated dict."""
    slug = voice_slug(name)
    _stamp(f"Pass {chunk_name} merge: '{name}' (slug={slug}, fixtures={use_test_fixtures})")

    perp_text, dr_text, gem_text = _load_sources(repo_root, slug, use_test_fixtures)
    schema_vars = _inline_schemas(output_keys)

    system = render(
        template_name,
        name=name,
        type=voice_type,
        subtype=subtype,
        voice_mode=voice_mode,
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

    out_dir = repo_root / "runs" / slug / "01_research" / (output_subdir or f"pass_{chunk_name.replace('.', '_')}")
    out_dir.mkdir(parents=True, exist_ok=True)
    for key in output_keys:
        write_json_atomic(out_dir / f"{key}.json", result[key])
    _stamp(f"  Wrote {', '.join(f'{k}.json' for k in output_keys)} under {out_dir.relative_to(repo_root)}")
    return result
