# ADR-087: the cognitive-complexity gate covers `scripts/`; the ceiling stays at 15

## Status
Accepted — **supersedes `ADR-086-scripts-type-checked-tree.md`** in exactly one respect: its gate-map row
for `complexipy` (`:18`, "Covers `scripts/`? — no") and the sentence of its Decision bullet that keeps
complexipy at `paths = ["src", "tests"]` (`:47-50`). Every other ADR-086 decision — `scripts/` as a
type-checked tree, the stdlib-only generator, coverage/bandit/`ty` scopes, the `fail_under = 92` floor —
stands unchanged.

ADR-086 is **not edited**. A decision record is superseded, never rewritten; the supersession is recorded
here, in the superseding record. Precedent: ADR-082 supersedes ADR-002 and states that the ADRs whose
wording it absorbs are "deliberately **not** edited … only their naming … is stale".

## Context
ADR-086 made `scripts/` a type-checked tree and, in the same table, froze the rest of the gate map —
coverage, complexipy, bandit, `ty`. That freeze was **scope discipline for that change**, not a judgment
that repository tooling should go unmeasured: its own Consequences section calls the resulting asymmetry
"`scripts/` is type-checked but not coverage-, complexity- or bandit-scanned … now explicit so it is a
decision someone can revisit, not an accident someone 'fixes' by pointing every tool at `.`".

This is one of those revisits, and the measurement that prompted it is concrete (`complexipy-scripts`,
base `eddf94f`, 2026-10-11):

- `uv run complexipy scripts --max-complexity-allowed 15` → **exit 1**: **50 functions analysed, 4 over the
  ceiling** — `check_traceability.py::check` **17**, `check_traceability.py::matrix_rows` **19**,
  `validate_task_dag.py::check_acyclic` **22**, `verify_spec.py::main` **22**.
- Both forms of the gate were blind to them: `uv run complexipy` (config-driven) and the CI line
  `uv run complexipy src tests --max-complexity-allowed 15` each analysed 2 186 functions and exited **0**.
  The tool did not look at `scripts/` and find nothing — it never looked.
- The four offenders are in the code that **polices every other change's gates**
  (`check_traceability.py`, `validate_task_dag.py`, `verify_spec.py`), and two of them have **no
  behavioral tests**, so the only thing standing between a future edit and a broken spec gate was the
  readability of a 22-point function.
- `scripts/` is already inside three other static gates — `ruff check`/`format` (`.`), `deptry` (`.`), and
  since ADR-086 `mypy scripts/`. Complexity was the last of the four that did not see it.
- `docs/specs/structure-map.md` NFR-005 stated the same scope descriptively ("`scripts/` is not analyzed by
  complexipy"), so widening the gate makes an approved spec line false. It is amended in the same PR
  (spec **v4**, Spec Amendment Workflow) rather than left contradicted.

## Decision
- **The complexity gate's scope becomes `src`, `tests`, `scripts` — in both places the scope is written**
  (Q-05):
  - `pyproject.toml` `[tool.complexipy] paths = ["src", "tests", "scripts"]` — the source of truth for a
    local `uv run complexipy`;
  - `.github/workflows/quality.yml`, the `complexity` job:
    `uv run complexipy src tests scripts --max-complexity-allowed 15` — the positional args stay
    **explicit** (they override the config `paths`) so CI fails loudly on a bad config, which is exactly
    what that job's comment says the repetition is for.

  Widening only one of the two leaves the other blind: a CI-only change keeps every local run blind to
  `scripts/`, and a config-only change leaves CI's positional args overriding it and makes its comment
  false. `pyproject-tooling-gaps` was created to close that config-vs-CI drift; re-opening it here would
  undo that change.
- **The ceiling does not move: `max-complexity-allowed = 15`.** The four offenders were brought under it,
  not exempted from it, and the internal target was **≤ 12** (Q-13) — the maximum already demonstrated in
  `scripts/make_map.py` — so the widened gate has margin, not a squeaker. No per-file carve-out, no
  baseline, no snapshot: `pyproject-tooling-gaps` already rejected encoding debt, and this change follows
  the same precedent (fix the offenders, keep the ceiling).

  | Function | Before | After |
  |---|---|---|
  | `check_traceability.py::check` | **17** ✗ | **0** ✅ |
  | `check_traceability.py::matrix_rows` | **19** ✗ | **2** ✅ |
  | `validate_task_dag.py::check_acyclic` | **22** ✗ | **3** ✅ |
  | `verify_spec.py::main` | **22** ✗ | **3** ✅ |
  | whole of `scripts/` | 50 functions, **4 FAILED**, exit 1 | **67 functions, 0 FAILED**, max 12, exit **0** |
  | whole gate (`src` + `tests` + `scripts`) | 2 186 analysed (config/CI), exit 0 | **2 253 analysed**, exit **0** |

  The restructures are pure extractions under a **byte-identical stdout + exit-code contract** (Q-07): the
  three scripts' observable surface is argv, stdout and exit code, and the change's primary evidence is a
  golden-output byte comparison plus FAIL-path differential fixtures, not a regression run.
- **Everything else ADR-086 froze stays frozen** (Q-17): coverage (`source = ["src/backend",
  "src/frontend"]`, `fail_under = 92`), bandit (`-r src/`), `ty` (`root = ["./src"]`), and `migrations/` +
  `.github/hooks/ruff-post-edit.py` outside every gate. This decision widens **one** gate, and only to the
  tree ADR-086 already made first-class.
- **No pin, no version snapshot, no score ratchet** (Q-18): `complexipy>=8.0.1` stays a dependabot-managed
  dev-group dependency.
- **The witness is not touched** (Q-12): `tests/acceptance/test_structure_map.py::
  test_nfr_005_complexipy_threshold_holds` keeps pinning its own `_COMPLEXIPY_PATHS = ("src", "tests")` and
  keeps passing; it is neither weakened nor extended to `scripts/`.

## Consequences
- **Positive:** 67 `scripts/` functions are now gated, so a future over-complex function in the repository's
  own spec-police fails CI instead of landing unreviewed; local and CI runs of the gate agree (measured:
  the config-driven run and the CI form now produce identical reports, 2 253 functions); the four
  functions that the workflow depends on most are the smallest they have ever been; the spec line and the
  config now say the same thing.
- **Accepted drift risk (Q-18):** widening adds 67 functions whose scores depend on a tool dependabot
  updates, and this engine has already moved once — `pyproject-tooling-gaps` measured
  `test_inv_003_last_admin_invariant` scored **20 PASSED** by complexipy 5.1.0 and **38 FAILED** by 8.0.1,
  same code. Mitigation is the ≤ 12 target: a modest rescore cannot push a ≤ 12 function over 15. If a
  bump does redden `scripts/`, that is a tooling event and gets its own TODO — not a pin retrofitted here.
- **Near-misses deliberately left alone (Q-17):** `test_ac_008_document_shape` = 15,
  `_feature_logger_names` = 14, `test_inv_004_other_loggers_untouched` = 14,
  `test_concurrent_thread_safe` = 14, `SearchService::search` = 13, `SettingsRegistry::create_template` =
  13. They pass the gate today; pulling them in would be unrelated churn in other changes' files, and a
  function parked at 15 is a fact about that function's change, not about this one.
- **Enforcement asymmetry (accepted, Q-12):** the widened scope is enforced by the `complexity` job plus
  `[tool.complexipy] paths`, with **no** config-contract test asserting that `scripts/` stays in the gate.
  A test that re-reads the config would duplicate the gate it is meant to protect, and the change's type
  (DOCS/CHORE) forbids touching tests. The stale witness is recorded here so the next reader does not
  "fix" it by extending it without a decision.
- **Two places, one scope:** the gate scope is written twice (config + CI positional args) and can drift
  again. That duplication is deliberate — it is what makes a broken config fail loudly — and it is now
  stated in both the config and this record.
- `scripts/` is now lint-, dependency-, type- and complexity-gated. It is still not coverage- or
  bandit-scanned, and the local `ty` tool still does not see it: ADR-086's remaining asymmetry is
  untouched by this decision.

## Alternatives Considered
- **Leave `scripts/` out of the complexity gate** (ADR-086's row as written) — rejected: it left four
  functions at 17–22 in the untested code that enforces every other change's spec gates, and both forms of
  the gate exited 0 without ever looking at them.
- **Raise or parameterise the 15 ceiling, or add a per-file carve-out / complexipy snapshot baseline** —
  rejected (Q-13, Q-17): the point is to meet the existing ceiling, not to encode debt;
  `pyproject-tooling-gaps` fixed 10 offenders rather than raise the ceiling and rejected the snapshot.
- **Widen only the CI line** — rejected: `uv run complexipy` (the config-driven local run developers
  actually use) stays blind to `scripts/`.
- **Widen only `[tool.complexipy] paths`** — rejected: CI passes positional args, which override the config,
  so CI would stay blind and the job's "repeated here so CI fails loudly on a bad config" comment would be
  false.
- **Pin complexipy, or record a per-function score ratchet** — rejected (Q-18): the repo chose one engine
  (`>=8.0.1`) and rejected snapshots; a rescore event deserves its own TODO.
- **Extend `test_nfr_005_complexipy_threshold_holds` to `scripts/`** — rejected for this change (Q-12): the
  DOCS/CHORE type forbids test changes, and a config-contract witness would duplicate the CI gate.
- **Also bring `migrations/` and `.github/hooks/` under the gate** — rejected: alembic-generated revisions
  and a hook script are not this decision's tree; ADR-086 excluded them and nothing measured here argues
  otherwise.

## References
- `docs/decisions/ADR-086-scripts-type-checked-tree.md` — the superseded `complexipy` row (`:18`) and
  frozen-scope bullet (`:47-50`); **not edited**
- `docs/decisions/ADR-082-structlog-processor-layer-over-stdlib.md` — the supersession convention followed
  here (supersede in the new record, leave the old one intact)
- `docs/specs/structure-map.md` — NFR-005 (amended at **v4** in this PR), §15 Changelog
- `docs/verification/complexipy-scripts.md` — the scope record, the complexity baseline, the golden-output
  byte comparison and the Phase 4/5 evidence
- `pyproject.toml` `[tool.complexipy]`; `.github/workflows/quality.yml` — the `complexity` job
- `docs/todo/archive/pyproject-tooling-gaps.md` — the precedent: fix offenders, keep the ceiling, no
  snapshot; and the config-vs-CI duplication this decision preserves
- `docs/questions/complexipy-scripts.md` — Q-04 (amend NFR-005 **and** supersede), Q-05 (both places),
  Q-12 (no witness), Q-13 (≤ 12), Q-17 (non-goals), Q-18 (drift accepted)
