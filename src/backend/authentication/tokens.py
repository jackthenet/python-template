"""Opaque token generation and hashing (REQ-006, NFR-002).

Raw session and reset tokens are 256-bit URL-safe random values
(``secrets.token_urlsafe(32)``). Tokens are stored only as their SHA-256 hash;
the raw token is returned exactly once at issuance and never persisted.
"""

from __future__ import annotations

import hashlib
import secrets


def new_token() -> str:
    """Return a fresh 256-bit URL-safe random token (43 chars for ``token_urlsafe(32)``)."""
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    """Return the SHA-256 hex digest of ``token`` (the form stored at rest)."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
