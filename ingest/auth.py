"""HTTP Basic Auth with a single shared password.

Username is ignored (convention: "producer"). Password is the single
`UPLOAD_APP_PASSWORD` env var. Comparison is fixed-time.
"""

from __future__ import annotations

import os
import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

_security = HTTPBasic(realm="AI Assembly Ingest")


def require_auth(creds: HTTPBasicCredentials = Depends(_security)) -> str:
    """FastAPI dependency: 401 unless the Basic-Auth password matches env."""
    expected = os.environ.get("UPLOAD_APP_PASSWORD", "")
    # compare_digest requires equal-length inputs; fall back to a known-wrong
    # constant when the env var is missing so we still fail closed.
    ok = bool(expected) and secrets.compare_digest(creds.password, expected)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid credentials",
            headers={"WWW-Authenticate": 'Basic realm="AI Assembly Ingest"'},
        )
    return creds.username or "producer"
