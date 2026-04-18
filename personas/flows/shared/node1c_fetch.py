"""Pass 1c — Primary Text Fetch.

Reads voice_input.primary_text_sources (list of HTTP URLs) and downloads the
plaintext, stripping Project Gutenberg headers/footers when present.

Output: list of {url, source, text, char_count} saved to
runs/<slug>/01_research/primary_texts.json

SECURITY: _check_url uses gethostbyname for its SSRF check, which is
TOCTOU-vulnerable — urlopen will resolve the hostname a second time,
and DNS rebinding could return a private IP. Also, gethostbyname only
returns one A record; multi-record DNS answers aren't fully checked.
Acceptable for the pre-conference voice-config URL set (small, vetted,
Wikipedia/Gutenberg/academic domains). Not acceptable if this is ever
used on user-controlled URLs — swap to getaddrinfo + pin the resolved
IP into a custom opener, or use requests with a hook that blocks the
post-resolve connection.
"""
from __future__ import annotations
import ipaddress
import re
import socket
import urllib.parse
import urllib.request
from typing import Any

GUTENBERG_START = re.compile(r"\*\*\*\s*START OF (?:THE|THIS) PROJECT GUTENBERG.*?\*\*\*", re.I)
GUTENBERG_END = re.compile(r"\*\*\*\s*END OF (?:THE|THIS) PROJECT GUTENBERG.*?\*\*\*", re.I)

# Max bytes accepted per URL — prevents memory exhaustion on large texts.
MAX_RESPONSE_BYTES = 5 * 1024 * 1024  # 5 MB

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
    """Raise ValueError for disallowed schemes or RFC-1918 destinations."""
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"Disallowed URL scheme {parsed.scheme!r}; only http/https allowed")
    host = parsed.hostname or ""
    try:
        addr = ipaddress.ip_address(socket.gethostbyname(host))
    except (socket.gaierror, ValueError):
        # If resolution fails, let urlopen handle the error naturally.
        return
    for net in _PRIVATE_NETS:
        if addr in net:
            raise ValueError(f"URL {url!r} resolves to private/loopback address {addr}; blocked")


def _strip_gutenberg(text: str) -> tuple[str, str]:
    """Return (cleaned_body, source_label). Cleans Project Gutenberg boilerplate."""
    s = GUTENBERG_START.search(text)
    e = GUTENBERG_END.search(text)
    if s and e and s.end() < e.start():
        return text[s.end():e.start()].strip(), "gutenberg"
    return text.strip(), "raw"


def fetch_url(url: str, timeout: int = 30) -> dict[str, Any]:
    """Fetch a single URL; return {url, source, text, char_count}.

    Only http/https URLs are allowed. Private/loopback IPs are rejected.
    Response body is capped at MAX_RESPONSE_BYTES.
    """
    _check_url(url)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (AI-Assembly-Persona-Pipeline)"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw_bytes = r.read(MAX_RESPONSE_BYTES + 1)
    if len(raw_bytes) > MAX_RESPONSE_BYTES:
        raise ValueError(f"Response from {url!r} exceeds {MAX_RESPONSE_BYTES // 1024 // 1024} MB cap; skipping")
    raw = raw_bytes.decode("utf-8", errors="ignore")
    cleaned, source = _strip_gutenberg(raw)
    return {"url": url, "source": source, "text": cleaned, "char_count": len(cleaned)}


def fetch_all(sources: list[str]) -> list[dict[str, Any]]:
    """Fetch each URL; on failure record an error entry instead of raising."""
    out = []
    for url in sources:
        try:
            out.append(fetch_url(url))
        except (OSError, ValueError, urllib.error.URLError) as e:
            out.append({"url": url, "source": "error", "text": "", "char_count": 0,
                        "error": f"{type(e).__name__}: {e}"})
    return out
