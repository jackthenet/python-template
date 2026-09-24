"""Application entrypoint (the composition root).

Registers every feature's settings in the shared settings registry at startup,
then calls ``setup_logger`` exactly once (spec section 3.3, REQ-011). The call
is idempotent and thread-safe, so a second call (e.g. from a test or a
re-import) is a no-op.

The composition root (docs/specs/user-roles-permissions.md, ADR-069) builds the
static permission catalog from the six features' ``register_actions`` calls
(REQ-005), creates the shared ``PermissionService``, and wires it as the shared
``PermissionChecker`` into the six services (their ``permission_service``
constructor parameter). The ``PermissionService`` and the ``UserManager`` form a
circular dependency (the service looks up users; the service enforces the
user-management methods), and the ``PermissionService`` and the settings registry
form another (the service syncs the system-set alias; the registry enforces the
settings methods); both are broken with lazy proxies so the shared instances are
wired into both sides.
"""

from uuid import UUID

from backend.authentication import (
    AuthService,
    SqlitePasswordResetRepository,
    SqliteSessionRepository,
    SqliteWebAuthnCredentialRepository,
)
from backend.authentication import (
    register_settings as register_authentication_settings,
)
from backend.authentication.feature_actions import register_actions as register_authentication_actions
from backend.eventbus import get_event_bus
from backend.eventbus import register_settings as register_eventbus_settings
from backend.filemanagement import (
    FileService,
    LocalDiskStorageBackend,
    SqliteFileRepository,
)
from backend.filemanagement.feature_actions import register_actions as register_filemanagement_actions
from backend.logging import register_settings as register_logging_settings
from backend.logging import setup_logger
from backend.mail import MailService
from backend.mail.feature_actions import register_actions as register_mail_actions
from backend.permissions import (
    BOOTSTRAP_SYSTEM_PERMISSIONS,
    PermissionCatalog,
    PermissionService,
    SqliteGrantRepository,
    SqliteRoleRepository,
    SqliteSystemPrincipalRepository,
)
from backend.permissions import register_settings as register_permissions_settings
from backend.sessionmanagement import SessionService
from backend.sessionmanagement.feature_actions import register_actions as register_sessionmanagement_actions
from backend.settings import SettingsRegistry
from backend.settings.feature_actions import register_actions as register_settings_actions
from backend.settings.registry import _registry as _settings_registry_singleton
from backend.usermanagement import (
    SqliteUserRepository,
    UserManager,
)
from backend.usermanagement import (
    register_settings as register_usermanagement_settings,
)
from backend.usermanagement.feature_actions import register_actions as register_usermanagement_actions

# --- The static permission catalog (REQ-004, REQ-005) ---
# Built at startup from the six features' ``register_actions`` calls; closed
# thereafter (no runtime creation of permission names).
_catalog = PermissionCatalog()
register_usermanagement_actions(_catalog)
register_authentication_actions(_catalog)
register_settings_actions(_catalog)
register_filemanagement_actions(_catalog)
register_mail_actions(_catalog)
register_sessionmanagement_actions(_catalog)


# --- Lazy proxies (break the composition-root cycles) ---
class _LazyPermissionService:
    """A lazy proxy for the shared PermissionService (the composition-root wiring).

    Satisfies the structural ``PermissionChecker`` protocol (the two check
    methods delegate to the real service once it is set); other attributes are
    resolved through the proxy.
    """

    def __init__(self) -> None:
        self._service: PermissionService | None = None

    def set_service(self, service: PermissionService) -> None:
        self._service = service

    def require_permission(self, user_id: UUID | None, permission: str, session_token: str | None = None) -> None:
        self._service.require_permission(user_id, permission, session_token=session_token)  # type: ignore[union-attr]

    def has_permission(self, user_id: UUID | None, permission: str, session_token: str | None = None) -> bool:
        return self._service.has_permission(user_id, permission, session_token=session_token)  # type: ignore[union-attr]

    def __getattr__(self, name: str):
        return getattr(self._service, name)


class _LazyUserManager:
    """A lazy proxy for the shared UserManager (the composition-root wiring)."""

    def __init__(self) -> None:
        self._manager: UserManager | None = None

    def set_manager(self, manager: UserManager) -> None:
        self._manager = manager

    def __getattr__(self, name: str):
        return getattr(self._manager, name)


_permission_service_proxy = _LazyPermissionService()
_user_manager_proxy = _LazyUserManager()

# --- The shared settings registry (one of the six services) ---
# Wired with the shared PermissionService (via the lazy proxy, which is set to
# the real service below); set as the shared singleton so the other services
# and the settings registration use the same instance.
_settings_registry = SettingsRegistry(permission_service=_permission_service_proxy)
_settings_registry_singleton[0] = _settings_registry

# --- The shared PermissionService (the composition-root wiring) ---
# Its user lookup goes through the lazy UserManager proxy (set to the real
# UserManager below), breaking the PermissionService <-> UserManager cycle.
# It is created (and set on the proxy) before the settings registration, so the
# registry's enforced methods resolve the real service.
_PERMISSION_DB = "sqlite:///./data/permissions.db"
_permission_service = PermissionService(
    SqliteRoleRepository(_PERMISSION_DB),
    SqliteGrantRepository(_PERMISSION_DB),
    SqliteSystemPrincipalRepository(_PERMISSION_DB),
    _user_manager_proxy,  # type: ignore[arg-type]  # the lazy proxy resolves to the real UserManager
    catalog=_catalog,
    event_bus=get_event_bus(),  # activates the SettingChanged subscription (REQ-019, D16)
    settings_registry=_settings_registry,
)
_permission_service_proxy.set_service(_permission_service)

# Seed the system-principal set with the bootstrap set plus the settings-read keys the
# composition root needs at startup (setup_logger reads the logging settings live via
# registry.has / registry.get_value, REQ-011/REQ-005). The bootstrap set covers the
# internal startup calls (settings registration, password verification, mail, cleanup);
# the settings-read keys cover the live settings reads at startup.
_permission_service.set_system_permissions(
    BOOTSTRAP_SYSTEM_PERMISSIONS | {"settings.has", "settings.get_value"}
)

# --- Register every feature's settings ---
register_logging_settings(_settings_registry)
register_authentication_settings(_settings_registry)
register_usermanagement_settings(_settings_registry)
register_eventbus_settings(_settings_registry)
register_permissions_settings(_settings_registry)  # REQ-019: the permissions.system_principal alias

# --- The shared UserManager (one of the six services) ---
_user_repository = SqliteUserRepository("sqlite:///./data/usermanagement/users.db")
_user_manager = UserManager(_user_repository, permission_service=_permission_service)
_user_manager_proxy.set_manager(_user_manager)

# --- The remaining five services (wired with the shared PermissionService) ---
_AUTH_DB = "sqlite:///./data/authentication.db"
_auth_service = AuthService(
    _user_manager,
    _user_repository,
    SqliteSessionRepository(_AUTH_DB),
    SqlitePasswordResetRepository(_AUTH_DB),
    SqliteWebAuthnCredentialRepository(_AUTH_DB),
    permission_service=_permission_service,
)
_file_service = FileService(
    SqliteFileRepository("sqlite:///./data/filemanagement.db"),
    LocalDiskStorageBackend("./data/files"),
    settings_registry=_settings_registry,
    permission_service=_permission_service,
)
_mail_service = MailService(permission_service=_permission_service)
_session_service = SessionService(
    SqliteSessionRepository(_AUTH_DB),
    settings_registry=_settings_registry,
    permission_service=_permission_service,
)

setup_logger()
