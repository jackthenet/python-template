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

# The console sink's descriptor: sys.stderr's own fd at import time. The managed
# console handler is built with whatever sys.stderr is when setup_logger() runs
# (pytest's captured stream in-process, the real stderr in a fresh interpreter),
# so the fd is taken from the live stream rather than hard-coded to 2.
STDERR_FD = sys.stderr.fileno()

# REQ-002: the feature logger owns exactly the console sink and the queue-fed file sink
MANAGED_HANDLER_COUNT = 2


def _drain_queue() -> None:
    """Wait until the queue listener has dequeued every record headed for the file sink."""
    _console, file_sink = managed_sinks()
    pending = getattr(file_sink, "queue", None)
    if pending is None:  # a file handler attached directly to the feature logger
        return
    while not pending.empty():
        time.sleep(0.001)
    time.sleep(0.005)  # dequeued: let the handler's write land on disk


def wait_for_file_content(path: Path, predicate: Callable[[str], bool], timeout: float = 15.0) -> bool:
    """Wait for a file written by an enqueued sink to satisfy predicate(content).

    First waits for the queue listener (D4) to take every queued record, so the
    wait is deterministic under load instead of relying on the listener thread's
    scheduling (which can be starved on a busy CI runner and time out).
    """
    _drain_queue()
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


try:  # pytest's logging plugin attaches its capture handler to every NON-PROPAGATING logger
    from _pytest.logging import LogCaptureHandler as _PytestCaptureHandler
except ImportError:  # pragma: no cover - running outside pytest
    _PytestCaptureHandler = None


def _is_harness_handler(handler: logging.Handler) -> bool:
    """True for a capture handler the test harness owns, which is never a managed sink.

    Two handlers belong to the harness rather than to the pipeline: pytest's
    ``catching_logs`` attaches its own ``LogCaptureHandler`` to every NON-PROPAGATING
    logger (the pipeline logger is non-propagating by design, AC-001), and the
    record-capture surface (``tests/conftest.py``) attaches its own handler to the
    pipeline logger to collect records for a test. Both mark themselves — pytest by
    type, the capture surface by the ``_harness_capture`` attribute — and the
    ownership assertions below count only the handlers the pipeline itself installed.
    """
    if getattr(handler, "_harness_capture", False):
        return True
    return _PytestCaptureHandler is not None and isinstance(handler, _PytestCaptureHandler)


def managed_handlers(logger: logging.Logger) -> list[logging.Handler]:
    """The handlers the pipeline owns on ``logger`` (harness handlers filtered out)."""
    return [h for h in logger.handlers if not _is_harness_handler(h)]


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
        if isinstance(obj, logging.Logger) and any(_is_console_handler(h) for h in managed_handlers(obj))
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
    owned = managed_handlers(feature)
    console = [h for h in owned if _is_console_handler(h)]
    file_sink = [
        h for h in owned if isinstance(h, logging.handlers.QueueHandler | logging.handlers.RotatingFileHandler)
    ]
    if len(owned) != MANAGED_HANDLER_COUNT or len(console) != 1 or len(file_sink) != 1:
        handlers = [type(h).__name__ for h in owned]
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


def parse_json_records(text: str) -> list[dict[str, Any]]:
    """The JSON-object-per-line records in ``text`` (non-JSON lines are skipped)."""
    records: list[dict[str, Any]] = []
    for line in text.splitlines():
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            records.append(parsed)
    return records


def json_records(path: Path) -> list[dict[str, Any]]:
    """The JSON-object-per-line records in ``path`` (non-JSON lines are skipped)."""
    return parse_json_records(path.read_text(encoding="utf-8"))


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
        # ponytail: the captured file is left in place because every caller reads it
        # after the block; the OS cleans the session temp dir. Upgrade path: yield the
        # decoded text instead of the path and unlink here.


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

from backend.logging import register_settings as _register_logging_settings
from backend.settings import SettingsRegistry, YamlValueRepository, set_settings_registry

_registry = SettingsRegistry(value_repository=YamlValueRepository(tempfile.mkdtemp()))
set_settings_registry(_registry)
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


# --------------------------------------------------------------------------
# In-process tracing observation (the session pipeline's file sink)
#
# A traced call is observed through the RENDERED record, never through the
# decorator's internals: the JSON object the file sink writes is the contract
# (spec §3). The three traced record kinds are told apart by their fields, not
# by message wording — an exit record carries ``elapsed_ms`` (REQ-011), an
# exception record carries ``exception`` (REQ-009), an entry record carries
# neither. Records are located by a token unique to the call under test, because
# the session log file accumulates records across tests.
# --------------------------------------------------------------------------


def session_log_path() -> Path:
    """The file-sink path of the in-process (session) pipeline."""
    import backend.logging as feature

    return Path(feature.get_settings().log_file)


def record_mentions(record: dict[str, Any], token: str) -> bool:
    """True when a rendered record names ``token`` (a traced qualname lands in the event)."""
    return token in str(record.get("event", "")) or token in str(record.get("logger", ""))


def wait_for_traced_record(
    token: str, kind: str = "exit", *, path: Path | None = None, timeout: float = 15.0
) -> dict[str, Any] | None:
    """Wait for the traced record of ``kind`` (``entry`` | ``exit`` | ``exception``) for ``token``."""
    target = session_log_path() if path is None else path

    def _match(record: dict[str, Any]) -> bool:
        if not record_mentions(record, token):
            return False
        if kind == "exit":
            return "elapsed_ms" in record
        if kind == "exception":
            return "exception" in record
        return "elapsed_ms" not in record and "exception" not in record

    return wait_for_record(target, _match, timeout=timeout)


def traced_records(token: str, *, path: Path | None = None) -> list[dict[str, Any]]:
    """Every file-sink record naming ``token`` (call it once the awaited record has landed)."""
    target = session_log_path() if path is None else path
    return [record for record in json_records(target) if record_mentions(record, token)]


def file_size(path: Path) -> int:
    """Current size of the log file in bytes (0 before the sink creates it)."""
    return path.stat().st_size if path.exists() else 0


def records_since(path: Path, offset: int) -> list[dict[str, Any]]:
    """The JSON records the file sink appended after byte ``offset``.

    A property test emits, waits for its own record, then reads only this window, so
    examples never read each other's records and a leak is attributed to the call
    that caused it.
    """
    return parse_json_records(path.read_bytes()[offset:].decode("utf-8", errors="replace"))


def wait_for_record_since(
    path: Path, offset: int, predicate: Callable[[dict[str, Any]], bool], timeout: float = 15.0
) -> dict[str, Any] | None:
    """Wait for a JSON record appended after byte ``offset``; return it, or ``None`` on timeout.

    The byte window is what keeps a property test's examples independent: the wait
    cannot be satisfied by an earlier example's record, and the caller then reads the
    same window to see exactly what this call emitted.
    """
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        for record in records_since(path, offset):
            if predicate(record):
                return record
        time.sleep(0.01)
    return None
