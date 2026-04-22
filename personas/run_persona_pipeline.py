"""End-to-end Persona Pipeline runner for a single voice.

Starts from Pass 1-merge. Requires that Pass 1a (Perplexity) and Pass 1b
(Gemini) have already been run by run_phase0_1_research.py, which also
produces the Pass 0b Claude DR prompt. The manual Claude DR session
(Pass 1a-DR) must also be complete before this runner starts.

Walks: Node 0 -> Pass 1a-DR load -> Pass 1-merge (3-way) -> Pass 1c-extract
-> Pass 1c (fetch) -> primary-text review gate -> Pass 1d -> Pass 2 -> CT
-> Pass 3 -> CT -> Pass 4a -> CT -> Pass 4b -> CT -> Pass 5 -> Pass 6
-> Pass 7-pre -> Pass 7a -> revision loop -> Pass 7b -> Pass 7c -> Derive
-> assembled card.

Designed for resumability: each pass writes its output JSON before the next
pass starts. If a pass already exists, it's loaded from disk instead of
re-called. To force a re-run, delete the output JSON.
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
load_dotenv(REPO_ROOT.parent / ".env", override=True)


from flows.shared import paths as _paths
from flows.shared.chunk_runner import detect_dr_mode
from flows.shared.dr_validation import validate_dr_dossier
from flows.shared.io import load_prompt, load_voice_input, voice_slug, write_json_atomic
from flows.shared.node0_validation import validate_input
from flows.shared.project_root import add_project_arg, resolve_project_root
from flows.shared.prompt_render import render
from flows.shared.clients import call_claude, call_gemini, call_openai
from flows.shared.node1c_fetch import fetch_all
from flows.shared.node1d_excerpt_selection import build_structural_index, apply_selections


_parser = argparse.ArgumentParser(description="End-to-end Persona Pipeline for a single voice")
_parser.add_argument("name", help='Voice name, e.g. "Plato" or "Hannah Arendt"')
add_project_arg(_parser)
_args = _parser.parse_args()

PROJECT_ROOT = resolve_project_root(_args.project, repo_root=REPO_ROOT)

VOICE_NAME = _args.name
SLUG = voice_slug(VOICE_NAME)


def _load_conference_context_string() -> str:
    """Assemble the short conference-context string for Pass 7b / metadata.

    Phase B dropped the `conference_context` field from voice_config; runners
    that still need the short context paragraph (Pass 7b; pipeline metadata)
    read it directly from the split conference_facts.json under PROJECT_ROOT.
    """
    facts_path = _paths.conference_facts(PROJECT_ROOT)
    if facts_path.exists():
        facts = json.loads(facts_path.read_text())
        return facts.get("conference_context_paragraph", "")
    return ""

_paths.ensure_voice_dirs(SLUG, PROJECT_ROOT)


def stamp(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def cached(path: Path, label: str):
    """Return parsed JSON if path exists, else None and log."""
    if path.exists():
        stamp(f"  CACHE HIT: {label} -> {path.name}")
        with path.open(encoding="utf-8") as f:
            return json.load(f)
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
stamp(f"NODE 0: validating {VOICE_NAME}  (PROJECT_ROOT={PROJECT_ROOT})")
vi = validate_input(load_voice_input(VOICE_NAME, PROJECT_ROOT))
stamp(f"  type={vi['type']} voice_mode={vi['voice_mode']} hostile={vi['hostile_sources']}")


# ---------- VALIDATE PRE-COMPUTED PASS 1a + 1b OUTPUTS ----------
# Pass 1a (Perplexity) and Pass 1b (Gemini) must be run BEFORE this script
# via run_phase0_1_research.py. Check that both outputs exist.
_pass1a_path = _paths.perplexity_dossier(SLUG, PROJECT_ROOT)
_pass1b_path = _paths.gemini_broad_scan(SLUG, PROJECT_ROOT)
_missing = [str(p.relative_to(PROJECT_ROOT)) for p in [_pass1a_path, _pass1b_path] if not p.exists()]
if _missing:
    sys.exit(
        "Pass 1a + 1b outputs missing. Run run_phase0_1_research.py first:\n"
        f"  python3 run_phase0_1_research.py \"{VOICE_NAME}\"\n"
        f"Missing: {', '.join(_missing)}"
    )

pass1a = cached(_pass1a_path, "Pass 1a (pre-computed)")
dossier_text = pass1a.get("text") or pass1a.get("text_clean", "")
stamp(f"PASS 1a: loaded Perplexity dossier ({len(dossier_text)} chars)")

pass1b = cached(_pass1b_path, "Pass 1b (pre-computed)")
broad_scan_text = pass1b["text"]
stamp(f"PASS 1b: loaded Gemini broad scan ({len(broad_scan_text)} chars)")


# ---------- DR MODE DETECTION ----------
# Auto-detect per-section vs monolithic DR mode. Errors cleanly on partial state.
try:
    dr_mode = detect_dr_mode(SLUG, PROJECT_ROOT)
    stamp(f"PASS 1a-DR: detected DR mode = {dr_mode}")
    if dr_mode == "per_section":
        dr_dossier_path = _paths.dr_dossier_dir(SLUG, PROJECT_ROOT)
        validate_dr_dossier(dr_dossier_path)
        claude_dr_text = "per_section"  # signals DR is present; chunk_runner loads per-section
    else:
        monolithic_path = _paths.concat_claude_dr(SLUG, PROJECT_ROOT)
        validate_dr_dossier(monolithic_path)
        claude_dr_text = monolithic_path.read_text(encoding="utf-8")
        stamp(f"  monolithic DR: {len(claude_dr_text):,} chars")
except RuntimeError as e:
    stamp(f"ERROR: {e}")
    sys.exit(1)


# ---------- PHASE B CHUNKED PASS 1 MERGE ----------
# Replaces v3.10's monolithic contradiction-check merge with the 6+1 chunked
# merge (Pass 1.1-1.7). Run via the Phase B orchestrator which handles
# parallel chunk execution + coherence pass + Pydantic validation + atomic
# writes. Output shape is the MergedDossier Pydantic schema at
# personas/schemas/merged_dossier.py (16 chunk keys + coherence_flags +
# coherence_resolutions) rather than v3.10's concatenated-markdown blob.
#
# Pass 2-6 prompts (updated in Phase H) read from merged_dossier.<chunk_key>
# paths into this JSON shape. We serialize the dossier dict and pass it as
# the `merged_dossier` template variable — the same variable name Pass 2-6
# user prompts already use, so no prompt changes needed here.
stamp("PASS 1 (Phase B): chunked merge 1.1-1.7 (parallel + coherence)")
_merged_dossier_path = _paths.merged_dossier(SLUG, PROJECT_ROOT)
if _merged_dossier_path.exists():
    # Cached: load prior run's chunked merged_dossier as-is.
    stamp(f"  CACHE HIT: loading {_merged_dossier_path.name}")
    merged_dossier_dict = json.loads(_merged_dossier_path.read_text())
else:
    from run_pass_1_all import run_pass_1_all  # noqa: E402 — deferred to runtime
    merged_dossier_dict = run_pass_1_all(
        name=vi["name"],
        voice_type=vi["type"],
        subtype=vi.get("subtype"),
        voice_mode=vi.get("voice_mode") or "philosophical",
        use_test_fixtures=False,
        max_parallel=3,
        project_root=PROJECT_ROOT,
        dr_mode=dr_mode,
    )
    # run_pass_1_7 already writes merged_dossier.json to this path; the cache
    # branch above picks it up on re-run.

# The template variable Pass 2-6 see. JSON-serialized with indent for
# readability; Claude parses structured input from this cleanly.
merged_dossier = json.dumps(merged_dossier_dict, ensure_ascii=False, indent=2)
_n_flags = len(merged_dossier_dict.get("coherence_flags", []))
stamp(f"  merged_dossier: {len(merged_dossier)} chars; {_n_flags} coherence_flags")


# ---------- PASS 1c-extract: Extract primary text URLs from merged dossier ----------
# Primary text URLs are discovered by the three research sources (Perplexity,
# Claude DR, Gemini) in their Section 6 outputs, then extracted here by a
# Sonnet call. If the voice config has primary_text_sources populated (backward
# compat / manual override), those are used directly and extraction is skipped.

if vi["primary_text_sources"]:
    # Backward compat: manual override from voice config
    primary_text_urls = vi["primary_text_sources"]
    _extracted_url_items: list = []  # no extraction step, manual override
    stamp(f"PASS 1c-extract: SKIPPED (voice config has {len(primary_text_urls)} manual URLs)")
else:
    # 1-arch-07 (2026-04-22): URLs derived deterministically at render-time
    # from passages[].citation and works[] fields via extract_urls(). The
    # old `urls` chunk was LLM-emitted and invited drift vs. URLs already
    # embedded in sibling chunks. No LLM call — pure regex extraction.
    from flows.shared.url_extract import extract_urls as _extract_urls
    stamp("PASS 1c-extract: deriving URLs from works + passages chunks (no LLM, 1-arch-07)")
    _works_chunk = merged_dossier_dict.get("works", {})
    _passages_chunk = merged_dossier_dict.get("passages", {})
    _extracted_url_items = [
        {"url": u["url"], "work": u["work_title"], "source": u["source"],
         "note": u.get("license_or_access_note", "")}
        for u in _extract_urls(_works_chunk, _passages_chunk)
    ]
    primary_text_urls = [item["url"] for item in _extracted_url_items]
    stamp(f"  {len(primary_text_urls)} URLs derived from works + passages")
    notes = ""
    # Satisfy the downstream pass1c_extract reference with a synthetic cache entry.
    pass1c_extract = {
        "voice_name": vi["name"], "voice_slug": SLUG, "pass": "1c_extract_urls_phase_b",
        "result": {"primary_text_urls": _extracted_url_items, "extraction_notes": ""},
    }
    write_json_atomic(_paths.primary_text_urls(SLUG, PROJECT_ROOT), pass1c_extract)


# ---------- PASS 1c: Fetch primary texts ----------
def _pass_1c():
    fetched = fetch_all(primary_text_urls)
    return {"voice_name": vi["name"], "voice_slug": SLUG, "pass": "1c_primary_text_fetch",
            "source_count": len(fetched), "passages": fetched,
            "total_chars": sum(p["char_count"] for p in fetched)}

if primary_text_urls:
    stamp("PASS 1c: fetching primary texts")
    pass1c = call_or_cache(_paths.primary_texts(SLUG, PROJECT_ROOT), "Pass 1c", _pass_1c)
    stamp(f"  fetched {pass1c['source_count']} sources, {pass1c['total_chars']} total chars")
else:
    stamp("PASS 1c: SKIPPED (no primary text URLs found)")
    pass1c = {"passages": []}


# ---------- PASS 1c REVIEW GATE ----------
# Spec Node 1c: manual review required before pipeline proceeds to Pass 1d.
# Resumes on re-run when primary_texts_reviewed.flag is present.

def _write_primary_texts_review(review_path: Path) -> None:
    lines = [f"# Primary Text Review — {vi['name']}", ""]
    corpus = vi.get("corpus_constraint", "")
    subtype_v = vi.get("subtype", "")
    if corpus == "lyrics — describe patterns only":
        lines += [
            "**CORPUS CONSTRAINT: lyrics — describe patterns only**",
            "Lyrics are not fetchable by design. Supply an alternative corpus "
            "(interview transcripts, speeches, scholarly analyses of catalogue "
            "patterns) before Pass 4a and Pass 6 run.",
            "",
        ]
    if subtype_v == "system":
        lines += [
            "**SYSTEM ENTITY (subtype=system)**",
            "Legislation text, indigenous oral sources, and scholarly legal analyses "
            "may not be web-fetchable or may need specific editions. Review carefully "
            "and supplement manually as needed.",
            "",
        ]
    lines += ["## Extracted URLs", ""]
    if not _extracted_url_items:
        lines.append("_URLs came from manual voice_config override (primary_text_sources field)._")
    else:
        for item in _extracted_url_items:
            lines.append(f"- {item.get('url', '?')}")
    lines.append("")
    lines += ["## Fetch Results", ""]
    passages = pass1c.get("passages", [])
    if not passages:
        lines.append("_No URLs fetched._")
    else:
        for p in passages:
            url = p.get("url", "?")
            if p.get("error"):
                err = p["error"]
                if "timeout" in err.lower():
                    tag = "TIMEOUT"
                elif "404" in err:
                    tag = "404"
                elif "private" in err.lower() or "ssrf" in err.lower():
                    tag = "SSRF-BLOCKED"
                else:
                    tag = "ERROR"
                lines.append(f"- FAIL [{tag}] {url}")
                lines.append(f"  {err}")
            else:
                lines.append(f"- OK {url} — {p['char_count']:,} chars (source: {p['source']})")
    lines += [
        "",
        "## Next Steps",
        "",
        "1. Review fetch results above.",
        f"2. Optionally edit voices/{SLUG}/03_corpus/01_primary_texts.json to add or replace passages.",
        f"3. Create the flag to continue: touch voices/{SLUG}/03_corpus/03_primary_texts_reviewed.flag",
        f"4. Re-run: python3 run_persona_pipeline.py \"{vi['name']}\"",
    ]
    review_path.write_text("\n".join(lines), encoding="utf-8")

_review_flag = _paths.primary_texts_reviewed_flag(SLUG, PROJECT_ROOT)
if not _review_flag.exists():
    _review_path = _paths.primary_texts_review(SLUG, PROJECT_ROOT)
    _write_primary_texts_review(_review_path)
    sys.exit(
        f"\n=== PASS 1c REVIEW GATE ===\n"
        f"Primary text fetch complete. Human review required before pipeline continues.\n\n"
        f"  1. Read:    {_review_path.relative_to(PROJECT_ROOT)}\n"
        f"  2. Edit:    {_paths.primary_texts(SLUG, PROJECT_ROOT).relative_to(PROJECT_ROOT)} "
        f"(add/replace passages if needed)\n"
        f"  3. Create:  touch {_review_flag.relative_to(PROJECT_ROOT)}\n"
        f"  4. Re-run:  python3 run_persona_pipeline.py \"{vi['name']}\"\n"
    )
stamp("PASS 1c gate: review flag present — continuing to Pass 1d")


# ---------- REVISION LOOP STATE ----------
# Per v3.7 spec: when Pass 7a returns REVISION_NEEDED, re-run flagged passes
# with critique appended to user prompt. Max 2 loops before flagging for
# human review. Critiques are populated from Pass 7a's field_issues array.
REVISION_CRITIQUES = {}  # pass_label (str) -> critique block (str)

def _critique_suffix(pass_label: str) -> str:
    """Return revision critique block appended to a generation pass's user
    prompt when set. Empty string when not in a revision loop."""
    crit = REVISION_CRITIQUES.get(pass_label)
    if not crit:
        return ""
    return (
        f"\n\n=== REVISION REQUEST (Pass 7a flagged this pass) ===\n"
        f"A cross-model validator reviewed your previous output and flagged "
        f"the following issues. Address each one in your revised output:\n\n"
        f"{crit}\n"
        f"=== END REVISION REQUEST ===\n"
    )


# ---------- HELPER: Claude call wrapper for generation passes ----------
# 1-arch-03 max_tokens bump: default 24000 → 32000 per plan §6.2. Under
# additive merge, Pass 2/3/4a/6 read richer merged_dossier (300-400K chars
# vs pre-arch-03 162K) and produce richer card fields. Phase L Dostoevsky
# fit ~12-14K output; 32K gives comfortable headroom for 1-arch-03's
# richer synthesis. Individual passes may override via kwargs if warranted.
def _claude_pass(*, system, user, model, max_tokens=32000, thinking=True, temperature=1.0):
    return call_claude(
        system=system, user=user, model=model,
        max_tokens=max_tokens, temperature=temperature,
        thinking=thinking,
        response_format_json=True,
    )


# label → paths accessor for coherence threading cache files
_CT_PATH_MAP = {
    "pass2":     lambda: _paths.ct_after_pass_2(SLUG, PROJECT_ROOT),
    "pass2_3":   lambda: _paths.ct_after_pass_3(SLUG, PROJECT_ROOT),
    "pass2_3_4a": lambda: _paths.ct_after_pass_4a(SLUG, PROJECT_ROOT),
    "pass2_3_4": lambda: _paths.ct_after_pass_4b(SLUG, PROJECT_ROOT),
}


# ---------- HELPER: coherence threading compress ----------
def _ct_compress(prior_pass_output: dict, label: str) -> str:
    ct_path = _CT_PATH_MAP[label]()
    cached_v = cached(ct_path, f"CT compress {label}")
    if cached_v is not None:
        return cached_v["summary_text"]
    stamp(f"  CT compressing {label}...")
    user = render("persona_coherence_threading", name=vi["name"],
                  prior_pass_output_json=json.dumps(prior_pass_output, ensure_ascii=False))
    r = call_claude(system="You compress persona fields into a tight summary.",
                    user=user, model="claude-sonnet-4-6", max_tokens=2048,
                    temperature=0.0, thinking=False)
    write_json_atomic(ct_path, {"label": label, "model": r["model"], "usage": r["usage"],
                                "summary_text": r["text"]})
    return r["text"]


# ---------- PASS 2 (Identity & Boundaries) ----------
def _pass_2():
    sysp = render("persona_pass_2_identity_boundaries", name=vi["name"], type=vi["type"],
                  subtype=vi.get("subtype"), voice_mode=vi["voice_mode"],
                  hostile_sources=vi["hostile_sources"])
    userp = render("persona_pass_2_user", merged_dossier=merged_dossier) + _critique_suffix("2")
    r = _claude_pass(system=sysp, user=userp, model="claude-opus-4-7")
    return {"voice_name": vi["name"], "voice_slug": SLUG, "pass": "2_identity_boundaries",
            "model": r["model"], "usage": r["usage"], "fields": r["json"]}

stamp("PASS 2: Identity & Boundaries (Opus + thinking)")
pass2 = call_or_cache(_paths.pass_2(SLUG, PROJECT_ROOT), "Pass 2", _pass_2)
pass_2_summary = _ct_compress(pass2["fields"], "pass2")


# ---------- PASS 3 (Intellectual Core) ----------
def _pass_3():
    sysp = render("persona_pass_3_intellectual_core", name=vi["name"], type=vi["type"],
                  subtype=vi.get("subtype"), voice_mode=vi["voice_mode"],
                  hostile_sources=vi["hostile_sources"])
    userp = render("persona_pass_3_user", merged_dossier=merged_dossier,
                   pass_2_summary=pass_2_summary) + _critique_suffix("3")
    r = _claude_pass(system=sysp, user=userp, model="claude-opus-4-7")
    return {"voice_name": vi["name"], "voice_slug": SLUG, "pass": "3_intellectual_core",
            "model": r["model"], "usage": r["usage"], "fields": r["json"]}

stamp("PASS 3: Intellectual Core (Opus + thinking, ~5 min)")
pass3 = call_or_cache(_paths.pass_3(SLUG, PROJECT_ROOT), "Pass 3", _pass_3)
combined_2_3 = {**pass2["fields"], **pass3["fields"]}
pass_2_3_summary = _ct_compress(combined_2_3, "pass2_3")


# ---------- PASS 4a (Voice) — corpus-grounded ----------
# Pass 1d (Excerpt Selection): use Sonnet to curate ~30K chars of representative
# passages from the fetched primary_texts, guided by the dossier's identification
# of important works/scenes. Replaces the prior naive first-80K-character slice.
def _pass_1d():
    # 1d-05: corpus_constraint=lyrics_patterns_only (e.g. Marley) returns SKIPPED here.
    # HANDOFF.md specifies a two-tier corpus for such voices: public-domain interview
    # transcripts / scholarly analyses as the open tier; reference_only_passages[] as
    # the private tier. The private tier must be supplied externally (not fetched by 1c).
    # Before Phase N, verify that the Marley voice_config supplies an alternative
    # public-tier URL set OR that Pass 4a/6 handle the lyrics-constraint path correctly.
    if not pass1c.get("passages"):
        return {"voice_name": vi["name"], "voice_slug": SLUG, "pass": "1d_excerpt_selection",
                "status": "SKIPPED", "reason": "No primary_texts to select from",
                "selections": [], "selected_text": "[NO PRIMARY TEXTS — output will be from training data; flag voice_basis as 'training-data']"}
    structural_index = build_structural_index(pass1c["passages"])
    user_prompt = render("persona_pass_1d_excerpt_selection",
                         name=vi["name"], merged_dossier=merged_dossier,
                         structural_index=structural_index,
                         type=vi.get("type", "human"),
                         subtype=vi.get("subtype", ""))
    # 1d-04: 8192 (up from 4096) — 15+ selections × ~200 JSON tokens each
    # approaches 4096 ceiling; bump eliminates truncation risk at zero cost.
    r = call_claude(system="You are a textual scholar curating excerpt selections for an AI persona's primary-text grounding.",
                    user=user_prompt,
                    model="claude-sonnet-4-6", max_tokens=8192,
                    temperature=0.0, thinking=False,
                    response_format_json=True)
    selections = r["json"].get("selections", [])
    selected_text = apply_selections(pass1c["passages"], selections)
    return {"voice_name": vi["name"], "voice_slug": SLUG, "pass": "1d_excerpt_selection",
            "model": r["model"], "usage": r["usage"],
            "selection_count": len(selections), "selected_chars": len(selected_text),
            "selections": selections, "selected_text": selected_text}

stamp("PASS 1d: Excerpt Selection (Sonnet, curated subset)")
pass1d = call_or_cache(_paths.excerpt_selections(SLUG, PROJECT_ROOT), "Pass 1d", _pass_1d)
primary_block = pass1d["selected_text"]
stamp(f"  primary_texts block: {len(primary_block)} chars from {pass1d.get('selection_count', 0)} curated selections")

def _pass_4a():
    sysp = render("persona_pass_4a_voice", name=vi["name"], type=vi["type"],
                  subtype=vi.get("subtype"), voice_mode=vi["voice_mode"],
                  hostile_sources=vi["hostile_sources"],
                  corpus_constraint=vi.get("corpus_constraint", "full"))
    userp = render("persona_pass_4a_user", merged_dossier=merged_dossier,
                   primary_texts=primary_block, pass_2_3_summary=pass_2_3_summary) + _critique_suffix("4a")
    # Opus + adaptive thinking: long-context pattern recognition across primary
    # texts. Especially load-bearing for hard voice types (musical, system, etc.)
    r = _claude_pass(system=sysp, user=userp, model="claude-opus-4-7",
                     max_tokens=24000, thinking=True, temperature=1.0)
    return {"voice_name": vi["name"], "voice_slug": SLUG, "pass": "4a_voice",
            "model": r["model"], "usage": r["usage"], "fields": r["json"],
            "voice_basis": "corpus-based" if pass1c.get("passages") else "training-data"}

stamp("PASS 4a: Voice (Opus + thinking, corpus-grounded)")
pass4a = call_or_cache(_paths.pass_4a(SLUG, PROJECT_ROOT), "Pass 4a", _pass_4a)
combined_2_3_4a = {**combined_2_3, **pass4a["fields"]}
pass_2_3_4a_summary = _ct_compress(combined_2_3_4a, "pass2_3_4a")


# ---------- PASS 4b (Artifact) ----------
def _pass_4b():
    sysp = render("persona_pass_4b_artifact", name=vi["name"], type=vi["type"])
    userp = render("persona_pass_4b_user",
                   pass_2_3_4a_summary=pass_2_3_4a_summary,
                   rhetorical_mode=json.dumps(pass4a["fields"].get("rhetorical_mode", "")),
                   characteristic_moves=json.dumps(pass4a["fields"].get("characteristic_moves", [])),
                   register_and_tone=json.dumps(pass4a["fields"].get("register_and_tone", ""))) + _critique_suffix("4b")
    r = _claude_pass(system=sysp, user=userp, model="claude-sonnet-4-6",
                     max_tokens=6144, thinking=False, temperature=0.2)
    return {"voice_name": vi["name"], "voice_slug": SLUG, "pass": "4b_artifact",
            "model": r["model"], "usage": r["usage"], "fields": r["json"]}

stamp("PASS 4b: Artifact (Sonnet)")
pass4b = call_or_cache(_paths.pass_4b(SLUG, PROJECT_ROOT), "Pass 4b", _pass_4b)
combined_2_3_4 = {**combined_2_3_4a, **pass4b["fields"]}
pass_2_3_4_summary = _ct_compress(combined_2_3_4, "pass2_3_4")


# ---------- PASS 5 (Engagement) ----------
def _pass_5():
    sysp = render("persona_pass_5_engagement", name=vi["name"], type=vi["type"],
                  subtype=vi.get("subtype"), voice_mode=vi["voice_mode"])
    userp = render(
        "persona_pass_5_user",
        pass_2_3_4_summary=pass_2_3_4_summary,
        constitution=json.dumps(pass3["fields"].get("constitution", ""), ensure_ascii=False, indent=2),
        reasoning_method=json.dumps(pass3["fields"].get("reasoning_method", ""), ensure_ascii=False, indent=2),
    ) + _critique_suffix("5")
    r = _claude_pass(system=sysp, user=userp, model="claude-opus-4-7",
                     max_tokens=16000, thinking=True, temperature=1.0)
    return {"voice_name": vi["name"], "voice_slug": SLUG, "pass": "5_engagement",
            "model": r["model"], "usage": r["usage"], "fields": r["json"]}

stamp("PASS 5: Engagement (Opus + thinking)")
pass5 = call_or_cache(_paths.pass_5(SLUG, PROJECT_ROOT), "Pass 5", _pass_5)


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
    ) + _critique_suffix("6")
    r = _claude_pass(system=sysp, user=userp, model="claude-sonnet-4-6",
                     max_tokens=8000, thinking=False, temperature=0.1)
    return {"voice_name": vi["name"], "voice_slug": SLUG, "pass": "6_corpus_curation",
            "model": r["model"], "usage": r["usage"], "fields": r["json"]}

stamp("PASS 6: Corpus Curation (Sonnet, selection task)")
pass6 = call_or_cache(_paths.pass_6(SLUG, PROJECT_ROOT), "Pass 6", _pass_6)


# ---------- PASS 7-pre (Citation Verification) ----------
# Spec: Sonnet 4.6, temp 0.0, max_tokens 4096. Verifies card claims against
# (a) primary texts from Node 1c — strongest anchor, and (b) merged dossier.
# Branches by voice_mode and hostile_sources for verification approach.
def _pass_7pre():
    full_card_for_verify = {**combined_2_3_4, **pass5["fields"]}
    if pass6.get("fields"):
        full_card_for_verify.update(pass6["fields"])
    sysp = render("persona_pass_7pre_citation",
                  type=vi["type"], voice_mode=vi["voice_mode"],
                  hostile_sources=vi["hostile_sources"])
    userp = render("persona_pass_7pre_citation_user",
                   persona_card_json=json.dumps(full_card_for_verify, ensure_ascii=False, indent=2),
                   primary_texts=primary_block,
                   merged_dossier=merged_dossier)
    r = call_claude(system=sysp, user=userp, model="claude-sonnet-4-6",
                    max_tokens=24000, temperature=0.0, thinking=False,
                    response_format_json=True)
    return {"voice_name": vi["name"], "voice_slug": SLUG, "pass": "7pre_citation_verification",
            "model": r["model"], "usage": r["usage"], "result": r["json"]}

stamp("PASS 7-pre: Citation Verification (Sonnet)")
pass7pre = call_or_cache(_paths.pass_7_pre(SLUG, PROJECT_ROOT), "Pass 7-pre", _pass_7pre)
verif = pass7pre["result"]
stamp(f"  verification: {verif.get('overall', '?')} | "
      f"verified={verif.get('summary', {}).get('verified', 0)} "
      f"unverified={verif.get('summary', {}).get('unverified', 0)} "
      f"interp={verif.get('summary', {}).get('interpretive', 0)} "
      f"dossier_only={verif.get('summary', {}).get('dossier_only', 0)} "
      f"inconsistent={verif.get('summary', {}).get('inconsistent', 0)} "
      f"hostile={verif.get('summary', {}).get('hostile_flagged', 0)}")


# ---------- PASS 7-anachronism (TimeChara-style temporal check) ----------
# Phase B NEW sub-pass (decisions log #14). Runs between 7-pre and 7a.
# Cross-family evaluator (NOT Claude, per self-preference-bias argument);
# o3 primary, Gemini fallback. Reads the assembled card; checks every
# concept / framing / vocabulary term for period-access anachronism.
# If REVISION_NEEDED, feeds into the same revision loop as Pass 7a.
def _pass_7_anachronism():
    full_card_for_anach = {**combined_2_3_4, **pass5["fields"]}
    if pass6.get("fields"):
        full_card_for_anach.update(pass6["fields"])
    # Derive voice_world_period from the card's world field for the prompt.
    _world = full_card_for_anach.get("world", "")
    _world_period = _world.split("\n", 1)[0][:300] if isinstance(_world, str) else str(_world)[:300]
    sysp = render("persona_pass_7_anachronism",
                  voice_name=vi["name"], voice_type=vi["type"],
                  voice_world_period=_world_period,
                  persona_card_json=json.dumps(full_card_for_anach, ensure_ascii=False, indent=2))
    userp = (
        "Run the S²RD temporal-anachronism check across the card per the "
        "system prompt. Emit anachronism_flags[] with severity + category + "
        "field_path + problematic_text + reason + suggested_fix. Emit "
        "overall verdict. JSON only."
    )
    for openai_model in ("o3", "gpt-4o"):
        try:
            r = call_openai(system=sysp, user=userp, model=openai_model,
                            temperature=0.0, max_tokens=8192,
                            response_format_json=True)
            return {"voice_name": vi["name"], "voice_slug": SLUG,
                    "pass": "7_anachronism_check",
                    "validator": f"openai:{openai_model}", "model": r["model"],
                    "usage": r["usage"], "result": r["json"]}
        except Exception as e:
            stamp(f"  WARN: {openai_model} failed ({type(e).__name__}: {str(e)[:120]}); trying next")
    try:
        r = call_gemini(user=sysp + "\n\n" + userp, temperature=0.0,
                        max_output_tokens=16384)
        cleaned = r["text"].strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1].rsplit("```", 1)[0]
        return {"voice_name": vi["name"], "voice_slug": SLUG,
                "pass": "7_anachronism_check",
                "validator": "google:gemini-2.5-pro", "model": r["model"],
                "usage": r["usage"], "result": json.loads(cleaned)}
    except Exception as e:
        stamp(f"  WARN: Gemini fallback also failed ({type(e).__name__}); skipping")
        return {"voice_name": vi["name"], "voice_slug": SLUG,
                "pass": "7_anachronism_check", "validator": "skipped",
                "result": {"overall": "SKIPPED",
                           "summary": "No cross-model evaluator available."}}

stamp("PASS 7-anachronism: TimeChara temporal check (o3 → Gemini fallback)")
pass7_anach = call_or_cache(_paths.pass_7_anachronism(SLUG, PROJECT_ROOT),
                            "Pass 7-anachronism", _pass_7_anachronism)
_anach_flags = pass7_anach["result"].get("anachronism_flags", [])
stamp(f"  validator: {pass7_anach.get('validator', '?')} | "
      f"overall: {pass7_anach['result'].get('overall', '?')} | "
      f"flags: {len(_anach_flags)}")


# ---------- PASS 7a (Cross-Model Validation) ----------
# Spec: must NOT be Claude (self-preference bias). gpt-4o preferred -> Gemini fallback -> skip.
def _pass_7a():
    full_card_for_validate = {**combined_2_3_4, **pass5["fields"]}
    if pass6.get("fields"):
        full_card_for_validate.update(pass6["fields"])
    sysp = load_prompt("persona_pass_7a_cross_model")
    userp = render("persona_pass_7a_cross_model_user",
                   persona_card_json=json.dumps(full_card_for_validate, ensure_ascii=False, indent=2))
    # Try o3 first (reasoning-mode for multi-criterion evaluation), then gpt-4o, then Gemini
    for openai_model in ("o3", "gpt-4o"):
        try:
            r = call_openai(system=sysp, user=userp, model=openai_model,
                            temperature=0.0, max_tokens=8192,
                            response_format_json=True)
            return {"voice_name": vi["name"], "voice_slug": SLUG, "pass": "7a_cross_model_validation",
                    "validator": f"openai:{openai_model}", "model": r["model"],
                    "usage": r["usage"], "result": r["json"]}
        except Exception as e:
            stamp(f"  WARN: {openai_model} failed ({type(e).__name__}: {str(e)[:120]}); trying next")
    # Fall back to Gemini
    try:
        full_prompt = sysp + "\n\n" + userp
        r = call_gemini(user=full_prompt, temperature=0.0, max_output_tokens=16384)
        # Parse JSON out of Gemini text
        cleaned = r["text"].strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1].rsplit("```", 1)[0]
        return {"voice_name": vi["name"], "voice_slug": SLUG, "pass": "7a_cross_model_validation",
                "validator": "google:gemini-2.5-pro", "model": r["model"],
                "usage": r["usage"], "result": json.loads(cleaned)}
    except Exception as e:
        stamp(f"  WARN: Gemini fallback also failed ({type(e).__name__}); skipping")
        return {"voice_name": vi["name"], "voice_slug": SLUG, "pass": "7a_cross_model_validation",
                "validator": "skipped", "result": {"overall": "SKIPPED",
                "summary": "No cross-model validator available."}}

stamp("PASS 7a: Cross-Model Validation (gpt-4o -> Gemini fallback)")
pass7a = call_or_cache(_paths.pass_7a(SLUG, PROJECT_ROOT), "Pass 7a", _pass_7a)
stamp(f"  validator: {pass7a.get('validator', '?')} | overall: {pass7a['result'].get('overall', '?')}")


# ---------- REVISION LOOP (per v3.7 spec, max 2) ----------
# Pass 7a may return REVISION_NEEDED with revision_target_passes + field_issues.
# Re-run flagged passes with critique appended; invalidate downstream caches;
# re-run Pass 7a. Loop max 2 times.
DOWNSTREAM_CHAIN = {
    "2":  ["pass2_identity_boundaries", "_ct_pass2", "pass3_intellectual_core", "_ct_pass2_3",
           "pass4a_voice", "_ct_pass2_3_4a", "pass4b_artifact", "_ct_pass2_3_4",
           "pass5_engagement", "pass6_corpus", "pass7pre_citation", "pass7a_cross_model"],
    "3":  ["pass3_intellectual_core", "_ct_pass2_3",
           "pass4a_voice", "_ct_pass2_3_4a", "pass4b_artifact", "_ct_pass2_3_4",
           "pass5_engagement", "pass6_corpus", "pass7pre_citation", "pass7a_cross_model"],
    "4a": ["pass4a_voice", "_ct_pass2_3_4a", "pass4b_artifact", "_ct_pass2_3_4",
           "pass5_engagement", "pass6_corpus", "pass7pre_citation", "pass7a_cross_model"],
    "4b": ["pass4b_artifact", "_ct_pass2_3_4",
           "pass5_engagement", "pass6_corpus", "pass7pre_citation", "pass7a_cross_model"],
    "5":  ["pass5_engagement", "pass6_corpus", "pass7pre_citation", "pass7a_cross_model"],
    "6":  ["pass6_corpus", "pass7pre_citation", "pass7a_cross_model"],
}

# fname string → paths accessor (used to invalidate downstream caches in revision loop)
_FNAME_TO_PATH = {
    "pass2_identity_boundaries": lambda: _paths.pass_2(SLUG, PROJECT_ROOT),
    "_ct_pass2":                 lambda: _paths.ct_after_pass_2(SLUG, PROJECT_ROOT),
    "pass3_intellectual_core":   lambda: _paths.pass_3(SLUG, PROJECT_ROOT),
    "_ct_pass2_3":               lambda: _paths.ct_after_pass_3(SLUG, PROJECT_ROOT),
    "pass4a_voice":              lambda: _paths.pass_4a(SLUG, PROJECT_ROOT),
    "_ct_pass2_3_4a":            lambda: _paths.ct_after_pass_4a(SLUG, PROJECT_ROOT),
    "pass4b_artifact":           lambda: _paths.pass_4b(SLUG, PROJECT_ROOT),
    "_ct_pass2_3_4":             lambda: _paths.ct_after_pass_4b(SLUG, PROJECT_ROOT),
    "pass5_engagement":          lambda: _paths.pass_5(SLUG, PROJECT_ROOT),
    "pass6_corpus":              lambda: _paths.pass_6(SLUG, PROJECT_ROOT),
    "pass7pre_citation":         lambda: _paths.pass_7_pre(SLUG, PROJECT_ROOT),
    "pass7a_cross_model":        lambda: _paths.pass_7a(SLUG, PROJECT_ROOT),
}

# Map from spec target labels (2, 3, 4a, ...) to the runner's pass function +
# its result variable name. Used to re-bind after re-running.
PASS_RUNNERS = {
    "2": ("_pass_2", "pass2"),
    "3": ("_pass_3", "pass3"),
    "4a": ("_pass_4a", "pass4a"),
    "4b": ("_pass_4b", "pass4b"),
    "5": ("_pass_5", "pass5"),
    "6": ("_pass_6", "pass6"),
}

revision_loops = 0
MAX_REVISION_LOOPS = 2

# Phase B: merge Pass 7-anachronism flags into Pass 7a's revision decision.
# Anachronism flags are structured {category, field_path, problematic_text,
# reason, suggested_fix, severity}; we translate them into field_issues the
# revision loop already understands. Pass 2 + 4a + 5 are the usual targets
# (world-field anachronisms → Pass 2; voice-vocabulary anachronisms → Pass 4a;
# engagement-protocol anachronisms → Pass 5).
if pass7_anach["result"].get("overall") == "REVISION_NEEDED":
    _anach_issues = []
    for flag in pass7_anach["result"].get("anachronism_flags", []):
        _path = flag.get("field_path", "")
        _target = "2"  # default
        if _path.startswith(("constitution", "concept_lexicon", "reasoning_method",
                              "finds_compelling", "resists")):
            _target = "3"
        elif _path.startswith(("rhetorical_mode", "characteristic_moves",
                                "register_and_tone", "metaphorical_repertoire",
                                "preferred_vocabulary", "banned_language",
                                "banned_modes")):
            _target = "4a"
        elif _path.startswith(("bold_engagement", "default_questions",
                                "disagreement_protocol", "unique_contribution")):
            _target = "5"
        _anach_issues.append({
            "flagged_pass": _target,
            "field": _path,
            "issue": f"[anachronism/{flag.get('category', 'vocabulary')}/{flag.get('severity', 'minor')}] {flag.get('reason', '')}",
            "recommended_fix": flag.get("suggested_fix", ""),
        })
    # Merge into pass7a result so the existing loop picks them up.
    pass7a["result"].setdefault("field_issues", []).extend(_anach_issues)
    pass7a["result"].setdefault("revision_target_passes", [])
    for issue in _anach_issues:
        if issue["flagged_pass"] not in pass7a["result"]["revision_target_passes"]:
            pass7a["result"]["revision_target_passes"].append(issue["flagged_pass"])
    # If 7a said PASS but 7-anach said REVISION_NEEDED, escalate the overall.
    if pass7a["result"].get("overall") != "REVISION_NEEDED":
        pass7a["result"]["overall"] = "REVISION_NEEDED"
        stamp(f"  Pass 7a overall escalated to REVISION_NEEDED by {len(_anach_issues)} anachronism flags")

while pass7a["result"].get("overall") == "REVISION_NEEDED" and revision_loops < MAX_REVISION_LOOPS:
    targets = [str(t) for t in pass7a["result"].get("revision_target_passes", [])]
    targets = [t for t in targets if t in PASS_RUNNERS]  # filter to known passes
    if not targets:
        stamp(f"REVISION LOOP: 7a flagged REVISION_NEEDED but no actionable target passes; halting loop")
        break

    revision_loops += 1
    stamp(f"REVISION LOOP {revision_loops}/{MAX_REVISION_LOOPS}: re-running passes {targets}")

    # Build per-pass critiques from field_issues
    REVISION_CRITIQUES.clear()
    for issue in pass7a["result"].get("field_issues", []):
        target = str(issue.get("flagged_pass"))
        if target not in REVISION_CRITIQUES:
            REVISION_CRITIQUES[target] = ""
        REVISION_CRITIQUES[target] += (
            f"- field: {issue.get('field')}\n"
            f"  issue: {issue.get('issue')}\n"
            f"  recommended_fix: {issue.get('recommended_fix')}\n"
        )
    # Add general check feedback (anachronism, register, etc.) to ALL targets
    general_notes = []
    for check_name, check in pass7a["result"].get("checks", {}).items():
        if check.get("status") == "ISSUE":
            general_notes.append(f"- [{check_name}] {check.get('notes', '')}")
    if general_notes:
        general_block = "GENERAL ISSUES (apply to all fields you produce):\n" + "\n".join(general_notes) + "\n\n"
        for t in targets:
            REVISION_CRITIQUES[t] = general_block + REVISION_CRITIQUES.get(t, "")

    # Compute union of all caches to invalidate (target + downstream)
    to_invalidate = set()
    for t in targets:
        for fname in DOWNSTREAM_CHAIN.get(t, []):
            to_invalidate.add(fname)

    # Delete cache files
    for fname in to_invalidate:
        cache_path = _FNAME_TO_PATH[fname]()
        if cache_path.exists():
            cache_path.unlink()

    # Also invalidate everything computed AFTER Pass 7a. DOWNSTREAM_CHAIN
    # only covers through 7a (the loop's last step); but 7b, 7c, Derive,
    # and the assembled card / provocateur_profile / evaluation_rubric
    # all read the revised card fields and must be re-computed on any
    # revision. Without this step, a prior run's stale downstream outputs
    # would cache-hit on the next invocation even though the card has
    # changed. (Captured as a known bug in commit 0452a23 during the
    # Plato revision-loop verification.)
    post_7a_invalidation = [
        _paths.pass_7b(SLUG, PROJECT_ROOT),
        _paths.pass_7c(SLUG, PROJECT_ROOT),
        _paths.derive_raw(SLUG, PROJECT_ROOT),
        _paths.assembled_card(SLUG, PROJECT_ROOT),
        _paths.provocateur_profile(SLUG, PROJECT_ROOT),
        _paths.evaluation_rubric(SLUG, PROJECT_ROOT),
    ]
    for cache_path in post_7a_invalidation:
        if cache_path.exists():
            cache_path.unlink()

    # Re-run target passes + downstream + Pass 7a in sequence
    # We re-execute pass functions in order. Each function reads outer-scope
    # state (pass2["fields"], etc.) so we re-bind those globals as we go.
    pass_order = ["2", "3", "4a", "4b", "5", "6"]
    earliest = min((pass_order.index(t) for t in targets), default=0)
    chain_to_run = pass_order[earliest:]

    _pass_path_fns = {
        "2": _paths.pass_2, "3": _paths.pass_3, "4a": _paths.pass_4a,
        "4b": _paths.pass_4b, "5": _paths.pass_5, "6": _paths.pass_6,
    }
    for pass_label in chain_to_run:
        runner_name, var_name = PASS_RUNNERS[pass_label]
        runner_fn = globals()[runner_name]
        cache_path = _pass_path_fns[pass_label](SLUG, PROJECT_ROOT)
        result = call_or_cache(cache_path, f"Pass {pass_label} (revision loop {revision_loops})", runner_fn)
        globals()[var_name] = result
        # Update derived combined dicts so downstream reads see fresh fields
        if pass_label == "2":
            pass_2_summary = _ct_compress(result["fields"], "pass2")
        elif pass_label == "3":
            combined_2_3 = {**pass2["fields"], **result["fields"]}
            pass_2_3_summary = _ct_compress(combined_2_3, "pass2_3")
        elif pass_label == "4a":
            combined_2_3_4a = {**combined_2_3, **result["fields"]}
            pass_2_3_4a_summary = _ct_compress(combined_2_3_4a, "pass2_3_4a")
        elif pass_label == "4b":
            combined_2_3_4 = {**combined_2_3_4a, **result["fields"]}
            pass_2_3_4_summary = _ct_compress(combined_2_3_4, "pass2_3_4")

    # Re-run Pass 7-pre (verifies revised card)
    pass7pre = call_or_cache(_paths.pass_7_pre(SLUG, PROJECT_ROOT),
                             f"Pass 7-pre (revision loop {revision_loops})", _pass_7pre)
    verif = pass7pre["result"]
    stamp(f"  verification (loop {revision_loops}): {verif.get('overall', '?')}")

    # Re-run Pass 7a (re-validates)
    pass7a = call_or_cache(_paths.pass_7a(SLUG, PROJECT_ROOT),
                           f"Pass 7a (revision loop {revision_loops})", _pass_7a)
    stamp(f"  validator: {pass7a.get('validator', '?')} | overall: {pass7a['result'].get('overall', '?')}")

# Clear critiques after loop ends so subsequent passes (7b, 7c, derive) get clean prompts
REVISION_CRITIQUES.clear()

if pass7a["result"].get("overall") == "REVISION_NEEDED" and revision_loops >= MAX_REVISION_LOOPS:
    stamp(f"REVISION LOOP: hit max {MAX_REVISION_LOOPS} loops, still REVISION_NEEDED — flagged for human review")
else:
    stamp(f"REVISION LOOP: complete after {revision_loops} loop(s), final 7a verdict: {pass7a['result'].get('overall', '?')}")


# ---------- PASS 7b (Worked Provocations) ----------
# Spec: Sonnet temp 0.4. We use Opus + adaptive thinking — these
# provocations are a build-time smoke test + Pass 7c diagnostic
# surface + human-review artifact. They are NOT runtime few-shot
# exemplars (see metadata.smoke_test_chains_role below, and
# personas/HANDOFF.md). High stakes because Pass 7c reads them.
def _pass_7b():
    full_card_for_provoke = {**combined_2_3_4, **pass5["fields"]}
    if pass6.get("fields"):
        full_card_for_provoke.update(pass6["fields"])
    sysp = render("persona_pass_7b_smoke_test",
                  conference_context=_load_conference_context_string(),
                  voice_mode=vi["voice_mode"], subtype=vi.get("subtype"))
    userp = render("persona_pass_7b_smoke_test_user",
                   persona_card_json=json.dumps(full_card_for_provoke, ensure_ascii=False, indent=2))
    r = _claude_pass(system=sysp, user=userp, model="claude-opus-4-7",
                     max_tokens=24000, thinking=True, temperature=1.0)
    return {"voice_name": vi["name"], "voice_slug": SLUG, "pass": "7b_smoke_test_chains",
            "model": r["model"], "usage": r["usage"], "fields": r["json"]}

stamp("PASS 7b: Worked Provocations (Opus + thinking)")
pass7b = call_or_cache(_paths.pass_7b(SLUG, PROJECT_ROOT), "Pass 7b", _pass_7b)
n_provs = len(pass7b["fields"].get("smoke_test_chains", []))
stamp(f"  generated {n_provs} provocation chains")


# ---------- PASS 7c (Negative Constraints) ----------
# Spec: Gemini preferred (cross-model bias avoidance) -> Sonnet fallback (with
# bias-awareness instruction). Refines banned_language and banned_modes.
def _pass_7c():
    voice_fields = pass4a["fields"]
    userp = render("persona_pass_7c_negative_user",
                   rhetorical_mode=json.dumps(voice_fields.get("rhetorical_mode", ""), ensure_ascii=False),
                   characteristic_moves=json.dumps(voice_fields.get("characteristic_moves", []), ensure_ascii=False, indent=2),
                   register_and_tone=json.dumps(voice_fields.get("register_and_tone", ""), ensure_ascii=False),
                   banned_language=json.dumps(voice_fields.get("banned_language", []), ensure_ascii=False, indent=2),
                   banned_modes=json.dumps(voice_fields.get("banned_modes", []), ensure_ascii=False, indent=2),
                   smoke_test_chains=json.dumps(pass7b["fields"].get("smoke_test_chains", []), ensure_ascii=False, indent=2))
    # Try Gemini first (preferred per spec)
    sysp_gemini = render("persona_pass_7c_negative", claude_fallback=False)
    try:
        full_prompt = sysp_gemini + "\n\n" + userp
        r = call_gemini(user=full_prompt, temperature=0.0, max_output_tokens=16384)
        cleaned = r["text"].strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1].rsplit("```", 1)[0]
        return {"voice_name": vi["name"], "voice_slug": SLUG, "pass": "7c_negative_constraints",
                "evaluator": "google:gemini-2.5-pro", "model": r["model"],
                "usage": r["usage"], "result": json.loads(cleaned)}
    except Exception as e:
        stamp(f"  WARN: Gemini failed ({type(e).__name__}: {str(e)[:120]}); falling back to Sonnet w/ bias-awareness")
    # Sonnet fallback with bias-awareness
    sysp_claude = render("persona_pass_7c_negative", claude_fallback=True)
    r = call_claude(system=sysp_claude, user=userp, model="claude-sonnet-4-6",
                    max_tokens=8192, temperature=0.0, thinking=False,
                    response_format_json=True)
    return {"voice_name": vi["name"], "voice_slug": SLUG, "pass": "7c_negative_constraints",
            "evaluator": "anthropic:claude-sonnet-4-6 (bias-aware fallback)",
            "model": r["model"], "usage": r["usage"], "result": r["json"]}

stamp("PASS 7c: Negative Constraints (Gemini -> Sonnet fallback)")
pass7c = call_or_cache(_paths.pass_7c(SLUG, PROJECT_ROOT), "Pass 7c", _pass_7c)
add_summary = pass7c["result"].get("additions_summary", {})
stamp(f"  evaluator: {pass7c.get('evaluator', '?')} | "
      f"banned_language +{add_summary.get('language_added', 0)} "
      f"banned_modes +{add_summary.get('modes_added', 0)}")


# ---------- DERIVE (Provocateur Profile + Evaluation Rubric) ----------
# Spec Node Derive: Sonnet 4.6, temp 0.1, max 4096. Single call producing
# 8-field Provocateur Profile (becomes a council_config.json member entry)
# + 9-test Evaluation Rubric (for ongoing testing of the runtime voice).
def _derive():
    # Build the card the Derive call sees (after Pass 7b/7c additions/refinements)
    full_card_for_derive = {**combined_2_3_4, **pass5["fields"]}
    if pass6.get("fields"):
        full_card_for_derive.update(pass6["fields"])
    if pass7b.get("fields"):
        full_card_for_derive.update(pass7b["fields"])
    if pass7c.get("result"):
        if pass7c["result"].get("banned_language") is not None:
            full_card_for_derive["banned_language"] = pass7c["result"]["banned_language"]
        if pass7c["result"].get("banned_modes") is not None:
            full_card_for_derive["banned_modes"] = pass7c["result"]["banned_modes"]
    sysp = load_prompt("persona_derive")
    userp = render("persona_derive_user",
                   persona_card_json=json.dumps(full_card_for_derive, ensure_ascii=False, indent=2))
    r = call_claude(system=sysp, user=userp, model="claude-sonnet-4-6",
                    max_tokens=8192, temperature=0.1, thinking=False,
                    response_format_json=True)
    return {"voice_name": vi["name"], "voice_slug": SLUG, "pass": "derive",
            "model": r["model"], "usage": r["usage"], "result": r["json"]}

stamp("DERIVE: Provocateur Profile + Evaluation Rubric (Sonnet)")
derive = call_or_cache(_paths.derive_raw(SLUG, PROJECT_ROOT), "Derive", _derive)
prov_profile = derive["result"].get("provocateur_profile", {})
eval_rubric = derive["result"].get("evaluation_rubric", {})
stamp(f"  provocateur_profile: {len(prov_profile)} fields | "
      f"evaluation_rubric: {len(eval_rubric.get('identity_tests', []))} identity, "
      f"{len(eval_rubric.get('reasoning_tests', []))} reasoning, "
      f"{len(eval_rubric.get('stress_tests', []))} stress")

# Save Provocateur Profile as standalone artifact for the runtime ai-assembly
# repo's council_config.json wiring (per spec — stored separately).
write_json_atomic(_paths.provocateur_profile(SLUG, PROJECT_ROOT), prov_profile)
write_json_atomic(_paths.evaluation_rubric(SLUG, PROJECT_ROOT), eval_rubric)
stamp(f"  saved: provocateur_profile.json + evaluation_rubric.json → voices/{SLUG}/06_derive/")


# ---------- FINAL SUMMARY ----------
# Register-check constants (see _check_register below)
REGISTER_CHECK_SKIP_FIELDS = {
    # Fields whose content is legitimately third-person scholarly annotation,
    # not voice-field content. Third-person in these fields is NOT a register
    # violation.
    "curated_corpus_passages",   # primary text excerpts + scholarly annotations
    "reference_only_passages",   # two-tier corpus private tier (Step 1 only)
    "smoke_test_chains",        # diagnostic artifact with scholarly gloss
    "metadata",                   # pipeline metadata
}

# Matches bracketed scholarly annotations that should be stripped from voice
# fields before register checking. These markers explicitly signal
# meta-commentary rather than voice content, e.g.:
#   [inference: Plato's willingness to stage devastating criticism ...]
#   [hostile source: Plutarch frames Cleopatra as ...]
#   [reconstruction: Roller argues ...]
BRACKET_ANNOTATION_RE = re.compile(
    r"\[(?:inference|hostile source|reconstruction|scholarly note|"
    r"editor note|meta|note|dossier|own voice): [^\]]*\]",
    re.IGNORECASE,
)


def _check_register(card_fields: dict, voice_last_name: str):
    """Detect third-person register leaks in voice fields.

    Two corrections over the original string-match version:

    1. Scholar-annotation fields are SKIPPED. Fields like curated_corpus_passages,
       smoke_test_chains, and metadata legitimately contain third-person
       scholarly commentary about the figure (e.g., "Plato's method of
       steelmanning" as an annotation on a Republic excerpt). These are not
       voice-field content and shouldn't be flagged.

    2. Bracketed scholarly annotations within voice fields are STRIPPED before
       checking. reasoning_method can contain inline [inference: Plato's
       willingness ...] markers — meta-commentary distinguishing voice from
       interpretive gloss. The brackets make these legitimate; strip them
       from the text before looking for third-person patterns.

    Returns (count, details) where details is a list of
    {field, flag, context} dicts for each violation found.
    """
    flags = [f"{voice_last_name}'s ", f"{voice_last_name} was", f"{voice_last_name} is",
             f"{voice_last_name} believed", f"{voice_last_name} argued"]
    details = []
    for field_name, fv in card_fields.items():
        if field_name in REGISTER_CHECK_SKIP_FIELDS:
            continue
        t = json.dumps(fv) if not isinstance(fv, str) else fv
        # Strip bracketed scholarly annotations — these are legitimate
        # meta-commentary within otherwise first-person voice content
        t_stripped = BRACKET_ANNOTATION_RE.sub("", t)
        for flag in flags:
            idx = t_stripped.find(flag)
            while idx != -1:
                start = max(0, idx - 40)
                end = min(len(t_stripped), idx + len(flag) + 40)
                details.append({
                    "field": field_name,
                    "flag": flag,
                    "context": t_stripped[start:end],
                })
                idx = t_stripped.find(flag, idx + 1)
    return len(details), details


full_card = {**combined_2_3_4, **pass5["fields"]}
if pass6.get("fields"):
    full_card.update(pass6["fields"])
# Pass 7b: smoke_test_chains field
if pass7b.get("fields"):
    full_card.update(pass7b["fields"])
# Pass 7c: refined banned_language and banned_modes (overwrite Pass 4a's seeds)
if pass7c.get("result"):
    if pass7c["result"].get("banned_language") is not None:
        full_card["banned_language"] = pass7c["result"]["banned_language"]
    if pass7c["result"].get("banned_modes") is not None:
        full_card["banned_modes"] = pass7c["result"]["banned_modes"]

# For most human voices, last token of the name is the surname. For
# non-human voices where the whole name is a noun (Octopus, River) or
# includes generic nouns (Whanganui River), using the naive last token
# would false-positive on content mentioning the noun in third person.
# Override for known-edge-case voices.
_LAST_NAME_OVERRIDES = {
    "Octopus": None,                # skip register check entirely
    "Whanganui River": "Whanganui", # match the unique part, not "River"
}
last_name = _LAST_NAME_OVERRIDES.get(vi["name"], vi["name"].split()[-1])
if last_name is None:
    register_violations, register_details = 0, []
else:
    register_violations, register_details = _check_register(full_card, last_name)

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
stamp(f"  Pass 7-pre verify:    {pass7pre['result'].get('overall', '?')} (review notes saved)")
stamp(f"  Pass 7a validate:     {pass7a['result'].get('overall', '?')} ({pass7a.get('validator', '?')}) "
      f"after {revision_loops} revision loop(s)")
stamp(f"  Pass 7b provocations: {len(pass7b['fields'].get('smoke_test_chains', []))} chains")
stamp(f"  Pass 7c neg-constr:   +{pass7c['result'].get('additions_summary', {}).get('language_added', 0)} lang, "
      f"+{pass7c['result'].get('additions_summary', {}).get('modes_added', 0)} modes ({pass7c.get('evaluator', '?')})")
stamp(f"  Derive:               provocateur_profile + evaluation_rubric saved")
stamp(f"  Total card fields:    {len(full_card)}")
stamp(f"  Output Register check: {register_violations} violations ({'CLEAN' if register_violations == 0 else 'NEEDS REVIEW'})")
stamp(f"  Card saved to:        {_paths.voice_root(SLUG, PROJECT_ROOT)}/")
stamp("=" * 60)

write_json_atomic(_paths.assembled_card(SLUG, PROJECT_ROOT), {
    # Spec wants 37 card fields flat at root + a metadata block.
    "voice_name": vi["name"],
    "voice_mode": vi["voice_mode"],
    "pipeline_version": "3.10",
    "generated_date": time.strftime("%Y-%m-%d"),

    # All 35 generated card fields, flat at root level
    **full_card,

    # Two-tier corpus (Phase B): reference_only_passages is loaded into
    # Voice Pipeline Step 1 ONLY; Step 2 drops it before assembling its
    # system prompt. See personas/HANDOFF.md §"reference_only_passages is
    # Step 1 only" for the enforcement contract.
    "reference_only_passages": merged_dossier_dict.get("reference_only_passages", {"passages": []}),

    # Runtime continuity fields (populated by Voice Pipeline at deployment, not
    # by Persona Pipeline). Initialized null so consumers don't get KeyError.
    "continuity_block_if_night_2": None,
    "continuity_block_artifact_if_night_2": None,

    "metadata": {
        "passes_completed": [
            "1a_perplexity",
            "1a_dr_claude" if claude_dr_text else "1a_dr_claude_SKIPPED",
            "1b_gemini", "1c_primary_text_fetch", "1merge_three_way",
            "2_identity_boundaries", "ct_pass2",
            "3_intellectual_core", "ct_pass2_3",
            "1d_excerpt_selection",
            "4a_voice", "ct_pass2_3_4a",
            "4b_artifact", "ct_pass2_3_4",
            "5_engagement",
            "6_corpus_curation" if pass6.get("status") != "HALTED" else "6_corpus_curation_HALTED",
            "7pre_citation_verification",
            "7a_cross_model_validation",
            "7b_smoke_test_chains",
            "7c_negative_constraints",
            "derive_provocateur_profile_and_rubric",
        ],
        "validation_status": pass7a["result"].get("overall", "unknown"),
        "revision_loops": revision_loops,
        "tools_used": ["perplexity:sonar-deep-research", "anthropic:claude-opus-4-7", "anthropic:claude-sonnet-4-6", "google:gemini-2.5-pro", "openai:gpt-4o", "gutenberg:web_fetch"],
        "voice_basis": pass4a["voice_basis"],
        "hostile_sources": vi["hostile_sources"],
        "corpus_constraint": vi.get("corpus_constraint", "full"),
        "subtype": vi.get("subtype"),
        "deployment_context": _load_conference_context_string(),
        "human_review_status": "pending",
        "approach_c": bool(claude_dr_text),
        "citation_verification": {
            "overall": pass7pre["result"].get("overall"),
            "summary": pass7pre["result"].get("summary", {}),
            "review_notes": pass7pre["result"].get("review_notes", ""),
        },
        "cross_model_validation": {
            "validator": pass7a.get("validator"),
            "overall": pass7a["result"].get("overall"),
            "revision_target_passes": pass7a["result"].get("revision_target_passes", []),
            "summary": pass7a["result"].get("summary", ""),
        },
        "negative_constraints_refinement": {
            "evaluator": pass7c.get("evaluator"),
            "additions_summary": pass7c["result"].get("additions_summary", {}),
        },
        "smoke_test_chains_role": (
            "DIAGNOSTIC + HANDOFF ARTIFACT, NOT RUNTIME EXEMPLAR. "
            "These provocations are the card's first words — generated by "
            "Pass 7b as (1) a smoke test that the 35-field spec coheres into "
            "a voice, (2) a diagnostic surface for Pass 7c to refine "
            "banned_language and banned_modes, and (3) a pre-runtime artifact "
            "for human review. The Voice Pipeline at runtime MUST NOT few-shot "
            "from these. The persona card is the contract; the provocations "
            "are the smoke test. They go stale the moment a real conference "
            "question arrives that's nothing like the test set."
        ),
        "derived_outputs": {
            "provocateur_profile_path": f"voices/{SLUG}/06_derive/01_provocateur_profile.json",
            "evaluation_rubric_path": f"voices/{SLUG}/06_derive/02_evaluation_rubric.json",
            "note": (
                "Provocateur Profile is the 8-field council_config.json member "
                "entry. Evaluation Rubric is 9 test prompts (3 identity + 3 "
                "reasoning + 3 stress) for ongoing voice quality monitoring. "
                "Per spec, these are stored separately from the assembled card "
                "for clean handoff to the Provocateur Pipeline (profile) and "
                "Voice Pipeline testing harness (rubric)."
            ),
        },
        # Diagnostic extras (not in spec but useful for our development)
        "field_counts": {
            "pass2": len(pass2["fields"]), "pass3": len(pass3["fields"]),
            "pass4a": len(pass4a["fields"]), "pass4b": len(pass4b["fields"]),
            "pass5": len(pass5["fields"]), "pass6": len(pass6.get("fields", {})),
            "pass7b_smoke_test": len(pass7b["fields"].get("smoke_test_chains", [])),
        },
        "register_violations": register_violations,
        "register_violation_details": register_details,
    },
})
stamp(f"Assembled card -> {_paths.assembled_card(SLUG, PROJECT_ROOT).relative_to(PROJECT_ROOT)}")
