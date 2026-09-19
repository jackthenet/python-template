"""Fixtures for the mail property tests."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from settings_test_helpers import isolated_registry


@pytest.fixture(autouse=True)
def _reset_registry() -> Iterator[None]:
    """Isolate the settings-registry singleton across mail tests."""
    with isolated_registry():
        yield
