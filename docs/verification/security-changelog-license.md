# Verification: security-changelog-license

- **Type:** DOCS/CHORE
- **Change:** `security-changelog-license` (branch `chore/security-changelog-license`, worktree `../python-template_kopie-worktrees/chore/security-changelog-license`)
- **Date:** 2026-10-10 (P.4 Draft)
- **Spec:** n/a — DOCS/CHORE produces no specification and no approval PR (Phase Matrix)
- **P.5 (self-consistency):** **n/a for this type** — the specify skill runs P.5 for FEATURE/CROSS-CUTTING only. The **READY gate** for this change is the **verified P.4 artifact** (this scope record), per AGENTS.md "Phase P atomic steps" P.5 row and the specify skill's Rules ("A change is READY only when every question … is ANSWERED and the P.4 artifact exists").
- **Question file:** `docs/questions/security-changelog-license.md` — **Q-1 … Q-10 all ANSWERED** (2 rounds). This record cites the question file's own numbering; the orchestrator's launch prompt compressed it to "Q-1 … Q-8" — the mapping is: prompt Q-1 = file Q-1+Q-2, Q-2 = Q-3, Q-3 = Q-4, Q-4 = Q-5+Q-6, Q-5 = Q-7, Q-6 = Q-8, Q-7/Q-8 = Q-9 (+Q-10 workflow confirmation).

## 1. Corrected facts (re-derived on current `main` at P.4 — the P.2 evidence in the question file is stale)

Every number below was re-measured in this worktree at branch head `50a4420`; where it differs from the question file / TODO, the value here is authoritative for Phase 4.

| Fact | P.2 / TODO value | **Measured now** | Evidence |
|---|---|---|---|
| Project version | `0.6.0` | **`1.1.0`** | `pyproject.toml:4` `version = "1.1.0"`, `[tool.bumpversion] current_version = "1.1.0"` (`:85`) |
| Released versions to backfill | 10 (`31d2a1a`…`3c90e6f`) | **14 entries: `0.1.0` + 13 bump commits** (`0.1.0 … 1.1.0`) | `git log --oneline --grep="Bump version"` → 13 bumps (see §3.3 table) |
| Git tags | none | **none** (still) | `git tag` → empty → release dates come from the bump commits |
| `pyproject.toml` `license` / `authors` / `classifiers` | absent | **still absent** — `grep -ni "license\|authors\|classifiers" pyproject.toml` → no match | `[project]` = name, version, description, readme, requires-python, dependencies (`pyproject.toml:3-25`) |
| `[build-system]` | absent | **still absent** — `grep -n "build-system" pyproject.toml` → no match | uv therefore uses the default setuptools backend; see §5 for the PEP 639 smoke-test |
| `LICENSE`, `SECURITY.md`, `CHANGELOG.md` | absent | **still absent at the repository root** | `ls LICENSE SECURITY.md CHANGELOG.md` → "No such file or directory" (also no `CONTRIBUTING.md`) |
| `README.md` badge row | did not exist (P.2) | **exists — `README.md:3-9`**, 7 badges (Quality, Lint, Spec Validation, Python, Ruff, uv, pre-commit) | `update-readme` merged and its records are archived (`f208aad chore(update-readme): archive MERGED`) |
| README License/Security/Changelog prose | — | **none** — `grep -ni "license\|changelog" README.md` → no match; "security" appears only as a CI-job word (`:17`, `:64`, `:76`) | the License badge is the only README edit in scope (Q-9 as settled) |
| `AGENTS.md` anchors (line numbers moved) | `AGENTS.md:1077-1083` etc. | **locate by content, not line number** (file is now 1187 lines): `### Phase 5: VERIFY` (item 16 = the DOCS/CHORE line), `### Phase 6: REVIEW` (items 10–11), `## Versioning` (the bullet list ending with "**Dry run:**") | `grep -n "^### Phase 5: VERIFY\|^### Phase 6: REVIEW\|^## Versioning" AGENTS.md` |
| `pyproject-tooling-gaps` (the merge-order constraint "merge before it") | PREPARING | **already MERGED** — `3686554 chore(pyproject-tooling-gaps): archive MERGED`, merged as PR #68 (`refactor/pyproject-tooling-gaps`) inside the `0.6.1 → 1.0.0` range | the "must merge before" constraint is **vacated** (§7) |
| `chore/spec-interview-protocol` (the merge-order constraint "merge after it") | — | **open, PR #77**, TODO `Status: WAITING` (head commit `50a4420`) | `git diff --name-status main...chore/spec-interview-protocol` → `AGENTS.md`, `.agents/skills/specify/SKILL.md`, `docs/questions/template.md`, `docs/specs/template.md`, `docs/verification/spec-interview-protocol.md`, `docs/workflow/PROBLEMS.md` |
| `make_map.py --check` on `main` | — | **already exits 1 (pre-existing)** — the committed `STRUCTURE.md` says `docs/ — 220 files` (`STRUCTURE.md:449`) but `git ls-files docs \| wc -l` = **222**; the primary worktree is clean (`git status --porcelain` empty) | the two planning-record commits under `docs/todo/` + `docs/questions/` are committed directly to `main` without a map regeneration — see §6 finding F-1 |

## 2. Scope summary (the exact file list Phase 4 may touch)

| # | File | Action | Authorised by |
|---|---|---|---|
| 1 | `LICENSE` | **create** (MIT text, `Copyright (c) 2026 jackthenet`) | Q-1, Q-2 |
| 2 | `SECURITY.md` | **create** (channel, supported versions, 14-day acknowledgement, template-scope paragraph, posture as fact) | Q-3 |
| 3 | `CHANGELOG.md` | **create** (Keep a Changelog + `## [Unreleased]` + 14 backfilled releases) | Q-5, Q-6 |
| 4 | `pyproject.toml` | **edit** — `license = "MIT"` + `authors = [{ name = "jackthenet" }]` in `[project]` | Q-4 |
| 5 | `AGENTS.md` | **edit** — the changelog-entry rule in the Phase 5/Phase 6 area and in `## Versioning` | Q-7 |
| 6 | `.agents/skills/implement/SKILL.md`, `.agents/skills/verify/SKILL.md`, `.agents/skills/review/SKILL.md` | **edit** — the same rule at the step level | Q-7 |
| 7 | `README.md` | **edit** — one License badge line in the existing badge row (`README.md:3-9`) | Q-9 (as settled by `update-readme` Q-2 = (a)) |
| 8 | `STRUCTURE.md` | **regenerate** (generated artifact, not hand-edited) — see finding **F-1**; flagged to the orchestrator | AGENTS.md "Structure Map" rule + `test_ac_021_committed_map_matches_fresh_render` |

Nothing else. Phase 4 writes **no** `src/`, `tests/`, `scripts/`, `migrations/`, `docs/specs/` file, and no test.

## 3. File-by-file scope with the planned text

### 3.1 `LICENSE` (new) — Q-1 (MIT), Q-2 (`Copyright (c) 2026 jackthenet`)

The full MIT License text, exactly this, nothing added (the copyright holder is the GitHub handle — the user's explicit decision over the recommended legal name; do **not** substitute a legal name in Phase 4):

```text
MIT License

Copyright (c) 2026 jackthenet

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

Single year `2026` (the repository's first year, `bda69ed` 2026-08-16); no year range (Q-2). File must be newline-terminated with no trailing whitespace (`.pre-commit-config.yaml` `trailing-whitespace` / `end-of-file-fixer`).

### 3.2 `SECURITY.md` (new) — Q-3

Five sections, all content either a user decision (Q-3) or a measured fact from this repository — no promises beyond what exists:

1. **Reporting channel — GitHub private vulnerability reporting.** "Report it through the repository's **Security** tab → *Report a vulnerability* (GitHub private vulnerability reporting). Do not open a public issue." **No email address is published.** Plus one honest sentence: the channel depends on the repository setting being enabled on GitHub, which is outside this PR (the user action; recorded in §6 F-2).
2. **Supported versions** — a two-column table with exactly one supported row:

   | Version | Supported |
   |---|---|
   | latest release (currently `1.1.0`) | ✅ |
   | anything older | ❌ |

   (Q-3: latest release only. The `1.1.0` parenthetical is the version measured in §1 and is the only value that goes stale; it is a snapshot, not a promise.)
3. **Response** — "We aim to **acknowledge** a report within **14 days**. There is **no fix SLA**: whether and when a fix ships is our call, and a report does not obligate a fix." (Q-3.)
4. **Template-scope paragraph** — "This repository is a **template / library scaffold**, not a hosted service. Reports about code you forked or vendored, about the example wiring in `src/main.py`, or about a deployment you built on top of the template are **out of scope** — fix those in your own project, and carry your own security policy. What is in scope: a vulnerability in the template's own shipped code (`src/backend/`) or in its default configuration as committed here." (Q-3.)
5. **Posture, stated as fact** (no new tooling promised) — the `security` job of `.github/workflows/quality.yml` runs `uv run pip-audit` (quality.yml:42-43) and `uv run bandit -r src/` (:44-45); the `dependency-review` job runs `actions/dependency-review-action@v5` on pull requests only (quality.yml:63-80); `.github/dependabot.yml` opens weekly `uv` and `github-actions` update PRs (`interval: "weekly"`, :4-7 and :39-42); a real dependency CVE has been fixed through this process (`docs/verification/anyio-cve-fix.md`, PR #48).

### 3.3 `CHANGELOG.md` (new) — Q-5 (Keep a Changelog + SemVer + `## [Unreleased]`, backfill every release), Q-6 (hand-maintained)

Structure (Keep a Changelog style, one section per released version, newest first):

```markdown
# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.1.0] - 2026-10-09
### Added
...
```

Sub-headings used: `### Added`, `### Changed`, `### Fixed`, `### Removed` — only the ones a release actually needs.

**Release mapping (derived at P.4 — 14 entries, not the 10 the P.2 record lists; there are no git tags, so the bump commit is the release marker and its author date is the release date):**

| Version | Release marker | Date (`git log -1 --format=%ad --date=short`) | Content range | Traceable headline evidence |
|---|---|---|---|---|
| `0.1.0` | `e9fd8c1` *Add the first iteration* (the commit that set `version = "0.1.0"`; there is no bump commit for it) | 2026-08-16 | `bda69ed`..`e9fd8c1` | the initial template (`bda69ed` Initial commit) |
| `0.2.0` | `31d2a1a` | 2026-09-12 | `e9fd8c1`..`31d2a1a` (146 commits) | PRs #1–#21 — settings feature + coverage (#16), `bump-my-version` (#17), workflow/tooling chores (#18–#21) |
| `0.3.0` | `50344bc` | 2026-09-14 | `31d2a1a`..`50344bc` | PRs #22–#23 — mail-service feature |
| `0.3.1` | `8a2f931` | 2026-09-15 | `50344bc`..`8a2f931` | PR #25 (file-management start), file-management spec (#24), `settings-test-isolation` ISSUE fix |
| `0.4.0` | `7290f94` | 2026-09-19 | `8a2f931`..`7290f94` | session-management feature T-001…T-009; dependabot bumps (PRs #29–#36) |
| `0.4.1` | `8ae9978` | 2026-09-20 | `7290f94`..`8ae9978` | PRs #38–#40 — session-management completion, dependency-updates refactor |
| `0.4.2` | `1646862` | 2026-09-21 | `8ae9978`..`1646862` | PRs #41–#45 — `hanging-observability-test` fix, dependency bumps |
| `0.4.3` | `78475af` | 2026-09-21 | `1646862`..`78475af` | PRs #46–#48 — dev-tooling wiring, env-aware perf budget, **anyio CVE fix** |
| `0.5.0` | `6d6f120` | 2026-09-24 | `78475af`..`6d6f120` | PRs #49–#50 — workflow docs / CI timing, bandit assert fix |
| `0.5.1` | `c6fd876` | 2026-10-02 | `6d6f120`..`c6fd876` | PRs #51–#57 — user-roles-permissions (crosscut), search (start), dependabot groups |
| `0.6.0` | `3c90e6f` | 2026-10-02 | `c6fd876`..`3c90e6f` | PR #58 (`main-ci-green`) + the search feature's final work (spec v3, CI remediation) |
| `0.6.1` | `df81d8b` | 2026-10-04 | `3c90e6f`..`df81d8b` | PRs #54, #59–#62 — search merge, workflow optimisation, repo hygiene, prepared-workflow, remove-spec-tdd-driver |
| `1.0.0` | `137b7e9` | 2026-10-07 | `df81d8b`..`137b7e9` (200 commits) | PRs #67–#73 — structlog-logging (crosscut), pyproject-tooling-gaps, structure-map, value-triage-gate, settings-public-registry-setter; the 1.0.0 milestone itself is the `### Changed` note |
| `1.1.0` | `744eea1` | 2026-10-09 | `137b7e9`..`744eea1` | PR #74 — structlog-logging follow-up |

**`## [Unreleased]` content.** Seeded with what merged **after** `744eea1` and is user-observable: PR #76 (`chore/ruff-d-docstrings` — ruff `D` docstring gate over `src/`). PR #75 (`feature/structure-map`) is **not** repeated — its commits are already inside the `1.1.0` range and it is credited there once (double-crediting across a release boundary is the classic backfill error). Everything merged later is fed by the rule added in §3.5.

**Pointer rule (Q-5).** Where a release's content cannot be traced to a commit/PR in its range, the entry is a single line `- See <range-start>…<range-end> for the full change list.` — **never** invented prose. Measured at P.4: **all 14 ranges have traceable headline content** (evidence column above), so **no release is expected to carry a pointer**; if Phase 4 cannot trace a headline for some range, that range gets the pointer and §8 records it.

### 3.4 `pyproject.toml` (edit) — Q-4 = (a)

Two keys added to the existing `[project]` table, after `description` / `readme` (the exact insertion point Phase 4 should use keeps the metadata block together):

```toml
license = "MIT"
authors = [{ name = "jackthenet" }]
```

Explicitly **not** part of this file's scope:

- **no** `License :: OSI Approved :: MIT License` classifier — deprecated by PEP 639 (Q-4); the file has **no** `classifiers` key at all today and gains none.
- **no** `[tool.bumpversion]` change — **no** `[[tool.bumpversion.files]]` entry for `CHANGELOG.md` (Q-6 = (a)); the existing single entry (`pyproject.toml:92-95`) stays exactly as it is.
- **no** version change — `version = "1.1.0"` (`:4`) and `current_version = "1.1.0"` (`:85`) are untouched (DOCS/CHORE → no bump, AGENTS.md "Versioning" bump mapping).
- no `[build-system]` table is added (there is none today and adding one would be a behavior change).

### 3.5 `AGENTS.md` (edit) — Q-7 = (b): the changelog rule ships in this change

Locate the anchors **by content** (line numbers moved; see §1). Current structure, verified at P.4: the Phase 6 list runs **1–11**, with item **9** = "document reusable shared capabilities in `AGENTS.md`", item **10** = "bump the version per the change type", item **11** = "open a PR"; the `## Versioning` bullets run **Install / Bump mapping / When / Tagging / Dry run**. Two insertions:

**(a) Phase 6: REVIEW list** — insert a new item between item 9 ("document reusable shared capabilities") and the bump item, and extend the bump item. Planned text, verbatim:

```markdown
10. **When the review report is clean, add the change's `CHANGELOG.md` entry** — append it under `## [Unreleased]` in the root `CHANGELOG.md` (Keep a Changelog headings: `Added` / `Changed` / `Fixed` / `Removed`). Every change type writes one, REFACTOR and DOCS/CHORE included (usually under `Changed`). One line per user-observable change, traced to what this change actually did — never invented prose. The entry is part of the reviewed PR.
```

and, inside the existing bump item, after "the bump commit is part of the PR.":

```markdown
When a bump is made, move the `## [Unreleased]` entries into a new `## [<new version>] - <YYYY-MM-DD>` section in the same commit as the bump (`CHANGELOG.md` is hand-maintained — `bump-my-version` does not touch it).
```

(The old items 10 and 11 are renumbered to 11 and 12; the Phase 6 list is the only numbered list touched.)

**(b) `## Versioning` section** — add one bullet **after the `- **When:**` bullet** (before `- **Tagging:**`). Planned text, verbatim:

```markdown
- **Changelog:** the root `CHANGELOG.md` is hand-maintained (no `[[tool.bumpversion.files]]` entry): every change adds an entry under `## [Unreleased]` in Phase 6, and the agent that makes a bump moves those entries into a new `## [<new version>] - <YYYY-MM-DD>` section in the bump commit. Changes with no bump (REFACTOR, DOCS/CHORE) leave their entries under `## [Unreleased]` until the next bumped release.
```

No other `AGENTS.md` text is touched — the bump mapping table, the fast-path section, the Phase Matrix and the prohibitions/obligations lists stay as they are.

### 3.6 `.agents/skills/` (edit) — Q-7 = (b), exactly three skill files

| Skill file | Anchor (verified at P.4) | What it gains |
|---|---|---|
| `.agents/skills/implement/SKILL.md` | `### S4.5 Commit + update status` (`:76`) and Process `### 7. Commit & update status — FEATURE/CROSS-CUTTING` (`:114`) | One clause: the change's `CHANGELOG.md` entry under `## [Unreleased]` is committed with the change (AGENTS.md "Versioning"). |
| `.agents/skills/verify/SKILL.md` | `## MUST` → `### All types` (`:112`); the `### DOCS/CHORE` list (`:107-110`) already says "Confirm no test files or behavior were touched" | One check: confirm the change's `CHANGELOG.md` entry exists under `## [Unreleased]` (every change type owes one) and record it in the verification report. |
| `.agents/skills/review/SKILL.md` | `## MUST` (`:85`, DOCS/CHORE line `:98`) and `### S6.4 Bump version + open PR` (`:78`) | One check: a change that ships without a `CHANGELOG.md` entry is a finding; and in S6.4's done-criteria: on a bump, the `## [Unreleased]` entries move into the new `## [<new version>] - <date>` section in the bump commit. |

No other skill is touched (`specify`, `decompose`, `test`, `git`, `code-structure-map`, `python-best-practices`, `update-readme` are out of scope — the rule lives at the commit/verify/review steps, not at planning or decomposition time).

### 3.7 `README.md` (edit) — Q-9 as settled

One line appended to the existing badge row (`README.md:3-9`, currently 7 badges), after the `pre-commit` badge:

```markdown
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
```

That is the **only** README edit: no new README section, no prose about security or the changelog (the badge is backed by the `LICENSE` file this same change creates, which is what the `update-readme` skill's "badges only for things that really exist" rule requires — the reason `update-readme` shipped without it).

### 3.8 `STRUCTURE.md` (regenerate) — finding **F-1**, flagged to the orchestrator

The launch prompt put `STRUCTURE.md` out of scope. Measured, it cannot stay out:

- `make_map.py` renders **top-level files by name** (REQ-009 / AC-009) — the committed map's tree starts `.editorconfig`, `.gitignore`, `.pre-commit-config.yaml`, `AGENTS.md`, `README.md`, `STRUCTURE.md`, `alembic.ini`, `mkdocs.yml`, `pyproject.toml`, `uv.lock` (`STRUCTURE.md:7-16`) — so creating `LICENSE`, `SECURITY.md` and `CHANGELOG.md` at the root makes the map stale by three lines.
- `tests/acceptance/test_structure_map.py::test_ac_021_committed_map_matches_fresh_render` (`:1468`) asserts the committed map is a byte-exact fresh render. The `structure-map-check` pre-commit hook would **not** catch it (its `files:` filter is `\.py$`, `.pre-commit-config.yaml:33-39`), but the acceptance test runs in the suite and in CI, so the staleness is caught there.
- **The map is already stale on `main`** (exit 1, §1): `docs/ — 220 files` vs 222 tracked files, because the `docs/todo/` + `docs/questions/` planning-record commits go directly to `main` without a regeneration. So this is a pre-existing condition, not something this change creates — but this change would add three more stale lines to it.

**Decision recorded here (Phase 4 executes it):** regenerate with `uv run python scripts/make_map.py` **inside the change worktree** and commit the regenerated `STRUCTURE.md` with the change. It is a generated artifact (never hand-edited, AGENTS.md "Structure Map"), it carries no behavior, and one command keeps the acceptance test and the hook honest. The regeneration also absorbs the pre-existing `docs/` count drift — recorded, not hidden. If the orchestrator rejects this, Phase 4 must leave `STRUCTURE.md` untouched and Phase 5 must record `test_ac_021_committed_map_matches_fresh_render` as a **known, pre-existing failure with three new causes**, which is the worse outcome.

## 4. Explicitly NOT in scope

Any edit to, or creation of:

- `src/**`, `tests/**`, `scripts/**`, `migrations/**` — no source, no test, no fixture, no conftest change.
- `docs/specs/**`, `docs/decisions/**`, `docs/tasks/**`, `docs/verification/traceability.md` — no spec, no ADR, no traceability row (no spec mentions `LICENSE`, `SECURITY.md`, `CHANGELOG.md` or copyright, so no spec amendment and no matrix row is owed).
- `mkdocs.yml`, `userdocs/**` — Q-8 = (a): the three files are **root-only**, no nav entry, no mirror copy under `userdocs/` (a relative link from a `userdocs/` page to a root file would break `mkdocs build --strict`, since `docs_dir: userdocs`).
- `.github/workflows/**`, `.github/dependabot.yml`, `.pre-commit-config.yaml` — no CI, no hook, no license-header scanner, no REUSE/SPDX tooling.
- `pyproject.toml` beyond the two `[project]` keys of §3.4 — **no version bump**, no `classifiers`, no `[tool.bumpversion]` change, no `[build-system]`.
- `docs/todo/**` and `docs/questions/**` — orchestrator-owned, `main`-only; this branch must not modify them (it carries the P.1–P.3 copies inherited from `main`).
- `STRUCTURE.md` is the **one** generated file that IS touched (§3.8 / F-1); every other generated artifact is untouched.
- **Enabling GitHub private vulnerability reporting** — a GitHub repository setting only the user can change; it is a **user action outside this PR**, and `SECURITY.md` says so (finding F-2).
- No version bump anywhere (DOCS/CHORE → `none` in the bump mapping), no tag, no release.

## 5. No-behavior-delta confirmation

**Claim:** nothing in this scope changes externally observable runtime behavior.

- Seven of the eight files are documentation or metadata: `LICENSE`, `SECURITY.md`, `CHANGELOG.md`, the `AGENTS.md` rule, three `SKILL.md` rule lines, one README badge line. None is imported, executed, or read at runtime.
- The rule text added to `AGENTS.md` / the skills changes what a future **agent** does, not what the **software** does — the DOCS/CHORE criterion ("documentation, comments, configuration, CI, tooling") covers it.
- **The one real risk: `pyproject.toml` is read by tooling.** Checked on this host at the current head:
  1. **Does the build/install path accept PEP 639?** Smoke-tested in a scratch project of the same shape (`[project]` with `name/version/description/readme/requires-python/license = "MIT"/authors`, **no** `[build-system]`; uv 0.11.13, CPython 3.14.5): `uv build` → **exit 0**, wheel `METADATA` gained `License-Expression: MIT` and `Author: jackthenet`; `uv sync` → **exit 0**. The default setuptools backend on this toolchain implements PEP 639, so the SPDX string cannot break the project build every `uv run` performs (uv builds the project itself — observed as `Building python-template @ file:///…` in this worktree).
  2. **Does any test or script read `pyproject.toml` metadata?** `grep -rn "pyproject" tests/ scripts/` → exactly two files:
     - `tests/contract/logging/test_dependency_contract.py` — parses the real `pyproject.toml` and reads `["project"]["dependencies"]` and `["tool"]["deptry"]["per_rule_ignores"]`. Two sibling keys cannot change either read. **Targeted guard: `uv run pytest tests/contract/logging/test_dependency_contract.py -v`.**
     - `tests/acceptance/test_structure_map.py` — uses the *name* `pyproject.toml` only inside `tmp_path` fixture trees (a 20-byte fake `[project]`), never the repository's file, so the metadata edit cannot affect it — **but** it owns `test_ac_021_committed_map_matches_fresh_render`, the test that reacts to the three new root files. **Targeted guard: `uv run pytest tests/acceptance/test_structure_map.py -v`.**
  3. **Does any runtime code read its own package metadata?** `grep -rn "importlib.metadata|pkg_resources|__version__|metadata.version" src/ tests/ scripts/` → **no match**. Nothing at runtime can observe `license` or `authors`.
  4. **Tooling that reacts to a `pyproject.toml` edit:** the `deptry` pre-commit hook (`files: ^(pyproject\.toml|…)`) and the `mkdocs-build` pre-push hook (`files: ^(mkdocs\.yml|userdocs/|pyproject\.toml)`) — gates, not behavior; both are in the Phase 5 check set (§8).
- **New root files and the map:** the only *mechanical* consequence of adding `LICENSE` / `SECURITY.md` / `CHANGELOG.md` is the generated `STRUCTURE.md` (F-1), handled by regeneration, never by hand-editing.
- **Suite impact:** no test file is created or modified, so no acceptance test can be weakened — Phase 6 still verifies that against the diff, not against this claim.

## 6. Findings from P.4 (for the orchestrator)

| ID | Finding | Disposition |
|---|---|---|
| **F-1** | `STRUCTURE.md` was listed out of scope, but the map renders root files by name and its acceptance test + pre-commit hook assert byte-exactness, so three new root files make it stale. | **Decision recorded in §3.8:** regenerate it in the change worktree (`uv run python scripts/make_map.py`) and commit it with the change. It is a generated artifact, not hand-edited. The orchestrator may override, at the cost in §3.8. |
| **F-2** | `SECURITY.md` points at GitHub private vulnerability reporting, which **only works once the repository setting is enabled on GitHub** (Security → Advanced security → Private reporting). That is a **user action outside this PR** and outside the change's scope (Q-3). | The orchestrator must tell the user to enable it after the PR merges; the file itself states the dependency in one sentence so the document is not a false promise. |
| **F-3** | The P.2 evidence in `docs/questions/security-changelog-license.md` (version `0.6.0`, 10 released versions, "no badge row in README") is **stale** on current `main`. | Corrected in §1. The question file is orchestrator-owned and **was not edited** (P.4 rule); this record is the correction of record. |
| **F-4** | The launch prompt's question numbering (`Q-1 … Q-8`) does not match the question file (`Q-1 … Q-10`). | Mapping recorded in the header. No answer is missing — all 10 are ANSWERED and incorporated. |
| **F-5** | The recorded merge-order constraint "merge **before** `pyproject-tooling-gaps`" is **vacated**: that change already merged (PR #68, archived `3686554`). | §7 restates the order that still applies. |
| **F-6** | `make_map.py --check` already exits 1 on `main` (map says `docs/ — 220 files`, 222 are tracked) because planning records are committed directly to `main` without a regeneration. Pre-existing, unrelated to this change. | Orchestrator may want a chore to regenerate; the regeneration in F-1 absorbs it on this branch. Suggested Problem Log entry (friction, not a failure of this change). |
| **F-7** | `SECURITY.md`'s supported-versions row quotes the current release (`1.1.0`), which goes stale at the next bump. | Accepted per Q-3 (latest release only). Phase 4 keeps the wording "latest release (currently `1.1.0`)" so the stale part is a parenthetical, not the rule. |

## 7. Merge order (restated against the current backlog)

- **After `chore/spec-interview-protocol`** (PR #77, open, `Status: WAITING`). Both changes edit `AGENTS.md` and `.agents/skills/`. Measured overlap: that PR touches `AGENTS.md` around the interview-protocol text plus `.agents/skills/specify/SKILL.md`, `docs/questions/template.md`, `docs/specs/template.md`; this change touches the **Phase 6 list**, the **`## Versioning`** section, and `implement` / `verify` / `review` skills — **no shared section**, so a conflict is unlikely, but the recorded order stands and Phase 4/6 rebase if git disagrees.
- **`crosscut/settings-public-registry-setter`** (in flight) also adds `AGENTS.md` text (its two "Using the …" sections). Different sections; no conflict expected. No order is required between them.
- **Before any future change that edits `pyproject.toml`** — the reason the original constraint existed. `pyproject-tooling-gaps` itself already merged, so the constraint is now only prospective (F-5).

## 8. Phase 5 check set for this change (DOCS/CHORE light tier)

Required (AGENTS.md Phase 5 DOCS/CHORE: "lint and type checks where applicable; confirm no test files or behavior were touched"), run in the change worktree:

```bash
uv run ruff check .                      # whole-repo sweep is the Phase 5 gate (matches CI)
uv run ruff format --check .
uv run mypy src/
uv run python scripts/check_traceability.py     # no matrix row is added; must stay green
uv run --group docs mkdocs build --strict       # REQUIRED: pyproject.toml is touched and the docs build reads project metadata
uv run deptry .                                 # the deptry pre-commit hook fires on pyproject.toml
uv run pytest tests/contract/logging/test_dependency_contract.py tests/acceptance/test_structure_map.py -v   # the two pyproject/map-reading guards named in §5
uv run python scripts/make_map.py --check       # after the F-1 regeneration
uv run bandit -q -r src/                        # cheap: the security job's gate, untouched by this change but it proves src/ is unchanged in effect
git diff --name-status main...HEAD              # scope proof: exactly the 8 files of §2, nothing under §4
```

Recommended (not a DOCS/CHORE gate): one full `uv run pytest tests/` at **S6.4 before the PR opens**, because `pyproject.toml` is touched and the suite is the cheapest blanket proof that the metadata edit changed nothing. Record the result in the review report.

## 9. P.4 gate statement

- The exact non-behavior changes are defined **file by file** (§2–§3), with the planned text and the authorising answer for each.
- The no-behavior-delta confirmation is recorded (§5), including the one real risk (`pyproject.toml` read by tooling) and the two named guard tests.
- The scope record exists at `docs/verification/security-changelog-license.md` and is committed as `chore(security-changelog-license): scope`.
- **No implementation file was written by this step** — no `LICENSE`, no `CHANGELOG.md`, no `SECURITY.md`, no `pyproject.toml`/`README.md`/`AGENTS.md`/skill edit, no `STRUCTURE.md` regeneration. Those are Phase 4's work (§2 is its brief).
- **P.5 does not run for DOCS/CHORE.** The READY gate for this change = this verified P.4 artifact + all questions ANSWERED. Verified at P.4: `docs/questions/security-changelog-license.md` header `**Status:** ALL ANSWERED`; entries **Q-1 … Q-10 all `ANSWERED`** (13 `ANSWERED` hits, 10 of them entry statuses); the only two `PENDING` hits are the file's own template placeholder lines (22, 24), not an entry.

## 10. Phase 4 launch brief (pass this to the S4.x subagent verbatim)

Change `security-changelog-license`, type **DOCS/CHORE**, worktree `../python-template_kopie-worktrees/chore/security-changelog-license`, branch `chore/security-changelog-license`. Read `docs/verification/security-changelog-license.md` §2–§3 and execute exactly:

1. Create `LICENSE` — MIT text verbatim from §3.1, `Copyright (c) 2026 jackthenet`, newline-terminated.
2. Create `SECURITY.md` — the five sections of §3.2 (private-vulnerability-reporting channel, no email, latest-release-only table with `1.1.0` parenthetical, 14-day acknowledgement / no fix SLA, template-scope paragraph, posture as fact with the cited line references).
3. Create `CHANGELOG.md` — Keep a Changelog header + `## [Unreleased]` (seeded per §3.3) + the 14 release sections of the §3.3 table, newest first, dates from that table, content traced to that table's evidence column; use the `see <range>` pointer only for a range that cannot be traced.
4. Edit `pyproject.toml` — add `license = "MIT"` and `authors = [{ name = "jackthenet" }]` to `[project]` (§3.4). Nothing else in the file.
5. Edit `AGENTS.md` — the two insertions of §3.5 (new Phase 6 item 10 + the bump-item sentence + renumber 10→11, 11→12; the `## Versioning` **Changelog:** bullet after **When:**).
6. Edit the three skill files per §3.6 (implement, verify, review — anchors given).
7. Edit `README.md` — append the License badge line after the `pre-commit` badge (line 9), nothing else.
8. Regenerate the map: `uv run python scripts/make_map.py` (never without `--check` in a check-only run — Problem Log P-94), then `uv run python scripts/make_map.py --check` must exit 0.
9. `uv run ruff check <changed paths>` + `uv run ruff format <changed paths>` where applicable (no `.py` file is touched, so this is a no-op gate that must still be recorded), then commit as `chore(security-changelog-license): license, security policy, changelog + metadata` (one commit, or a small series — no version bump commit).
10. Handoff `ruff` field: the result on the changed paths; `next`: Phase 5 (S5.1–S5.4 with the §8 check set).

Forbidden in Phase 4: anything in §4, any version bump, any PR, any merge, any `docs/todo/` or `docs/questions/` write.

## 11. Phase 4 — implementation (S4.x, DOCS/CHORE item 12)

Executed §10 exactly. No file outside §2's list was written; nothing in §4 was touched.

### 11.1 Files written

| File | Action | Scope source |
|---|---|---|
| `LICENSE` | new — MIT text verbatim from §3.1, `Copyright (c) 2026 jackthenet` (the user's handle, single year, no range) | §3.1 |
| `SECURITY.md` | new — the five sections of §3.2 | §3.2 |
| `CHANGELOG.md` | new — Keep a Changelog header, `## [Unreleased]`, 14 release sections | §3.3 |
| `pyproject.toml` | `license = "MIT"` + `authors = [{ name = "jackthenet" }]` added to `[project]`; nothing else | §3.4 |
| `AGENTS.md` | Phase 6 changelog item inserted (old 10→11, 11→12), bump-item sentence, `## Versioning` **Changelog:** bullet | §3.5 |
| `.agents/skills/implement/SKILL.md` | S4.5 done-criteria + Process §7 changelog clause | §3.6 |
| `.agents/skills/verify/SKILL.md` | `### All types` — confirm the `## [Unreleased]` entry exists | §3.6 |
| `.agents/skills/review/SKILL.md` | S6.4 done-criteria (move Unreleased → version section in the bump commit) + "flag a change that ships without a changelog entry" | §3.6 |
| `README.md` | one badge line appended after the `pre-commit` badge | §3.7 |
| `STRUCTURE.md` | regenerated (never hand-edited) | §3.8, F-1 |
| `docs/verification/security-changelog-license.md` | this section | — |

`.agents/skills/specify/SKILL.md` was **not** touched (decision: the rule lives at
commit/verify/review time, not at planning/decomposition time).

### 11.2 `SECURITY.md` — cited job names verified, not copied from the plan

The posture paragraph cites what the workflows actually contain, verified in the worktree:
the `security` job of `.github/workflows/quality.yml` runs `uv run pip-audit` and
`uv run bandit -r src/`; the `dependency-review` job of the **same file** runs
`actions/dependency-review-action@v5` on pull requests only. There is no
`.github/workflows/security.yml` — an earlier draft of this record named one, and the file
was checked before committing. Dependabot is weekly for the `uv` and `github-actions`
ecosystems, with four `uv` groups (`runtime-core`, `lint-and-types`, `test-tooling`,
`dev-utilities`) per `.github/dependabot.yml`. The anyio CVE fix is cited as PR #48
(`docs/verification/anyio-cve-fix.md`). No email address is published; the supported-versions
table reads "latest release (currently `1.1.0`)"; acknowledgement within 14 days, explicitly
**no fix SLA**.

**F-2 stands as a user action outside this PR:** GitHub private vulnerability reporting is a
repository setting only the user can enable; nothing in this change enables it, and
`SECURITY.md` states the dependency ("once it is enabled in the repository's Security tab")
rather than promising the channel already works.

### 11.3 `CHANGELOG.md` — backfill evidence, per release

No git tags exist (`git tag --list` is empty), so each section is dated from its
`Bump version:` commit. Every release's entries were derived from
`git log --oneline <prev-marker>..<marker>` (merge commits read with `--first-parent`, and
`git log c38e7b2^1..c38e7b2^2`-style second-parent walks to read what a delivery merge
brought in), never invented. **The `see <range>` pointer was never needed — all 14 ranges
were traceable.**

| Section | Date | Marker | Range read |
|---|---|---|---|
| `1.1.0` | 2026-10-09 | `744eea1` | `137b7e9..744eea1` |
| `1.0.0` | 2026-10-07 | `137b7e9` | `df81d8b..137b7e9` |
| `0.6.1` | 2026-10-04 | `df81d8b` | `3c90e6f..df81d8b` |
| `0.6.0` | 2026-10-02 | `3c90e6f` | `c6fd876..3c90e6f` |
| `0.5.1` | 2026-10-02 | `c6fd876` | `6d6f120..c6fd876` |
| `0.5.0` | 2026-09-24 | `6d6f120` | `78475af..6d6f120` |
| `0.4.3` | 2026-09-21 | `78475af` | `1646862..78475af` |
| `0.4.2` | 2026-09-21 | `1646862` | `8ae9978..1646862` |
| `0.4.1` | 2026-09-20 | `8ae9978` | `7290f94..8ae9978` |
| `0.4.0` | 2026-09-19 | `7290f94` | `8a2f931..7290f94` |
| `0.3.1` | 2026-09-15 | `8a2f931` | `50344bc..8a2f931` |
| `0.3.0` | 2026-09-14 | `50344bc` | `31d2a1a..50344bc` |
| `0.2.0` | 2026-09-12 | `31d2a1a` | `e9fd8c1..31d2a1a` |
| `0.1.0` | 2026-08-16 | `e9fd8c1` (the commit that set `0.1.0`; `bda69ed` is the empty initial commit) | `git ls-tree -r e9fd8c1` + `git show e9fd8c1:pyproject.toml` |

Backfill rules applied:

- **A PR is credited in exactly one section.** PR #75 (`feature/structure-map`) appears only
  inside `1.1.0`; it is not repeated under `## [Unreleased]`. `## [Unreleased]` is seeded
  with PR #76 (`chore/ruff-d-docstrings`, the ruff `D` docstring gate over `src/`).
- A change whose **implementation** landed in one release but whose **delivery merge** landed
  in the next is credited once, in the release holding the implementation, with the merge
  named in the other section (e.g. the anyio fix under `0.4.2`, its merge PR #48 under
  `0.4.3`; `structlog-logging` under `1.0.0`, its merge PR #74 under `1.1.0`).
- The `0.1.0` entry was corrected against the tree at `e9fd8c1` (20 tracked files,
  `src/core/logging/`, no `docs/specs/`, no alembic, no deptry) after an initial draft
  described the later template shape — the draft was wrong and was replaced, not kept.

### 11.4 Gates run in the change worktree

| Gate | Command | Result |
|---|---|---|
| ruff (changed paths) | `uv run ruff check <changed paths>` | **no-op — no `.py` file is touched.** Passing `LICENSE` explicitly makes ruff parse it as Python and report 123 bogus syntax errors; that is an artifact of naming an extensionless file on the command line, not a lint failure. |
| ruff (repo, recorded for information) | `uv run ruff check .` | `All checks passed!` exit 0 — the directory walk skips `LICENSE`, so the new root files cannot add lint errors. |
| structure map check | `uv run python scripts/make_map.py --check` | exit **0** (after `uv run python scripts/make_map.py` regenerated it; the pre-regeneration `--check` exited 1, as predicted by F-1) |
| guard test 1 | `uv run pytest tests/acceptance/test_structure_map.py -q` | **31 passed** — fully GREEN, including `test_ac_021_committed_map_matches_fresh_render`, which fails on `main` (F-6) |
| guard test 2 | `uv run pytest tests/contract/logging/test_dependency_contract.py -q` | **2 passed** |
| whitespace / newlines | `git diff --check` exit 0; 0 trailing-whitespace lines in `LICENSE`/`SECURITY.md`/`CHANGELOG.md`; every new file ends with `\n`; index EOL is `i/lf` for every touched tracked file | clean |
| package metadata still builds | the `uv run …` calls above build the project (`Built python-template @ file:///…`) with `license`/`authors` present | exit 0 — the PEP 639 metadata keys do not break the default setuptools backend |

**F-6 absorbed, not hidden:** the regeneration also picked up the pre-existing `docs/`
file-count drift on `main` (the committed map said 220 files, 222 are tracked, because
planning records are committed directly to `main` without regenerating the map). The
`STRUCTURE.md` diff on this branch therefore contains both the three new root files **and**
the `docs/` count fix, and it turns `test_ac_021_committed_map_matches_fresh_render` from
RED on `main` into GREEN here. No test was edited or deleted.

### 11.5 Phase 4 gate statement

- The scoped non-behavior changes are made: 8 scoped files + `STRUCTURE.md` + this record.
- No version bump, no tag, no release, no PR, no merge (DOCS/CHORE).
- No `src/`, `tests/`, `scripts/`, `migrations/`, `docs/specs/`, `docs/decisions/`,
  `docs/tasks/`, `docs/verification/traceability.md`, `mkdocs.yml`, `userdocs/`, `.github/`,
  `.pre-commit-config.yaml`, `docs/todo/`, `docs/questions/` change; `pyproject.toml` gained
  exactly the two planned keys.
- No other worktree or branch was touched.
- **next:** Phase 5 (S5.1–S5.4) with the §8 check set.

## Phase 5 — verification report (S5.x, DOCS/CHORE light gate set)

Run in the change worktree at branch head `8ec73ee`, working tree clean before and after
every check. DOCS/CHORE owes the light gate set (AGENTS.md Phase Matrix, Phase 5 item 16,
§8 of this record): lint/types where applicable + confirmation that no test file or behavior
was touched. There is **no spec**, so there is no spec-coverage check, no `verify_spec.py`
run, and no traceability row owed.

### 1. Tool gates (§8)

| # | Check | Command | Result |
|---|---|---|---|
| 1 | Lint (whole-repo sweep = the Phase 5 gate, matches CI `lint.yml`) | `uv run ruff check .` | **PASS** — `All checks passed!`, exit 0 |
| 2 | Formatting | `uv run ruff format --check .` | **PASS** — `343 files already formatted`, exit 0 |
| 3 | Types | `uv run mypy src/` | **PASS** — `Success: no issues found in 84 source files`, exit 0 |
| 4 | Traceability referential integrity (no row added by this change) | `uv run python scripts/check_traceability.py` | **PASS** — `Traceability: PASS (881 matrix rows, 136 spec IDs, 801 test functions)`, exit 0 |
| 5 | Docs site (required: `pyproject.toml` is touched and the docs build reads project metadata; also proves the three new root files are not referenced from `userdocs/`) | `uv run --group docs mkdocs build --strict` | **PASS** — `Documentation built in 3.18 seconds`, exit 0, no strict-mode warning (the only banner is the upstream MkDocs-2.0 notice, unrelated) |
| 6 | Dependency check (the `deptry` pre-commit hook fires on `pyproject.toml`) | `uv run deptry .` | **PASS** — `Success! No dependency issues found.` (91 files), exit 0 |
| 7 | The two named guards (§5) | `uv run pytest tests/acceptance/test_structure_map.py tests/contract/logging/test_dependency_contract.py -q` | **PASS** — **33 passed** (31 + 2), exit 0 — matches the orchestrator's independent run; includes `test_ac_021_committed_map_matches_fresh_render`, RED on `main` (F-6), GREEN here |
| 8 | Structure map freshness (after the F-1 regeneration) | `uv run python scripts/make_map.py --check` | **PASS** — exit 0, no output (check-only mode; generate mode was **not** run in this step, per P-94) |
| 9 | Security scan (`src/` unchanged in effect) | `uv run bandit -q -r src/` | **PASS** — exit 0, no issue found; the `nosec … no failed test` WARNING lines on the four `feature_actions.py` files are pre-existing `src/` noise, untouched by this change (check 10 proves `src/` is not in the diff) |

### 2. Scope proofs

**10. `git diff --name-status main...HEAD` — PASS.** Exactly 11 paths at the Phase 4 head
`8ec73ee`, all authorised:

```text
M .agents/skills/implement/SKILL.md   M AGENTS.md      A CHANGELOG.md
M .agents/skills/review/SKILL.md      A LICENSE        M README.md
M .agents/skills/verify/SKILL.md      A SECURITY.md    M STRUCTURE.md
A docs/verification/security-changelog-license.md      M pyproject.toml
```

§2's 8 scoped items (item 6 = the three skill files) + `STRUCTURE.md` (§3.8 / F-1) + this
record. **Nothing** from §4: no `src/`, `tests/`, `scripts/`, `migrations/`, `docs/specs/`,
`docs/decisions/`, `docs/tasks/`, `docs/verification/traceability.md`, `mkdocs.yml`,
`userdocs/`, `.github/`, `.pre-commit-config.yaml`, `docs/todo/`, `docs/questions/`. No test
file is created, modified, weakened or deleted → the DOCS/CHORE "no test files or behavior
were touched" confirmation holds.

After this Phase 5 commit the diff has **one more** path, `docs/workflow/PROBLEMS.md` (P-97,
the friction the Phase 4 step reported). It is the workflow-mandated Problem Log
(AGENTS.md "Problem Log" — the orchestrator's obligation, discharged here on its behalf), it
is **not** in §4's forbidden list, and it carries no behavior. Everything else is unchanged.

**11. `git diff main...HEAD -- pyproject.toml` — PASS.** One hunk, two added lines in
`[project]` after `description`:

```toml
+license = "MIT"
+authors = [{ name = "jackthenet" }]
```

`version = "1.1.0"` unchanged, no `classifiers` key, no `[build-system]`, no
`[tool.bumpversion]` change, no dependency change.

### 3. Content spot-checks (this change's risk is factual, not mechanical)

**`LICENSE` — PASS.** The canonical MIT text, word for word (permission grant, the
"above copyright notice and this permission notice" condition, the all-caps warranty
disclaimer and liability limitation), and the copyright line is exactly
`Copyright (c) 2026 jackthenet` — the user's handle, single year, no range (Q-2).

**`SECURITY.md` — PASS on every factual claim, one wording nit (F-8).**

| Claim | Verified against |
|---|---|
| the `security` job of `.github/workflows/quality.yml` runs `uv run pip-audit` and `uv run bandit -r src/` | job `security` at `quality.yml:30`; `uv run pip-audit` at `:43`; `uv run bandit -r src/` at `:45` |
| the `dependency-review` job runs `actions/dependency-review-action@v5` on pull requests only | job `dependency-review` at `:63`, `if: github.event_name != 'push'` at `:67`, action at `:81` |
| `.github/dependabot.yml` opens weekly PRs for the `uv` and `github-actions` ecosystems | `:4`/`:7` and `:39`/`:42`, both `interval: "weekly"` |
| a real dependency CVE was fixed through this process (PR #48) | `docs/verification/anyio-cve-fix.md` exists; `10066d5 Merge pull request #48 from jackthenet/issue/anyio-cve-fix` |
| private-vulnerability-reporting channel described as requiring the user to enable it | "The form works only once private vulnerability reporting is enabled in the repository's settings on GitHub … if the *Report a vulnerability* button is missing, the setting has not been enabled yet" — F-2 stated, not papered over |
| no email address published | the only `@` hits in the file are the sentence "No email address is published" and the action reference `dependency-review-action@v5`; no `mailto:` |
| supported-versions row uses the snapshot form | `\| latest release (currently \`1.1.0\`) \| ✅ \|` + "The version in parentheses is a snapshot of the current release, not part of the rule" (F-7 handled as planned) |
| 14-day acknowledgement, no fix SLA | "We aim to **acknowledge** a report within **14 days**. There is **no fix SLA** …" |
| template-scope paragraph | the `## Scope: this is a template, not a service` section — forks / vendored code / the `src/main.py` example wiring / downstream deployments out of scope; `src/backend/` and the committed default configuration in scope |

**`CHANGELOG.md` — PASS.** 15 `##` sections: `## [Unreleased]` + **14 release sections
`0.1.0 … 1.1.0`, newest-first**. All 14 dates match their marker commit exactly
(`git log -1 --format=%ad --date=short`): `744eea1` 2026-10-09, `137b7e9` 2026-10-07,
`df81d8b` 2026-10-04, `3c90e6f`/`c6fd876` 2026-10-02, `6d6f120` 2026-09-24, `78475af`/`1646862`
2026-09-21, `8ae9978` 2026-09-20, `7290f94` 2026-09-19, `8a2f931` 2026-09-15, `50344bc`
2026-09-14, `31d2a1a` 2026-09-12, `e9fd8c1` 2026-08-16. Sub-headings are only
`Added`/`Changed`/`Fixed`/`Removed`. The `see <range>` pointer was never used (§3.3 predicted
all 14 ranges traceable — confirmed).

Five releases spot-checked against `git log` (not the record):

| Release | Range read | Entries confirmed against history |
|---|---|---|
| `1.1.0` (newest) | `137b7e9..744eea1` | `b82d5ff feat(T-002)` stdlib-only generator, `28a24be feat(T-005)` `--check`, `725e7ca feat(T-007)` commit `STRUCTURE.md`, `8d6334e feat(T-006)` skill + hook, `b1c6116 feat(T-001)` `scripts/` in the mypy gate, `c7a9119 Merge pull request #74` (structlog delivery merge credited under 1.0.0 exactly as the entry says) |
| `1.0.0` | `df81d8b..137b7e9` | merges #63, #65, #66, #67, #68 in range; #69/#70/#71/#72/#73 are ancestors of the marker — every cited PR resolves |
| `0.5.1` | `6d6f120..c6fd876` | `f9cfe45 fix(settings): … U+0085 (NEL)`, `4d9514e fix(logging): reconfigure removes only managed sinks`, `dd27702 chore(ci): run dependency-review only on pull_request events`, merges #53/#55/#56/#57 in range, and #58 (the `main-ci-green` delivery merge) in the **0.6.0** range — precisely the split the entry states |
| `0.3.1` | `50344bc..8a2f931` | `d0c99e1 spec(file-management): … (#24)`, `c38e7b2 Merge pull request #25`, the `settings-test-isolation` P1→P6 chain, `d5f0a94 fix: sync uv.lock version to 0.3.0 (missed by bump PR #25)` |
| `0.1.0` (earliest) | `git ls-tree -r e9fd8c1` | 20 tracked files: `src/main.py`, `src/core/logging/{__init__,_decorator,_setup}.py`, `loguru>=0.7.3` in `pyproject.toml`, `.pre-commit-config.yaml` with ruff + complexipy + file-hygiene hooks, `.github/workflows/lint.yml`, `.vscode/launch.json` + `settings.json`, the `.github/` prompt and `ruff-post-edit` hook files — the entry describes the **2026-08-16** tree, not the later template shape (§11.3's correction stands) |

**No invented citation anywhere in the file:** every `PR #NN` mentioned in `CHANGELOG.md`
resolves to a real merge commit (`git log --all --grep="pull request #NN"`), the single
exception being **#24**, which is squash-merged as `d0c99e1 … specification (#24)` — a real PR,
a different merge style. No entry could not be traced to a commit in its range.

**`README.md` — PASS.** Exactly one added line after the `pre-commit` badge:
`[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)` — the link
target `LICENSE` exists at the repository root (created by this same change), so the
`update-readme` "badges only for things that really exist" rule is satisfied. No other
README edit.

### 4. Self-consistency of the new rule (check 13)

The obligation is stated in five places. The three substantive elements are **identical**
everywhere:

| Element | AGENTS.md Phase 6 item 10 | AGENTS.md `## Versioning` **Changelog:** | `implement` S4.5 + Process 7 | `verify` MUST/All types | `review` MUST + S6.4 |
|---|---|---|---|---|---|
| entry goes under `## [Unreleased]` | ✓ | ✓ | ✓ | ✓ | ✓ |
| a bump moves it to `## [<version>] - <YYYY-MM-DD>` in the bump commit | ✓ (item 11) | ✓ | — (not that step's job) | — | ✓ (S6.4 done-criteria) |
| **every** change type owes one (REFACTOR / DOCS/CHORE included) | ✓ | ✓ | ✓ | ✓ | ✓ |
| hand-maintained, `bump-my-version` does not touch it | ✓ (item 11) | ✓ (no `[[tool.bumpversion.files]]` entry) | — | — | — |

The Phase 6 renumbering is clean: item 10 inserted, old 10 → 11, old 11 → 12, and no text
anywhere in the repository references a Phase 6 item by number, so nothing went stale.

**One drift, recorded as finding F-9 (not fixed here — out of this step's write set):** the
*when* differs. `AGENTS.md` puts the entry in **Phase 6** (item 10 "when the review report is
clean"; the Versioning bullet says "in Phase 6"), while the `implement` skill commits it at
**S4.5 / Process step 7 (Phase 4)**. The `verify` skill's Phase 5 check ("confirm the entry
exists") is only satisfiable under the `implement`-skill timing — under the AGENTS.md timing
the entry does not exist yet when Phase 5 runs. The content of the obligation is consistent;
the step that writes it is not. Phase 6 should pick one (the Phase 4 timing is the one that
makes the Phase 5 check meaningful, and is what this change itself needed — see F-10).

### 5. The change obeying its own rule (check 14)

**Finding F-10 — the rule was not yet satisfied by this change at Phase 5, and this step
fixed it.** Phase 4 created `CHANGELOG.md` with `## [Unreleased]` seeded only with PR #76 (the
ruff `D` docstring gate) and added the rule to `AGENTS.md` and the three skills, but shipped
**no entry for `security-changelog-license` itself** — the change the rule is about. Per check
14 this step added it under `### Added` (two bullets: the three new root files + the
`pyproject.toml` metadata, and the changelog-entry rule itself), factual, no PR number
invented — the change name is cited instead, since the change PR does not exist yet. The
`verify` skill's new "All types" check now passes for this change on its own terms.

### 6. Checks skipped, with reasons

| Check | Why skipped |
|---|---|
| Spec coverage = 100% / `verify_spec.py` | **n/a** — DOCS/CHORE produces no specification (Phase Matrix); there are no REQ/AC IDs to cover |
| Traceability row for this change (S5.3) | **n/a** — no spec mentions `LICENSE`, `SECURITY.md`, `CHANGELOG.md` or copyright, so no matrix row is owed (§4); the referential-integrity script was still run and passes (check 4) |
| Full test suite (`uv run pytest tests/`) | **Deferred to the S6.4 pre-merge gate** per §8's recommendation — `pyproject.toml` is touched, so one full run before the PR opens is the blanket proof the metadata edit changed nothing; the result belongs in the review report. The two tests that could possibly react to the edit are the 33 that were run (check 7) |
| Coverage threshold, architecture-rule inspection, `red`/`green` gates | n/a for DOCS/CHORE — no behavior, no source, no task DAG |
| Version bump | n/a — DOCS/CHORE → `none` in the bump mapping; `1.1.0` is untouched (proof 11) |

### 7. Findings from Phase 5

| ID | Finding | Disposition |
|---|---|---|
| **F-8** | `SECURITY.md` says the `security` job runs "on every push and pull request"; `quality.yml:3-7` triggers on `push: branches: [main]` and `pull_request`, i.e. pushes **to main**, not every push. | Wording nit, not a false promise — the job and both scans exist and run on the mainline and on PRs. Phase 6 may tighten it to "on pushes to `main` and on pull requests". Not fixed here (out of this step's write set). |
| **F-9** | Rule-timing drift: `AGENTS.md` says the changelog entry is added in Phase 6; the `implement` skill adds it at S4.5 (Phase 4); the `verify` skill's Phase 5 check only works under the Phase 4 timing. | Flagged for Phase 6 (S6.1/S6.3): pick one timing. Content of the rule is consistent across all five places. |
| **F-10** | This change shipped without a `CHANGELOG.md` entry for itself — the rule it introduces was unmet by the change that introduces it. | **Fixed by this step** (check 14): the entry is added under `### Added` in `## [Unreleased]` and committed with this report. |

### 8. Verdict

All nine tool gates pass; both scope proofs pass; every factual claim in the three new root
files and the README badge checks out against the repository; the new rule is consistent in
content across all five places it is stated (one timing drift flagged, F-9); the missing
self-entry is fixed (F-10). No test, source, script, migration, spec, CI or planning-record
file was touched.

**VERDICT: PASS (light gate set)**

- **next:** S6.x Phase 6 (light review + PR). The full test suite must run and pass at S6.4
  before the PR opens (§8 recommendation), and the review should resolve F-8 and F-9.

## Phase 6 — review report (S6.1–S6.4, DOCS/CHORE light review)

Reviewed the **final state** of the changed files at branch head `b227341` against the
normative basis — this scope record (§2 scope, §3 planned text, §4 forbidden list, §5
no-behavior-delta, §6 F-1…F-7, §8 check set, §11 Phase 4 evidence) plus the Phase 5 report
and its findings F-8/F-9/F-10. NOT a commit-by-commit diff; the full suite was run once, as
the S6.4 pre-merge gate (§8 recommendation), because `pyproject.toml` is touched.

### Check 1 — scope conformance: PASS

`git diff --name-status main...HEAD` → 12 paths: §2's 8 scoped items (item 6 = the three
skill files) + `STRUCTURE.md` (§3.8 / F-1) + this record + `docs/workflow/PROBLEMS.md` (the
workflow-mandated Problem Log, AGENTS.md "Problem Log"). Nothing from §4: no `src/`, `tests/`,
`scripts/`, `migrations/`, `docs/specs/`, `docs/decisions/`, `docs/tasks/`,
`docs/verification/traceability.md`, `mkdocs.yml`, `userdocs/`, `.github/`,
`.pre-commit-config.yaml`, `docs/todo/`, `docs/questions/`. The Phase 6 commit below adds no
new path — it edits four already-scoped files.

### Check 2 — no behavior delta: PASS

No `src/`, `tests/`, `scripts/` or `migrations/` path in the diff. `pyproject.toml` diff = one
hunk, two added keys in `[project]` (`license = "MIT"`, `authors = [{ name = "jackthenet" }]`).
`version = "1.1.0"` (`:4`) and `current_version = "1.1.0"` (`:87`) unchanged; no `classifiers`
key; no `[build-system]`; no `[tool.bumpversion]` change; `dependencies` unchanged.
`git log --oneline main..HEAD | grep -i bump` → no bump commit; `git tag --list` → empty. No
version bump anywhere (DOCS/CHORE → none).

### Check 3 — factual accuracy of the new documents: PASS (one wording nit → F-8, fixed)

**`LICENSE`** — the canonical MIT text (header, grant, the "above copyright notice and this
permission notice" condition, the all-caps disclaimer), copyright line exactly
`Copyright (c) 2026 jackthenet` (handle, single year, no range, Q-2). `file` → ASCII text;
newline-terminated; no trailing whitespace.

**`SECURITY.md`** — every claim re-verified against the repository:

| Claim | Verified against |
|---|---|
| `security` job of `quality.yml` runs `uv run pip-audit` and `uv run bandit -r src/` | job at `quality.yml:30`, `pip-audit` `:43`, `bandit` `:45` |
| `dependency-review` job runs `actions/dependency-review-action@v5` on pull requests only | job `:63`, `if: github.event_name != 'push'` `:68`, action `:81` |
| dependabot weekly PRs for `uv` and `github-actions` | `.github/dependabot.yml:4`/`:7`, `:39`/`:42`, both `interval: "weekly"` |
| a real dependency CVE fixed through the process (PR #48) | `10066d5 Merge pull request #48 from jackthenet/issue/anyio-cve-fix` + `docs/verification/anyio-cve-fix.md` |
| no email published | the only `@` in the file is the action reference; no `mailto:`; `:8` states "No email address is published" |
| private-reporting channel depends on the user's repository setting | `:9-12` states it (F-2 stated, not papered over) |
| latest release only, snapshot parenthetical | `\| latest release (currently \`1.1.0\`) \| ✅ \|` + "not part of the rule" (F-7) |
| 14-day acknowledgement, no fix SLA | `## Response` |
| template-scope paragraph | `## Scope: this is a template, not a service` |

`SECURITY.md` cites **no line numbers**, so the record's `:67` vs the actual `:68` drift in the
Phase 5 table is not in the shipped file.

**`CHANGELOG.md`** — 15 `##` sections: `## [Unreleased]` + **14 dated release sections,
newest-first** (`1.1.0` 2026-10-09 … `0.1.0` 2026-08-16). Sub-headings only
`Added`/`Changed`/`Fixed`/`Removed`. No `see <range>` pointer anywhere (grep → none), as §3.3
predicted. Six releases re-checked against `git log` (≥ 4 required, `0.1.0` and `1.1.0`
included):

| Release | Re-checked | Result |
|---|---|---|
| `1.1.0` | `git log --first-parent 137b7e9..744eea1` | `725e7ca` T-007 commit `STRUCTURE.md`, `28a24be` T-005 `--check`, `8d6334e` T-006 skill + hook, `c7a9119` PR #74 — matches the entries, incl. the "implementation credited under 1.0.0" note |
| `1.0.0` | `df81d8b..137b7e9` first-parent | merges #63, #64, #65, #66, #67, #68 in range; #69 (`570bfbc`) is an ancestor of the marker but not of `df81d8b` — exactly as the entry says |
| `0.5.1` | `6d6f120..c6fd876` | `f9cfe45` NEL round-trip, `4d9514e` managed-sinks reconfigure, `dd27702` dependency-review on PR events only |
| `0.4.2` | `8ae9978..1646862` | `bab5cd2 fix(deps): upgrade anyio to >= 4.14.2 (CVE-2026-63374, CVE-2026-64847)` |
| `0.4.1` | `7290f94..8ae9978` | `fe35f82 … fix infinite loop in AC-045 assertion loop (GREEN)` |
| `0.1.0` | `git ls-tree -r e9fd8c1` | 20 tracked files: `src/main.py`, `src/core/logging/{__init__,_decorator,_setup}.py`, `.pre-commit-config.yaml`, `.github/workflows/lint.yml`, `.vscode/`, the `.github/` prompt + ruff-post-edit hooks — the entry describes the 2026-08-16 tree |

Every `PR #NN` cited resolves to a real merge (`git log --all --grep="pull request #NN"`);
#24 is squash-merged (`d0c99e1 … specification (#24)`). No invented entry or PR number.

**F-11 (new, accepted)** — the `0.3.0` / `0.3.1` boundary. `Bump version: 0.2.0 → 0.3.0`
(`50344bc`) is **not** on `main`'s first-parent chain (the pre-worktree workflow bumped on the
feature branch); it reached `main` with the PR #25 merge `c38e7b2`, so `main` first read
`version = "0.3.0"` at the very merge that delivered file-management. The file therefore credits
file-management under `0.3.1` — the window that starts at that merge and closes at `8a2f931`
(2026-09-15) — which is the marker-to-marker-on-`main` convention the other 13 sections use.
Both readings are defensible; the entry is real, correctly dated, and credited exactly once, so
it is **accepted** rather than rewritten (moving a whole feature across a release boundary on a
judgment call is a bigger risk than the ambiguity).

### Check 4 — the rule the change introduces is internally consistent: PASS after fixing F-9

See the F-9 resolution below: all five sites now state the **Phase 6** timing, and the
obligation content is identical everywhere.

### Check 5 — boundaries / architecture: PASS

`LICENSE`, `SECURITY.md`, `CHANGELOG.md` are **root-only**: `grep -rn "SECURITY.md|CHANGELOG.md|LICENSE" mkdocs.yml userdocs/` → no reference, so no nav entry and no `userdocs/` mirror
(Q-8), and `mkdocs build --strict` passes. No new dependency (`dependencies` unchanged, `deptry`
PASS at Phase 5). No CI or hook change (`.github/`, `.pre-commit-config.yaml` not in the diff).
No `src/` module touched, so the feature-boundary and architecture rules are unaffected.

### Check 6 — tests not weakened: PASS

No test path appears in `git diff --name-status main...HEAD`; no test was created, modified,
weakened or deleted. `STRUCTURE.md` is generator output, never hand-edited: `uv run python
scripts/make_map.py --check` exits 0, i.e. the committed map is a byte-exact fresh render, and
`test_ac_021_committed_map_matches_fresh_render` is GREEN here (RED on `main`, F-6).

### Check 7 — the change obeys its own new rule (F-10): PASS

`CHANGELOG.md` `## [Unreleased]` → `### Added` carries this change's own entry (the three root
files + the `pyproject.toml` metadata, and the changelog-entry rule). It is factual, cites the
change name (`security-changelog-license`) rather than a PR number — the PR did not exist when
the entry was written — and the only PR it cites in that block, #76, resolves to `2ab0461
Merge pull request #76 from jackthenet/chore/ruff-d-docstrings`.

### Findings and resolutions

| ID | Finding | Resolution |
|---|---|---|
| **F-8** | `SECURITY.md` said the `security` job runs "on every push and pull request"; `quality.yml:3-7` triggers on `push: branches: [main]` and `pull_request: branches: [main]`. | **Fixed.** The posture line now reads "on pushes to `main` and on pull requests targeting `main`" — what the workflow actually does. |
| **F-9** | Timing drift: `AGENTS.md` adds the entry in Phase 6, the `implement` skill committed it at S4.5 (Phase 4), and the `verify` skill's Phase 5 check was only satisfiable under the Phase 4 timing. | **Fixed — Phase 6 timing chosen** (AGENTS.md is normative, and the Phase 4 timing is wrong on its own terms: S4.5 repeats per DAG task while the entry describes the *change*). Edits: `implement` S4.5 done-criteria reverted (the entry is not that step's gate) and Process step 12 reworded to "added in Phase 6, not here"; `verify`'s All-types bullet reworded to what is true at Phase 5 — record that the entry is **owed** and lands at Phase 6 item 10, since it does not exist yet at Phase 5; `review`'s MUST bullet now says the check applies when the PR opens, not in S6.1, and S6.4's done-criteria now requires the entry present under `## [Unreleased]` before the bump-move clause. `AGENTS.md` untouched (it already states the Phase 6 timing). Obligation content identical at all five sites: entry under `## [Unreleased]`; a bump moves those entries to `## [<new version>] - <YYYY-MM-DD>` in the bump commit; **every** change type owes one, REFACTOR and DOCS/CHORE included; the file is hand-maintained and `bump-my-version` does not touch it. Nothing weakened. The ≥ 20-question interview text and the Question-files subsection were **not** touched (PR #77's territory). |
| **F-10** | This change shipped without a `CHANGELOG.md` entry for itself. | **Closed** — fixed at Phase 5, confirmed here (check 7). Note: it was added by the Phase 5 step under the old `verify` wording; under the corrected timing it belongs to Phase 6. Either way it is present and part of the reviewed PR. |
| **F-11** | New in this review: the `0.3.0`/`0.3.1` attribution of file-management (see check 3). | **Accepted** with the reasoning recorded; no edit. |

### S6.4 pre-merge gate (full suite — required because `pyproject.toml` is touched)

`uv run pytest tests/ -q` → **`816 passed, 1 skipped in 283.74s (0:04:43)`**, exit 0. The single
skip is `tests\acceptance\filemanagement\test_filemanagement.py:364` ("symlinks not available on
this host") — pre-existing and unrelated. No test was edited or weakened.

Gates re-run after the F-8/F-9 edits (commit `chore(security-changelog-license): review findings
F-8, F-9`):

| Gate | Result |
|---|---|
| `uv run ruff check .` | `All checks passed!` exit 0 |
| `uv run ruff format --check .` | `343 files already formatted` exit 0 |
| `uv run python scripts/make_map.py --check` | exit 0 |
| `uv run --group docs mkdocs build --strict` | `Documentation built in 2.04 seconds` exit 0 |

**Version bump: none** (DOCS/CHORE → none in the bump mapping); `1.1.0` untouched, no tag.
Working tree clean apart from the four files this step edited, which are committed with this
report.

### Verdict

All seven checks PASS; F-8 and F-9 fixed, F-10 closed, F-11 accepted with a recorded reason; the
full suite passes; no version bump.

**REVIEW REPORT: CLEAN**

- **next:** human merge of the change PR (S6.4 gate), then S7.1 post-merge cleanup.
- **Merge order:** merge **after** PR #77 (`chore/spec-interview-protocol`) — both edit
  `AGENTS.md` and `.agents/skills/`, in non-overlapping sections (§7).
- **User action outside this PR (F-2):** enable GitHub **private vulnerability reporting** in the
  repository's Security settings — `SECURITY.md` points at that channel.
