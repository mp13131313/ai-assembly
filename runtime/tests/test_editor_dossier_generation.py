"""Tests for flows/editor/dossier_generation.py.

Covers:
  - build_dossier_briefing: dedupes theme block, keeps all N voice entries,
    handles missing fields defensively
  - parse_dossier_output: extracts kicker/headline/subline/body_paragraphs/
    headnotes/front_abstract from prose-and-parse output; tolerates missing
    fields
  - stamp_runtime_fields: enriches headnotes with voice_name + formulation_text;
    fills metadata block; computes colophon
  - generate_dossier (end-to-end with mocked Anthropic): orchestrates
    briefing → user prompt → parse → stamp without burning credits
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_RUNTIME_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_RUNTIME_ROOT))

from flows.editor import dossier_generation as dg  # noqa: E402


# --- Fixtures -------------------------------------------------------------


def _write_briefing(run_dir: Path, voice_slug: str, theme_id: str,
                    *, narrative: str = "<briefing>") -> None:
    p = run_dir / "03_provocateur" / "briefings" / f"{voice_slug}.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({
        "formulations": [
            {
                "theme_id": theme_id,
                "theme_display_title": theme_id.replace("_", " ").title(),
                "mode": "question",
                "narrative_briefing": narrative,
                "full_theme_record": {
                    "theme_title_from_researcher": f"Researcher's title for {theme_id}",
                    "theme_abstract_from_researcher": f"Abstract for {theme_id}",
                    "clusters": [
                        {
                            "cluster_id": "c1",
                            "cluster_title": "Cluster 1",
                            "cluster_abstract": "Abstract 1",
                            "extractions": [
                                {"id": "e1", "speaker": "X", "extraction": "..."}
                            ],
                        }
                    ],
                    "theme_flags": {"audience_friction": "moderate"},
                }
            }
        ]
    }))


def _write_artifact(run_dir: Path, voice_slug: str, *, council_member: str,
                    artifact_text: str = "<artifact>") -> None:
    p = run_dir / "04_voice" / "step2_first_draft_artifacts" / f"{voice_slug}.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({
        "lineage": {"voice_slug": voice_slug, "themes_covered": []},
        "council_member": council_member,
        "focus_decision": "...",
        "artifact_text": artifact_text,
    }))


@pytest.fixture
def run_dir(tmp_path: Path) -> Path:
    rd = tmp_path / "athens_night_1"
    rd.mkdir()
    return rd


# --- build_dossier_briefing ---------------------------------------------


class TestBuildDossierBriefing:
    def test_single_voice(self, run_dir):
        _write_briefing(run_dir, "plato", "theme_001",
                        narrative="<plato briefing for theme_001>")
        _write_artifact(run_dir, "plato", council_member="Plato",
                        artifact_text="<plato artifact>")

        briefing = dg.build_dossier_briefing(
            "theme_001", ["plato"], run_dir, night=1,
        )
        assert briefing["theme"]["theme_id"] == "theme_001"
        assert briefing["theme"]["theme_title_from_researcher"] == "Researcher's title for theme_001"
        assert len(briefing["theme"]["clusters"]) == 1
        assert briefing["theme"]["clusters"][0]["extractions"][0]["id"] == "e1"
        assert len(briefing["engaged_voices"]) == 1
        assert briefing["engaged_voices"][0]["voice_name"] == "the voice of Plato"
        assert briefing["engaged_voices"][0]["narrative_briefing"] == "<plato briefing for theme_001>"
        assert briefing["engaged_voices"][0]["artifact_text"] == "<plato artifact>"

    def test_multi_voice_dedupes_theme(self, run_dir):
        """Five voices' briefings carry identical theme block. The merged
        dossier briefing has one theme block + 5 engaged_voices entries."""
        for slug in ("v1", "v2", "v3", "v4", "v5"):
            _write_briefing(run_dir, slug, "theme_001",
                            narrative=f"<{slug} briefing>")
            _write_artifact(run_dir, slug, council_member=slug.upper(),
                            artifact_text=f"<{slug} artifact>")
        briefing = dg.build_dossier_briefing(
            "theme_001", ["v1", "v2", "v3", "v4", "v5"], run_dir, night=1,
        )
        assert briefing["theme"]["theme_id"] == "theme_001"
        assert len(briefing["engaged_voices"]) == 5
        # Each has unique narrative_briefing
        narratives = {v["narrative_briefing"] for v in briefing["engaged_voices"]}
        assert len(narratives) == 5

    def test_empty_voice_list_raises(self, run_dir):
        with pytest.raises(ValueError, match="No voices routed"):
            dg.build_dossier_briefing("theme_001", [], run_dir, night=1)

    def test_prior_editions_passthrough(self, run_dir):
        _write_briefing(run_dir, "plato", "theme_001")
        _write_artifact(run_dir, "plato", council_member="Plato")
        prior = [{"night": 1, "issue_no": 42193, "dossiers": [{"kicker": "K", "headline": "H", "body_paragraphs": ["p1"]}]}]
        briefing = dg.build_dossier_briefing(
            "theme_001", ["plato"], run_dir, night=2, prior_editions=prior,
        )
        assert briefing["prior_editions"] == prior


# --- parse_dossier_output ----------------------------------------------


class TestParseOutput:
    def test_parse_clean_output(self):
        raw = """**kicker:** FOUR NAMINGS OF A DISSOLVED THING

**headline:** The Voices Refused To Call It Governance

**subline:** Four voices, in different vocabularies, decline the term; the editor notes a convergence she will not call agreement

**body_paragraphs:**
We received the night's submissions in the order they arrived.

The first thing to say is that they did not agree.

* * *

The convergence, then, is on what is dissolved.

**headnotes:**
voice_slug: plato
artifact_title: DOCTORS OR COOKS?
framing_text: Plato wrote a dialogue rather than an essay.
voice_slug: cleopatra
artifact_title: A PROSTAGMA, ISSUED AT NIGHT
framing_text: Cleopatra issued a prostagma.

**front_abstract:** Four voices, in different vocabularies, declined to call faceless sortings governance; the editor names a convergence she will not call agreement.
"""
        parsed = dg.parse_dossier_output(raw)
        assert parsed["kicker"] == "FOUR NAMINGS OF A DISSOLVED THING"
        assert parsed["headline"].startswith("The Voices Refused")
        assert "convergence" in parsed["subline"].lower()
        assert len(parsed["body_paragraphs"]) == 4   # 3 paras + asterism
        assert "* * *" in parsed["body_paragraphs"]
        assert len(parsed["headnotes"]) == 2
        assert parsed["headnotes"][0]["voice_slug"] == "plato"
        assert parsed["headnotes"][0]["artifact_title"] == "DOCTORS OR COOKS?"
        assert parsed["headnotes"][1]["artifact_title"] == "A PROSTAGMA, ISSUED AT NIGHT"
        assert "front_abstract" in parsed
        assert parsed["front_abstract"].startswith("Four voices")

    def test_parse_missing_fields_defaults(self):
        """Empty output → all fields are empty defaults; no crash."""
        parsed = dg.parse_dossier_output("")
        assert parsed["kicker"] == ""
        assert parsed["headline"] == ""
        assert parsed["body_paragraphs"] == []
        assert parsed["headnotes"] == []
        assert parsed["theme_title_for_dossier"] == ""
        assert parsed["theme_abstract_for_dossier"] == ""

    def test_parse_theme_title_and_abstract(self):
        """B1 (2026-05-04 PM): Claudia emits theme_title_for_dossier +
        theme_abstract_for_dossier for the dossier's Page 3 (theme page) —
        paper-voice short title + publishing-register short abstract
        derived from Researcher's record. Suffix `_for_dossier` matches
        the convention pattern (`theme_title_from_researcher`).
        """
        raw = """**kicker:** A KICKER

**headline:** A headline

**theme_title_for_dossier:** On The Legitimacy Of Algorithmic Sortings

**theme_abstract_for_dossier:** The theme reaches across last night's three sessions, asking what an institution owes when its sorting devices have begun to issue verdicts no human will sign for. The voices answer in four vocabularies; none calls the device legitimate.
"""
        parsed = dg.parse_dossier_output(raw)
        assert parsed["theme_title_for_dossier"] == "On The Legitimacy Of Algorithmic Sortings"
        assert parsed["theme_abstract_for_dossier"].startswith("The theme reaches across")
        assert "four vocabularies" in parsed["theme_abstract_for_dossier"]

    def test_parse_theme_fields_after_body_paragraphs(self):
        """The closing prompt emits theme_title_for_dossier +
        theme_abstract_for_dossier AFTER body_paragraphs (swipe order:
        Page 2 article body → Page 3 theme). body_paragraphs's regex must
        terminate at the theme_title_for_dossier label without swallowing
        the theme content into the body.
        """
        raw = """**kicker:** A KICKER

**headline:** A headline

**subline:** A subline

**front_abstract:** Front teaser.

**body_paragraphs:**
First paragraph of the article body.

Second paragraph.

* * *

Third paragraph.

**theme_title_for_dossier:** Page Three Title

**theme_abstract_for_dossier:** Page Three abstract that orients a reader who arrives directly here.

**headnotes:**
voice_slug: plato
artifact_title: DOCTORS OR COOKS?
framing_text: Plato wrote a dialogue.
"""
        parsed = dg.parse_dossier_output(raw)
        # body_paragraphs stops at theme_title_for_dossier — doesn't bleed
        assert len(parsed["body_paragraphs"]) == 4  # 3 paras + asterism
        assert "Page Three Title" not in " ".join(parsed["body_paragraphs"])
        assert "Page Three abstract" not in " ".join(parsed["body_paragraphs"])
        # theme fields parse cleanly
        assert parsed["theme_title_for_dossier"] == "Page Three Title"
        assert parsed["theme_abstract_for_dossier"].startswith("Page Three abstract")
        # headnotes still parse
        assert len(parsed["headnotes"]) == 1
        assert parsed["headnotes"][0]["artifact_title"] == "DOCTORS OR COOKS?"

    def test_parse_strips_markdown_chrome(self):
        raw = "**kicker:** ***WAIT***\n\n**headline:** _italic stuff_"
        parsed = dg.parse_dossier_output(raw)
        # leading ** stripped
        assert "WAIT" in parsed["kicker"]
        assert "italic stuff" in parsed["headline"]


# --- stamp_runtime_fields ----------------------------------------------


class TestStampRuntime:
    def test_stamp_basic(self):
        parsed = {
            "kicker": "K",
            "headline": "H",
            "subline": "S",
            "body_paragraphs": ["p1", "p2"],
            "headnotes": [{"voice_slug": "plato",
                           "artifact_title": "DOCTORS OR COOKS?",
                           "framing_text": "F-plato"}],
            "front_abstract": "FA",
        }
        dossier = dg.stamp_runtime_fields(
            parsed,
            night=1,
            theme_id="theme_001",
            theme_display_title="On The Question",
            voice_slugs=["plato"],
            voice_name_by_slug={"plato": "the voice of Plato"},
            formulation_by_slug={"plato": "<formulation>"},
        )
        assert dossier["schema_version"] == "2.0"
        assert dossier["kicker"] == "K"
        assert dossier["headline"] == "H"
        assert dossier["body_paragraphs"] == ["p1", "p2"]
        # Headnote enriched with voice_name + formulation_text
        assert dossier["headnotes"][0]["voice_name"] == "the voice of Plato"
        assert dossier["headnotes"][0]["formulation_text"] == "<formulation>"
        assert dossier["headnotes"][0]["artifact_title"] == "DOCTORS OR COOKS?"
        assert dossier["headnotes"][0]["framing_text"] == "F-plato"
        # Metadata
        assert dossier["metadata"]["theme_id"] == "theme_001"
        assert dossier["metadata"]["issue_no"] == 42_193
        assert dossier["metadata"]["vol"] == "CXVI"
        assert dossier["metadata"]["night"] == 1

    def test_stamp_carries_theme_title_and_abstract(self):
        """theme_title_for_dossier + theme_abstract_for_dossier land on
        the dossier output if Claudia emitted them; default to empty
        strings otherwise (microsite can fall back to the upstream theme
        record)."""
        parsed = {
            "kicker": "K",
            "headline": "H",
            "subline": "S",
            "body_paragraphs": [],
            "headnotes": [],
            "front_abstract": "",
            "theme_title_for_dossier": "On The Legitimacy Of The Sortings",
            "theme_abstract_for_dossier": "Across last night's three sessions the question reached for what an institution owes when its sorting devices have begun to issue verdicts no human will sign for.",
        }
        dossier = dg.stamp_runtime_fields(
            parsed,
            night=1,
            theme_id="theme_001",
            theme_display_title="On The Question",
            voice_slugs=[],
            voice_name_by_slug={},
            formulation_by_slug={},
        )
        assert dossier["theme_title_for_dossier"] == "On The Legitimacy Of The Sortings"
        assert dossier["theme_abstract_for_dossier"].startswith("Across last night's")

    def test_stamp_embeds_artifact_text_and_form_in_headnotes(self):
        """Self-contained dossier: each headnote carries the per-voice
        artifact_text body + artifact_form (CSS bundle key) so the
        microsite renders an artifact page from the dossier alone — no
        per-voice file fetch needed.
        """
        parsed = {
            "kicker": "K", "headline": "H", "subline": "S",
            "front_abstract": "FA",
            "body_paragraphs": ["p1"],
            "headnotes": [
                {"voice_slug": "cleopatra",
                 "artifact_title": "A PROSTAGMA, ISSUED AT NIGHT",
                 "framing_text": "Cleopatra issues an ordinance."},
                {"voice_slug": "plato",
                 "artifact_title": "DOCTORS OR COOKS?",
                 "framing_text": "Plato asks one question."},
            ],
        }
        dossier = dg.stamp_runtime_fields(
            parsed,
            night=1,
            theme_id="theme_001",
            theme_display_title="On The Question",
            voice_slugs=["cleopatra", "plato"],
            voice_name_by_slug={"cleopatra": "the voice of Cleopatra",
                                "plato": "the voice of Plato"},
            formulation_by_slug={"cleopatra": "<f-cleo>", "plato": "<f-plato>"},
            artifact_text_by_slug={"cleopatra": "[full prostagma body — γινέσθωι]",
                                   "plato": "[full dialogue body]"},
            artifact_form_by_slug={"cleopatra": "prostagma", "plato": "dialogue"},
        )
        h_cleo = dossier["headnotes"][0]
        h_plato = dossier["headnotes"][1]
        # Both headnotes carry the body + form for self-contained rendering
        assert h_cleo["artifact_text"] == "[full prostagma body — γινέσθωι]"
        assert h_cleo["artifact_form"] == "prostagma"
        assert h_plato["artifact_text"] == "[full dialogue body]"
        assert h_plato["artifact_form"] == "dialogue"

    def test_stamp_artifact_fields_default_empty_when_dicts_omitted(self):
        """Back-compat: if caller doesn't pass the new artifact_*_by_slug
        dicts, headnotes get empty strings rather than crashing."""
        parsed = {
            "kicker": "K", "headline": "H", "subline": "S",
            "body_paragraphs": [], "headnotes": [], "front_abstract": "",
        }
        dossier = dg.stamp_runtime_fields(
            parsed,
            night=1,
            theme_id="theme_001",
            theme_display_title="X",
            voice_slugs=["plato"],
            voice_name_by_slug={"plato": "Plato"},
            formulation_by_slug={"plato": "x"},
        )
        h = dossier["headnotes"][0]
        assert h["artifact_text"] == ""
        assert h["artifact_form"] == ""

    def test_stamp_theme_fields_default_empty_when_missing(self):
        """If parsed dict omits theme_title_for_dossier /
        theme_abstract_for_dossier, dossier carries empty strings —
        defensive against parser misses."""
        parsed = {
            "kicker": "K", "headline": "H", "subline": "",
            "body_paragraphs": [], "headnotes": [], "front_abstract": "",
        }
        dossier = dg.stamp_runtime_fields(
            parsed,
            night=1,
            theme_id="theme_001",
            theme_display_title="X",
            voice_slugs=[],
            voice_name_by_slug={},
            formulation_by_slug={},
        )
        assert dossier["theme_title_for_dossier"] == ""
        assert dossier["theme_abstract_for_dossier"] == ""
        # Colophon present
        assert "Editor's desk" in dossier["colophon"]
        assert "Issue No. 42,193" in dossier["colophon"]

    def test_stamp_missing_voice_in_parsed_headnotes(self):
        """Routing routed plato + cleopatra here; Claudia's parsed output
        only had artifact_title + framing for plato. The other voice still
        appears in headnotes (with empty artifact_title + framing_text) —
        never silently drop."""
        parsed = {
            "kicker": "K", "headline": "H", "subline": "S",
            "body_paragraphs": [],
            "headnotes": [{"voice_slug": "plato",
                           "artifact_title": "DOCTORS OR COOKS?",
                           "framing_text": "F-plato"}],
            "front_abstract": "",
        }
        dossier = dg.stamp_runtime_fields(
            parsed,
            night=1, theme_id="t1", theme_display_title="T",
            voice_slugs=["plato", "cleopatra"],
            voice_name_by_slug={"plato": "P", "cleopatra": "C"},
            formulation_by_slug={"plato": "fp", "cleopatra": "fc"},
        )
        slugs = [h["voice_slug"] for h in dossier["headnotes"]]
        assert slugs == ["plato", "cleopatra"]
        # Cleopatra has empty artifact_title + framing_text but voice_name +
        # formulation_text stamped
        cleo = dossier["headnotes"][1]
        assert cleo["voice_name"] == "C"
        assert cleo["formulation_text"] == "fc"
        assert cleo["artifact_title"] == ""
        assert cleo["framing_text"] == ""
        # Plato's artifact_title preserved
        assert dossier["headnotes"][0]["artifact_title"] == "DOCTORS OR COOKS?"

    def test_issue_numbers_per_night(self):
        for night, expected in ((1, 42193), (2, 42194), (3, 42195)):
            parsed = {"kicker": "", "headline": "", "subline": "",
                      "body_paragraphs": [], "headnotes": [], "front_abstract": ""}
            dossier = dg.stamp_runtime_fields(
                parsed, night=night, theme_id="t", theme_display_title="T",
                voice_slugs=[], voice_name_by_slug={}, formulation_by_slug={},
            )
            assert dossier["metadata"]["issue_no"] == expected
            assert f"Issue No. {expected:,}" in dossier["colophon"]


# --- generate_dossier (end-to-end with mocked Anthropic) -----------------


class TestGenerateDossier:
    def test_end_to_end_mocked(self, run_dir, monkeypatch):
        """Mock the Anthropic call; verify the function orchestrates
        briefing → user prompt → parse → stamp without crashing."""
        for slug in ("plato", "cleopatra"):
            _write_briefing(run_dir, slug, "theme_001",
                            narrative=f"<{slug} briefing>")
            _write_artifact(run_dir, slug, council_member=slug.title(),
                            artifact_text=f"<{slug} artifact>")

        # Mock stream_voice_call to return a v2-shaped output without API call.
        mock_response = """**kicker:** TEST KICKER
**headline:** Test Headline About An Event
**subline:** Test deck
**body_paragraphs:**
First paragraph of the test article.

Second paragraph.

**headnotes:**
voice_slug: plato
artifact_title: TEST PLATO TITLE
framing_text: Plato framed thus.
voice_slug: cleopatra
artifact_title: A TEST PROSTAGMA
framing_text: Cleopatra framed otherwise.

**front_abstract:** Test teaser drawn from article opening.
"""
        mock_usage = MagicMock(input_tokens=1000, output_tokens=500,
                               cache_creation_input_tokens=0, cache_read_input_tokens=0)
        mock_final = MagicMock(usage=mock_usage)
        monkeypatch.setattr(dg, "stream_voice_call",
                            lambda *a, **kw: (mock_response, "", mock_final, 100))

        # Mock client (not used since stream_voice_call is mocked)
        client = MagicMock()
        system_prompt = ("PREFIX", "TAIL")

        dossier = dg.generate_dossier(
            theme_id="theme_001",
            voice_slugs=["plato", "cleopatra"],
            run_dir=run_dir,
            night=1,
            system_prompt=system_prompt,
            client=client,
        )

        assert dossier["kicker"] == "TEST KICKER"
        assert dossier["headline"] == "Test Headline About An Event"
        assert len(dossier["body_paragraphs"]) == 2
        assert len(dossier["headnotes"]) == 2
        assert dossier["headnotes"][0]["voice_name"] == "the voice of Plato"
        assert dossier["headnotes"][0]["artifact_title"] == "TEST PLATO TITLE"
        assert dossier["headnotes"][1]["voice_name"] == "the voice of Cleopatra"
        assert dossier["headnotes"][1]["artifact_title"] == "A TEST PROSTAGMA"
        assert dossier["metadata"]["input_tokens"] == 1000
        assert dossier["metadata"]["output_tokens"] == 500
        assert dossier["metadata"]["model"]   # set
        assert dossier["schema_version"] == "2.0"
