"""Public API of the permissions feature (module: backend.permissions).

The public API is the NFR-003 backward-compatibility contract: the service +
singleton, the catalog, the models, the repository ABCs + concrete
implementations, the events, the error hierarchy, the settings registration,
and the bootstrap system set.
"""

from __future__ import annotations

from backend.permissions.catalog import PermissionCatalog
from backend.permissions.errors import (
    AuthorizationError,
    PermissionDeniedError,
    RoleAlreadyExistsError,
    RoleInUseError,
    RoleNotFoundError,
    RoleProtectedError,
    UnknownPermissionError,
)
from backend.permissions.events import (
    EventPublisher,
    PermissionDenied,
    PermissionEvent,
    RoleCreated,
    RoleDeleted,
    RolePermissionsChanged,
)
from backend.permissions.feature_settings import register_settings
from backend.permissions.models import (
    BOOTSTRAP_SYSTEM_PERMISSIONS,
    PermissionRead,
    Role,
    RolePermission,
    RoleRead,
    SystemPrincipalPermission,
)
from backend.permissions.repositories import (
    GrantRepository,
    MemoryGrantRepository,
    MemoryRoleRepository,
    MemorySystemPrincipalRepository,
    RoleRepository,
    SqliteGrantRepository,
    SqliteRoleRepository,
    SqliteSystemPrincipalRepository,
    SystemPrincipalRepository,
)
from backend.permissions.service import (
    PermissionService,
    get_permission_service,
    reset_permission_service,
)

__all__ = [
    "BOOTSTRAP_SYSTEM_PERMISSIONS",
    "AuthorizationError",
    "EventPublisher",
    "GrantRepository",
    "MemoryGrantRepository",
    "MemoryRoleRepository",
    "MemorySystemPrincipalRepository",
    "PermissionCatalog",
    "PermissionDenied",
    "PermissionDeniedError",
    "PermissionEvent",
    "PermissionRead",
    "PermissionService",
    "Role",
    "RoleAlreadyExistsError",
    "RoleCreated",
    "RoleDeleted",
    "RoleInUseError",
    "RoleNotFoundError",
    "RolePermission",
    "RolePermissionsChanged",
    "RoleProtectedError",
    "RoleRead",
    "RoleRepository",
    "SqliteGrantRepository",
    "SqliteRoleRepository",
    "SqliteSystemPrincipalRepository",
    "SystemPrincipalPermission",
    "SystemPrincipalRepository",
    "UnknownPermissionError",
    "get_permission_service",
    "register_settings",
    "reset_permission_service",
]
