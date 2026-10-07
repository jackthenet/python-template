"""Acceptance tests for the public install operation of the feature singletons.

Spec: ``docs/specs/settings-public-registry-setter.md`` (AC-001 .. AC-014).
T-001 derives AC-001 (the settings feature); T-009/T-010/T-011 add the
remaining witnesses of this file (the five-feature parametrization, the
concurrency cases, the tracing case).
"""

from __future__ import annotations

from settings_test_helpers import restore_singleton
from singleton_install_test_helpers import SETTINGS_SLOT

from backend.settings import get_settings_registry, reset_settings_registry


def test_ac_001_install_then_get_returns_instance() -> None:
    """AC-001 (REQ-001): the install operation returns None and the getter returns that instance."""
    saved = get_settings_registry(required=False)
    try:
        reset_settings_registry()  # Given: the shared slot is empty
        registry = SETTINGS_SLOT.new()  # built with an isolated value repository
        assert SETTINGS_SLOT.install(registry) is None
        assert get_settings_registry() is registry
    finally:
        restore_singleton(saved)
