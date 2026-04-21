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
   through it (each voice's full assembled card as system prompt; shared
   provocation as user message). Evaluator reads 12 responses side-by-side;
   scores pairwise similarity. Flag pairs scoring > 0.7 (too similar).

Evaluator: OpenAI o3 (cross-family from Claude writer per self-preference-
bias argument; baseline File 2 §4). Fallback to Gemini 2.5-pro if o3
unavailable. NOT Claude — same-family biases the distinctiveness judgment.

Voice invocation for same_question uses Claude (the voice's actual
runtime model) — this is NOT evaluation, it is *producing the 12
responses* that the evaluator then compares. Evaluator still crosses
families.

Output: `<project_root>/runs/cross_persona_qc.json` with per-pair similarity
scores + flagged distinctiveness gaps + per-voice "needs rework"
recommendations.
"""
from __future__ import annotations

import argparse
import json
import random
import re
import sys
import time
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))

from dotenv import load_dotenv
load_dotenv(REPO_ROOT.parent / ".env", override=True)

from flows.shared.io import voice_slug, write_json_atomic
from flows.shared.project_root import add_project_arg, resolve_project_root


SHUFFLE_SEED = 42  # per REBUILD_PLAN; reproducible sampling
EXPECTED_VOICE_COUNT = 12
SIMILARITY_FLAG_THRESHOLD = 0.7


def stamp(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] [phase5_qc] {msg}", flush=True)


def _gate_check(project_root: Path) -> list[dict]:
    """Verify all 12 voices have assembled cards; return the loaded cards."""
    roster = json.loads((project_root / "inputs/panel_roster.json").read_text())
    expected = roster.get("panel_members_final", [])
    if len(expected) != EXPECTED_VOICE_COUNT:
        sys.exit(
            f"Panel roster has {len(expected)} voices; expected "
            f"{EXPECTED_VOICE_COUNT}. Update <project_root>/inputs/panel_roster.json or "
            f"EXPECTED_VOICE_COUNT."
        )
    cards: list[dict] = []
    missing: list[str] = []
    for name in expected:
        slug = voice_slug(name)
        card_path = project_root / "runs" / slug / "persona_card_assembled.json"
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


def _parse_json_from_text(text: str) -> dict | None:
    """Extract a JSON object from an evaluator's text response.

    Evaluators sometimes wrap JSON in markdown fences or add preamble.
    Tries response_format_json result first, then strips fences, then
    greedy-matches the outermost {…} block.
    """
    if not text:
        return None
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    m = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(0))
        except json.JSONDecodeError:
            return None
    return None


def _call_evaluator(*, system: str, user: str, model: str = "o3") -> dict:
    """Cross-family evaluator call. Tries OpenAI o3 → gpt-4o → Gemini."""
    from flows.shared.clients import call_gemini
    # o3 / gpt-4o.
    try:
        from flows.shared.clients import call_openai
        for m in (model, "gpt-4o"):
            try:
                r = call_openai(
                    system=system, user=user, model=m,
                    temperature=0.0, max_tokens=8192,
                    response_format_json=True,
                )
                return {
                    "text": r.get("text", ""),
                    "json": r.get("json") or _parse_json_from_text(r.get("text", "")),
                    "model": m, "usage": r.get("usage", {}),
                }
            except Exception as exc:
                stamp(f"  WARN: {m} failed ({type(exc).__name__}: {str(exc)[:120]}); trying next")
    except ImportError:
        pass
    # Gemini fallback.
    r = call_gemini(user=system + "\n\n" + user, temperature=0.0, max_output_tokens=8192)
    return {
        "text": r["text"],
        "json": _parse_json_from_text(r["text"]),
        "model": r["model"], "usage": r["usage"],
    }


# ---------------------------------------------------------------------------
# Sub-test 1: SWAP TEST (strict JSON parsing)
# ---------------------------------------------------------------------------


def _swap_test(cards: list[dict]) -> dict:
    """For each ordered pair (A, B), plant A's first constitution principle
    into B's set. Evaluator identifies the interloper position. Scores %
    correct (interloper always at position 1 in our construction).
    """
    results: list[dict] = []
    rng = random.Random(SHUFFLE_SEED)
    pairs = [(a, b) for a in cards for b in cards if a["slug"] != b["slug"]]
    rng.shuffle(pairs)

    def _principle_from(card: dict) -> str:
        constitution = card.get("constitution", "")
        if isinstance(constitution, list):
            return (constitution[0] if constitution else "")[:500]
        if isinstance(constitution, str):
            parts = [p.strip() for p in constitution.split("\n\n") if p.strip()]
            return (parts[0] if parts else constitution[:500])[:500]
        return str(constitution)[:500]

    for a, b in pairs:
        a_principle = _principle_from(a["card"])
        b_principle = _principle_from(b["card"])
        if not a_principle or not b_principle:
            continue
        system = (
            "You are a cross-voice distinctiveness evaluator. Exactly ONE of "
            "the two principles below is an interloper planted from a "
            "DIFFERENT voice's constitution. The other is genuinely from the "
            "named voice. Identify the interloper index.\n\n"
            "Return JSON only: {\"interloper_index\": <1 or 2>, "
            "\"confidence\": <float 0-1>, \"reason\": \"<one sentence>\"}."
        )
        user = (
            f"VOICE UNDER TEST: {b['name']}\n\n"
            f"PRINCIPLE 1: {a_principle}\n\n"
            f"PRINCIPLE 2: {b_principle}\n\n"
            "Which principle is the interloper — 1 or 2?"
        )
        r = _call_evaluator(system=system, user=user)
        parsed = r.get("json") or {}
        idx = parsed.get("interloper_index")
        # We always plant A's principle at position 1; correct answer = 1.
        correct = (idx == 1)
        results.append({
            "voice_a": a["slug"], "voice_b": b["slug"],
            "evaluator_model": r.get("model"),
            "parsed_interloper_index": idx,
            "confidence": parsed.get("confidence"),
            "reason": parsed.get("reason"),
            "correct": correct,
        })
    correct = sum(1 for r in results if r["correct"])
    return {
        "sub_test": "swap",
        "pair_count": len(results),
        "correct_identifications": correct,
        "accuracy": correct / len(results) if results else 0.0,
        "per_pair": results,
        "interpretation": (
            "Accuracy < 0.75 suggests constitution principles too generic. "
            "Re-run Pass 3 for low-scoring voices with cross-card critique."
        ),
    }


# ---------------------------------------------------------------------------
# Sub-test 2: BLIND IDENTIFICATION (strict JSON parsing)
# ---------------------------------------------------------------------------


def _blind_id_test(cards: list[dict]) -> dict:
    """Shuffle unnamed character + register_and_tone excerpts; evaluator
    attributes each. Strict per-excerpt scoring via parsed JSON attributions.
    """
    rng = random.Random(SHUFFLE_SEED + 1)
    excerpts: list[dict] = []
    for c in cards:
        character = c["card"].get("character", "")
        register = c["card"].get("register_and_tone", "")
        c_text = character if isinstance(character, str) else json.dumps(character)
        r_text = register if isinstance(register, str) else json.dumps(register)
        excerpts.append({
            "slug": c["slug"], "name": c["name"], "field": "character",
            "excerpt": c_text[:600],
        })
        excerpts.append({
            "slug": c["slug"], "name": c["name"], "field": "register_and_tone",
            "excerpt": r_text[:400],
        })
    rng.shuffle(excerpts)
    choices = [c["name"] for c in cards]

    system = (
        "You are reading unlabeled excerpts from persona specifications for "
        "12 distinct voices. For each excerpt, identify which voice it comes "
        "from. Each voice may appear in 0 or more excerpts.\n\n"
        f"PANEL (choose FROM THIS LIST ONLY): {', '.join(choices)}\n\n"
        "Return JSON only:\n"
        "{\"attributions\": [{\"excerpt_id\": <int>, \"voice_name\": <str>, "
        "\"confidence\": <float 0-1>}]}."
    )
    user = "EXCERPTS:\n" + "\n\n".join(
        f"[{i}] {e['excerpt']}" for i, e in enumerate(excerpts)
    )
    r = _call_evaluator(system=system, user=user)
    parsed = r.get("json") or {}
    attributions = parsed.get("attributions", [])

    correct = 0
    details: list[dict] = []
    by_id = {a.get("excerpt_id"): a for a in attributions if isinstance(a, dict)}
    for i, e in enumerate(excerpts):
        attr = by_id.get(i) or {}
        predicted = attr.get("voice_name")
        is_correct = (predicted == e["name"])
        if is_correct:
            correct += 1
        details.append({
            "excerpt_id": i, "field": e["field"],
            "actual_name": e["name"], "predicted_name": predicted,
            "confidence": attr.get("confidence"),
            "correct": is_correct,
        })
    return {
        "sub_test": "blind_id",
        "excerpts_count": len(excerpts),
        "correct_attributions": correct,
        "accuracy": correct / len(excerpts) if excerpts else 0.0,
        "evaluator_model": r.get("model"),
        "per_excerpt": details,
        "interpretation": (
            "Accuracy < 0.6 → character + register_and_tone not distinctive "
            "enough across the panel. Re-run Pass 4a with cross-card critique."
        ),
    }


# ---------------------------------------------------------------------------
# Sub-test 3: SAME-QUESTION DISTINCTIVENESS (live 12-voice invocation)
# ---------------------------------------------------------------------------


def _invoke_voice(card_path: Path, provocation: str, max_tokens: int = 4096) -> str:
    """Invoke a voice at Step-1-like register: full card as system prompt,
    provocation as user message, Claude Sonnet (cheaper than Opus for this).
    Returns the voice's text response.
    """
    from flows.shared.clients import call_claude
    card = json.loads(card_path.read_text())
    # Drop runtime metadata and smoke_test_chains (NOT few-shot material per
    # HANDOFF.md). The rest of the card becomes the system prompt.
    card_for_system = {k: v for k, v in card.items()
                        if k not in ("metadata", "smoke_test_chains",
                                     "continuity_block_if_night_2",
                                     "continuity_block_artifact_if_night_2")}
    system = json.dumps(card_for_system, ensure_ascii=False, indent=2)
    r = call_claude(
        system=system, user=provocation, model="claude-sonnet-4-6",
        max_tokens=max_tokens, temperature=0.7, thinking=False,
        response_format_json=False,
    )
    return r.get("text", "")


def _same_question_test(cards: list[dict], project_root: Path) -> dict:
    """Run all 12 voices through one shared provocation; evaluator scores
    pairwise similarity across the 12 responses. Flag pairs > threshold.
    """
    rng = random.Random(SHUFFLE_SEED + 2)
    # Pick the shared provocation from the first voice's smoke_test_chains.
    first_card = cards[0]["card"]
    chains = first_card.get("smoke_test_chains", [])
    default_prompt = (
        "What happens to the idea of democracy when non-human participants "
        "enter deliberation overnight and the humans read their artifacts "
        "over morning coffee?"
    )
    if chains and isinstance(chains, list):
        pick = chains[rng.randrange(len(chains))]
        prompt = (
            pick.get("provocation") if isinstance(pick, dict) else None
        ) or default_prompt
    else:
        prompt = default_prompt

    stamp(f"  invoking 12 voices on shared provocation ({len(prompt)} chars)…")
    responses: list[dict] = []
    for c in cards:
        card_path = project_root / "runs" / c["slug"] / "persona_card_assembled.json"
        try:
            t0 = time.time()
            text = _invoke_voice(card_path, prompt)
            stamp(f"    {c['name']}: {len(text)} chars in {time.time()-t0:.1f}s")
        except Exception as exc:
            stamp(f"    {c['name']}: FAILED ({exc})")
            text = ""
        responses.append({"slug": c["slug"], "name": c["name"], "response": text})

    # Pairwise similarity scoring by evaluator.
    stamp("  scoring pairwise similarity with cross-family evaluator…")
    # Bundle all 12 labeled responses and ask the evaluator for a similarity
    # matrix — one call, not 66.
    system = (
        "You are scoring response distinctiveness for a persona pipeline "
        "quality gate. You will read 12 labeled responses to the same "
        "provocation. Score each pair for semantic + rhetorical similarity "
        "on a 0-1 scale, where 0 = entirely distinct voices and 1 = "
        "indistinguishable. A distinctive panel should have most pairs "
        "< 0.4. Flag any pair ≥ 0.7 as too similar.\n\n"
        "Return JSON only:\n"
        "{\"pairwise_similarity\": [{\"voice_a\": <slug>, \"voice_b\": <slug>, "
        "\"similarity\": <float 0-1>, \"note\": \"<brief>\"}], "
        "\"flagged_pairs\": [{\"voice_a\": <slug>, \"voice_b\": <slug>, "
        "\"similarity\": <float>, \"reason\": \"<sentence>\"}]}."
    )
    rendered = "\n\n".join(
        f"=== VOICE: {r['name']} (slug={r['slug']}) ===\n{r['response'][:1500]}"
        for r in responses if r["response"]
    )
    user = f"PROVOCATION:\n{prompt}\n\nRESPONSES:\n\n{rendered}"
    e = _call_evaluator(system=system, user=user)
    parsed = e.get("json") or {}

    return {
        "sub_test": "same_question_distinctiveness",
        "shared_prompt": prompt,
        "responses": responses,
        "evaluator_model": e.get("model"),
        "pairwise_similarity": parsed.get("pairwise_similarity", []),
        "flagged_pairs": parsed.get("flagged_pairs", []),
        "threshold": SIMILARITY_FLAG_THRESHOLD,
        "interpretation": (
            "Pairs scored > threshold indicate voices that converge on the "
            "same provocation. Flagged pairs get Pass 4a re-run with "
            "cross-card critique (distinct voice register)."
        ),
    }


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------


def run_cross_persona_qc(
    out_path: Path | None = None,
    *,
    project_root: Path | None = None,
    project: str | None = None,
) -> dict:
    if project_root is None:
        project_root = resolve_project_root(project, repo_root=REPO_ROOT)
    stamp(f"Phase 5 Cross-Persona QC  (PROJECT_ROOT={project_root})")
    cards = _gate_check(project_root)
    stamp(f"  12 assembled cards loaded.")

    stamp("  Sub-test 1: SWAP TEST")
    swap = _swap_test(cards)
    stamp(f"    accuracy={swap['accuracy']:.2%} across {swap['pair_count']} pairs")

    stamp("  Sub-test 2: BLIND IDENTIFICATION")
    blind_id = _blind_id_test(cards)
    stamp(f"    accuracy={blind_id['accuracy']:.2%} across {blind_id['excerpts_count']} excerpts")

    stamp("  Sub-test 3: SAME-QUESTION DISTINCTIVENESS (live 12-voice)")
    same_q = _same_question_test(cards, project_root)
    _flagged = len(same_q.get("flagged_pairs", []))
    stamp(f"    {_flagged} pairs flagged above threshold {SIMILARITY_FLAG_THRESHOLD}")

    result: dict[str, Any] = {
        "run_date": time.strftime("%Y-%m-%d"),
        "voice_count": len(cards),
        "evaluator_family": "openai_o3_or_gpt4o_or_gemini_cross_family",
        "shuffle_seed": SHUFFLE_SEED,
        "similarity_flag_threshold": SIMILARITY_FLAG_THRESHOLD,
        "sub_tests": {"swap": swap, "blind_id": blind_id, "same_question": same_q},
        "recommendations": _derive_recommendations(swap, blind_id, same_q, cards),
    }

    out_path = out_path or (project_root / "runs" / "cross_persona_qc.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    write_json_atomic(out_path, result)
    stamp(f"  wrote {out_path.relative_to(project_root)}")
    return result


def _derive_recommendations(
    swap: dict, blind_id: dict, same_q: dict, cards: list[dict]
) -> list[dict]:
    """Per-voice 'needs rework' recommendations feeding the revision loop."""
    recs: list[dict] = []
    # Swap-test per-voice failure count.
    per_voice_fail: dict[str, int] = {c["slug"]: 0 for c in cards}
    for pair in swap.get("per_pair", []):
        if not pair.get("correct", False):
            for key in ("voice_a", "voice_b"):
                per_voice_fail[pair[key]] = per_voice_fail.get(pair[key], 0) + 1
    for slug, fails in per_voice_fail.items():
        if fails > 4:
            recs.append({
                "voice_slug": slug, "flagged_by": "swap_test",
                "failure_count": fails,
                "recommended_rerun": "Pass 3 (with cross-card critique)",
                "reason": "Constitution principles did not distinguish this voice in >4 swap-test pairs.",
            })
    # Blind-ID — overall accuracy low triggers panel-wide Pass 4a re-run.
    if blind_id.get("accuracy", 1.0) < 0.6:
        recs.append({
            "voice_slug": "__ALL__", "flagged_by": "blind_id_test",
            "accuracy": blind_id["accuracy"],
            "recommended_rerun": "Pass 4a (with cross-card critique)",
            "reason": "character + register_and_tone not distinctive enough across the panel.",
        })
    # Same-question — per-pair similarity flags trigger Pass 4a on both voices.
    for flag in same_q.get("flagged_pairs", []):
        for key in ("voice_a", "voice_b"):
            recs.append({
                "voice_slug": flag.get(key), "flagged_by": "same_question",
                "pair_similarity": flag.get("similarity"),
                "recommended_rerun": "Pass 4a (with cross-card critique)",
                "reason": flag.get("reason", "Similarity above threshold."),
            })
    return recs


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Phase 5 Cross-Persona QC")
    parser.add_argument("--out", default=None)
    add_project_arg(parser)
    args = parser.parse_args()
    run_cross_persona_qc(
        out_path=Path(args.out) if args.out else None,
        project=args.project,
    )
