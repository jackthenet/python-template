# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

This file is hand-maintained: there are no git tags, so each release section is dated from
its `Bump version:` commit (the `0.1.0` section from the commit that set the version).

## [Unreleased]

### Added

- A public install operation on each of the five singleton-owning features —
  `set_settings_registry()`, `set_event_bus()`, `set_permission_service()`, `set_search_service()`,
  `set_session_service()` — the third member of every feature's `get_*()` / `reset_*()` trio,
  re-exported from the feature package root. Installing over a non-empty default replaces it
  unconditionally and logs exactly one `WARNING`; it is never retroactive, never starts or shuts
  down either instance, never accepts `None` (clearing stays `reset_*()`'s job), and publishes no
  event (`settings-public-registry-setter` T-001…T-005, REQ-001…REQ-010 / REQ-014, ADR-083).
- Two guards against writing another package's private singleton slot: ruff `TID251` banned-api
  entries for the five private slots (`TID251` added to `[tool.ruff.lint] select`, without which the
  table is inert) and the source-scanning architecture test
  `tests/unit/architecture/test_singleton_slots.py`, which also reads the code strings handed to
  `subprocess` (T-007 / T-008, REQ-013, ADR-084).
- The new wiring requirement in each affected feature spec: `settings.md` v5 REQ-026,
  `event-bus.md` v2 REQ-008, `user-roles-permissions.md` v2 REQ-030, `search.md` v4 REQ-024,
  `session-management.md` v2 REQ-023.
- `AGENTS.md` sections `## Using the Permissions Feature` and `## Using the Session Management
  Feature` (Q-30), an "Install the shared default" bullet in each of the five features' "Using the …"
  section (REQ-015), and a `## Using the Feature Singletons (install / reset)` section describing the
  trio, the slot ban and the test seam (Phase 6 review).

### Changed

- `src/main.py` installs the registry it wires through `set_settings_registry()` and reads the shared
  instance back through `get_settings_registry()` at its six `register_*_settings` calls and its four
  service-construction sites, instead of writing the private slot and passing a local handle
  (T-006, REQ-011 / AC-016).
- `get_permission_service()` is now traced with `@logged(slow_threshold_ms=5)` and carries a
  `module function` row in the `docs/specs/logging-coverage.md` §3.1 inventory (v4, Q-31 = Option A);
  `reset_permission_service()` stays out of scope and remains a follow-up candidate.
- `docs/specs/structure-map.md` NFR-002 (v3): the `STRUCTURE.md` line budget raised 2 000 → 2 200.
  This change's own new test packages and traced install operations grew the committed map to 2 004
  lines (`make_map --check` exit 0); the content policy is unchanged and the REQ-017 per-class field
  cap stays the safety valve.
- `docs/specs/structlog-logging.md` v2: the REQ-005 per-file statement counts and AC-009's total
  refreshed 39 → 42 for the five new one-off replace `WARNING`s, with the pinned counts in
  `tests/acceptance/logging_coverage/test_statements_via_feature.py` raised to match.

### Fixed

- Concurrent first reads of four of the five feature singletons could construct two instances and
  silently lose one. Install, lazy create and reset are now mutually exclusive under one
  module-level lock per owning module (REQ-006); the settings slot lock is an `RLock` because its
  guarded lazy create re-enters the guard through the event bus (finding F-57).

### Removed

- The 12 writes to another package's private singleton slot — one in `src/main.py`, eleven in test
  helpers and in code strings handed to `subprocess` — each migrated to the owning feature's public
  install operation with the same capture-install-restore semantics and no test weakened (REQ-012).

## [1.1.1] - 2026-10-10

### Added

- Ruff now gates docstrings (`D` rules, Google style) over `src/`, and every missing or
  malformed docstring in the backend packages was added or fixed (PR #76).
- `LICENSE` (MIT, `Copyright (c) 2026 jackthenet`), `SECURITY.md` (reporting channel,
  supported versions, response, template scope) and this `CHANGELOG.md`, backfilled over the
  14 releases so far; `pyproject.toml` gained `license` and `authors` metadata
  (`security-changelog-license`).
- The changelog-entry rule: every change adds an entry under `## [Unreleased]`, and a version
  bump moves those entries into a dated release section (`AGENTS.md` Phase 6 +
  `## Versioning`, and the `implement`, `verify` and `review` skills).

### Fixed

- The structure-map generator no longer drops a parameter default whose unparsed text exceeds 20
  characters: it abbreviates that default to the `…` placeholder in the parameter's own slot, so
  `STRUCTURE.md` signature lines no longer shift an over-long default onto the following parameter
  or render a defaulted parameter as required. Corrected renderings: `AuthService.__init__`,
  `build_auth_service`, `build_memory_auth_service`, `simple_template` (`map-default-drop-shift`;
  rule amended in `docs/specs/structure-map.md` v2 — REQ-014/AC-014 amended, INV-007 and EDGE-017
  added).

## [1.1.0] - 2026-10-09

### Added

- `scripts/make_map.py`: a stdlib-only generator for `STRUCTURE.md`, the committed map of
  the repository (directory tree with per-module line counts), with `--check` mode for
  byte-exact staleness and pinned exit codes (structure-map T-001…T-007, delivered by
  PR #75; specified in 1.0.0).
- The `code-structure-map` skill and a check-only `structure-map` pre-commit hook, so the
  committed map stays current with the tree (structure-map T-006).
- `scripts/` joined the mypy type gate (structure-map T-001, AC-025).

### Changed

- The structlog-logging change reached `main` through its delivery merge (PR #74); its
  implementation is credited under 1.0.0.

## [1.0.0] - 2026-10-07

### Added

- The `structure-map` specification (PR #69) — the map feature itself shipped in 1.1.0.
- Architecture tests for the feature-boundary and architecture rules (PR #65).
- A backlog value-triage gate in the workflow: every TODO is scored 1–5 with an
  implement / merge / drop decision recorded before its branch is created (PR #70).
- The refreshed `README.md` front page with CI badges backed only by workflows that exist
  (PR #66).

### Changed

- **Logging backend: `loguru` replaced by `structlog` over stdlib handlers**
  (crosscut `structlog-logging`, PRs #67, #74). `setup_logger()` owns exactly two managed
  sinks, `@logged` / `@logged_class` trace functions and classes, and every feature's log
  statements were migrated to `get_logger()`; `loguru` left the dependency set.
- `pyproject.toml` tooling gaps closed (PR #68): `mypy disallow_untyped_defs` enabled and
  the missing annotations added, the complexipy complexity gate added to CI, ruff `DTZ`
  selected, `py-webauthn` declared, and the `docs` tooling moved to its own dependency
  group.
- The 1.0.0 milestone: the template's feature set (logging, settings, event bus, mail,
  user management, authentication, session management, file management, search, RBAC) and
  the Spec-TDD workflow around it are considered stable.

### Fixed

- `session_lookup` was not wired in the composition root (PR #63).
- The queue listener stopped draining when a sink raised, which hung the full test suite
  (`structlog-logging` T-002).

## [0.6.1] - 2026-10-04

### Added

- The `python-best-practices` skill is tracked in the repository (8 files).

### Changed

- The search feature reached `main` through its delivery merge (PR #54); its implementation
  is credited under 0.6.0.
- The Spec-TDD workflow was reworked around Phase P (PREPARE): front-loaded human
  interaction, per-change question files, and synchronous step subagents
  (`workflow-optimization` PR #59, `prepared-workflow` PR #61).
- Repository hygiene pass (PR #60).

### Removed

- The unused `spec-tdd` workflow driver (PR #62).

## [0.6.0] - 2026-10-02

### Added

- The search feature (`src/backend/search/`): a central cross-feature search abstraction —
  `SearchService`, registered per-feature sources, free-text query, filter/sort/pagination,
  per-source timeout, and permission enforcement (search T-001…T-008).
- Search sources exposed by three features: `build_user_source`, `build_file_source`,
  `build_session_source`, wired into the composition root.

### Fixed

- The search startup wiring was missing from `src/main.py` (S6.1 finding F-1).
- A deprecated `sqlite3` datetime adapter in the permissions migration.
- Bandit false positives in `get_search_service` and in feature action descriptions (PR #58).

## [0.5.1] - 2026-10-02

### Added

- The `search` CROSS-CUTTING specification (PR #53); the feature itself shipped in 0.6.0.
- Dependabot update groups delivered their first grouped bumps — `lint-and-types`,
  `test-tooling`, `runtime-core` (PRs #55–#57).

### Changed

- CI and the test suite were made deterministic (`main-ci-green`; its delivery merge, PR #58,
  landed in 0.6.0): shared event-bus and settings/logging singleton state is no longer
  leaked between tests, and Hypothesis deadlines are measured rather than guessed.
- The `dependency-review` job now runs on pull-request events only, where a base/head pair
  exists.

### Fixed

- Settings YAML persistence did not round-trip `U+0085` (NEL) values.
- Logging reconfigure removed unmanaged sinks, racing with test sinks on CI.

## [0.5.0] - 2026-09-24

### Added

- Role-based access control (`user-roles-permissions`, crosscut, T-001…T-014): a shared
  `PermissionService`, a permission-key catalog, the `@requires_permission` decorator, and
  enforcement wired across the six feature services (user management, authentication,
  settings, mail, file management, session management) with a trailing `principal`
  parameter on their public methods.

### Changed

- The `user-roles-permissions` specification and the change's delivery merge landed in the
  next release (PRs #51, #52); the implementation is here.
- Workflow documentation and CI timing notes (PR #50).

### Fixed

- Three regressions surfaced by the RBAC wiring: a tracing test's `principal` parameter, two
  new public classes missing `@logged_class`, and a missing `None` check in `service.py`.

## [0.4.3] - 2026-09-21

### Added

- Development tooling wiring: the local quality gates made explicit in the workflow docs
  (PR #46).

### Changed

- The performance-budget contract tests are environment-aware, so a slow CI host no longer
  fails a budget that passes locally (PR #47).

### Fixed

- Bandit `B101` (assert) findings in the source scan — explicit `raise` instead of `assert`
  (its delivery merge, PR #49, landed in 0.5.0).
- The `anyio` CVE fix reached `main` through its delivery merge (PR #48); the dependency
  upgrade itself is credited under 0.4.2.

## [0.4.2] - 2026-09-21

### Added

- Dependabot package groups in `.github/dependabot.yml`, so updates arrive as grouped PRs.

### Changed

- Dependencies updated to current releases (`dependency-updates`, PR #45), plus Dependabot
  bumps of ruff, pydantic and hypothesis (PRs #41–#43).

### Fixed

- `anyio` raised to `>= 4.14.2` to resolve CVE-2026-63374 and CVE-2026-64847 (the
  `anyio-cve-fix` change; its delivery merge, PR #48, landed in 0.4.3).
- An infinite loop in the AC-045 observability assertion loop (`hanging-observability-test`;
  its delivery merge, PR #44, landed here, the fix in 0.4.1).

## [0.4.1] - 2026-09-20

### Changed

- The session-management change reached `main` through its delivery merges (PRs #38, #39);
  its implementation is credited under 0.4.0.
- The settings / event-bus singleton order-dependency leak fixed at the source with a
  restore-on-teardown fixture pattern (`dependency-updates`, PR #40).

### Fixed

- The hanging observability test: the AC-045 assertion loop no longer spins forever
  (`hanging-observability-test`, RED → GREEN on the branch).

## [0.4.0] - 2026-09-19

### Added

- The session-management feature (`src/backend/sessionmanagement/`, T-001…T-009):
  `SessionService.list_sessions`, revocation operations (`revoke_session`,
  `logout_all_sessions`, `logout_other_sessions`, `revoke_all_sessions`), batch-bounded
  `cleanup_expired`, per-user session caps, user-lifecycle revocation, device identification
  at login, feature-owned settings, and the `get_session_service` singleton.
- Tooling hardening for the local quality gates (`tooling-hardening`, PR #28).

### Changed

- Workflow documentation reworked for subagent ergonomics and the after-workflow optimization
  (PRs #26, #27).
- The `settings-test-isolation` fix reached `main` through its delivery merge (PR #37); the
  fix itself is credited under 0.3.1.
- Dependabot bumps: `actions/checkout`, `actions/setup-python`, `astral-sh/setup-uv`,
  `pytest`, `ruff`, `orjson`, `pre-commit`, `complexipy` (PRs #29–#36).

## [0.3.1] - 2026-09-15

### Added

- The file-management specification (PR #24) and the first file-management implementation
  (PR #25): `FileService`, the SQLite file repository, and the storage backends.

### Fixed

- Settings test registries now use an isolated value repository, removing cross-test
  contamination (`settings-test-isolation`, ISSUE triage → reproduction test → fix).
- `uv.lock` was left out of sync by the 0.3.0 bump (missed by PR #25).

## [0.3.0] - 2026-09-14

### Added

- The mail service feature (`src/backend/mail/`, PRs #22, #23): `MailService.send_email` with
  `{{variable}}` template rendering, the password-reset and email-verification templates,
  feature-owned SMTP settings, an `smtplib`-backed transport behind an ABC, and `EmailSent` /
  `EmailFailed` events.

## [0.2.0] - 2026-09-12

### Added

- The logging feature (`src/core/logging/` at the time, PRs #1, #2): `setup_logger()` with a
  console and a rotating file sink, `@logged` / `@logged_class` tracing, and feature-owned
  settings.
- The event bus feature (`src/backend/eventbus/`, PRs #3, #4): `get_event_bus()`,
  non-blocking `publish`, `subscribe` by `isinstance`, per-handler error isolation.
- The user-management feature (`src/backend/usermanagement/`, PRs #5, #8): `UserManager`
  with argon2id password hashing, the last-admin guard, SQLite storage, and mutation events.
- The settings feature (`src/backend/settings/`, PRs #6, #7): `SettingsRegistry` with seven
  setting kinds, validated writes, YAML value persistence, templates, and `SettingChanged`
  events.
- The authentication feature (`src/backend/authentication/`, PRs #9–#11): login, server-side
  sessions, password reset, passkeys (WebAuthn), and brute-force lockout.
- Full test coverage for the logging and settings features (`logging-coverage` PRs #12, #14;
  `settings-coverage` PRs #15, #16) — acceptance, property, contract, unit and integration
  suites derived from their specifications.
- `bump-my-version` configuration and the Phase 6 version-bump step (PR #17).

### Changed

- The project became a template: the `novel-writer` leftovers were pruned and the
  distribution renamed to `python-template`, and feature code moved from `src/core/` to
  `src/backend/` — the flat feature-package layout the template uses today.
- The Spec-TDD workflow protocol became change-type routed, with the subagent-per-phase
  execution protocol and the todo-tracking discipline (PRs #13, #19, #20, #21).
- Performance budgets amended: settings mutating operations and logging setup under 50 ms,
  with the contract tests re-derived (PR #19).

### Fixed

- `model_fields` accessed on the class rather than the instance in user-management (a
  Pydantic deprecation).
- Unused module-level imports in the settings test helpers (PR #18).

## [0.1.0] - 2026-08-16

### Added

- The initial scaffold: `src/main.py` and a `src/core/logging/` package (`setup_logger` plus
  a call-tracing decorator over `loguru`), `pyproject.toml` managed by `uv`, a
  `.pre-commit-config.yaml` with ruff check/format, complexipy and the file-hygiene hooks,
  the `lint` CI workflow, VS Code launch/settings, and the `.github/` agent prompt and
  ruff-post-edit hook files.
