"""Load sessions.json + speakers.json; join them into per-session session.json.

The heavy lifting is the schema translation at upload time: sessions.json
uses different field names from what flows/transcription_flow.py consumes.
Mapping is documented in the plan and enforced here in `build_session_json`.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .config import DAY_TO_RUN, RUNS_DIR, SESSIONS_PATH, SPEAKERS_PATH


# --- Dataclasses -------------------------------------------------------------


@dataclass
class Session:
    """One row from reference/sessions.json (subset of fields we use)."""

    session_id: str
    ai_assembly: bool
    day: str
    day_index: int
    date: str | None
    start_time: str
    end_time: str
    date_time_start: str | None
    venue: str
    venue_sub: str
    track: str
    title: str
    description: str
    speakers: list[str]
    session_format: str
    partner: str = ""
    limited_capacity: bool = False
    capacity: int | None = None

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Session":
        return cls(
            session_id=d["session_id"],
            ai_assembly=bool(d.get("ai_assembly", False)),
            day=d.get("day", ""),
            day_index=int(d.get("day_index", -1)),
            date=d.get("date"),
            start_time=d.get("start_time", ""),
            end_time=d.get("end_time", ""),
            date_time_start=d.get("date_time_start"),
            venue=d.get("venue", ""),
            venue_sub=d.get("venue_sub", ""),
            track=d.get("track", ""),
            title=d.get("title", ""),
            description=d.get("description", ""),
            speakers=list(d.get("speakers", [])),
            session_format=d.get("session_format", "panel"),
            partner=d.get("partner", ""),
            limited_capacity=bool(d.get("limited_capacity", False)),
            capacity=d.get("capacity"),
        )


@dataclass
class Speaker:
    """One row from reference/speakers.json."""

    name: str
    title: str = ""
    affiliation: str = ""
    bio: str = ""
    sessions: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Speaker":
        return cls(
            name=d.get("name", ""),
            title=d.get("title", ""),
            affiliation=d.get("affiliation", ""),
            bio=d.get("bio", ""),
            sessions=list(d.get("sessions", [])),
        )


# --- Loaders -----------------------------------------------------------------


def load_sessions(path: Path = SESSIONS_PATH) -> list[Session]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return [Session.from_dict(s) for s in data.get("sessions", [])]


def load_speakers(path: Path = SPEAKERS_PATH) -> dict[str, Speaker]:
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    out: dict[str, Speaker] = {}
    for s in data.get("speakers", []):
        if s.get("_dropped_from_program"):
            continue  # keep the bio in the file, but don't join on dropped speakers
        sp = Speaker.from_dict(s)
        if sp.name:
            out[sp.name] = sp
    return out


# --- Derivations -------------------------------------------------------------


# Track name → CSS class. Mirrors the program page's track colour system so
# the ingest UI colour-codes sessions the same way producers see them on
# program.worldbeautifulbusinessforum.com. Tracks that chain two names with
# " / " map to the first one's colour.
_TRACK_CSS: dict[str, str] = {
    "MAIN STAGE": "track-main-stage",
    "AGENTIC AGORA": "track-agentic-agora",
    "AI DEMOCRACY MARATHON": "track-ai-marathon",
    "BEAUTY SALON": "track-beauty-salon",
    "BUREAU OF CARE": "track-bureau-care",
    "DEPARTMENT OF DEPTH": "track-dept-depth",
    "HOME OF BELONGING": "track-home-belonging",
    "LONGEVITY LAB": "track-longevity-lab",
    "MINISTRY OF REGENERATION": "track-ministry-regen",
    "TEMPLE OF REENCHANTMENT": "track-temple",
    "THE BEAUTIFUL BUSINESS SCHOOL": "track-bbs",
    "COMMUNITY": "track-community",
}


def track_css_class(track: str) -> str:
    """Map a session's track string to its CSS class, or '' if unknown."""
    t = (track or "").strip().upper()
    if t in _TRACK_CSS:
        return _TRACK_CSS[t]
    # Chained tracks use the first segment for colour.
    first = t.split(" / ", 1)[0].strip()
    return _TRACK_CSS.get(first, "")


def run_for_session(session: Session) -> str | None:
    """Which overnight run does this session's audio feed into? None if n/a."""
    return DAY_TO_RUN.get(session.day)


def session_dir(session: Session) -> Path | None:
    """Canonical filesystem dir for this session's Stage 0 outputs."""
    run = run_for_session(session)
    if run is None:
        return None
    return RUNS_DIR / run / "01_transcription" / session.session_id


def derive_roster(
    session: Session, speakers: dict[str, Speaker]
) -> tuple[list[dict[str, str]], list[str]]:
    """Join speaker names to full profiles. Returns (roster, missing_names).

    `missing_names` is the subset of session.speakers with no entry (or an
    empty bio) in speakers.json — surfaced in the UI so producers can see
    that Speaker ID Pass 3 will be weaker on that session.
    """
    roster: list[dict[str, str]] = []
    missing: list[str] = []
    for name in session.speakers:
        sp = speakers.get(name)
        if sp is None:
            roster.append({"name": name, "title": "", "affiliation": "", "bio": ""})
            missing.append(name)
        else:
            roster.append(
                {
                    "name": sp.name,
                    "title": sp.title,
                    "affiliation": sp.affiliation,
                    "bio": sp.bio,
                }
            )
            if not sp.bio.strip():
                missing.append(name)
    return roster, missing


def build_session_json(
    session: Session, speakers: dict[str, Speaker]
) -> dict[str, Any]:
    """Produce the session.json payload flows/transcription_flow.py consumes.

    Translates field names from sessions.json schema to session_template.json
    schema. Joins speakers.json for roster bios. Only `session_title` is
    strictly required by the transcription flow — the rest default gracefully.
    """
    roster, _missing = derive_roster(session, speakers)
    venue = session.venue
    if session.venue_sub:
        venue = f"{venue} · {session.venue_sub}"

    return {
        "session_id": session.session_id,
        "session_title": session.title,
        "session_description": session.description,
        "session_format": session.session_format,
        "track": session.track,
        "date_time": session.date_time_start or "",
        "venue": venue,
        "expected_speaker_count": len(roster),
        "roster": roster,
    }


# --- Lookup by id ------------------------------------------------------------


def find_session(sessions: list[Session], session_id: str) -> Session | None:
    for s in sessions:
        if s.session_id == session_id:
            return s
    return None
