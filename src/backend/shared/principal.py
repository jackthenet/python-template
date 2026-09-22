"""Shared enforcement plumbing (docs/specs/user-roles-permissions.md, D14, ADR-070).

Generic authorization plumbing shared by the six backend features: the
``Principal`` model (REQ-025), the structural ``PermissionChecker`` protocol,
and the ``requires_permission`` decorator. No feature-specific business logic
and no import of ``backend.permissions`` — features resolve checks through the
injected checker only, so no circular import can form (ADR-070).
"""

from __future__ import annotations

import functools
import inspect
from collections.abc import Callable
from typing import Any, Protocol
from uuid import UUID

from pydantic import BaseModel


class Principal(BaseModel):
    """The acting principal (REQ-025).

    ``Principal()`` (``user_id=None``) is the system principal: it is the
    default trailing parameter of every enforced service method, so an enforced
    method called without an explicit principal is evaluated as the system
    principal (EDGE-022). ``session_token`` is validated by the check when
    present (REQ-017).
    """

    user_id: UUID | None = None
    session_token: str | None = None


class PermissionChecker(Protocol):
    """Structural check seam (D14): the permission service satisfies it.

    Features depend only on this protocol (the constructor parameter
    ``permission_service``), never on ``backend.permissions`` (ADR-070).
    """

    def require_permission(self, user_id: UUID | None, permission: str, session_token: str | None = None) -> None:
        """Require the permission for the principal; a denial raises and propagates."""
        ...

    def has_permission(self, user_id: UUID | None, permission: str, session_token: str | None = None) -> bool:
        """Report whether the permission is granted to the principal."""
        ...


def requires_permission(permission_key: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator for enforced service methods (D13, REQ-024/REQ-025; ADR-071).

    The wrapper (1) resolves the wrapped method's trailing ``principal``
    parameter (the parameter named ``principal``; default ``Principal()`` = the
    system principal), (2) calls
    ``self._permission_service.require_permission(principal.user_id,
    permission_key, session_token=principal.session_token)`` at entry — a no-op
    when ``self._permission_service is None`` (standalone mode, no enforcement)
    — and (3) invokes the wrapped method. A denial raises and propagates: the
    method body never runs. The decorator never imports ``backend.permissions``
    (it calls the injected checker and lets the denial propagate; ADR-070).
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            principal = _resolve_principal(func, args, kwargs)
            instance = args[0] if args else kwargs.get("self")
            checker = getattr(instance, "_permission_service", None) if instance is not None else None
            if checker is not None:
                checker.require_permission(principal.user_id, permission_key, session_token=principal.session_token)
            return func(*args, **kwargs)

        return wrapper

    return decorator


def _resolve_principal(func: Callable[..., Any], args: tuple[Any, ...], kwargs: dict[str, Any]) -> Principal:
    """Resolve the wrapped method's ``principal`` parameter (default ``Principal()``).

    The principal is the trailing parameter named ``principal`` (ADR-071); it
    may be passed positionally or by keyword. A method without a ``principal``
    parameter (or whose signature cannot be inspected) is evaluated as the
    system principal.
    """
    try:
        signature = inspect.signature(func)
    except TypeError, ValueError:
        return Principal()
    if "principal" not in signature.parameters:
        return Principal()
    bound = signature.bind(*args, **kwargs)
    principal = bound.arguments.get("principal")
    return principal if isinstance(principal, Principal) else Principal()
