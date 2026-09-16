# ADR-065: Constructor DI plus module singleton get_session_service()

## Status
Accepted

## Context
The service must be testable with fakes and constructible for application
use. The repo pattern is constructor injection of repository ABCs plus an
optional structural `EventPublisher` (ADR-025, ADR-027 pattern), with
in-memory fakes for tests. Application code needs a stable access point
without re-plumbing the repository on every call, consistent with the
existing module singletons (`get_event_bus()`, `get_settings_registry()`).

## Decision
`SessionService` is constructed with a `SessionRepository` (authentication's
ABC, extended per ADR-061), an optional `event_bus` (structural
`EventPublisher` protocol; `None` → no events and no subscriptions), and an
optional `settings_registry` (`None` → shared `get_settings_registry()`)
(REQ-020). The module singleton `get_session_service(repository=None,
event_bus=None, settings_registry=None)` is the application access point:
the first call creates the singleton (requiring a repository — `ValueError`
without one), and subsequent calls (with or without arguments) return the
existing instance (REQ-020, AC-041, AC-042). `reset_session_service()`
clears the singleton for test isolation (AC-043).

## Consequences
- Tests construct `SessionService` directly with fakes (no singleton
  involvement); the singleton is application-only.
- A `None` event bus means no events and no subscriptions (REQ-018, AC-038) —
  the same structural pattern as the other features.
- Consistent with the eventbus/settings singleton pattern and the
  constructor-DI pattern of `AuthService`/`UserManager`/`FileService`.

## Alternatives Considered
- Singleton only (no constructor DI) — rejected: tests would share the
  singleton's state; constructor DI is the repo standard for testability
  (Q-57).
- Constructor DI only (no singleton) — rejected: application code would have
  to construct and retain the service itself; the singleton provides a
  stable access point consistent with `get_event_bus()` /
  `get_settings_registry()` (Q-57).

## References
- `docs/specs/session-management.md` (REQ-020, REQ-018; AC-041, AC-042,
  AC-043)
- `docs/decisions/ADR-025-authentication-feature-placement.md`
- `AI_Questions.md` (Q-57)
