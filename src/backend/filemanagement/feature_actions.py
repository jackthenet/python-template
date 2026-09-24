"""Feature-owned permission action declarations (docs/specs/user-roles-permissions.md, D3).

The composition root calls ``register_actions(catalog)`` at startup to declare
the filemanagement catalog actions (the 10 enforced public ``FileService``
methods; the spec Section 3 initial catalog table is the source of truth).
The ``PermissionCatalog`` annotation is type-checking only: the feature never
imports ``backend.permissions`` at runtime (ADR-070).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from backend.permissions.catalog import PermissionCatalog


def register_actions(catalog: PermissionCatalog) -> None:
    """Register the filemanagement actions (permission key -> description)."""
    catalog.register_feature(
        "filemanagement",
        {
            "filemanagement.upload": "Upload a file",
            "filemanagement.upload_avatar": "Upload a user's first avatar",
            "filemanagement.replace_avatar": "Replace a user's avatar",
            "filemanagement.delete_avatar": "Delete a user's avatar",
            "filemanagement.get_avatar": "Read a user's avatar",
            "filemanagement.download": "Download a file's content",
            "filemanagement.open": "Open a file as a stream",
            "filemanagement.delete": "Delete a file",
            "filemanagement.get_file": "Read a file's metadata",
            "filemanagement.list_files": "List files",
        },
    )
