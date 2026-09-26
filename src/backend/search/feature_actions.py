"""Feature-owned permission action declarations (docs/specs/search.md, D16).

The composition root calls ``register_actions(catalog)`` at startup to declare
the search catalog action (``search.search``; additive to the
user-roles-permissions catalog — no change to the permissions feature's code
or behavior, REQ-016/ADR-079). The ``PermissionCatalog`` annotation is
type-checking only: the feature never imports ``backend.permissions`` at
runtime (ADR-070).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from backend.logging import logged

if TYPE_CHECKING:
    from backend.permissions.catalog import PermissionCatalog


@logged
def register_actions(catalog: PermissionCatalog) -> None:
    """Register the search action (permission key -> description)."""
    catalog.register_feature(
        "search",
        {
            "search.search": "Search registered sources",
        },
    )
