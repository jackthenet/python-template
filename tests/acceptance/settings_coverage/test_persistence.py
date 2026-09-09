"""AC-013 / AC-015: value persistence and precedence."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
from settings_test_helpers import make_registry

from backend.settings import SettingDefinition, SettingKind, YamlValueRepository


@pytest.fixture(autouse=True)
def _reset_registry() -> Iterator[None]:
    from backend.settings import reset_settings_registry

    reset_settings_registry()
    yield
    reset_settings_registry()


def test_set_value_persists() -> None:
    """AC-013: set_value persists all current values to the value repository."""
    reg, _bus = make_registry()
    reg.register(SettingDefinition(key="a", kind=SettingKind.TEXT, default="x"))
    reg.set_value("a", "y")

    repo = reg.value_repository
    assert repo is not None
    loaded = repo.load()
    assert loaded is not None
    assert loaded["a"] == "y"


def test_persisted_precedence(tmp_path: Path) -> None:
    """AC-015: persisted values take precedence over definition defaults."""
    directory = tmp_path / "values"
    repo = YamlValueRepository(str(directory))
    repo.save({"a": "persisted"})

    from backend.settings import SettingsRegistry

    reg = SettingsRegistry(value_repository=repo)
    reg.register(SettingDefinition(key="a", kind=SettingKind.TEXT, default="default"))
    assert reg.get_value("a") == "persisted"
