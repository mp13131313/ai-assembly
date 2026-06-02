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
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet">
<style>
  /* ─── Style adapted from World Beautiful Business Forum (WBBF) ─── */
  :root {
    --ink: #0a0a0a;
    --paper: #ffffff;
    --cream: #f5f5f5;
    --warm-mid: #555555;
    --warm-light: #888888;
    --border-soft: rgba(0,0,0,0.08);
    --border-mid: rgba(0,0,0,0.15);
    /* Brand palette */
    --brand-blue: #0F49F4;
    --brand-blue-light: #e8eeff;
    --brand-red: #D63C23;
    --brand-red-light: #fff0ec;
    --brand-green: #00845C;
    --brand-gold: #8C7203;
    /* Phase semantics — Conference Data = blue (facts/research), Assembly Output = rust-red (voices/deliberation) */
    --conf-accent: #0F49F4;
    --conf-accent-bg: #e8eeff;
    --assembly-accent: #D63C23;
    --assembly-accent-bg: #fff0ec;
    /* Backward-compat aliases (so existing inline references resolve) */
    --bg: var(--paper);
    --fg: var(--ink);
    --muted: var(--warm-mid);
    --border: var(--border-mid);
    --accent: var(--conf-accent);
    --accent-bg: var(--conf-accent-bg);
    --card: var(--paper);
    --highlight: #fef0c8;
    /* Fonts */
    --sans: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    --serif: 'Libre Baskerville', Georgia, serif;
    --display: 'Impact', 'Arial Black', 'Helvetica Neue Condensed', sans-serif;
    --mono: 'SF Mono', 'Monaco', 'Inconsolata', monospace;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  html { scroll-behavior: smooth; }
  body { background: var(--paper); color: var(--ink); font: 13px/1.6 var(--sans);
         min-height: 100vh; overflow-x: hidden; }

  /* When the active page is the Assembly page, swap accent to rust-red */
  .page-pane[id$="_assembly"] { --accent: var(--assembly-accent);
                                --accent-bg: var(--assembly-accent-bg); }

  /* ─── HERO ─── */
  .hero { background: var(--ink); color: var(--paper); padding: 64px 40px 48px;
          position: relative; overflow: hidden; }
  .hero-eyebrow { font-family: var(--sans); font-size: 10px; letter-spacing: 0.25em;
                  text-transform: uppercase; color: rgba(255,255,255,0.7);
                  margin-bottom: 10px; font-weight: 500; }
  .hero-title { font-family: var(--display); font-size: clamp(40px, 6vw, 72px);
                font-weight: 400; line-height: 1.0; letter-spacing: 0.02em;
                text-transform: uppercase; margin-bottom: 10px; }
  .hero-title em { font-style: normal; color: var(--brand-blue); }
  .hero-subtitle { font-family: var(--serif); font-size: clamp(15px, 1.8vw, 20px);
                   font-weight: 400; font-style: italic; color: rgba(255,255,255,0.75);
                   margin-bottom: 36px; max-width: 720px; line-height: 1.45; }
  .hero-meta { display: flex; gap: 40px; flex-wrap: wrap; }
  .hero-meta-item { display: flex; flex-direction: column; gap: 4px; }
  .hero-meta-label { font-size: 9px; letter-spacing: 0.2em; text-transform: uppercase;
                     color: rgba(255,255,255,0.55); font-weight: 500; }
  .hero-meta-value { font-family: var(--serif); font-size: 18px; font-weight: 400;
                     color: var(--paper); }

  /* ─── STICKY CONTROLS (top nav with night dropdowns) ─── */
  nav.tabs { background: var(--ink); border-bottom: 2px solid var(--brand-blue);
             padding: 0 40px; display: flex; align-items: stretch; gap: 0;
             position: sticky; top: 0; z-index: 99; overflow: visible; }
  nav.tabs .night-menu { position: relative; display: inline-flex; }
  nav.tabs .night-button { background: transparent; border: 0;
                           color: rgba(255,255,255,0.75); font-family: var(--sans);
                           font-size: 10px; letter-spacing: 0.15em; text-transform: uppercase;
                           padding: 16px 18px; cursor: pointer; white-space: nowrap;
                           border-bottom: 2px solid transparent; margin-bottom: -2px;
                           transition: color 0.2s; }
  nav.tabs .night-menu:hover .night-button { color: var(--paper); }
  nav.tabs .night-menu.has-conf-active .night-button { color: var(--paper);
                                                       border-bottom-color: var(--brand-blue); }
  nav.tabs .night-menu.has-assembly-active .night-button { color: var(--paper);
                                                          border-bottom-color: var(--brand-red); }
  nav.tabs .night-menu .dropdown { display: none; position: absolute; top: 100%; left: 0;
                                    background: var(--ink); border: 1px solid rgba(255,255,255,0.2);
                                    min-width: 240px; padding: 0; z-index: 200; }
  nav.tabs .night-menu:hover .dropdown { display: block; }
  nav.tabs .night-menu .dropdown a { display: block; color: rgba(255,255,255,0.85);
                                     padding: 12px 18px; text-decoration: none;
                                     font-family: var(--sans); font-size: 10px;
                                     letter-spacing: 0.12em; text-transform: uppercase;
                                     font-weight: 500; cursor: pointer;
                                     border-left: 3px solid transparent;
                                     transition: all 0.15s; }
  nav.tabs .night-menu .dropdown a:hover { background: rgba(255,255,255,0.08);
                                           color: var(--paper); }
  nav.tabs .night-menu .dropdown a.active.conf-link { background: var(--brand-blue);
                                                      color: var(--paper);
                                                      border-left-color: var(--brand-blue); }
  nav.tabs .night-menu .dropdown a.active.assembly-link { background: var(--brand-red);
                                                          color: var(--paper);
                                                          border-left-color: var(--brand-red); }
  nav.tabs .spacer { flex: 1; }
  nav.tabs .voices-index { color: rgba(255,255,255,0.75); padding: 16px 18px;
                           cursor: pointer; font-family: var(--sans); font-size: 10px;
                           letter-spacing: 0.15em; text-transform: uppercase;
                           position: relative; font-weight: 500; }
  nav.tabs .voices-index:hover { color: var(--paper); }
  .voices-index .menu { display: none; position: absolute; top: 100%; right: 0;
                        background: var(--ink); border: 1px solid rgba(255,255,255,0.2);
                        min-width: 320px; padding: 12px; z-index: 200;
                        text-transform: none; letter-spacing: normal;
                        font-family: var(--sans); }
  .voices-index:hover .menu { display: block; }
  .voices-index .menu a { display: inline-block; color: rgba(255,255,255,0.85);
                          padding: 2px 4px; text-decoration: none; font-size: 11px; }
  .voices-index .menu a:hover { color: var(--brand-blue); }

  /* ─── MAIN ─── */
  main { padding: 0 40px 80px; max-width: 1280px; margin: 0 auto; }

  /* ─── STATS BAR ─── */
  .stats { background: transparent; border: 0; border-bottom: 1px solid var(--border-soft);
           padding: 24px 0 18px; margin: 0 0 8px; font-family: var(--sans);
           font-size: 11px; color: var(--warm-mid); letter-spacing: 0.02em; }
  .stats b { font-family: var(--serif); font-style: italic; font-size: 22px;
             font-weight: 400; color: var(--ink); display: block; margin-bottom: 8px;
             letter-spacing: -0.01em; }

  /* ─── SUB-NAV (section pills, filter-chip style) ─── */
  .sub-nav { position: sticky; top: 50px; background: var(--cream);
             border-bottom: 1px solid var(--border-soft); padding: 12px 40px;
             margin: 0 -40px 24px; z-index: 50; display: flex; gap: 6px;
             flex-wrap: wrap; align-items: center; }
  .sub-nav .phase-tag { font-family: var(--sans); font-size: 9px; letter-spacing: 0.2em;
                        text-transform: uppercase; color: var(--warm-mid);
                        margin-right: 10px; font-weight: 600; }
  .sub-nav .phase-tag.conf { color: var(--brand-blue); }
  .sub-nav .phase-tag.assembly { color: var(--brand-red); }
  .sub-nav .phase-tag::after { content: ''; }
  .sub-nav a.section-link { background: var(--paper); border: 1px solid var(--border-mid);
                            color: var(--ink); font-family: var(--sans); font-size: 10px;
                            letter-spacing: 0.05em; padding: 5px 12px;
                            border-radius: 2px; text-decoration: none;
                            white-space: nowrap; transition: all 0.15s; }
  .sub-nav a.section-link:hover { background: var(--ink); border-color: var(--ink);
                                   color: var(--paper); }
  .sub-nav a.section-link.active.conf { background: var(--brand-blue);
                                         border-color: var(--brand-blue); color: var(--paper); }
  .sub-nav a.section-link.active.assembly { background: var(--brand-red);
                                              border-color: var(--brand-red); color: var(--paper); }

  /* ─── SECTION TITLES ─── */
  .section-title { font-family: var(--serif); font-size: 24px; font-style: italic;
                   font-weight: 400; color: var(--ink); margin: 36px 0 14px;
                   padding-bottom: 10px; border-bottom: 2px solid var(--ink); }

  /* ─── DETAILS / CARDS ─── */
  details { background: var(--paper); border: 1px solid var(--border-mid);
            margin: 6px 0; border-radius: 2px; }
  details > summary { cursor: pointer; padding: 12px 16px; font-family: var(--serif);
                      font-size: 14px; line-height: 1.4; color: var(--ink);
                      user-select: none; transition: background 0.15s; }
  details > summary:hover { background: var(--cream); }
  details > .body { padding: 14px 16px 16px; border-top: 1px solid var(--border-soft); }
  details details { margin-left: 14px; border-left: 2px solid var(--border-soft);
                    border-top: 0; border-right: 0; border-bottom: 0; border-radius: 0; }
  details details > summary { padding: 10px 14px; font-size: 13px; }

  /* ─── IDs / META ─── */
  .id { font-family: var(--mono); font-size: 10px; color: var(--warm-light);
        letter-spacing: 0.02em; }
  .abstract { background: var(--cream); padding: 12px 16px; margin: 10px 0;
              border-left: 3px solid var(--accent); font-family: var(--serif);
              font-size: 13px; font-style: italic; color: #2a2a2a; line-height: 1.55; }
  .meta { font-size: 11px; color: var(--warm-mid); margin: 4px 0;
          font-family: var(--sans); }
  .meta b { color: var(--ink); font-weight: 600; }
  .meta-grid { display: grid; grid-template-columns: max-content 1fr;
               gap: 4px 16px; font-size: 11px; color: var(--warm-mid);
               margin: 8px 0; font-family: var(--sans); }
  .meta-grid b { color: var(--ink); font-weight: 600; }

  /* ─── THINKING TRACE (mono editorial muted) ─── */
  .thinking-trace { background: var(--cream); border: 1px solid var(--border-soft);
                    padding: 10px 14px; font-family: var(--mono); font-size: 11px;
                    white-space: pre-wrap; max-height: 400px; overflow-y: auto;
                    color: var(--warm-mid); line-height: 1.55; }

  /* ─── BODY CONTENT BLOCKS (Libre Baskerville) ─── */
  .artifact-text, .response-text, .body-paragraphs, .formulation-text, .narrative-briefing,
  .deployment-context, .continuity-block, .extraction-content {
    white-space: pre-wrap; font: 14px/1.75 var(--serif); margin: 8px 0;
    background: var(--paper); padding: 16px 20px;
    border-left: 3px solid var(--accent); color: #1a1a1a;
  }

  /* ─── TURNS (transcripts) ─── */
  .turn-text { font-size: 13px; color: #2a2a2a; padding: 4px 10px;
               border-left: 2px solid var(--border-soft); margin: 4px 0;
               font-family: var(--sans); line-height: 1.6; }
  .turn-meta { font-size: 10px; color: var(--warm-light); font-family: var(--mono);
               letter-spacing: 0.02em; }

  /* ─── LABELS (status pills) ─── */
  .label { display: inline-block; background: var(--accent-bg); color: var(--accent);
           padding: 2px 7px; font-size: 9px; font-family: var(--sans);
           font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase;
           border-radius: 2px; margin-right: 4px; vertical-align: middle;
           line-height: 1.5; }
  .label.pass { background: #d8f0e2; color: #00563c; }
  .label.warn { background: #fef0c8; color: #6b5300; }
  .label.hold { background: #fee0d0; color: #893309; }
  .label.released { background: #d8f0e2; color: #00563c; }

  /* ─── JUMP LINKS ─── */
  .jump-link { color: var(--accent); text-decoration: none; cursor: pointer;
               border-bottom: 1px solid currentColor; }
  .jump-link:hover { background: var(--accent-bg); }

  /* ─── PANELS ─── */
  .panel { background: var(--paper); border: 1px solid var(--border-mid);
           padding: 16px 18px; margin: 14px 0; border-radius: 2px; }
  pre.json { font-family: var(--mono); font-size: 10px; max-height: 300px;
             overflow: auto; background: var(--cream); padding: 10px;
             border-radius: 2px; line-height: 1.5; }

  /* ─── PAGE PANES ─── */
  .page-pane { display: none; }
  .page-pane.active { display: block; }

  /* ─── DEPLOYMENT CONTEXT (special pane) ─── */
  .deployment-context-pane { background: var(--cream); padding: 14px 18px;
                              border-left: 3px solid var(--brand-gold);
                              font-family: var(--sans); font-size: 13px;
                              white-space: pre-wrap; line-height: 1.6;
                              color: var(--ink); }

  /* ─── BACKLINK PILLS ─── */
  .backlink { font-family: var(--sans); font-size: 10px; letter-spacing: 0.05em;
              color: var(--accent); margin: 4px 4px 4px 0; padding: 3px 8px;
              background: var(--accent-bg); border-radius: 2px;
              display: inline-block; text-transform: none; }

  /* ─── EXTRACTION SUMMARIES ─── */
  .extraction-summary { font-size: 13px; }
  .extraction-summary .speaker { font-weight: 600; color: var(--warm-mid);
                                 font-family: var(--sans); }
  .extraction-summary .lens { color: var(--accent); font-family: var(--sans);
                              font-size: 10px; letter-spacing: 0.08em;
                              text-transform: uppercase; }
  details.extraction > summary { font: 14px/1.5 var(--serif); padding: 12px 16px;
                                  color: var(--ink); }
  details.extraction > summary b.speaker { font-family: var(--sans); font-weight: 700;
                                            color: var(--accent); font-size: 10px;
                                            letter-spacing: 0.1em; text-transform: uppercase; }
  details.extraction > summary i.lens { font-style: normal; font-family: var(--sans);
                                         font-size: 9px; letter-spacing: 0.1em;
                                         text-transform: uppercase; color: var(--warm-mid);
                                         background: var(--cream); padding: 2px 7px;
                                         border-radius: 2px; margin-right: 8px; }

  /* ─── TRACK / CAPTURE-GROUP HEADERS ─── */
  .capture-group-header { background: var(--ink); color: var(--paper);
                          padding: 12px 18px; font-family: var(--display);
                          font-size: 14px; font-weight: 400; letter-spacing: 0.08em;
                          text-transform: uppercase; margin: 28px 0 8px;
                          border-radius: 0; }
  .track-header { background: transparent; color: var(--ink);
                  padding: 6px 0; font-family: var(--serif); font-style: italic;
                  font-size: 16px; font-weight: 400; margin: 18px 0 6px;
                  border-bottom: 1px solid var(--border-soft); border-radius: 0;
                  letter-spacing: 0; }

  /* ─── FOOTER ─── */
  footer.footer { background: var(--ink); color: var(--paper); padding: 32px 40px;
                  text-align: center; font-family: var(--sans); font-size: 10px;
                  letter-spacing: 0.15em; text-transform: uppercase; margin-top: 40px; }
  footer.footer a { color: inherit; text-decoration: underline; }

  /* ─── MOBILE ─── */
  @media (max-width: 768px) {
    .hero { padding: 40px 20px 32px; }
    nav.tabs { padding: 0 16px; }
    main { padding: 0 16px 60px; }
    .sub-nav { padding: 10px 16px; margin: 0 -16px 16px; }
    .hero-meta { gap: 24px; }
  }
</style>
</head>
<body>
<header class="hero">
  <p class="hero-eyebrow">House of Beautiful Business · AI Assembly · Athens 2026</p>
  <h1 class="hero-title">Athens <em>Data Graph</em></h1>
  <p class="hero-subtitle">The pipeline behind three nights of deliberation — sessions, extractions, clusters, themes, voices, dossiers — every field preserved.</p>
  <div class="hero-meta" id="heroMeta"></div>
</header>
<nav class="tabs">
  <span class="night-menu has-conf-active" data-night="night_1">
    <button class="night-button">Night 1 ▾</button>
    <div class="dropdown">
      <a class="dropdown-link conf-link active" data-page="night_1_conf">📊 Conference Data</a>
      <a class="dropdown-link assembly-link" data-page="night_1_assembly">🎭 Assembly Output</a>
    </div>
  </span>
  <span class="night-menu" data-night="night_2">
    <button class="night-button">Night 2 ▾</button>
    <div class="dropdown">
      <a class="dropdown-link conf-link" data-page="night_2_conf">📊 Conference Data</a>
      <a class="dropdown-link assembly-link" data-page="night_2_assembly">🎭 Assembly Output</a>
    </div>
  </span>
  <span class="night-menu" data-night="night_3">
    <button class="night-button">Night 3 closing ▾</button>
    <div class="dropdown">
      <a class="dropdown-link conf-link" data-page="night_3_conf">📊 Conference Data</a>
      <a class="dropdown-link assembly-link" data-page="night_3_assembly">🎭 Assembly Output</a>
    </div>
  </span>
  <span class="spacer"></span>
  <span class="voices-index">Voices index ▾
    <div class="menu" id="voices-menu"></div>
  </span>
</nav>
<main>
  <div id="night_1_conf" class="page-pane active"></div>
  <div id="night_1_assembly" class="page-pane"></div>
  <div id="night_2_conf" class="page-pane"></div>
  <div id="night_2_assembly" class="page-pane"></div>
  <div id="night_3_conf" class="page-pane"></div>
  <div id="night_3_assembly" class="page-pane"></div>
</main>
<footer class="footer">
  <p>Athens 2026 · House of Beautiful Business · AI Assembly</p>
  <p style="margin-top:8px;letter-spacing:0.1em;">Self-contained viewer · regenerate with <code style="background:rgba(255,255,255,0.1);padding:1px 6px;">build_athens_data_graph.py</code></p>
</footer>
<script id="data" type="application/json">__JSON_DATA__</script>
<script>
const DATA = JSON.parse(document.getElementById('data').textContent);

// Populate hero meta from DATA — emits 4 label/value cards
(function populateHeroMeta() {
  const heroMeta = document.getElementById('heroMeta');
  if (!heroMeta) return;
  const md = DATA.metadata || {};
  const nodes = md.nodes_per_kind || {};
  const items = [
    ['Dates', 'May 7–9, 2026'],
    ['Nights', '3'],
    ['Sessions', String(nodes.sessions || 0)],
    ['Artifacts', String(nodes.voice_step2 || 0)],
  ];
  for (const [label, value] of items) {
    const item = document.createElement('div');
    item.className = 'hero-meta-item';
    const lbl = document.createElement('span');
    lbl.className = 'hero-meta-label';
    lbl.textContent = label;
    const val = document.createElement('span');
    val.className = 'hero-meta-value';
    val.textContent = value;
    item.appendChild(lbl);
    item.appendChild(val);
    heroMeta.appendChild(item);
  }
})();

// Format voice slug for display. tim_leberecht → "the editor"; ada_lovelace → "Ada Lovelace"
function formatVoiceName(slug) {
  if (!slug) return '';
  if (slug === 'tim_leberecht' || slug === 'the_editor' || slug === 'editor') return 'the editor';
  return slug.split('_').map(w => w ? w[0].toUpperCase() + w.slice(1) : '').join(' ');
}

// Format an artifact summary. Falls back to "artifact" when no real title (avoids dumping verbose selected_form).
function formatArtifactSummary(s) {
  const voice = formatVoiceName(s.voice_slug);
  const title = (s.artifact_title || '').trim();
  const wc = s.word_count || 0;
  if (title) return `${voice}: "${title}" (${wc} words)`;
  return `${voice}: artifact (${wc} words)`;
}

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
      const pagePane = targetEl.closest('.page-pane');
      if (pagePane && pagePane.id) showPage(pagePane.id);
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

function showPage(pageId) {
  document.querySelectorAll('.page-pane').forEach(p => p.classList.remove('active'));
  const target = document.getElementById(pageId);
  if (!target) return;
  target.classList.add('active');
  // Highlight active dropdown link
  document.querySelectorAll('.dropdown-link').forEach(a => a.classList.remove('active'));
  const link = document.querySelector(`.dropdown-link[data-page="${pageId}"]`);
  if (link) link.classList.add('active');
  // Highlight night menu (which night + which phase is current)
  const night = pageId.replace(/_conf$|_assembly$/, '');
  const phase = pageId.endsWith('_assembly') ? 'assembly' : 'conf';
  document.querySelectorAll('.night-menu').forEach(m => {
    m.classList.remove('has-conf-active', 'has-assembly-active');
  });
  const menu = document.querySelector(`.night-menu[data-night="${night}"]`);
  if (menu) menu.classList.add(phase === 'conf' ? 'has-conf-active' : 'has-assembly-active');
  // Reset section-link highlighting; the IntersectionObserver will re-activate as user scrolls
  document.querySelectorAll('.sub-nav a.section-link').forEach(a => a.classList.remove('active'));
  const firstLink = target.querySelector('.sub-nav a.section-link');
  if (firstLink) firstLink.classList.add('active');
}

document.querySelectorAll('.dropdown-link').forEach(a => {
  a.addEventListener('click', e => {
    e.preventDefault();
    showPage(a.dataset.page);
    window.scrollTo({top: 0, behavior: 'instant'});
  });
});

// Render each of the 6 pages (3 nights × 2 phases)
for (const night of ['night_1', 'night_2', 'night_3']) {
  for (const phase of ['conf', 'assembly']) {
    const pane = document.getElementById(`${night}_${phase}`);
    renderPage(pane, night, phase);
  }
}

function renderPage(pane, night, phase) {
  const n = DATA.nights[night] || {};
  const stats = n.statistics || {};
  const nightLabel = night.replace('_', ' ').replace(/^./, c => c.toUpperCase());
  const phaseLabel = phase === 'conf' ? '📊 Conference Data' : '🎭 Assembly Output';

  // Stats bar — same stats both pages; header distinguishes which page you're on
  const statsBar = el('div', {class: 'stats'});
  statsBar.innerHTML = `
    <b>${nightLabel} — ${phaseLabel}</b> —
    ${stats.sessions || 0} sessions ·
    ${(stats.turns || 0).toLocaleString()} turns ·
    ${(stats.words || 0).toLocaleString()} words ·
    ${stats.extractions || 0} extractions ·
    ${stats.clusters || 0} clusters ·
    ${stats.themes_selected || 0}/${stats.themes_total || 0} themes selected ·
    ${stats.formulations || 0} formulations ·
    ${stats.voice_step1 || 0} private-thinking responses ·
    ${stats.voice_step2 || 0} artifacts ·
    ${stats.dossiers || 0} dossiers
  `;
  pane.appendChild(statsBar);

  // Deployment context discipline rules (Conference Data page only — it's about how researcher/provocateur read the content)
  if (phase === 'conf' && n.deployment_context_rules) {
    const [d, body] = det('📋 Deployment context discipline rules (this night)');
    body.appendChild(el('div', {class: 'deployment-context-pane'}, n.deployment_context_rules));
    pane.appendChild(d);
  }

  // Sub-nav — section pills for this page's phase only
  const subnav = el('nav', {class: 'sub-nav'});
  if (phase === 'conf') {
    subnav.innerHTML = `
      <span class="phase-tag conf">Conference Data</span>
      <a href="#" data-target="sec-${night}-sessions" class="section-link conf">📼 Sessions</a>
      <a href="#" data-target="sec-${night}-themes" class="section-link conf">🏷 Themes (with clusters inside)</a>
    `;
  } else {
    subnav.innerHTML = `
      <span class="phase-tag assembly">Assembly Output</span>
      <a href="#" data-target="sec-${night}-selected" class="section-link assembly">🎯 Selected themes</a>
      <a href="#" data-target="sec-${night}-voices" class="section-link assembly">🗣 Voices</a>
      <a href="#" data-target="sec-${night}-dossiers" class="section-link assembly">📰 Dossiers</a>
    `;
  }
  subnav.querySelectorAll('a').forEach(a => {
    a.addEventListener('click', e => {
      e.preventDefault();
      const tgt = document.getElementById(a.dataset.target);
      if (tgt) tgt.scrollIntoView({behavior: 'smooth', block: 'start'});
    });
  });
  pane.appendChild(subnav);

  if (phase === 'conf') {
    // ===== CONFERENCE DATA =====

    // Sessions — grouped by capture type, then by track (matching DATA_INVENTORY)
    pane.appendChild(el('div', {class: 'section-title', id: `sec-${night}-sessions`, 'data-section': `sec-${night}-sessions`},
      `📼 Sessions (${stats.sessions || 0})`));
    const sessions = Object.values(DATA.sessions).filter(s => s.night === night);
    const audioSessions = sessions.filter(s => !s.is_reflection)
      .sort((a, b) => (a.date_time || '').localeCompare(b.date_time || ''));
    const reflectionSessions = sessions.filter(s => s.is_reflection)
      .sort((a, b) => (a.date_time || '').localeCompare(b.date_time || ''));

    function groupByTrack(arr) {
      const groups = {};
      for (const s of arr) {
        const track = s.track || 'Other';
        if (!groups[track]) groups[track] = [];
        groups[track].push(s);
      }
      return groups;
    }
    function formatTrack(t) {
      if (!t) return 'Other';
      return t.split(' ').map(w => w ? w[0].toUpperCase() + w.slice(1).toLowerCase() : '').join(' ');
    }
    const trackOrder = ['MAIN STAGE', 'AI DEMOCRACY MARATHON', 'DEPARTMENT OF DEPTH',
                        'AGENTIC AGORA', 'COMMUNITY'];
    function trackSort(a, b) {
      const ia = trackOrder.indexOf(a), ib = trackOrder.indexOf(b);
      if (ia >= 0 && ib >= 0) return ia - ib;
      if (ia >= 0) return -1;
      if (ib >= 0) return 1;
      return a.localeCompare(b);
    }

    if (audioSessions.length) {
      pane.appendChild(el('div', {class: 'capture-group-header'},
        `🎙 Audio (${audioSessions.length} captures) — panel transcriptions, by track`));
      const byTrack = groupByTrack(audioSessions);
      for (const track of Object.keys(byTrack).sort(trackSort)) {
        pane.appendChild(el('div', {class: 'track-header'}, formatTrack(track)));
        for (const s of byTrack[track]) {
          pane.appendChild(renderSession(s, night));
        }
      }
    }
    if (reflectionSessions.length) {
      pane.appendChild(el('div', {class: 'capture-group-header'},
        `💬 Audience reflections (${reflectionSessions.length}) — spoken contributions submitted via the audience tool, by track`));
      const byTrack = groupByTrack(reflectionSessions);
      for (const track of Object.keys(byTrack).sort(trackSort)) {
        pane.appendChild(el('div', {class: 'track-header'}, formatTrack(track)));
        for (const s of byTrack[track]) {
          pane.appendChild(renderSession(s, night));
        }
      }
    }

    // Themes (with clusters nested inside; ungrouped clusters listed at end if any)
    pane.appendChild(el('div', {class: 'section-title', id: `sec-${night}-themes`, 'data-section': `sec-${night}-themes`},
      `🏷 Themes (${stats.themes_total || 0} total · ${stats.themes_selected || 0} selected by Provocateur) — clusters nested inside`));
    const themes = Object.values(DATA.themes).filter(t => t.night === night)
      .sort((a, b) => (a.theme_id || '').localeCompare(b.theme_id || ''));
    for (const t of themes) {
      pane.appendChild(renderThemePhaseA(t, night));
    }
    // Orphan clusters (no theme) — surface at the end so they're not invisible
    const allClusters = Object.values(DATA.clusters).filter(c => c.night === night);
    const orphans = allClusters.filter(c => !c.theme_id);
    if (orphans.length) {
      pane.appendChild(el('div', {class: 'section-title', style: 'color: var(--muted);'},
        `🔗 Orphan clusters (${orphans.length}) — not grouped into any theme`));
      for (const c of orphans) {
        pane.appendChild(renderCluster(c, night, 'standalone'));
      }
    }
  } else {
    // ===== ASSEMBLY OUTPUT =====

    const themes = Object.values(DATA.themes).filter(t => t.night === night)
      .sort((a, b) => (a.theme_id || '').localeCompare(b.theme_id || ''));

    // Selected themes → voice responses + dossier (the deliberation chain)
    pane.appendChild(el('div', {class: 'section-title', id: `sec-${night}-selected`, 'data-section': `sec-${night}-selected`},
      `🎯 Selected themes → voice responses → dossier (${stats.themes_selected || 0} themes)`));
    const selectedThemes = themes.filter(t => t.selected_for_provocateur);
    for (const t of selectedThemes) {
      pane.appendChild(renderThemePhaseB(t, night));
    }

    // Voices' Artifacts (per-voice synthesis)
    pane.appendChild(el('div', {class: 'section-title', id: `sec-${night}-voices`, 'data-section': `sec-${night}-voices`},
      `🗣 Voices' Artifacts (${stats.voice_step2 || 0}) — per-voice synthesis across themes`));
    const step2s = Object.values(DATA.voice_step2).filter(s => s.night === night)
      .sort((a, b) => (a.voice_slug || '').localeCompare(b.voice_slug || ''));
    for (const s of step2s) {
      pane.appendChild(renderStep2(s, night));
    }

    // Dossiers (the editor's compositions)
    pane.appendChild(el('div', {class: 'section-title', id: `sec-${night}-dossiers`, 'data-section': `sec-${night}-dossiers`},
      `📰 Dossiers (${stats.dossiers || 0}) — the editor's compositions`));
    const dossiers = Object.values(DATA.dossiers).filter(d => d.night === night)
      .sort((a, b) => (a.dossier_num || '').localeCompare(b.dossier_num || ''));
    for (const d of dossiers) {
      pane.appendChild(renderDossier(d, night));
    }
  }
}

function renderThemePhaseA(t, night) {
  // Phase A: theme grouping clusters; selected/dropped marker
  const status = t.selected_for_provocateur ? '⭐ SELECTED' : '✗ dropped';
  const clusterIds = t.cluster_ids || [];
  const clusters = clusterIds.map(cid => DATA.clusters[cid]).filter(Boolean);
  const totalExtractions = clusters.reduce((sum, c) => sum + (c.extraction_ids || []).length, 0);
  const sessCount = themeSessionCount(t);
  const [d, body] = det(`"${t.title}" (${t.theme_id}) · ${clusters.length} cluster${clusters.length === 1 ? '' : 's'} · ${totalExtractions} extraction${totalExtractions === 1 ? '' : 's'} from ${sessCount} session${sessCount === 1 ? '' : 's'} · ${status}`);
  d.setAttribute('data-anchor', t.prefixed_id);
  body.appendChild(el('div', {class: 'id'}, t.prefixed_id));
  if (t.abstract) body.appendChild(abstract(t.abstract));
  // Sessions contributing to this theme — sorted by date_time so they appear in conference order
  const sessionIds = themeSessionIds(t);
  if (sessionIds.length) {
    sessionIds.sort((a, b) => {
      const sa = DATA.sessions[a], sb = DATA.sessions[b];
      return ((sa && sa.date_time) || '').localeCompare((sb && sb.date_time) || '');
    });
    const sWrap = el('div', {style: 'margin: 0.5rem 0;'},
      el('b', {}, `Sessions contributing to this theme (${sessionIds.length}):`));
    const ul = el('ul', {style: 'margin: 0.3rem 0; padding-left: 1.5rem;'});
    for (const sid of sessionIds) {
      const s = DATA.sessions[sid];
      if (s) {
        const li = el('li', {style: 'margin: 0.15rem 0;'});
        li.appendChild(jumpLink(`"${s.session_title}" (${s.venue || ''})`, sid));
        ul.appendChild(li);
      }
    }
    sWrap.appendChild(ul);
    body.appendChild(sWrap);
  }
  // Clusters nested inside the theme — full cluster view (extractions grouped by session)
  if (clusters.length) {
    body.appendChild(el('div', {class: 'meta', style: 'margin: 0.5rem 0; font-style: italic;'},
      `${clusters.length} cluster${clusters.length === 1 ? '' : 's'} below — each grouped by source session`));
    for (const c of clusters) {
      body.appendChild(renderCluster(c, night, 'theme'));
    }
  }
  return d;
}

function renderThemePhaseB(t, night) {
  // Phase B: selected theme as starting point of deliberation chain
  const [d, body] = det(`⭐ "${t.title}" (${t.theme_id})`);
  d.setAttribute('data-anchor', 'phase-b-' + t.prefixed_id);
  if (t.abstract) body.appendChild(abstract(t.abstract));
  // Provocateur annotations — rendered as readable content (not JSON)
  if (t.triage_flags) {
    const tf = t.triage_flags;
    const [tfd, tfb] = det('Provocateur triage flags');
    const yesNo = v => v === true ? 'Yes' : v === false ? 'No' : '—';
    tfb.appendChild(metaGrid([
      ['Worth surfacing', yesNo(tf.worth_surfacing)],
      ['Audience friction', tf.audience_friction || '—'],
      ['Fault line present', yesNo(tf.fault_line_present)],
    ]));
    if (tf.fault_line_description) {
      tfb.appendChild(el('div', {style: 'margin: 0.5rem 0; padding: 0.5rem 0.75rem; background: #f5f1e8; border-left: 3px solid var(--accent);'},
        el('b', {}, 'Fault line: '),
        tf.fault_line_description));
    }
    // Surface any fields not in the known set so nothing's lost silently
    const knownKeys = new Set(['theme_id', 'worth_surfacing', 'audience_friction', 'fault_line_present', 'fault_line_description']);
    const extras = Object.entries(tf).filter(([k]) => !knownKeys.has(k));
    if (extras.length) {
      const [ed, eb] = det('Other fields');
      eb.appendChild(el('pre', {class: 'json'}, JSON.stringify(Object.fromEntries(extras), null, 2)));
      tfb.appendChild(ed);
    }
    body.appendChild(tfd);
  }
  // Formulations (per voice on this theme)
  const formsForTheme = Object.values(DATA.formulations)
    .filter(f => f.theme_id === t.prefixed_id)
    .sort((a, b) => (a.voice_slug || '').localeCompare(b.voice_slug || ''));
  const [fSec, fBody] = det(`Formulations (${formsForTheme.length}) — one per voice that engaged this theme`);
  body.appendChild(fSec);
  for (const f of formsForTheme) {
    fBody.appendChild(renderFormulation(f, night));
  }
  // Dossier (if Tim composed one around this theme)
  const dossierForTheme = Object.values(DATA.dossiers).find(d => d.theme_id === t.prefixed_id);
  if (dossierForTheme) {
    body.appendChild(el('div', {class: 'panel', style: 'margin: 0.5rem 0;'},
      el('b', {}, '📰 The editor composed a dossier around this theme: '),
      jumpLink('"' + (dossierForTheme.kicker || dossierForTheme.headline) + '" (' + dossierForTheme.dossier_num + ') ↓',
               dossierForTheme.dossier_id)));
  } else {
    body.appendChild(el('div', {class: 'meta', style: 'font-style: italic;'},
      'No dossier composed around this theme (the editor picked other selected themes for the 5/5/3 published).'));
  }
  return d;
}

function renderCluster(c, night, context) {
  // context: 'standalone' (default) | 'theme' (nested inside theme — skip theme backlink)
  context = context || 'standalone';
  const extCount = (c.extraction_ids || []).length;
  const sessCount = clusterSessionCount(c);
  const [d, body] = det(`"${c.cluster_title}" (${c.cluster_id}) — ${extCount} extractions from ${sessCount} session${sessCount === 1 ? '' : 's'}`);
  d.setAttribute('data-anchor', c.prefixed_id);
  body.appendChild(el('div', {class: 'id'}, c.prefixed_id));
  if (c.cluster_abstract) body.appendChild(abstract(c.cluster_abstract));
  // Theme backlink — only when standalone (e.g. orphan cluster); skip when nested inside theme view
  if (c.theme_id && context !== 'theme') {
    const t = DATA.themes[c.theme_id];
    body.appendChild(el('div', {},
      el('span', {class: 'backlink'},
        '↑ Belongs to theme: ',
        jumpLink(`"${(t && t.title) || ''}" (${(t && t.theme_id) || c.theme_id})${t && t.selected_for_provocateur ? ' ⭐' : ''}`,
                 c.theme_id))));
  }
  // Extractions grouped by session
  const allExt = (c.extraction_ids || []).map(eid => DATA.extractions[eid]).filter(Boolean);
  const bySession = groupExtractionsBy(allExt, e => e.session_id || '_no_session');
  const [eSec, eBody] = det(`Extractions, grouped by session (${extCount} total across ${bySession.size} session${bySession.size === 1 ? '' : 's'})`);
  body.appendChild(eSec);
  // Sort sessions by date_time
  const sortedSessionIds = [...bySession.keys()].sort((a, b) => {
    const sa = DATA.sessions[a], sb = DATA.sessions[b];
    return ((sa && sa.date_time) || '').localeCompare((sb && sb.date_time) || '');
  });
  for (const sid of sortedSessionIds) {
    const s = DATA.sessions[sid];
    const exts = bySession.get(sid);
    const sessionTitle = s ? `"${s.session_title}" (${s.venue || ''})` : sid;
    const [sd, sb] = det(`From session: ${sessionTitle} — ${exts.length} extraction${exts.length === 1 ? '' : 's'}`);
    sb.appendChild(el('div', {class: 'meta'},
      '↗ ', jumpLink('Open this session in Sessions section ↑', sid)));
    // Hide cluster link always (we're in the cluster); also hide theme if cluster is nested in theme
    const hide = context === 'theme' ? ['cluster', 'theme'] : 'cluster';
    for (const e of exts) {
      sb.appendChild(renderExtraction(e, night, hide));
    }
    eBody.appendChild(sd);
  }
  return d;
}

// Count how many distinct sessions contributed extractions to a cluster
function clusterSessionCount(c) {
  const sids = new Set();
  for (const eid of c.extraction_ids || []) {
    const e = DATA.extractions[eid];
    if (e && e.session_id) sids.add(e.session_id);
  }
  return sids.size;
}
function clusterSessionIds(c) {
  const sids = new Set();
  for (const eid of c.extraction_ids || []) {
    const e = DATA.extractions[eid];
    if (e && e.session_id) sids.add(e.session_id);
  }
  return [...sids];
}
function themeSessionCount(t) {
  return themeSessionIds(t).length;
}
function themeSessionIds(t) {
  const sids = new Set();
  for (const cid of t.cluster_ids || []) {
    const c = DATA.clusters[cid];
    if (!c) continue;
    for (const eid of c.extraction_ids || []) {
      const e = DATA.extractions[eid];
      if (e && e.session_id) sids.add(e.session_id);
    }
  }
  return [...sids];
}

// Group extractions by a key extractor
function groupExtractionsBy(extractions, keyFn) {
  const groups = new Map();
  for (const e of extractions) {
    const k = keyFn(e);
    if (!groups.has(k)) groups.set(k, []);
    groups.get(k).push(e);
  }
  return groups;
}

// hide: which parent-context links to hide. String ('session', 'cluster', 'theme')
// or array (['cluster', 'theme'] for cluster-nested-in-theme).
function renderExtraction(e, night, hide) {
  if (!Array.isArray(hide)) hide = [hide || 'session'];
  const cluster = e.cluster_id ? DATA.clusters[e.cluster_id] : null;
  const theme = cluster && cluster.theme_id ? DATA.themes[cluster.theme_id] : null;
  const session = e.session_id ? DATA.sessions[e.session_id] : null;
  // Summary: lens tag + speaker + the extraction itself
  const d = document.createElement('details');
  d.className = 'extraction';
  const summary = document.createElement('summary');
  if (e.lens) summary.appendChild(el('i', {class: 'lens'}, e.lens));
  if (e.speaker) {
    summary.appendChild(el('b', {class: 'speaker'}, e.speaker));
    summary.appendChild(document.createTextNode(' · '));
  }
  summary.appendChild(document.createTextNode(e.extraction || '(no extraction text)'));
  d.appendChild(summary);
  const body = el('div', {class: 'body'});
  d.appendChild(body);
  d.setAttribute('data-anchor', e.extraction_id);
  // Forward links — hide the link(s) pointing back to current parent context(s)
  const links = el('div', {style: 'margin: 0.4rem 0;'});
  if (cluster && !hide.includes('cluster')) {
    links.appendChild(el('span', {class: 'backlink'},
      '→ Part of cluster: ',
      jumpLink(`"${cluster.cluster_title}" (${cluster.cluster_id})`, cluster.prefixed_id)));
    links.appendChild(document.createTextNode(' '));
  }
  if (theme && !hide.includes('theme')) {
    links.appendChild(el('span', {class: 'backlink'},
      '→ In theme: ',
      jumpLink(`"${theme.title}" (${theme.theme_id})${theme.selected_for_provocateur ? ' ⭐' : ''}`,
               theme.prefixed_id)));
    links.appendChild(document.createTextNode(' '));
  }
  if (session && !hide.includes('session')) {
    links.appendChild(el('span', {class: 'backlink'},
      '→ From session: ',
      jumpLink(`"${session.session_title}" (${session.venue || ''})`, session.session_id)));
  }
  body.appendChild(links);
  // Metadata
  body.appendChild(metaGrid([
    ['Extraction ID', e.extraction_id],
    ['Session', e.session_title],
    ['Speaker', e.speaker],
    ['Lens', e.lens],
    ['Energy', e.energy],
    ['Engagement', e.engagement || '—'],
    ['Responds to', e.responds_to || '—'],
  ]));
  if (e.context) {
    const [cd, cb] = det('Context (surrounding turn text)');
    cb.appendChild(el('div', {class: 'turn-text'}, e.context));
    body.appendChild(cd);
  }
  return d;
}

function renderFormulation(f, night) {
  const [d, body] = det(`${formatVoiceName(f.voice_slug)} × "${f.theme_display_title || ''}" (${f.theme_id_raw})`);
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
    const [s1d, s1b] = det(`Private thinking (${(s1.detailed_response || '').length.toLocaleString()} chars)`);
    body.appendChild(s1d);
    s1b.appendChild(renderStep1Body(s1));
  }
  // Step 2 — only show inline when THIS formulation's theme was the voice's primary focus;
  // otherwise the chain stops at Step 1 (Step 2 is reachable via Voices section).
  const step2Id = `${night}/${f.voice_slug}`;
  const s2 = DATA.voice_step2[step2Id];
  if (s2) {
    const primaryTheme = (s2.lineage || {}).primary_theme_id;
    const isPrimary = primaryTheme === f.theme_id_raw;
    if (isPrimary) {
      const sumTxt = `★ ${formatVoiceName(s2.voice_slug)} chose this theme — ${formatArtifactSummary(s2)}`;
      const s2d = document.createElement('details');
      const s2sum = document.createElement('summary');
      s2sum.textContent = sumTxt;
      s2d.appendChild(s2sum);
      const s2b = el('div', {class: 'body'});
      s2d.appendChild(s2b);
      // Lazy-render on first expand
      let rendered = false;
      s2d.addEventListener('toggle', () => {
        if (s2d.open && !rendered) {
          s2b.appendChild(el('div', {class: 'meta', style: 'margin-bottom: 0.5rem;'},
            '↗ ', jumpLink('Open in Voices section ↓', step2Id)));
          s2b.appendChild(renderStep2Body(s2, night));
          rendered = true;
        }
      });
      body.appendChild(s2d);
    } else if (primaryTheme) {
      // Voice didn't pick this theme — small breadcrumb to where they went
      body.appendChild(el('div', {class: 'meta', style: 'margin-top: 0.5rem; font-style: italic; color: var(--muted);'},
        `(${formatVoiceName(s2.voice_slug)}'s artifact went to ${primaryTheme} — see Voices' Artifacts section)`));
    }
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
  const sumTxt = formatArtifactSummary(s);
  const [d, body] = det(sumTxt);
  d.setAttribute('data-anchor', s.step2_id);
  body.appendChild(renderStep2Body(s, night));
  return d;
}

// Readable validation + operator-decision renderers
function verdictLabel(v) {
  if (!v) return el('span', {class: 'meta'}, '—');
  const lower = String(v).toLowerCase();
  const cls = lower === 'pass' ? 'pass' : lower === 'hold' ? 'hold' : 'warn';
  return label(v, cls);
}
function renderFlagsList(flags, labelName) {
  if (!flags || !Array.isArray(flags) || !flags.length) return null;
  const [d, b] = det(`${labelName} — ${flags.length} flagged`);
  for (const f of flags) {
    const item = el('div', {style: 'margin: 0.5rem 0; padding: 0.5rem 0.75rem; background: #fdeeee; border-left: 3px solid #c44;'});
    if (f.text) {
      item.appendChild(el('div', {}, el('b', {}, 'Flagged text: '), '"', f.text, '"'));
    }
    if (f.rule_cited) {
      item.appendChild(el('div', {class: 'meta', style: 'margin-top: 0.3rem;'},
        el('b', {}, 'Rule cited: '), f.rule_cited));
    }
    // catch any other fields
    for (const [k, v] of Object.entries(f)) {
      if (k !== 'text' && k !== 'rule_cited') {
        item.appendChild(el('div', {class: 'meta', style: 'margin-top: 0.2rem;'},
          el('b', {}, k + ': '), typeof v === 'string' ? v : JSON.stringify(v)));
      }
    }
    b.appendChild(item);
  }
  return d;
}
function renderCallMeta(call) {
  if (!call) return null;
  return el('div', {class: 'meta', style: 'margin-top: 0.5rem; color: var(--muted);'},
    `Validator call: ${call.model || ''} · ${call.input_tokens || 0}→${call.output_tokens || 0} tokens · ${call.wall_clock_s || 0}s`);
}
function renderValidation(v) {
  if (!v) return null;
  const wrap = el('div');
  // Top-level summary
  const top = el('div', {style: 'margin: 0.3rem 0 0.75rem;'});
  if (v.overall_verdict) {
    top.appendChild(el('b', {}, 'Overall verdict: '));
    top.appendChild(verdictLabel(v.overall_verdict));
  }
  if (v.operator_recommendation) {
    top.appendChild(document.createTextNode('  '));
    top.appendChild(el('b', {}, 'Recommendation: '));
    top.appendChild(el('span', {style: 'font-family: var(--mono);'}, v.operator_recommendation));
  }
  wrap.appendChild(top);
  // Safeguards
  if (v.safeguards) {
    const sg = v.safeguards;
    const [sd, sb] = det('Safeguards check');
    sb.appendChild(el('div', {}, el('b', {}, 'Verdict: '), verdictLabel(sg.verdict)));
    const flagCategories = [
      ['hard_limits_breach', 'Hard limits breach'],
      ['banned_modes_slip', 'Banned modes slip'],
      ['banned_language_ai_slop', 'Banned language / AI slop'],
      ['first_person_presence_leak', 'First-person presence leak'],
      ['ai_self_acknowledgment', 'AI self-acknowledgment'],
      ['defamation_risk', 'Defamation risk'],
      ['topics_requiring_care_breach', 'Topics-requiring-care breach'],
    ];
    for (const [key, lbl] of flagCategories) {
      const fl = sg[key];
      if (Array.isArray(fl) && fl.length) {
        const r = renderFlagsList(fl, lbl);
        if (r) sb.appendChild(r);
      } else if (fl == null || (Array.isArray(fl) && fl.length === 0)) {
        sb.appendChild(el('div', {class: 'meta'}, `✓ ${lbl}: clean`));
      } else {
        // Unexpected shape — show inline
        sb.appendChild(el('div', {class: 'meta'}, `${lbl}: `, JSON.stringify(fl)));
      }
    }
    const cm = renderCallMeta(sg._call);
    if (cm) sb.appendChild(cm);
    wrap.appendChild(sd);
  }
  // Engagement
  if (v.engagement) {
    const eg = v.engagement;
    const [ed, eb] = det('Engagement check');
    eb.appendChild(el('div', {}, el('b', {}, 'Verdict: '), verdictLabel(eg.verdict)));
    const checks = ['form_fidelity', 'grounding_fidelity', 'length_compliance'];
    for (const key of checks) {
      const c = eg[key];
      if (c == null) {
        eb.appendChild(el('div', {class: 'meta'}, `✓ ${key}: clean`));
      } else if (typeof c === 'object') {
        const [cd, cb] = det(key);
        for (const [k, val] of Object.entries(c)) {
          cb.appendChild(el('div', {class: 'meta', style: 'margin: 0.3rem 0;'},
            el('b', {}, k + ': '),
            typeof val === 'string' ? val : JSON.stringify(val)));
        }
        eb.appendChild(cd);
      } else {
        eb.appendChild(el('div', {class: 'meta'}, `${key}: `, String(c)));
      }
    }
    const cm = renderCallMeta(eg._call);
    if (cm) eb.appendChild(cm);
    wrap.appendChild(ed);
  }
  // Voice fidelity
  if (v.voice_fidelity) {
    const vf = v.voice_fidelity;
    const [vfd, vfb] = det('Voice fidelity check');
    vfb.appendChild(el('div', {}, el('b', {}, 'Verdict: '), verdictLabel(vf.verdict)));
    if (Array.isArray(vf.characteristic_moves_performed) && vf.characteristic_moves_performed.length) {
      const [md, mb] = det(`Characteristic moves performed (${vf.characteristic_moves_performed.length})`);
      const ul = el('ul', {style: 'margin: 0.3rem 0; padding-left: 1.5rem;'});
      for (const m of vf.characteristic_moves_performed) {
        ul.appendChild(el('li', {style: 'margin: 0.15rem 0;'}, typeof m === 'string' ? m : JSON.stringify(m)));
      }
      mb.appendChild(ul);
      vfb.appendChild(md);
    }
    if (Array.isArray(vf.quality_criteria_results) && vf.quality_criteria_results.length) {
      const [qd, qb] = det(`Quality criteria results (${vf.quality_criteria_results.length})`);
      for (const q of vf.quality_criteria_results) {
        if (q && typeof q === 'object') {
          const item = el('div', {style: 'margin: 0.5rem 0; padding: 0.5rem 0.75rem; background: #f5f1e8; border-left: 3px solid var(--accent);'});
          for (const [k, val] of Object.entries(q)) {
            item.appendChild(el('div', {class: 'meta', style: 'margin: 0.2rem 0;'},
              el('b', {}, k + ': '),
              typeof val === 'string' ? val : JSON.stringify(val)));
          }
          qb.appendChild(item);
        } else {
          qb.appendChild(el('div', {}, String(q)));
        }
      }
      vfb.appendChild(qd);
    }
    const cm = renderCallMeta(vf._call);
    if (cm) vfb.appendChild(cm);
    wrap.appendChild(vfd);
  }
  // Cross-night echo
  if (v.cross_night_echo) {
    wrap.appendChild(el('div', {class: 'meta', style: 'margin: 0.5rem 0;'},
      el('b', {}, 'Cross-night echo: '),
      typeof v.cross_night_echo === 'string' ? v.cross_night_echo : JSON.stringify(v.cross_night_echo)));
  }
  if (v.wall_clock_s) {
    wrap.appendChild(el('div', {class: 'meta', style: 'color: var(--muted);'},
      `Total validation wall clock: ${v.wall_clock_s}s`));
  }
  return wrap;
}
function renderOperatorDecision(od) {
  if (!od) return null;
  const wrap = el('div');
  const decision = od.decision || '';
  const cls = decision === 'release' ? 'released' : decision === 'hold' ? 'hold' : '';
  wrap.appendChild(el('div', {style: 'margin: 0.3rem 0 0.5rem;'},
    el('b', {}, 'Decision: '),
    label(decision || '—', cls)));
  wrap.appendChild(metaGrid([
    ['Decided at', od.decided_at],
    ['Decided by', od.decided_by],
  ]));
  // any other fields
  const known = new Set(['voice_slug', 'night', 'decision', 'decided_at', 'decided_by']);
  const extras = Object.entries(od).filter(([k]) => !known.has(k));
  for (const [k, v] of extras) {
    wrap.appendChild(el('div', {class: 'meta'}, el('b', {}, k + ': '),
      typeof v === 'string' ? v : JSON.stringify(v)));
  }
  return wrap;
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
    const [vd, vb] = det('Validation — full flag detail (Safeguards / Engagement / Voice fidelity)');
    vb.appendChild(renderValidation(s.validation));
    wrap.appendChild(vd);
  }
  if (s.operator_decision) {
    const [od, ob] = det('Operator decision');
    ob.appendChild(renderOperatorDecision(s.operator_decision));
    wrap.appendChild(od);
  }
  // Source step1s — items may be strings (legacy) or objects {theme_id, formulation_id, path}
  const lineage = s.lineage || {};
  if (lineage.consumed_detailed_responses && lineage.consumed_detailed_responses.length) {
    const [ld, lb] = det(`Source private-thinking responses consumed (${lineage.consumed_detailed_responses.length})`);
    for (const item of lineage.consumed_detailed_responses) {
      let path, themeId;
      if (typeof item === 'string') {
        path = item;
      } else if (item && typeof item === 'object') {
        path = item.path || '';
        themeId = item.theme_id;
      } else {
        continue;
      }
      const filename = (path || '').split('/').pop().replace('.json', '') || '(unknown)';
      const step1Id = `${night}/${filename}`;
      const labelTxt = themeId ? `→ ${filename} (theme: ${themeId})` : `→ ${filename}`;
      lb.appendChild(el('div', {style: 'margin: 0.2rem 0;'}, jumpLink(labelTxt, step1Id)));
    }
    wrap.appendChild(ld);
  }
  return wrap;
}

function renderDossier(d, night) {
  const [dEl, body] = det(`"${d.kicker || ''}" (${d.dossier_num}) — ${d.headline || ''}`);
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
  // Count extractions from this session
  const sessionExtractions = Object.values(DATA.extractions)
    .filter(e => e.session_id === s.session_id);
  // Time portion of date_time (HH:MM)
  let timeStr = '';
  if (s.date_time) {
    const m = s.date_time.match(/T(\d{2}:\d{2})/);
    if (m) timeStr = m[1];
  }
  // Detect split-audio captures
  const sid = s.session_id || '';
  const splitNote = sid.endsWith('__audio2') ? ' (capture 2 — split-audio companion)'
                  : sid.endsWith('__audio') ? ' (capture 1 of split-audio pair)' : '';
  const titlePart = s.session_title || sid;
  const venuePart = s.venue ? ` — ${s.venue}${timeStr ? ', ' + timeStr : ''}` : '';
  const statsPart = ` · ${s.turn_count || 0} turns · ${sessionExtractions.length} extractions`;
  const summary = `${titlePart}${venuePart}${splitNote}${statsPart}`;
  const [d, body] = det(summary);
  d.setAttribute('data-anchor', s.session_id);
  body.appendChild(metaGrid([
    ['Track', s.track],
    ['Venue', s.venue],
    ['Date/time', s.date_time],
    ['Format', s.session_format],
    ['Source', s.source || (s.is_reflection ? 'vendor' : 'audio')],
    ['Reflection?', s.is_reflection ? 'Yes' : 'No'],
    ['Turn count', s.turn_count],
    ['Word count', (s.word_count || 0).toLocaleString()],
  ]));
  if (s.session_description) {
    body.appendChild(el('div', {class: 'meta'}, el('b', {}, 'Description: '), s.session_description));
  }
  // Roster (speakers + bios)
  if (s.roster && s.roster.length) {
    const [rd, rb] = det(`Roster (${s.roster.length} speakers + bios)`);
    for (const sp of s.roster) {
      rb.appendChild(el('div', {class: 'meta', style: 'margin: 0.5rem 0;'},
        el('b', {}, sp.name || ''),
        sp.title ? ' — ' + sp.title : '',
        sp.affiliation ? ' (' + sp.affiliation + ')' : '',
        sp.bio ? el('div', {class: 'meta', style: 'margin-top: 0.2rem; color: #888;'}, sp.bio) : null));
    }
    body.appendChild(rd);
  }
  // Extractions from THIS session — the main click-into-clusters path
  if (sessionExtractions.length) {
    const [ed, eb] = det(`Extractions from this session (${sessionExtractions.length}) — click each to see which cluster + theme it led to`);
    for (const ext of sessionExtractions) {
      eb.appendChild(renderExtraction(ext, night));
    }
    body.appendChild(ed);
  }
  // Full transcript (collapsed deeper)
  if (s.turns && s.turns.length) {
    const [td, tb] = det(`Full transcript (${s.turns.length} turns)`);
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
    row.appendChild(el('b', {}, formatVoiceName(slug)));
    for (const n of ['night_1', 'night_2', 'night_3']) {
      const s2id = `${n}/${slug}`;
      const exists = DATA.voice_step2[s2id];
      const link = el('a', {class: 'jump-link', href: '#', style: 'margin-left: 0.5rem;'}, n.replace('night_', 'N'));
      if (exists) {
        link.addEventListener('click', e => {
          e.preventDefault();
          showPage(`${n}_assembly`);
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

// Sticky sub-nav: highlight current section as user scrolls
function setupSectionObserver() {
  const sections = document.querySelectorAll('[data-section]');
  if (!sections.length) return;
  let lastActive = null;
  const observer = new IntersectionObserver((entries) => {
    // Find the topmost section currently in view
    const inView = entries.filter(e => e.isIntersecting)
      .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top);
    if (!inView.length) return;
    const top = inView[0].target;
    const targetId = top.id;
    if (targetId === lastActive) return;
    lastActive = targetId;
    // Update all sub-navs (each night has its own); only the visible one matters
    document.querySelectorAll('.sub-nav a').forEach(a => {
      if (a.dataset.target === targetId) a.classList.add('active');
      else a.classList.remove('active');
    });
  }, {
    root: null,
    rootMargin: '-120px 0px -55% 0px',  // section is "active" when between ~120px from top and ~45% down
    threshold: 0,
  });
  sections.forEach(s => observer.observe(s));
}
setupSectionObserver();

// Initial active state for night_1 Conference Data (the first sub-nav link)
const initialFirstLink = document.querySelector('#night_1_conf .sub-nav a.section-link');
if (initialFirstLink) initialFirstLink.classList.add('active');
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
