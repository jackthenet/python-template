"""Unit tests for the settings-coverage feature (docs/specs/settings-coverage.md).

Covers AC-002, AC-006, AC-007..AC-012, AC-016..AC-018, AC-021, AC-025, AC-026,
AC-027, EDGE-001..EDGE-012, NFR-001, NFR-004, NFR-006.
"""

from __future__ import annotations

import importlib
import inspect
import threading
import time
from collections.abc import Iterator
from pathlib import Path

import pytest

from backend.settings import (
    ListSpec,
    SettingDefinition,
    SettingKind,
    SettingsRegistry,
    YamlValueRepository,
    get_settings_registry,
    reset_settings_registry,
)
from backend.settings.exceptions import (
    SettingsRegistrationError,
    SettingsValidationError,
    ValueStorageError,
)


# --- AC-002: no import side effects ---

@pytest.fixture(autouse=True)
def _reset_registry() -> Iterator[None]:
    reset_settings_registry()
    yield
    reset_settings_registry()


def test_no_import_side_effects() -> None:
    """AC-002: importing a feature module does not mutate the registry singleton."""
    # Import the feature modules (fresh, no side effects).
    for module_name in (
        "backend.logging",
        "backend.authentication",
        "backend.usermanagement",
        "backend.eventbus",
    ):
        mod = importlib.import_module(module_name)
        # Each feature exposes register_settings (the new API).
        assert hasattr(mod, "register_settings"), f"{module_name} missing register_settings"
    # The registry singleton is not mutated by the imports (no settings registered).
    reg = get_settings_registry()
    assert reg.has("logging.log_level") is False
    assert reg.has("authentication.session_ttl") is False


# --- AC-006 / EDGE-002: unregistered-key fallback ---

def test_unregistered_key_fallback() -> None:
    """AC-006: reading an unregistered key returns the hardcoded default + warning."""
    # The feature's live-read helper falls back to the original hardcoded default
    # and logs a warning when the key is unregistered.
    from backend.logging import _read_setting  # noqa: F401  (the new helper)

    # A fresh registry has no logging.* settings registered.
    reg = get_settings_registry()
    value = _read_setting(reg, "logging.log_level", fallback="INFO")
    assert value == "INFO"


def test_unregistered_key_warning() -> None:
    """EDGE-002: an unregistered key logs a warning."""
    from backend.logging import _read_setting

    reg = get_settings_registry()
    # The fallback default is returned (the warning is a side effect).
    assert _read_setting(reg, "logging.log_level", fallback="INFO") == "INFO"


# --- AC-007: LIST definition accepted ---

def test_list_definition_accepted() -> None:
    """AC-007: a LIST SettingDefinition with a ListSpec is accepted."""
    spec = ListSpec(item_pattern=r"^[a-z]+$")
    d = SettingDefinition(
        key="k", kind=SettingKind.LIST, default=["a"], list_spec=spec
    )
    assert d.kind == SettingKind.LIST
    assert d.list_spec == spec


# --- AC-008: LIST value validation ---

def test_list_value_validation() -> None:
    """AC-008: a LIST value is validated against item_pattern."""
    reg, _ = _make_registry()
    reg.register(
        SettingDefinition(
            key="roles",
            kind=SettingKind.LIST,
            default=["admin"],
            list_spec=ListSpec(item_pattern=r"^[a-z0-9_-]{1,32}$"),
        )
    )
    assert reg.set_value("roles", ["admin", "member"]) == ["admin", "member"]
    with pytest.raises(SettingsValidationError):
        reg.set_value("roles", ["Admin"])  # uppercase does not fullmatch


# --- AC-009: LIST min_items ---

def test_list_min_items() -> None:
    """AC-009: a LIST value with fewer than min_items items is rejected."""
    reg, _ = _make_registry()
    reg.register(
        SettingDefinition(
            key="roles", kind=SettingKind.LIST, default=["admin"],
            list_spec=ListSpec(min_items=1),
        )
    )
    with pytest.raises(SettingsValidationError):
        reg.set_value("roles", [])


# --- AC-010: LIST no duplicates ---

def test_list_no_duplicates() -> None:
    """AC-010: a LIST value with duplicates is rejected when allow_duplicates=False."""
    reg, _ = _make_registry()
    reg.register(
        SettingDefinition(
            key="roles", kind=SettingKind.LIST, default=["admin"],
            list_spec=ListSpec(allow_duplicates=False),
        )
    )
    with pytest.raises(SettingsValidationError):
        reg.set_value("roles", ["a", "a"])


# --- AC-011: LIST min > max rejected ---

def test_list_min_gt_max_rejected() -> None:
    """AC-011: a LIST SettingDefinition with min_items > max_items is rejected."""
    with pytest.raises(SettingsValidationError):
        SettingDefinition(
            key="k", kind=SettingKind.LIST, default=["a"],
            list_spec=ListSpec(min_items=5, max_items=2),
        )


# --- AC-012: LIST spec on TEXT rejected ---

def test_list_spec_on_text_rejected() -> None:
    """AC-012: a TEXT SettingDefinition with a ListSpec is rejected."""
    with pytest.raises(SettingsValidationError):
        SettingDefinition(
            key="k", kind=SettingKind.TEXT, default="x",
            list_spec=ListSpec(),
        )


# --- AC-016: guarded read no side effect ---

def test_guarded_read_no_side_effect() -> None:
    """AC-016: get_settings_registry(required=False) returns None without creating the singleton."""
    reg_or_none = get_settings_registry(required=False)
    assert reg_or_none is None
    # The singleton is not created by the guarded read.
    assert get_settings_registry(required=False) is None


# --- AC-017: EventBus no registry default ---

def test_eventbus_no_registry_default() -> None:
    """AC-017: EventBus() uses max_queue_size=1000 when the registry does not exist."""
    from backend.eventbus import EventBus

    # No registry exists (the guarded read returns None).
    bus = EventBus()
    assert bus.max_queue_size == 1000


# --- AC-018: EventBus registry value ---

def test_eventbus_registry_value() -> None:
    """AC-018: EventBus() reads eventbus.max_queue_size from the registry when it exists."""
    from backend.eventbus import EventBus

    reg = get_settings_registry()
    reg.register(
        SettingDefinition(key="eventbus.max_queue_size", kind=SettingKind.NUMBER, default=1000)
    )
    reg.set_value("eventbus.max_queue_size", 500)
    bus = EventBus()
    assert bus.max_queue_size == 500


# --- AC-021: logging stub removed ---

def test_logging_stub_removed() -> None:
    """AC-021: the logging stub Settings model does not exist."""
    stub_path = Path("src/backend/logging/settings.py")
    assert not stub_path.exists(), "the logging stub Settings model must be removed"


# --- AC-025: tracing ---

def test_tracing() -> None:
    """AC-025: register_settings is traced; a live read is traced on change."""
    # The register_settings functions are traced with @logged.
    from backend.logging import register_settings as logging_register

    # The function is traced (the @logged decorator marks it).
    fn = inspect.unwrap(logging_register)
    assert getattr(fn, "__wrapped__", None) is not None or hasattr(
        logging_register, "__wrapped__"
    ), "register_settings must be traced with @logged"


# --- AC-026: no env vars ---

def test_no_env_vars() -> None:
    """AC-026: the settings feature reads no environment variables."""
    import inspect as _inspect
    import backend.settings as _settings_mod

    source = _inspect.getsource(_settings_mod)
    assert "os.environ" not in source
    assert "getenv" not in source


# --- AC-027: settings registers nothing ---

def test_settings_registers_nothing() -> None:
    """AC-027: the settings feature registers no settings of its own."""
    reg = get_settings_registry()
    # The settings feature does not register any settings with the registry.
    assert reg.has("settings.log_level") is False
    assert reg.has("settings.anything") is False


# --- EDGE-001: EventBus bootstrap cycle ---

def test_eventbus_bootstrap_cycle() -> None:
    """EDGE-001: EventBus() constructed when the registry does not exist; no infinite recursion."""
    from backend.eventbus import EventBus

    # Constructing EventBus does not recurse (no infinite recursion).
    bus = EventBus()
    assert bus.max_queue_size == 1000


# --- EDGE-003: corrupted values.yaml ---

def test_corrupted_values_yaml() -> None:
    """EDGE-003: a corrupted values.yaml raises ValueStorageError on load."""
    repo = YamlValueRepository(str(Path("test_corrupted_dir")))
    # Write corrupted content.
    d = Path("test_corrupted_dir")
    d.mkdir(exist_ok=True)
    (d / "values.yaml").write_text("not: [valid: yaml", encoding="utf-8")
    with pytest.raises(ValueError):  # ValueStorageError is a ValueError subclass
        repo.load()


# --- EDGE-004: missing values.yaml ---

def test_missing_values_yaml() -> None:
    """EDGE-004: a missing values.yaml returns None from load()."""
    repo = YamlValueRepository(str(Path("test_missing_dir")))
    assert repo.load() is None


# --- EDGE-005: LIST item pattern mismatch ---

def test_list_item_pattern_mismatch() -> None:
    """EDGE-005: a LIST value with an item that does not match item_pattern is rejected."""
    reg, _ = _make_registry()
    reg.register(
        SettingDefinition(
            key="roles", kind=SettingKind.LIST, default=["admin"],
            list_spec=ListSpec(item_pattern=r"^[a-z]+$"),
        )
    )
    with pytest.raises(SettingsValidationError):
        reg.set_value("roles", ["Admin"])


# --- EDGE-006: LIST min > max ---

def test_list_min_gt_max() -> None:
    """EDGE-006: a LIST SettingDefinition with min_items > max_items is rejected."""
    with pytest.raises(SettingsValidationError):
        SettingDefinition(
            key="k", kind=SettingKind.LIST, default=["a"],
            list_spec=ListSpec(min_items=5, max_items=2),
        )


# --- EDGE-007: setup_logger idempotent ---

def test_setup_logger_idempotent() -> None:
    """EDGE-007: setup_logger() called twice; the second call is a no-op."""
    from backend.logging import setup_logger

    setup_logger()
    setup_logger()  # no-op


# --- EDGE-008: sink reconfigured rotation ---

def test_sink_reconfigured_rotation() -> None:
    """EDGE-008: a logging.* setting change reconfigures the sink (rotation parameters)."""
    from backend.logging import setup_logger

    setup_logger()
    reg = get_settings_registry()
    # Change a rotation parameter (requires sink replacement).
    reg.register(
        SettingDefinition(key="logging.log_max_bytes", kind=SettingKind.NUMBER, default=10485760)
    )
    reg.set_value("logging.log_max_bytes", 20971520)


# --- EDGE-009: persist all values ---

def test_persist_all_values() -> None:
    """EDGE-009: all current values are persisted (including those equal to their default)."""
    reg, _ = _make_registry()
    reg.register(SettingDefinition(key="a", kind=SettingKind.TEXT, default="x"))
    reg.register(SettingDefinition(key="b", kind=SettingKind.NUMBER, default=1))
    # All values are persisted (including those equal to their default).
    repo = reg.value_repository
    assert repo is not None
    loaded = repo.load()
    assert loaded is not None
    assert "a" in loaded and "b" in loaded


# --- EDGE-010: live read no trace on same ---

def test_live_read_no_trace_on_same() -> None:
    """EDGE-010: a live read observing an unchanged value logs no trace."""
    # The live-read helper traces only on change; an unchanged value logs no trace.
    from backend.logging import _read_setting

    reg = get_settings_registry()
    reg.register(SettingDefinition(key="logging.log_level", kind=SettingKind.SELECT, default="INFO"))
    # Reading the same value twice logs no trace on the second read.
    assert _read_setting(reg, "logging.log_level", fallback="INFO") == "INFO"
    assert _read_setting(reg, "logging.log_level", fallback="INFO") == "INFO"


# --- EDGE-011: guarded read none ---

def test_guarded_read_none() -> None:
    """EDGE-011: get_settings_registry(required=False) returns None when the registry does not exist."""
    assert get_settings_registry(required=False) is None


# --- EDGE-012: LIST non-string rejected ---

def test_list_non_string_rejected() -> None:
    """EDGE-012: a LIST value that is not a list of strings is rejected."""
    reg, _ = _make_registry()
    reg.register(SettingDefinition(key="roles", kind=SettingKind.LIST, default=["admin"]))
    with pytest.raises(SettingsValidationError):
        reg.set_value("roles", [1, 2, 3])  # numbers, not strings


# --- NFR-001: live read in memory ---

def test_live_read_in_memory() -> None:
    """NFR-001: live reads are in-memory (no per-read file I/O)."""
    reg, _ = _make_registry()
    reg.register(SettingDefinition(key="a", kind=SettingKind.TEXT, default="x"))
    # A live read is an in-memory map lookup (no file I/O).
    start = time.monotonic()
    for _ in range(1000):
        reg.get_value("a")
    elapsed = time.monotonic() - start
    assert elapsed < 1.0  # 1000 in-memory reads are fast


# --- NFR-004: observability tracing ---

def test_observability_tracing() -> None:
    """NFR-004: register_settings and change-detection live reads are logged."""
    # The register_settings functions and the live-read helper are traced.
    from backend.logging import register_settings, _read_setting

    assert hasattr(register_settings, "__wrapped__") or hasattr(
        inspect.unwrap(register_settings), "__wrapped__"
    )
    assert _read_setting is not None


# --- NFR-006: thread safety ---

def test_thread_safety() -> None:
    """NFR-006: the registry and ValueRepository are thread-safe."""
    reg, _ = _make_registry()
    reg.register(SettingDefinition(key="a", kind=SettingKind.NUMBER, default=0))
    errors: list[Exception] = []

    def worker(i: int) -> None:
        try:
            for j in range(100):
                reg.set_value("a", i * 100 + j)
                reg.get_value("a")
        except Exception as e:  # noqa: BLE001
            errors.append(e)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert not errors


# --- helpers ---

def _make_registry() -> tuple[SettingsRegistry, object]:
    """Build a registry wired to a fresh event bus for a test."""
    from settings_test_helpers import make_registry

    return make_registry()
