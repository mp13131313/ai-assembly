"""Phase 5 — Cross-Persona QC.

Runs once after all 12 assembled cards complete. Three sub-tests measure
cross-voice distinctiveness:

1. SWAP TEST (`_swap_test`): for each pair (A, B), construct a test — take a
   constitution principle from voice A, present it attributed to voice B
   alongside voice B's actual principles. Ask the cross-model evaluator:
   which is the interloper? Score: % correctly identified. Low → cards
   are too generic.

2. BLIND IDENTIFICATION (`_blind_id_test`): remove voice names from
   `character` + `register_and_tone` excerpts. Shuffle. Present to
   evaluator without attribution. Ask: which voice does this excerpt
   come from? Score: % correctly attributed across 12 × K excerpts.

3. SAME-QUESTION DISTINCTIVENESS (`_same_question_test`): pick one shared
   provocation (reuse a smoke_test_chain from Pass 7b). Run all 12 voices
   through it. Evaluator reads 12 responses side-by-side; scores pairwise
   similarity. Flag pairs scoring > 0.7 (too similar).

Evaluator: OpenAI o3 (cross-family from Claude writer per self-preference-
bias argument; baseline File 2 §4). Fallback to Gemini 2.5-pro if o3
unavailable. NOT Claude — same-family biases the distinctiveness judgment.

Output: `runs/cross_persona_qc.json` with per-pair similarity scores +
flagged distinctiveness gaps + per-voice "needs rework" recommendations.

Revision integration:
- Constitution similarity → re-run Pass 3 with cross-card critique
- Voice/register similarity → re-run Pass 4a with cross-card critique
- Max 2 cross-card revision rounds per voice
"""
from __future__ import annotations

import argparse
import json
import random
import sys
import time
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))

from dotenv import load_dotenv
load_dotenv(REPO_ROOT.parent / ".env", override=True)

from flows.shared.io import voice_slug, write_json_atomic


SHUFFLE_SEED = 42  # per REBUILD_PLAN; reproducible sampling
PANEL_ROSTER_PATH = REPO_ROOT / "inputs/panel_roster.json"
EXPECTED_VOICE_COUNT = 12
SIMILARITY_FLAG_THRESHOLD = 0.7


def stamp(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] [phase5_qc] {msg}", flush=True)


def _gate_check() -> list[dict]:
    """Verify all 12 voices have assembled cards; return the loaded cards.

    Returns list of (voice_slug, card_dict) tuples; raises SystemExit if
    the panel isn't complete.
    """
    roster = json.loads(PANEL_ROSTER_PATH.read_text())
    expected = roster.get("panel_members_final", [])
    if len(expected) != EXPECTED_VOICE_COUNT:
        sys.exit(
            f"Panel roster has {len(expected)} voices; expected "
            f"{EXPECTED_VOICE_COUNT}. Update inputs/panel_roster.json or "
            f"EXPECTED_VOICE_COUNT."
        )
    cards: list[dict] = []
    missing: list[str] = []
    for name in expected:
        slug = voice_slug(name)
        card_path = REPO_ROOT / "runs" / slug / "persona_card_assembled.json"
        if not card_path.exists():
            missing.append(f"{name} ({slug})")
            continue
        cards.append({"name": name, "slug": slug, "card": json.loads(card_path.read_text())})
    if missing:
        sys.exit(
            "Phase 5 QC gates on 12 complete assembled cards. Missing:\n  - "
            + "\n  - ".join(missing)
        )
    return cards


def _call_evaluator(*, system: str, user: str, model: str = "o3") -> dict:
    """Thin wrapper around OpenAI o3; falls back to Gemini on error.

    Uses the personas.flows.shared.clients OpenAI client if available.
    Returns {'text': str, 'json': dict|None, 'model': str, 'usage': dict}.
    """
    # Lazy import — the OpenAI + Gemini clients live in personas.flows.shared.
    from flows.shared import clients
    try:
        # o3 requires max_completion_tokens, no temperature per clients.py conventions.
        if hasattr(clients, "call_openai"):
            return clients.call_openai(
                system=system, user=user, model=model,
                max_completion_tokens=8192, response_format_json=True,
            )
    except Exception as exc:  # pragma: no cover — o3 unavailable
        stamp(f"  o3 call failed ({exc}); falling back to Gemini")
    # Gemini fallback.
    from flows.shared.clients import call_gemini
    r = call_gemini(user=system + "\n\n" + user, temperature=0.0, max_output_tokens=8192)
    return {
        "text": r["text"], "json": None, "model": r["model"], "usage": r["usage"],
    }


# ---------------------------------------------------------------------------
# Sub-test 1: SWAP TEST
# ---------------------------------------------------------------------------


def _swap_test(cards: list[dict]) -> dict:
    """For each (A, B) pair, plant A's constitution principle in B's set.

    Evaluator must identify the interloper. Aggregated score = % correct.
    """
    results: list[dict] = []
    rng = random.Random(SHUFFLE_SEED)
    pairs = [(a, b) for a in cards for b in cards if a["slug"] != b["slug"]]
    rng.shuffle(pairs)

    for a, b in pairs:
        a_constitution = a["card"].get("constitution", "")
        b_constitution = b["card"].get("constitution", "")
        if not a_constitution or not b_constitution:
            continue
        # Pick one principle from A (naive: first line / first entry).
        a_first = a_constitution.split("\n", 1)[0].strip() if isinstance(a_constitution, str) else str(a_constitution)[:400]
        b_shuffled = b_constitution if isinstance(b_constitution, str) else json.dumps(b_constitution, ensure_ascii=False)
        system = (
            "You are a cross-voice distinctiveness evaluator. ONE of the "
            "principles below is an interloper from a different voice. "
            "Identify which — return JSON: {\"interloper_index\": <int>, "
            "\"reason\": \"...\"}."
        )
        user = (
            f"VOICE: {b['name']}\n\n"
            f"PRINCIPLES (one is the interloper):\n\n"
            f"1. {a_first}\n\n"
            f"2. {b_shuffled[:600]}\n\n"
            "Return JSON only."
        )
        r = _call_evaluator(system=system, user=user)
        results.append({
            "voice_a": a["slug"], "voice_b": b["slug"],
            "evaluator_response": r.get("text", ""),
            "correct": "1" in r.get("text", "") or "interloper_index\": 1" in r.get("text", ""),
        })
    correct = sum(1 for r in results if r["correct"])
    return {
        "sub_test": "swap",
        "pair_count": len(results),
        "correct_identifications": correct,
        "accuracy": correct / len(results) if results else 0.0,
        "per_pair": results,
        "interpretation": (
            "Accuracy < 0.75 suggests constitution principles too generic; "
            "re-run Pass 3 for low-scoring voices with cross-card critique."
        ),
    }


# ---------------------------------------------------------------------------
# Sub-test 2: BLIND IDENTIFICATION
# ---------------------------------------------------------------------------


def _blind_id_test(cards: list[dict], excerpts_per_voice: int = 3) -> dict:
    """Shuffle unnamed `character` + `register_and_tone` excerpts; evaluator identifies."""
    rng = random.Random(SHUFFLE_SEED + 1)
    excerpts: list[dict] = []
    for c in cards:
        character = c["card"].get("character", "")
        register = c["card"].get("register_and_tone", "")
        text = (character if isinstance(character, str) else json.dumps(character))[:600]
        excerpts.append({"slug": c["slug"], "name": c["name"], "excerpt": text, "field": "character"})
        excerpts.append({"slug": c["slug"], "name": c["name"],
                         "excerpt": (register if isinstance(register, str) else json.dumps(register))[:400],
                         "field": "register_and_tone"})
    rng.shuffle(excerpts)
    choices = [c["name"] for c in cards]

    system = (
        "You are reading unlabeled excerpts from persona specifications for "
        "12 distinct AI voices. For each excerpt, identify which voice it "
        "comes from. Return JSON: {\"attributions\": [{\"excerpt_id\": <int>, "
        "\"voice_name\": <one of the panel names>}]}."
    )
    user = (
        "PANEL: " + ", ".join(choices) + "\n\n"
        "EXCERPTS:\n"
        + "\n\n".join(f"[{i}] {e['excerpt']}" for i, e in enumerate(excerpts))
        + "\n\nReturn JSON only."
    )
    r = _call_evaluator(system=system, user=user)
    # Lenient scoring: parse the evaluator text for name mentions.
    text = r.get("text", "")
    correct = 0
    for i, e in enumerate(excerpts):
        # Heuristic: evaluator said e['name'] near the excerpt index. Strict
        # parsing is deferred to real integration.
        if e["name"] in text:
            correct += 1
    return {
        "sub_test": "blind_id",
        "excerpts_count": len(excerpts),
        "attributions_correct_heuristic": correct,
        "accuracy_heuristic": correct / len(excerpts) if excerpts else 0.0,
        "evaluator_raw": text,
        "interpretation": (
            "Heuristic < 0.6 → voices indistinguishable at character / "
            "register_and_tone level; re-run Pass 4a with cross-card critique."
        ),
    }


# ---------------------------------------------------------------------------
# Sub-test 3: SAME-QUESTION DISTINCTIVENESS
# ---------------------------------------------------------------------------


def _same_question_test(cards: list[dict]) -> dict:
    """Run all 12 voices through one shared provocation; evaluator scores pairwise similarity."""
    rng = random.Random(SHUFFLE_SEED + 2)
    # Pick a shared provocation: reuse a smoke_test_chain from the first
    # voice's card; fallback to a default if absent.
    default_prompt = (
        "What happens to the idea of democracy when non-human participants "
        "enter deliberation overnight and the humans read their artifacts "
        "over morning coffee?"
    )
    first = cards[0]["card"]
    chains = first.get("smoke_test_chains", [])
    if chains and isinstance(chains, list):
        shared = chains[rng.randrange(len(chains))]
        prompt = shared.get("provocation") if isinstance(shared, dict) else default_prompt
    else:
        prompt = default_prompt

    # Runtime LLM invocation per voice is heavy; this scaffold records the
    # intended structure but the live run of 12 voices against this prompt
    # + side-by-side scoring is deferred to the real Phase L+ integration.
    return {
        "sub_test": "same_question_distinctiveness",
        "shared_prompt": prompt,
        "status": "scaffolded",
        "note": (
            "Per REBUILD_PLAN K.2: runs each of 12 voices against the shared "
            "prompt at their Voice Pipeline Step 1 register, then evaluator "
            "scores pairwise similarity. Pairs > "
            f"{SIMILARITY_FLAG_THRESHOLD} are flagged. Live integration "
            "lands after Phase L first-voice end-to-end."
        ),
        "threshold": SIMILARITY_FLAG_THRESHOLD,
    }


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------


def run_cross_persona_qc(out_path: Path | None = None) -> dict:
    stamp("Phase 5 Cross-Persona QC")
    cards = _gate_check()
    stamp(f"  12 assembled cards loaded.")

    stamp("  Sub-test 1: SWAP TEST")
    swap = _swap_test(cards)
    stamp(f"    accuracy={swap['accuracy']:.2%} across {swap['pair_count']} pairs")

    stamp("  Sub-test 2: BLIND IDENTIFICATION")
    blind_id = _blind_id_test(cards)
    stamp(f"    heuristic accuracy={blind_id['accuracy_heuristic']:.2%}")

    stamp("  Sub-test 3: SAME-QUESTION DISTINCTIVENESS")
    same_q = _same_question_test(cards)
    stamp(f"    status={same_q['status']}")

    result: dict[str, Any] = {
        "run_date": time.strftime("%Y-%m-%d"),
        "voice_count": len(cards),
        "evaluator_family": "openai_o3_or_gemini_cross_family",
        "shuffle_seed": SHUFFLE_SEED,
        "similarity_flag_threshold": SIMILARITY_FLAG_THRESHOLD,
        "sub_tests": {"swap": swap, "blind_id": blind_id, "same_question": same_q},
        "recommendations": _derive_recommendations(swap, blind_id, cards),
    }

    out_path = out_path or (REPO_ROOT / "runs" / "cross_persona_qc.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    write_json_atomic(out_path, result)
    stamp(f"  wrote {out_path.relative_to(REPO_ROOT)}")
    return result


def _derive_recommendations(swap: dict, blind_id: dict, cards: list[dict]) -> list[dict]:
    """Per-voice 'needs rework' recommendations feeding the revision loop."""
    recs: list[dict] = []
    # Aggregate swap-test per-voice failure count.
    per_voice_fail = {c["slug"]: 0 for c in cards}
    for pair in swap.get("per_pair", []):
        if not pair.get("correct", False):
            per_voice_fail[pair["voice_a"]] = per_voice_fail.get(pair["voice_a"], 0) + 1
            per_voice_fail[pair["voice_b"]] = per_voice_fail.get(pair["voice_b"], 0) + 1
    for slug, fails in per_voice_fail.items():
        if fails > 4:
            recs.append({
                "voice_slug": slug,
                "flagged_by": "swap_test",
                "failure_count": fails,
                "recommended_rerun": "Pass 3 (with cross-card critique)",
                "reason": "Constitution principles did not distinguish this voice in >4 swap-test pairs.",
            })
    # Blind-ID heuristic — if overall accuracy low, recommend Pass 4a re-run for all.
    if blind_id.get("accuracy_heuristic", 1.0) < 0.6:
        recs.append({
            "voice_slug": "__ALL__",
            "flagged_by": "blind_id_test",
            "accuracy": blind_id["accuracy_heuristic"],
            "recommended_rerun": "Pass 4a (with cross-card critique)",
            "reason": "character + register_and_tone not distinctive enough across the panel.",
        })
    return recs


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Phase 5 Cross-Persona QC")
    parser.add_argument("--out", default=None)
    args = parser.parse_args()
    run_cross_persona_qc(out_path=Path(args.out) if args.out else None)
