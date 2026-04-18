"""HTTP Basic Auth with a single shared password and IP-based rate limiting.

Username is ignored (convention: "producer"). Password is the single
`UPLOAD_APP_PASSWORD` env var. Comparison is fixed-time.

Rate limiting: after 10 failed attempts from the same IP within 60 seconds
the request is rejected with 429. In-memory; resets on process restart.
For a persistent / distributed limit, move to Redis or similar.
"""

from __future__ import annotations

import os
import secrets
import threading
import time
from collections import defaultdict

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

_security = HTTPBasic(realm="AI Assembly Ingest")

# --- Rate limiting -----------------------------------------------------------

_WINDOW_SECONDS = 60
_MAX_FAILURES = 10

_lock = threading.Lock()
_failures: dict[str, list[float]] = defaultdict(list)  # ip -> [timestamps]


def _client_ip(request: Request) -> str:
    """Real IP for rate-limiting.

    SECURITY: assumes the app runs behind Caddy (or equivalent reverse
    proxy) that sets X-Real-IP to the actual client IP. If the app is
    ever exposed directly (without a proxy in front), these headers are
    attacker-controlled and rate-limiting becomes trivially bypassable.
    See runtime/ingest/deploy/Caddyfile:27-28 for the proxy config.
    """
    return (
        request.headers.get("X-Real-IP")
        or request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
        or (request.client.host if request.client else "unknown")
    )


def _check_and_record(ip: str, *, failed: bool) -> None:
    """Check rate limit before auth; record a failure if auth failed.

    Raises 429 if the IP has exceeded _MAX_FAILURES in the last window.
    Call with failed=False before checking credentials (to gate early),
    and call again with failed=True only when credentials are wrong.
    """
    now = time.monotonic()
    with _lock:
        # Prune IPs with no recent failures. Cheap and bounds memory growth
        # under sustained probing.
        stale = [k for k, v in _failures.items()
                 if not v or now - max(v) > _WINDOW_SECONDS]
        for k in stale:
            del _failures[k]

        recent = [t for t in _failures[ip] if now - t < _WINDOW_SECONDS]
        if len(recent) >= _MAX_FAILURES:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="too many failed attempts — try again later",
                headers={"Retry-After": str(_WINDOW_SECONDS)},
            )
        if failed:
            recent.append(now)
        _failures[ip] = recent


# --- Auth dependency ---------------------------------------------------------


def require_auth(
    request: Request,
    creds: HTTPBasicCredentials = Depends(_security),
) -> str:
    """FastAPI dependency: 401 unless the Basic-Auth password matches env."""
    ip = _client_ip(request)
    # Gate: reject immediately if this IP is already over the limit.
    _check_and_record(ip, failed=False)

    expected = os.environ.get("UPLOAD_APP_PASSWORD", "")
    # compare_digest requires equal-length inputs; fall back to a known-wrong
    # constant when the env var is missing so we still fail closed.
    ok = bool(expected) and secrets.compare_digest(creds.password, expected)
    if not ok:
        _check_and_record(ip, failed=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid credentials",
            headers={"WWW-Authenticate": 'Basic realm="AI Assembly Ingest"'},
        )
    return creds.username or "producer"
