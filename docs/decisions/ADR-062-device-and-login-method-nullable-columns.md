# ADR-062: Device info and login method as nullable columns on the sessions table

## Status
Accepted

## Context
"Active sessions/devices" requires per-session device identification, but
with no HTTP layer the backend cannot observe user-agent/IP in-process, and
the `Session` table has no device fields (REQ-016). Login is owned by
authentication (`AuthService.login(LoginRequest)`); the login method
(password vs. passkey) is known at session issuance but not stored. The
`Session` table is governed by authentication NFR-003 (backward-compatibility
contract); bootstrap is `create_all` with no migration framework, so adding
nullable columns is backward-compatible at the schema level.

## Decision
Capture device info at login (REQ-016): authentication's `LoginRequest` gains
optional `user_agent`/`ip`/`device_name` fields, and the `Session` table
gains nullable columns `user_agent`/`ip`/`device_name` plus a nullable
`login_method` column (`"password"` | `"passkey"`). Every login stores the
provided device fields (omitted → `None`) and the login method on the issued
session row. Existing rows remain `NULL`; the list exposes the fields as
`None` for pre-feature rows (REQ-004, EDGE-006).

## Consequences
- Device data lives directly on the `Session` row: no join table, no extra
  round trip; the list maps row → entry 1:1.
- Backward-compatible per authentication NFR-003: nullable columns,
  `create_all` bootstrap, existing rows `NULL`; the login schema extension is
  additive and all existing authentication behavior remains valid.
- `login_method` distinguishes password and passkey sessions in the list
  (AC-008, AC-032).
- Pre-feature rows list with all device fields `None` (AC-007, EDGE-006).

## Alternatives Considered
- A separate `session_devices` join table (one row per session, `sessions`
  table untouched) — rejected: a join table for a 1:1 relationship adds a
  second table and a join on every list for no benefit; nullable columns on
  the existing table are simpler and equally backward-compatible (Q-52).
- No device identification (a "device" is just a session listed with
  timestamps) — rejected: the feature's goal is active sessions/devices with
  device identification; device fields and the login method were explicitly
  requested (Q-36, Q-45).

## References
- `docs/specs/session-management.md` (REQ-016, REQ-004; AC-007, AC-008,
  AC-032; EDGE-006)
- `docs/specs/authentication.md` (NFR-003)
- `AI_Questions.md` (Q-36, Q-45, Q-52)
