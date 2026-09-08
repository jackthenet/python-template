"""Property tests for tokens (docs/specs/authentication.md, INV-001)."""

from __future__ import annotations

import hashlib

from authentication_test_helpers import build_memory_auth_service, create_user, valid_login
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from backend.authentication import LoginRequest, PasswordResetRequest

_MAX_EXAMPLES = 10


@settings(max_examples=_MAX_EXAMPLES, suppress_health_check=[HealthCheck.too_slow])
@given(n=st.integers(min_value=1, max_value=4))
def test_inv_001_token_hash_uniqueness(n: int) -> None:
    fixture = build_memory_auth_service()
    create_user(fixture.user_manager)
    hashes: list[str] = []
    for _ in range(n):
        result = fixture.service.login(LoginRequest(**valid_login("alice")))
        hashes.append(hashlib.sha256(result.token.encode("utf-8")).hexdigest())
    for _ in range(n):
        token = fixture.service.request_password_reset(PasswordResetRequest(email="alice@example.com"))
        assert token is not None
        hashes.append(hashlib.sha256(token.encode("utf-8")).hexdigest())
    assert len(set(hashes)) == len(hashes)
