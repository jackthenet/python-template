"""Fixtures for the mail unit tests."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from mail_test_helpers import reset_registry


@pytest.fixture(autouse=True)
def _reset_registry() -> Iterator[None]:
    """Isolate the settings-registry singleton across mail tests."""
    reset_registry()
    yield
    reset_registry()
