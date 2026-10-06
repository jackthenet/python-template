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
