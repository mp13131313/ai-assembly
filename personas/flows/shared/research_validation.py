"""Smoke-test validators for Pass 1a / 1b research output.

The Perplexity + Gemini prompts ask for specific content shapes (period-
vocabulary in original language, evidence tags, counter-tradition block
if hostile_sources, per-section structure). The returned text is free-form
markdown — Pydantic can't validate it. These validators grep-check for
the structural asks and emit WARNINGS (not errors). Non-blocking: Pass 1.1
merge will attempt the Boddice-shaped synthesis regardless; warnings
surface "this dossier is thin in area X" early so the curator can decide
to re-run Phase 0.5 with a tighter `--hint` rather than discovering the
thinness at Pass 2 quality review.

Design: every check returns (ok: bool, message: str). The orchestrator
prints WARNING for failures and continues.
"""
from __future__ import annotations

import re
from dataclasses import dataclass


# Minimum counts per voice type. Empirical floors — dossiers below this
# produce thin chunked-merge output.
_MIN_EVIDENCE_TAGS_HUMAN = 10
_MIN_EVIDENCE_TAGS_NON_HUMAN = 5
_MIN_PERIOD_VOCABULARY_HUMAN = 3  # 5-10 requested; 3 is bottom-of-acceptable
_MIN_SECTION_HEADERS = 4  # 6 requested; 4 is bottom-of-acceptable

# Heuristic: period-vocabulary in original language will contain non-ASCII
# characters (Greek, Arabic, Sanskrit, Hebrew, CJK, etc.) OR be flagged
# with explicit `[foreign term]` brackets. ASCII-only output is a red
# flag for voices whose vocabulary lives in other scripts.
_NON_ASCII_RE = re.compile(r"[^\x00-\x7F]")

# Section headers of the Pass 1a 6-section structure. Case-insensitive
# substring match; any of these keywords qualifies.
_SECTION_HINTS = [
    ("section 1", "foundation"), ("section 2", "framework"),
    ("section 3", "reasoning"), ("section 4", "voice"),
    ("section 5", "boundaries"), ("section 6", "primary"),
]

# Evidence-tag patterns. Pass 1a (post-2026-04 revision) asks Perplexity for
# the lighter [primary]/[consensus]/[contested] set; the chunked merge prompts
# (Opus reads) apply the full 5-Boddice-tag rigor. Validator accepts both so
# either era of dossier passes the smoke test.
_EVIDENCE_TAG_RE = re.compile(
    r"\[(?:"
    # Pass 1a lighter set (Perplexity-friendly):
    r"primary|consensus|contested"
    # Boddice 5-tag set (chunked-merge rigor):
    r"|stated|scholarly[_ ]consensus|inference"
    r"|experiential[_ ]reconstruction|projection[_ ]warning"
    # Hostile-source addenda:
    r"|hostile[_ ]source|hostile source|reconstruction|own[_ ]voice|own voice"
    r")[:\]]",
    re.IGNORECASE,
)

# Counter-tradition markers (required when hostile_sources=True).
_COUNTER_TRADITION_RE = re.compile(
    r"\b(?:counter[- ]tradition|read(?:ing)? against the grain|"
    r"against[- ]the[- ]grain|\[reconstruction\]|\[own voice\])",
    re.IGNORECASE,
)


@dataclass
class Check:
    name: str
    ok: bool
    message: str


def validate_perplexity_dossier(
    *,
    text: str,
    voice_type: str,
    hostile_sources: bool,
) -> list[Check]:
    """Smoke-test a Perplexity dossier against the Pass 1a prompt's asks.

    Returns a list of Check records. Callers print WARNING for any ok=False
    and continue — this is not a blocking gate. Phase L quality review is
    the real validation.
    """
    results: list[Check] = []

    # 1. Total length — dossier shouldn't be suspiciously short.
    word_count = len(text.split())
    min_words = 5000 if voice_type == "non_human" else 8000
    results.append(Check(
        "word_count",
        word_count >= min_words,
        f"{word_count} words (floor {min_words}; well-documented voices usually 15–30k).",
    ))

    # 2. Section coverage — 6-section structure.
    detected = sum(
        1 for sec, kw in _SECTION_HINTS
        if sec in text.lower() or kw in text.lower()
    )
    results.append(Check(
        "section_coverage",
        detected >= _MIN_SECTION_HEADERS,
        f"{detected}/6 section markers detected (floor {_MIN_SECTION_HEADERS}).",
    ))

    # 3. Evidence tags — every claim is supposed to carry one.
    tag_count = len(_EVIDENCE_TAG_RE.findall(text))
    floor = _MIN_EVIDENCE_TAGS_NON_HUMAN if voice_type == "non_human" else _MIN_EVIDENCE_TAGS_HUMAN
    results.append(Check(
        "evidence_tags",
        tag_count >= floor,
        f"{tag_count} evidence tags (floor {floor}). "
        f"Pass 1.1–1.6 need these for validation.",
    ))

    # 4. Period vocabulary in original-language script (human + fictional voices).
    if voice_type in ("human", "fictional"):
        non_ascii_chars = len(_NON_ASCII_RE.findall(text))
        # Allow ASCII-transliterated terms (e.g. "sabr", "episteme") via the
        # presence of italic-style markers or parenthetical glosses.
        gloss_markers = len(re.findall(
            r"\*[a-zA-Z\-]{3,20}\*|\([a-zA-Z\-]{3,20}\)",
            text,
        ))
        score = (1 if non_ascii_chars >= 20 else 0) + (1 if gloss_markers >= 5 else 0)
        results.append(Check(
            "period_vocabulary",
            score >= 1,
            f"non-ASCII chars={non_ascii_chars}, gloss markers={gloss_markers}. "
            f"Pre-1820 voices need period vocabulary in original script OR "
            f"with explicit glosses. 0/2 signals generic Anglophone output.",
        ))

    # 5. Counter-tradition block (required when hostile_sources=True).
    if hostile_sources:
        counter_count = len(_COUNTER_TRADITION_RE.findall(text))
        results.append(Check(
            "counter_tradition",
            counter_count >= 3,
            f"{counter_count} counter-tradition markers (floor 3). "
            f"hostile_sources=True requires LEAD with [reconstruction] + "
            f"[own voice] material; absence signals the hostile-sources "
            f"branch didn't fire correctly in the prompt.",
        ))

    return results


def validate_gemini_scan(*, text: str, voice_type: str) -> list[Check]:
    """Lighter-touch check on Gemini broad-scan output.

    Pass 1b is intentionally thinner than Pass 1a (catches what Perplexity
    misses); we check for minimum length + at least some citations.
    """
    results: list[Check] = []
    word_count = len(text.split())
    results.append(Check(
        "word_count",
        word_count >= 500,
        f"{word_count} words (floor 500 — Gemini filtering or max_output_tokens "
        f"hit would produce empty/very-short text).",
    ))
    # Citations — Pass 1b prompt asks every claim to carry a source.
    citation_hints = len(re.findall(
        r"\(\d{4}\)|\[\w[^\]]*\d{4}[^\]]*\]|(?:et al\.|Press,|Journal)",
        text,
    ))
    results.append(Check(
        "citations",
        citation_hints >= 5,
        f"{citation_hints} citation-like markers (floor 5).",
    ))
    return results


def print_warnings(
    checks: list[Check],
    source: str,
    stamp_fn,
) -> int:
    """Print WARNING for each failed check. Returns count of failures.

    Pass stamp_fn=print or your runner's timestamped logger.
    """
    failures = [c for c in checks if not c.ok]
    if not failures:
        stamp_fn(f"  {source} smoke-tests: {len(checks)}/{len(checks)} pass")
        return 0
    stamp_fn(f"  {source} smoke-tests: {len(checks) - len(failures)}/{len(checks)} pass, "
             f"{len(failures)} WARNING(s):")
    for c in failures:
        stamp_fn(f"    ⚠ {c.name}: {c.message}")
    return len(failures)
