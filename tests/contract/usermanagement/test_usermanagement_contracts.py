"""Contract tests for the usermanagement feature (docs/specs/user-management.md).

Covers the spec's NFRs: performance budgets, no plaintext/hash exposure,
backward-compatible public API, concurrent repository safety, and logging
observability.
"""

from __future__ import annotations

import inspect
import threading
import time
from pathlib import Path
from typing import Any
from uuid import uuid4

import pytest
from usermanagement_test_helpers import db_url, valid_create

from backend.usermanagement import (
    InvalidRoleError,
    LastAdminError,
    SqliteUserRepository,
    UserAlreadyExistsError,
    UserCreate,
    UserManager,
    UserManagerError,
    UserNotFoundError,
    UserRead,
    UserRepository,
)

_READ_BUDGET_MS = 5.0
_WRITE_BUDGET_S = 1.0
_THREADS = 8

# The spec's public API contract (NFR-003).
_PUBLIC_API = (
    "User",
    "UserCreate",
    "UserUpdate",
    "UserRead",
    "UserEvent",
    "UserCreated",
    "UserUpdated",
    "UserDeleted",
    "UserPasswordChanged",
    "UserRoleChanged",
    "UserActivated",
    "UserDeactivated",
    "EventPublisher",
    "UserRepository",
    "SqliteUserRepository",
    "UserManager",
    "UserManagerError",
    "UserAlreadyExistsError",
    "UserNotFoundError",
    "InvalidRoleError",
    "LastAdminError",
)


def _median_ms(fn: Any, n: int) -> float:
    """The median elapsed milliseconds of ``n`` calls of ``fn``."""
    samples: list[float] = []
    for _ in range(n):
        start = time.monotonic()
        fn()
        samples.append((time.monotonic() - start) * 1000)
    samples.sort()
    return samples[len(samples) // 2]


def test_nfr_001_performance_budgets(tmp_path: Path) -> None:
    """NFR-001: reads < 5 ms (median); create_user/verify_password < 1 s (median)."""
    repo = SqliteUserRepository(db_url(tmp_path))
    manager = UserManager(repo)
    user = manager.create_user(UserCreate(**valid_create()))

    def read_once() -> None:
        manager.get_user(user.id)
        manager.get_user_by_username("alice")
        manager.list_users()

    counter = 0

    def write_once() -> None:
        nonlocal counter
        counter += 1
        manager.create_user(
            UserCreate(
                **valid_create(
                    username=f"perf{counter}x",
                    email=f"perf{counter}@example.com",
                )
            )
        )
        manager.verify_password(user.id, "correct-horse-1")

    read_ms = _median_ms(read_once, 21)
    write_s = _median_ms(write_once, 5) / 1000
    assert read_ms < _READ_BUDGET_MS, f"read median {read_ms:.3f} ms exceeds 5 ms budget"
    assert write_s < _WRITE_BUDGET_S, f"create/verify median {write_s:.3f} s exceeds 1 s budget"


def test_nfr_002_no_plaintext_or_hash_exposed(tmp_path: Path, log_records: list[Any]) -> None:
    """NFR-002: no plaintext stored or logged; only the Argon2id hash; no hash/raw User exposure."""
    password = "correct-horse-1"
    repo = SqliteUserRepository(db_url(tmp_path))
    manager = UserManager(repo)
    user = manager.create_user(UserCreate(**valid_create(password=password)))

    # Only the Argon2id hash is stored, never the plaintext.
    record = repo.get_by_id(user.id)
    assert record is not None
    assert record.password_hash.startswith("$argon2id$")
    assert record.password_hash != password

    # The raw DB file contains no plaintext.
    db_content = (tmp_path / "users.db").read_bytes().decode("utf-8", errors="ignore")
    assert password not in db_content

    # The service API never exposes password_hash or the raw User table object.
    read = manager.get_user(user.id)
    assert type(read) is UserRead
    assert "password_hash" not in UserRead.model_fields
    assert "password_hash" not in read.model_dump()
    listed = manager.list_users(include_inactive=True)
    assert all(type(u) is UserRead for u in listed)

    # Verification works against the stored hash (argon2 constant-time verify).
    assert manager.verify_password(user.id, password) is True
    assert manager.verify_password(user.id, "wrong-password-1") is False

    # Passwords never appear in log records.
    assert password not in "\n".join(str(m) for m in log_records)


def test_nfr_003_api_backward_compatible() -> None:
    """NFR-003: the public API is importable and backward-compatible."""
    import backend.usermanagement as um

    for name in _PUBLIC_API:
        assert hasattr(um, name), f"public API missing {name}"

    # Existing caller patterns keep working: positional repository first, all
    # other parameters optional.
    sig = inspect.signature(UserManager.__init__)
    params = list(sig.parameters)
    assert params[0] == "self"
    assert params[1] == "repository"
    for name in params[2:]:
        assert sig.parameters[name].default is not inspect.Parameter.empty, f"{name} must be optional"

    # SqliteUserRepository implements the UserRepository ABC, which exposes
    # the spec's repository methods.
    assert issubclass(SqliteUserRepository, UserRepository)
    for method in (
        "add",
        "get_by_id",
        "get_by_username",
        "get_by_email",
        "update",
        "delete",
        "list_all",
        "count_active_by_role",
    ):
        assert hasattr(UserRepository, method), f"UserRepository missing {method}"

    # The error hierarchy is rooted at UserManagerError.
    for exc in (UserAlreadyExistsError, UserNotFoundError, InvalidRoleError, LastAdminError):
        assert issubclass(exc, UserManagerError), f"{exc.__name__} not rooted at UserManagerError"


def test_nfr_004_concurrent_repository_safety(tmp_path: Path) -> None:
    """NFR-004: concurrent thread use is safe; parent dir auto-created; no partial state on failure."""
    # The DB file's parent directory is auto-created.
    repo = SqliteUserRepository(db_url(tmp_path, name="a/b/c/users.db"))
    manager = UserManager(repo)

    # Concurrent creates from multiple threads: all succeed, all visible.
    errors: list[BaseException] = []
    barrier = threading.Barrier(_THREADS)

    def create(i: int) -> None:
        barrier.wait()
        try:
            manager.create_user(UserCreate(**valid_create(username=f"t{i}x", email=f"t{i}@example.com")))
        except BaseException as e:  # collected, not raised
            errors.append(e)

    threads = [threading.Thread(target=create, args=(i,)) for i in range(_THREADS)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert not errors, errors
    assert len(manager.list_users()) == _THREADS

    # A failed operation leaves no partial state.
    before = [u.id for u in manager.list_users(include_inactive=True)]
    with pytest.raises(UserAlreadyExistsError) as exc_info:
        # Fresh email so only the username collides (a full duplicate would
        # violate both UNIQUE constraints; SQLite reports an ambiguous one).
        manager.create_user(UserCreate(**valid_create(username="t0x", email="fresh@example.com")))
    after = [u.id for u in manager.list_users(include_inactive=True)]
    assert before == after
    assert exc_info.value.field == "username"


def test_nfr_005_operations_logged(tmp_path: Path, log_records: list[Any]) -> None:
    """NFR-005: operations traced via the shared logging feature; errors logged with context; no passwords in logs."""
    password = "correct-horse-1"
    repo = SqliteUserRepository(db_url(tmp_path))
    manager = UserManager(repo)
    manager.create_user(UserCreate(**valid_create(password=password)))

    # A domain error is raised and logged with context.
    with pytest.raises(UserNotFoundError):
        manager.get_user(uuid4())

    text = [str(m) for m in log_records]
    # @logged_class entry/exit traces carry the method qualname.
    assert any("create_user" in t and ">>" in t for t in text), "no entry trace for create_user"
    assert any("create_user" in t and "<<" in t for t in text), "no exit trace for create_user"
    # The domain error is logged with its type (context).
    assert any("UserNotFoundError" in t for t in text), "domain error not logged"
    # Passwords never appear in log records.
    assert password not in "\n".join(text)
