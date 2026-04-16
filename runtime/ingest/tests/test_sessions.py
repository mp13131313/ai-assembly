"""Schema translation + roster join tests.

Uses the real reference/sessions.json and reference/speakers.json to exercise
the actual data shape we'll see at Athens.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from ingest.sessions import (
    Session,
    Speaker,
    build_session_json,
    derive_roster,
    find_session,
    load_sessions,
    load_speakers,
    run_for_session,
    session_dir,
)

REPO = Path(__file__).resolve().parent.parent.parent


def test_load_sessions_non_empty():
    sessions = load_sessions()
    assert len(sessions) > 0
    # Every session has a non-empty session_id
    assert all(s.session_id for s in sessions)


def test_load_speakers_non_empty():
    speakers = load_speakers()
    assert len(speakers) > 0


def test_day_to_run_mapping():
    """Only Day One/Two/Three get overnight runs; others return None."""
    def s(day: str) -> Session:
        return Session(
            session_id="x", ai_assembly=True, day=day, day_index=0,
            date=None, start_time="", end_time="", date_time_start=None,
            venue="", venue_sub="", track="", title="", description="",
            speakers=[], session_format="panel",
        )

    assert run_for_session(s("Day One")) == "athens_night_1"
    assert run_for_session(s("Day Two")) == "athens_night_2"
    assert run_for_session(s("Day Three")) == "athens_night_3"
    assert run_for_session(s("Day Zero")) is None
    assert run_for_session(s("Day Four")) is None
    assert run_for_session(s("Special Activations")) is None


def test_session_dir_for_unrun_day_is_none():
    sessions = load_sessions()
    # pick one on Day Zero (or any unrun day)
    day_zero = [s for s in sessions if s.day == "Day Zero"]
    if day_zero:
        assert session_dir(day_zero[0]) is None


def test_build_session_json_schema_translation():
    """The critical test: sessions.json → session.json field rename + roster join."""
    sess = Session(
        session_id="test_001",
        ai_assembly=True,
        day="Day One",
        day_index=1,
        date="2026-05-07",
        start_time="10:00",
        end_time="11:00",
        date_time_start="2026-05-07T10:00:00+03:00",
        venue="Demos",
        venue_sub="Auditorium",
        track="MAIN STAGE",
        title="Test Panel",
        description="A test panel description.",
        speakers=["Alice Example", "Bob Someone"],
        session_format="panel",
    )
    speakers = {
        "Alice Example": Speaker(
            name="Alice Example",
            title="CEO",
            affiliation="Acme",
            bio="Alice is a test speaker.",
        ),
        # Bob intentionally missing from speakers dict
    }

    out = build_session_json(sess, speakers)

    # Field renames
    assert out["session_title"] == "Test Panel"
    assert out["session_description"] == "A test panel description."
    assert out["date_time"] == "2026-05-07T10:00:00+03:00"
    # venue + venue_sub concatenation
    assert out["venue"] == "Demos · Auditorium"

    # Passthroughs
    assert out["session_id"] == "test_001"
    assert out["session_format"] == "panel"
    assert out["track"] == "MAIN STAGE"

    # Roster: 2 entries, one with bio, one stub
    assert out["expected_speaker_count"] == 2
    assert len(out["roster"]) == 2
    alice = out["roster"][0]
    bob = out["roster"][1]
    assert alice["name"] == "Alice Example"
    assert alice["bio"] == "Alice is a test speaker."
    assert bob["name"] == "Bob Someone"
    assert bob["bio"] == ""  # stub for missing speaker


def test_derive_roster_reports_missing():
    sess = Session(
        session_id="x", ai_assembly=True, day="Day One", day_index=1,
        date=None, start_time="", end_time="", date_time_start=None,
        venue="", venue_sub="", track="", title="", description="",
        speakers=["Known Speaker", "Unknown Speaker", "BlankBio Speaker"],
        session_format="panel",
    )
    speakers = {
        "Known Speaker": Speaker(name="Known Speaker", bio="A real bio."),
        "BlankBio Speaker": Speaker(name="BlankBio Speaker", bio=""),
    }
    roster, missing = derive_roster(sess, speakers)
    assert len(roster) == 3
    # Both unknown-in-dict AND empty-bio count as missing.
    assert set(missing) == {"Unknown Speaker", "BlankBio Speaker"}


def test_build_session_json_no_venue_sub():
    """When venue_sub is empty, venue should not have a trailing ' · '."""
    sess = Session(
        session_id="x", ai_assembly=True, day="Day One", day_index=1,
        date=None, start_time="", end_time="", date_time_start=None,
        venue="Demos", venue_sub="", track="", title="t", description="",
        speakers=[], session_format="panel",
    )
    out = build_session_json(sess, {})
    assert out["venue"] == "Demos"


def test_find_session_returns_none_for_unknown():
    assert find_session([], "nope") is None


def test_real_sessions_have_consistent_shape():
    """Every session in the real file can be translated without crashing."""
    sessions = load_sessions()
    speakers = load_speakers()
    for s in sessions:
        out = build_session_json(s, speakers)
        assert "session_title" in out
        assert "roster" in out
        # session_title is the only field the real flow strictly requires.
        assert out["session_title"] == s.title
