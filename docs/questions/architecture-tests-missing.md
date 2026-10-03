# Questions: architecture-tests-missing

One question file per change, created at **P.1 Frame** from the template.

- **Change:** architecture-tests-missing (DOCS/CHORE provisional)
- **TODO file:** `docs/todo/architecture-tests-missing.md`
- **Spec:** n/a
- **Opened:** 2026-10-03
- **Status:** OPEN  <!-- OPEN | ALL ANSWERED -->
- **Answer rounds:** 0

## Preparation questions (P.2)

## Q-1 — remove the dangling gate, or build the architecture tests?
- **Step:** P.1 Frame (raised at framing; P.2 has not run)
- **Why needed:** the change type — and therefore the whole workflow shape — depends on it. DOCS/CHORE (3-line text fix, no spec, no bump) vs FEATURE (a new test capability: spec + approval PR + `minor` bump + Phase 3 RED).
- **Context:** `tests/architecture/` does not exist, yet `AGENTS.md:579` and `verify/SKILL.md:88,103` make `uv run pytest tests/architecture/ -v` a Phase 5 gate for REFACTOR (and `AGENTS.md:212` promises it in the Phase Matrix). No spec requires such tests, so this is not a defect against an approved spec.
- **Question:** (a) delete/qualify the three references so the process stops citing a directory that does not exist, or (b) create `tests/architecture/` with executable rules for the boundaries the text already names (`model/` holds domain concepts, `services/` holds use cases, `shared/` stays small, no cross-feature internal imports)?
- **Answer:** **PENDING**
- **Date:** 2026-10-03
- **Status:** PENDING
- **Incorporated:** no

## Q-2 — if (b): which rules are actually checkable, and against what?
- **Step:** P.1 Frame
- **Why needed:** a gate that fails on day one blocks every REFACTOR change; a gate that duplicates `ruff`/`deptry` is dead weight.
- **Context:** the import direction between features is already partly enforced by `deptry` and ruff's isort settings; the "model/ has no infrastructure imports" and "shared/ is small" rules are not checkable by those tools.
- **Question:** which rules should the first version enforce — (i) no cross-feature internal imports (features import each other's public `__init__` only), (ii) `shared/` file-count/dependency ceiling, (iii) `model/` modules must not import persistence/IO libraries, or a minimal (i) only?
- **Answer:** **PENDING**
- **Date:** 2026-10-03
- **Status:** PENDING
- **Incorporated:** no

## Q-3 — sequencing against the other two `AGENTS.md` editors
- **Step:** P.1 Frame
- **Why needed:** three backlog changes edit `AGENTS.md` (this one at `:212`/`:579`, `value-triage-gate` at the Phase P table/Obligations, `workflow-docs-nits` at the `specify` skill). `value-triage-gate`'s own Q-4 asks the reciprocal question.
- **Context:** `value-triage-gate` and `workflow-docs-nits` are both WAITING on user answers; this change is PREPARING.
- **Question:** land this one first, last, or fold its (a) variant into `value-triage-gate`'s PR (it already rewrites the same Phase 5 / Phase Matrix wording)?
- **Answer:** **PENDING**
- **Date:** 2026-10-03
- **Status:** PENDING
- **Incorporated:** no

## Late questions (Phases 2–6)

<questions discovered after the change entered the workflow; same entry format, Step field set to the step that found it>
