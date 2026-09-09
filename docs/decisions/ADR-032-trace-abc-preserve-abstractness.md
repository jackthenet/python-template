# ADR-032: Trace repository/provider ABCs while preserving abstractness

## Status
Accepted

## Context
The logging-coverage spec (REQ-003) requires every public repository and provider
ABC to be traced with `@logged_class` so that concrete subclasses inherit tracing.
The affected ABCs are `SessionRepository`, `PasswordResetRepository`,
`WebAuthnCredentialRepository`, `AttemptTracker`, `WebAuthnProvider`
(authentication), `UserRepository` (usermanagement), and `TemplateRepository`
(settings).

An ABC is a contract: it declares abstract methods and must remain instantiable
only through a concrete subclass. Tracing a class with `@logged_class` wraps its
public methods. The design question is whether wrapping the ABC's methods
preserves the ABC's abstractness (i.e., the ABC still cannot be instantiated
directly, and a concrete subclass must still implement the abstract methods).

## Decision
Trace the ABCs with `@logged_class` in a way that **preserves abstractness**:
- The ABC remains an `ABC` (or equivalent) and its abstract methods stay abstract.
- A concrete subclass that implements the abstract methods is still required to
  instantiate the ABC (instantiating the ABC directly still raises `TypeError`).
- The concrete subclass's own public methods are what produce log records at
  runtime (the ABC's wrapped methods are not the runtime path for a concrete
  instance).

The observable contract (REQ-003 / AC-003): a concrete subclass of a traced ABC
produces entry/exit log records when its public methods are called, and the ABC
remains abstract.

## Consequences
- Concrete subclasses inherit tracing without each re-annotating the ABC.
- The ABC's abstractness is preserved, so the type system still enforces concrete
  implementation.
- The implementation must verify that `@logged_class` does not accidentally make
  the ABC instantable or drop its abstract methods (covered by AC-003 / EDGE-003).

## Alternatives Considered
- Tracing only the concrete subclasses (not the ABCs) — rejected: the spec
  (REQ-003) requires ABC tracing so that any future concrete subclass inherits
  tracing automatically; tracing only the known concretes would miss future ones.
- Making the ABC a concrete base with a default no-op tracing — rejected: this
  would drop abstractness and allow direct instantiation of the ABC, breaking the
  contract.

## References
- `docs/specs/logging-coverage.md` (REQ-003, AC-003, EDGE-003, §3.1)
- `AGENTS.md` — Using the Logging Feature (Tracing policy)
