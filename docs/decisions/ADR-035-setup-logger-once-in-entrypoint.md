# ADR-035: Call setup_logger exactly once in the entrypoint

## Status
Accepted

## Context
The logging-coverage spec (REQ-011) requires the entrypoint (`src/main.py`) to
call `setup_logger(Settings(...))` exactly once at startup, before any feature
code runs, and a second call to be a no-op.

Currently `src/main.py` is empty (0 bytes), so `setup_logger` is never called and
the logging feature's sink configuration is never applied. The design question is
where and how often `setup_logger` is called so that all traced calls and log
statements flow through the configured sinks.

## Decision
The entrypoint calls `setup_logger(Settings(...))` **exactly once** at startup,
before any feature code runs:
- `setup_logger` configures loguru's sinks (console + rotating file) and the
  stdlib interception; calling it once makes all subsequent `@logged`/
  `@logged_class` calls and direct loguru statements flow through those sinks.
- The call is idempotent and thread-safe (a second call is a no-op), so the
  "exactly once" requirement is a wiring convention, not a correctness risk.
- The `Settings` instance sets `log_level` (and the other logging settings).

## Consequences
- All features share a single, consistently configured logging sink.
- The entrypoint is the single source of sink configuration; features do not
  call `setup_logger` themselves.
- If `setup_logger` is never called, traced calls still work but flow through
  loguru's default sinks (not the configured ones) — hence the entrypoint wiring
  is required (REQ-011 / AC-011).

## Alternatives Considered
- Calling `setup_logger` in each feature — rejected: duplicates sink
  configuration and risks inconsistent sinks across features; the entrypoint is
  the natural single point.
- Making `setup_logger` required at import time (module-level call) — rejected:
  import-time side effects are fragile and make the logging feature harder to
  import without wiring; an explicit entrypoint call is clearer.

## References
- `docs/specs/logging-coverage.md` (REQ-011, AC-011, EDGE-005, §3.3)
- `docs/specs/logging.md` (`setup_logger` idempotency/thread-safety)
- `AGENTS.md` — Using the Logging Feature (Set it up once at startup)
