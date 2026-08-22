# Contract Tests

Contract tests verify that external/interface contracts remain compatible. They answer: **Does the external/interface contract remain compatible?**

## Rules

- Contract tests MUST pin the exact shape of external interfaces (API responses, DB schemas, message formats).
- Contract tests MUST fail when a contract is broken, even if the implementation still works.
- Contract tests SHOULD be the first tests to run in CI (fast, deterministic).
- Contract tests MUST reference the NFR-XXX contract requirements from the spec.

## Layout

```
tests/contract/
├── test_api_contract.py
├── test_db_contract.py
└── ...
```

## Example

```python
"""Contract tests for the public API response schema."""

def test_response_schema_contract():
    """NFR-003: Response schema must remain backward-compatible."""
    response = get_response()
    assert set(response.keys()) >= {"id", "status", "data"}
    assert isinstance(response["data"], dict)
```
