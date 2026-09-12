"""Integration tests for concurrent sends (NFR-005)."""

from __future__ import annotations

import threading

from backend.mail import MailService
from mail_test_helpers import EventCollector, RecordingTransport, ensure_mail_settings, simple_template

THREADS = 8
SENDS_PER_THREAD = 4


def test_nfr_005_concurrent_send_thread_safety() -> None:
    """NFR-005: the service is safe for concurrent use from multiple threads (full stack)."""
    ensure_mail_settings()  # the full stack: settings + service + transport + events
    transport = RecordingTransport()
    events = EventCollector()
    service = MailService(transport=transport, event_bus=events)
    template = simple_template()
    errors: list[BaseException] = []

    def worker(index: int) -> None:
        try:
            for i in range(SENDS_PER_THREAD):
                service.send_email(f"t{index}-{i}@example.com", template, {"who": f"T{index}-{i}"})
        except BaseException as exc:  # record any worker failure
            errors.append(exc)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(THREADS)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=60)

    assert not errors
    assert len(transport.messages) == THREADS * SENDS_PER_THREAD
    assert len(events.events) == THREADS * SENDS_PER_THREAD
