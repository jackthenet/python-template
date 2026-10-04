# Verification Record: structlog-logging

**Change type:** CROSS-CUTTING (Phase 0 / P.1 classification, first matching criterion #3: the change intentionally spans two or more features — it changes shared infrastructure (the logging feature's record pipeline) and, in the same change, the log-statement policy of `settings`, `eventbus` and `permissions`, plus the guidance records that publish the current policy.)

**Phase P status:** prepared at P.4 (draft spec + amendments + superseding ADR + re-measured NFR budgets). P.5 (self-consistency + dependency smoke-test) has not run.

**Branch / worktree:** `crosscut/structlog-logging` at `python-template_kopie-worktrees/crosscut/structlog-logging`, created from `main` at commit `869d309d569ff6df97cf5cc04803eaf45e924ec1` ("chore(update-readme): status WAITING (PR #66 open) + Phase 6 recorded").

**Normative basis:** `docs/specs/structlog-logging.md` (new, v1) + the amendment PR touching `docs/specs/logging.md` (v3), `docs/specs/logging-coverage.md` (v2), `docs/specs/settings-coverage.md` (v2), `docs/specs/settings.md` (v4) + `docs/decisions/ADR-082-structlog-processor-layer-over-stdlib.md` (supersedes ADR-002).

---

## P.4 — What was produced

| Artifact | File | State |
|---|---|---|
| Draft spec (CROSS-CUTTING, with Impact Analysis) | `docs/specs/structlog-logging.md` | v1 draft, 15 REQ / 20 AC / 5 INV / 6 EDGE / 5 NFR |
| Amendment — logging | `docs/specs/logging.md` | v3: REQ-001, REQ-003, REQ-005, AC-001, AC-004 restated; AC-005, EDGE-005 deleted; INV-001, NFR-001, NFR-002, NFR-003 restated/re-budgeted; Goal, Dependencies, Architecture rows reworded |
| Amendment — logging coverage | `docs/specs/logging-coverage.md` | v2: REQ-010/AC-010 restated (statements kept, but through the feature's exported logger); Goal, Dependencies, Architecture rows reworded |
| Amendment — settings coverage | `docs/specs/settings-coverage.md` | v2: REQ-014/015/016, AC-019/020/021, EDGE-008 restated; Dependencies row no longer names a backend |
| Amendment — settings | `docs/specs/settings.md` | v4: wording only (Scope, Dependencies, observability wording) — no ID change |
| Superseding ADR | `docs/decisions/ADR-082-structlog-processor-layer-over-stdlib.md` | new; answers ADR-002's recorded reasoning point by point |
| Superseded ADR | `docs/decisions/ADR-002-loguru-logging-backend.md` | Status line → "Superseded by ADR-082"; Context/Decision/Alternatives left intact as the historical record |
| Traceability | `docs/verification/traceability.md` | new § *Structlog Logging Matrix*: 15 REQ + 20 AC rows, all `PENDING` (Phase 3 replaces them with the derived tests + RED, Phase 5 with GREEN) |

**ADR-035 and ADR-060 were deliberately not edited** (Q-16 = (A): one new ADR absorbs their loguru wording). Their normative content is unchanged by this change: `setup_logger()` stays called exactly once in `src/main.py` before feature code, idempotent and thread-safe (ADR-035), and the tracing policy — `@logged_class(slow_threshold_ms=…, include_args=False)` on public service classes, `@logged` on public module-level functions — is unchanged (ADR-060). Both are cited as constraints in the new spec (§2 Constraints, REQ-012).

## ADR numbering

The new ADR is **ADR-082**, not ADR-081. `docs/decisions/` on `main` tops out at ADR-080, so ADR-081 is free on disk, but the `api-keys` change pre-announced ADR-081+ for its per-domain key stores (`docs/todo/api-keys.md:64`, "New ADRs (next free number)"). Taking 081 here would force `api-keys` to renumber. The gap is recorded here so it is not read as an error. If another change claims 082 before this PR merges, the number is reassigned at merge order and ADR-002's Status line, the new spec's §2/§4 references and this record are updated in the same commit.

## NFR budgets — re-measured before the amendment

Precedent: `docs/verification/amend-nfr-001-budgets.md` (measure first, amend second, record the context). The budgets are executable gates in `tests/contract/logging/test_logging_contracts.py` (`test_nfr_001_setup_time_budget`, `test_nfr_002_decorator_overhead_budget`).

**Measurement context.** Windows 11 (build 26200), Python 3.14.5, 32 CPUs. Throwaway benchmark outside the repository (`C:/Users/domin/AppData/Local/Temp/nfr_bench_structlog.py`, not committed); it mirrors the two gates: NFR-001 times `setup_logger()` in **5 fresh processes** and takes the median; NFR-002 times 20 000 calls of a bare function against the same function wrapped in `@logged`, median of 3 samples. The candidate pipeline was measured with `uv run --with structlog` (structlog is **not** added to the project at P.4 — no `pyproject.toml`/`uv.lock` change; the dependency smoke-test is P.5's job).

| Quantity | Current backend (loguru) | Candidate pipeline | New budget |
|---|---|---|---|
| NFR-001 `setup_logger()` | 5.18 ms median (n=5 fresh processes) | **0.85 ms median** (min 0.84, max 0.87, n=5) — console handler + queue handler + rotating file handler + root forwarding handler, listener started | **< 25 ms** |
| NFR-002 `@logged` overhead, sinks **disabled** | 0.023 ms/call | 0.006 ms/call (tracing machinery only, no handler attached) | — (not the specified context) |
| NFR-002 `@logged` overhead, sinks **active at DEBUG** | 0.156 ms/call | **0.148 ms/call** (console + queue + rotating file at DEBUG) | **< 1 ms/call** |

**Budget reasoning.**
- *NFR-001 < 25 ms.* The old 50 ms budget was set after CI observed 15.55 ms against a 10 ms spec (`docs/specs/logging.md` changelog v2), i.e. CI ran ~3× slower than the local machine. The candidate pipeline measures 0.85 ms locally, so 25 ms leaves ~10× headroom over the local figure and ~30× over the CI-scaled figure — a tightening from 50 ms that still cannot plausibly fail on CI. It is deliberately not tighter: the pipeline installs four handlers and starts a listener thread, and a budget that only the fastest possible implementation meets is a trap for the next change.
- *NFR-002 < 1 ms/call, measured with the sinks active.* The old budget (0.5 ms) was measured with logging **disabled** (`logger.disable("DEBUG")`), which is not the context the feature runs in: `docs/specs/logging-coverage.md`'s observability table requires every traced call to emit entry and exit records, so a budget for the decorator must be achievable *with the records being written*. The new gate therefore forbids disabling the pipeline and measures with both managed sinks at DEBUG. 0.148 ms measured against a 1 ms budget is ~6.7× headroom; the queue handler is what keeps the file sink out of the measurement (REQ-010), which is also why the number is not dominated by disk I/O.
- Both budgets are restated in `docs/specs/logging.md` v3 (NFR-001, NFR-002) and carried into the new spec (§8).

## Design decisions taken at P.4 (recorded because they bind Phase 2–4)

1. **Sink ownership (Q-07).** A dedicated, non-propagating logger owns the two handlers instead of the root logger. This is what makes alembic's `logging.config.fileConfig` call in `migrations/env.py` harmless (new EDGE-003) and keeps foreign handlers untouched (INV-004). `migrations/env.py` is **not** modified — it is not in this change's file set, and the fix is in the logging feature, not in the migration runner.
2. **Interception by forwarding (Q-08).** One handler on the stdlib root logger forwards foreign records to the two managed handlers. Level, logger name and originating file/line survive with no call-depth arithmetic, which is why `logging.md` AC-005 (importlib bootstrap frame) and EDGE-005 (non-standard numeric level) can be deleted rather than re-derived; the unknown-level case survives as this spec's EDGE-004.
3. **Async tracing is a behavior expansion (Q-23).** `docs/decisions/ADR-002` recorded "async functions are NOT natively traced by `@logged`"; the new spec requires it (REQ-007, AC-011). The existing test `tests/unit/logging/test_logging.py::test_ac_007_logged_async_entry_exit` already asserts it, so the code is ahead of ADR-002's wording; the ADR correction is part of the amendment.
4. **Secret policy is non-negotiable (Q-09).** REQ-009 + INV-002 + NFR-003 (restated) + AC-015: no record may contain local variable values; the property test holds a secret local in a raising function and asserts the value never reaches the file sink. `include_args=False` semantics stay byte-identical.
5. **Structured output claims no present consumer (Q-02).** The spec's Overview states the boundary explicitly: `src/frontend/` is empty, there is no HTTP layer, nothing in `src/` parses log output; JSON records are future-proofing for the machine-driven surface `api-keys` would create and for later aggregation.
6. **Statement migration count (Q-05).** 39 direct `logger.*` calls in the four feature files — `settings/registry.py` 17, `settings/repository.py` 11, `eventbus/eventbus.py` 10, `permissions/service.py` 1 — plus 2 inside the logging feature's own `feature_settings.py`. REQ-005 names the four feature files; the logging feature's own module is migrated as part of REQ-001 (no backend import under `src/`).
7. **orjson.** Already declared and unused (`pyproject.toml:14`) with a `DEP002` suppression at `pyproject.toml:115-119`. This change makes it used and retires the suppression (REQ-013, AC-018). It does **not** touch `[tool.deptry]`'s other entries — `pyproject-tooling-gaps` owns that table and merges first (Q-21).

## Test re-derivation protocol (Q-18, Q-25)

1. The amendment PR merges first. Tests are then re-derived from the amended IDs — they are RED against the current (loguru) code — then the implementation lands, then GREEN.
2. Deletions are authorized **per amended-away ID only**, and each must be named here when it happens. The tests this change authorizes for deletion (their IDs are amended away or deleted):
   - `tests/acceptance/logging_coverage/test_direct_loguru_kept.py::test_existing_direct_loguru_kept` — sole enforcer of the retired `logging-coverage.md` REQ-010/AC-010 wording.
   - `tests/unit/logging/test_logging.py::test_ac_005_intercept_handler_skips_bootstrap` — enforces the deleted `logging.md` AC-005 frame arithmetic.
   - `tests/unit/logging/test_logging_edges.py::test_edge_005_intercept_unknown_level` — enforces the deleted `logging.md` EDGE-005; the case is re-derived as this spec's EDGE-004.
   No other test may be deleted or weakened.
3. `tests/contract/logging/test_logging_contracts.py::test_nfr_004_backward_compatible_api` asserts that `logged` exposes `context_getter` and `depth`. That gate contradicts the breaking API redesign (Q-10) and is **amended**, not preserved — it must assert the reduced parameter set instead (AC-013).
4. `test_nfr_002_decorator_overhead_budget` uses the backend's `disable`/`enable` to measure the decorator with logging off. It is amended to measure with the managed sinks active (AC-018/NFR-002); the backend-specific disable/enable call disappears with the backend.
5. Test helpers may be adapted to the new backend provided every assertion traces to an amended ID: `tests/conftest.py`, `tests/logging_test_helpers.py`, `tests/logging_coverage_test_helpers.py`, `tests/settings_test_helpers.py`. Two helper capabilities have no stdlib equivalent and MUST be re-implemented, or nine cross-feature tests break: **fd-level console capture** (`_console_sink_fd()` walks the backend's internal handler table to reach the console stream's `fileno()` for the `dup2` swap used by `captured_stderr()`) and **queue drain** (`wait_for_file_content()` drains the enqueued file sink before polling). Affected beyond the logging feature's own tests: `tests/acceptance/authentication/test_logging.py`, `tests/acceptance/mail/test_logging.py`, `tests/contract/authentication/test_logging.py`, `tests/contract/mail/test_logging.py`, `tests/acceptance/settings_coverage/test_setup_logger.py`, `tests/acceptance/logging_coverage/test_sink_failure.py`, `tests/property/logging_coverage/test_invariants.py`, `tests/unit/logging_coverage/test_edge_cases.py`, `tests/unit/test_settings_coverage.py`.
6. The autouse `_stdlib_root_logging_restored` fixture in `tests/conftest.py` **stays** — it is what keeps alembic's `fileConfig` from leaking across tests, and it is backend-neutral.
7. Suite baseline for the re-derivation gates: 727 passed, 1 skipped (`docs/verification/traceability.md`). Blast radius measured at P.2: 7 source files reference the backend, the logging feature is 606 LOC, 17 test files hold 43 backend matches / 2390 LOC / 75 test functions.

## Sequencing constraints (Q-19, Q-20, Q-21, Q-22)

- **Two PRs.** Amendment PR (4 specs + ADR-082 + ADR-002 status + the new spec) merges **first**; one implementation PR after. The amendment is never smuggled into the code PR.
- This change lands **before** `api-keys` and `notifications` implement, and it clears `tenacity-rich-cachetools`'s `Depends on: decision on docs/todo/structlog-logging.md`.
- This change lands **after** `pyproject-tooling-gaps` (which owns `[tool.deptry]` and `quality_check`); `security-changelog-license` merges before `pyproject-tooling-gaps`. `python-3.15` is dropped; only the trigger-gated `python-3.15-upgrade` remains.
- Version bump: **major** (Q-22) — the decorator parameter set and the public export surface change (REQ-015).

## P.4 gate evidence

- `uv run python scripts/check_traceability.py` → `OK: traceability matrix is consistent.` (exit 0) after the spec edits and the new matrix rows.
- `uv run mkdocs build --strict` → builds with no warnings (the new spec and ADR are not in the site nav, matching the other `docs/specs/` and `docs/decisions/` records).
- No `src/` or `tests/` file was modified at P.4; `pyproject.toml` and `uv.lock` are unchanged (`uv run` re-synced `uv.lock`'s project version to 0.6.1 during the checks; that edit was reverted — `main`'s lockfile is stale against `pyproject.toml` and is not this change's concern).
- Spec ID self-consistency: every AC/INV/EDGE/NFR in `docs/specs/structlog-logging.md` has a row in its Test Strategy, and the amended approved IDs have rows naming the existing tests that will be re-derived.

## Not yet done (P.5 and later)

- **P.5** must run the Self-Consistency Checklist and the **Dependency Smoke-Test** for `structlog` (not installed today: `uv run python -c "import structlog"` → `ModuleNotFoundError`) and for `orjson` (installed, currently unused).
- Phase 1 S1.4: commit the prepared spec and open the **amendment PR** for human approval/merge.
- Phase 2: ADRs beyond ADR-082 are not expected (no new pattern beyond the ADR); the task DAG must group by affected feature (logging, settings, eventbus, permissions, tooling/guidance).
