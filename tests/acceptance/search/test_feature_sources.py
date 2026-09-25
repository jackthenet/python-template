"""Acceptance tests for the feature search sources (docs/specs/search.md).

One test function per feature-source acceptance criterion AC-034 .. AC-036:
the user-management, file-management, and session-management sources. Each
test builds the feature's existing repository with valid rows, registers the
feature's ``build_*_source`` with a fresh ``SearchService``, and searches over
the feature's content — asserting the source name, ``item_id``, and the
declared display fields.

The ``backend.search`` and ``build_*_source`` imports are deferred into the
test bodies so the module collects cleanly before the feature is implemented
(RED).
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from search_test_helpers import (
    db_url,
    filter_condition,
    filter_group,
    fresh_registry,
    search_query,
    service,
)

_BASE = datetime(2024, 1, 1, tzinfo=UTC)


def test_ac_034_user_source(tmp_path: Path) -> None:
    """AC-034: ``build_user_source`` exposes users as a search source named
    ``usermanagement`` (free text on username/email/display_name; filters on
    is_active/created_at/updated_at); ``item_id`` = the user id."""
    from backend.usermanagement import SqliteUserRepository, User, build_user_source

    repo = SqliteUserRepository(db_url(tmp_path))
    users = [
        User(
            username="alice",
            email="alice@example.com",
            display_name="Alice",
            roles=["user"],
            password_hash="argon2id:fake-alice",
            profile_picture_url=None,
            is_active=True,
            created_at=_BASE,
            updated_at=_BASE,
        ),
        User(
            username="bob",
            email="bob@example.com",
            display_name="Bob",
            roles=["user"],
            password_hash="argon2id:fake-bob",
            profile_picture_url=None,
            is_active=False,
            created_at=_BASE,
            updated_at=_BASE,
        ),
    ]
    for u in users:
        repo.add(u)

    svc = service(settings_registry=fresh_registry())
    svc.register_source(build_user_source(repo))
    assert "usermanagement" in svc.list_sources()

    # Free text on username.
    result = svc.search(search_query(feature="usermanagement", free_text="alice"))
    assert result.total == 1
    item = result.items[0]
    assert item.feature == "usermanagement"
    assert item.item_id == str(users[0].id)  # item_id = the user id (stable string identifier)
    assert item.fields["username"] == "alice"
    assert item.fields["email"] == "alice@example.com"
    assert item.fields["display_name"] == "Alice"
    assert item.fields["is_active"] is True

    # Filter on is_active.
    active = svc.search(
        search_query(
            feature="usermanagement",
            filters=filter_group("and", [filter_condition("is_active", "equals", True)]),
        )
    )
    assert active.total == 1
    assert active.items[0].fields["username"] == "alice"


def test_ac_035_file_source(tmp_path: Path) -> None:
    """AC-035: ``build_file_source`` exposes files as a search source named
    ``filemanagement`` (free text on key/namespace/original_filename; filters
    on detected_mime_type/size/created_at/updated_at); ``item_id`` = the file id."""
    from backend.filemanagement import FileRecord, SqliteFileRepository, build_file_source

    repo = SqliteFileRepository(db_url(tmp_path))
    size_1 = 1024
    size_2 = 2048
    records = [
        FileRecord(
            key="rep-1",
            original_filename="report.txt",
            declared_mime_type="text/plain",
            detected_mime_type="text/plain",
            size=size_1,
            sha256="a" * 64,
            namespace="general",
            uploader=None,
            created_at=_BASE,
            updated_at=_BASE,
        ),
        FileRecord(
            key="rep-2",
            original_filename="notes.txt",
            declared_mime_type="text/plain",
            detected_mime_type="text/plain",
            size=size_2,
            sha256="b" * 64,
            namespace="general",
            uploader=None,
            created_at=_BASE,
            updated_at=_BASE,
        ),
    ]
    for r in records:
        repo.add(r)

    svc = service(settings_registry=fresh_registry())
    svc.register_source(build_file_source(repo))
    assert "filemanagement" in svc.list_sources()

    # Free text on key.
    result = svc.search(search_query(feature="filemanagement", free_text="rep-1"))
    assert result.total == 1
    item = result.items[0]
    assert item.feature == "filemanagement"
    assert item.item_id == str(records[0].id)  # item_id = the file id (stable string identifier)
    assert item.fields["key"] == "rep-1"
    assert item.fields["size"] == size_1
    assert item.fields["detected_mime_type"] == "text/plain"

    # Filter on size.
    big = svc.search(
        search_query(
            feature="filemanagement",
            filters=filter_group("and", [filter_condition("size", "gte", size_2)]),
        )
    )
    assert big.total == 1
    assert big.items[0].fields["key"] == "rep-2"


def test_ac_036_session_source(tmp_path: Path) -> None:
    """AC-036: ``build_session_source`` exposes sessions as a search source
    named ``sessionmanagement`` (filters on user_id/created_at/expires_at/
    revoked/login_method); ``item_id`` = the session id. Requires the additive
    ``SessionRepository.list_all`` (authentication)."""
    from backend.authentication import hash_token, new_token
    from backend.authentication.models import Session
    from backend.authentication.repository import SqliteSessionRepository
    from backend.sessionmanagement import build_session_source

    repo = SqliteSessionRepository(db_url(tmp_path))
    user_a = uuid4()
    user_b = uuid4()
    rows = [
        Session(
            user_id=user_a,
            token_hash=hash_token(new_token()),
            created_at=_BASE,
            expires_at=_BASE,
            revoked=False,
            login_method="password",
        ),
        Session(
            user_id=user_b,
            token_hash=hash_token(new_token()),
            created_at=_BASE,
            expires_at=_BASE,
            revoked=True,
            login_method="passkey",
        ),
    ]
    for row in rows:
        repo.add(row)

    svc = service(settings_registry=fresh_registry())
    svc.register_source(build_session_source(repo))
    assert "sessionmanagement" in svc.list_sources()

    # All sessions (including revoked) are exposed.
    result = svc.search(search_query(feature="sessionmanagement"))
    assert result.total == len(rows)
    for item in result.items:
        assert item.feature == "sessionmanagement"
        assert item.item_id in {str(rows[0].id), str(rows[1].id)}  # item_id = the session id (stable string identifier)

    # Filter on revoked.
    revoked = svc.search(
        search_query(
            feature="sessionmanagement",
            filters=filter_group("and", [filter_condition("revoked", "equals", True)]),
        )
    )
    assert revoked.total == 1
    assert revoked.items[0].fields["user_id"] == str(user_b)
