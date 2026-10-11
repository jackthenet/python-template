# TODO: startup-settings-registration-gaps

Backlog item for one planned change, created at **P.1 Frame** from this template and named `startup-settings-registration-gaps.md`. One file per change.

This is a **planning record, not normative**: like `docs/questions/`, it is committed directly to `main` (see "Phase P: PREPARE" in `AGENTS.md`). It carries no approval gate — the spec does.

- **Status:** WAITING  <!-- PREPARING | QUESTIONS-ANSWERED | READY | IN-WORKFLOW | WAITING | MERGED | DROPPED -->
- **Change type:** ISSUE  <!-- confirmed at P.3 Q-01 (deviation from settings-coverage REQ-002/AC-003) and re-confirmed after the Q-15 widening at Q-24: the type stays ISSUE, the spec wordings are amended inside this change's PR -->
- **Created:** 2026-10-10
- **Question file:** `docs/questions/startup-settings-registration-gaps.md`
- **Spec:** n/a  <!-- the affected spec is docs/specs/settings-coverage.md; a Spec Amendment PR is possible if AC-003's wording must change -->
- **Worktree:** <created at P.4> `../python-template_kopie-worktrees/issue/startup-settings-registration-gaps`
- **Depends on:** ~~`settings-public-registry-setter`~~ — **satisfied by fact**: MERGED 2026-10-10 (PR #81, merge commit `2115faa`, release 1.2.0), so this change applies on top of the final composition-root shape (`src/main.py:191-196` on `main`, Q-13(a))
- **Related specs:** `docs/specs/settings-coverage.md` (REQ-002 / AC-003), `docs/specs/file-management.md`, `docs/specs/mail-service.md`, `docs/specs/session-management.md` (each states its settings are "registered via the feature-owned `register_settings(registry)` (call at startup)")

## Goal (one line)
Make `src/main.py` register the settings of **every** feature that owns a `feature_settings.py`, so no feature silently runs on hardcoded fallback defaults.

## Why
Measured at `main` (2026-10-10): nine features define `register_settings` (`src/backend/{authentication,eventbus,filemanagement,logging,mail,permissions,search,sessionmanagement,usermanagement}/feature_settings.py`), but `src/main.py` calls only six (`:173-178` — logging, authentication, usermanagement, eventbus, permissions, search). **`filemanagement`, `mail` and `sessionmanagement` are never registered anywhere in `src/`**, so every read of their settings keys falls back to the hardcoded default (settings REQ-005) instead of the registry value — a user cannot change SMTP, storage-root, avatar or session-TTL configuration at all.

The AC-003 witness hid it: `tests/acceptance/settings_coverage/test_wiring.py::test_main_wires_all_features` asserts only 4 keys from 4 features (`logging.log_level`, `authentication.session_ttl`, `usermanagement.roles`, `eventbus.max_queue_size`) while AC-003 says "**all** features' settings". The witness is incomplete, not the spec.

## In scope
_(as widened by the user's P.3 answers — Q-14, Q-15, Q-09, Q-17, Q-22, Q-24, Q-25, Q-26, Q-28, Q-29)_
- Register the settings of **all nine** features in the composition root, replacing the six named one-liners with a **data-driven list + loop** of the `register_settings` callables (Q-14).
- Strengthen the AC-003 witness `tests/acceptance/settings_coverage/test_wiring.py::test_main_wires_all_features` **in place** (same name), deriving the expected key set by **scanning** `src/backend/*/feature_settings.py` and probing the composition root's registry with `has()` (Q-04, Q-05, Q-06, Q-07), and **isolate** it (`cwd=tmp_path` + absolute `src` path) (Q-22).
- Add the **contract-tier** guard: widen `tests/contract/settings_coverage/test_inventory.py` to the nine-feature inventory, register all nine in its helper, and give `test_category_group` the corrected categories as AC-023 evidence (Q-17).
- Fix the four out-of-domain `category=` values to `category="security"` — `permissions.system_principal`, `sessionmanagement.max_listed_sessions` / `max_sessions_per_user` / `cleanup_batch_size` (Q-15 item 3, Q-25) — a second genuine REQ-018/AC-023 defect.
- Rewire `filemanagement.storage_root` so it is live: drop the explicit `LocalDiskStorageBackend("./data/files")` from the `FileService` construction (Q-15 item 2, Q-09).
- Add a startup **`WARNING`** in the settings registry naming every key whose persisted value overrode its definition default (Q-12, Q-28) — new behavior, riding this ISSUE by explicit user decision (Q-29).
- Amend four spec files **inside this change's PR**, each with a `## Changelog` entry: `settings-coverage.md` (§3.5 inventory + REQ-001/REQ-017/REQ-019/AC-024, NFR-002 credential carve-out, the new WARNING REQ), `file-management.md` (REQ-015/AC-029 wiring), `user-roles-permissions.md` (`:288` block), `session-management.md` (`:132-136` block) (Q-02, Q-11, Q-13(b), Q-24, Q-26, Q-27).
- Regenerate `STRUCTURE.md` in the same commit as the `src/main.py` edit; record the inherited `test_ac_021` RED as the baseline (Q-19).
- `bump-my-version bump patch` + `CHANGELOG.md` `Fixed` and `Changed` lines (Q-21).

## Out of scope
- Registering settings for features that do not own a `feature_settings.py`.
- Changing any feature's settings **keys** or **default values**.
- The composition-root extraction itself (`composition-root-factory`) and the service singleton installs (`composition-root-singleton-install`).
- Pruning stale keys from `values.yaml`, versioning the values file, or excluding credential settings from persistence (considered and rejected at Q-28).
- Widening the system principal's permissions (e.g. granting `settings.views`) — the witness uses `has()` (Q-07).

## Affected features
`src/main.py` (composition root); reads affected in `src/backend/filemanagement/`, `src/backend/mail/`, `src/backend/sessionmanagement/`.

## Constraints and risks
- Registering 16 previously-unregistered keys changes live behaviour: a `settings/values.yaml` or a template that already carries one of those keys will now take effect. The change must state that as the intended fix, not a regression.
- `src/main.py:173-178` is pinned by the in-flight `settings-public-registry-setter` REQ-011/AC-016 source scan — merge order matters.
- The AC-003 witness writes `_reg_mod._registry[0] = ...` (a private-slot write that `settings-public-registry-setter` T-007 migrates) — the same file changes there.

## Value triage (2026-10-10, pre-workflow)
- **Overlap:** none — no live or archived TODO covers startup settings registration; `composition-root-factory` Q-14 explicitly rules it out of that change's scope and recommends a separate TODO. The nearest existing mechanism is the settings feature's own `register_feature` (`src/backend/settings/registry.py`), which this change *uses*, not re-implements.
- **Beneficiary:** the operator/user of the template: three features become configurable through the settings registry (SMTP host/from, storage root, allowed types, avatar limits, session TTL/cap) instead of being frozen at code defaults; it also makes AC-003's claim true.
- **Score: 5/5** — a real defect against an approved AC, a small localized diff (3 call sites + 1 witness), and it removes a silent-failure class the settings feature was designed to prevent.
- **Recommendation:** implement
- **Decision:** **implement** (user, 2026-10-11, P.3 round 1). Confirmed by the same round's **Q-18 = C**: this TODO is its own ISSUE and lands **before** `composition-root-factory`, whose Q-14 has been re-answered to put the three calls out of that change's scope.  <!-- recorded when the user answers; a dropped TODO moves to docs/todo/archive/ with its question file -->

## Acceptance signal (plain language)
Running `src/main.py` and asking the shared registry reports `True` for every settings key every feature owns (including `filemanagement.*`, `mail.*`, `sessionmanagement.*`), and the AC-003 acceptance test fails if any one of them is dropped again.

## Prep log
| Step | Date | Result |
|---|---|---|
| P.1 Frame | 2026-10-10 | classified ISSUE (affected REQ-002 / AC-003 of `settings-coverage.md`); measured 9 `register_settings` definitions vs 6 calls in `src/main.py`; AC-003 witness samples 4 keys only |
| P.2 Interrogate (23 questions) | 2026-10-10 | **DONE — 23 questions (Q-01…Q-23; Q-01…Q-17 from the first execution kept as recorded, Q-18…Q-23 added on re-entry), every entry with a `Recommended:` + reason (verified: 23 entries, 0 missing fields); `### Category coverage` filled — 15 rows, 13 covered-with-reference, 2 skipped with reasons; non-goals Q-15 and overlap Q-16/Q-18 present.** Commit `63298e2`. **⚠ Cross-change contradiction now on the board:** `composition-root-factory` **Q-14 = C** (user, 2026-10-10) assigned these three `register_settings` calls + the gap-closing acceptance test to *that* change — i.e. this TODO's whole scope — while `composition-root-singleton-install` Q-26 says the registration gap is another change's work. **Q-18** asks the user to resolve it; P.2 recommends **C** (keep this ISSUE separate and land it first after `settings-public-registry-setter` merges, and re-answer factory Q-14 = out-of-scope in the same P.3 round) so a 3-line 5/5 fix is not parked behind a hard dependency and 22 unanswered questions in a 3/5 change. **New baseline fact:** `main`'s full suite is **RED** today — `uv run pytest tests/ -q` → 1 failed, 815 passed, 1 skipped (`test_ac_021_committed_map_matches_fresh_render`, `docs/ 225` vs `231` stale `STRUCTURE.md`), unrelated to this defect; Q-19 asks who absorbs it (recommended: regenerate the map in the same commit as the `src/main.py` edit and record the inherited failure as the baseline). **The `## Value triage` `Decision:` is still the unfilled placeholder — this TODO may not pass P.4 until the user decides.** Next: **P.3 Answer** (⏸ user) |
| P.3 Answer (<n> answered) | 2026-10-11 | **DONE — 25 questions answered (Q-01…Q-29, 0 PENDING), 8 rounds.** Type kept **ISSUE** (Q-01, re-confirmed Q-24) with the spec wordings amended inside this change's PR. Scope **widened by the user** beyond P.2's recommendation: registration **loop** (Q-14), the four `category` fixes → `security` (Q-15/Q-25/Q-26), `storage_root` made live by dropping the explicit backend (Q-09), contract-tier inventory guard (Q-17), witness isolation + repo-root hygiene fixture (Q-22), startup `WARNING` on persisted-value overrides (Q-12/Q-28) riding this ISSUE by explicit decision (Q-29). `patch` bump + `Fixed`/`Changed` changelog lines (Q-21); `STRUCTURE.md` regenerated with the `src/main.py` commit, inherited `test_ac_021` RED recorded as the baseline (Q-19). Four spec files amended in-PR (Q-02, Q-11/Q-27, Q-13(b), Q-26). Next: **P.4 Draft** (triage record + branch + worktree) |
| P.4 Draft spec / triage / baseline / scope | 2026-10-11 | **DONE — branch `issue/startup-settings-registration-gaps` + worktree `../python-template_kopie-worktrees/issue/startup-settings-registration-gaps` created from `main @25b7e7b`; triage record `docs/verification/startup-settings-registration-gaps.md` (226 lines) committed as `cce7439`.** **Six defects confirmed by re-measurement in the worktree** (D-1 16 of 34 owned keys never registered — filemanagement 5, mail 8, sessionmanagement 3, and `filemanagement.storage_root` has no definition at all; D-2 the AC-003 witness samples 4 keys from 4 features; D-3 four out-of-domain `category=` values at `sessionmanagement/feature_settings.py:41,48,55` + `permissions/feature_settings.py:31`; D-4 `FileService` pins `LocalDiskStorageBackend("./data/files")` at `src/main.py:215` against REQ-015/AC-029; D-5 silent persisted-value override at `registry.py:121`; D-6 `mail.smtp_password` vs NFR-002). Affected IDs: settings-coverage REQ-001/002/005/017/018/019 + AC-003/023/024 + NFR-002/003, settings-public-registry-setter REQ-011/AC-016, file-management REQ-015/AC-029, user-roles-permissions REQ-019, session-management REQ-019/AC-039. Reproduction plan **R-1** (strengthen `test_main_wires_all_features` in place) + **R-2** (widen `test_inventory.py` → `test_category_group`), targeted RED/GREEN commands in §5. **Two TODO claims corrected:** the inherited baseline is **3 failed, 887 passed, 1 skipped (351.73 s)** — `test_ac_021` is a CRLF-vs-LF byte-compare artifact (`make_map --check` exits 0, 2004/2004 lines), not a stale `docs/` count, and the two property failures are Hypothesis deadline flakes that pass in isolation. **Light ISSUE tier NOT qualified** (10 non-test files, 4 features, 5 specs) → full Phase 5 gate set. **⚠ LQ-01 raised (late question, appended on `main`):** widening the contract inventory guard makes `test_no_secret_settings` fail on `mail.smtp_password` — NFR-002 vs the approved mail spec; S3.1 needs the (a)/(b) decision. Next: **S3.1** once LQ-01 is answered |
| P.5 Self-consistency (FEATURE/CROSS-CUTTING) | | |
