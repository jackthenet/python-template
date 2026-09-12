"""Fixtures for the mail acceptance tests."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from mail_test_helpers import reset_registry, setup_isolated_registry


@pytest.fixture(autouse=True)
def _reset_registry() -> Iterator[None]:
    """Isolate the settings-registry singleton across mail tests."""
    setup_isolated_registry()
    yield
    reset_registry()
