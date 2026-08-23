# Skill: review

Spec-driven code review: review behavior against the specification before reviewing implementation style.

## Entry Conditions

- [ ] A pull request or diff exists to review.
- [ ] An approved specification exists for the feature.
- [ ] Acceptance tests exist for the feature.

## Input

Pull request / diff + spec + tests.

## Output

Review findings ordered by severity.

## Review Order

1. **Specification** — Does the change implement what the spec says? No more, no less.
2. **Traceability** — Does every `REQ-XXX` map to `AC-XXX` map to executable tests?
3. **Acceptance tests** — Do the tests prove the specified behavior? Are they weakened or orphaned?
4. **Implementation** — Is the code correct, minimal, and within feature boundaries?
5. **Architecture** — Do dependencies respect the feature architecture rules?
6. **Quality** — Lint, type checks, naming, duplication, complexity.

## MUST

- Review behavior against the specification before reviewing implementation style.
- Check that no acceptance test was modified to make the implementation pass.
- Check that no test was deleted or weakened.
- Check that no unspecified behavior was introduced.
- Check that feature boundaries are respected.
- Check that dependencies follow the architecture rules.
- Flag any orphaned tests (tests without spec reference).
- Flag any missing traceability links.

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
- Verify the specification is approved.
- Verify acceptance tests exist.

After work:
- Post review findings as PR comments.
- Do NOT merge the PR (human governance).

## Verification

- All review findings addressed or accepted.
- Spec compliance confirmed.
- Traceability intact.
- Architecture rules respected.
