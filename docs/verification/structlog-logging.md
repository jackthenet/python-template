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

## Not yet done (later phases)

- ~~Phase 1 S1.4: commit the prepared spec and open the **amendment PR** for human approval/merge.~~ **Done** — PR #67 merged as `eb68ed2` on 2026-10-04 (see *Phase 2 (S2.1) — Cached spec-approval result*).
- ~~Phase 2: ADRs beyond ADR-082 are not expected (no new pattern beyond the ADR)~~ — **confirmed at S2.1** (see *Phase 2 (S2.1) — ADR decision*). The task DAG must still group by affected feature (logging, settings, eventbus, permissions, tooling/guidance).

---

## Phase 2 (S2.1) — ADRs (2026-10-04)

### Cached spec-approval result (checked once, at S2.1 entry)

| Item | Value |
|---|---|
| Approved | **yes** — HUMAN APPROVED through the configured GitHub review process |
| Approval PR | **#67** (`crosscut/structlog-logging` → `main`) |
| Merge commit | `eb68ed2dfc4e9812d07fb36357cc9b3cfa67e66a` — "Merge pull request #67 from jackthenet/crosscut/structlog-logging" |
| Date | **2026-10-04** |
| Check (run once) | `git log main --oneline -- docs/specs/structlog-logging.md` → `3cd700e` (P.4 draft) and `098ca1a` (P.5 pass); both reach `main` **only through the merge commit** `eb68ed2`, i.e. a reviewed merge, not a direct push |
| Normative files carried by that merge | `docs/specs/structlog-logging.md` (new, v1), `docs/specs/logging.md` (v3), `docs/specs/logging-coverage.md` (v2), `docs/specs/settings-coverage.md` (v2), `docs/specs/settings.md` (v4), plus `docs/decisions/ADR-082-…` (new) and `docs/decisions/ADR-002-…` (status line only) |

This row **is** the cache: later phases and later step subagents read it and MUST NOT re-run `git log main -- …`.

### Branch sync at S2.1 entry

- `git fetch --prune`; the local branch was 23 commits behind `origin/crosscut/structlog-logging` → `git merge --ff-only origin/crosscut/structlog-logging` (fast-forward, no conflicts).
- `git merge main` → **fast-forward** to `main` at `0e4a1b7`; **no conflicts, nothing resolved**. The branch tip was already an ancestor of `main` (PR #67 merged it), so the merge only pulled in work that merged after the approval PR was opened.
- `pyproject-tooling-gaps` — this change's `Depends on:` — is now on the branch (PR **#68**, merge `a278bd2`). The content this change depends on: `[tool.deptry]` now carries `package_module_name_map` and `DEP001 = ["webauthn"]`, and `DEP002` still lists `orjson` (`pyproject.toml:112-124`); `quality_check` is at Phase 5 parity — `uv run ruff check . && uv run ruff format --check . && uv run mypy src/ && uv run deptry .` (`pyproject.toml:224`); docs tooling moved to a separate `docs` dependency group (`pyproject.toml:68-77`) with `default-groups = ["dev"]` (`pyproject.toml:80-82`).
- Post-sync state: `git merge-base --is-ancestor main HEAD` → true; the branch equalled `main` (`0e4a1b7`) before this S2.1 commit.

### ADR decision: **no new ADR — ADR-082 is this change's only ADR, and it is already merged on `main`**

The S2.1 threshold (new dependency / new pattern or architecture element / cross-feature interface) applied to every decision in the approved spec set:

| # | Candidate decision | Threshold trigger | Verdict |
|---|---|---|---|
| 1 | Replace the third-party logging backend with structlog as a processor/renderer layer over standard-library handlers (`structlog-logging.md` §2 Dependencies) | **new dependency** (`structlog` added, `loguru` removed, `orjson` becomes used) **and** new pattern | **ADR-082** — created at P.4, merged with the approval PR; nothing further to create |
| 2 | D1 handler ownership, D2 interception by forwarding, D3 renderer per sink, D4 queue handler + single listener, D7 exception rendered into a field / callsite at the emitting call site | the same new pattern element as #1 | Covered by ADR-082 § Decision + § "Verified pipeline constraints". Splitting one pipeline decision into five ADRs would fragment the record, not add to it |
| 3 | D5 — `get_logger()` as the single statement entry point; 39 direct backend statements in `settings`, `eventbus`, `permissions` migrate to it | **cross-feature interface** | Already recorded in ADR-082 § Decision ("One statement entry point"), and the logging feature already owned the logging interface — ADR-035 (entrypoint wiring) and ADR-060 (tracing policy) stand unchanged and are named as absorbed. No second interface decision |
| 4 | D6 — breaking surface, no shim (`context_getter`/`depth` removed, `renderer` added, `get_logger()` added, **major** bump) | consequence of #1/#3, no new pattern of its own | Recorded in ADR-082 § Decision, § Consequences and § Compliance (`logging.md` NFR-004 amended to the import path, not the parameter surface) |
| 5 | Re-implementing the two test-helper capabilities with no standard-library equivalent (fd-level console capture, queue drain) | none — test infrastructure only: no new dependency, no production pattern, no cross-feature interface | Skip (protocol already recorded under *Test re-derivation protocol*) |
| 6 | Retiring the `orjson` `DEP002` suppression and removing `loguru` from the dependency set | none — a tooling consequence of #1 | Skip; ADR-082 § Consequences already names it, and REQ-013/AC-018 make it executable |
| 7 | Settings-driven level/rotation and sink reconfigure on a settings change | none — pre-existing decision (ADR-035; `settings-coverage.md` REQ-015/AC-020), unchanged by this change | Skip |

**ADR numbering re-checked against merged `main`:** `docs/decisions/` still tops out at ADR-082 and **ADR-081 remains deliberately unclaimed** for `api-keys` (`docs/todo/api-keys.md:64`), so the numbering note above stands and no renumber is needed.

### ADR-082 sanity check against merged `main`

Every `pyproject.toml` statement ADR-082 makes was re-read against the post-`pyproject-tooling-gaps` state:

- "`orjson` stops being an unused dependency and its `DEP002` suppression in `pyproject.toml` is retired" — **still true as a plan**: `orjson` is in `dependencies` (`pyproject.toml:14`) and still listed in `DEP002` (`pyproject.toml:122`); the retirement is this change's REQ-013/AC-018 and has not happened yet.
- "This lands after `pyproject-tooling-gaps` (which owns `[tool.deptry]`)" — **now satisfied** (PR #68, merge `a278bd2`).
- **No statement in ADR-082 is factually false after the merge, so ADR-082 was not edited.**

Two facts the merged `main` adds that bind Phase 2–4 (recorded for S2.2; not ADR changes):

1. `quality_check` now runs `deptry` at Phase 5 parity, so REQ-013/AC-018 is a gate the task DAG must satisfy **inside** the task that changes the dependency set: dropping `loguru` from `dependencies` while `src/` still imports it is a deptry *missing-dependency* failure, and dropping `orjson` from `DEP002` only stays clean once `orjson` is actually imported in `src/`. The dependency-set change, the 39-statement migration and the `orjson` file renderer therefore cannot be spread across tasks in an order that leaves deptry failing in an intermediate state.
2. Docs tooling is now the `docs` dependency group with `default-groups = ["dev"]`, so the docs gate in a fresh worktree is `uv run --group docs mkdocs build --strict` (the plain form still worked here only because this worktree's venv already had mkdocs installed from before the group split).

### S2.1 gates

| Gate | Command | Result |
|---|---|---|
| Traceability | `uv run python scripts/check_traceability.py` | `Traceability: PASS (765 matrix rows, 129 spec IDs, 714 test functions)`, exit 0 |
| Docs | `uv run --group docs mkdocs build --strict` | exit 0, no warnings (only the Material-for-MkDocs 2.0 deprecation banner) |

S2.1 touched **no** `src/`, `tests/`, `pyproject.toml` or `uv.lock` file — docs-only, so ruff is n/a. `docs/todo/` and `docs/questions/` were not touched (orchestrator-owned on `main`).

## P.5 Self-consistency (2026-10-04)

Ran the specify skill's Self-Consistency Checklist and the Dependency Smoke-Test against the P.4 draft, and fixed the specification documents for every finding. Only spec / ADR / verification documents were changed — no `src/`, `tests/` or `pyproject.toml` file was touched.

### Checklist results

| Check | Result | Evidence |
|---|---|---|
| No duplicate ID | PASS | `REQ-001…015`, `AC-001…020`, `INV-001…005`, `EDGE-001…006`, `NFR-001…005` are each defined once in §4/§5/§6/§7/§8 (checked by script over the section tables; the repeats elsewhere are strategy and matrix references). |
| No ID referenced that is not defined | PASS | Every ID `structlog-logging.md` references resolves inside this spec or inside the amended spec that defines it; the deleted `logging.md` `AC-005`/`EDGE-005` are named only as deleted. |
| Every REQ has at least one AC | PASS (after F-P5-01) | All 15 REQs appear in the AC column of §5; REQ-011 was uncovered before the fix. |
| Every AC maps to at least one REQ | PASS | 20 AC rows, each with a REQ column. |
| Every INV/EDGE/NFR has a test-strategy row | PASS | §11 has a row for all 5 INV, 6 EDGE, 5 NFR and all 20 AC. |
| Test-strategy rows name tests that exist or are marked to be created | PASS | The §11 rows for new tests name files that do not exist yet — all are Phase 3 creations, stated as such in §11. Every row of the amended-ID table names a test that exists on disk (`tests/acceptance/logging/test_logging.py::test_ac_001_setup_logger_adds_sinks`, `tests/unit/logging/test_logging.py::test_ac_004_intercept_handler_routes_records`, `tests/contract/logging/test_logging_contracts.py::test_nfr_001_setup_time_budget` / `test_nfr_002_decorator_overhead_budget` / `test_nfr_004_backward_compatible_api`, `tests/property/logging/test_logging_properties.py::test_inv_001_concurrent_setup_logger_sinks`, `tests/acceptance/settings_coverage/test_setup_logger.py::test_setup_logger_reads_registry` / `test_sink_reconfigured_on_change`, `tests/unit/test_settings_coverage.py::test_logging_stub_removed` / `test_sink_reconfigured_rotation` / `test_observability_tracing`). The three authorized deletions are named and bounded. `scripts/check_traceability.py` enforces existence for matrix rows only, never for spec tables, so this was verified by hand. |
| Configurability — nothing hard-coded that should be configurable | PASS | Level, rotation size and backup count stay settings-driven (`log_level`, `log_max_bytes`, `log_backup_count`); `renderer` is a parameter, not a constant; unregistered keys keep their documented fallbacks. |
| Parameter coverage — every parameter in the spec is in the schema and vice versa | PASS | §2/§3 give `@logged` the parameters `level`, `slow_threshold_ms`, `slow_threshold_setting`, `include_args`; `@logged_class` `slow_threshold_ms`, `include_args`; `setup_logger()` `renderer`; and `context_getter`/`depth` are named as removed in REQ-007, REQ-015 and AC-013. |
| REQ ↔ AC wording match | PASS (after F-P5-01, F-P5-06) | AC-003 now states the REQ-011 field contract, including the negative half (the pipeline's own names must not leak into a record). |
| Terminology drift | PASS (after F-P5-05) | §3 defines a **sink** as one managed standard-library handler plus its renderer, so REQ-002 ("two managed sinks") and INV-001 ("exactly one console handler and one file handler") state the same fact. |
| Scope consistency (CROSS-CUTTING: Impact Analysis names every affected feature and the REQ/AC IDs it touches) | PASS | §10 has 7 rows — `backend.logging` (owner), `backend.settings`, `backend.eventbus`, `backend.permissions`, tooling (`pyproject.toml`), guidance, and the amended specs — matching the TODO In-scope list and the 39-statement migration count (17 + 11 + 10 + 1). Out-of-scope items in `docs/todo/structlog-logging.md` (no HTTP request logging, no log shipping/aggregation, no consumer of structured records) appear in §1 Scope boundaries and nowhere as a requirement. |
| Performance budget still holds with the mandated logging active, and states the logging context | PASS | NFR-001 < 25 ms (measured 0.85 ms median, n = 5 fresh processes, INFO, console + queue + rotating file handler + root forwarding handler + listener started). NFR-002 < 1 ms **with both managed sinks active at DEBUG** (measured 0.148 ms/call; 0.006 ms/call for the tracing machinery alone) — the pre-amendment budget had only ever been measured with logging disabled. NFR-005 caps the pipeline at one extra thread; NFR-003 keeps locals out of records. |
| Traceability rows are legal | PASS | `## Structlog Logging Matrix` holds 18 rows (15 per-REQ plus grouped INV / EDGE / NFR rows), citing only IDs this spec defines and the legal `PENDING` status; the NFR row now covers NFR-001…NFR-005 (F-P5-08). |
| Repository gates | PASS | `uv run python scripts/check_traceability.py` → `Traceability: PASS (765 matrix rows, 129 spec IDs, 714 test functions)`, exit 0. `uv run mkdocs build --strict` → exit 0, only the Material for MkDocs 2.0 deprecation banner. |

### Dependency Smoke-Test — PASS

`structlog` is not a project dependency, so it was smoke-tested without adding one: `uv run --with structlog python C:/Users/domin/AppData/Local/Temp/p5_structlog_smoke.py`, run from the change worktree (the script is deliberately left uncommitted in the temp directory). Versions: structlog 26.1.0, orjson 3.12.0, project Python 3.14.5, Windows 11. No hang, no crash, no segfault; the script ends `SMOKE OK` and asserts, from what the JSON file sink actually wrote:

- exactly one record per emitted call (one record per line, no appended traceback);
- `level`, `logger`, `event`, `timestamp`, the location fields and `elapsed_ms` on the traced-exit record;
- the formatter's bookkeeping keys absent from every record;
- the exception record carries the traceback and **not** the value of the local variable planted in the raising frame (REQ-009, NFR-003);
- a forwarded third-party record reaches the sink with its own logger name, level and emitting file (REQ-004, REQ-011);
- a numeric level (47) renders as `[level 47 ]` (EDGE-004);
- the bootstrap record appears exactly once (AC-015).

The dependency is therefore **kept** as the ADR's default; the capability-first wording of REQ-001 and ADR-082 is what keeps the requirements independent of it.

Six library facts came out of the smoke test and were absorbed into the design (F-P5-06, now in ADR-082 § Decision and spec D3/D4/D7): the JSON renderer's serializer option is `serializer=` (the older keyword was removed and an unknown keyword fails only at render time); the JSON serializer returns **bytes**, so the adapter must decode to `str` and must tolerate the keyword arguments the renderer forwards; the formatter injects two bookkeeping keys that nothing strips by default, so a processor must drop them before rendering; the standard queue handler formats records while enqueueing, so the queue handler must pass the record through unformatted; the callsite step must run at the emitting call site (in the formatter chain it resolves inside the listener thread) and names its fields `filename`/`lineno`; and `log.exception()` puts the exception on the record rather than in the event dict, so the pipeline renders it into `exception` and suppresses the standard library's own formatting.

### Findings and resolutions

| # | Finding | Resolution |
|---|---|---|
| F-P5-01 | `REQ-011` (record fields) had **no acceptance criterion** in §5, while the traceability row claimed AC-003 covered it — an untestable requirement plus a matrix claim the spec did not support. | AC-003 now maps to `REQ-002, REQ-011` and states the negative half of the field contract. |
| F-P5-02 | `logging.md` §9/§10 cited test paths and function names that do not exist on disk (`tests/acceptance/test_logging.py::test_setup_logger_sinks_configured`, `tests/unit/test_logging.py::test_intercept_handler_routes_records`, …) — pre-existing drift already noted at `docs/verification/main-ci-green.md:368`. After P.4 it directly contradicted `structlog-logging.md` §11, which names the real functions. | §9/§10 corrected to the on-disk names (`tests/acceptance/logging/test_logging.py::test_ac_001_setup_logger_adds_sinks`, `tests/unit/logging/test_logging.py::test_ac_004_intercept_handler_routes_records`, `tests/unit/logging/test_logging_edges.py::test_edge_001…004`, `tests/property/logging/test_logging_properties.py::test_inv_001…003`). Wording only: no ID and no status change; noted in the v3 changelog. |
| F-P5-03 | `logging-coverage.md` mandated `setup_logger(Settings(...))` in five places (Design Pattern, D5, the §3.3 example, REQ-011, AC-011) although the call has always been no-arg (`def setup_logger() -> None` at `src/backend/logging/_setup.py:96`, called as `setup_logger()` at `src/main.py:220`) and the amended signature is keyword-only (`setup_logger(*, renderer=...)`) — the mandated call would be a `TypeError` after this change. | REQ-011, AC-011, D5, the Design Pattern line and the §3.3 example corrected to `setup_logger()`; the level and sinks come from the settings registry. Recorded in the v2 changelog. |
| F-P5-04 | The amendment table restated `logging.md` NFR-001/002/003 but **omitted NFR-004**, whose test (`test_nfr_004_backward_compatible_api`) asserts that `logged` still accepts `context_getter` and `depth` — the parameters this change removes. The spec planned to amend a test for an ID it never declared amended. | NFR-004 added to the amendment table, to Impact Analysis row 1 and to ADR-082 Compliance; `logging.md` NFR-004 restated so the compatibility it requires is the **import path**, not the parameter surface; §11's row now reads `logging.md REQ-005, NFR-004`, and `logging.md` §9/§10 gained the NFR-004 row it was missing. |
| F-P5-05 | Terminology drift: REQ-002 says "two managed sinks" while AC-002 and INV-001 say "two handlers". | §3 defines a sink as one managed handler plus its renderer and says both phrasings name the same pair. |
| F-P5-06 | The record-field contract names `file`/`line`, but the pipeline's callsite step emits `filename`/`lineno`, and nothing said who maps them; the formatter's bookkeeping keys would otherwise reach rendered records. | §3 states the names are the contract and that the feature maps them; AC-003 forbids the pipeline's own names; D3/D4 and the new D7 record the adapter duties; ADR-082 records the six verified constraints. |
| F-P5-07 | REQ-014/AC-019 scoped the guidance correction to text that "names the removed backend", but the same guidance also names the removed parameters `context_getter`/`depth` (`AGENTS.md:766`) and shows a `setup_logger(Settings(...))` call the amended signature rejects (`AGENTS.md:763`, `:769`, `:772-774`) — guidance this change makes false with no requirement to fix it. | REQ-014 and AC-019 widened to three defect classes (removed backend, removed parameters, rejected call shape) over the **same four files** Q-23 named; Impact Analysis row 7 updated. No new file enters scope. |
| F-P5-08 | The `## Structlog Logging Matrix` NFR row covered only NFR-001 and NFR-002, leaving NFR-003/004/005 untraceable. | Row widened to `NFR-001 … NFR-005`. |

### Accepted, deliberately out of scope

- `logging.md` REQ-008 and its Design Decisions still describe a stub `Settings` module at `src/backend/logging/settings.py`, which conflicts with `settings-coverage.md` REQ-016. Pre-existing drift: `structlog-logging.md` explicitly leaves the `Settings`, `get_settings`, `register_settings` and `_read_setting` exports unchanged, so changing it here would introduce behavior this spec does not describe.
- `AGENTS.md:764` ("Configure with `Settings`") stays for the same reason — the export is unchanged; only the call shape and the removed parameters are inside REQ-014.
- `docs/verification/main-ci-green.md:368` keeps its now-stale note about `logging.md:133-155`: dated verification records are not rewritten.

### P.5 verdict: **PASS**

The specification set is internally consistent; every normative ID has an acceptance criterion and a test-strategy row; the CROSS-CUTTING impact analysis matches the TODO scope; the performance budgets hold with the mandated logging active and state their measurement context; the mandated dependency is verified working on the host; and both repository gates pass. The change is READY for Phase 1 S1.4 (commit the prepared spec, open the amendment PR).

## Phase 2 (S2.2) — Task DAG (2026-10-05)

**Artifact:** `docs/tasks/structlog-logging.tasks.json` (7 tasks), copied to `.github/task-runner/tasks.json` to initialize the active build environment.

**Grouping (CROSS-CUTTING, by affected feature — §10 Impact Analysis):** `backend.logging` owner (T-001 pipeline core + dependency-set part 1, T-002 decorators + tracing-surface contract) · `backend.settings` (T-003 live reconfigure + the amended settings-coverage IDs, T-004 the 28 registry/repository statements) · `backend.eventbus` (T-005 the 10 statements) · `backend.permissions` + `tooling` (T-006 the last loguru import together with the dependency-set finalization) · `guidance` (T-007 AGENTS.md + the python-best-practices skill). §10 row 5 (migrations/alembic) needs no task — no code change, its interaction is EDGE-003, tested in T-001; row 7's amended specs merged with PR #67; row 8 (test suite) is carried by every task's `green_command`.

**ID coverage (machine-checked):** all 51 normative IDs of `docs/specs/structlog-logging.md` (REQ-001…015, AC-001…020, INV-001…005, EDGE-001…006, NFR-001…005) appear in at least one task's `requirements` / `acceptance_criteria` / `invariants` / `edge_cases` / `non_functional`, and all 21 amended IDs of the four amended specs (`logging.md` REQ-001/003/005, AC-001/004/005†, INV-001, EDGE-005†, NFR-001…004; `logging-coverage.md` REQ-010, AC-010; `settings-coverage.md` REQ-014/015/016, AC-019/020/021, EDGE-008) appear in a task's `amended_ids`. The mapping is embedded in the DAG under `id_coverage` for Phase 3/5 traceability. (`settings-coverage.md` REQ-016 / AC-021 / EDGE-008 are amended IDs of that spec, not new IDs of this one.)

**Gate evidence:**

| Check | Command | Result |
|---|---|---|
| DAG well-formed + acyclic + docs/runner in sync | `uv run python scripts/validate_task_dag.py docs/tasks/structlog-logging.tasks.json` and `uv run python scripts/validate_task_dag.py` | PASSED: 7 tasks, acyclic, well-formed (both) |
| JSON validity | `uv run python -c "import json; json.load(...)"` on both files | both valid |
| ID coverage + allowed_files citation | ad-hoc check against the spec tables | 51 own + 21 amended covered, no missing ID, no citation outside `allowed_files` |

**Deptry interlock (S2.1 merged-main fact 1, honored in the graph):** `quality_check` runs `uv run deptry .` at Phase 5 parity (`pyproject.toml:224`) and deptry scans `src/`, `migrations/`, `scripts/` but **not** `tests/` (it reports "Scanning 89 files" — the 90 non-test `.py` files). The dependency set is therefore changed in exactly two tasks, each paired with the code that keeps deptry clean afterwards: **T-001** declares `structlog` in the same task that imports it and drops `orjson` from the `DEP002` ignore in the same task that imports `orjson` (loguru stays declared — settings/eventbus/permissions still import it); **T-006** removes the last loguru import in the scan set (`src/backend/permissions/service.py`) in the same task that removes loguru from `[project].dependencies`. Every intermediate state passes deptry, and `uv run deptry .` is a `completion_gates` entry of T-001, T-004, T-005 and T-006.

**DAG corrections made during validation (gate satisfiability — no test was dropped):**

1. **Narrowed gate, AC-003 / INV-005 / the elapsed half of REQ-011 moved from T-001 to T-002.** They assert a *traced* exit record (`elapsed_ms`, the mapped field set), which needs the rebuilt decorator; in T-001 only untraced records exist. T-001 keeps the non-traced record-field path; **T-002** covers the traced-exit path.
2. **Narrowed gate, AC-009 split per feature.** The spec's single all-four-features witness (`test_ac_009_statements_go_through_get_logger`) cannot pass before every feature is migrated, so T-004 and T-005 carry per-file witnesses (`…_settings_statements_go_through_get_logger`, `…_eventbus_statements_go_through_get_logger`) and **T-006** owns the spec-named all-four witness plus AC-001 (no backend import anywhere) — the task that removes the last one.
3. **Gate scoping fix.** T-001, T-002 and T-004 originally ran whole test directories in `green_command`; because Phase 3 derives *every* task's tests before Phase 4 starts, those directories would have contained a later task's still-RED tests and the task's GREEN gate could never be observed. The commands now name this task's tests plus the pre-existing tests it must fix, and exclude later tasks' files (recorded as a `design_constraints` entry in each affected task). The full suite stays the Phase 5 gate.
4. **T-004 dependency check.** Its `green_command` no longer runs `tests/acceptance/settings_coverage/` — T-004 does not depend on T-003, so T-003's RED tests would have failed T-004's gate.
5. **Breaking-change containment (S2.1 merged-main fact 2).** Every task that breaks a pre-existing test lists those tests in its own `green_command`: T-001 (the two authorized deletions + the re-derived `logging.md` AC-001/AC-004/INV-001/NFR-001 tests), T-002 (the whole `logging_coverage` suite plus the four cross-feature logging tests, reached through the re-implemented helpers), T-003 (the six re-derived settings-coverage tests), T-006 (the `logging-coverage` REQ-010/AC-010 traceability row update alongside the authorized test deletion, so `scripts/check_traceability.py` never sees a dangling reference).

**Phase 2 gate: PASS** — the DAG is initialized, acyclic, well-formed, feature-grouped, and covers every normative ID. Next: S3.1 (derive tests, one fresh subagent per DAG task).

## Phase 3 (S3.1) — T-001 test derivation (2026-10-05)

**Step scope:** DAG task **T-001** only (record-pipeline core: dedicated non-propagating feature logger, two managed stdlib sinks, the single root forwarding handler, `renderer=` selection, `get_logger()`, the export surface, the structlog/orjson dependency half). T-002's tracing decorators were **not** derived. The binding list was T-001's `tests_to_create` array in `docs/tasks/structlog-logging.tasks.json` — **22 test functions (18 created + 4 re-derived) plus 2 authorized deletions**, all present, nothing else derived.

**Normative basis:** `docs/specs/structlog-logging.md` (approval cached in § Phase 2 (S2.1)) + `docs/specs/logging.md` v3 (AC-001, AC-004, INV-001, NFR-001 restated; AC-005, EDGE-005 deleted) + `docs/decisions/ADR-082-structlog-processor-layer-over-stdlib.md` (D1–D7, six pinned structlog-26 API facts — not re-discovered).

### Tests created / re-derived (22)

| Test | ID(s) | Layer | Observed failure mode at S3.1 |
|---|---|---|---|
| `tests/acceptance/logging/test_logging.py::test_ac_001_setup_logger_adds_sinks` (re-derived) | AC-001 v3 | acceptance | AssertionError — `managed_sinks()`: "expected exactly one logger owning the managed console sink, found {}" |
| `tests/acceptance/logging/test_pipeline_backend.py::test_ac_002_two_managed_handlers` | AC-002, REQ-002/003 | acceptance | same AssertionError |
| `tests/acceptance/logging/test_third_party_records.py::test_ac_006_third_party_reaches_both_sinks` | AC-006, REQ-004 | acceptance | same AssertionError |
| `tests/acceptance/logging/test_get_logger.py::test_ac_008_get_logger_emits_to_sinks` | AC-008, REQ-005 | acceptance | AssertionError — `bound_logger()`: "REQ-005: backend.logging must export get_logger()" |
| `tests/acceptance/logging/test_renderer.py::test_ac_010_renderer_selection` | AC-010, REQ-006 | acceptance | AssertionError — subprocess returncode ≠ 0 (`setup_logger(renderer=…)` not implemented) |
| `tests/acceptance/logging_coverage/test_sink_failure.py::test_ac_016_call_unaffected_by_failing_file_sink` | AC-016 | acceptance | same `managed_sinks()` AssertionError (no managed sink to sabotage) |
| `tests/unit/logging/test_sink_ownership.py::test_ac_004_foreign_handlers_untouched` | AC-004, INV-004 | unit | **PASSED (expected GREEN)** — loguru already leaves foreign handlers untouched; kept as the ownership regression guard |
| `tests/unit/logging/test_sink_ownership.py::test_ac_005_no_duplicate_records` | AC-005, REQ-003/004 | unit | AssertionError — `bound_logger()` (get_logger missing) |
| `tests/unit/logging/test_third_party_records.py::test_ac_007_location_of_emitting_call` | AC-007, REQ-004/014 | unit | AssertionError — "AC-007: the forwarded record must reach the file sink" |
| `tests/unit/logging/test_pipeline_edges.py::test_edge_001_log_file_parent_created` | EDGE-001 | unit | AssertionError — "the record must be written as JSON" (loguru pipe-format line in the file) |
| `…::test_edge_002_rotation_with_open_handle` | EDGE-002 | unit | AssertionError — "rotation must produce a backup file, found ['app.log']" (loguru dated-name rotation) |
| `…::test_edge_004_unknown_numeric_level` | EDGE-004 | unit | `managed_sinks()` AssertionError |
| `…::test_edge_005_unknown_renderer` | EDGE-005, REQ-006 | unit | AssertionError — "REQ-006: setup_logger() must accept a renderer parameter" |
| `…::test_edge_006_get_logger_before_setup` | EDGE-006 | unit | AssertionError — "using get_logger() before setup must not raise" |
| `…::test_nfr_005_single_listener_thread` | NFR-005, D4 | unit | AssertionError — "the file sink must be fed through a queue handler" |
| `tests/integration/logging/test_external_reconfiguration.py::test_edge_003_file_config_keeps_managed_handlers` | EDGE-003, REQ-013 | integration | `managed_sinks()` AssertionError |
| `tests/property/logging/test_pipeline_invariants.py::test_inv_001_concurrent_setup_owns_two_handlers` | INV-001 v3, REQ-002 | property (Hypothesis, `st.integers(1, 16)`, `max_examples=8`) | AssertionError — subprocess probe prints `OWNERS 0 / CONSOLE 0 / FILE 0` |
| `tests/property/logging/test_pipeline_invariants.py::test_inv_004_other_loggers_untouched` | INV-004, REQ-003 | property (Hypothesis, sampled operations/levels/renderers) | ExceptionGroup of **two AssertionErrors** (renderer parameter; no managed sink) — no setup/fixture error |
| `tests/property/logging/test_logging_properties.py::test_inv_001_concurrent_setup_logger_sinks` (re-derived) | INV-001 v3 | property | AssertionError — "INV-001: 1 concurrent setups, output: …" |
| `tests/contract/logging/test_tracing_surface.py::test_ac_020_public_export_surface` | AC-020, REQ-015 | contract | AssertionError — export set ≠ §3 public API (`get_logger` missing) |
| `tests/contract/logging/test_logging_contracts.py::test_nfr_001_setup_time_budget` (re-derived, budget 50 → **25 ms**, median of 3 fresh processes) | NFR-001 v3 | contract | **PASSED (expected GREEN)** — the current loguru setup measures ≈ 5 ms median; the budget gate is a ceiling, not a RED signal |
| `tests/unit/logging/test_logging.py::test_ac_004_intercept_handler_routes_records` (re-derived as the root-forwarding-handler case) | AC-004 v3 | unit | `managed_sinks()` AssertionError |

**RED audit for S3.2:** 20 of 22 fail with an **AssertionError on unimplemented behavior**; none fails in collection, import, fixture setup, or test-data construction. The two PASSED tests are the expected-GREEN guards named above (AC-004 ownership guard, NFR-001 time budget) — S3.2 must not read them as a missing RED. A missing public symbol is surfaced as an AssertionError, never an ImportError: no test module imports `get_logger` at module level; `bound_logger()` in `tests/logging_test_helpers.py` resolves it with `getattr` and asserts it is callable.

### Authorized per-ID deletions (2, Q-18)

| Deleted test | Justification |
|---|---|
| `tests/unit/logging/test_logging.py::test_ac_005_intercept_handler_skips_bootstrap` | `logging.md` **AC-005 deleted** in v3 — the bootstrap-skip rule is retired with the loguru intercept handler (structlog-logging REQ-004 replaces it with the single root forwarding handler) |
| `tests/unit/logging/test_logging_edges.py::test_edge_005_intercept_unknown_level` | `logging.md` **EDGE-005 deleted** in v3 — the case survives as `structlog-logging` **EDGE-004**, re-covered by `tests/unit/logging/test_pipeline_edges.py::test_edge_004_unknown_numeric_level` |

No other test was deleted, weakened or altered. The third deletion the spec authorizes (`tests/acceptance/logging_coverage/test_direct_loguru_kept.py`, enforcer of the retired `logging-coverage.md` REQ-010/AC-010 wording) is **not** in T-001's list and was left in place — it belongs to T-006.

### Test-design decisions recorded for the implementer

- **Observation without private imports:** the feature logger is found by scanning `logging.Logger.manager.loggerDict` for the single non-root logger owning a stderr `StreamHandler` (stderr = `stream is sys.stderr or stream.fileno() == 2`, identity alone fails under pytest's fd capture); the rotating handler is found by a `gc` scan, because D4 attaches it to the listener, not the logger; console output is captured with fd-level `dup2` on the handler's stream fd, because a `ConsoleRenderer` may bind its own stream object.
- **INV-004 vs AC-006 (documented interpretation, not a question):** INV-004 freezes every logger's handler set, level and disabled state *except* "the single forwarding handler the feature installs on the root logger". AC-006 requires foreign records to reach both sinks **at the configured level**, which needs the root logger's level to route them. Reading: the root-logger exception covers the root logger's **routing state** — the one forwarding handler plus the root level needed to route foreign records. Asserted that way in `test_ac_006_third_party_reaches_both_sinks` and `test_inv_004_other_loggers_untouched` (which asserts foreign loggers are untouched and that the root logger gains at most one handler and never loses one).
- **No color assertion:** the spec fixes record fields, never the format string (D3), and structlog's `ConsoleRenderer` colorizes only on a tty — the console assertions stop at "standard error + human-readable text, not JSON".
- **EDGE-002 is naming-agnostic:** more than one file matching the log-path glob, every probe record present across them, and `--- Logging error ---` absent from the subprocess stderr, because the stdlib swallows handler exceptions through `Handler.handleError` and a non-zero returncode cannot prove otherwise.
- **EDGE-003 does not touch `migrations/env.py`** (spec constraint): the integration test replays `logging.config.fileConfig(..., disable_existing_loggers=True)` to mimic alembic and asserts the two managed handlers survive, a later `logging.*` change re-enables the feature's own logger and re-installs the root forwarding handler, and a foreign logger disabled by `fileConfig` stays disabled. The autouse `tests/conftest.py::_stdlib_root_logging_restored` fixture stays as the suite guard.
- **Renderer selection runs in fresh interpreters** (`setup_logger()` is idempotent per process, so a second call with another renderer is a no-op); the subprocess points `sys.stderr` at a file before setup so the console handler binds to a readable stream. The subprocess property probes inline their handler-scan code (`PIPELINE_COUNT_CODE`), because `pyproject.toml` sets no `pythonpath` and `sys.executable -c` can import only `backend.*`.
- **AC-016 sabotages both failure points** — the `QueueHandler` on the feature logger (raises in the caller's thread) and the rotating handler (raises on the listener thread) — restoring both in `try/finally` so the session-scoped sinks are not poisoned, and proves console liveness with a separate stdlib probe record rather than the traced call's records (the `@logged` decorator is still loguru-based until T-002).
- **Callsite assertions are path-shape agnostic:** `Path(record["file"]).name` equals the test module name and `record["line"]` equals the line captured by the emitting helper (`inspect.currentframe().f_lineno - 1`), never an absolute-path comparison.
- **Helpers are additive:** `tests/logging_test_helpers.py` gained `STDERR_FD`, `MANAGED_HANDLER_COUNT`, `_is_console_handler`, `pipeline_logger`, `managed_sinks`, `rotating_file_handlers`, `captured_console`, `json_records`, `wait_for_record`, `bound_logger`, `subprocess_setup_code`, `PIPELINE_COUNT_CODE`, `run_python`. The loguru-era helpers (`captured_stderr`, `wait_for_file_content`, `_console_sink_fd`) are untouched — other suites import them and replacing them is an implementation step.
- **Left for the T-001 implementation step** (in `allowed_files`, not in `tests_to_create`): `tests/unit/logging/test_logging_sink_ownership.py` and the loguru-internals tests in `tests/unit/logging/test_logging.py` (`test_ac_003_setup_logger_thread_safe`, AC-006…AC-014) inspect `logger._core.handlers` and will break when the loguru sinks are removed; they were deliberately not derived here. `tests/acceptance/logging/test_logging.py::test_ac_002_setup_logger_idempotent` compares handler counts before/after setup and stays valid (0 == 0) after the loguru sinks are gone.

### S3.1 gates

| Check | Command | Result |
|---|---|---|
| Pre-flight collection (before derivation) | `uv run pytest --collect-only -q <T-001 paths>` | clean — 32 tests, 0 errors |
| Post-flight collection | `uv run pytest --collect-only -q <T-001 paths>` | clean — **48 tests, 0 errors**; all 22 T-001 functions collected, both deleted tests absent |
| Lint + format (changed paths only) | `uv run ruff check <paths>` / `uv run ruff format <paths>` | **All checks passed** (24 files) |
| No implementation code written | `git status --short -- src pyproject.toml migrations` | empty — the commit contains no `src/`, dependency or migration change |
| Traceability after the 2 deletions | `uv run python scripts/check_traceability.py` | **PASS** (765 rows, 129 spec IDs, 729 test functions) — the `logging.md` AC-005/EDGE-005 rows already carry an em-dash Test cell, so nothing dangles |

**Phase 3 (S3.1, T-001) gate: PASS.** Next: S3.1 for T-002…T-006, then S3.2 (ruff + RED confirmation across the derived set).

## Phase 3 (S3.1) — T-002 test derivation (2026-10-05)

Task **T-002 — Tracing decorator: entry/exit/exception records, `@logged_class`, coverage-suite capture** (REQ-005, REQ-010, REQ-011, REQ-012, REQ-013, REQ-014; AC-003, AC-011…AC-015; INV-002, INV-003, INV-005; NFR-002, NFR-004). All 11 `tests_to_create` functions exist; the three amended existing tests were rewritten in place, never weakened.

### Tests created / amended

| Test | File | Requirement | Expected failure mode (RED) |
|---|---|---|---|
| `test_ac_011_sync_and_async_traced_records` | `tests/acceptance/logging/test_tracing_records.py` (new) | AC-011 / REQ-011 | `TimeoutError` from `wait_for_traced_record` — the loguru decorator writes no record to the managed file sink, so `json_records` never yields an entry or exit record for the call. |
| `test_ac_012_exception_record_and_propagation` | `tests/acceptance/logging/test_tracing_records.py` (new) | AC-012 / REQ-012 | `TimeoutError` waiting for the exception record (no `exception` field is produced by the current decorator). |
| `test_ac_014_logged_class_records` | `tests/acceptance/logging/test_tracing_records.py` (new) | AC-014 / REQ-014 | `TimeoutError` waiting for the public method's exit record; the private-method assertion passes vacuously today and stays as the regression guard. |
| `test_ac_003_file_record_fields_as_json` | `tests/acceptance/logging/test_pipeline_backend.py` (amended) | AC-003 / REQ-005 + REQ-011 elapsed half | `TimeoutError` — the traced call produces no JSON record, so the required-field set (`level`, `logger`, `event`, `timestamp`, `elapsed_ms`, `file`, `line`) and the forbidden-key set are never checked. |
| `test_ac_015_no_local_values_in_exception_record` | `tests/acceptance/logging/test_secrets.py` (new) | AC-015 / NFR-003 | `AssertionError` on `'RuntimeError' in blob` — the exception record never reaches the file, so the record assertions fail **before** the no-local-values assertion. |
| `test_ac_013_removed_parameters` | `tests/contract/logging/test_tracing_surface.py` (appended) | AC-013 / REQ-013 | `AssertionError` — `context_getter` and `depth` are still in `inspect.signature(logged)`, and calling `@logged(context_getter=…)` / `@logged(depth=1)` does not raise. |
| `test_inv_002_no_local_value_ever_recorded` | `tests/property/logging/test_pipeline_invariants.py` (appended) | INV-002 / NFR-003 | Pre-flight `AssertionError` (`managed_sinks()` is empty) before Hypothesis runs, so RED costs one assertion, not one wait per example. |
| `test_inv_003_elapsed_non_negative` | `tests/property/logging/test_pipeline_invariants.py` (appended) | INV-003 / REQ-011 | Same pre-flight `AssertionError` on the empty pipeline. |
| `test_inv_005_required_fields_present` | `tests/property/logging/test_pipeline_invariants.py` (appended) | INV-005 / REQ-005 | Same pre-flight `AssertionError`; the per-example body asserts the exact rendered key set (no `filename`/`lineno`, no formatter bookkeeping keys). |
| `test_nfr_002_decorator_overhead_budget` | `tests/contract/logging/test_logging_contracts.py` (amended) | NFR-002 | `AssertionError` — `managed_sinks()` is empty, so the measurement context cannot be established (the test no longer measures with logging disabled). |
| `test_nfr_004_backward_compatible_api` | `tests/contract/logging/test_logging_contracts.py` (amended) | NFR-004 | `AssertionError` — `logged`'s parameter set is still `{level, slow_threshold_ms, slow_threshold_setting, include_args, context_getter, depth}`; the import path and the zero-argument `setup_logger()` call already hold. |

### Design decisions taken while deriving

- **Records are observed through the pipeline surface, not loguru capture.** Every T-002 test reads the managed file sink as JSON (`json_records` / `wait_for_record`) and classifies traced records by **fields**, never by message wording: entry = event mentions the qualname and has no `elapsed_ms` key; exit = carries `elapsed_ms`; exception = carries an `exception` field. The spec fixes the fields, not the wording, so the tests cannot pin an event format T-004 is free to choose.
- **AC-003 forbidden-key set is verified, not guessed.** `ProcessorFormatter` pops `positional_args` and `events` from the event dict before rendering (confirmed against structlog 26.1.0 with `uv run --with structlog==26.1.0`), and `PositionalArgumentsFormatter` writes `positional_args`. The asserted forbidden set is therefore `{filename, lineno, _record, _from_structlog, positional_args, events}`; the required set is `{level, logger, event, timestamp, elapsed_ms, file, line}`.
- **AC-015 plants the secret where only a local-value dumper leaks it.** The secret is a local in the raising frame and never an argument, message or exception attribute, so a record that carries only type + message + traceback frames cannot contain it; the assertion scans the whole log file, not one record.
- **Property tests fail fast.** INV-002/003/005 assert the managed pipeline exists before the Hypothesis loop and use short per-example waits, so a RED run costs one assertion instead of a 15 s wait per example. INV-002 checks only the bytes appended by its own call (`file_size` + `records_since`), which keeps examples independent in one shared session file.
- **NFR-002 states its measurement context.** The test asserts the managed console handler and the queue-wrapped rotating file handler are installed at `DEBUG` before timing, and measures with **nothing disabled** — the old `logger.disable("DEBUG")` / `logger.enable("DEBUG")` pair disappears with the backend. Budget `< 1 ms/call` against the spec's 0.148 ms/call reference measurement.
- **NFR-004 asserts compatibility of the import path, not of the old parameter list.** The old body asserted `context_getter` and `depth` are present, which the amended spec (design decision D6) removes; it now asserts the exact reduced parameter set and that `setup_logger()` still takes no required argument. This is a spec-driven restatement, not a weakening: the assertion got **stronger** on the parameter set and the import path is unchanged.

### Helper adaptations (no assertion weakened)

`tests/logging_test_helpers.py` gained, additively: `parse_json_records`, `session_log_path`, `record_mentions`, `wait_for_traced_record`, `traced_records`, `file_size`, `records_since`; `json_records` now delegates to `parse_json_records` (same signature, same behaviour). Nothing was removed or renamed, so every existing importer still resolves.

The loguru-era capture helpers (`capture_records` in `tests/logging_coverage_test_helpers.py`, `log_records` in `tests/conftest.py`, and the loguru half of `tests/logging_test_helpers.py`) were **not** rewritten during derivation: they are the capture mechanism for 38 currently-green tests outside T-002's `tests_to_create`, and re-implementing them before the pipeline exists would turn those tests red without adding a single new RED signal. Re-implementing them keeping their public signatures is T-002's **implementation** step (they are in its `allowed_files`), and the coverage-suite assertions themselves are untouched.

### Forward risks recorded for the implementation step

- `test_nfr_003_diagnose_false` (same file, not in `tests_to_create`) drives the file sink through **loguru's** `logger.exception` and waits with the loguru-based `wait_for_file_content`. It is GREEN now and will break when `setup_logger` stops installing loguru sinks; §11 maps NFR-003 to the INV-002 property test, so the implementation step must re-point it at the pipeline (or delete it as a superseded loguru-internals test) rather than relax the no-local-values check.
- `wait_for_file_content` still calls `logger.complete()` (loguru) before polling. Once the loguru sinks are gone that drain is a no-op and the flush must come from the stdlib `QueueListener`; every file-sink assertion in this task depends on that flush.
- `tests/conftest.py`'s autouse `_stdlib_root_logging_restored` fixture is unchanged and stays.

### Capture-helper blast radius (measured, for the implementation step)

The loguru-era capture surface is wider than the task brief's estimate: **38 test functions in 24 modules** call `capture_records` / `log_records` / the coverage helpers. 14 of them are cross-feature (authentication, mail, settings, filemanagement, search, usermanagement, permissions, sessionmanagement); the remaining 24 are the `logging_coverage` suite. All 38 are currently GREEN and none is in T-002's `tests_to_create`, which is why the helpers were left working during derivation. T-002's implementation step must re-implement them behind their existing signatures or all 38 break at once.

### S3.1 (T-002) gates

| Check | Command | Result |
|---|---|---|
| Pre-flight collection (before derivation) | `uv run pytest --collect-only -q <T-002 paths>` | clean — 8 tests, 0 errors (the 4 existing files at HEAD; the 3 new modules did not exist, none of the 11 `tests_to_create` names present) |
| Post-flight collection | `uv run pytest --collect-only -q <T-002 paths>` | clean — **17 tests, 0 errors**; all 11 `tests_to_create` functions collected (3 + 2 + 1 + 2 + 4 + 5 per file) |
| Lint + format (changed paths only) | `uv run ruff check <paths>` / `uv run ruff format <paths>` | **All checks passed** (7 files) |
| Traceability referential integrity | `uv run python scripts/check_traceability.py` | **PASS** (765 matrix rows, 129 spec IDs, 738 test functions) |
| No implementation code written | `git status --short -- src pyproject.toml uv.lock migrations` | empty |

**Phase 3 (S3.1, T-002) gate: PASS.** Next: S3.1 for T-003.


---

## Phase 3 (S3.1) — T-003 test derivation (2026-10-05)

Task **T-003 — live reconfiguration on a `logging.*` settings change** (REQ-012, AC-017, INV-004; amended `settings-coverage.md` v2 REQ-014/015/016, AC-019/020/021, EDGE-008; `settings.md` v4 observability wording). All 6 `tests_to_create` functions exist in the DAG's paths; 5 were re-derived in place from the amended wording, none was weakened or deleted.

### Tests created / re-derived

| Test | File | Requirement | Old → new | Observed failure mode at HEAD `d82cc1e` |
|---|---|---|---|---|
| `test_ac_017_live_reconfigure` | `tests/acceptance/settings_coverage/test_setup_logger.py` (new) | AC-017 / REQ-012 + INV-004 | new — no predecessor | `AssertionError: expected exactly one logger owning the managed console sink, found {}` from `managed_sinks()` — no standard-library pipeline exists yet |
| `test_setup_logger_reads_registry` | same file (re-derived) | AC-019 / REQ-014 v2 | subprocess printing loguru's private `logger._core.handlers` → `h._sink._file.name` / `h._levelno`, polled with `time.sleep(0.05)` → `PIPELINE_COUNT_CODE` + `_ROTATING_CONFIG_CODE` (handler configuration) + an ERROR/WARNING routing probe read from the captured stderr, no sleeps | `AssertionError: REQ-002: the no-arg setup must own one console sink: OWNERS 0 / CONSOLE 0 / FILE 0 / QUEUED 0 / FEATURE_HANDLERS 0 / ROTATING 0`. The level half already holds pre-change (the ERROR record is routed, the WARNING record is suppressed by loguru's ERROR sink) |
| `test_sink_reconfigured_on_change` | same file (re-derived) | AC-020 / REQ-015 v2 + INV-004 | subprocess + loguru `h._levelno` polled with sleeps → in-process: the records that reach the console (fd capture) and the file sink (JSON), plus the INV-004 foreign-handler witnesses | `AssertionError: expected exactly one logger owning the managed console sink, found {}` |
| `test_logging_stub_removed` | `tests/unit/test_settings_coverage.py` (re-derived) | AC-021 / REQ-016 v2 | one assertion on a CWD-relative path → repo-root path + `Settings` is not a model + its exact field set + the export carries the live registry values | **GREEN at HEAD** — the stub was already removed by the settings-coverage change; the re-derivation only strengthens the witness, so this test contributes no RED |
| `test_sink_reconfigured_rotation` | same file (re-derived) | EDGE-008 v2 | **no assertion at all** after the write (the body ended at `set_value_settled`) → exactly one managed rotating sink, `maxBytes`/`backupCount` re-applied, path + encoding kept, a record at the current level still reaching the file | `AssertionError: EDGE-008/INV-001: exactly one managed rotating file sink after the reconfigure, found 0` |
| `test_observability_tracing` | same file (re-derived) | NFR-004 + `settings.md` v4 §9 wording | `register_settings` traced + `assert _read_setting is not None` (vacuous) → both traced + the value-change record must arrive in the managed file sink | `AssertionError: NFR-004 / settings.md v4 §9: the value change must be logged with key context through the shared logging feature` (`assert None is not None`) — the loguru record is not a pipeline record |

### Design decisions taken while deriving

- **No sleeps.** The two old subprocess tests polled with `time.sleep(0.05)` against a 5 s deadline; neither re-derived test contains a `sleep` call. The in-process tests use the shared wait helpers (`wait_for_record`, `wait_for_record_since`) for the queue-fed file sink, and read the console deterministically — a standard-library `StreamHandler` flushes on `emit`, so the console half of AC-019 is asserted on the subprocess's captured stderr once the process has exited, with no waiting at all.
- **Mechanism-free assertions.** EDGE-008 v2 states that replacing the sink is "one allowed mechanism, not a required one" and REQ-015 v2 allows mutating the feature's own handlers in place, so the tests read the handler's **configuration** (`maxBytes`, `backupCount`, `baseFilename`, `encoding`) and the **records** that reach the sinks — never whether a sink object was replaced.
- **Registry values chosen so the defaults cannot masquerade as the configuration.** AC-019's subprocess sets `log_level=ERROR` (the hardcoded default is INFO), `log_max_bytes=2048`, `log_backup_count=3` (defaults 10485760 / 5). The level is probed behaviourally (an ERROR record lands, a WARNING record is suppressed) because the spec fixes the effective level, not whether it is set on the logger or on the handlers.
- **In-process vs subprocess.** AC-017's clause is "without restarting the process", so it runs in-process against the session pipeline; AC-019 needs a process where `setup_logger()` has not run yet, so it stays a subprocess (the shape the old test already had). Both reuse the T-001/T-002 helpers; the only new subprocess source is `_ROTATING_CONFIG_CODE`, kept module-local in the test file because `tests/logging_test_helpers.py` is not in T-003's `allowed_files`.
- **One witness set for the INV-004 clause.** A module-local `_ForeignState` attaches a handler to the root logger and a handler to another feature's logger, records their level/formatter and the other logger's level/propagate/disabled, and `assert_untouched()` checks them from both AC-017 and AC-020 (the same clause in both). It also keeps AC-017 inside ruff's PLR0915 statement limit.
- **Registry hygiene.** Every `logging.*` write in the in-process tests goes through `set_value_settled` (the write's dispatch is awaited) and is restored in a `finally`, so the session sinks end pointed at the session log file for later tests. `test_logging_stub_removed` builds its registry with `EventCollector`, so its writes publish nothing to the shared bus and cannot reconfigure the session sinks; `test_observability_tracing` uses `install_isolated_registry()` with a temp `YamlValueRepository` and a non-`logging.*` probe key.
- **No duplication of T-004's witness.** `test_observability_tracing` deliberately does not scan the settings modules for a backend import — that is structlog-logging AC-009's witness, derived in T-004 (`test_ac_009_settings_statements_go_through_get_logger`). What is observable from the settings side is that a settings operation's record arrives in the logging feature's file sink.

### Assertion-strength record (settings-coverage: nothing weakened)

| Test | Old | New | Delta |
|---|---|---|---|
| `test_setup_logger_reads_registry` | file-sink path == `log_file`; console handler level == the registry level | the same two facts via handler configuration + handler counts + `maxBytes`/`backupCount`/`encoding` + routed/suppressed records | restated in capability terms, strictly more assertions |
| `test_sink_reconfigured_on_change` | after the write, the loguru handler levels are DEBUG | both sinks emit a DEBUG record without a restart + only the feature's own sinks change | same contract plus the third clause the v2 wording adds |
| `test_logging_stub_removed` | stub file absent (CWD-relative) | stub absent (repo-root) + not a model + exact field set + export carries registry values | +3 assertions |
| `test_sink_reconfigured_rotation` | none after the write | 5 assertions | +5 |
| `test_observability_tracing` | `register_settings` traced; `_read_setting is not None` | both traced + record reaches the managed file sink | the one deleted assertion cannot fail (it asserted a name is not `None`); it is replaced by a tracing assertion on the same object plus a record-level assertion |

### Red-command observation (informational — S3.2 runs the gate)

`uv run pytest tests/acceptance/settings_coverage/test_setup_logger.py tests/unit/test_settings_coverage.py::test_logging_stub_removed tests/unit/test_settings_coverage.py::test_sink_reconfigured_rotation tests/unit/test_settings_coverage.py::test_observability_tracing -v` → **5 failed, 1 passed**; every failure is an assertion failure on unimplemented behaviour (no import, collection or test-data error). Neighbours: `uv run pytest tests/acceptance/settings_coverage tests/unit/test_settings_coverage.py -q` → 5 failed (the same set), **34 passed** — no collateral damage and no state leak into the tests that follow.

### Cross-task dependency the orchestrator must know

`test_observability_tracing` (NFR-004) cannot go GREEN inside T-003. Its witness is a **settings feature** operation's record arriving in the logging feature's managed file sink, and `src/backend/settings/registry.py` still logs through `from loguru import logger` — 17 statements there and 11 in `repository.py`. Those statements are migrated to `get_logger()` by **T-004** (REQ-005 / AC-009). Until then the record never reaches the standard-library pipeline, so the test stays RED after T-003's own reconfigure work lands. T-003's `green_command` therefore reaches 100% only once T-004 has run; the DAG lists no `blockedBy` edge between them. Shaping the witness to pass earlier would have meant asserting something other than the requirement, so it was left faithful and flagged.

### Gate table (S3.1, T-003)

| Gate | Command | Result |
|---|---|---|
| Pre-flight collection | `uv run pytest --collect-only -q tests/acceptance/settings_coverage/test_setup_logger.py` | 32 collected, 0 errors |
| Post-flight collection (touched paths) | `uv run pytest --collect-only -q tests/acceptance/settings_coverage/test_setup_logger.py tests/unit/test_settings_coverage.py` | 33 collected, 0 errors |
| Post-flight collection (whole suite) | `uv run pytest --collect-only -q tests/` | 755 collected, 0 errors |
| Ruff (changed paths) | `uv run ruff check tests/acceptance/settings_coverage/test_setup_logger.py tests/unit/test_settings_coverage.py` | All checks passed |
| Format | `uv run ruff format <same paths>` | 2 files left unchanged |
| Traceability | `uv run python scripts/check_traceability.py` | PASS (765 matrix rows, 129 spec IDs, 739 test functions) |
| No test weakened | assertion-strength table above | 5 re-derived tests are strictly stronger; EDGE-008 had no assertion at all before |
| No implementation code written | `git status --short -- src pyproject.toml uv.lock migrations` | empty |

**Phase 3 (S3.1, T-003) gate: PASS.** Next: S3.1 for T-004.


---

## Phase 3 (S3.1) — T-004 test derivation (2026-10-06)

Task **T-004 — migrate the 28 direct backend statements in `src/backend/settings/registry.py` (17) and `src/backend/settings/repository.py` (11) to `get_logger()`** (REQ-005; AC-009; amended `logging-coverage.md` v2 REQ-010 / AC-010). Its single `tests_to_create` function exists in the DAG's path.

### Tests created

| Test | File | Requirement | Expected failure mode (RED) |
|---|---|---|---|
| `test_ac_009_settings_statements_go_through_get_logger` | `tests/acceptance/logging_coverage/test_statements_via_feature.py` (new module) | AC-009 / REQ-005 + `logging-coverage.md` REQ-010 / AC-010 v2 | `AssertionError` naming every violated clause: both modules import `loguru.logger`, and all 17 + 11 statement call sites are written on a backend-bound `logger` instead of a `get_logger()`-bound logger |

### Witness design (derived from the spec, not from the current implementation)

- **AC-009 is a source-level witness by construction** — "**Then** none of them imports a logging backend, **And** each of the 39 one-off statements is written through `get_logger()`". The import clause is not observable from any record, so the test parses the module with `ast` rather than driving it.
- **Three clauses, one assertion.** `_statement_violations(path, count)` returns violation strings for (1) an import of a logging backend (`loguru` / `structlog`), (2) the per-file statement count REQ-005 fixes (17 / 11 — `logging-coverage.md` REQ-010 v2: statements stay statements, none added, none removed), and (3) every statement call site whose receiver does not resolve to a `get_logger()` call or to a name bound to one. The test asserts the combined list is empty, so one run names every violation in both files, and a clause that already holds is visible by its absence.
- **The count clause holds pre-change, which validates the detector.** The scan finds exactly 17 and 11 `<logger>.<level>(…)` call sites today, and no other `.debug` / `.info` / `.warning` / `.error` call in either file, so the RED is specifically the "written through `get_logger()`" clause — not a miscount.
- **Implementation-agnostic.** The witness accepts any shape that satisfies REQ-005 — `get_logger("settings").info(…)`, a module-level `_LOG = get_logger("settings")`, or a per-method local — and pins no logger name, no placement, no message wording and no keyword-field form, so T-004's `implementation_steps` (message + fields instead of brace formatting) stay free.
- **The feature-wide gate is included.** T-004's completion gate is "no `loguru` import remains anywhere under `src/backend/settings/`", so the test also scans every module of the settings feature for a backend import (REQ-001's "no module under `src/` imports one", scoped to this task's feature).
- **No behavioural duplicate.** The behavioural half — a settings operation's record arriving in the managed file sink — is already derived in T-003 (`test_observability_tracing`, `tests/unit/test_settings_coverage.py`), and AC-008 covers `get_logger()`'s own record contract; this module deliberately re-asserts neither. The record-capture helpers (`json_records`, `wait_for_record`, `bound_logger`) are therefore not needed by this witness.
- **Helpers are module-local and parameterised** because `tests/logging_coverage_test_helpers.py` is not in T-004's `allowed_files`. T-005 appends `test_ac_009_eventbus_statements_go_through_get_logger` and T-006 appends the spec-named all-four witness `test_ac_009_statements_go_through_get_logger` to this same module and reuse `_statement_violations` / `_backend_imports` unchanged.

### S3.1 T-004 — RED

`uv run pytest tests/acceptance/logging_coverage/test_statements_via_feature.py::test_ac_009_settings_statements_go_through_get_logger -v` → **1 failed, 0 passed** (0.35 s), one `AssertionError` (no import, collection or test-data error):

```text
AssertionError: AC-009 / REQ-005 (logging-coverage REQ-010 v2): src/backend/settings/registry.py imports a logging backend: ['loguru.logger']; src/backend/settings/registry.py statements not written through get_logger(): line(s) [89, 94, 113, 142, 146, 160, 173, 244, 248, 255, 259, 264, 283, 295, 299, 308, 317]; src/backend/settings/repository.py imports a logging backend: ['loguru.logger']; src/backend/settings/repository.py statements not written through get_logger(): line(s) [140, 151, 154, 156, 248, 259, 262, 264, 281, 284, 286]; a module under src/backend/settings/ imports a logging backend: ['src/backend/settings/registry.py', 'src/backend/settings/repository.py']
```

Failure mode: **assertion on unimplemented behaviour** — the 17 + 11 statement line numbers are named, and the count clause contributes no violation (both counts already match REQ-005), so the test is red exactly on the migration AC-009 requires.

Neighbours (no collateral): `uv run pytest tests/acceptance/logging_coverage -q` → **2 failed, 16 passed** — the new AC-009 test plus `test_ac_016_call_unaffected_by_failing_file_sink` (T-001's, still red awaiting the pipeline); nothing else in the directory changed state.

### Gate table (S3.1, T-004)

| Gate | Command | Result |
|---|---|---|
| Pre-flight collection | `uv run pytest --collect-only -q tests/acceptance/logging_coverage/test_statements_via_feature.py` | the module did not exist at HEAD `f2490a0`; none of T-004's `tests_to_create` names present |
| Post-flight collection | same command | clean — **1 test collected, 0 errors** |
| Ruff (changed path) | `uv run ruff check tests/acceptance/logging_coverage/test_statements_via_feature.py` | **All checks passed** |
| Format | `uv run ruff format tests/acceptance/logging_coverage/test_statements_via_feature.py` | **1 file left unchanged** |
| RED (T-004 `red_command`) | `uv run pytest tests/acceptance/logging_coverage/test_statements_via_feature.py::test_ac_009_settings_statements_go_through_get_logger -v` | **1 failed** — assertion failure, message quoted above |
| Test contract / test-data validity | failure output | no `ValidationError` / `ValueError`, no fixture or collection error — the witness builds no model instance |
| Traceability referential integrity | `uv run python scripts/check_traceability.py` | **PASS** (765 matrix rows, 129 spec IDs, 740 test functions) — the AC-009 matrix row itself is S3.2's |
| No implementation code written | `git status --short -- src pyproject.toml uv.lock migrations` | empty |

**Phase 3 (S3.1, T-004) gate: PASS.** Next: S3.1 for T-005.



---

## Phase 3 (S3.1) — T-005 test derivation (2026-10-06)

Task **T-005 — migrate the 10 direct backend statements in `src/backend/eventbus/eventbus.py` to `get_logger()`** (REQ-005; AC-009; amended `logging-coverage.md` v2 REQ-010 / AC-010; Impact Analysis row 3 — `backend.eventbus`, "no spec ID change"). Its single `tests_to_create` function exists in the DAG's path.

### Tests created

| Test | File | Requirement | Expected failure mode (RED) |
|---|---|---|---|
| `test_ac_009_eventbus_statements_go_through_get_logger` | `tests/acceptance/logging_coverage/test_statements_via_feature.py` (appended) | AC-009 / REQ-005 + `logging-coverage.md` REQ-010 / AC-010 v2 | `AssertionError` naming every violated clause: `eventbus.py` imports `loguru.logger`, and all 10 statement call sites are written on the backend-bound `logger` instead of a `get_logger()`-bound logger |

### Witness design (derived from the spec, not from the current implementation)

- **The T-004 helpers are reused unchanged** — `_statement_violations(path, count)`, `_backend_imports`, `_statement_calls`, `_feature_logger_names`, `_written_via_get_logger`, `_parse`. AC-009's three clauses are identical for every named file, so the event bus witness differs only in its argument: `_statement_violations("src/backend/eventbus/eventbus.py", 10)`. Nothing is duplicated and no helper is rewritten.
- **The count 10 comes from the spec, not from the code** — REQ-005 names `src/backend/eventbus/eventbus.py` (10) and Impact Analysis row 3 restates "10 direct statements migrate to `get_logger()`". `logging-coverage.md` REQ-010 v2 keeps each of them a statement: none added, none removed.
- **The feature-wide clause mirrors T-004's** — T-005's completion gate is "no `loguru` import remains anywhere under `src/backend/eventbus/`", so the test also scans every module of the event bus feature (`__init__.py`, `eventbus.py`, `feature_settings.py`) for a backend import, per REQ-001's "no module under `src/` imports one" scoped to this task's feature.
- **Implementation-agnostic.** The witness pins no logger name, no placement (module-level binding vs. per-call `get_logger(...)`), no message wording and no keyword-field form — T-005's `implementation_steps` ("same messages and levels", worker-thread statements unchanged) stay free. Spec section 9 fixes only that the statements' levels stay "DEBUG/INFO/WARNING as today" and the wording is unchanged; the level/message half of that is not observable from the source witness and is covered by the event bus's own existing test directory (T-005's `green_command` runs it unchanged — no behavior delta).
- **No behavioural duplicate.** AC-008 (`test_ac_008_get_logger_emits_to_sinks`) already covers `get_logger()`'s record contract; the event bus's records are asserted by `tests/acceptance/eventbus` / `tests/unit/eventbus`. This witness re-asserts neither.

### S3.1 T-005 — RED

`uv run pytest tests/acceptance/logging_coverage/test_statements_via_feature.py::test_ac_009_eventbus_statements_go_through_get_logger -v` → **1 failed, 0 passed** (0.31 s), one `AssertionError` (no import, collection or test-data error):

```text
AssertionError: AC-009 / REQ-005 (logging-coverage REQ-010 v2): src/backend/eventbus/eventbus.py imports a logging backend: ['loguru.logger']; src/backend/eventbus/eventbus.py statements not written through get_logger(): line(s) [86, 96, 115, 120, 136, 176, 197, 205, 222, 233]; a module under src/backend/eventbus/ imports a logging backend: ['src/backend/eventbus/eventbus.py']
```

Failure mode: **assertion on unimplemented behaviour** — the 10 statement line numbers are named, and the count clause contributes no violation (the count already matches REQ-005's 10), so the test is red exactly on the migration AC-009 requires.

Neighbours (no collateral): `uv run pytest tests/acceptance/logging_coverage -q` → **3 failed, 16 passed** — the new AC-009 event bus test plus the two already-red ones (`test_ac_009_settings_statements_go_through_get_logger` from T-004, `test_ac_016_call_unaffected_by_failing_file_sink` from T-001); nothing else in the directory changed state.

### Gate table (S3.1, T-005)

| Gate | Command | Result |
|---|---|---|
| Pre-flight collection | `uv run pytest --collect-only -q tests/acceptance/logging_coverage/test_statements_via_feature.py` | clean — **1 test collected, 0 errors**; T-005's `tests_to_create` name not present |
| Post-flight collection | same command | clean — **2 tests collected, 0 errors** |
| Ruff (changed path) | `uv run ruff check tests/acceptance/logging_coverage/test_statements_via_feature.py` | **All checks passed** |
| Format | `uv run ruff format tests/acceptance/logging_coverage/test_statements_via_feature.py` | **1 file left unchanged** |
| RED (T-005 `red_command`) | `uv run pytest tests/acceptance/logging_coverage/test_statements_via_feature.py::test_ac_009_eventbus_statements_go_through_get_logger -v` | **1 failed** — assertion failure, message quoted above |
| Test contract / test-data validity | failure output | no `ValidationError` / `ValueError`, no fixture or collection error — the witness builds no model instance |
| Traceability referential integrity | `uv run python scripts/check_traceability.py` | **PASS** (765 matrix rows, 129 spec IDs, 741 test functions) — the AC-009 matrix row itself is S3.2's |
| No implementation code written | `git status --short -- src pyproject.toml uv.lock migrations` | empty |

**Phase 3 (S3.1, T-005) gate: PASS.** Next: S3.1 for T-006.


---

## Phase 3 (S3.1) — T-006 test derivation (2026-10-06)

Task **T-006 — migrate the last backend statement in the deptry scan set (`src/backend/permissions/service.py`) to `get_logger()`, remove loguru from the dependency set, delete the retired-policy test and update its traceability row** (REQ-001, REQ-005, REQ-013; AC-001, AC-009, AC-018; NFR-004; Impact Analysis rows 2–4 and 6 — `backend.permissions` + tooling, dependency set part 2). All three `tests_to_create` functions exist in the DAG's paths.

### Tests created

| Test | File | Requirement | Expected failure mode (RED) |
|---|---|---|---|
| `test_ac_009_statements_go_through_get_logger` | `tests/acceptance/logging_coverage/test_statements_via_feature.py` (appended) | AC-009 / REQ-005 + `logging-coverage.md` REQ-010 / AC-010 v2 | `AssertionError` naming all four named files' backend import and all 39 statement line numbers (17 + 11 + 10 + 1) |
| `test_ac_001_no_backend_import_and_stdlib_chain` | `tests/acceptance/logging/test_pipeline_backend.py` (appended) | AC-001 / REQ-001 | `AssertionError` naming the 18 modules under `src/` and `tests/` that still import the removed backend, **and** the missing standard-library chain (no logger owns the managed console sink, so `get_logger()` has nothing to emit through) |
| `test_ac_018_dependency_report_clean` | `tests/contract/logging/test_dependency_contract.py` (new module) | AC-018 / REQ-013 + NFR-004 | `AssertionError` naming four violated dependency-set clauses: loguru still declared, structlog not declared, orjson still `DEP002`-suppressed, no module under `src/` imports orjson |

### Witness design (derived from the spec, not from the current implementation)

- **The all-four witness is AC-009 as the spec states it.** AC-009 names *the four files* and *the 39 statements*; T-004's and T-005's witnesses each cover one feature, so neither alone is the criterion. `_AC_009_STATEMENTS` is REQ-005's own per-file table (17 / 11 / 10 / 1) and `_AC_009_TOTAL_STATEMENTS = 39` is AC-009's own total, so the table cannot silently drift from the spec. The witness reuses `_statement_violations` / `_backend_imports` / `_statement_calls` / `_feature_logger_names` / `_written_via_get_logger` **unchanged** — no per-file witness is rewritten.
- **It deliberately stops at AC-009's scope.** REQ-001's repo-wide half ("no module under `src/` or `tests/` imports one") is AC-001's witness, which is strictly wider than the per-feature directory scans T-004 and T-005 carry; repeating it here would add no gate.
- **AC-001's search is parsed, not grepped.** REQ-001 forbids an *import*, and the repository keeps the removed backend's name in prose (docstrings in `src/backend/logging/_setup.py`, superseded ADR-002's title, this record), so a text search would report false matches forever. The scan walks `ast.Import` / `ast.ImportFrom` over every `.py` under `src/` and `tests/` — both trees, because REQ-001 names both and T-006's design constraint pins the test half of the migration.
- **The search is for the removed backend, not for every third-party logging package.** AC-001 says "an import of the removed logging backend", and REQ-013 names it: loguru. structlog is not a backend in this spec's vocabulary — ADR-082 keeps it as the processor/renderer layer the logging feature itself owns — so a repo-wide structlog ban would be a test that can never go green. The feature-side ban (feature modules import neither loguru nor structlog and call `get_logger()` instead) is exactly what the AC-009 witnesses enforce through `_BACKEND_PACKAGES`.
- **AC-001's second clause is the chain, not the format.** "a record emitted by the feature passes through the standard-library handler chain (a handler attached to the feature logger observes it)": a plain `logging.Handler` is attached to the feature logger (the non-propagating logger owning the managed sinks, D1), one statement is emitted through the public `get_logger()`, and the clause asserts the handler saw a record carrying the message. Format, fields and level are AC-003 / AC-011 / AC-008's territory (T-001's tests) and are not re-asserted.
- **Both AC-001 clauses are collected, not asserted one by one**, so one run names every violated clause. The chain clause's dependency (the managed pipeline, `get_logger()`) does not exist yet, and `pipeline_logger()` / `bound_logger()` report that as an `AssertionError`; collecting it into the violation list keeps the import clause's evidence visible instead of letting a helper error mask it.
- **AC-018 runs the check the repository already gates on.** `uv run deptry .` is part of `quality_check` (`pyproject.toml`) and of the CI quality job, and deptry scans `src/`, `migrations/` and `scripts/` but not `tests/` — so the contract test runs that same checker (`python -m deptry .`, 0.6 s) and asserts its exit status, plus the clauses the checker alone cannot show: loguru absent from `[project].dependencies`, structlog present, and orjson both de-suppressed (`DEP002`) and actually imported under `src/` (the file renderer is what makes it used).
- **The deptry interlock decides where this RED sits.** T-001 declares structlog and de-suppresses orjson in the state it leaves behind, so by the time T-006 runs the open clauses are loguru's removal from the dependency set and the orjson import — which is why the task pairs the last import with the last declaration (S2.1 merged-main fact 1).

### S3.1 T-006 — RED

`uv run pytest tests/acceptance/logging_coverage/test_statements_via_feature.py::test_ac_009_statements_go_through_get_logger tests/acceptance/logging/test_pipeline_backend.py::test_ac_001_no_backend_import_and_stdlib_chain tests/contract/logging/test_dependency_contract.py::test_ac_018_dependency_report_clean -v` → **3 failed, 0 passed** (0.89 s), three `AssertionError`s (no import, collection or test-data error):

```text
AssertionError: AC-009 / REQ-005 (logging-coverage REQ-010 v2): src/backend/settings/registry.py imports a logging backend: ['loguru.logger']; src/backend/settings/registry.py statements not written through get_logger(): line(s) [89, 94, 113, 142, 146, 160, 173, 244, 248, 255, 259, 264, 283, 295, 299, 308, 317]; src/backend/settings/repository.py imports a logging backend: ['loguru.logger']; src/backend/settings/repository.py statements not written through get_logger(): line(s) [140, 151, 154, 156, 248, 259, 262, 264, 281, 284, 286]; src/backend/eventbus/eventbus.py imports a logging backend: ['loguru.logger']; src/backend/eventbus/eventbus.py statements not written through get_logger(): line(s) [86, 96, 115, 120, 136, 176, 197, 205, 222, 233]; src/backend/permissions/service.py imports a logging backend: ['loguru.logger']; src/backend/permissions/service.py statements not written through get_logger(): line(s) [432]
```

```text
AssertionError: AC-001 / REQ-001: 18 module(s) import the removed logging backend: ["src/backend/eventbus/eventbus.py -> ['loguru.logger']", "src/backend/logging/_decorator.py -> ['loguru.logger']", "src/backend/logging/_setup.py -> ['loguru.logger']", "src/backend/logging/feature_settings.py -> ['loguru.logger']", "src/backend/permissions/service.py -> ['loguru.logger']", "src/backend/settings/registry.py -> ['loguru.logger']", "src/backend/settings/repository.py -> ['loguru.logger']", "tests/acceptance/logging/test_logging.py -> ['loguru.logger']", "tests/acceptance/logging_coverage/test_sink_failure.py -> ['loguru.logger']", "tests/conftest.py -> ['loguru.logger']", "tests/contract/logging/test_logging_contracts.py -> ['loguru.logger']", "tests/integration/logging/test_logging_integration.py -> ['loguru.logger']", "tests/logging_coverage_test_helpers.py -> ['loguru.logger']", "tests/logging_test_helpers.py -> ['loguru.logger']", "tests/property/logging_coverage/test_invariants.py -> ['loguru.logger']", "tests/unit/logging/test_logging.py -> ['loguru.logger']", "tests/unit/logging/test_logging_sink_ownership.py -> ['loguru.logger']", "tests/unit/logging_coverage/test_edge_cases.py -> ['loguru.logger']"]; stdlib handler chain: expected exactly one logger owning the managed console sink, found {}
```

```text
AssertionError: AC-018 / NFR-004 (REQ-013): loguru is still declared in [project].dependencies; structlog is not declared in [project].dependencies; orjson is still suppressed as an unused dependency (DEP002); no module under src/ imports orjson, so it is unused
```

Failure mode per test: **assertion on unimplemented behaviour** in all three. AC-009 names 17 + 11 + 10 + 1 = 39 statement line numbers and contributes no count violation (the counts already match REQ-005), so it is red exactly on the migration. AC-001 is red on both clauses — 18 importing modules, and no managed pipeline for the chain clause. AC-018 is red on four clauses; its deptry-run clause already holds (the check is clean at HEAD: "Success! No dependency issues found."), which is the honest shape — the contract is about the dependency *set*, not about the checker being broken.

Test-contract fix inside this step: the first draft of the all-four witness built `violations` as a list of lists, so the gate raised `TypeError: sequence item 0: expected str instance, list found` — a test-contract bug, not a RED. Flattened and re-checked in the same execution; the quoted AC-009 message is the corrected run.

Neighbours (no collateral): the same three directories at HEAD `1e1ec3b` (the two modified files stashed, the new module moved aside) → **17 failed, 20 passed**; with T-006's tests in place → **20 failed, 20 passed** — exactly +3 failures, all three new, and no previously-green test changed state.

### Gate table (S3.1, T-006)

| Gate | Command | Result |
|---|---|---|
| Pre-flight collection | `uv run pytest --collect-only -q <the three files>` | the three `tests_to_create` names are absent at HEAD `1e1ec3b` (`git show HEAD:<path>` greps → `0`, `0`; the contract module is not in `HEAD`) |
| Post-flight collection | same command | clean — **7 tests collected, 0 errors** |
| Ruff (changed paths) | `uv run ruff check tests/acceptance/logging_coverage/test_statements_via_feature.py tests/acceptance/logging/test_pipeline_backend.py tests/contract/logging/test_dependency_contract.py` | **All checks passed** |
| Format | `uv run ruff format <the same three paths>` | **1 file reformatted, 2 files left unchanged**; ruff re-checked after formatting: **All checks passed** |
| RED (T-006 `red_command`) | the command quoted above | **3 failed, 0 passed** — three assertion failures, messages quoted above |
| Test contract / test-data validity | failure output | no `ValidationError` / `ValueError`, no fixture or collection error; the one `TypeError` of the first draft was fixed and re-run (see above) |
| Traceability referential integrity | `uv run python scripts/check_traceability.py` | **PASS** (765 matrix rows, 129 spec IDs, 744 test functions) — the AC-001 / AC-009 / AC-018 matrix rows are S3.2's; the retired `logging-coverage` REQ-010 / AC-010 row is re-pointed in T-006's implementation |
| No implementation code written | `git status --short -- src pyproject.toml uv.lock migrations` | empty |

**Phase 3 (S3.1, T-006) gate: PASS.** Next: S3.1 for T-007.

---

## Phase 3 (S3.1) — T-007 test derivation (2026-10-06)

Task **T-007 — rewrite the agent-facing logging guidance to the new surface** (`AGENTS.md` "Using the Logging Feature" + the tooling line, and the `python-best-practices` skill's logging entry point) (REQ-014; AC-019; Impact Analysis row 7 — guidance: `AGENTS.md` + 3 skill reference files). Its single `tests_to_create` function exists in the DAG's path, in the module T-006 created.

### Tests created

| Test | File | Requirement | Expected failure mode (RED) |
|---|---|---|---|
| `test_ac_019_guidance_names_feature_entry_points` | `tests/contract/logging/test_dependency_contract.py` (appended; T-006's `test_ac_018_dependency_report_clean` untouched) | AC-019 / REQ-014 | `AssertionError` naming 24 violated clauses with file and line: `loguru` named twice on `AGENTS.md:769` and once on `:771`; `context_getter` and `depth` named on `:767`; `get_logger` absent from `AGENTS.md`; three `setup_logger(…)` call shapes the amended signature rejects (`:765`, `:771`, `:776`); the four entry points absent from `SKILL.md` and from `modern-python.md`; three entry points absent from `errors-and-resources.md`, plus its four backend entry points (`import structlog` / `structlog.get_logger` at `:17`, `:19`, `:43`, `:45`) |

### Witness design (derived from the spec, not from the current guidance text)

- **The file set is REQ-014's own list, verbatim** — `AGENTS.md`, `.agents/skills/python-best-practices/SKILL.md`, `references/modern-python.md`, `references/errors-and-resources.md`. The scan is deliberately narrowed to those four rather than to the whole skill directory: T-007's design constraint is "no other guidance file changes", and the other five skill files carry no logging reference, so a directory-wide scan would demand entry points from files the change is forbidden to touch — a test that cannot go green.
- **The forbidden tokens come from the spec, not from the text it judges.** `loguru` is the removed backend named by REQ-013 / NFR-004 (the module's existing `_REMOVED_BACKEND` constant, reused unchanged); `context_getter` and `depth` are the parameters REQ-007 removes and REQ-015 states have no compatibility shim. Both are matched as whole words, so the failure names the exact line that names them.
- **The required names are §3 / REQ-015's public surface** — `setup_logger`, `logged`, `logged_class`, `get_logger` — the parenthesised list AC-019 itself gives, applied per file ("**each** names the shared logging feature's own entry points"). Word-boundary matching keeps the four independent: `\blogged\b` does not match `logged_class`, so a file naming only the class decorator is not credited with the function decorator.
- **A name check alone would not close AC-019's third clause, so the backend-entry-point clause is part of it.** `errors-and-resources.md` already contains the string `get_logger` — as `structlog.get_logger()` — so a pure presence check would go green while the guidance still shows the backend's entry point, which is exactly the defect T-007's inputs name ("direct backend entry point in the skill files"). The clause bans an import of the backend/processor layer or a call through it (`import structlog`, `structlog.get_logger`, `loguru.logger`, …), per the DAG's own rationale that REQ-005 forbids a direct backend import even in guidance. structlog is *not* the removed backend (ADR-082 keeps it as the processor/renderer layer), so naming it as a library stays legal — only importing it or calling through it is a defect.
- **The fourth clause is checked against the amended signature, not against the old call.** §3 fixes `setup_logger(*, renderer: str | None = None)`, so an accepted call is no argument at all or a single keyword-only `renderer` (`renderer="json"`, `renderer=…`); a positional argument, a `Settings` object, or more than one argument is a violation. The argument text is captured by a paren-balancing scan, so the rejected `setup_logger(Settings(log_level="INFO"))` shape is reported whole rather than truncated at its inner paren.
- **Every clause is collected, not asserted one by one**, and each violation string carries `file:line`, so one run names every defect class in all four files and the implementation step can work down the list (same shape as the T-004 / T-005 / T-006 witnesses).
- **Known ceiling, recorded deliberately:** `depth` is matched as a whole word because AC-019 reads "none names `context_getter` or `depth`". If future guidance ever needs the word in another sense, that is a spec-amendment conversation, not a test weakening.
- **No behavioural duplicate.** The surface the guidance describes is asserted by AC-020 (`test_ac_020_public_export_surface`, T-002) and the accepted call shape by AC-010 / EDGE-005 (T-001); this witness asserts only what the *documents* say, which no runtime test can reach.
- **Nothing of T-006's is rewritten** — `_REPO_ROOT`, `_REMOVED_BACKEND` and `_PROCESSOR_LAYER` are reused; `test_ac_018_dependency_report_clean` and its helpers are untouched.

### S3.1 T-007 — RED

`uv run pytest tests/contract/logging/test_dependency_contract.py::test_ac_019_guidance_names_feature_entry_points -v` → **1 failed, 0 passed** (0.31 s), one `AssertionError` (no import, collection or test-data error):

```text
AssertionError: AC-019 / REQ-014: AGENTS.md:769 names the removed backend 'loguru'; AGENTS.md:769 names the removed backend 'loguru'; AGENTS.md:771 names the removed backend 'loguru'; AGENTS.md:767 names the removed parameter 'context_getter'; AGENTS.md:767 names the removed parameter 'depth'; AGENTS.md does not name the feature entry point 'get_logger'; AGENTS.md:765 shows setup_logger(settings), a call the amended signature rejects; AGENTS.md:771 shows setup_logger(Settings(...)), a call the amended signature rejects; AGENTS.md:776 shows setup_logger(Settings(log_level="INFO")), a call the amended signature rejects; .agents/skills/python-best-practices/SKILL.md does not name the feature entry point 'setup_logger'; … 'logged'; … 'logged_class'; … 'get_logger'; .agents/skills/python-best-practices/references/modern-python.md does not name the feature entry point 'setup_logger'; … 'logged'; … 'logged_class'; … 'get_logger'; .agents/skills/python-best-practices/references/errors-and-resources.md does not name the feature entry point 'setup_logger'; … 'logged'; … 'logged_class'; .agents/skills/python-best-practices/references/errors-and-resources.md:17 shows the backend entry point 'import structlog'; …:19 shows the backend entry point 'structlog.get_logger'; …:43 shows the backend entry point 'import structlog'; …:45 shows the backend entry point 'structlog.get_logger'
```

(Elided with `…` for width only — the run prints all 24 violation strings in full.)

Failure mode: **assertion on uncorrected guidance** — all three REQ-014 defect classes are represented (removed backend, removed parameters, rejected `setup_logger(Settings(…))` shape), plus the missing entry points and the backend entry point in the skill examples. The witness reads only guidance text, builds no model instance and touches no `src/` file.

Neighbours (no collateral): `uv run pytest tests/contract/logging -q` at HEAD `d52e821` with the modified file stashed → **5 failed, 2 passed**; with T-007's test in place → **6 failed, 2 passed** — exactly +1 failure, the new one, and no previously-green test changed state.

### Gate table (S3.1, T-007)

| Gate | Command | Result |
|---|---|---|
| Pre-flight collection | `git show HEAD:tests/contract/logging/test_dependency_contract.py` grepped for `test_ac_019_guidance_names_feature_entry_points` | **0** — T-007's `tests_to_create` name absent at HEAD `d52e821` |
| Post-flight collection | `uv run pytest --collect-only -q tests/contract/logging/test_dependency_contract.py` | clean — **2 tests collected, 0 errors** |
| Ruff (changed path) | `uv run ruff check tests/contract/logging/test_dependency_contract.py` | **All checks passed** |
| Format | `uv run ruff format tests/contract/logging/test_dependency_contract.py` | **1 file left unchanged** |
| RED (T-007 `red_command`) | `uv run pytest tests/contract/logging/test_dependency_contract.py::test_ac_019_guidance_names_feature_entry_points -v` | **1 failed, 0 passed** — assertion failure, message quoted above |
| Test contract / test-data validity | failure output | no `ValidationError` / `ValueError`, no fixture or collection error; the witness builds no model instance and runs no subprocess |
| Guidance files untouched (Phase 4 scope) | `git status --short -- AGENTS.md .agents` | empty — the test only reads them |
| Traceability referential integrity | `uv run python scripts/check_traceability.py` | **PASS** (765 matrix rows, 129 spec IDs, 745 test functions) — the AC-019 matrix row itself is S3.2's |
| No implementation code written | `git status --short -- src pyproject.toml uv.lock migrations` | empty |

**Phase 3 (S3.1, T-007) gate: PASS.** Next: S3.2 (ruff + confirm RED across all derived tests + traceability rows).

---

## Phase 3 gate (S3.2) — RED confirmed for T-001..T-007 (2026-10-06)

Inputs: the tests derived by S3.1 for all seven DAG tasks — T-001 `fcce934`, T-002 `d82cc1e`, T-003 `f2490a0`, T-004 `28d3d40`, T-005 `1e1ec3b`, T-006 `d52e821`, T-007 `cc7894f` — observed at HEAD `cc7894f`. This step wrote no `src/`, `pyproject.toml` or `uv.lock` change and modified no test assertion.

### Ruff on every path Phase 3 wrote

Path list derived with `git diff --name-only main...HEAD -- tests/` — 23 files:

```text
tests/acceptance/logging/test_get_logger.py
tests/acceptance/logging/test_logging.py
tests/acceptance/logging/test_pipeline_backend.py
tests/acceptance/logging/test_renderer.py
tests/acceptance/logging/test_secrets.py
tests/acceptance/logging/test_third_party_records.py
tests/acceptance/logging/test_tracing_records.py
tests/acceptance/logging_coverage/test_sink_failure.py
tests/acceptance/logging_coverage/test_statements_via_feature.py
tests/acceptance/settings_coverage/test_setup_logger.py
tests/contract/logging/test_dependency_contract.py
tests/contract/logging/test_logging_contracts.py
tests/contract/logging/test_tracing_surface.py
tests/integration/logging/test_external_reconfiguration.py
tests/logging_test_helpers.py
tests/property/logging/test_logging_properties.py
tests/property/logging/test_pipeline_invariants.py
tests/unit/logging/test_logging.py
tests/unit/logging/test_logging_edges.py
tests/unit/logging/test_pipeline_edges.py
tests/unit/logging/test_sink_ownership.py
tests/unit/logging/test_third_party_records.py
tests/unit/test_settings_coverage.py
```

| Gate | Command | Result |
|---|---|---|
| Lint (changed paths) | `uv run ruff check <the 23 paths above>` | **All checks passed!** |
| Format (changed paths) | `uv run ruff format --check <the 23 paths above>` | **23 files already formatted** — no formatting fix was needed, so no test file was rewritten by this step |
| Pre-flight collection | `uv run pytest --collect-only -q tests/acceptance/logging tests/acceptance/logging_coverage tests/acceptance/settings_coverage tests/contract/logging tests/property/logging tests/unit/logging tests/unit tests/unit/test_settings_coverage.py tests/integration/logging` | **117 tests collected in 0.46 s, 0 errors** — no import/collection blocker |
| Working tree before the step | `git status --short` | clean (HEAD `cc7894f`) |

### Per-task RED gate (the DAG's own `red_command`, verbatim)

Each command is copied verbatim from `.github/task-runner/tasks.json` and was run one by one in the change worktree.

**T-001** — backend.logging (owner) + tooling (pyproject.toml dependency set, part 1)

```text
uv run pytest tests/acceptance/logging/test_pipeline_backend.py::test_ac_002_two_managed_handlers tests/acceptance/logging/test_third_party_records.py::test_ac_006_third_party_reaches_both_sinks tests/acceptance/logging/test_get_logger.py::test_ac_008_get_logger_emits_to_sinks tests/acceptance/logging/test_renderer.py::test_ac_010_renderer_selection tests/acceptance/logging_coverage/test_sink_failure.py::test_ac_016_call_unaffected_by_failing_file_sink tests/unit/logging/test_sink_ownership.py::test_ac_004_foreign_handlers_untouched tests/unit/logging/test_sink_ownership.py::test_ac_005_no_duplicate_records tests/unit/logging/test_third_party_records.py::test_ac_007_location_of_emitting_call tests/unit/logging/test_pipeline_edges.py tests/integration/logging/test_external_reconfiguration.py tests/property/logging/test_pipeline_invariants.py::test_inv_001_concurrent_setup_owns_two_handlers tests/property/logging/test_pipeline_invariants.py::test_inv_004_other_loggers_untouched tests/contract/logging/test_tracing_surface.py::test_ac_020_public_export_surface tests/acceptance/logging/test_logging.py::test_ac_001_setup_logger_adds_sinks tests/unit/logging/test_logging.py::test_ac_004_intercept_handler_routes_records tests/property/logging/test_logging_properties.py::test_inv_001_concurrent_setup_logger_sinks tests/contract/logging/test_logging_contracts.py::test_nfr_001_setup_time_budget -v
```
→ **20 failed, 2 passed (19.20 s)** — RED observed.
- failure mode (test contract sanity check): 20 `AssertionError`s, 0 collection/fixture/import errors. Two failures (`test_ac_010_renderer_selection`, `test_edge_006_get_logger_before_setup`) run their witness in a subprocess that dies with `ImportError: cannot import name 'get_logger' from 'backend.logging'` — the unimplemented export surfacing **inside** the witness; the test itself crashes on `AssertionError` (`renderer='json': setup or emit failed:` / `EDGE-006: using get_logger() before setup must not raise:`), re-checked with `--tb=line`. `test_inv_004_other_loggers_untouched` fails on the helper's explicit `raise AssertionError("expected exactly one logger owning the managed console sink, found {}")`.
- already green at the RED gate: `test_ac_004_foreign_handlers_untouched`, `test_nfr_001_setup_time_budget`

**T-002** — backend.logging (owner)

```text
uv run pytest tests/acceptance/logging/test_tracing_records.py tests/acceptance/logging/test_secrets.py tests/acceptance/logging/test_pipeline_backend.py::test_ac_003_file_record_fields_as_json tests/contract/logging/test_tracing_surface.py::test_ac_013_removed_parameters tests/property/logging/test_pipeline_invariants.py::test_inv_002_no_local_value_ever_recorded tests/property/logging/test_pipeline_invariants.py::test_inv_003_elapsed_non_negative tests/property/logging/test_pipeline_invariants.py::test_inv_005_required_fields_present tests/contract/logging/test_logging_contracts.py::test_nfr_002_decorator_overhead_budget tests/contract/logging/test_logging_contracts.py::test_nfr_004_backward_compatible_api -v
```
→ **11 failed, 0 passed (75.43 s)** — RED observed.
- failure mode (test contract sanity check): 11 `AssertionError`s, 0 errors. The one `ValueError` string in the log is the test's own propagation probe (`ac_012_boom raised ValueError(ac_012 exception propagation probe)`) that AC-012 requires to propagate — not a test-data error.
- already green at the RED gate: none

**T-003** — backend.settings (amended settings-coverage IDs; the reconfigure code lives in the logging feature's _setup.py)

```text
uv run pytest tests/acceptance/settings_coverage/test_setup_logger.py tests/unit/test_settings_coverage.py::test_logging_stub_removed tests/unit/test_settings_coverage.py::test_sink_reconfigured_rotation tests/unit/test_settings_coverage.py::test_observability_tracing -v
```
→ **5 failed, 1 passed (15.75 s)** — RED observed.
- failure mode (test contract sanity check): 5 `AssertionError`s, 0 errors.
- already green at the RED gate: `test_logging_stub_removed` (settings-coverage AC-021, re-derived and already holding)

**T-004** — backend.settings

```text
uv run pytest tests/acceptance/logging_coverage/test_statements_via_feature.py::test_ac_009_settings_statements_go_through_get_logger -v
```
→ **1 failed, 0 passed (0.33 s)** — RED observed.
- failure mode (test contract sanity check): 1 `AssertionError` (the settings feature's statements are not written through `backend.logging.get_logger()`), 0 errors.
- already green at the RED gate: none

**T-005** — backend.eventbus

```text
uv run pytest tests/acceptance/logging_coverage/test_statements_via_feature.py::test_ac_009_eventbus_statements_go_through_get_logger -v
```
→ **1 failed, 0 passed (0.31 s)** — RED observed.
- failure mode (test contract sanity check): 1 `AssertionError` (the event bus feature's statements are not written through `get_logger()`), 0 errors.
- already green at the RED gate: none

**T-006** — backend.permissions + tooling (pyproject.toml dependency set, part 2 - the deptry interlock)

```text
uv run pytest tests/acceptance/logging_coverage/test_statements_via_feature.py::test_ac_009_statements_go_through_get_logger tests/acceptance/logging/test_pipeline_backend.py::test_ac_001_no_backend_import_and_stdlib_chain tests/contract/logging/test_dependency_contract.py::test_ac_018_dependency_report_clean -v
```
→ **3 failed, 0 passed (0.87 s)** — RED observed.
- failure mode (test contract sanity check): 3 `AssertionError`s (dependency report still names the removed backend; the all-four witness statement test; the no-backend-import chain test), 0 errors.
- already green at the RED gate: none

**T-007** — guidance (AGENTS.md + .agents/skills/python-best-practices/)

```text
uv run pytest tests/contract/logging/test_dependency_contract.py::test_ac_019_guidance_names_feature_entry_points -v
```
→ **1 failed, 0 passed (0.31 s)** — RED observed.
- failure mode (test contract sanity check): 1 `AssertionError` naming 24 violated guidance clauses, 0 errors.
- already green at the RED gate: none

### Directory-level counts (before / after)

Identical command in both worktrees: `uv run pytest tests/acceptance/logging tests/acceptance/logging_coverage tests/acceptance/settings_coverage tests/contract/logging tests/property/logging tests/unit/logging tests/unit -q --tb=line -rf`

| Worktree | Revision | Result |
|---|---|---|
| primary (`main`) | `cb5d92f` | **271 passed, 0 failed** (35.54 s) — the before-number |
| change worktree | `cc7894f` | **41 failed, 261 passed** (138.93 s) — the after-number |
| collection | `cb5d92f` → `cc7894f` | 271 → **302** collected: **+33** new test functions, **−2** deleted (`test_ac_005_intercept_handler_skips_bootstrap`, `test_edge_005_intercept_unknown_level` — the two per-ID deletions authorized by the merged `logging.md` v3 amendment and named in spec §11) |

**No previously-green test flipped to red.** The 41 failures decompose as:

- **32** are new test functions (absent from `main`'s collection);
- **9** exist on `main` and were green there — every one is a test this change **re-derived from an amended spec ID**, in a file the change modified:

| Flipped test | Amended ID it was re-derived from |
|---|---|
| `tests/acceptance/logging/test_logging.py::test_ac_001_setup_logger_adds_sinks` | `logging.md` AC-001 |
| `tests/unit/logging/test_logging.py::test_ac_004_intercept_handler_routes_records` | `logging.md` AC-004 |
| `tests/property/logging/test_logging_properties.py::test_inv_001_concurrent_setup_logger_sinks` | `logging.md` INV-001 |
| `tests/contract/logging/test_logging_contracts.py::test_nfr_002_decorator_overhead_budget` | `logging.md` NFR-002 |
| `tests/contract/logging/test_logging_contracts.py::test_nfr_004_backward_compatible_api` | `logging.md` REQ-005 / NFR-004 |
| `tests/acceptance/settings_coverage/test_setup_logger.py::test_setup_logger_reads_registry` | `settings-coverage.md` AC-019 / REQ-014 |
| `tests/acceptance/settings_coverage/test_setup_logger.py::test_sink_reconfigured_on_change` | `settings-coverage.md` AC-020 / REQ-015 |
| `tests/unit/test_settings_coverage.py::test_sink_reconfigured_rotation` | `settings-coverage.md` EDGE-008 |
| `tests/unit/test_settings_coverage.py::test_observability_tracing` | `settings.md` §9 (no ID) |

- **0** failures in a file the change did not touch — the failed node IDs were cross-checked against `git diff --name-only main...HEAD -- tests/`: no collateral damage to any untouched test.

### Test-data validity (AGENTS.md Phase 3 item 6)

No failing test fails with a `ValidationError` / `ValueError` from constructing test data. Across the seven task logs and the directory run, the only exception type reported at test level is `AssertionError` (82 occurrences in the directory run, 0 of any other type). The `ImportError` / `ValueError` strings that appear in the T-001 and T-002 logs are (a) inside the repr of a subprocess the witness itself spawns — the missing `get_logger` export, i.e. the unimplemented behavior — and (b) the test's own deliberate propagation probe `ac_012_boom raised ValueError(...)`. No fixture builds a model instance out of domain; no fixture or collection error occurred. Nothing had to be fixed, so this step changed no test data and no assertion.

### Traceability matrix

`docs/verification/traceability.md` § *Structlog Logging Matrix*: the 18 `PENDING` rows recorded at P.4 were replaced by **37 rows** (one per REQ/AC pair, plus the INV / EDGE / NFR rows), each citing the concrete test function that now exists, with `RED` status and `structlog-logging S3.2, 2026-10-06` inside the cell — except the three witnesses that already hold at the RED gate (`test_ac_004_foreign_handlers_untouched`, `test_nfr_001_setup_time_budget`, and the re-derived `test_logging_stub_removed`), recorded `GREEN` as observed (convention B: a row records the gate as observed). Amended rows updated in place: `logging-coverage` REQ-010 / AC-010 (superseded by this change's AC-009 witness; the direct-backend witness is deleted in the implementation PR), and `settings-coverage` REQ-014/AC-019, REQ-015/AC-020, REQ-016/AC-021, EDGE-008, NFR-004. Net matrix change: **765 → 784 rows (+19)**.

```text
Traceability: PASS (784 matrix rows, 129 spec IDs, 745 test functions)
```

### Gate table (S3.2)

| Gate | Command | Result |
|---|---|---|
| Ruff lint, 23 phase paths | `uv run ruff check <paths>` | **All checks passed!** |
| Ruff format, 23 phase paths | `uv run ruff format --check <paths>` | **23 files already formatted** |
| Collection clean | `uv run pytest --collect-only -q <affected dirs>` | **117 collected, 0 errors** |
| RED, T-001 | its `red_command` | **20 failed, 2 passed** — all assertion failures |
| RED, T-002 | its `red_command` | **11 failed, 0 passed** — all assertion failures |
| RED, T-003 | its `red_command` | **5 failed, 1 passed** — all assertion failures |
| RED, T-004 | its `red_command` | **1 failed, 0 passed** — assertion failure |
| RED, T-005 | its `red_command` | **1 failed, 0 passed** — assertion failure |
| RED, T-006 | its `red_command` | **3 failed, 0 passed** — all assertion failures |
| RED, T-007 | its `red_command` | **1 failed, 0 passed** — assertion failure |
| Directory run (after) | `uv run pytest <affected dirs> -q --tb=line -rf` | **41 failed, 261 passed** |
| Directory run (before, `main`) | same command in the primary worktree | **271 passed, 0 failed** |
| No green test flipped | failed node IDs × `main` collection × the phase path list | 32 new + 9 intentional re-derivations, **0 in an untouched file** |
| Test-data validity | failure output of all 41 failures | only `AssertionError` at test level; no `ValidationError` / `ValueError`, no fixture or collection error |
| Traceability referential integrity | `uv run python scripts/check_traceability.py` | **PASS** (784 matrix rows, 129 spec IDs, 745 test functions) |
| No implementation code written | `git status --short -- src pyproject.toml uv.lock migrations` | empty |

**Phase 3 (S3.2) gate: PASS — RED observed for T-001..T-007.** Next: Phase 4, S4.1 (T-001).

---

## Phase 4 (S4.1) — T-001 picked, RED re-confirmed (2026-10-06)

**Task picked: T-001** — *pipeline core: dedicated non-propagating feature logger owning two managed stdlib sinks (colorized text console + queue-fed rotating JSON file via orjson), root forwarding handler, renderer selection, `get_logger()`, public export surface; declare structlog and retire the orjson DEP002 suppression*.

### Readiness check

| Check | Evidence | Result |
|---|---|---|
| Only ready task | `dependencies: []` for T-001; T-002..T-007 all list `T-001` (T-003 also `T-002`) in `.github/task-runner/tasks.json` | T-001 is the only unblocked task |
| Status still `PENDING` | `.github/task-runner/tasks.json` → `"status": "PENDING"` for T-001 | confirmed |
| Its tests exist | derived at `fcce934` ("S3.1 T-001 pipeline-core tests (+2 authorized per-ID deletions)"), present at HEAD `aba98f8`; the two authorized deletions (`test_ac_005_intercept_handler_skips_bootstrap`, `test_edge_005_intercept_unknown_level`) are already absent from `tests/` | confirmed |
| Working tree | `git status --short` clean at `aba98f8` | confirmed |

### RED re-confirmed (the DAG's own `red_command`, verbatim)

```text
uv run pytest tests/acceptance/logging/test_pipeline_backend.py::test_ac_002_two_managed_handlers tests/acceptance/logging/test_third_party_records.py::test_ac_006_third_party_reaches_both_sinks tests/acceptance/logging/test_get_logger.py::test_ac_008_get_logger_emits_to_sinks tests/acceptance/logging/test_renderer.py::test_ac_010_renderer_selection tests/acceptance/logging_coverage/test_sink_failure.py::test_ac_016_call_unaffected_by_failing_file_sink tests/unit/logging/test_sink_ownership.py::test_ac_004_foreign_handlers_untouched tests/unit/logging/test_sink_ownership.py::test_ac_005_no_duplicate_records tests/unit/logging/test_third_party_records.py::test_ac_007_location_of_emitting_call tests/unit/logging/test_pipeline_edges.py tests/integration/logging/test_external_reconfiguration.py tests/property/logging/test_pipeline_invariants.py::test_inv_001_concurrent_setup_owns_two_handlers tests/property/logging/test_pipeline_invariants.py::test_inv_004_other_loggers_untouched tests/contract/logging/test_tracing_surface.py::test_ac_020_public_export_surface tests/acceptance/logging/test_logging.py::test_ac_001_setup_logger_adds_sinks tests/unit/logging/test_logging.py::test_ac_004_intercept_handler_routes_records tests/property/logging/test_logging_properties.py::test_inv_001_concurrent_setup_logger_sinks tests/contract/logging/test_logging_contracts.py::test_nfr_001_setup_time_budget -v
```

→ **20 failed, 2 passed (19.49 s)** at HEAD `aba98f8` — **identical to the S3.2 gate (20 failed / 2 passed)**; no drift between Phase 3 and Phase 4 entry. 22 items collected, 0 collection/fixture/import errors, every failure an `AssertionError` on unimplemented behavior (the two subprocess witnesses die with `ImportError: cannot import name 'get_logger' from 'backend.logging'` *inside* the subprocess and the test itself asserts).

Already green at the RED gate (unchanged from S3.2, expected-GREEN guards, not a missing RED): `tests/unit/logging/test_sink_ownership.py::test_ac_004_foreign_handlers_untouched` (INV-004/AC-004 ownership regression guard) and `tests/contract/logging/test_logging_contracts.py::test_nfr_001_setup_time_budget` (the < 25 ms ceiling; it must **stay** green after the rebuild).

### Scope the implementation step may touch (`allowed_files.source_files`)

```text
src/backend/logging/_setup.py
src/backend/logging/__init__.py
src/backend/logging/feature_settings.py
src/backend/logging/_pipeline.py      (new; the module split inside src/backend/logging/ is the implementer's choice, no new package)
src/backend/logging/_renderers.py     (new; same note)
pyproject.toml                        (dependencies + [tool.deptry.per_rule_ignores] DEP002 only)
uv.lock
```

Test paths it may also touch are the 20 entries in T-001's `allowed_files.test_files` (notably `tests/logging_test_helpers.py`, `tests/unit/logging/test_logging_sink_ownership.py`, `tests/integration/logging/test_logging_integration.py`, `tests/unit/logging/test_logging.py`). `_decorator.py` is **not** in T-001's file set — the tracing decorators stay loguru-based until T-002.

### Completion gates (T-001, verbatim from the DAG)

1. RED observed on the `red_command` set before implementation; recorded here. **← this step**
2. AC-002, AC-004, AC-005, AC-006, AC-007, AC-008, AC-010, AC-016, AC-020 tests pass.
3. Property tests for INV-001 (concurrent setup owns exactly two handlers) and INV-004 (other loggers untouched) pass.
4. Unit/integration tests for EDGE-001…EDGE-006 and NFR-005 pass.
5. Contract gate NFR-001: `setup_logger()` < 25 ms (median of 3 fresh processes).
6. `uv run deptry .` clean in the state this task leaves behind (structlog declared + imported; orjson declared, imported, no longer in DEP002; loguru still declared and still imported by the three not-yet-migrated feature files).
7. `uv run ruff check <changed paths>` / `uv run ruff format <changed paths>` clean; `uv run mypy src/` clean.
8. `uv run python scripts/check_traceability.py` stays green.
9. Both authorized deletions recorded here (done at S3.1, § *Authorized per-ID deletions*).

### Implementation risk notes for S4.2 (read from the current `src/backend/logging/` against spec §2–§8)

**A. What must exist for the 20 red tests to go green** — the observable contract the helpers in `tests/logging_test_helpers.py` enforce (they locate the pipeline through public `logging` machinery only, so the implementation is free internally):

- Exactly **one non-root logger** in `logging.Logger.manager.loggerDict` owns a `StreamHandler` whose stream is `sys.stderr` or fd 2 (`pipeline_logger()` / `_is_console_handler`); that logger owns **exactly `MANAGED_HANDLER_COUNT` = 2 handlers**, one console + one `QueueHandler` **or** `RotatingFileHandler` (`managed_sinks()`). The rotating handler is found by `gc` scan (`rotating_file_handlers()`), i.e. D4 may attach it to the listener, not the logger — but its `maxBytes == log_max_bytes`, `backupCount == log_backup_count`, `encoding == "utf-8"` are read from the handler itself (AC-002).
- The feature logger must **not propagate** (AC-005: one record, exactly once per sink).
- One **forwarding handler on the root logger** hands foreign records to the two managed handlers with level, logger name and `file`/`line` of the *emitting* call intact (AC-006, AC-007, EDGE-004 — the numeric level survives, no `_LEVEL_NAMES` mapping).
- File records are **one JSON object per line** with the §3 field names (`level`, `logger`, `event`, `timestamp`, `file`, `line`) and never `filename`/`lineno` or the formatter's bookkeeping keys; console records are human-readable text, not JSON (AC-010 selects the pair: `renderer="json"` → JSON console, `renderer="text"` → text file, no argument → text console + JSON file).
- `setup_logger(*, renderer: str | None = None)` must **accept the keyword** (`inspect.signature` is asserted in `test_edge_005_unknown_renderer`) and raise `ValueError` **before** installing anything; setup stays idempotent + thread-safe + settings-driven with no argument.
- `get_logger(name=None)` must be **exported from `backend.logging`** and usable **before** `setup_logger()` without raising (EDGE-006); the export set must be exactly §3's eight names (AC-020) — `setup_logger`, `logged`, `logged_class`, `get_logger`, `Settings`, `get_settings`, `register_settings`, `_read_setting`.
- A `QueueHandler` must be discoverable among all loggers' handlers (`test_nfr_005_single_listener_thread` counts them and asserts setup adds **at most one thread** and emitting adds none).
- EDGE-001: the log file's parent directory is created; EDGE-002: rotation with an open handle produces a backup file matching the log-path glob, every probe record present, and **no `--- Logging error ---`** on the subprocess stderr (the stdlib swallows handler errors through `Handler.handleError`, so a non-zero returncode proves nothing).
- EDGE-003 (`tests/integration/logging/test_external_reconfiguration.py`): after a `logging.config.fileConfig(..., disable_existing_loggers=True)` replay, the two managed handlers survive on the feature logger, a later `logging.*` change **re-enables the feature's own logger and re-installs the root forwarding handler**, and a foreign logger disabled by `fileConfig` stays disabled. `migrations/env.py` is not touched; the autouse `tests/conftest.py::_stdlib_root_logging_restored` fixture stays.
- AC-016 sabotages both the `QueueHandler` (raises in the caller's thread) and the rotating handler (raises on the listener thread) — the implementation must not let either escape the traced call, and must keep the console sink live.
- ADR-082's six pinned structlog-26 facts are binding (do not re-discover them): `serializer=` is the JSON renderer option; the serializer returns **bytes** (adapter must decode to `str` and tolerate the renderer's forwarded kwargs); the formatter injects two bookkeeping keys nothing strips by default (a processor must drop them); the stdlib `QueueHandler` **formats while enqueueing** — override `prepare()` to pass the record through unformatted; the callsite step must run at the emitting call site (inside the formatter chain it resolves in the listener thread) and names its fields `filename`/`lineno`, which the feature maps to `file`/`line`; `log.exception()` puts the exception on the record, not the event dict — render it into `exception` and suppress the stdlib's own exception formatting so a JSON record stays one line.

**B. Pre-existing tests inside T-001's `green_command` that are GREEN today and will flip when the loguru pipeline is removed** (all in `allowed_files.test_files`; the current `green_command` baseline is **22 failed / 26 passed**):

| Test | Why it breaks | Adaptation |
|---|---|---|
| `tests/unit/logging/test_logging_sink_ownership.py` (all 3) | walks `logger._core.handlers` and matches loguru sink class names `StreamSink` / `FileSink` | re-express against the two stdlib managed handlers (the settings-coverage REQ-015/AC-020 semantics it guards stay) |
| `tests/unit/logging/test_logging.py::test_ac_003_setup_logger_thread_safe` | asserts `len(logger._core.handlers) == _EXPECTED_HANDLER_COUNT` | re-express as INV-001-style handler ownership on the feature logger |
| `tests/integration/logging/test_logging_integration.py::test_stdlib_loguru_decorator_pipeline` | emits a raw `loguru.logger.info` line and asserts loguru's `<<` marker in the file | see risk note D — its traced-call clause is a T-002 dependency |
| `tests/acceptance/logging/test_logging.py::test_ac_002_setup_logger_idempotent` | compares `len(logger._core.handlers)` before/after — stays vacuously true (0 == 0), but the module keeps `from loguru import logger` | drop the loguru import (T-006's AC-001 search covers `tests/` too) |
| `tests/unit/logging/test_logging_edges.py::test_edge_001_log_file_parent_created` | subprocess only asserts the file exists — expected to survive | no change expected |

**Still safe in the T-001 intermediate state** (because `_decorator.py` keeps emitting through loguru and `log_records` / `capture_records` install their **own** loguru sink): the `log_records`-based decorator tests — `tests/unit/logging/test_logging.py::test_ac_006…test_ac_013`, `tests/unit/logging/test_logging_edges.py::test_edge_002/003`, `tests/property/logging/test_logging_properties.py::test_inv_002/003`, and the whole `logging_coverage` suite plus the cross-feature `log_records` users (27 modules). They break in **T-002**, not here. Do **not** re-implement `capture_records` / `log_records` in T-001.

**C. Helper interlock.** `tests/logging_test_helpers.py` keeps two loguru-era helpers that T-001 must re-implement with the same public signatures (implementation step 10): `_console_sink_fd()` (walks `logger._core.handlers` — dead once no loguru sink is installed) and `wait_for_file_content()` (drains via `logger.complete()` — a no-op once the file sink is the stdlib listener, so the flush must come from the `QueueListener`). `captured_stderr()` is used only inside that module (measured: no other test imports it), so its blast radius is small; `wait_for_file_content` has two external users — `tests/integration/logging/test_logging_integration.py` and `tests/contract/logging/test_logging_contracts.py` (the NFR contract file; only `test_nfr_001_setup_time_budget` is in T-001's gate, `test_nfr_003_diagnose_false` drives loguru's `logger.exception` and is T-002's problem). New-era helpers (`managed_sinks`, `pipeline_logger`, `captured_console`, `json_records`, `wait_for_record`, `bound_logger`, `rotating_file_handlers`) already exist and are what the T-001 tests use.

**D. Gate conflict to resolve before S4.2 (found by reading `green_command` against the task scope).** Three tests are inside T-001's `green_command` but cannot be GREEN with T-001's declared scope:

1. `tests/acceptance/logging/test_pipeline_backend.py::test_ac_001_no_backend_import_and_stdlib_chain` — the AC-001 witness is **T-006's** task; it AST-searches **all of `src/` and `tests/`** for a `loguru` import, and loguru imports necessarily remain in `src/backend/settings/`, `src/backend/eventbus/`, `src/backend/permissions/` (deptry interlock) and in the not-yet-adapted test helpers until T-004/T-005/T-006.
2. `tests/acceptance/logging/test_pipeline_backend.py::test_ac_003_file_record_fields_as_json` — the AC-003 witness is **T-002's** task; it needs a *traced* call, and the decorator stays loguru-based until T-002.
3. `tests/integration/logging/test_logging_integration.py::test_stdlib_loguru_decorator_pipeline` — its `@logged` clause (`integration_work_fn` + `<<` in the file) needs T-002's rebuilt decorator; its raw-loguru clause needs the removed backend. Weakening either clause is prohibited.

Both (1) and (2) are pulled in only because `green_command` names the whole file `tests/acceptance/logging/test_pipeline_backend.py` (the DAG's gate-scoping constraint excludes later tasks at **file** granularity, and these two live in a file T-001 also owns). Recommended reading for the S4.2 GREEN gate: T-001's gate is its own `tests_to_create` set plus the pre-existing tests it can honestly fix; these three are recorded as expected-red-at-T-001 and go green in T-002 (AC-003, the integration test) and T-006 (AC-001). The orchestrator must confirm this scoping before S4.2, since the DAG's `completion_gates` list does not name them.

**E. Dependency-set change + deptry interlock (measured baseline).** `uv run deptry .` at HEAD `aba98f8` → **Success! No dependency issues found** (Scanning 89 files). `structlog` is **not installed** in this worktree (`ModuleNotFoundError`), so step 1 is: add `structlog>=26` to `[project].dependencies` and `uv sync` (which also writes `uv.lock`) **in the same task that imports it**; remove `"orjson"` from `[tool.deptry.per_rule_ignores] DEP002` (`pyproject.toml:120-123`) **in the same task that imports orjson** (the file renderer). `loguru` (`pyproject.toml:12`) **stays declared** — `src/backend/settings/registry.py`, `src/backend/settings/repository.py`, `src/backend/eventbus/eventbus.py`, `src/backend/permissions/service.py` still import it, so it is neither DEP001 nor DEP002 in the state T-001 leaves behind; its removal is T-006. Do not touch the rest of `[tool.deptry]` (`pyproject-tooling-gaps` owns that table). The logging feature's own 2 statements in `src/backend/logging/feature_settings.py` (`logger.warning` / `logger.debug`) migrate to `get_logger()` here — part of REQ-001 (no backend import under `src/`); no test asserts those two statements through `log_records`, so the migration is behavior-neutral.

**F. Intermediate-state noise.** `_configure()` currently calls loguru's `logger.remove()` to drop its default stderr sink. Once `_setup.py` stops touching loguru, **loguru's default stderr sink stays installed** for the whole session, so every still-loguru-based `@logged` record prints to stderr. `captured_console()` dup2s the *managed console handler's* fd, so it is unaffected, but any assertion that reads raw stderr of a subprocess (`run_python`) may see loguru lines; `test_edge_002_rotation_with_open_handle` only greps for `--- Logging error ---`, which loguru does not emit.

**Gate table (S4.1)**

| Gate | Command | Result |
|---|---|---|
| Task ready | `.github/task-runner/tasks.json` — T-001 `dependencies: []`, `status: PENDING` | confirmed |
| Tests present | derived at `fcce934`, HEAD `aba98f8`; both authorized deletions already absent | confirmed |
| RED re-observed | T-001 `red_command` verbatim | **20 failed, 2 passed (19.49 s)** — same as S3.2, all `AssertionError` |
| deptry baseline (pre-implementation) | `uv run deptry .` | **Success! No dependency issues found** (89 files) |
| green_command baseline (pre-implementation) | T-001 `green_command` | **22 failed, 26 passed (38.56 s)** — the 2 extra failures are the two later-task witnesses in note D |
| No implementation written | this step changed only `docs/verification/structlog-logging.md` | confirmed |

**Phase 4 (S4.1, T-001) gate: PASS — RED re-confirmed.** Next: S4.2 (T-001) — implement + confirm GREEN.



---

## Phase 4 (S4.2, T-001) — pipeline core implemented, GREEN confirmed (2026-10-06)

**Step objective:** turn T-001's 20 red tests green by implementing the pipeline core in `src/backend/logging/`, without touching the tracing decorators (T-002).

### What was built (`allowed_files.source_files`, nothing else)

| File | State | Content |
|---|---|---|
| `src/backend/logging/_pipeline.py` | **new**, 358 lines / 13 310 bytes | The pipeline: `PIPELINE_LOGGER_NAME = "backend.logging"`, `PipelineSinks` (console + queue + rotating + forwarding + listener), `setup_logger(*, renderer=None)` (renderer validated **before** any mutation, EDGE-005), `_install` / `_reconfigure` / `_reconcile_ownership` (EDGE-003), `_ForwardingHandler` on the root logger (ADR-082 D2: forward, never re-emit), `_PipelineQueueHandler` overriding `prepare()` so the record is enqueued unformatted (ADR-082 pinned fact), `_RotatingHandler` retrying `doRollover` under a Windows open-handle `PermissionError` (EDGE-002), `get_logger(name=None)` (structlog `BoundLogger` over the pipeline logger; a plain `logger_factory` callable, **not** `structlog.stdlib.LoggerFactory`, whose `__init__` performs a global `logging.setLoggerClass` mutation — INV-004), `managed_sinks()`, `shutdown_pipeline()`, the `SettingChanged` subscription that reconfigures on any `logging.*` write |
| `src/backend/logging/_renderers.py` | **new**, 261 lines / 9 480 bytes | The record-field contract and the renderers: `RENDERED_FIELD_ORDER` (`level, logger, event, timestamp, file, line`), `INTERNAL_FIELDS` / `PROCESSOR_META_FIELDS` (the pipeline's `filename`/`lineno` and the formatter's `_record`/`_from_structlog` never reach a rendered record), `callsite_adder` (runs in the emitting thread), `add_level_field` (level from `_record.levelname`, so `exception()` is `ERROR` and numeric 47 is `Level 47` — EDGE-004), `add_logger_field` (event-dict `logger_name`, else `record.name`), `rename_callsite_fields`, `drop_pipeline_internals`, `add_timestamp`, `exception_field` (nested `type`/`message`/`frames`, never local values), `render_json` (orjson `serializer=`, bytes decoded to `str`), `TextRenderer` + `color_for_tty` (ANSI only on a TTY) |
| `src/backend/logging/_setup.py` | **deleted** (`git rm`) | The loguru backend (`logger.add` sinks, `_InterceptHandler`, `_SinkState.ids`) — superseded by `_pipeline.py` |
| `src/backend/logging/__init__.py` | modified | Exports exactly the §3 eight names: `Settings, _read_setting, get_logger, get_settings, logged, logged_class, register_settings, setup_logger` (AC-020; `logger`/`loguru` absent) |
| `src/backend/logging/feature_settings.py` | modified | Its 2 own statements now go through a module-level `_feature_logger = get_logger("logging")` binding; `from loguru import logger` is gone (REQ-001/REQ-005, behavior-neutral) |
| `pyproject.toml` | modified | `structlog>=25.1.0` declared (imported by this task); `"orjson"` removed from `[tool.deptry.per_rule_ignores] DEP002` (imported by this task). `loguru` **stays** declared — `src/backend/settings/`, `src/backend/eventbus/`, `src/backend/permissions/` still import it (deptry interlock, removal is T-006) |
| `uv.lock` | modified | `uv sync` recorded structlog 26.1.0 |

`src/backend/logging/_decorator.py` and `_settings.py` are untouched (mtime unchanged) — the decorators stay loguru-based until T-002, as T-001's file set requires.

### GREEN gate — the DAG's own `green_command`, verbatim

```text
uv run pytest tests/acceptance/logging/test_pipeline_backend.py tests/acceptance/logging/test_third_party_records.py tests/acceptance/logging/test_get_logger.py tests/acceptance/logging/test_renderer.py tests/acceptance/logging/test_logging.py tests/unit/logging/ tests/property/logging/test_pipeline_invariants.py::test_inv_001_concurrent_setup_owns_two_handlers tests/property/logging/test_pipeline_invariants.py::test_inv_004_other_loggers_untouched tests/property/logging/test_logging_properties.py tests/integration/logging tests/contract/logging/test_tracing_surface.py::test_ac_020_public_export_surface tests/contract/logging/test_logging_contracts.py::test_nfr_001_setup_time_budget tests/acceptance/logging_coverage/test_sink_failure.py tests/acceptance/logging_coverage/test_setup_logger.py -v
```

→ **45 passed, 3 failed (46.22 s)** — from the S4.1 baseline of **22 failed / 26 passed**. Every one of T-001's own `tests_to_create` witnesses is GREEN: AC-002, AC-004, AC-005, AC-006, AC-007, AC-008, AC-010, AC-016, AC-020, INV-001, INV-004, EDGE-001…EDGE-006, NFR-001, NFR-005, plus the pre-existing tests the task had to fix (`test_ac_001_setup_logger_adds_sinks`, `test_ac_002_setup_logger_idempotent`, `test_ac_003_setup_logger_thread_safe`, `test_ac_004_intercept_handler_routes_records`, the 3 re-derived `test_logging_sink_ownership` tests, `test_inv_001_concurrent_setup_logger_sinks`, `tests/integration/logging` except the note-D test).

**The 3 remaining failures are the note-D cross-task exemptions, confirmed by the orchestrator's ruling** (the DAG's `green_command` is a **file-granularity** gate and these three live in files T-001 also owns; they are not pipeline defects):

| Test | Needs | Goes green in |
|---|---|---|
| `test_ac_001_no_backend_import_and_stdlib_chain` | no `loguru` import anywhere under `src/` or `tests/` — 12 modules still import it (deptry interlock + not-yet-adapted test helpers) | **T-006** |
| `test_ac_003_file_record_fields_as_json` | a *traced* call's exit record in the file sink — the decorator is still loguru-based | **T-002** |
| `test_stdlib_loguru_decorator_pipeline` | the rebuilt `@logged` **and** the removed backend | **T-002** |

Neither clause was weakened: both files keep their full assertions and stay red until their owning task lands.

### NFR-001 measurement (contract gate 5)

`test_nfr_001_setup_time_budget` (median of 3 fresh processes) is GREEN. Independent re-measurement, 5 fresh processes, same shape: `SETUP_MS 1.15 / 1.16 / 1.20 / 1.19 / 1.16` → **median 1.19 ms** (min 1.15, max 1.20) against the **< 25 ms** budget. Measurement context: Windows 11, Python 3.14.5, INFO, console + queue + rotating file + root forwarding handler + listener started.

### Test-side adaptations (all inside T-001's `allowed_files.test_files`; no assertion weakened)

| Change | Why | Strength |
|---|---|---|
| `tests/logging_test_helpers.py`: `STDERR_FD = sys.stderr.fileno()` (evaluated at import) instead of the hardcoded `2` | pytest's capture object is `sys.stderr` at fd 9 in-process; AC-010 reassigns `sys.stderr` to a file before `setup_logger()`, so the console handler must bind the *current* `sys.stderr` | same assertion, correct fd (9 in-process, 2 in a fresh interpreter) |
| `captured_console()` no longer unlinks its temp file | all 10 call sites read the yielded path **after** the `with` block exits | unchanged |
| `wait_for_file_content()` drains the `QueueHandler` queue (`_drain_queue()`) instead of loguru's `logger.complete()` | the flush is now the listener's | unchanged |
| loguru-era `_console_sink_fd()` / `captured_stderr()` deleted | dead once no loguru sink exists; no remaining importer | n/a |
| `managed_handlers()` added; `pipeline_logger()` / `managed_sinks()` / `test_logging_sink_ownership._feature_handlers()` / `test_ac_003_setup_logger_thread_safe` count **owned** handlers | pytest's `catching_logs` attaches its own `LogCaptureHandler` to **every non-propagating logger** — and the pipeline logger is non-propagating by design (AC-005), so the harness handler appears on it during each test phase. It is not one of the two managed sinks | same counts (one console + one file sink), harness noise excluded; verified: the feature logger owns exactly `StreamHandler` + `_PipelineQueueHandler` |
| EDGE-002 subprocess poll wrapped in `try/except OSError` (`_WAIT_FOR_ROTATED`) | the listener renames `app.log.1 → app.log.2` and deletes the oldest backup while the poll reads the glob — a real race in the **witness**, which made the test flaky (it failed once in a full gate run, passed in isolation) | all three assertions unchanged (`returncode 0`, no `--- Logging error ---`, probe 059 present); re-ran the file 3× → 6 passed each time |

### Production fixes found by the witnesses (not test-side)

- **AC-016 (REQ-013):** `Handler.handle()` does **not** guard `emit()`, so a managed sink whose `emit` raises travelled through the root forwarding handler into the emitting business call. Fixed at both trust boundaries: `_PipelineQueueHandler.emit` now catches and calls `handleError` (protects the direct pipeline-logger path), and `_ForwardingHandler.emit` guards each `target.handle(record)` so one dead sink neither reaches the caller nor stops the other sink from receiving the record.
- **EDGE-002:** rotation under an open handle on Windows raised `PermissionError` inside `doRollover`; `_RotatingHandler` retries with a short backoff before deferring to the stdlib.

### Collateral-damage check (affected directories)

`uv run pytest tests/acceptance/logging tests/unit/logging tests/integration/logging tests/property/logging tests/contract/logging tests/acceptance/logging_coverage tests/unit/logging_coverage tests/property/logging_coverage tests/acceptance/settings_coverage tests/unit/test_settings_coverage.py` → **22 failed, 105 passed (14 m 32 s)**. Every failure is a later-task witness, none is new collateral damage:

| Owner | Failures |
|---|---|
| T-002 (rebuild `@logged` / `@logged_class` on the pipeline) | `test_ac_011_sync_and_async_traced_records`, `test_ac_012_exception_record_and_propagation`, `test_ac_014_logged_class_records`, `test_ac_015_no_local_values_in_exception_record`, `test_ac_013_removed_parameters`, `test_module_functions_traced`, `test_inventory_covers_all_public_classes`, `test_traced_classes_have_concrete_threshold`, `test_nfr_003_diagnose_false`, `test_nfr_004_backward_compatible_api`, `test_inv_002/inv_003/inv_005`, `test_ac_003_file_record_fields_as_json`, `test_stdlib_loguru_decorator_pipeline` |
| T-004 / T-005 (migrate the 39 statements) | `test_ac_009_statements_go_through_get_logger`, `test_ac_009_settings_statements_go_through_get_logger`, `test_ac_009_eventbus_statements_go_through_get_logger`, `test_observability_tracing` |
| T-006 (remove loguru) | `test_ac_018_dependency_report_clean`, `test_ac_001_no_backend_import_and_stdlib_chain` |
| T-007 (guidance) | `test_ac_019_guidance_names_feature_entry_points` |

Must-stay-green guards from the RED gate are all still green: `test_ac_004_foreign_handlers_untouched`, `test_nfr_001_setup_time_budget`, `test_logging_stub_removed`.

### Gate table (S4.2, T-001)

| Gate | Command | Result |
|---|---|---|
| GREEN (T-001 `green_command`) | verbatim above | **45 passed, 3 failed** — the 3 are the note-D cross-task exemptions |
| T-001's own `tests_to_create` | subset of the above | 100% passed |
| Ruff (changed paths) | `uv run ruff check tests/unit/logging/test_pipeline_edges.py tests/unit/logging/test_logging.py tests/unit/logging/test_logging_sink_ownership.py tests/logging_test_helpers.py src/backend/logging/` | All checks passed |
| Format (changed paths) | `uv run ruff format <same>` | 10 files left unchanged |
| Types | `uv run mypy src/` | **Success: no issues found in 84 source files** |
| Dependencies | `uv run deptry .` | **Success! No dependency issues found** (90 files) — structlog declared + imported, orjson declared + imported + out of DEP002, loguru declared + still imported |
| Traceability | `uv run python scripts/check_traceability.py` | **PASS** (784 matrix rows, 129 spec IDs, 745 test functions) |
| NFR-001 | 5 fresh processes | median **1.19 ms** (< 25 ms) |
| Scope | `git status --short` | only T-001's `allowed_files` paths; `_decorator.py` / `_settings.py` / `migrations/` untouched |
| No test weakened | adaptation table above | 0 assertions removed; 2 test-side robustness fixes recorded |

**Phase 4 (S4.2, T-001) gate: PASS — GREEN confirmed.** Working tree left **uncommitted** (S4.4 commits and sets `VERIFIED`). Next: S4.3 (T-001) refactor, then S4.4 commit + status.


---

### S4.3 T-001 — refactor (2026-10-06)

**Not a no-op.** A review pass over `_pipeline.py` / `_renderers.py` (the two new modules) and the changed `__init__.py` / `feature_settings.py` found seven behaviour-preserving cleanups; `__init__.py` and `feature_settings.py` needed none (the export set is exactly spec §3's eight names, and the feature's two own statements already go through `_feature_logger`). `_decorator.py` untouched (T-002).

| # | Change | Why it is behavior-preserving |
|---|---|---|
| 1 | Deleted `_renderers.RecordField` (a `Literal` alias) and its `Literal` import | Zero references anywhere in `src/`, `tests/`, `scripts/` or the docs — dead code. The record-field contract itself stays in `RENDERED_FIELD_ORDER` and spec §3 |
| 2 | `_pipeline.managed_sinks()` and `_pipeline.shutdown_pipeline()` deleted | Neither is in spec §3's surface and neither has a caller: the tests reach the sinks through the **public** stdlib machinery (`tests/logging_test_helpers.pipeline_logger` / `.managed_sinks` scan `logging.Logger.manager` deliberately, never a private import), and `logging.handlers.QueueListener` starts a **daemon** thread (`t.daemon = True`), so no stop hook is needed for the process to exit. `PipelineSinks.managed()` — the only ownership accessor the pipeline itself uses — stays |
| 3 | `_ForwardingHandler.emit`: removed `if target is self: continue` | Unreachable: `PipelineSinks.managed()` returns `(console, queue)` and the forwarder is never one of them (it lives on the root logger, and the pipeline logger never propagates) |
| 4 | `_validate_renderer`: `return renderer  # type: ignore[return-value]` → `return cast("RendererName", renderer)` | Same value; a real narrowing instead of a suppressed mypy error |
| 5 | `_level_of`: `str(settings.log_level).upper()` → `settings.log_level.upper()` | `Settings.log_level` is typed `str` and `get_settings()` always builds a `str` — the `str()` was a no-op |
| 6 | `_on_setting_changed`: single `_sinks[0]` read under the lock instead of a triple read (`… and _sinks[0] is not None` plus a redundant inline re-check) | Same decision table; the lock is taken before the read, and `_reconfigure` still returns early if the pipeline is gone. No new lock nesting (`_reconfigure` never takes `_setup_lock`) |
| 7 | `_renderers`: `drop_pipeline_internals` iterates the precomputed `_DROPPED_FIELDS = PROCESSOR_META_FIELDS \| INTERNAL_FIELDS` instead of rebuilding a 9-key tuple per record; `_traceback_frames` gained the docstring that states **why** it reads only `linecache` source text and never frame locals (REQ-009 / INV-002) | Same key set, same removals; the constant is built once at import |

**Considered and deliberately kept:** `_PipelineQueueHandler.emit`'s `try/except → handleError` guard. `logging.handlers.QueueHandler.emit` already guards itself in 3.14, so the override is currently redundant — but AC-016/REQ-013 is the feature's guarantee, and once T-002 routes traced records through the pipeline logger directly (`Handler.handle()` does **not** guard `emit()`), relying on the stdlib's internal guard would be an implicit dependency. The comment now says exactly that, so a future dead-code sweep does not delete the boundary. `_install` was left as one linear construction block (splitting it would add indirection without removing duplication with `_reconfigure`).

**Net:** `_pipeline.py` 358 → 348 lines, `_renderers.py` 261 → 268 lines (the added docstring), −5 lines overall; no public surface change.

| Gate | Command | Result |
|---|---|---|
| GREEN before | T-001 `green_command`, verbatim (S4.2 state) | **45 passed, 3 failed** (46.57 s) |
| GREEN after | T-001 `green_command`, verbatim (final state) | **45 passed, 3 failed** (46.69 s) — the same three note-D exemptions (`test_ac_001_no_backend_import_and_stdlib_chain` → T-006, `test_ac_003_file_record_fields_as_json` → T-002, `test_stdlib_loguru_decorator_pipeline` → T-002) |
| Ruff (changed paths) | `uv run ruff check src/backend/logging/_pipeline.py src/backend/logging/_renderers.py src/backend/logging/__init__.py src/backend/logging/feature_settings.py` | All checks passed |
| Format (changed paths) | `uv run ruff format <same four>` | 4 files left unchanged |
| Types | `uv run mypy src/` | Success: no issues found in 84 source files |
| Dependencies | `uv run deptry .` | Success! No dependency issues found (90 files) |
| Tests touched | — | none (refactor touched only the two pipeline modules) |

**Phase 4 (S4.3, T-001) gate: PASS — refactor applied, GREEN unchanged.** Next: S4.4 (T-001) commit + set `"status": "VERIFIED"`.


---

### S4.4 T-001 — VERIFIED (2026-10-06)

**Commit of the S4.2 + S4.3 work.** `git status --short` clean before the step; HEAD `b1675ad` — *"chore(structlog-logging): S4.2+S4.3 T-001 pipeline core (structlog + stdlib sinks, get_logger) + refactor pass"* — 13 files, +939 / −350:

`docs/verification/structlog-logging.md`, `pyproject.toml`, `uv.lock`, `src/backend/logging/__init__.py`, `src/backend/logging/_pipeline.py` (new), `src/backend/logging/_renderers.py` (new), `src/backend/logging/_setup.py` (deleted), `src/backend/logging/feature_settings.py`, `tests/integration/logging/test_logging_integration.py`, `tests/logging_test_helpers.py`, `tests/unit/logging/test_logging.py`, `tests/unit/logging/test_logging_sink_ownership.py`, `tests/unit/logging/test_pipeline_edges.py` — all inside T-001's `allowed_files`.

**GREEN re-confirmed once (the DAG's own `green_command`, verbatim).** → **45 passed, 3 failed** (46.81 s). The 3 failures are exactly the note-D cross-task exemptions ruled at the S3.2 RED gate — each is another task's witness, not a T-001 gap:

| Exempted test | Owning task | Why it is not T-001's |
|---|---|---|
| `tests/acceptance/logging/test_pipeline_backend.py::test_ac_001_no_backend_import_and_stdlib_chain` | **T-006** (remove loguru) | asserts the loguru-free dependency state; loguru is still declared and still imported by the three not-yet-migrated feature files |
| `tests/acceptance/logging/test_pipeline_backend.py::test_ac_003_file_record_fields_as_json` | **T-002** (rebuild `@logged` / `@logged_class` on the pipeline) | asserts the traced-record field set reaching the file sink; the decorators are still the old loguru-backed ones |
| `tests/integration/logging/test_logging_integration.py::test_stdlib_loguru_decorator_pipeline` | **T-002** | same: the decorator → pipeline integration is T-002's scope |

T-001's own `tests_to_create` and every other path in its `green_command`: **45/45 passed**.

**Status write.** `"status": "VERIFIED"` set for **T-001 only** in `.github/task-runner/tasks.json` and mirrored in `docs/tasks/structlog-logging.tasks.json`. The two files are **byte-identical** (`diff` → no output; `tasks` arrays compared as parsed JSON → equal), all other tasks still `PENDING`.

**State machine (T-001).** `RED_CONFIRMED → GREEN → REFACTORED → VERIFIED` — RED observed at S3.2/S4.1, GREEN at S4.2, refactor applied without changing the GREEN result at S4.3, VERIFIED here with the traceability matrix already updated by S3.2 and the S4.2 collateral record.

**Ready tasks unlocked by T-001 = VERIFIED** (per `dependencies` in `tasks.json`):

| Task | Dependencies | State after T-001 |
|---|---|---|
| **T-002** | T-001 | **READY** |
| **T-004** | T-001 | **READY** |
| **T-005** | T-001 | **READY** |
| T-003 | T-001, T-002 | still blocked by T-002 |
| T-007 | T-001, T-002 | still blocked by T-002 |
| T-006 | T-001, T-002, T-003, T-004, T-005 | still blocked by T-002, T-003, T-005 |

| Gate | Command | Result |
|---|---|---|
| Work committed | `git status --short` / `git show --stat b1675ad` | clean tree; 13 files in the S4.2+S4.3 commit |
| GREEN re-check | T-001 `green_command`, verbatim | **45 passed, 3 failed** — the three exemptions above, no new failure |
| Status sync | `diff .github/task-runner/tasks.json docs/tasks/structlog-logging.tasks.json` | identical; T-001 `VERIFIED`, T-002..T-007 `PENDING` |
| Ruff | n/a — S4.4 wrote no source or test file | n/a |

**Phase 4 (S4.4, T-001) gate: PASS — T-001 VERIFIED.** Next: S4.1 (T-002) pick the next ready task.


---

### S4.1 T-005 — task picked, RED re-confirmed (2026-10-06)

**Task picked: T-005** — *migrate the 10 direct backend statements in `src/backend/eventbus/eventbus.py` to `get_logger()`* (REQ-005 / AC-009; amended `logging-coverage.md` v2 REQ-010 / AC-010; Impact Analysis row 3 — `backend.eventbus`, "no spec ID change").

#### Readiness check

| Check | Evidence | Result |
|---|---|---|
| Dependency satisfied | T-005 `"dependencies": ["T-001"]`; T-001 `"status": "VERIFIED"` (S4.4, HEAD `1dc155c`) | satisfied |
| Status still `PENDING` | `.github/task-runner/tasks.json` — T-001 `VERIFIED`, T-002..T-007 `PENDING` | confirmed |
| Its test exists | `tests/acceptance/logging_coverage/test_statements_via_feature.py::test_ac_009_eventbus_statements_go_through_get_logger` (derived at S3.1, T-005) — collected and run below | confirmed |
| The pipeline it migrates to exists | T-001 shipped `src/backend/logging/_pipeline.py` with `get_logger(name=None) -> BoundLogger`, exported from `backend.logging` (the §3 eight-name surface, AC-020); `src/backend/eventbus/eventbus.py:22` already imports `logged, logged_class` from it | confirmed |
| Working tree | `git status --short` clean at HEAD `1dc155c` | confirmed |

#### RED re-confirmed (the DAG's own `red_command`, verbatim)

```text
uv run pytest tests/acceptance/logging_coverage/test_statements_via_feature.py::test_ac_009_eventbus_statements_go_through_get_logger -v
```

→ **1 failed, 0 passed (0.30 s)** at HEAD `1dc155c` — **identical to the S3.2 gate (1 failed / 0 passed)**; no drift between Phase 3 and Phase 4 entry. One `AssertionError` on unimplemented behavior; no collection, import, fixture or test-data error:

```text
AssertionError: AC-009 / REQ-005 (logging-coverage REQ-010 v2): src/backend/eventbus/eventbus.py imports a logging backend: ['loguru.logger']; src/backend/eventbus/eventbus.py statements not written through get_logger(): line(s) [86, 96, 115, 120, 136, 176, 197, 205, 222, 233]; a module under src/backend/eventbus/ imports a logging backend: ['src/backend/eventbus/eventbus.py']
```

The **count clause contributes no violation** — the file already holds exactly REQ-005's 10 statement call sites — so the witness is red exactly on the two clauses T-005 fixes: the backend import, and every statement's receiver not being a `get_logger()`-bound logger.

Pre-implementation baselines for this task's gates:

- `green_command` set minus the witness — `uv run pytest tests/acceptance/eventbus tests/unit/eventbus tests/contract/eventbus tests/property/eventbus tests/integration/eventbus -q` → **31 passed (3.78 s)**. The whole set must still be 31 passed afterwards (no behavior delta).
- `uv run deptry .` → **Success! No dependency issues found** (90 files) — loguru is still declared *and* still imported by four feature modules, so neither DEP001 nor DEP002.

#### Migration scope (`allowed_files.source_files`: `src/backend/eventbus/eventbus.py` only)

The one import to replace: `eventbus.py:20` `from loguru import logger`. It is the **only** backend import anywhere under `src/backend/eventbus/` (`__init__.py` and `feature_settings.py` have none), so that single line fixes the witness's feature-wide clause. `get_logger` joins the existing `from backend.logging import logged, logged_class` edge at line 22 — no new import direction (spec §10 row 3).

The 10 statement call sites (line numbers as they stand at `1dc155c`; levels and wording stay exactly as listed — spec §9 row 2, "DEBUG/INFO/WARNING as today", unchanged wording):

| Line | Method | Message (current, loguru brace form) | Positional args |
|---|---|---|---|
| 86 | `logger.debug` | `event bus: subscribed handler '{}' for event type '{}'` | `_handler_name(handler)`, `event_type.__name__` |
| 96 | `logger.debug` | `event bus: unsubscribed handler '{}' for event type '{}'` | same |
| 115 | `logger.debug` | `event bus: published event type '{}'` | `type(event).__name__` |
| 120 | `logger.warning` | `event bus: queue full; dropping event type '{}' (dropped={})` | `type(event).__name__`, `dropped` |
| 136 | `logger.debug` | `event bus: shutdown initiated` | — |
| 176 | `logger.debug` | `event bus: started background worker thread` | — |
| 197 | `logger.debug` | `event bus: dispatching event type '{}' to handler '{}'` | `type(event).__name__`, `_handler_name(handler)` |
| 205 | `logger.exception` | `event bus: handler '{}' raised for event type '{}'` | `_handler_name(handler)`, `type(event).__name__` |
| 222 | `logger.debug` | `event bus: created shared default instance` | — |
| 233 | `logger.debug` | `event bus: reset shared default instance` | — |

8 × DEBUG, 1 × WARNING, 1 × `exception` (ERROR level).

#### What the witness accepts (read from its own helpers in `test_statements_via_feature.py`)

- `_backend_imports` flags a `loguru` **or `structlog`** import in **any** module under `src/backend/eventbus/` — the migration must not reach for structlog directly (REQ-005: `get_logger()` is the only entry point).
- `_statement_calls` counts every call shaped `<recv>.<level>(...)` (`debug|info|warning|warn|error|exception|critical|fatal|log`); the count must stay **exactly 10** — none added, none removed, none folded into a helper (logging-coverage REQ-010 v2).
- `_written_via_get_logger` accepts either an inline `get_logger(...).debug(...)` receiver or a name bound by an assignment (`_x = get_logger(...)`, module-level or attribute target). The module-level binding T-001 used in `src/backend/logging/feature_settings.py` (`_feature_logger = get_logger("logging")`) is the established, already-clean pattern to follow.

#### Design constraints (verbatim from the DAG)

1. REQ-005: no feature imports a logging backend; `get_logger()` is the only entry point.
2. The statement count stays 10 (`logging-coverage` REQ-010 restated).
3. Import direction unchanged: `backend.eventbus -> backend.logging` is the allowed direction (spec §10 row 3).
4. deptry interlock: **`loguru` stays declared in `pyproject.toml`** — `src/backend/permissions/service.py` still imports it; removing the declaration is **T-006**. `pyproject.toml` is not in T-005's `allowed_files` and must not be touched here.
5. `implementation_steps` 2: the worker-thread statements (startup, handler exception, shutdown) keep their current levels — the bus's own observability policy is unchanged.

#### Risk notes for S4.2

**A. Brace formatting silently loses data on the new pipeline — this is why the task says "keyword-field form".** `get_logger()` returns a `structlog.stdlib.BoundLogger` configured with `_EMITTING_CHAIN = (callsite_adder(), exception_field)` + `ProcessorFormatter.wrap_for_formatter` (`_pipeline.py:50`, `:166-173`); there is **no `PositionalArgumentsFormatter`** in the chain. Verified against the installed structlog 26.1.0: `structlog.stdlib.BoundLogger._proxy_to_logger` moves positional args into `event_kw["positional_args"]`, and `positional_args` is listed in `_renderers.INTERNAL_FIELDS`, so it is **dropped from every rendered record**. Copying the `'{}'` messages with positional args would emit `event bus: published event type '{}'` with the braces unfilled and the value discarded. The keyword-field form keeps the wording and keeps the values: `str.format` fills named placeholders from the same kwargs that land in the event dict (e.g. `"event bus: published event type '{event_type}'"` with `event_type=type(event).__name__`).

**B. Two loguru-era tests outside T-005's scope go red at T-005 (cross-task interlock — do not "fix" them here).** Both capture through the **loguru** `log_records` fixture (`tests/conftest.py:106`, `logger.add(...)`), which stays loguru-based until **T-002** re-implements the capture (T-002 `implementation_steps` item 5; `tests/conftest.py` is in T-002's `allowed_files.test_files`). Neither file is in T-005's `allowed_files`, and neither is in T-005's `green_command`:

| Test | Green now? | Why T-005 breaks it | Goes green in |
|---|---|---|---|
| `tests/acceptance/logging_coverage/test_levels.py::test_semantic_log_levels` | **yes** (measured: passes at `1dc155c`) | its only ERROR-level record is the bus's `logger.exception` at line 205 — `_dispatch` is private, so `@logged_class` emits no ERROR of its own; after the migration that record leaves the loguru capture | **T-002** (pipeline-based capture) |
| `tests/acceptance/logging_coverage/test_direct_loguru_kept.py::test_existing_direct_loguru_kept` | **yes** (measured: 1 passed) | it asserts the literal wording of two bus statements (`event bus: published event type`, `event bus: shutdown initiated`) inside the loguru capture | **T-006** deletes the file (authorized deletion, recorded at S3.1 and in the S4.2 collateral note; it is T-006's `implementation_steps` item 1) |

Schedule consequence: if T-005 runs **before T-002**, the Phase 5 full suite gains these two red tests, and **T-002's own `green_command` already includes `tests/acceptance/logging_coverage/test_levels.py`**, so T-002's conftest re-implementation is exactly what repairs the first one. Running T-002 before T-005 avoids the temporary red entirely. Neither test may be weakened, adapted or deleted in T-005 (prohibited, and out of `allowed_files`).

**C. The bus's worker thread emits through the pipeline.** Statements at 176 / 197 / 205 run on the `eventbus-worker` daemon thread. The pipeline's file sink is a `QueueHandler` → `QueueListener`: the record is enqueued **unformatted** (`_PipelineQueueHandler.prepare` override, ADR-082) and rendered on the listener thread, while `callsite_adder` and `exception_field` run in the **emitting** thread — so `file`/`line` still point at `eventbus.py`, and line 205's `exc_info` is resolved in the worker thread before the record crosses the queue (structlog's `exception()` sets `exc_info=True`; `_renderers.exception_field` renders type / message / frames only, never locals — INV-002). Nothing to add: AC-016's "a failing sink never reaches the caller" guarantee is already enforced at both handler boundaries, so the implementer must not wrap the emits in a `try/except` or format anything by hand.

**D. `@logged_class(slow_threshold_ms=250)` on `EventBus` and `@logged` on `get_event_bus` / `reset_event_bus` stay loguru-based until T-002.** After T-005 this one module emits through **two** backends (traced records via loguru, statements via the pipeline). That is the intended intermediate state — `_decorator.py` is not in T-005's file set and must not be touched, and the `logged` / `logged_class` import must stay.

**E. Level filtering is unchanged, but visible.** The pipeline logger's level comes from settings (`Settings.log_level` default `INFO`, `_settings.py:19`; the `logging.log_level` SELECT default is `INFO`, `feature_settings.py:62`), so the 8 DEBUG statements reach a sink only at DEBUG — the same effective behavior as the deleted loguru sinks, which were added at `settings.log_level` (`_setup.py:159`, `:164` at `b1675ad^`). Tests that assert those statements install their own sink at DEBUG. The event bus's own 31 tests assert **no** records at all (measured: no `log_records` / `capture_records` / `caplog` use in any `tests/*/eventbus` file), which is precisely why the `green_command` set is a clean no-delta guard.

**F. A module-level `get_logger()` binding is safe at import time.** It runs `_configure_structlog()` during import — already the case via `backend/logging/feature_settings.py` — and binds to the singleton `logging.Logger` the pipeline later attaches its sinks to (`_logger_factory` returns `pipeline_logger()`); using `get_logger()` before `setup_logger()` must not raise (EDGE-006, GREEN since T-001).

#### Completion gates (T-005, verbatim from the DAG)

1. RED observed on the `red_command` set; recorded here. **← this step**
2. The eventbus-half AC-009 witness passes.
3. No `loguru` import remains anywhere under `src/backend/eventbus/`.
4. The event bus's whole test directory passes unchanged (no behavior delta) — baseline **31 passed**.
5. `uv run deptry .` clean; `uv run ruff check <changed paths>` clean; `uv run mypy src/` clean.

#### Gate table (S4.1, T-005)

| Gate | Command | Result |
|---|---|---|
| Task ready | T-005 `dependencies: ["T-001"]` (VERIFIED), `status: "PENDING"` | confirmed |
| Its test present | collected and executed below | confirmed |
| RED re-observed | T-005 `red_command` verbatim | **1 failed, 0 passed (0.30 s)** — same as S3.2, one `AssertionError` |
| `green_command` baseline (pre-implementation) | the event bus's five test directories | **31 passed (3.78 s)** |
| deptry baseline (pre-implementation) | `uv run deptry .` | **Success! No dependency issues found** (90 files) |
| Cross-task red tests identified | `test_levels.py` and `test_direct_loguru_kept.py` measured green before this step | note B |
| No implementation written | this step changed only `docs/verification/structlog-logging.md` | confirmed |

**Phase 4 (S4.1, T-005) gate: PASS — RED re-confirmed.** Next: S4.2 (T-005) — implement + confirm GREEN.

---

### S4.1 T-002 — task picked, RED re-confirmed (2026-10-06)

**Task picked: T-002** — *tracing decorators rebuilt on the pipeline's binding machinery: `@logged` (sync + async) entry / exit-with-`elapsed_ms` / exception, `@logged_class`, exception rendered into the `exception` field with no local values, `context_getter` and `depth` removed, tracing-surface contract, amended NFR-002 budget, test record-capture helpers re-implemented* — Impact Analysis row 1, `backend.logging` (owner). Covers **REQ-007/008/009/011/015**, **AC-003/011/012/013/014/015**, **INV-002/003/005**, **NFR-002/003**.

**Ordering (orchestrator decision, recorded because it departs from the DAG's numeric order).** T-002 runs **before T-004/T-005**. Note B of the S4.1 (T-005) block measured that migrating the feature statements first turns `tests/acceptance/logging_coverage/test_levels.py::test_semantic_log_levels` red — its only ERROR-level record is the bus's `logger.exception`, captured through the **loguru** `log_records` fixture (`tests/conftest.py:106`). T-002's `implementation_steps` item 5 re-implements exactly that capture surface, and `test_levels.py` is already in T-002's `green_command`, so rebuilding the decorators + capture first removes the temporary red instead of creating it.

#### Readiness check

| Check | Evidence | Result |
|---|---|---|
| Dependency satisfied | T-002 `"dependencies": ["T-001"]`; T-001 `"status": "VERIFIED"` (S4.4, `1dc155c`) | satisfied |
| Status still `PENDING` | `.github/task-runner/tasks.json` — T-001 `VERIFIED`, T-002..T-007 `PENDING` | confirmed |
| Its tests exist | `--collect-only -q` on the `red_command` set → **11 tests collected in 0.18 s**, every node id resolves | confirmed |
| The pipeline it builds on exists | T-001 shipped `_pipeline.py` (`get_logger()` → `structlog.stdlib.BoundLogger` over `pipeline_logger()`, `_EMITTING_CHAIN = (callsite_adder(), exception_field)`, `_configure_structlog()`), and `_renderers.py` (`exception_field` / `_exception_content` / `_traceback_frames` = type + message + frames, never locals; `rename_callsite_fields`; `drop_pipeline_internals`) | confirmed |
| Working tree | `git status --short` clean at HEAD `1a5ceb8` | confirmed |

#### RED re-confirmed (the DAG's own `red_command`, verbatim)

```text
uv run pytest tests/acceptance/logging/test_tracing_records.py tests/acceptance/logging/test_secrets.py tests/acceptance/logging/test_pipeline_backend.py::test_ac_003_file_record_fields_as_json tests/contract/logging/test_tracing_surface.py::test_ac_013_removed_parameters tests/property/logging/test_pipeline_invariants.py::test_inv_002_no_local_value_ever_recorded tests/property/logging/test_pipeline_invariants.py::test_inv_003_elapsed_non_negative tests/property/logging/test_pipeline_invariants.py::test_inv_005_required_fields_present tests/contract/logging/test_logging_contracts.py::test_nfr_002_decorator_overhead_budget tests/contract/logging/test_logging_contracts.py::test_nfr_004_backward_compatible_api -v
```

→ **10 failed, 1 passed (135.40 s)** at HEAD `1a5ceb8`. **S3.2 recorded 11 failed / 0 passed — the drift is exactly one test, and it is an improvement, not a weakening:** `test_nfr_002_decorator_overhead_budget` now passes. Verified by elimination against the collected list (it is the only collected node absent from the run's `short test summary` FAILED list); the reason is T-001 — the amended budget (< 1 ms with both managed sinks at DEBUG) is now measured against the new pipeline, whose overhead the spec records at **0.148 ms/call**. No test file changed after S3.2's gate (`git log -1 -- tests/contract/logging/test_logging_contracts.py` → `d82cc1e`, the S3.1 T-002 derivation commit).

**Failure mode (test-contract sanity check): 10 `AssertionError`s, 0 collection / import / fixture / test-data errors.** Every failure is an assertion on unimplemented behavior:

| Test | Failure (verbatim) |
|---|---|
| `test_tracing_surface.py::test_ac_013_removed_parameters:73` | `AC-013/REQ-007/D6: @logged must not accept context_getter (no shim, no alias)` |
| `test_logging_contracts.py::test_nfr_004_backward_compatible_api:138` | `NFR-004 v3/AC-013: context_getter is removed from the @logged surface (no shim, no alias)` |
| `test_tracing_records.py::test_ac_011_sync_and_async_traced_records:39` | `AC-011: ac_011_sync_target must emit an entry record before its exit record` |
| `test_tracing_records.py::test_ac_012_exception_record_and_propagation:93` | `AC-012: the exception record must reach the file sink` |
| `test_tracing_records.py::test_ac_014_logged_class_records:39` | `AC-014: ac_014_public_call must emit an entry record before its exit record` |
| `test_secrets.py::test_ac_015_no_local_values_in_exception_record:35` | `AC-015: the exception record must reach the file sink` |
| `test_pipeline_backend.py::test_ac_003_file_record_fields_as_json:79` | `AC-003: the traced exit record must reach the file sink as a JSON object` |
| `test_pipeline_invariants.py::test_inv_002_no_local_value_ever_recorded:258` | `INV-002: the raising traced call must emit an exception record to the file sink` |
| `test_pipeline_invariants.py::test_inv_003_elapsed_non_negative:287` | `INV-003/REQ-011: inv_003_sync_probe must emit an exit record carrying elapsed_ms` |
| `test_pipeline_invariants.py::test_inv_005_required_fields_present:332` | `INV-005: the sync call emitted no record the test could wait for` |

Single root cause for all ten: `src/backend/logging/_decorator.py` (231 lines) is still the pre-change **loguru** implementation. Its records go to loguru sinks that T-001 removed, so no traced record reaches the pipeline's file sink (8 failures), and `logged` still has parameters `func, level, slow_threshold_ms, slow_threshold_setting, include_args, context_getter, depth` (2 failures).

#### Pre-implementation baseline for T-002's `green_command` set

The `green_command` set verbatim → **14 failed, 60 passed (168.02 s)**. The 10 above plus **4 more reds this task owns** (the first three are the T-001-side consequence of `setup_logger` no longer being decorated):

| Test | Failure (verbatim) | Why it is red / what fixes it |
|---|---|---|
| `logging_coverage/test_inventory.py::test_inventory_covers_all_public_classes:24` | `setup_logger is not traced with @logged` | `INVENTORY_MODULE_FUNCTIONS` (`tests/logging_coverage_test_helpers.py:74-83`) lists `setup_logger` and `get_settings`; T-001's rewrite left `setup_logger` undecorated → re-apply `@logged` in `_pipeline.py` |
| `logging_coverage/test_slow_threshold.py::test_traced_classes_have_concrete_threshold:41` | `setup_logger has no concrete slow_threshold_ms (got None)` | same — the decorator must keep storing the resolved threshold on the wrapper |
| `logging_coverage/test_services_traced.py::test_module_functions_traced:136` | `setup_logger: expected at least 1 entry record` | same — and that entry record must reach the re-implemented capture |
| `test_logging_contracts.py::test_nfr_003_diagnose_false:116` | `assert False` on `wait_for_file_content(log_file, "nfr_003 leak test")` | the test emits through **loguru** (`logger.exception`, line 113), which no longer has a sink. Test-side adaptation inside T-002's allowed files: emit through the feature's own entry point; the assertion (`secret not in content`) stays exactly as written |

#### Implementation brief for S4.2

**(a) What the rebuilt `@logged` / `@logged_class` must produce.**

Record classification is defined by the helpers, not by the test: `wait_for_traced_record` (`tests/logging_test_helpers.py:338-353`) calls a record **exit** iff it carries `elapsed_ms`, **exception** iff it carries `exception`, and **entry** iff it carries **neither**. So:

| Record | Event text | Extra fields | Level |
|---|---|---|---|
| entry | `>> {func.__qualname__} called` (+ ` {_format_args(...)}` when `include_args`) | none | the `level` param (default `DEBUG`) |
| exit | `<< {qualname} returned in {elapsed_ms:.3f} ms` | `elapsed_ms` as a **number**, not a string — AC-003 reads it from the parsed JSON | `level`, or `WARNING` when `elapsed_ms > slow_threshold_ms` |
| exception | `!! {qualname} raised {Type}({msg})` | `exception` = `{type, message, frames}` — produced by the pipeline's `exception_field` processor, **not** by the decorator | `level` |

- The text wording is **load-bearing**: `entry_records` / `exit_records` / `exception_records` filter on the `>>` / `<<` / `!!` prefixes, `parse_elapsed_ms` greps `returned in ([\d.]+) ms`, and `test_module_functions_traced` / `test_secret_args` / `test_abc_traced` assert the exact prefixes. Keep the three templates byte-identical and add `elapsed_ms` as a bound field on top.
- `record_mentions` matches the token in `event` **or** `logger`, so the qualname must stay in the event text.
- Exception path: emit with `exc_info` set (structlog's `exception()` sets `exc_info=True`; `_renderers.exception_field` then falls back to `sys.exc_info()` in the emitting thread and renders type / message / **frames** only — `_traceback_frames` reads `linecache` source text, never frame locals). Do **not** build the `exception` dict in the decorator: the pipeline owns it (D7). The exception still propagates unchanged (AC-012).
- AC-003 forbids the keys `filename`, `lineno`, `_record`, `_from_structlog` in the rendered record (`tests/acceptance/logging/test_pipeline_backend.py:64-65`); `_renderers.INTERNAL_FIELDS` additionally drops `exc_info`, `stack_info`, `positional_args`. Consequence: **never pass positional arguments to the logger** — there is no `PositionalArgumentsFormatter` in `_EMITTING_CHAIN`, so they would land in `positional_args` and be dropped (the same trap recorded as note A of S4.1 T-005). Build the event text with f-strings.
- AC-013 (`tests/contract/logging/test_tracing_surface.py:60-77`) inspects `inspect.signature(feature.logged).parameters`: `context_getter` and `depth` must be **absent**, and `logged(context_getter=None)` / `logged(depth=1)` must raise `TypeError`. Delete both parameters, `_format_context`, and the `logger.opt(depth=...)` line — no shim, no alias (D6). `level`, `slow_threshold_ms`, `slow_threshold_setting`, `include_args` stay with their current semantics (`_resolve_slow_threshold` and the byte-identical `_format_args` stay as they are).
- Keep the markers the coverage suite inspects: `wrapper.__logged__`, `wrapper.slow_threshold_ms` (concrete, `> 0`), `cls.__logged_class__`, `cls.slow_threshold_ms`; `logged_class` keeps skipping private methods (`_is_private_method`) and keeps applying the threshold to every public method (AC-014, AC-007).
- The sync/async split (`inspect.iscoroutinefunction`) stays; AC-011 requires both flavors to emit entry + exit-with-`elapsed_ms` at the configured level. `elapsed_ms` from `time.perf_counter` (INV-003, non-negative). logging-coverage INV-001: exactly one entry + one exit per call.
- The `level` parameter is a **string name**; drive the stdlib method (`logger.debug/info/warning/error`, or `logger.log(number, ...)`) so `add_level_field` reads the authoritative `record.levelname` — AC-011 asserts `entry["level"] == "INFO"` for `level="INFO"`.

**(b) Capture-surface re-implementation plan** (`implementation_steps` item 5; `tests/conftest.py`, `tests/logging_coverage_test_helpers.py`, `tests/logging_test_helpers.py` — public signatures unchanged).

The interface the suite actually uses (measured over all consumers: `str(r)` ×21, `entry_records` ×17, `exit_records` ×11, `level_name` ×6, `for_qualname` ×6, `capture_records` ×4, `messages` ×3, `r["level"].name` ×2, `exception_records` ×1, `log_records.clear()` ×1). The replacement must therefore keep, per captured record: `str(record)` → the event text; `record["level"].name` → the level name (an object with a `.name` attribute — today `_Captured` hands back loguru's `Level`); `record["record"]` → the whole record; and a plain `list` (`.clear()` is called by `tests/contract/authentication/test_logging.py:13`).

Facts the implementer must design against:

1. **Attach to the pipeline logger, not the root.** Traced records go to `logging.getLogger("backend.logging")`, which is `propagate = False` (`_pipeline.py`). A handler on the root logger never sees them — use `logging_test_helpers.pipeline_logger()` (or the name) and set the handler's own level to `DEBUG`. The session fixture already sets `logging.log_level = DEBUG` (`tests/conftest.py:44`), so DEBUG entry records pass the logger's level filter.
2. **A raw handler receives the event dict, not a rendered line.** With `ProcessorFormatter.wrap_for_formatter`, the record's `msg` **is the event dict** — the render chain runs inside the formatter (on the listener thread for the file sink) — and only `_EMITTING_CHAIN` (`callsite_adder`, `exception_field`) has run by then. So the shim must normalize: message text = `msg["event"]` when `msg` is a dict, else `record.getMessage()`; level = `record.levelname`; `record["record"]` = that dict. Do **not** run the pipeline formatter inside the capture handler (double rendering, and the file sink's formatter belongs to the listener thread).
3. **The intermediate state is dual-backend.** Until T-004/T-005/T-006 the settings registry and repository, the event bus and `src/backend/permissions/service.py` still emit through **loguru**, and `tests/acceptance/logging_coverage/test_direct_loguru_kept.py` (in `green_command`, deleted only by T-006) asserts their literal wording inside the capture; `test_levels.py` needs the bus's ERROR and the registry's WARNING through the same capture. So the fixture must keep its loguru sink **and** add the stdlib handler — mark that as a temporary dual capture with a comment naming the task that removes the loguru half.
4. `capture_records(level="DEBUG")` (`tests/logging_coverage_test_helpers.py:156-172`) and `_LiveMessages._texts()` keep their signatures — 4 call sites in `tests/property/logging_coverage/test_invariants.py` plus the settings / filemanagement / search / usermanagement contract suites — with the same normalization as `_Captured`.
5. Keep the fixture's `_drain_event_bus()` preamble (`tests/conftest.py:106-152`). Its stated reason (a stale `SettingChanged` triggering `logger.remove()`) no longer applies — `_reconfigure` mutates handlers in place and never removes a sink — but the drain still isolates cross-test bus traffic, and keeping it is the zero-risk choice.

**(c) Amended NFR-002 budget** (`implementation_steps` item 6, spec NFR-002): `@logged` overhead **< 1 ms/call measured with the two managed sinks active at DEBUG**, nothing disabled. Re-measured for this pipeline: **0.148 ms/call** with console + queue + rotating file active at DEBUG (n = 3), and **0.006 ms/call** for the tracing machinery alone with no handler attached. The old gate's backend-specific disable/enable call disappears with the backend. The witness `test_nfr_002_decorator_overhead_budget` already passes at this step — do not re-tune it.

**(d) The two T-001 exemptions T-002 must turn GREEN.**

| Test | Status at `1a5ceb8` | In `green_command`? |
|---|---|---|
| `tests/acceptance/logging/test_pipeline_backend.py::test_ac_003_file_record_fields_as_json` | RED (listed above) | yes |
| `tests/integration/logging/test_logging_integration.py::test_stdlib_loguru_decorator_pipeline:36` | **RED** (re-measured this step: `assert False` on `wait_for_file_content(log_file, "integration_work_fn" and "<<")`) | **no** — S4.2 must run it explicitly; it is T-002's own exemption |

**(e) AC-016: the protection for the traced path must sit at the emitting call site.** `tests/acceptance/logging_coverage/test_sink_failure.py::test_ac_016_call_unaffected_by_failing_file_sink` replaces `queue_handler.emit` **on the instance** with a raising function. `Logger.callHandlers` → `Handler.handle()` does **not** guard `emit()`, and `_PipelineQueueHandler.emit`'s own guard is bypassed by the instance override. The test passes today only because the traced call still goes through loguru; once the decorator emits through the pipeline, that `RuntimeError` travels into `SqliteUserRepository.get_by_username` and the test fails. So the rebuilt decorator must not let an emitting failure reach the caller (guard the logging call, or route it through a helper that does) — the reasoning `_ForwardingHandler.emit` already records in its comment. Do not "fix" it by touching the test.

**(f) Import-cycle trap for re-decorating `setup_logger`.** `_pipeline.py` must import `logged` in order to decorate `setup_logger` (the three reds in the baseline table), while `_decorator.py` needs the pipeline's `get_logger()` — which also runs `_configure_structlog()`, so a bare `structlog.get_logger()` before `setup_logger()` would bind to structlog's default `PrintLogger` and lose EDGE-006. A module-level `from backend.logging._pipeline import get_logger` in `_decorator.py` is circular. Follow the pattern already in `_decorator.py:55-57`: import inside the wrapper (or inside a one-line `_tracing_logger()` helper), with the same "imported here to avoid a circular import" comment.

**(g) Blast radius: every consumer of the capture surface.** 27 test modules read `log_records` / `capture_records`; only part of them is in `green_command`, so the rest is the collateral check S4.2 must run (the discipline T-001 recorded):

| In `green_command` (GREEN at this task's gate) | Outside `green_command` (collateral check — must not regress) |
|---|---|
| `unit/logging/test_logging.py` (20), `unit/logging/test_logging_edges.py` (4), `acceptance/logging_coverage/test_services_traced.py` (11), `test_secret_args.py` (10), `test_levels.py` (5), `test_sink_failure.py` (3), `test_abc_traced.py` (3), `test_slow_threshold.py` (2), `test_direct_loguru_kept.py` (2), `test_behavior_unchanged.py` (1), `property/logging/test_logging_properties.py` (3), `property/logging_coverage/test_invariants.py` (5), `contract/authentication/test_logging.py` (3), `contract/mail/test_logging.py` (2), `acceptance/authentication/test_logging.py` (2), `acceptance/mail/test_logging.py` (2) | `unit/logging_coverage/test_edge_cases.py` (11), `acceptance/sessionmanagement/test_observability.py` (9), `contract/usermanagement/test_usermanagement_contracts.py` (4), `contract/search/test_search_contracts.py` (4), `contract/filemanagement/test_filemanagement_contracts.py` (4), `contract/settings/test_settings_contracts.py` (3 — uses `r["level"].name` directly), `acceptance/search/test_search.py` (3), `acceptance/permissions/test_check_api.py` (3), `acceptance/filemanagement/test_filemanagement.py` (2), `contract/mail/test_secrets.py` (2), `contract/authentication/test_secrets.py` (2) |

#### Completion gates (T-002, verbatim from the DAG)

1. RED observed on the `red_command` set; recorded in `docs/verification/structlog-logging.md`. **← this step**
2. AC-003, AC-011, AC-012, AC-013, AC-014, AC-015 tests pass.
3. Property tests for INV-002, INV-003, INV-005 pass (INV-002 is also the NFR-003 witness).
4. Contract gate NFR-002: `@logged` overhead < 1 ms/call with both managed sinks active at DEBUG (nothing disabled).
5. The whole `logging_coverage` suite and the four cross-feature logging tests pass with unchanged assertions (this breaking change is fixed inside this task, not deferred to Phase 5).
6. `uv run ruff check <changed paths>` clean; `uv run mypy src/` clean.
7. `uv run python scripts/check_traceability.py` stays green.

#### Gate table (S4.1, T-002)

| Gate | Command | Result |
|---|---|---|
| Task ready | T-002 `dependencies: ["T-001"]` (VERIFIED), `status: "PENDING"` | confirmed |
| Its tests present | `--collect-only -q` on the `red_command` set | **11 collected** |
| RED re-observed | T-002 `red_command` verbatim | **10 failed, 1 passed (135.40 s)** — 10 `AssertionError`s, 0 errors |
| Drift vs S3.2 (11 failed / 0 passed) | one test newly green: `test_nfr_002_decorator_overhead_budget` | explained (T-001 pipeline + amended budget); no test changed since S3.2 |
| `green_command` baseline (pre-implementation) | the `green_command` set verbatim | **14 failed, 60 passed (168.02 s)** — the 10 plus 4 owned reds |
| T-001 exemptions located | `test_ac_003_file_record_fields_as_json`, `test_stdlib_loguru_decorator_pipeline` | both RED; the second is outside `green_command` |
| Capture-surface blast radius enumerated | grep over `tests/` | 27 consumer modules; interface reduced to 6 accessors |
| No implementation written | this step changed only `docs/verification/structlog-logging.md` | confirmed |

**Phase 4 (S4.1, T-002) gate: PASS — RED re-confirmed.** Next: S4.2 (T-002) — rebuild `_decorator.py` on the pipeline and re-implement the capture helpers, then confirm GREEN on the `green_command` set plus the two T-001 exemptions and the collateral check.

### S4.2 T-002 — the full-suite hang root-caused and fixed, then GREEN confirmed (2026-10-06)

**Relaunch context.** The first S4.2 (T-002) execution was interrupted after three `[checkpoint]` commits (`7092f13`, `88b23b7`, `05a1b88`) on top of the S4.1 checkpoint `b0a932f`. This step finished the task and, ahead of everything else, root-caused the full-suite **hang** the checkpoints had introduced.

#### The blocker: the full suite hung instead of finishing

`uv run pytest tests/ -p no:randomly -p faulthandler -o faulthandler_timeout=90 -q` never terminated. The `faulthandler` dump (`C:/workspace/tmp/suite4.log`) showed the main thread parked in `tests/logging_test_helpers.py:40` — `while not pending.empty(): time.sleep(0.001)` inside `_drain_queue()` — reached from `test_setup_logger.py::test_ac_017_live_reconfigure` → `wait_for_record`. The dump listed **no queue-listener thread at all** (only the main thread and two idle `eventbus-worker` threads): the listener that drains the file sink's queue was **dead**, so the queue never emptied and the helper's unbounded wait never returned.

**Minimal reproduction (two files, no randomness):**

```text
uv run pytest tests/acceptance/logging_coverage/test_sink_failure.py tests/acceptance/settings_coverage/test_setup_logger.py -p no:randomly -q
```

→ hang, same dump. The whole `settings_coverage` directory passes alone (9 passed), which is why the failure looked like a cross-test interaction.

#### Root cause (implementation, not test)

`tests/acceptance/logging_coverage/test_sink_failure.py::test_ac_016_call_unaffected_by_failing_file_sink` (the AC-016 witness Phase 3 derived for T-001) replaces the rotating file handler's `emit` **on the instance** with a function that raises `RuntimeError`. That is the point of the test — a broken managed file sink.

The stdlib listener loop does not survive it. `logging.handlers.QueueListener._monitor` (CPython 3.14, `logging/handlers.py:1608-1621`) wraps the whole loop body in `try: … except queue.Empty: break` — **only** `queue.Empty`. An exception escaping `self.handle(record)` therefore propagates out of `_monitor` and ends the listener thread:

```text
File "...\logging\handlers.py", line 1618, in _monitor
    self.handle(record)
File "...\logging\handlers.py", line 1599, in handle
    handler.handle(record)
File "...\logging\__init__.py", line 1027, in handle
    self.emit(record)
RuntimeError: managed file sink is down
```

The stdlib `Handler.emit` guard (`except Exception: self.handleError(record)`) is *inside* the handler's own `emit`, so an instance-level override that raises bypasses it, and `QueueListener` has **no** `handleError` of its own. The test restores `rotating.emit` in its `finally`, but the thread is already gone: from that point on, every record headed for the file sink is enqueued and never written, and every later `wait_for_file_content` / `wait_for_record` that reaches `_drain_queue()` blocks forever. Reproduced standalone (`C:/workspace/tmp/repro_listener_dead.py`): `threads after patch: ['MainThread', 'eventbus-worker']`, `queue empty? False`.

So the amplification is the real defect, independent of the test: **one broken sink takes the whole file sink down for the remaining lifetime of the process** — the AC-016 / REQ-013 guarantee ("a log sink failure must not interrupt the call") held for the emitting call but silently broke the sink itself.

#### The fix (`src/backend/logging/_pipeline.py`)

`_PipelineQueueListener(logging.handlers.QueueListener)` overrides `handle()` so one record's failure is reported and the drain loop continues; `_install` now builds the listener through it. Reporting goes through the handlers' own `handleError` (stdlib traceback on stderr) under `contextlib.suppress`, since `QueueListener` has no `handleError`.

Second, related thread-safety fix found while reading the same path: `_move_file_handler` closed and reopened the rotating handler's stream from the settings-change thread while the listener thread was writing to it. The swap now takes the handler's own lock (`Handler.acquire()` / `release()` — the lock `Handler.handle()` holds around `emit`; `RLock`, and `FileHandler.close()` re-enters it safely).

**No test was weakened.** `tests/logging_test_helpers.py::_drain_queue` is left exactly as Phase 3 wrote it: waiting for the listener to drain is the correct contract, and the hang was a dead listener, not a wrong helper.
#### Regression witness for the fix (written before the fix, RED observed first)

`tests/acceptance/logging_coverage/test_sink_failure.py::test_ac_016_file_sink_keeps_working_after_a_failing_sink` — the AC-016 witness extended to the *sink's* lifetime: break `rotating.emit`, emit one record into the broken window, restore, then require (a) the queue to drain within a bounded `wait_for` (fails fast instead of hanging) and (b) a record emitted **after** the window to reach the file sink.

| Step | Command | Result |
|---|---|---|
| RED (listener reverted to `logging.handlers.QueueListener`, fix withheld) | `uv run pytest tests/acceptance/logging_coverage/test_sink_failure.py::test_ac_016_file_sink_keeps_working_after_a_failing_sink -q -p no:randomly` | **1 failed in 5.66 s** — `AC-016: the queue listener must keep draining after a sink failure` |
| GREEN (`_PipelineQueueListener` installed) | `uv run pytest tests/acceptance/logging_coverage/test_sink_failure.py -q -p no:randomly` | **3 passed in 0.77 s** |
| Hang gate | `uv run pytest tests/acceptance/logging_coverage/test_sink_failure.py tests/acceptance/settings_coverage/ -p no:randomly -q` | **11 passed in 2.12 s** (was: hang) |

#### T-002 implementation state at this step

The three checkpoint commits already carried the task's implementation; this step verified it against the S4.1 brief and completed the missing evidence. What is in place:

- `src/backend/logging/_decorator.py` rebuilt on the pipeline: `_Tracer` emits `>> {qualname} called` / `<< {qualname} returned in {ms} ms` (+ `elapsed_ms` as a number) / `!! {qualname} raised {Type}({msg})` through `get_logger()`; sync **and** async wrappers (`inspect.iscoroutinefunction`); slow exit escalated to WARNING; `exc_info=True` inside the `except` block so `_renderers.exception_field` renders type + message + frames (never locals); `contextlib.suppress(Exception)` around the emit so a broken sink never reaches the traced call (brief item (e)); markers `__logged__` / `slow_threshold_ms` / `__logged_class__` kept.
- `context_getter` and `depth` deleted with no shim (AC-013, D6); `level`, `slow_threshold_ms`, `slow_threshold_setting`, `include_args` unchanged, `_format_args` byte-identical.
- Capture surface re-implemented (`tests/conftest.py`, `tests/logging_coverage_test_helpers.py`, `tests/logging_test_helpers.py`): `PipelineCaptureHandler` on the pipeline logger with level parity (`pipeline_capture` sets and restores the logger level), `CaptureRecord` normalising `str(r)` / `r["level"].name` / `r["record"]`, the temporary dual loguru half named with the task that removes it (T-006).
- `setup_logger` re-decorated with `@logged(level="INFO", slow_threshold_ms=25.0)` in `_pipeline.py` (the three T-001 reds in the S4.1 baseline table).

#### GREEN gate — the DAG's own `green_command`, verbatim

```text
uv run pytest tests/acceptance/logging/test_tracing_records.py tests/acceptance/logging/test_secrets.py tests/acceptance/logging/test_pipeline_backend.py::test_ac_003_file_record_fields_as_json tests/unit/logging/ tests/property/logging/test_pipeline_invariants.py tests/property/logging/test_logging_properties.py tests/contract/logging/test_tracing_surface.py tests/contract/logging/test_logging_contracts.py tests/acceptance/logging_coverage/test_abc_traced.py tests/acceptance/logging_coverage/test_behavior_unchanged.py tests/acceptance/logging_coverage/test_docstrings.py tests/acceptance/logging_coverage/test_inventory.py tests/acceptance/logging_coverage/test_levels.py tests/acceptance/logging_coverage/test_new_classes_traced.py tests/acceptance/logging_coverage/test_secret_args.py tests/acceptance/logging_coverage/test_services_traced.py tests/acceptance/logging_coverage/test_slow_threshold.py tests/acceptance/logging_coverage/test_direct_loguru_kept.py tests/unit/logging_coverage tests/property/logging_coverage tests/acceptance/authentication/test_logging.py tests/contract/authentication/test_logging.py tests/acceptance/mail/test_logging.py tests/contract/mail/test_logging.py -v
```

→ **74 passed, 0 failed (19.51 s)** — from the S4.1 baseline of **14 failed, 60 passed**. The `red_command` set (11 tests) is a subset of it and is likewise green.

**T-002's own exemption outside `green_command`** (S4.1 brief item (d)): `tests/integration/logging/test_logging_integration.py::test_stdlib_loguru_decorator_pipeline` — was RED at `1a5ceb8`, now **2 passed in 0.52 s** for `tests/integration/logging/`. The test-side change raises the **root** logger's level for its own AC-006 given and restores it (the feature never re-levels the root, INV-004); the assertions are unchanged.
#### Collateral check (S4.1 brief item (g), the capture-surface consumers outside `green_command`)

```text
uv run pytest tests/acceptance/sessionmanagement/test_observability.py tests/contract/usermanagement/test_usermanagement_contracts.py tests/contract/search/test_search_contracts.py tests/contract/filemanagement/test_filemanagement_contracts.py tests/contract/settings/test_settings_contracts.py tests/acceptance/search/test_search.py tests/acceptance/permissions/test_check_api.py tests/acceptance/filemanagement/test_filemanagement.py tests/contract/mail/test_secrets.py tests/contract/authentication/test_secrets.py tests/acceptance/logging_coverage/test_sink_failure.py -q -p no:randomly
```

→ **132 passed, 1 skipped** (the known `test_filemanagement.py:364` symlink skip) in 53.37 s. No assertion changed.

#### Hang gate — the FULL suite

```text
uv run pytest tests/ -q
```

→ **754 passed, 7 failed, 1 skipped in 233.84 s**. The suite **completes**; the wall clock is back in the pre-hang order (~230–300 s), not thousands of seconds. The single skip is `tests/acceptance/filemanagement/test_filemanagement.py:364` (symlinks unavailable on this host).

The 7 failures are all **later DAG tasks' Phase 3 reds**, unchanged from the pre-existing set and none owned by T-002:

| Failing test | Owner |
|---|---|
| `test_statements_via_feature.py::test_ac_009_settings_statements_go_through_get_logger` | T-004 |
| `test_statements_via_feature.py::test_ac_009_eventbus_statements_go_through_get_logger` | T-005 |
| `test_statements_via_feature.py::test_ac_009_statements_go_through_get_logger` | T-006 |
| `test_pipeline_backend.py::test_ac_001_no_backend_import_and_stdlib_chain` | T-006 |
| `test_dependency_contract.py::test_ac_018_dependency_report_clean` | T-006 |
| `test_dependency_contract.py::test_ac_019_guidance_names_feature_entry_points` | T-007 |
| `unit/test_settings_coverage.py::test_observability_tracing` | T-003 (`red_command` lists it) |

#### Quality gates

| Gate | Command | Result |
|---|---|---|
| Ruff (lint) | `uv run ruff check src/backend/logging/_decorator.py src/backend/logging/_pipeline.py tests/acceptance/logging_coverage/test_services_traced.py tests/acceptance/logging_coverage/test_sink_failure.py tests/conftest.py tests/contract/logging/test_logging_contracts.py tests/integration/logging/test_logging_integration.py tests/logging_coverage_test_helpers.py tests/logging_test_helpers.py tests/property/logging_coverage/test_invariants.py tests/unit/logging_coverage/test_edge_cases.py` | **All checks passed!** |
| Ruff (format) | same paths, `ruff format --check` | **11 files already formatted** |
| Types | `uv run mypy src/` | **Success: no issues found in 84 source files** |
| Traceability | `uv run python scripts/check_traceability.py` | **PASS (784 matrix rows, 129 spec IDs, 745 test functions)** |

#### Scope deviations recorded honestly

1. `tests/acceptance/logging_coverage/test_sink_failure.py` and `tests/integration/logging/test_logging_integration.py` are **not** in T-002's `allowed_files.test_files`, and the new AC-016 listener witness is a test this task added rather than one the DAG's `tests_to_create` listed. Justification: the S4.1 brief names `test_stdlib_loguru_decorator_pipeline` as "T-002's own exemption" that S4.2 must run, and `test_sink_failure.py` is the AC-013/AC-016 home for the sink-failure contract this task's decorator now routes through the pipeline (brief item (e)). In every case the **assertions were not weakened** — the mechanism under observation changed from a loguru sink to a pipeline handler, and the added witness only *strengthens* AC-016.
2. The listener fix is an implementation change inside `_pipeline.py`, which T-002's `allowed_files` admits as "(binding helpers only, if needed)". It adds no behavior beyond REQ-013/AC-016: it keeps the specified guarantee true for the sink itself instead of only for the emitting call. No spec amendment is required; if Phase 5 wants the lifetime clause spelled out, that is a spec-amendment candidate, not new behavior.

#### Gate table (S4.2, T-002)

| Gate | Result |
|---|---|
| Full-suite hang eliminated | **PASS** — suite completes, 233.84 s, no listener-thread loss |
| Root cause found in the implementation | **PASS** — `QueueListener._monitor` guards only `queue.Empty`; fixed with `_PipelineQueueListener` |
| Regression witness RED→GREEN | **PASS** — 1 failed (5.66 s) → 3 passed (0.77 s) |
| `green_command` GREEN | **PASS** — 74 passed / 0 failed |
| T-002 exemption (`integration/logging`) GREEN | **PASS** — 2 passed |
| Collateral check | **PASS** — 132 passed, 1 known skip |
| Ruff on changed paths (check + format) | **PASS** |
| `mypy src/` | **PASS** |
| `check_traceability.py` | **PASS** |
| No test weakened or deleted | **PASS** |

**Phase 4 (S4.2, T-002) gate: PASS — GREEN confirmed.** Next: S4.3 (T-002) refactor pass, then S4.4 sets `VERIFIED`.

### S4.3 (T-002) — Refactor pass (keep GREEN)

**Objective:** improve the structure of T-002's changed code without changing specified behaviour.

#### What was reviewed

T-002's changed paths: `src/backend/logging/_decorator.py`, `src/backend/logging/_pipeline.py`,
`tests/conftest.py`, `tests/logging_coverage_test_helpers.py`, `tests/logging_test_helpers.py`,
`tests/acceptance/logging_coverage/test_sink_failure.py`, `tests/acceptance/logging_coverage/test_services_traced.py`,
`tests/contract/logging/test_logging_contracts.py`, `tests/integration/logging/test_logging_integration.py`,
`tests/property/logging_coverage/test_invariants.py`, `tests/unit/logging_coverage/test_edge_cases.py`.

**Source side: no change needed.** S4.2's `_Tracer` already removed the sync/async duplication that
`_wrap_sync`/`_wrap_async` carried (the level resolution, the record text and the sink-failure guard now
live in one place), and `_pipeline.py` shares its formatter construction (`_formatter_for`) and its
renderer-pair default (`_renderer_pair`) between `_install` and `_reconfigure`. The two level helpers are
not duplicates: `_decorator._level_method` maps a level *name* to the bound-logger method (AC-011), while
`_pipeline._level_of` maps the configured level to a stdlib *number* (REQ-002). The three emit guards
(`_PipelineQueueHandler.emit`, `_PipelineQueueListener.handle`, `_ForwardingHandler.emit`, plus
`_Tracer._emit`) sit at four different boundaries of the emission path — collapsing any one of them would
drop the AC-016 guarantee for the others. No source file was touched.

**Test side: two real duplications introduced by S4.2 were removed.**

1. **The failing-sink harness block, three copies.** `FailingHandler()` + `pipeline_logger().addHandler(...)`
   + `try:` + `finally: removeHandler(...)` appeared verbatim in `test_sink_failure.py`
   (`test_sink_failure_does_not_interrupt`), `test_edge_cases.py` (`test_sink_failure_graceful`) and
   `test_invariants.py` (`test_tracing_never_interrupts_call`). Replaced by one context manager,
   `failing_sink_attached()`, next to `FailingHandler` in `logging_coverage_test_helpers.py` — the same
   shape the neighbouring `pipeline_capture` already uses. The handler-attach ordering rule (the capture
   handler must be attached first, because stdlib does not guard one handler's `emit` from the next) is now
   stated once, in the helper's docstring, instead of being re-explained at each call site. The
   `pipeline_logger` import dropped out of `test_invariants.py` and `test_edge_cases.py` (the latter keeps
   `managed_sinks`) and out of `test_sink_failure.py`.
2. **`exploding_emit` defined twice in one file.** `test_sink_failure.py` defined the identical nested
   `exploding_emit` in both AC-016 tests and repeated the `handler.emit = ...` / `finally: del handler.emit`
   dance. Replaced by one module-local `broken_emit(handler)` context manager, used as
   `with broken_emit(queue_handler), broken_emit(rotating):` and `with broken_emit(rotating):`.

#### What was deliberately NOT changed

- `_PipelineQueueHandler.emit` re-states the guard stdlib's `QueueHandler.emit` already performs. It is
  redundant by construction, but it is **pre-existing T-001 code with an explicit rationale comment**
  (the AC-016 guarantee must not depend on a stdlib implementation detail), and it is outside T-002's
  refactor scope. Left as is.
- `_CAPTURED_DROP` (capture side) vs `_renderers.PROCESSOR_META_FIELDS` / `INTERNAL_FIELDS` (render side)
  look like duplicates but are not: the capture reads the event dict *before* the render chain runs, so it
  drops a different set (`exc_info`/`stack_info` markers, not the callsite fields the render chain adds).
  Coupling the test helper to the renderer's private constants would be a false sharing.
- No test assertion was weakened, added or removed; the only test edits are structural (context managers
  and imports). No new dependency, no new abstraction beyond the two context managers that replace the
  duplicated blocks.

#### Evidence (S4.3, T-002)

| Gate | Command | Result |
|---|---|---|
| Baseline before refactor | `green_command` | 74 passed in 19.66 s |
| GREEN after refactor | `green_command` + `tests/acceptance/logging_coverage/test_sink_failure.py` | **77 passed in 19.87 s** (74 + the 3 sink-failure tests, which the `green_command` set does not list) |
| Lint | `uv run ruff check <4 changed paths>` | **All checks passed** |
| Format | `uv run ruff format <4 changed paths>` | **4 files left unchanged** |
| Types | `uv run mypy src/` | **Success: no issues found in 84 source files** (no source file touched) |

Diff: 4 test files, `+49 / −44`. Behaviour: unchanged — the same handlers are attached and detached in the
same order, and the same `emit` overrides are installed and removed.

**S4.3 (T-002) gate: PASS — refactored, GREEN maintained.** Next: S4.4 (T-002) commit + set `VERIFIED`.

---

### S4.1 (T-005) — RED re-confirmed at 2b047e4 (2026-10-06)

**Re-entry.** T-005 was picked once before (commit `1a5ceb8`, HEAD `1dc155c`). That observation predates **T-002** — decorators rebuilt on the pipeline, capture helpers re-implemented, `QueueListener` fix — so RED is re-observed here before S4.2 (T-005) implements. The DAG entry was re-read verbatim: `task_id: "T-005"`, `feature_group: backend.eventbus`, REQ-005 / AC-009, amended `logging-coverage.md` v2 REQ-010 / AC-010, and its `red_command`, `green_command`, `implementation_steps`, `design_constraints`, `completion_gates` are unchanged.

#### Readiness check (re-run)

| Check | Evidence at `2b047e4` | Result |
|---|---|---|
| Dependencies satisfied | `dependencies: ["T-001"]` → `VERIFIED`; T-002 also `VERIFIED` (S4.4, `2b047e4`) | satisfied |
| Status still `PENDING` | `.github/task-runner/tasks.json`: T-001 `VERIFIED`, T-002 `VERIFIED`, T-003..T-007 `PENDING` | confirmed |
| Its test exists | `tests/acceptance/logging_coverage/test_statements_via_feature.py::test_ac_009_eventbus_statements_go_through_get_logger` — collected and run below | confirmed |
| Migration target unchanged | no commit since `1dc155c` touches `src/backend/eventbus/` or any `tests/*/eventbus` directory; the only backend import is still line 20 `from loguru import logger`, `from backend.logging import logged, logged_class` still line 22 | confirmed |
| Working tree | `git status --short` clean at HEAD `2b047e4` | confirmed |

#### RED re-confirmed (the DAG's own `red_command`, verbatim)

```text
uv run pytest tests/acceptance/logging_coverage/test_statements_via_feature.py::test_ac_009_eventbus_statements_go_through_get_logger -v
```

→ **1 failed, 0 passed (0.32 s)** — identical to the S3.2 gate and to the `1a5ceb8` re-confirmation: **no drift** from T-001/T-002 landing. One `AssertionError` at `test_statements_via_feature.py:149`; **no import, collection, fixture or test-data error** (the witness builds no model instance):

```text
AssertionError: AC-009 / REQ-005 (logging-coverage REQ-010 v2): src/backend/eventbus/eventbus.py imports a logging backend: ['loguru.logger']; src/backend/eventbus/eventbus.py statements not written through get_logger(): line(s) [86, 96, 115, 120, 136, 176, 197, 205, 222, 233]; a module under src/backend/eventbus/ imports a logging backend: ['src/backend/eventbus/eventbus.py']
```

Failure reason per clause: (1) the file still imports a logging backend (`loguru.logger`); (2) all **10** statement receivers are the backend-bound `logger`, not a `get_logger()`-bound one — the same 10 line numbers as at `1dc155c`, so the scope did not move; (3) the feature-wide clause repeats (1). The **count clause contributes no violation** (the file already holds exactly REQ-005's 10 statements), so the witness is red exactly on what T-005 fixes.

#### Neighborhood and baselines at `2b047e4`

| Measurement | Command | Result |
|---|---|---|
| `green_command` set minus the witness (no-delta guard) | the five eventbus test directories (`-q`) | **31 passed (4.05 s)** — unchanged from `1dc155c`; must still be 31 after T-005 |
| deptry | `uv run deptry .` | **Success! No dependency issues found** (90 files) — loguru still declared *and* still imported by settings/permissions (T-006 interlock) |
| `tests/acceptance/logging_coverage` (`-q`) | same directory | **3 failed, 18 passed** — red: T-005's eventbus witness, T-004's settings witness, T-006's all-four-features witness `test_ac_009_statements_go_through_get_logger`. AC-016's witness is GREEN since T-002 (red at S3.2) |
| Cross-task tests note B flagged (`test_levels.py`, `test_direct_loguru_kept.py`) | `-q` on those two files | **2 passed (0.52 s)** — green baseline T-005 must not break |

#### What changed since the `1a5ceb8` observation (T-002 landed)

- **Note B is resolved.** `log_records` (`tests/conftest.py:84`) is now **dual-backend** (`loguru_sink` + `pipeline_capture`, T-002), so a bus statement migrated to `get_logger()` is still captured: `test_semantic_log_levels` (ERROR from the bus's `logger.exception`) and `test_existing_direct_loguru_kept` (asserts the wording `event bus: published event type` / `event bus: shutdown initiated`) stay green **provided wording and levels are preserved exactly**. They are no longer scheduled to go red at T-005; S4.2 runs them as a collateral check.
- **Note D is obsolete.** `_decorator.py` is pipeline-based since T-002, so after T-005 `eventbus.py` emits through **one** backend — no dual-backend intermediate state.
- **Worker-thread statements (176 / 197 / 205)** are covered by T-002's `_PipelineQueueListener` fix (the full-suite hang root cause); the AC-016 guarantee holds at both handler boundaries, so no `try/except` around the emits.
- **Risk A stands unchanged**: `_EMITTING_CHAIN` has no `PositionalArgumentsFormatter`, so the 8 `'{}'`-style positional messages must become the keyword-field form (`implementation_steps` item 1) or their values are dropped from every rendered record.

#### Gate table (S4.1, T-005 re-entry)

| Gate | Command | Result |
|---|---|---|
| Task ready | T-005 `dependencies: ["T-001"]` VERIFIED, `status: "PENDING"` | confirmed |
| Its test present | collected and executed | confirmed |
| RED re-observed at `2b047e4` | T-005 `red_command` verbatim | **1 failed, 0 passed (0.32 s)** — one `AssertionError`, no import/collection/fixture error |
| Nothing implemented | only `docs/verification/structlog-logging.md` changed in this step | confirmed |

**Phase 4 (S4.1, T-005) gate: PASS — RED re-confirmed at `2b047e4`.** Next: S4.2 (T-005) — implement + confirm GREEN.

---

### S4.2 T-005 — implement + confirm GREEN (2026-10-06)

**Objective:** migrate the 10 direct loguru statements in `src/backend/eventbus/eventbus.py` to the logging feature's `get_logger()` (REQ-005 / AC-009; `logging-coverage.md` v2 REQ-010 / AC-010). Files changed: `src/backend/eventbus/eventbus.py` (the only allowed source file — `__init__.py` untouched, no new export was needed) and `tests/acceptance/logging_coverage/test_statements_via_feature.py` (in T-005's `allowed_files.test_files`; a crash in the witness's own helper, see *Finding 1*).

#### What was implemented

One import line and one module-level binding replace the backend:

```python
from backend.logging import get_logger, logged, logged_class

_logger = get_logger("eventbus")
```

The module-level binding is the pattern T-001 established in `src/backend/logging/feature_settings.py:22` (`_feature_logger = get_logger("logging")`) — one call per module, not one per statement: `get_logger()` re-runs `_configure_structlog()` on every call (`_decorator.py:86`), so an inline `get_logger(...).debug(...)` receiver at all 10 sites would re-configure structlog 10 times per burst. The name `"eventbus"` follows the same feature-name convention and renders as the record's `logger` field. Import direction unchanged (`backend.eventbus → backend.logging`, spec §10 row 3); `logged` / `logged_class` stay as they were.

All 10 call sites converted, level and wording unchanged (spec §9 row 2, "DEBUG/INFO/WARNING as today"):

| Old line | Level | Rendered event text (identical to the loguru output) | Keyword fields |
|---|---|---|---|
| 86 | DEBUG | `event bus: subscribed handler '{h}' for event type '{e}'` | `handler`, `event_type` |
| 96 | DEBUG | `event bus: unsubscribed handler '{h}' for event type '{e}'` | `handler`, `event_type` |
| 115 | DEBUG | `event bus: published event type '{e}'` | `event_type` |
| 120 | WARNING | `event bus: queue full; dropping event type '{e}' (dropped={n})` | `event_type`, `dropped` |
| 136 | DEBUG | `event bus: shutdown initiated` | — |
| 176 | DEBUG | `event bus: started background worker thread` | — |
| 197 | DEBUG | `event bus: dispatching event type '{e}' to handler '{h}'` | `event_type`, `handler` |
| 205 | ERROR (`exception`) | `event bus: handler '{h}' raised for event type '{e}'` | `handler`, `event_type` |
| 222 | DEBUG | `event bus: created shared default instance` | — |
| 233 | DEBUG | `event bus: reset shared default instance` | — |

Statement count stays **exactly 10** (logging-coverage REQ-010 v2): nothing added, removed, folded into a helper, or moved. Where a value appears twice it is bound to a local (`handler_name`, `event_name`) instead of being recomputed — locals only, no new function, no behavior delta (the values were already evaluated eagerly as loguru positional args).

#### Correction to note A of S4.1 (T-005): `str.format` does **not** fill named placeholders here

Note A proposed `"event bus: published event type '{event_type}'"` with `event_type=…`, on the premise that "`str.format` fills named placeholders from the same kwargs that land in the event dict". **That premise is false for this pipeline** — measured against the installed structlog and this chain:

- `structlog.stdlib.BoundLogger._proxy_to_logger` only moves *positional* args into `event_kw["positional_args"]`; it never formats the event string. The base `FilteringBoundLogger._proxy_to_logger` passes the event through unchanged.
- stdlib `LogRecord.getMessage()` interpolates `%`-style `record.args` only, and structlog passes none.
- Probe at this step (`get_logger("probe").debug("… '{event_type}'", event_type="UserCreated")` with the pipeline installed): the console line renders **`event bus: published event type '{event_type}'`** — braces literal, value only in the appended field.

So the message is built with an **f-string** (the pattern T-002's brief already states: "Build the event text with f-strings", §(a) of the S4.1 T-002 block) and the same values are **additionally** passed as keyword fields. That satisfies both halves of spec §9 row 2 — "message + keyword fields, unchanged wording" — and avoids the `positional_args` drop trap note A identified correctly. The rendered wording is byte-identical to the loguru output (evidence below), which is what `test_direct_loguru_kept.py` and `test_levels.py` depend on.

#### Finding 1 — the AC-009 witness helper crashed on the first migrated module (test-code defect, fixed in place)

`_feature_logger_names` (`tests/acceptance/logging_coverage/test_statements_via_feature.py:51`) read `node.target` on an `ast.Assign` node:

```text
AttributeError: 'Assign' object has no attribute 'target'. Did you mean: 'targets'?
```

`ast.Assign` carries a **list** `targets`; only `ast.AnnAssign` has a single `target`. The line is reached only when the parsed module actually contains a `name = get_logger(...)` assignment, so the defect was invisible while every module under test still imported the backend — the first migrated module (this one) surfaced it. The witness therefore failed with a **test-code error, not an `AssertionError` on behavior**, which is not a legal RED/GREEN state (AGENTS.md, Phase 3: a test that crashes on its own data/code is invalid test code, not evidence).

Fix (3 lines, in T-005's `allowed_files.test_files`, shared by all three AC-009 witnesses — one fix, not one per test):

```python
targets = node.targets if isinstance(node, ast.Assign) else [node.target]
for target in targets:
    ...
```

- **No assertion was changed, weakened or deleted** — the clause logic is untouched; the fix makes the third clause *actually evaluate* instead of crashing, i.e. the witness becomes strictly stronger.
- The same defect would have blocked **T-004** (the settings modules get the same module-level binding) and **T-006** (`permissions/service.py`), so fixing the shared helper here removes a third of the re-work those tasks would otherwise hit.
- Status of the other two witnesses is **unchanged** by the fix: `test_ac_009_settings_statements_go_through_get_logger` and `test_ac_009_statements_go_through_get_logger` still fail with the same `AssertionError` naming the settings/permissions statements and their `loguru` imports (T-004 / T-006's reds).

#### Rendered-output evidence (wording and levels preserved, worker-thread statements alive)

Probe run against the installed pipeline at DEBUG (`setup_logger()`, `logging.log_level=DEBUG`), subscribe → publish → failing handler → unsubscribe → shutdown. Console (text renderer):

```text
[DEBUG ] event bus: subscribed handler 'bad' for event type 'E' (eventbus:90)
[DEBUG ] event bus: started background worker thread (eventbus:186)
[DEBUG ] event bus: published event type 'E' (eventbus:123)
[DEBUG ] event bus: dispatching event type 'E' to handler 'bad' (eventbus:208)
[ERROR ] event bus: handler 'bad' raised for event type 'E' (eventbus:216)
  exception: RuntimeError: handler boom
[DEBUG ] event bus: unsubscribed handler 'bad' for event type 'E' (eventbus:103)
[DEBUG ] event bus: shutdown initiated (eventbus:146)
```

File sink (JSON, default renderer) — the keyword fields arrive structured, the callsite still points at `eventbus.py` although the record was emitted on the `eventbus-worker` thread, and the exception record carries type/message/frames only (INV-002, no locals):

```json
{"level":"ERROR","logger":"eventbus","event":"event bus: handler 'bad' raised for event type 'E'","timestamp":"…","file":"eventbus.py","line":216,"handler":"bad","event_type":"E","exception":{"type":"RuntimeError","message":"handler boom","frames":[…]}}
{"level":"DEBUG","logger":"eventbus","event":"event bus: unsubscribed handler 'bad' for event type 'E'","…":"…","file":"eventbus.py","line":103,"handler":"bad","event_type":"E"}
```

No `try/except` was added around any emit (AC-013/AC-016 are enforced at the handler boundaries, T-002's `_PipelineQueueListener` keeps the listener draining) — the three worker-thread statements (176 / 197 / 205) are visible above, emitted from the worker thread.

#### Gate table (S4.2, T-005)

| # | Gate | Command (verbatim) | Result |
|---|---|---|---|
| a | **T-005 GREEN** | `uv run pytest tests/acceptance/logging_coverage/test_statements_via_feature.py::test_ac_009_eventbus_statements_go_through_get_logger tests/acceptance/eventbus tests/unit/eventbus tests/contract/eventbus tests/property/eventbus tests/integration/eventbus -v` | **32 passed, 0 failed (4.19 s)** — the witness PASSED, and the five eventbus directories are the pre-implementation **31 passed** unchanged (no behavior delta) |
| b | Cross-task collateral (note B) | `uv run pytest tests/acceptance/logging_coverage/test_levels.py tests/acceptance/logging_coverage/test_direct_loguru_kept.py -q` | **2 passed (0.53 s)** — the bus's ERROR record and the two literal wordings survive the migration |
| c | Event bus + all contract suites | `uv run pytest tests/acceptance/eventbus tests/integration/eventbus tests/unit/eventbus tests/property/eventbus tests/contract -q` | **2 failed, 76 passed (1:29)** — both failures pre-existing, re-measured at `122caba` with this work stashed: `test_ac_018_dependency_report_clean` (loguru still declared → **T-006**), `test_ac_019_guidance_names_feature_entry_points` (guidance not yet corrected → **T-007**). **No new failure** |
| c+ | Full suite (extra evidence, not a Phase 4 gate) | `uv run pytest tests/ -q` | **7 failed, 754 passed, 1 skipped (4:08)** — 6 reds are the scheduled T-003/T-004/T-006/T-007 set (`test_ac_001_no_backend_import_and_stdlib_chain` → T-006, the two remaining AC-009 witnesses → T-004/T-006, `test_ac_018` → T-006, `test_ac_019` → T-007, `unit/test_settings_coverage.py::test_observability_tracing` → T-003); the 7th, `tests/contract/search/test_search_contracts.py::test_nfr_001_performance_budgets`, is a **load-flaky timing budget**: PASSED in isolation both with this change (7.28 s) and at `122caba` (7.48 s) — not a T-005 regression |
| d | Ruff (changed paths) | `uv run ruff check src/backend/eventbus/eventbus.py tests/acceptance/logging_coverage/test_statements_via_feature.py` / `uv run ruff format <same>` | **All checks passed!** / **2 files left unchanged** |
| e | Types | `uv run mypy src/` | **Success: no issues found in 84 source files** |
| f | Dependency check (T-005 completion gate) | `uv run deptry .` | **Success! No dependency issues found** (90 files) — loguru still declared *and* still imported by settings/permissions, the interlock T-006 lifts |

T-005 completion gates from the DAG: (1) RED recorded ✓ (S4.1); (2) the eventbus-half AC-009 witness passes ✓; (3) no `loguru` import remains under `src/backend/eventbus/` ✓ (the witness's feature-wide clause is green — `__init__.py` and `feature_settings.py` never had one, so no export was added); (4) the event bus's whole test directory passes unchanged, 31 → 31 ✓; (5) deptry / ruff / mypy clean ✓.

Out of scope, untouched as required: `pyproject.toml` (loguru declaration → T-006), `src/backend/settings/` (→ T-004), `src/backend/permissions/service.py` (→ T-006), every other test file, `docs/tasks/` and `.github/task-runner/tasks.json` (T-005's `status` stays `PENDING` — setting it to `VERIFIED` is S4.4's job).

**Phase 4 (S4.2, T-005) gate: PASS — GREEN confirmed and recorded.** Next: S4.3 (T-005) — refactor, keep GREEN.

---

### S4.3 T-005 — refactor, keep GREEN (2026-10-06)

**Objective:** improve the structure of the T-005 diff (duplication, complexity, naming, feature boundaries) without changing observable behavior, keeping the task's targeted tests GREEN. Diff reviewed: `src/backend/eventbus/eventbus.py` and `tests/acceptance/logging_coverage/test_statements_via_feature.py` (T-005's two `allowed_files`).

#### Source: no structural changes needed (`src/backend/eventbus/eventbus.py` untouched)

The migration is already the minimal form, and the two remaining "smells" are forced by the task's own gates, not by the code:

1. **No logging helper for the four handler/event sites.** They repeat the shape *bind two locals → f-string event + the same values as keyword fields*. Folding that into a helper is forbidden by T-005's `design_constraints` ("The statement count stays 10", logging-coverage REQ-010 v2 restated): the AC-009 witness counts `<logger>.<level>(...)` call sites (`_statement_calls`) and asserts exactly 10, so a wrapper that emits on the callers' behalf would drop the count to 4 and fail the very test that gates this task. It would also move the record's callsite (`file`/`line` in the JSON sink, `_pipeline.py` `CallsiteParameterAdder`) off the emitting statement — an observable delta.
2. **The value appears twice (interpolated + as a field) by design.** Spec §9 row 2 requires "message + keyword fields, unchanged wording", and the chain has no `PositionalArgumentsFormatter`, so the positional form would silently drop the values (measured in S4.2, "Correction to note A"). The locals (`handler_name`, `event_name`) are already the cheapest way to avoid recomputing `_handler_name(handler)` / `__name__` twice per site; hoisting `event_name` out of the `_dispatch` loop instead would compute it eagerly for events with no matching handler — a worse trade, not an improvement.
3. **Naming and boundaries match the established T-001 pattern.** `_logger = get_logger("eventbus")` mirrors `src/backend/logging/feature_settings.py:22` (`_feature_logger = get_logger("logging")`): one module-level binding per module, feature-named, `@logged`/`@logged_class` untouched, import direction still `backend.eventbus → backend.logging` (spec §10 row 3). No new module, export, or abstraction was introduced, so `shared/` and the feature boundary are unchanged.

#### Test: one real deduplication (`tests/acceptance/logging_coverage/test_statements_via_feature.py`)

The per-feature half of the two per-feature witnesses — "scan the feature directory for a module that still imports a logging backend" — was copy-pasted verbatim in `test_ac_009_settings_statements_go_through_get_logger` and `test_ac_009_eventbus_statements_go_through_get_logger` (7 lines each, differing only in the directory and the message). Extracted once:

```python
def _dir_backend_imports(relative_dir: str) -> list[str]:
    """Every module under ``relative_dir`` (repo-relative) that imports a logging backend. ..."""
```

and both call sites became `if offenders := _dir_backend_imports("src/backend/settings"):` / `("src/backend/eventbus")`. Net diff **+15 / −14** (one helper, two call sites collapsed).

- **No test was weakened, deleted, renamed or converted**, and no assertion or violation-message wording changed — the helper returns exactly the list the inline scan built, and each witness still appends its own `f"a module under … imports a logging backend: {offenders}"`. Test function names are untouched, which matters because `scripts/check_traceability.py` fails on a matrix row citing a test function that no longer exists.
- **The other two AC-009 witnesses are unaffected**: re-run before and after, `test_ac_009_settings_statements_go_through_get_logger` (T-004) and `test_ac_009_statements_go_through_get_logger` (T-006) still fail with a **byte-identical** violation string (only the assertion's line number in the traceback moves). `2 failed, 1 passed` before and after.

#### Gate table (S4.3, T-005)

| # | Gate | Command (verbatim) | Result |
|---|---|---|---|
| a | **T-005 GREEN after the refactor** | `uv run pytest tests/acceptance/logging_coverage/test_statements_via_feature.py::test_ac_009_eventbus_statements_go_through_get_logger tests/acceptance/eventbus tests/unit/eventbus tests/contract/eventbus tests/property/eventbus tests/integration/eventbus -v` | **32 passed, 0 failed (4.21 s)** — identical to the S4.2 result (1 witness + the 31 eventbus tests), i.e. no behavior delta |
| b | Re-run after the formatter pass (the only reformatting the step caused) | same command | **32 passed (4.23 s → 4.21 s)** |
| c | Other AC-009 witnesses still RED, unchanged | `uv run pytest tests/acceptance/logging_coverage/test_statements_via_feature.py -q` | **2 failed, 1 passed (0.32 s)** — same two failures, same wording as before the refactor |
| d | Ruff (changed paths) | `uv run ruff check tests/acceptance/logging_coverage/test_statements_via_feature.py src/backend/eventbus/eventbus.py` / `uv run ruff format <same>` then `--check` | **All checks passed!** / 1 file reformatted (the helper's generator fits on one line at 120 cols) → **2 files already formatted** |
| e | Types | n/a — no `src/` file was changed in this step (`uv run mypy src/` covers `src/` only and its S4.2 result stands: *Success: no issues found in 84 source files*) | n/a |

Out of scope, untouched: `pyproject.toml`, `src/backend/settings/`, `src/backend/permissions/`, every other test file, the spec, and `.github/task-runner/tasks.json` / `docs/tasks/` (T-005's `status` stays `PENDING` — setting it to `VERIFIED` is S4.4's job).

**Phase 4 (S4.3, T-005) gate: PASS — source needs no structural change (reasons above), the test-side duplication removed once, GREEN maintained (32 passed), ruff clean.** Next: S4.4 (T-005) — commit + set status `VERIFIED`.

### S4.1 (T-007) — pick task + confirm RED (2026-10-06)

#### Picked task

**T-007** — *"rewrite the agent-facing logging guidance to the new surface: AGENTS.md 'Using the Logging Feature' (backend named, removed @logged parameters, setup_logger(Settings(...)) shape) and the python-best-practices skill's direct backend entry point"* — `REQ-014` / `AC-019`, feature group `guidance (AGENTS.md + .agents/skills/python-best-practices/)`.

**Ready set at pick time** (`.github/task-runner/tasks.json`, HEAD `4f66028`): T-001/T-002/T-005 `VERIFIED`; **ready** (all `dependencies` VERIFIED) = **T-003** (`deps T-001, T-002`), **T-004** (`deps T-001`), **T-007** (`deps T-001, T-002`); **not ready** = T-006 (`deps T-003, T-004` still `PENDING`).

**Why T-007 (easiest-first among the three ready tasks):**

| Task | Scope | Why it is (not) the easiest ready task |
|---|---|---|
| **T-007** | Guidance text only — 4 markdown files, **no Python source**, one contract witness | **Picked.** Zero `src/` change, zero mypy surface, one test to flip, and the API it documents is already final (T-001 `setup_logger(*, renderer: str \| None = None)` at `src/backend/logging/_pipeline.py:240`, T-002 decorators — both `VERIFIED`), so the target of the rewrite cannot move under the step. |
| T-004 | 28 direct backend statements in `src/backend/settings/registry.py` (17) + `repository.py` (11) | Bigger mechanical diff, touches two live service modules (mypy + settings-suite regression surface). |
| T-003 | Live reconfiguration mutating the managed handlers in `src/backend/logging/_setup.py` | Deepest of the three: 5 implementation steps, timing/rotation semantics, and the settings-coverage suites (`test_setup_logger.py`, `unit/`, `property/`, `contract/`) may need re-derivation. |

T-007's `dependencies` (`T-001`, `T-002`) are both `VERIFIED`, so nothing blocks it; the DAG gives it no ordering against T-003/T-004, so the ease ordering applies.

#### Task-definition constraints that bind S4.2

Quoted from `.github/task-runner/tasks.json` → `T-007`:

- **`allowed_files.source_files`** — `AGENTS.md` (the *"Using the Logging Feature"* section and the tooling line that names loguru), `.agents/skills/python-best-practices/SKILL.md`, `.agents/skills/python-best-practices/references/errors-and-resources.md`, `.agents/skills/python-best-practices/references/modern-python.md`. **`allowed_files.test_files`** — `tests/contract/logging/test_dependency_contract.py` only. *"Implementation MUST only touch `allowed_files.source_files`"* (implement skill, Rules).
- **`implementation_scope`** — *"Guidance text only - no Python source, no test assertion weakened. The AC-019 contract test is the only code this task adds."* (the test already exists from S3.1, so S4.2 adds no code at all).
- **`design_constraints`** — *"REQ-014: agent-facing guidance must describe the new surface; guidance must not name a removed backend or a removed parameter."* · *"REQ-005 applies to guidance too: an example must show the feature's exported entry points, never a backend import."* · *"Keep the ADR-060 tracing-policy wording (which classes are traced, include_args=False for secrets) - only the backend and the removed parameters change."* · *"No userdocs/ change: mkdocs.yml sets docs_dir: userdocs and userdocs/ … contains no loguru or setup_logger reference, so the published site is unaffected."* · *"No other guidance file changes (README.md, userdocs/, .agents/skills/{specify,test,implement,verify,review,decompose,git}/ are out of scope for this change)."*
- **`implementation_steps`** (4) — rewrite the AGENTS.md *"Using the Logging Feature"* section (drop the loguru backend sentence, drop `context_getter`/`depth` from the `@logged` parameter list, replace the `setup_logger(Settings(...))` example with `setup_logger()` / `setup_logger(renderer=...)`, `get_logger()`, `@logged`, `@logged_class`); rewrite the python-best-practices skill's logging guidance at `SKILL.md:16`, `references/errors-and-resources.md:19` and `:45`, `references/modern-python.md:85` to the feature's own entry points *"because REQ-005 forbids a direct backend import even in guidance"*; keep the ADR-060 tracing-policy wording; no `userdocs/` change.
- **`completion_gates`** — RED observed + recorded (this section) · *"AC-019 passes: AGENTS.md and the python-best-practices skill name the feature's entry points and no removed backend or parameter"* · `uv run --group docs mkdocs build --strict` succeeds (published-site regression guard only) · `uv run python scripts/check_traceability.py` passes (the AC-019 row cites the new contract test — already added in S3.1) · `uv run ruff check tests/contract/logging/test_dependency_contract.py` clean.

#### RED gate — verbatim `red_command`

```text
uv run pytest tests/contract/logging/test_dependency_contract.py::test_ac_019_guidance_names_feature_entry_points -v
```

``text
collecting ... collected 1 item
tests/contract/logging/test_dependency_contract.py::test_ac_019_guidance_names_feature_entry_points FAILED [100%]
============================== 1 failed in 0.31s ==============================
```

**RED is a behavior failure, not a collection/import error**: the test is collected and executed, and fails on its own assertion (`tests/contract/logging/test_dependency_contract.py:202: AssertionError`) —

```python
assert not violations, "AC-019 / REQ-014: " + "; ".join(violations)
```

with **24 violations** listed in the assertion message (AGENTS.md 9, `SKILL.md` 4, `modern-python.md` 4, `errors-and-resources.md` 8). The witness (`_guidance_violations`, `tests/contract/logging/test_dependency_contract.py:171`) checks five clauses over the four files in `_GUIDANCE_FILES` (`:106`):

1. no `\bloguru\b` (case-insensitive, `_REMOVED_BACKEND_WORD`, `:114`);
2. no `\bcontext_getter\b` / `\bdepth\b` (`_REMOVED_PARAMETERS`, `:117`);
3. each file names **all four** feature entry points `setup_logger`, `logged`, `logged_class`, `get_logger` (`_FEATURE_ENTRY_POINTS`, `:120`);
4. no backend entry point — `import|from structlog|loguru`, or `structlog|loguru . get_logger|getLogger|logger` (`_BACKEND_ENTRY_POINT`, `:125`; naming structlog as a *library* is allowed);
5. every `setup_logger(` call shown must be accepted by the amended signature — no argument, or the single keyword-only `renderer` (`_amended_signature_accepts`, `:163`, against `setup_logger(*, renderer: str | None = None)`).

Failure output (verbatim, one line per violation group):

```text
E   AssertionError: AC-019 / REQ-014: AGENTS.md:769 names the removed backend 'loguru';
E   AGENTS.md:769 names the removed backend 'loguru'; AGENTS.md:771 names the removed backend
E   'loguru'; AGENTS.md:767 names the removed parameter 'context_getter'; AGENTS.md:767 names the
E   removed parameter 'depth'; AGENTS.md does not name the feature entry point 'get_logger';
E   AGENTS.md:765 shows setup_logger(settings), a call the amended signature rejects;
E   AGENTS.md:771 shows setup_logger(Settings(...)), a call the amended signature rejects;
E   AGENTS.md:776 shows setup_logger(Settings(log_level="INFO")), a call the amended signature
E   rejects; .agents/skills/python-best-practices/SKILL.md does not name the feature entry point
E   'setup_logger'; … 'logged'; … 'logged_class'; … 'get_logger';
E   .agents/skills/python-best-practices/references/modern-python.md does not name the feature
E   entry point 'setup_logger'; … 'logged'; … 'logged_class'; … 'get_logger';
E   .agents/skills/python-best-practices/references/errors-and-resources.md does not name the
E   feature entry point 'setup_logger'; … 'logged'; … 'logged_class';
E   .agents/skills/python-best-practices/references/errors-and-resources.md:17 shows the backend
E   entry point 'import structlog'; …:19 shows the backend entry point 'structlog.get_logger';
E   …:43 shows the backend entry point 'import structlog'; …:45 shows the backend entry point
E   'structlog.get_logger'
```

#### Exact guidance locations that must change (grep evidence, HEAD `4f66028`)

| File:line | Current text (the string the witness rejects) | Clause |
|---|---|---|
| `AGENTS.md:765` | "Call `setup_logger(settings)` exactly once in the application entrypoint" — the rejected `Settings`-passing call shape | 5 |
| `AGENTS.md:766` | "**Configure with `Settings`.** Build a `Settings` instance (or use `get_settings()`) to set `log_level`, `log_file`, …" — not itself a violation, but it is the sentence that makes the `setup_logger(settings)` shape coherent and must be rewritten to the settings-registry/live-reconfiguration surface (T-003) | — |
| `AGENTS.md:767` | "…with parameters: `level`, `slow_threshold_ms`, `slow_threshold_setting`, `include_args`, **`context_getter`**, **`depth`**" | 2 |
| `AGENTS.md:769` | "The feature configures **loguru**'s sinks, so feature code may also use **loguru**'s `logger` directly" (2 occurrences) | 1 |
| `AGENTS.md:770` | "`diagnose=False` is enforced … `from backend.logging import logged, logged_class, setup_logger, Settings, get_settings`" — the import list names three of the four entry points, **not `get_logger`** | 3 |
| `AGENTS.md:771` | "Direct **loguru** (`logger.info(...)`) is reserved for one-off statements … `setup_logger(Settings(...))` MUST be called exactly once" | 1 + 5 |
| `AGENTS.md:774` | `from backend.logging import Settings, logged, setup_logger` — example import, missing `get_logger` | 3 |
| `AGENTS.md:776` | `setup_logger(Settings(log_level="INFO"))` — rejected call shape | 5 |
| `.agents/skills/python-best-practices/SKILL.md:16` | "Use the project logger (structlog) instead of `print`." — names none of the four entry points | 3 |
| `.agents/skills/python-best-practices/references/errors-and-resources.md:17` | `import structlog` | 4 |
| `.agents/skills/python-best-practices/references/errors-and-resources.md:19` | `log = structlog.get_logger()` | 4 |
| `.agents/skills/python-best-practices/references/errors-and-resources.md:43` | `import structlog` (the `timer()` example) | 4 |
| `.agents/skills/python-best-practices/references/errors-and-resources.md:45` | `log = structlog.get_logger()` | 4 |
| `.agents/skills/python-best-practices/references/modern-python.md:85` | "Logging: structlog events, not f-string messages and not `print`." — names none of the four entry points | 3 |

Notes for S4.2:

- `AGENTS.md` already satisfies clause 3 for `setup_logger` / `logged` / `logged_class` (line 770) — only **`get_logger`** is missing there, so the AGENTS.md fix is clauses 1, 2, 3 (one name) and 5.
- The three skill files each need **all four** entry-point names present (clause 3) *and* the two `structlog` call sites replaced (clause 4) — `errors-and-resources.md` is the only skill file with a backend import.
- `AGENTS.md` names `loguru` **only** at 769 and 771 (`grep -ni loguru AGENTS.md`): the "Tooling & Execution Environment" section has no loguru line, so the `allowed_files` parenthetical *"the tooling line that names loguru"* is already satisfied — nothing to change there.
- The public surface the guidance must name is final (`src/backend/logging/__init__.py:__all__`): `setup_logger`, `get_logger`, `logged`, `logged_class`, `Settings`, `get_settings`, `register_settings`.

#### Gate table (S4.1, T-007)

| # | Gate | Command (verbatim) | Result |
|---|---|---|---|
| a | Task is ready in the DAG | `python -c "…print(task_id, status, dependencies)…"` on `.github/task-runner/tasks.json` | T-007 `PENDING`, `dependencies` `T-001` + `T-002` both `VERIFIED` → **ready** |
| b | **RED observed** | `uv run pytest tests/contract/logging/test_dependency_contract.py::test_ac_019_guidance_names_feature_entry_points -v` | **1 failed in 0.31 s** — assertion failure at `test_dependency_contract.py:202`, **24 violations**, collected and executed (not a collection/import error) |
| c | No file changed by this step | `git status --short` | clean before the step; only `docs/verification/structlog-logging.md` modified by this evidence commit |
| d | Ruff | n/a — this step writes no tests or implementation code (guidance files untouched, `red_command` only) | n/a |
| e | Full suite | not run (Phase 5 gate; per-task targeted runs only) | n/a |

Out of scope, untouched: `AGENTS.md`, the three `.agents/skills/python-best-practices/` files, `tests/contract/logging/test_dependency_contract.py`, `pyproject.toml`, `src/`, the spec, and `.github/task-runner/tasks.json` / `docs/tasks/` (T-007's `status` stays `PENDING` — setting it to `VERIFIED` is S4.4's job).

**Phase 4 (S4.1, T-007) gate: PASS — a ready task is picked (easiest of T-003/T-004/T-007) and RED is observed on its `red_command` (1 failed, 24 AC-019 violations).** Next: S4.2 (T-007) — rewrite the four guidance files to the new surface, confirm GREEN on the same command.


### S4.2 T-007 — implement + confirm GREEN (2026-10-06)

**Objective:** rewrite the four agent-facing guidance files to the implemented logging surface so the AC-019 witness passes. Guidance text only — no `src/`, no test change, no dependency change (`implementation_scope` in `.github/task-runner/tasks.json` → T-007).

#### What changed, per file

| File | Change (the defect class it clears) |
|---|---|
| `AGENTS.md` — "Using the Logging Feature" (9 lines rewritten, 1 bullet added, 18 ±) | **Setup bullet**: `setup_logger(settings)` → `setup_logger()`, and the idempotence wording now states what is actually idempotent (two managed sinks; a later call reconfigures them) instead of "later calls are no-ops" (clauses 1/5). **New bullet**: the `renderer` keyword — `setup_logger(renderer="json")` / `setup_logger(renderer="text")` / default `None` = text console + JSON file, `ValueError` before anything is installed (matches `_validate_renderer`, `src/backend/logging/_pipeline.py:209`, and `RENDERERS = ("text", "json")`, `:45`). **Settings bullet**: "Build a `Settings` instance" → the live settings-registry surface (`register_settings(registry)` + the five `logging.*` keys, fallback to the `Settings` default, `get_settings()`), which is how `setup_logger` actually reads its values (`_settings_from_registry`, `_settings.py:26`). **`@logged` bullet**: parameter list is now exactly `level`, `slow_threshold_ms`, `slow_threshold_setting`, `include_args` — `context_getter` and `depth` deleted (clause 2, matches `_decorator.logged`, `:189`). **New "One-off statements" bullet** replaces the removed loguru sentence: `get_logger()` / `get_logger("eventbus")` + keyword fields, usable before setup (clause 1 + clause 3's missing `get_logger`; matches `get_logger`, `_pipeline.py:178` and the T-005 call pattern `src/backend/eventbus/eventbus.py:27`). **Conventions bullet**: the loguru-only `diagnose=False` wording replaced by the specified invariant ("records never contain local variable values; pass what should be recorded as keyword fields" — INV-002), the public-import list extended with `get_logger` / `register_settings`, and the private-module list corrected to the modules that exist (`_pipeline` / `_decorator` / `_renderers` / `_settings` — `_setup.py` no longer exists), plus the REQ-005 rule that feature code never imports or calls a backend directly. **Tracing-policy bullet**: "Direct loguru (`logger.info(...)`)" → "`get_logger()`"; the closing sentence's `setup_logger(Settings(...))` → `setup_logger()` (clauses 1 + 5). ADR-060's tracing-policy content (which classes are traced, `include_args=False` for secrets, semantic levels) is unchanged, per `design_constraints`. **Example block**: `from backend.logging import get_logger, logged, setup_logger` + `setup_logger()` + `log = get_logger("myfeature")` (clause 5's rejected `setup_logger(Settings(log_level="INFO"))` is gone). |
| `.agents/skills/python-best-practices/SKILL.md:16` | "Use the project logger (structlog) instead of `print`." → the feature's own entry points: `setup_logger()` once at startup, `get_logger()` for one-off statements, `@logged` / `@logged_class` to trace calls, never a backend import. Clears clause 3 (all four names were missing). |
| `.agents/skills/python-best-practices/references/modern-python.md:85` | "Logging: structlog events, …" → the shared feature's entry points with keyword fields, still "not f-string messages and not `print`". Clears clause 3. |
| `.agents/skills/python-best-practices/references/errors-and-resources.md:17,19,43,45` | Both examples now import the feature (`from backend.logging import get_logger` → `log = get_logger()`) instead of `import structlog` / `structlog.get_logger()` — clears clause 4 (4 violations). The "Rules" bullet names `setup_logger()` and `@logged` / `@logged_class` and states that a traced function's exception is already recorded; a closing line notes `@logged(slow_threshold_ms=...)` already measures a call's elapsed time, so a hand-written timer is for blocks — clears clause 3. |

**No-op recorded:** `allowed_files` names "the tooling line [in AGENTS.md] that names loguru". There is no such line — `grep -ni loguru AGENTS.md` matched only lines 769 and 771 (both inside "Using the Logging Feature", both removed by this step), and the "Tooling & Execution Environment" section names no logging backend. Nothing to change there (confirmed again after the edit: `grep -ni "loguru|structlog|depth|context_getter" AGENTS.md` → no match).

#### GREEN gate — verbatim `green_command`

```text
uv run pytest tests/contract/logging/test_dependency_contract.py::test_ac_019_guidance_names_feature_entry_points -v
```

```text
collecting ... collected 1 item
tests/contract/logging/test_dependency_contract.py::test_ac_019_guidance_names_feature_entry_points PASSED [100%]
============================== 1 passed in 0.21s ==============================
```

**AC-019 violation count: 24 → 0.** Re-measured with the witness's own scanner (not only the pass/fail line), so the count is evidence and not an inference:

```text
uv run python -c "…m._guidance_violations(rel, text) for rel in m._GUIDANCE_FILES…"  →  violations after: 0
```

All five clauses are satisfied by real content, not by inserted magic strings: every entry-point name appears in a sentence that describes what that entry point does, the two backend call sites are replaced by the feature's own import, and the three rejected `setup_logger(...)` call shapes in `AGENTS.md` are replaced by calls the amended signature (`setup_logger(*, renderer: str | None = None)`, `_pipeline.py:240`) accepts. The witness test was not touched (`git status` shows only the four guidance files + this record).

#### Gate table (S4.2, T-007)

| # | Gate | Command (verbatim) | Result |
|---|---|---|---|
| a | **GREEN observed** | `uv run pytest tests/contract/logging/test_dependency_contract.py::test_ac_019_guidance_names_feature_entry_points -v` | **1 passed in 0.21 s** (was 1 failed, 24 violations) |
| b | AC-019 clause count | the witness's `_guidance_violations` over the four files | **0 violations** (before: AGENTS.md 9, `SKILL.md` 4, `modern-python.md` 4, `errors-and-resources.md` 7) |
| c | **Ruff (changed paths)** | `uv run ruff check AGENTS.md .agents/skills/python-best-practices/SKILL.md .agents/skills/python-best-practices/references/modern-python.md .agents/skills/python-best-practices/references/errors-and-resources.md` | **All checks passed!** (exit 0) — `warning: No Python files found under the given path(s)`: every changed path is Markdown, so ruff has nothing to check and `ruff format` does not apply |
| d | Published site unaffected | `uv run --group docs mkdocs build --strict` | succeeds (2.92 s, exit 0) — `docs_dir: userdocs`, so neither `AGENTS.md` nor `.agents/skills/` is in the site; the gate confirms no regression, per `design_constraints` |
| e | Scope | `git status --short` | exactly the four `allowed_files.source_files` + `docs/verification/structlog-logging.md`; `src/`, `tests/`, `pyproject.toml`, specs, `docs/todo/`, `docs/questions/`, `docs/verification/traceability.md`, `.github/task-runner/tasks.json` untouched (T-007 stays `PENDING` — S4.4's job) |
| f | Full suite | not run (Phase 5 gate; per-task targeted run only) | n/a |

**Phase 4 (S4.2, T-007) gate: PASS — GREEN confirmed (AC-019 witness passes, 24 → 0 violations) and recorded; ruff clean on the changed paths (Markdown-only, nothing to check).** Next: S4.3 (T-007) — refactor (keep GREEN; the no-op fast-path is expected, there is no code in this task's diff), then S4.4 commit + set T-007 `VERIFIED`.


### S4.3 T-007 — refactor, keep GREEN (2026-10-06)

**Objective:** review the T-007 diff (commit `9071346`) for text-quality/structure problems only — duplicated guidance, wording that contradicts the implemented API, stale references, broken markdown/links — and fix them without changing what the guidance mandates. Guidance text only; no `src/`, no tests, no specs.

#### Review findings (four guidance files, checked against `src/backend/logging/`)

| # | Finding | Verdict | Action |
|---|---|---|---|
| 1 | `AGENTS.md:770` — "It is usable before setup — the record still reaches standard error" contradicts the implemented behaviour. Before `setup_logger()` the pipeline logger has no handler, so the record propagates to the root logger and only stdlib `lastResort` (level `WARNING`) writes it: an `info` record is dropped. Measured: `uv run python -c "from backend.logging import get_logger; get_logger('probe').info(...); get_logger('probe').warning(...)"` → only the `warning` record on stderr. `EDGE-006` and its test (`tests/unit/logging/test_pipeline_edges.py:157`) use `.warning(...)` for exactly this reason. | **Defect** — guidance not true of the code it publishes (the spec's stated goal) | Reworded to what the pipeline actually does: no exception, the record bypasses the managed sinks, only WARNING-and-above reaches standard error via the last-resort handler, and setup still comes first (the setup mandate is unchanged) |
| 2 | `AGENTS.md:772` — the tracing-policy bullet re-states the setup mandate verbatim ("`setup_logger()` MUST be called exactly once in the application entrypoint, before any feature code runs"), already stated by the bullet that owns it (`:765`, "Set it up once at startup") and again as a precondition in `:771`. Three copies of one MUST. | **Duplication** | Deleted the third copy from the tracing-policy bullet. The mandate is preserved verbatim in `:765` and its precondition in `:771`; nothing the guidance mandates changed |
| 3 | Entry-point list repeated in all four guidance files (`AGENTS.md`, `SKILL.md:16`, `modern-python.md:85`, `errors-and-resources.md:30`) | **Not a defect — kept.** AC-019 clause 3 requires **each** of the four files to name all four entry points (`_FEATURE_ENTRY_POINTS` in `tests/contract/logging/test_dependency_contract.py:122`), and `SKILL.md:26` tells the reader to open only one reference file per task, so each reference must be self-contained. Deduplicating would break the witness and the skill | none |
| 4 | Stale references: `grep -ci "loguru|context_getter|\bdepth\b|diagnose|structlog"` over the four files | **Clean** — 0 matches in every file; no `setup_logger(Settings(...))` shape survives anywhere in `AGENTS.md` (`grep -n "setup_logger\|get_settings()\|Settings("` → only the corrected lines 765–777) | none |
| 5 | Markdown/links: the `SKILL.md` reference table's seven `references/*.md` links all resolve (`ls .agents/skills/python-best-practices/references/`); code fences balanced; the two files the diff touched at EOF keep the skill files' existing convention (CRLF throughout, no final newline — `SKILL.md` is untouched and also has none), so no mixed line endings were introduced | **Clean** | none |
| 6 | API agreement of the rest of the rewritten text: `@logged` parameters (`level`, `slow_threshold_ms`, `slow_threshold_setting`, `include_args`) match `_decorator.logged:189`; `@logged_class` parameters match `_decorator.logged_class:220`; `renderer` values and the `ValueError`-before-install wording match `_validate_renderer` / `RENDERERS` in `_pipeline.py`; the five `logging.*` keys match `feature_settings.register_settings`; the private-module list (`_pipeline` / `_decorator` / `_renderers` / `_settings`) matches the files that exist | **Clean** | none |

#### Changes made

One file, two lines (`git diff --stat` → `AGENTS.md | 4 ++--`): the "One-off statements" bullet reworded (finding 1) and the duplicated setup mandate deleted from the "Tracing policy" bullet (finding 2). No mandate added, weakened or removed; no other guidance file needed a change.

#### Gate table (S4.3, T-007)

| # | Gate | Command (verbatim) | Result |
|---|---|---|---|
| a | **GREEN re-confirmed after the refactor** | `uv run pytest tests/contract/logging/test_dependency_contract.py::test_ac_019_guidance_names_feature_entry_points -v` | **1 passed in 0.20 s** |
| b | AC-019 clause count still 0 | the witness's own `_guidance_violations` over the four files | **0 violations** (AGENTS.md 0, SKILL.md 0, modern-python.md 0, errors-and-resources.md 0) |
| c | Published site unaffected | `uv run --group docs mkdocs build --strict` | exit **0** (1.57 s) — re-run because `AGENTS.md` text moved |
| d | **Ruff** | `uv run ruff check AGENTS.md` | n/a — every changed path is Markdown (`warning: No Python files found under the given path(s)`, `All checks passed!`); `ruff format` does not apply |
| e | Scope | `git status --short` | only `AGENTS.md` + this record; `src/`, `tests/`, specs, `docs/todo/`, `docs/questions/`, `.github/task-runner/tasks.json` (T-007 stays `PENDING` — S4.4's job) untouched |
| f | Full suite | not run (Phase 5 gate; per-task targeted run only, per the skill's S4.4 no-op/re-run rule) | n/a |

**Phase 4 (S4.3, T-007) gate: PASS — two text defects fixed (one contradiction with the implemented pipeline, one duplicated mandate), GREEN maintained, ruff n/a (markdown).** Next: S4.4 (T-007) — commit + set T-007 `VERIFIED`.


---

### S4.1 (T-004) — pick task + confirm RED (2026-10-07)

**Task picked: T-004** — *"migrate the 28 direct backend statements in `src/backend/settings/registry.py` (17) and `src/backend/settings/repository.py` (11) to `get_logger()`"* — `REQ-005` / `AC-009` (amended `logging-coverage.md` v2 `REQ-010` / `AC-010`), feature group `backend.settings`, Impact Analysis row 2.

#### Ready set at pick time (`.github/task-runner/tasks.json`, HEAD `86b9274`)

`T-001` `T-002` `T-005` `T-007` `VERIFIED`; **ready** (every `dependency` `VERIFIED`) = **T-003** (`deps T-001, T-002`) and **T-004** (`deps T-001`); **not ready** = **T-006** (`deps T-003, T-004` still `PENDING`).

**Why T-004 (easiest-first among the two ready tasks):**

| Task | Scope | Why it is (not) the easiest ready task |
|---|---|---|
| **T-004** | 28 statement call sites in 2 modules: swap one import per module, re-express each call in keyword-field form. No new API, no new pattern — the exact shape **T-005 just proved and verified** on the event bus (`src/backend/eventbus/eventbus.py:27` + its 10 sites, `VERIFIED` at `e595e04`) | **Picked.** Purely mechanical, the target surface is frozen (T-001 `get_logger`, T-002 decorators/capture both `VERIFIED`), and the witness's own helper (`_dir_backend_imports`) is already shared, so nothing has to be designed here. |
| T-003 | Live reconfiguration: mutate the managed handlers in place, `setup_logger()` with no arguments, **settings-coverage tests re-derived** (amended REQ-014/015/016, AC-019/020/021, EDGE-008) | Heavier: it changes behavior (not a statement swap), it re-derives tests from four amended IDs, and it owns the rotation/level semantics the settings suites assert. |
| T-006 | last statement + remove loguru from the dependency set + delete the retired-policy test + traceability row | **Stays last by construction** — its `dependencies` are `T-003, T-004` (and it is the only task allowed to drop `loguru` from `pyproject.toml`, which needs every importer gone). |

#### The task entry, verbatim from `.github/task-runner/tasks.json`

```json
{
  "task_id": "T-004",
  "feature_group": "backend.settings",
  "title": "migrate the 28 direct backend statements in src/backend/settings/registry.py (17) and src/backend/settings/repository.py (11) to get_logger()",
  "requirements": ["REQ-005"],
  "acceptance_criteria": ["AC-009"],
  "invariants": [],
  "edge_cases": [],
  "non_functional": [],
  "amended_ids": [
    "logging-coverage.md REQ-010 (restated: statements stay statements, written through the feature's exported logger)",
    "logging-coverage.md AC-010 (restated)"
  ],
  "tests_to_create": [
    "tests/acceptance/logging_coverage/test_statements_via_feature.py::test_ac_009_settings_statements_go_through_get_logger (per-file AC-009 witness: the two settings files import no backend and every one-off statement is written through get_logger())"
  ],
  "red_command": "uv run pytest tests/acceptance/logging_coverage/test_statements_via_feature.py::test_ac_009_settings_statements_go_through_get_logger -v",
  "implementation_steps": [
    "Replace `from loguru import logger` in src/backend/settings/registry.py and src/backend/settings/repository.py with the logging feature's exported get_logger(); keep the same message wording and level (spec section 9: the observability policy does not change).",
    "Convert the 28 call sites to the feature logger's keyword-field form (message + fields) instead of the backend's brace-formatting form; no statement added, none removed, no level change.",
    "Leave the settings feature's tracing decorators untouched (ADR-060).",
    "Leave the loguru declaration in pyproject.toml in place (eventbus and permissions still import it - deptry interlock, T-006)."
  ],
  "green_command": "uv run pytest tests/acceptance/logging_coverage/test_statements_via_feature.py::test_ac_009_settings_statements_go_through_get_logger tests/acceptance/settings tests/unit/settings tests/contract/settings tests/property/settings tests/integration/settings -v",
  "inputs": [
    "docs/specs/structlog-logging.md section 4 (REQ-005), section 5 (AC-009), section 9, section 10 row 2",
    "docs/specs/logging-coverage.md v2 (REQ-010 / AC-010 restated)",
    "T-001 handoff (get_logger is exported)"
  ],
  "allowed_files": {
    "source_files": ["src/backend/settings/registry.py", "src/backend/settings/repository.py"],
    "test_files": ["tests/acceptance/logging_coverage/test_statements_via_feature.py"]
  },
  "implementation_scope": "Statement migration only, in the two settings files. No behavior, level or message-semantics change.",
  "design_constraints": [
    "REQ-005: get_logger() is the only supported entry point for one-off statements; a feature must not import a logging backend.",
    "The statement count stays 17 + 11 (logging-coverage REQ-010 restated: statements stay statements).",
    "Import direction unchanged: backend.settings -> backend.logging is the allowed direction (spec section 10 row 2).",
    "deptry interlock: loguru stays declared here - src/backend/eventbus and src/backend/permissions still import it.",
    "Gate scoping (Phase 3 derives every task's tests before Phase 4 starts): green_command lists this task's own tests plus the pre-existing tests this task must fix, and deliberately EXCLUDES test files owned by a later DAG task, so this task's GREEN gate is honest and satisfiable with only this task and its declared dependencies. The full suite is the Phase 5 gate."
  ],
  "completion_gates": [
    "RED observed on the red_command set; recorded in docs/verification/structlog-logging.md.",
    "The settings-half AC-009 witness passes.",
    "No `loguru` import remains anywhere under src/backend/settings/.",
    "The settings feature's whole test directory passes unchanged (no behavior delta).",
    "uv run deptry . clean; uv run ruff check <changed paths> clean; uv run mypy src/ clean."
  ],
  "dependencies": ["T-001"],
  "status": "PENDING"
}
```

**What constrains S4.2** (read off the entry, no interpretation added):

1. **Only two files may change** — `allowed_files.source_files` = `src/backend/settings/registry.py`, `src/backend/settings/repository.py`. `pyproject.toml` is **not** in the set (the loguru declaration stays; removing it is T-006). The one test file in `allowed_files.test_files` needs **no** change (see "the witness helper is already shared" below).
2. **The count is a gate, not a style preference** — 17 + 11 statement call sites must still be there after the migration; folding sites into a helper or dropping one fails the witness's count clause and logging-coverage REQ-010 v2.
3. **Wording and level are frozen** — spec §9 row 2: "DEBUG/INFO/WARNING as today … through `get_logger()`, message + keyword fields, **unchanged wording**". So the migration may change *how* the values travel (keyword fields), never *what* the record says.
4. **Decorators untouched** (ADR-060) — `@logged_class(slow_threshold_ms=250)` on `SettingsRegistry` (`registry.py:48`), `@logged(slow_threshold_ms=5)` at `registry.py:360, 377`, and the five `@logged_class(slow_threshold_ms=100)` classes in `repository.py` (`:99, 116, 165, 190, 218`) stay exactly as they are; the `logged` / `logged_class` imports must stay.
5. **No new import direction** — `backend.settings → backend.logging` already exists in both files (`registry.py:12`, `repository.py:28`), so `get_logger` joins an existing edge (spec §10 row 2).

#### Readiness check

| Check | Evidence | Result |
|---|---|---|
| Dependency satisfied | T-004 `"dependencies": ["T-001"]`; T-001 `"status": "VERIFIED"` | satisfied |
| Status still `PENDING` | `.github/task-runner/tasks.json` and `docs/tasks/structlog-logging.tasks.json` agree: T-001/T-002/T-005/T-007 `VERIFIED`, T-003/T-004/T-006 `PENDING` | confirmed |
| Its test exists | `tests/acceptance/logging_coverage/test_statements_via_feature.py::test_ac_009_settings_statements_go_through_get_logger` (derived at S3.1 T-004, commit `28d3d40`) — collected and run below | confirmed |
| The pipeline it migrates to exists | `get_logger(name=None) -> BoundLogger` at `src/backend/logging/_pipeline.py:178`, exported from `backend.logging`; already used by T-005 (`src/backend/eventbus/eventbus.py:27`) and T-001 (`feature_settings.py`) | confirmed |
| Working tree | `git status --short` clean at HEAD `86b9274` | confirmed |

#### RED re-confirmed (the DAG's own `red_command`, verbatim)

```text
uv run pytest tests/acceptance/logging_coverage/test_statements_via_feature.py::test_ac_009_settings_statements_go_through_get_logger -v
```

→ **1 failed, 0 passed (0.32 s)** at HEAD `86b9274` — **identical to the S3.2 gate (1 failed / 0 passed)**; no drift between Phase 3 and Phase 4 entry. One `AssertionError` naming the offending imports and statements — **not** a collection, import, fixture or test-data error:

```text
AssertionError: AC-009 / REQ-005 (logging-coverage REQ-010 v2): src/backend/settings/registry.py imports a logging backend: ['loguru.logger']; src/backend/settings/registry.py statements not written through get_logger(): line(s) [89, 94, 113, 142, 146, 160, 173, 244, 248, 255, 259, 264, 283, 295, 299, 308, 317]; src/backend/settings/repository.py imports a logging backend: ['loguru.logger']; src/backend/settings/repository.py statements not written through get_logger(): line(s) [140, 151, 154, 156, 248, 259, 262, 264, 281, 284, 286]; a module under src/backend/settings/ imports a logging backend: ['src/backend/settings/registry.py', 'src/backend/settings/repository.py']
```

The **count clause contributes no violation** — both files already hold exactly REQ-005's 17 and 11 statement call sites — so the witness is red exactly on the three clauses T-004 fixes: the two backend imports, the 28 unmigrated receivers, and the feature-wide "no module under `src/backend/settings/` imports a backend" clause (which the same two files satisfy once migrated).

#### The witness helper is already shared — no test change needed in T-004

The feature-wide clause is produced by `_dir_backend_imports` (`test_statements_via_feature.py:50`), the helper extracted **once** in **T-005's S4.3** (commit `e595e04`, recorded under "S4.3 T-005 — refactor, keep GREEN") out of the copy-pasted inline scan that both per-feature witnesses carried. The settings witness already calls it (`:137`), and T-005's S4.3 re-measured that the settings witness still failed with a **byte-identical** violation string after the extraction. Consequence for S4.2: `allowed_files.test_files` is listed but **must not need editing** — the witness is final, and any change to it would be a test weakening under the Phase 6 review check.

#### Pre-implementation baselines for this task's gates (all measured at `86b9274`)

| Baseline | Command | Result |
|---|---|---|
| `green_command` set as a whole | the verbatim `green_command` | **1 failed, 87 passed (40.26 s)** — the 1 failure is the witness; after T-004 the set must be **88 passed** |
| The settings feature's five test directories (gate 4, "passes unchanged") | `uv run pytest tests/acceptance/settings tests/unit/settings tests/contract/settings tests/property/settings tests/integration/settings -q` | **87 passed (40.19 s)** |
| The retired-policy test that asserts two settings wordings | `uv run pytest tests/acceptance/logging_coverage/test_direct_loguru_kept.py -q` | **1 passed** — it asserts `"setting registered: key="` and `"value set: key="` (`:51-54`) and must stay green (T-006 deletes the file, not T-004) |
| The level witness (asserts a settings WARNING) | `uv run pytest tests/acceptance/logging_coverage/test_levels.py -q` | **1 passed** — `:66` asserts `WARNING` + `"duplicate registration"`; its eventbus ERROR assertion is already satisfied by a **migrated** statement, which is the proof that the dual capture carries pipeline statements at their level and wording |
| The three AC-009 witnesses together | `uv run pytest tests/acceptance/logging_coverage/test_statements_via_feature.py -q` | **2 failed, 1 passed** — settings half (T-004) and all-four half (T-006) red, eventbus half (T-005) green |
| Dependency gate (gate 5) | `uv run deptry .` | **Success! No dependency issues found.** (90 files) — loguru still declared *and* still imported, so neither DEP001 nor DEP002 |
| Type gate (gate 5) | `uv run mypy src/` | **Success: no issues found in 84 source files** |

Remaining `loguru` importers at `86b9274` — `src/backend/settings/registry.py:10`, `src/backend/settings/repository.py:22` (**T-004**), `src/backend/permissions/service.py` (**T-006**), and three test files (`tests/acceptance/logging/test_logging.py`, `tests/conftest.py`, `tests/logging_coverage_test_helpers.py` — the dual-capture half, T-006).

#### Freshly measured inventory — the 28 statements to migrate (as they stand at `86b9274`)

Parsed from the two files with the witness's own `_statement_calls` shape (`<recv>.<level>(...)`); every receiver is the module-level loguru `logger`. **Levels and wording are the values that must survive the migration** (spec §9 row 2).

`src/backend/settings/registry.py` — 17 statements (**9 DEBUG, 8 WARNING**), import at line 10:

| Line | Level | Message (current loguru brace form) | Positional args |
|---|---|---|---|
| 89 | `warning` | `duplicate registration: key={}` | `definition.key` |
| 94 | `debug` | `setting registered: key={} kind={}` | `definition.key`, `definition.kind` |
| 113 | `debug` | `feature settings registered: feature={} count={}` | `feature`, `len(definitions)` |
| 142 | `warning` | `value set rejected (invalid): key={}` | `key` |
| 146 | `debug` | `value set: key={}` | `key` |
| 160 | `debug` | `value reset: key={}` | `key` |
| 173 | `debug` | `value reset: key={}` | `key` |
| 244 | `warning` | `template create rejected (invalid name): name={}` | `name` |
| 248 | `warning` | `template create rejected (duplicate): name={}` | `name` |
| 255 | `warning` | `template create rejected (scope): name={}` | `name` |
| 259 | `warning` | `template create rejected (invalid value): name={} key={}` | `name`, `k` |
| 264 | `debug` | `template created: name={} category={} group={}` | `name`, `category`, `group` |
| 283 | `debug` | `template loaded: name={} count={}` | `name`, `len(template.values)` |
| 295 | `warning` | `template update rejected (scope): name={}` | `name` |
| 299 | `warning` | `template update rejected (invalid value): name={} key={}` | `name`, `k` |
| 308 | `debug` | `template updated: name={}` | `name` |
| 317 | `debug` | `template deleted: name={}` | `name` |

`src/backend/settings/repository.py` — 11 statements (**5 DEBUG, 6 ERROR**), import at line 22:

| Line | Level | Message (current loguru brace form) | Positional args |
|---|---|---|---|
| 140 | `debug` | `values saved to storage: count={}` | `len(values)` |
| 151 | `error` | `value storage failure: reason={}` | `e` |
| 154 | `error` | `value storage failure: reason={}` | `e` |
| 156 | `debug` | `values loaded from storage: count={}` | `len(result)` |
| 248 | `debug` | `template saved to storage: name={}` | `template.name` |
| 259 | `error` | `template storage failure: name={} reason={}` | `name`, `e` |
| 262 | `error` | `template storage failure: name={} reason={}` | `name`, `e` |
| 264 | `debug` | `template loaded from storage: name={}` | `name` |
| 281 | `error` | `template storage failure: reason={}` | `e` |
| 284 | `error` | `template storage failure: reason={}` | `e` |
| 286 | `debug` | `templates loaded from storage: count={}` | `len(templates)` |

Total **28** (14 DEBUG, 8 WARNING, 6 ERROR) — matches REQ-005's per-file counts and the witness's `17` / `11` arguments.

#### What the witness accepts (read from its own helpers)

- `_backend_imports` flags a `loguru` **or `structlog`** import — the migration must not reach for structlog directly (REQ-005: `get_logger()` is the only entry point).
- `_statement_calls` counts every `<recv>.<level>(...)` call (`debug|info|warning|warn|error|exception|critical|fatal|log`): the count must stay **exactly 17 and 11** — none added, none removed, none folded into a helper.
- `_written_via_get_logger` accepts an inline `get_logger(...).debug(...)` receiver **or** a name bound by an assignment (`_x = get_logger(...)`). The established pattern is the module-level binding: T-001's `src/backend/logging/feature_settings.py` (`_feature_logger = get_logger("logging")`) and T-005's `src/backend/eventbus/eventbus.py:27` (`_logger = get_logger("eventbus")`) — one feature-named binding per module. `get_logger()` with no name falls back to the caller's `__name__` (`_caller_module`, `_pipeline.py:188`), which the witness also accepts; the feature-named form is the one the two precedents use, and the name travels in the `logger_name` field (`_renderers.LOGGER_NAME_FIELD`).

#### Risk notes for S4.2

**A. The brace form must not be copied with positional args — this is why `implementation_steps` 2 says "keyword-field form".** The pipeline's chain is `_EMITTING_CHAIN = (callsite_adder(), exception_field)` + `ProcessorFormatter.wrap_for_formatter` (`_pipeline.py:202`); there is **no `PositionalArgumentsFormatter`**. Measured in T-005's S4.2 against structlog 26.1.0: positional args land in `event_kw["positional_args"]`, which `_renderers.INTERNAL_FIELDS` drops from every rendered record — so `get_logger("settings").debug("value set: key={}", key)` would emit the braces **unfilled** and discard the value. The proven form (T-005, `VERIFIED`) is an f-string event plus the same values as keyword fields, e.g. `_logger.debug(f"value set: key={key}", key=key)`. Keep the wording **character-for-character** (T-005's messages carry quotes only because the original eventbus wording did); only the interpolation mechanism changes.
**B. `reason={e}` keeps its wording under an f-string.** Loguru's `{}` and `f"{e}"` both render `str(e)`, so the six `error` sites in `repository.py` keep the same text; they stay `.error(...)` — **not** `.exception(...)` — because they are not exception records and `exception()` would add an `exc_info` field the current records do not carry (the spec forbids a level/semantics change).
**C. The record-capture path is already migrated, so the settings suites should not need touching.** Since T-002 the `log_records` fixture is **dual-backend** (`tests/conftest.py:84`: loguru sink + `pipeline_capture`), the tracing decorators already emit through the pipeline, and the pipeline capture sets the feature logger to `DEBUG` for the block (`logging_coverage_test_helpers.pipeline_capture`, which exists precisely because the pipeline gates level on the *logger*). The three settings-wording/level assertions that could break — `test_direct_loguru_kept.py:51-54`, `test_levels.py:66`, `tests/contract/settings/test_settings_contracts.py:193-210` (DEBUG for `app.name` / `t1`, ERROR for a storage failure) — are all in the `green_command` set and all currently green, two of them already fed by **migrated** eventbus statements. If any of them goes red, the fix belongs in the migrated **source** (wording/level), never in the test.
**D. Live reconfiguration can re-level the pipeline mid-test — already true today, not introduced here.** A `logging.*` `SettingChanged` event triggers `_reconfigure` → `pipeline_logger().setLevel(level)` (`_pipeline.py:303-318`), and the settings suites are the ones that write `logging.log_level` / `logging.log_file` (visible in the RED run's captured stderr). The suite is green today because traced settings records already travel on that logger and `conftest._drain_event_bus()` drains stale events before the sinks attach. T-004 must not "fix" any such flake by changing the capture; T-003 owns live reconfiguration.
**E. `pyproject.toml` and `src/backend/permissions/service.py` are out of scope.** After T-004, `loguru` is still declared and still imported by `permissions/service.py` plus the three test helpers — that is the deptry interlock (`design_constraints` 4) and resolves in T-006. `uv run deptry .` must stay clean at T-004's gate.
**F. Two modules, one feature name.** Both files bind their own module-level logger; using the same feature name (`get_logger("settings")`) in both keeps the `logger_name` field feature-scoped, matching T-005's `get_logger("eventbus")`. No test asserts a specific statement logger name, so this is a consistency choice, not a gate.

#### Completion gates (T-004, verbatim from the DAG)

1. RED observed on the `red_command` set; recorded here. **← this step**
2. The settings-half AC-009 witness passes.
3. No `loguru` import remains anywhere under `src/backend/settings/`.
4. The settings feature's whole test directory passes unchanged (no behavior delta) — baseline **87 passed**.
5. `uv run deptry .` clean; `uv run ruff check <changed paths>` clean; `uv run mypy src/` clean.

#### Gate table (S4.1, T-004)

| # | Gate | Command (verbatim) | Result |
|---|---|---|---|
| a | Task ready | T-004 `dependencies: ["T-001"]` (`VERIFIED`), `status: "PENDING"`; ready set {T-003, T-004} | confirmed |
| b | Its test present | collected and executed below | confirmed |
| c | **RED re-observed** | T-004 `red_command` verbatim | **1 failed, 0 passed (0.32 s)** — same as the S3.2 gate, one `AssertionError` naming the 2 backend imports + 28 statement lines |
| d | `green_command` baseline (pre-implementation) | the verbatim `green_command` | **1 failed, 87 passed (40.26 s)** |
| e | Scope | `git status --short` | only `docs/verification/structlog-logging.md` (this record); `src/`, `tests/`, `pyproject.toml`, specs, `docs/todo/`, `docs/questions/`, `.github/task-runner/tasks.json` (T-004 stays `PENDING` — S4.4's job) untouched |
| f | Full suite | not run (Phase 5 gate; per-task targeted run only) | n/a |

**Phase 4 (S4.1, T-004) gate: PASS — T-004 picked from the ready set, RED re-confirmed (1 failed, assertion naming the offending imports and all 28 statements), inventory measured, baselines recorded.** Next: S4.2 (T-004) — implement in the two settings files + confirm GREEN on the verbatim `green_command` (expect 88 passed).

---

### S4.2 T-004 — implement + confirm GREEN (2026-10-07)

**Objective:** migrate the 28 direct loguru statements in `src/backend/settings/registry.py` (17) and `src/backend/settings/repository.py` (11) to the logging feature's `get_logger()` surface (REQ-005 / AC-009; `logging-coverage.md` v2 REQ-010 / AC-010). **Files changed: exactly the two `allowed_files.source_files`** — no test file, no `pyproject.toml`, no spec, no task-status file (`git status --short` before the commit: the two source files only, plus this record).

#### What was implemented

Two import lines and two module-level bindings replace the backend — the pattern T-001 established (`src/backend/logging/feature_settings.py:22`) and T-005 shipped (`src/backend/eventbus/eventbus.py:27`), one feature-named binding per module, never one `get_logger()` call per statement (`get_logger()` re-runs `_configure_structlog()` on every call, `_decorator.py:86`):

```python
from backend.logging import get_logger, logged, logged_class   # registry.py
from backend.logging import get_logger, logged_class           # repository.py

_logger = get_logger("settings")
```

Both modules use the **same feature name** (`"settings"`) — S4.1 note F: no test asserts a statement logger name, and the name travels in the `logger` field (`_renderers.LOGGER_NAME_FIELD`), so the records of the whole feature stay attributable to it. Import direction unchanged (`backend.settings → backend.logging`, spec §10 row 2 — the edge already existed in both files). `logged` / `logged_class` imports and all **8 decorators** (`registry.py:51, 388, 405`; `repository.py:104, 121, 170, 195, 223`) untouched (ADR-060).

All 28 call sites converted to the proven form — **f-string event + the same values as keyword fields** (S4.1 note A: the chain has no `PositionalArgumentsFormatter`, so the brace/positional form would render the braces unfilled and drop the values). Wording is character-for-character the loguru text (spec §9 row 2), levels unchanged, `logger.error(...)` sites stay `.error(...)` — **not** `.exception(...)` (S4.1 note B: they are not exception records and `exception()` would add an `exception` field the current records do not carry).

#### Statement inventory — before → after (the count is a gate)

Re-parsed with the witness's own `_statement_calls` shape after the change:

| File | Before (`86b9274` / `a06796e`) | After | Levels preserved |
|---|---|---|---|
| `src/backend/settings/registry.py` | 17 | **17** | 9 DEBUG, 8 WARNING |
| `src/backend/settings/repository.py` | 11 | **11** | 5 DEBUG, 6 ERROR |
| **Total** | **28** | **28** | 14 DEBUG, 8 WARNING, 6 ERROR |

Nothing added, removed, folded into a helper, or moved (logging-coverage REQ-010 v2: statements stay statements). No new local/helper/function was introduced — the values are interpolated in the f-string and repeated as keyword fields, which is the whole delta (the values were already evaluated eagerly as loguru positional args).

#### Rendered-output spot check (JSON file sink, `renderer` default, level DEBUG)

Throwaway probe (not committed): register → duplicate → `register_feature` → invalid set → template create/duplicate/load/update/delete → corrupted template file → corrupted values file. Console = text, file sink = JSON; the file lines below are the migrated records (`logger` field = `settings`, `file`/`line` still point at the emitting statement):

```json
{"level":"DEBUG","logger":"settings","event":"setting registered: key=x.y kind=text","file":"registry.py","line":97,"key":"x.y","kind":"text"}
{"level":"WARNING","logger":"settings","event":"duplicate registration: key=x.y","file":"registry.py","line":92,"key":"x.y"}
{"level":"DEBUG","logger":"settings","event":"feature settings registered: feature=feat count=1","file":"registry.py","line":120,"feature":"feat","count":1}
{"level":"WARNING","logger":"settings","event":"value set rejected (invalid): key=x.y","file":"registry.py","line":153,"key":"x.y"}
{"level":"DEBUG","logger":"settings","event":"template created: name=t1 category=cat group=None","file":"registry.py","line":279,"name":"t1","category":"cat","group":null}
{"level":"DEBUG","logger":"settings","event":"values saved to storage: count=1","file":"repository.py","line":145,"count":1}
{"level":"ERROR","logger":"settings","event":"template storage failure: name=t2 reason=while parsing a flow node…","file":"repository.py","line":264,"name":"t2","reason":{"type":"ParserError","message":"while parsing a flow node…"}}
{"level":"ERROR","logger":"settings","event":"value storage failure: reason=while parsing a flow node…","file":"repository.py","line":156,"reason":{"type":"ParserError","message":"while parsing a flow node…"}}
```

Wordings are identical to the pre-migration loguru output (`SettingKind` is a `StrEnum`, so `f"{definition.kind}"` renders `text` exactly as loguru's `{}` did; `f"{e}"` renders `str(e)` exactly as loguru's `{}` did). The `reason` field carries the exception object and `_renderers._orjson_default` serializes it to `{type, message}` — the pipeline's designed handling for a bound exception, no record lost, no locals leaked (INV-002).

#### Gate table (S4.2, T-004)

| # | Gate | Command (verbatim) | Result |
|---|---|---|---|
| a | **T-004 GREEN** | `uv run pytest tests/acceptance/logging_coverage/test_statements_via_feature.py::test_ac_009_settings_statements_go_through_get_logger tests/acceptance/settings tests/unit/settings tests/contract/settings tests/property/settings tests/integration/settings -v` | **88 passed, 0 failed (39.90 s)** — exactly the S4.1 baseline prediction (1 failed + 87 passed → 88 passed): the settings-half AC-009 witness PASSED and the five settings directories are the pre-implementation **87 passed** unchanged (no behavior delta) |
| b | Cross-task witnesses | `uv run pytest tests/acceptance/logging_coverage/test_levels.py tests/acceptance/logging_coverage/test_direct_loguru_kept.py -v` | **2 passed (0.52 s)** — `test_levels` still sees the settings WARNING + `duplicate registration`, `test_direct_loguru_kept` still sees `setting registered: key=` and `value set: key=`; both now fed by **migrated** statements, which is the direct proof that wording and level survived |
| c | Ruff (changed paths, the ruff gate) | `uv run ruff check src/backend/settings/registry.py src/backend/settings/repository.py` / `uv run ruff format src/backend/settings/registry.py src/backend/settings/repository.py` | **All checks passed!** / **2 files left unchanged** (already formatted) / re-check **All checks passed!** |
| d | Types (T-004 completion gate 5) | `uv run mypy src/` | **Success: no issues found in 84 source files** (same file count as the baseline) |
| e | Dependency check (T-004 completion gate 5) | `uv run deptry .` | **Success! No dependency issues found.** (90 files) — loguru still declared *and* still imported by `permissions/service.py` + the three test helpers: the interlock S4.1 note E describes, lifted by T-006 |
| f | Full suite | not run (Phase 5 gate; per-task targeted run only) | n/a |

T-004 completion gates from the DAG: (1) RED recorded ✓ (S4.1); (2) the settings-half AC-009 witness passes ✓; (3) **no `loguru` import remains anywhere under `src/backend/settings/`** ✓ — `grep -rn loguru src/backend/settings/` matches only stale `__pycache__` byte-code, and the witness's feature-wide clause (`_dir_backend_imports`) is green; (4) the settings feature's whole test directory passes unchanged, **87 → 87** ✓; (5) deptry / ruff / mypy clean ✓.

Out of scope, untouched as required: `pyproject.toml` (loguru declaration → T-006), `src/backend/permissions/service.py` (→ T-006), every test file — including `tests/acceptance/logging_coverage/test_statements_via_feature.py`, listed in `allowed_files.test_files` but needing no edit (its helper was already fixed in T-005) — `docs/specs/`, `docs/tasks/`, `docs/todo/`, `docs/questions/`, and `.github/task-runner/tasks.json` (T-004's `status` stays `PENDING` — setting it is S4.4's job).

**Phase 4 (S4.2, T-004) gate: PASS — GREEN confirmed (88 passed, 0 failed) and recorded.** Next: S4.3 (T-004) — refactor, keep GREEN.
