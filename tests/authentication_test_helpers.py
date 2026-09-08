"""Shared helpers for the authentication test suite.

Follows the usermanagement helper pattern: a synchronous event collector
for deterministic event assertions, a valid login field factory, a
configurable fake WebAuthn provider for deterministic passkey tests,
cross-platform absolute-path SQLite file URL construction, a fully wired
``AuthService`` factory, and the shared test fixtures.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path
from typing import Any

import pytest

from backend.authentication import (
    AuthService,
    InvalidPasskeyResponseError,
    SqlitePasswordResetRepository,
    SqliteSessionRepository,
    SqliteWebAuthnCredentialRepository,
    VerifiedAssertion,
    VerifiedCredential,
    WebAuthnProvider,
)
from backend.usermanagement import SqliteUserRepository, UserCreate, UserManager


class EventCollector:
    """A synchronous ``EventPublisher`` that collects published events.

    The spec's event ACs are phrased as "Given a publisher", so a
    synchronous collector (not the async event bus) yields deterministic
    assertions.
    """

    def __init__(self) -> None:
        self.events: list[Any] = []

    def publish(self, event: object) -> None:
        self.events.append(event)

    def of_type(self, event_type: type) -> list[Any]:
        return [e for e in self.events if isinstance(e, event_type)]


def db_url(tmp_path: Path, name: str = "auth.db") -> str:
    """A cross-platform absolute-path SQLite file URL under ``tmp_path``.

    POSIX absolute paths require four slashes (``sqlite:////abs``); Windows
    paths (``C:/...``) are already absolute and use three.
    """
    p = str(tmp_path / name).replace("\\", "/")
    prefix = "sqlite:////" if p.startswith("/") else "sqlite:///"
    return f"{prefix}{p}"


def valid_login(identifier: str = "alice", password: str = "correct-horse-1") -> dict[str, Any]:
    """A valid ``LoginRequest`` field mapping."""
    return {"identifier": identifier, "password": password}


def create_user(
    user_manager: UserManager,
    username: str = "alice",
    email: str = "alice@example.com",
    password: str = "correct-horse-1",
    role: str = "member",
) -> Any:
    """Create a user through user-management and return the ``UserRead``."""
    return user_manager.create_user(
        UserCreate(username=username, email=email, password=password, role=role)
    )


class FakeWebAuthnProvider(WebAuthnProvider):
    """A configurable ``WebAuthnProvider`` for deterministic passkey tests.

    The spec's passkey ACs are phrased as "Given ... a verified response",
    so a fake provider (not real py-webauthn verification, which requires a
    browser challenge) yields deterministic assertions.
    """

    def __init__(self) -> None:
        self.credential_id = "fake-credential"
        self.public_key = "fake-public-key"
        self.transports: list[str] = ["internal"]
        self.registration_options: dict[str, Any] = {"type": "registration-options"}
        self.authentication_options: dict[str, Any] = {"type": "authentication-options"}
        self.sign_count = 0
        self.fail_registration = False
        self.fail_assertion = False

    def generate_registration_options(self, user_id: Any, username: str, display_name: str | None) -> dict[str, Any]:
        return dict(self.registration_options)

    def verify_registration_response(self, user_id: Any, username: str, response: dict[str, Any]) -> VerifiedCredential:
        if self.fail_registration:
            raise InvalidPasskeyResponseError("registration response verification failed")
        return VerifiedCredential(
            credential_id=self.credential_id,
            public_key=self.public_key,
            transports=list(self.transports),
            sign_count=self.sign_count,
        )

    def generate_authentication_options(self, credential_id: str) -> dict[str, Any]:
        return dict(self.authentication_options)

    def verify_authentication_response(self, credential_id: str, response: dict[str, Any]) -> VerifiedAssertion:
        if self.fail_assertion:
            raise InvalidPasskeyResponseError("authentication response verification failed")
        return VerifiedAssertion(credential_id=credential_id, sign_count=self.sign_count)


@dataclass
class AuthFixture:
    """A fully wired ``AuthService`` and its collaborators."""

    service: AuthService
    user_manager: UserManager
    collector: EventCollector
    webauthn_provider: WebAuthnProvider
    session_repository: SqliteSessionRepository
    reset_repository: SqlitePasswordResetRepository
    webauthn_repository: SqliteWebAuthnCredentialRepository


def _wire(
    user_url: str,
    auth_url: str,
    *,
    collector: EventCollector | None,
    max_failed_attempts: int,
    lockout_duration: timedelta,
    session_ttl: timedelta,
    reset_token_ttl: timedelta,
    webauthn_provider: WebAuthnProvider | None,
) -> AuthFixture:
    """Wire the repositories and the ``AuthService`` over SQLite URLs."""
    user_repo = SqliteUserRepository(user_url)
    user_manager = UserManager(user_repo)
    session_repo = SqliteSessionRepository(auth_url)
    reset_repo = SqlitePasswordResetRepository(auth_url)
    webauthn_repo = SqliteWebAuthnCredentialRepository(auth_url)
    provider = webauthn_provider if webauthn_provider is not None else FakeWebAuthnProvider()
    service = AuthService(
        user_manager,
        user_repo,
        session_repo,
        reset_repo,
        webauthn_repo,
        webauthn_provider=provider,
        event_bus=collector,
        max_failed_attempts=max_failed_attempts,
        lockout_duration=lockout_duration,
        session_ttl=session_ttl,
        reset_token_ttl=reset_token_ttl,
    )
    return AuthFixture(
        service=service,
        user_manager=user_manager,
        collector=collector if collector is not None else EventCollector(),
        webauthn_provider=provider,
        session_repository=session_repo,
        reset_repository=reset_repo,
        webauthn_repository=webauthn_repo,
    )


def build_auth_service(
    tmp_path: Path,
    *,
    event_bus: EventCollector | None = None,
    max_failed_attempts: int = 5,
    lockout_duration: timedelta = timedelta(minutes=15),
    session_ttl: timedelta = timedelta(days=7),
    reset_token_ttl: timedelta = timedelta(minutes=15),
    webauthn_provider: WebAuthnProvider | None = None,
) -> AuthFixture:
    """Wire a full ``AuthService`` over SQLite stores under ``tmp_path``.

    ``event_bus=None`` passes ``None`` through to the service (the spec's
    "a None publisher means no events" case); a collector instance is used
    for event assertions.
    """
    return _wire(
        db_url(tmp_path, "users.db"),
        db_url(tmp_path, "auth.db"),
        collector=event_bus,
        max_failed_attempts=max_failed_attempts,
        lockout_duration=lockout_duration,
        session_ttl=session_ttl,
        reset_token_ttl=reset_token_ttl,
        webauthn_provider=webauthn_provider,
    )


def build_memory_auth_service(
    *,
    event_bus: EventCollector | None = None,
    max_failed_attempts: int = 5,
    lockout_duration: timedelta = timedelta(minutes=15),
    session_ttl: timedelta = timedelta(days=7),
    reset_token_ttl: timedelta = timedelta(minutes=15),
    webauthn_provider: WebAuthnProvider | None = None,
) -> AuthFixture:
    """Wire a full ``AuthService`` over in-memory SQLite (property tests).

    Each repository gets its own in-memory database; no cross-database
    queries occur, so separate ``:memory:`` URLs are correct.
    """
    return _wire(
        "sqlite:///:memory:",
        "sqlite:///:memory:",
        collector=event_bus,
        max_failed_attempts=max_failed_attempts,
        lockout_duration=lockout_duration,
        session_ttl=session_ttl,
        reset_token_ttl=reset_token_ttl,
        webauthn_provider=webauthn_provider,
    )


@pytest.fixture
def collector() -> EventCollector:
    return EventCollector()


@pytest.fixture
def auth(tmp_path: Path, collector: EventCollector) -> AuthFixture:
    return build_auth_service(tmp_path, event_bus=collector)


@pytest.fixture
def auth_service(auth: AuthFixture) -> AuthService:
    return auth.service


@pytest.fixture
def user_manager(auth: AuthFixture) -> UserManager:
    return auth.user_manager
