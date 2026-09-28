"""Plain helper functions for the logging feature test suite.

Kept separate from tests/conftest.py (which holds fixtures) so test modules
can import the helpers without going through pytest's conftest machinery.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import time
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from pathlib import Path

from loguru import logger


@contextmanager
def captured_stderr() -> Iterator[Path]:
    """Redirect the stderr file descriptor (fd 2) to a temp file.

    loguru writes standard-stream sinks to the underlying file descriptor, so
    this captures console output without going through Python-level buffering.
    """
    fd = sys.stderr.fileno()
    saved_fd = os.dup(fd)
    tmp_fd, tmp_name = tempfile.mkstemp()
    tmp = Path(tmp_name)
    try:
        os.dup2(tmp_fd, fd)
        yield tmp
    finally:
        os.dup2(saved_fd, fd)
        os.close(saved_fd)
        os.close(tmp_fd)
        tmp.unlink(missing_ok=True)


def wait_for_file_content(path: Path, predicate: Callable[[str], bool], timeout: float = 15.0) -> bool:
    """Wait for a file written by an enqueued sink to satisfy predicate(content).

    First drains loguru's enqueued-sink queue via ``logger.complete()`` so the
    pending write is flushed before polling. This makes the wait deterministic
    under load instead of relying on the background writer's scheduling (which
    can be starved on a busy CI runner and time out).
    """
    logger.complete()
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if path.exists():
            try:
                if predicate(path.read_text(encoding="utf-8")):
                    return True
            except OSError:
                pass
        time.sleep(0.01)
    return False


def run_python(code: str, timeout: float = 60.0) -> subprocess.CompletedProcess[str]:
    """Run Python code in a fresh interpreter.

    The venv's editable install makes backend importable, so the subprocess
    sees the same code as the test process.
    """
    return subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
