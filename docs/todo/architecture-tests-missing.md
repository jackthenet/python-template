# TODO: architecture-tests-missing

Backlog item for one planned change, created at **P.1 Frame** from the template.

This is a **planning record, not normative**: like `docs/questions/`, it is committed directly to `main` (see "Phase P: PREPARE" in `AGENTS.md`). It carries no approval gate — the spec does.

- **Status:** PREPARING  <!-- PREPARING | QUESTIONS-ANSWERED | READY | IN-WORKFLOW | WAITING | MERGED -->
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
- One of the two resolutions in Q-1 of the question file: (a) remove/qualify the three dangling references, or (b) create `tests/architecture/` with executable rules for the boundaries the process text already names.
- Whatever the resolution, keep `AGENTS.md`, the `verify` skill and the Phase Matrix mutually consistent (they currently promise the same gate in three different words).

## Out of scope
- Changing the project-structure rules themselves (`AGENTS.md` "Project Structure" stays as it is).
- Any `src/` move that architecture tests might reveal — that would be a separate REFACTOR/ISSUE.

## Affected features
None (process guidance and/or `tests/architecture/`).

## Constraints and risks
- If the tests are created, they must pass on the current tree (a gate that fails on day one blocks every REFACTOR change), and they must not duplicate the import rules `ruff`/`deptry` already enforce.
- `AGENTS.md` is also being edited by `value-triage-gate` (WAITING) and `workflow-docs-nits` (WAITING) — three changes touching the same file means the sequencing question is real (see its Q-4/Q-3).

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
| P.2 Interrogate (<n> questions) | | |
| P.3 Answer (<n> answered) | | |
| P.4 Draft spec / triage / baseline / scope | | |
| P.5 Self-consistency | | |
