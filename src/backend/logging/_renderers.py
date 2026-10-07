"""Renderers and record-field processors for the logging pipeline (ADR-082).

Every record — feature, foreign or third-party — is rendered from the same field
set, and the JSON renderer is the only place a record is serialized with orjson.
This module must never import ``backend.logging._pipeline``: the pipeline imports
this one, and a cycle back fails while ``_pipeline`` is still initializing.
"""

from __future__ import annotations

import linecache
import sys
import traceback
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

import orjson
from structlog.processors import CallsiteParameter, CallsiteParameterAdder

#: The fields every rendered record carries, in the order both renderers emit them.
RENDERED_FIELD_ORDER: tuple[str, ...] = (
    "level",
    "logger",
    "event",
    "timestamp",
    "file",
    "line",
)

#: Pipeline bookkeeping keys that must never reach a rendered record. The callsite
#: parameters are renamed to ``file``/``line`` before rendering, so their structlog
#: names are bookkeeping too.
INTERNAL_FIELDS: frozenset[str] = frozenset({"filename", "lineno", "exc_info", "stack_info", "positional_args"})

#: The bookkeeping keys ``ProcessorFormatter`` injects into the event dict.
PROCESSOR_META_FIELDS: frozenset[str] = frozenset({"_record", "_from_structlog"})

#: Everything the render chain strips out of a record before it is rendered.
_DROPPED_FIELDS: frozenset[str] = PROCESSOR_META_FIELDS | INTERNAL_FIELDS

TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%SZ"  # ISO-8601 UTC (spec §3)

#: The event-dict key that carries a feature's own logger name (REQ-005). Defined
#: here because the pipeline module imports this one, never the other way round.
LOGGER_NAME_FIELD = "logger_name"

LEVEL_COLORS: dict[str, str] = {
    "debug": "\033[36m",
    "info": "\033[32m",
    "warning": "\033[33m",
    "error": "\033[31m",
    "critical": "\033[41;97m",
}
_COLOR_RESET = "\033[0m"


def callsite_adder() -> CallsiteParameterAdder:
    """Capture the emitting callsite as ``filename``/``lineno``.

    The pipeline reads the callsite in the emitting thread (the processor chain
    runs there), never in the listener thread, and skips the logging feature's own
    frames so a traced call reports its caller, not the decorator (ADR-082).
    """
    return CallsiteParameterAdder(
        parameters={CallsiteParameter.FILENAME, CallsiteParameter.LINENO},
        additional_ignores=["backend.logging"],
    )


def add_level_field(
    logger: Any,  # structlog passes its logger wrapper
    method_name: str,
    event_dict: dict[str, Any],
) -> dict[str, Any]:
    """Set ``level`` from the record's own level name.

    The structlog method name is not authoritative: ``log.exception()`` would label
    the record ``exception``, while ``levelname`` is ERROR — and an unknown numeric
    level renders as ``Level 47`` (EDGE-004).
    """
    record = event_dict.get("_record")
    event_dict["level"] = getattr(record, "levelname", None) or method_name.upper()
    return event_dict


def add_logger_field(
    logger: Any,  # structlog passes its logger wrapper
    method_name: str,
    event_dict: dict[str, Any],
) -> dict[str, Any]:
    """Set the ``logger`` field to the emitting logger's own name.

    A feature's name travels in ``LOGGER_NAME_FIELD``; a foreign record keeps the
    third-party logger's name, and the pipeline logger's name is never substituted.
    """
    record = event_dict.get("_record")
    name = event_dict.pop(LOGGER_NAME_FIELD, None)
    if name is None and record is not None:
        name = record.name
    event_dict["logger"] = name
    return event_dict


def add_timestamp(
    logger: Any,  # unused structlog parameter
    method_name: str,
    event_dict: dict[str, Any],
) -> dict[str, Any]:
    """Stamp the record at render time (the queue keeps the emitting order)."""
    event_dict["timestamp"] = datetime.now(tz=UTC).strftime(TIMESTAMP_FORMAT)
    return event_dict


def rename_callsite_fields(
    logger: Any,  # unused structlog parameter
    method_name: str,
    event_dict: dict[str, Any],
) -> dict[str, Any]:
    """Rename the callsite parameters to the specified ``file``/``line`` fields."""
    event_dict["file"] = event_dict.pop("filename", None)
    event_dict["line"] = event_dict.pop("lineno", None)
    return event_dict


def exception_field(
    logger: Any,  # unused structlog parameter
    method_name: str,
    event_dict: dict[str, Any],
) -> dict[str, Any]:
    """Render an active exception into the ``exception`` field, never its locals.

    Foreign records carry the exception on their ``LogRecord``; structlog records
    carry it there too once stdlib resolved ``exc_info`` at the call site.
    """
    record = event_dict.get("_record")
    exc_info = getattr(record, "exc_info", None) or event_dict.get("exc_info")
    if exc_info is True:  # structlog's exception() marks it without carrying the tuple
        exc_info = sys.exc_info()
    if exc_info and exc_info[0] is not None:
        event_dict["exception"] = _exception_content(exc_info)  # type: ignore[arg-type]
    return event_dict


def drop_pipeline_internals(
    logger: Any,  # unused structlog parameter
    method_name: str,
    event_dict: dict[str, Any],
) -> dict[str, Any]:
    """Drop structlog's formatter bookkeeping and the pipeline's own key names."""
    for key in _DROPPED_FIELDS:
        event_dict.pop(key, None)
    return event_dict


def _exception_content(
    exc_info: tuple[type[BaseException], BaseException, Any],
) -> dict[str, Any]:
    """The exception type, message and traceback frames — no local values."""
    kind, value, tb = exc_info
    return {
        "type": kind.__qualname__,
        "message": str(value),
        "frames": _traceback_frames(tb),
    }


def _traceback_frames(tb: Any) -> list[dict[str, Any]]:
    """The traceback as file/line/function/source lines.

    Only the source *text* of each frame is read (``linecache``), never the frame's
    locals: an exception record must stay explainable without leaking local values
    (REQ-009, INV-002).
    """
    frames: list[dict[str, Any]] = []
    for frame, lineno in traceback.walk_tb(tb):
        code = frame.f_code
        frames.append(
            {
                "file": code.co_filename,
                "line": lineno,
                "function": code.co_name,
                "source": linecache.getline(code.co_filename, lineno).rstrip(),
            }
        )
    return frames


def _ordered(event_dict: dict[str, Any]) -> dict[str, Any]:
    """Put the canonical fields first, then the feature's own fields."""
    ordered = {field: event_dict[field] for field in RENDERED_FIELD_ORDER if field in event_dict}
    rest = {key: value for key, value in event_dict.items() if key not in ordered}
    return {**ordered, **rest}


def _orjson_default(value: Any) -> Any:
    """Serialize anything a feature bound into a record without losing the record."""
    if isinstance(value, (set, frozenset)):
        return sorted(value, key=str)
    if isinstance(value, BaseException):
        return {"type": type(value).__qualname__, "message": str(value)}
    return repr(value)


def render_json(
    logger: Any,  # unused structlog parameter
    method_name: str,
    event_dict: dict[str, Any],
    **_: Any,
) -> str:
    """Render one JSON object per line with orjson (ADR-082)."""
    text = orjson.dumps(_ordered(event_dict), default=_orjson_default, option=orjson.OPT_NON_STR_KEYS)
    return text.decode("utf-8")


@dataclass(frozen=True)
class TextRenderer:
    """Human-readable console rendering; the JSON file sink never uses it."""

    color: bool = False

    def __call__(
        self,
        logger: Any,  # unused structlog parameter
        method_name: str,
        event_dict: dict[str, Any],
        **_: Any,
    ) -> str:
        fields = _ordered(event_dict)
        level = str(fields.get("level", ""))
        # ``level`` is the record's ``levelname`` (uppercase); the map is keyed lowercase.
        shown_level = self._colorize(level, LEVEL_COLORS.get(level.lower(), ""))
        head = f"{fields.get('timestamp', '')} [{shown_level:<8}] {fields.get('event', '')} ({fields.get('logger', '')}"
        if fields.get("file") is not None:
            head += f":{fields.get('line')}"
        head += ")"
        parts = [head]
        parts.extend(
            f"  {key}={_display(value)}"
            for key, value in fields.items()
            if key not in RENDERED_FIELD_ORDER and key != "exception"
        )
        if "exception" in fields:
            parts.append(_display_exception(fields["exception"]))
        return "\n".join(parts)

    def _colorize(self, text: str, color: str) -> str:
        if not color or not self.color:
            return text
        return f"{color}{text}{_COLOR_RESET}"


def color_for_tty(stream: Any) -> bool:
    """Colorize only when the console sink really is an interactive terminal."""
    isatty = getattr(stream, "isatty", None)
    try:
        return bool(isatty()) if callable(isatty) else False
    except ValueError:  # a closed stream (e.g. after interpreter shutdown)
        return False


def _display(value: Any) -> str:
    return repr(value) if isinstance(value, str) else str(value)


def _display_exception(exception: dict[str, Any]) -> str:
    lines = [f"  exception: {exception['type']}: {exception['message']}"]
    lines.extend(f"    {frame['file']}:{frame['line']} in {frame['function']}" for frame in exception["frames"])
    return "\n".join(lines)
