"""Secure ``{{variable}}`` template rendering (docs/specs/mail-service.md, D3, ADR-044).

A small, secure substitution (no Jinja2): each ``{{variable}}`` is replaced with
the corresponding context value, HTML-escaped (the secure default against XSS in
HTML emails). The template itself is trusted (written by the feature developer);
only the substituted values are escaped.

- A ``{{variable}}`` with no corresponding context value raises
  ``MailTemplateError`` (reason ``"missing_variable:<name>"``).
- A malformed template (a ``{{`` without a closing ``}}``, or a placeholder whose
  name is not a valid identifier) raises ``MailTemplateError`` (reason
  ``"malformed_template"``).
- Rendering is deterministic (INV-001) and XSS-safe (INV-002).
"""

from __future__ import annotations

import html
import re
from dataclasses import dataclass

from backend.mail.errors import MailTemplateError
from backend.mail.templates import EmailTemplate

# A valid placeholder variable name: an identifier (letters, digits, underscore;
# not starting with a digit).
_NAME_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


@dataclass(frozen=True)
class RenderedTemplate:
    """The rendered subject and bodies (values HTML-escaped)."""

    subject: str
    body_html: str
    body_text: str


def _substitute(field: str, context: dict[str, str]) -> str:
    """Replace each ``{{variable}}`` in ``field`` with its HTML-escaped value.

    Raises ``MailTemplateError`` for a missing variable or a malformed template.
    The substituted value is inserted as-is (escaped) and never re-processed, so
    a value containing ``{{`` is treated as data, not a template.
    """
    out: list[str] = []
    i = 0
    length = len(field)
    while i < length:
        open_idx = field.find("{{", i)
        if open_idx == -1:
            out.append(field[i:])
            break
        out.append(field[i:open_idx])
        close_idx = field.find("}}", open_idx + 2)
        if close_idx == -1:
            raise MailTemplateError("malformed_template")
        name = field[open_idx + 2 : close_idx].strip()
        if not _NAME_RE.fullmatch(name):
            raise MailTemplateError("malformed_template")
        if name not in context:
            raise MailTemplateError(f"missing_variable:{name}")
        out.append(html.escape(context[name]))
        i = close_idx + 2
    return "".join(out)


def render_template(template: EmailTemplate, context: dict[str, str]) -> RenderedTemplate:
    """Render ``template`` with ``context`` (HTML-escaped values)."""
    return RenderedTemplate(
        subject=_substitute(template.subject, context),
        body_html=_substitute(template.body_html, context),
        body_text=_substitute(template.body_text, context),
    )
