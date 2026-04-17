"""Pass 0a — Voice Config.

Takes a voice name and hint. Produces TWO artifacts a human reviews and signs
off on before Pass 0b generates the per-voice DR prompt:

  inputs/voices/<slug>.json                  — pipeline input
  inputs/voices/<slug>_pass0a_review.md      — human review doc

Pass 0b (run_pass0b_dr_prompt.py) is a separate script that runs AFTER
human sign-off, reads the (possibly-edited) voice config, and produces the
customized DR prompt at inputs/dossiers/_dr_prompts/<slug>_dr_prompt.md.

Usage:
    python3 run_pass0a_voice_config.py "Cleopatra" --hint "the Egyptian queen"
    python3 run_pass0a_voice_config.py "Peter Thiel" --hint "the investor"
    python3 run_pass0a_voice_config.py "Octopus" --hint "the cephalopod"
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
load_dotenv(REPO_ROOT.parent / ".env")

import anthropic as _anthropic
from flows.shared.clients import call_claude
from flows.shared.io import voice_slug, write_json_atomic
from flows.shared.node0_validation import InputRejected, validate_input

_RETRYABLE = (RuntimeError, json.JSONDecodeError, _anthropic.APIError, _anthropic.RateLimitError)


def _call_with_retry(stamp_fn, **kwargs):
    try:
        return call_claude(**kwargs)
    except _RETRYABLE as exc:
        stamp_fn(f"  Error on attempt 1 ({exc}); retrying in 15 s…")
        time.sleep(15)
    try:
        return call_claude(**kwargs)
    except _RETRYABLE as exc:
        sys.exit(f"Pass 0a failed after retry: {exc}")


PROJECT_CONTEXT_PATH = REPO_ROOT / "inputs/conference_context.json"
SYSTEM_PROMPT_PATH = REPO_ROOT / "flows/shared/prompts/pass_0a_voice_config.md"
VOICES_DIR = REPO_ROOT / "inputs/voices"


def stamp(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def main(name: str, hint: str) -> None:
    stamp(f"Pass 0a voice config: '{name}'")

    if not PROJECT_CONTEXT_PATH.exists():
        sys.exit(f"Missing project config: {PROJECT_CONTEXT_PATH}")
    if not SYSTEM_PROMPT_PATH.exists():
        sys.exit(f"Missing system prompt: {SYSTEM_PROMPT_PATH}")

    project_ctx = json.loads(PROJECT_CONTEXT_PATH.read_text())
    system = SYSTEM_PROMPT_PATH.read_text()
    user_payload = {
        "name": name,
        "disambiguation_hint": hint,
        "conference_context": project_ctx,
    }
    user = (
        "Produce the two Pass 0a artifacts for the voice below. "
        "Return ONLY the JSON object with keys voice_config, review_doc.\n\n"
        f"VOICE_INPUT:\n{json.dumps(user_payload, ensure_ascii=False, indent=2)}"
    )

    _call_kwargs = dict(
        system=system,
        model="claude-opus-4-7",
        max_tokens=24000,
        temperature=1.0,
        thinking_budget=None,  # adaptive thinking
        response_format_json=True,
    )
    _real_ctx = project_ctx["conference_context_paragraph"]

    def _do_call(user_msg: str) -> tuple[dict, dict]:
        """Call Claude, parse, validate enum fields. Returns (voice_config, review_doc)."""
        r = _call_with_retry(stamp, user=user_msg, **_call_kwargs)
        stamp(f"  tokens in={r['usage']['input_tokens']} out={r['usage']['output_tokens']}")
        out = r["json"]
        for required in ("voice_config", "review_doc"):
            if required not in out:
                sys.exit(f"Pass 0a output missing required key: {required}")
        vc = out["voice_config"]
        vc.pop("primary_text_sources", None)
        # Temporarily inject real conference_context so validate_input() passes
        # the required-field check (model emits placeholder "INJECTED_BY_RUNNER")
        vc_for_validation = dict(vc, conference_context=_real_ctx)
        validate_input(vc_for_validation)
        return vc, out["review_doc"]

    stamp("Calling Claude Opus 4.7 + adaptive thinking...")
    t0 = time.time()
    try:
        voice_config, review_doc = _do_call(user)
    except InputRejected as exc:
        stamp(f"  Validation failed on attempt 1: {exc}; retrying with critique…")
        critique_user = user + (
            f"\n\nYour previous response failed validation:\n{exc}\n"
            "Fix the invalid enum fields and return valid JSON."
        )
        try:
            voice_config, review_doc = _do_call(critique_user)
        except InputRejected as exc2:
            sys.exit(f"Pass 0a validation failed after retry: {exc2}")
    wall = time.time() - t0
    stamp(f"  done in {wall:.1f}s")

    display_name = voice_config.get("name", name)
    slug = voice_slug(display_name)

    # Inject the real conference context (overwrite model's placeholder)
    voice_config["conference_context"] = _real_ctx

    # Write artifacts
    VOICES_DIR.mkdir(parents=True, exist_ok=True)

    voice_path = VOICES_DIR / f"{slug}.json"
    review_path = VOICES_DIR / f"{slug}_pass0a_review.md"

    write_json_atomic(voice_path, voice_config)
    review_path.write_text(review_doc, encoding="utf-8")

    stamp("Pass 0a complete.")
    stamp(f"  Voice config:  {voice_path.relative_to(REPO_ROOT)}")
    stamp(f"  Review doc:    {review_path.relative_to(REPO_ROOT)}")
    stamp("")
    stamp("Next steps:")
    stamp(f"  1. Read {review_path.name} and edit {voice_path.name} if needed")
    stamp(f"  2. Run Pass 0b: python3 run_pass0b_dr_prompt.py \"{display_name}\"")
    stamp(f"  3. Then follow the DR prompt's instructions to produce the dossier.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pass 0a — Voice Config")
    parser.add_argument("name", help='Voice name (e.g. "Cleopatra", "Octopus")')
    parser.add_argument("--hint", required=True, help="Disambiguation hint (required)")
    args = parser.parse_args()
    main(args.name, args.hint)
