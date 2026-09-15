"""AC-005: constructor defaults use the registry value; an explicit argument wins."""

from __future__ import annotations

from collections.abc import Iterator

import pytest

from backend.settings import SettingDefinition, SettingKind


@pytest.fixture(autouse=True)
def _reset_registry() -> Iterator[None]:
    # Install an isolated registry (temp-dir value repository) so no value is
    # persisted to the shared default "settings/" directory (test isolation).
    from settings_test_helpers import install_isolated_registry

    install_isolated_registry()
    yield
    from backend.settings import reset_settings_registry

    reset_settings_registry()


def test_constructor_default_registry_value() -> None:
    """AC-005: without explicit arguments the registry value is used; an explicit argument wins."""
    from backend.settings import get_settings_registry

    reg = get_settings_registry()
    reg.register(SettingDefinition(key="eventbus.max_queue_size", kind=SettingKind.NUMBER, default=1000))
    reg.set_value("eventbus.max_queue_size", 500)

    from backend.eventbus import EventBus

    _REGISTRY_VALUE = 500
    _EXPLICIT_VALUE = 777
    # No explicit argument: the registry value is used.
    assert EventBus().max_queue_size == _REGISTRY_VALUE
    # Explicit argument: it wins over the registry value.
    assert EventBus(_EXPLICIT_VALUE).max_queue_size == _EXPLICIT_VALUE
