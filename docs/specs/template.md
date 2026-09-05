# Spec: [Feature Name]

## 1. Overview & Objectives
- **Feature Name:** [e.g., Redis Rate Limiter]
- **Target Component:** [e.g., `src/middleware/rate_limit.py`]
- **Goal:** [1-2 sentences on what this feature achieves and why it is needed]

## 2. Architecture & Design Decisions
- **Design Pattern:** [e.g., Sliding Window Counter via Redis, Middleware Interceptor]
- **Dependencies:** [e.g., `redis-py >= 5.0.0`, `FastAPI`]
- **Constraints:** [e.g., Must execute in < 5ms per request; non-blocking async execution]
- **Design Decisions:** [Reference ADRs in `docs/decisions/` for rationale. Keep only WHAT here; WHY goes to ADRs.]

## 3. Data Structures & API Schemas
```python
# Provide exact Pydantic models, TypeScript types, or database schemas here.
from pydantic import BaseModel

class RateLimitConfig(BaseModel):
    requests_per_minute: int = 60
    burst_limit: int = 100
```

## 4. Requirements

Each normative requirement MUST have a stable ID. These IDs propagate through the lifecycle:
`REQ-001 → AC-001 → test → task → implementation`.

| ID | Requirement |
|----|-------------|
| REQ-001 | [e.g., The service validates incoming requests against the schema.] |
| REQ-002 | [e.g., Invalid requests return a structured error identifying the field.] |
| REQ-003 | [e.g., Valid requests return a normalized representation.] |

## 5. Acceptance Criteria

Each acceptance criterion MUST have a stable ID and MUST reference at least one requirement. Use Given/When/Then format.

| ID | References | Criterion |
|----|------------|-----------|
| AC-001 | REQ-001 | **Given** a valid request, **When** the request is submitted, **Then** the service returns 200, **And** the response contains a normalized representation. |
| AC-002 | REQ-002 | **Given** a request without `customer_id`, **When** the request is submitted, **Then** the service returns 400, **And** the error identifies `customer_id`. |
| AC-003 | REQ-002 | **Given** a request with an invalid `customer_id`, **When** the request is submitted, **Then** the service returns 422. |

## 6. Invariants

State invariants that hold over a large input space. These become Hypothesis property-based tests.

| ID | Invariant |
|----|-----------|
| INV-001 | [e.g., For every valid input x: normalize(normalize(x)) == normalize(x)] |

## 7. Edge Cases & Error Conditions

| ID | Condition | Expected Behavior |
|----|-----------|-------------------|
| EDGE-001 | [e.g., Request body is empty] | [e.g., Return 400 with `body_required` error] |
| EDGE-002 | [e.g., Timeout during processing] | [e.g., Return 504 with `timeout` error] |

## 8. Non-Functional Requirements

| ID | Category | Requirement |
|----|----------|-------------|
| NFR-001 | Performance | [e.g., Must execute in < 5ms per request] |
| NFR-002 | Security | [e.g., All requests must be authenticated] |
| NFR-003 | Contract | [e.g., Response schema must remain backward-compatible] |
| NFR-004 | Observability | [e.g., Errors and lifecycle events are logged with request/event context] |

## 9. Observability & Logging

Every feature MUST be observable. Specify the logging behavior: which operations are logged, at what level, and with what context. Shared infrastructure features MUST log entry points, errors, and lifecycle events; verbose tracing belongs at DEBUG (off by default).

| Operation / Event | Level | Context |
|-------------------|-------|---------|
| [e.g., Request received] | DEBUG | [e.g., request id, path] |
| [e.g., Error handling request] | EXCEPTION | [e.g., request id, exception] |
| [e.g., Worker started] | DEBUG | [e.g., thread name] |
| [e.g., Queue full / dropped] | WARNING | [e.g., event type, dropped count] |

- **Default level:** [e.g., INFO; verbose tracing at DEBUG]
- **Error conditions:** [which conditions are errors, and how they're logged]

## 10. Test Strategy

Map each requirement/AC to a test category. This drives the test file layout.

| ID | Test Category | Test File | Test Function |
|----|---------------|-----------|---------------|
| AC-001 | acceptance | `tests/acceptance/test_feature.py` | `test_valid_request` |
| AC-002 | acceptance | `tests/acceptance/test_feature.py` | `test_missing_customer_id` |
| AC-003 | acceptance | `tests/acceptance/test_feature.py` | `test_invalid_customer_id` |
| INV-001 | property | `tests/property/test_feature.py` | `test_normalize_idempotent` |
| EDGE-001 | unit | `tests/unit/test_feature.py` | `test_empty_body` |

## 11. Traceability Matrix

Maintain this matrix as tests are written and pass. Every normative requirement MUST have at least one executable test.

| Requirement | Acceptance Criterion | Test | Status |
|-------------|---------------------|------|--------|
| REQ-001 | AC-001 | `test_valid_request` | PENDING |
| REQ-002 | AC-002 | `test_missing_customer_id` | PENDING |
| REQ-002 | AC-003 | `test_invalid_customer_id` | PENDING |
| INV-001 | — | `test_normalize_idempotent` | PENDING |
