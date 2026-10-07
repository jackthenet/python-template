"""AC-010: ``setup_logger(renderer=...)`` selects the renderer pair
(docs/specs/structlog-logging.md REQ-006).

Each case runs in a fresh process: ``setup_logger()`` is idempotent per process
(REQ-002), so the renderer can only be chosen by a process that has not set the
pipeline up yet.
"""

from __future__ import annotations

from pathlib import Path

from logging_test_helpers import json_records, run_python, subprocess_setup_code


def _run(tmp_path: Path, renderer: str | None, token: str) -> tuple[Path, Path]:
    """Set the pipeline up with ``renderer`` and emit one record; return the sink files."""
    case_dir = tmp_path / (renderer or "default")
    case_dir.mkdir()
    console_file = case_dir / "console.txt"
    log_file = case_dir / "logs" / "app.log"
    renderer_arg = "" if renderer is None else f"renderer={renderer!r}"
    code = (
        subprocess_setup_code(str(log_file), {"logging.log_level": "INFO"})
        + f"""
import sys
import time
from pathlib import Path

from backend.logging import get_logger, setup_logger

console_file = Path({str(console_file)!r})
log_file = Path({str(log_file)!r})
sys.stderr = open(console_file, "w", encoding="utf-8")
setup_logger({renderer_arg})
get_logger("ac_010").info({token!r})
deadline = time.monotonic() + 15
while time.monotonic() < deadline:
    if log_file.exists() and {token!r} in log_file.read_text(encoding="utf-8", errors="replace"):
        break
    time.sleep(0.05)
sys.stderr.flush()
"""
    )
    result = run_python(code)
    assert result.returncode == 0, f"renderer={renderer!r}: setup or emit failed:\n{result.stderr}"
    return console_file, log_file


def test_ac_010_renderer_selection(tmp_path: Path) -> None:
    """AC-010: json -> JSON console record; text -> text file record; default -> text console + JSON file."""
    console_json, _ = _run(tmp_path, "json", "ac010 json console probe")
    events = [record.get("event") for record in json_records(console_json)]
    assert "ac010 json console probe" in events, (
        "AC-010: renderer='json' must write a JSON object to the console sink, got "
        f"{console_json.read_text(encoding='utf-8')!r}"
    )

    console_file, log_file = _run(tmp_path, "text", "ac010 text file probe")
    assert "ac010 text file probe" in log_file.read_text(encoding="utf-8")
    assert json_records(log_file) == [], (
        f"AC-010: renderer='text' must write human-readable text to the file sink, got {log_file.read_text('utf-8')!r}"
    )
    assert json_records(console_file) == [], "AC-010: renderer='text' must not write JSON to the console sink"

    console_file, log_file = _run(tmp_path, None, "ac010 default probe")
    assert "ac010 default probe" in console_file.read_text(encoding="utf-8")
    assert json_records(console_file) == [], "AC-010: the default console record is text"
    assert "ac010 default probe" in [record.get("event") for record in json_records(log_file)], (
        "AC-010: the default file record is JSON"
    )
