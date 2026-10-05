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
