"""The permission service foundation (docs/specs/user-roles-permissions.md, D19, REQ-023).

``PermissionService`` is the RBAC use-case service. This module provides the
service's construction contract (constructor DI with the repository ABCs,
the ``UserManager``, and the structural session-lookup seam — ADR-069) and
the module singleton (``get_permission_service``) / reset
(``reset_permission_service``) (D19). The check core, role CRUD, dynamic
grants, and role-assignment pass-throughs are implemented by the subsequent
tasks (T-004..T-006).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from backend.permissions.catalog import PermissionCatalog
from backend.permissions.models import SessionLookup
from backend.permissions.repositories import (
    GrantRepository,
    RoleRepository,
    SqliteGrantRepository,
    SqliteRoleRepository,
    SqliteSystemPrincipalRepository,
    SystemPrincipalRepository,
)
from backend.usermanagement import UserManager

if TYPE_CHECKING:
    from backend.permissions.events import EventPublisher
    from backend.settings import SettingsRegistry

# Default persistence wiring of the module singleton (D19): the common
# persistence root ``./data/`` (ADR-056 layout convention), one database per
# feature.
DEFAULT_DATABASE_URL = "sqlite:///./data/permissions.db"
DEFAULT_USER_DATABASE_URL = "sqlite:///./data/usermanagement/users.db"


class PermissionService:
    """The RBAC use-case service (constructor DI, REQ-023).

    The service depends only on the repository ABCs, the ``UserManager``
    (user lookup + role-assignment delegation, D8), and the structural
    session-lookup seam (D9) (ADR-069).
    """

    def __init__(  # noqa: PLR0917  # the 8 positional dependencies are the spec construction contract (D19)
        self,
        role_repository: RoleRepository,
        grant_repository: GrantRepository,
        system_repository: SystemPrincipalRepository,
        user_manager: UserManager,
        session_lookup: SessionLookup | None = None,
        catalog: PermissionCatalog | None = None,
        event_bus: EventPublisher | None = None,
        settings_registry: SettingsRegistry | None = None,
    ) -> None:
        self._role_repository = role_repository
        self._grant_repository = grant_repository
        self._system_repository = system_repository
        self._user_manager = user_manager
        self._session_lookup = session_lookup
        self._catalog = catalog if catalog is not None else PermissionCatalog()
        self._event_bus = event_bus
        self._settings_registry = settings_registry


_permission_service: list[PermissionService | None] = [None]


def get_permission_service() -> PermissionService:
    """Return the shared PermissionService (module singleton, D19).

    The first call lazily creates the singleton, wired to the shared SQLite
    repositories and the shared user manager at construction; subsequent
    calls return the existing instance.
    """
    service = _permission_service[0]
    if service is None:
        from backend.usermanagement import SqliteUserRepository

        service = PermissionService(
            SqliteRoleRepository(DEFAULT_DATABASE_URL),
            SqliteGrantRepository(DEFAULT_DATABASE_URL),
            SqliteSystemPrincipalRepository(DEFAULT_DATABASE_URL),
            UserManager(SqliteUserRepository(DEFAULT_USER_DATABASE_URL)),
        )
        _permission_service[0] = service
    return service


def reset_permission_service() -> None:
    """Reset the shared PermissionService (for test isolation, D19)."""
    _permission_service[0] = None
