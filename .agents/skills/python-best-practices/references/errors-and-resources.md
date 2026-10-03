# Errors and resources

## Group handlers that do the same thing

Avoid (only when both handlers are identical):
```python
try:
    do()
except ValueError:
    handle()
except TypeError:
    handle()
```

Prefer:
```python
import structlog

log = structlog.get_logger()

try:
    do()
except (ValueError, TypeError) as exc:
    log.warning("do_failed", error_type=type(exc).__name__, error=str(exc))
    raise
```

Rules:
- Catch the narrowest exceptions that you can actually handle.
- Log with the logger, not `print`. Re-raise (`raise`) unless you truly recover.
- Keep different handlers separate when the recovery differs.
- Never write `except Exception: pass`.

## Context managers for setup and cleanup

Use `try/finally` inside so cleanup runs even when the body raises. Use a monotonic clock for durations.

```python
from collections.abc import Iterator
from contextlib import contextmanager
from time import perf_counter

import structlog

log = structlog.get_logger()


@contextmanager
def timer(label: str) -> Iterator[None]:
    start = perf_counter()
    try:
        yield
    finally:
        log.info("elapsed", label=label, seconds=perf_counter() - start)


with timer("squares"):
    total = sum(i * i for i in range(10**6))
```

Why not `time.time()`: it is not monotonic and can jump (clock changes).
Always use `with` for files, locks, DB sessions and HTTP clients instead of manual open/close.