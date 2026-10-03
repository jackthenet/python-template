# TODO: update-readme

Backlog item for one planned change, created at **P.1 Frame** from this template and named `update-readme.md`. One file per change.

This is a **planning record, not normative**: like `docs/questions/`, it is committed directly to `main` (see "Phase P: PREPARE" in `AGENTS.md`). It carries no approval gate — the spec does.

- **Status:** PREPARING  <!-- PREPARING | QUESTIONS-ANSWERED | READY | IN-WORKFLOW | WAITING | MERGED -->
- **Change type:** DOCS/CHORE  <!-- docs + agent tooling; no externally observable behavior delta -->
- **Created:** 2026-10-03
- **Question file:** `docs/questions/update-readme.md`
- **Spec:** n/a  <!-- DOCS/CHORE: no spec -->
- **Worktree:** <created at P.4> `../python-template_kopie-worktrees/chore/update-readme`
- **Depends on:** none
- **Related specs:** none (no `docs/specs/` file is touched; `README.md` is not part of the mkdocs site, which is built from `userdocs/`)

## Goal (one line)
Add the `update-readme` skill at `.agents/skills/update-readme/SKILL.md` and apply it to bring `README.md` up to current GitHub front-page practice with badges backed only by facts that exist in this repo.

## Why
`README.md` is 30 lines: a title, one sentence, `Setup`, `Run`, `Structure`. It carries no badges, no Contributing, no License statement, no quick start, and its `Run` section shows only `uv run pytest` as if that were the whole workflow. Meanwhile the repo now has three CI workflows (`Lint`, `Quality`, `Spec Validation`), a coverage gate, pre-commit, mkdocs docs, and a strict process documented in `AGENTS.md` — none of it is discoverable from the front page.

The user supplied a complete `update-readme` skill definition (inspect → badges → structure → quality rules → verify → report). Tracking it as a skill makes the same procedure reusable for every future repo refresh; applying it once fixes this repo's front page.

## In scope
- Create `.agents/skills/update-readme/SKILL.md` with the user-supplied content (frontmatter `name: update-readme` + the Workflow sections 1–6) — verbatim, no editorial rewrite.
- Rewrite `README.md` in place per that skill: badge row under the single H1, the 8-section structure (skipping what does not apply), copy-pasteable commands matching this repo's real tooling (`uv run ...`), relative links that resolve.
- Facts already verified at P.1 (so P.4 does not re-guess them):
  - `owner/repo` = `jackthenet/python-template` (`git remote get-url origin`).
  - Workflows: `.github/workflows/lint.yml` (`Lint`), `quality.yml` (`Quality`), `spec-validation.yml` (`Spec Validation`).
  - `requires-python = ">=3.14"`, `version = "0.6.0"`, `readme = "README.md"` in `pyproject.toml`.
  - `.pre-commit-config.yaml` exists; `pytest-cov` is a dev dependency and `[tool.coverage.report] fail_under` is enforced by the `coverage` job in `quality.yml`.
  - **No `LICENSE` file exists** → the skill's own rule ("only badges backed by something real") forbids a license badge.

## Out of scope
- Adding a `LICENSE` file, a `CONTRIBUTING.md`, a PyPI publish workflow, or a coverage service (Codecov) — the skill explicitly forbids inventing what is not there; each is a **separate** change if wanted, and P.4's report lists them as optional improvements.
- Any change to `AGENTS.md`, the other skills, `docs/specs/`, `userdocs/`, `mkdocs.yml`, `src/`, `tests/`, `.github/workflows/`, or any config file.
- Editing the skill's supplied wording beyond what P.2's conflict check requires (see Constraints).

## Affected features
None — no `src/backend/` or `src/frontend/` path is touched. Files: `README.md`, `.agents/skills/update-readme/SKILL.md`.

## Constraints and risks
- **No behavior delta.** `README.md` is referenced by `pyproject.toml` (`readme = "README.md"`) only as package metadata; changing its prose cannot alter observable behavior. The mkdocs site builds from `userdocs/`, never `docs/` or `README.md`, so `mkdocs build --strict` is unaffected — but it is still cheap Phase 5 evidence that nothing downstream broke.
- **Badge honesty is the whole point of the skill.** A badge for a service this repo does not use (license, PyPI downloads, Codecov) is a defect, not a polish. `python-template` is not published to a registry (no publish workflow in `.github/workflows/`); P.2 must confirm whether that is a fact to state or an assumption to leave out.
- **Coverage badge is the one genuinely ambiguous case**: coverage *is* configured (pytest-cov + `fail_under` gate in CI) but no external coverage service exists, so a shields.io badge would have to be a static hand-maintained number — which drifts. P.2 must resolve it (see `docs/questions/update-readme.md`).
- **Skill/AGENTS conflict check.** The supplied skill ends with "Edit `README.md` in place, then reply with …" — this repo additionally requires the evidence trail (`docs/verification/update-readme.md`) and the Phase 6 PR. The skill is not wrong, just silent; P.4 must not read it as license to skip the workflow. If any other line of the skill contradicts `AGENTS.md`, that is a reclassification trigger (DOCS/CHORE → any), not a silent fix.
- The skill file is committed as supplied; content edits beyond a recorded conflict fix exceed the no-behavior-delta scope.

## Value triage (2026-10-03, pre-workflow)
- **Overlap:** none — no existing TODO, spec or skill touches `README.md` (`grep -rn -i readme docs/todo docs/specs AGENTS.md .agents/skills/*/SKILL.md` → no match).
- **Beneficiary:** every visitor landing on the GitHub front page (currently cannot see CI status, Python version, or how to run the checks), and every future change that touches the front page — the skill is reusable guidance, not a one-off.
- **Score: 3/5** — real, visible improvement plus a reusable procedure, but no new capability and no effect on the product.
- **Decision:** user asked for the TODO file; implementation decision pending at P.3.

## Acceptance signal (plain language)
`README.md` has exactly one H1, a badge row of 4–7 linked badges with alt text directly under it, every badge URL pointing at a workflow file that exists in `.github/workflows/` or a fact this repo really has, every relative link resolving to an existing path, and every command matching the real tooling (`uv run ...`). The change's diff contains **only** `README.md` and `.agents/skills/update-readme/SK.md` — no `src/`, `tests/`, `pyproject.toml`, or `.github/` path — so the DOCS/CHORE light gate applies (lint/types where applicable, no full-suite run).

## Prep log
| Step | Date | Result |
|---|---|---|
| P.1 Frame | 2026-10-03 | TODO + question file created on `main`; type DOCS/CHORE; todo set created; repo facts (remote, workflows, manifest, pre-commit, no LICENSE) verified |
| P.2 Interrogate (<n> questions) | | |
| P.3 Answer (<n> answered) | | |
| P.4 Draft spec / triage / baseline / scope | | |
| P.5 Self-consistency | | n/a (DOCS/CHORE) |
