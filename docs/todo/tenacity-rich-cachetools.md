# TODO: tenacity-rich-cachetools

Backlog item for one planned change, created at **P.1 Frame** from this template and named `tenacity-rich-cachetools.md`. One file per change.

This is a **planning record, not normative**: like `docs/questions/`, it is committed directly to `main` (see "Phase P: PREPARE" in `AGENTS.md`). It carries no approval gate — the spec does.

- **Status:** PREPARING  <!-- PREPARING | QUESTIONS-ANSWERED | READY | IN-WORKFLOW | WAITING | MERGED -->
- **Change type:** FEATURE  <!-- each dependency only delivers externally observable behavior once something consumes it; adding the packages alone is not a change the repo can accept (see Why) -->
- **Created:** 2026-10-03
- **Question file:** `docs/questions/tenacity-rich-cachetools.md`
- **Spec:** `docs/specs/tenacity-rich-cachetools.md` — **only if** an item is adopted; the spec would be the consuming feature's spec, not a "add three packages" spec
- **Worktree:** <created at P.4> `../python-template_kopie-worktrees/feature/tenacity-rich-cachetools`
- **Depends on:** decision on `docs/todo/structlog-logging.md` (loguru → structlog) for the `rich` item
- **Related specs:** `docs/specs/authentication.md` (session TTL/revocation, lockout — the caching target), `docs/specs/session-management.md`, `docs/specs/mail-service.md` (the only external-service integration, currently SMTP via `smtplib`, not httpx)

## Goal (one line)
Decide whether **tenacity** (retry/backoff), **rich** (tracebacks/CLI output) and **cachetools** (TTL/LRU cache) earn a place in this template — and if any does, add it together with the feature that consumes it.

## Why
The suggestion is a dependency menu, not a change. Checked against the repo, each item's premise is missing:

| Suggested dependency | Stated rationale | Verified state of the repo |
|---|---|---|
| **tenacity** | "httpx is your outbound HTTP client, but nothing handles retry/backoff for flaky or rate-limited calls." | **There are no outbound HTTP calls.** `grep -rln httpx src/` matches only `src/python_template.egg-info/` (generated metadata) — zero call sites. `pyproject.toml` itself says so: the DEP002 ignore lists `httpx` and `orjson` as *"declared runtime capabilities not yet imported from source."* The one real external integration (mail) uses `smtplib`, not httpx. Retrying a call that does not exist is untestable and unmeasurable. |
| **cachetools** | "if any auth/session logic does repeated lookups … skip if you already have a cache layer." | **No cache layer exists** (`grep -rn "lru_cache\|cachetools\|TTLCache\|_cache" src/` → nothing), so the skip-condition does not apply — but neither is there a measured hot path. Worse, the proposed target is the security-critical one: sessions are opaque tokens whose **hash** is looked up per request, and the spec requires that a password change or completed reset **revokes all existing sessions** and that a locked identifier stays locked for the lockout window. A TTL cache in front of those reads is a revocation-latency decision, not a performance tweak. |
| **rich** | "pairs naturally with loguru: nicer tracebacks, tabular CLI output, better diffs when something in your test suite fails." | Partially right, partially not. `rich.traceback` is a real fit for loguru today — but `docs/todo/structlog-logging.md` (CROSS-CUTTING, pending) proposes replacing loguru entirely, so a traceback integration written now may be superseded. "Better diffs when your test suite fails" is **not** what rich does: pytest already renders assertion diffs, and rich does not hook into pytest without a plugin. There is also no CLI in this repo to render tables for. |

And the mechanical blocker, independent of merit: **a dependency with no consumer fails CI.** `uv run deptry .` is a gate job (`.github/workflows/quality.yml:93-94`) and a pre-commit hook; an unused `tenacity`/`rich`/`cachetools` is a DEP002 finding. Suppressing it with another `DEP002` ignore would mean adding a package the project's own tooling calls dead weight — the exact signal the deptry config was tuned to produce.

`AGENTS.md` is explicit about the ordering this suggestion inverts: *"Dependency decisions must be traceable to the feature or architectural decision that motivated them. Record the decision in an ADR."* The feature comes first; the dependency follows.

## In scope
- One decision per dependency: **adopt with a consumer**, or **decline**.
- If adopted, the change is the **feature that needs it**, with the dependency as one line of its spec:
  - *tenacity* → the first feature that actually calls an external HTTP API (e.g. an OAuth/OIDC or third-party provider integration). Retry policy must be specified: which exceptions, how many attempts, backoff+jitter, total deadline, and whether the call is idempotent enough to retry at all.
  - *cachetools* → a specified cache with an explicit invalidation contract: TTL, max size, and **where revocation busts it** (password change, completed reset, logout, lockout, session revoke). Without the invalidation ACs this is a security regression dressed as an optimization.
  - *rich* → a CLI/reporting surface that does not exist yet, or `rich.traceback` installed as loguru's formatter (only after the `structlog-logging` decision, since that change may remove loguru).
- Per adopted dependency: an ADR (new dependency decision), a test strategy (`respx` for retry behavior — assert attempt counts, not just success; `time-machine` for TTL expiry — freeze and advance the clock), and the `[tool.deptry]` config left untouched (no new ignore).

## Out of scope
- Adding any of the three packages without a consuming feature — that is the failure mode this TODO exists to prevent.
- A new `DEP002` ignore entry to make an unused dependency pass CI.
- Caching anything in `authentication` / `sessionmanagement` before the revocation-latency question is answered in a spec.
- A general "make the CLI nicer" change — there is no CLI.
- Replacing loguru's traceback rendering (owned by `docs/todo/structlog-logging.md`).

## Affected features
Undecided — determined by whichever consumer is specified. Candidates: `src/backend/authentication/` + `src/backend/sessionmanagement/` (cachetools), `src/backend/mail/` or a new external-provider feature (tenacity), a new CLI/reporting entrypoint (rich). Today: none.

## Constraints and risks
- **Revocation latency is the sharp edge.** Session validity, lockout state and reset-token single-use are all time- and state-sensitive. A cache that returns a session object for `ttl` after the password changed is a real authentication bug, not a performance trade-off. Any cache here needs an AC of the form *"Given a valid session, When the password is changed, Then the next `session_info(token)` fails"* — and that test must be written before the cache is.
- **Retry correctness needs idempotency.** Retrying a non-idempotent POST duplicates side effects (a duplicated password-reset email, a duplicated file record). The spec must state which operations are retryable.
- **Test tooling already covers both** (`respx`, `time-machine` per "Using the Test Tooling"), so the test cost is low *once a consumer exists* — and undefined before that.
- **Template scope.** This is a template: a dependency in `[project] dependencies` is inherited by every project bootstrapped from it, so an unused one is copied forward indefinitely. That raises the bar for adding, and lowers the cost of declining.
- **Ordering risk:** `rich` + loguru integration vs. the pending `structlog-logging` change. Do not build on the losing side of that undecided swap.

## Value triage (2026-10-03, pre-workflow)
- **Overlap:** none of the three exists today, so there is no duplication — but there is also no consumer, which is the other way a dependency item fails the bar.
- **Beneficiary:** hypothetical — "the first time an external service hiccups", and this repo currently makes no external service calls from `src/`.
- **Score: 2/5** — as written, all three are solutions ahead of their problems; `cachetools` additionally carries a security cost the suggestion does not mention. `rich` is the only one with a plausible near-term home, and its home depends on another open decision.
- **Recommendation: decline all three now; keep this file as the menu.** Re-open each as one line inside the spec of the feature that first needs it (retry → first outbound HTTP feature; cache → a measured hot path plus an invalidation contract; rich → a real CLI or the post-structlog traceback decision). Adding them "because they're low-risk" would make `uv run deptry .` red and add a DEP002 ignore, which is worse than the problem.

## Acceptance signal (plain language)
For each dependency that ends up adopted: it is imported by at least one module under `src/`, `uv run deptry .` is clean **without** a new `DEP002` ignore, an ADR records why it was chosen over the alternatives, and its behavior has tests (attempt counts under `respx`; expiry under `time-machine`; revocation-still-holds for any cache). For each that is declined: this file records the decision and the trigger that would re-open it. Either way `uv run pytest tests/` is green and no package sits in `dependencies` that nothing imports.

## Prep log
| Step | Date | Result |
|---|---|---|
| P.1 Frame | 2026-10-03 | TODO + question file created on `main`; type FEATURE (per dependency, once a consumer exists); premises verified — **httpx has zero call sites in `src/`** (DEP002 already records it as declared-but-unused), **no cache layer exists**, **no CLI exists**, pytest already renders assertion diffs; mechanical blocker recorded: an unused dependency fails the `deptry` CI gate (`quality.yml:94`); **value triage 2/5 — decline now, re-open per consuming feature** |
| P.2 Interrogate | 2026-10-03 | **not run — recommended DROPPED, awaiting the user's decision.** The Why section already closes every interrogation point from repository evidence (zero httpx call sites, no cache layer, no CLI, `deptry` DEP002 blocker, template-inheritance cost), so a P.2 subagent would be ceremony. P.2 runs only if the user decides to adopt one of the three, and then as one line inside the consuming feature's spec |
| P.3 Answer (<n> answered) | | |
| P.4 Draft spec / triage / baseline / scope | | |
| P.5 Self-consistency | | |
