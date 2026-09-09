"""Persistence contract and the SQLite/SQLModel repository (REQ-013).

The :class:`UserRepository` ABC is the only persistence contract the service
sees, so the database can be swapped later (ADR-020).
:class:`SqliteUserRepository` implements the ABC with SQLModel/SQLite:

- the DB file's parent directory is auto-created (EDGE-007);
- all tables are bootstrapped via ``SQLModel.metadata.create_all`` at init
  (no migration framework, D8);
- violated ``uq_users_username`` / ``uq_users_email`` constraints are mapped
  to :class:`UserAlreadyExistsError` with the offending ``field`` (race guard
  for concurrent creates, EDGE-015);
- the repository is safe for concurrent use from multiple threads (NFR-004):
  each operation opens its own session and SQLite busy-timeout serializes
  concurrent writers;
- ``sqlite:///:memory:`` uses a static pool so one instance sees one
  in-memory database, and each instance is isolated (EDGE-008).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from datetime import UTC
from pathlib import Path
from uuid import UUID

from sqlalchemy import func
from sqlalchemy import select as sa_select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

from backend.logging import logged_class
from backend.usermanagement.errors import UserAlreadyExistsError
from backend.usermanagement.models import User

_MEMORY_URL = "sqlite:///:memory:"


def _attach_utc(user: User | None) -> User | None:
    """Attach UTC to naive timestamps (SQLite stores UTC without tzinfo).

    The service contract is tz-aware UTC (REQ-013); SQLite/SQLAlchemy
    materializes naive datetimes, so the repository is the single place
    where the storage representation is reconciled with the contract.
    """
    if user is None:
        return None
    for attr in ("created_at", "updated_at", "deleted_at"):
        value = getattr(user, attr, None)
        if value is not None and value.tzinfo is None:
            setattr(user, attr, value.replace(tzinfo=UTC))
    return user


def _sqlite_file_path(database_url: str) -> str | None:
    """The on-disk file path for a file-based SQLite URL, else ``None``."""
    if database_url == _MEMORY_URL:
        return None
    if database_url.startswith("sqlite:///"):
        return database_url[len("sqlite:///") :]
    return None


@logged_class(slow_threshold_ms=100)
class UserRepository(ABC):
    """The persistence contract the service depends on (REQ-013).

    The ABC is traced via the shared logging feature (``@logged_class``);
    concrete subclasses inherit the tracing.
    """

    @abstractmethod
    def add(self, user: User) -> User:
        """Insert ``user``; raise :class:`UserAlreadyExistsError` on a
        uniqueness-constraint violation (race guard)."""
        ...

    @abstractmethod
    def get_by_id(self, user_id: UUID) -> User | None: ...

    @abstractmethod
    def get_by_username(self, username: str) -> User | None: ...

    @abstractmethod
    def get_by_email(self, email: str) -> User | None: ...

    @abstractmethod
    def update(self, user: User) -> User: ...

    @abstractmethod
    def delete(self, user_id: UUID) -> None: ...

    @abstractmethod
    def list_all(self, include_inactive: bool = False) -> Sequence[User]: ...

    @abstractmethod
    def count_active_by_role(self, role: str) -> int: ...


@logged_class(slow_threshold_ms=100)
class SqliteUserRepository(UserRepository):
    """A SQLite/SQLModel implementation of :class:`UserRepository`.

    The class is traced via the shared logging feature (``@logged_class``).
    """

    def __init__(self, database_url: str) -> None:
        self._database_url = database_url
        file_path = _sqlite_file_path(database_url)
        if file_path is not None:
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        connect_args: dict[str, object] = {"check_same_thread": False}
        if file_path is None:
            # One shared connection: a single in-memory DB per instance.
            self._engine = create_engine(
                database_url,
                connect_args=connect_args,
                poolclass=StaticPool,
            )
        else:
            # Busy timeout serializes concurrent writers (NFR-004).
            connect_args["timeout"] = 30
            self._engine = create_engine(database_url, connect_args=connect_args)
        SQLModel.metadata.create_all(self._engine)

    @staticmethod
    def _map_integrity_error(error: IntegrityError) -> UserAlreadyExistsError:
        detail = str(error.orig) if error.orig is not None else str(error)
        if "uq_users_email" in detail or "users.email" in detail:
            return UserAlreadyExistsError(field="email")
        return UserAlreadyExistsError(field="username")

    def _session(self) -> Session:
        # expire_on_commit=False keeps attributes loaded after commit so
        # detached instances stay readable (the service reads them after add/update).
        return Session(self._engine, expire_on_commit=False)

    def add(self, user: User) -> User:
        try:
            with self._session() as session:
                session.add(user)
                session.commit()
        except IntegrityError as error:
            raise self._map_integrity_error(error) from error
        return user

    def get_by_id(self, user_id: UUID) -> User | None:
        with self._session() as session:
            return _attach_utc(session.get(User, user_id))

    def get_by_username(self, username: str) -> User | None:
        with self._session() as session:
            statement = select(User).where(User.username == username)
            return _attach_utc(session.exec(statement).first())

    def get_by_email(self, email: str) -> User | None:
        with self._session() as session:
            statement = select(User).where(User.email == email.lower())
            return _attach_utc(session.exec(statement).first())

    def update(self, user: User) -> User:
        try:
            with self._session() as session:
                merged = session.merge(user)
                session.commit()
            return merged
        except IntegrityError as error:
            raise self._map_integrity_error(error) from error

    def delete(self, user_id: UUID) -> None:
        with self._session() as session:
            user = session.get(User, user_id)
            if user is not None:
                session.delete(user)
                session.commit()

    def list_all(self, include_inactive: bool = False) -> Sequence[User]:
        with self._session() as session:
            statement = select(User)
            if not include_inactive:
                statement = statement.where(User.is_active == True)  # noqa: E712
            return [_attach_utc(user) for user in session.exec(statement).all()]

    def count_active_by_role(self, role: str) -> int:
        with self._session() as session:
            statement = (
                sa_select(func.count())
                .select_from(User)
                .where(
                    User.role == role,
                    User.is_active == True,  # noqa: E712
                )
            )
            return int(session.scalar(statement))
