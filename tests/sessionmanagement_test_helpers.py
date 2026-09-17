"""Shared helpers for the sessionmanagement test suite.

Follows the house feature-helper pattern (``authentication_test_helpers``,
``settings_test_helpers``): a synchronous event collector for deterministic
event assertions, a cross-platform SQLite file URL builder, a session-row
factory over the reused authentication store, and a ``SessionService`` factory.

The feature package (``backend.sessionmanagement``) is imported lazily inside
``build_session_service`` so the RED state (module missing) shows up as a
per-test fixture error rather than a file-level collection error (house
pattern, see ``tests/conftest.py``).
"""

from __future__ import annotations

import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from uuid import UUID, uuid4

import pytest

from backend.authentication import hash_token, new_token
from backend.authentication.models import Session
from backend.authentication.repository import SqliteSessionRepository
from backend.settings import SettingsRegistry, YamlValueRepository


class EventCollector:
    """A synchronous ``EventPublisher`` that collects published events.

    The spec's event ACs are phrased as "Given a publisher", so a synchronous
    collector (not the async event bus) yields deterministic assertions.
    """

    def __init__(self) -> None:
        self.events: list[object] = []

    def publish(self, event: object) -> None:
        self.events.append(event)

    def of_type(self, event_type: type) -> list[object]:
        return [e for e in self.events if isinstance(e, event_type)]


def db_url(tmp_path: Path, name: str = "sessions.db") -> str:
    """A cross-platform absolute-path SQLite file URL under ``tmp_path``.

    POSIX absolute paths require four slashes (``sqlite:////abs``); Windows
    paths (``C:/...``) are already absolute and use three.
    """
    p = str(tmp_path / name).replace("\\", "/")
    prefix = "sqlite:////" if p.startswith("/") else "sqlite:///"
    return f"{prefix}{p}"


def make_session(
    repository: SqliteSessionRepository,
    user_id: UUID,
    *,
    created_at: datetime,
    expires_at: datetime | None = None,
    revoked: bool = False,
) -> tuple[Session, str]:
    """Insert a session row via the reused store's public ABC.

    Returns ``(row, raw_token)``. The row's ``token_hash`` is the SHA-256 hex
    of ``raw_token`` (matching authentication's token-at-rest contract), so
    ``raw_token`` resolves through the token path. Device columns are left at
    their defaults (``None``), modelling a pre-feature row (EDGE-006).
    """
    token = new_token()
    row = Session(
        user_id=user_id,
        token_hash=hash_token(token),
        created_at=created_at,
        expires_at=expires_at if expires_at is not None else created_at + timedelta(days=7),
        revoked=revoked,
    )
    repository.add(row)
    return row, token


def build_session_service(
    repository: SqliteSessionRepository,
    *,
    event_bus: EventCollector | None = None,
    settings_registry: SettingsRegistry | None = None,
) -> object:
    """Construct ``SessionService`` over the reused store (REQ-017, REQ-020).

    The feature package is imported lazily so the RED state (module missing)
    surfaces as a per-test fixture error, not a collection error. A ``None``
    ``settings_registry`` uses a fresh isolated registry (temp-dir value
    repository) so no test touches the shared default ``settings/`` directory.
    """
    from backend.sessionmanagement import SessionService

    if settings_registry is None:
        settings_registry = SettingsRegistry(
            value_repository=YamlValueRepository(tempfile.mkdtemp())
        )
    return SessionService(
        repository,
        event_bus=event_bus,
        settings_registry=settings_registry,
    )


@pytest.fixture
def user_id() -> UUID:
    return uuid4()


@pytest.fixture
def session_repository(tmp_path: Path) -> SqliteSessionRepository:
    return SqliteSessionRepository(db_url(tmp_path))


@pytest.fixture
def collector() -> EventCollector:
    return EventCollector()


@pytest.fixture
def settings_registry() -> SettingsRegistry:
    return SettingsRegistry(value_repository=YamlValueRepository(tempfile.mkdtemp()))


@pytest.fixture
def session_service(session_repository, collector, settings_registry):
    return build_session_service(
        session_repository, event_bus=collector, settings_registry=settings_registry
    )
