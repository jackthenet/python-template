"""Feature-owned permission action declarations (docs/specs/user-roles-permissions.md, D3).

The composition root calls ``register_actions(catalog)`` at startup to declare
the settings catalog actions (the 19 enforced public ``SettingsRegistry``
methods; the spec Section 3 initial catalog table is the source of truth).
The ``PermissionCatalog`` annotation is type-checking only: the feature never
imports ``backend.permissions`` at runtime (ADR-070).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from backend.permissions.catalog import PermissionCatalog


def register_actions(catalog: PermissionCatalog) -> None:
    """Register the settings actions (permission key -> description)."""
    catalog.register_feature(
        "settings",
        {
            "settings.register": "Register a single setting definition",
            "settings.register_feature": "Register a feature's setting definitions",
            "settings.has": "Check whether a setting key is registered",
            "settings.get_definition": "Read a setting definition",
            "settings.get_value": "Read a setting value",
            "settings.set_value": "Set a setting value (validated)",
            "settings.reset": "Reset a setting to its default",
            "settings.reset_all": "Reset all settings to their defaults",
            "settings.get_status": "Read a setting's status",
            "settings.to_view": "Read a renderable setting view",
            "settings.views": "List renderable setting views",
            "settings.grouped_views": "List setting views grouped by category/group",
            "settings.create_template": "Create a named value template",
            "settings.load_template": "Load a template's values",
            "settings.update_template": "Update a template's values",
            "settings.delete_template": "Delete a template",
            "settings.get_template": "Read a template",
            "settings.has_template": "Check whether a template exists",
            "settings.list_templates": "List templates",
        },
    )
