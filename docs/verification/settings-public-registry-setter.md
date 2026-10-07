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
