# Spec: Authentication (Backend)

## Changelog
- v1 (2026-09-07): Initial specification.

## 1. Overview & Objectives
- **Feature Name:** Authentication (Backend)
- **Target Component:** `src/backend/authentication/`
- **Goal:** Provide a backend service for authenticating users — username/email + password login with revocable opaque session tokens, Passkey/WebAuthn registration and login (preferred modern method, with password retained as fallback), and password recovery via secure single-use reset tokens — integrated with the existing user-management feature rather than duplicating user storage.
- **Scope:** In-process Python service (no HTTP layer). Login with username or email + password; Argon2id password verification via the user-management feature; opaque DB-backed session tokens (256-bit, SHA-256 hashed at rest, server-side revocation, configurable TTL); password recovery (always-succeeding reset request, single-use tokens with configurable 15-minute default TTL, supersede-on-new-request, session revocation on completed reset); Passkey/WebAuthn registration + login via `py-webauthn` behind a provider interface; brute-force throttling via an in-memory per-identifier attempt tracker with lockout window; unified invalid-credentials error (no user enumeration); typed lifecycle events published to an injected event publisher; structured domain errors; observability via the shared logging feature.
- **Feature Brief (from adversarial interrogation):**
  - **Goals:** secure simple auth (password + passkey); revocable sessions; safe recovery flow; anti-enumeration and anti-brute-force posture; full integration with `backend.usermanagement` (user lookup, password verification, password changes); testable via constructor injection.
  - **Constraints:** backend only (no HTTP layer, no frontend); reuse `UserManager`/`UserRepository` — no duplicate user store or hashing logic; follow the existing architecture (service + repository ABCs + SQLModel/SQLite, constructor DI, `@logged_class`, structural `EventPublisher` protocol, two-tier validation); the only new dependency is `py-webauthn` (no existing dependency covers WebAuthn — ADR-recorded); tokens are 256-bit URL-safe random and SHA-256 hashed at rest; password rules are the shared user-management rules (8–128 chars, letter + digit); session TTL default 7 days, reset token TTL default 15 minutes, both configurable; lockout default 5 failures → 15-minute window, in-memory and injectable.
  - **Out of scope:** frontend; HTTP/REST/GraphQL API layer; email sending/delivery (reset delivery is handled by a separate email feature — the project has no email service); MFA/TOTP/backup codes; user registration (user-management owns user creation); persistent audit log; database migration/upgrade framework (bootstrap via `create_all` only); multi-tenancy; JWT sessions (rejected in favor of opaque DB-backed tokens — OWASP-recommended for session management, instant revocation, no new dependency); DB-backed attempt logging (in-memory tracker chosen).
  - **Edge cases:** unknown user / wrong password / inactive user all map to one error; locked identifiers reject even correct passwords until the window elapses; reset tokens expire, are single-use, and are superseded by newer requests; passkey sign-count regression is a hijack signal; logout is idempotent; raw tokens are returned exactly once.
- **Out of Scope:** Frontend (implemented in a separate workflow), HTTP/REST/GraphQL API layer, email verification/sending, MFA, user registration, JWT-based sessions, persistent audit log, database migration/upgrade framework (bootstrap via `create_all` only), and multi-tenancy.

## 2. Architecture & Design Decisions
- **Design Pattern:** Service + repository + provider. `AuthService` (use cases, domain rules) depends on: the user-management `UserManager` (password verification, password changes) and `UserRepository` (user lookup by username/email); its own `SessionRepository`, `PasswordResetRepository`, and `WebAuthnCredentialRepository` ABCs (SQLModel/SQLite implementations); an `AttemptTracker` (in-memory default) for brute-force throttling; and a `WebAuthnProvider` (py-webauthn-backed default) for WebAuthn option generation and response verification. The service publishes typed lifecycle events to an injected `EventPublisher` (structural protocol; the real event bus is injected at wiring time).
- **Dependencies:** `pydantic>=2.13.1`, `sqlmodel>=0.0.42` (pulls in `sqlalchemy`), `email-validator>=2.3.0`, `py-webauthn>=2.0.0` (new — WebAuthn server library; no existing dependency covers WebAuthn; ADR-recorded); uses `backend.usermanagement` (public API only) and the shared logging feature `backend.logging` (`@logged_class`). No web framework. No import of `backend.eventbus` (event integration is a structural protocol, consistent with user-management).
- **Constraints:** The service API MUST NOT expose `password_hash` or raw tokens after the initial return. Session/reset tokens MUST be 256-bit random and stored only as SHA-256 hashes. Passwords and tokens MUST NOT appear in log records or events. The service code MUST reference only repository/provider ABCs (storage and WebAuthn backends must be swappable). The SQLite stores are the default concrete repositories, sharing the same SQLite database as user-management.
- **Design Decisions (WHAT; WHY goes to ADRs in Phase 2):**
  - D1: Repository pattern — `SessionRepository`, `PasswordResetRepository`, `WebAuthnCredentialRepository` ABCs + `Sqlite*` implementations (SQLModel/SQLite); constructor injection into `AuthService`.
  - D2: Opaque DB-backed session tokens — 256-bit `secrets.token_urlsafe(32)` tokens, SHA-256 hashed at rest, server-side revocation; JWT rejected (no instant revocation, larger verification surface, new dependency for a statelessness benefit this project does not need).
  - D3: Password verification reuses user-management — `UserManager.verify_password` for found users; a dummy Argon2id verification for unknown users (timing equalization). Password changes on reset completion go through `UserManager.change_password` (shared password rules, re-hashing, `UserPasswordChanged` event).
  - D4: Unified invalid-credentials error — unknown user, wrong password, and inactive user all raise `InvalidCredentialsError`; locked identifiers also raise `InvalidCredentialsError` (no lock-state signal).
  - D5: In-memory brute-force throttling — `InMemoryAttemptTracker` (per-identifier failure count, lockout window, success clears); injectable; resets on process restart (documented, acceptable for simple auth).
  - D6: Password recovery — `request_password_reset` always succeeds (no enumeration); a token is created only for registered emails; tokens are single-use, expire after the reset TTL, and a new request for the same email invalidates prior tokens; completed reset changes the password and revokes all sessions for the user.
  - D7: Passkey/WebAuthn — full registration + login via a `WebAuthnProvider` ABC; the default `PyWebAuthnProvider` wraps `py-webauthn` (`generate_registration_options`, `verify_registration_response`, `generate_authentication_options`, `verify_authentication_response`); RP settings (`rp_id`, `rp_name`, `origin`) are constructor parameters with sensible defaults; credentials stored in a `webauthn_credentials` table; sign-count regression is rejected as hijack.
  - D8: Password and passkey coexist — a user may log in with either method; neither method disables the other.
  - D9: Field-format validation is schema-level (Pydantic models → `pydantic.ValidationError`); domain failures are service-level (exception hierarchy rooted at `AuthenticationError`).
  - D10: Table bootstrap via `SQLModel.metadata.create_all` at each repository init (no migration framework; the shared metadata also covers the user-management tables).
  - D11: `SessionInfo`/`LoginResult`/`WebAuthnCredentialRead` are the only session/passkey representations returned by the service (no hash, no raw table object).
  - D12: Typed lifecycle events are published to the injected `EventPublisher` on successful operations and on login failure; a `None` publisher means no events; no event is published on other failures.
  - D13: Events carry non-sensitive data only (no password, no raw token, no hash).

## 3. Data Structures & API Schemas

```python
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import UTC, datetime, timedelta
from typing import Any, Sequence
from uuid import UUID, uuid4

from pydantic import BaseModel, EmailStr, Field
from sqlmodel import SQLModel, Field as SField

# --- Table models (persistence; same SQLite DB as user-management) ---

class Session(SQLModel, table=True):
    __tablename__ = "sessions"
    id: UUID = SField(default_factory=uuid4, primary_key=True)
    user_id: UUID = SField(index=True)
    token_hash: str = SField(unique=True, index=True)  # SHA-256 hex of the raw token
    created_at: datetime  # UTC
    expires_at: datetime  # UTC
    revoked: bool = False

class PasswordReset(SQLModel, table=True):
    __tablename__ = "password_resets"
    id: UUID = SField(default_factory=uuid4, primary_key=True)
    user_id: UUID = SField(index=True)
    email: str = SField(index=True)  # stored lowercased
    token_hash: str = SField(unique=True, index=True)  # SHA-256 hex of the raw token
    created_at: datetime  # UTC
    expires_at: datetime  # UTC
    used: bool = False

class WebAuthnCredential(SQLModel, table=True):
    __tablename__ = "webauthn_credentials"
    id: UUID = SField(default_factory=uuid4, primary_key=True)
    user_id: UUID = SField(index=True)
    credential_id: str = SField(unique=True, index=True)  # base64url credential id
    public_key: str  # base64-encoded public key
    transports: str  # JSON-encoded list of transport strings
    sign_count: int = 0
    created_at: datetime  # UTC

# --- Request schemas (schema-level validation -> pydantic.ValidationError) ---

class LoginRequest(BaseModel):
    identifier: str = Field(min_length=1, max_length=320)  # username or email
    password: str = Field(min_length=1, max_length=1024)

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetComplete(BaseModel):
    token: str = Field(min_length=1, max_length=256)
    new_password: str  # validated with the shared rules (8..128 chars, letter + digit)

class PasskeyRegistrationBegin(BaseModel):
    user_id: UUID
    username: str = Field(min_length=1, max_length=320)
    display_name: str | None = None

class PasskeyRegistrationComplete(BaseModel):
    user_id: UUID
    response: dict[str, Any]  # WebAuthn registration response (JSON)

class PasskeyLoginBegin(BaseModel):
    credential_id: str = Field(min_length=1, max_length=512)  # base64url

class PasskeyLoginComplete(BaseModel):
    credential_id: str = Field(min_length=1, max_length=512)  # base64url
    response: dict[str, Any]  # WebAuthn authentication response (JSON)

# --- Representations (no hash, no raw token after the initial return) ---

class SessionInfo(BaseModel):
    user_id: UUID
    created_at: datetime
    expires_at: datetime

class LoginResult(BaseModel):
    user: UserRead  # from backend.usermanagement
    session: SessionInfo
    token: str  # raw opaque token; returned exactly once, at login

class WebAuthnCredentialRead(BaseModel):
    credential_id: str  # base64url
    transports: list[str]
    created_at: datetime

# --- Verified WebAuthn results (provider -> service) ---

class VerifiedCredential(BaseModel):
    credential_id: str  # base64url
    public_key: str  # base64
    transports: list[str]
    sign_count: int

class VerifiedAssertion(BaseModel):
    credential_id: str  # base64url
    sign_count: int

# --- Errors (service-level; messages free of secrets) ---

class AuthenticationError(Exception):
    """Base class for all authentication domain errors."""

class InvalidCredentialsError(AuthenticationError):
    """Unified login failure: unknown user, wrong password, inactive user, or locked."""

class InvalidSessionError(AuthenticationError):
    """The session token is unknown, revoked, or expired."""

class InvalidResetTokenError(AuthenticationError):
    """The reset token is invalid. ``reason`` is ``"unknown"``, ``"expired"``, or ``"used"``."""
    def __init__(self, reason: str) -> None: ...

class PasskeyCredentialNotFoundError(AuthenticationError):
    """No stored WebAuthn credential for the requested credential id."""

class InvalidPasskeyResponseError(AuthenticationError):
    """The WebAuthn response failed verification (registration or authentication)."""

class PasskeyHijackError(AuthenticationError):
    """The assertion sign count is lower than the stored sign count (hijack signal)."""

# --- Structural protocols (ABCs for swappable backends) ---

class AttemptTracker(ABC):
    @abstractmethod
    def record_failure(self, identifier: str) -> None: ...
    @abstractmethod
    def record_success(self, identifier: str) -> None: ...
    @abstractmethod
    def is_locked(self, identifier: str) -> bool: ...

class WebAuthnProvider(ABC):
    @abstractmethod
    def generate_registration_options(
        self, user_id: UUID, username: str, display_name: str | None
    ) -> dict[str, Any]: ...
    @abstractmethod
    def verify_registration_response(
        self, user_id: UUID, username: str, response: dict[str, Any]
    ) -> VerifiedCredential: ...
    @abstractmethod
    def generate_authentication_options(self, credential_id: str) -> dict[str, Any]: ...
    @abstractmethod
    def verify_authentication_response(
        self, credential_id: str, response: dict[str, Any]
    ) -> VerifiedAssertion: ...

# --- Repositories (ABCs + Sqlite* implementations) ---

class SessionRepository(ABC):
    @abstractmethod
    def add(self, session: Session) -> Session: ...
    @abstractmethod
    def get_by_token_hash(self, token_hash: str) -> Session | None: ...
    @abstractmethod
    def revoke(self, session_id: UUID) -> None: ...
    @abstractmethod
    def revoke_all_for_user(self, user_id: UUID) -> None: ...
    @abstractmethod
    def delete_expired(self) -> int: ...

class PasswordResetRepository(ABC):
    @abstractmethod
    def add(self, reset: PasswordReset) -> PasswordReset: ...
    @abstractmethod
    def get_by_token_hash(self, token_hash: str) -> PasswordReset | None: ...
    @abstractmethod
    def invalidate_all_for_user(self, user_id: UUID) -> None: ...
    @abstractmethod
    def mark_used(self, reset_id: UUID) -> None: ...

class WebAuthnCredentialRepository(ABC):
    @abstractmethod
    def add(self, credential: WebAuthnCredential) -> WebAuthnCredential: ...
    @abstractmethod
    def get_by_credential_id(self, credential_id: str) -> WebAuthnCredential | None: ...
    @abstractmethod
    def list_for_user(self, user_id: UUID) -> Sequence[WebAuthnCredential]: ...
    @abstractmethod
    def update_sign_count(self, credential_id: str, sign_count: int) -> None: ...
    @abstractmethod
    def delete(self, credential_id: str) -> None: ...

# --- Events (typed lifecycle; non-sensitive data only) ---

class AuthEvent(BaseModel):
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

class LoginSucceeded(AuthEvent):
    user_id: UUID
    method: str  # "password" | "passkey"

class LoginFailed(AuthEvent):
    identifier: str  # the identifier as attempted (username/email or credential id)
    method: str  # "password" | "passkey"

class Logout(AuthEvent):
    user_id: UUID

class PasswordResetRequested(AuthEvent):
    email: str

class PasswordResetCompleted(AuthEvent):
    user_id: UUID

class PasskeyRegistered(AuthEvent):
    user_id: UUID
    credential_id: str

class PasskeyDeleted(AuthEvent):
    user_id: UUID
    credential_id: str

# --- Service ---

class AuthService:
    def __init__(
        self,
        user_manager: UserManager,  # from backend.usermanagement
        user_repository: UserRepository,  # from backend.usermanagement (lookup)
        session_repository: SessionRepository,
        reset_repository: PasswordResetRepository,
        webauthn_repository: WebAuthnCredentialRepository,
        webauthn_provider: WebAuthnProvider | None = None,  # default: PyWebAuthnProvider(rp_id, rp_name, origin)
        event_bus: EventPublisher | None = None,
        attempt_tracker: AttemptTracker | None = None,  # default: InMemoryAttemptTracker(max_failed_attempts, lockout_duration)
        session_ttl: timedelta = timedelta(days=7),
        reset_token_ttl: timedelta = timedelta(minutes=15),
        max_failed_attempts: int = 5,
        lockout_duration: timedelta = timedelta(minutes=15),
        rp_id: str = "localhost",
        rp_name: str = "Python Template",
        origin: str = "http://localhost:3000",
    ) -> None: ...

    def login(self, request: LoginRequest) -> LoginResult: ...
    def logout(self, token: str) -> None: ...
    def session_info(self, token: str) -> SessionInfo: ...
    def request_password_reset(self, request: PasswordResetRequest) -> None: ...
    def complete_password_reset(self, request: PasswordResetComplete) -> None: ...
    def begin_passkey_registration(self, request: PasskeyRegistrationBegin) -> dict[str, Any]: ...
    def complete_passkey_registration(self, request: PasskeyRegistrationComplete) -> WebAuthnCredentialRead: ...
    def begin_passkey_login(self, request: PasskeyLoginBegin) -> dict[str, Any]: ...
    def complete_passkey_login(self, request: PasskeyLoginComplete) -> LoginResult: ...
    def list_passkeys(self, user_id: UUID) -> list[WebAuthnCredentialRead]: ...
    def delete_passkey(self, user_id: UUID, credential_id: str) -> None: ...
```

Notes on the schema:
- `UserManager`, `UserRepository`, `UserRead`, and `EventPublisher` are imported from `backend.usermanagement` (public API only).
- `InMemoryAttemptTracker` (default) is thread-safe; it tracks per-identifier failure counts and lock-until timestamps, and `record_success` clears the identifier's state.
- `PyWebAuthnProvider` (default) is constructed with `rp_id`, `rp_name`, and `origin`; its `verify_*` methods raise `InvalidPasskeyResponseError` when the underlying `py-webauthn` verification fails.
- `complete_password_reset` validates `new_password` with the shared user-management password rules (8..128 chars, at least one letter and one digit); violations raise `pydantic.ValidationError`.
- `delete_passkey` raises `PasskeyCredentialNotFoundError` when the credential id is unknown or does not belong to the user.
- `begin_passkey_login` raises `PasskeyCredentialNotFoundError` when the credential id is not stored.
- `complete_passkey_login` with a verified assertion updates the stored sign count to the response's sign count before issuing the session.

## 4. Requirements

| ID | Requirement |
|----|-------------|
| REQ-001 | The service authenticates a user by username or email plus password and, on success, returns a `LoginResult` containing the user's `UserRead`, a `SessionInfo`, and a new opaque session token. |
| REQ-002 | Password verification uses the stored Argon2id hash via the user-management feature (`UserManager.verify_password`); the service never stores or returns the hash. |
| REQ-003 | Login failure for an unknown user, a wrong password, or an inactive user raises the unified `InvalidCredentialsError` (no user enumeration; no lock-state signal). |
| REQ-004 | Login attempts for an identifier that reach `max_failed_attempts` failures lock the identifier for `lockout_duration`; while locked, attempts fail with `InvalidCredentialsError` even with the correct password; a successful login clears the identifier's failure state. |
| REQ-005 | Every login attempt performs an Argon2id verification even when no user matches the identifier (dummy verification), so timing does not reveal whether the identifier exists. |
| REQ-006 | Session tokens are 256-bit random (`secrets.token_urlsafe(32)`), URL-safe, returned exactly once at login, and stored only as their SHA-256 hash. |
| REQ-007 | A session expires `session_ttl` (default 7 days, configurable) after creation; expired sessions are invalid. |
| REQ-008 | `session_info(token)` returns the `SessionInfo` for a valid, unexpired, unrevoked session; unknown, revoked, or expired tokens raise `InvalidSessionError`. |
| REQ-009 | `logout(token)` revokes the session server-side so the token becomes immediately unusable; `logout` with an unknown, revoked, or expired token is an idempotent no-op. |
| REQ-010 | `request_password_reset(email)` always succeeds (no user enumeration); a reset token is created only when the email is registered. |
| REQ-011 | Reset tokens are single-use, expire after `reset_token_ttl` (default 15 minutes, configurable), and a new reset request for the same email invalidates all prior tokens for that email. |
| REQ-012 | `complete_password_reset(token, new_password)` with a valid token changes the password via the user-management feature (shared password rules), consumes the token, and revokes all sessions for the user. |
| REQ-013 | `complete_password_reset` with an unknown, expired, or used token raises `InvalidResetTokenError` with the corresponding `reason` (`"unknown"`, `"expired"`, `"used"`). |
| REQ-014 | Passkey registration: `begin_passkey_registration` returns WebAuthn registration options; `complete_passkey_registration` verifies the response via the WebAuthn provider and stores the credential (user id, credential id, public key, transports, sign count). |
| REQ-015 | Passkey login: `begin_passkey_login` returns WebAuthn authentication options for a stored credential; `complete_passkey_login` verifies the assertion, updates the stored sign count, and issues a session token (method `"passkey"`). |
| REQ-016 | A passkey assertion whose sign count is lower than the stored sign count is rejected with `PasskeyHijackError` and no session is issued (hijack detection). |
| REQ-017 | Passkey credentials can be listed per user (`list_passkeys`) and deleted (`delete_passkey`); deleting an unknown or foreign credential raises `PasskeyCredentialNotFoundError`. |
| REQ-018 | Password and passkey coexist: a user may log in with either method; enrolling or using one method does not disable the other. |
| REQ-019 | Input validation is schema-level (Pydantic request models → `pydantic.ValidationError`); domain failures raise the `AuthenticationError` hierarchy with secret-free messages. |
| REQ-020 | Typed lifecycle events are published to the injected `EventPublisher`: `LoginSucceeded`/`LoginFailed`, `Logout`, `PasswordResetRequested`, `PasswordResetCompleted`, `PasskeyRegistered`, `PasskeyDeleted`; a `None` publisher means no events; no event is published on other failures. |
| REQ-021 | Service representations (`LoginResult`, `SessionInfo`, `WebAuthnCredentialRead`) never expose `password_hash` or the raw session token after the initial login return. |
| REQ-022 | The service is traced with the shared logging feature (`@logged_class`); `include_args` stays `False`; passwords and tokens never appear in log records. |

## 5. Acceptance Criteria

| ID | References | Criterion |
|----|------------|-----------|
| AC-001 | REQ-001 | **Given** a user with a valid password, **When** `login` is called with the username and the correct password, **Then** a `LoginResult` is returned **and** `session_info` succeeds for the returned token. |
| AC-002 | REQ-001 | **Given** a user with a valid password, **When** `login` is called with the email and the correct password, **Then** a `LoginResult` is returned. |
| AC-003 | REQ-003 | **Given** a user, **When** `login` is called with the wrong password, **Then** `InvalidCredentialsError` is raised. |
| AC-004 | REQ-003 | **Given** no such user, **When** `login` is called with an unknown identifier, **Then** `InvalidCredentialsError` is raised (the same error kind as AC-003). |
| AC-005 | REQ-003 | **Given** an inactive user, **When** `login` is called with the correct password, **Then** `InvalidCredentialsError` is raised. |
| AC-006 | REQ-004 | **Given** `max_failed_attempts - 1` failed logins for an identifier, **When** the next login is attempted, **Then** the identifier is not yet locked and the attempt is evaluated normally. |
| AC-007 | REQ-004 | **Given** `max_failed_attempts` failed logins for an identifier, **When** `login` is attempted with the correct password during the lockout window, **Then** `InvalidCredentialsError` is raised. |
| AC-008 | REQ-004 | **Given** a locked identifier, **When** the lockout window has elapsed and `login` is attempted with the correct password, **Then** the login succeeds **and** the identifier's failure state is cleared. |
| AC-009 | REQ-005 | **Given** no such user, **When** `login` is attempted, **Then** an Argon2id verification is still executed (dummy verification against a fixed dummy hash). |
| AC-010 | REQ-006 | **Given** a successful login, **When** the token is inspected, **Then** it is URL-safe 256-bit (43 chars for `token_urlsafe(32)`) **and** the store contains only its SHA-256 hash. |
| AC-011 | REQ-007 | **Given** a session created with TTL `T`, **When** `session_info` is called after `T` has elapsed, **Then** `InvalidSessionError` is raised. |
| AC-012 | REQ-008 | **Given** a valid session, **When** `session_info(token)` is called, **Then** `SessionInfo(user_id, created_at, expires_at)` is returned. |
| AC-013 | REQ-009 | **Given** a valid session, **When** `logout(token)` is called, **Then** the token is immediately unusable (`session_info` raises `InvalidSessionError`). |
| AC-014 | REQ-009 | **Given** an unknown, revoked, or expired token, **When** `logout(token)` is called, **Then** no error is raised (idempotent no-op). |
| AC-015 | REQ-010 | **Given** a registered email, **When** `request_password_reset` is called, **Then** no error is raised **and** a reset token is created. |
| AC-016 | REQ-010 | **Given** an unregistered email, **When** `request_password_reset` is called, **Then** no error is raised **and** no reset token is created. |
| AC-017 | REQ-011 | **Given** a created reset token, **When** `complete_password_reset` is called with it, **Then** the token is consumed **and** a second completion with the same token raises `InvalidResetTokenError` with `reason="used"`. |
| AC-018 | REQ-011 | **Given** a created reset token, **When** a new reset request is made for the same email, **Then** the prior token is invalidated. |
| AC-019 | REQ-012 | **Given** a valid reset token, **When** `complete_password_reset` is called with a strong new password, **Then** the password is changed (login with the new password succeeds, login with the old password fails) **and** all sessions for the user are revoked. |
| AC-020 | REQ-013 | **Given** an expired reset token, **When** `complete_password_reset` is called, **Then** `InvalidResetTokenError` with `reason="expired"` is raised. |
| AC-021 | REQ-013 | **Given** an unknown reset token, **When** `complete_password_reset` is called, **Then** `InvalidResetTokenError` with `reason="unknown"` is raised. |
| AC-022 | REQ-014 | **Given** a valid user, **When** `begin_passkey_registration` is called, **Then** WebAuthn registration options are returned. |
| AC-023 | REQ-014 | **Given** registration options, **When** `complete_passkey_registration` is called with a verified response, **Then** the credential is stored **and** `WebAuthnCredentialRead` is returned. |
| AC-024 | REQ-015 | **Given** a stored credential, **When** `begin_passkey_login` is called, **Then** WebAuthn authentication options are returned. |
| AC-025 | REQ-015 | **Given** authentication options, **When** `complete_passkey_login` is called with a verified assertion, **Then** a session token is issued (`LoginResult`) **and** the stored sign count is updated to the response's sign count. |
| AC-026 | REQ-016 | **Given** a stored credential with sign count `N`, **When** `complete_passkey_login` is called with a response sign count `< N`, **Then** `PasskeyHijackError` is raised **and** no session is issued. |
| AC-027 | REQ-017 | **Given** stored credentials for a user, **When** `list_passkeys` is called, **Then** all credentials for the user are returned. |
| AC-028 | REQ-017 | **Given** a stored credential, **When** `delete_passkey` is called, **Then** the credential is removed. |
| AC-029 | REQ-018 | **Given** a user with both a password and a passkey, **When** login is attempted with either method, **Then** both succeed. |
| AC-030 | REQ-019 | **Given** a login request with an empty identifier, **When** validation runs, **Then** `pydantic.ValidationError` is raised. |
| AC-031 | REQ-020 | **Given** a publisher, **When** `login` succeeds, **Then** `LoginSucceeded` is published. |
| AC-032 | REQ-020 | **Given** a publisher, **When** `login` fails, **Then** `LoginFailed` is published. |
| AC-033 | REQ-020 | **Given** a publisher, **When** logout, reset request, reset completion, passkey registration, or passkey deletion succeeds, **Then** the corresponding event is published; **and** given a `None` publisher, no event is published and no error is raised. |
| AC-034 | REQ-021 | **Given** any service representation (`LoginResult`, `SessionInfo`, `WebAuthnCredentialRead`), **When** its fields are inspected, **Then** no `password_hash` field is present **and** no raw session token is present except the initial `LoginResult.token`. |
| AC-035 | REQ-022 | **Given** the service, **When** its methods are called, **Then** no log record contains the password or the raw session token. |

## 6. Invariants

| ID | Invariant |
|----|-----------|
| INV-001 | For any set of generated session or reset tokens, the stored SHA-256 hashes are pairwise distinct (no two tokens map to the same stored hash). |
| INV-002 | A session token is valid if and only if its session is unrevoked and unexpired: `session_info` succeeds exactly when `revoked == False` and `expires_at > now`. |
| INV-003 | A reset token is usable at most once: after a successful `complete_password_reset`, the same token is no longer usable (double-spend impossible). |
| INV-004 | For any sequence of fewer than `max_failed_attempts` failures for an identifier, the identifier is not locked; after `max_failed_attempts` failures it is locked for the full `lockout_duration`; after a success it is never locked. |
| INV-005 | For any login attempt (success or failure), the password never appears in any observable output: the returned `LoginResult`, the raised error's message, or the published events. |

## 7. Edge Cases & Error Conditions

| ID | Condition | Expected Behavior |
|----|-----------|-------------------|
| EDGE-001 | Login with an identifier that matches neither a username nor an email | `InvalidCredentialsError`; no internal exception escapes. |
| EDGE-002 | Login with an inactive user | `InvalidCredentialsError` (same error kind as a wrong password). |
| EDGE-003 | Login while the identifier is locked | `InvalidCredentialsError` even with the correct password. |
| EDGE-004 | `session_info` with an expired token | `InvalidSessionError`. |
| EDGE-005 | `session_info` with a revoked token | `InvalidSessionError`. |
| EDGE-006 | `logout` called twice with the same token | The second call is an idempotent no-op (no error). |
| EDGE-007 | Reset request for an unknown email | No error; no token created. |
| EDGE-008 | Reset completion with an expired token | `InvalidResetTokenError` with `reason="expired"`. |
| EDGE-009 | Reset completion with a used token | `InvalidResetTokenError` with `reason="used"`. |
| EDGE-010 | Reset completion with an unknown token | `InvalidResetTokenError` with `reason="unknown"`. |
| EDGE-011 | A new reset request after a token was created | All prior tokens for the same email are invalidated. |
| EDGE-012 | Reset completion with a weak new password (violates shared rules) | `pydantic.ValidationError`. |
| EDGE-013 | Passkey registration completion with an invalid/failed WebAuthn response | `InvalidPasskeyResponseError`; nothing is stored. |
| EDGE-014 | `begin_passkey_login` with an unregistered credential id | `PasskeyCredentialNotFoundError`. |
| EDGE-015 | Passkey login completion with a sign-count regression | `PasskeyHijackError`; no session issued. |
| EDGE-016 | Passkey login completion with a failed assertion | `InvalidPasskeyResponseError`; no session issued. |
| EDGE-017 | `session_info` for a valid session | The raw token is not returned (only `SessionInfo`). |
| EDGE-018 | Login with an empty identifier | `pydantic.ValidationError`. |

## 8. Non-Functional Requirements

| ID | Category | Requirement |
|----|----------|-------------|
| NFR-001 | Performance | A password login (Argon2id verify + SQLite round-trips + attempt-tracker update) completes in ≤ 250 ms at p95, measured on local hardware against a local SQLite database with the shared logging feature configured at its default INFO level with a synchronous console sink (DEBUG method tracing off); the budget holds including the per-call logging overhead at that level. |
| NFR-002 | Security | Passwords, raw session tokens, raw reset tokens, and password hashes never appear in log records, events, or error messages; session and reset tokens are ≥ 256-bit random; tokens are stored only as SHA-256 hashes. |
| NFR-003 | Contract | The public API of `backend.authentication` (service, request/representation models, error hierarchy, repository ABCs, provider ABCs, events) is a backward-compatibility contract. |
| NFR-004 | Observability | The service is traced with `@logged_class` (entry/exit/exception per public method); lifecycle events are published to the injected publisher. |
| NFR-005 | Reliability | The service and the SQLite repositories are safe for concurrent use from multiple threads (each operation opens its own session; SQLite busy-timeout serializes concurrent writers; the in-memory attempt tracker is internally locked). |

## 9. Observability & Logging

| Operation / Event | Level | Context |
|-------------------|-------|---------|
| Public method entry/exit (all `AuthService` methods) | DEBUG | Method name, elapsed ms; no arguments (`include_args` stays `False`). |
| Method exception (any `AuthenticationError` raised) | DEBUG | Exception type and secret-free message (e.g., `InvalidCredentialsError`); no identifier, no token, no password. |
| Lifecycle events | — | Published to the injected `EventPublisher` (not logged by this feature); events carry non-sensitive data only. |

- **Default level:** DEBUG for method tracing (off by default at the INFO default level); exceptions are logged with secret-free messages.
- **Error conditions:** Every domain error is an `AuthenticationError` subclass with a secret-free message (error kind only); schema-level validation failures are `pydantic.ValidationError` identifying the offending field name (never the field value).

## 10. Test Strategy

| ID | Test Category | Test File | Test Function |
|----|---------------|-----------|---------------|
| AC-001 | acceptance | `tests/acceptance/authentication/test_login.py` | `test_ac_001_login_by_username_success` |
| AC-002 | acceptance | `tests/acceptance/authentication/test_login.py` | `test_ac_002_login_by_email_success` |
| AC-003 | acceptance | `tests/acceptance/authentication/test_login.py` | `test_ac_003_login_wrong_password_rejected` |
| AC-004 | acceptance | `tests/acceptance/authentication/test_login.py` | `test_ac_004_login_unknown_user_rejected` |
| AC-005 | acceptance | `tests/acceptance/authentication/test_login.py` | `test_ac_005_login_inactive_user_rejected` |
| AC-006 | acceptance | `tests/acceptance/authentication/test_lockout.py` | `test_ac_006_below_max_failures_not_locked` |
| AC-007 | acceptance | `tests/acceptance/authentication/test_lockout.py` | `test_ac_007_locked_identifier_rejected_even_correct_password` |
| AC-008 | acceptance | `tests/acceptance/authentication/test_lockout.py` | `test_ac_008_lockout_expires_and_success_clears` |
| AC-009 | acceptance | `tests/acceptance/authentication/test_timing.py` | `test_ac_009_dummy_verify_on_unknown_user` |
| AC-010 | acceptance | `tests/acceptance/authentication/test_sessions.py` | `test_ac_010_token_format_and_hashed_at_rest` |
| AC-011 | acceptance | `tests/acceptance/authentication/test_sessions.py` | `test_ac_011_session_expiry` |
| AC-012 | acceptance | `tests/acceptance/authentication/test_sessions.py` | `test_ac_012_session_info_valid` |
| AC-013 | acceptance | `tests/acceptance/authentication/test_sessions.py` | `test_ac_013_logout_revokes` |
| AC-014 | acceptance | `tests/acceptance/authentication/test_sessions.py` | `test_ac_014_logout_invalid_noop` |
| AC-015 | acceptance | `tests/acceptance/authentication/test_password_reset.py` | `test_ac_015_reset_request_registered_email` |
| AC-016 | acceptance | `tests/acceptance/authentication/test_password_reset.py` | `test_ac_016_reset_request_unknown_email` |
| AC-017 | acceptance | `tests/acceptance/authentication/test_password_reset.py` | `test_ac_017_reset_token_single_use` |
| AC-018 | acceptance | `tests/acceptance/authentication/test_password_reset.py` | `test_ac_018_new_request_supersedes` |
| AC-019 | acceptance | `tests/acceptance/authentication/test_password_reset.py` | `test_ac_019_reset_completes_and_revokes_sessions` |
| AC-020 | acceptance | `tests/acceptance/authentication/test_password_reset.py` | `test_ac_020_reset_expired_token` |
| AC-021 | acceptance | `tests/acceptance/authentication/test_password_reset.py` | `test_ac_021_reset_unknown_token` |
| AC-022 | acceptance | `tests/acceptance/authentication/test_passkey.py` | `test_ac_022_begin_registration_options` |
| AC-023 | acceptance | `tests/acceptance/authentication/test_passkey.py` | `test_ac_023_complete_registration_stores` |
| AC-024 | acceptance | `tests/acceptance/authentication/test_passkey.py` | `test_ac_024_begin_login_options` |
| AC-025 | acceptance | `tests/acceptance/authentication/test_passkey.py` | `test_ac_025_complete_login_issues_session` |
| AC-026 | acceptance | `tests/acceptance/authentication/test_passkey.py` | `test_ac_026_hijack_detected` |
| AC-027 | acceptance | `tests/acceptance/authentication/test_passkey.py` | `test_ac_027_list_passkeys` |
| AC-028 | acceptance | `tests/acceptance/authentication/test_passkey.py` | `test_ac_028_delete_passkey` |
| AC-029 | acceptance | `tests/acceptance/authentication/test_passkey.py` | `test_ac_029_password_and_passkey_coexist` |
| AC-030 | acceptance | `tests/acceptance/authentication/test_validation.py` | `test_ac_030_empty_identifier_validation_error` |
| AC-031 | acceptance | `tests/acceptance/authentication/test_events.py` | `test_ac_031_login_success_event` |
| AC-032 | acceptance | `tests/acceptance/authentication/test_events.py` | `test_ac_032_login_failed_event` |
| AC-033 | acceptance | `tests/acceptance/authentication/test_events.py` | `test_ac_033_lifecycle_events_and_none_publisher` |
| AC-034 | acceptance | `tests/acceptance/authentication/test_representation.py` | `test_ac_034_no_hash_in_representations` |
| AC-035 | acceptance | `tests/acceptance/authentication/test_logging.py` | `test_ac_035_no_secrets_in_log_records` |
| INV-001 | property | `tests/property/authentication/test_tokens.py` | `test_inv_001_token_hash_uniqueness` |
| INV-002 | property | `tests/property/authentication/test_sessions.py` | `test_inv_002_session_validity_iff_unexpired_unrevoked` |
| INV-003 | property | `tests/property/authentication/test_reset.py` | `test_inv_003_reset_token_at_most_once` |
| INV-004 | property | `tests/property/authentication/test_lockout.py` | `test_inv_004_lockout_threshold` |
| INV-005 | property | `tests/property/authentication/test_secrets.py` | `test_inv_005_no_password_in_observable_output` |
| EDGE-001 | unit | `tests/unit/authentication/test_login.py` | `test_edge_001_login_neither_username_nor_email` |
| EDGE-002 | unit | `tests/unit/authentication/test_login.py` | `test_edge_002_login_inactive_user` |
| EDGE-003 | unit | `tests/unit/authentication/test_lockout.py` | `test_edge_003_login_while_locked` |
| EDGE-004 | unit | `tests/unit/authentication/test_sessions.py` | `test_edge_004_session_info_expired` |
| EDGE-005 | unit | `tests/unit/authentication/test_sessions.py` | `test_edge_005_session_info_revoked` |
| EDGE-006 | unit | `tests/unit/authentication/test_sessions.py` | `test_edge_006_logout_twice_noop` |
| EDGE-007 | unit | `tests/unit/authentication/test_reset.py` | `test_edge_007_reset_unknown_email_no_token` |
| EDGE-008 | unit | `tests/unit/authentication/test_reset.py` | `test_edge_008_reset_expired_token` |
| EDGE-009 | unit | `tests/unit/authentication/test_reset.py` | `test_edge_009_reset_used_token` |
| EDGE-010 | unit | `tests/unit/authentication/test_reset.py` | `test_edge_010_reset_unknown_token` |
| EDGE-011 | unit | `tests/unit/authentication/test_reset.py` | `test_edge_011_new_request_supersedes` |
| EDGE-012 | unit | `tests/unit/authentication/test_reset.py` | `test_edge_012_reset_weak_password` |
| EDGE-013 | unit | `tests/unit/authentication/test_passkey.py` | `test_edge_013_registration_invalid_response` |
| EDGE-014 | unit | `tests/unit/authentication/test_passkey.py` | `test_edge_014_begin_login_unregistered_credential` |
| EDGE-015 | unit | `tests/unit/authentication/test_passkey.py` | `test_edge_015_hijack_detected` |
| EDGE-016 | unit | `tests/unit/authentication/test_passkey.py` | `test_edge_016_login_failed_assertion` |
| EDGE-017 | unit | `tests/unit/authentication/test_sessions.py` | `test_edge_017_session_info_no_token` |
| EDGE-018 | unit | `tests/unit/authentication/test_login.py` | `test_edge_018_empty_identifier` |
| NFR-001 | contract | `tests/contract/authentication/test_performance.py` | `test_nfr_001_login_performance_budget` |
| NFR-002 | contract | `tests/contract/authentication/test_secrets.py` | `test_nfr_002_no_secrets_in_logs_or_events` |
| NFR-003 | contract | `tests/contract/authentication/test_public_api.py` | `test_nfr_003_public_api_stable` |
| NFR-004 | contract | `tests/contract/authentication/test_logging.py` | `test_nfr_004_service_traced` |
| NFR-005 | integration | `tests/integration/authentication/test_concurrency.py` | `test_nfr_005_concurrent_login_thread_safety` |
| — | integration | `tests/integration/authentication/test_sqlite_repositories.py` | `test_session_repository_roundtrip`, `test_reset_repository_roundtrip`, `test_webauthn_repository_roundtrip`, `test_full_flow_login_reset_logout` |

## 11. Traceability Matrix

Maintain this matrix as tests are written and pass. Every normative requirement MUST have at least one executable test.

| Requirement | Acceptance Criterion | Test | Status |
|-------------|---------------------|------|--------|
| REQ-001 | AC-001 | `test_ac_001_login_by_username_success` | PENDING |
| REQ-001 | AC-002 | `test_ac_002_login_by_email_success` | PENDING |
| REQ-002 | AC-003 | `test_ac_003_login_wrong_password_rejected` | PENDING |
| REQ-003 | AC-003 | `test_ac_003_login_wrong_password_rejected` | PENDING |
| REQ-003 | AC-004 | `test_ac_004_login_unknown_user_rejected` | PENDING |
| REQ-003 | AC-005 | `test_ac_005_login_inactive_user_rejected` | PENDING |
| REQ-004 | AC-006 | `test_ac_006_below_max_failures_not_locked` | PENDING |
| REQ-004 | AC-007 | `test_ac_007_locked_identifier_rejected_even_correct_password` | PENDING |
| REQ-004 | AC-008 | `test_ac_008_lockout_expires_and_success_clears` | PENDING |
| REQ-005 | AC-009 | `test_ac_009_dummy_verify_on_unknown_user` | PENDING |
| REQ-006 | AC-010 | `test_ac_010_token_format_and_hashed_at_rest` | PENDING |
| REQ-007 | AC-011 | `test_ac_011_session_expiry` | PENDING |
| REQ-008 | AC-012 | `test_ac_012_session_info_valid` | PENDING |
| REQ-009 | AC-013 | `test_ac_013_logout_revokes` | PENDING |
| REQ-009 | AC-014 | `test_ac_014_logout_invalid_noop` | PENDING |
| REQ-010 | AC-015 | `test_ac_015_reset_request_registered_email` | PENDING |
| REQ-010 | AC-016 | `test_ac_016_reset_request_unknown_email` | PENDING |
| REQ-011 | AC-017 | `test_ac_017_reset_token_single_use` | PENDING |
| REQ-011 | AC-018 | `test_ac_018_new_request_supersedes` | PENDING |
| REQ-012 | AC-019 | `test_ac_019_reset_completes_and_revokes_sessions` | PENDING |
| REQ-013 | AC-020 | `test_ac_020_reset_expired_token` | PENDING |
| REQ-013 | AC-021 | `test_ac_021_reset_unknown_token` | PENDING |
| REQ-014 | AC-022 | `test_ac_022_begin_registration_options` | PENDING |
| REQ-014 | AC-023 | `test_ac_023_complete_registration_stores` | PENDING |
| REQ-015 | AC-024 | `test_ac_024_begin_login_options` | PENDING |
| REQ-015 | AC-025 | `test_ac_025_complete_login_issues_session` | PENDING |
| REQ-016 | AC-026 | `test_ac_026_hijack_detected` | PENDING |
| REQ-017 | AC-027 | `test_ac_027_list_passkeys` | PENDING |
| REQ-017 | AC-028 | `test_ac_028_delete_passkey` | PENDING |
| REQ-018 | AC-029 | `test_ac_029_password_and_passkey_coexist` | PENDING |
| REQ-019 | AC-030 | `test_ac_030_empty_identifier_validation_error` | PENDING |
| REQ-020 | AC-031 | `test_ac_031_login_success_event` | PENDING |
| REQ-020 | AC-032 | `test_ac_032_login_failed_event` | PENDING |
| REQ-020 | AC-033 | `test_ac_033_lifecycle_events_and_none_publisher` | PENDING |
| REQ-021 | AC-034 | `test_ac_034_no_hash_in_representations` | PENDING |
| REQ-022 | AC-035 | `test_ac_035_no_secrets_in_log_records` | PENDING |
| INV-001 | — | `test_inv_001_token_hash_uniqueness` | PENDING |
| INV-002 | — | `test_inv_002_session_validity_iff_unexpired_unrevoked` | PENDING |
| INV-003 | — | `test_inv_003_reset_token_at_most_once` | PENDING |
| INV-004 | — | `test_inv_004_lockout_threshold` | PENDING |
| INV-005 | — | `test_inv_005_no_password_in_observable_output` | PENDING |
| EDGE-001 | — | `test_edge_001_login_neither_username_nor_email` | PENDING |
| EDGE-002 | — | `test_edge_002_login_inactive_user` | PENDING |
| EDGE-003 | — | `test_edge_003_login_while_locked` | PENDING |
| EDGE-004 | — | `test_edge_004_session_info_expired` | PENDING |
| EDGE-005 | — | `test_edge_005_session_info_revoked` | PENDING |
| EDGE-006 | — | `test_edge_006_logout_twice_noop` | PENDING |
| EDGE-007 | — | `test_edge_007_reset_unknown_email_no_token` | PENDING |
| EDGE-008 | — | `test_edge_008_reset_expired_token` | PENDING |
| EDGE-009 | — | `test_edge_009_reset_used_token` | PENDING |
| EDGE-010 | — | `test_edge_010_reset_unknown_token` | PENDING |
| EDGE-011 | — | `test_edge_011_new_request_supersedes` | PENDING |
| EDGE-012 | — | `test_edge_012_reset_weak_password` | PENDING |
| EDGE-013 | — | `test_edge_013_registration_invalid_response` | PENDING |
| EDGE-014 | — | `test_edge_014_begin_login_unregistered_credential` | PENDING |
| EDGE-015 | — | `test_edge_015_hijack_detected` | PENDING |
| EDGE-016 | — | `test_edge_016_login_failed_assertion` | PENDING |
| EDGE-017 | — | `test_edge_017_session_info_no_token` | PENDING |
| EDGE-018 | — | `test_edge_018_empty_identifier` | PENDING |
| NFR-001 | — | `test_nfr_001_login_performance_budget` | PENDING |
| NFR-002 | — | `test_nfr_002_no_secrets_in_logs_or_events` | PENDING |
| NFR-003 | — | `test_nfr_003_public_api_stable` | PENDING |
| NFR-004 | — | `test_nfr_004_service_traced` | PENDING |
| NFR-005 | — | `test_nfr_005_concurrent_login_thread_safety` | PENDING |
