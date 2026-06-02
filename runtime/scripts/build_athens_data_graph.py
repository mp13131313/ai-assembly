"""Build a unified data graph of the Athens 2026 pipeline.

Walks projects/athens-2026/runs/athens_night_{1,2,3}/ and
projects/athens-2026/published_artifacts/ and assembles a single nested
JSON capturing every entity + every field at every pipeline stage:

  Session (transcripts)
    → Extraction (positions)
      → Cluster (KJ-grouped extractions)
        → Theme (cluster-of-clusters)
          → Selection (which themes survived for Provocateur)
            → Formulation (per voice per kept theme)
              → Voice Step 1 (private reasoning per formulation)
                → Voice Step 2 (per-voice synthesis)
                  → Dossier (Tim's per-theme composition)
                    → per-voice published page

Plus: per-night manifest, deployment_context discipline rules,
operator_decisions, validation verdicts (full flag detail), token
+ cost metadata at every LLM stage, voice continuity blocks
across nights.

Outputs:
  - projects/athens-2026/published_artifacts/data_views/athens_data_graph.json
  - projects/athens-2026/published_artifacts/data_views/view_by_theme.html
  - projects/athens-2026/published_artifacts/data_views/README.md
"""
from __future__ import annotations
import json
import os
import sys
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(os.environ.get(
    "AI_ASSEMBLY_PROJECT_ROOT",
    "/Users/aienvironment/Desktop/AI Assembly/projects/athens-2026",
))
OUTPUT_DIR = PROJECT_ROOT / "published_artifacts" / "data_views"
NIGHTS = ["night_1", "night_2", "night_3"]


def load_json(path: Path) -> dict | list | None:
    if not path.exists():
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_text(path: Path) -> str | None:
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def extract_sessions(run_dir: Path, night: str, graph: dict) -> None:
    """Walk 01_transcription/<session_id>/session_package.json — capture every field."""
    trans_dir = run_dir / "01_transcription"
    if not trans_dir.exists():
        return
    for session_subdir in sorted(trans_dir.iterdir()):
        if not session_subdir.is_dir():
            continue
        pkg_path = session_subdir / "session_package.json"
        if not pkg_path.exists():
            continue
        pkg = load_json(pkg_path)
        if not pkg:
            continue
        meta = pkg.get("metadata", {})
        session_id = meta.get("session_id") or session_subdir.name
        transcript = pkg.get("transcript", {})
        if isinstance(transcript, dict):
            turns = transcript.get("turns", [])
            speakers_present = transcript.get("speakers_present", [])
        else:
            turns = transcript if isinstance(transcript, list) else []
            speakers_present = []
        graph["sessions"][session_id] = {
            "session_id": session_id,
            "night": night,
            "session_title": meta.get("session_title") or meta.get("title"),
            "session_description": meta.get("session_description") or meta.get("description"),
            "session_format": meta.get("session_format"),
            "track": meta.get("track"),
            "date_time": meta.get("date_time") or meta.get("start_time"),
            "venue": meta.get("venue"),
            "venue_sub": meta.get("venue_sub"),
            "source": meta.get("source") or meta.get("audio_source"),
            "is_reflection": meta.get("source") == "vendor" or "_reflection_source" in meta,
            "_reflection_source": meta.get("_reflection_source"),
            "_vendor_internal_session_id": meta.get("_vendor_internal_session_id"),
            "_collected_at": meta.get("_collected_at"),
            "ai_assembly_meta": meta.get("ai_assembly"),
            "roster": meta.get("roster", []),
            "speakers_present": speakers_present,
            "turns": turns,
            "turn_count": len(turns),
            "word_count": sum(len(t.get("text", "").split()) for t in turns if isinstance(t, dict)),
            "review_queue": pkg.get("review_queue"),
            "_extra_metadata_fields": {
                k: v for k, v in meta.items() if k not in {
                    "session_id", "session_title", "title", "session_description", "description",
                    "session_format", "track", "date_time", "start_time", "venue", "venue_sub",
                    "source", "audio_source", "_reflection_source", "_vendor_internal_session_id",
                    "_collected_at", "ai_assembly", "roster",
                }
            },
        }


def extract_researcher(run_dir: Path, night: str, graph: dict) -> None:
    """Walk 02_researcher/{all_extractions, clusters, grouping}.json."""
    rs = run_dir / "02_researcher"
    if not rs.exists():
        return

    # Extractions
    extractions = load_json(rs / "all_extractions.json") or []
    for ext in extractions:
        ext_id = ext.get("id")
        if not ext_id:
            continue
        # Session-id is the prefix before the colon in the extraction id
        session_id = ext_id.split(":")[0] if ":" in ext_id else None
        graph["extractions"][ext_id] = {
            "extraction_id": ext_id,
            "night": night,
            "session_id": session_id,
            "session_title": ext.get("session"),  # this is the title; session_id resolves to it
            "speaker": ext.get("speaker"),
            "lens": ext.get("lens"),
            "extraction": ext.get("extraction"),
            "context": ext.get("context"),
            "engagement": ext.get("engagement"),
            "responds_to": ext.get("responds_to"),
            "energy": ext.get("energy"),
            "cluster_id": None,  # backref filled later
            "_extra": {k: v for k, v in ext.items() if k not in {
                "id", "session", "speaker", "lens", "extraction",
                "context", "engagement", "responds_to", "energy",
            }},
        }

    # Clusters
    clusters_doc = load_json(rs / "clusters.json") or {}
    for cl in clusters_doc.get("clusters", []):
        cl_id = cl.get("cluster_id")
        if not cl_id:
            continue
        # Prefix with night so cluster_001 across nights doesn't collide
        prefixed = f"{night}/{cl_id}"
        graph["clusters"][prefixed] = {
            "cluster_id": cl_id,
            "prefixed_id": prefixed,
            "night": night,
            "cluster_title": cl.get("cluster_title"),
            "cluster_abstract": cl.get("cluster_abstract"),
            "extraction_ids": cl.get("extraction_ids", []),
            "theme_id": None,  # backref filled later
            "_extra": {k: v for k, v in cl.items() if k not in {
                "cluster_id", "cluster_title", "cluster_abstract", "extraction_ids",
            }},
        }
        # backref into extractions
        for eid in cl.get("extraction_ids", []):
            if eid in graph["extractions"]:
                graph["extractions"][eid]["cluster_id"] = prefixed

    # Themes (grouping.json inlines clusters; we already have them in graph["clusters"])
    grouping = load_json(rs / "grouping.json") or {}
    for th in grouping.get("themes", []):
        th_id = th.get("theme_id")
        if not th_id:
            continue
        prefixed = f"{night}/{th_id}"
        cluster_ids_under_theme = [c.get("cluster_id") for c in th.get("clusters", [])]
        graph["themes"][prefixed] = {
            "theme_id": th_id,
            "prefixed_id": prefixed,
            "night": night,
            "title": th.get("title"),
            "abstract": th.get("abstract"),
            "cluster_ids": [f"{night}/{cid}" for cid in cluster_ids_under_theme if cid],
            "selected_for_provocateur": False,  # filled by extract_provocateur_selection
            "fault_lines": None,  # filled if triage_flags available
            "_extra": {k: v for k, v in th.items() if k not in {
                "theme_id", "title", "abstract", "clusters",
            }},
        }
        for cid in cluster_ids_under_theme:
            cl_pref = f"{night}/{cid}"
            if cl_pref in graph["clusters"]:
                graph["clusters"][cl_pref]["theme_id"] = prefixed

    # Cluster isolates (no theme)
    graph["nights"][night]["cluster_isolates"] = clusters_doc.get("isolates", [])
    graph["nights"][night]["theme_isolates"] = grouping.get("isolates", [])


def extract_provocateur(run_dir: Path, night: str, graph: dict) -> None:
    """Walk 03_provocateur/{briefings, selection, triage_*, manifest}."""
    pv = run_dir / "03_provocateur"
    if not pv.exists():
        return

    # Selection: which themes were kept, how voices were assigned
    selection = load_json(pv / "selection.json") or {}
    for kt in selection.get("kept_themes", []):
        # kept_themes might be a list of theme_ids OR list of dicts
        if isinstance(kt, dict):
            th_id = kt.get("theme_id")
            note = kt
        else:
            th_id = kt
            note = None
        prefixed = f"{night}/{th_id}"
        if prefixed in graph["themes"]:
            graph["themes"][prefixed]["selected_for_provocateur"] = True
            if note is not None:
                graph["themes"][prefixed]["selection_note"] = note
    for dt in selection.get("dropped_themes", []):
        if isinstance(dt, dict):
            th_id = dt.get("theme_id")
            note = dt
        else:
            th_id = dt
            note = None
        prefixed = f"{night}/{th_id}"
        if prefixed in graph["themes"]:
            graph["themes"][prefixed]["selected_for_provocateur"] = False
            if note is not None:
                graph["themes"][prefixed]["drop_note"] = note

    graph["nights"][night]["selection"] = {
        "assignments_by_member": selection.get("assignments_by_member"),
        "kept_themes": selection.get("kept_themes"),
        "dropped_themes": selection.get("dropped_themes"),
        "coverage_per_member": selection.get("coverage_per_member"),
        "forced_fits": selection.get("forced_fits"),
        "stretch_swaps": selection.get("stretch_swaps"),
        "below_target": selection.get("below_target"),
        "prior_exclusions_applied": selection.get("prior_exclusions_applied"),
        "prior_exclusions_blocked": selection.get("prior_exclusions_blocked"),
        "prior_nights_consumed": selection.get("prior_nights_consumed"),
        "selection_parameters_used": selection.get("selection_parameters_used"),
    }

    # Triage flags (fault_lines, audience_friction per theme)
    flags = load_json(pv / "triage_flags.json") or {}
    for tf in flags.get("theme_flags", []):
        th_id = tf.get("theme_id")
        prefixed = f"{night}/{th_id}"
        if prefixed in graph["themes"]:
            graph["themes"][prefixed]["triage_flags"] = tf
    graph["nights"][night]["triage_flags_call"] = {
        k: v for k, v in flags.items() if k != "theme_flags"
    }

    # Triage voices (per-voice ranked themes + activation)
    tv_dir = pv / "triage_voices"
    if tv_dir.exists():
        per_voice = {}
        for vf in sorted(tv_dir.glob("*.json")):
            voice_slug = vf.stem
            per_voice[voice_slug] = load_json(vf)
        graph["nights"][night]["triage_voices"] = per_voice

    # Briefings → formulations
    briefings_dir = pv / "briefings"
    if briefings_dir.exists():
        for bf in sorted(briefings_dir.glob("*.json")):
            voice_slug = bf.stem
            briefing = load_json(bf) or {}
            for fm in briefing.get("formulations", []):
                th_id = fm.get("theme_id")
                if not th_id:
                    continue
                form_id = f"{night}/{th_id}__{voice_slug}"
                graph["formulations"][form_id] = {
                    "formulation_id": form_id,
                    "night": night,
                    "voice_slug": voice_slug,
                    "theme_id": f"{night}/{th_id}",
                    "theme_id_raw": th_id,
                    "theme_display_title": fm.get("theme_display_title"),
                    "mode": fm.get("mode"),
                    "formulation_text": fm.get("formulation_text"),
                    "context_narrative": fm.get("context_narrative"),
                    "selected_quotes": fm.get("selected_quotes", []),
                    "narrative_briefing": fm.get("narrative_briefing"),
                    "full_theme_record": fm.get("full_theme_record"),
                    "_extra": {k: v for k, v in fm.items() if k not in {
                        "theme_id", "theme_display_title", "mode", "formulation_text",
                        "context_narrative", "selected_quotes", "narrative_briefing",
                        "full_theme_record",
                    }},
                }

    # Provocateur manifest
    graph["nights"][night]["provocateur_manifest"] = load_json(pv / "manifest.json")


def extract_voice_step1(run_dir: Path, night: str, graph: dict) -> None:
    """Walk 04_voice/step1_detailed_responses/<voice>__<theme_id>.json."""
    s1_dir = run_dir / "04_voice" / "step1_detailed_responses"
    if not s1_dir.exists():
        return
    for s1f in sorted(s1_dir.glob("*.json")):
        d = load_json(s1f) or {}
        lineage = d.get("lineage", {})
        voice_slug = lineage.get("voice_slug")
        theme_id_raw = lineage.get("theme_id")
        if not voice_slug or not theme_id_raw:
            # fall back to filename parse: voice__theme_NNN
            stem = s1f.stem
            if "__theme_" in stem:
                voice_slug, theme_part = stem.split("__theme_", 1)
                theme_id_raw = "theme_" + theme_part
            else:
                continue
        s1_id = f"{night}/{voice_slug}__{theme_id_raw}"
        graph["voice_step1"][s1_id] = {
            "step1_id": s1_id,
            "night": night,
            "voice_slug": voice_slug,
            "theme_id": f"{night}/{theme_id_raw}",
            "theme_id_raw": theme_id_raw,
            "formulation_id": f"{night}/{theme_id_raw}__{voice_slug}",
            "lineage": lineage,
            "council_member": d.get("council_member"),
            "theme_display_title": d.get("theme_display_title"),
            "formulation_text": d.get("formulation_text"),
            "mode": d.get("mode"),
            "detailed_response": d.get("detailed_response"),
            "extractions_engaged": d.get("extractions_engaged", []),
            "thinking_trace": d.get("thinking_trace"),
            "model": d.get("model"),
            "thinking_enabled": d.get("thinking_enabled"),
            "input_tokens": d.get("input_tokens"),
            "output_tokens": d.get("output_tokens"),
            "thinking_tokens": d.get("thinking_tokens"),
            "cache_creation_input_tokens": d.get("cache_creation_input_tokens"),
            "cache_read_input_tokens": d.get("cache_read_input_tokens"),
            "wall_clock_s": d.get("wall_clock_s"),
            "_extra": {k: v for k, v in d.items() if k not in {
                "lineage", "council_member", "theme_display_title", "formulation_text",
                "mode", "detailed_response", "extractions_engaged", "thinking_trace",
                "model", "thinking_enabled", "input_tokens", "output_tokens",
                "thinking_tokens", "cache_creation_input_tokens", "cache_read_input_tokens",
                "wall_clock_s",
            }},
        }


def extract_voice_step2(run_dir: Path, night: str, graph: dict) -> None:
    """Walk 04_voice/step2_first_draft_artifacts/<voice>.json + validation + decisions."""
    s2_dir = run_dir / "04_voice" / "step2_first_draft_artifacts"
    if not s2_dir.exists():
        return
    val_dir = run_dir / "04_voice" / "step2_validation"
    op_dir = run_dir / "04_voice" / "operator_decisions"

    for s2f in sorted(s2_dir.glob("*.json")):
        voice_slug = s2f.stem
        d = load_json(s2f) or {}
        s2_id = f"{night}/{voice_slug}"
        graph["voice_step2"][s2_id] = {
            "step2_id": s2_id,
            "night": night,
            "voice_slug": voice_slug,
            "lineage": d.get("lineage"),
            "council_member": d.get("council_member"),
            "weight_assessment": d.get("weight_assessment"),
            "focus_decision": d.get("focus_decision"),
            "focus_rationale": d.get("focus_rationale"),
            "stance": d.get("stance"),
            "stance_rationale": d.get("stance_rationale"),
            "selected_form": d.get("selected_form"),
            "form_rationale": d.get("form_rationale"),
            "artifact_title": d.get("artifact_title"),
            "artifact_subtitle": d.get("artifact_subtitle"),
            "artifact_text": d.get("artifact_text"),
            "thinking_trace": d.get("thinking_trace"),
            "word_count": d.get("word_count"),
            "model": d.get("model"),
            "thinking_enabled": d.get("thinking_enabled"),
            "input_tokens": d.get("input_tokens"),
            "output_tokens": d.get("output_tokens"),
            "thinking_tokens": d.get("thinking_tokens"),
            "cache_creation_input_tokens": d.get("cache_creation_input_tokens"),
            "cache_read_input_tokens": d.get("cache_read_input_tokens"),
            "wall_clock_s": d.get("wall_clock_s"),
            "validation": None,  # filled below
            "operator_decision": None,  # filled below
            "_extra": {k: v for k, v in d.items() if k not in {
                "lineage", "council_member", "weight_assessment", "focus_decision",
                "focus_rationale", "stance", "stance_rationale", "selected_form",
                "form_rationale", "artifact_title", "artifact_subtitle", "artifact_text",
                "thinking_trace", "word_count", "model", "thinking_enabled",
                "input_tokens", "output_tokens", "thinking_tokens",
                "cache_creation_input_tokens", "cache_read_input_tokens", "wall_clock_s",
            }},
        }
        # Validation overlay
        vf = val_dir / f"{voice_slug}.json"
        if vf.exists():
            graph["voice_step2"][s2_id]["validation"] = load_json(vf)
        # Operator decision overlay
        opf = op_dir / f"{voice_slug}.json"
        if opf.exists():
            graph["voice_step2"][s2_id]["operator_decision"] = load_json(opf)


def extract_voice_step1_validation(run_dir: Path, night: str, graph: dict) -> None:
    """Walk 04_voice/validation/<voice>__<theme>.json (Step 1 validation, if present)."""
    val_dir = run_dir / "04_voice" / "validation"
    if not val_dir.exists():
        return
    for vf in sorted(val_dir.glob("*.json")):
        stem = vf.stem
        if "__theme_" not in stem:
            continue
        voice_slug, theme_part = stem.split("__theme_", 1)
        theme_id_raw = "theme_" + theme_part
        s1_id = f"{night}/{voice_slug}__{theme_id_raw}"
        if s1_id in graph["voice_step1"]:
            graph["voice_step1"][s1_id]["step1_validation"] = load_json(vf)


def extract_voice_manifest(run_dir: Path, night: str, graph: dict) -> None:
    manifest = load_json(run_dir / "04_voice" / "manifest.json")
    graph["nights"][night]["voice_manifest"] = manifest
    themes_to_voices = load_json(run_dir / "04_voice" / f"themes_to_voices_night_{night.split('_')[-1]}.json")
    if themes_to_voices:
        graph["nights"][night]["themes_to_voices"] = themes_to_voices


def extract_dossiers(night: str, graph: dict) -> None:
    """Walk published_artifacts/dossiers/night_N/dossier_NNN.json."""
    d_dir = PROJECT_ROOT / "published_artifacts" / "dossiers" / night
    if not d_dir.exists():
        return
    index = load_json(d_dir / "_index.json")
    if index:
        graph["nights"][night]["dossiers_index"] = index
    for df in sorted(d_dir.glob("dossier_*.json")):
        d = load_json(df) or {}
        dossier_num = df.stem
        meta = d.get("metadata", {})
        theme_id_raw = meta.get("theme_id")
        prefixed_theme = f"{night}/{theme_id_raw}" if theme_id_raw else None
        dossier_id = f"{night}/{dossier_num}"
        # Identify voices featured by scanning headnotes for voice mentions
        voices_featured = []
        for hn in d.get("headnotes", []):
            if isinstance(hn, dict):
                vs = hn.get("voice_slug") or hn.get("voice")
                if vs:
                    voices_featured.append(vs)
        graph["dossiers"][dossier_id] = {
            "dossier_id": dossier_id,
            "dossier_num": dossier_num,
            "night": night,
            "theme_id": prefixed_theme,
            "theme_id_raw": theme_id_raw,
            "theme_display_title": meta.get("theme_display_title"),
            "schema_version": d.get("schema_version"),
            "kicker": d.get("kicker"),
            "headline": d.get("headline"),
            "front_abstract": d.get("front_abstract"),
            "subline": d.get("subline"),
            "pull_quote": d.get("pull_quote"),
            "body_paragraphs": d.get("body_paragraphs", []),
            "theme_title_for_dossier": d.get("theme_title_for_dossier"),
            "theme_abstract_for_dossier": d.get("theme_abstract_for_dossier"),
            "headnotes": d.get("headnotes", []),
            "voices_featured": voices_featured or None,
            "panel_speakers": d.get("panel_speakers", []),
            "thinking_trace": d.get("thinking_trace"),
            "colophon": d.get("colophon"),
            "metadata": meta,
            "_extra": {k: v for k, v in d.items() if k not in {
                "schema_version", "kicker", "headline", "front_abstract", "subline",
                "pull_quote", "body_paragraphs", "theme_title_for_dossier",
                "theme_abstract_for_dossier", "headnotes", "panel_speakers",
                "thinking_trace", "colophon", "metadata",
            }},
        }


def extract_published_voice_pages(night: str, graph: dict) -> None:
    """Walk published_artifacts/nights/night_N/<voice>.json."""
    n_dir = PROJECT_ROOT / "published_artifacts" / "nights" / night
    if not n_dir.exists():
        return
    index = load_json(n_dir / "_index.json")
    if index:
        graph["nights"][night]["voices_index"] = index
    pages = {}
    for vf in sorted(n_dir.glob("*.json")):
        if vf.stem.startswith("_"):
            continue
        pages[vf.stem] = load_json(vf)
    graph["nights"][night]["published_voice_pages"] = pages


def extract_continuity(night: str, graph: dict) -> None:
    """Walk voices/<slug>/continuity_night_N.json (gitignored on disk)."""
    # Continuity for night N is GENERATED at end of night N-1 and CONSUMED at start of night N
    # So continuity_night_2.json is the bridge from Night 1 → Night 2
    # File is in voices/<slug>/ at PROJECT_ROOT
    n = int(night.split("_")[-1])
    if n == 1:
        return  # no incoming continuity for night 1
    continuity_filename = f"continuity_night_{n}.json"
    voices_dir = PROJECT_ROOT / "voices"
    if not voices_dir.exists():
        return
    for voice_dir in sorted(voices_dir.iterdir()):
        if not voice_dir.is_dir():
            continue
        voice_slug = voice_dir.name
        cf = voice_dir / continuity_filename
        if not cf.exists():
            continue
        s2_id = f"{night}/{voice_slug}"
        if s2_id in graph["voice_step2"]:
            graph["voice_step2"][s2_id]["continuity_from_prior_night"] = load_json(cf)


def extract_deployment_context(run_dir: Path, night: str, graph: dict) -> None:
    """Read _dossier_deployment_context.md if present."""
    dc_path = run_dir / "_dossier_deployment_context.md"
    text = load_text(dc_path)
    if text:
        graph["nights"][night]["deployment_context_rules"] = text


def compute_statistics(graph: dict) -> None:
    """Per-night counts."""
    for night in NIGHTS:
        if night not in graph["nights"]:
            graph["nights"][night] = {}
        sessions = [s for sid, s in graph["sessions"].items() if s["night"] == night]
        extractions = [e for eid, e in graph["extractions"].items() if e["night"] == night]
        clusters = [c for cid, c in graph["clusters"].items() if c["night"] == night]
        themes = [t for tid, t in graph["themes"].items() if t["night"] == night]
        formulations = [f for fid, f in graph["formulations"].items() if f["night"] == night]
        step1 = [s for sid, s in graph["voice_step1"].items() if s["night"] == night]
        step2 = [s for sid, s in graph["voice_step2"].items() if s["night"] == night]
        dossiers = [d for did, d in graph["dossiers"].items() if d["night"] == night]
        graph["nights"][night]["statistics"] = {
            "sessions": len(sessions),
            "turns": sum(s.get("turn_count", 0) for s in sessions),
            "words": sum(s.get("word_count", 0) for s in sessions),
            "extractions": len(extractions),
            "clusters": len(clusters),
            "themes_total": len(themes),
            "themes_selected": sum(1 for t in themes if t.get("selected_for_provocateur")),
            "formulations": len(formulations),
            "voice_step1": len(step1),
            "voice_step2": len(step2),
            "dossiers": len(dossiers),
        }


def build_graph() -> dict:
    graph = {
        "metadata": {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "project": "athens-2026",
            "schema_version": "1.0.0",
            "source_run_dirs": [f"runs/athens_{n}" for n in NIGHTS],
            "nights_included": NIGHTS,
            "extraction_script": "code/runtime/scripts/build_athens_data_graph.py",
        },
        "nights": {n: {} for n in NIGHTS},
        "sessions": {},
        "extractions": {},
        "clusters": {},
        "themes": {},
        "formulations": {},
        "voice_step1": {},
        "voice_step2": {},
        "dossiers": {},
    }
    for night in NIGHTS:
        run_dir = PROJECT_ROOT / "runs" / f"athens_{night}"
        if not run_dir.exists():
            print(f"⚠️ skipping {night} — run dir missing")
            continue
        print(f"  {night} ...")
        extract_deployment_context(run_dir, night, graph)
        extract_sessions(run_dir, night, graph)
        extract_researcher(run_dir, night, graph)
        extract_provocateur(run_dir, night, graph)
        extract_voice_step1(run_dir, night, graph)
        extract_voice_step1_validation(run_dir, night, graph)
        extract_voice_step2(run_dir, night, graph)
        extract_voice_manifest(run_dir, night, graph)
        extract_continuity(night, graph)
        extract_dossiers(night, graph)
        extract_published_voice_pages(night, graph)
    compute_statistics(graph)
    # Totals
    graph["metadata"]["total_nodes"] = (
        len(graph["sessions"]) + len(graph["extractions"]) + len(graph["clusters"])
        + len(graph["themes"]) + len(graph["formulations"]) + len(graph["voice_step1"])
        + len(graph["voice_step2"]) + len(graph["dossiers"])
    )
    graph["metadata"]["nodes_per_kind"] = {
        "sessions": len(graph["sessions"]),
        "extractions": len(graph["extractions"]),
        "clusters": len(graph["clusters"]),
        "themes": len(graph["themes"]),
        "formulations": len(graph["formulations"]),
        "voice_step1": len(graph["voice_step1"]),
        "voice_step2": len(graph["voice_step2"]),
        "dossiers": len(graph["dossiers"]),
    }
    return graph


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Athens 2026 — Data Graph</title>
<style>
  :root {
    --bg: #fafaf7; --fg: #1a1a1a; --muted: #6a6a6a;
    --border: #d8d4cc; --accent: #5a3a8a; --accent-bg: #ece5f5;
    --card: #ffffff; --highlight: #fff4d4;
    --mono: "SF Mono", "Monaco", "Inconsolata", monospace;
    --serif: "Cormorant Garamond", "Iowan Old Style", Georgia, serif;
  }
  * { box-sizing: border-box; }
  body { margin: 0; padding: 0; background: var(--bg); color: var(--fg);
         font: 16px/1.55 -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif; }
  header { background: #1a1a1a; color: #fafaf7; padding: 1rem 2rem;
           display: flex; align-items: baseline; gap: 2rem; flex-wrap: wrap;
           position: sticky; top: 0; z-index: 100; }
  header h1 { margin: 0; font: italic 600 1.5rem var(--serif); }
  header .subtitle { color: #aaa; font-size: 0.9rem; }
  nav.tabs { background: #2a2a2a; padding: 0 2rem; display: flex; gap: 0;
             position: sticky; top: 0; z-index: 99; }
  nav.tabs button { background: transparent; border: 0; color: #aaa;
                    padding: 0.75rem 1.5rem; font: inherit; cursor: pointer;
                    border-bottom: 3px solid transparent; }
  nav.tabs button:hover { color: #fff; }
  nav.tabs button.active { color: #fff; border-bottom-color: var(--accent); }
  nav.tabs .spacer { flex: 1; }
  nav.tabs .voices-index { color: #aaa; padding: 0.75rem 1rem; cursor: pointer;
                           position: relative; }
  nav.tabs .voices-index:hover { color: #fff; }
  .voices-index .menu { display: none; position: absolute; top: 100%; right: 0;
                        background: #2a2a2a; border: 1px solid #444; min-width: 280px;
                        padding: 0.5rem; z-index: 200; }
  .voices-index:hover .menu { display: block; }
  .voices-index .menu a { display: block; color: #ddd; padding: 0.25rem 0.5rem;
                          text-decoration: none; font-size: 0.85rem; }
  .voices-index .menu a:hover { background: #444; color: #fff; }
  main { padding: 1.5rem 2rem; max-width: 1100px; margin: 0 auto; }
  .stats { background: var(--card); border: 1px solid var(--border);
           padding: 0.75rem 1rem; margin-bottom: 1.5rem; font-size: 0.85rem;
           font-family: var(--mono); color: var(--muted); }
  .stats b { color: var(--fg); }
  .section-title { font: italic 600 1.6rem var(--serif); margin: 1.5rem 0 0.75rem;
                   border-bottom: 1px solid var(--border); padding-bottom: 0.25rem; }
  details { background: var(--card); border: 1px solid var(--border); margin: 0.5rem 0;
            border-radius: 4px; }
  details > summary { cursor: pointer; padding: 0.5rem 0.75rem; font-weight: 500;
                      user-select: none; }
  details > summary:hover { background: #f5f1e8; }
  details > .body { padding: 0.5rem 0.75rem 0.75rem; border-top: 1px solid var(--border); }
  details details { margin-left: 1rem; }
  .id { font-family: var(--mono); font-size: 0.75rem; color: var(--muted); }
  .abstract { background: #f5f1e8; padding: 0.5rem 0.75rem; margin: 0.5rem 0;
              border-left: 3px solid var(--accent); font-size: 0.92rem; }
  .meta { font-size: 0.82rem; color: var(--muted); margin: 0.25rem 0; }
  .meta-grid { display: grid; grid-template-columns: max-content 1fr;
               gap: 0.25rem 0.75rem; font-size: 0.82rem; color: var(--muted);
               margin: 0.5rem 0; }
  .meta-grid b { color: var(--fg); }
  .thinking-trace { background: #fef9e7; border: 1px solid #f0e0a0;
                    padding: 0.5rem; font-family: var(--mono); font-size: 0.75rem;
                    white-space: pre-wrap; max-height: 400px; overflow-y: auto;
                    color: #5a4a1a; }
  .artifact-text, .response-text, .body-paragraphs, .formulation-text, .narrative-briefing,
  .deployment-context, .continuity-block, .extraction-content {
    white-space: pre-wrap; font: 16px/1.6 var(--serif); margin: 0.5rem 0;
    background: #fff; padding: 0.75rem; border-left: 3px solid var(--accent);
  }
  .turn-text { font-size: 0.85rem; color: #333; padding: 0.25rem 0.5rem;
               border-left: 2px solid #ddd; margin: 0.25rem 0; }
  .turn-meta { font-size: 0.72rem; color: var(--muted); font-family: var(--mono); }
  .label { display: inline-block; background: var(--accent-bg); color: var(--accent);
           padding: 1px 6px; font-size: 0.7rem; font-family: var(--mono);
           border-radius: 3px; margin-right: 0.25rem; vertical-align: middle; }
  .label.pass { background: #d4f0d4; color: #2a6a2a; }
  .label.warn { background: #fdebcb; color: #8a5a1a; }
  .label.hold { background: #f9d6d6; color: #8a2a2a; }
  .label.released { background: #d4f0d4; color: #2a6a2a; }
  .jump-link { color: var(--accent); text-decoration: none; cursor: pointer; }
  .jump-link:hover { text-decoration: underline; }
  .panel { background: var(--card); border: 1px solid var(--border); padding: 1rem;
           margin: 1rem 0; }
  pre.json { font-size: 0.72rem; max-height: 300px; overflow: auto;
             background: #f5f1e8; padding: 0.5rem; }
  .night-pane { display: none; }
  .night-pane.active { display: block; }
  .deployment-context-pane { background: #f0e8dc; padding: 0.75rem;
                              border-left: 3px solid #8a5a1a; font-size: 0.9rem;
                              white-space: pre-wrap; }
</style>
</head>
<body>
<header>
  <h1>Athens 2026 — Data Graph</h1>
  <span class="subtitle">__SUMMARY__</span>
</header>
<nav class="tabs">
  <button data-night="night_1" class="active">Night 1</button>
  <button data-night="night_2">Night 2</button>
  <button data-night="night_3">Night 3 closing</button>
  <span class="spacer"></span>
  <span class="voices-index">Voices index ▾
    <div class="menu" id="voices-menu"></div>
  </span>
</nav>
<main>
  <div id="night_1" class="night-pane active"></div>
  <div id="night_2" class="night-pane"></div>
  <div id="night_3" class="night-pane"></div>
</main>
<script id="data" type="application/json">__JSON_DATA__</script>
<script>
const DATA = JSON.parse(document.getElementById('data').textContent);

function el(tag, attrs={}, ...children) {
  const e = document.createElement(tag);
  for (const k in attrs) {
    if (k === 'class') e.className = attrs[k];
    else if (k === 'html') e.innerHTML = attrs[k];
    else e.setAttribute(k, attrs[k]);
  }
  for (const c of children) {
    if (c == null) continue;
    if (typeof c === 'string') e.appendChild(document.createTextNode(c));
    else e.appendChild(c);
  }
  return e;
}

function det(summary, open=false) {
  const d = el('details');
  if (open) d.setAttribute('open', '');
  d.appendChild(el('summary', {}, summary));
  const body = el('div', {class: 'body'});
  d.appendChild(body);
  return [d, body];
}

function meta(label, value) {
  if (value == null || value === '') return null;
  const wrap = el('div', {class: 'meta'});
  wrap.appendChild(el('b', {}, label + ':'));
  wrap.appendChild(document.createTextNode(' ' + String(value)));
  return wrap;
}

function metaGrid(pairs) {
  const g = el('div', {class: 'meta-grid'});
  for (const [k, v] of pairs) {
    if (v == null || v === '') continue;
    g.appendChild(el('b', {}, k + ':'));
    g.appendChild(el('span', {}, String(v)));
  }
  return g;
}

function abstract(text) {
  if (!text) return null;
  return el('div', {class: 'abstract'}, text);
}

function thinkingTrace(text) {
  if (!text) return null;
  const [d, body] = det(`🧠 Thinking trace (${text.length.toLocaleString()} chars)`);
  body.appendChild(el('div', {class: 'thinking-trace'}, text));
  return d;
}

function label(text, cls='') {
  return el('span', {class: 'label ' + cls}, text);
}

function jumpLink(text, target) {
  const a = el('a', {class: 'jump-link', href: '#' + CSS.escape(target)}, text);
  a.addEventListener('click', e => {
    e.preventDefault();
    const targetEl = document.querySelector('[data-anchor="' + target + '"]');
    if (targetEl) {
      const pane = targetEl.closest('.night-pane');
      if (pane) showNight(pane.id);
      // Open all <details> ancestors so the target is visible
      let cur = targetEl;
      while (cur && cur !== document.body) {
        if (cur.tagName === 'DETAILS') cur.setAttribute('open', '');
        cur = cur.parentElement;
      }
      // Also open the target itself if it's a <details>
      if (targetEl.tagName === 'DETAILS') targetEl.setAttribute('open', '');
      setTimeout(() => {
        targetEl.scrollIntoView({behavior: 'smooth', block: 'center'});
        targetEl.style.background = 'var(--highlight)';
        setTimeout(() => targetEl.style.background = '', 2500);
      }, 50);
    }
  });
  return a;
}

function anchor(id, ...children) {
  const a = el('div', {'data-anchor': id, id: 'a-' + id});
  for (const c of children) if (c) a.appendChild(c);
  return a;
}

function showNight(nightId) {
  document.querySelectorAll('.night-pane').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('nav.tabs button').forEach(b => b.classList.remove('active'));
  document.getElementById(nightId).classList.add('active');
  document.querySelector(`nav.tabs button[data-night="${nightId}"]`).classList.add('active');
}

document.querySelectorAll('nav.tabs button').forEach(b => {
  b.addEventListener('click', () => showNight(b.dataset.night));
});

// Render each night
for (const night of ['night_1', 'night_2', 'night_3']) {
  const pane = document.getElementById(night);
  renderNight(pane, night);
}

function renderNight(pane, night) {
  const n = DATA.nights[night] || {};
  const stats = n.statistics || {};
  // Stats bar
  const statsBar = el('div', {class: 'stats'});
  statsBar.innerHTML = `
    <b>${night.replace('_', ' ').replace(/^./, c => c.toUpperCase())}</b> —
    ${stats.sessions || 0} sessions ·
    ${(stats.turns || 0).toLocaleString()} turns ·
    ${(stats.words || 0).toLocaleString()} words ·
    ${stats.extractions || 0} extractions ·
    ${stats.clusters || 0} clusters ·
    ${stats.themes_selected || 0}/${stats.themes_total || 0} themes selected ·
    ${stats.formulations || 0} formulations ·
    ${stats.voice_step1 || 0} step1 ·
    ${stats.voice_step2 || 0} step2 ·
    ${stats.dossiers || 0} dossiers
  `;
  pane.appendChild(statsBar);

  // Deployment context discipline rules
  if (n.deployment_context_rules) {
    const [d, body] = det('📋 Deployment context discipline rules (this night)');
    body.appendChild(el('div', {class: 'deployment-context-pane'}, n.deployment_context_rules));
    pane.appendChild(d);
  }

  // Themes section
  pane.appendChild(el('div', {class: 'section-title'}, `Themes (${stats.themes_total || 0} total, ${stats.themes_selected || 0} selected)`));
  const themes = Object.values(DATA.themes).filter(t => t.night === night)
    .sort((a, b) => (a.theme_id || '').localeCompare(b.theme_id || ''));
  for (const t of themes) {
    pane.appendChild(renderTheme(t, night));
  }

  // Voices section
  pane.appendChild(el('div', {class: 'section-title'}, `Voices on ${night.replace('_', ' ')}`));
  const step2s = Object.values(DATA.voice_step2).filter(s => s.night === night)
    .sort((a, b) => (a.voice_slug || '').localeCompare(b.voice_slug || ''));
  for (const s of step2s) {
    pane.appendChild(renderStep2(s, night));
  }

  // Dossiers section
  pane.appendChild(el('div', {class: 'section-title'}, `Dossiers (${stats.dossiers || 0})`));
  const dossiers = Object.values(DATA.dossiers).filter(d => d.night === night)
    .sort((a, b) => (a.dossier_num || '').localeCompare(b.dossier_num || ''));
  for (const d of dossiers) {
    pane.appendChild(renderDossier(d, night));
  }

  // Sessions section (collapsed at top level)
  const [sessSec, sessBody] = det(`📼 Sessions (${stats.sessions || 0} — transcripts + speakers)`);
  pane.appendChild(sessSec);
  const sessions = Object.values(DATA.sessions).filter(s => s.night === night);
  for (const s of sessions) {
    sessBody.appendChild(renderSession(s, night));
  }
}

function renderTheme(t, night) {
  const sel = t.selected_for_provocateur ? label('SELECTED', 'pass') : label('dropped', 'warn');
  const [d, body] = det(
    `▼ ${t.theme_id_raw || t.theme_id} — "${t.title}"  ` + (t.selected_for_provocateur ? '⭐' : '')
  );
  // Tag with anchor
  d.setAttribute('data-anchor', t.prefixed_id);
  body.appendChild(el('div', {class: 'id'}, t.prefixed_id, ' — ',
    t.selected_for_provocateur ? '✓ selected' : '✗ dropped'));
  if (t.abstract) body.appendChild(abstract(t.abstract));

  // Clusters
  const clusterIds = t.cluster_ids || [];
  const [cSec, cBody] = det(`Clusters (${clusterIds.length})`);
  body.appendChild(cSec);
  for (const cid of clusterIds) {
    const c = DATA.clusters[cid];
    if (c) cBody.appendChild(renderCluster(c, night));
  }

  // Formulations + Step 1 + Step 2 chain (if theme was selected)
  if (t.selected_for_provocateur) {
    const formsForTheme = Object.values(DATA.formulations)
      .filter(f => f.theme_id === t.prefixed_id)
      .sort((a, b) => (a.voice_slug || '').localeCompare(b.voice_slug || ''));
    const [fSec, fBody] = det(`Formulations (${formsForTheme.length}) — per voice`);
    body.appendChild(fSec);
    for (const f of formsForTheme) {
      fBody.appendChild(renderFormulation(f, night));
    }
  }

  // Dossier for this theme
  const dossierForTheme = Object.values(DATA.dossiers).find(d => d.theme_id === t.prefixed_id);
  if (dossierForTheme) {
    const [doSec, doBody] = det(`📰 Dossier organized around this theme: ${dossierForTheme.dossier_num} — "${dossierForTheme.kicker || dossierForTheme.headline}"`);
    body.appendChild(doSec);
    const link = jumpLink('Open dossier ↓', dossierForTheme.dossier_id);
    doBody.appendChild(el('div', {}, link));
  }

  return d;
}

function renderCluster(c, night) {
  const [d, body] = det(`${c.cluster_id} — "${c.cluster_title}" (${(c.extraction_ids||[]).length} extractions)`);
  d.setAttribute('data-anchor', c.prefixed_id);
  body.appendChild(el('div', {class: 'id'}, c.prefixed_id));
  if (c.cluster_abstract) body.appendChild(abstract(c.cluster_abstract));
  const [eSec, eBody] = det(`Extractions (${(c.extraction_ids||[]).length})`);
  body.appendChild(eSec);
  for (const eid of c.extraction_ids || []) {
    const e = DATA.extractions[eid];
    if (e) eBody.appendChild(renderExtraction(e, night));
  }
  return d;
}

function renderExtraction(e, night) {
  const [d, body] = det(
    `${e.extraction_id} — ${(e.extraction || '').slice(0, 100)}…`
  );
  d.setAttribute('data-anchor', e.extraction_id);
  body.appendChild(metaGrid([
    ['Session', e.session_title],
    ['Speaker', e.speaker],
    ['Lens', e.lens],
    ['Energy', e.energy],
    ['Engagement', e.engagement || '—'],
    ['Responds to', e.responds_to || '—'],
  ]));
  if (e.extraction) body.appendChild(el('div', {class: 'extraction-content'}, e.extraction));
  if (e.context) {
    const [cd, cb] = det('Context (surrounding turn text)');
    cb.appendChild(el('div', {class: 'turn-text'}, e.context));
    body.appendChild(cd);
  }
  // Session jump
  if (e.session_id) {
    body.appendChild(el('div', {},
      jumpLink('→ Jump to session: ' + e.session_title, e.session_id)));
  }
  return d;
}

function renderFormulation(f, night) {
  const [d, body] = det(`${f.voice_slug} × ${f.theme_id_raw} — "${f.theme_display_title || ''}"`);
  d.setAttribute('data-anchor', f.formulation_id);
  body.appendChild(el('div', {class: 'id'}, f.formulation_id));
  if (f.formulation_text) {
    body.appendChild(el('div', {}, el('b', {}, 'Formulation:')));
    body.appendChild(el('div', {class: 'formulation-text'}, f.formulation_text));
  }
  if (f.context_narrative) {
    const [cd, cb] = det('Context narrative');
    cb.appendChild(el('div', {class: 'narrative-briefing'}, f.context_narrative));
    body.appendChild(cd);
  }
  if (f.narrative_briefing) {
    const [nd, nb] = det('Full narrative briefing (passed to voice)');
    nb.appendChild(el('div', {class: 'narrative-briefing'}, f.narrative_briefing));
    body.appendChild(nd);
  }
  // Step 1 response for this formulation
  const step1Id = `${night}/${f.voice_slug}__${f.theme_id_raw}`;
  const s1 = DATA.voice_step1[step1Id];
  if (s1) {
    const [s1d, s1b] = det(`▶ Voice Step 1 response (${(s1.detailed_response || '').length.toLocaleString()} chars private reasoning)`);
    body.appendChild(s1d);
    s1b.appendChild(renderStep1Body(s1));
  }
  // Step 2 jump link — voice synthesizes across themes; full artifact lives in Voices section
  const step2Id = `${night}/${f.voice_slug}`;
  const s2 = DATA.voice_step2[step2Id];
  if (s2) {
    const primaryTheme = (s2.lineage || {}).primary_theme_id;
    const isPrimary = primaryTheme === f.theme_id_raw;
    const note = isPrimary
      ? `★ This voice's Step 2 focused on THIS theme (${primaryTheme})`
      : `This voice's Step 2 focused on ${primaryTheme || 'another theme'} — see Voices section for full synthesis`;
    const wrap = el('div', {class: 'panel', style: 'margin-top: 0.5rem;'});
    wrap.appendChild(el('div', {class: 'meta'}, note));
    wrap.appendChild(el('div', {}, '▶ ',
      jumpLink(`${s2.voice_slug} Step 2 artifact: "${s2.artifact_title || s2.selected_form || ''}" (${s2.word_count || 0} words) ↓`, step2Id)));
    body.appendChild(wrap);
  }
  return d;
}

function renderStep1Body(s1) {
  const wrap = el('div');
  wrap.appendChild(metaGrid([
    ['Model', s1.model],
    ['Thinking enabled', s1.thinking_enabled],
    ['Input tokens', s1.input_tokens],
    ['Output tokens', s1.output_tokens],
    ['Thinking tokens', s1.thinking_tokens],
    ['Cache creation', s1.cache_creation_input_tokens],
    ['Cache read', s1.cache_read_input_tokens],
    ['Wall clock', s1.wall_clock_s + 's'],
  ]));
  if (s1.detailed_response) {
    wrap.appendChild(el('div', {}, el('b', {}, 'Detailed response:')));
    wrap.appendChild(el('div', {class: 'response-text'}, s1.detailed_response));
  }
  const tt = thinkingTrace(s1.thinking_trace);
  if (tt) wrap.appendChild(tt);
  if (s1.step1_validation) {
    const [vd, vb] = det('Step 1 validation');
    vb.appendChild(el('pre', {class: 'json'}, JSON.stringify(s1.step1_validation, null, 2)));
    wrap.appendChild(vd);
  }
  return wrap;
}

function renderStep2(s, night) {
  const validation = s.validation || {};
  const verdict = (validation.overall_verdict || '').toLowerCase();
  const verdictClass = verdict === 'pass' ? 'pass' : verdict === 'hold' ? 'hold' : 'warn';
  const decision = (s.operator_decision || {}).decision || '';
  const sumTxt = `▼ ${s.voice_slug} Step 2 — "${s.artifact_title || s.selected_form || ''}" (${(s.word_count || 0)} words)`;
  const [d, body] = det(sumTxt);
  d.setAttribute('data-anchor', s.step2_id);
  body.appendChild(renderStep2Body(s, night));
  return d;
}

function renderStep2Body(s, night) {
  const wrap = el('div');
  const validation = s.validation || {};
  const verdict = (validation.overall_verdict || '').toLowerCase();
  const verdictClass = verdict === 'pass' ? 'pass' : verdict === 'hold' ? 'hold' : 'warn';
  const decision = (s.operator_decision || {}).decision || '';
  const labels = el('div', {});
  if (validation.overall_verdict) labels.appendChild(label(validation.overall_verdict, verdictClass));
  if (decision) labels.appendChild(label(decision, decision === 'release' ? 'released' : ''));
  if (s.focus_decision) labels.appendChild(label(s.focus_decision));
  wrap.appendChild(labels);

  // Continuity from prior night
  if (s.continuity_from_prior_night) {
    const [cd, cb] = det('↰ Continuity from prior night (voice memory consumed at start of this night)');
    cb.appendChild(el('div', {class: 'continuity-block'}, typeof s.continuity_from_prior_night === 'string' ? s.continuity_from_prior_night : JSON.stringify(s.continuity_from_prior_night, null, 2)));
    wrap.appendChild(cd);
  }

  wrap.appendChild(metaGrid([
    ['Focus decision', s.focus_decision],
    ['Selected form', s.selected_form],
    ['Stance', s.stance],
    ['Word count', s.word_count],
    ['Model', s.model],
    ['Input tokens', s.input_tokens],
    ['Output tokens', s.output_tokens],
    ['Thinking tokens', s.thinking_tokens],
    ['Wall clock', s.wall_clock_s + 's'],
  ]));

  if (s.focus_rationale) {
    wrap.appendChild(el('div', {}, el('b', {}, 'Focus rationale: '), s.focus_rationale));
  }
  if (s.stance_rationale) {
    wrap.appendChild(el('div', {}, el('b', {}, 'Stance rationale: '), s.stance_rationale));
  }
  if (s.form_rationale) {
    wrap.appendChild(el('div', {}, el('b', {}, 'Form rationale: '), s.form_rationale));
  }
  if (s.weight_assessment) {
    const [wd, wb] = det('Weight assessment');
    wb.appendChild(el('div', {class: 'response-text'}, s.weight_assessment));
    wrap.appendChild(wd);
  }
  if (s.artifact_text) {
    wrap.appendChild(el('div', {}, el('b', {}, 'Artifact text:')));
    wrap.appendChild(el('div', {class: 'artifact-text'}, s.artifact_text));
  }
  const tt = thinkingTrace(s.thinking_trace);
  if (tt) wrap.appendChild(tt);

  if (s.validation) {
    const [vd, vb] = det('Full validation verdict (all flags)');
    vb.appendChild(el('pre', {class: 'json'}, JSON.stringify(s.validation, null, 2)));
    wrap.appendChild(vd);
  }
  if (s.operator_decision) {
    const [od, ob] = det('Operator decision');
    ob.appendChild(el('pre', {class: 'json'}, JSON.stringify(s.operator_decision, null, 2)));
    wrap.appendChild(od);
  }
  // Source step1s
  const lineage = s.lineage || {};
  if (lineage.consumed_detailed_responses) {
    const [ld, lb] = det('Source Step 1 responses (consumed)');
    for (const sid of lineage.consumed_detailed_responses) {
      const step1Id = `${night}/${sid.replace('.json','')}`;
      lb.appendChild(el('div', {}, jumpLink('→ ' + sid, step1Id)));
    }
    wrap.appendChild(ld);
  }
  return wrap;
}

function renderDossier(d, night) {
  const [dEl, body] = det(`▼ ${d.dossier_num} — ${d.kicker || ''} · ${d.headline || ''}`);
  dEl.setAttribute('data-anchor', d.dossier_id);
  body.appendChild(el('div', {class: 'id'}, d.dossier_id + ' · theme: ' + (d.theme_id_raw || '—')));

  if (d.theme_id) {
    body.appendChild(el('div', {}, '⬆ ', jumpLink('Back to theme: ' + d.theme_display_title, d.theme_id)));
  }
  if (d.front_abstract) {
    body.appendChild(el('div', {}, el('b', {}, 'Abstract: '), d.front_abstract));
  }
  if (d.subline) {
    body.appendChild(el('div', {}, el('b', {}, 'Subline: '), d.subline));
  }
  if (d.pull_quote) {
    body.appendChild(el('div', {class: 'abstract'}, '“', d.pull_quote, '”'));
  }
  if (d.theme_title_for_dossier || d.theme_abstract_for_dossier) {
    body.appendChild(metaGrid([
      ['Theme title (for dossier)', d.theme_title_for_dossier],
      ['Theme abstract (for dossier)', d.theme_abstract_for_dossier],
    ]));
  }
  // Voices featured (from headnotes)
  if (d.headnotes && d.headnotes.length) {
    const [hd, hb] = det(`Headnotes (${d.headnotes.length} voices featured)`);
    for (const hn of d.headnotes) {
      const hnD = el('div', {style: 'border-left: 3px solid var(--accent); padding: 0.5rem; margin: 0.5rem 0; background: #fff;'});
      const slug = (hn.voice_slug || hn.voice || '').toLowerCase();
      hnD.appendChild(el('b', {}, hn.voice || hn.voice_slug || ''));
      if (slug) {
        hnD.appendChild(document.createTextNode(' — '));
        hnD.appendChild(jumpLink('see Step 2', `${night}/${slug}`));
      }
      const fields = ['headnote_text', 'pull_quote', 'gloss', 'note'];
      for (const f of fields) {
        if (hn[f]) {
          hnD.appendChild(el('div', {class: 'meta'}, el('b', {}, f + ': '), String(hn[f])));
        }
      }
      hb.appendChild(hnD);
    }
    body.appendChild(hd);
  }
  // Body paragraphs (the actual dossier text)
  if (d.body_paragraphs && d.body_paragraphs.length) {
    const [bd, bb] = det(`Body paragraphs (${d.body_paragraphs.length})`, true);
    for (const para of d.body_paragraphs) {
      const text = typeof para === 'string' ? para : (para.text || JSON.stringify(para));
      bb.appendChild(el('div', {class: 'body-paragraphs'}, text));
    }
    body.appendChild(bd);
  }
  // Panel speakers
  if (d.panel_speakers && d.panel_speakers.length) {
    const [pd, pb] = det(`Panel speakers (${d.panel_speakers.length})`);
    pb.appendChild(el('pre', {class: 'json'}, JSON.stringify(d.panel_speakers, null, 2)));
    body.appendChild(pd);
  }
  // Metadata
  if (d.metadata) {
    body.appendChild(metaGrid([
      ['Theme', d.metadata.theme_display_title],
      ['Generated by', d.metadata.generated_by],
      ['Model', d.metadata.model],
      ['Thinking tokens', d.metadata.thinking_tokens],
      ['Input tokens', d.metadata.input_tokens],
      ['Output tokens', d.metadata.output_tokens],
      ['Wall clock', d.metadata.wall_clock_s + 's'],
    ]));
  }
  // Tim's thinking trace
  const tt = thinkingTrace(d.thinking_trace);
  if (tt) body.appendChild(tt);
  if (d.colophon) {
    body.appendChild(el('div', {class: 'meta'}, '— ', d.colophon));
  }
  return dEl;
}

function renderSession(s, night) {
  const [d, body] = det(`${s.session_title || s.session_id} (${s.turn_count || 0} turns, ${(s.word_count||0).toLocaleString()} words)`);
  d.setAttribute('data-anchor', s.session_id);
  body.appendChild(metaGrid([
    ['Track', s.track],
    ['Venue', s.venue],
    ['Date/time', s.date_time],
    ['Format', s.session_format],
    ['Source', s.source],
    ['Reflection?', s.is_reflection ? 'Yes' : 'No'],
  ]));
  if (s.session_description) {
    body.appendChild(el('div', {class: 'meta'}, el('b', {}, 'Description: '), s.session_description));
  }
  if (s.roster && s.roster.length) {
    const [rd, rb] = det(`Roster (${s.roster.length} speakers)`);
    for (const sp of s.roster) {
      rb.appendChild(el('div', {class: 'meta'},
        el('b', {}, sp.name || ''),
        sp.title ? ' — ' + sp.title : '',
        sp.affiliation ? ' (' + sp.affiliation + ')' : ''));
    }
    body.appendChild(rd);
  }
  if (s.turns && s.turns.length) {
    const [td, tb] = det(`Transcript (${s.turns.length} turns)`);
    for (const turn of s.turns) {
      const tw = el('div', {});
      tw.appendChild(el('div', {class: 'turn-meta'},
        `#${turn.turn_index} — ${turn.speaker} (${turn.role || ''}) [${turn.confidence || ''}]`));
      tw.appendChild(el('div', {class: 'turn-text'}, turn.text || ''));
      tb.appendChild(tw);
    }
    body.appendChild(td);
  }
  return d;
}

// Build voices index dropdown
function buildVoicesIndex() {
  const menu = document.getElementById('voices-menu');
  const voiceSlugs = new Set();
  for (const k in DATA.voice_step2) {
    voiceSlugs.add(DATA.voice_step2[k].voice_slug);
  }
  for (const slug of [...voiceSlugs].sort()) {
    const row = el('div', {style: 'padding: 0.25rem 0.5rem; color: #ddd; font-size: 0.85rem;'});
    row.appendChild(el('b', {}, slug));
    for (const n of ['night_1', 'night_2', 'night_3']) {
      const s2id = `${n}/${slug}`;
      const exists = DATA.voice_step2[s2id];
      const link = el('a', {class: 'jump-link', href: '#', style: 'margin-left: 0.5rem;'}, n.replace('night_', 'N'));
      if (exists) {
        link.addEventListener('click', e => {
          e.preventDefault();
          showNight(n);
          setTimeout(() => {
            const target = document.querySelector(`[data-anchor="${s2id}"]`);
            if (target) {
              target.setAttribute('open', '');
              target.scrollIntoView({behavior: 'smooth', block: 'center'});
              target.style.background = 'var(--highlight)';
              setTimeout(() => target.style.background = '', 2000);
            }
          }, 100);
        });
        row.appendChild(link);
      } else {
        row.appendChild(el('span', {style: 'margin-left: 0.5rem; color: #666;'}, n.replace('night_', 'N')));
      }
    }
    menu.appendChild(row);
  }
}
buildVoicesIndex();
</script>
</body>
</html>
"""


def write_html_viewer(graph: dict) -> None:
    out_html = OUTPUT_DIR / "view_by_theme.html"
    # Summary line for header
    total = graph["metadata"]["total_nodes"]
    nodes = graph["metadata"]["nodes_per_kind"]
    summary = (f"{nodes['sessions']} sessions · {nodes['extractions']} extractions · "
               f"{nodes['clusters']} clusters · {nodes['themes']} themes · "
               f"{nodes['formulations']} formulations · {nodes['voice_step1']} step1 · "
               f"{nodes['voice_step2']} step2 · {nodes['dossiers']} dossiers")
    # Embed JSON safely: escape </script>
    json_text = json.dumps(graph, ensure_ascii=False, separators=(',', ':')).replace("</", "<\\/")
    html = HTML_TEMPLATE.replace("__SUMMARY__", summary).replace("__JSON_DATA__", json_text)
    out_html.write_text(html, encoding="utf-8")
    size_mb = out_html.stat().st_size / (1024 * 1024)
    print(f"✅ Wrote {out_html}  ({size_mb:.1f} MB)")


def write_readme() -> None:
    readme = OUTPUT_DIR / "README.md"
    readme.write_text("""# data_views — Athens 2026 data graph

Two files generated by `code/runtime/scripts/build_athens_data_graph.py`:

| File | What it is |
|---|---|
| `athens_data_graph.json` | The full pipeline data as one normalized JSON. Every entity (sessions, extractions, clusters, themes, formulations, voice Step 1/2, dossiers) with every field preserved (including thinking traces, token counts, validation flag detail, operator decisions, voice continuity blocks across nights, deployment_context discipline rules per night, all_extras catchalls so nothing is silently dropped). |
| `view_by_theme.html` | Self-contained interactive browser viewer. Open in any modern browser; no install, no server, no dependencies. Three tabs (Night 1 / 2 / 3 closing). Theme-tree drill-down + voices section + dossiers section + transcripts at the bottom. Native `<details>` collapsibles; cross-night threading via jump links; voices index in the top-right shows each voice's per-night status. |

## Rebuilding

```bash
cd code
AI_ASSEMBLY_PROJECT_ROOT="/path/to/athens-2026" \\
    python3 runtime/scripts/build_athens_data_graph.py
```

The script walks `runs/athens_night_{1,2,3}/` + `published_artifacts/` and
assembles both files. Idempotent; re-run any time the source data
changes.

## What's NOT in here

- Audio files (excluded from athens-2026 git per `.gitignore`)
- Step 3 amended artifacts (Step 3 was skipped for Athens per OPEN_ITEMS A1)
- Future build state (vatican-2026, etc.)

## Companion docs

- `published_artifacts/DATA_INVENTORY.md` — prose tour of what was collected per night
- `published_artifacts/EDITORIAL_ASSESSMENT.md` — editorial quality read of the 13 dossiers
- This dir = navigable structure of the same data, with every field preserved
""", encoding="utf-8")
    print(f"✅ Wrote {readme}")


def main() -> None:
    print(f"Building Athens data graph from {PROJECT_ROOT}")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    graph = build_graph()
    out_json = OUTPUT_DIR / "athens_data_graph.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(graph, f, ensure_ascii=False, indent=2)
    size_mb = out_json.stat().st_size / (1024 * 1024)
    print(f"\n✅ Wrote {out_json}  ({size_mb:.1f} MB)")
    print(f"   Total nodes: {graph['metadata']['total_nodes']}")
    print(f"   Per kind: {graph['metadata']['nodes_per_kind']}")
    for night in NIGHTS:
        s = graph["nights"][night].get("statistics", {})
        print(f"   {night}: {s}")
    write_html_viewer(graph)
    write_readme()


if __name__ == "__main__":
    main()
