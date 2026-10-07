# ADR-084: Two guards for the singleton slot — ruff `TID251` banned-api plus a source-scanning architecture test

## Status
Accepted

## Context
ADR-083 makes the install operation the only public way to change a feature's
shared default. That holds only if nothing writes another package's private slot
again — and 12 sites did exactly that (see ADR-083). A reviewer cannot catch the
pattern by eye across five feature packages plus the test suite, and the pattern
re-appears silently: the write is one line, it works, and nothing downstream
notices.

The repository already has both candidate mechanisms in some form:

- **ruff** is the CI-enforced lint gate (`.github/workflows/lint.yml:37` runs
  `uv run ruff check .`), and it has a `flake8-tidy-imports` `banned-api` rule —
  **never used in this repository** (`grep -rn "banned-api\|flake8-tidy"
  pyproject.toml` → no match; `[tool.ruff.lint] select` at `pyproject.toml:182`
  lists `I,E,W,B,F,UP,RUF,PL,Q,SIM,C4,DTZ` and no `TID` rule).
- **A source-scanning pytest test**: `tests/acceptance/logging_coverage/test_new_classes_traced.py`
  walks `pathlib.Path("src/backend").rglob("*.py")`, `ast.parse`s each file and
  enforces a rule. There is **no** `tests/architecture/` directory — the merged
  `architecture-tests-missing` change (`4f684f8`) removed that path from the
  workflow, and its own architecture checks were `rg` scans recorded in
  `docs/verification/architecture-tests-missing.md`, not executable tests.

Five measurements (P.5 dependency smoke-test, `docs/verification/settings-public-registry-setter.md`)
decide the shape of the guard, and they are the reason this is a decision rather
than a detail:

| Probe | Result |
|---|---|
| `banned-api` entry with the project's real `select` list, **without** `TID251` selected | the violation is **not** reported — the whole table is **inert** |
| `banned-api` key given as the **bare slot name** (`"_registry"`) | `All checks passed!` — flags **nothing**; keys must be fully qualified |
| fully-qualified key + `from backend.settings.registry import _registry` | `TID251` reported |
| fully-qualified key + `import backend.settings.registry as reg` then `reg._registry[0] = …` | `TID251` reported (the form `tests/eventbus_test_helpers.py:76-85` uses today) |
| violation written **inside the owning module** (its own slot) | **not** reported — `TID251` flags cross-module references only |
| `uv run ruff check --isolated --select TID src tests` | `All checks passed!` — zero pre-existing violations, so selecting the rule cannot break the lint gate by itself |

And one fact about the writes themselves: **3 of the 12 migrated sites are code
strings handed to `subprocess`** (`tests/acceptance/settings_coverage/test_setup_logger.py:31,55`,
`tests/acceptance/settings_coverage/test_wiring.py:18`), so a scan that walks only
real statements does not see them.

## Decision
Guard the pattern **twice**, because the two guards see different things:

1. **ruff `TID251` banned-api**, with one entry per private slot keyed by its
   **fully-qualified module path** (`backend.settings.registry._registry`,
   `backend.eventbus.eventbus._default_bus`,
   `backend.permissions.service._permission_service`,
   `backend.search.service._singleton`,
   `backend.sessionmanagement.service._session_service`), each `.msg` naming that
   feature's `set_* / get_* / reset_*` trio — **and** `TID251` added to
   `[tool.ruff.lint] select`. Only `TID251` is selected, not the whole `TID`
   family. Without the `select` entry the table enforces nothing (`REQ-013`,
   `AC-018`, `NFR-004`).
2. **A pytest scan test in a new `tests/unit/architecture/` package** that walks
   every `.py` under `src/` and `tests/` and fails, naming file and line, on an
   assignment to a slot owned by a different package — checking **both** real
   statements (`ast`) **and** the same pattern inside string literals
   (`ast.Constant` str nodes), with a planted-violation fixture (one per form)
   proving the scanner actually fires (`REQ-012`, `AC-017`).

**Ban width (normative).** The guard targets the five private slots, not the
module and not the public API: importing `get_*`/`set_*`/`reset_*`, or a public
symbol from the owning module path (`from backend.settings.registry import
SettingsRegistry`, 13 test sites today), is never flagged, and a module writing
its **own** slot stays legal — the five lazy-create and reset paths need no
suppression (`EDGE-008`, `EDGE-009`).

## Consequences
- **The import that makes a foreign write possible is caught at edit time**, in
  the lint job that already runs on every push — no CI change is needed. The
  `.msg` text is the guidance: it names the trio the caller should use instead.
- **The write itself is caught in the test suite**, including the form the lint
  rule cannot see (code inside a `subprocess` string), and the planted-violation
  fixture means the guard cannot rot into a test that passes vacuously.
- **Future singleton-owning features add one `banned-api` key and one entry in the
  scanner's slot list** — the guard is a pattern, not a one-off.
- **Costs / risks:** one more rule in `select` — any future code that imports a
  private slot now fails the lint gate and must be migrated rather than suppressed
  (measured: zero pre-existing violations, so the rule cannot break the gate on
  landing). The string-literal half of the scan is a **heuristic**: it matches the
  slot-name assignment pattern in any string, so a comment or a doc string that
  spells the pattern out would be reported — accepted, because the alternative
  (ast-only) misses the three real embedded sites. The scanner's slot list must be
  kept in sync with the five features by hand.
- **The guard is not an import-permission rule.** Who may import
  `backend.settings` / `backend.eventbus` at all is TODO
  `public-api-import-boundary`; `TID251` here bans five names, not a package.
- **No new dependency**: ruff, pytest and mypy are already installed
  (`docs/specs/settings-public-registry-setter.md` §12 row 9).

## Alternatives Considered
- **ruff only** — rejected: `TID251` inspects imports and attribute references in
  real code, so it never sees the three subprocess-embedded writes, and it does
  not run over string content.
- **Scan test only** — rejected: it fires in CI after the code is written, not at
  edit time in the lint gate, and it does not flag the import that makes the write
  possible. The two guards are complementary, and both are cheap (Q-16).
- **`rg`-based architecture checks recorded in a verification document** (the
  `architecture-tests-missing` precedent) — rejected: not executable, not
  CI-enforced, no planted-violation proof, and it would leave `REQ-012` with no
  test in the suite.
- **Bare-name `banned-api` keys** (`"_registry"`) — rejected **on measurement**:
  they flag nothing, so the guard would pass vacuously.
- **Select the whole `TID` family** — rejected: `TID252` (relative imports) is a
  wider rule than the agreed ban width (Q-19); measured zero violations either
  way, so the narrower selection costs nothing today and keeps the gate's scope
  explicit.
- **A custom ruff/mypy plugin or a lint plugin package** — rejected: a new
  dependency and a maintenance surface for a rule the installed linter already
  implements.
- **Rely on review discipline instead of a guard** — rejected: the pattern already
  reached 12 sites, including the composition root, while the repo had a written
  rule against it.

## References
- `docs/specs/settings-public-registry-setter.md` — REQ-012, REQ-013, AC-017,
  AC-018, EDGE-005, EDGE-008, EDGE-009, NFR-004; decision D12; §3.4 (the
  normative `pyproject.toml` block and scanner contract); §10 (the measured
  mechanics: `tests/unit/architecture/` is new and needs an `__init__.py`; the
  existing scanning test to follow; `--isolated --select TID` reports no
  pre-existing violation).
- `docs/decisions/ADR-083-public-install-operation-feature-singletons.md` (the
  interface this guard protects).
- `docs/verification/settings-public-registry-setter.md` (§ "Dependency
  Smoke-Test" — the six ruff probes; § "S2.1 — ADR decision").
- `docs/verification/architecture-tests-missing.md` (the `rg`-scan precedent this
  ADR replaces with an executable test).
- `.github/workflows/lint.yml:37` (the job that runs `uv run ruff check .`).
