# Verification: mail-service

## Phase 0 — Classification

- **Change name:** `mail-service`
- **Change type:** `FEATURE`
- **Branch:** `feature/mail-service`
- **Worktree:** `../python-template_kopie-worktrees/feature/mail-service`
- **Scope:** Backend only. The mail-service feature has both backend and frontend
  components; this workflow implements the backend exclusively. The frontend is
  implemented separately in another workflow.

### Rationale (FEATURE, not CROSS-CUTTING)

The change is a **single new feature** — a central mail-service that is a
*provider* other features consume. It does not restructure, modify, or span
existing features:

- It **consumes** the existing shared capabilities (settings, logging, event
  bus) through their public APIs; it does not modify them.
- It **does not** modify the user-management or authentication features, and it
  does not create duplicate configuration, user, authentication, or email
  functionality.
- "Password-reset emails for the authentication system" and "email
  verification emails" are delivered as **reusable high-level operations** of
  the mail service (template + send), not as modifications to the
  authentication feature.

All changes are isolated to this backend feature (new `src/backend/mail/`
package, its tests, its spec, and its verification/traceability records).

## Phase 1 — Specify (FEATURE)

- **Status:** DONE (spec committed; PR open for human approval).
- **Artifact:** `docs/specs/mail-service.md` (the single kept artifact; the
  feature brief from adversarial interrogation is folded into it — no separate
  `.brief.md`).
- **PR:** https://github.com/jackthenet/python-template/pull/22 (head
  `feature/mail-service`, base `main`). Awaiting human review/merge (human
  governance) — NOT merged.
- **Normative basis:** 17 REQ (REQ-001..REQ-017), 19 AC (AC-001..AC-019),
  5 INV (INV-001..INV-005), 10 EDGE (EDGE-001..EDGE-010), 5 NFR
  (NFR-001..NFR-005).
- **Self-consistency checklist:** passed (configurability, parameter coverage,
  REQ↔AC wording, terminology, test-strategy coverage, ID references, scope
  consistency, performance budget vs. observability).
- **Design decisions (WHAT; WHY → ADRs in Phase 2):** D1 SMTP transport
  abstraction (`SmtpTransport` ABC + smtplib default), D2 templates
  (`EmailTemplate`), D3 secure `{{variable}}` substitution (no Jinja2), D4 core
  send, D5 high-level operations, D6 feature-specific emails, D7 live settings,
  D8 `MailError` hierarchy, D9 events, D10 observability, D11 validation, D12 no
  persistence, D13 independence.

## Phase 2 — Decompose (FEATURE)

- **Status:** DONE (ADRs created; task DAG committed and initialized).
- **Spec approval:** verified — `docs/specs/mail-service.md` merged into `main` (PR #22; `git log main -- docs/specs/mail-service.md` non-empty).
- **ADRs** (WHY, not WHAT; continuing the ADR-042 sequence):
  - `docs/decisions/ADR-043-smtp-transport-abstraction.md` — D1: `SmtpTransport` ABC + smtplib-backed `SmtpTransportImpl`; the service references only the ABC (test seam, swappable backend).
  - `docs/decisions/ADR-044-secure-variable-substitution.md` — D3: small, secure `{{variable}}` substitution with HTML-escaped values instead of Jinja2 (no new dependency, XSS-safe, deterministic).
  - `docs/decisions/ADR-045-mailerror-hierarchy-secret-free-reasons.md` — D8: `MailError` + `MailConfigurationError` / `MailTransportError` / `MailTemplateError` with secret-free reason strings; the kind maps to `EmailFailed.reason`.
  - `docs/decisions/ADR-046-per-send-transport-independence.md` — D13 (+D12): the transport is created per send, no long-lived connection, no per-send mutable state, no persistence (failure isolation, thread safety without locks).
  - `docs/decisions/ADR-047-include-args-false-slow-threshold-5000.md` — D10: `@logged_class(slow_threshold_ms=5000, include_args=False)` — tokens/recipient never in log records; no false slow warnings for network-dependent sends.
  - Decisions folded into existing ADRs: D7 live settings (ADR-037 + ADR-036 registration pattern), D9 structural publisher (ADR-021), D11 two-tier validation (ADR-023 pattern); D2/D4/D5/D6 are captured in the task DAG implementation steps.
- **Task DAG:** `docs/tasks/mail-service.tasks.json` — 6 tasks (T-001 .. T-006):
  - T-001 errors, templates, models, secure rendering, message building (REQ-007/008/009/017; AC-008/009/010/019; INV-001/002; EDGE-001/002/003)
  - T-002 settings registration + live config resolution (REQ-001/002; AC-001/002/003)
  - T-003 `SmtpTransport` ABC + `SmtpTransportImpl` (REQ-011; EDGE-005/006/007/008)
  - T-004 `MailService` core `send_email` + events + tracing (REQ-003/006/010/011/012/013; AC-004/007/011/012/013/014/015; EDGE-004/009/010; INV-003/004/005)
  - T-005 high-level operations (REQ-004/005; AC-005/006)
  - T-006 cross-cutting: concurrency, performance, secrets, public API, tracing (REQ-014/015/016; AC-016/017/018; NFR-001..005)
- **Coverage:** every REQ (REQ-001..REQ-017) and every AC (AC-001..AC-019) is covered by at least one task; all 39 test functions from the spec's test strategy (19 AC + 5 INV + 10 EDGE + 5 NFR) are assigned to tasks; task dependencies form a DAG (T-001/T-002 → T-003 → T-004 → T-005 → T-006).
- **Build environment:** `docs/tasks/mail-service.tasks.json` copied to `.github/task-runner/tasks.json` (active build environment initialized).

## Phase history

| Phase | Status | Evidence |
|-------|--------|----------|
| 0 Classify | DONE | this file |
| 1 Specify | DONE | `docs/specs/mail-service.md` + PR #22 (this file) |
| 2 Decompose | DONE | ADR-043..047 + `docs/tasks/mail-service.tasks.json` + `.github/task-runner/tasks.json` (this file) |
