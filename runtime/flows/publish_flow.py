"""Publish Pipeline — cross-pipeline aggregation for the publish layer.

Runs once per night AFTER voice_flow has produced:
  - <run_dir>/04_voice/step3_amended_artifacts/<slug>.json
  - <PROJECT_ROOT>/published_artifacts/nights/night_<N>/<slug>.json
  - <PROJECT_ROOT>/published_artifacts/nights/night_<N>/_index.json

Reads from upstream pipelines (Researcher + Provocateur + Voice) and
produces:

  <PROJECT_ROOT>/published_artifacts/themes/night_<N>/<theme_id>.json
       Per-theme files: theme metadata + clusters + extractions +
       formulations-per-voice + voices-who-addressed + amendments-on-
       this-theme. First-class theme entities so the micro-site can
       render theme pages without re-joining upstream pipelines.

  <PROJECT_ROOT>/published_artifacts/extractions/<extraction_id>.json
       Per-extraction reverse-index: extraction metadata + which
       clusters/themes contain it + which formulations grounded in it
       + which voices addressed it. Lets you walk back from any
       extraction to all the artifacts it informed.

  <PROJECT_ROOT>/published_artifacts/traces/lineage_graph_night_<N>.json
       Per-night bidirectional graph (nodes + edges) walkable in either
       direction: extraction → cluster → theme → formulation →
       detailed_response → first_draft → amended_artifact, and reverse.

  <PROJECT_ROOT>/published_artifacts/voices/<slug>.json
       Per-voice multi-night index. Aggregated across whatever nights
       have published files at the time of run. Gets re-built each
       publish_flow run (additive across nights). Lets the micro-site
       render per-voice timeline pages.

Run:

    python flows/publish_flow.py <run_dir> --night N --project PATH

CLI flags:
    <run_dir>       Run directory containing 02_researcher/ +
                    03_provocateur/ + 04_voice/.
    --night N       Night number (1, 2, or 3).
    --project PATH  PROJECT_ROOT override (or set $AI_ASSEMBLY_PROJECT_ROOT).
    --skip-themes   Skip per-theme file generation.
    --skip-extractions  Skip per-extraction file generation.
    --skip-graph    Skip lineage-graph generation.
    --skip-voices   Skip cross-night per-voice index regeneration.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

try:
    from dotenv import load_dotenv
    load_dotenv(_REPO_ROOT.parent / ".env")
    from flows.shared.io import get_logger, write_json_atomic
    from flows.shared.project_root import add_project_arg, resolve_project_root
except ImportError as e:
    sys.stderr.write(
        f"Missing dependency: {e.name}\n"
        "Install with:  pip install python-dotenv\n"
    )
    sys.exit(1)


# --- Filename helpers ---------------------------------------------------

def _extraction_id_to_filename(extraction_id: str) -> str:
    """Convert an extraction ID like 'breaking_point:014' to a safe filename.

    Filenames can't have colons cross-platform; we use double-underscore
    and the original ID is preserved inside the JSON content for round-
    tripping.
    """
    return extraction_id.replace(":", "__")


def _filename_to_extraction_id(filename: str) -> str:
    """Reverse of _extraction_id_to_filename. Strips .json suffix if present."""
    base = filename.removesuffix(".json")
    return base.replace("__", ":", 1)


# --- Source loaders -----------------------------------------------------

def _load_researcher_outputs(run_dir: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    """Load all_extractions.json + grouping.json from Researcher output."""
    extractions_path = run_dir / "02_researcher" / "all_extractions.json"
    grouping_path = run_dir / "02_researcher" / "grouping.json"
    if not extractions_path.exists():
        raise FileNotFoundError(
            f"Researcher all_extractions.json not found at {extractions_path}. "
            f"Run the Researcher pipeline first."
        )
    if not grouping_path.exists():
        raise FileNotFoundError(
            f"Researcher grouping.json not found at {grouping_path}."
        )
    with open(extractions_path, encoding="utf-8") as f:
        all_extractions = json.load(f)
    with open(grouping_path, encoding="utf-8") as f:
        grouping = json.load(f)
    return all_extractions, grouping


def _load_provocateur_briefings(run_dir: Path) -> dict[str, list[dict[str, Any]]]:
    """Load all per-voice briefings from 03_provocateur/briefings/."""
    briefings_dir = run_dir / "03_provocateur" / "briefings"
    if not briefings_dir.exists():
        return {}
    out: dict[str, list[dict[str, Any]]] = {}
    for p in sorted(briefings_dir.glob("*.json")):
        slug = p.stem
        with open(p, encoding="utf-8") as f:
            briefing = json.load(f)
        out[slug] = briefing.get("formulations", [])
    return out


def _load_provocateur_formulations(run_dir: Path) -> dict[str, dict[str, Any]]:
    """Load per-pair formulation files (theme_id__voice_slug.json).

    These carry grounding_extraction_ids verbatim.
    """
    formulations_dir = run_dir / "03_provocateur" / "formulations"
    if not formulations_dir.exists():
        return {}
    out: dict[str, dict[str, Any]] = {}
    for p in sorted(formulations_dir.glob("*.json")):
        with open(p, encoding="utf-8") as f:
            out[p.stem] = json.load(f)
    return out


def _load_published_voices_for_night(
    project_root: Path, night: int
) -> dict[str, dict[str, Any]]:
    """Load all published per-voice files for one night."""
    night_dir = project_root / "published_artifacts" / "nights" / f"night_{night}"
    if not night_dir.exists():
        return {}
    out: dict[str, dict[str, Any]] = {}
    for p in sorted(night_dir.glob("*.json")):
        if p.name.startswith("_"):
            continue  # skip _index.json
        slug = p.stem
        with open(p, encoding="utf-8") as f:
            out[slug] = json.load(f)
    return out


# --- Per-theme builder -------------------------------------------------

def _normalize_theme_record(theme_obj: dict[str, Any]) -> dict[str, Any]:
    """Pull out theme metadata regardless of which Researcher schema vintage."""
    return {
        "theme_id": theme_obj.get("theme_id") or theme_obj.get("id"),
        "researcher_title": theme_obj.get("title", ""),
        "researcher_abstract": theme_obj.get("abstract", ""),
        "cluster_ids": theme_obj.get("cluster_ids", []),
    }


def _normalize_cluster_record(cluster_obj: dict[str, Any]) -> dict[str, Any]:
    return {
        "cluster_id": cluster_obj.get("cluster_id") or cluster_obj.get("id"),
        "title": cluster_obj.get("cluster_title") or cluster_obj.get("title", ""),
        "abstract": cluster_obj.get("cluster_abstract") or cluster_obj.get("abstract", ""),
        "extraction_ids": cluster_obj.get("extraction_ids", []),
    }


def _build_per_theme_files(
    run_dir: Path,
    night: int,
    project_root: Path,
    all_extractions: list[dict[str, Any]],
    grouping: dict[str, Any],
    briefings: dict[str, list[dict[str, Any]]],
    formulations: dict[str, dict[str, Any]],
    published_voices: dict[str, dict[str, Any]],
) -> list[str]:
    """Build per-theme files. Returns list of theme_ids written.

    Theme files are written under a per-night subdirectory:
    `published_artifacts/themes/night_<N>/<theme_id>.json`. Theme_ids
    are not stable across Researcher runs (each Researcher run emits
    fresh sequential IDs), so a flat `themes/<theme_id>.json` layout
    causes Night 2's theme_001 to overwrite Night 1's theme_001 — silent
    data loss across the Athens 3-night sequence. The per-night
    subdirectory disambiguates without requiring a wider ID-naming
    refactor. (Spec evolution noted in OPEN_ITEMS C3 + C9.)
    """
    logger = get_logger("publish_flow")
    out_dir = project_root / "published_artifacts" / "themes" / f"night_{night}"
    out_dir.mkdir(parents=True, exist_ok=True)

    extractions_by_id = {e["id"]: e for e in all_extractions}
    themes_written: list[str] = []

    # Index briefings → formulations per theme per voice (theme_display_title
    # + audience_friction etc. come from briefings).
    briefing_lookup: dict[tuple[str, str], dict[str, Any]] = {}
    for slug, formulation_list in briefings.items():
        for f in formulation_list:
            tid = f.get("theme_id")
            if tid:
                briefing_lookup[(tid, slug)] = f

    # Build amendment edges per theme — per-voice published files have
    # amendments[].cited_theme_id so we can index amendments by theme.
    amendments_by_theme: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for slug, pub in published_voices.items():
        for a in pub.get("deliberation", {}).get("amendments", []):
            tid = a.get("cited_theme_id")
            if tid:
                amendments_by_theme[tid].append({
                    "from_voice_slug": slug,
                    "from_voice_name": pub.get("voice_name", slug),
                    "from_url_path": pub.get("url_path", ""),
                    "to_voice_slug": a.get("cited_voice_slug", ""),
                    "to_voice_name": a.get("cited_voice_name", ""),
                    "to_url_path": a.get("cited_url_path", ""),
                    "amendment_type": a.get("amendment_type", ""),
                    "rationale": a.get("rationale", ""),
                })

    for theme in grouping.get("themes", []):
        meta = _normalize_theme_record(theme)
        theme_id = meta["theme_id"]
        if not theme_id:
            continue

        # Resolve clusters + their extractions.
        clusters_resolved = []
        all_extraction_ids: list[str] = []
        for cid in meta["cluster_ids"]:
            # Find the cluster in either grouping (newer schema embeds
            # clusters in themes) or top-level clusters.
            cluster_obj = None
            for c in theme.get("clusters", []):
                if c.get("cluster_id") == cid or c.get("id") == cid:
                    cluster_obj = c
                    break
            if cluster_obj is None:
                continue
            cluster_norm = _normalize_cluster_record(cluster_obj)
            clusters_resolved.append(cluster_norm)
            all_extraction_ids.extend(cluster_norm["extraction_ids"])

        # Resolve extraction objects in full.
        extractions_resolved = []
        for eid in all_extraction_ids:
            e = extractions_by_id.get(eid)
            if not e:
                continue
            extractions_resolved.append({
                "id": e["id"],
                "session_id": e.get("session_id") or (eid.split(":", 1)[0] if ":" in eid else ""),
                "speaker": e.get("speaker") or "",
                "lens": e.get("lens") or "",
                "text": e.get("extraction") or e.get("text") or "",
                "context": e.get("context") or "",
                "engagement": e.get("engagement"),
                "responds_to": e.get("responds_to"),
                "energy": e.get("energy") or "normal",
            })

        # Per-voice formulations on this theme (from briefings/formulations).
        formulations_per_voice = []
        for (tid, slug), entry in briefing_lookup.items():
            if tid != theme_id:
                continue
            voice_published = published_voices.get(slug)
            voice_name = voice_published.get("voice_name", slug) if voice_published else slug
            url_path = voice_published.get("url_path", "") if voice_published else f"/night-{night}/{slug}"
            formulations_per_voice.append({
                "voice_slug": slug,
                "voice_name": voice_name,
                "url_path": url_path,
                "formulation_text": entry.get("formulation_text", ""),
                "mode": entry.get("mode", "question"),
                "addressed_in_artifact": (
                    voice_published is not None
                    and theme_id in voice_published.get("themes_addressed", [])
                ),
            })

        # Pull editorial flags from the briefing's full_theme_record (any
        # voice's briefing for this theme has them — they're per-theme,
        # not per-voice).
        theme_flags: dict[str, Any] = {}
        for (tid, _slug), entry in briefing_lookup.items():
            if tid == theme_id:
                ftr = entry.get("full_theme_record", {})
                theme_flags = ftr.get("theme_flags", {}) or {}
                break

        # Display title: prefer Provocateur's display title from any
        # briefing for this theme; fall back to Researcher's.
        display_title = ""
        for (tid, _slug), entry in briefing_lookup.items():
            if tid == theme_id and entry.get("theme_display_title"):
                display_title = entry["theme_display_title"]
                break
        if not display_title:
            display_title = meta["researcher_title"]

        theme_record = {
            "theme_id": theme_id,
            "night": night,
            "display_title": display_title,
            "abstract": meta["researcher_abstract"],
            "researcher_title": meta["researcher_title"],
            "researcher_abstract": meta["researcher_abstract"],
            "audience_friction": theme_flags.get("audience_friction"),
            "fault_line_present": theme_flags.get("fault_line_present"),
            "fault_line_description": theme_flags.get("fault_line_description"),
            "clusters": clusters_resolved,
            "extractions": extractions_resolved,
            "extraction_count": len(extractions_resolved),
            "formulations_per_voice": formulations_per_voice,
            "voices_who_addressed": [
                {
                    "voice_slug": fpv["voice_slug"],
                    "voice_name": fpv["voice_name"],
                    "url_path": fpv["url_path"],
                    "addressed": fpv["addressed_in_artifact"],
                }
                for fpv in formulations_per_voice
            ],
            "amendments_on_this_theme": amendments_by_theme.get(theme_id, []),
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        }

        out_path = out_dir / f"{theme_id}.json"
        write_json_atomic(out_path, theme_record)
        themes_written.append(theme_id)

    logger.info(
        f"  Themes: {len(themes_written)} written to {out_dir.relative_to(project_root)}"
    )
    return themes_written


# --- Per-extraction reverse-index builder ------------------------------

def _build_per_extraction_files(
    run_dir: Path,
    night: int,
    project_root: Path,
    all_extractions: list[dict[str, Any]],
    grouping: dict[str, Any],
    briefings: dict[str, list[dict[str, Any]]],
    formulations: dict[str, dict[str, Any]],
    published_voices: dict[str, dict[str, Any]],
) -> list[str]:
    """Build per-extraction reverse-index files. Returns list of extraction_ids."""
    logger = get_logger("publish_flow")
    out_dir = project_root / "published_artifacts" / "extractions"
    out_dir.mkdir(parents=True, exist_ok=True)

    # extraction → clusters
    extraction_to_clusters: dict[str, list[str]] = defaultdict(list)
    # cluster → themes
    cluster_to_themes: dict[str, list[str]] = defaultdict(list)
    for theme in grouping.get("themes", []):
        tid = theme.get("theme_id") or theme.get("id")
        for c in theme.get("clusters", []):
            cid = c.get("cluster_id") or c.get("id")
            if cid and tid:
                cluster_to_themes[cid].append(tid)
            for eid in c.get("extraction_ids", []):
                if eid and cid:
                    extraction_to_clusters[eid].append(cid)

    # extraction → formulations grounded in it
    extraction_to_formulations: dict[str, list[dict[str, str]]] = defaultdict(list)
    for fid, f in formulations.items():
        for eid in f.get("grounding_extraction_ids", []):
            extraction_to_formulations[eid].append({
                "formulation_id": fid,
                "voice_slug": fid.split("__", 1)[1] if "__" in fid else "",
                "theme_id": fid.split("__", 1)[0] if "__" in fid else "",
            })

    extractions_written: list[str] = []
    for e in all_extractions:
        eid = e["id"]
        clusters = sorted(set(extraction_to_clusters.get(eid, [])))
        themes = sorted({tid for cid in clusters for tid in cluster_to_themes.get(cid, [])})
        grounded_formulations = extraction_to_formulations.get(eid, [])

        # Voices whose published artifacts address themes containing this extraction.
        addressed_in_artifacts = []
        for slug, pub in published_voices.items():
            voice_themes = set(pub.get("themes_addressed", []))
            if voice_themes & set(themes):
                addressed_in_artifacts.append({
                    "voice_slug": slug,
                    "voice_name": pub.get("voice_name", slug),
                    "url_path": pub.get("url_path", ""),
                    "themes_intersect": sorted(voice_themes & set(themes)),
                })

        # Resolve grounded_formulations to richer entries.
        grounded_resolved = []
        for gf in grounded_formulations:
            voice_slug = gf["voice_slug"]
            voice_name = (
                published_voices.get(voice_slug, {}).get("voice_name", voice_slug)
            )
            url_path = (
                published_voices.get(voice_slug, {}).get("url_path", f"/night-{night}/{voice_slug}")
            )
            grounded_resolved.append({
                "voice_slug": voice_slug,
                "voice_name": voice_name,
                "url_path": url_path,
                "theme_id": gf["theme_id"],
                "formulation_id": gf["formulation_id"],
            })

        record = {
            "extraction_id": eid,
            "night": night,
            "session_id": e.get("session_id") or (eid.split(":", 1)[0] if ":" in eid else ""),
            "speaker": e.get("speaker") or "",
            "lens": e.get("lens") or "",
            "text": e.get("extraction") or e.get("text") or "",
            "context": e.get("context") or "",
            "engagement": e.get("engagement"),
            "responds_to": e.get("responds_to"),
            "energy": e.get("energy") or "normal",
            "in_clusters": clusters,
            "in_themes": themes,
            "grounded_formulations": grounded_resolved,
            "addressed_in_artifacts": addressed_in_artifacts,
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        }
        out_path = out_dir / f"{_extraction_id_to_filename(eid)}.json"
        write_json_atomic(out_path, record)
        extractions_written.append(eid)

    logger.info(
        f"  Extractions: {len(extractions_written)} written to "
        f"{out_dir.relative_to(project_root)}"
    )
    return extractions_written


# --- Lineage graph builder ---------------------------------------------

def _build_lineage_graph(
    run_dir: Path,
    night: int,
    project_root: Path,
    all_extractions: list[dict[str, Any]],
    grouping: dict[str, Any],
    formulations: dict[str, dict[str, Any]],
    published_voices: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Build a per-night bidirectional lineage graph as a node + edge JSON.

    Node IDs:
      session:<session_id>
      extraction:<extraction_id>
      cluster:<cluster_id>
      theme:<theme_id>
      formulation:<formulation_id>
      detailed_response:<voice_slug>:<theme_id>
      first_draft:<voice_slug>
      amended_artifact:<voice_slug>

    Edge `rel` types:
      contains      session → extraction; cluster → extraction; theme → cluster
      grounded_in   formulation → extraction
      formulated_for theme → formulation
      engaged_by    formulation → detailed_response
      consumed_by   detailed_response → first_draft
      amended_by    first_draft → amended_artifact (1:1 per voice)
      cites         amended_artifact → amended_artifact (with amendment_type)
    """
    logger = get_logger("publish_flow")
    out_dir = project_root / "published_artifacts" / "traces"
    out_dir.mkdir(parents=True, exist_ok=True)

    nodes: dict[str, dict[str, Any]] = {}
    edges: list[dict[str, Any]] = []

    # Sessions + extractions.
    for e in all_extractions:
        eid = e["id"]
        sid = e.get("session_id") or (eid.split(":", 1)[0] if ":" in eid else "")
        nodes[f"extraction:{eid}"] = {
            "type": "extraction",
            "session_id": sid,
            "speaker": e.get("speaker") or "",
            "lens": e.get("lens") or "",
            "text_preview": (e.get("extraction") or e.get("text") or "")[:120],
        }
        if sid and f"session:{sid}" not in nodes:
            nodes[f"session:{sid}"] = {"type": "session", "session_id": sid}
        if sid:
            edges.append({
                "from": f"session:{sid}",
                "to": f"extraction:{eid}",
                "rel": "contains",
            })

    # Clusters + themes.
    for theme in grouping.get("themes", []):
        tid = theme.get("theme_id") or theme.get("id")
        if not tid:
            continue
        nodes[f"theme:{tid}"] = {
            "type": "theme",
            "title": theme.get("title", ""),
        }
        for c in theme.get("clusters", []):
            cid = c.get("cluster_id") or c.get("id")
            if not cid:
                continue
            nodes[f"cluster:{cid}"] = {
                "type": "cluster",
                "title": c.get("cluster_title") or c.get("title", ""),
                "theme_id": tid,
            }
            edges.append({
                "from": f"theme:{tid}",
                "to": f"cluster:{cid}",
                "rel": "contains",
            })
            for eid in c.get("extraction_ids", []):
                edges.append({
                    "from": f"cluster:{cid}",
                    "to": f"extraction:{eid}",
                    "rel": "contains",
                })

    # Formulations + grounded extractions.
    for fid, f in formulations.items():
        nodes[f"formulation:{fid}"] = {
            "type": "formulation",
            "voice_slug": f.get("member") and f["member"].lower().replace(" ", "_"),
            "theme_id": f.get("theme_id"),
            "mode": f.get("mode", "question"),
        }
        if f.get("theme_id"):
            edges.append({
                "from": f"theme:{f['theme_id']}",
                "to": f"formulation:{fid}",
                "rel": "formulated_for",
            })
        for eid in f.get("grounding_extraction_ids", []):
            edges.append({
                "from": f"formulation:{fid}",
                "to": f"extraction:{eid}",
                "rel": "grounded_in",
            })

    # Detailed responses + first-drafts + amended artifacts (per voice).
    # We read the detailed_response files directly to confirm presence;
    # the amended_artifact info comes from the published_voices dict.
    detailed_dir = run_dir / "04_voice" / "step1_detailed_responses"
    if detailed_dir.exists():
        for p in sorted(detailed_dir.glob("*.json")):
            base = p.stem  # "<voice_slug>__<theme_id>"
            if "__" not in base:
                continue
            voice_slug, theme_id = base.split("__", 1)
            dr_node = f"detailed_response:{voice_slug}:{theme_id}"
            nodes[dr_node] = {
                "type": "detailed_response",
                "voice_slug": voice_slug,
                "theme_id": theme_id,
            }
            # formulation_id = theme_id__voice_slug per Provocateur convention.
            fid = f"{theme_id}__{voice_slug}"
            edges.append({
                "from": f"formulation:{fid}",
                "to": dr_node,
                "rel": "engaged_by",
            })

    for slug, pub in published_voices.items():
        # Step 2 output exists alongside Step 3; we represent the
        # first_draft as a node even though we don't read its file
        # contents directly (the published_voice IS the amended one).
        first_draft_node = f"first_draft:{slug}"
        amended_node = f"amended_artifact:{slug}"
        nodes[first_draft_node] = {
            "type": "first_draft",
            "voice_slug": slug,
            "voice_name": pub.get("voice_name", slug),
            "night": night,
        }
        nodes[amended_node] = {
            "type": "amended_artifact",
            "voice_slug": slug,
            "voice_name": pub.get("voice_name", slug),
            "night": night,
            "title": pub.get("artifact", {}).get("title", ""),
            "decision": pub.get("deliberation", {}).get("decision", ""),
            "url_path": pub.get("url_path", ""),
        }
        # detailed_response → first_draft (consumed_by).
        for tid in pub.get("themes_addressed", []):
            dr_node = f"detailed_response:{slug}:{tid}"
            if dr_node in nodes:
                edges.append({
                    "from": dr_node,
                    "to": first_draft_node,
                    "rel": "consumed_by",
                })
        # first_draft → amended_artifact.
        edges.append({
            "from": first_draft_node,
            "to": amended_node,
            "rel": "amended_by",
        })
        # amended_artifact → amended_artifact (cites, with amendment_type).
        for a in pub.get("deliberation", {}).get("amendments", []):
            cited_slug = a.get("cited_voice_slug")
            if cited_slug:
                edges.append({
                    "from": amended_node,
                    "to": f"amended_artifact:{cited_slug}",
                    "rel": "cites",
                    "amendment_type": a.get("amendment_type", ""),
                    "cited_theme_id": a.get("cited_theme_id", ""),
                })

    graph = {
        "night": night,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "node_count": len(nodes),
        "edge_count": len(edges),
        "nodes": nodes,
        "edges": edges,
    }
    out_path = out_dir / f"lineage_graph_night_{night}.json"
    write_json_atomic(out_path, graph)
    logger.info(
        f"  Lineage graph: {len(nodes)} nodes, {len(edges)} edges → "
        f"{out_path.relative_to(project_root)}"
    )
    return {"node_count": len(nodes), "edge_count": len(edges), "path": str(out_path)}


# --- Per-voice multi-night index ---------------------------------------

def _build_per_voice_multi_night_index(
    project_root: Path,
) -> list[str]:
    """Walk all published_artifacts/nights/night_*/<slug>.json and aggregate
    per voice across whatever nights have published files at this point.

    Re-built each publish_flow run (additive: as more nights publish,
    the per-voice index grows). Idempotent.
    """
    logger = get_logger("publish_flow")
    nights_root = project_root / "published_artifacts" / "nights"
    voices_dir = project_root / "published_artifacts" / "voices"
    voices_dir.mkdir(parents=True, exist_ok=True)

    if not nights_root.exists():
        logger.warning(
            f"  Voices index: no nights/ directory at {nights_root}; skipping."
        )
        return []

    # Discover nights present.
    night_dirs = sorted(nights_root.glob("night_*"))
    by_voice: dict[str, dict[int, dict[str, Any]]] = defaultdict(dict)
    voice_names: dict[str, str] = {}
    for nd in night_dirs:
        m = re.match(r"night_(\d+)$", nd.name)
        if not m:
            continue
        night = int(m.group(1))
        for p in sorted(nd.glob("*.json")):
            if p.name.startswith("_"):
                continue
            slug = p.stem
            with open(p, encoding="utf-8") as f:
                pub = json.load(f)
            voice_names[slug] = pub.get("voice_name", slug)
            by_voice[slug][night] = pub

    voices_written: list[str] = []
    for slug, nights in by_voice.items():
        nights_present = sorted(nights)
        record = {
            "voice_name": voice_names.get(slug, slug),
            "voice_slug": slug,
            "nights_present": nights_present,
            "url_paths": {
                str(n): nights[n].get("url_path", f"/night-{n}/{slug}")
                for n in nights_present
            },
            "artifact_summaries": {
                str(n): {
                    "title": nights[n].get("artifact", {}).get("title", ""),
                    "subtitle": nights[n].get("artifact", {}).get("subtitle", ""),
                    "selected_form": nights[n].get("artifact", {}).get("selected_form", ""),
                    "stance": nights[n].get("artifact", {}).get("stance", ""),
                    "themes_addressed": nights[n].get("themes_addressed", []),
                    "decision": nights[n].get("deliberation", {}).get("decision", ""),
                    "word_count": nights[n].get("artifact", {}).get("word_count", 0),
                }
                for n in nights_present
            },
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        }
        out_path = voices_dir / f"{slug}.json"
        write_json_atomic(out_path, record)
        voices_written.append(slug)

    logger.info(
        f"  Voices multi-night index: {len(voices_written)} voices → "
        f"{voices_dir.relative_to(project_root)}"
    )
    return voices_written


# --- Main flow --------------------------------------------------------

def run_publish(
    run_dir: str | Path,
    night: int,
    project_root: Path | None = None,
    skip_themes: bool = False,
    skip_extractions: bool = False,
    skip_graph: bool = False,
    skip_voices: bool = False,
) -> dict[str, Any]:
    """Run the publish pipeline for one night."""
    logger = get_logger("publish_flow")
    run_dir = Path(run_dir)
    if project_root is None:
        project_root = resolve_project_root(None)

    # Defensive: refuse to run if --night doesn't match run_dir's embedded
    # night number. Same guard as voice_flow — protects per-night published
    # paths (themes/night_<N>/, traces/lineage_graph_night_<N>.json) from
    # being written under the wrong night.
    from flows.shared.io import assert_run_dir_night_matches
    assert_run_dir_night_matches(run_dir, night)

    logger.info(f"Publish Pipeline: run_dir={run_dir}, night={night}")
    t_start = time.time()

    all_extractions, grouping = _load_researcher_outputs(run_dir)
    briefings = _load_provocateur_briefings(run_dir)
    formulations = _load_provocateur_formulations(run_dir)
    published_voices = _load_published_voices_for_night(project_root, night)

    if not published_voices:
        logger.warning(
            f"  No published voice files for night {night} at "
            f"{project_root / 'published_artifacts' / 'nights' / f'night_{night}'}. "
            f"Run voice_flow first (publish step is integrated)."
        )

    summary: dict[str, Any] = {
        "night": night,
        "run_id": run_dir.name,
        "voices_in_publish": len(published_voices),
        "extractions_in_run": len(all_extractions),
        "themes_in_run": len(grouping.get("themes", [])),
    }

    if not skip_themes:
        summary["themes_written"] = _build_per_theme_files(
            run_dir, night, project_root,
            all_extractions, grouping, briefings, formulations, published_voices,
        )
    if not skip_extractions:
        summary["extractions_written"] = _build_per_extraction_files(
            run_dir, night, project_root,
            all_extractions, grouping, briefings, formulations, published_voices,
        )
    if not skip_graph:
        summary["lineage_graph"] = _build_lineage_graph(
            run_dir, night, project_root,
            all_extractions, grouping, formulations, published_voices,
        )
    if not skip_voices:
        summary["per_voice_multi_night_index"] = _build_per_voice_multi_night_index(
            project_root
        )

    summary["wall_clock_s"] = round(time.time() - t_start, 2)

    # Write a publish-run manifest under traces/.
    manifest_path = (
        project_root / "published_artifacts" / "traces" / f"publish_manifest_night_{night}.json"
    )
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    write_json_atomic(manifest_path, summary)
    logger.info(
        f"Publish complete: night={night}, wall={summary['wall_clock_s']}s. "
        f"Manifest: {manifest_path.relative_to(project_root)}"
    )
    return summary


# --- CLI --------------------------------------------------------------

def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Publish Pipeline — cross-pipeline aggregation for the publish layer."
    )
    p.add_argument("run_dir", help="Run directory containing 02_researcher/ + 03_provocateur/ + 04_voice/")
    p.add_argument("--night", type=int, required=True, choices=[1, 2, 3])
    p.add_argument("--skip-themes", action="store_true")
    p.add_argument("--skip-extractions", action="store_true")
    p.add_argument("--skip-graph", action="store_true")
    p.add_argument("--skip-voices", action="store_true")
    add_project_arg(p)
    return p.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    project_root = resolve_project_root(args.project)
    run_publish(
        run_dir=args.run_dir,
        night=args.night,
        project_root=project_root,
        skip_themes=args.skip_themes,
        skip_extractions=args.skip_extractions,
        skip_graph=args.skip_graph,
        skip_voices=args.skip_voices,
    )
