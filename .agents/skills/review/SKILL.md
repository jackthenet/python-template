---
name: review
description: Reviews code changes against the change's normative basis (spec for FEATURE/CROSS-CUTTING, triage record + affected spec IDs for ISSUE, baseline + scope for REFACTOR, scope for DOCS/CHORE) before reviewing implementation style. Checks traceability, acceptance tests, feature boundaries, and architecture rules. Use when reviewing pull requests, diffs, or code changes for any change type.
---

# Review

Change-type-routed code review: review behavior against the change's normative basis before reviewing implementation style.

## Entry Conditions

- [ ] A pull request or diff exists to review.
- [ ] FEATURE/CROSS-CUTTING: an approved specification exists; acceptance tests exist.
- [ ] ISSUE: a triage record exists; reproduction tests exist.
- [ ] REFACTOR: a GREEN baseline is recorded.
- [ ] DOCS/CHORE: a no-behavior scope is recorded.

## Input

Pull request / diff + the change's normative basis (spec / triage record / baseline + scope / scope) + tests.

## Output

Review findings ordered by severity.

## Review Order

1. **Normative basis** — Does the change implement what the normative basis says? No more, no less (spec for FEATURE/CROSS-CUTTING; affected spec IDs for ISSUE; no behavior change for REFACTOR; no behavior delta for DOCS/CHORE).
2. **Traceability** — Does every `REQ-XXX` map to `AC-XXX` map to executable tests?
3. **Acceptance tests** — Do the tests prove the specified behavior? Are they weakened or orphaned?
4. **Implementation** — Is the code correct, minimal, and within feature boundaries?
5. **Architecture** — Do dependencies respect the feature architecture rules?
6. **Quality** — Lint, type checks, naming, duplication, complexity.
7. **Observability** — Does the feature log meaningfully (entry points, errors, lifecycle) at appropriate levels with useful context? Shared infrastructure features MUST be observable.

## Todo

Per the AGENTS.md Todo Tracking Discipline: mark the Phase 6 item `in_progress` before starting; `completed` only when the review report is clean and the PR is open.

## MUST

- Review behavior against the change's normative basis before reviewing implementation style.
- Check that no acceptance test was modified to make the implementation pass.
- Check that no test was deleted or weakened.
- Check that no unspecified behavior was introduced (FEATURE/CROSS-CUTTING) or that no behavior changed at all beyond the type's contract (ISSUE/REFACTOR/DOCS-CHORE).
- Check that feature boundaries are respected.
- Check that dependencies follow the architecture rules.
- Flag any orphaned tests (tests without spec reference).
- Flag any missing traceability links.
- CROSS-CUTTING: check that the traceability matrix rows of every affected feature are updated.
- ISSUE: check that the fix is minimal and introduces no behavior beyond the affected spec IDs; check that the full regression suite has no new failures.
- REFACTOR: check that the full suite is GREEN with zero test changes and no observable behavior changed.
- DOCS/CHORE: check that no behavior, test, or source-behavior changes are present beyond the scoped non-behavior changes.
- Check that the feature is observable: it logs entry points, errors, and lifecycle events at appropriate levels with useful context (shared infrastructure features MUST be observable).
- When the review is clean and the change is a reusable shared capability, add a short "how to use this" note to `AGENTS.md` (so future changes use it correctly).
- Before opening the PR, bump the version per the change type (ISSUE → `patch`, FEATURE → `minor`, CROSS-CUTTING → `minor`/`major`; no bump for REFACTOR/DOCS-CHORE): run `bump-my-version bump <level>` in the change worktree with a clean working tree; the bump commit is part of the PR (see the "Versioning" section in `AGENTS.md`).
- When the review is clean, open a PR for the change branch to `main` and present it for human review/merge, then STOP (do NOT merge it yourself) — PR creation per the git skill (`.agents/skills/git/SKILL.md`, operation "Create PR").
- After the PR is merged (human governance), perform post-merge cleanup per the git skill (`.agents/skills/git/SKILL.md`, operation "Post-merge cleanup").

## MUST-NOT

- Review implementation style before verifying spec compliance.
- Approve a change that modifies acceptance tests to pass.
- Approve a change that introduces unspecified behavior.
- Approve a change that violates feature boundaries.
- Treat code style as more important than spec compliance.

## Git Responsibilities

This skill does not create commits. It reviews existing PRs/diffs.

Before work:
- Verify the PR/diff exists.
- Verify the change's normative basis is in place (spec approved / triage record / baseline + scope / scope).
- Verify acceptance tests exist (FEATURE/CROSS-CUTTING) or reproduction tests exist (ISSUE).

After work:
- Post review findings as PR comments.
- When the review is clean and the change is a reusable shared capability, document how to use it in `AGENTS.md` (so future changes use it correctly).
- When the review is clean, ensure a PR for the change branch to `main` is open (open one if it isn't) and present it for human review/merge.
- Do NOT merge the PR (human governance).
- After the PR is merged (human governance), perform post-merge cleanup per the git skill (`.agents/skills/git/SKILL.md`, operation "Post-merge cleanup").

## Verification

- All review findings addressed or accepted.
- Normative-basis compliance confirmed.
- Traceability intact.
- Architecture rules respected.
