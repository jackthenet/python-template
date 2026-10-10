# TODO: docs-path-ci-trigger

Backlog item for one planned change, created at **P.1 Frame** from this template and named `docs-path-ci-trigger.md`. One file per change.

This is a **planning record, not normative**: like `docs/questions/`, it is committed directly to `main` (see "Phase P: PREPARE" in `AGENTS.md`). It carries no approval gate — the spec does.

- **Status:** DROPPED  <!-- PREPARING | QUESTIONS-ANSWERED | READY | IN-WORKFLOW | WAITING | MERGED | DROPPED -->
  <!-- advanced 2026-10-07: `value-triage-gate` merged (PR #70, d77e833) and added `DROPPED` to the vocabulary, so the drop decision recorded below is now expressible in `Status:`; both records archived -->
- **Disposition:** **DROPPED** — user decision, 2026-10-04 (value triage 1/5). At the time the `Status:` vocabulary had no value for a dead item (`value-triage-gate` Q-3, then unanswered); that change has since merged, so the status line now carries the decision.
- **Change type:** DOCS/CHORE
- **Created:** 2026-10-03
- **Question file:** `docs/questions/docs-path-ci-trigger.md`
- **Spec:** n/a  <!-- DOCS/CHORE: no spec -->
- **Worktree:** <created at P.4> `../python-template_kopie-worktrees/chore/docs-path-ci-trigger`
- **Depends on:** prepared-workflow (merged: `4b42c58`)
- **Related specs:** none (no `docs/specs/` file is touched)

## Goal (one line)
Add `docs/todo/**` and `docs/questions/**` to the `paths:` filters of `.github/workflows/spec-validation.yml` so a planning-record-only PR still runs the spec-validation job.

## Why
Recorded as follow-up #2 in the merged `prepared-workflow` change (`docs/verification/prepared-workflow.md:80`): the two new planning-record folders were not added to the workflow's path filters, so a PR that touches only planning records does not trigger the job.

## In scope
- <to be established at P.2 — the two `paths:` blocks (pull_request + push) in `.github/workflows/spec-validation.yml`>

## Out of scope
- Changing what the job actually validates (`scripts/verify_spec.py`, `scripts/check_traceability.py`).
- Adding path filters to the other workflows (`lint.yml`, `quality.yml`).

## Affected features
None — CI configuration only; no `src/backend/` or `src/frontend/` path is touched.

## Constraints and risks
- CI configuration is a trust boundary for the gates: a filter that fires on paths the job cannot validate produces green runs that prove nothing, and adds runner minutes to every planning-record commit (which the workflow makes frequently — every `Status:` advance).

## Value triage (2026-10-03, pre-workflow)
- **Overlap:** the job already validates the paths that matter — `check_traceability.py:129-131` reads `docs/verification/traceability.md`, `docs/specs/` and `tests/`, all three of which are already in the `paths:` list (`spec-validation.yml:6-14`). Planning records carry no gate by design (`AGENTS.md`, "Planning records (owner: the orchestrator)").
- **Beneficiary:** nobody — the trigger would fire a job that asserts nothing about `docs/todo/` or `docs/questions/`.
- **Score: 1/5** — it adds CI cost and a false signal of coverage without any new check.
- **Recommendation: drop.** Logged because the user wants the full backlog recorded; if a real check over planning records is ever wanted (e.g. `Status:` value validation), that belongs in `scripts/check_traceability.py` first, and the path filter becomes worthwhile only then.

## Acceptance signal (plain language)
<to be written if the change is ever picked up>

## Prep log
| Step | Date | Result |
|---|---|---|
| P.1 Frame | 2026-10-03 | TODO + question file created on `main`; type DOCS/CHORE; **value triage 1/5, recommended drop** |
| P.2 Interrogate | 2026-10-03 | **not run — recommended DROPPED (1/5), awaiting the user's decision.** The drop is already recorded in the merged `remove-spec-tdd-driver` scope record as one of the prepared-workflow follow-ups closed as dropped; P.2 would be ceremony unless the user decides to implement it |
| P.3 Answer (drop decision) | 2026-10-04 | **CLOSED AS DROPPED** — the user confirmed the drop (the alternative was to keep it and run P.2). Nothing enters the workflow; the file stays as the record of why. Re-open trigger: a real check over planning records (e.g. `Status:` value validation) lands in `scripts/check_traceability.py` first |
| P.4 Draft spec / triage / baseline / scope | | |
| P.5 Self-consistency | | |
