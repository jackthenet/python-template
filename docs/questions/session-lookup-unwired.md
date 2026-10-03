# Questions: session-lookup-unwired

One question file per change, created at **P.1 Frame** from the template.

- **Change:** session-lookup-unwired (ISSUE)
- **TODO file:** `docs/todo/session-lookup-unwired.md`
- **Spec:** n/a (defect against `docs/specs/user-roles-permissions.md`)
- **Opened:** 2026-10-03
- **Status:** OPEN  <!-- OPEN | ALL ANSWERED -->
- **Answer rounds:** 0

## Preparation questions (P.2)

_None yet — P.2 has not run. The two points below are recorded by P.1 as context for P.2, not as questions._

- The reproduction test must exercise the **real composition root** (`src/main.py`), because every existing test constructs its own `PermissionService` and therefore cannot see the missing wiring.
- Whether the session repository is already constructed before `_permission_service` in `src/main.py`, or needs a lazy proxy (the `UserManager` proxy precedent at `src/main.py:139-144`), is a P.2/P.4 finding from the code, not a user decision.

## Late questions (Phases 2–6)

<questions discovered after the change entered the workflow; same entry format, Step field set to the step that found it>
