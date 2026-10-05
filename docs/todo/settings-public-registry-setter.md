# TODO: settings-public-registry-setter

Backlog item for one planned change, created at **P.1 Frame** from the template.

This is a **planning record, not normative**: like `docs/questions/`, it is committed directly to `main` (see "Phase P: PREPARE" in `AGENTS.md`). It carries no approval gate — the spec does.

- **Status:** PREPARING  <!-- PREPARING | QUESTIONS-ANSWERED | READY | IN-WORKFLOW | WAITING | MERGED -->
- **Change type:** FEATURE  <!-- provisional: a new public API on the settings feature + an amendment to docs/specs/settings.md REQ-014; P.2/P.3 may reclassify as a Spec Amendment (ISSUE-adjacent) or REFACTOR -->
- **Created:** 2026-10-04
- **Question file:** `docs/questions/settings-public-registry-setter.md`
- **Spec:** `docs/specs/settings.md` — **amendment required** (REQ-014 currently specifies only `get_settings_registry()` / `reset_settings_registry()`)
- **Worktree:** <created at P.4> `../python-template_kopie-worktrees/feature/settings-public-registry-setter`
- **Depends on:** `architecture-tests-missing` (`chore/architecture-tests-missing`, PR pending) — it records the finding that produced this item and leaves `src/main.py:67` as-is
- **Related specs:** `docs/specs/settings.md` (REQ-014 singleton surface)

## Goal (one line)
Give the settings feature a **public** way to install the shared `SettingsRegistry` singleton, so the composition root and the tests stop reaching into the private `_registry` list.

## Why
Found at **P.4 of `architecture-tests-missing`** (finding F-1, recorded in `docs/verification/architecture-tests-missing.md`). That change fixed 3 of the 4 private-module import sites Q-5 named; the fourth cannot be fixed as a chore:

- `src/main.py:67` does `from backend.settings._setup import _registry` and then assigns `_registry[0] = <the proxy-wired SettingsRegistry>` (`src/main.py:136-137`) in order to install the composition root's wired instance as the shared singleton.
- The feature's public surface (`src/backend/settings/__init__.py`, spec REQ-014) offers only `get_settings_registry()` — which **lazily creates a default** `SettingsRegistry()` with no `permission_service` — and `reset_settings_registry()`. Substituting either for the private write **discards the wired instance**, i.e. a behavior change, which is exactly what a DOCS/CHORE may not do.
- The same private write is repeated in **6 test files at 9 sites** (`_registry[0]`), so the leak is not one-off: the private singleton slot is the de-facto injection point for the whole test suite.

Consequence today: the composition root and the tests depend on an internal implementation detail of another feature, which the project's own architecture rule forbids (`AGENTS.md`: features expose public interfaces; `docs/specs/settings.md` REQ-014 does not sanction the private write).

## In scope (to be settled by P.2/P.3)
- A public setter on the settings feature (e.g. `set_settings_registry(registry)`), specified by an **amendment to `docs/specs/settings.md` REQ-014** with its own REQ/AC IDs, semantics (replace vs. create-if-absent, idempotence, thread-safety with the existing lazy creation) and error contract.
- Re-point `src/main.py` and the 6 test files / 9 `_registry[0]` sites at the public API.
- Deprecate/remove the private-slot write from outside the package.

## Out of scope
- Any change to settings **value/template** behavior, kinds, validation, storage or events.
- The other three import fixes (already done in `architecture-tests-missing`).
- Registry construction order or the lazy `UserManager`/`PermissionService` proxies in `src/main.py` (unchanged wiring semantics).

## Affected features
`src/backend/settings/` (public API + spec), `src/main.py` (composition root), `tests/**` (6 files, 9 sites).

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
| P.3 Answer | | |
| P.4 Draft spec | | |
| P.5 Self-consistency | | |
