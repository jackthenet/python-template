"""Contract tests for the public API (docs/specs/session-management.md, NFR-003)."""

from __future__ import annotations

import importlib
import inspect

_EXPECTED_API = [
    # service
    "SessionService",
    # representation
    "SessionEntry",
    # events
    "SessionRevoked",
    "AllSessionsRevoked",
    "ExpiredSessionsDeleted",
    "SessionsListed",
    # module functions
    "register_settings",
    "get_session_service",
    "reset_session_service",
]

_ORIGINAL_ABC_METHODS = [
    "add",
    "get_by_token_hash",
    "revoke",
    "revoke_all_for_user",
    "delete_expired",
]

_NEW_ABC_METHODS = [
    "get",
    "list_for_user",
    "revoke_user_sessions",
]


def test_nfr_003_public_api_contract() -> None:
    """NFR-003: the public API of backend.sessionmanagement is a
    backward-compatibility contract; the SessionRepository ABC extension is
    additive and backward-compatible per authentication NFR-003."""
    # the public API of backend.sessionmanagement
    module = importlib.import_module("backend.sessionmanagement")
    for name in _EXPECTED_API:
        assert hasattr(module, name), f"backend.sessionmanagement.{name} is missing"
    # the SessionRepository ABC keeps its original methods unchanged
    from backend.authentication import SessionRepository

    for name in _ORIGINAL_ABC_METHODS:
        assert hasattr(SessionRepository, name), f"SessionRepository.{name} is missing"
    # the ABC is extended additively with the new methods
    for name in _NEW_ABC_METHODS:
        assert hasattr(SessionRepository, name), f"SessionRepository.{name} is missing"
    # delete_expired's signature is extended with an optional limit
    # (None = all, the previous behavior)
    limit = inspect.signature(SessionRepository.delete_expired).parameters.get("limit")
    assert limit is not None, "SessionRepository.delete_expired has no optional limit parameter"
    assert limit.default is None, "SessionRepository.delete_expired's limit must default to None (all)"
