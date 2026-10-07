# Questions: ruff-d-docstrings

One question file per change, created at **P.1 Frame** from this template and named `ruff-d-docstrings.md`. It replaces the retired central `AI_Questions.md` (archived at `docs/questions/archive-AI_Questions.md`).

- **Change:** ruff-d-docstrings (DOCS/CHORE)
- **TODO file:** `docs/todo/ruff-d-docstrings.md`
- **Spec:** n/a
- **Opened:** 2026-10-04
- **Status:** OPEN  <!-- OPEN | ALL ANSWERED — set OPEN by the orchestrator at P.1; ALL ANSWERED once every question in this file has an answer (the orchestrator records it together with the `QUESTIONS-ANSWERED` TODO advance) -->
- **Answer rounds:** 1  <!-- round 1, 2026-10-07: Q-1..Q-4 answered; round 2 (Q-5..Q-7 + the Q-3/Q-4 conflict) raised the same day -->

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

### P.2 Interrogate preamble — 2026-10-05

**28 questions** in one `BLOCKED-USER` batch (DOCS/CHORE: every genuine open decision is recorded; the ≥20 floor is met, nothing padded). Most blocking first: rule set → scope → increment shape → docstring content policy → docs/config → sequencing → evidence/escalation/versioning.

**Re-measured today** (`main` @ `305add3`, ruff `0.16.9` — the TODO's 379 is stale, +7):

| Tree | `--select D` | `D1xx` (missing) | `D2xx`/`D3xx`/`D4xx` (format/phrasing) |
|---|---|---|---|
| `src/` | **386** | **198** — D102 131, D107 51, D101 14, D105 2 | 188 — D205 66, D401 58, D209 57, D403 4, D301 3 |
| `tests/` | **762** | 468 — D103 358, D104 42, D102 49, D107 19 | 294 — D205 130, D209 109, D401 53, D301 2 |
| `scripts/` | **3** | D103 3 | 0 |
| `migrations/` | **11** | D100 1, D103 4 | D400 2, D415 2, D401 2 |
| `.github/hooks/ruff-post-edit.py` | **1** | D103 1 | 0 |
| `userdocs/` | **0** — no Python there | — | — |
| repo-wide (`ruff check .`) | **1 164** | — | — |

- **The published surface is where the work is:** **195 of the 198** `src/` `D1xx` sites sit on objects listed in a feature's `__all__` (the mkdocstrings surface) — only 3 do not. Per feature (`__all__`-published `D1xx`): authentication 50, usermanagement 45, filemanagement 37, permissions 32, settings 14, mail 6, search 6, eventbus 3, sessionmanagement 2.
- **`userdocs/api.md:7-14` renders only 8 packages** — `permissions` (32) and `search` (6) are exported but **not rendered**, so 38 of the 195 are currently invisible to readers; `shared` is not rendered either.
- **File spread:** 43 `src/` files carry a `D` violation — 36 have `D1xx`, of which 18 need *only* new docstrings, 8 need *only* reformatting, 17 need both. The `D102` bulk is repetitive repository/service ABCs: `permissions/repositories.py` 20, `authentication/repository.py` 18, `filemanagement/repository.py` 16, `usermanagement/service.py` 14, `usermanagement/repository.py` 14, `authentication/service.py` 11, `settings/repository.py` 10, `filemanagement/storage.py` 10.
- **Style is measured, not assumed:** `grep` over `src/` finds **0** docstrings using `Args:` / `Returns:` / `Raises:` / `Parameters:` / `:param:` — the existing style is plain prose (e.g. `src/backend/authentication/repository.py:57` "The on-disk file path for a file-based SQLite URL, else ``None``.").
- **Convention costs (`--select D` + `[tool.ruff.lint.pydocstyle] convention`, `src/`):** `google` → **328** (D401 off), `numpy` → **335** (D107 off), `pep257` → **386**. Plain `select = ["D"]` with no convention prints two warnings on **every** ruff run (D203/D211 and D212/D213 are incompatible pairs).
- **Gate mechanics:** `lint.yml:37` runs `uv run ruff check .` **repo-wide**, but the workflow's `paths:` filter (`lint.yml:6-13`) fires only on `src/**`, `tests/**`, `pyproject.toml`, `.pre-commit-config.yaml`, `lint.yml`, `.github/hooks/**` — a `scripts/`-only or `migrations/`-only PR never runs the lint job. `pyproject.toml:224` `quality_check` also runs `ruff check .` (Phase 5 parity). `ruff check .` and `ruff format --check .` are **green on `main` today** — the gate must stay green.
- **There is no `[tool.ruff.lint.per-file-ignores]` section in `pyproject.toml` today** (the task-definition assumed entries exist; they do not) — adding one would be a new config element, not an edit.
- **Tool-version skew found:** pre-commit runs ruff **v0.15.12** (`.pre-commit-config.yaml:11`) while the dev group pins `ruff>=0.16.9` (`pyproject.toml:62`). `D` rule sets move between ruff versions, so the local hook and CI can disagree about what is documented.

**Closed from evidence — not asked:** `D100`/`D103`/`D104` in `src/` are already **0** (every module, every feature `__init__.py`, and every public module-level function is documented — the earlier "0 missing module docstrings" holds); no `@logged_class` class lacks a docstring (0 of 45), so `docs/specs/logging-coverage.md:120` REQ-009 / AC-009 (`tests/acceptance/logging_coverage/test_docstrings.py::test_traced_class_docstrings_mention_tracing`) is green today; all 5 `@property`/`@cached_property` in `src/` are documented; `src/` has no `__post_init__`; `D1xx` never fires on private functions, so `_setup.py`-style internals are outside the rule by construction; `userdocs/` holds no Python.

**Overlap check** (`docs/specs/` grepped for `docstring`; all 22 live TODOs read):
- `pyproject-tooling-gaps` — **MERGED** (PR #68, `a278bd2`); its Q-9 decision is `docs/verification/pyproject-tooling-gaps.md:164` ("Ruff `D` … stays out of `select`; the backfill is its own backlog item"); its final `select` added `DTZ`. Nothing else in the backlog touches `[tool.ruff.lint] select` (grep over every TODO: 0 hits) — this change owns that list now.
- `structlog-logging` — **WAITING, in flight** (worktree `crosscut/structlog-logging`, Phase 3: tests written, `src/` untouched). Its Phase 4 rewrites `src/backend/logging/` (3 `D` sites today) and its branch already measures **tests 795 vs main 762 (+33 `D`)**. Direct sequencing question (Q-21).
- `structure-map` — **QUESTIONS-ANSWERED, next step P.4**. It adds `scripts/make_map.py`, adds `uv run mypy scripts/` to the gate (its Q-28a), edits `AGENTS.md` (Project Structure + Skill-to-Phase rows + a tooling line), and its generated `STRUCTURE.md` embeds **each module's docstring summary** — so docstring work changes its output, and both changes want `AGENTS.md` and `scripts/` (Q-22).
- `api-keys` / `notifications` — **WAITING FEATURE**, both `Depends on: structlog-logging`; they will add new public API. No collision, but they decide whether new code arrives already `D`-clean (Q-5/Q-7).
- `settings-public-registry-setter` — **PREPARING**, will touch `src/backend/settings/` (14 `D1xx` there) — same-file overlap, small.
- `python-3.15-upgrade` — trigger-gated, edits `pyproject.toml` but not `[tool.ruff.lint]`. `workflow-docs-nits`, `track-python-skill`, `update-readme`, `architecture-tests-missing`, `remove-spec-tdd-driver` — **MERGED**, no overlap. `docs-path-ci-trigger` — **DROPPED**.
- No spec in `docs/specs/` requires docstrings except `logging-coverage.md` REQ-009/AC-009 (traced-class wording, Q-17). `scripts/verify_spec.py:63` shows the "orphaned acceptance test" check that would read test docstrings is **skipped**, so test docstrings are a human traceability convention, not a CI-parsed one (Q-4).

## Q-1 — Which `D` codes enter `[tool.ruff.lint] select`?
- **Step:** P.2 Interrogate
- **Why needed:** The TODO leaves the rule subset open ("`D1xx` only versus the full `D` family"), and the subset decides the size of the whole change (198 vs 386 in `src/`, 198 vs 1 164 repo-wide) and what future changes are held to.
- **Context:** `pyproject.toml:182` `select` today has `I,E,W,B,F,UP,RUF,PL,Q,SIM,C4,DTZ` — no `D`. Measured `--select D src` → 386 (`D1xx` 198, format/phrasing 188); `--select D1 src` → 198. `pyproject-tooling-gaps` Q-9 (`docs/verification/pyproject-tooling-gaps.md:164`) deferred exactly this decision.
- **Question:** Which `D` codes go into `select`?
- **Options:**
  - **(a) `"D"` plus `[tool.ruff.lint.pydocstyle] convention = "google"` (Recommended)** — 328 `src/` sites today; one line of config, silences the two incompatible-rule warnings, matches the mkdocstrings default parser, and drops the 58 D401 imperative-mood rewrites.
  - **(b) `"D1"` only** — 198 sites, the smallest gate and the smallest diff; docstring *formatting* stays unenforced and can drift again.
  - **(c) `"D"` with no convention (pep257)** — 386 sites; every ruff run prints two incompatible-rule warnings until one of each pair is ignored by hand.
  - **(d) A hand-written code list** (e.g. `"D1","D2","D3","D400","D403"`) — maximum control, but every future ruff release adds a `D` code that is silently outside the list.
- **Answer:** **(a) `"D"` plus `[tool.ruff.lint.pydocstyle] convention = "google"`** (user, 2026-10-07). Full `D` family, google convention: 328 `src/` sites today, one config line, no incompatible-rule warnings, matches the mkdocstrings default parser, and D401 (imperative mood) is off — which also keeps the existing `AC-009: …` style test docstrings legal.
- **Date:** 2026-10-07
- **Status:** ANSWERED
- **Incorporated:** yes — P.4 scope: `pyproject.toml` `[tool.ruff.lint] select` gains `"D"`; a new `[tool.ruff.lint.pydocstyle] convention = "google"` section is added

## Q-2 — Which docstring style do the new docstrings follow?
- **Step:** P.2 Interrogate
- **Why needed:** The docstrings are published output (`userdocs/api.md` → mkdocstrings), so the style is a documentation decision, not a lint detail — and it decides whether parameter sections exist at all.
- **Context:** `grep` over `src/` finds **0** docstrings with `Args:`/`Returns:`/`Raises:`/`Parameters:`/`:param:` — the house style is one prose sentence, sometimes with a second paragraph citing REQ IDs (`src/backend/filemanagement/search_source.py:100`, `:113`). `mkdocs.yml:13` configures `mkdocstrings` with `default_handler: python` and **no** handler options, so the parser is griffe's default (google). AGENTS.md:737 says only "concise docstrings; explain *why*".
- **Question:** Which docstring style is normative for the backfill and for future code?
- **Options:**
  - **(a) Plain prose summary (current house style), no parameter sections (Recommended)** — zero parser coupling, smallest diff, consistent with the 414 docstrings that already exist; parameter docs stay in the type annotations.
  - **(b) Google style with `Args:`/`Returns:`/`Raises:`** — richest published API reference, but every one of the 195 published objects grows a section block and the diff roughly triples.
  - **(c) NumPy style (`Parameters\n ----------`)** — same cost as (b) and needs `docstring_style: numpy` in `mkdocs.yml` to render.
  - **(d) reST/Sphinx (`:param x:`)** — same cost again, needs `docstring_style: sphinx`; nothing in the repo uses it.
- **Answer:** **(b) Google style with `Args:` / `Returns:` / `Raises:`** (user, 2026-10-07) — **not** the recommended plain-prose option. Consequences the user accepted by choosing it: the ~195 published `src/` objects each grow a section block (the diff roughly triples over the missing-docstring count), and the 414 existing prose docstrings become the inconsistent minority unless also converted (raised as a follow-up in round 2). Consistent with Q-1's `convention = "google"`, so ruff enforces the section grammar (`D417` etc.).
- **Date:** 2026-10-07
- **Status:** ANSWERED
- **Incorporated:** yes — P.4 scope: the backfill writes Google sections; `mkdocs.yml` needs no `docstring_style` change (griffe's default is google) — to be re-verified at P.4

## Q-3 — Which trees does the `D` gate cover?
- **Step:** P.2 Interrogate
- **Why needed:** `lint.yml:37` runs `uv run ruff check .` repo-wide, so selecting `D` without a scope decision commits the repo to 1 164 violations, of which only 386 are in `src/`.
- **Context:** Measured: `src/` 386, `tests/` 762, `migrations/` 11, `scripts/` 3, `.github/hooks/ruff-post-edit.py` 1, `userdocs/` 0 (no Python). `pyproject.toml` has **no** `[tool.ruff.lint.per-file-ignores]` section today, so scoping means adding one.
- **Question:** Which trees must satisfy the new `D` codes?
- **Options:**
  - **(a) `src/` only — add `per-file-ignores` for `tests/*`, `scripts/*`, `migrations/*`, `.github/*` (Recommended)** — the gate protects the published API surface; the backfill is 198–386 sites, not 1 164.
  - **(b) `src/` + `scripts/` + `migrations/` + `.github/hooks/`** — 400 sites total; cheap now, but every future alembic autogen file must carry a docstring.
  - **(c) Everything (`ruff check .` as-is)** — 1 164 sites; the biggest backfill in the repo's history and it collides with every in-flight change's tests.
  - **(d) `src/` + `tests/`** — 1 148 sites; makes test intent enforceable but swamps the change.
- **Answer:** **(a) `src/` only** — add `[tool.ruff.lint.per-file-ignores]` for `tests/*`, `scripts/*`, `migrations/*`, `.github/*` (user, 2026-10-07). **Conflict flagged by the orchestrator:** Q-4 was answered "backfill all 313 test docstrings **and gate `tests/`**", which contradicts gating `src/` only. Resolved in round 2 (see the new Q-29).
- **Date:** 2026-10-07
- **Status:** ANSWERED
- **Incorporated:** partially — the `per-file-ignores` section is in scope; whether `tests/*` stays in it waits on Q-29

## Q-4 — Are the 313 undocumented test functions a gap to backfill, or exempt by design?
- **Step:** P.2 Interrogate
- **Why needed:** This is the substance behind the `tests/` half of Q-3, and it is a policy about the test suite, not about docs — 414 of 727 test functions already carry an `AC-XXX:`/`INV-XXX:` docstring, so the repo clearly has a convention, but nothing says it is mandatory.
- **Context:** AST count over `tests/`: 727 `test_*` functions, **414 with a docstring, 313 without** (ruff reports 358 `D103` because helpers count too). Existing docstrings are traceability markers, e.g. `tests/acceptance/logging_coverage/test_docstrings.py:14` "AC-009: each inventory class's docstring mentions tracing". `scripts/verify_spec.py:63` shows the CI check that would read test docstrings ("No orphaned acceptance tests") is **skipped**, so nothing parses them today.
- **Question:** Must every test function carry a docstring (and the `AC-XXX:` prefix), or is the current mix acceptable and `tests/` stays out of the `D` gate permanently?
- **Options:**
  - **(a) Exempt — `tests/` stays out of the `D` gate; the `AC-XXX:` docstring stays a convention, not a rule (Recommended)** — no 313-docstring diff, and it avoids forcing imperative phrasing onto `AC-009: …` docstrings.
  - **(b) Required — backfill all 313 with `AC-XXX:`/`INV-XXX:` docstrings and gate `tests/`** — traceability becomes enforceable, but the change roughly quadruples.
  - **(c) Required only for `tests/acceptance/`** — the category that carries spec evidence gets the rule; unit/property/contract stay free.
  - **(d) Exempt now, separate backlog item for `tests/` later** — keeps this change small and records the intent.
- **Answer:** **(b) Required — backfill all 313 with `AC-XXX:`/`INV-XXX:` docstrings and gate `tests/`** (user, 2026-10-07). Traceability is to be enforceable, not a convention. **Conflict flagged by the orchestrator:** this contradicts Q-3 (a), which exempts `tests/*` via `per-file-ignores`; and with Q-2 = Google style the `tests/` backfill is 468 `D1xx` + 294 format sites, not 313. Resolved in round 2 (Q-29).
- **Date:** 2026-10-07
- **Status:** ANSWERED
- **Incorporated:** pending Q-29 — the intent (test docstrings mandatory + enforced) is recorded; the file set and site count wait on it

## Q-5 — One change, or one change per feature?
- **Step:** P.2 Interrogate
- **Why needed:** The TODO's own risk note says 379 (now 386) is "a lot for one PR" and that a mega-change "invites filler docstrings"; the increment shape decides how many PRs, how many worktrees, and how reviewable each is.
- **Context:** Measured published `D1xx` per feature: authentication 50, usermanagement 45, filemanagement 37, permissions 32, settings 14, mail 6, search 6, eventbus 3, sessionmanagement 2 (195 total, 36 files). The `D102` bulk is repetitive ABC method lists (`permissions/repositories.py` 20, `authentication/repository.py` 18, `filemanagement/repository.py` 16), which is what makes a per-feature split cheap to review.
- **Question:** How is the backfill cut into changes?
- **Options:**
  - **(a) One change, one commit per feature, `select` edit in the last commit (Recommended)** — one PR to review but bisectable per feature; the gate lands green in the same PR and no half-done state exists on `main`.
  - **(b) One change per feature (up to 9), `select` in the last one** — smallest review unit each, but 9 worktrees, 9 PRs, 9 verification records, and `D` enforces nothing until the last one merges.
  - **(c) Two changes: big four (authentication, usermanagement, filemanagement, permissions = 164) then the rest + config** — three PRs, each reviewable.
  - **(d) One sweep PR with no per-feature commits** — fewest ceremony, worst reviewability (the risk the TODO flags).
- **Answer:** **(a) One change, one commit per feature, `select` in the last commit** (user, 2026-10-07). One PR, bisectable per feature, no half-gated state on `main`.
- **Date:** 2026-10-07
- **Status:** ANSWERED
- **Incorporated:** yes — P.4 scope: single change `ruff-d-docstrings`, commit order = 9 feature commits (authentication, usermanagement, filemanagement, permissions, settings, mail, search, eventbus, sessionmanagement) then the config commit

## Q-6 — If it is split, does the orchestrator open the sibling TODOs now?
- **Step:** P.2 Interrogate
- **Why needed:** Phase P's "prepare as many changes as you like" model only pays off if the sibling items exist as TODO + question files with a `Depends on:` chain; otherwise the split lives only in this file and the next one is framed from scratch.
- **Context:** `docs/todo/` holds 22 live items; none of them is a docstring item (overlap check: 0 TODOs touch `[tool.ruff.lint] select`). `pyproject-tooling-gaps` Q-9 created exactly one TODO for this work, so a split means new files at P.1 (orchestrator-owned).
- **Question:** If Q-5 is (b) or (c), does the orchestrator create the sibling `docs/todo/<name>.md` + `docs/questions/<name>.md` pairs now, with `Depends on: ruff-d-docstrings` ordering?
- **Options:**
  - **(a) Yes — create them at P.1 with the chain, and keep this item as the first feature + the config edit (Recommended)** — the backlog shows the real work and the never-idle scheduler can pick them up.
  - **(b) No — keep one TODO and let Phase 4 commits carry the split** — fewer planning records, but the backlog understates the remaining work.
  - **(c) Create one sibling TODO only ("docstrings: tests/" or "docstrings: remaining features")** — one extra record, coarse tracking.
- **Answer:** **(a) Yes — create the sibling pair now** (user, 2026-10-07). Q-5 answered (a) — one change, one commit per feature — so Q-6's "if it is split" premise is false for the `src/` backfill; the sibling the answers actually require is the **`tests/`** one from Q-29. The orchestrator creates `docs/todo/docstrings-tests.md` + `docs/questions/docstrings-tests.md` at P.1 with `Depends on: ruff-d-docstrings` and its own value triage.
- **Date:** 2026-10-07
- **Status:** ANSWERED
- **Incorporated:** yes — `docstrings-tests` framed at P.1 on `main` (2026-10-07), chain recorded in both TODO files

## Q-7 — How does the `select` edit land without ever turning `lint.yml` red?
- **Step:** P.2 Interrogate
- **Why needed:** The TODO makes "the gate must land green" a constraint, and there are two different mechanisms for it; they produce different PR shapes and different intermediate states on `main`.
- **Context:** `lint.yml:37` runs `uv run ruff check .` on every PR touching `src/**` or `pyproject.toml`; `ruff check .` is green on `main` today. `pyproject.toml` has no `per-file-ignores` section, so a ratchet would be new config. A per-file-ignores ratchet would list the not-yet-clean features and shrink as each is documented.
- **Question:** What is the mechanism that keeps the lint job green while the backfill is in progress?
- **Options:**
  - **(a) Docstrings first, `select` in the final commit of the same PR (Recommended)** — `main` is never red, no temporary config to delete, and the PR diff is "docstrings + one config line".
  - **(b) Add `D` to `select` first with a `per-file-ignores` allowlist of the undocumented features, then delete entries feature by feature** — a visible ratchet that stops new violations in already-clean features, but it lands a config block that must later be removed and each intermediate PR re-edits `pyproject.toml`.
  - **(c) Add `D` to `select` only for the features that are clean, extend the selection per PR** — same ratchet effect expressed in `select`, more `pyproject.toml` churn.
- **Answer:** **(a) Docstrings first, `select` gains `"D"` in the final commit of the same PR** (user, 2026-10-07). `main` is never red, no temporary config block to delete, and the PR diff is "docstrings per feature + one config line + the `pydocstyle`/`per-file-ignores` sections".
- **Date:** 2026-10-07
- **Status:** ANSWERED
- **Incorporated:** yes — P.4 commit order: per-feature docstring commits first, `pyproject.toml` `select` edit last; the lint job stays green at every commit

## Q-8 — If intermediate PRs leave `D` off, what guarantees the rest gets done?
- **Step:** P.2 Interrogate
- **Why needed:** Under Q-5 (b)/(c) the config edit lands in the last PR, so between the first and the last merge nothing prevents new undocumented public API from arriving in the not-yet-gated features — the exact drift the change exists to stop.
- **Context:** `api-keys` and `notifications` are WAITING FEATURE items that will each add new public classes and methods; `structlog-logging` is in flight and will add new public logging API. None of them has a docstring requirement in its tasks (grep: 1 `docstring` mention in `.github/task-runner/tasks.json`).
- **Question:** What enforces the remaining features during the gap?
- **Options:**
  - **(a) The `Depends on:` chain plus the backlog records — accept the gap, keep it short (Recommended)** — no temporary config; the gap is only as long as the queue between the sibling changes.
  - **(b) Land the shrinking `per-file-ignores` ratchet from Q-7 (b) so every feature is gated as soon as it is clean** — no gap for completed features, at the cost of churn in `pyproject.toml`.
  - **(c) Do the whole `src/` backfill in one PR (Q-5 a/d) so there is no gap at all** — the gap disappears by construction.
- **Answer:** **Closed by implication (orchestrator, 2026-10-07)** — Q-5 = (a) and Q-7 = (a) mean the whole `src/` backfill and the `select` edit land in **one** PR, so option (c) holds by construction and there is no intermediate ungated window on `main`. The only gap is the one Q-29 accepts: `tests/` stays ungated until `docstrings-tests` merges.
- **Date:** 2026-10-07
- **Status:** ANSWERED
- **Incorporated:** yes — no ratchet config in scope; the gap question is answered by the single-PR shape

## Q-9 — Are `__init__` docstrings required (D107, 51 sites)?
- **Step:** P.2 Interrogate
- **Why needed:** `D107` is 26 % of the whole `src/` `D1xx` backfill (51 of 198), and it is the family where a required docstring is most likely to be pure filler — most of the sites are exception classes.
- **Context:** Measured `D107` sites: `permissions/errors.py` 6, `filemanagement/errors.py` 6, `usermanagement/errors.py` 4, `authentication/repository.py` 3, `settings/repository.py` 3, `search/errors.py` 3, `permissions/repositories.py` 3, `mail/errors.py` 3, plus 26 single sites. ruff's `pydocstyle.convention = "numpy"` disables `D107` (document the class instead); `google`/`pep257` keep it. Whether mkdocstrings merges an `__init__` docstring into the class page is a griffe behaviour to confirm at P.4, not assumed here.
- **Question:** Must the 51 `__init__` methods get their own docstrings?
- **Options:**
  - **(a) Yes, but only where the constructor adds context the class docstring lacks; disable `D107` for `*/errors.py` (Recommended)** — keeps the useful ones, avoids 19 "Initialize self."-class fillers in exception modules.
  - **(b) Yes, all 51, no exemption** — uniform rule, but the exception-class docstrings will be near-empty.
  - **(c) No — disable `D107` globally (the numpy convention choice)** — 51 fewer docstrings; constructor context has to live in the class docstring.
- **Answer:** **(b) Yes, all 51, no exemption** (user, 2026-10-07) — **not** the recommended partial exemption. `D107` stays on for every class including the exception modules (`permissions/errors.py` 6, `filemanagement/errors.py` 6, `usermanagement/errors.py` 4, `search/errors.py` 3, `mail/errors.py` 3, …). Consequence: the exception-class `__init__` docstrings must still pass the Q-15 no-filler rule, so they have to say something the class docstring does not (or the class docstring carries the content and the `__init__` docstring names the constructor's contract). Flagged for the Phase 6 checklist.
- **Date:** 2026-10-07
- **Status:** ANSWERED
- **Incorporated:** yes — no `per-file-ignores` entry for `*/errors.py`; all 51 `D107` sites are in the backfill

## Q-10 — Is `D401` (imperative-mood first line) enforced?
- **Step:** P.2 Interrogate
- **Why needed:** `D401` is the second-largest family in `src/` (58 sites) and it is the one rule that forces a *voice* change on docstrings that are already good — a real style imposition on published text, not a formatting fix.
- **Context:** Examples ruff reports: `src/backend/authentication/repository.py:57` and `src/backend/filemanagement/repository.py:54` — "The on-disk file path for a file-based SQLite URL, else ``None``." (a noun phrase describing a property/lookup); `src/backend/filemanagement/search_source.py:147` "String operators (D4): case-insensitive via the normalized value." ruff's `convention = "google"` disables `D401`; `pep257`/`numpy` keep it. No fix is available for `D401` — every site is a hand rewrite.
- **Question:** Do the 58 descriptive first lines get rewritten to imperative mood, or does `D401` stay off?
- **Options:**
  - **(a) Off — pick the convention that disables it (google) (Recommended)** — descriptive noun phrases are correct for queries and lookups, and 58 hand rewrites add review noise to a docs-only change.
  - **(b) On — rewrite all 58 to imperative mood** — strict PEP 257 voice across the published API reference.
  - **(c) On, but with `# noqa: D401` at the sites where a noun phrase is genuinely better** — the rule stays visible; the exceptions are explicit and greppable.
- **Answer:** **Closed by implication (orchestrator, 2026-10-07)** — Q-1 chose `convention = "google"`, which **disables** `D401`; option (a) therefore holds without a further decision. The 58 descriptive noun-phrase first lines stay as they are.
- **Date:** 2026-10-07
- **Status:** ANSWERED
- **Incorporated:** yes — `D401` is not enforced; no imperative-mood rewrites in scope

## Q-11 — Are the `D2xx` formatting fixes (123 sites in `src/`) part of this change?
- **Step:** P.2 Interrogate
- **Why needed:** They are a separate kind of work from writing docstrings (re-indenting existing ones), and mixing 123 reformatting edits with 198 new docstrings in one diff makes neither reviewable in isolation.
- **Context:** `src/` format families: `D205` 66 (blank line after summary), `D209` 57 (closing quotes on its own line), `D301` 3 (`r"""` — `permissions/catalog.py:1,35`, `settings/repository.py:44`), `D403` 4 (`filemanagement/search_source.py:161`, `search/service.py:283`, `sessionmanagement/search_source.py:143`, `usermanagement/search_source.py:153`). 8 `src/` files need *only* reformatting and no new docstring at all.
- **Question:** Does this change fix the existing docstrings' formatting too?
- **Options:**
  - **(a) Yes — same change, separate commits from the docstring additions (Recommended)** — one config edit covers the whole `D` subset, and the commit split keeps the review readable.
  - **(b) No — select only the codes that are already clean, and defer formatting to a follow-up TODO** — smaller diff now, but the formatting rules stay unenforced.
  - **(c) Only the auto-fixable ones (`D209`, `D301`, `D403`), hand-written `D205` deferred** — cheapest half, but a partial rule set is the confusing middle ground.
- **Answer:** **(a) Yes — same change, separate commits from the docstring additions** (user, 2026-10-07). All 123 `src/` format sites are in scope (`D205` 66, `D209` 57, `D301` 3, `D403` 4); the commit split keeps the two kinds of work reviewable separately.
- **Date:** 2026-10-07
- **Status:** ANSWERED
- **Incorporated:** yes — full `D` subset selected (Q-1) and the format families are part of the backfill, not deferred

## Q-12 — Does `[tool.ruff.lint] fixable` gain the fixable `D` codes?
- **Step:** P.2 Interrogate
- **Why needed:** `pyproject.toml:196` `fixable` is an explicit allow-list (`I, UP035, RUF022, Q000-Q004`), so `ruff check --fix` will **not** touch any `D` code as configured — the mechanical part of the backfill stays manual unless this list grows. The pre-commit hook runs `ruff-check` with `--fix` (`.pre-commit-config.yaml:14`), so widening the list also widens what gets rewritten on every local commit.
- **Context:** ruff 0.16.9 reports: `D209`/`D204`/`D207`/`D208`/`D211`/`D212`/`D403` "Fix is always available"; `D205`/`D200`/`D201`/`D202`/`D210`/`D300`/`D301`/`D400`/`D415` "sometimes"; `D401`/`D402`/`D404`/`D414`/`D417`/`D418`/`D419` no fix. AGENTS.md forbids repo-wide `--fix` during a task step (P-6) and scopes fixes to changed paths.
- **Question:** Should the `fixable` allow-list be extended to the `D` codes this change selects?
- **Options:**
  - **(a) Yes, but scoped to the codes actually selected (Recommended)** — the 123 formatting sites become one command on the changed paths, and pre-commit keeps them from regressing.
  - **(b) No — keep `fixable` as-is and apply the formatting by hand** — nothing new is auto-rewritten in a docs change, at the cost of 123 manual edits.
  - **(c) Yes, and run the fix once as an explicit first step of this change only** — mechanical sweep now, no permanent widening of `fixable`.
- **Answer:** **(a) Yes, scoped to the codes actually selected** (user, 2026-10-07). `[tool.ruff.lint] fixable` gains the fixable `D` codes (always-fixable: `D204`, `D207`, `D208`, `D209`, `D211`, `D212`, `D403`; sometimes-fixable ones stay under ruff's own safety rules). AGENTS.md's P-6 rule still applies: `--fix` is scoped to the step's changed paths, never repo-wide during a task step.
- **Date:** 2026-10-07
- **Status:** ANSWERED
- **Incorporated:** yes — `pyproject.toml` `fixable` allow-list extended in the same config commit as `select`

## Q-13 — Are the two `D105` magic methods documented?
- **Step:** P.2 Interrogate
- **Why needed:** `D105` fires only on `__enter__`/`__exit__`, and the answer sets the precedent for dunder docstrings in a codebase that uses context managers in the event bus and elsewhere.
- **Context:** `src/backend/eventbus/eventbus.py:158` and `:161` are the only `D105` sites in `src/`. AGENTS.md documents the bus as usable as a context manager, so the behaviour is public API and rendered by mkdocstrings (`userdocs/api.md:8`).
- **Question:** Do `EventBus.__enter__` / `__exit__` get docstrings?
- **Options:**
  - **(a) Yes — two one-line docstrings naming the context-manager contract (Recommended)** — it is published behaviour and it clears the rule with no exemption needed.
  - **(b) No — add `D105` to `ignore`** — dunders stay undocumented repo-wide, and future dunders never trigger the rule.
  - **(c) No — `# noqa: D105` on the two lines** — rule stays active, the exception is local and visible.
- **Answer:** **(a) Yes — two one-line docstrings naming the context-manager contract** (user, 2026-10-07). `D105` stays selected; no ignore, no noqa.
- **Date:** 2026-10-07
- **Status:** ANSWERED
- **Incorporated:** yes — `src/backend/eventbus/eventbus.py:158,161` are in the backfill

## Q-14 — Are private helpers in scope even though `D` never requires them?
- **Step:** P.2 Interrogate
- **Why needed:** `D1xx` only fires on public objects, so a "docstring the public API" change leaves the hardest-to-read code (`_check`, `_validate`, `_dialogue`) untouched — and a reviewer will ask why.
- **Context:** The complex functions the merged `pyproject-tooling-gaps` change just refactored are private: `SettingDefinition::_validate` (26 → refactored), `PermissionService::_check`, `SqliteUserRepository::list_for_user` internals; `src/backend/settings/_setup.py` and `src/backend/logging/_decorator.py` are private modules whose module docstrings exist (`D100` = 0) but whose functions are outside `D103`. `src/` has 83 Python files; the `D` gate touches 43 of them.
- **Question:** Does this change also write docstrings for private helpers, or strictly the objects `D` covers?
- **Options:**
  - **(a) Strictly what `D` covers (Recommended)** — the gate and the diff stay aligned, and the change stays mechanically checkable ("`ruff check --select D src` is clean").
  - **(b) Also the private helpers in the files already being touched** — better docs where the complexity is, but the diff grows and no gate proves it.
  - **(c) Also the private helpers of the functions `pyproject-tooling-gaps` refactored** — targeted at the known-complex code, but it drags that change's files back in.
- **Answer:** **(b) Also the private helpers in the files already being touched** (user, 2026-10-07) — **not** the recommended strict scope. Consequences recorded: the diff grows beyond what `ruff check --select D src` can prove, so the Phase 5 done-criterion is "`D` clean **plus** every private helper in a touched file documented" (checked by review, not by the gate); the private-helper docstrings are still subject to the Q-15 no-filler rule.
- **Date:** 2026-10-07
- **Status:** ANSWERED
- **Incorporated:** yes — scope: private helpers inside the 43 `src/` files the change touches are in scope; the gate stays `ruff check --select D src` clean, the extra coverage is a review check

## Q-15 — How is the "no filler docstring" rule enforced?
- **Step:** P.2 Interrogate
- **Why needed:** The TODO's own risk note is that a big sweep "invites filler docstrings that restate the signature — worse than none, because mkdocstrings then publishes noise", but no gate in the repo detects filler; if nothing enforces it, the 198-docstring diff is exactly where it appears.
- **Context:** ruff has no filler detector (`D402` "first line is not the function's signature" is the closest and reports 0 today; `D419` "docstring is empty" also 0). The published surface is 195 objects (`userdocs/api.md` + `__all__`). Existing good examples already cite intent and requirements, e.g. `src/backend/filemanagement/search_source.py:100` "The declared display field values for ``record`` (REQ-021)."
- **Question:** What enforces "a docstring must add information the signature does not"?
- **Options:**
  - **(a) Reviewer rule stated in the scope record + the Phase 6 review checklist (Recommended)** — zero new tooling; the reviewer rejects "Get the user."-class docstrings by hand, per feature commit.
  - **(b) A small scripted check in `scripts/` that fails a docstring equal to/near the de-snaked callable name** — enforceable, but it is new tooling with its own false positives, and it needs its own tests.
  - **(c) Enable `D402` + `D419` and rely on ruff** — free, but measured 0 hits today, so it catches almost no filler in practice.
  - **(d) Nothing explicit — rely on the per-feature commit split (Q-5 a) keeping each chunk reviewable** — cheapest, weakest.
- **Answer:** **(a) Reviewer rule stated in the scope record + the Phase 6 review checklist** (user, 2026-10-07). No new tooling. The rule is recorded in `docs/verification/ruff-d-docstrings.md` at P.4 and becomes a Phase 6 review check: no docstring that restates the signature ("Get the user.") may pass review; per-feature commits are the unit of that check.
- **Date:** 2026-10-07
- **Status:** ANSWERED
- **Incorporated:** yes — scope record carries the no-filler rule; Phase 6 checklist gains the check; no `scripts/` checker, no `D402`/`D419` reliance

## Q-16 — Do REQ/AC IDs stay inside published docstrings?
- **Step:** P.2 Interrogate
- **Why needed:** The house style already embeds internal IDs in docstrings, and those strings are what the published API reference shows to a reader who has no access to `docs/specs/` — the same sentence is either traceability or noise depending on the answer.
- **Context:** Existing examples: `src/backend/filemanagement/search_source.py:100` "…(REQ-021)", `:161` "number / datetime operators: exact (REQ-012)", `src/backend/permissions/catalog.py:1`. `docs/specs/` is explicitly **not** part of the published site (`mkdocs.yml:2-5`: the site source is `userdocs/`, `docs/` is the internal record). `scripts/check_traceability.py` enforces matrix↔spec↔test referential integrity but does **not** read docstrings.
- **Question:** Do the new docstrings cite `REQ-XXX`/`AC-XXX` IDs?
- **Options:**
  - **(a) Yes, follow the existing style — IDs in docstrings (Recommended)** — consistent with the docstrings already in `src/`, and it keeps code↔spec links greppable.
  - **(b) No — reader-facing prose only, no internal IDs** — cleaner published pages, but it breaks the established convention and the grep-ability.
  - **(c) IDs only where the docstring explains a rule the spec defines, not as decoration** — middle ground, reviewer judgement.
- **Answer:** **(a) Yes — IDs stay in docstrings** (user, 2026-10-07), following the existing style (`filemanagement/search_source.py:100` "… (REQ-021)"). Recorded caveat: `docs/specs/` is not published (`mkdocs.yml` site source is `userdocs/`), so a reader of the API reference sees an ID with nothing to resolve it against — accepted, because code↔spec grep-ability is the higher value here.
- **Date:** 2026-10-07
- **Status:** ANSWERED
- **Incorporated:** yes — the scope record's docstring convention names REQ/AC citation as expected, not forbidden

## Q-17 — Is the traced-class docstring wording (REQ-009 / AC-009) a hard constraint on this change?
- **Step:** P.2 Interrogate
- **Why needed:** An approved spec requires every traced class's docstring to mention that it is traced via the shared logging feature, and this change edits docstrings — a rewording that drops the words "traced" or "logged" breaks an acceptance test in a change that is supposed to have no behavior delta.
- **Context:** `docs/specs/logging-coverage.md:120` REQ-009 and `:144` AC-009; the test is `tests/acceptance/logging_coverage/test_docstrings.py::test_traced_class_docstrings_mention_tracing`, which asserts `"traced" in doc and "logged" in doc` for every class in the logging inventory. Measured: 45 `@logged_class` classes in `src/`, **0** without a docstring — so the risk is not `D101`, it is a rewording (e.g. a `D401` imperative rewrite of a class docstring that starts "The class is traced via …").
- **Question:** Is "never remove the tracing mention from a traced class's docstring" recorded as an explicit invariant of this change's scope?
- **Options:**
  - **(a) Yes — record it as a MUST-hold invariant and re-run that acceptance test in Phase 5 (Recommended)** — one sentence in the scope record, and the test already exists.
  - **(b) No — rely on the full test suite to catch it** — the test does catch it, but only if the suite is run, and a light-tier Phase 5 might not run it.
  - **(c) Yes, and additionally exclude traced classes' docstrings from any reformatting step** — belt and braces, but it leaves 45 classes outside the formatting rules.
- **Answer:** **(a) Yes — a MUST-hold invariant, and Phase 5 re-runs `tests/acceptance/logging_coverage/test_docstrings.py::test_traced_class_docstrings_mention_tracing`** (user, 2026-10-07). Rewording is allowed; dropping "traced" or "logged" from any of the 45 `@logged_class` classes' docstrings is not.
- **Date:** 2026-10-07
- **Status:** ANSWERED
- **Incorporated:** yes — recorded as an invariant of the scope record; the named acceptance test is in the Phase 5 evidence set

## Q-18 — Does `mkdocs.yml` pin the docstring parser explicitly?
- **Step:** P.2 Interrogate
- **Why needed:** The site currently relies on griffe's default parser; if the chosen docstring style and that default ever disagree, the published pages silently lose their sections — and `mkdocs build --strict` does not fail on an unparsed section.
- **Context:** `mkdocs.yml:11-13` configures `plugins: [search, mkdocstrings(default_handler: python)]` with **no** handler options — no `docstring_style`, no `members`, no `filters`. The repo's style is plain prose (Q-2), so today the default is harmless.
- **Question:** Does this change add an explicit `handlers.python.options.docstring_style` to `mkdocs.yml`?
- **Options:**
  - **(a) No — leave `mkdocs.yml` untouched (Recommended)** — plain prose needs no parser, and touching the docs config is a second gate to re-verify for no gain.
  - **(b) Yes — pin `docstring_style: google` to match the ruff convention (Q-1 a)** — the two tools can no longer drift apart, at the cost of a config line that means nothing while no sections exist.
  - **(c) Yes — pin it to whatever Q-2 chooses** — self-consistent by construction, same cost as (b).
- **Answer:** **(b/c) Yes — pin `handlers.python.options.docstring_style: google` in `mkdocs.yml`** (user, 2026-10-07). The premise changed after Q-1/Q-2 chose Google sections: griffe's default is already `google`, so the line is a drift guard, not a behavior change. One config line in the same config commit as `select`.
- **Date:** 2026-10-07
- **Status:** ANSWERED
- **Incorporated:** yes — `mkdocs.yml` joins the config surface; `mkdocs build --strict` (Q-19) verifies it

## Q-19 — Is `mkdocs build --strict` a Phase 5 gate for this change?
- **Step:** P.2 Interrogate
- **Why needed:** The TODO flags that a malformed docstring can break the docs build, but the docs job is not part of the `quality_check` string the workflow runs — so unless it is named, nothing in Phase 5 proves the published site still builds after 198 new docstrings.
- **Context:** `pyproject.toml:224` `quality_check = "ruff check . && ruff format --check . && mypy src/ && deptry ."` — mkdocs is deliberately CI-only (comment at `pyproject.toml:69-71`). The docs build is gated by the `docs` job in `.github/workflows/quality.yml` and by the `mkdocs-build` **pre-push** hook (`.pre-commit-config.yaml`, `files: ^(mkdocs\.yml|userdocs/|pyproject\.toml)`) — note that hook does **not** fire on a `src/`-only change, so a docstring-only push is not covered locally. Building needs `uv run --group docs`.
- **Question:** Does Phase 5 of this change run `uv run --group docs mkdocs build --strict` and record the result?
- **Options:**
  - **(a) Yes — it is the only check that sees the docstrings as published output (Recommended)** — one extra command in Phase 5, and it is the change's real deliverable.
  - **(b) No — rely on the CI `docs` job on the PR** — no local step, but a failure then surfaces after the whole change is committed.
  - **(c) Yes, and also add `userdocs/`-adjacent paths to the `mkdocs-build` pre-push hook's `files:` filter** — closes the local gap permanently, but edits CI config beyond the change's scope.
- **Answer:** **(a) Yes — Phase 5 runs `uv run --group docs mkdocs build --strict` and records the result** (user, 2026-10-07). No change to the pre-push hook's `files:` filter.
- **Date:** 2026-10-07
- **Status:** ANSWERED
- **Incorporated:** yes — named in the Phase 5 evidence set for this change (see Q-25)

## Q-20 — Does `userdocs/api.md` gain the three packages it does not render?
- **Step:** P.2 Interrogate
- **Why needed:** 38 of the 195 published-surface `D1xx` sites are in `permissions` and `search` — features that have approved specs and `__all__` contracts but appear on no docs page. Documenting them is wasted effort for readers, or an argument that the page is stale; either way it must be decided, because the TODO puts `userdocs/` prose out of scope.
- **Context:** `userdocs/api.md:7-14` lists 8 packages; `src/backend/` holds 11 (`permissions`, `search`, `shared` missing). `permissions` has 32 `D1xx` sites, `search` 6, `shared` 0. Specs exist for both (`docs/specs/user-roles-permissions.md`, `docs/specs/search.md`). The TODO's "Out of scope" says "`userdocs/` prose beyond what mkdocstrings picks up automatically".
- **Question:** Does this change add `::: backend.permissions`, `::: backend.search` (and `::: backend.shared`?) to `userdocs/api.md`?
- **Options:**
  - **(a) No — leave `api.md` as-is; document the code, let a docs change extend the page (Recommended)** — keeps the DOCS/CHORE scope at docstrings + config, and the `D` gate covers all 11 packages regardless.
  - **(b) Yes — add `permissions` and `search` (not `shared`)** — the backfill pays off for readers immediately; two lines of `api.md`.
  - **(c) Yes — all 11 packages** — the page becomes complete, but `shared` is plumbing and its inclusion is its own judgement call.
- **Answer:** **(a) No — `userdocs/api.md` stays as-is** (user, 2026-10-07). The `D` gate still covers `permissions`, `search` and `shared` (Q-3's `src/` scope is all of `src/`), so 38 documented objects remain unrendered; extending the page is a separate docs change. Recorded as a known gap, not an oversight.
- **Date:** 2026-10-07
- **Status:** ANSWERED
- **Incorporated:** yes — `userdocs/api.md` is out of scope; the TODO's out-of-scope line stands

## Q-21 — How is `structlog-logging` sequenced against this change?
- **Step:** P.2 Interrogate
- **Why needed:** `structlog-logging` is in flight in its own worktree and its Phase 4 will rewrite `src/backend/logging/` and add new public API and many new test functions — the one in-flight change that touches both sides of this one.
- **Context:** `docs/todo/structlog-logging.md:7` `Status: WAITING` (branch `crosscut/structlog-logging` at `f2490a0`, Phase 3 tests written, `src/` untouched — `git diff --name-only main...crosscut/structlog-logging` = 24 files, all tests/docs/task JSON). Measured in that worktree: `src/` `D` unchanged at 386, `tests/` **795 vs main's 762 (+33)**. `src/backend/logging/` has only 3 `D` sites today (0 `D1xx`).
- **Question:** Does this change wait for `structlog-logging` to merge, run alongside it, or exclude the logging feature?
- **Options:**
  - **(a) Run alongside, and leave `src/backend/logging/` out of this backfill (Recommended)** — only 3 `D` sites and 0 `D1xx` there, so nothing is lost, and the two branches never touch the same file.
  - **(b) Wait for `structlog-logging` to merge, then start** — zero collision risk, but this change cannot start while the queue has other READY work.
  - **(c) Run alongside including `logging`** — 3 sites of avoidable conflict in a package the other change is rewriting.
- **Answer:** **Closed by implication (orchestrator, 2026-10-07)** — the premise is stale: `structlog-logging` **merged** on 2026-10-07 (PR #74, merge commit `c7a9119`), so `ruff-d-docstrings` branches from a `main` that already contains it. No sequencing decision is needed; the `src/` `D` measurements in this file were taken on that `main`. Option (a)'s concern (touching `src/backend/logging/` while it is being rewritten) no longer applies — `logging` is in scope like any other feature (3 `D` sites, 0 `D1xx`).
- **Date:** 2026-10-07
- **Status:** ANSWERED
- **Incorporated:** yes — no `Depends on:` entry for `structlog-logging`

## Q-22 — How is `structure-map` sequenced (AGENTS.md, `scripts/`, and the map's docstring summaries)?
- **Step:** P.2 Interrogate
- **Why needed:** `structure-map` is the next item to reach P.4 and it wants the same three surfaces this change touches or decides: `AGENTS.md`, `scripts/`, and docstring content (its generated `STRUCTURE.md` embeds each module's docstring summary, so this change rewrites part of that artifact's input).
- **Context:** `docs/todo/structure-map.md:126` (Q-11: it rewrites `AGENTS.md`'s Project Structure section and the stale `tests/architecture/` references), `:127` (Q-28a: `uv run mypy scripts/` joins the CI gate, pre-existing `scripts/` mypy errors in scope), `:148` (the map lists "module summary, classes with bases, annotated signatures"). This change may also edit `AGENTS.md:737` (Q-24) and decides whether `D` covers `scripts/` (Q-3) — where `structure-map` adds `scripts/make_map.py`.
- **Question:** Which of the two changes lands first?
- **Options:**
  - **(a) This change first, `structure-map` rebases (Recommended)** — the map is generated, so it picks up the new docstring summaries for free on its first regeneration; and `D` covering `scripts/` is decided before `make_map.py` is written.
  - **(b) `structure-map` first, this change rebases** — the map exists while the backfill runs (useful navigation for a 43-file sweep), but its committed `STRUCTURE.md` goes stale the moment docstrings are added.
  - **(c) Either order, with a note in both PR bodies to regenerate `STRUCTURE.md` after merge** — no sequencing constraint, but whoever is second must re-run the generator.
- **Answer:** **(a) `ruff-d-docstrings` first, `structure-map` rebases** (user, 2026-10-07). The generated map picks up the new docstring summaries free on its first regeneration, and the "does `D` cover `scripts/`" decision (Q-3: no) is settled before `scripts/make_map.py` is written. Recorded as a `Depends on:` note in `docs/todo/structure-map.md`.
- **Date:** 2026-10-07
- **Status:** ANSWERED
- **Incorporated:** yes — ordering recorded in both TODO files; `AGENTS.md` edits (Q-24 here, `structure-map` Q-11) are sequenced by this decision

## Q-23 — Are `migrations/` files permanently exempt from `D`?
- **Step:** P.2 Interrogate
- **Why needed:** Migration files are generated by `alembic revision`, so a `D` rule over `migrations/` writes a standing obligation on every future schema change — a decision with a permanent cost, distinct from the one-off backfill.
- **Context:** `migrations/` measures 11 `D` sites today: `D100` 1 (module docstring), `D103` 4, `D400` 2, `D415` 2, `D401` 2 across `migrations/env.py` and the two `versions/*.py`. AGENTS.md's alembic section makes `alembic revision -m "<description>"` the standard, and the `-m` text becomes the generated file's docstring — so the rule is partly satisfiable by habit. The `migrations` CI job runs `alembic upgrade head` against a temp DB (`quality.yml`).
- **Question:** What is the standing rule for `migrations/`?
- **Options:**
  - **(a) Exempt permanently via `per-file-ignores` (Recommended)** — generated files stay generated; the 11 sites are never touched.
  - **(b) Cover them: document the 11 sites now and hold future revisions to it** — uniform gate, and the `-m` habit covers most of it.
  - **(c) Cover `migrations/env.py` only, exempt `versions/*`** — the hand-written scaffold is documented, the autogen output is not.
- **Answer:** **(a) Exempt permanently via `per-file-ignores`** (user, 2026-10-07). `migrations/*` joins the Q-3 exemption list; the 11 sites are never touched, and no standing obligation lands on future `alembic revision` output.
- **Date:** 2026-10-07
- **Status:** ANSWERED
- **Incorporated:** yes — `per-file-ignores` = `tests/*`, `scripts/*`, `migrations/*`, `.github/*`

## Q-24 — Does `AGENTS.md` gain a normative docstring convention line?
- **Step:** P.2 Interrogate
- **Why needed:** The gate keeps the tree clean only if agents write compliant docstrings first time; the current guidance is one clause that does not name a style, a summary rule, or the filler prohibition — and this change is what makes the difference enforceable.
- **Context:** `AGENTS.md:737` ("General Code & Style Conventions" → "Documentation: Keep docstrings concise; explain *why* non-obvious logic exists rather than restating *what* the code does.") is the only docstring guidance in the file; the `python-best-practices` skill contains **no** docstring guidance at all (grep: 0 hits). `structure-map` also edits `AGENTS.md` (Q-22), and `update-readme` already added a non-phase-skills line to it.
- **Question:** Does this change update `AGENTS.md` to state the convention it is enforcing?
- **Options:**
  - **(a) Yes — extend the existing line with the chosen convention and the no-filler rule (Recommended)** — one or two lines where the guidance already lives, so future code lands clean and the gate costs nothing later.
  - **(b) No — the ruff rule is the guidance; `AGENTS.md` stays untouched** — no `AGENTS.md` conflict with `structure-map`, but agents learn the rule only by failing the lint job.
  - **(c) Yes, and also add a docstring section to the `python-best-practices` skill** — better placement for agents, but that skill's content is out of this change's scope (`track-python-skill` committed it as-is).
- **Answer:** **(a) Yes — extend `AGENTS.md:737`** (user, 2026-10-07) with the enforced convention: Google-style sections (`Args:` / `Returns:` / `Raises:`) where a callable has parameters or a return, one-line summary + blank line (D205), and the no-filler rule. The `python-best-practices` skill is not touched.
- **Date:** 2026-10-07
- **Status:** ANSWERED
- **Incorporated:** yes — `AGENTS.md` "General Code & Style Conventions" is in this change's file set; sequenced before `structure-map` (Q-22)

## Q-25 — How is "no behavior delta" proven for a ~200-docstring diff?
- **Step:** P.2 Interrogate
- **Why needed:** DOCS/CHORE requires a confirmed no-behavior-delta scope, and a diff that adds ~198 strings to 43 files is large enough that "the reviewer eyeballs it" is weak evidence — yet the standard evidence (the test suite) does not read docstrings.
- **Context:** The suite never asserts on docstrings except `test_traced_class_docstrings_mention_tracing` (Q-17); `ruff format --check .` is green today and stays green; `mypy src/` is unaffected. A docstring is a `Constant` expression node — an AST comparison that strips docstrings would prove the executable code is byte-identical.
- **Question:** What is the Phase 5 evidence that no behavior changed?
- **Options:**
  - **(a) Full suite + `ruff check .` + `ruff format --check .` + `mkdocs build --strict`, plus a one-off AST-equality check (docstrings stripped) recorded in the verification file (Recommended)** — cheap, mechanical, and it proves the claim rather than asserting it.
  - **(b) Full suite + lint/format/mkdocs only** — the repo's normal DOCS/CHORE evidence; the docstring-vs-code claim rests on review.
  - **(c) Targeted suite per feature + the full suite at the Phase 6 pre-merge gate** — faster during Phase 4, same final evidence.
- **Answer:** **(a) Full suite + `ruff check .` + `ruff format --check .` + `uv run --group docs mkdocs build --strict` + a one-off AST-equality check (docstrings stripped) recorded in `docs/verification/ruff-d-docstrings.md`** (user, 2026-10-07). The AST check proves the executable code is byte-identical before and after the sweep — the claim is demonstrated, not asserted.
- **Date:** 2026-10-07
- **Status:** ANSWERED
- **Incorporated:** yes — Phase 5 evidence set for this change; the AST check is a throwaway script run during Phase 5, not a permanent `scripts/` addition

## Q-26 — What happens when a docstring reveals that a behavior claim is wrong?
- **Step:** P.2 Interrogate
- **Why needed:** The TODO says "stop and reclassify as ISSUE", but with a per-feature increment that instruction is ambiguous: reclassifying the whole change strands the docstrings already written, and the repo has a lighter alternative (a separate ISSUE item).
- **Context:** The TODO's "Out of scope" and the classification comment both name the escalation (`docs/todo/ruff-d-docstrings.md`, Change type line). AGENTS.md's Escalation Rules cover `DOCS/CHORE → any` ("Stop; reclassify"), and the Light ISSUE tier exists for small localized fixes. Candidate sites are the docstrings that assert semantics no test asserts — e.g. `src/backend/filemanagement/search_source.py:147` "String operators (D4): case-insensitive via the normalized value" and `:161` "number / datetime operators: exact (REQ-012)", which describe spec behaviour (`docs/specs/search.md`) that a docstring could misstate.
- **Question:** When writing a docstring uncovers a wrong claim, what is the procedure?
- **Options:**
  - **(a) Record it as a finding, write the docstring that matches the code, and open a separate ISSUE TODO (Recommended)** — the docs change stays DOCS/CHORE and finishes; the defect gets its own RED/GREEN cycle.
  - **(b) Reclassify this change to ISSUE mid-flight per the Escalation Rules** — one change carries both, but the branch re-runs Phase P for ISSUE and the docstring work waits.
  - **(c) Stop the change entirely and wait for the human to decide** — safest, but it strands every feature already done.
- **Answer:** **(a) Record it as a finding, write the docstring that matches the code, and open a separate ISSUE TODO** (user, 2026-10-07). This change stays DOCS/CHORE and finishes; the defect gets its own triage + RED/GREEN cycle. The TODO's "stop and reclassify as ISSUE" line is amended to this procedure in the P.4 scope record.
- **Date:** 2026-10-07
- **Status:** ANSWERED
- **Incorporated:** yes — escalation procedure recorded in the scope record; no mid-flight reclassification

## Q-27 — Version bump: none, or patch?
- **Step:** P.2 Interrogate
- **Why needed:** AGENTS.md maps DOCS/CHORE to no bump, but this change alters the **published** API reference — the one case where "does not alter externally observable behavior" is arguable, and the version is the only signal a docs reader has.
- **Context:** AGENTS.md Versioning: "REFACTOR / DOCS-CHORE → none"; `pyproject.toml:4` `version = "0.6.1"`, `[tool.bumpversion] current_version = "0.6.1"`, `tag = false`. Precedent: `update-readme` and `workflow-docs-nits` (both DOCS/CHORE, both rewrote published text) shipped with no bump.
- **Question:** Does this change bump the version?
- **Options:**
  - **(a) None — follow the DOCS/CHORE rule (Recommended)** — consistent with `update-readme`/`workflow-docs-nits`; the published site is rebuilt from `main` regardless of the version string.
  - **(b) `patch` — treat the published docs change as a release-visible fix** — signals the docs change, but it deviates from the version table and needs the reason recorded.
- **Answer:** **PENDING**
- **Date:** 2026-10-05
- **Status:** PENDING
- **Incorporated:** no

## Q-28 — Does this change align the pre-commit ruff pin with the dev pin?
- **Step:** P.2 Interrogate
- **Why needed:** The pre-commit hook and CI would run two different ruff versions over the new `D` rules, so a locally "clean" commit can fail CI (or the hook can rewrite docstrings differently than CI judges them) — and `D` rule sets are exactly the kind of thing that moves between ruff releases.
- **Context:** `.pre-commit-config.yaml:11` `rev: v0.15.12` with `args: [--fix]` (`.pre-commit-config.yaml:14`); `pyproject.toml:62` `ruff>=0.16.9`; `uv run ruff --version` → 0.16.9. The file's own comment says "Review hook revisions during the first maintenance week of each month and any time the Python or CI toolchain changes materially" — enabling a new rule family is arguably that moment. `pyproject-tooling-gaps` removed the complexipy hook for a comparable version-skew reason (its Q-2/Q-3).
- **Question:** Does this change bump the `ruff-pre-commit` rev to match the dev pin?
- **Options:**
  - **(a) Yes — bump the hook rev to the ruff version the dev group pins (Recommended)** — one line, and it removes a known source of local-vs-CI disagreement before the new rules start biting.
  - **(b) No — leave the pin alone; it is a separate chore** — keeps this change's diff to docstrings + `select`, but the skew stays live.
  - **(c) Yes, and pin both sides to an exact version (`ruff==0.16.9`)** — removes drift permanently, but changes the project's `>=` pinning convention for ruff.
- **Answer:** **PENDING**
- **Date:** 2026-10-05
- **Status:** PENDING
- **Incorporated:** no

## Q-29 — Q-3 (gate `src/` only) contradicts Q-4 (backfill **and** gate `tests/`)
- **Step:** P.3 Answer — orchestrator-raised conflict, round 2 (2026-10-07)
- **Why needed:** Round 1 answered Q-3 = "`src/` only, add `per-file-ignores` for `tests/*`" and Q-4 = "backfill all 313 test docstrings **and gate `tests/`**". Both cannot hold: a tree listed in `per-file-ignores` is by definition not gated. The contradiction has to be resolved before P.4 can state a file set and a site count.
- **Context:** Measured `tests/` `D` sites = **762** (468 `D1xx` — D103 358, D102 49, D104 42, D107 19 — plus 294 format/phrasing), not 313: the 313 figure is the AST count of undocumented `test_*` functions, while ruff also counts helpers, classes and modules. With Q-2 = Google style the section-block cost applies to `tests/` too. `scripts/verify_spec.py:63` (the orphaned-acceptance-test check) is skipped, so nothing parses test docstrings today.
- **Question:** Which resolution: `src/` gated now and `tests/` as a follow-up change, `tests/` gated for missing-docstring codes only, both trees fully gated in one change, or `tests/` backfilled without gating?
- **Answer:** **`src/` now, `tests/` as a follow-up change** (user, 2026-10-07). This change gates `src/` only (328 sites, `per-file-ignores` for `tests/*`, `scripts/*`, `migrations/*`, `.github/*`); the `tests/` backfill **and** its gate move to a new sibling change **`docstrings-tests`**, framed at P.1 with `Depends on: ruff-d-docstrings`. Q-4's intent (test docstrings mandatory and enforced) survives; it is delivered by the follow-up, not dropped.
- **Date:** 2026-10-07
- **Status:** ANSWERED
- **Incorporated:** yes — `ruff-d-docstrings` scope = `src/` only; `docstrings-tests` created at P.1 (`docs/todo/docstrings-tests.md`) carrying the `tests/` backfill + gate; Q-3/Q-4 answers annotated accordingly

## Late questions (Phases 2–6)

<questions discovered after the change entered the workflow; same entry format, Step field set to the step that found it>
