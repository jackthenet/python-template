"""``@logged`` decorator for tracing function entry, exit, and elapsed time."""

from __future__ import annotations

import asyncio
import functools
import inspect
import time
from collections.abc import Callable, Mapping
from typing import Any, overload

from loguru import logger

from core.settings import Settings, get_settings

_LOGGED_MARKER_ATTR = "__nw_logged__"
_LOGGED_CLASS_MARKER_ATTR = "__nw_logged_class__"


def _log_call_end(
    qualname: str,
    elapsed_ms: float,
    level: str,
    slow_threshold_ms: float | None,
    slow_level: str,
    context_suffix: str = "",
    extra_depth: int = 0,
) -> None:
    """Emit the end-of-call log line, escalating to *slow_level* when the threshold is exceeded.

    CALL-DEPTH CONTRACT: must be called exactly one frame below a wrapper function.
    depth=2 baseline: [0] _log_call_end, [1] *_wrapper, [2] actual call site.
    Pass *extra_depth* when called from a deeper frame.
    """
    depth = 2 + extra_depth
    if slow_threshold_ms is not None and elapsed_ms >= slow_threshold_ms:
        logger.opt(depth=depth).log(
            slow_level, "<< {} completed in {:.1f} ms [SLOW]{}", qualname, elapsed_ms, context_suffix
        )
    else:
        logger.opt(depth=depth).log(level, "<< {} completed in {:.1f} ms{}", qualname, elapsed_ms, context_suffix)


def _log_exception(
    qualname: str,
    exc: BaseException,
    elapsed_ms: float,
    level: str,
    *,
    is_async: bool,
    context_suffix: str = "",
) -> None:
    """Emit the exception log line from inside a *_wrapper except block.

    CALL-DEPTH CONTRACT: must be called exactly one frame below an except block
    inside a *_wrapper function.
    depth=3: [0] _log_exception, [1] except block, [2] *_wrapper frame, [3] actual call site.
    """
    quiet = isinstance(exc, (KeyboardInterrupt, SystemExit))
    if is_async:
        quiet = quiet or isinstance(exc, asyncio.CancelledError)
    logger.opt(depth=3).log(
        "DEBUG" if quiet else level,
        "!! {} raised {} after {:.1f} ms{}",
        qualname,
        type(exc).__name__,
        elapsed_ms,
        context_suffix,
    )


def _truncate_detail(value: Any, *, limit: int = 96) -> str:
    text = repr(value)
    if len(text) <= limit:
        return text
    return f"{text[: limit - 3]}..."


def _format_context_suffix(
    *,
    context: Mapping[str, Any] | None,
    include_args: bool,
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> str:
    details: list[str] = []

    if context:
        for key, value in context.items():
            if value in (None, "", [], {}, ()):
                continue
            details.append(f"{key}={_truncate_detail(value)}")

    if include_args:
        if args:
            details.append(f"args={_truncate_detail(args)}")
        if kwargs:
            details.append(f"kwargs={_truncate_detail(kwargs)}")

    if not details:
        return ""
    return f" ({' '.join(details)})"


def _resolve_slow_threshold(*, slow_threshold_ms: float | None, slow_threshold_setting: str | None) -> float | None:
    if slow_threshold_ms is not None:
        return slow_threshold_ms if slow_threshold_ms > 0 else None
    if slow_threshold_setting is None:
        return None

    threshold = getattr(get_settings(), slow_threshold_setting)
    if isinstance(threshold, (int, float)):
        return float(threshold) if float(threshold) > 0 else None
    return None


def _resolve_include_args(include_args: bool | None) -> bool:
    if include_args is not None:
        return include_args
    return bool(get_settings().profiling_include_arguments)


def _resolve_call_context_suffix(
    *,
    include_args: bool | None,
    context_getter: Callable[..., Mapping[str, Any] | None] | None,
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> str:
    context = context_getter(*args, **kwargs) if context_getter is not None else None
    return _format_context_suffix(
        context=context,
        include_args=_resolve_include_args(include_args),
        args=args,
        kwargs=kwargs,
    )


def _wrap_async_logged[CallableT: Callable[..., Any]](
    func: CallableT,
    *,
    qualname: str,
    level: str,
    slow_threshold_ms: float | None,
    slow_threshold_setting: str | None,
    slow_level: str,
    include_args: bool | None,
    context_getter: Callable[..., Mapping[str, Any] | None] | None,
) -> CallableT:
    @functools.wraps(func)
    async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
        context_suffix = _resolve_call_context_suffix(
            include_args=include_args,
            context_getter=context_getter,
            args=args,
            kwargs=kwargs,
        )
        logger.opt(depth=1).log(level, ">> {}{}", qualname, context_suffix)
        t0 = time.perf_counter()
        try:
            result = await func(*args, **kwargs)
            elapsed = (time.perf_counter() - t0) * 1000
            _log_call_end(
                qualname,
                elapsed,
                level,
                _resolve_slow_threshold(
                    slow_threshold_ms=slow_threshold_ms,
                    slow_threshold_setting=slow_threshold_setting,
                ),
                slow_level,
                context_suffix,
            )
            return result
        except BaseException as exc:
            _log_exception(
                qualname,
                exc,
                (time.perf_counter() - t0) * 1000,
                level,
                is_async=True,
                context_suffix=context_suffix,
            )
            raise

    setattr(async_wrapper, _LOGGED_MARKER_ATTR, True)
    return async_wrapper  # type: ignore[return-value]


def _wrap_sync_logged[CallableT: Callable[..., Any]](
    func: CallableT,
    *,
    qualname: str,
    level: str,
    slow_threshold_ms: float | None,
    slow_threshold_setting: str | None,
    slow_level: str,
    include_args: bool | None,
    context_getter: Callable[..., Mapping[str, Any] | None] | None,
) -> CallableT:
    @functools.wraps(func)
    def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
        context_suffix = _resolve_call_context_suffix(
            include_args=include_args,
            context_getter=context_getter,
            args=args,
            kwargs=kwargs,
        )
        logger.opt(depth=1).log(level, ">> {}{}", qualname, context_suffix)
        t0 = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            elapsed = (time.perf_counter() - t0) * 1000
            _log_call_end(
                qualname,
                elapsed,
                level,
                _resolve_slow_threshold(
                    slow_threshold_ms=slow_threshold_ms,
                    slow_threshold_setting=slow_threshold_setting,
                ),
                slow_level,
                context_suffix,
            )
            return result
        except BaseException as exc:
            _log_exception(
                qualname,
                exc,
                (time.perf_counter() - t0) * 1000,
                level,
                is_async=False,
                context_suffix=context_suffix,
            )
            raise

    setattr(sync_wrapper, _LOGGED_MARKER_ATTR, True)
    return sync_wrapper  # type: ignore[return-value]


@overload
def logged_class[ClassT: type](_cls: ClassT) -> ClassT: ...


@overload
def logged_class[ClassT: type](
    _cls: None = None,
    *,
    level: str = ...,
    slow_threshold_ms: float | None = ...,
    slow_threshold_setting: str | None = ...,
    slow_level: str = ...,
    include_args: bool | None = ...,
    context_getter: Callable[..., Mapping[str, Any] | None] | None = ...,
    include_init: bool = ...,
) -> Callable[[ClassT], ClassT]: ...


def logged_class[ClassT: type](
    _cls: ClassT | None = None,
    *,
    level: str = "DEBUG",
    slow_threshold_ms: float | None = None,
    slow_threshold_setting: str | None = None,
    slow_level: str = "WARNING",
    include_args: bool | None = None,
    context_getter: Callable[..., Mapping[str, Any] | None] | None = None,
    include_init: bool = False,
) -> ClassT | Callable[[ClassT], ClassT]:
    """Decorate public class methods so service classes emit entry/exit timing logs."""

    def decorator(cls: ClassT) -> ClassT:
        if getattr(cls, _LOGGED_CLASS_MARKER_ATTR, False):
            return cls

        for name, value in vars(cls).items():
            if name.startswith("_") and not (include_init and name == "__init__"):
                continue
            if isinstance(value, property):
                continue

            descriptor_type: type[staticmethod] | type[classmethod] | None = None
            func: Callable[..., Any] | None = None

            if isinstance(value, staticmethod):
                descriptor_type = staticmethod
                func = value.__func__
            elif isinstance(value, classmethod):
                descriptor_type = classmethod
                func = value.__func__
            elif callable(value):
                func = value

            if func is None or getattr(func, _LOGGED_MARKER_ATTR, False):
                continue

            wrapped = logged(
                level=level,
                slow_threshold_ms=slow_threshold_ms,
                slow_threshold_setting=slow_threshold_setting,
                slow_level=slow_level,
                include_args=include_args,
                context_getter=context_getter,
            )(func)

            if descriptor_type is None:
                setattr(cls, name, wrapped)
            else:
                setattr(cls, name, descriptor_type(wrapped))

        setattr(cls, _LOGGED_CLASS_MARKER_ATTR, True)
        return cls

    if _cls is not None:
        return decorator(_cls)
    return decorator


@overload
def logged[CallableT: Callable[..., Any]](_func: CallableT) -> CallableT: ...


@overload
def logged[CallableT: Callable[..., Any]](
    _func: None = None,
    *,
    level: str = ...,
    slow_threshold_ms: float | None = ...,
    slow_threshold_setting: str | None = ...,
    slow_level: str = ...,
    include_args: bool | None = ...,
    context_getter: Callable[..., Mapping[str, Any] | None] | None = ...,
) -> Callable[[CallableT], CallableT]: ...


def logged[CallableT: Callable[..., Any]](
    _func: CallableT | None = None,
    *,
    level: str = "DEBUG",
    slow_threshold_ms: float | None = None,
    slow_threshold_setting: str | None = None,
    slow_level: str = "WARNING",
    include_args: bool | None = None,
    context_getter: Callable[..., Mapping[str, Any] | None] | None = None,
) -> CallableT | Callable[[CallableT], CallableT]:
    """Decorator that logs function entry, exit, and elapsed time in milliseconds.

    Usable with or without arguments::

        @logged
        def save(): ...

        @logged(level="INFO", slow_threshold_ms=500)
        async def generate(): ...

    ``asyncio.CancelledError``, ``KeyboardInterrupt``, and ``SystemExit`` are
    logged at DEBUG then re-raised.  All other exceptions are logged at *level*
    then re-raised.

    Args:
        level: Loguru level name for start/end messages.  Default ``"DEBUG"``.
        slow_threshold_ms: When set, calls exceeding this many milliseconds are
            re-logged at *slow_level*.
        slow_threshold_setting: Name of a ``Settings`` field containing the
            slow-call threshold in milliseconds. Used when *slow_threshold_ms*
            is not provided.
        slow_level: Loguru level name used for slow-call messages.  Default
            ``"WARNING"``.
        include_args: When ``True``, include positional and keyword arguments
            in profiling messages. When ``None``, follows
            ``Settings.profiling_include_arguments``.
        context_getter: Optional callable receiving the same ``*args`` and
            ``**kwargs`` as the wrapped function and returning structured
            context to include in timing logs.

    Raises:
        ValueError: If *level* or *slow_level* is not a known loguru level name.
    """
    for lv, param in ((level, "level"), (slow_level, "slow_level")):
        try:
            logger.level(lv)
        except ValueError as exc:
            raise ValueError(f"@logged: invalid {param}={lv!r}") from exc

    if slow_threshold_setting is not None and slow_threshold_setting not in Settings.model_fields:
        raise ValueError(f"@logged: unknown slow_threshold_setting={slow_threshold_setting!r}")

    def decorator(func: CallableT) -> CallableT:
        qualname = func.__qualname__
        if inspect.iscoroutinefunction(func):
            return _wrap_async_logged(
                func,
                qualname=qualname,
                level=level,
                slow_threshold_ms=slow_threshold_ms,
                slow_threshold_setting=slow_threshold_setting,
                slow_level=slow_level,
                include_args=include_args,
                context_getter=context_getter,
            )

        return _wrap_sync_logged(
            func,
            qualname=qualname,
            level=level,
            slow_threshold_ms=slow_threshold_ms,
            slow_threshold_setting=slow_threshold_setting,
            slow_level=slow_level,
            include_args=include_args,
            context_getter=context_getter,
        )

    if _func is not None:
        return decorator(_func)
    return decorator  # type: ignore[return-value]
