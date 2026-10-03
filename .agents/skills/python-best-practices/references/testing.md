# Testing

Tools in this project: `pytest`, `pytest-randomly`, `pytest-xdist`, `pytest-cov`, `hypothesis`,
`polyfactory`, `respx`, `time-machine`.

## Principles

- Test **behavior**, not implementation. Assert on results and observable effects, not on which private helper was called.
- Mock only at the boundaries (HTTP, clock, filesystem when needed). Do not mock your own internals.
- Arrange, act, assert. One idea per test. Name tests by behavior: `test_login_rejects_wrong_password`.
- Every bug fix gets a test that fails without the fix.
- Coverage is a floor, not a goal. An assertion-free test that raises coverage is worse than none.

## Tests must be independent

`pytest-randomly` shuffles test order and `pytest-xdist` runs tests in parallel, so a test must not depend on another one.

- No shared mutable state at module level. Build state in function-scoped fixtures.
- Use `tmp_path` for files, never fixed paths. No fixed ports or shared database rows.
- Reproduce a failing order with `pytest -p no:randomly` (disable) or `pytest --randomly-seed=1234`; run in parallel with `pytest -n auto`.

## Test data: polyfactory, not hand-built dicts

```python
from polyfactory.factories.pydantic_factory import ModelFactory
from pydantic import BaseModel


class User(BaseModel):
    name: str
    email: str


class UserFactory(ModelFactory[User]):
    __model__ = User


def test_user_keeps_given_email() -> None:
    user = UserFactory.build(email="a@example.com")  # override only what the test cares about
    assert user.email == "a@example.com"
```

Override only the fields the test depends on; that makes it obvious what matters.

## HTTP: respx

```python
import httpx
import respx


def get_user(client: httpx.Client, user_id: int) -> dict[str, object]:
    response = client.get(f"https://api.example.com/users/{user_id}")
    response.raise_for_status()
    return response.json()


def test_get_user_returns_payload() -> None:
    with respx.mock:
        respx.get("https://api.example.com/users/1").respond(json={"id": 1})
        with httpx.Client() as client:
            assert get_user(client, 1) == {"id": 1}
```

## Time: time-machine, not sleeps

```python
import datetime as dt

import time_machine


@time_machine.travel(dt.datetime(2026, 1, 1, tzinfo=dt.UTC), tick=False)
def test_year_is_frozen() -> None:
    assert dt.datetime.now(dt.UTC).year == 2026
```

Never use `time.sleep` to wait for time-dependent behavior.

## Properties: hypothesis

Use it for parsing, validation and anything with an invariant. Example-based tests cover the cases you thought of;
hypothesis covers the ones you did not.

```python
import re

from hypothesis import given
from hypothesis import strategies as st


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


@given(st.text())
def test_slugify_is_idempotent(text: str) -> None:
    assert slugify(slugify(text)) == slugify(text)
```

## Many cases: parametrize with ids

```python
import pytest


@pytest.mark.parametrize(
    ("value", "expected"),
    [("Hello World", "hello-world"), ("  a  b  ", "a-b"), ("", "")],
    ids=["words", "extra-spaces", "empty"],
)
def test_slugify_examples(value: str, expected: str) -> None:
    assert slugify(value) == expected
```