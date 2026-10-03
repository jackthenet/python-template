# Python 3.15

3.15 was scheduled for release on 2026-10-01 (PEP 790). Verify the installed version before relying on it.

## Version gate (read first)

Use a 3.15-only feature **only if the project's `requires-python` is `>=3.15`** and CI runs on 3.15.
Several features below are new syntax or new built-ins that fail on 3.14 (`SyntaxError` or `NameError`).
If the project supports 3.14, use the 3.14-compatible form shown in each section. Also check that the
type checker and ruff version understand the feature (see Typing).

## New syntax

### Lazy imports (PEP 810)

```python
lazy import json
lazy from pathlib import Path
```

The module loads on first use, which shortens startup for CLIs that often exit early (for example `--help`).

- Module level only: not allowed inside functions, class bodies or `try` blocks.
- Moves the import cost, does not remove it. A program that uses everything pays the same total.
- A typo or missing module only fails at first use, not at startup. Do not lazily import modules whose import has needed side effects (registration, patching).
- Use it for heavy, rarely needed dependencies in CLI entry points, not as a blanket default.
- 3.14-compatible form: a normal `import`, or an import inside the function that needs it.

### Unpacking in comprehensions (PEP 798)

```python
flat = [*items for items in nested]            # instead of [x for xs in nested for x in xs]
merged = {**layer for layer in layers}          # later keys win, like `|`
total = sum(*items for items in nested)
```

The starred expression must be the whole element expression; `[*a, 0 for ...]` is a SyntaxError.
3.14-compatible form: `itertools.chain.from_iterable(nested)` or the double-`for` comprehension.

## New built-ins

### `frozendict` (PEP 814)

Immutable, hashable (if values are) mapping. Use it for constants and defaults instead of a mutable `dict` or `MappingProxyType`.

```python
DEFAULTS = frozendict({"theme": "light", "autosave": True})
custom = DEFAULTS | {"theme": "dark"}   # new frozendict
```

It is **not** a `dict` subclass: `isinstance(x, dict)` is False. Annotate parameters as `Mapping[str, T]`, not `dict`.
3.14-compatible form: `MappingProxyType` or a module constant that is never mutated.

### `sentinel`

Replaces the `object()` idiom for "no value passed" when `None` is a valid value. It prints readably, keeps identity when copied or pickled (define it at module level under the same name) and works in unions.

```python
MISSING = sentinel("MISSING")


def get_option(options: dict[str, object], name: str, default: object = MISSING) -> object:
    value = options.get(name, default)
    if value is MISSING:
        raise KeyError(name)
    return value
```

Compare with `is`, never `==`. 3.14-compatible form: `MISSING = object()`.

## Typing

- `typing.TypeForm[T]` (PEP 747): annotate functions that take a type expression such as `int | None` or `list[int]` and return that type (parsers, validators, DI containers). `type[T]` cannot describe those.
- `TypedDict(closed=True)` and `extra_items=str` (PEP 728): forbid extra keys, or allow extra keys with one value type.
- Tool support lags. Pyright supported these at the time of writing; mypy did not yet accept `extra_items`. Confirm your checker supports a feature before using it.

## Text, files and encodings (PEP 686)

UTF-8 is now the default encoding everywhere. **Still pass `encoding="utf-8"` explicitly** so the code behaves the same on 3.14.
Files an older program wrote under a legacy locale (for example `cp1252`) may now fail with `UnicodeDecodeError`; pass that encoding explicitly or convert the files once.

## Profiling (PEP 799)

Measure before optimizing. 3.15 adds a standard-library sampling profiler, Tachyon:

```bash
python -m profiling.sampling run script.py
```

Low overhead, so it can attach to running processes. `cProfile` is available as `profiling.tracing`; the pure-Python `profile` module is deprecated (removal in 3.17). On 3.14 and earlier use `py-spy`.

## Small additions worth using (3.15+)

| Instead of | Use |
|---|---|
| `re.match(p, s)` | `re.prefixmatch(p, s)` (`re.match` is soft-deprecated, never removed) |
| manual array hooks after `json.loads` | `json.loads(text, array_hook=tuple)` |
| `max(nan, x)` surprises | `math.fmax` / `math.fmin` (ignore NaN) |
| iterating a `TaskGroup` with workarounds to stop early | `TaskGroup.cancel()` |
| `len(text)` to count user-visible characters | `unicodedata.iter_graphemes(text)` |

`tomllib` now reads TOML 1.1 (trailing commas in inline tables).

## Behavior changes to watch when upgrading from 3.14

- `@contextmanager` applied to a generator function now keeps the context open while the generator runs (it used to close immediately).
- `sqlite3.connect()`: every argument except the path is keyword-only.
- `datetime.strptime("Feb 29", "%b %d")` (day without year) raises `ValueError`; include a year.
- `argparse`: `add_argument("-f", "-foo")` stores under `foo`, not `f`.
- Removed: `sre_compile`/`sre_constants`/`sre_parse`, the CGI handler in `http.server`, `platform.java_ver()`, keyword-argument `NamedTuple("P", x=int)` (use class syntax).
- Deprecated: `typing.ByteString` and `collections.abc.ByteString` (removal in 3.17), per-module `__version__` attributes, `import` lines in `.pth` files.
- The experimental JIT is faster but off by default (`PYTHON_JIT=1`). Measure before enabling it.

## Upgrade check

```bash
uv run --isolated --python 3.15 pytest -W error::DeprecationWarning
```

For production, wait until your compiled dependencies ship 3.15 wheels.