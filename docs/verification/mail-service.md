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

## Phase history

| Phase | Status | Evidence |
|-------|--------|----------|
| 0 Classify | DONE | this file |
