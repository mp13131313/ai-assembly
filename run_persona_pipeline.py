"""End-to-end Persona Pipeline runner for a single voice.

Walks: Node 0 -> Pass 1a (Perplexity) + Pass 1a-DR (Claude Deep Research file)
+ Pass 1b (Gemini) -> Pass 1c -> Pass 1-merge (3-way) -> Pass 2 -> CT
-> Pass 3 (+ DR supplement if triggered) -> CT -> Pass 1d (excerpt selection)
-> Pass 4a -> CT -> Pass 4b -> CT -> Pass 5 -> Pass 6 -> assembled card.

APPROACH C (active default for all voices): Pass 1a is augmented by a manually-
produced Claude Deep Research markdown file at inputs/dossiers/<voice_slug>_claude_dr.md
(referenced via the input JSON's pass_1a_claude_dr_file field). Pass 1-merge
does a three-way contradiction check across Perplexity + Claude DR + Gemini.
If the file is missing the runner falls back to two-source merge with a warning.

Designed for resumability: each pass writes its output JSON before the next
pass starts. If a pass already exists, it's loaded from disk instead of
re-called. To force a re-run, delete the output JSON.
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
from flows.shared.clients import call_claude, call_perplexity, call_openai, call_gemini
from flows.shared.node1c_fetch import fetch_all
from flows.shared.node1d_excerpt_selection import build_structural_index, apply_selections


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


# ---------- PASS 1a-DR (Claude Deep Research, manually produced) ----------
# Approach C: Pass 1a is augmented by a manually-produced Claude Deep Research
# markdown file. The user runs claude.ai with Opus 4.6 + extended thinking +
# Deep Research feature (60-120 min wall time per voice), exports the result
# to inputs/dossiers/<voice_slug>_claude_dr.md, and references it in the
# voice's input JSON as pass_1a_claude_dr_file.
claude_dr_text = ""
claude_dr_file = vi.get("pass_1a_claude_dr_file")
if claude_dr_file:
    p = Path(claude_dr_file)
    if not p.is_absolute():
        p = Path("/Users/aienvironment/Desktop/ai-assembly-personas") / p
    if p.exists():
        claude_dr_text = p.read_text()
        stamp(f"PASS 1a-DR: loaded Claude Deep Research from {p.name} ({len(claude_dr_text)} chars)")
        write_json_atomic(RUN / "01_research/claude_dr_dossier.json", {
            "voice_name": vi["name"], "voice_slug": SLUG, "pass": "1a_dr_claude_deep_research",
            "source_file": str(p), "char_count": len(claude_dr_text), "text": claude_dr_text,
        })
    else:
        stamp(f"PASS 1a-DR: WARN file not found: {p} — falling back to 2-source merge")
else:
    stamp("PASS 1a-DR: no pass_1a_claude_dr_file in input — falling back to 2-source merge (Perplexity + Gemini only)")


# ---------- PASS 1b (Gemini broad scan) ----------
def _pass_1b():
    prompt = render("persona_pass_1b_broad_scan", name=vi["name"])
    r = call_gemini(user=prompt, temperature=0.2, max_output_tokens=16384)
    return {"voice_name": vi["name"], "voice_slug": SLUG, "pass": "1b_broad_scan",
            "model": r["model"], "usage": r["usage"], "text": r["text"]}

stamp("PASS 1b: Gemini broad scan")
pass1b = call_or_cache(RUN / "01_research/gemini_broad_scan.json", "Pass 1b", _pass_1b)
broad_scan_text = pass1b["text"]
stamp(f"  broad scan: {len(broad_scan_text)} chars")


# ---------- PASS 1-MERGE (Claude contradiction check, three-way: Perplexity + Claude DR + Gemini) ----------
def _pass_1merge():
    sysp = open("flows/shared/prompts/persona_pass_1merge_contradiction_system.md").read().strip()
    userp = render("persona_pass_1merge_three_way_user",
                   perplexity_dossier=dossier_text,
                   claude_dr_dossier=claude_dr_text or None,
                   gemini_broad_scan=broad_scan_text)
    r = call_claude(system=sysp, user=userp, model="claude-sonnet-4-6",
                    max_tokens=4096, temperature=0.0, thinking_budget=None,
                    response_format_json=True)
    return {"voice_name": vi["name"], "voice_slug": SLUG, "pass": "1merge_contradiction_check",
            "model": r["model"], "usage": r["usage"], "result": r["json"],
            "sources_compared": ["perplexity"] + (["claude_dr"] if claude_dr_text else []) + ["gemini"]}

n_sources = 2 + (1 if claude_dr_text else 0)
stamp(f"PASS 1-merge: contradiction check ({n_sources}-way, Sonnet)")
pass1merge = call_or_cache(RUN / "01_research/contradiction_check.json", "Pass 1-merge", _pass_1merge)
merge_status = pass1merge["result"].get("status", "UNKNOWN")
stamp(f"  status: {merge_status}")

# Build merged_dossier: all available sources concatenated + contradiction flags
merged_dossier_parts = [
    "=== PRIMARY DOSSIER (Perplexity sonar-deep-research) ===",
    dossier_text,
]
if claude_dr_text:
    merged_dossier_parts += [
        "",
        "=== CLAUDE DEEP RESEARCH DOSSIER (Opus 4.6 + extended thinking + DR) ===",
        claude_dr_text,
    ]
merged_dossier_parts += [
    "",
    "=== BROAD SCAN SUPPLEMENT (Gemini 2.5 Pro) ===",
    broad_scan_text,
]
if merge_status == "CONTRADICTIONS":
    items = pass1merge["result"].get("items", [])
    merged_dossier_parts += [
        "",
        f"=== FLAGGED CONTRADICTIONS ({len(items)}) ===",
        "Subsequent passes should treat the following as flagged for caution:",
    ]
    for i, item in enumerate(items, 1):
        merged_dossier_parts += [f"\n[{i}] Assessment: {item.get('assessment', '?')}"]
        # New shape: claims is a list of {source, claim}
        claims = item.get("claims", [])
        if claims:
            for c in claims:
                merged_dossier_parts.append(f"    Source {c.get('source', '?')}: {c.get('claim', '')}")
        else:
            # Backward-compat with old two-source shape
            merged_dossier_parts += [
                f"    Claim A: {item.get('claim_a', '')}",
                f"    Claim B: {item.get('claim_b', '')}",
            ]
merged_dossier = "\n".join(merged_dossier_parts)

write_json_atomic(RUN / "01_research/merged_dossier.json", {
    "voice_name": vi["name"], "voice_slug": SLUG,
    "merged_dossier": merged_dossier,
    "sources": pass1merge.get("sources_compared", []),
    "contradiction_check": pass1merge["result"],
    "approach_c": bool(claude_dr_text),
    "degraded_mode": False,
})
stamp(f"  merged_dossier: {len(merged_dossier)} chars")


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
# Conditional ChatGPT DR supplement per v3.7 spec — fires when ANY of:
#   (a) needs_dr_supplement is True
#   (b) dossier INTELLECTUAL FRAMEWORK section < 500 words
#   (c) voice_mode == "observational"
def _should_dr_supplement() -> tuple[bool, str]:
    if vi.get("needs_dr_supplement"):
        return True, "needs_dr_supplement=True in input"
    if vi["voice_mode"] == "observational":
        return True, "voice_mode is observational"
    # Word count of INTELLECTUAL FRAMEWORK section in dossier
    import re
    m = re.search(r"INTELLECTUAL FRAMEWORK(.*?)(?=\n#+\s|\Z)", merged_dossier, flags=re.DOTALL | re.IGNORECASE)
    if m:
        words = len(m.group(1).split())
        if words < 500:
            return True, f"INTELLECTUAL FRAMEWORK section is {words} words (<500)"
    return False, "no trigger conditions met"

def _pass_3_dr_supplement():
    prompt = (
        f"Analyse the intellectual framework of {vi['name']}, focusing specifically on:\n"
        "1. Their characteristic reasoning method — how they move through a problem\n"
        "2. Internal tensions or contradictions in their thought\n"
        "3. Key concepts they use with distinctive precision\n"
        "4. How their positions evolved over their lifetime\n"
        "5. Minority scholarly readings beyond the standard interpretation\n\n"
        "Draw on scholarly sources beyond the most commonly cited works. Include "
        "specific textual references (work title, chapter/section) for each claim."
    )
    r = call_openai(system="You are a scholar of intellectual history conducting deep research.",
                    user=prompt, model="gpt-4o", temperature=0.3, max_tokens=16000)
    return {"voice_name": vi["name"], "voice_slug": SLUG, "pass": "3_dr_supplement",
            "model": r["model"], "usage": r["usage"], "text": r["text"]}

dr_should, dr_reason = _should_dr_supplement()
chatgpt_supplement_text = None
if dr_should:
    stamp(f"PASS 3 DR supplement: triggered ({dr_reason})")
    try:
        dr_path = RUN / "01_research/chatgpt_dr_supplement.json"
        dr_result = call_or_cache(dr_path, "Pass 3 DR supplement", _pass_3_dr_supplement)
        chatgpt_supplement_text = dr_result["text"]
    except Exception as e:
        stamp(f"  WARN: DR supplement failed ({type(e).__name__}: {str(e)[:120]}); proceeding without")
else:
    stamp(f"PASS 3 DR supplement: skipped ({dr_reason})")

def _pass_3():
    sysp = render("persona_pass_3_intellectual_core", name=vi["name"], type=vi["type"],
                  subtype=vi.get("subtype"), voice_mode=vi["voice_mode"],
                  hostile_sources=vi["hostile_sources"])
    userp = render("persona_pass_3_user", merged_dossier=merged_dossier,
                   chatgpt_supplement=chatgpt_supplement_text, pass_2_summary=pass_2_summary)
    r = _claude_pass(system=sysp, user=userp, model="claude-opus-4-6")
    return {"voice_name": vi["name"], "voice_slug": SLUG, "pass": "3_intellectual_core",
            "model": r["model"], "usage": r["usage"], "fields": r["json"]}

stamp("PASS 3: Intellectual Core (Opus + thinking, ~5 min)")
pass3 = call_or_cache(RUN / "02_passes/pass3_intellectual_core.json", "Pass 3", _pass_3)
combined_2_3 = {**pass2["fields"], **pass3["fields"]}
pass_2_3_summary = _ct_compress(combined_2_3, "pass2_3")


# ---------- PASS 4a (Voice) — corpus-grounded ----------
# Pass 1d (Excerpt Selection): use Sonnet to curate ~30K chars of representative
# passages from the fetched primary_texts, guided by the dossier's identification
# of important works/scenes. Replaces the prior naive first-80K-character slice.
def _pass_1d():
    if not pass1c.get("passages"):
        return {"voice_name": vi["name"], "voice_slug": SLUG, "pass": "1d_excerpt_selection",
                "status": "SKIPPED", "reason": "No primary_texts to select from",
                "selections": [], "selected_text": "[NO PRIMARY TEXTS — output will be from training data; flag voice_basis as 'training-data']"}
    structural_index = build_structural_index(pass1c["passages"])
    user_prompt = render("persona_pass_1d_excerpt_selection",
                         name=vi["name"], merged_dossier=merged_dossier,
                         structural_index=structural_index)
    r = call_claude(system="You are a textual scholar curating excerpt selections for an AI persona's primary-text grounding.",
                    user=user_prompt,
                    model="claude-sonnet-4-6", max_tokens=4096,
                    temperature=0.0, thinking_budget=None,
                    response_format_json=True)
    selections = r["json"].get("selections", [])
    selected_text = apply_selections(pass1c["passages"], selections)
    return {"voice_name": vi["name"], "voice_slug": SLUG, "pass": "1d_excerpt_selection",
            "model": r["model"], "usage": r["usage"],
            "selection_count": len(selections), "selected_chars": len(selected_text),
            "selections": selections, "selected_text": selected_text}

stamp("PASS 1d: Excerpt Selection (Sonnet, curated subset)")
pass1d = call_or_cache(RUN / "01_research/excerpt_selections.json", "Pass 1d", _pass_1d)
primary_block = pass1d["selected_text"]
stamp(f"  primary_texts block: {len(primary_block)} chars from {pass1d.get('selection_count', 0)} curated selections")

def _pass_4a():
    sysp = render("persona_pass_4a_voice", name=vi["name"], type=vi["type"],
                  subtype=vi.get("subtype"), voice_mode=vi["voice_mode"],
                  hostile_sources=vi["hostile_sources"],
                  corpus_constraint=vi.get("corpus_constraint", "full"))
    userp = render("persona_pass_4a_user", merged_dossier=merged_dossier,
                   primary_texts=primary_block, pass_2_3_summary=pass_2_3_summary)
    # Opus + adaptive thinking: long-context pattern recognition across primary
    # texts. Especially load-bearing for hard voice types (musical, system, etc.)
    r = _claude_pass(system=sysp, user=userp, model="claude-opus-4-6",
                     max_tokens=24000, thinking=True, temperature=1.0)
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
    userp = render(
        "persona_pass_5_user",
        pass_2_3_4_summary=pass_2_3_4_summary,
        constitution=json.dumps(pass3["fields"].get("constitution", ""), ensure_ascii=False, indent=2),
        reasoning_method=json.dumps(pass3["fields"].get("reasoning_method", ""), ensure_ascii=False, indent=2),
    )
    r = _claude_pass(system=sysp, user=userp, model="claude-opus-4-6",
                     max_tokens=16000, thinking=True, temperature=1.0)
    return {"voice_name": vi["name"], "voice_slug": SLUG, "pass": "5_engagement",
            "model": r["model"], "usage": r["usage"], "fields": r["json"]}

stamp("PASS 5: Engagement (Opus + thinking)")
pass5 = call_or_cache(RUN / "02_passes/pass5_engagement.json", "Pass 5", _pass_5)


# ---------- PASS 6 (Corpus Curation) ----------
def _pass_6():
    if not pass1c.get("passages"):
        # Spec HALT pattern: mark the field BLOCKED so assembled card surfaces
        # the issue, rather than missing the key entirely.
        return {"voice_name": vi["name"], "voice_slug": SLUG, "pass": "6_corpus_curation",
                "status": "HALTED",
                "reason": "No primary_texts available — Pass 6 cannot run per spec.",
                "fields": {"curated_corpus_passages": "BLOCKED — awaiting Node 1c manual provision"}}
    sysp = render("persona_pass_6_corpus", name=vi["name"],
                  corpus_constraint=vi.get("corpus_constraint", "full"))
    userp = render(
        "persona_pass_6_user",
        primary_texts=primary_block,
        merged_dossier=merged_dossier,
        pass_2_3_4a_summary=pass_2_3_4a_summary,
        constitution=json.dumps(pass3["fields"].get("constitution", ""), ensure_ascii=False, indent=2),
        concept_lexicon=json.dumps(pass3["fields"].get("concept_lexicon", ""), ensure_ascii=False, indent=2),
        reasoning_method=json.dumps(pass3["fields"].get("reasoning_method", ""), ensure_ascii=False, indent=2),
        rhetorical_mode=json.dumps(pass4a["fields"].get("rhetorical_mode", ""), ensure_ascii=False),
        characteristic_moves=json.dumps(pass4a["fields"].get("characteristic_moves", []), ensure_ascii=False, indent=2),
        register_and_tone=json.dumps(pass4a["fields"].get("register_and_tone", ""), ensure_ascii=False),
    )
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
    # Spec wants 37 card fields flat at root + a metadata block.
    "voice_name": vi["name"],
    "voice_mode": vi["voice_mode"],
    "pipeline_version": "3.7",
    "generated_date": time.strftime("%Y-%m-%d"),

    # All 35 generated card fields, flat at root level
    **full_card,

    # Runtime continuity fields (populated by Voice Pipeline at deployment, not
    # by Persona Pipeline). Initialized null so consumers don't get KeyError.
    "continuity_block_if_night_2": None,
    "continuity_block_artifact_if_night_2": None,

    "metadata": {
        "passes_completed": [
            "1a_perplexity", "1c_primary_text_fetch",
            "2_identity_boundaries", "ct_pass2",
            "3_intellectual_core", "ct_pass2_3",
            "4a_voice", "ct_pass2_3_4a",
            "4b_artifact", "ct_pass2_3_4",
            "5_engagement",
            "6_corpus_curation" if pass6.get("status") != "HALTED" else "6_corpus_curation_HALTED",
        ],
        "validation_status": "pending — Phase 3 not yet built",
        "revision_loops": 0,
        "tools_used": ["perplexity:sonar-deep-research", "anthropic:claude-opus-4-6", "anthropic:claude-sonnet-4-6", "gutenberg:web_fetch"],
        "voice_basis": pass4a["voice_basis"],
        "hostile_sources": vi["hostile_sources"],
        "corpus_constraint": vi.get("corpus_constraint", "full"),
        "subtype": vi.get("subtype"),
        "deployment_context": vi.get("conference_context", ""),
        "human_review_status": "pending",
        # Diagnostic extras (not in spec but useful for our development)
        "field_counts": {
            "pass2": len(pass2["fields"]), "pass3": len(pass3["fields"]),
            "pass4a": len(pass4a["fields"]), "pass4b": len(pass4b["fields"]),
            "pass5": len(pass5["fields"]), "pass6": len(pass6.get("fields", {})),
        },
        "register_violations": register_violations,
    },
})
stamp(f"Assembled card -> {RUN}/persona_card_assembled.json")
