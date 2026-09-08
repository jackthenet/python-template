# AGENTS.md — AI Agent Operating Guidelines

This repository strictly enforces a **Spec-Driven, Test-Driven Development (Spec-TDD) Workflow**. AI agents operating in this project MUST follow the procedures defined below.

---

## Primary Constraint: No Direct Implementation Code
**DO NOT write, modify, or scaffold implementation source code (`src/`, `lib/`, `app/`, etc.) without an approved Specification file and a validated Task Graph.**

If asked to implement a new feature, refactor core components, or build a system, you MUST complete **Phase 1**, **Phase 2**, and **Phase 3** first.

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

## The 6-Phase Spec-TDD Workflow Protocol

### Skill-to-Phase Mapping

| Phase | Skill | Purpose |
|-------|-------|---------|
| Phase 1: DISCOVER & SPECIFY | `specify` | Creates a feature branch, adversarially interrogates the feature idea into a feature brief, and turns the brief into an approved-quality specification with stable REQ, AC, INV, EDGE, and NFR IDs. |
| Phase 2: DECOMPOSE | `decompose` | Creates ADRs and decomposes the spec into a machine-readable JSON task DAG. |
| Phase 3: TEST & RED | `test` | Converts an approved specification into executable acceptance tests, property tests, unit tests, and contract tests, and confirms RED state. |
| Phase 4: IMPLEMENT | `implement` | Implements the minimum behavior required to turn failing acceptance tests (RED) into passing tests (GREEN), then refactors without changing specified behavior. |
| Phase 5: VERIFY | `verify` | Produces evidence that the implementation satisfies the specification by running acceptance tests, regression suites, lint, type checks, coverage, and architecture rules. |
| Phase 6: REVIEW | `review` | Reviews code changes against the specification before reviewing implementation style. Checks traceability, acceptance tests, feature boundaries, and architecture rules. |

### Phase 1: DISCOVER & SPECIFY (`docs/specs/`)
Before writing task files or code:
1. Create a feature branch `feature/[feature-name]` from `main`.
2. Adversarially interrogate the feature idea to discover ambiguity, hidden requirements, edge cases, and scope boundaries; capture a feature brief.
3. Search and read existing codebase files to understand current context and patterns.
4. Check `docs/specs/template.md` for formatting requirements.
5. Draft a complete feature spec at `docs/specs/[feature-name].md`.
6. Include exact API schemas, Pydantic models, interface signatures, and non-functional requirements.
7. Assign stable IDs to every normative requirement (`REQ-XXX`), acceptance criterion (`AC-XXX`), invariant (`INV-XXX`), edge case (`EDGE-XXX`), and NFR (`NFR-XXX`).
8. Define the test strategy mapping each AC/INV/EDGE to a test category and test function.
9. **STOP and present the spec for human approval via Git PR.**

### Phase 2: DECOMPOSE (`docs/decisions/`, `docs/tasks/`)
Once the specification file is merged into `main`:
1. Create ADRs in `docs/decisions/` for significant design decisions (WHY, not WHAT).
2. Decompose the spec into a machine-readable JSON task DAG at `docs/tasks/[feature-name].tasks.json`.
3. Each task MUST specify:
   - `requirements`: REQ-XXX IDs covered by this task.
   - `acceptance_criteria`: AC-XXX IDs covered by this task.
   - `tests_to_create`: Test functions to write (MUST come before implementation scope).
   - `red_command`: Command to confirm RED state.
   - `implementation_steps`: Explicit steps for implementation.
   - `green_command`: Command to confirm GREEN state.
   - `design_constraints`: Constraints that must be respected.
   - `completion_gates`: Gates that must pass before the task is complete.
4. Copy `docs/tasks/[feature-name].tasks.json` to `.github/task-runner/tasks.json` to initialize the active build environment.
### Phase 3: TEST & RED (`tests/`)
After the task DAG is initialized:
1. Write acceptance tests derived directly from the spec's acceptance criteria.
2. Write property tests for every invariant (`INV-XXX`) using Hypothesis.
3. Write unit tests for edge cases and error conditions.
4. Write contract tests for NFR contract requirements.
5. Write integration tests for multi-component interactions.
6. **Run the test suite and confirm RED state** (tests must fail before implementation).
7. Record RED evidence in `docs/verification/[feature-name].md`.
8. Update the traceability matrix in `docs/verification/traceability.md` with test references.
### Phase 4: IMPLEMENT
When instructed to execute tasks:
1. Pick a ready task from the task DAG.
2. **QA Agent (Red):** Write failing tests in `allowed_files.test_files`. Run `red_command`. Confirm tests FAIL.
3. **Record RED evidence** in `docs/verification/[feature-name].md`.
4. **Coder Agent (Green):** Implement logic in `allowed_files.source_files` following `implementation_steps`. Run `green_command`. Confirm tests PASS 100%.
5. **Record GREEN evidence** in `docs/verification/[feature-name].md`.
6. **Refactor:** Improve code without changing observable behavior. Re-run `green_command`.
7. **Commit & Update Status:** Set `"status": "VERIFIED"` in `.github/task-runner/tasks.json`. Sync final statuses back to `docs/tasks/[feature-name].tasks.json`.
### Phase 5: VERIFY
After all tasks are complete:    
1. Run the full test suite: `uv run pytest tests/ -v`.
2. Run acceptance tests: `uv run pytest tests/acceptance/ -v`.
3. Run property tests: `uv run pytest tests/property/ -v`.
4. Run contract tests: `uv run pytest tests/contract/ -v`.
5. Update the traceability matrix: every REQ must have at least one GREEN test.
6. Produce a verification report: specification coverage, acceptance coverage, branch coverage.
7. **Spec coverage = 100% is required.** Code coverage is a secondary quality signal, not evidence that the specification has been implemented.
8. **If verification fails**, the agent MUST re-enter either Phase 4 (IMPLEMENT) to fix the failing behavior, or Phase 3 (TEST & RED) to re-derive failing tests from the specification. The agent MUST NOT mark the feature verified until spec coverage = 100% and all gates pass.
### Phase 6: REVIEW
After verification passes:
1. Review all code changes against the approved specification.
2. Check traceability: every REQ has at least one GREEN test, every acceptance test traces back to a normative requirement.
3. Verify feature boundaries: code lives in the correct feature directory, no cross-feature internal imports.
4. Verify architecture rules: `model/` contains domain concepts, `services/` contains use cases, `shared/` is deliberately small.
5. Verify acceptance tests were not weakened or deleted to achieve GREEN.
6. Verify no behavior was introduced that is not represented in the specification.
7. Produce a review report documenting any findings and their resolutions.
8. **The feature is only considered complete when the review report is clean.**
9. **When the review report is clean, document the feature in `AGENTS.md`.** If the feature is reusable by future features (a shared capability, not a one-off), add a short "how to use this feature" note to `AGENTS.md` so future features use it correctly. Skip this if the feature is not applicable to other features.
10. **When the review report is clean, open a PR** for the feature branch to `main` and present it for human review/merge, then STOP. The agent MUST NOT merge the PR itself (human governance).

---

## Review Gate (Phase 6)

A feature is considered **COMPLETE** if and only if the Phase 6 review report is clean. A clean review report means:

- Every REQ-XXX has at least one GREEN test.
- Every acceptance test traces back to a normative requirement.
- No acceptance test was weakened or deleted to achieve GREEN.
- No behavior was introduced that is not represented in the specification.
- Feature boundaries and architecture rules are respected.

If the review report is not clean, the agent MUST resolve every finding and re-run the review before declaring the feature complete. A feature with an open finding MUST NOT be merged or marked verified.

When the review report IS clean, the feature branch MUST be merged into `main` via a GitHub pull request. The agent MUST open the PR and present it for human review/merge, then STOP — the agent MUST NOT merge the PR itself (human governance).

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
- **Tests are the contract.** Once acceptance tests are re-derived from an approved spec, the executable tests are the authoritative contract. If a spec *wording* or an implementation detail conflicts with a re-derived test, the test wins. The conflict MUST be flagged as a finding and resolved via the Spec Amendment Workflow — never by weakening, removing, or "fixing" the test to match the implementation.

---

## General Code & Style Conventions
- **Language & Runtime:** Python 3.14+
- **Type Safety:** Strict typing required. Every function signature must have explicit parameters and return type hints.
- **Testing Standard:** Framework `pytest`. Tests must precede implementation code. Never remove existing tests without explicit spec authorization.
- **Property Testing:** Use `hypothesis` for invariant verification. Strategies must match the domain.
- **Documentation:** Keep docstrings concise; explain *why* non-obvious logic exists rather than restating *what* the code does.

---

## Using the Logging Feature

New backend features MUST use the shared logging feature at `src/backend/logging/` (spec: `docs/specs/logging.md`) instead of inventing their own logging.

- **Set it up once at startup.** Call `setup_logger(settings)` exactly once in the application entrypoint (e.g., `src/main.py` / backend startup) before any feature code runs. It is idempotent and thread-safe (later calls are no-ops).
- **Configure with `Settings`.** Build a `Settings` instance (or use `get_settings()`) to set `log_level`, `log_file`, `log_max_bytes`, `log_backup_count`, and `profiling_include_arguments`.
- **Trace functions with `@logged`.** Decorate sync or async functions/methods to log entry, exit (with elapsed ms), and exceptions. Usable bare (`@logged`, default level `DEBUG`) or with parameters: `level`, `slow_threshold_ms`, `slow_threshold_setting`, `include_args`, `context_getter`, `depth`.
- **Trace classes with `@logged_class`.** Decorate a class to apply `@logged` to every public method (private methods are skipped).
- **Simple statements.** The feature configures loguru's sinks, so feature code may also use loguru's `logger` directly (e.g., `logger.info("...")`) for one-off statements.
- **Conventions.** `diagnose=False` is enforced (no local variable leakage). Import the public API only (`from backend.logging import logged, logged_class, setup_logger, Settings, get_settings`); do not import the private `_setup` / `_decorator` modules. The logger MUST be set up before any `@logged` call or log statement.

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

- **Get the registry.** Use `get_settings_registry()` (the module singleton) or instantiate `SettingsRegistry(event_bus=..., template_repository=...)` for tests/DI. A `None` event bus uses the shared `get_event_bus()`; a `None` repository uses in-memory storage.
- **Register settings.** Call `register(SettingDefinition(...))` for a single setting or `register_feature("name", [definitions])` for a feature's settings (each key must start with `"name."`).
- **Read/write values.** Use `get_value(key)`, `set_value(key, value)` (validated), `reset(key)`, `reset_all()`. Values are always valid for their kind; invalid writes raise `SettingsValidationError`.
- **Kinds.** Six kinds: TEXT, NUMBER, BOOLEAN, EMAIL, SLIDER, SELECT, each with kind-specific parameters and per-kind validation (see the spec).
- **Views.** Use `to_view(key)`, `views()`, `grouped_views()` for renderable metadata (category/group hierarchy, status).
- **Templates.** Use `create_template`/`load_template`/`update_template`/`delete_template`/`get_template`/`list_templates` for named value profiles scoped to a (category, group). Create/update require exact scope coverage; load sets the template's values and leaves others as-is.
- **Storage.** Use `YamlTemplateRepository(directory)` for YAML persistence (one file per template, atomic writes) or `MemoryTemplateRepository()` for in-memory. Both implement the `TemplateRepository` ABC.
- **Events.** Value changes publish `SettingChanged` (key, value, previous) to the event bus (best-effort).
- **Errors.** Exceptions are the `SettingsError` hierarchy (from `backend.settings.exceptions`): `SettingsNotFoundError`, `SettingsValidationError`, `SettingsRegistrationError`, `TemplateNotFoundError`, `TemplateValidationError`, `TemplateStorageError`.
- **Testing.** Use `reset_settings_registry()` to reset the module singleton between tests.

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

The boundary is concrete: if the change alters externally observable behavior, the full spec-and-task workflow applies regardless of how small the change appears.
## Spec Approval Gate (GitHub Review)
A specification file `docs/specs/[feature-name].md` is considered **HUMAN APPROVED** if and only if it has been merged through the repository's configured GitHub review process.

Before starting Phase 2, verify approval via:
`git log main -- docs/specs/[feature-name].md`

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

