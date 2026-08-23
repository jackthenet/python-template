# Skill: grill

Adversarially interrogate a feature idea to discover ambiguity, hidden requirements, edge cases, conflicting assumptions, and scope boundaries before specification.

## Entry Conditions

- [ ] A feature idea exists (user request, GitHub issue, or problem description).
- [ ] A feature branch exists (created by `feature` skill).
- [ ] No specification exists for this feature yet.

## Input

Feature idea / user request / GitHub issue.

## Output

Feature brief: decisions, scope, actors, out-of-scope, open questions.

## Purpose

The purpose of the grill is to discover ambiguity, hidden requirements, edge cases, conflicting assumptions, and scope boundaries before specification. Not merely to ask questions — to challenge assumptions.

## Dimensions

Adaptively probe based on the feature. Not all dimensions apply every time:

- **GOAL** — What problem are we solving?
- **ACTORS** — Who interacts with it?
- **SCOPE** — What is included? What is explicitly excluded?
- **BEHAVIOR** — What should happen?
- **STATE** — What states exist? What transitions exist?
- **BOUNDARIES** — What are the API/UI/domain boundaries?
- **ERRORS** — What can go wrong?
- **EDGE CASES** — What happens at the boundaries?
- **SECURITY** — Who is allowed to do what?
- **DATA** — What information is created/changed/deleted?
- **INTEGRATIONS** — What external systems are involved?
- **CONCURRENCY** — What happens when operations happen simultaneously?
- **IDEMPOTENCY** — What happens if the same operation occurs twice?
- **PERFORMANCE** — Are there latency/throughput constraints?
- **OBSERVABILITY** — What should be logged/audited?
- **MIGRATION** — Does existing data or behavior need consideration?
- **SCOPE CONTROL** — What are we deliberately NOT building?

## Stopping Condition

Stop when the feature can be expressed as a bounded set of externally observable behaviors with no unresolved decisions that would materially affect architecture, acceptance criteria, or scope.

## MUST

- Challenge assumptions, not just ask questions.
- Probe dimensions adaptively based on the feature.
- Identify actors, scope, boundaries, errors, edge cases.
- Identify what is explicitly out of scope.
- Produce a feature brief with decisions, scope, actors, out-of-scope, open questions.
- Stop when the stopping condition is met.

## MUST-NOT

- Modify the repository (discovery skill only).
- Create commits or repository artifacts.
- Turn a half-baked idea into REQ-001 immediately.
- Ask all dimensions every time (adaptively probe).
- Be merely inquisitive — must be adversarial.

## Verification

- Feature brief produced.
- No open questions that would materially affect architecture, AC, or scope.
- Scope boundaries explicit.
- Out-of-scope items explicit.
