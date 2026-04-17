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

from flows.shared.clients import call_claude
from flows.shared.io import voice_slug, write_json_atomic


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

    stamp("Calling Claude Opus 4.7 + adaptive thinking...")
    t0 = time.time()
    r = call_claude(
        system=system,
        user=user,
        model="claude-opus-4-7",
        max_tokens=24000,
        temperature=1.0,
        thinking_budget=None,  # adaptive thinking
        response_format_json=True,
    )
    wall = time.time() - t0
    stamp(f"  done in {wall:.1f}s | tokens in={r['usage']['input_tokens']} out={r['usage']['output_tokens']}")

    out = r["json"]
    for required in ("voice_config", "review_doc"):
        if required not in out:
            sys.exit(f"Pass 0a output missing required key: {required}")

    voice_config = out["voice_config"]
    review_doc = out["review_doc"]

    # Strip primary_text_sources if the model accidentally emitted it —
    # this field is a manual-edit hook only, not Pass 0a output.
    voice_config.pop("primary_text_sources", None)

    display_name = voice_config.get("name", name)
    slug = voice_slug(display_name)

    # Inject the project-level conference context paragraph (don't trust the
    # model to copy it verbatim — substitute it server-side)
    voice_config["conference_context"] = project_ctx["conference_context_paragraph"]

    # Set pass_1a_claude_dr_file path (consistent with pipeline expectation)
    voice_config["pass_1a_claude_dr_file"] = f"inputs/dossiers/{slug}_claude_dr.md"

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
