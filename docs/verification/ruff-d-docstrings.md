# ruff-d-docstrings — Scope Record (DOCS/CHORE)

- **Change:** ruff-d-docstrings · **Type:** DOCS/CHORE (Phase 0 classified at P.1; re-stated here, not re-classified)
- **Branch / worktree:** `chore/ruff-d-docstrings` @ `45aa61c` (== `main` at P.4, 2026-10-08), worktree `../python-template_kopie-worktrees/chore/ruff-d-docstrings`
- **Version:** `1.0.0` (`pyproject.toml:4`) — **no bump** (Q-27; AGENTS.md Versioning: REFACTOR / DOCS-CHORE → none)
- **Phase Matrix for this type:** Phase 1 scope (this file, at P.4) · Phase 2/3 skipped · Phase 4 make the scoped non-behavior changes · Phase 5 light gate (lint/types where applicable + the Q-25 evidence set) · Phase 6 light review + PR. No spec, no spec PR.
- **Question file:** `docs/questions/ruff-d-docstrings.md` — Q-1 … Q-29, all `ANSWERED`; the binding decisions are summarized in `docs/todo/ruff-d-docstrings.md` §"P.3 decisions".
- **Date:** 2026-10-08

## Phase 0 — classification: DOCS/CHORE

First matching criterion (#5 in the Change Types table): the change **does not alter behavior** — it adds docstrings (documentation), edits `pyproject.toml` / `mkdocs.yml` / `.pre-commit-config.yaml` (configuration / tooling), and extends one `AGENTS.md` guidance line. No control flow, no public signature, no runtime path changes; §"No-behavior-delta proof plan" proves it rather than asserting it (Q-25).

Not **REFACTOR**: no existing code is restructured — the AST digest below shows the executable syntax tree is byte-identical before and after. Not **FEATURE/ISSUE**: nothing new is observable and nothing deviates from an approved spec.

**Escalation amendment (Q-26, supersedes the TODO's "stop and reclassify as ISSUE" line).** If writing a docstring reveals that a **behavior claim is wrong** (a docstring or comment asserting semantics the code does not implement), the procedure is: (1) record it as a **finding** in this file, (2) write the docstring that matches **the code as it is**, (3) open a **separate ISSUE TODO** (`docs/todo/<name>.md`, its own triage + RED/GREEN cycle). This change **stays DOCS/CHORE and finishes**; no mid-flight reclassification, no stranded per-feature commits.

## Fresh measurement (2026-10-08, this worktree, `ruff 0.16.10`, base commit `45aa61c`)

The TODO carries stale figures (see §Findings). Re-measured with `uv run ruff check --select D --statistics <tree>`, both bare and with the chosen convention:

| Tree | `--select D` (bare) | `--select D` + `convention = "google"` | Gated by this change |
|---|---|---|---|
| `src/` | 398 | **328** | **yes** |
| `tests/` | 827 | 743 | no — `per-file-ignores` (Q-3/Q-29 → sibling `docstrings-tests`) |
| `migrations/` | 11 | 7 | no — `per-file-ignores` (Q-23) |
| `scripts/` | 3 | 3 | no — `per-file-ignores` (Q-3) |
| `.github/` | 2 | 2 | no — `per-file-ignores` (Q-3) |
| repo-wide | 1 164 | 1 083 | — |

`src/` under the google convention (the set this change gates), by code:

```text
131  D102  undocumented-public-method        66  D205  missing-blank-line-after-summary
 57  D209  new-line-after-last-paragraph      51  D107  undocumented-public-init
 14  D101  undocumented-public-class           4  D403  first-word-uncapitalized
  3  D301  escape-sequence-in-docstring        2  D105  undocumented-magic-method
                                            ---  total 328   (D1xx missing-docstring family: 198)
```

Measured side effects of `convention = "google"` (ruff 0.16.10): `D401` (70 bare hits) is **not selected** — descriptive noun-phrase first lines stay (Q-10); `D400`/`D415`/`D203`/`D211`/`D212`/`D213` are not selected either, and the two "incompatible rule pair" warnings that bare `--select D` prints on stderr **disappear** with the convention set, so CI output stays clean.

`src/` files affected: **41** (nothing under `src/frontend/` and `src/main.py` — measured 0 `D` sites there):

| Feature (`src/backend/<f>/`) | Files | `D` total | `D1xx` (missing docstrings) |
|---|---|---|---|
| usermanagement | 7 | 70 | 47 |
| search | 4 | 61 | 6 |
| filemanagement | 6 | 58 | 37 |
| authentication | 7 | 51 | 50 |
| permissions | 6 | 45 | 33 |
| sessionmanagement | 3 | 16 | 2 |
| settings | 2 | 16 | 14 |
| mail | 4 | 6 | 6 |
| eventbus | 1 | 3 | 3 |
| logging | 1 | 2 | 0 |
| shared / frontend / `main.py` | 0 | 0 | 0 |
| **Total** | **41** | **328** | **198** |

Published surface (`userdocs/api.md` renders 8 packages): `permissions` (33 `D1xx`) and `search` (6) are documented but **not rendered** — `api.md` keeps its 8 packages (Q-20); that is a known gap, not an oversight.

## Exact change scope (file-level; nothing else is touched)

### 1. `pyproject.toml` (config commit, lands **last** — Q-7 a)

```toml
[tool.ruff.lint]
select = [
    # ... existing I, E, W, B, F, UP, RUF, PL, Q, SIM, C4, DTZ ...
    "D",  # pydocstyle — docstrings (google convention; src/ only, see per-file-ignores)
]

fixable = [
    # ... existing I, UP035, RUF022, Q000-Q004 ...
    "D204", "D207", "D208", "D209", "D211", "D212", "D403",  # docstring layout, always-fixable (Q-12)
]

[tool.ruff.lint.pydocstyle]
convention = "google"          # Q-1 / Q-2

[tool.ruff.lint.per-file-ignores]
"tests/*" = ["D"]              # Q-3 / Q-29 → sibling change docstrings-tests
"scripts/*" = ["D"]            # Q-3
"migrations/*" = ["D"]         # Q-23
".github/*" = ["D"]            # Q-3
```

Measured facts behind each entry:

- **`per-file-ignores` glob form.** Q-3's literal `tests/*` / `.github/*` work **as written**: `uv run ruff check --select D --per-file-ignores='.github/*:D' .github` → *All checks passed* (the 2 sites are in the nested `.github/hooks/`), and `--per-file-ignores='tests/*:D' tests` silences all 827 sites in nested test directories — ruff's per-file-ignores globs match across `/`. No `**` rewrite needed.
- **`fixable` widening (Q-12) — what it actually buys.** Measured with `--diff --fixable=D` on `src/`: `D209` (57 sites) and `D403` (4) have **safe** fixes (203 / 16 diff lines); `D301` (3) is fixable **only** with `--unsafe-fixes` (10 lines); `D205` (66) has **no fix available at all** — those 66 blank-line-after-summary sites are manual. So of the 130 format sites, 61 are mechanical, 3 need an explicit unsafe-fix run on the changed paths, 66 are hand edits. Of Q-12's seven named always-fixable codes, only `D209` and `D403` fire under the google convention today; the other five (`D204`, `D207`, `D208`, `D211`, `D212`) are listed for symmetry and report 0. `--fix` stays scoped to the step's changed paths, never repo-wide (AGENTS.md P-6).
- **No new dependency, no dependency version change.** `ruff>=0.16.10` (`pyproject.toml:62`) is untouched; only the pre-commit hook rev moves (item 3).

### 2. `mkdocs.yml` (same config commit — Q-18)

```yaml
plugins:
  - search
  - mkdocstrings:
      default_handler: python
      handlers:
        python:
          options:
            docstring_style: google
```

Measured: `mkdocstrings-python 2.0.8` (`uv.lock`) defines `PythonInputOptions.docstring_style: Literal["auto","google","numpy","sphinx"] | None = "google"` — the handler **already defaults to google**, so this is an explicit pin, not a rendering change: zero docs-output delta from this line. The delta comes from the docstrings themselves (blanks → text).

### 3. `.pre-commit-config.yaml` (same config commit — Q-28)

`rev: v0.15.12` → **`rev: v0.16.10`** on the `astral-sh/ruff-pre-commit` hook (one line, `.pre-commit-config.yaml:11`). Q-28's answer is "bump the hook rev **to match the dev pin**"; the number it quoted (`v0.16.9`) is stale — `pyproject.toml:62` is `ruff>=0.16.10` and `uv run ruff --version` → `0.16.10` (finding F-6). The hook runs `ruff-check --fix`, so with the widened `fixable` list the hook and CI must agree on the rule set and version. `pyproject.toml`'s `>=` pinning convention is unchanged (Q-28 c rejected).

### 4. `AGENTS.md` (config/guidance commit — Q-24)

Extend the single "Documentation" bullet in §"General Code & Style Conventions" (currently `AGENTS.md:743`) with the enforced convention and the no-filler rule, e.g.: docstrings are **Google style** and gated by ruff `D` over `src/` (`tests/`, `scripts/`, `migrations/`, `.github/` exempt via `per-file-ignores`); every public object in a backend package carries a docstring that states something its signature does not — filler that restates the signature ("Get the user.") is rejected in review. Prose only; no behavior, no CI change. The `python-best-practices` skill is **not** touched (Q-24).

### 5. `src/**/*.py` — docstrings and formatting (per-feature commits, item order below)

328 `D` sites in 41 files: **198 docstring additions** (`D102` 131, `D107` 51, `D101` 14, `D105` 2) and **130 format sites** (`D205` 66, `D209` 57, `D403` 4, `D301` 3) fixed in **separate commits** from the additions (Q-11). Content rules: all 51 `D107` `__init__` sites included, no `errors.py` exemption (Q-9); the two `D105` `EventBus.__enter__`/`__exit__` documented (Q-13); private helpers **in the touched files** documented too (Q-14 — review-checked, not gate-checked); `REQ-XXX`/`AC-XXX` IDs stay cited inside docstrings (Q-16); no docstring may restate the signature (Q-15).

### 6. Explicitly **not** touched

`userdocs/` (incl. `api.md` and its 8 packages — Q-20) · `tests/`, `scripts/`, `migrations/`, `.github/hooks/` docstrings and their gate (Q-29 → sibling `docstrings-tests`) · any test file, assertion or fixture · any spec, ADR or task DAG · type annotations (mypy strictness is `pyproject-tooling-gaps` follow-up work) · the `mkdocs-build` pre-push hook's `files:` filter (Q-19) · `pyproject.toml` version (Q-27) · the `python-best-practices` skill (Q-24).
## Commit plan (Q-5 a one change · Q-7 a docstrings first, config last · Q-11 format separate)

`ruff check .` is green on `main` today and stays green at **every** commit on the branch, because `select += "D"` is the last commit — before it, the new docstrings are simply un-gated additions.

| Order (easiest first) | Commits per feature | Sites |
|---|---|---|
| 1 | `eventbus` docstrings → `eventbus` format | 3 |
| 2 | `logging` format only (0 missing docstrings) | 2 |
| 3 | `mail` docstrings → format | 6 |
| 4 | `sessionmanagement` docstrings → format | 16 |
| 5 | `settings` docstrings → format | 16 |
| 6 | `permissions` docstrings → format | 45 |
| 7 | `authentication` docstrings → format | 51 |
| 8 | `filemanagement` docstrings → format | 58 |
| 9 | `search` docstrings → format | 61 |
| 10 | `usermanagement` docstrings → format | 70 |
| 11 | **config**: `pyproject.toml` + `mkdocs.yml` + `.pre-commit-config.yaml` + `AGENTS.md` | gate flips |

A feature with 0 format sites (or 0 `D1xx` sites) skips that half of the pair — the split is per feature, not a fixed 2×10.

## No-behavior-delta proof plan (Phase 5 — proven, not asserted; Q-25)

Baseline measured **now** at `45aa61c` in this worktree: `uv run ruff check .` → *All checks passed!*; `uv run ruff format --check .` → **339 files already formatted**; docstring-stripped AST digest of `src/` → **`64fc1d6ee758bf6ac572d58b100eff95d4bbd1205c993f7d9e2e126657d7bec0`** (identical in the primary worktree, so the digest is worktree-independent when run with the relative `src` root). The pytest and `mypy src/` baselines are recorded at **S4.1** before the first edit.

| Evidence | Command | Expected |
|---|---|---|
| Suite unchanged | `uv run pytest tests/ -q` (S4.1 baseline vs S5.1) | **identical counts**; no test added, changed, weakened or skipped |
| AC-009 invariant intact | `uv run pytest tests/acceptance/logging_coverage/test_docstrings.py::test_traced_class_docstrings_mention_tracing -v` | PASS (the only test in the suite that reads docstrings) |
| Lint green **with the new gate** | `uv run ruff check .` | clean — i.e. `D` selected over `src/` and 0 findings (== CI, `.github/workflows/lint.yml`) |
| Format gate green | `uv run ruff format --check .` | 0 files would be reformatted (baseline 339 already formatted) |
| Types unchanged | `uv run mypy src/` | same result as the S4.1 baseline |
| Published site still builds | `uv run --group docs mkdocs build --strict` | passes (the `mkdocs-build` pre-push hook does **not** fire on a `src/`-only change — Q-19) |
| **Executable code identical** | one-off AST digest check below, run at `45aa61c` and at the final commit | **identical digest** `64fc1d6e…` |
| Worktree clean | `git status --porcelain` | empty (S7.1 removes the worktree without `--force`) |

The AST check (throwaway script, **not** added to `scripts/` — Q-25). It removes every docstring statement and the `docstring` attribute, then hashes the dump:

```python
"""One-off no-behavior-delta check (Q-25): hash each src file's AST with every
docstring removed, so a docstring-only diff hashes identically."""
import ast, hashlib, sys
from pathlib import Path

DOC_HOSTS = (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)

def is_doc(node: ast.AST) -> bool:
    return isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str)

def strip(node: ast.AST) -> None:
    if isinstance(node, DOC_HOSTS):
        node.docstring = None
        body = getattr(node, "body", [])
        if body and is_doc(body[0]):
            body.pop(0)
            if not body:
                body.append(ast.Pass())
    for child in ast.iter_child_nodes(node):
        strip(child)

def digest(root: Path) -> str:
    h = hashlib.sha256()
    for p in sorted(root.rglob("*.py")):
        tree = ast.parse(p.read_text(encoding="utf-8"), filename=str(p))
        strip(tree)
        h.update(p.as_posix().encode())
        h.update(ast.dump(tree).encode())
    return h.hexdigest()

if __name__ == "__main__":
    print(digest(Path(sys.argv[1] if len(sys.argv) > 1 else "src")))
```

Control run (2026-10-08, this worktree — the check is sensitive to code and blind to docstrings):

```text
before (copy of src)          : 461499a8902c944e…
+ docstring on EventBus.__enter__ : 461499a8902c944e…   SAME   (digest ignores the docstring)
+ max_queue_size 1000 → 1001      : fc5635607e934ee3…   DIFFERENT (digest catches a code change)
```

Run it with the **relative** `src` root in each worktree (the digest includes the file paths, so an absolute root would make the two sides incomparable).

## Invariants that MUST hold

- **INV-A (traced wording, logging-coverage REQ-009 / AC-009).** No `@logged_class` class docstring may lose the "traced" + "logged" wording. Measured: **41** classes in `src/` carry `@logged_class` (all 41 already have a docstring); the AC-009 test asserts the wording for the **19** classes in `INVENTORY_CLASSES` (`tests/logging_coverage_test_helpers.py:53`). Phase 5 re-runs `test_traced_class_docstrings_mention_tracing`. (The TODO's "45" is stale — finding F-3.)
- **INV-B (no test touched).** No test file is added, removed, weakened or converted; the diff touches no file under `tests/`.
- **INV-C (no escape hatches).** No `# noqa` anywhere, and `per-file-ignores` gains **exactly** the four trees decided in Q-3/Q-23/Q-29 — never a per-file exemption for a real gap in `src/`.
- **INV-D (executable code identical).** Proven by the AST digest, not by review.
- **INV-E (no version bump)** — `pyproject.toml:4` and `[tool.bumpversion] current_version` stay at `1.0.0` (Q-27).
- **INV-F (no new dependency, no dependency-range change)** — only the pre-commit hook rev moves.
- **INV-G (no-filler rule, Q-15).** No docstring that restates the signature ("Get the user.") may pass review; the unit of that check is the per-feature commit. No scripted checker is added (Q-15 b rejected) — this is a **Phase 6 review checklist item**.
- **INV-H (private helpers in touched files documented, Q-14).** Beyond what `ruff check --select D src` can prove; verified by review in Phase 6, not by the gate.
- **INV-I (spec IDs stay cited, Q-16).** `REQ-XXX`/`AC-XXX` references inside docstrings are kept.
- **INV-J (feature boundaries / architecture rules unchanged).** No file moves, no new import, no cross-feature internal import — the diff is docstrings inside existing files plus config.

## Phase 5 gate list (DOCS/CHORE light gate) and acceptance signal

Gate = the table in §"No-behavior-delta proof plan" (full suite unchanged, `ruff check .` clean **with `D` selected over `src/`**, `ruff format --check .` clean, `mypy src/` unchanged, `mkdocs build --strict` passes, AST digest identical, INV-A test re-run green) + INV-B/C/E/F verified against the final diff.

**Acceptance signal (plain language, from the TODO):** `uv run ruff check .` is green with `D` selected over `src/`; every public object in the backend packages has a docstring that says something its signature does not; `userdocs/api.md` renders real text instead of blanks; `mkdocs build --strict` still passes; the full test suite and `mypy src/` are unchanged.

## Findings (recorded at P.4 — the Problem-Log item the P.2 log owed here)

| # | Finding | Measured truth (2026-10-08, `ruff 0.16.10`, `45aa61c`) |
|---|---|---|
| F-1 | `docs/todo/ruff-d-docstrings.md` §Why still carries "`uv run ruff check --select D src` → **379 errors**" (2026-10-04) | `src/` = **398** bare, **328** under the chosen google convention. The 386 figure from P.2 (`305add3`) is also superseded — `structlog-logging` merged since then |
| F-2 | The `pyproject-tooling-gaps` claim "**156 of 515 public defs** lack a docstring" is **not reproducible** under any `D` rule | The `src/` missing-docstring family is **198** (`D102` 131, `D107` 51, `D101` 14, `D105` 2); no `D` code reports "public defs" |
| F-3 | TODO/Q-17 say "**45** `@logged_class` classes" | **41** decorated classes in `src/` (AST count), all of them already documented; the AC-009 test asserts the wording for **19** of them |
| F-4 | TODO per-feature `D1xx` split (authentication 50, usermanagement 45, filemanagement 37, permissions 32, settings 14, mail 6, search 6, eventbus 3, sessionmanagement 2) | usermanagement **47**, permissions **33**; the rest unchanged. Phase 4 uses the fresh table in §Fresh measurement |
| F-5 | TODO/Q-11 call it "the **123** `src/` format sites (`D205` 66, `D209` 57, `D301` 3, `D403` 4)" | Those four codes sum to **130**, and only 61 are auto-fixable (`D209` 57 + `D403` 4 safe; `D301` 3 unsafe-only); `D205` (66) has **no fix at all** |
| F-6 | Q-28's answer pins the pre-commit hook to "**v0.16.9**" | The dev pin is `ruff>=0.16.10` and the installed ruff is **0.16.10**; Q-28's stated intent ("match the dev pin") resolves to `rev: v0.16.10`. A scope detail, not a user block |
| F-7 | P.2 recorded `tests/` = 762 `D` sites (input for the sibling change) | **827** bare / **743** under google. Out of scope here — `docstrings-tests` must re-measure at its own P.4 |
| F-8 | Q-18 reads as if `docstring_style: google` changes rendering | `mkdocstrings-python 2.0.8` already defaults to `google` — the pin is explicit but inert; the rendering delta comes from the docstrings themselves |
| F-9 | `uv.lock` on `main` is **stale**: it records `python-template 0.6.1` while `pyproject.toml:4` says `1.0.0` (the `structlog-logging` bump never re-locked) | Any `uv run` in a fresh worktree rewrites `uv.lock` (1-line diff), so the change worktree cannot stay `git status`-clean without a decision. **Recommendation for the orchestrator:** fold the one-line `uv.lock` refresh into this change's config commit (non-behavioral, forced by the tooling), or open a separate one-line chore TODO. Not decided in P.3; reverted here so the scope record stands alone |

None of F-1 … F-9 changes what this change does: every figure is a count, and the one version number (F-6) follows its answer's own stated intent. **No item in the P.3 decision set alters externally observable behavior**, so the DOCS/CHORE classification stands and no `BLOCKED-USER` question is raised.

## Phase 4 — S4.1 baseline (2026-10-09)

Measured in this worktree at `8ec2edf` (P.4 scope record; `src/` byte-identical to `45aa61c` — **no implementation file edited yet**, by design). DOCS/CHORE has no RED gate; this section is the GREEN baseline Phase 5 (S5.1/S5.2) must reproduce. Toolchain at measurement: `ruff 0.16.10`, `mypy 2.4.0`, `Python 3.14.5`.

### Gate baselines (what Phase 5 compares against)

| Evidence | Command | S4.1 baseline (2026-10-09) |
|---|---|---|
| Suite unchanged | `uv run pytest tests/ -q` | **`1 failed, 760 passed, 1 skipped in 236.60s (0:03:56)`** — the single failure is the pre-existing timing flake in §Baseline flake; skip = `SKIPPED [1] tests\acceptance\filemanagement\test_filemanagement.py:364: symlinks not available on this host` |
| Types unchanged | `uv run mypy src/` | **`Success: no issues found in 84 source files`** |
| Lint as the gate stands today (`D` not yet selected) | `uv run ruff check .` | **`All checks passed!`** (exit 0) |
| Format gate | `uv run ruff format --check .` | **`339 files already formatted`** (exit 0) |
| Executable code identical | AST digest, §method below | **`64fc1d6ee758bf6ac572d58b100eff95d4bbd1205c993f7d9e2e126657d7bec0`** — **MATCHES** the P.4 baseline; run twice, identical output |

### AST digest reproduction (§method)

The throwaway script is the one embedded verbatim in §No-behavior-delta proof plan — copied unchanged to a path **outside** the repo (`%LOCALAPPDATA%/Temp/s41_ast_digest.py`), never added to `scripts/` (Q-25). Run in this worktree with the **relative** `src` root:

```text
uv run python "$LOCALAPPDATA/Temp/s41_ast_digest.py" src
→ 64fc1d6ee758bf6ac572d58b100eff95d4bbd1205c993f7d9e2e126657d7bec0   (run 1)
→ 64fc1d6ee758bf6ac572d58b100eff95d4bbd1205c993f7d9e2e126657d7bec0   (run 2, stability check)
```

Phase 5 re-runs the same command at the final commit and requires the same digest (INV-D).

### Baseline flake (pre-existing; recorded so Phase 5 does not misread it)

`tests/contract/search/test_search_contracts.py::test_nfr_001_performance_budgets` failed in the full-suite run:
`assert statistics.median(query_samples) < 0.3` → `0.30619730008766055 < 0.3` (NFR-001 local budget, 2% over, 10k-item SQLite source under the load of a 762-test run).

- Isolated re-run at the same commit: **`1 passed in 8.44s`** → timing/load flake, not a defect and not caused by this change (no `src/` file edited at S4.1; INV-D keeps the code identical to `main`).
- Same class as the history: `docs/workflow/PROBLEMS.md` **P-36** (the NFR-001 budget is tight against the current query path) and the flaky-failure classifications in `docs/verification/search.md` §S5.1.
- **Consequence for the Phase 5 gate:** "identical counts" is not reproducible for this one test. If S5.1 shows exactly this failure, re-run it in isolation; pass ⇒ classify as the known flake and record it, exactly as `search.md` did. Any *other* delta from `1 failed, 760 passed, 1 skipped` is a regression. → Problem Log **P-73**.

### Per-feature `D`-site work list (the gated set: `D` over `src/`, `convention = "google"`)

Measured **without** editing `pyproject.toml` — one run per group, the convention supplied inline so the numbers are what the gate will see once `select += "D"` lands (group 11):

```text
uv run ruff check src/backend/<group> --select D --output-format=concise \
  --config 'lint.pydocstyle.convention = "google"'
```

The inline `--config` also suppresses the two incompatible-rule warnings that bare `--select D` prints (as §Fresh measurement predicts), so the counts are directly comparable to the gate.

| Commit order | Group | Files | `D` total | `D1xx` additions | format (`D205`/`D209`/`D403`/`D301`) | codes |
|---|---|---|---|---|---|---|
| 1 | eventbus | 1 | 3 | 3 | 0 | `D105`:2 `D107`:1 |
| 2 | logging | 1 | 2 | 0 | 2 | `D205`:1 `D209`:1 |
| 3 | mail | 4 | 6 | 6 | 0 | `D107`:5 `D102`:1 |
| 4 | sessionmanagement | 3 | 16 | 2 | 14 | `D205`:7 `D209`:6 `D403`:1 `D102`:1 `D107`:1 |
| 5 | settings | 2 | 16 | 14 | 2 | `D102`:10 `D107`:4 `D205`:1 `D301`:1 |
| 6 | permissions | 6 | 45 | 33 | 12 | `D102`:22 `D107`:11 `D205`:5 `D209`:5 `D301`:2 |
| 7 | authentication | 7 | 51 | 50 | 1 | `D102`:36 `D101`:7 `D107`:7 `D205`:1 |
| 8 | filemanagement | 6 | 58 | 37 | 21 | `D102`:27 `D205`:11 `D107`:10 `D209`:9 `D403`:1 |
| 9 | search | 4 | 61 | 6 | 55 | `D205`:28 `D209`:26 `D107`:5 `D102`:1 `D403`:1 |
| 10 | usermanagement | 7 | 70 | 47 | 23 | `D102`:33 `D205`:12 `D209`:10 `D101`:7 `D107`:7 `D403`:1 |
| 11 | config (`pyproject.toml` + `mkdocs.yml` + `.pre-commit-config.yaml` + `AGENTS.md`) | 4 | 0 | 0 | 0 | gate flips |
| — | **Total (`src/`)** | **41** | **328** | **198** | **130** | `D102` 131 · `D205` 66 · `D209` 57 · `D107` 51 · `D101` 14 · `D403` 4 · `D301` 3 · `D105` 2 |

Cross-check: the ten group runs sum to **328 findings in 41 files**, and `uv run ruff check src --select D --statistics --config 'lint.pydocstyle.convention = "google"'` reports the same per-code totals; `src/main.py` + `src/frontend/` → **0** sites. The §Fresh measurement table (measured at `45aa61c`) **holds at `8ec2edf`** — no figure needed correcting in this step.

Mechanical vs manual split per group (derived from the code counts, per §Exact change scope item 1): `D209` + `D403` have safe fixes (61 repo-wide), `D301` (3: settings 1, permissions 2) needs an explicit `--unsafe-fixes` run on the changed paths, `D205` (66) has **no** fix and is hand-edited. Groups 1 and 3 have no format half; group 2 has no `D1xx` half — the pair collapses per feature as the commit plan says.

File-level work list (per group, `D` = total sites, `D1xx` = additions, `fmt` = format sites):

```text
eventbus
  src/backend/eventbus/eventbus.py                        D=3  D1xx=3  fmt=0   [D105x2 D107x1]
logging
  src/backend/logging/_decorator.py                       D=2  D1xx=0  fmt=2   [D205x1 D209x1]
mail
  src/backend/mail/errors.py                              D=3  D1xx=3  fmt=0   [D107x3]
  src/backend/mail/models.py                              D=1  D1xx=1  fmt=0   [D102x1]
  src/backend/mail/service.py                             D=1  D1xx=1  fmt=0   [D107x1]
  src/backend/mail/transport.py                           D=1  D1xx=1  fmt=0   [D107x1]
sessionmanagement
  src/backend/sessionmanagement/events.py                 D=1  D1xx=1  fmt=0   [D102x1]
  src/backend/sessionmanagement/search_source.py          D=12 D1xx=0  fmt=12  [D205x6 D209x5 D403x1]
  src/backend/sessionmanagement/service.py                D=3  D1xx=1  fmt=2   [D107x1 D205x1 D209x1]
settings
  src/backend/settings/registry.py                        D=2  D1xx=1  fmt=1   [D107x1 D205x1]
  src/backend/settings/repository.py                      D=14 D1xx=13 fmt=1   [D102x10 D107x3 D301x1]
permissions
  src/backend/permissions/catalog.py                      D=3  D1xx=1  fmt=2   [D301x2 D107x1]
  src/backend/permissions/errors.py                       D=6  D1xx=6  fmt=0   [D107x6]
  src/backend/permissions/events.py                       D=1  D1xx=1  fmt=0   [D102x1]
  src/backend/permissions/models.py                       D=3  D1xx=1  fmt=2   [D102x1 D205x1 D209x1]
  src/backend/permissions/repositories.py                 D=27 D1xx=23 fmt=4   [D102x20 D107x3 D205x2 D209x2]
  src/backend/permissions/service.py                      D=5  D1xx=1  fmt=4   [D205x2 D209x2 D107x1]
authentication
  src/backend/authentication/errors.py                    D=1  D1xx=1  fmt=0   [D107x1]
  src/backend/authentication/events.py                    D=7  D1xx=7  fmt=0   [D101x7]
  src/backend/authentication/repositories.py              D=1  D1xx=0  fmt=1   [D205x1]
  src/backend/authentication/repository.py                D=21 D1xx=21 fmt=0   [D102x18 D107x3]
  src/backend/authentication/service.py                   D=12 D1xx=12 fmt=0   [D102x11 D107x1]
  src/backend/authentication/tracker.py                   D=4  D1xx=4  fmt=0   [D102x3 D107x1]
  src/backend/authentication/webauthn.py                  D=5  D1xx=5  fmt=0   [D102x4 D107x1]
filemanagement
  src/backend/filemanagement/errors.py                    D=6  D1xx=6  fmt=0   [D107x6]
  src/backend/filemanagement/events.py                    D=1  D1xx=1  fmt=0   [D102x1]
  src/backend/filemanagement/repository.py                D=21 D1xx=17 fmt=4   [D102x16 D107x1 D205x2 D209x2]
  src/backend/filemanagement/search_source.py             D=12 D1xx=0  fmt=12  [D205x6 D209x5 D403x1]
  src/backend/filemanagement/service.py                   D=6  D1xx=1  fmt=5   [D107x1 D205x3 D209x2]
  src/backend/filemanagement/storage.py                   D=12 D1xx=12 fmt=0   [D102x10 D107x2]
search
  src/backend/search/errors.py                            D=5  D1xx=3  fmt=2   [D107x3 D205x1 D209x1]
  src/backend/search/events.py                            D=3  D1xx=1  fmt=2   [D102x1 D205x1 D209x1]
  src/backend/search/models.py                            D=14 D1xx=0  fmt=14  [D205x7 D209x7]
  src/backend/search/service.py                           D=39 D1xx=2  fmt=37  [D205x19 D209x17 D107x2 D403x1]
usermanagement
  src/backend/usermanagement/errors.py                    D=4  D1xx=4  fmt=0   [D107x4]
  src/backend/usermanagement/events.py                    D=8  D1xx=8  fmt=0   [D101x7 D102x1]
  src/backend/usermanagement/models.py                    D=2  D1xx=2  fmt=0   [D102x2]
  src/backend/usermanagement/repository.py                D=19 D1xx=15 fmt=4   [D102x14 D205x2 D209x2 D107x1]
  src/backend/usermanagement/role_store.py                D=3  D1xx=3  fmt=0   [D102x2 D107x1]
  src/backend/usermanagement/search_source.py             D=12 D1xx=0  fmt=12  [D205x6 D209x5 D403x1]
  src/backend/usermanagement/service.py                   D=22 D1xx=15 fmt=7   [D102x14 D205x4 D209x3 D107x1]
```

### S4.1 exit state

Nothing edited: `git status --porcelain` showed only `M uv.lock` (finding F-9 — rewritten by every `uv run`), restored before this commit and never staged. `src/`, `pyproject.toml`, `mkdocs.yml`, `.pre-commit-config.yaml`, `AGENTS.md` untouched.

**Next (S4.2, group 1):** `eventbus` docstrings — 3 sites in 1 file (`src/backend/eventbus/eventbus.py`: `D105`×2 `__enter__`/`__exit__` per Q-13, `D107`×1), no format half (0 format sites → the pair collapses to one commit).

## Phase 4 — groups 1-3 (S4.2, 2026-10-09)

Three commit-plan groups done, one commit each (groups 1 and 3 have no format half, group 2 has no `D1xx` half — the pair collapses per feature as §Commit plan says). Every `uv run` rewrote `uv.lock` (F-9); it was `git restore`d before each commit and never staged.

| Group | Commit | Sites fixed | `ruff check src/backend/<group>` | `--select D` (google) after | Feature tests (`-q`) |
|---|---|---|---|---|---|
| 1 `eventbus` | `1560bfc` `docs(eventbus): add missing docstrings (D105 x2, D107 x1)` | 3 additions | All checks passed! | **0** | `tests/{acceptance,unit,contract,integration,property}/eventbus` → **31 passed** |
| 2 `logging` | `a7894c8` `docs(logging): fix docstring formatting (D205, D209)` | 2 format | All checks passed! | **0** | `tests/acceptance/logging tests/acceptance/logging_coverage` → **33 passed**; AC-009 `test_traced_class_docstrings_mention_tracing` → **1 passed** (INV-A) |
| 3 `mail` | `b96ad16` `docs(mail): add missing docstrings (D107 x5, D102 x1)` | 6 additions | All checks passed! | **0** | `tests/{acceptance,unit,contract,integration,property}/mail` → **40 passed** |

### Sites, as edited

```text
eventbus  src/backend/eventbus/eventbus.py
  47  D107 EventBus.__init__              added (queue bound; None → live eventbus.max_queue_size
                                          setting else 1000, AC-017/AC-018; worker starts lazily)
  168 D105 EventBus.__enter__             added (returns the bus; still no worker thread)   [Q-13]
  171 D105 EventBus.__exit__              added (drains then stops; exception args ignored ⇒ never suppresses)  [Q-13]
logging   src/backend/logging/_decorator.py
  77  D205 + D209 _is_private_method      summary line split from the description; closing """ on its own line
mail      src/backend/mail/errors.py
  23  D107 MailConfigurationError.__init__   added
  37  D107 MailTransportError.__init__       added
  52  D107 MailTemplateError.__init__        added
mail      src/backend/mail/models.py
  52  D102 EventPublisher.publish          added (abstract one-liner → docstring + `...`)
mail      src/backend/mail/service.py
  42  D107 MailService.__init__           added (the three optional seams; AC-031 citation kept)
mail      src/backend/mail/transport.py
  44  D107 SmtpTransportImpl.__init__     added (no connection at construction; auth only when username non-empty)
```

Private helpers in all six touched files already carried docstrings (`_handler_name`, `_ensure_worker_unlocked`, `_worker_loop`, `_dispatch`, `_get_transport`, `_publish`) — INV-H needs no additions here. No filler docstring was written (INV-G): each states a fact the signature does not (resolution order, laziness, exception semantics, seam defaults). No `REQ-`/`AC-` citation was removed (INV-I); `AC-017/AC-018`, `AC-031`, `NFR-002` stay cited.

### No-behavior-delta (INV-D)

The throwaway script of §No-behavior-delta proof plan — byte-identical to the embedded block (verified by extracting the fenced block and comparing) — was re-used at `%LOCALAPPDATA%/Temp/s41_ast_digest.py`, never added to `scripts/` (Q-25):

```text
uv run python "$LOCALAPPDATA/Temp/s41_ast_digest.py" src
→ 64fc1d6ee758bf6ac572d58b100eff95d4bbd1205c993f7d9e2e126657d7bec0   (run 1)
→ 64fc1d6ee758bf6ac572d58b100eff95d4bbd1205c993f7d9e2e126657d7bec0   (run 2)
```

**MATCHES** the S4.1/P.4 baseline — the executable code in `src/` is unchanged. `git diff --stat 84b25bd..b96ad16` = 6 files, +41/−3, all inside docstrings (the 3 deletions are the reformatted `_is_private_method` summary line and the `EventPublisher.publish` one-liner). `ruff format src/backend/{eventbus,logging,mail}` → "files left unchanged" in all three groups.

### Q-26 check (docstring vs. code)

No docstring was written that contradicts the code, so no finding under the binding amendment. One observation for the record (not a finding, no action taken): `MailService._publish` does **not** catch a publisher exception, so a failing publisher propagates out of `send_email` — unlike user-management/authentication/file-management, whose `AGENTS.md` entries promise "a publisher failure never breaks the operation". The mail spec (REQ-012, D9) makes no such promise, and the new `EventPublisher.publish` docstring states the actual behavior ("does not catch a publisher exception, so a failing publisher surfaces to the caller"). If isolation is intended for mail, that is a separate ISSUE/FEATURE, not this change.

**Next (S4.2, groups 4-5):** `sessionmanagement` (16 sites: 2 additions + 14 format) → `settings` (16 sites: 14 additions + 2 format, incl. 1 `D301` needing `--unsafe-fixes`).

## Phase 4 — groups 4-5 (S4.2, 2026-10-09)

Groups 4 (`sessionmanagement`) and 5 (`settings`) done, **two commits each** — additions half then format half (Q-11). `uv.lock` was rewritten by every `uv run` (F-9), `git restore`d before each commit, never staged.

| Group | Commit | Sites | `ruff check src/backend/<group>` | `--select D` (google) after | Feature tests (`-q`) |
|---|---|---|---|---|---|
| 4 `sessionmanagement` additions | `e3f95c6` `docs(sessionmanagement): add missing docstrings (D102 x1, D107 x1)` | 2 additions | All checks passed! | 14 (format half pending) | — |
| 4 `sessionmanagement` format | `df45d17` `docs(sessionmanagement): fix docstring formatting (D205, D209, D403)` | 14 format | All checks passed! | **0** | `tests/{acceptance,contract,integration,property,unit}/sessionmanagement` → **69 passed** |
| 5 `settings` additions | `899c027` `docs(settings): add missing docstrings (D102 x10, D107 x4)` | 14 additions | All checks passed! | 2 (format half pending) | — |
| 5 `settings` format | `2284b71` `docs(settings): fix docstring formatting (D205, D301)` | 2 format | All checks passed! | **0** | `tests/{acceptance,contract,integration,property,unit}/settings{,_coverage}` → **103 passed** |

### Sites, as edited

```text
sessionmanagement  src/backend/sessionmanagement/events.py
  55  D102 EventPublisher.publish          added (synchronous fire-and-forget; the bus only
                                          enqueues; a publisher exception is NOT caught ⇒
                                          propagates, REQ-018). The stub body `...` is kept
                                          after the docstring — see INV-D below.
sessionmanagement  src/backend/sessionmanagement/service.py
  69  D107 SessionService.__init__        added (construction is the only wiring point: cap
                                          eviction on the *shared* bus, user-lifecycle
                                          revocation on the *injected* one and only if it has
                                          `subscribe`; None permission_service = standalone,
                                          AC-031; REQ-014/REQ-015/AC-038)
```

Format half, group 4 — 14 findings over 8 docstrings, **all hand-edited**: `--fix` and `--diff` offered **no** fix for the 6 `D209` and the 1 `D403` here. Probed on isolated single-code docstrings in `%TEMP%` (ruff 0.16.10): `D209 --fix`/`--diff` and `D403 --fix` produce **nothing** — neither code has a fixer in this version — so §"Mechanical vs manual split"'s "`D209` + `D403` have safe fixes (61 repo-wide)" does **not** hold; all 61 are hand-edits. Recorded here as finding **F-10** (the §Findings table stops at P.4); Phase 5/6 should re-measure the remaining groups' mechanical share.

```text
sessionmanagement  src/backend/sessionmanagement/search_source.py
  95  D205+D209 _free_text_matches        summary line + blank line + closing """ own line
  105 D205+D209 _eval_group               idem
  115 D205+D209 _eval_condition           idem
  143 D403      _apply_exact_operator     `boolean` → `Boolean` (first word capitalized)
  153 D205+D209 _sort_key                 idem
  163 D205+D209 _query                    idem
  189 D205      build_session_source      blank line after the summary (closing """ already ok)
sessionmanagement  src/backend/sessionmanagement/service.py
  217 D205+D209 _order_with_current       summary line split; closing """ own line
```

```text
settings  src/backend/settings/registry.py
  59  D107 SettingsRegistry.__init__      added (seam defaults incl. the lazy eventbus import that
                                          breaks the circular import; persisted values loaded once
                                          and override defaults, REQ-009/REQ-011 of
                                          settings-coverage; None permission_service = standalone,
                                          AC-031)
settings  src/backend/settings/repository.py
  131 D107 YamlValueRepository.__init__   added (single values.yaml, dir created eagerly, lock is
                                          per-instance not cross-process)
  139 D102 .save                          added (temp file + os.replace ⇒ never a partial file)
  147 D102 .load                          added (missing file is not an error; corrupted file →
                                          ValueStorageError, EDGE-003)
  202 D107 MemoryTemplateRepository.__init__ added (nothing loaded, nothing persisted)
  206 D102 .save                          added (silent replace; the frozen instance itself is kept)
  210 D102 .get                           added
  214 D102 .delete                        added (unknown name = silent no-op)
  218 D102 .list                          added (name-ordered, not insertion-ordered)
  233 D107 YamlTemplateRepository.__init__ added (one file per template, dir created eagerly)
  241 D102 .save                          added (.<name>.yaml.tmp sibling, atomic, REQ-022)
  255 D102 .get                           added (name selects the file only; fields come from the
                                          file; corrupted/incomplete → TemplateStorageError, AC-032)
  272 D102 .delete                        added (absent file = silent no-op)
  278 D102 .list                          added (one corrupted file fails the whole listing, AC-032)
```

Q-14 / INV-H additions in the touched files (not gate-detected — `D` under the google convention ignores private defs; found with a one-off `ast` walk): `registry.py` `_require_definition`, `_scope_keys`, `_publish_setting_changed`, `_persist_values`; `repository.py` `_path` ×2, `_parse` ×2. Every other private helper in the five touched files already had a docstring.

Format half, group 5:

```text
settings  src/backend/settings/registry.py
  1   D205 module docstring               summary line split from the description (hand-edited)
settings  src/backend/settings/repository.py
  49  D301 _str_representer              `r"""` prefix + `\\x85` → `\x85`, so the docstring VALUE is
                                          byte-identical (verified: ast.get_docstring of the
                                          function is equal before and after). `--unsafe-fixes`
                                          was deliberately NOT used: it only adds the `r` prefix,
                                          which would have doubled the backslash in the rendered
                                          docstring (a needless content change).
```

### Gates & no-behavior-delta (INV-D)

```text
uv run ruff check src/backend/sessionmanagement src/backend/settings --select D \
  --config 'lint.pydocstyle.convention = "google"'      → All checks passed!   (0)
uv run ruff check .                                     → All checks passed!
uv run ruff format --check src/backend/sessionmanagement src/backend/settings → 13 files already formatted
uv run python "$LOCALAPPDATA/Temp/s41_ast_digest.py" src → 64fc1d6ee758bf6ac572d58b100eff95d4bbd1205c993f7d9e2e126657d7bec0   (twice)
git diff --stat 70f68b2..HEAD                           → 5 files, +150/−26, all inside docstrings
```

**Digest near-miss, caught and fixed inside this execution.** The group-4 additions commit first replaced the protocol stub body `def publish(...) -> None: ...` with the docstring alone; the digest then printed `0736d32b…` — the strip script replaces an emptied body with `Pass`, so dropping the `Expr(Ellipsis)` **is** an AST delta. Fixed by keeping `...` after the docstring (the pattern group 3 used for `mail/models.py:52`), digest back to `64fc1d6e…`, and the one-line fix folded into `e3f95c6` with `git commit --fixup` + `--autosquash` (the branch was never pushed, so no history was rewritten for anyone else). The digest is what caught it — INV-D earned its keep.

### Q-26 check (docstring vs. code)

No docstring contradicts the code; each of the following is stated **as the code is**, with no code change and no reclassification:

- `sessionmanagement.events.EventPublisher.publish` — the feature does not catch a publisher exception, so a failing publisher propagates to the calling session method. The session-management spec (REQ-018) makes no isolation promise, so this is not a defect; it is the same observation already recorded for mail.
- `settings.repository.YamlTemplateRepository.get` — the requested name only selects the file; the returned template's fields come from the file, so a file whose `name` field disagrees with its stem is returned unchanged (no cross-check exists).
- `settings.repository.YamlTemplateRepository._path` — the repository neither validates nor escapes the name; the registry does (`is_template_name_valid`). Documented at the method.
- Citation note (no edit): the pre-existing comments in `_persist_values` cite `REQ-009`/`EDGE-009`, which are **`settings-coverage.md`** IDs (`settings.md` REQ-009 is *resets*). The new docstrings cite the `settings-coverage` IDs where the behavior comes from that spec (REQ-009, REQ-010, REQ-011, EDGE-003, EDGE-009) and `settings.md` IDs where it comes from that one (REQ-022, AC-032); no existing citation was removed (INV-I).

**Next (S4.2, group 6):** `permissions` (45 sites: 33 additions + 12 format, incl. 2 `D301`).
