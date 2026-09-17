"""Acceptance tests for the module singleton (docs/specs/session-management.md, AC-041, AC-043).

The singleton is module-level global state, so an autouse fixture resets it
before and after each test (test isolation, AC-043) to guarantee isolation.
The feature package (``backend.sessionmanagement``) is imported lazily inside
the fixture and test bodies so the RED state (module missing) surfaces as a
per-test error rather than a file-level collection error (house pattern).
"""

from __future__ import annotations

from pathlib import Path

import pytest
from sessionmanagement_test_helpers import db_url

from backend.authentication.repository import SqliteSessionRepository


@pytest.fixture(autouse=True)
def _isolate_singleton():
    """Reset the module singleton before and after each test (test isolation, AC-043)."""
    from backend.sessionmanagement import reset_session_service

    reset_session_service()
    yield
    reset_session_service()


def test_ac_041_singleton_created_once(tmp_path: Path) -> None:
    """AC-041: first call creates the singleton; subsequent calls return the same instance."""
    from backend.sessionmanagement import get_session_service

    # Given: no singleton yet (the fixture reset it)
    repository = SqliteSessionRepository(db_url(tmp_path))
    # When: the first call creates the singleton
    first = get_session_service(repository)
    # Then: subsequent calls (with or without arguments) return the same instance
    assert get_session_service(repository) is first
    assert get_session_service() is first


def test_ac_043_reset_session_service(tmp_path: Path) -> None:
    """AC-043: reset clears the singleton; a subsequent call creates a new instance."""
    from backend.sessionmanagement import get_session_service, reset_session_service

    # Given: an existing singleton
    repository = SqliteSessionRepository(db_url(tmp_path))
    first = get_session_service(repository)
    # When: the singleton is reset
    reset_session_service()
    # Then: a subsequent call creates a new instance
    second = get_session_service(repository)
    assert second is not first
