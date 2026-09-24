"""Acceptance tests for the mail enforcement wiring (user-roles-permissions, REQ-024).

Covers T-012: every public ``MailService`` method takes a trailing ``principal``
parameter (default = the system principal, REQ-025); all 3 methods are enforced
(the mail exempt set is empty, spec Section 3) and enforce ``require_permission``
at entry (a denial propagates to the caller, an allow proceeds, the permission key
is ``mail.<method>``); an enforced method called without an explicit principal is
evaluated as the system principal (EDGE-022); the constructor gains an optional
``permission_service`` checker (standalone by default, AC-031); and the feature-owned
``feature_actions.register_actions`` declares the 3 mail catalog actions
(spec Section 3).

These tests verify externally observable behavior only. Per the design constraint
(ADR-071), the test uses a fake ``PermissionChecker`` (structural protocol) — the
feature never imports ``backend.permissions``. The ``backend.shared`` and
``feature_actions`` imports are deferred into the test body so the module collects
cleanly before the feature is implemented (RED).
"""

from __future__ import annotations

import inspect
from typing import Any
from uuid import uuid4

import pytest

from backend.mail import (
    EmailSendResult,
    EmailTemplate,
    EmailVerificationEmailRequest,
    MailService,
    PasswordResetEmailRequest,
)

# The spec's mail catalog (Section 3): all 3 public methods are enforced
# (the mail exempt set is empty).
ENFORCED_METHODS: tuple[str, ...] = (
    "send_email",
    "send_password_reset_email",
    "send_email_verification_email",
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


class _FakeSmtpTransport:
    """A recording stand-in for the SMTP transport (no real SMTP).

    Lets the allow/standalone paths complete the send so the test can observe the
    operation proceeded (the transport received the message).
    """

    def __init__(self) -> None:
        self.sent: list[Any] = []

    def send(self, message: Any) -> None:
        self.sent.append(message)


def _probe_template() -> EmailTemplate:
    """A minimal template with no placeholders (renders with an empty context)."""
    return EmailTemplate(
        name="probe",
        subject="Probe subject",
        body_html="<p>Probe</p>",
        body_text="Probe",
    )


def _principal_default(method_name: str) -> Any:
    """Return the trailing ``principal`` parameter's default for a public method.

    Asserts the ADR-071 contract: the last parameter is named ``principal`` and has
    a default (existing positional call sites are unaffected).
    """
    method = getattr(MailService, method_name)
    params = list(inspect.signature(method).parameters.values())
    assert params, f"MailService.{method_name} has no parameters"
    last = params[-1]
    assert last.name == "principal", (
        f"MailService.{method_name}: trailing parameter is {last.name!r}, expected 'principal'"
    )
    assert last.default is not inspect.Parameter.empty, (
        f"MailService.{method_name}: 'principal' has no default; existing call sites would break"
    )
    return last.default


def _build_service(transport: _FakeSmtpTransport, checker: _FakePermissionChecker) -> MailService:
    """Construct a ``MailService`` over the given transport with the checker injected."""
    return MailService(transport=transport, event_bus=None, permission_service=checker)


def _denial_probes() -> dict[str, tuple[Any, ...]]:
    """Probe arguments for each enforced method (the denial happens at entry, before the body)."""
    return {
        "send_email": ("probe@example.com", _probe_template(), {}),
        "send_password_reset_email": (
            PasswordResetEmailRequest(
                to="probe@example.com",
                display_name="Probe",
                reset_url="https://app.example.com/reset?token=probe",
            ),
        ),
        "send_email_verification_email": (
            EmailVerificationEmailRequest(
                to="probe@example.com",
                display_name="Probe",
                verification_url="https://app.example.com/verify?token=probe",
            ),
        ),
    }


def test_mail_enforcement_wiring() -> None:
    # --- principal parameter (REQ-024 / ADR-071): all 3 public methods ---
    for name in ENFORCED_METHODS:
        default = _principal_default(name)
        assert getattr(default, "user_id", "MISSING") is None, (
            f"MailService.{name}: the default principal is not the system principal (user_id must be None)"
        )
        assert getattr(default, "session_token", "MISSING") is None, (
            f"MailService.{name}: the default principal is not the system principal (session_token must be None)"
        )

    # --- constructor: optional permission_service, standalone by default (AC-031) ---
    ctor_params = inspect.signature(MailService.__init__).parameters
    assert "permission_service" in ctor_params, "MailService.__init__ has no 'permission_service' parameter"
    assert ctor_params["permission_service"].default is None, (
        "MailService.__init__: 'permission_service' must default to None (standalone mode)"
    )

    # --- deny: every enforced method lets the checker's denial propagate to the caller ---
    denier = _FakePermissionChecker(deny=True)
    service = _build_service(_FakeSmtpTransport(), denier)
    probes = _denial_probes()
    for name, args in probes.items():
        with pytest.raises(_PermissionDenied):
            getattr(service, name)(*args)
    assert [call[1] for call in denier.calls] == [f"mail.{name}" for name in probes]

    # --- allow: an enforced method proceeds; the default principal is the system principal (EDGE-022) ---
    allow_checker = _FakePermissionChecker(deny=False)
    allow_transport = _FakeSmtpTransport()
    service = _build_service(allow_transport, allow_checker)
    result = service.send_email("probe@example.com", _probe_template(), {})
    assert isinstance(result, EmailSendResult)
    assert result.to == "probe@example.com"
    assert len(allow_transport.sent) == 1
    assert allow_checker.calls == [(None, "mail.send_email", None)]

    # --- an explicit principal (user_id + session token) reaches the check (REQ-024) ---
    from backend.shared import Principal  # deferred: collects cleanly before T-001 lands (RED)

    user_id = uuid4()
    principal = Principal(user_id=user_id, session_token="principal-token")
    explicit_checker = _FakePermissionChecker(deny=False)
    explicit_transport = _FakeSmtpTransport()
    service = _build_service(explicit_transport, explicit_checker)
    service.send_email("probe@example.com", _probe_template(), {}, principal=principal)
    assert explicit_checker.calls == [(user_id, "mail.send_email", "principal-token")]

    # --- standalone mode (AC-031): a service without a checker performs no check ---
    standalone_transport = _FakeSmtpTransport()
    standalone = MailService(transport=standalone_transport, event_bus=None)
    read = standalone.send_email(
        "probe@example.com",
        _probe_template(),
        {},
        principal=Principal(user_id=uuid4(), session_token="standalone-session"),
    )
    assert read.to == "probe@example.com"
    assert len(standalone_transport.sent) == 1

    # --- feature_actions: the feature declares its 3 catalog actions (REQ-005 / REQ-024) ---
    from backend.mail.feature_actions import register_actions  # deferred: T-012 artifact (RED)

    catalog = _FakeCatalog()
    register_actions(catalog)
    declared = catalog.features.get("mail")
    assert declared is not None, "register_actions did not declare the 'mail' feature"
    expected = {f"mail.{name}" for name in ENFORCED_METHODS}
    assert set(declared) == expected, (
        f"register_actions declares {sorted(declared)}, expected the 3 mail actions {sorted(expected)}"
    )
