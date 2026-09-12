# Workflow Examples (concrete, usable)

Concrete examples of the new execution model, so the mechanism is verifiably usable — not just documented. Each example is the exact artifact a run would produce.

## 1. Task-Definition (the orchestrator's launch prompt for one atomic step)

This is the exact launch prompt the orchestrator sends to a step subagent for **S4.2 Implement + confirm GREEN** (the subagent must never have to infer anything):

```text
STEP: S4.2 — Implement + confirm GREEN
OBJECTIVE: Implement the minimum behavior for task T-004 to turn its RED tests GREEN.

CHANGE: mail-service (FEATURE)
WORKTREE: ../python-template_kopie-worktrees/feature/mail-service   (run all commands here)

SKILL: .agents/skills/implement/SKILL.md
  - Section: "2. Green (minimum implementation)" (the S4.2 step)

INPUTS (prior step S4.1 handoff):
  - status: DONE
  - gate: RED confirmed (T-004 tests fail with ModuleNotFoundError)
  - artifacts: tests/acceptance/mail/... (T-004 tests)
  - user answers: none

DONE CRITERIA:
  - T-004 tests PASS 100% (run `uv run pytest tests/acceptance/mail/ -k T-004`)
  - GREEN evidence recorded in docs/verification/mail-service.md
  - ruff clean (`uv run ruff check .`)

REQUIRED HANDOFF:
  step / status / gate / artifacts / ruff / questions / problem / next
```

## 2. Example question entry (matches `AI_Questions.md` format)

```markdown
## Q-1 — Which session expiry for password-reset links?
- **Step:** S1.1 Interrogate — Phase 1
- **Change:** mail-service (FEATURE)
- **Why needed:** The spec must state how long a password-reset email link stays valid, but the request did not say.
- **Context:** The feature sends password-reset emails; the link must carry a token that expires.
- **Question:** How long should a password-reset link stay valid (e.g., 15 minutes, 1 hour)?
- **Answer:** 15 minutes
- **Date:** 2026-09-12
- **Status:** ANSWERED
- **Incorporated:** yes — REQ-007 (reset link validity) in docs/specs/mail-service.md
```

## 3. Example problem entry (matches `docs/workflow/PROBLEMS.md` format)

```markdown
## P-1 — Phase 3 subagent timed out with no committed progress
- **Problem:** The first Phase 3 (Test & RED) subagent hit a network timeout after 33 tool uses and made no committed or uncommitted progress (still in the inspection phase).
- **Step / Phase:** S3.1 Derive tests — Phase 3
- **Change:** mail-service (FEATURE)
- **Duration / iterations:** 1 failed attempt + 1 retry
- **Resolution:** Orchestrator logged the problem, launched a fresh S3.1 subagent (never resumed the stuck one); the retry completed RED.
- **Date:** 2026-09-12
```
