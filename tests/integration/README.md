# Integration Tests

Integration tests verify that components work together correctly. They answer: **Do the components work together correctly?**

## Rules

- Integration tests MUST test interactions between at least two components.
- Integration tests MUST NOT duplicate acceptance test logic.
- Integration tests SHOULD use real dependencies (not mocks) where practical.
- Integration tests MUST be deterministic and isolated.

## Layout

```
tests/integration/
├── test_feature_a_integration.py
├── test_feature_b_integration.py
└── ...
```

## Example

```python
"""Integration tests for request validation + normalization pipeline."""

def test_validation_normalization_pipeline():
    """Verify that validated requests flow correctly into normalization."""
    validated = validate_request(raw_payload)
    normalized = normalize(validated)
    assert normalized.customer_id == raw_payload["customer_id"]
```
