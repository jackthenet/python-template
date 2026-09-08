"""Public API of the authentication feature (module: backend.authentication).

The public API is the NFR-003 backward-compatibility contract: the
:class:`AuthService` (T-004), the request schemas, the representations, the
error hierarchy, the repository ABCs and their ``Sqlite*`` implementations
(T-002), the :class:`WebAuthnProvider` ABC and :class:`PyWebAuthnProvider`
(T-006), :class:`InMemoryAttemptTracker` (T-003), the table models, and the
lifecycle events.
"""

from __future__ import annotations

from backend.authentication.errors import (
    AuthenticationError,
    InvalidCredentialsError,
    InvalidPasskeyResponseError,
    InvalidResetTokenError,
    InvalidSessionError,
    PasskeyCredentialNotFoundError,
    PasskeyHijackError,
)
from backend.authentication.events import (
    AuthEvent,
    LoginFailed,
    LoginSucceeded,
    Logout,
    PasskeyDeleted,
    PasskeyRegistered,
    PasswordResetCompleted,
    PasswordResetRequested,
)
from backend.authentication.models import (
    LoginRequest,
    LoginResult,
    PasskeyLoginBegin,
    PasskeyLoginComplete,
    PasskeyRegistrationBegin,
    PasskeyRegistrationComplete,
    PasswordReset,
    PasswordResetComplete,
    PasswordResetRequest,
    Session,
    SessionInfo,
    VerifiedAssertion,
    VerifiedCredential,
    WebAuthnCredential,
    WebAuthnCredentialRead,
)
from backend.authentication.protocols import AttemptTracker, WebAuthnProvider
from backend.authentication.repositories import (
    PasswordResetRepository,
    SessionRepository,
    WebAuthnCredentialRepository,
)
from backend.authentication.repository import (
    SqlitePasswordResetRepository,
    SqliteSessionRepository,
    SqliteWebAuthnCredentialRepository,
)
from backend.authentication.service import AuthService
from backend.authentication.tokens import hash_token, new_token
from backend.authentication.tracker import InMemoryAttemptTracker
from backend.authentication.webauthn import PyWebAuthnProvider

__all__ = [
    "AttemptTracker",
    "AuthEvent",
    "AuthService",
    "AuthenticationError",
    "InMemoryAttemptTracker",
    "InvalidCredentialsError",
    "InvalidPasskeyResponseError",
    "InvalidResetTokenError",
    "InvalidSessionError",
    "LoginFailed",
    "LoginRequest",
    "LoginResult",
    "LoginSucceeded",
    "Logout",
    "PasskeyCredentialNotFoundError",
    "PasskeyDeleted",
    "PasskeyHijackError",
    "PasskeyLoginBegin",
    "PasskeyLoginComplete",
    "PasskeyRegistered",
    "PasskeyRegistrationBegin",
    "PasskeyRegistrationComplete",
    "PasswordReset",
    "PasswordResetComplete",
    "PasswordResetCompleted",
    "PasswordResetRepository",
    "PasswordResetRequest",
    "PasswordResetRequested",
    "PyWebAuthnProvider",
    "Session",
    "SessionInfo",
    "SessionRepository",
    "SqlitePasswordResetRepository",
    "SqliteSessionRepository",
    "SqliteWebAuthnCredentialRepository",
    "VerifiedAssertion",
    "VerifiedCredential",
    "WebAuthnCredential",
    "WebAuthnCredentialRead",
    "WebAuthnCredentialRepository",
    "WebAuthnProvider",
    "hash_token",
    "new_token",
]
