"""Pass 1.1 BIOGRAPHICAL merge — chunked Pass 1 proof of architecture.

Reads Perplexity + Claude DR + Gemini dossiers for a voice, calls Claude Opus
4.7 with adaptive thinking, validates the output against
`schemas.pass_1_1.LifeScaffold` + `FormativeCandidate[]`, retries once with
critique on validation failure, writes:

    <project_root>/runs/<slug>/01_research/pass_1_1/life_scaffold.json
    <project_root>/runs/<slug>/01_research/pass_1_1/formative_candidates.json

Test mode: `--use-test-fixtures` reads from `personas/tests/fixtures/<slug>/`
(code-level) instead of `<project_root>/voices/<slug>/01_research/`, uses a
truncated mock DR dossier, and exercises merge mechanics (schema validation +
retry + atomic write). Use `synthetic_voice` slug for the code-level fixture.
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
# override=True: the Claude Code runtime may inject an empty ANTHROPIC_API_KEY
# into the environment; without override, dotenv won't replace it.
load_dotenv(REPO_ROOT.parent / ".env", override=True)

import anthropic as _anthropic
from flows.shared.clients import call_claude
from flows.shared.io import voice_slug, write_json_atomic
from flows.shared.project_root import add_project_arg, resolve_project_root
from flows.shared.prompt_render import render
from schemas._entry import ValidationError, validate_chunk_output, generate_json_schemas
from schemas.pass_1_1 import FormativeCandidate, LifeScaffold


_RETRYABLE = (RuntimeError, json.JSONDecodeError, _anthropic.APIError, _anthropic.RateLimitError)


def stamp(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def _load_sources(project_root: Path, slug: str, use_test_fixtures: bool) -> tuple[str, str, str]:
    """Return (perplexity_text, claude_dr_text, gemini_text).

    Test fixtures live under `REPO_ROOT/tests/fixtures/` (code).
    Live runs live under `project_root/runs/` (project data).
    """
    if use_test_fixtures:
        fixtures = REPO_ROOT / "tests/fixtures" / slug
        perp = json.loads((fixtures / "perplexity_dossier.json").read_text())
        gem = json.loads((fixtures / "gemini_broad_scan.json").read_text())
        # No pinned DR dossier; use a compact placeholder so merge mechanics run.
        dr_text = (
            "[MOCK DEEP RESEARCH DOSSIER — fixtures mode.]\n\n"
            "Phase B test harness placeholder. Pass 1.1 merge mechanics are "
            "exercised; Boddice-shape content depends on a real DR dossier and "
            "lands in Phase L. Treat the Perplexity + Gemini material as primary "
            "grounding; do not invent content for fields a real DR dossier would "
            "supply — flag missing material with evidence_tag=inference and a "
            "short note."
        )
    else:
        research = project_root / "runs" / slug / "01_research"
        perp = json.loads((research / "perplexity_dossier.json").read_text())
        gem = json.loads((research / "gemini_broad_scan.json").read_text())
        dr_path = research / "claude_dr_dossier.md"
        if not dr_path.exists():
            sys.exit(
                f"Missing Claude DR dossier at {dr_path}. Phase 0.5 must complete "
                f"+ human must paste the claude.ai output before Pass 1.1 runs."
            )
        dr_text = dr_path.read_text()

    # Perplexity / Gemini dossiers are JSON-wrapped. For the merge prompt we
    # want the textual content a model can read naturally.
    perp_text = perp.get("text") or json.dumps(perp, ensure_ascii=False, indent=2)
    gem_text = gem.get("text") or json.dumps(gem, ensure_ascii=False, indent=2)
    return perp_text, dr_text, gem_text


def _inline_schemas() -> tuple[str, str]:
    """Return (LifeScaffold JSON Schema str, FormativeCandidate JSON Schema str).

    Regenerates generated/ files as a side effect so the schemas on disk stay
    in sync with the Pydantic source.
    """
    generate_json_schemas()
    ls = LifeScaffold.model_json_schema()
    fc = FormativeCandidate.model_json_schema()
    return (
        json.dumps(ls, indent=2, ensure_ascii=False),
        json.dumps(fc, indent=2, ensure_ascii=False),
    )


def _validate(data: dict) -> tuple[LifeScaffold, list[FormativeCandidate]]:
    """Validate the LLM's two-key output; raise ValidationError on failure."""
    if not isinstance(data, dict) or set(data.keys()) < {"life_scaffold", "formative_candidates"}:
        raise ValidationError.from_exception_data(
            "Pass 1.1 output", [{"type": "missing", "loc": (), "msg": "expected keys life_scaffold + formative_candidates", "input": data}]
        )
    scaffold = validate_chunk_output(LifeScaffold, data["life_scaffold"])
    candidates = [
        validate_chunk_output(FormativeCandidate, c)
        for c in data["formative_candidates"]
    ]
    return scaffold, candidates


def run_pass_1_1(
    *,
    name: str,
    voice_type: str = "human",
    subtype: str | None = None,
    voice_mode: str = "philosophical",
    use_test_fixtures: bool = False,
    output_dir: Path | None = None,
    project_root: Path | None = None,
    project: str | None = None,
) -> dict:
    slug = voice_slug(name)
    stamp(f"Pass 1.1 BIOGRAPHICAL merge: '{name}' (slug={slug}, fixtures={use_test_fixtures})")

    if project_root is None:
        project_root = resolve_project_root(project, repo_root=REPO_ROOT)

    perp_text, dr_text, gem_text = _load_sources(project_root, slug, use_test_fixtures)
    life_scaffold_schema, formative_candidate_schema = _inline_schemas()

    system = render(
        "pass_1_1_merge",
        name=name,
        type=voice_type,
        subtype=subtype,
        voice_mode=voice_mode,
        perplexity_dossier_text=perp_text,
        claude_dr_dossier_text=dr_text,
        gemini_broad_scan_text=gem_text,
        life_scaffold_schema=life_scaffold_schema,
        formative_candidate_schema=formative_candidate_schema,
    )
    user = (
        "Produce the Pass 1.1 biographical merge for the voice specified in "
        "the system prompt. Return the single JSON object with keys "
        "`life_scaffold` and `formative_candidates` as described. JSON only."
    )

    call_kwargs = dict(
        system=system,
        model="claude-opus-4-7",
        max_tokens=32000,
        temperature=1.0,
        thinking=True,
        response_format_json=True,
    )

    def _call_and_validate(user_msg: str) -> dict:
        r = call_claude(user=user_msg, **call_kwargs)
        stamp(
            f"  tokens in={r['usage']['input_tokens']} out={r['usage']['output_tokens']} "
            f"model={r.get('model','?')}"
        )
        data = r["json"]
        scaffold, candidates = _validate(data)
        return {
            "life_scaffold": scaffold.model_dump(),
            "formative_candidates": [c.model_dump() for c in candidates],
            "_usage": r["usage"],
            "_model": r.get("model"),
        }

    try:
        result = _call_and_validate(user)
    except ValidationError as exc:
        stamp(f"  VALIDATION FAIL on attempt 1; retrying with critique…")
        critique = (
            "\n\nYour previous response failed Pydantic validation. Critique:\n"
            f"{exc}\n\nFix the schema mismatch and return valid JSON only."
        )
        try:
            result = _call_and_validate(user + critique)
        except ValidationError as exc2:
            sys.exit(f"Pass 1.1 failed after retry: {exc2}")
    except _RETRYABLE as exc:
        stamp(f"  Retryable error on attempt 1 ({exc}); retrying in 15 s…")
        time.sleep(15)
        try:
            result = _call_and_validate(user)
        except _RETRYABLE as exc2:
            sys.exit(f"Pass 1.1 failed after retry: {exc2}")

    # Write artifacts.
    out_dir = output_dir or (project_root / "runs" / slug / "01_research/pass_1_1")
    out_dir.mkdir(parents=True, exist_ok=True)
    write_json_atomic(out_dir / "life_scaffold.json", result["life_scaffold"])
    write_json_atomic(out_dir / "formative_candidates.json", result["formative_candidates"])

    stamp(f"  LifeScaffold fields: {list(result['life_scaffold'].keys())}")
    stamp(f"  FormativeCandidates: {len(result['formative_candidates'])}")
    stamp(f"  Wrote {out_dir.relative_to(project_root)}")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pass 1.1 BIOGRAPHICAL merge")
    parser.add_argument("name", help='Voice name (e.g. "Plato", "Ibn Battuta")')
    parser.add_argument("--type", default="human", choices=["human", "non_human", "fictional"])
    parser.add_argument("--subtype", default=None, choices=[None, "organism", "system"])
    parser.add_argument("--voice-mode", default="philosophical")
    parser.add_argument(
        "--use-test-fixtures", action="store_true",
        help="Read from personas/tests/fixtures/<slug>/ (code-level) instead of "
             "<project_root>/runs/<slug>/01_research/ "
             "(exercises merge mechanics without a live Phase 0.5 run).",
    )
    add_project_arg(parser)
    args = parser.parse_args()
    run_pass_1_1(
        name=args.name,
        voice_type=args.type,
        subtype=args.subtype,
        voice_mode=args.voice_mode,
        use_test_fixtures=args.use_test_fixtures,
        project=args.project,
    )
