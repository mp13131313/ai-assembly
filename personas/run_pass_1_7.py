"""Pass 1.7 COHERENCE — cross-chunk consistency check.

Reads the 6 chunk outputs (1.1-1.6); emits `merged_dossier.json` with
`coherence_flags[]` + `coherence_resolutions[]`. This is the final Pass 1
step; its output is the single input to Pass 2-6 synthesis.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))

from dotenv import load_dotenv
load_dotenv(REPO_ROOT.parent / ".env", override=True)

import anthropic as _anthropic
from flows.shared.clients import call_claude
from flows.shared.io import voice_slug, write_json_atomic
from flows.shared.prompt_render import render
from schemas._entry import ValidationError, validate_chunk_output, generate_json_schemas
from schemas.merged_dossier import MergedDossier


_RETRYABLE = (RuntimeError, json.JSONDecodeError, _anthropic.APIError, _anthropic.RateLimitError)


def _stamp(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def _load_chunk_outputs(repo_root: Path, slug: str) -> dict:
    """Load the 6 chunks written by Passes 1.1-1.6."""
    base = repo_root / "runs" / slug / "01_research"
    out: dict = {}
    # Per-chunk output layout: pass_1_N/<key>.json for each key.
    layout = {
        "pass_1_1": ["life_scaffold", "formative_candidates"],
        "pass_1_2": ["commitments", "concepts", "tensions"],
        "pass_1_3": ["reasoning_method", "textures"],
        "pass_1_4": ["moves", "register", "vocabulary"],
        "pass_1_5": ["knowledge_boundary", "sensitive_topics", "hard_limits"],
        "pass_1_6": ["works", "passages", "urls"],
    }
    for chunk_dir, keys in layout.items():
        for key in keys:
            path = base / chunk_dir / f"{key}.json"
            if not path.exists():
                sys.exit(f"Missing chunk output {path}. Run Pass {chunk_dir.replace('pass_','').replace('_','.')} first.")
            out[key] = json.loads(path.read_text())
    return out


def run_pass_1_7(*, name: str) -> dict:
    slug = voice_slug(name)
    _stamp(f"Pass 1.7 COHERENCE: '{name}' (slug={slug})")

    chunks = _load_chunk_outputs(REPO_ROOT, slug)
    generate_json_schemas()
    merged_dossier_schema = json.dumps(
        MergedDossier.model_json_schema(), indent=2, ensure_ascii=False
    )

    render_ctx = {f"{k}_json": json.dumps(v, ensure_ascii=False, indent=2) for k, v in chunks.items()}
    system = render(
        "pass_1_7_coherence",
        name=name,
        merged_dossier_schema=merged_dossier_schema,
        **render_ctx,
    )
    user = (
        "Run the 7 cross-chunk coherence checks and return the single "
        "merged_dossier object with all 16 chunk keys + coherence_flags[] + "
        "coherence_resolutions[]. JSON only."
    )

    call_kwargs = dict(
        system=system,
        model="claude-opus-4-7",
        max_tokens=40000,
        temperature=1.0,
        thinking=True,
        response_format_json=True,
    )

    def _call_and_validate(user_msg: str) -> dict:
        r = call_claude(user=user_msg, **call_kwargs)
        _stamp(
            f"  tokens in={r['usage']['input_tokens']} out={r['usage']['output_tokens']} "
            f"model={r.get('model','?')}"
        )
        dossier = validate_chunk_output(MergedDossier, r["json"])
        # by_alias=True so the JSON key stays "register" (not "voice_register")
        # per the MergedDossier aliasing note. Pass 2-6 prompts and
        # downstream consumers all read the JSON by the "register" key.
        return dossier.model_dump(by_alias=True)

    try:
        result = _call_and_validate(user)
    except ValidationError as exc:
        _stamp(f"  VALIDATION FAIL on attempt 1; retrying with critique…")
        critique = f"\n\nValidation failed:\n{exc}\n\nFix and return valid JSON only."
        try:
            result = _call_and_validate(user + critique)
        except ValidationError as exc2:
            sys.exit(f"Pass 1.7 failed after retry: {exc2}")
    except _RETRYABLE as exc:
        _stamp(f"  Retryable error ({exc}); retrying in 15 s…")
        time.sleep(15)
        result = _call_and_validate(user)

    out_path = REPO_ROOT / "runs" / slug / "01_research" / "merged_dossier.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    write_json_atomic(out_path, result)
    _stamp(
        f"  merged_dossier written. coherence_flags={len(result.get('coherence_flags', []))} "
        f"coherence_resolutions={len(result.get('coherence_resolutions', []))}"
    )
    return result


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Pass 1.7 COHERENCE")
    p.add_argument("name")
    args = p.parse_args()
    run_pass_1_7(name=args.name)
