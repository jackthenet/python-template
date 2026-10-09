# TODO: spec-interview-protocol

Backlog item for one planned change, created at **P.1 Frame** from this template and named `spec-interview-protocol.md`. One file per change.

This is a **planning record, not normative**: like `docs/questions/`, it is committed directly to `main` (see "Phase P: PREPARE" in `AGENTS.md`). It carries no approval gate — the spec does.

- **Status:** READY  <!-- PREPARING | QUESTIONS-ANSWERED | READY | IN-WORKFLOW | WAITING | MERGED -->
- **Change type:** DOCS/CHORE  <!-- process guidance only; no externally observable behavior delta. Same classification as `value-triage-gate` and `workflow-docs-nits`. -->
- **Created:** 2026-10-03
- **Question file:** `docs/questions/spec-interview-protocol.md`
- **Spec:** n/a  <!-- DOCS/CHORE: no spec -->
- **Worktree:** <created at P.4> `../python-template_kopie-worktrees/chore/spec-interview-protocol`
- **Depends on:** `value-triage-gate` (recommended: land **after** it — both edit the same P.2/P.3 guidance surface, and the value-triage step is inserted before interrogation)
- **Related specs:** none (no `docs/specs/` feature spec is touched; `docs/specs/template.md` is a template, not a spec)

## Goal (one line)
Fold the four things the proposed **Specification Interview** protocol adds — a recommended answer per question, category coverage with skipped categories justified, an explicit non-goals question, and a per-round "what is decided now" recap — into the existing **P.2 Interrogate / P.3 Answer** steps, instead of running a second, parallel interview process.

## Why
The protocol is a good description of what this repository already does — about 80 % of it is already normative, and the remaining 20 % is four small edits. Adopting it wholesale would create two overlapping procedures for the same step.

| Protocol rule | Already in the repo? | Where |
|---|---|---|
| "Explore first — if a question can be answered from the repo, look there instead of asking." | **Yes** | `specify` SKILL.md, P.2: *"Before P.2, check existing features and specs (no double work): read the specs in `docs/specs/` … every TODO file in `docs/todo/` … the existing feature directories under `src/`"* |
| "Ask at most 4 questions per round, then wait." | **Yes** | AGENTS.md P.3 + P.2 batching: *"≤ 4 per `ask_user_question` round, the most blocking first"*; one `BLOCKED-USER` batch per step, never partial batches |
| "Rank by impact — lead with expensive-to-reverse decisions." | **Yes** | same: *"most blocking first"* |
| "Do not write code during this phase." | **Yes, structurally** | P.1–P.3 write only `docs/todo/` + `docs/questions/`; the change branch and worktree are not created until **P.4**; implementation is Phase 4 |
| "Record questions and answers durably." | **Yes** | `docs/questions/<name>.md`, one file per change, with step / why / context / answer / date / status / incorporated |
| "Wait for my approval of the spec before implementation." | **Yes, gated** | Spec Approval Gate — S1.4 PR merged through GitHub review; `git log main -- docs/specs/[name].md` |
| "Ask about non-goals at some point." | **Partly** | the feature brief must capture *"out-of-scope"*, and AGENTS.md says to fold it into the spec — but **`docs/specs/template.md` has no Non-goals / Out-of-scope section** (§1 Overview → §11 Traceability), so there is nowhere standard to put the answer, and no step is required to *ask* it |
| "Propose a default answer + one-line reason for every question." | **No** (only at presentation) | the orchestrator's `ask_user_question` convention puts the recommended option first with "(Recommended)", but the **question-file entry format has no `Recommended:` field**, so the recommendation is not recorded and not available to the P.4/P.5 subagent |
| "Tag each question with its category; report which categories were covered and which were skipped, and why." | **No** | P.2's done-criteria is a count, not a coverage checklist; the interrogation dimensions are named in prose (*"ambiguity, hidden requirements, edge cases, scope boundaries"*) but not tracked |
| "After each round, state in 1–2 lines what is now decided." | **No** | not required anywhere |
| "No fixed question count — stop when questions would be filler." | **Conflicts** | AGENTS.md P.2 and the `specify` skill both require **≥ 20 questions** for FEATURE/CROSS-CUTTING as the done-criterion |
| "Then write the spec: Goal / Non-goals / Decisions / Open risks / Acceptance criteria." | **Conflicts** | `docs/specs/template.md` requires stable **REQ/AC/INV/EDGE/NFR IDs**, Given/When/Then ACs, a test-strategy map and a traceability matrix; `scripts/check_traceability.py` (the `traceability` CI job) fails on IDs that are defined but untested or referenced but undefined. The interview's five headings carry none of that |

So the real decision is not "adopt the protocol?" — it is "which four lines to add to P.2/P.3, and what to do about the ≥ 20 floor."

## In scope
- **`Recommended:` field in `docs/questions/template.md`** — one line per entry: the step's proposed answer + a one-line reason. Cheap, and it makes the recommendation survive into the P.4 draft subagent's inputs.
- **Category coverage checklist in the `specify` skill's P.2** — the seven categories (Scope & Goals, Data & State, Behavior & Edge Cases, Interfaces, Constraints, Testing & Acceptance, Architecture & Conventions), each marked covered / skipped-with-reason, reported in the P.2 handoff. This is what "no meaningful ambiguity remains" actually means in a checkable form.
- **A mandatory non-goals question** in P.2 (one clause in `specify/SKILL.md:71` + `AGENTS.md:142`), and an **`- **Out of Scope / Non-goals:**` bullet in `docs/specs/template.md` §1** — §1 bullet, **not** a numbered section, and it **must stay ID-free** so `check_traceability.py:105` does not demand a matrix row for it. (Today the answer exists in the feature brief, which AGENTS.md says is *not* saved as a separate file — so it currently evaporates.) **No backfill** of `logging.md`, `logging-coverage.md`, `session-management.md` — the template binds new specs only.
- ~~**A per-round recap line** in P.3 ("what is decided now")~~ — **dropped at Q-5 = (C)**, see Out of scope.
- **Decide the ≥ 20 question floor** (see Constraints): keep it, or replace it with the coverage checklist as the FEATURE/CROSS-CUTTING done-criterion. This is the one item that changes a gate, so it needs an explicit answer.

## Out of scope
- **A new interview step or a new protocol document.** P.2/P.3 already are the interview; adding a parallel procedure means every future change answers two questionnaires.
- **Replacing `docs/specs/template.md` with the interview's five-section layout.** That would drop REQ/AC/INV/EDGE/NFR IDs, the test-strategy map and the traceability matrix, and break `scripts/check_traceability.py`. At most the interview's headings become a short preamble inside §1.
- **Changing the ≤ 4-per-round batching, the single `BLOCKED-USER` batch rule, or the Spec Approval Gate** — already correct, already enforced.
- **Anything about implementation.** The protocol's "no code during this phase" is already structural (worktree created at P.4).
- Value triage placement (owned by `docs/todo/value-triage-gate.md`).
- **The per-round "now decided" recap** — dropped at **Q-5 = (C)**: it has no artifact, no producer and no evidence path, so a MUST would be a gate signal nothing can verify (the P-39 class, `docs/workflow/PROBLEMS.md:371-377`). The question file plus the recorded `Recommended:` field already carry the same information durably.
- **Backfilling non-goals into the three approved specs** that lack one (`logging.md`, `logging-coverage.md`, `session-management.md`) — **Q-4 = (3) no backfill**; each would need its own Spec Amendment PR and the template binds new specs only.

## Affected features
No `src/` code. Files: `.agents/skills/specify/SKILL.md` (P.2 / P.3 sections), `docs/questions/template.md`, `docs/specs/template.md` (§1), and — only if the ≥ 20 floor changes — `AGENTS.md` (P.2 done-criteria) and the `specify` skill's done-criteria/checklist lines.

## Constraints and risks
- **The ≥ 20 floor is load-bearing, and it is a proxy, not a goal.** It exists so a subagent cannot return three vague questions and call the interrogation done. Replacing it with a coverage checklist is only safe if the checklist is genuinely checkable (seven categories, each covered or explicitly skipped with a reason) — otherwise the step becomes easier to pass, which is the opposite of why the floor was added. Recommendation: **keep ≥ 20 and add the checklist on top** (both), rather than swap one for the other.
- **Two procedures for one step is the failure mode.** If this TODO is implemented as a new document instead of edits to the `specify` skill, P.2 and the interview will drift, and future agents will not know which one the gate refers to.
- **`AGENTS.md` is normative; the skill is operational.** Any change to a done-criterion must be made in both, or the handoff verification and the step disagree.
- **Ordering with `value-triage-gate`.** That TODO inserts a value-triage step before interrogation in the same text. Landing this one first creates a merge conflict in the same paragraphs; land it second, or land them as one change.
- **No behavior delta, so no test.** The Phase 5 gate here is `mkdocs build --strict` (if the guidance is published) plus a human read of the diff — not the test suite.

## Value triage (2026-10-03, pre-workflow)
- **Overlap:** high — most of the protocol is already normative in `AGENTS.md` + the `specify` skill (see the table above). The overlap check is the substance of this TODO.
- **Beneficiary:** the next P.2/P.3 run: a recommendation recorded per question means the user can answer "ok" to the cheap ones, and the category checklist makes "we're done asking" a checkable claim instead of a vibe.
- **Score: 4/5** — the four surviving deltas are small, low-risk text edits with a real payoff in round-trip count; the two conflicting items are worth deciding but should be **declined as written**.
- **Recommendation: implement the four deltas as edits to the existing P.2/P.3 guidance; decline the interview's spec layout (IDs are CI-enforced); decide the ≥ 20 floor with a bias toward keeping it alongside the checklist.** Do not create a separate interview protocol document.

## Acceptance signal (plain language)
`docs/questions/template.md` has a `Recommended:` field; the `specify` skill's P.2 names the seven categories and requires each to be marked covered or skipped-with-reason in the handoff; a non-goals question is required at P.2 and `docs/specs/template.md` has a Non-goals subsection to record it in; P.3 requires a one-line "now decided" recap; the ≥ 20 question rule is either kept or replaced by an explicit, checkable criterion — whichever was decided, `AGENTS.md` and the skill say the same thing; and there is exactly one interview procedure in the repo, not two.

## Prep log
| Step | Date | Result |
|---|---|---|
| P.1 Frame | 2026-10-03 | TODO + question file created on `main`; type DOCS/CHORE; protocol compared line-by-line against `AGENTS.md` Phase P and `.agents/skills/specify/SKILL.md` — **~80 % already normative** (explore-first, ≤4/round, impact ranking, no-code, durable Q&A, approval gate); 4 genuine deltas found (recommended answer per question, category coverage, non-goals question + spec subsection, per-round recap); 2 conflicts flagged (≥ 20 question floor; spec layout vs. REQ/AC IDs enforced by `scripts/check_traceability.py`); **value triage 4/5 — fold into P.2/P.3, do not add a parallel protocol** |
| P.2 Interrogate (6 questions) | 2026-10-04 | **DONE** (question file written; this Prep-log row was missing and is filled in now) — Q-1…Q-6 recorded: the `Recommended:` field, category coverage (which list + MUST/SHOULD), the ≥ 20 floor, non-goals (mandatory P.2 question + `docs/specs/template.md` §1 slot + backfill), the per-round recap, and the landing order against `value-triage-gate` / `workflow-docs-nits` |
| P.3 Answer (round 1: Q-1, Q-2, Q-3) | 2026-10-04 | **WAITING** — **Q-1 = (A) MUST**: `- **Recommended:** <answer + one-line reason>` joins the Entry format and P.2's done-criteria. **Q-2 = (A) MUST**: a `### Category coverage` table (own dimensions; the seven categories are a starting checklist, not a closed set) in P.2's done-criteria. **Q-3 = (A)**: keep the ≥ 20 floor **and** add the coverage gate — neither replaces the other. (Q-4/Q-5/Q-6 resolved in round 2 below) |
| P.4 Draft scope + create branch/worktree | | |
| P.3 Answer (round 2: Q-4, Q-5, Q-6) | 2026-10-04 | **RESOLVED — all 6 ANSWERED.** **Q-4 = all three recs**: mandatory P.2 non-goals question + an **ID-free** `- **Out of Scope / Non-goals:**` bullet in `docs/specs/template.md` §1 (not a numbered section) + **no backfill** of the three approved specs. **Q-5 = (C) drop the recap** — a MUST would be a gate signal with no reachable producer (P-39). **Q-6 = (A)** `workflow-docs-nits` → `value-triage-gate` → this change last; single answer for both this change and `value-triage-gate` Q-4 |
| P.5 Self-consistency | n/a (DOCS/CHORE) | |
