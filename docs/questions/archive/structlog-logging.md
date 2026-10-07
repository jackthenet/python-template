# Questions: structlog-logging

One question file per change, created at **P.1 Frame** from this template and named `<change-name>.md`. It replaces the retired central `AI_Questions.md` (archived at `docs/questions/archive-AI_Questions.md`).

- **Change:** structlog-logging (CROSS-CUTTING)
- **TODO file:** `docs/todo/structlog-logging.md`
- **Spec:** docs/specs/structlog-logging.md (new) + amendments to docs/specs/logging.md and docs/specs/logging-coverage.md
- **Opened:** 2026-10-03
- **Status:** ALL ANSWERED  <!-- OPEN | ALL ANSWERED — set OPEN by the orchestrator at P.1; ALL ANSWERED once every question in this file has an answer (the orchestrator records it together with the `QUESTIONS-ANSWERED` TODO advance) -->
- **Answer rounds:** 5
- **P.2 result:** 25 questions in one `BLOCKED-USER` batch (2026-10-03); 15 points closed from evidence; 21 categories covered, 3 skipped with reason (Dependency Smoke-Test → P.5, ADR drafting → P.4/S2.1, task DAG → Phase 2). Recommendation: **Option A (2-line DOCS/CHORE)** — see the measured comparison above.

Every question that needs user input is recorded HERE — never in a central file. A step that needs input records **all** of its open questions in one batch and returns `BLOCKED-USER`; the orchestrator presents them (as few `ask_user_question` rounds as possible, <= 4 per round, most blocking first), records the answers here, marks each **ANSWERED** and **incorporated**, and relaunches the step **once** with the full answer set. The change is `WAITING` while its questions are unanswered — the orchestrator works on another change meanwhile, it does not idle.

### Entry format

```markdown
## Q-<n> — <short title>
- **Step:** <P.2 Interrogate, or Sx.x <step name> — Phase <n>>
- **Why needed:** <the ambiguity, missing requirement, or decision>
- **Context:** <what the step had learned at the time>
- **Question:** <the question for the user>
- **Answer:** <the user's answer>  (or **PENDING**)
- **Date:** <YYYY-MM-DD>
- **Status:** PENDING | ANSWERED
- **Incorporated:** no | yes — <where: REQ-XXX / AC-XXX / spec section / decision>
```

## Preparation questions (P.2)

**25 questions, one `BLOCKED-USER` batch.** Q-01 is the decision; Q-02…Q-25 are the CROSS-CUTTING consequences that only matter **if** Q-01 = migrate (Q-23 applies either way). Nothing here is filler: each entry is a decision the spec/ADR cannot make for itself. 15 points were closed from evidence and are recorded under "Evidence-closed" instead of being asked.

### Interrogation result — the two options, measured (re-measured 2026-10-03, not inherited from the TODO)

| | **Option A — correct the guidance (DOCS/CHORE)** | **Option B — swap the backend (CROSS-CUTTING)** |
|---|---|---|
| What changes | 2 lines of skill text: `.agents/skills/python-best-practices/SKILL.md:16`, `references/modern-python.md:85` (+ 2 structlog examples at `references/errors-and-resources.md:17,43`) → say loguru | loguru → structlog pipeline + stdlib handlers behind the same public API |
| Source files | 0 | 7 (`rg -c loguru src`): `logging/_setup.py` 12, `_decorator.py` 1, `logging/feature_settings.py` 1, `eventbus/eventbus.py` 1, `permissions/service.py` 1, `settings/registry.py` 1, `settings/repository.py` 1 — logging feature = 606 LOC (`_decorator.py` 231, `_setup.py` 177, `feature_settings.py` 111, `_settings.py` 64, `__init__.py` 23) |
| Direct backend calls outside the feature | 0 | **39** `logger.*` calls: `settings/registry.py` 17, `settings/repository.py` 11, `eventbus/eventbus.py` 10, `permissions/service.py` 1 (imports at `registry.py:10`, `repository.py:22`, `eventbus.py:20`, `service.py:38`) |
| Test files touched | 0 | **17** files, **43** loguru matches, **2 390 LOC**, **75** `def test` functions — incl. `tests/acceptance/logging_coverage/test_direct_loguru_kept.py` (54 LOC, exists only to enforce REQ-010) and `tests/unit/logging/test_logging_sink_ownership.py` (3 reconfigure tests) |
| Specs to amend | 0 | `logging.md` (REQ-001, REQ-003, AC-001, AC-004, INV-001, EDGE-005, NFR-003, Goal:9, Dependencies:13), `logging-coverage.md` (REQ-010/AC-010), `settings-coverage.md` (REQ-014/015, AC-019/020, EDGE-008), `settings.md:11,16,351` |
| ADRs | 0 | new ADR superseding **ADR-002** (its "Alternatives Considered" already rejected structlog); ADR-035:19,21,31 and ADR-060:37 also name loguru |
| Extra gates | none | Spec Amendment PR merged **before** implementation (`AGENTS.md:1073`), Phase 3 re-derivation, per-feature traceability rows, NFR-001/NFR-002 re-measured, version bump |
| Precedent cost | `chore(track-python-skill)` `c2342b6` (8 files, docs only) | `amend-nfr-001-budgets` (`docs/verification/amend-nfr-001-budgets.md`) — a **one-ID** amendment already cost a separate PR + 2 re-derived contract tests + 2 traceability rows |
| Who benefits | an agent following the repo's own guidance (the contradiction disappears) | nobody today: no HTTP layer (`pyproject.toml` has no fastapi/flask/uvicorn), `src/frontend/` is empty, no log parser in `src/` |

**Recommendation (P.2): Option A.** The structlog text was never a project decision — it entered the repo as verbatim third-party skill boilerplate in `chore(track-python-skill)` (`c2342b6`), which only *tracked* an untracked directory. There is no consumer of structured records in this repo (Q-02), and Option B's cost is one spec amendment + 7 source files + 17 test files + 2 re-measured budgets for zero new capability. If the user does want structured output, Option B is legitimate — but it must be chosen for that reason, not to fix the contradiction (Option A fixes the contradiction at 2 lines).

### Coverage

| Category | Status |
|---|---|
| migrate-vs-correct decision | covered (Q-01, Q-02) |
| dependency choice (structlog vs loguru vs stdlib) | covered (Q-03, Q-17) |
| spec-amendment mechanics | covered (Q-04, Q-19) |
| ADR supersession | covered (Q-16) |
| Impact Analysis (per feature + REQ/AC IDs) | covered — table below |
| test re-derivation cost / weakening prohibition | covered (Q-18, Q-25) |
| public API compatibility | covered (Q-10) |
| sinks / rotation / `log_max_bytes` / `log_backup_count` | covered (Q-15) |
| `diagnose=False` secret policy | covered (Q-09) |
| settings keys / live reconfigure | covered (Q-06, Q-07) |
| stdlib interception & frame depth | covered (Q-08) |
| loguru-only capabilities (colorize/backtrace/enqueue) | covered (Q-14) |
| output format / renderer / JSON | covered (Q-11, Q-12) |
| performance (NFR-001/NFR-002) | covered (Q-13) |
| decorator implementation strategy | covered (Q-24) |
| migration / rollout order | covered (Q-19, Q-20, Q-21) |
| NFRs & version bump | covered (Q-13, Q-22) |
| test strategy | covered (Q-18, Q-25) |
| feature boundaries | covered (Q-05, Q-20) |
| hybrid option | covered (Q-03) |
| out-of-scope confirmation (tracing policy, existing log history) | covered (Q-11, Q-23) |
| Dependency Smoke-Test | **skipped — P.5's step** (`structlog` is not installed today: `uv run python -c "import structlog"` → `ModuleNotFoundError`); P.2 must not add a dependency |
| ADR content drafting | **skipped — P.4/S2.1's work**; only the numbering question is asked (Q-16) |
| task DAG shape | **skipped — Phase 2** |

### Evidence-closed (not asked)

- The contradiction is real and one-directional: skill says structlog (`SKILL.md:16`, `modern-python.md:85`, `errors-and-resources.md:17,43`), code+spec say loguru (`docs/specs/logging.md:13,44,66,68,82,85,104,116`; `pyproject.toml:12` `loguru>=0.7.3`). No `structlog` anywhere in `src/`, `tests/`, `pyproject.toml`.
- ADR-002 rejected structlog **on a false premise** — "it adds a second dependency": structlog is not a backend, it is a processor/renderer pipeline that binds to stdlib `logging` handlers, so the swap *removes* a dependency and moves the sinks to stdlib `RotatingFileHandler`/`StreamHandler`. ADR-002 also cites "NFR-002" as the dependency constraint, but `logging.md:123` NFR-002 is decorator overhead; the constraint is the Overview Dependencies row (`logging.md:13`) — a stale ID reference the amendment should fix.
- `setup_logger()` is already **no-arg and settings-driven** (`_setup.py:96`; `settings-coverage.md:141` REQ-014, `:142` REQ-015, `:176` AC-020) and reconfigures the sinks on `logging.*` changes; the TODO's "`setup_logger(settings)`" framing is outdated. Settings keys are `logging.log_level`, `logging.log_file`, `logging.log_max_bytes`, `logging.log_backup_count`, `logging.profiling_include_arguments` (`feature_settings.py:58-106`) — not the bare `log_level` names in the TODO.
- Public API surface today: `Settings`, `get_settings`, `setup_logger`, `logged`, `logged_class`, `register_settings`, `_read_setting` (`src/backend/logging/__init__.py:16-22`).
- Sink-ownership behaviour is a live contract from issue `main-ci-green` item E: `test_reconfigure_keeps_foreign_sink`, `test_reconfigure_replaces_only_the_managed_sinks`, `test_reconfigure_after_external_removal_of_a_managed_sink` (`tests/unit/logging/test_logging_sink_ownership.py:130,149,164`; traceability rows `docs/verification/traceability.md:18,33`).
- NFR budgets are executable: `tests/contract/logging/test_logging_contracts.py:26` (`test_nfr_001_setup_time_budget`), `:54` (`test_nfr_002_decorator_overhead_budget`), `:90` (`test_nfr_003_diagnose_false`), `:104` (`test_nfr_004_backward_compatible_api`).
- `orjson` is already a declared runtime dependency, unused from source and DEP002-ignored (`pyproject.toml:14`, `:115-119`) — a JSON renderer needs no new dependency.
- Next free ADR number is **ADR-081** (81 files, highest `ADR-080`), but `docs/todo/api-keys.md:64` already plans "ADRs from **ADR-081**" — a numbering collision to resolve at merge order, not a question for the user.
- Suite baseline for any re-derivation gate: 727 passed, 1 skipped (`docs/verification/traceability.md:19`).
- Repo state: `git worktree list` → primary only; `git branch -a` → `main` + `origin/main`; `gh pr list --state open` → none (PR #62 merged).

### Impact Analysis — Option B (per feature; Option A touches no feature)

| Feature / artifact | What changes | REQ/AC/INV/EDGE/NFR touched | Traceability rows (`docs/verification/traceability.md`) |
|---|---|---|---|
| `backend/logging` (owner) | `_setup.py` sinks → stdlib handlers + structlog config; `_decorator.py` emit path; `_settings.py` unchanged | `logging.md` REQ-001, REQ-002 (mechanism), REQ-003, AC-001, AC-002, AC-004, AC-005, INV-001, EDGE-001, EDGE-005, NFR-001, NFR-002, NFR-003, NFR-004 | :18, :19, :21, :33, and the logging matrix rows |
| `backend/settings` | 28 direct `logger.*` calls (registry 17, repository 11) → feature API or new backend's logger | `logging-coverage.md` REQ-010/AC-010; `settings-coverage.md` REQ-014/015, AC-019/020, EDGE-008 | :390, :391, :411 |
| `backend/eventbus` | 10 direct calls (`eventbus.py:86-233`) | `logging-coverage.md` REQ-010/AC-010; `event-bus.md` rows touched by item H | :45, and Event Bus Matrix |
| `backend/permissions` | 1 direct call (`service.py:38`) | `logging-coverage.md` REQ-010/AC-010 | user-roles-permissions matrix |
| `logging-coverage` policy | REQ-010 "keep direct loguru" retired or restated | REQ-010, AC-010 (+ `test_direct_loguru_kept.py`) | :343 |
| `settings.md` / `settings-coverage.md` wording | "loguru observability" / dependency rows | `settings.md:11,16,351`; `settings-coverage.md:10` | settings matrices |
| `authentication`, `usermanagement`, `sessionmanagement`, `filemanagement`, `mail`, `search`, `src/main.py` | **no code change** (public API unchanged) — only their log-record format changes | their NFR/secret rows re-checked (e.g. authentication NFR-002, mail secret-free events) | their matrices' logging-related rows only if format is asserted |
| ADRs | new ADR supersedes ADR-002; ADR-035, ADR-060 annotated | — | — |

### Impact Analysis — Option A

| Artifact | Change | IDs touched |
|---|---|---|
| `.agents/skills/python-best-practices/SKILL.md:16`, `references/modern-python.md:85` (+ `references/errors-and-resources.md:17,43` examples) | "structlog" → "the shared logging feature (`backend.logging`, loguru-backed)" | none (no behavior, no spec ID) |
| `docs/todo/structlog-logging.md` | closed as declined (superseded by the chore) | — |
| `docs/todo/tenacity-rich-cachetools.md:13,37,45,55` | its `rich` dependency on this decision clears immediately | — |

### Overlap check (13 specs, 16 TODOs, worktrees/branches/PRs)

- **Specs naming logging/loguru:** `logging.md`, `logging-coverage.md`, `settings.md:11,16,351`, `settings-coverage.md:10,141-143,175-177`; 8 more specs reference the logging *feature* (`authentication`, `event-bus`, `file-management`, `mail-service`, `search`, `session-management`, `user-management`, `user-roles-permissions`) — none names a backend, so only 4 specs need amendment. ADRs naming loguru: ADR-002, ADR-035, ADR-060.
- **TODOs (16):** `tenacity-rich-cachetools` (PREPARING) declares `Depends on: decision on docs/todo/structlog-logging.md` for its `rich` item (`:13,37,45,55`) — it explicitly refuses to build on the losing side, so **the decision itself is the unblock**, whichever way it goes. `api-keys` (WAITING) and `notifications` (WAITING) will write new logging-using code and must follow whichever backend wins (ADR-060 tracing policy is backend-agnostic, so no rework either way). `pyproject-tooling-gaps` and `python-3.15` (PREPARING) both edit `pyproject.toml` — merge-order conflict with the dependency swap (Q-21). `value-triage-gate.md:91` already scores this change 3/5 "decide at P.3 first". `track-python-skill` (MERGED) is the commit that introduced the structlog text (`c2342b6`) — no double work: correcting it is a new 2-line chore, not a re-do of that change. No other TODO touches logging.
- **In-flight:** no worktrees besides the primary, no branches besides `main`/`origin/main`, no open PRs.

## Q-01 — Migrate to structlog, or correct the guidance to match loguru?
- **Step:** P.2 Interrogate
- **Why needed:** The whole change rests on the premise that the loguru→structlog swap is wanted. The repo's own value triage (`docs/todo/structlog-logging.md` "Value triage", `docs/todo/value-triage-gate.md:91`) says "decide at P.3 first"; every other question is conditional on it.
- **Context:** Option A = 2 skill lines (`SKILL.md:16`, `modern-python.md:85`) corrected to name loguru, matching the approved spec. Option B = 7 source files (606 LOC in the logging feature) + 39 direct backend calls + 17 test files (2 390 LOC, 75 test functions) + 4 spec amendments + a superseding ADR + 2 re-measured NFR budgets. The structlog text arrived by accident as third-party skill boilerplate in `chore(track-python-skill)` (`c2342b6`), not as a decision.
- **Question:** Which option? **(A)** DOCS/CHORE: correct the two skill lines to name the loguru-backed `backend.logging` feature, close this TODO as declined — *recommended, 2 lines, no spec touched, unblocks `tenacity-rich-cachetools` immediately*. **(B)** CROSS-CUTTING swap: amend 4 specs, supersede ADR-002, re-derive 17 test files. **(C)** Hybrid: keep loguru sinks, add a structlog facade on top (strictly more code than A and more dependencies than B — see Q-03). **(D)** Drop loguru for stdlib `logging` only (no new dependency; see Q-03).
- **Answer:** **(B) Migrate — the full CROSS-CUTTING structlog swap.** Chosen over the recommended (A); the user wants structured records, so 4 spec amendments, a superseding ADR, 7 source files and 17 re-derived test files are accepted. Q-02…Q-25 are therefore live, not moot.
- **Date:** 2026-10-04 (rounds 1-5)
- **Status:** ANSWERED
- **Incorporated:** yes — TODO type stays CROSS-CUTTING; In scope rewritten

## Q-02 — Is there any consumer that needs structured (key/value) log records?
- **Step:** P.2 Interrogate
- **Why needed:** Structured output is the *only* genuinely new capability in Option B (the TODO admits it: "the *only* genuinely new thing is structured key/value records"). If no consumer exists, the benefit is unrealizable and the cost is unjustified.
- **Context:** No HTTP/RPC layer (`pyproject.toml` has no fastapi/flask/uvicorn/starlette), `src/frontend/` is empty, nothing in `src/` parses log output, `logs/app.log` is read by humans. `api-keys` (WAITING) would create the first machine-driven API surface — a future consumer, not a present one.
- **Question:** Name the consumer that needs JSON/key-value records today (log aggregator, Loki/OTLP, an LLM reading logs, a CLI filter). If none: is structured output still wanted as future-proofing, or is that YAGNI and Option A wins?
- **Answer:** **Future-proofing — no present consumer is named.** The amended Goal states structured records as preparation for the machine-driven surface `api-keys` would create and for log aggregation; today `src/frontend/` is empty, there is no HTTP layer, and humans read `logs/app.log`. The JSON file sink still gets ACs, but the spec does not claim a present consumer.
- **Date:** 2026-10-04 (rounds 1-5)
- **Status:** ANSWERED
- **Incorporated:** yes — amended `logging.md` Goal + decision Q-02

## Q-03 — If migrating: structlog+stdlib, stdlib only, or structlog over loguru?
- **Step:** P.2 Interrogate
- **Why needed:** The dependency decision drives the ADR, the spec wording, and deptry. ADR-002's rejection ("adds a second dependency") is factually wrong and must be re-evaluated per `AGENTS.md` "Dependencies and Existing Packages".
- **Context:** structlog is a processor/renderer pipeline that binds to stdlib `logging` handlers, so B implies stdlib `StreamHandler` + `RotatingFileHandler` and *removes* loguru. `orjson` is already declared and unused (`pyproject.toml:14`, DEP002 at `:115-119`), so JSON rendering needs no new dependency either.
- **Question:** **(A)** stdlib `logging` only — zero new dependencies, sinks/rotation/interception all native, `diagnose`-equivalent trivial, deptry clean — *recommended if migrating*. **(B)** structlog + stdlib handlers — processor chain, context binding, JSON renderer; one new dependency, and `AGENTS.md`'s "Capability, not library" rule means the spec should name the capability anyway. **(C)** structlog facade over loguru sinks — two backends, worst of both; recommend rejecting. Which?
- **Answer:** **(B) structlog + stdlib handlers.** structlog's processor/renderer pipeline binds to stdlib `StreamHandler` + `RotatingFileHandler`; **loguru is removed** and structlog added. (C) structlog-over-loguru rejected (two backends). ADR-002's 'adds a second dependency' rationale is re-evaluated in the superseding ADR.
- **Date:** 2026-10-04 (rounds 1-5)
- **Status:** ANSWERED
- **Incorporated:** yes — decision Q-03; new ADR; `pyproject.toml` deps

## Q-04 — Which spec IDs get amended, and in which wording style?
- **Step:** P.2 Interrogate
- **Why needed:** The Spec Amendment Workflow (`AGENTS.md:1073`) forbids editing the approved spec outside its own PR, and the amendment must be merged **before** implementation. The ID list defines the affected-task set and the re-derivation scope.
- **Context:** loguru-specific IDs: `logging.md:66` REQ-001 (console+file loguru sinks, colorize/backtrace/enqueue/`diagnose=False`), `:68` REQ-003 (`_InterceptHandler` routes stdlib→loguru), `:82` AC-001, `:85` AC-004, `:104` INV-001 ("number of **loguru** sinks"), `:116` EDGE-005 (level unknown *to loguru*), `:124` NFR-003 (`diagnose=False`), plus Goal `:9` and Dependencies `:13`. Also `logging-coverage.md:118` REQ-010 / `:142` AC-010 ("all existing direct loguru statements are kept unchanged"), `settings-coverage.md:141-143` REQ-014/015/016 + `:175-177` AC-019/020/021 + EDGE-008, and `settings.md:11,16,351`.
- **Question:** Confirm the amendment list, and choose the style: **(A)** restate in capability terms ("one console sink + one rotating file sink, UTF-8, rotation by size with N backups, third-party stdlib records captured with correct file/line, no local-variable values in records") so the backend is a default, not a norm — *recommended, matches the skill's "Capability, not library" rule*; **(B)** name structlog/stdlib normatively in v3 (simpler, but re-creates the same contradiction if the backend changes again). Which IDs and which style?
- **Answer:** **(A) capability terms.** The amendment restates rather than names the backend. ID list confirmed: `logging.md` REQ-001, REQ-003, AC-001, AC-004, INV-001, EDGE-005, NFR-003 + Goal + Dependencies; `logging-coverage.md` REQ-010/AC-010; `settings-coverage.md` REQ-014/015/016 + AC-019/020/021 + EDGE-008; `settings.md` references.
- **Date:** 2026-10-04 (rounds 1-5)
- **Status:** ANSWERED
- **Incorporated:** yes — amendment PR ID list

## Q-05 — Keep or retire the "direct backend statements are allowed" policy (logging-coverage REQ-010/AC-010)?
- **Step:** P.2 Interrogate
- **Why needed:** It decides whether 39 call sites in 3 other features migrate (a cross-feature edit) or stay. It also decides whether `tests/acceptance/logging_coverage/test_direct_loguru_kept.py` is re-derived or deleted.
- **Context:** 39 direct calls: `settings/registry.py` 17, `settings/repository.py` 11, `eventbus/eventbus.py` 10, `permissions/service.py` 1. `AGENTS.md:767,769` currently sanctions direct loguru for one-off statements; `logging-coverage.md:118` REQ-010 makes "keep them" normative; `test_direct_loguru_kept.py:20` asserts the four exact message texts.
- **Question:** **(A)** retire the policy — features import a logger from `backend.logging` (e.g. a new `get_logger()` export), so a future backend swap touches 1 file; costs 39 call-site edits + re-derived AC-010 test. **(B)** keep the policy, restated backend-agnostically ("direct statements via the configured backend") — 39 sites still change import, but the invariant survives. **(C)** keep loguru untouched in those files (impossible under Option B). Which?
- **Answer:** **(A) Retire the policy.** Features import a logger from `backend.logging` via a new `get_logger()` export, so a future swap touches one file. All 39 direct calls migrate (`settings/registry.py` 17, `settings/repository.py` 11, `eventbus/eventbus.py` 10, `permissions/service.py` 1); AC-010 is re-derived, not kept as 'direct loguru kept'.
- **Date:** 2026-10-04 (rounds 1-5)
- **Status:** ANSWERED
- **Incorporated:** yes — amended REQ-010/AC-010; `AGENTS.md` tracing policy

## Q-06 — Must runtime reconfiguration of the sinks survive the swap?
- **Step:** P.2 Interrogate
- **Why needed:** It is normative in `settings-coverage.md` (REQ-015/AC-020/EDGE-008) and is the hardest behavior to port; if it may be dropped, the amendment shrinks and the swap gets much cheaper.
- **Context:** Today `setup_logger()` is no-arg and reads `logging.*` from the settings registry (`_setup.py:96`), subscribes to `SettingChanged` (`_setup.py:118`), and re-adds sinks on change (`_setup.py:144-164`). With stdlib handlers, level/rotation can be mutated in place instead of remove-and-re-add — a different mechanism, same observable effect.
- **Question:** Must `set_value("logging.log_level", "DEBUG")` still take effect without a restart (keep REQ-015/AC-020/EDGE-008, restated capability-wise), or is "applies at next start" acceptable (amend those IDs — a behavior removal)? Recommend keeping it; it is user-visible via the settings UI.
- **Answer:** **Live reconfiguration survives.** `set_value("logging.log_level", …)` still takes effect without a restart; REQ-015/AC-020/EDGE-008 are kept and restated capability-wise. Mechanism may change (stdlib level/rotation mutate in place instead of remove-and-re-add).
- **Date:** 2026-10-04 (rounds 1-5)
- **Status:** ANSWERED
- **Incorporated:** yes — amended `settings-coverage.md` REQ-015/AC-020/EDGE-008

## Q-07 — Must "reconfigure replaces only the sinks it owns" survive?
- **Step:** P.2 Interrogate
- **Why needed:** It is a live contract added by issue `main-ci-green` item E and it is exactly the kind of behavior a backend swap silently breaks (stdlib root handlers vs loguru sink ids).
- **Context:** `tests/unit/logging/test_logging_sink_ownership.py:130,149,164` — foreign sinks/handlers must survive, a externally-removed managed sink must not break reconfigure, and `tests/conftest.py` has the autouse `_stdlib_root_logging_restored` fixture (item I) because alembic's `fileConfig` already replaces stdlib root handlers. With stdlib handlers the feature would *install into the same namespace alembic mutates* — a new interaction to specify.
- **Question:** Confirm the invariant is restated (not dropped) in the amended spec, and decide the mechanism: attach handlers to the stdlib root logger (and cooperate with `fileConfig` users such as alembic), or keep a dedicated non-propagating logger? Which, and does the alembic interaction become an EDGE?
- **Answer:** **Invariant restated, not dropped**, and the mechanism is a **dedicated non-propagating logger** that owns the two handlers — so alembic's `fileConfig` cannot replace them and foreign handlers are untouched. The alembic/`fileConfig` interaction is recorded as a new EDGE ID.
- **Date:** 2026-10-04 (rounds 1-5)
- **Status:** ANSWERED
- **Incorporated:** yes — amended INV-001 + new EDGE; `test_logging_sink_ownership.py` re-derived

## Q-08 — Does stdlib interception (REQ-003, AC-004/005, EDGE-005) get amended or deleted?
- **Step:** P.2 Interrogate
- **Why needed:** Under a stdlib-native backend the interception handler is largely *unnecessary* — third-party records are already in the right system. Deleting normative IDs is a bigger amendment than restating them, and it changes which tests are re-derived vs removed.
- **Context:** `_InterceptHandler` (`_setup.py:42`) routes stdlib→loguru and skips frozen importlib bootstrap frames for correct file/line (AC-005, EDGE-005). Under stdlib handlers, records arrive natively; the frame-depth work disappears, but "third-party records reach the same console+file sinks" must still be normative.
- **Question:** **(A)** restate REQ-003 as "records from third-party stdlib loggers reach the same sinks with correct level, file and line" and delete the bootstrap-frame AC/EDGE as no longer meaningful; **(B)** keep every ID and port the frame logic. Which? (Deleting IDs must be explicit in the amendment changelog — `AGENTS.md` Spec Amendment Workflow.)
- **Answer:** **(A) Restate and delete.** REQ-003 becomes 'records from third-party stdlib loggers reach the same sinks with correct level, file and line'; the importlib bootstrap-frame AC-005 and EDGE-005 are **deleted** as no longer meaningful, named explicitly in the amendment changelog per the Spec Amendment Workflow.
- **Date:** 2026-10-04 (rounds 1-5)
- **Status:** ANSWERED
- **Incorporated:** yes — amendment changelog (deletions)

## Q-09 — How is the no-local-variable-leakage rule (NFR-003) restated and proven?
- **Step:** P.2 Interrogate
- **Why needed:** It is a security requirement with no structlog/stdlib one-to-one equivalent, and it is currently asserted by a loguru-specific contract test (`test_nfr_003_diagnose_false`, `tests/contract/logging/test_logging_contracts.py:90`). It must not quietly disappear in the swap.
- **Context:** `AGENTS.md` "Using the Logging Feature" enforces `diagnose=False`; `logging-coverage.md:123` REQ-015 / `:158` INV-002 forbid raw tokens/passwords/hashes in any record; authentication NFR-002 and mail's secret-free events depend on it.
- **Question:** Restate NFR-003 as "no exception record may contain local variable values; only type, message and traceback frames" — and which test proves it (a property test over a raising function with a secret local, asserting the secret never appears in the file sink)? Confirm that is the acceptance bar, and confirm `include_args=False` semantics stay byte-identical.
- **Answer:** **Restated + property test.** NFR-003 becomes 'no exception record may contain local variable values — only type, message and traceback frames', proven by a Hypothesis property test over a raising function with a secret local, asserting the secret never reaches the file sink. `include_args=False` semantics stay byte-identical.
- **Date:** 2026-10-04 (rounds 1-5)
- **Status:** ANSWERED
- **Incorporated:** yes — amended NFR-003 + new property test

## Q-10 — Is the public API byte-compatible, or is this a breaking change?
- **Step:** P.2 Interrogate
- **Why needed:** It decides the version bump (`minor` vs `major`) and whether consumer features are edited at all.
- **Context:** Exports today: `Settings`, `get_settings`, `setup_logger`, `logged`, `logged_class`, `register_settings`, `_read_setting` (`src/backend/logging/__init__.py:16-22`); `test_nfr_004_backward_compatible_api` (`test_logging_contracts.py:104`) guards NFR-004.
- **Question:** Keep all seven exports and every decorator parameter (`level`, `slow_threshold_ms`, `slow_threshold_setting`, `include_args`, `context_getter`, `depth`) unchanged → non-breaking, `minor`? Or take the opportunity to change the surface (e.g. export `get_logger()` for Q-05, drop `context_getter`/`depth`, add a `renderer` parameter) → breaking, `major` + every consumer touched. Recommend byte-compatible; confirm.
- **Answer:** **BREAKING redesign.** The public surface changes: `context_getter` and `depth` are dropped, a `renderer` parameter is added, `get_logger()` is added (Q-05). Consequences: `major` bump (Q-22), and the `logging-coverage.md` IDs asserting `context_getter`/`depth` are amended away with their tests re-derived.
- **Date:** 2026-10-04 (rounds 1-5)
- **Status:** ANSWERED
- **Incorporated:** yes — amended `logging-coverage.md` IDs; version bump major

## Q-11 — Is the log line format allowed to change, and is that itself breaking?
- **Step:** P.2 Interrogate
- **Why needed:** Log format is externally observable (the TODO's own risk note: "people grep and read `logs/app.log`"), which is why this is CROSS-CUTTING and not REFACTOR — but the spec never specifies a format, so the amendment must decide how much freedom the new backend has.
- **Context:** loguru's current format carries timestamp/level/module:line/message with color on the console; nothing in `docs/specs/logging.md` pins it, and no test asserts the exact format string (tests assert substrings, e.g. `test_direct_loguru_kept.py:44-54`).
- **Question:** **(A)** free format — the spec states only the record's *fields* (level, logger name, message, elapsed ms, file/line) and the format is an implementation detail; **(B)** pin a format in the amended spec (text template) so greps keep working; **(C)** pin fields + add a `logging.format` setting. Which? And does a format change alone force `major` (see Q-22)?
- **Answer:** **(A) Fields only, free format.** The amended spec states the record's fields (level, logger name, message, elapsed ms, file/line); the format string is an implementation detail. Nothing today pins it and no test asserts the exact template.
- **Date:** 2026-10-04 (rounds 1-5)
- **Status:** ANSWERED
- **Incorporated:** yes — amended `logging.md` (fields list)

## Q-12 — Output format and renderer: text, JSON, or both — and with which serializer?
- **Step:** P.2 Interrogate
- **Why needed:** It is the concrete deliverable of "structured records" and it decides whether a new dependency enters (the skill's Dependency Smoke-Test then applies at P.5).
- **Context:** `orjson` is already declared and unused (`pyproject.toml:14`, DEP002 ignore `:115-119`) — adopting it for the renderer would also retire that ignore; stdlib `logging.Formatter`/`structlog.processors.JSONRenderer` need nothing new.
- **Question:** Which renderer(s): text for the console + text for the file (no structured output at all — then why migrate?), text console + JSON file, or JSON both with a setting? Which serializer (stdlib `json`, `orjson`, structlog's `JSONRenderer`)? Default value for the setting?
- **Answer:** **Text console + JSON rotating file, serialized with `orjson`.** Using the already-declared-but-unused `orjson` also retires its `DEP002` ignore (`pyproject.toml:115-119`).
- **Date:** 2026-10-04 (rounds 1-5)
- **Status:** ANSWERED
- **Incorporated:** yes — amended REQ-001 + `pyproject.toml` DEP002 (see Q-21)

## Q-13 — Re-measure NFR-001/NFR-002 for the new backend, or inherit the budgets?
- **Step:** P.2 Interrogate
- **Why needed:** The budgets are executable gates (`test_nfr_001_setup_time_budget`, `test_nfr_002_decorator_overhead_budget`), and the logging budget was already relaxed once *because of loguru* (changelog v2, `docs/specs/logging.md:4`: < 10 ms → < 50 ms after CI observed 15.55 ms). Inheriting a budget measured on the removed backend is an unverified claim; the skill's self-consistency checklist flags exactly this ("performance budget vs. observability").
- **Question:** Measure on the host/CI before the amendment and state the new numbers with the measurement context (which sink, warm/cold, machine), or keep < 50 ms / < 1 ms and let Phase 5 discover a failure? Recommend measure-first (precedent: `docs/verification/amend-nfr-001-budgets.md`).
- **Answer:** **Measure first.** NFR-001 setup time and NFR-002 decorator overhead are measured on host/CI **before** the amendment, and the new numbers are stated with measurement context (sink, warm/cold, machine). Precedent: `docs/verification/amend-nfr-001-budgets.md`.
- **Date:** 2026-10-04 (rounds 1-5)
- **Status:** ANSWERED
- **Incorporated:** yes — amended NFR-001/NFR-002 budgets

## Q-14 — Which loguru-only capabilities must survive (colorize, backtrace, enqueue)?
- **Step:** P.2 Interrogate
- **Why needed:** REQ-001/AC-001 name them normatively; they have no 1:1 equivalent, so the amendment must either restate, implement, or drop each — otherwise AC-001 becomes untestable.
- **Context:** `logging.md:66` REQ-001 requires colorized console + backtrace + `enqueue` (loguru's async-safe queue); `_setup.py:87` sets `enqueue: True`. stdlib equivalents: color = a formatter (or nothing), backtrace = `exc_info` traceback (already the case), `enqueue` = `QueueHandler`/`logging.handlers.QueueListener`.
- **Question:** For each of the three: keep (implement the equivalent) or drop from the spec? Recommend: drop colorize (cosmetic, untested), restate backtrace as "exception records include the traceback frames without locals", keep async-safety as a capability ("logging never blocks the traced call" — already REQ-013/EDGE-002 in `logging-coverage.md`). Confirm.
- **Answer:** **Implement all three equivalents**: a colorizing formatter for the console, exception records carrying traceback frames (without locals, per Q-09), and a `QueueHandler`/`QueueListener` for loguru's `enqueue` async-safety. REQ-001/AC-001 stay testable.
- **Date:** 2026-10-04 (rounds 1-5)
- **Status:** ANSWERED
- **Incorporated:** yes — amended REQ-001/AC-001

## Q-15 — Rotation and file semantics: exact equivalence?
- **Step:** P.2 Interrogate
- **Why needed:** `log_max_bytes`/`log_backup_count` are user-facing settings whose meaning must not drift, and Windows file-locking behavior differs between loguru's enqueued sink and stdlib `RotatingFileHandler` (the repo runs on Windows and CI on Linux).
- **Context:** `_setup.py:90` passes `rotation=settings.log_max_bytes`; EDGE-001 requires the parent directory be created; `logging-coverage.md` EDGE-008 covers rotation reconfiguration; settings defaults `10485760` / backup count in `feature_settings.py:85-96`.
- **Question:** Confirm `RotatingFileHandler(maxBytes=log_max_bytes, backupCount=log_backup_count, encoding="utf-8")` is the required equivalence, and decide the Windows concurrency story (multi-process writes, pytest-xdist runs, reconfigure while a handle is open): is a `QueueHandler` wrapper required, and does a rotation-under-Windows edge become a new EDGE ID?
- **Answer:** **Exact equivalence + queue.** `RotatingFileHandler(maxBytes=log_max_bytes, backupCount=log_backup_count, encoding="utf-8")` plus a `QueueHandler` wrapper, and a **new EDGE ID** for rotation on Windows while a handle is open (repo runs Windows, CI Linux, pytest-xdist in play). EDGE-001 (parent dir created) survives.
- **Date:** 2026-10-04 (rounds 1-5)
- **Status:** ANSWERED
- **Incorporated:** yes — amended REQ-001 + new EDGE

## Q-16 — ADR supersession: which ADRs, and what must the new one record?
- **Step:** P.2 Interrogate
- **Why needed:** ADR-002 explicitly rejected structlog; reversing it without a superseding ADR leaves two contradictory decisions in `docs/decisions/`. Two more ADRs describe loguru mechanics.
- **Context:** Next free number is **ADR-081** (highest existing `ADR-080`), but `docs/todo/api-keys.md:64` already plans its ADRs "from ADR-081" — collision by merge order. ADR-035 (`:19,21,31`) documents `setup_logger` wiring with loguru sinks; ADR-060 (`:37`) reserves direct loguru for one-off statements.
- **Question:** **(A)** one new ADR (numbered at S2.1 by merge order) that supersedes ADR-002 and *also* absorbs the ADR-035/ADR-060 loguru wording — *recommended, fewest files*; **(B)** new ADR + status edits in ADR-035/ADR-060. And confirm the new ADR must contain the dependency evaluation required by `AGENTS.md` "Dependencies and Existing Packages" (including why stdlib-only was or was not enough) and ADR-002's Status → "Superseded by ADR-0xx".
- **Answer:** **(A) One superseding ADR**, numbered at S2.1 by merge order (not pre-reserved — `api-keys` also wants ADR-081), superseding ADR-002 and absorbing the loguru wording in ADR-035 and ADR-060. ADR-002's status becomes 'Superseded by ADR-0xx'; the new ADR carries the dependency evaluation `AGENTS.md` requires.
- **Date:** 2026-10-04 (rounds 1-5)
- **Status:** ANSWERED
- **Incorporated:** yes — new ADR + ADR-002/035/060 status

## Q-17 — Dependency evaluation: is removing loguru without adding structlog acceptable?
- **Step:** P.2 Interrogate
- **Why needed:** `AGENTS.md` requires dependency decisions to be traceable, and "no new dependency" is the lazier, smaller change — but the TODO's stated goal is specifically structlog, so dropping it is a scope decision for the user.
- **Context:** The TODO's acceptance signal says "`pyproject.toml` lists structlog and not loguru". stdlib-only satisfies every capability the amended spec would state (sinks, rotation, interception, structured fields via `extra`/`LoggerAdapter`), removes a dependency, and keeps `deptry` green with no new ignore.
- **Question:** If migrating: is stdlib-only acceptable (goal restated as "structured records behind the existing API", not "structlog"), or is structlog specifically required (then justify what it buys over stdlib `Formatter` + `extra`, and expect a P.5 smoke-test gate)?
- **Answer:** **Closed by Q-03 = (B)** — structlog specifically is required; stdlib-only was offered and rejected. The P.5 Dependency Smoke-Test therefore applies, and the new ADR must justify structlog over stdlib `Formatter` + `extra`.
- **Date:** 2026-10-04 (rounds 1-5)
- **Status:** ANSWERED
- **Incorporated:** yes — decision Q-03; P.5 smoke test

## Q-18 — Confirm the 17 test files are re-derived from the amended spec, never edited to fit the code
- **Step:** P.2 Interrogate
- **Why needed:** `AGENTS.md:726` ("Tests are the contract … never by weakening, removing, or 'fixing' the test") and the prohibitions list forbid editing acceptance tests to match an implementation; a backend swap is precisely the situation where that rule bites hardest, and the user must authorize the *deletion* of tests that encode removed IDs.
- **Context:** 17 test files, 43 loguru matches, 2 390 LOC, 75 test functions; `test_direct_loguru_kept.py` exists only for REQ-010; `test_logging_sink_ownership.py` for item E; `tests/conftest.py` holds the session setup and the `_stdlib_root_logging_restored` autouse fixture. Baseline: 727 passed, 1 skipped (`docs/verification/traceability.md:19`).
- **Question:** Confirm the Phase 3 plan: amendment merged → tests re-derived from the amended IDs (RED against the old code) → implement → GREEN, with old loguru-specific tests deleted **only** where their ID was amended away, and each deletion named in the verification record. Do you authorize deleting/renaming `test_direct_loguru_kept.py` if REQ-010 is amended (Q-05)? Any test you consider untouchable?
- **Answer:** **Authorized, per-ID.** Amendment merged → tests re-derived from the amended IDs (RED against the old code) → implement → GREEN. loguru-specific tests are deleted **only** where their ID was amended away, each deletion named in the verification record — including `tests/acceptance/logging_coverage/test_direct_loguru_kept.py` with REQ-010. No test is weakened.
- **Date:** 2026-10-04 (rounds 1-5)
- **Status:** ANSWERED
- **Incorporated:** yes — Phase 3 plan + verification record

## Q-19 — Amendment PR sequencing: how many PRs, and in what order?
- **Step:** P.2 Interrogate
- **Why needed:** `AGENTS.md:1073` + the Spec Amendment Workflow require the spec PR merged **before** implementation resumes, and forbid smuggling the amendment into the implementation PR. This sets the gate sequence and the number of human merges.
- **Context:** Precedent: `amend-nfr-001-budgets` was a separate amendment PR for a single ID (`docs/verification/amend-nfr-001-budgets.md`). Option B touches 4 specs and 20+ IDs.
- **Question:** **(A)** amendment PR (4 specs + new ADR) → merge → implementation PR → merge (2 human merges, recommended); **(B)** amendment PR, then two implementation PRs (feature swap first, then the 39 direct-call migrations per Q-05); **(C)** one PR with amendment+code (violates the rule — needs an explicit exception). Which?
- **Answer:** **(A) Two PRs:** the amendment PR (4 specs + the new ADR) merges first, then one implementation PR. Two human merges; the amendment is never smuggled into the code PR.
- **Date:** 2026-10-04 (rounds 1-5)
- **Status:** ANSWERED
- **Incorporated:** yes — TODO Prep log / gate sequence

## Q-20 — Ordering against `api-keys`, `notifications`, and `tenacity-rich-cachetools`
- **Step:** P.2 Interrogate
- **Why needed:** Three planned changes consume the logging backend; whichever way Q-01 goes, the decision must be recorded so they do not build on a losing assumption (`tenacity-rich-cachetools.md:55` says exactly that).
- **Context:** `api-keys` and `notifications` are WAITING (their own PRs blocked on human merge); `tenacity-rich-cachetools` declares `Depends on: decision on docs/todo/structlog-logging.md` for its `rich` item (`:13`). No worktrees/branches/open PRs exist, so there is no in-flight code to rebase.
- **Question:** Must the backend decision land **before** `api-keys`/`notifications` implement (so their new code uses the winning backend), or is the tracing policy (ADR-060, backend-agnostic) sufficient and the swap can happen after them? And does `tenacity-rich-cachetools`'s dependency clear the moment you answer Q-01 (recommended: yes — remove the `Depends on:` at P.3)?
- **Answer:** **The swap lands first.** `api-keys` and `notifications` implement after it so their new code uses the winning backend from day one. `tenacity-rich-cachetools`'s `Depends on: decision on docs/todo/structlog-logging.md` **clears now** and is removed at P.3.
- **Date:** 2026-10-04 (rounds 1-5)
- **Status:** ANSWERED
- **Incorporated:** yes — TODO Depends on (both changes)

## Q-21 — `pyproject.toml` / `uv.lock` churn and conflict order with `python-3.15` and `pyproject-tooling-gaps`
- **Step:** P.2 Interrogate
- **Why needed:** Three prepared changes edit the same file; merge order decides who rebases, and deptry/CI gates (`dependencies` job, pre-commit hook) react to the dependency swap.
- **Context:** `python-3.15` (PREPARING) raises `requires-python` and 11 CI pins; `pyproject-tooling-gaps` (PREPARING) touches `[tool.deptry]`/`quality_check`; this change swaps `loguru>=0.7.3` (`pyproject.toml:12`) and possibly adds `structlog`, plus the DEP002 ignore list at `:115-119`.
- **Question:** Any required ordering (e.g. land the dependency swap before the 3.15 bump so the lock resolves once)? Should the change also retire the `orjson` DEP002 ignore if Q-12 uses it, or is that `pyproject-tooling-gaps`' scope (avoid double work)?
- **Answer:** **After `pyproject-tooling-gaps`.** That change (now REFACTOR) owns `[tool.deptry]` and `quality_check`, so this change rebases on it; **this change owns the `orjson` DEP002 retirement** because Q-12 makes `orjson` a real import. `python-3.15` is DROPPED, so only `python-3.15-upgrade` (trigger-gated) remains in the pin set. `security-changelog-license` adds `license`/`authors` and must merge before `pyproject-tooling-gaps`.
- **Date:** 2026-10-04 (rounds 1-5)
- **Status:** ANSWERED
- **Incorporated:** yes — TODO Depends on + merge order

## Q-22 — Version bump level
- **Step:** P.2 Interrogate
- **Why needed:** `AGENTS.md` Versioning: CROSS-CUTTING → `minor`, `major` if breaking. Whether a log-format change or a new export counts as breaking is a user decision, not an agent's.
- **Context:** Option A (DOCS/CHORE) → no bump. Option B with a byte-compatible public API (Q-10) → `minor`.
- **Question:** If migrating: `minor` (API unchanged, format changed) or `major` (log format is part of the observable contract)? Confirm the mapping for Option A = no bump.
- **Answer:** **major** — follows from Q-10 = breaking redesign (public API and decorator parameter surface change). CROSS-CUTTING normally bumps `minor`; `major` is taken because the surface breaks.
- **Date:** 2026-10-04 (rounds 1-5)
- **Status:** ANSWERED
- **Incorporated:** yes — Phase 6 bump level

## Q-23 — Update the guidance files in the same change (AGENTS.md + skill), regardless of Q-01?
- **Step:** P.2 Interrogate
- **Why needed:** `AGENTS.md:767,769` also mandate loguru ("feature code may use loguru's `logger` directly"), so the contradiction exists in three places, and the skill text is wrong *today* whichever backend wins eventually.
- **Context:** Files: `AGENTS.md:767,769`; `.agents/skills/python-best-practices/SKILL.md:16`; `references/modern-python.md:85`; `references/errors-and-resources.md:17,43` (structlog examples). `AGENTS.md` is normative for agents, not user docs.
- **Question:** Should the guidance edits be part of this change in all cases (Option A: they *are* the change; Option B: they follow the new backend), and is `AGENTS.md` in scope for the wording fix, or only the skill files? Recommend: yes, all four locations, one chore.
- **Answer:** **Yes — all four locations** in the implementation PR: `AGENTS.md:767,769`, `.agents/skills/python-best-practices/SKILL.md:16`, `references/modern-python.md:85`, `references/errors-and-resources.md:17,43`.
- **Date:** 2026-10-04 (rounds 1-5)
- **Status:** ANSWERED
- **Incorporated:** yes — TODO In scope

## Q-24 — Keep the hand-written `@logged`/`@logged_class` machinery, or rebuild it on the new backend's binding features?
- **Step:** P.2 Interrogate
- **Why needed:** It is the largest single file at risk (`_decorator.py`, 231 LOC) and the difference between "swap the emit call" and "rewrite the decorator" is most of Option B's cost and risk.
- **Context:** The decorator owns entry/exit/elapsed-ms/exception records, `slow_threshold_ms` escalation, `include_args` truncation, `context_getter`, `depth`, sync+async support, and `__logged_class__` marking (asserted by `logging-coverage.md` REQ-002..008, INV-001..004).
- **Question:** **(A)** minimal — keep the decorator logic byte-for-byte, change only where the record goes (recommended; keeps INV-001..004 and all 75 tests meaningful); **(B)** adopt the backend's own function-tracing/binding machinery (smaller code, but re-derives the whole coverage spec's IDs and risks behavior drift). Which?
- **Answer:** **Superseded by the Q-10/Q-24 tie-break: full rewrite.** The decorator is rebuilt on structlog's function-tracing/binding machinery rather than kept byte-for-byte. Accepted cost: `logging-coverage.md` REQ-002..008 and INV-001..004 are re-derived and behavior drift is the main risk, mitigated by re-deriving tests from the amended IDs before implementing.
- **Date:** 2026-10-04 (rounds 1-5)
- **Status:** ANSWERED
- **Incorporated:** yes — decision Q-10 tie-break; amended coverage IDs

## Q-25 — Are the test *helpers* and `conftest.py` part of the contract, or freely editable infrastructure?
- **Step:** P.2 Interrogate
- **Why needed:** The prohibition on changing tests applies to assertions that encode the contract; the swap cannot work at all without touching `tests/conftest.py` (4 loguru refs), `tests/logging_test_helpers.py` (5), `tests/logging_coverage_test_helpers.py` (2), `tests/settings_test_helpers.py` (1) — the user should confirm the boundary before Phase 3/4 argue about it.
- **Context:** `tests/conftest.py` builds the session `Settings`, registers `logging.*`, and holds the autouse `_stdlib_root_logging_restored` fixture (issue `main-ci-green` item I); `logging_test_helpers.run_python()` runs subprocess-isolated logging checks.
- **Question:** Confirm: fixtures/helpers may be adapted to the new backend as long as every assertion in a test function traces to an amended ID and none is weakened; and confirm the autouse stdlib-root-restore fixture stays (it guards alembic's `fileConfig`, see Q-07).
- **Answer:** **Helpers are adaptable.** `tests/conftest.py` and `logging_test_helpers.py` / `logging_coverage_test_helpers.py` / `settings_test_helpers.py` may be adapted to the new backend provided every assertion in a test function traces to an amended ID and none is weakened; the autouse `_stdlib_root_logging_restored` fixture stays (it guards alembic's `fileConfig`, Q-07).
- **Date:** 2026-10-04 (rounds 1-5)
- **Status:** ANSWERED
- **Incorporated:** yes — Phase 3/4 boundary + verification record

## Late questions (Phases 2–6)

<questions discovered after the change entered the workflow; same entry format, Step field set to the step that found it>
