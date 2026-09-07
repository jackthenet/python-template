# ADR-019: Argon2id password hashing via argon2-cffi

## Status
Accepted

## Context
User passwords must be stored securely (REQ-004, NFR-002): plaintext is never
stored, only a hash, and the hash is never exposed through the service API.
`verify_password` must check a candidate against the stored hash. Password
hashing is a cryptographic operation where a custom implementation is
disproportionately risky.

## Decision
Use the established `argon2-cffi` package with the Argon2id algorithm
(argon2's `PasswordHasher` with library defaults). Only the resulting hash is
stored on the `User.password_hash` column; `verify_password` uses
`PasswordHasher.verify`, which is constant-time. Passwords never appear in log
records.

## Consequences
- Cryptographically sound hashing without a custom implementation; the
  algorithm choice and parameter defaults are maintained upstream.
- A new runtime dependency (`argon2-cffi>=25.1.0`, already in
  `pyproject.toml`) with a native library (libargon2) bundled by the package.
- Hash generation dominates `create_user`/`change_password`/`verify_password`
  latency, which the NFR-001 budget (< 1 s median) explicitly allows.

## Alternatives Considered
- A custom PBKDF2/bcrypt/Scrypt implementation — rejected: cryptography is a
  strong "use an established package" case per `AGENTS.md`; a hand-rolled
  hash is a security risk.
- bcrypt — rejected: Argon2id is the current recommended default (memory
  hard, resistant to GPU/ASIC attacks) and `argon2-cffi` is the standard
  Python binding.
- Storing a salted SHA-256 hash — rejected: fast hash, unsuitable for
  password storage.

## References
- `docs/specs/user-management.md` (REQ-004, NFR-002; D2)
- `AGENTS.md` — Dependencies and Existing Packages
- `pyproject.toml` (`argon2-cffi>=25.1.0`)
