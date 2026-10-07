"""AC-015: an exception record carries the exception, never the raising frame's locals.

REQ-009 renders an exception as its type, message and traceback frames — there is no
``diagnose``-style local-variable dump in the pipeline (NFR-003, INV-002). The probe
function therefore plants an identifiable value in a local of the raising frame: the
record must show the failure and the frame, and that value must appear in no record.
"""

from __future__ import annotations

import json

import pytest
from logging_test_helpers import json_records, session_log_path, wait_for_traced_record

from backend.logging import logged, setup_logger

_SECRET = "ac015-secret-local-value-9f2c74"
_MESSAGE = "ac_015 exception record probe"


def test_ac_015_no_local_values_in_exception_record() -> None:
    """AC-015: the exception record carries type, message and frames; the local's value appears in no record."""
    setup_logger()

    @logged
    def ac_015_leaky_probe() -> None:
        secret_value = _SECRET  # noqa: F841  a local in the raising frame is the point of the test
        raise RuntimeError(_MESSAGE)

    with pytest.raises(RuntimeError):
        ac_015_leaky_probe()

    record = wait_for_traced_record("ac_015_leaky_probe", "exception")
    assert record is not None, "AC-015: the exception record must reach the file sink"

    rendered = str(record["exception"])
    assert "RuntimeError" in rendered, f"AC-015/REQ-009: the exception type must be in the record, got {rendered!r}"
    assert _MESSAGE in rendered, f"AC-015/REQ-009: the exception message must be in the record, got {rendered!r}"
    assert "ac_015_leaky_probe" in rendered, (
        f"AC-015/REQ-009: the traceback frames must be in the record (the raising function names one), got {rendered!r}"
    )

    path = session_log_path()
    assert _SECRET not in path.read_text(encoding="utf-8", errors="replace"), (
        "AC-015/NFR-003: the raising frame's local value must never reach the file sink"
    )
    leaked = [entry for entry in json_records(path) if _SECRET in json.dumps(entry)]
    assert not leaked, f"AC-015/INV-002: the local value must appear in no record, got {leaked}"
