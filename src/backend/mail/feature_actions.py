"""Feature-owned permission action declarations (docs/specs/user-roles-permissions.md, D3).

The composition root calls ``register_actions(catalog)`` at startup to declare
the mail catalog actions (the 3 enforced public ``MailService`` methods; the
mail exempt set is empty, spec Section 3). The ``PermissionCatalog`` annotation
is type-checking only: the feature never imports ``backend.permissions`` at
runtime (ADR-070).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from backend.permissions.catalog import PermissionCatalog


def register_actions(catalog: PermissionCatalog) -> None:
    """Register the mail actions (permission key -> description)."""
    catalog.register_feature(
        "mail",
        {
            "mail.send_email": "Send an email",
            "mail.send_password_reset_email": "Send a password-reset email",
            "mail.send_email_verification_email": "Send an email-verification email",
        },
    )
