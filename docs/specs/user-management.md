# Spec: User Management (Backend)

## 1. Overview & Objectives
- **Feature Name:** User Management (Backend)
- **Target Component:** `src/backend/usermanagement/`
- **Goal:** Provide a backend service for managing user account records — creation, reading, updating, deletion, password management, role management, and activation — with the essential account fields (username, email, role, password, profile picture, display name, active state, and created/updated timestamps). Users are persisted in SQLite via SQLModel behind a repository interface, so the database can be changed later.
- **Scope:** In-process Python service (no HTTP layer); SQLite/SQLModel persistence behind a `UserRepository` ABC; Argon2id password hashing; configurable role set (preconfigured `admin` + `member`); last-admin protection; activation; typed lifecycle events published to an injected event publisher; structured domain errors; observability via the shared logging feature.
- **Out of Scope:** Frontend (implemented in a separate workflow), HTTP/REST/GraphQL API layer, authentication (login/logout, sessions, tokens, MFA), email verification/sending, profile picture upload/storage (URL reference only), user groups/teams/permissions beyond roles, persistent audit log, password recovery/reset flows, database migration/upgrade framework (bootstrap via `create_all` only), and multi-tenancy.

## 2. Architecture & Design Decisions
- **Design Pattern:** Service + repository. `UserManager` (use cases, validation, domain rules) depends only on the `UserRepository` ABC; `SqliteUserRepository` implements the ABC with SQLModel/SQLite. The service publishes typed lifecycle events to an injected `EventPublisher` (structural protocol; the real event bus is injected at wiring time).
- **Dependencies:** `sqlmodel>=0.0.42` (pulls in `sqlalchemy`), `argon2-cffi>=25.1.0`, `email-validator>=2.3.0`; uses the shared logging feature `backend.logging` (`@logged_class`). No web framework. No import of `backend.eventbus` (the event integration is a structural protocol, so this feature does not hard-depend on the event-bus feature's source).
- **Constraints:** The service API MUST NOT expose `password_hash` or the raw `User` table object. The service code MUST reference only `UserRepository` (the database must be swappable later). The SQLite store is the default concrete repository. Passwords MUST NOT appear in log records.
- **Design Decisions (WHAT; WHY goes to ADRs in Phase 2):**
  - D1: Repository pattern — `UserRepository` ABC + `SqliteUserRepository` (SQLModel/SQLite); constructor injection into `UserManager`.
  - D2: Argon2id password hashing via argon2-cffi (library defaults); only the hash is stored.
  - D3: Configurable role set — roles are lowercase strings; `UserManager(roles=...)`, default `{"admin", "member"}`; membership is validated on create and set_role.
  - D4: Last-admin protection — while `admin` is in the configured role set, operations that would leave zero active admins are rejected with `LastAdminError`.
  - D5: `username` is immutable and case-sensitive; `email` is mutable, case-insensitive (stored lowercased).
  - D6: Hard delete; activation is a flag (`is_active`), not a deletion.
  - D7: Field-format validation is schema-level (Pydantic models → `pydantic.ValidationError`); domain rules are service-level (exception hierarchy rooted at `UserManagerError`).
  - D8: Table bootstrap via `SQLModel.metadata.create_all` at repository init (no migration framework).
  - D9: `UserRead` is the only user representation returned by the service (no hash, no raw table object).
  - D10: Typed lifecycle events are published to the injected `EventPublisher` after each successful mutation; a `None` publisher means no events; no event is published on failure or on a no-op.
  - D11: Events carry non-sensitive data only (no password, no hash).

## 3. Data Structures & API Schemas

```python
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Protocol, Sequence
from uuid import UUID, uuid4

from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import UniqueConstraint
from sqlmodel import SQLModel, Field as SField

# --- Table model (persistence) ---

class User(SQLModel, table=True):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("username", name="uq_users_username"),
        UniqueConstraint("email", name="uq_users_email"),
    )
    id: UUID = SField(default_factory=uuid4, primary_key=True)
    username: str = SField(index=True)
    email: str = SField(index=True)          # stored lowercased (D5)
    display_name: str | None = None
    role: str
    password_hash: str                        # Argon2id hash only (D2)
    profile_picture_url: str | None = None
    is_active: bool = True
    created_at: datetime                      # UTC
    updated_at: datetime                      # UTC

# --- Request / response schemas ---

class UserCreate(BaseModel):
    username: str                             # ^[a-zA-Z0-9][a-zA-Z0-9._-]{1,30}[a-zA-Z0-9]$
    email: EmailStr                           # valid email (email-validator)
    password: str                             # 8..128 chars, >= 1 letter, >= 1 digit
    display_name: str | None = None           # 1..64 chars after strip (whitespace-only rejected)
    role: str                                 # ^[a-z0-9_-]{1,32}$; membership checked by the service
    profile_picture_url: str | None = None    # must start with "http://" or "https://"

class UserUpdate(BaseModel):
    email: EmailStr | None = None             # None means "no change" (not "clear")
    display_name: str | None = None           # 1..64 chars after strip
    profile_picture_url: str | None = None    # must start with "http://" or "https://"
    # No username field: username is immutable (D5)

class UserRead(BaseModel):
    id: UUID
    username: str
    email: str
    display_name: str | None
    role: str
    profile_picture_url: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    # No password_hash field (D9)
```

```python
# --- Lifecycle events (typed; D10/D11) ---

class UserEvent(BaseModel):
    occurred_at: datetime                     # UTC

class UserCreated(UserEvent):
    user_id: UUID
    username: str
    email: str
    role: str

class UserUpdated(UserEvent):
    user_id: UUID
    changed_fields: list[str]                # subset of {"email", "display_name", "profile_picture_url"}

class UserDeleted(UserEvent):
    user_id: UUID
    username: str                            # carried because the record is gone

class UserPasswordChanged(UserEvent):
    user_id: UUID

class UserRoleChanged(UserEvent):
    user_id: UUID
    old_role: str
    new_role: str

class UserActivated(UserEvent):
    user_id: UUID

class UserDeactivated(UserEvent):
    user_id: UUID

# --- Publisher protocol (structural; the real EventBus satisfies it) ---

class EventPublisher(Protocol):
    def publish(self, event: object) -> None: ...
```

```python
# --- Repository ---

class UserRepository(ABC):
    @abstractmethod
    def add(self, user: User) -> User: ...
        # Raises UserAlreadyExistsError when a uniqueness constraint is violated (race guard)
    @abstractmethod
    def get_by_id(self, user_id: UUID) -> User | None: ...
    @abstractmethod
    def get_by_username(self, username: str) -> User | None: ...
    @abstractmethod
    def get_by_email(self, email: str) -> User | None: ...
    @abstractmethod
    def update(self, user: User) -> User: ...
    @abstractmethod
    def delete(self, user_id: UUID) -> None: ...
    @abstractmethod
    def list_all(self, include_inactive: bool = False) -> Sequence[User]: ...
    @abstractmethod
    def count_active_by_role(self, role: str) -> int: ...

class SqliteUserRepository(UserRepository):
    def __init__(self, database_url: str) -> None: ...
    # Creates the DB file's parent directory and all tables (D8);
    # maps violated uq_users_username / uq_users_email to UserAlreadyExistsError.field
```

```python
# --- Service ---

class UserManager:
    def __init__(
        self,
        repository: UserRepository,
        roles: Iterable[str] = ("admin", "member"),
        event_bus: EventPublisher | None = None,
    ) -> None: ...
    # roles: non-empty iterable; each entry matches ^[a-z0-9_-]{1,32}$; otherwise ValueError
    def create_user(self, data: UserCreate) -> UserRead: ...
    def get_user(self, user_id: UUID) -> UserRead: ...
    def get_user_by_username(self, username: str) -> UserRead: ...
    def list_users(self, include_inactive: bool = False) -> list[UserRead]: ...
    def update_user(self, user_id: UUID, data: UserUpdate) -> UserRead: ...
    def delete_user(self, user_id: UUID) -> None: ...
    def change_password(self, user_id: UUID, new_password: str) -> None: ...
    def verify_password(self, user_id: UUID, password: str) -> bool: ...
    def set_role(self, user_id: UUID, role: str) -> UserRead: ...
    def activate_user(self, user_id: UUID) -> UserRead: ...
    def deactivate_user(self, user_id: UUID) -> UserRead: ...
```

```python
# --- Errors ---

class UserManagerError(Exception): ...

class UserAlreadyExistsError(UserManagerError):
    field: str                               # "username" | "email"

class UserNotFoundError(UserManagerError): ...

class InvalidRoleError(UserManagerError):
    role: str
    allowed: frozenset[str]

class LastAdminError(UserManagerError): ...
```

**Package layout:**

```text
src/backend/usermanagement/
├── __init__.py    # re-exports the public API
├── models.py      # User, UserCreate, UserUpdate, UserRead
├── events.py      # UserEvent + lifecycle events, EventPublisher
├── errors.py      # exception hierarchy
├── repository.py  # UserRepository, SqliteUserRepository
└── service.py     # UserManager
```

**Public API** (the NFR-003 backward-compatibility contract): `User`, `UserCreate`, `UserUpdate`, `UserRead`, `UserEvent`, `UserCreated`, `UserUpdated`, `UserDeleted`, `UserPasswordChanged`, `UserRoleChanged`, `UserActivated`, `UserDeactivated`, `EventPublisher`, `UserRepository`, `SqliteUserRepository`, `UserManager`, `UserManagerError`, `UserAlreadyExistsError`, `UserNotFoundError`, `InvalidRoleError`, `LastAdminError`.

## 4. Requirements

Each normative requirement MUST have a stable ID. These IDs propagate through the lifecycle:
`REQ-001 → AC-001 → test → task → implementation`.

| ID | Requirement |
|----|-------------|
| REQ-001 | The service manages user records with the essential account fields: username, email, display name, role, password, profile picture URL, active state, and created/updated timestamps. |
| REQ-002 | `create_user` validates input (schema-level field format; service-level domain rules) and stores the user with a hashed password, a generated id, and UTC created/updated timestamps. |
| REQ-003 | Uniqueness: usernames are unique case-sensitively; emails are unique case-insensitively (stored lowercased). |
| REQ-004 | Passwords are hashed with Argon2id; plaintext is never stored; the hash is never exposed through the service API. |
| REQ-005 | Password operations: `change_password` validates the new password against the password rules, re-hashes it, and stores it; `verify_password` checks a password against the stored hash and returns True/False. |
| REQ-006 | Roles are configurable: the service is constructed with a role set (default `{"admin", "member"}`); user roles are validated against the set on create and set_role. |
| REQ-007 | Role changes are supported via `set_role`. |
| REQ-008 | Last-admin protection: while `admin` is in the configured role set, operations that would leave zero active admins (delete, deactivate, demote) are rejected with `LastAdminError`. |
| REQ-009 | Activation: users have an `is_active` flag; `activate_user`/`deactivate_user` set it (idempotent no-ops publish no event). |
| REQ-010 | Read operations: `get_user` (by id), `get_user_by_username`, `list_users` (default excludes inactive users). |
| REQ-011 | `update_user` mutates email, display name, and profile picture URL; usernames are immutable. |
| REQ-012 | `delete_user` removes the user record (hard delete). |
| REQ-013 | Persistence via the repository pattern: `UserRepository` ABC + `SqliteUserRepository` (SQLModel/SQLite); the service depends only on the ABC, so the database can be changed later. |
| REQ-014 | Structured domain errors: an exception hierarchy rooted at `UserManagerError` with documented context attributes. |
| REQ-015 | Observability: the service is traced via the shared logging feature (`@logged_class`); domain errors are logged with context; passwords never appear in log records. |
| REQ-016 | The service publishes typed lifecycle events to the injected event publisher after each successful mutation: create, update, delete, password change, role change, activate, deactivate. |
| REQ-017 | Events carry non-sensitive data only; the publisher is optional (None → no events, no errors); no event is published on failure or on a no-op. |

## 5. Acceptance Criteria

Each acceptance criterion MUST have a stable ID and MUST reference at least one requirement. Use Given/When/Then format.

| ID | References | Criterion |
|----|------------|-----------|
| AC-001 | REQ-001, REQ-002 | **Given** a valid `UserCreate`, **When** `create_user` is called, **Then** a `UserRead` is returned with the same username, email, display name, role, and profile picture URL, `is_active=True`, a fresh `id`, and UTC `created_at`/`updated_at`, **And** the user is retrievable via `get_user`. |
| AC-002 | REQ-003 | **Given** a user with username `alice`, **When** `create_user` is called with username `alice`, **Then** a `UserAlreadyExistsError` is raised with `field == "username"`, **And** no second user is created. |
| AC-003 | REQ-003 | **Given** a user with email `Alice@Example.com`, **When** `create_user` is called with email `alice@example.com`, **Then** a `UserAlreadyExistsError` is raised with `field == "email"`. |
| AC-004 | REQ-002 | **Given** a `UserCreate` with username `ab`, **When** the model is constructed, **Then** a `pydantic.ValidationError` is raised identifying `username`. |
| AC-005 | REQ-002 | **Given** a `UserCreate` with password `short1`, **When** the model is constructed, **Then** a `pydantic.ValidationError` is raised identifying `password`. |
| AC-006 | REQ-002 | **Given** a `UserCreate` with email `not-an-email`, **When** the model is constructed, **Then** a `pydantic.ValidationError` is raised identifying `email`. |
| AC-007 | REQ-002 | **Given** a `UserCreate` with profile picture URL `ftp://example.com/p.png`, **When** the model is constructed, **Then** a `pydantic.ValidationError` is raised identifying `profile_picture_url`. |
| AC-008 | REQ-006 | **Given** `UserManager(repo, roles={"admin", "member"})`, **When** `create_user` is called with `role="superuser"`, **Then** an `InvalidRoleError` is raised. |
| AC-009 | REQ-006 | **Given** `UserManager(repo, roles={"owner", "worker"})`, **When** `create_user` is called with `role="worker"`, **Then** it succeeds, **And** `create_user` with `role="member"` raises `InvalidRoleError`. |
| AC-010 | REQ-004 | **Given** a created user, **When** the stored record is read via the repository, **Then** `password_hash` starts with `$argon2id$` and is not the plaintext, **And** `UserRead` has no `password_hash` field. |
| AC-011 | REQ-005 | **Given** a user with password `correct-horse-battery`, **When** `change_password(user_id, "new-password-1")` is called, **Then** `verify_password(user_id, "new-password-1")` is True, **And** `verify_password(user_id, "correct-horse-battery")` is False. |
| AC-012 | REQ-005 | **Given** a user, **When** `verify_password(user_id, <the correct password>)` is called, **Then** it returns True, **And** for a wrong password it returns False. |
| AC-013 | REQ-005 | **Given** a user, **When** `change_password` is called with password `abcdef1` (7 chars), **Then** a `pydantic.ValidationError` is raised. |
| AC-014 | REQ-005 | **Given** an unknown user id, **When** `change_password` or `verify_password` is called, **Then** a `UserNotFoundError` is raised. |

| AC-015 | REQ-007 | **Given** a user with role `member`, **When** `set_role(user_id, "admin")` is called, **Then** a `UserRead` with role `admin` is returned, **And** `get_user` reflects it. |
| AC-016 | REQ-006 | **Given** a user, **When** `set_role(user_id, "superuser")` is called (not in the set), **Then** an `InvalidRoleError` is raised. |
| AC-017 | REQ-008 | **Given** exactly one active admin and `admin` in the role set, **When** `delete_user(last_admin_id)` is called, **Then** a `LastAdminError` is raised, **And** the user is not deleted. |
| AC-018 | REQ-008 | **Given** exactly one active admin, **When** `deactivate_user(last_admin_id)` is called, **Then** a `LastAdminError` is raised. |
| AC-019 | REQ-008 | **Given** exactly one active admin, **When** `set_role(last_admin_id, "member")` is called, **Then** a `LastAdminError` is raised. |
| AC-020 | REQ-009 | **Given** an active user, **When** `deactivate_user` is called, **Then** a `UserRead` with `is_active=False` is returned, **And** the user is excluded from the default `list_users()`, **And** `activate_user` restores `is_active=True`. |
| AC-021 | REQ-009 | **Given** an active user, **When** `activate_user` is called, **Then** a `UserRead` with `is_active=True` is returned (idempotent no-op, no event). |
| AC-022 | REQ-010 | **Given** a user, **When** `get_user(user_id)` is called, **Then** a `UserRead` is returned, **And** for an unknown id a `UserNotFoundError` is raised. |
| AC-023 | REQ-010 | **Given** a user with username `bob`, **When** `get_user_by_username("bob")` is called, **Then** a `UserRead` is returned, **And** for an unknown username a `UserNotFoundError` is raised. |
| AC-024 | REQ-010 | **Given** active users A, B and inactive user C, **When** `list_users()` is called, **Then** it returns A and B, **And** `list_users(include_inactive=True)` returns all three. |
| AC-025 | REQ-011 | **Given** a user, **When** `update_user(user_id, UserUpdate(email=..., display_name=...))` is called, **Then** a `UserRead` reflecting both changes is returned, **And** `username`, `id`, and `created_at` are unchanged, **And** `updated_at` is set to a fresh UTC timestamp. |
| AC-026 | REQ-012 | **Given** a user, **When** `delete_user(user_id)` is called, **Then** `get_user(user_id)` raises `UserNotFoundError`, **And** the user is absent from `list_users(include_inactive=True)`. |
| AC-027 | REQ-013 | **Given** a user created via `SqliteUserRepository("sqlite:///<tmp>/users.db")`, **When** a new repository + service instance is constructed on the same file, **Then** the user is visible. |
| AC-028 | REQ-013 | **Given** a service constructed with a non-SQLite `UserRepository` implementation (a test fake), **When** all operations are invoked, **Then** they work (the service depends only on the ABC). |
| AC-029 | REQ-014 | **Given** a domain error, **When** it is caught, **Then** it is a `UserManagerError` subclass carrying the documented context (`UserAlreadyExistsError.field`, `InvalidRoleError.role`/`.allowed`). |
| AC-030 | REQ-016 | **Given** a publisher that collects events, **When** `create_user` succeeds, **Then** a `UserCreated` event with `user_id`, `username`, `email`, `role` is published. |
| AC-031 | REQ-016 | **Given** a collector, **When** a non-empty `update_user` succeeds, **Then** a `UserUpdated` event with `user_id` and `changed_fields` is published. |
| AC-032 | REQ-016 | **Given** a collector, **When** `delete_user` succeeds, **Then** a `UserDeleted` event with `user_id` and `username` is published. |
| AC-033 | REQ-016 | **Given** a collector, **When** `change_password` succeeds, **Then** a `UserPasswordChanged` event with `user_id` is published. |
| AC-034 | REQ-016 | **Given** a collector, **When** `set_role` succeeds, **Then** a `UserRoleChanged` event with `user_id`, `old_role`, `new_role` is published. |
| AC-035 | REQ-016 | **Given** a collector, **When** `activate_user` succeeds as an actual transition, **Then** a `UserActivated` event with `user_id` is published. |
| AC-036 | REQ-016 | **Given** a collector, **When** `deactivate_user` succeeds as an actual transition, **Then** a `UserDeactivated` event with `user_id` is published. |
| AC-037 | REQ-017 | **Given** a collector, **When** an operation fails with a domain error, **Then** no event is published. |
| AC-038 | REQ-017 | **Given** `UserManager(repo)` without a publisher, **When** operations succeed, **Then** they work normally (no events, no errors). |

## 6. Invariants

State invariants that hold over a large input space. These become Hypothesis property-based tests.

| ID | Invariant |
|----|-----------|
| INV-001 | For any valid `UserCreate`, `create_user` returns a `UserRead` whose username, email, display name, role, and profile picture URL equal the input, `is_active` is True, and `created_at`/`updated_at` are set. |
| INV-002 | For any user and any password `p` satisfying the password rules: after creation with `p` (or `change_password(p)`), `verify_password(user_id, p)` is True, and for any `p' != p`, `verify_password(user_id, p')` is False. |
| INV-003 | For any sequence of operations, while `admin` is in the configured role set: if the store contains one or more users with role `admin`, at least one of them is active. |
| INV-004 | For any user and any valid `UserUpdate`: after `update_user`, `id`, `username`, and `created_at` are unchanged; fields named in the update equal the update's values; other mutable fields retain their previous values. |
| INV-005 | For any two distinct users in the store: their usernames differ (case-sensitive) and their stored emails differ. |
| INV-006 | For any successful mutation operation, exactly one corresponding event is published with the correct `user_id`; no event is published on failure or on a no-op. |

## 7. Edge Cases & Error Conditions

| ID | Condition | Expected Behavior |
|----|-----------|-------------------|
| EDGE-001 | `update_user` with an email that collides with another user's email | A `UserAlreadyExistsError` is raised with `field == "email"` |
| EDGE-002 | `update_user` with an empty `UserUpdate()` | No-op: the same `UserRead` is returned, no event, `updated_at` unchanged |
| EDGE-003 | `delete_user` called twice | The second call raises `UserNotFoundError` |
| EDGE-004 | `deactivate_user` on an already-inactive user | No-op (idempotent): a `UserRead` with `is_active=False` is returned, no event |
| EDGE-005 | `set_role` to the same role | No-op (idempotent): a `UserRead` is returned, no event |
| EDGE-006 | `verify_password` with an unknown id | A `UserNotFoundError` is raised |
| EDGE-007 | `SqliteUserRepository` with a `database_url` whose parent directory does not exist | The parent directory is auto-created; the repository works |
| EDGE-008 | `SqliteUserRepository` with `sqlite:///:memory:` | Works; each instance is isolated |
| EDGE-009 | `UserManager(roles=())` | A `ValueError` is raised |
| EDGE-010 | `UserManager(roles={"Admin"})` (uppercase) | A `ValueError` is raised (role names must be lowercase) |
| EDGE-011 | `create_user` with username `al ice` (whitespace) | A `pydantic.ValidationError` is raised |
| EDGE-012 | `create_user` with password `abcdefgh` (no digit) | A `pydantic.ValidationError` is raised |
| EDGE-013 | `create_user` with password `12345678` (no letter) | A `pydantic.ValidationError` is raised |
| EDGE-014 | `list_users` on an empty store | Returns `[]` |
| EDGE-015 | Concurrent `create_user` with the same username (two threads) | Exactly one succeeds; the other raises `UserAlreadyExistsError` |
| EDGE-016 | `delete_user` on an admin while two active admins exist | Allowed (only the last admin is protected) |
| EDGE-017 | `update_user` with an unknown id | A `UserNotFoundError` is raised |
| EDGE-018 | `create_user` with display name `   ` (whitespace only) | A `pydantic.ValidationError` is raised |
| EDGE-019 | A user created without display name or profile picture | `UserRead` has `display_name=None`, `profile_picture_url=None` |
| EDGE-020 | The publisher raises on `publish` | The exception propagates to the caller; the mutation is already committed |
| EDGE-021 | `create_user` with usernames differing only in case (`Alice` vs `alice`) | Both are allowed (case-sensitive uniqueness) |

## 8. Non-Functional Requirements

| ID | Category | Requirement |
|----|----------|-------------|
| NFR-001 | Performance | Read operations (`get_user`, `get_user_by_username`, `list_users`) complete in < 5 ms (median) in-process on SQLite; `create_user` and `verify_password` complete in < 1 s (median) (Argon2id hashing dominates). |
| NFR-002 | Security | Passwords are never stored or logged in plaintext; only the Argon2id hash is stored; the service API never exposes `password_hash` or the raw `User` table object; verification uses argon2's constant-time verify. |
| NFR-003 | Contract | The public API (`UserManager`, `UserRepository`, `SqliteUserRepository`, schemas, events, errors) is backward-compatible; adding optional parameters must not break existing callers. |
| NFR-004 | Reliability | The SQLite repository is safe for concurrent use from multiple threads; the DB file's parent directory is auto-created; a failed operation leaves no partial state. |
| NFR-005 | Observability | Service operations are traced via the shared logging feature; domain errors are logged with context; passwords never appear in log records. |

## 9. Observability & Logging

Every feature MUST be observable. Specify the logging behavior: which operations are logged, at what level, and with what context.

- `UserManager` is decorated with `@logged_class` from the shared logging feature: every public method is traced with an entry line, an exit line (elapsed ms), and an exception line on error.
- `include_args` stays at the default `False`: method arguments (including `UserCreate` with the password) are never logged.
- Domain error messages carry no secrets (only error kind, field names, and role names), so exception lines are safe.

| Operation / Event | Level | Context |
|-------------------|-------|---------|
| Any service method call (entry/exit) | DEBUG | method qualname, elapsed ms |
| `create_user` success | DEBUG | method qualname, elapsed ms (username via return value, not args) |
| `change_password` success | DEBUG | method qualname, elapsed ms (never the password) |
| Domain error (`UserAlreadyExistsError`, `UserNotFoundError`, `InvalidRoleError`, `LastAdminError`) | DEBUG (exception line) | error type + message (no secrets) |

- **Default level:** DEBUG tracing (off at INFO); domain errors are logged with type + message.
- **Error conditions:** domain errors are logged via `@logged` exception tracing; passwords never appear in any log record (NFR-002).

## 10. Test Strategy

Map each requirement/AC to a test category. This drives the test file layout.

| ID | Test Category | Test File | Test Function |
|----|---------------|-----------|---------------|
| AC-001 | acceptance | `tests/acceptance/usermanagement/test_usermanagement.py` | `test_ac_001_create_valid_user` |
| AC-002 | acceptance | `tests/acceptance/usermanagement/test_usermanagement.py` | `test_ac_002_duplicate_username` |
| AC-003 | acceptance | `tests/acceptance/usermanagement/test_usermanagement.py` | `test_ac_003_duplicate_email_case_insensitive` |
| AC-004 | acceptance | `tests/acceptance/usermanagement/test_usermanagement.py` | `test_ac_004_username_too_short` |
| AC-005 | acceptance | `tests/acceptance/usermanagement/test_usermanagement.py` | `test_ac_005_password_too_short` |
| AC-006 | acceptance | `tests/acceptance/usermanagement/test_usermanagement.py` | `test_ac_006_invalid_email` |
| AC-007 | acceptance | `tests/acceptance/usermanagement/test_usermanagement.py` | `test_ac_007_non_http_profile_picture_url` |
| AC-008 | acceptance | `tests/acceptance/usermanagement/test_usermanagement.py` | `test_ac_008_role_not_in_set_create` |
| AC-009 | acceptance | `tests/acceptance/usermanagement/test_usermanagement.py` | `test_ac_009_custom_role_set` |
| AC-010 | acceptance | `tests/acceptance/usermanagement/test_usermanagement.py` | `test_ac_010_argon2_hash_stored_not_exposed` |
| AC-011 | acceptance | `tests/acceptance/usermanagement/test_usermanagement.py` | `test_ac_011_change_password` |
| AC-012 | acceptance | `tests/acceptance/usermanagement/test_usermanagement.py` | `test_ac_012_verify_password` |
| AC-013 | acceptance | `tests/acceptance/usermanagement/test_usermanagement.py` | `test_ac_013_change_password_weak` |
| AC-014 | acceptance | `tests/acceptance/usermanagement/test_usermanagement.py` | `test_ac_014_password_ops_unknown_user` |
| AC-015 | acceptance | `tests/acceptance/usermanagement/test_usermanagement.py` | `test_ac_015_set_role` |
| AC-016 | acceptance | `tests/acceptance/usermanagement/test_usermanagement.py` | `test_ac_016_set_role_not_in_set` |
| AC-017 | acceptance | `tests/acceptance/usermanagement/test_usermanagement.py` | `test_ac_017_delete_last_admin` |
| AC-018 | acceptance | `tests/acceptance/usermanagement/test_usermanagement.py` | `test_ac_018_deactivate_last_admin` |
| AC-019 | acceptance | `tests/acceptance/usermanagement/test_usermanagement.py` | `test_ac_019_demote_last_admin` |
| AC-020 | acceptance | `tests/acceptance/usermanagement/test_usermanagement.py` | `test_ac_020_deactivate_activate` |
| AC-021 | acceptance | `tests/acceptance/usermanagement/test_usermanagement.py` | `test_ac_021_activate_idempotent` |
| AC-022 | acceptance | `tests/acceptance/usermanagement/test_usermanagement.py` | `test_ac_022_get_user` |
| AC-023 | acceptance | `tests/acceptance/usermanagement/test_usermanagement.py` | `test_ac_023_get_user_by_username` |
| AC-024 | acceptance | `tests/acceptance/usermanagement/test_usermanagement.py` | `test_ac_024_list_users_excludes_inactive` |
| AC-025 | acceptance | `tests/acceptance/usermanagement/test_usermanagement.py` | `test_ac_025_update_user` |
| AC-026 | acceptance | `tests/acceptance/usermanagement/test_usermanagement.py` | `test_ac_026_delete_user` |
| AC-027 | acceptance | `tests/acceptance/usermanagement/test_usermanagement.py` | `test_ac_027_persistence_across_instances` |
| AC-028 | acceptance | `tests/acceptance/usermanagement/test_usermanagement.py` | `test_ac_028_service_with_fake_repository` |
| AC-029 | acceptance | `tests/acceptance/usermanagement/test_usermanagement.py` | `test_ac_029_error_hierarchy_context` |
| AC-030 | acceptance | `tests/acceptance/usermanagement/test_usermanagement.py` | `test_ac_030_event_user_created` |
| AC-031 | acceptance | `tests/acceptance/usermanagement/test_usermanagement.py` | `test_ac_031_event_user_updated` |
| AC-032 | acceptance | `tests/acceptance/usermanagement/test_usermanagement.py` | `test_ac_032_event_user_deleted` |
| AC-033 | acceptance | `tests/acceptance/usermanagement/test_usermanagement.py` | `test_ac_033_event_password_changed` |
| AC-034 | acceptance | `tests/acceptance/usermanagement/test_usermanagement.py` | `test_ac_034_event_role_changed` |
| AC-035 | acceptance | `tests/acceptance/usermanagement/test_usermanagement.py` | `test_ac_035_event_activated` |
| AC-036 | acceptance | `tests/acceptance/usermanagement/test_usermanagement.py` | `test_ac_036_event_deactivated` |
| AC-037 | acceptance | `tests/acceptance/usermanagement/test_usermanagement.py` | `test_ac_037_no_event_on_failure` |
| AC-038 | acceptance | `tests/acceptance/usermanagement/test_usermanagement.py` | `test_ac_038_no_publisher` |

| INV-001 | property | `tests/property/usermanagement/test_usermanagement_properties.py` | `test_inv_001_create_read_consistency` |
| INV-002 | property | `tests/property/usermanagement/test_usermanagement_properties.py` | `test_inv_002_password_round_trip` |
| INV-003 | property | `tests/property/usermanagement/test_usermanagement_properties.py` | `test_inv_003_last_admin_invariant` |
| INV-004 | property | `tests/property/usermanagement/test_usermanagement_properties.py` | `test_inv_004_update_semantics` |
| INV-005 | property | `tests/property/usermanagement/test_usermanagement_properties.py` | `test_inv_005_uniqueness` |
| INV-006 | property | `tests/property/usermanagement/test_usermanagement_properties.py` | `test_inv_006_event_correspondence` |
| EDGE-001 | unit | `tests/unit/usermanagement/test_usermanagement_edges.py` | `test_edge_001_update_email_collision` |
| EDGE-002 | unit | `tests/unit/usermanagement/test_usermanagement_edges.py` | `test_edge_002_empty_update_noop` |
| EDGE-003 | unit | `tests/unit/usermanagement/test_usermanagement_edges.py` | `test_edge_003_double_delete` |
| EDGE-004 | unit | `tests/unit/usermanagement/test_usermanagement_edges.py` | `test_edge_004_deactivate_already_inactive` |
| EDGE-005 | unit | `tests/unit/usermanagement/test_usermanagement_edges.py` | `test_edge_005_set_role_same` |
| EDGE-006 | unit | `tests/unit/usermanagement/test_usermanagement_edges.py` | `test_edge_006_verify_unknown` |
| EDGE-007 | unit | `tests/unit/usermanagement/test_usermanagement_edges.py` | `test_edge_007_repo_creates_parent_dir` |
| EDGE-008 | unit | `tests/unit/usermanagement/test_usermanagement_edges.py` | `test_edge_008_memory_repository` |
| EDGE-009 | unit | `tests/unit/usermanagement/test_usermanagement_edges.py` | `test_edge_009_empty_roles` |
| EDGE-010 | unit | `tests/unit/usermanagement/test_usermanagement_edges.py` | `test_edge_010_uppercase_role` |
| EDGE-011 | unit | `tests/unit/usermanagement/test_usermanagement_edges.py` | `test_edge_011_username_whitespace` |
| EDGE-012 | unit | `tests/unit/usermanagement/test_usermanagement_edges.py` | `test_edge_012_password_no_digit` |
| EDGE-013 | unit | `tests/unit/usermanagement/test_usermanagement_edges.py` | `test_edge_013_password_no_letter` |
| EDGE-014 | unit | `tests/unit/usermanagement/test_usermanagement_edges.py` | `test_edge_014_list_empty` |
| EDGE-015 | unit | `tests/unit/usermanagement/test_usermanagement_edges.py` | `test_edge_015_concurrent_duplicate_create` |
| EDGE-016 | unit | `tests/unit/usermanagement/test_usermanagement_edges.py` | `test_edge_016_delete_admin_with_two_admins` |
| EDGE-017 | unit | `tests/unit/usermanagement/test_usermanagement_edges.py` | `test_edge_017_update_unknown` |
| EDGE-018 | unit | `tests/unit/usermanagement/test_usermanagement_edges.py` | `test_edge_018_display_name_whitespace` |
| EDGE-019 | unit | `tests/unit/usermanagement/test_usermanagement_edges.py` | `test_edge_019_optional_fields_none` |
| EDGE-020 | unit | `tests/unit/usermanagement/test_usermanagement_edges.py` | `test_edge_020_publisher_raises` |
| EDGE-021 | unit | `tests/unit/usermanagement/test_usermanagement_edges.py` | `test_edge_021_case_sensitive_usernames` |
| NFR-001 | contract | `tests/contract/usermanagement/test_usermanagement_contracts.py` | `test_nfr_001_performance_budgets` |
| NFR-002 | contract | `tests/contract/usermanagement/test_usermanagement_contracts.py` | `test_nfr_002_no_plaintext_or_hash_exposed` |
| NFR-003 | contract | `tests/contract/usermanagement/test_usermanagement_contracts.py` | `test_nfr_003_api_backward_compatible` |
| NFR-004 | contract | `tests/contract/usermanagement/test_usermanagement_contracts.py` | `test_nfr_004_concurrent_repository_safety` |
| NFR-005 | contract | `tests/contract/usermanagement/test_usermanagement_contracts.py` | `test_nfr_005_operations_logged` |
| — | integration | `tests/integration/usermanagement/test_usermanagement_integration.py` | `test_full_user_lifecycle` |
| — | integration | `tests/integration/usermanagement/test_usermanagement_integration.py` | `test_events_and_persistence_across_instances` |

## 11. Traceability Matrix

Maintain this matrix as tests are written and pass. Every normative requirement MUST have at least one executable test.

| Requirement | Acceptance Criterion | Test | Status |
|-------------|---------------------|------|--------|
| REQ-001 | AC-001 | `test_ac_001_create_valid_user` | PENDING |
| REQ-002 | AC-001 | `test_ac_001_create_valid_user` | PENDING |
| REQ-002 | AC-004 | `test_ac_004_username_too_short` | PENDING |
| REQ-002 | AC-005 | `test_ac_005_password_too_short` | PENDING |
| REQ-002 | AC-006 | `test_ac_006_invalid_email` | PENDING |
| REQ-002 | AC-007 | `test_ac_007_non_http_profile_picture_url` | PENDING |
| REQ-003 | AC-002 | `test_ac_002_duplicate_username` | PENDING |
| REQ-003 | AC-003 | `test_ac_003_duplicate_email_case_insensitive` | PENDING |
| REQ-004 | AC-010 | `test_ac_010_argon2_hash_stored_not_exposed` | PENDING |
| REQ-005 | AC-011 | `test_ac_011_change_password` | PENDING |
| REQ-005 | AC-012 | `test_ac_012_verify_password` | PENDING |
| REQ-005 | AC-013 | `test_ac_013_change_password_weak` | PENDING |
| REQ-005 | AC-014 | `test_ac_014_password_ops_unknown_user` | PENDING |
| REQ-006 | AC-008 | `test_ac_008_role_not_in_set_create` | PENDING |
| REQ-006 | AC-009 | `test_ac_009_custom_role_set` | PENDING |
| REQ-006 | AC-016 | `test_ac_016_set_role_not_in_set` | PENDING |
| REQ-007 | AC-015 | `test_ac_015_set_role` | PENDING |
| REQ-008 | AC-017 | `test_ac_017_delete_last_admin` | PENDING |
| REQ-008 | AC-018 | `test_ac_018_deactivate_last_admin` | PENDING |
| REQ-008 | AC-019 | `test_ac_019_demote_last_admin` | PENDING |
| REQ-009 | AC-020 | `test_ac_020_deactivate_activate` | PENDING |
| REQ-009 | AC-021 | `test_ac_021_activate_idempotent` | PENDING |
| REQ-010 | AC-022 | `test_ac_022_get_user` | PENDING |
| REQ-010 | AC-023 | `test_ac_023_get_user_by_username` | PENDING |
| REQ-010 | AC-024 | `test_ac_024_list_users_excludes_inactive` | PENDING |
| REQ-011 | AC-025 | `test_ac_025_update_user` | PENDING |
| REQ-012 | AC-026 | `test_ac_026_delete_user` | PENDING |
| REQ-013 | AC-027 | `test_ac_027_persistence_across_instances` | PENDING |
| REQ-013 | AC-028 | `test_ac_028_service_with_fake_repository` | PENDING |
| REQ-014 | AC-029 | `test_ac_029_error_hierarchy_context` | PENDING |
| REQ-015 | — | `test_nfr_005_operations_logged` | PENDING |
| REQ-016 | AC-030 | `test_ac_030_event_user_created` | PENDING |
| REQ-016 | AC-031 | `test_ac_031_event_user_updated` | PENDING |
| REQ-016 | AC-032 | `test_ac_032_event_user_deleted` | PENDING |
| REQ-016 | AC-033 | `test_ac_033_event_password_changed` | PENDING |
| REQ-016 | AC-034 | `test_ac_034_event_role_changed` | PENDING |
| REQ-016 | AC-035 | `test_ac_035_event_activated` | PENDING |
| REQ-016 | AC-036 | `test_ac_036_event_deactivated` | PENDING |
| REQ-017 | AC-037 | `test_ac_037_no_event_on_failure` | PENDING |
| REQ-017 | AC-038 | `test_ac_038_no_publisher` | PENDING |
| INV-001 | — | `test_inv_001_create_read_consistency` | PENDING |
| INV-002 | — | `test_inv_002_password_round_trip` | PENDING |
| INV-003 | — | `test_inv_003_last_admin_invariant` | PENDING |
| INV-004 | — | `test_inv_004_update_semantics` | PENDING |
| INV-005 | — | `test_inv_005_uniqueness` | PENDING |
| INV-006 | — | `test_inv_006_event_correspondence` | PENDING |
| NFR-001 | — | `test_nfr_001_performance_budgets` | PENDING |
| NFR-002 | — | `test_nfr_002_no_plaintext_or_hash_exposed` | PENDING |
| NFR-003 | — | `test_nfr_003_api_backward_compatible` | PENDING |
| NFR-004 | — | `test_nfr_004_concurrent_repository_safety` | PENDING |
| NFR-005 | — | `test_nfr_005_operations_logged` | PENDING |
