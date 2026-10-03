# Project structure and boundaries

The backend is organized **by feature**, not by technical layer. Adapt names below if the repository already
does something different; follow the repo and mention the difference.

## Layout

```
src/backend/
├── authentication/        # one folder per feature
│   ├── __init__.py        # public interface: only what other features may import
│   ├── models.py          # database tables
│   ├── schemas.py         # request/response models (Pydantic)
│   ├── service.py         # business logic, no HTTP types
│   └── router.py          # HTTP layer, thin
└── <next_feature>/
```

The file names inside a feature are a suggestion; the rule that matters is **one feature = one folder**
containing everything that feature needs.

## Rules

- New code goes into the feature it belongs to. If it fits no feature, ask before creating a new top-level folder.
- Another feature may import only from a feature's public interface (`__init__.py`), never from its internal modules.
- No import cycles between features. If two features need each other, extract the shared concept or pass it in as a parameter.
- There is currently no shared/core folder next to the features. Do not create one preemptively; extract shared
  code only after at least three places need the identical thing (rule of three).
- Keep routers thin: parse input, call the service, return the result. Business logic lives in the service and takes plain
  Python values or models, so it can be tested without HTTP.
- Tests mirror the source layout: `tests/backend/<feature>/test_<module>.py`.

## Good and bad

Bad (reaches into another feature's internals):
```python
from backend.authentication.service import _hash_password
```

Good (uses the public interface):
```python
from backend.authentication import hash_password
```

## Optional: enforce it

The rules above are not checked by ruff or the type checker. `import-linter` can enforce them in CI:

```toml
[tool.importlinter]
root_package = "backend"

[[tool.importlinter.contracts]]
name = "Features do not import each other"
type = "independence"
modules = [
    "backend.authentication",
    # add every feature here
]
```

If features are allowed to call each other through public interfaces, use a `forbidden` contract on
the internal modules instead of `independence`.