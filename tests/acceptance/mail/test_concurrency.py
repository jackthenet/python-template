"""Acceptance tests for concurrent sends (AC-018)."""

from __future__ import annotations

import threading

from backend.mail import MailService
from mail_test_helpers import RecordingTransport, simple_template

THREADS = 8
SENDS_PER_THREAD = 5


def test_ac_018_concurrent_send() -> None:
    """AC-018: send_email called concurrently — every send is independent, no thread crashes."""
    transport = RecordingTransport()
    service = MailService(transport=transport, event_bus=None)
    template = simple_template()
    errors: list[BaseException] = []
    barrier = threading.Barrier(THREADS)

    def worker(index: int) -> None:
        try:
            barrier.wait(timeout=10)
            for i in range(SENDS_PER_THREAD):
                service.send_email(f"user{index}-{i}@example.com", template, {"who": f"User {index}-{i}"})
        except BaseException as exc:  # record any worker failure
            errors.append(exc)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(THREADS)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=60)

    assert not errors
    assert len(transport.messages) == THREADS * SENDS_PER_THREAD
