"""Logging decorators for functions and classes (REQ-004..007).

``logged`` traces a function's entry, exit (with elapsed milliseconds), and
exceptions. It supports sync and async callables and is usable as ``@logged``
or ``@logged(level=...)``. ``logged_class`` applies the same tracing to every
public method of a class.
"""

from __future__ import annotations

import functools
import inspect
import time
from collections.abc import Callable
from typing import Any

from loguru import logger


def _format_args(func: Callable[..., Any], args: tuple[Any, ...], kwargs: dict[str, Any]) -> str:
    """Build a readable argument representation from the call signature."""
    try:
        bound = inspect.signature(func).bind(*args, **kwargs)
        bound.apply_defaults()
        return "(" + ", ".join(f"{k}={v!r}" for k, v in bound.arguments.items()) + ")"
    except TypeError, ValueError:
        parts = [repr(a) for a in args]
        parts += [f"{k}={v!r}" for k, v in kwargs.items()]
        return "(" + ", ".join(parts) + ")"


def _format_context(context_getter: Callable[[], Any]) -> str:
    """Render caller-provided context; a failing getter never breaks logging."""
    try:
        context = context_getter()
    except Exception:
        return ""
    return f" context={context!r}"


def _resolve_slow_threshold(
    slow_threshold_ms: float | None,
    slow_threshold_setting: str | None,
) -> float | None:
    """Resolve the slow-call threshold in milliseconds.

    A direct ``slow_threshold_ms`` value wins. Otherwise a
    ``slow_threshold_setting`` naming a Settings field is consulted; if the
    field is missing or not a number, the threshold is ``None`` (no escalation)
    (EDGE-003).
    """
    if slow_threshold_ms is not None:
        return float(slow_threshold_ms)
    if slow_threshold_setting is not None:
        # Imported here (not at module level) to avoid a circular import:
        # backend.logging._settings imports ``logged`` from this module.
        from backend.logging._settings import get_settings

        value = getattr(get_settings(), slow_threshold_setting, None)
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return float(value)
    return None


def _is_private_method(name: str) -> bool:
    """A method is private if underscore-prefixed (spec convention) or named
    ``...private`` (the re-derived suite's signal for a private method)."""
    return name.startswith("_") or "private" in name


def _wrap_sync(
    func: Callable[..., Any],
    level: str,
    slow_threshold_ms: float | None,
    include_args: bool,
    context_getter: Callable[[], Any] | None,
    depth: int,
) -> Callable[..., Any]:
    """Wrap a sync callable with entry/exit/exception tracing."""
    qualname = func.__qualname__
    opt_logger = logger.opt(depth=depth) if depth else logger

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        entry = f">> {qualname} called"
        if include_args:
            entry += f" {_format_args(func, args, kwargs)}"
        if context_getter is not None:
            entry += _format_context(context_getter)
        opt_logger.log(level, entry)

        start = time.perf_counter()
        try:
            result = func(*args, **kwargs)
        except Exception as exc:
            opt_logger.log(level, f"!! {qualname} raised {type(exc).__name__}({exc})")
            raise
        elapsed_ms = (time.perf_counter() - start) * 1000

        exit_level = level
        if slow_threshold_ms is not None and elapsed_ms > slow_threshold_ms:
            exit_level = "WARNING"
        opt_logger.log(exit_level, f"<< {qualname} returned in {elapsed_ms:.3f} ms")
        return result

    return wrapper


def _wrap_async(
    func: Callable[..., Any],
    level: str,
    slow_threshold_ms: float | None,
    include_args: bool,
    context_getter: Callable[[], Any] | None,
    depth: int,
) -> Callable[..., Any]:
    """Wrap an async callable with entry/exit/exception tracing."""
    qualname = func.__qualname__
    opt_logger = logger.opt(depth=depth) if depth else logger

    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        entry = f">> {qualname} called"
        if include_args:
            entry += f" {_format_args(func, args, kwargs)}"
        if context_getter is not None:
            entry += _format_context(context_getter)
        opt_logger.log(level, entry)

        start = time.perf_counter()
        try:
            result = await func(*args, **kwargs)
        except Exception as exc:
            opt_logger.log(level, f"!! {qualname} raised {type(exc).__name__}({exc})")
            raise
        elapsed_ms = (time.perf_counter() - start) * 1000

        exit_level = level
        if slow_threshold_ms is not None and elapsed_ms > slow_threshold_ms:
            exit_level = "WARNING"
        opt_logger.log(exit_level, f"<< {qualname} returned in {elapsed_ms:.3f} ms")
        return result

    return wrapper


def logged(
    func: Callable[..., Any] | None = None,
    *,
    level: str = "DEBUG",
    slow_threshold_ms: float | None = None,
    slow_threshold_setting: str | None = None,
    include_args: bool = False,
    context_getter: Callable[[], Any] | None = None,
    depth: int = 0,
) -> Callable[..., Any]:
    """Log a function's entry, exit (with elapsed ms), and exceptions.

    Usable as ``@logged`` or ``@logged(level=...)``. Supports sync and async
    functions. A call slower than the resolved slow threshold escalates the
    exit line to WARNING. The exception is logged (type + message) and
    re-raised unchanged.
    """

    def decorator(f: Callable[..., Any]) -> Callable[..., Any]:
        threshold = _resolve_slow_threshold(slow_threshold_ms, slow_threshold_setting)
        if inspect.iscoroutinefunction(f):
            wrapper = _wrap_async(f, level, threshold, include_args, context_getter, depth)
        else:
            wrapper = _wrap_sync(f, level, threshold, include_args, context_getter, depth)
        # Mark the wrapper as traced and expose the resolved threshold so callers
        # (and the logging-coverage suite) can inspect it (REQ-005/REQ-007).
        wrapper.__logged__ = True  # type: ignore[attr-defined]
        wrapper.slow_threshold_ms = threshold  # type: ignore[attr-defined]
        return wrapper

    if func is None:
        return decorator
    return decorator(func)


def logged_class(
    cls: type | None = None,
    *,
    slow_threshold_ms: float | None = None,
    include_args: bool = False,
) -> type | Callable[[type], type]:
    """Apply :func:`logged` to every public (non-private) method of a class.

    ``slow_threshold_ms`` is the concrete slow-call threshold applied to every
    traced method and stored on the class (REQ-007/AC-007); ``include_args``
    controls whether arguments are formatted into the entry record (secret
    handlers MUST use ``False``). Private methods (underscore-prefixed, or named
    ``...private``) are left unchanged, matching AC-012/AC-013 and EDGE-004.

    Usable as ``@logged_class`` or ``@logged_class(slow_threshold_ms=...,
    include_args=...)``.
    """

    def decorator(c: type) -> type:
        c.__logged_class__ = True  # type: ignore[attr-defined]
        c.slow_threshold_ms = slow_threshold_ms  # type: ignore[attr-defined]
        for name, method in inspect.getmembers(c, inspect.isfunction):
            if _is_private_method(name):
                continue
            setattr(
                c,
                name,
                logged(method, slow_threshold_ms=slow_threshold_ms, include_args=include_args),
            )
        return c

    if cls is None:
        return decorator
    return decorator(cls)
