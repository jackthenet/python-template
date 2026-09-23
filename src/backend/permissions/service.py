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
from backend.permissions.models import BUILTIN_ROLES, RoleRead, SessionLookup
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
        self._system_repository.set_permissions(permissions)

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
        if self._event_bus is not None:
            self._event_bus.publish(RoleCreated(role=role))
        return RoleRead(
            role=created.role,
            description=created.description,
            is_builtin=created.is_builtin,
            created_at=created.created_at,
        )

    def list_roles(self) -> list[RoleRead]:
        """All roles (REQ-006)."""
        return [
            RoleRead(
                role=stored.role,
                description=stored.description,
                is_builtin=stored.is_builtin,
                created_at=stored.created_at,
            )
            for stored in self._role_repository.list_all()
        ]

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
        if self._event_bus is not None:
            self._event_bus.publish(RoleDeleted(role=role))

    def grant_permission(self, role: str, permission: str) -> None:
        """Grant ``permission`` to ``role`` (REQ-008; idempotent — no duplicate row).

        The permission must be a catalog action or a feature wildcard (an
        unknown key raises :class:`UnknownPermissionError`); an unknown role
        raises :class:`RoleNotFoundError`.
        """
        if not self._is_valid_grant_key(permission):
            raise UnknownPermissionError(permission)
        if not self._role_known(role):
            raise RoleNotFoundError(role)
        self._grant_repository.grant(role, permission)
        if self._event_bus is not None:
            self._event_bus.publish(RolePermissionsChanged(role=role, added=[permission], removed=[]))

    def revoke_permission(self, role: str, permission: str) -> None:
        """Revoke ``permission`` from ``role`` (REQ-008; idempotent no-op when absent).

        The permission must be a catalog action or a feature wildcard (an
        unknown key raises :class:`UnknownPermissionError`); an unknown role
        raises :class:`RoleNotFoundError`.
        """
        if not self._is_valid_grant_key(permission):
            raise UnknownPermissionError(permission)
        if not self._role_known(role):
            raise RoleNotFoundError(role)
        if permission in self._grant_repository.get_role_permissions(role):
            self._grant_repository.revoke(role, permission)
            if self._event_bus is not None:
                self._event_bus.publish(RolePermissionsChanged(role=role, added=[], removed=[permission]))

    def get_role_permissions(self, role: str) -> frozenset[str]:
        """The role's explicit grants (REQ-008); an unknown role raises
        :class:`RoleNotFoundError`."""
        if not self._role_known(role):
            raise RoleNotFoundError(role)
        return self._grant_repository.get_role_permissions(role)

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
        if self._event_bus is not None:
            self._event_bus.publish(PermissionDenied(user_id=user_id, permission=permission, reason=reason))

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
