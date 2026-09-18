# Spec: Session Management

## 1. Overview & Objectives
- **Feature Name:** Session Management
- **Target Component:** `src/backend/sessionmanagement/` (new feature package) plus additive, backward-compatible extensions to `src/backend/authentication/` (login schema, `Session` table columns, `SessionRepository` ABC)
- **Goal:** Manage the sessions owned by the authentication feature: list a user's active sessions/devices with device identification and a current-session marker; revoke a specific session or all sessions (self-service via token, admin via user id); clean up expired session rows; enforce a configurable per-user session cap with oldest-first eviction; and revoke all sessions on user password change, deactivation, or deletion.

## 2. Architecture & Design Decisions
- **Design Pattern:** Use-case service over the shared session store (no second session store). Constructor dependency injection of the authentication `SessionRepository` ABC plus optional structural `EventPublisher` and settings registry; module singleton `get_session_service()` for application use. Event-driven integration: the feature subscribes to authentication's `LoginSucceeded` (cap eviction) and user-management's `UserPasswordChanged`/`UserDeactivated`/`UserDeleted` (revocation-on-lifecycle). Feature-owned settings registration with live reads (mail-service / file-management pattern).
- **Dependencies:** No new third-party dependencies. Reuses `backend.authentication` (`Session` table, `SessionRepository` ABC, `session_info(token)`, `InvalidSessionError`, `LoginSucceeded` event, `LoginRequest` schema), `backend.usermanagement` (events `UserPasswordChanged`, `UserDeactivated`, `UserDeleted`), `backend.settings` (settings registry), `backend.eventbus` (event bus / structural `EventPublisher` protocol), `backend.logging` (shared logging feature).
- **Constraints:**
  - Backend-only in-process service — no HTTP/REST layer, no frontend.
  - MUST reuse authentication's `Session` table + `SessionRepository` (constructor-injected); no second session store.
  - Raw session tokens and token hashes never appear in list entries, log records, events, or error messages (only session ids) — extends authentication NFR-002.
  - No threads or background workers in the feature (cleanup is application-scheduled).
  - No change to expiration semantics: sessions expire per `authentication.session_ttl` (authentication REQ-007); no activity tracking, no `last_seen_at`, no `expires_at` updates.
- **Design Decisions:** (WHAT only; WHY goes to ADRs in `docs/decisions/` in Phase 2.)
  - A new feature package `backend.sessionmanagement` reuses authentication's session store; the `SessionRepository` ABC is extended additively (REQ-017).
  - Device identification is captured at login: optional `user_agent`/`ip`/`device_name` on the login schema, stored as nullable columns on the `sessions` table, plus a nullable `login_method` column (`"password"` | `"passkey"`) (REQ-016).
  - The per-user session cap is enforced event-driven on `LoginSucceeded` — authentication's login path is not modified beyond the additive schema fields (REQ-014).
  - Revocation on user lifecycle events is implemented as subscriptions to user-management events (REQ-015).
  - Expired-row cleanup is exposed as `cleanup_expired() -> int`, bounded by `sessionmanagement.cleanup_batch_size`, called by the application on its own schedule (REQ-012).
  - A single `list_sessions` method serves both self-service (token) and admin (user_id) listing (REQ-001).
  - No new exception types: argument errors are `ValueError`; invalid-token failures re-raise authentication's `InvalidSessionError` (REQ-002, REQ-009, REQ-010); revocation of unknown/already-revoked targets is an idempotent no-op (REQ-008, REQ-011).
  - Module singleton `get_session_service()` plus `reset_session_service()` for test isolation (REQ-020).

### Overlap & Extension of Existing Features (explicit)

- **`backend.authentication`** (spec: `docs/specs/authentication.md`):
  - **Reused unchanged:** REQ-006 (opaque 256-bit tokens, SHA-256 at rest), REQ-007 (TTL expiration via `authentication.session_ttl`), REQ-008 (`session_info(token)` — the token-path resolution point for all token-based operations here), REQ-009 (`logout(token)` — remains the token-based single-session path; this feature does not re-specify it), REQ-012 (reset completion revokes all sessions — unchanged; this feature's `UserPasswordChanged` subscription is idempotent with it), REQ-015 (passkey login issues a session with method `"passkey"` — source of the `login_method` column value), REQ-020 (typed lifecycle events incl. `LoginSucceeded` — the cap-eviction hook), REQ-021 (service representations never expose tokens — extended here), INV-002 (a session is valid iff unrevoked and unexpired — the valid-only listing rule), NFR-001 (performance measurement context), NFR-002 (secrets policy — extended), NFR-003 (public API backward-compatibility contract — governs the ABC extension below), NFR-005 (thread-safe repositories).
  - **Extended (additive, backward-compatible per authentication NFR-003):**
    - `LoginRequest` gains optional `user_agent`/`ip`/`device_name` fields (this spec REQ-016); omitted fields → `None` stored; all existing authentication behavior and acceptance criteria remain valid.
    - The `Session` table gains nullable columns `user_agent`/`ip`/`device_name`/`login_method`; existing rows are `NULL` (bootstrap is `create_all`, no migration framework — adding nullable columns is backward-compatible at the schema level).
    - The `SessionRepository` ABC gains `get`, `list_for_user`, `revoke_user_sessions`, and an optional `limit` parameter on `delete_expired` (this spec REQ-017); all existing ABC methods retain their behavior (only `delete_expired` gains a backward-compatible optional `limit`), so existing implementors and call sites remain valid.
  - **No spec amendment to `authentication.md`** (recorded decision).
- **`backend.usermanagement`** (spec: `docs/specs/user-management.md`): consumes events `UserPasswordChanged` (REQ-016/AC-033), `UserDeactivated` (REQ-016/AC-036), `UserDeleted` (REQ-016/AC-032). `change_password` (REQ-005) and all user-management behavior are unchanged — the new revocation behavior is a subscription in this feature (this spec REQ-015).
- **`backend.settings`** (spec: `docs/specs/settings.md`): feature-owned `register_settings(registry)` plus live reads of `sessionmanagement.*` keys (this spec REQ-019); `authentication.session_ttl` is reused as-is (no duplicate TTL key).
- **`backend.eventbus`** (spec: `docs/specs/event-bus.md`): the publisher is the structural `EventPublisher` protocol; the feature receives subscription events through the shared bus.
- **`backend.logging`** (spec: `docs/specs/logging.md`): `@logged_class` on `SessionService`, `@logged` on module functions (this spec REQ-022).

## 3. Data Structures & API Schemas

```python
# --- Session entry representation (this feature; read-only, no tokens/hashes) ---
class SessionEntry(BaseModel):
    session_id: UUID
    created_at: datetime            # UTC
    expires_at: datetime            # UTC
    is_current: bool                # True for exactly the session resolved from the provided token
    user_agent: str | None = None   # None for pre-feature rows
    ip: str | None = None           # None for pre-feature rows
    device_name: str | None = None  # None for pre-feature rows
    login_method: str | None = None # "password" | "passkey" | None (pre-feature rows)

# --- Events (this feature; non-sensitive data only — no tokens/hashes) ---
class SessionRevoked(BaseModel):
    user_id: UUID
    session_id: UUID

class AllSessionsRevoked(BaseModel):
    user_id: UUID
    excluded_session_id: UUID | None = None  # None = all sessions revoked incl. the caller's

class ExpiredSessionsDeleted(BaseModel):
    count: int

class SessionsListed(BaseModel):
    user_id: UUID
    count: int                      # number of entries returned

# --- Service public API (this feature) ---
class SessionService:
    def __init__(self, repository: SessionRepository,                 # authentication's ABC (extended, REQ-017)
                 event_bus: EventPublisher | None = None,             # structural publish protocol; None = no events/subscriptions
                 settings_registry: SettingsRegistry | None = None) -> None: ...  # None = shared get_settings_registry()
    def list_sessions(self, token: str | None = None, user_id: UUID | None = None,
                      limit: int | None = None) -> list[SessionEntry]: ...  # exactly one of token/user_id
    def revoke_session(self, session_id: UUID) -> None: ...            # idempotent no-op for unknown/already-revoked
    def logout_all_sessions(self, token: str) -> None: ...             # self-service; revokes the caller's session too
    def logout_other_sessions(self, token: str) -> None: ...           # self-service; keeps the caller's session
    def revoke_all_sessions(self, user_id: UUID, exclude_session_id: UUID | None = None) -> int: ...  # admin; returns count
    def cleanup_expired(self) -> int: ...                              # bounded by sessionmanagement.cleanup_batch_size

def register_settings(registry: SettingsRegistry) -> None: ...        # feature-owned registration (REQ-019)
def get_session_service(repository: SessionRepository | None = None,
                        event_bus: EventPublisher | None = None,
                        settings_registry: SettingsRegistry | None = None) -> SessionService: ...  # module singleton
    # first call creates the singleton and requires a repository; later calls return the existing instance
def reset_session_service() -> None: ...                              # clears the singleton (tests)

# --- Additive extension of authentication's SessionRepository ABC (REQ-017) ---
# Existing methods unchanged: add, get_by_token_hash, revoke, revoke_all_for_user; `delete_expired` is extended below (backward-compatible).
class SessionRepository(ABC):
    def get(self, session_id: UUID) -> Session | None: ...                       # NEW: row by id, any revocation state
    def list_for_user(self, user_id: UUID) -> Sequence[Session]: ...             # NEW: ALL rows for the user (any
                                                                                 #     revocation state), created_at descending
    def revoke_user_sessions(self, user_id: UUID, exclude_session_id: UUID | None = None) -> int: ...  # NEW
    def delete_expired(self, limit: int | None = None) -> int: ...               # SIGNATURE EXTENDED: optional limit;
                                                                                 #     None = all (previous behavior)

# --- Schema extension: authentication's Session table (REQ-016) ---
class Session(SQLModel, table=True):
    __tablename__ = "sessions"
    id: UUID                    # primary key
    user_id: UUID               # indexed
    token_hash: str             # unique, indexed — SHA-256 hex only
    created_at: datetime        # UTC
    expires_at: datetime        # UTC
    revoked: bool = False
    # NEW nullable columns (this feature; existing rows NULL):
    user_agent: str | None = None
    ip: str | None = None
    device_name: str | None = None
    login_method: str | None = None   # "password" | "passkey"

# --- Schema extension: authentication's LoginRequest (REQ-016) ---
class LoginRequest(BaseModel):
    identifier: str
    password: str
    # NEW optional fields (this feature): omitted = None stored
    user_agent: str | None = None
    ip: str | None = None
    device_name: str | None = None

# --- Settings registration (REQ-019) ---
register_settings(registry):
    registry.register(SettingDefinition(key="sessionmanagement.max_listed_sessions",
                                        kind=SettingKind.NUMBER, default=100, min_value=1, category="sessionmanagement"))
    registry.register(SettingDefinition(key="sessionmanagement.max_sessions_per_user",
                                        kind=SettingKind.NUMBER, default=5, min_value=1, category="sessionmanagement"))
    registry.register(SettingDefinition(key="sessionmanagement.cleanup_batch_size",
                                        kind=SettingKind.NUMBER, default=1000, min_value=1, category="sessionmanagement"))
# `authentication.session_ttl` (authentication feature) is reused unchanged — no duplicate TTL key.
```

## 4. Requirements

Each normative requirement MUST have a stable ID. These IDs propagate through the lifecycle:
`REQ-001 → AC-001 → test → task → implementation`.

| ID | Requirement |
|----|-------------|
| REQ-001 | `list_sessions(token=None, user_id=None, limit=None)` returns a bounded list of `SessionEntry` for the user identified by exactly one of `token` (self-service) or `user_id` (admin); both or neither provided → `ValueError`. |
| REQ-002 | The token path resolves the user and the current session via authentication's `session_info(token)` (authentication REQ-008); an unknown, revoked, or expired token raises `InvalidSessionError` (authentication). |
| REQ-003 | The list contains only valid sessions — unrevoked and unexpired (authentication INV-002); a user with zero valid sessions yields an empty list (no error). |
| REQ-004 | Each entry exposes exactly: `session_id`, `created_at`, `expires_at`, `is_current`, `user_agent`, `ip`, `device_name`, `login_method`; the device fields and `login_method` are `None` for rows created before this feature. |
| REQ-005 | `is_current` is `True` for exactly one entry — the session resolved from the provided token (token path); on the admin (`user_id`) path all entries have `is_current` `False`. |
| REQ-006 | List ordering: `created_at` descending (newest first), with the current session (token path) pinned first. |
| REQ-007 | The list is bounded by `limit` (no offset): `limit` defaults to the live-read `sessionmanagement.max_listed_sessions`; `limit < 1` → `ValueError`; the result is truncated to `limit`. |
| REQ-008 | `revoke_session(session_id)` revokes the session with that id; an unknown or already-revoked id is an idempotent no-op (no error, no event). |
| REQ-009 | `logout_all_sessions(token)` revokes all sessions for the token's user, including the caller's own session; an invalid token raises `InvalidSessionError` (authentication). |
| REQ-010 | `logout_other_sessions(token)` revokes all sessions for the token's user except the caller's current session; an invalid token raises `InvalidSessionError` (authentication). |
| REQ-011 | `revoke_all_sessions(user_id, exclude_session_id=None)` (admin; open in-process, no token) revokes all sessions for the user except the excluded session; returns the number of sessions revoked. |
| REQ-012 | `cleanup_expired() -> int` deletes up to the live-read `sessionmanagement.cleanup_batch_size` expired rows and returns the number deleted; the application calls it on its own schedule (no threads or background workers in the feature). |
| REQ-013 | Expiration semantics are unchanged: sessions expire per `authentication.session_ttl` (authentication REQ-007); this feature adds no expiration mode, no activity tracking, and no `expires_at` update. |
| REQ-014 | Per-user session cap: on `LoginSucceeded` (authentication REQ-020), if the user's valid session count exceeds the live-read `sessionmanagement.max_sessions_per_user`, the oldest valid sessions (`created_at` ascending) are revoked until the count equals the cap. |
| REQ-015 | Revocation on user lifecycle: the feature subscribes to `UserPasswordChanged`, `UserDeactivated`, `UserDeleted` (user-management) and revokes all sessions for the affected user on each. |
| REQ-016 | Device identification at login: authentication's `LoginRequest` gains optional `user_agent`/`ip`/`device_name` fields; the `Session` row gains nullable columns `user_agent`/`ip`/`device_name`/`login_method`; every login stores the provided device fields and the login method (`"password"` | `"passkey"`) on the issued session row (additive, backward-compatible per authentication NFR-003). |
| REQ-017 | Session store reuse: the feature reuses authentication's `Session` table and `SessionRepository` (constructor-injected); the ABC is extended additively with `get`, `list_for_user`, `revoke_user_sessions`, and an optional `limit` on `delete_expired` (backward-compatible per authentication NFR-003); no second session store. |
| REQ-018 | Typed events are published to the injected publisher: `SessionRevoked(user_id, session_id)`, `AllSessionsRevoked(user_id, excluded_session_id)`, `ExpiredSessionsDeleted(count)`, `SessionsListed(user_id, count)`; a `None` publisher means no events and no subscriptions. |
| REQ-019 | Settings: the feature registers `sessionmanagement.max_listed_sessions` (default 100), `sessionmanagement.max_sessions_per_user` (default 5), `sessionmanagement.cleanup_batch_size` (default 1000) via the feature-owned `register_settings(registry)` and reads them live on each operation; unregistered keys fall back to the hardcoded defaults. |
| REQ-020 | Construction: `SessionService` is constructed with a `SessionRepository` and an optional `event_bus` (structural `EventPublisher` protocol; `None` → no events/subscriptions) and an optional `settings_registry` (`None` → shared `get_settings_registry()`); `get_session_service()` is the module singleton for application use (first call creates it and requires a repository; subsequent calls return the existing instance); `reset_session_service()` clears the singleton (tests). |
| REQ-021 | Secrets: raw session tokens and token hashes never appear in list entries, log records, events, or error messages (only session ids) (extends authentication NFR-002 / REQ-021). |
| REQ-022 | Observability: `SessionService` is traced with `@logged_class` (`include_args=False`, `slow_threshold_ms=100`); the module functions (`register_settings`, `get_session_service`, `reset_session_service`) are traced with `@logged`. |

## 5. Acceptance Criteria

Each acceptance criterion MUST have a stable ID and MUST reference at least one requirement. Use Given/When/Then format.

| ID | References | Criterion |
|----|------------|-----------|
| AC-001 | REQ-001 | **Given** a user with 3 valid sessions, **When** `list_sessions(token)` is called with a valid token, **Then** 3 `SessionEntry` objects are returned **and** the entry for the token's session has `is_current` `True`. |
| AC-002 | REQ-001 | **Given** a user with 3 valid sessions, **When** `list_sessions(user_id=...)` is called, **Then** 3 entries are returned **and** every entry has `is_current` `False`. |
| AC-003 | REQ-001 | **Given** any state, **When** `list_sessions` is called with both `token` and `user_id` (or with neither), **Then** `ValueError` is raised. |
| AC-004 | REQ-002 | **Given** an unknown, revoked, or expired token, **When** `list_sessions(token)` is called, **Then** `InvalidSessionError` (authentication) is raised. |
| AC-005 | REQ-003 | **Given** a user with 2 valid sessions and 1 expired-but-not-cleaned session, **When** `list_sessions` is called, **Then** only the 2 valid sessions are returned. |
| AC-006 | REQ-003 | **Given** a user with zero valid sessions, **When** `list_sessions` is called, **Then** an empty list is returned (no error). |
| AC-007 | REQ-004 | **Given** a session row created before this feature (device columns `NULL`), **When** `list_sessions` is called, **Then** the entry's `user_agent`/`ip`/`device_name`/`login_method` are all `None`. |
| AC-008 | REQ-004, REQ-016 | **Given** a login with `user_agent`/`ip`/`device_name` provided, **When** `list_sessions` is called for that session, **Then** the entry exposes the provided values **and** `login_method` is `"password"`. |
| AC-009 | REQ-006 | **Given** a user with 3 valid sessions, **When** `list_sessions(token)` is called with the token of the oldest session, **Then** the oldest session's entry is first **and** the remaining entries are ordered `created_at` descending. |
| AC-010 | REQ-006 | **Given** a user with 3 valid sessions, **When** `list_sessions(user_id=...)` is called, **Then** the entries are ordered `created_at` descending (newest first). |
| AC-011 | REQ-007 | **Given** the default `max_listed_sessions` 100 and a user with 150 valid sessions, **When** `list_sessions` is called without an explicit limit, **Then** 100 entries are returned. |
| AC-012 | REQ-007 | **Given** a user with 5 valid sessions, **When** `list_sessions(limit=2)` is called, **Then** 2 entries are returned. |
| AC-013 | REQ-007 | **Given** any state, **When** `list_sessions(limit=0)` (or a negative limit) is called, **Then** `ValueError` is raised. |
| AC-014 | REQ-008 | **Given** a valid session, **When** `revoke_session(session_id)` is called, **Then** the session is revoked (it no longer appears in `list_sessions`). |
| AC-015 | REQ-008 | **Given** a session id that does not exist, **When** `revoke_session` is called, **Then** no error is raised (idempotent no-op). |
| AC-016 | REQ-008 | **Given** an already-revoked session id, **When** `revoke_session` is called, **Then** no error is raised (idempotent no-op). |
| AC-017 | REQ-009 | **Given** a user with 3 valid sessions including the token's, **When** `logout_all_sessions(token)` is called, **Then** all 3 sessions are revoked **and** the token is immediately unusable. |
| AC-018 | REQ-009 | **Given** an unknown, revoked, or expired token, **When** `logout_all_sessions(token)` is called, **Then** `InvalidSessionError` (authentication) is raised. |
| AC-019 | REQ-010 | **Given** a user with 3 valid sessions including the token's, **When** `logout_other_sessions(token)` is called, **Then** the other 2 sessions are revoked **and** the token's session remains valid. |
| AC-020 | REQ-010 | **Given** a user with exactly 1 valid session (the token's), **When** `logout_other_sessions(token)` is called, **Then** the token's session remains valid (nothing else revoked). |
| AC-021 | REQ-011 | **Given** a user with 3 valid sessions, **When** `revoke_all_sessions(user_id)` is called, **Then** all 3 sessions are revoked **and** 3 is returned. |
| AC-022 | REQ-011 | **Given** a user with 3 valid sessions, **When** `revoke_all_sessions(user_id, exclude_session_id=X)` is called, **Then** the other 2 sessions are revoked, **And** session X remains valid, **and** 2 is returned. |
| AC-023 | REQ-011 | **Given** a user with zero valid sessions, **When** `revoke_all_sessions(user_id)` is called, **Then** 0 is returned (no error). |
| AC-024 | REQ-012 | **Given** 150 expired rows and `cleanup_batch_size` 100, **When** `cleanup_expired()` is called, **Then** 100 rows are deleted **and** 100 is returned. |
| AC-025 | REQ-012 | **Given** no expired rows, **When** `cleanup_expired()` is called, **Then** 0 is returned (no error). |
| AC-026 | REQ-013 | **Given** a session created with TTL `T` and any sequence of this feature's operations, **When** `T` has elapsed, **Then** the session is invalid **and** no operation of this feature has changed `expires_at` or tracked activity. |
| AC-027 | REQ-014 | **Given** `max_sessions_per_user` 5 and a user with 5 valid sessions, **When** a 6th login succeeds (`LoginSucceeded`), **Then** the oldest session is revoked **and** the user has 5 valid sessions. |
| AC-028 | REQ-014 | **Given** `max_sessions_per_user` 5 and a user with 3 valid sessions, **When** a login succeeds, **Then** no session is revoked **and** the user has 4 valid sessions. |
| AC-029 | REQ-015 | **Given** a user with valid sessions, **When** `change_password` succeeds (`UserPasswordChanged`), **Then** all sessions for the user are revoked. |
| AC-030 | REQ-015 | **Given** a user with valid sessions, **When** the user is deactivated (`UserDeactivated`), **Then** all sessions for the user are revoked. |
| AC-031 | REQ-015 | **Given** a user with valid sessions, **When** the user is deleted (`UserDeleted`), **Then** all sessions for the user are revoked. |
| AC-032 | REQ-016 | **Given** a passkey login (authentication REQ-015), **When** the issued session row is inspected, **Then** `login_method` is `"passkey"`. |
| AC-033 | REQ-017 | **Given** the feature constructed with authentication's `SessionRepository`, **When** any operation runs, **Then** it acts on the same `sessions` table as authentication (no second session store). |
| AC-034 | REQ-018 | **Given** a publisher, **When** `revoke_session` revokes a session, **Then** `SessionRevoked(user_id, session_id)` is published. |
| AC-035 | REQ-018 | **Given** a publisher, **When** `logout_all_sessions`, `logout_other_sessions`, or `revoke_all_sessions` succeeds, **Then** `AllSessionsRevoked(user_id, excluded_session_id)` is published with the correct excluded id (`None` for `logout_all_sessions` and for `revoke_all_sessions` without exclusion); when 0 sessions are revoked, no event is published. |
| AC-036 | REQ-018 | **Given** a publisher, **When** `cleanup_expired` deletes `n > 0` rows, **Then** `ExpiredSessionsDeleted(n)` is published; **and** when 0 rows are deleted, no event is published. |
| AC-037 | REQ-018 | **Given** a publisher, **When** `list_sessions` succeeds, **Then** `SessionsListed(user_id, count)` is published with `count` equal to the number of entries returned. |
| AC-038 | REQ-018 | **Given** a `None` publisher, **When** any operation runs, **Then** no event is published, no error is raised, **and** no subscription to user-management or authentication events occurs. |
| AC-039 | REQ-019 | **Given** a settings registry, **When** `register_settings(registry)` is called, **Then** the 3 keys are registered with defaults 100 / 5 / 1000 (all `min_value` 1). |
| AC-040 | REQ-019 | **Given** `max_listed_sessions` changed in the registry, **When** `list_sessions` is called without an explicit limit, **Then** the new value is used (live read). |
| AC-041 | REQ-020 | **Given** no singleton yet, **When** `get_session_service(repository)` is called, **Then** the singleton is created; **and** subsequent calls (with or without arguments) return the same instance. |
| AC-042 | REQ-020 | **Given** no singleton yet, **When** `get_session_service()` is called without a repository, **Then** `ValueError` is raised. |
| AC-043 | REQ-020 | **Given** an existing singleton, **When** `reset_session_service()` is called, **Then** the singleton is cleared (a subsequent `get_session_service(repository)` creates a new instance). |
| AC-044 | REQ-021 | **Given** any `SessionEntry`, log record, published event, or error message produced by this feature, **When** inspected, **Then** no raw session token or token hash appears (only session ids). |
| AC-045 | REQ-022 | **Given** `SessionService`, **When** its methods are called, **Then** entry/exit/exception records are produced by `@logged_class` **and** no log record contains a raw token or token hash. |

## 6. Invariants

State invariants that hold over a large input space. These become Hypothesis property-based tests.

| ID | Invariant |
|----|-----------|
| INV-001 | Revocation idempotency: for any table state, re-running `revoke_session`, `revoke_all_sessions`, `logout_other_sessions`, cap eviction, or user-lifecycle revocation after it has succeeded is a no-op — no error, no state change, no duplicate event (an operation that revokes 0 sessions publishes no event, per AC-035). `logout_all_sessions` is the exception: it revokes the caller's own session, so a re-run with the same token raises `InvalidSessionError` (authentication) because the token is now revoked. |
| INV-002 | Valid-only listing: for any table state, every entry of `list_sessions` satisfies `revoked == False` and `expires_at > now` (at call time) — the list never contains an invalid session (authentication INV-002). |
| INV-003 | Cap: after `LoginSucceeded` handling, the user's valid session count is at most `sessionmanagement.max_sessions_per_user` (as read at that moment). |
| INV-004 | Secrets: for any operation output — returned entries, published events, raised error messages — the raw session token and its SHA-256 hash never appear. |
| INV-005 | Current-session pinning: for any table state and any valid token, the first entry of `list_sessions(token)` is the session resolved from that token. |

## 7. Edge Cases & Error Conditions

| ID | Condition | Expected Behavior |
|----|-----------|-------------------|
| EDGE-001 | A user with zero valid sessions | `list_sessions` → empty list; `revoke_all_sessions` → 0 returned; `logout_all_sessions`/`logout_other_sessions` → `InvalidSessionError` (authentication) — a valid token implies a valid session (authentication INV-002), so no valid token exists in this state. |
| EDGE-002 | `revoke_session` with an unknown session id | Idempotent no-op (no error, no event). |
| EDGE-003 | `revoke_session` with an already-revoked session id | Idempotent no-op (no error, no event). |
| EDGE-004 | `logout_all_sessions` including the caller's own session | The caller's token becomes unusable (self-lockout accepted for self-service). |
| EDGE-005 | `logout_other_sessions` when the caller's session is the only valid session | Nothing is revoked; the caller remains valid. |
| EDGE-006 | Device fields / `login_method` for pre-existing rows (created before this feature) | All `None` in the entry (no error). |
| EDGE-007 | Expired-but-not-cleaned rows at listing time | Excluded from the list (valid-only, per authentication INV-002). |
| EDGE-008 | `list_sessions` called with both `token` and `user_id` (or with neither) | `ValueError`. |
| EDGE-009 | `list_sessions` with `limit < 1` | `ValueError`. |
| EDGE-010 | Concurrent revocation and listing (one thread revokes while another lists) | No crash; the list reflects a consistent revocation state (a row is either present or absent, never partial). |
| EDGE-011 | Cap eviction at login when the user already has exactly `max_sessions_per_user` valid sessions | The oldest session is evicted; the new session is kept. |
| EDGE-012 | `cleanup_expired` with fewer expired rows than `cleanup_batch_size` | All expired rows are deleted; the count is returned. |

## 8. Non-Functional Requirements

| ID | Category | Requirement |
|----|----------|-------------|
| NFR-001 | Performance | Listing 100 sessions completes in ≤ 100 ms at p95; revoking all sessions for a user with 1000 sessions completes in ≤ 500 ms at p95; cleanup of 1000 expired rows completes in ≤ 500 ms at p95 — all measured on local hardware against a local SQLite database with the shared logging feature configured at its default INFO level with a synchronous console sink (DEBUG method tracing off); the budgets hold including the per-call logging overhead at that level. |
| NFR-002 | Security | Raw session tokens, token hashes, and passwords never appear in log records, events, error messages, or list entries (only session ids); tokens remain ≥ 256-bit random and stored only as SHA-256 hashes (authentication REQ-006, NFR-002). |
| NFR-003 | Contract | The public API of `backend.sessionmanagement` (`SessionService`, `SessionEntry`, the 4 events, `register_settings`, `get_session_service`, `reset_session_service`) is a backward-compatibility contract; the `SessionRepository` ABC extension is additive and backward-compatible per authentication NFR-003. |
| NFR-004 | Observability | `SessionService` is traced with `@logged_class` (`include_args=False`, `slow_threshold_ms=100`; entry/exit/exception per public method); module functions are traced with `@logged`; lifecycle events are published to the injected publisher. |
| NFR-005 | Reliability | The service and the SQLite repositories are safe for concurrent use from multiple threads (each operation opens its own session; SQLite busy-timeout serializes concurrent writers; authentication NFR-005). |

## 9. Observability & Logging

| Operation / Event | Level | Context |
|-------------------|-------|---------|
| Public method entry/exit (all `SessionService` methods) | DEBUG | Method name, elapsed ms; no arguments (`include_args` stays `False`). |
| Slow call (elapsed > `slow_threshold_ms` = 100 ms) | WARNING | Method name, elapsed ms (the end-of-call line escalates to the default `slow_level` of the logging feature). |
| Method exception (`InvalidSessionError` re-raise, `ValueError`, repository failure) | DEBUG | Exception type and secret-free message; no token, no hash, no identifier value. |
| `revoke_session` / `revoke_all_sessions` / `cleanup_expired` success | DEBUG | Method name, session id / user id / count, elapsed ms. |
| Lifecycle events (`SessionRevoked`, `AllSessionsRevoked`, `ExpiredSessionsDeleted`, `SessionsListed`) | — | Published to the injected `EventPublisher` (not logged by this feature); events carry non-sensitive data only (user ids, session ids, counts — no tokens/hashes). |

- **Default level:** INFO; routine method tracing at DEBUG (off by default at the INFO default level); exceptions are logged with secret-free messages.
- **Error conditions:** `InvalidSessionError` (re-raised from authentication for unknown/revoked/expired tokens — the token never appears in the record); `ValueError` for argument violations (limit < 1; both/neither `token`+`user_id`; first `get_session_service()` call without a repository); repository failures propagate as-is (secret-free).

## 10. Test Strategy

Map each requirement/AC to a test category. This drives the test file layout.

| ID | Test Category | Test File | Test Function |
|----|---------------|-----------|---------------|
| REQ-001 | acceptance, unit | `tests/acceptance/sessionmanagement/test_list_sessions.py`, `tests/unit/sessionmanagement/test_validation.py` | `test_ac_001_list_token_returns_entries_with_current_flag`, `test_ac_002_list_user_id_admin_all_not_current`, `test_ac_003_both_or_neither_token_user_id_value_error` |
| REQ-002 | acceptance | `tests/acceptance/sessionmanagement/test_list_sessions.py` | `test_ac_004_list_invalid_token_raises` |
| REQ-003 | acceptance | `tests/acceptance/sessionmanagement/test_list_sessions.py` | `test_ac_005_list_excludes_expired_rows`, `test_ac_006_list_zero_sessions_empty` |
| REQ-004 | acceptance, integration | `tests/acceptance/sessionmanagement/test_list_sessions.py`, `tests/integration/sessionmanagement/test_device_fields.py` | `test_ac_007_pre_feature_row_null_device_fields`, `test_ac_008_login_stores_device_fields` |
| REQ-005 | acceptance | `tests/acceptance/sessionmanagement/test_list_sessions.py` | `test_ac_001_list_token_returns_entries_with_current_flag`, `test_ac_002_list_user_id_admin_all_not_current` |
| REQ-006 | acceptance | `tests/acceptance/sessionmanagement/test_list_sessions.py` | `test_ac_009_list_current_session_pinned_first`, `test_ac_010_list_ordered_created_at_desc` |
| REQ-007 | acceptance, unit | `tests/acceptance/sessionmanagement/test_list_sessions.py`, `tests/unit/sessionmanagement/test_validation.py` | `test_ac_011_list_default_limit_100`, `test_ac_012_list_explicit_limit_truncates`, `test_ac_013_limit_below_one_value_error` |
| REQ-008 | acceptance | `tests/acceptance/sessionmanagement/test_revocation.py` | `test_ac_014_revoke_session_revokes`, `test_ac_015_revoke_unknown_id_noop`, `test_ac_016_revoke_already_revoked_noop` |
| REQ-009 | acceptance | `tests/acceptance/sessionmanagement/test_revocation.py` | `test_ac_017_logout_all_revokes_including_caller`, `test_ac_018_logout_all_invalid_token_raises` |
| REQ-010 | acceptance | `tests/acceptance/sessionmanagement/test_revocation.py` | `test_ac_019_logout_other_keeps_caller`, `test_ac_020_logout_other_only_caller_noop` |
| REQ-011 | acceptance | `tests/acceptance/sessionmanagement/test_revocation.py` | `test_ac_021_revoke_all_returns_count`, `test_ac_022_revoke_all_excludes_session`, `test_ac_023_revoke_all_zero_sessions` |
| REQ-012 | acceptance | `tests/acceptance/sessionmanagement/test_cleanup.py` | `test_ac_024_cleanup_bounded_by_batch_size`, `test_ac_025_cleanup_no_expired_returns_zero` |
| REQ-013 | acceptance | `tests/acceptance/sessionmanagement/test_expiration.py` | `test_ac_026_expiration_unchanged_no_activity_tracking` |
| REQ-014 | acceptance | `tests/acceptance/sessionmanagement/test_cap_eviction.py` | `test_ac_027_cap_evicts_oldest_at_sixth_login`, `test_ac_028_no_eviction_below_cap` |
| REQ-015 | integration | `tests/integration/sessionmanagement/test_user_lifecycle.py` | `test_ac_029_password_change_revokes_all`, `test_ac_030_deactivation_revokes_all`, `test_ac_031_deletion_revokes_all` |
| REQ-016 | integration, acceptance | `tests/integration/sessionmanagement/test_device_fields.py`, `tests/acceptance/sessionmanagement/test_list_sessions.py` | `test_ac_008_login_stores_device_fields`, `test_ac_032_passkey_login_stores_method` |
| REQ-017 | acceptance | `tests/acceptance/sessionmanagement/test_store_reuse.py` | `test_ac_033_same_sessions_table_as_authentication` |
| REQ-018 | acceptance | `tests/acceptance/sessionmanagement/test_events.py` | `test_ac_034_session_revoked_event`, `test_ac_035_all_sessions_revoked_event`, `test_ac_036_expired_sessions_deleted_event`, `test_ac_037_sessions_listed_event`, `test_ac_038_none_publisher_no_events_no_subscriptions` |
| REQ-019 | acceptance | `tests/acceptance/sessionmanagement/test_settings.py` | `test_ac_039_register_settings_defaults`, `test_ac_040_live_read_max_listed_sessions` |
| REQ-020 | acceptance, unit | `tests/acceptance/sessionmanagement/test_singleton.py`, `tests/unit/sessionmanagement/test_validation.py` | `test_ac_041_singleton_created_once`, `test_ac_042_singleton_first_call_without_repository_value_error`, `test_ac_043_reset_session_service` |
| REQ-021 | acceptance | `tests/acceptance/sessionmanagement/test_observability.py` | `test_ac_044_no_tokens_in_outputs` |
| REQ-022 | acceptance | `tests/acceptance/sessionmanagement/test_observability.py` | `test_ac_045_traced_methods_no_tokens_in_logs` |
| AC-001 | acceptance | `tests/acceptance/sessionmanagement/test_list_sessions.py` | `test_ac_001_list_token_returns_entries_with_current_flag` |
| AC-002 | acceptance | `tests/acceptance/sessionmanagement/test_list_sessions.py` | `test_ac_002_list_user_id_admin_all_not_current` |
| AC-003 | unit | `tests/unit/sessionmanagement/test_validation.py` | `test_ac_003_both_or_neither_token_user_id_value_error` |
| AC-004 | acceptance | `tests/acceptance/sessionmanagement/test_list_sessions.py` | `test_ac_004_list_invalid_token_raises` |
| AC-005 | acceptance | `tests/acceptance/sessionmanagement/test_list_sessions.py` | `test_ac_005_list_excludes_expired_rows` |
| AC-006 | acceptance | `tests/acceptance/sessionmanagement/test_list_sessions.py` | `test_ac_006_list_zero_sessions_empty` |
| AC-007 | acceptance | `tests/acceptance/sessionmanagement/test_list_sessions.py` | `test_ac_007_pre_feature_row_null_device_fields` |
| AC-008 | integration | `tests/integration/sessionmanagement/test_device_fields.py` | `test_ac_008_login_stores_device_fields` |
| AC-009 | acceptance | `tests/acceptance/sessionmanagement/test_list_sessions.py` | `test_ac_009_list_current_session_pinned_first` |
| AC-010 | acceptance | `tests/acceptance/sessionmanagement/test_list_sessions.py` | `test_ac_010_list_ordered_created_at_desc` |
| AC-011 | acceptance | `tests/acceptance/sessionmanagement/test_list_sessions.py` | `test_ac_011_list_default_limit_100` |
| AC-012 | acceptance | `tests/acceptance/sessionmanagement/test_list_sessions.py` | `test_ac_012_list_explicit_limit_truncates` |
| AC-013 | unit | `tests/unit/sessionmanagement/test_validation.py` | `test_ac_013_limit_below_one_value_error` |
| AC-014 | acceptance | `tests/acceptance/sessionmanagement/test_revocation.py` | `test_ac_014_revoke_session_revokes` |
| AC-015 | acceptance | `tests/acceptance/sessionmanagement/test_revocation.py` | `test_ac_015_revoke_unknown_id_noop` |
| AC-016 | acceptance | `tests/acceptance/sessionmanagement/test_revocation.py` | `test_ac_016_revoke_already_revoked_noop` |
| AC-017 | acceptance | `tests/acceptance/sessionmanagement/test_revocation.py` | `test_ac_017_logout_all_revokes_including_caller` |
| AC-018 | acceptance | `tests/acceptance/sessionmanagement/test_revocation.py` | `test_ac_018_logout_all_invalid_token_raises` |
| AC-019 | acceptance | `tests/acceptance/sessionmanagement/test_revocation.py` | `test_ac_019_logout_other_keeps_caller` |
| AC-020 | acceptance | `tests/acceptance/sessionmanagement/test_revocation.py` | `test_ac_020_logout_other_only_caller_noop` |
| AC-021 | acceptance | `tests/acceptance/sessionmanagement/test_revocation.py` | `test_ac_021_revoke_all_returns_count` |
| AC-022 | acceptance | `tests/acceptance/sessionmanagement/test_revocation.py` | `test_ac_022_revoke_all_excludes_session` |
| AC-023 | acceptance | `tests/acceptance/sessionmanagement/test_revocation.py` | `test_ac_023_revoke_all_zero_sessions` |
| AC-024 | acceptance | `tests/acceptance/sessionmanagement/test_cleanup.py` | `test_ac_024_cleanup_bounded_by_batch_size` |
| AC-025 | acceptance | `tests/acceptance/sessionmanagement/test_cleanup.py` | `test_ac_025_cleanup_no_expired_returns_zero` |
| AC-026 | acceptance | `tests/acceptance/sessionmanagement/test_expiration.py` | `test_ac_026_expiration_unchanged_no_activity_tracking` |
| AC-027 | acceptance | `tests/acceptance/sessionmanagement/test_cap_eviction.py` | `test_ac_027_cap_evicts_oldest_at_sixth_login` |
| AC-028 | acceptance | `tests/acceptance/sessionmanagement/test_cap_eviction.py` | `test_ac_028_no_eviction_below_cap` |
| AC-029 | integration | `tests/integration/sessionmanagement/test_user_lifecycle.py` | `test_ac_029_password_change_revokes_all` |
| AC-030 | integration | `tests/integration/sessionmanagement/test_user_lifecycle.py` | `test_ac_030_deactivation_revokes_all` |
| AC-031 | integration | `tests/integration/sessionmanagement/test_user_lifecycle.py` | `test_ac_031_deletion_revokes_all` |
| AC-032 | integration | `tests/integration/sessionmanagement/test_device_fields.py` | `test_ac_032_passkey_login_stores_method` |
| AC-033 | acceptance | `tests/acceptance/sessionmanagement/test_store_reuse.py` | `test_ac_033_same_sessions_table_as_authentication` |
| AC-034 | acceptance | `tests/acceptance/sessionmanagement/test_events.py` | `test_ac_034_session_revoked_event` |
| AC-035 | acceptance | `tests/acceptance/sessionmanagement/test_events.py` | `test_ac_035_all_sessions_revoked_event` |
| AC-036 | acceptance | `tests/acceptance/sessionmanagement/test_events.py` | `test_ac_036_expired_sessions_deleted_event` |
| AC-037 | acceptance | `tests/acceptance/sessionmanagement/test_events.py` | `test_ac_037_sessions_listed_event` |
| AC-038 | acceptance | `tests/acceptance/sessionmanagement/test_events.py` | `test_ac_038_none_publisher_no_events_no_subscriptions` |
| AC-039 | acceptance | `tests/acceptance/sessionmanagement/test_settings.py` | `test_ac_039_register_settings_defaults` |
| AC-040 | acceptance | `tests/acceptance/sessionmanagement/test_settings.py` | `test_ac_040_live_read_max_listed_sessions` |
| AC-041 | acceptance | `tests/acceptance/sessionmanagement/test_singleton.py` | `test_ac_041_singleton_created_once` |
| AC-042 | unit | `tests/unit/sessionmanagement/test_validation.py` | `test_ac_042_singleton_first_call_without_repository_value_error` |
| AC-043 | acceptance | `tests/acceptance/sessionmanagement/test_singleton.py` | `test_ac_043_reset_session_service` |
| AC-044 | acceptance | `tests/acceptance/sessionmanagement/test_observability.py` | `test_ac_044_no_tokens_in_outputs` |
| AC-045 | acceptance | `tests/acceptance/sessionmanagement/test_observability.py` | `test_ac_045_traced_methods_no_tokens_in_logs` |
| INV-001 | property | `tests/property/sessionmanagement/test_sessionmanagement_properties.py` | `test_inv_001_revocation_idempotent` |
| INV-002 | property | `tests/property/sessionmanagement/test_sessionmanagement_properties.py` | `test_inv_002_valid_only_listing` |
| INV-003 | property | `tests/property/sessionmanagement/test_sessionmanagement_properties.py` | `test_inv_003_cap_held_after_login` |
| INV-004 | property | `tests/property/sessionmanagement/test_sessionmanagement_properties.py` | `test_inv_004_no_tokens_in_outputs` |
| INV-005 | property | `tests/property/sessionmanagement/test_sessionmanagement_properties.py` | `test_inv_005_current_session_first` |
| EDGE-001 | acceptance | `tests/acceptance/sessionmanagement/test_revocation.py` | `test_edge_001_zero_sessions_empty_and_noop` |
| EDGE-002 | acceptance | `tests/acceptance/sessionmanagement/test_revocation.py` | `test_edge_002_revoke_unknown_id_noop` |
| EDGE-003 | acceptance | `tests/acceptance/sessionmanagement/test_revocation.py` | `test_edge_003_revoke_already_revoked_noop` |
| EDGE-004 | acceptance | `tests/acceptance/sessionmanagement/test_revocation.py` | `test_edge_004_logout_all_self_lockout` |
| EDGE-005 | acceptance | `tests/acceptance/sessionmanagement/test_revocation.py` | `test_edge_005_logout_other_only_caller` |
| EDGE-006 | acceptance | `tests/acceptance/sessionmanagement/test_list_sessions.py` | `test_edge_006_pre_feature_null_fields` |
| EDGE-007 | acceptance | `tests/acceptance/sessionmanagement/test_list_sessions.py` | `test_edge_007_expired_rows_excluded` |
| EDGE-008 | unit | `tests/unit/sessionmanagement/test_validation.py` | `test_edge_008_both_or_neither_value_error` |
| EDGE-009 | unit | `tests/unit/sessionmanagement/test_validation.py` | `test_edge_009_limit_below_one_value_error` |
| EDGE-010 | integration | `tests/integration/sessionmanagement/test_concurrency.py` | `test_edge_010_concurrent_revocation_and_listing` |
| EDGE-011 | acceptance | `tests/acceptance/sessionmanagement/test_cap_eviction.py` | `test_edge_011_cap_eviction_at_exact_cap` |
| EDGE-012 | acceptance | `tests/acceptance/sessionmanagement/test_cleanup.py` | `test_edge_012_cleanup_below_batch_size` |
| NFR-001 | contract | `tests/contract/sessionmanagement/test_performance.py` | `test_nfr_001_list_100_sessions_budget`, `test_nfr_001_revoke_1000_sessions_budget`, `test_nfr_001_cleanup_1000_rows_budget` |
| NFR-002 | property | `tests/property/sessionmanagement/test_sessionmanagement_properties.py` | `test_inv_004_no_tokens_in_outputs` (shared with INV-004) |
| NFR-003 | contract | `tests/contract/sessionmanagement/test_contract.py` | `test_nfr_003_public_api_contract` |
| NFR-004 | acceptance | `tests/acceptance/sessionmanagement/test_observability.py` | `test_nfr_004_traced_service_publishes_events` |
| NFR-005 | integration | `tests/integration/sessionmanagement/test_concurrency.py` | `test_nfr_005_concurrent_threads_safe` |

## 11. Traceability Matrix

Maintain this matrix as tests are written and pass. Every normative requirement MUST have at least one executable test.

| Requirement | Acceptance Criterion | Test | Status |
|-------------|---------------------|------|--------|
| REQ-001 | AC-001, AC-002, AC-003 | `test_ac_001_list_token_returns_entries_with_current_flag`, `test_ac_002_list_user_id_admin_all_not_current`, `test_ac_003_both_or_neither_token_user_id_value_error` | PENDING |
| REQ-002 | AC-004 | `test_ac_004_list_invalid_token_raises` | PENDING |
| REQ-003 | AC-005, AC-006 | `test_ac_005_list_excludes_expired_rows`, `test_ac_006_list_zero_sessions_empty` | PENDING |
| REQ-004 | AC-007, AC-008 | `test_ac_007_pre_feature_row_null_device_fields`, `test_ac_008_login_stores_device_fields` | PENDING |
| REQ-005 | AC-001, AC-002 | `test_ac_001_list_token_returns_entries_with_current_flag`, `test_ac_002_list_user_id_admin_all_not_current` | PENDING |
| REQ-006 | AC-009, AC-010 | `test_ac_009_list_current_session_pinned_first`, `test_ac_010_list_ordered_created_at_desc` | PENDING |
| REQ-007 | AC-011, AC-012, AC-013 | `test_ac_011_list_default_limit_100`, `test_ac_012_list_explicit_limit_truncates`, `test_ac_013_limit_below_one_value_error` | PENDING |
| REQ-008 | AC-014, AC-015, AC-016 | `test_ac_014_revoke_session_revokes`, `test_ac_015_revoke_unknown_id_noop`, `test_ac_016_revoke_already_revoked_noop` | PENDING |
| REQ-009 | AC-017, AC-018 | `test_ac_017_logout_all_revokes_including_caller`, `test_ac_018_logout_all_invalid_token_raises` | PENDING |
| REQ-010 | AC-019, AC-020 | `test_ac_019_logout_other_keeps_caller`, `test_ac_020_logout_other_only_caller_noop` | PENDING |
| REQ-011 | AC-021, AC-022, AC-023 | `test_ac_021_revoke_all_returns_count`, `test_ac_022_revoke_all_excludes_session`, `test_ac_023_revoke_all_zero_sessions` | PENDING |
| REQ-012 | AC-024, AC-025 | `test_ac_024_cleanup_bounded_by_batch_size`, `test_ac_025_cleanup_no_expired_returns_zero` | PENDING |
| REQ-013 | AC-026 | `test_ac_026_expiration_unchanged_no_activity_tracking` | PENDING |
| REQ-014 | AC-027, AC-028 | `test_ac_027_cap_evicts_oldest_at_sixth_login`, `test_ac_028_no_eviction_below_cap` | PENDING |
| REQ-015 | AC-029, AC-030, AC-031 | `test_ac_029_password_change_revokes_all`, `test_ac_030_deactivation_revokes_all`, `test_ac_031_deletion_revokes_all` | PENDING |
| REQ-016 | AC-008, AC-032 | `test_ac_008_login_stores_device_fields`, `test_ac_032_passkey_login_stores_method` | PENDING |
| REQ-017 | AC-033 | `test_ac_033_same_sessions_table_as_authentication` | PENDING |
| REQ-018 | AC-034, AC-035, AC-036, AC-037, AC-038 | `test_ac_034_session_revoked_event`, `test_ac_035_all_sessions_revoked_event`, `test_ac_036_expired_sessions_deleted_event`, `test_ac_037_sessions_listed_event`, `test_ac_038_none_publisher_no_events_no_subscriptions` | PENDING |
| REQ-019 | AC-039, AC-040 | `test_ac_039_register_settings_defaults`, `test_ac_040_live_read_max_listed_sessions` | PENDING |
| REQ-020 | AC-041, AC-042, AC-043 | `test_ac_041_singleton_created_once`, `test_ac_042_singleton_first_call_without_repository_value_error`, `test_ac_043_reset_session_service` | PENDING |
| REQ-021 | AC-044 | `test_ac_044_no_tokens_in_outputs` | PENDING |
| REQ-022 | AC-045 | `test_ac_045_traced_methods_no_tokens_in_logs` | PENDING |
| INV-001 | — | `test_inv_001_revocation_idempotent` | PENDING |
| INV-002 | — | `test_inv_002_valid_only_listing` | PENDING |
| INV-003 | — | `test_inv_003_cap_held_after_login` | PENDING |
| INV-004 | — | `test_inv_004_no_tokens_in_outputs` | PENDING |
| INV-005 | — | `test_inv_005_current_session_first` | PENDING |
