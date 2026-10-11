# Questions: notifications

Question file for **one** change, created at **P.1 Frame** from `docs/questions/template.md` and filled in at **P.2 Interrogate**. One file per change.

This is a **planning record, not normative**, and it is the **only** place (besides `docs/todo/`) a workflow step may reach `main` directly (see "Phase P: PREPARE" in `AGENTS.md`). It carries no approval gate — the spec does.

- **Change:** `notifications`
- **Created:** 2026-10-03
- **Status:** OPEN  <!-- OPEN | ANSWERED -->

One entry per question, using the fields below. **P.2** (the Interrogate step) MUST create an entry for every ambiguity, missing requirement, edge case, and scope boundary it identifies — for FEATURE/CROSS-CUTTING, **at least 20**, all in **one** `BLOCKED-USER` batch. The orchestrator presents them (≤ 4 per `ask_user_question` round, most blocking first) and records the answers here at **P.3**.

A late question (Phases 2–6) is appended under "Late questions" with `Step:` set to the step that found it.

---

## Phase P questions (P.2)

| ID | Question (one line) | Blocking |
|---|---|---|
| Q-01 | Event-driven only, an explicit `create()` API, or both? | yes |
| Q-02 | Who owns the event → notification-type mapping: the notifications feature centrally, or each feature in its own `feature_notifications.py`? | yes (escalation verdict) |
| Q-03 | Delivery guarantee: accept at-most-once, add an idempotency key, or build an outbox/retry? | yes |
| Q-04 | Is the SMTP send allowed to run inline on the event bus's single worker thread? | yes |
| Q-05 | Which notification types ship in v1, and which existing events are explicitly exempt? | yes |
| Q-06 | How is the recipient resolved when the event carries no `user_id` — and is a new `usermanagement` read allowed? | yes (escalation verdict) |
| Q-07 | Do per-user channel preferences live in a notifications-owned table or in the settings registry? | yes |
| Q-08 | With no preference row stored, is a channel on or off by default? | yes |
| Q-09 | What exactly does a registered notification type declare, and may types be registered after startup? | yes |
| Q-10 | Which `notifications.*` permission actions exist, and is the event-driven create path permission-enforced? | yes (escalation verdict) |
| Q-11 | Does this change take `Depends on: api-keys`, or ship an in-process read API with the consumer deferred? | yes |
| Q-12 | Is the notification body rendered and stored at creation, or stored as type + context and rendered on read? | yes |
| Q-13 | Does the notifications feature own its `EmailTemplate`s and call `MailService.send_email` (no change to `mail`)? | yes |
| Q-14 | Does notifications depend on the concrete `MailService` or on a structural sender protocol? | yes |
| Q-15 | What happens to a user's notification rows when the user is deleted? | yes |
| Q-16 | Retention and cleanup policy for notification rows (age, batch size, per-user cap)? | yes |
| Q-17 | When the email send fails, what happens to the in-app record, and is the failure recorded? | yes |
| Q-18 | Does the global `notifications.enabled` kill switch suppress record creation or only the email channel? | yes |
| Q-19 | Confirm the `notifications.*` settings inventory (keys, kinds, defaults). | no |
| Q-20 | Confirm the read/mutation API surface and its idempotency + pagination semantics. | yes |
| Q-21 | May an admin read or delete another user's notifications? | yes |
| Q-22 | Are broadcast / role-targeted notifications (e.g. notify all admins) in scope for v1? | no |
| Q-23 | Which events does the notifications feature itself publish (and how is a self-loop prevented)? | no |
| Q-24 | New `NotificationError` hierarchy, or plain `ValueError` like session-management? | no |
| Q-25 | How is "no secret in a notification body" enforced — spec rule + tests, or a runtime guard? | yes |
| Q-26 | Does notifications register a search source (`build_notification_source`) in v1? | no |
| Q-27 | Confirm storage: own SQLite file under `./data/notifications/`, repository ABC + SQLite concrete, own migration. | no |
| Q-28 | Confirm the NFR budgets (creation latency, list latency, email excluded, suite runtime). | no |
| Q-29 | Confirm the test strategy: how the mail dependency is faked, and which invariants get Hypothesis property tests. | no |
| Q-30 | Confirm the classification stays FEATURE (no spec amendment to any existing feature) and the bump is `minor`. | yes |
| Q-31 | What does this change explicitly NOT do — the `notifications` ↔ `mail` / `eventbus` / `backend-api` ownership boundary? | yes (non-goals) |

**Batch state (one `BLOCKED-USER` batch, complete):** **31** entries, every one `Status: PENDING` / `Incorporated: no`, every one carrying a `- **Recommended:**` answer — the FEATURE floor (≥ 20) is met with 11 to spare. Q-31 was appended to **this same** batch by the P.2 completion pass (nothing has been presented to the user yet, so it is not a second batch): **P.3 presents all 31 in one set**, ≤ 4 per round, most blocking first — the leading round is the escalation-verdict cluster **Q-02, Q-06, Q-10, Q-30** (plus **Q-31**, the non-goals question that fixes the spec's out-of-scope section).

---

### Q-01 — Event-driven only, an explicit `create()` API, or both?

- **Step:** P.2 (Phase P)
- **Date:** 2026-10-03
- **Status:** PENDING
- **Incorporated:** no

**Context:** The TODO says notifications are "turned out of existing domain events", but also that "a feature can register a new notification type at startup and get notifications for it without the notifications feature's code changing". Those are two different mechanisms. The repo precedent for reacting to another feature is a subscription inside the consuming feature (ADR-063/ADR-064: `sessionmanagement` subscribes to authentication's `LoginSucceeded` and user-management's `UserPasswordChanged`/`UserDeactivated`/`UserDeleted`; no emitting feature imports session-management).

**Why needed:** It fixes the public API of the feature, who may call it, and whether any other feature has to change at all.

**Options:**
- **A. Event-driven only** — the feature exposes no create API; only registered event subscriptions produce notifications.
- **B. Explicit API only** — features call `create(recipient_id, type_id, context)`; no subscriptions.
- **C. Both** — registration declares `event_type → notification_type`; the generated handlers call an internal `create()` that is also public for direct use and tests.

- **Recommended:** **C.** It is the only option that satisfies the TODO's acceptance signal ("a feature registers a new notification type at startup and gets notifications without the notifications feature changing") while keeping the create path directly testable without an event round-trip — the subscription half is already the house pattern (`src/backend/sessionmanagement/service.py`, ADR-063/ADR-064), and the missing half is measurable: session-management has no create seam, so its tests must publish on a real bus to reach the behavior (`tests/acceptance/sessionmanagement/test_cap_eviction.py:74`).

---

### Q-02 — Who owns the event → notification-type mapping?

- **Step:** P.2 (Phase P)
- **Date:** 2026-10-03
- **Status:** PENDING
- **Incorporated:** no

**Context:** This is the escalation trigger written into the TODO ("escalation candidate → CROSS-CUTTING"). Two established patterns exist:
- **In the consuming feature:** session-management owns its own subscriptions to other features' events (`src/backend/sessionmanagement/service.py`), and the notifications feature would own a `subscriptions.py` listing every event it reacts to. No other feature's package is edited.
- **In the producing feature:** each feature declares its own notification types in a feature-owned module registered from the composition root — the ADR-036 pattern (`feature_settings.py`, `feature_actions.py`) extended by ADR-077 (`search_source.py`: `build_user_source`, `build_file_source`, `build_session_source` live in the *producing* features and are wired in `src/main.py`). Note `docs/specs/search.md` was classified **CROSS-CUTTING** precisely because it also added a method to another feature's repository ABC.

**Why needed:** It decides whether the change touches other features' packages and whether `docs/specs/` for other features must gain IDs — i.e. FEATURE vs CROSS-CUTTING, hence the spec shape (Impact Analysis section), the ADR threshold, the Phase 5 per-feature traceability updates, and the version bump level.

**Options:**
- **A. Notifications owns all mappings** — one module in `src/backend/notifications/`; zero edits to other features' packages.
- **B. Each producing feature owns its `feature_notifications.py`** — additive modules in other packages + `src/main.py` wiring; the notifications feature never changes when a feature adds a type.
- **C. Hybrid** — notifications owns the v1 built-in set; the registration API is public so a feature may add its own later.

- **Recommended:** **A for v1** (fewest files, no other feature's spec or code touched → stays FEATURE, `minor` bump). Choose **B** only if the user wants the "any feature declares its own types" property to be *demonstrated* in v1 — that makes the change CROSS-CUTTING (per-feature impact analysis + per-feature traceability), which is legitimate but strictly more expensive. Measured cost of B on `main`: a new `feature_notifications.py` in each of the **7** packages that publish events (`ls src/backend/*/events.py` → 7) plus 7 `src/main.py` wiring lines, against A's one module in `src/backend/notifications/`.

---

### Q-03 — Delivery guarantee: at-most-once, idempotency key, or outbox/retry?

- **Step:** P.2 (Phase P)
- **Date:** 2026-10-03
- **Status:** PENDING
- **Incorporated:** no

**Context:** The TODO already flags this: "the event bus is asynchronous, best-effort and **at-most-once** (`docs/specs/event-bus.md` NFR-002; handler exceptions are swallowed, INV-001), so a failed notification handler is silently lost — delivery semantics MUST be a spec decision." Verified in `src/backend/eventbus/eventbus.py`: a bounded `queue.Queue(maxsize=max_queue_size)` (default 1000), a **single** worker thread, `put_nowait` → on a full queue the event is **dropped, logged and counted** (REQ-008/REQ-009), and a handler exception is caught and logged (INV-001). Nothing is retried, and nothing survives a process restart.

**Why needed:** It determines whether the feature needs a delivery-status column, a retry path, a dedup constraint, or only an explicit NFR stating the ceiling. It also decides whether "notification was created" can ever be claimed as a guarantee.

**Options:**
- **A. Accept at-most-once** — no retry, no dedup; an NFR/EDGE states that a dropped event or a raising handler means the notification never exists, and the handler logs at `ERROR`.
- **B. A + idempotency key** — the type definition may declare a dedup key (e.g. `(type_id, recipient_id, source_id)` with a unique index), so a duplicate event cannot create two rows.
- **C. Transactional outbox / retry queue** — a persisted pending-delivery state machine re-driven by a scheduler.

- **Recommended:** **A, plus B only if a concrete duplicate source exists** (e.g. `LoginSucceeded` firing twice). **C is out of scope** — `docs/specs/mail-service.md:14` lists "queueing/retry of failed sends" as explicitly out of scope for the mail feature, and building an outbox would be a second dispatch mechanism next to the event bus. Mark the ceiling with a `ponytail:` comment naming the upgrade path (C).

---

### Q-04 — Is the SMTP send allowed to run inline on the event bus's single worker thread?

- **Step:** P.2 (Phase P)
- **Date:** 2026-10-03
- **Status:** PENDING
- **Incorporated:** no

**Context:** Event handlers are synchronous (`subscribe(event_type, handler: Callable[[T], None])`) and are dispatched by **one** worker thread (`_worker_loop` → `_dispatch`). `mail`'s send is a blocking network operation: `SmtpTransportImpl` connects per send with a live `mail.smtp_timeout` setting, and `MailService` is traced with `slow_threshold_ms=5000`. So one slow/hanging SMTP send inside a notification handler stalls **every** event in the process and, with the queue bounded at 1000, can cause other features' events to be dropped.

**Why needed:** It is the single largest operational risk in the change and it decides whether the feature needs its own worker/thread pool — a real architectural addition (ADR + tests).

**Options:**
- **A. Inline, documented** — send from the handler; state the ceiling in an NFR and a `ponytail:` comment (ceiling: one worker thread, SMTP latency stalls global dispatch; upgrade path: feature-owned sender thread).
- **B. Feature-owned sender thread/queue** — the handler only creates the record; a notifications-owned thread performs email sends (new machinery, new ADR, new lifecycle tests).
- **C. Email channel out of scope for v1** — in-app records only; email is a follow-up change.

- **Recommended:** **A** for v1 (the mail feature already bounds the send with `mail.smtp_timeout`, so the stall is bounded), with the NFR and the comment made explicit. Choose **C** if the user would rather not carry the risk at all before an HTTP/API surface exists. Measured: `mail.smtp_timeout` is a registered NUMBER setting with default `30` (`src/backend/mail/feature_settings.py:128`), live-read with a 30 s fallback at `src/backend/mail/feature_settings.py:60`, and handed to `smtplib.SMTP(host, port, timeout=…)` at `src/backend/mail/transport.py:71` (a timeout becomes `MailTransportError("timeout")`, `transport.py:85`) — so the worst-case stall on the bus's single worker is a known, configurable constant, not an unbounded hang. (Corrected at the second completion pass: the earlier citation `src/backend/mail/repository.py:60` names a file that does not exist — `src/backend/mail/` has no `repository.py`.)

---

### Q-05 — Which notification types ship in v1, and which events are explicitly exempt?

- **Step:** P.2 (Phase P)
- **Date:** 2026-10-03
- **Status:** PENDING
- **Incorporated:** no

**Context:** The TODO exempts one event only: "the password-reset flow already emails the user through `mail` (`authentication` REQ-013/REQ-014) — a `PasswordResetRequested` subscription would **double-email**; the spec MUST decide which events are exempt." The full event inventory (from `src/backend/*/events.py`) is:

| Feature | Events (payload fields that identify a user) |
|---|---|
| user-management | `UserCreated(user_id, username, email, roles)`, `UserUpdated(user_id, changed_fields)`, `UserDeleted(user_id, username)`, `UserPasswordChanged(user_id)`, `UserRoleChanged(user_id, old_roles, new_roles)`, `UserDeactivated(user_id, username)` |
| authentication | `LoginSucceeded(user_id, method)`, `LoginFailed(identifier, method)`, `Logout(user_id)`, `PasswordResetRequested(email)`, `PasswordResetCompleted(user_id)`, `PasskeyRegistered(user_id, credential_id)`, `PasskeyDeleted(user_id, credential_id)` |
| session-management | `SessionRevoked(user_id, session_id)`, `AllSessionsRevoked(user_id, excluded_session_id)`, `ExpiredSessionsDeleted(count)`, `SessionsListed(user_id, count)` |
| file-management | `FileUploaded(file_id, key, namespace, size, detected_mime_type)`, `FileDownloaded`, `FileDeleted`, `FileValidationFailed(key, namespace, reason)`, `AvatarUploaded(user_id: str, file_id, url)`, `AvatarDeleted` — **no `user_id` on the file events** |
| mail | `EmailSent(to, template)`, `EmailFailed(to, template, reason)` |
| permissions | `PermissionDenied(user_id, permission, reason)`, `RoleCreated/RoleDeleted/RolePermissionsChanged(role, …)` |
| search | `SourceRegistered/SourceUnregistered(source)`, `SourceQueryFailed(source, reason)` — **no recipient at all** |
| settings | `SettingChanged(key, value, previous)` — **no recipient** |

**Why needed:** The v1 type set is the spec's built-in inventory (REQ/AC + acceptance tests per type); the exempt list is what prevents the double-email defect and the notification-about-a-notification loop. Without an explicit list the spec cannot reach 100% coverage.

**Options:**
- **A. Security-account set (recommended):** `security.password_changed` ← `UserPasswordChanged`, `security.new_login` ← `LoginSucceeded`, `security.account_deactivated` ← `UserDeactivated`, `welcome.account_created` ← `UserCreated`.
- **B. A + operational set:** also `security.passkey_registered`, `security.role_changed`, `files.validation_failed` (needs a recipient decision, see Q-06).
- **C. Minimal:** only `security.password_changed` + `security.new_login`.

- **Recommended:** **A**, and exempt by rule (never by omission): `PasswordResetRequested` (double email), `EmailSent`/`EmailFailed` (loop), `SettingChanged`, `SourceRegistered`/`SourceUnregistered`/`SourceQueryFailed`, `ExpiredSessionsDeleted`, `SessionsListed`, and every file event (no recipient). State the exemption as an EDGE with a test asserting no row is created.

---

### Q-06 — How is the recipient resolved when the event carries no `user_id` — and is a new `usermanagement` read allowed?

- **Step:** P.2 (Phase P)
- **Date:** 2026-10-03
- **Status:** PENDING
- **Incorporated:** no

**Context:** Some events identify a user only by email or identifier: `PasswordResetRequested(email)`, `LoginFailed(identifier, method)`, and mail's `EmailSent(to, …)`. `UserManager`'s public reads are `get_user(user_id)`, `get_user_by_username(username)` and `list_users(include_inactive)` — **there is no public by-email read** (`get_by_email` exists only on `UserRepository`, `src/backend/usermanagement/repository.py`). So resolving email → user would require adding a public read to another feature (an interface change → CROSS-CUTTING, cf. ADR-080 which added `SessionRepository.list_all()` and forced search's spec to gain REQ-028/AC-051).

**Why needed:** It decides whether another feature's public API and spec change (escalation), and it prevents a silent "notify nobody" behavior for email-keyed events.

**Options:**
- **A. Types must declare a recipient extractor; events with no resolvable recipient produce no notification** (and the type is simply not registered for such events). No change to any other feature.
- **B. Add `UserManager.get_user_by_email(email)`** (additive public read, new REQ in `user-management.md`) so email-keyed events can be resolved → CROSS-CUTTING.
- **C. Fan out over `list_users()` and match the email in the notification feature** — no API change, but an O(n) read of every user per event.

- **Recommended:** **A.** Every v1 type from Q-05 carries a `user_id`, so nothing needs email resolution; record B as the upgrade path if an email-keyed type is ever wanted. **C is rejected** — measured on `main`, `get_by_email` exists only on `UserRepository` (`src/backend/usermanagement/repository.py:94` ABC, `:200` SQLite) and never on `UserManager`, so C would re-implement a query user-management already owns, unbounded, per event.

---

### Q-07 — Do per-user channel preferences live in a notifications-owned table or in the settings registry?

- **Step:** P.2 (Phase P)
- **Date:** 2026-10-03
- **Status:** PENDING
- **Incorporated:** no

**Context:** The TODO flags this as a P.2 question: "the settings registry is **not user-scoped** (values are global by `(category, group)`), so per-user channel preferences likely need a notifications-owned table — where they live is a P.2 question." Verified: `SettingsRegistry.get_value(key, principal=…)` has no user dimension (`src/backend/settings/registry.py:130`), values persist to one `values.yaml` per registry, and `docs/specs/settings.md` REQ-018 scopes settings only by `category`/`group`. `principal` appears in the settings API solely for **permission enforcement**, never as a value scope.

**Why needed:** It decides the data model (a second table + migration + repository methods), whether the settings feature is involved at all, and where the isolation invariant lives.

**Options:**
- **A. Notifications-owned table** (`notification_preferences(user_id, type_id, in_app, email)`), created via `SQLModel.metadata.create_all` + an alembic revision.
- **B. Extend the settings registry with a user scope** — a new settings feature capability (amends `docs/specs/settings.md`, CROSS-CUTTING, affects templates/views/persistence).
- **C. Store preferences as a JSON column on a notifications-owned `user_state` row.**

- **Recommended:** **A.** B is a cross-feature architecture change to an approved spec for one feature's need; C loses per-type querying and constraint enforcement. Measured at this pass: `SettingsRegistry.get_value(key, principal: Principal = _SYSTEM_PRINCIPAL)` is `src/backend/settings/registry.py:166` — `principal` is an enforcement argument, not a value scope, so the registry genuinely cannot hold a per-user toggle today (the `:130` cited in Context has drifted; the claim itself holds).

---

### Q-08 — With no preference row stored, is a channel on or off by default?

- **Step:** P.2 (Phase P)
- **Date:** 2026-10-03
- **Status:** PENDING
- **Incorporated:** no

**Context:** The TODO promises "per-user **per-notification-type channel preferences** (in-app / email)". Nothing in the repo defines a default for an un-stored preference; the settings feature's analogue is "persisted value > definition default" (settings REQ-011), and file-management's analogue is "unregistered key falls back to the hardcoded default + a warning".

**Why needed:** It is an acceptance criterion on its own (a brand-new user with no rows must get a defined set of channels), and it decides whether the feature writes default rows at user creation (which would need a `UserCreated` subscription — i.e. preferences and notifications share a handler).

**Options:**
- **A. Per-type default declared at registration** (`default_channels=("in_app",)` or `("in_app","email")`); a user with no row gets the type's default; a stored row overrides it.
- **B. Global default: in-app on, email off** (opt-in email) unless a row says otherwise.
- **C. Global default: both on** (opt-out email).

- **Recommended:** **A**, with `("in_app",)` as the default for every v1 type and email explicitly opted-in per type only where the user asked for it — this keeps "email is sent **only** when that recipient's preference enables the email channel" (TODO acceptance signal) true by construction, and avoids emailing every user the moment the feature is deployed. A is also the only option that needs no new write path: the repo's two existing default mechanisms are "persisted value beats definition default" (settings REQ-011) and "unregistered key falls back to the hardcoded default" (file-management), and both resolve at read time, exactly like A.

---

### Q-09 — What exactly does a registered notification type declare, and may types be registered after startup?

- **Step:** P.2 (Phase P)
- **Date:** 2026-10-03
- **Status:** PENDING
- **Incorporated:** no

**Context:** The TODO requires "an **extensible notification-type registration API** so a feature can add a new notification type at startup without the notifications feature changing". The repo's registration precedents are: `PermissionCatalog.register_feature(feature, actions)` (closed vocabulary, duplicate key → `ValueError`, no runtime creation), `SettingsRegistry.register(SettingDefinition(...))` (duplicate → `SettingsRegistrationError`, ADR-036: registration at startup, no import side effects), and `SearchService.register_source(SearchSource(name, fields, query))` (ADR-077).

**Why needed:** It is the feature's extension contract — the spec section every other feature will read — and it fixes the error behavior for duplicates and unknown types.

**Options:**
- **A. A frozen `NotificationType` model** registered via `register_type(...)`: `type_id` (pattern `^[a-z0-9_-]+\.[a-z0-9_-]+$`, mirroring the catalog key rule), `title_template`, `body_template`, `event_type` (the event class it reacts to), `recipient_extractor`, `default_channels`, `email_template: EmailTemplate | None`, `sensitive: bool`. Duplicate `type_id` → `NotificationTypeRegistrationError`; registration only at startup (a later duplicate is an error, not a silent overwrite).
- **B. Same, but types may also be registered/unregistered at runtime** (needs events + views + a mutable registry, like search's `register_source`/`unregister_source`).
- **C. Minimal:** a plain dict/enum of type ids with templates owned inside the feature (no external registration) — contradicts the TODO's acceptance signal.

- **Recommended:** **A.** Startup-only keeps the vocabulary closed and auditable (catalog precedent) and removes the need for `SourceUnregistered`-style events; runtime registration is YAGNI until a plugin exists. The duplicate-key error to copy is concrete: `PermissionCatalog.register_feature` raises `ValueError` for a key that is malformed, out of scope, or already registered (`src/backend/permissions/catalog.py:48-52`).

---

### Q-10 — Which `notifications.*` permission actions exist, and is the event-driven create path permission-enforced?

- **Step:** P.2 (Phase P)
- **Date:** 2026-10-03
- **Status:** PENDING
- **Incorporated:** no

**Context:** The TODO says "adding `notifications.*` actions is **additive** to the closed catalog (ADR-079 precedent) **but does change the catalog the permissions spec describes** — if `user-roles-permissions.md` must be amended, escalate to CROSS-CUTTING." Evidence that it does **not** have to be amended: ADR-079 added `search.search` through `src/backend/search/feature_actions.py` with no change to the permissions feature's code or spec, and `docs/specs/user-roles-permissions.md` REQ-005 normatively describes *feature-owned* `register_actions` modules. **However**, a new wrinkle exists: every enforced method is checked against the **system principal** when called as `Principal()`, and the system grant set is a hardcoded, migration-seeded list (`BOOTSTRAP_SYSTEM_PERMISSIONS` in `src/backend/permissions/models.py`, seeded by `migrations/versions/d94b7f2e6a31_permissions_tables_and_seeds.py`, default in `SystemPrincipalPermission.permissions`). authentication solves this by **exempting** its internal methods (REQ-024: "the exempt set is the login, session-validation, logout, password-reset and passkey ceremony methods").

**Why needed:** If the event-driven create path is enforced, its action must be added to `BOOTSTRAP_SYSTEM_PERMISSIONS` — a change to another feature's code **and** its seeded data (a new migration), which is a CROSS-CUTTING signal. If it is exempt, nothing outside the notifications feature changes.

**Options:**
- **A. Enforce the user-facing methods only** (`notifications.list`, `notifications.mark_read`, `notifications.delete`, `notifications.manage_preferences`, e.g. `notifications.create` **exempt**), so the internal/event path needs no system grant.
- **B. Enforce everything and add `notifications.create` to `BOOTSTRAP_SYSTEM_PERMISSIONS`** + a seed migration → touches `permissions` code and data.
- **C. No enforcement at all** (no `feature_actions.py`, no `permission_service` injection) — contradicts ADR-071 and the search precedent.

- **Recommended:** **A** — mirrors authentication's exempt set, keeps the change inside one feature (stays FEATURE), and still gives every user-facing operation a catalog action. Also decide whether the actions are added to any role by default (recommend: **no** — the catalog gains keys, roles stay untouched, so no existing user's grants change). Measured cost of B: `BOOTSTRAP_SYSTEM_PERMISSIONS` is a hardcoded `frozenset` at `src/backend/permissions/models.py:99`, so B means editing that set **and** adding a seed migration — a change to another feature's code and data (CROSS-CUTTING).

---

### Q-11 — Does this change take `Depends on: api-keys`, or ship an in-process read API with the consumer deferred?

- **Step:** P.2 (Phase P)
- **Date:** 2026-10-03
- **Status:** PENDING
- **Incorporated:** no

**Context:** The TODO: "**In-app means in-process today.** 'In-app notifications' without any HTTP layer delivers a read API nothing can call from outside the process. If the user wants a browser-visible inbox, this change and `api-keys` become coupled (add `Depends on:` at P.3)." `docs/todo/api-keys.md` already records `Depends on: none (may be depended on by docs/todo/notifications.md)`, and it is scored 5/5 but still `PREPARING` (its own P.2 has not run). Every existing spec is backend-only in-process (`docs/specs/session-management.md`: "Backend-only in-process service — no HTTP/REST layer").

**Why needed:** It changes the schedule (a `Depends on:` edge makes notifications the *second* change in the pair) and the value score (the TODO already docked a point for the missing consumer).

**Options:**
- **A. No dependency** — ship the in-process read/mutation API now; the HTTP surface arrives with `api-keys` and consumes it later.
- **B. Add `Depends on: api-keys`** — notifications waits until the API surface exists, then ships an actually reachable inbox.
- **C. Ship notifications **inside** the api-keys change** as one CROSS-CUTTING change.

- **Recommended:** **A.** The record store, preferences, registration API and mail integration are all independent of transport; deferring them behind an unrelated HTTP decision couples a 4/5 item to a change that has not even been specified. Note the deferred value honestly in the spec's Overview. Refreshed at the completion pass: the HTTP surface is now `docs/todo/backend-api.md` (CROSS-CUTTING, WAITING — split out of `api-keys` at its P.3 round 1, 2026-10-08), and `api-keys`' own P.2 reached the same verdict for this very question ("`notifications` should not take `Depends on: api-keys`", `docs/todo/api-keys.md` prep log, 2026-10-03) — the user still decides.

---

### Q-12 — Is the notification body rendered and stored at creation, or stored as type + context and rendered on read?

- **Step:** P.2 (Phase P)
- **Date:** 2026-10-03
- **Status:** PENDING
- **Incorporated:** no

**Context:** `mail` renders with `{{variable}}` substitution and HTML-escaping, and deliberately does **not** persist sent emails ("no persistence of sent emails or delivery history"). The TODO's data model lists "title/body (**or template reference**)" — undecided. Rendering on read would require storing the raw context (which may contain usernames/emails) and re-rendering with a template that may have changed since.

**Why needed:** It fixes the table columns, the retention/PII story, and whether a template change retroactively alters already-created notifications.

**Options:**
- **A. Snapshot at creation** — store rendered `title` and `body` strings on the row; the row is immutable except `read_at`.
- **B. Store `type_id` + JSON context; render on read.**
- **C. Store both** (context for future re-render, snapshot for display).

- **Recommended:** **A.** Fewer moving parts, no re-render drift, and it keeps the raw event payload out of the store (less PII at rest). Reuses `mail`'s renderer rather than inventing a second one — see Q-13.

---

### Q-13 — Does the notifications feature own its `EmailTemplate`s and call `MailService.send_email` (no change to `mail`)?

- **Step:** P.2 (Phase P)
- **Date:** 2026-10-03
- **Status:** PENDING
- **Incorporated:** no

**Context:** `docs/specs/mail-service.md` D6: "Feature-specific emails. A feature that needs its own email provides its own `EmailTemplate` and calls the core `send_email` — no need to own SMTP logic." `EmailTemplate` is a frozen model with **mandatory** `subject`, `body_html` **and** `body_text` (every message is `multipart/alternative`), and `send_email(to, template, context)` raises `MailTemplateError` on a missing context variable. `mail` has no base-URL setting and does not build links.

**Why needed:** It confirms that no `mail` spec/code change is needed (escalation check), and it forces the decision that every notification email must supply **both** bodies — a real authoring cost per type.

**Options:**
- **A. Notifications owns one `EmailTemplate` per notification type** and calls `MailService.send_email(to, template, context)`; no change to `mail`.
- **B. Add a generic `notification` template to `mail`** (a new built-in template + a new high-level `send_notification_email(...)` on `MailService`) → amends `docs/specs/mail-service.md` → CROSS-CUTTING.
- **C. Notifications builds its own MIME message** — duplicates `mail`, explicitly prohibited by AGENTS.md.

- **Recommended:** **A.** It is the pattern the mail spec prescribes, and it keeps `mail` untouched. If a type declares no `email_template`, its email channel is unavailable and the preference is rejected/ignored (decide which in the spec).

---

### Q-14 — Does notifications depend on the concrete `MailService` or on a structural sender protocol?

- **Step:** P.2 (Phase P)
- **Date:** 2026-10-03
- **Status:** PENDING
- **Incorporated:** no

**Context:** The repo uses structural protocols at feature seams: `EventPublisher` (a `publish(event)` protocol re-declared inside each consuming feature, ADR-062), `PermissionChecker`/`Principal` in `src/backend/shared/principal.py`, and ABCs (`SmtpTransport`, `SessionRepository`, `FileRepository`) as the test seam. `MailService.send_email` is itself permission-enforced (`@requires_permission("mail.send_email")`) and `mail.send_email` **is** in `BOOTSTRAP_SYSTEM_PERMISSIONS`, so a notification handler calling it as the system principal is already allowed. Note also: in `src/main.py` the mail service is constructed as `MailService(permission_service=...)` with **no** `event_bus`, so `EmailSent`/`EmailFailed` are never published in the composition root today.

**Why needed:** It fixes the constructor signature, the test seam, and whether notifications must pass a `principal` when calling mail.

**Options:**
- **A. Depend on the concrete `MailService`** (public API, injected, `None` = email channel disabled) — tests inject a `MailService` built with a fake `SmtpTransport`.
- **B. Depend on a structural `EmailSender` protocol** (`send_email(to, template, context)`) declared inside notifications — a fake is one class, no SMTP machinery in tests.
- **C. Depend on `mail`'s `SmtpTransport`** and build the message in notifications — duplicates mail, rejected.

- **Recommended:** **B** (a one-method protocol in the notifications package, satisfied by the real `MailService`), matching the `EventPublisher` precedent and keeping notification tests free of SMTP. Record the mail call's principal explicitly (system principal, since `mail.send_email` is bootstrap-granted — `src/backend/permissions/models.py:106`). Note the composition-root fact that makes the protocol the cheaper seam: `src/main.py:219` builds `MailService(permission_service=_permission_service)` with **no** `event_bus`, so `EmailSent`/`EmailFailed` are not published today and cannot be relied on as the notification feature's delivery signal.

---

### Q-15 — What happens to a user's notification rows when the user is deleted?

- **Step:** P.2 (Phase P)
- **Date:** 2026-10-03
- **Status:** PENDING
- **Incorporated:** no

**Context:** `UserRepository.delete` **hard-deletes** the user row (`src/backend/usermanagement/repository.py`), and user-management's own tables declare **no foreign keys at all**. A cross-database FK is impossible anyway: each feature keeps its own SQLite file under `./data/` (ADR-056; `data/usermanagement/users.db`, `data/authentication.db`, `data/permissions.db`, `data/filemanagement/storage.db`). Two precedents exist: session-management **subscribes** to `UserDeleted`/`UserDeactivated`/`UserPasswordChanged` and revokes that user's sessions (ADR-064); file-management keeps a dangling mapping and repairs it lazily (EDGE-011: `get_avatar` returns the default and clears the mapping).

**Why needed:** It is an EDGE + invariant (no notification may ever be readable by anyone after its recipient is gone) and it decides whether notifications subscribes to `UserDeleted`.

**Options:**
- **A. Subscribe to `UserDeleted` and delete that user's notifications and preferences** (session-management precedent).
- **B. Keep the rows** (orphaned `user_id`s; reads are always filtered by `user_id`, so nothing is exposed).
- **C. Lazy cleanup** — drop rows for a missing user on read (file-management EDGE-011 style).

- **Recommended:** **A**, plus a retention sweep (Q-16) as the safety net for a dropped `UserDeleted` event (the bus is at-most-once, so A alone is not a guarantee — state that in the spec). A is the exact precedent: ADR-064 is session-management subscribing to `UserDeleted`/`UserDeactivated`/`UserPasswordChanged` and cleaning up that user's rows (`src/backend/sessionmanagement/service.py`), and user-management's tables declare no foreign keys, so nothing else can cascade for us.

---

### Q-16 — Retention and cleanup policy for notification rows (age, batch size, per-user cap)?

- **Step:** P.2 (Phase P)
- **Date:** 2026-10-03
- **Status:** PENDING
- **Incorporated:** no

**Context:** The TODO: "Notification rows grow unbounded — a retention/cleanup policy (compare `sessionmanagement.cleanup_expired()`) is needed." The established shape is `cleanup_expired(*, batch_size: int | None = None) -> int` (session-management REQ-015/REQ-019: bounded batch, `None` = live `sessionmanagement.cleanup_batch_size` default 1000, **application-scheduled**, "no scheduler in this change"), with settings `sessionmanagement.session_ttl` / `cleanup_batch_size`.

**Why needed:** Unbounded growth is the one measurable operational defect of the feature; the answer fixes the API, the settings keys, and the EDGE tests.

**Options:**
- **A. Age-based sweep:** `cleanup_old(*, batch_size=None) -> int` deleting rows older than `notifications.retention_days` (default e.g. 90), application-scheduled, no scheduler in this change.
- **B. A + per-user cap:** keep at most `notifications.max_per_user` (e.g. 500) newest rows per recipient; older ones are deleted at creation time.
- **C. No cleanup** — rows live forever.

- **Recommended:** **A + B.** The cap is what actually bounds the table for an active user (age alone does not, since a busy user can produce >retention rows/day), and both are one `DELETE` each. Read/unread semantics must not be affected by the sweep (deleting an unread row is legal — state it). The shape to copy is already in the tree: `SessionService.cleanup_expired(principal=…)` (`src/backend/sessionmanagement/service.py:325`) is bounded by the live-read `sessionmanagement.cleanup_batch_size` (`feature_settings.py:51`) and is application-scheduled with no scheduler in that change.

---

### Q-17 — When the email send fails, what happens to the in-app record, and is the failure recorded?

- **Step:** P.2 (Phase P)
- **Date:** 2026-10-03
- **Status:** PENDING
- **Incorporated:** no

**Context:** `mail` raises `MailConfigurationError` / `MailTransportError` / `MailTemplateError` and publishes `EmailFailed(to, template, reason)` with `reason ∈ {template, configuration, transport}` — but only when an `event_bus` was injected, which `src/main.py` does **not** do today. The handler's exception is swallowed by the bus (event-bus INV-001), so a raise never reaches the publisher.

**Why needed:** It decides ordering (create-then-send vs. send-then-create), whether the record carries a delivery status, and whether a failed email is visible anywhere.

**Options:**
- **A. Create the in-app record first, then attempt the email; a failed send is logged at `ERROR` and the record stays** (no status column).
- **B. A + a per-row delivery marker** (e.g. `email_failed: bool` or a `delivery_error` string) so the user/operator can see it.
- **C. Skip the in-app record when the email fails** (all-or-nothing) — impossible to roll back cleanly across a network call.

- **Recommended:** **A**, with the failure recorded in the log (structured, secret-free) and an EDGE test. **B** only if the user wants user-visible delivery state — it adds a column, an AC and a test for a state nothing acts on (no retry exists, Q-03). Grounded in the composition root: `src/main.py:219` injects no `event_bus` into `MailService`, so `EmailFailed` is never published today — a log record is the only failure signal that actually exists without a wiring change to `main.py`.

---

### Q-18 — Does the global `notifications.enabled` kill switch suppress record creation or only the email channel?

- **Step:** P.2 (Phase P)
- **Date:** 2026-10-03
- **Status:** PENDING
- **Incorporated:** no

**Context:** The TODO lists feature-owned settings including "a global `notifications.enabled`". Live-read semantics are normative (settings-coverage REQ-003: `set_value` affects a running feature without re-construction), and file-management's live-limit analogue (REQ-021: "a file already **created** while the limit was higher is not retroactively affected") is the precedent for "the switch applies to new work only".

**Why needed:** It is an AC either way, and it decides whether disabling notifications loses data permanently.

**Options:**
- **A. Kill switch stops everything** — no record is created, no email is sent (events are ignored while disabled).
- **B. Kill switch stops only email**; in-app records are still created (a "quiet mode").
- **C. Two switches:** `notifications.enabled` (whole feature) and `notifications.email_enabled` (channel).

- **Recommended:** **A** for the global switch (simplest to reason about: disabled = the feature does nothing), and rely on per-type/per-user preferences for the granular case. Add `notifications.email_enabled` only if the user wants a global email mute (C) — cheap, but it is a second switch to test. Live-read semantics are already normative (settings-coverage REQ-003/AC-004: a `set_value` affects a running feature without re-construction), so neither option needs a restart story — only an AC saying whether rows created while enabled survive a disable.

---

### Q-19 — Confirm the `notifications.*` settings inventory (keys, kinds, defaults).

- **Step:** P.2 (Phase P)
- **Date:** 2026-10-03
- **Status:** PENDING
- **Incorporated:** no

**Context:** settings-coverage REQ-017/REQ-018/REQ-019 require the full key prefix (`<feature>.*`), `category` = domain, `group` = feature name, and a complete inventory in the spec. Existing analogues: `sessionmanagement.session_ttl` + `cleanup_batch_size`; `filemanagement.max_file_size` / `avatar_max_size` / `allowed_types` (LIST) / `avatar_base_url`; `eventbus.max_queue_size`.

**Why needed:** The inventory is a normative table (REQ + AC + a settings-coverage test), and a wrong key name is a spec amendment later.

**Options (proposed inventory):**

| Key | Kind | Default |
|---|---|---|
| `notifications.enabled` | BOOLEAN | `true` |
| `notifications.retention_days` | NUMBER | `90` |
| `notifications.cleanup_batch_size` | NUMBER | `1000` |
| `notifications.max_per_user` | NUMBER | `500` |

- **A. Exactly the four above.**
- **B. The four + `notifications.email_enabled` (BOOLEAN, `true`)** (see Q-18).
- **C. Fewer:** drop `max_per_user` (no cap, age sweep only, see Q-16).

- **Recommended:** **A** (or **B** if Q-18 chooses C) — the four keys follow settings-coverage REQ-017 (full `notifications.*` prefix) and REQ-018 (`category` = `application`, `group` = `notifications`), and this table is exactly what REQ-019's inventory check and the existing contract tests (`test_key_prefix`, `test_category_group`) will assert.

---

### Q-20 — Confirm the read/mutation API surface and its idempotency + pagination semantics.

- **Step:** P.2 (Phase P)
- **Date:** 2026-10-03
- **Status:** PENDING
- **Incorporated:** no

**Context:** Two pagination conventions exist: file-management's `list_files(namespace=None, limit=100, offset=0)` with `limit < 1` or `offset < 0` → `ValueError`; session-management's bounded `list_sessions(token=None, user_id=None, limit=100)` with **no** offset and a documented "no pagination beyond the bounded list" decision. Idempotency precedent: session-management INV-001 — revoking an already-revoked or unknown id is a **no-op**, no event, no error.

**Why needed:** These are the feature's core acceptance criteria (the TODO's signal: "can be listed, marked read and deleted") and the isolation invariant.

**Options (proposed surface):**
```python
list_notifications(user_id, *, unread_only: bool = False, limit: int = 100, offset: int = 0) -> list[NotificationRead]
unread_count(user_id) -> int
mark_read(notification_id, *, user_id) -> None      # idempotent no-op for an unknown/other-user id
mark_all_read(user_id) -> int
delete(notification_id, *, user_id) -> None         # idempotent no-op
```
- **A. As above** (limit/offset like file-management; idempotent no-ops like session-management; a cross-user id is indistinguishable from a missing one, so existence never leaks).
- **B. As above but raising `NotificationNotFoundError`** for an unknown id (leaks existence across users unless carefully worded).
- **C. Bounded list, no offset** (session-management style).

- **Recommended:** **A.** Never-raising, user-scoped mutations are the smallest correct surface and make the isolation invariant (INV: a mutation with `user_id` X can never affect a row owned by Y) directly testable with a property test. Both alternatives are named decisions already in the corpus — ADR-066 ("bounded list, no offset, current session pinned") is option C and ADR-067 ("idempotent revocation, no new exceptions") is the no-op rule; A keeps C's idempotency but takes file-management's `limit`/`offset` pagination (`src/backend/filemanagement/service.py:829`), which an inbox needs and a session list did not.

---

### Q-21 — May an admin read or delete another user's notifications?

- **Step:** P.2 (Phase P)
- **Date:** 2026-10-03
- **Status:** PENDING
- **Incorporated:** no

**Context:** session-management deliberately allows the admin path (`list_sessions(token=None, user_id=...)` requires `sessionmanagement.list_sessions`, which only `admin` has; REQ-002/AC-002), and permissions REQ-011/AC-011 guarantee `admin` holds every catalog action. But notifications contain personal content (login locations, security events), and the TODO's acceptance signal is "no user can read another user's notifications".

**Why needed:** It is the difference between "no user" and "no non-admin user", and it decides whether the read methods take a `principal` and check ownership, or an explicit `user_id` argument.

**Options:**
- **A. Self-only** — the API takes the acting `principal` and derives the recipient from it; no admin read path in v1.
- **B. Self + admin** — an admin holding `notifications.list` may pass an explicit `user_id` (session-management analogue).
- **C. Self + admin, gated by a separate action** (e.g. `notifications.read_any`).

- **Recommended:** **A for v1** (strictest reading of the TODO's signal, no second action, no admin UI consumer exists yet), with B recorded as the extension point. If A is chosen, state explicitly that `admin` does **not** get an exception, because permissions **REQ-010/AC-012** — not REQ-011, as the Context above cites (REQ-011 is "the `user` role starts with zero permissions") — make `admin` an **implicit wildcard over the catalog**: `has_permission` returns `True` for any catalog action, so a `notifications.list` action alone would open every inbox to every admin unless the ownership rule is stated in the spec.

---

### Q-22 — Are broadcast / role-targeted notifications (e.g. notify all admins) in scope for v1?

- **Step:** P.2 (Phase P)
- **Date:** 2026-10-03
- **Status:** PENDING
- **Incorporated:** no

**Context:** Some events have no single recipient but are exactly what an operator would want notified: `PermissionDenied(user_id, permission, reason)`, `SourceQueryFailed(source, reason)`, `EmailFailed(to, template, reason)`. Supporting them needs a recipient fan-out (resolve a role → user ids), which touches `usermanagement.list_users` + the permission service's role model.

**Why needed:** Fan-out changes the data model (one row per recipient vs. one row per event), the creation API (a list of recipients), and the volume/retention math.

**Options:**
- **A. Out of scope** — every notification has exactly one recipient user; multi-recipient needs are N separate rows created by N registrations.
- **B. In scope** — a type may declare a recipient resolver returning many users (e.g. all active admins).

- **Recommended:** **A.** No v1 type from Q-05 needs it, and admin alerting is a different product concept (audit/alerting) that belongs with `api-keys`' audit story, not here. Measured: `PermissionDenied` carries the **acting** `user_id` (`src/backend/permissions/events.py:25`), not an admin audience, so no event in the Q-05 inventory has a natural multi-recipient type.

---

### Q-23 — Which events does the notifications feature itself publish (and how is a self-loop prevented)?

- **Step:** P.2 (Phase P)
- **Date:** 2026-10-03
- **Status:** PENDING
- **Incorporated:** no

**Context:** Every feature publishes lifecycle events (`UserCreated`, `SessionRevoked`, `EmailSent`, `SourceRegistered`, …) best-effort, and the bus dispatches by `isinstance` — so a handler for a base class receives subclass events. The TODO requires "no password-reset token or other secret may appear in a notification body, log record or **event**".

**Why needed:** It fixes the Observability section, and an unguarded `NotificationCreated` subscription is a self-amplification risk (a notification about a notification).

**Options:**
- **A. Publish `NotificationCreated(recipient_id, type_id)` and `PreferencesChanged(user_id, type_id, …)`** only (no body/title content in the event), and never subscribe to the feature's own events.
- **B. No events at all** from this feature in v1.
- **C. Full set** (`NotificationCreated`/`NotificationRead`/`NotificationDeleted`/`PreferencesChanged`) — read/delete events for a feature nothing else consumes.

- **Recommended:** **A.** `NotificationCreated` is the hook an external consumer (future push/webhook) needs; read/delete events have no consumer (YAGNI). State normatively that the feature subscribes to no event it publishes — the precedent for a deliberately small typed event set is ADR-068 (session-management's typed lifecycle events), and the loop risk is real because the bus matches by `isinstance` (`docs/specs/event-bus.md`).

---

### Q-24 — New `NotificationError` hierarchy, or plain `ValueError` like session-management?

- **Step:** P.2 (Phase P)
- **Date:** 2026-10-03
- **Status:** PENDING
- **Incorporated:** no

**Context:** Most features define an exception hierarchy (`UserManagerError`, `AuthenticationError`, `MailError`, `FileManagementError`, `SettingsError`, `SearchError`). session-management deliberately defines **none**: "No new exception types: unknown/invalid tokens are `InvalidSessionError` from authentication; malformed arguments raise `ValueError` (consistent with file-management's pagination `ValueError`)".

**Why needed:** It fixes the errors section and the contract tests; a hierarchy nobody raises is dead code, and a missing one forces callers to catch `Exception`.

**Options:**
- **A. Minimal hierarchy:** `NotificationError` base + `NotificationTypeRegistrationError` (duplicate/invalid type) — nothing else, since reads/mutations are no-ops rather than raises.
- **B. Full hierarchy** (+ `NotificationNotFoundError`, `NotificationPreferenceError`, `NotificationDeliveryError`).
- **C. No new exceptions** (session-management style: `ValueError` for malformed arguments, no-op for unknown ids).

- **Recommended:** **A.** Registration is the only place a caller can genuinely be wrong at startup, and a distinct error type there is what makes a misbehaving feature's wiring fail loudly. Both extremes are precedented: session-management ships **no** hierarchy (ADR-067 "idempotent revocation, no new exceptions") while seven features ship one (`UserManagerError`, `AuthenticationError`, `MailError`, `FileManagementError`, `SettingsError`, `SearchError`, `AuthorizationError`) — A is the middle that matches a feature with exactly one raise site.

---

### Q-25 — How is "no secret in a notification body" enforced — spec rule + tests, or a runtime guard?

- **Step:** P.2 (Phase P)
- **Date:** 2026-10-03
- **Status:** PENDING
- **Incorporated:** no

**Context:** The TODO's acceptance signal: "no password-reset token or other secret appears in a notification body, log record or event." Existing mechanisms: `@logged_class(include_args=False)` on secret-handling classes (authentication, mail), secret-free event payloads (mail's `EmailFailed` carries `reason`, never the body), and test-enforced invariants (authentication INV-004/AC-044: "no log record … contains a password, a raw session token, or a password-reset token"; session-management's `test_no_secret_in_logs`). There is **no** runtime redaction anywhere in the repo.

**Why needed:** It decides whether the spec needs a runtime content check (new machinery, false-confidence risk) or a normative content rule plus tests, and it fixes which classes get `include_args=False`.

**Options:**
- **A. Normative rule + tests:** the type registry's templates are the only content source; a `sensitive: bool` flag forces `include_args=False`-style handling for that type; an invariant test scans log records and stored bodies for token-shaped strings (the authentication/session-management helper pattern).
- **B. A runtime redaction pass** over rendered bodies (pattern blocklist) before storing/sending.
- **C. Rule only, no test.**

- **Recommended:** **A.** A blocklist redactor is a false sense of security and a maintenance burden — measured: no redaction/masking helper exists anywhere in `src/backend/`, and nothing would be maintained by it. The real guarantee is that the context a type may reference is declared at registration, so an undeclared variable simply cannot be rendered (`mail` already raises `MailTemplateError` on an unknown variable — reuse that as the enforcement point). The test pattern to copy is already in the repo, with correct IDs: `tests/acceptance/logging_coverage/test_secret_args.py::test_no_raw_secrets_in_any_log_record` (logging-coverage **AC-015**/REQ-015, sentinel-based), plus authentication **REQ-022/AC-035** (`tests/acceptance/authentication/test_logging.py::test_ac_035_no_secrets_in_log_records`) and session-management **AC-044/AC-045** (`tests/acceptance/sessionmanagement/test_observability.py`). The "INV-004/AC-044" pair cited in the Context above is wrong on `main`: authentication INV-004 is the lockout invariant and AC-044 does not exist in that spec.

---

### Q-26 — Does notifications register a search source (`build_notification_source`) in v1?

- **Step:** P.2 (Phase P)
- **Date:** 2026-10-03
- **Status:** PENDING
- **Incorporated:** no

**Context:** ADR-077's contract: a feature exposes `build_*_source(repository)` in its own package (`src/backend/sessionmanagement/search_source.py` exists) supplying a source name, a field schema over the closed `FieldType` set (`string`/`number`/`boolean`/`datetime`) and a **sync** query function; `src/main.py` registers all three existing sources. Adding one is additive and does not change the search feature.

**Why needed:** It is a scope decision with a real cost (a source module, field schema, permission wiring, tests, a search spec row) for a consumer that does not exist yet (Q-11).

**Options:**
- **A. Out of scope for v1.**
- **B. In scope** — `build_notification_source(repository)` with fields (`type_id`, `title`, `created_at`, `read_at`), registered in `src/main.py`.

- **Recommended:** **A.** Same reasoning as the inbox: nothing can call it yet, and a source with no consumer is untested value. Record it as the natural follow-up. Measured: exactly three sources exist today (`src/backend/usermanagement/search_source.py`, `src/backend/filemanagement/search_source.py`, `src/backend/sessionmanagement/search_source.py`), all registered from `src/main.py`, and none of them has an out-of-process consumer until `backend-api` lands.

---

### Q-27 — Confirm storage: own SQLite file under `./data/notifications/`, repository ABC + SQLite concrete, own migration.

- **Step:** P.2 (Phase P)
- **Date:** 2026-10-03
- **Status:** PENDING
- **Incorporated:** no

**Context:** ADR-020/ADR-056: each feature keeps its own SQLite file under `./data/`, tables bootstrapped by `SQLModel.metadata.create_all` at repository init, plus an alembic revision (AGENTS.md "Using Migrations": a table-schema change MUST add a revision, and a new models module MUST be imported in `migrations/env.py` — currently 4 imports: authentication, filemanagement, permissions, usermanagement). Every repository is an ABC with a SQLite concrete (`SqliteUserRepository`, `SqliteFileRepository`, `SqliteSessionRepository`), with `busy_timeout=5000` on SQLite.

**Why needed:** It fixes the persistence section, the migration list, and the test-isolation story (temp-dir DB per test, like the other features' helpers).

**Options (proposed):**
- **A.** `NotificationRepository` ABC + `SqliteNotificationRepository("sqlite:///./data/notifications/notifications.db")`; tables `notifications` (id, recipient user_id, type_id, title, body, channel flags, created_at, read_at) and `notification_preferences` (user_id, type_id, in_app, email); one alembic revision; models module added to `migrations/env.py`.
- **B. Same tables in the existing `data/usermanagement/users.db`** — rejected (cross-feature persistence dependency, violates ADR-056's "no code dependency").
- **C. In-memory only in v1** — rejected (the TODO's acceptance signal requires records that can be listed later).

- **Recommended:** **A.** It is the shape every existing feature already uses — measured on `main`, `migrations/env.py:15-18` has exactly 4 model-module imports (authentication, filemanagement, permissions, usermanagement), so this change adds a fifth import plus one revision, and ADR-056 already fixes one SQLite file per feature under `./data/` (B would create the cross-feature persistence dependency ADR-056 exists to prevent).

---

### Q-28 — Confirm the NFR budgets (creation latency, list latency, email excluded, suite runtime).

- **Step:** P.2 (Phase P)
- **Date:** 2026-10-03
- **Status:** PENDING
- **Incorporated:** no

**Context:** The P.5 self-consistency checklist requires NFRs to be measurable **and consistent with the suite runtime** ("a per-test budget the suite cannot meet is a finding"), and the logging-context clause ("under logging enabled, AC-XXX measures …"). Existing analogues: session-management NFR-001 ("list of 100 sessions in < 50 ms **under logging enabled** (AC-040)"), NFR-002 ("`cleanup_expired` bounded by `batch_size`"), NFR-003 ("full suite runtime unchanged, < 120 s"); file-management NFR-001/002/003 (same shape).

**Why needed:** Unmeasurable or unmeetable NFRs are the most common P.5 finding in this repo (see `docs/workflow/PROBLEMS.md`), and the email path must be excluded from any latency budget (it is a network call).

**Options (proposed):**
- **A.** `NFR-001` creating a notification (record write, no email) < 50 ms under logging enabled; `NFR-002` listing 100 notifications < 50 ms under logging enabled; `NFR-003` the email path is excluded from latency budgets and bounded only by `mail.smtp_timeout`; `NFR-004` full suite runtime < 120 s.
- **B. Looser:** 100 ms budgets.
- **C. No latency NFRs** (only the suite-runtime NFR).

- **Recommended:** **A**, but the suite-runtime clause must be re-measured at P.4 rather than copied: the `< 120 s` figure quoted from session-management is stale — measured on `main` at this pass, `uv run pytest tests/ -q` → **889 passed, 1 skipped, 1 failed in 271.81 s** (the failure is the pre-existing `tests/acceptance/test_structure_map.py::test_ac_021_committed_map_matches_fresh_render`, unrelated to this change). Keep the 50 ms record-write and list budgets — session-management NFR-001 states the measurement context this spec must reuse (default INFO, synchronous console sink, budgets hold including per-call tracing overhead) — and keep the email path out of every latency budget.

---

### Q-29 — Confirm the test strategy: how the mail dependency is faked, and which invariants get Hypothesis property tests.

- **Step:** P.2 (Phase P)
- **Date:** 2026-10-03
- **Status:** PENDING
- **Incorporated:** no

**Context:** AGENTS.md mandates the shared test tooling (`tests/tooling_test_helpers.py`: `model_factory`, `travel`, `mock_http`) and Hypothesis for invariants; `respx` mocks httpx (irrelevant here — mail uses smtplib), and `mail`'s test seam is the `SmtpTransport` ABC. Existing helpers per feature (`*_test_helpers.py`) plus `tests/{acceptance,unit,integration,contract,property}/<feature>/`.

**Why needed:** The test strategy section must map every AC/INV/EDGE to a test category and function, and a wrong seam means the acceptance tests cannot be written without SMTP.

**Options (proposed):**
- **A.** Acceptance: one per v1 type (event → record for the right recipient; email only when the preference enables it; registration of a new type; isolation; no secret). Property (Hypothesis): recipient isolation over generated (owner, actor, id) triples; preference resolution (stored row overrides type default); retention sweep never deletes a row younger than the cutoff. Unit: registration errors, malformed pagination, exempt events create nothing. Integration: event bus → handler → record → mail fake. Contract: `register_type` signature + `EmailSender` protocol compatibility with the real `MailService`. Mail fake: a recording `EmailSender` (Q-14 B) — no SMTP, no `respx`. Time: `travel(..., tick=True)` for retention.
- **B. Fake at the transport level instead** (`MailService(transport=FakeSmtpTransport())`) — exercises mail's MIME building in notification tests (slower, more coupling).

- **Recommended:** **A.** `tests/tooling_test_helpers.py` exists on `main` (`model_factory` / `travel` / `mock_http`) and 13 feature directories already sit under `tests/property/`, so the property strategies have a home; faking at the `EmailSender` protocol (Q-14 B) keeps SMTP out of the feature's tests while mail's own MIME behaviour stays covered where it is specified (`tests/contract/mail/`), and `respx` genuinely does not apply — `SmtpTransportImpl` uses `smtplib`, not httpx.

---

### Q-30 — Confirm the classification stays FEATURE (no spec amendment to any existing feature) and the bump is `minor`.

- **Step:** P.2 (Phase P)
- **Date:** 2026-10-03
- **Status:** PENDING
- **Incorporated:** no

**Context:** The TODO classifies the change FEATURE with "escalation candidate → CROSS-CUTTING if the impact analysis shows it changes existing features' interfaces". The concrete escalation triggers found during interrogation are: (1) feature-owned `feature_notifications.py` modules in other features (Q-02 B); (2) a new public read on `UserManager` (Q-06 B); (3) a new built-in template / high-level send on `MailService` (Q-13 B); (4) adding `notifications.create` to `BOOTSTRAP_SYSTEM_PERMISSIONS` + a seed migration (Q-10 B); (5) a user scope in the settings registry (Q-07 B). ADR-079 shows that adding a feature's own `feature_actions.py`/`feature_settings.py` and its catalog keys is **additive and does not amend** `user-roles-permissions.md`.

**Why needed:** It fixes the Phase Matrix (Impact Analysis section, ADR threshold, per-feature traceability updates in Phase 5) and the version bump (`minor` for FEATURE; `minor`/`major` for CROSS-CUTTING).

**Options:**
- **A. FEATURE** — all of Q-02 A, Q-06 A, Q-13 A, Q-10 A, Q-07 A hold; no existing spec is amended; bump `minor`.
- **B. CROSS-CUTTING** — at least one trigger above is chosen; the spec gains a per-feature Impact Analysis, ADRs are required (new cross-feature interfaces), Phase 5 updates every affected feature's traceability rows; bump `minor` (no breaking change).

- **Recommended:** **A**, with the spec's Impact Analysis still written informally in the Overview ("touches `mail`, `eventbus`, `usermanagement`, `permissions` read-only / additively; none of their specs change") so the verdict is auditable. Grounded: ADR-079 is the proof that a feature-owned `feature_actions.py` (`src/backend/search/feature_actions.py`) adds catalog keys without touching the permissions feature, and `docs/specs/search.md` became CROSS-CUTTING only because it added a method to another feature's repository ABC — the pattern ADR-080 later repeated for sessions.

---

### Q-31 — What does this change explicitly NOT do — the `notifications` ↔ `mail` / `eventbus` / `backend-api` ownership boundary?

- **Step:** P.2 (Phase P, added at the completion pass)
- **Date:** 2026-10-11
- **Status:** PENDING
- **Incorporated:** no

**Context:** Q-01…Q-30 each decide one item; none states what this change **refuses** to do. Three boundaries are where a notification feature silently grows into a second implementation of something that already exists:
- **`mail`** — `MailService.send_email(to, template, context)`, `EmailTemplate` and the `{{variable}}` renderer already exist, and `docs/specs/mail-service.md` D6 normatively assigns the split ("A feature that needs its own email provides its own `EmailTemplate` and calls the core `send_email` — no need to own SMTP logic").
- **`eventbus`** — dispatch, the single worker thread, the bounded queue and handler isolation already exist (`docs/specs/event-bus.md`, `src/backend/eventbus/eventbus.py`); a notifications-owned outbox, retry loop or sender thread (Q-03 C, Q-04 B) would be a **second dispatcher** in the same process.
- **`backend-api` / `api-keys`** — the HTTP boundary is a separate CROSS-CUTTING change (`docs/todo/backend-api.md`, WAITING, spec PR pending; `docs/todo/api-keys.md` now depends on it). "In-app" here can only mean an in-process read API: measured, `src/frontend/` contains no files, so nothing outside the process can call an inbox in v1.
The TODO already carries an Out of scope list (frontend/UI, push, WebSocket/SSE, SMS, digests, scheduled sending, retries, dead-letter, bounce handling, i18n, the HTTP surface); what is missing is whether the **spec** restates it as normative non-goals plus the three ownership rules.

**Why needed:** Without a normative non-goals section, P.4's REQ set can drift (an outbox here, a template store inside `mail`, a push channel), and Phase 6 review check 6 ("no behavior was introduced that is not represented in the specification") has nothing to check against. It is also the record that the deferred half of the value — the reason the value triage docked a point — is deliberately deferred and owned by another change, not forgotten.

**Options:**
- **A. A normative "Out of scope" section** restating the TODO's list verbatim **plus** three ownership rules: notifications never builds a MIME message or touches SMTP (`mail` owns it — Q-13/Q-14); notifications never owns a queue, worker, retry or scheduler (`eventbus` owns dispatch — Q-03/Q-04); notifications ships no HTTP route, no frontend, no search source, no broadcast fan-out (`backend-api` owns the boundary — Q-11/Q-22/Q-26).
- **B. The TODO's list only** — the reuse decisions stay implicit in the REQs and are discoverable only by reading the code.
- **C. A broader v1** — fold the HTTP inbox and/or the delivery outbox into this change (reclassification per Q-30, strictly larger diff).

- **Recommended:** **A.** It costs one spec section and every rule is checkable against a file that already exists — `src/backend/mail/` owns SMTP/templates/rendering, `src/backend/eventbus/eventbus.py` owns the process's only event worker, and `docs/todo/backend-api.md` owns the boundary — so Phase 6 can verify the rule against code rather than against intent; **C** additionally breaks the FEATURE verdict Q-30 recommends and re-opens the escalation triggers.

### Category coverage

`Q-nn` = an entry in this file (Q-01…Q-31). This change has no "closed from evidence" section, so every reference is a question entry.

| Category | Coverage |
|---|---|
| Classification & Normative Basis (FEATURE vs CROSS-CUTTING, the escalation triggers) | covered (Q-30, Q-02, Q-06, Q-07, Q-10, Q-13) |
| Scope & Goals / non-goals (mandatory) | covered (Q-31, Q-22, Q-26, Q-11, Q-03) |
| Overlap & Sequencing against other changes (mandatory) | covered (Q-11, Q-26, Q-03, Q-28 — see "Overlap check (P.2)") |
| Delivery Semantics & Reliability (at-most-once, inline SMTP, send failure, kill switch) | covered (Q-03, Q-04, Q-17, Q-18, Q-15) |
| Data & State (tables, preferences, snapshot vs. template reference, retention, user deletion) | covered (Q-07, Q-12, Q-15, Q-16, Q-27) |
| Interfaces & Public API (create vs. events, read/mutation surface, registration contract, admin access) | covered (Q-01, Q-09, Q-20, Q-21) |
| Behavior & Edge Cases (v1 type inventory, exempt events, recipient resolution, self-loop) | covered (Q-05, Q-06, Q-08, Q-23) |
| Interfaces to other features (mail seam, eventbus, settings, usermanagement, permissions) | covered (Q-13, Q-14, Q-07, Q-06, Q-10) |
| Configurability (settings inventory, defaults, live reads) | covered (Q-19, Q-18, Q-08) |
| Security & Secrets (no secret in body/log/event, the admin wildcard, catalog actions) | covered (Q-25, Q-21, Q-10) |
| Testing & Acceptance (mail fake, property strategies, no-secret scans) | covered (Q-29, Q-20, Q-25) |
| Traceability & Spec Drift (which approved specs would be amended, catalog growth) | covered (Q-30, Q-10, Q-02) |
| Architecture & Conventions (feature shape, module singleton trio, exceptions, search source, tracing) | covered (Q-24, Q-26, Q-27, Q-23) |
| NFRs & Performance (latency budgets, suite runtime, unbounded growth) | covered (Q-28, Q-16, Q-04) |
| Dependencies & Sequencing (new runtime dependency, predecessor changes) | covered (Q-11, Q-03, Q-26) — no new dependency is at stake: `mail`, `eventbus`, `settings`, `permissions`, `usermanagement` and `logging` are already installed and specified, and Q-03 rejects pulling in a retry library |
| Release & Changelog (bump level, `CHANGELOG.md` entry) | skipped — no question is possible: AGENTS.md Versioning fixes FEATURE → `minor`, and Phase 6 item 10 requires the `CHANGELOG.md` entry. Measured at this pass: `pyproject.toml:4` is **`1.2.0`**, so the bump target is **`1.3.0`** (CROSS-CUTTING would also be `minor` here — nothing breaks). |
| UI / Accessibility | skipped — the change ships no UI: `src/frontend/` contains no files (measured: `find src/frontend -type f` → no output), the TODO lists "Frontend / UI" out of scope, and the only user-visible surface in v1 is an in-process read API (Q-11) plus the email bodies (Q-13). |

---

## Late questions (Phases 2–6)

_(none yet — the orchestrator appends entries here, with `Step:` set to the step that found the question.)_

---

## For P.4 (what the answers change)

- **Escalation verdict (Q-02, Q-06, Q-10, Q-13, Q-07, Q-30, Q-31):** decides whether `docs/specs/notifications.md` is a FEATURE spec or a CROSS-CUTTING spec with a per-feature Impact Analysis, whether ADRs are required, and the bump level. **ADR numbering starts at ADR-087** — the corpus now ends at **ADR-086** (the "ends at ADR-080" note above is stale as of this pass; ADR-082 is the structlog backend, ADR-083/084 the singleton install trio, ADR-085 profiling, ADR-086 the `scripts/` type-checking decision). Per the AGENTS.md ADR threshold (new dependency / new pattern / cross-feature interface), the notification-type registry (Q-01/Q-09) is the one ADR candidate; the storage, settings and catalog wiring follow ADR-056/057/077/079 and need none. Bump: `minor` → **`1.2.0` → `1.3.0`** (`pyproject.toml:4`, measured).
- **Data model (Q-07, Q-12, Q-15, Q-16, Q-27):** two tables (`notifications`, `notification_preferences`), their columns, the alembic revision, and the `migrations/env.py` import addition.
- **Public API (Q-01, Q-09, Q-10, Q-20, Q-21):** the service signature list, the registration model, the enforced method set, and the exempt set.
- **Delivery semantics (Q-03, Q-04, Q-17, Q-18):** the NFR/EDGE set, the `ponytail:` ceiling comment, and whether any delivery-status column exists.
- **Normative inventory (Q-05, Q-19, Q-23):** the built-in type list, the settings inventory, and the published-event list — each becomes REQ/AC/EDGE rows with a test.
- **Test strategy (Q-29):** the test files under `tests/{acceptance,unit,integration,contract,property}/notifications/`, the `notifications_test_helpers.py` module, and the property-test strategies.
- **Schedule (Q-11):** whether `docs/todo/notifications.md` gains `Depends on: api-keys`.

## Overlap check (P.2)

Checked at P.2 (2026-10-03) against all 13 files in `docs/specs/` and all 16 items in `docs/todo/`; **refreshed at the completion pass (2026-10-11)** against the current tree: **16** files in `docs/specs/`, **11** live TODOs in `docs/todo/` (plus 20 archived).

**The reuse decision, stated once:** the **transport** already exists (`src/backend/mail/`: `send_email`, `EmailTemplate`, the `{{variable}}` renderer, SMTP with a live `mail.smtp_timeout`) and the **dispatch** already exists (`src/backend/eventbus/eventbus.py`: bounded queue, one worker, handler isolation). The **notification record, read/unread state, per-user channel preferences and the notification-type registry exist nowhere** — measured: `grep -rni notification src --include=*.py` → **no output**, and `docs/specs/` mentions "notifications" once, only as a sequencing note (`docs/specs/structlog-logging.md:217`). So `notifications` owns exactly those four things and reuses everything else — it is not a second mailer and not a second dispatcher (Q-31).

**Specs — no overlap (no existing spec owns a notification record, read state, or channel preference):** the P.2 claim still holds; the only `docs/specs/` mention is the structlog sequencing note, and the only ADR mention is `ADR-016:26` ("notification, not a delta") plus `ADR-082:35` (sequencing). Adjacent-but-distinct:

| Spec | Relationship | Verdict |
|---|---|---|
| `mail-service.md` | consumed (`send_email`, `EmailTemplate`, `{{variable}}` renderer); owns no notification state | reuse, no amendment (Q-13) |
| `event-bus.md` | the dispatch mechanism; at-most-once + handler isolation constrain the design | reuse, no amendment (Q-03/Q-04) |
| `settings.md` / `settings-coverage.md` | feature-owned `register_settings`, live reads, key prefix/category/group conventions | reuse; **not** a per-user store (Q-07) |
| `user-roles-permissions.md` | catalog keys added via `feature_actions.py` (ADR-079), `Principal`/`@requires_permission` reuse | additive, no amendment (Q-10) |
| `user-management.md` | recipient source (`get_user`), `UserCreated`/`UserDeleted` events | reuse; by-email lookup would be an amendment (Q-06) |
| `authentication.md` | the password-reset email already exists → `PasswordResetRequested` must be exempt; the exempt-set pattern is the model for the create path | reuse, no amendment (Q-05/Q-10) |
| `session-management.md` | the closest structural template (bounded list, idempotent no-op, `cleanup_expired`, no new exceptions, event-driven reactions) | pattern reuse |
| `file-management.md` | limit/offset pagination, live settings reads, dangling-mapping EDGE precedent | pattern reuse |
| `search.md` | ADR-077 additive-source pattern; a notifications source is optional | pattern reuse / optional (Q-26) |
| `logging.md`, `logging-coverage.md` | `@logged_class`/`@logged` policy, `include_args=False`, secret-free records | reuse |
| `structlog-logging.md` | the logging backend swap (ADR-082, MERGED); the only `docs/specs/` file that mentions `notifications` at all, and only as a sequencing note (line 217) | predecessor, satisfied |
| `settings-public-registry-setter.md` | the `get_*`/`set_*`/`reset_*` install trio (ADR-083/084, MERGED PR #81) the notifications module singleton MUST ship, and the private-slot write ban the architecture tests enforce | reuse, no amendment |
| `structure-map.md` | `STRUCTURE.md` must be regenerated in the same commit as this change's new `.py` files (`uv run python scripts/make_map.py --check`) — the gate Q-28 measured failing on `main` | obligation, not overlap |
| `template.md` | the spec template, not a spec | n/a |
| ~~`profiling.md`~~ | **does not exist** — profiling is ADR-085 plus the `logging.profiling_include_arguments` setting (`docs/specs/settings-coverage.md:110`); the row P.2 wrote named a file that is not in `docs/specs/` (measured: 16 files = 15 specs + `template.md`) | corrected at this pass |

**TODOs — overlap findings (refreshed 2026-10-11, all 11 live TODOs):**

| TODO (status) | What it owns vs. what `notifications` owns — finding |
|---|---|
| `backend-api.md` (CROSS-CUTTING, WAITING) | Owns the **HTTP boundary** (FastAPI/uvicorn, session-token auth, the 61-action route mapping). `notifications` owns records, preferences, the type registry and an **in-process** read API. Q-11/Q-31: no dependency edge — the read API is transport-agnostic and the boundary consumes it later. This TODO did not exist at P.2 (2026-10-03); it is the change the P.2 text called "`api-keys`' API surface". |
| `api-keys.md` (FEATURE, WAITING) | Owns machine credentials + audit **and now depends on `backend-api`**. Its own P.2 answered this change's Q-11 from its side: "notifications does **not** depend on api-keys" (`docs/questions/api-keys.md` Q-31). No functional overlap. |
| `composition-root-factory.md` (CROSS-CUTTING, QUESTIONS-ANSWERED) | Owns **where the object graph is built** (`src/main.py` → a factory). `notifications` needs startup wiring (register settings/actions/types, build the service) in exactly that file. No conflict, but the wiring call must be written so a later move is mechanical — the same coordination `docs/questions/backend-api.md` Q-07 records. |
| `startup-settings-registration-gaps.md` (ISSUE, WAITING) | Owns the defect "features whose `register_settings` is not called at startup" (settings-coverage REQ-002/AC-003). `notifications` must call its own `register_settings` from day one so it never joins that defect list; no shared file beyond `src/main.py`. |
| `public-api-import-boundary.md` (REFACTOR, WAITING) | Owns the public-import boundary (`TID251` banned-api guard). `notifications`' public API (`get_notifications`/`set_*`/`reset_*`, errors, events) should be shaped for that guard from the start; no overlap of scope. |
| `tenacity-rich-cachetools.md` (FEATURE, WAITING, 2/5) | **Do not couple.** Its retry/backoff item is the tempting "fix" for Q-03/Q-17, but it is unscheduled; the spec must not assume retry exists (Q-03 C is rejected for the same reason). |
| `python-3.15-upgrade.md` (DOCS/CHORE, WAITING) | Owns the interpreter/CI bump. No overlap; `notifications` writes no version-gated code. |
| `docstrings-tests.md` (DOCS/CHORE, WAITING, 2/5) | Owns test docstrings + one `per-file-ignores` removal. Ordering only: if it lands first, `notifications`' new test files must carry docstrings from day one (cheap); if it lands after, its diff grows by this change's test files. |
| `gitattributes-line-endings.md` (DOCS/CHORE, PREPARING) | Owns the EOL normalization policy. No overlap (this file is LF, measured). |
| `complexipy-scripts.md` (DOCS/CHORE, WAITING, PR #82) | Owns the complexity gate over `scripts/`. No overlap — `notifications` adds no `scripts/` file. |
| `notifications.md` (this change) | Owns: the notification record + read state, per-user per-type channel preferences, the notification-type registry, the event→notification handlers, `notifications.*` settings/actions, and the mail call. Not: SMTP, templates, dispatch, HTTP, frontend. |
| Archived since P.2 (20 files in `docs/todo/archive/`, measured): `structlog-logging.md`, `pyproject-tooling-gaps.md`, `python-3.15.md`, `security-changelog-license.md`, `update-readme.md`, `structure-map.md`, `docs-path-ci-trigger.md`, `spec-interview-protocol.md`, `split-archived-qa.md`, `workflow-docs-nits.md`, `remove-spec-tdd-driver.md`, `value-triage-gate.md`, `track-python-skill.md`, **and** `settings-public-registry-setter.md`, `composition-root-singleton-install.md`, `map-default-drop-shift.md`, `ruff-d-docstrings.md`, `architecture-tests-missing.md`, `session-lookup-unwired.md`, `codecov-coverage-badge.md` | **`structlog-logging` has merged** — the TODO's `Depends on: structlog-logging must land first` is **satisfied** (measured: `docs/specs/structlog-logging.md` and ADR-082 are on `main`, `src/backend/logging/_pipeline.py:23` imports `structlog`, and the TODO sits in `docs/todo/archive/`). `notifications` uses only the public logging API (`@logged_class`, `@logged`, `get_logger`), so it is backend-agnostic. **Four more archived items bind P.4:** `settings-public-registry-setter` (**MERGED**, PR #81, merge commit `2115faa`) owns the `get_*`/`set_*`/`reset_*` singleton trio (ADR-083/084) that `notifications`' module singleton must ship (AGENTS.md "Using the Feature Singletons") and the private-slot guard `public-api-import-boundary` widens; `map-default-drop-shift` (**MERGED**, PRs #79/#80) owns the `scripts/make_map.py` behaviour behind `STRUCTURE.md`, which this change must regenerate in the same commit as its new `.py` files — that is exactly the check Q-28 measured failing on `main`; `ruff-d-docstrings` (**MERGED**) is the change `docstrings-tests` waits on, i.e. the `tests/*` `per-file-ignores` removal that decides whether this change's test files need docstrings from day one; `composition-root-singleton-install` is **DROPPED** (not merged), so the install-trio semantics stand on ADR-083/084 alone and no dropped change's wording may be cited. `architecture-tests-missing` / `session-lookup-unwired` (MERGED) and `codecov-coverage-badge` (DROPPED) and the remaining docs/CI/workflow items have no overlap. |

**In-flight state (re-checked 2026-10-11):** `git worktree list` → the primary (`main`) plus `chore/complexipy-scripts` and `issue/startup-settings-registration-gaps`; `gh pr list` → one OPEN PR (#82, `chore/complexipy-scripts`). Neither touches `src/backend/notifications/` (which does not exist) or the notification concepts, so there is no branch conflict with this change. Both in-flight changes do touch `src/`-adjacent files (`scripts/`, one ISSUE in `src/main.py` wiring) — the `composition-root-factory` + `startup-settings-registration-gaps` + `notifications` collision on `src/main.py` is the only merge-order risk to watch.

### Contract check (completion pass, 2026-10-11)

The batch is consistent with the change's type and the TODO's scope:

- **Type:** every recommendation keeps the change **FEATURE** — none requires amending an approved spec. The five escalation triggers P.2 identified (Q-02 B, Q-06 B, Q-07 B, Q-10 B, Q-13 B) are each recommended **against**, so Q-30 A is the coherent verdict and the bump is `minor` (`pyproject.toml:4` = `1.2.0` → `1.3.0`).
- **TODO In scope** — each item has an owning question: notification records + read/unread (Q-12, Q-20, Q-27), per-user per-type channel preferences (Q-07, Q-08), startup type registration (Q-01, Q-09), event-driven creation (Q-01, Q-05), in-app + email through `mail` (Q-13, Q-14), settings (Q-18, Q-19), retention (Q-16).
- **TODO Out of scope** — restated normatively by Q-31; the HTTP surface (Q-11), the search source (Q-26), broadcast (Q-22), retry/outbox (Q-03), push / SMS / digests / i18n (Q-31).
- **TODO Constraints and risks** — each is carried by at least one question: at-most-once bus (Q-03/04/15/17), settings not user-scoped (Q-07/19), no by-email user read (Q-06), `mail` owns SMTP and authentication already sends the reset email (Q-05/13/14), no consumer for an in-app inbox (Q-11/21/26/31), do not duplicate `mail` or become a second dispatcher (Q-03/13/14/31), do not assume `tenacity` (Q-03), unbounded growth (Q-16/28), no secret in body/log/event (Q-25), the permissions catalog grows (Q-10/21).
- **TODO acceptance signals** — signal 1 ("a feature registers a type at startup and gets notifications without the notifications feature changing"): Q-01/02/09; signal 2 ("a user lists unread notifications, marks them read, sets a per-type channel preference"): Q-07/08/20/27; signal 3 ("a password change produces an in-app notification and, if the user opted in, an email"): Q-05/08/13/14/17.
- **TODO `Depends on:`** — `structlog-logging` is satisfied (it merged; see the overlap table), and the `api-keys` decision is Q-11, whose mirror in `docs/questions/api-keys.md` Q-31 reached the same recommendation.

## Prep log

| Step | Date | Result |
|---|---|---|
| P.1 Frame | 2026-10-03 | TODO + question file created on `main`; type FEATURE (escalation candidate CROSS-CUTTING); todo set created; **value triage 4/5, implement** |
| P.2 Interrogate (30 questions) | 2026-10-03 | 30 questions recorded in one `BLOCKED-USER` batch (≥ 20 floor met); overlap checked against 13 specs + 16 TODOs; 5 concrete CROSS-CUTTING escalation triggers identified (Q-02/06/07/10/13) |
| P.2 Interrogate — completion pass (2026-10-11) | 2026-10-11 | Re-checked against the current P.2 done-criteria. **Floor:** 30 entries already present, each with `Options:` and a recommendation; all 30 recommendations restyled to the `- **Recommendation:**` field the completed files use, and the three bare ones (Q-27/Q-28/Q-29) plus the thin ones given a measured reason. **Added Q-31** (the mandatory non-goals / scope-boundary question — Q-01…Q-30 asked per-item scope but never the global `notifications` ↔ `mail` / `eventbus` / `backend-api` ownership boundary), so the file has **31** entries. Added the mandatory **`### Category coverage`** table (17 rows: 15 covered, 2 skipped with reasons — every `Q-nn` reference checked against the entries). Refreshed the overlap section for the 11 live TODOs (it predated `backend-api`, `composition-root-factory`, `docstrings-tests`, `gitattributes-line-endings`, `public-api-import-boundary`, `python-3.15-upgrade`, `startup-settings-registration-gaps`) and recorded that `structlog-logging` — the TODO's stated predecessor — has merged. Corrected three stale facts P.4 would otherwise inherit: permissions **REQ-010/AC-012** (not REQ-011) is the admin wildcard (Q-21); authentication INV-004 is the lockout invariant and there is no AC-044 in that spec — the secret scans are logging-coverage AC-006/AC-015, authentication REQ-022/AC-035, session-management AC-044/AC-045 (Q-25); the suite-runtime NFR figure is stale — measured `uv run pytest tests/ -q` → **889 passed, 1 skipped, 1 failed in 271.81 s** on `main` (the failure is the pre-existing structure-map check `test_ac_021_committed_map_matches_fresh_render`) (Q-28). **No existing entry's wording, numbering, `Answer:` or `Status:` was changed** — all 31 remain `PENDING`. |
| P.2 Interrogate — second completion pass (2026-10-11) | 2026-10-11 | Re-audited the P.2 done-criteria against the current tree. **Floor/batch:** 31 entries, all `PENDING`, one batch — verified by script (31 `### Q-nn` headings, 31 `Status: PENDING`, 31 `Incorporated:`, 31 recommendation fields, no gaps). **Field name normalised:** `- **Recommendation:**` → `- **Recommended:**` on all 31 entries — the name `docs/questions/template.md` and AGENTS.md use and the name 7 of the 9 other question files use (`backend-api.md` still uses `Recommendation:`; that file is not this change's to touch), so the field is now grep-findable by the P.3 check. **Added the missing `- **Date:**` line to every entry** (Q-01…Q-30 → 2026-10-03, the P.2 batch commit `84534ff`; Q-31 → 2026-10-11, commit `0b3f491`) — the template's entry format requires it and the file had none. **Category coverage table:** already present (17 rows, 15 covered / 2 skipped with reasons) — re-verified by script: all 31 `Q-nn` references resolve to real entries and every entry is cited at least once. **Non-goals question:** Q-31 ✓. **Overlap check re-run:** `docs/specs/` = 16 files (15 specs + template), `grep -rniE "notification|inbox|in-app|broadcast|alerting" docs/specs/*.md` → **one hit only**, the `structlog-logging.md:217` sequencing note, so **no approved spec covers notification/inbox/alert/in-app messaging behavior**; `docs/todo/` = 11 live TODOs + 20 archived, none of which owns a notification record, read state, channel preference or type registry — the nearest are `backend-api` (the HTTP boundary this change refuses, Q-31) and `api-keys` (whose own Q-31 already answered this change's Q-11 from the other side). Refreshed the archived-TODO row for the four merged/dropped items that bind P.4 (see the table). **One bad citation fixed:** Q-04 cited `src/backend/mail/repository.py:60`, a file that does not exist — replaced with `feature_settings.py:60` + `transport.py:71`. Spot-checked the other measured citations in the recommendations: `permissions/models.py:99` (`BOOTSTRAP_SYSTEM_PERMISSIONS`) and `:106` (`mail.send_email`), `main.py:219` (`MailService(permission_service=…)`), `settings/registry.py:166` (`get_value(key, principal=…)`), `usermanagement/repository.py:94`/`:200` (`get_by_email` on the repository only), `permissions/catalog.py:47-52`, `sessionmanagement/service.py:325`, `sessionmanagement/feature_settings.py:51`, `filemanagement/service.py:829`, `migrations/env.py:15-18` (4 model imports), `pyproject.toml:4` (`1.2.0`), `src/backend/*/events.py` → 7, `find src/frontend -type f` → empty, `grep -rni notification src --include=*.py` → empty — **all confirmed**. **Spec-overlap table corrected:** it listed `profiling.md`, which is not in `docs/specs/` (profiling is ADR-085 + the `logging.profiling_include_arguments` setting), and omitted three files that are — `structlog-logging.md`, `settings-public-registry-setter.md` (the install trio this change's singleton must ship) and `structure-map.md` (the `STRUCTURE.md` regeneration obligation); the table now covers all 16 `docs/specs/` entries. No answer was invented; all 31 entries stay `PENDING`. |
| P.3 Answer (<n> answered) | | |
| P.4 Draft spec + create branch/worktree | | |
| P.5 Self-consistency | | |
