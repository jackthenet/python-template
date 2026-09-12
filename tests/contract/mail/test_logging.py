"""Contract tests for observability (NFR-004)."""

from __future__ import annotations

from backend.mail import MailService
from mail_test_helpers import RecordingTransport, simple_template

SLOW_THRESHOLD_MS = 5000
MIN_TRACE_RECORDS = 2


def test_nfr_004_service_traced(log_records) -> None:
    """NFR-004: the service is traced with @logged_class (entry/exit per public method)."""
    # The class is marked traced with the spec's slow threshold.
    assert getattr(MailService, "__logged_class__", False) is True
    assert getattr(MailService, "slow_threshold_ms", None) == SLOW_THRESHOLD_MS

    service = MailService(transport=RecordingTransport(), event_bus=None)
    service.send_email("nfr@example.com", simple_template(), {"who": "Nfr"})

    # Entry/exit records for the public method (DEBUG tracing).
    assert len(log_records) >= MIN_TRACE_RECORDS
