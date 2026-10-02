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


def _console_sink_fd() -> int:
    """Return the file descriptor that loguru's console (standard-stream) sink writes to.

    loguru links a standard-stream sink permanently to the stream object that
    ``sys.stderr`` referred to when the sink was ADDED. A ``logging.*`` setting
    change reconfigures the sinks at runtime (AC-020) from the event bus's
    background worker, so the console sink can be re-added at an arbitrary
    moment - possibly while ``sys.stderr`` is the real stderr rather than a
    test framework's captured stream. Redirecting the *current* ``sys.stderr``
    descriptor would then miss the sink's output, so the descriptor is taken
    from the sink's own stream.
    """
    for handler in logger._core.handlers.values():
        stream = getattr(getattr(handler, "_sink", None), "_stream", None)
        fileno = getattr(stream, "fileno", None)
        if callable(fileno):
            return int(fileno())
    return int(sys.stderr.fileno())


@contextmanager
def captured_stderr() -> Iterator[Path]:
    """Redirect the stderr file descriptor the console sink writes to.

    loguru writes standard-stream sinks to the underlying file descriptor, so
    this captures console output without going through Python-level buffering.
    The descriptor comes from the console sink's own stream (see
    ``_console_sink_fd``), not from the current ``sys.stderr``.
    """
    fd = _console_sink_fd()
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
