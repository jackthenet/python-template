# TODO: settings-public-registry-setter

Backlog item for one planned change, created at **P.1 Frame** from the template.

This is a **planning record, not normative**: like `docs/questions/`, it is committed directly to `main` (see "Phase P: PREPARE" in `AGENTS.md`). It carries no approval gate — the spec does.

- **Status:** PREPARING  <!-- PREPARING | QUESTIONS-ANSWERED | READY | IN-WORKFLOW | WAITING | MERGED -->
- **Change type:** **CROSS-CUTTING**  <!-- reclassified from FEATURE at P.3 on 2026-10-06 (Q-2 = all five module singletons): the change intentionally spans five features and introduces a new shared pattern (a public install operation on a feature's module singleton) -->
- **Created:** 2026-10-04
- **Question file:** `docs/questions/settings-public-registry-setter.md`
- **Spec:** **five amendments required** — `docs/specs/settings.md` (REQ-014 names only `get_settings_registry()` / `reset_settings_registry()`), plus `event-bus.md`, `user-roles-permissions.md`, `search.md`, `session-management.md` (each specifies its own singleton accessor with no install operation)
- **Worktree:** <created at P.4> `../python-template_kopie-worktrees/crosscut/settings-public-registry-setter` (branch `crosscut/settings-public-registry-setter`)
- **Depends on:** `architecture-tests-missing` — **satisfied** (MERGED, PR #65 → `4f684f8`). Rebase expected on `structlog-logging` (IN-WORKFLOW): it amends `docs/specs/settings.md` at v4 and rewrites statements inside `src/backend/settings/registry.py`
- **Related specs:** `docs/specs/settings.md` (REQ-014 singleton surface), `docs/specs/settings-coverage.md` (REQ-012/AC-016/EDGE-011 guarded read), `docs/specs/event-bus.md`, `docs/specs/user-roles-permissions.md`, `docs/specs/search.md`, `docs/specs/session-management.md`

## Goal (one line)
Give the settings feature a **public** way to install the shared `SettingsRegistry` singleton, so the composition root and the tests stop reaching into the private `_registry` list.

## Why
Found at **P.4 of `architecture-tests-missing`** (finding F-1, recorded in `docs/verification/architecture-tests-missing.md`). That change fixed 3 of the 4 private-module import sites Q-5 named; the fourth cannot be fixed as a chore:

- `src/main.py:67` does `from backend.settings._setup import _registry` and then assigns `_registry[0] = <the proxy-wired SettingsRegistry>` (`src/main.py:136-137`) in order to install the composition root's wired instance as the shared singleton.
- The feature's public surface (`src/backend/settings/__init__.py`, spec REQ-014) offers only `get_settings_registry()` — which **lazily creates a default** `SettingsRegistry()` with no `permission_service` — and `reset_settings_registry()`. Substituting either for the private write **discards the wired instance**, i.e. a behavior change, which is exactly what a DOCS/CHORE may not do.
- The same private write is repeated in **6 test files at 9 sites** (`_registry[0]`), so the leak is not one-off: the private singleton slot is the de-facto injection point for the whole test suite.

Consequence today: the composition root and the tests depend on an internal implementation detail of another feature, which the project's own architecture rule forbids (`AGENTS.md`: features expose public interfaces; `docs/specs/settings.md` REQ-014 does not sanction the private write).

## Reclassification (P.3, 2026-10-06)
Q-2 was answered **all five singletons now**, so per the Escalation Rules the change is **CROSS-CUTTING**: it spans `settings`, `eventbus`, `permissions`, `search` and `sessionmanagement` and introduces a new shared pattern. Consequences: the spec carries an **Impact Analysis** grouped by feature; **ADRs** are required (new pattern + cross-feature interface); Phase 2 groups the task DAG by affected feature; Phase 5 additionally updates every affected feature's traceability rows; the version bump is **`minor`**. To be recorded in `docs/verification/settings-public-registry-setter.md` at P.4.

## In scope (settled by P.3 — see the question file)
- A public install operation on **each of the five** singleton-owning features (e.g. `set_settings_registry(registry)` and four siblings), each specified by an amendment to its own spec with **new REQ/AC/EDGE IDs beside** the existing singleton requirement (Q-1, Q-2, Q-4).
- Re-point `src/main.py` and the 6 test files / 9 `_registry[0]` sites at the public API.
- Deprecate/remove the private-slot write from outside the package.

## Out of scope
- Any change to settings **value/template** behavior, kinds, validation, storage or events.
- The other three import fixes (already done in `architecture-tests-missing`).
- Registry construction order or the lazy `UserManager`/`PermissionService` proxies in `src/main.py` (unchanged wiring semantics).

## Affected features
`src/backend/settings/` (public API + spec), `src/backend/eventbus/`, `src/backend/permissions/`, `src/backend/search/`, `src/backend/sessionmanagement/` (sibling install operation + spec amendment), `src/main.py` (composition root), `tests/**` (6 files, 9 settings sites + `tests/eventbus_test_helpers.py:77,84`).

## Constraints and risks
- **Spec amendment first.** Per the Spec Amendment Workflow, `docs/specs/settings.md` must change through its own PR (Changelog entry, new IDs) before implementation.
- **Singleton semantics.** `get_settings_registry()` lazily creates an instance; a setter must define what happens on double-install and how it interacts with `reset_settings_registry()` and the lazy path (the `@logged`/`@logged_class` tracing rules apply to the new public function).
- **Test-suite blast radius.** 9 test sites depend on the current private write; the migration must not weaken any test.
- **Do not reorder startup wiring** while re-pointing `src/main.py`.

## Acceptance signal (plain language)
`rg "from backend.settings._setup import" src tests` returns nothing; the composition root installs its wired registry through a public call and the composed application behaves exactly as before (full suite green, no test changed in behavior); the settings spec names the setter with an AC and a GREEN test.

## Value triage
- **Overlap:** none — no existing public setter exists (verified at ATM P.4: `__init__.py` exports `get_settings_registry` / `reset_settings_registry` only).
- **Beneficiary:** the composition root and every test that injects a registry; future features that need to install a configured singleton.
- **Score:** 3/5 — removes a cross-feature private-dependency violation that recurs in 10 call sites, but it changes no user-visible behavior and needs a spec amendment to do it properly.
- **Recommendation:** schedule after `architecture-tests-missing` merges; do not fold into a chore.

## Prep log
| Step | Date | Result |
|---|---|---|
| P.1 Frame | 2026-10-04 | TODO + question file created on `main`; type **FEATURE** (provisional — new public API + `docs/specs/settings.md` REQ-014 amendment). Discovered as finding **F-1** during `architecture-tests-missing` P.4 (record: `docs/verification/architecture-tests-missing.md`, commit `b9afe76`); evidence: `src/main.py:67` + `:136-137`, `src/backend/settings/__init__.py`, REQ-014, 9 `_registry[0]` sites in 6 test files |
| P.2 Interrogate (29 questions) | 2026-10-05 | **BLOCKED-USER** — 29 questions (**Q-1 … Q-29**) recorded in `docs/questions/settings-public-registry-setter.md`, one batch, most-blocking first (Q-1 fix shape: setter vs DI vs test-only override; Q-2 settings-only vs all five singletons → classification; Q-3 amendment PR count; Q-4 new REQ-026 vs amending REQ-014 in place). Feature brief recorded in the preamble. **`Depends on:` satisfied** — `architecture-tests-missing` is MERGED (`4f684f8`). **Two citations in this TODO are wrong and must be restated at P.4**: there is **no `src/backend/settings/_setup.py`** (the private slot is `_registry` at `src/backend/settings/registry.py:45`; `_setup.py` belongs to `backend.logging`), so the acceptance grep `from backend.settings._setup import` matches nothing even while the violation is present; and `src/main.py` drifted by one line (import `:68`, install `:137-138`). Re-measured: **10** outside-package writes (1 in `src/main.py` + 9 in 6 test files), 3 inside the owner module, the same private-list pattern in **5** features with **no** `set_*` setter anywhere, and only `search` guards lazy creation with a lock |
| P.3 Answer (round 1: Q-1 … Q-4) | 2026-10-06 | **IN PROGRESS — 4 of 29 ANSWERED.** **Q-1 = public setter** (rejected pure DI: the `PermissionService`↔`UserManager` and `SettingsRegistry`↔`PermissionService` cycles survive DI, the globals are in-feature fallbacks, and the singleton is specified behavior in REQ-013/014/020). **Q-2 = all five singletons** → **reclassified CROSS-CUTTING** (section above). **Q-3 = one PR** — the S1.4 approval PR carries the five amended specs (precedent: `structlog-logging` v4). **Q-4 = new REQ beside** the existing singleton REQ (`REQ-026` in `settings.md`, next free IDs REQ-026/AC-040/INV-011/EDGE-030/NFR-005), AC-018's dated row untouched (Convention B). 25 questions remain (Q-5 … Q-29), 4 per round |
| P.4 Draft spec | | |
| P.5 Self-consistency | | |
