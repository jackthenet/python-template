# TODO: session-lookup-unwired

Backlog item for one planned change, created at **P.1 Frame** from the template.

This is a **planning record, not normative**: like `docs/questions/`, it is committed directly to `main` (see "Phase P: PREPARE" in `AGENTS.md`). It carries no approval gate — the spec does.

- **Status:** WAITING  <!-- PREPARING | QUESTIONS-ANSWERED | READY | IN-WORKFLOW | WAITING | MERGED -->  <!-- waiting on human merge of PR #63 -->
- **Change type:** ISSUE
- **Created:** 2026-10-03
- **Question file:** `docs/questions/session-lookup-unwired.md`
- **Spec:** n/a (defect against the approved `docs/specs/user-roles-permissions.md`)
- **Worktree:** <created at P.4> `../python-template_kopie-worktrees/issue/session-lookup-unwired`
- **Depends on:** none
- **Related specs:** `docs/specs/user-roles-permissions.md` (REQ-017, AC-020, AC-021, EDGE-007), `docs/specs/session-management.md` (the session repository's `get_by_token_hash`)

## Goal (one line)
Wire the session lookup into the composition root so a session-token-bearing permission check actually validates the session instead of always denying.

## Why
Found during the `api-keys` P.2 interrogation, not by a user report. `src/main.py:145-153` constructs `PermissionService` **without** `session_lookup=`, and `src/backend/permissions/service.py:407` returns `"storage_error"` whenever `self._session_lookup is None` (fail-closed, EDGE-007). No production call site passes the argument — `rg -n "session_lookup\s*=" src tests` finds it only in `tests/unit/permissions/test_edge_cases.py` and `tests/acceptance/permissions/test_check_api.py`. Consequence: in the composed application, **every** check that supplies a `session_token` is denied, so the positive branch of **AC-020** ("a valid, unrevoked, unexpired session token … the check proceeds") is unachievable outside tests, and **REQ-017**'s validation path never runs. The spec treats the wiring as real: `docs/specs/user-roles-permissions.md:827` states "The session repository (`get_by_token_hash`) is used by the check for session validation (REQ-017)". Fail-closed means it is safe, but it silently disables a specified capability — and the traceability row for REQ-017/AC-020 is still recorded `PENDING` (`docs/specs/user-roles-permissions.md:786`).

## In scope
- Reproduce the defect with a failing test that exercises the **composition root** (not a hand-built `PermissionService`), asserting that a valid session token is accepted.
- Pass the session lookup (the session repository's `get_by_token_hash`, per ADR-073's structural `SessionLookup` seam) when constructing `PermissionService` in `src/main.py`.
- Confirm no other composition-root wiring is missing on the same construction path (the same call passes `catalog`, `event_bus`, `settings_registry` — check each is wired, not defaulted).

## Out of scope
- Any change to `PermissionService`'s check logic, the `SessionLookup` protocol, or the fail-closed behaviour for a genuinely unavailable lookup (EDGE-007 stays as specified).
- New session or permission behaviour (that would be a FEATURE / spec amendment, not this ISSUE).
- The `api-keys` credential type (separate change; it does not depend on this path).

## Affected features
`src/main.py` (composition root); behaviour observed through `src/backend/permissions/` and `src/backend/sessionmanagement/`.

## Constraints and risks
- The construction order in `src/main.py` is deliberate (the lazy `UserManager` proxy breaks a cycle); the session repository must be available at that point, or the lookup must be a lazy proxy like the user lookup — decide at triage, do not reorder startup wiring blindly.
- Fail-closed is a hard invariant of the permissions spec (`user-roles-permissions.md:19`): the fix must not turn a storage failure into an allow.
- A test that only builds its own `PermissionService` cannot catch this class of defect — the reproduction test must go through the real composition root.

## Acceptance signal (plain language)
A test that starts the application's real wiring and calls a permission check with a valid, unrevoked, unexpired session token passes; the same check with a revoked or another user's token still denies; the full suite and the `EDGE-007` fail-closed tests stay green.

## Value triage
- **Overlap:** none — no existing test or script covers composition-root wiring (`rg -ln "main.py|composition root" tests` returns only feature wiring tests, none for the permission service's session lookup).
- **Beneficiary:** every caller that passes a session token (and the future `api-keys` / HTTP surface, which would otherwise inherit a check path that cannot validate sessions).
- **Score:** 4/5 — a specified capability is silently dead; the fix is small and localized.
- **Recommendation:** implement as its own ISSUE (light tier likely: 1 file + 1 test, single feature area, existing tests cover the check path).

## Prep log
| Step | Date | Result |
|---|---|---|
| P.1 Frame | 2026-10-03 | TODO + question file created on `main`; type **ISSUE** (deviation from approved REQ-017/AC-020, no new behaviour); discovered during the `api-keys` P.2 interrogation. Evidence verified on `main`: `src/main.py:145-153` (no `session_lookup=`), `src/backend/permissions/service.py:407` (`"storage_error"` when the lookup is `None`), `rg` shows the argument passed only in tests |
| P.2 Interrogate (0 questions) | 2026-10-03 | **DONE** — **defect confirmed** against REQ-017 (`user-roles-permissions.md:513`), AC-020 (`:552`), AC-021 (`:553`), EDGE-007 (`:597`) and the Impact-Analysis claim at `:827`; reachable through `@requires_permission` → `principal.session_token` (`src/backend/shared/principal.py:74`), latent today only because no in-repo caller sets a token. Traceability: spec matrix `:786` `PENDING`, `docs/verification/traceability.md:680` `GREEN` — the GREEN test injects a fake lookup, so the **composition root is uncovered**. **Fix shape settled from code:** `SqliteSessionRepository.get_by_token_hash` (`src/backend/authentication/repository.py:92-94`) structurally satisfies `SessionLookup` (`models.py:78-81`); the repo is built later (`main.py:177-178` vs `:145`) but has **no cycle**, so moving those two lines above `:144` and passing `session_lookup=_session_repository` is the whole fix — **no lazy proxy** (larger than the problem). **Reproduction plan:** new `tests/acceptance/permissions/test_composition_wiring.py::test_ac_020_composition_root_validates_session_token`, reusing the subprocess + `import main` + temp-registry pattern of `tests/acceptance/settings_coverage/test_wiring.py:12-31`. **Light-tier ISSUE: qualifies** (1 file, no new dependency/interface, covering tests named). `api-keys` Q-03 explicitly **not** pre-decided |
| P.2 Interrogate (second pass, 2 questions) | 2026-10-03 | **BLOCKED-USER** — the first pass wrote a zero-question record without the required sweep; a second pass closed 9 more points from evidence (E-1…E-9) and raised **Q-01** (scope: composition root only, or also the caller-less `get_permission_service()` fallback at `service.py:497-514` — recommendation: composition root only) and **Q-02** (governance: close the `PENDING` REQ-017/AC-020 rows inside the approved spec's §11 matrix, or leave them as the historical record — recommendation: leave them, add the evidence row to `docs/verification/traceability.md` at Phase 5). **Correction to this file's framing:** `src/main.py:145-153` does **not** pass `user_lookup=` / `group_lookup=` / `role_lookup=` / `permission_lookup=` — those names exist nowhere in the repo; the real signature is `src/backend/permissions/service.py:128-137` (8 dependencies, 7 wired), `session_lookup` is the only unwired one |
| P.3 Answer (2 pending) | 2026-10-04 | **DONE — both answered, `Status: READY`.** **Q-01 = A (composition root only)** — `get_permission_service()`'s fallback stays unwired (no caller in `src/`; wiring it would add a cross-feature import inside `backend/permissions/`); the light-tier 1-file claim stands. **Q-02 = B (leave the spec §11 rows)** — no Spec Amendment, no Changelog; Phase 5 adds only the new composition-root evidence row to `docs/verification/traceability.md`. Both answers match the already-drafted triage (`e522dee`), so P.4 needs no rework; the record's stale "P.2 DONE — 0 questions / P.3 no-op" row is the only thing to correct on resumption. Next: **Phase 3** (reproduction test → RED) |
| P.4 Draft triage + worktree | 2026-10-03 | **already done, out of order** — the first P.2 subagent also created the branch `issue/session-lookup-unwired` + worktree `../python-template_kopie-worktrees/issue/session-lookup-unwired` and wrote `docs/verification/session-lookup-unwired.md` (commit `e522dee`, triage quality is high: defect confirmed, reproduction plan, light-tier qualifies, fix = 2 lines moved + 1 keyword in `src/main.py`). Two things to fix on resumption: the record's Phase P table still claims "P.2 DONE — 0 questions / P.3 no-op" (superseded by the second pass's Q-01/Q-02), and its §6/§3 already match the recommended answers (composition root only; spec §11 rows left as the historical record) |
| P.5 Self-consistency | | n/a (ISSUE) |
| Phase 3 (S3.1 + S3.2) | 2026-10-04 | **RED CONFIRMED** — new `tests/acceptance/permissions/test_composition_wiring.py::test_ac_020_composition_root_validates_session_token` drives the real composition root (`import main` in a subprocess, `cwd=tmp_path`, src path derived from `__file__`); fails with `AssertionError: [False, False, False, False]` and `reason=storage_error` in the subprocess log — the `session_lookup is None` short-circuit. Commits `94d5b59`, `7ec4284`; evidence in `docs/verification/session-lookup-unwired.md`. Traceability row deferred to S5.3 per **Q-02** |
| Phase 4 (S4.2; S4.3 no-op) | 2026-10-04 | **GREEN** — `src/main.py`: `_AUTH_DB` + `_session_repository` moved above `PermissionService`, `session_lookup=_session_repository` added (10 +-). Lazy-proxy order intact; `src/backend/permissions/` untouched, so EDGE-007/INV-002 fail-closed unchanged. Targeted 45 passed, permissions dirs 59 passed, ruff clean. Commit `f85deba`. S4.3 refactor: no structural changes needed (fast path) |
| Phase 5 (S5.1+S5.2, S5.3+S5.4) | 2026-10-04 | **PASS (light tier)** — repro 1 passed; permissions dirs 64 passed; smoke (settings_coverage + sessionmanagement + authentication) 126 passed; `ruff check .` clean; `mypy src/` clean (83 files); `check_traceability.py` PASS (747 rows). New evidence row in `docs/verification/traceability.md` (own `## Issue:` section; existing REQ-017/AC-020 rows left byte-identical per Q-02). Commits `d406dd8`, `f05b34c` |
| Phase 6 (S6.1–S6.3, S6.4) | 2026-10-04 | **REVIEW CLEAN** (4 findings, all resolved/accepted, 0 open, commit `8a67bc3`) → **pre-merge gate: full suite 728 passed, 1 skipped** (+1 vs the 727 baseline = this change's test, 0 regressions, commit `b9bfc10`) → **bump patch 0.6.0 → 0.6.1** (`df81d8b`) → **PR #63** opened: https://github.com/jackthenet/python-template/pull/63. Status **WAITING** for human merge; S7.1 cleanup follows |
