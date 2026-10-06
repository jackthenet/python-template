# TODO: <change-name>

Backlog item for one planned change, created at **P.1 Frame** from this template and named `<change-name>.md`. One file per change.

This is a **planning record, not normative**: like `docs/questions/`, it is committed directly to `main` (see "Phase P: PREPARE" in `AGENTS.md`). It carries no approval gate — the spec does.

- **Status:** PREPARING  <!-- PREPARING | QUESTIONS-ANSWERED | READY | IN-WORKFLOW | WAITING | MERGED | DROPPED -->
- **Change type:** <ISSUE | FEATURE | CROSS-CUTTING | REFACTOR | DOCS/CHORE>
- **Created:** <YYYY-MM-DD>
- **Question file:** `docs/questions/<change-name>.md`
- **Spec:** `docs/specs/<change-name>.md`  <!-- FEATURE/CROSS-CUTTING only; n/a for the other types -->
- **Worktree:** <created at P.4> `../<repo-name>-worktrees/<type>/<change-name>`
- **Depends on:** <changes that must be merged before this one may start; "none">
- **Related specs:** <docs/specs/ files this change touches or reuses>

## Goal (one line)
<what the change delivers, in one sentence>

## Why
<the motivation, symptom, or opportunity behind the change>

## In scope
- <bullet>

## Out of scope
- <bullet>

## Affected features
<`src/backend/<feature>` / `src/frontend/<feature>` paths, or "new feature: `src/backend/<name>`">

## Constraints and risks
- <bullet>

## Value triage (<YYYY-MM-DD>, pre-workflow)
- **Overlap:** <what in this repository already covers it — name the file/function; "none">. If it overlaps: <the existing feature to extend instead of a new one>
- **Beneficiary:** <who benefits and how (the end user of this project); "unclear" / "too vague to judge" instead of guessing>
- **Score: <1-5>/5** — <one sentence explaining the score>  <!-- 5 = clear user value, new, small change · 3 = some value, or partly overlapping, or moderate effort · 1 = no clear value, duplicate, or large/risky change -->
- **Recommendation:** implement / merge into <existing feature> / drop
- **Decision:** <the user's answer + date>  <!-- recorded when the user answers; a dropped TODO moves to docs/todo/archive/ with its question file -->

## Acceptance signal (plain language)
<how we will know it works when it is done — the observable outcome, not the AC IDs>

## Prep log
| Step | Date | Result |
|---|---|---|
| P.1 Frame | | |
| P.2 Interrogate (<n> questions) | | |
| P.3 Answer (<n> answered) | | |
| P.4 Draft spec / triage / baseline / scope | | |
| P.5 Self-consistency (FEATURE/CROSS-CUTTING) | | |
