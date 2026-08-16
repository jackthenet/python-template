"""Logging setup and ``@logged`` decorator.

This package is the canonical place for logging setup.

It configures loguru sinks (console + rotating file) based on application
Settings. Consumer modules should import the logger directly::

    from loguru import logger

The :func:`logged` and :func:`logged_class` decorators trace function entry,
exit, and elapsed time and are importable from this package::

    from core.logging import logged, logged_class

    @logged
    def save(): ...

    @logged(level="INFO", slow_threshold_ms=200)
    async def generate(): ...

    @logged_class(slow_threshold_setting="backend_slow_operation_ms")
    class Service:
        def run(self): ...
"""

from core.logging._decorator import logged, logged_class
from core.logging._setup import setup_logger

__all__ = ["logged", "logged_class", "setup_logger"]
