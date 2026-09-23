"""The permission service foundation (docs/specs/user-roles-permissions.md, D19, REQ-023).

``PermissionService`` is the RBAC use-case service. This module provides the
service's construction contract (constructor DI with the repository ABCs,
the ``UserManager``, and the structural session-lookup seam — ADR-069) and
the module singleton (``get_permission_service``) / reset
(``reset_permission_service``) (D19).

The check core (D1, T-004): ``has_permission`` / ``require_permission`` —
fail-closed (ADR-075), the ``admin`` implicit wildcard (REQ-010), the
non-admin role's zero permissions (REQ-011), the multi-role union of explicit
grants (REQ-009), the live user lookup (REQ-014), session validation via the
structural ``SessionLookup`` seam (ADR-073), and the system principal
(``user_id=None``, D10, REQ-018). Denials are logged at WARNING (never the
session token, REQ-028/NFR-002) and publish the ``PermissionDenied`` event
(REQ-020). Role CRUD and dynamic grants (T-005): ``create_role`` /
``list_roles`` / ``delete_role`` (with the deletion guards) and
``grant_permission`` / ``revoke_permission`` / ``get_role_permissions``
(validated against the catalog, idempotent, role events). The
role-assignment pass-throughs are implemented by the subsequent task (T-006).
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Iterable
from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import UUID

from loguru import logger

from backend.logging import logged_class
from backend.permissions.catalog import PermissionCatalog
from backend.permissions.errors import (
    PermissionDeniedError,
    RoleInUseError,
    RoleNotFoundError,
    RoleProtectedError,
    UnknownPermissionError,
)
from backend.permissions.events import PermissionDenied, RoleCreated, RoleDeleted, RolePermissionsChanged
from backend.permissions.models import BUILTIN_ROLES, Role, RoleRead, SessionLookup
from backend.permissions.repositories import (
    GrantRepository,
    RoleRepository,
    SqliteGrantRepository,
    SqliteRoleRepository,
    SqliteSystemPrincipalRepository,
    SystemPrincipalRepository,
)
from backend.usermanagement import UserManager, UserNotFoundError

if TYPE_CHECKING:
    from backend.permissions.events import EventPublisher
    from backend.settings import SettingsRegistry
    from backend.usermanagement import UserRead

# The permission key shape (REQ-002): hierarchical ``feature.action`` keys.
_PERMISSION_KEY_PATTERN = re.compile(r"^[a-z0-9_-]+\.[a-z0-9_-]+$")

# The role name shape (REQ-006): 1..32 lowercase alphanumeric / ``_`` / ``-``.
_ROLE_NAME_PATTERN = re.compile(r"^[a-z0-9_-]{1,32}$")


def _grant_matches(grant: str, perm: str) -> bool:
    """Whether a grant key matches a permission (exact, or a ``<feature>.*`` wildcard)."""
    if grant == perm:
        return True
    if grant.endswith(".*"):
        return perm.startswith(grant[:-1])  # "mail.*" -> the "mail." prefix
    return False


def _any_grant_matches(grants: Iterable[str], perm: str) -> bool:
    """Whether any grant key in ``grants`` matches ``perm`` (exact, or a ``<feature>.*`` wildcard)."""
    return any(_grant_matches(grant, perm) for grant in grants)


def _to_role_read(stored: Role) -> RoleRead:
    """The read-only representation of a stored role row."""
    return RoleRead(
        role=stored.role,
        description=stored.description,
        is_builtin=stored.is_builtin,
        created_at=stored.created_at,
    )


# Default persistence wiring of the module singleton (D19): the common
# persistence root ``./data/`` (ADR-056 layout convention), one database per
# feature.
DEFAULT_DATABASE_URL = "sqlite:///./data/permissions.db"
DEFAULT_USER_DATABASE_URL = "sqlite:///./data/usermanagement/users.db"


@logged_class(include_args=False)
class PermissionService:
    """The RBAC use-case service (constructor DI, REQ-023).

    The service depends only on the repository ABCs, the ``UserManager``
    (user lookup + role-assignment delegation, D8), and the structural
    session-lookup seam (D9) (ADR-069).

    The check core (D1) is fail-closed (ADR-075): every undeterminable check
    denies. The ``admin`` role is an implicit wildcard (REQ-010); the
    non-admin role starts with zero permissions (REQ-011); the effective set
    is the union of the roles' explicit grants (REQ-009); the user lookup is
    live (REQ-014); a provided session token is validated via the structural
    ``SessionLookup`` seam (ADR-073); the system principal (``user_id=None``)
    is granted the configurable system set (D10, REQ-018). The class is traced
    via ``@logged_class`` (``include_args=False`` — the session token never
    appears in a log record, REQ-028/NFR-002).
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
        self._subscribe_to_setting_changed()

    # --- Checks (D1) ---

    def has_permission(self, user_id: UUID | None, permission: str, session_token: str | None = None) -> bool:
        """Whether ``user_id`` (or the system principal when ``None``) holds ``permission``.

        Fail-closed (ADR-075): every undeterminable check returns ``False``.
        """
        reason = self._check(user_id, permission, session_token)
        if reason is None:
            return True
        self._deny(user_id, permission, reason)
        return False

    def require_permission(self, user_id: UUID | None, permission: str, session_token: str | None = None) -> None:
        """Raise :class:`PermissionDeniedError` unless the check passes (fail-closed, ADR-075)."""
        reason = self._check(user_id, permission, session_token)
        if reason is None:
            return
        self._deny(user_id, permission, reason)
        raise PermissionDeniedError(user_id, permission, reason)

    # --- System principal (D10) ---

    def set_system_permissions(self, permissions: Iterable[str]) -> None:
        """Atomically replace the system-principal set (validated against the catalog, D18).

        Each key must be a catalog action or a feature wildcard ``<feature>.*``;
        an unknown key raises :class:`UnknownPermissionError` (and the set is
        left unchanged).
        """
        for permission in permissions:
            if not self._is_valid_grant_key(permission):
                raise UnknownPermissionError(permission)
        permission_list = list(permissions)
        self._system_repository.set_permissions(permission_list)
        self._sync_settings_registry(permission_list)

    def get_system_permissions(self) -> frozenset[str]:
        """The current system-principal set (live read, D10)."""
        return self._system_repository.get_permissions()

    # --- Role CRUD + dynamic grants (D5) ---

    def create_role(self, role: str, description: str | None = None) -> RoleRead:
        """Create a runtime-managed role (REQ-006); return its :class:`RoleRead`.

        The role name must match ``^[a-z0-9_-]{1,32}$`` (a malformed name
        raises ``ValueError``); a duplicate name raises
        :class:`RoleAlreadyExistsError` (the repository contract).
        """
        if not _ROLE_NAME_PATTERN.match(role):
            raise ValueError(f"role name {role!r} is malformed (expected ^[a-z0-9_-]{{1,32}}$)")
        self._role_repository.add(role, description, is_builtin=False)
        created = self._role_repository.get(role)
        if created is None:  # defensive: the add above guarantees presence
            raise RoleNotFoundError(role)
        self._publish(RoleCreated(role=role))
        return _to_role_read(created)

    def list_roles(self) -> list[RoleRead]:
        """All roles (REQ-006)."""
        return [_to_role_read(stored) for stored in self._role_repository.list_all()]

    def delete_role(self, role: str) -> None:
        """Delete a role (and its grants) with the deletion guards (REQ-007).

        An unknown role raises :class:`RoleNotFoundError`; a built-in role
        (``admin``, ``user``) raises :class:`RoleProtectedError`; a role
        assigned to any user raises :class:`RoleInUseError`.
        """
        stored = self._role_repository.get(role)
        if stored is None:
            raise RoleNotFoundError(role)
        if stored.is_builtin:
            raise RoleProtectedError(role)
        if self._role_assigned_to_any_user(role):
            raise RoleInUseError(role)
        self._role_repository.delete(role)
        self._publish(RoleDeleted(role=role))

    def grant_permission(self, role: str, permission: str) -> None:
        """Grant ``permission`` to ``role`` (REQ-008; idempotent — no duplicate row).

        The permission must be a catalog action or a feature wildcard (an
        unknown key raises :class:`UnknownPermissionError`); an unknown role
        raises :class:`RoleNotFoundError`.
        """
        self._validate_grant(role, permission)
        self._grant_repository.grant(role, permission)
        self._publish(RolePermissionsChanged(role=role, added=[permission], removed=[]))

    def revoke_permission(self, role: str, permission: str) -> None:
        """Revoke ``permission`` from ``role`` (REQ-008; idempotent no-op when absent).

        The permission must be a catalog action or a feature wildcard (an
        unknown key raises :class:`UnknownPermissionError`); an unknown role
        raises :class:`RoleNotFoundError`.
        """
        self._validate_grant(role, permission)
        if permission in self._grant_repository.get_role_permissions(role):
            self._grant_repository.revoke(role, permission)
            self._publish(RolePermissionsChanged(role=role, added=[], removed=[permission]))

    def get_role_permissions(self, role: str) -> frozenset[str]:
        """The role's explicit grants (REQ-008); an unknown role raises
        :class:`RoleNotFoundError`."""
        if not self._role_known(role):
            raise RoleNotFoundError(role)
        return self._grant_repository.get_role_permissions(role)

    # --- Role assignment (delegates to the UserManager; D8, REQ-012) ---

    def assign_role(self, user_id: UUID, role: str) -> UserRead:
        """Assign ``role`` to ``user_id`` (replace semantics) via the UserManager.

        The permission service never mutates user roles directly (REQ-012):
        this delegates to :meth:`UserManager.set_role` (``set_roles([role])``).
        ``role`` is validated against the role store first (EDGE-026); an
        unknown role raises :class:`RoleNotFoundError`.
        """
        self._validate_assignment_role(role)
        return self._user_manager.set_role(user_id, role)

    def add_role(self, user_id: UUID, role: str) -> UserRead:
        """Add ``role`` to ``user_id`` (append semantics) via the UserManager.

        Delegates to :meth:`UserManager.add_role` (REQ-012); ``role`` is
        validated against the role store first (EDGE-026).
        """
        self._validate_assignment_role(role)
        return self._user_manager.add_role(user_id, role)

    def remove_role(self, user_id: UUID, role: str) -> UserRead:
        """Remove ``role`` from ``user_id`` via the UserManager.

        Delegates to :meth:`UserManager.remove_role` (REQ-012); the last-admin
        guard is preserved on the delegation (AC-015); ``role`` is validated
        against the role store first (EDGE-026).
        """
        self._validate_assignment_role(role)
        return self._user_manager.remove_role(user_id, role)

    def set_roles(self, user_id: UUID, roles: Iterable[str]) -> UserRead:
        """Replace ``user_id``'s roles with ``roles`` via the UserManager.

        Delegates to :meth:`UserManager.set_roles` (REQ-012); every role is
        validated against the role store first (EDGE-026).
        """
        role_list = list(roles)
        for role in role_list:
            self._validate_assignment_role(role)
        return self._user_manager.set_roles(user_id, role_list)

    def _validate_assignment_role(self, role: str) -> None:
        """Validate an assignment-pass-through role against the role store (EDGE-026).

        An unknown role (not a built-in role and not a row in the roles table)
        raises :class:`RoleNotFoundError` before the delegation.
        """
        if not self._role_known(role):
            raise RoleNotFoundError(role)

    def _validate_grant(self, role: str, permission: str) -> None:
        """Validate a grant/revoke target (REQ-008): the permission must be a catalog action or
        a feature wildcard (an unknown key raises :class:`UnknownPermissionError`); an unknown
        role raises :class:`RoleNotFoundError`."""
        if not self._is_valid_grant_key(permission):
            raise UnknownPermissionError(permission)
        if not self._role_known(role):
            raise RoleNotFoundError(role)

    def _role_known(self, role: str) -> bool:
        """Whether ``role`` is a known role (a built-in role, or a row in the roles table).

        The built-in roles (``admin``, ``user``) are always known (seeded by the
        migration in production) even before a row exists in the roles table.
        """
        return role in BUILTIN_ROLES or self._role_repository.get(role) is not None

    def _role_assigned_to_any_user(self, role: str) -> bool:
        """Whether ``role`` is assigned to any user (the multi-role UserRead, REQ-007)."""
        return any(role in user.roles for user in self._user_manager.list_users(include_inactive=True))

    # --- Check core (private; not traced) ---

    def _check(self, user_id: UUID | None, permission: str, session_token: str | None) -> str | None:  # noqa: PLR0911
        """Run the check; return ``None`` (allowed) or the denial ``reason`` (closed set, D12).

        Order: permission shape, then the principal (the user lookup precedes
        session validation, EDGE-024), then the session, then the catalog,
        then the grant evaluation (fail-closed, ADR-075).

        ``# noqa: PLR0911`` — the fail-closed check has one early return per
        denial reason (a closed set, D12); each step short-circuits the rest.
        """
        # 1. Permission key shape (REQ-002).
        if not _PERMISSION_KEY_PATTERN.match(permission):
            return "malformed_permission"
        # 2. Principal resolution (live user lookup, REQ-014; precedes session validation, EDGE-024).
        user: UserRead | None = None
        if user_id is not None:
            user, reason = self._lookup_user(user_id)
            if reason is not None:
                return reason
            if not user.is_active:
                return "inactive_user"
        # 3. Session validation (only when a token is provided; ADR-073).
        reason = self._validate_session(user_id, session_token)
        if reason is not None:
            return reason
        # 4. Catalog (REQ-004): an unknown permission denies even for admin.
        if not self._catalog.has(permission):
            return "unknown_permission"
        # 5. Grant evaluation.
        if user is None:
            # System principal (D10): the configurable system set (live read).
            system_set = self._system_repository.get_permissions()
            return None if _any_grant_matches(system_set, permission) else "unauthorized"
        # Admin implicit wildcard (REQ-010): every catalog permission, no explicit grant.
        if "admin" in user.roles:
            return None
        # Multi-role union of explicit grants (REQ-009), including feature wildcards (REQ-003).
        for role in user.roles:
            grants = self._grant_repository.get_role_permissions(role)
            if _any_grant_matches(grants, permission):
                return None
        return "unauthorized"

    def _lookup_user(self, user_id: UUID) -> tuple[UserRead | None, str | None]:
        """Live user lookup (no caching, REQ-014); map lookup failures to denial reasons."""
        try:
            user = self._user_manager.get_user(user_id)
        except UserNotFoundError:
            return None, "unknown_user"
        except Exception:
            return None, "storage_error"
        return user, None

    def _validate_session(self, user_id: UUID | None, session_token: str | None) -> str | None:
        """Validate a provided session token via the structural ``SessionLookup`` seam (ADR-073).

        The token is hashed (SHA-256) before the lookup; the token itself never
        leaves this method (REQ-028/NFR-002).
        """
        if session_token is None:
            return None  # Omitted token: validation is skipped (AC-021).
        if self._session_lookup is None:
            return "storage_error"  # Unavailable lookup: fail-closed (EDGE-007).
        token_hash = hashlib.sha256(session_token.encode("utf-8")).hexdigest()
        try:
            record = self._session_lookup.get_by_token_hash(token_hash)
        except Exception:
            return "storage_error"  # Raising lookup: fail-closed (EDGE-007).
        if record is None or record.revoked or record.expires_at < datetime.now(UTC):
            return "invalid_session"  # Unknown / revoked / expired (REQ-017).
        if record.user_id != user_id:
            return "session_principal_mismatch"  # A different user's session (REQ-017).
        return None

    def _deny(self, user_id: UUID | None, permission: str, reason: str) -> None:
        """Log the denial at WARNING (never the session token, REQ-028) and publish the event (REQ-020)."""
        logger.warning(
            "permission check denied: user_id={} permission={} reason={}",
            user_id,
            permission,
            reason,
        )
        self._publish(PermissionDenied(user_id=user_id, permission=permission, reason=reason))

    def _publish(self, event: object) -> None:
        """Publish ``event`` when an event bus is injected (a no-op otherwise, AC-025)."""
        if self._event_bus is not None:
            self._event_bus.publish(event)

    # --- Settings alias sync (D16, REQ-019) ---

    def _subscribe_to_setting_changed(self) -> None:
        """Subscribe to ``SettingChanged`` so a registry write updates the system-set table.

        The system-set table is the source of truth (D16); the registry key
        ``permissions.system_principal`` is the live-configurable alias. A
        registry write publishes ``SettingChanged``; this handler applies it to
        the table. A structural publisher without a ``subscribe`` method (the
        no-publisher mode, AC-025) skips the subscription.
        """
        bus = self._event_bus
        if bus is None:
            return
        subscribe = getattr(bus, "subscribe", None)
        if subscribe is None:
            return
        from backend.settings import SettingChanged

        subscribe(SettingChanged, self._on_setting_changed)

    def _on_setting_changed(self, event: object) -> None:
        """Apply a ``SettingChanged`` for ``permissions.system_principal`` to the table."""
        key = getattr(event, "key", None)
        if key != "permissions.system_principal":
            return
        value = getattr(event, "value", None)
        if isinstance(value, (list, tuple, set, frozenset)):
            self._system_repository.set_permissions(list(value))

    def _sync_settings_registry(self, permissions: list[str]) -> None:
        """Best-effort: sync ``permissions.system_principal`` to the registry (D16, REQ-019).

        The table is the source of truth; this mirrors the new set into the
        registry key so the alias and the table stay in sync. A missing
        registry (the no-settings mode) or an unregistered key is a no-op.
        """
        registry = self._settings_registry
        if registry is None:
            from backend.settings import get_settings_registry

            registry = get_settings_registry(required=False)
        if registry is None:
            return
        try:
            if registry.has("permissions.system_principal"):
                registry.set_value("permissions.system_principal", list(permissions))
        except Exception:
            pass  # best-effort: a registry failure never breaks the table write

    def _is_valid_grant_key(self, permission: str) -> bool:
        """Whether ``permission`` is a valid grant key (a catalog action or a feature wildcard, D18)."""
        if self._catalog.has(permission):
            return True
        if permission.endswith(".*"):
            return permission[: -len(".*")] in self._catalog.features()
        return False


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
