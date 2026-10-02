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
