"""Tests for `member_slug` — incl. C34 "Voice of [the] " prefix stripping.

C34 (2026-05-04) extended `member_slug` so council_configs that adopt
the athens-2026 "Voice of X" naming convention still resolve to the
short folder slug (`voices/plato/` not `voices/voice_of_plato/`).
Backward-compatible: short-name inputs slug as before.
"""
from __future__ import annotations

import sys
from pathlib import Path

_RUNTIME_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_RUNTIME_ROOT / "flows"))

from shared.io import member_slug  # noqa: E402


class TestMemberSlugLegacy:
    """Pre-C34 behaviour preserved for short-name inputs."""

    def test_simple_name(self):
        assert member_slug("Plato") == "plato"

    def test_two_part_name(self):
        assert member_slug("Hannah Arendt") == "hannah_arendt"

    def test_with_punctuation(self):
        assert member_slug("Bob Marley") == "bob_marley"

    def test_compound_with_underscore_collapse(self):
        assert member_slug("Whanganui  River") == "whanganui_river"


class TestMemberSlugVoiceOfPrefix:
    """C34 — strip 'Voice of [the] ' prefix from athens-2026 convention."""

    def test_voice_of_simple(self):
        assert member_slug("Voice of Plato") == "plato"

    def test_voice_of_the_simple(self):
        assert member_slug("Voice of the Octopus") == "octopus"

    def test_voice_of_the_compound(self):
        assert member_slug("Voice of the Whanganui River") == "whanganui_river"

    def test_voice_of_two_part_name(self):
        assert member_slug("Voice of Hannah Arendt") == "hannah_arendt"

    def test_voice_of_fyodor_dostoevsky(self):
        assert member_slug("Voice of Fyodor Dostoevsky") == "fyodor_dostoevsky"

    def test_voice_of_ibn_battuta(self):
        assert member_slug("Voice of Ibn Battuta") == "ibn_battuta"

    def test_voice_of_ada_lovelace(self):
        assert member_slug("Voice of Ada Lovelace") == "ada_lovelace"

    def test_case_insensitive_prefix(self):
        # Defensive — operator paste might lowercase
        assert member_slug("voice of plato") == "plato"
        assert member_slug("VOICE OF THE OCTOPUS") == "octopus"

    def test_extra_whitespace(self):
        assert member_slug("  Voice of  Plato  ") == "plato"


class TestMemberSlugEdgeCases:
    """Behaviour at edges — name that looks like a prefix, etc."""

    def test_name_starting_with_voice_but_not_the_prefix(self):
        # "Voice" as part of a name (no "of " after) — not stripped.
        assert member_slug("Voiceless") == "voiceless"

    def test_voice_alone(self):
        assert member_slug("Voice") == "voice"

    def test_name_with_voice_in_middle(self):
        # "Voice" not at the start — not stripped.
        assert member_slug("The Voice of Reason") == "the_voice_of_reason"
