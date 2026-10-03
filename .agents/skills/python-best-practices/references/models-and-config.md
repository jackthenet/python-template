# Models and config

## Dynamic config: use a validated model, not `setattr`

Why: `setattr` loops hide attributes from the type checker and IDE, accept any key, and skip validation.

Avoid:
```python
class Config: ...

config = Config()
for key, value in data.items():
    setattr(config, key, value)
```

Prefer:
```python
from pydantic import BaseModel


class Config(BaseModel):
    host: str
    port: int = 5432


config = Config.model_validate(data)  # typed, validated, errors point at the bad field
```

When to use: any time data comes from outside the program (dict, JSON, YAML, env).
When not to: purely internal value objects with no validation need - use a dataclass.

## Internal value objects: dataclass

```python
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Point:
    x: float
    y: float
```

`frozen=True` makes it hashable and safe to share; `slots=True` is free and saves memory (see `performance.md`).

## Truly dynamic keys

If keys are genuinely unknown at write time, keep them in a `dict[str, T]` or `Mapping`, not as attributes. Use `getattr`/`setattr` only for plugin or reflection code, and say why in a comment.