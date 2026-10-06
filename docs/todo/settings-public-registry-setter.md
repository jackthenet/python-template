# TODO: settings-public-registry-setter

Backlog item for one planned change, created at **P.1 Frame** from the template.

This is a **planning record, not normative**: like `docs/questions/`, it is committed directly to `main` (see "Phase P: PREPARE" in `AGENTS.md`). It carries no approval gate — the spec does.

- **Status:** QUESTIONS-ANSWERED  <!-- PREPARING | QUESTIONS-ANSWERED | READY | IN-WORKFLOW | WAITING | MERGED -->
- **Change type:** **CROSS-CUTTING**  <!-- reclassified from FEATURE at P.3 on 2026-10-06 (Q-2 = all five module singletons): the change intentionally spans five features and introduces a new shared pattern (a public install operation on a feature's module singleton) -->
- **Created:** 2026-10-04
- **Question file:** `docs/questions/settings-public-registry-setter.md`
- **Spec:** **six amendments required** — `docs/specs/settings.md` (REQ-014 names only `get_settings_registry()` / `reset_settings_registry()`), plus `event-bus.md`, `user-roles-permissions.md`, `search.md`, `session-management.md` (each specifies its own singleton accessor with no install operation), plus `logging-coverage.md` §3.1 (REQ-001's normative inventory must list the new public module functions — Q-15)
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

## In scope (settled by P.3 — all 29 questions answered, see the question file)
- **The operation.** A public `set_settings_registry(registry)` on `backend.settings`, plus four siblings (`set_event_bus`, `set_permission_service`, `set_search_service`, `set_session_service`) — one per singleton-owning feature, each specified by an amendment to its own spec with **new REQ/AC/EDGE IDs beside** the existing singleton requirement (Q-1, Q-2, Q-4, Q-6). Parameter type = the concrete class; return `None`; no `None` argument (Q-7, Q-9).
- **Semantics.** Replace unconditionally, **WARNING** when the slot was already occupied (Q-5). Not retroactive: later `get_*()` calls see the new instance, already-constructed consumers keep theirs — stated in the REQ + one AC (Q-22). No event published; `settings.md` D7 stays (Q-29). No runtime type check — annotation + `mypy src/` (Q-23).
- **Concurrency.** A module-level `threading.Lock` per feature guards **all three** slot operations (install / lazy create / reset), mirroring `search/service.py:547,558,571` (Q-10, Q-11). Specified as an AC in Given/When/Then form, not an INV (Q-12). The owner module's lazy path keeps its direct write, still under the lock (Q-13).
- **Tracing.** `@logged(slow_threshold_ms=5)` on each new function, default `include_args` — identical to its neighbours (Q-14); a §3.1 row per function in `logging-coverage.md` (Q-15).
- **Migration.** `src/main.py` (install at `:137-138`, same module-import position — Q-21) then **reads the global back** at the consumer sites (Q-20); 9 settings test sites (Q-16); the 2 `tests/eventbus_test_helpers.py:77,84` sites (Q-27); and the 3 writes embedded in `python -c` programs in `test_wiring.py:17-18` / `test_setup_logger.py:31,55` (Q-17).
- **Guard.** Both forms (Q-18): a `tests/unit/` scan for cross-package private-slot writes (CI-enforced for free via the existing `pytest tests/` jobs) **and** ruff `TID251` banned-api entries in `pyproject.toml` for `_registry` + the four sibling slots. Ban width = the private slot only (Q-19).
- **Docs.** One bullet per feature in `AGENTS.md`'s five "Using the …" sections (Q-26). Version bump **`minor` → 0.7.0** at S6.4 (Q-25).

## Out of scope
- Any change to settings **value/template** behavior, kinds, validation, storage or events.
- The other three import fixes (already done in `architecture-tests-missing`).
- Registry construction order or the lazy `UserManager`/`PermissionService` proxies in `src/main.py` (unchanged wiring semantics).
- **Deferred to new TODOs opened at P.3 (2026-10-06):** `public-api-import-boundary` — the wider convention that a feature's package `__init__` is the only import surface, with a self-import exemption (Q-19); `composition-root-factory` — giving `src/main.py` a callable composition root instead of 221 lines of module-level wiring (Q-21).
- Making the install propagate to already-constructed consumers (Q-22 declined: needs new API in three features).

## Affected features
`src/backend/settings/` (public API + spec), `src/backend/eventbus/`, `src/backend/permissions/`, `src/backend/search/`, `src/backend/sessionmanagement/` (sibling install operation + spec amendment), `src/main.py` (composition root), `tests/**` (6 files, 9 settings sites + `tests/eventbus_test_helpers.py:77,84`).

## Constraints and risks
- **Spec amendment first.** Per the Spec Amendment Workflow, `docs/specs/settings.md` must change through its own PR (Changelog entry, new IDs) before implementation.
- **Singleton semantics.** `get_settings_registry()` lazily creates an instance; a setter must define what happens on double-install and how it interacts with `reset_settings_registry()` and the lazy path (the `@logged`/`@logged_class` tracing rules apply to the new public function).
- **Test-suite blast radius.** 9 test sites depend on the current private write; the migration must not weaken any test.
- **Do not reorder startup wiring** while re-pointing `src/main.py`.

## Acceptance signal (plain language)
No code outside a feature package writes that feature's singleton slot: `rg "_registry\\[0\\]\\s*=" src tests` and the four sibling equivalents return nothing, and a build fails if such a write returns (the `tests/unit/` scan + ruff `TID251`). The composition root installs its wired registry through a public call and the composed application behaves exactly as before (full suite green, no test weakened); each of the six amended specs names its setter with an AC and a GREEN test.

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
| P.3 Answer (rounds 1–10: Q-1 … Q-29) | 2026-10-06 | **COMPLETE — 29 of 29 ANSWERED and incorporated** (10 `ask_user_question` rounds; two rounds re-asked after the user asked for evidence: Q-18/Q-19 in round 6, Q-21/Q-22/Q-23 in round 8). Decisions are recorded in the "In scope" section above, keyed by question ID. Two questions spawned new backlog items instead of widening this change: **Q-19 → `public-api-import-boundary`**, **Q-21 → `composition-root-factory`** (both P.1-framed on `main`, REFACTOR, 3/5, implement). Two corrections the answers forced: the guard's option 3 was wrong (`quality_check` at `pyproject.toml:224` is a local uv alias, **no CI job runs it**; `scripts/check_traceability.py` has its own job in `spec-validation.yml`), and Q-27's premise ("one spec only") was void once Q-2 took all five singletons. TODO advanced to **QUESTIONS-ANSWERED**; next step is **P.4** (create `crosscut/settings-public-registry-setter` worktree + draft the six spec amendments with the Impact Analysis).
| P.3 round 1 detail (Q-1 … Q-4) | 2026-10-06 | 4 of 29 ANSWERED in the first round (superseded by the row above — all 29 are answered). **Q-1 = public setter** (rejected pure DI: the `PermissionService`↔`UserManager` and `SettingsRegistry`↔`PermissionService` cycles survive DI, the globals are in-feature fallbacks, and the singleton is specified behavior in REQ-013/014/020). **Q-2 = all five singletons** → **reclassified CROSS-CUTTING** (section above). **Q-3 = one PR** — the S1.4 approval PR carries the five amended specs (precedent: `structlog-logging` v4). **Q-4 = new REQ beside** the existing singleton REQ (`REQ-026` in `settings.md`, next free IDs REQ-026/AC-040/INV-011/EDGE-030/NFR-005), AC-018's dated row untouched (Convention B). |
| P.4 Draft spec | | |
| P.5 Self-consistency | | |
