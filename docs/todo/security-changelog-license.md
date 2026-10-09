# TODO: security-changelog-license

Backlog item for one planned change, created at **P.1 Frame** from this template and named `security-changelog-license.md`. One file per change.

This is a **planning record, not normative**: like `docs/questions/`, it is committed directly to `main` (see "Phase P: PREPARE" in `AGENTS.md`). It carries no approval gate — the spec does.

- **Status:** READY  <!-- PREPARING | QUESTIONS-ANSWERED | READY | IN-WORKFLOW | WAITING | MERGED -->
- **Change type:** DOCS/CHORE
- **Created:** 2026-10-03
- **Question file:** `docs/questions/security-changelog-license.md`
- **Spec:** n/a  <!-- DOCS/CHORE: no spec -->
- **Worktree:** <created at P.4> `../python-template_kopie-worktrees/chore/security-changelog-license`
- **Depends on:** `update-readme` (it creates the `README.md` badge row this change adds the License badge to), and the `AGENTS.md`/skills docs changes — **Q-7 = (b)** puts a changelog rule into `AGENTS.md` + skills, so land after `workflow-docs-nits` → `value-triage-gate` → `architecture-tests-missing` → `spec-interview-protocol`. This change must merge **before** `pyproject-tooling-gaps` (both touch `pyproject.toml`, Q-4 = (a)).
- **Related specs:** none (no `docs/specs/` file is touched)

## Goal (one line)
Add the three community-facing root files the repository does not have: **`SECURITY.md`, `CHANGELOG.md` and `LICENSE`**.

## Why
`ls LICENSE* SECURITY* CHANGELOG*` → none exist, and `grep -ni "license|security|changelog" README.md` → no match either. Consequences today: (1) with **no license** the template is legally "all rights reserved by default" — GitHub shows no license, and reuse of something whose stated purpose is *"Default template for Python projects"* (`pyproject.toml:4`) is not actually granted; (2) there is **no vulnerability-disclosure channel**, while the project already runs `bandit` and `pip-audit` in CI (`.github/workflows/quality.yml`) and has previously had to fix a dependency CVE by hand (`docs/verification/anyio-cve-fix.md`); (3) there is **no user-facing change history** — the version exists (`version = "0.6.0"`, `[tool.bumpversion]` with templated bump commits) but what changed between versions lives only in `git log` and in per-spec `## Changelog` lines under `docs/specs/`, which AGENTS.md defines as the *internal process record* and which mkdocs deliberately does not publish (`mkdocs.yml`: `docs_dir: userdocs`).

## In scope
- **`LICENSE`** — full text of the chosen license with the correct copyright holder and year. The choice is the user's (MIT / Apache-2.0 / BSD-3-Clause / ISC / other), as is the holder name; P.2 records it as a question, the agent does not pick it.
- **`CHANGELOG.md`** — Keep a Changelog style (`### Added / Changed / Fixed / Removed`) with an `## [Unreleased]` section and released-version entries reconstructed **only** from evidence that exists (`git log`, the bump commits, the `docs/specs/*.md` changelog lines). No invented content.
- **`SECURITY.md`** — supported-versions table (today: a single 0.x line), how to report a vulnerability (GitHub private security advisory / a security contact — user decision), what is in and out of scope for reports (this is a template/library, not a hosted service), and the existing dependency posture (`pip-audit`, `bandit`, the `migrations`/`quality` CI jobs) stated as fact.
- **`pyproject.toml` metadata** — **Q-4 = (a):** `license = "MIT"` (PEP 639 SPDX string) and `authors = [{ name = "jackthenet" }]` in `[project]`; no deprecated `License :: OSI Approved ::` classifier. Still no behavior delta (there is no `[build-system]` table and no publish workflow, so the fields are inert metadata).
- **Changelog process rule** — **Q-7 = (b):** the 'every change adds a `CHANGELOG.md` entry' rule is added **in this change** to `AGENTS.md` (Phase 5/6 and the Versioning section) and the affected skills. This widens the diff beyond the three root files and is what makes `AGENTS.md`/`.agents/skills/` in scope.
- **`README.md` License badge** — **Q-9, settled by `update-readme` Q-2 = (a):** once `LICENSE` exists, this change adds the License badge to the badge row `update-readme` created. This **reverses** the P.2 note 'this change must not write README' (`docs/todo/security-changelog-license.md:58`); the badge row must be re-read, not assumed.
- **Consequence of `update-readme` Q-2 = (a), decided 2026-10-04:** `update-readme` lands **first** and ships **no** License badge (its skill rule forbids a badge with nothing behind it). Once `LICENSE` exists, **this** change adds the License badge to the `README.md` badge row — which **reverses** the P.2 collision note "this change must not write README" (`docs/todo/security-changelog-license.md:58`). The badge edit must re-read the badge row `update-readme` created.

## Out of scope
- Any `src/`, `tests/`, `migrations/` or `docs/specs/` change.
- Changing the versioning scheme or the bump mapping in `AGENTS.md`.
- Adding CI (license header scanners, REUSE tooling, SPDX headers in source files).
- ~~Making "every change must add a CHANGELOG entry" a **workflow rule**~~ — **superseded by Q-7 = (b): the rule IS in scope** (`AGENTS.md` Phase 5/6 + Versioning + skills).
- ~~Surfacing the files on the mkdocs site~~ — **Q-8 = (a): root files only**, nothing under `userdocs/`, no nav entry, `mkdocs build --strict` untouched.
- ~~`bump-my-version` maintaining `CHANGELOG.md`~~ — **Q-6 = (a): hand-maintained**, no `[[tool.bumpversion.files]]` entry; the Phase 6 agent appends the release section next to the bump commit.
- Legal advice or relicensing of third-party code.

## Affected features
None — root documentation only (`LICENSE`, `CHANGELOG.md`, `SECURITY.md`, optionally `README.md` / `userdocs/` / `pyproject.toml` bumpversion config).

## Constraints and risks
- **No behavior delta is the contract.** The only config file that may change is `[tool.bumpversion]` (a file entry for the changelog), and that must not alter the bump mapping or the version itself.
- **License choice is irreversible in practice** (you cannot retroactively un-grant a permissive license). It must come from the user, not from a default.
- **CHANGELOG drift.** Resolved by **Q-7 = (b)**: the feeding rule ships in this change (`AGENTS.md` Phase 5/6 + Versioning + skills), so the changelog is not left to drift. Cost: the diff now touches the workflow contract, so it must land after the other `AGENTS.md`/skills changes.
- **mkdocs `--strict`.** Adding nav entries pointing at root files breaks the build (`docs_dir: userdocs`); either mirror into `userdocs/` or do not add nav.
- **Reconstruction accuracy.** Entries must be traceable to commits; a changelog that mis-attributes a release is worse than none.

## Value triage (2026-10-03, pre-workflow)
- **Overlap:** none in content — `README.md` has no license/security/changelog section, and the `docs/specs/*.md` `## Changelog` blocks are internal process records, deliberately not published. The only machinery to reuse is `bump-my-version` (version source of truth) and the existing CI security jobs, which `SECURITY.md` can cite instead of promising new tooling.
- **Beneficiary:** anyone reusing the template (license), any security reporter (channel), and anyone deciding whether to upgrade 0.5.0 → 0.6.0 (changelog).
- **Score: 4/5** — small, cheap diff with real governance and reuse value; docked one point because it adds no capability and the changelog will drift unless a follow-up rule is added.
- **Recommendation: implement** (blocked on one user decision: which license + who the copyright holder is + the disclosure channel).

## Acceptance signal (plain language)
`LICENSE`, `CHANGELOG.md` and `SECURITY.md` exist at the repo root with the MIT text and `Copyright (c) 2026 jackthenet`, a `Unreleased` section plus all 10 reconstructed released entries, and GitHub private vulnerability reporting as the named channel; `pyproject.toml` carries `license` + `authors`; `AGENTS.md` + the skills name the changelog step; the README badge row gains a License badge. `uv run mkdocs build --strict` and `uv run python scripts/check_traceability.py` still pass; `git diff --name-status` lists only those paths and **no** `src/` or `tests/` path — so the DOCS/CHORE light gate applies.

## Prep log
| Step | Date | Result |
|---|---|---|
| P.1 Frame | 2026-10-03 | TODO + question file created on `main`; type DOCS/CHORE; todo set created; **value triage 4/5, implement** |
| P.2 Interrogate (10 questions) | 2026-10-03 | **BLOCKED-USER** — 10 questions needing user input, 9 points closed from evidence. **Not fast-path** (verified against `AGENTS.md:1078`/`:1083`: three new files ≈ 200+ lines is far over the ≤ 2-line bound), so the DOCS/CHORE path runs: Phase P → Phase 4 → Phase 5 lint/types → light review → PR, no version bump. Evidence: `pyproject.toml:3-7` has no `license`, no authors, no classifiers (GitHub shows "No license"); `[tool.bumpversion]` has exactly one `files` entry (`pyproject.toml:87-90`); `mkdocs.yml` has no `nav`, so a relative link from `userdocs/` to a root file would break `--strict`; 10 releases exist in bump commits (`31d2a1a`…`3c90e6f`, 2026-09-12…2026-10-02) but `git tag` is empty. **Collisions:** `update-readme` already owns `README.md` incl. its License section (`update-readme.md:41,58,84,87`) — this change must not write README; `pyproject-tooling-gaps` lists `pyproject.toml` + `README.md` (`pyproject-tooling-gaps.md:51`) — collides only if the pyproject-metadata option is taken. **Note:** Q-3's GitHub private-vulnerability-reporting toggle is a repo setting only the user can enable (outside the PR) |
| P.3 Answer (10 answered) | 2026-10-04 | **ALL ANSWERED** (2 rounds). **Q-1 MIT.** **Q-2 `Copyright (c) 2026 jackthenet`** — the GitHub handle, chosen over the recommended legal name (the user's explicit decision). **Q-3** GitHub private vulnerability reporting (no email; the repo setting is a user action outside the PR), latest release only supported, acknowledge ≤ 14 days with no fix SLA, explicit template-scope paragraph, posture stated as fact (`pip-audit` + `bandit` at `quality.yml:28-43`, `dependency-review` at `:61`). **Q-4 (a)** `pyproject.toml` gains `license` + `authors` → this change must merge **before** `pyproject-tooling-gaps`. **Q-5** Keep a Changelog + SemVer + `## [Unreleased]`, **all 10 releases** backfilled from the dated bump commits (`31d2a1a` … `3c90e6f`; no git tags exist), untraceable entries get a `see <range>` pointer. **Q-6 (a)** hand-maintained, no bumpversion entry. **Q-7 (b)** the changelog rule is added **here** to `AGENTS.md` + skills — the diff is no longer 3 files, so `AGENTS.md`/`.agents/skills/` join the collision set. **Q-8 (a)** root files only, no site presence. **Q-9** settled by `update-readme` Q-2 = (a): this change adds the License badge to the badge row that change creates. **Q-10** run the DOCS/CHORE workflow (no `--skip-spec`). Not fast-path: three new files plus a workflow-rule edit |
| P.4 Draft scope + create branch/worktree | | |
| P.5 Self-consistency | | n/a (DOCS/CHORE) |
