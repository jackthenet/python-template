# Questions: composition-root-factory

One question file per change, created at **P.1 Frame** from this template and named `composition-root-factory.md`. It replaces the retired central `AI_Questions.md` (archived at `docs/questions/archive-AI_Questions.md`).

- **Change:** composition-root-factory (REFACTOR)
- **TODO file:** `docs/todo/composition-root-factory.md`
- **Spec:** n/a (REFACTOR) — `docs/specs/settings-coverage.md` REQ-002 / AC-003 likely need an amendment
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

_None yet — the P.2 Interrogate step has not run. Opened out of `settings-public-registry-setter` Q-21 (2026-10-06): the composition-root factory that change deliberately declined to do._

Known decision points to interrogate (not yet questions): whether a factory that changes wiring **timing** is still a REFACTOR or needs a Spec Amendment PR for `settings-coverage.md` REQ-002/AC-003 first; the factory's name and return shape; whether `main`'s module-level globals stay as a compatibility layer or every consumer is updated; whether the subprocess wiring tests may be rewritten in-process; how the `_LazyPermissionService`/`_LazyUserManager` cycle proxies survive a callable root; whether importing `main` must remain side-effect-free.

## Late questions (Phases 2–6)

<questions discovered after the change entered the workflow; same entry format, Step field set to the step that found it>
