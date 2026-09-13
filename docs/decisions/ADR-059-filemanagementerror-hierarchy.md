# ADR-059: FileManagementError exception hierarchy with context attributes

## Status
Accepted

## Context
Callers need structured, debuggable errors that distinguish the failure
kinds: not found, too large, type not allowed, validation failure, storage
failure, avatar error (REQ-023). A single error type with a code, or bare
exceptions, would force callers to parse messages. The repository already
uses per-feature exception hierarchies with secret-free context
(user-management, mail service ADR-045).

## Decision
Define a `FileManagementError` root exception with six subclasses —
`FileManagementNotFoundError`, `FileTooLargeError`,
`FileTypeNotAllowedError`, `FileValidationError`, `StorageError`,
`AvatarError` — each carrying documented **context attributes** (key; actual
`size` vs. `limit`; `detected` vs. `allowed`; `reason`; `user_id`/
`operation`). A validation failure (upload rejected by size, type, key,
namespace, source, or image validation) publishes `FileValidationFailed`
and raises the corresponding domain error. Error messages carry no file
content (only error kind, key, size, MIME type, dimensions), so they are
safe to log.

## Consequences
- Structured error handling: callers can catch by kind (e.g. only
  `FileTooLargeError`) and read the context without parsing.
- Context attributes make logs and debugging precise (actual vs. limit,
  detected vs. allowed).
- Error messages are secret-free (NFR-002); file content never appears.
- The `FileValidationFailed` event plus the domain error give both an
  async signal and a synchronous one for the same failure.

## Alternatives Considered
- A single error type with a string code — rejected: less Pythonic, harder
  to catch by kind, no typed context.
- Returning error tuples — rejected: not Pythonic; forces every call site
  to check.
- Bare `Exception` — rejected: unstructured; callers cannot distinguish
  failure kinds.

## References
- `docs/specs/file-management.md` (REQ-023, D11)
- `docs/decisions/ADR-045-mailerror-hierarchy-secret-free-reasons.md`
