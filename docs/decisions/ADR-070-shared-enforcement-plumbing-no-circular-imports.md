# ADR-070: Shared enforcement plumbing in `backend/shared` (no circular imports)

## Status
Accepted

## Context
The six existing features must enforce permission checks at their entry
points, but none of them may import `backend.permissions` directly:
user-management delegates role assignment to the permission service, and the
permission service depends on the `UserManager` — a direct
user-management ↔ permissions import cycle would result. The enforcement
mechanism (the principal model, the check seam, and the decorator) is
generic authorization plumbing with no feature-specific business logic, and
the repository rule is that `shared/` is deliberately small and holds only
genuinely shared, feature-neutral code.

## Decision
Place the enforcement plumbing in `src/backend/shared/principal.py`: the
`Principal` model (`user_id: UUID | None`, `session_token: str | None`;
`Principal()` = the system principal), the structural `PermissionChecker`
protocol (`require_permission` / `has_permission`), and the
`requires_permission(permission_key)` decorator (D14, REQ-025). The six
features depend only on `backend.shared` (and on the injected
`PermissionChecker`), never on `backend.permissions`. The permission service
satisfies the `PermissionChecker` protocol and is wired in at the
composition root. The new `src/backend/shared/` package is additive
(breaking change #8); no existing imports change.

## Consequences
- No circular imports: the six features resolve checks through the structural
  `PermissionChecker` protocol; the user-management ↔ permissions cycle is
  avoided (D14).
- `shared/` stays deliberately small — one module of generic authorization
  plumbing, no feature-specific business logic (repository `shared/` rule).
- The six features never import `backend.permissions`; they can be
  constructed standalone (no checker) and enforce nothing (AC-031).
- The decorator is the single enforcement point; the check itself lives in
  the permission service (separation of wiring and decision).

## Alternatives Considered
- Placing `Principal` / `PermissionChecker` / `requires_permission` in
  `backend.permissions` — rejected: the six features would import
  `backend.permissions`, and user-management (which the permission service
  depends on for role assignment) would create an import cycle (D14).
- Placing the plumbing in `backend.usermanagement` (the account store) —
  rejected: authorization is not account management; the other five features
  would depend on user-management for a generic check seam, coupling
  unrelated concerns (the ADR-061 store-reuse-vs-new-feature reasoning).
- A per-feature check helper (each feature implements its own) — rejected:
  six copies of the same principal/decorator logic would drift; a single
  shared module keeps the mechanism consistent.

## References
- `docs/specs/user-roles-permissions.md` (D14, REQ-025; §3 package layout;
  §13 #8)
- `docs/specs/session-management.md` (constructor DI pattern)
- `docs/decisions/ADR-061-session-store-reuse-constructor-di.md`
- `AI_Questions.md` (Q-73, Q-75)
