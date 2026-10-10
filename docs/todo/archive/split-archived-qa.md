# TODO: split-archived-qa

Backlog item for one planned change, created at **P.1 Frame** from this template and named `split-archived-qa.md`. One file per change.

This is a **planning record, not normative**: like `docs/questions/`, it is committed directly to `main` (see "Phase P: PREPARE" in `AGENTS.md`). It carries no approval gate — the spec does.

- **Status:** DROPPED  <!-- PREPARING | QUESTIONS-ANSWERED | READY | IN-WORKFLOW | WAITING | MERGED | DROPPED -->
  <!-- advanced 2026-10-07: `value-triage-gate` merged (PR #70, d77e833) and added `DROPPED` to the vocabulary, so the drop decision recorded below is now expressible in `Status:`; both records archived -->
- **Disposition:** **DROPPED** — user decision, 2026-10-04 (value triage 1/5). At the time the `Status:` vocabulary had no value for a dead item (`value-triage-gate` Q-3, then unanswered); that change has since merged, so the status line now carries the decision.
- **Change type:** DOCS/CHORE
- **Created:** 2026-10-03
- **Question file:** `docs/questions/split-archived-qa.md`
- **Spec:** n/a  <!-- DOCS/CHORE: no spec -->
- **Worktree:** <created at P.4> `../python-template_kopie-worktrees/chore/split-archived-qa`
- **Depends on:** prepared-workflow (merged: `4b42c58`)
- **Related specs:** none (no `docs/specs/` file is touched)

## Goal (one line)
Split the retired central question record `docs/questions/archive-AI_Questions.md` into per-change question files under `docs/questions/`.

## Why
Recorded as follow-up #1 in the merged `prepared-workflow` change (`docs/verification/prepared-workflow.md:79`): the central file was archived rather than decomposed, so historical Q&A is not browsable per change the way the new per-change question files are.

## In scope
- <to be established at P.2 — the split itself: which historical entries map to which change name>

## Out of scope
- Re-opening or re-answering any historical question.
- Changing the live per-change question files of merged changes.

## Affected features
None — no `src/backend/` or `src/frontend/` path is touched.

## Constraints and risks
- `AGENTS.md` forbids re-editing the archived central record ("Historical references to it (ADRs, verification records) are left intact"), so a split means adding new files and leaving or replacing the archive — that tension is exactly why P.2 must resolve the mechanism before any drafting.

## Value triage (2026-10-03, pre-workflow)
- **Overlap:** `docs/questions/archive-AI_Questions.md` already holds the history in one browsable place; `AGENTS.md` explicitly retired the central file and points to it as an archive.
- **Beneficiary:** nobody in the live workflow — no gate, skill or script reads the archive; only a human doing archaeology would.
- **Score: 1/5** — it churns a frozen historical record for a nicety nothing consumes.
- **Recommendation: drop.** Logged because the user wants the full backlog recorded; it should not enter the workflow unless a real need for per-change history appears.

## Acceptance signal (plain language)
<to be written if the change is ever picked up>

## Prep log
| Step | Date | Result |
|---|---|---|
| P.1 Frame | 2026-10-03 | TODO + question file created on `main`; type DOCS/CHORE; **value triage 1/5, recommended drop** |
| P.2 Interrogate | 2026-10-03 | **not run — recommended DROPPED (1/5), awaiting the user's decision.** The drop is already recorded in the merged `remove-spec-tdd-driver` scope record as one of the prepared-workflow follow-ups closed as dropped; P.2 would be ceremony unless the user decides to implement it |
| P.3 Answer (drop decision) | 2026-10-04 | **CLOSED AS DROPPED** — the user confirmed the drop (the alternative was to keep it and run P.2). `docs/questions/archive-AI_Questions.md` stays a single frozen archive, as `AGENTS.md` already requires |
| P.4 Draft spec / triage / baseline / scope | | |
| P.5 Self-consistency | | |
