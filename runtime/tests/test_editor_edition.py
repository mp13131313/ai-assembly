"""C46: editor `--single-dossier` must not clobber the night's dossier index.

Background (`_workspace/planning/runtime/OPEN_ITEMS.md` C46):
`editor_flow.py --single-dossier theme_X` regenerates one dossier, but
Stage 3 (`finalize_edition` / `build_night_index`) used to rewrite
`published_artifacts/dossiers/night_<N>/_index.json` from only the
dossier(s) processed in THAT run, dropping every other dossier from the
index. Same bug class as C50 (`voice/publish.py::_rebuild_index_from_disk`).

Fix: the per-night index's dossier list is now rebuilt from every
`dossier_<NNN>.json` actually on disk for that night
(`_rebuild_dossiers_from_disk`), not from the in-memory
`dossiers_by_theme` this call happened to (re)generate. The edition-lead
pick was already immune to the bug — it sources from the full-night
`routing["themes_to_dossiers"]` + `_load_theme_flags(run_dir)`, neither
of which is filtered by `--single-dossier` — these tests lock that in
too.

No real Anthropic calls — pure file-shape transforms over seeded
run_dir / project_root pairs.
"""
from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

_RUNTIME = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_RUNTIME))

from flows.shared.io import write_json_atomic  # noqa: E402
from flows.editor.edition import (  # noqa: E402
    NIGHT_INDEX_OWNED_DOSSIER_KEYS,
    NIGHT_INDEX_OWNED_TOP_LEVEL_KEYS,
    _rebuild_dossiers_from_disk,
    finalize_edition,
    merge_night_index,
)


# --- Fixture builders ------------------------------------------------------


def _dossier(theme_id: str, dossier_no: int, kicker: str = "K") -> dict:
    return {
        "schema_version": "2.0",
        "kicker": kicker,
        "headline": f"Headline {dossier_no}",
        "subline": "",
        "body_paragraphs": ["p1"],
        "headnotes": [],
        "metadata": {
            "theme_id": theme_id,
            "theme_display_title": f"Theme {dossier_no}",
            "night": 1,
        },
    }


def _write_published_dossier(
    project_root: Path, night: int, dossier_no: int, dossier: dict
) -> Path:
    p = (
        project_root / "published_artifacts" / "dossiers"
        / f"night_{night}" / f"dossier_{dossier_no:03d}.json"
    )
    write_json_atomic(p, dossier)
    return p


def _routing(themes_to_dossiers: list[dict], voices_routing: list[dict]) -> dict:
    return {
        "schema_version": "1.0",
        "night": 1,
        "themes_to_dossiers": themes_to_dossiers,
        "voices_routing": voices_routing,
        "refusals": [],
    }


# --- _rebuild_dossiers_from_disk -------------------------------------------


class TestRebuildDossiersFromDisk:
    def test_returns_empty_when_dir_missing(self, tmp_path):
        assert _rebuild_dossiers_from_disk(tmp_path, night=1) == []

    def test_reads_every_dossier_file_and_injects_dossier_no(self, tmp_path):
        _write_published_dossier(tmp_path, 1, 1, _dossier("theme_001", 1))
        _write_published_dossier(tmp_path, 1, 2, _dossier("theme_002", 2))
        out = _rebuild_dossiers_from_disk(tmp_path, night=1)
        assert {d["dossier_no"] for d in out} == {1, 2}
        by_no = {d["dossier_no"]: d for d in out}
        assert by_no[1]["metadata"]["theme_id"] == "theme_001"
        assert by_no[2]["metadata"]["theme_id"] == "theme_002"

    def test_skips_unparseable_file(self, tmp_path):
        night_dir = tmp_path / "published_artifacts" / "dossiers" / "night_1"
        night_dir.mkdir(parents=True)
        (night_dir / "dossier_001.json").write_text("{not json")
        _write_published_dossier(tmp_path, 1, 2, _dossier("theme_002", 2))
        out = _rebuild_dossiers_from_disk(tmp_path, night=1)
        assert [d["dossier_no"] for d in out] == [2]

    def test_ignores_index_json(self, tmp_path):
        _write_published_dossier(tmp_path, 1, 1, _dossier("theme_001", 1))
        idx_path = (
            tmp_path / "published_artifacts" / "dossiers" / "night_1" / "_index.json"
        )
        write_json_atomic(idx_path, {"night": 1})
        out = _rebuild_dossiers_from_disk(tmp_path, night=1)
        assert len(out) == 1


# --- finalize_edition: the C46 scenario ------------------------------------


class TestSingleDossierRerunPreservesIndex:
    """Full run (2 dossiers) then a `--single-dossier` rerun of just one
    theme must leave BOTH dossiers indexed, with the lead re-computed
    across the full night — not just the reprocessed dossier."""

    THEMES_TO_DOSSIERS = [
        {"theme_id": "theme_001", "dossier_no": 1, "theme_title": "T1", "n_engaged_voices": 5},
        {"theme_id": "theme_002", "dossier_no": 2, "theme_title": "T2", "n_engaged_voices": 1},
    ]
    VOICES_ROUTING = [
        {"voice_slug": "plato", "voice_name": "Voice of Plato",
         "primary_theme": "theme_001", "primary_dossier": 1},
        {"voice_slug": "cleopatra", "voice_name": "Voice of Cleopatra",
         "primary_theme": "theme_002", "primary_dossier": 2},
    ]

    def _routing(self) -> dict:
        return _routing(self.THEMES_TO_DOSSIERS, self.VOICES_ROUTING)

    def test_full_run_then_single_dossier_rerun_keeps_both_indexed(self, tmp_path):
        run_dir = tmp_path / "athens_night_1"
        project_root = tmp_path / "project"
        routing = self._routing()

        # --- "Full run": both dossiers generated + written to disk (as
        # editor_flow.py's write_dossier() does in Stage 2), then Stage 3
        # runs once with both in dossiers_by_theme.
        d1 = _dossier("theme_001", 1)
        d2 = _dossier("theme_002", 2)
        _write_published_dossier(project_root, 1, 1, d1)
        _write_published_dossier(project_root, 1, 2, d2)
        audit_full = finalize_edition(
            run_dir=run_dir, project_root=project_root, night=1,
            routing=routing,
            dossiers_by_theme={"theme_001": d1, "theme_002": d2},
        )
        # theme_001 has 5 engaged voices vs theme_002's 1 -> theme_001 leads.
        assert audit_full["lead_dossier_no"] == 1

        idx_path = (
            project_root / "published_artifacts" / "dossiers" / "night_1" / "_index.json"
        )
        idx_full = json.loads(idx_path.read_text())
        assert idx_full["dossier_count"] == 2
        assert {d["dossier_no"] for d in idx_full["dossiers"]} == {1, 2}
        assert idx_full["edition_lead"]["lead_dossier_no"] == 1

        # --- "--single-dossier theme_002" rerun: only theme_002's dossier
        # is regenerated + rewritten to disk (write_dossier already ran by
        # the time Stage 3 fires, matching editor_flow.py's ordering);
        # dossier_001 is untouched on disk from the full run above.
        d2_v2 = _dossier("theme_002", 2, kicker="REGENERATED")
        _write_published_dossier(project_root, 1, 2, d2_v2)
        audit_rerun = finalize_edition(
            run_dir=run_dir, project_root=project_root, night=1,
            routing=routing,
            dossiers_by_theme={"theme_002": d2_v2},
        )
        # Lead is unchanged — still computed off the FULL routing manifest,
        # not just the reprocessed dossier.
        assert audit_rerun["lead_dossier_no"] == 1

        idx_rerun = json.loads(idx_path.read_text())
        # C46: dossier_001 must still be indexed even though this call
        # only reprocessed dossier_002.
        assert idx_rerun["dossier_count"] == 2
        assert {d["dossier_no"] for d in idx_rerun["dossiers"]} == {1, 2}
        assert idx_rerun["edition_lead"]["lead_dossier_no"] == 1
        by_no = {d["dossier_no"]: d for d in idx_rerun["dossiers"]}
        assert by_no[2]["kicker"] == "REGENERATED"
        assert by_no[1]["kicker"] == "K"  # untouched from the full run

    def test_lead_pick_recoverable_even_when_leading_dossier_not_reprocessed(self, tmp_path):
        """The dossier that WINS the lead-pick doesn't have to be the one
        this call reprocessed — proves the lead-pick isn't sourced from
        `dossiers_by_theme` (the in-memory reprocessed subset)."""
        run_dir = tmp_path / "athens_night_1"
        project_root = tmp_path / "project"
        routing = self._routing()

        d1 = _dossier("theme_001", 1)  # 5 engaged voices — the eventual lead
        d2 = _dossier("theme_002", 2)  # 1 engaged voice
        _write_published_dossier(project_root, 1, 1, d1)
        _write_published_dossier(project_root, 1, 2, d2)

        # Single-dossier rerun of theme_002 ONLY — dossiers_by_theme never
        # sees theme_001 at all in this call.
        audit = finalize_edition(
            run_dir=run_dir, project_root=project_root, night=1,
            routing=routing,
            dossiers_by_theme={"theme_002": d2},
        )
        assert audit["lead_dossier_no"] == 1
        assert audit["scoring_audit"]["audit"][0]["theme_id"] == "theme_001"

    def test_missing_dossier_on_disk_warns_and_is_absent_from_index(self, tmp_path, caplog):
        """Defensive path: if `dossiers_by_theme` claims a theme was
        processed but its file never landed on disk (write_dossier
        failing silently, or a caller misuse), finalize_edition warns
        instead of silently indexing a phantom entry."""
        run_dir = tmp_path / "athens_night_1"
        project_root = tmp_path / "project"
        routing = self._routing()

        d1 = _dossier("theme_001", 1)
        _write_published_dossier(project_root, 1, 1, d1)
        # theme_002's dossier is NOT written to disk, unlike the normal
        # editor_flow.py ordering (write_dossier always runs first).

        with caplog.at_level(logging.WARNING, logger="editor_edition"):
            audit = finalize_edition(
                run_dir=run_dir, project_root=project_root, night=1,
                routing=routing,
                dossiers_by_theme={
                    "theme_001": d1,
                    "theme_002": {"metadata": {"theme_id": "theme_002"}},
                },
            )

        assert any("theme_002" in rec.message for rec in caplog.records)
        idx_path = (
            project_root / "published_artifacts" / "dossiers" / "night_1" / "_index.json"
        )
        idx = json.loads(idx_path.read_text())
        assert idx["dossier_count"] == 1
        assert idx["dossiers"][0]["dossier_no"] == 1
        # Lead-pick is unaffected by the missing file — still scored off
        # routing, not off what actually landed on disk.
        assert audit["lead_dossier_no"] == 1


# --- merge_night_index (pure function) -------------------------------------
#
# Two writers (this module's `finalize_edition` and
# `publish_flow.py::_build_per_night_dossier_index`) share
# `published_artifacts/dossiers/night_<N>/_index.json` with different
# schemas. `merge_night_index` is the shared helper that stops either one
# from clobbering the other's fields on a rewrite. These tests exercise
# it directly (no disk I/O, no finalize_edition) using stand-in owned-key
# sets so the merge *mechanism* is tested independently of the editor's
# actual schema.


class TestMergeNightIndexPure:
    OWNED_TOP = {"night", "dossiers", "editor_only_field"}
    OWNED_DOSSIER = {"dossier_no", "kicker", "editor_only_dossier_field"}

    def test_no_existing_returns_new_unchanged(self):
        new = {"night": 1, "dossiers": [{"dossier_no": 1, "kicker": "K"}]}
        assert merge_night_index(
            None, new,
            owned_top_level_keys=self.OWNED_TOP,
            owned_dossier_keys=self.OWNED_DOSSIER,
        ) == new

    def test_unreadable_existing_passed_as_none_returns_new_unchanged(self):
        # Callers pass `existing=None` for an unreadable/malformed file —
        # same code path as "no file yet".
        new = {"night": 1, "dossiers": []}
        assert merge_night_index(
            {}, new,  # empty dict is falsy — same short-circuit as None
            owned_top_level_keys=self.OWNED_TOP,
            owned_dossier_keys=self.OWNED_DOSSIER,
        ) == new

    def test_preserves_unowned_top_level_keys(self):
        existing = {"night": 1, "dossiers": [], "publish_only_field": "keep-me"}
        new = {"night": 1, "dossiers": []}
        merged = merge_night_index(
            existing, new,
            owned_top_level_keys=self.OWNED_TOP,
            owned_dossier_keys=self.OWNED_DOSSIER,
        )
        assert merged["publish_only_field"] == "keep-me"

    def test_owned_top_level_key_always_takes_new_value(self):
        existing = {"night": 1, "editor_only_field": "stale", "dossiers": []}
        new = {"night": 2, "editor_only_field": "fresh", "dossiers": []}
        merged = merge_night_index(
            existing, new,
            owned_top_level_keys=self.OWNED_TOP,
            owned_dossier_keys=self.OWNED_DOSSIER,
        )
        assert merged["night"] == 2
        assert merged["editor_only_field"] == "fresh"

    def test_owned_top_level_key_wins_even_when_absent_from_existing(self):
        """A key this writer owns always reflects `new`, even if the
        existing file never had it at all (e.g. first time this field
        was introduced)."""
        existing = {"night": 1, "dossiers": []}
        new = {"night": 1, "editor_only_field": "fresh", "dossiers": []}
        merged = merge_night_index(
            existing, new,
            owned_top_level_keys=self.OWNED_TOP,
            owned_dossier_keys=self.OWNED_DOSSIER,
        )
        assert merged["editor_only_field"] == "fresh"

    def test_preserves_unowned_dossier_keys_matched_by_dossier_no(self):
        existing = {
            "dossiers": [
                {"dossier_no": 1, "kicker": "OLD", "issue_no": 42193, "vol": "CXVI"},
            ],
        }
        new = {
            "dossiers": [
                {"dossier_no": 1, "kicker": "NEW"},
            ],
        }
        merged = merge_night_index(
            existing, new,
            owned_top_level_keys=self.OWNED_TOP,
            owned_dossier_keys=self.OWNED_DOSSIER,
        )
        entry = merged["dossiers"][0]
        # Own field (kicker) takes the new value...
        assert entry["kicker"] == "NEW"
        # ...but the fields this writer doesn't produce survive.
        assert entry["issue_no"] == 42193
        assert entry["vol"] == "CXVI"

    def test_owned_dossier_key_always_takes_new_value(self):
        existing = {"dossiers": [{"dossier_no": 1, "editor_only_dossier_field": "stale"}]}
        new = {"dossiers": [{"dossier_no": 1, "editor_only_dossier_field": "fresh"}]}
        merged = merge_night_index(
            existing, new,
            owned_top_level_keys=self.OWNED_TOP,
            owned_dossier_keys=self.OWNED_DOSSIER,
        )
        assert merged["dossiers"][0]["editor_only_dossier_field"] == "fresh"

    def test_dossier_removed_from_new_list_is_dropped(self):
        """The writer's own dossier list is authoritative for WHICH
        dossiers exist — an entry only in `existing` (dossier removed
        from disk) is not resurrected, even though it carried unowned
        fields worth keeping in principle."""
        existing = {
            "dossiers": [
                {"dossier_no": 1, "kicker": "K1", "issue_no": 1},
                {"dossier_no": 2, "kicker": "K2", "issue_no": 2},
            ],
        }
        new = {"dossiers": [{"dossier_no": 1, "kicker": "K1"}]}
        merged = merge_night_index(
            existing, new,
            owned_top_level_keys=self.OWNED_TOP,
            owned_dossier_keys=self.OWNED_DOSSIER,
        )
        assert [d["dossier_no"] for d in merged["dossiers"]] == [1]

    def test_no_match_in_existing_leaves_new_entry_untouched(self):
        """A brand-new dossier_no with no existing counterpart passes
        through unchanged — nothing to merge in."""
        existing = {"dossiers": [{"dossier_no": 1, "kicker": "K1", "issue_no": 1}]}
        new = {"dossiers": [{"dossier_no": 1, "kicker": "K1"}, {"dossier_no": 2, "kicker": "K2"}]}
        merged = merge_night_index(
            existing, new,
            owned_top_level_keys=self.OWNED_TOP,
            owned_dossier_keys=self.OWNED_DOSSIER,
        )
        by_no = {d["dossier_no"]: d for d in merged["dossiers"]}
        assert by_no[2] == {"dossier_no": 2, "kicker": "K2"}


# --- Two-writer integration: finalize_edition merges onto publish's shape --


def _publish_shaped_index(night: int, dossiers: list[dict]) -> dict:
    """Build an `_index.json` payload shaped like
    `publish_flow.py::_build_per_night_dossier_index`'s output — used to
    seed disk state simulating "publish already ran" before
    finalize_edition (the editor) writes."""
    return {
        "night": night,
        "url_path": f"/dossiers/night-{night}",
        "generated_at": "2026-05-08T09:00:00+00:00",
        "dossier_count": len(dossiers),
        "dossiers": dossiers,
        "edition_lead": None,
        "voices_in_night": {"plato": {"voice_slug": "plato", "primary_dossier_no": 1}},
    }


class TestFinalizeEditionMergesOntoPublish:
    """`_workspace/planning/runtime/OPEN_ITEMS.md` — publish and the editor
    write the same `_index.json` with different schemas; the editor must
    not clobber publish's `voices_in_night` when it rewrites the file
    after publish already ran.
    """

    THEMES_TO_DOSSIERS = [
        {"theme_id": "theme_001", "dossier_no": 1, "theme_title": "T1", "n_engaged_voices": 5},
        {"theme_id": "theme_002", "dossier_no": 2, "theme_title": "T2", "n_engaged_voices": 1},
    ]
    VOICES_ROUTING = [
        {"voice_slug": "plato", "voice_name": "Voice of Plato",
         "primary_theme": "theme_001", "primary_dossier": 1},
        {"voice_slug": "cleopatra", "voice_name": "Voice of Cleopatra",
         "primary_theme": "theme_002", "primary_dossier": 2},
    ]

    def _routing(self) -> dict:
        return _routing(self.THEMES_TO_DOSSIERS, self.VOICES_ROUTING)

    def test_editor_rewrite_keeps_publish_only_fields(self, tmp_path):
        run_dir = tmp_path / "athens_night_1"
        project_root = tmp_path / "project"
        routing = self._routing()

        d1 = _dossier("theme_001", 1, kicker="K1")
        d2 = _dossier("theme_002", 2, kicker="K2")
        _write_published_dossier(project_root, 1, 1, d1)
        _write_published_dossier(project_root, 1, 2, d2)

        idx_path = (
            project_root / "published_artifacts" / "dossiers" / "night_1" / "_index.json"
        )
        # Simulate publish_flow.py having already written the index for
        # this night, with a field the editor's own build_night_index
        # never produces (voices_in_night).
        write_json_atomic(idx_path, _publish_shaped_index(1, [
            {"dossier_no": 1, "filename": "dossier_001.json",
             "url_path": "/dossiers/night-1/dossier_001", "kicker": "STALE",
             "headline": "", "subline": "", "theme_id": "theme_001",
             "theme_display_title": "", "voice_count": 0, "voices_routed": []},
            {"dossier_no": 2, "filename": "dossier_002.json",
             "url_path": "/dossiers/night-1/dossier_002", "kicker": "STALE",
             "headline": "", "subline": "", "theme_id": "theme_002",
             "theme_display_title": "", "voice_count": 0, "voices_routed": []},
        ]))

        finalize_edition(
            run_dir=run_dir, project_root=project_root, night=1,
            routing=routing,
            dossiers_by_theme={"theme_001": d1, "theme_002": d2},
        )

        idx = json.loads(idx_path.read_text())

        # Editor's own fields win for its own data (not left as "STALE").
        by_no = {d["dossier_no"]: d for d in idx["dossiers"]}
        assert by_no[1]["kicker"] == "K1"
        assert by_no[2]["kicker"] == "K2"
        # Editor now owns and has set a real edition_lead (was None).
        assert idx["edition_lead"]["lead_dossier_no"] == 1

        # The publish-only field the editor doesn't produce survives the
        # editor's rewrite.
        assert idx["voices_in_night"] == {"plato": {"voice_slug": "plato", "primary_dossier_no": 1}}

    def test_editor_rewrite_drops_dossier_removed_from_disk(self, tmp_path):
        """publish's stale index carries a 3rd dossier that's no longer on
        disk; the editor's rewrite (sourced from disk, per C46) must not
        resurrect it, even though its entry carried an unowned key that
        survives for dossiers that DO still exist. (The key is a legacy
        `issue_no`, as in indexes written before 2026-05-05; publish
        stopped writing it in C64, but the merge rule still carries
        unowned keys forward.)"""
        run_dir = tmp_path / "athens_night_1"
        project_root = tmp_path / "project"
        routing = self._routing()

        d1 = _dossier("theme_001", 1)
        d2 = _dossier("theme_002", 2)
        _write_published_dossier(project_root, 1, 1, d1)
        _write_published_dossier(project_root, 1, 2, d2)
        # dossier_003 intentionally NOT written to disk.

        idx_path = (
            project_root / "published_artifacts" / "dossiers" / "night_1" / "_index.json"
        )
        write_json_atomic(idx_path, _publish_shaped_index(1, [
            {"dossier_no": 1, "filename": "dossier_001.json", "kicker": "K1", "issue_no": 1},
            {"dossier_no": 2, "filename": "dossier_002.json", "kicker": "K2", "issue_no": 2},
            {"dossier_no": 3, "filename": "dossier_003.json", "kicker": "K3", "issue_no": 3},
        ]))

        finalize_edition(
            run_dir=run_dir, project_root=project_root, night=1,
            routing=routing,
            dossiers_by_theme={"theme_001": d1, "theme_002": d2},
        )

        idx = json.loads(idx_path.read_text())
        assert idx["dossier_count"] == 2
        assert {d["dossier_no"] for d in idx["dossiers"]} == {1, 2}
        # Survivors still carry the unowned legacy key.
        by_no = {d["dossier_no"]: d for d in idx["dossiers"]}
        assert by_no[1]["issue_no"] == 1
        assert by_no[2]["issue_no"] == 2

    def test_owned_key_sets_do_not_overlap_on_edition_lead(self):
        """Sanity check on the schema contract itself: `edition_lead` is
        the one top-level field the editor owns that publish's own
        `_DOSSIER_INDEX_OWNED_TOP_LEVEL_KEYS` (imported here to avoid
        drift) must NOT claim — that's what lets it survive a publish
        rewrite."""
        from flows.publish_flow import (
            _DOSSIER_INDEX_OWNED_DOSSIER_KEYS,
            _DOSSIER_INDEX_OWNED_TOP_LEVEL_KEYS,
        )
        assert "edition_lead" in NIGHT_INDEX_OWNED_TOP_LEVEL_KEYS
        assert "edition_lead" not in _DOSSIER_INDEX_OWNED_TOP_LEVEL_KEYS
        # No per-dossier key is editor-only — publish's per-dossier
        # schema covers the editor's (today the two are identical).
        assert NIGHT_INDEX_OWNED_DOSSIER_KEYS <= _DOSSIER_INDEX_OWNED_DOSSIER_KEYS
