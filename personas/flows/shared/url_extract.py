"""Deterministic URL extraction from Pass 1.6 chunk outputs.

Replaces the `urls` chunk key removed under 1-arch-07 (2026-04-22). URLs are
now extracted mechanically from `passages[].citation` strings and `works[].*`
url/access_note fields rather than LLM-emitted as a separate chunk. This
eliminates drift risk between urls.json and the URLs already embedded in
sibling chunk files.

Called by Pass 1c-extract (in `run_persona_pipeline.py`) to populate the
URL inventory for primary-text fetch. Pure Python, no LLM.

See _workspace/planning/PIPELINE_REVIEW_FIXES.md § 1-arch-07 for rationale.
"""
from __future__ import annotations

import re
from typing import Any

_URL_RE = re.compile(r"https?://[^\s\])}>,\"']+", re.IGNORECASE)

# Strip common trailing punctuation that isn't part of the URL itself.
_TRAILING_STRIP = ".,;:!?)]}'\"\u2019\u201d"


def _clean(url: str) -> str:
    """Strip trailing punctuation noise that regex captured."""
    while url and url[-1] in _TRAILING_STRIP:
        url = url[:-1]
    return url


def _extract_from_text(text: str) -> list[str]:
    return [_clean(u) for u in _URL_RE.findall(text or "")]


def extract_urls_from_works(works_chunk: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract URL entries from the Pass 1.6 `works` chunk output.

    `works_chunk` is the loaded JSON of `pass_1_6/works.json` — i.e. the
    `Works` Pydantic model dumped as dict. Structure:
      {"works": [WorkEntry, ...], "bibliographic_scholarly_context": "..."}

    Current `WorkEntry` schema does not carry an explicit `url` field — URLs
    historically leaked into `canonical_reference` / `note` / the separate
    URLs chunk. We scan all string-valued fields of each entry for URLs.
    Each entry returned has `url`, `work_title`, `source` fields to match
    the old URLEntry shape so downstream consumers don't need to change.
    """
    out: list[dict[str, Any]] = []
    for work in works_chunk.get("works", []) or []:
        title = work.get("title", "")
        for field_name, value in work.items():
            if not isinstance(value, str):
                continue
            for url in _extract_from_text(value):
                out.append(
                    {
                        "url": url,
                        "work_title": title,
                        "source": _source_for_url(url),
                        "license_or_access_note": None,
                    }
                )
    return out


def extract_urls_from_passages(passages_chunk: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract URL entries from the Pass 1.6 `passages` chunk output.

    Each passage's `citation` (and other string fields) is scanned for
    URLs. The `work_title` from the passage entry is the best available
    attribution.
    """
    out: list[dict[str, Any]] = []
    for passage in passages_chunk.get("passages", []) or []:
        title = passage.get("work_title", "") or passage.get("title", "")
        for field_name, value in passage.items():
            if not isinstance(value, str):
                continue
            for url in _extract_from_text(value):
                out.append(
                    {
                        "url": url,
                        "work_title": title,
                        "source": _source_for_url(url),
                        "license_or_access_note": None,
                    }
                )
    return out


def extract_urls(
    works_chunk: dict[str, Any] | None,
    passages_chunk: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    """Combined extraction: works + passages, deduplicated by URL.

    Returns a list of URLEntry-shaped dicts (url, work_title, source,
    license_or_access_note) in stable order: first-seen wins for dedup.
    """
    seen: dict[str, dict[str, Any]] = {}
    for src_fn, src_chunk in (
        (extract_urls_from_works, works_chunk or {}),
        (extract_urls_from_passages, passages_chunk or {}),
    ):
        for entry in src_fn(src_chunk):
            if entry["url"] not in seen:
                seen[entry["url"]] = entry
    return list(seen.values())


_SOURCE_PATTERNS: tuple[tuple[str, str], ...] = (
    ("gutenberg.org", "Project Gutenberg"),
    ("archive.org", "Archive.org"),
    ("rvb.ru", "Russian Virtual Library"),
    ("feb-web.ru", "FEB"),
    ("az.lib.ru", "lib.ru"),
    ("traumlibrary.ru", "TraumLibrary"),
    ("perseus.tufts.edu", "Perseus"),
    ("standardebooks.org", "Standard Ebooks"),
    ("books.google", "Google Books"),
    ("fedordostoevsky.ru", "Dostoevsky Group"),
    ("bloggerskaramazov.com", "NADS Blog"),
    ("sarahjyoung.com", "Sarah J. Young"),
    ("dlls.univr.it", "Dostoevsky Studies"),
    ("wikisource.org", "Wikisource"),
    ("hathitrust.org", "HathiTrust"),
)


def _source_for_url(url: str) -> str:
    """Best-effort attribution label based on URL host. Falls back to 'web'."""
    u = url.lower()
    for pattern, label in _SOURCE_PATTERNS:
        if pattern in u:
            return label
    return "web"
