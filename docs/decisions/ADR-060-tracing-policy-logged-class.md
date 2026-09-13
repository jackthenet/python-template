# ADR-060: Tracing policy (@logged_class, include_args=False, slow_threshold_ms=5000)

## Status
Accepted

## Context
The AGENTS.md observability policy requires public service classes to be
traced by default, and sensitive arguments (file content, paths) must never
be logged (REQ-025, NFR-002, NFR-005). The service methods take file
content (bytes/stream), paths, and user references as arguments — all of
which are sensitive. The 10 MB upload budget is < 2 s (NFR-001), so the
slow-call threshold must sit above the budget to avoid false positives.

## Decision
`FileService` is traced with
`@logged_class(slow_threshold_ms=5000, include_args=False)` from the shared
logging feature: every public method is traced with an entry line, an exit
line (elapsed ms), and an exception line on error; `include_args=False` so
arguments (file content, paths, user references) are never logged. The
module-level functions `register_settings` and `get_default_avatar` are
traced with `@logged` (`register_settings` with `slow_threshold_ms=5`,
consistent with the other features). File content never appears in any log
record; domain error messages are content-free, so exception lines are safe.

## Consequences
- Entry/exit/exception tracing with elapsed ms without hand-logging
  (consistent with the shared logging feature).
- `include_args=False` prevents content/paths from leaking into logs
  (NFR-002).
- `slow_threshold_ms=5000` sits above the 10 MB upload budget (2 s), so a
  budgeted upload is not flagged slow (consistent with the mail service).
- DEBUG tracing is off at INFO; domain errors are logged with type +
  message (no content).

## Alternatives Considered
- Manual `logger.info` entry/exit calls — rejected: duplicates the
  decorator's output; AGENTS.md reserves direct loguru for one-off
  statements.
- `include_args=True` — rejected: file content and paths would leak into
  log records (NFR-002).
- A lower slow threshold — rejected: a budgeted 10 MB upload (< 2 s) would
  be flagged slow, producing false positives.

## References
- `docs/specs/file-management.md` (REQ-025, NFR-001, NFR-002, NFR-005;
  section 9)
- `docs/decisions/ADR-033-slow-threshold-observability.md`
- `docs/decisions/ADR-034-include-args-false-for-secrets.md`
