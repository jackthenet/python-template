# TODO: composition-root-factory

Backlog item for one planned change, created at **P.1 Frame** from this template and named `composition-root-factory.md`. One file per change.

This is a **planning record, not normative**: like `docs/questions/`, it is committed directly to `main` (see "Phase P: PREPARE" in `AGENTS.md`). It carries no approval gate — the spec does.

- **Status:** WAITING  <!-- PREPARING | QUESTIONS-ANSWERED | READY | IN-WORKFLOW | WAITING | MERGED | DROPPED -->
- **Change type:** CROSS-CUTTING  <!-- reclassified from REFACTOR at P.3 round 1, 2026-10-10 (Q-01 = A): `import main`'s side effects are externally observable and two approved specs' ACs pin module/import-time wiring, so the REFACTOR "no behavior delta" claim is false -->
- **Created:** 2026-10-06
- **Question file:** `docs/questions/composition-root-factory.md`
- **Spec:** `docs/specs/composition-root-factory.md` (created at P.4, with an Impact Analysis) — plus a **Spec Amendment PR** touching `docs/specs/settings-coverage.md` REQ-002/AC-003, `docs/specs/logging-coverage.md` REQ-011/AC-011 and `docs/specs/settings-public-registry-setter.md` REQ-011/AC-016 (Q-01 = A, Q-02 = A, 2026-10-10)
- **Worktree:** <created at P.4> `../python-template_kopie-worktrees/crosscut/composition-root-factory`
- **Depends on:** `settings-public-registry-setter` (IN-WORKFLOW — **hard gate confirmed by Q-02 = A on 2026-10-10**: P.4 may not start before it merges, because this change amends its REQ-011/AC-016), `structlog-logging` (**MERGED** 2026-10-07, PR #74 → `c7a9119` — dependency satisfied). **Blocks `backend-api`** (added 2026-10-10: that change builds its FastAPI app on this change's `build_composition_root()`, Q-07 = B there).
- **Related specs:** `docs/specs/settings-coverage.md` (REQ-002 "the entrypoint calls each feature's `register_settings(registry)` once at startup", AC-003 the subprocess wiring test), `docs/specs/logging-coverage.md` (startup ordering of `setup_logger`)

## Goal (one line)

Give `src/main.py` an explicit composition root — a **`build_composition_root() -> App`** callable returning a frozen dataclass of named, typed fields (decided 2026-10-10, Q-04 = A) — so the object graph is built on demand instead of as a side effect of importing the module, and `import main` creates nothing (Q-03 = A: the module-level wiring is removed, not kept as a compatibility layer).

## Why

`src/main.py` is 221 lines of module-level wiring: `_catalog` (`:82`), the cycle proxies (`:130-131`), `_settings_registry` (`:137`), and every service as a module global (`:145,153,181,186,194,201,202,212`). Importing `main` therefore opens SQLite repositories and creates files on disk (`SqliteSessionRepository(_AUTH_DB)` at `:145`, `SqliteUserRepository("sqlite:///./data/usermanagement/users.db")` at `:181`, `SqliteFileRepository("sqlite:///./data/filemanagement.db")` at `:194`) before any caller can configure anything. That is why the wiring tests must run `main.py` in a **subprocess** (`tests/acceptance/settings_coverage/test_wiring.py`) — an in-process test cannot import `main` twice with different wiring. Deferred explicitly by `settings-public-registry-setter` Q-21 (2026-10-06): the setter keeps the current position, and the factory becomes its own change.

## In scope

- Introduce a callable composition root (name and shape decided at P.2) that builds the object graph and returns it.
- Keep a module-level import path working so existing consumers of `main`'s globals keep resolving (or enumerate and update them — P.2 decides).
- Move the subprocess wiring tests to in-process equivalents **only if** the spec amendment is approved; otherwise leave them as they are.

## Out of scope

- Any change to what is wired, in which order, or with which repositories.
- Breaking the `_LazyPermissionService` / `_LazyUserManager` cycle handling — the cycle is real (`PermissionService` ↔ `UserManager`, `SettingsRegistry` ↔ `PermissionService`) and the proxies stay.
- The singleton install semantics — owned by `settings-public-registry-setter`.

## Affected features

`src/main.py` only (plus its tests). No feature package code changes.

## Constraints and risks

- `docs/specs/settings-coverage.md` REQ-002/AC-003 specify **import-time** wiring; a factory changes that, so this change cannot stay a pure no-behavior-delta REFACTOR without a Spec Amendment PR for those IDs. P.2 must resolve REFACTOR-with-amendment vs reclassification before P.4.
- Importing `main` twice in one process is currently impossible to test; whatever shape is chosen must not make that worse.
- Both `main.py` and its tests are touched by `settings-public-registry-setter` and `structlog-logging` — hence the `Depends on:`.

## Value triage (2026-10-06, pre-workflow)

- **Overlap:** none in `docs/todo/`; the only related record is `settings-public-registry-setter` Q-21, which deferred this. At code level, `src/main.py`'s module-level wiring is the thing itself — there is no existing factory to extend.
- **Beneficiary:** whoever tests or embeds this backend: importing `main` would stop creating databases and directories, and the wiring tests would no longer need a subprocess. Indirect end-user value (fewer test-only workarounds, faster tests).
- **Score: 3/5** — genuine architectural value and it removes a real test workaround, but it touches the whole composition root, needs a spec amendment to `settings-coverage.md`, and is blocked by two in-flight changes that edit the same file.
- **Recommendation:** implement — after `settings-public-registry-setter` and `structlog-logging` merge.
- **Decision:** implement — requested by the user on 2026-10-06 as the answer to `settings-public-registry-setter` Q-21 ("Go with 1 but open a todo for 2").

## Acceptance signal (plain language)

`import main` no longer creates `data/` databases or opens repositories; calling the composition root builds the same object graph the module used to build, in the same order, and the wiring assertions that today need a subprocess can be made in-process. The full suite is GREEN and no service behaves differently.

## Prep log
| Step | Date | Result |
|---|---|---|
| P.1 Frame | 2026-10-06 | classified REFACTOR (P.2 must confirm the spec-amendment path); TODO + question file created; value triage recorded (3/5, implement) |
| P.2 Interrogate (<n> questions) | | |
| P.3 Answer (<n> answered) | | |
| P.4 Draft spec / triage / baseline / scope | | |
| P.5 Self-consistency (FEATURE/CROSS-CUTTING) | | |
