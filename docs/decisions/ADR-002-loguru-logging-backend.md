# ADR-002: Loguru as the Logging Backend

## Status
Accepted

## Context
The logging feature needs a logging backend that supports: console sink with colorization and backtrace, rotating file sink with UTF-8 encoding and enqueue, stdlib logging interception, and decorator-based tracing. The spec (NFR-002) constrains the feature to depend only on loguru and the standard library.

## Decision
The logging feature uses loguru as its sole third-party dependency. All sinks (console, rotating file) are configured through loguru's `logger.add()` API. Stdlib logging records are routed to loguru via a custom `_InterceptHandler` that subclasses `logging.Handler`.

## Consequences
- Single dependency keeps the feature lightweight and auditable.
- Loguru's built-in backtrace and colorize support eliminates the need for custom formatters.
- The intercept handler must carefully compute call-frame depth to preserve the original logger's file/line information.
- Async functions are not natively traced by the `@logged` decorator; async support would require a separate wrapper (not in current spec scope).

## Alternatives Considered
- Standard library `logging` only — rejected because it lacks built-in colorization, backtrace, and rotating file sinks with enqueue; achieving equivalent behavior would require significant custom code.
- structlog — rejected because it adds a second dependency and its output format does not match the spec's console/file sink requirements.
- Python logging with rich handler — rejected because rich is a heavier dependency and the spec constrains dependencies to loguru and stdlib.

## References
- `docs/specs/logging.md` (NFR-002, REQ-001, REQ-003)
- Loguru documentation: https://loguru.readthedocs.io/
