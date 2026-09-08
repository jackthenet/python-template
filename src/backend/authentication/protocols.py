"""Structural protocols for swappable authentication backends (D-protocols).

:class:`AttemptTracker` abstracts the brute-force throttling backend
(in-memory in this feature; a persistent backend could be swapped in).
:class:`WebAuthnProvider` abstracts the WebAuthn (passkey) backend
(``PyWebAuthnProvider`` in this feature).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID

from backend.authentication.models import VerifiedAssertion, VerifiedCredential


class AttemptTracker(ABC):
    """Brute-force throttling for login identifiers."""

    @abstractmethod
    def record_failure(self, identifier: str) -> None:
        """Record a failed login attempt for ``identifier``."""

    @abstractmethod
    def record_success(self, identifier: str) -> None:
        """Clear the failure state for ``identifier`` (successful login)."""

    @abstractmethod
    def is_locked(self, identifier: str) -> bool:
        """Return whether ``identifier`` is currently locked out."""


class WebAuthnProvider(ABC):
    """WebAuthn (passkey) registration and login backend."""

    @abstractmethod
    def generate_registration_options(self, user_id: UUID, username: str, display_name: str | None) -> dict[str, Any]:
        """Return WebAuthn registration options for a new credential."""

    @abstractmethod
    def verify_registration_response(
        self, user_id: UUID, username: str, response: dict[str, Any]
    ) -> VerifiedCredential:
        """Verify a registration response and return the stored credential."""

    @abstractmethod
    def generate_authentication_options(self, credential_id: str) -> dict[str, Any]:
        """Return WebAuthn authentication options for a stored credential."""

    @abstractmethod
    def verify_authentication_response(self, credential_id: str, response: dict[str, Any]) -> VerifiedAssertion:
        """Verify an authentication response and return the assertion."""
