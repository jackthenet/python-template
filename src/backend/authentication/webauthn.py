"""WebAuthn (passkey) provider wrapping py-webauthn (T-006, ADR-031).

The py-webauthn import is deferred to :class:`PyWebAuthnProvider` method calls
so the feature — and its test suite, which uses a configurable fake provider —
imports and runs without py-webauthn installed. In production,
``PyWebAuthnProvider`` requires py-webauthn; its ``verify_*`` methods raise
:class:`InvalidPasskeyResponseError` when the underlying verification fails.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from backend.authentication.errors import InvalidPasskeyResponseError
from backend.authentication.models import VerifiedAssertion, VerifiedCredential
from backend.authentication.protocols import WebAuthnProvider


def _webauthn():
    """Import and return the py-webauthn module (deferred import)."""
    try:
        import webauthn
    except ImportError as error:
        raise InvalidPasskeyResponseError(
            "py-webauthn is required for PyWebAuthnProvider but is not installed"
        ) from error
    return webauthn


class PyWebAuthnProvider(WebAuthnProvider):
    """A WebAuthn provider backed by py-webauthn.

    The registration and authentication challenges are tracked per user id and
    credential id respectively, so the ``verify_*`` methods (which receive only
    the response) can complete verification.
    """

    def __init__(self, rp_id: str, rp_name: str, origin: str) -> None:
        self._rp_id = rp_id
        self._rp_name = rp_name
        self._origin = origin
        self._registration_challenges: dict[str, str] = {}
        self._authentication_challenges: dict[str, str] = {}

    def generate_registration_options(self, user_id: UUID, username: str, display_name: str | None) -> dict[str, Any]:
        webauthn = _webauthn()
        options = webauthn.generate_registration_options(
            rp_id=self._rp_id,
            rp_name=self._rp_name,
            user_id=str(user_id),
            user_name=username,
            user_display_name=display_name or username,
        )
        self._registration_challenges[str(user_id)] = options.challenge
        return options.public_dict

    def verify_registration_response(
        self, user_id: UUID, username: str, response: dict[str, Any]
    ) -> VerifiedCredential:
        webauthn = _webauthn()
        challenge = self._registration_challenges.pop(str(user_id), "")
        try:
            verification = webauthn.verify_registration_response(
                registration_response=response,
                expected_challenge=challenge,
                expected_rp_id=self._rp_id,
                expected_origin=self._origin,
                require_user_verification=False,
            )
        except Exception as error:
            raise InvalidPasskeyResponseError("registration response verification failed") from error
        cred = verification["credential"]
        return VerifiedCredential(
            credential_id=cred["id"],
            public_key=cred["publicKey"],
            transports=list(cred.get("transports", [])),
            sign_count=int(cred.get("signCount", 0)),
        )

    def generate_authentication_options(self, credential_id: str) -> dict[str, Any]:
        webauthn = _webauthn()
        options = webauthn.generate_authentication_options(
            credential_ids=[credential_id],
            rp_id=self._rp_id,
            user_verification="preferred",
        )
        self._authentication_challenges[credential_id] = options.challenge
        return options.public_dict

    def verify_authentication_response(self, credential_id: str, response: dict[str, Any]) -> VerifiedAssertion:
        webauthn = _webauthn()
        challenge = self._authentication_challenges.pop(credential_id, "")
        try:
            verification = webauthn.verify_authentication_response(
                authentication_response=response,
                expected_challenge=challenge,
                expected_rp_id=self._rp_id,
                expected_origin=self._origin,
                require_user_verification=False,
            )
        except Exception as error:
            raise InvalidPasskeyResponseError("authentication response verification failed") from error
        return VerifiedAssertion(
            credential_id=credential_id,
            sign_count=int(verification.get("new_sign_count", 0)),
        )
