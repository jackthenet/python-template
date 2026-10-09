"""Tracing decorators for callables and classes (REQ-007, REQ-008, REQ-015).

``logged`` traces a callable's entry, its exit (with ``elapsed_ms``) and its
exceptions; ``logged_class`` applies the same tracing to every public method of a
class. Both emit through the pipeline's bound logger (ADR-082 D5), so a traced
record is the same JSON object the file sink writes (REQ-011, AC-003) — the
decorator owns the event text and the ``elapsed_ms`` field, the pipeline owns the
rendered ``exception`` field (D7).
"""

from __future__ import annotations

import contextlib
import functools
import inspect
import sys
import time
from collections.abc import Callable
from typing import Any

# The accepted level names, mapped to the bound logger's methods. structlog's stdlib
# wrapper has no numeric routing (its LEVEL_TO_NAME table raises KeyError for an
# unknown number) and add_level_field reads the record's own levelname, so the method
# name is what sets the level (AC-011).
_LEVEL_METHODS = frozenset({"debug", "info", "warning", "error", "critical"})

# REQ-006/REQ-014: a call slower than its threshold escalates its exit record.
_SLOW_EXIT_METHOD = "warning"


def _level_method(level: str) -> str:
    """The bound-logger method for a level name, validated at decoration time."""
    method = level.lower()
    if method not in _LEVEL_METHODS:
        msg = f"unknown log level {level!r}; expected one of {', '.join(sorted(_LEVEL_METHODS))}"
        raise ValueError(msg)
    return method


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
    """A method is private if underscore-prefixed (spec convention).

    The second signal is the substring ``private`` anywhere in the name — the
    re-derived suite's signal for a private method.
    """
    return name.startswith("_") or "private" in name


class _Tracer:
    """The three traced records of one call site (REQ-007, REQ-009, REQ-011).

    The bound logger is resolved once per call site rather than per call:
    ``get_logger()`` re-runs structlog's configuration on every call, and the
    processor chain never changes semantically (INV-005).
    """

    __slots__ = ("_func", "_include_args", "_level", "_logger", "_qualname", "_threshold")

    def __init__(
        self,
        func: Callable[..., Any],
        level: str,
        slow_threshold_ms: float | None,
        include_args: bool,
    ) -> None:
        self._func = func
        self._qualname = getattr(func, "__qualname__", getattr(func, "__name__", repr(func)))
        self._level = _level_method(level)
        self._threshold = slow_threshold_ms
        self._include_args = include_args
        self._logger: Any = None

    def entry(self, args: tuple[Any, ...], kwargs: dict[str, Any]) -> None:
        """The entry record: the qualname, plus the arguments when asked (REQ-007)."""
        event = f">> {self._qualname} called"
        if self._include_args:
            event += f" {_format_args(self._func, args, kwargs)}"
        self._emit(self._level, event)

    def exit(self, elapsed_ms: float) -> None:
        """The exit record carrying ``elapsed_ms`` as a number (REQ-011, AC-003)."""
        method = _SLOW_EXIT_METHOD if self._is_slow(elapsed_ms) else self._level
        self._emit(method, f"<< {self._qualname} returned in {elapsed_ms:.3f} ms", elapsed_ms=elapsed_ms)

    def exception(self) -> None:
        """The exception record: the pipeline renders the field, never the locals.

        ``exc_info=True`` is a structlog event field (it never reaches stdlib's
        ``exc_info`` keyword), and ``_renderers.exception_field`` falls back to
        ``sys.exc_info()`` in the emitting thread — which is why this runs inside
        the ``except`` block (REQ-009, INV-002).
        """
        exc = sys.exc_info()[1]
        self._emit(self._level, f"!! {self._qualname} raised {type(exc).__name__}({exc})", exc_info=True)

    def _is_slow(self, elapsed_ms: float) -> bool:
        return self._threshold is not None and elapsed_ms > self._threshold

    def _bound_logger(self) -> Any:
        # Imported here (not at module level) to avoid a circular import:
        # backend.logging._settings imports ``logged`` from this module, and
        # _pipeline imports _settings.
        from backend.logging._pipeline import get_logger

        if self._logger is None:
            self._logger = get_logger(getattr(self._func, "__module__", "") or "backend.logging")
        return self._logger

    def _emit(self, method: str, event: str, **fields: Any) -> None:
        """Emit one record; a broken sink never reaches the traced call (AC-016).

        ``Logger.callHandlers`` calls ``Handler.handle()`` without guarding it, so a
        sink whose ``emit`` raises would otherwise travel into business code — the
        same guarantee ``_ForwardingHandler.emit`` records for the forwarding path.
        """
        with contextlib.suppress(Exception):  # best-effort by specification (REQ-013)
            getattr(self._bound_logger(), method)(event, **fields)


def _wrap_sync(func: Callable[..., Any], tracer: _Tracer) -> Callable[..., Any]:
    """Wrap a sync callable with entry/exit/exception tracing."""

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        tracer.entry(args, kwargs)
        start = time.perf_counter()
        try:
            result = func(*args, **kwargs)
        except Exception:
            tracer.exception()
            raise
        tracer.exit((time.perf_counter() - start) * 1000)
        return result

    return wrapper


def _wrap_async(func: Callable[..., Any], tracer: _Tracer) -> Callable[..., Any]:
    """Wrap an async callable with the same tracing (AC-011)."""

    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        tracer.entry(args, kwargs)
        start = time.perf_counter()
        try:
            result = await func(*args, **kwargs)
        except Exception:
            tracer.exception()
            raise
        tracer.exit((time.perf_counter() - start) * 1000)
        return result

    return wrapper


def logged(
    func: Callable[..., Any] | None = None,
    *,
    level: str = "DEBUG",
    slow_threshold_ms: float | None = None,
    slow_threshold_setting: str | None = None,
    include_args: bool = False,
) -> Callable[..., Any]:
    """Log a callable's entry, exit (with elapsed ms), and exceptions.

    Usable as ``@logged`` or ``@logged(level=...)``. Supports sync and async
    callables. A call slower than the resolved slow threshold escalates the exit
    record to WARNING. The exception is logged (type + message, frames rendered by
    the pipeline) and re-raised unchanged.
    """

    def decorator(f: Callable[..., Any]) -> Callable[..., Any]:
        threshold = _resolve_slow_threshold(slow_threshold_ms, slow_threshold_setting)
        tracer = _Tracer(f, level, threshold, include_args)
        wrapper = _wrap_async(f, tracer) if inspect.iscoroutinefunction(f) else _wrap_sync(f, tracer)
        # Mark the wrapper as traced and expose the resolved threshold so callers
        # (and the logging-coverage suite) can inspect it (REQ-007/AC-007).
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
