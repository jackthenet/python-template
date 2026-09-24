"""Public API of the shared enforcement plumbing (module: backend.shared).

Generic authorization plumbing shared by the six backend features (D14,
ADR-070): the ``Principal`` model, the structural ``PermissionChecker``
protocol, and the ``requires_permission`` decorator. No feature-specific
business logic; no import of ``backend.permissions`` (no circular imports).
"""

from __future__ import annotations

from backend.shared.principal import PermissionChecker, Principal, requires_permission

__all__ = ["PermissionChecker", "Principal", "requires_permission"]
