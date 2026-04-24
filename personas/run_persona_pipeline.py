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
import os
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
from flows.shared.pass_7pre_chunked import run_chunked_pass_7pre
from flows.shared.patch_walker import apply_patch_in_place as _apply_patch_in_place
from flows.shared.chat_prompt_builder import write_chat_system_prompt


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


def _load_deployment_priming() -> dict[str, str]:
    """Load audience + conference context for Pass 5 audience-priming (FU#12-B).

    Returns a dict with three string fields:
      - conference_summary: 1-paragraph context for the deployment
      - audience_profile: rich participant description
      - programming_tracks: comma-joined track list

    Each field defaults to "" if its source file is missing — Pass 5's
    prompt branches on emptiness and skips the priming block. So the
    pipeline still works on projects without these files.
    """
    out = {"conference_summary": "", "audience_profile": "",
           "programming_tracks": ""}
    facts_path = _paths.conference_facts(PROJECT_ROOT)
    if facts_path.exists():
        facts = json.loads(facts_path.read_text())
        out["conference_summary"] = facts.get("conference_context_paragraph", "")
        role = facts.get("session_role_for_ai_assembly", "")
        if role:
            out["conference_summary"] = (out["conference_summary"]
                                         + " " + role).strip()
    aud_path = _paths.audience_profile(PROJECT_ROOT)
    if aud_path.exists():
        aud = json.loads(aud_path.read_text())
        out["audience_profile"] = aud.get("participant_profile", "")
        tracks = aud.get("programming_tracks_representative", []) or []
        out["programming_tracks"] = ", ".join(tracks)
    return out

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
# Under 1-arch-05 Part A (2026-04-23), Pass 1d/2/3/4a/6 read per-chunk
# variables instead of the merged_dossier blob. The blob string is kept
# for any legacy references but the primary rendering path is per-chunk.
merged_dossier = json.dumps(merged_dossier_dict, ensure_ascii=False, indent=2)
_n_flags = len(merged_dossier_dict.get("coherence_flags", []))
stamp(f"  merged_dossier: {len(merged_dossier)} chars; {_n_flags} coherence_flags")


# ── 1-arch-05 Part A: per-chunk render variables ────────────────────────────
# Pass 1d/2/3/4a/6 user prompts declare named template variables for the
# specific chunks (and sub-slices + filtered interpretive_frames subsets)
# they consume. This replaces the `{{ merged_dossier }}` blob rendering.
# Each pass's render call passes a tailored subset of these.
#
# Naming convention: chunk keys use their natural names where there is NO
# collision with a downstream card-field name. Three chunks (`reasoning_method`,
# `knowledge_boundary`, `hard_limits`) collide with Pass 2/3 card-field names;
# those chunk reads use `_chunk` suffix (`reasoning_method_chunk`, etc.) in
# templates to prevent ambiguity when a pass might receive BOTH the chunk
# AND the card-field value in some future wiring.

def _per_chunk_vars(md: dict) -> dict:
    """Per-chunk render variables for Pass 1d/2/3/4a/6 user prompts.

    Returns a dict mapping template-variable names to JSON-serialized
    strings. Each render call picks the subset it needs.
    """
    def J(v):
        return json.dumps(v, ensure_ascii=False, indent=2)

    frames = md.get("interpretive_frames", []) or []
    return {
        # Chunk 1.1 — BIOGRAPHICAL
        "life_scaffold":                J(md.get("life_scaffold", {})),
        "formative_candidates":         J(md.get("formative_candidates", [])),
        # Chunk 1.2 — INTELLECTUAL
        "commitments":                  J(md.get("commitments", [])),
        "concepts":                     J(md.get("concepts", [])),
        "tensions":                     J(md.get("tensions", [])),
        "interpretive_frames":          J(frames),
        # Chunk 1.3 — REASONING (_chunk suffix: avoids collision with Pass 3's
        # `reasoning_method` card-field output name when downstream passes
        # receive BOTH)
        "reasoning_method_chunk":       J(md.get("reasoning_method", {})),
        "textures":                     J(md.get("textures", {})),
        "analytical_context_reasoning": J(md.get("analytical_context_reasoning", {})),
        # Chunk 1.4 — VOICE
        "moves":                        J(md.get("moves", {})),
        "register":                     J(md.get("register", {})),
        "vocabulary":                   J(md.get("vocabulary", {})),
        "analytical_context_voice":     J(md.get("analytical_context_voice", None)),
        # Chunk 1.5 — BOUNDARIES (_chunk suffix: same collision-avoidance
        # reason for `knowledge_boundary` and `hard_limits` card fields)
        "knowledge_boundary_chunk":     J(md.get("knowledge_boundary", {})),
        "sensitive_topics":             J(md.get("sensitive_topics", {})),
        "hard_limits_chunk":            J(md.get("hard_limits", {})),
        # Chunk 1.6 — CORPUS (`urls` removed per 1-arch-07; derived at render)
        "works":                        J(md.get("works", {})),
        "passages":                     J(md.get("passages", {})),
        "reference_only_passages":      J(md.get("reference_only_passages", {"passages": []})),
        # Sub-slice plucks for cross-chunk references (Pass 4a primary user)
        "available_pathe":              J(md.get("life_scaffold", {}).get("available_pathe", [])),
        "reasoning_method_summary":     md.get("reasoning_method", {}).get("summary", ""),
        # Filtered interpretive_frames subsets (consumers filter by frame_type)
        "voice_level_debate_frames":    J([f for f in frames if f.get("frame_type") == "voice_level_debate"]),
        "cross_disciplinary_frames":    J([f for f in frames if f.get("frame_type") == "cross_disciplinary_reframing"]),
        "interpretive_methods":         J([f for f in frames if f.get("frame_type") == "interpretive_method"]),
    }


chunk_vars = _per_chunk_vars(merged_dossier_dict)
stamp(f"  per-chunk vars ready (1-arch-05 Part A): {len(chunk_vars)} render vars")


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


# ---------- REVISION LOOP STATE — REMOVED FU#13 (2026-04-23) ----------
# The revision loop is replaced by the linear Pass 7a-FIX step (FU#13).
# REVISION_CRITIQUES are no longer needed; writers
# are not re-invoked. The `+ _critique_suffix("N")` call sites in
# Pass 2/3/4a/4b/5/6 user-prompt rendering have been removed.
# (Kept this comment block as a tombstone so a fresh reader knows where
# the old infrastructure was; remove entirely after Plato run validates
# the new architecture.)


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
    # 2026-04-23: thinking=False → True (quality-tuning). CT does heavier
    # compression than the textbook "summarization" framing suggests:
    # pass2_3_4a is 22 fields → 2K (25-35× ratio); pass2_3_4 is 30 fields
    # → 2K (35-50× ratio). At those ratios the model isn't summarizing —
    # it's selecting which of dozens of voice-defining nuances to surface.
    # That's deliberation, not compression. Thinking gives Sonnet the
    # budget to make those tradeoffs. Kept on Sonnet (not Opus) — the task
    # is still fidelity-bound; Opus + thinking risks injecting interpretive
    # framing where source-faithful selection is wanted. temperature
    # 0.0 → 1.0 (required for thinking). max_tokens 2048 → 16000 (thinking
    # shares budget with output; ~14K thinking + ~2K narrative summary).
    r = call_claude(system="You compress persona fields into a tight summary.",
                    user=user, model="claude-sonnet-4-6", max_tokens=16000,
                    temperature=1.0, thinking=True)
    write_json_atomic(ct_path, {"label": label, "model": r["model"], "usage": r["usage"],
                                "summary_text": r["text"]})
    return r["text"]


# ---------- PASS 2 (Identity & Boundaries) ----------
def _pass_2():
    sysp = render("persona_pass_2_identity_boundaries", name=vi["name"], type=vi["type"],
                  subtype=vi.get("subtype"), voice_mode=vi["voice_mode"],
                  hostile_sources=vi["hostile_sources"])
    # 1-arch-05 Part A: per-chunk reads. Pass 2 consumes chunks 1.1 + 1.5 +
    # voice_level_debate subset of interpretive_frames (1.2).
    userp = render(
        "persona_pass_2_user",
        life_scaffold=chunk_vars["life_scaffold"],
        formative_candidates=chunk_vars["formative_candidates"],
        knowledge_boundary_chunk=chunk_vars["knowledge_boundary_chunk"],
        sensitive_topics=chunk_vars["sensitive_topics"],
        hard_limits_chunk=chunk_vars["hard_limits_chunk"],
        voice_level_debate_frames=chunk_vars["voice_level_debate_frames"],
    )
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
    # 1-arch-05 Part A: per-chunk reads. Pass 3 consumes chunks 1.2 + 1.3 +
    # interpretive_frames (full list — Pass 3 filters method + cross_disciplinary
    # internally via frame_type).
    userp = render(
        "persona_pass_3_user",
        commitments=chunk_vars["commitments"],
        concepts=chunk_vars["concepts"],
        tensions=chunk_vars["tensions"],
        interpretive_frames=chunk_vars["interpretive_frames"],
        reasoning_method_chunk=chunk_vars["reasoning_method_chunk"],
        textures=chunk_vars["textures"],
        analytical_context_reasoning=chunk_vars["analytical_context_reasoning"],
        pass_2_summary=pass_2_summary,
    )
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
    # 1-arch-05 Part A: per-chunk reads for Pass 1d. Reads specific chunk
    # content for selection criteria — passages (index of scholar-flagged
    # important passages with purpose_tags), works (bibliographic context),
    # reasoning_method_chunk + register + moves (to identify voice-exemplar
    # and reasoning-in-action passages).
    user_prompt = render(
        "persona_pass_1d_excerpt_selection",
        name=vi["name"],
        type=vi.get("type", "human"),
        subtype=vi.get("subtype", ""),
        structural_index=structural_index,
        passages=chunk_vars["passages"],
        works=chunk_vars["works"],
        reasoning_method_chunk=chunk_vars["reasoning_method_chunk"],
        register=chunk_vars["register"],
        moves=chunk_vars["moves"],
    )
    # 1d-04: 8192 (up from 4096) — 15+ selections × ~200 JSON tokens each
    # approaches 4096 ceiling; bump eliminates truncation risk at zero cost.
    # 2026-04-23: model upgraded claude-sonnet-4-6 → claude-opus-4-7 after
    # Stage 2 v2 hit Anthropic's output content-filtering policy on a
    # Sonnet emission (literary-canon corpus includes violent/disturbing
    # scenes — Dostoevsky's Rebellion, Stavrogin confession, etc. — which
    # Sonnet's output descriptions reproduced and got blocked). Opus 4.7
    # handles this material reliably. Modest cost delta; Pass 1d is a
    # small call (~8K output).
    # Opus 4.7 deprecated `temperature` — pass None to omit from API call
    # (model defaults to 1.0, which is what extended-thinking mode requires).
    # 2026-04-23: thinking=False → True (quality-tuning checklist). Excerpt
    # selection IS a judgment task — what's representative? voice-exemplar?
    # reasoning-in-action? Thinking lets Opus deliberate between candidates
    # rather than greedy-picking. Latency cost ~30s; quality upside flows
    # downstream into Pass 4a voice modeling + Pass 6 corpus curation.
    # max_tokens 8192 → 16000 — thinking budget shares the output ceiling.
    r = call_claude(system="You are a textual scholar curating excerpt selections for an AI persona's primary-text grounding.",
                    user=user_prompt,
                    model="claude-opus-4-7", max_tokens=16000,
                    temperature=None, thinking=True,
                    response_format_json=True)
    selections = r["json"].get("selections", [])
    selected_text = apply_selections(pass1c["passages"], selections)
    return {"voice_name": vi["name"], "voice_slug": SLUG, "pass": "1d_excerpt_selection",
            "model": r["model"], "usage": r["usage"],
            "selection_count": len(selections), "selected_chars": len(selected_text),
            "selections": selections, "selected_text": selected_text}

stamp("PASS 1d: Excerpt Selection (Opus + thinking, curated subset)")
pass1d = call_or_cache(_paths.excerpt_selections(SLUG, PROJECT_ROOT), "Pass 1d", _pass_1d)
primary_block = pass1d["selected_text"]
stamp(f"  primary_texts block: {len(primary_block)} chars from {pass1d.get('selection_count', 0)} curated selections")

def _pass_4a():
    sysp = render("persona_pass_4a_voice", name=vi["name"], type=vi["type"],
                  subtype=vi.get("subtype"), voice_mode=vi["voice_mode"],
                  hostile_sources=vi["hostile_sources"],
                  corpus_constraint=vi.get("corpus_constraint", "full"))
    # 1-arch-05 Part A: per-chunk reads. Pass 4a consumes chunk 1.4 (full:
    # moves + register + vocabulary + analytical_context_voice) + cross-refs
    # (available_pathe from 1.1, reasoning_method_summary from 1.3) + filtered
    # cross_disciplinary subset of interpretive_frames + primary_block from 1d.
    userp = render(
        "persona_pass_4a_user",
        moves=chunk_vars["moves"],
        register=chunk_vars["register"],
        vocabulary=chunk_vars["vocabulary"],
        analytical_context_voice=chunk_vars["analytical_context_voice"],
        available_pathe=chunk_vars["available_pathe"],
        reasoning_method_summary=chunk_vars["reasoning_method_summary"],
        cross_disciplinary_frames=chunk_vars["cross_disciplinary_frames"],
        primary_texts=primary_block,
        pass_2_3_summary=pass_2_3_summary,
    )
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
                   register_and_tone=json.dumps(pass4a["fields"].get("register_and_tone", "")))
    # 2026-04-23: model upgraded claude-sonnet-4-6 → claude-opus-4-7 + thinking
    # ON (quality-tuning checklist). Pass 4b owns 8 output_characteristics
    # fields and is CT-only (no chunk reads); baseline Pass 7a flagged 6 of
    # those fields for register-drift. Hypothesis: the issue is model
    # underspec, not just upstream context. Opus + thinking gives the
    # nuanced first-/second-person register discipline that artifact
    # generation requires. max_tokens 6144 → 24000 (thinking-budget +
    # richer output headroom).
    r = _claude_pass(system=sysp, user=userp, model="claude-opus-4-7",
                     max_tokens=24000, thinking=True, temperature=1.0)
    return {"voice_name": vi["name"], "voice_slug": SLUG, "pass": "4b_artifact",
            "model": r["model"], "usage": r["usage"], "fields": r["json"]}

stamp("PASS 4b: Artifact (Opus + thinking)")
pass4b = call_or_cache(_paths.pass_4b(SLUG, PROJECT_ROOT), "Pass 4b", _pass_4b)
combined_2_3_4 = {**combined_2_3_4a, **pass4b["fields"]}
pass_2_3_4_summary = _ct_compress(combined_2_3_4, "pass2_3_4")


# ---------- PASS 5 (Engagement) ----------
def _pass_5():
    sysp = render("persona_pass_5_engagement", name=vi["name"], type=vi["type"],
                  subtype=vi.get("subtype"), voice_mode=vi["voice_mode"])
    # FU#12-B (2026-04-23): audience + conference context primes Pass 5's
    # audience-facing fields (bold_engagement_topics, default_questions). Voice
    # arrives "ready" for the deployment context. NO new schema field — uses
    # existing fields, just better-grounded. translation_table lookup proposal
    # was withdrawn (would have foreclosed contextual richness + risked
    # ventriloquism); translation_protocol method already encodes generative
    # handling per Pass 2.
    deployment = _load_deployment_priming()
    userp = render(
        "persona_pass_5_user",
        pass_2_3_4_summary=pass_2_3_4_summary,
        constitution=json.dumps(pass3["fields"].get("constitution", ""), ensure_ascii=False, indent=2),
        reasoning_method=json.dumps(pass3["fields"].get("reasoning_method", ""), ensure_ascii=False, indent=2),
        conference_summary=deployment["conference_summary"],
        audience_profile=deployment["audience_profile"],
        programming_tracks=deployment["programming_tracks"],
    )
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
    # 1-arch-05 Part A: per-chunk reads for Pass 6. Consumes chunk 1.6 (works,
    # passages, reference_only_passages) + primary_block from 1d + already-
    # produced card fields (constitution / concept_lexicon / reasoning_method /
    # rhetorical_mode / characteristic_moves / register_and_tone) as selection
    # criteria.
    userp = render(
        "persona_pass_6_user",
        primary_texts=primary_block,
        works=chunk_vars["works"],
        passages=chunk_vars["passages"],
        reference_only_passages=chunk_vars["reference_only_passages"],
        pass_2_3_4a_summary=pass_2_3_4a_summary,
        constitution=json.dumps(pass3["fields"].get("constitution", ""), ensure_ascii=False, indent=2),
        concept_lexicon=json.dumps(pass3["fields"].get("concept_lexicon", ""), ensure_ascii=False, indent=2),
        reasoning_method=json.dumps(pass3["fields"].get("reasoning_method", ""), ensure_ascii=False, indent=2),
        rhetorical_mode=json.dumps(pass4a["fields"].get("rhetorical_mode", ""), ensure_ascii=False),
        characteristic_moves=json.dumps(pass4a["fields"].get("characteristic_moves", []), ensure_ascii=False, indent=2),
        register_and_tone=json.dumps(pass4a["fields"].get("register_and_tone", ""), ensure_ascii=False),
    )
    # 2026-04-23: model upgraded claude-sonnet-4-6 → claude-opus-4-7 + thinking
    # ON (quality-tuning checklist). Pass 6 owns the cited_passages field
    # that runtime Provocateur literally quotes. Literary-canon passage
    # selection requires inter-passage judgment: which scene best shows
    # polyphony? which monologue exemplifies sobornost? Sonnet can rubric-
    # follow but Opus + thinking deliberates the tradeoffs. max_tokens
    # 8000 → 24000 (thinking-budget + 1+1 fields can include long passages).
    r = _claude_pass(system=sysp, user=userp, model="claude-opus-4-7",
                     max_tokens=24000, thinking=True, temperature=1.0)
    return {"voice_name": vi["name"], "voice_slug": SLUG, "pass": "6_corpus_curation",
            "model": r["model"], "usage": r["usage"], "fields": r["json"]}

stamp("PASS 6: Corpus Curation (Opus + thinking, literary judgment)")
pass6 = call_or_cache(_paths.pass_6(SLUG, PROJECT_ROOT), "Pass 6", _pass_6)


# ---------- PASS 7-pre (Citation Verification) — FU#2 chunked 2026-04-24 ----
# FU#2 2026-04-24: replaced single-shot call that hit Sonnet 4.6's 128K
# output ceiling on rich cards (empirically hit twice on 2026-04-24
# Dostoevsky re-run). Now a three-stage pipeline in
# flows/shared/pass_7pre_chunked.py:
#   Stage 1: extract verifiable claims from card (1 Sonnet call, card-only
#            input, ~20-40K output; well under ceiling)
#   Stage 2: verify batches of ~25 claims in parallel (N Sonnet calls,
#            primary_texts + dossier input, 16K max_tokens each)
#   Stage 3: check boddice_tag_flags (1 small Sonnet call, parallel with
#            Stage 2)
# Python aggregates: summary counts, overall verdict, review_notes.
# Output schema preserved — Pass 7a reads the same fields as before.
# Try/except wrap retained for graceful degradation (API overload, etc.).
def _pass_7pre():
    full_card_for_verify = {**combined_2_3_4, **pass5["fields"]}
    if pass6.get("fields"):
        full_card_for_verify.update(pass6["fields"])
    result = run_chunked_pass_7pre(
        persona_card=full_card_for_verify,
        primary_texts=primary_block,
        merged_dossier=merged_dossier,
        voice_type=vi["type"],
        voice_mode=vi["voice_mode"],
        hostile_sources=vi["hostile_sources"],
    )
    return {"voice_name": vi["name"], "voice_slug": SLUG, "pass": "7pre_citation_verification",
            "model": "claude-sonnet-4-6-chunked", "usage": {}, "result": result}

stamp("PASS 7-pre: Citation Verification (Sonnet, FU#2 chunked)")
try:
    pass7pre = call_or_cache(_paths.pass_7_pre(SLUG, PROJECT_ROOT), "Pass 7-pre", _pass_7pre)
    verif = pass7pre["result"]
    stamp(f"  verification: {verif.get('overall', '?')} | "
          f"verified={verif.get('summary', {}).get('verified', 0)} "
          f"unverified={verif.get('summary', {}).get('unverified', 0)} "
          f"interp={verif.get('summary', {}).get('interpretive', 0)} "
          f"dossier_only={verif.get('summary', {}).get('dossier_only', 0)} "
          f"inconsistent={verif.get('summary', {}).get('inconsistent', 0)} "
          f"hostile={verif.get('summary', {}).get('hostile_flagged', 0)} | "
          f"boddice_tag_flags={len(verif.get('boddice_tag_flags', []))} | "
          f"items={len(verif.get('items', []))}")
except (RuntimeError, Exception) as e:
    # FU#2 dramatically reduces the chance of ceiling-hit failures, but
    # retain graceful-degradation wrap for API overload / batch-call
    # failures. Each verify batch is already defensively wrapped in
    # pass_7pre_chunked.py — this catches the (rare) top-level failure.
    stamp(f"  WARN: Pass 7-pre (chunked) failed at top level: {type(e).__name__}: {str(e)[:160]}")
    stamp(f"  Proceeding without Pass 7-pre. Card ships without citation-verification audit; "
          f"Pass 7a still runs on full card.")
    pass7pre = {"voice_name": vi["name"], "voice_slug": SLUG, "pass": "7pre_citation_verification",
                "result": {"overall": "VERIFICATION_SKIPPED",
                           "summary": {"verified": 0, "unverified": 0, "interpretive": 0,
                                       "dossier_only": 0, "inconsistent": 0, "hostile_flagged": 0},
                           "skip_reason": f"chunked pipeline failure: {type(e).__name__}: {str(e)[:200]}"}}
    write_json_atomic(_paths.pass_7_pre(SLUG, PROJECT_ROOT), pass7pre)


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
    # 2026-04-23: ladder updated — gpt-5.4 primary with reasoning_effort=high
    # (1M context + unified reasoning model; supersedes gpt-4.1/o3/gpt-4o
    # which were retired from ChatGPT on 2026-02-13 but remain API-available
    # as fallbacks). Reasoning mode is essential for multi-criterion
    # anachronism evaluation. Gemini 2.5 Pro last resort.
    # max_tokens bumped 8192→16384 because reasoning tokens count against
    # max_completion_tokens budget for gpt-5.x high-effort calls.
    for openai_model in ("gpt-5.4", "gpt-4.1", "o3", "gpt-4o"):
        try:
            _effort = "high" if openai_model.startswith("gpt-5") else None
            r = call_openai(system=sysp, user=userp, model=openai_model,
                            temperature=0.0, max_tokens=16384,
                            reasoning_effort=_effort,
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

stamp("PASS 7-anachronism: TimeChara temporal check (gpt-5.4 high → Gemini fallback)")
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
    # 2026-04-23: ladder updated — gpt-5.4 primary with reasoning_effort=high
    # (1M context + unified reasoning model; supersedes gpt-4.1/o3/gpt-4o
    # which were retired from ChatGPT on 2026-02-13 but remain API-available
    # as fallbacks). Reasoning mode is essential for the multi-criterion
    # rubric evaluation Pass 7a performs. Gemini 2.5 Pro last resort.
    # max_tokens bumped 8192→16384 because reasoning tokens count against
    # max_completion_tokens budget for gpt-5.x high-effort calls.
    for openai_model in ("gpt-5.4", "gpt-4.1", "o3", "gpt-4o"):
        try:
            _effort = "high" if openai_model.startswith("gpt-5") else None
            r = call_openai(system=sysp, user=userp, model=openai_model,
                            temperature=0.0, max_tokens=16384,
                            reasoning_effort=_effort,
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

stamp("PASS 7a: Cross-Model Validation (gpt-5.4 high -> Gemini fallback)")
pass7a = call_or_cache(_paths.pass_7a(SLUG, PROJECT_ROOT), "Pass 7a", _pass_7a)
stamp(f"  validator: {pass7a.get('validator', '?')} | overall: {pass7a['result'].get('overall', '?')}")


# ---------- REVISION LOOP (per v3.7 spec, max 2) ----------
# Pass 7a may return REVISION_NEEDED with revision_target_passes + field_issues.
# Re-run flagged passes with critique appended; invalidate downstream caches;
# re-run Pass 7a. Loop max 2 times.
# DOWNSTREAM_CHAIN, _FNAME_TO_PATH, PASS_RUNNERS, revision_loops counter +
# MAX_REVISION_LOOPS — REMOVED FU#13 (2026-04-23). The linear Pass 7a-FIX
# step replaces all of this. Cache invalidation under FU#13 is a small
# inline list (Pass 7-pre, 7-anach, 7a + post-7a artifacts); pass-runner
# lookup not needed because writers are not re-invoked. See _pass_7a_fix()
# below for the new architecture.

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

# ---------- PASS 7a-FIX — Linear field-level patcher (FU#13, 2026-04-23) ----------
# Replaces the prior revision loop entirely. If Pass 7a (with merged Pass 7-
# anachronism flags) returns REVISION_NEEDED, fire ONE patcher call (Sonnet
# 4.6 + thinking) that emits surgical replacement values for the flagged
# fields. Apply patches via path-walker into in-memory pass outputs + write
# patched cache files. Optionally re-fire 7-pre / 7-anach / 7a once for
# verification. No iteration. No writer re-invocation. Single shot.
#
# Why this replaces FU#3 surgical revision loop: writer re-invocation
# over-corrected on the in-flight Dostoevsky run (Pass 7-pre's REVIEW_NEEDED
# metrics showed +29 dossier_only and +8 inconsistent citations after
# surgical loop 1 — Opus + thinking + critique tends toward EXPANSION
# rather than the TRIM the validator wanted). A focused field-level patcher
# avoids that pattern: explicit "replace this exact value" with no other
# changes. Cost ~$0.50-1 vs ~$5-10 per loop. Removed: DOWNSTREAM_CHAIN,
# _TARGET_FNAME, MAX_REVISION_LOOPS-bounded while loop, SKIP_REVISION_LOOPS
# env var, REVISION_CRITIQUES dict, surgical-vs-cascade branching, post_7a
# invalidation list (replaced with simpler post-fix invalidation).

# _apply_patch_in_place moved to flows/shared/patch_walker.py (FU#10-mod
# 2026-04-24) for testability. Imported above as alias.


_PASS_VAR_LOOKUP = {
    "2": "pass2", "3": "pass3", "4a": "pass4a", "4b": "pass4b",
    "5": "pass5", "6": "pass6",
}
_PASS_PATH_FNS = {
    "2": _paths.pass_2, "3": _paths.pass_3, "4a": _paths.pass_4a,
    "4b": _paths.pass_4b, "5": _paths.pass_5, "6": _paths.pass_6,
}


def _pass_7a_fix(pass7a_result: dict, pass7_anach_result: dict) -> dict:
    """Linear field-level patcher. Fires once; applies patches to in-memory
    pass outputs + cache files. Returns fix_log dict (also written to disk
    by caller)."""
    fix_log = {
        "validator_verdict": pass7a_result.get("overall"),
        "validator_model": pass7a_result.get("validator", "unknown"),
        "field_issues_count": len(pass7a_result.get("field_issues", []) or []),
        "anachronism_flags_count": len(pass7_anach_result.get("anachronism_flags", []) or []),
        "patches_emitted": 0,
        "patches_applied": 0,
        "patches_failed": 0,
        "patches_skipped": 0,
        "post_fix_verdict": None,
        "patches": [],
        "log": [],
    }

    field_issues = pass7a_result.get("field_issues", []) or []
    if not field_issues:
        fix_log["log"].append("No field_issues to patch — skipping fix-pass entirely")
        return fix_log

    affected = sorted({str(i.get("flagged_pass") or i.get("revision_target_pass") or "")
                       for i in field_issues})
    affected = [p for p in affected if p in _PASS_VAR_LOOKUP]
    if not affected:
        fix_log["log"].append(f"No actionable passes in field_issues — skipping. "
                               f"Issues: {len(field_issues)}")
        return fix_log

    # FU#5 (2026-04-23): snapshot pre-fix state of 04_generation + 05_validation
    # so operator can diff post-fix vs pre-fix card. Single snapshot per voice
    # (no per-loop directories — there are no loops under FU#13). Triggered
    # before patches land + cache files get overwritten.
    import shutil
    snapshot_root = _paths.voice_root(SLUG, PROJECT_ROOT) / "04_generation" / "_snapshots" / "pre_fix_pass"
    snapshot_root.mkdir(parents=True, exist_ok=True)
    for src_subdir in ("04_generation", "05_validation"):
        src = _paths.voice_root(SLUG, PROJECT_ROOT) / src_subdir
        if not src.exists():
            continue
        dst = _paths.voice_root(SLUG, PROJECT_ROOT) / src_subdir / "_snapshots" / "pre_fix_pass"
        dst.mkdir(parents=True, exist_ok=True)
        for f in src.glob("*.json"):
            try:
                shutil.copy2(f, dst / f.name)
            except OSError as e:
                fix_log["log"].append(f"WARN snapshot {f.name}: {type(e).__name__}: {e}")
    fix_log["snapshot_dir_pre_fix"] = "04_generation/_snapshots/pre_fix_pass + 05_validation/_snapshots/pre_fix_pass"
    fix_log["log"].append(f"Snapshotted pre-fix state to {fix_log['snapshot_dir_pre_fix']}")

    pass_outputs = {}
    for pass_id in affected:
        var = globals().get(_PASS_VAR_LOOKUP[pass_id])
        if var and var.get("fields"):
            pass_outputs[f"pass_{pass_id}"] = var["fields"]

    voice_context = {
        "rhetorical_mode": pass4a["fields"].get("rhetorical_mode", ""),
        "register_and_tone": pass4a["fields"].get("register_and_tone", ""),
        "characteristic_moves": pass4a["fields"].get("characteristic_moves", []),
        "translation_protocol": pass2["fields"].get("translation_protocol", ""),
        "knowledge_boundary": pass2["fields"].get("knowledge_boundary", ""),
    }

    sysp = load_prompt("persona_pass_7a_fix")
    userp = render(
        "persona_pass_7a_fix_user",
        field_issues_json=json.dumps(field_issues, ensure_ascii=False, indent=2),
        relevant_pass_outputs_json=json.dumps(pass_outputs, ensure_ascii=False, indent=2),
        rhetorical_mode=str(voice_context["rhetorical_mode"]),
        register_and_tone=str(voice_context["register_and_tone"]),
        characteristic_moves_json=json.dumps(voice_context["characteristic_moves"],
                                              ensure_ascii=False, indent=2),
        translation_protocol=str(voice_context["translation_protocol"]),
        knowledge_boundary=str(voice_context["knowledge_boundary"]),
    )

    stamp(f"PASS 7a-FIX: linear patcher (Opus 4.7 + thinking, "
          f"{len(field_issues)} field issues across passes {affected})")
    # 2026-04-23 (live test iteration):
    # - Sonnet 4.6 + thinking + 16K: hit max, raw text 0
    # - Sonnet 4.6 + thinking + 48K: hit max, raw text 3239 chars (~800 tokens)
    # - Sonnet adaptive thinking deliberates extensively on 20+ issues, eating
    #   most of max_tokens. Even 64K (Sonnet's standard ceiling) might not be
    #   enough for 20+ issues.
    # Switching model: Opus 4.7 + thinking @ 32K (the established pattern for
    # Pass 2/3/4a/5/7b — works reliably). FU#13's expansion-risk concern was
    # about writer re-invocation with critique; the patcher prompt's
    # "trim don't expand" + "modify ONLY flagged fields" + "schema-preserving"
    # guardrails counter the Opus expansion tendency.
    r = call_claude(system=sysp, user=userp, model="claude-opus-4-7",
                    max_tokens=32000, temperature=1.0, thinking=True,
                    response_format_json=True)

    patches = r["json"].get("patches", []) or []
    fix_log["patches_emitted"] = len(patches)

    for patch in patches:
        pass_id = str(patch.get("pass_id", ""))
        field_path = patch.get("field_path", "")
        new_value = patch.get("new_value")
        rationale = patch.get("rationale", "")

        if not (pass_id and field_path):
            fix_log["patches_skipped"] += 1
            fix_log["log"].append(f"SKIP malformed patch: {patch}")
            continue
        if pass_id not in _PASS_VAR_LOOKUP:
            fix_log["patches_skipped"] += 1
            fix_log["log"].append(f"SKIP patch: unknown pass_id={pass_id!r}")
            continue

        try:
            var_name = _PASS_VAR_LOOKUP[pass_id]
            pass_var = globals()[var_name]
            _apply_patch_in_place(pass_var["fields"], field_path, new_value)
            cache_path = _PASS_PATH_FNS[pass_id](SLUG, PROJECT_ROOT)
            write_json_atomic(cache_path, pass_var)
            fix_log["patches_applied"] += 1
            fix_log["patches"].append({
                "pass_id": pass_id, "field_path": field_path,
                "rationale": rationale, "status": "applied",
            })
            fix_log["log"].append(f"APPLIED pass_{pass_id}.{field_path}: {rationale[:120]}")
        except Exception as e:
            fix_log["patches_failed"] += 1
            fix_log["patches"].append({
                "pass_id": pass_id, "field_path": field_path,
                "rationale": rationale, "status": "failed",
                "error": f"{type(e).__name__}: {str(e)[:200]}",
            })
            fix_log["log"].append(f"FAILED pass_{pass_id}.{field_path}: "
                                   f"{type(e).__name__}: {str(e)[:120]}")

    return fix_log


# ---------- LINEAR FLOW: fire fix-pass once if REVISION_NEEDED ----------
fix_log_path = _paths.merge_dir(SLUG, PROJECT_ROOT) / "_fix_log.json"

if pass7a["result"].get("overall") == "REVISION_NEEDED" and not fix_log_path.exists():
    # Skip if fix-pass already ran on this card (single-shot per FU#13 design;
    # without this guard, every pipeline restart re-fires fix-pass since Pass 7a
    # cache stays REVISION_NEEDED. Operator deletes _fix_log.json + downstream
    # caches manually if a re-fix is desired.)
    fix_log = _pass_7a_fix(pass7a["result"], pass7_anach["result"])
    write_json_atomic(fix_log_path, fix_log)

    if fix_log["patches_applied"] > 0:
        # Patches landed — invalidate downstream + re-fire validators once
        for p in [_paths.pass_7_pre(SLUG, PROJECT_ROOT),
                  _paths.pass_7_anachronism(SLUG, PROJECT_ROOT),
                  _paths.pass_7a(SLUG, PROJECT_ROOT),
                  _paths.pass_7b(SLUG, PROJECT_ROOT),
                  _paths.pass_7c(SLUG, PROJECT_ROOT),
                  _paths.derive_raw(SLUG, PROJECT_ROOT),
                  _paths.assembled_card(SLUG, PROJECT_ROOT),
                  _paths.provocateur_profile(SLUG, PROJECT_ROOT),
                  _paths.evaluation_rubric(SLUG, PROJECT_ROOT)]:
            if p.exists():
                p.unlink()

        # Refresh cumulative card dicts (Pass 2-6 may have changed)
        combined_2_3 = {**pass2["fields"], **pass3["fields"]}
        combined_2_3_4a = {**combined_2_3, **pass4a["fields"]}
        combined_2_3_4 = {**combined_2_3_4a, **pass4b["fields"]}

        # Re-fire Pass 7-pre + Pass 7-anachronism + Pass 7a once for verification.
        # Wrapped in try/except per Pass 7-pre 128K ceiling: richer post-fix
        # cards may exceed Sonnet 4.6's max output. FU#2 (chunked verification)
        # is the architectural fix; this stop-gap lets pipeline ship the
        # patched card with REVISION_NEEDED status preserved if validators
        # can't complete.
        try:
            pass7pre = call_or_cache(_paths.pass_7_pre(SLUG, PROJECT_ROOT),
                                     "Pass 7-pre (post-fix)", _pass_7pre)
        except RuntimeError as e:
            stamp(f"  WARN: Pass 7-pre (post-fix) hit ceiling: {str(e)[:160]}")
            stamp(f"  Proceeding without post-fix Pass 7-pre verification "
                  f"(FU#2 architectural fix needed). Card ships with patched "
                  f"content + pre-fix Pass 7-pre verdict in metadata.")
            fix_log["log"].append(f"Pass 7-pre (post-fix) skipped due to ceiling: "
                                   f"{type(e).__name__}: {str(e)[:160]}")
        try:
            if fix_log["anachronism_flags_count"] > 0:
                pass7_anach = call_or_cache(_paths.pass_7_anachronism(SLUG, PROJECT_ROOT),
                                             "Pass 7-anachronism (post-fix)",
                                             _pass_7_anachronism)
        except Exception as e:
            stamp(f"  WARN: Pass 7-anachronism (post-fix) failed: {str(e)[:160]}")
            fix_log["log"].append(f"Pass 7-anachronism (post-fix) skipped: "
                                   f"{type(e).__name__}: {str(e)[:160]}")
        try:
            pass7a = call_or_cache(_paths.pass_7a(SLUG, PROJECT_ROOT),
                                    "Pass 7a (post-fix)", _pass_7a)
            fix_log["post_fix_verdict"] = pass7a["result"].get("overall")
        except Exception as e:
            stamp(f"  WARN: Pass 7a (post-fix) failed: {str(e)[:160]}")
            fix_log["post_fix_verdict"] = "VERIFICATION_FAILED"
            fix_log["log"].append(f"Pass 7a (post-fix) skipped: "
                                   f"{type(e).__name__}: {str(e)[:160]}")
        write_json_atomic(fix_log_path, fix_log)

        stamp(f"PASS 7a-FIX: applied {fix_log['patches_applied']} of "
              f"{fix_log['patches_emitted']} patches "
              f"(failed={fix_log['patches_failed']}, skipped={fix_log['patches_skipped']}); "
              f"post-fix verdict: {fix_log['post_fix_verdict']}")
    else:
        stamp(f"PASS 7a-FIX: 0 patches applied (emitted={fix_log['patches_emitted']}, "
              f"failed={fix_log['patches_failed']}, skipped={fix_log['patches_skipped']}); "
              f"accepting Pass 7a verdict as-is")

# Final verdict (whether or not fix-pass ran)
if pass7a["result"].get("overall") == "REVISION_NEEDED":
    stamp(f"FINAL: post-fix verdict still REVISION_NEEDED — flagged for human review")
else:
    stamp(f"FINAL: 7a verdict {pass7a['result'].get('overall', '?')} — "
          f"proceeding to 7b/7c/Derive/Assembly")


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
    # 2026-04-23: model upgraded claude-sonnet-4-6 → claude-opus-4-7 + thinking
    # ON (quality-tuning checklist). Derive is HIGH-LEVERAGE: provocateur_
    # profile.system_prompt drives every runtime interaction × sessions ×
    # turns × voices. Small quality differential here multiplies across
    # thousands of runtime touchpoints. Despite consuming an Opus-quality
    # card, derive itself is judgment-bound: selective synthesis (44 fields
    # → ~5-10K prompt), voice-embedding from word one (Dostoevskian texture
    # in the prompt voice; non-anthropocentric framing for Octopus), high-
    # ratio compression with nuance preservation, AND original generation
    # of evaluation_rubric (voice-specific scoring criteria, not derived).
    # Sonnet rubric-follows; Opus + thinking deliberates the tradeoffs.
    # Cost: ~$0.10-0.30 extra per voice (runs once). Quality: meaningful at
    # every runtime turn. max_tokens 8192 → 24000 (thinking + ~10K output).
    # temperature 0.1 → 1.0 (required for thinking).
    r = call_claude(system=sysp, user=userp, model="claude-opus-4-7",
                    max_tokens=24000, temperature=1.0, thinking=True,
                    response_format_json=True)
    return {"voice_name": vi["name"], "voice_slug": SLUG, "pass": "derive",
            "model": r["model"], "usage": r["usage"], "result": r["json"]}

stamp("DERIVE: Provocateur Profile + Evaluation Rubric (Opus + thinking)")
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
_fix_log_summary = (
    "no fix needed" if not fix_log_path.exists()
    else f"fix-pass applied {json.loads(fix_log_path.read_text()).get('patches_applied', 0)} "
         f"of {json.loads(fix_log_path.read_text()).get('patches_emitted', 0)} patches"
)
stamp(f"  Pass 7a validate:     {pass7a['result'].get('overall', '?')} ({pass7a.get('validator', '?')}) "
      f"— {_fix_log_summary}")
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
            *(["7a_fix_linear_patcher"] if fix_log_path.exists() else []),
            "7b_smoke_test_chains",
            "7c_negative_constraints",
            "derive_provocateur_profile_and_rubric",
        ],
        "validation_status": pass7a["result"].get("overall", "unknown"),
        "fix_pass_log": (json.loads(fix_log_path.read_text()) if fix_log_path.exists() else None),
        "tools_used": ["perplexity:sonar-deep-research", "anthropic:claude-opus-4-7", "anthropic:claude-sonnet-4-6", "google:gemini-2.5-pro", "openai:gpt-5.4", "gutenberg:web_fetch"],
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


# ---------- FU#41 2026-04-24: chat-ready system prompt artifact ----------
# Writes a 4th Derive artifact (alongside provocateur_profile + evaluation_
# rubric): a chat-ready persona-card JSON suitable for direct paste into
# Claude project custom instructions. Mechanical field-strip transform of
# the assembled card — drops Voice-Pipeline-only fields (metadata,
# smoke_test_chains, reference_only_passages, artifact-spec fields,
# continuity blocks). No content modification; editorial polish is operator
# territory. Enables fast chat-test validation: pipeline run -> paste
# artifact -> ask probing question -> assess voice quality. See
# flows/shared/chat_prompt_builder.py for the transformation spec + the
# list of Voice-Pipeline-only fields dropped.
_assembled_card_dict = json.loads(_paths.assembled_card(SLUG, PROJECT_ROOT).read_text())
_chat_prompt_path = _paths.voice_root(SLUG, PROJECT_ROOT) / "06_derive" / "03_chat_system_prompt.json"
write_chat_system_prompt(_assembled_card_dict, _chat_prompt_path)
stamp(f"Chat-ready system prompt -> {_chat_prompt_path.relative_to(PROJECT_ROOT)}")


# ---------- FU#7 2026-04-24: Operator-facing CARD COMPLETE summary ----------
# Compact end-of-pipeline decision helper — surfaces validation_status,
# human_review_status, fix-pass effectiveness, top concerns (severity-
# ordered), recommended action, and artifact paths. Operators skim this
# to triage 12 voices at panel scale without opening each card.

def _compose_top_concerns(
    pass7a_result: dict,
    pass7pre_result: dict,
    fix_log: dict | None,
    register_violations: int,
) -> list[str]:
    """Severity-ordered top-concerns list for operator triage."""
    concerns: list[tuple[str, str]] = []  # (severity, description)
    if register_violations > 0:
        concerns.append(("HIGH", f"Register violations: {register_violations} field(s) — see metadata.register_violation_details"))
    pass7a_issues = pass7a_result.get("field_issues", []) or []
    if len(pass7a_issues) > 0:
        concerns.append(("HIGH", f"Pass 7a field_issues: {len(pass7a_issues)} flagged — see metadata.cross_model_validation"))
    summary = pass7pre_result.get("summary", {}) or {}
    unverified = summary.get("unverified", 0)
    inconsistent = summary.get("inconsistent", 0)
    if inconsistent > 0:
        concerns.append(("HIGH", f"Pass 7-pre INCONSISTENT claims: {inconsistent}"))
    if unverified > 0:
        concerns.append(("MED", f"Pass 7-pre UNVERIFIED claims: {unverified}"))
    if pass7pre_result.get("overall") == "VERIFICATION_SKIPPED":
        concerns.append(("MED", "Pass 7-pre skipped (likely ceiling hit pre-FU#2, or chunked pipeline failure)"))
    boddice_count = len(pass7pre_result.get("boddice_tag_flags", []) or [])
    if boddice_count > 0:
        concerns.append(("MED", f"Boddice tag flags: {boddice_count} missing tag(s)"))
    if fix_log:
        remaining_issues = fix_log.get("field_issues_count", 0) - fix_log.get("patches_applied", 0)
        if remaining_issues > 0:
            concerns.append(("LOW", f"Fix-pass residual: {remaining_issues} field_issues not resolved by patches"))
        failed = fix_log.get("patches_failed", 0) or 0
        if failed > 0:
            concerns.append(("HIGH", f"Fix-pass failures: {failed} patch(es) failed validation"))
    severity_order = {"HIGH": 0, "MED": 1, "LOW": 2}
    concerns.sort(key=lambda c: severity_order.get(c[0], 99))
    return [f"[{sev}] {desc}" for sev, desc in concerns[:8]]


def _compose_recommended_action(
    pass7a_result: dict,
    pass7pre_result: dict,
    register_violations: int,
    fix_log: dict | None,
) -> str:
    overall_a = (pass7a_result.get("overall") or "").upper()
    overall_pre = (pass7pre_result.get("overall") or "").upper()
    if overall_a == "PASS" and overall_pre == "PASS" and register_violations == 0:
        return "Card ready for human review + sign-off."
    actions: list[str] = []
    if overall_a == "REVISION_NEEDED":
        actions.append("Pass 7a flagged REVISION_NEEDED; review top concerns above.")
    if overall_pre == "VERIFICATION_SKIPPED":
        actions.append("Pass 7-pre skipped — confirm FU#2 chunked pipeline status or manually review citations.")
    elif overall_pre == "REVIEW_NEEDED":
        actions.append("Pass 7-pre flagged REVIEW_NEEDED; inspect _pass_7_pre_citation.json for per-item verdicts.")
    if register_violations > 0:
        actions.append(f"{register_violations} register violation(s) — rewrite flagged fields into first/second person.")
    if fix_log and (fix_log.get("patches_failed", 0) or 0) > 0:
        actions.append("Patch validation failures — inspect _fix_log.json for error traces.")
    if not actions:
        actions.append("Review flagged items above; manual spot-check may resolve.")
    return " | ".join(actions)


_card_path = _paths.assembled_card(SLUG, PROJECT_ROOT)
_provocateur_path = _paths.voice_root(SLUG, PROJECT_ROOT) / "06_derive" / "01_provocateur_profile.json"
_rubric_path = _paths.voice_root(SLUG, PROJECT_ROOT) / "06_derive" / "02_evaluation_rubric.json"
_fix_log_for_summary = json.loads(fix_log_path.read_text()) if fix_log_path.exists() else None
_top_concerns = _compose_top_concerns(
    pass7a["result"], pass7pre["result"], _fix_log_for_summary, register_violations
)
_recommended = _compose_recommended_action(
    pass7a["result"], pass7pre["result"], register_violations, _fix_log_for_summary
)
_card_size_bytes = _card_path.stat().st_size if _card_path.exists() else 0

print()
stamp("=" * 60)
stamp(f"CARD COMPLETE — operator triage summary")
stamp("=" * 60)
stamp(f"  voice:                 {vi['name']} ({SLUG})")
stamp(f"  card size:             {_card_size_bytes:,} bytes ({len(full_card)} fields)")
stamp(f"  validation_status:     {pass7a['result'].get('overall', 'unknown')}")
stamp(f"  human_review_status:   pending")
stamp("")
if _fix_log_for_summary:
    stamp(f"  Fix-pass effectiveness:")
    stamp(f"    patches:             {_fix_log_for_summary.get('patches_applied', 0)} applied / "
          f"{_fix_log_for_summary.get('patches_emitted', 0)} emitted "
          f"(failed: {_fix_log_for_summary.get('patches_failed', 0) or 0}, "
          f"skipped: {_fix_log_for_summary.get('patches_skipped', 0) or 0})")
    stamp(f"    anachronism_flags:   {_fix_log_for_summary.get('anachronism_flags_count', 0)} initial")
    stamp(f"    field_issues:        {_fix_log_for_summary.get('field_issues_count', 0)} initial")
    stamp(f"    post_fix_verdict:    {_fix_log_for_summary.get('post_fix_verdict', '?')}")
else:
    stamp(f"  Fix-pass effectiveness: no fix needed (Pass 7a PASSED, or verdict was SKIPPED)")
stamp("")
_pass7pre_summary = pass7pre["result"].get("summary", {}) or {}
_items_count = len(pass7pre["result"].get("items", []) or [])
stamp(f"  Pass 7-pre citation audit:")
stamp(f"    items:               {_items_count}")
stamp(f"    verified:            {_pass7pre_summary.get('verified', 0)}")
stamp(f"    unverified:          {_pass7pre_summary.get('unverified', 0)}")
stamp(f"    dossier_only:        {_pass7pre_summary.get('dossier_only', 0)}")
stamp(f"    interpretive:        {_pass7pre_summary.get('interpretive', 0)}")
stamp(f"    inconsistent:        {_pass7pre_summary.get('inconsistent', 0)}")
stamp(f"    boddice_tag_flags:   {len(pass7pre['result'].get('boddice_tag_flags', []) or [])}")
stamp("")
if _top_concerns:
    stamp(f"  Top concerns (severity-ordered):")
    for concern in _top_concerns:
        stamp(f"    {concern}")
    stamp("")
stamp(f"  Recommended action:")
for _line in _recommended.split(" | "):
    stamp(f"    → {_line}")
stamp("")
stamp(f"  Artifacts:")
stamp(f"    card:                {_card_path.relative_to(PROJECT_ROOT)}")
if _provocateur_path.exists():
    stamp(f"    provocateur_profile: {_provocateur_path.relative_to(PROJECT_ROOT)}")
if _rubric_path.exists():
    stamp(f"    evaluation_rubric:   {_rubric_path.relative_to(PROJECT_ROOT)}")
if fix_log_path.exists():
    stamp(f"    fix_log:             {fix_log_path.relative_to(PROJECT_ROOT)}")
_synthesis_audit_path = _paths.voice_root(SLUG, PROJECT_ROOT) / "_synthesis_audit.json"
if _synthesis_audit_path.exists():
    stamp(f"    synthesis_audit:     {_synthesis_audit_path.relative_to(PROJECT_ROOT)}")
if _chat_prompt_path.exists():
    stamp(f"    chat_system_prompt:  {_chat_prompt_path.relative_to(PROJECT_ROOT)}")
    stamp(f"                         (paste into Claude project custom instructions)")
stamp("=" * 60)
