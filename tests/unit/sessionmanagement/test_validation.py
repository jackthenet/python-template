"""Unit tests for list_sessions argument validation (docs/specs/session-management.md).

Covers AC-003, AC-013, AC-042, EDGE-008, EDGE-009.
"""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from sessionmanagement_test_helpers import make_session


def test_ac_003_both_or_neither_token_user_id_value_error(session_service) -> None:
    """AC-003: both token and user_id, or neither, raises ValueError."""
    # both provided
    with pytest.raises(ValueError):
        session_service.list_sessions(token="some-token", user_id=uuid4())
    # neither provided
    with pytest.raises(ValueError):
        session_service.list_sessions()


def test_ac_013_limit_below_one_value_error(
    session_service, session_repository, user_id
) -> None:
    """AC-013: limit < 1 raises ValueError (with a valid token)."""
    _, token = make_session(session_repository, user_id, created_at=datetime.now(UTC))
    with pytest.raises(ValueError):
        session_service.list_sessions(token=token, limit=0)
    with pytest.raises(ValueError):
        session_service.list_sessions(token=token, limit=-1)


def test_edge_008_both_or_neither_value_error(session_service) -> None:
    """EDGE-008: list_sessions with both (or neither) token and user_id raises ValueError."""
    with pytest.raises(ValueError):
        session_service.list_sessions(token="t", user_id=uuid4())
    with pytest.raises(ValueError):
        session_service.list_sessions()


def test_edge_009_limit_below_one_value_error(
    session_service, session_repository, user_id
) -> None:
    """EDGE-009: list_sessions with limit < 1 raises ValueError."""
    _, token = make_session(session_repository, user_id, created_at=datetime.now(UTC))
    for limit in (0, -1, -5):
        with pytest.raises(ValueError):
            session_service.list_sessions(token=token, limit=limit)


def test_ac_042_singleton_first_call_without_repository_value_error() -> None:
    """AC-042: first call without a repository raises ValueError."""
    from backend.sessionmanagement import get_session_service, reset_session_service

    # Given: no singleton yet
    reset_session_service()
    try:
        # When/Then: the first call without a repository raises ValueError
        with pytest.raises(ValueError):
            get_session_service()
    finally:
        # cleanup: isolate the module singleton
        reset_session_service()
