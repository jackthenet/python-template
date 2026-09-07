# ADR-023: Two-tier validation — schema-level Pydantic vs. service-level domain errors

## Status
Accepted

## Context
Input validation has two distinct natures: field-format validation (username
pattern, password rules, email format, URL scheme) is data-shape checking,
while domain rules (role membership, uniqueness, last-admin protection,
unknown ids) depend on service state and the store. Mixing the two in one
error type would blur the contract between "malformed input" and "forbidden
by domain rules" (D7, REQ-014).

## Decision
Field-format validation lives in the Pydantic models (`UserCreate`,
`UserUpdate`) and raises `pydantic.ValidationError` at model construction.
Domain rules live in `UserManager` and raise the exception hierarchy rooted
at `UserManagerError` (`UserAlreadyExistsError`, `UserNotFoundError`,
`InvalidRoleError`, `LastAdminError`). The service reuses the password rules
for `change_password` by validating through the same Pydantic rules, so weak
passwords raise `pydantic.ValidationError` there too (AC-013).

## Consequences
- Callers can distinguish malformed input (fix the payload) from domain
  rejections (change the operation) by exception type.
- The public error contract is stable: `pydantic.ValidationError` for
  format, `UserManagerError` hierarchy for domain (AC-029).
- Password rules are defined once (Pydantic) and shared by `create_user` and
  `change_password`, so the two cannot drift.

## Alternatives Considered
- A single `UserManagerError` for all failures — rejected: loses the
  malformed-input vs. domain-rejection distinction the spec's ACs rely on
  (AC-004…AC-007 expect `pydantic.ValidationError`).
- Mapping `pydantic.ValidationError` to a service exception — rejected: the
  spec's acceptance criteria explicitly expect `pydantic.ValidationError` for
  schema-level failures.
- Service-side re-validation of field formats — rejected: duplicates the
  model rules and risks drift.

## References
- `docs/specs/user-management.md` (REQ-002, REQ-014; D7; AC-004…AC-007, AC-013, AC-029)
