"""Acceptance tests for the settings enforcement wiring (user-roles-permissions, REQ-024).

Covers T-010: every public ``SettingsRegistry`` method takes a trailing ``principal``
parameter (default = the system principal, REQ-025); all 19 methods are enforced
(the settings exempt set is empty, spec Section 3) and enforce ``require_permission``
at entry (a denial propagates to the caller, an allow proceeds, the permission key is
``settings.<method>``); an enforced method called without an explicit principal is
evaluated as the system principal (EDGE-022); the constructor gains an optional
``permission_service`` checker (standalone by default, AC-031); and the feature-owned
``feature_actions.register_actions`` declares the 19 settings catalog actions
(spec Section 3).

These tests verify externally observable behavior only. Per the design constraint
(ADR-071), the test uses a fake ``PermissionChecker`` (structural protocol) — the
feature never imports ``backend.permissions``. The ``backend.shared`` and
``feature_actions`` imports are deferred into the test body so the module collects
cleanly before the feature is implemented (RED).
"""

from __future__ import annotations

import inspect
import tempfile
from typing import Any
from uuid import uuid4

import pytest

from backend.eventbus import EventBus
from backend.settings import (
    SettingDefinition,
    SettingKind,
    SettingsRegistry,
    YamlValueRepository,
)

# The spec's settings catalog (Section 3): all 19 public methods are enforced
# (the settings exempt set is empty).
ENFORCED_METHODS: tuple[str, ...] = (
    "register",
    "register_feature",
    "has",
    "get_definition",
    "get_value",
    "set_value",
    "reset",
    "reset_all",
    "get_status",
    "to_view",
    "views",
    "grouped_views",
    "create_template",
    "load_template",
    "update_template",
    "delete_template",
    "get_template",
    "has_template",
    "list_templates",
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
    method = getattr(SettingsRegistry, method_name)
    params = list(inspect.signature(method).parameters.values())
    assert params, f"SettingsRegistry.{method_name} has no parameters"
    last = params[-1]
    assert last.name == "principal", (
        f"SettingsRegistry.{method_name}: trailing parameter is {last.name!r}, expected 'principal'"
    )
    assert last.default is not inspect.Parameter.empty, (
        f"SettingsRegistry.{method_name}: 'principal' has no default; existing call sites would break"
    )
    return last.default


def _text_def(key: str = "probe.key") -> SettingDefinition:
    return SettingDefinition(key=key, kind=SettingKind.TEXT, default="x")


def _build_registry(checker: _FakePermissionChecker) -> SettingsRegistry:
    """Construct an isolated ``SettingsRegistry`` with the checker injected."""
    bus = EventBus()
    try:
        return SettingsRegistry(
            event_bus=bus,
            value_repository=YamlValueRepository(tempfile.mkdtemp()),
            permission_service=checker,
        )
    except Exception:
        bus.shutdown()
        raise


def _denial_probes() -> dict[str, tuple[Any, ...]]:
    """Probe arguments for each enforced method (the denial happens at entry, before the body)."""
    return {
        "register": (_text_def(),),
        "register_feature": ("probe", [_text_def("probe.key")]),
        "has": ("probe.key",),
        "get_definition": ("probe.key",),
        "get_value": ("probe.key",),
        "set_value": ("probe.key", "v"),
        "reset": ("probe.key",),
        "reset_all": (),
        "get_status": ("probe.key",),
        "to_view": ("probe.key",),
        "views": (),
        "grouped_views": (),
        "create_template": ("probe-template", "probe", None),
        "load_template": ("probe-template",),
        "update_template": ("probe-template", {}),
        "delete_template": ("probe-template",),
        "get_template": ("probe-template",),
        "has_template": ("probe-template",),
        "list_templates": (),
    }


def test_settings_enforcement_wiring() -> None:
    # --- principal parameter (REQ-024 / ADR-071): all 19 public methods ---
    for name in ENFORCED_METHODS:
        default = _principal_default(name)
        assert getattr(default, "user_id", "MISSING") is None, (
            f"SettingsRegistry.{name}: the default principal is not the system principal (user_id must be None)"
        )
        assert getattr(default, "session_token", "MISSING") is None, (
            f"SettingsRegistry.{name}: the default principal is not the system principal (session_token must be None)"
        )

    # --- constructor: optional permission_service, standalone by default (AC-031) ---
    ctor_params = inspect.signature(SettingsRegistry.__init__).parameters
    assert "permission_service" in ctor_params, "SettingsRegistry.__init__ has no 'permission_service' parameter"
    assert ctor_params["permission_service"].default is None, (
        "SettingsRegistry.__init__: 'permission_service' must default to None (standalone mode)"
    )

    # --- deny: every enforced method lets the checker's denial propagate to the caller ---
    denier = _FakePermissionChecker(deny=True)
    registry = _build_registry(denier)
    probes = _denial_probes()
    for name, args in probes.items():
        with pytest.raises(_PermissionDenied):
            getattr(registry, name)(*args)
    assert [call[1] for call in denier.calls] == [f"settings.{name}" for name in probes]

    # --- allow: an enforced method proceeds; the default principal is the system principal (EDGE-022) ---
    allow_checker = _FakePermissionChecker(deny=False)
    registry = _build_registry(allow_checker)
    registry.register(_text_def())
    assert registry.get_value("probe.key") == "x"
    assert allow_checker.calls == [(None, "settings.register", None), (None, "settings.get_value", None)]

    # --- an explicit principal (user_id + session token) reaches the check (REQ-024) ---
    from backend.shared import Principal  # deferred: collects cleanly before T-001 lands (RED)

    user_id = uuid4()
    principal = Principal(user_id=user_id, session_token="principal-token")
    explicit_checker = _FakePermissionChecker(deny=False)
    registry = _build_registry(explicit_checker)
    registry.register(_text_def())
    registry.get_value("probe.key", principal=principal)
    assert explicit_checker.calls == [
        (None, "settings.register", None),
        (user_id, "settings.get_value", "principal-token"),
    ]

    # --- standalone mode (AC-031): a registry without a checker performs no check ---
    bus = EventBus()
    standalone = SettingsRegistry(
        event_bus=bus, value_repository=YamlValueRepository(tempfile.mkdtemp())
    )
    try:
        standalone.register(_text_def())
        # An enforced method called with an explicit principal (a user without any
        # permission) performs no check in standalone mode: the operation proceeds.
        read = standalone.get_value(
            "probe.key", principal=Principal(user_id=uuid4(), session_token="standalone-session")
        )
        assert read == "x"
    finally:
        bus.shutdown()

    # --- feature_actions: the feature declares its 19 catalog actions (REQ-005 / REQ-024) ---
    from backend.settings.feature_actions import register_actions  # deferred: T-010 artifact (RED)

    catalog = _FakeCatalog()
    register_actions(catalog)
    declared = catalog.features.get("settings")
    assert declared is not None, "register_actions did not declare the 'settings' feature"
    expected = {f"settings.{name}" for name in ENFORCED_METHODS}
    assert set(declared) == expected, (
        f"register_actions declares {sorted(declared)}, expected the 19 settings actions {sorted(expected)}"
    )
