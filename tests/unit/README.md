# Unit Tests

Unit tests verify that a particular component implements its local behavior correctly. They answer: **Does this particular component implement its local behavior correctly?**

## Rules

- Unit tests MUST test a single component in isolation.
- Unit tests SHOULD use mocks/stubs for external dependencies.
- Unit tests MUST be fast (< 100ms per test).
- Unit tests MUST NOT duplicate acceptance or integration test logic.
- Unit tests SHOULD cover edge cases and error conditions from the spec.

## Layout

```
tests/unit/
├── test_feature_a_unit.py
├── test_feature_b_unit.py
└── ...
```

## Example

```python
"""Unit tests for the request validator component."""

def test_empty_body_returns_error():
    """EDGE-001: Given empty body, When validated, Then returns body_required error."""
    result = validate_request({})
    assert result.error == "body_required"

def test_missing_field_returns_error():
    """AC-002: Given missing customer_id, When validated, Then returns 400 identifying field."""
    result = validate_request({"other": "value"})
    assert result.status_code == 400
    assert "customer_id" in result.error_fields
```
