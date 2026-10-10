# TODO: startup-settings-registration-gaps

Backlog item for one planned change, created at **P.1 Frame** from this template and named `startup-settings-registration-gaps.md`. One file per change.

This is a **planning record, not normative**: like `docs/questions/`, it is committed directly to `main` (see "Phase P: PREPARE" in `AGENTS.md`). It carries no approval gate — the spec does.

- **Status:** PREPARING  <!-- PREPARING | QUESTIONS-ANSWERED | READY | IN-WORKFLOW | WAITING | MERGED | DROPPED -->
- **Change type:** ISSUE  <!-- P.2 must confirm: the defect is a deviation from settings-coverage REQ-002/AC-003 ("all features' settings are registered") -->
- **Created:** 2026-10-10
- **Question file:** `docs/questions/startup-settings-registration-gaps.md`
- **Spec:** n/a  <!-- the affected spec is docs/specs/settings-coverage.md; a Spec Amendment PR is possible if AC-003's wording must change -->
- **Worktree:** <created at P.4> `../python-template_kopie-worktrees/issue/startup-settings-registration-gaps`
- **Depends on:** `settings-public-registry-setter` (IN-WORKFLOW — it rewrites the same wiring lines `src/main.py:173-178` and migrates the private-slot write in the AC-003 witness)
- **Related specs:** `docs/specs/settings-coverage.md` (REQ-002 / AC-003), `docs/specs/file-management.md`, `docs/specs/mail-service.md`, `docs/specs/session-management.md` (each states its settings are "registered via the feature-owned `register_settings(registry)` (call at startup)")

## Goal (one line)
Make `src/main.py` register the settings of **every** feature that owns a `feature_settings.py`, so no feature silently runs on hardcoded fallback defaults.

## Why
Measured at `main` (2026-10-10): nine features define `register_settings` (`src/backend/{authentication,eventbus,filemanagement,logging,mail,permissions,search,sessionmanagement,usermanagement}/feature_settings.py`), but `src/main.py` calls only six (`:173-178` — logging, authentication, usermanagement, eventbus, permissions, search). **`filemanagement`, `mail` and `sessionmanagement` are never registered anywhere in `src/`**, so every read of their settings keys falls back to the hardcoded default (settings REQ-005) instead of the registry value — a user cannot change SMTP, storage-root, avatar or session-TTL configuration at all.

The AC-003 witness hid it: `tests/acceptance/settings_coverage/test_wiring.py::test_main_wires_all_features` asserts only 4 keys from 4 features (`logging.log_level`, `authentication.session_ttl`, `usermanagement.roles`, `eventbus.max_queue_size`) while AC-003 says "**all** features' settings". The witness is incomplete, not the spec.

## In scope
- Add the three missing `register_*_settings(...)` calls to the composition root in the correct position (before any feature code runs).
- Strengthen the AC-003 witness so it covers every feature that owns settings (never weaken it).

## Out of scope
- Registering settings for features that do not own a `feature_settings.py`.
- Changing any feature's default values or its settings keys.
- The composition-root extraction itself (`composition-root-factory`) and the singleton installs (`composition-root-singleton-install`).

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
- **Decision:** <the user's answer + date>  <!-- recorded when the user answers; a dropped TODO moves to docs/todo/archive/ with its question file -->

## Acceptance signal (plain language)
Running `src/main.py` and asking the shared registry reports `True` for every settings key every feature owns (including `filemanagement.*`, `mail.*`, `sessionmanagement.*`), and the AC-003 acceptance test fails if any one of them is dropped again.

## Prep log
| Step | Date | Result |
|---|---|---|
| P.1 Frame | 2026-10-10 | classified ISSUE (affected REQ-002 / AC-003 of `settings-coverage.md`); measured 9 `register_settings` definitions vs 6 calls in `src/main.py`; AC-003 witness samples 4 keys only |
| P.2 Interrogate (23 questions) | 2026-10-10 | **DONE — 23 questions (Q-01…Q-23; Q-01…Q-17 from the first execution kept as recorded, Q-18…Q-23 added on re-entry), every entry with a `Recommended:` + reason (verified: 23 entries, 0 missing fields); `### Category coverage` filled — 15 rows, 13 covered-with-reference, 2 skipped with reasons; non-goals Q-15 and overlap Q-16/Q-18 present.** Commit `63298e2`. **⚠ Cross-change contradiction now on the board:** `composition-root-factory` **Q-14 = C** (user, 2026-10-10) assigned these three `register_settings` calls + the gap-closing acceptance test to *that* change — i.e. this TODO's whole scope — while `composition-root-singleton-install` Q-26 says the registration gap is another change's work. **Q-18** asks the user to resolve it; P.2 recommends **C** (keep this ISSUE separate and land it first after `settings-public-registry-setter` merges, and re-answer factory Q-14 = out-of-scope in the same P.3 round) so a 3-line 5/5 fix is not parked behind a hard dependency and 22 unanswered questions in a 3/5 change. **New baseline fact:** `main`'s full suite is **RED** today — `uv run pytest tests/ -q` → 1 failed, 815 passed, 1 skipped (`test_ac_021_committed_map_matches_fresh_render`, `docs/ 225` vs `231` stale `STRUCTURE.md`), unrelated to this defect; Q-19 asks who absorbs it (recommended: regenerate the map in the same commit as the `src/main.py` edit and record the inherited failure as the baseline). **The `## Value triage` `Decision:` is still the unfilled placeholder — this TODO may not pass P.4 until the user decides.** Next: **P.3 Answer** (⏸ user) |
| P.3 Answer (<n> answered) | | |
| P.4 Draft spec / triage / baseline / scope | | |
| P.5 Self-consistency (FEATURE/CROSS-CUTTING) | | |
