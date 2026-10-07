---
name: python-best-practices
description: Conventions and vetted good-code examples for writing, reviewing or refactoring Python. Use this skill whenever the user asks for Python code - new modules, services, config or data models, tests, project structure, Python 3.15 features or upgrades, file or stream processing, error handling, logging, context managers, caching, or performance tuning - and when reviewing, modernizing or cleaning up existing Python, even if they do not mention "best practices".
---

# Python best practices

Write modern, typed, boring Python. Clarity first; optimize only after measuring.

## Core rules

- Target the version in the project's `requires-python` (baseline 3.14). Use 3.15-only features only when it says `>=3.15`.
- Full type hints on every signature, no `Any` unless unavoidable.
- Validate external data (config, API payloads, files) with Pydantic at the boundary.
- Use `pathlib.Path` instead of `os.path`, `httpx` instead of `requests`, `orjson` for hot JSON paths.
- Log through the shared logging feature instead of `print`: `setup_logger()` once at startup, `get_logger()` for one-off statements, `@logged` / `@logged_class` to trace calls (`from backend.logging import ...`) — never import a logging backend directly.
- Catch specific exceptions; never use a bare `except:`; never swallow errors silently.
- No mutable default arguments; no new dependencies without asking.
- Prefer the standard library tool (`functools.cache`, `dataclass(slots=True)`, `contextlib`) over hand-rolled versions.
- Do not duplicate what tooling enforces. Ruff and the type checker catch style and typing issues; spend effort on design.

## References

Read only the file that matches the task:

| Task | File |
|---|---|
| Project targets Python 3.15 (lazy imports, `frozendict`, `sentinel`, comprehension unpacking, upgrade notes) | `references/python-3.15.md` |
| Any new code: check for outdated typing, stdlib, Pydantic v1 or library idioms | `references/modern-python.md` |
| Where new code goes, feature folders, imports between features | `references/structure.md` |
| Writing or changing tests, test data, mocking HTTP or time | `references/testing.md` |
| Config objects, data models, dynamic attributes | `references/models-and-config.md` |
| try/except, multiple exceptions, resource handling, timers | `references/errors-and-resources.md` |
| Caching, lookups, large files, dispatch, memory | `references/performance.md` (apply only after measuring) |

## Verify before finishing

Run, and fix anything that fails:

```bash
ruff check --fix && ruff format
ty check   # or: mypy --strict
pytest
```

If a rule in a reference conflicts with the project's existing conventions, follow the project and mention the difference.