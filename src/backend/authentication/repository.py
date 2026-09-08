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

_MEMORY_URL = "sqlite:///:memory:"


def _attach_utc(obj: Session | PasswordReset | WebAuthnCredential | None):
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


class SqliteSessionRepository(SessionRepository):
    """A SQLite/SQLModel implementation of :class:`SessionRepository`."""

    def __init__(self, database_url: str) -> None:
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
        return SModelSession(self._engine, expire_on_commit=False)

    def add(self, session: Session) -> Session:
        with self._session() as s:
            s.add(session)
            s.commit()
        return session

    def get_by_token_hash(self, token_hash: str) -> Session | None:
        with self._session() as s:
            statement = select(Session).where(Session.token_hash == token_hash)
            return _attach_utc(s.exec(statement).first())

    def revoke(self, session_id: UUID) -> None:
        with self._session() as s:
            row = s.get(Session, session_id)
            if row is not None and not row.revoked:
                row.revoked = True
                s.add(row)
                s.commit()

    def revoke_all_for_user(self, user_id: UUID) -> None:
        with self._session() as s:
            statement = select(Session).where(Session.user_id == user_id)
            for row in s.exec(statement).all():
                if not row.revoked:
                    row.revoked = True
                    s.add(row)
            s.commit()

    def delete_expired(self) -> int:
        now = datetime.now(UTC)
        with self._session() as s:
            statement = select(Session).where(Session.expires_at <= now)
            rows = list(s.exec(statement).all())
            for row in rows:
                s.delete(row)
            s.commit()
        return len(rows)


class SqlitePasswordResetRepository(PasswordResetRepository):
    """A SQLite/SQLModel implementation of :class:`PasswordResetRepository`."""

    def __init__(self, database_url: str) -> None:
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
        return SModelSession(self._engine, expire_on_commit=False)

    def add(self, reset: PasswordReset) -> PasswordReset:
        with self._session() as s:
            s.add(reset)
            s.commit()
        return reset

    def get_by_token_hash(self, token_hash: str) -> PasswordReset | None:
        with self._session() as s:
            statement = select(PasswordReset).where(PasswordReset.token_hash == token_hash)
            return _attach_utc(s.exec(statement).first())

    def invalidate_all_for_user(self, user_id: UUID) -> None:
        with self._session() as s:
            statement = select(PasswordReset).where(PasswordReset.user_id == user_id)
            for row in s.exec(statement).all():
                if not row.used:
                    row.used = True
                    s.add(row)
            s.commit()

    def mark_used(self, reset_id: UUID) -> None:
        with self._session() as s:
            row = s.get(PasswordReset, reset_id)
            if row is not None and not row.used:
                row.used = True
                s.add(row)
                s.commit()


class SqliteWebAuthnCredentialRepository(WebAuthnCredentialRepository):
    """A SQLite/SQLModel implementation of :class:`WebAuthnCredentialRepository`."""

    def __init__(self, database_url: str) -> None:
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
        return SModelSession(self._engine, expire_on_commit=False)

    def add(self, credential: WebAuthnCredential) -> WebAuthnCredential:
        with self._session() as s:
            s.add(credential)
            s.commit()
        return credential

    def get_by_credential_id(self, credential_id: str) -> WebAuthnCredential | None:
        with self._session() as s:
            statement = select(WebAuthnCredential).where(WebAuthnCredential.credential_id == credential_id)
            return _attach_utc(s.exec(statement).first())

    def list_for_user(self, user_id: UUID) -> list[WebAuthnCredential]:
        with self._session() as s:
            statement = select(WebAuthnCredential).where(WebAuthnCredential.user_id == user_id)
            return [_attach_utc(c) for c in s.exec(statement).all()]

    def update_sign_count(self, credential_id: str, sign_count: int) -> None:
        with self._session() as s:
            row = s.exec(select(WebAuthnCredential).where(WebAuthnCredential.credential_id == credential_id)).first()
            if row is not None:
                row.sign_count = sign_count
                s.add(row)
                s.commit()

    def delete(self, credential_id: str) -> None:
        with self._session() as s:
            row = s.exec(select(WebAuthnCredential).where(WebAuthnCredential.credential_id == credential_id)).first()
            if row is not None:
                s.delete(row)
                s.commit()
