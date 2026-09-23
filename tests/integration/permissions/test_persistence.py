"""Integration tests for the permissions persistence (docs/specs/user-roles-permissions.md).

Covers AC-027 (REQ-022): the alembic migration creates the
``roles`` / ``role_permissions`` / ``system_principal_permissions`` tables and
seeds the built-in roles (``admin`` / ``user``, both ``is_builtin=True``) and
the bootstrap system set; the SQLite repositories work on the same file.
Covers AC-028 (REQ-023): the in-memory repositories — the full service API
works without SQLite — and the module singleton (``get_permission_service()``
returns the same instance twice; ``reset_permission_service()`` clears it).

These tests verify externally observable behavior only. The
``backend.permissions`` imports are deferred into the test bodies so the
module collects cleanly before the feature is implemented (RED).
"""

from __future__ import annotations

from pathlib import Path

from backend.usermanagement import SqliteUserRepository, UserCreate, UserManager

# The bootstrap system set (spec D10) — the expected seed of
# ``system_principal_permissions`` after the migration.
_BOOTSTRAP_SYSTEM_PERMISSIONS = frozenset(
    {
        "usermanagement.get_user",
        "usermanagement.verify_password",
        "usermanagement.change_password",
        "settings.register",
        "settings.register_feature",
        "mail.send_email",
        "mail.send_password_reset_email",
        "mail.send_email_verification_email",
        "sessionmanagement.cleanup_expired",
    }
)


def test_in_memory_repos_and_singleton() -> None:
    """AC-028 / REQ-023: the in-memory repositories and the module singleton.

    Given the in-memory repositories, when the full service API is exercised,
    then it works without SQLite; given the singleton, when
    ``get_permission_service()`` is called twice, then the same instance is
    returned; when ``reset_permission_service()`` is called, then the
    singleton is cleared.
    """
    from backend.permissions import (
        MemoryGrantRepository,
        MemoryRoleRepository,
        MemorySystemPrincipalRepository,
        PermissionCatalog,
        PermissionDeniedError,
        PermissionService,
        get_permission_service,
        reset_permission_service,
    )

    repo = SqliteUserRepository("sqlite:///:memory:")
    manager = UserManager(repo)
    user = manager.create_user(
        UserCreate(username="user1", email="user1@example.com", password="correct-horse-1", roles=["user"])
    )
    # A second active admin so ``user`` is never the last active admin —
    # the in-memory/singleton test must not hit the last-admin guard (AC-028).
    manager.create_user(
        UserCreate(username="admin2", email="admin2@example.com", password="correct-horse-1", roles=["admin"])
    )

    catalog = PermissionCatalog()
    catalog.register_feature(
        "mail",
        {
            "mail.send_email": "Send an email via the shared mail service",
            "mail.send_password_reset_email": "Send the built-in password-reset email",
        },
    )

    role_repo = MemoryRoleRepository()
    role_repo.add("admin", None, True)
    role_repo.add("user", None, True)

    service = PermissionService(
        role_repo,
        MemoryGrantRepository(),
        MemorySystemPrincipalRepository(),
        manager,
        catalog=catalog,
    )

    perm = "mail.send_email"

    # The full service API works without SQLite (the in-memory repositories).
    created = service.create_role("editor")
    assert created.role == "editor"
    assert any(role.role == "editor" for role in service.list_roles())
    service.grant_permission("editor", perm)
    assert perm in service.get_role_permissions("editor")
    service.revoke_permission("editor", perm)
    assert perm not in service.get_role_permissions("editor")
    service.delete_role("editor")
    service.set_system_permissions({perm})
    assert service.get_system_permissions() == frozenset({perm})
    assert service.has_permission(user.id, perm) is False
    try:
        service.require_permission(user.id, perm)
        raise AssertionError("expected PermissionDeniedError")
    except PermissionDeniedError:
        pass
    service.assign_role(user.id, "admin")
    assert manager.get_user(user.id).roles == ["admin"]
    service.add_role(user.id, "user")
    service.remove_role(user.id, "admin")
    service.set_roles(user.id, ["user"])
    assert manager.get_user(user.id).roles == ["user"]

    # The singleton returns the same instance twice...
    first = get_permission_service()
    second = get_permission_service()
    assert first is second
    # ...and reset_permission_service clears it.
    reset_permission_service()
    third = get_permission_service()
    assert third is not first


def _alembic_upgrade_head(db_path: Path) -> None:
    """Apply ``alembic upgrade head`` in-process against ``db_path``."""
    from alembic import command
    from alembic.config import Config as AlembicConfig

    root = Path(__file__).resolve().parents[3]
    cfg = AlembicConfig(str(root / "alembic.ini"))
    cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(cfg, "head")


def test_migration_seeds_roles_and_system_set(tmp_path: Path) -> None:
    """AC-027 / REQ-022: the alembic migration seeds the built-in roles and the bootstrap system set.

    Given the alembic migration applied to a fresh database, when the tables
    are inspected, then ``roles`` is seeded with ``admin`` and ``user`` (both
    ``is_builtin=True``), ``system_principal_permissions`` is seeded with the
    bootstrap set, and the SQLite repositories work on the same file.
    """
    import sqlite3

    from backend.permissions import (
        SqliteGrantRepository,
        SqliteRoleRepository,
        SqliteSystemPrincipalRepository,
    )

    db_path = tmp_path / "app.db"
    _alembic_upgrade_head(db_path)

    # The tables are inspected directly in the migrated database file.
    with sqlite3.connect(db_path) as conn:
        tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        assert {"roles", "role_permissions", "system_principal_permissions"} <= tables, (
            f"expected the permissions tables after the migration, got {sorted(tables)}"
        )
        seeded_roles = {row[0]: bool(row[1]) for row in conn.execute("SELECT role, is_builtin FROM roles")}
        assert seeded_roles.get("admin") is True, f"'admin' not seeded as a built-in role: {seeded_roles}"
        assert seeded_roles.get("user") is True, f"'user' not seeded as a built-in role: {seeded_roles}"
        seeded_system = {row[0] for row in conn.execute("SELECT permission FROM system_principal_permissions")}
        assert seeded_system == set(_BOOTSTRAP_SYSTEM_PERMISSIONS), (
            f"system set seed mismatch: {sorted(seeded_system)}"
        )

    # The SQLite repositories work on the same file.
    url = f"sqlite:///{db_path}"

    role_repo = SqliteRoleRepository(url)
    seeded = {role.role: role for role in role_repo.list_all()}
    assert seeded["admin"].is_builtin is True
    assert seeded["user"].is_builtin is True

    system_repo = SqliteSystemPrincipalRepository(url)
    assert system_repo.get_permissions() == _BOOTSTRAP_SYSTEM_PERMISSIONS

    grant_repo = SqliteGrantRepository(url)
    grant_repo.grant("user", "mail.send_email")
    assert "mail.send_email" in grant_repo.get_role_permissions("user")
    grant_repo.revoke("user", "mail.send_email")
    assert "mail.send_email" not in grant_repo.get_role_permissions("user")
