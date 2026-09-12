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
  commit: <phase-3 commit>

#### AC-002
RED:
  command: uv run pytest tests/acceptance/mail/test_settings.py::test_ac_002_live_read_modified_host -v
  result: FAILED (ModuleNotFoundError: No module named 'backend.mail')
  commit: <phase-3 commit>

#### AC-003
RED:
  command: uv run pytest tests/acceptance/mail/test_settings.py::test_ac_003_fallback_unregistered_host -v
  result: FAILED (ModuleNotFoundError: No module named 'backend.mail')
  commit: <phase-3 commit>

#### AC-004
RED:
  command: uv run pytest tests/acceptance/mail/test_send.py::test_ac_004_core_send_success -v
  result: FAILED (ModuleNotFoundError: No module named 'backend.mail')
  commit: <phase-3 commit>

#### AC-005
RED:
  command: uv run pytest tests/acceptance/mail/test_high_level.py::test_ac_005_password_reset_email -v
  result: FAILED (ModuleNotFoundError: No module named 'backend.mail')
  commit: <phase-3 commit>

#### AC-006
RED:
  command: uv run pytest tests/acceptance/mail/test_high_level.py::test_ac_006_email_verification_email -v
  result: FAILED (ModuleNotFoundError: No module named 'backend.mail')
  commit: <phase-3 commit>

#### AC-007
RED:
  command: uv run pytest tests/acceptance/mail/test_send.py::test_ac_007_feature_specific_template -v
  result: FAILED (ModuleNotFoundError: No module named 'backend.mail')
  commit: <phase-3 commit>

#### AC-008
RED:
  command: uv run pytest tests/acceptance/mail/test_render.py::test_ac_008_template_rendering -v
  result: FAILED (ModuleNotFoundError: No module named 'backend.mail')
  commit: <phase-3 commit>

#### AC-009
RED:
  command: uv run pytest tests/acceptance/mail/test_validation.py::test_ac_009_invalid_recipient -v
  result: FAILED (ModuleNotFoundError: No module named 'backend.mail')
  commit: <phase-3 commit>

#### AC-010
RED:
  command: uv run pytest tests/acceptance/mail/test_validation.py::test_ac_010_missing_variable -v
  result: FAILED (ModuleNotFoundError: No module named 'backend.mail')
  commit: <phase-3 commit>

#### AC-011
RED:
  command: uv run pytest tests/acceptance/mail/test_config.py::test_ac_011_empty_smtp_host -v
  result: FAILED (ModuleNotFoundError: No module named 'backend.mail')
  commit: <phase-3 commit>

#### AC-012
RED:
  command: uv run pytest tests/acceptance/mail/test_transport.py::test_ac_012_transport_failure -v
  result: FAILED (ModuleNotFoundError: No module named 'backend.mail')
  commit: <phase-3 commit>

#### AC-013
RED:
  command: uv run pytest tests/acceptance/mail/test_events.py::test_ac_013_email_sent_event -v
  result: FAILED (ModuleNotFoundError: No module named 'backend.mail')
  commit: <phase-3 commit>

#### AC-014
RED:
  command: uv run pytest tests/acceptance/mail/test_events.py::test_ac_014_email_failed_event -v
  result: FAILED (ModuleNotFoundError: No module named 'backend.mail')
  commit: <phase-3 commit>

#### AC-015
RED:
  command: uv run pytest tests/acceptance/mail/test_events.py::test_ac_015_non_sensitive_events -v
  result: FAILED (ModuleNotFoundError: No module named 'backend.mail')
  commit: <phase-3 commit>

#### AC-016
RED:
  command: uv run pytest tests/acceptance/mail/test_logging.py::test_ac_016_no_secrets_in_log_records -v
  result: FAILED (ModuleNotFoundError: No module named 'backend.mail')
  commit: <phase-3 commit>

#### AC-017
RED:
  command: uv run pytest tests/acceptance/mail/test_public_api.py::test_ac_017_public_api_stable -v
  result: FAILED (ModuleNotFoundError: No module named 'backend.mail')
  commit: <phase-3 commit>

#### AC-018
RED:
  command: uv run pytest tests/acceptance/mail/test_concurrency.py::test_ac_018_concurrent_send -v
  result: FAILED (ModuleNotFoundError: No module named 'backend.mail')
  commit: <phase-3 commit>

#### AC-019
RED:
  command: uv run pytest tests/acceptance/mail/test_message.py::test_ac_019_multipart_alternative -v
  result: FAILED (ModuleNotFoundError: No module named 'backend.mail')
  commit: <phase-3 commit>

#### INV-001
RED:
  command: uv run pytest tests/property/mail/test_render.py::test_inv_001_rendering_deterministic -v
  result: FAILED (ModuleNotFoundError: No module named 'backend.mail')
  commit: <phase-3 commit>

#### INV-002
RED:
  command: uv run pytest tests/property/mail/test_render.py::test_inv_002_xss_safe_substitution -v
  result: FAILED (ModuleNotFoundError: No module named 'backend.mail')
  commit: <phase-3 commit>

#### INV-003
RED:
  command: uv run pytest tests/property/mail/test_secrets.py::test_inv_003_no_password_in_observable_output -v
  result: FAILED (ModuleNotFoundError: No module named 'backend.mail')
  commit: <phase-3 commit>

#### INV-004
RED:
  command: uv run pytest tests/property/mail/test_secrets.py::test_inv_004_no_body_in_events -v
  result: FAILED (ModuleNotFoundError: No module named 'backend.mail')
  commit: <phase-3 commit>

#### INV-005
RED:
  command: uv run pytest tests/property/mail/test_independence.py::test_inv_005_failure_independence -v
  result: FAILED (ModuleNotFoundError: No module named 'backend.mail')
  commit: <phase-3 commit>

#### EDGE-001
RED:
  command: uv run pytest tests/unit/mail/test_validation.py::test_edge_001_invalid_recipient -v
  result: FAILED (ModuleNotFoundError: No module named 'backend.mail')
  commit: <phase-3 commit>

#### EDGE-002
RED:
  command: uv run pytest tests/unit/mail/test_validation.py::test_edge_002_missing_variable -v
  result: FAILED (ModuleNotFoundError: No module named 'backend.mail')
  commit: <phase-3 commit>

#### EDGE-003
RED:
  command: uv run pytest tests/unit/mail/test_validation.py::test_edge_003_malformed_template -v
  result: FAILED (ModuleNotFoundError: No module named 'backend.mail')
  commit: <phase-3 commit>

#### EDGE-004
RED:
  command: uv run pytest tests/unit/mail/test_config.py::test_edge_004_empty_smtp_host -v
  result: FAILED (ModuleNotFoundError: No module named 'backend.mail')
  commit: <phase-3 commit>

#### EDGE-005
RED:
  command: uv run pytest tests/unit/mail/test_transport.py::test_edge_005_connection_refused -v
  result: FAILED (ModuleNotFoundError: No module named 'backend.mail')
  commit: <phase-3 commit>

#### EDGE-006
RED:
  command: uv run pytest tests/unit/mail/test_transport.py::test_edge_006_auth_failure -v
  result: FAILED (ModuleNotFoundError: No module named 'backend.mail')
  commit: <phase-3 commit>

#### EDGE-007
RED:
  command: uv run pytest tests/unit/mail/test_transport.py::test_edge_007_protocol_error -v
  result: FAILED (ModuleNotFoundError: No module named 'backend.mail')
  commit: <phase-3 commit>

#### EDGE-008
RED:
  command: uv run pytest tests/unit/mail/test_transport.py::test_edge_008_timeout -v
  result: FAILED (ModuleNotFoundError: No module named 'backend.mail')
  commit: <phase-3 commit>

#### EDGE-009
RED:
  command: uv run pytest tests/unit/mail/test_events.py::test_edge_009_none_event_bus -v
  result: FAILED (ModuleNotFoundError: No module named 'backend.mail')
  commit: <phase-3 commit>

#### EDGE-010
RED:
  command: uv run pytest tests/unit/mail/test_independence.py::test_edge_010_failure_then_success -v
  result: FAILED (ModuleNotFoundError: No module named 'backend.mail')
  commit: <phase-3 commit>

#### NFR-001
RED:
  command: uv run pytest tests/contract/mail/test_performance.py::test_nfr_001_preparation_performance_budget -v
  result: FAILED (ModuleNotFoundError: No module named 'backend.mail')
  commit: <phase-3 commit>

#### NFR-002
RED:
  command: uv run pytest tests/contract/mail/test_secrets.py::test_nfr_002_no_secrets_in_logs_or_events -v
  result: FAILED (ModuleNotFoundError: No module named 'backend.mail')
  commit: <phase-3 commit>

#### NFR-003
RED:
  command: uv run pytest tests/contract/mail/test_public_api.py::test_nfr_003_public_api_stable -v
  result: FAILED (ModuleNotFoundError: No module named 'backend.mail')
  commit: <phase-3 commit>

#### NFR-004
RED:
  command: uv run pytest tests/contract/mail/test_logging.py::test_nfr_004_service_traced -v
  result: FAILED (ModuleNotFoundError: No module named 'backend.mail')
  commit: <phase-3 commit>

#### NFR-005
RED:
  command: uv run pytest tests/integration/mail/test_concurrency.py::test_nfr_005_concurrent_send_thread_safety -v
  result: FAILED (ModuleNotFoundError: No module named 'backend.mail')
  commit: <phase-3 commit>

## Phase history

| Phase | Status | Evidence |
|-------|--------|----------|
| 0 Classify | DONE | this file |
| 1 Specify | DONE | `docs/specs/mail-service.md` + PR #22 (this file) |
| 2 Decompose | DONE | ADR-043..047 + `docs/tasks/mail-service.tasks.json` + `.github/task-runner/tasks.json` (this file) |
| 3 Test & RED | DONE | 39 spec-derived tests RED (`ModuleNotFoundError: backend.mail`) + this file |
