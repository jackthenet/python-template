# Acceptance Tests

Acceptance tests are derived directly from the specification. They answer: **Does the system satisfy the requirement?**

## Rules

- Every acceptance test MUST reference at least one acceptance criterion (AC-XXX) from the spec.
- Test function names MUST match the test strategy table in the spec.
- Acceptance tests MUST NOT be modified to make implementation pass.
- Acceptance tests MUST NOT be deleted or weakened without spec authorization.

## Layout

```
tests/acceptance/
├── test_feature_a.py
├── test_feature_b.py
└── ...
```

## Example

```python
"""Acceptance tests for REQ-001 / AC-001."""

def test_valid_request():
    """AC-001: Given a valid request, When submitted, Then returns 200 with normalized response."""
    response = submit_request(valid_payload)
    assert response.status_code == 200
    assert "normalized" in response.json()
```
