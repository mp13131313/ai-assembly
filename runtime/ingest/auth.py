"""HTTP Basic Auth with role-based credentials and IP-based rate limiting.

Two credentials, identified by which password matched:

  * UPLOAD_APP_PASSWORD → role "producer". HoBB A/V producer credentials,
    shared with venue uploaders. Used during conference. Rotate after.
  * ADMIN_APP_PASSWORD  → role "admin". Operator credentials. Optional —
    if not set in env, admin role is unavailable (back-compat with the
    pre-2026-05-03 single-password setup).

Username is ignored. Password matching is constant-time.

Rate limiting: after 10 failed attempts from the same IP within 60 seconds
the request is rejected with 429. In-memory; resets on process restart.
For a persistent / distributed limit, move to Redis or similar.

The `require_auth` dependency returns the role string ("producer" or
"admin"). Routes that need admin only should use `require_admin`.
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


# --- Auth dependencies -------------------------------------------------------


def _match_role(password: str) -> str | None:
    """Return the role name whose env credential matches, or None.

    Each comparison is constant-time. Both env vars are read on every
    call so that operator rotation (edit `.env`, `systemctl restart
    ingest`) takes effect without a code change. Empty env vars never
    match — `secrets.compare_digest` returns False against the empty
    candidate, plus the explicit `bool(expected)` guard.
    """
    producer_pw = os.environ.get("UPLOAD_APP_PASSWORD", "")
    admin_pw = os.environ.get("ADMIN_APP_PASSWORD", "")
    # Check admin first — if both happen to be set to the same value
    # (operator misconfiguration), the role escalates to admin, which
    # is the safer-fail direction (operator sees more, not less).
    if admin_pw and secrets.compare_digest(password, admin_pw):
        return "admin"
    if producer_pw and secrets.compare_digest(password, producer_pw):
        return "producer"
    return None


def require_auth(
    request: Request,
    creds: HTTPBasicCredentials = Depends(_security),
) -> str:
    """FastAPI dependency: 401 unless creds match producer or admin password.

    Returns the role string ("producer" | "admin"). Use directly in route
    signatures to know which role the request came in as.
    """
    ip = _client_ip(request)
    # Gate: reject immediately if this IP is already over the limit.
    _check_and_record(ip, failed=False)

    role = _match_role(creds.password)
    if role is None:
        _check_and_record(ip, failed=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid credentials",
            headers={"WWW-Authenticate": 'Basic realm="AI Assembly Ingest"'},
        )
    return role


def require_admin(
    request: Request,
    creds: HTTPBasicCredentials = Depends(_security),
) -> str:
    """FastAPI dependency: 401/403 unless creds match the admin password.

    401 on bad creds (so a producer who just typed wrong gets the auth
    prompt back); 403 when creds are valid producer-tier but caller
    needs admin. The 403 response is rare in practice — producers don't
    bookmark admin URLs — so this distinction is mostly for honest API
    behavior, not UX.
    """
    ip = _client_ip(request)
    _check_and_record(ip, failed=False)

    role = _match_role(creds.password)
    if role is None:
        _check_and_record(ip, failed=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid credentials",
            headers={"WWW-Authenticate": 'Basic realm="AI Assembly Ingest"'},
        )
    if role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="admin role required",
        )
    return role
