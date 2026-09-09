"""Opaque token generation and hashing (REQ-006, NFR-002).

Raw session and reset tokens are 256-bit URL-safe random values
(``secrets.token_urlsafe(32)``). Tokens are stored only as their SHA-256 hash;
the raw token is returned exactly once at issuance and never persisted.
"""

from __future__ import annotations

import hashlib
import secrets

from backend.logging import logged


@logged(slow_threshold_ms=10, include_args=False)
def new_token() -> str:
    """Return a fresh 256-bit URL-safe random token (43 chars for ``token_urlsafe(32)``).

    Traced via the shared logging feature (``@logged``) with ``include_args=False``.
    """
    return secrets.token_urlsafe(32)


@logged(slow_threshold_ms=10, include_args=False)
def hash_token(token: str) -> str:
    """Return the SHA-256 hex digest of ``token`` (the form stored at rest).

    Traced via the shared logging feature (``@logged``) with ``include_args=False``
    so the raw token never appears in log records.
    """
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
