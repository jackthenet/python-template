"""Acceptance tests for the permissions feature's enforcement plumbing (docs/specs/user-roles-permissions.md).

Covers AC-032 (REQ-025): the Principal model — ``Principal()`` is the system
principal, and construction sets the fields.

Covers AC-031 (REQ-024): standalone mode — a service constructed without an
injected permission checker performs no check (open, as today).

These tests verify externally observable behavior only. The ``backend.shared``
imports are deferred into the test bodies so the module collects cleanly before
the feature is implemented (RED).
"""

from __future__ import annotations

from uuid import uuid4

from backend.usermanagement import SqliteUserRepository, UserCreate, UserManager


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


def test_standalone_mode_no_check() -> None:
    """AC-031 / REQ-024: standalone mode (no checker) performs no check (open, as today).

    Given a ``UserManager`` constructed without an injected permission checker
    (standalone mode), when an enforced method is called (with an explicit
    principal that holds no permissions), then no check is performed: the
    operation proceeds, as today.
    """
    from backend.shared import Principal

    repo = SqliteUserRepository("sqlite:///:memory:")
    manager = UserManager(repo)  # standalone: no permission checker injected

    # An enforced method called with an explicit principal (a user without any
    # permission) performs no check in standalone mode: the operation proceeds.
    user = manager.create_user(
        UserCreate(username="alice", email="alice@example.com", password="correct-horse-1", roles=["user"]),
        principal=Principal(user_id=uuid4(), session_token="standalone-session"),
    )
    assert user.username == "alice"

    # A second enforced method is likewise open in standalone mode (no check).
    read = manager.get_user(user.id, principal=Principal(user_id=uuid4(), session_token="standalone-session"))
    assert read.id == user.id
