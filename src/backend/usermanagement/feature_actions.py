"""Feature-owned permission action declarations (docs/specs/user-roles-permissions.md, D3).

The composition root calls ``register_actions(catalog)`` at startup to declare
the usermanagement catalog actions (the 11 enforced public ``UserManager``
methods; the spec Section 3 initial catalog table is the source of truth).
The ``PermissionCatalog`` annotation is type-checking only: the feature never
imports ``backend.permissions`` at runtime (ADR-070).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from backend.permissions.catalog import PermissionCatalog


def register_actions(catalog: PermissionCatalog) -> None:
    """Register the usermanagement actions (permission key -> description)."""
    catalog.register_feature(
        "usermanagement",
        {
            "usermanagement.create_user": "Create a user account",
            "usermanagement.get_user": "Read a user by id",
            "usermanagement.get_user_by_username": "Read a user by username",
            "usermanagement.list_users": "List users",
            "usermanagement.update_user": "Update mutable user fields",
            "usermanagement.delete_user": "Delete a user account",
            "usermanagement.change_password": "Change a user's password",
            "usermanagement.verify_password": "Verify a user's password",
            "usermanagement.set_role": "Replace a user's roles with a single role",
            "usermanagement.activate_user": "Activate a user",
            "usermanagement.deactivate_user": "Deactivate a user",
        },
    )
