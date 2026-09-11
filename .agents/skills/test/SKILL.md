---
name: test
description: Converts an approved specification into executable acceptance tests, property tests, unit tests, and contract tests (FEATURE/CROSS-CUTTING), or writes the reproduction test for a defect (ISSUE). Derives tests from acceptance criteria, confirms RED state, and records evidence. Use when an approved specification exists and acceptance tests need to be created before implementation, or when an ISSUE triage record exists and a reproduction test is needed.
---

# Test

Convert an approved specification into executable acceptance tests (FEATURE/CROSS-CUTTING), or write the reproduction test for a defect (ISSUE).

## Entry Conditions

- [ ] FEATURE/CROSS-CUTTING: an approved specification exists at `docs/specs/<name>.md` (merged PR); acceptance criteria are identified in the spec; no acceptance tests exist for this change yet.
- [ ] ISSUE: a triage record exists in `docs/verification/<name>.md` (affected REQ/AC, defect confirmation, reproduction plan).
- [ ] Working tree is clean.

## Input

- FEATURE/CROSS-CUTTING: `docs/specs/<name>.md`
- ISSUE: `docs/verification/<name>.md` (triage record)

## Output

- FEATURE/CROSS-CUTTING: `tests/acceptance/<name>/test_<name>.py` (plus property/unit/contract tests)
- ISSUE: the reproduction test(s) named in the triage plan (in the affected feature's test directory)

## Execution Context (Subagents)

This phase runs in a **new subagent** launched by the orchestrator via the `subagent` tool (see "Phase Execution (Subagents)" in `AGENTS.md`).

- **Inputs from the orchestrator:** the change name and type, the change worktree path, this skill file, and the previous step's handoff (prior phase's status, gate result, artifacts, evidence location).
- **Todo:** the orchestrator manages this phase's todo item (`in_progress` before launch, `completed` after verifying the handoff). The subagent never touches the todo list.
- **User questions:** do NOT call `ask_user_question`. Return the questions in the handoff (`status: BLOCKED-USER`); the orchestrator presents them to the user and resumes this subagent with the answers.
- **Handoff:** end with the structured handoff required by `AGENTS.md`: `status` / `gate` / `artifacts` / `questions` / `next`.
- **Scope:** execute exactly this phase. Do not execute another phase, do not launch a subagent, do not talk to the user.

## Todo

Per the AGENTS.md Todo Tracking Discipline, the orchestrator (not this subagent) manages the Phase 3 item: `in_progress` before launching this subagent; `completed` only after verifying the handoff that RED is observed and recorded in `docs/verification/[name].md`.

## MUST

- FEATURE/CROSS-CUTTING: derive one or more test functions per `AC-XXX`.
- Test names MUST reference the `AC-XXX` ID (e.g., `test_ac_001_valid_request`).
- Test externally observable behavior only — not implementation details.
- Run the test suite and confirm RED state (tests fail before implementation).
- Record RED evidence in `docs/verification/<name>.md` using `TDD-evidence-template.md`.
- Update the traceability matrix in `docs/verification/traceability.md`.
- FEATURE/CROSS-CUTTING: write property tests for every `INV-XXX` using Hypothesis in `tests/property/<name>/`.
- FEATURE/CROSS-CUTTING: write unit tests for `EDGE-XXX` cases in `tests/unit/<name>/`.
- FEATURE/CROSS-CUTTING: write contract tests for `NFR-XXX` requirements in `tests/contract/<name>/`.
- **Async event-bus tests:** the bus dispatches queued events to handlers registered *at dispatch time*. So subscribe BEFORE any setup writes, wait for the setup events to be delivered, then clear the collector — so no setup event is in flight when asserting on the operation under test. Never publish setup events and then subscribe (racy).
- Commit the tests: `test(<name>): add acceptance tests` (FEATURE/CROSS-CUTTING) or `test(<name>): add reproduction test` (ISSUE).

### ISSUE: reproduction test (RED)

- Write the reproduction test(s) named in the triage plan.
- The test MUST fail on the current (defective) code — this is RED for the issue.
- The test MUST assert the behavior the spec requires (per the affected `AC-XXX`), not the defective behavior.
- Test names MUST reference the affected `AC-XXX` ID and the issue (e.g., `test_ac_005_valid_request_issue_login-lockout`).
- Run the reproduction tests and confirm RED state.
- Record RED evidence in `docs/verification/<name>.md` using `TDD-evidence-template.md`.
- Update the traceability matrix in `docs/verification/traceability.md` with the issue's test references (affected REQ/AC + reproduction test).

### Test contract sanity check (before confirming RED)

A valid RED is an **assertion failure on behavior that does not yet match the spec** (unimplemented for FEATURE/CROSS-CUTTING, defective for ISSUE) — not an error in test setup. Before confirming RED, verify the test contract is correct. A test that errors in setup is RED for the wrong reason and MUST NOT pass the gate.

- **Failure mode.** Run the suite and inspect each red test. It must FAIL (`AssertionError`) on the unimplemented behavior. If it ERRORS in setup/fixture/collection/import (e.g., `AttributeError` in a helper, a bad import, a fixture collision), that is a broken test contract — fix the test, do not confirm RED.
- **Strategy/domain match.** Every Hypothesis strategy must match the spec's domain (min/max length, value ranges, types). A strategy that generates out-of-domain input (e.g., a 5-char password when the spec requires 8–128) is a contract bug — fix the strategy.
- **Fixture uniqueness.** Setup fixtures must not collide on unique fields (e.g., two users sharing one email in a test that asserts UNIQUE). Give each fixture distinct unique values.
- **Record the failure mode** (assertion vs error) in the RED evidence so the gate is auditable.

## MUST-NOT

- Implement missing behavior.
- Weaken the specification.
- Make tests pass by changing expected behavior.
- Test implementation details at the acceptance layer.
- Modify the spec to fit the tests.
- Skip RED confirmation.
- Commit implementation code.

## Git Responsibilities

Before work:
- Verify the current branch is the change branch.
- Verify the specification is approved (merged PR) (FEATURE/CROSS-CUTTING) or the triage record exists (ISSUE).
- Verify the working tree is clean.

After work:
- Run the RED command.
- Commit the acceptance tests.
- Do not commit implementation code.

Commit:
    test(<name>): add acceptance tests      (FEATURE/CROSS-CUTTING)
    test(<name>): add reproduction test    (ISSUE)

## Verification

- Tests exist and reference `AC-XXX` IDs.
- Tests fail (RED confirmed) before implementation — each as an **assertion failure**, not a setup error (test contract sanity check passed).
- RED evidence recorded (including failure mode per test).
- Traceability matrix updated.
- Tests committed.
