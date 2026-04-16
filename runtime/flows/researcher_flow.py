"""Researcher Pipeline — flows/researcher_flow.py

Takes a run directory containing session packages from the Transcription
Pipeline and produces the Researcher's two outputs: a complete extraction
table (atomic positions, reframings, and open questions from every session)
and a themed grouping (those extractions clustered into themes by affinity).

Usage:
    python flows/researcher_flow.py runs/dev_msc_test

Inputs (relative to the run directory):
    01_transcription/<session>/session_package.json    — per-session

Outputs (relative to the run directory):
    02_researcher/<session>_extractions.json            — per-session Node 1
    02_researcher/all_extractions.json                  — concatenated +
                                                          globally renumbered
    02_researcher/grouping.json                         — Node 2 output

For full architecture detail, see the v2.4 stage entry in the run's
_manifest.json. The current canonical pipeline version is v2.4 — Opus
4.6 with adaptive thinking, KJ-method clustering with minimal model-
facing input + deterministic shuffle, theme grouping operating on
cluster abstracts only (not raw extractions).
"""

from __future__ import annotations

import json
import os
import random
import sys
import time
from pathlib import Path

# Make `flows.shared.io` importable when this script is run directly
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

try:
    from anthropic import Anthropic
    from prefect import flow, task, get_run_logger
    from prefect.tasks import exponential_backoff
    from dotenv import load_dotenv
    load_dotenv(_REPO_ROOT.parent / ".env")
    from flows.shared.io import (
        extract_json,
        get_logger,
        load_prompt,
        load_session_package,
        write_json_atomic,
    )
except ImportError as e:
    sys.stderr.write(
        f"Missing dependency: {e.name}\n"
        "Install with:  pip install anthropic prefect python-dotenv\n"
    )
    sys.exit(1)


# --- Config ---------------------------------------------------------------

# Default to Opus 4.6 — canonical model for Researcher Pipeline v3 per the
# v2.4 validation run. Override via CLAUDE_MODEL env var for dev iteration
# on Sonnet (CLAUDE_MODEL=claude-sonnet-4-6 python3 flows/researcher_flow.py).
CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", "claude-opus-4-6")

# Extended thinking (Opus 4.6 is the recommended target, works on Sonnet
# 4.6 too). Enabled via env var so the same code path supports both
# "fast Sonnet baseline" and "slow Opus+thinking baseline" without edits.
# When enabled, max_tokens headroom below must accommodate both output
# and thinking tokens (in recent API versions thinking counts against
# max_tokens).
# Default to thinking ON — canonical setting for Researcher Pipeline v3.
# Disable via RESEARCHER_THINKING=0 env var for dev iteration.
THINKING_ENABLED = os.environ.get("RESEARCHER_THINKING", "1") != "0"
EXTRACTION_THINKING_BUDGET = 8000
CLUSTERING_THINKING_BUDGET = 20000
THEMING_THINKING_BUDGET = 15000

# Per-task output budgets. When thinking is enabled these are sized to
# include both the thinking budget and the actual response with headroom.
# When thinking is disabled these are looser than strictly necessary but
# the unused portion is free.
EXTRACTION_MAX_TOKENS = 40000  # was 32000 pre-thinking

# Round 1 (clustering) produces one cluster per ~2-3 extractions with
# declarative title + abstract + extraction_ids. The dev_msc_test run at
# 85 extractions → 34 clusters used ~5-6K output tokens with Sonnet; with
# a 20K thinking budget on top we need 40K ceiling.
CLUSTERING_MAX_TOKENS = 40000  # was 16000 pre-thinking

# Round 2 (theming) output is small — cluster_ids only, no raw text
# repetition. ~20 themes × ~250 tokens each = 5K. With 15K thinking
# budget we need 24K ceiling.
THEMING_MAX_TOKENS = 24000  # was 8000 pre-thinking


def _thinking_kwargs(budget_tokens: int) -> dict:
    """Return the thinking kwargs for messages.create/stream when enabled.

    When THINKING_ENABLED is False (default), returns an empty dict so
    `**_thinking_kwargs(...)` is a no-op on the API call. When enabled,
    returns Opus 4.6's recommended 'adaptive' thinking mode — the model
    decides how much to think based on the task, which Anthropic's own
    testing shows outperforms fixed-budget 'enabled' mode. The
    `budget_tokens` argument is kept for API symmetry but is unused in
    adaptive mode (it's documented in the per-task constants for future
    reference and fallback).

    Extended thinking requires temperature=1.0. This matches the SDK
    default but is set explicitly for safety against default drift.
    """
    if not THINKING_ENABLED:
        return {}
    return {
        "thinking": {
            "type": "adaptive",
        },
        "temperature": 1.0,
    }


# --- Logger shim ----------------------------------------------------------
# Delegates to flows.shared.io.get_logger — same implementation used by
# transcription_flow and provocateur_flow.

def _get_logger():
    return get_logger("researcher_flow")


# --- Prompts --------------------------------------------------------------

EXTRACTION_SYSTEM = load_prompt("researcher_extraction")
CLUSTERING_SYSTEM = load_prompt("researcher_clustering")
THEMING_SYSTEM = load_prompt("researcher_theming")


# --- Helpers --------------------------------------------------------------

def build_extraction_user_prompt(pkg: dict, session_id: str) -> str:
    """Assemble the Node 1 user message from a session package.

    The `session_id` is the short identifier (e.g. 'vox_populi') used as
    the namespace prefix for generated extraction ids — the system prompt
    reads it from the user message header.
    """
    meta = pkg.get("metadata", {})
    transcript = pkg.get("transcript", {})
    review_queue = pkg.get("review_queue", {})
    verify_markers = review_queue.get("verify_markers", [])

    roster_lines = []
    for c in meta.get("roster", []):
        line = f"- {c['name']}"
        if c.get("title"):
            line += f", {c['title']}"
        if c.get("affiliation"):
            line += f", {c['affiliation']}"
        if c.get("bio"):
            line += f"\n  Bio: {c['bio']}"
        roster_lines.append(line)
    roster_block = "\n".join(roster_lines) if roster_lines else "(none)"

    user = (
        f"session_id: {session_id}\n"
        f"Session: {meta.get('session_title', '')}\n"
        f"Description: {meta.get('session_description', '')}\n"
        f"Format: {meta.get('session_format', 'panel')}\n\n"
        f"Roster (scheduled contributors with bios):\n"
        f"{roster_block}\n\n"
        f"Speakers present (who actually spoke):\n"
        f"{json.dumps(transcript.get('speakers_present', []), ensure_ascii=False)}\n\n"
        f"Transcript (each turn has turn_index, speaker, role, confidence, "
        f"text — confidence reflects how certain the upstream pipeline was "
        f"about the speaker attribution; treat low-confidence speaker labels "
        f"with appropriate caution):\n"
        f"{json.dumps(transcript.get('turns', []), indent=2, ensure_ascii=False)}\n\n"
        f"Review queue — turns containing words the cleaning pass flagged as "
        f"uncertain (proper names, acronyms, policy terms). Each entry "
        f"references a turn by its turn_index. When an extraction's substance "
        f"hinges on one of these flagged words, mark the extraction's context "
        f"with \"[word uncertain in source]\":\n"
        f"{json.dumps(verify_markers, indent=2, ensure_ascii=False)}"
    )
    return user


def validate_and_concat(per_session_results: list, logger=None) -> list:
    """Concatenate per-session extractions and validate namespaced IDs.

    Each session's Node 1 output carries IDs in the format
    `{session_id}:NNN` where the session_id matches the containing
    folder name. Because each session generates its IDs independently
    using its own namespace, IDs are globally unique by construction —
    no renumbering needed.

    This function performs two defensive checks:
    1. Coerces any integer IDs back to strings (in case the model
       forgot the format rule) and flags them as warnings.
    2. Detects duplicate IDs across sessions (should never happen with
       proper namespacing, but catches model drift).

    Returns a flat list of extractions with their IDs preserved.
    """
    all_extractions = []
    seen_ids = set()
    collisions = []
    coerced = 0

    for result in per_session_results:
        session_id = result.get("session_id", "unknown")
        extractions = result.get("extractions", [])

        for e in extractions:
            # Coerce non-string IDs and responds_to refs
            if not isinstance(e.get("id"), str):
                e["id"] = str(e["id"])
                coerced += 1
            rt = e.get("responds_to")
            if rt is not None and not isinstance(rt, str):
                e["responds_to"] = str(rt)

            eid = e["id"]
            # Warn if the id doesn't carry the expected namespace prefix
            if not eid.startswith(f"{session_id}:"):
                if logger:
                    logger.warning(
                        f"Extraction id '{eid}' in session '{session_id}' "
                        f"does not carry the expected namespace prefix. "
                        f"Downstream linking may break."
                    )

            if eid in seen_ids:
                collisions.append(eid)
            seen_ids.add(eid)

        all_extractions.extend(extractions)

    if coerced and logger:
        logger.warning(
            f"Coerced {coerced} non-string extraction ids to strings"
        )
    if collisions and logger:
        logger.error(
            f"ID collisions across sessions: {collisions}. "
            f"Namespacing is broken."
        )

    return all_extractions


# --- Tasks ----------------------------------------------------------------

@task(
    name="researcher-extract",
    retries=2,
    retry_delay_seconds=exponential_backoff(backoff_factor=5),
)
def extract_session(session_package_path: str) -> dict:
    """Node 1: Extract positions, reframings, and open questions from one
    session package."""
    logger = _get_logger()
    client = Anthropic()

    pkg_path = Path(session_package_path)
    pkg = load_session_package(pkg_path)
    session_id = pkg_path.parent.name
    session_title = pkg.get("metadata", {}).get(
        "session_title", session_id
    )

    logger.info(
        f"Node 1 extraction: {session_title} (session_id={session_id})"
        + (f" [thinking={EXTRACTION_THINKING_BUDGET}]" if THINKING_ENABLED else "")
    )
    user = build_extraction_user_prompt(pkg, session_id)

    # Streaming required for outputs that may exceed the SDK's 21K
    # non-streaming threshold.
    t0 = time.time()
    chunks = []
    with client.messages.stream(
        model=CLAUDE_MODEL,
        max_tokens=EXTRACTION_MAX_TOKENS,
        system=EXTRACTION_SYSTEM,
        messages=[{"role": "user", "content": user}],
        **_thinking_kwargs(EXTRACTION_THINKING_BUDGET),
    ) as stream:
        for text in stream.text_stream:
            chunks.append(text)
        final = stream.get_final_message()
    full_text = "".join(chunks)
    logger.info(
        f"  done in {time.time()-t0:.1f}s "
        f"(in={final.usage.input_tokens}, out={final.usage.output_tokens})"
    )
    if final.usage.output_tokens > EXTRACTION_MAX_TOKENS * 0.8:
        logger.warning(
            f"Extraction used {final.usage.output_tokens}/"
            f"{EXTRACTION_MAX_TOKENS} output tokens (>80%). Consider "
            f"increasing EXTRACTION_MAX_TOKENS."
        )

    extractions = extract_json(full_text)
    for e in extractions:
        e["session"] = session_title

    logger.info(f"  extracted {len(extractions)} items")
    return {
        "session_id": session_id,
        "session_title": session_title,
        "extractions": extractions,
    }


@task(
    name="researcher-cluster",
    retries=2,
    retry_delay_seconds=exponential_backoff(backoff_factor=5),
)
def cluster_extractions(all_extractions: list) -> dict:
    """Node 2 Round 1: group extractions into clusters.

    The model-facing input is stripped to content only — `extraction`
    and `context` — with a temp `ref` id scoped to this call. Session,
    speaker, lens, responds_to, engagement, energy, and the real
    namespaced id are NOT visible to the clustering LLM call. This
    prevents the model from using provenance metadata as a grouping
    shortcut (e.g. clustering by session prefix) and forces affinity
    judgment based on claim content alone.

    The input array is deterministically shuffled before being sent so
    the model's top-to-bottom reading order does not correlate with
    session structure.

    After the model returns, temp refs are translated back to real
    namespaced extraction ids via a lookup table, and the output is
    validated and normalized to the standard schema (clusters with
    extraction_ids, isolates as a list).
    """
    logger = _get_logger()
    client = Anthropic()

    logger.info(
        f"Node 2 Round 1 (clustering): "
        f"{len(all_extractions)} extractions"
        + (f" [thinking={CLUSTERING_THINKING_BUDGET}]" if THINKING_ENABLED else "")
    )

    # Build the minimal model-facing input. Each extraction gets a
    # temporary zero-padded sequential ref; the real namespaced id is
    # recorded in a lookup table so we can translate the model's output
    # back after the call. Nothing else about the extraction is visible
    # to the model: no session, no speaker, no lens, no responds_to.
    minimal_items = []
    ref_to_real_id = {}
    for i, e in enumerate(all_extractions, start=1):
        ref = f"{i:03d}"
        minimal_items.append({
            "ref": ref,
            "extraction": e.get("extraction", ""),
            "context": e.get("context", "") or "",
        })
        ref_to_real_id[ref] = e["id"]

    # Deterministic shuffle: break the session-ordered top-to-bottom
    # reading bias without losing reproducibility. Fixed seed so the
    # same input always produces the same shuffle.
    rng = random.Random(42)
    rng.shuffle(minimal_items)

    user = json.dumps(minimal_items, indent=2, ensure_ascii=False)

    # Streaming because the output can exceed ~21K at Athens scale; the
    # dev_msc_test run hit the non-streaming ceiling on first attempt and
    # only recovered via Prefect retry. Streaming holds the connection
    # open via SSE chunks and lets us collect the full JSON safely.
    t0 = time.time()
    chunks = []
    with client.messages.stream(
        model=CLAUDE_MODEL,
        max_tokens=CLUSTERING_MAX_TOKENS,
        system=CLUSTERING_SYSTEM,
        messages=[{"role": "user", "content": user}],
        **_thinking_kwargs(CLUSTERING_THINKING_BUDGET),
    ) as stream:
        for text in stream.text_stream:
            chunks.append(text)
        final = stream.get_final_message()
    full_text = "".join(chunks)
    logger.info(
        f"  done in {time.time()-t0:.1f}s "
        f"(in={final.usage.input_tokens}, out={final.usage.output_tokens})"
    )
    if final.usage.output_tokens > CLUSTERING_MAX_TOKENS * 0.8:
        logger.warning(
            f"Clustering used {final.usage.output_tokens}/"
            f"{CLUSTERING_MAX_TOKENS} output tokens (>80%). Consider "
            f"increasing CLUSTERING_MAX_TOKENS."
        )

    raw_result = extract_json(full_text)

    # Translate temp refs back to real namespaced extraction ids and
    # normalize the schema to match what downstream code (theming,
    # merge, Provocateur) expects: clusters carry `extraction_ids`,
    # not `refs`.
    result = {"clusters": [], "isolates": []}
    unknown_refs = []
    for c in raw_result.get("clusters", []):
        translated = []
        for ref in c.get("refs", []):
            real = ref_to_real_id.get(str(ref))
            if real is None:
                unknown_refs.append(ref)
                continue
            translated.append(real)
        result["clusters"].append({
            "cluster_id": c.get("cluster_id"),
            "cluster_title": c.get("cluster_title", ""),
            "cluster_abstract": c.get("cluster_abstract", ""),
            "extraction_ids": translated,
        })
    for ref in raw_result.get("isolates", []) or []:
        real = ref_to_real_id.get(str(ref))
        if real is None:
            unknown_refs.append(ref)
            continue
        result["isolates"].append(real)

    if unknown_refs:
        logger.warning(
            f"Clustering: {len(unknown_refs)} unknown ref(s) in model "
            f"output (not in the input lookup table): {unknown_refs[:10]}"
        )

    result = _validate_clusters(result, all_extractions, logger)

    n_clusters = len(result.get("clusters", []))
    n_isolates = len(result.get("isolates", []))
    logger.info(f"  result: {n_clusters} clusters, {n_isolates} isolates")
    return result


@task(
    name="researcher-theme",
    retries=2,
    retry_delay_seconds=exponential_backoff(backoff_factor=5),
)
def group_clusters_into_themes(clusters_result: dict) -> dict:
    """Node 2 Round 2: group clusters into themes using only cluster
    titles and abstracts (NOT raw extractions). The Round 2 prompt
    explicitly forces the model to work at the cluster level.

    Returns a dict with `themes` (each referencing cluster_ids) that
    is then merged with the Round 1 cluster details to produce the
    final grouping.json structure.
    """
    logger = _get_logger()
    client = Anthropic()

    clusters = clusters_result.get("clusters", [])
    logger.info(
        f"Node 2 Round 2 (theming): {len(clusters)} clusters"
        + (f" [thinking={THEMING_THINKING_BUDGET}]" if THINKING_ENABLED else "")
    )

    # IMPORTANT: the input to Round 2 is deliberately stripped down to
    # cluster_id + cluster_title + cluster_abstract only. The raw
    # extraction_ids are NOT sent — the spec requires Round 2 to work
    # at the cluster level, not by re-grouping raw extractions.
    round2_input = [
        {
            "cluster_id": c["cluster_id"],
            "cluster_title": c["cluster_title"],
            "cluster_abstract": c["cluster_abstract"],
        }
        for c in clusters
    ]

    # Deterministic shuffle to break the within-session adjacency
    # that naturally arises when Round 1 reads extractions in
    # session-grouped chunks. Uses the same fixed seed pattern as
    # Round 1 for reproducibility.
    rng = random.Random(42)
    rng.shuffle(round2_input)

    user = json.dumps(round2_input, indent=2, ensure_ascii=False)

    # Streaming required: when thinking is enabled, the SDK's
    # non-streaming timeout heuristic refuses operations that might
    # exceed 10 minutes. Streaming also handles ThinkingBlock filtering
    # for free — stream.text_stream yields only text deltas and silently
    # skips thinking content.
    t0 = time.time()
    chunks = []
    with client.messages.stream(
        model=CLAUDE_MODEL,
        max_tokens=THEMING_MAX_TOKENS,
        system=THEMING_SYSTEM,
        messages=[{"role": "user", "content": user}],
        **_thinking_kwargs(THEMING_THINKING_BUDGET),
    ) as stream:
        for text in stream.text_stream:
            chunks.append(text)
        final = stream.get_final_message()
    full_text = "".join(chunks)
    logger.info(
        f"  done in {time.time()-t0:.1f}s "
        f"(in={final.usage.input_tokens}, out={final.usage.output_tokens})"
    )

    themes_result = extract_json(full_text)
    themes_result = _validate_themes(themes_result, clusters, logger)

    n_themes = len(themes_result.get("themes", []))
    logger.info(f"  result: {n_themes} themes")
    return themes_result


def merge_clusters_and_themes(
    clusters_result: dict, themes_result: dict
) -> dict:
    """Combine Round 1 clusters and Round 2 themes into the final
    grouping.json structure.

    Round 2's output references clusters by cluster_id; we expand each
    theme's cluster_ids into the full cluster objects from Round 1 so
    downstream consumers see the familiar `themes → clusters →
    extraction_ids` nesting.
    """
    clusters_by_id = {
        c["cluster_id"]: c for c in clusters_result.get("clusters", [])
    }

    merged_themes = []
    for theme in themes_result.get("themes", []):
        merged_clusters = []
        for cid in theme.get("cluster_ids", []):
            if cid in clusters_by_id:
                merged_clusters.append(clusters_by_id[cid])
        merged_themes.append({
            "theme_id": theme.get("theme_id"),
            "title": theme.get("theme_title", theme.get("title", "")),
            "abstract": theme.get("theme_abstract", theme.get("abstract", "")),
            "clusters": merged_clusters,
        })

    return {
        "themes": merged_themes,
        "isolates": clusters_result.get("isolates", []),
    }


def _validate_clusters(
    clusters_result: dict, all_extractions: list, logger
) -> dict:
    """Enforce closure and uniqueness on Round 1 output.

    Every extraction_id in the input must appear exactly once across
    clusters + isolates. Duplicates are dropped (keep first); orphans
    are appended to isolates; empty clusters left by dedup are pruned.
    """
    input_ids = set(e.get("id") for e in all_extractions if e.get("id"))

    # Pass 1: detect duplicates, keep first occurrence
    seen = set()
    dup_log = []
    for cluster in clusters_result.get("clusters", []):
        deduped = []
        for eid in cluster.get("extraction_ids", []):
            if eid in seen:
                dup_log.append((eid, cluster.get("cluster_title", "?")))
                continue
            seen.add(eid)
            deduped.append(eid)
        cluster["extraction_ids"] = deduped

    # Dedupe isolates too
    isolates_deduped = []
    for eid in clusters_result.get("isolates", []) or []:
        if eid in seen:
            dup_log.append((eid, "(isolates)"))
            continue
        seen.add(eid)
        isolates_deduped.append(eid)
    clusters_result["isolates"] = isolates_deduped

    if dup_log:
        logger.warning(
            f"Clustering: dropped {len(dup_log)} duplicate memberships"
        )
        for eid, where in dup_log:
            logger.warning(f"  {eid} dropped from {where}")

    # Pass 1.5: prune empty clusters (dedup leftovers)
    pruned = []
    surviving = []
    for cluster in clusters_result.get("clusters", []):
        if cluster.get("extraction_ids"):
            surviving.append(cluster)
        else:
            pruned.append(cluster.get("cluster_title", "?"))
    clusters_result["clusters"] = surviving
    if pruned:
        logger.warning(f"Clustering: pruned {len(pruned)} empty cluster(s)")
        for p in pruned:
            logger.warning(f"  pruned empty: {p}")

    # Pass 2: find orphans, append to isolates
    orphans = input_ids - seen
    if orphans:
        logger.warning(
            f"Clustering: {len(orphans)} orphans appended to isolates"
        )
        for oid in sorted(orphans):
            logger.warning(f"  orphan: {oid}")
        clusters_result["isolates"].extend(sorted(orphans))

    # Hallucination check
    hallucinated = seen - input_ids
    if hallucinated:
        logger.warning(
            f"Clustering: {len(hallucinated)} hallucinated ids: "
            f"{sorted(hallucinated)}"
        )

    return clusters_result


def _validate_themes(themes_result: dict, input_clusters: list, logger) -> dict:
    """Enforce closure on Round 2 output: every input cluster_id must
    appear in exactly one theme. Duplicates are dropped (keep first);
    orphan clusters are promoted to single-cluster themes per spec.
    """
    input_cluster_ids = set(c["cluster_id"] for c in input_clusters)
    cluster_title_by_id = {
        c["cluster_id"]: c.get("cluster_title", "?") for c in input_clusters
    }

    # Dedupe cluster_ids across themes
    seen = set()
    dup_log = []
    for theme in themes_result.get("themes", []):
        deduped = []
        for cid in theme.get("cluster_ids", []):
            if cid in seen:
                dup_log.append((cid, theme.get("theme_title", "?")))
                continue
            seen.add(cid)
            deduped.append(cid)
        theme["cluster_ids"] = deduped

    if dup_log:
        logger.warning(
            f"Theming: dropped {len(dup_log)} duplicate cluster memberships"
        )
        for cid, where in dup_log:
            logger.warning(f"  {cid} dropped from {where}")

    # Prune themes whose cluster_ids list became empty
    pruned_themes = []
    surviving_themes = []
    for theme in themes_result.get("themes", []):
        if theme.get("cluster_ids"):
            surviving_themes.append(theme)
        else:
            pruned_themes.append(theme.get("theme_title", "?"))
    themes_result["themes"] = surviving_themes
    if pruned_themes:
        logger.warning(
            f"Theming: pruned {len(pruned_themes)} empty theme(s)"
        )

    # Promote orphan clusters to single-cluster themes
    orphans = input_cluster_ids - seen
    if orphans:
        logger.warning(
            f"Theming: {len(orphans)} cluster(s) orphaned by Round 2; "
            f"promoting each to a single-cluster theme per spec"
        )
        next_theme_num = len(surviving_themes) + 1
        for cid in sorted(orphans):
            themes_result["themes"].append({
                "theme_id": f"theme_{next_theme_num:03d}",
                "theme_title": cluster_title_by_id.get(cid, "Untitled"),
                "theme_abstract": (
                    "(auto-promoted: this cluster did not fit any "
                    "multi-cluster theme.)"
                ),
                "cluster_ids": [cid],
            })
            next_theme_num += 1

    # Hallucination check
    hallucinated = seen - input_cluster_ids
    if hallucinated:
        logger.warning(
            f"Theming: {len(hallucinated)} hallucinated cluster_ids: "
            f"{sorted(hallucinated)}"
        )

    return themes_result


# --- Flow -----------------------------------------------------------------

@flow(name="researcher-pipeline")
def run_researcher(run_root: str) -> dict:
    """Run the Researcher pipeline against a run directory.

    Discovers session packages under `{run_root}/01_transcription/*/`,
    extracts per session (Node 1), concatenates with namespaced IDs,
    clusters (Round 1), then themes clusters (Round 2), writing
    intermediate artifacts at each stage.
    """
    logger = _get_logger()
    run_path = Path(run_root).resolve()

    if not run_path.exists():
        raise FileNotFoundError(f"Run directory not found: {run_path}")

    transcription_dir = run_path / "01_transcription"
    if not transcription_dir.exists():
        raise FileNotFoundError(
            f"Expected {transcription_dir} to exist — the Researcher needs "
            f"session packages produced by the Transcription Pipeline."
        )

    packages = sorted(transcription_dir.glob("*/session_package.json"))
    if not packages:
        raise RuntimeError(
            f"No session packages found under {transcription_dir}. "
            f"Expected at least one */session_package.json."
        )

    logger.info(f"Found {len(packages)} session packages:")
    for p in packages:
        logger.info(f"  - {p.parent.name}")

    output_dir = run_path / "02_researcher"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Node 1: extraction per session. Write each per-session output to
    # disk as we go so partial progress survives a crash or timeout.
    per_session_results = []
    for pkg_path in packages:
        result = extract_session(str(pkg_path))
        per_session_results.append(result)
        out_path = output_dir / f"{result['session_id']}_extractions.json"
        write_json_atomic(out_path, result)
        logger.info(f"  wrote {out_path}")

    # Concat with namespaced id validation
    all_extractions = validate_and_concat(per_session_results, logger)
    combined_path = output_dir / "all_extractions.json"
    write_json_atomic(combined_path, all_extractions)
    logger.info(
        f"Wrote {combined_path} — {len(all_extractions)} total extractions"
    )

    # Node 2 Round 1: clustering
    clusters_result = cluster_extractions(all_extractions)
    clusters_path = output_dir / "clusters.json"
    write_json_atomic(clusters_path, clusters_result)
    logger.info(f"Wrote {clusters_path}")

    # Node 2 Round 2: theming (sees only cluster titles + abstracts)
    themes_result = group_clusters_into_themes(clusters_result)

    # Merge Round 1 clusters and Round 2 themes into final grouping
    grouping = merge_clusters_and_themes(clusters_result, themes_result)
    grouping_path = output_dir / "grouping.json"
    write_json_atomic(grouping_path, grouping)
    logger.info(f"Wrote {grouping_path}")

    logger.info(
        "Done. Start with grouping.json, then drill into clusters.json "
        "and all_extractions.json."
    )
    return {
        "all_extractions": all_extractions,
        "clusters": clusters_result,
        "grouping": grouping,
    }


# --- CLI entry point ------------------------------------------------------

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Researcher Pipeline")
    parser.add_argument(
        "run_root",
        help="Path to the run directory (e.g. runs/dev_msc_test)",
    )
    args = parser.parse_args()
    for key in ("ANTHROPIC_API_KEY",):
        if not os.environ.get(key):
            sys.stderr.write(f"Missing environment variable: {key}\n")
            sys.exit(1)
    run_researcher(args.run_root)
