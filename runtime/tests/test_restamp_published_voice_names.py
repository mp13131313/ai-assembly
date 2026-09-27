"""C53 published-record repair: scripts/restamp_published_voice_names.py."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_RUNTIME = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_RUNTIME / "scripts"))

import restamp_published_voice_names as rs  # noqa: E402

ADA_BAD = "I am Augusta Ada King, Countess of Lovelace — Byron's daughter"
OCTO_BAD = "I am octopus. The name is yours, not mine"


def _w(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _r(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture
def project(tmp_path: Path) -> Path:
    _w(tmp_path / "council_config.json", {"members": [
        {"name": "Voice of Ada Lovelace"},
        {"name": "Voice of the Octopus"},
        {"name": "Voice of Hannah Arendt"},
    ]})
    pa = tmp_path / "published_artifacts"
    _w(pa / "nights/night_1/ada_lovelace.json",
       {"voice_name": ADA_BAD, "voice_slug": "ada_lovelace", "artifact": {"text": "body"}})
    _w(pa / "nights/night_1/hannah_arendt.json",
       {"voice_name": "Hannah Arendt", "voice_slug": "hannah_arendt"})
    _w(pa / "nights/night_1/_index.json", {"voices": [
        {"voice_slug": "ada_lovelace", "voice_name": ADA_BAD, "title": "T"}]})
    _w(pa / "dossiers/night_1/dossier_001.json", {"headnotes": [
        {"voice_slug": "ada_lovelace", "voice_name": "the Voice of " + ADA_BAD},
        {"voice_slug": "octopus", "voice_name": "the Voice of " + OCTO_BAD},
        {"voice_slug": "hannah_arendt", "voice_name": "the Voice of Hannah Arendt"},
    ], "framing_text": "The Voice of Ada writes."})
    _w(pa / "dossiers/night_1/_index.json", {"dossiers": [{"voices_routed": [
        {"voice_slug": "octopus", "voice_name": OCTO_BAD}]}]})
    _w(pa / "_archive/old/ada_lovelace.json", {"voice_name": ADA_BAD, "voice_slug": "ada_lovelace"})
    _w(pa / "data_views/x.json", {"voice_name": ADA_BAD, "voice_slug": "ada_lovelace"})
    return tmp_path


def test_dry_run_reports_but_writes_nothing(project):
    before = _r(project / "published_artifacts/nights/night_1/ada_lovelace.json")
    n = rs.restamp(project, apply=False)
    assert n == 6  # ada page, hannah page, index, 2 headnotes, voices_routed
    assert _r(project / "published_artifacts/nights/night_1/ada_lovelace.json") == before


def test_apply_rewrites_to_fixed_code_output_and_is_idempotent(project):
    pa = project / "published_artifacts"
    rs.restamp(project, apply=True)

    assert _r(pa / "nights/night_1/ada_lovelace.json")["voice_name"] == "Voice of Ada Lovelace"
    assert _r(pa / "nights/night_1/ada_lovelace.json")["artifact"] == {"text": "body"}
    assert _r(pa / "nights/night_1/hannah_arendt.json")["voice_name"] == "Voice of Hannah Arendt"
    assert _r(pa / "nights/night_1/_index.json")["voices"][0]["voice_name"] == "Voice of Ada Lovelace"
    heads = _r(pa / "dossiers/night_1/dossier_001.json")
    assert [h["voice_name"] for h in heads["headnotes"]] == [
        "the Voice of Ada Lovelace", "the Voice of the Octopus", "the Voice of Hannah Arendt"]
    assert heads["framing_text"] == "The Voice of Ada writes."  # prose untouched
    routed = _r(pa / "dossiers/night_1/_index.json")["dossiers"][0]["voices_routed"][0]
    assert routed["voice_name"] == "Voice of the Octopus"

    # historical + derived dirs untouched
    assert _r(pa / "_archive/old/ada_lovelace.json")["voice_name"] == ADA_BAD
    assert _r(pa / "data_views/x.json")["voice_name"] == ADA_BAD

    assert rs.restamp(project, apply=True) == 0


def test_refuses_without_council_config(project):
    (project / "council_config.json").unlink()
    with pytest.raises(SystemExit):
        rs.restamp(project, apply=False)


def test_refuses_to_write_unresolved_slug(project):
    _w(project / "published_artifacts/nights/night_1/ghost.json",
       {"voice_name": "I am nobody", "voice_slug": "ghost"})
    with pytest.raises(SystemExit):
        rs.restamp(project, apply=True)
    # nothing written — the refusal happens before any write
    assert _r(project / "published_artifacts/nights/night_1/ada_lovelace.json")["voice_name"] == ADA_BAD


def test_incomplete_night_index_rebuilt_from_disk(project):
    """C50 symptom still in the published record: the Night 1/2 voice indexes
    list 3/10 and 1/10 voices. The repair rebuilds an incomplete index from
    the page files on disk, after restamping, so names come out corrected."""
    pa = project / "published_artifacts"
    # fixture index lists only ada; hannah's page is also on disk
    assert len(_r(pa / "nights/night_1/_index.json")["voices"]) == 1
    rs.restamp(project, apply=False)
    assert len(_r(pa / "nights/night_1/_index.json")["voices"]) == 1  # dry run: untouched

    rs.restamp(project, apply=True)
    index = _r(pa / "nights/night_1/_index.json")
    assert index["voice_count"] == 2
    assert {v["voice_slug"]: v["voice_name"] for v in index["voices"]} == {
        "ada_lovelace": "Voice of Ada Lovelace",
        "hannah_arendt": "Voice of Hannah Arendt",
    }
