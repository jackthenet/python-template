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

## Ponytail, lazy senior dev mode

You are a lazy senior developer. Lazy means efficient, not careless. The best code is the code never written.

Before writing any code, stop at the first rung that holds:

1. Does this need to be built at all? (YAGNI)
2. Does it already exist in this codebase? Reuse the helper, util, or pattern that's already here, don't re-write it.
3. Does the standard library already do this? Use it.
4. Does a native platform feature cover it? Use it.
5. Does an already-installed dependency solve it? Use it.
6. Can this be one line? Make it one line.
7. Only then: write the minimum code that works.

The ladder runs after you understand the problem, not instead of it: read the task and the code it touches, trace the real flow end to end, then climb.

Bug fix = root cause, not symptom: a report names a symptom. Grep every caller of the function you touch and fix the shared function once — one guard there is a smaller diff than one per caller, and patching only the path the ticket names leaves a sibling caller still broken.

Rules:

- No abstractions that weren't explicitly requested.
- No new dependency if it can be avoided.
- No boilerplate nobody asked for.
- Deletion over addition. Boring over clever. Fewest files possible.
- Shortest working diff wins, but only once you understand the problem. The smallest change in the wrong place isn't lazy, it's a second bug.
- Question complex requests: "Do you actually need X, or does Y cover it?"
- Pick the edge-case-correct option when two stdlib approaches are the same size, lazy means less code, not the flimsier algorithm.
- Mark deliberate simplifications that cut a real corner with a known ceiling (global lock, O(n²) scan, naive heuristic) with a `ponytail:` comment naming the ceiling and upgrade path.

Not lazy about: understanding the problem (read it fully and trace the real flow before picking a rung, a small diff you don't understand is just laziness dressed up as efficiency), input validation at trust boundaries, error handling that prevents data loss, security, accessibility, the calibration real hardware needs (the platform is never the spec ideal, a clock drifts, a sensor reads off), anything explicitly requested. Lazy code without its check is unfinished: non-trivial logic leaves ONE runnable check behind, the smallest thing that fails if the logic breaks (an assert-based demo/self-check or one small test file; no frameworks, no fixtures). Trivial one-liners need no test.

---

## Tooling & Execution Environment
This repository utilizes modern Python tooling managed via `uv`:
- **Package Manager:** `uv` (Use `uv run <command>` for isolated execution)
- **Quality Assurance & Formatting:** `ruff` (`uv run ruff check .` / `uv run ruff format .`). **Scope split:** per-task steps (S3.2, S4.3, S4.4) lint only the step's changed paths (`uv run ruff check <changed-paths>`); the whole-repo sweep (`uv run ruff check .`) runs **once at Phase 5** (verify), matching CI (`.github/workflows/lint.yml`) exactly — pre-existing lint errors are in scope, not out of scope. Ruff's built-in content-hash cache (`.ruff_cache`) makes re-runs over unchanged files cheap.
- **Type Checking:** `mypy` (`uv run mypy src/` / `uv run mypy scripts/`) — the gate; `ty` (`uv run ty check src/`) is the fast local/LSP tool. mypy runs on `src/` (the import closure needs the whole package); its built-in cache (`.mypy_cache`) is keyed on file hashes, so unchanged files are not re-checked.
- **Test Runner:** `pytest` (`uv run pytest`)
- **Property Testing:** `hypothesis` (`uv run pytest tests/property/`)
- **Standard Verification:** `uv run pytest tests/`
- **Version Bumping:** `bump-my-version` (`uv tool install bump-my-version`; config in `pyproject.toml` under `[tool.bumpversion]`)
- **Database Migrations:** `alembic` (`uv run alembic upgrade head` / `uv run alembic revision -m "<description>"`) — schema migrations for the SQLModel tables; the scaffold (`alembic.ini` + `migrations/`) is wired to `SQLModel.metadata` (see "Using Migrations (alembic)").
- **Dependency Check:** `deptry` (`uv run deptry .`) — detects unused/missing/misplaced dependencies; configuration in `[tool.deptry]` (per-rule ignores for CLI/pytest-plugin tools).
- **Documentation Site:** `mkdocs` + `mkdocs-material` + `mkdocstrings[python]` (`uv run --group docs mkdocs build --strict`) — published docs generated from `userdocs/` (never `docs/` — that is the internal process record).
- **Test Tooling:** `polyfactory` (factories for Pydantic/SQLModel models), `respx` (httpx mocking), `time-machine` (time travel) — see "Using the Test Tooling".
- **Structure Map:** `STRUCTURE.md` (repository root) is the generated map of the repository — generate it with `uv run python scripts/make_map.py`, check it with `uv run python scripts/make_map.py --check`; regenerate it in the same commit as the `.py` change, and on a merge conflict in it take either side and regenerate (never hand-merge the generated file). How-to skill: `code-structure-map`.

**MkDocs site note.** Published docs live in `userdocs/` (binding decision Q-64; never `docs/` — that is the internal process record: specs, decisions, verification, workflow). Build gate: `uv run --group docs mkdocs build --strict` (the docs tooling is the `docs` dependency group, not the default `dev` group; `uv sync --group docs` installs it); CI: the `docs` job in `.github/workflows/quality.yml`; pre-push: the `mkdocs-build` hook in `.pre-commit-config.yaml`.

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

### Lifecycle (mapped to Phase P and the 6 phases)

Exact commands, procedures, and edge cases for each operation live in the git skill (`.agents/skills/git/SKILL.md`).

- **Phase P (prepare)** — **P.1** writes `docs/todo/<name>.md` and `docs/questions/<name>.md` **on `main`** (planning records, see "Phase P: PREPARE"). The change branch **and its worktree** are created at **P.4** from `main` (git skill: "Create change worktree"), so the branch carries the TODO file and the answered questions.
- **Phase 1 (S1.4)** — S1.4 only: commit the prepared spec in the change worktree and open the approval PR. All work from **P.4** through Phase 6 is performed inside the change worktree (P.1–P.3 write the planning records on `main`).
- **Phases 2–5** — decompose, test, implement, verify: all commands (`uv run ...`) run inside the change worktree. The primary worktree (`main`) is used for:
  - the planning-record commits and `Status:` advances (`docs/todo/`, `docs/questions/`),
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
- `.ruff_cache` and `.mypy_cache` are per-worktree by default (each is created in the worktree's CWD and is gitignored), so the cheap-re-run benefit does not carry across worktrees — a new change starts with a cold cache. To share them, point both tools' cache dirs at a common location outside the worktrees (ruff: `RUFF_CACHE_DIR`; mypy: `MYPY_CACHE_DIR`).
- `git worktree remove` fails on a dirty worktree: do NOT use `--force` on an unmerged change. Force-removal is only permitted when the changes are intentionally discarded.
- If a worktree directory was deleted manually, run `git worktree prune`.
- Check for leftovers with `git worktree list`; after cleanup, the only worktree should be the primary (`main`).
- **Direct-to-`main` commits are allowed only for the planning records** under `docs/todo/` and `docs/questions/` — their creation at P.1–P.3 **and every later `Status:` advance through `MERGED` and `DROPPED`, and the archive move of the two records** (see "Planning records (owner: the orchestrator)"). Nothing else — no spec, no verification record, no source, no test — may be committed directly to `main`; it reaches `main` only through a merged PR.

---

## Phase P: PREPARE — Front-Loaded Human Interaction

All **scheduled** human interaction happens **before** the workflow runs. Phase P turns each change idea into a **prepared change**: a TODO file, a fully answered question file, and — for FEATURE/CROSS-CUTTING — a self-consistent draft specification. The normal workflow (Phases 1–6) then runs **autonomously**: the human actions that remain are merging the spec PR (S1.4) and the change PR (S6.4), plus any **late** question a step raises. None of them stops the agent — a late question puts the change in WAITING and the agent switches to another prepared change (see "Multi-change scheduling (never idle)").

### Preparation artifacts (per change)

| Artifact | Created at | Committed to |
|---|---|---|
| `docs/todo/<name>.md` (from `docs/todo/template.md`) | P.1 | `main` (→ `docs/todo/archive/<name>.md` once `DROPPED`/`MERGED`) |
| `docs/questions/<name>.md` (from `docs/questions/template.md`) | P.1, answered at P.3 | `main` (→ `docs/questions/archive/<name>.md` once `DROPPED`/`MERGED`) |
| `docs/specs/<name>.md` — draft spec | P.4, fixed at P.5 | the change branch |
| `docs/verification/<name>.md` — type + triage / baseline / scope | P.4 | the change branch |

`docs/todo/` and `docs/questions/` are **planning records, not normative**: they carry no approval gate and are the **only** files the workflow may commit directly to `main` (the backlog and the Q&A must be browsable in one place). Everything normative — `docs/specs/`, `docs/verification/`, `src/`, `tests/` — is written in the change worktree and reaches `main` only through a merged PR. The **Spec Approval Gate is unchanged**.

### Phase P atomic steps

| Step | Owner | Objective | Done when |
|---|---|---|---|
| **P.1 Frame** | orchestrator | classify the change type (Phase 0); create the TODO file and the question file from their templates; create the change's todo set; **value-triage the TODO** (existing overlap, beneficiary, 1–5 score, recommendation — see "Backlog value triage") | both files exist on `main`; the orchestrator sets TODO `Status: PREPARING`; the TODO's `## Value triage` section is filled in (the user's decision is recorded **before P.4**) |
| **P.2 Interrogate** | subagent (specify skill) | adversarially interrogate the idea; record every question in `docs/questions/<name>.md` | ≥ 20 questions (FEATURE/CROSS-CUTTING) recorded in **one** `BLOCKED-USER` batch; overlap checked against `docs/specs/` **and** every TODO in `docs/todo/` |
| **P.3 Answer** | orchestrator ⏸ | present the batch (≤ 4 per `ask_user_question` round, most blocking first) and record the answers | every question `ANSWERED` + incorporated; the orchestrator sets TODO `Status: QUESTIONS-ANSWERED` |
| **P.4 Draft** | subagent (specify skill) | create the change branch + worktree from `main` (so the branch carries the TODO and the answers), then write the type's Phase 1 output: draft spec (FEATURE/CROSS-CUTTING), triage (ISSUE), GREEN baseline (REFACTOR), scope (DOCS/CHORE) | the artifact exists in the worktree and is committed |
| **P.5 Verify self-consistency** | subagent (specify skill) — **FEATURE/CROSS-CUTTING only** | run the Self-Consistency Checklist + the Dependency Smoke-Test against the draft specification; fix the specification itself | the specification passes the Self-Consistency Checklist and the Dependency Smoke-Test; the orchestrator sets the TODO `Status: READY` |

**Prep gate ◆ READY.** A change is **READY** when its TODO file says `Status: READY`, **every** question in its question file is `ANSWERED`, and the P.4 artifact exists. Only a READY change may enter the normal workflow.

### Planning records (owner: the orchestrator)

`docs/todo/<name>.md` and `docs/questions/<name>.md` are **orchestrator-owned records that live only on `main`**. Both paths are written **only in the primary worktree**: P.1–P.3 and every `Status:` advance by the **orchestrator** — which commits each change directly to `main` (git skill: "Commit planning artifacts and status advances (orchestrator, `main`)") — and **P.2 by its step subagent** (which runs in the primary worktree because no change worktree exists yet, and writes only the question file). **No write to them may happen inside a change worktree**, and a change branch and its PR therefore never contain them — because the branch does not modify those paths, a later direct-to-`main` status update is never reverted by the merge. The orchestrator also **moves** the two files **together** — `docs/todo/<name>.md` → `docs/todo/archive/<name>.md` and `docs/questions/<name>.md` → `docs/questions/archive/<name>.md` — at the **drop** decision and at **post-merge cleanup (S7.1)**; the question file always moves with its TODO file, and the move is itself a direct-to-`main` planning-record commit. `docs/questions/archive-AI_Questions.md` (the retired central file) is unrelated to the new folder and stays where it is.

The orchestrator advances the TODO `Status:` on `main` at each of these moments, and commits each advance:

| When | Status |
|---|---|
| P.1 Frame | `PREPARING` |
| after P.3 Answer (every question `ANSWERED`) | `QUESTIONS-ANSWERED` |
| after the P.5 handoff is verified (**FEATURE/CROSS-CUTTING**) or after the P.4 artifact is verified (**ISSUE / REFACTOR / DOCS/CHORE**) | `READY` |
| when the change enters the normal workflow (S1.4 / Phase 3 / Phase 4) | `IN-WORKFLOW` |
| when the change reaches a human gate (`S1.4` approval, `S6.4` merge, `BLOCKED-USER`, `BLOCKED-HUMAN`) | `WAITING` |
| after post-merge cleanup (the two records then move to `docs/todo/archive/` and `docs/questions/archive/`) | `MERGED` |
| when the user's value-triage decision is **drop** (the two records then move to `docs/todo/archive/` and `docs/questions/archive/`) | `DROPPED` |

Step subagents never write the `Status:` field: they report the gate in their handoff and the orchestrator records it. A **late mid-workflow question** is returned in the step's handoff (`questions` field); the orchestrator appends it to the change's question file **on `main`** — a step subagent must not edit `docs/questions/` after P.4.

### Phase P outputs per change type

| Type | Phase P output | Normal workflow starts at |
|---|---|---|
| FEATURE / CROSS-CUTTING | TODO + answered questions + self-consistent draft spec | **S1.4** Present for approval (spec PR → human merge) → Phase 2 |
| ISSUE | TODO + answered questions + triage record (affected REQ/AC, defect confirmation, reproduction plan) | **Phase 3** (reproduction test → RED) |
| REFACTOR | TODO + answered questions + GREEN baseline + refactor scope | **Phase 4** |
| DOCS/CHORE | TODO + answered questions + no-behavior scope | **Phase 4** |

The former specification steps **S1.1 / S1.2 / S1.3** are now **P.2 / P.4 / P.5** (FEATURE/CROSS-CUTTING) — same content, run during preparation. **S1.4** keeps its number and stays in the normal workflow.

### Preparing many changes

Prepare as many changes as you like before starting the workflow — preparation is what makes the workflow parallel. A prepared change costs nothing while it waits: its TODO, Q&A and draft spec are on disk and its worktree exists, but no phase runs for it until it is picked up.

### Backlog value triage

Before implementing any TODO, decide whether it is worth doing. At **P.1 Frame** the orchestrator fills in the TODO's `## Value triage` section: **(1)** check the codebase for existing functionality that covers it and name the file/function — if it overlaps, propose extending that feature instead of building a new one; **(2)** identify who benefits and how (the end user of this project), and say so instead of guessing when the value is unclear or the TODO is too vague to judge; **(3)** score it **1–5** (`5` = clear user value, new, small change · `3` = some value, or partly overlapping, or moderate effort · `1` = no clear value, duplicate, or large/risky change) with one sentence explaining the score; **(4)** recommend **implement / merge into <existing feature> / drop**. Present the results as a table (`ID | TODO | score | recommendation | reason`) and ask the user which to implement, merge, or drop: over a backlog sweep that is **one triage batch**, presented in as few rounds as possible (≤ 4 per round, most blocking first); a single TODO framed outside a sweep gets its ask **immediately**, as a one-row table riding that change's existing P.3 round-trip — no extra ⏸. The ask and the decision are recorded **only in the TODO's `## Value triage` section**, never as a question-file entry. **No TODO may pass P.4 (create its branch and worktree) until its own value-triage decision is recorded**; already-decided and READY changes keep running, so "never idle" is unaffected. Prefer reusing existing code and the smallest diff that delivers the value — dropping a low-value or duplicate TODO is a good outcome. The code-level counterpart is the "Ponytail, lazy senior dev mode" ladder (rungs 1–2), which this rule cross-references instead of restating. A dropped TODO gets `Status: DROPPED` and its two records move to the archive folders (see "Planning records (owner: the orchestrator)").

---

## The Spec-TDD Workflow Protocol (Change-Type Routed)

Every change in this repository is one of five **change types**. The type determines which phases run, what each phase produces, and which gates apply. **Phase P (PREPARE) is the single entry point for all types**: it classifies the change first (Phase 0, at **P.1**), then produces the type's Phase 1 output during preparation. The normal workflow starts at **S1.4** (FEATURE/CROSS-CUTTING), **Phase 3** (ISSUE), or **Phase 4** (REFACTOR, DOCS/CHORE).

### Change Types & Classification (Phase 0)

Classify the change at **P.1 Frame** — before any other work (specify skill, Phase P). Use the **first matching criterion, in this order**:

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
| **P Prepare** | Adversarial interrogation → TODO + answered questions + draft spec (REQ/AC/INV/EDGE/NFR) | TODO + answered questions + **Triage**: affected REQ/AC from existing specs, defect confirmation, reproduction plan. No spec. | Adversarial interrogation → TODO + answered questions + draft spec **with per-feature impact analysis** | TODO + answered questions + **Baseline**: full suite GREEN + refactor scope. No spec. | TODO + answered questions + **Scope**: exact non-behavior changes; confirm no behavior delta. No spec. |
| **1 Specify** | S1.4 only: commit the prepared spec → **PR approval** | — (done in Phase P) | S1.4 only: commit the prepared spec → **PR approval** | — (done in Phase P) | — (done in Phase P) |
| **2 Decompose** | ADRs + task DAG | — (skip; the triage is the plan) | ADRs + task DAG **grouped by affected feature** | — (skip) | — (skip) |
| **3 Test & RED** | Tests derived from spec → RED | **Reproduction test** → RED | Tests derived from spec → RED | — (skip; existing tests are the contract) | — (skip) |
| **4 Implement** | GREEN from DAG + refactor | **Minimal fix** → GREEN | GREEN from DAG + refactor | Behavior-preserving steps; suite stays GREEN | Make the change |
| **5 Verify** | Full gate set | Targeted tests + full regression + lint/types | Full gate set **+ per-feature traceability updates** | Full regression + architecture rules (manual, Phase 6 checks 3–4) + lint/types (no spec coverage) | Light: lint/types where applicable |
| **6 Review** | Full review → PR → merge → cleanup | Full review → PR → merge → cleanup | Full review → PR → merge → cleanup | Full review (**tests not weakened**) → PR → merge → cleanup | Light review → PR → merge → cleanup |

"Full gate set" = the Phase 5 FEATURE checks below. Every type ends with a PR to `main` for human review/merge (human governance). Every Phase P output in the row above presupposes a recorded **Value triage** decision for that TODO (see "Backlog value triage"); a TODO whose decision is not recorded may not reach P.4.

### Workflow Diagram (atomic steps, dependencies, ownership, validation / user input)

Legend: **[O]** = orchestrator (no subagent) · **[S]** = step subagent (**synchronous, never background**) · **◆** = gate (validation) · **⏸** = user input (the **change** stops until answered) · **P.x** steps run during preparation (Phase P), before the workflow

```text
PHASE P   PREPARE (per change, before the workflow — all scheduled human input here)
  P.1    [O] Frame: classify + docs/todo/<name>.md + docs/questions/<name>.md (on main) + todo set
             │
             ▼
  P.2    [S] Interrogate (specify skill) ──► docs/questions/<name>.md ──⏸──► BLOCKED-USER
             │
             ▼
  P.3    [O] Answer ⏸ ──► answers recorded in docs/questions/<name>.md ◆
             │
             ▼
  P.4    [S] Create worktree + draft spec / triage / baseline / scope
             │
             ▼
  P.5    [S] Verify self-consistency (FEATURE/CROSS-CUTTING only) ◆ ──► READY ◆
             │
             ▼
PHASE 1   [S] SPECIFY (specify skill)
  S1.4   Present for approval ──► PR ──⏸──► HUMAN APPROVAL ◆
             │
             ▼
PHASE 2   [S] DECOMPOSE (decompose skill)
  S2.1   Create ADRs
             │
             ▼
  S2.2   Decompose into task DAG ──► .github/task-runner/tasks.json ◆
             │
             ▼
PHASE 3   [S] TEST & RED (test skill)
  S3.1   Derive tests (per task in the DAG)
             │
             ▼
  S3.2   Ruff ◆ + confirm RED ◆ (tests FAIL on behavior)
             │
             ▼
PHASE 4   [S] IMPLEMENT (implement skill)     [repeat per task in the DAG]
  S4.1   Pick task + confirm RED
             │
             ▼
  S4.2   Implement + confirm GREEN ◆
             │
             ▼
  S4.3   Ruff ◆
             │
             ▼
  S4.4   Refactor (keep GREEN)
             │
             ▼
  S4.5   Commit + update status (VERIFIED)
             │
             ▼
PHASE 5   [S] VERIFY (verify skill)
  S5.1   Run full test suite ◆
             │
             ▼
  S5.2   Lint + types ◆
             │
             ▼
  S5.3   Update traceability
             │
             ▼
  S5.4   Verification report (spec coverage = 100%) ◆
             │
             ▼
PHASE 6   [S] REVIEW (review skill)
  S6.1   Review vs. normative basis
             │
             ▼
  S6.2   Traceability + boundaries
             │
             ▼
  S6.3   Review report (clean) ◆
             │
             ▼
  S6.4   Bump version + open PR ──► PR ──⏸──► HUMAN MERGE ◆
             │
             ▼
POST-MERGE [S] CLEANUP (git skill)
  S7.1   Verify merge + remove worktree + delete branches ◆
```

- **Dependencies:** steps run in order within a phase; a phase runs only after the previous phase's gate ◆ passes. A failed gate re-enters the same or an earlier step with a **new** subagent.
- **Ownership:** Phase P's **P.1 Frame** and **P.3 Answer** are the orchestrator; every other step is a dedicated, **synchronous** subagent (one atomic step each).
- **User input (⏸):** the user is needed at **P.2/P.3** (questions → `docs/questions/<name>.md`), **S1.4** (spec approval) and **S6.4** (PR merge). A change never proceeds past a ⏸ until the user answers.
- **Non-blocking:** a change that reaches a ⏸ gate goes **WAITING** and the orchestrator immediately works on another READY change (see "Multi-change scheduling (never idle)") — the workflow never idles.
- **Friction (Problem Log):** any step that fails / is relaunched / iterates / blocks is recorded in `docs/workflow/PROBLEMS.md`.

### Skill-to-Phase Mapping

| Phase | Skill | Applies to | Purpose |
|-------|-------|------------|---------|
| Phase P: PREPARE | `specify` | all | Turns an idea into a prepared change: TODO file, interrogation, answered questions, draft spec / triage / baseline / scope. |
| Phase 1: SPECIFY (approve only) | `specify` | FEATURE, CROSS-CUTTING | S1.4 only: commit the prepared spec and open the approval PR (other types' Phase 1 output is produced in Phase P). |
| Phase 2: DECOMPOSE | `decompose` | FEATURE, CROSS-CUTTING | Creates ADRs and decomposes the spec into a machine-readable JSON task DAG (per-feature grouping for CROSS-CUTTING). |
| Phase 3: TEST & RED | `test` | FEATURE, CROSS-CUTTING, ISSUE | Derives tests from the spec (FEATURE/CROSS-CUTTING) or writes the reproduction test (ISSUE), and confirms RED state. |
| Phase 4: IMPLEMENT | `implement` | all | Turns RED into GREEN (or performs behavior-preserving steps / makes the chore change), then refactors without changing specified behavior. |
| Phase 5: VERIFY | `verify` | all | Produces evidence that the change satisfies its type-specific gates. |
| Phase 6: REVIEW | `review` | all | Reviews the change against its type-specific criteria before reviewing implementation style. |
| (cross-cutting) | `git` | all | Branch/worktree creation, PR creation, post-merge cleanup. |
| (ambient) | `code-structure-map` | all | Optional, before exploring: read the generated `STRUCTURE.md` map instead of walking the tree, and regenerate it with the change. |
| (ambient) | `python-best-practices` | all | Conventions and vetted good-code examples for writing, reviewing or refactoring Python. |

Non-phase skills: `.agents/skills/update-readme/` (refresh `README.md` to current GitHub front-page practice, badges backed only by facts that exist) maps to no workflow phase.

### Phase Execution (Atomic Steps, Synchronous Subagents)

Every workflow step is executed by a **new subagent** launched via the `subagent` tool (type `general-purpose`). The orchestrating agent (the agent talking to the user) **never executes a step itself** — it only orchestrates. A step subagent executes **exactly one atomic step** and returns.

#### Execution Model

- **Synchronous — never background.** Every subagent is launched with `run_in_background: false` (the default). The orchestrator **waits for the subagent to complete its step and return a handoff** before proceeding to the next step. A subagent is never left running in the background and is never polled. If a subagent does not return (timeout / network / error), the orchestrator treats it as a **failed step**: it logs the problem (Problem Log), launches a **fresh** subagent for the same step (never resumes a stuck one), and continues. A step subagent MUST end with the **structured handoff**; a step that returns without it (e.g., ends with an intermediate statement) is treated as a **FAILED step** and relaunched with a fresh subagent (completion guard, P-3/P-7). The synchronous model applies **per step**; the orchestrator interleaves **changes** (see "Multi-change scheduling (never idle)"), so a human gate on one change never idles the agent.
- **Atomic steps.** Each phase is broken into **atomic steps** (table below). An atomic step has a **single objective**, clear **inputs/outputs**, a **required skill**, a **dedicated subagent**, a clear **“done” definition**, and a **validation** before the next step. A step subagent executes **exactly one atomic step** — never more. Small steps exist so a subagent can actually **finish** its work.
- **One subagent per atomic step.** Every time an atomic step is (re-)entered — including re-entry after a failed gate (Phase 5 → Phase 4/3) and reclassification re-runs — the orchestrator launches a **new** subagent. A `BLOCKED-USER` step is re-entered with a **fresh** subagent; the orchestrator includes the user's recorded answers in the new launch prompt. The orchestrator **NEVER** resumes/restores a previously launched subagent session (its context is full/stale) — every (re-)entry, including after BLOCKED-USER, after a failed gate, and after reclassification, launches a **new** subagent.
- **In-step fix-and-recheck (trivial self-introduced issues).** The fresh-subagent rule governs step **re-entries**, not internal retries. A step subagent that hits a **trivial, self-introduced** issue while finishing its step (a single lint violation, a formatting nit, a missed import) MUST fix it and re-check **within the same execution**, then return one handoff — it does NOT return `FAILED` for a nit it can fix itself. `FAILED` (which triggers a fresh-subagent relaunch) is reserved for substantive failures: done-criteria genuinely not met, missing context, or a block the subagent cannot resolve on its own.
- **Naming.** The orchestrator names each step subagent's description `Sx.x: <short objective>` (e.g., `S4.2: implement FileService.upload`), or `Px.x: <short objective>` for a Phase P step (e.g., `P.2: interrogate the settings-coverage idea`); for per-task steps it includes the task ID (e.g., `S4.2 (T-005): implement FileService.upload`).

#### Atomic Steps

Phase P plus the six phases are the **gates** (entry/exit criteria per the Phase Matrix). Within each phase, the work is done in atomic steps; **each atomic step is one subagent execution**. Phase P's **P.1 Frame** and **P.3 Answer** stay on the **orchestrator** (the worktree is created at P.4).

| Phase | Atomic steps (one subagent each, in order) |
|-------|-------------------------------------------|
| **P Prepare** | **P.1 Frame** (orchestrator) → **P.2 Interrogate** → **P.3 Answer** (orchestrator ⏸) → **P.4 Draft** → **P.5 Verify self-consistency** (FEATURE/CROSS-CUTTING only) ◆ READY |
| **1 Specify** | **S1.4 Present for approval** (commit + PR) |
| **2 Decompose** | **S2.1 Create ADRs** → **S2.2 Decompose into task DAG** |
| **3 Test & RED** | **S3.1 Derive tests (per task: one fresh subagent derives one DAG task's `tests_to_create`)** → **S3.2 Ruff + confirm RED** |
| **4 Implement** | **S4.1 Pick task + confirm RED** → **S4.2 Implement + confirm GREEN** (ruff gate) → **S4.3 Refactor** (keep GREEN; ruff gate; no-op fast-path) → **S4.4 Commit + update status** |
| **5 Verify** | **S5.1 Run full test suite** → **S5.2 Lint + types** → **S5.3 Update traceability** → **S5.4 Verification report** |
| **6 Review** | **S6.1 Review vs. normative basis** → **S6.2 Traceability + boundaries** → **S6.3 Review report** → **S6.4 Bump version + open PR** |
| **Post-merge** | **S7.1 Cleanup** (verify merge + remove worktree + delete branches) |

**Ruff gate.** Every atomic step that writes or modifies **tests or implementation code** MUST run ruff on the **step's changed paths** (`uv run ruff check <changed-paths>`) before it returns and record the result in the handoff (`ruff` field). A step that leaves lint errors is **not done**. The **whole-repo** sweep (`uv run ruff check .`) is a **Phase 5** gate (verify) — per-task steps do NOT run it implicitly. Scope `uv run ruff check --fix` + `uv run ruff format` to the **task's changed paths** (not repo-wide) — repo-wide `--fix`/`format` during a task step modifies out-of-scope files and can introduce new errors (P-6); a repo-wide lint fix is a separate, explicit step (or the verify phase). There is **no separate ruff step** — the ruff gate is part of the step that writes the code (S4.2 implement, S4.3 refactor); a dedicated ruff subagent launch is redundant overhead (the old S4.3 ruff step was removed in the after-workflow-optimization).

#### Task-Definition Contract

The orchestrator's launch prompt for an atomic step MUST contain **exactly** what the step needs — the subagent must never have to infer it:
- the **step ID** (e.g., `S4.2`) and its **single objective**;
- the **change name and type**;
- the **change worktree path** (all commands run there; **P.1–P.3** run in the **primary worktree** — no change worktree exists until P.4);
- the **skill file** to read (`.agents/skills/<skill>/SKILL.md`) **and the specific skill section** that applies to this step;
- the **inputs** — the prior step's handoff (status, gate result, artifacts, evidence location, and any user answers);
- the **done criteria** (the step's validation, e.g., “GREEN confirmed and recorded in `docs/verification/<name>.md`”);
- the **required handoff output** (below).

#### Roles

- **Orchestrator** — performs Phase 0 **at P.1** (classify the change type, create `docs/todo/<name>.md` and `docs/questions/<name>.md` on `main`, create the change's todo set) and runs **P.3** (present the question batch, record the answers); launches one subagent per atomic step (**synchronously**); **waits** for each handoff; **schedules across changes** — when one change is WAITING it picks the next READY change (see "Multi-change scheduling (never idle)"); presents user questions and approval requests to the user; manages the todo list; verifies each step's handoff; logs problems (Problem Log). **The orchestrator does NOT execute a step, investigate a failure, or make an implementation decision.** When a step is blocked or fails, the orchestrator supplies more context (or the user's answer) and **relaunches the same step** — it never does the work itself.
- **Step subagent** — reads its skill file and executes **exactly one atomic step** inside the change worktree. It never executes another step, never launches a subagent, never talks to the user, and never runs in the background.

#### Handoff Output

The step subagent MUST end with a structured handoff:
- `step` — the step ID (e.g., `S4.2`).
- `status` — `DONE` (done-criteria met) | `BLOCKED-USER` (needs user input) | `BLOCKED-HUMAN` (needs human governance: spec approval, PR merge) | `FAILED` (done-criteria not met, with reason). A `BLOCKED-USER` or `BLOCKED-HUMAN` handoff puts **that change** in **WAITING** state: the orchestrator records it and moves on to another READY change instead of waiting.
- `gate` — the step's validation result and where the evidence is recorded (`docs/verification/<name>.md`).
- `artifacts` — the files, commits, and PRs created.
- `ruff` — the ruff result on the step's changed paths (`uv run ruff check <changed-paths>`; the whole-repo sweep is a Phase 5 gate) (for steps that write tests/implementation), or `n/a`.
- `questions` (BLOCKED-USER only) — the questions for the user (each also recorded in `docs/questions/<name>.md`).
- `problem` (optional) — a friction point to log (see Problem Log).
- `next` — the next atomic step, or `STOP`.

#### Question files (`docs/questions/<name>.md`)

Questions that need user input are recorded persistently in **one file per change** — `docs/questions/<name>.md`, created at **P.1** from `docs/questions/template.md` — so they are not lost between steps. Each entry has: the question, the generating step (step ID `P.x` / `Sx.x` + phase), why it is needed, the context at the time, the user's answer, the date/status, and whether the answer has been incorporated.

- **MAY create questions:** any step, when it meets an ambiguity, a missing requirement, or a decision that requires user input.
- **MUST create questions:** the **Interrogate** step (**P.2**) MUST create a question for every ambiguity, missing requirement, edge case, and scope boundary it identifies — the prep phase is where user input is most needed. Any step that returns `BLOCKED-USER` MUST have its questions recorded in the change's question file.
- **Late questions (Phases 2–6):** a question discovered after the change entered the normal workflow is returned in the step's handoff (`questions` field) and the **orchestrator** appends it to the **same** file on `main` under `## Late questions (Phases 2–6)`, with its `Step:` field set to the step that found it. Step subagents do not edit the question file after P.4 — `docs/questions/` is orchestrator-owned (see "Planning records (owner: the orchestrator)").
- **Batching (one round-trip per step):** a step that needs user input MUST collect **all** of its open questions into a **single** `BLOCKED-USER` batch (one set of question-file entries, one handoff) — never one round-trip per question, and never partial batches across re-entries. For **P.2**: interrogate fully first, then return the complete question batch. The orchestrator presents the batch in as few `ask_user_question` rounds as possible (≤ 4 questions per round; the most blocking questions first), records all answers in the question file, and relaunches the step **once** with the full answer set. This keeps human-response latency off the critical path of every individual question.
- **Change stop, not workflow stop:** when a step returns `BLOCKED-USER`, **that change** goes **WAITING**: the orchestrator presents the questions to the user (via `ask_user_question`), records the answers in the question file, marks them **incorporated**, and **relaunches the same step** with the answers — while it works on another READY change (see "Multi-change scheduling (never idle)"). The change never proceeds past a `BLOCKED-USER` step until the user has answered; the **workflow** does not stop. If the BLOCKED-USER subagent's session is released (resume unavailable) and the only remaining work is verifying already-recorded answers, the orchestrator may record the answers, mark the step done directly, and commit — without relaunching (P-2).
- **Central file retired.** The central repo-root question file is no longer live guidance: it is archived at `docs/questions/archive-AI_Questions.md` and MUST NOT be edited again. Historical references to it (ADRs, older verification records) are left intact.

#### Problem Log (`docs/workflow/PROBLEMS.md`)

Problems that take a lot of time (friction points) are recorded in `docs/workflow/PROBLEMS.md` so the **after-workflow-optimization** knows where the friction was. Each entry has: the problem, the step/phase, how long / how many iterations, the resolution, and the date.

- **MUST log** when a step (a) fails and is relaunched, (b) takes more than one iteration to complete, (c) is blocked on a non-trivial user decision, or (d) takes disproportionately long relative to its objective.
- **Who logs:** the orchestrator (it sees the relaunches, iterations, and blocks). A step subagent flags a problem in its handoff (`status: FAILED` with reason, or the `problem` field); the orchestrator records it.
- **Purpose:** the after-workflow-optimization (a meta-task) reads `PROBLEMS.md` to find the friction and improve the workflow.

#### Handoff Verification

The orchestrator MUST verify a handoff before marking the step's todo `completed`: the evidence exists in `docs/verification/<name>.md`, the commits exist in the worktree, and the step's done-criteria are met. A subagent's self-report is not evidence.

#### Fast Path

Emergency/fast-path exceptions (≤ 2 lines, one-line fix with an existing failing test, `--skip-spec`) bypass the workflow entirely — no phases, no subagents. A fast-path change needs **no TODO file and no question file**. (The **Light ISSUE tier** at the end of this document is the in-workflow counterpart — it shrinks Phase 5, it does not bypass the workflow.)

#### Multi-change scheduling (never idle)

- **Unbounded in flight.** Any number of changes may be in flight, each in its own worktree with its own todo set. Parallelism comes from **interleaving changes**, not from concurrent subagents — only one step subagent runs at a time (see Execution Model).
- **Never idle.** A change that reaches a human gate — S1.4 (spec approval), S6.4 (PR merge), or a mid-workflow `BLOCKED-USER` / `BLOCKED-HUMAN` — goes **WAITING**; the orchestrator immediately takes the next ready step of **another** change. It stops only when every in-flight change is WAITING **and** no prepared change is READY.
- **Ready selection order.** (1) a change whose `Depends on:` changes are already merged; (2) among ready changes, **easiest first** (see Todo Tracking Discipline); (3) tie-break **FIFO by READY date**. A `DROPPED` or `MERGED` change's records live under `docs/todo/archive/` and `docs/questions/archive/`, so the two live folders are the backlog to select from.
- **Resume.** A WAITING change's gate is cleared when its spec PR / PR merge is reachable from `origin/main` after `git fetch` (`git merge-base --is-ancestor <merge-commit> origin/main`), or when its question file shows every answer. Then launch a **fresh** subagent at its next atomic step. A change whose records have moved to `docs/todo/archive/` / `docs/questions/archive/` is finished (`MERGED`) or dead (`DROPPED`) — it is not resumed; read its question file there if its record must be checked.
- **Todo sets.** One todo set per change; at most one `in_progress` **per change**; a WAITING change's step stays `in_progress` with an `activeForm` naming the wait (e.g. "waiting for spec PR merge").
- **Backlog status on `main`.** **WAITING**, **IN-WORKFLOW**, **MERGED** and **DROPPED** are written to the change's TODO file **on `main`** by the orchestrator at those moments (see "Planning records (owner: the orchestrator)"), so the backlog on `main` is the live schedule.

### Todo Tracking Discipline (todo tool)

The agent MUST track every in-flight change with the `todo` tool. The todo list is the change's live progress record: **one item per phase** the change type runs (per the Phase Matrix, Phase P included), **linked by dependency** in phase order, with **status orders** driven by the workflow gates. Each phase is executed in **atomic steps** (see Phase Execution (Atomic Steps, Synchronous Subagents)); a phase's todo is `completed` only when **all of its atomic steps are done** and the phase's gate passes. Todo management belongs to the **orchestrator** (see Phase Execution (Atomic Steps, Synchronous Subagents)): step subagents never create, update, or read the todo list.

**One todo set per change.** With Phase P and multi-change scheduling there are several sets in the single todo list at once. Each set covers the **Phase P steps** plus the phases its type runs, linked by `blockedBy`. At most one item is `in_progress` **per change**; a **WAITING** change's step stays `in_progress` with an `activeForm` naming the wait. Sets are created at **P.1** and completed by the **Post-merge cleanup** item; a **`DROPPED`** change's set is closed by the orchestrator at the drop decision (no Post-merge cleanup item runs for it).

**Creating the todo set (P.1).** When preparing a change, create one todo item per workflow step the change type executes, in phase order, starting with the Phase P item. Give each a short imperative subject naming the phase and its key output. A step the type skips (per the Phase Matrix) gets **no** todo item.

**Task ordering (easiest first).** When a todo set contains tasks that are not dependency-locked, work them **easiest first**: the task you already have a solution for, or reach one with least effort. Early easy wins establish the scaffolding, conventions, and gate mechanics the harder tasks then reuse. Where `blockedBy` or the phase order fixes the sequence, the dependency wins — the ease ordering applies only among tasks that are ready at the same time (e.g. which DAG task to pick in Phase 4).

**Linking dependencies.** Link each step to its predecessor with `blockedBy` so the list encodes the phase order: Phase 2 blocked by Phase 1, Phase 3 blocked by Phase 2, and so on. The final **Post-merge cleanup** item is blocked by Phase 6.

**Status orders (at the right steps).**
- **Before starting a step**, the orchestrator marks its todo `in_progress` (with a present-continuous `activeForm` label, e.g. "running the RED gate") **before launching the step's subagent**. At most one step is `in_progress` **per change** (several changes may each have one).
- **Immediately when a step's type-specific gate passes**, the orchestrator marks its todo `completed` **after verifying the step's handoff** — never batch completions. A step is `completed` only when its gate is satisfied:
  - Phase P — `completed` only at the **READY** gate: TODO `Status: READY`, every question `ANSWERED`, and the type's Phase 1 output (draft spec / triage / baseline / scope) recorded.
  - Phase 1 — `completed` when the spec PR is opened (FEATURE/CROSS-CUTTING, S1.4); the other types have no Phase 1 step — their Phase 1 output is the Phase P gate.
  - Phase 2 — `completed` when the task DAG is initialized (copied to `.github/task-runner/tasks.json`).
  - Phase 3 — `completed` only when **RED is observed** and recorded.
  - Phase 4 — `completed` only when **GREEN is achieved** and recorded.
  - Phase 5 — `completed` only when the type-specific gate set passes.
  - Phase 6 — `completed` only when the review report is clean **and** the PR is open.
  - Post-merge cleanup — `in_progress` after the human merges the PR; `completed` when the worktree is removed, the local + remote branches are deleted, and the two planning records have been moved to the archive folders.

**Reclassification (Escalation Rules).** When the change type changes, re-derive the todo set for the new type (add/remove items, relink with `blockedBy`) and record the reclassification in `docs/verification/[name].md`.

**Example (FEATURE, prepared).**
```text
#1 Phase P: Prepare — TODO + questions answered + draft spec
#2 Phase 1: S1.4 — spec PR opened                   ⛓ #1
#3 Phase 2: Decompose — ADRs + task DAG             ⛓ #2
#4 Phase 3: Test & RED — tests RED                  ⛓ #3
#5 Phase 4: Implement — GREEN                       ⛓ #4
#6 Phase 5: Verify — full gate set                  ⛓ #5
#7 Phase 6: Review — clean report + PR              ⛓ #6
#8 Post-merge cleanup — verify + remove + delete    ⛓ #7
```

**Example (ISSUE, prepared)** — Phase 1 and Phase 2 are skipped, so they have no todo item:
```text
#1 Phase P: Prepare — TODO + questions answered + triage
#2 Phase 3: Repro test — RED                        ⛓ #1
#3 Phase 4: Minimal fix — GREEN                     ⛓ #2
#4 Phase 5: Verify — regression + lint/types        ⛓ #3
#5 Phase 6: Review — clean report + PR              ⛓ #4
#6 Post-merge cleanup — verify + remove + delete    ⛓ #5
```

### Phase P + Phase 1: PREPARE & SPECIFY
Single entry point for all change types (specify skill). The procedure below is unchanged and normative; what changed is **where each part runs**: the **Phase 0 — Classify** items run at **P.1 Frame**, the FEATURE / ISSUE / CROSS-CUTTING / REFACTOR / DOCS-CHORE items run at **P.2–P.4** (interrogate → answer → draft), with **P.5** self-consistency for **FEATURE/CROSS-CUTTING only**, and only **S1.4 Present for approval** (FEATURE/CROSS-CUTTING) runs inside the normal workflow.

**Phase 0 — Classify (all types, at P.1):**
1. Create the change branch **and its worktree** from `main` per the "Git Worktrees" section — at **P.4**, after the answers are recorded, so the branch carries the TODO file and the answered questions. Branch: `<type>/<name>` (`feature/`, `issue/`, `crosscut/`, `refactor/`, `chore/`).
2. Classify the change using the Change Types table. Record the type in the change's verification artifact (`docs/verification/[name].md`).

**FEATURE** (at **P.2–P.5**):
3. Adversarially interrogate the feature idea to discover ambiguity, hidden requirements, edge cases, and scope boundaries; capture a feature brief. The brief is an **intermediate artifact** of the interrogation — do **not** save it as a separate `.brief.md` file. Fold it into the spec (goals/overview, scope boundaries, out-of-scope, edge cases); the spec is the single kept artifact.
4. Search and read existing codebase files to understand current context and patterns.
5. Check `docs/specs/template.md` for formatting requirements.
6. Draft a complete feature spec at `docs/specs/[feature-name].md`.
7. Include exact API schemas, Pydantic models, interface signatures, and non-functional requirements.
8. Assign stable IDs to every normative requirement (`REQ-XXX`), acceptance criterion (`AC-XXX`), invariant (`INV-XXX`), edge case (`EDGE-XXX`), and NFR (`NFR-XXX`).
9. Define the test strategy mapping each AC/INV/EDGE to a test category and test function.
10. **STOP and present the spec for human approval via Git PR** — this is **S1.4**, the only item of this list that runs inside the normal workflow.

**ISSUE** (triage — no spec, no PR) (at **P.2–P.4**):
11. Identify the affected requirements (`REQ-XXX`) and acceptance criteria (`AC-XXX`) from the **existing approved specs** in `docs/specs/`; cite the spec files and IDs.
12. Confirm the defect: the observed behavior deviates from what the spec requires (cite the spec ID and state the observed vs. required behavior).
13. If the fix requires behavior the spec does not state, STOP: open a Spec Amendment PR (Spec Amendment Workflow) or reclassify as FEATURE.
14. Write the reproduction plan: the failing test(s) that reproduce the defect, the fix scope, and the files expected to change.
15. Record the triage in `docs/verification/[name].md` (type: ISSUE, affected REQ/AC, defect confirmation, reproduction plan).

**CROSS-CUTTING** (at **P.2–P.5**):
16. Adversarially interrogate the change (goals, affected features, constraints, out-of-scope, edge cases).
17. Draft the spec at `docs/specs/[name].md` with an **Impact Analysis** section: every affected feature, what changes in each, and which of their REQ/AC IDs are touched.
18. Assign stable IDs (`REQ-XXX`, `AC-XXX`, `INV-XXX`, `EDGE-XXX`, `NFR-XXX`) and define the test strategy as for FEATURE.
19. **STOP and present the spec for human approval via Git PR** — **S1.4**, inside the normal workflow.

**REFACTOR** (baseline — no spec, no PR) (at **P.2–P.4**):
20. Run the full suite (`uv run pytest tests/ -v`) and confirm it is GREEN. Record the baseline in `docs/verification/[name].md`.
21. Define the refactor scope: which code moves/renames/simplifies, and the invariants that MUST hold (no observable behavior change, no test changes).

**DOCS/CHORE** (scope — no spec, no PR) (at **P.2–P.4**):
22. Define the exact non-behavior changes (files, content) and confirm they do not alter externally observable behavior. Record the scope in `docs/verification/[name].md`.

### Phase 2: DECOMPOSE (`docs/decisions/`, `docs/tasks/`)
FEATURE and CROSS-CUTTING only. Once the specification file is merged into `main`:
1. Create ADRs in `docs/decisions/` for significant design decisions (WHY, not WHAT). **Threshold:** an ADR is required only for a decision that introduces a **new dependency**, a **new pattern/architecture element**, or a **cross-feature interface**. A small change (no new dependency, no new pattern, impact confined to one feature and a handful of files) creates **no** ADRs — S2.1 records the skip + rationale in `docs/verification/[name].md` instead (the step still runs; its output is the recorded skip).
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

Test derivation is **per task in the DAG** (S3.1): one fresh subagent derives one task's `tests_to_create`; S3.2 stays a single ruff + RED gate, run **targeted** (the newly derived tests must fail on behavior — the full suite is a Phase 5 gate, not a per-task or per-derivation run).

**FEATURE / CROSS-CUTTING** (after the task DAG is initialized):
1. Write acceptance tests derived directly from the spec's acceptance criteria.
2. Write property tests for every invariant (`INV-XXX`) using Hypothesis.
3. Write unit tests for edge cases and error conditions.
4. Write contract tests for NFR contract requirements.
5. Write integration tests for multi-component interactions.
6. **Validate test data, then run the test suite and confirm RED state.** The test fixtures/data MUST construct VALID model instances (pass the model's validation) — a test that fails with a `ValidationError`/`ValueError` when constructing test data (e.g., a username too short/long for the model's pattern) has **invalid test data, not a valid RED**; fix the test data (in-domain values) before confirming RED. Then confirm RED (tests must fail on behavior, before implementation).
7. Record RED evidence in `docs/verification/[name].md`.
8. Update the traceability matrix in `docs/verification/traceability.md` with test references.

**ISSUE** (after triage):
1. Write the reproduction test(s) from the triage plan. They MUST fail on the current (defective) code — this is RED for the issue.
2. **Run the reproduction tests and confirm RED state.**
3. Record RED evidence in `docs/verification/[name].md`.
4. Update the traceability matrix with the issue's test references (affected REQ/AC + reproduction test).
### Phase 4: IMPLEMENT
All types.

**Targeted GREEN (cost control).** `red_command` / `green_command` run **only the task's targeted tests** (the task's `tests_to_create` plus directly affected tests) — not the full suite. The full suite is a **Phase 5 gate** (and the REFACTOR per-step gate); it catches anything a targeted run misses, so per-task full-suite runs are not needed.

**FEATURE / CROSS-CUTTING** (when instructed to execute tasks):
1. Pick a ready task from the task DAG.
2. **QA Agent (Red):** Write failing tests in `allowed_files.test_files`. Run `red_command`. Confirm tests FAIL.
3. **Record RED evidence** in `docs/verification/[name].md`.
4. **Coder Agent (Green):** Implement logic in `allowed_files.source_files` following `implementation_steps`. Run `green_command`. Confirm tests PASS 100%. Run ruff on the changed paths (the ruff gate — no separate ruff step).
5. **Record GREEN evidence** in `docs/verification/[name].md`.
6. **Refactor:** Improve code without changing observable behavior. Re-run `green_command`. **No-op fast-path:** when S4.2's implementation is a small change or follows an established, already-clean pattern (e.g., a repeated ADR-071 enforcement wiring), confirm 'no structural changes needed' and return — the targeted `green_command` suffices; do NOT re-run the full suite (that is a Phase 5 gate).
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
9. Run the reproduction tests (GREEN) and the full regression suite (no new failures) — **Light-tier ISSUE** (see "Light ISSUE tier" under Emergency / Fast-Path Exception): targeted + smoke instead, with the full regression suite as the Phase 6 pre-merge gate.
10. Run lint (`uv run ruff check .`) and type checks (`uv run mypy src/`).
11. Update the traceability matrix with the issue's evidence rows.
12. If the regression suite shows a failure, classify it as in the FEATURE path (pre-existing vs regression).

**REFACTOR**:
13. Run the full regression suite (MUST be GREEN, zero test changes) and verify the architecture rules by inspection — feature boundaries (code lives in the correct feature directory, no cross-feature internal imports) and architecture rules (`model/` contains domain concepts, `services/` contains use cases, `shared/` is deliberately small) — recording the result in `docs/verification/[name].md`. These are the same checks as Phase 6 review checks 3 and 4.
14. Run lint (`uv run ruff check .`) and type checks (`uv run mypy src/`).
15. Confirm no observable behavior changed (suite result identical to baseline).

**DOCS/CHORE**:
16. Run lint and type checks where applicable; confirm no test files or behavior were touched.
### Phase 6: REVIEW
All types. After verification passes:

**Bounded scope (per S6.x step).** Each S6.x step is a bounded subagent with explicit, bounded inputs — the approved spec, the verification artifact, and the FINAL code state — NOT the full commit-by-commit diff. Do NOT re-run the full test suite (Phase 5 already confirmed the gate CLEAN). Review the final state of the code; an unbounded 'review the whole diff' scope loops (P-27).

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

On reclassification: keep the same worktree, rename the branch to the new type (`git branch -m <old> <new>`), re-run the new type's Phase P from **P.1** (its Phase 1 output is produced there), and record the reclassification in `docs/verification/[name].md`.

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
PREPARED → SPECIFIED → TESTS_WRITTEN → RED_CONFIRMED → IMPLEMENTING → GREEN → REFACTORED → VERIFIED
```

`PREPARED` is reached at the Phase P **READY** gate (TODO `Status: READY` + every question `ANSWERED` + the type's Phase 1 output recorded). A change MUST NOT enter Phase 1/2/3/4 unless it is `PREPARED`.

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
- Start implementation work before classifying the change type (Phase 0, at P.1).
- Start **P.4** (create the change branch and worktree) for a TODO whose `## Value triage` section is empty or whose implement / merge / drop decision is not recorded (see "Backlog value triage").
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
- Execute a workflow step directly in the orchestrator's context — every workflow step runs in a new subagent (see Phase Execution (Atomic Steps, Synchronous Subagents)).
- Run a step subagent in the **background** — step subagents are always synchronous; the workflow waits for the step to complete and return its handoff before proceeding.
- Proceed past a `BLOCKED-USER` step until the user has answered the recorded question — the **change** must not proceed; the **workflow** continues with another change.
- Start Phase 1 (S1.4) or any later phase for a change whose question file still has a `PENDING` answer or whose TODO is not `READY`.
- Idle or wait in place on a human gate (spec approval, PR merge, `BLOCKED-USER`) while another change is READY — mark the gated change WAITING and continue with another change.
- Commit anything except the Phase P planning artifacts (`docs/todo/`, `docs/questions/`) directly to `main`.
- Record questions in a central question file — questions go in `docs/questions/<name>.md`, one file per change.
- Skip the **ruff** gate after an implementation or test step (ruff must be clean before the step's other gates).
- Let a step subagent call `ask_user_question` directly — questions are recorded in `docs/questions/<name>.md` and presented by the orchestrator.

---

## Agent Obligations

An agent MUST:
1. Classify the change type (Phase 0, at P.1) and record it in `docs/verification/[name].md`.
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
12. Track the change with the `todo` tool per the Todo Tracking Discipline: one item per phase the type runs, linked by `blockedBy`, `in_progress` before a phase starts, `completed` only when all of its atomic steps are done and its gate passes.
13. Execute each workflow step in a new **synchronous** subagent via the `subagent` tool (see Phase Execution (Atomic Steps, Synchronous Subagents)); verify each step's handoff before marking its todo `completed`.
14. Record every `BLOCKED-USER` question in the change's question file `docs/questions/<name>.md` (step, why needed, context, question, answer, status, incorporated) and present it to the user before that change proceeds.
15. Run **ruff** after each implementation or test step and require it to be clean before the step's other gates.
16. Log friction (failed/relaunched/iterating/blocked steps) in `docs/workflow/PROBLEMS.md` so the after-workflow-optimization can read it.
17. Prepare every change before running its workflow (Phase P): TODO file, ≥ 20 interrogation questions for FEATURE/CROSS-CUTTING, all answers recorded, draft spec / triage / baseline / scope, self-consistency check (FEATURE/CROSS-CUTTING); the **value triage** (overlap, beneficiary, 1–5 score, recommendation) with the user's implement / merge / drop decision recorded before P.4.
18. Keep the workflow moving: when a change reaches a human gate, mark it WAITING and continue with the next READY change; resume it with a fresh subagent when its gate clears.

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
- **The matrix Status column is a historical gate record** (decision Q-129, convention B). A row records the state *as observed by the change that wrote it* — the change name and date live inside the cell (e.g. `GREEN (full suite: 727 passed … search S5.1 …, commit 7bbc05a)`). A later change adds or updates rows only for the REQs/ACs it actually touches; it never refreshes rows it did not change, and a dated `RED`/`PENDING` row is a legal record of a past gate, not a defect.
- **CI enforces referential integrity, not status freshness.** `uv run python scripts/check_traceability.py` (the `traceability` job in `.github/workflows/spec-validation.yml`) fails when a `REQ-XXX`/`AC-XXX` defined in `docs/specs/` has no matrix row, when a row references an ID no spec defines, when a row cites a test function that no longer exists under `tests/`, or when a Status cell uses an undeclared value (`PENDING`, `RED`, `GREEN`, `REFACTORED`, `VERIFIED`, `N/A`). It never fails because a row's status is stale.
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

- **Set it up once at startup.** Call `setup_logger()` exactly once in the application entrypoint (e.g., `src/main.py` / backend startup) before any feature code runs. It is idempotent and thread-safe: it owns exactly two managed sinks (a console handler and a rotating file handler), and a later call reconfigures them instead of adding handlers.
- **Pick a renderer with `renderer=`.** `setup_logger(renderer="json")` writes JSON records on both sinks, `setup_logger(renderer="text")` writes human-readable text on both — the level name is colorized only where the sink's stream is a terminal, so the rotating file records are never colorized; the default (`renderer=None`) is text on the console and JSON in the file. An unknown value raises `ValueError` before anything is installed.
- **Configure the `log_*` values through the settings registry.** `register_settings(registry)` registers `logging.log_level`, `logging.log_file`, `logging.log_max_bytes`, `logging.log_backup_count` and `logging.profiling_include_arguments`; they are read live, and an unregistered key falls back to the `Settings` default. Use `get_settings()` to read the current values.
- **Trace functions with `@logged`.** Decorate sync or async functions/methods to log entry, exit (with elapsed ms), and exceptions. Usable bare (`@logged`, default level `DEBUG`) or with parameters: `level`, `slow_threshold_ms`, `slow_threshold_setting`, `include_args`.
- **Trace classes with `@logged_class`.** Decorate a class to apply `@logged` to every public method (private methods are skipped). Usable bare (`@logged_class`) or with parameters: `slow_threshold_ms` (concrete slow-call threshold stored on the class) and `include_args` (whether arguments are formatted into the entry record; secret handlers MUST use `False`). The class is marked traced (`__logged_class__ = True`) and exposes the concrete `slow_threshold_ms` attribute.
- **One-off statements.** For anything the decorators do not cover, use the feature's own logger: `log = get_logger()` (or `get_logger("eventbus")` to name the records' logger), then `log.info("index built", files=12)`. Calling it before setup does not raise: the record bypasses the managed sinks, and only WARNING-and-above reaches standard error through the standard library's last-resort handler — setup still comes first.
- **Conventions.** Records never contain local variable values; pass what should be recorded as keyword fields. Import the public API only (`from backend.logging import get_logger, logged, logged_class, register_settings, setup_logger, Settings, get_settings`); do not import the private `_pipeline` / `_decorator` / `_renderers` / `_settings` modules, and never import or call a logging backend from feature code. The pipeline MUST be set up before any `@logged` call or log statement.
- **Tracing policy (default).** Public service/registry/repository/provider classes MUST be traced with `@logged_class` by default, and public module-level functions MUST be traced with `@logged`. `get_logger()` is reserved for one-off statements (business decisions, lifecycle, warnings) and MUST NOT be used to hand-log entry/exit that the decorator already provides. Use `include_args=False` for methods that handle passwords/tokens/credentials. Set a sensible `slow_threshold_ms` on traced classes. Use semantic log levels (DEBUG for routine tracing, INFO for significant lifecycle, WARNING for recoverable issues, ERROR for failures).

```python
from backend.logging import get_logger, logged, setup_logger

setup_logger()
log = get_logger("myfeature")

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

## Using the Mail Service Feature

New backend features that need to send emails MUST use the shared mail service at `src/backend/mail/` (spec: `docs/specs/mail-service.md`) instead of implementing their own SMTP/mail-sending logic.

- **Service entry point.** Use `MailService` (the use-case service). Construct it with an optional `transport` (an `SmtpTransport`; when `None` it builds a `SmtpTransportImpl` from the live settings on each send) and an optional `event_bus` — any object with a `publish(event)` method (structural `EventPublisher` protocol, no base class required). A `None` event bus means no events.
- **Core operations.** `send_email(to, template, context) -> EmailSendResult` (the core send: validate recipient → render template → build a `multipart/alternative` message → resolve SMTP config live → send → publish `EmailSent`). High-level: `send_password_reset_email(PasswordResetEmailRequest)` and `send_email_verification_email(EmailVerificationEmailRequest)` (built-in `PASSWORD_RESET_TEMPLATE` / `EMAIL_VERIFICATION_TEMPLATE`).
- **Feature-specific emails.** A feature provides its own `EmailTemplate` and calls the core `send_email` — no need to own SMTP logic.
- **Templates.** `EmailTemplate` is a frozen model: `name`, `subject`, `body_html`, `body_text`, all with `{{variable}}` placeholders. Rendering is `{{variable}}` substitution with HTML-escaped values (no Jinja2). A missing variable or a malformed template raises `MailTemplateError`.
- **SMTP settings.** Registered via the feature-owned `register_settings(registry)` (call at startup); read live on each send. Keys: `mail.smtp_host`, `mail.smtp_port`, `mail.smtp_username`, `mail.smtp_password` (sensitive — never in logs/events), `mail.smtp_from`, `mail.smtp_tls`, `mail.smtp_timeout`, `mail.from_name`. Unregistered keys fall back to hardcoded defaults.
- **Events.** A successful send publishes `EmailSent`; a failed send publishes `EmailFailed` (with the error kind: `"template"`, `"configuration"`, or `"transport"`) and re-raises the `MailError`. Events carry non-sensitive data only (no email body, no token, no SMTP password).
- **Errors.** Exceptions are the `MailError` hierarchy (from `backend.mail.errors`): `MailConfigurationError` (SMTP settings missing/invalid at send time), `MailTransportError` (delivery failed: connection, authentication, SMTP protocol error, or timeout), `MailTemplateError` (invalid recipient, missing/unknown variable, malformed template). All messages are secret-free.
- **Transport.** `SmtpTransport` is the ABC (a single `send(message)`); `SmtpTransportImpl` is the smtplib-backed default (connects per send, authenticates when a username is present). The ABC is the seam for a fake transport in tests.
- **Tracing.** `MailService` is traced via `@logged_class` (`include_args=False`, `slow_threshold_ms=5000`); the SMTP password and tokens never appear in log records.

```python
from backend.mail import (
    MailService,
    PasswordResetEmailRequest,
    register_settings,
)
from backend.settings import get_settings_registry

register_settings(get_settings_registry())  # once at startup

service = MailService(event_bus=event_bus)
service.send_password_reset_email(
    PasswordResetEmailRequest(
        to="alice@example.com",
        display_name="Alice",
        reset_url="https://app.example.com/reset?token=...",
    )
)
```

---

## Using the File Management Feature

New backend features that need user-file storage MUST use the shared file-management feature at `src/backend/filemanagement/` (spec: `docs/specs/file-management.md`) instead of implementing their own file storage.

- **Service entry point.** Use `FileService` (the use-case service). Construct it with a `FileRepository` and an optional `StorageBackend` (when `None` it builds a `LocalDiskStorageBackend` from the live `filemanagement.storage_root` on each operation), plus an optional `event_bus` — any object with a `publish(event)` method (structural `EventPublisher` protocol, no base class required) — and an optional `settings_registry` (when `None` it uses the shared `get_settings_registry()`). A `None` event bus means no events; a publisher failure never breaks the operation.
- **Core operations.** `upload(source, key=None, namespace="general", original_filename=None, declared_mime_type=None, uploader=None) -> FileRead` (source: a filesystem path, raw bytes, or a file-like binary stream; validation: key/namespace patterns, zero-byte, live size limit, magic-byte type detection as the source of truth, declared/filename type conflicts rejected, live allowed-type set; the write is atomic with mutual rollback between the storage content and the metadata record), `download(key) -> bytes`, `open(key) -> BinaryIO` (file-like stream, usable as a context manager), `delete(key)` (no-op if the content is already missing), `get_file(key) -> FileRead`, `list_files(namespace=None, limit=100, offset=0) -> list[FileRead]` (namespace prefix match, created_at ordering, limit/offset pagination; `limit < 1` or `offset < 0` → `ValueError`).
- **Avatar operations.** `upload_avatar(user_id, source) -> AvatarRead` (first avatar; an existing avatar → `AvatarError(operation='upload')`), `replace_avatar(user_id, source) -> AvatarRead` (stores the new file + variants, deletes the old file + variants; a missing avatar → `AvatarError(operation='replace')`; publishes `FileUploaded`/`FileDeleted` but NO `AvatarUploaded`), `delete_avatar(user_id)` (deletes the file + variants, clears the user→file mapping; a missing avatar is a no-op), `get_avatar(user_id) -> AvatarRead` (returns the default avatar when the user has no avatar or a dangling mapping; a dangling mapping is cleared), `get_default_avatar() -> bytes` (module function). Avatars: image/png, image/jpeg, image/webp only; Pillow decode validation (truncated image → `FileValidationError(reason='image_decode_failed')`); dimensions ≤ 4096×4096; 64px/256px PNG variants stored as separate files (deleted with the main file); URL `https://<base>/files/<file_id>` (live `filemanagement.avatar_base_url`, always https).
- **Settings.** Registered via the feature-owned `register_settings(registry)` (call at startup); read live on each operation. Keys: `filemanagement.storage_root` (TEXT, default `./data/files`), `filemanagement.max_file_size` (NUMBER, default `10485760`), `filemanagement.avatar_max_size` (NUMBER, default `2097152`), `filemanagement.allowed_types` (LIST, 9 MIME defaults), `filemanagement.avatar_base_url` (TEXT, default `files.example.com`). Unregistered keys fall back to hardcoded defaults.
- **Storage backends.** `LocalDiskStorageBackend(root)` (production: flat layout, key-pattern + resolved-path containment enforcement, symlink rejection, atomic `put` via temp file + `os.replace`, last-write-wins) / `InMemoryStorageBackend()` (tests/DI; instances are isolated) — both implement the `StorageBackend` ABC (`put`/`get`/`delete`/`exists`/`stat`).
- **Repository.** `SqliteFileRepository("sqlite:///...")` (production: auto-creates the DB file's parent directory, thread-safe SQLite, atomic same-key replacement) — implements the `FileRepository` ABC.
- **Events.** `FileUploaded`, `FileDownloaded`, `FileDeleted`, `FileValidationFailed`, `AvatarUploaded`, `AvatarDeleted` (non-sensitive data only — never file content, never secrets).
- **Errors.** Exceptions are the `FileManagementError` hierarchy (from `backend.filemanagement.errors`): `FileManagementNotFoundError`, `FileTooLargeError`, `FileTypeNotAllowedError`, `FileValidationError`, `StorageError`, `AvatarError`. All carry context attributes (key, reason, user_id, operation).
- **Tracing.** `FileService` and the repository classes are traced via `@logged_class` (`include_args=False` — file content never appears in log records); `register_settings` and `get_default_avatar` are traced via `@logged`.

```python
from backend.filemanagement import (
    FileService,
    LocalDiskStorageBackend,
    SqliteFileRepository,
    register_settings,
)
from backend.settings import get_settings_registry

register_settings(get_settings_registry())  # once at startup

service = FileService(
    SqliteFileRepository("sqlite:///./files.db"),
    LocalDiskStorageBackend("./data/files"),
    event_bus=event_bus,
)
record = service.upload("report.pdf", namespace="general", original_filename="report.pdf")
content = service.download(record.key)
```

---

## Using the Search Feature

New backend features that need to expose their content to cross-feature search MUST register a search source with the shared search feature at `src/backend/search/` (spec: `docs/specs/search.md`) instead of implementing their own search.

- **Service entry point.** Use `get_search_service()` (the module singleton) or `SearchService(event_bus=..., settings_registry=..., permission_service=...)` for tests/DI. Call `reset_search_service()` between tests. `InMemorySource` is the test/DI source helper (a list of items wrapped as a source).
- **Register a source.** Call `register_source(SearchSource(name, fields, query))`: `name` is the source name (pattern `^[a-z][a-z0-9_]*$`); `fields` is the field schema (`SourceField` — `name`, `type` from the closed `FieldType` set, and the `searchable`/`filterable`/`sortable`/`display` flags); `query` is the **sync** query function `SourceQueryContext -> SourcePage` (apply free text, filters, sort, and pagination in memory; stateless live query — no index, no cache, no persistence). The source's default ordering is the order `query` returns items in when `sort` is `None`.
- **Query.** `search(SearchQuery(free_text, filters, feature, offset, limit, sort), principal=...)` — omitting `feature` fans out to **all** registered sources (combined pagination); `limit` `None` = the live `search.default_page_size`. A source failure is resilient: global fan-out returns partial results + a `SourceFailure` marker + a `SourceQueryFailed` event (no exception); a single-source query (`feature` set) raises `SourceQueryFailedError`. Each source query runs under the live `search.source_timeout` (ms) — exceeding it is a `timeout` failure.
- **Feature-owned registration.** The search feature exposes `register_settings(registry)` (settings: `search.default_page_size`, `search.max_page_size`, `search.source_timeout`) and `register_actions(catalog)` (the additive `search.search` catalog action) in `feature_settings.py` / `feature_actions.py` — call them at startup, like the other features' feature-owned registrations.
- **Permissions.** The enforced query path requires the `search.search` action (the shared `Principal`/`PermissionChecker` enforcement plumbing, ADR-079); callers may pass an explicit `principal` (default: the system principal).
- **Events.** Registration/unregistration/failure publish `SourceRegistered`/`SourceUnregistered`/`SourceQueryFailed` (best-effort; non-sensitive data only — never query text or result content).
- **Errors.** Exceptions are the `SearchError` hierarchy (from `backend.search`): `UnknownSourceError`, `MalformedQueryError` (invalid pagination, non-filterable/non-sortable field, invalid operator, wrong value type — identifies the reason and the field/source), `SourceQueryFailedError` (source + reason + error kind).
- **Existing sources.** user-management, file-management, and session-management expose `build_user_source(repository)` / `build_file_source(repository)` / `build_session_source(repository)` — the startup wiring in `src/main.py` registers all three.

```python
from backend.search import SearchQuery, get_search_service
from backend.usermanagement import build_user_source

service = get_search_service()
service.register_source(build_user_source(user_repository))  # each feature exposes build_*_source

result = service.search(SearchQuery(free_text="ali"))  # global fan-out, combined pagination
```

---

## Using the Test Tooling (polyfactory, respx, time-machine)

Feature tests MUST use the shared test tooling instead of hand-crafted test data, real time, or ad-hoc fake transports. The shared helpers live at `tests/tooling_test_helpers.py` (import top-level, like the other `*_test_helpers` modules).

- **polyfactory — model factories.** `model_factory(MyModel)` returns a factory class for a Pydantic model: `.build()` produces a schema-valid instance (no hand-crafted field dicts), `.build(field=value)` overrides individual fields, `.batch(n)` produces `n` instances.
- **time-machine — time travel.** `travel(destination)` freezes the clock for a block (yields the frozen `datetime`); for deadline behavior (TTLs, lockouts, token expiry) pass `tick=True` so the deadline passes. No sleeps, no manual clock mocking.
- **respx — httpx mocking.** `mock_http()` mocks outbound httpx calls for a block; register routes on the yielded router. Strict defaults hold: an unmocked request raises, and every registered route must be called before the block exits.

```python
import httpx
from pydantic import BaseModel

from tooling_test_helpers import model_factory, mock_http, travel

class Person(BaseModel):
    name: str
    age: int

factory = model_factory(Person)
person = factory.build()             # schema-valid instance
alice = factory.build(name="Alice")  # per-field override

with travel("2024-01-02T03:04:05") as now:
    ...  # datetime.now() is frozen at `now`

with mock_http() as router:
    router.route(method="GET", url="https://api.example.com/items").respond(json=[1, 2])
    items = httpx.Client().get("https://api.example.com/items")
```

---

## Using Migrations (alembic)

Schema migrations for the SQLModel tables.

- **Rule.** A change to a SQLModel table schema MUST add a migration (`uv run alembic revision -m "<description>"`); never hand-edit an already-applied migration.
- **Apply.** `uv run alembic upgrade head`.
- **Scaffold.** `alembic.ini` + `migrations/` are wired to `SQLModel.metadata`; `migrations/env.py` imports the model modules that define tables (backend.authentication.models, backend.filemanagement.models, backend.usermanagement.models) — when a new module defines SQLModel tables, add its import to `env.py`.
- **CI.** The `migrations` job in `.github/workflows/quality.yml` runs `alembic upgrade head` against a temp database.
- **Note.** Existing per-repository `SQLModel.metadata.create_all` bootstrapping is unchanged by this.

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

### Light ISSUE tier (in-workflow, not fast-path)

A small, localized ISSUE fix may shrink Phase 5 without leaving the workflow. An ISSUE qualifies for the **light tier** when **all** of the following hold:

- Single feature; the fix touches ≤ 3 files (excluding tests).
- No new dependency, no new public interface, no cross-feature change.
- The existing test suite already covers the affected area (the triage record names the covering tests).

For a light-tier ISSUE, Phase 5 runs **targeted + smoke** instead of full regression: the reproduction tests, the covering tests named in the triage record, and the affected feature's test directory (`uv run pytest tests/<affected-dir> -v`), plus lint and type checks. The **full regression suite** runs as a **Phase 6 pre-merge gate** (S6.4, before the PR opens) and must pass; the result is recorded in the review report. Record the light-tier qualification in the triage record (`docs/verification/[name].md`).

## Spec Approval Gate (GitHub Review)
A specification file `docs/specs/[name].md` is considered **HUMAN APPROVED** if and only if it has been merged through the repository's configured GitHub review process. This gate applies to FEATURE and CROSS-CUTTING changes (the only types that produce a spec).

Before starting Phase 2, verify approval via:
`git log main -- docs/specs/[name].md`

- Output is empty: **STOP.** Prompt user to merge spec PR first.
- Commit logs appear: Verify the commit was introduced by a merged PR (not a direct push to `main`). **PROCEED** only if the spec was reviewed.

**Direct commits to `main` do NOT constitute approval.** The spec must go through GitHub PR review to maintain the boundary: human controls WHAT, agent controls HOW.

**Verify once per change (cache the result).** The approval check runs **once**, before Phase 2, and its result (approved + merge commit + date) is recorded in `docs/verification/[name].md`. A merged spec cannot become unapproved, so later phases and step subagents MUST NOT re-run the check — they read the cached result (if the cached result is missing on re-entry, run the check once and record it). Re-running `git log main -- docs/specs/[name].md` at later phase transitions is wasted round-trips.

The spec is drafted and self-checked during **Phase P**; S1.4 only commits it and opens the approval PR, so the approval check runs after that PR is merged — the caching rule is unchanged.

## Project Structure
The project is organized around a single `src/` package, and `backend` is the only runtime boundary that exists inside it: no `src/frontend/` directory exists (the coverage configuration reserves the name). Feature packages under `src/backend/` are flat — there is no `model/` and no `services/` subdirectory anywhere — and the only nested directory under `src/` is `src/backend/filemanagement/assets/`.

```text
project/
├── .agents/
│   └── skills/
├── .github/
├── .vscode/
├── docs/
├── userdocs/
│
├── scripts/
├── migrations/
│   └── versions/
│
├── src/
│   ├── main.py
│   └── backend/
│       ├── <feature>/
│       │   └── <module>.py
│       ├── filemanagement/
│       │   └── assets/
│       └── shared/
│
└── tests/
    ├── acceptance/
    │   └── <feature>/
    ├── contract/
    ├── integration/
    ├── property/
    └── unit/
```

The generated `STRUCTURE.md` at the repository root is the authoritative map of this layout (see "Tooling & Execution Environment"); it is never hand-edited.

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
