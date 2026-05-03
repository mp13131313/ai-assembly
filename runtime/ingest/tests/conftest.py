"""Pytest fixtures for ingest tests.

Defends against env-clobber: when other test modules in the runtime suite
(notably tests/test_orchestrator.py) import their target script, that
script may call `load_dotenv(override=True)`, which overwrites the test
passwords pytest set at collection time. Every ingest test re-applies
its expected env via this autouse fixture.
"""

from __future__ import annotations

import os

import pytest


@pytest.fixture(autouse=True)
def _force_test_env(monkeypatch):
    """Pin the test passwords + clear auth rate-limit state per test.

    Auth.py reads UPLOAD_APP_PASSWORD / ADMIN_APP_PASSWORD on every
    request, so pinning here is sufficient — no module reload needed.
    """
    monkeypatch.setenv("UPLOAD_APP_PASSWORD", "testpw")
    monkeypatch.setenv("ADMIN_APP_PASSWORD", "admin_pw")
    # ANTHROPIC + ASSEMBLYAI keys are only needed at lifespan
    # check_required_env(); test fakes are fine.
    monkeypatch.setenv("ANTHROPIC_API_KEY", os.environ.get("ANTHROPIC_API_KEY", "test"))
    monkeypatch.setenv("ASSEMBLYAI_API_KEY", os.environ.get("ASSEMBLYAI_API_KEY", "test"))
    # Reset the in-memory auth rate-limit so accumulated failures across
    # the suite don't trigger 429 on later tests.
    from ingest import auth as auth_mod
    auth_mod._failures.clear()
    yield
