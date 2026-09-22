"""Integration tests for the permissions persistence (docs/specs/user-roles-permissions.md).

Covers AC-028 (REQ-023): the in-memory repositories — the full service API
works without SQLite — and the module singleton (``get_permission_service()``
returns the same instance twice; ``reset_permission_service()`` clears it).

These tests verify externally observable behavior only. The
``backend.permissions`` imports are deferred into the test bodies so the
module collects cleanly before the feature is implemented (RED).
"""

from __future__ import annotations

from backend.usermanagement import SqliteUserRepository, UserCreate, UserManager


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
        UserCreate(username="u1", email="u1@example.com", password="correct-horse-1", roles=["user"])
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
