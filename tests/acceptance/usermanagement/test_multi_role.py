"""Acceptance tests for the user-management multi-role amendment (docs/specs/user-roles-permissions.md).

Covers AC-033 .. AC-037 (REQ-013, REQ-026): ``UserCreate.roles`` / ``UserRead.roles``
as non-empty lists, role existence validated against the injected ``RoleStore``, the new
assignment methods ``set_roles`` / ``add_role`` / ``remove_role`` (with ``set_role``
preserved as ``set_roles([role])``), the last-admin guard on every assignment path, the
``member`` -> ``user`` rename, and the alembic data migration.

These tests verify externally observable behavior only.
"""

from __future__ import annotations

import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

import pytest
from usermanagement_test_helpers import EventCollector, db_url, valid_create

from backend.usermanagement import (
    InvalidRoleError,
    LastAdminError,
    SqliteUserRepository,
    UserCreate,
    UserCreated,
    UserManager,
    UserRead,
    UserRoleChanged,
)

# The repository root (the worktree root), so the alembic scaffold is located
# relative to the test file rather than the current working directory.
_REPO_ROOT = Path(__file__).resolve().parents[3]

# The number of users seeded by ``_seed_pre_amendment_db`` (AC-035).
_SEEDED_USER_COUNT = 3


@pytest.fixture
def collector() -> EventCollector:
    return EventCollector()


@pytest.fixture
def repo(tmp_path: Path) -> SqliteUserRepository:
    return SqliteUserRepository(db_url(tmp_path))


@pytest.fixture
def manager(repo: SqliteUserRepository, collector: EventCollector) -> UserManager:
    return UserManager(repo, event_bus=collector)


def _create_fields(**overrides: Any) -> dict[str, Any]:
    """A valid create field mapping for the amended schema.

    The amendment replaces the single ``role`` field with a ``roles`` list, so the
    shared helper's ``role`` key is dropped here; ``roles`` is passed explicitly by
    the caller.
    """
    fields = valid_create(**overrides)
    fields.pop("role")
    return fields


# --- AC-033: create_user with a roles list ---


def test_create_user_with_roles_list(manager: UserManager) -> None:
    """AC-033 / REQ-026: ``create_user`` accepts ``roles`` (a list); unknown roles are rejected.

    Given the amended ``UserManager``, when ``create_user`` is called with
    ``roles=["admin", "user"]``, then a ``UserRead`` with ``roles=["admin", "user"]`` is
    returned. When ``create_user`` is called with ``roles=["nonexistent"]``, then an
    ``InvalidRoleError`` is raised.
    """
    created = manager.create_user(
        UserCreate(roles=["admin", "user"], **_create_fields(username="multi1", email="multi1@example.com"))
    )
    assert isinstance(created, UserRead)
    assert created.roles == ["admin", "user"]
    assert manager.get_user(created.id).roles == ["admin", "user"]

    with pytest.raises(InvalidRoleError):
        manager.create_user(
            UserCreate(roles=["nonexistent"], **_create_fields(username="multi2", email="multi2@example.com"))
        )


# --- AC-034: add_role / remove_role / set_role on the roles list ---


def test_add_remove_set_roles(manager: UserManager) -> None:
    """AC-034 / REQ-026: ``add_role`` / ``remove_role`` / ``set_role`` operate on the roles list.

    Given a user with ``roles=["user"]``, when ``add_role(u, "admin")`` is called, then
    ``roles=["user", "admin"]`` is returned; when ``remove_role(u, "user")`` is called,
    then ``roles=["admin"]`` is returned; when ``set_role(u, "user")`` is called, then
    ``roles=["user"]`` is returned (replaced).
    """
    created = manager.create_user(UserCreate(roles=["user"], **_create_fields(username="ar1", email="ar1@example.com")))
    assert created.roles == ["user"]

    added = manager.add_role(created.id, "admin")
    assert added.roles == ["user", "admin"]

    removed = manager.remove_role(created.id, "user")
    assert removed.roles == ["admin"]

    replaced = manager.set_role(created.id, "user")
    assert replaced.roles == ["user"]


# --- AC-035: the alembic data migration ---


# The exact pre-amendment ``users`` table DDL (single ``role`` column) as produced by
# the ORM before the amendment. The migration test seeds this schema so the data
# migration has something to rewrite.
_PRE_AMENDMENT_USERS_DDL = """
CREATE TABLE users (
    id CHAR(32) NOT NULL,
    username VARCHAR NOT NULL,
    email VARCHAR NOT NULL,
    display_name VARCHAR,
    role VARCHAR NOT NULL,
    password_hash VARCHAR NOT NULL,
    profile_picture_url VARCHAR,
    is_active BOOLEAN NOT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    PRIMARY KEY (id),
    CONSTRAINT uq_users_username UNIQUE (username),
    CONSTRAINT uq_users_email UNIQUE (email)
)
"""


def _seed_pre_amendment_db(db_file: Path) -> None:
    """Create the pre-amendment ``users`` table and seed users (AC-035).

    Seeds two ``member`` users (one active, one inactive) and one ``admin`` user so the
    migration's role-value rewrite (``member`` -> ``user``) and column conversion
    (single role -> role list) are both exercised, and "all users are readable" covers
    an inactive user too.
    """
    con = sqlite3.connect(db_file)
    try:
        con.execute(_PRE_AMENDMENT_USERS_DDL)
        now = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S.%f")
        seeded = [
            ("member1", "member1@example.com", "member", 1),
            ("admin1", "admin1@example.com", "admin", 1),
            ("member2", "member2@example.com", "member", 0),
        ]
        for username, email, role, is_active in seeded:
            con.execute(
                "INSERT INTO users (id, username, email, display_name, role, "
                "password_hash, profile_picture_url, is_active, created_at, updated_at) "
                "VALUES (?, ?, ?, NULL, ?, '$argon2id$placeholder', NULL, ?, ?, ?)",
                (uuid4().hex, username, email, role, is_active, now, now),
            )
        con.commit()
    finally:
        con.close()


def _apply_migrations(db_file: Path) -> None:
    """Apply the alembic migrations to the database (AC-035).

    Runs the scaffold's migrations in-process against the seeded database, mirroring
    the CI gate (``uv run alembic upgrade head``) but pointed at the test database.
    """
    from alembic import command
    from alembic.config import Config

    p = str(db_file).replace("\\", "/")
    prefix = "sqlite:////" if p.startswith("/") else "sqlite:///"
    url = f"{prefix}{p}"
    cfg = Config()
    cfg.set_main_option("script_location", str(_REPO_ROOT / "migrations"))
    cfg.set_main_option("sqlalchemy.url", url)
    command.upgrade(cfg, "head")


def test_migration_member_to_user_and_role_list(tmp_path: Path) -> None:
    """AC-035 / REQ-026: the data migration rewrites ``member`` -> ``user`` and converts role to a list.

    Given an existing user-management database, when the migration is applied, then role
    values ``member`` become ``user``, the single role column becomes a role list, and
    all users are readable.
    """
    db_file = tmp_path / "users.db"
    _seed_pre_amendment_db(db_file)
    _apply_migrations(db_file)

    repo = SqliteUserRepository(db_url(tmp_path))
    manager = UserManager(repo)
    users = manager.list_users(include_inactive=True)
    by_username = {u.username: u for u in users}

    # All users are readable (including the inactive one).
    assert len(by_username) == _SEEDED_USER_COUNT
    # Role values ``member`` become ``user``; the single role column becomes a role list.
    assert by_username["member1"].roles == ["user"]
    assert by_username["admin1"].roles == ["admin"]
    assert by_username["member2"].roles == ["user"]


# --- AC-036: the last-admin guard on every assignment path ---


def test_last_admin_guard_all_paths(manager: UserManager) -> None:
    """AC-036 / REQ-013, REQ-026: the last-admin guard fires on every assignment path.

    Given the last active admin with ``roles=["admin", "user"]``, when ``remove_role`` /
    ``set_roles`` / ``set_role`` / ``deactivate_user`` / ``delete_user`` are called, then
    a ``LastAdminError`` is raised (no bypass). The guard is scoped to the *last* active
    admin: demoting one of two active admins is allowed.
    """
    admin = manager.create_user(
        UserCreate(roles=["admin", "user"], **_create_fields(username="root1", email="root1@example.com"))
    )

    with pytest.raises(LastAdminError):
        manager.remove_role(admin.id, "admin")
    with pytest.raises(LastAdminError):
        manager.set_roles(admin.id, ["user"])
    with pytest.raises(LastAdminError):
        manager.set_role(admin.id, "user")
    with pytest.raises(LastAdminError):
        manager.deactivate_user(admin.id)
    with pytest.raises(LastAdminError):
        manager.delete_user(admin.id)

    # The last admin is still intact after all the rejected operations.
    assert manager.get_user(admin.id).roles == ["admin", "user"]
    assert manager.get_user(admin.id).is_active is True

    # Positive control: the guard is scoped to the *last* active admin — once a second
    # active admin exists, demoting the first is allowed (no over-broad guard).
    manager.create_user(
        UserCreate(roles=["admin", "user"], **_create_fields(username="root2", email="root2@example.com"))
    )
    demoted = manager.remove_role(admin.id, "admin")
    assert demoted.roles == ["user"]


# --- AC-037: events carry role lists ---


def test_role_events_carry_lists(manager: UserManager, collector: EventCollector) -> None:
    """AC-037 / REQ-026: events carry role lists.

    Given a successful ``set_roles``, when the event is inspected, then a
    ``UserRoleChanged`` event is published with ``old_roles`` and ``new_roles`` as
    lists. Given a successful ``create_user``, then a ``UserCreated`` event is published
    with ``roles`` as a list.
    """
    created = manager.create_user(UserCreate(roles=["user"], **_create_fields(username="ev1", email="ev1@example.com")))
    created_events = collector.of_type(UserCreated)
    assert len(created_events) == 1
    assert isinstance(created_events[0].roles, list)
    assert created_events[0].roles == ["user"]

    manager.set_roles(created.id, ["admin", "user"])
    changed_events = collector.of_type(UserRoleChanged)
    assert len(changed_events) == 1
    assert isinstance(changed_events[0].old_roles, list)
    assert isinstance(changed_events[0].new_roles, list)
    assert changed_events[0].old_roles == ["user"]
    assert changed_events[0].new_roles == ["admin", "user"]
