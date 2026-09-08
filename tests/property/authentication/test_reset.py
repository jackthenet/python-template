"""Property tests for password reset (docs/specs/authentication.md, INV-003)."""

from __future__ import annotations

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from authentication_test_helpers import build_memory_auth_service, create_user
from backend.authentication import InvalidResetTokenError, PasswordResetComplete, PasswordResetRequest

_MAX_EXAMPLES = 10


@settings(max_examples=_MAX_EXAMPLES, suppress_health_check=[HealthCheck.too_slow])
@given(attempts=st.integers(min_value=1, max_value=5))
def test_inv_003_reset_token_at_most_once(attempts: int) -> None:
    fixture = build_memory_auth_service()
    create_user(fixture.user_manager)
    token = fixture.service.request_password_reset(PasswordResetRequest(email="alice@example.com"))
    assert token is not None
    # the first completion succeeds
    fixture.service.complete_password_reset(PasswordResetComplete(token=token, new_password="new-pass-1"))
    # every further attempt fails (double-spend is impossible)
    for _ in range(attempts):
        with pytest.raises(InvalidResetTokenError) as exc:
            fixture.service.complete_password_reset(
                PasswordResetComplete(token=token, new_password="new-pass-1")
            )
        assert exc.value.reason == "used"
