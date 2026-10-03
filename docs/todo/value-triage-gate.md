# TODO: value-triage-gate

Backlog item for one planned change, created at **P.1 Frame** from this template and named `value-triage-gate.md`. One file per change.

This is a **planning record, not normative**: like `docs/questions/`, it is committed directly to `main` (see "Phase P: PREPARE" in `AGENTS.md`). It carries no approval gate — the spec does.

- **Status:** WAITING  <!-- PREPARING | QUESTIONS-ANSWERED | READY | IN-WORKFLOW | WAITING | MERGED -->
- **Change type:** DOCS/CHORE  <!-- codifies process guidance; no externally observable behavior delta -->
- **Created:** 2026-10-03
- **Question file:** `docs/questions/value-triage-gate.md`
- **Spec:** n/a  <!-- DOCS/CHORE: no spec -->
- **Worktree:** <created at P.4> `../python-template_kopie-worktrees/chore/value-triage-gate`
- **Depends on:** prepared-workflow (merged: `4b42c58`); **workflow-docs-nits** (landing order decided 2026-10-04 — it lands first, this change builds on its `specify/SKILL.md:45/46` qualifiers)
- **Related specs:** none (no `docs/specs/` file is touched)

## Goal (one line)
Make **value triage** a named, mandatory step of the workflow: before any TODO is implemented, check it against existing functionality, score its value 1–5, and get the user's implement / merge-into-existing / drop decision.

## Why
The practice already happened by hand on 2026-10-03 for five backlog items — each now carries a hand-written `## Value triage` section (`docs/todo/docs-path-ci-trigger.md:35`, `split-archived-qa.md:35`, `workflow-docs-nits.md:40`, `track-python-skill.md:39`, `remove-spec-tdd-driver.md:39`; commit `891b31f`) — and it paid for itself: two items were scored 1/5 and recommended **dropped**, one was bundled instead of split, and one changed scope from "update the driver" to "delete the driver". Nothing in `AGENTS.md` or the skills **requires** it, and `docs/todo/template.md` has no section for it, so the next change gets the triage only if the agent happens to remember. Codifying it turns a lucky outcome into a default.

## Rule text to add (verbatim from the request)
```text
Before implementing any TODO, decide whether it is worth doing.

For each TODO:
1. Check the codebase for existing functionality that covers it. Name the
   file/function if there is overlap. If it overlaps, propose extending that
   feature instead of building a new one.
2. Identify who benefits and how (the end user of this project). If the
   value is unclear or the TODO is too vague to judge, say so instead of guessing.
3. Give a score from 1-5:
   5 = clear user value, new, small change
   3 = some value, or partly overlapping, or moderate effort
   1 = no clear value, duplicate, or large/risky change
   Add one sentence explaining the score.
4. Recommend: implement / merge into <existing feature> / drop.

Prefer reusing existing code and the smallest diff that delivers the value.
Dropping low-value or duplicate TODOs is a good outcome.

Present the results as a table (ID | TODO | score | recommendation | reason),
then ask me which to implement, merge, or drop. Do not implement anything
until I answer.
```

## In scope
- **Decided 2026-10-04 (Q-1 = (b)):** the triage is a **mandatory Value triage clause inside P.1 Frame** plus one short "Backlog value triage" paragraph under Phase P — **not** a new numbered `P.0` step. No new step row, no Phase P table/diagram/todo-set changes, and `specify/SKILL.md:45`/`:46` are **not** touched (which dissolves the collision with `workflow-docs-nits`).
- The four checks and the 1–5 anchors above, as normative text, plus the "say so instead of guessing" clause for vague items.
- The required output: the `ID | TODO | score | recommendation | reason` table, one batched ask, and the hard rule **no implementation before the user answers**.
- Where the text lands (all `.md`): `AGENTS.md` — the P.1 Frame row of the Phase P atomic-steps table, the Phase Matrix "P Prepare" cell, the Multi-change scheduling rules, Agent Obligations and Prohibitions; `docs/todo/template.md` — a `## Value triage` section matching the five existing hand-written ones; `.agents/skills/specify/SKILL.md` — the P.1 area only (its Outputs/Done wording), **not** the `:45`/`:46` step-order and ownership lists.
- **Decided 2026-10-04 (Q-3 = (a) + Q-7 = (i)):** add **`DROPPED`** to the `Status:` vocabulary (a row in the `AGENTS.md:155-162` advance table, a value in the `docs/todo/template.md:7` comment, a mention in `.agents/skills/git/SKILL.md:65`), and **move dead records out of the live backlog**: `docs/todo/archive/<name>.md` and `docs/questions/archive/<name>.md`, moved by the orchestrator **at the drop decision** and **at post-merge cleanup (S7.1)**, the question file moving with its TODO file. The live guidance that names the two paths (Phase P artifacts table, planning-records section, Ready-selection order, cleared-gate test, `git/SKILL.md`) must be updated to match.

## Out of scope
- Changing what any existing gate requires (the READY gate, the Spec Approval Gate, RED/GREEN, Phase 5/6 gates) — the triage sits **before** them.
- The "Ponytail, lazy senior dev mode" section in `AGENTS.md` — it is the code-level counterpart and stays as is; the new text references it rather than restating it.
- Any new script, CI job, or machine-readable score validation — the triage is a documented step, not a checker.
- `src/`, `tests/`, `docs/specs/`, `.github/workflows/`.

## Affected features
None — process documentation and skill text only; no `src/backend/` or `src/frontend/` path is touched.

## Constraints and risks
- **Overlap with the existing Ponytail ladder** (`AGENTS.md:23-33`, rungs 1–2: "Does this need to be built at all? (YAGNI)" / "Does it already exist in this codebase?"). That ladder governs *how* a change is written; this governs *whether* it runs at all. The new text must cross-reference it, not duplicate it — two copies of the same rule drift.
- **Scheduling cost.** Phase P is built around "never idle" (AGENTS.md, "Multi-change scheduling"). A per-item user question would add a ⏸ per change; the rule must therefore be **batched** — one table over the backlog, one ask — so it costs one round-trip per sweep.
- **Subjectivity.** Without the "value unclear / too vague → say so" clause, a 1–5 score invites invented user value; the anchors must stay verbatim.
- Skill and `AGENTS.md` text is live protocol guidance: wording that reads as a *blocking* gate on every change (rather than one batched backlog gate) would change scheduling behavior — still DOCS/CHORE in kind, but a wording trap to catch in review.

## Value triage (2026-10-03, pre-workflow) — the rule applied to itself
- **Overlap:** the *principle* already exists in `AGENTS.md:23-33` (Ponytail rungs 1–2) and the *procedure* already exists in practice in five `docs/todo/*.md` `## Value triage` sections — but neither is required anywhere, and `docs/todo/template.md` has no slot for it. So this change codifies a proven practice rather than inventing one; the diff is text in three existing files.
- **Beneficiary:** whoever owns the backlog (the user, and the orchestrator picking the next READY change). Measured, not guessed: the five 2026-10-03 triages dropped 2 items, bundled 1, and re-scoped 1 — work that would otherwise have been spent on `docs-path-ci-trigger` and `split-archived-qa` alone.
- **Score: 5/5** — clear value (it demonstrably prevents work), new to the protocol, and a small doc-only diff in files that already describe Phase P.
- **Recommendation: implement** as one bundle (not split into per-file changes).

## Backlog value triage sweep (2026-10-03, produced during this change's P.2)

The table the codified step would produce, run over all 16 backlog items — recorded here so the
decision is in one place (the step itself is not yet normative; this change is what would make it so).

| ID | TODO | score | recommendation | reason |
|---|---|---|---|---|
| 1 | value-triage-gate | 5/5 | implement (one bundle) | codifies a practice already used in 5 TODOs; 3 `.md` files, no gate changed |
| 2 | api-keys | 5/5 | implement | clear user value, new capability; the enforcement half already exists |
| 3 | notifications | 4/5 | implement | new capability; reuses mail + eventbus; part of the value waits on an API surface |
| 4 | security-changelog-license | 4/5 | implement | the missing LICENSE is a legal gap, not cosmetic |
| 5 | spec-interview-protocol | 4/5 | implement **after** #1 | same P.2/P.3 surface; its own TODO declares the order |
| 6 | structure-map | 4/5 | implement | one capability, self-contained; touches `AGENTS.md` in one line only |
| 7 | remove-spec-tdd-driver | 4/5 | decided — **WAITING**, PR #62 | user chose implement |
| 8 | pyproject-tooling-gaps | 3/5 | implement the cheap items only | the complexipy gate/version gap is real; two headline review claims were false |
| 9 | python-3.15 | 3/5 | implement Option A, defer Option B | future-proofing; blocked on 3.15 final wheels |
| 10 | structlog-logging | 3/5 | decide at P.3 first | total overlap with the existing logging feature; cost disproportionate to a dependency swap |
| 11 | update-readme | 3/5 | implement | real gap (30-line README), low value per unit effort |
| 12 | workflow-docs-nits | 2/5 | merge into #1 or drop | overlaps #1's files (`template.md`, `specify/SKILL.md:45`) — see its Q-3 |
| 13 | tenacity-rich-cachetools | 2/5 | decline | no consumer; an unused dependency fails the `deptry` gate |
| 14 | docs-path-ci-trigger | 1/5 | drop | the job asserts nothing about planning records |
| 15 | split-archived-qa | 1/5 | drop | churns a frozen record for a nicety nothing reads |
| 16 | track-python-skill | 4/5 | done — `MERGED` (`c2342b6`) | landed directly on `main`; deviation recorded in its TODO |

## Acceptance signal (plain language)
`AGENTS.md`, the `specify` skill and `docs/todo/template.md` all name the triage step, its four checks, its 1–5 anchors, the required table, and the "ask before implementing" rule — and cross-reference the Ponytail ladder instead of restating it. A backlog item framed **after** the merge gets a filled-in Value triage section without the user having to ask, and a dropped item is left on disk with its reason. `git diff --name-status` shows only `.md` paths; `mkdocs build --strict` and the traceability check still pass.

## Prep log
| Step | Date | Result |
|---|---|---|
| P.1 Frame | 2026-10-03 | TODO + question file created on `main`; type DOCS/CHORE; todo set for this change; **value triage 5/5, implement as one bundle** |
| P.2 Interrogate (5 questions) | 2026-10-04 | **DONE** (the question file was written; this Prep-log row was missing and is filled in now) — Q-1…Q-5 recorded, with the **placement cost analysis** (a numbered P.0 forces ~13 coordinated `AGENTS.md`/skill edits and collides with the todo-set, status-vocabulary and READY rules) and the finding that **all five triages actually performed are recorded inside the P.1 record**, i.e. the practice as run is already a P.1 sub-item |
| P.3 Answer (round 1: Q-3, Q-4) | 2026-10-04 | **WAITING** — **Q-4 = (a)**: landing order fixed as `workflow-docs-nits` → **this change** → `spec-interview-protocol`, so `workflow-docs-nits` items (a)+(b) are not folded here and this change gains `Depends on: workflow-docs-nits`. **Q-3 = (a)**: add `DROPPED` to the `Status:` vocabulary — **plus the user's addition** that dropped **and merged** records should move to a different folder, which is a new question, **Q-7** (layout + when the move happens + whether `docs/questions/<name>.md` moves too). Still open: **Q-1** (P.0 step vs P.1 clause), **Q-2** (per-item vs global stop), **Q-5** (packaging + recording), **Q-7** |
| P.3 Answer (round 2: Q-1, Q-7) | 2026-10-04 | **WAITING** — **Q-1 = (b)**: the triage is a **clause inside P.1 Frame** + a "Backlog value triage" paragraph, not a numbered `P.0` step (so no Phase P table/diagram/todo-set edits, and `specify/SKILL.md:45`/`:46` stay untouched — the `workflow-docs-nits` collision dissolves). **Q-7 = (i)**: `docs/todo/archive/<name>.md` + `docs/questions/archive/<name>.md`, moved at the drop decision and at S7.1, question file moving with the TODO file — the live guidance that names those two paths must be updated. Still open: **Q-2** (per-item vs global stop), **Q-5** (packaging + recording) |
| P.4 Draft scope + create branch/worktree | | |
| P.5 Self-consistency | | n/a (DOCS/CHORE) |
