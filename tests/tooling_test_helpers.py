"""Shared helpers for the test tooling (polyfactory, time-machine, respx).

House conventions for feature tests — use these instead of hand-crafted
field dicts, real time, or ad-hoc fake transports:

- **polyfactory** — ``model_factory(MyModel)`` returns a factory class for
  a Pydantic model: ``.build()`` produces a valid instance,
  ``.build(field=value)`` overrides fields, ``.batch(n)`` produces ``n``
  instances.
- **time-machine** — ``travel(destination)`` freezes the clock for a block
  (TTL, lockout, token-expiry tests): no sleeps, no manual clock mocking.
- **respx** — ``mock_http()`` mocks outbound httpx calls for a block;
  register routes on the yielded router.

Import top-level, like the other ``*_test_helpers`` modules (``tests/`` is
on ``sys.path``).
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime

import respx
import time_machine
from polyfactory.factories.pydantic_factory import ModelFactory
from pydantic import BaseModel


def model_factory[T: BaseModel](model: type[T]) -> type[ModelFactory[T]]:
    """A polyfactory factory class for ``model`` (valid default test data).

    ``.build()`` produces a schema-valid instance instead of a hand-crafted
    field dict, ``.build(field=value)`` overrides individual fields, and
    ``.batch(n)`` produces ``n`` instances. polyfactory generates values
    per field from the model's schema, so every built instance passes the
    model's validation.
    """
    return ModelFactory.create_factory(model)


@contextmanager
def travel(destination: time_machine.DestinationType, *, tick: bool = False) -> Iterator[datetime]:
    """Freeze (or advance) the clock at ``destination`` for the block.

    Yields the frozen ``datetime`` so a test can assert against the exact
    moment. ``tick=False`` (the default) keeps the clock frozen; pass
    ``tick=True`` for deadline tests (TTLs, lockouts, token expiry) that
    must observe the deadline pass — no sleeps, no manual clock mocking.
    """
    with time_machine.travel(destination, tick=tick):
        yield datetime.now()


@contextmanager
def mock_http() -> Iterator[respx.MockRouter]:
    """Mock outbound httpx calls for the block (respx).

    Yields the respx router; register routes on it (``router.route(
    method="GET", url=...).respond(...)``). Respx's strict defaults hold:
    an unmocked request raises, and every registered route must be called
    before the block exits — a test can never silently touch the network
    or leave a dead route behind.
    """
    with respx.mock() as router:
        yield router
