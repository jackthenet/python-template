"""Contract tests for the logging feature (docs/specs/logging.md).

Covers the spec's non-functional requirements: setup time budget, decorator
overhead budget, diagnose=False (no local variable leakage), and the
backward-compatible public API.
"""

from __future__ import annotations

import inspect
import logging
import re
import statistics
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

from logging_test_helpers import managed_sinks, pipeline_logger, run_python, wait_for_file_content
from loguru import logger

from backend.logging import logged, setup_logger

_SETUP_TIME_BUDGET_MS = 25  # structlog-logging NFR-001 amends logging.md NFR-001 (was 50 ms)

# structlog-logging NFR-002 amends logging.md NFR-002: the budget is measured with both
# managed sinks active at DEBUG (was 1 ms with the logging backend's output disabled).
# Reference measurement: 0.148 ms/call with console + queue + rotating file at DEBUG
# (n = 3, Windows 11 / Python 3.14.5 / 32 CPU) — the budget keeps ~6.7x headroom.
_OVERHEAD_BUDGET_MS = 1.0
_OVERHEAD_CALLS_PER_SAMPLE = 500
_OVERHEAD_SAMPLES = 3


def test_nfr_001_setup_time_budget(tmp_path: Path) -> None:
    """NFR-001 (structlog-logging, amending logging.md NFR-001): setup_logger() completes in under 25 ms (median of 3 fresh processes)."""
    log_file = tmp_path / "nfr_001.log"
    code = f"""
import time, tempfile
from backend.settings import SettingsRegistry, YamlValueRepository
from backend.settings import registry as _reg_mod
from backend.logging import register_settings as logging_register, setup_logger
reg = SettingsRegistry(value_repository=YamlValueRepository(tempfile.mkdtemp()))
_reg_mod._registry[0] = reg
logging_register(reg)
reg.set_value('logging.log_file', {str(log_file)!r})
reg.set_value('logging.log_level', 'INFO')
start = time.perf_counter()
setup_logger()
elapsed_ms = (time.perf_counter() - start) * 1000
print(f"SETUP_MS {{elapsed_ms:.2f}}")
"""
    samples: list[float] = []
    for _ in range(3):
        result = run_python(code)
        assert result.returncode == 0, result.stderr
        match = re.search(r"SETUP_MS ([\d.]+)", result.stdout)
        assert match, result.stdout
        samples.append(float(match.group(1)))
    assert statistics.median(samples) < _SETUP_TIME_BUDGET_MS


def test_nfr_002_decorator_overhead_budget() -> None:
    """NFR-002 (structlog-logging, amending logging.md NFR-002): @logged overhead stays under 1 ms/call.

    Measurement context (binding): both managed sinks — the console handler and the
    queue-fed rotating file handler — are installed and active at DEBUG, and nothing
    is disabled. The old gate measured with the removed backend's logging switched
    off, which is not the context the observability policy requires: every traced call
    writes an entry and an exit record, so that cost belongs in the budget.
    """
    setup_logger()
    console, file_sink = managed_sinks()
    assert console is not None and file_sink is not None, "NFR-002: both managed sinks must be active"
    effective = pipeline_logger().getEffectiveLevel()
    assert effective <= logging.DEBUG, (
        f"NFR-002: the measurement context requires the pipeline active at DEBUG, got level {effective}"
    )

    @logged
    def nfr_002_noop() -> None:
        return None

    def bare_noop() -> None:
        return None

    def median_per_call(fn: Callable[[], None], n: int) -> float:
        fn()
        start = time.perf_counter()
        for _ in range(n):
            fn()
        return (time.perf_counter() - start) / n

    samples = [
        median_per_call(nfr_002_noop, _OVERHEAD_CALLS_PER_SAMPLE)
        - median_per_call(bare_noop, _OVERHEAD_CALLS_PER_SAMPLE)
        for _ in range(_OVERHEAD_SAMPLES)
    ]
    overhead_ms = statistics.median(samples) * 1000
    assert overhead_ms < _OVERHEAD_BUDGET_MS, (
        f"NFR-002: @logged costs {overhead_ms:.3f} ms/call with both managed sinks active at DEBUG "
        f"(budget {_OVERHEAD_BUDGET_MS} ms)"
    )


def test_nfr_003_diagnose_false(session_settings: Any) -> None:
    """NFR-003: the file sink uses diagnose=False; local variable values never reach the log file."""
    secret = "SECRET_TOKEN_12345"
    try:
        local_secret = secret  # noqa: F841  (the variable's existence in the frame is the point)
        raise RuntimeError("nfr_003 leak test")
    except RuntimeError:
        logger.exception("nfr_003 leak test")

    log_file = Path(session_settings.log_file)
    assert wait_for_file_content(log_file, lambda c: "nfr_003 leak test" in c, timeout=15)
    content = log_file.read_text(encoding="utf-8")
    assert secret not in content


def test_nfr_004_backward_compatible_api() -> None:
    """NFR-004 (logging.md v3): the public API stays importable from ``backend.logging``.

    v3 restates the compatibility promise: what has to stay compatible is the import
    path and the names, not the parameter surface — ``@logged``'s parameter list is the
    amended REQ-005 list, so the removed ``context_getter`` / ``depth`` must be gone
    (AC-013, design decision D6).
    """
    import backend.logging as logging_feature

    for name in ("setup_logger", "logged", "logged_class", "get_logger"):
        assert hasattr(logging_feature, name), f"NFR-004: {name} must stay importable from backend.logging"

    logged_params = set(inspect.signature(logging_feature.logged).parameters)
    for param in ("level", "slow_threshold_ms", "slow_threshold_setting", "include_args"):
        assert param in logged_params, f"NFR-004/REQ-005: logged missing parameter {param}"
    for removed in ("context_getter", "depth"):
        assert removed not in logged_params, (
            f"NFR-004 v3/AC-013: {removed} is removed from the @logged surface (no shim, no alias)"
        )

    setup_sig = inspect.signature(logging_feature.setup_logger)
    # setup_logger() stays callable with no arguments (REQ-014); any parameter it does
    # accept is optional and keyword-only, so an existing setup_logger() call keeps working.
    setup_logger()
    for parameter in setup_sig.parameters.values():
        assert parameter.kind is inspect.Parameter.KEYWORD_ONLY, (
            f"NFR-004 v3: setup_logger() parameter {parameter.name} must be keyword-only"
        )
        assert parameter.default is not inspect.Parameter.empty, (
            f"NFR-004 v3: setup_logger() parameter {parameter.name} must be optional"
        )
