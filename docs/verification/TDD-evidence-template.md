# TDD Evidence: [Feature Name]

This file records the RED and GREEN evidence for each acceptance criterion.

## TDD Evidence

### AC-001
RED:
  command: uv run pytest tests/acceptance/test_feature.py::test_valid_request -v
  result: FAILED
  commit: abc123

GREEN:
  command: uv run pytest tests/acceptance/test_feature.py::test_valid_request -v
  result: PASSED
  commit: def456

### AC-002
RED:
  command: uv run pytest tests/acceptance/test_feature.py::test_missing_customer_id -v
  result: FAILED
  commit: abc123

GREEN:
  command: uv run pytest tests/acceptance/test_feature.py::test_missing_customer_id -v
  result: PASSED
  commit: def456

### AC-003
RED:
  command: uv run pytest tests/acceptance/test_feature.py::test_invalid_customer_id -v
  result: FAILED
  commit: abc123

GREEN:
  command: uv run pytest tests/acceptance/test_feature.py::test_invalid_customer_id -v
  result: PASSED
  commit: def456
