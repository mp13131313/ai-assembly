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

# 2026-04-23: canonicalize archive landing-page URLs to raw-text URLs.
# Pass 1.6 merge frequently emits human-friendly catalogue URLs (cite-style)
# rather than raw-text download URLs. Fetching the catalogue returns ~5KB of
# HTML metadata instead of the actual literary content; downstream Pass 1d
# excerpt selection then has nothing to select from. Canonicalize at extract
# time so the works/passages chunks retain the cite-friendly URL while the
# fetcher gets the raw text. Affects all voices with public-domain corpora
# (Plato, Cleopatra, Ibn Battuta, Scheherazade, Ada Lovelace, Dostoevsky).
_GUTENBERG_LANDING_RE = re.compile(
    r"^(https?://)(?:www\.)?gutenberg\.org/ebooks/(\d+)(?:[/?#].*)?$",
    re.IGNORECASE,
)
_ARCHIVE_LANDING_RE = re.compile(
    r"^(https?://)(?:www\.)?archive\.org/details/([^/?#]+)/?(?:[?#].*)?$",
    re.IGNORECASE,
)


def _canonicalize_to_text_url(url: str) -> str:
    """Rewrite known landing-page URLs to their raw-text equivalents.

    Gutenberg: https://www.gutenberg.org/ebooks/<id>
            -> https://www.gutenberg.org/files/<id>/<id>-0.txt
    Archive.org: https://archive.org/details/<id>
              -> https://archive.org/download/<id>/<id>_djvu.txt

    Returns the original URL unchanged if no pattern matches. Best-effort:
    not every archive.org item has a `_djvu.txt` derivative (some have
    `_text.txt`, some have neither — a fetch returning HTML will surface in
    the Pass 1c REVIEW GATE artifact for operator inspection).
    """
    m = _GUTENBERG_LANDING_RE.match(url)
    if m:
        ebook_id = m.group(2)
        return f"https://www.gutenberg.org/files/{ebook_id}/{ebook_id}-0.txt"
    m = _ARCHIVE_LANDING_RE.match(url)
    if m:
        item_id = m.group(2)
        return f"https://archive.org/download/{item_id}/{item_id}_djvu.txt"
    return url


def _clean(url: str) -> str:
    """Strip trailing punctuation, then canonicalize landing-page URLs."""
    while url and url[-1] in _TRAILING_STRIP:
        url = url[:-1]
    return _canonicalize_to_text_url(url)


def _extract_from_text(text: str) -> list[str]:
    return [_clean(u) for u in _URL_RE.findall(text or "")]


def _walk_for_urls(obj: Any, work_title: str = "") -> list[dict[str, Any]]:
    """Recursively walk a JSON-like structure and extract URL entries.

    Added 2026-04-23 per 1-arch-07 post-test follow-up: URLs in arch-03
    merge output live at `passages[].citations[].url` (nested list-of-dicts),
    which the flat field-iteration in extract_urls_from_{works,passages}()
    misses. This walker handles any nesting depth and also recognizes the
    convention where a dict has a `url` key whose string value IS the URL
    (no regex extraction needed).

    `work_title` propagates the last-known title attribution down the tree.
    """
    out: list[dict[str, Any]] = []
    if isinstance(obj, dict):
        # Update title context if this dict carries one
        local_title = obj.get("work_title") or obj.get("title") or obj.get("work") or work_title
        # Shortcut: if this dict has a url field pointing at a string, treat it as a URL directly
        if isinstance(obj.get("url"), str) and obj["url"].strip():
            u = _clean(obj["url"].strip())
            # Accept if looks URL-ish (has scheme or domain dot)
            if u and ("://" in u or "." in u):
                out.append({
                    "url": u,
                    "work_title": local_title or "",
                    "source": _source_for_url(u),
                    "license_or_access_note": obj.get("license_or_access_note")
                        or obj.get("access_note")
                        or obj.get("license"),
                })
        # Recurse through all fields (including string fields scanned for URLs)
        for k, v in obj.items():
            if k == "url":
                continue  # handled above
            if isinstance(v, str):
                for u in _extract_from_text(v):
                    out.append({
                        "url": u,
                        "work_title": local_title or "",
                        "source": _source_for_url(u),
                        "license_or_access_note": None,
                    })
            else:
                out.extend(_walk_for_urls(v, local_title))
    elif isinstance(obj, list):
        for item in obj:
            out.extend(_walk_for_urls(item, work_title))
    elif isinstance(obj, str):
        for u in _extract_from_text(obj):
            out.append({
                "url": u,
                "work_title": work_title or "",
                "source": _source_for_url(u),
                "license_or_access_note": None,
            })
    return out


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

    2026-04-23: uses _walk_for_urls() for full recursion into nested
    structures. Handles both conventions: (1) URLs embedded in string
    fields (regex-extracted), (2) dicts with explicit `url` key whose
    value IS the URL (common in passages[].citations[].url shape under
    arch-03 merge). Flat-iteration extract_urls_from_* helpers retained
    for backward compatibility.
    """
    seen: dict[str, dict[str, Any]] = {}
    for chunk in (works_chunk or {}, passages_chunk or {}):
        for entry in _walk_for_urls(chunk):
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
