# Questions: codecov-coverage-badge

One question file per change, created at **P.1 Frame** from this template and named `codecov-coverage-badge.md`. It replaces the retired central `AI_Questions.md` (archived at `docs/questions/archive-AI_Questions.md`).

- **Change:** codecov-coverage-badge (DOCS/CHORE)
- **TODO file:** `docs/todo/codecov-coverage-badge.md`
- **Spec:** n/a
- **Opened:** 2026-10-04
- **Status:** CLOSED — change **DROPPED** at P.3 (2026-10-07)  <!-- Q-1 = drop; Q-2 was answered then became moot; Q-3 = n/a; Q-4 … Q-29 were never asked (moot once the service is declined) -->
- **Answer rounds:** 0  <!-- P.2 Interrogate has not run yet -->

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

**P.2 Interrogate ran 2026-10-05: 29 questions (Q-1 … Q-29), one `BLOCKED-USER` batch, most-blocking first** (service/go-no-go and the "is the badge honest" contract before the CI mechanics, the CI mechanics before the cosmetic badge-row questions). The change is small, but every question below is a decision the repository does not already answer — the 13 points that the repo *does* answer are listed under "Closed from evidence" and cost no question.

### P.2 interrogation record (coverage, evidence, overlap)

**Category coverage** (P.2 adversarial interrogation, DOCS/CHORE-relevant categories):

| Category | Result | Where settled |
|---|---|---|
| Go/no-go: the external service itself (Ponytail rung 1) | asked | Q-1 |
| Scope boundary: what lands in which PR, and the honesty gate | asked | Q-2, Q-3 |
| Secrets / CI trust boundary (forks, Dependabot, OIDC) | asked + evidence (repo is public) | Q-4, Q-5 |
| CI event surface (which runs upload) | asked | Q-6 |
| Failure semantics (may CI go red? what does a red upload mean?) | asked + evidence (action default) | Q-7, Q-17 |
| Interaction with the existing `fail_under` gate (status checks, comments, config file) | asked | Q-8, Q-9, Q-10, Q-12 |
| Report correctness (paths in `coverage.xml`, which number the badge shows) | asked + **measured** (see below) | Q-11, Q-13 |
| Tooling choice & pinning | asked + evidence (v7 is current, dependabot covers actions) | Q-14 |
| Job placement / CI cost | asked | Q-15, Q-18 |
| Report discovery and grouping | asked | Q-16, Q-19 |
| Badge surface (URL, alt text, link, position, staleness) | asked | Q-20 … Q-23 |
| Traceability of the dependency decision (ADR rule in `AGENTS.md`) | asked | Q-24 |
| Change type / version bump | asked | Q-25 |
| Phase 5 evidence set for a CI-only change | asked | Q-26 |
| Collisions with other in-flight changes | asked + evidence | Q-27, Q-28 |
| Downstream template users (this repo is a template) | asked | Q-29 |
| Report format (`--cov-report=xml`) | **closed from evidence** | — |
| `coverage.xml` accidentally committed | **closed from evidence** | — |
| Other jobs producing coverage data | **closed from evidence** | — |
| mkdocs / `userdocs/` badge duplication | **closed from evidence** | — |
| `deptry` / `uv.lock` impact | **closed from evidence** | — |
| Tests or scripts that assert on workflow files | **closed from evidence** | — |
| Action major version / drift | **closed from evidence** | — |

**Closed from evidence (no question spent):**

1. **The report format already exists.** `.github/workflows/quality.yml:59` already runs `uv run pytest tests/ --cov --cov-report=xml`, so `coverage.xml` is produced in CI today and thrown away. Re-run locally 2026-10-05 (`uv run pytest tests/unit/eventbus -q --cov --cov-report=xml`) → `Coverage XML written to file coverage.xml`. The TODO's in-scope bullet "plus whatever report format it needs (e.g. `--cov-report=xml`)" (`docs/todo/codecov-coverage-badge.md:30`) is already satisfied — the upload step is the only new CI line.
2. **`coverage.xml` cannot be committed by accident.** `.gitignore` already lists `coverage.xml`, `.coverage`, `.coverage.*`, `htmlcov/`, `nosetests.xml` (the "Unit and packaging / coverage reports" block).
3. **The repository is public.** `GET https://api.github.com/repos/jackthenet/python-template` → `"private": false`. The TODO's risk note "a private repository additionally needs a `CODECOV_TOKEN` repository secret" (`docs/todo/codecov-coverage-badge.md:44`) does not describe this repo today — Q-4 is about *which* authentication method, not about privacy.
4. **No other job produces coverage data.** `grep -rn -i cov .github/workflows/` → matches only `quality.yml:45,57,58,59`. `lint.yml` and `spec-validation.yml` produce none, so there is exactly one upload point and no double-reporting.
5. **Nothing asserts on the workflow files.** `grep -rln "quality.yml|workflows" tests/ scripts/` → no match. Editing `quality.yml` breaks no test and no script.
6. **The published docs site carries no badges.** `grep -rn -i badge userdocs/ mkdocs.yml` → no match (`userdocs/` = `api.md`, `index.md`). The badge is a `README.md`-only edit; `mkdocs build --strict` cannot be affected by it.
7. **`deptry` and `uv.lock` are untouched.** A GitHub Action is not a Python package, so no dependency group changes (`pyproject.toml:29-77`) and `[tool.deptry]` stays as it is.
8. **The action's own default already keeps CI green.** `codecov/codecov-action@v7 action.yml:52-55` → `fail_ci_if_error` default `'false'`; `:82-85` → `handle_no_reports_found` default `'false'`. The TODO's "CI must stay green" worry (`docs/todo/codecov-coverage-badge.md:46`) is the default behaviour; Q-7 asks whether to keep that default or make a failed upload loud.
9. **Current action major is v7.** `GET /repos/codecov/codecov-action/tags` → `v7.1.1`, `v7`, `v6.0.2`, `v5.5.5`. Repo precedent is a major tag, never a SHA: `actions/checkout@v7`, `astral-sh/setup-uv@v7`, `actions/setup-python@v7` (`quality.yml:48,50,52`), `actions/dependency-review-action@v5` (`quality.yml:71`).
10. **Dependabot already maintains actions.** `.github/dependabot.yml` has a `github-actions` ecosystem (`directory: "/"`, weekly), so a `@v7` ref does not silently rot.
11. **`update-readme` is MERGED, not WAITING.** `docs/todo/update-readme.md:10` → `Status: MERGED` (PR #66, merge `b7b0ee0`, cleanup 2026-10-05). The badge row this change edits **already exists on `main`**: `README.md:3-9`, 7 badges, all in the `[![Alt](svg-url)](link-url)` form. The TODO's constraint "update-readme (WAITING, lands independently)" (`docs/todo/codecov-coverage-badge.md:47`) is stale — the row is there, and it must be re-read, not assumed.
12. **A badge URL returning 200 is not proof that coverage is published.** Measured 2026-10-05: `https://codecov.io/gh/jackthenet/python-template/graph/badge.svg` → **200**, and its SVG text is `unknown`; `https://codecov.io/gh/jackthenet/python-template/branch/main/graph/badge.svg` → **200**; `https://img.shields.io/codecov/c/github/jackthenet/python-template.json` → `{"label":"coverage","message":"unknown","color":"lightgrey"}`; `https://codecov.io/api/v2/gh/jackthenet/python-template` → **404**. Every candidate badge URL already "works" while reporting nothing — which is exactly the "a badge that lies is worse than no badge" risk (`docs/todo/codecov-coverage-badge.md:45`). Hence Q-3 defines the proof.
13. **`src/frontend` contributes nothing to the report.** Measured `coverage.xml` `<sources>` lists both roots (`…\src\backend`, `…\src\frontend`) but the `<packages>` list has no `frontend` entry (the directory is empty) — consistent with the `pyproject.toml:99-102` comment. No question needed; it only matters for Q-11/Q-13.

**Measured report shape (the load-bearing finding for Q-11 and Q-13).** `coverage.xml` from this repo's config (`[tool.coverage.run] source = ["src/backend", "src/frontend"]`, `branch = true`, `pyproject.toml:96-102`):

```xml
<coverage version="7.16.0" … lines-valid="4429" lines-covered="679" line-rate="0.1533"
          branches-valid="956" branches-covered="86" branch-rate="0.08996">
  <sources>
    <source>C:\workspace\active-projects\python-template_kopie\src\backend</source>
    <source>C:\workspace\active-projects\python-template_kopie\src\frontend</source>
  </sources>
  <package name="authentication" …><classes>
    <class … filename="authentication/__init__.py">
```

So the per-file names are **relative to each source root** (`authentication/__init__.py`), **not** repo paths (`src/backend/authentication/__init__.py`), and the roots are absolute host paths (`C:\…` locally, `/home/runner/work/python-template/python-template/src/backend` on CI). Codecov has to resolve that mapping to show files, and its action exposes `disable_file_fixes`, `network_filter`, `network_prefix`, `root_dir` and `fixes` for exactly this. Whether anything has to be done is Q-11 — and the tempting "fix" (change `source` to `["src"]`) changes **what is measured**, which `pyproject-tooling-gaps` already put out of scope (`docs/todo/pyproject-tooling-gaps.md:47`) and which would move the `fail_under = 92` denominator (Q-12).

**Overlap & collision analysis** (all 13 `docs/specs/` files grepped for `codecov`/`coverage`, all 23 `docs/todo/` items read for `quality.yml|README.md|badge|coverage`, `docs/verification/` scanned, `git worktree list` / `git branch -a`):

- **Specs:** `grep -rn -i codecov docs/specs/` → no match. No spec governs CI, coverage publishing, or badges. `docs/specs/logging-coverage.md` is about *test* coverage of the logging feature, unrelated to publishing a number. "Related specs: none" in the TODO holds.
- **`update-readme` (MERGED)** — the *reason* this change exists: `docs/questions/update-readme.md:83-84` Q-3 = **(d)** "add Codecov, as a separate change", and `docs/todo/update-readme.md:93` names this change as its owner. Its verification record's badge deny-list (`docs/verification/update-readme.md:104,272,358`) forbids a coverage badge **in that change** and greps `README.md` to prove it. No double work: that change ships the row, this one adds the coverage badge to it.
- **`security-changelog-license` (QUESTIONS-ANSWERED)** — will add the **License badge to the same badge row** (`docs/todo/security-changelog-license.md:28-29`, "the badge row must be re-read, not assumed"). Same file, same 7-line block → **Q-27**.
- **`structure-map` (QUESTIONS-ANSWERED)** — its Q-28 answer adds `uv run mypy scripts/` to "the CI quality job (`quality.yml`)", i.e. it edits the same workflow file (a different job block) → **Q-28**.
- **`python-3.15` (QUESTIONS-ANSWERED) / `python-3.15-upgrade` (PREPARING)** — both inventory and edit the **11 `python-version: '3.14'` literals**, including `quality.yml:54`, which is *inside the `coverage` job this change edits* (`docs/todo/python-3.15-upgrade.md:29,32`; `docs/todo/python-3.15.md:69` already flags the `pyproject-tooling-gaps` collision precedent) → **Q-28**.
- **`pyproject-tooling-gaps` (MERGED)** — added the `complexity` job (`quality.yml:120-137`) and the `docs` group split; its out-of-scope list is explicit: "Raising `fail_under` above 92, **or changing what coverage measures**" (`docs/todo/pyproject-tooling-gaps.md:47`). That decision already owns the coverage-measurement boundary this change must not cross → **Q-12**.
- **`docs-path-ci-trigger` — DROPPED** (value triage 1/5, `docs/todo/docs-path-ci-trigger.md:13`), and it explicitly excluded "adding path filters to the other workflows (`lint.yml`, `quality.yml`)" (`:28`). So no trigger-filter collision: the `coverage` job keeps firing on every `pull_request` and `push` to `main` (`quality.yml:3-7`) — relevant to Q-6, Q-15.
- **`structlog-logging` (WAITING, the only live worktree: `crosscut/structlog-logging`)** — touches `src/backend/{logging,eventbus,permissions,settings}`, tests, `pyproject.toml`, `AGENTS.md`, skills; **not** `quality.yml` and **not** `README.md`. It will move the coverage percentage, which is Codecov's business, not this change's. No file collision.
- **MERGED / no overlap:** `architecture-tests-missing`, `session-lookup-unwired`, `workflow-docs-nits`, `track-python-skill`, `remove-spec-tdd-driver`. **PREPARING / QUESTIONS-ANSWERED with no overlap:** `api-keys`, `notifications`, `ruff-d-docstrings`, `settings-public-registry-setter`, `split-archived-qa`, `spec-interview-protocol`, `tenacity-rich-cachetools`, `value-triage-gate`.
- **No existing verification record covers a coverage upload or a coverage badge** — `docs/verification/` has no codecov/coverage-badge record; `docs/verification/update-readme.md` and `pyproject-tooling-gaps.md` only record the *decision to defer it to this change*.
- **Branch/worktree state:** `git worktree list` → primary (`main`) + `crosscut/structlog-logging`. No open PR for this change; nothing to rebase.

**For P.4 (scope record)** — the answers below feed: the exact `quality.yml` insertion point (after `:59`, inside the `coverage` job), the auth method and any `permissions:` block, the event condition, the failure semantics, whether a root `codecov.yml` joins the file set, the exact `README.md` badge line and its position, whether an ADR joins the diff, and the Phase 5 evidence list. The `fail_under = 92` line and `[tool.coverage.*]` stay byte-identical unless Q-12 says otherwise.

---

## Q-1 — Do you authorize Codecov as a service, and will you do the account-side steps?
- **Step:** P.2 Interrogate
- **Why needed:** The change adds a third-party SaaS dependency, and the parts that make it work — installing/authorizing the Codecov GitHub App and activating `jackthenet/python-template` on codecov.io — are account and repo-settings actions **outside any PR**. The agent cannot perform them, and without them nothing in this change can ever be proven.
- **Context:** `grep -rn -i codecov` over the repo → only this change's planning records; no upload step (`quality.yml:45-59`), no Codecov config, no secret reference. The repo is public (`"private": false`, GitHub API). The value case is already triaged 3/5 in `docs/todo/codecov-coverage-badge.md:25`, and the local gate (`pyproject.toml:105` `fail_under = 92`) already prevents regressions — the gain is history and a real badge, not a new guarantee.
- **Question:** Do you accept Codecov as the coverage service for this repo, and will you personally activate the repo on codecov.io (and install its GitHub App) so the upload can be verified?
  - **A. Yes — Codecov accepted, I will activate the repo (Recommended)** — the change proceeds exactly as framed; the agent writes the CI step and the badge only after the activation is real.
  - **B. Yes, but I want to see the CI diff before I activate anything** — the upload step is reviewed first, activation follows; the badge necessarily lands later (feeds Q-2).
  - **C. No — drop the change** — the `fail_under` gate stays the only coverage signal; no external service, no badge, nothing to maintain.
  - **D. No — a different service (Coveralls, self-hosted, or a generated static badge)** — the change must be re-framed before P.4.
- **Answer:** **No — drop the change** (user, 2026-10-07, after the orchestrator's architecture read: a badge buys visibility, not assurance; `fail_under = 92` is already the guarantee, and in a *template* repo every third-party integration is a configure-or-delete task for every downstream user). A hardcoded static shields.io badge was ruled out as silently lying; a self-hosted `coverage.json` + shields endpoint was ruled out as more machinery than Codecov for the same result.
- **Date:** 2026-10-07
- **Status:** ANSWERED
- **Incorporated:** yes — the change is DROPPED (`docs/todo/codecov-coverage-badge.md`); no P.4, no worktree, no CI step, no badge

## Q-2 — Does the badge ship in the same PR as the upload step?
- **Step:** P.2 Interrogate
- **Why needed:** The TODO makes the badge conditional — "**only** once the upload is proven to work on `main`" (`docs/todo/codecov-coverage-badge.md:31`) — but a PR is merged before any `main` run happens. The sequencing decides how many PRs this change has and whether `README.md` can ever display a number nothing produced.
- **Context:** `README.md:3-9` already holds 7 badges from the merged `update-readme`. Measured today, every candidate Codecov badge URL for this repo already returns **200** while reporting `unknown` (see the preamble, item 12) — so a badge merged in the same PR would render as "unknown" until a `main` push uploads, which is precisely the "a badge that lies is worse than no badge" risk (`docs/todo/codecov-coverage-badge.md:45`).
- **Question:** Is the badge added in the same PR as the upload step, or only in a second PR after the first successful upload on `main`?
  - **A. Two PRs: upload step first, badge in a follow-up PR after the `main` run is verified (Recommended)** — `README.md` never shows a number that does not exist; costs one extra PR cycle and one extra `chore/` branch (or a second commit pushed after the gate clears).
  - **B. One PR, badge included** — one review, but `README.md` shows `unknown` from merge until the first `main` push completes (minutes to hours, and indefinitely if the upload silently fails).
  - **C. One PR, badge added in a later commit of the same branch after a branch run proves the upload** — one PR, but a branch/PR upload is not a `main` upload, so the badge can still be unproven at merge.
- **Answer:** **One PR, badge included** (user, 2026-10-07). This **overrides** the TODO's conditional wording "**only** once the upload is proven to work on `main`" (`docs/todo/codecov-coverage-badge.md:31`): one PR, one review, `README.md` may render `unknown` from merge until the first `main` push completes. The honesty risk is accepted **because** Q-3 still defines a post-merge proof that must be observed and recorded — the badge is not allowed to stay unproven.
- **Date:** 2026-10-07
- **Status:** ANSWERED
- **Incorporated:** yes — P.4 scope: single PR file set includes `README.md`; the "proven" gate moves from *before the badge is written* to *after the merge, before the change is called MERGED* (Phase 5/6 evidence, Q-3). **Superseded 2026-10-07:** Q-1 dropped the change, so this answer is a record of a decision that was never executed.

## Q-3 — What exactly counts as "the upload is proven"?
- **Step:** P.2 Interrogate
- **Why needed:** The acceptance signal ("Codecov shows a coverage number for the run", `docs/todo/codecov-coverage-badge.md:50`) is not checkable as written, and the obvious check — does the badge URL load — is already true today with no Codecov at all. Without a defined proof, P.4 cannot state a done-criterion and Phase 5 cannot record evidence.
- **Context:** Measured 2026-10-05: `…/graph/badge.svg` → 200 with SVG text `unknown`; `…/branch/main/graph/badge.svg` → 200; `img.shields.io/codecov/c/github/jackthenet/python-template.json` → `{"message":"unknown","color":"lightgrey"}`; `codecov.io/api/v2/gh/jackthenet/python-template` → 404 (unauthenticated). The action's `fail_ci_if_error` default is `'false'` (`action.yml:52-55`), so even "the step exited 0" is not proof that Codecov stored a report.
- **Question:** Which observation makes the upload "proven"?
  - **A. Codecov's UI shows a commit for the `main` push with a non-zero coverage percentage and a file tree (Recommended)** — proves upload, path mapping (Q-11) and the badge's data source in one look; recorded as a dated screenshot/URL in `docs/verification/codecov-coverage-badge.md`.
  - **B. The upload step exits 0 in the `main` run** — cheap and automatable, but with `fail_ci_if_error: false` it can be 0 on a rejected upload.
  - **C. The badge stops reporting `unknown`** — end-user visible, but it lags, and it says nothing about whether per-file paths resolved.
  - **D. The Codecov API returns a coverage value for the commit** — machine-checkable, but needs a token to query v2 (404 today), i.e. more secrets for a one-off check.
- **Answer:** **n/a** — moot: Q-1 declined the service, so there is no upload to prove.
- **Date:** 2026-10-07
- **Status:** ANSWERED
- **Incorporated:** n/a — change dropped

## Q-4 — How does the upload authenticate?
- **Step:** P.2 Interrogate
- **Why needed:** The upload needs authorization, and the three supported methods have different setup costs, different secret surface, and different requirements on the workflow file. This is a trust-boundary decision, not an implementation detail.
- **Context:** The repo is **public** (`"private": false`). `codecov/codecov-action@v7` exposes `token` (`action.yml:145-147`, `required: false`) and OIDC support (`:151-156`, README `:111-127`, which additionally requires `permissions: id-token: write` on the job — `quality.yml` currently declares **no** `permissions:` block at all). Its README `:49` states "Tokenless uploading is unsupported. However, PRs made from forks to the upstream public repos will support tokenless", and `:23` notes tokenless for public repos depends on an organization-level "Global Upload Token" opt-out — this repo is owned by a **user** account (`jackthenet`), not an org.
- **Question:** Which authentication method does the upload step use?
  - **A. `token: ${{ secrets.CODECOV_TOKEN }}` — a repository secret you create (Recommended)** — the documented supported path; needs one manual secret, and secrets are unavailable to fork PRs (see Q-6).
  - **B. `use_oidc: true`** — no secret to store and nothing to rotate, but it adds a `permissions: id-token: write` block to the job and depends on GitHub OIDC being reachable from the runner.
  - **C. Tokenless (no token at all)** — zero setup, but the action's own README calls it unsupported for the repository's own runs; uploads may be rejected with no CI failure (Q-7 default) and the badge silently never fills.
- **Answer:** **PENDING**
- **Date:** 2026-10-05
- **Status:** PENDING
- **Incorporated:** no

## Q-5 — What happens on Dependabot PR runs?
- **Step:** P.2 Interrogate
- **Why needed:** Dependabot opens PRs in this repo, and Dependabot PRs cannot read ordinary repository secrets. If the upload runs there, it either fails or silently reports nothing on every dependency PR — a recurring, self-inflicted noise source this repo created for itself.
- **Context:** `.github/dependabot.yml` has two ecosystems: `uv` (weekly, grouped) and `github-actions` (weekly) — so dependency PRs are routine. `codecov-action@v7` README `:54`: "For repositories using `Dependabot`, users will need to ensure that it has access to the Codecov token for PRs from Dependabot to upload coverage. To do this, please add your `CODECOV_TOKEN` as a Dependabot Secret."
- **Question:** How are Dependabot PR runs handled?
  - **A. Accept it: Dependabot PR uploads report nothing, the step stays non-failing (Recommended)** — zero extra setup; the trend line only needs `main`, and PR coverage is not what the badge shows.
  - **B. Add `CODECOV_TOKEN` as a Dependabot secret so those PRs upload too** — complete PR data, but it copies the secret into a second store and Dependabot PRs then get patch coverage on a template repo nobody reviews for coverage.
  - **C. Skip the upload on Dependabot runs (`if:` on the actor)** — explicit and quiet, at the cost of one more condition in the workflow.
- **Answer:** **PENDING**
- **Date:** 2026-10-05
- **Status:** PENDING
- **Incorporated:** no

## Q-6 — Which runs upload to Codecov?
- **Step:** P.2 Interrogate
- **Why needed:** The workflow fires on both `pull_request` and `push` to `main` (`quality.yml:3-7`), so an unconditional upload step posts a report for **every PR** as well as every `main` push. That decides whether Codecov comments on PRs, whether patch coverage exists, and whether fork PRs (no secrets) hit a failing upload.
- **Context:** The `coverage` job has no `if:` today, and `quality.yml:61-65` shows the repo already uses an event guard for a job that cannot run on push (`dependency-review`: `if: github.event_name != 'push'`) — the pattern exists to copy. The repo has no path filter on `quality.yml`, so doc-only PRs run the coverage job too.
- **Question:** Which events upload a report?
  - **A. Both `push` to `main` and `pull_request` (Recommended)** — PR reports give patch/diff coverage and the PR comment; fork PRs upload tokenless (supported for forks per the action README), so nothing fails.
  - **B. `push` to `main` only (`if: github.event_name == 'push'`)** — the smallest, quietest surface: one report per merged change, no PR comments, no fork/secret problem; no patch coverage.
  - **C. `push` to `main` plus PRs, but with the PR upload marked informational** — full data, more conditions to maintain.
- **Answer:** **PENDING**
- **Date:** 2026-10-05
- **Status:** PENDING
- **Incorporated:** no

## Q-7 — May a failed upload turn the `Quality` run red?
- **Step:** P.2 Interrogate
- **Why needed:** The TODO states the requirement "CI must stay green" as if it needed an `if:`/`continue-on-error:` decision, but the action's default already swallows upload errors. The real decision is whether a silently broken upload is acceptable — a dead upload means the badge goes stale with no signal (Q-23).
- **Context:** `codecov-action@v7 action.yml:52-55` → `fail_ci_if_error` default `'false'` ("On error, exit with non-zero code"), `:82-85` → `handle_no_reports_found` default `'false'`. The repo's precedent for a deliberately non-blocking CI step is `uv run ty check src/` with `continue-on-error: true` (`quality.yml:36-37`), and the `dependency-review` comment at `:61-65` records that **no branch protection on `main` depends on these checks**.
- **Question:** What should happen when the upload fails?
  - **A. Keep the default (`fail_ci_if_error: false`) — the upload never fails the job (Recommended)** — CI stays green exactly as today; a dead upload is discovered by looking at Codecov, not by a red check.
  - **B. `fail_ci_if_error: true` on `push` to `main` only** — a broken upload becomes loud where the badge's data comes from, while PR runs stay unaffected; a Codecov outage then blocks the `Quality` run on `main`.
  - **C. `fail_ci_if_error: true` everywhere** — maximum signal, but a third-party outage now reddens every PR, which the TODO explicitly wants to avoid.
- **Answer:** **PENDING**
- **Date:** 2026-10-05
- **Status:** PENDING
- **Incorporated:** no

## Q-8 — Do Codecov's commit status checks stay enabled?
- **Step:** P.2 Interrogate
- **Why needed:** Codecov posts its own commit statuses (`codecov/patch`, `codecov/project`) by default. A `project` status compares against the base commit and can fail a PR **even when the repo's own gate passes** — that would add a second, differently-defined coverage gate, which the TODO puts out of scope ("the gate stays exactly as it is", `docs/todo/codecov-coverage-badge.md:35`).
- **Context:** The only coverage gate today is `[tool.coverage.report] fail_under = 92` (`pyproject.toml:103-105`) enforced by `quality.yml:59`. `quality.yml:61-65` records that no branch protection on `main` depends on CI checks, so a red Codecov status would not block a merge today — but it would still show as a failing check in the PR view, and `structure-map` Q-28 is adding a `mypy scripts/` step to the same workflow, i.e. the check set is already growing.
- **Question:** Should Codecov's commit status checks be enabled?
  - **A. Disable them (`coverage.status.project: false`, `coverage.status.patch: false`) — `fail_under = 92` stays the only coverage gate (Recommended)** — the badge and the trend still work; nothing new can turn a PR red.
  - **B. Leave the defaults (both statuses on)** — free "don't drop coverage in this PR" signal, but it is a second gate with different semantics than `fail_under`, and it can fail PRs the repo's own gate passes.
  - **C. `project` off, `patch` on** — per-PR diff coverage only; still a new failing check on PRs, and patch coverage on a template repo is mostly noise.
- **Answer:** **PENDING**
- **Date:** 2026-10-05
- **Status:** PENDING
- **Incorporated:** no

## Q-9 — Should Codecov comment on pull requests?
- **Step:** P.2 Interrogate
- **Why needed:** A PR comment is new, externally visible behaviour in every PR of a repo whose process is already comment-heavy (review reports, PR descriptions). It is a separate switch from the status checks (Q-8) and it changes what a reviewer sees.
- **Context:** `update-readme`'s review record shows this repo's PRs carry detailed agent-written reports; `docs/verification/update-readme.md` documents a 6-finding review in the PR body. Codecov's comment is posted by the Codecov bot on PR runs that upload (Q-6).
- **Question:** Should Codecov post a coverage comment on PRs?
  - **A. No — `comment: false` (Recommended)** — the badge and the trend are the goal; the PR view stays free of a bot that repeats what the `coverage` job already asserts.
  - **B. Yes — leave the default comment on** — reviewers see per-file deltas, at the cost of a bot comment on every PR that touches code.
  - **C. Comment only when coverage changes materially (commit/behavior thresholds)** — less noise, but more configuration to own.
- **Answer:** **PENDING**
- **Date:** 2026-10-05
- **Status:** PENDING
- **Incorporated:** no

## Q-10 — Is a `codecov.yml` committed to the repo root?
- **Step:** P.2 Interrogate
- **Why needed:** Q-8, Q-9 and possibly Q-11/Q-19 are configured **either** in a tracked `codecov.yml` **or** in the Codecov web UI. UI-only settings are invisible in the repo, so the "dependency decisions must be traceable" rule (`AGENTS.md`, "Dependencies and Existing Packages") would be satisfied only by prose in a verification record, and a future change could not see what is configured.
- **Context:** The repo has no `codecov.yml` today; the action exposes `codecov_yml_path` (`action.yml`) for a non-default location. The repo's precedent for tracked configuration of an external tool is root-level files (`alembic.ini`, `.pre-commit-config.yaml`, `.github/dependabot.yml`). A new root file also joins the DOCS/CHORE file set and the collision surface.
- **Question:** Where does Codecov's configuration live?
  - **A. A tracked root `codecov.yml` with the switches this change decides (Recommended)** — reviewable, diff-visible, inherited by forks of the template, and self-documenting.
  - **B. Codecov UI only; nothing committed** — smaller diff, but the configuration is invisible in the repo and untraceable for downstream users.
  - **C. Commit `codecov.yml` only if Q-8/Q-9 need non-default values** — minimal file set, but the decision then depends on answers to two other questions.
- **Answer:** **PENDING**
- **Date:** 2026-10-05
- **Status:** PENDING
- **Incorporated:** no

## Q-11 — Do the file paths in `coverage.xml` need fixing for Codecov?
- **Step:** P.2 Interrogate
- **Why needed:** The report's per-file names are **not** repo paths. Measured: `filename="authentication/__init__.py"` with `<sources>` = the absolute host roots (`…\src\backend`, `…\src\frontend`). If Codecov does not resolve that, the aggregate number may still be right while the file tree, per-file coverage and patch coverage are wrong or empty — a badge that is half-true.
- **Context:** `[tool.coverage.run] source = ["src/backend", "src/frontend"]` (`pyproject.toml:96-102`) — paths, not module names, deliberately, so the empty `src/frontend` placeholder stays covered. `codecov-action@v7` exposes `disable_file_fixes`, `network_filter`, `network_prefix`, `root_dir`, and `codecov.yml` `fixes:` for exactly this; the CI root is `/home/runner/work/python-template/python-template`.
- **Question:** How are the paths handled?
  - **A. Do nothing; verify in the proof step (Q-3) that Codecov resolved the tree, and only add `fixes:`/`network_filter` if it did not (Recommended)** — Codecov normally strips the `<sources>` prefix; no speculative config, and the verification step is the gate.
  - **B. Add explicit `fixes:` (or `network_filter`/`network_prefix`) up front** — deterministic without a probe, but it is untested config that can itself break the mapping.
  - **C. Change `[tool.coverage.run] source` to `["src"]` so the XML carries repo-relative paths** — makes the report self-describing, but it changes **what is measured** (adds `src/main.py`), moves the `fail_under = 92` number, and crosses the boundary `pyproject-tooling-gaps` set (`docs/todo/pyproject-tooling-gaps.md:47`) — see Q-12.
- **Answer:** **PENDING**
- **Date:** 2026-10-05
- **Status:** PENDING
- **Incorporated:** no

## Q-12 — Is `pyproject.toml` off-limits for this change?
- **Step:** P.2 Interrogate
- **Why needed:** The TODO forbids touching the gate (`docs/todo/codecov-coverage-badge.md:35`), but several tempting fixes (source roots, XML output path, `[tool.coverage.xml]`, a `--cov-fail-under` flag) live in `pyproject.toml`. The scope record needs an explicit "must not change, and what to do if it must" rule, because touching it is a reclassification trigger.
- **Context:** `pyproject.toml:96-105` holds `[tool.coverage.run]` (`branch = true`, `source = ["src/backend", "src/frontend"]`) and `[tool.coverage.report] fail_under = 92` with the comment "Floor of the 2026-09-15 coverage baseline (92.74%); raise as coverage improves". `pyproject-tooling-gaps` (MERGED) put "changing what coverage measures" out of scope (`docs/todo/pyproject-tooling-gaps.md:47`). `structlog-logging` (WAITING) will change the measured number by rewriting `src/backend/logging/`, but not the config.
- **Question:** What is the rule if the upload appears to need a coverage-config change?
  - **A. Hard constraint: `pyproject.toml` is not touched at all; if the upload cannot work without it, stop and reclassify (Recommended)** — the gate stays byte-identical, the DOCS/CHORE classification stays honest, and the fix moves to its own change.
  - **B. Allow non-semantic additions (e.g. `[tool.coverage.xml] output = "coverage.xml"`) but never `source`/`fail_under`/`branch`** — slightly more freedom, but "non-semantic" is a judgement call that can still move the number.
  - **C. Allow any coverage-config change needed to make Codecov correct** — simplest path to a working upload, but it changes the measured set and the gate, so the change is no longer DOCS/CHORE.
- **Answer:** **PENDING**
- **Date:** 2026-10-05
- **Status:** PENDING
- **Incorporated:** no

## Q-13 — Is a badge number that differs from the `fail_under` number acceptable?
- **Step:** P.2 Interrogate
- **Why needed:** The badge will show **Codecov's** computed project coverage, which is not necessarily the same figure `pytest-cov` prints against `fail_under`. With `branch = true`, coverage.py's total mixes line and branch data; Codecov computes its own totals from the XML. If the README shows 91% while CI passes a 92 floor, the badge reads like a contradiction of a green gate.
- **Context:** Measured XML from a partial run: `line-rate="0.1533"`, `branch-rate="0.08996"`, while pytest-cov reported a single combined total of `14.21%` — i.e. the XML carries line and branch rates separately and the tool computes the headline number. `pyproject.toml:103-105` documents the floor as "Floor of the 2026-09-15 coverage baseline (92.74%)".
- **Question:** How is the badge's number treated?
  - **A. Accept Codecov's own project total; state in the verification record that it is Codecov's figure, not the `fail_under` figure (Recommended)** — no extra config; the badge is a trend, the gate is the gate.
  - **B. Configure Codecov to report the same measure as the gate (e.g. line-only totals)** — the two numbers agree, but it is more config to own and it hides branch coverage, which the repo deliberately measures (`branch = true`).
  - **C. Require the two numbers to match and treat a mismatch as a defect to fix in this change** — strongest honesty, but it may force a `pyproject.toml` change (Q-12) and could reclassify the change.
- **Answer:** **PENDING**
- **Date:** 2026-10-05
- **Status:** PENDING
- **Incorporated:** no

## Q-14 — Which action reference does the step use?
- **Step:** P.2 Interrogate
- **Why needed:** The TODO says "the `codecov/codecov-action` action, **pinned**" (`docs/todo/codecov-coverage-badge.md:30`), but "pinned" has three meanings here, and the repo has an established convention plus a Dependabot ecosystem that behaves differently for each.
- **Context:** `GET /repos/codecov/codecov-action/tags` → latest `v7.1.1`, plus `v7`, `v6`, `v5.5.5`. Every existing action ref in this repo is a **major tag**: `actions/checkout@v7`, `astral-sh/setup-uv@v7`, `actions/setup-python@v7` (`quality.yml:48,50,52`), `actions/dependency-review-action@v5` (`:71`). `.github/dependabot.yml` has a `github-actions` ecosystem (weekly), so Dependabot opens PRs for both tag and SHA refs.
- **Question:** Which ref form?
  - **A. `codecov/codecov-action@v7` — major tag, matching the repo convention (Recommended)** — consistent with the other four refs; Dependabot keeps it current; a breaking major can land via a Dependabot PR.
  - **B. Full commit SHA pin (`@<sha> # v7.1.1`)** — supply-chain strongest and still Dependabot-maintained, but it is the only SHA pin in the workflow and makes the file inconsistent.
  - **C. Exact version tag `@v7.1.1`** — reproducible today, but nothing updates it automatically except Dependabot, and it matches no existing line in this repo.
- **Answer:** **PENDING**
- **Date:** 2026-10-05
- **Status:** PENDING
- **Incorporated:** no

## Q-15 — Step in the existing `coverage` job, or a separate job?
- **Step:** P.2 Interrogate
- **Why needed:** It decides the CI cost (one runner minute vs a whole new job), whether the upload can fail independently, and whether an artifact hand-off is needed at all.
- **Context:** The `coverage` job is `quality.yml:45-59` (checkout → setup-uv → setup-python → `uv sync --only-group dev` → `uv run pytest tests/ --cov --cov-report=xml`). The workflow already has 8 jobs, and `pyproject-tooling-gaps` added the `complexity` job (`:120-137`), so job count is a real cost axis. A separate job would need `actions/upload-artifact` + `download-artifact` because jobs do not share a workspace.
- **Question:** Where does the upload step go?
  - **A. A step appended to the `coverage` job after `:59` (Recommended)** — zero extra runner minutes, `coverage.xml` is right there, no artifact plumbing; the only downside is that an upload failure appears inside the same job.
  - **B. A new `coverage-upload` job with `needs: coverage` + artifact upload/download** — clean isolation and its own red/green signal, but ~2 extra minutes and two more action refs to maintain.
  - **C. A step in the `coverage` job but with its own `if:` and name so it is visibly separate** — same cost as A, slightly clearer in the run view.
- **Answer:** **PENDING**
- **Date:** 2026-10-05
- **Status:** PENDING
- **Incorporated:** no

## Q-16 — Explicit report path or the action's auto-search?
- **Step:** P.2 Interrogate
- **Why needed:** The action searches the workspace for reports by default. In this repo that search currently finds exactly one XML, but a search that silently finds nothing (or finds a future second report) is a failure mode the workflow should not rely on.
- **Context:** `codecov-action@v7` inputs include `files`, `directory`, `disable_search`, `exclude`, and `handle_no_reports_found` (default `'false'`, `action.yml:82-85`). `.gitignore` already excludes `coverage.xml`, `nosetests.xml`, `htmlcov/`, so no other report is tracked; the pytest step at `quality.yml:59` writes `coverage.xml` in the workspace root.
- **Question:** How is the report located?
  - **A. Explicit `files: coverage.xml` (Recommended)** — self-documenting, immune to a future second report, and a missing report is a clear error rather than a fuzzy search result.
  - **B. Rely on the auto-search (no `files:` input)** — shortest diff, and it works today; but "found nothing" and "found the wrong thing" are both invisible.
- **Answer:** **PENDING**
- **Date:** 2026-10-05
- **Status:** PENDING
- **Incorporated:** no

## Q-17 — Should the upload run when the coverage step failed?
- **Step:** P.2 Interrogate
- **Why needed:** By default a job stops at the first failing step, so on a run where coverage dropped below 92 and the `coverage` job fails, **nothing is uploaded** — the trend line gets a hole exactly on the runs that matter. Uploading anyway would push a partial/failed run into the trend.
- **Context:** `quality.yml:58-59` is the last step of the job today; `fail_under = 92` makes that step the gate. Codecov's own project status is separately decided in Q-8.
- **Question:** Does the upload run after a failed coverage step?
  - **A. No — upload only when the coverage step succeeded (default, no `if:` needed) (Recommended)** — the trend contains only real, gate-passing runs; a below-floor run is already red in CI.
  - **B. Yes — `if: always()` so even failing runs are uploaded** — an unbroken trend line including regressions, but Codecov then stores runs the repo declared unacceptable.
  - **C. Yes, but flagged with a Codecov flag (e.g. `failing-gate`) so they are separable** — full history with a filter, but only meaningful if Q-19 introduces flags, and more configuration to own.
- **Answer:** **PENDING**
- **Date:** 2026-10-05
- **Status:** PENDING
- **Incorporated:** no

## Q-18 — Is `coverage.xml` also kept as a GitHub artifact?
- **Step:** P.2 Interrogate
- **Why needed:** The TODO lists "its artifact handling" as in scope (`docs/todo/codecov-coverage-badge.md:30`), but nothing in the repo consumes an artifact today, and an artifact is a second copy of the same data with a retention cost.
- **Context:** `grep` over `.github/workflows/` shows **no** `upload-artifact`/`download-artifact` step in any of the three workflows; the coverage number is visible in the pytest output (`quality.yml:58-59` prints the coverage table).
- **Question:** Should the workflow upload `coverage.xml` as a workflow artifact?
  - **A. No — Codecov is the artifact store (Recommended)** — no new action ref, no storage, nothing to expire; the report is browsable on Codecov.
  - **B. Yes, always (`actions/upload-artifact`)** — the raw report is inspectable without a third-party account, at the cost of one more action and per-run storage.
  - **C. Yes, only on failure (`if: failure()`)** — debugging aid without routine cost, but it adds a conditional step to a job that currently has none.
- **Answer:** **PENDING**
- **Date:** 2026-10-05
- **Status:** PENDING
- **Incorporated:** no

## Q-19 — Does the upload carry a Codecov flag?
- **Step:** P.2 Interrogate
- **Why needed:** Flags group reports (e.g. by test suite or by branch). This repo has a single coverage run, so flags are probably pointless — but if the badge is flag-scoped, an unflagged upload makes the badge read empty, so the two must be decided consistently.
- **Context:** `codecov-action@v7` input `flags` (`action.yml:59-61`, "Comma-separated list of flags to upload to group coverage metrics"). The repo runs exactly one coverage command (`quality.yml:59`); there is no matrix build (`python-3.15` P.2 records "**no CI matrix exists** — 11 jobs hard-pin the literal", `docs/todo/python-3.15.md:69`).
- **Question:** Are flags used?
  - **A. No flags — one ungrouped report per run (Recommended)** — simplest badge, nothing to keep in sync; flags would only matter with multiple suites.
  - **B. One flag (e.g. `unittest`) on every upload** — future-proof for a second suite, but the badge must then be flag-scoped or it can read empty.
  - **C. Flags per branch/event (`main` vs PR)** — separates the trend, but the badge then needs an explicit branch/flag selector (Q-20).
- **Answer:** **PENDING**
- **Date:** 2026-10-05
- **Status:** PENDING
- **Incorporated:** no

## Q-20 — Which badge URL form goes in the README?
- **Step:** P.2 Interrogate
- **Why needed:** Three different URL families produce a coverage badge, they differ in whether the branch is pinned, and one of them (shields.io) is a third-party proxy of a third-party value. The repo's badge row is strict about form and `owner/repo` (`docs/verification/update-readme.md:358`).
- **Context:** Measured 2026-10-05, all for `jackthenet/python-template`: `https://codecov.io/gh/<owner>/<repo>/graph/badge.svg` → 200 (`unknown` today); `…/branch/main/graph/badge.svg` → 200; `https://img.shields.io/codecov/c/github/<owner>/<repo>` → 200, JSON `{"message":"unknown","color":"lightgrey"}`. Existing row form: `[![Alt](svg)](target)` at `README.md:3-9`; three badges use GitHub's own workflow badge, four use `img.shields.io`.
- **Question:** Which badge URL?
  - **A. Codecov's own badge, default-branch form: `https://codecov.io/gh/jackthenet/python-template/graph/badge.svg` (Recommended)** — one hop to the source of the number, no branch literal to update if the default branch changes, matches how Codecov documents its badge.
  - **B. Branch-pinned legacy form: `…/branch/main/graph/badge.svg`** — explicit about which branch the number comes from, but hard-codes `main` in `README.md`.
  - **C. shields.io proxy: `https://img.shields.io/codecov/c/github/jackthenet/python-template`** — visually consistent with the four shields badges already in the row, but adds a second network hop and shields.io caching between the measurement and the display.
- **Answer:** **PENDING**
- **Date:** 2026-10-05
- **Status:** PENDING
- **Incorporated:** no

## Q-21 — What does the badge link to, and what is its alt text?
- **Step:** P.2 Interrogate
- **Why needed:** The `update-readme` skill rule the repo now follows requires every badge to have alt text and to link to the relevant page (`docs/todo/update-readme.md:44`), and the merged row obeys it (`README.md:3-9`, alt text = the target's name). The coverage badge needs both decided, or the row becomes inconsistent.
- **Context:** Existing pattern: `[![Quality](…/quality.yml/badge.svg)](…/quality.yml)` — alt text equals the target's name; `[![Ruff](https://img.shields.io/badge/lint-ruff-blue)](https://docs.astral.sh/ruff/)` — alt text names the tool, link points at the tool's page. `https://codecov.io/gh/jackthenet/python-template` currently answers **301** (redirect, i.e. the project page exists as a URL even before activation).
- **Question:** Alt text and link target for the coverage badge?
  - **A. `[![Coverage](…/graph/badge.svg)](https://codecov.io/gh/jackthenet/python-template)` — alt "Coverage", links to the Codecov project page (Recommended)** — matches the row's "alt names the thing, link goes to the thing's page" pattern.
  - **B. Alt "Codecov", same link** — names the service rather than the metric; consistent with the `Ruff`/`uv`/`pre-commit` badges that name the service.
  - **C. Alt "Coverage", no link (bare image)** — shortest line, but breaks the row's rule that every badge links somewhere.
- **Answer:** **PENDING**
- **Date:** 2026-10-05
- **Status:** PENDING
- **Incorporated:** no

## Q-22 — Where in the badge row does the coverage badge go?
- **Step:** P.2 Interrogate
- **Why needed:** The row is a single 7-line block and two other planned changes will insert into it (`security-changelog-license`, Q-27). A stated position keeps the diff predictable and the merge conflicts trivial.
- **Context:** `README.md:3-9` order today: three GitHub workflow status badges (`Quality`, `Lint`, `Spec Validation`), then four shields badges (`Python >=3.14`, `Ruff`, `uv`, `pre-commit`). The `update-readme` procedure's badge guidance groups status badges first, tooling after (`docs/todo/update-readme.md:41-47`).
- **Question:** Which position?
  - **A. Immediately after the three workflow status badges (line 6) — status first, then measurement, then tooling (Recommended)** — the coverage badge is a measured status, so it sits with the other status badges and before the static tooling badges.
  - **B. At the end of the row (after `pre-commit`)** — zero reordering of existing lines, smallest diff, but a measurement badge buried among tool badges.
  - **C. Directly after the title with no grouping rule** — no; it destroys the existing grouping the merged `update-readme` established.
- **Answer:** **PENDING**
- **Date:** 2026-10-05
- **Status:** PENDING
- **Incorporated:** no

## Q-23 — What happens when the badge goes stale or reads `unknown`?
- **Step:** P.2 Interrogate
- **Why needed:** A badge is a standing claim. If Codecov stops receiving reports (revoked token, service outage, the repo uninstalled from Codecov), `README.md` keeps showing either an old number or `unknown` — and with `fail_ci_if_error: false` (Q-7) nothing tells anyone. The repo needs a stated policy, not silence.
- **Context:** Measured: the badge endpoints already serve `unknown` today with no Codecov configured at all (preamble item 12). The repo has no monitoring of external services, and `docs/verification/update-readme.md:104` already flagged as unverifiable that "the *status colour* each workflow badge renders is GitHub run history, not observable offline".
- **Question:** What is the staleness policy?
  - **A. Document it as an accepted limitation in the verification record; fix it by inspection if the badge reads `unknown` (Recommended)** — no new machinery for a template repo; the honest statement is on record.
  - **B. Add a CI check that the badge is not `unknown` (a small script or a `curl` assertion)** — automated honesty, but it adds a network-dependent check to CI and a script to maintain.
  - **C. Remove the badge as soon as the upload stops working (a manual rule in `AGENTS.md`)** — strongest honesty, but it requires noticing, and it re-opens the `update-readme` deny-list question of what the row may contain.
- **Answer:** **PENDING**
- **Date:** 2026-10-05
- **Status:** PENDING
- **Incorporated:** no

## Q-24 — ADR, verification record, or both for the service decision?
- **Step:** P.2 Interrogate
- **Why needed:** `AGENTS.md` says dependency decisions "must be traceable … Record the decision in an ADR", and the TODO plans only a verification-record entry (`docs/todo/codecov-coverage-badge.md:32`). The two rules point at different files, and the answer changes the change's file set.
- **Context:** `docs/decisions/` holds ADR-000…ADR-082 (ADR-081 is absent — the next free number is **ADR-083**). Existing ADRs cover dependency and placement decisions, e.g. `ADR-002-loguru-logging-backend.md` (a dependency choice now being superseded by `ADR-082`), and `AGENTS.md`'s "Dependencies and Existing Packages" section ends with "Record the decision in an ADR". The decompose skill's threshold ("an ADR is required only for a decision that introduces a new dependency, a new pattern/architecture element, or a cross-feature interface") is met by a new external service — but that threshold is written for Phase 2 (FEATURE/CROSS-CUTTING), which DOCS/CHORE skips.
- **Question:** Where is the Codecov decision recorded?
  - **A. `docs/verification/codecov-coverage-badge.md` only (Recommended)** — the decision is one CI step plus one badge, the type skips Phase 2, and the record already carries the why/cost/unreachable-case; no ADR-number churn for a chore.
  - **B. A new `ADR-083-…` **plus** the verification record** — literal compliance with the "record the decision in an ADR" rule and a durable "why an external service is allowed" precedent for this template's users.
  - **C. ADR only** — the verification record then lacks the operational detail (what to do when Codecov is unreachable) the TODO promises.
- **Answer:** **PENDING**
- **Date:** 2026-10-05
- **Status:** PENDING
- **Incorporated:** no

## Q-25 — Does the change stay DOCS/CHORE (and therefore get no version bump)?
- **Step:** P.2 Interrogate
- **Why needed:** The change adds a step to a CI job and a visible badge, and depending on Q-6/Q-8 it may add a status check or a PR comment — arguably externally observable. The type decides whether a spec + approval PR exist, which phases run, and whether `bump-my-version bump minor` fires.
- **Context:** `AGENTS.md` classification criterion #5 is explicit: "**DOCS/CHORE** — the change **does not alter behavior**: documentation, comments, configuration, **CI**, tooling", and the bump table gives DOCS/CHORE **no** bump. Precedent: `update-readme` (DOCS/CHORE, "no version bump", `docs/todo/update-readme.md` Phase 6 row) and `pyproject-tooling-gaps` (started DOCS/CHORE, **reclassified** once `src/` code had to change, `docs/todo/pyproject-tooling-gaps.md:56`).
- **Question:** Confirm the classification.
  - **A. DOCS/CHORE as classified — no spec, no approval PR, Phase 4 direct, no version bump (Recommended)** — CI + README only, no `src/`/`tests/` change, and the answers above keep the observable surface to a badge.
  - **B. Reclassify to FEATURE — spec + approval PR + `minor` bump** — defensible if Q-8/Q-9 turn the change into new PR-visible behaviour (status checks, bot comments), at the cost of a spec for a CI step.
  - **C. Reclassify to CROSS-CUTTING** — only if the upload is treated as shared infrastructure spanning features; nothing in the repo supports that reading (no `src/` feature is touched).
- **Answer:** **PENDING**
- **Date:** 2026-10-05
- **Status:** PENDING
- **Incorporated:** no

## Q-26 — What is the Phase 5 evidence set for a CI-only change?
- **Step:** P.2 Interrogate
- **Why needed:** DOCS/CHORE Phase 5 is "lint and type checks where applicable; confirm no test files or behavior were touched" — but this change's real gate is a **CI run**, which no local command can produce. Without naming the evidence, Phase 5 either runs the full suite for nothing or claims a gate that was never observed.
- **Context:** Precedent from the merged `update-readme` (also README-only): Phase 5 light gate = `ruff check .` clean, `mkdocs build --strict` exit 0, `check_traceability.py` PASS, diff limited to the allowed paths (`docs/todo/update-readme.md` Phase 4+5 row). For this change the diff is `.github/workflows/quality.yml` (+ maybe `codecov.yml`, `README.md`, one verification record) — no Python file, so `mypy`/`pytest` prove nothing about it, and the `Quality` run **of the PR itself** is the only place the upload step executes.
- **Question:** Which evidence closes Phase 5?
  - **A. `ruff check .` + `mkdocs build --strict` + `check_traceability.py` + the PR's own `Quality` run showing the upload step executed, plus the Q-3 proof on `main` after merge (Recommended)** — every claim has an observation, and the full test suite is not re-run for a YAML edit.
  - **B. A + the full `uv run pytest tests/` suite** — matches the default DOCS/CHORE reading of "no behavior delta", but the suite cannot observe a workflow change.
  - **C. Only the CI run** — cheapest, but leaves the README link/badge-row checks (the `update-readme` precedent) unverified.
- **Answer:** **PENDING**
- **Date:** 2026-10-05
- **Status:** PENDING
- **Incorporated:** no

## Q-27 — Sequencing against `security-changelog-license` (same badge row)?
- **Step:** P.2 Interrogate
- **Why needed:** Both changes insert one line into the same 7-line block of `README.md`. Whoever merges second must re-read the row, and an unstated order guarantees a conflict in a file neither change can regenerate.
- **Context:** `security-changelog-license` is **QUESTIONS-ANSWERED** and states it "adds the License badge to the badge row" and "the badge row must be re-read, not assumed" (`docs/todo/security-changelog-license.md:28-29`). This change inserts a coverage badge (Q-22). The repo's precedent for exactly this situation is `update-readme` Q-2 = **(a)**: land independently, no `Depends on:`, whoever lands second re-reads the file (`docs/todo/update-readme.md:80`).
- **Question:** Is there a dependency between the two changes?
  - **A. No dependency; each re-reads `README.md:3-9` before editing, whoever merges second rebases (Recommended)** — matches the `update-readme` Q-2 precedent; the two lines are independent, so the conflict is one-line and trivial.
  - **B. Add `Depends on: security-changelog-license`** — a guaranteed-conflict-free order, but it blocks a CI change behind a licensing change that has its own open decisions.
  - **C. Coordinate one combined badge-row edit (one change writes the row)** — one clean diff, but it merges two unrelated decisions into one PR and breaks the `update-readme` ownership split.
- **Answer:** **PENDING**
- **Date:** 2026-10-05
- **Status:** PENDING
- **Incorporated:** no

## Q-28 — Sequencing against the changes that also edit `quality.yml`?
- **Step:** P.2 Interrogate
- **Why needed:** Three other backlog items edit the same workflow file, and one of them edits the inside of the very job block this change appends a step to. Unstated, the four changes will rebase against each other; stated, the edit is a one-step append that survives any order.
- **Context:** `structure-map` (QUESTIONS-ANSWERED) Q-28 answer: "Add `uv run mypy scripts/` to the gate — AGENTS.md Tooling and the CI quality job (`quality.yml`) both check `scripts/`". `python-3.15-upgrade` (PREPARING) and `python-3.15` (QUESTIONS-ANSWERED) inventory and edit the **11 `python-version: '3.14'` literals** including `quality.yml:54`, which is inside the `coverage` job (`docs/todo/python-3.15-upgrade.md:29`). `pyproject-tooling-gaps` (MERGED) already added a job to the same file. The repo's precedent is "whichever merges second rebases those lines" (`docs/todo/python-3.15.md:47`).
- **Question:** Is there a dependency or ordering rule for `quality.yml`?
  - **A. No dependency; this change only appends one step after `quality.yml:59`, and whoever merges second rebases (Recommended)** — an append at the end of a job block is the least conflict-prone edit in the file.
  - **B. Add `Depends on: structure-map` (and/or `python-3.15-upgrade`)** — one clean rebase instead of several, but it stalls a small CI change behind larger ones.
  - **C. Land this change first, before the `quality.yml`-heavy items start** — cheapest for this change, but it is a scheduling claim the orchestrator cannot guarantee.
- **Answer:** **PENDING**
- **Date:** 2026-10-05
- **Status:** PENDING
- **Incorporated:** no

## Q-29 — Is the setup documented for downstream users of this template?
- **Step:** P.2 Interrogate
- **Why needed:** This repository is a **template** ("Default template for Python projects", `pyproject.toml:4`), and the merged `update-readme` front page advertises the CI gates. A hard-coded Codecov upload for `jackthenet/python-template` is a step that silently does nothing (or fails) in every fork — so whether the setup is documented is a real scope question, not a nice-to-have.
- **Context:** `README.md:50-78` ("Development") already lists the coverage command (`:57`, `uv run pytest tests/ --cov --cov-report=xml # coverage gate (fail_under = 92)`) and names the three workflows that run the same checks (`:75-78`); `userdocs/` carries no badges and no CI page; the `update-readme` skill rule is "never invent URLs or badges for services the project doesn't use" — the mirror-image problem is a badge that points at the *upstream* repo from a fork.
- **Question:** Does this change document the Codecov setup for forks?
  - **A. No new prose beyond the verification record — the badge and the step are repo-specific plumbing (Recommended)** — smallest diff; the fork problem is real but is a template-usability question for another change.
  - **B. Add 2–3 lines to `README.md` "Development" (or a `codecov.yml` comment) stating what a fork must configure** — keeps the template honest for its actual audience, at the cost of touching the README beyond the badge line.
  - **C. Make the upload conditional so forks without the secret skip it cleanly** — operationally the tidiest, but it is more workflow logic and overlaps Q-6/Q-7.
- **Answer:** **PENDING**
- **Date:** 2026-10-05
- **Status:** PENDING
- **Incorporated:** no

## Late questions (Phases 2–6)

<questions discovered after the change entered the workflow; same entry format, Step field set to the step that found it>
