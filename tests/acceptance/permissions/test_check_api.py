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
    username="u1",
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
        UserCreate(username="u2", email="u2@example.com", password="correct-horse-1", roles=["admin"])
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
