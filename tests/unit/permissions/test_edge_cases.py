"""Unit tests for the permissions check edge cases (docs/specs/user-roles-permissions.md).

Local-behavior tests for the check-core edge cases: malformed / unknown permission,
unknown / inactive user, revoked / expired / mismatched session, an unavailable session
lookup, a concurrently deleted user, a raising user lookup, and the system-principal set
validation (unknown permission rejected, feature wildcard allowed).

The ``backend.permissions`` imports are deferred into the test bodies so the module
collects cleanly before the feature is implemented (RED).
"""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from backend.usermanagement import SqliteUserRepository, UserCreate, UserManager


class _SessionRecord:
    """A structural ``SessionRecord`` (the check reads ``user_id`` / ``expires_at`` / ``revoked``)."""

    def __init__(self, user_id, expires_at, revoked):
        self.user_id = user_id
        self.expires_at = expires_at
        self.revoked = revoked


class _FakeSessionLookup:
    """A structural ``SessionLookup`` keyed by the SHA-256 hash of the token."""

    def __init__(self):
        self._records = {}

    def add(self, token, record):
        self._records[hashlib.sha256(token.encode("utf-8")).hexdigest()] = record

    def get_by_token_hash(self, token_hash):
        return self._records.get(token_hash)


class _RaisingUserManager:
    """A structural UserManager whose user lookup raises (storage failure)."""

    def get_user(self, user_id):
        raise RuntimeError("storage failure")


class _RaisingSessionLookup:
    """A structural SessionLookup whose lookup raises (storage failure)."""

    def get_by_token_hash(self, token_hash):
        raise RuntimeError("storage failure")


def _build(
    service_cls,
    role_repo_cls,
    grant_repo_cls,
    system_repo_cls,
    catalog_cls,
    *,
    user_roles=None,
    username="u1",
    grants=None,
    session_lookup=None,
    user_manager=None,
):
    """Construct a ``PermissionService`` over in-memory repositories for the edge-case tests.

    Returns ``(service, manager, user, grant_repo)``. ``user_roles`` of ``None`` creates no
    user; ``grants`` is a mapping ``role -> [permissions]`` applied to the grant repository;
    ``user_manager`` overrides the user manager (a structural fake).
    """
    catalog = catalog_cls()
    catalog.register_feature(
        "mail",
        {
            "mail.send_email": "Send an email via the shared mail service",
            "mail.send_password_reset_email": "Send the built-in password-reset email",
        },
    )
    grant_repo = grant_repo_cls()
    for role, perms in (grants or {}).items():
        for perm in perms:
            grant_repo.grant(role, perm)
    system_repo = system_repo_cls()
    manager = UserManager(SqliteUserRepository("sqlite:///:memory:")) if user_manager is None else user_manager
    user = None
    if user_roles is not None:
        user = manager.create_user(
            UserCreate(username=username, email=f"{username}@example.com", password="correct-horse-1", roles=user_roles)
        )
    service = service_cls(
        role_repo_cls(),
        grant_repo,
        system_repo,
        manager,
        session_lookup=session_lookup,
        catalog=catalog,
    )
    return service, manager, user, grant_repo


def _create_admin_pair(manager, first: str, second: str) -> None:
    """Create a second admin so deactivating/deleting the first does not trip the last-admin guard."""
    manager.create_user(
        UserCreate(username=second, email=f"{second}@example.com", password="correct-horse-1", roles=["admin"])
    )


def test_malformed_key_denied() -> None:
    """EDGE-001: a check with a malformed permission key denies (malformed_permission)."""
    from backend.permissions import (
        MemoryGrantRepository,
        MemoryRoleRepository,
        MemorySystemPrincipalRepository,
        PermissionCatalog,
        PermissionDeniedError,
        PermissionService,
    )

    service, _, user, _ = _build(
        PermissionService, MemoryRoleRepository, MemoryGrantRepository, MemorySystemPrincipalRepository, PermissionCatalog,
        user_roles=["user"],
    )
    for malformed in ("no-dot", "UPPER.case", "a.b.c"):
        assert service.has_permission(user.id, malformed) is False
        try:
            service.require_permission(user.id, malformed)
            raise AssertionError("expected PermissionDeniedError")
        except PermissionDeniedError as exc:
            assert exc.reason == "malformed_permission"


def test_unknown_permission_denied() -> None:
    """EDGE-002: a check with an unknown permission (valid key, not in the catalog) denies
    (unknown_permission)."""
    from backend.permissions import (
        MemoryGrantRepository,
        MemoryRoleRepository,
        MemorySystemPrincipalRepository,
        PermissionCatalog,
        PermissionDeniedError,
        PermissionService,
    )

    service, _, user, _ = _build(
        PermissionService, MemoryRoleRepository, MemoryGrantRepository, MemorySystemPrincipalRepository, PermissionCatalog,
        user_roles=["user"],
    )
    unknown = "mail.not_in_catalog"
    assert service.has_permission(user.id, unknown) is False
    try:
        service.require_permission(user.id, unknown)
        raise AssertionError("expected PermissionDeniedError")
    except PermissionDeniedError as exc:
        assert exc.reason == "unknown_permission"


def test_unknown_user_denied() -> None:
    """EDGE-003: a check with an unknown user denies (unknown_user)."""
    from backend.permissions import (
        MemoryGrantRepository,
        MemoryRoleRepository,
        MemorySystemPrincipalRepository,
        PermissionCatalog,
        PermissionDeniedError,
        PermissionService,
    )

    service, _, _, _ = _build(
        PermissionService, MemoryRoleRepository, MemoryGrantRepository, MemorySystemPrincipalRepository, PermissionCatalog,
        user_roles=["user"],
    )
    unknown_id = uuid4()
    assert service.has_permission(unknown_id, "mail.send_email") is False
    try:
        service.require_permission(unknown_id, "mail.send_email")
        raise AssertionError("expected PermissionDeniedError")
    except PermissionDeniedError as exc:
        assert exc.reason == "unknown_user"


def test_inactive_user_denied() -> None:
    """EDGE-004: a check with an inactive user (even with ``admin``) denies (inactive_user)."""
    from backend.permissions import (
        MemoryGrantRepository,
        MemoryRoleRepository,
        MemorySystemPrincipalRepository,
        PermissionCatalog,
        PermissionDeniedError,
        PermissionService,
    )

    service, manager, user, _ = _build(
        PermissionService, MemoryRoleRepository, MemoryGrantRepository, MemorySystemPrincipalRepository, PermissionCatalog,
        user_roles=["admin"], username="admin1",
    )
    _create_admin_pair(manager, "admin1", "admin2")
    manager.deactivate_user(user.id)
    assert service.has_permission(user.id, "mail.send_email") is False
    try:
        service.require_permission(user.id, "mail.send_email")
        raise AssertionError("expected PermissionDeniedError")
    except PermissionDeniedError as exc:
        assert exc.reason == "inactive_user"


def test_revoked_expired_token_denied() -> None:
    """EDGE-005: a check with a revoked or expired session token denies (invalid_session)."""
    from backend.permissions import (
        MemoryGrantRepository,
        MemoryRoleRepository,
        MemorySystemPrincipalRepository,
        PermissionCatalog,
        PermissionDeniedError,
        PermissionService,
    )

    now = datetime.now(UTC)
    lookup = _FakeSessionLookup()
    service, _, user, _ = _build(
        PermissionService, MemoryRoleRepository, MemoryGrantRepository, MemorySystemPrincipalRepository, PermissionCatalog,
        user_roles=["admin"], session_lookup=lookup,
    )
    # A revoked token denies.
    lookup.add("revoked", _SessionRecord(user.id, now + timedelta(hours=1), True))
    assert service.has_permission(user.id, "mail.send_email", session_token="revoked") is False
    try:
        service.require_permission(user.id, "mail.send_email", session_token="revoked")
        raise AssertionError("expected PermissionDeniedError")
    except PermissionDeniedError as exc:
        assert exc.reason == "invalid_session"
    # An expired token denies.
    lookup.add("expired", _SessionRecord(user.id, now - timedelta(hours=1), False))
    assert service.has_permission(user.id, "mail.send_email", session_token="expired") is False
    try:
        service.require_permission(user.id, "mail.send_email", session_token="expired")
        raise AssertionError("expected PermissionDeniedError")
    except PermissionDeniedError as exc:
        assert exc.reason == "invalid_session"


def test_mismatched_token_denied() -> None:
    """EDGE-006: a check with a token belonging to a different user denies
    (session_principal_mismatch)."""
    from backend.permissions import (
        MemoryGrantRepository,
        MemoryRoleRepository,
        MemorySystemPrincipalRepository,
        PermissionCatalog,
        PermissionDeniedError,
        PermissionService,
    )

    now = datetime.now(UTC)
    lookup = _FakeSessionLookup()
    service, manager, user, _ = _build(
        PermissionService, MemoryRoleRepository, MemoryGrantRepository, MemorySystemPrincipalRepository, PermissionCatalog,
        user_roles=["admin"], session_lookup=lookup,
    )
    other = manager.create_user(
        UserCreate(username="u2", email="u2@example.com", password="correct-horse-1", roles=["admin"])
    )
    lookup.add("mismatch", _SessionRecord(other.id, now + timedelta(hours=1), False))
    assert service.has_permission(user.id, "mail.send_email", session_token="mismatch") is False
    try:
        service.require_permission(user.id, "mail.send_email", session_token="mismatch")
        raise AssertionError("expected PermissionDeniedError")
    except PermissionDeniedError as exc:
        assert exc.reason == "session_principal_mismatch"


def test_unavailable_session_lookup_denied() -> None:
    """EDGE-007: a check with a token when the session lookup is unavailable (``None`` or
    raises) denies (storage_error)."""
    from backend.permissions import (
        MemoryGrantRepository,
        MemoryRoleRepository,
        MemorySystemPrincipalRepository,
        PermissionCatalog,
        PermissionDeniedError,
        PermissionService,
    )

    # Case A: the session lookup is ``None``.
    service, _, user, _ = _build(
        PermissionService, MemoryRoleRepository, MemoryGrantRepository, MemorySystemPrincipalRepository, PermissionCatalog,
        user_roles=["admin"],
    )
    assert service.has_permission(user.id, "mail.send_email", session_token="tok") is False
    try:
        service.require_permission(user.id, "mail.send_email", session_token="tok")
        raise AssertionError("expected PermissionDeniedError")
    except PermissionDeniedError as exc:
        assert exc.reason == "storage_error"
    # Case B: the session lookup raises.
    service2, _, user2, _ = _build(
        PermissionService, MemoryRoleRepository, MemoryGrantRepository, MemorySystemPrincipalRepository, PermissionCatalog,
        user_roles=["admin"], session_lookup=_RaisingSessionLookup(),
    )
    assert service2.has_permission(user2.id, "mail.send_email", session_token="tok") is False
    try:
        service2.require_permission(user2.id, "mail.send_email", session_token="tok")
        raise AssertionError("expected PermissionDeniedError")
    except PermissionDeniedError as exc:
        assert exc.reason == "storage_error"


def test_user_deleted_concurrent_denied() -> None:
    """EDGE-009: a user deleted between the caller's lookup and the check (concurrent)
    denies (unknown_user) — the live lookup re-resolves."""
    from backend.permissions import (
        MemoryGrantRepository,
        MemoryRoleRepository,
        MemorySystemPrincipalRepository,
        PermissionCatalog,
        PermissionDeniedError,
        PermissionService,
    )

    service, manager, user, _ = _build(
        PermissionService, MemoryRoleRepository, MemoryGrantRepository, MemorySystemPrincipalRepository, PermissionCatalog,
        user_roles=["admin"], username="admin1",
    )
    _create_admin_pair(manager, "admin1", "admin2")
    manager.delete_user(user.id)
    assert service.has_permission(user.id, "mail.send_email") is False
    try:
        service.require_permission(user.id, "mail.send_email")
        raise AssertionError("expected PermissionDeniedError")
    except PermissionDeniedError as exc:
        assert exc.reason == "unknown_user"


def test_lookup_raises_denied() -> None:
    """EDGE-011: a check when the user lookup raises (storage failure) denies
    (storage_error), never a crash."""
    from backend.permissions import (
        MemoryGrantRepository,
        MemoryRoleRepository,
        MemorySystemPrincipalRepository,
        PermissionCatalog,
        PermissionDeniedError,
        PermissionService,
    )

    service, _, _, _ = _build(
        PermissionService, MemoryRoleRepository, MemoryGrantRepository, MemorySystemPrincipalRepository, PermissionCatalog,
        user_manager=_RaisingUserManager(),
    )
    user_id = uuid4()
    assert service.has_permission(user_id, "mail.send_email") is False
    try:
        service.require_permission(user_id, "mail.send_email")
        raise AssertionError("expected PermissionDeniedError")
    except PermissionDeniedError as exc:
        assert exc.reason == "storage_error"


def test_set_system_unknown_permission() -> None:
    """EDGE-020: ``set_system_permissions`` with an unknown permission raises
    ``UnknownPermissionError``."""
    from backend.permissions import (
        MemoryGrantRepository,
        MemoryRoleRepository,
        MemorySystemPrincipalRepository,
        PermissionCatalog,
        PermissionService,
        UnknownPermissionError,
    )

    service, _, _, _ = _build(
        PermissionService, MemoryRoleRepository, MemoryGrantRepository, MemorySystemPrincipalRepository, PermissionCatalog,
        user_roles=["user"],
    )
    try:
        service.set_system_permissions({"mail.not_in_catalog"})
        raise AssertionError("expected UnknownPermissionError")
    except UnknownPermissionError:
        pass


def test_set_system_wildcard_allowed() -> None:
    """EDGE-021: ``set_system_permissions`` with a feature wildcard (``mail.*``) is allowed
    and matches the mail actions on system checks."""
    from backend.permissions import (
        MemoryGrantRepository,
        MemoryRoleRepository,
        MemorySystemPrincipalRepository,
        PermissionCatalog,
        PermissionService,
    )

    service, _, _, _ = _build(
        PermissionService, MemoryRoleRepository, MemoryGrantRepository, MemorySystemPrincipalRepository, PermissionCatalog,
        user_roles=["user"],
    )
    # A feature wildcard is allowed (no error).
    service.set_system_permissions({"mail.*"})
    # It matches the mail actions on system checks.
    assert service.has_permission(None, "mail.send_email") is True
    assert service.has_permission(None, "mail.send_password_reset_email") is True


def test_token_deleted_user_denied() -> None:
    """EDGE-024: a session token for a user deleted after login denies (unknown_user) — the
    user lookup precedes session validation."""
    from backend.permissions import (
        MemoryGrantRepository,
        MemoryRoleRepository,
        MemorySystemPrincipalRepository,
        PermissionCatalog,
        PermissionDeniedError,
        PermissionService,
    )

    now = datetime.now(UTC)
    lookup = _FakeSessionLookup()
    service, manager, user, _ = _build(
        PermissionService, MemoryRoleRepository, MemoryGrantRepository, MemorySystemPrincipalRepository, PermissionCatalog,
        user_roles=["admin"], username="admin1", session_lookup=lookup,
    )
    _create_admin_pair(manager, "admin1", "admin2")
    # A valid session token for the user (added while the user exists).
    lookup.add("tok", _SessionRecord(user.id, now + timedelta(hours=1), False))
    # The user is deleted after login.
    manager.delete_user(user.id)
    # The user lookup precedes session validation: the user is absent -> unknown_user
    # (not invalid_session, even though the token is still "valid" in the lookup).
    assert service.has_permission(user.id, "mail.send_email", session_token="tok") is False
    try:
        service.require_permission(user.id, "mail.send_email", session_token="tok")
        raise AssertionError("expected PermissionDeniedError")
    except PermissionDeniedError as exc:
        assert exc.reason == "unknown_user"


def test_expired_session_denied() -> None:
    """EDGE-025: a check with a token for a user whose session is expired denies
    (invalid_session) — even for a granted permission."""
    from backend.permissions import (
        MemoryGrantRepository,
        MemoryRoleRepository,
        MemorySystemPrincipalRepository,
        PermissionCatalog,
        PermissionDeniedError,
        PermissionService,
    )

    now = datetime.now(UTC)
    lookup = _FakeSessionLookup()
    service, _, user, _ = _build(
        PermissionService, MemoryRoleRepository, MemoryGrantRepository, MemorySystemPrincipalRepository, PermissionCatalog,
        user_roles=["admin"], session_lookup=lookup,
    )
    # An expired session for a granted permission (the admin wildcard) still denies.
    lookup.add("expired", _SessionRecord(user.id, now - timedelta(hours=1), False))
    assert service.has_permission(user.id, "mail.send_email", session_token="expired") is False
    try:
        service.require_permission(user.id, "mail.send_email", session_token="expired")
        raise AssertionError("expected PermissionDeniedError")
    except PermissionDeniedError as exc:
        assert exc.reason == "invalid_session"
