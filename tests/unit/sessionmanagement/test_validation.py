"""Unit tests for list_sessions argument validation and the singleton repository rule
(docs/specs/session-management.md).

Covers AC-003, AC-013, AC-042, EDGE-008, EDGE-009, and — added by
``session-management.md`` v2 — EDGE-013, EDGE-014 (the shared-default install edge
cases, change ``settings-public-registry-setter``). The install/get/reset trio is
reached through ``SESSIONMANAGEMENT_SLOT``, which resolves the names by attribute at
call time, so the missing install operation fails inside the test body instead of at
import (house pattern).
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

import pytest
from sessionmanagement_test_helpers import make_session
from singleton_install_test_helpers import SESSIONMANAGEMENT_SLOT, non_tracing_warnings


def test_ac_003_both_or_neither_token_user_id_value_error(session_service) -> None:
    """AC-003: both token and user_id, or neither, raises ValueError."""
    # both provided
    with pytest.raises(ValueError):
        session_service.list_sessions(token="some-token", user_id=uuid4())
    # neither provided
    with pytest.raises(ValueError):
        session_service.list_sessions()


def test_ac_013_limit_below_one_value_error(session_service, session_repository, user_id) -> None:
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


def test_edge_009_limit_below_one_value_error(session_service, session_repository, user_id) -> None:
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


# --- Shared-default install edge cases (session-management.md v2 REQ-023, EDGE-013 .. EDGE-014) ---


def test_edge_013_repository_rule_after_install_and_reset() -> None:
    """EDGE-013: after an install the getter needs no repository; after a reset the AC-042 ValueError still stands."""
    from backend.sessionmanagement import get_session_service, reset_session_service

    reset_session_service()
    try:
        installed = SESSIONMANAGEMENT_SLOT.new()
        SESSIONMANAGEMENT_SLOT.install(installed)
        # after set_session_service(a): a is returned with no repository argument
        assert get_session_service() is installed, "the installed service is not returned without a repository"
        reset_session_service()
        # after reset_session_service(): AC-042 is unchanged
        with pytest.raises(ValueError):
            get_session_service()
    finally:
        reset_session_service()


def test_edge_014_install_over_nonempty_default(log_records: list[Any]) -> None:
    """EDGE-014: replacing a non-empty shared default warns once, raises nothing, and leaves the replaced service working."""
    from backend.sessionmanagement import get_session_service, reset_session_service

    reset_session_service()
    try:
        replaced = SESSIONMANAGEMENT_SLOT.new()
        replacement = SESSIONMANAGEMENT_SLOT.new()
        SESSIONMANAGEMENT_SLOT.install(replaced)  # the shared default is now non-empty
        SESSIONMANAGEMENT_SLOT.install(replacement)  # EDGE-014: replace it — no exception
        assert get_session_service() is replacement, "the non-empty shared default was not replaced"
        warnings = non_tracing_warnings(log_records)
        assert len(warnings) == 1, f"expected exactly one replace WARNING, got {warnings!r}"
        assert "session" in str(warnings[0]).lower(), f"the WARNING does not name the shared default: {warnings[0]!r}"
        # No lifecycle effect: the install neither mutates nor shuts down what it replaced,
        # so the replaced service keeps working for every caller that holds it (change
        # REQ-003) — and it never touched the replacement either.
        assert replaced.list_sessions(user_id=uuid4()) == []
        assert replacement.list_sessions(user_id=uuid4()) == []
    finally:
        reset_session_service()
