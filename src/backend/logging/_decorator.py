"""Logging decorators for functions and classes."""

from __future__ import annotations

import functools
import inspect
from typing import Any, Callable, TypeVar

import loguru

F = TypeVar("F", bound=Callable[..., Any])


def _format_args(func: Callable[..., Any], args: tuple, kwargs: dict) -> str:
    """Build a readable argument string from the call signature."""
    try:
        bound = inspect.signature(func).bind(*args, **kwargs)
        bound.apply_defaults()
        return ", ".join(f"{k}={v!r}" for k, v in bound.arguments.items())
    except (TypeError, ValueError):
        return ", ".join(repr(a) for a in args) + (
            (", " + ", ".join(f"{k}={v!r}" for k, v in kwargs.items())) if kwargs else ""
        )


def logged(func: F | None = None, *, level: str = "INFO") -> Any:
    """Log function calls, return values, and exceptions.

    Usable as @logged or @logged(level="DEBUG").
    """

    def decorator(f: F) -> F:
        @functools.wraps(f)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            arg_str = _format_args(f, args, kwargs)
            loguru.logger.log(level, "{} called: {}", f.__qualname__, arg_str)
            try:
                result = f(*args, **kwargs)
                loguru.logger.log(level, "{} returned: {}", f.__qualname__, result)
                return result
            except Exception as exc:
                loguru.logger.opt(exception=exc).log(level, "{} raised: {}", f.__qualname__, exc)
                raise

        return wrapper  # type: ignore[return-value]

    if func is None:
        return decorator
    return decorator(func)


def logged_class(cls: type) -> type:
    """Log method calls, return values, and exceptions on a class."""
    for name, method in inspect.getmembers(cls, inspect.isfunction):
        if name.startswith("_"):
            continue
        setattr(cls, name, logged(method))
    return cls
