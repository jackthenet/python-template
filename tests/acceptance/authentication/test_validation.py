"""Acceptance tests for input validation (docs/specs/authentication.md, AC-030)."""

from __future__ import annotations

import pydantic
import pytest

from backend.authentication import LoginRequest


def test_ac_030_empty_identifier_validation_error() -> None:
    with pytest.raises(pydantic.ValidationError):
        LoginRequest(identifier="", password="correct-horse-1")
