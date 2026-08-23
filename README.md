# python-template

Default template for Python projects.

## Setup

```bash
uv sync
```

## Run

```bash
uv run pytest
```

## Structure

```text
docs/         Specifications, decisions, verification
scripts/      Utility scripts (verify_spec.py)
src/          Application code
  frontend/   Frontend features
    features/ Feature-based frontend code
    shared/   Shared frontend utilities
  backend/    Backend features
    features/ Feature-based backend code
    shared/   Shared backend utilities
tests/        Test suite
  acceptance/ Feature acceptance tests
  integration/ Multi-component tests
  contract/   Interface contract tests
  property/   Invariant property tests
  unit/       Component unit tests
```