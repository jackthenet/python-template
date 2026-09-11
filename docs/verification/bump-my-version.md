# Verification — Bump-My-Version Integration

**Type:** DOCS/CHORE
**Branch:** `chore/bump-my-version`

---

## Phase 1 — Scope (no behavior delta)

**Date:** 2026-09-11

### Changes

1. `pyproject.toml`
   - Keep the existing `[project] version = "0.1.0"` as the single source of truth for the version (it already exists; the "0.0.0" in the request was a format example, not a reset — noted for review).
   - Add a `[tool.bumpversion]` table for the `bump-my-version` tool:
     - `current_version = "0.1.0"`, semver `parse`/`serialize` (major.minor.patch).
     - `[[tool.bumpversion.files]]` → `pyproject.toml`, with an explicit `search = 'version = "{current_version}"'` / `replace = 'version = "{new_version}"'` so only the PEP 621 version line is rewritten (never a dependency string).
     - `commit = true` (templated bump commit), `tag = false` (no tags on change branches; version tags are created on `main` at release time, outside the workflow).
2. `AGENTS.md`
   - "Tooling & Execution Environment": add `bump-my-version` (`uv tool install bump-my-version`; config in `pyproject.toml` under `[tool.bumpversion]`).
   - New "Versioning" section: version location, bump mapping per change type, when/where the bump runs (Phase 6, before the PR), tagging policy.
   - Phase 6 list: add the version-bump step before "open a PR".
3. `.agents/skills/review/SKILL.md`
   - MUST list: bump the version per change type before opening the PR (no bump for REFACTOR/DOCS-CHORE).
4. `docs/verification/bump-my-version.md` (this file): scope + verification evidence.

### Bump mapping (to be documented in AGENTS.md)

| Change type | Bump level |
|---|---|
| ISSUE | `patch` |
| FEATURE | `minor` |
| CROSS-CUTTING | `minor` (`major` if breaking) |
| REFACTOR / DOCS-CHORE | none |

### No-behavior-delta confirmation

- No `src/` files, no `tests/` files, no API or dependency changes.
- `[project] version` already exists; adding the `[tool.bumpversion]` table is tool configuration only — ignored by the build backend, uv, ruff, mypy, and pytest.
- `AGENTS.md` and the review skill are workflow documentation.
- The explicit `search`/`replace` patterns guarantee the bump only rewrites the `version = "..."` line.
