# TODO: workflow-docs-nits

Backlog item for one planned change, created at **P.1 Frame** from this template and named `workflow-docs-nits.md`. One file per change.

This is a **planning record, not normative**: like `docs/questions/`, it is committed directly to `main` (see "Phase P: PREPARE" in `AGENTS.md`). It carries no approval gate — the spec does.

- **Status:** WAITING  <!-- PREPARING | QUESTIONS-ANSWERED | READY | IN-WORKFLOW | WAITING | MERGED -->
- **Change type:** DOCS/CHORE
- **Created:** 2026-10-03
- **Question file:** `docs/questions/workflow-docs-nits.md`
- **Spec:** n/a  <!-- DOCS/CHORE: no spec -->
- **Worktree:** <created at P.4> `../python-template_kopie-worktrees/chore/workflow-docs-nits`
- **Depends on:** prepared-workflow (merged: `4b42c58`)
- **Related specs:** none (no `docs/specs/` file is touched)

## Goal (one line)
Apply the four cosmetic wording/consistency fixes that `prepared-workflow` accepted as follow-ups but deliberately left undone (`docs/verification/prepared-workflow.md:583-587`).

## Why
The Phase 6 review of `prepared-workflow` closed every finding and listed four accepted follow-ups, each adjudicated "cosmetic; blocks no gate": leaving them scattered means the next reader of the templates and the `specify` skill still meets step lists that read as if P.5 applied to every change type.

## In scope
- `docs/todo/template.md:44` — qualify the Prep-log row as `P.5 Self-consistency (FEATURE/CROSS-CUTTING)` so it matches the already-qualified `Spec:` row at `:11`.
- `.agents/skills/specify/SKILL.md:14`, `:45`, `:46` — add the "(FEATURE/CROSS-CUTTING)" qualifier where P.5 (and S1.4) are listed without their types, so they read like `AGENTS.md:175`.
- `docs/questions/template.md:9` — keep the header `Status:` producer in sync with the F-5 ownership table (add the row there).
- `docs/verification/prepared-workflow.md` (S6.9 sweep table) — correct the hit counts (24 / 42 → 25 / 43) or add the missing `PROBLEMS.md:377` row.

## Out of scope
- Any change to what a gate requires — the READY gate, the Phase Matrix, and the atomic-step tables stay byte-identical in meaning.
- `AGENTS.md`, `docs/specs/`, `src/`, `tests/`, `.github/workflows/`.
- Re-opening any closed finding of `prepared-workflow`.

## Affected features
None — process documentation and skill text only; no `src/backend/` or `src/frontend/` path is touched.

## Constraints and risks
- Editing a merged verification record (`prepared-workflow.md`) is a historical-record edit: it must go through a PR (never direct to `main`) and must not rewrite findings, only correct a count. Note that `remove-spec-tdd-driver` deliberately puts *its own* record edits out of scope — if both changes run, this one owns the `prepared-workflow.md` edit and the other must not touch it.
- Skill text is live guidance: a qualifier that accidentally reads as a new gate rule would turn a cosmetic change into a protocol change (reclassification trigger).

## Value triage (2026-10-03, pre-workflow)
- **Overlap:** the governing rules already exist and are correct (`AGENTS.md:175` and the per-type Phase P list in `specify/SKILL.md:18-21`); these four items only make the restatements match them.
- **Beneficiary:** whoever reads the templates and the `specify` skill next — they stop having to infer that P.5 is spec-types-only.
- **Score: 2/5** — real but tiny clarity value; nothing is blocked today, so it is worth exactly one bundled chore, not four separate changes.
- **Recommendation: implement as one bundle** (or drop if the backlog stays busy — it never blocks another change).

## Acceptance signal (plain language)
Every place that lists P.5 or S1.4 names the types it applies to; the `prepared-workflow.md` sweep counts match the tree; `git diff --name-status` shows only `.md` paths (no `src/`, `tests/`, config); `mkdocs build --strict` and the traceability check still pass.

## Prep log
| Step | Date | Result |
|---|---|---|
| P.1 Frame | 2026-10-03 | TODO + question file created on `main`; type DOCS/CHORE; **value triage 2/5, bundle-then-implement** |
| P.2 Interrogate (3 questions) | 2026-10-03 | **BLOCKED-USER** — 3 questions needing user input, 9 points closed from evidence. All four In-scope items verified against the tree; two of them are partly no-ops as written: item (c)'s fix actually lives in `AGENTS.md:155-162` (which this TODO excludes from scope) and item (d) edits a frozen merged record. Re-measured sweep counts: 25/43 at `4b42c58` (the claim is true; the gap is exactly `PROBLEMS.md:377`), 47/63 on today's `main`. Real collision found with `value-triage-gate` (same `specify/SKILL.md:45` line + `docs/todo/template.md`) |
| P.3 Answer (round 1: Q-3) | 2026-10-04 | **WAITING** — **Q-3 = (a)**: this change **lands first** of the three `AGENTS.md`/`specify`-skill editors (`workflow-docs-nits` → `value-triage-gate` → `spec-interview-protocol`); items (a)+(b) are not folded into `value-triage-gate`, which now depends on this change. Still open: **Q-1** (item (c) — drop it, or bring `AGENTS.md:155-162` into scope for one row) and **Q-2** (item (d) — touch the frozen `prepared-workflow.md` record or not). Because this change is now first in the queue, those two answers are the critical path for all three |
| P.4 Draft spec / triage / baseline / scope | | |
| P.5 Self-consistency | | n/a (DOCS/CHORE) |
