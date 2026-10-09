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
        """Snapshot ``roles`` into a tuple at construction.

        A later change to the caller's collection cannot alter the accepted
        role set.
        """
        self._roles = tuple(roles)

    def has_role(self, role: str) -> bool:
        """Exact, case-sensitive membership test against the stored tuple."""
        return role in self._roles

    def list_roles(self) -> Sequence[str]:
        """The stored tuple itself — immutable, so a caller cannot mutate the accepted set."""
        return self._roles
