"""Wikipedia Search + Summary REST API helpers."""
from __future__ import annotations

import urllib.parse

import requests

_SEARCH_URL = "https://en.wikipedia.org/w/api.php"
_SUMMARY_URL = "https://en.wikipedia.org/api/rest_v1/page/summary/{}"
_HEADERS = {"User-Agent": "ai-assembly-persona-pipeline/1.0 (research tool; contact: peschelero@gmail.com)"}


def search(query: str, limit: int = 5) -> list[dict]:
    """Return list of {title, description, url} dicts from Wikipedia OpenSearch."""
    params = {
        "action": "opensearch",
        "search": query,
        "limit": limit,
        "format": "json",
        "redirects": "resolve",
    }
    resp = requests.get(_SEARCH_URL, params=params, timeout=10, headers=_HEADERS)
    resp.raise_for_status()
    data = resp.json()
    # OpenSearch response: [query, [titles], [descriptions], [urls]]
    titles = data[1] if len(data) > 1 else []
    descriptions = data[2] if len(data) > 2 else []
    urls = data[3] if len(data) > 3 else []
    results = []
    for i, title in enumerate(titles):
        results.append({
            "title": title,
            "description": descriptions[i] if i < len(descriptions) else "",
            "url": urls[i] if i < len(urls) else f"https://en.wikipedia.org/wiki/{urllib.parse.quote(title)}",
        })
    return results


def summary(title_or_url: str) -> dict:
    """Return {title, extract, description, url} for a specific Wikipedia page.

    Accepts either a page title or a full Wikipedia URL.
    """
    if title_or_url.startswith("http"):
        # Extract title from URL: https://en.wikipedia.org/wiki/Cleopatra -> Cleopatra
        title = title_or_url.rstrip("/").split("/wiki/")[-1]
    else:
        title = title_or_url
    title_encoded = urllib.parse.quote(title, safe="")
    url = _SUMMARY_URL.format(title_encoded)
    resp = requests.get(url, timeout=10, headers={**_HEADERS, "Accept": "application/json"})
    resp.raise_for_status()
    data = resp.json()
    return {
        "title": data.get("title", title),
        "extract": data.get("extract", ""),
        "description": data.get("description", ""),
        "url": data.get("content_urls", {}).get("desktop", {}).get("page",
               f"https://en.wikipedia.org/wiki/{title_encoded}"),
    }
