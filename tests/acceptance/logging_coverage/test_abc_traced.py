"""AC-003: repository/provider ABCs are traced; concrete subclasses inherit
tracing; the ABCs remain abstract.

REQ-003: every public repository and provider ABC is traced with
``@logged_class`` so concrete subclasses inherit tracing; tracing MUST preserve
the ABC's abstractness.
"""

from __future__ import annotations

from typing import Any

import pytest
from logging_coverage_test_helpers import (
    INVENTORY_CLASSES,
    entry_records,
    exit_records,
    for_qualname,
)

from backend.usermanagement.repository import SqliteUserRepository, UserRepository


def test_abc_traced_subclass_inherits(log_records: list[Any], tmp_path: Any) -> None:
    """AC-003: a traced ABC's concrete subclass produces entry + exit records, and the
    ABC remains abstract (direct instantiation still raises TypeError)."""
    # Every inventory ABC is traced.
    abc_names = [
        "SessionRepository",
        "PasswordResetRepository",
        "WebAuthnCredentialRepository",
        "AttemptTracker",
        "WebAuthnProvider",
        "UserRepository",
        "TemplateRepository",
    ]
    for name in abc_names:
        cls = INVENTORY_CLASSES[name]
        assert getattr(cls, "__logged_class__", False) is True, f"{name} is not traced"

    # The ABC remains abstract: direct instantiation raises TypeError.
    with pytest.raises(TypeError):
        UserRepository()  # type: ignore[call-arg]

    # A concrete subclass inherits tracing: its public method produces records.
    repo = SqliteUserRepository(f"sqlite:///{tmp_path}/abc.db")
    repo.get_by_username("probe")
    entries = for_qualname(entry_records(log_records), "SqliteUserRepository.get_by_username")
    exits = for_qualname(exit_records(log_records), "SqliteUserRepository.get_by_username")
    assert len(entries) == 1, "concrete subclass did not produce an entry record"
    assert len(exits) == 1, "concrete subclass did not produce an exit record"
