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

## 2. Example question entry (matches the change's `docs/questions/<name>.md` format)

```markdown
## Q-1 — Which session expiry for password-reset links?
- **Step:** P.2 Interrogate — Phase P
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

## 4. Phase P example (a prepared change)

Phase P front-loads ALL human interaction: the TODO file, the answered questions, and the draft spec exist before the workflow starts, so the workflow then runs without waiting for a human (see "Phase P: PREPARE" in `AGENTS.md`).

### 4a. Filled TODO file — `docs/todo/session-audit-log.md`

```markdown
# TODO: session-audit-log

- **Status:** READY
- **Change type:** FEATURE
- **Created:** 2026-10-05
- **Question file:** `docs/questions/session-audit-log.md`
- **Spec:** `docs/specs/session-audit-log.md`
- **Worktree:** `../python-template_kopie-worktrees/feature/session-audit-log` (created at P.4, 2026-10-06)
- **Depends on:** none (session-management and authentication are already merged)
- **Related specs:** `docs/specs/session-management.md`, `docs/specs/authentication.md`, `docs/specs/logging.md`

## Goal (one line)
Record every session lifecycle event (login, logout, revocation, eviction) as an append-only audit record an admin can query per user.

## Why
Admins can see how many sessions a user has, but not what happened to them: a compromised account cannot be reconstructed after the fact, and support tickets about "I was logged out" have no evidence.

## In scope
- An append-only audit record per session lifecycle event (actor, target user, event kind, timestamp, session id).
- A query API filtered by user, event kind, and time range, with pagination.
- Records written by event-bus subscriptions, never by the auth login path itself.

## Out of scope
- Tamper-evident / signed audit chains.
- Retention deletion or archival jobs (a later change).
- Any UI.

## Affected features
New feature: `src/backend/auditlog`; subscribes to `src/backend/authentication` and `src/backend/sessionmanagement` events.

## Constraints and risks
- Must not add latency to the login path: the write happens in the event handler, and a failed audit write must never break the login (Q-2).
- Records must not contain tokens, passwords, or IP addresses beyond what the privacy answer in Q-3 allows.
- Reuses the shared settings registry for retention/limits and the shared logging feature for tracing — no new dependency.

## Acceptance signal (plain language)
After a user logs in, is evicted by the session cap, and logs out, an admin query for that user returns three ordered records naming what happened and when, and the login itself is no slower than before.

## Prep log
| Step | Date | Result |
|---|---|---|
| P.1 Frame | 2026-10-05 | TODO + question file created on `main` (commit 4c1f9a2), `Status: PREPARING` |
| P.2 Interrogate (24 questions) | 2026-10-05 | 24 questions recorded; overlap check: no TODO in `docs/todo/` and no spec in `docs/specs/` covers audit records |
| P.3 Answer (24 answered) | 2026-10-06 | 6 `ask_user_question` rounds; all entries ANSWERED; TODO → `QUESTIONS-ANSWERED` |
| P.4 Draft spec / triage / baseline / scope | 2026-10-06 | worktree created from `main`; `docs/specs/session-audit-log.md` drafted (REQ-001..REQ-014, AC-001..AC-018, INV-001..INV-004, EDGE-001..EDGE-007, NFR-001..NFR-003) |
| P.5 Self-consistency | 2026-10-07 | checklist passed (2 fixes: REQ-009 wording, NFR-002 logging context); TODO → `READY` |
```

### 4b. Filled question file excerpt — `docs/questions/session-audit-log.md`

```markdown
# Questions: session-audit-log

- **Change:** session-audit-log (FEATURE)
- **TODO file:** `docs/todo/session-audit-log.md`
- **Spec:** `docs/specs/session-audit-log.md`
- **Opened:** 2026-10-05
- **Status:** ALL ANSWERED
- **Answer rounds:** 6

## Preparation questions (P.2)

## Q-1 — How long are audit records kept?
- **Step:** P.2 Interrogate — Phase P
- **Why needed:** The spec must state whether the feature owns retention, or only writes records somebody else prunes.
- **Context:** The feature is append-only; `docs/specs/session-management.md` has a `cleanup_expired()` pattern for expired rows, but nothing for history.
- **Question:** Does this change define a retention period for audit records, or is retention out of scope?
- **Answer:** Out of scope for this change — records are kept indefinitely; a later change adds a `auditlog.retention_days` setting and a cleanup method.
- **Date:** 2026-10-06
- **Status:** ANSWERED
- **Incorporated:** yes — Out of Scope section + EDGE-007 in docs/specs/session-audit-log.md

## Q-2 — Must a failed audit write break the session operation that caused it?
- **Step:** P.2 Interrogate — Phase P
- **Why needed:** The write happens in an event handler; the spec must say whether an audit failure is fatal to login/logout.
- **Context:** The event bus isolates handler exceptions (docs/specs/event-bus.md), so a handler failure never reaches the publisher.
- **Question:** If writing an audit record fails, should the login/logout still succeed?
- **Answer:** Yes — the audit write is best-effort; the failure is logged at WARNING and an `AuditWriteFailed` event is published, never propagated.
- **Date:** 2026-10-06
- **Status:** ANSWERED
- **Incorporated:** yes — INV-003, AC-014 in docs/specs/session-audit-log.md

## Q-3 — May an audit record store the client IP and user agent?
- **Step:** P.2 Interrogate — Phase P
- **Why needed:** session-management already captures `user_agent`/`ip` at login; copying them into an indefinitely-retained record is a privacy decision.
- **Context:** Q-1 answered that records are retained indefinitely, which raises the stakes on what they contain.
- **Question:** Which of the captured device fields may the audit record carry?
- **Answer:** `user_agent` and `device_name` yes; raw IP no — store only the truncated /24 prefix.
- **Date:** 2026-10-06
- **Status:** ANSWERED
- **Incorporated:** yes — REQ-006, NFR-002 in docs/specs/session-audit-log.md

## Late questions (Phases 2–6)

## Q-25 — Which permission gates the audit query?
- **Step:** S4.2 Implement + confirm GREEN — Phase 4
- **Why needed:** The spec says "an admin can query" but names no catalog action; the permission catalog is action-based and the task's tests need the exact action id.
- **Context:** T-007 wires the query through the shared enforcement plumbing (ADR-079); `user-roles-permissions` already defines `session.list_all` for the analogous admin read.
- **Question:** Should the audit query reuse `session.list_all` or add an additive `auditlog.query` action?
- **Answer:** Add `auditlog.query` as an additive action registered by `feature_actions.py`; do not widen `session.list_all`.
- **Date:** 2026-10-14
- **Status:** ANSWERED
- **Incorporated:** yes — REQ-011 amended in docs/specs/session-audit-log.md (Changelog v2); T-007 re-run RED→GREEN
```

### 4c. Task-definition launch prompt for **P.2 Interrogate** (no worktree yet)

```text
STEP: P.2 — Interrogate the session-audit-log idea
OBJECTIVE: Adversarially interrogate the idea and record every open question in docs/questions/session-audit-log.md, then return the complete batch in ONE BLOCKED-USER handoff.

CHANGE: session-audit-log (FEATURE)
WORKTREE: none yet — the change worktree is created at P.4. Run this step in the PRIMARY worktree (on main) and write ONLY docs/questions/session-audit-log.md.

SKILL: .agents/skills/specify/SKILL.md
  - Section: "P.2 Interrogate" (Atomic Steps, FEATURE / CROSS-CUTTING)

INPUTS (prior step P.1 handoff):
  - status: DONE
  - gate: docs/todo/session-audit-log.md (Status: PREPARING) and docs/questions/session-audit-log.md (Status: OPEN) exist on main, commit 4c1f9a2
  - artifacts: the change's todo set (Phase P + Phases 1–6 + post-merge cleanup)
  - user answers: none

DONE CRITERIA:
  - >= 20 questions recorded under "## Preparation questions (P.2)" in docs/questions/session-audit-log.md, each with Step / Why needed / Context / Question / Answer: PENDING / Date / Status: PENDING / Incorporated: no
  - overlap checked against every spec in docs/specs/ AND every TODO file in docs/todo/; the result recorded in the handoff
  - handoff status: BLOCKED-USER with the complete batch (never partial batches)
  - nothing else on disk changed; no commit (the orchestrator commits the answers at P.3)

REQUIRED HANDOFF:
  step / status / gate / artifacts / ruff: n/a / questions / problem / next
```

### 4d. Scheduling snapshot (three changes in flight — never idle)

```text
in flight (one worktree + one todo set each; one step subagent at a time, changes interleaved):
  session-audit-log   feature/session-audit-log   WAITING  S1.4 spec approval — PR #212 open, merge not yet reachable from origin/main
                                                        activeForm: "waiting for spec PR merge"
  login-lockout       issue/login-lockout         ACTIVE   S4.2 (T-003) implement + confirm GREEN   <- running now
  search-filters      feature/search-filters      WAITING  S6.4 human merge — PR #208 open

prepared, no phase running yet:
  password-policy     feature/password-policy     READY    Phase 1 S1.4: commit the prepared spec, open the approval PR

next step: pick the next READY change — never idle
```
