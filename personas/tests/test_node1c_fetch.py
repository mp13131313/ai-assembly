"""node1c_fetch — Wikisource body extraction (§37 A3) and SSRF checks (§37 A13).

Offline: DNS lookups are mocked, nothing is fetched.
"""
from __future__ import annotations

import socket
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import flows.shared.node1c_fetch as nf  # noqa: E402

# Shape of a Wikisource page: the parser-output wrapper holds a header
# template (nested divs + a <style> block) before the actual text.
WIKISOURCE_PAGE = """<html><body>
<div id="mw-content-text" class="mw-body-content mw-content-ltr">
<div class="mw-content-ltr mw-parser-output" lang="en">
<style data-mw-deduplicate="x">.mw-parser-output .ws-header{font-size:83%}</style>
<div class="ws-header"><div class="title">Sketch of the Analytical Engine</div></div>
<p>Those labours which belong to the various branches of the mathematical sciences &amp; which</p>
<div class="footnote"><p>Note A.</p></div>
<p>The Analytical Engine has no pretensions whatever to originate anything.</p>
</div></div>
<div class="printfooter">Retrieved from Wikisource</div>
</body></html>"""


@pytest.fixture
def no_bs4(monkeypatch):
    monkeypatch.setattr(nf, "_HAS_BS4", False)  # the personas venv has no bs4


def test_wikisource_keeps_the_whole_body_not_just_the_header(no_bs4):
    text = nf._html_to_text(WIKISOURCE_PAGE, "https://en.wikisource.org/wiki/Sketch")
    assert "originate anything" in text          # past the nested divs
    assert "mathematical sciences & which" in text  # entities decoded
    assert "font-size" not in text                # <style> body dropped
    assert "Retrieved from Wikisource" not in text  # outside the wrapper


def test_mediawiki_content_absent_returns_none():
    assert nf._mediawiki_content("<html><body><p>plain</p></body></html>") is None


def _resolve_to(monkeypatch, ip: str) -> None:
    family = socket.AF_INET6 if ":" in ip else socket.AF_INET
    monkeypatch.setattr(nf.socket, "getaddrinfo",
                        lambda host, port: [(family, 0, 0, "", (ip, 0))])


@pytest.mark.parametrize("ip", ["100.64.1.1", "0.0.0.1", "fe80::1", "::ffff:127.0.0.1", "169.254.169.254"])
def test_check_url_blocks_private_ranges(monkeypatch, ip):
    _resolve_to(monkeypatch, ip)
    with pytest.raises(ValueError, match="private/loopback"):
        nf._check_url("https://example.org/text")


def test_check_url_allows_public_address(monkeypatch):
    _resolve_to(monkeypatch, "93.184.216.34")
    nf._check_url("https://example.org/text")  # no exception


def test_redirect_to_private_address_is_refused(monkeypatch):
    _resolve_to(monkeypatch, "169.254.169.254")
    handler = nf._CheckedRedirectHandler()
    with pytest.raises(ValueError, match="private/loopback"):
        handler.redirect_request(None, None, 302, "Found", {}, "http://metadata.internal/latest")
