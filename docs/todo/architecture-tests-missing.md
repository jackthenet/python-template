# TODO: architecture-tests-missing

Backlog item for one planned change, created at **P.1 Frame** from the template.

This is a **planning record, not normative**: like `docs/questions/`, it is committed directly to `main` (see "Phase P: PREPARE" in `AGENTS.md`). It carries no approval gate — the spec does.

- **Status:** WAITING  <!-- PREPARING | QUESTIONS-ANSWERED | READY | IN-WORKFLOW | WAITING | MERGED -->  <!-- P.4 scope record committed b9afe76 in ../python-template_kopie-worktrees/chore/architecture-tests-missing -->
- **Change type:** DOCS/CHORE  <!-- provisional: the type question (remove the reference vs. build the tests) is Q-1 in the question file -->
- **Created:** 2026-10-03
- **Question file:** `docs/questions/architecture-tests-missing.md`
- **Spec:** n/a
- **Worktree:** <created at P.4> `../python-template_kopie-worktrees/chore/architecture-tests-missing`
- **Depends on:** none
- **Related specs:** none (no spec requires architecture tests — verified: `rg -n "architecture" docs/specs/*.md` returns only prose about architecture in `authentication.md:14` and `search.md:416`, no requirement)

## Goal (one line)
Make the workflow's architecture gate honest: either the `tests/architecture/` gate exists, or the process text stops citing it.

## Why
Found during the `structure-map` P.2 interrogation. Three places make `uv run pytest tests/architecture/ -v` a **gate**, but the directory does not exist (verified on `main`: `ls -d tests/architecture` → no such directory):

- `AGENTS.md:579` — Phase 5 REFACTOR: "Run the full regression suite (MUST be GREEN, zero test changes) and the architecture rules (`uv run pytest tests/architecture/ -v`)."
- `AGENTS.md:212` — Phase Matrix, REFACTOR column: "Full regression + architecture + lint/types".
- `.agents/skills/verify/SKILL.md:88` and `:103` — "Run architecture rules (`uv run pytest tests/architecture/ -v`) and confirm they pass."

`AGENTS.md:593` and `:624` additionally require reviewing "architecture rules: `model/` contains domain concepts, `services/` contains use cases, `shared/` is deliberately small" and treat respecting them as a clean-review condition — with nothing executable behind them. A REFACTOR change that reaches Phase 5 today is instructed to run a command that errors (`no tests ran`), so its gate can only be satisfied by ignoring the instruction or by inventing the directory mid-change.

## In scope
- **Decided 2026-10-04 (Q-1 = (a), Q-6 = (a2)):** remove the four dangling `uv run pytest tests/architecture/ -v` citations — `AGENTS.md:212` (Phase Matrix REFACTOR cell), `AGENTS.md:579` (Phase 5 step 13), `.agents/skills/verify/SKILL.md:88` and `:103` — and re-point the architecture check at the **manual** boundary review `AGENTS.md:592-593` already defines, recorded in `docs/verification/<name>.md`. No `tests/architecture/` directory is created.
- **Decided 2026-10-04 (Q-5 = fold in):** the 4 private-module import fixes — `src/backend/authentication/feature_settings.py:7`, `src/backend/eventbus/feature_settings.py:7`, `src/backend/usermanagement/feature_settings.py:7` (import `logged` from `backend.logging`, as `AGENTS.md:768` requires) and `src/main.py:67` (stop importing the private `_registry`). Four one-line import rewrites.
- Keep `AGENTS.md`, the `verify` skill and the Phase Matrix mutually consistent (they currently promise the same gate in three different words), and mirror the `AGENTS.md:592-593` wording so the re-point does not read as a new rule.

## Out of scope
- Changing the project-structure rules themselves (`AGENTS.md` "Project Structure" stays as it is).
- Any `src/` **move** that architecture tests might reveal — that would be a separate REFACTOR/ISSUE. (The 4 import rewrites are in scope per Q-5; no code moves.)
- Creating `tests/architecture/` or any CI-enforced boundary rule — see Q-4, still open as a backlog question.

## Affected features
Process guidance (`AGENTS.md`, `.agents/skills/verify/SKILL.md`) plus four `src/` import sites: `backend/authentication/`, `backend/eventbus/`, `backend/usermanagement/` (one line each) and the composition root `src/main.py`. No `tests/` change.

## Constraints and risks
- **`src/` is now touched, so the light docs-only Phase 5 gate does not apply.** The no-behavior-delta proof is the **full regression suite GREEN** (`uv run pytest tests/`), plus `uv run ruff check <changed-paths>` and `uv run mypy src/`; the public-API contract suites (`tests/contract/*/test_public_api.py`) pin the names being switched to and must stay GREEN.
- Landing order (Q-3, answered): this change edits **different lines** from `workflow-docs-nits`, `value-triage-gate` and `spec-interview-protocol` (which land in that order), so it has no `Depends on:` — but if `value-triage-gate` lands first, re-read the Phase Matrix cell before editing it.

## Acceptance signal (plain language)
Running the REFACTOR Phase 5 instruction from `AGENTS.md` no longer errors: either the command finds tests and passes, or the text no longer cites a directory that does not exist.

## Value triage
- **Overlap:** the review skill's "verify architecture rules" step (`AGENTS.md:593`) is the human/agent counterpart; nothing executable exists.
- **Beneficiary:** every REFACTOR and CROSS-CUTTING change (the gate is in their Phase 5), and the `structure-map` change (its P.2 hit the same wall).
- **Score:** 3/5 — a small honesty fix that removes a false gate; the "build the tests" option is larger and its value depends on whether automated boundary checks are actually wanted.
- **Recommendation:** decide Q-1 first; option (a) is a 3-line DOCS/CHORE, option (b) is a FEATURE with its own spec.

## Prep log
| Step | Date | Result |
|---|---|---|
| P.1 Frame | 2026-10-03 | TODO + question file created on `main`; type provisionally **DOCS/CHORE** (no spec requires the directory, so this is not a defect against an approved spec; the "build the tests" alternative would be a FEATURE → Q-1 decides). Evidence verified on `main`: `tests/architecture/` absent; cited by `AGENTS.md:212`, `:579` and `verify/SKILL.md:88`, `:103`. Discovered during the `structure-map` P.2 interrogation |
| P.2 Interrogate (5 questions) | 2026-10-04 | **DONE** — Q-1/Q-2/Q-3 narrowed by evidence (E-1…E-12): the dangling citation count is **4 in 2 files** (`AGENTS.md:212`, `:579`; `verify/SKILL.md:88`, `:103`), CI never runs the command (so the gate was enforced by nobody), option (a) costs 4 line edits with no bump, option (b) costs ~60–90 lines of stdlib `ast` tests but has **21 day-one violations** under the strict import rule and 4 under the no-private-import rule, and the `model/`/`services/` rule is untestable (those directories do not exist). Classification verdict: **DOCS/CHORE for both options** |
| P.3 Answer (round 1: Q-1 answered, Q-2 closed) | 2026-10-04 | **WAITING** — **Q-1 = (a) remove/qualify the references** (no `tests/architecture/` in this change; DOCS/CHORE confirmed). **Q-2 closed as moot** (it was conditional on (b)). Still open: the (a1)/(a2) sub-variant → **Q-6**, plus **Q-3** (landing order), **Q-4** (CI-enforced vs agent-only), **Q-5** (the 4 private-module imports) |
| P.3 Answer (round 2: Q-3, Q-5, Q-6) | 2026-10-04 | **DONE except Q-4.** **Q-6 = (a2)** — re-point the four citations at the manual boundary check (`AGENTS.md:592-593`), no directory named. **Q-5 = fold in** — the 4 private-module import fixes join the scope, so `src/` is touched and Phase 5 runs the full regression suite + ruff + mypy (not the docs-only light gate). **Q-3 = land independently** — the three colliding items land `workflow-docs-nits` → `value-triage-gate` → `spec-interview-protocol`; this one edits different lines. Only **Q-4** (should a boundary rule be CI-enforced at all) stays open — it is a backlog question, not a blocker for P.4 |
| P.3 Answer (round 3: Q-4) | 2026-10-04 | **DONE — all 6 questions ANSWERED.** **Q-4 = (a) manual only, no follow-up**: no `tests/architecture/` suite and no CI boundary rule; the ruff `TID251` banned-api option was offered and not taken, so the 4 import fixes are made but not guarded. Next: **P.4** — create `chore/architecture-tests-missing` worktree + scope record → READY |
| P.4 Draft spec / triage / baseline / scope | | |
| P.5 Self-consistency | | |
| P.4 Draft scope + worktree | 2026-10-04 | **DONE → READY** — branch `chore/architecture-tests-missing` + worktree from `main` @ `99ce0b8`; scope record `docs/verification/architecture-tests-missing.md` (`b9afe76`, +181): verbatim before/after for the 4 doc citations (`AGENTS.md:212`/`:579`, `verify/SKILL.md:88`/`:103`) and the import rewrites; no-behavior-delta proof; Phase 5 gate; bump = none. **F-1 scope finding:** only **3** of Q-5's 4 import fixes are DOCS/CHORE-actionable — `src/main.py:67` imports the private `_registry` to *install* the proxy-wired singleton, and `docs/specs/settings.md` REQ-014 exposes no public setter, so any substitution is a behavior change. It is out of scope here; the fix needs a public `set_settings_registry()` → settings-spec amendment (REQ-014), framed as a separate backlog item. Also corrected two drifted P.2 evidence numbers (`AGENTS.md:1145`, version `0.6.1`) |
| Phase 4 + 5 (S4.2, S5.1/S5.2) | 2026-10-04 | **DONE / PASS (light)** — 4 citations removed (`AGENTS.md` Phase Matrix REFACTOR cell + Phase 5 step 13, `verify/SKILL.md` 2 bullets) and re-pointed at the manual boundary review; 3 private-import fixes (`authentication`/`eventbus`/`usermanagement` `feature_settings.py:7` → `from backend.logging import logged`); `src/main.py` untouched (F-1). `rg tests/architecture AGENTS.md .agents` → no matches; `ruff check .` clean; `mypy src/` clean (83 files); affected-feature tests 102 + 186 passed; **full suite 728 passed, 1 skipped — identical to baseline**; `check_traceability.py` PASS. Commits `5902af4`, `acf846b` (P-42/P-43), `11378fa`. Coalesced per P-41 |
| Phase 6 (S6.1–S6.4) | 2026-10-04 | **REVIEW CLEAN** (F-1..F-4 resolved/accepted, none open; commit `383cf44`) → **no version bump** (DOCS/CHORE) → **PR #65**: https://github.com/jackthenet/python-template/pull/65. **WAITING** for human merge; S7.1 follows (confirm CI green) |
