"""End-to-end Persona Pipeline runner for a single voice (Plato test run).

Walks: Node 0 -> Pass 1a -> Pass 1c -> Pass 1-merge -> Pass 2 -> CT ->
Pass 3 -> CT -> Pass 4a -> CT -> Pass 4b -> Pass 5 -> Pass 6.

Designed for resumability: each pass writes its output JSON before the next
pass starts. If a pass already exists, it's loaded from disk instead of
re-called. To force a re-run, delete the output JSON.

Pass 1b (Gemini broad scan) is skipped — the project's Google API key has
zero free-tier quota. Pass 1-merge therefore runs in degraded mode.
"""
from __future__ import annotations
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, ".")
from dotenv import load_dotenv
load_dotenv("/Users/aienvironment/Desktop/ai-assembly-personas/.env")

from flows.shared.io import load_voice_input, write_json_atomic
from flows.shared.node0_validation import validate_input
from flows.shared.prompt_render import render
from flows.shared.clients import call_claude, call_perplexity
from flows.shared.node1c_fetch import fetch_all


VOICE_NAME = sys.argv[1] if len(sys.argv) > 1 else "Plato"
SLUG = VOICE_NAME.lower().replace(" ", "_").replace("-", "_")
RUN = Path(f"runs/{SLUG}")
(RUN / "01_research").mkdir(parents=True, exist_ok=True)
(RUN / "02_passes").mkdir(parents=True, exist_ok=True)


def stamp(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def cached(path: Path, label: str):
    """Return parsed JSON if path exists, else None and log."""
    if path.exists():
        stamp(f"  CACHE HIT: {label} -> {path.name}")
        return json.load(open(path))
    return None


def call_or_cache(path: Path, label: str, runner):
    """Run `runner()` if `path` doesn't exist, save result, return result."""
    cached_v = cached(path, label)
    if cached_v is not None:
        return cached_v
    stamp(f"  RUNNING: {label}")
    started = time.time()
    result = runner()
    result["_elapsed_seconds"] = round(time.time() - started, 1)
    write_json_atomic(path, result)
    stamp(f"  DONE in {result['_elapsed_seconds']}s -> {path.name}")
    return result


# ---------- NODE 0 ----------
stamp(f"NODE 0: validating {VOICE_NAME}")
vi = validate_input(load_voice_input(VOICE_NAME))
stamp(f"  type={vi['type']} voice_mode={vi['voice_mode']} hostile={vi['hostile_sources']} sources={len(vi['primary_text_sources'])}")


# ---------- PASS 1a ----------
def _pass_1a():
    prompt = render("persona_pass_1a_research_human", name=vi["name"], hostile_sources=vi["hostile_sources"])
    r = call_perplexity(user=prompt, temperature=0.0)
    return {"voice_name": vi["name"], "voice_slug": SLUG, "pass": "1a_research_dossier",
            "model": r["model"], "usage": r["usage"], "citations": r.get("citations", []),
            "search_results": r.get("search_results", []), "text": r["text"], "think": r["think"]}

stamp("PASS 1a: Perplexity sonar-deep-research")
pass1a = call_or_cache(RUN / "01_research/perplexity_dossier.json", "Pass 1a", _pass_1a)
dossier_text = pass1a.get("text") or pass1a.get("text_clean")
stamp(f"  dossier: {len(dossier_text)} chars")


# ---------- PASS 1c ----------
def _pass_1c():
    fetched = fetch_all(vi["primary_text_sources"])
    return {"voice_name": vi["name"], "voice_slug": SLUG, "pass": "1c_primary_text_fetch",
            "source_count": len(fetched), "passages": fetched,
            "total_chars": sum(p["char_count"] for p in fetched)}

if vi["primary_text_sources"]:
    stamp("PASS 1c: fetching primary texts")
    pass1c = call_or_cache(RUN / "01_research/primary_texts.json", "Pass 1c", _pass_1c)
    stamp(f"  fetched {pass1c['source_count']} sources, {pass1c['total_chars']} total chars")
else:
    stamp("PASS 1c: SKIPPED (no primary_text_sources)")
    pass1c = {"passages": []}


# ---------- PASS 1-MERGE (degraded — only Pass 1a available) ----------
merged_dossier = dossier_text
write_json_atomic(RUN / "01_research/merged_dossier.json", {
    "voice_name": vi["name"], "voice_slug": SLUG,
    "merged_dossier": merged_dossier,
    "sources": ["pass_1a_perplexity"],
    "skipped": ["pass_1b_gemini", "pass_1merge_contradiction_check"],
    "skip_reasons": {
        "pass_1b_gemini": "Google project has zero free-tier quota",
        "pass_1merge": "trivially CLEAN with single source",
    },
    "degraded_mode": True,
})


# ---------- HELPER: Claude call wrapper for generation passes ----------
def _claude_pass(*, system, user, model, max_tokens=24000, thinking=True, temperature=1.0):
    return call_claude(
        system=system, user=user, model=model,
        max_tokens=max_tokens, temperature=temperature,
        thinking_budget=10000 if thinking else None,
        response_format_json=True,
    )


# ---------- HELPER: coherence threading compress ----------
def _ct_compress(prior_pass_output: dict, label: str) -> str:
    ct_path = RUN / f"02_passes/_ct_{label}.json"
    cached_v = cached(ct_path, f"CT compress {label}")
    if cached_v is not None:
        return cached_v["summary_text"]
    stamp(f"  CT compressing {label}...")
    user = render("persona_coherence_threading", name=vi["name"],
                  prior_pass_output_json=json.dumps(prior_pass_output, ensure_ascii=False))
    r = call_claude(system="You compress persona fields into a tight summary.",
                    user=user, model="claude-sonnet-4-6", max_tokens=2048,
                    temperature=0.0, thinking_budget=None)
    write_json_atomic(ct_path, {"label": label, "model": r["model"], "usage": r["usage"],
                                "summary_text": r["text"]})
    return r["text"]


# ---------- PASS 2 (Identity & Boundaries) ----------
def _pass_2():
    sysp = render("persona_pass_2_identity_boundaries", name=vi["name"], type=vi["type"],
                  subtype=vi.get("subtype"), voice_mode=vi["voice_mode"],
                  hostile_sources=vi["hostile_sources"])
    userp = render("persona_pass_2_user", merged_dossier=merged_dossier)
    r = _claude_pass(system=sysp, user=userp, model="claude-opus-4-6")
    return {"voice_name": vi["name"], "voice_slug": SLUG, "pass": "2_identity_boundaries",
            "model": r["model"], "usage": r["usage"], "fields": r["json"]}

stamp("PASS 2: Identity & Boundaries (Opus + thinking)")
pass2 = call_or_cache(RUN / "02_passes/pass2_identity_boundaries.json", "Pass 2", _pass_2)
pass_2_summary = _ct_compress(pass2["fields"], "pass2")


# ---------- PASS 3 (Intellectual Core) ----------
def _pass_3():
    sysp = render("persona_pass_3_intellectual_core", name=vi["name"], type=vi["type"],
                  subtype=vi.get("subtype"), voice_mode=vi["voice_mode"],
                  hostile_sources=vi["hostile_sources"])
    userp = render("persona_pass_3_user", merged_dossier=merged_dossier,
                   chatgpt_supplement=None, pass_2_summary=pass_2_summary)
    r = _claude_pass(system=sysp, user=userp, model="claude-opus-4-6")
    return {"voice_name": vi["name"], "voice_slug": SLUG, "pass": "3_intellectual_core",
            "model": r["model"], "usage": r["usage"], "fields": r["json"]}

stamp("PASS 3: Intellectual Core (Opus + thinking, ~5 min)")
pass3 = call_or_cache(RUN / "02_passes/pass3_intellectual_core.json", "Pass 3", _pass_3)
combined_2_3 = {**pass2["fields"], **pass3["fields"]}
pass_2_3_summary = _ct_compress(combined_2_3, "pass2_3")


# ---------- PASS 4a (Voice) — corpus-grounded ----------
# Concatenate first ~80K chars of primary texts (avoid blowing context budget)
def _build_primary_texts_block():
    if not pass1c.get("passages"):
        return "[NO PRIMARY TEXTS — output will be from training data; flag voice_basis as 'training-data']"
    parts = []
    budget = 80000
    for p in pass1c["passages"]:
        if "error" in p or not p.get("text"):
            continue
        snippet = p["text"][:max(0, budget)]
        parts.append(f"=== SOURCE: {p['url']} ({p['source']}, {p['char_count']} chars) ===\n{snippet}")
        budget -= len(snippet)
        if budget <= 0:
            break
    return "\n\n".join(parts) if parts else "[NO USABLE PASSAGES]"

primary_block = _build_primary_texts_block()
stamp(f"  primary_texts block built: {len(primary_block)} chars (budget cap 80K)")

def _pass_4a():
    sysp = render("persona_pass_4a_voice", name=vi["name"], type=vi["type"],
                  subtype=vi.get("subtype"), voice_mode=vi["voice_mode"],
                  hostile_sources=vi["hostile_sources"],
                  corpus_constraint=vi.get("corpus_constraint", "full"))
    userp = render("persona_pass_4a_user", merged_dossier=merged_dossier,
                   primary_texts=primary_block, pass_2_3_summary=pass_2_3_summary)
    r = _claude_pass(system=sysp, user=userp, model="claude-sonnet-4-6",
                     max_tokens=8000, thinking=False, temperature=0.3)
    return {"voice_name": vi["name"], "voice_slug": SLUG, "pass": "4a_voice",
            "model": r["model"], "usage": r["usage"], "fields": r["json"],
            "voice_basis": "corpus-based" if pass1c.get("passages") else "training-data"}

stamp("PASS 4a: Voice (Sonnet, corpus-grounded)")
pass4a = call_or_cache(RUN / "02_passes/pass4a_voice.json", "Pass 4a", _pass_4a)
combined_2_3_4a = {**combined_2_3, **pass4a["fields"]}
pass_2_3_4a_summary = _ct_compress(combined_2_3_4a, "pass2_3_4a")


# ---------- PASS 4b (Artifact) ----------
def _pass_4b():
    sysp = render("persona_pass_4b_artifact", name=vi["name"], type=vi["type"])
    userp = render("persona_pass_4b_user",
                   pass_2_3_4a_summary=pass_2_3_4a_summary,
                   rhetorical_mode=json.dumps(pass4a["fields"].get("rhetorical_mode", "")),
                   characteristic_moves=json.dumps(pass4a["fields"].get("characteristic_moves", [])),
                   register_and_tone=json.dumps(pass4a["fields"].get("register_and_tone", "")))
    r = _claude_pass(system=sysp, user=userp, model="claude-sonnet-4-6",
                     max_tokens=6144, thinking=False, temperature=0.2)
    return {"voice_name": vi["name"], "voice_slug": SLUG, "pass": "4b_artifact",
            "model": r["model"], "usage": r["usage"], "fields": r["json"]}

stamp("PASS 4b: Artifact (Sonnet)")
pass4b = call_or_cache(RUN / "02_passes/pass4b_artifact.json", "Pass 4b", _pass_4b)
combined_2_3_4 = {**combined_2_3_4a, **pass4b["fields"]}
pass_2_3_4_summary = _ct_compress(combined_2_3_4, "pass2_3_4")


# ---------- PASS 5 (Engagement) ----------
def _pass_5():
    sysp = render("persona_pass_5_engagement", name=vi["name"], type=vi["type"],
                  voice_mode=vi["voice_mode"])
    userp = render("persona_pass_5_user", pass_2_3_4_summary=pass_2_3_4_summary)
    r = _claude_pass(system=sysp, user=userp, model="claude-sonnet-4-6",
                     max_tokens=4096, thinking=True, temperature=1.0)
    return {"voice_name": vi["name"], "voice_slug": SLUG, "pass": "5_engagement",
            "model": r["model"], "usage": r["usage"], "fields": r["json"]}

stamp("PASS 5: Engagement (Sonnet + thinking)")
pass5 = call_or_cache(RUN / "02_passes/pass5_engagement.json", "Pass 5", _pass_5)


# ---------- PASS 6 (Corpus Curation) ----------
def _pass_6():
    if not pass1c.get("passages"):
        return {"voice_name": vi["name"], "voice_slug": SLUG, "pass": "6_corpus_curation",
                "status": "HALTED", "reason": "No primary_texts available — Pass 6 cannot run per spec.",
                "fields": {}}
    sysp = render("persona_pass_6_corpus", name=vi["name"],
                  corpus_constraint=vi.get("corpus_constraint", "full"))
    userp = render("persona_pass_6_user", primary_texts=primary_block,
                   pass_2_3_4a_summary=pass_2_3_4a_summary)
    r = _claude_pass(system=sysp, user=userp, model="claude-sonnet-4-6",
                     max_tokens=8000, thinking=False, temperature=0.1)
    return {"voice_name": vi["name"], "voice_slug": SLUG, "pass": "6_corpus_curation",
            "model": r["model"], "usage": r["usage"], "fields": r["json"]}

stamp("PASS 6: Corpus Curation (Sonnet, selection task)")
pass6 = call_or_cache(RUN / "02_passes/pass6_corpus.json", "Pass 6", _pass_6)


# ---------- FINAL SUMMARY ----------
def _check_register(card_fields: dict, voice_last_name: str) -> int:
    """Count third-person leaks (voice_last_name + " was/is/believed/argued" patterns)."""
    flags = [f"{voice_last_name}'s ", f"{voice_last_name} was", f"{voice_last_name} is",
             f"{voice_last_name} believed", f"{voice_last_name} argued"]
    n = 0
    for fv in card_fields.values():
        t = json.dumps(fv) if not isinstance(fv, str) else fv
        for flag in flags:
            if flag in t:
                n += 1
    return n


full_card = {**combined_2_3_4, **pass5["fields"]}
if pass6.get("fields"):
    full_card.update(pass6["fields"])

last_name = vi["name"].split()[-1]
register_violations = _check_register(full_card, last_name)

print()
stamp("=" * 60)
stamp(f"PIPELINE COMPLETE for {vi['name']}")
stamp("=" * 60)
stamp(f"  Voice slug:           {SLUG}")
stamp(f"  Pass 2 fields:        {len(pass2['fields'])}")
stamp(f"  Pass 3 fields:        {len(pass3['fields'])}")
stamp(f"  Pass 4a fields:       {len(pass4a['fields'])} (voice_basis: {pass4a['voice_basis']})")
stamp(f"  Pass 4b fields:       {len(pass4b['fields'])}")
stamp(f"  Pass 5 fields:        {len(pass5['fields'])}")
stamp(f"  Pass 6 fields:        {len(pass6.get('fields', {}))}")
stamp(f"  Total card fields:    {len(full_card)}")
stamp(f"  Output Register check: {register_violations} violations ({'CLEAN' if register_violations == 0 else 'NEEDS REVIEW'})")
stamp(f"  Card saved to:        {RUN}/02_passes/")
stamp("=" * 60)

write_json_atomic(RUN / "persona_card_assembled.json", {
    "voice_name": vi["name"], "voice_slug": SLUG,
    "field_counts": {"pass2": len(pass2["fields"]), "pass3": len(pass3["fields"]),
                     "pass4a": len(pass4a["fields"]), "pass4b": len(pass4b["fields"]),
                     "pass5": len(pass5["fields"]), "pass6": len(pass6.get("fields", {}))},
    "total_fields": len(full_card),
    "voice_basis": pass4a["voice_basis"],
    "register_violations": register_violations,
    "card": full_card,
})
stamp(f"Assembled card -> {RUN}/persona_card_assembled.json")
