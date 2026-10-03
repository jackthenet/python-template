# TODO: value-triage-gate

Backlog item for one planned change, created at **P.1 Frame** from this template and named `value-triage-gate.md`. One file per change.

This is a **planning record, not normative**: like `docs/questions/`, it is committed directly to `main` (see "Phase P: PREPARE" in `AGENTS.md`). It carries no approval gate — the spec does.

- **Status:** PREPARING  <!-- PREPARING | QUESTIONS-ANSWERED | READY | IN-WORKFLOW | WAITING | MERGED -->
- **Change type:** DOCS/CHORE  <!-- codifies process guidance; no externally observable behavior delta -->
- **Created:** 2026-10-03
- **Question file:** `docs/questions/value-triage-gate.md`
- **Spec:** n/a  <!-- DOCS/CHORE: no spec -->
- **Worktree:** <created at P.4> `../python-template_kopie-worktrees/chore/value-triage-gate`
- **Depends on:** prepared-workflow (merged: `4b42c58`)
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
- One new **orchestrator** step in Phase P, working name **P.0 Value triage** (runs over the backlog before a change is interrogated/drafted; exact placement — a standalone step vs. a P.1 sub-item — is decided at P.2).
- The four checks and the 1–5 anchors above, as normative text, plus the "say so instead of guessing" clause for vague items.
- The required output: the `ID | TODO | score | recommendation | reason` table, one batched ask, and the hard rule **no implementation before the user answers**.
- Where the text lands (all `.md`): `AGENTS.md` — Phase P atomic-steps table, the Phase Matrix "P Prepare" cell, the Workflow Diagram, the Multi-change scheduling / READY-gate rules, Agent Obligations and Prohibitions; `docs/todo/template.md` — a `## Value triage` section matching the five existing hand-written ones; `.agents/skills/specify/SKILL.md` — the P.1/P.2 area and its Outputs/Done sections.
- Recording a **dropped** TODO as a legitimate, logged outcome (the drop decision stays in the TODO file, like the two 1/5 records do today).

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

## Acceptance signal (plain language)
`AGENTS.md`, the `specify` skill and `docs/todo/template.md` all name the triage step, its four checks, its 1–5 anchors, the required table, and the "ask before implementing" rule — and cross-reference the Ponytail ladder instead of restating it. A backlog item framed **after** the merge gets a filled-in Value triage section without the user having to ask, and a dropped item is left on disk with its reason. `git diff --name-status` shows only `.md` paths; `mkdocs build --strict` and the traceability check still pass.

## Prep log
| Step | Date | Result |
|---|---|---|
| P.1 Frame | 2026-10-03 | TODO + question file created on `main`; type DOCS/CHORE; todo set for this change; **value triage 5/5, implement as one bundle** |
| P.2 Interrogate (<n> questions) | | |
| P.3 Answer (<n> answered) | | |
| P.4 Draft scope + create branch/worktree | | |
| P.5 Self-consistency | | n/a (DOCS/CHORE) |
