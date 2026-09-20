# python-template

Default template for Python projects.

A feature-based Python application scaffold: `src/` holds the runtime
boundaries (`frontend/`, `backend/`), each feature owns its domain model and
use cases, and the test suite (`tests/`) mirrors the feature vocabulary
(acceptance, integration, contract, property, unit).

## Backend features

- **authentication** — login, sessions, password recovery, passkeys.
- **eventbus** — async, in-memory event bus for decoupled backend communication.
- **filemanagement** — user-file storage, avatars, validation.
- **logging** — structured logging with function/class tracing decorators.
- **mail** — email sending (SMTP) with typed templates.
- **sessionmanagement** — session listing, revocation, and expiry.
- **settings** — typed, validated settings registry with persistence.
- **usermanagement** — user account records, roles, and passwords.

## API reference

The [API reference](api.md) auto-documents each backend feature's public API
from its package `__init__` via [mkdocstrings](https://mkdocstrings.github.io/).

## Building the site

```bash
uv run mkdocs build --strict
```

The site source is `userdocs/` (this directory); `mkdocs.yml` at the repo
root points `docs_dir` at it. `docs/` at the repo root is the internal
process record (specs, decisions, verification) and is not part of the site.
