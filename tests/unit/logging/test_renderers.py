"""Unit witness for the console renderer's color clause (docs/specs/structlog-logging.md
AC-002 "one writes colorized text to standard error", `logging.md` v3 AC-001).

No other witness in the suite can see this clause: the AC-002 acceptance witness runs
against the session pipeline, whose console stream is pytest's captured stream, and
the renderer-selection witness (`test_ac_010_renderer_selection`) has to run each case
in a fresh process with standard error redirected to a file — so ``color_for_tty()``
is False in every one of them and only the plain path ever runs. The clause is
therefore witnessed here, at the level the spec's own test strategy calls unit: the
pipeline's formatter factory is driven with a stream that reports itself a terminal
and one that does not, and the rendered console line is compared.
"""

from __future__ import annotations

import logging

from backend.logging._pipeline import _formatter_for
from backend.logging._renderers import LEVEL_COLORS, color_for_tty


class _Stream:
    """A stream whose only relevant behavior is whether it reports itself a terminal."""

    def __init__(self, *, tty: bool = True, closed: bool = False) -> None:
        self._tty = tty
        self._closed = closed

    def isatty(self) -> bool:
        if self._closed:
            raise ValueError("I/O operation on closed file")
        return self._tty

    def write(self, text: str) -> int:  # the StreamHandler contract
        return len(text)

    def flush(self) -> None:
        return None


def _record() -> logging.LogRecord:
    """An INFO record as the pipeline produces one (``levelname`` is the level field's source)."""
    return logging.LogRecord("ac_002", logging.INFO, "console_probe.py", 7, "colorized console probe", (), None)


def test_ac_002_console_color_is_selected_only_for_a_terminal_stream() -> None:
    """AC-002: the console sink colorizes for a terminal standard error, and only for one."""
    assert color_for_tty(_Stream(tty=True)) is True, "a terminal stream must select color"
    assert color_for_tty(_Stream(tty=False)) is False, "a redirected stream must stay plain"
    assert color_for_tty(_Stream(closed=True)) is False, "a closed stream must fall back to plain text"

    colored = _formatter_for("text", _Stream(tty=True)).format(_record())
    plain = _formatter_for("text", _Stream(tty=False)).format(_record())

    assert "colorized console probe" in colored, f"the console record must carry its event, got {colored!r}"
    assert "colorized console probe" in plain, f"the plain console record must carry its event, got {plain!r}"

    escape = LEVEL_COLORS["info"]
    assert escape in colored, (
        "AC-002: the console record written to a terminal standard error must carry the level's "
        f"ANSI escape ({escape!r}), got {colored!r}"
    )
    assert escape not in plain, f"AC-002: a redirected console record must not be colorized, got {plain!r}"
