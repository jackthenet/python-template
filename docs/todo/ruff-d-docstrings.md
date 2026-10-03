# TODO: ruff-d-docstrings

Backlog item for one planned change, created at **P.1 Frame** from this template and named `ruff-d-docstrings.md`. One file per change.

This is a **planning record, not normative**: like `docs/questions/`, it is committed directly to `main` (see "Phase P: PREPARE" in `AGENTS.md`). It carries no approval gate — the spec does.

- **Status:** PREPARING  <!-- PREPARING | QUESTIONS-ANSWERED | READY | IN-WORKFLOW | WAITING | MERGED -->
- **Change type:** DOCS/CHORE  <!-- docstrings + ruff select only; no externally observable behavior delta. Escalates if a docstring reveals a behavior claim that is wrong (then ISSUE). -->
- **Created:** 2026-10-04
- **Question file:** `docs/questions/ruff-d-docstrings.md`
- **Spec:** n/a  <!-- DOCS/CHORE: no spec -->
- **Worktree:** <created at P.4> `../python-template_kopie-worktrees/chore/ruff-d-docstrings`
- **Depends on:** `pyproject-tooling-gaps` — it decided (Q-9, 2026-10-04) that ruff `D` stays out of `select` and that the backfill is this separate item; it also edits `[tool.ruff.lint] select`, so this change rebases on it
- **Related specs:** none

## Goal (one line)
Document the public API so `userdocs/api.md` renders real docstrings instead of blanks, and make that state **enforced** by adding ruff `D` to `[tool.ruff.lint] select`.

## Why
`userdocs/api.md:7-14` renders every feature's public API through mkdocstrings (`::: backend.authentication`, `::: backend.eventbus`, …, driven by the `mkdocstrings` plugin at `mkdocs.yml:13`). Whatever a public object's docstring says **is** the published API documentation — so the missing docstrings are not a style gap, they are gaps in the shipped docs.

Measured 2026-10-04: `uv run ruff check --select D src` → **379 errors**. The earlier estimate in `pyproject-tooling-gaps` ("156 of 515 public defs lack a docstring") counted only the `D1xx` missing-docstring family; `D` also pulls in the `D2xx`/`D4xx` formatting and phrasing rules. No `D` code is in `select` today, so nothing prevents further drift.

## In scope
To be fixed at this item's P.2/P.3. Candidate scope:
- Decide the **rule subset**: `D1xx` only (missing docstrings: `D100`–`D107`) versus the full `D` family. The `D2xx`/`D4xx` formatting rules are a separate, larger cleanup and may stay off.
- Decide the **increment shape**: one change per feature (8 features are rendered: authentication, eventbus, filemanagement, logging, mail, sessionmanagement, settings, usermanagement — plus permissions, search, roles) versus one large backfill.
- Add the chosen `D` codes to `[tool.ruff.lint] select` **only once the tree is clean for them**, so the gate never lands red.
- Docstrings follow the repo convention: concise, explaining *why* where non-obvious rather than restating *what* (AGENTS.md, "General Code & Style Conventions").

## Out of scope
- Any change to what the code **does** — docstrings and ruff config only. If a docstring written while documenting contradicts the code, that is a defect: stop and reclassify as ISSUE.
- `userdocs/` prose beyond what mkdocstrings picks up automatically.
- Type-annotation work — that belongs to the mypy strictness step (`pyproject-tooling-gaps` Q-8 enabled `disallow_untyped_defs`; a follow-up may enable `warn-return-any`, measured at 20 errors in 12 files).
- Enabling `D2xx`/`D4xx` unless explicitly decided at P.3.

## Affected features
All rendered features, docstrings only: `backend/{authentication,eventbus,filemanagement,logging,mail,sessionmanagement,settings,usermanagement,permissions,search}`. Config: `pyproject.toml` `[tool.ruff.lint] select`.

## Constraints and risks
- **379 is a lot for one PR.** A single mega-change is unreviewable and invites filler docstrings that restate the signature — worse than none, because mkdocstrings then publishes noise.
- **Docstrings are published output.** `mkdocs build --strict` is a CI gate, so a malformed docstring (bad section, stray `Args:` block) can break the docs build.
- **Gate must land green.** Adding `D` to `select` before the tree is clean turns `lint.yml` red; the config edit is the last step, not the first.
- **Do not fight `pyproject-tooling-gaps`** — it edits the same `select` list.

## Value triage (2026-10-04, pre-workflow)
- **Overlap:** none — no other backlog item does docstring work; `pyproject-tooling-gaps` explicitly deferred it to this item (Q-9).
- **Beneficiary:** readers of the published API reference (`userdocs/api.md` via mkdocstrings) and every future change, because the `D` gate stops further drift.
- **Verdict:** **ACCEPT — 3/5, incremental.** Real consumer, mechanical work, but large: it must be scoped per feature at P.3, not attempted as one 379-error sweep.

## Preparation log

| Step | Date | Result |
|---|---|---|
| P.1 Frame | 2026-10-04 | Framed from `pyproject-tooling-gaps` Q-9 (user decision: `D` off + backlog TODO). Measured cost re-checked: `ruff check --select D src` → 379 errors; consumer confirmed at `userdocs/api.md:7-14` + `mkdocs.yml:13` |
| P.2 Interrogate (<n> questions) | | |
| P.3 Answer (<n> answered) | | |
| P.4 Draft scope + create branch/worktree | | |
| P.5 Self-consistency (FEATURE/CROSS-CUTTING) | | |
