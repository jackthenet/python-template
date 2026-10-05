"""Plain helper functions for the logging feature test suite.

Kept separate from tests/conftest.py (which holds fixtures) so test modules
can import the helpers without going through pytest's conftest machinery.
"""

from __future__ import annotations

import gc
import json
import logging
import logging.handlers
import os
import subprocess
import sys
import tempfile
import time
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from loguru import logger

# standard error's descriptor: the console sink's stream, whatever pytest redirects
STDERR_FD = 2

# REQ-002: the feature logger owns exactly the console sink and the queue-fed file sink
MANAGED_HANDLER_COUNT = 2


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


# --------------------------------------------------------------------------
# stdlib pipeline helpers (docs/specs/structlog-logging.md)
#
# The managed sinks are ordinary standard-library handlers (REQ-002), so the
# tests locate them through the public ``logging`` machinery instead of through
# a backend's private handler table. ``rotating_file_handlers`` is the one place
# that cannot: the file handler may sit behind the queue listener (D4), so it is
# found by type among the live objects rather than by walking the logger tree.
# --------------------------------------------------------------------------


def _is_console_handler(handler: logging.Handler) -> bool:
    """A non-file StreamHandler writing to standard error (the managed console sink)."""
    if isinstance(handler, logging.FileHandler) or not isinstance(handler, logging.StreamHandler):
        return False
    stream = getattr(handler, "stream", None)
    if stream is sys.stderr:
        return True
    fileno = getattr(stream, "fileno", None)
    try:
        return bool(callable(fileno) and fileno() == STDERR_FD)
    except OSError:  # a closed or redirected stream has no descriptor
        return False


def pipeline_logger() -> logging.Logger:
    """The logging feature's own logger: the non-root logger that owns the console sink.

    D1 pins the ownership model (a dedicated, non-propagating logger owns the two
    managed handlers), so the console sink identifies it without naming it.
    Raises ``AssertionError`` when the pipeline is not installed - the honest RED
    signal for every test that requires the managed sinks to exist.
    """
    manager = logging.Logger.manager
    candidates = [
        obj
        for obj in manager.loggerDict.values()
        if isinstance(obj, logging.Logger) and any(_is_console_handler(h) for h in obj.handlers)
    ]
    if len(candidates) != 1:
        found = {lg.name: [type(h).__name__ for h in lg.handlers] for lg in candidates}
        raise AssertionError(f"expected exactly one logger owning the managed console sink, found {found}")
    return candidates[0]


def managed_sinks() -> tuple[logging.Handler, logging.Handler]:
    """The two managed sinks as ``(console handler, file sink handler)`` (REQ-002).

    The file sink is the rotating file handler itself or the queue handler that
    feeds it (D4); either way the feature logger owns exactly two handlers.
    """
    feature = pipeline_logger()
    console = [h for h in feature.handlers if _is_console_handler(h)]
    file_sink = [
        h
        for h in feature.handlers
        if isinstance(h, logging.handlers.QueueHandler | logging.handlers.RotatingFileHandler)
    ]
    if len(feature.handlers) != MANAGED_HANDLER_COUNT or len(console) != 1 or len(file_sink) != 1:
        handlers = [type(h).__name__ for h in feature.handlers]
        raise AssertionError(
            f"REQ-002/INV-001: the feature logger must own one console + one file sink, got {handlers}"
        )
    return console[0], file_sink[0]


def rotating_file_handlers() -> list[logging.handlers.RotatingFileHandler]:
    """Every ``logging.handlers.RotatingFileHandler`` alive in the process.

    The managed file handler is fed through a queue listener (D4), so it is not
    always reachable from a logger's handler list; its rotation parameters
    (``maxBytes``/``backupCount``/``encoding``) are the REQ-002 contract, so the
    tests read them from the handler itself.
    """
    return [obj for obj in gc.get_objects() if isinstance(obj, logging.handlers.RotatingFileHandler)]


def json_records(path: Path) -> list[dict[str, Any]]:
    """The JSON-object-per-line records in ``path`` (non-JSON lines are skipped)."""
    records: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            records.append(parsed)
    return records


@contextmanager
def captured_console() -> Iterator[Path]:
    """Redirect the descriptor the managed console handler writes to, yielding its file.

    fd-level capture (not ``capsys``) because the managed console sink holds the
    stream object it was constructed with, which is not necessarily the current
    ``sys.stderr``; the descriptor is taken from the handler's own stream.
    """
    console, _file_sink = managed_sinks()
    fd = int(console.stream.fileno())
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


def bound_logger(name: str) -> Any:
    """A bound logger from the feature's public ``get_logger()`` (REQ-005).

    Resolved through ``getattr`` so a missing export fails as an assertion about the
    required API, not as an import error at collection time.
    """
    import backend.logging as feature

    get_logger = getattr(feature, "get_logger", None)
    assert callable(get_logger), "REQ-005: backend.logging must export get_logger()"
    return get_logger(name)


def wait_for_record(
    path: Path, predicate: Callable[[dict[str, Any]], bool], timeout: float = 15.0
) -> dict[str, Any] | None:
    """Wait for the file sink to write a JSON record matching ``predicate``; return it.

    Returns ``None`` on timeout, so the caller's assertion names the record it wanted
    rather than failing inside the polling helper.
    """
    match: list[dict[str, Any]] = []

    def _found(_content: str) -> bool:
        hit = next((record for record in json_records(path) if predicate(record)), None)
        if hit is None:
            return False
        match.append(hit)
        return True

    return match[0] if wait_for_file_content(path, _found, timeout=timeout) else None


# The preamble a subprocess test uses to get a settings registry with the logging
# feature's settings registered (the same shape as the in-process session fixture).
_SUBPROCESS_REGISTRY_PREAMBLE = """
import tempfile
from pathlib import Path

import backend.settings.registry as _registry_module
from backend.logging import register_settings as _register_logging_settings
from backend.settings import SettingsRegistry, YamlValueRepository

_registry = SettingsRegistry(value_repository=YamlValueRepository(tempfile.mkdtemp()))
_registry_module._registry[0] = _registry
_register_logging_settings(_registry)
"""


def subprocess_setup_code(log_file: str, values: dict[str, object] | None = None) -> str:
    """Python source that installs an isolated registry with ``logging.*`` values.

    Used by the subprocess tests (renderer selection, rotation, thread count), which
    need a process where ``setup_logger()`` has not run yet.
    """
    lines = [_SUBPROCESS_REGISTRY_PREAMBLE, f"_registry.set_value('logging.log_file', {log_file!r})"]
    lines += [f"_registry.set_value({key!r}, {value!r})" for key, value in (values or {}).items()]
    return "\n".join(lines)


# The handler scan the subprocess tests share: ``tests/`` is not on a subprocess's
# import path, so the same scan the in-process helpers perform ships as source.
PIPELINE_COUNT_CODE = """
import gc
import logging
import logging.handlers
import sys


def _is_console(handler):
    return (
        isinstance(handler, logging.StreamHandler)
        and not isinstance(handler, logging.FileHandler)
        and getattr(handler, "stream", None) is sys.stderr
    )


_owners = [
    lg
    for lg in logging.Logger.manager.loggerDict.values()
    if isinstance(lg, logging.Logger) and any(_is_console(h) for h in lg.handlers)
]
_console = sum(len([h for h in lg.handlers if _is_console(h)]) for lg in _owners)
_queued = sum(len([h for h in lg.handlers if isinstance(h, logging.handlers.QueueHandler)]) for lg in _owners)
_rotating = [obj for obj in gc.get_objects() if isinstance(obj, logging.handlers.RotatingFileHandler)]
print("OWNERS", len(_owners))
print("CONSOLE", _console)
print("FILE", len(_rotating))
print("QUEUED", _queued)
print("FEATURE_HANDLERS", sum(len(lg.handlers) for lg in _owners))
"""


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
