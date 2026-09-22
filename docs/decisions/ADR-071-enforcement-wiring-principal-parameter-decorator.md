# ADR-071: Enforcement wiring via trailing `principal` parameter + decorator (standalone mode)

## Status
Accepted

## Context
The six existing features' public service methods do not currently take a
principal parameter, and the change must enforce `require_permission` at each
entry point (Q-75). The existing methods are a backward-compatibility
contract, and the approved change permits breaking changes only as enumerated
in Section 13, with every break fixed within this change's scope (Q-97). The
principal (user_id + session token) must reach the enforced method so the
check can evaluate it, including session validation (Q-73, Q-82).

## Decision
Every enforced public service method of the six features (53 methods) takes a
trailing `principal: Principal = Principal()` parameter and is decorated with
`@requires_permission("<feature>.<method>")` (D13, REQ-024). The decorator
resolves the wrapped method's `principal` parameter (default `Principal()` =
the system principal) and calls
`self._permission_service.require_permission(principal.user_id,
permission_key, session_token=principal.session_token)` — a no-op when
`self._permission_service is None` (standalone mode, no enforcement) — before
invoking the wrapped method. Each service constructor gains an optional
`permission_service: PermissionChecker | None = None` (default `None` →
standalone). The exempt set (authentication's session-establishment/teardown/
introspection operations: `login`, `session_info`, `logout`,
`request_password_reset`, `complete_password_reset`, `begin_passkey_login`,
`complete_passkey_login`) is declared in the catalog but not enforced.

## Consequences
- The trailing parameter with a default keeps existing positional call sites
  unaffected; an enforced method called without an explicit principal is
  evaluated as the system principal (EDGE-022).
- Enforcement is active only when a checker is injected; standalone mode
  (no checker) is today's behavior — additive, no existing construction
  breaks (AC-031, breaking change #7).
- The principal (user_id + session token) reaches the check, so session
  validation is part of the check (REQ-017, Q-73, Q-82).
- The exempt set stays reachable for zero-permission users (login, password
  reset) — internal calls are evaluated against the bootstrap system set
  (AC-030, EDGE-023).

## Alternatives Considered
- A required (no-default) `principal` parameter — rejected: every existing
  positional call site would break, a break not enumerated in Section 13;
  the trailing default (system principal) keeps call sites working (Q-97).
- Passing the principal as a separate leading argument — rejected: a leading
  argument shifts all existing positional arguments and breaks call sites;
  trailing is the least-invasive position.
- Enforcing inside the method body (explicit `require_permission` call)
  instead of a decorator — rejected: 53 hand-written calls would be
  inconsistent and easy to forget; the decorator is the single, uniform
  enforcement point (D13).
- Enforcing the exempt set too — rejected: login/password-reset must remain
  reachable for zero-permission users (session establishment/teardown);
  enforcing them would lock everyone out (AC-030, EDGE-023).

## References
- `docs/specs/user-roles-permissions.md` (D13, REQ-024, REQ-025; §3 enforced
  methods table; §13 #6, #7)
- `docs/decisions/ADR-070-shared-enforcement-plumbing-no-circular-imports.md`
- `AI_Questions.md` (Q-73, Q-75, Q-82, Q-97)
