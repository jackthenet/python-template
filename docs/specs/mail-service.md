# Spec: Mail Service (Backend)

## Changelog
- v1 (2026-09-07): Initial specification.

## 1. Overview & Objectives
- **Feature Name:** Mail Service (Backend)
- **Target Component:** `src/backend/mail/`
- **Goal:** Provide a central, reusable email-sending capability for the application — backend only — with central SMTP configuration through the existing settings feature, a reusable email-sending service other features consume, email templates with variable substitution, high-level operations for password-reset and email-verification emails, and support for feature-specific emails without requiring each feature to implement its own mail-sending logic.
- **Scope:** In-process Python service (no HTTP layer). Central SMTP configuration registered through the shared settings feature (`register_settings`) and read live on each send; a reusable `MailService` exposing a core `send_email` operation plus high-level `send_password_reset_email` and `send_email_verification_email` operations; email templates (`EmailTemplate`) with `{{variable}}` substitution (HTML-escaped values); a `SmtpTransport` ABC (smtplib-backed default, injectable fake for tests); a `MailError` hierarchy (`MailConfigurationError`, `MailTransportError`, `MailTemplateError`); typed lifecycle events (`EmailSent`, `EmailFailed`) published to the injected event publisher; observability via the shared logging feature (`@logged_class`, `include_args=False`).
- **Feature Brief (from adversarial interrogation):**
  - **Goals:** a single place to configure and send email; other features (e.g., authentication, user-management) consume it without owning SMTP logic; template-driven emails with variables; high-level operations for the two application-critical emails (password reset, email verification); feature-specific emails via a provided template + the core send; central, live, validated configuration; safe handling of secrets (SMTP password) and tokens (in email bodies); testable without a real SMTP server.
  - **Constraints:** backend only (no HTTP layer, no frontend); reuse the existing settings feature (register SMTP settings via `register_settings(registry)`, read them live on each use — do NOT create a new configuration mechanism); reuse the existing logging feature (`@logged_class`, `include_args=False`); reuse the existing event bus (publish `EmailSent`/`EmailFailed` via the structural `EventPublisher` protocol); do NOT modify the user-management, authentication, settings, logging, or event-bus features; do NOT create duplicate configuration, user, authentication, or email functionality; keep all changes isolated to this backend feature (`src/backend/mail/`, its tests, its spec, its verification/traceability records); the mail service is a *provider* other features consume, not a modifier of them; the SMTP transport is abstracted behind an ABC (seam for testability); the SMTP password is sensitive (never in logs/events); the email body contains tokens (never in events).
  - **Out of scope:** frontend; HTTP/REST/GraphQL API layer; the SMTP server itself (delivery infrastructure); email tracking (open/click); attachments; CC/BCC; multiple recipients per message; queueing/retry of failed sends; i18n of template text; a full templating engine (Jinja2) — a small, secure `{{variable}}` substitution is used instead; persistence of sent emails; token generation (the authentication/user-management feature generates tokens; the mail service only sends the email given a URL/token); URL construction (the caller provides the full `reset_url`/`verification_url`; the mail service does not build URLs and therefore does not need a base-URL setting).
  - **Edge cases:** invalid recipient; missing template variable; malformed template (a `{{` without a closing `}}`); empty SMTP host; SMTP connection failure; SMTP authentication failure; SMTP protocol error; SMTP timeout; unregistered settings (fall back to hardcoded defaults); a failure in one send MUST NOT affect subsequent sends (each send is independent — the transport is created per send, no long-lived connection).

## 2. Architecture & Design Decisions
- **Design Pattern:** Service + transport + templates. `MailService` (use cases, domain rules) depends on: a `SmtpTransport` ABC (the physical SMTP send; smtplib-backed default, injectable fake for tests); the shared settings feature (live-read of SMTP configuration); and the shared event bus (typed lifecycle events via the structural `EventPublisher` protocol). The service composes: validate recipient → render template → build a `multipart/alternative` `EmailMessage` → resolve SMTP configuration live → send via the transport → publish the lifecycle event.
- **Dependencies:** `pydantic>=2.13.1` (request/representation models), `email-validator>=2.3.0` (recipient validation; already a project dependency), the Python standard library `email.message`/`email.utils`/`smtplib`/`socket` (no new third-party SMTP dependency — `smtplib` is in the standard library); uses `backend.settings` (public API only, via the feature-owned `register_settings` and the live-read pattern), `backend.logging` (`@logged`, `@logged_class`), and the structural `EventPublisher` protocol (the real event bus is injected at wiring time, consistent with user-management and authentication). No Jinja2 (a small, secure `{{variable}}` substitution is used instead — see D3). No web framework.
- **Constraints:** The service API MUST NOT expose the SMTP password or the raw email body. The SMTP password MUST NOT appear in log records, events, or error messages. The rendered email body (which contains reset/verification tokens) MUST NOT appear in events. The service code MUST reference only the `SmtpTransport` ABC (the SMTP backend must be swappable). The mail service MUST NOT import or modify the user-management, authentication, settings, logging, or event-bus features beyond their public APIs (it consumes them; it does not change them).
- **Design Decisions (WHAT; WHY goes to ADRs in Phase 2):**
  - D1: SMTP transport abstraction — `SmtpTransport` ABC (a single `send(message)` operation) + `SmtpTransportImpl` (the smtplib-backed default; connects per send, authenticates when credentials are present, sends, closes). The service accepts an optional `transport` in its constructor; when `None` it builds a `SmtpTransportImpl` from the live settings on each send. This is the seam for testability (a fake transport in tests records messages without a network).
  - D2: Templates — `EmailTemplate` (frozen Pydantic model: `name`, `subject`, `body_html`, `body_text`; all with `{{variable}}` placeholders). The message is always `multipart/alternative` (text + HTML), so both `body_html` and `body_text` are required.
  - D3: Template rendering — a small, secure `{{variable}}` substitution (no Jinja2). Each `{{variable}}` is replaced with the corresponding context value, HTML-escaped (the secure default against XSS in HTML emails). A `{{variable}}` with no corresponding context value raises `MailTemplateError`. A malformed template (a `{{` without a closing `}}`) raises `MailTemplateError`. The template itself is trusted (written by the feature developer); only the substituted values are escaped.
  - D4: Core send — `send_email(to, template, context)` composes: validate recipient (REQ-008) → render template (REQ-007/REQ-009) → build a `multipart/alternative` `EmailMessage` (From from settings, REQ-017) → resolve SMTP configuration live (REQ-002/REQ-010) → send via the transport (REQ-011) → publish the lifecycle event (REQ-012/REQ-013).
  - D5: High-level operations — `send_password_reset_email(to, display_name, reset_url)` and `send_email_verification_email(to, display_name, verification_url)` compose the core send with the built-in `PASSWORD_RESET_TEMPLATE` and `EMAIL_VERIFICATION_TEMPLATE` respectively. They are the reusable high-level operations the application invokes (template + send), NOT modifications to the authentication feature.
  - D6: Feature-specific emails — a feature provides its own `EmailTemplate` and calls the core `send_email` operation. This satisfies "support for feature-specific emails without requiring each feature to implement its own mail-sending logic."
  - D7: Live settings — the mail service reads its SMTP settings live from the settings registry on each send (per the live-read pattern used by logging and user-management). Unregistered settings fall back to hardcoded defaults. The mail service validates the SMTP host is non-empty at send time (defense in depth; the settings feature enforces the kind, the mail service enforces usability).
  - D8: Error hierarchy — `MailError` (base) + `MailConfigurationError` (SMTP settings missing/invalid at send time), `MailTransportError` (SMTP delivery failed: connection, authentication, SMTP protocol error, or timeout), `MailTemplateError` (the email could not be prepared: invalid recipient, missing/unknown template variable, or malformed template). All messages are secret-free.
  - D9: Events — `EmailSent`/`EmailFailed` (typed, frozen Pydantic models) published to the injected `EventPublisher` (structural protocol; the real event bus is injected at wiring time, consistent with authentication). A `None` publisher means no events. Events carry non-sensitive data only (no email body, no rendered subject, no token, no SMTP password).
  - D10: Observability — the service is traced with `@logged_class` (`include_args=False`, `slow_threshold_ms=5000` — the SMTP send is network-dependent, so a high threshold avoids false "slow" warnings). The SMTP password and tokens never appear in log records.
  - D11: Validation — schema-level (Pydantic request models → `pydantic.ValidationError` for invalid email/empty fields) + service-level (recipient validation, template rendering, SMTP configuration → the `MailError` hierarchy).
  - D12: No persistence — the mail service does not store sent emails (no database, no file).
  - D13: Independence — each send is independent: the transport is created per send (no long-lived connection), so a failure in one send does not affect subsequent sends.

## 3. Data Structures & API Schemas

```python
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import UTC, datetime
from email.message import EmailMessage
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field

# --- Errors (service-level; messages are secret-free) ---

class MailError(Exception):
    """Base class for all mail domain errors."""

class MailConfigurationError(MailError):
    """The mail service is not correctly configured at send time.

    Raised when a required SMTP setting is missing or unusable (e.g., the
    SMTP host is empty). ``reason`` is a short, secret-free string
    (e.g., ``"smtp_host_empty"``).
    """
    def __init__(self, reason: str) -> None: ...

class MailTransportError(MailError):
    """The SMTP transport failed to deliver the email.

    Raised on connection failure, authentication failure, SMTP protocol
    error, or timeout. ``reason`` is a short, secret-free string
    (e.g., ``"connection"``, ``"authentication"``, ``"smtp"``, ``"timeout"``).
    The SMTP password is never included.
    """
    def __init__(self, reason: str) -> None: ...

class MailTemplateError(MailError):
    """The email could not be prepared from its template.

    Raised when the recipient is not a valid email address, a template
    variable is missing from the context, or the template is malformed
    (a ``{{`` without a closing ``}}``). ``reason`` is a short, secret-free
    string (e.g., ``"invalid_recipient"``, ``"missing_variable:reset_url"``,
    ``"malformed_template"``).
    """
    def __init__(self, reason: str) -> None: ...

# --- Templates (frozen; the "clear structure" of an email template) ---

class EmailTemplate(BaseModel):
    """A named email template with ``{{variable}}`` placeholders.

    ``subject``, ``body_html``, and ``body_text`` all support
    ``{{variable}}`` placeholders. The message is always
    ``multipart/alternative`` (text + HTML), so both ``body_html`` and
    ``body_text`` are required.
    """
    model_config = ConfigDict(frozen=True)

    name: str = Field(min_length=1)          # e.g., "password_reset"
    subject: str                             # with {{variable}} placeholders
    body_html: str                           # with {{variable}} placeholders
    body_text: str                           # with {{variable}} placeholders

# --- Request schemas (schema-level validation -> pydantic.ValidationError) ---

class PasswordResetEmailRequest(BaseModel):
    to: EmailStr
    display_name: str = Field(min_length=1, max_length=320)
    reset_url: str = Field(min_length=1, max_length=2048)

class EmailVerificationEmailRequest(BaseModel):
    to: EmailStr
    display_name: str = Field(min_length=1, max_length=320)
    verification_url: str = Field(min_length=1, max_length=2048)

# --- Representations (no body, no token, no password) ---

class EmailSendResult(BaseModel):
    """The result of a successful send (non-sensitive data only)."""
    model_config = ConfigDict(frozen=True)

    to: str
    template: str                            # the template name

# --- Structural protocol (satisfied by the shared event bus) ---

class EventPublisher(ABC):
    """Structural publisher protocol (consistent with user-management)."""
    @abstractmethod
    def publish(self, event: object) -> None: ...

# --- Events (typed lifecycle; non-sensitive data only) ---

class MailEvent(BaseModel):
    model_config = ConfigDict(frozen=True)
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

class EmailSent(MailEvent):
    to: str                                 # the recipient (not a secret)
    template: str                           # the template name

class EmailFailed(MailEvent):
    to: str
    template: str
    reason: str                             # "template" | "configuration" | "transport"

# --- SMTP transport (ABC + smtplib-backed default) ---

class SmtpTransport(ABC):
    """The physical SMTP send (the seam for testability)."""
    @abstractmethod
    def send(self, message: EmailMessage) -> None:
        """Send ``message``; raise ``MailTransportError`` on failure."""
        ...

class SmtpTransportImpl(SmtpTransport):
    """The smtplib-backed default transport (connects per send)."""
    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        use_tls: bool,
        timeout: float,
    ) -> None: ...
    def send(self, message: EmailMessage) -> None:
        """Connect, authenticate when credentials are present, send, close.

        Wraps ``smtplib.SMTPException`` / ``socket`` / ``OSError`` failures
        in ``MailTransportError`` (secret-free ``reason``). The SMTP password
        is never included in the error or in any log/event.
        """
        ...

# --- Built-in templates (module-level constants) ---

PASSWORD_RESET_TEMPLATE: EmailTemplate = EmailTemplate(
    name="password_reset",
    subject="Reset your password",
    body_html=(
        "<p>Hello {{display_name}},</p>"
        "<p>Click the link below to reset your password:</p>"
        f'<p><a href="{{{{reset_url}}}}">Reset password</a></p>'
        "<p>If you did not request this, you can ignore this email.</p>"
    ),
    body_text=(
        "Hello {{display_name}},\n\n"
        "Reset your password by visiting the link below:\n"
        "{{reset_url}}\n\n"
        "If you did not request this, you can ignore this email.\n"
    ),
)

EMAIL_VERIFICATION_TEMPLATE: EmailTemplate = EmailTemplate(
    name="email_verification",
    subject="Verify your email address",
    body_html=(
        "<p>Hello {{display_name}},</p>"
        "<p>Click the link below to verify your email address:</p>"
        f'<p><a href="{{{{verification_url}}}}">Verify email</a></p>'
    ),
    body_text=(
        "Hello {{display_name}},\n\n"
        "Verify your email address by visiting the link below:\n"
        "{{verification_url}}\n"
    ),
)

# --- Service ---

class MailService:
    def __init__(
        self,
        transport: SmtpTransport | None = None,      # default: SmtpTransportImpl from live settings
        event_bus: EventPublisher | None = None,     # default: no events
    ) -> None: ...

    def send_email(
        self, to: str, template: EmailTemplate, context: dict[str, str]
    ) -> EmailSendResult: ...

    def send_password_reset_email(
        self, request: PasswordResetEmailRequest
    ) -> EmailSendResult: ...

    def send_email_verification_email(
        self, request: EmailVerificationEmailRequest
    ) -> EmailSendResult: ...
```

Notes on the schema:
- `EventPublisher` is the structural publisher protocol (satisfied by the shared event bus), consistent with user-management and authentication. A `None` event bus means no events.
- `SmtpTransportImpl` connects per send (no long-lived connection): it opens the SMTP connection (TLS when `use_tls` is true), authenticates when `username` is non-empty, sends the message, and closes. It wraps `smtplib.SMTPException`, `socket.error`, and `OSError` failures in `MailTransportError` with a secret-free `reason` (`"connection"`, `"authentication"`, `"smtp"`, `"timeout"`). The SMTP password is never included in the error, in any log, or in any event.
- `send_email` is the core operation: it validates the recipient (REQ-008), renders the template (REQ-007/REQ-009), builds a `multipart/alternative` `EmailMessage` (From from the `mail.from_name`/`mail.smtp_from` settings, REQ-017), resolves the SMTP configuration live (REQ-002/REQ-010), sends via the transport (REQ-011), and publishes the lifecycle event (REQ-012/REQ-013). It raises `MailTemplateError`, `MailConfigurationError`, or `MailTransportError` on failure (and publishes `EmailFailed`).
- `send_password_reset_email` and `send_email_verification_email` are the high-level operations: they build the context (`display_name`, `reset_url`/`verification_url`) and call the core send with the built-in template. They are the reusable high-level operations the application invokes (template + send), NOT modifications to the authentication feature.
- The `{{variable}}` placeholders in the built-in templates are `{{display_name}}`, `{{reset_url}}` (password reset), and `{{verification_url}}` (email verification). The context values are HTML-escaped during rendering (D3).

### 3.1 SMTP Settings (registered via `register_settings`)

The mail service registers its SMTP settings with the settings registry via a feature-owned `register_settings(registry)` (no import side effects, consistent with the other features). Each setting is read live on each send (REQ-002).

| Key | Kind | Default | Constraints | Notes |
|-----|------|---------|-------------|-------|
| `mail.smtp_host` | TEXT | `"localhost"` | — | The SMTP server host. The mail service validates it is non-empty at send time (REQ-010). |
| `mail.smtp_port` | NUMBER | `587` | `min_value=1`, `max_value=65535` | The SMTP server port. |
| `mail.smtp_username` | TEXT | `""` | — | The SMTP authentication username. Empty means no authentication. |
| `mail.smtp_password` | TEXT | `""` | — | The SMTP authentication password. **Sensitive** — never in logs/events. Empty means no authentication. |
| `mail.smtp_from` | EMAIL | `"no-reply@example.com"` | — | The From address. |
| `mail.smtp_tls` | BOOLEAN | `True` | — | Whether to use TLS for the SMTP connection. |
| `mail.smtp_timeout` | NUMBER | `30` | `min_value=1` | The SMTP connection/send timeout in seconds. |
| `mail.from_name` | TEXT | `"Python Template"` | — | The display name for the From header (combined with `mail.smtp_from`). |

The `register_settings` function (in `feature_settings.py`) registers these `SettingDefinition`s with `category="application"` and `group="mail"`, traced with `@logged(slow_threshold_ms=5)` (consistent with the other features). The mail service reads them live on each send via the live-read pattern (REQ-002), falling back to the hardcoded defaults above when a key is unregistered.

## 4. Requirements

Each normative requirement MUST have a stable ID. These IDs propagate through the lifecycle:
`REQ-001 → AC-001 → test → task → implementation`.

| ID | Requirement |
|----|-------------|
| REQ-001 | The mail service registers its SMTP settings with the settings registry via a feature-owned `register_settings(registry)` (no import side effects), consistent with the other features. |
| REQ-002 | The mail service reads its SMTP settings live from the settings registry on each send; unregistered settings fall back to hardcoded defaults. |
| REQ-003 | The mail service exposes a core `send_email(to, template, context)` operation that renders `template` with `context` and sends the resulting email to `to`, returning an `EmailSendResult`. |
| REQ-004 | The mail service exposes a `send_password_reset_email(request)` operation that sends a password-reset email using the built-in `PASSWORD_RESET_TEMPLATE` and the request's `display_name` and `reset_url`. |
| REQ-005 | The mail service exposes a `send_email_verification_email(request)` operation that sends an email-verification email using the built-in `EMAIL_VERIFICATION_TEMPLATE` and the request's `display_name` and `verification_url`. |
| REQ-006 | The mail service supports feature-specific emails: a feature can provide its own `EmailTemplate` and call the core `send_email` operation without implementing its own mail-sending logic. |
| REQ-007 | The mail service renders templates with `{{variable}}` substitution: each `{{variable}}` is replaced with the corresponding context value, HTML-escaped. |
| REQ-008 | The mail service validates the recipient is a valid email address; an invalid recipient raises `MailTemplateError`. |
| REQ-009 | The mail service validates that all template variables are present in the context; a missing variable raises `MailTemplateError`. |
| REQ-010 | The mail service validates the SMTP configuration at send time; an empty SMTP host raises `MailConfigurationError`. |
| REQ-011 | The mail service sends the email via the SMTP transport; a transport failure (connection, authentication, SMTP protocol error, or timeout) raises `MailTransportError`. |
| REQ-012 | The mail service publishes an `EmailSent` event on successful send and an `EmailFailed` event on send failure (with the error kind: `"template"`, `"configuration"`, or `"transport"`); on failure it re-raises the `MailError`. |
| REQ-013 | The mail service's events carry non-sensitive data only: no email body, no rendered subject, no token, and no SMTP password. |
| REQ-014 | The mail service is traced with the shared logging feature (`@logged_class`); `include_args` stays `False`; the SMTP password and tokens never appear in log records. |
| REQ-015 | The mail service's public API (service, request/representation models, error hierarchy, transport ABC, events, built-in templates) is a backward-compatibility contract. |
| REQ-016 | The mail service is safe for concurrent use from multiple threads: each send is independent (the transport is created per send, no long-lived connection). |
| REQ-017 | The mail service builds a `multipart/alternative` email (text + HTML) from the template and sets the From header from the `mail.from_name` and `mail.smtp_from` settings. |

## 5. Acceptance Criteria

Each acceptance criterion MUST have a stable ID and MUST reference at least one requirement. Use Given/When/Then format.

| ID | References | Criterion |
|----|------------|-----------|
| AC-001 | REQ-001 | **Given** a settings registry, **When** `register_settings(registry)` is called, **Then** the mail service's SMTP settings are registered (e.g., `mail.smtp_host`, `mail.smtp_port`, `mail.smtp_username`, `mail.smtp_password`, `mail.smtp_from`, `mail.smtp_tls`, `mail.smtp_timeout`, `mail.from_name`). |
| AC-002 | REQ-002 | **Given** a settings registry with a modified `mail.smtp_host`, **When** `send_email` is called, **Then** the modified host is used (live read). |
| AC-003 | REQ-002 | **Given** a settings registry where `mail.smtp_host` is unregistered, **When** `send_email` is called, **Then** the hardcoded default host is used (fallback). |
| AC-004 | REQ-003 | **Given** a valid recipient, a valid template, and a complete context, **When** `send_email` is called, **Then** the email is sent via the transport **and** an `EmailSendResult` is returned. |
| AC-005 | REQ-004 | **Given** a valid `PasswordResetEmailRequest`, **When** `send_password_reset_email` is called, **Then** a password-reset email is sent using the built-in `PASSWORD_RESET_TEMPLATE` with the request's `display_name` and `reset_url`. |
| AC-006 | REQ-005 | **Given** a valid `EmailVerificationEmailRequest`, **When** `send_email_verification_email` is called, **Then** an email-verification email is sent using the built-in `EMAIL_VERIFICATION_TEMPLATE` with the request's `display_name` and `verification_url`. |
| AC-007 | REQ-006 | **Given** a feature-provided `EmailTemplate` and a complete context, **When** `send_email` is called with them, **Then** the email is sent using the feature's template. |
| AC-008 | REQ-007 | **Given** a template with `{{variable}}` placeholders and a context, **When** the template is rendered, **Then** each `{{variable}}` is replaced with the corresponding context value **and** the value is HTML-escaped. |
| AC-009 | REQ-008 | **Given** an invalid recipient, **When** `send_email` is called, **Then** `MailTemplateError` is raised. |
| AC-010 | REQ-009 | **Given** a template with a `{{variable}}` not present in the context, **When** `send_email` is called, **Then** `MailTemplateError` is raised. |
| AC-011 | REQ-010 | **Given** an empty SMTP host, **When** `send_email` is called, **Then** `MailConfigurationError` is raised. |
| AC-012 | REQ-011 | **Given** a transport that fails, **When** `send_email` is called, **Then** `MailTransportError` is raised. |
| AC-013 | REQ-012 | **Given** a publisher, **When** `send_email` succeeds, **Then** `EmailSent` is published. |
| AC-014 | REQ-012 | **Given** a publisher, **When** `send_email` fails, **Then** `EmailFailed` is published (with the error kind) **and** the `MailError` is re-raised. |
| AC-015 | REQ-013 | **Given** a successful or failed send, **When** the published events are inspected, **Then** no email body, rendered subject, token, or SMTP password is present. |
| AC-016 | REQ-014 | **Given** the service, **When** its methods are called, **Then** no log record contains the SMTP password or a token. |
| AC-017 | REQ-015 | **Given** the public API, **When** it is inspected, **Then** the service, request/representation models, error hierarchy, transport ABC, events, and built-in templates are present and stable. |
| AC-018 | REQ-016 | **Given** the service, **When** `send_email` is called concurrently from multiple threads, **Then** every send is independent **and** no thread crashes. |
| AC-019 | REQ-017 | **Given** a successful send, **When** the built `EmailMessage` is inspected, **Then** it is `multipart/alternative` (text + HTML) **and** the From header is set from `mail.from_name` and `mail.smtp_from`. |

## 6. Invariants

State invariants that hold over a large input space. These become Hypothesis property-based tests.

| ID | Invariant |
|----|-----------|
| INV-001 | For any template and context, rendering is deterministic: rendering the same template with the same context produces the same output. |
| INV-002 | For any context value, the HTML-escaped value contains no raw `<`, `>`, `&`, `"`, or `'` from the original value (XSS-safe substitution). |
| INV-003 | For any send (success or failure), the SMTP password never appears in any observable output: the returned `EmailSendResult`, the raised error's message, or the published events. |
| INV-004 | For any send (success or failure), the email body (which contains tokens) never appears in the published events. |
| INV-005 | A send failure does not affect subsequent sends: after a failed send, the next send is evaluated independently (no long-lived connection state). |

## 7. Edge Cases & Error Conditions

| ID | Condition | Expected Behavior |
|----|-----------|-------------------|
| EDGE-001 | `send_email` with an invalid recipient (e.g., `"not-an-email"`) | `MailTemplateError` (reason `"invalid_recipient"`). |
| EDGE-002 | `send_email` with a template variable missing from the context | `MailTemplateError` (reason `"missing_variable:<name>"`). |
| EDGE-003 | `send_email` with a malformed template (a `{{` without a closing `}}`) | `MailTemplateError` (reason `"malformed_template"`). |
| EDGE-004 | `send_email` with an empty SMTP host | `MailConfigurationError` (reason `"smtp_host_empty"`). |
| EDGE-005 | `send_email` when the SMTP connection is refused | `MailTransportError` (reason `"connection"`); `EmailFailed` published. |
| EDGE-006 | `send_email` when the SMTP authentication fails | `MailTransportError` (reason `"authentication"`); `EmailFailed` published. |
| EDGE-007 | `send_email` when the SMTP server returns a protocol error | `MailTransportError` (reason `"smtp"`); `EmailFailed` published. |
| EDGE-008 | `send_email` when the SMTP send times out | `MailTransportError` (reason `"timeout"`); `EmailFailed` published. |
| EDGE-009 | `send_email` with a `None` event bus | No event is published, no error is raised. |
| EDGE-010 | A failed send followed by a successful send | The successful send is evaluated independently (no state carried over). |

## 8. Non-Functional Requirements

| ID | Category | Requirement |
|----|----------|-------------|
| NFR-001 | Performance | Email preparation (template rendering + message building) completes in ≤ 50 ms at p95, measured on local hardware with the shared logging feature configured at its default INFO level with a synchronous console sink; the budget holds including the per-call logging overhead at that level. The SMTP delivery time is network-dependent and is not budgeted. |
| NFR-002 | Security | The SMTP password never appears in log records, events, or error messages; the email body (containing tokens) never appears in events; template context values are HTML-escaped in the rendered output. |
| NFR-003 | Contract | The public API of `backend.mail` (service, request/representation models, error hierarchy, transport ABC, events, built-in templates) is a backward-compatibility contract. |
| NFR-004 | Observability | The service is traced with `@logged_class` (entry/exit/exception per public method); lifecycle events are published to the injected publisher. |
| NFR-005 | Reliability | The service is safe for concurrent use from multiple threads (each send is independent; the transport is created per send). |

## 9. Observability & Logging

| Operation / Event | Level | Context |
|-------------------|-------|---------|
| Public method entry/exit (all `MailService` methods) | DEBUG | Method name, elapsed ms; no arguments (`include_args` stays `False`). A slow call (elapsed > `slow_threshold_ms`) is logged at WARNING. |
| Method exception (any `MailError` raised) | DEBUG | Exception type and secret-free message (e.g., `MailTransportError`); no SMTP password, no token, no email body. |
| Lifecycle events | — | Published to the injected `EventPublisher` (not logged by this feature); events carry non-sensitive data only. |

- **Default level:** DEBUG for method tracing (off by default at the INFO default level); exceptions are logged with secret-free messages.
- **Error conditions:** Every domain error is a `MailError` subclass with a secret-free message (error kind + short reason only; never the SMTP password, a token, or the email body). Schema-level validation failures are `pydantic.ValidationError` identifying the offending field name (never the field value).
- **Tracing policy:** The `MailService` class is traced with `@logged_class(slow_threshold_ms=5000, include_args=False)` — `include_args` stays `False` because the high-level operations carry a `reset_url`/`verification_url` (which contains a token) and the core send carries the recipient; `slow_threshold_ms` is 5000 ms because the SMTP send is network-dependent. The feature-owned `register_settings` is traced with `@logged(slow_threshold_ms=5)` (consistent with the other features).

## 10. Test Strategy

Map each requirement/AC to a test category. This drives the test file layout.

| ID | Test Category | Test File | Test Function |
|----|---------------|-----------|---------------|
| AC-001 | acceptance | `tests/acceptance/mail/test_settings.py` | `test_ac_001_register_settings` |
| AC-002 | acceptance | `tests/acceptance/mail/test_settings.py` | `test_ac_002_live_read_modified_host` |
| AC-003 | acceptance | `tests/acceptance/mail/test_settings.py` | `test_ac_003_fallback_unregistered_host` |
| AC-004 | acceptance | `tests/acceptance/mail/test_send.py` | `test_ac_004_core_send_success` |
| AC-005 | acceptance | `tests/acceptance/mail/test_high_level.py` | `test_ac_005_password_reset_email` |
| AC-006 | acceptance | `tests/acceptance/mail/test_high_level.py` | `test_ac_006_email_verification_email` |
| AC-007 | acceptance | `tests/acceptance/mail/test_send.py` | `test_ac_007_feature_specific_template` |
| AC-008 | acceptance | `tests/acceptance/mail/test_render.py` | `test_ac_008_template_rendering` |
| AC-009 | acceptance | `tests/acceptance/mail/test_validation.py` | `test_ac_009_invalid_recipient` |
| AC-010 | acceptance | `tests/acceptance/mail/test_validation.py` | `test_ac_010_missing_variable` |
| AC-011 | acceptance | `tests/acceptance/mail/test_config.py` | `test_ac_011_empty_smtp_host` |
| AC-012 | acceptance | `tests/acceptance/mail/test_transport.py` | `test_ac_012_transport_failure` |
| AC-013 | acceptance | `tests/acceptance/mail/test_events.py` | `test_ac_013_email_sent_event` |
| AC-014 | acceptance | `tests/acceptance/mail/test_events.py` | `test_ac_014_email_failed_event` |
| AC-015 | acceptance | `tests/acceptance/mail/test_events.py` | `test_ac_015_non_sensitive_events` |
| AC-016 | acceptance | `tests/acceptance/mail/test_logging.py` | `test_ac_016_no_secrets_in_log_records` |
| AC-017 | acceptance | `tests/acceptance/mail/test_public_api.py` | `test_ac_017_public_api_stable` |
| AC-018 | acceptance | `tests/acceptance/mail/test_concurrency.py` | `test_ac_018_concurrent_send` |
| AC-019 | acceptance | `tests/acceptance/mail/test_message.py` | `test_ac_019_multipart_alternative` |
| INV-001 | property | `tests/property/mail/test_render.py` | `test_inv_001_rendering_deterministic` |
| INV-002 | property | `tests/property/mail/test_render.py` | `test_inv_002_xss_safe_substitution` |
| INV-003 | property | `tests/property/mail/test_secrets.py` | `test_inv_003_no_password_in_observable_output` |
| INV-004 | property | `tests/property/mail/test_secrets.py` | `test_inv_004_no_body_in_events` |
| INV-005 | property | `tests/property/mail/test_independence.py` | `test_inv_005_failure_independence` |
| EDGE-001 | unit | `tests/unit/mail/test_validation.py` | `test_edge_001_invalid_recipient` |
| EDGE-002 | unit | `tests/unit/mail/test_validation.py` | `test_edge_002_missing_variable` |
| EDGE-003 | unit | `tests/unit/mail/test_validation.py` | `test_edge_003_malformed_template` |
| EDGE-004 | unit | `tests/unit/mail/test_config.py` | `test_edge_004_empty_smtp_host` |
| EDGE-005 | unit | `tests/unit/mail/test_transport.py` | `test_edge_005_connection_refused` |
| EDGE-006 | unit | `tests/unit/mail/test_transport.py` | `test_edge_006_auth_failure` |
| EDGE-007 | unit | `tests/unit/mail/test_transport.py` | `test_edge_007_protocol_error` |
| EDGE-008 | unit | `tests/unit/mail/test_transport.py` | `test_edge_008_timeout` |
| EDGE-009 | unit | `tests/unit/mail/test_events.py` | `test_edge_009_none_event_bus` |
| EDGE-010 | unit | `tests/unit/mail/test_independence.py` | `test_edge_010_failure_then_success` |
| NFR-001 | contract | `tests/contract/mail/test_performance.py` | `test_nfr_001_preparation_performance_budget` |
| NFR-002 | contract | `tests/contract/mail/test_secrets.py` | `test_nfr_002_no_secrets_in_logs_or_events` |
| NFR-003 | contract | `tests/contract/mail/test_public_api.py` | `test_nfr_003_public_api_stable` |
| NFR-004 | contract | `tests/contract/mail/test_logging.py` | `test_nfr_004_service_traced` |
| NFR-005 | integration | `tests/integration/mail/test_concurrency.py` | `test_nfr_005_concurrent_send_thread_safety` |

## 11. Traceability Matrix

Maintain this matrix as tests are written and pass. Every normative requirement MUST have at least one executable test.

| Requirement | Acceptance Criterion | Test | Status |
|-------------|---------------------|------|--------|
| REQ-001 | AC-001 | `test_ac_001_register_settings` | PENDING |
| REQ-002 | AC-002 | `test_ac_002_live_read_modified_host` | PENDING |
| REQ-002 | AC-003 | `test_ac_003_fallback_unregistered_host` | PENDING |
| REQ-003 | AC-004 | `test_ac_004_core_send_success` | PENDING |
| REQ-004 | AC-005 | `test_ac_005_password_reset_email` | PENDING |
| REQ-005 | AC-006 | `test_ac_006_email_verification_email` | PENDING |
| REQ-006 | AC-007 | `test_ac_007_feature_specific_template` | PENDING |
| REQ-007 | AC-008 | `test_ac_008_template_rendering` | PENDING |
| REQ-008 | AC-009 | `test_ac_009_invalid_recipient` | PENDING |
| REQ-009 | AC-010 | `test_ac_010_missing_variable` | PENDING |
| REQ-010 | AC-011 | `test_ac_011_empty_smtp_host` | PENDING |
| REQ-011 | AC-012 | `test_ac_012_transport_failure` | PENDING |
| REQ-012 | AC-013 | `test_ac_013_email_sent_event` | PENDING |
| REQ-012 | AC-014 | `test_ac_014_email_failed_event` | PENDING |
| REQ-013 | AC-015 | `test_ac_015_non_sensitive_events` | PENDING |
| REQ-014 | AC-016 | `test_ac_016_no_secrets_in_log_records` | PENDING |
| REQ-015 | AC-017 | `test_ac_017_public_api_stable` | PENDING |
| REQ-016 | AC-018 | `test_ac_018_concurrent_send` | PENDING |
| REQ-017 | AC-019 | `test_ac_019_multipart_alternative` | PENDING |
| INV-001 | — | `test_inv_001_rendering_deterministic` | PENDING |
| INV-002 | — | `test_inv_002_xss_safe_substitution` | PENDING |
| INV-003 | — | `test_inv_003_no_password_in_observable_output` | PENDING |
| INV-004 | — | `test_inv_004_no_body_in_events` | PENDING |
| INV-005 | — | `test_inv_005_failure_independence` | PENDING |
| EDGE-001 | — | `test_edge_001_invalid_recipient` | PENDING |
| EDGE-002 | — | `test_edge_002_missing_variable` | PENDING |
| EDGE-003 | — | `test_edge_003_malformed_template` | PENDING |
| EDGE-004 | — | `test_edge_004_empty_smtp_host` | PENDING |
| EDGE-005 | — | `test_edge_005_connection_refused` | PENDING |
| EDGE-006 | — | `test_edge_006_auth_failure` | PENDING |
| EDGE-007 | — | `test_edge_007_protocol_error` | PENDING |
| EDGE-008 | — | `test_edge_008_timeout` | PENDING |
| EDGE-009 | — | `test_edge_009_none_event_bus` | PENDING |
| EDGE-010 | — | `test_edge_010_failure_then_success` | PENDING |
| NFR-001 | — | `test_nfr_001_preparation_performance_budget` | PENDING |
| NFR-002 | — | `test_nfr_002_no_secrets_in_logs_or_events` | PENDING |
| NFR-003 | — | `test_nfr_003_public_api_stable` | PENDING |
| NFR-004 | — | `test_nfr_004_service_traced` | PENDING |
| NFR-005 | — | `test_nfr_005_concurrent_send_thread_safety` | PENDING |
