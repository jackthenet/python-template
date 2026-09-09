"""Application entrypoint.

Calls ``setup_logger`` exactly once at startup, before any feature code runs
(spec section 3.3, REQ-011). The call is idempotent and thread-safe, so a
second call (e.g. from a test or a re-import) is a no-op.
"""

from backend.logging import Settings, setup_logger

setup_logger(Settings(log_level="INFO"))
