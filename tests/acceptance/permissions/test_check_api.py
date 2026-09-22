"""Acceptance tests for the permissions check core (docs/specs/user-roles-permissions.md).

Covers the check API (``has_permission`` / ``require_permission``), the fail-closed
denials (malformed / unknown permission, unknown user, storage error, inactive user),
the ``admin`` implicit wildcard, the non-admin role's zero permissions, session
validation in the check, and the denial logging (the session token is a secret).

These tests verify externally observable behavior only. The ``backend.permissions``
imports are deferred into the test bodies so the module collects cleanly before the
feature is implemented (RED).
"""

from __future__ import annotations

import contextlib
import hashlib
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from backend.usermanagement import SqliteUserRepository, UserCreate, UserManager


def _build(
    service_cls,
    role_repo_cls,
    grant_repo_cls,
    system_repo_cls,
    catalog_cls,
    *,
    user_roles,
    grants=None,
    system_perms=None,
    session_lookup=None,
    event_bus=None,
    username="user1",
):
    """Construct a ``PermissionService`` over in-memory repositories for the check tests.

    Returns ``(service, manager, user)``. The user is created with ``user_roles``;
    ``grants`` is a mapping ``role -> [permissions]`` applied to the grant repository
    (the repository-level grant, so the check's live lookup reads it); ``system_perms``
    is the system-principal set. The catalog registers the ``usermanagement`` and
    ``mail`` features used by these tests.
    """
    repo = SqliteUserRepository("sqlite:///:memory:")
    manager = UserManager(repo)
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

    grant_repo = grant_repo_cls()
    for role, perms in (grants or {}).items():
        for perm in perms:
            grant_repo.grant(role, perm)

    system_repo = system_repo_cls()
    if system_perms is not None:
        system_repo.set_permissions(system_perms)

    service = service_cls(
        role_repo_cls(),
        grant_repo,
        system_repo,
        manager,
        session_lookup=session_lookup,
        catalog=catalog,
        event_bus=event_bus,
    )
    return service, manager, user


# --- AC-002: a denied require_permission carries the denial context ---


def test_denied_permission_raises_with_context() -> None:
    """AC-002 / REQ-001: a denied ``require_permission`` carries the denial context.

    Given a user without ``usermanagement.delete_user``, when ``has_permission``
    is called, then ``False`` is returned; when ``require_permission`` is called,
    then a ``PermissionDeniedError`` is raised with ``user_id``,
    ``permission="usermanagement.delete_user"``, ``reason="unauthorized"``.
    """
    from backend.permissions import (
        MemoryGrantRepository,
        MemoryRoleRepository,
        MemorySystemPrincipalRepository,
        PermissionCatalog,
        PermissionDeniedError,
        PermissionService,
    )

    service, _, user = _build(
        PermissionService,
        MemoryRoleRepository,
        MemoryGrantRepository,
        MemorySystemPrincipalRepository,
        PermissionCatalog,
        user_roles=["user"],
    )

    # has_permission returns False.
    assert service.has_permission(user.id, "usermanagement.delete_user") is False

    # require_permission raises with the denial context.
    try:
        service.require_permission(user.id, "usermanagement.delete_user")
        raise AssertionError("expected PermissionDeniedError")
    except PermissionDeniedError as exc:
        assert exc.user_id == user.id
        assert exc.permission == "usermanagement.delete_user"
        assert exc.reason == "unauthorized"


# --- AC-003: a malformed permission key denies (malformed_permission) ---


def test_malformed_permission_denied() -> None:
    """AC-003 / REQ-002: a malformed permission key denies (malformed_permission).

    Given a check for a key that does not match the permission pattern
    (``^[a-z0-9_-]+\\.[a-z0-9_-]+$``), when ``has_permission`` is called, then
    ``False`` is returned (reason ``malformed_permission``).
    """
    from backend.permissions import (
        MemoryGrantRepository,
        MemoryRoleRepository,
        MemorySystemPrincipalRepository,
        PermissionCatalog,
        PermissionDeniedError,
        PermissionService,
    )

    service, _, user = _build(
        PermissionService,
        MemoryRoleRepository,
        MemoryGrantRepository,
        MemorySystemPrincipalRepository,
        PermissionCatalog,
        user_roles=["user"],
    )

    # A key that does not match the pattern (uppercase feature segment).
    malformed = "Usermanagement.get_user"
    assert service.has_permission(user.id, malformed) is False
    try:
        service.require_permission(user.id, malformed)
        raise AssertionError("expected PermissionDeniedError")
    except PermissionDeniedError as exc:
        assert exc.reason == "malformed_permission"


# --- AC-012: the admin role is an implicit wildcard ---


def test_admin_wildcard_allows_all() -> None:
    """AC-012 / REQ-010: the admin role is an implicit wildcard.

    Given a user with the ``admin`` role, when ``has_permission`` is called for
    any catalog permission, then ``True`` is returned, including for permissions
    not explicitly granted to ``admin``.
    """
    from backend.permissions import (
        MemoryGrantRepository,
        MemoryRoleRepository,
        MemorySystemPrincipalRepository,
        PermissionCatalog,
        PermissionService,
    )

    service, _, user = _build(
        PermissionService,
        MemoryRoleRepository,
        MemoryGrantRepository,
        MemorySystemPrincipalRepository,
        PermissionCatalog,
        user_roles=["admin"],
    )

    for perm in ("usermanagement.get_user", "usermanagement.delete_user", "mail.send_email"):
        assert service.has_permission(user.id, perm) is True


# --- AC-013: the non-admin role starts with zero permissions ---


def test_user_role_starts_with_zero_permissions() -> None:
    """AC-013 / REQ-011: the non-admin (user) role starts with zero permissions.

    Given a freshly created user with the ``user`` role, when ``has_permission``
    is called for any catalog permission, then ``False`` is returned (zero
    permissions; its permissions come only from dynamic grants).
    """
    from backend.permissions import (
        MemoryGrantRepository,
        MemoryRoleRepository,
        MemorySystemPrincipalRepository,
        PermissionCatalog,
        PermissionService,
    )

    service, _, user = _build(
        PermissionService,
        MemoryRoleRepository,
        MemoryGrantRepository,
        MemorySystemPrincipalRepository,
        PermissionCatalog,
        user_roles=["user"],
    )

    for perm in ("usermanagement.get_user", "usermanagement.delete_user", "mail.send_email"):
        assert service.has_permission(user.id, perm) is False


# --- AC-017: an unknown user id denies (unknown_user) ---


def test_unknown_user_denied() -> None:
    """AC-017 / REQ-015: an unknown user id denies (unknown_user).

    Given an unknown user id, when ``has_permission`` is called, then ``False``
    is returned (reason ``unknown_user``); when ``require_permission`` is called,
    then a ``PermissionDeniedError`` with ``reason="unknown_user"`` is raised.
    """
    from backend.permissions import (
        MemoryGrantRepository,
        MemoryRoleRepository,
        MemorySystemPrincipalRepository,
        PermissionCatalog,
        PermissionDeniedError,
        PermissionService,
    )

    service, _, _ = _build(
        PermissionService,
        MemoryRoleRepository,
        MemoryGrantRepository,
        MemorySystemPrincipalRepository,
        PermissionCatalog,
        user_roles=["user"],
    )

    unknown_id = uuid4()
    assert service.has_permission(unknown_id, "usermanagement.get_user") is False
    try:
        service.require_permission(unknown_id, "usermanagement.get_user")
        raise AssertionError("expected PermissionDeniedError")
    except PermissionDeniedError as exc:
        assert exc.reason == "unknown_user"


# --- AC-018: a user lookup that raises denies (storage_error) ---


def test_storage_error_denied_fail_closed() -> None:
    """AC-018 / REQ-015: a user lookup that raises denies (storage_error).

    Given a user lookup that raises (storage failure), when ``has_permission``
    is called, then ``False`` is returned (reason ``storage_error``) and no
    exception other than the denial is propagated (never a crash).
    """
    from backend.permissions import (
        MemoryGrantRepository,
        MemoryRoleRepository,
        MemorySystemPrincipalRepository,
        PermissionCatalog,
        PermissionDeniedError,
        PermissionService,
    )

    class _RaisingUserManager:
        """A structural UserManager whose user lookup raises (storage failure)."""

        def get_user(self, user_id):
            raise RuntimeError("storage failure")

    catalog = PermissionCatalog()
    catalog.register_feature("usermanagement", {"usermanagement.get_user": "Read a user by id"})

    service = PermissionService(
        MemoryRoleRepository(),
        MemoryGrantRepository(),
        MemorySystemPrincipalRepository(),
        _RaisingUserManager(),
        catalog=catalog,
    )

    user_id = uuid4()
    assert service.has_permission(user_id, "usermanagement.get_user") is False
    try:
        service.require_permission(user_id, "usermanagement.get_user")
        raise AssertionError("expected PermissionDeniedError")
    except PermissionDeniedError as exc:
        assert exc.reason == "storage_error"


# --- AC-019: an inactive user (even with admin) denies (inactive_user) ---


def test_inactive_user_denied_even_admin() -> None:
    """AC-019 / REQ-016: an inactive user (even with admin) denies (inactive_user).

    Given an inactive user with the ``admin`` role, when ``has_permission`` is
    called for any catalog permission, then ``False`` is returned (reason
    ``inactive_user``).
    """
    from backend.permissions import (
        MemoryGrantRepository,
        MemoryRoleRepository,
        MemorySystemPrincipalRepository,
        PermissionCatalog,
        PermissionDeniedError,
        PermissionService,
    )

    # Two admins so deactivating one does not trip the last-admin guard.
    service, manager, user = _build(
        PermissionService,
        MemoryRoleRepository,
        MemoryGrantRepository,
        MemorySystemPrincipalRepository,
        PermissionCatalog,
        user_roles=["admin"],
        username="admin1",
    )
    manager.create_user(
        UserCreate(username="admin2", email="admin2@example.com", password="correct-horse-1", roles=["admin"])
    )
    manager.deactivate_user(user.id)

    assert service.has_permission(user.id, "usermanagement.get_user") is False
    try:
        service.require_permission(user.id, "usermanagement.get_user")
        raise AssertionError("expected PermissionDeniedError")
    except PermissionDeniedError as exc:
        assert exc.reason == "inactive_user"


# --- AC-020: a provided session token is validated in the check ---


def test_session_validation_in_check() -> None:
    """AC-020 / REQ-017: a provided session token is validated in the check.

    Given a valid, unrevoked, unexpired session token for user ``u``, when
    ``has_permission(u, p, session_token=t)`` is called, then the session is
    validated and the check proceeds. Given a revoked token, then ``False`` is
    returned (reason ``invalid_session``). Given a token belonging to a
    different user, then ``False`` is returned (reason
    ``session_principal_mismatch``).
    """
    from backend.permissions import (
        MemoryGrantRepository,
        MemoryRoleRepository,
        MemorySystemPrincipalRepository,
        PermissionCatalog,
        PermissionDeniedError,
        PermissionService,
    )

    class _SessionRecord:
        def __init__(self, user_id, expires_at, revoked):
            self.user_id = user_id
            self.expires_at = expires_at
            self.revoked = revoked

    class _FakeSessionLookup:
        """A structural SessionLookup keyed by the SHA-256 hash of the token."""

        def __init__(self):
            self._records = {}

        def add(self, token, record):
            self._records[hashlib.sha256(token.encode("utf-8")).hexdigest()] = record

        def get_by_token_hash(self, token_hash):
            return self._records.get(token_hash)

    lookup = _FakeSessionLookup()
    now = datetime.now(UTC)

    service, manager, user = _build(
        PermissionService,
        MemoryRoleRepository,
        MemoryGrantRepository,
        MemorySystemPrincipalRepository,
        PermissionCatalog,
        user_roles=["admin"],
        session_lookup=lookup,
    )

    # A valid, unrevoked, unexpired session for the user -> the check proceeds.
    valid_token = "valid-token"
    lookup.add(valid_token, _SessionRecord(user.id, now + timedelta(hours=1), False))
    assert service.has_permission(user.id, "usermanagement.get_user", session_token=valid_token) is True

    # A revoked token -> deny (invalid_session).
    revoked_token = "revoked-token"
    lookup.add(revoked_token, _SessionRecord(user.id, now + timedelta(hours=1), True))
    assert service.has_permission(user.id, "usermanagement.get_user", session_token=revoked_token) is False
    try:
        service.require_permission(user.id, "usermanagement.get_user", session_token=revoked_token)
        raise AssertionError("expected PermissionDeniedError")
    except PermissionDeniedError as exc:
        assert exc.reason == "invalid_session"

    # A token belonging to a different user -> deny (session_principal_mismatch).
    other_user = manager.create_user(
        UserCreate(username="user2", email="user2@example.com", password="correct-horse-1", roles=["admin"])
    )
    mismatch_token = "mismatch-token"
    lookup.add(mismatch_token, _SessionRecord(other_user.id, now + timedelta(hours=1), False))
    assert service.has_permission(user.id, "usermanagement.get_user", session_token=mismatch_token) is False
    try:
        service.require_permission(user.id, "usermanagement.get_user", session_token=mismatch_token)
        raise AssertionError("expected PermissionDeniedError")
    except PermissionDeniedError as exc:
        assert exc.reason == "session_principal_mismatch"


# --- AC-021: an omitted token skips session validation ---


def test_session_validation_skipped_when_token_none() -> None:
    """AC-021 / REQ-017: an omitted token skips session validation.

    Given a check with ``session_token=None``, when it is called, then session
    validation is skipped (the session lookup is never invoked) and the
    user/role evaluation proceeds.
    """
    from backend.permissions import (
        MemoryGrantRepository,
        MemoryRoleRepository,
        MemorySystemPrincipalRepository,
        PermissionCatalog,
        PermissionService,
    )

    class _DenyIfCalledLookup:
        def get_by_token_hash(self, token_hash):
            raise AssertionError("session lookup must be skipped when the token is None")

    service, _, user = _build(
        PermissionService,
        MemoryRoleRepository,
        MemoryGrantRepository,
        MemorySystemPrincipalRepository,
        PermissionCatalog,
        user_roles=["admin"],
        session_lookup=_DenyIfCalledLookup(),
    )

    assert service.has_permission(user.id, "usermanagement.get_user", session_token=None) is True


# --- AC-039: a denied check logs user_id/permission/reason, never the token ---


def test_denial_log_and_no_token_leak(log_records) -> None:
    """AC-039 / REQ-028: a denied check logs user_id/permission/reason, never the token.

    Given the traced service, when a check with a session token is denied, then
    the WARNING log contains ``user_id``, ``permission``, ``reason`` and no log
    record contains the session token.
    """
    from backend.permissions import (
        MemoryGrantRepository,
        MemoryRoleRepository,
        MemorySystemPrincipalRepository,
        PermissionCatalog,
        PermissionService,
    )

    class _UnknownSessionLookup:
        def get_by_token_hash(self, token_hash):
            return None  # unknown session -> deny

    service, _, user = _build(
        PermissionService,
        MemoryRoleRepository,
        MemoryGrantRepository,
        MemorySystemPrincipalRepository,
        PermissionCatalog,
        user_roles=["user"],
        session_lookup=_UnknownSessionLookup(),
    )

    token = "secret-session-token"
    with contextlib.suppress(Exception):
        service.require_permission(user.id, "usermanagement.get_user", session_token=token)

    def _text(record) -> str:
        # Combine the message text and the full record dict so both the log
        # message and any record fields are checked.
        return str(record) + str(record["record"])

    # The denial is logged (the permission key appears in a log record).
    assert any("usermanagement.get_user" in _text(r) for r in log_records), "expected the denial to be logged"
    # No log record contains the session token.
    assert all(token not in _text(r) for r in log_records), "session token leaked in the log"


def _build_grant_scenario(
    service_cls,
    role_repo_cls,
    grant_repo_cls,
    system_repo_cls,
    catalog_cls,
    *,
    user_roles,
    grants=None,
    username="user1",
    role_store=None,
):
    """Construct a ``PermissionService`` over in-memory repositories for the dynamic-grant tests.

    Returns ``(service, manager, user)``. The catalog registers the ``usermanagement``,
    ``mail`` and ``settings`` features; ``grants`` is a mapping ``role -> [permissions]``
    applied to the grant repository (the repository-level grant, so the check's live
    lookup reads it); ``role_store`` overrides the user manager's role store (needed
    when the user holds a non-built-in role).
    """
    repo = SqliteUserRepository("sqlite:///:memory:")
    manager = UserManager(repo) if role_store is None else UserManager(repo, role_store=role_store)
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
    catalog.register_feature(
        "settings",
        {
            "settings.get_value": "Read a setting value",
            "settings.set_value": "Set a setting value (validated)",
        },
    )

    grant_repo = grant_repo_cls()
    for role, perms in (grants or {}).items():
        for perm in perms:
            grant_repo.grant(role, perm)

    system_repo = system_repo_cls()
    service = service_cls(
        role_repo_cls(),
        grant_repo,
        system_repo,
        manager,
        catalog=catalog,
    )
    return service, manager, user


# --- AC-001: a granted permission is allowed ---


def test_granted_permission_allowed() -> None:
    """AC-001 / REQ-001: a granted permission is allowed.

    Given a user whose role is granted ``usermanagement.get_user``, when
    ``has_permission(user_id, "usermanagement.get_user")`` is called, then ``True``
    is returned; when ``require_permission(user_id, "usermanagement.get_user")`` is
    called, then no exception is raised.
    """
    from backend.permissions import (
        MemoryGrantRepository,
        MemoryRoleRepository,
        MemorySystemPrincipalRepository,
        PermissionCatalog,
        PermissionService,
    )

    service, _, user = _build(
        PermissionService,
        MemoryRoleRepository,
        MemoryGrantRepository,
        MemorySystemPrincipalRepository,
        PermissionCatalog,
        user_roles=["user"],
        grants={"user": ["usermanagement.get_user"]},
    )

    assert service.has_permission(user.id, "usermanagement.get_user") is True
    service.require_permission(user.id, "usermanagement.get_user")


# --- AC-004: a feature wildcard grant matches every action of the feature ---


def test_feature_wildcard_grant() -> None:
    """AC-004 / REQ-003: a feature wildcard grant matches every action of the feature.

    Given a role granted ``settings.*``, when ``has_permission(user_id,
    "settings.get_value")`` is called for a holder of that role, then ``True`` is
    returned; when ``has_permission(user_id, "mail.send_email")`` is called, then
    ``False`` is returned.
    """
    from backend.permissions import (
        MemoryGrantRepository,
        MemoryRoleRepository,
        MemorySystemPrincipalRepository,
        PermissionCatalog,
        PermissionService,
    )

    service, _, user = _build_grant_scenario(
        PermissionService,
        MemoryRoleRepository,
        MemoryGrantRepository,
        MemorySystemPrincipalRepository,
        PermissionCatalog,
        user_roles=["user"],
        grants={"user": ["settings.*"]},
    )

    assert service.has_permission(user.id, "settings.get_value") is True
    assert service.has_permission(user.id, "mail.send_email") is False


# --- AC-005: an unknown permission denies and the grant is rejected ---


def test_unknown_permission_denied_and_grant_rejected() -> None:
    """AC-005 / REQ-004: an unknown permission denies and the grant is rejected.

    Given the catalog built at startup, when a check is made for a key not in the
    catalog (``reports.export``), then the check denies (reason
    ``unknown_permission``); when ``grant_permission(role, "reports.export")`` is
    called, then an ``UnknownPermissionError`` is raised.
    """
    from backend.permissions import (
        MemoryGrantRepository,
        MemoryRoleRepository,
        MemorySystemPrincipalRepository,
        PermissionCatalog,
        PermissionDeniedError,
        PermissionService,
        UnknownPermissionError,
    )

    service, _, user = _build(
        PermissionService,
        MemoryRoleRepository,
        MemoryGrantRepository,
        MemorySystemPrincipalRepository,
        PermissionCatalog,
        user_roles=["user"],
    )

    assert service.has_permission(user.id, "reports.export") is False
    try:
        service.require_permission(user.id, "reports.export")
        raise AssertionError("expected PermissionDeniedError")
    except PermissionDeniedError as exc:
        assert exc.reason == "unknown_permission"
    try:
        service.grant_permission("user", "reports.export")
        raise AssertionError("expected UnknownPermissionError")
    except UnknownPermissionError:
        pass


# --- AC-011: the multi-role union of permissions ---


def test_multi_role_union_of_permissions() -> None:
    """AC-011 / REQ-009: the effective permission set is the union of the roles' grants.

    Given a user with roles ``[a, b]`` where ``a`` is granted ``p1`` and ``b`` is
    granted ``p2``, when ``has_permission`` is called for ``p1`` and for ``p2``,
    then both return ``True`` (union).
    """
    from backend.permissions import (
        MemoryGrantRepository,
        MemoryRoleRepository,
        MemorySystemPrincipalRepository,
        PermissionCatalog,
        PermissionService,
    )
    from backend.usermanagement import StaticRoleStore

    service, _, user = _build_grant_scenario(
        PermissionService,
        MemoryRoleRepository,
        MemoryGrantRepository,
        MemorySystemPrincipalRepository,
        PermissionCatalog,
        user_roles=["a", "b"],
        grants={"a": ["usermanagement.get_user"], "b": ["mail.send_email"]},
        role_store=StaticRoleStore(("admin", "user", "a", "b")),
    )

    p1 = "usermanagement.get_user"
    p2 = "mail.send_email"
    assert service.has_permission(user.id, p1) is True
    assert service.has_permission(user.id, p2) is True
    # A permission granted to neither role is not in the union.
    assert service.has_permission(user.id, "usermanagement.delete_user") is False


# --- AC-014: role assignment is delegated to the UserManager ---


class _SpyUserManager:
    """A structural UserManager spy: records the assignment methods and delegates to the real manager.

    The permission service only sees this spy, so every user-role write is
    observable as a recorded call to the corresponding UserManager method
    (delegation; the service never writes user roles directly).
    """

    def __init__(self, inner) -> None:
        self._inner = inner
        self.set_role_calls: list[tuple] = []
        self.set_roles_calls: list[tuple] = []
        self.add_role_calls: list[tuple] = []
        self.remove_role_calls: list[tuple] = []

    def set_role(self, user_id, role):
        self.set_role_calls.append((user_id, role))
        return self._inner.set_role(user_id, role)

    def set_roles(self, user_id, roles):
        self.set_roles_calls.append((user_id, list(roles)))
        return self._inner.set_roles(user_id, roles)

    def add_role(self, user_id, role):
        self.add_role_calls.append((user_id, role))
        return self._inner.add_role(user_id, role)

    def remove_role(self, user_id, role):
        self.remove_role_calls.append((user_id, role))
        return self._inner.remove_role(user_id, role)

    def get_user(self, user_id):
        return self._inner.get_user(user_id)


def test_assignment_delegates_to_user_manager() -> None:
    """AC-014 / REQ-012: role assignment is delegated to the UserManager.

    Given the permission service, when ``assign_role`` / ``add_role`` /
    ``remove_role`` / ``set_roles`` are called, then the corresponding
    ``UserManager`` method is invoked (delegation) and the service does not
    write user roles directly (the user's roles follow the manager semantics).
    """
    from backend.permissions import (
        MemoryGrantRepository,
        MemoryRoleRepository,
        MemorySystemPrincipalRepository,
        PermissionCatalog,
        PermissionService,
    )

    repo = SqliteUserRepository("sqlite:///:memory:")
    manager = UserManager(repo)
    user = manager.create_user(
        UserCreate(username="user1", email="user1@example.com", password="correct-horse-1", roles=["user"])
    )

    catalog = PermissionCatalog()
    catalog.register_feature("mail", {"mail.send_email": "Send an email"})

    role_repo = MemoryRoleRepository()
    role_repo.add("admin", None, True)
    role_repo.add("user", None, True)

    spy = _SpyUserManager(manager)
    service = PermissionService(
        role_repo,
        MemoryGrantRepository(),
        MemorySystemPrincipalRepository(),
        spy,
        catalog=catalog,
    )

    # assign_role delegates to set_role (replace).
    service.assign_role(user.id, "admin")
    assert spy.set_role_calls == [(user.id, "admin")]
    assert manager.get_user(user.id).roles == ["admin"]

    # add_role delegates to add_role (append).
    service.add_role(user.id, "user")
    assert spy.add_role_calls == [(user.id, "user")]
    assert manager.get_user(user.id).roles == ["admin", "user"]

    # remove_role delegates to remove_role.
    service.remove_role(user.id, "admin")
    assert spy.remove_role_calls == [(user.id, "admin")]
    assert manager.get_user(user.id).roles == ["user"]

    # set_roles delegates to set_roles (replace).
    service.set_roles(user.id, ["user", "admin"])
    assert spy.set_roles_calls == [(user.id, ["user", "admin"])]
    assert manager.get_user(user.id).roles == ["user", "admin"]


# --- AC-015: the last-admin guard is preserved on the pass-throughs ---


def test_last_admin_guard_preserved_via_service() -> None:
    """AC-015 / REQ-013: the last-admin guard is preserved on the pass-throughs.

    Given the last active admin, when ``remove_role(last_admin_id, "admin")``
    is called via the service, then a ``LastAdminError`` is raised (from the
    delegation) and the user's roles are unchanged.
    """
    from backend.permissions import (
        MemoryGrantRepository,
        MemoryRoleRepository,
        MemorySystemPrincipalRepository,
        PermissionCatalog,
        PermissionService,
    )
    from backend.usermanagement import LastAdminError

    repo = SqliteUserRepository("sqlite:///:memory:")
    manager = UserManager(repo)
    admin = manager.create_user(
        UserCreate(username="admin1", email="admin1@example.com", password="correct-horse-1", roles=["admin"])
    )

    catalog = PermissionCatalog()
    catalog.register_feature("mail", {"mail.send_email": "Send an email"})

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

    try:
        service.remove_role(admin.id, "admin")
        raise AssertionError("expected LastAdminError")
    except LastAdminError:
        pass
    # The demotion did not happen: the roles are unchanged.
    assert manager.get_user(admin.id).roles == ["admin"]


# --- AC-016: a granted role takes effect on the next check ---


def test_grant_change_takes_effect_immediately() -> None:
    """AC-016 / REQ-014: a granted role takes effect on the next check.

    Given a user denied ``p``, when the role holding ``p`` is granted to the
    user, and ``has_permission(user_id, p)`` is called again, then ``True`` is
    returned (immediate effect, no re-login, no cache).
    """
    from backend.permissions import (
        MemoryGrantRepository,
        MemoryRoleRepository,
        MemorySystemPrincipalRepository,
        PermissionCatalog,
        PermissionService,
    )
    from backend.usermanagement import StaticRoleStore

    repo = SqliteUserRepository("sqlite:///:memory:")
    manager = UserManager(repo, role_store=StaticRoleStore(("admin", "user", "editor")))
    user = manager.create_user(
        UserCreate(username="user1", email="user1@example.com", password="correct-horse-1", roles=["user"])
    )

    catalog = PermissionCatalog()
    catalog.register_feature("mail", {"mail.send_email": "Send an email"})

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
    # The user is denied the permission.
    assert service.has_permission(user.id, perm) is False
    # The role holding the permission is created, granted, and assigned to the user.
    service.create_role("editor")
    service.grant_permission("editor", perm)
    service.add_role(user.id, "editor")
    # Immediate effect on the next check (no re-login, no cache).
    assert service.has_permission(user.id, perm) is True


# --- AC-006: the initial catalog is exactly the 60 keys of the spec table ---

# The initial catalog table (spec Section 3; the table is the source of truth):
# 60 actions across the six features.
INITIAL_CATALOG_SIZE: int = 60
EXPECTED_INITIAL_CATALOG: dict[str, tuple[str, ...]] = {
    "usermanagement": (
        "usermanagement.create_user",
        "usermanagement.get_user",
        "usermanagement.get_user_by_username",
        "usermanagement.list_users",
        "usermanagement.update_user",
        "usermanagement.delete_user",
        "usermanagement.change_password",
        "usermanagement.verify_password",
        "usermanagement.set_role",
        "usermanagement.activate_user",
        "usermanagement.deactivate_user",
    ),
    "authentication": (
        "authentication.login",
        "authentication.session_info",
        "authentication.logout",
        "authentication.request_password_reset",
        "authentication.complete_password_reset",
        "authentication.begin_passkey_registration",
        "authentication.complete_passkey_registration",
        "authentication.begin_passkey_login",
        "authentication.complete_passkey_login",
        "authentication.list_passkeys",
        "authentication.delete_passkey",
    ),
    "settings": (
        "settings.register",
        "settings.register_feature",
        "settings.has",
        "settings.get_definition",
        "settings.get_value",
        "settings.set_value",
        "settings.reset",
        "settings.reset_all",
        "settings.get_status",
        "settings.to_view",
        "settings.views",
        "settings.grouped_views",
        "settings.create_template",
        "settings.load_template",
        "settings.update_template",
        "settings.delete_template",
        "settings.get_template",
        "settings.has_template",
        "settings.list_templates",
    ),
    "filemanagement": (
        "filemanagement.upload",
        "filemanagement.upload_avatar",
        "filemanagement.replace_avatar",
        "filemanagement.delete_avatar",
        "filemanagement.get_avatar",
        "filemanagement.download",
        "filemanagement.open",
        "filemanagement.delete",
        "filemanagement.get_file",
        "filemanagement.list_files",
    ),
    "mail": (
        "mail.send_email",
        "mail.send_password_reset_email",
        "mail.send_email_verification_email",
    ),
    "sessionmanagement": (
        "sessionmanagement.list_sessions",
        "sessionmanagement.revoke_session",
        "sessionmanagement.logout_all_sessions",
        "sessionmanagement.logout_other_sessions",
        "sessionmanagement.revoke_all_sessions",
        "sessionmanagement.cleanup_expired",
    ),
}


def test_initial_catalog_exactly_60_keys() -> None:
    """AC-006 / REQ-005: the six features' register_actions produce exactly the 60 keys.

    Given the six features' ``register_actions`` called at startup, when the
    catalog is inspected, then it contains exactly the 60 keys of the initial
    catalog table, grouped by the six features.
    """
    from backend.authentication.feature_actions import register_actions as authentication_actions  # deferred: RED
    from backend.filemanagement.feature_actions import register_actions as filemanagement_actions  # deferred: RED
    from backend.mail.feature_actions import register_actions as mail_actions  # deferred: RED
    from backend.sessionmanagement.feature_actions import register_actions as sessionmanagement_actions  # deferred: RED
    from backend.settings.feature_actions import register_actions as settings_actions  # deferred: RED
    from backend.usermanagement.feature_actions import register_actions as usermanagement_actions  # deferred: RED

    from backend.permissions import PermissionCatalog  # deferred: RED

    catalog = PermissionCatalog()
    usermanagement_actions(catalog)
    authentication_actions(catalog)
    settings_actions(catalog)
    filemanagement_actions(catalog)
    mail_actions(catalog)
    sessionmanagement_actions(catalog)

    # Grouped by the six features.
    assert catalog.features() == frozenset(EXPECTED_INITIAL_CATALOG)

    # Exactly the 60 keys of the initial catalog table (spec Section 3).
    expected: set[str] = {key for keys in EXPECTED_INITIAL_CATALOG.values() for key in keys}
    assert len(expected) == INITIAL_CATALOG_SIZE
    assert {action.permission for action in catalog.actions()} == expected

    # Every key is grouped under its own feature (feature.action).
    for feature, keys in EXPECTED_INITIAL_CATALOG.items():
        feature_actions = list(catalog.actions(feature))
        assert {action.permission for action in feature_actions} == set(keys)
        assert all(action.feature == feature for action in feature_actions)
