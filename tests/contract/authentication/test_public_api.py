"""Contract tests for the public API (docs/specs/authentication.md, NFR-003)."""

from __future__ import annotations

import importlib

_EXPECTED_API = [
    # service
    "AuthService",
    # request models
    "LoginRequest",
    "PasswordResetRequest",
    "PasswordResetComplete",
    "PasskeyRegistrationBegin",
    "PasskeyRegistrationComplete",
    "PasskeyLoginBegin",
    "PasskeyLoginComplete",
    # representations
    "SessionInfo",
    "LoginResult",
    "WebAuthnCredentialRead",
    "VerifiedCredential",
    "VerifiedAssertion",
    # error hierarchy
    "AuthenticationError",
    "InvalidCredentialsError",
    "InvalidSessionError",
    "InvalidResetTokenError",
    "PasskeyCredentialNotFoundError",
    "InvalidPasskeyResponseError",
    "PasskeyHijackError",
    # repository ABCs + implementations
    "SessionRepository",
    "PasswordResetRepository",
    "WebAuthnCredentialRepository",
    "SqliteSessionRepository",
    "SqlitePasswordResetRepository",
    "SqliteWebAuthnCredentialRepository",
    # provider ABCs + implementation
    "WebAuthnProvider",
    "PyWebAuthnProvider",
    # tracker
    "AttemptTracker",
    "InMemoryAttemptTracker",
    # table models
    "Session",
    "PasswordReset",
    "WebAuthnCredential",
    # events
    "AuthEvent",
    "LoginSucceeded",
    "LoginFailed",
    "Logout",
    "PasswordResetRequested",
    "PasswordResetCompleted",
    "PasskeyRegistered",
    "PasskeyDeleted",
]


def test_nfr_003_public_api_stable() -> None:
    module = importlib.import_module("backend.authentication")
    for name in _EXPECTED_API:
        assert hasattr(module, name), f"backend.authentication.{name} is missing"
