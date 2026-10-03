# Performance patterns

Apply these only after measuring (`timeit`, `py-spy`, a profiler). Do not add them by default;
readable code beats micro-optimization. Profile with `py-spy`, or on 3.15 with
`python -m profiling.sampling run script.py` (see `python-3.15.md`). Each section says when it applies and when it does not.

## Cache expensive pure computations: `functools.cache`

Avoid (function-attribute hack, rejected by type checkers):
```python
def expensive():
    if not hasattr(expensive, "cache"):
        expensive.cache = sum(i * i for i in range(10**6))
    return expensive.cache
```

Prefer:
```python
from functools import cache


@cache
def expensive() -> int:
    return sum(i * i for i in range(10**6))
```

Notes: only for pure functions with hashable arguments. Do not put `@cache` on methods (it keeps
`self` alive and leaks); use `functools.cached_property` for per-instance values. Use
`@lru_cache(maxsize=N)` when the argument space is unbounded.

## Membership tests: build the set once

A single check on a list is O(n) and converting first costs O(n) too, so this only helps for repeated lookups.

Avoid:
```python
valid = [x for x in data if x in allowed_list]
```

Prefer:
```python
allowed = frozenset(allowed_items)  # built once
valid = [x for x in data if x in allowed]
```

## Large files: stream instead of loading everything

Reading a small file whole is fine. For large files, process incrementally.

```python
from functools import partial
from pathlib import Path


def process(chunk: bytes) -> None: ...


with Path("big.bin").open("rb") as f:
    for chunk in iter(partial(f.read, 8192), b""):
        process(chunk)
```

`iter(callable, sentinel)` calls the callable until it returns the sentinel. It is the right tool for fixed-size
reads or queue draining. For text lines use `for line in f:` directly. Always pass `encoding=` when opening text files.

## Dispatch tables vs. branches

Define the table once at module level and fail loudly on unknown keys.

```python
from collections.abc import Callable


def start() -> None: ...
def stop() -> None: ...


ACTIONS: dict[str, Callable[[], None]] = {
    "start": start,
    "stop": stop,
}


def handle(action: str) -> None:
    try:
        handler = ACTIONS[action]
    except KeyError:
        raise ValueError(f"unknown action: {action!r}") from None
    handler()
```

Do not use `.get(action, lambda: None)`: it silently hides typos.
For two or three branches use plain `if/elif` or `match`; use a table when there are many cases or when handlers are registered dynamically.

## Many small instances: `slots=True`

```python
from dataclasses import dataclass


@dataclass(slots=True)
class User:
    name: str
    age: int
```

Saves memory and speeds attribute access when you create very many instances (hundreds of thousands+).
Measure first. Prefer the dataclass flag over hand-written `__slots__`. Slots classes cannot gain new attributes
and need extra care with multiple inheritance.