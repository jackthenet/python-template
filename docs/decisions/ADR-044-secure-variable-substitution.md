# ADR-044: Secure `{{variable}}` substitution instead of Jinja2

## Status
Accepted

## Context
Email templates need variable substitution: the built-in templates substitute `{{display_name}}`, `{{reset_url}}`, and `{{verification_url}}`, and feature-specific templates substitute their own variables.

Jinja2 is the established templating engine for Python, but it is a full engine (filters, loops, conditionals, loading, sandboxing). The mail service only needs to substitute a small number of string variables in trusted templates (written by the feature developer, not by end users). A full engine adds a dependency, a large feature surface, and sandboxing concerns the feature does not need.

## Decision
Use a small, secure `{{variable}}` substitution (no Jinja2):

- Each `{{variable}}` is replaced with the corresponding context value, **HTML-escaped** (`html.escape`) — the secure default against XSS in HTML emails.
- A `{{variable}}` with no corresponding context value raises `MailTemplateError` (reason `"missing_variable:<name>"`).
- A malformed template (a `{{` without a closing `}}`) raises `MailTemplateError` (reason `"malformed_template"`).
- The template itself is trusted (written by the feature developer); only the substituted values are escaped.
- Rendering is deterministic: the same template with the same context produces the same output (INV-001).

## Consequences
- No new dependency; no engine feature surface (no filters, loops, conditionals, file loading) to maintain or sandbox.
- XSS-safe substitution is the default behavior (INV-002): context values containing `<`, `>`, `&`, `"`, `'` never reach the rendered output raw.
- Failures are explicit and typed: a missing variable or a malformed template is a `MailTemplateError`, not a silent partial render.
- The substitution syntax (`{{variable}}`) matches the common templating convention, so templates are portable if the feature ever adopts a full engine.

## Alternatives Considered
- Jinja2 — rejected: a full engine for a string-substitution need; adds a dependency, a feature surface, and sandboxing concerns; the spec explicitly scopes a full templating engine out (a small, secure substitution is used instead).
- `string.Template` (`$variable`) — rejected: different placeholder syntax than the spec's `{{variable}}`; no hook for HTML-escaping the substituted values; weaker failure semantics for missing variables.
- No escaping (raw substitution) — rejected: XSS in HTML emails; context values carry URLs and display names that must be escaped (NFR-002, INV-002).
- Escaping the template as well — rejected: the template is trusted and contains intentional HTML markup; escaping it would break the templates.

## References
- `docs/specs/mail-service.md` (D3; REQ-007, REQ-009; INV-001, INV-002; EDGE-002, EDGE-003; NFR-002)
- `docs/decisions/ADR-045-mailerror-hierarchy-secret-free-reasons.md` (failure typing)
