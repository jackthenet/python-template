# Verification Record: settings-public-registry-setter

**Change type:** CROSS-CUTTING. Classified **FEATURE** at P.1 and **reclassified CROSS-CUTTING at P.3
(2026-10-06)** when Q-2 was answered "all five singletons": the change now intentionally spans two or
more features (settings, eventbus, permissions, search, sessionmanagement) and changes shared
infrastructure (the module-singleton install mechanism), so criterion #3 of the Phase 0 table
applies. The reclassification re-ran P.2/P.3 for the wider scope; the same worktree and branch are
kept, and the branch was renamed `feature/…` → `crosscut/…` before P.4 (the branch was created at P.4
from `main`, already under the `crosscut/` name).

**Phase P status:** prepared at P.4 (draft spec + six spec amendments + traceability rows). P.5
(self-consistency + dependency smoke-test) has not run.

**Branch naming:** the branch was created at P.4 directly as `crosscut/settings-public-registry-setter`
— no `feature/…` branch ever existed for this change, so no `git branch -m` rename was needed.

**Branch / worktree:** `crosscut/settings-public-registry-setter` at
`C:/workspace/active-projects/python-template_kopie-worktrees/crosscut/settings-public-registry-setter`,
created from `main` at commit `de8a6a5` ("chore(settings-public-registry-setter): P.3 complete
(29/29 answered) -> Status: QUESTIONS-ANSWERED") — so the branch carries the TODO file and all 29
answered questions. The P.3 reclassification is therefore recorded on the branch's own base commit,
and the branch name already matches the final type.

**Normative basis:** `docs/specs/settings-public-registry-setter.md` (new, v1 draft) + one amendment
PR touching `docs/specs/settings.md` (v5), `docs/specs/event-bus.md` (v2),
`docs/specs/user-roles-permissions.md` (v2), `docs/specs/search.md` (v4),
`docs/specs/session-management.md` (v2), `docs/specs/logging-coverage.md` (v3) — all six in **one**
approval PR (Q-3).

---

## P.4 — What was produced

| Artifact | File | State |
|---|---|---|
| Draft spec (CROSS-CUTTING, with Impact Analysis) | `docs/specs/settings-public-registry-setter.md` | v1 draft, 16 REQ / 20 AC / 3 INV / 10 EDGE / 4 NFR; §12 Impact Analysis over 10 affected components |
| Amendment — settings | `docs/specs/settings.md` | **v5**: REQ-026 new; AC-040..AC-043, INV-011, EDGE-030..EDGE-033 new; REQ-014's singleton-surface enumeration and the §3 API block extended; §9 observability rows; §10/§11 rows |
| Amendment — event bus | `docs/specs/event-bus.md` | **v2** (Changelog section added): REQ-008 new; AC-013..AC-016, EDGE-011, EDGE-012 new; REQ-006 enumeration and NFR-004 public-API list extended; §9/§10 rows |
| Amendment — user roles & permissions | `docs/specs/user-roles-permissions.md` | **v2** (Changelog added): REQ-030 new; AC-041..AC-044, EDGE-027, EDGE-028 new; REQ-023 enumeration, §3 file-tree comment and Public API list extended; §10/§11 rows |
| Amendment — search | `docs/specs/search.md` | **v4**: REQ-024 new; AC-038..AC-041, EDGE-022, EDGE-023 new; REQ-017 enumeration, REQ-015 traced-function list, §3 API block and Public API list extended; §10/§11 rows |
| Amendment — session management | `docs/specs/session-management.md` | **v2** (Changelog added): REQ-023 new; AC-046..AC-049, EDGE-013, EDGE-014 new; REQ-020 enumeration, REQ-022 traced-function list, §3 API block and NFR-003 contract list extended; §10/§11 rows |
| Amendment — logging coverage | `docs/specs/logging-coverage.md` | **v3**: **no new ID** — five `module function` inventory rows in §3.1 for the five install operations + a note naming the pre-existing inventory gap (Q-15) |
| Traceability | `docs/verification/traceability.md` | new § *Settings Public Registry Setter Matrix*: 16 REQ + 20 AC + INV/EDGE/NFR rows for the change spec, plus the new IDs of the six amended specs — all `PENDING` (Test column filled in Phase 3) |

No implementation source file and no test file was written at P.4.

## ID allocation (Q-4: new IDs beside the existing singleton requirement, never a rewritten dated row)

| Spec | Existing singleton requirement (cited, enumeration extended only) | New IDs |
|---|---|---|
| `settings.md` | REQ-014 (AC-018), NFR-002 | REQ-026; AC-040..AC-043; INV-011; EDGE-030..EDGE-033 |
| `event-bus.md` | REQ-006 (AC-011), REQ-005 (reset shuts down), NFR-004 | REQ-008; AC-013..AC-016; EDGE-011, EDGE-012 |
| `user-roles-permissions.md` | REQ-023 (AC-028), NFR-003, REQ-004/REQ-005/AC-006 (static catalog, unchanged) | REQ-030; AC-041..AC-044; EDGE-027, EDGE-028 |
| `search.md` | REQ-017 (AC-032), REQ-015 | REQ-024; AC-038..AC-041; EDGE-022, EDGE-023 |
| `session-management.md` | REQ-020 (AC-041 create-once, AC-042 first call without repository → `ValueError`, AC-043 reset clears), REQ-022, NFR-003 | REQ-023; AC-046..AC-049; EDGE-013, EDGE-014 |
| `logging-coverage.md` | REQ-001 (the §3.1 inventory is normative), REQ-007 (concrete `slow_threshold_ms`) | none — five inventory rows only |

The change spec keeps its own ID space (REQ-001..REQ-016, AC-001..AC-020, INV-001..INV-003,
EDGE-001..EDGE-010, NFR-001..NFR-004). Every ID was taken as the next free number **read from the
file**, not guessed; every ID stays three-digit, matching the rest of `docs/specs/`. No existing ID
was renumbered, restated or deleted, and no dated row in any spec's own matrix or in
`docs/verification/traceability.md` was refreshed (convention B, decision Q-129).

## Facts verified against the code at P.4 (they bind Phase 2–4)

1. **The write sites are 12, not 14** (correction to the TODO's "Constraints and risks" wording):
   one in `src/` — `src/main.py:138` writing `_settings_registry_singleton[0]`, the alias imported at
   `src/main.py:68` (`from backend.settings.registry import _registry as _settings_registry_singleton`)
   — plus 11 in tests: `tests/settings_test_helpers.py:132,160,180`,
   `tests/eventbus_test_helpers.py:77,84`, `tests/acceptance/settings_coverage/test_setup_logger.py:31,55`,
   `tests/acceptance/settings_coverage/test_wiring.py:18`, `tests/contract/logging/test_logging_contracts.py:35`,
   `tests/property/logging/test_logging_properties.py:42`, `tests/unit/logging/test_logging_edges.py:32`.
   Nine of the eleven write `backend.settings.registry._registry[0]`, two write
   `backend.eventbus.eventbus._default_bus[0]`.
2. **There is no `src/backend/settings/_setup.py`** (TODO correction): the private settings slot is
   `_registry: list[SettingsRegistry | None] = [None]` at `src/backend/settings/registry.py:45`;
   `get_settings_registry()` is at `:361` (lazy write at `:373`), `reset_settings_registry()` at `:378`.
3. **Only one of the five slots is locked today**: `src/backend/search/service.py` has
   `_singleton_lock = threading.Lock()` (`:547`, `:558`, `:571`). The other four are a bare
   one-element list, so the lazy-create race is real today (REQ-006, AC-009, EDGE-033, EDGE-012, EDGE-028).
4. **Tracing today**: `get_settings_registry` / `reset_settings_registry`, `get_event_bus` /
   `reset_event_bus`, `get_search_service` / `reset_search_service` and `get_session_service` /
   `reset_session_service` carry `@logged(slow_threshold_ms=5)`; `get_permission_service` /
   `reset_permission_service` carry **no** `@logged`. The new install operations are specified with
   the same `@logged(slow_threshold_ms=5)` (REQ-010) so they match their traced siblings.
5. **The permission catalog is unaffected** (`user-roles-permissions.md` §3: the catalog is exactly
   the public non-underscore methods of the six public service classes, and wiring/registration
   functions, singleton getters and reset functions are explicitly not catalog entries). REQ-016 +
   AC-020 make that a testable non-change rather than an assumption.
6. **`src/main.py` keeps its wiring position.** `docs/specs/settings-coverage.md` REQ-002 requires the
   entrypoint to call each feature's `register_settings(registry)` once at startup before feature code
   runs; REQ-011 + AC-016 keep that wiring intact and only replace the mechanism
   (`_settings_registry_singleton[0] = …` → `set_settings_registry(…)`).

## Findings for the user (recorded, not silently resolved)

1. **Code/spec signature gap in `docs/specs/settings.md` §3.** The API block shows
   `def get_settings_registry() -> SettingsRegistry: ...`, but the
   real signature is `get_settings_registry(required: bool = True) -> SettingsRegistry | None`
   (`src/backend/settings/registry.py:361`), and the `required=False` guarded read is normative in
   `docs/specs/settings-coverage.md` REQ-012 (AC-016, EDGE-011). This change **does not** amend that
   block: the two guard forms the new spec had to cover are already normative in
   `settings-coverage.md`, and fixing the `settings.md` wording is an unrelated amendment. The new
   spec cites `settings-coverage.md` REQ-012 / AC-016 / EDGE-011 unchanged (EDGE-004, EDGE-032).
   If the user wants the `settings.md` §3 block corrected, that is a separate Spec Amendment PR.
2. **Pre-existing `logging-coverage.md` §3.1 inventory gap.** The permissions, search and
   session-management singleton getters/resets have no inventory rows at all (the search and session
   ones are nevertheless decorated `@logged` in code; the permissions pair is not). Q-15 scoped this
   change to adding rows for the **five new install operations only**, so the gap is left as a
   follow-up candidate and is named in the v3 changelog note rather than fixed here.
3. **`reset_event_bus()` is the only reset with a lifecycle effect** (it calls `bus.shutdown()`). The
   install operations deliberately neither start nor shut down anything (D14), so
   `set_event_bus()` + `reset_event_bus()` are not symmetric on lifecycle — specified as EDGE-006 /
   EDGE-007 and event-bus EDGE-011 so it cannot be read as an oversight.

## Version bump plan (Q-25)

CROSS-CUTTING → **minor** at S6.4, after a clean review report: `bump-my-version bump minor` taking
the project version from **0.6.1** (`pyproject.toml:4`) to **0.7.0**, working tree clean,
`tag = false` (tags are cut on `main` at release time). The bump commit is part of the reviewed PR.

## Phase plan (per the Phase Matrix, CROSS-CUTTING)

P.5 self-consistency + dependency smoke-test → S1.4 (commit the prepared spec, open the **single**
approval PR for the new spec + six amendments, human merge) → Phase 2 (S2.1 ADR decision — a new
public pattern across five features makes an ADR likely, but the call is S2.1's gate, not P.4's;
S2.2 task DAG grouped by affected feature) → Phase 3 (tests per DAG task, RED) → Phase 4 (implement,
GREEN) → Phase 5 (full gate set + traceability rows for **every** affected feature) → Phase 6 (review,
minor bump, PR, human merge) → S7.1 cleanup.

**Out of scope, deferred to their own TODOs** (spec §13): `public-api-import-boundary` (who may import
`backend.settings` / `backend.eventbus`) and `composition-root-factory` (a `create_app()` composition
root, deferred by Q-11).

## P.4 gate evidence

- `uv run python scripts/check_traceability.py` (run inside the change worktree, 2026-10-06):
  **PASS — 796 matrix rows, 136 spec IDs, 714 test functions.** Referential integrity holds for the
  new spec and the six amendments; the new rows are `PENDING`, which is a legal gate record.
- **Traceability rows are recorded, and CI will not force them.** `docs/verification/traceability.md`
  gained a `## Settings Public Registry Setter Matrix (spec amendment PR, 2026-10-06)` section — one row
  per `REQ` of the change spec, plus the new IDs of each amended spec, all `PENDING
  (settings-public-registry-setter P.4, 2026-10-06)` with the Test column left empty (the precedent is
  the structlog-logging P.4 section). Note that `scripts/check_traceability.py` treats requirement IDs
  as one **global** namespace across `docs/specs/`, so it would NOT have failed had these rows been
  omitted: only 7 IDs are genuinely new to the repository (`REQ-030`, `INV-011`, `EDGE-030`–`EDGE-033`,
  and the change-local `REQ-026`/`REQ-024`/`REQ-023`/`REQ-008` which collide with existing IDs of other
  specs). **Phase 3 must fill the Test column of these rows deliberately** — CI will not remind it.
- No test or implementation file was created or modified, so the ruff gate is `n/a` for this step.
- `docs/todo/` and `docs/questions/` were **not** touched in this worktree (orchestrator-owned,
  `main`-only).

## P.5 — Self-Consistency Checklist + Dependency Smoke-Test (2026-10-06)

The spec under test is `docs/specs/settings-public-registry-setter.md` as drafted at P.4 (`1dbddb6`).
Every failure below was fixed **in the spec text**; nothing in `src/` or `tests/` was written, and no
requirement was weakened to make the spec self-consistent. The six amended approved specs were **not**
edited (P.5's file set is the change spec, this record, and `docs/workflow/PROBLEMS.md`) — where an
amendment is inconsistent, the divergence is recorded here as a finding for the S1.4 reviewer.

### Checklist, item by item

| Item | Verdict on the P.4 draft | Fix applied to the spec |
|---|---|---|
| **Configurability** | PASS. The spec makes no "configurable X" claim: the install operations take no configuration, no settings key is added or changed, and the only new parameter is the instance itself. | — |
| **Parameter coverage** | PASS. Each `set_*(instance)` has exactly one parameter, typed as the concrete class, with **no** default and no `None` acceptance — stated by REQ-004 / AC-007 / AC-008 and D5/D6/D7 (Q-7, Q-9, Q-23). `@logged(slow_threshold_ms=5)` names its parameter and its value; `include_args` is explicitly left at the decorator default (D9). | Added to D9 the sentence that Q-14 governs over Q-5's passing mention of `include_args=False`, so an implementer does not flip it. |
| **REQ↔AC wording** | **FAIL ×3.** (1) REQ-012 required "no existing test is weakened, converted or deleted" with no AC able to evidence it. (2) REQ-008 / INV-001 / AC-009 / AC-010 / AC-011 asserted "no read raises" and "exactly one default instance was constructed" for **all five** features, but `get_session_service()` with no `repository` argument raises `ValueError` (`session-management.md` EDGE-003, AC-042) — those assertions are unsatisfiable for session-management. (3) INV-001 ("no install is ever silently lost") read as contradicting EDGE-010 ("no lost update beyond the last writer"). | (1) REQ-012 now cites its evidence path (AC-017 + the Phase 5 full-suite regression + the Phase 6 no-weakening review) instead of implying an untestable AC — no new ID was invented, so §10/§11 and `docs/verification/traceability.md` stay ID-stable. (2) The lazy-create assertions are scoped to the four features whose `get_*()` builds a default; session-management is covered by an injected-repository variant, and AC-010's final slot value may also be a lazily created default. (3) INV-001 now reads "no install is lost **without a WARNING record** — last writer wins", which is exactly EDGE-010. |
| **Terminology drift** | **FAIL.** The draft mixed "install operation", "public setter" and "installer" (including in the test name `test_ac_019_agents_md_names_installer`). | §3.1 now declares **install operation** the normative term, with "setter"/"installer" as prose and test-name shorthand. |
| **Test strategy coverage** | PASS (measured). All 53 of the spec's own IDs (REQ-001…016, AC-001…020, INV-001…003, EDGE-001…010, NFR-001…004) appear in §10 with a category and a test function. §11 covers EDGE-002…006 and NFR-002/003 by range rows (`EDGE-001 … EDGE-007`, `NFR-001 … NFR-004`); Phase 5 expands those range rows when the rows land in `docs/verification/traceability.md`. | — |
| **ID references** | **FAIL ×2.** (1) NFR-002 benchmarked install latency against "the existing logging **NFR-002** budget", but `logging-coverage.md` NFR-002 is *Security* (no raw tokens/passwords/hashes in any log record); the performance NFR is **NFR-001**. (2) EDGE-005 cited "the **four** subprocess-embedded test sites"; `rg` measures **three** (`tests/acceptance/settings_coverage/test_wiring.py:18`, `tests/acceptance/settings_coverage/test_setup_logger.py:31,55`). | (1) NFR-002 now cites `logging-coverage.md` NFR-001 and `settings.md` NFR-001. (2) EDGE-005 and AC-017 now say three, and REQ-012 / §1 state the measured total of **12** outside-owner write sites. |
| **Scope consistency** | PASS after fix. Every in-scope item has a REQ; every §13 out-of-scope item (composition-root factory, runtime type validation, install events, lifecycle of the replaced instance, catalog actions, ADR) is excluded by a REQ/decision that does not accidentally cover it. The §12 Impact Analysis named the features but **omitted IDs the amendments actually introduce**. | §12 row 4 now names `search.md` REQ-015 and NFR-003, row 5 now names `session-management.md` REQ-022 and NFR-003; row 1 records the `settings.md` §3/§9 additions and the AC-042 divergence below. |
| **Performance budget vs. observability** | **FAIL.** NFR-002's < 1 ms budget has to hold with the mandated `@logged` tracing plus the WARNING record, and its measurement context was mis-described as "console + queue sinks" — `src/backend/logging/sinks` configures a **console sink on `sys.stderr`** plus a **rotating file sink with `enqueue=True`**; there is no queue sink. | NFR-002 now covers *either* path (empty-slot install, or a replace including its WARNING record) and states the logging context as the console (stderr) sink plus the enqueued rotating file sink, at DEBUG. NFR-003 keeps the lock short and puts the WARNING **after** the lock is released, so the budget does not pay for sink I/O under the lock. |

### Dependency Smoke-Test

No new dependency is named (stdlib `threading`; already-installed ruff / pytest / mypy; §12 row 9 records
"no new dependency"). Per the skill's *capability, not library* rule, the newly named **tooling
capability** — a ruff `TID251` banned-api guard — was smoke-tested on the host before being baked into the
spec. Measured on this host with the repository's own ruff, against temporary fixture files outside the
repository (nothing left behind):

| Probe | Result | Consequence for the spec |
|---|---|---|
| `banned-api` entry keyed by the **bare slot name** (`"_registry"`) | `All checks passed!` — flags **nothing** | §3.4 keys MUST be fully qualified (`backend.settings.registry._registry`, …); EDGE-009 states this. |
| Fully-qualified key + `from backend.settings.registry import _registry` | `TID251` reported | AC-018 (import form). |
| Fully-qualified key + `import backend.settings.registry as reg` then `reg._registry[0] = …` | `TID251` reported | AC-018 now names **both** reference forms. |
| Fully-qualified key, violation written **inside the owner module** (a probe `backend/search/service.py` writing its own `_singleton`) | **not** reported (only unrelated `PLW0602` from the probe's `global`) | EDGE-008 holds as written: the five owner modules keep their direct slot writes and need no `noqa`. |
| The project's real `[tool.ruff.lint] select` (`I,E,W,B,F,UP,RUF,PL,Q,SIM,C4,DTZ`) + a `banned-api` table, **without** `TID251` selected | the violation is **not** reported (only `F401`) | **Material fix:** §3.4 and §12 row 9 now require adding `TID251` to `[tool.ruff.lint] select` — without it the guard is inert and AC-018 would pass vacuously. |
| `uv run ruff check --isolated --select TID src tests` (whole TID family) | `All checks passed!` — zero pre-existing violations | Selecting the rule cannot break the lint gate by itself; §10 records it. |
| `uv run ruff check --isolated --select TID252 src tests` | `All checks passed!` | Not needed: only `TID251` is selected, keeping Q-19's ban width. |

### Facts re-measured at P.5 (they bind Phase 2–4)

- **Outside-owner singleton-slot writes: 12, not 14.** `rg` over `src/` and `tests/` for the five slot names
  gives `src/main.py:138` plus 11 test sites (`tests/settings_test_helpers.py:132,160,180`;
  `tests/eventbus_test_helpers.py:77,84`; `tests/acceptance/settings_coverage/test_setup_logger.py:31,55`;
  `tests/acceptance/settings_coverage/test_wiring.py:18`; `tests/contract/logging/test_logging_contracts.py:35`;
  `tests/property/logging/test_logging_properties.py:42`; `tests/unit/logging/test_logging_edges.py:32`).
  `docs/todo/settings-public-registry-setter.md` says **14** because it counts the 3 subprocess-embedded
  writes separately from the 9 settings sites, although they are inside those 9. P.5 may not edit the TODO
  file, so the correction lives here and in the handoff; the spec states 12.
- **Inside-owner writes: 10** (`settings/registry.py:373,380`; `eventbus/eventbus.py:221,232`;
  `search/service.py:560,572`; `sessionmanagement/service.py:364,371`; `permissions/service.py:524,530`) —
  all stay, under the module lock (Q-13).
- **`tests/unit/architecture/` does not exist**, and neither does `tests/architecture/`: the
  `architecture-tests-missing` change (merged, `4f684f8`) removed that path from the workflow, and its own
  architecture checks were `rg` scans recorded in its verification record, not test files. The new scan test
  therefore creates a new package and needs an `__init__.py` (every other test package has one). §10 records
  this and points at the only existing source-scanning test,
  `tests/acceptance/logging_coverage/test_new_classes_traced.py` (`ast.parse` over
  `pathlib.Path("src/backend").rglob("*.py")`, CWD-relative because pytest runs from the repository root).
- **`src/main.py` order measured:** `_settings_registry = SettingsRegistry(...)` at `:137`, the private-slot
  write at `:138`, then `register_*_settings(_settings_registry)` at `:173-178` and the service-construction
  sites at `:161,198,204,214` — all passing the **local handle**, never `get_settings_registry()`. REQ-011,
  D10 and AC-016 now state the read-back rule *and* the install-before-register ordering that makes
  `settings-coverage.md` REQ-002 literally true, instead of describing the read-back as if it already happened.

### Findings recorded, not silently resolved

1. **`settings.md` AC-042 is narrower than its four siblings.** As amended by P.4 it covers concurrent
   install + read; `event-bus.md` AC-015, `user-roles-permissions.md` AC-043, `search.md` AC-040 and
   `session-management.md` AC-048 cover install + read + **reset**, and Q-10/Q-11 require the module lock to
   guard all three operations in every feature. The change spec's AC-010 is the stronger rule (all five
   features, all three operations) and its test covers reset, so the change is self-consistent as specified.
   Widening `settings.md` AC-042 is an edit to an approved spec, outside P.5's file set — **the S1.4 reviewer
   should widen it in the same approval PR**; §12 row 1 records the divergence.
2. **`docs/todo` says 14 write sites; measurement says 12** (see above). The orchestrator may correct the TODO
   text on `main`; the spec and this record use 12.
3. **`settings.md` §3's simplified `get_settings_registry()` signature block** (no `required`, non-nullable
   return) remains unamended — carried over from the P.4 findings list, unchanged by P.5.

### P.5 gate evidence

- `uv run python scripts/verify_spec.py` (in the change worktree, 2026-10-06) — **PASS** for all seven
  touched specs: `settings-public-registry-setter`, `settings`, `event-bus`, `user-roles-permissions`,
  `search`, `session-management`, `logging-coverage` (plus `settings-coverage`, cited but unamended).
- `uv run python scripts/check_traceability.py` — **PASS (796 matrix rows, 136 spec IDs, 714 test
  functions)**. P.5 added, removed and renumbered **no** ID, so the P.4 rows still cover every ID.
- Ruff: `n/a` — no test or implementation file was written; the ruff probes ran on temporary fixture files
  outside the repository.
- Files changed by P.5: `docs/specs/settings-public-registry-setter.md`, this record,
  `docs/workflow/PROBLEMS.md`. `docs/todo/`, `docs/questions/`, `src/`, `tests/` and the six amended specs
  were not touched.

## S2.1 — ADR decision (2026-10-07)

**Cached Spec Approval Gate (recorded here, not re-checked in this step).** Approval PR **#73** was
merged into `main` as merge commit **`a1a15db`** (2026-10-06T20:07:48Z), carrying the new spec plus all
six spec amendments in one PR (Q-3). The gate is satisfied and the result is cached per AGENTS.md
(“verify once per change”); later steps read this line and MUST NOT re-run
`git log main -- docs/specs/settings-public-registry-setter.md`. The P.5 finding that `settings.md`
AC-042 is narrower than its four siblings was **not** widened by the reviewer, so the change implements
against its own **AC-010** (install + read + **reset**, all five features), which is the stronger rule.

### Threshold applied

AGENTS.md Phase 2 item 1 / decompose SKILL §S2.1: an ADR is required only for a decision that
introduces a **new dependency**, a **new pattern/architecture element**, or a **cross-feature
interface**. Measured against the code on this branch:

- **No new dependency** — stdlib `threading`, plus already-installed ruff / pytest / mypy
  (§12 row 9). No dependency ADR.
- **A new cross-feature interface** — five features gain the same new public operation, called by the
  composition root and by every state-isolating test helper; 12 outside-owner private-slot writes exist
  today (`src/main.py:138` + 11 test sites). → **ADR-083**.
- **A new pattern/architecture element in the quality gate** — first use of ruff `banned-api` in this
  repository (`grep -rn "banned-api|flake8-tidy" pyproject.toml` → no match; `[tool.ruff.lint] select`
  at `pyproject.toml:182` contains no `TID` rule) and the first `tests/unit/architecture/` package.
  → **ADR-084**.

### Which decisions got an ADR, and which did not

| Spec decision | ADR | Why |
|---|---|---|
| D6 + D7 (one module-level lock guarding install, lazy create and reset; the owner keeps its direct lazy write) | **ADR-083** | Same architectural element as the interface — the slot-access pattern. Splitting it off would be a second ADR about one variable. |
| D12 (two guards: ruff `TID251` banned-api + a pytest source-scan test) | **ADR-084** | New enforcement pattern for the repository, with five measured shape-facts (the table is inert without `TID251` in `select`; bare-name keys flag nothing; owner-module writes are not flagged; both import forms are flagged; zero pre-existing `TID` violations) and a real rejected precedent (the `rg` scans of `architecture-tests-missing`). |
| D1 (`set_*` beside `get_*`/`reset_*`), D2 (replace + exactly one WARNING), D3 (not retroactive), D4 (never `None`), D5 (annotation + mypy only), D8 (no event), D14 (no lifecycle effect) | inside **ADR-083** | Boundary rules *of* the new interface — WHAT-level detail already fixed by the spec; they introduce no pattern beyond the trio, so they are stated in the Decision and argued in its Alternatives, not as separate ADRs. |
| D9 (`@logged(slow_threshold_ms=5)`, default `include_args`) | none | Reuses the existing tracing policy (ADR-060) and the siblings' existing threshold — no new pattern. |
| D10 (composition root keeps its module-import-time position) | none | The *new* pattern (a `create_app()` factory) is explicitly deferred to TODO `composition-root-factory`; keeping the position is the conservative non-decision. |
| D11 (test migration keeps capture-install-restore semantics) | none | Mechanical migration of 11 sites; the semantics are the helpers' existing contract. |
| D13 (one `AGENTS.md` bullet per feature) | none | Documentation placement. |
| D15 (no ADR at P.4, decision deferred to S2.1) | closed by this section | — |

### ADR files

| File | Title | Supersedes |
|---|---|---|
| `docs/decisions/ADR-083-public-install-operation-feature-singletons.md` | Public install operation (`set_*`) as the third member of the singleton trio, one module lock per slot | **nothing** — extends ADR-009, ADR-017, ADR-040, ADR-065 (all decisions stand) |
| `docs/decisions/ADR-084-two-guards-singleton-slot-tid251-scan-test.md` | Two guards for the singleton slot — ruff `TID251` banned-api plus a source-scanning architecture test | **nothing** — replaces the *mechanism* of the `rg` scans recorded in `docs/verification/architecture-tests-missing.md`, which were never an ADR |

No existing ADR was edited, renumbered or marked superseded. The clarification that matters is recorded
inside ADR-083: **ADR-017's `threading.RLock` guards `SettingsRegistry` instance state, while this
change's module-level lock guards the slot variable** — two different locks, and `settings/registry.py`
ends up holding both.

**Numbering.** Highest ADR file present: `ADR-082-structlog-processor-layer-over-stdlib.md`;
`ADR-081` is **not on disk and is deliberately left unclaimed** for the `api-keys` change
(`docs/todo/api-keys.md:64`, “ADRs from **ADR-081**” — the same reservation ADR-082’s own
“Numbering” consequence records). This step therefore took the next two free numbers, **083** and
**084**. Verified with `ls docs/decisions` (82 files, no `ADR-081*`) and
`git log --all --oneline -- "docs/decisions/ADR-081*"` (empty).

### ID traceability

- **ADR-083** — change spec REQ-001…REQ-012, AC-001…AC-014, AC-016, INV-001…INV-003,
  EDGE-001…EDGE-007, EDGE-010, NFR-001…NFR-003 (D1–D8, D10–D11, D14); amended specs
  `settings.md` v5 REQ-026 / AC-040…AC-043 / INV-011 / EDGE-030…EDGE-033,
  `event-bus.md` v2 REQ-008 / AC-013…AC-016 / EDGE-011–012,
  `user-roles-permissions.md` v2 REQ-030 / AC-041…AC-044 / EDGE-027–028,
  `search.md` v4 REQ-024 / AC-038…AC-041 / EDGE-022–023,
  `session-management.md` v2 REQ-023 / AC-046…AC-049 / EDGE-013–014,
  `logging-coverage.md` v3 (five §3.1 rows, no new ID).
- **ADR-084** — change spec REQ-012, REQ-013, AC-017, AC-018, EDGE-005, EDGE-008, EDGE-009, NFR-004
  (D12, §3.4, §10).

Every ID cited in the two ADRs is defined by a spec on this branch (checked against
`docs/specs/settings-public-registry-setter.md` and `docs/specs/settings.md` v5); no ID was invented,
renumbered or restated by this step.

### S2.1 gate evidence

- Worktree (printed with the counts, per P-57): `git rev-parse --show-toplevel` →
  `C:/workspace/active-projects/python-template_kopie-worktrees/crosscut/settings-public-registry-setter`.
- Files created by S2.1: the two ADR files above. Files modified: this record only.
  `src/`, `tests/`, `pyproject.toml`, `AGENTS.md`, `docs/specs/`, `docs/tasks/`,
  `.github/task-runner/`, `docs/todo/` and `docs/questions/` were **not** touched.
- `docs/decisions` file count: **82 before → 84 after** (`ls docs/decisions | wc -l`, same command in the
  same worktree).
- Ruff: **`n/a`** — no Python or TOML file was written or modified by this step.
- Done-criteria check: an ADR exists for every decision that passes the threshold (2), the below-threshold
decisions are listed with reasons above, and both ADRs plus this record are committed on the change branch.
S2.2 (task DAG, grouped by affected feature per §12) is the next step and was **not** run here.

---

## S2.2 — Task DAG (2026-10-07)

CROSS-CUTTING, so the DAG is grouped by affected feature (spec §12): one group per singleton-owning
feature, then the cross-cutting groups. 12 tasks, all `status: "PENDING"`.

### Artifacts

| File | Role | sha256 |
|---|---|---|
| `docs/tasks/settings-public-registry-setter.tasks.json` | the task DAG (12 tasks, 109,619 bytes) | `abdc38efeb81aadcf655c3c9735c342c421021ea0cc7a36517506a9aab43e255` |
| `.github/task-runner/tasks.json` | the active build environment (byte-identical copy, 109,619 bytes) | `abdc38efeb81aadcf655c3c9735c342c421021ea0cc7a36517506a9aab43e255` |

`cmp docs/tasks/settings-public-registry-setter.tasks.json .github/task-runner/tasks.json` → no output
(byte-identity, the repo invariant). Both files were written from one builder run
(`build_dag_sprs.py`, kept in a temp directory **outside both worktrees**, so the two copies cannot
drift and no build script is committed).

### Validator output (recorded, because CI does not enforce it)

```text
$ uv run python scripts/validate_task_dag.py .github/task-runner/tasks.json
Task DAG validation PASSED: 12 tasks, acyclic, well-formed.            exit 0

$ uv run python scripts/validate_task_dag.py docs/tasks/settings-public-registry-setter.tasks.json
Task DAG validation PASSED: 12 tasks, acyclic, well-formed.            exit 0
```

The second invocation also runs the script's docs↔runner sync check (task-id sets + per-task
`status`). `.github/workflows/spec-validation.yml:54` runs the validator with `|| true` (and
downgrades `scripts/verify_spec.py` to a message at `:50`), so a DAG failure never fails CI —
which is exactly why the validator result and the coverage result are recorded here.

### Schema

Per-task keys, in this order: `task_id, feature_group, title, description, requirements,
acceptance_criteria, invariants, edge_cases, non_functional, amended_spec_ids, tests_to_create,
red_command, implementation_steps, green_command, inputs, allowed_files{source_files,test_files},
implementation_scope, design_constraints, completion_gates, dependencies, status`.

- The dependency field is **`dependencies`**, not `depends_on`: `scripts/validate_task_dag.py:29`
  requires it (`required_fields = ["task_id", "title", "status", "dependencies", "requirements",
  "acceptance_criteria"]`) and every existing DAG uses it.
- The shape matches `docs/tasks/structlog-logging.tasks.json` (the most recent DAG, in the
  `crosscut/structlog-logging` worktree) so Phase 4/5 reads one form.
- Top level: `feature, spec, branch, change_type, version, adrs, spec_approval, grouping,
  amended_specs, ci_gates_read_from, interlock, open_findings, id_coverage, tasks`. The cached
  Spec Approval Gate result (PR #73 → `a1a15db`, 2026-10-06T20:07:48Z) is carried in `spec_approval`
  so no later step re-runs the check.

### Task list — IDs per task

| Task | Feature group | REQ | AC | INV / EDGE / NFR | depends on |
|---|---|---|---|---|---|
| T-001 | settings | 001,002,004–010,014 | 001 | — | — |
| T-002 | eventbus | 001–010,014 | — | — | T-001 |
| T-003 | permissions | 001,002,004–010,014,016 | — | — | T-001, T-002 |
| T-004 | search | 001,002,004–010,014 | — | — | T-001…T-003 |
| T-005 | session-management | 001,002,004–010,014 | — | — | T-001…T-004 |
| T-006 | composition root (`src/main.py`) | 011,012 | 016 | — | T-001 |
| T-007 | test infrastructure (11 write sites) + the architecture scan guard | 012,013 | 017 | EDGE-008 | T-001, T-002, T-006 |
| T-008 | tooling — `pyproject.toml` ruff configuration | 013 | 018 | EDGE-009, NFR-004 | T-007 |
| T-009 | cross-feature witness set — install semantics, API contract, catalog, latency | 001–005,009,014,016 | 002–008,013,020 | INV-002, INV-003, EDGE-001–007, NFR-001, NFR-002 | T-001…T-005 |
| T-010 | cross-feature witness set — the module lock | 006,007,008 | 009–012 | INV-001, EDGE-010, NFR-003 | T-001…T-005, T-009 |
| T-011 | logging coverage — the five install operations in the §3.1 inventory | 010 | 014,015 | — | T-001…T-005, T-009 |
| T-012 | guidance — AGENTS.md “Using the …” sections | 015 | 019 | — | T-001…T-005, T-008, T-009 |

(REQ/AC columns abbreviate the change spec's own `REQ-`/`AC-` IDs.)

### One-line scope per task

- **T-001 settings** — `set_settings_registry()` + a module lock guarding install, lazy create (both
  `required` modes) and reset in `src/backend/settings/registry.py`; package re-export.
- **T-002 eventbus** — `set_event_bus()` + module lock in `src/backend/eventbus/eventbus.py`; reset
  still shuts the slot's bus down; the replaced bus never is.
- **T-003 permissions** — `set_permission_service()` + module lock in `src/backend/permissions/service.py`;
  `get_permission_service`/`reset_permission_service` stay untraced (out of scope).
- **T-004 search** — `set_search_service()` guarded by the module's **existing** `_singleton_lock`
  (`src/backend/search/service.py:547/558/571`) — no new lock (search.md v4).
- **T-005 session-management** — `set_session_service()` + module lock in
  `src/backend/sessionmanagement/service.py`; no lazy-create path exists, so the repository-argument
  rule (`ValueError`) is unchanged.
- **T-006 composition root** — `src/main.py` installs through `set_settings_registry()` at its current
  module-import-time position (`:137-138`), imports no private slot (`:68`), and reads the shared
  instance back through `get_settings_registry()` at `:161`, `:173-178`, `:198`, `:204`, `:214`.
  Write site 1 of the 12.
- **T-007 test infrastructure + scan guard** — migrate the remaining **11** private-slot writes
  (3 in `tests/settings_test_helpers.py`, 2 in `tests/eventbus_test_helpers.py`, 6 in the logging /
  settings-coverage witnesses, three of them code strings handed to subprocess) to the public
  operations, and add `tests/unit/architecture/test_singleton_slots.py`, which flags foreign slot
  writes both as real statements and inside subprocess strings while owner writes stay allowed.
- **T-008 tooling** — add `TID251` to `[tool.ruff.lint].select` (only TID251) and the five fully
  qualified `banned-api` entries; the contract test runs ruff on a `tmp_path` fixture and asserts
  `uv run ruff check .` stays clean.
- **T-009 cross-feature semantics** — the parametrized witnesses over all five singletons: install →
  get, replace → exactly one WARNING naming the shared default, not retroactive, never `None`, no
  `isinstance`, no event, replaced instance neither started nor shut down, the public API contract,
  the unchanged 60-key permission catalog, and NFR-001/NFR-002.
- **T-010 cross-feature lock** — concurrent lazy create (one instance), concurrent
  install/read/reset (never a torn slot), the lazy path emitting exactly one traced pair, and
  install → reset → default for the four features whose `get_*()` builds a default.
- **T-011 logging coverage** — each install operation traced with `@logged(slow_threshold_ms=5)` and
  present as a module-function row in the logging-coverage inventory
  (`tests/logging_coverage_test_helpers.py:76 INVENTORY_MODULE_FUNCTIONS`).
- **T-012 guidance** — one AGENTS.md bullet per feature naming its install operation, the
  replace-plus-WARNING semantics and `reset_*()` as the test seam, plus the guidance contract test.

### Dependency graph

```text
T-001 ─┬─ T-002 ─┬─ T-003 ─┬─ T-004 ─┬─ T-005
       │         │         │         └──────────────┐
       │         │         └─ T-006 (main.py)       │
       │         └─ T-007 (11 sites + scan) ─ T-008 (ruff)
       └────────────────────────────────────────────┼─ T-009 ─┬─ T-010
                                                    │         ├─ T-011
                                                    └─────────┴─ T-012 (also needs T-008)
```

The five feature tasks are chained (T-001 → T-005) rather than independent: no task calls a later
task's service method, but they share the `tests/*/singleton_install/` packages and the singleton
semantics must converge in one order, so the chain fixes the order instead of leaving it to chance.

### ID coverage

- **Change spec** `docs/specs/settings-public-registry-setter.md`: **53** normative IDs
  (16 REQ, 20 AC, 3 INV, 10 EDGE, 4 NFR) → **53 assigned, 0 unassigned, 0 unknown**. The builder
  computes this and aborts the write if any ID is unassigned or any assigned ID is undefined, so the
  number is measured, not asserted by hand. The full ID → task map is in the JSON under
  `id_coverage.by_id`.
- **Amended feature specs**: 40 IDs, listed per task under `amended_spec_ids` and aggregated per file
  under `id_coverage.amended_specs` — `settings.md` v5: 10 (REQ-026, AC-040…043, INV-011,
  EDGE-030…033) → T-001; `event-bus.md` v2: 7 → T-002; `user-roles-permissions.md` v2: 7 → T-003;
  `search.md` v4: 7 → T-004; `session-management.md` v2: 7 → T-005; `logging-coverage.md` v3: 1
  (five new §3.1 rows, no new ID) → T-011; `settings-coverage.md`: 1 (REQ-002 cited unchanged) → T-006.
- **IDs are namespaced per spec file and collide across the six specs** (`AC-041` is settings.md
  AC-041 in T-001 and user-roles-permissions.md AC-041 in T-003). Change-spec IDs are written bare;
  feature-spec IDs are always qualified by the file name — in the DAG and in this record.
- T-002…T-005 carry an empty change-spec `acceptance_criteria` list **by design**: their evidence is
  their own feature's amended-spec ACs, whose test functions are named in `tests_to_create`
  (e.g. `tests/acceptance/eventbus/test_eventbus.py::test_ac_013_set_event_bus_installs_default`).
  No normative ID of any spec involved is left without an executable test.

### Gate satisfiability (decompose skill check)

Every test in a task's `tests_to_create` can pass using only that task plus its declared
`dependencies`:

- T-001…T-005 need only their own module (each feature's install operation and lock).
- T-006 needs `set_settings_registry` (T-001) — the only operation `src/main.py` calls.
- T-007 needs `set_settings_registry` (T-001) and `set_event_bus` (T-002) — the only two operations
  its 11 migrated sites call — plus T-006, because its scan test asserts the whole repository is free
  of foreign slot writes and `src/main.py` is one of the 12 sites.
- T-008 needs T-007: with every private-slot import migrated, enabling TID251 cannot break
  `uv run ruff check .`.
- T-009 needs T-001…T-005. T-010 and T-011 additionally depend on T-009 because they extend files
  T-009 owns (`tests/singleton_install_test_helpers.py`,
  `tests/acceptance/singleton_install/test_install.py`,
  `tests/property/singleton_install/test_install_properties.py`).
- T-012 needs T-008 (owner of `tests/contract/singleton_install/__init__.py`) and T-009.

No test was moved or deleted to satisfy the rule, and no task's gate calls a later task's API.

### allowed_files = each task's own witness scope (PROBLEMS.md P-55)

- T-001 **creates** `tests/singleton_install_test_helpers.py` (the five
  `(module, installer, getter, reset, instance-factory)` tuples the parametrized witnesses run over)
  and names `tests/settings_test_helpers.py` read-only (its writes belong to T-007).
- T-002 names `tests/eventbus_test_helpers.py` read-only; T-004 `tests/search_test_helpers.py`;
  T-005 `tests/sessionmanagement_test_helpers.py` + `tests/unit/sessionmanagement/conftest.py`.
- T-007 lists all 11 migrated sites by path **and line**, plus the new `tests/unit/architecture/`
  package (`__init__.py` + the scan test).
- T-008 owns `pyproject.toml` — the `[tool.ruff.lint].select` and
  `[tool.ruff.lint.flake8-tidy-imports.banned-api]` tables and nothing else in it.
- T-011 names `tests/logging_coverage_test_helpers.py` (the inventory data it must extend).
- T-009/T-010/T-011 list the five owner modules as **fix-only** entries: their witnesses may expose a
  uniformity or lock-scope defect, and the fix belongs in the owning module, recorded against that
  feature.

### CI gates named in completion_gates (PROBLEMS.md P-56, read from the workflow files)

- `.github/workflows/lint.yml:37` `uv run ruff check .`, `:39` `uv run ruff format --check .`
- `.github/workflows/quality.yml:23` mypy (gate); `:25-26` `uv run ty check src/` is
  **informational** (`continue-on-error: true`) and is named as such, never as a gate; `:41`
  pip-audit; `:43` bandit; `:59` `uv run pytest tests/ --cov --cov-report=xml` with the floor
  `fail_under = 92` (`pyproject.toml:110`); `:94` deptry; `:109` `mkdocs build --strict`; `:127`
  `alembic upgrade head`; `:144` `uv run complexipy src tests --max-complexity-allowed 15` (gate).
- `.github/workflows/spec-validation.yml:48` `verify_spec.py`, `:54` `validate_task_dag.py`
  (`|| true`), `:68` `check_traceability.py`, `:84` `pytest tests/ -v`.
- Only **T-008** carries the repository-wide ruff sweep (it changes the lint configuration); every
  other task's ruff gate is scoped to its own changed paths.

### red_command / green_command are targeted (PROBLEMS.md P-56)

Every command names individual pytest **node IDs** for that task's own tests — never the full suite
(the full suite is a Phase 5 gate). Node IDs rather than whole files are required by this change's
layout: Phase 3 derives every task's tests before Phase 4 starts, so the shared files
(`tests/acceptance/singleton_install/test_install.py`,
`tests/property/singleton_install/test_install_properties.py`) will already hold other tasks'
failing tests, and a file-level command could never go GREEN for one task.

### Breaking-change rule (decompose skill)

- T-007 rewrites 7 pre-existing test files; its `green_command` includes all of them plus
  `tests/unit/test_settings_test_isolation.py` (the helpers' isolation contract), so the break is
  repaired in-task and never deferred to Phase 5.
- T-006 changes the composition root's mechanism; its `green_command` includes
  `tests/acceptance/settings_coverage/test_wiring.py`.
- No public API is removed (NFR-001 additive-only), so no other task breaks existing tests.

### Narrowed gates

The repository-wide ruff sweep is narrowed to T-008, and each feature task's gate exercises only its
own module's lazy path; the paths a narrowed gate does not exercise are covered by the tasks that do
(T-009 semantics across all five, T-010 the locks across all five, T-011 the tracing across all
five), and Phase 5's full gate set covers the remainder.

### Test layout the DAG produces

22 distinct test files, of which 12 are new: `tests/{acceptance,unit,property,contract,integration}/
singleton_install/` (6 new packages, 7 new files), `tests/unit/architecture/` (new package,
`test_singleton_slots.py`), and three new files inside existing packages —
`tests/acceptance/permissions/test_singleton_install.py`,
`tests/acceptance/search/test_singleton_install.py`, `tests/unit/sessionmanagement/test_validation.py`
(that directory currently holds only `__init__.py` and `conftest.py`). The remaining 10 are existing
per-feature files extended with `test_ac_*` / `test_edge_*` / `test_inv_*` functions named by the
amended specs' test-strategy sections.

### Findings recorded (not silently resolved)

- **F-1 — D13 vs AC-019 (AGENTS.md).** D13/REQ-015 assume AGENTS.md already has a “Using the …”
  section for each of the five features. Measured on this branch (2026-10-07): it has eight such
  sections and **none** for the permissions or the session-management feature. AC-019 is normative and
  names five sections, so T-012 adds the two missing sections in the existing house form — the
  requirement wins over the design note. Recorded in the DAG (`open_findings`) and here rather than
  raised as a late question: both readings deliver the same guidance, the difference is two short
  sections, and the user can reject it at the change PR (S6.4) without blocking Phase 3.
- **F-2 — interlock with `crosscut/structlog-logging`.** That change (PR #74 open, not yet merged)
  edits `tests/contract/logging/test_logging_contracts.py`,
  `tests/property/logging/test_logging_properties.py` and `tests/unit/logging/test_logging_edges.py`
  — three of T-007's files — and `tests/acceptance/logging_coverage/*`, which T-011 extends.
  Whichever branch merges second rebases and keeps both edits; neither may overwrite the other's test
  content. Recorded in the DAG under `interlock`.

### S2.2 gate evidence

- Worktree (printed with the counts, per P-57): `git rev-parse --show-toplevel` →
  `C:/workspace/active-projects/python-template_kopie-worktrees/crosscut/settings-public-registry-setter`;
  branch `crosscut/settings-public-registry-setter`.
- Branch state after this step's commit: `git log --oneline origin/main..HEAD` → `aeda963` (S2.1
  ADRs) + the **S2.2 commit** (this step, the branch tip — its sha is in the S2.2 handoff, not
  repeated here because amending this record would change it), i.e.
  `git rev-list --left-right --count origin/main...HEAD`
  → **7 behind / 2 ahead**. The spec-approval merge `a1a15db` (PR #73) is an ancestor of
  `origin/main` (`git merge-base --is-ancestor a1a15db origin/main` → true), and the branch carries
  the approved spec because its P.4/P.5 commits are ancestors of that merge. The cached approval
  result is unchanged. The behind-count is reported for the orchestrator (a rebase before the change
  PR is its decision, not this step's). Nothing was pushed.
- Files created: `docs/tasks/settings-public-registry-setter.tasks.json`,
  `.github/task-runner/tasks.json`. File modified: this record only.
- Untouched by this step: `src/`, `tests/`, `pyproject.toml`, `AGENTS.md`, `docs/specs/`,
  `docs/decisions/`, `docs/todo/`, `docs/questions/`, `.github/workflows/`.
- Ruff: `uv run ruff check .` → **All checks passed** (exit 0); no Python file was written by this
  step. Passing the JSON paths explicitly makes ruff parse them as Python and report `B018` at 1:1 —
  the identical report appears for the pre-existing `docs/tasks/search.tasks.json`, and the CI sweep
  (`lint.yml:37`) does not lint JSON. Recorded so a later step does not “fix” a non-issue.
- Validator: PASSED for both invocations (output above). ID coverage: 53/53, 0 unassigned.
  Byte-identity: `cmp` clean, sha256 `abdc38ef…e255` for both files.
- Not done in this step (by instruction): no test or implementation code, no full test suite run, no
  write to `docs/todo/` or `docs/questions/`, no subagent, no push, no todo-list change.

**Next step: S3.1** — derive tests per DAG task (one fresh subagent per task's `tests_to_create`),
then S3.2 (ruff on the changed paths + confirm RED, targeted).

---

## S3.1 — T-001 test derivation (2026-10-07)

One fresh subagent, one atomic step: derive **T-001**'s tests (group `settings`,
`requirements` REQ-001 + REQ-026, `acceptance_criteria` AC-001, `amended_spec_ids`
`settings.md` v5 AC-040, AC-041, AC-042, AC-043, INV-011, EDGE-030, EDGE-031, EDGE-032,
EDGE-033). Tests only — no `src/` file was touched (`git status --porcelain` shows three
modified test files and two new test paths, nothing else). The task object was read from
`.github/task-runner/tasks.json`; its seven `tests_to_create` entries expand to **ten**
`path::test_name` nodes (the last entry packs four), and all ten node IDs were written
**exactly** as the DAG spells them.

### Tests written (ten nodes, verbatim from `tests_to_create`)

| Test node | Category | Witnesses |
|---|---|---|
| `tests/acceptance/singleton_install/test_install.py::test_ac_001_install_then_get_returns_instance` | acceptance | AC-001 (REQ-001) |
| `tests/acceptance/settings/test_settings.py::test_ac_040_set_settings_registry_installs_default` | acceptance | `settings.md` v5 AC-040 (REQ-026) |
| `tests/acceptance/settings/test_settings.py::test_ac_041_replace_logs_one_warning` | acceptance | AC-041 (+ REQ-002 WARNING rule) |
| `tests/acceptance/settings/test_settings.py::test_ac_042_concurrent_install_and_read` | acceptance | AC-042 (+ INV-011/REQ-003 lock) |
| `tests/acceptance/settings/test_settings.py::test_ac_043_install_then_reset_then_default` | acceptance | AC-043 |
| `tests/property/settings/test_settings_properties.py::test_inv_011_last_install_wins` | property (hypothesis) | INV-011 |
| `tests/unit/settings/test_settings_edges.py::test_edge_030_install_over_nonempty_default` | unit | EDGE-030 |
| `tests/unit/settings/test_settings_edges.py::test_edge_031_install_then_reset_creates_default` | unit | EDGE-031 |
| `tests/unit/settings/test_settings_edges.py::test_edge_032_required_false_after_install` | unit | EDGE-032 |
| `tests/unit/settings/test_settings_edges.py::test_edge_033_concurrent_lazy_create` | unit | EDGE-033 |

New files: `tests/acceptance/singleton_install/__init__.py` (empty, like every other
`tests/` package) and `tests/singleton_install_test_helpers.py`.

### Shared helper: `tests/singleton_install_test_helpers.py`

- `SingletonSlot` — a `NamedTuple` with exactly the five DAG fields (`module`, `installer`,
  `getter`, `reset`, `factory`). `installer` / `getter` / `reset` are **attribute-name
  strings** resolved by `getattr` at call time, never imported. That is what makes the RED
  signal correct: a feature whose install operation does not exist yet fails **inside** the
  test body with `AttributeError: module 'backend.settings' has no attribute
  'set_settings_registry'`, instead of a module-level import that would turn into a
  **collection error** and take the ~60 pre-existing tests in
  `tests/acceptance/settings/test_settings.py` down with it.
- `SLOTS` — the table the parametrized witnesses run over. T-001 can only contribute the
  settings entry (the other four install operations do not exist), so `SLOTS ==
  (SETTINGS_SLOT,)`; **T-002..T-005 append their own entry here and change none of T-001's
  tests** (the DAG's `design_constraints` requirement).
- `widened_lazy_create_window(monkeypatch, cls)` — holds the creating thread inside
  `cls.__init__` (after the instance is built, before the slot write) and records every
  instance built. Needed because the unguarded lazy window is microseconds wide under the
  GIL: a plain two-thread lazy-create test **passes before the module lock exists**, so it
  would not be RED at all.
- `non_tracing_warnings(records)` — WARNING records that are not the tracing decorator's
  own (`>>`, `<<`, `!!` prefixes). See finding F-4.
- Isolation: the settings factory builds
  `SettingsRegistry(value_repository=YamlValueRepository(tempfile.mkdtemp(...)))`, so no
  value is ever written to the shared default `settings/` directory, and every test that
  touches the shared slot saves it with `get_settings_registry(required=False)` and restores
  it in a `finally` with `restore_singleton(saved)` — the house pattern of
  `test_ac_018_singleton`. `tests/settings_test_helpers.py` was **read, not changed**
  (its private-slot writes belong to T-007); the new tests deliberately do **not** use
  `install_isolated_registry` / `isolated_registry`, which write
  `backend.settings.registry._registry[0]` directly — the exact pattern this change bans.

### Collection and RED evidence

Worktree for every count below (`git rev-parse --show-toplevel`):
`C:/workspace/active-projects/python-template_kopie-worktrees/crosscut/settings-public-registry-setter`.

- Collection (not a RED signal if it breaks): `uv run pytest --collect-only -q
  tests/acceptance/singleton_install tests/acceptance/settings tests/property/settings
  tests/unit/settings` → **91 tests collected in 1.13s**, zero collection errors — all ten
  new nodes collect as tests.
- The task's `red_command` run **verbatim** (ten node IDs, targeted — the full suite is a
  Phase 5 gate): **10 failed in 1.09s**. Failure reason per test:
  - `test_ac_001…`, `test_ac_040…`, `test_ac_041…`, `test_ac_043…`, `test_inv_011…`
    (shrunk by hypothesis to `ops=['install']`), `test_edge_030…`, `test_edge_031…`,
    `test_edge_032…` — all eight:
    `AttributeError: module 'backend.settings' has no attribute 'set_settings_registry'`
    → the install operation the task adds does not exist. Correct reason.
  - `test_edge_033_concurrent_lazy_create` — `assert 2 == 1` where `2 =
    len(window.instances)`: the two racing readers each built a `SettingsRegistry`. The
    unguarded lazy path, witnessed deterministically. Correct reason.
  - `test_ac_042_concurrent_install_and_read` — `assert 8 == 1`: eight concurrent readers
    built eight instances. Its install/read half is only reached once the lazy-create half
    is GREEN (see F-3). Correct reason.
  - No collection, setup, fixture or import error; no `ValidationError`/`ValueError` from
    test data; no Hypothesis strategy generating out-of-domain input (the strategy draws
    operation names only).
- Determinism + no state leak: the four touched files re-run twice
  (`uv run pytest tests/acceptance/singleton_install tests/acceptance/settings/test_settings.py
  tests/unit/settings/test_settings_edges.py tests/property/settings/test_settings_properties.py
  -q -p no:randomly`) → **`10 failed, 78 passed`** both times. Exactly the ten new tests
  fail; every pre-existing test in those files still passes, so the new tests leave the
  shared settings singleton as they found it.

### Quality gates (per-step scope)

- Ruff gate on the six changed paths: `uv run ruff check <paths>` → **All checks passed**;
  `uv run ruff format --diff <paths>` → **6 files already formatted**. The whole-repo sweep
  (`ruff check .` / `ruff format --check .`) is the Phase 5 gate and was not run here.
- `uv run python scripts/check_traceability.py` → **PASS (796 matrix rows, 136 spec IDs,
  724 test functions)** — still green.
- `uv run python scripts/verify_spec.py docs/specs/settings.md` → **Traceability: PASS**,
  including `✓ INV-011 has property test` (the property witness now exists).
- `uv run complexipy src tests --max-complexity-allowed 15` → **All functions are within the
  allowed complexity** (the new test functions included).
- `uv run mypy src/` → **Success: no issues found in 83 source files** (no `src/` file was
  changed by this step).

### Findings

- **F-3 — AC-042/EDGE-033 witness the unguarded lazy path first.** Both race tests fail on
  the *lazy-create* half (8 instances / 2 instances), not on the install half, because the
  lazy half is asserted first and is the half that is observably broken today. T-001's
  implementation must make the lazy half pass **and** keep the install/read half meaningful;
  the reviewer should read the AC-042 test as two halves, not one.
- **F-4 — the WARNING count must exclude tracing records.** `@logged(slow_threshold_ms=5)`
  escalates the *exit* record to WARNING, and that record
  (`<< set_settings_registry returned in X ms`) contains the substring `registry`, so a
  "WARNING records mentioning registry" count would over-count AC-041/EDGE-030. The helper
  filters on the `>>` / `<<` / `!!` prefixes instead, and asserts **exactly one** non-tracing
  WARNING.
- **F-5 — traceability Test cells are left to S5.3.** AGENTS.md Phase 3 item 8 says update
  the matrix with test references, but the rows for these IDs were written at P.4 as
  `PENDING` with `—` Test cells, the DAG assigns the traceability update to **S5.3**, and
  this step's brief scoped the commit to the test files plus this record. The rows are
  unchanged here; the Phase 3 gate only requires `check_traceability.py` to stay green, which
  it does. Flagged so the orchestrator can confirm S5.3 fills the cells for AC-001, AC-040
  .. AC-043, INV-011 and EDGE-030 .. EDGE-033.
- No new question for the user: nothing in the spec left a decision open, and the AC-010 vs
  `settings.md` AC-042 concurrency-coverage divergence already recorded at S2.2 is unchanged
  (this step witnesses `settings.md` AC-042 as written).

### Not done in this step (by instruction)

No `src/` change, no other DAG task's tests, no full test-suite run, no write to
`docs/todo/` or `docs/questions/`, no push, no todo-list change, no subagent, no background
work. **The Phase 3 RED gate is not declared here** — S3.2 owns it for all tasks; this
section records T-001's derivation and its targeted run only.

**Next step: S3.1 (T-002)** — derive the `eventbus` task's tests; T-002 appends its entry to
`SLOTS` in `tests/singleton_install_test_helpers.py` and must not edit T-001's tests.

## S3.1 — T-002 test derivation (2026-10-07)

One fresh subagent, one atomic step: derive **T-002**'s tests (group `eventbus`,
`requirements` REQ-001 .. REQ-009 + REQ-010 + REQ-014, `amended_spec_ids`
`event-bus.md` v2 REQ-008, AC-013, AC-014, AC-015, AC-016, EDGE-011, EDGE-012).
Tests only — no `src/` file was touched (`git status --porcelain` shows three modified
test files and nothing else). The task object was read from
`.github/task-runner/tasks.json` (sha256 `abdc38ef…43e255`, identical to
`docs/tasks/settings-public-registry-setter.tasks.json`); its two `tests_to_create`
entries expand to **six** `path::test_name` nodes (the first entry packs four), and all
six node IDs were written **exactly** as the DAG spells them. T-001's ten tests were not
edited.

### Tests written (six nodes, verbatim from `tests_to_create`)

| Test node | Category | Witnesses |
|---|---|---|
| `tests/acceptance/eventbus/test_eventbus.py::test_ac_013_set_event_bus_installs_default` | acceptance | `event-bus.md` v2 AC-013 (REQ-008; change REQ-001) |
| `tests/acceptance/eventbus/test_eventbus.py::test_ac_014_replace_logs_one_warning` | acceptance | AC-014 (+ REQ-002 WARNING rule, INV-002 for this feature) |
| `tests/acceptance/eventbus/test_eventbus.py::test_ac_015_concurrent_install_read_reset` | acceptance | AC-015 (+ REQ-006 module lock, EDGE-010) |
| `tests/acceptance/eventbus/test_eventbus.py::test_ac_016_install_then_reset_then_default` | acceptance | AC-016 (change REQ-008 pair; event-bus REQ-005 reset unchanged) |
| `tests/unit/eventbus/test_eventbus_edges.py::test_edge_011_replaced_bus_not_shut_down` | unit | EDGE-011 (change REQ-003 / D14 lifecycle neutrality) |
| `tests/unit/eventbus/test_eventbus_edges.py::test_edge_012_concurrent_lazy_create` | unit | EDGE-012 (change REQ-006/REQ-007 guarded lazy create) |

No new test package or `__init__.py` was needed — both target files already exist and
already carry the feature's AC-001 .. AC-012 / EDGE-001 .. EDGE-010 witnesses.

### Shared helper: `tests/singleton_install_test_helpers.py` (T-002's append)

- **`EVENTBUS_SLOT`** appended to `SLOTS` (`module=backend.eventbus`,
  `installer="set_event_bus"`, `getter="get_event_bus"`, `reset="reset_event_bus"`,
  `factory=EventBus`), so `SLOTS == (SETTINGS_SLOT, EVENTBUS_SLOT)`. T-001's tests use
  `SETTINGS_SLOT` directly, so appending changes nothing in them (verified below). The
  trio is still resolved by `getattr` at call time, which is what keeps the RED signal
  in the test body instead of in a module-level import.
- **`concurrent_reads(slot, count, args=(), timeout=5.0)`** — new: `slot.read(*args)`
  from `count` threads released by one `threading.Barrier`, with every thread's exception
  collected and asserted empty. Needed by two of this task's nodes (AC-015's 8-reader
  half, EDGE-012's 2-reader case) and reusable unchanged by T-003/T-004/T-005
  (`user-roles-permissions.md` AC-043, `search.md` AC-040, `session-management.md`
  AC-048 — the last one passes its `repository` through `args`).
- `widened_lazy_create_window` and `non_tracing_warnings` are **reused as T-001 wrote
  them** — the eventbus lazy window is exactly the settings one (the unguarded window is
  microseconds wide under the GIL, so without it EDGE-012/AC-015 would pass before the
  lock exists and would not be RED at all).
- Isolation: every new test runs inside `isolated_event_bus()` (the existing
  park/restore helper in `tests/eventbus_test_helpers.py`, **read but not changed** — its
  two private-slot writes are T-007's), so the suite's live shared bus is parked, the
  block works on a scratch instance, and the scratch is shut down and the parked bus put
  back on exit. Buses the tests build are shut down in a `finally`. `reset_event_bus()`
  is only ever called inside that park, never on the live shared instance.

### Collection and RED evidence

Worktree for every count below (`git rev-parse --show-toplevel`):
`C:/workspace/active-projects/python-template_kopie-worktrees/crosscut/settings-public-registry-setter`.

- Collection (not a RED signal if it breaks): `uv run pytest --collect-only -q
  tests/acceptance/eventbus tests/unit/eventbus` → **28 tests collected in 0.18s**, zero
  collection errors; across all touched + T-001 files
  (`tests/acceptance/eventbus tests/unit/eventbus tests/acceptance/singleton_install
  tests/acceptance/settings tests/property/settings tests/unit/settings`) → **119 tests
  collected in 0.33s**, zero collection errors. All six new nodes collect as tests.
- The task's `red_command` run **verbatim** (six node IDs, targeted — the full suite is a
  Phase 5 gate): **6 failed in 0.50s**. Failure reason per test:
  - `test_ac_013…`, `test_ac_014…`, `test_ac_016…`, `test_edge_011…` — all four:
    `AttributeError: module 'backend.eventbus' has no attribute 'set_event_bus'`
    (raised inside the test body via `SingletonSlot.install`) → the install operation the
    task adds does not exist. Correct reason.
  - `test_ac_015_concurrent_install_read_reset` — `AssertionError: lazy create race built
    8 buses` (`len(window.instances) == 1`): eight concurrent readers built eight buses on
    the unguarded lazy path. Correct reason.
  - `test_edge_012_concurrent_lazy_create` — `AssertionError: lazy create race built
    2 buses`: the two-thread form of the same missing lock. Correct reason.
  - No collection, setup, fixture or import error; no `ValidationError`/`ValueError` from
    test data (the events are the suite's own `UserCreated`/`OrderPlaced` helpers); no
    Hypothesis strategy involved (T-002 has no `INV` ID — the change spec's INV-001 ..
    INV-003 property witnesses belong to T-009).
- T-001's ten nodes re-run unchanged after the `SLOTS` append: **10 failed in 0.67s**,
  same reasons as recorded at T-001 (eight `AttributeError … set_settings_registry`,
  `assert 8 == 1` in AC-042, `assert 2 == 1` in EDGE-033). Nothing of T-001 broke.
- Determinism + no state leak: the two touched files re-run twice
  (`uv run pytest tests/acceptance/eventbus tests/unit/eventbus -q -p no:randomly`) →
  **`6 failed, 22 passed`** both times (3.01s / 3.03s). Exactly the six new tests fail;
  all 22 pre-existing eventbus tests still pass, so the new tests leave the shared bus and
  its subscribers as they found them.
- Neighbouring eventbus suites smoke-checked (they share `isolated_event_bus` and the
  helper module): `uv run pytest tests/contract/eventbus tests/integration/eventbus
  tests/property/eventbus -q` → **9 passed**; `uv run pytest
  tests/acceptance/settings_coverage tests/contract/logging -q` → **12 passed**.

### Quality gates (per-step scope)

- Ruff gate on the three changed paths: `uv run ruff check <paths>` → **All checks
  passed**; `uv run ruff format <paths>` → **3 files left unchanged**. The whole-repo
  sweep (`ruff check .` / `ruff format --check .`) is the Phase 5 gate and was not run.
- `uv run python scripts/check_traceability.py` → **PASS (796 matrix rows, 136 spec IDs,
  730 test functions)** — still green; the test-function count rose from 724 (T-001) to
  730, i.e. the six new functions are seen by the script.
- `uv run python scripts/verify_spec.py docs/specs/event-bus.md` → **Traceability: PASS**,
  including `✓ AC-013/AC-014/AC-015/AC-016 have executable test` (the four witnesses now
  exist).
- `uv run complexipy src tests --max-complexity-allowed 15` → **All functions are within
  the allowed complexity** (the new test functions and the new helper included).
- `uv run mypy src/` → **Success: no issues found in 83 source files** (no `src/` file was
  changed by this step).

### Findings

- **F-6 — the AC-014 WARNING assertion is wording-agnostic.** `event-bus.md` AC-014 and
  the change spec §9 require the WARNING to *name the feature's shared default* but fix no
  exact message (the §9 example is `settings: shared default registry replaced`, and the
  eventbus module's house prefix is `event bus: …`). The test therefore asserts
  **exactly one** non-tracing WARNING **and** `"bus" in str(record).lower()` — strong
  enough to fail a record that does not name the shared default, loose enough that T-002
  is not forced into one phrasing. The tracing records (`>>` / `<<` / `!!`) are excluded by
  `non_tracing_warnings` (F-4 still applies: `set_event_bus`'s own exit record contains
  `bus`).
- **F-7 — AC-015 witnesses the lazy-create half first** (same shape as F-3): the test
  fails on `len(window.instances) == 1` before it reaches the install/read/reset half,
  because the lazy half is the half that is observably broken today. T-002's implementation
  must make the lazy half pass **and** keep the install/read/reset half meaningful — the
  reviewer should read AC-015 as two halves. The reset threads in the second half do shut
  buses down (`reset_event_bus()` keeps that semantics, event-bus REQ-005); the assertion
  is that every read still yields a whole `EventBus` and no thread raises, which a shut-down
  bus satisfies.
- **F-8 — EDGE-011 installs over the parked scratch bus, not over a reset slot.** Inside
  `isolated_event_bus()` the slot already holds the scratch instance, so the test's first
  `install(replaced)` replaces it (one WARNING, deliberately not asserted there) and the
  second install is the EDGE-011 replace. That is the helper's own parking pattern and it
  additionally exercises D14: the scratch bus is left alive for the helper's `finally` to
  shut down, exactly as `tests/eventbus_test_helpers.py:76-82` assumes.
- **F-9 — traceability Test cells still left to S5.3** (unchanged from F-5): the rows for
  `REQ-008 (event-bus.md v2) | AC-013..AC-016` and `EDGE-011, EDGE-012 (event-bus.md v2)`
  exist in `docs/verification/traceability.md` as `PENDING` with `—` Test cells (written at
  P.4); the DAG assigns the matrix fill to S5.3 and this step's commit is scoped to the
  test files plus this record. `check_traceability.py` stays green either way. Flagged so
  S5.3 fills those two rows with the six node IDs above.
- No new question for the user: nothing in `event-bus.md` v2 or the change spec left a
  decision open for these six witnesses.

### Not done in this step (by instruction)

No `src/` change, no other DAG task's tests, no full test-suite run, no write to
`docs/todo/` or `docs/questions/`, no change to `tests/eventbus_test_helpers.py` or
`tests/settings_test_helpers.py`, no push, no todo-list change, no subagent, no background
work. No `docs/workflow/PROBLEMS.md` entry: this step had no relaunch, no iteration and no
block (next free id stays **P-63**). **The Phase 3 RED gate is not declared here** — S3.2
owns it for all tasks; this section records T-002's derivation and its targeted run only.

**Next step: S3.1 (T-003)** — derive the `permissions` task's tests; T-003 appends its
entry to `SLOTS` and may reuse `concurrent_reads`, `widened_lazy_create_window` and
`non_tracing_warnings` unchanged.

## S3.1 — T-003 test derivation (2026-10-07)

One fresh subagent, one atomic step: derive **T-003**'s tests (group `permissions`,
`requirements` REQ-001 .. REQ-010 + REQ-014 + REQ-016, `amended_spec_ids`
`user-roles-permissions.md` v2 REQ-030, AC-041, AC-042, AC-043, AC-044, EDGE-027,
EDGE-028). Tests only — no `src/` file was touched (`git status --porcelain` shows two
modified test files and one new test file, nothing else). The task object was read from
`.github/task-runner/tasks.json` (sha256 `abdc38ef…43e255`, identical to
`docs/tasks/settings-public-registry-setter.tasks.json`); its two `tests_to_create` entries
expand to **six** `path::test_name` nodes (the first entry packs four), and all six node
IDs were written **exactly** as the DAG spells them. T-001's ten and T-002's six tests
were not edited.

### Tests written (six nodes, verbatim from `tests_to_create`)

| Test node | Category | Witnesses |
|---|---|---|
| `tests/acceptance/permissions/test_singleton_install.py::test_ac_041_set_permission_service_installs_default` | acceptance | `user-roles-permissions.md` v2 AC-041 (REQ-030; change REQ-001) |
| `tests/acceptance/permissions/test_singleton_install.py::test_ac_042_replace_logs_one_warning` | acceptance | AC-042 (+ REQ-002 WARNING rule, change INV-002 for this feature) |
| `tests/acceptance/permissions/test_singleton_install.py::test_ac_043_concurrent_install_read_reset` | acceptance | AC-043 (+ change REQ-006 module lock, change AC-009) |
| `tests/acceptance/permissions/test_singleton_install.py::test_ac_044_install_then_reset_then_default` | acceptance | AC-044 (change REQ-008 reset pair) |
| `tests/unit/permissions/test_edge_cases.py::test_install_over_nonempty_default` | unit | EDGE-027 (change REQ-003 lifecycle neutrality + REQ-002 WARNING) |
| `tests/unit/permissions/test_edge_cases.py::test_concurrent_lazy_create` | unit | EDGE-028 (change REQ-006/REQ-007 guarded lazy create) |

No new test package or `__init__.py` was needed — `tests/acceptance/permissions/` already
exists and `tests/unit/permissions/test_edge_cases.py` already carries the feature's
edge-case witnesses. T-003 has no `INV`/`NFR` ID of its own, so no property or contract
file was created (the change spec's INV-001 .. INV-003 and the REQ-016 catalog witness
`test_ac_020_permission_catalog_unchanged` belong to T-009/T-010).

### Shared helper: `tests/singleton_install_test_helpers.py` (T-003's append)

- **`PERMISSIONS_SLOT`** appended to `SLOTS` (`module=backend.permissions`,
  `installer="set_permission_service"`, `getter="get_permission_service"`,
  `reset="reset_permission_service"`, `factory=_new_permission_service`), so
  `SLOTS == (SETTINGS_SLOT, EVENTBUS_SLOT, PERMISSIONS_SLOT)`. The factory builds a
  `PermissionService` over the three in-memory repositories plus a `UserManager` on
  `sqlite:///:memory:` — the construction AC-041 names ("a `PermissionService` built with
  in-memory repositories", REQ-023) — and holds no file, bus or settings state, so the
  instances are isolated. T-001's and T-002's tests use their own slot objects, so the
  append changes nothing in them (verified below).
- The trio is reached **only** through the slot object; nothing in the new tests writes
  `from backend.permissions import set_permission_service`. That is what keeps the RED
  signal inside the test body instead of a collection error that would take the 59
  pre-existing tests in the two permissions packages down with it.
- `concurrent_reads`, `widened_lazy_create_window` and `non_tracing_warnings` are reused
  unchanged, as T-002 left them. The widened window is mandatory here: the unguarded lazy
  path in `get_permission_service()` (read slot → build the SQLite-wired default → write it
  back) is microseconds wide under the GIL, so without it EDGE-028 and AC-043's first half
  would pass before the module lock exists and would not be RED at all.
- Isolation: `shared_permission_slot_reset()` in the acceptance file, and the same
  `reset_permission_service()` / `reset_permission_service()` pair inline in the two unit
  tests — public API only, no private-slot write. See F-10.

### Collection and RED evidence

Worktree for every count below (`git rev-parse --show-toplevel`):
`C:/workspace/active-projects/python-template_kopie-worktrees/crosscut/settings-public-registry-setter`.

- Collection (not a RED signal if it breaks): `uv run pytest --collect-only -q
  tests/acceptance/permissions tests/unit/permissions` → **65 tests collected in 0.44s**
  (59 before this step), zero collection errors. All six new nodes collect as tests.
- The task's `red_command` run **verbatim** (six node IDs, targeted — the full suite is a
  Phase 5 gate): **6 failed in 0.75s**. Failure reason per test:
  - `test_ac_041…`, `test_ac_042…`, `test_ac_044…`, `test_install_over_nonempty_default`
    — all four: `AttributeError: module 'backend.permissions' has no attribute
    'set_permission_service'` (raised inside the test body via `SingletonSlot.install`)
    → the install operation the task adds does not exist. Correct reason.
  - `test_ac_043_concurrent_install_read_reset` — `AssertionError: lazy create race built
    8 services` (`assert 8 == 1`): eight concurrent readers built eight services on the
    unguarded lazy path. Correct reason.
  - `test_concurrent_lazy_create` — `AssertionError: lazy create race built 2 services`
    (`assert 2 == 1`): the two-thread form of the same missing lock. Correct reason.
  - No collection, setup, fixture or import error; no `ValidationError`/`ValueError` from
    test data (services come from the slot factory over in-memory repositories; the one
    role name `editor` is in-domain for `_ROLE_NAME_PATTERN`); no Hypothesis strategy
    involved (T-003 has no `INV` ID).
- T-001's ten nodes re-run unchanged after the `SLOTS` append: **10 failed in 1.05s**;
  T-002's six nodes: **6 failed in 0.67s** — same reasons as recorded at T-001/T-002
  (eight `AttributeError … set_settings_registry`, `assert 8 == 1`, `assert 2 == 1`; four
  `AttributeError … set_event_bus`, `built 8 buses`, `built 2 buses`). Nothing of the
  earlier tasks broke.
- Determinism + no state leak: the two touched test files re-run twice
  (`uv run pytest tests/acceptance/permissions tests/unit/permissions -q -p no:randomly`)
  → **`6 failed, 59 passed`** both times (4.73s / 4.67s). Exactly the six new tests fail;
  all 59 pre-existing permissions tests still pass, so the new tests leave the shared
  permission-service slot as they found it.
- Neighbouring permissions suites smoke-checked (they share the module singleton):
  `uv run pytest tests/contract/permissions tests/integration/permissions -q` → **4
  passed**; all four permissions test directories together with random order enabled →
  **6 failed, 63 passed** — `tests/integration/permissions/test_persistence.py`, which
  reads and resets the same shared slot, is unaffected.

### Quality gates (per-step scope)

- Ruff gate on the three changed paths: `uv run ruff check <paths>` → **All checks
  passed**; `uv run ruff format <paths>` → **3 files reformatted**, after which
  `ruff check` and `ruff format --check` are both clean on those paths. The whole-repo
  sweep (`ruff check .` / `ruff format --check .`) is the Phase 5 gate and was not run.
- `uv run python scripts/check_traceability.py` → **PASS (796 matrix rows, 136 spec IDs,
  736 test functions)** — still green; the function count rose from 730 (T-002) to 736,
  i.e. the six new functions are seen by the script.
- `uv run python scripts/verify_spec.py docs/specs/user-roles-permissions.md` →
  **Traceability: PASS**, including `✓ AC-041/AC-042/AC-043/AC-044 have executable test`.
- `uv run complexipy src tests --max-complexity-allowed 15` → **All functions are within
  the allowed complexity** (the new test functions and the helper append included).
- `uv run mypy src/` → **Success: no issues found in 83 source files** (no `src/` file was
  changed by this step).

### Findings

- **F-10 — the permissions slot cannot be *saved*, so the new tests reset it before and
  after.** The hand-off pattern `get_*(required=False)` + `restore_singleton(saved)` has no
  permissions form: `get_permission_service()` takes no `required` flag, so reading the
  current instance would *construct* one, and putting a saved instance back would need the
  install operation T-003 adds — which would raise `AttributeError` in the `finally` and
  mask the real RED. `restore_singleton` in `tests/settings_test_helpers.py` is
  settings-specific (it writes `backend.settings.registry._registry[0]`, the pattern this
  change bans). The tests therefore reset the slot on entry and on exit: the slot's state
  at module import is "unset", so each block starts from the AC's "shared default is
  unset" precondition and leaves that pristine state behind, through public API only.
  T-007 (test infrastructure) can turn this into a real save/restore once all five install
  operations exist.
- **F-11 — a latent broken witness in T-002's AC-015 (reported, not fixed: out of this
  task's scope).** `tests/acceptance/eventbus/test_eventbus.py::_concurrent_install_read_reset`
  builds its install threads as `threading.Thread(target=_run, args=(EVENTBUS_SLOT.install,
  bus))` while `_run(action)` takes a single argument, so every install thread raises
  `TypeError` into `errors` and never installs. It is invisible today because AC-015 fails
  earlier at the lazy-create assert (`lazy create race built 8 buses`), but it will surface
  as a false failure once T-002 is implemented and the lazy half goes GREEN. T-003's
  equivalent threads the instance through (`_run(action, *args)` → `action(*args)`), which
  is the one-line shape T-002 needs. T-002's test file was **not** touched.
- **F-12 — AC-043 witnesses the lazy-create half first** (same shape as F-3/F-7): it fails
  on `len(window.instances) == 1` before reaching the install/read/reset half, because the
  lazy half is the half observably broken today. T-003's implementation must make the lazy
  half pass **and** keep the install/read/reset half meaningful — read AC-043 as two halves.
- **F-13 — the lazy-create witness touches the on-disk default databases, and that is the
  AC.** `get_permission_service()`'s lazy path wires the SQLite repositories at
  `DEFAULT_DATABASE_URL` / `DEFAULT_USER_DATABASE_URL`, so the concurrent readers each open
  `./data/permissions.db` and `./data/usermanagement/users.db` (gitignored, already created
  by `tests/integration/permissions/test_persistence.py`). Observed: no SQLite locking
  error and no measurable slowdown (the engines set a 30 s busy timeout,
  `src/backend/permissions/repositories.py:61`), so no single-threaded table warm-up was
  added — the race being witnessed is the slot write, not the DDL.
- **F-14 — traceability Test cells still left to S5.3** (unchanged from F-5/F-9): the rows
  for `REQ-030 (user-roles-permissions.md v2) | AC-041 .. AC-044` and
  `EDGE-027, EDGE-028 (user-roles-permissions.md v2)` exist in
  `docs/verification/traceability.md` as `PENDING` with `—` Test cells (written at P.4);
  the DAG assigns the matrix fill to S5.3 and this step's commit is scoped to the test
  files plus this record. `check_traceability.py` stays green either way. Flagged so S5.3
  fills those rows with the six node IDs above.
- No new question for the user: nothing in `user-roles-permissions.md` v2 or the change
  spec left a decision open for these six witnesses. The AC-010 vs `settings.md` AC-042
  concurrency-coverage divergence recorded at S2.2 is unaffected — this task's AC-043
  covers install + read + **reset**, as the stronger change-spec rule requires.

### Not done in this step (by instruction)

No `src/` change, no other DAG task's tests, no full test-suite run, no write to
`docs/todo/` or `docs/questions/`, no change to `tests/eventbus_test_helpers.py`,
`tests/settings_test_helpers.py` or T-001's/T-002's tests (F-11 reported, not fixed), no
push, no todo-list change, no subagent, no background work. No `docs/workflow/PROBLEMS.md`
entry: this step had no relaunch, no iteration and no block (next free id stays **P-63**).
**The Phase 3 RED gate is not declared here** — S3.2 owns it for all tasks; this section
records T-003's derivation and its targeted run only.

**Next step: S3.1 (T-004)** — derive the `search` task's tests; T-004 appends its entry to
`SLOTS` and may reuse `concurrent_reads` and `non_tracing_warnings` unchanged, but its
lazy-create witness differs: `src/backend/search/service.py:547` already has a
module-level `_singleton_lock` and `get_search_service()` / `reset_search_service()` take
it today, so search's lazy path is **already** closed — `test_edge_023_concurrent_install_and_lazy_create`
must be RED for the missing `set_search_service`, not for a create race, and
`widened_lazy_create_window` must not be used to force a failure the existing lock
prevents. `get_search_service()` also takes optional `event_bus` / `settings_registry` /
`permission_service` arguments, so the slot read may need `concurrent_reads(..., args=...)`.

## S3.1 — T-004 test derivation (2026-10-07)

One fresh subagent, one atomic step: derive **T-004**'s tests (group `search`,
`requirements` REQ-001 .. REQ-010 + REQ-014, `amended_spec_ids` `search.md` v4 REQ-024,
AC-038, AC-039, AC-040, AC-041, EDGE-022, EDGE-023). Tests only — no `src/` file was
touched (`git status --porcelain` shows two modified test files, one new test file and
this record, nothing else). The task object was read from `.github/task-runner/tasks.json`
(identical to `docs/tasks/settings-public-registry-setter.tasks.json`); its two
`tests_to_create` entries expand to **six** `path::test_name` nodes (the first entry packs
four), and all six node IDs were written **exactly** as the DAG spells them. T-001's ten,
T-002's six and T-003's six tests were not edited.

Every ID below is read together with its spec file: `search.md` v4 **AC-038 .. AC-041**
collide numerically with `settings.md` v5 AC-040 .. AC-043 and
`user-roles-permissions.md` v2 AC-041 .. AC-044 (P-53).

### Tests written (six nodes, verbatim from `tests_to_create`)

| Test node | Category | Witnesses |
|---|---|---|
| `tests/acceptance/search/test_singleton_install.py::test_ac_038_set_search_service_installs_default` | acceptance | `search.md` v4 AC-038 (REQ-024; change REQ-001) |
| `tests/acceptance/search/test_singleton_install.py::test_ac_039_replace_logs_one_warning` | acceptance | AC-039 (+ change REQ-002 WARNING rule) |
| `tests/acceptance/search/test_singleton_install.py::test_ac_040_concurrent_install_read_reset` | acceptance | AC-040 (+ change REQ-006/REQ-007 one module lock, change AC-009/AC-010) |
| `tests/acceptance/search/test_singleton_install.py::test_ac_041_install_then_reset_then_default` | acceptance | AC-041 (change REQ-008 reset pair, AC-012) |
| `tests/unit/search/test_search_edges.py::test_edge_022_install_over_nonempty_default` | unit | EDGE-022 (change REQ-002/REQ-003: replace + one WARNING + no lifecycle/registration side effect) |
| `tests/unit/search/test_search_edges.py::test_edge_023_concurrent_install_and_lazy_create` | unit | EDGE-023 (change REQ-006: install and lazy create serialised by the **existing** module lock) |

No new test package or `__init__.py` was needed — `tests/acceptance/search/` already exists
and `tests/unit/search/test_search_edges.py` already carries the feature's EDGE-001 ..
EDGE-021 witnesses (its docstring range was extended to EDGE-023). T-004 has no `INV`/`NFR`
ID of its own, so no property or contract file was created (the change spec's INV-001 ..
INV-003 and the cross-feature parametrized sets belong to T-009/T-010).

### Shared helper: `tests/singleton_install_test_helpers.py` (T-004's append)

- **`SEARCH_SLOT`** appended to `SLOTS` (`module=backend.search`,
  `installer="set_search_service"`, `getter="get_search_service"`,
  `reset="reset_search_service"`, `factory=_new_search_service`), so
  `SLOTS == (SETTINGS_SLOT, EVENTBUS_SLOT, PERMISSIONS_SLOT, SEARCH_SLOT)`. The factory
  builds `SearchService(settings_registry=_new_settings_registry())` — the isolated
  temp-dir registry AC-038's "a `SearchService` built with an isolated source registry"
  needs (the source registry is per-instance by construction, so a fresh instance is also
  an isolated source registry, and nothing is shared with the composition root's service
  and its three feature sources). T-001/T-002/T-003 use their own slot objects, so the
  append changes nothing in them (verified below).
- The trio is reached **only** through the slot object; nothing in the new tests writes
  `from backend.search import set_search_service`. That is what keeps the RED signal
  inside the test body instead of a collection error that would take the 78 pre-existing
  tests in the three search packages down with it. `SearchService` itself **is** imported
  at module level (it exists today) — only the not-yet-existing installer is resolved by
  name at call time.
- `get_search_service()`'s three parameters (`event_bus`, `settings_registry`,
  `permission_service`) are all optional, so the hand-off caveat about
  `concurrent_reads(..., args=...)` does **not** apply to search: `args=()` is correct and
  the lazily created default reads the shared registry through
  `get_settings_registry(required=False)` (`src/backend/search/service.py:453-457`), so it
  creates no registry and writes no `settings/values.yaml`.
- `concurrent_reads`, `widened_lazy_create_window` and `non_tracing_warnings` are reused
  unchanged, as T-003 left them.
- Isolation: `shared_search_slot_reset()` in the acceptance file, and the
  `reset_search_service()` / `reset_search_service()` pair inline in the two unit tests —
  public API only, no private-slot write (ADR-084's ban on touching
  `backend.search.service._singleton` from tests). See F-18.

### Search is **not** symmetric: the lazy path is already closed

`src/backend/search/service.py` already holds a module-level `_singleton_lock`, and both
`get_search_service()` and `reset_search_service()` take it today. So, unlike T-001/T-002/
T-003, search's lazy-create half is **GREEN before the implementation**:

- `test_ac_040`'s first half (8 barrier-released readers + a widened create window) passes
  today — `len(window.instances) == 1` holds because the creating thread holds the lock. It
  is the **regression witness** that the direct write stays inside that lock (change
  REQ-007) when the install path joins it, and the test is RED only from its second half
  (the install/read/reset phase). The assertions are ordered so the install half carries
  the RED, exactly as the T-003 hand-off note required.
- `test_edge_023` uses the widened window to make the **serialisation** observable, not to
  manufacture a create race the lock prevents. The creating thread is held inside
  `SearchService.__init__`; an install that is *not* guarded by the same lock would write
  its instance first and then lose the slot to the create's write. The discriminating
  assertion is therefore `get_search_service() is installed` plus
  `all(inst is not final for inst in window.instances)` — under one lock both possible
  orders end with the installed instance in the slot (exactly one of the two instances, per
  EDGE-023), and with a second/unshared lock the create wins and the install is lost.

### Collection and RED evidence

Worktree for every count below (`git rev-parse --show-toplevel`):
`C:/workspace/active-projects/python-template_kopie-worktrees/crosscut/settings-public-registry-setter`.

- Collection (not a RED signal if it breaks): `uv run pytest --collect-only -q
  tests/acceptance/search tests/unit/search tests/contract/search` → **84 tests collected
  in 0.41s** (78 before this step), zero collection errors. All six new nodes collect as
  tests.
- The task's `red_command` run **verbatim** (six node IDs, targeted — the full suite is a
  Phase 5 gate): **6 failed in 0.78s**. Failure reason per test:
  - `test_ac_038…`, `test_ac_039…`, `test_ac_041…`, `test_edge_022_install_over_nonempty_default`
    — all four: `AttributeError: module 'backend.search' has no attribute
    'set_search_service'. Did you mean: 'get_search_service'?` raised inside the test body
    via `SingletonSlot.install` → the install operation the task adds does not exist.
    Correct reason.
  - `test_ac_040_concurrent_install_read_reset` — the same `AttributeError`, raised at
    `tests/acceptance/search/test_singleton_install.py:109`, i.e. **after** the
    lazy-create half passed (`window.instances == 1`, all 8 readers got one service). RED
    for the missing install operation, not for a create race. Correct reason.
  - `test_edge_023_concurrent_install_and_lazy_create` — `AssertionError: install/read
    threads raised: [AttributeError("module 'backend.search' has no attribute
    'set_search_service'")]`: the install thread's missing-operation error surfaced
    through the thread collector instead of dying silently. Correct reason.
  - No collection, setup, fixture or import error; no `ValidationError`/`ValueError` from
    test data (services come from the slot factory over an isolated registry; the one
    source name `demo` is in-domain for `SOURCE_NAME_PATTERN`); no Hypothesis strategy
    involved (T-004 has no `INV` ID).
- T-001's ten nodes re-run unchanged after the `SLOTS` append: **10 failed in 0.97s**
  (eight `AttributeError … set_settings_registry`, `assert 8 == 1`, `assert 2 == 1`);
  T-002's six: **6 failed in 0.63s** (four `AttributeError … set_event_bus`, `lazy create
  race built 8 buses`, `built 2 buses`); T-003's six: **6 failed in 0.71s** (four
  `AttributeError … set_permission_service`, `built 8 services`, `built 2 services`). All
  identical to the reasons recorded at T-001/T-002/T-003 — nothing of the earlier tasks
  broke.
- Determinism + no state leak: the two touched test files re-run twice
  (`uv run pytest tests/acceptance/search tests/unit/search -q -p no:randomly`) →
  **`6 failed, 73 passed`** both times (4.10s / 4.21s). Exactly the six new tests fail; all
  73 pre-existing tests in those two packages still pass, so the new tests leave the shared
  search-service slot as they found it.
- Neighbouring search suites smoke-checked (they share the module singleton and the public
  API list): `uv run pytest tests/contract/search tests/integration/search
  tests/property/search -q` → **14 passed in 10.24s**; all five search test directories
  together with random order enabled → **6 failed, 87 passed in 14.36s** — including
  `tests/acceptance/search/test_search.py::test_ac_032_singleton_and_reset`, which resets
  the same slot, and `tests/acceptance/search/test_feature_sources.py`, whose three
  feature-source registrations are untouched.

### Quality gates (per-step scope)

- Ruff gate on the three changed paths: `uv run ruff check <paths>` → **All checks
  passed**; `uv run ruff format <paths>` → **1 file reformatted**, after which
  `ruff check` and `ruff format --check` are both clean on those paths. The whole-repo
  sweep (`ruff check .` / `ruff format --check .`) is the Phase 5 gate and was not run.
- `uv run python scripts/check_traceability.py` → **PASS (796 matrix rows, 136 spec IDs,
  742 test functions)** — still green; the function count rose from 736 (T-003) to 742,
  i.e. the six new functions are seen by the script.
- `uv run python scripts/verify_spec.py docs/specs/search.md` → **Traceability: PASS**
  (unchanged from the pre-derivation baseline — see F-20: its AC check is not evidence for
  this task).
- `uv run complexipy src tests --max-complexity-allowed 15` → **All functions are within
  the allowed complexity** (the new test functions and the helper append included).
- `uv run mypy src/` → **Success: no issues found in 83 source files** (no `src/` file was
  changed by this step).

### Findings

- **F-15 — the DAG's T-004 gate names a file that does not exist.**
  `completion_gates[2]` cites `tests/contract/search/test_search_contract.py`; the file on
  disk is `tests/contract/search/test_search_contracts.py`. Its public-API check is
  `hasattr`-based (`_EXPECTED_API`, `:189`), so adding `set_search_service` to `__all__`
  cannot break it — the regression witnesses T-004 actually needs are
  `tests/contract/search/test_search_contracts.py` and
  `tests/acceptance/search/test_feature_sources.py`, both green above. Flagged so the
  implementation step runs the real paths.
- **F-16 — two of T-004's six witnesses have a half that is already GREEN.** AC-040's
  lazy-read half and EDGE-023's create half pass today because search already had the
  module lock (unlike the other four features). The RED is carried entirely by the install
  half, as the T-003 hand-off required. Consequence for T-004's implementation: the
  discriminating assertion in `test_edge_023` is that the **installed** instance ends in the
  slot after a concurrent install + widened lazy create — an implementation that guards the
  install with a second lock, or outside the lock, fails it. That is ADR-084's one-lock rule
  witnessed from the test side, and it is why the widened window stays.
- **F-17 — the widened create window makes `get_search_service()` a slow traced call.**
  Holding `SearchService.__init__` for 50 ms pushes the `@logged(slow_threshold_ms=5)` exit
  record to WARNING (`<< get_search_service returned in 50.057 ms`), observed in the run
  output. Harmless here (neither concurrency witness takes `log_records`, and
  `non_tracing_warnings` filters the `<<` prefix anyway), but **T-009/T-010** must count
  WARNINGs through `non_tracing_warnings` whenever a parametrized witness runs a widened
  window over `SEARCH_SLOT`.
- **F-18 — the search slot cannot be *saved*, so the new tests reset it before and after**
  (same shape as F-10). `get_search_service()` has no `required=False` form, so reading the
  current instance would construct one, and putting a saved instance back would need the
  install operation T-004 adds — which would raise `AttributeError` in the `finally` and
  mask the real RED. `reset_search_service()` exists today, so the cleanup works in RED
  state. The slot's state at module import is "unset", and
  `tests/acceptance/search/test_search.py::test_ac_032_singleton_and_reset` already resets
  it, so reset-before/after is the established public-API isolation for this feature. T-007
  can turn it into a real save/restore once all five install operations exist.
- **F-19 — traceability Test cells still left to S5.3** (unchanged from F-14): the rows
  `REQ-024 (search.md v4) | AC-038 .. AC-041` and `EDGE-022, EDGE-023 (search.md v4)` exist
  in `docs/verification/traceability.md` as `PENDING` with `—` Test cells (written at P.4);
  the DAG assigns the matrix fill to S5.3 and this step's commit is scoped to the test
  files plus this record. `check_traceability.py` stays green either way. Flagged so S5.3
  fills those rows with the six node IDs above.
- **F-20 — `scripts/verify_spec.py`'s AC check is a substring match and is not evidence
  here.** `check_traceability` in that script marks an AC covered when **any** test function
  name anywhere contains the AC's digits (`ac.lower().replace("ac-", "") in f`,
  `scripts/verify_spec.py:104`), so `search.md` v4 AC-038 .. AC-041 already printed `✓`
  before this step, satisfied by `test_ac_038_delete_avatar_noop` (filemanagement),
  `test_ac_038_none_publisher_no_events_no_subscriptions` (sessionmanagement) and
  `test_ac_038_thread_safe_registration` (settings) — the P-53 ID-collision problem again.
  The evidence for T-004 is the targeted `red_command` run plus
  `scripts/check_traceability.py`, which at least fails when a matrix row cites a test
  function that no longer exists under `tests/`; the whole-suite spec-validation job is a
  Phase 5 gate.
- No new question for the user: nothing in `search.md` v4 or the change spec left a
  decision open for these six witnesses. The AC-010 vs `settings.md` AC-042
  concurrency-coverage divergence recorded at S2.2 is unaffected — this task's AC-040
  covers install + read + **reset**, as the stronger change-spec rule requires.

### Not done in this step (by instruction)

No `src/` change, no other DAG task's tests, no full test-suite run, no write to
`docs/todo/` or `docs/questions/`, no change to `tests/search_test_helpers.py` (read-only
for this task), `tests/settings_test_helpers.py`, `tests/eventbus_test_helpers.py` or
T-001's/T-002's/T-003's tests (F-11 from T-003 stays reported, unfixed), no push, no
todo-list change, no subagent, no background work. No `docs/workflow/PROBLEMS.md` entry:
this step had no relaunch, no iteration and no block (next free id stays **P-63**). **The
Phase 3 RED gate is not declared here** — S3.2 owns it for all tasks; this section records
T-004's derivation and its targeted run only.

**Next step: S3.1 (T-005)** — derive the `sessionmanagement` task's tests. T-005 appends
its entry to `SLOTS` and may reuse `concurrent_reads` and `non_tracing_warnings` unchanged.
Session-management is the **second** asymmetry (after search): `get_session_service()` with
no `repository` argument raises `ValueError` (`session-management.md` EDGE-003 / AC-042),
so there is **no lazily created default** — the install → read → reset assertions apply only
to the four features that build a default, and session-management's pair must be observed
through `get_session_service(repository)` (change REQ-008 / AC-012, `session-management.md`
AC-049). Practical consequences: its `SingletonSlot.read` needs `args=(repository,)`
(`concurrent_reads` already supports `args=`), its AC-048 concurrency witness cannot rely on
a bare lazy create, and — as for search — check whether its lazy path is already guarded
before using `widened_lazy_create_window` to force a failure.

## S3.1 — T-005 test derivation (2026-10-07)

One fresh subagent, one atomic step: derive **T-005**'s tests (group
`session-management — src/backend/sessionmanagement/service.py + the backend.sessionmanagement
public surface`, `requirements` REQ-001 .. REQ-010 + REQ-014, `amended_spec_ids`
`session-management.md` v2 REQ-023, AC-046, AC-047, AC-048, AC-049, EDGE-013, EDGE-014).
Tests only — no `src/` file was touched (`git status --porcelain` shows three modified test
files and this record, nothing else). The task object was read from
`.github/task-runner/tasks.json` (identical to `docs/tasks/settings-public-registry-setter.tasks.json`);
its two `tests_to_create` entries expand to **six** `path::test_name` nodes (the first entry
packs four), and all six node IDs were written **exactly** as the DAG spells them. T-001's ten,
T-002's six, T-003's six and T-004's six tests were not edited.

Every ID below is read together with its spec file (P-53): `session-management.md` v2
**AC-046 .. AC-049** collide numerically with `file-management.md` AC-046 .. AC-049
(`test_ac_046_avatar_variants_replaced`, `test_ac_047_event_uploaded`,
`test_ac_048_event_downloaded_deleted`, `test_ac_049_event_validation_failed`), and its
**EDGE-013 / EDGE-014** collide with `settings.md` (`test_edge_013_reset_all`,
`test_edge_014_slider_min_gt_max`), `user-management.md`, `authentication.md`,
`user-roles-permissions.md` and `search.md` — six different EDGE-013 rows already exist in
`docs/verification/traceability.md`.

### Tests written (six nodes, verbatim from `tests_to_create`)

| Test node | Category | Witnesses |
|---|---|---|
| `tests/acceptance/sessionmanagement/test_singleton.py::test_ac_046_set_session_service_installs_default` | acceptance | `session-management.md` v2 AC-046 (REQ-023; change REQ-001) |
| `tests/acceptance/sessionmanagement/test_singleton.py::test_ac_047_replace_logs_one_warning` | acceptance | AC-047 (+ change REQ-002 WARNING rule, REQ-004 no-`None`) |
| `tests/acceptance/sessionmanagement/test_singleton.py::test_ac_048_concurrent_install_read_reset` | acceptance | AC-048 (+ change REQ-006/REQ-007 one module lock, change AC-010 with a repository) |
| `tests/acceptance/sessionmanagement/test_singleton.py::test_ac_049_install_then_reset_then_default` | acceptance | AC-049 (change REQ-008 / AC-012 reset pair, observed through `get_session_service(repository)`) |
| `tests/unit/sessionmanagement/test_validation.py::test_edge_013_repository_rule_after_install_and_reset` | unit | EDGE-013 (installed → no repository needed; reset → AC-042 `ValueError` unchanged) |
| `tests/unit/sessionmanagement/test_validation.py::test_edge_014_install_over_nonempty_default` | unit | EDGE-014 (replace + exactly one WARNING + no exception + the replaced service keeps working; change REQ-002/REQ-003) |

T-005 has no `INV`/`NFR` ID of its own, so no property or contract file was created (the
change spec's INV-001 .. INV-003 and the parametrized cross-feature sets belong to
T-009/T-010; `session-management.md` NFR-003's contract witness
`test_nfr_003_public_api_contract` already exists and was smoke-run below). No new test
package or `__init__.py` was needed — `tests/acceptance/sessionmanagement/` and
`tests/unit/sessionmanagement/test_validation.py` both already exist (see F-22); the two
files' module docstrings were extended to the new ID range.

### Shared helper: `tests/singleton_install_test_helpers.py` (T-005's append)

- **`SESSIONMANAGEMENT_SLOT`** appended to `SLOTS` (`module=backend.sessionmanagement`,
  `installer="set_session_service"`, `getter="get_session_service"`,
  `reset="reset_session_service"`, `factory=_new_session_service`), so `SLOTS` now holds all
  five singleton-owning features — the table T-009/T-010 parametrise over. The factory builds
  `SessionService(SqliteSessionRepository("sqlite:///:memory:"), settings_registry=_new_settings_registry())`:
  the repository is a **required** constructor argument (EDGE-003 — there is no default
  construction to fall back on), and the isolated temp-dir settings registry keeps the
  service's live setting reads away from the shared `settings/` directory. T-001 .. T-004 use
  their own slot objects, so the append changes nothing in them (re-run counts below).
- The trio is reached **only** through the slot object; nothing in the new tests writes
  `from backend.sessionmanagement import set_session_service`. That is what keeps the RED
  signal inside the test body instead of a collection error over the 69 pre-existing
  session-management tests. `SessionService` itself **is** imported at module level in the
  helper (it exists today) — only the not-yet-existing installer is resolved by name at call
  time.
- `concurrent_reads` is reused unchanged with `args=(repository,)`, exactly as its docstring
  anticipates for this getter; `non_tracing_warnings` is reused unchanged.
  **`widened_lazy_create_window` is deliberately not used** — see the next section.
- Isolation: the acceptance file's existing autouse `_isolate_singleton` fixture
  (`reset_session_service()` before and after every test) covers the four new acceptance
  tests, and the two unit tests use the inline `reset_session_service()` / `try` / `finally`
  pair already established in that file by
  `test_ac_042_singleton_first_call_without_repository_value_error`. Public API only in both
  cases — no private-slot write (ADR-084; the slot `backend.sessionmanagement.service._session_service`
  is never touched from a test).

### Session-management is the **hard** asymmetry: there is no lazily created default

`get_session_service()` with no `repository` raises `ValueError` (`session-management.md`
EDGE-003 / AC-042, unchanged by v2), so the install → read → reset assertions of the other
four features cannot be phrased bare here:

- AC-049 / change REQ-008 / AC-012: the reset pair is observed through
  `get_session_service(repository)` — the freshly created instance is the one the repository
  argument builds, and the assertion is `fresh is not installed`.
- AC-046 / EDGE-013: the *installed* instance **is** readable with no repository argument —
  that is the whole point of REQ-023, and it is the half that is RED today.
- AC-048: the "Given the shared default holds a service" setup uses the **existing** lazy
  create with a repository (`held = get_session_service(repository)`), so the witness does
  not depend on the install operation for its own setup and its read half actually runs in
  RED state. Every concurrent read carries the repository, so a read that races a reset
  cannot fail on `ValueError` — it either returns the held instance or creates one.
- **`widened_lazy_create_window` was checked and not used** (the T-004 hand-off asked for
  exactly that check). Measured: `src/backend/sessionmanagement/service.py` has **no** module
  lock today — `get_session_service()` reads `_session_service[0]` at `:359` and writes it at
  `:364`, and `reset_session_service()` writes it at `:371`, all unguarded (the slot global is
  declared at `:344`), so a widened window would manufacture a *real* create race here, unlike
  search. But asserting "exactly one instance was constructed" is **not** what this feature's
  AC says: `session-management.md` AC-048 requires only that every read returns a whole
  instance and no thread crashes, and the change spec's AC-009 (one constructed default)
  explicitly excludes this feature — "Session-management's lazy path needs a `repository`, so
  its concurrency case is AC-010 run with a repository supplied, and
  `docs/specs/session-management.md` AC-048". With 2 reset threads in the same run, a
  one-create assertion would be illegal regardless (a reset legitimately re-opens the create
  path). The lock-guarding of this feature's lazy path is therefore witnessed by **T-009**
  (change AC-010, session-management run with a repository), not by T-005 — recorded so
  nobody "fixes" AC-048 into a create-race test.

### Collection and RED evidence

Worktree for every count below (`git rev-parse --show-toplevel`):
`C:/workspace/active-projects/python-template_kopie-worktrees/crosscut/settings-public-registry-setter`.

- Collection (not a RED signal if it breaks): `uv run pytest --collect-only -q` over all five
  `sessionmanagement` test directories → **75 tests collected in 0.35s** (69 before this
  step), zero collection errors. The two touched files collect **13** tests (7 before). All
  six new nodes collect as tests.
- The task's `red_command` run **verbatim** (six node IDs, targeted — the full suite is a
  Phase 5 gate): **6 failed in 0.58s**. Failure reason per test:
  - `test_ac_046_set_session_service_installs_default`, `test_ac_047_replace_logs_one_warning`,
    `test_ac_049_install_then_reset_then_default`,
    `test_edge_013_repository_rule_after_install_and_reset`,
    `test_edge_014_install_over_nonempty_default` — all five: `AttributeError: module
    'backend.sessionmanagement' has no attribute 'set_session_service'. Did you mean:
    'get_session_service'?` raised inside the test body via `SingletonSlot.install` → the
    install operation the task adds does not exist. Correct reason.
  - `test_ac_048_concurrent_install_read_reset` — `AssertionError: install/read/reset threads
    raised: [AttributeError("… has no attribute 'set_session_service'") × 8]` raised at
    `tests/acceptance/sessionmanagement/test_singleton.py:138`, i.e. **after** the read half
    passed (`concurrent_reads(..., args=(repository,))` returned the held service to all 8
    readers). RED for the missing install operation, not for a torn slot. Correct reason.
  - No collection, setup, fixture or import error; no `ValidationError`/`ValueError` from test
    data (the `ValueError` that does appear is the *asserted* AC-042 behaviour inside
    `pytest.raises`, not test-data construction); services come from the slot factory over an
    in-memory store and an isolated registry; no Hypothesis strategy involved (T-005 has no
    `INV` ID).
- T-001's ten / T-002's six / T-003's six / T-004's six nodes re-run after the `SLOTS` append
  (each set's own node list from the DAG): **10 failed in 0.94s** (eight `AttributeError …
  set_settings_registry`, `assert 8 == 1`, `assert 2 == 1`), **6 failed in 0.68s** (four
  `AttributeError … set_event_bus`, `lazy create race built 8 buses`, `built 2 buses`),
  **6 failed in 0.77s** (four `AttributeError … set_permission_service`, `built 8 services`,
  `built 2 services`), **6 failed in 0.78s** (five `AttributeError … set_search_service`, one
  thread-collector `AssertionError`). All identical to the reasons recorded at T-001 .. T-004
  — nothing of the earlier tasks broke.
- Determinism + no state leak: the two touched test files re-run twice
  (`uv run pytest tests/acceptance/sessionmanagement tests/unit/sessionmanagement -q -p no:randomly`)
  → **`6 failed, 53 passed`** both times (9.62s / 9.78s). The pre-derivation baseline of those
  two directories was **53 passed**, so exactly the six new tests fail and every pre-existing
  test — including `test_ac_041_singleton_created_once`, `test_ac_043_reset_session_service`
  and `test_ac_042_singleton_first_call_without_repository_value_error`, which share the same
  slot — still passes.
- Neighbouring session-management suites smoke-checked (they share the module singleton and
  the public-API list): `uv run pytest tests/contract/sessionmanagement
  tests/integration/sessionmanagement tests/property/sessionmanagement -q` → **16 passed in
  40.97s** — including `test_nfr_003_public_api_contract`; all five session-management test
  directories together with random order enabled → **6 failed, 69 passed in 50.07s**.

### Quality gates (per-step scope)

- Ruff gate on the three changed paths: `uv run ruff check <paths>` → **All checks passed**;
  `uv run ruff format <paths>` → **2 files reformatted, 1 file left unchanged**, after which
  `ruff check` and `ruff format --check` are both clean on those paths, and the `red_command`
  was re-run after formatting (**6 failed**, same reasons). The whole-repo sweep
  (`ruff check .` / `ruff format --check .`) is the Phase 5 gate and was not run.
- `uv run python scripts/check_traceability.py` → **PASS (796 matrix rows, 136 spec IDs, 748
  test functions)** — still green; the function count rose from 742 (T-004) to 748, i.e. the
  six new functions are seen by the script.
- `uv run python scripts/verify_spec.py docs/specs/session-management.md` → **Traceability:
  PASS** (unchanged from the pre-derivation baseline — see F-20/F-26: its AC check is not
  evidence for this task).
- `uv run complexipy src tests --max-complexity-allowed 15` → **All functions are within the
  allowed complexity** (the new test functions and the helper append included).
- `uv run mypy src/` → **Success: no issues found in 83 source files** (no `src/` file was
  changed by this step).

### Findings

- **F-21 — session-management's lazy path is unguarded today, and T-005 does not witness
  it.** `src/backend/sessionmanagement/service.py:359-365` reads and writes
  `_session_service[0]` with no module lock (unlike search, which already holds
  `_singleton_lock`). `widened_lazy_create_window` would therefore expose a genuine create
  race here — but no `session-management.md` v2 AC asks for one, and change AC-009 excludes
  this feature by name. The witness for "the lazy create joins the module lock" (change
  REQ-006/REQ-007) in this feature is **T-009's AC-010 run with a repository supplied**.
  Consequence for T-005's implementation: adding `_session_service_lock` must keep
  AC-041/AC-042/AC-043 exactly as they are — those three tests are the regression witnesses
  and they are green in every run above.
- **F-22 — the DAG calls `tests/unit/sessionmanagement/test_validation.py` a new file; it is
  not.** It has existed since the session-management feature's own Phase 3 (`66f4cad`) and
  already carries `test_ac_042_singleton_first_call_without_repository_value_error` plus the
  AC-003/AC-013/EDGE-008/EDGE-009 witnesses. T-005 **appended** to it (which is what
  `completion_gates[3]` assumes when it says the existing suite must stay green). Flagged so
  the implementation step never rewrites that file wholesale.
- **F-23 — the public-API contract witness is `hasattr`-based, so the re-export cannot break
  it.** `tests/contract/sessionmanagement/test_contract.py::test_nfr_003_public_api_contract`
  checks `_EXPECTED_API` (declared at `:8`, asserted in the loop at `:45`), which lists
  `get_session_service` and `reset_session_service` but not `set_session_service`; adding the
  new name to `__all__` is
  therefore additive (NFR-003, change REQ-014). It is green in the 16-passed neighbour run.
  T-009's AC-007 is the witness that the new name is actually exported.
- **F-24 — the slot factory owns its own store.** Because `SessionService` cannot be
  constructed without a repository, `SESSIONMANAGEMENT_SLOT.new()` builds a private
  `SqliteSessionRepository("sqlite:///:memory:")` per instance (`StaticPool`, so each
  repository instance really is a separate in-memory database — nothing on disk, nothing
  shared), while AC-048/AC-049's *reads* pass a `tmp_path`-backed repository. The two are
  never compared by content, only by identity and wholeness, so the mismatch is harmless; it
  is recorded because a future witness that asserted stored state would have to use one
  repository consistently.
- **F-25 — traceability Test cells still left to S5.3** (unchanged from F-14/F-19): the rows
  `REQ-023 (session-management.md v2) | AC-046, AC-047, AC-048, AC-049` and
  `EDGE-013, EDGE-014 (session-management.md v2)` exist in `docs/verification/traceability.md`
  as `PENDING` with `—` Test cells (written at P.4); the DAG assigns the matrix fill to S5.3
  and this step's commit is scoped to the test files plus this record.
  `check_traceability.py` stays green either way. Flagged so S5.3 fills those rows with the
  six node IDs above.
- **F-26 — `verify_spec.py`'s ✓ on AC-046 .. AC-049 is a false positive for this spec**
  (the F-20 rule, now with the concrete collision): its AC check is a substring match on the
  digits over **all** test functions, so `session-management.md` v2 AC-046 was already
  satisfied by `test_ac_046_avatar_variants_replaced` (file-management) and its EDGE-013 by
  `test_edge_013_reset_all` (settings) before this step existed. The evidence for T-005 is
  the targeted `red_command` run plus `scripts/check_traceability.py`.
- No new question for the user: nothing in `session-management.md` v2 or the change spec left
  a decision open for these six witnesses. The AC-010 vs `settings.md` AC-042
  concurrency-coverage divergence recorded at S2.2 is unaffected — this task's AC-048 covers
  install + read + **reset**, as the stronger change-spec rule requires.

### Not done in this step (by instruction)

No `src/` change, no other DAG task's tests, no full test-suite run, no write to
`docs/todo/` or `docs/questions/`, no change to `tests/sessionmanagement_test_helpers.py` or
`tests/unit/sessionmanagement/conftest.py` (both read-only for this task), no change to
T-001's/T-002's/T-003's/T-004's tests, no push, no todo-list change, no subagent, no
background work. No `docs/workflow/PROBLEMS.md` entry: this step had no relaunch, no
iteration and no block (next free id stays **P-63**). **The Phase 3 RED gate is not declared
here** — S3.2 owns it for all tasks; this section records T-005's derivation and its targeted
run only.

**Next step: S3.1 (T-006)** — derive the composition-root task's tests
(`tests/integration/singleton_install/test_composition_root.py`, `requirements` REQ-011 +
REQ-012, `acceptance_criteria` AC-016, `amended_spec_ids` `settings-coverage.md` REQ-002 cited
unchanged; the only `src/` file in scope is `src/main.py`). Hand-off notes from T-005:

1. `SLOTS` now holds **all five** features, so T-009/T-010 can be written against the table
   as-is; T-006 must not append a sixth entry.
2. `src/main.py` today bypasses the install operation: it imports the private slot at `:68`
   (`from backend.settings.registry import _registry as _settings_registry_singleton`) and
   writes `_settings_registry_singleton[0] = _settings_registry` at `:138`, immediately after
   building the registry at `:137` and before the six `register_*_settings` calls at `:173-178`
   (D10: position and order unchanged, only the mechanism changes; REQ-011 needs the install
   to precede those registrations). Reading the installed instance back through
   `get_settings_registry()` is safe in a test (the getter exists); reaching it through
   `set_settings_registry()` is RED-by-design until T-001's implementation lands — keep using
   the slot object (`SETTINGS_SLOT`) so the RED stays inside the test body.
3. AC-016 asks for a **fresh subprocess** that imports `main`. The house pattern is
   `tests/acceptance/settings_coverage/test_wiring.py:16-31` (build a `code` string,
   `subprocess.run([sys.executable, "-c", code], cwd=_REPO_ROOT)`) and the `_run` helper of
   `test_setup_logger.py:12-14`. Two cautions: (a) that pattern's embedded string writes
   `_reg_mod._registry[0] = ...` at `test_wiring.py:18` — one of the 11 sites **T-007**
   migrates, so T-006's new file must not plant a *new* private-slot write that its own
   AC-017 scan would later flag; (b) `src/main.py` creates `./data/*.db`, `./data/files` and
   the settings YAML relative to the cwd (`:144`, `:152`, `:181`, `:194`, `:197`), which is
   why the worktree already has `data/` and `settings/` directories — run the subprocess with
   a scratch `cwd` (e.g. `tmp_path`) instead of `_REPO_ROOT` so the witness leaves nothing in
   the repository.
4. T-006's `green_command` names two existing startup-wiring witnesses as regression guards:
   `tests/acceptance/settings_coverage/test_wiring.py` and
   `tests/acceptance/permissions/test_composition_wiring.py` (plus
   `tests/acceptance/logging_coverage/test_setup_logger.py` in its completion gates). They are
   read-only for T-006 — `test_wiring.py`'s own slot write is migrated in T-007, not here.
5. Session-management's asymmetry does not reach T-006: the composition root constructs the
   session service with an explicit repository and never relies on a lazy default — but if a
   T-006 witness reads the session singleton afterwards, it must pass a repository (EDGE-003),
   and `src/main.py` must not be made to install one just to make a read bare.

## S3.1 — T-006 test derivation (2026-10-07)

One fresh subagent, one atomic step: derive **T-006**'s tests (group
`composition root — src/main.py (write site 1 of the 12)`, `requirements` REQ-011 + REQ-012,
`acceptance_criteria` AC-016, `amended_spec_ids` `settings-coverage.md` REQ-002 cited
unchanged). Tests only — no `src/` file was touched (`git status --porcelain` shows the new
test package and this record, nothing else). The task object was read from
`.github/task-runner/tasks.json` (identical to `docs/tasks/settings-public-registry-setter.tasks.json`);
its two `tests_to_create` entries are two single-node strings, and both node IDs were written
**exactly** as the DAG spells them. T-001's ten, T-002's six, T-003's six, T-004's six and
T-005's six tests were not edited, and `tests/singleton_install_test_helpers.py` was not
touched at all: `SLOTS` already holds all five features and T-006 adds no sixth entry
(T-005 hand-off note 1).

Every ID below is read together with its spec file (P-53): **AC-016** is defined in fourteen
spec files — `event-bus.md` v2 AC-016 is this change's own sibling ID and
`settings-coverage.md` AC-016 is the `required=False` guarded read — and **REQ-011 / REQ-012**
in twelve each (`settings-coverage.md` REQ-011/REQ-012 are cited by the change spec for a
different rule). `docs/verification/traceability.md` already carries `test_ac_016_to_view`,
`test_ac_016_set_role_not_in_set`, `test_ac_016_reset_request_unknown_email`,
`test_ac_016_no_secrets_in_log_records` and `test_ac_016_storage_failure_rollback`.

### Tests written (two nodes, verbatim from `tests_to_create`)

| Test node | Category | Witnesses |
|---|---|---|
| `tests/integration/singleton_install/test_composition_root.py::test_ac_016_main_installs_through_setter` | integration | change-spec AC-016, all three clauses (REQ-011: install through `set_settings_registry()` + the getter read-back with the feature settings registered; no private-slot import; no consumer site passed the local handle) |
| `tests/integration/singleton_install/test_composition_root.py::test_installed_registry_serves_feature_registration` | integration | change-spec REQ-011's ordering/identity half as AC-016 states it — the install precedes the six registrations and the installed instance **is** the instance they register into — which is what makes `settings-coverage.md` REQ-002 (cited unchanged) literally true |

T-006 has no `INV`/`EDGE`/`NFR` ID of its own, so no property, unit or contract file was
created. The category is `integration` because the change spec's §10 test-strategy table
assigns REQ-011 and AC-016 there; `tests/integration/singleton_install/__init__.py` is a new,
empty package marker (every other test package's `__init__.py` is 0 bytes).

### How the composition root is observed

- **Fresh interpreter.** The composition root's wiring runs at module-import time, so both
  witnesses run `import main` through `subprocess.run([sys.executable, "-c", code])` — the
  established pattern of `tests/acceptance/settings_coverage/test_wiring.py:16-31` and
  `tests/acceptance/permissions/test_composition_wiring.py` (its `sys.path.insert(0, <abs src>)`
  + `cwd=tmp_path` form, not `test_wiring.py`'s `cwd=_REPO_ROOT` form).
- **Scratch cwd.** `src/main.py` creates `./data/*.db`, `./data/files` and the `settings/` YAML
  directory relative to its cwd, so `cwd=tmp_path`. Measured: two runs of the new file leave
  `data/permissions.db` and `settings/values.yaml` byte-identical (md5), while the pre-existing
  `test_wiring.py` does rewrite `data/permissions.db` — see F-27. The new file plants **no**
  private-slot write anywhere, not even inside its embedded code string (grep for
  `_registry[0]` / `_singleton[0]` / `_default_bus[0]` in it → 0 hits), as T-005's note 3 asked.
- **The install operation is looked up, never imported.** The embedded preamble does
  `_real_setter = backend.settings.set_settings_registry` and wraps the six features'
  `register_settings` attributes **before** `import main`, because main binds both at its own
  import time. That is the only way "installs through `set_settings_registry()`" is observable
  at all, and it keeps the RED signal inside the subprocess (surfaced as an assertion failure
  on `returncode`) instead of an import error at collection.
- **AC-016's two static clauses** are witnessed by module-level AST helpers over
  `src/main.py` (precedent: `tests/acceptance/logging_coverage/test_setup_logger.py`). Measured
  today: the private-import scan reports `backend.settings.registry._registry` (line 68) and the
  consumer-site scan reports lines **153, 173, 174, 175, 176, 177, 178, 195, 202, 212** — the
  four `settings_registry=` service-construction sites plus the six `register_*_settings` calls,
  exactly the ten sites AC-016 and the DAG name. Run against the implementation form the DAG
  plans (`set_settings_registry(SettingsRegistry(...))` plus `_shared_settings_registry()` at the
  sites), both scans return `[]`, so they do not false-positive on the fix.

### Sensitivity proof (the witness is RED for T-006's own change)

Run out-of-band (scratch script, not committed): the same two code strings with a temporary
`backend.settings.set_settings_registry` shim installed — i.e. T-001 simulated as landed while
T-006 has not run — exit 0 and print `[False, False, True]` (AC-016) and
`[False, True, True, True]` (registrations). So the witness is still RED when only the setter
exists, and it is RED for exactly one clause: main does not call the setter. Every other clause
(`import main` succeeds, the getter returns the wired registry, all six keys of the six features
are registered, six registrations observed) is already `True`, which rules out a broken witness.

### Collection and RED evidence

Worktree for every count below (`git rev-parse --show-toplevel`):
`C:/workspace/active-projects/python-template_kopie-worktrees/crosscut/settings-public-registry-setter`.

- Collection (not a RED signal if it breaks): `uv run pytest --collect-only -q
  tests/integration/singleton_install` → **2 tests collected in 0.12s**; over the three touched
  directories (`tests/integration/singleton_install tests/acceptance/settings_coverage
  tests/acceptance/permissions`) → **46 tests collected in 0.44s**, zero collection errors.
- The task's `red_command` run **verbatim** (two node IDs, targeted — the full suite is a
  Phase 5 gate): **2 failed in 1.48s**. Failure reason per test — both:
  `AttributeError: module 'backend.settings' has no attribute 'set_settings_registry'. Did you
  mean: 'get_settings_registry'?` raised in the subprocess preamble at
  `_real_setter = backend.settings.set_settings_registry`, surfaced by
  `assert result.returncode == 0, result.stderr` at `test_composition_root.py:193` and `:208`
  — the install operation the change adds does not exist. Correct reason (assertion failure in
  the test body, not a collection/setup error).
- Determinism + no state leak: the new file re-run twice (`-p no:randomly`, then with random
  order) → **2 failed** both times (1.54s / 1.64s); `md5sum` of `data/permissions.db` and
  `settings/values.yaml` unchanged across those runs; `git status --porcelain` → only
  `?? tests/integration/singleton_install/`.
- T-001's ten / T-002's six / T-003's six / T-004's six / T-005's six nodes re-run after this
  derivation (each set's own `red_command` node list from the DAG): **10 failed in 1.18s**,
  **6 failed in 0.84s**, **6 failed in 0.93s**, **6 failed in 0.93s**, **6 failed in 0.61s** —
  same node sets and same reasons as recorded at T-001 .. T-005 (eight `AttributeError …
  set_settings_registry` + `assert 8 == 1` + `assert 2 == 1`; four `set_event_bus` + two thread
  collectors; four `set_permission_service` + two thread collectors; five `set_search_service` +
  one thread collector; five `set_session_service` + one thread collector). Nothing of the
  earlier tasks broke.
- T-006's regression witnesses (read-only for this task) run together with the new file —
  `uv run pytest tests/integration/singleton_install tests/acceptance/settings_coverage/test_wiring.py
  tests/acceptance/permissions/test_composition_wiring.py
  tests/acceptance/logging_coverage/test_setup_logger.py -q -p no:randomly` →
  **2 failed, 3 passed in 3.46s**: the three startup-wiring witnesses
  (`test_main_wires_all_features`, `test_ac_020_composition_root_validates_session_token`,
  `test_entrypoint_calls_setup_logger_once`) stay GREEN next to the two new red tests.

### Quality gates (per-step scope)

- Ruff gate on the two changed paths: `uv run ruff check <paths>` → **All checks passed**;
  `uv run ruff format <paths>` → **2 files left unchanged**, and `ruff format --check` on those
  paths → **2 files already formatted**. No whole-repo sweep (`ruff check .` /
  `ruff format --check .` is the Phase 5 gate).
- `uv run python scripts/check_traceability.py` → **PASS (796 matrix rows, 136 spec IDs, 750
  test functions)** — still green; the function count rose from 748 (T-005) to 750, i.e. the two
  new functions are seen by the script.
- `uv run complexipy src tests --max-complexity-allowed 15` → **All functions are within the
  allowed complexity** (the two test functions and the three scan helpers included).
- `uv run mypy src/` → **Success: no issues found in 83 source files** (no `src/` file was
  changed by this step).

### Findings

- **F-27 — the pre-existing `test_wiring.py` writes into the worktree's `data/`.** Measured:
  running `tests/acceptance/settings_coverage/test_wiring.py` alone changes
  `data/permissions.db` (md5 `3f56492…` → `39236be…`) because its subprocess runs with
  `cwd=_REPO_ROOT` (`test_wiring.py:31`), while `test_composition_wiring.py` and this step's new
  file use a scratch cwd and leave nothing. T-006 may not touch that file (its `allowed_files`
  lists it as a regression witness only), and this step's file therefore never copies its
  `cwd=_REPO_ROOT` form. Flagged for **T-007**, which migrates that file's embedded slot write
  anyway and can switch the cwd in the same edit.
- **F-28 — the DAG's second node name carries no ID.**
  `test_installed_registry_serves_feature_registration` is written verbatim as
  `tests_to_create` spells it (the DAG is normative for node IDs, as at T-003's
  `test_install_over_nonempty_default`); its docstring ties it to REQ-011 / AC-016 and
  `settings-coverage.md` REQ-002, and `check_traceability.py` counts it (750 functions).
  Flagged for **S5.3**: the `REQ-011 | AC-016` matrix row (currently `—` / `PENDING`, written at
  P.4) must cite **both** nodes, and the change spec's §10 table names only the first.
- **F-29 — AC-016's static clauses live in this file, not in T-007's scanner.** AC-017
  (T-007) proves *no file writes another package's singleton slot*; the two clauses "no
  private-slot import in `src/main.py`" and "no consumer site passed the local
  `_settings_registry` handle" are AC-016/REQ-011 rules and are witnessed here. T-007 must not
  be expected to cover the handle rule, and must not be expected to make these two assertions
  redundant.
- **F-30 — the witness patches the package attribute, so the import form matters.** The
  subprocess patches `backend.settings.set_settings_registry` before `import main`; if the
  implementation imported the setter from `backend.settings.registry` instead of from
  `backend.settings`, main would bind the unpatched function and the witness would stay red for
  the wrong reason. The DAG's implementation step 1 already prescribes
  `from backend.settings import set_settings_registry` (the feature's public surface, ADR-083 /
  NFR-002), so this is a confirmation, not a new constraint.
- **F-31 — traceability Test cells still left to S5.3** (continues F-14/F-19/F-25): the rows
  `REQ-011 | AC-016` and `REQ-012 | AC-017` exist as `PENDING` with `—` Test cells; this step's
  commit is scoped to the test files plus this record, and `check_traceability.py` stays green
  either way.
- No new question for the user: nothing in the change spec, `settings-coverage.md` REQ-002 or
  ADR-083/ADR-084 left a decision open for these two witnesses.

### Not done in this step (by instruction)

No `src/` change, no other DAG task's tests, no full test-suite run, no write to
`docs/todo/` or `docs/questions/`, no change to `tests/singleton_install_test_helpers.py` or to
`tests/acceptance/settings_coverage/test_wiring.py` (read-only regression witnesses), no change
to T-001's .. T-005's tests, no push, no todo-list change, no subagent, no background work. No
`docs/workflow/PROBLEMS.md` entry: the one defect found while deriving (`{!r}` on a `Path`
inside the embedded code string, a `NameError` in the subprocess) was fixed and re-checked
inside this same execution, which is an in-step self-introduced nit per AGENTS.md, not
friction — next free id stays **P-63**. **The Phase 3 RED gate is not declared here** — S3.2
owns it for all tasks; this section records T-006's derivation and its targeted run only.

**Next step: S3.1 (T-007)** — derive the test-infrastructure + architecture-scan task
(`tests/unit/architecture/test_singleton_slots.py`, `requirements` REQ-012 + REQ-013,
`acceptance_criteria` AC-017 + AC-018, the 11 test-side foreign-slot writes). Hand-off notes
from T-006:

1. The 12 measured foreign-slot writes are unchanged by this step: `src/main.py:138` (T-006's)
   plus exactly **eleven** in tests — `tests/acceptance/settings_coverage/test_setup_logger.py:31`
   and `:55`, `tests/acceptance/settings_coverage/test_wiring.py:18` (embedded in a code string),
   `tests/contract/logging/test_logging_contracts.py:35`,
   `tests/property/logging/test_logging_properties.py:42`, `tests/unit/logging/test_logging_edges.py:32`,
   `tests/eventbus_test_helpers.py:77` and `:84`, `tests/settings_test_helpers.py:132`, `:160`
   and `:180`. Re-verified by `grep -rn "\[0\] *=" src tests` (the two other hits,
   `test_usermanagement.py:95` and `test_usermanagement_contracts.py:150`, are `[0] ==` compares,
   not writes, and must not be reported).
2. `tests/integration/singleton_install/test_composition_root.py` is **clean** under the AC-017
   rule (0 slot-write hits), but it does contain, inside its embedded code string, the text
   `backend.settings.set_settings_registry = _install` (the deliberate patch of the **public**
   operation) and the bare literal `"_settings_registry"` (the handle name its own scan looks
   for). A scanner keyed on a substring (`_settings_registry`, or `<module>.<name> = `) would
   flag this witness; AC-017's scanner must key on the slot-write **shape**
   (`_registry[0] =`, `_default_bus[0] =`, `_permission_service[0] =`, `_session_service[0] =`,
   `_singleton[0] =`, and their `_settings_registry_singleton[0] =` alias form), as ADR-084
   describes.
3. T-007's scanner must also read string-literal bodies (AC-017's third clause) — the
   `test_wiring.py:18` site is one — and it runs over `tests/` as well as `src/`; the owner-side
   writes inside the five owning modules (`src/backend/settings/registry.py:373`/`:380`,
   `eventbus/eventbus.py:221`/`:232`, `permissions/service.py:524`/`:530`,
   `search/service.py:560`/`:572`, `sessionmanagement/service.py:364`/`:371`) are **not**
   violations and must not be reported.
4. If T-007 also switches `test_wiring.py`'s `cwd=_REPO_ROOT` to a scratch cwd (F-27), the
   witness's semantics stay identical — it installs an isolated registry before `import main`
   and asserts four registered keys — and this step's two nodes are unaffected either way.
5. `SLOTS` still holds exactly the five features; T-007 must not add a sixth, and the
   parametrized sets of T-009/T-010 read that table as-is.

## S3.1 — T-007 test derivation (2026-10-07)

One fresh subagent, one atomic step: derive **T-007**'s tests (group
`test infrastructure — the 11 foreign-slot write sites + the architecture scan test`,
`requirements` REQ-012 + REQ-013 (scan half), `acceptance_criteria` AC-017, `edge_cases`
EDGE-008, `amended_spec_ids` none). Tests only — no `src/` file and no existing test file was
touched (`git status --porcelain` shows the new test package and this record, nothing else), and
the **11 test-side write sites were deliberately left in place**: the repository witness has to
be RED precisely because they are still there (T-007's `implementation_steps` migrate them in
Phase 4). The task object was read from `.github/task-runner/tasks.json` (identical to
`docs/tasks/settings-public-registry-setter.tasks.json`); its three `tests_to_create` entries are
three single-node strings and all three node IDs were written **exactly** as the DAG spells them.
T-001's ten, T-002's six, T-003's six, T-004's six, T-005's six and T-006's two tests were not
edited, and `tests/singleton_install_test_helpers.py` was not touched — the scan needs no helper
there (see "The scanner").

Every ID below is read together with its spec file (P-53): **AC-017** is defined in twelve spec
files (`settings-coverage.md` AC-017 is the settings-registry view rule, `user-management.md`
AC-017 the last-admin guard, `authentication.md` AC-017 the log-secret rule, `search.md` AC-017
the timeout rule …), **REQ-012** and **REQ-013** in thirteen each, **EDGE-008** in thirteen
(`settings.md` EDGE-008 is the LIST-kind rule, `event-bus.md` EDGE-008 the shutdown rule). The
IDs mean what `docs/specs/settings-public-registry-setter.md` says here.
`docs/verification/traceability.md` already carries `test_ac_017_status_transitions`,
`test_ac_017_delete_last_admin`, `test_ac_017_reset_token_single_use`,
`test_edge_008_handler_raises`, `test_edge_008_slider_out_of_range`,
`test_edge_008_memory_repository` and `test_edge_008_reset_expired_token` for other features —
none of them is this change's row.

### Tests written (three nodes, verbatim from `tests_to_create`)

| Test node | Category | Witnesses |
|---|---|---|
| `tests/unit/architecture/test_singleton_slots.py::test_ac_017_no_cross_package_slot_write` | unit | change-spec AC-017 / REQ-012 / REQ-013 over the **whole repository**: every `.py` under `src/` and `tests/` is AST-parsed and no file may write a slot owned by another package. Anti-vacuity guard first (below) |
| `tests/unit/architecture/test_singleton_slots.py::test_ac_017_scanner_reports_planted_violation` | unit | AC-017's "the scan fires" half — planted fixtures in `tmp_path` for all three reference forms, each reported with its path, line, slot and form; plus the negative control that the migrated form is **not** reported |
| `tests/unit/architecture/test_singleton_slots.py::test_edge_008_owner_slot_write_allowed` | unit | EDGE-008 — the owning module's own write is not reported, and the guard targets writes and imports only (a foreign **read** is legal) |

New package `tests/unit/architecture/` with `__init__.py` carrying the one-line comment
`# Architecture guards: source-scanning tests over src/ and tests/.` — the repo is mixed (42 test
`__init__.py` files are 0 bytes, 20 carry a one-line comment, `tests/unit/__init__.py` among
them); the commented form was used because the package's purpose is not self-evident from its
name. No `tests/architecture_test_helpers.py` was created: the DAG allows it, the single-file form
is preferred, and the scanner is only read by this file (F-37).

### The scanner (inside the test file — what AC-017 actually checks)

- **Owner table** (fixed, from the spec §3.1 / ADR-083): `backend.settings.registry._registry`,
  `backend.eventbus.eventbus._default_bus`, `backend.permissions.service._permission_service`,
  `backend.search.service._singleton`,
  `backend.sessionmanagement.service._session_service`.
- **Three reported forms.** `import` — an `ast.ImportFrom` of a private slot from its owning
  module (the step that makes a foreign write possible, the in-test counterpart of the `TID251`
  half); `write` — an `ast.Assign` whose target is an `ast.Subscript` rooted on a bare slot
  **Name** or on a slot **Attribute** (`_mod._registry[0] = …`, the module-alias form the DAG
  names); `embedded-write` — the same write spelled out inside an `ast.Constant` string, which is
  how six of the eleven test-side sites reach the slot (they hand code strings to a subprocess).
- **Reads are not violations.** The scanner looks only at assignment targets, so
  `tests/eventbus_test_helpers.py` parking and restoring the live bus
  (`saved = _eventbus_module._default_bus[0]`) is not reported — only its two writes are. That is
  EDGE-008's "writes and imports only" boundary.
- **Owner exemption (EDGE-008).** A file whose path ends with the owning module's path
  (`src/backend/settings/registry.py` for `_registry`, …) may write its own slot; the exemption is
  per slot, not per file, so an owner writing *another* feature's slot is still reported.
- **The string-literal half is a regex, assembled from the owner table at import time**
  (`(?:<dotted prefix>?)?_registry\s*\[\s*0\s*\]\s*=`), not a literal pattern in this file — see
  F-36 for why that matters, and ADR-084 for the accepted heuristic cost (a comment or docstring
  that spells the write out is reported).
- **Scope**: `pathlib.Path("src").rglob("*.py")` + `Path("tests").rglob("*.py")`, CWD-relative
  like `tests/acceptance/logging_coverage/test_new_classes_traced.py`. Measured scope: **83 files
  under `src/`, 241 under `tests/`, 324 total**, scanned in ~0.6 s.
- **Anti-vacuity guard.** `test_ac_017_no_cross_package_slot_write` first asserts that each of the
  five owning modules' `src/` path is inside the scanned file set, so a wrong CWD cannot turn the
  repository scan into a pass.
- **`ponytail:` ceiling, recorded in the `_scan_file` docstring.** No import-binding resolution: a
  write through an import alias is caught by the **import** half, not by the write half — measured
  on `src/main.py`, where the aliased import at line 68 is reported and the write through that
  alias at line 138 is not — and a write built through `getattr` is not caught at all. The file is
  reported either way, which is what AC-017 asks. Upgrade path: a per-file `asname → slot` map.

### RED evidence (`red_command`, verbatim)

Worktree for every count below (`git rev-parse --show-toplevel`):
`C:/workspace/active-projects/python-template_kopie-worktrees/crosscut/settings-public-registry-setter`.

- `uv run pytest tests/unit/architecture/test_singleton_slots.py::test_ac_017_no_cross_package_slot_write
  tests/unit/architecture/test_singleton_slots.py::test_ac_017_scanner_reports_planted_violation
  tests/unit/architecture/test_singleton_slots.py::test_edge_008_owner_slot_write_allowed -v -p no:randomly`
  → **1 failed, 2 passed in 0.72s**.
- **RED, correct reason** — `AssertionError: 12 foreign singleton-slot write(s):` at
  `test_singleton_slots.py:178` (an assertion in the test body, not a collection, fixture, import
  or `ValidationError`):

  | Site | Form |
  |---|---|
  | `src/main.py:68` | `import` of `_registry` |
  | `tests/settings_test_helpers.py:132`, `:160`, `:180` | `write` of `_registry` |
  | `tests/eventbus_test_helpers.py:77`, `:84` | `write` of `_default_bus` |
  | `tests/acceptance/settings_coverage/test_setup_logger.py:31`, `:55` | `embedded-write` of `_registry` |
  | `tests/acceptance/settings_coverage/test_wiring.py:18` | `embedded-write` of `_registry` |
  | `tests/contract/logging/test_logging_contracts.py:35` | `embedded-write` of `_registry` |
  | `tests/property/logging/test_logging_properties.py:42` | `embedded-write` of `_registry` |
  | `tests/unit/logging/test_logging_edges.py:32` | `embedded-write` of `_registry` |

  `src/main.py:138` (`_settings_registry_singleton[0] = _settings_registry`) is **not** in the list:
  the write goes through the alias bound by the line-68 import, so the scanner reports the import
  instead (the `ponytail:` ceiling above) — see F-33.

- **The two GREEN nodes are witnesses by construction, not a missing witness.**
  `test_ac_017_scanner_reports_planted_violation` and `test_edge_008_owner_slot_write_allowed`
  assert against fixtures in `tmp_path`, so they pass as soon as the scanner exists — which is
  exactly their role: they prove the scanner fires and does not over-fire, so the single RED above
  is evidence about the repository, not evidence about a broken scanner. **S3.2 must expect
  1 failed / 2 passed** from this `red_command`.
- **Sensitivity — the witness's GREEN state is reachable by the planned fix** (out-of-band scratch
  script, not committed): `src/` + `tests/` copied to a temp tree, scanned (**12 violations**),
  then the DAG's migration applied mechanically to the sites (`set_settings_registry(…)` /
  `set_event_bus(…)` at the five real statements and the six embedded code strings, plus deleting
  the `src/main.py` private import) — 8 files rewritten, re-scan → **0 violations**, every rewritten
  file still AST-parses. The witness is not satisfiable by deleting tests.
- Collection: `uv run pytest --collect-only -q tests/unit/architecture` → **3 tests collected**;
  over the touched paths (`tests/unit/architecture tests/unit/test_settings_test_isolation.py`) →
  **4 tests collected in 0.11s**, zero collection errors.
- Determinism + no state leak: the new file re-run twice (`-p no:randomly`, then with random order)
  → **1 failed, 2 passed** both times (0.72s / 0.59s); `git status --porcelain` after the runs →
  only `?? tests/unit/architecture/` (the planted fixtures live in `tmp_path`).
- T-001's ten / T-002's six / T-003's six / T-004's six / T-005's six / T-006's two nodes re-run
  after this derivation (each set's own `red_command` node list from the DAG): **10 failed**,
  **6 failed**, **6 failed**, **6 failed**, **6 failed**, **2 failed** — same node sets, same
  reasons as recorded at T-001 .. T-006. Nothing of the earlier tasks broke.
- T-007's own `green_command` minus the new file — the six pre-existing files it also runs
  (`tests/unit/test_settings_test_isolation.py tests/acceptance/settings_coverage/test_setup_logger.py
  tests/acceptance/settings_coverage/test_wiring.py tests/contract/logging/test_logging_contracts.py
  tests/property/logging/test_logging_properties.py tests/unit/logging/test_logging_edges.py`) →
  **16 passed in 11.24s**. That is the baseline Phase 4 must preserve while it edits those very
  files.

### Quality gates (per-step scope)

- Ruff gate on the two changed paths: `uv run ruff check <paths>` → **All checks passed**;
  `uv run ruff format <paths>` → **1 file reformatted, 1 file left unchanged** (the first pass
  reflowed the new file), then `ruff format --check` → **2 files already formatted**, and the
  `red_command` was re-run after the reformat with the same result. No whole-repo sweep
  (`ruff check .` / `ruff format --check .` is the Phase 5 gate).
- `uv run python scripts/check_traceability.py` → **PASS (796 matrix rows, 136 spec IDs, 753 test
  functions)** — the function count rose from 750 (T-006) to 753, i.e. the three new functions are
  seen by the script.
- `uv run complexipy src tests --max-complexity-allowed 15` → clean. The first draft of `_scan_file`
  scored **23** and failed the gate; it was split into `_import_violation` (4),
  `_write_violations` (7) and `_embedded` (5), after which `uv run complexipy tests/unit/architecture
  --max-complexity-allowed 15` reports **0** failures (`_scan_file` now 6; max in the file: 7).
- `uv run mypy src/` → **Success: no issues found in 83 source files** (no `src/` file was changed
  by this step; mypy covers `src/` only, so the test file is not type-checked).

### Findings

- **F-32 — the embedded-site count is six, not three.** The DAG's `implementation_steps` ("three of
  them are inside subprocess code strings") and the spec/ADR repeat the P.5 figure of three;
  measured, **six of the eleven** test-side sites are embedded in code strings
  (`test_setup_logger.py:31` and `:55`, `test_wiring.py:18`, `test_logging_contracts.py:35`,
  `test_logging_properties.py:42`, `test_logging_edges.py:32`) and only five are real statements
  (`settings_test_helpers.py:132/:160/:180`, `eventbus_test_helpers.py:77/:84`). The string-literal
  half of the scan is therefore load-bearing, not a hardening extra. No spec/ADR/DAG edit here
  (S3.1 writes tests only); flagged for **S5.3/S6** and for **T-007 Phase 4**, which must migrate
  six embedded sites, not three.
- **F-33 — the scan reports 12 violations, not 11, and `src/main.py` contributes one of them, not
  two.** `src/main.py:68` imports `_registry` under the alias `_settings_registry_singleton`, and the
  write at `src/main.py:138` goes through that alias, so the scanner reports the **import** and not
  the write (F-34's form list plus the documented ceiling). T-006's migration — delete the import,
  call `set_settings_registry(…)` — removes both at once, and **T-007 Phase 4 must delete that
  import line** (`src/main.py` is in T-007's `allowed_files`, and T-006's own task already rewrites
  the write site): the witness cannot go GREEN while the import stays, whatever happens to the other
  eleven. T-007 must not be expected to make the aliased write visible as a 13th violation.
- **F-34 — the scanner reports three forms, and reads are legal.** The DAG names two forms
  (import, subscript write); the embedded form is the third and is what AC-017 needs for the six
  subprocess sites (F-32). A foreign **read** of a slot is not a violation — the guard targets
  writes and imports (EDGE-008) — so `eventbus_test_helpers.py`'s park/restore reads stay legal
  even after the migration; only its two writes are reported.
- **F-35 — the embedded line number is `node.lineno + newlines before the match`.**
  `test_wiring.py:16-20` builds its subprocess code by implicit string concatenation, which the AST
  folds into **one** `Constant` spanning several source lines; reporting `node.lineno` alone would
  point at the first line of the literal instead of the line the write is written on. Measured: the
  reported line is 18, which is where the write text starts.
- **F-36 — the test file must stay clean under the scan it participates in.** A literal
  `f"_mod._registry[0] = …"` in this file would be an `ast.JoinedStr` whose `Constant` chunks are
  `.` and `[0] = …` — the slot name is never adjacent to the write, so even the naive form would
  not self-report; the pattern is nevertheless **assembled from the owner table at import time**
  and the planted fixtures are built with f-strings, so no string constant in the file ever places
  a slot name next to `[0] =`, and the docstrings never spell the write out either. Measured: the
  repository scan reports 12 violations, **none** in `tests/unit/architecture/`. Planted violating
  files live only in `tmp_path` (design constraint) — nothing planted can trip the repository scan
  or the lint gate.
- **F-37 — the scanner is written in Phase 3, not Phase 4.** `allowed_files` lists only test files,
  and the repository witness cannot exist without the scanner, so the scan logic is part of S3.1's
  deliverable. Consequence for **T-007 Phase 4**: its remaining work is exactly the 11-site
  migration (plus the `src/main.py` import line, F-33) — the scan test itself should not need to
  change, and if it does, that is a signal the migration is wrong.
- **F-38 — the matrix rows stay `PENDING`.** `docs/verification/traceability.md` rows
  `REQ-012 | AC-017`, `REQ-013 | AC-017, AC-018` and `EDGE-008` for this change were written at
  P.4 with `—` test cells and are untouched by this step (S5.3 owns them). Flagged for **S5.3**:
  the `REQ-012 | AC-017` row must cite
  `test_ac_017_no_cross_package_slot_write` + `test_ac_017_scanner_reports_planted_violation`, and
  the `EDGE-008` row `test_edge_008_owner_slot_write_allowed`. The change spec is already aligned:
  its §10 table names both AC-017 nodes in one row and `test_edge_008_owner_slot_write_allowed`
  under EDGE-008, and its §11 matrix maps `REQ-013 | AC-017, AC-018` to
  `test_ac_017_scanner_reports_planted_violation` plus T-008's
  `test_ac_018_ruff_bans_private_slot_import`.

### Not done in this step (by design)

No `src/` change; no migration of the 11 test-side sites or of the `src/main.py` import; no change
to any earlier task's tests or to `tests/singleton_install_test_helpers.py`; no `pyproject.toml`
`TID251` / `flake8-tidy-imports.banned-api` rule and no
`tests/contract/singleton_install/test_lint_contract.py` (T-008: REQ-013 ban half, AC-018,
EDGE-009); no `docs/verification/traceability.md` edit (S5.3); no `docs/todo/` or
`docs/questions/` write and no question was raised; no full-suite run (Phase 5 gate); no
`docs/workflow/PROBLEMS.md` entry — the only re-work was the in-step complexipy refactor of the
subagent's own new file (F-37 context), which is an in-step fix-and-recheck, not a step re-entry.

### Hand-off note for T-008 (ruff ban + lint contract test)

- T-008 owns REQ-013's **ban half**, AC-018 and EDGE-009: the `TID251`
  (`flake8-tidy-imports.banned-api`) rule in `pyproject.toml` plus
  `tests/contract/singleton_install/test_lint_contract.py`. Do **not** re-witness the scan half —
  AC-017's three nodes already cover it (F-29 is the mirror image: T-007 does not cover AC-016's
  handle rule, T-008 does not cover the scan).
- `TID251` keys must be **fully qualified** (`"backend.settings.registry._registry" = …`): a bare
  name key (`"_registry"`) flags nothing (EDGE-009, measured in ADR-084's six probes). Importing
  the public trio, or a public symbol from the owning module path, must stay unflagged — 13 such
  test imports exist today and are **not** migrated (they belong to TODO
  `public-api-import-boundary`).
- AC-018 must check **both reference forms** (the `banned-api` entry and the `select` list
  containing `TID251`), and owner writes must stay exempt from the *scan* while the *ban* still
  fires for non-owner files — the two guards are deliberately different in width (ADR-084).
- Order matters: T-008 lands **after** T-007's migration, otherwise the new ruff rule fails the
  whole-repo lint gate on the 12 sites the scan already lists.
- If the contract test plants a violating file, plant it in `tmp_path` and run
  `ruff check --config <temp config>` against it — never inside the repository, for the same
  reason F-36 gives for the scan.
- **Interlock** (DAG `interlock`): `crosscut/structlog-logging` edits
  `tests/contract/logging/test_logging_contracts.py`, `tests/property/logging/test_logging_properties.py`
  and `tests/unit/logging/test_logging_edges.py` — three of the files T-007 Phase 4 migrates.
  Whichever branch merges second rebases and keeps both edits; neither may overwrite the other.

## S3.1 — T-008 test derivation (lint contract: AC-018, EDGE-009, NFR-004) — 2026-10-07

Task under test, read from `.github/task-runner/tasks.json` (byte-identical to
`docs/tasks/settings-public-registry-setter.tasks.json`): **T-008** "Add the five TID251 banned-api
entries and enable TID251 in [tool.ruff.lint].select; prove the ban fires and the repo stays clean"
— `requirements` [REQ-013], `acceptance_criteria` [AC-018], `edge_cases` [EDGE-009],
`non_functional` [NFR-004], `dependencies` [T-007]. Every bare ID below is a
`docs/specs/settings-public-registry-setter.md` ID unless a spec file is named (P-53).
`git rev-parse --show-toplevel` =
`C:/workspace/active-projects/python-template_kopie-worktrees/crosscut/settings-public-registry-setter`
for every count in this section.

### Files created — exactly the DAG's `allowed_files.test_files`

| File | Lines | Notes |
|---|---|---|
| `tests/contract/singleton_install/__init__.py` | 1 | new package (every `tests/` package carries `__init__.py`, which is what puts `tests/` on `sys.path`); T-009/T-011/T-012 add their files to it |
| `tests/contract/singleton_install/test_lint_contract.py` | 212 | the three DAG node IDs, spelled verbatim |

`pyproject.toml` was **not** touched — the config change is T-008's implementation step (S4.x), and
P-55 keeps that file owned by this task only.

### Tests derived (3)

| Test | Normative ID | Assertion design |
|---|---|---|
| `test_ac_018_ruff_bans_private_slot_import` | AC-018 (REQ-013) | four conjuncts, in this order: (1) five files planted in `tmp_path`, each importing one private slot in **both** AC-018 reference forms, must yield exactly 2 `TID251` findings each whose message names the banned path **and** that feature's install operation; (2) `[tool.ruff.lint].select` contains `"TID251"` (read with `tomllib` — AC-018 states the selection as a normative fact, so pinning it is spec-derived, not an implementation detail); (3) `ruff check .` over the repository reports no `TID251`; (4) the five owner modules' own slot files report no `TID251` (the ruff counterpart of EDGE-008) |
| `test_edge_009_public_api_not_banned` | EDGE-009 | five planted files importing the install operation from the feature package **and** a public symbol from the owning module path (`SettingsRegistry`, `EventBus`, `PermissionService`, `SearchService`, `SessionService`) → no `TID251`; plus an **anti-vacuity control**: a sibling planted file importing `backend.settings.registry._registry` **must** be flagged by the same run |
| `test_nfr_004_ruff_and_mypy_clean` | NFR-004 | three conjuncts: the `[tool.ruff.lint.flake8-tidy-imports.banned-api]` table holds all five fully-qualified keys, each with a non-empty `.msg`; `ruff check .` reports no `TID251`; `python -m mypy src` exits 0 |

Tool invocation (deviation from the DAG wording, F-41): `sys.executable -m ruff check
--output-format=json --config <abs pyproject.toml>` and `sys.executable -m mypy src`, `cwd=_REPO_ROOT`
with `_REPO_ROOT = Path(__file__).resolve().parents[3]`. Same tool, same repository configuration, but
resolved from this file's own location instead of the caller's CWD (PROBLEMS.md P-57), and the
interpreter is the one already running the test, so no environment re-resolution happens mid-test.
`_ruff_findings` asserts exit code ∈ {0, 1} and JSON-parseable stdout **before** any assertion on
findings, so a broken invocation can never read as "no violation found".

### Collection

- before: `tests/contract/singleton_install/` did not exist — no nodes.
- after: `uv run pytest --collect-only -q tests/contract/singleton_install` → **3 tests collected**,
  no errors (no module-level import of a not-yet-existing install operation: the tests never import
  `backend.*` at all, they only plant text into `tmp_path`).

### RED gate — the DAG's `red_command`, verbatim

```
uv run pytest tests/contract/singleton_install/test_lint_contract.py::test_ac_018_ruff_bans_private_slot_import \
  tests/contract/singleton_install/test_lint_contract.py::test_edge_009_public_api_not_banned \
  tests/contract/singleton_install/test_lint_contract.py::test_nfr_004_ruff_and_mypy_clean -v
```

| Test | Observed failure |
|---|---|
| `test_ac_018_ruff_bans_private_slot_import` | `AssertionError: AC-018: importing backend.settings.registry._registry must be reported in both reference forms (the ImportFrom and the module-alias write), got 0: []` / `assert 0 == 2` |
| `test_edge_009_public_api_not_banned` | `AssertionError: EDGE-009 anti-vacuity: the same ruff run must report TID251 for a private-slot import — while the ban is inert, 'the public API is not banned' proves nothing` / `assert []` |
| `test_nfr_004_ruff_and_mypy_clean` | `AssertionError: NFR-004 / REQ-013: [tool.ruff.lint.flake8-tidy-imports.banned-api] must configure these fully-qualified keys: ['backend.settings.registry._registry', 'backend.eventbus.eventbus._default_bus', 'backend.permissions.service._permission_service', 'backend.search.service._singleton', 'backend.sessionmanagement.service._session_service']` / `assert [...] == []` |

`3 failed in 0.48s`. Every failure is an `AssertionError` raised in the test body; no
collection/import/fixture error, no `ValidationError`/`ValueError` from test data.

### Why this is a valid RED and not a broken invocation

- `uv run python -m ruff check --output-format=concise --config <abs repo pyproject.toml> <planted
  fixture>` on this branch prints the fixture's own `I001` and `All checks passed!`, exit 0 — the
  invocation runs and the repository configuration loads for a file outside the repo, and **no
  `TID251` comes back** because `TID251` is not in `[tool.ruff.lint].select` (ADR-084: an unselected
  `banned-api` table is inert).
- Sensitivity probe, out-of-band and never committed (`/tmp/tmp.eqFr5NHX5f/probe.py`: the three test
  functions called directly with the module's `_PYPROJECT` pointed at a scratch copy of
  `pyproject.toml` carrying `TID251` + the five fully-qualified keys):
  `test_edge_009_public_api_not_banned: PASS`;
  `test_ac_018…: FAIL -> AC-018: the repository itself must report no TID251 violation`;
  `test_nfr_004…: FAIL -> NFR-004: ruff check . must report no TID251 violation in the repository`.
  So the ban half of both witnesses is satisfiable by exactly the planned config, and the surviving
  failure is the DAG's `T-008 depends on T-007` ordering, not a broken witness.

### Measured facts handed to T-008's implementation step (S4.x)

- Repository sweep with the scratch config: **9** `TID251` findings
  (`uv run python -m ruff check --output-format=concise --config <scratch pyproject.toml> . | grep -c TID251`)
  — the un-migrated write sites T-007 removes. A targeted run over the eight site files
  (`src/main.py`, `tests/settings_test_helpers.py`, `tests/eventbus_test_helpers.py`,
  `tests/acceptance/settings_coverage/test_setup_logger.py`,
  `tests/acceptance/settings_coverage/test_wiring.py`, `tests/contract/logging/test_logging_contracts.py`,
  `tests/property/logging/test_logging_properties.py`, `tests/unit/logging/test_logging_edges.py`)
  gives the same 9.
- The five owner modules' own slot files report **no** `TID251` under the scratch config — `TID251`
  sees cross-module references only (the ruff counterpart of EDGE-008, measured).
- `uv run python -m mypy src` → `Success: no issues found in 83 source files`, exit 0, 0.4 s.
- `uv run ruff check .` on the current tree → `All checks passed!` — i.e. AC-018's repository half is
  "clean" today only because the rule is inert.

### Gates run for this step

- `uv run ruff check tests/contract/singleton_install/__init__.py tests/contract/singleton_install/test_lint_contract.py`
  → **All checks passed** (after one in-step fix: `PLR2004` on the literal `2`, replaced by the named
  constant `_REFERENCE_FORMS`).
- `uv run ruff format --check` on the same two paths → **2 files already formatted**.
- `uv run complexipy tests/contract/singleton_install --max-complexity-allowed 15` → all functions
  within the limit (max 7).
- `uv run python scripts/check_traceability.py` → `Traceability: PASS (796 matrix rows, 136 spec IDs,
  756 test functions)`.
- T-007's three nodes re-run after adding this file: `1 failed, 2 passed`, still **12** foreign write
  sites — the new file lives under `tests/` and **is** read by the T-007 scanner, and it is not
  flagged, because the planted fixture source is assembled from the owner table with f-strings so no
  string constant in this file places a slot name next to a subscript write (the F-36 lesson applied
  before the first run, not after a scan failure).
- Determinism: the `red_command` run twice (plain, and `-p no:randomly`) → the same 3 failures with
  the same messages; the whole package re-run → `3 failed`.
- State leak: `git status --porcelain` → only `?? tests/contract/singleton_install/`. Planted ruff
  fixtures live in pytest `tmp_path`, never in the repository — the `lint` job runs `ruff check .` on
  every push (`.github/workflows/lint.yml:37`), so a planted violation committed into the repo would
  break CI (T-008 design constraint, ADR-084).

### Findings

- **F-41** The DAG's `red_command`/`green_command` wording (`uv run ruff check --config pyproject.toml
  <fixture>`) is CWD-dependent: a relative `pyproject.toml` resolves against the caller's directory,
  which is exactly the PROBLEMS.md P-57 hazard. The tests invoke the same tool with an absolute
  config path derived from `__file__` and the test interpreter. Deviation from the DAG wording only;
  the tool, the configuration and the assertion target are unchanged.
- **F-42** Fixture naming collision, caught by the sensitivity probe before commit: keying a planted
  file on the owning module's leaf name collapses three fixtures into one, because three of the five
  owning modules are `service.py`. The probe's AC-018 message quoted
  `backend.sessionmanagement.service._session_service` findings under the permissions slot. Fixed by
  keying the planted names on the slot (unique across the five) plus an explicit uniqueness assert in
  both tests.
- **F-43** EDGE-009's witness needed an anti-vacuity control: with the ban inert, "the public API is
  not flagged" is trivially true, so the test would have been GREEN before implementation — an invalid
  RED. It now also asserts that the *same* ruff run reports `TID251` for a private-slot import.
- **F-44** Citation defects inside the T-008 DAG entry (same class as F-37): `inputs` cite
  "`pyproject.toml` [tool.ruff.lint].select (line 95)" — `select` is at `pyproject.toml:182` — and
  "spec section 11" for the measured ruff facts — §11 is the Traceability Matrix, the facts are in §10
  Test Strategy (spec lines 326-327). No effect on the derivation; recorded so the S2.x record is not
  trusted for line numbers.
- **F-45** `test_ac_018_ruff_bans_private_slot_import` and `test_nfr_004_ruff_and_mypy_clean` will stay
  RED on their repository half until T-007's Phase 4 migration of the 12 write sites lands (measured:
  9 `TID251` findings with the config applied). The DAG already orders T-008 after T-007; this is the
  dependency made visible, not a defect in the witnesses. `test_edge_009_public_api_not_banned` is the
  only one of the three that goes GREEN on the config change alone.
- **F-46** Matrix rows for these IDs are the change-spec rows `REQ-013 | AC-017, AC-018`
  (`docs/verification/traceability.md:937`), `EDGE-001 … EDGE-010` (`:942`) and `NFR-001 … NFR-004`
  (`:943`), all `PENDING` from P.4; S5.3 fills them with these node IDs. P-53 warning for S5.3: the
  matrix already carries unrelated `AC-018` rows (`:106` `settings.md`, `:199` user-roles-permissions)
  and unrelated `EDGE-009` / `NFR-004` rows — write only inside the change-spec section.

### Hand-off

- **S3.2 (T-008)**: the ruff gate for this step is already clean on the changed paths and RED is
  observed above; S3.2 re-confirms RED on the three nodes. It must **not** run the whole-repo sweep —
  that is one of T-008's own completion gates in Phase 4/5, and it is clean today only because the
  rule is inert.
- **T-008 implementation (S4.x)**: add `TID251` to `[tool.ruff.lint].select` (only `TID251`, not the
  `TID` family) and the `[tool.ruff.lint.flake8-tidy-imports.banned-api]` table with the five
  fully-qualified keys, each `.msg` naming that feature's `set_*`/`get_*`/`reset_*` trio; the
  repository half then requires T-007's migration.

### Next

S3.1 for **T-009** (cross-cutting witness set: AC-002..AC-008, AC-013, AC-020, EDGE-001..EDGE-007,
INV-002, INV-003, NFR-001, NFR-002).

---

## S3.1 — T-009 test derivation (cross-cutting witness set) — 2026-10-07

Task object re-read from `.github/task-runner/tasks.json` before writing (PROBLEMS.md P-63):
`feature_group` "cross-cutting witness set — all five features: uniform install semantics,
public API contract, catalog surface, latency"; `requirements` REQ-001…REQ-005, REQ-009,
REQ-014, REQ-016; `acceptance_criteria` AC-002…AC-008, AC-013, AC-020; `edge_cases`
EDGE-001…EDGE-007; `invariants` INV-002, INV-003; `non_functional` NFR-001, NFR-002;
`dependencies` T-001…T-005 (a **Phase 4** ordering constraint — derivation ran now, with none
of the five install operations implemented, so RED is the expected state).
`implementation_scope`: "…No src/ file changes." — no `src/` file was touched in this step.

### Files created / modified — exactly the DAG's `allowed_files.test_files`

| File | Nodes | State |
|---|---|---|
| `tests/acceptance/singleton_install/test_install.py` | 6 (AC-002…AC-006, AC-013) | modified — added to the file T-001 created |
| `tests/contract/singleton_install/test_api_contract.py` | 4 (AC-007, AC-008, AC-020, NFR-001) | new |
| `tests/contract/singleton_install/test_performance_contract.py` | 1 (NFR-002) | new |
| `tests/unit/singleton_install/test_edges.py` | 7 (EDGE-001…EDGE-007) | new |
| `tests/property/singleton_install/test_install_properties.py` | 2 (INV-002, INV-003) | new |
| `tests/singleton_install_test_helpers.py` | — | modified — extended the T-001 slot table (PROBLEMS.md P-55) |
| `tests/unit/singleton_install/__init__.py`, `tests/property/singleton_install/__init__.py` | — | new packages |
| `tests/contract/singleton_install/__init__.py` | — | **untouched** — T-008 already created it |

### The helper extension (what the witnesses share)

`SingletonSlot` gained three fields — `stamper` (required), `dispose` (default no-op),
`warning_keyword` — and two methods, `stamp()` and `name()`. `stamp()` returns
`(instance, probe)` where the probe recognizes **that one instance** through its own public
API only (two instances of the same class are otherwise indistinguishable, so a cross-feature
witness could not tell "the caller still gets what it was given" from "the install swapped it
out"): settings registers a unique `app.name` default read by `get_value`; eventbus subscribes
a per-stamp private event class and the probe publishes it; permissions creates a runtime role
`stamp_<hex>` (a **grant** would need a catalog the isolated service does not carry — its
default `PermissionCatalog` is empty, `src/backend/permissions/service.py:135`) read by
`list_roles()`; search registers a uniquely named source read by `list_sources()`;
session-management builds the service over a store pre-loaded with one session row read by
`list_sessions()` (the service owns no state of its own — its store is its observable state).
`EventWatcher` subscribes the collector for `object` on every touched instance that has
`subscribe` (only `EventBus` does) and `drain()` shuts each watched bus down, which drains its
queue (event-bus.md AC-008) — so "no event arrived" is a settled fact, not a race.

### Collection — the DAG's 20 node IDs, exact

`uv run pytest <the five files> --collect-only -q -p no:randomly` → **21** collected: the 20
`tests_to_create` node IDs plus `test_ac_001_install_then_get_returns_instance` (T-001's node,
which lives in the shared `test_install.py`). Diff against the task object:
`MISSING: []`, `EXTRA: [test_ac_001…]` only. `git rev-parse --show-toplevel` →
`C:/workspace/active-projects/python-template_kopie-worktrees/crosscut/settings-public-registry-setter`
(the change worktree, PROBLEMS.md P-57).

The witnesses **loop over `SLOTS` inside each test function** instead of using
`pytest.mark.parametrize`: a parametrized node ID carries a `[param]` suffix and would push the
collected set past the 20 node IDs the DAG names for this task.

### RED gate — the DAG's `red_command`, verbatim

`red_command` = `uv run pytest <20 node IDs> -v` (24 argv words; `red_command == green_command`).

```
============================= 20 failed in 1.38s ==============================
```

Failure kinds (all 20):

| Kind | Nodes | Message |
|---|---|---|
| `AttributeError` at call time | 19 | `module 'backend.<feature>' has no attribute 'set_<x>'` |
| `AssertionError` (subprocess) | 1 (`test_edge_005`) | `the child process did not run: … AttributeError: module 'backend.settings' has no attribute 'set_settings_registry'` + `assert 1 == 0` |

Determinism: the five-file set re-run twice (plain and `-p no:randomly`) → the same 21 failures
(20 + T-001's); `tests/property/singleton_install/ tests/unit/singleton_install/` re-run with
randomization on → `9 failed` (7 EDGE + 2 INV).

### Why this is a valid RED and not a broken invocation

- **No collection, import or fixture error.** Every witness resolves the install/get/reset trio
  with `getattr` on the slot object **at call time**, so a missing installer fails inside the
  test body; a module-level `from backend.settings import set_settings_registry` would be a
  collection error and would take down T-001's node in the same file.
- **Test data is valid.** Every stamped instance is built by the real constructor over isolated
  storage (in-memory SQLite for permissions/session-management, a temp-dir value repository for
  settings); no `ValidationError`/`ValueError` is raised while constructing fixtures — the only
  `ValueError` in the set is the one `test_edge_003` asserts, which is the specified behaviour
  of `get_session_service()` with no repository (session-management.md EDGE-003/AC-042).
- **Anti-vacuity anchors** (each one is what makes the witness RED now instead of GREEN by
  construction): AC-013 publishes a sentinel **after** the installs and asserts exactly it
  arrives, so "no event" is a working collector's verdict; AC-020 asserts `hasattr(module,
  installer)` before claiming the installer is not a catalog action; NFR-001 asserts the five
  installers are in `__all__` on top of the superset check (the per-package contract tests, e.g.
  `tests/contract/sessionmanagement/test_contract.py::test_nfr_003_public_api_contract`, are
  `hasattr`-based over a hand-maintained list that omits the new name, so they cannot go RED on
  an additive surface — finding F-23); EDGE-007 asserts the **install** WARNING first so that
  "reset logs none" is a contrast rather than a tautology; INV-003's event pass asserts the
  witness's own event arrives; `test_edge_005` asserts `returncode == 0` so a child that never
  ran is a failure, not a silent pass (findings F-41 / PROBLEMS.md P-57).
- **Three nodes contain a half that is already true today** (`test_edge_003`, `test_edge_004`,
  `test_edge_007`): they witness behaviour the change must **preserve**, and each also performs
  an install, which is what makes them RED now. They are the regression half of EDGE-003/004/007.

### Measured facts handed to T-009's implementation step (S4.x)

- The permission catalog built the only way it can be built — `PermissionCatalog()` plus
  `register_actions(catalog)` on each of the **seven** `feature_actions` modules — enumerates
  **61** action keys over 7 features (authentication 11, filemanagement 10, mail 3, search 1,
  sessionmanagement 6, settings 19, usermanagement 11). `test_ac_020_permission_catalog_unchanged`
  freezes that measured composition (total + per-feature counts + no installer key + no new
  action), not the spec's "60" wording — see F-47.
- NFR-002 times **only** the install call (instances built and slots cleared outside the timed
  region); `_REPEATS = 100` per path per slot, budget `1.0 ms` median. The same run asserts the
  pipeline was at DEBUG (`>= _REPEATS` DEBUG records captured) and that the replacing path logged
  exactly one non-tracing WARNING per install while the empty-slot path logged none — which also
  pins that the WARNING is inside the timed region.
- `widened_lazy_create_window` (T-007's helper) is **not** used by any T-009 witness: search
  already guards its lazy path with `_singleton_lock` (`src/backend/search/service.py:547`) and
  session-management has **no** module lock at all (`src/backend/sessionmanagement/service.py:344,
  359, 364, 371`), so widening it there would manufacture a real create race rather than witness
  one (finding F-21). The session-management create-race witness is T-010's AC-010 run with a
  repository supplied.
- The event bus matches handlers by `isinstance`, so an `object` subscription receives every
  event type; `publish()` on a shut-down bus is a **silent no-op**
  (`src/backend/eventbus/eventbus.py:109-111`) — that is what makes the EDGE-006/EDGE-007
  "still dispatching / no longer dispatching" probes observable through the public API.
- Every witness that resets the event bus slot does so inside the existing
  `isolated_event_bus()` helper (eventbus_test_helpers) — a bare `reset_event_bus()` shuts the
  suite's live bus down before clearing it and kills the logging feature's sink wiring
  (helper docstring, main-ci-green item H).

### Gates run for this step

- `uv run ruff check <the six changed paths>` → `All checks passed!` (after `--fix` for three
  `I001` import-order findings and one `Q001`, and one manual `check=False` for `PLW1510` on the
  subprocess call — the returncode assertion is the witness, so `check=True` would raise instead
  of reporting which side failed).
- `uv run ruff format <the six changed paths>` → clean; a second pass reports no further change.
- `uv run complexipy <the four new/changed test paths> tests/singleton_install_test_helpers.py
  --max-complexity-allowed 15` → no finding (one refactor was needed: the inline INV-002 body
  scored **18**, fixed by extracting `_count_installs_on_nonempty_slot`, see F-51).
- `uv run python scripts/check_traceability.py` → `Traceability: PASS (796 matrix rows, 136 spec
  IDs, 776 test functions)`. The matrix rows for these IDs are the change-spec rows
  `EDGE-001 … EDGE-010` and `NFR-001 … NFR-004` (`docs/verification/traceability.md:942-943`) and
  the `REQ-013 | AC-017, AC-018` row (`:937`), all still `PENDING` with `—` in the Test column —
  established practice on this branch is that no S3.1 step fills the Test column (S5.3 does).
- `uv run pytest tests/unit/architecture/test_singleton_slots.py` (T-007's AC-017 scan) → `1
  failed, 2 passed`, still **12** foreign write sites, none of them in a file this step wrote:
  the new tests plant no private-slot write (they go through the public `reset_*` operations, and
  the event-bus parking is the pre-existing helper at `tests/eventbus_test_helpers.py:77,84`).
- `uv run mypy src/` — not run: the gate targets `src/` and this step changed no `src/` file
  (`ty check src/` likewise). Not run at all: the whole-repo ruff sweep (Phase 5,
  `.github/workflows/lint.yml:37`), the full test suite, `deptry`, `alembic`, `mkdocs`.
- State leak: `git status --porcelain` → the six paths in the table above and nothing else;
  `data/` and `settings/` are gitignored (`.gitignore:230`, `:225`) and the subprocess witness
  runs with `cwd=tmp_path`, so the child writes nothing into the worktree.

### Findings

- **F-47** AC-020's wording — "the static **60**-key mapping built from public non-underscore
  methods of the six public service classes" — does not match the repository: the catalog is
  built at startup from feature-owned `register_feature(feature, actions)` calls
  (`src/backend/permissions/catalog.py`), seven features register, and the measured key count is
  **61**. The witness freezes the measured composition rather than the spec's number: asserting
  60 would be a RED caused by a spec-wording defect, not by this change. Escalation for S5.3 /
  Phase 6: either the AC-020 wording is amended through the Spec Amendment Workflow or the review
  records the measured 61 as the frozen baseline.
- **F-48** `build_default_catalog` does not exist in `src/backend/permissions/catalog.py`
  (invented API, same family as F-43/F-44). The catalog is constructible only as
  `PermissionCatalog()` plus `register_actions(catalog)` on each feature's actions module, and
  exactly seven packages expose `register_actions` — `backend.eventbus` exposes none (its
  package holds only `__init__.py`, `eventbus.py`, `feature_settings.py`), so the event bus
  contributes no catalog action.
- **F-49** `PermissionService.__init__` defaults `catalog` to an **empty** `PermissionCatalog()`
  (`src/backend/permissions/service.py:135`), so an isolated service cannot
  `grant_permission("settings.select")` — `UnknownPermissionError`. The permissions stamp marks a
  runtime **role**, not a grant. Any later witness that needs real catalog keys must build the
  catalog itself.
- **F-50** NFR-002's "measured with the logging pipeline at DEBUG" is not observable through a
  loguru API (`Logger` has no `is_debug`; the first draft of the contract test raised
  `AttributeError: 'Logger' object has no attribute 'is_debug'` — an invalid test, not a RED).
  The pipeline state is pinned from the capture instead (DEBUG record count + the WARNING count
  per install path).
- **F-51** The complexipy gate (`.github/workflows/quality.yml:144`, `pyproject.toml:97-99`)
  caught the inline INV-002 body at **18** > 15. Extracted helper; the property semantics are
  unchanged.
- **F-52** AC-005 and INV-003's "every object that was constructed with an injected instance"
  half is witnessed with a per-slot stamp/probe holder rather than with real injected consumers:
  of the five singleton classes only three have a consuming service in the public API
  (settings/eventbus/permissions are injected into `SearchService`/`SessionService`/etc.), and
  search and session-management have **no** consumers anywhere. The holder carries a `ponytail:`
  comment naming that ceiling; the injected-consumer form is witnessed by the feature specs
  themselves (search.md EDGE-022, session-management.md EDGE-014, event-bus.md EDGE-011).
- **F-53** `test_edge_007_reset_event_bus_still_shuts_down` would have been GREEN before
  implementation (reset already shuts the instance down today, and it logs no WARNING today
  either). It now installs a bus, replaces it (asserting the install WARNING that makes the
  contrast real) and only then resets, so the node is RED now and its "reset logs none" half is
  a statement about the post-change world.
- **F-54** INV-003's two halves run as **separate per-slot passes**: `drain()` shuts every watched
  bus down, so a bus stamp published afterwards would fail, and a stamp published beforehand
  would put the stamp's own marker event into the collector and break the no-events assertion.
  The passes are ordered events-first, holder-second.
- **F-55** The DAG's `allowed_files.test_files` lists
  `tests/contract/singleton_install/__init__.py` "(only if T-008 has not created it yet)" — T-008
  created it, so it is untouched; the two new packages this step needed
  (`tests/unit/singleton_install/`, `tests/property/singleton_install/`) are the only new
  `__init__.py` files.

### Not done in this step (by instruction)

- The **Phase 3 RED gate declaration** — S3.2 owns it; this record is the evidence S3.2 re-confirms.
- No implementation, no refactor, no `src/` change; no full-suite run; no push; no other
  worktree touched; no `docs/todo/` or `docs/questions/` edit; no `PROBLEMS.md` entry; no
  traceability-matrix edit (S5.3).

### Hand-off

- **S3.2 (T-009)**: re-run the DAG's `red_command` verbatim — expect `20 failed`, all
  `AttributeError: … has no attribute 'set_*'` except `test_edge_005`, which fails on
  `assert 1 == 0` with the child's own `AttributeError` in its stderr. Ruff is already clean on
  the changed paths.
- **T-009 implementation (S4.x)**: the five install operations must (a) take exactly one
  positional parameter annotated with the concrete class and return `None` (AC-007), (b) contain
  no `isinstance`/`type(...)` guard and add no new `*Error` export (AC-008), (c) log exactly one
  non-tracing WARNING naming the replaced default on the replacing path and none on the empty-slot
  path (AC-003/AC-004, INV-002), (d) publish no event (AC-013, INV-003), (e) leave the replaced
  `EventBus` running and the installed one unstarted (AC-006 — `EventBus.is_running` is the public
  probe; EDGE-006 — the `eventbus-worker` thread count), (f) leave `reset_event_bus()` shutting the instance down and logging nothing
  (EDGE-007), and (g) stay inside the existing `_singleton_lock` where one exists (ADR-084).
  If a witness exposes a divergence between two features, fix the module — do not relax the
  witness (T-009 design constraint).
- **T-010 / T-011** extend `tests/singleton_install_test_helpers.py` and
  `tests/property/singleton_install/test_install_properties.py` (`test_inv_001_last_install_wins`
  is T-010's, deliberately absent here); they must keep the `SingletonSlot` field order and the
  five `SLOTS` entries intact — T-009's witnesses iterate `SLOTS` and assume exactly five.

### Next

S3.1 for **T-010** (the module lock: REQ-006…REQ-008, AC-009…AC-012, INV-001, EDGE-010,
NFR-003), which depends on T-009's helper surface.

## S3.1 — T-010 test derivation (cross-cutting witness set — the module lock) — 2026-10-07

Task object re-read from `.github/task-runner/tasks.json` before writing (PROBLEMS.md P-63):
`feature_group` "cross-cutting witness set — all five features: the module lock (install, lazy
create, reset)"; `requirements` REQ-006, REQ-007, REQ-008; `acceptance_criteria` AC-009…AC-012;
`edge_cases` EDGE-010; `invariants` INV-001; `non_functional` NFR-003; `dependencies` T-001…T-005,
T-009 (a **Phase 4** ordering constraint — derivation ran now, with none of the five install
operations implemented and no module lock added, so RED is the expected state).
`implementation_scope` — no `src/` file was touched in this step; the five feature modules listed in
`allowed_files.source_files` are fix-only for the implementation step.

### Files created / modified — exactly the DAG's `allowed_files.test_files`

| File | Nodes | State |
|---|---|---|
| `tests/acceptance/singleton_install/test_concurrency.py` | 3 (AC-009, AC-010 + EDGE-010, NFR-003) | **new** (252 lines) |
| `tests/acceptance/singleton_install/test_install.py` | 2 (AC-011, AC-012) | modified — added to the file T-001/T-009 created (266 lines) |
| `tests/property/singleton_install/test_install_properties.py` | 1 (INV-001 + the EDGE-010 concurrency half) | modified — added to the file T-009 created (269 lines) |
| `tests/singleton_install_test_helpers.py` | — | modified — extended the shared slot table (PROBLEMS.md P-55), 499 lines |

No new package `__init__.py` was needed (both target directories already exist). No `src/`, no
`docs/specs/`, no `docs/verification/traceability.md`, no `docs/todo/`, no `docs/questions/` change.

### The helper extension (what the five witnesses share)

`SingletonSlot` gained two fields — `reader_args` (a `Callable[[], tuple]` supplying the arguments a
feature's `get_*()` needs, default `_no_reader_args`) and the matching `read_args()` method — plus the
module-level `concurrent_installs(slot, instances)` helper. Appending defaulted fields is safe because
all five `SLOTS` entries are constructed with keyword arguments, and the field order and the five
entries are unchanged (T-009's witnesses iterate `SLOTS`). Session-management's slot supplies
`lambda: (SqliteSessionRepository(<temp url>),)` so every read of that slot carries a repository
(`session-management.md` EDGE-003); the other four supply `()`. `record_constructions` and the mixed
install/read/reset race driver stay **local** to `test_concurrency.py` — they are this task's shape,
not shared surface.

### Collection — the DAG's 6 node IDs, exact

`uv run pytest tests/acceptance/singleton_install/ tests/property/singleton_install/ --collect-only -q`
→ **15 tests collected**, no errors: the 6 `tests_to_create` node IDs plus the 9 pre-existing nodes of
the shared files (T-001's AC-001…AC-006 + AC-013, T-009's INV-002 + INV-003).
`git rev-parse --show-toplevel` → `C:/workspace/active-projects/python-template_kopie-worktrees/crosscut/settings-public-registry-setter`
(the change worktree, PROBLEMS.md P-57). As in T-009, the witnesses **loop over `SLOTS` inside the test
function** instead of parametrizing, so no `[param]` suffix pushes the collected set past the node IDs
the DAG names.

### RED gate — the DAG's `red_command`, verbatim

`red_command` = `uv run pytest <the 6 node IDs> -v` (`red_command == green_command`).

```
plain (random order)          →  6 failed in 0.84s
-p no:randomly                →  6 failed in 0.89s
third plain re-run            →  6 failed in 0.84s
```

Failure reason per node (`-p no:randomly --tb=long --show-capture=no`; `--show-capture=no` is required
because the captured loguru tracing output otherwise floods the tracebacks):

| Node | Reason |
|---|---|
| `test_ac_009_concurrent_lazy_create` | `AssertionError: settings: 8 concurrent reads of an empty slot returned 8 different instances — the read-and-swap is not one atomic module-lock step` / `assert 8 == 1` (`test_concurrency.py:77`) |
| `test_ac_010_concurrent_install_read_reset` | `AttributeError: module 'backend.settings' has no attribute 'set_settings_registry'. Did you mean: 'get_settings_registry'?` |
| `test_nfr_003_slot_lock_is_short_lived` | `AttributeError: module 'backend.eventbus' has no attribute 'set_event_bus'. Did you mean: 'get_event_bus'?` |
| `test_ac_011_lazy_path_emits_one_traced_pair` | `AssertionError: settings: set_settings_registry() does not exist, so 'no entry record for it' would be vacuous` (`test_install.py:218`, the `hasattr` anti-vacuity anchor) |
| `test_ac_012_install_then_reset_then_default` | `AttributeError: module 'backend.settings' has no attribute 'set_settings_registry'` |
| `test_inv_001_last_install_wins` | same `AttributeError`, `Failing test case: inner(ops=['install'])` |

### Why this is a valid RED and not a broken invocation

- **No collection, import or fixture error.** The trio is resolved by `getattr` at call time
  (`SingletonSlot.install/read/clear`), so the missing public setter fails **inside** the test body —
  a module-level `from backend.settings import set_settings_registry` would be a collection error and
  would take down T-001's and T-009's nodes in the same files.
- **Test data is valid.** Every instance is built by the real constructor over isolated storage (temp-dir
  value repository, in-memory SQLite for permissions/session-management, a scratch bus inside
  `isolated_event_bus()`); no `ValidationError`/`ValueError` is raised while building fixtures. The only
  `ValueError` in the set is the one AC-009 **asserts** for session-management (`pytest.raises(ValueError)`
  — the specified EDGE-003 behaviour of `get_session_service()` with no repository).
- **One invalid RED was found and fixed inside this step** (F-57): `_no_reader_args` was copied from the
  docstring-only `_keep` disposer and had no `return ()`, so `slot.read(*slot.read_args())` raised
  `TypeError: … argument after * must be an iterable, not NoneType` — a helper bug, not a RED.

### Anti-vacuity — each witness can fail

- **AC-009 (the lock-removal teeth).** The lazy-create window is widened for **all four** lazy features
  **including search**, which reverses the T-009 hand-off note (F-56). Sensitivity measured out-of-band
  (scratch probe, deleted before the commit; run twice with the same result):
  `WITH search _singleton_lock: distinct reads=1 constructed=1` /
  `WITHOUT search _singleton_lock: distinct reads=8 constructed=8` — i.e. the widened race is genuinely
  gated by search's module lock, and with the lock present widening can only serialize, so search's leg
  is neither vacuous nor artificially manufactured. The other three legs are sensitive today by
  construction: settings/eventbus/permissions have no module lock, which is exactly what the recorded
  `assert 8 == 1` shows.
- **AC-010 + EDGE-010.** The witness asserts no thread raised, all 8 reads completed, no read returned an
  instance no constructor completed (identity set = A + the 8 installed + everything `__init__` recorded),
  the settled slot value is in that set, and the replace-WARNING count is in `_INSTALLS - _RESETS … _INSTALLS`
  (6…8) — the bounds are properties of the schedule (only the 2 resets can empty the slot), not of the
  scheduler. Its lock-removal sensitivity is **capped by the GIL** and the witness says so in a
  `ponytail:` comment rather than faking more teeth (F-58).
- **NFR-003.** The witness parks a reset inside `EventBus.shutdown()` (an instance attribute shadows the
  bound method — `EventBus` declares no `__slots__`) and requires the install to complete while the reset
  is provably still inside the call; the **same predicate is then evaluated against a serialized control
  pass** that waits for the release itself — exactly what a lock held across `shutdown()` would do — and
  the witness asserts that control reports `False`, so the real pass cannot be GREEN by construction.
- **AC-011.** `hasattr(module, installer)` is asserted before the "no entry record for the install
  operation" claim, which is the node's current RED trigger; the pair count is taken over `>>`/`<<`
  records naming the getter, and warnings are filtered with `non_tracing_warnings` so the `@logged`
  slow-call escalation cannot fake the count.

### Gates run for this step

- `uv run ruff check <the four changed paths>` → `All checks passed!`
- `uv run ruff format <the four changed paths>` → `4 files left unchanged` (a first pass reformatted 3).
- `uv run complexipy <the four changed paths> --max-complexity-allowed 15` → *All functions are within the
  allowed complexity*; every T-010 function was analysed (highest: `_assert_read_returns_last_write` **10**,
  `test_ac_009_concurrent_lazy_create` **5**, `_assert_concurrent_installs_last_writer_wins` **5**), so no
  F-51-style refactor was needed.
- `uv run python scripts/check_traceability.py` → `Traceability: PASS (796 matrix rows, 136 spec IDs,
  782 test functions)`. The rows for REQ-006…REQ-008, AC-009…AC-012, INV-001, EDGE-010, NFR-003 already
  exist as `PENDING` (`docs/verification/traceability.md:942-943` area); established practice on this
  branch is that no S3.1 step fills the Test column (S5.3 does — F-31/F-38).
- `uv run pytest tests/unit/architecture/test_singleton_slots.py` (T-007's AC-017 scan) → `1 failed, 2
  passed`, still **12** foreign write sites, none in a file this step wrote. The new tests plant no
  private-slot write: they go through the public `reset_*` operations and the pre-existing
  `isolated_event_bus()` parking helper.
- **No regression in any earlier task's node set** — every earlier task's own `red_command` re-run after
  this step: T-001 `10 failed`, T-002 `6 failed`, T-003 `6 failed`, T-004 `6 failed`, T-005 `6 failed`,
  T-006 `2 failed`, T-007 `1 failed, 2 passed`, T-008 `3 failed`, T-009 `20 failed` — identical to the
  counts recorded in each section above. (T-011/T-012 exit with usage error `rc 4`: their tests do not
  exist yet.)
- **No regression in the shared helper's other consumers.** `tests/singleton_install_test_helpers.py` is
  imported by 15 test files, not only the `singleton_install` ones (F-62), so the helper-consumer set
  (`tests/contract/singleton_install tests/unit/singleton_install
  tests/unit/architecture/test_singleton_slots.py tests/acceptance/settings/test_settings.py
  tests/property/settings tests/unit/settings/test_settings_edges.py
  tests/unit/eventbus/test_eventbus_edges.py tests/unit/permissions/test_edge_cases.py
  tests/unit/search/test_search_edges.py tests/unit/sessionmanagement/test_validation.py`) was run **with
  and without** this step's changes: `33 failed, 141 passed` both times — byte-identical outcome, so the
  additive helper change moved nothing.
- `uv run mypy src/` / `ty check src/` — not run: the gate targets `src/` and this step changed no `src/`
  file. Not run at all: the whole-repo ruff sweep (Phase 5, `.github/workflows/lint.yml:37`), the full
  test suite, `deptry`, `alembic`, `mkdocs`.
- State leak: `md5sum data/permissions.db settings/values.yaml` identical before and after the runs
  (`555e225f…`, `af81d232…`); `git status --porcelain` after the step → the four paths in the table above
  and nothing else (the scratch RED capture file and the scratch probe were deleted before the commit).

### Findings

- **F-56 — AC-009 widens the lazy-create window for search too, reversing the T-009 hand-off note.**
  T-009's note (and the earlier reading of F-21) said `widened_lazy_create_window` must not be used for
  search because `src/backend/search/service.py:547` already guards the lazy path with `_singleton_lock`.
  For AC-009 that would make search's leg **vacuous**: the assertion would hold whether or not the lock
  existed. Widening is harmless where a lock exists (it can only serialize) and necessary where one does
  not, so the witness widens all four lazy features and the sensitivity is proven out-of-band instead of
  assumed — see the probe result above. The rule for later tasks: widen every lazy leg, and prove the
  guarded ones are still sensitive.
- **F-57 — `_no_reader_args` was a docstring-only body** (copied from the docstring-only `_keep`
  disposer), so it returned `None` and `slot.read(*slot.read_args())` raised `TypeError` — an invalid RED
  (helper bug) that the collection-only gate cannot catch. Fixed in this step with `return ()`. A no-op
  **disposer** may be docstring-only; a **tuple provider** may not.
- **F-58 — AC-010's lock-removal sensitivity is capped by the GIL.** A Python-level singleton slot write
  is atomic, so deleting the module lock would not tear a read and the whole-instance / final-value
  assertions would still pass. The witness therefore proves what it can prove (interface race-safety: no
  thread raises, no torn value, last-writer-wins, no install lost silently) and carries a `ponytail:`
  comment naming the ceiling; the lock-removal teeth for the create path live in AC-009. This cap is
  recorded rather than papered over with a weaker assertion.
- **F-59 — session-management has no lazy default, so two of the five legs are shaped differently.**
  AC-009 and AC-011 skip it (`get_session_service()` with no repository raises `ValueError` —
  `session-management.md` EDGE-003; the change spec scopes those ACs to the four features whose `get_*()`
  creates a default), and AC-010/AC-012 run it with a repository on every read (`session-management.md`
  AC-048/AC-049). The skip is an explicit `if slot is SESSIONMANAGEMENT_SLOT` branch with the reason in
  the test, not a silent narrowing.
- **F-60 — INV-001's property half and its EDGE-010 half run separately.** The `@given` sequence model
  (ops over `install`/`reset`/`read`, `max_size=8`, `max_examples=15`, `deadline=None`) cannot assert the
  EDGE-010 WARNING count — a reset inside the sequence makes "how many installs met a non-empty slot"
  schedule-dependent — so the concurrency half runs **once per slot outside the `@given` loop**, with the
  slot pre-filled and no reset during the race, which pins the count to exactly `_CONCURRENT_INSTALLS`
  (4). Fewer racers than AC-010's 8: the clause is about the race, not the volume. INV-001 was **not**
  weakened to satisfy EDGE-010 (T-010 design constraint).
- **F-61 — the pre-existing broken witness F-11 is still there and still untouched.**
  `tests/acceptance/eventbus/test_eventbus.py::_concurrent_install_read_reset` passes two arguments to a
  one-argument `_run(action)`, so its install threads only record a `TypeError`. This step did not touch
  that file (out of T-010's `allowed_files`); it is reported again because T-010's AC-010 is the shape the
  eventbus witness will be reconciled to.
- **F-62 — the shared helper has 15 importers.** `tests/singleton_install_test_helpers.py` is imported by
  the five feature test files, the contract/unit/property `singleton_install` files and
  `tests/property/settings/test_settings_properties.py`, so any helper edit must be regression-checked
  against that set, not only against the `singleton_install` directories. The with/without comparison
  above is the cheap way to do it.

### Not done in this step (by instruction)

- The **Phase 3 RED gate declaration** — S3.2 owns it; this record is the evidence S3.2 re-confirms.
- No implementation, no refactor, no `src/` change; no full-suite run; no push; no other worktree touched;
  no `docs/todo/` or `docs/questions/` edit; no `PROBLEMS.md` entry; no traceability-matrix edit (S5.3);
  no other DAG task's tests derived (PROBLEMS.md P-64).

### Hand-off

- **S3.2 (T-010)**: re-run the DAG's `red_command` verbatim — expect `6 failed`, with the per-node reasons
  in the table above. Ruff is already clean on the four changed paths. If the eventbus leg of AC-010 ever
  reaches its install half and F-11's file is involved, that file is still out of scope here.
- **T-010 implementation (S4.x)**: the five modules must (a) guard install, lazy create and reset with
  **one** module-level `threading.Lock` per module, mutually exclusive, with the `required=False` guarded
  read taking the same lock and creating nothing (REQ-006, ADR-084); (b) keep the owner's own lazy write
  direct — never via the public setter — and perform it under that lock (REQ-007, AC-011: exactly one
  traced entry/exit pair for the getter and **no** entry record for the install operation); (c) make
  install/reset a pair so the next `get_*()` builds a fresh default, session-management through
  `get_session_service(repository)` (REQ-008, AC-012); (d) hold the lock only for the slot read/swap — no
  construction, publication or `shutdown()` inside it, and emit the replace WARNING after the lock is
  released (NFR-003); (e) keep INV-001 intact — last-install-wins over any install/reset/read sequence and
  every install that replaced a non-empty slot logging its WARNING (EDGE-010). Search already has
  `_singleton_lock` (`src/backend/search/service.py:547`); session-management has **no** module lock at all
  (`src/backend/sessionmanagement/service.py`), which is why its lazy path is the one AC-009 cannot
  witness. If a witness exposes a divergence between two features, fix the module — do not relax the
  witness.
- **T-011** extends `tests/contract/singleton_install/` and may reuse
  `SingletonSlot.read_args()` / `concurrent_installs`; it must keep the `SingletonSlot` field order and the
  five `SLOTS` entries intact (T-009's and T-010's witnesses iterate `SLOTS` and assume exactly five).

### Next

S3.1 for **T-011**.

## S3.1 — T-011 test derivation (logging coverage — the five install operations) — 2026-10-07

**Step.** S3.1, one atomic step: derive **T-011's** `tests_to_create` and nothing else. No implementation, no
refactor, no other task's tests, no full suite, no push, no PROBLEMS.md entry, **no Phase 3 RED gate declared**
(that is S3.2). Skill: `.agents/skills/test/SKILL.md`, Phase 3 FEATURE / CROSS-CUTTING section.

**Task object re-read from `.github/task-runner/tasks.json` (the file wins, P-63).** `feature_group` "logging
coverage — the five install operations in the logging-coverage inventory"; `requirements` `[REQ-010]`;
`acceptance_criteria` `[AC-014, AC-015]`; `invariants` / `edge_cases` / `nfrs` all empty; `dependencies`
`[T-001, T-002, T-003, T-004, T-005, T-009]` (Phase 4 ordering only); `tests_to_create` exactly the two node IDs
below; `red_command` / `green_command` identical; `allowed_files.source_files` = the five feature modules
(**fix-only** — the decorator belongs to the owning module, T-011 adds no new tracing);
`allowed_files.test_files` = `tests/acceptance/singleton_install/test_install.py`,
`tests/singleton_install_test_helpers.py` (read-only), `tests/acceptance/logging_coverage/test_inventory.py`,
`tests/logging_coverage_test_helpers.py`; `design_constraints` — needs only T-001…T-005; **the
`docs/specs/logging-coverage.md` §3.1 table is the normative inventory and no existing inventory row may change**;
`@logged(slow_threshold_ms=5)`, default `include_args`, no local values in records; `completion_gates` — AC-014
witnesses entry + exit with elapsed ms; the inventory carries a row for each install operation and each traced
function; ruff clean on the changed paths; traceability PASS. **Verified field-for-field against the brief — no
invented task object.**

**The T-010 hand-off note is wrong about T-011 (finding F-63).** It says T-011 "extends
`tests/contract/singleton_install/`". T-011's `tests_to_create` and `allowed_files` name
`tests/acceptance/singleton_install/test_install.py` and `tests/acceptance/logging_coverage/test_inventory.py` —
nothing under `tests/contract/`. The DAG wins; the contract directory was left untouched.

### Files created / modified

| File | Change | Lines (after) |
|---|---|---|
| `tests/acceptance/singleton_install/test_install.py` | **modified** — `test_ac_014_install_is_traced` + `_witness_install_traced` appended after `_witness_install_reset_default`; `_traced_records` extracted and `_traced_pair` now delegates to it; `_INSTALL_SLOW_THRESHOLD_MS` added; `level_name` / `parse_elapsed_ms` imported read-only from `logging_coverage_test_helpers` | 334 (was 266) |
| `tests/acceptance/logging_coverage/test_inventory.py` | **modified** — `test_inventory_covers_install_operations` + `_spec_inventory_rows` + `_SPEC` / `_INSTALL_OPERATIONS` / `_INSTALL_SLOW_THRESHOLD_MS` / `_MIN_ROW_CELLS` added; module docstring extended | 104 (was 24) |
| `tests/singleton_install_test_helpers.py` | **not touched** (read-only per the DAG) — `SLOTS` already names the five installers | 499 |
| `tests/logging_coverage_test_helpers.py` | **not touched** — deliberately, see the interlock section | 172 |
| `src/backend/{settings/registry,eventbus/eventbus,permissions/service,search/service,sessionmanagement/service}.py` | **not touched** — fix-only in this task and nothing to fix yet: the install operations do not exist (T-001…T-005 not implemented) | — |

`git rev-parse --show-toplevel` =
`C:/workspace/active-projects/python-template_kopie-worktrees/crosscut/settings-public-registry-setter` beside
every count below.

### Interlock with `crosscut/structlog-logging` (PR #74) — exact lines

`git log -1 --format='%h %s' -- docs/specs/logging-coverage.md` →
`1dbddb6 docs(spec): P.4 draft CROSS-CUTTING spec + amend six approved specs` — the version this change's P.4
amended, and the version T-011's expectations come from. Nothing was fetched, merged or rebased, and no other
worktree was touched.

- `tests/acceptance/logging_coverage/test_inventory.py` — the **only** file this step changes that PR #74 also
  edits. Added lines: **7–13** (docstring paragraph), **18** (`import pathlib`), **25–63** (the four module
  constants + `_spec_inventory_rows`), **77–104** (`test_inventory_covers_install_operations`). Pre-existing
  lines **1–6**, **14–17**, **19–24**, **66–75** (`test_inventory_covers_all_public_classes`) are byte-identical
  to HEAD.
- `tests/logging_coverage_test_helpers.py` — **zero lines changed by this step.** The DAG puts the
  `INVENTORY_MODULE_FUNCTIONS` row additions in T-011's *implementation* step, not in derivation: the five
  missing rows are exactly the RED the AC-015 witness has to fail on (finding F-64). This shrinks the interlock
  footprint for T-011 to one file instead of two.
- `tests/acceptance/singleton_install/test_install.py` — new import edge
  `from logging_coverage_test_helpers import level_name, parse_elapsed_ms` (read-only; the helper itself is
  unmodified). The four helpers the AC-014 witness reuses are `parse_elapsed_ms` and `level_name` from
  `tests/logging_coverage_test_helpers.py`, and `SLOTS` / `SingletonSlot.installer` / `SingletonSlot.new` /
  `SingletonSlot.install` / `SingletonSlot.dispose` / `SingletonSlot.clear` from
  `tests/singleton_install_test_helpers.py`. Nothing was duplicated.

### Collection (no import/collection error)

`uv run pytest tests/acceptance/singleton_install/ tests/acceptance/logging_coverage/ --collect-only -q` →
**30 tests collected in 0.39s**, no errors — `test_install.py` 13 (12 pre-existing + AC-014),
`test_inventory.py` 2 (1 pre-existing + AC-015).

### RED gate for T-011 (observed; the Phase 3 gate itself is S3.2's)

`red_command` verbatim:

```
uv run pytest tests/acceptance/singleton_install/test_install.py::test_ac_014_install_is_traced tests/acceptance/logging_coverage/test_inventory.py::test_inventory_covers_install_operations -v
```

**2 failed in 0.58s** — reproduced **3×** (two default random-order runs, one `-p no:randomly`).

| Node | Failure reason (exact) |
|---|---|
| `…test_install.py::test_ac_014_install_is_traced` | `AssertionError: settings: set_settings_registry() does not exist, so it cannot be traced with @logged(slow_threshold_ms=5) (REQ-010)` / `assert None is not None` |
| `…test_inventory.py::test_inventory_covers_install_operations` | `AssertionError: the executable inventory has no 'module function' row for ['set_event_bus', 'set_permission_service', 'set_search_service', 'set_session_service', 'set_settings_registry'], which docs/specs/logging-coverage.md §3.1 lists (AC-015)` / `assert not [...]` |

**Why this is a valid RED.** Both are assertion failures on unimplemented behavior — the missing install
operations and the missing inventory rows — not a collection, import, fixture or test-data error (collection
clean above). The AC-014 witness resolves the installer with `getattr(slot.module, slot.installer, None)` and
asserts it is not None, so a missing installer is an `AssertionError`, never an `AttributeError` (finding
F-57/F-58 class of invalid RED avoided: no helper returns the wrong type, no `TypeError`). The AC-015 witness
fails on the five rows specifically, and its first assertion already proves the §3.1 table lists exactly those
five `module function` `set_*` rows — so the failure is "the executable inventory is behind the spec", not "the
spec changed".

### Anti-vacuity probes (scratch `_scratch_t011_probe.py`, deleted before the commit)

Out-of-band, exactly as T-010 did — the witnesses were driven against stand-ins to prove they fail for the right
reason and can pass:

| Probe | Witness outcome |
|---|---|
| AC-014, installer present but **undecorated** (correct name) | `FAIL: settings: set_settings_registry() exists but is not traced with @logged (REQ-010)` |
| AC-014, decorated with `slow_threshold_ms=50` | `FAIL: … slow_threshold_ms is 50.0, not 5 (docs/specs/logging-coverage.md §3.1 note)` |
| AC-014, decorated with `include_args=True` | `FAIL: settings: the entry record formats arguments or local values into the record: <…SettingsRegistry object at 0x…>` |
| AC-014, correct `@logged(slow_threshold_ms=5)` | **PASS** — records `['>> set_settings_registry called', '<< set_settings_registry returned in 0.001 ms', …]` (witness is satisfiable; exit at DEBUG; elapsed 0.001 ms ≪ 5 ms) |
| AC-015, rows absent (current state) | `FAIL: … no 'module function' row for [the five]` |
| AC-015, rows present but **untraced** | `FAIL: set_event_bus is not traced with @logged (AC-015)` |
| AC-015, rows present, `slow_threshold_ms=50` | `FAIL: set_event_bus is not traced with @logged(slow_threshold_ms=5) (…§3.1 note)` |
| AC-015, rows present and traced `@5` | **PASS** |
| AC-015, unrelated inventory churn only (added `set_unrelated`, replaced `get_settings`, removed `setup_logger`) | `FAIL: … no 'module function' row for [the five]` — the witness keys on the five rows, not on churn |

### Gates run

- `uv run ruff check <two changed paths>` → **All checks passed!** (after one scoped `--fix` for an import-block
  sort and one named constant for a magic value; `uv run ruff format <two changed paths>` → 1 reformatted, 1
  unchanged). No repo-wide sweep.
- `uv run python scripts/check_traceability.py` → **PASS (796 matrix rows, 136 spec IDs, 784 test functions)** —
  784 = the 782 recorded at T-010 plus the two functions derived here.
- `uv run complexipy <two changed paths> --max-complexity-allowed 15` → **All functions are within the allowed
  complexity** (max 10, `_spec_inventory_rows`; `test_inventory_covers_install_operations` 6,
  `_witness_install_traced` 1).
- AC-017 architecture scan (`uv run pytest tests/unit/architecture/test_singleton_slots.py -q`) →
  **1 failed, 2 passed**, still exactly **12 foreign singleton-slot write(s)** — the new tests plant no private
  slot write.
- No-regression proof, every earlier task's recorded `red_command` re-run (targeted, never the full suite):
  **T-001 10 failed · T-002 6 · T-003 6 · T-004 6 · T-005 6 · T-006 2 · T-007 1 failed + 2 passed · T-008 3 ·
  T-009 20 · T-010 6** — every count identical to its recorded value.
- Pre-existing logging-coverage tests: `uv run pytest tests/acceptance/logging_coverage/ -q` →
  **1 failed, 16 passed** — the single failure is the new AC-015 node; all 16 pre-existing nodes pass.
- Other consumers of the helper the new import edge touches
  (`tests/property/logging_coverage/ tests/unit/logging_coverage/ tests/acceptance/search/test_search.py
  tests/contract/search/test_search_contracts.py`) → **47 passed**.
- State leak: `md5sum data/permissions.db settings/values.yaml` identical before/after the T-011 run
  (`555e225f260ca009733a15d6a042a021`, `af81d2322fc8d15a398dc53a10391c1e`) — same values as the T-010 record.
  `git status --porcelain` after the run: only the two intended test files.
- `uv run mypy src/` not run — no `src/` file was touched by this step.

### Findings (for the Problem Log / after-workflow-optimization; no PROBLEMS.md entry written by this step)

- **F-63 — a hand-off note contradicted the DAG.** T-010's hand-off note listed
  `tests/contract/singleton_install/` as a file T-011 extends; T-011's `tests_to_create`/`allowed_files` name
  `tests/acceptance/singleton_install/test_install.py` and `tests/acceptance/logging_coverage/test_inventory.py`.
  Had the note been followed, the derivation would have written tests outside the task's allowed files. The DAG
  object is authoritative; re-read it per task (same class as P-63).
- **F-64 — derivation vs implementation in the DAG wording.** T-011's `implementation_steps` put the
  `INVENTORY_MODULE_FUNCTIONS` row additions in the same task as the witness. Adding them during S3.1 would have
  removed the exact RED the AC-015 witness must fail on. The rows are therefore left to the implementation step —
  which also keeps the `structlog-logging` interlock to one file.
- **F-65 — anchoring an inventory expectation to the spec, not to helper data.** A witness that compared
  `INVENTORY_MODULE_FUNCTIONS` against a list restated in the test would be satisfiable by editing test data.
  `_spec_inventory_rows()` parses the §3.1 table of `docs/specs/logging-coverage.md` (32 rows: 19 classes + 13
  module functions) and cross-checks it against the five names AC-015 names, so both the spec table and the
  executable inventory have to be right.
- **F-66 — `@logged` records carry `func.__qualname__`.** A witness that matches records on the public function
  name only works for module-level functions; the probe had to rename its stand-in **before** wrapping it. If an
  installer were ever nested, the record would name the qualname and the witness would miss it.
- **F-67 — the AC-014 exit-level assertion is timing-sensitive in principle.** `@logged(slow_threshold_ms=5)`
  escalates a slow call's exit record to WARNING, which would break "exit record at DEBUG". Measured 0.001 ms in
  the probe; the assertion is kept strict per AC-014 and the failure message carries the measured elapsed ms and
  the 5 ms threshold so any future flake is diagnosable rather than silent.
- **F-68 — repo-relative path in a test.** `_SPEC = pathlib.Path("docs/specs/logging-coverage.md")` depends on
  the pytest CWD being the repo root — the established pattern in this directory
  (`Path("src/backend")`, `Path("src/main.py")`), noted because it is a rootdir dependency, not a bug.

### Not done in this step (deliberate)

No implementation in the five feature modules (fix-only, and there is nothing to fix before T-001…T-005 exist);
no `@logged` added anywhere; no inventory row added; no other task's tests derived; no full suite; no push; no
PROBLEMS.md entry; **no Phase 3 RED gate declared**. **T-012 was not touched** — it is human-blocked by the open
D13 decision.

### Hand-off for S3.2 (Phase 3 ruff + RED gate)

Derived node IDs per task (the DAG's `tests_to_create`), with the RED count each task's `red_command` reproduces
— note that every `red_command` also names pre-existing nodes the task must repair, so the count is of the
command, not of the derived nodes:

| Task | Derived node IDs (`tests_to_create`) | `red_command` RED |
|---|---|---|
| T-001 | 7: `test_ac_001_install_then_get_returns_instance`, `test_ac_040_set_settings_registry_installs_default`, `test_ac_041_replace_logs_one_warning`, `test_ac_042_concurrent_install_and_read`, `test_ac_043_install_then_reset_then_default`, `test_inv_011_last_install_wins`, `test_edge_033_concurrent_lazy_create` | 10 failed (10 nodes) |
| T-002 | 2: `test_ac_016_install_then_reset_then_default`, `test_edge_012_concurrent_lazy_create` | 6 failed (6 nodes) |
| T-003 | 2: `test_ac_044_install_then_reset_then_default`, `test_concurrent_lazy_create` | 6 failed (6 nodes) |
| T-004 | 2: `test_ac_041_install_then_reset_then_default`, `test_edge_023_concurrent_install_and_lazy_create` | 6 failed (6 nodes) |
| T-005 | 2: `test_ac_049_install_then_reset_then_default`, `test_edge_014_install_over_nonempty_default` | 6 failed (6 nodes) |
| T-006 | 2: `test_ac_016_main_installs_through_setter`, `test_installed_registry_serves_feature_registration` | 2 failed (2 nodes) |
| T-007 | 3 architecture nodes | 1 failed, 2 passed (3 nodes) |
| T-008 | 1: `test_nfr_004_ruff_and_mypy_clean` | 3 failed (3 nodes) |
| T-009 | 5: `test_ac_013_install_publishes_no_event`, `test_nfr_001_public_api_additive`, `test_nfr_002_install_latency`, `test_edge_007_reset_event_bus_still_shuts_down`, `test_inv_003_no_events_and_no_rebinding` | 20 failed (20 nodes) |
| T-010 | 3: `test_nfr_003_slot_lock_is_short_lived`, `test_ac_012_install_then_reset_then_default`, `test_inv_001_last_install_wins` | 6 failed (6 nodes) |
| **T-011** | 2: `tests/acceptance/singleton_install/test_install.py::test_ac_014_install_is_traced`, `tests/acceptance/logging_coverage/test_inventory.py::test_inventory_covers_install_operations` | **2 failed (2 nodes)** |
| T-012 | **BLOCKED-USER — not derived** (open D13 decision; do not touch) | — |

S3.2 must: run `uv run ruff check` on the changed paths of every derived test (the two T-011 paths are already
clean), re-run each task's `red_command` and record the Phase 3 RED gate once in this file using
`docs/verification/TDD-evidence-template.md`, and update `docs/verification/traceability.md` with the T-011 rows
(AC-014 → `test_ac_014_install_is_traced`, AC-015 → `test_inventory_covers_install_operations`). The row to
update is `docs/verification/traceability.md:934` —
`| REQ-010 | AC-014, AC-015 | — | PENDING (settings-public-registry-setter P.4, 2026-10-06) |` — the only row of
this change's spec that T-011 supplies evidence for. (`check_traceability.py` already PASSes because the row
exists; it enforces referential integrity, not status freshness.)

Still open defects S3.2 owns:

- **F-11** — `tests/acceptance/eventbus/test_eventbus.py::_concurrent_install_read_reset` has a
  `_run(action)` signature mismatch (scheduled for S3.2).
- **F-56** — the widened lazy-create window must cover every lazy leg including search (already applied in
  `widened_lazy_create_window`; sensitivity 1 distinct read with `_singleton_lock` vs 8 without).
- **F-63** — the T-010 hand-off note's wrong "extends" list for T-011 (this record supersedes it).

Interlock lines changed by T-011 (for the later `crosscut/structlog-logging` merge): only
`tests/acceptance/logging_coverage/test_inventory.py` lines **7–13, 18, 25–63, 77–104**;
`tests/logging_coverage_test_helpers.py` untouched by this step.
