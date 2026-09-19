# ADR-066: Bounded session list without offset, created_at descending, current session pinned first

## Status
Accepted

## Context
The list API must serve both self-service (token) and admin (user_id)
listing (REQ-001, Q-42) with deterministic ordering and bounded output.
file-management's `list_files` uses limit/offset pagination; the session
list is a "devices" view, not a data-browsing view, and must bound its
output regardless of how many valid sessions a user has (e.g., pre-feature
users with many sessions — AC-011), because the cap is enforced only at
login (ADR-063).

## Decision
A single `list_sessions(token=None, user_id=None, limit=None)` method serves
both paths — exactly one of `token`/`user_id` (both or neither →
`ValueError`) (REQ-001, EDGE-008). The list is bounded by `limit` with no
offset: `limit` defaults to the live-read
`sessionmanagement.max_listed_sessions` (default 100), `limit < 1` →
`ValueError`, and the result is truncated to `limit` (REQ-007, EDGE-009).
Ordering is `created_at` descending (newest first), with the current session
(token path) pinned first (REQ-006, INV-005).

## Consequences
- One method covers self-service and admin listing; the token path resolves
  the user and the current session via `session_info(token)` (REQ-002).
- Bounded output with no offset keeps the "devices" view simple; the default
  100 covers users with many pre-feature sessions (AC-011).
- Deterministic ordering (created_at descending + pinning) makes tests and
  UI stable (AC-009, AC-010; INV-005).
- The limit is live-read, so a registry change takes effect on the next call
  (REQ-019, AC-040).

## Alternatives Considered
- limit/offset pagination like file-management — rejected: the list is a
  bounded "devices" view, not a data-browsing view; offset adds a
  page-navigation surface the feature does not need, and a single `limit`
  with a live default suffices (Q-50).
- No current-session pinning (pure created_at descending) — rejected:
  identifying the caller's own session ("this device" label, self-lockout
  awareness) requires the pin; the `is_current` flag alone does not place it
  deterministically first (Q-51).

## References
- `docs/specs/session-management.md` (REQ-001, REQ-006, REQ-007, REQ-019;
  INV-005; AC-009, AC-010, AC-011, AC-012, AC-013; EDGE-008, EDGE-009)
- `AI_Questions.md` (Q-42, Q-50, Q-51)
