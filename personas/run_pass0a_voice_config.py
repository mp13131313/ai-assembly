"""Pass 0a — Voice Config.

Takes a voice name and optional Wikipedia URL. Produces TWO artifacts a human
reviews and signs off on before Pass 0b generates the per-voice DR prompt:

  inputs/voices/<slug>.json                  — pipeline input
  inputs/voices/<slug>_pass0a_review.md      — human review doc

Phase 0.5 (run_phase0_1_research.py) runs AFTER human sign-off: it calls
Perplexity + Gemini in parallel and produces the customized DR prompt at
inputs/dossiers/_dr_prompts/<slug>_dr_prompt.md.

Usage:
    python3 run_pass0a_voice_config.py "Cleopatra"
    python3 run_pass0a_voice_config.py "Cleopatra" --wiki https://en.wikipedia.org/wiki/Cleopatra
    python3 run_pass0a_voice_config.py "Octopus" --hint "the cephalopod (no Wikipedia page needed)"
"""
from __future__ import annotations

import argparse
import json
import re
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
from flows.shared import wikipedia as _wiki


class IncompleteResponse(ValueError):
    """Raised when the model response is missing required keys."""


_RETRYABLE = (RuntimeError, json.JSONDecodeError, _anthropic.APIError, _anthropic.RateLimitError,
              IncompleteResponse)


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


CONFERENCE_FACTS_PATH = REPO_ROOT / "inputs/conference_facts.json"
PANEL_ROSTER_PATH = REPO_ROOT / "inputs/panel_roster.json"
SYSTEM_PROMPT_PATH = REPO_ROOT / "flows/shared/prompts/pass_0a_voice_config.md"
VOICES_DIR = REPO_ROOT / "inputs/voices"
NON_HUMAN_GROUNDING_DIR = REPO_ROOT / "inputs/non_human_grounding"


def _load_pass0a_context() -> dict:
    """Assemble the conference context dict Pass 0a sees (facts + roster only)."""
    facts = json.loads(CONFERENCE_FACTS_PATH.read_text())
    roster = json.loads(PANEL_ROSTER_PATH.read_text())
    return {**facts, **roster}


def _resolve_non_human_grounding(name: str) -> str | None:
    """For non-human voices, check personas/inputs/non_human_grounding/<slug>.md.

    Per decisions log #4: non-human voices get domain-specific curated
    grounding (Godfrey-Smith for Octopus, Te Awa Tupua Act for Whanganui)
    rather than Wikipedia. Returns the file contents if present, else None.
    """
    if not NON_HUMAN_GROUNDING_DIR.exists():
        return None
    slug = voice_slug(name)
    path = NON_HUMAN_GROUNDING_DIR / f"{slug}.md"
    if path.exists():
        return path.read_text()
    return None


def stamp(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def _resolve_wikipedia(name: str, wiki_url: str | None, hint: str | None,
                        choose: int | None = None) -> dict | None:
    """Return a Wikipedia summary dict, or None if no match found."""
    if wiki_url:
        stamp(f"Fetching Wikipedia summary from provided URL…")
        try:
            return _wiki.summary(wiki_url)
        except Exception as exc:
            stamp(f"  WARN: Wikipedia fetch failed ({exc}); proceeding without grounding")
            return None

    stamp(f"Searching Wikipedia for '{name}'…")
    try:
        results = _wiki.search(name, limit=5)
    except Exception as exc:
        stamp(f"  WARN: Wikipedia search failed ({exc}); use --wiki or --hint to provide grounding manually")
        return None

    if not results:
        stamp("  No Wikipedia results found. Use --wiki or --hint for grounding.")
        return None

    # Non-interactive path: --choose N. Always exits on out-of-range per
    # decisions log #5 — consistent behavior (no TTY-conditional fallback).
    # To override interactively, drop the flag.
    if choose is not None:
        idx = choose - 1
        if 0 <= idx < len(results):
            chosen = results[idx]
            stamp(f"  --choose {choose}: selecting '{chosen['title']}'")
            try:
                return _wiki.summary(chosen["url"])
            except Exception as exc:
                stamp(f"  WARN: Summary fetch failed ({exc}); proceeding without grounding")
                return None
        sys.exit(f"--choose {choose} out of range; only {len(results)} results found")

    print()
    print("Wikipedia search results:")
    for i, r in enumerate(results, 1):
        desc = f" — {r['description']}" if r["description"] else ""
        print(f"  {i}. {r['title']}{desc}")
    print("  none — skip Wikipedia grounding (will use --hint if provided)")
    print()

    while True:
        try:
            raw = input("Select a result (1-5 or 'none'): ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            raw = "none"
        if raw == "none" or raw == "0":
            stamp("Wikipedia grounding skipped.")
            return None
        try:
            idx = int(raw) - 1
            if 0 <= idx < len(results):
                chosen = results[idx]
                stamp(f"  Fetching summary for '{chosen['title']}'…")
                try:
                    return _wiki.summary(chosen["url"])
                except Exception as exc:
                    stamp(f"  WARN: Summary fetch failed ({exc}); proceeding without grounding")
                    return None
            else:
                print(f"  Please enter a number between 1 and {len(results)}, or 'none'.")
        except ValueError:
            print("  Please enter a number or 'none'.")


def main(
    name: str,
    wiki_url: str | None = None,
    hint: str | None = None,
    choose: int | None = None,
    editorial_rationale: str | None = None,
) -> None:
    stamp(f"Pass 0a voice config: '{name}'")

    for p in (CONFERENCE_FACTS_PATH, PANEL_ROSTER_PATH):
        if not p.exists():
            sys.exit(f"Missing project config: {p}")
    if not SYSTEM_PROMPT_PATH.exists():
        sys.exit(f"Missing system prompt: {SYSTEM_PROMPT_PATH}")

    # Resolve grounding: non-human domain file first, then Wikipedia, then hint.
    nh_grounding = _resolve_non_human_grounding(name)
    wiki_summary = None
    manual_grounding: str | None = None
    if nh_grounding:
        stamp(f"  Using curated non-human grounding from non_human_grounding/{voice_slug(name)}.md")
        manual_grounding = nh_grounding
    else:
        wiki_summary = _resolve_wikipedia(name, wiki_url, hint, choose=choose)
        if wiki_summary:
            manual_grounding = wiki_summary["extract"]
        elif hint:
            manual_grounding = hint

    project_ctx = _load_pass0a_context()
    system = SYSTEM_PROMPT_PATH.read_text()
    user_payload: dict = {
        "name": name,
        "conference_facts": {k: v for k, v in project_ctx.items() if k != "panel_members_final"},
        "panel_roster": project_ctx.get("panel_members_final", []),
    }
    if manual_grounding:
        user_payload["manual_grounding"] = manual_grounding
    if wiki_summary:
        user_payload["wikipedia_url"] = wiki_summary["url"]

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
        thinking=True,
        response_format_json=True,
    )

    def _do_call(user_msg: str) -> tuple[dict, dict]:
        r = _call_with_retry(stamp, user=user_msg, **_call_kwargs)
        stamp(f"  tokens in={r['usage']['input_tokens']} out={r['usage']['output_tokens']}")
        out = r["json"]
        missing = [k for k in ("voice_config", "review_doc") if k not in out]
        if missing:
            raise IncompleteResponse(f"Response missing required keys: {missing}")
        vc = out["voice_config"]
        # Phase B: voice_config no longer carries conference_context or
        # placeholder; no runner-side injection. Strip any legacy fields.
        for legacy in ("conference_context", "primary_text_sources"):
            vc.pop(legacy, None)
        validate_input(vc)
        return vc, out["review_doc"]

    stamp("Calling Claude Opus 4.7 + adaptive thinking...")
    t0 = time.time()
    try:
        voice_config, review_doc = _do_call(user)
    except InputRejected as exc:
        _field_match = re.search(
            r"Invalid (voice_mode|corpus_constraint|subtype|type)\s+(\S+)", str(exc)
        )
        _field = _field_match.group(1) if _field_match else "unknown"
        stamp(f"  VALIDATION FAIL: field={_field}")
        stamp(f"  Retrying with critique…")
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

    # Carry forward wikipedia_url if we have one (Pass 0b may reference it).
    if wiki_summary:
        voice_config["wikipedia_url"] = wiki_summary["url"]
    # Merge curator-provided editorial_rationale into the config if passed on CLI.
    if editorial_rationale:
        voice_config["editorial_rationale"] = editorial_rationale

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
    if nh_grounding is None and wiki_summary is None:
        stamp("⚠ No manual_grounding was provided. Classification confidence will be low.")
        stamp("  Consider adding a non_human_grounding/<slug>.md file (non-human voices)")
        stamp("  or re-running with --wiki or --hint.")
        stamp("")
    if not voice_config.get("editorial_rationale"):
        stamp("✍ CURATOR ACTION — editorial_rationale not set.")
        stamp(f"  Open {review_path.relative_to(REPO_ROOT)} and fill in the rationale paragraph.")
        stamp(f"  Then edit {voice_path.relative_to(REPO_ROOT)} to replace the null.")
        stamp("")
    stamp("Next steps:")
    stamp(f"  1. Read {review_path.name}; fill editorial_rationale in {voice_path.name} if needed.")
    stamp(f"  2. Run Phase 0.5 research: python3 run_phase0_1_research.py \"{display_name}\"")
    stamp(f"  3. Paste the tailored DR prompt into claude.ai to produce the dossier.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pass 0a — Voice Config")
    parser.add_argument("name", help='Voice name (e.g. "Cleopatra", "Octopus")')
    grp = parser.add_mutually_exclusive_group()
    grp.add_argument("--wiki", metavar="URL",
                     help="Wikipedia URL to use directly (skips interactive picker)")
    grp.add_argument("--hint", metavar="TEXT",
                     help="Fallback disambiguation hint when no Wikipedia match exists")
    grp.add_argument("--choose", metavar="N", type=int,
                     help="Non-interactive: select result N (1-indexed) from Wikipedia search")
    parser.add_argument("--editorial-rationale", metavar="TEXT", default=None,
                        help="Curator-written rationale to drop straight into voice_config. "
                             "If omitted, the config emits null and the review doc prompts the curator.")
    args = parser.parse_args()
    main(
        args.name, wiki_url=args.wiki, hint=args.hint, choose=args.choose,
        editorial_rationale=args.editorial_rationale,
    )
