"""C33: publish_flow dossier index + lineage extension.

Tests the per-night dossier index, cross-night dossier index, and the
voice → editor → dossier lineage edges. No real Anthropic calls — pure
file-shape transforms over seeded run_dirs.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_RUNTIME = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_RUNTIME))

from flows.shared.io import write_json_atomic  # noqa: E402
from flows.publish_flow import (  # noqa: E402
    _build_cross_night_dossier_index,
    _build_lineage_graph,
    _build_per_night_dossier_index,
    _load_theme_routing,
)


# --- Fixture builders --------------------------------------------------

def _theme_routing(night: int = 1) -> dict:
    return {
        "schema_version": "1.0",
        "night": night,
        "athens_base_issue": 42193,
        "issue_no": 42193,
        "vol": "CXVI",
        "themes_to_dossiers": [
            {
                "theme_id": "theme_001",
                "dossier_no": 1,
                "theme_title": "First theme",
                "n_engaged_voices": 2,
            },
            {
                "theme_id": "theme_002",
                "dossier_no": 2,
                "theme_title": "Second theme",
                "n_engaged_voices": 1,
            },
        ],
        "voices_routing": [
            {
                "voice_slug": "plato",
                "voice_name": "Plato",
                "primary_theme": "theme_001",
                "primary_dossier": 1,
                "focus_decision_parsed": "Focus on Response 1",
                "primary_theme_source": "Case 1",
            },
            {
                "voice_slug": "cleopatra",
                "voice_name": "Cleopatra",
                "primary_theme": "theme_001",
                "primary_dossier": 1,
                "focus_decision_parsed": "Focus on Response 1",
                "primary_theme_source": "Case 1",
            },
            {
                "voice_slug": "dostoevsky",
                "voice_name": "Dostoevsky",
                "primary_theme": "theme_002",
                "primary_dossier": 2,
                "focus_decision_parsed": "Focus on Response 2",
                "primary_theme_source": "Case 1",
            },
        ],
        "refusals": [],
        "dossier_lead_order_default": [1, 2],
    }


def _dossier(
    no: int,
    theme_id: str,
    title: str,
    *,
    headnote_count: int = 2,
    night: int = 1,
    headnotes: list[dict] | None = None,
) -> dict:
    """Build a fixture dossier. If `headnotes` is passed, use those
    verbatim (lets tests inject voice_slug + formulation_text + etc.);
    otherwise build minimal placeholders by `headnote_count`."""
    if headnotes is None:
        headnotes = [{"voice_slug": f"v{i}"} for i in range(headnote_count)]
    return {
        "schema_version": "2.0",
        "kicker": f"Kicker for {theme_id}",
        "headline": title,
        "subline": "subline goes here",
        "body_paragraphs": ["body paragraph one", "body paragraph two"],
        "headnotes": headnotes,
        "front_abstract": "front abstract",
        "colophon": {"editor": "Claudia Pinchbeck"},
        "metadata": {
            "theme_id": theme_id,
            "theme_display_title": title,
            "night": night,
            "issue_no": 42192 + night,
            "vol": "CXVI",
            "publication_date": f"2026-05-{6 + night:02d}",
            "publication_date_long": f"May {6 + night}, 2026",
            "edition_label": f"Night {night}",
            "generated_by": "tim_leberecht",
            "model": "claude-opus-4-7",
            "thinking_enabled": True,
        },
    }


def _seed_dossiers_for_night(
    project_root: Path,
    night: int,
    dossier_specs: list[tuple[int, str, str]],
) -> Path:
    """Seed published_artifacts/dossiers/night_<N>/ with dossier_NNN.json files.

    Returns the night directory.
    """
    out_dir = project_root / "published_artifacts" / "dossiers" / f"night_{night}"
    out_dir.mkdir(parents=True, exist_ok=True)
    for no, theme_id, title in dossier_specs:
        write_json_atomic(out_dir / f"dossier_{no:03d}.json", _dossier(no, theme_id, title, night=night))
    return out_dir


def _seed_run_dir_with_routing(tmp_path: Path, night: int = 1) -> Path:
    run_dir = tmp_path / "run"
    editor_dir = run_dir / "05_editor"
    editor_dir.mkdir(parents=True, exist_ok=True)
    write_json_atomic(editor_dir / "theme_routing.json", _theme_routing(night))
    return run_dir


# --- Per-night dossier index ------------------------------------------

class TestPerNightDossierIndex:
    def test_no_dossiers_returns_zero(self, tmp_path):
        run_dir = _seed_run_dir_with_routing(tmp_path)
        project_root = tmp_path / "project"
        result = _build_per_night_dossier_index(run_dir, 1, project_root)
        assert result["dossier_count"] == 0
        assert result["index_path"] is None

    def test_with_dossiers_builds_index(self, tmp_path):
        run_dir = _seed_run_dir_with_routing(tmp_path)
        project_root = tmp_path / "project"
        _seed_dossiers_for_night(
            project_root, 1, [(1, "theme_001", "First"), (2, "theme_002", "Second")]
        )
        result = _build_per_night_dossier_index(run_dir, 1, project_root)
        assert result["dossier_count"] == 2
        index = json.loads(Path(result["index_path"]).read_text())
        assert index["night"] == 1
        assert len(index["dossiers"]) == 2
        first = index["dossiers"][0]
        assert first["dossier_no"] == 1
        assert first["filename"] == "dossier_001.json"
        assert first["theme_id"] == "theme_001"
        assert first["url_path"] == "/dossiers/night-1/dossier_001"
        # B3-placeholder field provisioned (filled by edition_flow when shipped).
        assert "edition_lead" in index
        assert index["edition_lead"] is None

    def test_voices_in_night_block(self, tmp_path):
        """Per-night index carries a voices_in_night dict keyed by voice_slug,
        so the microsite can render per-voice navigation from one file (no
        themes/ walk needed). Each entry points back at the dossier the
        voice's artifact lives in.
        """
        run_dir = _seed_run_dir_with_routing(tmp_path)
        project_root = tmp_path / "project"
        out_dir = project_root / "published_artifacts" / "dossiers" / "night_1"
        out_dir.mkdir(parents=True)
        # Two dossiers; each has voice headnotes with the runtime-stamped
        # fields the voices_in_night block reads from.
        write_json_atomic(
            out_dir / "dossier_001.json",
            _dossier(1, "theme_001", "First", headnotes=[
                {"voice_slug": "cleopatra",
                 "voice_name": "the voice of Cleopatra",
                 "artifact_title": "A PROSTAGMA",
                 "framing_text": "Cleopatra issues an ordinance.",
                 "artifact_form": "prostagma",
                 "artifact_text": "[full body — γινέσθωι]",
                 "formulation_text": "Cleopatra's briefing for theme_001"},
                {"voice_slug": "ibn_battuta",
                 "voice_name": "the voice of Ibn Battuta",
                 "artifact_title": "A HALT",
                 "framing_text": "Battuta dictates a halt.",
                 "artifact_form": "rihla",
                 "artifact_text": "[full body]",
                 "formulation_text": "Battuta's briefing for theme_001"},
            ]),
        )
        write_json_atomic(
            out_dir / "dossier_002.json",
            _dossier(2, "theme_002", "Second", headnotes=[
                {"voice_slug": "dostoevsky",
                 "voice_name": "the voice of Dostoevsky",
                 "artifact_title": "A LETTER",
                 "framing_text": "Dostoevsky writes a Diary entry.",
                 "artifact_form": "diary_entry",
                 "artifact_text": "[full body]",
                 "formulation_text": "Dostoevsky's briefing for theme_002"},
            ]),
        )
        result = _build_per_night_dossier_index(run_dir, 1, project_root)
        index = json.loads(Path(result["index_path"]).read_text())
        assert "voices_in_night" in index
        v = index["voices_in_night"]
        assert set(v.keys()) == {"cleopatra", "ibn_battuta", "dostoevsky"}
        # Cleopatra → dossier_001, theme_001
        assert v["cleopatra"]["primary_dossier_no"] == 1
        assert v["cleopatra"]["primary_theme_id"] == "theme_001"
        assert v["cleopatra"]["url_path"] == "/dossiers/night-1/dossier_001"
        assert v["cleopatra"]["primary_formulation"] == "Cleopatra's briefing for theme_001"
        assert v["cleopatra"]["artifact_form"] == "prostagma"
        # Dostoevsky → dossier_002, theme_002
        assert v["dostoevsky"]["primary_dossier_no"] == 2
        assert v["dostoevsky"]["primary_theme_id"] == "theme_002"
        assert v["dostoevsky"]["url_path"] == "/dossiers/night-1/dossier_002"

    def test_voices_in_night_empty_when_no_headnote_voice_slugs(self, tmp_path):
        """If the dossier headnotes have no voice_slug fields, the
        voices_in_night dict is empty (no crash)."""
        run_dir = _seed_run_dir_with_routing(tmp_path)
        project_root = tmp_path / "project"
        out_dir = project_root / "published_artifacts" / "dossiers" / "night_1"
        out_dir.mkdir(parents=True)
        write_json_atomic(
            out_dir / "dossier_001.json",
            _dossier(1, "theme_001", "First", headnotes=[
                {"artifact_title": "no slug here"},  # missing voice_slug
            ]),
        )
        result = _build_per_night_dossier_index(run_dir, 1, project_root)
        index = json.loads(Path(result["index_path"]).read_text())
        assert index["voices_in_night"] == {}

    def test_cross_night_index_has_editions_by_night_placeholder(self, tmp_path):
        project_root = tmp_path / "project"
        _seed_dossiers_for_night(project_root, 1, [(1, "theme_001", "N1 First")])
        result = _build_cross_night_dossier_index(project_root)
        index = json.loads(Path(result["index_path"]).read_text())
        # B3-placeholder field provisioned (filled by edition_flow when shipped).
        assert "editions_by_night" in index
        assert index["editions_by_night"] == {}

    def test_voices_routed_from_theme_routing(self, tmp_path):
        run_dir = _seed_run_dir_with_routing(tmp_path)
        project_root = tmp_path / "project"
        _seed_dossiers_for_night(
            project_root, 1, [(1, "theme_001", "First"), (2, "theme_002", "Second")]
        )
        result = _build_per_night_dossier_index(run_dir, 1, project_root)
        index = json.loads(Path(result["index_path"]).read_text())
        d1 = next(d for d in index["dossiers"] if d["dossier_no"] == 1)
        d2 = next(d for d in index["dossiers"] if d["dossier_no"] == 2)
        assert d1["voice_count"] == 2
        assert sorted(v["voice_slug"] for v in d1["voices_routed"]) == ["cleopatra", "plato"]
        assert d2["voice_count"] == 1
        assert d2["voices_routed"][0]["voice_slug"] == "dostoevsky"

    def test_voice_count_falls_back_to_headnotes(self, tmp_path):
        # No theme_routing.json → voice_count comes from len(headnotes).
        run_dir = tmp_path / "run"
        run_dir.mkdir()  # no 05_editor subdir
        project_root = tmp_path / "project"
        _seed_dossiers_for_night(project_root, 1, [(1, "theme_001", "First")])
        # Override headnote count by re-writing the dossier with 5 headnotes.
        out = project_root / "published_artifacts" / "dossiers" / "night_1" / "dossier_001.json"
        write_json_atomic(out, _dossier(1, "theme_001", "First", headnote_count=5))
        result = _build_per_night_dossier_index(run_dir, 1, project_root)
        index = json.loads(Path(result["index_path"]).read_text())
        assert index["dossiers"][0]["voice_count"] == 5
        assert index["dossiers"][0]["voices_routed"] == []


# --- Cross-night dossier index ----------------------------------------

class TestCrossNightDossierIndex:
    def test_no_nights_returns_empty(self, tmp_path):
        project_root = tmp_path / "project"
        result = _build_cross_night_dossier_index(project_root)
        assert result["dossier_count"] == 0
        assert result["index_path"] is None
        assert result["nights_present"] == []

    def test_walks_multiple_nights(self, tmp_path):
        project_root = tmp_path / "project"
        _seed_dossiers_for_night(project_root, 1, [(1, "theme_001", "N1 First")])
        _seed_dossiers_for_night(
            project_root, 2, [(1, "theme_011", "N2 First"), (2, "theme_012", "N2 Second")]
        )
        result = _build_cross_night_dossier_index(project_root)
        assert result["dossier_count"] == 3
        assert result["nights_present"] == [1, 2]
        index = json.loads(Path(result["index_path"]).read_text())
        nights_in_dossiers = sorted({d["night"] for d in index["dossiers"]})
        assert nights_in_dossiers == [1, 2]
        # Dossiers are emitted in night-then-name order.
        assert index["dossiers"][0]["night"] == 1
        assert index["dossiers"][1]["night"] == 2
        assert index["dossiers"][2]["night"] == 2

    def test_idempotent(self, tmp_path):
        project_root = tmp_path / "project"
        _seed_dossiers_for_night(project_root, 1, [(1, "theme_001", "First")])
        first = _build_cross_night_dossier_index(project_root)
        second = _build_cross_night_dossier_index(project_root)
        assert first["dossier_count"] == second["dossier_count"]
        assert first["nights_present"] == second["nights_present"]


# --- Lineage graph extension to dossiers ------------------------------

def _published_voice(slug: str, *, themes: list[str]) -> dict:
    return {
        "voice_name": slug.title(),
        "voice_slug": slug,
        "night": 1,
        "url_path": f"/night-1/{slug}",
        "was_step3": False,
        "themes_addressed": themes,
        "artifact": {"title": f"{slug} title"},
        "deliberation": {"decision": "first_draft", "voices_read": [], "amendments": []},
    }


class TestLineageGraphDossierEdges:
    def test_no_routing_no_dossier_nodes(self, tmp_path):
        # When theme_routing.json is absent, no dossier nodes/edges added.
        run_dir = tmp_path / "run"
        run_dir.mkdir()
        project_root = tmp_path / "project"
        all_extractions = []
        grouping = {"themes": [{"theme_id": "theme_001", "title": "T1", "clusters": []}]}
        formulations = {}
        published_voices = {"plato": _published_voice("plato", themes=["theme_001"])}
        result = _build_lineage_graph(
            run_dir, 1, project_root,
            all_extractions, grouping, formulations, published_voices,
        )
        graph_path = project_root / "published_artifacts" / "traces" / "lineage_graph_night_1.json"
        graph = json.loads(graph_path.read_text())
        assert not any(n.get("type") == "dossier" for n in graph["nodes"].values())
        assert not any(e["rel"] == "routed_into" for e in graph["edges"])
        assert not any(e["rel"] == "composed_for" for e in graph["edges"])

    def test_routing_adds_dossier_nodes_and_edges(self, tmp_path):
        run_dir = _seed_run_dir_with_routing(tmp_path, night=1)
        project_root = tmp_path / "project"
        all_extractions = []
        grouping = {
            "themes": [
                {"theme_id": "theme_001", "title": "T1", "clusters": []},
                {"theme_id": "theme_002", "title": "T2", "clusters": []},
            ]
        }
        formulations = {}
        published_voices = {
            "plato": _published_voice("plato", themes=["theme_001"]),
            "cleopatra": _published_voice("cleopatra", themes=["theme_001"]),
            "dostoevsky": _published_voice("dostoevsky", themes=["theme_002"]),
        }
        _build_lineage_graph(
            run_dir, 1, project_root,
            all_extractions, grouping, formulations, published_voices,
        )
        graph_path = project_root / "published_artifacts" / "traces" / "lineage_graph_night_1.json"
        graph = json.loads(graph_path.read_text())

        # Two dossier nodes appear.
        dossier_nodes = {nid: n for nid, n in graph["nodes"].items() if n.get("type") == "dossier"}
        assert set(dossier_nodes.keys()) == {"dossier:1:001", "dossier:1:002"}
        assert dossier_nodes["dossier:1:001"]["theme_id"] == "theme_001"
        assert dossier_nodes["dossier:1:002"]["theme_id"] == "theme_002"

        # composed_for edges: theme → dossier (one per dossier).
        composed_for = [e for e in graph["edges"] if e["rel"] == "composed_for"]
        assert len(composed_for) == 2
        cf_pairs = {(e["from"], e["to"]) for e in composed_for}
        assert ("theme:theme_001", "dossier:1:001") in cf_pairs
        assert ("theme:theme_002", "dossier:1:002") in cf_pairs

        # routed_into edges: amended_artifact → dossier (one per voice in routing).
        routed = [e for e in graph["edges"] if e["rel"] == "routed_into"]
        assert len(routed) == 3
        r_pairs = {(e["from"], e["to"]) for e in routed}
        assert ("amended_artifact:plato", "dossier:1:001") in r_pairs
        assert ("amended_artifact:cleopatra", "dossier:1:001") in r_pairs
        assert ("amended_artifact:dostoevsky", "dossier:1:002") in r_pairs


class TestLoadThemeRouting:
    def test_missing_file_returns_none(self, tmp_path):
        assert _load_theme_routing(tmp_path) is None

    def test_present_file_loads(self, tmp_path):
        editor_dir = tmp_path / "05_editor"
        editor_dir.mkdir()
        write_json_atomic(editor_dir / "theme_routing.json", _theme_routing(1))
        loaded = _load_theme_routing(tmp_path)
        assert loaded is not None
        assert loaded["night"] == 1
        assert len(loaded["voices_routing"]) == 3
