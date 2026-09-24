"""Acceptance tests for the authentication enforcement wiring (user-roles-permissions, REQ-024).

Covers T-009: every public ``AuthService`` method takes a trailing ``principal``
parameter (default = the system principal, REQ-025); the enforced methods
(``begin_passkey_registration``, ``complete_passkey_registration``, ``list_passkeys``,
``delete_passkey``) enforce ``require_permission`` at entry (a denial propagates to
the caller, an allow proceeds, the permission key is ``authentication.<method>``);
the exempt set (session-establishment/teardown/introspection operations) is declared
but not enforced (AC-030 / EDGE-023); the constructor gains an optional
``permission_service`` checker (standalone by default, AC-031); and the feature-owned
``feature_actions.register_actions`` declares the 11 authentication catalog actions
(spec Section 3).

These tests verify externally observable behavior only. Per the design constraint
(ADR-071), the test uses a fake ``PermissionChecker`` (structural protocol) — the
feature never imports ``backend.permissions``. The ``backend.shared`` and
``feature_actions`` imports are deferred into the test body so the module collects
cleanly before the feature is implemented (RED).
"""

from __future__ import annotations

import inspect
from pathlib import Path
from typing import Any
from uuid import uuid4

import pytest
from authentication_test_helpers import FakeWebAuthnProvider, db_url

from backend.authentication import (
    AuthService,
    LoginRequest,
    PasskeyLoginBegin,
    PasskeyLoginComplete,
    PasskeyRegistrationBegin,
    PasskeyRegistrationComplete,
    PasswordResetComplete,
    PasswordResetRequest,
    SqlitePasswordResetRepository,
    SqliteSessionRepository,
    SqliteWebAuthnCredentialRepository,
)
from backend.usermanagement import SqliteUserRepository, UserCreate, UserManager

# The spec's authentication catalog (Section 3): 11 declared actions.
ENFORCED_METHODS: tuple[str, ...] = (
    "begin_passkey_registration",
    "complete_passkey_registration",
    "list_passkeys",
    "delete_passkey",
)
EXEMPT_METHODS: tuple[str, ...] = (
    "login",
    "session_info",
    "logout",
    "request_password_reset",
    "complete_password_reset",
    "begin_passkey_login",
    "complete_passkey_login",
)
ALL_METHODS: tuple[str, ...] = ENFORCED_METHODS + EXEMPT_METHODS


class _PermissionDenied(Exception):
    """A test-local denial error (the real one lives in backend.permissions, T-003).

    The wiring contract under test is that a denial raised by the injected checker
    propagates to the caller unchanged.
    """

    def __init__(self, permission: str) -> None:
        super().__init__(f"denied: {permission}")
        self.permission = permission


class _FakePermissionChecker:
    """A structural PermissionChecker that records calls and optionally denies."""

    def __init__(self, deny: bool) -> None:
        self.deny = deny
        self.calls: list[tuple[Any, str, Any]] = []

    def require_permission(self, user_id: Any, permission: str, session_token: Any = None) -> None:
        self.calls.append((user_id, permission, session_token))
        if self.deny:
            raise _PermissionDenied(permission)

    def has_permission(self, user_id: Any, permission: str, session_token: Any = None) -> bool:
        return not self.deny


class _FakeCatalog:
    """A recording stand-in for the permission catalog (structural)."""

    def __init__(self) -> None:
        self.features: dict[str, dict[str, str]] = {}

    def register_feature(self, feature: str, actions: dict[str, str]) -> None:
        self.features[feature] = dict(actions)


def _principal_default(method_name: str) -> Any:
    """Return the trailing ``principal`` parameter's default for a public method.

    Asserts the ADR-071 contract: the last parameter is named ``principal`` and has
    a default (existing positional call sites are unaffected).
    """
    method = getattr(AuthService, method_name)
    params = list(inspect.signature(method).parameters.values())
    assert params, f"AuthService.{method_name} has no parameters"
    last = params[-1]
    assert last.name == "principal", (
        f"AuthService.{method_name}: trailing parameter is {last.name!r}, expected 'principal'"
    )
    assert last.default is not inspect.Parameter.empty, (
        f"AuthService.{method_name}: 'principal' has no default; existing call sites would break"
    )
    return last.default


def _build_service(tmp_path: Path, checker: _FakePermissionChecker) -> AuthService:
    """Construct an ``AuthService`` over SQLite stores with the checker injected."""
    user_repo = SqliteUserRepository(db_url(tmp_path, "users.db"))
    user_manager = UserManager(user_repo)
    auth_url = db_url(tmp_path, "auth.db")
    return AuthService(
        user_manager,
        user_repo,
        SqliteSessionRepository(auth_url),
        SqlitePasswordResetRepository(auth_url),
        SqliteWebAuthnCredentialRepository(auth_url),
        webauthn_provider=FakeWebAuthnProvider(),
        permission_service=checker,
    )


def test_authentication_enforcement_wiring(tmp_path: Path) -> None:
    # --- principal parameter (REQ-024 / ADR-071): all 11 public methods ---
    for name in ALL_METHODS:
        default = _principal_default(name)
        assert getattr(default, "user_id", "MISSING") is None, (
            f"AuthService.{name}: the default principal is not the system principal (user_id must be None)"
        )
        assert getattr(default, "session_token", "MISSING") is None, (
            f"AuthService.{name}: the default principal is not the system principal (session_token must be None)"
        )

    # --- constructor: optional permission_service, standalone by default (AC-031) ---
    ctor_params = inspect.signature(AuthService.__init__).parameters
    assert "permission_service" in ctor_params, "AuthService.__init__ has no 'permission_service' parameter"
    assert ctor_params["permission_service"].default is None, (
        "AuthService.__init__: 'permission_service' must default to None (standalone mode)"
    )

    # --- deny: every enforced method lets the checker's denial propagate to the caller ---
    denier = _FakePermissionChecker(deny=True)
    service = _build_service(tmp_path, denier)
    user_id = uuid4()
    enforced_calls: dict[str, tuple[Any, ...]] = {
        "begin_passkey_registration": (PasskeyRegistrationBegin(user_id=user_id, username="carol"),),
        "complete_passkey_registration": (PasskeyRegistrationComplete(user_id=user_id, response={}),),
        "list_passkeys": (user_id,),
        "delete_passkey": (user_id, "bogus-credential"),
    }
    for name, args in enforced_calls.items():
        with pytest.raises(_PermissionDenied):
            getattr(service, name)(*args)
    assert [call[1] for call in denier.calls] == [f"authentication.{name}" for name in enforced_calls]

    # --- allow: an enforced method proceeds; the default principal is the system principal (EDGE-022) ---
    allow_checker = _FakePermissionChecker(deny=False)
    service = _build_service(tmp_path, allow_checker)
    assert service.list_passkeys(user_id) == []
    assert allow_checker.calls == [(None, "authentication.list_passkeys", None)]

    # --- an explicit principal (user_id + session token) reaches the check (REQ-024) ---
    from backend.shared import Principal  # deferred: collects cleanly before T-001 lands (RED)

    principal = Principal(user_id=user_id, session_token="principal-token")
    explicit_checker = _FakePermissionChecker(deny=False)
    service = _build_service(tmp_path, explicit_checker)
    service.list_passkeys(user_id, principal=principal)
    assert explicit_checker.calls == [(user_id, "authentication.list_passkeys", "principal-token")]

    # --- exempt set (ADR-071): declared but not enforced ---
    # A zero-permission user (the 'user' role starts with zero permissions, REQ-011)
    # must still be able to log in with a denying checker injected (AC-030 / EDGE-023).
    user_repo = SqliteUserRepository(db_url(tmp_path, "users.db"))
    user_manager = UserManager(user_repo)
    user = user_manager.create_user(
        UserCreate(username="carol", email="carol@example.com", password="carol-password-1", roles=["user"])
    )
    login_denier = _FakePermissionChecker(deny=True)
    service = _build_service(tmp_path, login_denier)
    result = service.login(LoginRequest(identifier="carol", password="carol-password-1"))
    assert result.user.id == user.id
    assert login_denier.calls == []  # no permission check on login itself

    # The remaining exempt methods must stay reachable: a call with a denying checker
    # must not raise the sentinel denial (domain errors for the probe arguments are
    # fine — they prove the method body was reached unchecked).
    probes: dict[str, tuple[Any, ...]] = {
        "session_info": ("bogus-token",),
        "logout": (result.token,),
        "request_password_reset": (PasswordResetRequest(email="unknown@example.com"),),
        "complete_password_reset": (PasswordResetComplete(token="bogus", new_password="new-password-1"),),
        "begin_passkey_login": (PasskeyLoginBegin(credential_id="bogus"),),
        "complete_passkey_login": (PasskeyLoginComplete(credential_id="bogus", response={}),),
    }
    for name, args in probes.items():
        try:
            getattr(service, name)(*args)
        except _PermissionDenied:
            pytest.fail(f"exempt method {name} was enforced (the denial propagated)")
        except Exception:
            pass  # a domain error for the probe arguments is not a denial
    assert login_denier.calls == []  # no exempt method performed a check

    # --- feature_actions: the feature declares its 11 catalog actions (REQ-005 / REQ-024) ---
    from backend.authentication.feature_actions import register_actions  # deferred: T-009 artifact (RED)

    catalog = _FakeCatalog()
    register_actions(catalog)
    declared = catalog.features.get("authentication")
    assert declared is not None, "register_actions did not declare the 'authentication' feature"
    expected = {f"authentication.{name}" for name in ALL_METHODS}
    assert set(declared) == expected, (
        f"register_actions declares {sorted(declared)}, expected the 11 authentication actions {sorted(expected)}"
    )
