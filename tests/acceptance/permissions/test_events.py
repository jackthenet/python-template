"""Acceptance tests for the permissions lifecycle events (docs/specs/user-roles-permissions.md).

Covers AC-024 (REQ-020): a collecting publisher receives ``PermissionDenied``
on a denial, ``RoleCreated`` / ``RoleDeleted`` / ``RolePermissionsChanged`` on
the successful role operations, and no permission-feature event on an
assignment pass-through (the assignment event is user-management's
``UserRoleChanged``); and AC-025 (REQ-020): a service without a publisher
works normally (no events, no errors).

These tests verify externally observable behavior only. The
``backend.permissions`` imports are deferred into the test bodies so the
module collects cleanly before the feature is implemented (RED).
"""

from __future__ import annotations

from backend.usermanagement import SqliteUserRepository, UserCreate, UserManager, UserRoleChanged


class _Collector:
    """A structural event publisher that collects events (synchronous)."""

    def __init__(self) -> None:
        self.events: list[object] = []

    def publish(self, event: object) -> None:
        self.events.append(event)

    def of_type(self, cls: type) -> list[object]:
        return [event for event in self.events if isinstance(event, cls)]

    def clear(self) -> None:
        self.events.clear()


def _build(
    service_cls,
    role_repo_cls,
    grant_repo_cls,
    system_repo_cls,
    catalog_cls,
    *,
    user_roles=None,
    username="user1",
    seed_roles=(),
    event_bus=None,
):
    """Construct a ``PermissionService`` over in-memory repositories for the event tests.

    Returns ``(service, manager, user)``. ``user_roles`` of ``None`` creates no user;
    ``seed_roles`` is an iterable of ``(role, is_builtin)`` pairs added to the role
    repository before the service is constructed; ``event_bus`` is the (structural)
    publisher wired to both the service and the user manager.
    """
    repo = SqliteUserRepository("sqlite:///:memory:")
    manager = UserManager(repo, event_bus=event_bus)
    user = None
    if user_roles is not None:
        user = manager.create_user(
            UserCreate(username=username, email=f"{username}@example.com", password="correct-horse-1", roles=user_roles)
        )

    catalog = catalog_cls()
    catalog.register_feature(
        "mail",
        {
            "mail.send_email": "Send an email via the shared mail service",
            "mail.send_password_reset_email": "Send the built-in password-reset email",
        },
    )

    role_repo = role_repo_cls()
    for role, is_builtin in seed_roles:
        role_repo.add(role, None, is_builtin)

    service = service_cls(
        role_repo,
        grant_repo_cls(),
        system_repo_cls(),
        manager,
        catalog=catalog,
        event_bus=event_bus,
    )
    return service, manager, user


# --- AC-024: the lifecycle events are published to the publisher ---


def test_events_published_on_operations() -> None:
    """AC-024 / REQ-020: the lifecycle events are published on the operations.

    Given a publisher that collects events, when a denial occurs, then a
    ``PermissionDenied(user_id, permission, reason)`` event is published; when
    ``create_role`` / ``delete_role`` / ``grant_permission`` /
    ``revoke_permission`` succeed, then ``RoleCreated`` / ``RoleDeleted`` /
    ``RolePermissionsChanged`` events are published; when an assignment
    pass-through succeeds, then no permission-feature event is published (the
    assignment event is user-management's ``UserRoleChanged``).
    """
    from backend.permissions import (
        MemoryGrantRepository,
        MemoryRoleRepository,
        MemorySystemPrincipalRepository,
        PermissionCatalog,
        PermissionDenied,
        PermissionDeniedError,
        PermissionService,
        RoleCreated,
        RoleDeleted,
        RolePermissionsChanged,
    )

    collector = _Collector()
    service, _, user = _build(
        PermissionService,
        MemoryRoleRepository,
        MemoryGrantRepository,
        MemorySystemPrincipalRepository,
        PermissionCatalog,
        user_roles=["user"],
        seed_roles=[("admin", True), ("user", True)],
        event_bus=collector,
    )

    perm = "mail.send_email"

    # A denial publishes PermissionDenied(user_id, permission, reason).
    try:
        service.require_permission(user.id, perm)
        raise AssertionError("expected PermissionDeniedError")
    except PermissionDeniedError:
        pass
    denied = collector.of_type(PermissionDenied)
    assert len(denied) == 1
    assert denied[0].user_id == user.id
    assert denied[0].permission == perm
    assert denied[0].reason == "unauthorized"

    # create_role publishes RoleCreated.
    collector.clear()
    service.create_role("editor")
    created = collector.of_type(RoleCreated)
    assert len(created) == 1
    assert created[0].role == "editor"

    # grant_permission publishes RolePermissionsChanged (added).
    collector.clear()
    service.grant_permission("user", perm)
    granted = collector.of_type(RolePermissionsChanged)
    assert len(granted) == 1
    assert granted[0].role == "user"
    assert granted[0].added == [perm]
    assert granted[0].removed == []

    # revoke_permission publishes RolePermissionsChanged (removed).
    collector.clear()
    service.revoke_permission("user", perm)
    revoked = collector.of_type(RolePermissionsChanged)
    assert len(revoked) == 1
    assert revoked[0].role == "user"
    assert revoked[0].added == []
    assert revoked[0].removed == [perm]

    # delete_role publishes RoleDeleted.
    collector.clear()
    service.delete_role("editor")
    deleted = collector.of_type(RoleDeleted)
    assert len(deleted) == 1
    assert deleted[0].role == "editor"

    # An assignment pass-through publishes no permission-feature event;
    # the assignment event is user-management's UserRoleChanged.
    collector.clear()
    service.assign_role(user.id, "admin")
    assert not collector.of_type(PermissionDenied)
    assert not collector.of_type(RoleCreated)
    assert not collector.of_type(RoleDeleted)
    assert not collector.of_type(RolePermissionsChanged)
    assert len(collector.of_type(UserRoleChanged)) == 1


# --- AC-025: a service without a publisher works normally ---


def test_no_publisher_still_works() -> None:
    """AC-025 / REQ-020: a service without a publisher works normally.

    Given a service without a publisher, when all operations are called, then
    they work normally (no events, no errors).
    """
    from backend.permissions import (
        MemoryGrantRepository,
        MemoryRoleRepository,
        MemorySystemPrincipalRepository,
        PermissionCatalog,
        PermissionDeniedError,
        PermissionService,
    )

    service, manager, user = _build(
        PermissionService,
        MemoryRoleRepository,
        MemoryGrantRepository,
        MemorySystemPrincipalRepository,
        PermissionCatalog,
        user_roles=["user"],
        seed_roles=[("admin", True), ("user", True)],
    )

    perm = "mail.send_email"

    # The checks work (deny and the denial error).
    assert service.has_permission(user.id, perm) is False
    try:
        service.require_permission(user.id, perm)
        raise AssertionError("expected PermissionDeniedError")
    except PermissionDeniedError:
        pass
    # The role operations work.
    service.create_role("editor")
    assert any(role.role == "editor" for role in service.list_roles())
    service.grant_permission("editor", perm)
    assert perm in service.get_role_permissions("editor")
    service.revoke_permission("editor", perm)
    assert perm not in service.get_role_permissions("editor")
    service.delete_role("editor")
    # The system set works.
    service.set_system_permissions({perm})
    assert service.get_system_permissions() == frozenset({perm})
    # The assignment pass-throughs work.
    service.assign_role(user.id, "admin")
    assert manager.get_user(user.id).roles == ["admin"]
    service.add_role(user.id, "user")
    service.remove_role(user.id, "admin")
    service.set_roles(user.id, ["user"])
    assert manager.get_user(user.id).roles == ["user"]
