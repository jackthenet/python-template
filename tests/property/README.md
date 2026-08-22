# Property Tests

Property tests verify that invariants hold over a large input space. They answer: **Does the invariant hold over a large input space?**

## Rules

- Property tests MUST use Hypothesis (`@given` decorator).
- Property tests MUST reference INV-XXX invariants from the spec.
- Property tests SHOULD use realistic strategies that match the domain.
- Property tests MUST run with sufficient examples (default 100, increase for critical invariants).

## Layout

```
tests/property/
├── test_feature_a_properties.py
├── test_feature_b_properties.py
└── ...
```

## Example

```python
"""Property tests for INV-001: normalize idempotency."""

from hypothesis import given, settings
from hypothesis import strategies as st

@given(st.text(min_size=1, max_size=100))
@settings(max_examples=200)
def test_normalize_idempotent(x: str):
    """INV-001: For every valid input x: normalize(normalize(x)) == normalize(x)."""
    assert normalize(normalize(x)) == normalize(x)
```
