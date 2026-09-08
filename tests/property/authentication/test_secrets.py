"""Property tests for secrets (docs/specs/authentication.md, INV-005)."""

from __future__ import annotations

from hypothesis import HealthCheck, assume, given, settings
from hypothesis import strategies as st

from authentication_test_helpers import build_memory_auth_service, create_user, valid_login
from backend.authentication import InvalidCredentialsError, LoginRequest

_MAX_EXAMPLES = 10


@settings(max_examples=_MAX_EXAMPLES, suppress_health_check=[HealthCheck.too_slow])
@given(
    password=st.text(
        min_size=8,
        max_size=32,
        alphabet=st.sampled_from("abcdefghijklmnopqrstuvwxyz0123456789"),
    ),
    success=st.booleans(),
)
def test_inv_005_no_password_in_observable_output(password: str, success: bool) -> None:
    # the password must satisfy the shared rules (8..128 chars, letter + digit)
    assume(any(c.isalpha() for c in password) and any(c.isdigit() for c in password))
    fixture = build_memory_auth_service()
    if success:
        create_user(fixture.user_manager, password=password)
    else:
        create_user(fixture.user_manager)  # password "correct-horse-1"
    try:
        result = fixture.service.login(LoginRequest(**valid_login("alice", password)))
        outputs = [result.model_dump_json()]
    except InvalidCredentialsError as exc:
        outputs = [str(exc), repr(exc)]
    for event in fixture.collector.events:
        outputs.append(event.model_dump_json())
    for out in outputs:
        assert password not in out
