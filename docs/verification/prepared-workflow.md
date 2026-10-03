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
10. **`docs/workflow/PROBLEMS.md`** — the Problem Log entry for this change's friction (added during S5.5 — the designated friction log, AGENTS.md Obligation 16; a process record with no behavioral surface).

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

## Verification (Phase 5)

- **Date:** 2026-10-03
- **Change type:** DOCS/CHORE — Phase 5 gate set per AGENTS.md item 16 ("Run lint and type checks where applicable; confirm no test files or behavior were touched") and the verify skill's DOCS/CHORE section.
- **Worktree:** `../python-template_kopie-worktrees/chore/prepared-workflow` (branch `chore/prepared-workflow`); commits under review: `331edcc` (scope), `1f03f39` (templates + archive), `c325c68` (AGENTS.md), `eeaa74c` (skills + examples).
- **Working tree before the run:** clean.

### Gate results

| # | Gate | Command | Result |
|---|---|---|---|
| 1 | Scope proof (docs only) | `git diff main --name-status -M` | **PASS** — 13 paths, all `.md`; nothing under `src/`, `tests/`, `scripts/`, `.github/`, `migrations/`, `userdocs/`; no `pyproject.toml` / `uv.lock` change |
| 2 | Lint (whole repo, = CI) | `uv run ruff check .` | **PASS** — `All checks passed!` |
| 3 | Traceability referential integrity (CI `traceability` job) | `uv run python scripts/check_traceability.py` | **PASS** — `Traceability: PASS (746 matrix rows, 129 spec IDs, 713 test functions)` (exit 0) |
| 4 | Spec validation parity (CI `spec-validation` job) | `uv run python scripts/verify_spec.py docs/specs/template.md` + the CI loop over `docs/specs/*.md` (template skipped) | **PASS** — 12/12 specs `rc=0`, identical on `main`; no new failures |
| 5 | Docs site build (CI `docs` job) | `uv run mkdocs build --strict` | **PASS** — `INFO - Documentation built in 3.16 seconds` (exit 0) |
| 6 | Types | `uv run mypy src/` | **PASS** — `Success: no issues found in 83 source files` (identical on `main`) |
| 7 | Full regression suite | `uv run pytest tests/ -q` | **PASS** — `727 passed, 1 skipped in 214.98s (0:03:34)` |
| 8 | Live-guidance consistency sweep (3 greps) | see below | **PASS** — no live guidance still points at the retired central question file, the old S1.1–S1.3 numbers, or a standalone Phase 0 that creates a worktree |
| 9 | Cross-reference audit (P.1–P.5, S1.4) | manual read of the six locations | **DONE with findings** — F-1…F-4 (documentation-only, not a gate failure) |
| 10 | Pre-existing S4 numbering inconsistency | recorded verbatim | **RECORDED** (out of scope) — see "Findings (out of scope)" |

### 1. Scope proof

```
$ git diff main --name-status -M
M	.agents/skills/decompose/SKILL.md
M	.agents/skills/git/SKILL.md
M	.agents/skills/implement/SKILL.md
M	.agents/skills/review/SKILL.md
M	.agents/skills/specify/SKILL.md
M	.agents/skills/test/SKILL.md
M	.agents/skills/verify/SKILL.md
M	AGENTS.md
R100	AI_Questions.md	docs/questions/archive-AI_Questions.md
A	docs/questions/template.md
A	docs/todo/template.md
A	docs/verification/prepared-workflow.md
M	docs/workflow/EXAMPLE.md
```

Every path is a `.md` file; `AI_Questions.md` is a pure rename (`R100`, content unchanged). No `src/`, `tests/`, `scripts/`, `.github/`, `migrations/`, `userdocs/`, `pyproject.toml` or `uv.lock` path appears — the no-behavior-delta scope claim holds.

### 2. Lint

```
$ uv run ruff check .
All checks passed!
```

### 3. Traceability (S5.3 for DOCS/CHORE)

```
$ uv run python scripts/check_traceability.py
Traceability: PASS (746 matrix rows, 129 spec IDs, 713 test functions)
```

Exit 0. The new `docs/todo/` and `docs/questions/` folders do not disturb the check (it scans `docs/specs/`, `docs/verification/traceability.md` and `tests/`). **S5.3 (update traceability): no matrix update required** — this change is not a spec and introduces no `REQ-XXX`/`AC-XXX`, so there is no row to add; the referential-integrity PASS is the evidence that the matrix is still consistent.

### 4. Spec validation parity (the CI `spec-validation` job)

```
$ uv run python scripts/verify_spec.py docs/specs/template.md
Specification validation
─────────────────────────
✓ REQ-001 has acceptance criteria
✓ REQ-002 has acceptance criteria
✓ REQ-003 has acceptance criteria
✓ AC-001 has executable test
✓ AC-002 has executable test
✓ AC-003 has executable test
✓ INV-001 has property test

Traceability: PASS
```

The CI loop (`for spec in docs/specs/*.md; [ "$(basename "$spec")" = "template.md" ] && continue; uv run python scripts/verify_spec.py "$spec"`) run on the change branch, then the same loop on `main` (primary worktree):

```
docs/specs/authentication.md rc=0 :: Traceability: PASS
docs/specs/event-bus.md rc=0 :: Traceability: PASS
docs/specs/file-management.md rc=0 :: Traceability: PASS
docs/specs/logging-coverage.md rc=0 :: Traceability: PASS
docs/specs/logging.md rc=0 :: Traceability: PASS
docs/specs/mail-service.md rc=0 :: Traceability: PASS
docs/specs/search.md rc=0 :: Traceability: PASS
docs/specs/session-management.md rc=0 :: Traceability: PASS
docs/specs/settings-coverage.md rc=0 :: Traceability: PASS
docs/specs/settings.md rc=0 :: Traceability: PASS
docs/specs/user-management.md rc=0 :: Traceability: PASS
docs/specs/user-roles-permissions.md rc=0 :: Traceability: PASS
SPECS_FAILED=0            # change branch (chore/prepared-workflow)
MAIN_SPECS_FAILED=0       # main
```

12/12 pass on both — no new failures versus `main` (`docs/specs/` is untouched by this change).

### 5. Docs site build

```
$ uv run mkdocs build --strict
INFO    -  Cleaning site directory
INFO    -  Building documentation to directory: ...\chore\prepared-workflow\site
INFO    -  Documentation built in 3.16 seconds
```

Exit 0 (the only other output is the pre-existing mkdocs-material 2.0 advisory banner, unrelated to this change). Confirms the `docs` CI job is unaffected: `docs/` — including the new `docs/todo/` and `docs/questions/` — is not in the nav, `userdocs/` is.

### 6. Types

```
$ uv run mypy src/            # change branch
Success: no issues found in 83 source files
$ uv run mypy src/            # main (primary worktree)
Success: no issues found in 83 source files
```

Identical — no `src/` file changed.

### 7. Full regression suite (strongest no-behavior-delta evidence)

```
$ uv run pytest tests/ -q
727 passed, 1 skipped in 214.98s (0:03:34)
SKIPPED [1] tests\acceptance\filemanagement\test_filemanagement.py:364: symlinks not available on this host
```

GREEN. The single skip is the pre-existing platform skip (symlinks unavailable on this host), not a skip this change introduced. Combined with gate 1 (no test or source file changed), the identical suite result is the no-behavior-delta proof.

### 8. Live-guidance consistency sweep

**(a) `grep -rn "AI_Questions" AGENTS.md .agents/skills docs/workflow docs/todo docs/questions/template.md`**

```
AGENTS.md:370:- **Central file retired.** The central repo-root question file is no longer live guidance: it is archived at `docs/questions/archive-AI_Questions.md` and MUST NOT be edited again. Historical references to it (ADRs, older verification records) are left intact.
docs/workflow/PROBLEMS.md:96:- **Problem:** S1.1 returned BLOCKED-USER (28 questions). The orchestrator completed the user round-trips (7 batches + 1 re-ask + user-initiated Q-29), recorded all answers in AI_Questions.md, and attempted to resume the BLOCKED-USER subagent ...
docs/questions/template.md:3:One question file per change, created at **P.1 Frame** from this template and named `<change-name>.md`. It replaces the retired central `AI_Questions.md` (archived at `docs/questions/archive-AI_Questions.md`).
```

Clean: the AGENTS.md and template hits are the archive pointer — they only state that the central file is retired and where it is archived. The `docs/workflow/PROBLEMS.md:96` hit is a **historical Problem Log record** of a past run, explicitly allowed by AGENTS.md:370 ("Historical references to it … are left intact") and by scope item C ("historical records … are NOT rewritten"). No live instruction anywhere tells a step to create or edit `AI_Questions.md`, and no skill file mentions it at all.

**(b) `grep -rn "S1\.1\|S1\.2\|S1\.3" AGENTS.md .agents/skills`**

```
AGENTS.md:158:The former steps **S1.1 / S1.2 / S1.3** are now **P.2 / P.4 / P.5** — same content, run during preparation. **S1.4** keeps its number and stays in the normal workflow.
.agents/skills/specify/SKILL.md:14:The former steps **S1.1 / S1.2 / S1.3** are now **P.2 / P.4 / P.5** — same content, run during preparation. Only **S1.4** stays inside the normal workflow, and the change branch and worktree are created at **P.4**, not at classification.
```

Clean: only the two explicit "now P.2 / P.4 / P.5" rename notes; no workflow step is still numbered S1.1–S1.3 anywhere.

**(c) `grep -rn "Phase 0" AGENTS.md .agents/skills`**

```
AGENTS.md:141:| **P.1 Frame** | orchestrator | classify the change type (Phase 0); create the TODO file and the question file from their templates; create the change's todo set | ...
AGENTS.md:168:... **Phase P (PREPARE) is the single entry point for all types**: it classifies the change first (Phase 0, at **P.1**) ...
AGENTS.md:170:### Change Types & Classification (Phase 0)
AGENTS.md:346:- **Orchestrator** — performs Phase 0 **at P.1** (classify the change type, create `docs/todo/<name>.md` and `docs/questions/<name>.md` on `main`, create the change's todo set) and runs **P.3** ...
AGENTS.md:445:... the **Phase 0 — Classify** items run at **P.1 Frame**, the FEATURE / ISSUE / CROSS-CUTTING / REFACTOR / DOCS-CHORE items run at **P.2–P.5** ... and only **S1.4 Present for approval** ... runs inside the normal workflow.
AGENTS.md:447:**Phase 0 — Classify (all types, at P.1):**
AGENTS.md:641:- Start implementation work before classifying the change type (Phase 0, at P.1).
AGENTS.md:667:1. Classify the change type (Phase 0, at P.1) and record it in `docs/verification/[name].md`.
.agents/skills/git/SKILL.md:13:- **P.4 (specify)** delegates: create the change branch and its worktree (per change type) — the worktree is created at P.4, after the questions are answered, NOT at Phase 0/Phase 1.
.agents/skills/specify/SKILL.md:64:- **Objective:** Classify the change type (Phase 0) and open the change's planning record.
.agents/skills/specify/SKILL.md:101:### 0. Classify the change type (Phase 0, at **P.1 Frame**, in the primary worktree)
```

Clean: every hit ties Phase 0 to **classification at P.1**; the only worktree mention (`git/SKILL.md:13`) explicitly denies worktree creation at Phase 0/Phase 1 (it happens at P.4). No standalone pre-work phase that creates a worktree survives.

### 9. Cross-reference audit — P.1–P.5 and S1.4 across the six locations

Locations read: (a) AGENTS.md Workflow Diagram, (b) AGENTS.md Atomic Steps table, (c) AGENTS.md Phase Matrix (plus the Phase P step/output tables), (d) AGENTS.md Skill-to-Phase Mapping, (e) `.agents/skills/specify/SKILL.md`, (f) `.agents/skills/git/SKILL.md`.

**Consistent across all six** (no finding): the step sequence **P.1 Frame → P.2 Interrogate → P.3 Answer → P.4 Draft → P.5 Verify self-consistency ◆ READY → S1.4**; the ownership split (P.1 and P.3 = orchestrator, P.2/P.4/P.5/S1.4 = one synchronous subagent each — diagram `[O]`/`[S]` markers, the Phase P table, AGENTS.md:286 and :318, specify SKILL.md:46); the artifacts and where they are committed (`docs/todo/<name>.md` + `docs/questions/<name>.md` on `main` at P.1/P.3; draft spec / triage / baseline / scope and `docs/verification/<name>.md` on the change branch at P.4, fixed at P.5); the READY gate definition (TODO `Status: READY` + every question `ANSWERED` + the P.4 artifact exists); the ≥ 20-question rule and the single complete `BLOCKED-USER` batch at P.2; the per-change question file replacing the central one; **S1.4 as the only Phase 1 step** (Phase Matrix "S1.4 only", Atomic Steps "**1 Specify** | S1.4 Present for approval", Skill-to-Phase "S1.4 only", the diagram, specify SKILL.md); the per-type workflow entry points (FEATURE/CROSS-CUTTING → S1.4 → Phase 2; ISSUE → Phase 3; REFACTOR and DOCS/CHORE → Phase 4); the worktree created at **P.4** from `main` so the branch carries the TODO file and the answers (AGENTS.md:98/144/448, git SKILL.md:13/23/75–88, specify SKILL.md P.4 "First action"); and never-idle multi-change scheduling (diagram "Non-blocking", AGENTS.md:391, git SKILL.md "Detect a cleared gate", specify SKILL.md "BLOCKED-USER = WAITING, not idle").

**Disagreements found** — reported as findings F-1…F-4 below; none is a gate failure and none was fixed here (this step changes no file other than this verification record).

### Findings

**F-1 — P.4 worktree creation: subagent or orchestrator? (AGENTS.md vs git skill).** The AGENTS.md Workflow Diagram marks `P.4  [S] Create worktree + draft spec / triage / baseline / scope`, and the Phase P atomic-steps table gives P.4 the owner "subagent (specify skill)" with the objective "create the change branch + worktree from `main` … then write the type's Phase 1 output"; `specify/SKILL.md` P.4 repeats it as the step's "**First action:** create the change branch **and its worktree** from `main`". But `git/SKILL.md` Execution Context says "**Create change worktree (P.4)** — **orchestrator, not a subagent**; runs at **P.4 Draft**, after the questions are answered". The same action is assigned to two different owners. Needs a decision: either the P.4 subagent runs `git worktree add` (fix the git skill's owner line), or the orchestrator does it before launching P.4 (then the diagram's `[S]` marker and the P.4 objective row need rewording).

**F-2 — Phase 1 name drift: "Specify" vs "Approve".** The Phase Matrix row and the Atomic Steps table call the phase "**1 Specify**", and the Workflow Diagram header reads "PHASE 1  [S] SPECIFY (specify skill)", while the Skill-to-Phase Mapping calls it "**Phase 1: APPROVE**". One step (S1.4) under three labels; a subagent reading only one table gets a different phase name.

**F-3 — P.5 done-criteria omits the Dependency Smoke-Test in the skill.** AGENTS.md's P.5 row requires "run the **Self-Consistency Checklist + the Dependency Smoke-Test**", but `specify/SKILL.md`'s P.5 step names only "the Self-Consistency Checklist (below)" in Inputs and its done-criteria mentions only the checklist; the Dependency Smoke-Test is a separate top-level section of the skill that the P.5 step never references. The content exists; the step's gate wording does not bind it.

**F-4 — "Phases 1–6 in the worktree" understates P.4/P.5.** AGENTS.md ("**Phase 1 (approve)** — S1.4 only … All work from Phase 1 through Phase 6 is performed inside the change worktree") and `git/SKILL.md` ("All subsequent work for the change (Phases 1–6) happens inside the change worktree") both start the worktree scope at Phase 1, while `specify/SKILL.md:46` says "P.5 and S1.4 run inside it" and the P.4 done-criteria puts the Phase 1 artifact in the worktree. The worktree scope actually begins at P.4; both "Phase 1 onward" sentences should read "P.4 onward".

### Findings (out of scope)

- The AGENTS.md **Workflow Diagram** numbers the Phase 4 steps S4.1–S4.5 (with a separate "S4.3 Ruff") while the AGENTS.md **Atomic Steps table** numbers them S4.1–S4.4 (ruff folded into S4.2/S4.3) — the same inconsistency exists in `.agents/skills/implement/SKILL.md`. It predates this change; the fix is a separate chore decision.

### Phase 5 conclusion

All DOCS/CHORE Phase 5 gates (1–8) **PASS** with the evidence above: the change touches only `.md` files; lint and types are clean and identical to `main`; the full suite is GREEN (727 passed, 1 pre-existing platform skip); CI parity holds for the `lint`, `traceability`, `spec-validation` and `docs` jobs; and no live guidance still references the retired mechanics. The cross-reference audit (9) produced four documentation-only findings (F-1…F-4) alongside the pre-existing S4 numbering finding — none is a gate failure, and none was fixed in this change (no file other than this verification record was modified). **Verified.**

### Findings F-1..F-4 — resolved (S5.5, 2026-10-03)

- **F-1 — P.4 worktree creation owner.** Resolved: the **P.4 Draft step subagent** creates the branch and worktree as its **first action**; the git skill owns the *how*, the orchestrator does NOT create it (matches the diagram's `P.4 [S]` marker, the Phase P owner column and specify SKILL.md's "First action"). → `.agents/skills/git/SKILL.md:23` (Execution Context owner line rewritten) and `.agents/skills/git/SKILL.md:77` (Operations intro now: "Run from the primary worktree; the **P.4 Draft step subagent** performs it as its first action, at **P.4 Draft** (after the questions are answered)"). The "Create change worktree (P.4)" heading is unchanged; AGENTS.md needed no change (it already assigns P.4 to the subagent).
- **F-2 — Phase 1 label drift.** Resolved: the phase name stays **"1 Specify"** in the Phase Matrix (`AGENTS.md:191`), the Workflow Diagram (`AGENTS.md:221`) and the Atomic Steps table (`AGENTS.md:323`); only the Skill-to-Phase Mapping row label changed `Phase 1: APPROVE` → `Phase 1: SPECIFY (approve only)`, its description untouched. → `AGENTS.md:296`.
- **F-3 — P.5 must bind the Dependency Smoke-Test.** Resolved: the P.5 step's Inputs now read "the Self-Consistency Checklist (below) **+ the Dependency Smoke-Test (below)**" and its done-criteria adds "**and** every newly named dependency has been smoke-tested on the host"; the Dependency Smoke-Test section itself is not duplicated. → `.agents/skills/specify/SKILL.md:88` (Inputs) and `.agents/skills/specify/SKILL.md:90` (Done-criteria).
- **F-4 — worktree scope wording.** Resolved: both "Phase 1 onward" sentences now start at **P.4** — `AGENTS.md:99` ("All work from **P.4** through Phase 6 is performed inside the change worktree (P.1–P.3 write the planning artifacts on `main`)") and `.agents/skills/git/SKILL.md:87` ("All subsequent work for the change (**P.4** through Phase 6) happens inside the change worktree").

Consistency sweep after the fixes (S5.5):

```text
$ grep -n "Phase 1: APPROVE" AGENTS.md
(no hit)
$ grep -n "orchestrator, not a subagent" .agents/skills/git/SKILL.md
(no hit)
$ grep -n "Phase 1 through Phase 6" AGENTS.md .agents/skills/git/SKILL.md
(no hit)
$ grep -n "Dependency Smoke-Test" .agents/skills/specify/SKILL.md
88:- **Inputs:** the written specification; the Self-Consistency Checklist (below) + the Dependency Smoke-Test (below).
157:## Dependency Smoke-Test
```

`uv run ruff check .` → `All checks passed!` (unchanged from the S5.4 gate). Files touched by S5.5: `AGENTS.md`, `.agents/skills/git/SKILL.md`, `.agents/skills/specify/SKILL.md`, this record, `docs/workflow/PROBLEMS.md` (P-38) — still strictly the Scope-C list.

## Review (Phase 6)

- **Date:** 2026-10-03
- **Steps:** S6.1 (review vs. normative basis) + S6.2 (traceability + boundaries) + S6.3 (review report)
- **Change type:** DOCS/CHORE — the normative basis is the **Scope record above** (Scope A–D + Follow-ups). No spec, no `REQ-XXX`/`AC-XXX`, so traceability is the referential-integrity gate (Phase 5 gate 3), not a per-REQ matrix update.
- **Reviewed state (bounded):** the FINAL content of the 14 paths in `git diff main --name-status -M` at `331edcc..d374418`. Phase 5 evidence was **read, not re-run**; no test suite re-run (P-27).

### Review checks

| # | Check | Result |
|---|---|---|
| R1 | No behavior delta | **PASS** |
| R2 | Scope conformance | **PASS** (one recorded addition) |
| R3 | Internal consistency of the new material | **PASS with findings** (F-5, F-6, F-7) |
| R4 | Contradiction hunt (old behaviour) | **PASS** (F-9 is a framing nit, not a contradiction) |
| R5 | Templates usable as written | **PASS** (F-6) |
| R6 | Deferred items honest | **PASS** (F-10 noted) |
| R7 | Acceptance tests not weakened/deleted | **PASS** (n/a — none exist for this type, none changed) |

**R1 — no behavior delta: PASS.** `git diff main --name-status -M` lists 14 paths, every one a `.md`; `AI_Questions.md → docs/questions/archive-AI_Questions.md` is `R100` (pure rename, content unchanged). No `src/`, `tests/`, `scripts/`, `.github/`, `migrations/`, `userdocs/`, `pyproject.toml` or `uv.lock` path. Matches the Phase 5 gate-1 evidence, and the unchanged lint / mypy / mkdocs / suite results (gates 2, 5, 6, 7) are the behavioral proof.

**R2 — scope conformance: PASS.** Every Scope D item is present: 1 `docs/todo/template.md`, 2 `docs/questions/template.md`, 3 the `R100` rename, 4 `AGENTS.md`, 5 `specify`, 6 `git`, 7 the five other skills (decompose / test / implement / verify / review), 8 `docs/workflow/EXAMPLE.md`, 9 this record. Nothing in the scope is missing, and no scope item was dropped or silently narrowed. The one path outside the Scope D list is `docs/workflow/PROBLEMS.md` (the P-38 entry), recorded in "Findings F-1..F-4 — resolved (S5.5)" ("Files touched by S5.5: … `docs/workflow/PROBLEMS.md` (P-38)"); the findings-resolution subsection itself is recorded in the same file. Accepted — see F-8.

**R3 — internal consistency of the new material: PASS with findings.** Consistent across all nine locations (Workflow Diagram `AGENTS.md:204-222`, Atomic Steps table `:322-323`, Phase Matrix `:190-191`, Skill-to-Phase `:295-296`, the Phase P section `:122-162`, Todo Tracking `:400-412`, State Machine `:618-622`, Prohibitions/Obligations `:651-660` / `:667-684`, `specify/SKILL.md`, `git/SKILL.md`):

- **Step numbering and names** — `P.1 Frame → P.2 Interrogate → P.3 Answer → P.4 Draft → P.5 Verify self-consistency ◆ READY → S1.4` everywhere; the `S1.1/S1.2/S1.3 → P.2/P.4/P.5` rename is stated once in each of the two places that need it (`AGENTS.md:158`, `specify:14`) and no step is still numbered `S1.1`–`S1.3`.
- **Ownership** — P.1 and P.3 = orchestrator, P.2/P.4/P.5/S1.4 = one synchronous subagent each: diagram `[O]`/`[S]` markers (`:206-218`), the Phase P owner column (`:141-145`), `:286`, `:318`, `:346`, `specify:46`. F-1's fix (the P.4 worktree is created by the **P.4 step subagent**) now agrees with `git/SKILL.md:23` and `:77`.
- **Where each artifact is written and committed** — `:128-135` (artifacts table) = `:98` = `specify:66` = `git/SKILL.md:63-71`; the spec / verification record land on the change branch at P.4 (`:133-134`, `:144`). Exception: the post-P.4 TODO status advances — F-5.
- **READY gate definition** — identical in all four places: `:147` (TODO `Status: READY` + every question `ANSWERED` + the P.4 artifact exists) = `:411` = `:622` (`PREPARED`) = `specify:170`; the per-type entry points match the Phase Matrix (`:151-156` vs `:191`) and the todo status order (`:412`).
- **Worktree creation point** — P.4 in every mention (`:98`, `:144`, `:448`, `git/SKILL.md:13`/`:75-88`, `specify:81`/`:113`/`:167`); `git/SKILL.md:13` explicitly denies creation at Phase 0/Phase 1.
- **"At most one `in_progress` per change"** — `:394`, `:400`, `:409`, `git/SKILL.md` Todo section; the old global "exactly one" wording survives nowhere.

**R4 — contradiction hunt: PASS.** No live sentence still says the workflow stops at a human gate, that Phase 1 interrogates and waits for the user, that a worktree exists before P.4, or that questions go in a central file. Re-run on the final state:

```text
$ grep -rnE "stops the workflow|workflow stops|single entry point|central question file|AI_Questions" \
    AGENTS.md .agents/skills/*/SKILL.md docs/todo/template.md docs/questions/template.md docs/workflow/EXAMPLE.md
AGENTS.md:168: … **Phase P (PREPARE) is the single entry point for all types** …
AGENTS.md:370: - **Central file retired.** … archived at `docs/questions/archive-AI_Questions.md` …
AGENTS.md:658: - Record questions in a central question file — questions go in `docs/questions/<name>.md` …
docs/questions/template.md:3: … It replaces the retired central `AI_Questions.md` (archived at …)
```

Every hit is the NEW semantics: `:168` names Phase P as the entry point, `:658` is the prohibition against the central file, `:370`/`template:3` are archive pointers. The ⏸ legend is now per-change (`:202` "the **change** stops until answered"), the only "stops" left is the scheduler's own stop condition (`:391` "It stops only when every in-flight change is WAITING **and** no prepared change is READY"), and `:369` says explicitly "the **workflow** does not stop".

**R5 — templates usable as written: PASS.** Status vocabularies match the places that reference them: TODO `PREPARING | QUESTIONS-ANSWERED | READY | IN-WORKFLOW | WAITING | MERGED` (`docs/todo/template.md:7`) = `specify:169`; question-file `OPEN | ALL ANSWERED` (`docs/questions/template.md:9`) = `specify:67` and `EXAMPLE.md:125`/`:187`; entry `PENDING | ANSWERED` (`template:22`/`:24`) = `AGENTS.md:147`/`:411`/`:622` and the cleared-gate test in `git/SKILL.md:100`. Entry fields (Step / Why needed / Context / Question / Answer / Date / Status / Incorporated, `template:18-25`) = `AGENTS.md:363` and Obligation 14 (`:680`). Headings `## Preparation questions (P.2)` / `## Late questions (Phases 2–6)` (`template:28`/`:32`) = the wording the five phase skills now point at. The Prep-log table (`docs/todo/template.md:37-44`) has exactly the P.1–P.5 rows the Phase P table defines. Gap: the three post-READY statuses are never assigned to a step — F-6.

**R6 — deferred items honest: PASS.** The Follow-ups list (`:78-80`) names exactly three deferrals, and none is required for the seven acceptance points: the archived-Q&A split is a historical-record nicety the workflow never reads; the CI path trigger is unnecessary because `scripts/check_traceability.py` scans `docs/specs/` + `docs/verification/traceability.md` + `tests/` (Phase 5 gate 3 PASSes with the new folders present) and `mkdocs` serves `userdocs/` (gate 5 PASS); `.pi/workflows/spec-tdd.workflow.ts` is an optional driver, not the normative protocol — `AGENTS.md` and the skills carry Phase P end to end, which is what the seven points depend on. Noted (not a finding): that script is now stale against the new protocol — F-10.

**R7 — acceptance tests: PASS (n/a).** No `tests/` path appears in the diff; nothing was added, weakened, converted or deleted. The suite result is identical to `main` (727 passed, 1 pre-existing platform skip).

### Acceptance signal (the user's stated goal)

| # | Point | Where it is delivered | Citation |
|---|---|---|---|
| 1 | A TODO template exists | `docs/todo/template.md` (new, 44 lines): status enum, type, dependencies, scope, acceptance signal, Prep log | `docs/todo/template.md:1`, `:7`, `:13`, `:34`, `:37` |
| 2 | Multiple TODO files are created from it and stored in a `todo` folder | P.1 creates `docs/todo/<name>.md` from the template on `main`; any number of changes may be prepared | `AGENTS.md:130`, `:141`, `:160-162`; `specify/SKILL.md:66`, `:109`; `git/SKILL.md:63-71`; example file `docs/workflow/EXAMPLE.md:65` |
| 3 | Each TODO file has its own separate set of questions | The TODO file names its question file; one question file per change | `docs/todo/template.md:10`; `AGENTS.md:131`, `:363`; `docs/questions/template.md:1` |
| 4 | Questions are answered per TODO file; question files live in a `questions` folder, one per TODO/spec, replacing the central file | P.2 records, P.3 answers in `docs/questions/<name>.md`; the central file is retired (archived by `git mv`, `R100`) and recording questions centrally is prohibited | `AGENTS.md:142-143`, `:361-370`, `:658`, `:680`; `docs/questions/template.md:1`, `:9`, `:28`, `:32`; `docs/questions/archive-AI_Questions.md` |
| 5 | The normal workflow starts only after all TODOs/specs are prepared and their questions answered | The ◆ READY prep gate + the `PREPARED` state + the prohibition + the Phase P todo completion rule + the phase skills' "Prepared first" precondition | `AGENTS.md:147`, `:411`, `:622`, `:655`; `specify/SKILL.md:170`, `:211`; `test/SKILL.md:33`; `implement/SKILL.md:34` |
| 6 | While a change waits for PR approval or other human interaction, work continues on other TODOs that need none | The non-blocking legend + the "Multi-change scheduling (never idle)" section + the per-skill WAITING rule + the scheduling example | `AGENTS.md:202`, `:288`, `:368`, `:388-394`, `:656`; `git/SKILL.md:102`; `review/SKILL.md:44`; `docs/workflow/EXAMPLE.md:201-214` |
| 7 | Once a blocked TODO can proceed, its normal workflow continues | The Resume rule + the git skill's cleared-gate detection (`git fetch` + `git merge-base --is-ancestor`) + the fresh-subagent relaunch | `AGENTS.md:393`, `:288`; `git/SKILL.md:90-102`; `specify/SKILL.md:50` |
| — | Overall goal: front-load ALL human interaction so the workflow runs autonomously, with multiple TODOs in parallel | The Phase P section's purpose statement + the unbounded-in-flight rule + the per-change todo sets | `AGENTS.md:122-124`, `:160-162`, `:390`, `:400`; `specify/SKILL.md:12`; `docs/workflow/EXAMPLE.md:61` |

### Findings

**F-5 — the READY status advance has no owner and no commit target (OPEN, must resolve before S6.4).** The gate signal is defined as a TODO-file state on `main`, but no step is assigned to write it there:

- `specify/SKILL.md:211` (Phase P Definition of Done): "The TODO file exists **on `main`** with `Status: READY`"; `specify/SKILL.md:196` (Outputs): "committed to `main`, its `Status:` advanced to **READY**".
- `specify/SKILL.md:46` puts **P.5** (the step the Rules at `:169` assign the READY advance to — "READY (P.5 gate)") **inside the change worktree**, whose HEAD is the change branch — and P.5's own Inputs/Outputs/Done-criteria (`:88-90`) never mention the TODO status at all.
- `git/SKILL.md:63` scopes the direct-to-`main` planning-artifact commit to "**(P.1–P.3)**" ("P.1 creates them, P.3 records the answers"), so no documented operation commits a post-P.3 status change.
- Consequence: if P.5 edits the TODO file in the worktree, `Status: READY` reaches `main` only when the change PR merges — i.e. after the workflow already ran — so the gate at `AGENTS.md:147` is unobservable in the backlog on `main` that `AGENTS.md:135` says must be browsable there; if instead the orchestrator commits it to `main`, that write is undocumented.

Minimal fix (documentation only, one or two sentences): state who advances the TODO `Status:` after P.3 (READY at the P.5 gate, then IN-WORKFLOW / WAITING / MERGED) and where it is committed — e.g. "the orchestrator advances the TODO `Status:` in the **primary worktree** and commits it to `main` as a planning-artifact commit (the `git` skill's planning-artifact operation extends to P.5 and to the workflow status changes); the change branch's copy is never updated" — then extend `git/SKILL.md:63`'s heading from "(P.1–P.3)" accordingly and add the status advance to `specify` P.5's Outputs. This is the same class as F-1/F-4, which this change resolved in-place.

**F-6 — the post-READY TODO statuses have no producer (accepted, fix with F-5).** `IN-WORKFLOW`, `WAITING` and `MERGED` are declared in `docs/todo/template.md:7` and `specify/SKILL.md:169`, but `AGENTS.md` never assigns them: the scheduling section (`:388-394`) treats WAITING as a scheduler state and a todo `activeForm`, not as a TODO-file write. Accepted as a completeness gap that F-5's fix closes in the same sentence; nothing in the seven acceptance points depends on the backlog showing those three states.

**F-7 — three unqualified wording residuals (accepted, minor).** (a) `AGENTS.md:99` "**Phase 1 (approve)**" and the todo example at `:425` "#2 Phase 1: Approve" still use the F-2 label the fix retired in the tables (canonical name "1 Specify", `:191`/`:221`/`:323`, Skill-to-Phase "SPECIFY (approve only)" `:296`) — the phase number and the single step (S1.4) are unambiguous, so no step can be misread. (b) `AGENTS.md:338` "the **change worktree path** (all commands run there)" is unqualified for P.1–P.3, which run in the primary worktree (`specify:46`, and `EXAMPLE.md:173-176` states "WORKTREE: none yet"). (c) `AGENTS.md:145` P.5 "Done when: the spec passes the checklist" omits the Dependency Smoke-Test its own Objective requires (the F-3 fix bound it in `specify:88`/`:90`), and its spec wording says nothing about what P.5 checks for ISSUE/REFACTOR/DOCS-CHORE (the skill routes those at P.4 only — `specify:121` ISSUE, `:133` REFACTOR, `:139` DOCS/CHORE).

**F-8 — the Scope D list under-reports one path (accepted).** Scope D is headed "Files this change touches (and ONLY these)" and lists 9 items; the final diff has a 10th path, `docs/workflow/PROBLEMS.md` (P-38). The addition is recorded in the same file (the S5.5 paragraph), the Problem Log write is mandated by AGENTS.md Obligation 16, and `docs/workflow/` is a process record with no behavioral surface — accepted as recorded, no re-scope needed.

**F-9 — "no human input left" is stronger than the mechanism (accepted).** `AGENTS.md:124` ("the only human actions left are merging the spec PR (S1.4) and the change PR (S6.4)") and `specify/SKILL.md:12` ("runs **without human input**") sit next to the documented late-question path (`docs/questions/template.md:32`, the `BLOCKED-USER` trigger in all five phase skills, `AGENTS.md:367`/`:369`). Operationally consistent — a late question makes the change WAITING and the workflow keeps moving — so the sentence reads as the goal, not a prohibition; a qualifier ("no *scheduled* human input; late questions stay non-blocking") would make it exact.

**F-10 — `.pi/workflows/spec-tdd.workflow.ts` is now stale (accepted, already a follow-up).** The script still describes the old Phase 1 ("creating the feature branch from main, adversarially interrogating … writing the specification", `.pi/workflows/spec-tdd.workflow.ts:65`) and has no prep node. It is an optional driver, not the normative protocol, and the deferral is recorded at `:80`.

### Pre-existing (out of scope, unchanged)

The Workflow Diagram's S4.1–S4.5 numbering vs. the Atomic Steps table's S4.1–S4.4 (and the same drift in `implement/SKILL.md:31`) predates this change and is recorded under "Findings (out of scope)" above. Likewise the Phase Execution intro's unqualified "Every workflow step is executed by a new subagent … never executes a step itself" (`AGENTS.md:305`) vs. the orchestrator-owned P.1/P.3 — the same tension existed with the old Phase 0/S0.1, and the exceptions are stated at `:286`, `:318`, `:346`.

### Verdict

The change delivers its normative basis exactly: Scope A–D are all present in the final state, nothing outside the recorded scope changed behavior, the seven acceptance points are each delivered and cited, and the deferred items are honestly deferred. One documentation defect (F-5) leaves the READY gate's key signal without an owner or commit target — the same class as F-1/F-4, which this change fixed in place.

REVIEW REPORT: NOT CLEAN (findings: F-5 open; F-6..F-10 accepted)

### Findings F-5, F-7, F-8, F-9 — resolved (S6.5, 2026-10-03)

- **F-5 — ownership and commit target of the planning records (the blocking finding).** Resolved: `docs/todo/<name>.md` and `docs/questions/<name>.md` are declared **orchestrator-owned records that live only on `main`** — the orchestrator writes/updates them from the primary worktree and commits every change directly to `main`; a change branch never edits them and a change PR never contains them (so a later direct-to-`main` status update is never reverted by the merge). A new AGENTS.md subsection **"Planning records (owner: the orchestrator)"** carries the six-moment status table (`PREPARING` at P.1 → `QUESTIONS-ANSWERED` after P.3 → `READY` after the verified P.5 handoff → `IN-WORKFLOW` on workflow entry → `WAITING` at a human gate → `MERGED` after cleanup), states that step subagents never write `Status:` (they report the gate in the handoff), and that a late question is returned in the handoff's `questions` field and appended by the orchestrator on `main` (no step edits `docs/questions/` after P.4). → `AGENTS.md:149-165` (new subsection), `AGENTS.md:141`/`:143`/`:145` (P.1/P.3/P.5 rows name the status they set), `AGENTS.md:101` + `:118` (primary-worktree use + the direct-to-`main` rule extended to every status advance), `AGENTS.md:412` (Multi-change scheduling "Backlog status on `main`" bullet), `AGENTS.md:384` (Question files: late question recorded by the orchestrator), `.agents/skills/git/SKILL.md:63-75` (operation retitled **"Commit planning artifacts and status advances (orchestrator, `main`)"**, covering every advance through `MERGED`, run from the primary worktree, with the never-in-a-change-branch rule), `:12`, `:22`, Rules (`:155-156`), `.agents/skills/specify/SKILL.md:90` (P.5 reports the READY gate; the orchestrator sets it on `main`), `:66`/`:67` (P.1 sets `PREPARING`), `:109`, `:169`/`:171` (Rules), `:196` (Outputs), `:211` (Definition of Done). No rule was weakened: the direct-to-`main` exception is now explicitly narrower (only those two paths, only the orchestrator, only status/Q&A updates).
- **F-6 — post-READY statuses with no producer.** Closed by the same fix: `IN-WORKFLOW` / `WAITING` / `MERGED` now have a named producer, moment and commit target (the F-5 table + the Multi-change scheduling bullet).
- **F-7 — three wording residuals.** Resolved: (a) `AGENTS.md:99` "Phase 1 (approve)" → **"Phase 1 (S1.4)"** and the todo example at `AGENTS.md:443` "Phase 1: Approve" → **"Phase 1: S1.4"** — the canonical phase name "1 Specify" (`:191`/`:221`/`:323`) is now the only phase label; (b) `AGENTS.md:355` the task-definition's "change worktree path" bullet is qualified — "all commands run there; **P.1–P.3** run in the **primary worktree** — no change worktree exists until P.4" (and `AGENTS.md:99` reads "All work from **P.4** through Phase 6 … (P.1–P.3 write the planning **records** on `main`)"); (c) `AGENTS.md:145` P.5 "Done when" is now type-neutral and complete — "the Phase 1 output passes the Self-Consistency Checklist and the Dependency Smoke-Test; the orchestrator sets the TODO `Status: READY`".
- **F-8 — Scope D under-reported one path.** Resolved: `docs/workflow/PROBLEMS.md` is now Scope D item **10** ("added during S5.5 — the designated friction log"), so the "and ONLY these" list matches the 14-path diff.
- **F-9 — "no human input" framing.** Resolved once in each place: `AGENTS.md:124` now reads "All **scheduled** human interaction happens before the workflow runs … the human actions that remain are merging the spec PR (S1.4) and the change PR (S6.4), plus any **late** question a step raises. None of them stops the agent — a late question puts the change in WAITING and the agent switches to another prepared change"; `specify/SKILL.md:12` "runs **without scheduled human input**" with the same qualifier; the Workflow Diagram header (`AGENTS.md:222`) reads "all **scheduled** human input here".

Gates for S6.5: `grep -n "Status: READY" AGENTS.md .agents/skills/specify/SKILL.md` — 7 hits (`AGENTS.md:145`/`:147`/`:429`/`:640`, `specify:56`/`:90`/`:211`), every one consistent with the orchestrator owning the write on `main`; `grep -n "P.1–P.3)" .agents/skills/git/SKILL.md` — no hit; `grep -n "Phase 1 (approve)" AGENTS.md` — no hit; `uv run ruff check .` → `All checks passed!`; `git diff main --name-only` — still only `.md` paths, and this step touched only `AGENTS.md`, `.agents/skills/specify/SKILL.md`, `.agents/skills/git/SKILL.md` and this record. The S6.3 report line above stands as the record as of S6.3; the re-review verdict is S6.6's output.

### Re-review (S6.6, 2026-10-03)

- **Bounded inputs (P-27):** the S6.5 fix commit `4756a41` (4 paths: `AGENTS.md`, `.agents/skills/specify/SKILL.md`, `.agents/skills/git/SKILL.md`, this record) read as a diff, plus the FINAL state of those three files, `docs/todo/template.md`, `docs/questions/template.md` and `docs/workflow/EXAMPLE.md`, checked against the Scope record. Nothing re-run — the Phase 5 gate set (gates 1–10) was read, not re-executed; no test suite, lint, mkdocs or repo-wide grep re-run. This step changed only this file.

**F-5 — CLOSED (the blocking finding).** Every one of the six `Status:` values in `docs/todo/template.md:7` now has a named producer, a moment and a commit target, all in one table (`AGENTS.md:153-162`) owned by the orchestrator (`AGENTS.md:151`, `:164`) and committed by one named operation (`.agents/skills/git/SKILL.md:65-75`, retitled "Commit planning artifacts and status advances (orchestrator, `main`)"; also `:12`, `:22`, Rules `:155-156`):

| Status | Producer / moment | Commit target | Evidence |
|---|---|---|---|
| `PREPARING` | orchestrator at P.1 | `main` | `AGENTS.md:141`, `:157`; `specify:67` |
| `QUESTIONS-ANSWERED` | orchestrator after P.3 | `main` | `AGENTS.md:143`, `:158`; `git:65` |
| `READY` | orchestrator after the verified P.5 handoff | `main` | `AGENTS.md:145`, `:159`; `specify:90`, `:196`, `:211` |
| `IN-WORKFLOW` | orchestrator at workflow entry (S1.4 / Phase 3 / Phase 4) | `main` | `AGENTS.md:160`, `:412` |
| `WAITING` | orchestrator at a human gate (S1.4, S6.4, BLOCKED-USER, BLOCKED-HUMAN) | `main` | `AGENTS.md:161`, `:412`; `git:65` |
| `MERGED` | orchestrator after post-merge cleanup | `main` | `AGENTS.md:162`, `:412`; `git:65` |

Step subagents are excluded from the write (`AGENTS.md:164`, `specify:90`, `:169`), so the F-5 "no owner / no commit target" defect is gone. The **never-in-a-change-branch** rule is stated in both files (`AGENTS.md:151`; `git:74`, `:156`) and does not contradict P.2 (which writes the question file in the **primary** worktree before any branch exists — `AGENTS.md:226`, `specify:69-75`, `EXAMPLE.md:180`) nor P.4/P.5 (which write only the normative artifacts and never the TODO file — `specify:90`).

**Merge-safety claim: verified, it holds.** The branch is created at P.4 from `main` (`git:75`, `:77-90`), so for `docs/todo/` and `docs/questions/` the branch side of the merge equals the merge base — a three-way merge therefore keeps `main`'s newer side (no conflict, no revert); a squash merge computes the same tree (the squashed diff is the branch's changes vs. base, which exclude those paths); a rebase merge replays only commits that touch other paths. The claim fails only if a change branch *does* modify those paths — exactly what `AGENTS.md:151` and `git:74`/`:156` now forbid. The branch's inherited copy stays stale after P.4 (`git:75`, `:90`), which is harmless: nothing reads the branch copy as the gate signal — the READY gate and the backlog read `main` (`AGENTS.md:147`, `:412`, `:640`, `:673`).

**F-6 — CLOSED.** `IN-WORKFLOW` / `WAITING` / `MERGED` have a producer, moment and target (rows 4–6 above; `AGENTS.md:412` "Backlog status on `main`"; `git:65` names all six statuses inside the one commit operation).

**F-7 — (a) CLOSED, (b) CLOSED, (c) STILL OPEN in part → F-11.**
- (a) `AGENTS.md:99` now reads "Phase 1 (S1.4)" and `AGENTS.md:443` "#2 Phase 1: S1.4"; `grep -n "Phase 1 (approve)\|Phase 1: Approve" AGENTS.md` → no hit. The only remaining "approve" label is the Skill-to-Phase row `AGENTS.md:313` "Phase 1: SPECIFY (approve only)" — the F-2-sanctioned label. The phase name is "1 Specify" at `:208` (Phase Matrix) and `:340` (Atomic Steps), and S1.4 is its only step (`:208`, `:238-239`, `:340`, `specify:45`).
- (b) `AGENTS.md:355` is qualified ("**P.1–P.3** run in the **primary worktree** — no change worktree exists until P.4"), matching `specify:46` and `EXAMPLE.md:180`.
- (c) The Dependency Smoke-Test half is CLOSED (`AGENTS.md:145` names it; `specify:88`/`:90` bind it). The "what does P.5 check for ISSUE / REFACTOR / DOCS-CHORE" half is not closed and the fix widened it — see F-11.

**F-8 — CLOSED.** Scope D item **10** is `docs/workflow/PROBLEMS.md`, and `git diff main --name-status -M` still lists exactly **14** paths, all `.md` (13 `M`/`A` + 1 `R100`), matching the 10 scope items (item 7 = the five skill files).

**F-9 — CLOSED in the three named places; one instance remains → F-13.** `AGENTS.md:124` ("All **scheduled** human interaction … plus any **late** question a step raises. None of them stops the agent"), `AGENTS.md:222` ("all **scheduled** human input here"), `specify:12` ("runs **without scheduled human input**" + the WAITING clause).

**New findings (S6.6).**

- **F-11 — the P.5 gate now over-reaches for the three non-spec types, and READY becomes unreachable for them (OPEN, blocking).** `AGENTS.md:145` requires, for every type, that "the Phase 1 output passes the **Self-Consistency Checklist** and the Dependency Smoke-Test". Against the normative basis and the skill this is (i) **more than the scope** — the Scope record's prep gate is "the spec passes the self-consistency checklist **(FEATURE/CROSS-CUTTING)** or the type's Phase 1 output is recorded" (`:31`); (ii) **contradicted by the skill** — the checklist is defined "against the written specification" (`specify:146`) and its P.5 step is written for a specification (`specify:87`), while the ISSUE / REFACTOR / DOCS-CHORE paths run at **P.4 only, questions at P.2**, with no P.5 step at all (`specify:121`, `:133`, `:139`) — even though `AGENTS.md:463`, `:479`, `:492` and `:496` say all five types run "P.2–P.5"; and (iii) **a gate hole** — `READY` is set only "after the **P.5 handoff** is verified" (`AGENTS.md:159`), so for a type whose path has no P.5 there is no handoff to verify and no status to set, and `AGENTS.md:673` then forbids starting that type's entry phase. Either reading is defective: P.5 runs for an ISSUE and must apply a spec checklist to a triage record, or it does not run and the change can never be READY. Minimal fix (documentation only): qualify the P.5 row (checklist → FEATURE/CROSS-CUTTING; smoke-test → any type that names a new dependency; for ISSUE/REFACTOR/DOCS-CHORE P.5 verifies the Phase 1 output against that type's own done-criteria), state the READY moment per type, and align the `specify` B/D/E headers with `AGENTS.md:463`.
- **F-12 — the git skill's ownership sentence forbids the write P.2 is required to make (OPEN, minor but a direct contradiction).** `.agents/skills/git/SKILL.md:74`: "Only the orchestrator edits them, and only in the primary worktree; **step subagents never do**" (repeated as a Rule at `:156`), and `AGENTS.md:151`: "the orchestrator **writes** and updates them". But P.2 is a step subagent that MUST write the question file: `AGENTS.md:142` (objective), `:226` (diagram arrow `P.2 [S] ──► docs/questions/<name>.md`), `specify:73`/`:74`/`:75`, and the worked launch prompt `EXAMPLE.md:180` ("Run this step in the PRIMARY worktree (on main) and **write ONLY `docs/questions/session-audit-log.md`**"). The qualified statements are correct (`AGENTS.md:164` "must not edit `docs/questions/` after P.4"; `AGENTS.md:384`; `specify:49` "After **P.4** the question file is orchestrator-owned"), so the unqualified pair is the residual. Same bullet, second half: "a change branch and its PR must never **contain** `docs/todo/` or `docs/questions/` paths" (`git:74`, `:156`) contradicts `git:75`/`:90` ("the change branch already **carries** the TODO file and the answered questions") — the branch *does* contain them (inherited at P.4); what it must never do is **modify** them, and they must never appear in the PR diff. Minimal fix: "only the orchestrator **commits** them; the only step that **edits** them is P.2, before any worktree exists; no step edits them after P.4; a change branch never modifies them and its PR diff never shows them."
- **F-13 — one unqualified "ALL human interaction" instance survives in the example (OPEN, trivial).** `docs/workflow/EXAMPLE.md:63`: "Phase P front-loads **ALL** human interaction … so the workflow then runs **without waiting for a human**" — the F-9 qualifier was applied to the three AGENTS.md/specify instances but not to this fourth one, and the same file's own example shows changes WAITING on a human merge (`EXAMPLE.md:205`, `:208`) and a late question (`EXAMPLE.md:160-170`). Minimal fix: "front-loads all **scheduled** human interaction … so the workflow then runs without waiting for a human **on the change it is working on**".
- **F-14 — the question file's own header status has no producer (accepted, minor).** `docs/questions/template.md:9` declares `OPEN | ALL ANSWERED` and the example sets it (`EXAMPLE.md:125`), but no rule assigns the `ALL ANSWERED` write — the F-5 table covers only the TODO `Status:`. Accepted: nothing reads the header; the READY gate and the cleared-gate test read the entry-level `ANSWERED` / `PENDING` values (`AGENTS.md:147`, `git:102`). One row in the F-5 table would close it if the next round touches that table anyway.

**Sweep of the new Phase P material (P.1–P.5 rows vs. Workflow Diagram vs. Atomic Steps vs. Skill-to-Phase vs. `specify` vs. `git`): consistent, except F-11 and F-12.** Step ids and order (`P.1 Frame → P.2 Interrogate → P.3 Answer → P.4 Draft → P.5 Verify self-consistency ◆ READY → S1.4`) agree at `AGENTS.md:141-145`, `:222-236`, `:339`, `:313`, `:175`, `specify:45`, `:117`, `:131`, `git:12-13`. The ownership split (P.1 and P.3 orchestrator; P.2, P.4, P.5 and S1.4 one synchronous subagent each; the change worktree created by the P.4 subagent) agrees at `AGENTS.md:141-145`, `:222-236`, `:304`, `:337`, `:363`, `specify:46`, `git:22-23`. Artifacts and their commit targets agree at `AGENTS.md:128-135`, `:98`, `:151`, `specify:66-67`, `:81`, `:196-201`, `git:65-75`, `:77-90`. The READY gate definition agrees at `AGENTS.md:147`, `:429`, `:640`, `specify:170`, `:211`, and the per-type entry points agree with the Phase Matrix (`AGENTS.md:170-173`, `:208`, `:673`). The `AGENTS.md:147` READY definition omits "passed P.5" but is equivalent — `Status: READY` is set only after the verified P.5 handoff (`:159`). Observation (pre-existing class, already recorded in this file): `AGENTS.md:364` "Step subagent — … executes exactly one atomic step **inside the change worktree**" is unqualified for P.2, which runs in the primary worktree — the same tension as the recorded `:305` sentence, resolved by the exceptions at `:355`, `:363` and `specify:46`.

**Regression check — the direct-to-`main` exception did not widen.** Final wording, `AGENTS.md:118`: "**Direct-to-`main` commits are allowed only for the planning records** under `docs/todo/` and `docs/questions/` — their creation at P.1–P.3 **and every later `Status:` advance through `MERGED`** … Nothing else — no spec, no verification record, no source, no test — may be committed directly to `main`; it reaches `main` only through a merged PR." `git/SKILL.md:155`: "Commit **directly to `main`** only for the planning records under `docs/todo/` and `docs/questions/` — their creation at P.1–P.3 and every `Status:` advance through `MERGED` — **and only from the primary worktree**." `specify:171`: "… and only by the **orchestrator** from the primary worktree". The path set is unchanged (exactly those two folders), the owner is narrowed (orchestrator, primary worktree only), and the only widening is in **duration** (P.1–P.3 → every status advance through `MERGED`), stated explicitly and inside the same two paths. `AGENTS.md:135` and `git:73` still say these are the **only** files the workflow may commit directly to `main`.

### Verdict (S6.6)

F-5, F-6 and F-8 are closed, and the F-5 fix's central claim — the planning records are orchestrator-owned, live only on `main`, are never touched by a change branch, and therefore are never reverted by the merge — is correct and now consistently stated in AGENTS.md and the git skill. The fix round left three documentation defects: the P.5 / READY gate is unreachable or undefined for ISSUE, REFACTOR and DOCS-CHORE (F-11 — the same class as the blocking F-5, a gate signal without a reachable producer), the git skill forbids the very write that P.2 is required to perform (F-12), and one unqualified "ALL human interaction" sentence survives in the example (F-13).

REVIEW REPORT: NOT CLEAN (findings: F-11, F-12, F-13 open; F-14 accepted; F-5, F-6, F-7(a), F-7(b), F-8, F-9 closed)

### Findings F-11, F-12, F-13, F-14 — resolved (S6.7, 2026-10-03)

- **F-11 — P.5 over-reached for the non-spec types and left `READY` without a reachable producer.** Resolved: the P.5 row is now **FEATURE/CROSS-CUTTING only** and spec-worded end to end ("run the Self-Consistency Checklist + the Dependency Smoke-Test against the **draft specification**; fix the specification itself"), and the `READY` moment is stated **per type** — "after the P.5 handoff is verified (**FEATURE/CROSS-CUTTING**) or after the **P.4 artifact** is verified (**ISSUE / REFACTOR / DOCS/CHORE**)", so every type has a reachable producer for the gate signal. The same over-widening was qualified everywhere it appeared: the diagram row, the Atomic Steps row, the Phase-P-and-Phase-1 lead-in ("items run at **P.2–P.4** … with **P.5** self-consistency for **FEATURE/CROSS-CUTTING only**"), the ISSUE / REFACTOR / DOCS/CHORE headers (**P.2–P.4**), the S1.1/S1.2/S1.3 → P.2/P.4/P.5 mapping sentence, and Agent Obligation 17. → `AGENTS.md:145` (owner + Done-when), `:159` (READY per type), `:175`, `:235`, `:339`, `:463`, `:479`, `:492`, `:496`, `:701`; `.agents/skills/specify/SKILL.md:170` ("and — for **FEATURE/CROSS-CUTTING** — passed P.5"). Confirmed against `specify` (P.5 exists only in the FEATURE/CROSS-CUTTING atomic steps; paths B/D/E run at **P.4**, questions at **P.2** — `:121`, `:133`, `:139`) and with the scope record's prep gate ("the spec passes the self-consistency checklist (FEATURE/CROSS-CUTTING) **or** the type's Phase 1 output is recorded"). The Phase P intro (`AGENTS.md:124`) and the Phase Matrix "P Prepare" row (`:208`) were checked and carry **no** over-widening — both already scope the self-consistent draft spec to FEATURE/CROSS-CUTTING — so they are unchanged.
- **F-12 — the ownership sentence forbade the write P.2 is required to make.** Resolved with one meaning in all three places: the two paths are written **only in the primary worktree** — P.1–P.3 and every `Status:` advance by the **orchestrator**, and **P.2 by its step subagent** (which runs there because no change worktree exists yet, writing only the question file); **no write to them may happen inside a change worktree**, and a change branch and its PR therefore never contain them. The merge-safety sentence is kept ("because the branch does not **modify** those paths, a later direct-to-`main` status update is never reverted by the merge"), and the contradiction with the branch *carrying* the P.1–P.3 copies is gone ("the branch carries the P.1–P.3 copies inherited at P.4 but never modifies them"). → `AGENTS.md:151`; `.agents/skills/git/SKILL.md:74` (operation body) + `:156` (Rules bullet) + `:65` ("every **commit** of those two files … P.2 records the questions (written by the P.2 step subagent in the primary worktree)"). Verified against the P.2 step description (`AGENTS.md:142`, `:226`; `specify:73-75` — primary worktree, question file only) and the worked launch prompt `docs/workflow/EXAMPLE.md:180` ("Run this step in the PRIMARY worktree (on main) and write ONLY `docs/questions/session-audit-log.md`") — both already agree, unchanged.
- **F-13 — unqualified "ALL human interaction" in the example.** Resolved with the AGENTS.md qualifier: Phase P front-loads all **scheduled** human input; what remains is the two PR merges (S1.4, S6.4) and any **late** question, which puts that change in WAITING while another prepared change runs. → `docs/workflow/EXAMPLE.md:63`.
- **F-14 — the question file's header `Status:` had no producer.** Resolved on the header line itself: `Status: OPEN` is set by the **orchestrator at P.1**; `ALL ANSWERED` once every question in the file has an answer, recorded by the orchestrator **together with the `QUESTIONS-ANSWERED` TODO advance**. → `docs/questions/template.md:9` (the example at `docs/workflow/EXAMPLE.md:125` already sets `ALL ANSWERED` and now matches).

Gates for S6.7: `grep -n "P.5" AGENTS.md` → 9 hits, every one marked **FEATURE/CROSS-CUTTING only** (`:145`, `:235`, `:339`, `:463`) or clearly spec-worded (`:132` draft-spec artifact row, `:159` READY per type, `:175` specification steps, `:469`/`:486` the FEATURE/CROSS-CUTTING headers); `grep -n "P.2–P.5" AGENTS.md` → only `:469`/`:486` (FEATURE, CROSS-CUTTING); `grep -n "never contain" .agents/skills/git/SKILL.md AGENTS.md` → 3 hits, all about the change worktree / branch / PR, none forbidding the P.2 write; `grep -n "ALL human interaction" docs/workflow/EXAMPLE.md` → no hit; `uv run ruff check .` → `All checks passed!`; `git diff main --name-only` → 14 paths, all `.md`, and this step touched only `AGENTS.md`, `.agents/skills/git/SKILL.md`, `.agents/skills/specify/SKILL.md`, `docs/workflow/EXAMPLE.md`, `docs/questions/template.md` and this record. No rule was weakened: every change **scoped** an over-wide statement to its type or its worktree, and added a producer where a gate signal had none. Friction logged as **P-39**.

### Final re-review (S6.8, 2026-10-03)

**Bounded inputs (P-27):** the S6.7 fix commit `4b45bdd` (`git show --stat` + `git show`, 7 paths) read as a diff, plus the FINAL state of the sentences it changed in `AGENTS.md`, `.agents/skills/git/SKILL.md`, `.agents/skills/specify/SKILL.md`, `docs/workflow/EXAMPLE.md`, `docs/questions/template.md`, and the READY-reachability trace named by the step. Nothing re-run: the R1–R7 checks and the Phase 5 gate set were read, not re-executed; no test suite, lint, mkdocs or repo-wide sweep re-run. This step changed only this file.

**F-11 — STILL OPEN (partial): closed in `AGENTS.md`, the same defect survives in `specify`.** Closed in `AGENTS.md`: the P.5 row is FEATURE/CROSS-CUTTING-only and spec-worded (`:145`), the READY moment is stated per type (`:159` — "after the P.5 handoff is verified (**FEATURE/CROSS-CUTTING**) or after the P.4 artifact is verified (**ISSUE / REFACTOR / DOCS/CHORE**)"), and every other over-widened mention is qualified (`:175`, `:235`, `:339`, `:463`, `:479`, `:492`, `:496`, `:701`); `grep -n "P\.5" AGENTS.md` → 9 hits, none requiring P.5 for a non-spec type, and `grep -n "P\.2–P\.5" AGENTS.md` → only `:469`/`:486` (FEATURE, CROSS-CUTTING). The State Machine `PREPARED` paragraph (`:640`), the Phase Matrix "P Prepare" row (`:207`), the Phase P intro (`:124`) and Obligation 17 (`:701`) are type-correct. **Not closed in the skill the commit also edited** — three sentences still make READY a P.5-only product for every type, and one says so explicitly:

- `.agents/skills/specify/SKILL.md:169` (Rules): "The TODO file's `Status:` field MUST be updated at each Phase P step: **PREPARING** (P.1) → **QUESTIONS-ANSWERED** (P.3) → **READY** (P.5 gate) → …"
- `.agents/skills/specify/SKILL.md:196` (Outputs): "its `Status:` advanced to **READY** by the **orchestrator** (on `main`, **after it verifies the P.5 handoff**)"
- `.agents/skills/specify/SKILL.md:211` (Definition of Done, under the header `:209` "**Phase P — the READY gate (all types):**"): "The TODO file exists on `main` with `Status: READY` — set and committed by the **orchestrator** on `main` **after it verifies the P.5 handoff**"

Against `AGENTS.md:159` (quoted above) and the skill's own paths B/D/E, which run at **P.4 only, questions at P.2** with no P.5 step (`specify:121`, `:133`, `:139`), an ISSUE / REFACTOR / DOCS/CHORE change has no P.5 handoff to verify, so its READY gate is unsatisfiable under `specify:211` while `AGENTS.md:159` says it closes after P.4 — the F-11 defect class (a gate signal with no reachable producer) in a new location. The commit fixed the neighbouring rule (`specify:170`) and left these three. **Recorded as F-15** (new, introduced by the S6.7 scoping). Minimal fix, one file, three clauses: qualify each with "…(FEATURE/CROSS-CUTTING) or after the verified **P.4 artifact** (ISSUE / REFACTOR / DOCS/CHORE)". Severity: minor-to-blocking — `specify:170` and `AGENTS.md:159` are correct, so the protocol is recoverable, but the skill's READY checklist is the artifact an agent uses to confirm the gate.

**READY reachability per type** (P.1 → P.2 → P.3 → P.4 → [P.5] → the orchestrator's READY write):

| Type | Path to `Status: READY` — every step on it exists? | Evidence |
|---|---|---|
| FEATURE | **REACHABLE.** P.1 → P.2 (≥ 20 questions, one `BLOCKED-USER` batch) → P.3 → P.4 (draft spec) → **P.5** (checklist + smoke-test) → orchestrator sets READY after the verified P.5 handoff | `AGENTS.md:141-145`, `:159` row 3, `:339`, `:469`; `specify:58-90`, `:115-117`, `:170`, `:209-223` |
| CROSS-CUTTING | **REACHABLE.** As FEATURE; P.4 adds the Impact Analysis | `AGENTS.md:145`, `:159`, `:339`, `:486`; `specify:129-131` |
| ISSUE | **REACHABLE in `AGENTS.md`, UNREACHABLE as `specify:169`/`:196`/`:211` word it.** P.1 → P.2 (interrogation, questions in one `BLOCKED-USER` batch, **no ≥ 20 floor**) → P.3 → P.4 (triage in `docs/verification/`) → **no P.5** → READY after the verified P.4 artifact | `AGENTS.md:142`, `:144`, `:159`, `:207`, `:479`; `specify:121-127`, `:170` vs `:169`, `:196`, `:211` |
| REFACTOR | **REACHABLE in `AGENTS.md`, UNREACHABLE per the same three `specify` sentences.** P.4 = GREEN baseline + refactor scope; no P.5 | `AGENTS.md:144`, `:159`, `:492`; `specify:133-136` vs `:169`, `:196`, `:211` |
| DOCS/CHORE | **REACHABLE in `AGENTS.md`, UNREACHABLE per the same three `specify` sentences.** P.4 = no-behavior scope; no P.5 | `AGENTS.md:144`, `:159`, `:496`; `specify:139-141` vs `:169`, `:196`, `:211` |

**P.2 for the non-spec types — what the docs actually require.** No place imposes the ≥ 20-question batch on ISSUE / REFACTOR / DOCS/CHORE: the `AGENTS.md:142` threshold is parenthesised "(FEATURE/CROSS-CUTTING)", `specify:74` sits under the section header "**Atomic Steps (FEATURE / CROSS-CUTTING)**" (`:58`), and `specify:174` and `:216` are qualified (the latter nested under the "FEATURE/CROSS-CUTTING:" bullet of the READY checklist). What they do require: P.2 runs and every question it raises is recorded in `docs/questions/<name>.md` in **one** `BLOCKED-USER` batch — `AGENTS.md:142` (objective), the Phase Matrix "P Prepare" cell for all five types ("TODO + **answered questions** + …", `:207`), the skill's B/D/E headers ("questions at **P.2**", `specify:121`, `:133`, `:139`), and the batching rule (`AGENTS.md:386`, `docs/questions/template.md:12`). Observation (pre-existing, untouched by `4b45bdd`, so outside the scoped check): `AGENTS.md:142` states the overlap check unqualified while `specify:176` scopes it to FEATURE/CROSS-CUTTING.

**F-12 — CLOSED.** One meaning in all four places: the two paths are written **only in the primary worktree** — P.1–P.3 and every `Status:` advance by the orchestrator, and **P.2 by its step subagent** (which runs there because no change worktree exists yet, writing only the question file); **no write inside a change worktree**; a change branch and its PR therefore never contain them, and the branch *carries* the P.1–P.3 copies inherited at P.4 without modifying them. `AGENTS.md:151` ≡ `.agents/skills/git/SKILL.md:74` (operation body) ≡ `:156` (Rules: "Never write `docs/todo/` or `docs/questions/` inside a change worktree…"), and `git:65` now separates write from commit ("This operation covers **every commit of** those two files: P.1 creates them, **P.2 records the questions (written by the P.2 step subagent in the primary worktree)**, P.3 records the answers, and the orchestrator then commits every `Status:` advance"). Consistent with the P.2 step (`AGENTS.md:142`, `:226`; `specify:46` "P.2 and P.3 run in the **primary worktree**", `:71-75`) and with the worked launch prompt `docs/workflow/EXAMPLE.md:180` ("Run this step in the PRIMARY worktree (on main) and write ONLY `docs/questions/session-audit-log.md`") + `:195` ("no commit (the orchestrator commits the answers at P.3)"). The F-12 second half is gone: nothing any more forbids a branch from *containing* the inherited copies; the prohibition is on *modifying* them (`AGENTS.md:151`, `git:74`), which keeps the merge-safety claim intact. `specify:171` ("the **only** files committed directly to `main`, and only by the **orchestrator**") is about the commit, not the write, so it does not reintroduce the contradiction. **Direct-to-`main` exception still limited to `docs/todo/` + `docs/questions/`** — checked all nine statements of it: `AGENTS.md:118`, `:135`, `:675`; `git:12`, `:22`, `:73`, `:155`; `specify:66`, `:109`, `:171`; `docs/todo/template.md:5`. No path added, no owner widened.

**F-13 — CLOSED.** `docs/workflow/EXAMPLE.md:63`, final text: "Phase P front-loads all **scheduled** human interaction: the TODO file, the answered questions, and the draft spec exist before the workflow starts, so the workflow then runs without waiting for a human **on the change it is working on** (see "Phase P: PREPARE" in `AGENTS.md`). What remains is the two PR merges (S1.4 spec approval, S6.4 change PR) and any **late** question a step raises — a late question puts that change in WAITING while another prepared change runs." Matches `AGENTS.md:124` and `:222`, and now agrees with the same file's own scheduling snapshot (`EXAMPLE.md:205`, `:208` WAITING on a merge) and late-question example (`:160-170`). `grep -n "ALL human interaction" docs/workflow/EXAMPLE.md` → no hit.

**F-14 — CLOSED.** `docs/questions/template.md:9`, final text: "- **Status:** OPEN  <!-- OPEN | ALL ANSWERED — set OPEN by the orchestrator at P.1; ALL ANSWERED once every question in this file has an answer (the orchestrator records it together with the `QUESTIONS-ANSWERED` TODO advance) -->". The header status now has a named producer and moment, and the example (`EXAMPLE.md:125` `ALL ANSWERED`, with the late Q-25 also `ANSWERED`) satisfies it.

**Scoped new-finding check (the `4b45bdd` diff only).** One contradiction, quoted above: the commit's P.5 scoping (`AGENTS.md:145` "subagent (specify skill) — **FEATURE/CROSS-CUTTING only**"; `:159` READY per type) vs. the untouched `specify:211` "**Phase P — the READY gate (all types):** … after it verifies the P.5 handoff" (and `:169`, `:196`) → **F-15**. Every other changed sentence was checked against its neighbours and contradicts nothing: the git-skill rewrite is internally consistent (`:65` vs `:74` vs `:156`) and consistent with `AGENTS.md:151`; `AGENTS.md:175`'s new "(FEATURE/CROSS-CUTTING)" qualifier leaves `specify:14`'s unqualified restatement of the same mapping ("The former steps S1.1 / S1.2 / S1.3 are now P.2 / P.4 / P.5") — an unqualified restatement, not a contradiction, since the per-type Phase P list sits directly below it (`specify:18-21`); `AGENTS.md:145`'s "the orchestrator sets the TODO `Status: READY`" agrees with `:159` row 3; the `docs/questions/template.md:9` comment agrees with `AGENTS.md:147`/`:158` and the entry-level `ANSWERED` gate. No rule was weakened: every change narrowed an over-wide statement to its type or its worktree, or named a producer. Citation nit in the S6.7 record (not a document defect): it cites the Phase Matrix "P Prepare" row as `AGENTS.md:208`; the row is `:207`.

**Verdict (S6.8).** F-12, F-13 and F-14 are closed and their fixes contradict nothing. F-11 is closed in `AGENTS.md` but its defect class persists in `.agents/skills/specify/SKILL.md:169`, `:196`, `:211` (F-15): the READY gate is unreachable for ISSUE / REFACTOR / DOCS/CHORE under the skill's own READY checklist, which is exactly the finding class F-11 was raised for. Three clauses in one file close it.

REVIEW REPORT: NOT CLEAN (findings: F-11 open in part → F-15 at `.agents/skills/specify/SKILL.md:169`, `:196`, `:211`; F-12, F-13, F-14 closed)

### Finding F-15 — resolved (S6.9, 2026-10-03)

**One rule, applied to every clause that names the READY producer** (identical to `AGENTS.md:159`): the orchestrator sets and commits `Status: READY` on `main` after it verifies **the P.5 handoff (FEATURE / CROSS-CUTTING)** or **the P.4 artifact (ISSUE / REFACTOR / DOCS/CHORE)**. Three clauses, one file; nothing else was reworded, and no rule was weakened — each change only names the types a gate signal applies to.

| Location | Before | After |
|---|---|---|
| `.agents/skills/specify/SKILL.md:169` (Rules) | "…**READY** (P.5 gate) → **IN-WORKFLOW**…" | "…**READY** (after the verified **P.5 handoff** — FEATURE/CROSS-CUTTING — or the verified **P.4 artifact** — ISSUE/REFACTOR/DOCS/CHORE) → **IN-WORKFLOW**…" |
| `.agents/skills/specify/SKILL.md:196` (Outputs) | "…advanced to **READY** by the **orchestrator** (on `main`, after it verifies the P.5 handoff)." | "…advanced to **READY** by the **orchestrator** (on `main`, after it verifies the **P.5 handoff** (FEATURE/CROSS-CUTTING) or the **P.4 artifact** (ISSUE/REFACTOR/DOCS/CHORE))." |
| `.agents/skills/specify/SKILL.md:211` (Definition of Done, under the `:209` header "**Phase P — the READY gate (all types):**") | "…`Status: READY` — set and committed by the **orchestrator** on `main` after it verifies the P.5 handoff — and the question file exists…" | "…`Status: READY` — set and committed by the **orchestrator** on `main` after it verifies the **P.5 handoff** (FEATURE/CROSS-CUTTING) or the **P.4 artifact** (ISSUE/REFACTOR/DOCS/CHORE) — and the question file exists…" |

The `:209` "(all types)" header stays: the per-type clause is what makes the checklist true for all five types, and the per-type bullets below it (`:214` FEATURE/CROSS-CUTTING, `:221` ISSUE, `:222` REFACTOR, `:223` DOCS/CHORE) already name each type's Phase 1 output.

**Repo-wide sweep (the point of this step — the id, not the edited file).** `grep -rn "P\.5" AGENTS.md .agents/skills docs/workflow docs/todo docs/questions/template.md` → 24 hits (AGENTS.md 9, `specify` 12, `EXAMPLE.md` 1, `docs/todo/template.md` 1, `PROBLEMS.md` 1); `grep -rn "READY" …same paths` → 42 hits (AGENTS.md 16, `specify` 11, `implement`/`test`/`git` 2 each, `decompose`/`review`/`verify` 1 each, `EXAMPLE.md` 4, `docs/todo/template.md` 1, `PROBLEMS.md` 1, `docs/questions/template.md` 0). Every hit that names the READY producer or requires P.5, classified as (a) marked FEATURE/CROSS-CUTTING-only, (b) per-type, or (c) irrelevant to the gate:

| Hit | Class — why it is correct |
|---|---|
| `AGENTS.md:159` | (b) per-type — the reference wording `4b45bdd` already fixed ("after the P.5 handoff is verified (**FEATURE/CROSS-CUTTING**) or after the P.4 artifact is verified (**ISSUE / REFACTOR / DOCS/CHORE**)") |
| `AGENTS.md:145` | (a) the P.5 step row is marked "**FEATURE/CROSS-CUTTING only**"; its READY clause is that step's own gate |
| `AGENTS.md:147`, `:429`, `:640` | (b) per-type — READY defined as TODO `Status: READY` + every question `ANSWERED` + **the type's** Phase 1 output / the P.4 artifact; no P.5 requirement |
| `AGENTS.md:235`, `:339` | (a) P.5 marked "(FEATURE/CROSS-CUTTING only)" in the diagram and the Phase Matrix row |
| `AGENTS.md:132`, `:175`, `:463`, `:469`, `:486` | (a)/(c) spec-worded artifacts and the FEATURE / CROSS-CUTTING step ranges (`:175` carries the "(FEATURE/CROSS-CUTTING)" qualifier; `:469`/`:486` are the FEATURE and CROSS-CUTTING headers) |
| `AGENTS.md:305`, `:363`, `:370`, `:386`, `:408`, `:409`, `:673`, `:674`, `:702` | (c) scheduling/"never idle" and prohibition wording — they consume an already-READY change, they never produce it |
| `specify:169`, `:196`, `:211` | (b) **fixed by this step** — all three now name both producers per type |
| `specify:170` | (b) already per-type (fixed at S6.7): "the P.4 artifact exists … and — for **FEATURE/CROSS-CUTTING** — passed P.5" |
| `specify:56` | (b) per-type — the Phase P todo is `completed` at READY "(TODO `Status: READY`, every question `ANSWERED`, **the type's** Phase 1 output recorded)" |
| `specify:89`, `:90` (P.5 Outputs / Done-criteria: "the **READY gate**", "the **orchestrator** sets `Status: READY`") | (a) both sit inside `### P.5 Verify self-consistency` (`:85`), itself inside `## Atomic Steps (FEATURE / CROSS-CUTTING)` (`:58`) — a step that only exists for the spec types, so its READY signal is scoped by its section |
| `specify:28`, `:50` | (c) "a prepared (READY) change needs its spec committed … (S1.4)" and the WAITING/not-idle rule — consumers of READY, not producers |
| `specify:14`, `:45`, `:46` | (c) unqualified **restatements of the step mapping** (S1.1/S1.2/S1.3 → P.2/P.4/P.5; the subagent step list), not gate clauses: they neither set nor gate READY, the cited source (`AGENTS.md:235`) marks P.5 FEATURE/CROSS-CUTTING-only, and the per-type Phase P list (`:18-21`) plus the per-type paths A–E (`:115`, `:121`, `:129`, `:133`, `:139`) govern which steps a change runs — the same classification S6.8 gave `:14`. Untouched to keep the diff minimal |
| `specify:115`, `:117`, `:129`, `:131` | (a) the FEATURE and CROSS-CUTTING path headers and their step lists |
| `implement:34`, `test:33` | (b) per-type — "Phase 4/3 runs only for a change that passed the Phase P **READY** gate (TODO `Status: READY`, every question … `ANSWERED`)"; no P.5 requirement, and both files are outside this step's allowed set |
| `decompose:32`, `implement:36`, `review:44`, `test:35`, `verify:34`, `git:104`, `specify:50` | (c) the WAITING/not-idle rule — READY as a scheduling input |
| `git:65` | (c) the commit-planning-artifacts operation: it lists which commit each `Status:` advance belongs to (P.1/P.2/P.3 + "the orchestrator commits every `Status:` advance") without naming a step the advance must follow |
| `docs/workflow/EXAMPLE.md:70`, `:113`, `:211`, `:213` | (a)/(c) the worked example is a **FEATURE** change (`session-audit-log`), so its "P.5 Self-consistency … TODO → `READY`" prep-log row and its READY scheduling snapshot are correct for that type; outside this step's allowed set |
| `docs/todo/template.md:7`, `:44` | (c) the `Status:` value list and the Prep-log **table row** "P.5 Self-consistency" — a log row, not a gate: a non-spec type leaves it blank/n-a and still reaches READY via `AGENTS.md:159`. **Observation (not fixed — outside this step's allowed set):** the row is unqualified, so a reader could think it must be filled for every type; a one-word "(FEATURE/CROSS-CUTTING)" qualifier on that row would make the template match `:11`'s already-qualified "**Spec:** … FEATURE/CROSS-CUTTING only" row. Carried as a cosmetic follow-up, not a finding: it blocks no gate |
| `docs/workflow/PROBLEMS.md:372` (P-39) | (c) the problem record itself — it *describes* the F-11 defect class; extended by this step |
| `docs/questions/template.md` | no `P.5` and no READY-producer hit (only the entry-level `ANSWERED` gate) |

**No remaining hit makes READY unreachable for any type.** `grep -n "P.5 handoff" .agents/skills/specify/SKILL.md` → 3 hits (`:169`, `:196`, `:211`), every one now per-type; `grep -rn "P\.5" AGENTS.md .agents/skills docs/workflow docs/todo docs/questions/template.md` → 24 hits, none requiring P.5 for ISSUE / REFACTOR / DOCS/CHORE. READY is reachable for all five types in both the protocol (`AGENTS.md:159`) and the skill the agent uses to confirm the gate (`specify:169`, `:170`, `:196`, `:211`).

**Gates (S6.9).** `grep -n "P.5 handoff" .agents/skills/specify/SKILL.md` → 3 hits, all per-type (quoted above); `uv run ruff check .` → `All checks passed!`; `git diff main --name-only` → 3 paths, all `.md` (`.agents/skills/specify/SKILL.md`, `docs/verification/prepared-workflow.md`, `docs/workflow/PROBLEMS.md`) — exactly this step's allowed files. Friction recipe added to **P-39** (grep the id across all live-guidance files, not only the file being edited).

### Final verdict (S6.10, 2026-10-03)

**Bounded inputs (P-27):** the S6.9 fix commit `6807d38` (`git show` — 3 paths) read as a diff, plus the FINAL state of the clauses it and the earlier fix commits changed. R1–R7, the Phase 5 gate set and findings F-1..F-14 were **read, not re-run**; no test suite, lint, mypy or mkdocs re-run; nothing was fixed in this step (report only). This step changed only this file.

**F-15 — CLOSED.** All three clauses in `.agents/skills/specify/SKILL.md` are now type-correct and identical in meaning to `AGENTS.md:159`:

- `:169` — "…**READY** (after the verified **P.5 handoff** — FEATURE/CROSS-CUTTING — or the verified **P.4 artifact** — ISSUE/REFACTOR/DOCS/CHORE) → **IN-WORKFLOW** / **WAITING** / **MERGED**." — names both producers and covers all five types.
- `:196` — "…its `Status:` advanced to **READY** by the **orchestrator** (on `main`, after it verifies the **P.5 handoff** (FEATURE/CROSS-CUTTING) or the **P.4 artifact** (ISSUE/REFACTOR/DOCS/CHORE))."
- `:211` — "The TODO file exists on `main` with `Status: READY` — set and committed by the **orchestrator** on `main` after it verifies the **P.5 handoff** (FEATURE/CROSS-CUTTING) or the **P.4 artifact** (ISSUE/REFACTOR/DOCS/CHORE) — and the question file exists with **every** question `ANSWERED` and incorporated."

`grep -n "P\.5 handoff" .agents/skills/specify/SKILL.md` → 3 hits (`:169`, `:196`, `:211`), every one per-type; `grep -n "P\.5" .agents/skills/specify/SKILL.md` → 12 hits, and paths **B (ISSUE, `:121`)**, **D (REFACTOR, `:133`)**, **E (DOCS/CHORE, `:139`)** carry **no** P.5 mention (headers verified: "runs at **P.4**, questions at **P.2**"). READY is reachable for all five types in the protocol (`AGENTS.md:147`, `:159`, `:429`, `:640`) and in the skill an agent uses to confirm the gate (`specify:169`, `:170`, `:196`, `:211`). **No remaining hit in the live guidance makes `Status: READY` unreachable for ISSUE / REFACTOR / DOCS/CHORE.**

**Spot-check of the S6.9 sweep table (8 rows re-derived by grep on the final state, not re-argued):**

| Sweep row | Independent check | Verdict |
|---|---|---|
| `AGENTS.md:159` | the row reads "after the P.5 handoff is verified (**FEATURE/CROSS-CUTTING**) or after the P.4 artifact is verified (**ISSUE / REFACTOR / DOCS/CHORE**)" | (b) per-type — **confirmed** |
| `AGENTS.md:145` | P.5 row owner cell: "subagent (specify skill) — **FEATURE/CROSS-CUTTING only**" | (a) — **confirmed** |
| `AGENTS.md:147`, `:429`, `:640` | `:147` "the P.4 artifact exists"; `:429` "the type's Phase 1 output (draft spec / triage / baseline / scope) recorded"; `:640` "the type's Phase 1 output recorded" — none mentions P.5 | (b) — **confirmed** |
| `AGENTS.md:235`, `:339` | diagram "P.5 … (FEATURE/CROSS-CUTTING only) ◆ ──► READY ◆"; Phase Matrix cell "**P.5 Verify self-consistency** (FEATURE/CROSS-CUTTING only) ◆ READY" | (a) — **confirmed** |
| `specify:89`, `:90` | section headers verified by grep: `:58` `## Atomic Steps (FEATURE / CROSS-CUTTING)`, `:85` `### P.5 Verify self-consistency` — both hits sit inside a step that exists only for the spec types | (a) — **confirmed** |
| `specify:115`, `:117`, `:129`, `:131` | A/C path headers carry "(runs at **P.2 / P.4 / P.5**…)"; B/D/E (`:121`, `:133`, `:139`) carry "(runs at **P.4**, questions at **P.2**)" and no P.5 | (a) — **confirmed** |
| `implement:34`, `test:33` | "Phase 4/3 runs only for a change that passed the Phase P **READY** gate (TODO `Status: READY`, every question … `ANSWERED`)" — no P.5 clause | (b) — **confirmed** |
| `docs/todo/template.md:7`, `:44`; `docs/questions/template.md` | template `:7` is the `Status:` value list, `:44` the Prep-log row (the file's only P.5 hit); `docs/questions/template.md` → **0** hits for both `P\.5` and `READY` | (c) — **confirmed** |

Sweep arithmetic (record nit, not a document defect): the S6.9 table reports 24 `P\.5` and 42 `READY` hits; the final state gives **25** and **43**. The difference is exactly `docs/workflow/PROBLEMS.md:377`, the P-39 recipe line the same commit added (it contains both "P.5" and "READY"), which the table's `PROBLEMS.md:372` row does not list. Both extra hits are the problem record itself — class (c), they describe the defect class and never produce READY — so the sweep's conclusion is unaffected.

**Cosmetic observation — `docs/todo/template.md:44` (the unqualified Prep-log row "P.5 Self-consistency"): ACCEPTED FOLLOW-UP, not a finding** — no gate anywhere in the live guidance reads the Prep log: the READY gate is TODO `Status: READY` + every question `ANSWERED` + the type's Phase 1 output (`AGENTS.md:147`, `:159`, `:429`, `:640`; `specify:170`, `:211`), so a non-spec type that leaves the row blank still reaches READY, and the defect class F-11/F-15 was a gate signal with no reachable producer, which this row is not. It is a one-word clarity nit next to the already-qualified `:11` "**Spec:** … FEATURE/CROSS-CUTTING only" row.

**Review chain complete.** S6.1 + S6.2 + S6.3 (review checks R1–R7, findings F-1..F-4) → S5.5 fix → S6.5 fix (F-5, F-7..F-9) → S6.6 re-review → S6.7 fix (F-11..F-14) → S6.8 re-review (F-15) → S6.9 fix → **S6.10 final verdict (this section)**. Every finding raised is closed or explicitly accepted: F-1..F-9 (F-7 as F-7(a) + F-7(b)) and F-11..F-15 closed; F-10 (the stale `.pi/workflows/spec-tdd.workflow.ts`) accepted at S6.4 and still an open follow-up (`docs/verification/prepared-workflow.md:78-80`). S6.4 (version bump + PR) has not run: `gh pr list --head chore/prepared-workflow` → no PR, and no version bump is due (DOCS/CHORE → none; `pyproject.toml:4` still `0.6.0`) — both are the next step's work, gated on this verdict.

**No rule was weakened anywhere in the fix commits** (`d374418`, `4756a41`, `4b45bdd`, `6807d38`). `git diff main..HEAD -- AGENTS.md .agents/skills` deletes seven normative-looking lines; every one is replaced by an equivalent or narrower statement (todo set moved Phase 0 → P.1; `AI_Questions.md` → the per-change question file; the legend's "workflow **stops** until answered" → the change-level WAITING rule, which is *stronger*: the workflow must keep moving). No prohibition was deleted: `grep -rn "exactly one" AGENTS.md .agents/skills` leaves only "exactly one worktree at a time" (`:91`, `git:36`) and "exactly one atomic step" (`:364`) — the old global "exactly one `in_progress`" wording survives nowhere. Final wording of the four rules the fixes touched:

(a) **Direct-to-`main` exception** — `AGENTS.md:118`: "**Direct-to-`main` commits are allowed only for the planning records** under `docs/todo/` and `docs/questions/` — their creation at P.1–P.3 **and every later `Status:` advance through `MERGED`** (see \"Planning records (owner: the orchestrator)\"). Nothing else — no spec, no verification record, no source, no test — may be committed directly to `main`; it reaches `main` only through a merged PR." (same limit at `AGENTS.md:135`, `:675`; `git:73`, `:155`; `specify:171` — path set unchanged, owner narrowed to the orchestrator in the primary worktree)

(b) **At most one `in_progress` per change** — `AGENTS.md:411`: "**Todo sets.** One todo set per change; at most one `in_progress` **per change**; a WAITING change's step stays `in_progress` with an `activeForm` naming the wait (e.g. \"waiting for spec PR merge\")." and `:427`: "**Before starting a step**, the orchestrator marks its todo `in_progress` … **before launching the step's subagent**. At most one step is `in_progress` **per change** (several changes may each have one)."

(c) **Never idle** — `AGENTS.md:408`: "**Never idle.** A change that reaches a human gate — S1.4 (spec approval), S6.4 (PR merge), or a mid-workflow `BLOCKED-USER` / `BLOCKED-HUMAN` — goes **WAITING**; the orchestrator immediately takes the next ready step of **another** change. It stops only when every in-flight change is WAITING **and** no prepared change is READY." (restated as a prohibition at `:674`, an obligation at `:702`, and in all six skills: `specify:50`, `decompose:32`, `implement:36`, `test:35`, `verify:34`, `review:44`, `git:104`)

(d) **≥ 20-question floor (FEATURE/CROSS-CUTTING)** — `AGENTS.md:142` (P.2 row, Done-when cell): "≥ 20 questions (FEATURE/CROSS-CUTTING) recorded in **one** `BLOCKED-USER` batch; overlap checked against `docs/specs/` **and** every TODO in `docs/todo/`"; `specify:174`: "Ask at least 20 questions during interrogation (FEATURE/CROSS-CUTTING). **Record each in the change's question file `docs/questions/<name>.md`** and return the **complete batch in a single** `BLOCKED-USER` handoff … Do not return partial batches across multiple round-trips." — qualified in every statement of it (`AGENTS.md:701`, `specify:74` under `## Atomic Steps (FEATURE / CROSS-CUTTING)` `:58`, `specify:216` nested under the FEATURE/CROSS-CUTTING bullet of the READY checklist, `docs/questions/template.md:30`), and imposed on no other type.

**Verdict (S6.10).** F-15 is closed; the sweep's conclusion holds under independent spot-check; the one remaining observation blocks no gate. Nothing blocks a gate.

REVIEW REPORT: CLEAN

### Accepted follow-ups (not findings)

1. `docs/todo/template.md:44` — qualify the Prep-log row as "P.5 Self-consistency (FEATURE/CROSS-CUTTING)" so it matches the already-qualified `Spec:` row at `:11`. Cosmetic; blocks no gate (adjudicated above).
2. `.agents/skills/specify/SKILL.md:14`, `:45`, `:46` — unqualified restatements of the step mapping / subagent step list (they list P.5 and S1.4 without naming the types). Class (c) per S6.9: they neither set nor gate READY, and the per-type Phase P list (`:18-21`) plus paths A–E (`:115`, `:121`, `:129`, `:133`, `:139`) govern which steps a change runs. A "(FEATURE/CROSS-CUTTING)" qualifier on `:45`/`:46` would make them read like `AGENTS.md:175`. Cosmetic; blocks no gate.
3. `docs/verification/prepared-workflow.md` (S6.9 sweep table) — the hit counts (24 / 42) are one lower than the final state (25 / 43) because the commit's own `PROBLEMS.md:377` line is not listed; correct the count or add the row if the record is next edited. Record-accuracy nit, not a document defect.
4. `docs/questions/template.md:9` header `Status:` — F-14's producer is named on the header line itself; if the F-5 ownership table is next touched, adding the row there keeps both places in sync (S6.8 noted this). Cosmetic.

**Gates (S6.10).** No gate re-run (P-27; Phase 5 confirmed the gate set CLEAN and S6.8/S6.9 recorded `uv run ruff check .` → `All checks passed!`). `git log --oneline main..HEAD` → 12 commits, chain complete. `git diff main --name-only` → 14 paths, all `.md` — unchanged DOCS/CHORE scope. This step: `ruff` n/a (no code written), one file changed (`docs/verification/prepared-workflow.md`), one commit. Next: **S6.4** — no version bump (DOCS/CHORE), open the PR to `main` for human review/merge, then STOP (human governance).
