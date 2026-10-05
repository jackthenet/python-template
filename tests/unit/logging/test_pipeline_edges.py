"""Edge cases of the standard-library logging pipeline (docs/specs/structlog-logging.md
EDGE-001, EDGE-002, EDGE-004, EDGE-005, EDGE-006 and NFR-005).

The subprocess cases need a process in which ``setup_logger()`` has not run yet
(nested paths, rotation, thread count, use-before-setup); the in-process cases
need the session's live pipeline.
"""

from __future__ import annotations

import inspect
import logging
from pathlib import Path

import pytest
from logging_test_helpers import (
    captured_console,
    json_records,
    managed_sinks,
    run_python,
    subprocess_setup_code,
    wait_for_record,
)

import backend.logging as feature
from backend.logging import setup_logger

# Polling helper for the subprocess bodies: the file sink is fed through a queue,
# so the writer runs on the listener thread and the process waits for its output.
_WAIT_FOR = """
def _wait_for(path, token):
    deadline = time.monotonic() + 15
    while time.monotonic() < deadline:
        if path.exists() and token in path.read_text(encoding="utf-8", errors="replace"):
            return True
        time.sleep(0.05)
    return False
"""


def test_edge_001_log_file_parent_created(tmp_path: Path) -> None:
    """EDGE-001: a log_file path whose parent directory does not exist is created."""
    log_file = tmp_path / "deep" / "nested" / "logs" / "app.log"
    token = "edge_001 nested log path probe"
    code = (
        subprocess_setup_code(str(log_file), {"logging.log_level": "INFO"})
        + f"""
import logging
import time
from pathlib import Path

from backend.logging import setup_logger

{_WAIT_FOR}
setup_logger()
logging.getLogger("edge_001").warning({token!r})
_wait_for(Path({str(log_file)!r}), {token!r})
"""
    )

    result = run_python(code)
    assert result.returncode == 0, f"EDGE-001: setup with a nested log path failed:\n{result.stderr}"
    assert log_file.parent.is_dir(), "EDGE-001: the parent directory must be created"
    assert log_file.is_file(), "EDGE-001: the log file must be created"

    probe = [record for record in json_records(log_file) if record.get("event") == token]
    assert probe, f"EDGE-001: the record must be written as JSON, got {log_file.read_text('utf-8')!r}"
    missing = {"level", "logger", "event", "timestamp", "file", "line"} - probe[0].keys()
    assert not missing, f"REQ-011: the record is missing {sorted(missing)}: {probe[0]!r}"


def test_edge_002_rotation_with_open_handle(tmp_path: Path) -> None:
    """EDGE-002: rotation while the handle is open neither raises nor loses the record."""
    log_file = tmp_path / "logs" / "app.log"
    code = (
        subprocess_setup_code(
            str(log_file),
            {"logging.log_level": "INFO", "logging.log_max_bytes": 1000, "logging.log_backup_count": 2},
        )
        + f"""
import logging
import time
from pathlib import Path

from backend.logging import setup_logger

setup_logger()
log = logging.getLogger("edge_002")
for i in range(60):
    log.warning("edge_002 rotation probe %03d %s" % (i, "x" * 60))
log_dir = Path({str(log_file)!r}).parent
deadline = time.monotonic() + 15
while time.monotonic() < deadline:
    written = "".join(p.read_text(encoding="utf-8", errors="replace") for p in log_dir.glob("app.log*"))
    if "edge_002 rotation probe 059" in written:
        break
    time.sleep(0.05)
"""
    )

    result = run_python(code)
    assert result.returncode == 0, f"EDGE-002: an exception escaped the emitting call:\n{result.stderr}"
    assert "--- Logging error ---" not in result.stderr, (
        f"EDGE-002: rotation must not fail inside the handler:\n{result.stderr}"
    )

    rotated = sorted(log_file.parent.glob("app.log*"))
    assert len(rotated) > 1, f"EDGE-002: rotation must produce a backup file, found {[p.name for p in rotated]}"
    content = "\n".join(path.read_text(encoding="utf-8", errors="replace") for path in rotated)
    assert "edge_002 rotation probe 059" in content, "EDGE-002: the newest record must not be lost silently"


def test_edge_004_unknown_numeric_level() -> None:
    """EDGE-004: a record with a non-standard numeric level reaches both sinks with it preserved."""
    setup_logger()

    third_party = logging.getLogger("edge_004_numeric_level")
    token = "edge_004 numeric level probe"

    with captured_console() as console_path:
        third_party.log(47, token)

    console_text = console_path.read_text(encoding="utf-8")
    assert token in console_text, "EDGE-004: the record must reach the console sink"
    assert "47" in console_text, f"EDGE-004: the numeric level must be preserved on the console, got {console_text!r}"

    record = wait_for_record(Path(feature.get_settings().log_file), lambda r: r.get("event") == token)
    assert record is not None, "EDGE-004: the record must reach the file sink"
    assert "47" in str(record["level"]), f"EDGE-004: the numeric level must be preserved, got {record['level']!r}"


def test_edge_005_unknown_renderer() -> None:
    """EDGE-005: an unknown renderer value raises ValueError before any handler changes."""
    setup_logger()

    parameters = inspect.signature(setup_logger).parameters
    assert "renderer" in parameters, "REQ-006: setup_logger() must accept a renderer parameter"
    assert parameters["renderer"].kind is inspect.Parameter.KEYWORD_ONLY, "REQ-006: renderer is keyword-only"

    before = managed_sinks()
    with pytest.raises(ValueError):
        setup_logger(renderer="yaml")
    assert managed_sinks() == before, "EDGE-005: the previous sink configuration must stay intact"


def test_edge_006_get_logger_before_setup(tmp_path: Path) -> None:
    """EDGE-006: get_logger() before setup_logger() neither raises nor reaches the managed sinks."""
    log_file = tmp_path / "logs" / "app.log"
    token = "edge_006 before setup probe"
    code = (
        subprocess_setup_code(str(log_file), {"logging.log_level": "INFO"})
        + f"""
from backend.logging import get_logger

get_logger("edge_006").warning({token!r})
print("NO-EXCEPTION")
"""
    )

    result = run_python(code)
    assert result.returncode == 0, f"EDGE-006: using get_logger() before setup must not raise:\n{result.stderr}"
    assert "NO-EXCEPTION" in result.stdout
    assert token in result.stderr, "EDGE-006: the record goes through the standard library's default handling"
    assert not log_file.exists() or token not in log_file.read_text(encoding="utf-8", errors="replace"), (
        "EDGE-006: the record must not be routed to the managed sinks"
    )


def test_nfr_005_single_listener_thread(tmp_path: Path) -> None:
    """NFR-005: the pipeline adds at most one thread, and emitting adds none."""
    log_file = tmp_path / "logs" / "app.log"
    code = (
        subprocess_setup_code(str(log_file), {"logging.log_level": "INFO"})
        + """
import logging
import logging.handlers
import threading

from backend.logging import setup_logger

before = threading.active_count()
setup_logger()
after_setup = threading.active_count()
log = logging.getLogger("nfr_005")
for i in range(100):
    log.info("nfr_005 probe %d" % i)
after_emit = threading.active_count()
queued = [
    handler
    for logger in logging.Logger.manager.loggerDict.values()
    if isinstance(logger, logging.Logger)
    for handler in logger.handlers
    if isinstance(handler, logging.handlers.QueueHandler)
]
print(before, after_setup, after_emit, len(queued))
"""
    )

    result = run_python(code)
    assert result.returncode == 0, f"NFR-005: the subprocess failed:\n{result.stderr}"
    before, after_setup, after_emit, queue_handlers = (int(value) for value in result.stdout.split()[-4:])
    assert after_setup - before <= 1, f"NFR-005: setup added {after_setup - before} threads, at most one is allowed"
    assert after_emit == after_setup, "NFR-005: emitting records must not add a thread per call"
    assert queue_handlers >= 1, "D4/REQ-010: the file sink must be fed through a queue handler"
