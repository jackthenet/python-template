# AGENTS.md — AI Agent Operating Guidelines

This repository strictly enforces a **Spec-Driven, Test-Driven Development (Spec-TDD) Workflow**. AI agents operating in this project MUST follow the procedures defined below.

---

## Primary Constraint: No Direct Implementation Code
**DO NOT write, modify, or scaffold implementation source code (`src/`, `lib/`, `app/`, etc.) without the type-specific gates of the change type being worked on.**

- **FEATURE / CROSS-CUTTING**: an approved Specification file and a validated Task Graph are required (Phases 1–3).
- **ISSUE**: a triage record (affected REQ/AC) and a failing reproduction test (RED) are required before the fix.
- **REFACTOR**: a GREEN baseline of the full suite is required before any restructuring.
- **DOCS/CHORE**: a confirmed no-behavior-delta scope is required.

If asked to implement a new feature, refactor core components, or build a system, you MUST complete the phases required by the change type first (see the Phase Matrix).

---

## Tooling & Execution Environment
This repository utilizes modern Python tooling managed via `uv`:
- **Package Manager:** `uv` (Use `uv run <command>` for isolated execution)
- **Quality Assurance & Formatting:** `ruff` (`uv run ruff check .` / `uv run ruff format .`). The verify phase lints the whole repo with `uv run ruff check .`, matching CI (`.github/workflows/lint.yml`) exactly — pre-existing lint errors are in scope, not out of scope.
- **Type Checking:** `mypy` (`uv run mypy src/`)
- **Test Runner:** `pytest` (`uv run pytest`)
- **Property Testing:** `hypothesis` (`uv run pytest tests/property/`)
- **Standard Verification:** `uv run pytest tests/`
- **Version Bumping:** `bump-my-version` (`uv tool install bump-my-version`; config in `pyproject.toml` under `[tool.bumpversion]`)

---

## Git Worktrees

The workflow uses **git worktrees** to isolate each in-flight change in its own working directory. This keeps `main` permanently available and allows multiple changes to progress in parallel (e.g., feature A's spec is in human review while issue B is being implemented) without branch switching, stashing, or checkout conflicts.

### Layout

- **Primary worktree**: the repository itself. It is **always on `main` and never switched** to another branch.
- **Change worktrees**: inside a central directory next to the repository, named `<repo-name>-worktrees`, with one subdirectory per change type, and one subdirectory per change (the plain change name, no type prefix):

```text
C:/workspace/active-projects/
├── python-template_kopie/                  (primary worktree: main)
└── python-template_kopie-worktrees/
    ├── feature/
    │   ├── settings-coverage/              (feature/settings-coverage)
    │   └── authentication/                (feature/authentication)
    └── issue/
        └── login-lockout/                 (issue/login-lockout)
```

- Branch naming per change type: `feature/<name>`, `issue/<name>`, `crosscut/<name>`, `refactor/<name>`, `chore/<name>`.
- Each change branch lives in **exactly one worktree at a time**.
- All worktrees share the same repository refs, so `git log main -- ...` works from anywhere.

### Lifecycle (mapped to the 6 phases)

Exact commands, procedures, and edge cases for each operation live in the git skill (`.agents/skills/git/SKILL.md`).

- **Phase 1 (specify)** — classify the change type, then create the change branch **and its worktree** (git skill: "Create change worktree"). All work from Phase 1 through Phase 6 is performed inside the change worktree.
- **Phases 2–5** — decompose, test, implement, verify: all commands (`uv run ...`) run inside the change worktree. The primary worktree (`main`) is used for:
  - spec-approval verification (`git log main -- docs/specs/[name].md`, FEATURE/CROSS-CUTTING only),
  - running the full test suite against `main`,
  - post-merge verification.
- **Phase 6 (review)** — open the PR from the change worktree (git skill: "Create PR"). The agent MUST NOT merge the PR (human governance).
- **Post-merge cleanup** — after the human merges the PR, the agent performs post-merge cleanup (git skill: "Post-merge cleanup"): verify the merge on `main`, remove the worktree, delete the local and remote change branches.

### Rules

- Never check out a change branch in the primary worktree.
- Never create two worktrees for the same change branch.
- Stay strictly inside the change's worktree: do not modify other changes' worktrees or branches.
- Each worktree has its own `uv` environment; run `uv run <command>` inside the worktree (the global uv cache is shared, so no extra setup is needed).
- `git worktree remove` fails on a dirty worktree: do NOT use `--force` on an unmerged change. Force-removal is only permitted when the changes are intentionally discarded.
- If a worktree directory was deleted manually, run `git worktree prune`.
- Check for leftovers with `git worktree list`; after cleanup, the only worktree should be the primary (`main`).

---

## The Spec-TDD Workflow Protocol (Change-Type Routed)

Every change in this repository is one of five **change types**. The type determines which phases run, what each phase produces, and which gates apply. **Phase 1 is the single entry point for all types**: it classifies the change first (Phase 0), then executes the type-specific Phase 1.

### Change Types & Classification (Phase 0)

Classify the change **before any other work** (specify skill, step 0). Use the **first matching criterion, in this order**:

| # | Type | Criterion |
|---|------|-----------|
| 1 | **ISSUE** | The change fixes a deviation from **approved spec behavior** (a defect). The approved spec is the source of truth; no new behavior is introduced. |
| 2 | **FEATURE** | The change adds externally observable behavior or capability **not covered by an approved spec**. |
| 3 | **CROSS-CUTTING** | The change intentionally spans **two or more features**: new shared capability, architecture change, or shared-infrastructure change. |
| 4 | **REFACTOR** | The change restructures existing code **without altering externally observable behavior**. |
| 5 | **DOCS/CHORE** | The change **does not alter behavior**: documentation, comments, configuration, CI, tooling. |

Classification is a first pass. If a later phase reveals the change belongs to a different type, apply the **Escalation Rules** at the end of this section.

### Phase Matrix

Which phases run for each type, and what each phase produces:

| Phase | FEATURE | ISSUE | CROSS-CUTTING | REFACTOR | DOCS/CHORE |
|-------|---------|-------|---------------|----------|------------|
| **1 Specify** | Adversarial interrogation → spec (REQ/AC/INV/EDGE/NFR) → **PR approval** | **Triage**: affected REQ/AC from existing specs, defect confirmation, reproduction plan. No spec, no PR. | Adversarial interrogation → spec **with per-feature impact analysis** → **PR approval** | **Baseline**: full suite GREEN + refactor scope. No spec, no PR. | **Scope**: exact non-behavior changes; confirm no behavior delta. No spec, no PR. |
| **2 Decompose** | ADRs + task DAG | — (skip; the triage is the plan) | ADRs + task DAG **grouped by affected feature** | — (skip) | — (skip) |
| **3 Test & RED** | Tests derived from spec → RED | **Reproduction test** → RED | Tests derived from spec → RED | — (skip; existing tests are the contract) | — (skip) |
| **4 Implement** | GREEN from DAG + refactor | **Minimal fix** → GREEN | GREEN from DAG + refactor | Behavior-preserving steps; suite stays GREEN | Make the change |
| **5 Verify** | Full gate set | Targeted tests + full regression + lint/types | Full gate set **+ per-feature traceability updates** | Full regression + architecture + lint/types (no spec coverage) | Light: lint/types where applicable |
| **6 Review** | Full review → PR → merge → cleanup | Full review → PR → merge → cleanup | Full review → PR → merge → cleanup | Full review (**tests not weakened**) → PR → merge → cleanup | Light review → PR → merge → cleanup |

"Full gate set" = the Phase 5 FEATURE checks below. Every type ends with a PR to `main` for human review/merge (human governance).

### Skill-to-Phase Mapping

| Phase | Skill | Applies to | Purpose |
|-------|-------|------------|---------|
| Phase 0+1: CLASSIFY & SPECIFY | `specify` | all | Classifies the change type, creates the change branch and worktree, and executes the type-specific Phase 1 (spec, triage, baseline, or scope). |
| Phase 2: DECOMPOSE | `decompose` | FEATURE, CROSS-CUTTING | Creates ADRs and decomposes the spec into a machine-readable JSON task DAG (per-feature grouping for CROSS-CUTTING). |
| Phase 3: TEST & RED | `test` | FEATURE, CROSS-CUTTING, ISSUE | Derives tests from the spec (FEATURE/CROSS-CUTTING) or writes the reproduction test (ISSUE), and confirms RED state. |
| Phase 4: IMPLEMENT | `implement` | all | Turns RED into GREEN (or performs behavior-preserving steps / makes the chore change), then refactors without changing specified behavior. |
| Phase 5: VERIFY | `verify` | all | Produces evidence that the change satisfies its type-specific gates. |
| Phase 6: REVIEW | `review` | all | Reviews the change against its type-specific criteria before reviewing implementation style. |
| (cross-cutting) | `git` | all | Branch/worktree creation, PR creation, post-merge cleanup. |

### Phase Execution (Subagents)

Every workflow step is executed by a **new subagent** launched via the `subagent` tool (type `general-purpose`). The orchestrating agent (the agent talking to the user) never executes a phase itself, and a step subagent never executes more than one phase.

**Roles.**
- **Orchestrator** — performs Phase 0 (classify, create branch/worktree, create the todo set); launches one subagent per workflow step; presents user questions and approval requests (spec approval, PR merge) to the user; manages the todo list; verifies each step's handoff before launching the next step.
- **Step subagent** — reads its phase skill file and executes exactly one phase inside the change worktree. It never executes another phase, never launches a subagent, and never talks to the user.

**Steps that get a subagent.** Phase 1 (specify), Phase 2 (decompose), Phase 3 (test), Phase 4 (implement), Phase 5 (verify), Phase 6 (review), and post-merge cleanup (git skill). **Phase 0 stays on the orchestrator** — classification, branch/worktree creation, and todo-set creation are required to route the phases.

**Launch contract.** The orchestrator's launch prompt MUST contain:
- the change name and type;
- the change worktree path (all commands run there);
- the phase skill file to read first (`.agents/skills/<skill>/SKILL.md`);
- the previous step's handoff (the prior phase's status, gate result, artifacts, and evidence location);
- the required handoff output (below).

**Handoff output.** The step subagent MUST end with a structured handoff:
- `status` — `DONE` (gate passed) | `BLOCKED-USER` (needs user input) | `BLOCKED-HUMAN` (needs human governance: spec approval, PR merge) | `FAILED` (gate failed, with reason).
- `gate` — the type-specific gate result and where the evidence is recorded (`docs/verification/<name>.md`).
- `artifacts` — the files, commits, and PRs created.
- `questions` (BLOCKED-USER only) — the questions for the user.
- `next` — the next step to launch per the Phase Matrix, or `STOP`.

**User questions.** A step subagent MUST NOT call `ask_user_question` itself. It returns `BLOCKED-USER` with its questions. The orchestrator presents them to the user (in batches of up to 4 per `ask_user_question` call) and **resumes the same subagent** with the answers. Resuming continues the same step only — the next step always gets a new subagent.

**One subagent per step execution.** Every time a step is (re-)entered — including re-entry after a failed gate (Phase 5 → Phase 4 or Phase 3) and reclassification re-runs of Phase 1 — the orchestrator launches a new subagent. A step subagent is never resumed to execute a different phase.

**Handoff verification.** The orchestrator MUST verify a handoff before marking the step's todo `completed`: the evidence exists in `docs/verification/<name>.md` and the commits exist in the worktree. A subagent's self-report is not evidence.

**Fast path.** Emergency/fast-path exceptions (≤ 2 lines, one-line fix with an existing failing test, `--skip-spec`) bypass the workflow entirely — no phases, no subagents.

### Todo Tracking Discipline (todo tool)

The agent MUST track every in-flight change with the `todo` tool. The todo list is the change's live progress record: **one item per workflow step** the change type runs (per the Phase Matrix), **linked by dependency** in phase order, with **status orders** driven by the workflow gates. Todo management belongs to the **orchestrator** (see Phase Execution (Subagents)): step subagents never create, update, or read the todo list.

**Creating the todo set (Phase 0).** When starting a change, create one todo item per workflow step the change type executes, in phase order. Give each a short imperative subject naming the phase and its key output. A step the type skips (per the Phase Matrix) gets **no** todo item.

**Linking dependencies.** Link each step to its predecessor with `blockedBy` so the list encodes the phase order: Phase 2 blocked by Phase 1, Phase 3 blocked by Phase 2, and so on. The final **Post-merge cleanup** item is blocked by Phase 6.

**Status orders (at the right steps).**
- **Before starting a step**, the orchestrator marks its todo `in_progress` (with a present-continuous `activeForm` label, e.g. "running the RED gate") **before launching the step's subagent**. Exactly one step is `in_progress` at a time.
- **Immediately when a step's type-specific gate passes**, the orchestrator marks its todo `completed` **after verifying the step's handoff** — never batch completions. A step is `completed` only when its gate is satisfied:
  - Phase 1 — `completed` when the type-specific output exists (spec PR opened / triage recorded / GREEN baseline / scope recorded).
  - Phase 2 — `completed` when the task DAG is initialized (copied to `.github/task-runner/tasks.json`).
  - Phase 3 — `completed` only when **RED is observed** and recorded.
  - Phase 4 — `completed` only when **GREEN is achieved** and recorded.
  - Phase 5 — `completed` only when the type-specific gate set passes.
  - Phase 6 — `completed` only when the review report is clean **and** the PR is open.
  - Post-merge cleanup — `in_progress` after the human merges the PR; `completed` when the worktree is removed and the local + remote branches are deleted.

**Reclassification (Escalation Rules).** When the change type changes, re-derive the todo set for the new type (add/remove items, relink with `blockedBy`) and record the reclassification in `docs/verification/[name].md`.

**Example (FEATURE).**
```text
#1 Phase 1: Specify — spec + PR approval
#2 Phase 2: Decompose — ADRs + task DAG            ⛓ #1
#3 Phase 3: Test & RED — tests RED                 ⛓ #2
#4 Phase 4: Implement — GREEN                       ⛓ #3
#5 Phase 5: Verify — full gate set                 ⛓ #4
#6 Phase 6: Review — clean report + PR             ⛓ #5
#7 Post-merge cleanup — verify + remove + delete   ⛓ #6
```

**Example (ISSUE)** — Phase 2 is skipped, so it has no todo item:
```text
#1 Phase 1: Triage — affected REQ/AC + repro plan
#2 Phase 3: Repro test — RED                       ⛓ #1
#3 Phase 4: Minimal fix — GREEN                    ⛓ #2
#4 Phase 5: Verify — regression + lint/types      ⛓ #3
#5 Phase 6: Review — clean report + PR            ⛓ #4
#6 Post-merge cleanup — verify + remove + delete  ⛓ #5
```

### Phase 1: CLASSIFY & SPECIFY
Single entry point for all change types (specify skill).

**Phase 0 — Classify (all types):**
1. Create the change branch **and its worktree** from `main` per the "Git Worktrees" section. Branch: `<type>/<name>` (`feature/`, `issue/`, `crosscut/`, `refactor/`, `chore/`).
2. Classify the change using the Change Types table. Record the type in the change's verification artifact (`docs/verification/[name].md`).

**FEATURE:**
3. Adversarially interrogate the feature idea to discover ambiguity, hidden requirements, edge cases, and scope boundaries; capture a feature brief. The brief is an **intermediate artifact** of the interrogation — do **not** save it as a separate `.brief.md` file. Fold it into the spec (goals/overview, scope boundaries, out-of-scope, edge cases); the spec is the single kept artifact.
4. Search and read existing codebase files to understand current context and patterns.
5. Check `docs/specs/template.md` for formatting requirements.
6. Draft a complete feature spec at `docs/specs/[feature-name].md`.
7. Include exact API schemas, Pydantic models, interface signatures, and non-functional requirements.
8. Assign stable IDs to every normative requirement (`REQ-XXX`), acceptance criterion (`AC-XXX`), invariant (`INV-XXX`), edge case (`EDGE-XXX`), and NFR (`NFR-XXX`).
9. Define the test strategy mapping each AC/INV/EDGE to a test category and test function.
10. **STOP and present the spec for human approval via Git PR.**

**ISSUE (triage — no spec, no PR):**
11. Identify the affected requirements (`REQ-XXX`) and acceptance criteria (`AC-XXX`) from the **existing approved specs** in `docs/specs/`; cite the spec files and IDs.
12. Confirm the defect: the observed behavior deviates from what the spec requires (cite the spec ID and state the observed vs. required behavior).
13. If the fix requires behavior the spec does not state, STOP: open a Spec Amendment PR (Spec Amendment Workflow) or reclassify as FEATURE.
14. Write the reproduction plan: the failing test(s) that reproduce the defect, the fix scope, and the files expected to change.
15. Record the triage in `docs/verification/[name].md` (type: ISSUE, affected REQ/AC, defect confirmation, reproduction plan).

**CROSS-CUTTING:**
16. Adversarially interrogate the change (goals, affected features, constraints, out-of-scope, edge cases).
17. Draft the spec at `docs/specs/[name].md` with an **Impact Analysis** section: every affected feature, what changes in each, and which of their REQ/AC IDs are touched.
18. Assign stable IDs (`REQ-XXX`, `AC-XXX`, `INV-XXX`, `EDGE-XXX`, `NFR-XXX`) and define the test strategy as for FEATURE.
19. **STOP and present the spec for human approval via Git PR.**

**REFACTOR (baseline — no spec, no PR):**
20. Run the full suite (`uv run pytest tests/ -v`) and confirm it is GREEN. Record the baseline in `docs/verification/[name].md`.
21. Define the refactor scope: which code moves/renames/simplifies, and the invariants that MUST hold (no observable behavior change, no test changes).

**DOCS/CHORE (scope — no spec, no PR):**
22. Define the exact non-behavior changes (files, content) and confirm they do not alter externally observable behavior. Record the scope in `docs/verification/[name].md`.

### Phase 2: DECOMPOSE (`docs/decisions/`, `docs/tasks/`)
FEATURE and CROSS-CUTTING only. Once the specification file is merged into `main`:
1. Create ADRs in `docs/decisions/` for significant design decisions (WHY, not WHAT).
2. Decompose the spec into a machine-readable JSON task DAG at `docs/tasks/[name].tasks.json`.
3. Each task MUST specify:
   - `requirements`: REQ-XXX IDs covered by this task.
   - `acceptance_criteria`: AC-XXX IDs covered by this task.
   - `tests_to_create`: Test functions to write (MUST come before implementation scope).
   - `red_command`: Command to confirm RED state.
   - `implementation_steps`: Explicit steps for implementation.
   - `green_command`: Command to confirm GREEN state.
   - `design_constraints`: Constraints that must be respected.
   - `completion_gates`: Gates that must pass before the task is complete.
4. CROSS-CUTTING: group tasks by affected feature so each feature's changes are independently verifiable.
5. Copy `docs/tasks/[name].tasks.json` to `.github/task-runner/tasks.json` to initialize the active build environment.
### Phase 3: TEST & RED (`tests/`)
FEATURE, CROSS-CUTTING, and ISSUE.

**FEATURE / CROSS-CUTTING** (after the task DAG is initialized):
1. Write acceptance tests derived directly from the spec's acceptance criteria.
2. Write property tests for every invariant (`INV-XXX`) using Hypothesis.
3. Write unit tests for edge cases and error conditions.
4. Write contract tests for NFR contract requirements.
5. Write integration tests for multi-component interactions.
6. **Run the test suite and confirm RED state** (tests must fail before implementation).
7. Record RED evidence in `docs/verification/[name].md`.
8. Update the traceability matrix in `docs/verification/traceability.md` with test references.

**ISSUE** (after triage):
1. Write the reproduction test(s) from the triage plan. They MUST fail on the current (defective) code — this is RED for the issue.
2. **Run the reproduction tests and confirm RED state.**
3. Record RED evidence in `docs/verification/[name].md`.
4. Update the traceability matrix with the issue's test references (affected REQ/AC + reproduction test).
### Phase 4: IMPLEMENT
All types.

**FEATURE / CROSS-CUTTING** (when instructed to execute tasks):
1. Pick a ready task from the task DAG.
2. **QA Agent (Red):** Write failing tests in `allowed_files.test_files`. Run `red_command`. Confirm tests FAIL.
3. **Record RED evidence** in `docs/verification/[name].md`.
4. **Coder Agent (Green):** Implement logic in `allowed_files.source_files` following `implementation_steps`. Run `green_command`. Confirm tests PASS 100%.
5. **Record GREEN evidence** in `docs/verification/[name].md`.
6. **Refactor:** Improve code without changing observable behavior. Re-run `green_command`.
7. **Commit & Update Status:** Set `"status": "VERIFIED"` in `.github/task-runner/tasks.json`. Sync final statuses back to `docs/tasks/[name].tasks.json`.

**ISSUE** (after RED confirmed):
8. Implement the **minimal fix** that turns the reproduction tests GREEN. No new behavior beyond the affected spec IDs.
9. **Record GREEN evidence** in `docs/verification/[name].md`.

**REFACTOR** (after baseline):
10. Perform small, focused behavior-preserving steps. Re-run the full suite after every step; it MUST stay GREEN.
11. Do not modify, weaken, or delete any test.

**DOCS/CHORE** (after scope):
12. Make the scoped non-behavior changes.
### Phase 5: VERIFY
All types.

**FEATURE / CROSS-CUTTING** (after all tasks are complete):    
1. Run the full test suite: `uv run pytest tests/ -v`.
2. Run acceptance tests: `uv run pytest tests/acceptance/ -v`.
3. Run property tests: `uv run pytest tests/property/ -v`.
4. Run contract tests: `uv run pytest tests/contract/ -v`.
5. Update the traceability matrix: every REQ must have at least one GREEN test.
6. Produce a verification report: specification coverage, acceptance coverage, branch coverage.
7. **Spec coverage = 100% is required.** Code coverage is a secondary quality signal, not evidence that the specification has been implemented.
8. **If verification fails**, the agent MUST re-enter either Phase 4 (IMPLEMENT) to fix the failing behavior, or Phase 3 (TEST & RED) to re-derive failing tests from the specification. The agent MUST NOT mark the change verified until spec coverage = 100% and all gates pass.
   CROSS-CUTTING additionally: update the traceability matrix rows of every affected feature.

**ISSUE**:
9. Run the reproduction tests (GREEN) and the full regression suite (no new failures).
10. Run lint (`uv run ruff check .`) and type checks (`uv run mypy src/`).
11. Update the traceability matrix with the issue's evidence rows.
12. If the regression suite shows a failure, classify it as in the FEATURE path (pre-existing vs regression).

**REFACTOR**:
13. Run the full regression suite (MUST be GREEN, zero test changes) and the architecture rules (`uv run pytest tests/architecture/ -v`).
14. Run lint (`uv run ruff check .`) and type checks (`uv run mypy src/`).
15. Confirm no observable behavior changed (suite result identical to baseline).

**DOCS/CHORE**:
16. Run lint and type checks where applicable; confirm no test files or behavior were touched.
### Phase 6: REVIEW
All types. After verification passes:
1. Review all code changes against the change's normative basis: the approved spec (FEATURE/CROSS-CUTTING), the triage record + affected spec IDs (ISSUE), the baseline + scope (REFACTOR), or the scope (DOCS/CHORE).
2. Check traceability: every REQ has at least one GREEN test, every acceptance test traces back to a normative requirement.
3. Verify feature boundaries: code lives in the correct feature directory, no cross-feature internal imports.
4. Verify architecture rules: `model/` contains domain concepts, `services/` contains use cases, `shared/` is deliberately small.
5. Verify acceptance tests were not weakened or deleted to achieve GREEN.
6. Verify no behavior was introduced that is not represented in the specification (FEATURE/CROSS-CUTTING), or that no behavior changed at all beyond the type's contract (ISSUE/REFACTOR/DOCS-CHORE).
7. Produce a review report documenting any findings and their resolutions.
8. **The change is only considered complete when the review report is clean.**
9. **When the review report is clean, document reusable shared capabilities in `AGENTS.md`** (FEATURE/CROSS-CUTTING only). If the change is a shared capability reusable by future changes (not a one-off), add a short "how to use this" note so future changes use it correctly. Skip this if the change is not applicable to other changes.
10. **When the review report is clean, bump the version per the change type** (Versioning section: ISSUE → `patch`, FEATURE → `minor`, CROSS-CUTTING → `minor`/`major`; no bump for REFACTOR/DOCS-CHORE). Run `bump-my-version bump <level>` in the change worktree with a clean working tree; the bump commit is part of the PR.
11. **When the review report is clean, open a PR** for the change branch to `main` and present it for human review/merge, then STOP. The agent MUST NOT merge the PR itself (human governance).

### Escalation Rules (Type Conversion)

Apply during any phase when the change's true nature is revealed:

- **ISSUE → spec amendment or FEATURE**: the fix requires behavior the approved spec does not state. Open a Spec Amendment PR (if amending existing spec IDs) or reclassify as FEATURE (if it is a missing capability).
- **ISSUE/FEATURE → CROSS-CUTTING**: impact analysis reveals the change spans two or more features.
- **CROSS-CUTTING → FEATURE or ISSUE**: impact analysis reveals the change is confined to a single feature.
- **REFACTOR → ISSUE or FEATURE**: a behavior change is discovered. Stop; reclassify (defect → ISSUE, new behavior → FEATURE).
- **DOCS/CHORE → any**: a behavior change is discovered. Stop; reclassify.

On reclassification: keep the same worktree, rename the branch to the new type (`git branch -m <old> <new>`), re-run the new type's Phase 1 from its first step, and record the reclassification in `docs/verification/[name].md`.

---

## Review Gate (Phase 6)

A change is considered **COMPLETE** if and only if the Phase 6 review report is clean. A clean review report means (type-specific):

- **FEATURE / CROSS-CUTTING**: every REQ-XXX has at least one GREEN test; every acceptance test traces back to a normative requirement; no behavior was introduced that is not represented in the specification; CROSS-CUTTING additionally has updated traceability rows for every affected feature.
- **ISSUE**: the reproduction tests are GREEN; the fix introduces no behavior beyond the affected spec IDs; the full regression suite has no new failures.
- **REFACTOR**: the full suite is GREEN with zero test changes; no observable behavior changed.
- **DOCS/CHORE**: no behavior, test, or source-behavior changes beyond the scoped non-behavior changes.
- **All types**: no acceptance test was weakened or deleted to achieve GREEN; feature boundaries and architecture rules are respected.

If the review report is not clean, the agent MUST resolve every finding and re-run the review before declaring the change complete. A change with an open finding MUST NOT be merged or marked verified.

When the review report IS clean, the change branch MUST be merged into `main` via a GitHub pull request. The agent MUST open the PR and present it for human review/merge, then STOP — the agent MUST NOT merge the PR itself (human governance).

---

## State Machine

Every task transitions through this state machine:

```
SPECIFIED → TESTS_WRITTEN → RED_CONFIRMED → IMPLEMENTING → GREEN → REFACTORED → VERIFIED
```

Each change type enters at a different state (phases it skips are not entered):

| Type | Entry state |
|------|-------------|
| FEATURE, CROSS-CUTTING | `SPECIFIED` (after spec approval + task DAG) |
| ISSUE | `TESTS_WRITTEN` (after triage; RED is the reproduction test) |
| REFACTOR | `IMPLEMENTING` (after GREEN baseline) |
| DOCS/CHORE | `IMPLEMENTING` (after scope) |

- An agent MUST NOT transition from `TESTS_WRITTEN` to `IMPLEMENTING` unless RED has been observed (FEATURE/CROSS-CUTTING/ISSUE).
- An agent MUST NOT transition from `GREEN` to `VERIFIED` unless the traceability matrix is updated.

---

## Agent Prohibitions

An agent MUST NOT:
- Start implementation work before classifying the change type (Phase 0).
- Apply one change type's gates to a different type's change (use the Escalation Rules instead).
- Write implementation before acceptance tests exist.
- Modify an acceptance test merely to make implementation pass.
- Delete or weaken a test to achieve GREEN.
- Convert a failing acceptance test into a weaker test.
- Introduce behavior not represented by the specification without updating the specification first.
- Mark a requirement complete without executable evidence.
- Skip the RED gate (transitioning from TESTS_WRITTEN to IMPLEMENTING without observing RED).
- Let code coverage substitute for specification coverage.
- Advance a workflow phase without the todo status discipline (the phase's todo must be `in_progress` before the step starts and `completed` only when its type-specific gate passes — see the Todo Tracking Discipline).
- Execute a workflow phase directly in the orchestrator's context — every workflow step runs in a new subagent (see Phase Execution (Subagents)).

---

## Agent Obligations

An agent MUST:
1. Classify the change type (Phase 0) and record it in `docs/verification/[name].md`.
2. Identify affected requirements (REQ-XXX).
3. Identify acceptance criteria (AC-XXX).
4. Create executable tests.
5. Run them and demonstrate RED.
6. Obtain approval if required.
7. Implement the minimum behavior required.
8. Achieve GREEN.
9. Refactor without changing observable behavior.
10. Run regression tests.
11. Produce a traceability/evidence report.
12. Track the change with the `todo` tool per the Todo Tracking Discipline: one item per workflow step the type runs, linked by `blockedBy`, `in_progress` before a step starts, `completed` only when its gate passes.
13. Execute each workflow step in a new subagent via the `subagent` tool (see Phase Execution (Subagents)); verify each step's handoff before marking its todo `completed`.

---

## Test Category Hierarchy

| Category | Directory | Answers |
|----------|-----------|---------|
| Acceptance | `tests/acceptance/` | Does the system satisfy the requirement? |
| Integration | `tests/integration/` | Do the components work together correctly? |
| Contract | `tests/contract/` | Does the external/interface contract remain compatible? |
| Property | `tests/property/` | Does the invariant hold over a large input space? |
| Unit | `tests/unit/` | Does this particular component implement its local behavior correctly? |

---

## Traceability & Spec Drift

- Every normative requirement MUST have at least one executable test.
- Every acceptance test MUST trace back to a normative requirement.
- The traceability matrix in `docs/verification/traceability.md` MUST be maintained.
- CI MUST detect: missing tests, orphaned tests, missing evidence, and changed behavior without spec updates.
- **Tests are the contract.** Once acceptance tests are re-derived from an approved spec, the executable tests are the authoritative contract. If a spec *wording* or an implementation detail conflicts with a re-derived test, the test wins. The conflict MUST be flagged as a finding and resolved via the Spec Amendment Workflow — never by weakening, removing, or "fixing" the test to match the implementation.

---

## General Code & Style Conventions
- **Language & Runtime:** Python 3.14+
- **Type Safety:** Strict typing required. Every function signature must have explicit parameters and return type hints.
- **Testing Standard:** Framework `pytest`. Tests must precede implementation code. Never remove existing tests without explicit spec authorization.
- **Property Testing:** Use `hypothesis` for invariant verification. Strategies must match the domain.
- **Documentation:** Keep docstrings concise; explain *why* non-obvious logic exists rather than restating *what* the code does.

---

## Versioning

The project version is a semantic version (major.minor.patch) stored in `pyproject.toml` (`[project] version`) — the single source of truth. Version bumps are made with the `bump-my-version` tool (config: `[tool.bumpversion]` in `pyproject.toml`).

- **Install:** `uv tool install bump-my-version` (standalone tool; not a project dependency).
- **Bump mapping (per change type):**

  | Change type | Bump level |
  |---|---|
  | ISSUE | `patch` |
  | FEATURE | `minor` |
  | CROSS-CUTTING | `minor` (`major` if breaking) |
  | REFACTOR / DOCS-CHORE | none |

- **When:** Phase 6 (REVIEW), after the review report is clean and before the PR is opened. The working tree MUST be clean first (`allow_dirty` is off). The tool commits the version change with a templated message; that bump commit is part of the reviewed PR.
- **Tagging:** `tag = false` — the workflow never creates version tags on change branches. Version tags (e.g., `v0.2.0`) are created on `main` at release time, outside the workflow.
- **Dry run:** `bump-my-version bump <level> --dry-run` previews the file changes without touching anything.

---

## Using the Logging Feature

New backend features MUST use the shared logging feature at `src/backend/logging/` (spec: `docs/specs/logging.md`) instead of inventing their own logging.

- **Set it up once at startup.** Call `setup_logger(settings)` exactly once in the application entrypoint (e.g., `src/main.py` / backend startup) before any feature code runs. It is idempotent and thread-safe (later calls are no-ops).
- **Configure with `Settings`.** Build a `Settings` instance (or use `get_settings()`) to set `log_level`, `log_file`, `log_max_bytes`, `log_backup_count`, and `profiling_include_arguments`.
- **Trace functions with `@logged`.** Decorate sync or async functions/methods to log entry, exit (with elapsed ms), and exceptions. Usable bare (`@logged`, default level `DEBUG`) or with parameters: `level`, `slow_threshold_ms`, `slow_threshold_setting`, `include_args`, `context_getter`, `depth`.
- **Trace classes with `@logged_class`.** Decorate a class to apply `@logged` to every public method (private methods are skipped). Usable bare (`@logged_class`) or with parameters: `slow_threshold_ms` (concrete slow-call threshold stored on the class) and `include_args` (whether arguments are formatted into the entry record; secret handlers MUST use `False`). The class is marked traced (`__logged_class__ = True`) and exposes the concrete `slow_threshold_ms` attribute.
- **Simple statements.** The feature configures loguru's sinks, so feature code may also use loguru's `logger` directly (e.g., `logger.info("...")`) for one-off statements.
- **Conventions.** `diagnose=False` is enforced (no local variable leakage). Import the public API only (`from backend.logging import logged, logged_class, setup_logger, Settings, get_settings`); do not import the private `_setup` / `_decorator` modules. The logger MUST be set up before any `@logged` call or log statement.
- **Tracing policy (default).** Public service/registry/repository/provider classes MUST be traced with `@logged_class` by default, and public module-level functions MUST be traced with `@logged`. Direct loguru (`logger.info(...)`) is reserved for one-off statements (business decisions, lifecycle, warnings) and MUST NOT be used to hand-log entry/exit that the decorator already provides. Use `include_args=False` for methods that handle passwords/tokens/credentials. Set a sensible `slow_threshold_ms` on traced classes. Use semantic log levels (DEBUG for routine tracing, INFO for significant lifecycle, WARNING for recoverable issues, ERROR for failures). `setup_logger(Settings(...))` MUST be called exactly once in the application entrypoint, before any feature code runs.

```python
from backend.logging import Settings, logged, setup_logger

setup_logger(Settings(log_level="INFO"))

@logged
def my_func() -> None: ...
```

---

## Using the Event Bus Feature

New backend features MUST use the shared event bus at `src/backend/eventbus/` (spec: `docs/specs/event-bus.md`) for async communication between features instead of calling other features directly.

- **Publish events.** Get the bus with `get_event_bus()` (the module singleton) and call `publish(event)`. It is non-blocking: the event is enqueued and dispatched by a background worker.
- **Subscribe handlers.** Call `subscribe(event_type, handler)` to register a handler for an event type. Matching is by `isinstance`, so a handler for a base type also receives subclass events.
- **Define events.** Any class is a valid event type (typically a Pydantic model or dataclass). No base class is required.
- **Isolate errors.** A handler's exception is caught and logged; other handlers for the same event still run; the exception never propagates to the publisher.
- **Lifecycle.** The worker starts lazily on the first `publish()`. Call `shutdown()` to drain pending events and stop (idempotent). The bus is usable as a context manager.
- **Testing.** Use `EventBus(max_queue_size=...)` for a fresh instance, and `reset_event_bus()` to reset the module singleton between tests.

```python
from backend.eventbus import get_event_bus

def on_user_created(event: UserCreated) -> None: ...

get_event_bus().subscribe(UserCreated, on_user_created)
get_event_bus().publish(UserCreated(user_id="u1", email="e1"))
```

---

## Using the Settings Feature

New backend features that need typed, validated configuration values MUST use the shared settings registry at `src/backend/settings/` (spec: `docs/specs/settings.md`) instead of inventing their own configuration mechanism.

- **Get the registry.** Use `get_settings_registry()` (the module singleton) or `get_settings_registry(required=False)` (returns `None` without creating if the singleton doesn't exist) or instantiate `SettingsRegistry(event_bus=..., template_repository=..., value_repository=...)` for tests/DI. A `None` event bus uses the shared `get_event_bus()`; a `None` repository uses in-memory storage; a `None` value repository defaults to `YamlValueRepository('settings')`.
- **Register settings.** Call `register(SettingDefinition(...))` for a single setting or `register_feature("name", [definitions])` for a feature's settings (each key must start with `"name."`).
- **Feature-owned registration.** Each feature exposes `register_settings(registry)` in its `feature_settings.py` module (e.g., `from backend.logging import register_settings`). Call it at startup to register the feature's settings. The feature then reads its settings live via `_read_setting(registry, key, fallback)` on each use.
- **Read/write values.** Use `get_value(key)`, `set_value(key, value)` (validated), `reset(key)`, `reset_all()`. Values are always valid for their kind; invalid writes raise `SettingsValidationError`.
- **Kinds.** Seven kinds: TEXT, NUMBER, BOOLEAN, EMAIL, SLIDER, SELECT, LIST, each with kind-specific parameters and per-kind validation (see the spec). LIST uses `ListSpec(item_pattern, min_items, max_items, allow_duplicates)`.
- **Value persistence.** Use `YamlValueRepository(directory)` for YAML persistence of values (single `values.yaml`, atomic writes) or `MemoryValueRepository()` for in-memory. Persisted values load at registry construction and override newly registered defaults (REQ-022).
- **Views.** Use `to_view(key)`, `views()`, `grouped_views()` for renderable metadata (category/group hierarchy, status).
- **Templates.** Use `create_template`/`load_template`/`update_template`/`delete_template`/`get_template`/`list_templates` for named value profiles scoped to a (category, group). Create/update require exact scope coverage; load sets the template's values and leaves others as-is.
- **Storage.** Use `YamlTemplateRepository(directory)` for YAML persistence (one file per template, atomic writes) or `MemoryTemplateRepository()` for in-memory. Both implement the `TemplateRepository` ABC.
- **Events.** Value changes publish `SettingChanged` (key, value, previous) to the event bus (best-effort).
- **Errors.** Exceptions are the `SettingsError` hierarchy (from `backend.settings.exceptions`): `SettingsNotFoundError`, `SettingsValidationError`, `SettingsRegistrationError`, `TemplateNotFoundError`, `TemplateValidationError`, `TemplateStorageError`, `ValueStorageError`.
- **Testing.** Use `reset_settings_registry()` to reset the module singleton between tests. Test registries MUST pass an explicit isolated value repository (e.g., `YamlValueRepository(tempfile.mkdtemp())`) to avoid cross-test contamination from the shared default directory.

```python
from backend.settings import SettingDefinition, SettingKind, get_settings_registry

reg = get_settings_registry()
reg.register(SettingDefinition(key="app.name", kind=SettingKind.TEXT, default="default", category="app"))
reg.set_value("app.name", "new")
```

---

## Using the User Management Feature

New backend features that need to manage user account records MUST use the shared user-management feature at `src/backend/usermanagement/` (spec: `docs/specs/user-management.md`) instead of inventing their own user storage.

- **Service entry point.** Use `UserManager` (the use-case service). Construct it with a `UserRepository`, an optional `roles` iterable (default `("admin", "member")`), and an optional `event_bus` — any object with a `publish(event)` method (structural `EventPublisher` protocol, no base class required).
- **Core operations.** `create_user(UserCreate)`, `get_user(id)`, `get_user_by_username(name)`, `list_users(include_inactive)`, `update_user(id, UserUpdate)`, `delete_user(id)`, `change_password(id, new_password)`, `verify_password(id, password)`, `set_role(id, role)`, `activate_user(id)`, `deactivate_user(id)`. All reads return the read-only `UserRead` representation.
- **Guard.** Deactivating, deleting, or demoting the last active admin raises `LastAdminError` (REQ-008).
- **Events.** Mutations publish `UserCreated`/`UserUpdated`/`UserDeleted`/`UserPasswordChanged`/`UserRoleChanged`/`UserActivated`/`UserDeactivated` to the publisher (best-effort; a publisher failure never breaks the mutation).
- **Errors.** Exceptions are the `UserManagerError` hierarchy (from `backend.usermanagement.errors`): `UserNotFoundError`, `UserAlreadyExistsError`, `InvalidRoleError`, `LastAdminError`.
- **Passwords.** Hashed with argon2id (ADR-019); plaintext is never stored. `verify_password` is the only way to check a password.
- **Storage.** Use `SqliteUserRepository("sqlite:///...")` for SQLite persistence. `UserRepository` is an ABC if you need a custom/fake repository (e.g., in tests).

```python
from backend.usermanagement import SqliteUserRepository, UserCreate, UserManager

repo = SqliteUserRepository("sqlite:///./users.db")
manager = UserManager(repo, event_bus=event_bus)

user = manager.create_user(UserCreate(username="alice", email="alice@example.com", password="s3cret!x", role="member"))
manager.verify_password(user.id, "s3cret!x")
```

---

## Using the Authentication Feature

New backend features that need login, sessions, or password recovery MUST use the shared authentication feature at `src/backend/authentication/` (spec: `docs/specs/authentication.md`) instead of inventing their own auth.

- **Service entry point.** Use `AuthService` (the use-case service). Construct it with the three repository ABCs and a `UserManager` (password verification + user reads are delegated to user-management), then keyword args: `webauthn_provider`, `event_bus`, `attempt_tracker`, `session_ttl` (default 7 days), `reset_token_ttl` (default 15 minutes), `max_failed_attempts` (default 5), `lockout_duration` (default 15 minutes), `rp_id`/`rp_name`/`origin` (relying-party settings). A `None` event bus or attempt tracker uses the shared defaults.
- **Core operations.** `login(LoginRequest) -> LoginResult` (username/email + password), `session_info(token)`, `logout(token)` (idempotent no-op for an invalid token), `request_password_reset(PasswordResetRequest) -> str | None` (returns the raw token exactly once for a registered email, `None` otherwise), `complete_password_reset(PasswordResetComplete)`. Passkey: `begin_passkey_registration`/`complete_passkey_registration`, `begin_passkey_login`/`complete_passkey_login`, `list_passkeys`, `delete_passkey`. Password and passkey coexist — a user can log in with either.
- **Sessions.** Server-side, opaque 256-bit URL-safe tokens; only the SHA-256 hash is stored. A password change or completed reset revokes all existing sessions.
- **Throttling.** Brute-force lockout via the `AttemptTracker` (default `InMemoryAttemptTracker`); a locked identifier is rejected even with a correct password.
- **Events.** Mutations publish `LoginSucceeded`/`LoginFailed`/`Logout`/`PasswordResetRequested`/`PasswordResetCompleted`/`PasskeyRegistered`/`PasskeyDeleted` to the publisher (best-effort; a publisher failure never breaks the operation).
- **Errors.** Exceptions are the `AuthenticationError` hierarchy (from `backend.authentication.errors`): `InvalidCredentialsError`, `InvalidSessionError`, `InvalidResetTokenError`, `PasskeyCredentialNotFoundError`, `InvalidPasskeyResponseError`, `PasskeyHijackError`.
- **Passkey provider.** Use `PyWebAuthnProvider` (real `py-webauthn`) for production; the `WebAuthnProvider` ABC is the seam for a fake in tests.
- **Storage.** Use `SqliteSessionRepository`/`SqlitePasswordResetRepository`/`SqliteWebAuthnCredentialRepository` (same SQLite database as user-management). The repository ABCs are the seam for custom/fake storage.
- **Tracing.** The class is traced via `@logged_class` (shared logging feature); `include_args` stays `False` so passwords and tokens never appear in log records.

```python
from backend.authentication import (
    AuthService, PyWebAuthnProvider, SqlitePasswordResetRepository,
    SqliteSessionRepository, SqliteWebAuthnCredentialRepository,
)
from backend.usermanagement import SqliteUserRepository, UserManager

user_repo = SqliteUserRepository("sqlite:///./app.db")
user_manager = UserManager(user_repo, event_bus=event_bus)
service = AuthService(
    SqliteSessionRepository("sqlite:///./app.db"),
    SqlitePasswordResetRepository("sqlite:///./app.db"),
    SqliteWebAuthnCredentialRepository("sqlite:///./app.db"),
    user_manager,
    event_bus=event_bus,
)
result = service.login(LoginRequest(identifier="alice", password="s3cret!x"))
```

---

## Dependencies and Existing Packages

Prefer established, well-maintained packages over custom implementations when a package materially solves the problem and fits the project's requirements, architecture, licensing, and operational constraints.

Do not implement functionality from scratch when a suitable, established package already exists.

When considering a dependency, evaluate:
- Does it solve the actual problem?
- Is it actively maintained?
- Is its API and behavior appropriate for the specification?
- Is the dependency reasonably lightweight?
- Is its license compatible with the project?
- Does it introduce undesirable security, operational, or architectural risk?
- Is the dependency sufficiently mature for the required use case?

Prefer an established package when it provides meaningful value over a custom implementation.

Do not add dependencies merely for convenience when a small, clear implementation is more appropriate.

Dependency decisions must be traceable to the feature or architectural decision that motivated them. Record the decision in an ADR.

Especially strong for: cryptography, password hashing, authentication protocols, parsing complex formats, database drivers, HTTP clients, OAuth/OIDC, serialization formats, timezone handling, validation, cryptographic randomness.

"Not invented here" is not a reason to reject a dependency. The question is whether the dependency is the better engineering choice.

---

## Spec Amendment Workflow

When an approved spec must change after implementation has started:

1. **Open a new PR** for the spec change. Do not edit the spec file on `main` directly.
2. **Version the spec file** by appending a changelog entry at the top of the spec:
   ```
   ## Changelog
   - v2 (2026-08-16): REQ-003 amended — response now includes `request_id`.
   ```
3. **Identify affected tasks** — any task whose `requirements` or `acceptance_criteria` reference the changed IDs.
4. **Re-run RED/GREEN** for affected tasks: re-derive tests from the amended spec, confirm RED, implement, confirm GREEN.
5. **Update the traceability matrix** with the amended IDs and new test references.
6. **Merge the spec PR** before resuming implementation on affected tasks.

An agent MUST NOT modify an approved spec without going through this workflow. Direct edits to `docs/specs/` on `main` are rejected.

---

## Emergency / Fast-Path Exception
The spec-and-task workflow is bypassed **ONLY** for:
- Changes that do not alter observable behavior and touch ≤ 2 lines (typos, docstring fixes, comment edits).
- One-line bug fixes with an existing, failing test already in place.
- Direct user commands explicitly containing the keyword `--skip-spec`.

The boundary is concrete: if the change alters externally observable behavior, the full workflow for the change's type applies regardless of how small the change appears.
## Spec Approval Gate (GitHub Review)
A specification file `docs/specs/[name].md` is considered **HUMAN APPROVED** if and only if it has been merged through the repository's configured GitHub review process. This gate applies to FEATURE and CROSS-CUTTING changes (the only types that produce a spec).

Before starting Phase 2, verify approval via:
`git log main -- docs/specs/[name].md`

- Output is empty: **STOP.** Prompt user to merge spec PR first.
- Commit logs appear: Verify the commit was introduced by a merged PR (not a direct push to `main`). **PROCEED** only if the spec was reviewed.

**Direct commits to `main` do NOT constitute approval.** The spec must go through GitHub PR review to maintain the boundary: human controls WHAT, agent controls HOW.

## Project Structure
The project is organized around a single `src/` package, with `frontend` and `backend` as the primary runtime boundaries inside it.

```text
project/
├── docs/
│   ├── specs/
│   └── decisions/
│
├── src/
│   ├── main.py
│   ├── frontend/
│   │   ├── <feature>/
│   │   │   ├── model/
│   │   │   ├── services/
│   │   │   └── ...
│   │   └── shared/
│   └── backend/
│       ├── <feature>/
│       │   ├── model/
│       │   ├── services/
│       │   └── ...
│       └── shared/
│
└── tests/
    └── acceptance/
        └── <feature>/
```

### Principles

* **Features are the primary architectural boundary.** Code belonging to a feature should live together rather than being split into global `models`, `services`, or `repositories` directories.
* **Frontend and backend are separate runtime boundaries inside `src/`.** A feature may have both a frontend and backend implementation, but each side owns its respective concerns.
* **`model` contains domain concepts and business rules.** It should not contain infrastructure concerns.
* **`services` contains use cases and orchestration.** Services coordinate models and external dependencies to implement a specific behavior.
* **Do not create layers or directories prematurely.** `model/` and `services/` are architectural roles, not mandatory folders. Small features may use simple modules and should be split only when complexity justifies it.
* **Features should expose explicit public interfaces.** Other features should depend on those interfaces rather than importing internal implementation details.
* **`shared/` is deliberately small.** Code belongs there only when it is genuinely shared by multiple features and contains no feature-specific business logic.
* **Avoid unnecessary abstractions.** Repositories, factories, adapters, and similar patterns should be introduced when a specification or design requires them, not because the template prescribes them.
* **Specifications, tests, and implementation should use the same feature vocabulary.** A feature should be traceable from its specification through acceptance tests to its frontend and/or backend implementation.

The architectural goal is:

```text
Specification
     │
     ▼
   Feature
   ┌───┴───┐
   ▼       ▼
Frontend Backend
   │       │
   └───┬───┘
       ▼
 Acceptance Tests
```

**Architecture should emerge from the requirements and tests rather than from the template.**

