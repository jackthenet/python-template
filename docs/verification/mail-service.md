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

## Phase history

| Phase | Status | Evidence |
|-------|--------|----------|
| 0 Classify | DONE | this file |
| 1 Specify | DONE | `docs/specs/mail-service.md` + PR #22 (this file) |
