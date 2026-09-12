"""Contract tests for the performance budget (NFR-001)."""

from __future__ import annotations

import time

from backend.mail import build_message, render_template
from mail_test_helpers import simple_template

SAMPLES = 100
BUDGET_SECONDS = 0.05  # 50 ms at p95


def test_nfr_001_preparation_performance_budget() -> None:
    """NFR-001: email preparation (render + build) completes in <= 50 ms at p95.

    Measured with the session's logging configuration (DEBUG — a stricter
    superset of the spec's default INFO level: more per-call logging
    overhead). The SMTP delivery time is network-dependent and not budgeted.
    """
    template = simple_template()
    context = {"who": "Performance"}

    # Warm up (one-time costs are not part of the per-call budget).
    render_template(template, context)

    samples: list[float] = []
    for _ in range(SAMPLES):
        start = time.perf_counter()
        rendered = render_template(template, context)
        build_message("perf@example.com", rendered, "Performance", "perf@example.com")
        samples.append(time.perf_counter() - start)

    samples.sort()
    p95 = samples[int(0.95 * (len(samples) - 1))]
    assert p95 <= BUDGET_SECONDS
