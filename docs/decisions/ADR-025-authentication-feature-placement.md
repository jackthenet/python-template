# ADR-025: Authentication feature placement

## Status
Accepted

## Context
The authentication feature must authenticate users without duplicating the
user-management feature's user storage, password hashing, or password rules
(spec D1, D3). The project architecture places each feature in its own
directory under `src/backend/` with explicit public interfaces; `shared/` is
deliberately small and holds no feature-specific business logic.

## Decision
Create the feature at `src/backend/authentication/` as a standalone feature
that depends on the `backend.usermanagement` **public API only**
(`UserManager`, `UserRepository`, `UserRead`, and the structural
`EventPublisher` protocol). The feature owns its own persistence for
sessions, password resets, and WebAuthn credentials
(`SessionRepository`, `PasswordResetRepository`,
`WebAuthnCredentialRepository` ABCs + `Sqlite*` implementations) in the same
SQLite database as user-management. It does not modify user-management.

## Consequences
- User storage, Argon2id hashing, and password rules remain owned by
  user-management; authentication composes them via constructor injection.
- The feature boundary is explicit: user-management's spec lists
  authentication as out of scope, and authentication's spec lists user
  creation as out of scope.
- The shared SQLite database means `SQLModel.metadata.create_all` bootstraps
  all tables (user-management + authentication) from whichever repository is
  initialized first (D10).

## Alternatives Considered
- Extending `backend.usermanagement` with authentication methods — rejected:
  authentication is a distinct concern (sessions, recovery, passkeys,
  throttling) and the user-management spec explicitly scopes it out; mixing
  them would couple unrelated change drivers.
- Placing authentication in `backend/shared/` — rejected: `shared/` is
  deliberately small and holds no feature-specific business logic;
  authentication is a feature, not shared infrastructure.
- A separate SQLite database for sessions — rejected: sessions and resets
  reference user ids from the user-management database; a single database
  keeps the data coherent without cross-database coordination.

## References
- `docs/specs/authentication.md` (D1, D3, D10; §2)
- `docs/specs/user-management.md` (out of scope)
- `docs/decisions/ADR-018-user-management-feature-placement.md`
- `AGENTS.md` — Project Structure & Principles
