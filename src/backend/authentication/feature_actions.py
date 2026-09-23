"""Feature-owned permission action declarations (docs/specs/user-roles-permissions.md, D3).

The composition root calls ``register_actions(catalog)`` at startup to declare
the authentication catalog actions (the 11 declared ``AuthService`` actions; the
spec Section 3 initial catalog table is the source of truth). The 7 exempt
session-establishment/teardown/introspection operations (D13/ADR-071) are
declared but not enforced. The ``PermissionCatalog`` annotation is
type-checking only: the feature never imports ``backend.permissions`` at
runtime (ADR-070).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from backend.permissions.catalog import PermissionCatalog


def register_actions(catalog: PermissionCatalog) -> None:
    """Register the authentication actions (permission key -> description)."""
    catalog.register_feature(
        "authentication",
        {
            "authentication.login": "Log in with username/email + password",
            "authentication.session_info": "Read session metadata for a token",
            "authentication.logout": "Log out (revoke a session)",
            "authentication.request_password_reset": "Request a password reset",
            "authentication.complete_password_reset": "Complete a password reset",
            "authentication.begin_passkey_registration": "Begin passkey registration",
            "authentication.complete_passkey_registration": "Complete passkey registration",
            "authentication.begin_passkey_login": "Begin passkey login",
            "authentication.complete_passkey_login": "Complete passkey login",
            "authentication.list_passkeys": "List a user's passkeys",
            "authentication.delete_passkey": "Delete a passkey",
        },
    )
