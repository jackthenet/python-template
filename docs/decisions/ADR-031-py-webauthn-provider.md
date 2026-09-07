# ADR-031: py-webauthn provider for Passkey/WebAuthn

## Status
Accepted

## Context
Passkey registration and login (REQ-014 … REQ-017) require implementing the
WebAuthn protocol: option generation, attestation verification, assertion
verification, CBOR encoding, and sign-count handling. No existing dependency
covers WebAuthn. WebAuthn is a complex protocol where a custom implementation
is disproportionately risky (cryptography, protocol edge cases, browser
interoperability).

## Decision
Use the established `py-webauthn>=2.0.0` package — the **only new
dependency** for this feature — behind the `WebAuthnProvider` ABC. The
default `PyWebAuthnProvider` wraps `generate_registration_options`,
`verify_registration_response`, `generate_authentication_options`, and
`verify_authentication_response`; its `verify_*` methods raise
`InvalidPasskeyResponseError` when the underlying verification fails. RP
settings (`rp_id`, `rp_name`, `origin`) are constructor parameters with
sensible defaults. Credentials are stored in the `webauthn_credentials`
table; a sign-count regression is rejected with `PasskeyHijackError`.

## Consequences
- Cryptographically sound WebAuthn without a custom implementation;
  protocol maintenance stays upstream.
- One new runtime dependency, recorded per the `AGENTS.md` dependency
  policy (established package, solves the actual problem, standard Python
  WebAuthn library).
- The ABC keeps the WebAuthn backend swappable; the service references only
  the provider interface.

## Alternatives Considered
- A custom WebAuthn implementation — rejected: protocol complexity (CBOR,
  attestation formats, assertion format) and cryptography are strong
  "use an established package" cases per `AGENTS.md`; a hand-rolled
  implementation is a security risk.
- Deferring passkeys to a later feature — rejected: the feature brief
  prioritizes passkeys as the preferred modern method with password as
  fallback; the spec scopes registration + login together.
- A different WebAuthn library — rejected: `py-webauthn` is the standard,
  actively maintained Python WebAuthn server library.

## References
- `docs/specs/authentication.md` (D7; REQ-014 … REQ-017)
- `AGENTS.md` — Dependencies and Existing Packages
- `pyproject.toml` (`py-webauthn>=2.0.0`)
