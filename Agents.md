# AGENTS.md — AI Agent Operating Guidelines

This repository strictly enforces a **Spec-Driven, Test-Driven Development (Spec-TDD) Workflow**. AI agents operating in this project MUST follow the procedures defined below.

---

## Primary Constraint: No Direct Implementation Code
**DO NOT write, modify, or scaffold implementation source code (`src/`, `lib/`, `app/`, etc.) without an approved Specification file and a validated Task Graph.**

If asked to implement a new feature, refactor core components, or build a system, you MUST complete **Phase 1** and **Phase 2** first.

---

## Tooling & Execution Environment
This repository utilizes modern Python tooling managed via `uv`:
- **Package Manager:** `uv` (Use `uv run <command>` for isolated execution)
- **Quality Assurance & Formatting:** `ruff` (`uv run ruff check` / `uv run ruff format`)
- **Type Checking:** `mypy` (`uv run mypy src/`)
- **Test Runner:** `pytest` (`uv run pytest`)
- **Property Testing:** `hypothesis` (`uv run pytest tests/property/`)
- **Standard Verification:** `uv run pytest tests/`

---

## The 5-Phase Spec-TDD Workflow Protocol

### Phase 1: SPECIFY (`docs/specs/`)
Before writing task files or code:
1. Search and read existing codebase files to understand current context and patterns.
2. Check `docs/specs/template.md` for formatting requirements.
3. Draft a complete feature spec at `docs/specs/[feature-name].md`.
4. Include exact API schemas, Pydantic models, interface signatures, and non-functional requirements.
5. Assign stable IDs to every normative requirement (`REQ-XXX`), acceptance criterion (`AC-XXX`), invariant (`INV-XXX`), edge case (`EDGE-XXX`), and NFR (`NFR-XXX`).
6. Define the test strategy mapping each AC/INV/EDGE to a test category and test function.
7. **STOP and present the spec for human approval via Git PR.**

### Phase 2: TEST DESIGN (`tests/`)
Once the specification file is merged into `main`:
1. Write acceptance tests derived directly from the spec's acceptance criteria.
2. Write property tests for every invariant (`INV-XXX`) using Hypothesis.
3. Write unit tests for edge cases and error conditions.
4. Write contract tests for NFR contract requirements.
5. Write integration tests for multi-component interactions.
6. **Run the test suite and confirm RED state** (tests must fail before implementation).
7. Update the traceability matrix in `docs/verification/traceability.md` with test references.

### Phase 3: DESIGN (`docs/decisions/`, `docs/tasks/`)
After RED is confirmed:
1. Create ADRs in `docs/decisions/` for significant design decisions (WHY, not WHAT).
2. Decompose the spec into a machine-readable JSON task DAG at `docs/tasks/[feature-name].tasks.json`.
3. Each task MUST specify:
   - `requirements`: REQ-XXX IDs covered by this task.
   - `acceptance_criteria`: AC-XXX IDs covered by this task.
   - `tests_to_create`: Test functions to write (MUST come before implementation scope).
   - `red_command`: Command to confirm RED state.
   - `green_command`: Command to confirm GREEN state.
   - `design_constraints`: Constraints that must be respected.
   - `implementation_scope`: What to implement.
   - `completion_gates`: Gates that must pass before the task is complete.
4. Copy `docs/tasks/[feature-name].tasks.json` to `.github/task-runner/tasks.json` to initialize the active build environment.

### Phase 4: IMPLEMENT
When instructed to execute tasks:
1. Pick a ready task from the task DAG.
2. **QA Agent (Red):** Write failing tests in `allowed_files.test_files`. Run `red_command`. Confirm tests FAIL.
3. **Coder Agent (Green):** Implement logic in `allowed_files.source_files`. Run `green_command`. Confirm tests PASS 100%.
4. **Refactor:** Improve code without changing observable behavior. Re-run `green_command`.
5. **Commit & Update Status:** Set `"status": "VERIFIED"` in `.github/task-runner/tasks.json`. Sync final statuses back to `docs/tasks/[feature-name].tasks.json`.

### Phase 5: VERIFY
After all tasks are complete:
1. Run the full test suite: `uv run pytest tests/ -v`.
2. Run acceptance tests: `uv run pytest tests/acceptance/ -v`.
3. Run property tests: `uv run pytest tests/property/ -v`.
4. Run contract tests: `uv run pytest tests/contract/ -v`.
5. Update the traceability matrix: every REQ must have at least one GREEN test.
6. Produce a verification report: specification coverage, acceptance coverage, branch coverage.
7. **Spec coverage = 100% is required.** Code coverage is a secondary quality signal, not evidence that the specification has been implemented.

---

## State Machine

Every task transitions through this state machine:

```
SPECIFIED → TESTS_WRITTEN → RED_CONFIRMED → IMPLEMENTING → GREEN → REFACTORED → VERIFIED
```

- An agent MUST NOT transition from `TESTS_WRITTEN` to `IMPLEMENTING` unless RED has been observed.
- An agent MUST NOT transition from `GREEN` to `VERIFIED` unless the traceability matrix is updated.

---

## Agent Prohibitions

An agent MUST NOT:
- Write implementation before acceptance tests exist.
- Modify an acceptance test merely to make implementation pass.
- Delete or weaken a test to achieve GREEN.
- Convert a failing acceptance test into a weaker test.
- Introduce behavior not represented by the specification without updating the specification first.
- Mark a requirement complete without executable evidence.
- Skip the RED gate (transitioning from TESTS_WRITTEN to IMPLEMENTING without observing RED).
- Let code coverage substitute for specification coverage.

---

## Agent Obligations

An agent MUST:
1. Identify affected requirements (REQ-XXX).
2. Identify acceptance criteria (AC-XXX).
3. Create executable tests.
4. Run them and demonstrate RED.
5. Obtain approval if required.
6. Implement the minimum behavior required.
7. Achieve GREEN.
8. Refactor without changing observable behavior.
9. Run regression tests.
10. Produce a traceability/evidence report.

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

---

## General Code & Style Conventions
- **Language & Runtime:** Python 3.14+
- **Type Safety:** Strict typing required. Every function signature must have explicit parameters and return type hints.
- **Testing Standard:** Framework `pytest`. Tests must precede implementation code. Never remove existing tests without explicit spec authorization.
- **Property Testing:** Use `hypothesis` for invariant verification. Strategies must match the domain.
- **Documentation:** Keep docstrings concise; explain *why* non-obvious logic exists rather than restating *what* the code does.

---

## Emergency / Fast-Path Exception
The spec-and-task workflow is bypassed **ONLY** for:
- Minor typos, docstring fixes, or comment edits.
- One-line bug fixes with an existing, failing test already in place.
- Direct user commands explicitly containing the keyword `--skip-spec`.

---

## Spec Approval Gate (Git-Native)
A specification file `docs/specs/[feature-name].md` is considered **HUMAN APPROVED** if and only if it exists on `main`.

Before starting Phase 2 or 3, verify approval via:
`git log main -- docs/specs/[feature-name].md`

- Output is empty: **STOP.** Prompt user to merge spec PR first.
- Commit logs appear: **PROCEED** to Task Decomposition / Execution.

## Project Structure and Feature Architecture

The project is organized around **features**, with `frontend` and `backend` as the primary runtime boundaries.

```text
project/
├── docs/
│   ├── specs/
│   └── decisions/
│
├── frontend/
│   ├── features/
│   │   ├── <feature>/
│   │   │   ├── model/
│   │   │   ├── services/
│   │   │   └── ...
│   │   └── ...
│   └── shared/
│
├── backend/
│   ├── features/
│   │   ├── <feature>/
│   │   │   ├── model/
│   │   │   ├── services/
│   │   │   └── ...
│   │   └── ...
│   └── shared/
│
└── tests/
    └── acceptance/
        └── <feature>/
```

### Principles

* **Features are the primary architectural boundary.** Code belonging to a feature should live together rather than being split into global `models`, `services`, or `repositories` directories.
* **Frontend and backend are separate runtime boundaries.** A feature may have both a frontend and backend implementation, but each side owns its respective concerns.
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

