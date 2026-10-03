# TODO: track-python-skill

Backlog item for one planned change, created at **P.1 Frame** from this template and named `track-python-skill.md`. One file per change.

This is a **planning record, not normative**: like `docs/questions/`, it is committed directly to `main` (see "Phase P: PREPARE" in `AGENTS.md`). It carries no approval gate — the spec does.

- **Status:** MERGED  <!-- PREPARING | QUESTIONS-ANSWERED | READY | IN-WORKFLOW | WAITING | MERGED -->
- **Change type:** DOCS/CHORE
- **Created:** 2026-10-03
- **Question file:** `docs/questions/track-python-skill.md`
- **Spec:** n/a  <!-- DOCS/CHORE: no spec -->
- **Worktree:** <created at P.4> `../python-template_kopie-worktrees/chore/track-python-skill`
- **Depends on:** none
- **Related specs:** none (no `docs/specs/` file is touched)

## Goal (one line)
Track the untracked `.agents/skills/python-best-practices/` skill (8 files, ~40 KB) in git so it exists in every change worktree and in CI.

## Why
The directory is present on disk and is loaded as live agent guidance (it is one of the skills `AGENTS.md` resolves), but `git status` reports it as untracked: `?? .agents/skills/python-best-practices/`. Consequences observed on 2026-10-03: it does **not** exist in any change worktree (each worktree checks out tracked paths only), it is invisible to PR reviewers, and a worktree/working-directory cleanup would lose it permanently — `SKILL.md` plus `references/` (modern-python, python-3.15, structure, testing, performance, errors-and-resources, models-and-config) have no copy anywhere in the repository history.

## In scope
- `git add .agents/skills/python-best-practices/` — the 8 existing files, content unchanged.
- Commit them on the change branch (`chore/track-python-skill`) so they reach `main` through a PR.

## Out of scope
- Editing the skill's content (its wording, examples, or reference split).
- Any change to `AGENTS.md`, the other skills, `docs/specs/`, `src/`, `tests/`, `.github/workflows/`, or config files.
- Adding a tooling or dependency for TypeScript/linting of skill files.

## Affected features
None — no `src/backend/` or `src/frontend/` path is touched.

## Constraints and risks
- No externally observable behavior delta: the skill is agent-facing guidance, not product code, and its content is not modified.
- **P.2 must check for guidance conflicts:** the skill is referenced by nothing (`grep -rn "python-best-practices"` outside its own directory → no match), so nothing states whether its advice agrees with this repo's conventions. If a reference file contradicts `AGENTS.md` (e.g. dependency or typing policy), that is a reclassification trigger (DOCS/CHORE → any), not a silent fix.
- The files must be committed as-is; a content edit inside this change would exceed the no-behavior-delta scope.

## Value triage (2026-10-03, pre-workflow)
- **Overlap:** none — the skill exists on disk but is tracked by nothing; there is no existing feature to extend.
- **Beneficiary:** anyone driving the agent from a change worktree (the skill is currently absent there) and every PR reviewer (currently cannot see the guidance).
- **Score: 4/5** — clear value and a one-command diff, but it delivers no new capability, only durability and visibility of guidance that already works locally.
- **Decision:** user chose **implement** (log + implement).

## Acceptance signal (plain language)
`git ls-files .agents/skills/python-best-practices` lists 8 paths, `git status` is clean, and the change's diff contains **only** those 8 added paths — no `src/`, `tests/`, `pyproject.toml`, `.github/` or config path — so the DOCS/CHORE light gate (lint/types where applicable, no full-suite run) applies.

## Prep log
| Step | Date | Result |
|---|---|---|
| P.1 Frame | 2026-10-03 | TODO + question file created on `main`; type DOCS/CHORE; todo set created |
| Delivered | 2026-10-03 | **Landed on `main` as direct commit `c2342b6`** — `git ls-files .agents/skills/python-best-practices` lists 8 paths, `git status` clean, acceptance signal met. **Process deviation recorded:** the content reached `main` without a change branch/PR, which `AGENTS.md` (“Git Worktrees”, “Agent Prohibitions”) permits only for `docs/todo/` + `docs/questions/`. P.2–P.6 were therefore not run; no worktree exists. Recorded here so the deviation is visible rather than hidden. |
| P.2 Interrogate (<n> questions) | | |
| P.3 Answer (<n> answered) | | |
| P.4 Draft spec / triage / baseline / scope | | |
| P.5 Self-consistency | | n/a (DOCS/CHORE) |
