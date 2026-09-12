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

## Phase 3 — Test & RED (FEATURE)

- **Status:** DONE (RED confirmed and recorded).
- **Date:** 2026-09-12
- **RED command:** `uv run pytest tests/acceptance/mail tests/property/mail tests/unit/mail tests/contract/mail tests/integration/mail -v`
- **RED result:** FAILED — pytest exit 4 (collection error). All five mail test
  directories error with `ModuleNotFoundError: No module named 'backend.mail'`
  (the feature package `src/backend/mail/` does not exist yet).
- **Failure mode (test contract sanity check):** import/collection error at the
  unimplemented feature module — NOT a test setup error. The chain is
  `conftest.py -> mail_test_helpers.py -> backend.mail` (missing feature);
  the helpers and fixtures are valid (all new files compile; `ruff check`
  clean). Per the change type, a `ModuleNotFoundError: backend.mail` is the
  valid RED for a not-yet-implemented feature. The rest of the suite is
  unaffected: `uv run pytest tests/ --collect-only -q` collects the 358
  pre-existing tests with only the 5 mail directories erroring.

### Test inventory (39 tests, spec-derived per the spec's Test Strategy, section 10)

| Category | Files | Tests |
|---|---|---|
| Acceptance | `tests/acceptance/mail/test_settings.py` | `test_ac_001_register_settings`, `test_ac_002_live_read_modified_host`, `test_ac_003_fallback_unregistered_host` |
| Acceptance | `tests/acceptance/mail/test_send.py` | `test_ac_004_core_send_success`, `test_ac_007_feature_specific_template` |
| Acceptance | `tests/acceptance/mail/test_high_level.py` | `test_ac_005_password_reset_email`, `test_ac_006_email_verification_email` |
| Acceptance | `tests/acceptance/mail/test_render.py` | `test_ac_008_template_rendering` |
| Acceptance | `tests/acceptance/mail/test_validation.py` | `test_ac_009_invalid_recipient`, `test_ac_010_missing_variable` |
| Acceptance | `tests/acceptance/mail/test_config.py` | `test_ac_011_empty_smtp_host` |
| Acceptance | `tests/acceptance/mail/test_transport.py` | `test_ac_012_transport_failure` |
| Acceptance | `tests/acceptance/mail/test_events.py` | `test_ac_013_email_sent_event`, `test_ac_014_email_failed_event`, `test_ac_015_non_sensitive_events` |
| Acceptance | `tests/acceptance/mail/test_logging.py` | `test_ac_016_no_secrets_in_log_records` |
| Acceptance | `tests/acceptance/mail/test_public_api.py` | `test_ac_017_public_api_stable` |
| Acceptance | `tests/acceptance/mail/test_concurrency.py` | `test_ac_018_concurrent_send` |
| Acceptance | `tests/acceptance/mail/test_message.py` | `test_ac_019_multipart_alternative` |
| Property | `tests/property/mail/test_render.py` | `test_inv_001_rendering_deterministic`, `test_inv_002_xss_safe_substitution` |
| Property | `tests/property/mail/test_secrets.py` | `test_inv_003_no_password_in_observable_output`, `test_inv_004_no_body_in_events` |
| Property | `tests/property/mail/test_independence.py` | `test_inv_005_failure_independence` |
| Unit | `tests/unit/mail/test_validation.py` | `test_edge_001_invalid_recipient`, `test_edge_002_missing_variable`, `test_edge_003_malformed_template` |
| Unit | `tests/unit/mail/test_config.py` | `test_edge_004_empty_smtp_host` |
| Unit | `tests/unit/mail/test_transport.py` | `test_edge_005_connection_refused`, `test_edge_006_auth_failure`, `test_edge_007_protocol_error`, `test_edge_008_timeout` |
| Unit | `tests/unit/mail/test_events.py` | `test_edge_009_none_event_bus` |
| Unit | `tests/unit/mail/test_independence.py` | `test_edge_010_failure_then_success` |
| Contract | `tests/contract/mail/test_performance.py` | `test_nfr_001_preparation_performance_budget` |
| Contract | `tests/contract/mail/test_secrets.py` | `test_nfr_002_no_secrets_in_logs_or_events` |
| Contract | `tests/contract/mail/test_public_api.py` | `test_nfr_003_public_api_stable` |
| Contract | `tests/contract/mail/test_logging.py` | `test_nfr_004_service_traced` |
| Integration | `tests/integration/mail/test_concurrency.py` | `test_nfr_005_concurrent_send_thread_safety` |

Shared helpers: `tests/mail_test_helpers.py` (registry isolation via
`reset_settings_registry`, idempotent mail-settings registration, live config
resolution accessor, synchronous `EventCollector`, `RecordingTransport` /
`FailingTransport` / `FlakyTransport` fakes, raw-socket `FakeSmtpServer`
(auth/protocol/timeout failure modes), `closed_port`). Each mail test
directory has a `conftest.py` with an autouse `_reset_registry` fixture
(settings-registry singleton isolation, per the settings live-read test
convention).

### TDD Evidence (RED)

All RED records below share the failure mode
`ModuleNotFoundError: No module named 'backend.mail'` (feature unimplemented);
GREEN records are filled in Phase 4.

#### AC-001
RED:
  command: uv run pytest tests/acceptance/mail/test_settings.py::test_ac_001_register_settings -v
  result: FAILED (ModuleNotFoundError: No module named 'backend.mail')
  commit: f896479

#### AC-002
RED:
  command: uv run pytest tests/acceptance/mail/test_settings.py::test_ac_002_live_read_modified_host -v
  result: FAILED (ModuleNotFoundError: No module named 'backend.mail')
  commit: f896479

#### AC-003
RED:
  command: uv run pytest tests/acceptance/mail/test_settings.py::test_ac_003_fallback_unregistered_host -v
  result: FAILED (ModuleNotFoundError: No module named 'backend.mail')
  commit: f896479

#### AC-004
RED:
  command: uv run pytest tests/acceptance/mail/test_send.py::test_ac_004_core_send_success -v
  result: FAILED (ModuleNotFoundError: No module named 'backend.mail')
  commit: f896479

#### AC-005
RED:
  command: uv run pytest tests/acceptance/mail/test_high_level.py::test_ac_005_password_reset_email -v
  result: FAILED (ModuleNotFoundError: No module named 'backend.mail')
  commit: f896479

#### AC-006
RED:
  command: uv run pytest tests/acceptance/mail/test_high_level.py::test_ac_006_email_verification_email -v
  result: FAILED (ModuleNotFoundError: No module named 'backend.mail')
  commit: f896479

#### AC-007
RED:
  command: uv run pytest tests/acceptance/mail/test_send.py::test_ac_007_feature_specific_template -v
  result: FAILED (ModuleNotFoundError: No module named 'backend.mail')
  commit: f896479

#### AC-008
RED:
  command: uv run pytest tests/acceptance/mail/test_render.py::test_ac_008_template_rendering -v
  result: FAILED (ModuleNotFoundError: No module named 'backend.mail')
  commit: f896479

#### AC-009
RED:
  command: uv run pytest tests/acceptance/mail/test_validation.py::test_ac_009_invalid_recipient -v
  result: FAILED (ModuleNotFoundError: No module named 'backend.mail')
  commit: f896479

#### AC-010
RED:
  command: uv run pytest tests/acceptance/mail/test_validation.py::test_ac_010_missing_variable -v
  result: FAILED (ModuleNotFoundError: No module named 'backend.mail')
  commit: f896479

#### AC-011
RED:
  command: uv run pytest tests/acceptance/mail/test_config.py::test_ac_011_empty_smtp_host -v
  result: FAILED (ModuleNotFoundError: No module named 'backend.mail')
  commit: f896479

#### AC-012
RED:
  command: uv run pytest tests/acceptance/mail/test_transport.py::test_ac_012_transport_failure -v
  result: FAILED (ModuleNotFoundError: No module named 'backend.mail')
  commit: f896479

#### AC-013
RED:
  command: uv run pytest tests/acceptance/mail/test_events.py::test_ac_013_email_sent_event -v
  result: FAILED (ModuleNotFoundError: No module named 'backend.mail')
  commit: f896479

#### AC-014
RED:
  command: uv run pytest tests/acceptance/mail/test_events.py::test_ac_014_email_failed_event -v
  result: FAILED (ModuleNotFoundError: No module named 'backend.mail')
  commit: f896479

#### AC-015
RED:
  command: uv run pytest tests/acceptance/mail/test_events.py::test_ac_015_non_sensitive_events -v
  result: FAILED (ModuleNotFoundError: No module named 'backend.mail')
  commit: f896479

#### AC-016
RED:
  command: uv run pytest tests/acceptance/mail/test_logging.py::test_ac_016_no_secrets_in_log_records -v
  result: FAILED (ModuleNotFoundError: No module named 'backend.mail')
  commit: f896479

#### AC-017
RED:
  command: uv run pytest tests/acceptance/mail/test_public_api.py::test_ac_017_public_api_stable -v
  result: FAILED (ModuleNotFoundError: No module named 'backend.mail')
  commit: f896479

#### AC-018
RED:
  command: uv run pytest tests/acceptance/mail/test_concurrency.py::test_ac_018_concurrent_send -v
  result: FAILED (ModuleNotFoundError: No module named 'backend.mail')
  commit: f896479

#### AC-019
RED:
  command: uv run pytest tests/acceptance/mail/test_message.py::test_ac_019_multipart_alternative -v
  result: FAILED (ModuleNotFoundError: No module named 'backend.mail')
  commit: f896479

#### INV-001
RED:
  command: uv run pytest tests/property/mail/test_render.py::test_inv_001_rendering_deterministic -v
  result: FAILED (ModuleNotFoundError: No module named 'backend.mail')
  commit: f896479

#### INV-002
RED:
  command: uv run pytest tests/property/mail/test_render.py::test_inv_002_xss_safe_substitution -v
  result: FAILED (ModuleNotFoundError: No module named 'backend.mail')
  commit: f896479

#### INV-003
RED:
  command: uv run pytest tests/property/mail/test_secrets.py::test_inv_003_no_password_in_observable_output -v
  result: FAILED (ModuleNotFoundError: No module named 'backend.mail')
  commit: f896479

#### INV-004
RED:
  command: uv run pytest tests/property/mail/test_secrets.py::test_inv_004_no_body_in_events -v
  result: FAILED (ModuleNotFoundError: No module named 'backend.mail')
  commit: f896479

#### INV-005
RED:
  command: uv run pytest tests/property/mail/test_independence.py::test_inv_005_failure_independence -v
  result: FAILED (ModuleNotFoundError: No module named 'backend.mail')
  commit: f896479

#### EDGE-001
RED:
  command: uv run pytest tests/unit/mail/test_validation.py::test_edge_001_invalid_recipient -v
  result: FAILED (ModuleNotFoundError: No module named 'backend.mail')
  commit: f896479

#### EDGE-002
RED:
  command: uv run pytest tests/unit/mail/test_validation.py::test_edge_002_missing_variable -v
  result: FAILED (ModuleNotFoundError: No module named 'backend.mail')
  commit: f896479

#### EDGE-003
RED:
  command: uv run pytest tests/unit/mail/test_validation.py::test_edge_003_malformed_template -v
  result: FAILED (ModuleNotFoundError: No module named 'backend.mail')
  commit: f896479

#### EDGE-004
RED:
  command: uv run pytest tests/unit/mail/test_config.py::test_edge_004_empty_smtp_host -v
  result: FAILED (ModuleNotFoundError: No module named 'backend.mail')
  commit: f896479

#### EDGE-005
RED:
  command: uv run pytest tests/unit/mail/test_transport.py::test_edge_005_connection_refused -v
  result: FAILED (ModuleNotFoundError: No module named 'backend.mail')
  commit: f896479

#### EDGE-006
RED:
  command: uv run pytest tests/unit/mail/test_transport.py::test_edge_006_auth_failure -v
  result: FAILED (ModuleNotFoundError: No module named 'backend.mail')
  commit: f896479

#### EDGE-007
RED:
  command: uv run pytest tests/unit/mail/test_transport.py::test_edge_007_protocol_error -v
  result: FAILED (ModuleNotFoundError: No module named 'backend.mail')
  commit: f896479

#### EDGE-008
RED:
  command: uv run pytest tests/unit/mail/test_transport.py::test_edge_008_timeout -v
  result: FAILED (ModuleNotFoundError: No module named 'backend.mail')
  commit: f896479

#### EDGE-009
RED:
  command: uv run pytest tests/unit/mail/test_events.py::test_edge_009_none_event_bus -v
  result: FAILED (ModuleNotFoundError: No module named 'backend.mail')
  commit: f896479

#### EDGE-010
RED:
  command: uv run pytest tests/unit/mail/test_independence.py::test_edge_010_failure_then_success -v
  result: FAILED (ModuleNotFoundError: No module named 'backend.mail')
  commit: f896479

#### NFR-001
RED:
  command: uv run pytest tests/contract/mail/test_performance.py::test_nfr_001_preparation_performance_budget -v
  result: FAILED (ModuleNotFoundError: No module named 'backend.mail')
  commit: f896479

#### NFR-002
RED:
  command: uv run pytest tests/contract/mail/test_secrets.py::test_nfr_002_no_secrets_in_logs_or_events -v
  result: FAILED (ModuleNotFoundError: No module named 'backend.mail')
  commit: f896479

#### NFR-003
RED:
  command: uv run pytest tests/contract/mail/test_public_api.py::test_nfr_003_public_api_stable -v
  result: FAILED (ModuleNotFoundError: No module named 'backend.mail')
  commit: f896479

#### NFR-004
RED:
  command: uv run pytest tests/contract/mail/test_logging.py::test_nfr_004_service_traced -v
  result: FAILED (ModuleNotFoundError: No module named 'backend.mail')
  commit: f896479

#### NFR-005
RED:
  command: uv run pytest tests/integration/mail/test_concurrency.py::test_nfr_005_concurrent_send_thread_safety -v
  result: FAILED (ModuleNotFoundError: No module named 'backend.mail')
  commit: f896479

## Phase 4 (Implement)

### Implementation
The `backend.mail` feature package was implemented per the approved spec (`docs/specs/mail-service.md` section 3) and the task DAG (`docs/tasks/mail-service.tasks.json`). Files created under `src/backend/mail/`:

- `errors.py` — `MailError` hierarchy (`MailConfigurationError`, `MailTransportError`, `MailTemplateError`), each storing a secret-free `reason` so `str(error) == reason`.
- `templates.py` — `EmailTemplate` + built-in `PASSWORD_RESET_TEMPLATE` / `EMAIL_VERIFICATION_TEMPLATE`.
- `models.py` — request schemas (`PasswordResetEmailRequest`, `EmailVerificationEmailRequest`), `EmailSendResult`, `EventPublisher` (ABC).
- `render.py` — `render_template` (`{{name}}` substitution, `html.escape`, `missing_variable:<name>` / `malformed_template` errors), `RenderedTemplate`.
- `message.py` — `build_message` (multipart/alternative, From from settings), `validate_recipient`.
- `feature_settings.py` — `register_settings` (8 SettingDefinitions), `resolve_mail_config` (live read + hardcoded fallback), `MailConfig`.
- `transport.py` — `SmtpTransport` ABC + `SmtpTransportImpl` (smtplib-backed, ordered exception mapping to secret-free reasons).
- `events.py` — `MailEvent` / `EmailSent` / `EmailFailed` (frozen Pydantic, `occurred_at` default `now(UTC)`).
- `service.py` — `MailService` (`@logged_class(slow_threshold_ms=5000, include_args=False)`): `send_email`, `send_password_reset_email`, `send_email_verification_email`.
- `__init__.py` — public API (NFR-003 contract).

### GREEN state
`uv run pytest tests/acceptance/mail/ tests/property/mail/ tests/unit/mail/ tests/contract/mail/ tests/integration/mail/` → **31 passed, 8 failed** (initial implementation run; the 8 failures are the test-design issues documented below, resolved by the user-approved test-harness fixes + the logging-coverage data-model/tracing changes in the GREEN evidence).

All 11 unit tests (EDGE-001..010) pass. All acceptance rendering/send/validation/settings/transport tests pass. All contract performance/public-API/logging tests pass. Property INV-001/002/005 pass.

### FINDINGS — 8 failing tests are test-design issues, not implementation defects

**Category A — 2 tests fundamentally un-passable (property strategy too broad).**
`tests/property/mail/test_secrets.py::test_inv_003_no_password_in_observable_output` and `::test_inv_004_no_body_in_events` use `@given(password=st.text(min_size=1, max_size=64))` / `@given(token=st.text(min_size=1, max_size=64))`. The strategy generates single characters. The assertion `password not in event_text(event)` (where `event_text` is `event.model_dump_json()`) then fails for any single character that appears in the event payload — e.g. `password='0'` appears in the `occurred_at` timestamp (`...T12:57:04.629778Z`), and `password='a'` appears in the `to` field (`a@example.com`). The spec (REQ-013) requires events to carry `to` + `occurred_at`, so the payload necessarily contains these characters. No implementation can make `password not in event_text` hold for `password='0'`/`'a'` while still carrying `to`/`occurred_at`. These two tests need a narrower strategy (e.g. a fixed high-entropy secret that cannot collide with the payload) — they cannot be satisfied as written.

**Category B — 6 tests fail due to cross-test settings persistence (test isolation).**
`tests/acceptance/mail/test_settings.py::test_ac_001_register_settings`, `test_events.py::test_ac_015_non_sensitive_events`, `test_logging.py::test_ac_016_no_secrets_in_log_records`, `test_message.py::test_ac_019_multipart_alternative`, `tests/contract/mail/test_secrets.py::test_nfr_002_no_secrets_in_logs_or_events`, `tests/integration/mail/test_concurrency.py::test_nfr_005_concurrent_send_thread_safety`. Root cause: the settings singleton's default `YamlValueRepository("settings")` persists values to `settings/values.yaml` on disk. The per-test conftest (`tests/acceptance/mail/conftest.py`) calls `reset_settings_registry()`, which only nulls the module singleton (`_registry[0] = None`) — it does NOT clear the on-disk file. So when an earlier test in the same run writes a value (notably `test_ac_011_empty_smtp_host` sets `mail.smtp_host=""`), that value is reloaded from disk by the next test's freshly-created registry, overriding the registered default. Concretely, the later tests observe `mail.smtp_host==""` and `send_email` raises `MailConfigurationError(smtp_host_empty)`. Each of these 6 tests passes in isolation (clean `settings/` dir) and fails only within the full suite. This is a test-isolation gap in the test harness (the reset does not clear the YAML value store), not a defect in the mail implementation.

### GREEN evidence (full suite)

- **Full test suite:** `uv run pytest tests/` → **397 passed** (0 failed), including the 39 spec-derived mail tests and the logging feature's forward-looking trace policy test `tests/acceptance/logging_coverage/test_new_classes_traced.py::test_new_public_classes_traced_by_default`.
- **Lint:** `uv run ruff check .` → **All checks passed!**
- **Type checks:** `uv run mypy src/` → **Success: no issues found in 43 source files**.
- **Commit:** `09da8be` — `feat(mail-service): achieve GREEN — MailConfig as pydantic model + test-harness isolation`.

**Data-model / tracing changes (mail feature only; no cross-feature test edits):**

- `MailConfig` (`src/backend/mail/feature_settings.py`) was changed from a frozen `@dataclass` to a **frozen pydantic `BaseModel`** (`model_config = ConfigDict(frozen=True)`, same 8 fields, same public name) — **user-approved**. This satisfies the logging feature's forward-looking trace policy (AC-012: every public class is traced or an excluded kind — pydantic `BaseModel` is the recognized data-model exclusion) without editing the logging feature's test, and is consistent with the codebase's dominant data-model type.
- `RenderedTemplate` (`src/backend/mail/render.py`) was likewise converted to a frozen pydantic `BaseModel` (pure data model, same 3 fields, keyword construction unchanged).
- `EventPublisher` (`src/backend/mail/models.py`), `SmtpTransport` and `SmtpTransportImpl` (`src/backend/mail/transport.py`) are traced with `@logged_class` (codebase convention for ABCs; `SmtpTransportImpl` uses `include_args=False` so the SMTP password never appears in log records — NFR-002). `functools.wraps` inside `@logged` preserves `__isabstractmethod__`, so the ABCs remain abstract.
- `src/backend/mail/__init__.py`: `PasswordResetEmailRequest` added to `__all__` (public API, NFR-003) and `__all__` sorted (RUF022).

**Test-harness fixes (mail tests only; no test weakened or deleted):**

- `tests/property/mail/test_secrets.py`: the INV-003/INV-004 property strategies now draw from a high-entropy non-ASCII alphabet (`min_size=8`, `max_size=64`) — the invariant (the secret never appears in observable output) is preserved and is now satisfiable, since a high-entropy secret cannot collide with the ASCII `to`/`occurred_at` payload content. A `# noqa: RUF001` marks the intentionally ambiguous Greek letters.
- `tests/mail_test_helpers.py` + the 5 mail conftests: a new `setup_isolated_registry()` backs the settings registry singleton with a temp-dir `YamlValueRepository`, so no mail test persists to the shared `settings/` directory and no value leaks across tests (resolves the 6 cross-test settings-persistence failures).

### Status
DONE — GREEN achieved and recorded: full suite 397 passed, lint clean, type checks clean (commit `09da8be`). The 8 Phase-4 findings are resolved by the user-approved test-harness fixes and the mail-feature data-model/tracing changes above; no test was weakened, deleted, or edited outside the mail feature.

## Phase 5 — Verify (FEATURE)

- **Status:** DONE (full gate set green; spec coverage = 100%).
- **Date:** 2026-09-12
- **Gate-set result:** PASSED — full suite 397/397, acceptance 170/170, property 42/42, contract 32/32, lint clean, types clean, verify_spec PASS. Spec coverage = 100% (every REQ/AC has a GREEN test).

### Specification coverage (MUST be 100%) — **100%**

Every `REQ-XXX` has at least one GREEN test (traceability matrix `docs/verification/traceability.md`, "Mail Service Matrix"):

| REQ | AC | GREEN test |
|-----|----|-----------|
| REQ-001 | AC-001 | `test_ac_001_register_settings` |
| REQ-002 | AC-002, AC-003 | `test_ac_002_live_read_modified_host`, `test_ac_003_fallback_unregistered_host` |
| REQ-003 | AC-004 | `test_ac_004_core_send_success` |
| REQ-004 | AC-005 | `test_ac_005_password_reset_email` |
| REQ-005 | AC-006 | `test_ac_006_email_verification_email` |
| REQ-006 | AC-007 | `test_ac_007_feature_specific_template` |
| REQ-007 | AC-008 | `test_ac_008_template_rendering` |
| REQ-008 | AC-009 | `test_ac_009_invalid_recipient` |
| REQ-009 | AC-010 | `test_ac_010_missing_variable` |
| REQ-010 | AC-011 | `test_ac_011_empty_smtp_host` |
| REQ-011 | AC-012 | `test_ac_012_transport_failure` |
| REQ-012 | AC-013, AC-014 | `test_ac_013_email_sent_event`, `test_ac_014_email_failed_event` |
| REQ-013 | AC-015 | `test_ac_015_non_sensitive_events` |
| REQ-014 | AC-016 | `test_ac_016_no_secrets_in_log_records` |
| REQ-015 | AC-017 | `test_ac_017_public_api_stable` |
| REQ-016 | AC-018 | `test_ac_018_concurrent_send` |
| REQ-017 | AC-019 | `test_ac_019_multipart_alternative` |

All 17 REQ covered → **spec coverage = 100%**. All 19 AC have a GREEN acceptance test. In addition, 5 INV (property), 10 EDGE (unit), and 5 NFR (contract/integration) tests are GREEN.

### Gate-set evidence

| Gate | Command | Result |
|------|---------|--------|
| Full suite | `uv run pytest tests/` | **397 passed** |
| Acceptance | `uv run pytest tests/acceptance/` | **170 passed** |
| Property | `uv run pytest tests/property/` | **42 passed** |
| Contract | `uv run pytest tests/contract/` | **32 passed** |
| Lint | `uv run ruff check .` | **All checks passed!** |
| Type checks | `uv run mypy src/` | **Success: no issues found in 43 source files** |
| Spec validation | `uv run python scripts/verify_spec.py docs/specs/mail-service.md` | **PASS** (17 REQ→AC, 19 AC→test, 5 INV→property) |
| Coverage | `uv run pytest tests/ --cov` | **397 passed**; mail feature 88–100% (render 96%, service 96%, transport 88%, rest 100%); total 94% |
| Architecture rules | `uv run pytest tests/architecture/` | **N/A** — no `tests/architecture/` category exists in this project (no test files, no CI reference) |

**Commits:** `09da8be` (implementation: MailConfig as pydantic model + test-harness isolation), `391180b` (Phase 4 GREEN evidence).

### Pre-existing flaky failures (other features — OUT OF SCOPE for mail-service)

During the Phase 5 runs, two **one-off** property-test failures occurred in **other** features, not mail:

- `tests/property/settings/test_settings_properties.py::test_inv_005_slider_grid_valid` (settings feature)
- `tests/property/eventbus/test_eventbus_properties.py::test_inv_003_queue_bounded` (eventbus feature)

Classification (pre-existing, not a regression from this change):
- The mail change touched **zero** settings/eventbus source or tests — `git diff <merge-base>..HEAD -- src/backend/settings/ src/backend/eventbus/ tests/property/settings/ tests/property/eventbus/` is **empty** (byte-identical to base).
- Both tests **pass in isolation** and on re-run (property suite stable 42/42 across two re-runs; the dedicated full-suite run passed 397/397).
- These are hypothesis property tests with a random seed; the one-off failures are characteristic flakiness, not a defect introduced by mail-service.

Per the verify protocol, pre-existing failures in other features are recorded here and are **not** fixed as part of this change. The mail-service gate set (all mail tests GREEN, spec coverage = 100%) is satisfied.

### Status
DONE — full gate set green, spec coverage = 100% (17/17 REQ, 19/19 AC GREEN). Two pre-existing flaky property tests in other features (settings, eventbus) recorded as out of scope. No test was weakened, deleted, or edited; no implementation source changed in this phase.

## Phase 6 — Review (FEATURE)

- **Status:** CLEAN (no unresolved findings)
- **Date:** 2026-09-12
- **Reviewer:** Phase 6 (REVIEW) subagent
- **Normative basis:** approved spec `docs/specs/mail-service.md` (merged via PR #22; `git log main -- docs/specs/mail-service.md` non-empty; spec file byte-identical to `main`).
- **Fresh evidence (this phase):** mail suites **39 passed** (`tests/{acceptance,property,unit,contract,integration}/mail/`); full suite **397 passed**; working tree clean.

### 1. Normative basis compliance (spec compliance) — PASS

The implementation matches the approved spec. Every normative requirement is implemented with no more and no less:

| Area | Spec basis | Implementation | Match |
|------|-----------|----------------|-------|
| Core send | REQ-003, D4 | `MailService.send_email`: validate recipient → render → resolve live config → host check → build multipart/alternative → send → publish `EmailSent` → return `EmailSendResult`; on failure publish `EmailFailed` (kind) + re-raise | ✓ |
| High-level ops | REQ-004/005, D5 | `send_password_reset_email` / `send_email_verification_email` compose the core send with `PASSWORD_RESET_TEMPLATE` / `EMAIL_VERIFICATION_TEMPLATE` | ✓ |
| Feature-specific | REQ-006, D6 | A feature provides its own `EmailTemplate` and calls `send_email` | ✓ |
| Rendering | REQ-007, D3 | `render_template`: `{{name}}` substitution, `html.escape` on values, `missing_variable:<name>` / `malformed_template` errors | ✓ |
| Recipient validation | REQ-008 | `validate_recipient` (email-validator, format-only) → `MailTemplateError("invalid_recipient")` | ✓ |
| Missing variable | REQ-009 | `render_template` → `MailTemplateError("missing_variable:<name>")` | ✓ |
| SMTP config validation | REQ-010, D7 | `resolve_mail_config` (live read + fallback); empty host → `MailConfigurationError("smtp_host_empty")` | ✓ |
| Transport | REQ-011, D1 | `SmtpTransport` ABC + `SmtpTransportImpl` (smtplib, connects per send, auth when username present, ordered exception mapping to secret-free reasons) | ✓ |
| Events | REQ-012/013, D9 | `EmailSent`/`EmailFailed` (frozen, non-sensitive) published to the injected `EventPublisher`; `None` publisher = no events | ✓ |
| Tracing | REQ-014, D10 | `MailService` traced `@logged_class(slow_threshold_ms=5000, include_args=False)` | ✓ |
| Public API | REQ-015, NFR-003 | service, models, errors, transport ABC, events, built-in templates exposed | ✓ |
| Concurrency | REQ-016, D13 | transport created per send; no long-lived connection | ✓ |
| Message | REQ-017 | `build_message`: multipart/alternative (text + HTML), From from `mail.from_name`/`mail.smtp_from` | ✓ |
| Invariants | INV-001..005 | deterministic render, XSS-safe substitution, secret-free output, body-free events, send independence | ✓ |
| Edge cases | EDGE-001..010 | invalid recipient, missing/malformed template, empty host, connection/auth/protocol/timeout, None bus, failure-then-success | ✓ |
| NFRs | NFR-001..005 | performance budget, security, contract, observability, reliability | ✓ |

**No behavior beyond the spec.** The only surface beyond the spec's *minimum* public API is a set of internal helpers (see Observations) and the tracing of the transport/publisher ABCs (required by the logging feature's forward-looking trace policy). None introduces new externally-observable behavior.

### 2. Traceability — PASS

- **Every `REQ-XXX` has ≥1 GREEN test.** `docs/verification/traceability.md` "Mail Service Matrix": all 39 rows GREEN (19 AC, 5 INV, 10 EDGE, 5 NFR). All 17 REQ covered.
- **Every acceptance test traces to a normative requirement.** Each test is named after and asserts its AC/INV/EDGE/NFR.
- **No orphaned tests, no missing links.**

### 3. Acceptance tests NOT weakened or deleted — PASS

All **39** spec-derived tests exist and pass (verified by reading each test and running the mail suites: 39 passed). Compared against the Phase 3 RED commit (`f896479`), the only post-RED test modifications are (all within the mail feature; **none weaken or delete a test**):

| File(s) | Change | Assessment |
|---------|--------|------------|
| 5 × `tests/*/mail/conftest.py` | autouse fixture `reset_registry()` → `setup_isolated_registry()` | **Stronger** isolation (temp-dir `YamlValueRepository`); no assertion changed. Prevents cross-test settings persistence. Not a weakening. |
| `tests/mail_test_helpers.py` | added `setup_isolated_registry()` helper | New helper (no test logic removed). Not a weakening. |
| `tests/property/mail/test_secrets.py` | INV-003/INV-004 strategy: `st.text(min_size=1, max_size=64)` → `st.text(alphabet=<high-entropy non-ASCII>, min_size=8, max_size=64)` | **Correctness fix, not a weakening** (see analysis below). |

**INV-003/INV-004 strategy-change analysis.** The invariant under test is "the SMTP password / email body (with token) never appears in observable output (result, error, events)". The test sets the secret, performs a send, and asserts the secret is *not* a substring of the output. The original strategy (`st.text(min_size=1, ...)`) generates single/short characters that are substrings of the *fixed* ASCII payload content (e.g. `'a'` in `to='a@example.com'`, `'0'` in the `occurred_at` timestamp), so `secret not in output` failed **even with a correct implementation** (documented as "fundamentally un-passable" in the Phase 4 findings). The fix constrains the alphabet to high-entropy non-ASCII letters (`min_size=8`) that cannot collide with the ASCII payload, making the test correct while:
- preserving the invariant (still asserts the secret never appears in the output),
- **not reducing the ability to catch a real leak** (if the implementation leaks the secret, it appears in the output and the assertion fails, regardless of alphabet),
- increasing `min_size` (1 → 8).

Conclusion: no acceptance test was weakened, deleted, or edited to make the implementation pass. The single strategy change is a test-correctness fix (the original was un-passable), and the invariant is fully preserved.

### 4. Feature boundaries — PASS

- The mail feature imports **only public APIs** of `backend.logging` (`logged`, `logged_class`) and `backend.settings` (`SettingsRegistry`, `get_settings_registry`, `SettingDefinition`, `SettingKind`). No internal (`_`-module) imports.
- The event bus is consumed via the **structural `EventPublisher` protocol** (the real bus is injected at wiring time), consistent with the spec and with user-management/authentication. The mail feature does not import `backend.eventbus`.
- The change **does not modify** `src/backend/{settings,logging,eventbus,usermanagement,authentication}/` or `src/frontend/` (`git diff main...HEAD` over those paths is empty).
- **No other feature imports `backend.mail`** (mail is a new provider; nothing consumes it yet).

### 5. Architecture — PASS

- The mail feature uses a **flat module layout** (`errors`, `events`, `feature_settings`, `message`, `models`, `render`, `service`, `templates`, `transport`) — no premature `model/`/`services/` directories.
- This is **consistent with the other shared features** (`logging`, `settings`, `eventbus` all use flat modules) and appropriate for the feature's size/complexity (each module has a single responsibility).

### 6. Observability — PASS

- `MailService` is traced with `@logged_class(slow_threshold_ms=5000, include_args=False)` (REQ-014, ADR-047). The SMTP password and tokens never appear in log records (verified by AC-016 / NFR-002).
- `SmtpTransport`/`SmtpTransportImpl` are traced with `include_args=False` (the password never appears in log records — NFR-002). `register_settings` is traced with `@logged(slow_threshold_ms=5)`.
- The transport/publisher ABC tracing is required by the logging feature's forward-looking trace policy (`tests/acceptance/logging_coverage/test_new_public_classes_traced.py`), which the mail feature satisfies without editing the logging feature.

### Observations (not findings; within the spec's design and codebase conventions)

1. **Public API is a superset of the spec's minimum.** `__all__` additionally exposes internal helpers referenced by the spec's design decisions: `MailConfig`/`resolve_mail_config` (D7 live-read), `build_message`/`validate_recipient` (D4/REQ-008/REQ-017), `render_template`/`RenderedTemplate` (D3/REQ-007), and `SmtpTransportImpl` (D1 default). These do not introduce new externally-observable behavior; they are implementation helpers made importable. Acceptable.
2. **`SmtpTransport`, `SmtpTransportImpl`, and `EventPublisher` are traced** (`@logged_class`). Required by the logging feature's forward-looking trace policy and consistent with codebase conventions; `include_args=False` on the secret-handling transport keeps the SMTP password out of log records.

### Findings and resolutions

| # | Severity | Finding | Resolution |
|---|----------|---------|------------|
| 1 | — | No blocking findings. | — |

All review checks (spec compliance, traceability, acceptance-test integrity, feature boundaries, architecture, observability) **PASS**. The two observations are within the spec's design and codebase conventions and require no action.

### Review gate

**The review report is CLEAN** (no unresolved findings). Proceed to: (a) document the reusable shared capability in `AGENTS.md`, (b) bump the version (FEATURE → minor), (c) open a PR to `main` for human review/merge.

## Phase history

| Phase | Status | Evidence |
|-------|--------|----------|
| 0 Classify | DONE | this file |
| 1 Specify | DONE | `docs/specs/mail-service.md` + PR #22 (this file) |
| 2 Decompose | DONE | ADR-043..047 + `docs/tasks/mail-service.tasks.json` + `.github/task-runner/tasks.json` (this file) |
| 3 Test & RED | DONE | 39 spec-derived tests RED (`ModuleNotFoundError: backend.mail`) + this file |
| 4 Implement | DONE | full suite **397 passed**, `ruff check .` clean, `mypy src/` clean — commit `09da8be` (this file) |
| 5 Verify | DONE | full gate set green (397/397, 170, 42, 32; lint+types clean; verify_spec PASS), **spec coverage = 100%** (17/17 REQ, 19/19 AC GREEN) + this file |
| 6 Review | DONE | review report CLEAN (no unresolved findings); spec compliance, traceability, acceptance-test integrity, feature boundaries, architecture, observability all PASS + this file |
