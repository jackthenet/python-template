# ADR-080: Additive `SessionRepository.list_all()` in authentication

## Status
Accepted

## Context
The session search source (`build_session_source`) must query all sessions —
including revoked and expired, with no user filter — to expose sessions as a
search source (REQ-022). The existing `SessionRepository` API only exposes
`list_for_user` (per-user, bounded) and session-validation lookups; there is no
complete listing. The authentication feature's public API (including the
repository ABCs) is a backward-compatibility contract (authentication NFR-003),
and the repository already carries an additive-extension precedent: the
`SessionRepository` ABC was extended additively with `get`, `list_for_user`,
`revoke_user_sessions`, and an optional `limit` on `delete_expired`
(session-management REQ-017).

## Decision
Add one additive `SessionRepository.list_all() -> Sequence[Session]` ABC method
(all sessions, including revoked and expired, no user filter; the
`SqliteSessionRepository` implementation returns the existing rows in
`created_at` descending order, consistent with `list_for_user`). No change to
`AuthService` or any existing operation; custom repository implementations gain
a new method (documented in the module docstring). Backward-compatible per
authentication NFR-003 (additive-only evolution; precedent: session-management
REQ-017).

## Consequences
- The session source queries the existing repository without new persistence
  and without new behavior in authentication's operations (impact analysis
  §12.4–§12.5).
- The ABC extension is additive: existing implementors and call sites remain
  valid (authentication NFR-003; session-management REQ-017 precedent).
- Custom repository implementations must implement the new method — documented
  in the module docstring (the one break for out-of-tree implementors).
- The session source's default ordering (`created_at` descending) matches the
  implementation's row order (REQ-022).

## Alternatives Considered
- A new session-listing repository in the search feature — rejected: it would
  duplicate authentication's session storage; the data is owned by
  authentication (ADR-025 feature-boundary reasoning).
- Composing `list_for_user` over all users — rejected: it would require
  enumerating users and one query per user; a single `list_all` is simpler and
  returns the existing rows in one pass.
- A search-specific session table — rejected: a second session store is
  explicitly excluded (session-management spec: "no second session store");
  the data must stay coherent with authentication's sessions.

## References
- `docs/specs/search.md` (D19; REQ-022; §12.4, §12.5)
- `docs/specs/authentication.md` (NFR-003)
- `docs/specs/session-management.md` (REQ-017 — additive ABC extension
  precedent)
