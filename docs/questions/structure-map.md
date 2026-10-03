# Questions: structure-map

One question file per change, created at **P.1 Frame** from this template and named `structure-map.md`. It replaces the retired central `AI_Questions.md` (archived at `docs/questions/archive-AI_Questions.md`).

- **Change:** structure-map (FEATURE)
- **TODO file:** `docs/todo/structure-map.md`
- **Spec:** `docs/specs/structure-map.md`
- **Opened:** 2026-10-03
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

## Preparation questions (P.2)

_None yet — P.2 Interrogate has not run, so the ≥ 20-question batch is still owed. The three instruction-vs-convention conflicts found at P.1 were put to the user directly at P.1 (2026-10-03) and are answered below; they do **not** count toward the P.2 minimum. The fourth P.1 flag — whether the change type stays FEATURE or drops to DOCS/CHORE — is **not** answered and belongs to P.2._

## Q-1 — Skill location
- **Step:** P.1 Frame (conflict flagged while framing; answered out of the P.2 batch)
- **Why needed:** The instruction names `skills/code-structure-map/SKILL.md`, but this repo's skills live in `.agents/skills/<name>/SKILL.md` and are loaded from there; a root `skills/` directory would be dead text.
- **Context:** `.agents/skills/` holds 8 skills (decompose, git, implement, python-best-practices, review, specify, test, verify).
- **Question:** Where should the skill live?
- **Answer:** `.agents/skills/code-structure-map/SKILL.md` — the path the harness actually loads.
- **Date:** 2026-10-03
- **Status:** ANSWERED
- **Incorporated:** yes — `docs/todo/structure-map.md`, "In scope" (skill bullet) and "Affected features"

## Q-2 — How the `--check` gate is enforced
- **Step:** P.1 Frame
- **Why needed:** The instruction offers "a pre-commit hook **or** Makefile target"; the repo has no Makefile, and a check-only hook fails every commit that touches a `.py` file until the map is regenerated.
- **Context:** `.pre-commit-config.yaml` already runs project tooling as local hooks via `uv run` (deptry, mkdocs-build).
- **Question:** pre-commit check-only, pre-commit that regenerates, or also a CI job?
- **Answer:** **pre-commit check-only** — a local hook running `make_map.py --check`. No Makefile, no CI job.
- **Date:** 2026-10-03
- **Status:** ANSWERED
- **Incorporated:** yes — `docs/todo/structure-map.md`, "In scope" (automation bullet) and "Out of scope" (CI job excluded)

## Q-3 — Output path of the generated map
- **Step:** P.1 Frame
- **Why needed:** The repo splits `docs/` (internal process record) from `userdocs/` (published site, `mkdocs.yml` `docs_dir`); a generated root-level artifact is a third category.
- **Context:** Binding decision Q-64 keeps published docs in `userdocs/`, never `docs/`.
- **Question:** Root `STRUCTURE.md`, `docs/STRUCTURE.md`, or `userdocs/STRUCTURE.md`?
- **Answer:** **`STRUCTURE.md` at the repo root** — as the instruction states.
- **Date:** 2026-10-03
- **Status:** ANSWERED
- **Incorporated:** yes — `docs/todo/structure-map.md`, "In scope" (STRUCTURE.md bullet) and "Out of scope" (not published via mkdocs)

## Late questions (Phases 2–6)

<questions discovered after the change entered the workflow; same entry format, Step field set to the step that found it>
