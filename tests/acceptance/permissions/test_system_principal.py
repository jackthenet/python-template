"""Acceptance tests for the permissions system principal (docs/specs/user-roles-permissions.md).

Covers AC-022 (REQ-018): the system principal (``user_id=None``) is granted the
configurable system permission set (stored in ``system_principal_permissions``, live
read); ``set_system_permissions`` / ``get_system_permissions`` manage it with immediate
effect (atomic replace).

These tests verify externally observable behavior only. The ``backend.permissions``
imports are deferred into the test bodies so the module collects cleanly before the
feature is implemented (RED).
"""

from __future__ import annotations

from backend.usermanagement import SqliteUserRepository, UserManager


def _build(service_cls, role_repo_cls, grant_repo_cls, system_repo_cls, catalog_cls, *, system_perms):
    """Construct a ``PermissionService`` over in-memory repositories for the system tests.

    Returns ``(service, catalog)``. The system principal check (``user_id=None``) never
    looks up a user, so a user manager is provided but no user is created.
    """
    catalog = catalog_cls()
    catalog.register_feature(
        "mail",
        {
            "mail.send_email": "Send an email via the shared mail service",
            "mail.send_password_reset_email": "Send the built-in password-reset email",
            "mail.send_email_verification_email": "Send the email-verification email",
        },
    )
    system_repo = system_repo_cls()
    system_repo.set_permissions(system_perms)
    manager = UserManager(SqliteUserRepository("sqlite:///:memory:"))
    service = service_cls(
        role_repo_cls(),
        grant_repo_cls(),
        system_repo,
        manager,
        catalog=catalog,
    )
    return service, catalog


def test_system_principal_check_and_set() -> None:
    """AC-022 / REQ-018: the system principal is granted the configurable system set.

    Given a system set ``{p1}``, when ``has_permission(None, p1)`` is called, then ``True``
    is returned; when ``has_permission(None, p2)`` is called, then ``False`` is returned;
    when ``set_system_permissions({p3})`` is called, then ``has_permission(None, p3)``
    returns ``True`` (immediate effect) and ``has_permission(None, p1)`` returns ``False``
    (atomic replace).
    """
    from backend.permissions import (
        MemoryGrantRepository,
        MemoryRoleRepository,
        MemorySystemPrincipalRepository,
        PermissionCatalog,
        PermissionService,
    )

    p1 = "mail.send_email"
    p2 = "mail.send_password_reset_email"
    p3 = "mail.send_email_verification_email"
    service, _ = _build(
        PermissionService,
        MemoryRoleRepository,
        MemoryGrantRepository,
        MemorySystemPrincipalRepository,
        PermissionCatalog,
        system_perms={p1},
    )
    # p1 is in the system set -> True.
    assert service.has_permission(None, p1) is True
    # p2 is in the catalog but not the system set -> False.
    assert service.has_permission(None, p2) is False
    # get_system_permissions reflects the current set.
    assert service.get_system_permissions() == frozenset({p1})
    # set_system_permissions replaces the set (immediate effect).
    service.set_system_permissions({p3})
    assert service.has_permission(None, p3) is True
    # Atomic replace: p1 is no longer granted.
    assert service.has_permission(None, p1) is False
    assert service.get_system_permissions() == frozenset({p3})


# --- AC-023: the settings alias syncs with the system-set table ---


def test_system_set_settings_alias_sync() -> None:
    """AC-023 / REQ-019: the settings alias syncs with the system-set table.

    Given ``register_settings`` called and the registry live, when
    ``set_value("permissions.system_principal", [p4])`` is called, then the
    system-set table is updated (via ``SettingChanged``), and when
    ``set_system_permissions([p5])`` is called, then the registry key is
    synced (best-effort).
    """
    from settings_test_helpers import make_registry, wait_for

    from backend.permissions import (
        MemoryGrantRepository,
        MemoryRoleRepository,
        MemorySystemPrincipalRepository,
        PermissionCatalog,
        PermissionService,
        register_settings,
    )

    registry, bus = make_registry()
    try:
        register_settings(registry)

        # The key is registered with the bootstrap default (a list).
        default = registry.get_value("permissions.system_principal")
        assert isinstance(default, list)
        assert "usermanagement.get_user" in default
        assert "mail.send_email" in default

        catalog = PermissionCatalog()
        catalog.register_feature(
            "mail",
            {
                "mail.send_email": "Send an email via the shared mail service",
                "mail.send_password_reset_email": "Send the built-in password-reset email",
                "mail.send_email_verification_email": "Send the email-verification email",
            },
        )
        system_repo = MemorySystemPrincipalRepository()
        manager = UserManager(SqliteUserRepository("sqlite:///:memory:"))
        service = PermissionService(
            MemoryRoleRepository(),
            MemoryGrantRepository(),
            system_repo,
            manager,
            catalog=catalog,
            event_bus=bus,
            settings_registry=registry,
        )

        # A registry write updates the system-set table (via SettingChanged).
        registry.set_value("permissions.system_principal", ["mail.send_password_reset_email"])
        assert wait_for(
            lambda: service.get_system_permissions() == frozenset({"mail.send_password_reset_email"})
        ), "the system-set table was not updated via SettingChanged"

        # set_system_permissions syncs the registry key (best-effort).
        service.set_system_permissions({"mail.send_email_verification_email"})
        assert service.get_system_permissions() == frozenset({"mail.send_email_verification_email"})
        assert registry.get_value("permissions.system_principal") == ["mail.send_email_verification_email"]
    finally:
        bus.shutdown()
