---
name: feature
description: Orchestrates the discovery side of a new feature: creates a feature branch, invokes grill to interrogate the idea, captures a feature brief, invokes specify to write the specification, and opens a PR for human review. Use when starting a new feature from a user request, GitHub issue, or problem description.
---

# Feature

Discover, challenge, scope, and establish a new feature. This skill is the orchestrator of the discovery side.

## Entry Conditions

- [ ] A new feature idea exists (user request, GitHub issue, or problem description).
- [ ] No feature branch exists for this feature yet.

## Input

User request / GitHub issue / problem description.

## Output

- Feature branch `feature/<name>`.
- Feature brief (from `grill`).
- Approved specification at `docs/specs/<feature>.md` (from `specify`).

## Workflow

1. **Initialize Git state:** Create feature branch `feature/<name>` from `main`.
2. **Invoke `grill`:** Adversarially interrogate the feature idea until it is understood.
3. **Capture feature brief:** Record decisions, scope, and open questions.
4. **Invoke `specify`:** Turn the feature brief into a specification.
5. **Commit specification:** `spec(<feature>): add specification`.
6. **Push and open PR:** Submit spec for human review. Do NOT merge.

## Git Responsibilities

Before work:
- Verify working tree is clean.
- Create feature branch from `main`.

After work:
- Commit the specification.
- Push the feature branch.
- Open a PR for human review.
- Do NOT merge the PR.

Commit:
    spec(<feature>): add specification

## MUST

- Create the feature branch before any work.
- Invoke `grill` before `specify`.
- Invoke `specify` after `grill` produces a feature brief.
- Commit the specification.
- Open a PR for human review.

## MUST-NOT

- Skip `grill` and go directly to `specify`.
- Merge the spec PR (human governance).
- Implement code.
- Create repository artifacts before the feature is understood.

## Verification

- Feature branch exists.
- Feature brief captured.
- Specification committed.
- PR opened for human review.
