# TODO: public-api-import-boundary

Backlog item for one planned change, created at **P.1 Frame** from this template and named `public-api-import-boundary.md`. One file per change.

This is a **planning record, not normative**: like `docs/questions/`, it is committed directly to `main` (see "Phase P: PREPARE" in `AGENTS.md`). It carries no approval gate — the spec does.

- **Status:** PREPARING  <!-- PREPARING | QUESTIONS-ANSWERED | READY | IN-WORKFLOW | WAITING | MERGED | DROPPED -->
- **Change type:** REFACTOR  <!-- P.2 may reclassify: if new public exports are required, FEATURE -->
- **Created:** 2026-10-06
- **Question file:** `docs/questions/public-api-import-boundary.md`
- **Spec:** n/a (REFACTOR) — the normative basis is the GREEN baseline + the refactor scope recorded in `docs/verification/public-api-import-boundary.md`
- **Worktree:** <created at P.4> `../python-template_kopie-worktrees/refactor/public-api-import-boundary`
- **Depends on:** `structlog-logging` (IN-WORKFLOW — it rewrites imports inside `src/backend/logging/` and amends `docs/specs/logging-coverage.md`), `settings-public-registry-setter` (its private-slot guard + ruff `TID251` block land first; this change widens that ban)
- **Related specs:** `docs/specs/logging-coverage.md` (its §3.1 inventory names the traced functions whose import sites move), plus every spec whose feature exposes a public API consumed across features

## Goal (one line)

Make each feature's package `__init__` the **only** import surface other code may use, and guard it — so a feature can restructure its internal modules without touching any consumer.

## Why

`architecture-tests-missing` (MERGED) fixed four private-module imports by hand and recorded at its Q-4 that no CI boundary rule would be enforced; the rule ("features expose explicit public interfaces; other features should not import internal implementation details") is still unguarded and still violated in a milder form: consumers import **public symbols from internal module paths** instead of from the package. Six test files import from `backend.settings.registry` directly, and features import each other's non-underscore modules. The `settings-public-registry-setter` change bans only the private **slot** (`_registry` and its four siblings) and explicitly deferred this wider rule to its own change (its Q-19 answer, 2026-10-06).

## In scope

- Enumerate cross-package imports of `backend.<feature>.<module>` (and `frontend` equivalents) and migrate them to `backend.<feature>` package imports.
- Add the missing re-exports to the affected `__init__.py` files where a needed public symbol is not yet exported.
- Widen the regression guard: the `tests/unit/` boundary scan from `settings-public-registry-setter` plus ruff `TID251` banned-api entries for cross-package module-path imports, **with a self-import exemption** (a feature may import its own modules; its tests may import its private modules).
- Decide and record the exemption mechanics (per-file `noqa`, `[tool.ruff.lint.per-file-ignores]`, or a rule in the scan test).

## Out of scope

- Any change to runtime behavior, public API semantics, or signatures.
- The private-slot ban itself — already owned by `settings-public-registry-setter`.
- Reorganising feature internals (moving/renaming modules) — this change only makes that safe later.

## Affected features

All of `src/backend/*` and `src/frontend/*` as **consumers**; the `__init__.py` of every feature that gains a re-export. Test-side: `tests/acceptance/logging_coverage/*` (6 sites), plus whatever the enumeration finds.

## Constraints and risks

- Must not collide with `structlog-logging` (it edits `src/backend/logging/` and `logging-coverage.md`) — hence the `Depends on:`.
- The self-import exemption is the hard part: without it the guard fails every feature's own tests. Decide it before writing the guard.
- REFACTOR gate: the full suite must stay GREEN with **zero test changes** — but migrating a test's import *is* a test edit, so the scope must state that import-path edits are the only permitted test changes (behaviour assertions untouched).
- ruff `TID251` additions must leave the whole-repo sweep clean at Phase 5.

## Value triage (2026-10-06, pre-workflow)

- **Overlap:** `architecture-tests-missing` (MERGED) — its Q-4/Q-5 fixed 4 private-module imports by hand and deliberately left the boundary rule manual; this TODO is the follow-up that rule was deferred to, not a duplicate of it. Partially overlaps the guard added by `settings-public-registry-setter` (Q-18/Q-19), which covers only the private slot and explicitly deferred the wider convention. Extend that guard rather than write a second one.
- **Beneficiary:** the people who change this codebase later (including the agent): a feature can rename or split its internal modules without a cross-feature hunt, and a boundary violation fails a build instead of a review. End-user value is indirect (fewer broken builds, cheaper refactors).
- **Score: 3/5** — real architectural value and it reuses a guard that already exists, but it is partly overlapping, its diff spans many test files, and it collides with an in-flight change until `structlog-logging` merges.
- **Recommendation:** implement — as its own change, sequenced after `structlog-logging` and `settings-public-registry-setter`.
- **Decision:** implement — requested by the user on 2026-10-06 as the answer to `settings-public-registry-setter` Q-19 ("1 but add a new todo for the wider convention").

## Acceptance signal (plain language)

`rg "from backend\.[a-z_]+\.[a-z_]+ import" src/ tests/` returns only imports a package makes of its own modules, and a build fails if anyone reaches into another feature's module path again. Nothing about the running system changes: the full suite is GREEN with no behaviour assertion edited.

## Prep log
| Step | Date | Result |
|---|---|---|
| P.1 Frame | 2026-10-06 | classified REFACTOR; TODO + question file created; value triage recorded (3/5, implement) |
| P.2 Interrogate (<n> questions) | | |
| P.3 Answer (<n> answered) | | |
| P.4 Draft spec / triage / baseline / scope | | |
| P.5 Self-consistency (FEATURE/CROSS-CUTTING) | | |
