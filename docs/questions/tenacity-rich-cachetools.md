# Questions: tenacity-rich-cachetools

Question file for one change, created at **P.1 Frame** from `template.md` and fully answered at **P.3 Answer**. One file per change — questions are never recorded in a central file.

Committed directly to `main` (like `docs/todo/`); it is a planning record, not normative, and carries no approval gate. Each entry: the question, the generating step, why it is needed, the context at the time, the answer, the date/status, and whether the answer has been incorporated.

- **Status:** OPEN  <!-- OPEN | ANSWERED -->
- **Answer rounds:** 0

## Preparation questions (P.2)

**P.2 Interrogate — 2026-10-05.** **33 questions**, one decision each, most blocking first. The item was **kept** by the user on 2026-10-04 after a 2/5 "decline all three" recommendation, so this batch does **not** re-litigate whether a consumer exists today — it interrogates **what a real consumer would need** for each package, with a decline option left open on each.

Measured consumer inventory (re-measured 2026-10-05; unchanged from the TODO's `Why` table):

| Probe | Result |
|---|---|
| `httpx` call sites in `src/` | **zero** — `grep -rn "httpx" src` matches only `src/python_template.egg-info/requires.txt:4` |
| Cache layer in `src/` | **none** — the only `cache` occurrence in `src/**/*.py` is `cache_ok = True` (`src/backend/usermanagement/models.py:37`, a Pydantic/SQLModel config flag); no memoization, no TTL/LRU layer, no `cachetools` import anywhere |
| CLI / reporting surface | **none** — `src/main.py` is the composition root only (settings registration, `setup_logger`, service wiring); `scripts/` holds 3 CI helper scripts |
| The one real external call | **SMTP over `smtplib`** — `src/backend/mail/transport.py:37` `SmtpTransportImpl`, not HTTP |
| `uv run deptry .` today | `Scanning 89 files... Success! No dependency issues found` — 83 `src/` + 3 `migrations/` + 3 `scripts/` `.py`; `tests/` is in deptry's `DEFAULT_EXCLUDE` (`.venv/Lib/site-packages/deptry/cli.py:25`) |

Overlap check (all 22 non-template files in `docs/todo/` read; `docs/specs/` and `docs/decisions/` grepped for retry / cache / render):

- **No other change provides a retry.** `docs/todo/notifications.md:34` puts "delivery retries" out of scope; `docs/todo/api-keys.md:36` puts "Outbound webhooks / third-party integrations" out of scope; `docs/specs/mail-service.md:14` puts "queueing/retry of failed sends" out of scope. **No backlog item makes an outbound call** — Q-1/Q-2 decide whether tenacity has any consumer at all, so Q-6…Q-15 are not asked as givens.
- **No other change provides a cache.** `docs/decisions/ADR-078-stateless-live-query.md` (Accepted) lists "Caching query results" under Alternatives Considered and **rejects** it ("results would go stale against live sources"); `docs/specs/search.md:11` scopes search to a "stateless live query (no index, no persistence)" and `:19` D1 repeats it; `docs/specs/settings.md:347` NFR-003 already keeps settings values in memory. A cache would be a **new architectural element against a standing decision** — Q-3, Q-16…Q-24.
- **No other change provides a rendering surface.** `docs/todo/structure-map.md` is explicitly "stdlib-only"; `docs/specs/structlog-logging.md:108` REQ-006 (PR #67, WAITING) fixes the renderer set to `"text" | "json"`, so a rich renderer is an amendment to a spec that has not merged yet — Q-4, Q-25…Q-29.
- `docs/todo/pyproject-tooling-gaps.md:50` — the "Any dependency addition (see `docs/todo/tenacity-rich-cachetools.md`)" item is **struck** (superseded by Q-4/`py-webauthn`) and "the *new*-dependency prohibition stands". That change is **MERGED** (PR #68), so this change cannot obtain `[tool.deptry]` relief through it.
- ADR numbers already claimed ahead of this change: the highest ADR file on `main` is **ADR-082** (`docs/decisions/ADR-082-structlog-processor-layer-over-stdlib.md`); **ADR-081** has no file yet but is planned by `api-keys` (`docs/questions/api-keys.md:740`, `:808`). Numbering is **already decided** — taken at S2.1 by merge order, never pre-reserved (`docs/questions/structlog-logging.md:87` records the collision as "not a question for the user", `:272` answers it) — so it is **not re-asked here**.
- `docs/todo/structlog-logging.md` / `docs/decisions/ADR-082-structlog-processor-layer-over-stdlib.md:35` — the structlog change "clears `tenacity-rich-cachetools`'s dependency on this decision"; the loguru→structlog swap is decided (Q-01 = B), so any rich question is asked against **structlog**, not loguru.

## Q-1 — tenacity: adopt it in this change at all?

- **Step:** P.2 (Phase P)
- **Why needed:** decides whether Q-6…Q-15 run at all; it is the gate on the whole tenacity branch.
- **Context:** `docs/todo/tenacity-rich-cachetools.md` `Why` table (zero `httpx` call sites, no consumer); `docs/specs/mail-service.md:14` excludes "queueing/retry of failed sends"; an unused declared dependency is a DEP002 finding (`pyproject.toml:120-124`, `.github/workflows/quality.yml:93-94`).
- **Options:**
  1. (Recommended) **Decline tenacity here** — no consumer exists today and no backlog item creates one (`docs/todo/notifications.md:34`, `docs/todo/api-keys.md:36`); record the re-open trigger (Q-2).
  2. **Adopt with mail as the consumer** — forces the mail-service scope amendment (Q-14) and every answer in Q-6…Q-13.
  3. **Adopt with a new shared outbound-call capability** specified in this change — the change becomes CROSS-CUTTING (Q-30) and needs its own spec before any code.
- **Question:** Does tenacity enter the template in this change, and on what basis — declined with a trigger, adopted against the existing SMTP call, or adopted against a new outbound-call capability?
- **Answer:** **PENDING**
- **Date:** -
- **Status:** PENDING
- **Incorporated:** no

## Q-2 — tenacity: what trigger re-opens it if declined?

- **Step:** P.2 (Phase P)
- **Why needed:** the TODO's own Acceptance signal requires a declined dependency to record "the trigger that would re-open it"; without a named trigger the item is re-litigated at the next dependency review.
- **Context:** `docs/todo/tenacity-rich-cachetools.md` Acceptance signal; `docs/todo/value-triage-gate.md:94` row 13 already scores the item 2/5 "decline".
- **Options:**
  1. (Recommended) **Named trigger in the TODO:** "the first approved spec that names an outbound third-party call (HTTP provider, webhook, external API)" — nothing is built until such a spec exists.
  2. **Open a companion backlog TODO now** for the provider feature that would consume it, and make this item `Depends on:` it.
  3. **No trigger** — re-open on demand when someone asks.
- **Question:** If tenacity is declined, what exactly is the recorded condition that re-opens it?
- **Answer:** **PENDING**
- **Date:** -
- **Status:** PENDING
- **Incorporated:** no

## Q-3 — cachetools: adopt it in this change at all?

- **Step:** P.2 (Phase P)
- **Why needed:** gate on the whole cachetools branch (Q-16…Q-24); a cache is the only one of the three that would change observable behavior of existing features.
- **Context:** `docs/decisions/ADR-078-stateless-live-query.md` rejected caching; `docs/specs/settings.md:347` NFR-003 keeps settings in memory already; `docs/specs/authentication.md:405` NFR-001 (login ≤ 250 ms p95) already passes with no cache; the hottest read is the session lookup, wired only since PR #63 (`src/main.py:158`, `src/backend/permissions/service.py:409-425`).
- **Options:**
  1. (Recommended) **Decline** — no measured hot path, and a TTL cache in front of session truth contradicts `docs/specs/authentication.md:373` INV-002 unless four specs are amended (Q-20).
  2. **Adopt for session validation** — answers Q-16…Q-24 and amends the authentication, session-management and permissions specs.
  3. **Adopt for a non-security read** (permission catalog / role resolution) — smaller blast radius, but still no measured need.
- **Question:** Does cachetools enter the template, and if so for which read?
- **Answer:** **PENDING**
- **Date:** -
- **Status:** PENDING
- **Incorporated:** no

## Q-4 — rich: adopt it in this change at all?

- **Step:** P.2 (Phase P)
- **Why needed:** gate on the whole rich branch (Q-25…Q-29).
- **Context:** no CLI or reporting surface exists (`src/main.py` is composition root only); pytest already renders assertion diffs; `docs/specs/structlog-logging.md:108` REQ-006 fixes the renderer set to `"text" | "json"`; a dev-group dependency is invisible to DEP002 (see Q-28 Context).
- **Options:**
  1. (Recommended) **Decline** — there is nothing in this template for rich to render.
  2. **Adopt dev-group only** (traceback/pretty output for local dev and scripts) — see Q-25, Q-28.
  3. **Adopt as a logging-feature renderer** — amends a spec whose PR (#67) has not merged (Q-26).
- **Question:** Does rich enter the template, and if so in what role?
- **Answer:** **PENDING**
- **Date:** -
- **Status:** PENDING
- **Incorporated:** no

## Q-5 — split this TODO into one per dependency?

- **Step:** P.2 (Phase P)
- **Why needed:** determines how many changes, specs, ADRs and PRs the orchestrator opens, and whether one change must be CROSS-CUTTING to hold three unrelated capabilities.
- **Context:** `docs/todo/tenacity-rich-cachetools.md` Goal covers three packages with three unrelated consumers; AGENTS.md "Multi-change scheduling" makes parallel prepared changes free.
- **Options:**
  1. (Recommended) **Split into three TODOs now** (tenacity / rich / cachetools) — each gets its own decision, spec, ADR and PR; nothing waits on an unrelated sibling.
  2. **Keep one umbrella TODO** — one ADR and one PR, but one spec must cover three unrelated capabilities and the type is forced to CROSS-CUTTING.
  3. **Split only the dependencies the user keeps** — declined ones stay recorded in this file.
- **Question:** Should this item stay one change or become three?
- **Answer:** **PENDING**
- **Date:** -
- **Status:** PENDING
- **Incorporated:** no

## Q-6 — tenacity: which mail failures are retryable?

- **Step:** P.2 (Phase P)
- **Why needed:** the retry predicate is the single most consequential tenacity decision — retrying a permanent failure doubles load on a server that just refused.
- **Context:** `MailTransportError` reasons are `"connection" | "authentication" | "smtp" | "timeout"` (`src/backend/mail/transport.py:79-87`; `docs/specs/mail-service.md:269` REQ-011, `:294` AC-012).
- **Options:**
  1. (Recommended) **`connection` and `timeout` only** — authentication and SMTP-protocol rejections are deterministic; re-sending them cannot succeed.
  2. **Every transport reason** — simplest rule, but retries permanent failures.
  3. **A live-configurable reason list** via the settings registry — matches the live-read pattern (ADR-057) but exposes a tuning surface nobody has measured.
- **Question:** Which `MailTransportError` reasons may a retry act on?
- **Answer:** **PENDING**
- **Date:** -
- **Status:** PENDING
- **Incorporated:** no

## Q-7 — tenacity: attempts, backoff and jitter

- **Step:** P.2 (Phase P)
- **Why needed:** the numbers are normative (an AC must state them) and they set the worst-case latency a caller waits.
- **Context:** `docs/specs/mail-service.md:247` `mail.smtp_timeout` default 30 s; the repo's test tooling can drive clocks (`tests/tooling_test_helpers.py:44` `travel`).
- **Options:**
  1. (Recommended) **3 attempts total, exponential base 1 s ×2 with full jitter, per-attempt cap 10 s** — conventional, bounded, testable without sleeps.
  2. **2 attempts, fixed 1 s** — minimal, less protection against a flapping server.
  3. **All three as live settings** (`mail.retry_max_attempts`, `mail.retry_backoff`, `mail.retry_jitter`) — configurable before there is a measured need.
- **Question:** What are the attempt count, backoff and jitter?
- **Answer:** **PENDING**
- **Date:** -
- **Status:** PENDING
- **Incorporated:** no

## Q-8 — tenacity: is there a total deadline for the retry loop?

- **Step:** P.2 (Phase P)
- **Why needed:** with a 30 s per-attempt socket timeout, 3 attempts plus backoff can block one request thread for ~90 s; no spec bounds the aggregate today.
- **Context:** `docs/specs/mail-service.md:247` (`mail.smtp_timeout` = 30 s), `:269` REQ-011 (one send per call), `:334` NFR-001 which explicitly refuses to budget SMTP delivery time; `docs/specs/authentication.md:405` NFR-001 budgets the *login* path, not the send.
- **Options:**
  1. (Recommended) **A total deadline** (live setting, default 60 s) that stops the loop from starting another attempt once exceeded — bounds the caller's worst case.
  2. **No deadline** — attempts only; worst case ≈ 90 s plus backoff.
  3. **Per-attempt timeout only** — no aggregate bound, the simplest contract.
- **Question:** Is the retry loop bounded by a total deadline, and what is its default?
- **Answer:** **PENDING**
- **Date:** -
- **Status:** PENDING
- **Incorporated:** no

## Q-9 — tenacity: what exactly is retried?

- **Step:** P.2 (Phase P)
- **Why needed:** decides whether a retry re-renders the template and re-reads live settings mid-flight.
- **Context:** `MailService.send_email` does validate → render → build → resolve SMTP config → send → publish (`docs/specs/mail-service.md:266-270` REQ-008…REQ-012); `SmtpTransport.send(message)` is the single transport operation (`src/backend/mail/transport.py:32`, `docs/decisions/ADR-043-smtp-transport-abstraction.md`).
- **Options:**
  1. (Recommended) **Only `SmtpTransport.send(message)`** — the already-rendered message is reused; a retry cannot re-render or re-read settings mid-flight.
  2. **The whole `send_email`** — re-validates and re-renders, so a retry sees live settings; costs a render per attempt.
  3. **Render + build + send** (recipient validation stays once) — middle ground, more moving parts.
- **Question:** Which unit of work does the retry wrap?
- **Answer:** **PENDING**
- **Date:** -
- **Status:** PENDING
- **Incorporated:** no

## Q-10 — tenacity: duplicate-send risk for the password-reset email

- **Step:** P.2 (Phase P)
- **Why needed:** a retried send is a real user-visible side effect; the specs make reset tokens single-use but a second email is still a second email in the user's inbox.
- **Context:** `docs/specs/authentication.md:315` REQ-011 (single-use, 15 min, a new request supersedes prior tokens), `:348-349` AC-017/AC-018; `docs/specs/mail-service.md:269` REQ-011 (a transport failure is raised after the attempt).
- **Options:**
  1. (Recommended) **Retry only failures raised before the server accepts the message** (connect/greeting-stage `connection` and `timeout`) — a duplicate then requires an ambiguous server state, not a policy choice.
  2. **Accept duplicate risk** — a second reset email is harmless because tokens are superseded and single-use.
  3. **Never retry the built-in `PASSWORD_RESET` / `EMAIL_VERIFICATION` templates**; retry only feature-supplied templates.
- **Question:** Is a duplicate send acceptable, and how is it bounded?
- **Answer:** **PENDING**
- **Date:** -
- **Status:** PENDING
- **Incorporated:** no

## Q-11 — tenacity: where does the retry live?

- **Step:** P.2 (Phase P)
- **Why needed:** it fixes the feature boundary (mail-only vs a new shared capability) and therefore the change type.
- **Context:** `SmtpTransportImpl` sees the raw `smtplib` errors and produces the reason (`src/backend/mail/transport.py:61-87`); `MailService` owns the event and exception contract (`docs/specs/mail-service.md:270` REQ-012, `:336` NFR-003).
- **Options:**
  1. (Recommended) **`SmtpTransportImpl`** — it already classifies the failure into a reason, and `MailService`'s observable contract is untouched.
  2. **`MailService`, around the transport call** — one place to publish a final `EmailFailed`, but it must re-derive the retryable reason from the wrapped error.
  3. **A new shared `backend/outbound/` retry capability** — reusable by future features, and makes this change CROSS-CUTTING (Q-30).
- **Question:** Which component owns the retry loop?
- **Answer:** **PENDING**
- **Date:** -
- **Status:** PENDING
- **Incorporated:** no

## Q-12 — tenacity: does the retry change the mail error/event contract?

- **Step:** P.2 (Phase P)
- **Why needed:** `docs/specs/mail-service.md:273` REQ-015 / `:336` NFR-003 make the public API a backward-compatibility contract; adding a field is an amendment with its own ACs.
- **Context:** `EmailFailed(to, template, reason)` with `reason: "template" | "configuration" | "transport"` (`docs/specs/mail-service.md:138-141`, `:270` REQ-012); `MailTransportError` carries only a secret-free message.
- **Options:**
  1. (Recommended) **No contract change** — attempt counts appear only in log records.
  2. **Add `attempts` to both `MailTransportError` and `EmailFailed`** — observable retry cost, but a REQ-015/NFR-003 contract amendment plus new ACs.
  3. **Add `attempts` to the event only** — the exception stays as-is; the event grows.
- **Question:** Does the retry surface attempt information in the public contract?
- **Answer:** **PENDING**
- **Date:** -
- **Status:** PENDING
- **Incorporated:** no

## Q-13 — tenacity: one `EmailFailed` per attempt or one per send?

- **Step:** P.2 (Phase P)
- **Why needed:** subscribers react once per event; three events per failed send changes what a subscriber (e.g. a future notification feature) would do.
- **Context:** `docs/specs/mail-service.md:270` REQ-012 publishes `EmailFailed` then re-raises; `docs/todo/notifications.md` plans subscribers on this event stream.
- **Options:**
  1. (Recommended) **One `EmailFailed` for the final failure only** — subscribers keep reacting once per send.
  2. **One per failed attempt** — full visibility, but an alerting subscriber fires 3×.
  3. **Final `EmailFailed` plus a WARNING log per attempt** — visibility without event spam.
- **Question:** How many `EmailFailed` events does a retried send publish?
- **Answer:** **PENDING**
- **Date:** -
- **Status:** PENDING
- **Incorporated:** no

## Q-14 — tenacity: mail-service Spec Amendment first?

- **Step:** P.2 (Phase P)
- **Why needed:** retry is explicitly out of the approved mail spec's scope, so code cannot be written against it without a spec change (AGENTS.md Spec Amendment Workflow).
- **Context:** `docs/specs/mail-service.md:14` "Out of scope: … queueing/retry of failed sends".
- **Options:**
  1. (Recommended) **Open a Spec Amendment PR for `docs/specs/mail-service.md`** (scope line + new REQ/AC) before implementation, per the Spec Amendment Workflow.
  2. **Write a new capability spec** (`docs/specs/outbound-retry.md`) and leave mail-service's scope untouched — retry then lives outside the mail feature (Q-11 option 3).
  3. **Decline tenacity** — closes Q-6…Q-15.
- **Question:** Which spec route does the retry take?
- **Answer:** **PENDING**
- **Date:** -
- **Status:** PENDING
- **Incorporated:** no

## Q-15 — tenacity: new ADR, or amend ADR-043?

- **Step:** P.2 (Phase P)
- **Why needed:** AGENTS.md requires every dependency decision to be traceable to an ADR; the alternatives the ADR must weigh are fixed by this answer.
- **Context:** `docs/decisions/ADR-043-smtp-transport-abstraction.md` (the transport ABC); AGENTS.md "Dependencies and Existing Packages" ("Dependency decisions must be traceable… Record the decision in an ADR"); the ADR number itself is taken at S2.1 by merge order, never pre-reserved (`docs/questions/structlog-logging.md:272`).
- **Options:**
  1. (Recommended) **A new ADR** weighing a stdlib retry loop (`time` + `random` + a deadline), tenacity, and caller-side retry — the dependency itself is the decision.
  2. **Amend ADR-043** — the retry is a transport-internal choice, but ADR-043's Decision is about the ABC seam, not about adopting a dependency.
  3. **Defer the ADR to the consumer change** — leaves a declared dependency with no recorded decision (and DEP002 pressure).
- **Question:** Where is the tenacity decision recorded, and which alternatives must it weigh?
- **Answer:** **PENDING**
- **Date:** -
- **Status:** PENDING
- **Incorporated:** no

## Q-16 — cachetools: which read is cached?

- **Step:** P.2 (Phase P)
- **Why needed:** the cached read determines every invalidation point (Q-19), every spec amendment (Q-20) and the change type (Q-30).
- **Context:** two independent session-by-token lookups exist — `src/backend/authentication/service.py:230-237` (`session_info`, `logout`) and `src/backend/permissions/service.py:409-425` (`_validate_session` via the structural `SessionLookup` seam, wired at `src/main.py:158`); permission decisions are not cached.
- **Options:**
  1. (Recommended) **None** — no measured hot path; NFR-001 (`docs/specs/authentication.md:405`) already passes without a cache.
  2. **`PermissionService._validate_session`'s `get_by_token_hash`** — the hottest read since PR #63 wired the lookup.
  3. **`AuthService.session_info`** — one read per call, no fan-out.
  4. **Permission decision results** (user + action) — the biggest win and the biggest invalidation surface.
- **Question:** Which specific read would the cache front?
- **Answer:** **PENDING**
- **Date:** -
- **Status:** PENDING
- **Incorporated:** no

## Q-17 — cachetools: what is the cache key?

- **Step:** P.2 (Phase P)
- **Why needed:** a cache keyed by a live credential would put a usable session token in process memory, against the repo's token-handling rules.
- **Context:** `docs/specs/authentication.md:406` NFR-002 (raw session tokens never in logs/events; tokens stored only as SHA-256 hashes); the lookup already hashes first (`src/backend/permissions/service.py:419`).
- **Options:**
  1. (Recommended) **The token hash only** — the raw token never enters the cache, matching the existing hashing rule.
  2. **The raw token** — saves one hash per hit, but caches a live credential.
  3. **The session id after first resolution** — still needs a token→id map, so it adds a second cache.
- **Question:** What keys the cache entries?
- **Answer:** **PENDING**
- **Date:** -
- **Status:** PENDING
- **Incorporated:** no

## Q-18 — cachetools: TTL and max size

- **Step:** P.2 (Phase P)
- **Why needed:** the TTL *is* the maximum window in which a revoked session is still honoured — it is a security parameter, not a tuning knob.
- **Context:** `docs/specs/authentication.md:312-313` REQ-008/REQ-009 (revoked/expired → `InvalidSessionError`), `:344` AC-013 ("immediately unusable"); the settings feature's live-read pattern (`docs/decisions/ADR-057-settings-registry-live-reads.md`).
- **Options:**
  1. (Recommended) **TTL 5 s, maxsize 1024** — bounds post-revocation acceptance to 5 s and memory to ~1024 entries.
  2. **TTL 60 s, maxsize 4096** — better hit rate, a full minute of post-revocation acceptance.
  3. **Live settings** (`session.cache_ttl`, `session.cache_max_size`) with those defaults — tunable per deployment, more surface.
- **Question:** What are the TTL and the max size?
- **Answer:** **PENDING**
- **Date:** -
- **Status:** PENDING
- **Incorporated:** no

## Q-19 — cachetools: which invalidation points must bust the cache?

- **Step:** P.2 (Phase P)
- **Why needed:** the specs require revocation to take effect immediately; every invalidation point the cache misses is a spec violation with a security consequence.
- **Context:** `docs/specs/authentication.md:344` AC-013 (logout "immediately unusable"), `:350` AC-019 (password change revokes all sessions), `:316` REQ-012; `docs/specs/session-management.md:150` REQ-008 (`revoke_session`), `:156` REQ-014 (per-user cap evicts oldest), `:157` REQ-015 (revocation on `UserPasswordChanged`/`UserDeactivated`/`UserDeleted`); `docs/specs/user-roles-permissions.md:513` REQ-017, `:597` EDGE-007.
- **Options:**
  1. (Recommended) **Subscribe to every revocation event the specs already publish** (`Logout`, `PasswordResetCompleted`, `UserPasswordChanged`, `UserDeactivated`, `UserDeleted`, `SessionRevoked`, `AllSessionsRevoked`) and clear that user's entries, plus a full clear on cap eviction.
  2. **TTL only, no invalidation** — simplest, but a revoked session stays usable for up to the TTL, contradicting AC-013's "immediately".
  3. **Invalidate on the authentication-side paths only** (logout, password change, completed reset) and accept staleness for `revoke_session` and cap eviction.
- **Question:** Which revocation paths must invalidate the cache?
- **Answer:** **PENDING**
- **Date:** -
- **Status:** PENDING
- **Incorporated:** no

## Q-20 — cachetools: which spec IDs must be amended before the cache exists?

- **Step:** P.2 (Phase P)
- **Why needed:** INV-002 is stated as an "if and only if" against the store; a TTL cache makes it observably false, and AGENTS.md forbids introducing behavior not represented in the spec.
- **Context:** `docs/specs/authentication.md:373` INV-002 ("valid if and only if … `revoked == False` and `expires_at > now`"), `:312-313` REQ-008/REQ-009; `docs/specs/session-management.md:150` REQ-008, `:157` REQ-015; `docs/specs/user-roles-permissions.md:513` REQ-017.
- **Options:**
  1. (Recommended) **Amend all four specs** (authentication INV-002 + REQ-008/REQ-009, session-management REQ-008/REQ-015, permissions REQ-017) with an explicit bounded-staleness clause before any cache code is written.
  2. **Write one new cache spec and leave the four IDs untouched** — the existing specs then contradict the executable tests.
  3. **Decline cachetools** — closes Q-16…Q-24.
- **Question:** Which spec IDs are amended first, and in which change?
- **Answer:** **PENDING**
- **Date:** -
- **Status:** PENDING
- **Incorporated:** no

## Q-21 — cachetools: which acceptance criteria must exist before the cache is written?

- **Step:** P.2 (Phase P)
- **Why needed:** Phase 3 requires tests derived from the spec before implementation; the invalidation ACs are the only thing that makes a security cache testable.
- **Context:** the repo's AC style (`docs/specs/authentication.md:344` AC-013, `:350` AC-019); property tests for invariants (`tests/property/authentication/test_sessions.py`, INV-002).
- **Options:**
  1. (Recommended) **One AC per invalidation point** (logout, password change, completed reset, `revoke_session`, user deactivate/delete, cap eviction), each "given a valid session, when X, then the next `session_info(token)` / `has_permission(...)` fails" — written and RED before the cache.
  2. **One representative AC (password change) plus a property test over INV-002** — smaller test set, less per-path evidence.
  3. **A property test only** — no per-point acceptance criterion.
- **Question:** What AC set must exist before the cache code lands?
- **Answer:** **PENDING**
- **Date:** -
- **Status:** PENDING
- **Incorporated:** no

## Q-22 — cachetools: how is the cache made thread-safe?

- **Step:** P.2 (Phase P)
- **Why needed:** the specs contract these services for concurrent use, and `cachetools` primitives are not thread-safe without a lock or a thread-local variant.
- **Context:** `docs/specs/authentication.md:409` NFR-005 (thread-safe services and repositories; the attempt tracker is internally locked); `tests/integration/authentication/test_concurrency.py` is the existing pattern.
- **Options:**
  1. (Recommended) **Wrap the cache in a `threading.Lock` inside the repo's own wrapper** — explicit, and testable with the existing concurrency test.
  2. **`cachetools.cached.TLRUCache`** (thread-local reclamation) — less lock contention, subtler semantics under explicit invalidation.
  3. **Document single-threaded use** — contradicts NFR-005.
- **Question:** What is the thread-safety mechanism for the cache?
- **Answer:** **PENDING**
- **Date:** -
- **Status:** PENDING
- **Incorporated:** no

## Q-23 — cachetools: how is TTL expiry tested (clock injection)?

- **Step:** P.2 (Phase P)
- **Why needed:** measured evidence — the repo's standard TTL-expiry test pattern does **not** work on a `cachetools` TTL, so the cache's clock must become an injectable seam or the expiry AC is untestable without sleeps.
- **Context:** measured 2026-10-05 under `uv run --with cachetools --with time-machine python -c …`: a `TTLCache` entry expires after a real sleep, and inside one `travel(..., tick=True)` block monotonic advances with real elapsed time, but a **nested `travel()` jump does not expire the entry** — `TTLCache` binds `time.monotonic` at construction. `cachetools` accepts a `timer=` callable. The house helper is `tests/tooling_test_helpers.py:44` `travel(destination, *, tick=False)`.
- **Options:**
  1. (Recommended) **Inject the clock** — build the cache with `timer=<callable the test controls>` so `travel()`/a fake timer drives expiry deterministically; no sleeps, no coupling of test TTL to production TTL.
  2. **Rely on `travel(tick=True)` with a sub-second TTL in tests** — works, but the test TTL and the production TTL (Q-18) diverge.
  3. **Real sleep past the TTL** — violates the repo's no-sleep test convention and slows the suite.
- **Question:** How is cache expiry made testable?
- **Answer:** **PENDING**
- **Date:** -
- **Status:** PENDING
- **Incorporated:** no

## Q-24 — cachetools: does a security-critical cache belong in a template at all?

- **Step:** P.2 (Phase P)
- **Why needed:** `[project].dependencies` is inherited by every project bootstrapped from this template, so the answer is a policy about the template, not about this repo.
- **Context:** `pyproject.toml:8-25` (runtime dependencies every bootstrapped project inherits); the template's own specs make revocation immediate (`docs/specs/authentication.md:344` AC-013); `docs/decisions/ADR-078-stateless-live-query.md` rejected caching for staleness reasons.
- **Options:**
  1. (Recommended) **No** — a cache in front of session/permission truth is a per-project performance decision; keep cachetools out of the template.
  2. **Yes, but opt-in** — shipped and wired with the TTL default `0` (disabled), so behavior is unchanged until a project enables it.
  3. **Yes, on by default** with the full invalidation contract — every bootstrapped project inherits the staleness window.
- **Question:** Is a security-critical TTL cache acceptable as a template default?
- **Answer:** **PENDING**
- **Date:** -
- **Status:** PENDING
- **Incorporated:** no

## Q-25 — rich: what would rich actually be for?

- **Step:** P.2 (Phase P)
- **Why needed:** rich has no consumer, so the role question must be answered before any other rich question; each role has a different spec and dependency placement.
- **Context:** no CLI or reporting entrypoint exists (`src/main.py` is composition root only; `scripts/` holds 3 CI helpers); pytest already renders assertion diffs; `docs/todo/structure-map.md` is stdlib-only by decision.
- **Options:**
  1. (Recommended) **Nothing** — decline; there is no surface to render.
  2. **A dev-group traceback handler for unhandled exceptions** (dev-only; see Q-28).
  3. **A `renderer="rich"` value in the logging feature** (see Q-26).
  4. **A `scripts/` reporting CLI** (e.g. a traceability/coverage report) as the consuming surface — a surface that does not exist today and would have to be specified first.
- **Question:** What would rich render in this template?
- **Answer:** **PENDING**
- **Date:** -
- **Status:** PENDING
- **Incorporated:** no

## Q-26 — rich: does the renderer set get amended?

- **Step:** P.2 (Phase P)
- **Why needed:** the renderer vocabulary is a closed set in a spec whose PR is not merged yet; adding a value is a Spec Amendment against a change still in flight.
- **Context:** `docs/specs/structlog-logging.md:49-53` `setup_logger(*, renderer: str | None = None)` accepts only `"text" | "json"`; `:108` REQ-006; `:152` AC-010; `:182` EDGE-005 (`ValueError` before any handler is installed); PR #67 is WAITING for the human merge.
- **Options:**
  1. (Recommended) **Do not touch it** — decline rich; the renderer set stays a closed two-value set.
  2. **Amend `structlog-logging.md` REQ-006 / AC-010 / EDGE-005 to add `"rich"`** — a third renderer, a new runtime dependency, and an amendment to a spec that has not merged.
  3. **Render with rich outside `setup_logger()`** (a dev entrypoint only) — no spec change, but a second, unspecified rendering path.
- **Question:** Does rich become a renderer value, and does that amend the structlog spec?
- **Answer:** **PENDING**
- **Date:** -
- **Status:** PENDING
- **Incorporated:** no

## Q-27 — rich: how is the locals-leak invariant preserved?

- **Step:** P.2 (Phase P)
- **Why needed:** rich's traceback rendering shows local variable values by default, and the repo has a proven invariant that exception output never carries locals — this is the invariant that keeps passwords and tokens out of logs.
- **Context:** `docs/decisions/ADR-082-structlog-processor-layer-over-stdlib.md:26` ("Exception records carry type, message and traceback frames only — never local variable values (`diagnose=False` policy … `logging.md` NFR-003 … proven by a Hypothesis property test)"); `docs/specs/authentication.md:376` INV-005 (the password never appears in observable output).
- **Options:**
  1. (Recommended) **If rich is ever adopted, `show_locals=False` is a normative AC with a test** that a secret held in a local never reaches the output.
  2. **Restrict rich to non-exception output** (tables, progress), never tracebacks — the invariant is never in play.
  3. **Decline rich** — the invariant stays unexposed by construction (closes Q-25…Q-29).
- **Question:** How is the "no locals in exception output" invariant preserved if rich lands?
- **Answer:** **PENDING**
- **Date:** -
- **Status:** PENDING
- **Incorporated:** no

## Q-28 — rich: does a dev-group dependency need a consumer?

- **Step:** P.2 (Phase P)
- **Why needed:** measured evidence — the deptry gate that makes an unused runtime dependency impossible **cannot see a dev-group dependency**, so the "must have a consumer" rule would be unenforced rather than satisfied.
- **Context:** measured 2026-10-05: `uv run deptry .` → `Scanning 89 files... Success! No dependency issues found` while `respx`, `polyfactory`, `time-machine` and `hypothesis` are declared in `[dependency-groups].dev` (`pyproject.toml:30-67`) and imported only from `tests/`, which is in deptry's `DEFAULT_EXCLUDE` (`.venv/Lib/site-packages/deptry/cli.py:25`); deptry classifies every `[dependency-groups]` group as dev unless listed in `non_dev_dependency_groups` (`.venv/Lib/site-packages/deptry/dependency_getter/pep621/base.py:186-190`), so DEP002 never fires for them.
- **Options:**
  1. (Recommended) **Same bar as runtime dependencies** — a dev-only dependency still needs a real consumer, because the gate is blind here, not because it is free.
  2. **Allow dev-only with no consumer** — deptry will not flag it, and dev tools already sit in the DEP002 ignore list (`pyproject.toml:120-124`).
  3. **Require a `scripts/` consumer specifically** — deptry scans `scripts/`, so the usage becomes gate-visible.
- **Question:** Does a dev-group dependency need a consuming feature?
- **Answer:** **PENDING**
- **Date:** -
- **Status:** PENDING
- **Incorporated:** no

## Q-29 — rich: does it wait for structlog-logging (PR #67)?

- **Step:** P.2 (Phase P)
- **Why needed:** sequencing decision — rich would attach to a logging surface that is mid-flight.
- **Context:** `docs/decisions/ADR-082-structlog-processor-layer-over-stdlib.md:35` — the structlog change "clears `tenacity-rich-cachetools`'s dependency on this decision"; `docs/todo/structlog-logging.md` Status WAITING (PR #67 open, amendment PR merges before its implementation PR).
- **Options:**
  1. (Recommended) **No rich work before #67 merges** — the renderer vocabulary and the exception-record shape are exactly what rich would attach to.
  2. **Proceed now against loguru** — the code would be rewritten by #67 within days.
  3. **Treat rich as independent** (dev-only traceback/CLI) — no dependency on #67 at all.
- **Question:** Does the rich path depend on structlog-logging landing first?
- **Answer:** **PENDING**
- **Date:** -
- **Status:** PENDING
- **Incorporated:** no

## Q-30 — when does this change become CROSS-CUTTING rather than FEATURE?

- **Step:** P.2 (Phase P)
- **Why needed:** the type decides whether a per-feature Impact Analysis, per-feature task grouping and per-feature traceability updates are required; a session cache spans three features.
- **Context:** AGENTS.md Change Types #3 (CROSS-CUTTING = intentionally spans two or more features) and the Escalation Rules; a session cache touches authentication + session-management + permissions; a shared outbound retry touches mail + future features.
- **Options:**
  1. (Recommended) **Reclassify to CROSS-CUTTING whenever the adopted dependency touches ≥2 features**, with per-feature impact analysis and traceability updates.
  2. **Keep FEATURE by confining the change to one feature** (e.g. retry inside mail only) — smaller graph, but the cache option is excluded by construction.
  3. **Split into one FEATURE change per affected feature** — independently verifiable, more PRs and more ADRs.
- **Question:** What is the change type once a dependency is adopted, and what triggers the reclassification?
- **Answer:** **PENDING**
- **Date:** -
- **Status:** PENDING
- **Incorporated:** no

## Q-31 — cachetools: which feature owns the cache?

- **Step:** P.2 (Phase P)
- **Why needed:** the cache would be read by two features and invalidated by a third; the owner decides where the invalidation subscriptions live and whether `shared/` grows.
- **Context:** AGENTS.md "`shared/` is deliberately small" and "Features are the primary architectural boundary"; session-management already owns revocation (`docs/specs/session-management.md:150` REQ-008, `:156` REQ-014, `:157` REQ-015) and subscribes to the user-lifecycle events; the readers are `src/backend/authentication/service.py:230-237` and `src/backend/permissions/service.py:409-425`.
- **Options:**
  1. (Recommended) **session-management owns it** — it already owns session revocation and the events that invalidate, so the cache and its invalidation live in one feature and are exposed through the repository/lookup seam the other features already depend on.
  2. **A new `backend/shared/` caching capability** — reusable, but `shared/` is deliberately small by rule and it needs its own spec (CROSS-CUTTING, Q-30).
  3. **Each consuming feature keeps its own cache** — no new shared code, but the invalidation logic is duplicated across authentication and permissions and can drift.
  4. **Decline cachetools** — closes Q-16…Q-24 and this with it.
- **Question:** If a cache lands, which feature owns it?
- **Answer:** **PENDING**
- **Date:** -
- **Status:** PENDING
- **Incorporated:** no

## Q-32 — where is an adopted dependency declared?

- **Step:** P.2 (Phase P)
- **Why needed:** `[project].dependencies` is inherited by every project bootstrapped from this template, and it is also the set deptry's DEP002 checks.
- **Context:** `pyproject.toml:8-25` (runtime dependencies), `:27-67` `[dependency-groups]` (`dev` at `:30`, `docs` at `:71`); **no `[project.optional-dependencies]` table is declared today** — `agent-runner` is a `[tool.agent-runner]` section (`:219`), not an extra; `docs/todo/pyproject-tooling-gaps.md:50` keeps the new-dependency prohibition.
- **Options:**
  1. (Recommended) **`[project].dependencies` only when a `src/` module imports it unconditionally** — that is also what keeps DEP002 honest.
  2. **A new `[project.optional-dependencies]` extra** (e.g. `cache`, `dev-tools`) — the template stays lean, but the consumer must degrade when the extra is absent: extra code, extra tests, and a table the template has never had.
  3. **The dev group** — only for a genuinely dev-only surface (Q-28), never for a runtime capability.
- **Question:** Which dependency declaration does an adopted package go into?
- **Answer:** **PENDING**
- **Date:** -
- **Status:** PENDING
- **Incorporated:** no

## Q-33 — what records a declined dependency?

- **Step:** P.2 (Phase P)
- **Why needed:** the TODO's Acceptance signal says a declined dependency is "recorded in this file and the trigger that would re-open it"; whether an ADR is also required decides if a non-adoption becomes an architectural record.
- **Context:** `docs/todo/tenacity-rich-cachetools.md` Acceptance signal; `docs/todo/value-triage-gate.md:94` row 13 (2/5, "decline"); AGENTS.md requires an ADR for dependency *decisions* — whether "not adopting" counts is open.
- **Options:**
  1. (Recommended) **The TODO prep log plus the value-triage row** — no spec, no ADR; a non-adoption is a backlog decision, not an architectural one.
  2. **Also a short "not adopted" ADR** — a durable record of why the template does not carry these three, so the question is not re-litigated at the next review.
  3. **Nothing beyond the prep log.**
- **Question:** What artifact records a declined dependency?
- **Answer:** **PENDING**
- **Date:** -
- **Status:** PENDING
- **Incorporated:** no

## Late questions (Phases 2-6)

<!-- Appended by the orchestrator (on main) from a step's BLOCKED-USER handoff, with the entry's Step: set to the step that found it. -->
