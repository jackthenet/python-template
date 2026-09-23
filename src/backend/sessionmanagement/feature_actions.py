"""Feature-owned permission action declarations (docs/specs/user-roles-permissions.md, D3).

The composition root calls ``register_actions(catalog)`` at startup to declare
the sessionmanagement catalog actions (the 6 enforced public ``SessionService``
methods; the sessionmanagement exempt set is empty, spec Section 3). The
``PermissionCatalog`` annotation is type-checking only: the feature never
imports ``backend.permissions`` at runtime (ADR-070).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from backend.permissions.catalog import PermissionCatalog


def register_actions(catalog: PermissionCatalog) -> None:
    """Register the sessionmanagement actions (permission key -> description)."""
    catalog.register_feature(
        "sessionmanagement",
        {
            "sessionmanagement.list_sessions": "List sessions",
            "sessionmanagement.revoke_session": "Revoke a session by id",
            "sessionmanagement.logout_all_sessions": "Log out all sessions for a token's user",
            "sessionmanagement.logout_other_sessions": "Log out all sessions except the token's",
            "sessionmanagement.revoke_all_sessions": "Revoke all sessions for a user",
            "sessionmanagement.cleanup_expired": "Delete expired sessions",
        },
    )
