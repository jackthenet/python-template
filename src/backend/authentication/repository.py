"""SQLite/SQLModel implementations of the authentication repository ABCs.

Each ``Sqlite*`` repository implements its ABC with SQLModel/SQLite:

- the DB file's parent directory is auto-created;
- all tables are bootstrapped via ``SQLModel.metadata.create_all`` at init
  (shared metadata also covers the user-management tables; no migration
  framework, D8);
- the repository is safe for concurrent use from multiple threads (NFR-005):
  each operation opens its own session and SQLite busy-timeout serializes
  concurrent writers;
- ``sqlite:///:memory:`` uses a static pool so one instance sees one
  in-memory database, and each instance is isolated.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import UUID

from sqlalchemy.pool import StaticPool
from sqlmodel import Session as SModelSession
from sqlmodel import SQLModel, create_engine, select

from backend.authentication.models import PasswordReset, Session, WebAuthnCredential
from backend.authentication.repositories import (
    PasswordResetRepository,
    SessionRepository,
    WebAuthnCredentialRepository,
)
from backend.logging import logged_class

_MEMORY_URL = "sqlite:///:memory:"


# mypy types SQLModel tables as `Any`; a precise union return adds ty diagnostics
# (`list[Session | None]` where callers declare `list[Session]`).
def _attach_utc(obj: Session | PasswordReset | WebAuthnCredential | None) -> Any:
    """Attach UTC to naive timestamps (SQLite stores UTC without tzinfo).

    The service contract is tz-aware UTC; SQLite/SQLAlchemy materializes naive
    datetimes, so the repository is the single place where the storage
    representation is reconciled with the contract.
    """
    if obj is None:
        return None
    for attr in ("created_at", "expires_at"):
        value = getattr(obj, attr, None)
        if value is not None and value.tzinfo is None:
            setattr(obj, attr, value.replace(tzinfo=UTC))
    return obj


def _sqlite_file_path(database_url: str) -> str | None:
    """The on-disk file path for a file-based SQLite URL, else ``None``."""
    if database_url == _MEMORY_URL:
        return None
    if database_url.startswith("sqlite:///"):
        return database_url[len("sqlite:///") :]
    return None


@logged_class(slow_threshold_ms=100, include_args=False)
class SqliteSessionRepository(SessionRepository):
    """A SQLite/SQLModel implementation of :class:`SessionRepository`.

    The class is traced via the shared logging feature (``@logged_class``) with
    ``include_args=False`` so token hashes never appear in log records.
    """

    def __init__(self, database_url: str) -> None:
        """Open the database and bootstrap the shared SQLModel metadata tables.

        A file URL's parent directory is auto-created and its writers get a 30 s
        busy timeout (NFR-005); ``sqlite:///:memory:`` gets a ``StaticPool`` so all
        operations of this instance share one in-memory database.
        """
        self._database_url = database_url
        file_path = _sqlite_file_path(database_url)
        if file_path is not None:
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        connect_args: dict[str, object] = {"check_same_thread": False}
        if file_path is None:
            self._engine = create_engine(database_url, connect_args=connect_args, poolclass=StaticPool)
        else:
            connect_args["timeout"] = 30
            self._engine = create_engine(database_url, connect_args=connect_args)
        SQLModel.metadata.create_all(self._engine)

    def _session(self) -> SModelSession:
        """A fresh SQLAlchemy session, kept readable after commit.

        ``expire_on_commit=False`` is what lets the rows returned by an operation
        still be read once the transaction has closed.
        """
        return SModelSession(self._engine, expire_on_commit=False)

    def add(self, session: Session) -> Session:
        """Insert a session row in its own transaction and return the object given in.

        The stored row holds the token hash, never the raw token (REQ-006).
        """
        with self._session() as s:
            s.add(session)
            s.commit()
        return session

    def get_by_token_hash(self, token_hash: str) -> Session | None:
        """Look a session up by its stored SHA-256 hash, with tz-aware timestamps.

        The caller hashes the raw token (``backend.authentication.tokens``); this
        method never sees or derives a token value.
        """
        with self._session() as s:
            statement = select(Session).where(Session.token_hash == token_hash)
            return _attach_utc(s.exec(statement).first())

    def revoke(self, session_id: UUID) -> None:
        """Set ``revoked`` on one session row; an unknown id or an already revoked row writes nothing."""
        with self._session() as s:
            row = s.get(Session, session_id)
            if row is not None and not row.revoked:
                row.revoked = True
                s.add(row)
                s.commit()

    def revoke_all_for_user(self, user_id: UUID) -> None:
        """Revoke every session of a user (the logout-all side of a completed password reset, REQ-012)."""
        with self._session() as s:
            statement = select(Session).where(Session.user_id == user_id)
            for row in s.exec(statement).all():
                if not row.revoked:
                    row.revoked = True
                    s.add(row)
            s.commit()

    def get(self, session_id: UUID) -> Session | None:
        """Read a row by primary key regardless of revocation or expiry.

        Validity is the service's decision, not the store's (INV-002). Additive
        extension for the session-management feature (REQ-017, ADR-061).
        """
        with self._session() as s:
            return _attach_utc(s.get(Session, session_id))

    def list_for_user(self, user_id: UUID) -> list[Session]:
        """Every row of a user, newest first (``id`` breaks ``created_at`` ties).

        Revoked and expired rows are included — the caller filters. Additive
        extension for the session-management feature (REQ-017, ADR-061).
        """
        with self._session() as s:
            statement = (
                select(Session).where(Session.user_id == user_id).order_by(Session.created_at.desc(), Session.id.desc())
            )
            return [_attach_utc(row) for row in s.exec(statement).all()]

    def revoke_user_sessions(self, user_id: UUID, exclude_session_id: UUID | None = None) -> int:
        """Revoke a user's sessions except ``exclude_session_id`` and report rows actually changed.

        Already revoked rows are skipped, so the count is the number of writes, not
        the number of rows matched (session-management REQ-017, ADR-061).
        """
        with self._session() as s:
            statement = select(Session).where(Session.user_id == user_id)
            count = 0
            for row in s.exec(statement).all():
                if row.id != exclude_session_id and not row.revoked:
                    row.revoked = True
                    s.add(row)
                    count += 1
            s.commit()
        return count

    def delete_expired(self, limit: int | None = None) -> int:
        """Delete past-expiry sessions, oldest expiry first, and report how many.

        ``limit`` caps the batch (``None`` = all, the pre-extension behavior) so a
        cleanup job can drain the table in bounded transactions (REQ-017, ADR-061).
        """
        now = datetime.now(UTC)
        with self._session() as s:
            statement = select(Session).where(Session.expires_at <= now).order_by(Session.expires_at.asc())
            rows = list(s.exec(statement).all())
            if limit is not None:
                rows = rows[:limit]
            for row in rows:
                s.delete(row)
            s.commit()
        return len(rows)

    def list_all(self) -> list[Session]:
        """Every session in the database, newest first, unfiltered by user or state.

        The backing read for the ``sessionmanagement`` search source (search
        REQ-022, ADR-080) — unpaginated by design.
        """
        with self._session() as s:
            statement = select(Session).order_by(Session.created_at.desc(), Session.id.desc())
            return [_attach_utc(row) for row in s.exec(statement).all()]


@logged_class(slow_threshold_ms=100, include_args=False)
class SqlitePasswordResetRepository(PasswordResetRepository):
    """A SQLite/SQLModel implementation of :class:`PasswordResetRepository`.

    The class is traced via the shared logging feature (``@logged_class``) with
    ``include_args=False`` so token hashes never appear in log records.
    """

    def __init__(self, database_url: str) -> None:
        """Open the database and bootstrap the shared SQLModel metadata tables.

        Same engine setup as :class:`SqliteSessionRepository` (auto-created parent
        directory, file busy timeout, ``StaticPool`` for ``:memory:``) — both
        repositories normally point at the same database file.
        """
        self._database_url = database_url
        file_path = _sqlite_file_path(database_url)
        if file_path is not None:
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        connect_args: dict[str, object] = {"check_same_thread": False}
        if file_path is None:
            self._engine = create_engine(database_url, connect_args=connect_args, poolclass=StaticPool)
        else:
            connect_args["timeout"] = 30
            self._engine = create_engine(database_url, connect_args=connect_args)
        SQLModel.metadata.create_all(self._engine)

    def _session(self) -> SModelSession:
        """A fresh SQLAlchemy session per operation (NFR-005 thread safety)."""
        return SModelSession(self._engine, expire_on_commit=False)

    def add(self, reset: PasswordReset) -> PasswordReset:
        """Insert a reset row in its own transaction and return the object given in.

        Only the token hash is stored (REQ-011); the raw token exists solely in the
        caller's return value.
        """
        with self._session() as s:
            s.add(reset)
            s.commit()
        return reset

    def get_by_token_hash(self, token_hash: str) -> PasswordReset | None:
        """Look a reset row up by its stored hash, with tz-aware timestamps.

        Expired and used rows are returned too — the service maps them to the three
        ``InvalidResetTokenError`` reasons (REQ-013).
        """
        with self._session() as s:
            statement = select(PasswordReset).where(PasswordReset.token_hash == token_hash)
            return _attach_utc(s.exec(statement).first())

    def invalidate_all_for_user(self, user_id: UUID) -> None:
        """Mark every pending reset row of a user used, so an older token cannot be spent after a new request (REQ-011, EDGE-011)."""
        with self._session() as s:
            statement = select(PasswordReset).where(PasswordReset.user_id == user_id)
            for row in s.exec(statement).all():
                if not row.used:
                    row.used = True
                    s.add(row)
            s.commit()

    def mark_used(self, reset_id: UUID) -> None:
        """Consume one reset row (single-use, INV-003); an unknown or already used id writes nothing."""
        with self._session() as s:
            row = s.get(PasswordReset, reset_id)
            if row is not None and not row.used:
                row.used = True
                s.add(row)
                s.commit()


@logged_class(slow_threshold_ms=100)
class SqliteWebAuthnCredentialRepository(WebAuthnCredentialRepository):
    """A SQLite/SQLModel implementation of :class:`WebAuthnCredentialRepository`.

    The class is traced via the shared logging feature (``@logged_class``).
    """

    def __init__(self, database_url: str) -> None:
        """Open the database and bootstrap the shared SQLModel metadata tables.

        Same engine setup as the other two repositories; tracing keeps its arguments
        visible here because the constructor takes only a database URL.
        """
        self._database_url = database_url
        file_path = _sqlite_file_path(database_url)
        if file_path is not None:
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        connect_args: dict[str, object] = {"check_same_thread": False}
        if file_path is None:
            self._engine = create_engine(database_url, connect_args=connect_args, poolclass=StaticPool)
        else:
            connect_args["timeout"] = 30
            self._engine = create_engine(database_url, connect_args=connect_args)
        SQLModel.metadata.create_all(self._engine)

    def _session(self) -> SModelSession:
        """A fresh SQLAlchemy session per operation (NFR-005 thread safety)."""
        return SModelSession(self._engine, expire_on_commit=False)

    def add(self, credential: WebAuthnCredential) -> WebAuthnCredential:
        """Insert a credential row in its own transaction and return the object given in.

        ``transports`` is stored as the JSON text the service encoded.
        """
        with self._session() as s:
            s.add(credential)
            s.commit()
        return credential

    def get_by_credential_id(self, credential_id: str) -> WebAuthnCredential | None:
        """Look a credential up by the id the browser presents (the assertion's own identity, not the user's)."""
        with self._session() as s:
            statement = select(WebAuthnCredential).where(WebAuthnCredential.credential_id == credential_id)
            return _attach_utc(s.exec(statement).first())

    def list_for_user(self, user_id: UUID) -> list[WebAuthnCredential]:
        """All credentials of a user in storage order (no ``order_by`` — the service does not promise one)."""
        with self._session() as s:
            statement = select(WebAuthnCredential).where(WebAuthnCredential.user_id == user_id)
            return [_attach_utc(c) for c in s.exec(statement).all()]

    def update_sign_count(self, credential_id: str, sign_count: int) -> None:
        """Store the counter an assertion presented, the basis for hijack detection (REQ-015/REQ-016).

        An unknown credential id is silently ignored — the service has already read
        the row in the same operation.
        """
        with self._session() as s:
            row = s.exec(select(WebAuthnCredential).where(WebAuthnCredential.credential_id == credential_id)).first()
            if row is not None:
                row.sign_count = sign_count
                s.add(row)
                s.commit()

    def delete(self, credential_id: str) -> None:
        """Delete a credential row; an unknown id is a no-op (the service checks ownership first, REQ-017)."""
        with self._session() as s:
            row = s.exec(select(WebAuthnCredential).where(WebAuthnCredential.credential_id == credential_id)).first()
            if row is not None:
                s.delete(row)
                s.commit()
