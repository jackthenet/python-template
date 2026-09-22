"""Acceptance tests for the permissions feature's enforcement plumbing (docs/specs/user-roles-permissions.md).

Covers AC-032 (REQ-025): the Principal model — ``Principal()`` is the system
principal, and construction sets the fields.

Covers AC-031 (REQ-024): standalone mode — a service constructed without an
injected permission checker performs no check (open, as today).

Covers AC-029 (REQ-024): filemanagement enforcement wiring — a ``FileService``
with an injected permission checker denies ``upload`` without
``filemanagement.upload`` (a ``PermissionDeniedError`` is raised, nothing is
written) and proceeds with it.

These tests verify externally observable behavior only. The ``backend.shared``
and ``backend.permissions`` imports are deferred into the test bodies so the
module collects cleanly before the feature is implemented (RED).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
from uuid import uuid4

import pytest
from filemanagement_test_helpers import db_url, isolated_registry, text_bytes

from backend.filemanagement import FileService, InMemoryStorageBackend, SqliteFileRepository
from backend.usermanagement import SqliteUserRepository, UserCreate, UserManager


class _FakePermissionChecker:
    """A structural ``PermissionChecker`` (spec D14) that records the checks it receives.

    Mimics the real checker's observable behavior: ``require_permission`` raises
    ``PermissionDeniedError`` on denial (the real error — deferred import) and
    ``has_permission`` reports the decision. Only this test double imports
    ``backend.permissions``; the feature under test never does (ADR-070).
    """

    def __init__(self, deny: bool) -> None:
        self.deny = deny
        self.calls: list[tuple[Any, str, Any]] = []

    def require_permission(self, user_id: Any, permission: str, session_token: Any = None) -> None:
        self.calls.append((user_id, permission, session_token))
        if self.deny:
            from backend.permissions.errors import PermissionDeniedError  # deferred: RED

            raise PermissionDeniedError(user_id=user_id, permission=permission, reason="unauthorized")

    def has_permission(self, user_id: Any, permission: str, session_token: Any = None) -> bool:
        return not self.deny


def _build_file_service(tmp_path: Path, checker: _FakePermissionChecker) -> FileService:
    """Construct a ``FileService`` over SQLite + in-memory storage with the checker injected."""
    return FileService(
        SqliteFileRepository(db_url(tmp_path)),
        backend=InMemoryStorageBackend(),
        event_bus=None,
        settings_registry=isolated_registry(),
        permission_service=checker,
    )


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


def test_enforced_method_denies_without_permission(tmp_path: Path) -> None:
    """AC-029 / REQ-024: an enforced FileService method denies without the permission, proceeds with it.

    Given a ``FileService`` with an injected permission checker, when ``upload``
    is called with a principal lacking ``filemanagement.upload``, then a
    ``PermissionDeniedError`` is raised (and nothing is written); when it is
    called with a principal holding it, then the upload proceeds.
    """
    from backend.permissions.errors import PermissionDeniedError  # deferred: RED
    from backend.shared import Principal  # deferred: RED

    user_id = uuid4()
    session_token = "upload-session"
    principal = Principal(user_id=user_id, session_token=session_token)
    payload = text_bytes(256)

    # --- deny: a principal lacking filemanagement.upload is denied (AC-029) ---
    denier = _FakePermissionChecker(deny=True)
    service = _build_file_service(tmp_path, denier)
    with pytest.raises(PermissionDeniedError):
        service.upload(payload, principal=principal)
    # The check evaluated the principal against the filemanagement.upload key,
    # and the denial happened at entry: nothing was written.
    assert denier.calls == [(user_id, "filemanagement.upload", session_token)]
    assert service.list_files() == []

    # --- allow: a principal holding filemanagement.upload proceeds (AC-029) ---
    allow_checker = _FakePermissionChecker(deny=False)
    service = _build_file_service(tmp_path, allow_checker)
    record = service.upload(payload, principal=principal)
    assert record.key
    assert service.download(record.key) == payload
    assert allow_checker.calls == [(user_id, "filemanagement.upload", session_token)]
