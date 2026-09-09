"""Contract tests for the logging feature (docs/specs/logging.md).

Covers the spec's non-functional requirements: setup time budget, decorator
overhead budget, diagnose=False (no local variable leakage), and the
backward-compatible public API.
"""

from __future__ import annotations

import inspect
import re
import statistics
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

from logging_test_helpers import run_python, wait_for_file_content
from loguru import logger

from backend.logging import logged

_SETUP_TIME_BUDGET_MS = 10


def test_nfr_001_setup_time_budget(tmp_path: Path) -> None:
    """NFR-001: setup_logger() completes in under 10 ms (median of 3 fresh processes)."""
    log_file = tmp_path / "nfr_001.log"
    code = f"""
import time
from backend.settings import get_settings_registry
from backend.logging import register_settings as logging_register, setup_logger
reg = get_settings_registry()
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
    """NFR-002: @logged decorator overhead per call is under 1 ms.

    Measured as the median per-call time of a decorated no-op minus an
    undecorated no-op, with DEBUG-level logging disabled so the log output
    itself (not the decorator machinery) is excluded from the budget.
    """

    @logged
    def nfr_002_noop() -> None:
        return None

    def bare_noop() -> None:
        return None

    nfr_002_noop()
    bare_noop()

    def median_per_call(fn: Callable[[], None], n: int) -> float:
        fn()
        start = time.perf_counter()
        for _ in range(n):
            fn()
        return (time.perf_counter() - start) / n

    logger.disable("DEBUG")
    try:
        decorated = median_per_call(nfr_002_noop, 500)
        bare = median_per_call(bare_noop, 500)
    finally:
        logger.enable("DEBUG")

    overhead_ms = (decorated - bare) * 1000
    assert overhead_ms < 1


def test_nfr_003_diagnose_false(session_settings: Any) -> None:
    """NFR-003: the file sink uses diagnose=False; local variable values never reach the log file."""
    secret = "SECRET_TOKEN_12345"
    try:
        local_secret = secret  # noqa: F841  (the variable's existence in the frame is the point)
        raise RuntimeError("nfr_003 leak test")
    except RuntimeError:
        logger.exception("nfr_003 leak test")

    log_file = Path(session_settings.log_file)
    assert wait_for_file_content(log_file, lambda c: "nfr_003 leak test" in c, timeout=5)
    content = log_file.read_text(encoding="utf-8")
    assert secret not in content


def test_nfr_004_backward_compatible_api() -> None:
    """NFR-004: the public API preserves the backward-compatible surface."""
    import backend.logging as logging_feature

    for name in ("setup_logger", "logged", "logged_class"):
        assert hasattr(logging_feature, name), name

    logged_params = set(inspect.signature(logging_feature.logged).parameters)
    for param in ("level", "slow_threshold_ms", "slow_threshold_setting", "include_args", "context_getter", "depth"):
        assert param in logged_params, f"logged missing parameter {param}"

    setup_sig = inspect.signature(logging_feature.setup_logger)
    # setup_logger() is no-arg (REQ-014): it reads the logging settings from the
    # shared registry, so it must be callable with no arguments.
    assert len(setup_sig.parameters) == 0
