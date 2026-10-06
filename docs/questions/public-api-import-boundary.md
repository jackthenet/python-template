# Questions: public-api-import-boundary

One question file per change, created at **P.1 Frame** from this template and named `public-api-import-boundary.md`. It replaces the retired central `AI_Questions.md` (archived at `docs/questions/archive-AI_Questions.md`).

- **Change:** public-api-import-boundary (REFACTOR)
- **TODO file:** `docs/todo/public-api-import-boundary.md`
- **Spec:** n/a (REFACTOR — the normative basis is the GREEN baseline + refactor scope)
- **Opened:** 2026-10-06
- **Status:** OPEN  <!-- OPEN | ALL ANSWERED -->
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

## Preparation questions (P.2)

_None yet — the P.2 Interrogate step has not run. Opened out of `settings-public-registry-setter` Q-19 (2026-10-06): the wider "package `__init__` is the only import surface" convention, deferred out of that change on purpose._

Known decision points to interrogate (not yet questions): the self-import exemption mechanics; whether import-path edits are the only permitted test changes under the REFACTOR "zero test changes" rule; whether missing `__init__` re-exports make this a FEATURE; how it composes with the `TID251` block already added by `settings-public-registry-setter`.

## Late questions (Phases 2–6)

<questions discovered after the change entered the workflow; same entry format, Step field set to the step that found it>
