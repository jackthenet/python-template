# python-template

[![Quality](https://github.com/jackthenet/python-template/actions/workflows/quality.yml/badge.svg)](https://github.com/jackthenet/python-template/actions/workflows/quality.yml)
[![Lint](https://github.com/jackthenet/python-template/actions/workflows/lint.yml/badge.svg)](https://github.com/jackthenet/python-template/actions/workflows/lint.yml)
[![Spec Validation](https://github.com/jackthenet/python-template/actions/workflows/spec-validation.yml/badge.svg)](https://github.com/jackthenet/python-template/actions/workflows/spec-validation.yml)
[![Python >=3.14](https://img.shields.io/badge/python-%3E%3D3.14-blue)](pyproject.toml)
[![Ruff](https://img.shields.io/badge/lint-ruff-blue)](https://docs.astral.sh/ruff/)
[![uv](https://img.shields.io/badge/env-uv-blue)](https://docs.astral.sh/uv/)
[![pre-commit](https://img.shields.io/badge/hooks-pre--commit-blue)](https://pre-commit.com/)

Default template for Python projects.

## Why this exists

A starting point that is already wired: backend feature packages under `src/backend/`, a
Spec-Driven, Test-Driven workflow (`AGENTS.md`), and the CI gates that enforce it — lint,
types, security, coverage, docs, migrations, spec/traceability validation. Point it at a new
project and the front page, the process and the checks are already in place.

## Installation

```bash
uv sync
```

## Quick start

```python
from backend.usermanagement import SqliteUserRepository, UserCreate, UserManager

manager = UserManager(SqliteUserRepository("sqlite:///:memory:"))
user = manager.create_user(
    UserCreate(username="alice", email="alice@example.com", password="s3cret!x", roles=["user"])
)
assert manager.verify_password(user.id, "s3cret!x")
```

Run it with `uv run python <file>`. There is no app or CLI entry point to run yet — `src/main.py`
is startup wiring, not a command.

## Configuration

Typed, validated configuration comes from the shared settings registry in
[`src/backend/settings/`](src/backend/settings/) — register a `SettingDefinition` per key, read
it live, invalid writes raise `SettingsValidationError`. See
[`docs/specs/settings.md`](docs/specs/settings.md) for the kinds and rules, and
[`docs/specs/logging.md`](docs/specs/logging.md) for the `log_level` / `log_file` settings the
shared logging feature reads.

## Development

```bash
uv run pre-commit install          # one-time: run the hooks on every commit

uv run pytest tests/               # the whole suite
uv run pytest tests/acceptance/ -v # acceptance / integration / contract / property / unit
uv run pytest tests/ --cov --cov-report=xml   # coverage gate (fail_under = 92)

uv run ruff check .                # lint
uv run ruff format .               # format
uv run mypy src/                   # types (the gate); uv run ty check src/ is the fast local tool
uv run deptry .                    # unused / missing dependencies
uv run pip-audit                   # dependency vulnerabilities
uv run bandit -r src/              # static security

uv run mkdocs build --strict       # docs site (built from userdocs/) — needs `uv sync --group docs`
uv run alembic upgrade head        # apply schema migrations
uv run alembic revision -m "<description>"   # add one

uv run python scripts/check_traceability.py   # REQ/AC ↔ test referential integrity
uv run python scripts/verify_spec.py docs/specs/<name>.md
uv run python scripts/validate_task_dag.py .github/task-runner/tasks.json  # informational in CI
```

The same checks run in CI: [`Lint`](.github/workflows/lint.yml) (ruff),
[`Quality`](.github/workflows/quality.yml) (types, security, coverage, dependencies, docs,
migrations) and [`Spec Validation`](.github/workflows/spec-validation.yml) (spec validation,
traceability, tests).

## Structure

`src/backend/<feature>/` holds the feature packages directly (`src/main.py` is the entrypoint
wiring); `tests/` is split by category (`acceptance/`, `integration/`, `contract/`, `property/`,
`unit/`); `docs/` is the internal process record (specs, decisions, verification) while
`userdocs/` is the published mkdocs site; `scripts/` holds the three spec/traceability checkers.

The authoritative layout is [AGENTS.md](AGENTS.md), section "Project Structure".

## Contributing

The process is defined in [AGENTS.md](AGENTS.md): every change is classified (ISSUE, FEATURE,
CROSS-CUTTING, REFACTOR, DOCS/CHORE), prepared in `docs/todo/` + `docs/questions/`, implemented
in its own git worktree on a `feature/`, `issue/`, `crosscut/`, `refactor/` or
`chore/` branch, and reaches `main` only through a reviewed pull request. Tests precede
implementation; the RED and GREEN evidence and the verification report go in
`docs/verification/<name>.md`.
