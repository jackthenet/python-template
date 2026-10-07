# TODO: codecov-coverage-badge

Backlog item for one planned change, created at **P.1 Frame** from this template and named `codecov-coverage-badge.md`. One file per change.

This is a **planning record, not normative**: like `docs/questions/`, it is committed directly to `main` (see "Phase P: PREPARE" in `AGENTS.md`). It carries no approval gate — the spec does.

- **Status:** DROPPED  <!-- PREPARING | QUESTIONS-ANSWERED | READY | IN-WORKFLOW | WAITING | MERGED | DROPPED -->
  <!-- dropped 2026-10-07 at P.3: Q-1 answered "drop — no badge". Reason: the badge buys visibility, not assurance — the assurance already exists (`fail_under = 92`, `pyproject.toml:105`, enforced at `quality.yml:59`); for a TEMPLATE repo every added third-party integration is a configuration-or-deletion task for every downstream user. The remaining 26 P.2 questions became moot and were never asked. -->
- **Disposition:** **DROPPED** — user decision, 2026-10-07 (P.3 round 1, Q-1). The 3/5 value triage stands; the deciding argument was the template-audience cost. No external service, no badge, no CI step. `update-readme` Q-3's option (d) — "add Codecov, as a separate change" — is hereby closed as declined, not deferred.
- **Change type:** DOCS/CHORE  <!-- CI + config only; no externally observable product behavior changes -->
- **Created:** 2026-10-04
- **Question file:** `docs/questions/codecov-coverage-badge.md`
- **Spec:** n/a  <!-- DOCS/CHORE: no spec -->
- **Worktree:** <created at P.4> `../python-template_kopie-worktrees/chore/codecov-coverage-badge`
- **Depends on:** none
- **Related specs:** none (no `docs/specs/` file is touched)

## Goal (one line)
Upload the coverage report CI already produces to Codecov and put a real coverage badge in `README.md`, so coverage is trended over time instead of only gating on `fail_under`.

## Why
Raised and decided while answering `update-readme` **Q-3** on 2026-10-04: the README cannot carry an honest coverage badge today because nothing publishes a measured value — `[tool.coverage.report] fail_under` only fails the `coverage` job in `.github/workflows/quality.yml`, and the number is discarded after the run. `update-readme` deliberately ships **no** coverage badge (its skill rule: "only badges backed by something real"), so the badge needs this change to exist first.

## Value triage
| ID | TODO | Score | Recommendation | Reason |
|---|---|---|---|---|
| V-1 | codecov-coverage-badge | 3 | implement | Real, visible value (coverage trend + a badge that reports a measurement, not a gate), but it adds an external service and a CI step; the local gate already prevents coverage regressions, so the gain is historical visibility rather than a new guarantee. |

Existing-functionality check: no overlap — `quality.yml` runs `pytest --cov` and enforces `fail_under`, and `docs/todo/update-readme.md` explicitly excludes a coverage service; nothing else publishes a measured value.

## In scope
- The upload step in the `coverage` job of `.github/workflows/quality.yml` (the `codecov/codecov-action` action, pinned), plus whatever report format it needs (e.g. `--cov-report=xml` producing `coverage.xml`) and its artifact handling.
- The Codecov badge line in `README.md` — **only** once the upload is proven to work on `main`.
- Recording the dependency/service decision (why Codecov, what it costs, what happens if the service is unreachable) in `docs/verification/codecov-coverage-badge.md`; `AGENTS.md` requires dependency decisions to be traceable.

## Out of scope
- Changing `fail_under`, the coverage threshold, or what the `coverage` job fails on — the gate stays exactly as it is.
- Any other badge or README section — that is `update-readme` (WAITING, lands independently).
- Adding `LICENSE` / `CONTRIBUTING.md` / a PyPI publish workflow (the other `update-readme` follow-ups).
- Any `src/` or `tests/` change.

## Affected features
None — `.github/workflows/quality.yml`, `README.md`, and one verification record. No `src/backend/` or `src/frontend/` path is touched.

## Constraints and risks
- **New external service.** Codecov is a third-party SaaS: it needs a repo connection, and a private repository additionally needs a `CODECOV_TOKEN` repository secret. The repo's own rule ("dependency decisions must be traceable", `AGENTS.md`) means the choice must be written down, not just added.
- **A badge that lies is worse than no badge.** The badge must not be merged before the first successful upload on `main`, or `README.md` shows a value nothing produced.
- **CI must stay green.** The upload step must not fail the `Quality` run when Codecov is down (an `if:`/`continue-on-error:` decision — P.2 question).
- `update-readme` also edits `README.md`; the two changes touch different lines (badge row vs the coverage badge line), so they do not collide, but whichever lands second re-reads the badge row.

## Acceptance signal (plain language)
After a push to `main`, Codecov shows a coverage number for the run, and `README.md` displays a coverage badge whose value matches what Codecov reports; the `coverage` job's pass/fail behaviour is unchanged.

## Prep log
| Step | Date | Result |
|---|---|---|
| P.1 Frame | 2026-10-04 | TODO + question file created on `main`; type **DOCS/CHORE** (CI/config only, no behavior delta); todo set for this change; **value triage 3/5, implement** — raised by the user's `update-readme` Q-3 = (d) answer on 2026-10-04 |
| P.2 Interrogate (29 questions) | 2026-10-05 | **BLOCKED-USER** — 29 questions (**Q-1 … Q-29**) recorded in `docs/questions/codecov-coverage-badge.md`, one batch, most-blocking first (Q-1 go/no-go on the service + the account-side activation only the human can do; Q-2/Q-3 the badge-honesty gate). 13 interrogation points closed from repository evidence without spending a question. Two P.1 premises corrected at P.2: `update-readme` is **MERGED** (PR #66 as `b7b0ee0`), so the badge row already exists at `README.md:3-9` and the "lands independently" note above is stale; and the repo is **public**, so the private-repo token framing does not apply (Q-4 still asks about authentication). Branch protection on `main` is not readable unauthenticated — Q-8 asks instead of asserting |
| P.3 Answer (<n> answered) | | |
| P.4 Draft scope + create branch/worktree | | |
| P.5 Self-consistency | | n/a (DOCS/CHORE) |
