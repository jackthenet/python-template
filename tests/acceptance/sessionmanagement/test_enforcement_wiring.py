"""Acceptance tests for the sessionmanagement enforcement wiring (user-roles-permissions, REQ-024).

Covers T-013: every public ``SessionService`` method takes a trailing ``principal``
parameter (default = the system principal, REQ-025); all 6 methods are enforced
(the sessionmanagement exempt set is empty, spec Section 3) and enforce
``require_permission`` at entry (a denial propagates to the caller, an allow proceeds,
the permission key is ``sessionmanagement.<method>``); an enforced method called without
an explicit principal is evaluated as the system principal (EDGE-022); the constructor
gains an optional ``permission_service`` checker (standalone by default, AC-031); and
the feature-owned ``feature_actions.register_actions`` declares the 6
sessionmanagement catalog actions (spec Section 3).

The session repository (the reused authentication store: ``get_by_token_hash`` over
SHA-256 hashes) is the real SessionLookup implementation the check uses for session
validation (REQ-017).

These tests verify externally observable behavior only. Per the design constraint
(ADR-071), the test uses a fake ``PermissionChecker`` (structural protocol) — the
feature never imports ``backend.permissions``. The ``backend.shared`` and
``feature_actions`` imports are deferred into the test body so the module collects
cleanly before the feature is implemented (RED).
"""

from __future__ import annotations

import inspect
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

import pytest
from sessionmanagement_test_helpers import db_url, make_session

from backend.authentication import SqliteSessionRepository
from backend.sessionmanagement import SessionService
from backend.settings import SettingsRegistry, YamlValueRepository

# The spec's sessionmanagement catalog (Section 3): all 6 public methods are enforced
# (the sessionmanagement exempt set is empty).
ENFORCED_METHODS: tuple[str, ...] = (
    "list_sessions",
    "revoke_session",
    "logout_all_sessions",
    "logout_other_sessions",
    "revoke_all_sessions",
    "cleanup_expired",
)


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
    method = getattr(SessionService, method_name)
    params = list(inspect.signature(method).parameters.values())
    assert params, f"SessionService.{method_name} has no parameters"
    last = params[-1]
    assert last.name == "principal", (
        f"SessionService.{method_name}: trailing parameter is {last.name!r}, expected 'principal'"
    )
    assert last.default is not inspect.Parameter.empty, (
        f"SessionService.{method_name}: 'principal' has no default; existing call sites would break"
    )
    return last.default


def _isolated_registry() -> SettingsRegistry:
    """A fresh isolated settings registry (temp-dir value repository, house pattern)."""
    return SettingsRegistry(value_repository=YamlValueRepository(tempfile.mkdtemp()))


def _build_service(repository: SqliteSessionRepository, checker: _FakePermissionChecker) -> SessionService:
    """Construct a ``SessionService`` over the given store with the checker injected."""
    return SessionService(
        repository,
        event_bus=None,
        settings_registry=_isolated_registry(),
        permission_service=checker,
    )


def _denial_probes() -> dict[str, tuple[Any, ...]]:
    """Probe arguments for each enforced method (the denial happens at entry, before the body)."""
    return {
        "list_sessions": ("probe-token",),
        "revoke_session": (uuid4(),),
        "logout_all_sessions": ("probe-token",),
        "logout_other_sessions": ("probe-token",),
        "revoke_all_sessions": (uuid4(),),
        "cleanup_expired": (),
    }


def test_sessionmanagement_enforcement_wiring(tmp_path: Path) -> None:
    # --- principal parameter (REQ-024 / ADR-071): all 6 public methods ---
    for name in ENFORCED_METHODS:
        default = _principal_default(name)
        assert getattr(default, "user_id", "MISSING") is None, (
            f"SessionService.{name}: the default principal is not the system principal (user_id must be None)"
        )
        assert getattr(default, "session_token", "MISSING") is None, (
            f"SessionService.{name}: the default principal is not the system principal (session_token must be None)"
        )

    # --- constructor: optional permission_service, standalone by default (AC-031) ---
    ctor_params = inspect.signature(SessionService.__init__).parameters
    assert "permission_service" in ctor_params, "SessionService.__init__ has no 'permission_service' parameter"
    assert ctor_params["permission_service"].default is None, (
        "SessionService.__init__: 'permission_service' must default to None (standalone mode)"
    )

    repository = SqliteSessionRepository(db_url(tmp_path))

    # --- deny: every enforced method lets the checker's denial propagate to the caller ---
    denier = _FakePermissionChecker(deny=True)
    service = _build_service(repository, denier)
    probes = _denial_probes()
    for name, args in probes.items():
        with pytest.raises(_PermissionDenied):
            getattr(service, name)(*args)
    assert [call[1] for call in denier.calls] == [f"sessionmanagement.{name}" for name in probes]

    # --- allow: an enforced method proceeds; the default principal is the system principal (EDGE-022) ---
    allow_checker = _FakePermissionChecker(deny=False)
    service = _build_service(repository, allow_checker)
    allow_user = uuid4()
    row, _ = make_session(repository, allow_user, created_at=datetime.now(UTC))
    count = service.revoke_all_sessions(allow_user)
    assert count == 1
    assert repository.get(row.id).revoked
    assert allow_checker.calls == [(None, "sessionmanagement.revoke_all_sessions", None)]

    # --- an explicit principal (user_id + session token) reaches the check (REQ-024) ---
    from backend.shared import Principal  # deferred: collects cleanly before T-001 lands (RED)

    principal_user = uuid4()
    principal = Principal(user_id=principal_user, session_token="principal-token")
    explicit_checker = _FakePermissionChecker(deny=False)
    service = _build_service(repository, explicit_checker)
    service.revoke_all_sessions(principal_user, principal=principal)
    assert explicit_checker.calls == [(principal_user, "sessionmanagement.revoke_all_sessions", "principal-token")]

    # --- standalone mode (AC-031): a service without a checker performs no check ---
    standalone = SessionService(
        repository,
        event_bus=None,
        settings_registry=_isolated_registry(),
    )
    standalone_user = uuid4()
    row, _ = make_session(repository, standalone_user, created_at=datetime.now(UTC))
    count = standalone.revoke_all_sessions(
        standalone_user,
        principal=Principal(user_id=uuid4(), session_token="standalone-session"),
    )
    assert count == 1
    assert repository.get(row.id).revoked

    # --- feature_actions: the feature declares its 6 catalog actions (REQ-005 / REQ-024) ---
    from backend.sessionmanagement.feature_actions import register_actions  # deferred: T-013 artifact (RED)

    catalog = _FakeCatalog()
    register_actions(catalog)
    declared = catalog.features.get("sessionmanagement")
    assert declared is not None, "register_actions did not declare the 'sessionmanagement' feature"
    expected = {f"sessionmanagement.{name}" for name in ENFORCED_METHODS}
    assert set(declared) == expected, (
        f"register_actions declares {sorted(declared)}, expected the 6 sessionmanagement actions {sorted(expected)}"
    )
