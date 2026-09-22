# Spec: User Roles & Permissions (RBAC, Cross-Cutting)

## 1. Overview & Objectives
- **Feature Name:** User Roles & Permissions (RBAC)
- **Target Component:** `src/backend/permissions/` (new feature) + amendments to `src/backend/usermanagement/`, `src/backend/authentication/`, `src/backend/settings/`, `src/backend/filemanagement/`, `src/backend/mail/`, `src/backend/sessionmanagement/`, and new enforcement plumbing in `src/backend/shared/`.
- **Goal:** Provide a shared, in-process RBAC authorization capability for the backend: runtime-managed roles with dynamic role→permission grants over hierarchical `feature.action` permissions, multi-role users with union-of-permissions, fail-closed permission checks callable from backend code, and enforcement wiring at the entry points of the six existing features.
- **Scope:**
  - New `PermissionService` (`backend.permissions`) with the check API (`has_permission` / `require_permission`), role CRUD, dynamic role→permission grants, and a configurable system principal.
  - Static permission catalog derived from feature-owned `register_actions(...)` declarations at startup; initial catalog = every public service method of the six features (60 actions).
  - User-management amendment: rename `member` → `user`; single role → role list (multiple roles per user, union of permissions); role existence validated against the permission feature's role store (the single source of truth for role names); new assignment methods (`set_roles` / `add_role` / `remove_role`) with `set_role` preserved; last-admin guard preserved on every assignment path.
  - Enforcement wiring (Q-75): every enforced public service method of the six features takes a `principal: Principal` parameter and enforces `require_permission` at its entry point; session validation is part of the check (coupling to authentication).
  - SQLite persistence (new tables: roles, role→permission grants, system-principal config) behind repository ABCs with in-memory variants for tests; alembic migrations for the new tables and for the user-management role-list migration.
  - Feature-owned `register_settings(registry)` integration (live reads), typed events, structured `AuthorizationError` exception hierarchy, `@logged_class` tracing, constructor DI + module singleton + reset.
- **Out of Scope (confirmed):** frontend UI; HTTP/REST layer; multi-tenancy; MFA; JWT; groups/teams; per-user (non-role) permission grants (direct user→permission grants bypassing roles); ABAC/policy engines; persistent audit log (denials are transient logs + events only).

## 2. Architecture & Design Decisions
- **Design Pattern:** Service + repository. `PermissionService` (use cases, validation, domain rules) depends only on repository ABCs (`RoleRepository`, `GrantRepository`, `SystemPrincipalRepository`), the `UserManager` (user lookup + role-assignment delegation), and a structural session-lookup seam (authentication's session repository). SQLite implementations use SQLModel; in-memory implementations serve tests/DI. A module singleton (`get_permission_service()`) + reset (`reset_permission_service()`) follow the session-management pattern. Enforcement is a decorator (`@requires_permission`) + a `principal` parameter on enforced service methods, resolved through a structural `PermissionChecker` protocol so the six features never import `backend.permissions` (no circular imports; `Principal` / `PermissionChecker` / `requires_permission` live in `backend/shared/`).
- **Dependencies:** `sqlmodel` (existing); the shared logging feature `backend.logging` (`@logged_class`); the shared settings registry `backend.settings` (feature-owned `register_settings`, live reads); the shared event bus (structural `EventPublisher` protocol — no hard import); user-management `backend.usermanagement` (`UserManager`, `UserRead`, `InvalidRoleError`, `LastAdminError`, new `RoleStore`); authentication's session store (structural `SessionLookup` protocol — no hard import). **No new third-party dependencies.**
- **Constraints:** Fail-closed on every undeterminable check (hard invariant). The session token is a secret: it never appears in log records, events, or error messages. Breaking changes to existing public APIs are allowed **only** as enumerated in Section 13, and every break is fixed within this change's scope (Q-97). The check path, repositories, and internal state are thread-safe.
- **Design Decisions (WHAT; WHY goes to ADRs in Phase 2):**
  - D1: Check API — `has_permission(user_id, permission, session_token=None) -> bool` and `require_permission(user_id, permission, session_token=None) -> None` (raises `PermissionDeniedError` on denial). `user_id=None` denotes the system/anonymous principal.
  - D2: Permission keys — hierarchical `feature.action` matching `^[a-z0-9_-]+\.[a-z0-9_-]+$`; checks are action-level; grants may be an action key or a feature-level wildcard `<feature>.*`.
  - D3: Static catalog — the permission vocabulary is a closed set derived from feature-owned `register_actions(catalog)` declarations called at startup (mirroring `register_settings`); no runtime creation of permission names; the initial catalog is the explicit table in Section 3 (60 actions across the six features).
  - D4: Roles are runtime-managed entities — the `roles` table (permission feature) is the single source of truth for which roles exist; role CRUD lives on `PermissionService`; user-management validates role existence against an injected `RoleStore` (default `StaticRoleStore(("admin", "user"))`).
  - D5: Multiple roles per user — `User.roles: list[str]`; the effective permission set is the union of the roles' explicit grants (including wildcard grants); assignment primitives on `UserManager`: `set_role` (preserved: replaces the set with one role), `set_roles`, `add_role`, `remove_role`; the last-admin guard applies to every path that removes `admin` from the last active admin.
  - D6: The `admin` role is an implicit wildcard — a user whose roles include `admin` is granted every catalog permission without any explicit grant.
  - D7: The non-admin (`user`) role starts with zero permissions; its permissions come only from dynamic grants.
  - D8: Role assignment is delegated — the permission service's assignment pass-throughs (`assign_role` / `add_role` / `remove_role` / `set_roles`) validate role existence against the role store and delegate to the corresponding `UserManager` method (the single enforcement point of the last-admin guard); the service never mutates user roles directly.
  - D9: Session validation in the check — when `session_token` is provided, the check validates it via the session lookup (SHA-256 hash lookup): unknown/revoked/expired → deny (`invalid_session`); a session belonging to a different user → deny (`session_principal_mismatch`); when the token is omitted, session validation is skipped.
  - D10: System principal — `user_id=None` evaluates the configurable system permission set (stored in `system_principal_permissions`, live read); `set_system_permissions` / `get_system_permissions` manage it; the default (bootstrap) system set covers the internal flows (login, password reset, startup wiring, background cleanup).
  - D11: No caching — every check performs live lookups (user, roles, grants, system set, session); role and activity changes take effect on the next check, no re-login.
  - D12: Fail-closed — every undeterminable check denies with a `reason` from a closed set (`unauthorized`, `unknown_user`, `inactive_user`, `unknown_permission`, `malformed_permission`, `invalid_session`, `session_principal_mismatch`, `storage_error`) plus a WARNING log and a `PermissionDenied` event.
  - D13: Enforcement wiring — every enforced public service method of the six features takes a trailing `principal: Principal = Principal()` parameter and is decorated `@requires_permission("<feature>.<method>")`; the service resolves the check through the injected `PermissionChecker` (constructor parameter `permission_service`, default `None` → standalone mode, no enforcement); the exempt set (authentication's session-establishment/teardown/introspection operations) is declared in the catalog but not enforced.
  - D14: Shared enforcement plumbing — `Principal`, the `PermissionChecker` protocol, and the `requires_permission` decorator live in `src/backend/shared/` (generic authorization plumbing, no feature-specific business logic; avoids the user-management ↔ permissions circular import).
  - D15: Persistence — three new tables (`roles`, `role_permissions`, `system_principal_permissions`) + an alembic migration (seeds: built-in roles `admin`/`user`; the bootstrap system set); the user-management amendment adds an alembic migration (rename `member` → `user`; single `role` column → `roles` list).
  - D16: Settings integration — feature-owned `register_settings(registry)` called at startup registers `permissions.system_principal` (LIST, default = the bootstrap set) as the live-configurable alias for the system set: a registry write updates the table (via the `SettingChanged` subscription), and `set_system_permissions` syncs the key (best-effort); the check reads the table (source of truth).
  - D17: Events — `PermissionDenied`, `RoleCreated`, `RoleDeleted`, `RolePermissionsChanged`; role assignment reuses user-management's `UserRoleChanged` (no new assignment event); events carry non-sensitive data only; the publisher is optional (None → no events).
  - D18: Errors — structured exception hierarchy in `backend.permissions.errors` rooted at `AuthorizationError` (avoids colliding with the built-in `PermissionError`); `PermissionDeniedError` context: `user_id`, `permission`, `reason`; role errors carry `role`; `UnknownPermissionError` carries `permission`.
  - D19: Singleton — `get_permission_service()` lazily creates the module singleton (wired to the shared repositories/user-manager at construction); `reset_permission_service()` clears it (tests).
  - D20: Tracing — `PermissionService` is traced via `@logged_class` with `include_args=False` (session tokens are arguments and are never logged); denials are additionally logged at WARNING with the reason.

## 3. Data Structures & API Schemas

```python
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Protocol, Sequence
from uuid import UUID

from pydantic import BaseModel, Field
from sqlmodel import SQLModel, Field as SField

# --- Table models (new; permission feature) ---

class Role(SQLModel, table=True):
    __tablename__ = "roles"
    role: str = SField(primary_key=True)       # ^[a-z0-9_-]{1,32}$
    description: str | None = None
    is_builtin: bool = False                   # True for the seeded admin / user roles
    created_at: datetime                       # UTC

class RolePermission(SQLModel, table=True):
    __tablename__ = "role_permissions"
    role: str = SField(foreign_key="roles.role", primary_key=True)
    permission: str = SField(primary_key=True)  # a catalog action key or a feature wildcard <feature>.*
    granted_at: datetime                       # UTC

class SystemPrincipalPermission(SQLModel, table=True):
    __tablename__ = "system_principal_permissions"
    permission: str = SField(primary_key=True)  # a catalog action key or a feature wildcard <feature>.*
    granted_at: datetime                       # UTC
```

```python
# --- Read models (permission feature) ---

class RoleRead(BaseModel):
    role: str
    description: str | None
    is_builtin: bool
    created_at: datetime

class PermissionRead(BaseModel):
    permission: str                            # the catalog action key (feature.action)
    feature: str
    description: str | None
```

```python
# --- Lifecycle events (permission feature; D17) ---

class PermissionEvent(BaseModel):
    occurred_at: datetime                      # UTC

class PermissionDenied(PermissionEvent):
    user_id: UUID | None
    permission: str
    reason: str                                # closed set (D12)

class RoleCreated(PermissionEvent):
    role: str

class RoleDeleted(PermissionEvent):
    role: str

class RolePermissionsChanged(PermissionEvent):
    role: str
    added: list[str]
    removed: list[str]
```

```python
# --- Errors (backend.permissions.errors; D18) ---

class AuthorizationError(Exception): ...

class PermissionDeniedError(AuthorizationError):
    user_id: UUID | None
    permission: str
    reason: str                                # "unauthorized" | "unknown_user" | "inactive_user" | "unknown_permission"
                                               # | "malformed_permission" | "invalid_session" | "session_principal_mismatch" | "storage_error"

class RoleNotFoundError(AuthorizationError):
    role: str

class RoleAlreadyExistsError(AuthorizationError):
    role: str

class RoleInUseError(AuthorizationError):
    role: str

class RoleProtectedError(AuthorizationError):
    role: str

class UnknownPermissionError(AuthorizationError):
    permission: str
```

```python
# --- Repositories (permission feature; D15) ---

class RoleRepository(ABC):
    @abstractmethod
    def add(self, role: str, description: str | None, is_builtin: bool) -> None: ...
        # Raises RoleAlreadyExistsError on a duplicate role
    @abstractmethod
    def get(self, role: str) -> Role | None: ...
    @abstractmethod
    def list_all(self) -> Sequence[Role]: ...
    @abstractmethod
    def delete(self, role: str) -> None: ...

class GrantRepository(ABC):
    @abstractmethod
    def grant(self, role: str, permission: str) -> None: ...      # idempotent
    @abstractmethod
    def revoke(self, role: str, permission: str) -> None: ...     # idempotent no-op when absent
    @abstractmethod
    def get_role_permissions(self, role: str) -> frozenset[str]: ...
    @abstractmethod
    def list_all(self) -> Sequence[RolePermission]: ...

class SystemPrincipalRepository(ABC):
    @abstractmethod
    def set_permissions(self, permissions: Iterable[str]) -> None: ...   # atomic replace
    @abstractmethod
    def get_permissions(self) -> frozenset[str]: ...
```

Concrete implementations: `SqliteRoleRepository` / `SqliteGrantRepository` / `SqliteSystemPrincipalRepository` (SQLModel/SQLite; the DB file's parent directory is auto-created; thread-safe) and `MemoryRoleRepository` / `MemoryGrantRepository` / `MemorySystemPrincipalRepository` (in-memory; instances are isolated; tests/DI).

```python
# --- Structural session-validation seam (D9; the real implementation is
#     authentication's session repository, which stores SHA-256 token hashes) ---

class SessionRecord(Protocol):
    user_id: UUID
    expires_at: datetime
    revoked: bool

class SessionLookup(Protocol):
    def get_by_token_hash(self, token_hash: str) -> SessionRecord | None: ...
```

```python
# --- Shared enforcement plumbing (src/backend/shared/; D14) ---

class Principal(BaseModel):
    user_id: UUID | None = None        # None -> the system/anonymous principal
    session_token: str | None = None   # validated by the check when present

class PermissionChecker(Protocol):
    def require_permission(self, user_id: UUID | None, permission: str, session_token: str | None = None) -> None: ...
    def has_permission(self, user_id: UUID | None, permission: str, session_token: str | None = None) -> bool: ...

def requires_permission(permission_key: str):
    """Decorator for enforced service methods.

    The wrapper (1) resolves the wrapped method's `principal` parameter
    (the parameter named `principal`; default `Principal()`), (2) calls
    `self._permission_service.require_permission(principal.user_id, permission_key,
    session_token=principal.session_token)` — a no-op when
    `self._permission_service is None` (standalone mode) — and (3) invokes
    the wrapped method. A denial raises `PermissionDeniedError`.
    """
```

```python
# --- Catalog (permission feature; D3) ---

class PermissionCatalog:
    """In-memory registry of declared actions. Built at startup from the
    features' register_actions calls; closed thereafter (no runtime creation)."""
    def register_feature(self, feature: str, actions: dict[str, str]) -> None: ...
        # actions: permission key -> description; keys must match ^[a-z0-9_-]+\.[a-z0-9_-]+$n        # and start with f"{feature}."; duplicate keys raise ValueError
    def has(self, permission: str) -> bool: ...
    def features(self) -> frozenset[str]: ...
    def actions(self, feature: str | None = None) -> Sequence[PermissionRead]: ...
```

Feature-owned declaration (each feature package gains a `feature_actions.py`, mirroring `feature_settings.py`):

```python
# e.g. src/backend/mail/feature_actions.py

def register_actions(catalog: PermissionCatalog) -> None:
    catalog.register_feature("mail", {
        "mail.send_email": "Send an email via the shared mail service",
        "mail.send_password_reset_email": "Send the built-in password-reset email",
        "mail.send_email_verification_email": "Send the built-in email-verification email",
    })
```

```python
# --- Service (permission feature) ---

class PermissionService:
    def __init__(
        self,
        role_repository: RoleRepository,
        grant_repository: GrantRepository,
        system_repository: SystemPrincipalRepository,
        user_manager: UserManager,                      # user lookup + role-assignment delegation (D8)
        session_lookup: SessionLookup | None = None,   # None -> any token-based check denies (storage_error)
        catalog: PermissionCatalog | None = None,     # None -> a fresh empty catalog
        event_bus: EventPublisher | None = None,      # structural publisher; None -> no events
        settings_registry: SettingsRegistry | None = None,  # None -> no settings alias sync
    ) -> None: ...
    # Checks (D1)
    def has_permission(self, user_id: UUID | None, permission: str, session_token: str | None = None) -> bool: ...
    def require_permission(self, user_id: UUID | None, permission: str, session_token: str | None = None) -> None: ...
        # Raises PermissionDeniedError on denial (always: WARNING log + PermissionDenied event)
    # Catalog (read-only after startup; D3)
    def list_permissions(self, feature: str | None = None) -> list[PermissionRead]: ...
    # Role CRUD (D4)
    def create_role(self, role: str, description: str | None = None) -> RoleRead: ...
    def list_roles(self) -> list[RoleRead]: ...
    def delete_role(self, role: str) -> None: ...
    # Dynamic role->permission grants (D2)
    def grant_permission(self, role: str, permission: str) -> None: ...
    def revoke_permission(self, role: str, permission: str) -> None: ...
    def get_role_permissions(self, role: str) -> frozenset[str]: ...
    # Role assignment (delegates to the UserManager; D8)
    def assign_role(self, user_id: UUID, role: str) -> UserRead: ...     # = UserManager.set_role (replace with [role])
    def add_role(self, user_id: UUID, role: str) -> UserRead: ...
    def remove_role(self, user_id: UUID, role: str) -> UserRead: ...
    def set_roles(self, user_id: UUID, roles: Iterable[str]) -> UserRead: ...
    # System principal (D10)
    def set_system_permissions(self, permissions: Iterable[str]) -> None: ...
    def get_system_permissions(self) -> frozenset[str]: ...
```

Feature-owned settings (D16):

```python
# src/backend/permissions/feature_settings.py

def register_settings(registry: SettingsRegistry) -> None:
    registry.register(SettingDefinition(
        key="permissions.system_principal",
        kind=SettingKind.LIST,
        default=list(BOOTSTRAP_SYSTEM_PERMISSIONS),
        category="permissions",
        # item pattern ^[a-z0-9_-]+\.[a-z0-9_-]+$; the set is validated against the catalog
    ))
```

**Initial permission catalog (D3; the table is the source of truth).** The catalog contains exactly the public (non-underscore) methods of the six public service classes — `UserManager`, `AuthService`, `SettingsRegistry`, `FileService`, `MailService`, `SessionService`. Wiring/registration functions (`register_settings`, `register_actions`, singleton getters, reset functions) and module-level helpers are not catalog entries.

| Permission key | Description |
|----------------|-------------|
| `usermanagement.create_user` | Create a user account |
| `usermanagement.get_user` | Read a user by id |
| `usermanagement.get_user_by_username` | Read a user by username |
| `usermanagement.list_users` | List users |
| `usermanagement.update_user` | Update mutable user fields |
| `usermanagement.delete_user` | Delete a user account |
| `usermanagement.change_password` | Change a user's password |
| `usermanagement.verify_password` | Verify a user's password |
| `usermanagement.set_role` | Replace a user's roles with a single role |
| `usermanagement.activate_user` | Activate a user |
| `usermanagement.deactivate_user` | Deactivate a user |
| `authentication.login` | Log in with username/email + password |
| `authentication.session_info` | Read session metadata for a token |
| `authentication.logout` | Log out (revoke a session) |
| `authentication.request_password_reset` | Request a password reset |
| `authentication.complete_password_reset` | Complete a password reset |
| `authentication.begin_passkey_registration` | Begin passkey registration |
| `authentication.complete_passkey_registration` | Complete passkey registration |
| `authentication.begin_passkey_login` | Begin passkey login |
| `authentication.complete_passkey_login` | Complete passkey login |
| `authentication.list_passkeys` | List a user's passkeys |
| `authentication.delete_passkey` | Delete a passkey |
| `settings.register` | Register a single setting definition |
| `settings.register_feature` | Register a feature's setting definitions |
| `settings.has` | Check whether a setting key is registered |
| `settings.get_definition` | Read a setting definition |
| `settings.get_value` | Read a setting value |
| `settings.set_value` | Set a setting value (validated) |
| `settings.reset` | Reset a setting to its default |
| `settings.reset_all` | Reset all settings to their defaults |
| `settings.get_status` | Read a setting's status |
| `settings.to_view` | Read a renderable setting view |
| `settings.views` | List renderable setting views |
| `settings.grouped_views` | List setting views grouped by category/group |
| `settings.create_template` | Create a named value template |
| `settings.load_template` | Load a template's values |
| `settings.update_template` | Update a template's values |
| `settings.delete_template` | Delete a template |
| `settings.get_template` | Read a template |
| `settings.has_template` | Check whether a template exists |
| `settings.list_templates` | List templates |
| `filemanagement.upload` | Upload a file |
| `filemanagement.upload_avatar` | Upload a user's first avatar |
| `filemanagement.replace_avatar` | Replace a user's avatar |
| `filemanagement.delete_avatar` | Delete a user's avatar |
| `filemanagement.get_avatar` | Read a user's avatar |
| `filemanagement.download` | Download a file's content |
| `filemanagement.open` | Open a file as a stream |
| `filemanagement.delete` | Delete a file |
| `filemanagement.get_file` | Read a file's metadata |
| `filemanagement.list_files` | List files |
| `mail.send_email` | Send an email via the shared mail service |
| `mail.send_password_reset_email` | Send the built-in password-reset email |
| `mail.send_email_verification_email` | Send the built-in email-verification email |
| `sessionmanagement.list_sessions` | List sessions |
| `sessionmanagement.revoke_session` | Revoke a session by id |
| `sessionmanagement.logout_all_sessions` | Log out all sessions for a token's user |
| `sessionmanagement.logout_other_sessions` | Log out all sessions except the token's |
| `sessionmanagement.revoke_all_sessions` | Revoke all sessions for a user |
| `sessionmanagement.cleanup_expired` | Delete expired sessions |

**Enforced methods (D13).** Every enforced public service method gains a trailing `principal: Principal = Principal()` parameter and the `@requires_permission("<feature>.<method>")` decorator; each service constructor gains `permission_service: PermissionChecker | None = None` (default `None` → standalone mode, no enforcement). The **exempt set** (declared in the catalog but not enforced — session-establishment/teardown/introspection operations that must remain reachable): `authentication.login`, `authentication.session_info`, `authentication.logout`, `authentication.request_password_reset`, `authentication.complete_password_reset`, `authentication.begin_passkey_login`, `authentication.complete_passkey_login`.

| Feature | Enforced methods (principal parameter + decorator) | Exempt (declared, not enforced) |
|---------|------------------------------------------------------|----------------------------------|
| usermanagement | `create_user`, `get_user`, `get_user_by_username`, `list_users`, `update_user`, `delete_user`, `change_password`, `verify_password`, `set_role`, `activate_user`, `deactivate_user` (11) | — |
| authentication | `begin_passkey_registration`, `complete_passkey_registration`, `list_passkeys`, `delete_passkey` (4) | `login`, `session_info`, `logout`, `request_password_reset`, `complete_password_reset`, `begin_passkey_login`, `complete_passkey_login` (7) |
| settings | `register`, `register_feature`, `has`, `get_definition`, `get_value`, `set_value`, `reset`, `reset_all`, `get_status`, `to_view`, `views`, `grouped_views`, `create_template`, `load_template`, `update_template`, `delete_template`, `get_template`, `has_template`, `list_templates` (19) | — |
| filemanagement | `upload`, `upload_avatar`, `replace_avatar`, `delete_avatar`, `get_avatar`, `download`, `open`, `delete`, `get_file`, `list_files` (10) | — |
| mail | `send_email`, `send_password_reset_email`, `send_email_verification_email` (3) | — |
| sessionmanagement | `list_sessions`, `revoke_session`, `logout_all_sessions`, `logout_other_sessions`, `revoke_all_sessions`, `cleanup_expired` (6) | — |

Total: 53 enforced methods; 7 exempt; 60 declared actions.

**Bootstrap system set (D10).** The default system principal permission set (seeded into `system_principal_permissions` by the migration and used as the default of `permissions.system_principal`):

```python
BOOTSTRAP_SYSTEM_PERMISSIONS: frozenset[str] = frozenset({
    "usermanagement.get_user",
    "usermanagement.verify_password",
    "usermanagement.change_password",
    "settings.register",
    "settings.register_feature",
    "mail.send_email",
    "mail.send_password_reset_email",
    "mail.send_email_verification_email",
    "sessionmanagement.cleanup_expired",
})
```

This covers the internal flows that run without a user principal: login (password verification + user read), password reset (complete → `change_password`; reset email), startup settings wiring, and background session cleanup.

**User-management amendment (D4/D5; the `backend.usermanagement` schemas after this change):**

```python
# --- Table model (amended) ---

class User(SQLModel, table=True):
    __tablename__ = "users"
    # ... (id, username, email, display_name, password_hash, profile_picture_url, is_active,
    #      created_at, updated_at unchanged) ...
    roles: list[str] = SField(default_factory=list)   # was: role: str; non-empty enforced by the service

# --- Schemas (amended) ---

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    display_name: str | None = None
    roles: list[str]                                   # was: role: str; non-empty; each ^[a-z0-9_-]{1,32}$;
                                                      # existence checked against the RoleStore
    profile_picture_url: str | None = None

class UserRead(BaseModel):
    id: UUID
    username: str
    email: str
    display_name: str | None
    roles: list[str]                                   # was: role: str
    profile_picture_url: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

# --- Events (amended) ---

class UserCreated(UserEvent):
    user_id: UUID
    username: str
    email: str
    roles: list[str]                                   # was: role: str

class UserRoleChanged(UserEvent):
    user_id: UUID
    old_roles: list[str]                               # was: old_role: str
    new_roles: list[str]                               # was: new_role: str

# --- Role store (new; D4) ---

class RoleStore(ABC):
    @abstractmethod
    def has_role(self, role: str) -> bool: ...
    @abstractmethod
    def list_roles(self) -> Sequence[str]: ...

class StaticRoleStore(RoleStore):
    def __init__(self, roles: Iterable[str]) -> None: ...

# --- Service (amended) ---

class UserManager:
    def __init__(
        self,
        repository: UserRepository,
        role_store: RoleStore | None = None,          # was: roles: Iterable[str] = ("admin", "member")
        event_bus: EventPublisher | None = None,
    ) -> None: ...
    # role_store: default StaticRoleStore(("admin", "user"))
    def create_user(self, data: UserCreate) -> UserRead: ...
    def get_user(self, user_id: UUID) -> UserRead: ...
    def get_user_by_username(self, username: str) -> UserRead: ...
    def list_users(self, include_inactive: bool = False) -> list[UserRead]: ...
    def update_user(self, user_id: UUID, data: UserUpdate) -> UserRead: ...
    def delete_user(self, user_id: UUID) -> None: ...
    def change_password(self, user_id: UUID, new_password: str) -> None: ...
    def verify_password(self, user_id: UUID, password: str) -> bool: ...
    def set_role(self, user_id: UUID, role: str) -> UserRead: ...        # preserved: = set_roles([role])
    def set_roles(self, user_id: UUID, roles: Iterable[str]) -> UserRead: ...   # new
    def add_role(self, user_id: UUID, role: str) -> UserRead: ...                # new
    def remove_role(self, user_id: UUID, role: str) -> UserRead: ...             # new
    def activate_user(self, user_id: UUID) -> UserRead: ...
    def deactivate_user(self, user_id: UUID) -> UserRead: ...
```

Last-admin guard (amended): an "active admin" is an active user whose `roles` include `admin`. Operations that remove `admin` from the last active admin's roles — `set_role`, `set_roles`, `remove_role`, `delete_user`, `deactivate_user` — raise `LastAdminError`. `add_role` cannot remove `admin` and is never rejected by the guard.

**Package layout:**

```text
src/backend/permissions/
├── __init__.py            # re-exports the public API
├── models.py              # Role, RolePermission, SystemPrincipalPermission, RoleRead, PermissionRead
├── catalog.py             # PermissionCatalog
├── events.py              # PermissionEvent + lifecycle events, EventPublisher (structural)
├── errors.py              # AuthorizationError hierarchy
├── repositories.py        # RoleRepository/GrantRepository/SystemPrincipalRepository ABCs + SQLite + in-memory
├── service.py             # PermissionService, get_permission_service, reset_permission_service
└── feature_settings.py    # register_settings (permissions.system_principal)

src/backend/shared/
└── principal.py           # Principal, PermissionChecker (protocol), requires_permission (decorator)
```

**Public API (permissions; the NFR-003 contract):** `PermissionService`, `get_permission_service`, `reset_permission_service`, `PermissionCatalog`, `Role`, `RolePermission`, `SystemPrincipalPermission`, `RoleRead`, `PermissionRead`, `RoleRepository`, `SqliteRoleRepository`, `MemoryRoleRepository`, `GrantRepository`, `SqliteGrantRepository`, `MemoryGrantRepository`, `SystemPrincipalRepository`, `SqliteSystemPrincipalRepository`, `MemorySystemPrincipalRepository`, `register_settings`, `BOOTSTRAP_SYSTEM_PERMISSIONS`, `PermissionEvent`, `PermissionDenied`, `RoleCreated`, `RoleDeleted`, `RolePermissionsChanged`, `AuthorizationError`, `PermissionDeniedError`, `RoleNotFoundError`, `RoleAlreadyExistsError`, `RoleInUseError`, `RoleProtectedError`, `UnknownPermissionError`. Shared: `Principal`, `PermissionChecker`, `requires_permission`.

## 4. Requirements

Each normative requirement MUST have a stable ID. These IDs propagate through the lifecycle:
`REQ-001 → AC-001 → test → task → implementation`.

| ID | Requirement |
|----|-------------|
| REQ-001 | The service exposes the check API: `has_permission(user_id, permission, session_token=None) -> bool` and `require_permission(user_id, permission, session_token=None) -> None` (raises `PermissionDeniedError` on denial). |
| REQ-002 | Permissions are hierarchical `feature.action` keys matching `^[a-z0-9_-]+\.[a-z0-9_-]+$`; checks are action-level. |
| REQ-003 | Feature-level wildcard grants: a grant of `<feature>.*` matches every catalog action of `<feature>`. |
| REQ-004 | The permission catalog is static: a closed set derived from feature declarations at startup; no runtime creation of permission names. |
| REQ-005 | Features declare their actions via feature-owned `register_actions(catalog)` called at startup (mirroring `register_settings`); the initial catalog is the explicit table in Section 3 (60 actions across the six features). |
| REQ-006 | Roles are runtime-managed entities: `create_role`, `list_roles`, `delete_role` backed by the `roles` table. |
| REQ-007 | Role deletion is guarded: built-in roles (`admin`, `user`) cannot be deleted (`RoleProtectedError`); a role assigned to any user cannot be deleted (`RoleInUseError`); deleting an unknown role raises `RoleNotFoundError`. |
| REQ-008 | Role→permission grants are dynamic: `grant_permission`, `revoke_permission`, `get_role_permissions` backed by the `role_permissions` table; grants are validated against the catalog (an action key or a feature wildcard); an unknown permission raises `UnknownPermissionError`; an unknown role raises `RoleNotFoundError`. |
| REQ-009 | A user may hold multiple roles; the effective permission set is the union of the roles' explicit grants (including wildcard grants). |
| REQ-010 | The `admin` role is an implicit wildcard: a user whose roles include `admin` is granted every catalog permission without an explicit grant. |
| REQ-011 | The non-admin (`user`) role starts with zero permissions; its permissions come only from dynamic grants. |
| REQ-012 | Role assignment to users is delegated to the user-management assignment methods (`set_role`, `set_roles`, `add_role`, `remove_role`); the permission service never mutates user roles directly. |
| REQ-013 | The last-admin guard is preserved on every role-assignment path (no bypass): demoting, deactivating, or deleting the last active admin raises `LastAdminError`. |
| REQ-014 | Checks perform a live user lookup (no caching); role and activity changes take effect on the next check (no re-login). |
| REQ-015 | Fail-closed: every undeterminable check is denied with a `reason` and a WARNING log (unknown user, storage error, unavailable dependency, malformed or unknown permission). |
| REQ-016 | A check for an inactive (deactivated) user denies all permissions. |
| REQ-017 | When `session_token` is provided, the check validates the session via the session lookup: unknown, revoked, or expired → deny (`invalid_session`); a session belonging to a different user → deny (`session_principal_mismatch`); when the token is omitted, session validation is skipped. |
| REQ-018 | The system principal (`user_id=None`) is granted the configurable system permission set (stored in `system_principal_permissions`, live read); `set_system_permissions` / `get_system_permissions` manage it. |
| REQ-019 | Settings integration: feature-owned `register_settings(registry)` called at startup registers `permissions.system_principal` (LIST, default = the bootstrap set) as the live-configurable alias for the system set: a registry write updates the table (via the `SettingChanged` subscription), and `set_system_permissions` syncs the key (best-effort). |
| REQ-020 | Events: `PermissionDenied` (on every denial), `RoleCreated`, `RoleDeleted`, `RolePermissionsChanged`; role assignment reuses user-management's `UserRoleChanged`; events carry non-sensitive data only; the publisher is optional (None → no events, no errors). |
| REQ-021 | Errors: a structured exception hierarchy in `backend.permissions.errors` rooted at `AuthorizationError` (no collision with the built-in `PermissionError`); `PermissionDeniedError` context: `user_id`, `permission`, `reason`; role errors carry `role`. |
| REQ-022 | Persistence: the `roles`, `role_permissions`, and `system_principal_permissions` tables (SQLModel/SQLite) behind the repository ABCs; an alembic migration creates them and seeds the built-in roles and the bootstrap system set. |
| REQ-023 | Construction and testing: constructor DI with the repository ABCs + `UserManager`; in-memory repositories for tests/DI; a module singleton `get_permission_service()` + `reset_permission_service()`. |
| REQ-024 | Enforcement wiring: every enforced public service method of the six features takes a trailing `principal: Principal = Principal()` parameter and enforces `require_permission("<feature>.<method>")` at entry (via `@requires_permission`); the exempt set (authentication's session-establishment/teardown/introspection operations) is declared but not enforced. |
| REQ-025 | The principal model: `Principal(user_id: UUID | None = None, session_token: str | None = None)`; `Principal()` is the system principal. |
| REQ-026 | User-management amendment: multiple roles per user (`User.roles: list[str]`, `UserCreate.roles`, `UserRead.roles`), role existence validated against an injected `RoleStore` (default `StaticRoleStore(("admin", "user"))`), new assignment methods `set_roles` / `add_role` / `remove_role` with `set_role` preserved as `set_roles([role])`, event field changes (`UserRoleChanged.old_roles`/`new_roles`, `UserCreated.roles`), the `member` → `user` rename, and a data migration. |
| REQ-027 | Thread safety: the check path, repositories, and internal state are safe for concurrent use from multiple threads. |
| REQ-028 | Observability: `PermissionService` is traced via the shared logging feature (`@logged_class`, `include_args=False`); denials are logged at WARNING with the reason; session tokens never appear in any log record. |
| REQ-029 | Performance: a check completes in < 5 ms (median) in-process, including the user/role/grant SQLite lookups and `@logged` tracing, measured with the synchronous console sink active. |

## 5. Acceptance Criteria

Each acceptance criterion MUST have a stable ID and MUST reference at least one requirement. Use Given/When/Then format.

| ID | References | Criterion |
|----|------------|-----------|
| AC-001 | REQ-001 | **Given** a user whose role is granted `usermanagement.get_user`, **When** `has_permission(user_id, "usermanagement.get_user")` is called, **Then** `True` is returned, **And** when `require_permission(user_id, "usermanagement.get_user")` is called, **Then** no exception is raised. |
| AC-002 | REQ-001 | **Given** a user without `usermanagement.delete_user`, **When** `has_permission(user_id, "usermanagement.delete_user")` is called, **Then** `False` is returned, **And** when `require_permission(user_id, "usermanagement.delete_user")` is called, **Then** a `PermissionDeniedError` is raised with `user_id`, `permission="usermanagement.delete_user"`, `reason="unauthorized"`. |
| AC-003 | REQ-002 | **Given** a check for a key that does not match the permission pattern (e.g., `Usermanagement.get_user`), **When** `has_permission` is called, **Then** `False` is returned (reason `malformed_permission`) **And** a WARNING is logged. |
| AC-004 | REQ-003 | **Given** a role granted `settings.*`, **When** `has_permission(user_id, "settings.get_value")` is called for a holder of that role, **Then** `True` is returned, **And** when `has_permission(user_id, "mail.send_email")` is called, **Then** `False` is returned. |
| AC-005 | REQ-004 | **Given** the catalog built at startup, **When** a check is made for a key not in the catalog (e.g., `reports.export`), **Then** the check denies (reason `unknown_permission`) **And** a WARNING is logged, **And** when `grant_permission(role, "reports.export")` is called, **Then** an `UnknownPermissionError` is raised. |
| AC-006 | REQ-005 | **Given** the six features' `register_actions` called at startup, **When** the catalog is inspected, **Then** it contains exactly the 60 keys of the initial catalog table, grouped by the six features. |
| AC-007 | REQ-006 | **Given** the role store, **When** `create_role("editor", description="Content editor")` is called, **Then** a `RoleRead` with `role="editor"`, `is_builtin=False` is returned, **And** when `list_roles()` is called, **Then** `editor` is present. |
| AC-008 | REQ-007 | **Given** the built-in role `admin`, **When** `delete_role("admin")` is called, **Then** a `RoleProtectedError` is raised, **And** given a role assigned to a user, **When** `delete_role` is called, **Then** a `RoleInUseError` is raised, **And** given an unknown role, **When** `delete_role` is called, **Then** a `RoleNotFoundError` is raised. |
| AC-009 | REQ-008 | **Given** the role `user`, **When** `grant_permission("user", "usermanagement.get_user")` is called, **Then** `get_role_permissions("user")` contains it, **And** when `revoke_permission("user", "usermanagement.get_user")` is called, **Then** it no longer contains it. |
| AC-010 | REQ-008 | **Given** the role `user`, **When** `grant_permission("user", "mail.*")` is called, **Then** the wildcard grant is stored, **And** when `has_permission(user_id, "mail.send_email")` is called for a holder of that role, **Then** `True` is returned. |
| AC-011 | REQ-009 | **Given** a user with roles `[a, b]` where `a` is granted `p1` and `b` is granted `p2`, **When** `has_permission` is called for `p1` and for `p2`, **Then** both return `True` (union). |
| AC-012 | REQ-010 | **Given** a user with the `admin` role, **When** `has_permission` is called for any catalog permission, **Then** `True` is returned, including for permissions not explicitly granted to `admin`. |
| AC-013 | REQ-011 | **Given** a freshly created user with the `user` role, **When** `has_permission` is called for any catalog permission, **Then** `False` is returned (zero permissions). |
| AC-014 | REQ-012 | **Given** the permission service, **When** `assign_role` / `add_role` / `remove_role` / `set_roles` are called, **Then** the corresponding `UserManager` method is invoked (delegation) **And** the service does not write user roles directly. |
| AC-015 | REQ-013 | **Given** the last active admin, **When** `remove_role(last_admin_id, "admin")` is called via the service, **Then** a `LastAdminError` is raised (from the delegation) **And** the user's roles are unchanged. |
| AC-016 | REQ-014 | **Given** a user denied `p`, **When** the role holding `p` is granted to the user, **And** when `has_permission(user_id, p)` is called again, **Then** `True` is returned (immediate effect, no re-login, no cache). |
| AC-017 | REQ-015 | **Given** an unknown user id, **When** `has_permission` is called, **Then** `False` is returned (reason `unknown_user`) **And** a WARNING is logged, **And** when `require_permission` is called, **Then** a `PermissionDeniedError` with `reason="unknown_user"` is raised. |
| AC-018 | REQ-015 | **Given** a user lookup that raises (storage failure), **When** `has_permission` is called, **Then** `False` is returned (reason `storage_error`) **And** no exception other than the denial is propagated. |
| AC-019 | REQ-016 | **Given** an inactive user with the `admin` role, **When** `has_permission` is called for any catalog permission, **Then** `False` is returned (reason `inactive_user`). |
| AC-020 | REQ-017 | **Given** a valid, unrevoked, unexpired session token for user `u`, **When** `has_permission(u, p, session_token=t)` is called, **Then** the session is validated and the check proceeds with the user/role evaluation, **And** given a revoked token, **When** the check is called, **Then** `False` is returned (reason `invalid_session`), **And** given a token belonging to a different user, **When** `has_permission(u, p, session_token=t2)` is called, **Then** `False` is returned (reason `session_principal_mismatch`). |
| AC-021 | REQ-017 | **Given** a check with `session_token=None`, **When** the check is called, **Then** session validation is skipped and the user/role evaluation proceeds. |
| AC-022 | REQ-018 | **Given** a system set `{p1}`, **When** `has_permission(None, p1)` is called, **Then** `True` is returned, **And** when `has_permission(None, p2)` is called, **Then** `False` is returned, **And** when `set_system_permissions({p3})` is called, **And** when `has_permission(None, p3)` is called, **Then** `True` is returned (immediate effect). |
| AC-023 | REQ-019 | **Given** `register_settings` called and the registry live, **When** `set_value("permissions.system_principal", [p4])` is called, **Then** the system-set table is updated (via `SettingChanged`), **And** when `set_system_permissions([p5])` is called, **Then** the registry key is synced (best-effort). |
| AC-024 | REQ-020 | **Given** a publisher that collects events, **When** a denial occurs, **Then** a `PermissionDenied(user_id, permission, reason)` event is published, **And** when `create_role` / `delete_role` / `grant_permission` / `revoke_permission` succeed, **Then** `RoleCreated` / `RoleDeleted` / `RolePermissionsChanged` events are published, **And** when an assignment pass-through succeeds, **Then** no permission-feature event is published (the assignment event is user-management's `UserRoleChanged`). |
| AC-025 | REQ-020 | **Given** a service without a publisher, **When** all operations are called, **Then** they work normally (no events, no errors). |
| AC-026 | REQ-021 | **Given** a `PermissionDeniedError`, **When** it is caught, **Then** the context `user_id`, `permission`, `reason` is present, **And** given a role error, **When** it is caught, **Then** the context `role` is present. |
| AC-027 | REQ-022 | **Given** the alembic migration applied to a fresh database, **When** the tables are inspected, **Then** `roles` is seeded with `admin` and `user` (both `is_builtin=True`) **And** `system_principal_permissions` is seeded with the bootstrap set **And** the SQLite repositories work on the same file. |
| AC-028 | REQ-023 | **Given** the in-memory repositories, **When** the full service API is exercised, **Then** it works without SQLite, **And** given the singleton, **When** `get_permission_service()` is called twice, **Then** the same instance is returned, **And** when `reset_permission_service()` is called, **Then** the singleton is cleared. |
| AC-029 | REQ-024 | **Given** a `FileService` with an injected permission checker, **When** `upload` is called with a principal lacking `filemanagement.upload`, **Then** a `PermissionDeniedError` is raised, **And** when it is called with a principal holding it, **Then** the upload proceeds. |
| AC-030 | REQ-024 | **Given** the exempt operation `authentication.login`, **When** it is called, **Then** no permission check is performed on `login` itself **And** the login flow succeeds for a user with zero permissions (the internal user-management/mail calls are evaluated against the bootstrap system set). |
| AC-031 | REQ-024 | **Given** a service constructed without an injected permission checker (standalone), **When** an enforced method is called, **Then** no check is performed (open, as today). |
| AC-032 | REQ-025 | **Given** `Principal()`, **When** it is inspected, **Then** `user_id=None` and `session_token=None` (the system principal), **And** given `Principal(user_id=u, session_token=t)`, **When** it is inspected, **Then** the fields are set. |
| AC-033 | REQ-026 | **Given** the amended `UserManager`, **When** `create_user` is called with `roles=["admin", "user"]`, **Then** a `UserRead` with `roles=["admin", "user"]` is returned, **And** when `create_user` is called with `roles=["nonexistent"]`, **Then** an `InvalidRoleError` is raised. |
| AC-034 | REQ-026 | **Given** a user with `roles=["user"]`, **When** `add_role(u, "admin")` is called, **Then** `roles=["user", "admin"]` is returned, **And** when `remove_role(u, "user")` is called, **Then** `roles=["admin"]` is returned, **And** when `set_role(u, "user")` is called, **Then** `roles=["user"]` is returned (replaced). |
| AC-035 | REQ-026 | **Given** an existing user-management database, **When** the migration is applied, **Then** role values `member` become `user`, the single role column becomes a role list, **And** all users are readable. |
| AC-036 | REQ-026 | **Given** the last active admin with `roles=["admin", "user"]`, **When** `remove_role(last_admin_id, "admin")` is called, **Then** a `LastAdminError` is raised, **And** when `set_roles(last_admin_id, ["user"])` is called, **Then** a `LastAdminError` is raised. |
| AC-037 | REQ-026 | **Given** a successful `set_roles`, **When** the event is inspected, **Then** a `UserRoleChanged` event is published with `old_roles` and `new_roles` as lists, **And** given a successful `create_user`, **Then** a `UserCreated` event is published with `roles` as a list. |
| AC-038 | REQ-027 | **Given** concurrent checks and role/grant changes from multiple threads, **When** they are executed, **Then** no exception is raised **And** no partial state is left **And** the results are consistent with the final state. |
| AC-039 | REQ-028 | **Given** the traced service, **When** a check with a session token is denied, **Then** the WARNING log contains `user_id`, `permission`, `reason` **And** no log record contains the session token. |
| AC-040 | REQ-029 | **Given** the measurement context (local SQLite, the shared logging feature at default INFO level with the synchronous console sink active, `@logged` tracing on), **When** a check is measured, **Then** it completes in < 5 ms (median). |

## 6. Invariants

State invariants that hold over a large input space. These become Hypothesis property-based tests.

| ID | Invariant |
|----|-----------|
| INV-001 | For any user state (active/inactive, role set) and any sequence of grant/revoke operations: `has_permission(user_id, p)` returns `True` if and only if the user is active and (the roles include `admin` or `p` is in the union of the roles' explicit grants, including wildcard matches); otherwise it returns `False`. |
| INV-002 | For any undeterminable state (unknown user, storage error, malformed or unknown permission, invalid or mismatched session, unavailable dependency): the check is never `True` — `has_permission` returns `False` and `require_permission` raises `PermissionDeniedError`. |
| INV-003 | For any sequence of assignment operations that does not raise: if any user has `admin` in their roles, at least one such user is active (the last-admin invariant). |
| INV-004 | The effective permission set is monotone in the role set: for any role sets R ⊆ R', effective(R) ⊆ effective(R'). |
| INV-005 | For any catalog permission (including permissions declared after the user's creation): a user with `admin` in their roles passes the check. |
| INV-006 | The set of valid grant keys is exactly the catalog actions ∪ the feature wildcards `{<f>.* : f in the catalog's features}`; a grant of any other key raises. |

## 7. Edge Cases & Error Conditions

| ID | Condition | Expected Behavior |
|----|-----------|-------------------|
| EDGE-001 | A check with a malformed permission key (`no-dot`, `UPPER.case`, `a.b.c`) | Deny (reason `malformed_permission`) + WARNING log |
| EDGE-002 | A check with an unknown permission (not in the catalog) | Deny (reason `unknown_permission`) + WARNING log |
| EDGE-003 | A check with an unknown user | Deny (reason `unknown_user`) + WARNING log |
| EDGE-004 | A check with an inactive user (even with `admin`) | Deny (reason `inactive_user`) |
| EDGE-005 | A check with a revoked or expired session token | Deny (reason `invalid_session`) |
| EDGE-006 | A check with a token belonging to a different user | Deny (reason `session_principal_mismatch`) |
| EDGE-007 | A check with a token when the session lookup is unavailable (None or raises) | Deny (reason `storage_error`) |
| EDGE-008 | A role with no permission mapping | Zero permissions: all checks for its holders deny (reason `unauthorized`) |
| EDGE-009 | A user deleted between the lookup and the check (concurrent) | Fail-closed deny: the live lookup re-resolves; the user absent at check time → reason `unknown_user` |
| EDGE-010 | Concurrent checks and role changes from multiple threads | Thread-safe; no partial state |
| EDGE-011 | A check when the user lookup raises (storage failure) | Deny (reason `storage_error`), never a crash |
| EDGE-012 | `delete_role` of a built-in role | A `RoleProtectedError` is raised |
| EDGE-013 | `delete_role` of a role assigned to any user | A `RoleInUseError` is raised |
| EDGE-014 | `create_role` of a duplicate role | A `RoleAlreadyExistsError` is raised |
| EDGE-015 | `create_role` with a malformed name (uppercase, > 32 chars) | A `ValueError` is raised |
| EDGE-016 | `grant_permission` of an unknown permission | An `UnknownPermissionError` is raised |
| EDGE-017 | `grant_permission` / `revoke_permission` / `get_role_permissions` of an unknown role | A `RoleNotFoundError` is raised |
| EDGE-018 | `revoke_permission` of an absent grant | Idempotent no-op |
| EDGE-019 | `grant_permission` of an already-granted permission | Idempotent (no error, no duplicate row) |
| EDGE-020 | `set_system_permissions` with an unknown permission | An `UnknownPermissionError` is raised |
| EDGE-021 | `set_system_permissions` with a feature wildcard (`mail.*`) | Allowed; it matches the mail actions on system checks |
| EDGE-022 | An enforced method called without an explicit principal (default) | Evaluated as the system principal (the system set) |
| EDGE-023 | `login` before any permission exists (a zero-permission user) | Login succeeds (exempt; the internal calls are covered by the bootstrap system set) |
| EDGE-024 | A session token for a user deleted after login | Deny (reason `unknown_user`) — the user lookup precedes session validation |
| EDGE-025 | A check with a token for a user whose session is expired | Deny (reason `invalid_session`) |
| EDGE-026 | An assignment pass-through with an unknown role (e.g., `add_role(u, "nonexistent")`) | A `RoleNotFoundError` is raised (the service validates against the role store before delegation) |

## 8. Non-Functional Requirements

| ID | Category | Requirement |
|----|----------|-------------|
| NFR-001 | Performance | A check (`has_permission` / `require_permission`) completes in < 5 ms (median) in-process, including the user/role/grant SQLite lookups and the `@logged` tracing overhead, measured against a local SQLite database with the shared logging feature at default INFO level and the synchronous console sink active. |
| NFR-002 | Security | Fail-closed is a hard invariant: every undeterminable check denies. Session tokens are secrets: they never appear in log records, events, or error messages. Events carry non-sensitive data only. The exception hierarchy is rooted at `AuthorizationError` (no shadowing of the built-in `PermissionError`). |
| NFR-003 | Contract | The public API of the new feature (`PermissionService`, the repositories, `Principal`, the catalog, the errors, the events, the singleton) is stable within this change. Breaking changes to the six existing features are limited to the enumerated list in Section 13 (Q-97), and every break is fixed within this change's scope. |
| NFR-004 | Reliability | The check path, repositories, and internal state are safe for concurrent use from multiple threads; the SQLite repositories are thread-safe; a failed operation leaves no partial state. |
| NFR-005 | Observability | `PermissionService` operations are traced via the shared logging feature; denials are logged at WARNING with the reason; session tokens never appear in any log record. |

## 9. Observability & Logging

Every feature MUST be observable. Specify the logging behavior: which operations are logged, at what level, and with what context.

- `PermissionService` is decorated with `@logged_class` from the shared logging feature: every public method is traced with an entry line, an exit line (elapsed ms), and an exception line on error.
- `include_args` stays `False`: method arguments (including any session token) are never logged.
- Every denial (from `has_permission` returning `False` or `require_permission` raising) is additionally logged at WARNING with `user_id`, `permission`, and `reason` — never the session token.
- Domain error messages carry no secrets (only error kind, role names, and permission keys), so exception lines are safe.

| Operation / Event | Level | Context |
|-------------------|-------|---------|
| Any service method call (entry/exit) | DEBUG | method qualname, elapsed ms |
| Check denial | WARNING | user_id, permission, reason (never the session token) |
| Role created / deleted | DEBUG | role |
| Role permissions changed | DEBUG | role, added, removed |
| Domain error (`RoleNotFoundError`, `RoleAlreadyExistsError`, `RoleInUseError`, `RoleProtectedError`, `UnknownPermissionError`) | DEBUG (exception line) | error type + message (no secrets) |

- **Default level:** DEBUG tracing (off at INFO); denials are logged at WARNING; domain errors are logged with type + message.
- **Error conditions:** denials and domain errors are logged as above; session tokens never appear in any log record (NFR-002).

## 10. Test Strategy

Map each requirement/AC to a test category. This drives the test file layout.

| ID | Test Category | Test File | Test Function |
|----|---------------|-----------|---------------|
| REQ-001 | acceptance | `tests/acceptance/permissions/test_check_api.py` | `test_granted_permission_allowed` |
| REQ-002 | acceptance | `tests/acceptance/permissions/test_check_api.py` | `test_malformed_permission_denied` |
| REQ-003 | acceptance | `tests/acceptance/permissions/test_check_api.py` | `test_feature_wildcard_grant` |
| REQ-004 | acceptance | `tests/acceptance/permissions/test_check_api.py` | `test_unknown_permission_denied_and_grant_rejected` |
| REQ-005 | acceptance | `tests/acceptance/permissions/test_check_api.py` | `test_initial_catalog_exactly_60_keys` |
| REQ-006 | acceptance | `tests/acceptance/permissions/test_role_management.py` | `test_create_role_and_list` |
| REQ-007 | acceptance | `tests/acceptance/permissions/test_role_management.py` | `test_delete_role_guards` |
| REQ-008 | acceptance | `tests/acceptance/permissions/test_role_management.py` | `test_grant_and_revoke_role_permission` |
| REQ-009 | acceptance | `tests/acceptance/permissions/test_check_api.py` | `test_multi_role_union_of_permissions` |
| REQ-010 | acceptance | `tests/acceptance/permissions/test_check_api.py` | `test_admin_wildcard_allows_all` |
| REQ-011 | acceptance | `tests/acceptance/permissions/test_check_api.py` | `test_user_role_starts_with_zero_permissions` |
| REQ-012 | acceptance | `tests/acceptance/permissions/test_check_api.py` | `test_assignment_delegates_to_user_manager` |
| REQ-013 | acceptance | `tests/acceptance/permissions/test_check_api.py` | `test_last_admin_guard_preserved_via_service` |
| REQ-014 | acceptance | `tests/acceptance/permissions/test_check_api.py` | `test_grant_change_takes_effect_immediately` |
| REQ-015 | acceptance | `tests/acceptance/permissions/test_check_api.py` | `test_unknown_user_denied` |
| REQ-016 | acceptance | `tests/acceptance/permissions/test_check_api.py` | `test_inactive_user_denied_even_admin` |
| REQ-017 | acceptance | `tests/acceptance/permissions/test_check_api.py` | `test_session_validation_in_check` |
| REQ-018 | acceptance | `tests/acceptance/permissions/test_system_principal.py` | `test_system_principal_check_and_set` |
| REQ-019 | acceptance | `tests/acceptance/permissions/test_system_principal.py` | `test_system_set_settings_alias_sync` |
| REQ-020 | acceptance | `tests/acceptance/permissions/test_events.py` | `test_events_published_on_operations` |
| REQ-021 | acceptance | `tests/acceptance/permissions/test_errors.py` | `test_error_context_attributes` |
| REQ-022 | integration | `tests/integration/permissions/test_persistence.py` | `test_migration_seeds_roles_and_system_set` |
| REQ-023 | integration | `tests/integration/permissions/test_persistence.py` | `test_in_memory_repos_and_singleton` |
| REQ-024 | acceptance | `tests/acceptance/permissions/test_enforcement.py` | `test_enforced_method_denies_without_permission` |
| REQ-025 | acceptance | `tests/acceptance/permissions/test_enforcement.py` | `test_principal_defaults_and_fields` |
| REQ-026 | acceptance | `tests/acceptance/usermanagement/test_multi_role.py` | `test_create_user_with_roles_list` |
| REQ-027 | integration | `tests/integration/permissions/test_thread_safety.py` | `test_concurrent_checks_and_changes` |
| REQ-028 | acceptance | `tests/acceptance/permissions/test_check_api.py` | `test_denial_log_and_no_token_leak` |
| REQ-029 | contract | `tests/contract/permissions/test_performance.py` | `test_check_latency_under_5ms_median` |
| AC-001 | acceptance | `tests/acceptance/permissions/test_check_api.py` | `test_granted_permission_allowed` |
| AC-002 | acceptance | `tests/acceptance/permissions/test_check_api.py` | `test_denied_permission_raises_with_context` |
| AC-003 | acceptance | `tests/acceptance/permissions/test_check_api.py` | `test_malformed_permission_denied` |
| AC-004 | acceptance | `tests/acceptance/permissions/test_check_api.py` | `test_feature_wildcard_grant` |
| AC-005 | acceptance | `tests/acceptance/permissions/test_check_api.py` | `test_unknown_permission_denied_and_grant_rejected` |
| AC-006 | acceptance | `tests/acceptance/permissions/test_check_api.py` | `test_initial_catalog_exactly_60_keys` |
| AC-007 | acceptance | `tests/acceptance/permissions/test_role_management.py` | `test_create_role_and_list` |
| AC-008 | acceptance | `tests/acceptance/permissions/test_role_management.py` | `test_delete_role_guards` |
| AC-009 | acceptance | `tests/acceptance/permissions/test_role_management.py` | `test_grant_and_revoke_role_permission` |
| AC-010 | acceptance | `tests/acceptance/permissions/test_role_management.py` | `test_wildcard_grant_stored_and_matches` |
| AC-011 | acceptance | `tests/acceptance/permissions/test_check_api.py` | `test_multi_role_union_of_permissions` |
| AC-012 | acceptance | `tests/acceptance/permissions/test_check_api.py` | `test_admin_wildcard_allows_all` |
| AC-013 | acceptance | `tests/acceptance/permissions/test_check_api.py` | `test_user_role_starts_with_zero_permissions` |
| AC-014 | acceptance | `tests/acceptance/permissions/test_check_api.py` | `test_assignment_delegates_to_user_manager` |
| AC-015 | acceptance | `tests/acceptance/permissions/test_check_api.py` | `test_last_admin_guard_preserved_via_service` |
| AC-016 | acceptance | `tests/acceptance/permissions/test_check_api.py` | `test_grant_change_takes_effect_immediately` |
| AC-017 | acceptance | `tests/acceptance/permissions/test_check_api.py` | `test_unknown_user_denied` |
| AC-018 | acceptance | `tests/acceptance/permissions/test_check_api.py` | `test_storage_error_denied_fail_closed` |
| AC-019 | acceptance | `tests/acceptance/permissions/test_check_api.py` | `test_inactive_user_denied_even_admin` |
| AC-020 | acceptance | `tests/acceptance/permissions/test_check_api.py` | `test_session_validation_in_check` |
| AC-021 | acceptance | `tests/acceptance/permissions/test_check_api.py` | `test_session_validation_skipped_when_token_none` |
| AC-022 | acceptance | `tests/acceptance/permissions/test_system_principal.py` | `test_system_principal_check_and_set` |
| AC-023 | acceptance | `tests/acceptance/permissions/test_system_principal.py` | `test_system_set_settings_alias_sync` |
| AC-024 | acceptance | `tests/acceptance/permissions/test_events.py` | `test_events_published_on_operations` |
| AC-025 | acceptance | `tests/acceptance/permissions/test_events.py` | `test_no_publisher_still_works` |
| AC-026 | acceptance | `tests/acceptance/permissions/test_errors.py` | `test_error_context_attributes` |
| AC-027 | integration | `tests/integration/permissions/test_persistence.py` | `test_migration_seeds_roles_and_system_set` |
| AC-028 | integration | `tests/integration/permissions/test_persistence.py` | `test_in_memory_repos_and_singleton` |
| AC-029 | acceptance | `tests/acceptance/permissions/test_enforcement.py` | `test_enforced_method_denies_without_permission` |
| AC-030 | acceptance | `tests/acceptance/permissions/test_enforcement.py` | `test_exempt_login_no_check` |
| AC-031 | acceptance | `tests/acceptance/permissions/test_enforcement.py` | `test_standalone_mode_no_check` |
| AC-032 | acceptance | `tests/acceptance/permissions/test_enforcement.py` | `test_principal_defaults_and_fields` |
| AC-033 | acceptance | `tests/acceptance/usermanagement/test_multi_role.py` | `test_create_user_with_roles_list` |
| AC-034 | acceptance | `tests/acceptance/usermanagement/test_multi_role.py` | `test_add_remove_set_roles` |
| AC-035 | acceptance | `tests/acceptance/usermanagement/test_multi_role.py` | `test_migration_member_to_user_and_role_list` |
| AC-036 | acceptance | `tests/acceptance/usermanagement/test_multi_role.py` | `test_last_admin_guard_all_paths` |
| AC-037 | acceptance | `tests/acceptance/usermanagement/test_multi_role.py` | `test_role_events_carry_lists` |
| AC-038 | integration | `tests/integration/permissions/test_thread_safety.py` | `test_concurrent_checks_and_changes` |
| AC-039 | acceptance | `tests/acceptance/permissions/test_check_api.py` | `test_denial_log_and_no_token_leak` |
| AC-040 | contract | `tests/contract/permissions/test_performance.py` | `test_check_latency_under_5ms_median` |
| INV-001 | property | `tests/property/permissions/test_invariants.py` | `test_check_true_iff_granted_and_active` |
| INV-002 | property | `tests/property/permissions/test_invariants.py` | `test_undeterminable_never_true` |
| INV-003 | property | `tests/property/permissions/test_invariants.py` | `test_last_admin_invariant` |
| INV-004 | property | `tests/property/permissions/test_invariants.py` | `test_effective_set_monotone` |
| INV-005 | property | `tests/property/permissions/test_invariants.py` | `test_admin_passes_any_catalog_permission` |
| INV-006 | property | `tests/property/permissions/test_invariants.py` | `test_valid_grant_keys_exactly_catalog_plus_wildcards` |
| EDGE-001 | unit | `tests/unit/permissions/test_edge_cases.py` | `test_malformed_key_denied` |
| EDGE-002 | unit | `tests/unit/permissions/test_edge_cases.py` | `test_unknown_permission_denied` |
| EDGE-003 | unit | `tests/unit/permissions/test_edge_cases.py` | `test_unknown_user_denied` |
| EDGE-004 | unit | `tests/unit/permissions/test_edge_cases.py` | `test_inactive_user_denied` |
| EDGE-005 | unit | `tests/unit/permissions/test_edge_cases.py` | `test_revoked_expired_token_denied` |
| EDGE-006 | unit | `tests/unit/permissions/test_edge_cases.py` | `test_mismatched_token_denied` |
| EDGE-007 | unit | `tests/unit/permissions/test_edge_cases.py` | `test_unavailable_session_lookup_denied` |
| EDGE-008 | unit | `tests/unit/permissions/test_edge_cases.py` | `test_role_no_mapping_zero_permissions` |
| EDGE-009 | unit | `tests/unit/permissions/test_edge_cases.py` | `test_user_deleted_concurrent_denied` |
| EDGE-010 | unit | `tests/unit/permissions/test_edge_cases.py` | `test_concurrent_thread_safe` |
| EDGE-011 | unit | `tests/unit/permissions/test_edge_cases.py` | `test_lookup_raises_denied` |
| EDGE-012 | unit | `tests/unit/permissions/test_edge_cases.py` | `test_delete_builtin_role_protected` |
| EDGE-013 | unit | `tests/unit/permissions/test_edge_cases.py` | `test_delete_in_use_role` |
| EDGE-014 | unit | `tests/unit/permissions/test_edge_cases.py` | `test_create_duplicate_role` |
| EDGE-015 | unit | `tests/unit/permissions/test_edge_cases.py` | `test_create_malformed_name` |
| EDGE-016 | unit | `tests/unit/permissions/test_edge_cases.py` | `test_grant_unknown_permission` |
| EDGE-017 | unit | `tests/unit/permissions/test_edge_cases.py` | `test_unknown_role_operations` |
| EDGE-018 | unit | `tests/unit/permissions/test_edge_cases.py` | `test_revoke_absent_idempotent` |
| EDGE-019 | unit | `tests/unit/permissions/test_edge_cases.py` | `test_grant_existing_idempotent` |
| EDGE-020 | unit | `tests/unit/permissions/test_edge_cases.py` | `test_set_system_unknown_permission` |
| EDGE-021 | unit | `tests/unit/permissions/test_edge_cases.py` | `test_set_system_wildcard_allowed` |
| EDGE-022 | unit | `tests/unit/permissions/test_edge_cases.py` | `test_default_principal_system` |
| EDGE-023 | unit | `tests/unit/permissions/test_edge_cases.py` | `test_login_before_permissions` |
| EDGE-024 | unit | `tests/unit/permissions/test_edge_cases.py` | `test_token_deleted_user_denied` |
| EDGE-025 | unit | `tests/unit/permissions/test_edge_cases.py` | `test_expired_session_denied` |
| EDGE-026 | unit | `tests/unit/permissions/test_edge_cases.py` | `test_assignment_unknown_role` |
| NFR-001 | contract | `tests/contract/permissions/test_performance.py` | `test_check_latency_under_5ms_median` |
| NFR-002 | property | `tests/property/permissions/test_invariants.py` | `test_undeterminable_never_true` |
| NFR-003 | integration | `tests/integration/permissions/test_persistence.py` | `test_in_memory_repos_and_singleton` |
| NFR-004 | integration | `tests/integration/permissions/test_thread_safety.py` | `test_concurrent_checks_and_changes` |
| NFR-005 | acceptance | `tests/acceptance/permissions/test_check_api.py` | `test_denial_log_and_no_token_leak` |

## 11. Traceability Matrix

Maintain this matrix as tests are written and pass. Every normative requirement MUST have at least one executable test.

| Requirement | Acceptance Criterion | Test | Status |
|-------------|---------------------|------|--------|
| REQ-001 | AC-001 | `test_granted_permission_allowed` | PENDING |
| REQ-001 | AC-002 | `test_denied_permission_raises_with_context` | PENDING |
| REQ-002 | AC-003 | `test_malformed_permission_denied` | PENDING |
| REQ-003 | AC-004 | `test_feature_wildcard_grant` | PENDING |
| REQ-004 | AC-005 | `test_unknown_permission_denied_and_grant_rejected` | PENDING |
| REQ-005 | AC-006 | `test_initial_catalog_exactly_60_keys` | PENDING |
| REQ-006 | AC-007 | `test_create_role_and_list` | PENDING |
| REQ-007 | AC-008 | `test_delete_role_guards` | PENDING |
| REQ-008 | AC-009 | `test_grant_and_revoke_role_permission` | PENDING |
| REQ-008 | AC-010 | `test_wildcard_grant_stored_and_matches` | PENDING |
| REQ-009 | AC-011 | `test_multi_role_union_of_permissions` | PENDING |
| REQ-010 | AC-012 | `test_admin_wildcard_allows_all` | PENDING |
| REQ-011 | AC-013 | `test_user_role_starts_with_zero_permissions` | PENDING |
| REQ-012 | AC-014 | `test_assignment_delegates_to_user_manager` | PENDING |
| REQ-013 | AC-015 | `test_last_admin_guard_preserved_via_service` | PENDING |
| REQ-014 | AC-016 | `test_grant_change_takes_effect_immediately` | PENDING |
| REQ-015 | AC-017 | `test_unknown_user_denied` | PENDING |
| REQ-015 | AC-018 | `test_storage_error_denied_fail_closed` | PENDING |
| REQ-016 | AC-019 | `test_inactive_user_denied_even_admin` | PENDING |
| REQ-017 | AC-020 | `test_session_validation_in_check` | PENDING |
| REQ-017 | AC-021 | `test_session_validation_skipped_when_token_none` | PENDING |
| REQ-018 | AC-022 | `test_system_principal_check_and_set` | PENDING |
| REQ-019 | AC-023 | `test_system_set_settings_alias_sync` | PENDING |
| REQ-020 | AC-024 | `test_events_published_on_operations` | PENDING |
| REQ-020 | AC-025 | `test_no_publisher_still_works` | PENDING |
| REQ-021 | AC-026 | `test_error_context_attributes` | PENDING |
| REQ-022 | AC-027 | `test_migration_seeds_roles_and_system_set` | PENDING |
| REQ-023 | AC-028 | `test_in_memory_repos_and_singleton` | PENDING |
| REQ-024 | AC-029 | `test_enforced_method_denies_without_permission` | PENDING |
| REQ-024 | AC-030 | `test_exempt_login_no_check` | PENDING |
| REQ-024 | AC-031 | `test_standalone_mode_no_check` | PENDING |
| REQ-025 | AC-032 | `test_principal_defaults_and_fields` | PENDING |
| REQ-026 | AC-033 | `test_create_user_with_roles_list` | PENDING |
| REQ-026 | AC-034 | `test_add_remove_set_roles` | PENDING |
| REQ-026 | AC-035 | `test_migration_member_to_user_and_role_list` | PENDING |
| REQ-026 | AC-036 | `test_last_admin_guard_all_paths` | PENDING |
| REQ-026 | AC-037 | `test_role_events_carry_lists` | PENDING |
| REQ-027 | AC-038 | `test_concurrent_checks_and_changes` | PENDING |
| REQ-028 | AC-039 | `test_denial_log_and_no_token_leak` | PENDING |
| REQ-029 | AC-040 | `test_check_latency_under_5ms_median` | PENDING |
| INV-001 | — | `test_check_true_iff_granted_and_active` | PENDING |
| INV-002 | — | `test_undeterminable_never_true` | PENDING |
| INV-003 | — | `test_last_admin_invariant` | PENDING |
| INV-004 | — | `test_effective_set_monotone` | PENDING |
| INV-005 | — | `test_admin_passes_any_catalog_permission` | PENDING |
| INV-006 | — | `test_valid_grant_keys_exactly_catalog_plus_wildcards` | PENDING |

## 12. Impact Analysis (per-feature)

This is a CROSS-CUTTING change: a new shared RBAC capability plus enforcement wiring across six existing features. Every affected feature, what changes in each, and which of their REQ/AC IDs are touched:

| Feature | What Changes | REQ/AC IDs Touched |
|---------|--------------|--------------------|
| **permissions** (new, `src/backend/permissions/`) | New shared RBAC feature: `PermissionService` (check API, role CRUD, dynamic role→permission grants, system principal), `PermissionCatalog` (static, startup-declared), repository ABCs + SQLModel/SQLite repositories + in-memory repositories, feature-owned `register_actions` / `register_settings` startup declarations, events (`PermissionDenied`, `RoleCreated`, `RoleDeleted`, `RolePermissionsChanged`), errors (`AuthorizationError` hierarchy), singleton `get_permission_service()` / `reset_permission_service()`. | REQ-001..REQ-023, REQ-025, REQ-027..REQ-029; AC-001..AC-028, AC-032, AC-038..AC-040; INV-001..INV-006; EDGE-001..EDGE-026 |
| **shared** (new, `src/backend/shared/`) | New package: `Principal` model, `PermissionChecker` protocol, `@requires_permission` decorator — the enforcement plumbing shared by all six features (avoids circular imports between usermanagement and permissions). | REQ-024, REQ-025; AC-029..AC-032; EDGE-022 |
| **usermanagement** | Multi-role amendment (breaking): `User.role: str` → `User.roles: list[str]`; `UserCreate.roles` / `UserRead.roles` (non-empty lists); role existence validated against an injected `RoleStore` (default `StaticRoleStore(("admin", "user"))`); new `UserManager` methods `set_roles` / `add_role` / `remove_role` (`set_role` preserved as `set_roles([role])`); the last-admin guard extended to every assignment path; `UserRoleChanged.old_roles` / `new_roles` and `UserCreated.roles` as lists; role value `member` → `user`; alembic data migration. | REQ-012, REQ-013, REQ-026; AC-014, AC-015, AC-033..AC-037 |
| **authentication** | Enforcement wiring: all 11 public `AuthService` methods take a trailing `principal: Principal = Principal()` parameter; the 7 exempt session-establishment/teardown/introspection operations (`login`, `logout`, `session_info`, `request_password_reset`, `complete_password_reset`, `begin_passkey_login`, `complete_passkey_login`) are declared but not enforced; `AuthService` constructor takes an optional `permission_checker`. `LoginResult.user` now carries `UserRead.roles` (multi-role). | REQ-024; AC-029..AC-031 |
| **settings** | Enforcement wiring: all 19 public `SettingsRegistry` methods take a trailing `principal` parameter; the registry constructor takes an optional `permission_checker`. The `permissions.system_principal` settings alias (REQ-019) is owned by the permissions feature and subscribes to `SettingChanged`. | REQ-024; AC-029..AC-031 |
| **filemanagement** | Enforcement wiring: all 10 public `FileService` methods take a trailing `principal` parameter; `FileService` constructor takes an optional `permission_checker`. | REQ-024; AC-029..AC-031 |
| **mail** | Enforcement wiring: all 3 public `MailService` methods take a trailing `principal` parameter; `MailService` constructor takes an optional `permission_checker`. | REQ-024; AC-029..AC-031 |
| **sessionmanagement** | Enforcement wiring: all 6 public `SessionService` methods take a trailing `principal` parameter; the service constructor takes an optional `permission_checker`. The session repository (`get_by_token_hash`) is used by the check for session validation (REQ-017). | REQ-017, REQ-024; AC-020, AC-021, AC-029..AC-031 |

## 13. Breaking Changes and In-Scope Fixes

Per Q-97, breaking changes are permitted for this change because every break is fixed within this change's scope. The complete list:

| # | Breaking Change | In-Scope Fix |
|---|-----------------|--------------|
| 1 | `User.role: str` → `User.roles: list[str]` (usermanagement model, repository, events) | Alembic data migration (single role → one-element list); all consumers and tests updated within this change. |
| 2 | Role value `member` → `user` | Alembic data migration rewrites role values; the static role store is `("admin", "user")`. |
| 3 | `UserCreate.role` / `UserRead.role` → `roles` (non-empty list) | Same migration; the read/create models are updated within this change. |
| 4 | `UserManager.set_role` semantics → `set_roles([role])` (replace, not add) | Documented in this spec; the new `set_roles` / `add_role` / `remove_role` methods are added within this change. |
| 5 | `UserRoleChanged` fields `role` → `old_roles` / `new_roles` (lists); `UserCreated.role` → `roles` (list) | All event consumers updated within this change; events carry non-sensitive data only. |
| 6 | Trailing `principal: Principal = Principal()` parameter on the 53 enforced public methods of the six features | The parameter is trailing with a default (the system principal), so existing positional call sites are unaffected; enforcement is active only when a permission checker is injected (standalone mode = today's behavior). |
| 7 | New optional `permission_checker` constructor parameter on the six services/registries | Additive (default `None` → standalone mode); no existing construction breaks. |
| 8 | New `src/backend/shared/` package | Additive; no existing imports change. |
| 9 | New tables + alembic migrations (permissions: `roles`, `role_permissions`, `system_principal_permissions`; usermanagement: role column → role list, `member` → `user`) | Migrations are part of this change; seeding (built-in roles, bootstrap system set) happens in the same migration. |

Every break above is fixed within this change's scope: migrations, consumer updates, and test updates are all part of this change.
