# ADR-086: `scripts/` becomes a type-checked tree; repo tooling stays stdlib-only in `scripts/`

## Status
Accepted

## Context
The generator this change adds is repository tooling, and where repo tooling lives decides which
gates see it. Measured at this branch head (`aabf878`), the gate map over the repository's Python is
asymmetric:

| Gate | Scope today | Covers `scripts/`? |
|---|---|---|
| `mypy` (CI `type-check` job) | `uv run mypy src/` | **no** |
| `ty` (local/informational) | `root = ["./src"]` (`[tool.ty.environment]`) | no |
| `ruff check` / `ruff format --check` (CI `lint`) | `.` | yes |
| `deptry` (CI `dependencies` + local hook) | `.` (hook `files` regex already includes `scripts/`) | yes |
| `coverage` (`fail_under = 92`) | `source = ["src/backend", "src/frontend"]` | no |
| `complexipy` (CI `complexity`) | `paths = ["src", "tests"]` | no |
| `bandit` (CI `security`) | `-r src/` | no |

So `scripts/` is already lint- and dependency-gated but **not type-checked**. Seven `.py` files live
outside `src/` and `tests/`: three in `scripts/` (`check_traceability.py`, `validate_task_dag.py`,
`verify_spec.py`), three in `migrations/`, one in `.github/hooks/ruff-post-edit.py`.

Widening the type gate is not free, and the cost is measured: `uv run mypy scripts/` at this head
reports **exactly one pre-existing error** —
`scripts/verify_spec.py:74: error: Item "TextIO" of "TextIO | Any" has no attribute "reconfigure"
[union-attr]` — **1 error in 1 file (checked 3 source files)**. The repository's mypy configuration is
strict (`disallow_untyped_defs = true`, `check_untyped_defs = true`, `python_version = "3.14"`).

The change also has to say what the generator is *not*: it is not a backend feature. It runs against
a checkout, over the repository itself, and must work before and independently of the application's
dependency set; `AGENTS.md`'s tracing policy and the shared logging feature are for backend features
(the existing `scripts/` modules set the precedent — none uses the logging feature).

## Decision
- **The generator lives at `scripts/make_map.py` and is stdlib-only** (REQ-001): `ast` (including
  `ast.unparse` for canonical signatures), `argparse`, `pathlib`, `subprocess`, `sys`, plus
  `collections`/`re`/`dataclasses` as needed. It adds **no project dependency**, reads each source
  file exactly once, and leaves `uv run deptry .` clean (NFR-003, AC-001).
- **`uv run mypy scripts/` joins the `type-check` job** of `.github/workflows/quality.yml`, next to
  `uv run mypy src/` (REQ-025, AC-025). `scripts/` thereby becomes typed, gate-covered code, and every
  future `scripts/` module inherits that requirement.
- **The pre-existing error is fixed in the same change**, confined to `scripts/verify_spec.py` and
  behaviour-preserving. The script has no unit tests, so its witness is the `spec-validation` job,
  which lists `scripts/verify_spec.py` as a path trigger and runs it over every spec (AC-025).
- **The widening is exactly the type gate, nothing else.** Coverage (`source = ["src/backend",
  "src/frontend"]`), complexipy (`paths = ["src", "tests"]`), bandit (`-r src/`) and `ty`
  (`root = ["./src"]`) keep their current scope; this change touches no coverage or complexity
  configuration, and the `fail_under = 92` floor must not move — `scripts/` and its tests earn no
  coverage credit (NFR-004, NFR-005, spec §13).
- **The generator is exempt from the tracing policy.** It uses no logging framework at all — neither
  the shared logging feature (a dependency REQ-001 forbids) nor stdlib `logging`; its entire
  observable output is the two `--check` lines on stdout and the sorted path lines on stderr
  (spec §10 Observability). Precedent: `scripts/check_traceability.py`, `scripts/verify_spec.py`.

## Consequences
- **Positive:** the generator's own contract — the exit-code table, the CLI surface, the render
  pipeline — is checked by the same gate as `src/`, so a type-level break in repo tooling fails CI
  instead of failing at the next pre-commit run; `deptry` stays meaningful because the generator
  imports nothing outside the standard library; the one latent mypy error in the repository is paid
  off rather than inherited.
- **Costs / accepted asymmetry:**
  - Every future `scripts/` file must satisfy strict mypy (`disallow_untyped_defs`), including
    throwaway tooling — a real cost, accepted because the tree now holds contract-bearing logic
    (≈250 lines targeting NFR-006), not one-liners.
  - The gate set stays asymmetric: `scripts/` is type-checked but not coverage-, complexity- or
    bandit-scanned, and the local `ty` tool does not see it. That asymmetry is now explicit so it is a
    decision someone can revisit, not an accident someone "fixes" by pointing every tool at `.`.
  - `mypy src/` and `mypy scripts/` are two invocations (two runs, two cache roots). Accepted:
    `scripts/` is three files, and merging the scopes would drag `migrations/` into the gate.
  - `scripts/` has no `__init__.py`, so mypy checks its files as standalone top-level modules; the
    `explicit_package_bases` / `namespace_packages` flags exist for the `src/backend` namespace
    package and do not affect them.
- **Not covered by this decision:** `migrations/` (3 `.py`, alembic-generated revisions) and
  `.github/hooks/ruff-post-edit.py` stay outside the type gate — REQ-025 widens it to `scripts/` only.

## Alternatives Considered
- **Put the generator under `src/` (e.g. `src/backend/structuremap/`)** — rejected: it is not a
  runtime feature and no in-process caller should import a repository-map generator; `src/` is the
  coverage source (`source = ["src/backend", "src/frontend"]`, `fail_under = 92`), so tooling would
  need coverage it does not earn, and the map's own Packages scope (REQ-011) deliberately treats
  `scripts/` as a first-class tree anyway.
- **A third-party documentation/API tool (sphinx autoapi, pydoc, mkdocstrings)** — rejected
  (REQ-001, NFR-003, spec §13): a new dependency for a job the standard library does exactly, with
  output ordering and formatting that are not byte-stable, so the `--check` exit-code contract
  (REQ-004/REQ-005) would not hold. `ast` + `ast.unparse` is the mechanism that gives canonical
  signatures immune to source formatting drift (REQ-014, AC-014).
- **Type-check the whole repository (`mypy .`)** — rejected: it would pull the alembic revision files
  under `migrations/` and `.github/hooks/` into the gate in the same PR, i.e. failures unrelated to
  this change; REQ-025 widens the gate to exactly the tree this change makes first-class.
- **Leave `scripts/` untyped** — rejected: the change adds a CLI with a five-code exit contract and a
  ~250-line render pipeline to an untyped tree, and the only obstacle (one `union-attr` error) is a
  one-line, behaviour-preserving fix.

## References
- `docs/specs/structure-map.md` — REQ-001, REQ-025; AC-001, AC-025; NFR-003, NFR-004, NFR-005,
  NFR-006; §10 (Observability), §13 (coverage note)
- `.github/workflows/quality.yml` — the `type-check` job (`uv run mypy src/`, `uv run ty check src/`)
- `.github/workflows/spec-validation.yml` — `scripts/verify_spec.py` as a path trigger and as the
  witness for the fixed script
- `.github/workflows/lint.yml`, `.pre-commit-config.yaml` — the gates that already cover `scripts/`
- `pyproject.toml` — `[tool.mypy]`, `[tool.ty.environment]`, `[tool.coverage.run]`,
  `[tool.coverage.report]`, `[tool.complexipy]`, `[tool.deptry]`
- `docs/decisions/ADR-085-committed-generated-structure-map-check-only-local-hook.md`
