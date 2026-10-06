"""The logging pipeline: stdlib handlers, structlog processors, orjson rendering (ADR-082).

Ownership model (ADR-082 D1): a dedicated, non-propagating logger owns exactly two
managed sinks — a console stream handler and a queue-fed rotating file handler —
and one handler on the root logger forwards foreign records to those same sinks
(D2) instead of re-emitting them. Reconfiguration mutates the managed handlers in
place, so the process never grows a second file handler.
"""

from __future__ import annotations

import contextlib
import logging
import logging.handlers
import queue
import sys
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, cast

import structlog
from structlog.stdlib import BoundLogger, ProcessorFormatter

from backend.logging._decorator import logged
from backend.logging._renderers import (
    LOGGER_NAME_FIELD,
    TextRenderer,
    add_level_field,
    add_logger_field,
    add_timestamp,
    callsite_adder,
    color_for_tty,
    drop_pipeline_internals,
    exception_field,
    rename_callsite_fields,
    render_json,
)
from backend.logging._settings import Settings, get_settings

PIPELINE_LOGGER_NAME = "backend.logging"

RendererName = Literal["text", "json"]
RENDERERS: tuple[RendererName, ...] = ("text", "json")

# The slow-call threshold for the setup call itself: NFR-001's budget, so a setup that
# stops being fast is visible as a WARNING exit record (REQ-007/AC-007).
_SETUP_SLOW_THRESHOLD_MS = 25.0

# The setup call is traced at INFO, not at the decorator default DEBUG: the pipeline's own
# lifecycle record ("logging configured") is INFO (spec §9), and a DEBUG setup trace would
# be filtered at the default level, so the entry/exit of setup would never be observable
# (AC-005 requires records for the traced ``setup_logger`` module function).
_SETUP_TRACE_LEVEL = "INFO"

# The chains that produce the specified record fields. The callsite and the
# exception are captured where they still exist: the structlog chain runs in the
# emitting thread, and the foreign pre-chain runs before the formatter clears the
# record's exception. The render chain (ProcessorFormatter.processors) runs on the
# listener thread and only assembles and renders.
_EMITTING_CHAIN: tuple[Any, ...] = (callsite_adder(), exception_field)
_RENDER_CHAIN: tuple[Any, ...] = (
    add_level_field,
    add_logger_field,
    rename_callsite_fields,
    drop_pipeline_internals,
    add_timestamp,
)


@dataclass
class PipelineSinks:
    """The two managed sinks plus the root forwarder and the listener that feeds them."""

    console: logging.StreamHandler
    queue: logging.handlers.QueueHandler
    rotating: logging.handlers.RotatingFileHandler
    forwarding: logging.Handler
    listener: logging.handlers.QueueListener
    renderer: RendererName | None
    log_file: Path

    def managed(self) -> tuple[logging.Handler, ...]:
        """The handlers a foreign record is forwarded to."""
        return (self.console, self.queue)


# The installed pipeline, or None before setup_logger() has run (the module-singleton
# pattern the other features use, so no global rebinding is needed).
_sinks: list[PipelineSinks | None] = [None]
_subscribed: list[bool] = [False]
_setup_lock = threading.Lock()


# Windows holds a log file open for a concurrent reader (a log tail, a test polling
# the file) without FILE_SHARE_DELETE, so stdlib's rename raises PermissionError and
# the record is lost through Handler.handleError. The reader's handle is short-lived,
# so a bounded retry covers the real case; a persistent conflict still surfaces.
_ROLLOVER_ATTEMPTS = 5
_ROLLOVER_BACKOFF_S = 0.01


class _ManagedRotatingFileHandler(logging.handlers.RotatingFileHandler):
    """Rotate through a transient sharing violation instead of dropping the record."""

    def doRollover(self) -> None:
        for attempt in range(_ROLLOVER_ATTEMPTS - 1):
            try:
                super().doRollover()
                return
            except PermissionError:
                time.sleep(_ROLLOVER_BACKOFF_S * (attempt + 1))
        super().doRollover()


class _PipelineQueueHandler(logging.handlers.QueueHandler):
    """Queue the record untouched; the listener's handlers do the formatting (D4)."""

    def prepare(self, record: logging.LogRecord) -> logging.LogRecord:
        return record

    def emit(self, record: logging.LogRecord) -> None:
        try:
            super().emit(record)
        except Exception:
            # REQ-013/AC-016: a broken sink never interrupts the emitting call. The
            # stdlib QueueHandler already guards its own emit; restating the guard at
            # our own boundary keeps the guarantee independent of a stdlib
            # implementation detail (a queue failure - closed interpreter, full queue -
            # must never travel into business code).
            self.handleError(record)


class _PipelineQueueListener(logging.handlers.QueueListener):
    """Keep draining when a sink raises: the stdlib monitor loop does not.

    ``QueueListener._monitor`` guards only ``queue.Empty``, so one exception escaping a
    handler (a broken ``emit``, a closed stream, a formatter failure) ends the thread and
    the file sink goes permanently silent for the rest of the process — every later
    record is queued and never written. That amplifies the AC-016 failure from one
    record to all of them, so the guard sits on the listener side of the queue too.
    """

    def handle(self, record: logging.LogRecord) -> None:
        try:
            super().handle(record)
        except Exception:
            # QueueListener has no handleError; the handlers' own reporting keeps the
            # failure visible (stdlib traceback on stderr) without ending the loop.
            with contextlib.suppress(Exception):  # a stderr that cannot be written
                for handler in self.handlers:
                    handler.handleError(record)


class _ForwardingHandler(logging.Handler):
    """Hand foreign records to the managed sinks, keeping their level, name and location."""

    def emit(self, record: logging.LogRecord) -> None:
        sinks = _sinks[0]
        if sinks is None:
            return
        for target in sinks.managed():
            try:
                target.handle(record)
            except Exception:
                # Handler.handle() does not guard emit: a sink whose emit raises (a
                # failure we do not control, AC-016) must not reach the emitting call,
                # and one dead sink must not stop the other sink from receiving it.
                self.handleError(record)


def pipeline_logger() -> logging.Logger:
    """The feature's own logger: the non-propagating owner of the managed sinks."""
    return logging.getLogger(PIPELINE_LOGGER_NAME)


def get_logger(name: str | None = None) -> BoundLogger:
    """Emit through the pipeline (REQ-005).

    Usable before ``setup_logger()``: no sink is created, and stdlib's last-resort
    handler still puts the record on standard error (EDGE-006).
    """
    _configure_structlog()
    return structlog.get_logger(**{LOGGER_NAME_FIELD: name or _caller_module()})


def _caller_module() -> str:
    """The module of ``get_logger()``'s caller, used when no name is given."""
    frame = sys._getframe(2)
    return str(frame.f_globals.get("__name__", PIPELINE_LOGGER_NAME))


def _logger_factory(*_args: Any, **_kwargs: Any) -> logging.Logger:
    """Structlog's logger factory: always the pipeline logger (never ``setLoggerClass``)."""
    return pipeline_logger()


def _configure_structlog() -> None:
    """Bind structlog to the pipeline: processors only, never a second backend."""
    structlog.configure(
        processors=[*_EMITTING_CHAIN, ProcessorFormatter.wrap_for_formatter],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=_logger_factory,
        cache_logger_on_first_use=True,
    )


def _validate_renderer(renderer: str | None) -> RendererName | None:
    """Validate before anything is mutated, so a rejected call changes nothing (EDGE-005)."""
    if renderer is None:
        return None
    if renderer not in RENDERERS:
        msg = f"unknown renderer {renderer!r}; expected one of {', '.join(RENDERERS)}"
        raise ValueError(msg)
    return cast("RendererName", renderer)


def _level_of(settings: Settings) -> int:
    """The configured level as a stdlib level number."""
    level = logging.getLevelName(settings.log_level.upper())
    return level if isinstance(level, int) else logging.INFO


def _renderer_pair(renderer: RendererName | None) -> tuple[RendererName, RendererName]:
    """The default pair is text console + JSON file; an explicit value sets both (REQ-006, D3)."""
    return (renderer or "text", renderer or "json")


def _formatter_for(renderer: RendererName, stream: Any) -> ProcessorFormatter:
    """One formatter per sink: the JSON serializer adapter returns str (ADR-082)."""
    render = render_json if renderer == "json" else TextRenderer(color=color_for_tty(stream))
    return ProcessorFormatter(
        processors=[*_RENDER_CHAIN, render],
        foreign_pre_chain=list(_EMITTING_CHAIN),
    )


@logged(level=_SETUP_TRACE_LEVEL, slow_threshold_ms=_SETUP_SLOW_THRESHOLD_MS)
def setup_logger(*, renderer: str | None = None) -> None:
    """Install the pipeline, or reconfigure the installed one (REQ-001, INV-001).

    Idempotent and thread-safe: concurrent calls leave exactly one set of sinks,
    and the stdlib root logger is never re-levelled (INV-004).
    """
    name = _validate_renderer(renderer)
    with _setup_lock:
        if _sinks[0] is None:
            _install(name)
        else:
            _reconfigure(name)


def _install(renderer: RendererName | None) -> None:
    settings = get_settings()
    level = _level_of(settings)
    log_file = Path(settings.log_file)
    log_file.parent.mkdir(parents=True, exist_ok=True)  # EDGE-001
    console_renderer, file_renderer = _renderer_pair(renderer)

    rotating = _ManagedRotatingFileHandler(
        log_file,
        maxBytes=settings.log_max_bytes,
        backupCount=settings.log_backup_count,
        encoding="utf-8",
    )
    queue_handler = _PipelineQueueHandler(queue.SimpleQueue())
    listener = _PipelineQueueListener(queue_handler.queue, rotating, respect_handler_level=True)

    console_stream = sys.stderr
    console = logging.StreamHandler(console_stream)
    console.setLevel(level)
    console.setFormatter(_formatter_for(console_renderer, console_stream))
    rotating.setLevel(level)
    rotating.setFormatter(_formatter_for(file_renderer, rotating))

    listener.start()  # NFR-005: the only thread the pipeline adds

    logger = pipeline_logger()
    logger.setLevel(level)
    logger.propagate = False
    logger.addHandler(console)
    logger.addHandler(queue_handler)

    forwarding = _ForwardingHandler()
    forwarding.setLevel(level)
    logging.getLogger().addHandler(forwarding)

    _sinks[0] = PipelineSinks(
        console=console,
        queue=queue_handler,
        rotating=rotating,
        forwarding=forwarding,
        listener=listener,
        renderer=renderer,
        log_file=log_file,
    )
    _configure_structlog()
    _subscribe_to_setting_changes()
    _emit_setup_record(reconfigured=False)


def _reconfigure(renderer: RendererName | None) -> None:
    """Mutate the installed handlers in place; never build a second file handler."""
    sinks = _sinks[0]
    if sinks is None:
        return
    settings = get_settings()
    level = _level_of(settings)
    console_renderer, file_renderer = _renderer_pair(renderer)

    sinks.renderer = renderer
    sinks.console.setFormatter(_formatter_for(console_renderer, sinks.console.stream))
    sinks.rotating.setFormatter(_formatter_for(file_renderer, sinks.rotating))
    pipeline_logger().setLevel(level)
    for handler in (sinks.console, sinks.rotating, sinks.forwarding):
        handler.setLevel(level)

    log_file = Path(settings.log_file)
    if log_file != sinks.log_file:
        _move_file_handler(sinks.rotating, log_file)
        sinks.log_file = log_file
    sinks.rotating.maxBytes = settings.log_max_bytes
    sinks.rotating.backupCount = settings.log_backup_count

    _reconcile_ownership(sinks)
    _emit_setup_record(reconfigured=True)


def _move_file_handler(handler: logging.handlers.RotatingFileHandler, log_file: Path) -> None:
    """Point the single rotating file handler at a new path (its stream is replaced)."""
    log_file.parent.mkdir(parents=True, exist_ok=True)
    # The rotating handler is written by the listener thread (D4); Handler.acquire()
    # takes the same lock Handler.handle() holds around emit.
    handler.acquire()
    try:
        if handler.stream is not None:
            handler.close()
        handler.baseFilename = str(log_file.resolve())
        handler.stream = handler._open()
    finally:
        handler.release()


def _reconcile_ownership(sinks: PipelineSinks) -> None:
    """Re-assert sink ownership after an outsider reconfigured stdlib logging (EDGE-003)."""
    logger = pipeline_logger()
    logger.disabled = False
    logger.propagate = False
    if not any(handler is sinks.forwarding for handler in logging.getLogger().handlers):
        logging.getLogger().addHandler(sinks.forwarding)
    for handler in (sinks.console, sinks.queue):
        if handler not in logger.handlers:
            logger.addHandler(handler)


def _emit_setup_record(*, reconfigured: bool) -> None:
    """The pipeline's own observability record (spec §9)."""
    sinks = _sinks[0]
    if sinks is None:
        return
    get_logger("logging").info(
        "logging configured",
        level=logging.getLevelName(sinks.console.level),
        file=str(sinks.log_file),
        rotation_bytes=sinks.rotating.maxBytes,
        renderer=sinks.renderer or "default",
        reconfigured=reconfigured,
    )


def _subscribe_to_setting_changes() -> None:
    """Reconfigure whenever a ``logging.*`` setting is written (settings-coverage AC-020)."""
    if _subscribed[0]:
        return
    from backend.eventbus import get_event_bus
    from backend.settings import SettingChanged

    def _on_setting_changed(event: SettingChanged) -> None:
        if not str(event.key).startswith("logging."):
            return
        with _setup_lock:
            sinks = _sinks[0]
            if sinks is not None:
                _reconfigure(sinks.renderer)

    get_event_bus().subscribe(SettingChanged, _on_setting_changed)
    _subscribed[0] = True
