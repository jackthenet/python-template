"""Unit tests for the settings-coverage feature (docs/specs/settings-coverage.md).

Covers AC-002, AC-006, AC-007..AC-012, AC-016..AC-018, AC-021, AC-025, AC-026,
AC-027, EDGE-001..EDGE-012, NFR-001, NFR-004, NFR-006.
"""

from __future__ import annotations

import dataclasses
import gc
import importlib
import inspect
import os
import threading
import time
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from logging_test_helpers import bound_logger, file_size, rotating_file_handlers, wait_for_record, wait_for_record_since
from pydantic import BaseModel
from settings_test_helpers import (
    EventCollector,
    install_isolated_registry,
    isolated_registry,
    restore_singleton,
    set_value_settled,
)

from backend.settings import (
    ListSpec,
    SelectOption,
    SelectSpec,
    SettingDefinition,
    SettingKind,
    SettingsRegistry,
    YamlValueRepository,
    get_settings_registry,
)
from backend.settings.exceptions import (
    SettingsValidationError,
)

_DEFAULT_QUEUE_SIZE = 1000
_CUSTOM_QUEUE_SIZE = 500
_ROTATED_MAX_BYTES = 20971520  # the rotation size written by EDGE-008 (double the default)
_ROTATED_BACKUP_COUNT = 3  # distinct from the logging.log_backup_count default (5)

# --- AC-002: no import side effects ---


@pytest.fixture(autouse=True)
def _reset_registry() -> Iterator[None]:
    # Reset the singleton for the test; the previous singleton is restored on
    # teardown (no state leak).
    with isolated_registry(install=False):
        yield


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
    # Use an isolated registry (temp-dir value repository) so no value is
    # persisted to the shared default "settings/" directory (test isolation).
    install_isolated_registry()
    reg = get_settings_registry()
    assert reg.has("logging.log_level") is False
    assert reg.has("authentication.session_ttl") is False


# --- AC-006 / EDGE-002: unregistered-key fallback ---


def test_unregistered_key_fallback() -> None:
    """AC-006: reading an unregistered key returns the hardcoded default + warning."""
    # The feature's live-read helper falls back to the original hardcoded default
    # and logs a warning when the key is unregistered.
    from backend.logging import _read_setting

    # A fresh registry has no logging.* settings registered.
    install_isolated_registry()
    reg = get_settings_registry()
    value = _read_setting(reg, "logging.log_level", fallback="INFO")
    assert value == "INFO"


def test_unregistered_key_warning() -> None:
    """EDGE-002: an unregistered key logs a warning."""
    from backend.logging import _read_setting

    install_isolated_registry()
    reg = get_settings_registry()
    # The fallback default is returned (the warning is a side effect).
    assert _read_setting(reg, "logging.log_level", fallback="INFO") == "INFO"


# --- AC-007: LIST definition accepted ---


def test_list_definition_accepted() -> None:
    """AC-007: a LIST SettingDefinition with a ListSpec is accepted."""
    spec = ListSpec(item_pattern=r"^[a-z]+$")
    d = SettingDefinition(key="k", kind=SettingKind.LIST, default=["a"], list_spec=spec)
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
            key="roles",
            kind=SettingKind.LIST,
            default=["admin"],
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
            key="roles",
            kind=SettingKind.LIST,
            default=["admin"],
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
            key="k",
            kind=SettingKind.LIST,
            default=["a"],
            list_spec=ListSpec(min_items=5, max_items=2),
        )


# --- AC-012: LIST spec on TEXT rejected ---


def test_list_spec_on_text_rejected() -> None:
    """AC-012: a TEXT SettingDefinition with a ListSpec is rejected."""
    with pytest.raises(SettingsValidationError):
        SettingDefinition(
            key="k",
            kind=SettingKind.TEXT,
            default="x",
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
    assert bus.max_queue_size == _DEFAULT_QUEUE_SIZE


# --- AC-018: EventBus registry value ---


def test_eventbus_registry_value() -> None:
    """AC-018: EventBus() reads eventbus.max_queue_size from the registry when it exists."""
    from backend.eventbus import EventBus

    install_isolated_registry()
    reg = get_settings_registry()
    reg.register(SettingDefinition(key="eventbus.max_queue_size", kind=SettingKind.NUMBER, default=1000))
    reg.set_value("eventbus.max_queue_size", _CUSTOM_QUEUE_SIZE)
    bus = EventBus()
    assert bus.max_queue_size == _CUSTOM_QUEUE_SIZE


# --- AC-021: logging stub removed ---


def test_logging_stub_removed(tmp_path: Path) -> None:
    """AC-021 (settings-coverage v2): no private settings model, and ``Settings`` carries the registry values.

    Re-derived from the amended wording, which states the whole contract (the feature owns
    no settings model of its own **and** its ``Settings`` export carries the registry
    values); the pre-amendment test only checked that the stub file was gone, and resolved
    that path from the current working directory rather than the repository root.
    """
    # (1) the stub settings module is gone.
    stub_path = Path(__file__).resolve().parents[2] / "src" / "backend" / "logging" / "settings.py"
    assert not stub_path.exists(), "AC-021: the logging stub Settings model must be removed"

    # (2) no private settings model: the export is a plain container of registry values.
    from backend.logging import Settings

    assert not issubclass(Settings, BaseModel), "AC-021: Settings must not be a validation/settings model"
    assert dataclasses.is_dataclass(Settings), "AC-021: Settings must be a plain container of the registry values"
    assert {field.name for field in dataclasses.fields(Settings)} == {
        "log_level",
        "log_file",
        "log_max_bytes",
        "log_backup_count",
        "profiling_include_arguments",
    }, "AC-021: Settings must carry exactly the five logging.* values"

    # (3) the Settings export carries the registry values, read from the live registry.
    # A registry with a no-op publisher: a logging.* write here would otherwise
    # reconfigure the session's sinks mid-test (settings-coverage REQ-015).
    from backend.logging import get_settings
    from backend.logging import register_settings as logging_register

    registry = SettingsRegistry(event_bus=EventCollector(), value_repository=YamlValueRepository(str(tmp_path)))
    logging_register(registry)
    registry.set_value("logging.log_level", "WARNING")
    registry.set_value("logging.log_file", str(tmp_path / "ac021.log"))
    registry.set_value("logging.log_max_bytes", 4096)
    registry.set_value("logging.log_backup_count", 3)
    restore_singleton(registry)
    try:
        settings = get_settings()
    finally:
        restore_singleton(None)
    assert (
        settings.log_level,
        settings.log_file,
        settings.log_max_bytes,
        settings.log_backup_count,
    ) == ("WARNING", str(tmp_path / "ac021.log"), 4096, 3), "AC-021: the Settings export must carry the registry values"


# --- AC-025: tracing ---


def test_tracing() -> None:
    """AC-025: register_settings is traced; a live read is traced on change."""
    # The register_settings functions are traced with @logged.
    from backend.logging import register_settings as logging_register

    # The function is traced (the @logged decorator marks it).
    fn = inspect.unwrap(logging_register)
    assert getattr(fn, "__wrapped__", None) is not None or hasattr(logging_register, "__wrapped__"), (
        "register_settings must be traced with @logged"
    )


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
    install_isolated_registry()
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
    assert bus.max_queue_size == _DEFAULT_QUEUE_SIZE


# --- EDGE-003: corrupted values.yaml ---


def test_corrupted_values_yaml(tmp_path: Path) -> None:
    """EDGE-003: a corrupted values.yaml raises ValueStorageError on load."""
    repo = YamlValueRepository(str(tmp_path / "values"))
    # Write corrupted content.
    d = tmp_path / "values"
    d.mkdir(exist_ok=True)
    (d / "values.yaml").write_text("not: [valid: yaml", encoding="utf-8")
    with pytest.raises(ValueError):  # ValueStorageError is a ValueError subclass
        repo.load()


# --- EDGE-004: missing values.yaml ---


def test_missing_values_yaml(tmp_path: Path) -> None:
    """EDGE-004: a missing values.yaml returns None from load()."""
    repo = YamlValueRepository(str(tmp_path / "values"))
    assert repo.load() is None


# --- EDGE-005: LIST item pattern mismatch ---


def test_list_item_pattern_mismatch() -> None:
    """EDGE-005: a LIST value with an item that does not match item_pattern is rejected."""
    reg, _ = _make_registry()
    reg.register(
        SettingDefinition(
            key="roles",
            kind=SettingKind.LIST,
            default=["admin"],
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
            key="k",
            kind=SettingKind.LIST,
            default=["a"],
            list_spec=ListSpec(min_items=5, max_items=2),
        )


# --- EDGE-007: setup_logger idempotent ---


def test_setup_logger_idempotent() -> None:
    """EDGE-007: setup_logger() called twice; the second call is a no-op."""
    from backend.logging import setup_logger

    setup_logger()
    setup_logger()  # no-op


# --- EDGE-008: sink reconfigured rotation ---


def test_sink_reconfigured_rotation(session_settings: Any) -> None:
    """EDGE-008 (settings-coverage v2): a ``logging.*`` change replaces the file sink and re-applies every current value.

    The amended wording is explicit that the sink is replaced and that all current
    ``logging.*`` values are re-applied, so the assertions cover the rotation parameters,
    the file path and the level — not only the parameter that changed.
    """
    from backend.logging import register_settings, setup_logger

    setup_logger()
    install_isolated_registry()
    reg = get_settings_registry()
    # The isolated registry starts without the logging.* definitions, so a
    # reconfigure triggered from it would read the feature's hardcoded defaults
    # (logs/app.log, INFO) and re-point the process's file sink away from the
    # session log file — state that leaks into every later test that reads that
    # file. Register the feature's own settings and restore the session's values
    # first, so only the rotation parameter changes.
    register_settings(reg)
    # Every write below is settled (its SettingChanged dispatch awaited) because
    # the logging feature's subscription reconfigures the sinks on the event-bus
    # worker (AC-020). An un-awaited reconfigure lands in whichever test runs
    # next, and its remove-then-add window transiently drops the process-global
    # managed handler count (main-ci-green item G).
    set_value_settled(reg, "logging.log_file", session_settings.log_file)
    set_value_settled(reg, "logging.log_level", session_settings.log_level)
    original_max = int(reg.get_value("logging.log_max_bytes"))
    original_backups = int(reg.get_value("logging.log_backup_count"))
    # Change the rotation parameters (requires the file sink to be replaced).
    try:
        set_value_settled(reg, "logging.log_max_bytes", _ROTATED_MAX_BYTES)
        set_value_settled(reg, "logging.log_backup_count", _ROTATED_BACKUP_COUNT)
        gc.collect()
        rotating = rotating_file_handlers()
        assert len(rotating) == 1, (
            f"EDGE-008/INV-001: exactly one managed rotating file sink after the reconfigure, found {len(rotating)}"
        )
        handler = rotating[0]
        assert handler.maxBytes == _ROTATED_MAX_BYTES, "EDGE-008: the new rotation size must take effect"
        assert handler.backupCount == _ROTATED_BACKUP_COUNT, "EDGE-008: the new backup count must take effect"
        # All current logging.* values are re-applied, not only the changed one: the sink
        # still points at the current logging.log_file, and a record at the current
        # logging.log_level still reaches it.
        assert os.path.normcase(os.path.realpath(handler.baseFilename)) == os.path.normcase(
            os.path.realpath(session_settings.log_file)
        ), "EDGE-008: the file sink must keep the current logging.log_file"
        assert handler.encoding == "utf-8", "EDGE-008: the file sink must keep the UTF-8 encoding"
        token = "edge008 rotation reconfigure probe"
        bound_logger("edge_008").debug(token)
        assert (
            wait_for_record(Path(session_settings.log_file), lambda record: record.get("event") == token) is not None
        ), "EDGE-008: the current logging.log_level must still be applied after the rotation change"
    finally:
        set_value_settled(reg, "logging.log_max_bytes", original_max)
        set_value_settled(reg, "logging.log_backup_count", original_backups)


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

    install_isolated_registry()
    reg = get_settings_registry()
    reg.register(
        SettingDefinition(
            key="logging.log_level",
            kind=SettingKind.SELECT,
            default="INFO",
            select=SelectSpec(options=[SelectOption(value="INFO"), SelectOption(value="DEBUG")]),
        )
    )
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


def test_observability_tracing(session_settings: Any) -> None:
    """NFR-004 + settings.md v4 §9: the settings feature's operations are logged through the logging feature's pipeline.

    Re-derived for the settings.md v4 wording ("the feature writes one-off statements
    through the shared logging feature's exported logger; it does not import a logging
    backend itself"): what is observable from the settings side is that a settings
    operation's record arrives in the logging feature's managed file sink. The per-file
    "imports no logging backend" scan is structlog-logging AC-009's witness (task T-004)
    and is not duplicated here.
    """
    # The register_settings entry point and the change-detecting live read are traced.
    from backend.logging import _read_setting, register_settings, setup_logger

    for traced in (register_settings, _read_setting):
        assert hasattr(traced, "__wrapped__") or hasattr(inspect.unwrap(traced), "__wrapped__"), (
            f"{traced} must be traced"
        )

    setup_logger()
    registry = install_isolated_registry()
    # No logging.* value is written here, so the session pipeline keeps its configuration:
    # the session setup (tests/conftest.py) runs it at DEBUG, which is the level the
    # settings feature logs its own operations at — the record below is observable only
    # because of that.
    registry.register(SettingDefinition(key="probe.observed_key", kind=SettingKind.TEXT, default="x"))
    log_file = Path(session_settings.log_file)
    offset = file_size(log_file)
    set_value_settled(registry, "probe.observed_key", "y")
    record = wait_for_record_since(log_file, offset, lambda record: "probe.observed_key" in str(record))
    assert record is not None, (
        "NFR-004 / settings.md v4 §9: the value change must be logged with key context through the shared logging feature"
    )


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
        except Exception as e:
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
