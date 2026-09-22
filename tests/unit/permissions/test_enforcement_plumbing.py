"""Unit tests for the shared enforcement plumbing (docs/specs/user-roles-permissions.md).

Covers the ``requires_permission`` decorator (REQ-025; ADR-070 / ADR-071):
a denial propagates, an allow proceeds, and standalone mode (no injected
checker) runs open.
"""

from __future__ import annotations

from uuid import uuid4

import pytest


class _PermissionDenied(Exception):
    """A test-local denial error (the real one lives in backend.permissions, T-003)."""


class _AllowingChecker:
    """A structural PermissionChecker that allows everything and records calls."""

    def __init__(self) -> None:
        self.calls: list[tuple[object, str, str | None]] = []

    def require_permission(self, user_id: object, permission: str, session_token: str | None = None) -> None:
        self.calls.append((user_id, permission, session_token))

    def has_permission(self, user_id: object, permission: str, session_token: str | None = None) -> bool:
        return True


class _DenyingChecker:
    """A structural PermissionChecker that denies everything and records calls."""

    def __init__(self) -> None:
        self.calls: list[tuple[object, str, str | None]] = []

    def require_permission(self, user_id: object, permission: str, session_token: str | None = None) -> None:
        self.calls.append((user_id, permission, session_token))
        raise _PermissionDenied("denied")

    def has_permission(self, user_id: object, permission: str, session_token: str | None = None) -> bool:
        return False


def test_requires_permission_decorator() -> None:
    """The ``@requires_permission`` decorator: deny propagates, allow proceeds, standalone open.

    The decorator wraps an enforced service method, resolves the trailing
    ``principal: Principal = Principal()`` parameter (the system principal by
    default), and — when a PermissionChecker is injected into the owning
    service — calls ``checker.require_permission(principal.user_id,
    permission_key, session_token=principal.session_token)`` at entry. A
    denial raises and propagates (the method body never runs); an allow
    proceeds to the method body; with no checker injected (standalone mode)
    the method runs open.
    """
    from backend.shared import Principal, requires_permission

    class _FakeService:
        """A fake enforced service (ADR-071: optional ``permission_service`` constructor)."""

        def __init__(self, permission_service: object | None = None) -> None:
            self._permission_service = permission_service
            self.executed: list[int] = []

        @requires_permission("feature.do_thing")
        # ADR-071 mandates the trailing principal parameter with the system-principal default.
        def do_thing(self, value: int, principal: Principal = Principal()) -> int:  # noqa: B008
            self.executed.append(value)
            return value * 2

    # --- deny propagates: the checker's denial raises, the method body never runs ---
    denying = _DenyingChecker()
    denied_service = _FakeService(permission_service=denying)
    with pytest.raises(_PermissionDenied):
        denied_service.do_thing(1)
    # the check ran at entry with the default (system) principal before the denial
    assert denying.calls == [(None, "feature.do_thing", None)]
    assert denied_service.executed == []

    # --- allow proceeds: the checker is called at entry, the method body runs ---
    allowing = _AllowingChecker()
    allowed_service = _FakeService(permission_service=allowing)
    value = 21
    result = allowed_service.do_thing(value)
    assert result == value * 2
    assert allowed_service.executed == [value]
    # default principal = the system principal (user_id=None, session_token=None)
    assert allowing.calls == [(None, "feature.do_thing", None)]

    # --- the explicit principal reaches the check (user_id + session_token) ---
    user_id = uuid4()
    token = "session-token"
    allowed_service.do_thing(1, principal=Principal(user_id=user_id, session_token=token))
    assert allowing.calls[-1] == (user_id, "feature.do_thing", token)

    # --- standalone mode (no checker injected): the method runs open ---
    standalone = _FakeService()
    value = 5
    standalone_result = standalone.do_thing(value)
    assert standalone_result == value * 2
    assert standalone.executed == [value]
