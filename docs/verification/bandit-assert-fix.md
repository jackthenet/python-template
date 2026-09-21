# Triage Record: bandit-assert-fix

- **Type:** ISSUE (light tier)
- **Change name:** `bandit-assert-fix`
- **Branch:** `issue/bandit-assert-fix` (based on `origin/main` @ `10066d5`)
- **Date:** 2026-07-22

## Classification Record

**Why ISSUE:** The CI `security` job's bandit step is failing — `uv run bandit -r src/` exits 1 because bandit flags an `assert` statement (B101:assert_used). This is a deviation from the project's own CI contract (the security job requires bandit to pass over `src/`); it is a defect, not new behavior. The fix introduces no new behavior: it replaces the `assert` with an explicit check that raises the same exception type (`AssertionError`), preserving behavior exactly.

**Why light tier:**
- Single feature (`backend.sessionmanagement`).
- The fix touches **1 file** excluding tests (`src/backend/sessionmanagement/service.py`).
- No new dependency, no new public interface, no cross-feature change.
- The existing test suite already covers the affected area (the sessionmanagement acceptance test suite; see Covering Tests).

## Affected Gate

The `security` job in `.github/workflows/quality.yml` — step **"Run bandit"**:

```yaml
- name: Run bandit
  run: uv run bandit -r src/
```

The step is currently failing (exit code 1), which fails the security job.

## Defect Confirmation

- **Observed behavior:** `uv run bandit -r src/` exits **1**, reporting exactly 1 issue: `B101:assert_used` at `src/backend/sessionmanagement/service.py:180:8` (Severity Low, Confidence High, CWE-703).
- **Required behavior:** `uv run bandit -r src/` exits **0** — no flagged issues in `src/` (the CI security job's contract).
- **Deviation confirmed:** the bandit run reports 1 issue where 0 are permitted.

## Affected Requirements (existing approved spec)

Spec: `docs/specs/session-management.md` (approved, merged on `main`).

The assert sits in `SessionService.list_sessions` (spec **REQ-001**: "a single `list_sessions` method serves both self-service (token) and admin (user_id) listing"; admin path **AC-002**, token path **AC-001**, argument validation **AC-003**). The fix MUST preserve REQ-001 behavior exactly — no observable behavior change. The defect itself is against the CI contract, not against REQ-001 behavior.

## Root Cause

The statement at `src/backend/sessionmanagement/service.py:180` is:

```python
assert user_id is not None  # validated above (exactly one of token/user_id)
```

The assert is a **pure type-narrowing** check, not a behavioral guard:
- Line 179 is `user_id = session.user_id` (inside the `if token is not None:` block); `Session.user_id` is non-nullable (`UUID = SField(index=True)` in `src/backend/authentication/models.py`), and the admin path guarantees `user_id` non-None (the method validates "exactly one of token or user_id" at the top, raising `ValueError` otherwise). The value is therefore guaranteed non-None by logic.
- The assert exists only to tell mypy that `user_id` is non-`None` (narrowing `UUID | None` → `UUID`).
- Bandit flags `assert` statements (B101) because asserts are stripped when compiling to optimized bytecode, so any logic depending on them silently disappears.

## Reproduction Plan (RED)

1. In the change worktree, run the CI security job's bandit command:

   ```bash
   uv run bandit -r src/
   ```

2. **RED:** the command exits **1** and reports exactly 1 issue: `B101:assert_used` at `src/backend/sessionmanagement/service.py:180:8`.
3. Record RED evidence in this file (Phase 3, S3.2).

## Fix Scope (Phase 4)

Replace the `assert` at `src/backend/sessionmanagement/service.py:180` with an explicit check that raises the same exception type, preserving behavior exactly:

```python
if user_id is None:
    raise AssertionError("user_id must not be None")
```

- **Behavior-preserving:** an `assert X` compiles to `if not X: raise AssertionError`; the explicit form raises the same `AssertionError` in the same (unreachable) case.
- **mypy:** narrows `user_id` to `UUID` for the code below, same as the assert.
- **bandit:** clean — no `assert` statement remains.

**Files to change:** `src/backend/sessionmanagement/service.py` (1 file only).

## Covering Tests

- Acceptance test directory: `tests/acceptance/sessionmanagement/` (the assert is in `list_sessions`, covered by `tests/acceptance/sessionmanagement/test_list_sessions.py` for REQ-001..REQ-007 of `docs/specs/session-management.md`).
- Phase 5 (light tier): run the covering tests named above plus the affected feature's test directory (`uv run pytest tests/acceptance/sessionmanagement/ -v`), plus lint and type checks. The full regression suite runs as the Phase 6 pre-merge gate.

## Light-Tier Qualification

All light-tier criteria hold:

| Criterion | Holds | Evidence |
|---|---|---|
| Single feature | ✅ | `backend.sessionmanagement` only |
| Fix touches ≤ 3 files (excluding tests) | ✅ | 1 file: `src/backend/sessionmanagement/service.py` |
| No new dependency | ✅ | none added |
| No new public interface | ✅ | no signature/API change |
| No cross-feature change | ✅ | confined to `sessionmanagement/service.py` |
| Existing test suite covers the affected area | ✅ | `tests/acceptance/sessionmanagement/` (named in Covering Tests) |

## Phase 3 (RED)

- **Date:** 2026-09-21
- **Step:** S3 (Phase 3 — confirm RED; reproduction "test" is the CI security job's bandit command itself)

### Command run

```bash
uv run bandit -r src/
```

(Worktree: `python-template_kopie-worktrees/issue/bandit-assert-fix`, branch `issue/bandit-assert-fix` — the exact command of the `security` job's "Run bandit" step in `.github/workflows/quality.yml`.)

### Result

- **Exit code:** `1`
- **Issues reported:** exactly **1** — `B101:assert_used` at `src/backend/sessionmanagement/service.py:180:8`
  - Severity: **Low**, Confidence: **High**, CWE: **CWE-703** (total issues: Low 1 / Medium 0 / High 0)
  - Flagged statement: `assert user_id is not None  # validated above (exactly one of token/user_id)` (line 180)
- **Scanned:** 5670 lines of code, 0 skipped, 0 potential issues skipped — no other findings.

### RED confirmation

This is **RED**: the current (defective) code fails the bandit gate. The CI security job requires `uv run bandit -r src/` to exit `0`; the observed exit code is `1` with exactly the 1 issue named in the triage's Reproduction Plan (B101:assert_used at `service.py:180:8`, Severity Low, Confidence High, CWE-703). The failure mode is a bandit finding (not an environment/invocation error) — the command ran to completion and reported the issue at the expected location.

**Next:** Phase 4 (S4) — minimal fix (replace the assert with an explicit `AssertionError`-raising check) → GREEN (bandit exits `0`).

## Phase 4 (GREEN)

- **Date:** 2026-09-21
- **Step:** S4 (Phase 4 — minimal fix, GREEN)

### The change (before/after)

File: `src/backend/sessionmanagement/service.py` (line 180, in `SessionService.list_sessions`)

Before:

```python
        assert user_id is not None  # validated above (exactly one of token/user_id)
```

After:

```python
        if user_id is None:
            raise AssertionError("user_id must not be None")  # validated above (exactly one of token/user_id)
```

### Gate results

| Gate | Command | Result |
|---|---|---|
| bandit (GREEN) | `uv run bandit -r src/` | **exit 0** — "No issues identified." (5671 lines scanned, 0 skipped, 0 potential issues skipped; severity Low 0 / Medium 0 / High 0) |
| mypy | `uv run mypy src/` | **clean** — "Success: no issues found in 56 source files" (exit 0) |
| ruff | `uv run ruff check src/backend/sessionmanagement/service.py` | **clean** — "All checks passed!" (exit 0) |
| behavior | `uv run pytest tests/acceptance/sessionmanagement/ -v` | **47 passed** in 8.05s (exit 0) — no new failures |

### Behavior-preservation confirmation

- **Same condition, same exception type:** an `assert X` statement compiles to `if not X: raise AssertionError`. The replacement is exactly `if user_id is None: raise AssertionError(...)` — the same check (`user_id is None`), the same exception type (`AssertionError`), and it is active in all compilation modes (not stripped in optimized mode, which is what bandit B101 objects to).
- **Unreachable branch, unchanged in practice:** `user_id` is guaranteed non-`None` at this point — the token path sets `user_id = session.user_id` where `Session.user_id` is non-nullable `UUID`, and the admin path guarantees non-`None` via the "exactly one of token or user_id" validation at the top of the method (which raises `ValueError` otherwise). The `if user_id is None` branch exists only to narrow the type for mypy and to satisfy bandit.
- **mypy narrowing intact:** mypy understands the `if x is None: raise` pattern and narrows `user_id` to `UUID` for the rest of the method — confirmed by the clean mypy run (56 source files, no issues), so the remainder of `list_sessions` (which uses `user_id` as `UUID`) type-checks unchanged.
- **bandit clean:** no `assert` statement remains in `src/` (B101 flags `assert` statements only, not `if ... raise`); the full bandit run over `src/` reports no issues.
- **Behavior preserved:** the sessionmanagement acceptance suite (covering `list_sessions` per REQ-001..REQ-007 of `docs/specs/session-management.md`) passes 47/47 — no observable behavior change.

**Next:** Phase 5 (S5) — verify, light gate set (targeted + smoke: covering tests + affected feature test directory + lint/types; full regression suite as the Phase 6 pre-merge gate).

## Phase 5 (Verify)

- **Date:** 2026-09-21
- **Step:** S5 (Phase 5 — verify, light gate set; light-tier ISSUE)
- **Base commit:** `3ca3b45` (GREEN)

### Gate set (light tier: targeted + smoke, NOT the full regression suite)

| # | Gate | Command | Result |
|---|------|---------|--------|
| 1 | Reproduction test (GREEN) | `uv run bandit -r src/` | **exit 0** — "No issues identified." (5671 lines scanned, 0 skipped, 0 potential issues skipped; severity Low 0 / Medium 0 / High 0) |
| 2 | Covering tests (named in triage) | `uv run pytest tests/acceptance/sessionmanagement/ -v` | **47 passed** in 7.69s (exit 0) — no new failures |
| 3 | Affected feature test directories | `uv run pytest tests/contract/sessionmanagement/ tests/integration/sessionmanagement/ tests/property/sessionmanagement/ tests/unit/sessionmanagement/ -v` | **21 passed** in 39.91s (exit 0) — no new failures |
| 4 | Lint (whole repo, matching CI) | `uv run ruff check .` | **clean** — "All checks passed!" (exit 0) |
| 5 | Type checks | `uv run mypy src/` | **clean** — "Success: no issues found in 56 source files" (exit 0) |

### Sessionmanagement test totals

- `tests/acceptance/sessionmanagement/`: 47 passed
- `tests/contract/sessionmanagement/` + `tests/integration/sessionmanagement/` + `tests/property/sessionmanagement/` + `tests/unit/sessionmanagement/`: 21 passed
- **Total: 68 passed, 0 failed** — no new failures.

### Light gate set confirmation

All light-tier Phase 5 gates pass:

- bandit exits **0** — the CI security job's contract is satisfied (the defect is fixed).
- The covering tests named in the triage record pass (47/47).
- All sessionmanagement test directories pass (68/68 total).
- Lint is clean on the whole repo (matching CI) — no new lint errors, and no pre-existing errors surfaced.
- Type checks are clean (56 source files) — no new type errors.

No new failures, no new lint/type errors. The change is verified at the light gate set.

### Full regression suite

The **full regression suite** (`uv run pytest tests/ -v`) is the **Phase 6 pre-merge gate** (S6.4, before the PR opens) per the light-tier ISSUE tier in `AGENTS.md`; it runs there and its result is recorded in the review report. It is intentionally not run in this light-tier Phase 5.

**Next:** Phase 6 (S6) — review, clean report + full regression pre-merge gate + PR.
