"""Property tests for sessions (docs/specs/authentication.md, INV-002)."""

from __future__ import annotations

import hashlib
import time
from datetime import UTC, datetime, timedelta

import pytest
from authentication_test_helpers import build_memory_auth_service, create_user, valid_login
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from backend.authentication import InvalidSessionError, LoginRequest

_MAX_EXAMPLES = 10


@settings(max_examples=_MAX_EXAMPLES, deadline=None, suppress_health_check=[HealthCheck.too_slow])
@given(phase=st.sampled_from(["unexpired", "expired", "revoked"]), ttl_ms=st.integers(min_value=100, max_value=300))
def test_inv_002_session_validity_iff_unexpired_unrevoked(phase: str, ttl_ms: int) -> None:
    fixture = build_memory_auth_service(session_ttl=timedelta(milliseconds=ttl_ms))
    create_user(fixture.user_manager)
    result = fixture.service.login(LoginRequest(**valid_login("alice")))
    digest = hashlib.sha256(result.token.encode("utf-8")).hexdigest()

    if phase == "expired":
        time.sleep((ttl_ms + 50) / 1000.0)
    elif phase == "revoked":
        fixture.service.logout(result.token)

    session = fixture.session_repository.get_by_token_hash(digest)
    assert session is not None
    expected_valid = (not session.revoked) and session.expires_at > datetime.now(UTC)
    if expected_valid:
        info = fixture.service.session_info(result.token)
        assert info.user_id == result.session.user_id
    else:
        with pytest.raises(InvalidSessionError):
            fixture.service.session_info(result.token)
