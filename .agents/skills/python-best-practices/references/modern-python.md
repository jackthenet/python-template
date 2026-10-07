# Modern Python: outdated vs. current

Models often reproduce older idioms from their training data. Use the current form (Python 3.14 baseline).
For features that exist only in 3.15 (`lazy import`, `frozendict`, `sentinel`, ...), see `python-3.15.md` and check `requires-python` first.
Ruff's `UP` rules catch some of these after the fact; write the right form the first time.

## Typing

| Outdated | Current |
|---|---|
| `Optional[str]`, `Union[int, str]` | `str \| None`, `int \| str` |
| `List[int]`, `Dict[str, int]`, `Tuple[int, ...]` | `list[int]`, `dict[str, int]`, `tuple[int, ...]` |
| `from typing import Callable, Iterator` | `from collections.abc import Callable, Iterator` |
| `T = TypeVar("T")` plus `Generic[T]` | `def first[T](items: Sequence[T]) -> T:` (PEP 695, 3.12+) |
| `Alias = dict[str, int]` for type aliases | `type Alias = dict[str, int]` |
| `-> "ClassName"` or `from __future__ import annotations` | plain annotations (deferred evaluation is the default on 3.14) |
| returning `"Self"` as a string | `from typing import Self` |
| overriding a method silently | `@override` (`from typing import override`) |

```python
from collections.abc import Sequence


def first[T](items: Sequence[T]) -> T:
    return items[0]


type UserMap = dict[int, str]
```

## Standard library

| Outdated | Current | Why |
|---|---|---|
| `datetime.utcnow()` | `datetime.now(UTC)` (`from datetime import UTC`) | `utcnow()` is deprecated and returns a naive datetime |
| `os.path.join(a, b)` | `Path(a) / b` | `pathlib` is clearer and portable |
| `open(path)` | `path.open(encoding="utf-8")` | explicit encoding avoids platform surprises |
| `class Color(str, Enum)` | `class Color(StrEnum)` | built in since 3.11 |
| `asyncio.get_event_loop()` | `asyncio.run(main())` and `asyncio.TaskGroup` | structured concurrency |
| `zip(a, b)` when lengths must match | `zip(a, b, strict=True)` | catches silent truncation |
| manual chunking loops | `itertools.batched(items, n)` (3.12+) | built in |
| `s[len(p):] if s.startswith(p) else s` | `s.removeprefix(p)` | clearer |
| third-party TOML parser for reading | `import tomllib` | built in since 3.11 |

```python
from datetime import UTC, datetime
from pathlib import Path

now = datetime.now(UTC)
text = Path("data.txt").read_text(encoding="utf-8")
```

## Pydantic v2 (not v1)

| v1 (do not use) | v2 |
|---|---|
| `@validator("x")` | `@field_validator("x")` with `@classmethod` |
| `@root_validator` | `@model_validator(mode="after")` |
| `obj.dict()` / `obj.json()` | `obj.model_dump()` / `obj.model_dump_json()` |
| `Model.parse_obj(data)` | `Model.model_validate(data)` |
| `class Config: ...` inside the model | `model_config = ConfigDict(...)` |

```python
from pydantic import BaseModel, ConfigDict, field_validator


class User(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, value: str) -> str:
        if not value:
            raise ValueError("name must not be empty")
        return value
```

## Libraries

- HTTP: `httpx`, not `requests` (async support, timeouts, one client for everything).
- JSON in hot paths: `orjson` (returns `bytes`, so use `.decode()` when you need `str`).
- YAML: `ruamel.yaml`, not `pyyaml`.
- Logging: the shared logging feature — `setup_logger()` once at startup, `get_logger()` for statements, `@logged` / `@logged_class` to trace calls — with keyword fields, not f-string messages and not `print`.