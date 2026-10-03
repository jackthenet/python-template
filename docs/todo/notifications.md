# TODO: notifications

Backlog item for one planned change, created at **P.1 Frame** from this template and named `notifications.md`. One file per change.

This is a **planning record, not normative**: like `docs/questions/`, it is committed directly to `main` (see "Phase P: PREPARE" in `AGENTS.md`). It carries no approval gate — the spec does.

- **Status:** WAITING  <!-- PREPARING | QUESTIONS-ANSWERED | READY | IN-WORKFLOW | WAITING | MERGED -->
- **Change type:** FEATURE  <!-- escalation candidate → CROSS-CUTTING if P.2 impact analysis shows it changes existing features' interfaces -->
- **Created:** 2026-10-03
- **Question file:** `docs/questions/notifications.md`
- **Spec:** `docs/specs/notifications.md`
- **Worktree:** <created at P.4> `../python-template_kopie-worktrees/feature/notifications`
- **Depends on:** `docs/todo/structlog-logging.md` **must land first** (its Q-20, decided 2026-10-04: the loguru → structlog swap is accepted, so this change's new code uses the winning backend from day one). `docs/todo/api-keys.md` is a possible predecessor, not a required one.
- **Related specs:** `docs/specs/mail-service.md` (sending), `docs/specs/event-bus.md` (dispatch), `docs/specs/settings.md` (global prefs), `docs/specs/user-management.md` (recipients), `docs/specs/user-roles-permissions.md` (enforcement + catalog actions), `docs/specs/logging.md` (tracing)

## Goal (one line)
A single notification feature that turns backend domain events into **in-app and email notifications** with **per-user preferences** and **extensible notification types**.

## Why
The backend already emits a rich, typed event stream — `UserCreated`/`UserPasswordChanged`/`UserDeactivated` (user-management), `LoginSucceeded`/`Logout`/`PasswordResetRequested` (authentication), `EmailSent`/`EmailFailed` (mail), `SettingChanged` (settings), `PermissionDenied` (permissions), `FileUploaded`/`AvatarDeleted` (file-management), `SourceQueryFailed` (search) — and `backend.mail` already owns SMTP, templates and `{{variable}}` rendering. What does **not** exist is anything that turns those events into something a user can see later: `grep -rni notification docs src --include=*.md --include=*.py` returns exactly one incidental hit (`docs/decisions/ADR-016-settingchanged-event-integration.md:26`, "notification, not a delta"). There is no notification record, no read/unread state, no per-user channel preference, and no way for a feature to declare "I have a new kind of thing worth telling the user about". Without it, every future "tell the user X" need hand-rolls its own store + mail call + read-state, and the mail feature gets used as a notification bus it was never scoped to be.

## In scope
- A new backend feature `src/backend/notifications/` (name confirmed at P.2) with a use-case service, SQLModel/SQLite storage, repository ABC + SQLite implementation, constructor DI, module singleton + `reset_*()` — the established feature shape (session-management is the closest template).
- **Notification record**: type, recipient user id, title/body (or template reference), channel, created_at, read_at/unread flag; list with pagination, mark-read, mark-all-read, delete; per-recipient isolation.
- **Channels**: (a) *in-app* — the stored record is the delivery surface (an in-process read API; all existing specs are "no HTTP layer"); (b) *email* — delegated to `backend.mail.MailService.send_email(to, template, context)` with a feature-owned `EmailTemplate`; no SMTP code here.
- **Preferences**: per-user, per-notification-type channel toggles (in-app on/off, email on/off), with a safe default per type. Where they live (own table vs. settings registry) is a P.2 question — the settings registry is **global**, not user-scoped, so it probably cannot hold them.
- **Extensible types**: a registration API (`register_notification_type(definition)` / `register_feature_types(...)`) mirroring feature-owned `register_settings` / `register_actions`, so another feature declares a type + its template + default channels at startup **without editing the notification feature**; plus the event-bus subscription path that turns a domain event into a notification.
- Feature-owned `register_settings(registry)` (e.g. `notifications.enabled`, retention) and `register_actions(catalog)` (e.g. `notifications.list`, `notifications.mark_read`, `notifications.manage_preferences`), enforced via the shared `Principal` / `@requires_permission` plumbing (ADR-070/071).
- Typed events (`NotificationCreated`, `NotificationRead`, …), an `NotificationError` hierarchy, `@logged_class` tracing with `include_args=False` where content is sensitive, alembic migration for the new tables.

## Out of scope
- **Frontend / UI** — `src/frontend/` is empty; no rendering layer exists to build against.
- Push, WebSocket/SSE streaming, SMS, desktop or mobile channels.
- Digests, scheduled/deferred sending, delivery retries, dead-letter queue, bounce handling.
- i18n / localization / per-user locale and timezone.
- The HTTP/API surface and API keys — separate change (`docs/todo/api-keys.md`).
- Re-specifying mail delivery (mail-service owns it) or authentication's reset flow.

## Affected features
New feature: `src/backend/notifications/`. Consumed **unchanged**: `src/backend/mail`, `src/backend/eventbus`, `src/backend/settings`, `src/backend/usermanagement`, `src/backend/permissions`, `src/backend/logging`, `src/backend/shared` (Principal). Startup wiring in `src/main.py` (registration + source registration, like the other features).

## Constraints and risks
- **Delivery semantics.** The event bus is best-effort and isolates handler errors (`docs/specs/event-bus.md`); a handler exception never reaches the publisher. So notification creation is at-most-once unless the spec defines a retry/idempotency key — a real P.2 question, not an implementation detail.
- **Double-notifying the reset flow.** authentication + mail already deliver the password-reset token (`authentication.md` changelog v2, `mail-service.md`). A naive `PasswordResetRequested` → notification subscription would email the user twice. The exempt set must be explicit.
- **Preferences are per-user; the settings registry is not.** `docs/specs/settings.md` scopes settings by (category, group) globally. Reusing it for per-user toggles would be a spec-level stretch → prefer a notifications-owned table, and say so in the spec.
- **Secrets and content.** Notification bodies may contain emails, file names, tokens handed to the user. `include_args=False` and non-sensitive events are mandatory (authentication NFR-002 pattern); a reset token must never be copied into a notification body.
- **Catalog growth.** New `notifications.*` actions change the closed catalog (`user-roles-permissions.md` REQ-004/REQ-005) and the bootstrap/system sets — that is an additive change to another feature's spec table; if P.2 finds it requires amending that spec, escalate to CROSS-CUTTING.
- **Unbounded growth.** Notification rows accumulate → retention/cleanup policy (compare `sessionmanagement.cleanup_expired()`).
- **In-app means in-process today.** "In-app notifications" without any HTTP layer delivers a read API nothing can call from outside the process. If the user wants a browser-visible inbox, this change and `api-keys` become coupled (add `Depends on:` at P.3).

## Value triage (2026-10-03, pre-workflow)
- **Overlap:** the *transport* already exists (`backend.mail`: templates, `{{var}}` rendering, SMTP, `EmailSent`/`EmailFailed`) and the *dispatch* already exists (`backend.eventbus`); the *record, read-state, preferences and type registry* exist nowhere. So the right shape is a thin feature that **reuses mail + eventbus** and owns only what is missing — not a second mailer.
- **Beneficiary:** the end user (things they must know stop being trapped in log files) and every future feature, which gets one registration call instead of its own notification code.
- **Score: 4/5** — clear, new user value and it prevents predictable duplication; docked one point because "in-app" has no consumer until an API/frontend exists, so part of the value is deferred.
- **Recommendation: implement** (after P.2/P.3 settle delivery semantics, preference storage, and whether it depends on `api-keys`).

## Acceptance signal (plain language)
A domain event (e.g. a user is created) results in a notification record for the right recipient that can be listed, marked read and deleted; the same event sends an email **only** when that recipient's preference enables the email channel, and the mail send goes through the mail feature (no SMTP code in notifications); a feature that registers a new notification type at startup gets its notifications without the notification feature's code changing; a user can never read another user's notifications; no password-reset token or other secret ever appears in a notification body, a log record or an event.

## Prep log
| Step | Date | Result |
|---|---|---|
| P.1 Frame | 2026-10-03 | TODO + question file created on `main`; type FEATURE (escalation candidate CROSS-CUTTING); todo set created; **value triage 4/5, implement** |
| P.2 Interrogate (30 questions) | 2026-10-03 | **BLOCKED-USER** — 30 questions in one batch (FEATURE floor ≥ 20 met), all with evidence, options and a recommendation. Interrogation found the bus's real limits (bounded single-worker queue, drop-on-full, swallowed handler errors) and verified the settings registry has **no** user scope (`registry.py:130`), so preferences need a notifications-owned table. **Classification finding:** the TODO's claim that adding `notifications.*` catalog actions forces CROSS-CUTTING is contradicted by ADR-079 (`search.search` was added via a feature-owned `feature_actions.py` with no permissions change) — with the recommended answers the change stays **FEATURE**; the real escalation triggers are Q-02/Q-06/Q-07/Q-10/Q-13 |
| P.3 Answer (<n> answered) | | |
| P.4 Draft spec + create branch/worktree | | |
| P.5 Self-consistency | | |
