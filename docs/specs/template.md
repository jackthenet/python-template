# Spec: [Feature Name]

## 1. Overview & Objectives
- **Feature Name:** [e.g., Redis Rate Limiter]
- **Target Component:** [e.g., `src/middleware/rate_limit.py`]
- **Goal:** [1-2 sentences on what this feature achieves and why it is needed]

## 2. Architecture & Design Decisions
- **Design Pattern:** [e.g., Sliding Window Counter via Redis, Middleware Interceptor]
- **Dependencies:** [e.g., `redis-py >= 5.0.0`, `FastAPI`]
- **Constraints:** [e.g., Must execute in < 5ms per request; non-blocking async execution]

## 3. Data Structures & API Schemas
```python
# Provide exact Pydantic models, TypeScript types, or database schemas here.
from pydantic import BaseModel

class RateLimitConfig(BaseModel):
    requests_per_minute: int = 60
    burst_limit: int = 100