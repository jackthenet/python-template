"""The static permission catalog (docs/specs/user-roles-permissions.md, D3).

The permission vocabulary is a closed set derived from feature-owned
``register_actions(catalog)`` declarations called at startup (REQ-004,
REQ-005); no runtime creation of permission names. Action keys are
hierarchical ``feature.action`` keys matching ``^[a-z0-9_-]+\\.[a-z0-9_-]+$``
(REQ-002); feature-level wildcard grants (``<feature>.*``) are validated
against this vocabulary by the grant path (REQ-003).
"""

from __future__ import annotations

import re
from collections.abc import Sequence

from backend.logging import logged_class
from backend.permissions.models import PermissionRead

_PERMISSION_KEY_PATTERN = re.compile(r"^[a-z0-9_-]+\.[a-z0-9_-]+$")


@logged_class
class PermissionCatalog:
    """In-memory registry of declared actions.

    Built at startup from the features' ``register_feature`` calls; closed
    thereafter (no runtime creation).
    """

    def __init__(self) -> None:
        self._actions: dict[str, str] = {}  # permission key -> description
        self._features: dict[str, list[str]] = {}  # feature -> keys (insertion order)

    def register_feature(self, feature: str, actions: dict[str, str]) -> None:
        """Register ``feature``'s actions (``permission key -> description``).

        Keys must match ``^[a-z0-9_-]+\\.[a-z0-9_-]+$`` and start with
        ``f"{feature}."``; duplicate keys raise ``ValueError``.
        """
        for key, description in actions.items():
            if not _PERMISSION_KEY_PATTERN.match(key):
                raise ValueError(f"permission key {key!r} is malformed (expected feature.action)")
            if not key.startswith(f"{feature}."):
                raise ValueError(f"permission key {key!r} does not belong to feature {feature!r}")
            if key in self._actions:
                raise ValueError(f"permission key {key!r} is already registered")
            self._actions[key] = description
            self._features.setdefault(feature, []).append(key)

    def has(self, permission: str) -> bool:
        """Whether ``permission`` is a declared action key."""
        return permission in self._actions

    def features(self) -> frozenset[str]:
        """The declared features."""
        return frozenset(self._features)

    def actions(self, feature: str | None = None) -> Sequence[PermissionRead]:
        """The declared actions, optionally restricted to ``feature``."""
        keys = list(self._actions) if feature is None else list(self._features.get(feature, []))
        return [
            PermissionRead(
                permission=key,
                feature=key.split(".", 1)[0],
                description=self._actions[key],
            )
            for key in keys
        ]
