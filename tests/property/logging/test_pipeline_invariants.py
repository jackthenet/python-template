"""Property tests for the structlog record pipeline (docs/specs/structlog-logging.md).

This module holds the pipeline-core invariants: INV-001 (the feature logger owns
exactly one console handler and one file handler) and INV-004 (no other logger's
routing state changes). INV-002, INV-003 and INV-005 belong to the tracing
decorators and are added here by that task.

The strategies generate only in-domain values: the concurrency count is a
positive thread count, the reconfigure level is one of the ``logging.log_level``
SELECT options, and the renderer is one of the ``"text" | "json" | None`` values
§3 defines.
"""

from __future__ import annotations

import inspect
import logging
from pathlib import Path

from hypothesis import given, settings
from hypothesis import strategies as st
from logging_test_helpers import PIPELINE_COUNT_CODE, pipeline_logger, run_python
from settings_test_helpers import set_value_settled

from backend.logging import setup_logger
from backend.settings import get_settings_registry

_ROTATION_BYTES = 2048
_ROTATION_BACKUPS = 3


def test_inv_001_concurrent_setup_owns_two_handlers(tmp_path: Path) -> None:
    """INV-001: for any number of concurrent setup_logger() calls, the feature logger owns exactly one console handler and one file handler.

    The subprocess shape is required: setup_logger() is idempotent per process,
    so a fresh interpreter is the only way to observe n competing setups. Beyond
    the pair count, the example pins the ownership consequences of D1 — a single
    owning logger, non-propagating, and the file handler rotating with the live
    ``logging.log_max_bytes`` / ``logging.log_backup_count`` values (REQ-002).
    """

    @settings(deadline=None, max_examples=8)  # each example costs a fresh interpreter
    @given(st.integers(min_value=1, max_value=16))
    def inner(n: int) -> None:
        log_file = tmp_path / f"inv_001_pipeline_{n}.log"
        code = f"""
import threading, tempfile
from backend.settings import SettingsRegistry, YamlValueRepository
from backend.settings import registry as _reg_mod
from backend.logging import register_settings as logging_register, setup_logger
reg = SettingsRegistry(value_repository=YamlValueRepository(tempfile.mkdtemp()))
_reg_mod._registry[0] = reg
logging_register(reg)
reg.set_value('logging.log_file', {str(log_file)!r})
reg.set_value('logging.log_level', 'INFO')
reg.set_value('logging.log_max_bytes', {_ROTATION_BYTES})
reg.set_value('logging.log_backup_count', {_ROTATION_BACKUPS})
errors = []

def worker():
    try:
        setup_logger()
    except BaseException as e:
        errors.append(e)

threads = [threading.Thread(target=worker) for _ in range({n})]
for t in threads:
    t.start()
for t in threads:
    t.join()
print("ERRORS", len(errors))
{PIPELINE_COUNT_CODE}
print("PROPAGATE", _owners[0].propagate if _owners else None)
print("MAXBYTES", _rotating[0].maxBytes if _rotating else 0)
print("BACKUPS", _rotating[0].backupCount if _rotating else 0)
"""
        result = run_python(code)
        assert result.returncode == 0, f"INV-001: the subprocess failed:\n{result.stderr}"
        out = result.stdout
        assert "ERRORS 0" in out, f"INV-001: {n} concurrent setups raised, output:\n{out}"
        assert "OWNERS 1" in out, f"INV-001: {n} concurrent setups, output:\n{out}"
        assert "CONSOLE 1" in out, f"INV-001: {n} concurrent setups, output:\n{out}"
        assert "FILE 1" in out, f"INV-001: {n} concurrent setups, output:\n{out}"
        assert "FEATURE_HANDLERS 2" in out, f"INV-001/D1: {n} concurrent setups, output:\n{out}"
        assert "PROPAGATE False" in out, f"REQ-003/D1: the feature logger must not propagate, output:\n{out}"
        assert f"MAXBYTES {_ROTATION_BYTES}" in out, (
            f"REQ-002: the file sink must rotate at the live value, output:\n{out}"
        )
        assert f"BACKUPS {_ROTATION_BACKUPS}" in out, f"REQ-002: retention must use the live value, output:\n{out}"

    inner()


def _routing_state() -> dict[str, tuple[tuple[logging.Handler, ...], int, bool]]:
    """The (handlers, level, disabled) triple of every named logger in the process.

    The root logger is not in ``loggerDict``, so it is deliberately absent here:
    INV-004's only exception is the single forwarding handler the feature
    installs on the root logger, which the test checks separately.
    """
    return {
        name: (tuple(lg.handlers), lg.level, lg.disabled)
        for name, lg in logging.Logger.manager.loggerDict.items()
        if isinstance(lg, logging.Logger)
    }


def test_inv_004_other_loggers_untouched() -> None:
    """INV-004: setup, live reconfigure and a renderer change leave every other logger's routing state unchanged.

    The foreign logger keeps its handler set, level and disabled state through
    every logging-feature operation; the root logger may gain at most the single
    forwarding handler (REQ-003) and never loses a handler it already had.
    """

    @settings(deadline=None, max_examples=20)
    @given(
        operation=st.sampled_from(("setup", "reconfigure", "renderer")),
        level=st.sampled_from(("DEBUG", "INFO", "WARNING", "ERROR")),
        renderer=st.sampled_from(("text", "json", None)),
    )
    def inner(operation: str, level: str, renderer: str | None) -> None:
        setup_logger()
        registry = get_settings_registry()
        original_level = registry.get_value("logging.log_level")
        foreign = logging.getLogger("inv_004_foreign")
        foreign.handlers.clear()
        foreign.addHandler(logging.NullHandler())
        foreign.setLevel(logging.WARNING)
        try:
            before = _routing_state()
            root_before = list(logging.getLogger().handlers)

            if operation == "setup":
                setup_logger()
            elif operation == "reconfigure":
                set_value_settled(registry, "logging.log_level", level)
            else:
                assert "renderer" in inspect.signature(setup_logger).parameters, (
                    "REQ-006: setup_logger() must accept a renderer parameter"
                )
                setup_logger(renderer=renderer)

            feature = pipeline_logger()
            after = _routing_state()
            changed = sorted(
                name for name, state in before.items() if after.get(name) != state and name != feature.name
            )
            assert not changed, f"INV-004: {operation} changed the routing state of {changed}"

            root_after = list(logging.getLogger().handlers)
            added = [handler for handler in root_after if handler not in root_before]
            assert len(added) <= 1, (
                f"INV-004/REQ-003: {operation} installed {len(added)} root handlers, at most one is allowed"
            )
            missing = [handler for handler in root_before if handler not in root_after]
            assert not missing, f"INV-004: {operation} removed {len(missing)} root handler(s) it does not own"
        finally:
            set_value_settled(registry, "logging.log_level", original_level)
            foreign.handlers.clear()
            foreign.setLevel(logging.NOTSET)

    inner()
