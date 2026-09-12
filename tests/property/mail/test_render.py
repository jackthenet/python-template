"""Property tests for template rendering (INV-001, INV-002)."""

from __future__ import annotations

import html

from backend.mail import EmailTemplate, render_template
from hypothesis import given
from hypothesis import strategies as st


@st.composite
def template_with_context(draw):
    """A template with 0..3 variables and a complete context."""
    variables = draw(st.lists(st.sampled_from(["a", "b", "c"]), min_size=0, max_size=3, unique=True))
    context = {v: draw(st.text(max_size=128)) for v in variables}
    placeholders = " ".join(f"{{{{{v}}}}}" for v in variables)
    template = EmailTemplate(
        name="prop",
        subject=f"S {placeholders}",
        body_html=f"<p>{placeholders}</p>",
        body_text=f"T {placeholders}",
    )
    return template, context


@given(data=template_with_context())
def test_inv_001_rendering_deterministic(data) -> None:
    """INV-001: rendering the same template with the same context is deterministic."""
    template, context = data
    first = render_template(template, context)
    second = render_template(template, context)
    assert first.subject == second.subject
    assert first.body_html == second.body_html
    assert first.body_text == second.body_text


@given(value=st.text(max_size=256))
def test_inv_002_xss_safe_substitution(value: str) -> None:
    """INV-002: the substituted value is HTML-escaped (no raw <, >, &, \", ' from the value)."""
    template = EmailTemplate(name="xss", subject="{{v}}", body_html="{{v}}", body_text="{{v}}")
    rendered = render_template(template, {"v": value})
    escaped = html.escape(value)
    assert rendered.subject == escaped
    assert rendered.body_html == escaped
    assert rendered.body_text == escaped
