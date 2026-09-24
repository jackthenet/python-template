"""The role store: the single source of truth for which roles exist (D4, ADR-072).

Role names are validated against an injected :class:`RoleStore` instead of a
hardcoded tuple, so the permission feature's role store can be the single
source of truth for role names (roles are runtime-managed entities, Q-77).
The default is :class:`StaticRoleStore` with ``("admin", "user")``.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable, Sequence

from backend.logging import logged_class


@logged_class
class RoleStore(ABC):
    """The role store interface (D4)."""

    @abstractmethod
    def has_role(self, role: str) -> bool:
        """Whether ``role`` is an existing role."""
        ...

    @abstractmethod
    def list_roles(self) -> Sequence[str]:
        """The existing roles."""
        ...


@logged_class
class StaticRoleStore(RoleStore):
    """A fixed role set (the default: ``("admin", "user")``)."""

    def __init__(self, roles: Iterable[str]) -> None:
        self._roles = tuple(roles)

    def has_role(self, role: str) -> bool:
        return role in self._roles

    def list_roles(self) -> Sequence[str]:
        return self._roles
