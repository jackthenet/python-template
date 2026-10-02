"""Unit tests for the feature search sources' query functions (docs/specs/search.md).

Exercises the ``_query`` function's operator/sort/pagination paths — the
coverage gap left by the acceptance tests (``test_feature_sources.py``), which
only cover free text on one field plus ``equals``/``gte``:

- string operators: ``contains`` / ``starts_with`` / ``in_list``;
- exact operators: ``gt`` / ``lt`` / ``lte`` / ``is_null``;
- nested AND/OR filter groups (the ``_eval_group`` recursion);
- sort: custom field, ``asc``/``desc``, and the ``_sort_key`` (None-last);
- pagination: ``offset`` / ``limit`` slicing.

Each source is driven through the public API (register the source, search) so
the test covers the real query path, not a re-implementation.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from search_test_helpers import (
    db_url,
    filter_condition,
    filter_group,
    fresh_registry,
    search_query,
    service,
    sort,
)

_BASE = datetime(2024, 1, 1, tzinfo=UTC)


# --- usermanagement source -------------------------------------------------


def _usernames(svc: Any, **kwargs: Any) -> list[str]:
    """The usernames in the order the usermanagement source returns them."""
    result = svc.search(search_query(feature="usermanagement", **kwargs))
    return [item.fields["username"] for item in result.items]


def _user_service(tmp_path: Path) -> Any:
    """A SearchService with the usermanagement source over three test users.

    alice (active, created ``_BASE``, display_name ``"Alice"``),
    bob (inactive, created ``_BASE + 1d``, display_name ``None``),
    carol (active, created ``_BASE + 2d``, display_name ``"Carol"``).
    """
    from backend.usermanagement import SqliteUserRepository, User, build_user_source

    repo = SqliteUserRepository(db_url(tmp_path))
    users = [
        User(
            username="alice",
            email="alice@example.com",
            display_name="Alice",
            roles=["user"],
            password_hash="argon2id:fake-alice",
            is_active=True,
            created_at=_BASE,
            updated_at=_BASE,
        ),
        User(
            username="bob",
            email="bob@example.com",
            display_name=None,
            roles=["user"],
            password_hash="argon2id:fake-bob",
            is_active=False,
            created_at=_BASE + timedelta(days=1),
            updated_at=_BASE + timedelta(days=1),
        ),
        User(
            username="carol",
            email="carol@example.com",
            display_name="Carol",
            roles=["user"],
            password_hash="argon2id:fake-carol",
            is_active=True,
            created_at=_BASE + timedelta(days=2),
            updated_at=_BASE + timedelta(days=2),
        ),
    ]
    for u in users:
        repo.add(u)
    svc = service(settings_registry=fresh_registry())
    svc.register_source(build_user_source(repo))
    return svc


def test_user_source_free_text_all_fields(tmp_path: Path) -> None:
    svc = _user_service(tmp_path)
    # Free text matches any searchable string field (username/email/display_name).
    assert _usernames(svc, free_text="alice") == ["alice"]  # username
    assert _usernames(svc, free_text="bob@example") == ["bob"]  # email
    assert _usernames(svc, free_text="Carol") == ["carol"]  # display_name (case-insensitive)


def test_user_source_string_filter_ops(tmp_path: Path) -> None:
    svc = _user_service(tmp_path)
    assert _usernames(svc, filters=filter_group("and", [filter_condition("username", "contains", "ob")])) == ["bob"]
    assert _usernames(svc, filters=filter_group("and", [filter_condition("username", "starts_with", "al")])) == [
        "alice"
    ]
    assert _usernames(
        svc, filters=filter_group("and", [filter_condition("username", "in_list", ["alice", "carol"])])
    ) == [
        "alice",
        "carol",
    ]


def test_user_source_exact_filter_ops(tmp_path: Path) -> None:
    svc = _user_service(tmp_path)
    # Datetime comparisons (gt/lt/lte) and is_null (display_name is None for bob).
    assert _usernames(svc, filters=filter_group("and", [filter_condition("created_at", "gt", _BASE)])) == [
        "bob",
        "carol",
    ]
    assert _usernames(
        svc, filters=filter_group("and", [filter_condition("created_at", "lt", _BASE + timedelta(days=2))])
    ) == [
        "alice",
        "bob",
    ]
    assert _usernames(
        svc, filters=filter_group("and", [filter_condition("created_at", "lte", _BASE + timedelta(days=1))])
    ) == [
        "alice",
        "bob",
    ]
    assert _usernames(svc, filters=filter_group("and", [filter_condition("display_name", "is_null")])) == ["bob"]


def test_user_source_nested_groups(tmp_path: Path) -> None:
    svc = _user_service(tmp_path)
    # OR group.
    assert _usernames(
        svc,
        filters=filter_group(
            "or",
            [filter_condition("username", "equals", "alice"), filter_condition("username", "equals", "bob")],
        ),
    ) == ["alice", "bob"]
    # AND group.
    assert _usernames(
        svc,
        filters=filter_group(
            "and",
            [filter_condition("is_active", "equals", True), filter_condition("username", "contains", "a")],
        ),
    ) == ["alice", "carol"]
    # Nested (group within group): (alice OR bob) AND active -> alice only (bob is inactive).
    nested = filter_group(
        "and",
        [
            filter_group(
                "or",
                [filter_condition("username", "equals", "alice"), filter_condition("username", "equals", "bob")],
            ),
            filter_condition("is_active", "equals", True),
        ],
    )
    assert _usernames(svc, filters=nested) == ["alice"]


def test_user_source_sort(tmp_path: Path) -> None:
    svc = _user_service(tmp_path)
    assert _usernames(svc, sort=sort("username", "asc")) == ["alice", "bob", "carol"]
    assert _usernames(svc, sort=sort("username", "desc")) == ["carol", "bob", "alice"]
    assert _usernames(svc, sort=sort("created_at", "desc")) == ["carol", "bob", "alice"]


def test_user_source_pagination(tmp_path: Path) -> None:
    svc = _user_service(tmp_path)
    # Default ordering is username ascending; offset/limit slice the matched set.
    assert _usernames(svc, offset=1, limit=1) == ["bob"]
    assert _usernames(svc, offset=0, limit=2) == ["alice", "bob"]


# --- filemanagement source -------------------------------------------------


def _file_keys(svc: Any, **kwargs: Any) -> list[str]:
    """The file keys in the order the filemanagement source returns them."""
    result = svc.search(search_query(feature="filemanagement", **kwargs))
    return [item.fields["key"] for item in result.items]


def _file_service(tmp_path: Path) -> Any:
    """A SearchService with the filemanagement source over three test files.

    rep-1 (size 1024, created ``_BASE``, original_filename ``"report.txt"``),
    rep-2 (size 2048, created ``_BASE + 1d``, original_filename ``None``),
    rep-3 (size 3072, created ``_BASE + 2d``, original_filename ``"notes.txt"``).
    """
    from backend.filemanagement import FileRecord, SqliteFileRepository, build_file_source

    repo = SqliteFileRepository(db_url(tmp_path))
    records = [
        FileRecord(
            key="rep-1",
            original_filename="report.txt",
            declared_mime_type="text/plain",
            detected_mime_type="text/plain",
            size=1024,
            sha256="a" * 64,
            namespace="general",
            uploader=None,
            created_at=_BASE,
            updated_at=_BASE,
        ),
        FileRecord(
            key="rep-2",
            original_filename=None,
            declared_mime_type="text/plain",
            detected_mime_type="text/plain",
            size=2048,
            sha256="b" * 64,
            namespace="general",
            uploader=None,
            created_at=_BASE + timedelta(days=1),
            updated_at=_BASE + timedelta(days=1),
        ),
        FileRecord(
            key="rep-3",
            original_filename="notes.txt",
            declared_mime_type="text/plain",
            detected_mime_type="text/plain",
            size=3072,
            sha256="c" * 64,
            namespace="general",
            uploader=None,
            created_at=_BASE + timedelta(days=2),
            updated_at=_BASE + timedelta(days=2),
        ),
    ]
    for r in records:
        repo.add(r)
    svc = service(settings_registry=fresh_registry())
    svc.register_source(build_file_source(repo))
    return svc


def test_file_source_free_text_all_fields(tmp_path: Path) -> None:
    svc = _file_service(tmp_path)
    # Free text matches any searchable string field (key/namespace/original_filename).
    assert _file_keys(svc, free_text="rep-1") == ["rep-1"]  # key
    assert _file_keys(svc, free_text="general") == ["rep-1", "rep-2", "rep-3"]  # namespace
    assert _file_keys(svc, free_text="notes") == ["rep-3"]  # original_filename


def test_file_source_string_filter_ops(tmp_path: Path) -> None:
    svc = _file_service(tmp_path)
    assert _file_keys(svc, filters=filter_group("and", [filter_condition("key", "contains", "p-2")])) == ["rep-2"]
    assert _file_keys(svc, filters=filter_group("and", [filter_condition("key", "starts_with", "rep-1")])) == ["rep-1"]
    assert _file_keys(svc, filters=filter_group("and", [filter_condition("key", "in_list", ["rep-1", "rep-3"])])) == [
        "rep-1",
        "rep-3",
    ]


def test_file_source_exact_filter_ops(tmp_path: Path) -> None:
    svc = _file_service(tmp_path)
    # Number comparisons (gt/lt/lte) and is_null (original_filename is None for rep-2).
    assert _file_keys(svc, filters=filter_group("and", [filter_condition("size", "gt", 1024)])) == ["rep-2", "rep-3"]
    assert _file_keys(svc, filters=filter_group("and", [filter_condition("size", "lt", 3072)])) == ["rep-1", "rep-2"]
    assert _file_keys(svc, filters=filter_group("and", [filter_condition("size", "lte", 2048)])) == ["rep-1", "rep-2"]
    assert _file_keys(svc, filters=filter_group("and", [filter_condition("original_filename", "is_null")])) == ["rep-2"]


def test_file_source_nested_groups(tmp_path: Path) -> None:
    svc = _file_service(tmp_path)
    # OR group.
    assert _file_keys(
        svc,
        filters=filter_group(
            "or",
            [filter_condition("key", "equals", "rep-1"), filter_condition("key", "equals", "rep-2")],
        ),
    ) == ["rep-1", "rep-2"]
    # AND group.
    assert _file_keys(
        svc,
        filters=filter_group(
            "and",
            [filter_condition("namespace", "equals", "general"), filter_condition("key", "contains", "rep")],
        ),
    ) == ["rep-1", "rep-2", "rep-3"]
    # Nested (group within group): (rep-1 OR rep-2) AND size > 1500 -> rep-2 only.
    nested = filter_group(
        "and",
        [
            filter_group(
                "or",
                [filter_condition("key", "equals", "rep-1"), filter_condition("key", "equals", "rep-2")],
            ),
            filter_condition("size", "gt", 1500),
        ],
    )
    assert _file_keys(svc, filters=nested) == ["rep-2"]


def test_file_source_sort(tmp_path: Path) -> None:
    svc = _file_service(tmp_path)
    assert _file_keys(svc, sort=sort("key", "asc")) == ["rep-1", "rep-2", "rep-3"]
    assert _file_keys(svc, sort=sort("key", "desc")) == ["rep-3", "rep-2", "rep-1"]
    assert _file_keys(svc, sort=sort("size", "desc")) == ["rep-3", "rep-2", "rep-1"]


def test_file_source_pagination(tmp_path: Path) -> None:
    svc = _file_service(tmp_path)
    # Default ordering is created_at ascending (rep-1, rep-2, rep-3).
    assert _file_keys(svc, offset=1, limit=1) == ["rep-2"]
    assert _file_keys(svc, offset=0, limit=2) == ["rep-1", "rep-2"]


# --- sessionmanagement source ----------------------------------------------


def _session_user_ids(svc: Any, **kwargs: Any) -> list[str]:
    """The user_ids in the order the sessionmanagement source returns them."""
    result = svc.search(search_query(feature="sessionmanagement", **kwargs))
    return [item.fields["user_id"] for item in result.items]


def _session_service(tmp_path: Path) -> tuple[Any, list[tuple[str, str]]]:
    """A SearchService with the sessionmanagement source over three sessions.

    Returns the service and the (user_id, session_id) pairs in creation order:
    s1 (login_method ``"password"``, not revoked, created ``_BASE``),
    s2 (login_method ``None``, revoked, created ``_BASE + 1d``),
    s3 (login_method ``"passkey"``, not revoked, created ``_BASE + 2d``).
    """
    import uuid

    from backend.authentication.models import Session
    from backend.authentication.repository import SqliteSessionRepository
    from backend.sessionmanagement import build_session_source

    repo = SqliteSessionRepository(db_url(tmp_path))
    u1, u2, u3 = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
    sessions = [
        Session(
            user_id=u1,
            token_hash="token-hash-1",
            created_at=_BASE,
            expires_at=_BASE + timedelta(days=7),
            revoked=False,
            login_method="password",
        ),
        Session(
            user_id=u2,
            token_hash="token-hash-2",
            created_at=_BASE + timedelta(days=1),
            expires_at=_BASE + timedelta(days=8),
            revoked=True,
            login_method=None,
        ),
        Session(
            user_id=u3,
            token_hash="token-hash-3",
            created_at=_BASE + timedelta(days=2),
            expires_at=_BASE + timedelta(days=9),
            revoked=False,
            login_method="passkey",
        ),
    ]
    for s in sessions:
        repo.add(s)
    svc = service(settings_registry=fresh_registry())
    svc.register_source(build_session_source(repo))
    return svc, [(str(u1), str(sessions[0].id)), (str(u2), str(sessions[1].id)), (str(u3), str(sessions[2].id))]


def test_session_source_free_text(tmp_path: Path) -> None:
    svc, pairs = _session_service(tmp_path)
    u1, s1_id = pairs[0]
    # Free text on session_id (the only searchable field) matches that session.
    assert _session_user_ids(svc, free_text=s1_id) == [u1]


def test_session_source_string_filter_ops(tmp_path: Path) -> None:
    svc, pairs = _session_service(tmp_path)
    u1, s1_id = pairs[0]
    u3, s3_id = pairs[2]
    # String ops on session_id (unique substrings of the random UUID).
    assert _session_user_ids(
        svc, filters=filter_group("and", [filter_condition("session_id", "contains", s1_id[4:20])])
    ) == [u1]
    assert _session_user_ids(
        svc, filters=filter_group("and", [filter_condition("session_id", "starts_with", s1_id[:8])])
    ) == [u1]
    assert _session_user_ids(
        svc, filters=filter_group("and", [filter_condition("session_id", "in_list", [s1_id, s3_id])])
    ) == [u3, u1]


def test_session_source_exact_filter_ops(tmp_path: Path) -> None:
    svc, pairs = _session_service(tmp_path)
    u1, _ = pairs[0]
    u2, _ = pairs[1]
    u3, _ = pairs[2]
    # Datetime comparisons (created_at) and is_null (login_method is None for s2).
    assert _session_user_ids(svc, filters=filter_group("and", [filter_condition("created_at", "gt", _BASE)])) == [
        u3,
        u2,
    ]
    assert _session_user_ids(
        svc, filters=filter_group("and", [filter_condition("created_at", "lt", _BASE + timedelta(days=2))])
    ) == [
        u2,
        u1,
    ]
    assert _session_user_ids(
        svc, filters=filter_group("and", [filter_condition("created_at", "lte", _BASE + timedelta(days=1))])
    ) == [
        u2,
        u1,
    ]
    assert _session_user_ids(svc, filters=filter_group("and", [filter_condition("login_method", "is_null")])) == [u2]


def test_session_source_nested_groups(tmp_path: Path) -> None:
    svc, pairs = _session_service(tmp_path)
    u1, _ = pairs[0]
    u2, _ = pairs[1]
    u3, _ = pairs[2]
    # OR group: revoked equals False OR revoked equals True -> all three.
    assert _session_user_ids(
        svc,
        filters=filter_group(
            "or",
            [filter_condition("revoked", "equals", False), filter_condition("revoked", "equals", True)],
        ),
    ) == [u3, u2, u1]
    # AND group: revoked equals False AND login_method equals "password" -> s1 only.
    assert _session_user_ids(
        svc,
        filters=filter_group(
            "and",
            [filter_condition("revoked", "equals", False), filter_condition("login_method", "equals", "password")],
        ),
    ) == [u1]
    # Nested: (login_method "password" OR "passkey") AND revoked False -> s1, s3.
    nested = filter_group(
        "and",
        [
            filter_group(
                "or",
                [
                    filter_condition("login_method", "equals", "password"),
                    filter_condition("login_method", "equals", "passkey"),
                ],
            ),
            filter_condition("revoked", "equals", False),
        ],
    )
    assert _session_user_ids(svc, filters=nested) == [u3, u1]


def test_session_source_sort(tmp_path: Path) -> None:
    svc, pairs = _session_service(tmp_path)
    u1, _ = pairs[0]
    u2, _ = pairs[1]
    u3, _ = pairs[2]
    # Sort by created_at (asc/desc).
    assert _session_user_ids(svc, sort=sort("created_at", "asc")) == [u1, u2, u3]
    assert _session_user_ids(svc, sort=sort("created_at", "desc")) == [u3, u2, u1]
    # Sort by login_method (a string field; None last): "passkey" < "password" < None.
    assert _session_user_ids(svc, sort=sort("login_method", "asc")) == [u3, u1, u2]


def test_session_source_pagination(tmp_path: Path) -> None:
    svc, pairs = _session_service(tmp_path)
    u2, _ = pairs[1]
    u3, _ = pairs[2]
    # Default ordering is created_at DESCENDING (s3, s2, s1).
    assert _session_user_ids(svc, offset=1, limit=1) == [u2]
    assert _session_user_ids(svc, offset=0, limit=2) == [u3, u2]
