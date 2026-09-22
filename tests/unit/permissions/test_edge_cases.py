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
import threading
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


def _build_role(
    service_cls,
    role_repo_cls,
    grant_repo_cls,
    system_repo_cls,
    catalog_cls,
    *,
    user_roles=None,
    username="u1",
    grants=None,
    role_store=None,
    seed_roles=(),
):
    """Construct a ``PermissionService`` over in-memory repositories for the role management edge cases.

    Returns ``(service, manager, user, role_repo, grant_repo)``. ``user_roles`` of
    ``None`` creates no user; ``seed_roles`` is an iterable of ``(role, is_builtin)``
    pairs added to the role repository before the service is constructed; ``role_store``
    overrides the user manager's role store (needed when the user holds a
    non-built-in role).
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
    role_repo = role_repo_cls()
    for role, is_builtin in seed_roles:
        role_repo.add(role, None, is_builtin)
    system_repo = system_repo_cls()
    repo = SqliteUserRepository("sqlite:///:memory:")
    manager = UserManager(repo) if role_store is None else UserManager(repo, role_store=role_store)
    user = None
    if user_roles is not None:
        user = manager.create_user(
            UserCreate(username=username, email=f"{username}@example.com", password="correct-horse-1", roles=user_roles)
        )
    service = service_cls(
        role_repo,
        grant_repo,
        system_repo,
        manager,
        catalog=catalog,
    )
    return service, manager, user, role_repo, grant_repo


# --- EDGE-008: a role with no permission mapping has zero permissions ---


def test_role_no_mapping_zero_permissions() -> None:
    """EDGE-008: a role with no permission mapping — zero permissions: all checks
    for its holders deny (reason ``unauthorized``)."""
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
    for perm in ("mail.send_email", "mail.send_password_reset_email"):
        assert service.has_permission(user.id, perm) is False
        try:
            service.require_permission(user.id, perm)
            raise AssertionError("expected PermissionDeniedError")
        except PermissionDeniedError as exc:
            assert exc.reason == "unauthorized"


# --- EDGE-010: concurrent checks and role changes are thread-safe ---


def test_concurrent_thread_safe() -> None:
    """EDGE-010: concurrent checks and role changes from multiple threads are
    thread-safe; no partial state."""
    from backend.permissions import (
        MemoryGrantRepository,
        MemoryRoleRepository,
        MemorySystemPrincipalRepository,
        PermissionCatalog,
        PermissionService,
    )

    service, _, user, _ = _build(
        PermissionService, MemoryRoleRepository, MemoryGrantRepository, MemorySystemPrincipalRepository, PermissionCatalog,
        user_roles=["user"],
    )
    perm = "mail.send_email"
    errors: list[BaseException] = []

    def toggler() -> None:
        try:
            for i in range(15):
                if i % 2 == 0:
                    service.grant_permission("user", perm)
                else:
                    service.revoke_permission("user", perm)
        except BaseException as exc:
            errors.append(exc)

    def checker() -> None:
        try:
            for _ in range(15):
                service.has_permission(user.id, perm)
        except BaseException as exc:
            errors.append(exc)

    threads = [threading.Thread(target=toggler), threading.Thread(target=toggler), threading.Thread(target=checker)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors, f"unexpected exceptions: {errors}"
    # No partial state: the final check is consistent with the final grant state.
    final_grants = service.get_role_permissions("user")
    assert final_grants <= frozenset({perm})
    assert service.has_permission(user.id, perm) is (perm in final_grants)


# --- EDGE-012: delete_role of a built-in role is protected ---


def test_delete_builtin_role_protected() -> None:
    """EDGE-012: ``delete_role`` of a built-in role raises ``RoleProtectedError``."""
    from backend.permissions import (
        MemoryGrantRepository,
        MemoryRoleRepository,
        MemorySystemPrincipalRepository,
        PermissionCatalog,
        PermissionService,
        RoleProtectedError,
    )

    service, _, _, _, _ = _build_role(
        PermissionService, MemoryRoleRepository, MemoryGrantRepository, MemorySystemPrincipalRepository, PermissionCatalog,
        seed_roles=[("admin", True), ("user", True)],
    )
    for builtin in ("admin", "user"):
        try:
            service.delete_role(builtin)
            raise AssertionError(f"expected RoleProtectedError for {builtin}")
        except RoleProtectedError as exc:
            assert exc.role == builtin


# --- EDGE-013: delete_role of a role assigned to any user ---


def test_delete_in_use_role() -> None:
    """EDGE-013: ``delete_role`` of a role assigned to any user raises
    ``RoleInUseError``."""
    from backend.permissions import (
        MemoryGrantRepository,
        MemoryRoleRepository,
        MemorySystemPrincipalRepository,
        PermissionCatalog,
        PermissionService,
        RoleInUseError,
    )

    from backend.usermanagement import StaticRoleStore

    service, _, _, _, _ = _build_role(
        PermissionService, MemoryRoleRepository, MemoryGrantRepository, MemorySystemPrincipalRepository, PermissionCatalog,
        user_roles=["editor"],
        role_store=StaticRoleStore(("admin", "user", "editor")),
        seed_roles=[("editor", False)],
    )
    try:
        service.delete_role("editor")
        raise AssertionError("expected RoleInUseError")
    except RoleInUseError as exc:
        assert exc.role == "editor"


# --- EDGE-014: create_role of a duplicate role ---


def test_create_duplicate_role() -> None:
    """EDGE-014: ``create_role`` of a duplicate role raises
    ``RoleAlreadyExistsError``."""
    from backend.permissions import (
        MemoryGrantRepository,
        MemoryRoleRepository,
        MemorySystemPrincipalRepository,
        PermissionCatalog,
        PermissionService,
        RoleAlreadyExistsError,
    )

    service, _, _, _, _ = _build_role(
        PermissionService, MemoryRoleRepository, MemoryGrantRepository, MemorySystemPrincipalRepository, PermissionCatalog,
    )
    service.create_role("editor")
    try:
        service.create_role("editor")
        raise AssertionError("expected RoleAlreadyExistsError")
    except RoleAlreadyExistsError as exc:
        assert exc.role == "editor"


# --- EDGE-015: create_role with a malformed name ---


def test_create_malformed_name() -> None:
    """EDGE-015: ``create_role`` with a malformed name (uppercase, > 32 chars)
    raises ``ValueError``."""
    from backend.permissions import (
        MemoryGrantRepository,
        MemoryRoleRepository,
        MemorySystemPrincipalRepository,
        PermissionCatalog,
        PermissionService,
    )

    service, _, _, _, _ = _build_role(
        PermissionService, MemoryRoleRepository, MemoryGrantRepository, MemorySystemPrincipalRepository, PermissionCatalog,
    )
    for malformed in ("Editor", "a" * 33):
        try:
            service.create_role(malformed)
            raise AssertionError(f"expected ValueError for {malformed!r}")
        except ValueError:
            pass


# --- EDGE-016: grant_permission of an unknown permission ---


def test_grant_unknown_permission() -> None:
    """EDGE-016: ``grant_permission`` of an unknown permission raises
    ``UnknownPermissionError``."""
    from backend.permissions import (
        MemoryGrantRepository,
        MemoryRoleRepository,
        MemorySystemPrincipalRepository,
        PermissionCatalog,
        PermissionService,
        UnknownPermissionError,
    )

    service, _, _, _, _ = _build_role(
        PermissionService, MemoryRoleRepository, MemoryGrantRepository, MemorySystemPrincipalRepository, PermissionCatalog,
        seed_roles=[("user", True)],
    )
    try:
        service.grant_permission("user", "reports.export")
        raise AssertionError("expected UnknownPermissionError")
    except UnknownPermissionError as exc:
        assert exc.permission == "reports.export"


# --- EDGE-017: operations on an unknown role ---


def test_unknown_role_operations() -> None:
    """EDGE-017: ``grant_permission`` / ``revoke_permission`` /
    ``get_role_permissions`` of an unknown role raise ``RoleNotFoundError``."""
    from backend.permissions import (
        MemoryGrantRepository,
        MemoryRoleRepository,
        MemorySystemPrincipalRepository,
        PermissionCatalog,
        PermissionService,
        RoleNotFoundError,
    )

    service, _, _, _, _ = _build_role(
        PermissionService, MemoryRoleRepository, MemoryGrantRepository, MemorySystemPrincipalRepository, PermissionCatalog,
    )
    for operation in (
        lambda: service.grant_permission("ghost", "mail.send_email"),
        lambda: service.revoke_permission("ghost", "mail.send_email"),
        lambda: service.get_role_permissions("ghost"),
    ):
        try:
            operation()
            raise AssertionError("expected RoleNotFoundError")
        except RoleNotFoundError as exc:
            assert exc.role == "ghost"


# --- EDGE-018: revoke_permission of an absent grant is an idempotent no-op ---


def test_revoke_absent_idempotent() -> None:
    """EDGE-018: ``revoke_permission`` of an absent grant is an idempotent no-op."""
    from backend.permissions import (
        MemoryGrantRepository,
        MemoryRoleRepository,
        MemorySystemPrincipalRepository,
        PermissionCatalog,
        PermissionService,
    )

    service, _, _, _, _ = _build_role(
        PermissionService, MemoryRoleRepository, MemoryGrantRepository, MemorySystemPrincipalRepository, PermissionCatalog,
        seed_roles=[("user", True)],
    )
    # Revoking a grant that was never made is a no-op (no error).
    service.revoke_permission("user", "mail.send_email")
    service.revoke_permission("user", "mail.send_email")
    assert "mail.send_email" not in service.get_role_permissions("user")


# --- EDGE-019: grant_permission of an already-granted permission is idempotent ---


def test_grant_existing_idempotent() -> None:
    """EDGE-019: ``grant_permission`` of an already-granted permission is
    idempotent (no error, no duplicate row)."""
    from backend.permissions import (
        MemoryGrantRepository,
        MemoryRoleRepository,
        MemorySystemPrincipalRepository,
        PermissionCatalog,
        PermissionService,
    )

    service, _, _, _, grant_repo = _build_role(
        PermissionService, MemoryRoleRepository, MemoryGrantRepository, MemorySystemPrincipalRepository, PermissionCatalog,
        seed_roles=[("user", True)],
    )
    perm = "mail.send_email"
    service.grant_permission("user", perm)
    service.grant_permission("user", perm)  # idempotent: no error
    # The permission is present...
    assert perm in service.get_role_permissions("user")
    # ...and stored exactly once (no duplicate row).
    rows = [(row.role, row.permission) for row in grant_repo.list_all()]
    assert rows.count(("user", perm)) == 1


# --- EDGE-026: an assignment pass-through with an unknown role ---


def test_assignment_unknown_role() -> None:
    """EDGE-026: an assignment pass-through with an unknown role raises
    ``RoleNotFoundError`` (the service validates against the role store before
    delegation)."""
    from backend.permissions import (
        MemoryGrantRepository,
        MemoryRoleRepository,
        MemorySystemPrincipalRepository,
        PermissionCatalog,
        PermissionService,
        RoleNotFoundError,
    )

    service, manager, user, _, _ = _build_role(
        PermissionService, MemoryRoleRepository, MemoryGrantRepository, MemorySystemPrincipalRepository, PermissionCatalog,
        user_roles=["user"],
    )
    unknown = "nonexistent"
    for operation in (
        lambda: service.assign_role(user.id, unknown),
        lambda: service.add_role(user.id, unknown),
        lambda: service.remove_role(user.id, unknown),
        lambda: service.set_roles(user.id, [unknown]),
    ):
        try:
            operation()
            raise AssertionError("expected RoleNotFoundError")
        except RoleNotFoundError:
            pass
    # The user's roles are unchanged (no partial mutation).
    assert manager.get_user(user.id).roles == ["user"]
