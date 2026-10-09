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

from sqlalchemy import Engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.pool import NullPool, StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

from backend.logging import logged_class
from backend.permissions.errors import RoleAlreadyExistsError
from backend.permissions.models import Role, RolePermission, SystemPrincipalPermission

_MEMORY_URL = "sqlite:///:memory:"


def _utcnow() -> datetime:
    """The single timestamp source for the ``created_at`` / ``granted_at`` columns.

    Timestamps are stored timezone-aware UTC and never read back: every listing
    is ordered by name, never by time.
    """
    return datetime.now(UTC)


def _sqlite_file_path(database_url: str) -> str | None:
    """The on-disk file path for a file-based SQLite URL, else ``None``."""
    if database_url == _MEMORY_URL:
        return None
    if database_url.startswith("sqlite:///"):
        return database_url[len("sqlite:///") :]
    return None


def _make_engine(database_url: str) -> Engine:
    """Create the SQLite engine for ``database_url``.

    The parent directory is auto-created; a busy timeout is set for file-based
    URLs; a static pool makes one instance see one ``:memory:`` database; a null
    pool releases a file-based database after each operation.
    """
    file_path = _sqlite_file_path(database_url)
    if file_path is not None:
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
    connect_args: dict[str, object] = {"check_same_thread": False}
    if file_path is None:
        return create_engine(database_url, connect_args=connect_args, poolclass=StaticPool)
    connect_args["timeout"] = 30
    return create_engine(database_url, connect_args=connect_args, poolclass=NullPool)


class _SqliteRepository:
    """Shared engine bootstrap for the SQLite repositories.

    The parent dir is auto-created and the tables are bootstrapped via
    ``SQLModel.metadata.create_all``.
    """

    def __init__(self, database_url: str) -> None:
        """Engine bootstrap shared by the three SQLite repositories.

        ``create_all`` runs on every construction and is idempotent, so the
        repositories work on a fresh file without a migration; the alembic
        migration is what seeds the built-in roles and the bootstrap system
        set (REQ-022, AC-027).
        """
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
        """Insert the role row, translating the primary-key violation into :class:`RoleAlreadyExistsError`.

        ``created_at`` is stamped here, not by the caller, and a rejected
        insert is rolled back so the existing row stays untouched.
        """
        with Session(self._engine) as session:
            try:
                session.add(Role(role=role, description=description, is_builtin=is_builtin, created_at=_utcnow()))
                session.commit()
            except IntegrityError as error:
                session.rollback()
                raise RoleAlreadyExistsError(role) from error

    def get(self, role: str) -> Role | None:
        """Read one role in its own session; a missing role is ``None``, never an error."""
        with Session(self._engine) as session:
            return session.exec(select(Role).where(Role.role == role)).first()

    def list_all(self) -> Sequence[Role]:
        """Every role row, ordered by role name (not by creation time)."""
        with Session(self._engine) as session:
            return session.exec(select(Role).order_by(Role.role)).all()

    def delete(self, role: str) -> None:
        """Delete the role and its grant rows in one session.

        The grant rows go first so no FK is left dangling; an unknown role is a
        silent no-op here — the service raises :class:`RoleNotFoundError` before
        calling (REQ-007).
        """
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
        """Insert the grant row only when it is absent, so a repeat grant keeps the original ``granted_at``."""
        with Session(self._engine) as session:
            if self._find_grant(session, role, permission) is None:
                session.add(RolePermission(role=role, permission=permission, granted_at=_utcnow()))
                session.commit()

    def revoke(self, role: str, permission: str) -> None:
        """Delete the grant row when present; an absent grant is a no-op (REQ-008)."""
        with Session(self._engine) as session:
            existing = self._find_grant(session, role, permission)
            if existing is not None:
                session.delete(existing)
                session.commit()

    def get_role_permissions(self, role: str) -> frozenset[str]:
        """The role's explicit grant keys.

        A role with no grants and a role that does not exist are
        indistinguishable here (both empty) — the service checks role existence
        separately (REQ-008).
        """
        with Session(self._engine) as session:
            rows = session.exec(select(RolePermission).where(RolePermission.role == role)).all()
            return frozenset(row.permission for row in rows)

    def list_all(self) -> Sequence[RolePermission]:
        """Every grant row, ordered by ``(role, permission)``."""
        with Session(self._engine) as session:
            return session.exec(select(RolePermission).order_by(RolePermission.role, RolePermission.permission)).all()


class SqliteSystemPrincipalRepository(_SqliteRepository, SystemPrincipalRepository):
    """A SQLite/SQLModel implementation of :class:`SystemPrincipalRepository`."""

    def set_permissions(self, permissions: Iterable[str]) -> None:
        """Replace the whole system set inside one session, so no reader sees a half-written set (REQ-018).

        Keys are validated in the service before this call, so an unknown key
        never reaches the table (EDGE-020).
        """
        # Atomic replace within one session (all-or-nothing).
        with Session(self._engine) as session:
            rows = session.exec(select(SystemPrincipalPermission)).all()
            for row in rows:
                session.delete(row)
            for permission in permissions:
                session.add(SystemPrincipalPermission(permission=permission, granted_at=_utcnow()))
            session.commit()

    def get_permissions(self) -> frozenset[str]:
        """Full table read on every call — the system set is live, never cached (REQ-018)."""
        with Session(self._engine) as session:
            rows = session.exec(select(SystemPrincipalPermission)).all()
            return frozenset(row.permission for row in rows)


class MemoryRoleRepository(RoleRepository):
    """An in-memory implementation (tests/DI); instances are isolated."""

    def __init__(self) -> None:
        """A fresh store: no roles, and no state shared with any other instance."""
        self._roles: dict[str, Role] = {}

    def add(self, role: str, description: str | None, is_builtin: bool) -> None:
        """Dict membership is the in-memory stand-in for the SQLite primary key (same error)."""
        if role in self._roles:
            raise RoleAlreadyExistsError(role)
        self._roles[role] = Role(role=role, description=description, is_builtin=is_builtin, created_at=_utcnow())

    def get(self, role: str) -> Role | None:
        """Direct dict lookup; a missing role is ``None``."""
        return self._roles.get(role)

    def list_all(self) -> Sequence[Role]:
        """Sorted by role name, matching the SQLite repository's ordering."""
        return [self._roles[key] for key in sorted(self._roles)]

    def delete(self, role: str) -> None:
        """Silent no-op for an unknown role (``pop`` with a default)."""
        self._roles.pop(role, None)


class MemoryGrantRepository(GrantRepository):
    """An in-memory implementation (tests/DI); instances are isolated."""

    def __init__(self) -> None:
        """A fresh store keyed by the ``(role, permission)`` pair — one row per pair."""
        self._grants: dict[tuple[str, str], RolePermission] = {}

    def grant(self, role: str, permission: str) -> None:
        """Insert-only: an existing grant is left untouched (idempotent, REQ-008)."""
        key = (role, permission)
        if key not in self._grants:
            self._grants[key] = RolePermission(role=role, permission=permission, granted_at=_utcnow())

    def revoke(self, role: str, permission: str) -> None:
        """Drop the pair when present; an absent grant is ignored."""
        self._grants.pop((role, permission), None)

    def get_role_permissions(self, role: str) -> frozenset[str]:
        """Linear scan over the grant keys — fine at the fixture sizes this store is built for."""
        return frozenset(permission for (grant_role, permission) in self._grants if grant_role == role)

    def list_all(self) -> Sequence[RolePermission]:
        """Grant rows ordered by their ``(role, permission)`` key, as the SQLite listing is."""
        return [self._grants[key] for key in sorted(self._grants)]


class MemorySystemPrincipalRepository(SystemPrincipalRepository):
    """An in-memory implementation (tests/DI); instances are isolated."""

    def __init__(self) -> None:
        """A fresh store, empty — the bootstrap system set is seeded by the migration, not here (REQ-022)."""
        self._permissions: dict[str, SystemPrincipalPermission] = {}

    def set_permissions(self, permissions: Iterable[str]) -> None:
        """Rebuild the whole mapping (a replacement, not a merge): keys not listed are dropped."""
        self._permissions = {
            permission: SystemPrincipalPermission(permission=permission, granted_at=_utcnow())
            for permission in permissions
        }

    def get_permissions(self) -> frozenset[str]:
        """Snapshot copy: mutating the returned set cannot change the store."""
        return frozenset(self._permissions)
