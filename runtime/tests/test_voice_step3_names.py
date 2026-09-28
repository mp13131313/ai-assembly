"""R1 (untouched-code review, 2026-09-28): the dormant Step-3 prompt must
name peers via `voice_display_name(slug, project_root)`, not their raw
`council_member` field — which on Step 1/2/3 artifacts is the long card
identity-prefix opening line ("I am Augusta Ada King, Countess of
Lovelace…"), the same corruption C53 fixed on the published surface.
Step 3 is dormant (Athens skipped it per A1), so this never shipped, but
re-enabling it (C61) would otherwise have every voice reading its peers
under those long identity lines.

Covers `flows/voice/card_assembly.filter_first_draft_for_step3` and
`flows/voice/step3_amended_artifact.build_step3_user_prompt`.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_RUNTIME = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_RUNTIME))

from flows.voice.card_assembly import filter_first_draft_for_step3  # noqa: E402
from flows.voice.step3_amended_artifact import build_step3_user_prompt  # noqa: E402

OCTOPUS_BAD = "I am octopus. The name is yours, not mine"


def _council_config(tmp_path: Path) -> Path:
    project_root = tmp_path / "project"
    project_root.mkdir()
    (project_root / "council_config.json").write_text(json.dumps({
        "members": [
            {"name": "Voice of the Octopus"},
            {"name": "Voice of Plato"},
        ]
    }))
    return project_root


class TestFilterFirstDraftForStep3:
    def test_resolves_via_council_config(self, tmp_path):
        project_root = _council_config(tmp_path)
        first_draft = {
            "lineage": {"voice_slug": "octopus", "themes_covered": ["theme_001"]},
            "council_member": OCTOPUS_BAD,
            "focus_decision": "Focus on Response 1.",
            "artifact_text": "the body",
        }
        out = filter_first_draft_for_step3(first_draft, project_root)
        assert out["voice_name"] == "Voice of the Octopus"
        assert OCTOPUS_BAD not in out.values()
        assert "council_member" not in out  # dropped, not just renamed
        assert out["artifact_text"] == "the body"

    def test_falls_back_to_raw_field_without_a_slug(self, tmp_path):
        project_root = _council_config(tmp_path)
        first_draft = {"council_member": "Some Legacy Name", "artifact_text": "x"}
        out = filter_first_draft_for_step3(first_draft, project_root)
        assert out["voice_name"] == "Some Legacy Name"

    def test_falls_back_to_slug_guess_without_project_root(self):
        first_draft = {
            "lineage": {"voice_slug": "octopus"},
            "council_member": OCTOPUS_BAD,
        }
        out = filter_first_draft_for_step3(first_draft, project_root=None)
        assert out["voice_name"] == "Voice of Octopus"  # slug-derived fallback, no article


class TestBuildStep3UserPrompt:
    def _drafts(self):
        own = {
            "lineage": {"voice_slug": "plato", "themes_covered": ["theme_001"]},
            "council_member": "I am Plato of Athens",
            "selected_form": "dialogue",
            "focus_decision": "Focus on Response 1.",
            "stance": "curious",
            "artifact_text": "Plato's piece.",
        }
        other = {
            "lineage": {"voice_slug": "octopus", "themes_covered": ["theme_001"]},
            "council_member": OCTOPUS_BAD,
            "artifact_text": "Octopus's piece.",
        }
        return own, other

    def test_peer_named_via_council_config_not_raw_council_member(self, tmp_path):
        project_root = _council_config(tmp_path)
        own, other = self._drafts()
        user, voices_read = build_step3_user_prompt(
            own, [other], project_root=project_root,
        )
        assert OCTOPUS_BAD not in user
        assert "addressed by you and Voice of the Octopus" in user
        assert voices_read == [{
            "voice_slug": "octopus",
            "council_member": "Voice of the Octopus",
            "first_draft_path": "04_voice/step2_first_draft_artifacts/octopus.json",
            "shared_themes": ["theme_001"],
        }]
        # The "FULL RECORD" JSON blob is also restamped, not just the
        # narrative cross-section text.
        assert '"voice_name": "Voice of the Octopus"' in user

    def test_falls_back_to_slug_guess_without_project_root(self):
        own, other = self._drafts()
        user, voices_read = build_step3_user_prompt(own, [other])
        assert OCTOPUS_BAD not in user
        assert voices_read[0]["council_member"] == "Voice of Octopus"
