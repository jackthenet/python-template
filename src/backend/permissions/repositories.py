"""Persistence contract and concrete repositories (docs/specs/user-roles-permissions.md, REQ-022, REQ-023).

The repository ABCs (``RoleRepository``, ``GrantRepository``,
``SystemPrincipalRepository``) are the only persistence contract the service
sees. Concrete implementations:

- ``SqliteRoleRepository`` / ``SqliteGrantRepository`` /
  ``SqliteSystemPrincipalRepository`` — SQLModel/SQLite: the DB file's parent
  directory is auto-created; all tables are bootstrapped via
  ``SQLModel.metadata.create_all``; each operation opens its own session and
  SQLite busy-timeout serializes concurrent writers (thread-safe, REQ-027);
  ``sqlite:///:memory:`` uses a static pool so one instance sees one
  in-memory database.
- ``MemoryRoleRepository`` / ``MemoryGrantRepository`` /
  ``MemorySystemPrincipalRepository`` — in-memory (tests/DI); instances are
  isolated.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable, Sequence
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy.exc import IntegrityError
from sqlalchemy.pool import NullPool, StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

from backend.logging import logged_class
from backend.permissions.errors import RoleAlreadyExistsError
from backend.permissions.models import Role, RolePermission, SystemPrincipalPermission

_MEMORY_URL = "sqlite:///:memory:"


def _utcnow() -> datetime:
    return datetime.now(UTC)


def _sqlite_file_path(database_url: str) -> str | None:
    """The on-disk file path for a file-based SQLite URL, else ``None``."""
    if database_url == _MEMORY_URL:
        return None
    if database_url.startswith("sqlite:///"):
        return database_url[len("sqlite:///") :]
    return None


def _make_engine(database_url: str):
    """Create the SQLite engine (parent dir auto-created; busy timeout for
    file-based URLs; a static pool for ``:memory:``; a null pool for
    file-based so the file is released after each operation)."""
    file_path = _sqlite_file_path(database_url)
    if file_path is not None:
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
    connect_args: dict[str, object] = {"check_same_thread": False}
    if file_path is None:
        return create_engine(database_url, connect_args=connect_args, poolclass=StaticPool)
    connect_args["timeout"] = 30
    return create_engine(database_url, connect_args=connect_args, poolclass=NullPool)


class _SqliteRepository:
    """Shared engine bootstrap for the SQLite repositories (the parent dir is
    auto-created and the tables are bootstrapped via
    ``SQLModel.metadata.create_all``)."""

    def __init__(self, database_url: str) -> None:
        self._engine = _make_engine(database_url)
        SQLModel.metadata.create_all(self._engine)


@logged_class(slow_threshold_ms=100)
class RoleRepository(ABC):
    """The role persistence contract (REQ-022)."""

    @abstractmethod
    def add(self, role: str, description: str | None, is_builtin: bool) -> None:
        """Insert ``role``; raise :class:`RoleAlreadyExistsError` on a duplicate role."""
        ...

    @abstractmethod
    def get(self, role: str) -> Role | None:
        """Return the role or ``None``."""
        ...

    @abstractmethod
    def list_all(self) -> Sequence[Role]:
        """All roles."""
        ...

    @abstractmethod
    def delete(self, role: str) -> None:
        """Delete the role (and its grants)."""
        ...


@logged_class(slow_threshold_ms=100)
class GrantRepository(ABC):
    """The role->permission grant persistence contract (REQ-022)."""

    @abstractmethod
    def grant(self, role: str, permission: str) -> None:
        """Grant ``permission`` to ``role`` (idempotent)."""
        ...

    @abstractmethod
    def revoke(self, role: str, permission: str) -> None:
        """Revoke ``permission`` from ``role`` (idempotent no-op when absent)."""
        ...

    @abstractmethod
    def get_role_permissions(self, role: str) -> frozenset[str]:
        """The role's explicit grants."""
        ...

    @abstractmethod
    def list_all(self) -> Sequence[RolePermission]:
        """All grants."""
        ...


@logged_class(slow_threshold_ms=100)
class SystemPrincipalRepository(ABC):
    """The system-principal permission persistence contract (REQ-022)."""

    @abstractmethod
    def set_permissions(self, permissions: Iterable[str]) -> None:
        """Atomically replace the system set with ``permissions``."""
        ...

    @abstractmethod
    def get_permissions(self) -> frozenset[str]:
        """The current system set."""
        ...


class SqliteRoleRepository(_SqliteRepository, RoleRepository):
    """A SQLite/SQLModel implementation of :class:`RoleRepository`."""

    def add(self, role: str, description: str | None, is_builtin: bool) -> None:
        with Session(self._engine) as session:
            try:
                session.add(Role(role=role, description=description, is_builtin=is_builtin, created_at=_utcnow()))
                session.commit()
            except IntegrityError as error:
                session.rollback()
                raise RoleAlreadyExistsError(role) from error

    def get(self, role: str) -> Role | None:
        with Session(self._engine) as session:
            return session.exec(select(Role).where(Role.role == role)).first()

    def list_all(self) -> Sequence[Role]:
        with Session(self._engine) as session:
            return session.exec(select(Role).order_by(Role.role)).all()

    def delete(self, role: str) -> None:
        with Session(self._engine) as session:
            grants = session.exec(select(RolePermission).where(RolePermission.role == role)).all()
            for grant in grants:
                session.delete(grant)
            role_obj = session.exec(select(Role).where(Role.role == role)).first()
            if role_obj is not None:
                session.delete(role_obj)
            session.commit()


class SqliteGrantRepository(_SqliteRepository, GrantRepository):
    """A SQLite/SQLModel implementation of :class:`GrantRepository`."""

    def _find_grant(self, session: Session, role: str, permission: str) -> RolePermission | None:
        """The existing grant row for ``(role, permission)``, or ``None``."""
        return session.exec(
            select(RolePermission).where(
                RolePermission.role == role,
                RolePermission.permission == permission,
            )
        ).first()

    def grant(self, role: str, permission: str) -> None:
        with Session(self._engine) as session:
            if self._find_grant(session, role, permission) is None:
                session.add(RolePermission(role=role, permission=permission, granted_at=_utcnow()))
                session.commit()

    def revoke(self, role: str, permission: str) -> None:
        with Session(self._engine) as session:
            existing = self._find_grant(session, role, permission)
            if existing is not None:
                session.delete(existing)
                session.commit()

    def get_role_permissions(self, role: str) -> frozenset[str]:
        with Session(self._engine) as session:
            rows = session.exec(select(RolePermission).where(RolePermission.role == role)).all()
            return frozenset(row.permission for row in rows)

    def list_all(self) -> Sequence[RolePermission]:
        with Session(self._engine) as session:
            return (
                session.exec(select(RolePermission).order_by(RolePermission.role, RolePermission.permission)).all()
            )


class SqliteSystemPrincipalRepository(_SqliteRepository, SystemPrincipalRepository):
    """A SQLite/SQLModel implementation of :class:`SystemPrincipalRepository`."""

    def set_permissions(self, permissions: Iterable[str]) -> None:
        # Atomic replace within one session (all-or-nothing).
        with Session(self._engine) as session:
            rows = session.exec(select(SystemPrincipalPermission)).all()
            for row in rows:
                session.delete(row)
            for permission in permissions:
                session.add(SystemPrincipalPermission(permission=permission, granted_at=_utcnow()))
            session.commit()

    def get_permissions(self) -> frozenset[str]:
        with Session(self._engine) as session:
            rows = session.exec(select(SystemPrincipalPermission)).all()
            return frozenset(row.permission for row in rows)


class MemoryRoleRepository(RoleRepository):
    """An in-memory implementation (tests/DI); instances are isolated."""

    def __init__(self) -> None:
        self._roles: dict[str, Role] = {}

    def add(self, role: str, description: str | None, is_builtin: bool) -> None:
        if role in self._roles:
            raise RoleAlreadyExistsError(role)
        self._roles[role] = Role(role=role, description=description, is_builtin=is_builtin, created_at=_utcnow())

    def get(self, role: str) -> Role | None:
        return self._roles.get(role)

    def list_all(self) -> Sequence[Role]:
        return [self._roles[key] for key in sorted(self._roles)]

    def delete(self, role: str) -> None:
        self._roles.pop(role, None)


class MemoryGrantRepository(GrantRepository):
    """An in-memory implementation (tests/DI); instances are isolated."""

    def __init__(self) -> None:
        self._grants: dict[tuple[str, str], RolePermission] = {}

    def grant(self, role: str, permission: str) -> None:
        key = (role, permission)
        if key not in self._grants:
            self._grants[key] = RolePermission(role=role, permission=permission, granted_at=_utcnow())

    def revoke(self, role: str, permission: str) -> None:
        self._grants.pop((role, permission), None)

    def get_role_permissions(self, role: str) -> frozenset[str]:
        return frozenset(permission for (grant_role, permission) in self._grants if grant_role == role)

    def list_all(self) -> Sequence[RolePermission]:
        return [self._grants[key] for key in sorted(self._grants)]


class MemorySystemPrincipalRepository(SystemPrincipalRepository):
    """An in-memory implementation (tests/DI); instances are isolated."""

    def __init__(self) -> None:
        self._permissions: dict[str, SystemPrincipalPermission] = {}

    def set_permissions(self, permissions: Iterable[str]) -> None:
        self._permissions = {
            permission: SystemPrincipalPermission(permission=permission, granted_at=_utcnow())
            for permission in permissions
        }

    def get_permissions(self) -> frozenset[str]:
        return frozenset(self._permissions)
