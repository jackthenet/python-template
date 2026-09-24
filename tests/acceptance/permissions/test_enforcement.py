"""Acceptance tests for the permissions feature's enforcement plumbing (docs/specs/user-roles-permissions.md).

Covers AC-032 (REQ-025): the Principal model — ``Principal()`` is the system
principal, and construction sets the fields.

Covers AC-031 (REQ-024): standalone mode — a service constructed without an
injected permission checker performs no check (open, as today).

Covers AC-029 (REQ-024): filemanagement enforcement wiring — a ``FileService``
with an injected permission checker denies ``upload`` without
``filemanagement.upload`` (a ``PermissionDeniedError`` is raised, nothing is
written) and proceeds with it.

These tests verify externally observable behavior only. The ``backend.shared``
and ``backend.permissions`` imports are deferred into the test bodies so the
module collects cleanly before the feature is implemented (RED).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
from uuid import uuid4

import pytest
from filemanagement_test_helpers import db_url, isolated_registry, text_bytes

from backend.filemanagement import FileService, InMemoryStorageBackend, SqliteFileRepository
from backend.usermanagement import SqliteUserRepository, UserCreate, UserManager


class _FakePermissionChecker:
    """A structural ``PermissionChecker`` (spec D14) that records the checks it receives.

    Mimics the real checker's observable behavior: ``require_permission`` raises
    ``PermissionDeniedError`` on denial (the real error — deferred import) and
    ``has_permission`` reports the decision. Only this test double imports
    ``backend.permissions``; the feature under test never does (ADR-070).
    """

    def __init__(self, deny: bool) -> None:
        self.deny = deny
        self.calls: list[tuple[Any, str, Any]] = []

    def require_permission(self, user_id: Any, permission: str, session_token: Any = None) -> None:
        self.calls.append((user_id, permission, session_token))
        if self.deny:
            from backend.permissions.errors import PermissionDeniedError  # deferred: RED

            raise PermissionDeniedError(user_id=user_id, permission=permission, reason="unauthorized")

    def has_permission(self, user_id: Any, permission: str, session_token: Any = None) -> bool:
        return not self.deny


def _build_file_service(tmp_path: Path, checker: _FakePermissionChecker) -> FileService:
    """Construct a ``FileService`` over SQLite + in-memory storage with the checker injected."""
    return FileService(
        SqliteFileRepository(db_url(tmp_path)),
        backend=InMemoryStorageBackend(),
        event_bus=None,
        settings_registry=isolated_registry(),
        permission_service=checker,
    )


def test_principal_defaults_and_fields() -> None:
    """AC-032 / REQ-025: ``Principal()`` is the system principal; construction sets the fields.

    Given ``Principal()``, when it is inspected, then ``user_id=None`` and
    ``session_token=None`` (the system principal). Given
    ``Principal(user_id=u, session_token=t)``, when it is inspected, then the
    fields are set.
    """
    from backend.shared import Principal

    # Principal() is the system principal: both fields default to None.
    system = Principal()
    assert system.user_id is None
    assert system.session_token is None

    # Each field defaults independently (REQ-025 signature).
    partial = Principal(user_id=uuid4())
    assert partial.session_token is None

    # Principal(user_id=u, session_token=t) sets the fields.
    user_id = uuid4()
    token = "session-token"
    principal = Principal(user_id=user_id, session_token=token)
    assert principal.user_id == user_id
    assert principal.session_token == token


def test_standalone_mode_no_check() -> None:
    """AC-031 / REQ-024: standalone mode (no checker) performs no check (open, as today).

    Given a ``UserManager`` constructed without an injected permission checker
    (standalone mode), when an enforced method is called (with an explicit
    principal that holds no permissions), then no check is performed: the
    operation proceeds, as today.
    """
    from backend.shared import Principal

    repo = SqliteUserRepository("sqlite:///:memory:")
    manager = UserManager(repo)  # standalone: no permission checker injected

    # An enforced method called with an explicit principal (a user without any
    # permission) performs no check in standalone mode: the operation proceeds.
    user = manager.create_user(
        UserCreate(username="alice", email="alice@example.com", password="correct-horse-1", roles=["user"]),
        principal=Principal(user_id=uuid4(), session_token="standalone-session"),
    )
    assert user.username == "alice"

    # A second enforced method is likewise open in standalone mode (no check).
    read = manager.get_user(user.id, principal=Principal(user_id=uuid4(), session_token="standalone-session"))
    assert read.id == user.id


def test_enforced_method_denies_without_permission(tmp_path: Path) -> None:
    """AC-029 / REQ-024: an enforced FileService method denies without the permission, proceeds with it.

    Given a ``FileService`` with an injected permission checker, when ``upload``
    is called with a principal lacking ``filemanagement.upload``, then a
    ``PermissionDeniedError`` is raised (and nothing is written); when it is
    called with a principal holding it, then the upload proceeds.
    """
    from backend.permissions.errors import PermissionDeniedError  # deferred: RED
    from backend.shared import Principal  # deferred: RED

    user_id = uuid4()
    session_token = "upload-session"
    principal = Principal(user_id=user_id, session_token=session_token)
    payload = text_bytes(256)

    # --- deny: a principal lacking filemanagement.upload is denied (AC-029) ---
    denier = _FakePermissionChecker(deny=True)
    service = _build_file_service(tmp_path, denier)
    with pytest.raises(PermissionDeniedError):
        service.upload(payload, principal=principal)
    # The check evaluated the principal against the filemanagement.upload key,
    # and the denial happened at entry: nothing was written.
    assert denier.calls == [(user_id, "filemanagement.upload", session_token)]
    assert service.list_files() == []

    # --- allow: a principal holding filemanagement.upload proceeds (AC-029) ---
    allow_checker = _FakePermissionChecker(deny=False)
    service = _build_file_service(tmp_path, allow_checker)
    record = service.upload(payload, principal=principal)
    assert record.key
    assert service.download(record.key) == payload
    assert allow_checker.calls == [(user_id, "filemanagement.upload", session_token)]


# --- AC-030: the exempt login performs no check on itself ---

# The bootstrap system set (spec Section 3, D10): the default system principal
# permission set. It covers the internal login flow (password verification +
# user read) so login stays reachable for zero-permission users.
BOOTSTRAP_SYSTEM_PERMISSIONS: frozenset[str] = frozenset({
    "usermanagement.get_user",
    "usermanagement.verify_password",
    "usermanagement.change_password",
    "settings.register",
    "settings.register_feature",
    "mail.send_email",
    "mail.send_password_reset_email",
    "mail.send_email_verification_email",
    "sessionmanagement.cleanup_expired",
})


class _SpyPermissionChecker:
    """A structural PermissionChecker that records every check and delegates to the real service.

    The composition-root wiring (the shared PermissionService injected into the
    services) is observable through the recorded checks: who was checked
    (user_id / session_token) and against which permission key.
    """

    def __init__(self, inner: Any) -> None:
        self._inner = inner
        self.calls: list[tuple[Any, str, Any]] = []

    def require_permission(self, user_id: Any, permission: str, session_token: Any = None) -> None:
        self.calls.append((user_id, permission, session_token))
        self._inner.require_permission(user_id, permission, session_token)

    def has_permission(self, user_id: Any, permission: str, session_token: Any = None) -> bool:
        return self._inner.has_permission(user_id, permission, session_token)


class _LazyUserManager:
    """A structural UserManager indirection that resolves the real manager after both sides exist.

    Breaks the construction cycle of the composition-root wiring: the
    PermissionService holds the (lazy) manager for its live user lookup, and
    the manager holds the shared PermissionService as its injected checker
    (ADR-069).
    """

    def __init__(self) -> None:
        self._manager = None

    def set_manager(self, manager: Any) -> None:
        self._manager = manager

    def __getattr__(self, name: str) -> Any:
        return getattr(self._manager, name)


def test_exempt_login_no_check(tmp_path: Path) -> None:
    """AC-030 / REQ-024: the exempt login performs no check on itself; the flow succeeds
    for a zero-permission user (the internal calls are evaluated against the
    bootstrap system set).

    Given the exempt operation ``authentication.login``, when it is called,
    then no permission check is performed on ``login`` itself, and the login
    flow succeeds for a user with zero permissions (the internal
    user-management/mail calls are evaluated against the bootstrap system set).
    """
    from authentication_test_helpers import FakeWebAuthnProvider, db_url
    from backend.permissions import (
        MemoryGrantRepository,
        MemoryRoleRepository,
        MemorySystemPrincipalRepository,
        PermissionCatalog,
        PermissionService,
    )

    from backend.authentication import (
        AuthService,
        LoginRequest,
        SqlitePasswordResetRepository,
        SqliteSessionRepository,
        SqliteWebAuthnCredentialRepository,
    )

    # A zero-permission user (the 'user' role starts with zero permissions,
    # REQ-011), created before the enforcement wiring (standalone mode).
    user_repo = SqliteUserRepository(db_url(tmp_path, "users.db"))
    standalone = UserManager(user_repo)
    user = standalone.create_user(
        UserCreate(username="carol", email="carol@example.com", password="carol-password-1", roles=["user"])
    )

    # The shared PermissionService (the composition-root wiring): its system set
    # is the bootstrap set (the internal login calls are covered by it).
    catalog = PermissionCatalog()
    catalog.register_feature(
        "usermanagement",
        {
            "usermanagement.verify_password": "Verify a user's password",
            "usermanagement.get_user": "Read a user by id",
        },
    )
    system_repo = MemorySystemPrincipalRepository()
    system_repo.set_permissions(BOOTSTRAP_SYSTEM_PERMISSIONS)

    lazy_manager = _LazyUserManager()
    service = PermissionService(
        MemoryRoleRepository(),
        MemoryGrantRepository(),
        system_repo,
        lazy_manager,
        catalog=catalog,
    )

    # The shared checker (spied so every check the wired services perform is
    # observable) is injected into the UserManager (the internal calls) and
    # the AuthService (the login flow) — the same instance, as at the
    # composition root.
    spy = _SpyPermissionChecker(service)
    lazy_manager.set_manager(UserManager(user_repo, permission_service=spy))
    auth_url = db_url(tmp_path, "auth.db")
    auth = AuthService(
        lazy_manager,
        user_repo,
        SqliteSessionRepository(auth_url),
        SqlitePasswordResetRepository(auth_url),
        SqliteWebAuthnCredentialRepository(auth_url),
        webauthn_provider=FakeWebAuthnProvider(),
        permission_service=spy,
    )

    # The login flow succeeds for the zero-permission user.
    result = auth.login(LoginRequest(identifier="carol", password="carol-password-1"))
    assert result.token
    assert result.user.id == user.id
    assert result.user.roles == ["user"]

    # No permission check is performed on login itself (the exempt set).
    assert all(permission != "authentication.login" for _, permission, _ in spy.calls)

    # The internal user-management calls (password verification + user read)
    # are evaluated as the system principal (the default principal) against
    # the bootstrap system set, which covers them (the login succeeded).
    assert (None, "usermanagement.verify_password", None) in spy.calls
    assert (None, "usermanagement.get_user", None) in spy.calls
