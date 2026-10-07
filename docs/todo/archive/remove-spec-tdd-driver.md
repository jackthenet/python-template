# TODO: remove-spec-tdd-driver

Backlog item for one planned change, created at **P.1 Frame** from this template and named `remove-spec-tdd-driver.md`. One file per change.

This is a **planning record, not normative**: like `docs/questions/`, it is committed directly to `main` (see "Phase P: PREPARE" in `AGENTS.md`). It carries no approval gate — the spec does.

^- **Status:** MERGED  <!-- PREPARING | QUESTIONS-ANSWERED | READY | IN-WORKFLOW | WAITING | MERGED -->
- **Change type:** DOCS/CHORE
- **Created:** 2026-10-03
- **Question file:** `docs/questions/remove-spec-tdd-driver.md`
- **Spec:** n/a  <!-- DOCS/CHORE: no spec -->
- **Worktree:** <created at P.4> `../python-template_kopie-worktrees/chore/remove-spec-tdd-driver`
- **Depends on:** prepared-workflow (merged: `4b42c58`)
- **Related specs:** none (no `docs/specs/` file is touched)

## Goal (one line)
Delete the unused `.pi/workflows/spec-tdd.workflow.ts` driver so no artifact in the repository still describes the pre-Phase-P protocol.

## Why
`prepared-workflow` left the driver stale: its Phase 1 node still instructs a subagent to create the branch, interrogate the idea, and write the specification (`.pi/workflows/spec-tdd.workflow.ts:65`), which is exactly the work Phase P now front-loads. The finding was accepted as F-10 and deferred as follow-up #3 (`docs/verification/prepared-workflow.md:80`). The 2026-10-03 value triage scored *updating* it 4/5, and the user decided the driver is not used at all — so deletion is the smaller diff that removes the contradiction.

## In scope
- Delete `.pi/workflows/spec-tdd.workflow.ts`.
- Record the triage decisions that close the other `prepared-workflow` follow-ups as **dropped** (archived-Q&A split, CI path trigger, shared cache dirs) with their reasons.

## Out of scope
- `.pi/subagents.json` — pi's own subagent state, gitignored (`.gitignore:234`), not a protocol artifact.
- Any change to `AGENTS.md`, the skills, `docs/specs/`, `src/`, `tests/`, or `.github/workflows/`.
- Rewriting the historical records that mention the driver (`docs/verification/prepared-workflow.md:80`, `:347`, `:383`).

## Affected features
None — no `src/backend/` or `src/frontend/` path is touched.

## Constraints and risks
- Nothing references the file except historical verification records; those stay unchanged, so a repo-wide grep will still show its name inside `docs/verification/`.
- `.pi/workflows/` becomes empty and therefore stops existing in the tree (git does not track empty directories).
- No externally observable behavior delta: the driver is an optional pi workflow entry point, not the normative protocol (`AGENTS.md` + the skills carry Phase P).

## Value triage (2026-10-03, pre-workflow)
- **Overlap:** the live protocol already exists in `AGENTS.md` ("Phase P: PREPARE") and `.agents/skills/specify/SKILL.md`; the driver duplicates it and is adjudicated stale as F-10 (`docs/verification/prepared-workflow.md:383`). The alternative — *update* the driver (the original follow-up #3) — was rejected: it keeps a second copy of the protocol that must track `AGENTS.md` forever.
- **Beneficiary:** anyone (agent or human) who could invoke `.pi/workflows/spec-tdd.workflow.ts` and be told to create the branch, interrogate and write the spec inside Phase 1 (`:65`) — the exact work Phase P front-loads.
- **Score: 4/5** — a one-path deletion of a 187-line file with **zero consumers** (`git ls-files .pi` lists exactly this path; no CI job, test, `package.json`/`tsconfig`, pre-commit hook or config references it) removes the last artifact describing the pre-Phase-P protocol; it is not a 5 because the payoff is hygiene, not new capability.
- **Decision:** user chose **implement as logged** — scope unchanged (delete the driver **and** record the three `prepared-workflow` follow-ups as dropped with reasons).

## Acceptance signal (plain language)
`git ls-files .pi` lists no workflow script, the only remaining mentions of `spec-tdd.workflow` are inside historical verification records, and the DOCS/CHORE light gate passes: a `git diff --name-status` scope proof showing exactly one deleted `.ts` path (no `src/`, `tests/`, `pyproject.toml`, `.github/` or config path touched) plus lint and type checks where applicable — no Python path is touched, so no full-suite run is required by this change's gate set.

## Prep log
| Step | Date | Result |
|---|---|---|
| P.1 Frame | 2026-10-03 | TODO + question file created on `main`; type DOCS/CHORE; todo set #9–#13 |
| P.2 Interrogate (0 questions) | 2026-10-03 | **DONE** — no question needs user input; overlap check (`docs/specs/` 13 files, `docs/todo/`, in-flight worktrees) clean; every raised point closed from evidence (the driver is the only tracked `.pi` path; no CI/test/config/dependency reference to it) |
| P.3 Answer (0 answered) | 2026-10-03 | **no-op** — 0 questions to present, 0 rounds; question file header set to `ALL ANSWERED` |
| Value triage (pre-workflow) | 2026-10-03 | **4/5 — implement as logged** (scope unchanged); user decision recorded above. Not yet started: held at P.4, planning-record logging only |
| P.4 Draft scope + create branch/worktree | 2026-10-03 | **DONE** — branch `chore/remove-spec-tdd-driver` + worktree created from `main` (`c2342b6`); `docs/verification/remove-spec-tdd-driver.md` scope record committed (`de57618`) with the exact one-path scope, the follow-up closures (split-archived-qa DROPPED 1/5, docs-path-ci-trigger DROPPED 1/5, driver update CLOSED BY THIS DELETION, shared-cache-dirs DROPPED) and a 9-check independently re-verified no-behavior-delta proof |
| P.5 Self-consistency (n/a — DOCS/CHORE) | | n/a |
| Phase 4 (S4, make the change) | 2026-10-03 | **DONE** — `git rm .pi/workflows/spec-tdd.workflow.ts` (commit `a7a6b04`); scope proof vs merge-base `c2342b6` = exactly `D` the `.ts` + `A` the scope record; `git ls-files .pi` empty |
| Phase 5 (S5, light gate set) | 2026-10-03 | **PASS** (commit `b8f88c6`) — ruff clean, `ruff format --check` 323 files already formatted, `mypy src/` Success (83 files), `check_traceability.py` PASS (746 rows / 129 IDs / 713 test functions), `mkdocs build --strict` exit 0; no full-suite run (no Python/test path touched — CI runs it on the PR) |
| Phase 6 (S6, review + PR) | 2026-10-03 | **CLEAN, 0 open findings** (report commit `4bd9247`); no version bump (DOCS/CHORE, stays `0.6.0`); **PR #62** open → https://github.com/jackthenet/python-template/pull/62 |
| Post-merge cleanup (S7.1) | 2026-10-03 | **DONE** — **PR #62 merged on `main`** (`a2000c2`, verified reachable via `git merge-base --is-ancestor a2000c2 origin/main`; `.pi/workflows/` no longer exists, `git ls-files .pi` empty). Worktree `python-template_kopie-worktrees/chore/remove-spec-tdd-driver` removed, local branch deleted (`git branch -d`, merged), remote branch `origin/chore/remove-spec-tdd-driver` deleted. `git worktree list` → primary only |
