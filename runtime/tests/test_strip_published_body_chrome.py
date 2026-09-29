"""C64 residual: strip the stray "**" from already-published dossier bodies."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts import strip_published_body_chrome as sb  # noqa: E402


def _dossier(tmp_path: Path, night: int, body: list[str]) -> Path:
    f = tmp_path / "published_artifacts" / "dossiers" / f"night_{night}" / "dossier_001.json"
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps({"kicker": "K", "body_paragraphs": body}, ensure_ascii=False))
    return f


def test_strips_only_the_leading_chrome_line(tmp_path):
    # The real shape: every Athens dossier body starts "**\n" then the lede.
    f = _dossier(tmp_path, 1, ["**\nAthens, late on the first night. The **bold** stays.", "* * *", "Second."])

    assert sb.run(tmp_path, apply=False) == [f]            # dry run reports
    assert json.loads(f.read_text())["body_paragraphs"][0].startswith("**\n")  # ...and writes nothing

    sb.run(tmp_path, apply=True)
    data = json.loads(f.read_text())
    assert data["body_paragraphs"] == ["Athens, late on the first night. The **bold** stays.", "* * *", "Second."]
    assert data["kicker"] == "K"
    assert sb.run(tmp_path, apply=False) == []             # idempotent


def test_leaves_clean_and_edge_bodies_alone(tmp_path):
    clean = _dossier(tmp_path, 2, ["Athens, the eighth of May.", "Two."])
    italic = _dossier(tmp_path, 3, ["*Athens*, an italic lede", "Two."])
    assert sb.run(tmp_path, apply=True) == []
    assert json.loads(clean.read_text())["body_paragraphs"][0] == "Athens, the eighth of May."
    assert json.loads(italic.read_text())["body_paragraphs"][0] == "*Athens*, an italic lede"


def test_a_chrome_only_first_paragraph_is_dropped(tmp_path):
    f = _dossier(tmp_path, 1, ["**\n", "First real paragraph."])
    sb.run(tmp_path, apply=True)
    assert json.loads(f.read_text())["body_paragraphs"] == ["First real paragraph."]
