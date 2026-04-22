"""Pass 1c — Primary Text Fetch.

Reads voice_input.primary_text_sources (list of HTTP URLs) and downloads the
plaintext, stripping Project Gutenberg headers/footers when present.

Output: list of {url, source, text, char_count} saved to
runs/<slug>/01_research/primary_texts.json

SECURITY: _check_url uses getaddrinfo (all A records) for SSRF checks. Still
TOCTOU-vulnerable — urlopen resolves the hostname again, and DNS rebinding
could return a private IP between checks. Acceptable for the current vetted
URL set (Wikipedia/Gutenberg/academic). Not acceptable if this pipeline ever
accepts user-controlled URLs — upgrade to a custom opener that pins the
pre-resolved IP into the socket connect() call.
"""
from __future__ import annotations
import ipaddress
import re
import socket
import time
import urllib.parse
import urllib.request
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

try:
    from bs4 import BeautifulSoup as _BS4
    _HAS_BS4 = True
except ImportError:
    _HAS_BS4 = False

GUTENBERG_START = re.compile(r"\*\*\*\s*START OF (?:THE|THIS) PROJECT GUTENBERG.*?\*\*\*", re.I)
GUTENBERG_END = re.compile(r"\*\*\*\s*END OF (?:THE|THIS) PROJECT GUTENBERG.*?\*\*\*", re.I)

# Perseus Digital Library XML wrapper pattern
_PERSEUS_XML = re.compile(r"<tei[^>]*>.*?</tei>", re.I | re.S)
# Wikisource / MediaWiki content wrapper
_WIKISOURCE_CONTENT = re.compile(
    r'<div[^>]+class="[^"]*(?:mw-content-text|mw-parser-output)[^"]*"[^>]*>(.*?)</div>',
    re.I | re.S,
)

# Max bytes accepted per URL — prevents memory exhaustion on large texts.
MAX_RESPONSE_BYTES = 5 * 1024 * 1024  # 5 MB

# Retry config (1c-02): one retry on transient errors with backoff.
_MAX_RETRIES = 1
_RETRY_BACKOFF_S = 10

# Parallelism config (1c-01): cap workers to avoid hammering any one host.
_FETCH_WORKERS = 4

# Politeness config (1c-06): per-domain sleep to avoid rate-limit blocks.
_DOMAIN_DELAY_S = 0.5

# RFC 1918 + loopback + link-local ranges — never fetch these on a VM.
_PRIVATE_NETS = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
]


def _check_url(url: str) -> None:
    """Raise ValueError for disallowed schemes or RFC-1918 destinations.

    Uses getaddrinfo (all A/AAAA records) rather than gethostbyname (one
    record) to catch multi-homed hosts where any resolved IP is private.
    """
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"Disallowed URL scheme {parsed.scheme!r}; only http/https allowed")
    host = parsed.hostname or ""
    try:
        results = socket.getaddrinfo(host, None)
    except socket.gaierror:
        # If resolution fails, let urlopen handle the error naturally.
        return
    for (_, _, _, _, sockaddr) in results:
        raw_ip = sockaddr[0]
        try:
            addr = ipaddress.ip_address(raw_ip)
        except ValueError:
            continue
        for net in _PRIVATE_NETS:
            if addr in net:
                raise ValueError(
                    f"URL {url!r} resolves to private/loopback address {addr}; blocked"
                )


def _html_to_text(html: str, url: str) -> str:
    """Convert HTML to plain text. Uses BeautifulSoup if available; falls back
    to simple tag stripping. Attempts to extract main content from Perseus /
    Wikisource wrappers before full-page extraction.
    """
    # Try Perseus XML
    m = _PERSEUS_XML.search(html)
    if m:
        html = m.group(0)
    # Try Wikisource / MediaWiki content wrapper
    m = _WIKISOURCE_CONTENT.search(html)
    if m:
        html = m.group(1)

    if _HAS_BS4:
        soup = _BS4(html, "html.parser")
        for tag in soup(["script", "style", "nav", "header", "footer"]):
            tag.decompose()
        return soup.get_text(separator="\n").strip()
    # Fallback: strip tags with regex
    return re.sub(r"<[^>]+>", " ", html).strip()


def _strip_boilerplate(raw: str, content_type: str, url: str) -> tuple[str, str]:
    """Return (cleaned_body, source_label).

    Applies appropriate stripping based on content-type and URL pattern:
    - Project Gutenberg plaintext: trim *** START / END *** wrappers
    - HTML (any source): convert to plain text, then Gutenberg-strip if needed
    - Raw: return as-is
    """
    is_html = "text/html" in content_type or "application/xhtml" in content_type

    if is_html:
        text = _html_to_text(raw, url)
        # Still apply Gutenberg strip in case HTML Gutenberg edition
        s = GUTENBERG_START.search(text)
        e = GUTENBERG_END.search(text)
        if s and e and s.end() < e.start():
            return text[s.end():e.start()].strip(), "gutenberg_html"
        return text, "html"

    # Plaintext path
    s = GUTENBERG_START.search(raw)
    e = GUTENBERG_END.search(raw)
    if s and e and s.end() < e.start():
        return raw[s.end():e.start()].strip(), "gutenberg"

    return raw.strip(), "raw"


def _decode_response(raw_bytes: bytes, content_type: str) -> str:
    """Decode bytes honouring charset declared in Content-Type."""
    # Extract charset="..." or charset=... from content-type header
    m = re.search(r"charset=([^\s;\"']+)", content_type, re.I)
    charset = m.group(1).strip("\"'") if m else "utf-8"
    try:
        return raw_bytes.decode(charset, errors="ignore")
    except (LookupError, UnicodeDecodeError):
        return raw_bytes.decode("utf-8", errors="ignore")


def fetch_url(url: str, timeout: int = 30) -> dict[str, Any]:
    """Fetch a single URL; return {url, source, text, char_count}.

    Only http/https URLs are allowed. Private/loopback IPs are rejected.
    Response body is capped at MAX_RESPONSE_BYTES.
    Content-Type is inspected; HTML responses are converted to plain text.
    Charset declared in Content-Type is honoured (fixes Latin-1 Gutenberg).
    """
    _check_url(url)
    req = urllib.request.Request(
        url, headers={"User-Agent": "Mozilla/5.0 (AI-Assembly-Persona-Pipeline)"}
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        content_type = r.headers.get("Content-Type", "")
        raw_bytes = r.read(MAX_RESPONSE_BYTES + 1)
    if len(raw_bytes) > MAX_RESPONSE_BYTES:
        raise ValueError(
            f"Response from {url!r} exceeds {MAX_RESPONSE_BYTES // 1024 // 1024} MB cap; skipping"
        )
    raw = _decode_response(raw_bytes, content_type)
    cleaned, source = _strip_boilerplate(raw, content_type, url)
    return {"url": url, "source": source, "text": cleaned, "char_count": len(cleaned)}


def _fetch_with_retry(url: str) -> dict[str, Any]:
    """Fetch with one retry on transient errors (1c-02)."""
    last_exc: Exception | None = None
    for attempt in range(_MAX_RETRIES + 1):
        try:
            return fetch_url(url)
        except (OSError, urllib.error.URLError) as e:
            last_exc = e
            if attempt < _MAX_RETRIES:
                time.sleep(_RETRY_BACKOFF_S)
        except ValueError:
            raise  # Non-transient (SSRF block, size cap) — don't retry
    assert last_exc is not None
    raise last_exc


def fetch_all(sources: list[str]) -> list[dict[str, Any]]:
    """Fetch each URL in parallel (ThreadPoolExecutor); on failure record an
    error entry instead of raising. Applies per-domain politeness delay.
    """
    results: dict[str, dict[str, Any]] = {}
    # Track last request time per domain for rate-limiting (1c-06)
    last_request: dict[str, float] = defaultdict(float)

    def _fetch_one(url: str) -> dict[str, Any]:
        domain = urllib.parse.urlparse(url).netloc
        elapsed = time.monotonic() - last_request[domain]
        if elapsed < _DOMAIN_DELAY_S:
            time.sleep(_DOMAIN_DELAY_S - elapsed)
        last_request[domain] = time.monotonic()
        try:
            return _fetch_with_retry(url)
        except Exception as e:
            return {"url": url, "source": "error", "text": "", "char_count": 0,
                    "error": f"{type(e).__name__}: {e}"}

    with ThreadPoolExecutor(max_workers=_FETCH_WORKERS) as pool:
        futures = {pool.submit(_fetch_one, url): url for url in sources}
        for fut in as_completed(futures):
            url = futures[fut]
            results[url] = fut.result()

    # Preserve input order
    return [results[url] for url in sources]
