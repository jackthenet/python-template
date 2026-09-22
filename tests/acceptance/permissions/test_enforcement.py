"""Acceptance tests for the permissions feature's enforcement plumbing (docs/specs/user-roles-permissions.md).

Covers AC-032 (REQ-025): the Principal model — ``Principal()`` is the system
principal, and construction sets the fields.
"""

from __future__ import annotations

from uuid import uuid4


def test_principal_defaults_and_fields() -> None:
    """AC-032 / REQ-025: ``Principal()`` is the system principal; construction sets the fields.

    Given ``Principal()``, when it is inspected, then ``user_id=None`` and
    ``session_token=None`` (the system principal). Given
    ``Principal(user_id=u, session_token=t)``, when it is inspected, then the
    fields are set.
    """
    from backend.shared import Principal

    # Principal() is the system principal: both fields default to None.
    system = Principal()
    assert system.user_id is None
    assert system.session_token is None

    # Each field defaults independently (REQ-025 signature).
    partial = Principal(user_id=uuid4())
    assert partial.session_token is None

    # Principal(user_id=u, session_token=t) sets the fields.
    user_id = uuid4()
    token = "session-token"
    principal = Principal(user_id=user_id, session_token=token)
    assert principal.user_id == user_id
    assert principal.session_token == token
