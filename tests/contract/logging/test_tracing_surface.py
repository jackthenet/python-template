"""Contract tests for the logging feature's public tracing surface.

AC-020 (docs/specs/structlog-logging.md REQ-015) pins the export surface of
``backend.logging``: exactly the §3 public API, and no logging backend is
reachable through the feature. AC-013 (the removed ``context_getter`` / ``depth``
decorator parameters) is added to this module by the tracing-decorator task.
"""

from __future__ import annotations

import inspect

import pytest
from logging_test_helpers import wait_for_traced_record

_PUBLIC_API = frozenset(
    {
        "setup_logger",
        "logged",
        "logged_class",
        "get_logger",
        "Settings",
        "get_settings",
        "register_settings",
        "_read_setting",
    }
)


def test_ac_020_public_export_surface() -> None:
    """AC-020: backend.logging exports exactly the §3 public API and re-exports no logging backend."""
    import backend.logging as feature

    assert set(feature.__all__) == set(_PUBLIC_API), "AC-020/REQ-015: the export set must be exactly §3's public API"

    for name in _PUBLIC_API:
        assert hasattr(feature, name), f"AC-020/REQ-015: backend.logging must export {name}()"

    for backend_name in ("logger", "loguru"):
        assert backend_name not in feature.__all__, (
            f"AC-020: no logging backend may be re-exported (found {backend_name})"
        )

    with pytest.raises(ImportError):
        from backend.logging import (  # noqa: F401  # AC-020: features must not reach a backend through the feature
            logger,
        )


# --------------------------------------------------------------------------
# AC-013: the decorator's parameter surface after the removals (REQ-007, D6)
#
# ``context_getter`` and ``depth`` are removed with no compatibility shim and no
# deprecation alias, so applying them must raise TypeError. The retained
# parameters keep their observable behavior: ``level`` selects the record level,
# ``include_args`` renders the argument representation into the entry record, and
# the two slow-threshold parameters resolve as logging.md defines them.
# --------------------------------------------------------------------------

_REMOVED_PARAMETERS = ("context_getter", "depth")
_RETAINED_PARAMETERS = ("level", "slow_threshold_ms", "slow_threshold_setting", "include_args")
_SLOW_THRESHOLD_MS = 1
_SLOW_WORK_ITEMS = 2_000_000
_UNKNOWN_SETTING = "no_such_logging_setting"


def test_ac_013_removed_parameters() -> None:
    """AC-013: applying a removed parameter raises TypeError; the retained ones behave as before."""
    import backend.logging as feature

    parameters = inspect.signature(feature.logged).parameters
    for removed in _REMOVED_PARAMETERS:
        assert removed not in parameters, f"AC-013/REQ-007/D6: @logged must not accept {removed} (no shim, no alias)"
        with pytest.raises(TypeError):
            feature.logged(**{removed: None})

    for retained in _RETAINED_PARAMETERS:
        assert retained in parameters, f"REQ-005 (logging.md): @logged must keep the {retained} parameter"

    feature.setup_logger()

    @feature.logged(level="INFO", include_args=True)
    def ac_013_level_and_args_probe(value: str) -> None:
        return None

    ac_013_level_and_args_probe("ac_013 argument value")
    entry = wait_for_traced_record("ac_013_level_and_args_probe", "entry")
    assert entry is not None, "AC-013: level and include_args must still emit an entry record"
    assert entry["level"] == "INFO", f"AC-013: level must still select the record level, got {entry.get('level')!r}"
    assert "ac_013 argument value" in str(entry["event"]), (
        "AC-013: include_args=True must still render the argument representation into the entry record"
    )

    @feature.logged(slow_threshold_ms=_SLOW_THRESHOLD_MS)
    def ac_013_slow_probe() -> int:
        return sum(range(_SLOW_WORK_ITEMS))

    ac_013_slow_probe()
    slow_exit = wait_for_traced_record("ac_013_slow_probe", "exit")
    assert slow_exit is not None, "AC-013: slow_threshold_ms must still emit an exit record"
    assert slow_exit["level"] == "WARNING", (
        f"AC-013/logging.md REQ-014: a call slower than slow_threshold_ms must escalate its exit "
        f"record to WARNING, got {slow_exit.get('level')!r}"
    )

    # slow_threshold_setting resolves against the live Settings; an unknown name yields no threshold.
    # (The resolved threshold is read through the wrapper attribute the whole suite already uses,
    # e.g. logging_coverage/test_slow_threshold.py.)
    resolved_wrapper = feature.logged(slow_threshold_setting="log_backup_count")(lambda: None)
    resolved = getattr(resolved_wrapper, "slow_threshold_ms", None)
    assert resolved == feature.get_settings().log_backup_count, (
        f"AC-013/logging.md REQ-005: slow_threshold_setting must resolve from Settings, got {resolved!r}"
    )
    unknown_wrapper = feature.logged(slow_threshold_setting=_UNKNOWN_SETTING)(lambda: None)
    unknown = getattr(unknown_wrapper, "slow_threshold_ms", None)
    assert unknown is None, (
        f"AC-013/logging.md EDGE-003: an unknown slow_threshold_setting yields no threshold, got {unknown!r}"
    )
