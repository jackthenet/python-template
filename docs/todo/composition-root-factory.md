# TODO: composition-root-factory

Backlog item for one planned change, created at **P.1 Frame** from this template and named `composition-root-factory.md`. One file per change.

This is a **planning record, not normative**: like `docs/questions/`, it is committed directly to `main` (see "Phase P: PREPARE" in `AGENTS.md`). It carries no approval gate — the spec does.

- **Status:** QUESTIONS-ANSWERED  <!-- PREPARING | QUESTIONS-ANSWERED | READY | IN-WORKFLOW | WAITING | MERGED | DROPPED -->
- **Blocked by:** `startup-settings-registration-gaps` (ISSUE, `QUESTIONS-ANSWERED`, lands first — Q-27)
- **Change type:** CROSS-CUTTING  <!-- reclassified from REFACTOR at P.3 round 1, 2026-10-10 (Q-01 = A): `import main`'s side effects are externally observable and two approved specs' ACs pin module/import-time wiring, so the REFACTOR "no behavior delta" claim is false -->
- **Created:** 2026-10-06
- **Question file:** `docs/questions/composition-root-factory.md`
- **Spec:** `docs/specs/composition-root-factory.md` (created at P.4, with an Impact Analysis) — plus a **Spec Amendment PR** touching `docs/specs/settings-coverage.md` REQ-002/AC-003, `docs/specs/logging-coverage.md` REQ-011/AC-011 and `docs/specs/settings-public-registry-setter.md` REQ-011/AC-016 (Q-01 = A, Q-02 = A, 2026-10-10)
- **Worktree:** <created at P.4> `../python-template_kopie-worktrees/crosscut/composition-root-factory`
- **Depends on:** (corrected 2026-10-11, **Q-27**) `settings-public-registry-setter` — **satisfied** (MERGED 2026-10-10, PR #81, merge commit `2115faa`); `structlog-logging` — **satisfied** (MERGED 2026-10-07, PR #74 → `c7a9119`); **`startup-settings-registration-gaps` — hard sequencing dependency, must merge first** (its loop + nine-feature registration set are what this change's Q-24 guard and Q-23 NFR inventory are re-derived from). **Blocks `backend-api`** (that change builds its FastAPI app on this change's `build_composition_root()`, `backend-api` Q-07 = B).
- **Related specs:** `docs/specs/settings-coverage.md` (REQ-002 "the entrypoint calls each feature's `register_settings(registry)` once at startup", AC-003 the subprocess wiring test), `docs/specs/logging-coverage.md` (startup ordering of `setup_logger`)

## Goal (one line)

Give `src/main.py` an explicit composition root — a **`build_composition_root() -> App`** callable returning a frozen dataclass of named, typed fields (decided 2026-10-10, Q-04 = A) — so the object graph is built on demand instead of as a side effect of importing the module, and `import main` creates nothing (Q-03 = A: the module-level wiring is removed, not kept as a compatibility layer).

## Why

`src/main.py` is 221 lines of module-level wiring: `_catalog` (`:82`), the cycle proxies (`:130-131`), `_settings_registry` (`:137`), and every service as a module global (`:145,153,181,186,194,201,202,212`). Importing `main` therefore opens SQLite repositories and creates files on disk (`SqliteSessionRepository(_AUTH_DB)` at `:145`, `SqliteUserRepository("sqlite:///./data/usermanagement/users.db")` at `:181`, `SqliteFileRepository("sqlite:///./data/filemanagement.db")` at `:194`) before any caller can configure anything. That is why the wiring tests must run `main.py` in a **subprocess** (`tests/acceptance/settings_coverage/test_wiring.py`) — an in-process test cannot import `main` twice with different wiring. Deferred explicitly by `settings-public-registry-setter` Q-21 (2026-10-06): the setter keeps the current position, and the factory becomes its own change.

## In scope
_(as settled by P.3, 2026-10-11 — Q-01…Q-30, 30 entries answered)_
- `build_composition_root() -> App` (Q-04): a frozen dataclass with named, typed fields, keyword-only parameters defaulting to today's literals (Q-05), living in a new **`src/backend/composition/`** package (Q-07, Q-20c); `src/main.py` becomes a thin entrypoint with an `if __name__ == "__main__":` guard (Q-06).
- The container exposes **all 14 wired objects including the two lazy proxies** (Q-28), and the factory **installs** `set_permission_service(...)` / `set_session_service(...)` (Q-15), absorbing `composition-root-singleton-install` (Q-30 — that TODO is DROPPED).
- **Self-resetting** on a second call: resets the settings/permissions/search/session slots and **reuses the live event bus** — never `reset_event_bus()`, which shuts it down (Q-10 + Q-10b).
- **Cycle simplification:** `_LazyUserManager` is deleted; `UserManager` is built first with the permission proxy, then `PermissionService` with the real manager (Q-16 + Q-16b). One proxy stays; two `type: ignore` comments remain (Q-17).
- The **full call order is an invariant, including the registration loop's element order** inherited from the ISSUE (Q-09), guarded by an exact registered-key-set assertion (nine features / 34 keys) plus a loop-order assertion (Q-24).
- Tests: rewrite the two subprocess wiring tests in-process (Q-12) and add exactly two new ones (Q-13); filesystem isolation by parameters + `monkeypatch.chdir` (Q-11).
- Spec amendments ride this change's own branch/PR (Q-29): `settings-coverage.md` REQ-002/AC-003, `logging-coverage.md` REQ-011/AC-011, `settings-public-registry-setter.md` REQ-011/AC-016, plus the new composition-module REQs and the two-install REQs; the three `src/main.py`-pinning witnesses and their traceability rows are updated in the same commit (Q-20).
- `STRUCTURE.md` regenerated in the same commit (Q-21); coverage now measures the new package (`source = ["src/backend", ...]`, `fail_under = 92`) and the total is re-measured at Phase 5 (Q-20).

## Out of scope
_(Q-25, as amended by the Q-15 tie-break)_
- New settings registrations — owned by `startup-settings-registration-gaps` (a).
- Singleton installs **beyond the two decided at Q-15** (b, narrowed).
- A new CLI / `[project.scripts]` entry point (c), any feature public-API change (d), any `scripts/` change (e), and the import-boundary migration owned by `public-api-import-boundary` (f).
- Splitting the factory into sub-builders (Q-19) and a numeric startup budget (Q-23).

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
| P.2 Interrogate (29 questions) | 2026-10-10 | **DONE — 29 questions (Q-01…Q-29) in one batch, every entry with a `Recommended:` + reason, `### Category coverage` table present.** Commit `fc02131`; TODO advanced to `WAITING` in `c040666`. The batch **challenged the P.1 REFACTOR classification** (Q-01): importing `main` has externally observable side effects — it creates `data/authentication.db`, `data/permissions.db`, `data/usermanagement/users.db`, `data/filemanagement.db`, `logs/app.log` and `settings/values.yaml` in ~1.04 s — so a "no behavior delta" claim is false. |
| P.3 Answer (8 of 29 answered, 2 rounds) | 2026-10-10 | **Rounds 1–2 recorded** — round 1 `544d2c9`: **Q-01 CROSS-CUTTING** (reclassify; new `docs/specs/composition-root-factory.md` + Impact Analysis + a Spec Amendment PR over `settings-coverage.md` REQ-002/AC-003 and `logging-coverage.md` REQ-011/AC-011), **Q-02** sequence after `settings-public-registry-setter` merges + amend its REQ-011/AC-016 to be position- and import-agnostic (drop the `:137-138` / `:173-178` line pins, keep install-before-register), **Q-03** remove the `src/main.py` module-level wiring entirely (no compatibility layer; the 2 subprocess wiring tests rewritten in-process), **Q-04** `build_composition_root() -> App` (frozen dataclass), name `create_app` left free for `backend-api`. Round 2 `c50c600`: **Q-05 A** keyword-only params defaulting to today's literals, reusing `permissions.service.DEFAULT_DATABASE_URL` / `DEFAULT_USER_DATABASE_URL`, **Q-07 B** the composition root moves to a **new `src/backend/composition/` package** (against the P.2 recommendation — enters the coverage source set, `STRUCTURE.md` gains a package, `src/main.py` keeps only the `__main__` shim), **Q-08 A** `setup_logger()` is the factory's first call after `register_logging_settings`, `logging-coverage` REQ-011/AC-011 amended to "exactly one call, inside the composition root, before any feature object is constructed" + both source-scan tests rewritten, **Q-14 C** (against the P.2 recommendation) the three never-called `register_settings` calls (filemanagement / mail / sessionmanagement, 16 unregistered keys) are fixed **inside this change** with a new acceptance test. **21 questions still PENDING — the change stays WAITING.** Two interlocks must be answered in the next round: **Q-15** (does the factory install the `PermissionService` / `SessionService` singletons?) is the same open question as `composition-root-singleton-install` **Q-01**, and **Q-14 = C** now contradicts `startup-settings-registration-gaps` **Q-18** (which recommends this change *not* absorb the registration gap). Next: **P.3 round 3** (⏸ user) |
| P.3 Answer (30 of 30 answered, 9 rounds) | 2026-10-11 | **DONE — all 30 entries answered (Q-01…Q-30 incl. the Q-10b and Q-16b follow-ups), 0 PENDING.** Key outcomes: package home `src/backend/composition/` (Q-07/Q-20c) with the three `src/main.py`-pinning witnesses and their specs amended in this PR (Q-20); container exposes all 14 objects (Q-28); **installs both service singletons** (Q-15) → `composition-root-singleton-install` **DROPPED as absorbed** (Q-30); self-resetting factory except the event bus (Q-10/Q-10b); `_LazyUserManager` removed (Q-16/Q-16b); full order invariant incl. the registration-loop element order (Q-09) guarded by the nine-feature key set + loop order (Q-24); two new tests + two rewritten (Q-12/Q-13); one branch, one approval PR, **minor** bump (Q-29). A **Q-25 ↔ Q-15 contradiction** was surfaced, put to the user with the architectural argument, and resolved in favour of installing (non-goal (b) narrowed to "beyond the two"). Advanced to `QUESTIONS-ANSWERED`. Next: **P.4 Draft** — only after `startup-settings-registration-gaps` merges (Q-27) |
| P.4 Draft spec / triage / baseline / scope | | |
| P.5 Self-consistency (FEATURE/CROSS-CUTTING) | | |
