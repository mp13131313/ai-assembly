"""Pass 1c — Primary Text Fetch.

Reads voice_input.primary_text_sources (list of HTTP URLs) and downloads the
plaintext, stripping Project Gutenberg headers/footers when present.

Output: list of {url, source, text, char_count} saved to
runs/<slug>/01_research/primary_texts.json
"""
from __future__ import annotations
import re
import urllib.request
from pathlib import Path
from typing import Any

GUTENBERG_START = re.compile(r"\*\*\*\s*START OF (?:THE|THIS) PROJECT GUTENBERG.*?\*\*\*", re.I)
GUTENBERG_END = re.compile(r"\*\*\*\s*END OF (?:THE|THIS) PROJECT GUTENBERG.*?\*\*\*", re.I)


def _strip_gutenberg(text: str) -> tuple[str, str]:
    """Return (cleaned_body, source_label). Cleans Project Gutenberg boilerplate."""
    s = GUTENBERG_START.search(text)
    e = GUTENBERG_END.search(text)
    if s and e and s.end() < e.start():
        return text[s.end():e.start()].strip(), "gutenberg"
    return text.strip(), "raw"


def fetch_url(url: str, timeout: int = 30) -> dict[str, Any]:
    """Fetch a single URL; return {url, source, text, char_count}."""
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (AI-Assembly-Persona-Pipeline)"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read().decode("utf-8", errors="ignore")
    cleaned, source = _strip_gutenberg(raw)
    return {"url": url, "source": source, "text": cleaned, "char_count": len(cleaned)}


def fetch_all(sources: list[str]) -> list[dict[str, Any]]:
    """Fetch each URL; on failure record an error entry instead of raising."""
    out = []
    for url in sources:
        try:
            out.append(fetch_url(url))
        except Exception as e:
            out.append({"url": url, "source": "error", "text": "", "char_count": 0,
                        "error": f"{type(e).__name__}: {e}"})
    return out
