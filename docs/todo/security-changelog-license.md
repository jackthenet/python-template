# TODO: security-changelog-license

Backlog item for one planned change, created at **P.1 Frame** from this template and named `security-changelog-license.md`. One file per change.

This is a **planning record, not normative**: like `docs/questions/`, it is committed directly to `main` (see "Phase P: PREPARE" in `AGENTS.md`). It carries no approval gate — the spec does.

- **Status:** WAITING  <!-- PREPARING | QUESTIONS-ANSWERED | READY | IN-WORKFLOW | WAITING | MERGED -->
- **Change type:** DOCS/CHORE
- **Created:** 2026-10-03
- **Question file:** `docs/questions/security-changelog-license.md`
- **Spec:** n/a  <!-- DOCS/CHORE: no spec -->
- **Worktree:** <created at P.4> `../python-template_kopie-worktrees/chore/security-changelog-license`
- **Depends on:** none
- **Related specs:** none (no `docs/specs/` file is touched)

## Goal (one line)
Add the three community-facing root files the repository does not have: **`SECURITY.md`, `CHANGELOG.md` and `LICENSE`**.

## Why
`ls LICENSE* SECURITY* CHANGELOG*` → none exist, and `grep -ni "license|security|changelog" README.md` → no match either. Consequences today: (1) with **no license** the template is legally "all rights reserved by default" — GitHub shows no license, and reuse of something whose stated purpose is *"Default template for Python projects"* (`pyproject.toml:4`) is not actually granted; (2) there is **no vulnerability-disclosure channel**, while the project already runs `bandit` and `pip-audit` in CI (`.github/workflows/quality.yml`) and has previously had to fix a dependency CVE by hand (`docs/verification/anyio-cve-fix.md`); (3) there is **no user-facing change history** — the version exists (`version = "0.6.0"`, `[tool.bumpversion]` with templated bump commits) but what changed between versions lives only in `git log` and in per-spec `## Changelog` lines under `docs/specs/`, which AGENTS.md defines as the *internal process record* and which mkdocs deliberately does not publish (`mkdocs.yml`: `docs_dir: userdocs`).

## In scope
- **`LICENSE`** — full text of the chosen license with the correct copyright holder and year. The choice is the user's (MIT / Apache-2.0 / BSD-3-Clause / ISC / other), as is the holder name; P.2 records it as a question, the agent does not pick it.
- **`CHANGELOG.md`** — Keep a Changelog style (`### Added / Changed / Fixed / Removed`) with an `## [Unreleased]` section and released-version entries reconstructed **only** from evidence that exists (`git log`, the bump commits, the `docs/specs/*.md` changelog lines). No invented content.
- **`SECURITY.md`** — supported-versions table (today: a single 0.x line), how to report a vulnerability (GitHub private security advisory / a security contact — user decision), what is in and out of scope for reports (this is a template/library, not a hosted service), and the existing dependency posture (`pip-audit`, `bandit`, the `migrations`/`quality` CI jobs) stated as fact.
- Optional, decided at P.2/P.3: a short "License / Security / Changelog" pointer section in `README.md`; whether the three files are also surfaced on the docs site (that requires copies under `userdocs/`, since `mkdocs build --strict` only sees `docs_dir: userdocs`); whether `[[tool.bumpversion.files]]` gains a `CHANGELOG.md` entry so the version line stays in sync.

## Out of scope
- Any `src/`, `tests/`, `migrations/` or `docs/specs/` change.
- Changing the versioning scheme or the bump mapping in `AGENTS.md`.
- Adding CI (license header scanners, REUSE tooling, SPDX headers in source files).
- Making "every change must add a CHANGELOG entry" a **workflow rule** — that is a process change to `AGENTS.md` + skills and would be its own change (this TODO only creates the file; if the user wants the rule, P.2 splits or re-scopes).
- Legal advice or relicensing of third-party code.

## Affected features
None — root documentation only (`LICENSE`, `CHANGELOG.md`, `SECURITY.md`, optionally `README.md` / `userdocs/` / `pyproject.toml` bumpversion config).

## Constraints and risks
- **No behavior delta is the contract.** The only config file that may change is `[tool.bumpversion]` (a file entry for the changelog), and that must not alter the bump mapping or the version itself.
- **License choice is irreversible in practice** (you cannot retroactively un-grant a permissive license). It must come from the user, not from a default.
- **CHANGELOG drift.** A hand-maintained changelog goes stale the moment it exists unless a rule keeps it fed; the honest options are (a) reconstruct history + `Unreleased` only, and accept drift, or (b) pair it with the process rule (out of scope here). Record which was chosen.
- **mkdocs `--strict`.** Adding nav entries pointing at root files breaks the build (`docs_dir: userdocs`); either mirror into `userdocs/` or do not add nav.
- **Reconstruction accuracy.** Entries must be traceable to commits; a changelog that mis-attributes a release is worse than none.

## Value triage (2026-10-03, pre-workflow)
- **Overlap:** none in content — `README.md` has no license/security/changelog section, and the `docs/specs/*.md` `## Changelog` blocks are internal process records, deliberately not published. The only machinery to reuse is `bump-my-version` (version source of truth) and the existing CI security jobs, which `SECURITY.md` can cite instead of promising new tooling.
- **Beneficiary:** anyone reusing the template (license), any security reporter (channel), and anyone deciding whether to upgrade 0.5.0 → 0.6.0 (changelog).
- **Score: 4/5** — small, cheap diff with real governance and reuse value; docked one point because it adds no capability and the changelog will drift unless a follow-up rule is added.
- **Recommendation: implement** (blocked on one user decision: which license + who the copyright holder is + the disclosure channel).

## Acceptance signal (plain language)
`LICENSE`, `CHANGELOG.md` and `SECURITY.md` exist at the repo root with the user's chosen license and holder, a `Unreleased` section plus reconstructed released entries, and a concrete reporting path; `uv run mkdocs build --strict` and `uv run python scripts/check_traceability.py` still pass; `git diff --name-status` lists only those paths (plus at most `README.md` / `userdocs/` / the bumpversion file entry) and **no** `src/` or `tests/` path — so the DOCS/CHORE light gate applies.

## Prep log
| Step | Date | Result |
|---|---|---|
| P.1 Frame | 2026-10-03 | TODO + question file created on `main`; type DOCS/CHORE; todo set created; **value triage 4/5, implement** |
| P.2 Interrogate (10 questions) | 2026-10-03 | **BLOCKED-USER** — 10 questions needing user input, 9 points closed from evidence. **Not fast-path** (verified against `AGENTS.md:1078`/`:1083`: three new files ≈ 200+ lines is far over the ≤ 2-line bound), so the DOCS/CHORE path runs: Phase P → Phase 4 → Phase 5 lint/types → light review → PR, no version bump. Evidence: `pyproject.toml:3-7` has no `license`, no authors, no classifiers (GitHub shows "No license"); `[tool.bumpversion]` has exactly one `files` entry (`pyproject.toml:87-90`); `mkdocs.yml` has no `nav`, so a relative link from `userdocs/` to a root file would break `--strict`; 10 releases exist in bump commits (`31d2a1a`…`3c90e6f`, 2026-09-12…2026-10-02) but `git tag` is empty. **Collisions:** `update-readme` already owns `README.md` incl. its License section (`update-readme.md:41,58,84,87`) — this change must not write README; `pyproject-tooling-gaps` lists `pyproject.toml` + `README.md` (`pyproject-tooling-gaps.md:51`) — collides only if the pyproject-metadata option is taken. **Note:** Q-3's GitHub private-vulnerability-reporting toggle is a repo setting only the user can enable (outside the PR) |
| P.3 Answer (<n> answered) | | |
| P.4 Draft scope + create branch/worktree | | |
| P.5 Self-consistency | | n/a (DOCS/CHORE) |
