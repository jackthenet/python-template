# ADR-083: Public install operation (`set_*`) as the third member of the singleton trio, one module lock per slot

## Status
Accepted

## Context
Five features expose a shared default through a module singleton — settings
(`get_settings_registry`), eventbus (`get_event_bus`), permissions
(`get_permission_service`), search (`get_search_service`) and
session-management (`get_session_service`) — each paired with a
`reset_*()` for tests. **There is no public operation that installs an
instance the caller built as that shared default.** A caller that wants the
instance it configured shared has to write the owning module's private
one-element list.

Measured on this branch (`crosscut/settings-public-registry-setter`, 2026-10-07):

- **12 outside-owner writes** to a slot the writing module does not own — one
  in `src/` (`src/main.py:138` writes `_settings_registry_singleton[0]`, the
  alias imported at `src/main.py:68`) and eleven in tests
  (`tests/settings_test_helpers.py:132,160,180`;
  `tests/eventbus_test_helpers.py:77,84`;
  `tests/acceptance/settings_coverage/test_setup_logger.py:31,55`;
  `tests/acceptance/settings_coverage/test_wiring.py:18`;
  `tests/contract/logging/test_logging_contracts.py:35`;
  `tests/property/logging/test_logging_properties.py:42`;
  `tests/unit/logging/test_logging_edges.py:32`).
- **Four of the five slots are unguarded.** Only `src/backend/search/service.py:547`
  has `_singleton_lock`; `settings/registry.py:45`, `eventbus/eventbus.py:212`,
  `permissions/service.py:504` and `sessionmanagement/service.py:344` are a bare
  `list[...] = [None]`. Two threads hitting the lazy-create path can each build a
  default and one is lost **silently** — no record, no error.

This is a **cross-feature interface** decision (the same new public operation in
five features, called by the composition root and by every test helper that
isolates state) and a **new pattern element** (the trio `get_* / set_* / reset_*`
with all three slot operations mutually exclusive under one lock). It is argued
against the S2.1 threshold in `docs/verification/settings-public-registry-setter.md`.

## Decision
Each singleton-owning feature exports a **public install operation** —
`set_settings_registry`, `set_event_bus`, `set_permission_service`,
`set_search_service`, `set_session_service` — as the third member of its
existing `get_*()` / `reset_*()` pair, re-exported from the feature package root
(`REQ-001`, `REQ-014`). Its semantics are fixed once for all five features:

- installing over a **non-empty** slot replaces the instance unconditionally and
  logs **exactly one WARNING** naming the shared default; installing into an
  empty slot logs none (`REQ-002`);
- an install is **not retroactive** and has **no lifecycle effect** on the
  instance it replaces — no `shutdown()`, no `start()`; lifecycle stays with the
  caller, and `reset_event_bus()` remains the only reset that shuts anything down
  (`REQ-003`, event-bus REQ-005);
- the parameter is the feature's concrete instance, **never `None`** — clearing
  stays the exclusive job of `reset_*()`; it is checked by the annotation and
  `mypy src/` only, with no runtime `isinstance` and no new exception type
  (`REQ-004`, `REQ-005`);
- an install publishes **no event** (`REQ-009`);
- each is traced `@logged(slow_threshold_ms=5)`, matching its sibling
  `get_*`/`reset_*` functions (`REQ-010`).

**One module-level `threading.Lock` per owning module guards all three slot
operations — install, lazy create and reset** (`REQ-006`). The owning module's
own lazy-create path **keeps its direct write to its own slot** and does not call
the public setter; it performs that write under the same lock (`REQ-007`). The
lock is held only for the slot read/swap: no repository, service construction or
event publication happens under it, and the WARNING is emitted after the lock is
released (`NFR-003`).

The composition root installs through the public setter at its current
module-import-time position and reads the shared instance back through
`get_settings_registry()` at its consumer sites instead of keeping a private
handle to the slot (`REQ-011`). The test suite migrates to the public setter with
its **existing capture-install-restore semantics unchanged** (`REQ-012`).

## Consequences
- **The private slot becomes an implementation detail of its owning module.** The
  guard that keeps it that way is ADR-084.
- **The lazy-create race closes** in the four features that had none, and install
  and reset become atomic with respect to reads (`AC-009`, `AC-010`, `EDGE-033`,
  event-bus EDGE-012, `user-roles-permissions.md` EDGE-028, `search.md` EDGE-023,
  `session-management.md` EDGE-014).
- **The trio becomes uniform across five features**, so "how do I install the
  instance I built?" has one answer everywhere, and `AGENTS.md` gains one bullet
  per feature (`REQ-015`, `AC-019`).
- **`settings-coverage.md` REQ-002 becomes literally true**: the startup wiring
  registers feature settings "using the shared registry from
  `get_settings_registry()`" only once the composition root reads the instance
  back through the getter instead of passing its local handle (`AC-016`).
- **Costs / risks:** five modules gain a function and a lock. A test helper that
  installs twice per test now emits one WARNING record per replace — accepted
  deliberately (raising on replace would break both the helpers and the
  composition root). The features are **not symmetric**: `get_session_service()`
  with no `repository` argument still raises `ValueError`, so install→reset→read
  is observed through `get_session_service(repository)` for that feature
  (`EDGE-003`, `AC-012`, `session-management.md` AC-049).
- **Extends, does not supersede:** ADR-017 (its `threading.RLock` guards
  `SettingsRegistry` **instance** state — the definition map, the values, the
  template repository; this ADR's module lock guards the **slot variable**. Two
  different locks, and the settings module ends up with both); ADR-065
  (constructor DI plus module singleton stands — `set_session_service` is
  additive); ADR-009 (instantiability is the reason an install operation is
  useful at all); ADR-040 (the `required=False` guarded read is unchanged, now
  taken under the same lock, and still creates nothing — `EDGE-004`,
  `settings.md` EDGE-032).
- **Deliberately not decided here:** who may *import* the public API (TODO
  `public-api-import-boundary`) and a `create_app()` composition root (TODO
  `composition-root-factory`). This change replaces the mechanism, not the
  wiring ownership.

## Alternatives Considered
- **Keep the direct slot write (with a `noqa` or an agreed exception)** —
  rejected: that is the defect. 12 sites already do it, four of the five slots
  are unguarded, and the pattern would keep spreading.
- **A composition-root factory / DI container instead of an install operation**
  — rejected for this change (Q-11, deferred TODO `composition-root-factory`): it
  moves wiring ownership and is a far larger diff, and it would not by itself
  give the test helpers an install seam.
- **`set_x(instance | None)` where `None` clears the slot** — rejected (Q-7): it
  duplicates `reset_*()`, makes the parameter nullable for every caller, and
  erases the WARNING signal that distinguishes "install over a live default" from
  "clear it".
- **Runtime `isinstance` validation plus a new exception type** — rejected
  (Q-8): the five modules are internal backend code with a typed call surface;
  `mypy src/` already catches the mistake, and a new error path would be behavior
  no requirement asks for.
- **Route the owner's lazy-create path through the public setter** — rejected
  (Q-10): it would emit a second traced entry/exit pair on every first read and
  make the WARNING path reachable from a read. The lock, not the setter, is what
  makes the lazy path safe.
- **Per-operation locks, an `RLock`, or a lock-free reference** — rejected: one
  plain `Lock` per module is what search already does (`service.py:547`), the
  guarded section is a read-and-swap of one list element, and re-entrancy buys
  nothing when no guarded section calls another.
- **Publish an event on install, or shut down the replaced instance** — rejected:
  no requirement asks for it, and shutting down an instance the caller may still
  hold would destroy a live object (the scratch/park pattern in
  `tests/eventbus_test_helpers.py:76-85` assumes the opposite).

## References
- `docs/specs/settings-public-registry-setter.md` — REQ-001…REQ-012,
  AC-001…AC-014, AC-016, INV-001…INV-003, EDGE-001…EDGE-007, EDGE-010,
  NFR-001…NFR-003; decisions D1–D8, D10–D11, D14.
- Amended specs: `docs/specs/settings.md` v5 (REQ-026; AC-040…AC-043; INV-011;
  EDGE-030…EDGE-033), `docs/specs/event-bus.md` v2 (REQ-008; AC-013…AC-016;
  EDGE-011, EDGE-012), `docs/specs/user-roles-permissions.md` v2 (REQ-030;
  AC-041…AC-044; EDGE-027, EDGE-028), `docs/specs/search.md` v4 (REQ-024;
  AC-038…AC-041; EDGE-022, EDGE-023), `docs/specs/session-management.md` v2
  (REQ-023; AC-046…AC-049; EDGE-013, EDGE-014), `docs/specs/logging-coverage.md`
  v3 (five §3.1 inventory rows, no new ID).
- `docs/decisions/ADR-009-module-singleton-instantiable.md`,
  `ADR-017-registry-singleton-thread-safety.md`,
  `ADR-040-guarded-registry-getter.md`,
  `ADR-065-constructor-di-module-singleton.md` (all extended, none superseded).
- Guard for this decision: `docs/decisions/ADR-084-two-guards-singleton-slot-tid251-scan-test.md`.
- Measurement record: `docs/verification/settings-public-registry-setter.md`
  (§ "Facts verified against the code at P.4", § "Facts re-measured at P.5",
  § "S2.1 — ADR decision").
