# TODO: composition-root-singleton-install

Backlog item for one planned change, created at **P.1 Frame** from this template and named `composition-root-singleton-install.md`. One file per change.

This is a **planning record, not normative**: like `docs/questions/`, it is committed directly to `main` (see "Phase P: PREPARE" in `AGENTS.md`). It carries no approval gate — the spec does.

- **Status:** PREPARING  <!-- PREPARING | QUESTIONS-ANSWERED | READY | IN-WORKFLOW | WAITING | MERGED | DROPPED -->
- **Change type:** FEATURE  <!-- P.2 must confirm: ISSUE if an approved spec already requires the composition root to install the shared defaults, FEATURE if it only says the getters are "for application use" -->
- **Created:** 2026-10-10
- **Question file:** `docs/questions/composition-root-singleton-install.md`
- **Spec:** `docs/specs/composition-root-singleton-install.md`  <!-- FEATURE: draft at P.4; may instead become a Spec Amendment of session-management/permissions if P.2 finds the requirement already stated -->
- **Worktree:** <created at P.4> `../python-template_kopie-worktrees/feature/composition-root-singleton-install`
- **Depends on:** `settings-public-registry-setter` (IN-WORKFLOW — it adds the public `set_*` install operations this change calls); `composition-root-factory` (recommended sequencing, not a hard dependency)
- **Related specs:** `docs/specs/session-management.md` (REQ-020 "module singleton `get_session_service()` for application use", REQ-023 `set_session_service`), `docs/specs/settings-public-registry-setter.md` (REQ-011 composition-root install pattern), `docs/specs/permissions.md`

## Goal (one line)
Have `src/main.py` install the `PermissionService` and `SessionService` it wires as the shared defaults, so `get_permission_service()` / `get_session_service()` return the wired instances instead of building different ones.

## Why
Measured at `main` (2026-10-10): `src/main.py` constructs the permission and session services locally, but never calls `set_permission_service(...)` or `set_session_service(...)` — `grep -rn "set_permission_service\|set_session_service" src/` finds only the definitions (`src/backend/permissions/service.py`, `src/backend/sessionmanagement/service.py`) and their `__init__` re-exports, no call site. Any code that reaches a service through the documented module singleton therefore gets a **second, differently-configured instance** (its own repository, its own settings registry, no event bus). Nothing in `src/` calls those getters today, so the defect is latent — it becomes real the moment `backend-api` / `api-keys` / `notifications` consume the singletons, which is exactly what those specs plan to do.

`composition-root-factory` P.2 (Q-15) measured the same gap and recommended keeping it out of that change as a separate TODO.

## In scope
- The composition root installs each service it constructs through the feature's public install operation.
- An acceptance witness proving `get_*_service()` returns the instance the composition root wired (the same shape as `settings-public-registry-setter` AC-016).

## Out of scope
- Extracting `build_composition_root()` (`composition-root-factory`).
- Adding new install operations to features that do not have one.
- Changing any service's construction arguments.

## Affected features
`src/main.py`; `src/backend/permissions/`, `src/backend/sessionmanagement/` (no code change expected there — their install operations already exist).

## Constraints and risks
- Installing over a non-empty slot logs one WARNING by spec (`session-management.md` REQ-023 / `settings-public-registry-setter` D2): a test that imports `main` twice will emit it, which some witnesses may assert on.
- The install is **not retroactive** — consumers that already hold a reference keep it; ordering inside `src/main.py` matters.
- `src/main.py` is pinned by `settings-public-registry-setter` REQ-011/AC-016 (line pins + source scan) — merge after it.
- `composition-root-factory` P.2 measured that a second wiring pass is silently stale for the search singleton; the install order must not depend on a lazy first call.

## Value triage (2026-10-10, pre-workflow)
- **Overlap:** partial — `settings-public-registry-setter` REQ-011 installs only the **settings** registry, not the services; `composition-root-factory` Q-15 explicitly excludes this. Extending REQ-011 instead of a new change is the alternative P.2 must weigh.
- **Beneficiary:** future feature consumers (`backend-api`, `api-keys`, `notifications`) get one correctly-configured service per process instead of an accidental second one — the class of bug where a permission check uses a different principal store than the wiring.
- **Score: 3/5** — real value and small diff, but the defect is latent today (no `src/` caller of the getters) and it partly overlaps two other changes that must land first.
- **Recommendation:** implement (after `settings-public-registry-setter` merges; P.2 should decide whether it is cheaper as an extension of that change's REQ-011)
- **Decision:** <the user's answer + date>  <!-- recorded when the user answers; a dropped TODO moves to docs/todo/archive/ with its question file -->

## Acceptance signal (plain language)
After running the composition root, `get_permission_service()` and `get_session_service()` return the very objects `src/main.py` built (identity check), and a test fails if a later change drops an install.

## Prep log
| Step | Date | Result |
|---|---|---|
| P.1 Frame | 2026-10-10 | classified FEATURE (P.2 to confirm ISSUE vs FEATURE); measured no `set_permission_service` / `set_session_service` call site anywhere in `src/` |
| P.2 Interrogate (<n> questions) | | |
| P.3 Answer (<n> answered) | | |
| P.4 Draft spec / triage / baseline / scope | | |
| P.5 Self-consistency (FEATURE/CROSS-CUTTING) | | |
