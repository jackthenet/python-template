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
