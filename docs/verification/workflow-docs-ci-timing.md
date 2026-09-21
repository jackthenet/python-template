# Verification: workflow-docs-ci-timing

**Type:** DOCS/CHORE (no-behavior)

**Phase 1 (Specify, DOCS/CHORE path):** exact non-behavior scope. This change bundles three small no-behavior changes. No spec, no PR approval gate (DOCS/CHORE).

---

## Scoped changes

### Change A — S4.4 Refactor: skip `green_command` re-run when zero file changes

- **File:** `.agents/skills/implement/SKILL.md`
- **Where:**
  - the `### S4.4 Refactor (keep GREEN)` section — its **Done-criteria** bullet (line 71);
  - the `### 4. Refactor (improve structure, keep GREEN) — FEATURE/CROSS-CUTTING` process step — the numbered "8. **Refactor:**" item (line 101).
- **Intended content:** add a rule stating that if S4.4 made **zero file changes** (nothing to refactor), the `green_command` re-run is **skipped** — GREEN established in S4.2/S4.3 still holds, so re-running is unnecessary.
- **Rationale:** the current wording ("Re-run `green_command` and `uv run ruff check <changed-paths>` after every meaningful refactoring step") triggers a full `green_command` re-run even when the refactor step edited nothing.

### Change B — per-worktree cache line

- **File:** `AGENTS.md`
- **Where:** the **Git Worktrees** section, "Rules" bullet list — immediately after the bullet "Each worktree has its own `uv` environment; run `uv run <command>` inside the worktree (the global uv cache is shared, so no extra setup is needed)." (line 78).
- **Intended content:** add one bullet/line confirming that `.ruff_cache` and `.mypy_cache` are **per-worktree by default** (each is created in the worktree's CWD and is gitignored), so the cheap-re-run benefit does **not** carry across worktrees — a new change starts with a cold cache. Note that to share them across worktrees you point both tools' cache dirs at a common location outside the worktrees (ruff: `RUFF_CACHE_DIR`; mypy: `MYPY_CACHE_DIR`).
- **Verified facts:**
  - `pyproject.toml` sets no shared cache dir.
  - `.gitignore` lists both `.mypy_cache/` (line 158) and `.ruff_cache/` (line 192).
  - mypy's `--cache-dir` defaults to `.mypy_cache` and honors `MYPY_CACHE_DIR`.
  - ruff's cache defaults to `.ruff_cache` and honors `RUFF_CACHE_DIR`.

### Change C — test `wait_for_file_content` timeout 5s → 15s (CI robustness)

- **Files + exact edits:**
  - `tests/logging_test_helpers.py` line 40: `def wait_for_file_content(path: Path, predicate: Callable[[str], bool], timeout: float = 5.0) -> bool:` → change the default `5.0` to `15.0`.
  - `tests/acceptance/logging/test_logging.py` line 37: `timeout=5` → `timeout=15`.
  - `tests/contract/logging/test_logging_contracts.py` line 100: `timeout=5` → `timeout=15`.
  - `tests/integration/logging/test_logging_integration.py` lines 33, 34, 35: `timeout=5` → `timeout=15` (3 occurrences).
- **Intended content / rationale:** raise the file-content wait timeout for CI robustness — the enqueued file write (loguru `enqueue=True`) takes >5s on slow CI hardware, so the logged line never reaches the file within the 5s window. **No behavioral assertion changes**: each test still asserts the specific line reaches the file; only the allowed time increases. `enqueue=True` is unchanged (spec AC-001 requires it).

---

## No-behavior-delta confirmation

Per change:

- **Change A:** documentation (workflow skill) only — no product code, no test, no configuration touched. **No behavior delta.**
- **Change B:** documentation (AGENTS.md) only — no product code, no test, no configuration touched. **No behavior delta.**
- **Change C:** test-timing (CI robustness) only — product behavior unchanged; no assertion weakened (the specific line still must reach the file; only the allowed time increases from 5s to 15s). **No behavior delta.**

**Overall:** this change does not alter externally observable (product) behavior. It consists of two documentation edits (A, B) and one test-timing adjustment (C). No product source file is modified; no behavioral assertion is added, removed, or weakened.
