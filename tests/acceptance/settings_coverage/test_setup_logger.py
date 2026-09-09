"""AC-019 / AC-020: setup_logger reads the registry; the sink reconfigures on change."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]


def _run(code: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        cwd=_REPO_ROOT,
    )


def test_setup_logger_reads_registry(tmp_path: Path) -> None:
    """AC-019: setup_logger() reads logging.* from the shared registry."""
    log_file = tmp_path / "app.log"
    code = f"""
import sys; sys.path.insert(0, 'src')
from backend.settings import get_settings_registry
from backend.logging import register_settings as logging_register, setup_logger
reg = get_settings_registry()
logging_register(reg)
reg.set_value('logging.log_file', {str(log_file)!r})
reg.set_value('logging.log_level', 'WARNING')
setup_logger()
from loguru import logger
for h in logger._core.handlers.values():
    sink = h._sink
    print(sink._file.name if hasattr(sink, '_file') else sink)
"""
    result = _run(code)
    assert result.returncode == 0, result.stderr
    assert str(log_file) in result.stdout, result.stdout


def test_sink_reconfigured_on_change(tmp_path: Path) -> None:
    """AC-020: a logging.* change reconfigures the sink at runtime."""
    log_file = tmp_path / "app.log"
    code = f"""
import sys, time; sys.path.insert(0, 'src')
from backend.settings import get_settings_registry
from backend.logging import register_settings as logging_register, setup_logger
reg = get_settings_registry()
logging_register(reg)
reg.set_value('logging.log_file', {str(log_file)!r})
setup_logger()
reg.set_value('logging.log_level', 'DEBUG')
deadline = time.monotonic() + 5
levels = []
while time.monotonic() < deadline:
    from loguru import logger
    levels = [h._levelno for h in logger._core.handlers.values()]
    if 10 in levels:
        break
    time.sleep(0.05)
print(levels)
"""
    result = _run(code)
    assert result.returncode == 0, result.stderr
    assert "10" in result.stdout, result.stdout
