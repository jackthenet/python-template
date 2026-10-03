# TODO: update-readme

Backlog item for one planned change, created at **P.1 Frame** from this template and named `update-readme.md`. One file per change.

This is a **planning record, not normative**: like `docs/questions/`, it is committed directly to `main` (see "Phase P: PREPARE" in `AGENTS.md`). It carries no approval gate — the spec does.

- **Status:** WAITING  <!-- PREPARING | QUESTIONS-ANSWERED | READY | IN-WORKFLOW | WAITING | MERGED -->
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

The user supplied a complete `update-readme` procedure (5 sections: inspect → badges → structure → quality rules → output/report). Tracking it as a skill makes the same procedure reusable for every future repo refresh; applying it once fixes this repo's front page.

## Supplied instruction set (verbatim, re-supplied 2026-10-03)

Recorded here so P.4 can write the skill without the user re-pasting it. This is the authoritative text for the skill body; it supersedes the earlier 6-section paraphrase in `## Why` (the re-supplied text has **5** sections — `verify` and `report` are folded into `### 5. Output`).

```text
# Task: Update the GitHub README

Improve the project's `README.md` so it follows current best practices and includes accurate status badges.

## 1. Inspect first (don't guess)
- Read the existing README, `pyproject.toml` / `package.json` (or equivalent), `LICENSE`, `.github/workflows/`, and the git remote URL.
- Determine the real project name, description, supported language versions, license, package registry (if published), and CI setup.

## 2. Badges
- Add a single row of badges directly under the title.
- Only include badges that match something that actually exists in the repo, e.g.:
  - CI status (the actual workflow file name)
  - License
  - Supported language versions
  - Package version/downloads (only if published)
  - Code coverage (only if configured)
  - Code style/tooling (e.g. Ruff, uv, pre-commit) if used
- Use shields.io or the native GitHub workflow badge, with the correct `owner/repo`. Never invent URLs or badges for services the project doesn't use.
- Each badge needs alt text and should link to the relevant page.

## 3. Structure and content
Use this order, skipping sections that don't apply:
1. Title + badges + one-sentence description
2. Features / why this exists
3. Installation
4. Quick start / usage (a minimal, working example)
5. Configuration
6. Development (setup, tests, linting, how to run checks)
7. Contributing
8. License

## 4. Quality rules
- Preserve all accurate existing information; don't delete content without a reason.
- Every command and code snippet must be copy-pasteable and match the project's real tooling.
- Use fenced code blocks with language tags, relative links for in-repo files, and consistent heading levels (a single H1).
- Keep it scannable: short paragraphs, no filler or marketing fluff.
- Add a table of contents only if the README is long.

## 5. Output
- Edit `README.md` in place.
- Afterwards, list what changed and flag anything you couldn't verify (e.g. a badge whose service isn't configured yet).
```

**Reconciliation against this repo's protocol** (the skill text is silent on these; it is not a contradiction, and P.4 must not read it as license to skip the workflow):
- "Edit `README.md` in place" happens in the **change worktree**, and reaches `main` only through the merged PR — `README.md` may not be committed directly to `main`.
- "list what changed and flag anything you couldn't verify" is the **change's report**, recorded in `docs/verification/update-readme.md` (Phase 5/6 evidence), not only in a chat reply.

## In scope
- Create `.agents/skills/update-readme/SKILL.md` from the verbatim instruction set recorded above (frontmatter `name: update-readme` + a short description + sections 1–5) — verbatim, no editorial rewrite.
- Rewrite `README.md` in place per that skill: badge row under the single H1, the 8-section structure (skipping what does not apply), copy-pasteable commands matching this repo's real tooling (`uv run ...`), relative links that resolve.
- **Decided 2026-10-04 (Q-4 = (b)):** the `Structure` section is **trimmed** to a short summary plus a relative link to `AGENTS.md` "Project Structure" — the wrong `features/` tree (`README.md:24`, `:27`) is deleted, not hand-corrected.
- **Decided 2026-10-04 (Q-5 = (b)):** the skill body stays verbatim **plus** a 2–3 line "Repo protocol" note pointing at the change-worktree/PR rule and `docs/verification/<name>.md`.
- **Decided 2026-10-04 (Q-2 = (a)):** no `Depends on: security-changelog-license` — this change lands without a License badge; that change adds it later and updates its own "must not write `README.md`" note.
- Facts already verified at P.1 (so P.4 does not re-guess them):
  - `owner/repo` = `jackthenet/python-template` (`git remote get-url origin`).
  - Workflows: `.github/workflows/lint.yml` (`Lint`), `quality.yml` (`Quality`), `spec-validation.yml` (`Spec Validation`).
  - `requires-python = ">=3.14"`, `version = "0.6.0"`, `readme = "README.md"` in `pyproject.toml`.
  - `.pre-commit-config.yaml` exists; `pytest-cov` is a dev dependency and `[tool.coverage.report] fail_under` is enforced by the `coverage` job in `quality.yml`.
  - **No `LICENSE` file exists** → the skill's own rule ("only badges backed by something real") forbids a license badge.

## Out of scope
- Adding a `LICENSE` file, a `CONTRIBUTING.md`, or a PyPI publish workflow — the skill explicitly forbids inventing what is not there; each is a **separate** change if wanted, and P.4's report lists them as optional improvements.
- **Coverage upload (Codecov) — Q-3 = (d), owned elsewhere:** framed as the separate backlog change **`codecov-coverage-badge`** (`docs/todo/codecov-coverage-badge.md`, 2026-10-04). This change therefore ships **no** coverage badge; the badge comes with/after that change.
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
`README.md` has exactly one H1, a badge row of 4–7 linked badges with alt text directly under it, every badge URL pointing at a workflow file that exists in `.github/workflows/` or a fact this repo really has, every relative link resolving to an existing path, every code block fenced with a language tag, the accurate content of the current 30-line README still present (notably the `Structure` tree), and every command matching the real tooling (`uv run ...`). No table of contents (the result stays short). The change's report lists what changed and flags every badge/service that could not be verified. The change's diff contains **only** `README.md` and `.agents/skills/update-readme/SKILL.md` — no `src/`, `tests/`, `pyproject.toml`, or `.github/` path — so the DOCS/CHORE light gate applies (lint/types where applicable, no full-suite run).

## Prep log
| Step | Date | Result |
|---|---|---|
| P.1 Frame | 2026-10-03 | TODO + question file created on `main`; type DOCS/CHORE; todo set created; repo facts (remote, workflows, manifest, pre-commit, no LICENSE) verified |
| P.1 duplicate check | 2026-10-03 | User re-supplied the instruction set (`#TODO3`). Overlap check → this file **is** the change; no second TODO created. Scope confirmed as the README + skill bundle; verbatim instruction text recorded above; `SK.md` path typo in the Acceptance signal corrected to `SKILL.md`. Still `PREPARING` — P.2 has not run. |
| P.2 Interrogate (6 questions) | 2026-10-04 | **DONE** (question file written; this Prep-log row was missing and is filled in now) — Q-1…Q-6 recorded, 12 interrogation points closed from repository evidence. Verified facts: `README.md` has **no** badges and its `Structure` tree is wrong (it lists `features/` at `:24` and `:27`, which does not exist); the badgeable CI is `.github/workflows/lint.yml`, `quality.yml` (which carries the `docs` and `migrations` jobs) and `spec-validation.yml`; no coverage upload step exists; the skill precedent is `python-best-practices` (a `.agents/skills/` skill listed nowhere in `AGENTS.md` or `userdocs/`) |
| P.3 Answer (round 1: Q-1) | 2026-10-04 | **WAITING** — **Q-1 = (a) Both**: the change ships `.agents/skills/update-readme/SKILL.md` **and** the `README.md` rewrite in one PR (the TODO's original scope). Still open: **Q-2** (sequence vs `security-changelog-license`), **Q-3** (coverage badge), **Q-4** (who fixes the `Structure` tree), **Q-5** (verbatim skill body vs +repo-protocol note), **Q-6** (listing the skill for discoverability) |
| P.3 Answer (round 2: Q-2, Q-3, Q-4, Q-5) | 2026-10-04 | **WAITING** — **Q-2 = (a)** land now, License badge later (no dependency; `security-changelog-license` must update its own README out-of-scope note). **Q-3 = (d)** Codecov is added by a **new separate change**, framed at P.1 as `codecov-coverage-badge`; this change ships no coverage badge. **Q-4 = (b)** trim the `Structure` tree + link to `AGENTS.md`. **Q-5 = (b)** verbatim skill body + a 2–3 line repo-protocol note. Only **Q-6** (listing the skill) stays open |
| P.4 Draft spec / triage / baseline / scope | | |
| P.5 Self-consistency | | n/a (DOCS/CHORE) |
