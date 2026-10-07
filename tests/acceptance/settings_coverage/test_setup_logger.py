"""Live logging configuration (docs/specs/structlog-logging.md AC-017, docs/specs/settings-coverage.md v2 AC-019/AC-020).

The managed sinks are ordinary standard-library handlers (structlog-logging REQ-002),
so a ``logging.*`` change is observed through the public ``logging`` API and through
the records that reach the two sinks — never through a logging backend's private
handler table (that is what the pre-amendment versions of these tests did).
"""

from __future__ import annotations

import gc
import logging
import logging.handlers
import os
from pathlib import Path

from logging_test_helpers import (
    PIPELINE_COUNT_CODE,
    bound_logger,
    captured_console,
    managed_sinks,
    rotating_file_handlers,
    run_python,
    subprocess_setup_code,
    wait_for_record,
)
from settings_test_helpers import set_value_settled

from backend.logging import setup_logger
from backend.settings import get_settings_registry

# The rotation values AC-017 writes. Distinct from the inventory defaults
# (10485760 / 5) so a reconfigure that never lands cannot satisfy the assertion.
_AC017_MAX_BYTES = 4096
_AC017_BACKUP_COUNT = 2

# The rotation values AC-019 puts in the registry BEFORE setup, so the values the
# no-argument call reads are distinguishable from the feature's hardcoded defaults
# (10485760 / 5, and log_level INFO - hence ERROR below, which also tells the two
# apart: at the default INFO a WARNING record would still reach the sinks).
_AC019_MAX_BYTES = 2048
_AC019_BACKUP_COUNT = 3

# The rotating file sink's configuration, printed by a subprocess probe. ``tests/`` is
# not on a ``python -c`` interpreter's import path, so the scan ships as source like
# PIPELINE_COUNT_CODE, which this extends (the file handler may sit behind the queue
# listener (D4), so it is located by type among the live objects).
_ROTATING_CONFIG_CODE = """
import gc
import logging.handlers

_rotating = [obj for obj in gc.get_objects() if isinstance(obj, logging.handlers.RotatingFileHandler)]
print("ROTATING", len(_rotating))
if _rotating:
    _handler = _rotating[0]
    print("BASENAME", _handler.baseFilename)
    print("MAXBYTES", _handler.maxBytes)
    print("BACKUPS", _handler.backupCount)
    print("ENCODING", _handler.encoding)
"""


def _probe_values(stdout: str) -> dict[str, str]:
    """The ``KEY value`` lines a subprocess probe printed (``value`` may contain spaces)."""
    values: dict[str, str] = {}
    for line in stdout.splitlines():
        key, separator, value = line.partition(" ")
        if separator and key:
            values[key] = value
    return values


def _same_path(left: str, right: Path) -> bool:
    """Compare two spellings of one filesystem path (the handler stores its own form)."""
    return bool(left) and os.path.normcase(os.path.realpath(left)) == os.path.normcase(os.path.realpath(str(right)))


class _ForeignState:
    """Handlers and a logger the logging feature does not own, plus their starting state (INV-004).

    AC-017 and AC-020 both end in the same clause — only the feature's own handlers may
    change — so the witnesses are attached and checked from one place.
    """

    def __init__(self, logger_name: str) -> None:
        self.root = logging.getLogger()
        self.other = logging.getLogger(logger_name)
        self.on_root = logging.Handler()
        self.on_other = logging.Handler()
        for handler in (self.on_root, self.on_other):
            handler.setLevel(logging.ERROR)
            handler.setFormatter(logging.Formatter("%(message)s"))
        self.root.addHandler(self.on_root)
        self.other.setLevel(logging.DEBUG)
        self.other.addHandler(self.on_other)
        self.root_handlers = list(self.root.handlers)
        self.other_state = (self.other.level, self.other.propagate, self.other.disabled)

    def assert_untouched(self) -> None:
        """INV-004: the reconfigure may not detach, re-level, re-route or disable what it does not own."""
        assert self.on_root in self.root.handlers, "INV-004: a root handler the feature does not own must stay attached"
        assert self.on_other in self.other.handlers, "INV-004: another feature's logger must stay untouched"
        for handler in (self.on_root, self.on_other):
            assert handler.level == logging.ERROR, "INV-004: a foreign handler must keep its own level"
            assert handler.formatter is not None, "INV-004: a foreign handler must keep its own formatter"
        assert (self.other.level, self.other.propagate, self.other.disabled) == self.other_state, (
            "INV-004: the reconfigure must not re-level, re-route or disable another logger"
        )
        assert set(self.root_handlers).issubset(self.root.handlers), (
            "INV-004: the feature may add only its own forwarding handler to the root logger"
        )

    def remove(self) -> None:
        """Take the witnesses back out so they never leak into another test."""
        self.root.removeHandler(self.on_root)
        self.other.removeHandler(self.on_other)
        self.other.setLevel(logging.NOTSET)


def test_ac_017_live_reconfigure(tmp_path: Path) -> None:
    """AC-017/REQ-012: a ``logging.*`` change reconfigures the running process's own handlers in place.

    One process, no restart: the level, the rotation parameters and the file path are
    each re-applied by the write that changed them, and the third clause (INV-004) —
    only the feature's own handlers change — is asserted in the same run.
    """
    setup_logger()
    managed_sinks()  # the honest RED signal: no managed standard-library sinks yet

    foreign = _ForeignState("ac_017_other_feature")
    registry = get_settings_registry()
    original = {
        key: registry.get_value(key)
        for key in ("logging.log_level", "logging.log_file", "logging.log_max_bytes", "logging.log_backup_count")
    }
    session_log_file = Path(str(original["logging.log_file"]))
    moved_log_file = tmp_path / "reconfigured" / "ac017.log"

    suppressed = "ac017 debug suppressed probe"
    accepted = "ac017 debug accepted probe"
    moved = "ac017 moved sink probe"
    try:
        # (1) level, re-applied: a DEBUG record must not reach the console at WARNING.
        set_value_settled(registry, "logging.log_level", "WARNING")
        with captured_console() as console_path:
            bound_logger("ac_017").debug(suppressed)
            assert suppressed not in console_path.read_text(encoding="utf-8"), (
                "AC-017: the console sink must not emit DEBUG while logging.log_level is WARNING"
            )

            # (2) the AC-017 write: DEBUG, in the same running process.
            set_value_settled(registry, "logging.log_level", "DEBUG")
            bound_logger("ac_017").debug(accepted)
        console_text = console_path.read_text(encoding="utf-8")
        assert accepted in console_text, "AC-017: DEBUG records must reach the console sink without a restart"
        assert wait_for_record(session_log_file, lambda record: record.get("event") == accepted) is not None, (
            "AC-017: DEBUG records must reach the file sink without a restart"
        )

        # (3) rotation parameters, re-applied by the write that changed them.
        set_value_settled(registry, "logging.log_max_bytes", _AC017_MAX_BYTES)
        set_value_settled(registry, "logging.log_backup_count", _AC017_BACKUP_COUNT)
        gc.collect()
        rotating = rotating_file_handlers()
        assert len(rotating) == 1, (
            f"INV-001: exactly one managed rotating file handler after a reconfigure, found {len(rotating)}"
        )
        assert rotating[0].maxBytes == _AC017_MAX_BYTES, "AC-017: the rotation size must be re-applied"
        assert rotating[0].backupCount == _AC017_BACKUP_COUNT, "AC-017: the backup count must be re-applied"

        # (4) the file path, re-applied (EDGE-001: the parent directory is created).
        set_value_settled(registry, "logging.log_file", str(moved_log_file))
        bound_logger("ac_017").info(moved)
        assert wait_for_record(moved_log_file, lambda record: record.get("event") == moved) is not None, (
            "AC-017: the file sink must follow logging.log_file without a restart"
        )

        # (5) only the feature's own handlers change (AC-017 third clause, INV-004).
        managed_sinks()
        foreign.assert_untouched()
    finally:
        for key, value in original.items():
            set_value_settled(registry, key, value)
        foreign.remove()


def test_setup_logger_reads_registry(tmp_path: Path) -> None:
    """AC-019 (settings-coverage v2): the no-argument ``setup_logger()`` reads ``logging.*`` from the shared registry.

    Re-derived from the amended wording: the call stays argument-free (REQ-014 v2 — any
    parameter the amended signature adds is optional and keyword-only), and the values it
    read are observed on the two managed standard-library sinks and in the records that
    reach them. The pre-amendment probe printed loguru's private ``sink._file.name``.
    """
    log_file = tmp_path / "logs" / "ac019.log"
    code = (
        subprocess_setup_code(
            str(log_file),
            {
                "logging.log_level": "ERROR",
                "logging.log_max_bytes": _AC019_MAX_BYTES,
                "logging.log_backup_count": _AC019_BACKUP_COUNT,
            },
        )
        + """
from backend.logging import setup_logger

setup_logger()  # no arguments: the specified default call shape (REQ-014 v2)
"""
        + PIPELINE_COUNT_CODE
        + _ROTATING_CONFIG_CODE
        + """
import logging

# The console sink is a standard-library StreamHandler (REQ-002), so its output is
# complete when the process exits: the level the registry configured is observable in
# the captured stderr without any waiting.
logging.getLogger("ac_019_probe").error("ac019 error probe")
logging.getLogger("ac_019_probe").warning("ac019 warning probe")
"""
    )
    result = run_python(code)
    assert result.returncode == 0, result.stderr
    values = _probe_values(result.stdout)

    assert values.get("CONSOLE") == "1", f"REQ-002: the no-arg setup must own one console sink: {result.stdout}"
    assert values.get("FILE") == "1", f"REQ-002: the no-arg setup must own one file sink: {result.stdout}"
    assert values.get("FEATURE_HANDLERS") == "2", (
        f"INV-001: the feature logger must own exactly the two sinks: {result.stdout}"
    )
    assert values.get("ROTATING") == "1", f"REQ-002: the file sink must be a rotating file handler: {result.stdout}"
    assert _same_path(values.get("BASENAME", ""), log_file), (
        f"AC-019: logging.log_file from the registry must configure the file sink, got {values.get('BASENAME')!r}"
    )
    assert values.get("MAXBYTES") == str(_AC019_MAX_BYTES), (
        "AC-019: logging.log_max_bytes from the registry must configure the file sink"
    )
    assert values.get("BACKUPS") == str(_AC019_BACKUP_COUNT), (
        "AC-019: logging.log_backup_count from the registry must configure the file sink"
    )
    assert values.get("ENCODING") == "utf-8", "REQ-002: the file sink writes UTF-8"
    assert "ac019 error probe" in result.stderr, (
        "AC-019: logging.log_level=ERROR from the registry must route ERROR records to the console sink"
    )
    assert "ac019 warning probe" not in result.stderr, (
        "AC-019: logging.log_level=ERROR from the registry must not route WARNING records (the default is INFO)"
    )


def test_sink_reconfigured_on_change() -> None:
    """AC-020 (settings-coverage v2): a ``logging.log_level`` change makes both managed sinks emit at DEBUG, no restart.

    Re-derived from the amended wording: the observable contract is unchanged (both sinks
    follow the new level in the running process) and the third clause — only the
    feature's own sinks change — is asserted explicitly. The pre-amendment probe polled
    loguru's private ``h._levelno``; this one observes the records that reach the sinks,
    so it does not pin the handler-level mechanism the implementation is free to choose.
    """
    setup_logger()
    managed_sinks()

    registry = get_settings_registry()
    original_level = str(registry.get_value("logging.log_level"))
    foreign = _ForeignState("ac_020_other_feature")

    suppressed = "ac020 debug suppressed probe"
    accepted = "ac020 debug accepted probe"
    try:
        with captured_console() as console_path:
            set_value_settled(registry, "logging.log_level", "WARNING")
            bound_logger("ac_020").debug(suppressed)
            assert suppressed not in console_path.read_text(encoding="utf-8"), (
                "AC-020: the console sink must not emit DEBUG while logging.log_level is WARNING"
            )

            # The AC-020 write, in the same running process.
            set_value_settled(registry, "logging.log_level", "DEBUG")
            bound_logger("ac_020").debug(accepted)
        assert accepted in console_path.read_text(encoding="utf-8"), (
            "AC-020: the console sink must emit at DEBUG after the change, without a restart"
        )

        log_file = Path(str(registry.get_value("logging.log_file")))
        assert wait_for_record(log_file, lambda record: record.get("event") == accepted) is not None, (
            "AC-020: the file sink must emit at DEBUG after the change, without a restart"
        )

        # Only the feature's own sinks change (AC-020 third clause, REQ-015 v2, INV-004).
        managed_sinks()
        foreign.assert_untouched()
    finally:
        set_value_settled(registry, "logging.log_level", original_level)
        foreign.remove()
