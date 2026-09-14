"""Persistence contract and the SQLite/SQLModel repository (REQ-013).

The :class:`FileRepository` ABC is the only persistence contract the service
sees, so the database can be swapped later (ADR-051).
:class:`SqliteFileRepository` implements the ABC with SQLModel/SQLite:

- the DB file's parent directory is auto-created (EDGE-015);
- all tables are bootstrapped via ``SQLModel.metadata.create_all`` at init
  (no migration framework);
- ``add`` is an atomic same-key replacement: an existing record with the same
  key is deleted and the new record inserted in one transaction
  (last-write-wins, D5, ADR-054);
- the repository is safe for concurrent use from multiple threads (NFR-004):
  each operation opens its own session and the SQLite busy-timeout serializes
  concurrent writers;
- ``sqlite:///:memory:`` uses a static pool so one instance sees one
  in-memory database.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

from backend.filemanagement.models import FileRecord, UserAvatar
from backend.logging import logged_class

_MEMORY_URL = "sqlite:///:memory:"


def _attach_utc(record: FileRecord | None) -> FileRecord | None:
    """Attach UTC to naive timestamps (SQLite stores UTC without tzinfo).

    The service contract is tz-aware UTC (REQ-012); SQLite/SQLAlchemy
    materializes naive datetimes, so the repository is the single place
    where the storage representation is reconciled with the contract.
    """
    if record is None:
        return None
    for attr in ("created_at", "updated_at"):
        value = getattr(record, attr, None)
        if value is not None and value.tzinfo is None:
            setattr(record, attr, value.replace(tzinfo=UTC))
    return record


def _sqlite_file_path(database_url: str) -> str | None:
    """The on-disk file path for a file-based SQLite URL, else ``None``."""
    if database_url == _MEMORY_URL:
        return None
    if database_url.startswith("sqlite:///"):
        return database_url[len("sqlite:///") :]
    return None


@logged_class(slow_threshold_ms=100)
class FileRepository(ABC):
    """The persistence contract the service depends on (REQ-013).

    The ABC is traced via the shared logging feature (``@logged_class``);
    concrete subclasses inherit the tracing.
    """

    @abstractmethod
    def add(self, record: FileRecord) -> FileRecord:
        """Insert ``record``; if a record with the same key exists it is
        atomically replaced (last-write-wins, D5) and the replaced record is
        deleted."""
        ...

    @abstractmethod
    def get_by_key(self, key: str) -> FileRecord | None: ...

    @abstractmethod
    def get_by_id(self, file_id: UUID) -> FileRecord | None: ...

    @abstractmethod
    def update(self, record: FileRecord) -> FileRecord: ...

    @abstractmethod
    def delete(self, file_id: UUID) -> None: ...

    @abstractmethod
    def list_by_namespace(
        self,
        namespace: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[FileRecord]:
        """Return records whose namespace starts with ``namespace``
        (None → all), ordered by created_at, with limit/offset pagination."""
        ...

    @abstractmethod
    def set_user_avatar(self, user_id: str, file_id: UUID) -> None: ...

    @abstractmethod
    def get_user_avatar(self, user_id: str) -> UUID | None: ...

    @abstractmethod
    def clear_user_avatar(self, user_id: str) -> None: ...


@logged_class(slow_threshold_ms=100)
class SqliteFileRepository(FileRepository):
    """A SQLite/SQLModel implementation of :class:`FileRepository`.

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

    def _session(self) -> Session:
        # expire_on_commit=False keeps attributes loaded after commit so
        # detached instances stay readable (the service reads them after add/update).
        return Session(self._engine, expire_on_commit=False)

    def add(self, record: FileRecord) -> FileRecord:
        with self._session() as session:
            existing = session.exec(select(FileRecord).where(FileRecord.key == record.key)).first()
            if existing is not None:
                # Atomic same-key replacement (last-write-wins, D5): the
                # replaced record is deleted in the same transaction.
                session.delete(existing)
            session.add(record)
            session.commit()
        return record

    def get_by_key(self, key: str) -> FileRecord | None:
        with self._session() as session:
            return _attach_utc(session.exec(select(FileRecord).where(FileRecord.key == key)).first())

    def get_by_id(self, file_id: UUID) -> FileRecord | None:
        with self._session() as session:
            return _attach_utc(session.get(FileRecord, file_id))

    def update(self, record: FileRecord) -> FileRecord:
        with self._session() as session:
            merged = session.merge(record)
            session.commit()
            return _attach_utc(merged)

    def delete(self, file_id: UUID) -> None:
        with self._session() as session:
            record = session.get(FileRecord, file_id)
            if record is not None:
                session.delete(record)
                session.commit()

    def list_by_namespace(
        self,
        namespace: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[FileRecord]:
        with self._session() as session:
            statement = select(FileRecord)
            if namespace is not None:
                statement = statement.where(FileRecord.namespace.like(f"{namespace}%"))
            # created_at ordering; key breaks ties so pagination is stable.
            statement = statement.order_by(FileRecord.created_at, FileRecord.key)
            rows = session.exec(statement.offset(offset).limit(limit)).all()
            return [_attach_utc(row) for row in rows]

    def set_user_avatar(self, user_id: str, file_id: UUID) -> None:
        with self._session() as session:
            row = session.exec(select(UserAvatar).where(UserAvatar.user_id == user_id)).first()
            if row is None:
                row = UserAvatar(user_id=user_id, file_id=file_id, updated_at=datetime.now(UTC))
                session.add(row)
            else:
                row.file_id = file_id
                row.updated_at = datetime.now(UTC)
            session.commit()

    def get_user_avatar(self, user_id: str) -> UUID | None:
        with self._session() as session:
            row = session.exec(select(UserAvatar).where(UserAvatar.user_id == user_id)).first()
            return row.file_id if row is not None else None

    def clear_user_avatar(self, user_id: str) -> None:
        with self._session() as session:
            row = session.exec(select(UserAvatar).where(UserAvatar.user_id == user_id)).first()
            if row is not None:
                session.delete(row)
                session.commit()
