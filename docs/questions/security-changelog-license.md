# Questions: security-changelog-license

One question file per change, created at **P.1 Frame** from this template and named `<change-name>.md`. It replaces the retired central `AI_Questions.md` (archived at `docs/questions/archive-AI_Questions.md`).

- **Change:** security-changelog-license (DOCS/CHORE)
- **TODO file:** `docs/todo/security-changelog-license.md`
- **Spec:** n/a
- **Opened:** 2026-10-03
- **Status:** ALL ANSWERED  <!-- OPEN | ALL ANSWERED — set OPEN by the orchestrator at P.1; ALL ANSWERED once every question in this file has an answer (the orchestrator records it together with the `QUESTIONS-ANSWERED` TODO advance) -->
- **Answer rounds:** 2

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

DOCS/CHORE → no ≥ 20 floor (AGENTS.md / specify skill). 10 questions: every one is a user-owned decision (legal grant, identity, disclosure channel, release-history policy, file ownership). Everything else is closed from evidence below.

## Q-1 — Which license?
- **Step:** P.2 Interrogate
- **Why needed:** The license is an irreversible legal grant; the agent must not pick it. Nothing in the repo pre-commits to one: `pyproject.toml` has **no** `license` field, no `classifiers`, no `authors` (`pyproject.toml:3-7` = name/version/description/readme/requires-python/dependencies), and `git ls-files | rg -i license` → only `docs/decisions/ADR-075-...` (a false hit on "security"). GitHub therefore shows "No license" → legally all-rights-reserved, while the stated purpose is `description = "Default template for Python projects."` (`pyproject.toml:4`) — i.e. reuse is asserted but never granted.
- **Context:** Template intended to be copied into new projects; no registry publication (no `[build-system]` table at all in `pyproject.toml`, no publish workflow in `.github/workflows/`).
- **Question:** Which license text goes in `LICENSE`?
  - **MIT** — shortest permissive; attribution + disclaimer only; zero friction for downstream commercial copying.
  - **Apache-2.0** — permissive **plus an explicit patent grant**, but requires stating changes and is ~3× the text.
  - **BSD-3-Clause** — MIT-like plus the no-endorsement clause.
  - **ISC** — functionally MIT, shorter, less familiar to readers.
  - **Recommendation: MIT** — the template's whole point is being copied; MIT is the least frictional grant and the least text to keep correct. Choose Apache-2.0 only if patent protection matters to the holder.
- **Answer:** MIT (user's own choice, not the recommendation's default push - same outcome). Full MIT text with the Q-2 holder line.
- **Date:** 2026-10-04 (rounds 1-2)
- **Status:** ANSWERED
- **Incorporated:** yes — decision Q-1

## Q-2 — Exact copyright holder + year line
- **Step:** P.2 Interrogate
- **Why needed:** The `LICENSE` first line (`Copyright (c) <year> <holder>`) names the legal entity granting the rights; a wrong holder is a defective grant. `pyproject.toml` declares no `authors` field, so nothing in the repo states it.
- **Context:** `git log --format='%an <%ae>'` → `jackthenet <dominik.wolff.85@gmail.com>` 535 commits, `jackthenet <75568988+jackthenet@users.noreply.github.com>` 67, `dependabot[bot]` 14. First commit 2026-08-16 (`git log --reverse`); latest bump 2026-10-02.
- **Question:** What exact line goes in `LICENSE`? Options: (a) `Copyright (c) 2026 Dominik Wolff` (personal legal name); (b) `Copyright (c) 2026 jackthenet` (GitHub handle as-is); (c) a company/legal entity name (please give it); (d) a year range `2026-2026`→`2026`. **Recommendation: (a) `Copyright (c) 2026 Dominik Wolff`** — a legal name, not a handle; single year 2026 (the repo's first year; a range is not required and goes stale).
- **Answer:** `Copyright (c) 2026 jackthenet` - the GitHub handle, NOT the legal name. The user chose option (b) over the recommended (a); recorded as their explicit decision, since a handle is not a legal entity. Single year 2026.
- **Date:** 2026-10-04 (rounds 1-2)
- **Status:** ANSWERED
- **Incorporated:** yes — decision Q-2

## Q-3 — Vulnerability disclosure channel + policy for SECURITY.md
- **Step:** P.2 Interrogate
- **Why needed:** SECURITY.md is worthless without a concrete channel, and the channel is the user's (it commits them to receiving and answering mail). The repo has **no** security policy today: `.github/` contains only `CODEOWNERS.md`, `dependabot.yml`, `hooks/`, `prompts/`, `task-runner/`, `workflows/` — no `SECURITY.md`, no `ISSUE_TEMPLATE`, no `SUPPORT.md`.
- **Context:** The repo already runs a `security` CI job (`pip-audit` + `bandit -r src/`, `.github/workflows/quality.yml:28-43`) and a `dependency-review` job (`:61`), and has fixed a dependency CVE by hand (`docs/verification/anyio-cve-fix.md`) — so SECURITY.md can state real posture instead of promising tooling. Note: enabling GitHub private vulnerability reporting is a **GitHub repository setting the agent cannot change** — it is a user action.
- **Question:** How should reporters reach you, and with what policy?
  - **Channel:** (a) GitHub **private vulnerability reporting** (repo setting, no address published, thread kept private); (b) a security email address (please give it — note it will be public and scraped); (c) both; (d) "template only — no channel, replace when you fork".
  - **Supported versions:** (a) only the latest release is supported (single 0.x line today, `version = "0.6.0"`, `pyproject.toml:4`); (b) latest + previous minor.
  - **Response promise:** (a) acknowledge within 14 days, no fix SLA; (b) 7 days; (c) no promise at all.
  - **Scope statement:** confirm SECURITY.md says this is a **template/library scaffold, not a hosted service** — reports about code a downstream user forked, or about the example wiring, are out of scope.
  - **Recommendation: (a) GitHub private vulnerability reporting + no email; latest release only; acknowledge ≤ 14 days, no fix SLA; explicit template-scope paragraph.**
- **Answer:** Channel: **GitHub private vulnerability reporting**, no published email (the user must enable the repo setting - outside the PR). Supported versions: **latest release only** (single 0.x line, `version = "0.6.0"`). Response promise: **acknowledge within 14 days, no fix SLA**. Scope paragraph: template/library scaffold, not a hosted service; forked code and example wiring are out of scope. Posture stated as fact: `pip-audit` + `bandit -r src/` (quality.yml:28-43) and `dependency-review` (:61).
- **Date:** 2026-10-04 (rounds 1-2)
- **Status:** ANSWERED
- **Incorporated:** yes — decision Q-3

## Q-4 — Does the change also update `pyproject.toml` metadata (license field / authors)?
- **Step:** P.2 Interrogate
- **Why needed:** A `LICENSE` file with no metadata is invisible to packaging tooling and to GitHub's license badge is fine, but `pip`/PyPI would still report "License: UNKNOWN". Editing `pyproject.toml` makes the change touch config, and `pyproject.toml` is **also** owned by the planned `pyproject-tooling-gaps` change → merge-order decision.
- **Context:** `pyproject.toml` has **no** `[build-system]` table and no publish workflow, so the project is not built or published — a `license` field is inert metadata (no build backend validates it), which keeps the change free of any observable behavior delta. `docs/todo/pyproject-tooling-gaps.md:51` lists `pyproject.toml` and `README.md` among its files.
- **Question:** In scope here, or later?
  - (a) **Yes** — add `license = "MIT"` (PEP 639 SPDX string, matching Q-1) and `authors = [{ name = "Dominik Wolff" }]` to `[project]`; skip the deprecated `License :: OSI Approved :: ...` classifier.
  - (b) **No** — `LICENSE` file only; metadata goes to `pyproject-tooling-gaps`.
  - **Recommendation: (a)** — it is 2 lines, it is the half of the license decision that makes it machine-visible, and it is still DOCS/CHORE (no behavior delta: no build backend, no published artifact). If chosen, this change must merge **before** `pyproject-tooling-gaps` to avoid a `pyproject.toml` conflict.
- **Answer:** **(a) Yes** - add `license = "MIT"` (PEP 639 SPDX string) and `authors = [{ name = "jackthenet" }]` to `[project]`; no deprecated `License :: OSI Approved ::` classifier. Still DOCS/CHORE (no `[build-system]`, no artifact). **Merge order consequence: this change merges BEFORE `pyproject-tooling-gaps`**, which also owns `pyproject.toml`.
- **Date:** 2026-10-04 (rounds 1-2)
- **Status:** ANSWERED
- **Incorporated:** yes — decision Q-4 + TODO Depends on

## Q-5 — CHANGELOG format and how far back it goes
- **Step:** P.2 Interrogate
- **Why needed:** The TODO forbids invented content, so the reconstruction depth is a user decision: a changelog that stops at 0.6.0 looks incomplete; one that backfills must be traceable.
- **Context:** There are **no git tags** (`git tag` → empty), so release dates must come from the bump commits, which do exist and are complete: `31d2a1a` 0.1.0→0.2.0 (2026-09-12) … `3c90e6f` 0.5.1→0.6.0 (2026-10-02) — 10 bumps, all dated. Per-spec `## Changelog` blocks exist in 6 specs (`docs/specs/{authentication,settings,mail-service,search,logging,file-management}.md:3`) but AGENTS.md defines `docs/` as the internal process record, not a publishable source.
- **Question:** Format and depth?
  - **Format:** (a) Keep a Changelog (`### Added / Changed / Fixed / Removed`) + SemVer + `## [Unreleased]`; (b) free-form list; (c) generated from `git log` at release time.
  - **Depth:** (a) backfill **all 10** releases (0.1.0 … 0.6.0) using bump-commit dates and the merged PR/spec titles between them; (b) backfill only the last 3 (0.4.0, 0.5.0, 0.6.0); (c) start at 0.6.0 with `Unreleased`.
  - **Recommendation: (a) Keep a Changelog + SemVer, backfill all 10**, each entry traceable to a merge commit/PR title; any version whose content cannot be traced gets a one-line "see `<range>`" pointer rather than invented prose.
- **Answer:** **(a) Keep a Changelog + SemVer + `## [Unreleased]`, backfilling all 10 releases** (0.1.0 ... 0.6.0), each entry traceable to a bump commit / merged PR / spec title; anything not traceable gets a `see <range>` pointer, never invented prose. No git tags exist, so dates come from the 10 dated bump commits (`31d2a1a` ... `3c90e6f`).
- **Date:** 2026-10-04 (rounds 1-2)
- **Status:** ANSWERED
- **Incorporated:** yes — decision Q-5 + TODO In scope

## Q-6 — Should `bump-my-version` maintain `CHANGELOG.md`?
- **Step:** P.2 Interrogate
- **Why needed:** The TODO lists this as an option; it changes the bump contract, and a wrong choice makes the changelog silently wrong on every bump.
- **Context:** `[tool.bumpversion]` currently has exactly **one** file entry (`pyproject.toml:87-90`: `filename = "pyproject.toml"`, `search = 'version = "{current_version}"'`, `replace = 'version = "{new_version}"'`). bump-my-version only does literal search/replace — it cannot insert a dated section; the usual trick (`## [Unreleased]` → `## [X.Y.Z] - {new_version}`) requires the search string to exist verbatim and adds a brittle contract to every future release.
- **Question:** Add a `[[tool.bumpversion.files]]` entry for `CHANGELOG.md`, or keep the changelog maintained by hand (the Phase 6 agent appends the release section next to the bump commit)? **Recommendation: hand-maintained — no bumpversion entry.** The version source of truth stays `pyproject.toml` (`AGENTS.md`, "Versioning"); a search/replace entry buys nothing here and can break the bump if the heading text drifts.
- **Answer:** **(a) Hand-maintained** - no `[[tool.bumpversion.files]]` entry. The Phase 6 agent appends the release section next to the bump commit; `pyproject.toml` stays the version source of truth.
- **Date:** 2026-10-04 (rounds 1-2)
- **Status:** ANSWERED
- **Incorporated:** yes — decision Q-6 + TODO Out of scope

## Q-7 — Changelog drift: add the process rule, or accept drift?
- **Step:** P.2 Interrogate
- **Why needed:** A hand-maintained changelog goes stale immediately unless something feeds it. The TODO puts the rule **out of scope** ("Making 'every change must add a CHANGELOG entry' a workflow rule … would be its own change"), which means the user must say what happens instead.
- **Context:** `rg -n CHANGELOG AGENTS.md .agents/skills/*/SKILL.md` → **no match**: no phase, gate or skill step mentions a changelog today. Adding the rule inside this change would edit `AGENTS.md` + skill files (still DOCS/CHORE, but a much wider diff touching the workflow contract).
- **Question:** (a) file only, accept drift; (b) add the rule in this same change (`AGENTS.md` Phase 5/6 + skills); (c) file only here **and** the orchestrator frames a separate TODO for the rule. **Recommendation: (c)** — keeps this change a clean 3-file docs diff and records the follow-up instead of silently dropping it.
- **Answer:** **(b) Add the process rule in this same change** - `AGENTS.md` (Phase 5/6 + the Versioning section) and the affected skills gain a 'every change adds a CHANGELOG entry' step. This **widens the diff beyond 3 files** and makes `AGENTS.md` + `.agents/skills/` in scope, so the change now collides with the other backlog changes that edit those files (see the TODO's Depends on).
- **Date:** 2026-10-04 (rounds 1-2)
- **Status:** ANSWERED
- **Incorporated:** yes — decision Q-7 + TODO In scope / Depends on

## Q-8 — Are the three files surfaced on the mkdocs site?
- **Step:** P.2 Interrogate
- **Why needed:** `mkdocs.yml:6` sets `docs_dir: userdocs`, and AGENTS.md:66 ("MkDocs site note") forbids publishing from `docs/`; a link from a `userdocs/` page to a **root** file (outside `docs_dir`) is a warning, and the build gate is `uv run mkdocs build --strict` (AGENTS.md:66; pre-push hook `mkdocs-build` in `.pre-commit-config.yaml`) — a warning becomes a failed push.
- **Context:** `mkdocs.yml` has **no `nav:`** key, so anything added under `userdocs/` is auto-published (currently only `userdocs/index.md` and `userdocs/api.md`). Duplicating LICENSE/SECURITY/CHANGELOG under `userdocs/` creates two copies that drift.
- **Question:** (a) root files only, **no** site presence (GitHub renders them natively on the repo front page); (b) mirror copies under `userdocs/`; (c) root files only + an **external** link to the GitHub-hosted files from `userdocs/index.md` (external links do not break `--strict`). **Recommendation: (a)** — GitHub already surfaces all three; (c) only if the user wants them in the site navigation, and then as an external link, never a copy.
- **Answer:** **(a) Root files only, no site presence.** GitHub renders `LICENSE`, `SECURITY.md` and `CHANGELOG.md` on the repo front page; nothing is added under `userdocs/` and no nav entry is created, so `mkdocs build --strict` is untouched.
- **Date:** 2026-10-04 (rounds 1-2)
- **Status:** ANSWERED
- **Incorporated:** yes — decision Q-8 + TODO Out of scope

## Q-9 — Who owns the README License/Security section? (collision)
- **Step:** P.2 Interrogate
- **Why needed:** Two planned DOCS/CHORE changes both want `README.md`; editing it in both produces a merge conflict and duplicated prose.
- **Context:** `docs/todo/update-readme.md` already owns the README rewrite — its 8-section structure includes "License" (`:41`, `:58`), it notes "No `LICENSE` file exists → the skill's own rule ('only badges backed by something real') forbids a license badge" (`:84`), and it explicitly defers "Adding a `LICENSE` file … a `CONTRIBUTING.md`" to a **separate** change (`:87`). So this change unblocks `update-readme`'s license badge but must not write the README itself.
- **Question:** (a) this change does **not** touch `README.md`; `update-readme` adds the License/Security section and the license badge afterwards (this change merges first); (b) this change adds a minimal 3-line "License / Security / Changelog" section and `update-readme` reconciles it. **Recommendation: (a)** — single owner per file, no conflict, and `update-readme` is the change designed to write README prose and badges.
- **Answer:** **Settled by `update-readme` Q-2 = (a) (2026-10-04), not re-asked.** `update-readme` lands first and ships no License badge (its skill rule forbids a badge with nothing behind it). Once `LICENSE` exists, **this** change adds the License badge to the badge row `update-readme` created, so the P.2 note 'this change must not write README' is **reversed**: a badge-row edit is in scope here, and it must re-read the row rather than assume its text.
- **Date:** 2026-10-04 (rounds 1-2)
- **Status:** ANSWERED
- **Incorporated:** yes — decision Q-9 + TODO In scope

## Q-10 — Confirm the DOCS/CHORE workflow runs (not fast-path)
- **Step:** P.2 Interrogate
- **Why needed:** The user may reasonably expect three markdown files to skip the process; the rule says otherwise, and the choice changes the phase count and the PR requirement.
- **Context:** AGENTS.md:1077-1083 ("Emergency / Fast-Path Exception"): "The spec-and-task workflow is bypassed **ONLY** for: Changes that do not alter observable behavior and touch ≤ 2 lines … One-line bug fixes … Direct user commands explicitly containing the keyword `--skip-spec`." and "if the change alters externally observable behavior, the full workflow for the change's type applies regardless of how small the change appears."
- **Question:** Proceed with the normal DOCS/CHORE workflow (Phase P → Phase 4 → light Phase 5 → light review → PR → human merge), or is there an explicit `--skip-spec` instruction? **Recommendation: run the workflow** — the change is far over the ≤ 2-line fast-path bound (three new files, ~200+ lines) and it edits `pyproject.toml` if Q-4(a) is chosen; the DOCS/CHORE path is already the cheapest full path (no spec, no task DAG, no test phase, light Phase 5).
- **Answer:** **Run the DOCS/CHORE workflow** - no `--skip-spec` was given, and the change is far over the <= 2-line fast-path bound (three new files plus `AGENTS.md`/skills under Q-7). Phase P -> Phase 4 -> light Phase 5 (lint/types, `mkdocs build --strict`, `check_traceability.py`) -> light review -> PR -> human merge; no version bump.
- **Date:** 2026-10-04 (rounds 1-2)
- **Status:** ANSWERED
- **Incorporated:** yes — decision Q-10

---

## Closed from evidence (no question needed)

| Point | Evidence / decision |
|---|---|
| The three files really are absent | `ls` → no `LICENSE`/`SECURITY.md`/`CHANGELOG.md`; `git ls-files \| rg -i "license\|security\|changelog"` → only `docs/decisions/ADR-075-fail-closed-security-posture.md` (a "security" title hit). |
| No existing security policy to match | `.github/` = `CODEOWNERS.md`, `dependabot.yml`, `hooks/`, `prompts/`, `task-runner/`, `workflows/` — no `SECURITY.md`, no issue templates, no `SUPPORT.md`. |
| SECURITY.md may state real posture, not promises | `security` job runs `uv run pip-audit` and `uv run bandit -r src/` (`.github/workflows/quality.yml:28-43`); `dependency-review` job (`:61`); dependabot weekly uv updates (`.github/dependabot.yml:4-7`); a real CVE fix record (`docs/verification/anyio-cve-fix.md`). |
| Version source of truth | `version = "0.6.0"` (`pyproject.toml:4`) + `[tool.bumpversion] current_version = "0.6.0"` (`:80`); bump mapping per AGENTS.md:739-751 — **DOCS/CHORE → no version bump**, so this change must not touch either value. |
| Release dates for the changelog are recoverable | 10 bump commits, all dated 2026-09-12 … 2026-10-02; `git tag` is empty, so bump commits are the only release markers. |
| New root `.md` files pass pre-commit | `.pre-commit-config.yaml` has no markdown/prettier hook; the only hooks that touch markdown are `trailing-whitespace` and `end-of-file-fixer` → the new files must be newline-terminated with no trailing whitespace. `deptry` fires only on `^(pyproject\.toml\|uv\.lock\|src/\|tests/\|scripts/\|migrations/)`; `mkdocs-build` (pre-push) fires on `^(mkdocs\.yml\|userdocs/\|pyproject\.toml)` — so a `pyproject.toml` edit (Q-4a) triggers a strict docs build, which is cheap evidence, not a risk. |
| mkdocs `--strict` and nav | `mkdocs.yml` has **no `nav:`** → pages under `userdocs/` are auto-published, so adding a nav entry is not required and cannot break; the strict-build risk is only a **relative link from a `userdocs/` page to a root file outside `docs_dir`** (Q-8). |
| Traceability CI is unaffected | `scripts/check_traceability.py` reads `docs/verification/traceability.md`, `docs/specs/`, `tests/` — root `.md` files are outside its inputs. |
| No spec is touched | `rg -ni "LICENSE\|SECURITY\.md\|CHANGELOG\.md\|copyright" docs/specs/` → no match; `docs/specs/*.md` `## Changelog` blocks are internal process records (AGENTS.md:66). |
| In-flight state | `git worktree list` → primary only; `gh pr list --state open` → none. No concurrent edit of these paths is in flight. |

## Overlap / collision analysis (all 16 TODOs, 13 specs, worktrees/PRs)

- **`update-readme` (DOCS/CHORE, PREPARING) — direct collision on `README.md`.** It owns the README rewrite, lists "License" as section 8 (`docs/todo/update-readme.md:41,58`), forbids a license badge while no `LICENSE` exists (`:84`), and defers "Adding a `LICENSE` file" to a separate change (`:87`). Resolution: Q-9(a) — this change never writes README; merge **this** change first so `update-readme` can add a truthful license badge.
- **`pyproject-tooling-gaps` (DOCS/CHORE, PREPARING) — collision on `pyproject.toml`** (its file list: `pyproject.toml`, `.pre-commit-config.yaml`, `lint.yml`, `quality.yml`, `README.md` — `docs/todo/pyproject-tooling-gaps.md:51`). Overlap is only if Q-4(a) adds `license`/`authors` to `[project]`; different tables from its `[tool.*]` edits, so a textual conflict is unlikely, but the two changes must not run in parallel on the same file. Resolution: merge this change first, or defer the metadata to `pyproject-tooling-gaps` (Q-4b).
- **`docs-path-ci-trigger`** touches only `.github/workflows/spec-validation.yml` `paths:` — no overlap; note that a root-`.md`-only PR does **not** trigger spec-validation today (its `paths:` filters, `spec-validation.yml:6,16`), which is that change's problem, not this one's.
- **All other TODOs** (`api-keys`, `architecture-tests-missing`, `notifications`, `python-3.15`, `remove-spec-tdd-driver`, `session-lookup-unwired`, `spec-interview-protocol`, `split-archived-qa`, `structlog-logging`, `structure-map`, `tenacity-rich-cachetools`, `track-python-skill`, `value-triage-gate`, `workflow-docs-nits`) — `rg -ni "SECURITY\.md\|LICENSE\|CHANGELOG\.md" docs/todo/` shows no other claim on these three files. `value-triage-gate.md:85` only scores this change (4/5, implement).
- **Specs:** none of the 13 `docs/specs/` files mentions a license, copyright, `SECURITY.md` or `CHANGELOG.md` → no spec amendment, no traceability row needed.
- **Worktrees/PRs:** primary worktree only, no open PRs → nothing to rebase.

## Fast-path vs workflow judgement

AGENTS.md:1077-1083: "The spec-and-task workflow is bypassed **ONLY** for: Changes that do not alter observable behavior and touch ≤ 2 lines (typos, docstring fixes, comment edits). One-line bug fixes with an existing, failing test already in place. Direct user commands explicitly containing the keyword `--skip-spec`."

**Judgement: not fast-path — run the DOCS/CHORE workflow.** Three new files (~200+ lines) are far over the ≤ 2-line bound, and Q-4(a) would add a `pyproject.toml` edit. The Light ISSUE tier (AGENTS.md:1085) is ISSUE-only and does not apply; the DOCS/CHORE path is already the lightest full path (Phase P → Phase 4 → Phase 5 lint/types only → light review → PR → human merge, no version bump per AGENTS.md:751). Recorded as Q-10 so the user can confirm or invoke `--skip-spec`.

## For P.4 (scope record) — exact files once answered

Create (root):
1. `LICENSE` — full text of the Q-1 license, first line = Q-2 copyright string.
2. `SECURITY.md` — reporting channel (Q-3), supported-versions table (latest release only unless Q-3 says otherwise), scope paragraph (template, not a hosted service), and the existing posture stated as fact: `pip-audit` + `bandit` (`quality.yml:28-43`), `dependency-review` (`:61`), weekly dependabot (`dependabot.yml:4-7`).
3. `CHANGELOG.md` — Keep a Changelog + SemVer headings, `## [Unreleased]`, plus the Q-5 backfill set with dates taken from the bump commits (`31d2a1a` … `3c90e6f`).

Edit (conditional on answers):
4. `pyproject.toml` — only if Q-4(a): `license = "<SPDX>"` and `authors = [{ name = "<Q-2 holder>" }]` in `[project]`. **Not** `[[tool.bumpversion.files]]` unless Q-6 says otherwise. Version values stay untouched (DOCS/CHORE → no bump).
5. `userdocs/index.md` — only if Q-8(c): an external link to the GitHub-hosted files (no copy under `userdocs/`).
6. `README.md` — **not touched** unless Q-9(b) is chosen (collision with `update-readme`).

Explicitly not touched: `src/`, `tests/`, `migrations/`, `docs/specs/`, `docs/decisions/`, `.github/workflows/*`, `AGENTS.md` + skills (the changelog rule is Q-7 → separate TODO if (c)).

Phase 5 gate (DOCS/CHORE, AGENTS.md Phase 5 item 16): `uv run ruff check .`, `uv run mypy src/` where applicable, `uv run mkdocs build --strict`, `uv run python scripts/check_traceability.py`, and `git diff --name-status` proving no `src/`/`tests/` path changed. Phase 6: no version bump. Follow-up to frame if Q-7(c): TODO `changelog-process-rule`.

## Late questions (Phases 2–6)

<questions discovered after the change entered the workflow; same entry format, Step field set to the step that found it>
