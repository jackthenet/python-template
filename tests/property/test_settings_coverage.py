"""Property tests for the settings-coverage feature (INV-001..INV-005)."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from backend.settings import (
    ListSpec,
    SettingDefinition,
    SettingKind,
    SettingsRegistry,
    YamlValueRepository,
)
from settings_test_helpers import make_registry

pytestmark = [settings(max_examples=25, deadline=None)]


@pytest.fixture(autouse=True)
def _reset_registry() -> Iterator[None]:
    from backend.settings import reset_settings_registry

    reset_settings_registry()
    yield
    reset_settings_registry()


_STRINGS = st.text(min_size=1, max_size=16).filter(lambda s: s.islower() and s.isalpha())


def test_get_value_valid_for_kind() -> None:
    """INV-001: for every registered setting, get_value returns a value valid for its kind."""
    from backend.settings.models import value_valid_for

    @given(value=_STRINGS)
    def check(value: str) -> None:
        reg, _bus = make_registry()
        reg.register(SettingDefinition(key="a", kind=SettingKind.TEXT, default=value))
        d = reg.get_definition("a")
        current = reg.get_value("a")
        assert value_valid_for(d, current)

    check()


def test_list_round_trip() -> None:
    """INV-002: for a LIST setting, a persisted value round-trips (save then load)."""
    from pathlib import Path

    @given(items=st.lists(_STRINGS, min_size=0, max_size=8))
    def check(items: list[str]) -> None:
        directory = Path("test_round_trip_dir")
        repo = YamlValueRepository(str(directory))
        repo.save({"roles": items})
        loaded = repo.load()
        assert loaded is not None
        assert loaded["roles"] == items

    check()


def test_live_read_after_set() -> None:
    """INV-003: for any feature, a live read after set_value returns value."""
    @given(value=_STRINGS)
    def check(value: str) -> None:
        reg, _bus = make_registry()
        reg.register(SettingDefinition(key="a", kind=SettingKind.TEXT, default="x"))
        reg.set_value("a", value)
        assert reg.get_value("a") == value

    check()


def test_register_idempotent_fresh() -> None:
    """INV-004: register_settings on a fresh registry succeeds; twice raises SettingsRegistrationError."""
    from backend.logging import register_settings as logging_register
    from backend.settings.exceptions import SettingsRegistrationError

    reg, _bus = make_registry()
    logging_register(reg)  # fresh registry: succeeds
    with pytest.raises(SettingsRegistrationError):
        logging_register(reg)  # same registry: duplicate keys


def test_persisted_precedence_invariant(tmp_path_factory: pytest.TempPathFactory) -> None:
    """INV-005: the persisted value takes precedence over the default."""
    from pathlib import Path

    @given(value=_STRINGS)
    def check(value: str) -> None:
        directory = tmp_path_factory.mktemp("precedence")
        repo = YamlValueRepository(str(directory))
        repo.save({"a": value})
        reg = SettingsRegistry(value_repository=repo)
        reg.register(SettingDefinition(key="a", kind=SettingKind.TEXT, default="default"))
        assert reg.get_value("a") == value

    check()
