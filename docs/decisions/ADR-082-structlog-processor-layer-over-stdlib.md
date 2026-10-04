# ADR-082: structlog as the processor/renderer layer over standard-library logging

## Status
Accepted (supersedes ADR-002)

## Context
The shared logging feature is built on a single third-party backend (ADR-002: loguru). Three facts make that record untenable:

1. **The repository's own guidance contradicts its code.** `.agents/skills/python-best-practices/SKILL.md:16`, `references/modern-python.md:85` and `references/errors-and-resources.md:17,43` tell the reader to use "the project logger (structlog)" and show `structlog.get_logger()`, while the code uses loguru. That text entered the repository as third-party skill boilerplate in `chore(track-python-skill)` (commit `c2342b6`) — it was never a decision. The contradiction has to be resolved in one direction or the other.
2. **ADR-002's rejection of structlog rests on a false premise.** It rejects structlog because "it adds a second dependency and its output format does not match the spec's console/file sink requirements". structlog is not a logging backend: it is a processor/renderer and key/value-binding layer that sits **on top of** the standard library's `logging` handlers and adds no second backend. ADR-002 also cites NFR-002 as the constraining budget, but NFR-002 is the `@logged` decorator overhead budget, not a dependency constraint; the real dependency constraint is the Overview Dependencies row of `docs/specs/logging.md`, which merely restated the decision.
3. **The sinks are invisible to the rest of the ecosystem.** Because the sinks live inside the backend, third-party records have to be re-emitted through a custom intercept handler that recomputes call-frame depth to recover the caller's file and line (the reason `logging.md` AC-005 and EDGE-005 exist, and the reason the frozen-importlib-frame rule exists at all). Standard-library handlers are the interface every other library, tool and test already speaks.

The user chose the full swap over the two-line documentation fix (Q-01 = B), accepting the cost knowingly: the value triage scored the swap 3/5 and the decision is a willingness-to-pay call, not a value-score reversal.

Measured baseline for the budgets below (`docs/verification/structlog-logging.md`, Windows 11 / Python 3.14.5 / 32 CPU, 2026-10-04): the removed backend measured **5.18 ms** median `setup_logger()` (n = 5 fresh processes) and **0.156 ms/call** traced overhead with sinks active at DEBUG (**0.023 ms/call** with tracing disabled). The candidate pipeline measured **0.85 ms** median setup (n = 5) and **0.148 ms/call** traced overhead with sinks active at DEBUG (**0.006 ms/call** machinery-only).

## Decision
Replace the third-party logging backend with **structlog used as a processor/renderer and binding layer over standard-library `logging` handlers**, and remove the backend from the dependency set:

- **Handler ownership.** A dedicated, non-propagating logger owns exactly two handlers: a console stream handler on standard error (colorized text) and a rotating file handler (UTF-8, JSON records serialized with `orjson`, `maxBytes = log_max_bytes`, `backupCount = log_backup_count`, `encoding = "utf-8"`). The feature never touches handlers, levels or loggers it does not own.
- **Interception by forwarding.** One forwarding handler on the root logger passes foreign records to the two managed handlers. The record keeps its own level, logger name and location, so no call-depth arithmetic is needed and the importlib-bootstrap rule disappears (`logging.md` AC-005, EDGE-005 deleted).
- **Rendering.** Console: human-readable colorized text. File: JSON objects. `setup_logger(renderer=...)` selects the pair; the default is text console + JSON file. The spec fixes record **fields**, never a format string.
- **Asynchronous file writes.** `QueueHandler` + `QueueListener` replace the backend's `enqueue`; exactly one listener thread (NFR-005).
- **One statement entry point.** A new `get_logger()` export is the only way feature code obtains a logger; the 39 direct backend statements in `settings/registry.py` (17), `settings/repository.py` (11), `eventbus/eventbus.py` (10) and `permissions/service.py` (1) migrate to it. The "direct backend statements are kept" policy (`logging-coverage.md` REQ-010/AC-010) is retired.
- **Breaking surface, no shim.** `context_getter` and `depth` are removed from `@logged` (they existed to serve the removed backend's frame arithmetic), `renderer` is added to `setup_logger()`, `get_logger()` is added. Version bump: **major** (Q-22).
- **Secrets.** Exception records carry type, message and traceback frames only — never local variable values (`diagnose=False` policy restated as `logging.md` NFR-003 and proven by a Hypothesis property test).

This ADR **supersedes ADR-002**. It also **absorbs the incidental loguru wording** of ADR-035 (`:19`, `:21`, `:31`) and ADR-060 (`:37`): both decisions stand unchanged — `setup_logger()` is still called exactly once in the entrypoint, idempotent and thread-safe, and `@logged_class` is still the default tracing policy — only their naming of the backend is stale. Those two ADR files are deliberately **not edited** (fewest files; the wording is superseded by this ADR, which is the current record of the pipeline).

## Consequences
- **Positive:** the sinks are ordinary standard-library handlers any tool, library or test can attach to; structured records are available for the machine-driven surface `api-keys` would create and for later log aggregation (no consumer exists today and none is claimed); setup is ~6× cheaper (0.85 ms vs 5.18 ms); the frame-arithmetic class of bugs disappears; the published guidance becomes true of the code; `orjson` stops being an unused dependency and its `DEP002` suppression in `pyproject.toml` is retired.
- **Costs / risks:** the whole logging feature (606 LOC, `_decorator.py` 231, `_setup.py` 177, `feature_settings.py` 111, `_settings.py` 64, `__init__.py` 23) is rewritten rather than adapted, so **behavior drift in the tracing contract is the main risk** — mitigated by re-deriving tests from the amended IDs (RED against the old code) before implementing. 17 test files (2 390 LOC, 75 test functions, 43 backend references) and three test-helper modules are re-derived or adapted. The public API change is breaking (major bump). A third party that calls `logging.config.fileConfig` (alembic's `migrations/env.py`) removes the forwarding handler and disables pre-existing non-root loggers; the managed handlers survive and interception is re-established at the next reconfigure (`structlog-logging.md` EDGE-003), and the autouse `tests/conftest.py::_stdlib_root_logging_restored` fixture stays as the test-suite guard.
- **Sequencing:** the amendment PR (4 specs + this ADR + ADR-002 status) merges first; the implementation PR follows. This lands after `pyproject-tooling-gaps` (which owns `[tool.deptry]`) and before `api-keys` and `notifications` implement; it clears `tenacity-rich-cachetools`'s dependency on this decision.
- **Numbering:** ADR-081 is left unclaimed on disk for the `api-keys` change, which pre-announced it (`docs/todo/api-keys.md:64`); this ADR takes the next free number, 082.

## Alternatives Considered
- **Documentation-only fix (2-line DOCS/CHORE correcting the skill text to name loguru)** — rejected by the user (Q-01 = B) despite being the smaller change; the contradiction would persist in the code's shape (backend-owned sinks, frame arithmetic) rather than in the wording.
- **Standard library only (`logging` `Formatter` + `extra`), no structlog** — rejected (Q-03): it delivers the handler ownership and interception simplicity but requires hand-written key/value binding, hand-written colorized and JSON formatters, and hand-written exception-frame rendering without locals; structlog's processors are exactly those pieces, maintained, and already the shape the repository's guidance describes.
- **structlog on top of the existing backend** — rejected (Q-03): two logging stacks, and the sinks still would not be standard-library handlers, so the ecosystem-visibility problem and the frame arithmetic stay.
- **Keep the backend and add a structlog façade for statements only** — rejected: it satisfies the guidance text but leaves the API surface split across two mechanisms and keeps the deleted AC-005/EDGE-005 machinery.

## Compliance
- `docs/specs/structlog-logging.md` (new, CROSS-CUTTING) — REQ-001…REQ-015, AC-001…AC-020, INV-001…INV-005, EDGE-001…EDGE-006, NFR-001…NFR-005.
- Amended: `docs/specs/logging.md` v3 (REQ-001, REQ-003, REQ-005, AC-001, AC-004, AC-005 deleted, INV-001, EDGE-005 deleted, NFR-001, NFR-002, NFR-003), `docs/specs/logging-coverage.md` v2 (REQ-010, AC-010), `docs/specs/settings-coverage.md` v2 (REQ-014/015/016, AC-019/020/021, EDGE-008), `docs/specs/settings.md` v4 (wording only).
- `docs/specs/event-bus.md` names no backend and is **not** amended.

## References
- Supersedes: `docs/decisions/ADR-002-loguru-logging-backend.md`.
- Absorbs wording of: ADR-035 (entrypoint wiring — decision unchanged), ADR-060 (tracing policy — decision unchanged).
- Measurement record: `docs/verification/structlog-logging.md` (§ NFR re-measurement).
- structlog documentation: https://www.structlog.org/ (processors, `ProcessorFormatter`, stdlib integration).
