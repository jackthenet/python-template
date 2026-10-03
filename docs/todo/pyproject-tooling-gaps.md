# TODO: pyproject-tooling-gaps

Backlog item for one planned change, created at **P.1 Frame** from this template and named `pyproject-tooling-gaps.md`. One file per change.

This is a **planning record, not normative**: like `docs/questions/`, it is committed directly to `main` (see "Phase P: PREPARE" in `AGENTS.md`). It carries no approval gate — the spec does.

- **Status:** PREPARING  <!-- PREPARING | QUESTIONS-ANSWERED | READY | IN-WORKFLOW | WAITING | MERGED -->
- **Change type:** DOCS/CHORE  <!-- configuration, CI wiring and explanatory comments; no externally observable behavior delta. Escalate if any item turns out to change behavior (see Constraints). -->
- **Created:** 2026-10-03
- **Question file:** `docs/questions/pyproject-tooling-gaps.md`
- **Spec:** n/a  <!-- DOCS/CHORE: no spec -->
- **Worktree:** <created at P.4> `../python-template_kopie-worktrees/chore/pyproject-tooling-gaps`
- **Depends on:** none
- **Related specs:** none (no `docs/specs/` file is touched; `docs/specs/*` NFRs about coverage are read-only context)

## Goal (one line)
Make every tool **configured** in `pyproject.toml` also **enforced** where it is claimed to be, and turn the two silent policy choices (complexipy threshold 30, permissive mypy) into documented ones.

## Why
An external review of `pyproject.toml` reported eight findings. Verified against the repo, **two of the three "most important" claims are already handled**, and the review missed the one gate that is actually broken. The change is therefore smaller than it looks, but not empty.

| Review claim | Verified reality | Evidence |
|---|---|---|
| "Coverage config exists, but nothing invokes it — the 92 % floor is decorative." | **False.** CI runs coverage as a gate: `uv run pytest tests/ --cov --cov-report=xml`, with the comment *"pytest-cov honors `[tool.coverage.report] fail_under` (92) from pyproject.toml."* | `.github/workflows/quality.yml:57-59` (`coverage` job) |
| "`deptry` has a thorough config but nothing runs it." | **False, twice over.** A CI gate job runs `uv run deptry .`, and a pre-commit local hook runs it whenever `pyproject.toml`, `uv.lock`, `src/`, `tests/`, `scripts/` or `migrations/` change. | `.github/workflows/quality.yml:93-94` (`dependencies` job); `.pre-commit-config.yaml` local hook `deptry` |
| "`agent-runner.quality_check` is `ruff check src/ && mypy src/` only." | **True** — this is the one accurate wiring gap: deptry/complexipy/coverage are not in the agent-runner quality check even though they are CI gates. | `pyproject.toml` `[tool.agent-runner] quality_check` |
| complexipy threshold 30 is "double the tool's default" and may be undocumented drift | **Understated — this is the real finding.** (a) complexipy runs **nowhere in CI** (only the pre-commit hook); (b) the hook pins `rev: v5.1.0` while the dev group pins `complexipy>=8.0.1` — the pre-rewrite Python engine vs. the Rust rewrite, i.e. two different scoring engines; (c) measured today, the tree **already violates 30**: `src/backend/settings/models.py::is_valid_value` = **47**, `tests/property/usermanagement/test_usermanagement_properties.py::test_inv_003_last_admin_invariant` = **38**. So the gate is being bypassed (`--no-verify`) or the older hook scores differently — either way the threshold comment is the least of the problems. | `uv run complexipy --top 5`; `.pre-commit-config.yaml` complexipy hook; `pyproject.toml` dev group |
| mkdocs stack in `dev` bloats every `uv sync` | **True but under-specified.** Splitting the group touches more than `pyproject.toml`: **8 CI jobs** each run `uv sync --only-group dev`, the `mkdocs-build` pre-push hook, and the README quickstart (`README.md:8`). | `.github/workflows/{lint,quality}.yml`, `.pre-commit-config.yaml`, `README.md:8` |
| `webauthn` enablement is tribal knowledge | **True.** The only pointer is the `DEP001` comment; there is no `[project.optional-dependencies]` entry anywhere. | `pyproject.toml` `[tool.deptry.per_rule_ignores] DEP001` |
| alembic in `dev` only may be missing at deploy | **Not decidable in this repo** — there is no deployment artifact at all (`find -maxdepth 2 -iname "*docker*"` → nothing; no Dockerfile, no compose, no release workflow that installs). It is a template-guidance question, not a code question. | repo root listing |
| mypy config is permissive; state the intent | **True, cost unmeasured.** Only `check_untyped_defs` is on. Whether `disallow_untyped_defs` / `warn_return_any` / `strict` are affordable has not been measured. | `pyproject.toml` `[tool.mypy]` |
| No `D` (pydocstyle) rules; consider `DTZ` | **True, and the costs are very different.** Measured: 83 source files, **0** missing module docstrings, but **156 of 515** public defs/classes lack a docstring → `D1xx` is a ~156-violation backfill. `DTZ` is nearly free: `src/` already uses `datetime.now(UTC)` throughout (authentication, filemanagement, permissions) and no naive `datetime.now()`/`utcnow()` was found. | AST scan of `src/`; `grep -rn "datetime.now(UTC)" src/` |
| "Nothing unnecessary to cut." | **Confirmed** — no dependency in the file is unused beyond the two documented declared-capability exceptions (`httpx`, `orjson`, DEP002-ignored). | `pyproject.toml` DEP002 comment |

## In scope
- **complexipy: decide and fix the gate, not just the comment.** Choose one: (a) add a complexipy job to CI at a threshold the tree actually passes, (b) keep it pre-commit-only and say so in a comment, or (c) lower the threshold and fix the two offenders (`is_valid_value` at 47 is the largest function in the repo). Either way: reconcile the pre-commit `rev: v5.1.0` pin with the `complexipy>=8.0.1` dev pin so hook and CLI score the same code, and record *why* the threshold is what it is.
- **`agent-runner.quality_check`**: add the tools that are already CI gates but absent from the agent's own quality loop (`deptry` at minimum; the coverage/complexipy decision follows from the complexipy item).
- **Explanatory comments** for the two deliberate-but-silent choices: the complexipy threshold, and the mypy permissiveness ("permissive template default, tighten per-project") — the latter only after measuring what strictness actually costs here.
- **`[project.optional-dependencies] webauthn = ["webauthn"]`** so the deferred-import capability is discoverable and installable, with the `DEP001` comment pointing at it.
- **Ruff `DTZ`** selection (near-zero cost, protects token/session/lockout expiry code).
- **Docs-group split** — *only if decided*: move `mkdocs`, `mkdocs-material`, `mkdocstrings[python]` to a non-default `docs` group and update all 8 `uv sync --only-group dev` CI lines, the `mkdocs-build` pre-push hook, and `README.md:8`.

## Out of scope
- Raising `fail_under` above 92, or changing what coverage measures.
- Adding `--cov` to `[tool.pytest.ini_options] addopts` — **explicitly not recommended**: CI already passes `--cov` explicitly, and putting it in `addopts` slows every targeted per-task `red_command`/`green_command` run (Phase 4 runs targeted tests, not the suite) and every `pytest -x` loop. The floor is not decorative; it is CI-enforced.
- Ruff `D1xx` backfill of the 156 undocumented public defs — decide at P.3 whether to (a) select `D` and backfill, (b) select `D` with a per-file ignore list, or (c) leave it and rely on `mkdocstrings` rendering whatever is there. The backfill itself is a separate change either way.
- Any dependency addition (see `docs/todo/tenacity-rich-cachetools.md`).
- Any source refactor forced by a lowered complexity threshold — that is a REFACTOR change, not this one.

## Affected features
No `src/` feature code. Files: `pyproject.toml`, `.pre-commit-config.yaml`, `.github/workflows/lint.yml`, `.github/workflows/quality.yml`, `README.md`.

## Constraints and risks
- **CI parity is the contract.** `AGENTS.md` states the Phase 5 whole-repo lint sweep must match `.github/workflows/lint.yml` exactly. Any gate added here changes what "verified" means for every in-flight change — a new failing gate mid-workflow re-opens finished changes. Sequence: land it when few changes are in flight, or land it with the tree already passing.
- **A new gate must pass on day one.** complexipy at 30 fails today (47, 38). Adding it to CI as-is turns the template red; the threshold, the offenders, or the scope (`src/` only, not `tests/`) must be decided first.
- **Two complexipy engines.** The pre-commit hook (`v5.1.0`) and the dev pin (`8.x`) are different implementations; a threshold tuned for one is not meaningful for the other. Do not tune the number before reconciling the versions.
- **The docs-group split is a wide, boring diff.** 8 CI lines + 1 hook + 1 README line; a missed one breaks the `docs` job, not a feature. If done, verify with `uv sync --group docs` and `uv run mkdocs build --strict` in a clean worktree.
- **mypy strictness can cascade.** `disallow_untyped_defs` over 83 files may produce a large diff; if it does, it belongs in its own REFACTOR change, not in a comment-only chore.
- **Escalation trigger:** if any item changes externally observable behavior (e.g. a coverage floor that fails an existing build, or a refactor forced by the complexity gate), reclassify per the Escalation Rules.

## Value triage (2026-10-03, pre-workflow)
- **Overlap:** two of the three headline items are already implemented (coverage gate, deptry gate ×2) — re-doing them would be pure waste. The overlap check is what saved this TODO from being a 30-minute mistake.
- **Beneficiary:** the next contributor and the next agent run — both currently read `pyproject.toml` as the source of truth about what is enforced, and today it under-states (no complexipy in CI) and over-states (no comment on the two policy choices) at the same time.
- **Score: 3/5** — the surviving items are small, cheap and genuinely corrective (complexipy gate/version, `quality_check`, two comments, optional-dependencies, `DTZ`), but none adds capability; the docs-group split is the only debatable one and its payoff is a slightly leaner `uv sync` against an 8-line CI diff.
- **Recommendation: implement the five cheap items as one DOCS/CHORE; decide the docs-group split at P.3 (default: skip it — the MkDocs stack is ~3 packages and the CI diff is wider than the benefit); drop the coverage-`addopts` suggestion outright.** Do not add a complexipy CI gate until the version mismatch and the two over-threshold functions are resolved.

## Acceptance signal (plain language)
Every tool with a config block in `pyproject.toml` is either run by a named CI job or pre-commit hook, or carries a comment saying it is deliberately manual; `[tool.agent-runner] quality_check` covers the same tools CI gates; the complexipy pre-commit pin and the dev-group pin are the same major version and the configured threshold passes the tree as it stands; `pip install .[webauthn]` (or `uv sync --extra webauthn`) installs py-webauthn without reading a code comment; `ruff check .` is clean with `DTZ` selected; and the two policy choices (threshold, mypy strictness) are explained in one line each in the file itself.

## Prep log
| Step | Date | Result |
|---|---|---|
| P.1 Frame | 2026-10-03 | TODO + question file created on `main`; type DOCS/CHORE; **review claims verified**: coverage gate (`quality.yml:59`) and deptry gate (`quality.yml:94` + pre-commit hook) already exist — both headline findings are false; new finding: complexipy is in no CI job, its pre-commit pin (v5.1.0) and dev pin (8.x) differ, and the tree already exceeds the configured 30 (47, 38); measured costs recorded (156/515 public defs lack docstrings; `DTZ` near-free); **value triage 3/5** |
| P.2 Interrogate (<n> questions) | | |
| P.3 Answer (<n> answered) | | |
| P.4 Draft scope + create branch/worktree | | |
| P.5 Self-consistency | n/a (DOCS/CHORE) | |
