"""Acceptance tests for the permissions role management (docs/specs/user-roles-permissions.md).

Covers role CRUD (``create_role`` / ``list_roles`` / ``delete_role``), the role
deletion guards (built-in roles protected, a role assigned to a user in use, an
unknown role), and the dynamic role→permission grants (``grant_permission`` /
``revoke_permission`` / ``get_role_permissions``), including the feature-wildcard
grant stored and matched on the check.

These tests verify externally observable behavior only. The ``backend.permissions``
imports are deferred into the test bodies so the module collects cleanly before the
feature is implemented (RED).
"""

from __future__ import annotations

from backend.usermanagement import SqliteUserRepository, UserCreate, UserManager


def _build(
    service_cls,
    role_repo_cls,
    grant_repo_cls,
    system_repo_cls,
    catalog_cls,
    *,
    user_roles=None,
    username="user1",
    role_store=None,
    seed_roles=(),
):
    """Construct a ``PermissionService`` over in-memory repositories for the role management tests.

    Returns ``(service, manager, user, role_repo)``. ``user_roles`` of ``None`` creates
    no user; ``seed_roles`` is an iterable of ``(role, is_builtin)`` pairs added to the
    role repository before the service is constructed (the built-in roles are seeded
    by the migration in production); ``role_store`` overrides the user manager's role
    store (needed when the user holds a non-built-in role).
    """
    repo = SqliteUserRepository("sqlite:///:memory:")
    manager = UserManager(repo) if role_store is None else UserManager(repo, role_store=role_store)
    user = None
    if user_roles is not None:
        user = manager.create_user(
            UserCreate(username=username, email=f"{username}@example.com", password="correct-horse-1", roles=user_roles)
        )

    catalog = catalog_cls()
    catalog.register_feature(
        "usermanagement",
        {
            "usermanagement.get_user": "Read a user by id",
            "usermanagement.delete_user": "Delete a user account",
        },
    )
    catalog.register_feature("mail", {"mail.send_email": "Send an email"})

    role_repo = role_repo_cls()
    for role, is_builtin in seed_roles:
        role_repo.add(role, None, is_builtin)

    service = service_cls(
        role_repo,
        grant_repo_cls(),
        system_repo_cls(),
        manager,
        catalog=catalog,
    )
    return service, manager, user, role_repo


# --- AC-007: create_role returns a RoleRead and list_roles includes it ---


def test_create_role_and_list() -> None:
    """AC-007 / REQ-006: create_role returns a RoleRead and list_roles includes it.

    Given the role store, when ``create_role("editor", description="Content
    editor")`` is called, then a ``RoleRead`` with ``role="editor"``,
    ``is_builtin=False`` is returned; when ``list_roles()`` is called, then
    ``editor`` is present.
    """
    from backend.permissions import (
        MemoryGrantRepository,
        MemoryRoleRepository,
        MemorySystemPrincipalRepository,
        PermissionCatalog,
        PermissionService,
    )

    service, _, _, _ = _build(
        PermissionService,
        MemoryRoleRepository,
        MemoryGrantRepository,
        MemorySystemPrincipalRepository,
        PermissionCatalog,
    )

    created = service.create_role("editor", description="Content editor")
    assert created.role == "editor"
    assert created.description == "Content editor"
    assert created.is_builtin is False

    listed = service.list_roles()
    assert any(role.role == "editor" for role in listed)


# --- AC-008: the role deletion guards ---


def test_delete_role_guards() -> None:
    """AC-008 / REQ-007: the role deletion guards.

    Given the built-in role ``admin``, when ``delete_role("admin")`` is called,
    then a ``RoleProtectedError`` is raised; given a role assigned to a user, when
    ``delete_role`` is called, then a ``RoleInUseError`` is raised; given an unknown
    role, when ``delete_role`` is called, then a ``RoleNotFoundError`` is raised.
    """
    from backend.permissions import (
        MemoryGrantRepository,
        MemoryRoleRepository,
        MemorySystemPrincipalRepository,
        PermissionCatalog,
        PermissionService,
        RoleInUseError,
        RoleNotFoundError,
        RoleProtectedError,
    )
    from backend.usermanagement import StaticRoleStore

    service, _, _, _ = _build(
        PermissionService,
        MemoryRoleRepository,
        MemoryGrantRepository,
        MemorySystemPrincipalRepository,
        PermissionCatalog,
        user_roles=["editor"],
        role_store=StaticRoleStore(("admin", "user", "editor")),
        seed_roles=[("admin", True), ("user", True), ("editor", False)],
    )

    # Built-in role -> RoleProtectedError.
    try:
        service.delete_role("admin")
        raise AssertionError("expected RoleProtectedError")
    except RoleProtectedError as exc:
        assert exc.role == "admin"

    # A role assigned to a user -> RoleInUseError.
    try:
        service.delete_role("editor")
        raise AssertionError("expected RoleInUseError")
    except RoleInUseError as exc:
        assert exc.role == "editor"

    # An unknown role -> RoleNotFoundError.
    try:
        service.delete_role("ghost")
        raise AssertionError("expected RoleNotFoundError")
    except RoleNotFoundError as exc:
        assert exc.role == "ghost"


# --- AC-009: grant and revoke a role permission ---


def test_grant_and_revoke_role_permission() -> None:
    """AC-009 / REQ-008: grant and revoke a role permission.

    Given the role ``user``, when ``grant_permission("user",
    "usermanagement.get_user")`` is called, then ``get_role_permissions("user")``
    contains it; when ``revoke_permission("user", "usermanagement.get_user")`` is
    called, then it no longer contains it.
    """
    from backend.permissions import (
        MemoryGrantRepository,
        MemoryRoleRepository,
        MemorySystemPrincipalRepository,
        PermissionCatalog,
        PermissionService,
    )

    service, _, _, _ = _build(
        PermissionService,
        MemoryRoleRepository,
        MemoryGrantRepository,
        MemorySystemPrincipalRepository,
        PermissionCatalog,
        seed_roles=[("user", True)],
    )

    perm = "usermanagement.get_user"
    service.grant_permission("user", perm)
    assert perm in service.get_role_permissions("user")

    service.revoke_permission("user", perm)
    assert perm not in service.get_role_permissions("user")


# --- AC-010: a wildcard grant is stored and matches on the check ---


def test_wildcard_grant_stored_and_matches() -> None:
    """AC-010 / REQ-008: a wildcard grant is stored and matches on the check.

    Given the role ``user``, when ``grant_permission("user", "mail.*")`` is called,
    then the wildcard grant is stored; when ``has_permission(user_id,
    "mail.send_email")`` is called for a holder of that role, then ``True`` is
    returned.
    """
    from backend.permissions import (
        MemoryGrantRepository,
        MemoryRoleRepository,
        MemorySystemPrincipalRepository,
        PermissionCatalog,
        PermissionService,
    )

    service, _, user, _ = _build(
        PermissionService,
        MemoryRoleRepository,
        MemoryGrantRepository,
        MemorySystemPrincipalRepository,
        PermissionCatalog,
        user_roles=["user"],
        seed_roles=[("user", True)],
    )

    service.grant_permission("user", "mail.*")
    # The wildcard grant is stored.
    assert "mail.*" in service.get_role_permissions("user")
    # It matches the mail actions on the check.
    assert service.has_permission(user.id, "mail.send_email") is True
