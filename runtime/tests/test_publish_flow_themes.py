"""C51: per-theme files from the Researcher's current grouping shape."""
from __future__ import annotations

import json
import sys
from pathlib import Path

_RUNTIME = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_RUNTIME))

from flows.publish_flow import _build_per_theme_files  # noqa: E402

EXTRACTIONS = [
    {"id": "s1:001", "session": "S1", "speaker": "A. Speaker", "lens": "assertion",
     "extraction": "Democracy is a design problem.", "context": ""},
    {"id": "s2:004", "session": "S2", "speaker": None, "lens": "open_question",
     "extraction": "Who designs the designers?", "context": ""},
]
# Production shape: clusters embedded in the theme, no `cluster_ids` list.
GROUPING = {"themes": [{
    "theme_id": "theme_001", "title": "Design vs heritage", "abstract": "Binding.",
    "clusters": [{"cluster_id": "cluster_001", "cluster_title": "C",
                  "cluster_abstract": "Why together.", "extraction_ids": ["s1:001", "s2:004"]}],
}]}


def test_embedded_clusters_resolve(tmp_path):
    written = _build_per_theme_files(
        tmp_path / "run", 1, tmp_path, EXTRACTIONS, GROUPING, {}, {}, {})
    assert written == ["theme_001"]
    theme = json.loads((tmp_path / "published_artifacts/themes/night_1/theme_001.json").read_text())
    assert [c["cluster_id"] for c in theme["clusters"]] == ["cluster_001"]
    assert [e["id"] for e in theme["extractions"]] == ["s1:001", "s2:004"]
    assert theme["extraction_count"] == 2
