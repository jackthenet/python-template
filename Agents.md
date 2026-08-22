# AGENTS.md

## Project Standards
- Architecture Pattern: Design-Driven Development (DDD).
- System Specs: Always consult `/docs/specs/` before creating new features.
- Tech Stack: Python 3.12, FastAPI, Pydantic v2, pytest.

## Workflow Rules
1. Never write implementation code until a design spec exists in `/docs/specs/`.
2. Do not modify public API schemas without updating the OpenAPI spec first.
3. Run `pytest` before marking any task as complete.

## Whenever asked to design a new feature:
1. First, create a specification file in `/docs/specs/[feature-name].md` using the Spec Template.
2. Second, break the feature into discrete, step-by-step task files in `/docs/tasks/`.
3. Never start writing code until the user approves the spec.

## Basic Directory Layout
my-project/
├── AGENTS.md                   # Global instructions for the AI
├── docs/
│   ├── specs/                  # High-level architecture & specs
│   │   └── user-auth.md
│   └── tasks/                  # Granular task files
│       ├── 001-auth-schemas.md # Completed or active task
│       ├── 002-auth-service.md # Current active task
│       └── 003-auth-api.md     # Pending Task





# AGENTS.md — AI Agent Operating Guidelines

This repository strictly enforces a **Design-Driven, Spec-First Development Workflow**. AI agents operating in this project MUST follow the procedures defined below.

---

## 🚫 Primary Constraint: No Direct Implementation Code
**DO NOT write, modify, or scaffold implementation source code (`src/`, `lib/`, `app/`, etc.) without an approved Specification and Task file.**

If asked to implement a new feature, refactor core components, or build a system, you MUST complete **Phase 1** and **Phase 2** first.

---

## 📋 The 3-Phase Workflow Protocol

### Phase 1: Specification (`/docs/specs/`)
Before writing any task files or code:
1. Search and read existing codebase files to understand current context and patterns.
2. Check `/docs/specs/template.md` for formatting requirements.
3. Draft a complete feature spec at `/docs/specs/[feature-name].md`.
4. Include:
   - Objectives & boundary conditions.
   - Core architecture and design decisions.
   - Exact API schemas, Pydantic/TypeScript models, or interface signatures.
   - Non-functional requirements and error-handling strategies.
5. **STOP and present the spec to the human user for explicit approval.**

---

### Phase 2: Task Decomposition (`/docs/tasks/`)
Once the specification file is approved:
1. Check `/docs/tasks/template.md` for task structure.
2. Break down the spec into sequential, isolated task files named:
   `/docs/tasks/[NNN]-[short-description].md` (e.g., `001-rate-limit-schema.md`).
3. Each task file MUST contain:
   - Clear reference to its parent spec in `/docs/specs/`.
   - Prerequisites (e.g., "Requires Task 001 to be marked Completed").
   - A single, tightly focused scope of work.
   - An explicit, runnable verification command (e.g., `pytest tests/test_rate_limit.py`).
4. Keep tasks small enough to execute in a single isolated prompt session without hitting context window limits.

---

### Phase 3: Task Execution & Verification
When instructed to execute a specific task (e.g., "Work on Task 002"):
1. Load ONLY the target task file and its referenced spec section into context.
2. Execute the implementation steps outlined in the task checklist.
3. Write matching unit/integration tests for the implemented code.
4. Run the exact **Verification Command** defined in the task file.
5. If tests pass:
   - Update the task file metadata status to `Completed`.
   - Update task checklist items from `- [ ]` to `- [x]`.
6. If tests fail:
   - Fix the code and rerun verification. Do NOT mark the task complete until tests pass cleanly.

---

## 📐 General Code & Style Conventions
- **Language & Runtime:** Python 3.12+
- **Type Safety:** Strict typing required. Every function signature must have explicit parameters and return type hints.
- **Testing Standard:** Every task must include tests (`pytest`). Never remove existing tests unless explicit approval is granted in a spec.
- **Documentation:** Keep docstrings concise; explain *why* non-obvious logic exists rather than restating *what* the code does.

---

## 🛠️ Emergency / Fast-Path Exception
The spec-and-task workflow is bypassed **ONLY** for:
- Minor typos, docstring fixes, or comment edits.
- One-line bug fixes with an existing, failing test already in place.
- Direct user commands explicitly containing the keyword `--skip-spec`.



Keeping the Index Updated (Manual vs. Automated)
Manual Update: As part of the AI's completion protocol (enforced via your AGENTS.md), the agent is instructed: "When marking a task as completed, update its status in /docs/tasks/README.md as well."

Automated Script (Optional): If you want to avoid manual updates entirely, write a 10-line Python script or shell command in your repo that scans the /docs/tasks/ folder, parses the YAML frontmatter or first heading of each file, and automatically rewrites the Markdown table in README.md before every commit.



# AGENTS.md — Git-Native Spec Approval Protocol

## 🔒 Spec Approval Gate (Git-Native)
A specification file `/docs/specs/[feature].md` is considered **HUMAN APPROVED** if and only if it meets one of the following conditions:

1. **Primary Branch Verification:** The spec file exists on the primary branch (`main` or `master`).
2. **Git Commit History:** The file was introduced via a merged Pull Request or explicitly committed by a human developer.

---

## 🚦 Execution Rules for AI Agents

### 1. When Drafting a Spec
- Create a dedicated Git branch: `spec/[feature-name]`.
- Draft the spec file at `/docs/specs/[feature-name].md`.
- Commit the file and prompt the human:
  > *"I have drafted the specification at `/docs/specs/[feature-name].md` on branch `spec/[feature-name]`. Please review, create a Pull Request, and merge to `main` when approved."*
- **STOP HERE.** Do NOT create task files or write implementation code on this branch.

### 2. When Creating Tasks or Writing Code
- Verify that `/docs/specs/[feature-name].md` exists in the local repo and is present on `main` (run `git merge-base --is-ancestor HEAD main` or check git status).
- **If the spec is NOT on `main`:** Refuse to implement code and remind the user to merge the spec PR first.
- **If the spec IS on `main`:** Proceed with generating tasks in `/docs/tasks/` and executing implementation steps.


## Spec Approval Verification Rule
Before starting any implementation work, run this exact bash command:
`git log main -- /docs/specs/[feature-name].md`

- If the output is empty: STOP. The spec has not been merged to `main`.
- If commit logs appear: Proceed with generating tasks and code.