# Questions: backend-api

One question file per change, created at **P.1 Frame** from this template and named `backend-api.md`. It replaces the retired central `AI_Questions.md` (archived at `docs/questions/archive-AI_Questions.md`).

- **Change:** backend-api (CROSS-CUTTING)
- **TODO file:** `docs/todo/backend-api.md`
- **Spec:** `docs/specs/backend-api.md`  <!-- created at P.4 -->
- **Opened:** 2026-10-08
- **Status:** OPEN  <!-- OPEN | ALL ANSWERED — set OPEN by the orchestrator at P.1; ALL ANSWERED once every question in this file has an answer (the orchestrator records it together with the `QUESTIONS-ANSWERED` TODO advance) -->
- **Answer rounds:** 0

Every question that needs user input is recorded HERE — never in a central file. A step that needs input records **all** of its open questions in one batch and returns `BLOCKED-USER`; the orchestrator presents them (as few `ask_user_question` rounds as possible, <= 4 per round, most blocking first), records the answers here, marks each **ANSWERED** and **incorporated**, and relaunches the step **once** with the full answer set. The change is `WAITING` while its questions are unanswered — the orchestrator works on another change meanwhile, it does not idle.

### Entry format

```markdown
## Q-<n> — <short title>
- **Step:** <P.2 Interrogate, or Sx.x <step name> — Phase <n>>
- **Why needed:** <the ambiguity, missing requirement, or decision>
- **Context:** <what the step had learned at the time>
- **Question:** <the question for the user>
- **Answer:** <the user's answer>  (or **PENDING**)
- **Date:** <YYYY-MM-DD>
- **Status:** PENDING | ANSWERED
- **Incorporated:** no | yes — <where: REQ-XXX / AC-XXX / spec section / decision>
```

## Decided before P.2 (from the `api-keys` P.3 round, 2026-10-08)

These are settled and MUST NOT be re-asked; P.2 builds on them:

1. **Transport:** a real HTTP API — **FastAPI + uvicorn** (new runtime dependency, new ADR). Not an in-process tool API, not a stdlib server.
2. **Change identity:** this is **the backend's API** (`backend-api`, CROSS-CUTTING), not an "api-keys" feature. The machine-credential half stays in the `api-keys` TODO, which now depends on this change.
3. **Authentication:** the backend's **own session tokens** (`AuthService.login()` → Bearer token → `Principal(user_id, session_token)`). No new credential type, no `Principal` change, no new seam.
4. **Authorization:** the **owner's existing roles** decide, through `@requires_permission` and the closed 61-action catalog. **No per-credential scope list in v1.**
5. **v1 surface:** **all 61 enforced catalog actions** (authentication 11, usermanagement 11, settings 19, filemanagement 10, sessionmanagement 6, mail 3, search 1).
6. **Spec governance:** the user **approved amending** `docs/specs/authentication.md` (line 15, "Out of scope: … HTTP/REST/GraphQL API layer") and `docs/specs/session-management.md` (Constraints, "no HTTP/REST layer, no frontend") — the amendments ride this change's PR.

## Preparation questions (P.2)

<filled by P.2 Interrogate>

## Interrogation coverage (P.2)

## Closed from evidence (no question needed)

## Impact Analysis (P.2) — draft for P.4

## Overlap check (P.2)

## For P.4 (what the answers change)

## Late questions (Phases 2–6)

<questions discovered after the change entered the workflow; same entry format, Step field set to the step that found it>

## Prep log
