"""Acceptance tests for session-store reuse (docs/specs/session-management.md, AC-033)."""

from __future__ import annotations

from pathlib import Path

from authentication_test_helpers import build_auth_service, create_user, valid_login
from sessionmanagement_test_helpers import build_session_service

from backend.authentication import LoginRequest


def test_ac_033_same_sessions_table_as_authentication(tmp_path: Path) -> None:
    """AC-033: the service acts on the same sessions table as authentication (no second store).

    A session issued by authentication's real login path (REQ-017) must appear
    in the sessionmanagement listing resolved from the same token.
    """
    fixture = build_auth_service(tmp_path)
    create_user(fixture.user_manager)
    result = fixture.service.login(LoginRequest(**valid_login("alice")))
    service = build_session_service(fixture.session_repository, event_bus=None)
    entries = service.list_sessions(token=result.token)
    assert len(entries) == 1
    assert entries[0].created_at == result.session.created_at
    assert entries[0].expires_at == result.session.expires_at
    assert entries[0].is_current is True
