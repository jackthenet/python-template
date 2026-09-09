"""The authentication service (T-004, T-005, T-006).

:class:`AuthService` implements the password login, session, password-recovery,
and passkey (WebAuthn) operations specified by ``docs/specs/authentication.md``.

- Password verification and password changes are delegated to the
  user-management feature (REQ-002, REQ-012); the service never stores or
  returns the hash.
- Login failures (unknown user, wrong password, inactive user, locked) raise
  the unified :class:`InvalidCredentialsError` (D4); every attempt performs an
  Argon2id verification (dummy when no user matches) so timing does not reveal
  whether the identifier exists (REQ-005).
- Session and reset tokens are 256-bit random and stored only as SHA-256 hashes
  (REQ-006); the raw token is returned exactly once at issuance.
- The class is traced via the shared logging feature (``@logged_class``);
  ``include_args`` stays ``False`` so passwords and tokens never appear in log
  records (REQ-022).
"""

from __future__ import annotations

import contextlib
import json
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from argon2 import PasswordHasher
from argon2.exceptions import Argon2Error

from backend.authentication.errors import (
    InvalidCredentialsError,
    InvalidResetTokenError,
    InvalidSessionError,
    PasskeyCredentialNotFoundError,
    PasskeyHijackError,
)
from backend.authentication.events import (
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
    WebAuthnCredential,
    WebAuthnCredentialRead,
)
from backend.authentication.protocols import AttemptTracker, WebAuthnProvider
from backend.authentication.repositories import (
    PasswordResetRepository,
    SessionRepository,
    WebAuthnCredentialRepository,
)
from backend.authentication.tokens import hash_token, new_token
from backend.authentication.tracker import InMemoryAttemptTracker
from backend.authentication.webauthn import PyWebAuthnProvider
from backend.logging import logged_class
from backend.usermanagement import EventPublisher, UserManager, UserRead, UserRepository

# A fixed Argon2id hash used for dummy verification (timing equalization, REQ-005).
_DUMMY_HASH = PasswordHasher().hash("dummy-password-for-timing-equalization")


@logged_class(slow_threshold_ms=250, include_args=False)
class AuthService:
    """The authentication use-case service.

    The class is traced via the shared logging feature (``@logged_class``) with
    ``include_args=False`` so passwords and tokens never appear in log records.
    """

    def __init__(
        self,
        user_manager: UserManager,
        user_repository: UserRepository,
        session_repository: SessionRepository,
        reset_repository: PasswordResetRepository,
        webauthn_repository: WebAuthnCredentialRepository,
        webauthn_provider: WebAuthnProvider | None = None,
        event_bus: EventPublisher | None = None,
        attempt_tracker: AttemptTracker | None = None,
        session_ttl: timedelta = timedelta(days=7),
        reset_token_ttl: timedelta = timedelta(minutes=15),
        max_failed_attempts: int = 5,
        lockout_duration: timedelta = timedelta(minutes=15),
        rp_id: str = "localhost",
        rp_name: str = "Python Template",
        origin: str = "http://localhost:3000",
    ) -> None:
        self._user_manager = user_manager
        self._user_repository = user_repository
        self._session_repository = session_repository
        self._reset_repository = reset_repository
        self._webauthn_repository = webauthn_repository
        self._event_bus = event_bus
        self._session_ttl = session_ttl
        self._reset_token_ttl = reset_token_ttl
        self._webauthn_provider = (
            webauthn_provider if webauthn_provider is not None else PyWebAuthnProvider(rp_id, rp_name, origin)
        )
        self._attempt_tracker = (
            attempt_tracker
            if attempt_tracker is not None
            else InMemoryAttemptTracker(max_failed_attempts, lockout_duration)
        )
        self._hasher = PasswordHasher()

    # --- private helpers (not traced by @logged_class) ---

    def _publish(self, event: object) -> None:
        if self._event_bus is not None:
            self._event_bus.publish(event)

    def _dummy_verify(self) -> None:
        """Perform an Argon2id verification against a fixed dummy hash (REQ-005)."""
        with contextlib.suppress(Argon2Error):
            self._hasher.verify(_DUMMY_HASH, "irrelevant-password")

    def _user_by_identifier(self, identifier: str):
        user = self._user_repository.get_by_username(identifier)
        if user is None:
            user = self._user_repository.get_by_email(identifier)
        return user

    def _issue_session(self, user: UserRead, method: str) -> LoginResult:
        token = new_token()
        now = datetime.now(UTC)
        session = Session(
            user_id=user.id,
            token_hash=hash_token(token),
            created_at=now,
            expires_at=now + self._session_ttl,
            revoked=False,
        )
        self._session_repository.add(session)
        session_info = SessionInfo(user_id=user.id, created_at=now, expires_at=now + self._session_ttl)
        self._publish(LoginSucceeded(user_id=user.id, method=method))
        return LoginResult(user=self._user_manager.get_user(user.id), session=session_info, token=token)

    # --- password login ---

    def login(self, request: LoginRequest) -> LoginResult:
        identifier = request.identifier

        if self._attempt_tracker.is_locked(identifier):
            self._dummy_verify()
            self._publish(LoginFailed(identifier=identifier, method="password"))
            raise InvalidCredentialsError("invalid credentials")

        user = self._user_by_identifier(identifier)

        if user is None or not user.is_active:
            self._dummy_verify()
            self._attempt_tracker.record_failure(identifier)
            self._publish(LoginFailed(identifier=identifier, method="password"))
            raise InvalidCredentialsError("invalid credentials")

        if not self._user_manager.verify_password(user.id, request.password):
            self._attempt_tracker.record_failure(identifier)
            self._publish(LoginFailed(identifier=identifier, method="password"))
            raise InvalidCredentialsError("invalid credentials")

        self._attempt_tracker.record_success(identifier)
        return self._issue_session(user, method="password")

    # --- sessions ---

    def session_info(self, token: str) -> SessionInfo:
        session = self._session_repository.get_by_token_hash(hash_token(token))
        if session is None or session.revoked or session.expires_at <= datetime.now(UTC):
            raise InvalidSessionError("invalid session")
        return SessionInfo(user_id=session.user_id, created_at=session.created_at, expires_at=session.expires_at)

    def logout(self, token: str) -> None:
        session = self._session_repository.get_by_token_hash(hash_token(token))
        if session is not None and not session.revoked and session.expires_at > datetime.now(UTC):
            self._session_repository.revoke(session.id)
            self._publish(Logout(user_id=session.user_id))

    # --- password recovery ---

    def request_password_reset(self, request: PasswordResetRequest) -> str | None:
        email = request.email.lower()
        user = self._user_repository.get_by_email(email)
        if user is None:
            self._publish(PasswordResetRequested(email=email))
            return None
        self._reset_repository.invalidate_all_for_user(user.id)
        token = new_token()
        now = datetime.now(UTC)
        reset = PasswordReset(
            user_id=user.id,
            email=email,
            token_hash=hash_token(token),
            created_at=now,
            expires_at=now + self._reset_token_ttl,
            used=False,
        )
        self._reset_repository.add(reset)
        self._publish(PasswordResetRequested(email=email))
        return token

    def complete_password_reset(self, request: PasswordResetComplete) -> None:
        reset = self._reset_repository.get_by_token_hash(hash_token(request.token))
        now = datetime.now(UTC)
        if reset is None:
            raise InvalidResetTokenError(reason="unknown")
        if reset.used:
            raise InvalidResetTokenError(reason="used")
        if reset.expires_at <= now:
            raise InvalidResetTokenError(reason="expired")
        self._reset_repository.mark_used(reset.id)
        self._user_manager.change_password(reset.user_id, request.new_password)
        self._session_repository.revoke_all_for_user(reset.user_id)
        self._publish(PasswordResetCompleted(user_id=reset.user_id))

    # --- passkey (WebAuthn) ---

    def begin_passkey_registration(self, request: PasskeyRegistrationBegin) -> dict[str, Any]:
        return self._webauthn_provider.generate_registration_options(
            request.user_id, request.username, request.display_name
        )

    def complete_passkey_registration(self, request: PasskeyRegistrationComplete) -> WebAuthnCredentialRead:
        credential = self._webauthn_provider.verify_registration_response(request.user_id, "", request.response)
        now = datetime.now(UTC)
        row = WebAuthnCredential(
            user_id=request.user_id,
            credential_id=credential.credential_id,
            public_key=credential.public_key,
            transports=json.dumps(credential.transports),
            sign_count=credential.sign_count,
            created_at=now,
        )
        self._webauthn_repository.add(row)
        self._publish(PasskeyRegistered(user_id=request.user_id, credential_id=credential.credential_id))
        return WebAuthnCredentialRead(
            credential_id=credential.credential_id,
            transports=list(credential.transports),
            created_at=now,
        )

    def begin_passkey_login(self, request: PasskeyLoginBegin) -> dict[str, Any]:
        credential = self._webauthn_repository.get_by_credential_id(request.credential_id)
        if credential is None:
            raise PasskeyCredentialNotFoundError("credential not found")
        return self._webauthn_provider.generate_authentication_options(request.credential_id)

    def complete_passkey_login(self, request: PasskeyLoginComplete) -> LoginResult:
        assertion = self._webauthn_provider.verify_authentication_response(request.credential_id, request.response)
        credential = self._webauthn_repository.get_by_credential_id(request.credential_id)
        if credential is None:
            raise PasskeyCredentialNotFoundError("credential not found")
        if assertion.sign_count < credential.sign_count:
            raise PasskeyHijackError("sign count regression")
        self._webauthn_repository.update_sign_count(request.credential_id, assertion.sign_count)
        user = self._user_manager.get_user(credential.user_id)
        return self._issue_session(user, method="passkey")

    def list_passkeys(self, user_id: UUID) -> list[WebAuthnCredentialRead]:
        rows = self._webauthn_repository.list_for_user(user_id)
        return [
            WebAuthnCredentialRead(
                credential_id=row.credential_id,
                transports=json.loads(row.transports),
                created_at=row.created_at,
            )
            for row in rows
        ]

    def delete_passkey(self, user_id: UUID, credential_id: str) -> None:
        credential = self._webauthn_repository.get_by_credential_id(credential_id)
        if credential is None or credential.user_id != user_id:
            raise PasskeyCredentialNotFoundError("credential not found")
        self._webauthn_repository.delete(credential_id)
        self._publish(PasskeyDeleted(user_id=user_id, credential_id=credential_id))
