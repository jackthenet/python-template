# prepared-workflow — Verification

## Change Type

- **Change type:** DOCS/CHORE
- **Date:** 2026-10-02
- **Purpose:** front-load ALL human interaction (questions + answers + draft spec) into a new **Phase P: PREPARE**, so the normal Spec-TDD workflow can then run autonomously and in parallel over many changes, never idling on a human gate.

No behavior delta: this change rewrites workflow documentation and adds two planning templates. It changes no implementation, no tests, no CI, no config.

## Scope (exact non-behavior changes)

### A. New Phase P — PREPARE (front-loaded human interaction), runs BEFORE the normal workflow

Purpose: collect all human input (questions + answers) and produce the draft spec for every planned change before the normal workflow starts, so the workflow then runs autonomously and in parallel over many changes.

Per prepared change, Phase P produces:

- `docs/todo/<name>.md` — created from `docs/todo/template.md`: the backlog item (what to build, change type, status, dependencies).
- `docs/questions/<name>.md` — created from `docs/questions/template.md`: every question for that change plus the user's answers.
- `docs/specs/<name>.md` — the full draft spec (FEATURE/CROSS-CUTTING), written in the change worktree.
- `docs/verification/<name>.md` — change type + the type's Phase 1 output (triage / baseline / scope) for the non-spec types.

Phase P atomic steps (same execution model as the S-steps: fresh synchronous subagent, structured handoff):

- **P.1 Frame** — orchestrator (like S0.1): classify the change type; create `docs/todo/<name>.md` and `docs/questions/<name>.md` from their templates **on main**; create the change's todo set (Phase P steps + the phases its type runs). No worktree yet.
- **P.2 Interrogate** — subagent (specify skill): the current S1.1 rules unchanged (>=20 questions, one complete BLOCKED-USER batch, overlap check against `docs/specs/` AND against every TODO file in `docs/todo/`); questions recorded in `docs/questions/<name>.md`.
- **P.3 Answer** — orchestrator, user input: present the batch in as few `ask_user_question` rounds as possible (<=4 per round, most blocking first), record the answers in `docs/questions/<name>.md`, mark each ANSWERED and incorporated.
- **P.4 Draft spec** — subagent: create the change branch + worktree (git skill "Create change worktree") from `main` — so the branch carries the TODO file and the answered questions — then run the current S1.2 (draft spec with REQ/AC/INV/EDGE/NFR IDs + test strategy) for FEATURE/CROSS-CUTTING, or the type's Phase 1 output for the other types (ISSUE triage record, REFACTOR GREEN baseline, DOCS/CHORE scope).
- **P.5 Verify self-consistency** — subagent: the current S1.3 self-consistency checklist + the dependency smoke-test; fix the spec itself.
- **Prep gate (READY)**: the TODO file says `Status: READY`; every question in the question file is ANSWERED; the spec passes the self-consistency checklist (FEATURE/CROSS-CUTTING) or the type's Phase 1 output is recorded. Only then may the change enter the normal workflow.

Where Phase P commits land:

- `docs/todo/` and `docs/questions/` are planning records, NOT normative: P.1–P.3 commit them **directly to `main`** (the backlog and the Q&A must be browsable in one place; they carry no approval gate). This is the ONLY direct-to-main commit the workflow allows.
- Everything normative (`docs/specs/`, `docs/verification/`, `src/`, `tests/`) is written in the change worktree from P.4 onward and reaches `main` only through a merged PR. The Spec Approval Gate is unchanged.

Normal-workflow entry points after prep: FEATURE/CROSS-CUTTING start at **S1.4 Present for approval** (spec PR, human merge) then Phase 2; ISSUE starts at Phase 3 (reproduction test -> RED); REFACTOR and DOCS/CHORE start at Phase 4. The old S1.1/S1.2/S1.3 become Phase P steps P.2/P.4/P.5 (renamed, same content); S1.4 keeps its number.

### B. Non-blocking gates and multi-change scheduling

- **Unbounded in-flight changes**: any number of changes may be in flight, each in its own worktree, each with its own todo set. Only one step subagent runs at a time globally (subagents stay synchronous) — the orchestrator INTERLEAVES changes.
- **Never idle**: when a change reaches a user-input gate (S1.4 spec approval, S6.4 PR merge, or a mid-workflow BLOCKED-USER), mark it WAITING and immediately take the next ready step of another change. The workflow stops only when every in-flight change is WAITING AND no prepared TODO is READY.
- **Ready selection order**: (1) changes whose declared `Depends on:` changes are already merged; (2) among ready changes, easiest first (existing rule); (3) tie-break FIFO by READY date.
- **Resume**: when a WAITING change's gate clears (its spec PR / PR merge is reachable from `origin/main` after `git fetch`, or its question file shows all answers), launch a FRESH subagent at its next atomic step.
- **Todo discipline**: one todo set per change; "exactly one in_progress at a time" becomes AT MOST ONE in_progress per change; a WAITING change's current step stays in_progress with an activeForm naming the wait (e.g. "waiting for spec PR merge").

### C. Question files replace the central `AI_Questions.md`

- One file per change: `docs/questions/<name>.md`, created from `docs/questions/template.md` at P.1.
- Same entry format as today (Q-n, Why needed, Context, Question, Answer, Date, Status, Incorporated) plus a **Step:** field (`P.2` for prep questions, `Sx.x` for late ones).
- Late (mid-workflow) questions are appended under a `## Late questions (Phases 2-6)` heading in the same file.
- `AI_Questions.md` is retired by `git mv AI_Questions.md docs/questions/archive-AI_Questions.md` (historical record, never edited afterwards). Live guidance (AGENTS.md, skills, docs/workflow/) references the per-change files; historical records (ADRs, old verification files) are NOT rewritten.

### D. Files this change touches (and ONLY these)

1. **`docs/todo/template.md`** (new) — the TODO template: Status (PREPARING | QUESTIONS-ANSWERED | READY | IN-WORKFLOW | WAITING | MERGED), change type, created date, worktree path, question-file path, spec path, `Depends on:`, related specs, Goal (one line), Why, In scope, Out of scope, Affected features, Constraints/risks, Acceptance signal (plain language), and a Prep log table (P.1..P.5 with date + result).
2. **`docs/questions/template.md`** (new) — the question-file template: header (change, type, TODO file, spec path, date opened, status OPEN | ALL ANSWERED, answer round count), a `## Preparation questions (P.2)` section and a `## Late questions (Phases 2-6)` section, and the Q-entry format (Step, Why needed, Context, Question, Answer, Date, Status, Incorporated).
3. **`AI_Questions.md` -> `docs/questions/archive-AI_Questions.md`** (`git mv`, content unchanged).
4. **`AGENTS.md`** — new "Phase P: PREPARE" section; Workflow Diagram gains a PHASE P block and PHASE 1 shrinks to S1.4; Phase Matrix note that Phase P precedes Phase 1 for all types; Atomic Steps table gains the P.1–P.5 row; Skill-to-Phase Mapping updated (specify covers Phase P + S1.4); Execution Model gains the non-blocking-gate / never-idle / resume / unbounded-in-flight rules; Todo Tracking Discipline gains per-change sets + WAITING; the "AI Questions Mechanism" section becomes "Question files (docs/questions/<name>.md)"; Git Worktrees gains the Phase P planning-artifact exception and the P.4 worktree creation; State Machine gains PREPARED as the first state; Agent Prohibitions and Agent Obligations updated.
5. **`.agents/skills/specify/SKILL.md`** — add the Phase P atomic steps (P.1–P.5) as the skill's front section (the existing S1.1/S1.2/S1.3 content becomes P.2/P.4/P.5; S1.4 stays), update Inputs (the two templates), the overlap check (also read `docs/todo/`), the Outputs and Definition of Done, and replace `AI_Questions.md` references with `docs/questions/<name>.md`.
6. **`.agents/skills/git/SKILL.md`** — the change worktree is created at P.4 (not Phase 0); the Phase P planning-artifact direct-to-main exception; how to detect that a WAITING change's gate cleared (`git fetch` + `git merge-base --is-ancestor`).
7. **`.agents/skills/decompose/SKILL.md`, `.agents/skills/test/SKILL.md`, `.agents/skills/implement/SKILL.md`, `.agents/skills/verify/SKILL.md`, `.agents/skills/review/SKILL.md`** — replace `AI_Questions.md` with `docs/questions/<name>.md`, and add one line: a BLOCKED-USER handoff puts that change in WAITING state and the orchestrator continues with another change (it never idles).
8. **`docs/workflow/EXAMPLE.md`** — add a Phase P example: a filled TODO file, a filled question file, and a P.2 task-definition launch prompt.
9. **`docs/verification/prepared-workflow.md`** (new) — this scope record.

## No-behavior-delta confirmation

- Only `.md` files change (plus one `git mv` of a `.md`).
- No `src/`, `tests/`, `pyproject.toml`, `.github/`, `scripts/`, `migrations/`, `userdocs/` changes.
- `docs/` is not published (mkdocs serves `userdocs/`), so the new `docs/todo/` and `docs/questions/` folders require no nav change.
- `scripts/check_traceability.py` scans `docs/specs/` only, so the new folders do not affect CI.

Externally observable system behavior is unchanged: this is a workflow/documentation change only.

## Follow-ups (not in scope)

- Splitting the archived Q&A history (`docs/questions/archive-AI_Questions.md`) into per-change question files.
- Adding a `docs/todo` / `docs/questions` path trigger to `.github/workflows/spec-validation.yml`.
- Updating `.pi/workflows/spec-tdd.workflow.ts` to include a prep node.
