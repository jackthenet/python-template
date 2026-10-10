# map-default-drop-shift — Triage Record (ISSUE)

- **Change:** `map-default-drop-shift` · **Type:** **ISSUE** (classified at P.1, first matching criterion: "fixes a deviation from approved spec behavior") — **with a Spec Amendment PR (PR A) first**, the user's recorded decision at Q-1.
- **Defect against:** the approved spec **`docs/specs/structure-map.md`** (v1, merged; `## 15. Changelog` at `:631`). This change authors **no** spec; it amends an existing one (Spec Amendment Workflow) and then fixes the code.
- **Branch / worktree:** `issue/map-default-drop-shift` @ base `7299108` (`main`, `pyproject.toml:4` version `1.1.0`), worktree `../python-template_kopie-worktrees/issue/map-default-drop-shift` — created at **P.4** from `main` (git skill, "Create change worktree (P.4)"), so the branch carries the TODO file and the answered question file as of P.3.
- **Date:** 2026-10-10 (all commands below were re-run in this worktree at this commit; nothing here is quoted from the TODO unchecked).
- **Phase Matrix for this type:** Phase P → triage record (this file) · Phase 1–2 skipped · **Phase 3** reproduction tests → RED · **Phase 4** minimal fix → GREEN · **Phase 5** targeted + smoke (**light tier**, §6) · **Phase 6** review + PR + `patch` bump (`1.1.0 → 1.1.1`, AGENTS.md Versioning).
- **P.5 does not run for ISSUE** (AGENTS.md, Phase P table: "P.5 Verify self-consistency — **FEATURE/CROSS-CUTTING only**"). **The READY gate for this change is this verified triage record** plus the fully answered question file; the orchestrator advances the TODO to `Status: READY` on `main` after verifying this handoff.
- **Two-PR shape (Q-1/Q-4/Q-17):** **PR A** = Spec Amendment to `docs/specs/structure-map.md` only, **no version bump**, merged **before Phase 3 starts**. **PR B** = this change (`issue/map-default-drop-shift`): reproduction tests → fix → regenerated `STRUCTURE.md` → `patch` bump.

## Phase P record

| Step | Date | Result |
|---|---|---|
| P.1 Frame (orchestrator, `main`) | 2026-10-09 | `docs/todo/map-default-drop-shift.md` + `docs/questions/map-default-drop-shift.md` created on `main`; type ISSUE; value triage recorded |
| P.2 Interrogate | 2026-10-09 | 18 questions recorded in one `BLOCKED-USER` batch |
| P.3 Answer (orchestrator ⏸, `main`) | 2026-10-09 | **19/19 ANSWERED + incorporated** (4 rounds; Q-19 derived from Q-15); value-triage decision **IMPLEMENT** (3/5) recorded → P.4 gate open |
| P.4 Draft triage + create branch/worktree | 2026-10-10 | **this file** — worktree + branch created from `main` `7299108`; every claim re-verified by executed commands in this worktree (§3) |
| P.5 Self-consistency | n/a | ISSUE — P.5 runs for FEATURE/CROSS-CUTTING only |

---

## 1. Classification rationale (and why an amendment comes first)

ISSUE, not FEATURE: the map already promises a signature rendering (REQ-014/AC-014) and the shipped artifact renders a signature that misrepresents the source function — a deviation from specified behavior at the artifact level. It is **not a plain ISSUE** either: the *required* rendering (which parameter keeps which default after an over-long default is abbreviated) is **not stated anywhere in the approved spec** (§3.4), so AGENTS.md ISSUE item 13 and the Spec Amendment Workflow apply — the wording is written first (PR A), the code follows (PR B). It is not a FEATURE (no new capability: the map's signature line already exists) and not CROSS-CUTTING (one artifact, one generator, no `src/` feature).

## 2. Affected requirements and acceptance criteria

All IDs are from the existing approved spec **`docs/specs/structure-map.md`** (line numbers verified at `7299108`).

| ID | Spec line | Required behavior **as written today** |
|---|---|---|
| **REQ-014** | `:270`, signature bullet `:287-289` | "signatures are produced with `ast.unparse` for parameters, annotations and return annotation, so formatting drift in the source cannot change the map; **a parameter default is included only when its unparsed text is ≤ 20 characters**." |
| **AC-014** | `:424` | "…**Then** each is rendered exactly once, in the REQ-014 group order…, in the stated line form, **And** the signature text equals the `ast.unparse` rendering, **And** a parameter default of ≤ 20 characters is shown **while a longer one is omitted**." |
| **REQ-021** | `:339` | `STRUCTURE.md` is committed, produced only by running the generator, "its content is the fresh render for the commit it is recorded at" — **forces the regeneration in PR B** |
| **AC-021** | `:431` | "**Given** the `STRUCTURE.md` committed by this change, **When** `uv run python scripts/make_map.py --check` runs at that commit, **Then** it exits `0`" — the freshness gate PR B must leave green |
| **REQ-019 / INV-001** | `:325` / `:443` | Determinism of the render — must keep holding (the placeholder rule is deterministic and idempotent; verified §5) |
| **INV-006** | `:448` | Hook cleanliness of the generated file — unaffected (`…` is mid-line; verified §5) |
| **NFR-002** | `:476` | Generated map ≤ 2 000 lines — unaffected: the fix changes line **content**, not line count (measured: 1 941 → 1 941, §5) |
| **NFR-005** | `:479` | "`scripts/` is **not** analyzed by complexipy" — confirmed: CI runs `uv run complexipy src tests --max-complexity-allowed 15` (`.github/workflows/quality.yml:146`); the extension to `scripts/` is `chore/complexipy-scripts`, not this change |
| **REQ-023 / AC-023** | `:344` / `:433` | The local `structure-map-check` hook (`files: \.py$`, check-only) — it is why PR B must regenerate in the same commit as the `.py` change (AGENTS.md "Structure Map") |

**IDs to be added by PR A** (per Q-9; they do not exist in the spec today — `grep -n "INV-007\|EDGE-017" docs/specs/structure-map.md` returns nothing):

| ID | Section | Status |
|---|---|---|
| **INV-007** (signature fidelity) | §8 Invariants (`:439`, after INV-006 at `:448`) | **to be added by PR A** |
| **EDGE-017** (over-long default in a positional / positional-only / keyword-only slot) | §9 Edge Cases (`:450`, after EDGE-016 at `:469`) | **to be added by PR A** |

Both IDs are **already defined by other specs** (`settings.md`, `file-management.md`, `authentication.md`, `search.md`) and already have matrix rows elsewhere — the matrix is a bare-ID namespace (structure-map's own §12 and `docs/verification/structure-map.md` finding 2), which is why PR B's rows must name the change inside the Status cell (Q-14).

---

## 3. Defect confirmation (observed vs required)

Everything below was executed in this worktree at `7299108`. Line numbers in `STRUCTURE.md` are given as observed **now** and drift with any regeneration — locate by content, not by number (finding F-11).

### 3.1 The generator drops over-long defaults from the parameter list

`scripts/make_map.py` (anchors verified at this commit; re-find by content):

- `_DEFAULT_MAX_CHARS = 20` — `:74`
- `_drop_long_defaults(args)` — `:375`, the two filters at `:382-385`:

  ```python
  args.defaults = [d for d in args.defaults if len(ast.unparse(d)) <= _DEFAULT_MAX_CHARS]
  args.kw_defaults = [
      d if d is not None and len(ast.unparse(d)) <= _DEFAULT_MAX_CHARS else None for d in args.kw_defaults
  ]
  ```

- `_signature(node)` — `:388`, calls `_drop_long_defaults(node.args)` at `:396` before `ast.unparse(node.args)`.

A positional default is removed **from the list**, so the remaining defaults shift onto earlier parameters; a keyword-only default is replaced by `None`, which `ast.unparse` renders as a parameter **with no default at all**. The generator's own docstring for `_drop_long_defaults` states both effects. That is the mechanism; the spec never sanctions the effect (§3.4).

### 3.2 Witness 1 — the positional shift (the TODO's witness)

Source, `tests/mail_test_helpers.py:70-75` — four positional parameters, defaults on all four, `body_html`'s default is 21 characters:

```python
def simple_template(
    name: str = "test",
    subject: str = "Test {{who}}",
    body_html: str = "<p>Test {{who}}</p>",
    body_text: str = "Test {{who}}",
) -> EmailTemplate:
```

Rendered in the committed map at `STRUCTURE.md:1816` (observed):

```text
- def `simple_template(name: str, subject: str='test', body_html: str='Test {{who}}', body_text: str='Test {{who}}') -> EmailTemplate`: Build an EmailTemplate for a test.
```

**Observed:** `name` reads as **required**; `subject` carries `name`'s default (`'test'`); `body_html` carries `subject`'s default; `body_text` carries `body_html`'s default. Every default in the line is attached to the wrong parameter, and the line is a valid-looking signature that no reader can distinguish from correct.

**Required (Q-2, normative after PR A):** `simple_template(name: str='test', subject: str='Test {{who}}', body_html: str=…, body_text: str='Test {{who}}')` — the over-long default is abbreviated **in its own slot**, so names, order and the defaults-set are preserved.

**Verified by rendering, not by reading:** applying the placeholder rule to the same source produces exactly the required line (probe in §5.2).

### 3.3 Witness 2 — keyword-only defaults rendered as required parameters

The same rule damages the map wherever a keyword-only default is over-long. A read-only AST scan of **all 342 tracked `.py` modules in the four code dirs** the map renders (`src/`, `tests/`, `scripts/`, `migrations/`) found **exactly 8** over-long defaults — 1 positional, 7 keyword-only (a narrower Packages-scope scan of 119 modules gives the same 8):

| Source | Function | Kind | Parameters (default length) |
|---|---|---|---|
| `src/backend/authentication/service.py:108` | `AuthService.__init__` | keyword-only | `reset_token_ttl` (21), `lockout_duration` (21), `origin` (23) |
| `tests/authentication_test_helpers.py:177` | `build_auth_service` | keyword-only | `lockout_duration` (21), `reset_token_ttl` (21) |
| `tests/authentication_test_helpers.py:205` | `build_memory_auth_service` | keyword-only | `lockout_duration` (21), `reset_token_ttl` (21) |
| `tests/mail_test_helpers.py:70` | `simple_template` | positional | `body_html` (21) |

All three keyword-only cases are live in the committed map — `STRUCTURE.md:686` (`AuthService.__init__`), `:1675` and `:1676` (the two helpers). Observed at `:686` (excerpt):

```text
…, session_ttl: timedelta=timedelta(days=7), reset_token_ttl: timedelta, max_failed_attempts: int=5, lockout_duration: timedelta, rp_id: str='localhost', rp_name: str='Python Template', origin: str, permission_service: PermissionChecker | None=None) -> None
```

**Observed:** `reset_token_ttl`, `lockout_duration` and `origin` render with **no default**, so a reader of the map concludes they are **required** keyword arguments — the opposite of the source, where all three are optional with defaults. AGENTS.md documents those very parameters as optional keyword arguments with defaults (`max_failed_attempts` (default 5), `lockout_duration` (default 15 minutes), `rp_id`/`rp_name`/`origin`), so the map contradicts the published contract.

**Required (Q-6/Q-7, uniform rule):** `reset_token_ttl: timedelta=…, lockout_duration: timedelta=…, origin: str=…`.

Both witnesses are required by Q-10; both are live in the committed artifact, so the defect is not hypothetical.

### 3.4 Why the approved spec does not settle it (the Spec Amendment stop)

AGENTS.md ISSUE item 13: *if the fix requires behavior the spec does not state, STOP — Spec Amendment PR or reclassify as FEATURE.* The current wording **prescribes the defective behavior** and is silent on the consequence:

- REQ-014 (`:288-289`): "a parameter default is included **only when** its unparsed text is ≤ 20 characters" — dropping is literally what the code does.
- AC-014 (`:424`): "a parameter default of ≤ 20 characters is shown **while a longer one is omitted**" — "omitted" is the current, shifting behavior, and the existing unit witnesses assert exactly that (`tests/unit/test_make_map.py`, `_AC014_DEFAULTS` at `:675` and the `_AC014_LINES` expectations at `:654`).

Nothing in REQ-014, AC-014, INV-001…INV-006 or EDGE-001…EDGE-016 states that the rendered parameter list must keep the parameter in its slot, must preserve which parameters have defaults, or must stay grammatically coherent. The fix therefore **changes specified behavior** (the map's rendered text changes for 4 lines), which the approved spec does not currently authorize. Per the Escalation Rules this is not a reclassification (still ISSUE: no new capability), so the route is the **Spec Amendment Workflow**: PR A amends REQ-014/AC-014 and adds INV-007 + EDGE-017, merges first, then PR B implements (§7).

The existing AC-014 witnesses assert the old behavior, so they **must** be re-derived from the amended spec — authorized by Q-11, and never weakened: the re-derived assertions are strictly stronger (they pin the placeholder **and** the parameter/defaults correspondence, §4.4).

### 3.5 Gate state observed on `main` (baseline, not caused by this change)

| Command (run in this worktree) | Result |
|---|---|
| `uv run python scripts/make_map.py --check` | **exit 1** — `STRUCTURE.md is out of date — run uv run python scripts/make_map.py` |
| `uv run pytest tests/acceptance/test_structure_map.py -q -p no:randomly` | **1 failed, 30 passed** — the failure is `test_ac_021_committed_map_matches_fresh_render` |
| `uv run pytest tests/unit/test_make_map.py tests/property/test_structure_map.py -q` | **24 passed** |

The `--check` failure and the AC-021 failure are **pre-existing on `main`** and are a single line: committed `docs/ · 223 files (process record)` (`STRUCTURE.md:452`) vs a fresh render of `224` — the map was last regenerated at `8ec73ee`, when `git ls-files docs` returned 223; `main` now tracks 224 because the Phase P planning records were committed directly to `main`, and no CI job runs `--check` (REQ-023/REQ-026 keep it local). PR B's regeneration absorbs it (finding F-01/F-02); a second, host-dependent cause is recorded as F-03.

---

## 4. Reproduction plan (Phase 3)

Four witnesses, all required by Q-10 (both symptoms) and Q-9 (the property test is mandatory because PR A adds INV-007). All follow the **established pattern of this test suite**: the generator is driven as a **subprocess** over a throwaway tree, never imported, so its absence is a test failure and not a collection error (a setup error is not a valid RED) — stated in the headers of both `tests/unit/test_make_map.py` and `tests/property/test_structure_map.py`.

### 4.1 Unit witness — the new EDGE-017 rule (RED on the current generator)

`tests/unit/test_make_map.py::test_edge_017_over_long_default_keeps_its_slot`

A synthetic module written into `src/edge017.py` under `tmp_path` (the `_t004_tree` helper the AC-014 witness at `:937` already uses), covering every slot the amended EDGE-017 names, including the two shapes that do not occur in the tree today (F-12):

```python
def shift(a: int = 1, b: str = "xy", c: list[int] = [1, 2, 3, 4, 5, 6, 7]) -> None: ...
def only(pool: list[int] = [1, 2, 3, 4, 5, 6, 7]) -> None: ...
def posonly(a: int = 1, b: str = "0123456789abcdefghij0", /) -> None: ...
def keys(*, need: int, k: int = 1, m: str = "0123456789abcdefghij0") -> None: ...
def edge(exact: str = "0123456789abcdefgh") -> None: ...
```

Assertions on the rendered `- def` lines (each is RED today):

| Case | Required rendering | What it pins |
|---|---|---|
| `shift` | `shift(a: int=1, b: str='xy', c: list[int]=…) -> None` | no shift: the two short defaults stay on their own parameters |
| `only` | `only(pool: list[int]=…) -> None` | the sole default of a function keeps its slot (the parameter is not rendered as required) |
| `posonly` | `posonly(a: int=1, b: str=…, /) -> None` | positional-only slot, and the `/` marker survives |
| `keys` | `keys(*, need: int, k: int=1, m: str=…) -> None` | keyword-only slot **and** a genuinely required keyword-only parameter (`need`, which must come first — a default may not precede it in Python) stays default-free: the F-08 trap |
| `edge` | `edge(exact: str='0123456789abcdefgh') -> None` | the `_DEFAULT_MAX_CHARS = 20` boundary is unchanged (Q-8): exactly 20 characters renders verbatim |

Both the fixture and every expected string above were **measured**, not assumed: the module parses (valid test data, AGENTS.md Phase 3 item 6), and the current generator renders it as `shift(a: int, b: str=1, c: list[int]='xy')`, `only(pool: list[int])`, `posonly(a: int, b: str=1, /)`, `keys(*, need: int, k: int=1, m: str)`, `edge(exact: str='0123456789abcdefgh')` — the shift is visible in the first three, and the placeholder rule produces exactly the required column.

### 4.2 Acceptance witness — the committed map must not misrepresent the source

`tests/acceptance/test_structure_map.py::test_ac_014_committed_map_renders_over_long_default_in_place`

Reads the committed `STRUCTURE.md` (module constant `_MAP_FILE`) — the same pattern `test_ac_021_committed_map_matches_fresh_render` (`:1468`) and `test_nfr_002_map_line_budget` (`:1484`) already use, because REQ-021/AC-021 make the committed artifact itself the object under test. It locates the two live witnesses **by content** (never by line number, F-11) and asserts:

- the `simple_template` line is `- def \`simple_template(name: str='test', subject: str='Test {{who}}', body_html: str=…, body_text: str='Test {{who}}') -> EmailTemplate\`: …` — i.e. `name` is not rendered required and no default sits on the wrong parameter;
- the `AuthService.__init__` line contains `reset_token_ttl: timedelta=…`, `lockout_duration: timedelta=…` and `origin: str=…`, and still contains `session_ttl: timedelta=timedelta(days=7)` and `max_failed_attempts: int=5` unharmed.

It is RED against the map committed at `7299108` and goes GREEN only when Phase 4 regenerates the map in the same commit as the generator fix (REQ-021/AC-021).

### 4.3 Property witness — INV-007 (mandatory, Q-9)

`tests/property/test_structure_map.py::test_inv_007_signature_fidelity_survives_default_abbreviation`

Name is deliberately distinct: `test_inv_007_*` already exists in other features' property files (`test_inv_007_key_containment`, `test_inv_007_load_scope_valid`) because the matrix is a bare-ID namespace (§2).

Hypothesis generates a module of functions whose parameters vary over: name, annotation, default length (short / exactly 20 / over-long), and slot (positional-only, positional, keyword-only, keyword-only **without** a default). Each example writes the module into a fresh `TemporaryDirectory` git tree (the file's existing reason for a fresh tree per example), runs the generator with `--out`, extracts the `- def` lines, and asserts the INV-007 fidelity property against the source AST:

1. the rendered parameter **names in order** equal the source's;
2. the **set of parameters that carry a default** equals the source's (this is the clause the defect breaks, and the clause F-08's naive fix would break in the other direction);
3. the positional-only / positional / keyword-only **split** is preserved (`/` and `*` markers present as in the source);
4. every over-long default renders exactly as `…`, every default of ≤ 20 characters renders verbatim;
5. the rendered parameter list, **with every `…` replaced by the literal `...`**, parses with `ast.parse` and re-unparses to the source parameter list with the over-long defaults replaced by `...`.

Clause 5 is the only workable form of "the signature still parses": `…` in a default position is a `SyntaxError` (F-06), so the invariant is stated over the placeholder-substituted text, and PR A's wording must say so.

### 4.4 Re-derived existing AC-014 witnesses (authorized by Q-11, never weakened)

`tests/unit/test_make_map.py::test_ac_014_symbol_inventory_and_unparsed_signatures` (`:937`) and its fixtures `_AC014_MODULE` (`:584`), `_AC014_LINES` (`:654`), `_AC014_DEFAULTS` (`:675`). The fixture already carries three over-long defaults, so **no fixture source change is needed** — only the expectations, which today assert the old dropping behavior:

| Fixture default | Today's expectation | Re-derived expectation |
|---|---|---|
| `pool: list[int] = [1, 2, 3, 4, 5, 6, 7]` (21, positional, sole default) | `- def \`items(pool: list[int]) -> None\`` | `- def \`items(pool: list[int]=…) -> None\`` |
| `data: dict[str, int] = {"alpha": 1, "beta": 2}` (23, keyword-only) | `data: dict[str, int]` (no default) | `data: dict[str, int]=…` |
| `over: str = "0123456789abcdefghi"` (21, keyword-only) | `over: str` (no default) | `over: str=…` |
| `exact: str = "0123456789abcdefgh"` (20) | shown verbatim | **unchanged** (Q-8) |
| `step: int = 4`, `b: str = "xy"` | shown verbatim | **unchanged** |

`_AC014_DEFAULTS` keeps every existing needle (the literal over-long default text must still be absent — that assertion is unchanged and still meaningful) and **adds** positive needles `pool: list[int]=…`, `data: dict[str, int]=…`, `over: str=…`: strictly more assertions than before, never fewer. The comment block at `:649-653` ("the 21-character defaults of `data`/`over`/`pool` are omitted") is corrected to the placeholder rule. Spec §11 gains the two new rows (§7.5); the existing AC-014 row (`:526`) keeps its function name because the witness is re-derived in place, not renamed.

**Correction to Q-11's premise (F-05):** the question file states the `resize(...)` line is unaffected because "`step`/`exact` defaults are both ≤ 20 chars". True for those two, but `resize` also carries the over-long keyword-only defaults `data` (23) and `over` (21), so under the uniform rule (Q-7) **its rendered line does change**. The authorized witness-edit list must include it.

### 4.5 RED / GREEN commands (targeted — AGENTS.md "Targeted GREEN")

```text
red_command:   uv run pytest tests/unit/test_make_map.py::test_edge_017_over_long_default_keeps_its_slot
                          tests/unit/test_make_map.py::test_ac_014_symbol_inventory_and_unparsed_signatures
                          tests/property/test_structure_map.py::test_inv_007_signature_fidelity_survives_default_abbreviation
                          tests/acceptance/test_structure_map.py::test_ac_014_committed_map_renders_over_long_default_in_place -v
green_command: the same four node ids, plus
               uv run python scripts/make_map.py && uv run python scripts/make_map.py --check   # exit 0
               uv run pytest tests/unit/test_make_map.py tests/property/test_structure_map.py tests/acceptance/test_structure_map.py -q
```

**Test-data validity (AGENTS.md Phase 3 item 6).** Every fixture above is a syntactically valid module the generator parses; the witnesses fail on **behavior** (rendered text), never on a construction error. The RED run must show assertion failures on the rendered signature text — if it shows a `SyntaxError`/collection error, the test data is wrong and RED is not valid.

### 4.6 Traceability rows (Phase 3 writes RED, Phase 5 writes GREEN)

Rows for **REQ-014/AC-014** (updated in place, with this change named inside the Status cell per Q-129 convention B) and new rows for **INV-007** and **EDGE-017** go into `docs/verification/traceability.md` **in PR B**, never in PR A — `scripts/check_traceability.py` rule (3) fails any row citing a backticked test function that does not exist under `tests/`, and those functions do not exist until Phase 3 (F-09).

---

## 5. Fix scope (Phase 4)

### 5.1 The one implementation change

`scripts/make_map.py::_drop_long_defaults` (`:375`) — the two filters at `:382-385` become a **substitution** instead of a deletion, uniformly over both lists:

```python
args.defaults = [d if len(ast.unparse(d)) <= _DEFAULT_MAX_CHARS else _PLACEHOLDER for d in args.defaults]
args.kw_defaults = [
    None if d is None else (d if len(ast.unparse(d)) <= _DEFAULT_MAX_CHARS else _PLACEHOLDER)
    for d in args.kw_defaults
]
```

Two clauses are load-bearing:

- **`None` stays `None`.** `ast.arguments.kw_defaults` is positionally aligned with `kwonlyargs` and holds `None` for a keyword-only parameter that has **no** default. A rule that substitutes every entry renders required parameters as optional (measured in F-08: a first attempt added `=…` to `username`, `password`, `use_tls`, `timeout` in `SmtpTransportImpl.__init__`, `STRUCTURE.md:1039`, which are required in the source). The §4.1 `keys(*, need: int, …)` case is the witness that locks this.
- **`_DEFAULT_MAX_CHARS = 20` is untouched** (Q-8). Only the treatment of a default that exceeds it changes.

The function's docstring (which currently describes the shifting/`None` effects as intended) is corrected to state the placeholder rule and why dropping is wrong.

### 5.2 How the `…` placeholder is rendered (verified probe)

`ast.unparse` cannot produce `…` from a real AST node — `ast.unparse(ast.Constant(...))` renders `...`, not `…` (F-07). Verified in this worktree: `ast.unparse(ast.Name(id="…"))` renders `…`, and because the placeholder is 1 character it survives a second pass of `_drop_long_defaults` unchanged, so the rule is **idempotent** and INV-001 (determinism, `:443`) is unaffected. The concrete injection mechanism (sentinel node vs. string-level substitution on the rendered signature) is a Phase 4 decision; it introduces no new dependency and no new pattern, so **no ADR** (Phase 2 is skipped for ISSUE; AGENTS.md ADR threshold not met).

Probe (read-only, scratch copy of the generator outside the repository, run against this worktree as `--root`):

| Subject | Today (committed map) | With the placeholder rule |
|---|---|---|
| `simple_template` | `simple_template(name: str, subject: str='test', body_html: str='Test {{who}}', body_text: str='Test {{who}}')` | `simple_template(name: str='test', subject: str='Test {{who}}', body_html: str=…, body_text: str='Test {{who}}')` |
| `_AC014_MODULE` `items` | `items(pool: list[int])` | `items(pool: list[int]=…)` |
| `_AC014_MODULE` `resize` | `resize(self, size: int, *, step: int=4, data: dict[str, int], exact: str='0123456789abcdefgh', over: str)` | `resize(self, size: int, *, step: int=4, data: dict[str, int]=…, exact: str='0123456789abcdefgh', over: str=…)` |

### 5.3 Regenerated `STRUCTURE.md` (required by REQ-021/AC-021, same commit as the `.py` change per REQ-023)

Measured diff of the placeholder-rule render against the map committed at `7299108` — **4 signature lines** change from the fix, plus 1 line from the pre-existing staleness:

| Line (as observed now) | Content |
|---|---|
| `:452` | `docs/ · 223 files (process record)` → `224 files` — **pre-existing staleness, not this fix** (F-01) |
| `:686` | `AuthService.__init__` — `reset_token_ttl`, `lockout_duration`, `origin` gain `=…` |
| `:1675` | `build_auth_service` — `lockout_duration`, `reset_token_ttl` gain `=…` |
| `:1676` | `build_memory_auth_service` — same two |
| `:1816` | `simple_template` — the positional shift is corrected |

Line count is unchanged (**1 941 → 1 941**), so NFR-002 (`:476`, ≤ 2 000) is unaffected; `…` is mid-line, so INV-006 hook cleanliness (`:448`) is unaffected. Regeneration must be the **last** step of the commit (AGENTS.md "Structure Map"; spec §14 Sequencing) and must be re-run if any `.py` file changes afterwards — the pre-commit `structure-map-check` hook is check-only and will otherwise block the commit.

### 5.4 Files expected to change in PR B

| File | Role |
|---|---|
| `scripts/make_map.py` | the fix (the only implementation file) |
| `STRUCTURE.md` | regenerated artifact (never hand-edited) |
| `tests/unit/test_make_map.py` | new EDGE-017 witness + re-derived AC-014 witnesses |
| `tests/acceptance/test_structure_map.py` | new committed-map witness |
| `tests/property/test_structure_map.py` | new INV-007 property witness |
| `docs/verification/map-default-drop-shift.md` | this record (RED/GREEN evidence appended by Phases 3–5) |
| `docs/verification/traceability.md` | REQ-014/AC-014 rows updated, INV-007/EDGE-017 rows added |
| `pyproject.toml` | `patch` bump `1.1.0 → 1.1.1` (S6.4, `bump-my-version bump patch`) |

Non-test, non-generated implementation files touched: **1** (`scripts/make_map.py`).

### 5.5 What the fix must not do

No change to `_signature`'s other outputs, to `_class_name` (`:403`, class bases/keywords — REQ-016, out of scope), to `type_params` handling (REQ-017, out of scope), to the threshold value, to any `src/` module, to any spec file (PR A owns those), and no compatibility flag or setting (Q-18). No new dependency.

---

## 6. Light-tier ISSUE qualification (AGENTS.md "Light ISSUE tier")

| Criterion | Result |
|---|---|
| Single feature | **yes** — the structure-map generator and its artifact; no `src/` feature is touched |
| ≤ 3 files excluding tests | **yes** — `scripts/make_map.py` + the generated `STRUCTURE.md` = 2 |
| No new dependency | **yes** — stdlib `ast` only |
| No new public interface | **yes** — the generator CLI is unchanged; only rendered text changes |
| No cross-feature change | **yes** — nothing under `src/backend/` changes |
| Existing suite covers the area | **yes** — the triage names the covering tests: `tests/unit/test_make_map.py` (24 passed with `tests/property/test_structure_map.py` at this commit), `tests/property/test_structure_map.py`, `tests/acceptance/test_structure_map.py` (30 passed, 1 pre-existing failure, §3.5) |

**Phase 5 runs targeted + smoke:** the four §4 witnesses, the three structure-map test modules (`uv run pytest tests/unit/test_make_map.py tests/property/test_structure_map.py tests/acceptance/test_structure_map.py -v`), `uv run ruff check .` and `uv run mypy src/` (plus `uv run mypy scripts/` since `scripts/make_map.py` changes), and `uv run python scripts/check_traceability.py`.

**Full regression suite runs at the Phase 6 pre-merge gate (S6.4)** before the PR opens — `uv run pytest tests/ -v` — and must pass; the result is recorded in the review report. Baseline note: `test_ac_021_committed_map_matches_fresh_render` is red on `main` today (§3.5, F-01/F-02/F-03); PR B's regeneration is what makes it green, so a red AC-021 at the S6.4 gate means the map was not regenerated after the last `.py` change (or the CRLF cause of F-03 re-appeared — re-run the generator, never hand-edit the map).

---

## 7. Spec Amendment PR A plan (must merge before Phase 3 starts)

**Branch/PR:** PR A is opened from this same change branch (`issue/map-default-drop-shift`) and contains **only** `docs/specs/structure-map.md`. It carries **no version bump** (Q-3/Q-4: the bump belongs to the change as a whole and is taken in PR B at S6.4; a docs-only change would get none anyway). It must be **merged before Phase 3** (AGENTS.md Spec Amendment Workflow item 6: merge the spec PR before resuming implementation), i.e. before the reproduction tests are written against the amended wording. The Spec Approval Gate applies to a spec **authored** by a change; an amendment reaches the spec through its own PR to `main` exactly as the Workflow requires — direct edits to `docs/specs/` on `main` are rejected.

### 7.1 REQ-014 (`:287-289`) — replace the last sentence

> …so formatting drift in the source cannot change the map; a parameter default is rendered **only when its unparsed text is ≤ 20 characters**, and a default that exceeds the threshold is abbreviated to the single-character placeholder **`…` in its own slot** — the parameter is never removed from the rendered list and never loses its `=` separator, so the rendered list preserves the source's parameter names, their order, the positional-only / positional / keyword-only split, and **which parameters carry a default**. The rule is **uniform** across positional, positional-only and keyword-only defaults.

### 7.2 AC-014 (`:424`) — amend the last two clauses

> …**And** the signature text equals the `ast.unparse` rendering **except that a parameter default whose unparsed text exceeds 20 characters renders as the `…` placeholder in its own slot**, **And** a parameter default of ≤ 20 characters is shown verbatim while a longer one is abbreviated to `…`, **And** the rendered parameter list, **with every `…` replaced by the literal `...`**, parses with `ast.parse` and yields the same parameter names, order, positional-only / positional / keyword-only split and set of defaulted parameters as the source.

The "with every `…` replaced by the literal `...`" qualifier is **mandatory**, not stylistic: `…` in a default position is a `SyntaxError` (F-06), so a literal "the rendered list parses" clause would be unsatisfiable and the witness unimplementable.

### 7.3 §8 Invariants (`:439`, after INV-006 at `:448`) — add one row

> | INV-007 | For every rendered signature, the parameter list with each `…` placeholder replaced by the literal `...` parses with `ast.parse` and yields exactly the source's parameter names in order, the same positional-only / positional / keyword-only split, and exactly the set of parameters that carry a default; a `…` appears **only** where the source default's unparsed text exceeds the REQ-014 threshold. |

### 7.4 §9 Edge Cases (`:450`, after EDGE-016 at `:469`) — add one row (3 columns)

> | EDGE-017 | A parameter default whose unparsed text exceeds 20 characters, in a positional, positional-only or keyword-only slot — including a function whose **only** default is over-long, and a keyword-only parameter that has **no** default at all. | The parameter is rendered in its own slot as `name: annotation=…`; the placeholder never shifts a neighbouring default onto an earlier parameter, a parameter with no default is never given one, and a parameter with a default is never rendered without one. |

### 7.5 §11 Test Strategy — add two rows (the spec table is not checked against `tests/`)

> | INV-007 | REQ-014 | property | `tests/property/test_structure_map.py` | `test_inv_007_signature_fidelity_survives_default_abbreviation` |
> | EDGE-017 | REQ-014 | unit | `tests/unit/test_make_map.py` | `test_edge_017_over_long_default_keeps_its_slot` |

The AC-014 row (`:526`) keeps its function name (the witness is re-derived in place, not renamed).

### 7.6 §15 Changelog (`:631`) — prepend above the v1 entry

> - v2 (2026-10-10): REQ-014/AC-014 amended — an over-long parameter default is now abbreviated to the `…` placeholder **in its own slot** instead of being dropped from the rendered parameter list; INV-007 (signature fidelity) and EDGE-017 added. The `_DEFAULT_MAX_CHARS` threshold value (20) is unchanged.

(Other amended specs in this repo put `## Changelog` at the **top** of the file, newest first — `docs/specs/settings.md:3`, `docs/specs/authentication.md:3`. `structure-map.md` numbers its changelog as §15 at the bottom with a single v1 entry at `:633-636`. The minimal, layout-preserving choice is to prepend v2 above v1 in §15; relocating the section to the top would be an unrelated restructure of an approved spec and is out of scope for PR A.)

### 7.7 PR A gates (verified against the workflow files at `7299108`)

| Gate | Effect of PR A |
|---|---|
| `.github/workflows/spec-validation.yml` (paths include `docs/specs/**`) — `verify_spec.py` per spec | **passes.** The `✗ INV-007 has property test` line is printed but is cosmetic: the script appends failures only when a whole test category is missing, not per ID (F-10) |
| same workflow — `uv run python scripts/check_traceability.py` | **passes without touching `docs/verification/traceability.md`**: rule (1) requires a matrix row only for **REQ/AC** IDs, PR A adds no new REQ/AC, and INV-007/EDGE-017 are already defined by other specs with existing rows (F-09) |
| same workflow — `uv run pytest tests/ -v` | **fails on the pre-existing `test_ac_021` red** (§3.5) — identical on `main`, not caused by the amendment; see F-02 for the decision the orchestrator/human must take |
| `.github/workflows/quality.yml` (no path filter → runs on every PR) | `type-check` (`mypy src/` + `mypy scripts/`) unaffected; `docs` job runs `mkdocs build --strict` — unaffected, because `mkdocs.yml` sets `docs_dir: userdocs` and `docs/specs/` is the internal process record, not the site (F-13); `coverage` job runs `pytest tests/ --cov` → same pre-existing AC-021 failure; `complexity` runs `complexipy src tests` — unaffected (`scripts/` not analyzed, NFR-005); `security`, `dependencies`, `dependency-review`, `migrations` unaffected |
| `.github/workflows/lint.yml` | **not triggered** — its path filter is `src/**`, `tests/**`, `pyproject.toml`, `.pre-commit-config.yaml`, `.github/workflows/lint.yml`, `.github/hooks/**`; a docs-only PR matches none |
| pre-commit `structure-map-check` hook (`files: \.py$`) | not triggered (no `.py` change) — PR A therefore does **not** regenerate the map |

**Sequencing note (resolved, not a blocker):** spec §14 requires `STRUCTURE.md` to be regenerated after `chore/remove-spec-tdd-driver` (PR #62) merged. That merge (`a2000c2`) predates the map's last regeneration (`8ec73ee`), and the measured diff in §5.3 shows no `.github/` count line — the requirement is already satisfied.

---

## 8. Explicitly out of scope (Q-16 hard boundary: the parameter-default rule only)

| Out of scope | Why |
|---|---|
| The rest of the REQ-015…REQ-018 symbol layer — `_class_name` (`scripts/make_map.py:403`) class bases and keywords (unfiltered today), `type_params` (ignored today) | Not the parameter-default rule; a separate change if wanted |
| The threshold value `_DEFAULT_MAX_CHARS = 20` (`:74`) | Q-8: untouched; only the treatment of an over-long default changes |
| Any `src/` change | The defect is in the generator; no backend behavior is involved |
| Extending complexipy to `scripts/` | Separate change `chore/complexipy-scripts` (Q-15/Q-19) |
| A compatibility flag / setting to keep the old rendering | Q-18: none |
| `test_ac_021_committed_map_matches_fresh_render`'s raw-byte comparison (CRLF fragility, F-03) and the `check_traceability.py` bare-ID namespace weakness (F-09) | Pre-existing, unrelated to the default rule; candidates for their own ISSUEs — recorded, not fixed here |
| Renaming the placeholder character | Q-2 fixes `…` as normative |

---

## 9. Findings (recorded at P.4; each verified by execution in this worktree)

| ID | Finding | Disposition |
|---|---|---|
| **F-01** | `uv run python scripts/make_map.py --check` exits **1 on `main`**: committed `docs/ · 223 files (process record)` (`STRUCTURE.md:452`) vs a fresh render of `224`. The map was last regenerated at `8ec73ee`, when `git ls-files docs` returned 223; `main` now tracks 224 because Phase P planning records are committed directly to `main` — and no CI job runs `--check` (REQ-023/REQ-026 keep it local). | PR B's regeneration absorbs it; recorded so it is not hidden. Structural cause (planning records make the map stale with no way to regenerate on `main`) is a workflow observation for the after-workflow-optimization. |
| **F-02** | Consequence: `tests/acceptance/test_structure_map.py::test_ac_021_committed_map_matches_fresh_render` is **RED on `main`** (acceptance module: 1 failed, 30 passed). So the full suite is not green on `main`, and **PR A's CI will show it red** (`spec-validation.yml` tests job, `quality.yml` coverage job). | PR B's regeneration makes it green. For PR A the orchestrator/human choose: merge with the known pre-existing red (recommended — it is red on `main` too), or add a one-line map regeneration to PR A. Not this step's decision; flagged in the handoff. |
| **F-03** | `test_ac_021` compares **raw bytes** (`committed == fresh`) while the working tree has CRLF (`git ls-files --eol STRUCTURE.md` → `i/lf w/crlf`, `core.autocrlf=true`), so on this host it has a **second, OS-dependent** failure cause that regeneration fixes only until the next checkout. EDGE-016 covers `--check` normalization, not this test. | Out of scope here (F-03 is a witness-quality ISSUE). Mitigation for the S6.4 gate: regenerate immediately before the full-suite run. |
| **F-04** | The defect is **not confined to positional defaults**: 7 of the 8 over-long defaults in the tree are keyword-only, and the committed map renders `reset_token_ttl`, `lockout_duration` and `origin` as **required** parameters (`STRUCTURE.md:686`, `:1675`, `:1676`) — contradicting AGENTS.md's own documented defaults. The uniform rule changes **4** map lines, not 1. | Both witnesses are in the reproduction plan (§4.1/§4.2); the amended EDGE-017 covers all three slots. |
| **F-05** | Q-11's answer claims the `resize(...)` witness line is unaffected. It is **not**: `resize` carries the over-long keyword-only defaults `data` (23) and `over` (21), so its line changes under the uniform rule. | The authorized witness-edit list in §4.4 includes it; the question file's statement is corrected here (the question file is orchestrator-owned and is not edited from this worktree). |
| **F-06** | `…` in a parameter-default position is a **`SyntaxError`** (`invalid character '…' (U+2026)`), so INV-007 / AC-014 cannot literally require the rendered parameter list to parse. | PR A wording uses "with every `…` replaced by the literal `...`" (§7.2/§7.3); verified that the substitution preserves names, order, the slot split and the defaults-set. |
| **F-07** | `ast.unparse` cannot emit `…` from a real node (`ast.unparse(ast.Constant(...))` → `...`). | The placeholder must be injected (sentinel node or string-level substitution). Verified: `ast.unparse(ast.Name(id="…"))` → `…`, and the rule stays idempotent (1 char ≤ 20), so INV-001 holds. Phase 4 picks the mechanism. |
| **F-08** | `ast.arguments.kw_defaults` holds `None` for keyword-only parameters **without** a default. A placeholder rule that substitutes every entry renders required parameters as optional — measured on a first attempt: `SmtpTransportImpl.__init__` (`STRUCTURE.md:1039`) gained `username: str=…, password: str=…, use_tls: bool=…, timeout: float=…`. | §5.1 keeps `None` as `None`; §4.1's `keys(*, need: int, …)` case is the witness that locks it. |
| **F-09** | Q-14's rationale ("`check_traceability.py` fails any defined ID with no matrix row") is **inaccurate for INV/EDGE IDs**: rule (1) matches REQ/AC only (`REQ_OR_AC_RE`); the structure-map spec's own §12 and `docs/verification/structure-map.md` finding 2 already state that all 54 of its REQ/AC IDs are covered by other specs' rows in the shared bare-ID namespace. Rule (2) fails rows citing undefined IDs and rule (3) fails rows citing a test function that does not exist under `tests/`. | The INV-007/EDGE-017 matrix rows are a **workflow** obligation, written in **PR B** after the witnesses exist (§4.6), not in PR A. The namespace collision risk (several specs define `INV-007`) is recorded as pre-existing and out of scope. |
| **F-10** | `scripts/verify_spec.py` prints `✗ INV-007 has property test` once PR A adds the ID, yet **exits 0** — the failure list is populated only when a category has no test functions at all. | PR A's spec-validation job stays green; the `✗` line disappears when Phase 3 adds the property witness. |
| **F-11** | Line-number citations drift: the TODO cites `STRUCTURE.md:1813`, the defective line is `:1816` at `7299108`. The `scripts/make_map.py` anchors in the TODO (`:74`, `:375-386`) are accurate. | All map locations in this record are content-locatable, and §4.2 forbids line-number assertions on the map. |
| **F-12** | The scan of all 342 tracked code-dir modules found **no** positional-only over-long default and **no** real module function whose only default is over-long (the only such case in the tree is the `_AC014_MODULE` fixture string). Those two EDGE-017 branches are unreachable in the current tree. | Covered by the synthetic unit witness (§4.1) and the property witness (§4.3), not by the map. |
| **F-13** | `mkdocs.yml` sets `docs_dir: userdocs`; `docs/specs/` is the internal process record and is **not** in the site nav, so `uv run --group docs mkdocs build --strict` (and the `docs` CI job) is unaffected by PR A — it still runs, because `quality.yml` has no path filter. | No action; recorded so the PR A gate list is not over-read. |
| **F-14** | Environment hazard (already in the Problem Log as **P-94**): `uv run python scripts/make_map.py` **without** `--check` rewrites `STRUCTURE.md` in place. Evidence gathering at P.4 must use `--check` or `--out <temp>`; recovery is `git checkout -- STRUCTURE.md`. | Honored throughout this step (no repository file other than this record was written; scratch probes live outside the repository). |

---

## 10. READY gate (for the orchestrator)

- TODO `Status: READY` may be set on `main` once this record is verified: the triage cites existing approved IDs (REQ-014, AC-014, REQ-021, AC-021, REQ-019/INV-001, INV-006, NFR-002, NFR-005, REQ-023), confirms observed-vs-required deviation with executed evidence and **two** live witnesses in the committed artifact, records the Spec Amendment stop (item 13) with PR A's exact wording and gates, names the reproduction tests with RED/GREEN commands, and qualifies the change for the **light tier** with the covering tests named.
- No P.5 step runs for ISSUE; no spec-approval PR is opened for this change beyond PR A itself.
- Next atomic step when PR A is merged: **S3.1 Derive tests** (Phase 3) in this worktree.

---

## PR A — spec amendment (executed on this branch, 2026-10-10)

PR A is the Spec Amendment PR required by §3.4 / §7 and opened from this same change branch
(`issue/map-default-drop-shift` → `main`). It changes **only** `docs/specs/structure-map.md` plus the
regenerated `STRUCTURE.md` (F-02 disposition below) and this record. **No** `scripts/`, `tests/`,
`src/`, `pyproject.toml`, `docs/todo/` or `docs/questions/` file is touched, and there is **no version
bump** (Q-3/Q-4: the `patch` bump belongs to PR B at S6.4).

`git diff --name-status main...HEAD` after the PR A commits:

```text
M  STRUCTURE.md
M  docs/specs/structure-map.md
M  docs/verification/map-default-drop-shift.md
```

### A.1 Amended IDs — exact before / after

**REQ-014** (§5, the signature bullet; only the last sentence changes) — before:

```text
- signatures are produced with `ast.unparse` for parameters, annotations and return annotation, so
  formatting drift in the source cannot change the map; a parameter default is included **only when
  its unparsed text is ≤ 20 characters**.
```

after:

```text
- signatures are produced with `ast.unparse` for parameters, annotations and return annotation, so
  formatting drift in the source cannot change the map; a parameter default is rendered **only when
  its unparsed text is ≤ 20 characters**, and a default that exceeds the threshold is abbreviated to
  the single-character placeholder **`…` in its own slot** — the parameter is never removed from the
  rendered list and never loses its `=` separator, so the rendered list preserves the source's
  parameter names, their order, the positional-only / positional / keyword-only split, and **which
  parameters carry a default**. The rule is **uniform** across positional, positional-only and
  keyword-only defaults (EDGE-017, INV-007).
```

**AC-014** (§7) — the Given/When/Then prefix through "in the stated line form" is unchanged; the last
clause is replaced by three. Before (last clause):

```text
**And** the signature text equals the `ast.unparse` rendering, **And** a parameter default of ≤ 20
characters is shown while a longer one is omitted.
```

after (last three clauses):

```text
**And** the signature text equals the `ast.unparse` rendering **except that a parameter default whose
unparsed text exceeds 20 characters renders as the `…` placeholder in its own slot**, **And** a
parameter default of ≤ 20 characters is shown verbatim while a longer one is abbreviated to `…`,
**And** the rendered parameter list, **with every `…` replaced by the literal `...`**, parses with
`ast.parse` and yields the same parameter names, order, positional-only / positional / keyword-only
split and set of defaulted parameters as the source.
```

The amendment is **stricter** than v1: v1 permitted "a longer one is omitted"; v2 forbids omission and
adds a parse-and-fidelity clause. No other ID was renumbered, restated or deleted, and no AC was
weakened.

### A.2 New IDs (added verbatim per §7.3/§7.4, in the existing table shape and section placement)

- **INV-007** — §8 Invariants, immediately after INV-006: *"For every rendered signature, the parameter
  list with each `…` placeholder replaced by the literal `...` parses with `ast.parse` and yields
  exactly the source's parameter names in order, the same positional-only / positional /
  keyword-only split, and exactly the set of parameters that carry a default; a `…` appears **only**
  where the source default's unparsed text exceeds the REQ-014 threshold."*
- **EDGE-017** — §9 Edge Cases, immediately after EDGE-016: *edge* — "A parameter default whose
  unparsed text exceeds 20 characters, in a positional, positional-only or keyword-only slot —
  including a function whose **only** default is over-long, and a keyword-only parameter that has
  **no** default at all"; *expected behavior* — "The parameter is rendered in its own slot as
  `name: annotation=…`; the placeholder never shifts a neighbouring default onto an earlier parameter,
  a parameter with no default is never given one, and a parameter with a default is never rendered
  without one."

Both are worded over the **placeholder-substituted** text, never over the literal rendered list, per
**F-06** (`…` in a default position is a `SyntaxError`).

### A.3 §11 Test Strategy — two rows added (existing rows untouched)

```text
| INV-007 | REQ-014 | property | `tests/property/test_structure_map.py` | `test_inv_007_signature_fidelity_survives_default_abbreviation` |
| EDGE-017 | REQ-014 | unit | `tests/unit/test_make_map.py` | `test_edge_017_over_long_default_keeps_its_slot` |
```

These are the witnesses named by the §4 reproduction plan. The AC-014 row keeps
`test_ac_014_symbol_inventory_and_unparsed_signatures` — the witness is re-derived in place in PR B,
not renamed (§4.4).

### A.4 §15 Changelog — v2 prepended above v1 (section placement unchanged)

> `- v2 (2026-10-10): REQ-014 amended — … AC-014 amended — … INV-007 (signature fidelity) and EDGE-017
> added, with their §11 witnesses. The 20-character threshold value is unchanged. No existing ID was
> renumbered, restated or deleted. Change map-default-drop-shift (ISSUE, Spec Amendment Workflow); see
> docs/verification/map-default-drop-shift.md.`

The section stays §15 at the bottom of the file (the layout-preserving choice recorded in §7.6);
"top of the changelog" means newest-first **inside** §15, matching the other amended specs.

### A.5 Gate results (all run in this worktree at the PR A commits)

| Gate | Command | Result |
|---|---|---|
| Traceability referential integrity (CI `traceability` job) | `uv run python scripts/check_traceability.py` | **exit 0** — `Traceability: PASS (881 matrix rows, 136 spec IDs, 801 test functions)`; no new REQ/AC ID was introduced, and INV/EDGE rows are not required by the checker (§12 of the spec, F-09) |
| Spec validation (CI `spec-validation` job, per spec) | `uv run python scripts/verify_spec.py docs/specs/structure-map.md` | **exit 0** — all REQ/AC/INV checks ✓, `Traceability: PASS` (see F-15) |
| Task DAG (CI, `\|\| true`) | `uv run python scripts/validate_task_dag.py .github/task-runner/tasks.json` | **exit 0** — `PASSED: 7 tasks, acyclic, well-formed` (unchanged; PR A touches no DAG file) |
| Docs site | `uv run --group docs mkdocs build --strict` | **exit 0** (F-13: `docs_dir: userdocs`, the spec is not in the site) |
| Structure-map acceptance | `uv run pytest tests/acceptance/test_structure_map.py -q` | **31 passed** — fully GREEN, including `test_ac_021_committed_map_matches_fresh_render`, which was red on `main` (F-02 disposition below) |
| Structure-map unit + property (smoke) | `uv run pytest tests/unit/test_make_map.py tests/property/test_structure_map.py -q` | **24 passed** — no existing expectation changed by the amendment; no test asserts on spec **text** (`grep -rn "docs/specs/structure-map" tests/` matches only module docstrings) |
| Map freshness | `uv run python scripts/make_map.py --check` | **exit 0** (was exit 1 on `main`) |
| Lint / format | `uv run ruff check .` / `uv run ruff format --check .` | **All checks passed!** / **343 files already formatted** — PR A touches no `.py` file, so both are unchanged from `main` |

### A.6 Finding dispositions taken in PR A

- **F-02 — disposition: fixed inside PR A** (orchestrator decision, recorded here). `STRUCTURE.md` was
  regenerated with `uv run python scripts/make_map.py` and verified with `--check` (exit 0), so PR A's
  CI gate set is meaningful instead of carrying the pre-existing red `test_ac_021` failure. The change
  is a **generated-file regeneration**, not a behavior change: the diff is **one line**, the
  `docs/ — 223 files (process record)` count → `225 files`. The map is never hand-edited (REQ-021,
  REQ-022 conflict rule), and `make_map.py` was run **once**, followed by `--check` (P-94).
- **F-09 — disposition: `docs/verification/traceability.md` is deliberately NOT touched by PR A.**
  `check_traceability.py` rule (3) fails any matrix row citing a backticked test function that does not
  exist under `tests/`; `test_inv_007_signature_fidelity_survives_default_abbreviation` and
  `test_edge_017_over_long_default_keeps_its_slot` are written in Phase 3 (PR B). The INV-007/EDGE-017
  rows and the updated REQ-014/AC-014 rows are therefore written in **PR B** (§4.6). The checker passes
  in PR A because rule (1) covers REQ/AC only and PR A adds no new REQ/AC ID.

### A.7 CI on PR A (#79)

All eleven required checks **pass** on the PR head (`gh pr checks 79`, merge state `CLEAN`):
`spec-validation`, `traceability`, `tests` (full suite, 5m36s), `coverage`, `docs`, `type-check`,
`complexity`, `dependencies`, `dependency-review`, `security`, `migrations`. `lint.yml` is **not
triggered** — its path filter (`src/**`, `tests/**`, `pyproject.toml`, `.pre-commit-config.yaml`,
`.github/workflows/lint.yml`, `.github/hooks/**`) matches none of this PR's three files, which is why
the local `ruff check .` / `ruff format --check .` results in A.5 are recorded.
This confirms the F-02 disposition: the pre-existing `test_ac_021` red that PR A would otherwise have
carried is gone, because the committed map is fresh at this commit.

### A.8 New findings from PR A

| ID | Finding | Disposition |
|---|---|---|
| **F-15** | F-10 predicted `verify_spec.py` would print `✗ INV-007 has property test` once the ID exists. It prints **`✓`**: the per-ID mark is `any("007" in f for f in property_funcs)` over **all** property test functions in the repository, and other specs already define `test_inv_007_*` (`test_inv_007_key_containment`, `test_inv_007_load_scope_valid`) — the same bare-ID namespace as F-09. The `failures` list is still only populated when the whole category is empty, so the exit code is 0 either way. | No action; PR A's `spec-validation` job is green as predicted, for a slightly different reason. Recorded so the after-workflow-optimization sees that `verify_spec.py` cannot witness a *specific* INV's property test. |
| **F-16** | §3.5/§5.3 measured the fresh `docs/` count as **224**; the regeneration in this worktree renders **225**. Both are correct: `git ls-files docs` is 224 on `main` and 225 on this branch, because the P.4 triage record (`docs/verification/map-default-drop-shift.md`) is a tracked `docs/` file on the change branch only. | Expected, not a defect: PR A merges the triage record together with the map, so `main`'s count and the committed map agree after the merge. PR B adds no new `docs/` file, so its regeneration stays at 225 unless `main` moves. |

## Phase 3 — reproduction tests (S3.1/S3.2 RED, 2026-10-10)

**Four witnesses, exactly the §4 plan; `scripts/make_map.py` untouched, `STRUCTURE.md` not regenerated, `docs/verification/traceability.md` untouched (F-09).**

| Witness | File | Status |
|---|---|---|
| §4.1 `test_edge_017_over_long_default_keeps_its_slot` (new) | `tests/unit/test_make_map.py` | **RED — assertion** |
| §4.2 `test_ac_014_committed_map_renders_over_long_default_in_place` (new) | `tests/acceptance/test_structure_map.py` | **RED — assertion** |
| §4.3 `test_inv_007_signature_fidelity_survives_default_abbreviation` (new) | `tests/property/test_structure_map.py` | **RED — assertion** |
| §4.4 `test_ac_014_symbol_inventory_and_unparsed_signatures` (re-derived in place) | `tests/unit/test_make_map.py` | **RED — assertion** |

**Pre-flight / post-flight collection:** `uv run pytest --collect-only tests/unit/test_make_map.py tests/property/test_structure_map.py tests/acceptance/test_structure_map.py -q` → `58 tests collected`, no errors (55 baseline + 3 new).

### RED (all four node ids, §4.5 `red_command`)

- **command:** `uv run pytest tests/unit/test_make_map.py::test_edge_017_over_long_default_keeps_its_slot tests/unit/test_make_map.py::test_ac_014_symbol_inventory_and_unparsed_signatures tests/property/test_structure_map.py::test_inv_007_signature_fidelity_survives_default_abbreviation tests/acceptance/test_structure_map.py::test_ac_014_committed_map_renders_over_long_default_in_place -v`
- **result:** `4 failed` (exit 1) — every failure is an `AssertionError` on **rendered signature text**; no `SyntaxError`, no `ValidationError`, no collection error, so the test data is valid and RED is a behaviour RED.
- **failure mode per witness:**
  - EDGE-017 unit: sequence clause 1 — the generator renders `shift(a: int, b: str=1, c: list[int]='xy')`, `only(pool: list[int])`, `posonly(a: int, b: str=1, /)`, `keys(*, need: int, k: int=1, m: str)` where the amended spec requires `shift(a: int=1, b: str='xy', c: list[int]=…)`, `only(pool: list[int]=…)`, `posonly(a: int=1, b: str=…, /)`, `keys(*, need: int, k: int=1, m: str=…)`; needle clause 2 additionally reports the **shift itself** (`b: str=1` and `c: list[int]='xy'` are rendered, must be absent) and `edge(exact: str='0123456789abcdefgh')` is already correct (no regression to fix).
  - AC-014 acceptance (committed map): clause 1 — `simple_template` renders `name: str, subject: str='test', body_html: str='Test {{who}}', …` (defaults shifted left) instead of `name: str='test', subject: str='Test {{who}}', body_html: str=…, …`; clause 2 — `reset_token_ttl: timedelta=…`, `lockout_duration: timedelta=…`, `origin: str=…` are missing from the `AuthService.__init__` line (they render default-free), while `session_ttl: timedelta=timedelta(days=7)` and `max_failed_attempts: int=5` are present and stay unharmed.
  - AC-014 unit (re-derived): clause 1 — `resize(...)` and `items(pool: list[int])` still render the old omission; needle clause 2 — the three new positive needles `data: dict[str, int]=…`, `over: str=…`, `pool: list[int]=…` are absent. Every pre-existing needle (the literal over-long default text absent, `exact`/`step`/`b` verbatim) is kept, so the witness is strictly stronger than before.
  - INV-007 property: hypothesis shrank to `def f0(alpha: int='0123456789abcdefghij0') -> None` — clause 4 `the rendered parameter list is 'alpha: int', expected 'alpha: int=…'`; clause 5 `the substituted list re-unparses to 'alpha: int', expected 'alpha: int=...'`; clause 2 `parameters carrying a default is [], the source's is ['alpha']`. Clauses 1/3 (names in order, slot split) pass on this example, as expected for a single-parameter function.

**Touched-file regression** (`uv run pytest tests/unit/test_make_map.py tests/property/test_structure_map.py tests/acceptance/test_structure_map.py -q -p no:randomly`): `5 failed, 53 passed` — the four RED witnesses plus the **pre-existing** `test_ac_021_committed_map_matches_fresh_render` red recorded in §3.4 (the committed map is stale against this branch's `docs/` count, F-16). No other test changed state.

**Ruff (changed paths):** `uv run ruff check tests/unit/test_make_map.py tests/property/test_structure_map.py tests/acceptance/test_structure_map.py` → `All checks passed!`; `uv run ruff format --check` on the same three paths → `3 files already formatted`.

### New findings from Phase 3

| ID | Finding | Disposition |
|---|---|---|
| **F-17** | The first draft of the INV-007 strategy put the whole slot builder inside `_signature_module`, which pushed its cyclomatic complexity to **20** and broke `test_nfr_005_complexipy_threshold_holds` (NFR-005 analyses `tests/` too, max 15). | Fixed inside S3.1 (in-step fix-and-recheck): the strategy is split into `_slots`, `_slot_text` and `_signature_text`; `uv run complexipy --max-complexity-allowed 15 tests` → *All functions are within the allowed complexity*, and NFR-005 passes again. |
| **F-18** | §4.2's `simple_template` expectation cannot be written as one f-string: `{{who}}` inside an f-string collapses to `{who}`, so the needle silently mismatched the committed map. | The constant is built as `plain + f"{_ELLIPSIS}" + plain` so the doubled braces survive; verified against the §5.2 probe rendering byte-for-byte. |

### S3.2 gate re-check (2026-10-10)

Independent re-run of the Phase 3 gate at HEAD `0ecf7bc` (`test(map-default-drop-shift): reproduction witnesses for EDGE-017/INV-007 + re-derived AC-014 (RED)`), working tree clean. Nothing was re-derived, implemented or regenerated here — verification only.

| Check | Command | Result line |
|---|---|---|
| RED (§4.5 `red_command`, unchanged) | `uv run pytest tests/unit/test_make_map.py::test_edge_017_over_long_default_keeps_its_slot tests/unit/test_make_map.py::test_ac_014_symbol_inventory_and_unparsed_signatures tests/property/test_structure_map.py::test_inv_007_signature_fidelity_survives_default_abbreviation tests/acceptance/test_structure_map.py::test_ac_014_committed_map_renders_over_long_default_in_place -v` | `4 failed in 1.73s` (exit 1) — **0 errors, 0 skipped, 0 xfail** |
| Failure kind (AGENTS.md Phase 3 item 6) | same run with `--tb=line` | all four are `AssertionError` on **rendered signature text** at `tests/unit/test_make_map.py:1052`, `tests/unit/test_make_map.py:1025`, `tests/acceptance/test_structure_map.py:1534`, `tests/property/test_structure_map.py:665` — no `SyntaxError`, no `ValidationError`, no collection/setup error; the INV-007 fixture's own `pytest.fail`-on-`SyntaxError` guard never fired, so the generated test data is valid |
| Ruff (changed paths) | `uv run ruff check tests/unit/test_make_map.py tests/property/test_structure_map.py tests/acceptance/test_structure_map.py` | `All checks passed!` (exit 0) |
| Ruff format (changed paths) | `uv run ruff format --check` on the same three paths | `3 files already formatted` (exit 0) — no in-step fix needed |
| NFR-005 guard (F-17) | `uv run complexipy --max-complexity-allowed 15 tests` | `All functions are within the allowed complexity.` (exit 0) |
| Branch scope | `git diff --name-status main...HEAD` | `M docs/verification/map-default-drop-shift.md`, `M tests/acceptance/test_structure_map.py`, `M tests/property/test_structure_map.py`, `M tests/unit/test_make_map.py` — `scripts/make_map.py` and `STRUCTURE.md` **untouched**, `docs/verification/traceability.md` untouched (F-09) |

**Gate ◆ RED: confirmed.** Phase 3 is complete; Phase 4 (`S4.1`) may start. The pre-existing `test_ac_021_committed_map_matches_fresh_render` red (F-02/F-16) is untouched by this re-check and stays a Phase 4 regeneration concern, not a Phase 3 gate item.

### S4.1 fix-target re-location (2026-10-10)

Re-located **by content** at HEAD `5b51614` (`docs(map-default-drop-shift): S3.2 RED gate re-check`), working tree clean. `scripts/make_map.py` was **not** edited here; the only file written is this record.

**RED still holds at HEAD** — the §4.5 `red_command` (four node ids, `-v`) → **`4 failed`** (exit 1, `4 failed in 1.05s`; 0 errors, 0 skipped, 0 xfail). With `--tb=line` all four are `AssertionError` on **rendered signature text** (`tests/property/test_structure_map.py:665`, and the unit/acceptance witnesses) — the INV-007 example is still `def f0(alpha: int='0123456789abcdefghij0')`-shaped, i.e. clause 2/4/5 of INV-007 broken, no `SyntaxError`/`ValidationError`/collection error. Map freshness at HEAD: `uv run python scripts/make_map.py --check` → **exit 1** (`STRUCTURE.md is out of date`) — expected, Phase 4 regenerates.

**Anchors — no drift.** `scripts/make_map.py` is 567 lines and was last touched by `28a24be` (predates the triage), so every §3.1 citation is still exact:

| Anchor | Line |
|---|---|
| `_DEFAULT_MAX_CHARS = 20` | `:74` (comment `:73`) |
| `_drop_long_defaults(args: ast.arguments) -> None` | `:375` (docstring `:376-381`) |
| the two filter sites | `:382` and `:383-385` |
| `_signature(...)` | `:388`; the `_drop_long_defaults(node.args)` call | `:396` |

Current code, verbatim (`:375-385`):

```python
def _drop_long_defaults(args: ast.arguments) -> None:
    """AC-014: keep a parameter default only when its unparsed text is <= 20 characters.

    Mutates the parsed tree (each module is rendered once, and the filter is idempotent). The
    positional defaults are one list aligned to the tail of the argument list, so dropping an entry
    shifts the kept ones onto the earlier parameters; the keyword defaults align one-to-one with
    `kwonlyargs`, so a dropped entry becomes None rather than being removed."""
    args.defaults = [d for d in args.defaults if len(ast.unparse(d)) <= _DEFAULT_MAX_CHARS]
    args.kw_defaults = [
        d if d is not None and len(ast.unparse(d)) <= _DEFAULT_MAX_CHARS else None for d in args.kw_defaults
    ]
```

The two `…` constants that already exist are **not** the default marker: `_SUMMARY_MARKER = "…"` (`:71`, REQ-018 summary truncation) and `_FIELD_MARKER = "…"` (`:79`, REQ-017 field cap). There is **no `_PLACEHOLDER`** in the file (F-19).

**§5.1 still applies to this code shape — verified by patch, not by reading.** A scratch copy of the generator **outside the repository** (`/tmp/tmp.1kZgDk6X0v/make_map_probe.py`) took the `:382-385` block as an **exact single match** and replaced it with the substitution form; the probe ran with `--root <worktree> --out <temp>` (P-94: the repository's `STRUCTURE.md` was never written; `git status` stayed clean).

Load-bearing clauses, unchanged and re-confirmed by the probe:

- **`kw_defaults` `None` stays `None`** — the probe keeps `None if d is None else (…)`, so `keys(*, need: int, …)`-shaped required keyword-only parameters stay default-free (F-08; the §4.1 `keys` witness locks it). The probe diff shows **no** `=…` added to any parameter that has no default in the source.
- **`_DEFAULT_MAX_CHARS = 20` untouched** (`:74`) — the probe left it at 20 and `edge(exact: str='0123456789abcdefgh')` still renders verbatim.

**§5.2 probe result, reproduced at this HEAD.** Mechanism used: `ast.Name(id=_DEFAULT_MARKER)` with `_DEFAULT_MARKER = "…"` added next to `:74` — `ast.unparse` renders it as `…`, and at 1 character it survives a second `_drop_long_defaults` pass, so the rule stays idempotent (INV-001). The probe render vs the committed map is **exactly the §5.3 set** — 5 changed lines, line count **1 941 → 1 941** (NFR-002 unaffected):

| Map line | Change |
|---|---|
| `:452` | `docs/ — 225 files (process record)` → `231 files` — pre-existing staleness only (F-01/F-16; the count grew again because `main` moved with new planning records), **not** this fix |
| `:686` | `AuthService.__init__` — `reset_token_ttl`, `lockout_duration`, `origin` gain `=…`; `session_ttl=timedelta(days=7)` and `max_failed_attempts: int=5` unharmed |
| `:1675` | `build_auth_service` — `lockout_duration`, `reset_token_ttl` gain `=…` |
| `:1676` | `build_memory_auth_service` — same two |
| `:1816` | `simple_template` — the positional shift is corrected to `name: str='test', subject: str='Test {{who}}', body_html: str=…, body_text: str='Test {{who}}'` |

**New findings from S4.1.**

| ID | Finding | Disposition |
|---|---|---|
| **F-19** | §5.1's snippet writes `else _PLACEHOLDER`, but no `_PLACEHOLDER` constant exists in `scripts/make_map.py`, and a bare `str` cannot be stored in `ast.arguments.defaults` — `ast.unparse` needs AST nodes (F-07). | Phase 4 adds its own constant (suggested `_DEFAULT_MARKER = "…"` beside `_DEFAULT_MAX_CHARS` at `:74`, mirroring the `_SUMMARY_MARKER`/`_FIELD_MARKER` shape) and injects it as a node (`ast.Name(id=_DEFAULT_MARKER)`) or by string-level substitution on the rendered signature — the §5.2 choice, unchanged. Still no new dependency, no new pattern → no ADR. |
| **F-20** | §5.4's PR B file list predates the changelog rule now on `main` (AGENTS.md Phase 6 item 10 at `:609`, item 11 at `:610`, Versioning at `:766`), so it omits `CHANGELOG.md`. | PR B also writes a `CHANGELOG.md` entry under `## [Unreleased]` (`Fixed`, at S6.4) and the bump commit moves the entries to `## [1.1.1] - <date>`. The light-tier "≤ 3 files excluding tests" count is unaffected — the criterion counts non-test files *changed by the fix*, and `CHANGELOG.md` is a Phase 6 record like `pyproject.toml`. |

**§5.4 list vs the branch state.** `git diff --name-status main...HEAD` at `5b51614`:

```text
M	docs/verification/map-default-drop-shift.md
M	tests/acceptance/test_structure_map.py
M	tests/property/test_structure_map.py
M	tests/unit/test_make_map.py
```

(PR A's three files — `docs/specs/structure-map.md`, `STRUCTURE.md`, this record — are already on `main` via merge `d8ba07f`, so they no longer appear in the range.) Still to be written in Phase 4 / later:

| Artifact | Status | Owner step |
|---|---|---|
| `scripts/make_map.py` — the generator fix + corrected `_drop_long_defaults` docstring (`:376-381` still documents the shifting/`None` effects as intended) | **not written** | S4.2 |
| `STRUCTURE.md` — regeneration, **last** step of the same commit as the `.py` change (REQ-021/AC-021, REQ-023 hook) | **not written** (`--check` exit 1) | S4.2/S4.4 |
| `docs/verification/traceability.md` — update the structure-map `REQ-014/AC-014` row (`:1034`, currently `GREEN (structure-map S5.1 …)`) and add rows for `test_edge_017_over_long_default_keeps_its_slot` + `test_inv_007_signature_fidelity_survives_default_abbreviation` + `test_ac_014_committed_map_renders_over_long_default_in_place`, naming this change inside the Status cell (Q-129 convention B). INV-007/EDGE-017 rows already exist for **other** specs (`:135`, `:536`, `:155`, `:243`, `:319`, `:554`, `:852`) — the bare-ID namespace (F-09). Legal now: the witnesses exist since `0ecf7bc`. | **not written** | S5.3 |
| `CHANGELOG.md` — `## [Unreleased]` → `Fixed` entry (F-20) | **not written** | S6.4 |
| `pyproject.toml` — `bump-my-version bump patch` `1.1.0 → 1.1.1` (verified still `1.1.0` on both `main` and this branch), entries moved to `## [1.1.1] - <date>` in the same commit | **not written** | S6.4 |

**Targeted GREEN commands for S4.2 (§4.5 `green_command`, unchanged):**

```text
uv run pytest tests/unit/test_make_map.py::test_edge_017_over_long_default_keeps_its_slot \
              tests/unit/test_make_map.py::test_ac_014_symbol_inventory_and_unparsed_signatures \
              tests/property/test_structure_map.py::test_inv_007_signature_fidelity_survives_default_abbreviation \
              tests/acceptance/test_structure_map.py::test_ac_014_committed_map_renders_over_long_default_in_place -v
uv run pytest tests/unit/test_make_map.py tests/property/test_structure_map.py tests/acceptance/test_structure_map.py -q
uv run python scripts/make_map.py && uv run python scripts/make_map.py --check   # both exit 0
```

The second command pair is the map-regeneration pair (write, then verify exit 0); the acceptance witness and `test_ac_021_committed_map_matches_fresh_render` go GREEN only after the regeneration, so the generator run must come **after** every `.py` edit in the commit (P-94: never run the write form while collecting evidence — `--check` or `--out <temp>` only).

**Gate ◆ S4.1: task picked, RED re-observed, fix target located by content, §5.1 confirmed against the live code shape.** Next: **S4.2 Implement + confirm GREEN**.

## Phase 4 — minimal fix (S4.2 GREEN, 2026-10-10)

HEAD at entry: `785da7a` (`docs(map-default-drop-shift): S4.1 fix-target re-location`), working tree clean.
**Files written by this step: `scripts/make_map.py` (the fix) and the regenerated `STRUCTURE.md`** — plus
this record. Nothing else: `tests/` untouched (the four witnesses are the contract),
`docs/verification/traceability.md` untouched (S5.3), `pyproject.toml` / `CHANGELOG.md` untouched (S6.4),
`docs/specs/`, `docs/todo/`, `docs/questions/` untouched.

### The fix (§5.1, the only implementation change)

`scripts/make_map.py` — the `:382-385` filter pair became a **substitution in the default's own slot**,
and the docstring that documented the shifting/`None` effects as intended was corrected (INV-007):

```python
def _abbreviate_default(default: ast.expr) -> ast.expr:
    """REQ-014 v2: `default` when its unparsed text fits the threshold, the `…` placeholder when it
    does not — a substitution, never a deletion."""
    return default if len(ast.unparse(default)) <= _DEFAULT_MAX_CHARS else ast.Name(id=_DEFAULT_MARKER)


def _drop_long_defaults(args: ast.arguments) -> None:
    """REQ-014/EDGE-017: abbreviate a parameter default to `…` when its unparsed text is > 20 characters.
    ... (docstring now states the placeholder rule and why dropping misrepresents the signature) ...
    `kw_defaults` is aligned one-to-one with `kwonlyargs` and holds None for a keyword-only
    parameter that has **no** default: None stays None, so a required parameter never gains `=…`."""
    args.defaults = [_abbreviate_default(d) for d in args.defaults]
    args.kw_defaults = [None if d is None else _abbreviate_default(d) for d in args.kw_defaults]
```

- **F-19 resolved as §5.2 predicted:** a new module constant `_DEFAULT_MARKER = "…"` sits next to
  `_DEFAULT_MAX_CHARS` (mirroring `_SUMMARY_MARKER` / `_FIELD_MARKER`), injected as
  `ast.Name(id=_DEFAULT_MARKER)` — `ast.unparse` renders a `Name`'s `id` verbatim, and at 1 character
  the placeholder stays under the threshold, so the rule is idempotent (INV-001). The §5.1 `else
  _PLACEHOLDER` form was not usable: a bare `str` cannot live in `ast.arguments.defaults` (F-07).
- **F-08 trap held:** `None if d is None else …` keeps a required keyword-only parameter default-free
  — the `keys(*, need: int, …)` unit witness and the INV-007 clause-2 property witness both lock it,
  and the regenerated map adds **no** `=…` to any parameter that has no default in the source (the
  `SmtpTransportImpl.__init__` line at `:1039` is unchanged).
- **`_DEFAULT_MAX_CHARS = 20` untouched** (Q-8): `edge(exact: str='0123456789abcdefgh')` still renders
  verbatim (unit + EDGE-017 witnesses).
- No rename (`_drop_long_defaults` keeps its name), no other change to the file, no new dependency,
  no new pattern → **no ADR** (AGENTS.md ADR threshold not met; Phase 2 is skipped for ISSUE).
- `_signature`, `_class_name`, `type_params` and every other generator output are untouched (§5.5).

### GREEN (targeted, §4.5 `green_command`)

| Check | Command | Result line |
|---|---|---|
| The four §4 witnesses | `uv run pytest tests/unit/test_make_map.py::test_edge_017_over_long_default_keeps_its_slot tests/unit/test_make_map.py::test_ac_014_symbol_inventory_and_unparsed_signatures tests/property/test_structure_map.py::test_inv_007_signature_fidelity_survives_default_abbreviation tests/acceptance/test_structure_map.py::test_ac_014_committed_map_renders_over_long_default_in_place -v` | **`4 passed in 2.64s`** (exit 0) — EDGE-017 unit, AC-014 unit (re-derived), INV-007 property, AC-014 acceptance |
| The three structure-map modules | `uv run pytest tests/unit/test_make_map.py tests/property/test_structure_map.py tests/acceptance/test_structure_map.py -q` | **`58 passed in 45.25s`** (exit 0) — includes `test_ac_021_committed_map_matches_fresh_render` (green only because the map was regenerated here) and `test_nfr_002_map_line_budget` |
| Map regeneration (last step, after every `.py` edit — P-94) | `uv run python scripts/make_map.py` then `uv run python scripts/make_map.py --check` | **exit 0 / exit 0** |
| Ruff (changed paths) | `uv run ruff check scripts/make_map.py` | `All checks passed!` (exit 0) |
| Ruff format (changed paths) | `uv run ruff format --check scripts/make_map.py` | `1 file already formatted` (exit 0) |
| Types | `uv run mypy scripts/make_map.py` | `Success: no issues found in 1 source file` (exit 0) — `mypy scripts/` **is** a CI gate (`quality.yml` type-check job runs `mypy src/` + `mypy scripts/`), so this is the gate, not only a local check |
| Complexity | `uv run complexipy --max-complexity-allowed 15 scripts/make_map.py` | `All functions are within the allowed complexity.` (exit 0) — `_abbreviate_default` 1, `_drop_long_defaults` 4, `_signature` 3 |

The full `tests/` suite was **not** run here (light tier: Phase 5 targeted + smoke, full regression at the
S6.4 pre-merge gate).

### The regenerated `STRUCTURE.md` (REQ-021/AC-021, same commit as the `.py` change per REQ-023)

`git diff --numstat STRUCTURE.md` → `6 6` — **six** changed lines, line count **1 941 → 1 941** (NFR-002
unaffected), `…` mid-line so INV-006 hook cleanliness unaffected. Five are the §5.3 set; the sixth is new
and expected (finding **F-21** below).

| Map line | Before | After |
|---|---|---|
| `:452` | `docs/ — 225 files (process record)` | `docs/ — 231 files (process record)` — pre-existing staleness only (F-01/F-16: `main` moved with new planning records), **not** this fix |
| `:487` | `#### scripts/make_map.py (567 lines)` | `#### scripts/make_map.py (581 lines)` — the map's own per-module line count for the file the fix edits (**F-21**) |
| `:686` | `… session_ttl: timedelta=timedelta(days=7), reset_token_ttl: timedelta, max_failed_attempts: int=5, lockout_duration: timedelta, rp_id: str='localhost', rp_name: str='Python Template', origin: str, …` | `… session_ttl: timedelta=timedelta(days=7), reset_token_ttl: timedelta=…, max_failed_attempts: int=5, lockout_duration: timedelta=…, rp_id: str='localhost', rp_name: str='Python Template', origin: str=…, …` — `session_ttl` and `max_failed_attempts` unharmed |
| `:1675` | `build_auth_service(..., lockout_duration: timedelta, ..., reset_token_ttl: timedelta, ...)` | `build_auth_service(..., lockout_duration: timedelta=…, ..., reset_token_ttl: timedelta=…, ...)` |
| `:1676` | `build_memory_auth_service(..., lockout_duration: timedelta, ..., reset_token_ttl: timedelta, ...)` | `build_memory_auth_service(..., lockout_duration: timedelta=…, ..., reset_token_ttl: timedelta=…, ...)` |
| `:1816` | ``simple_template(name: str, subject: str='test', body_html: str='Test {{who}}', body_text: str='Test {{who}}')`` | ``simple_template(name: str='test', subject: str='Test {{who}}', body_html: str=…, body_text: str='Test {{who}}')`` — the positional shift is corrected |

`STRUCTURE.md` was **regenerated, never hand-edited**, as the last step after the only `.py` edit, and
verified with `--check` (exit 0) — the local `structure-map-check` pre-commit hook (`files: \.py$`,
check-only, REQ-023) is satisfied because the map is regenerated **in the same commit** as the `.py` change.

### New findings from S4.2

| ID | Finding | Disposition |
|---|---|---|
| **F-21** | §5.3/S4.1 predicted a **5-line** map diff. The actual diff is **6 lines**: the map renders a per-module line count (`#### scripts/make_map.py (567 lines)` → `(581 lines)`), and the fix adds 14 lines to that module. The S4.1 probe could not predict it — it ran a **scratch copy of the generator outside the repository** against the unmodified tree, so `make_map.py`'s own count never changed there. | Expected, not a defect: the line-count line is generated content of the artifact, and the map must be regenerated for the edited file (REQ-021). No signature line outside the §5.3 set changed, and the total stays 1 941, so NFR-002 holds. Recorded so the S5.1/S6.x reviewers do not read the sixth line as scope creep. |

### S4.3 refactor (2026-10-10)

**Verdict: near no-op.** The S4.2 code is already the minimal form that keeps the F-08 `None` guard and
INV-007 fidelity; **one stale comment line was corrected** and nothing structural was changed.

**Considered and rejected (no churn invented):**

| Option | Why rejected |
|---|---|
| Inline `_abbreviate_default` into the two comprehensions | It is called from **two** sites (`args.defaults`, `args.kw_defaults`); inlining duplicates the threshold ternary and the `ast.Name(id=…)` mechanism — a bigger diff and two places to keep in sync. Helper stays. |
| Push the `None` guard **into** `_abbreviate_default` (`ast.expr \| None -> ast.expr \| None`) so both call sites become identical one-liners | Measured, not assumed: typeshed declares `ast.arguments.defaults: list[ast.expr]`, so the widened return type fails the gate — `uv run mypy` on a probe of exactly that shape reports `List comprehension has incompatible type List[expr \| None]; expected List[expr]`. Keeping it type-exact would need an overload/TypeVar — more code than the one inline `None if d is None else …` guard. The current split (helper is non-`None`, only the caller that can hold `None` guards it) is the smallest type-exact form. |
| Collapse the three `"…"` constants (`_SUMMARY_MARKER`, `_FIELD_MARKER`, `_DEFAULT_MARKER`) into one `_ELLIPSIS` | Renames two **out-of-scope** constants for cosmetics and blurs the per-rule spec IDs each one carries (REQ-018 / REQ-017 / REQ-014 v2). The file's convention is deliberately one marker constant per rule; `_DEFAULT_MARKER` already matches the `_X_MARKER` naming. |
| Rename `_drop_long_defaults` (it abbreviates, it no longer drops) | Cosmetic, and the name is the reference key in this change's own records (triage §3, S4.1, S4.2, `docs/todo/complexipy-scripts.md`, `structure-map.md` S4.3) — S4.2 explicitly recorded "no rename". The docstring's first line already states the v2 behaviour ("abbreviate … in the default's own slot") and the paragraph below states why deletion was wrong, so the name is not load-bearing. |
| Shorten the 4-line `_DEFAULT_MARKER` comment or the `_drop_long_defaults` docstring | They carry the non-obvious *why* (`ast.unparse` cannot emit `…` from a `Constant`; the substitution is idempotent → INV-001; deleting a positional default shifts the kept ones → INV-007). Trim would remove evidence, not noise. |
| `_abbreviate_default` docstring | States the rule plus the "a substitution, never a deletion" constraint; the *why* lives once in `_drop_long_defaults` rather than twice. Note: `scripts/*` is ruff `D`-exempt (`per-file-ignores`), so this is a review judgement, not a gate. |

**The one change (comment only, 1 line, `scripts/make_map.py:73`):** the constant's comment still stated
the **pre-fix** rule — "a parameter default is rendered **only when** its `ast.unparse` text is at most
this long" — which is exactly the drop semantics the amended REQ-014 v2 removed (an over-long default is
now rendered as `…` in its own slot). Corrected to
`# REQ-014 v2: a parameter default is rendered verbatim only when its ast.unparse text is at most this long.`
Behaviour-identical, and kept to **one line** on purpose: `make_map.py` stays at **581 lines**, so the map's
per-module count line for the file (F-21) does not move and `STRUCTURE.md` is **byte-identical** — no map
churn, no second regeneration.

**Gates (all run in this worktree after the edit):**

| Gate | Command | Result |
|---|---|---|
| Map regenerate + check | `uv run python scripts/make_map.py` then `--check` | exit **0** / **0**; `STRUCTURE.md` **1 941 lines** (unchanged) and **not modified** in the working tree (`git status` shows only `scripts/make_map.py`) |
| Witnesses (§4.5) | the four node ids, `-v` | **4 passed** |
| Targeted set | `uv run pytest tests/unit/test_make_map.py tests/property/test_structure_map.py tests/acceptance/test_structure_map.py -q` | **58 passed** (unchanged from S4.2) |
| Lint | `uv run ruff check scripts/make_map.py` | `All checks passed!` (exit 0) |
| Format | `uv run ruff format --check scripts/make_map.py` | `1 file already formatted` (exit 0) |
| Types | `uv run mypy scripts/make_map.py` | `Success: no issues found in 1 source file` (exit 0) |
| Complexity | `uv run complexipy --max-complexity-allowed 15 scripts/make_map.py` | `All functions are within the allowed complexity.` (exit 0) — `_abbreviate_default` 1, `_drop_long_defaults` 4, `_signature` 3 (unchanged) |

No test, spec, traceability, changelog or `pyproject.toml` file was touched; the full `tests/` suite was
not run (light tier — full regression stays the S6.4 pre-merge gate).

### S4.4 Phase 4 close-out (2026-10-10)

Phase 4 is closed at HEAD `db425ae`, working tree clean. This change is an **ISSUE**, so there is **no task
DAG** and no `.github/task-runner/tasks.json` to set `VERIFIED` (Phase 2 is skipped per the Phase Matrix);
the state-machine record is this section.

**Commit list** (`git log --oneline main..HEAD`, exactly the Phase 3/4 commits, nothing else):

| SHA | Subject |
|---|---|
| `0ecf7bc` | `test(map-default-drop-shift): reproduction witnesses for EDGE-017/INV-007 + re-derived AC-014 (RED)` |
| `5b51614` | `docs(map-default-drop-shift): S3.2 RED gate re-check` |
| `785da7a` | `docs(map-default-drop-shift): S4.1 fix-target re-location` |
| `0c73790` | `fix(make_map): keep an over-long default in its slot as … (map-default-drop-shift)` |
| `db425ae` | `refactor(make_map): correct the stale _DEFAULT_MAX_CHARS comment (map-default-drop-shift)` |

**PR B file set so far** (`git diff --name-status main...HEAD`) — exactly the §5.4 prediction, all six `M`:
`scripts/make_map.py`, `STRUCTURE.md`, `tests/unit/test_make_map.py`, `tests/property/test_structure_map.py`,
`tests/acceptance/test_structure_map.py`, `docs/verification/map-default-drop-shift.md`.
Still **absent** by design: `docs/verification/traceability.md` (S5.3, F-09), `CHANGELOG.md` and
`pyproject.toml` (S6.4 version bump), `docs/specs/` (only PR A), `docs/todo/`, `docs/questions/`
(orchestrator-owned on `main`).

**Independent re-run of the targeted GREEN set** (this step, at `db425ae`, nothing re-implemented):

| Check | Command | Result line |
|---|---|---|
| The four §4.5 node ids | the `green_command` four node ids, `-v` | **`4 passed in 2.59s`** (exit 0) |
| The three structure-map modules | `uv run pytest tests/unit/test_make_map.py tests/property/test_structure_map.py tests/acceptance/test_structure_map.py -q` | **`58 passed in 67.52s`** (exit 0) |
| Map freshness (check only — the generator was **not** re-run without `--check`) | `uv run python scripts/make_map.py --check` | **exit 0**, no output, `STRUCTURE.md` unmodified afterwards |

**State machine:** `RED_CONFIRMED` (S3.2 gate re-check at `0ecf7bc`, `4 failed`) → `IMPLEMENTING` (S4.1
fix-target re-location at `5b51614`) → **`GREEN`** (S4.2 GREEN table: `4 passed` on the four witnesses,
`58 passed` on the three modules, `make_map.py --check` exit 0, ruff/format/mypy/complexipy clean) →
**`REFACTORED`** (S4.3 verdict: near no-op, one stale comment line at `scripts/make_map.py:73` corrected,
file still 581 lines so `STRUCTURE.md` stayed byte-identical; all S4.3 gates re-run clean).

**Full regression suite is deliberately deferred** to the **S6.4 pre-merge gate** per the light-tier
qualification (§6): Phase 5 runs targeted + smoke instead, and `uv run pytest tests/ -v` must pass before
the PR opens, with the result recorded in the review report. Phase 4 ran no full-suite command.

**Gate ◆ Phase 4 (GREEN + REFACTORED): closed.** Phase 5 (`S5.1`) may start.

## Phase 5 — S5.1 targeted + smoke test evidence (2026-10-10)

HEAD at entry: `fada820` (`docs(map-default-drop-shift): Phase 4 close-out (GREEN, REFACTORED)`), working
tree clean. This step **ran tests only** — nothing was edited, regenerated, weakened, skipped or
deselected, and `git status --porcelain` is **empty** after the runs (the map is untouched:
`uv run python scripts/make_map.py --check` → **exit 0**, no output, run check-only per P-94).

**Light tier (§6): the full regression suite (`uv run pytest tests/`) is deliberately NOT run here.**
Under the light-tier qualification the **full regression suite is the Phase 6 pre-merge gate (S6.4)** —
`uv run pytest tests/ -v` must pass before the PR opens and its result is recorded in the review report.
Phase 5 runs the reproduction witnesses, the covering tests named in §6, the affected feature's test set,
and an acceptance-category smoke sweep instead.

### 5.1.1 The four §4.5 witnesses (reproduction tests GREEN)

- **command:** `uv run pytest tests/unit/test_make_map.py::test_edge_017_over_long_default_keeps_its_slot tests/unit/test_make_map.py::test_ac_014_symbol_inventory_and_unparsed_signatures tests/property/test_structure_map.py::test_inv_007_signature_fidelity_survives_default_abbreviation tests/acceptance/test_structure_map.py::test_ac_014_committed_map_renders_over_long_default_in_place -v`
- **result:** **`4 passed in 3.31s`** (exit 0) — `test_ac_014_symbol_inventory_and_unparsed_signatures`, `test_edge_017_over_long_default_keeps_its_slot`, `test_ac_014_committed_map_renders_over_long_default_in_place`, `test_inv_007_signature_fidelity_survives_default_abbreviation`. 0 failed, 0 skipped, 0 xfail, 0 errors.

### 5.1.2 The affected feature's test set (structure-map: unit + property + acceptance)

- **command:** `uv run pytest tests/unit/test_make_map.py tests/property/test_structure_map.py tests/acceptance/test_structure_map.py -v`
- **result:** **`58 passed in 44.77s`** (exit 0) — 58 collected, **0 failed, 0 skipped, 0 deselected**.
- The two witnesses the light-tier note in §6 calls out are among the passes:
  `tests/acceptance/test_structure_map.py::test_ac_021_committed_map_matches_fresh_render` **PASSED**
  (red on `main` at triage, §3.5/F-01/F-02/F-16 — green because Phase 4 regenerated the map in the same
  commit as the `.py` change) and `tests/acceptance/test_structure_map.py::test_nfr_002_map_line_budget`
  **PASSED** (NFR-002, the map stays ≤ 2 000 lines at 1 941).

### 5.1.3 Every covering test named in §6, per module

§6 names the covering tests as `tests/unit/test_make_map.py`, `tests/property/test_structure_map.py` and
`tests/acceptance/test_structure_map.py`. Each was also run **on its own** so each covering module's result
is recorded separately and reconciles against the §3.5 baseline:

| Covering module (as named in §6) | Command | Result line | Reconciliation vs the §3.5/§6 baseline |
|---|---|---|---|
| `tests/unit/test_make_map.py` | `uv run pytest tests/unit/test_make_map.py -v` | **`19 passed in 4.67s`** (exit 0) | §3.5 recorded unit + property = **24 passed**; unit is now 19 because Phase 3 added `test_edge_017_over_long_default_keeps_its_slot` (+1) |
| `tests/property/test_structure_map.py` | `uv run pytest tests/property/test_structure_map.py -v` | **`7 passed in 28.41s`** (exit 0) | 7 = the baseline's 6 + the new `test_inv_007_signature_fidelity_survives_default_abbreviation` (+1); unit + property = **26 = 24 + 2**, no baseline test lost |
| `tests/acceptance/test_structure_map.py` | `uv run pytest tests/acceptance/test_structure_map.py -v` | **`32 passed in 13.34s`** (exit 0) | §3.5 recorded **1 failed, 30 passed**; now **32 passed** = 30 + the new `test_ac_014_committed_map_renders_over_long_default_in_place` (+1) + the previously **pre-existing** `test_ac_021_committed_map_matches_fresh_render` turning green (F-01/F-02/F-16) |

**No covering test regressed:** every module is fully green, and the only count changes are the three new
witnesses plus the pre-existing AC-021 red resolved by the Phase 4 regeneration.

### 5.1.4 Smoke sweep — the acceptance category as a whole

- **command:** `uv run pytest tests/acceptance -q`
- **result:** **`396 passed, 1 skipped in 62.93s (0:01:02)`** (exit 0; wall clock `1m4s` for the whole
  `uv run` invocation). Not slow — run in full, nothing substituted or narrowed.
- The single skip is **pre-existing and host-dependent**, not produced by this step or this change:
  `tests/acceptance/filemanagement/test_filemanagement.py:364` — `test_ac_031_symlink_rejected` calls
  `pytest.skip("symlinks not available on this host")` from its own `except OSError` guard around
  `os.symlink` (Windows host without symlink privilege). That file is **not** in this branch's diff
  (`git diff --name-status main...HEAD` lists only `STRUCTURE.md`, `docs/verification/map-default-drop-shift.md`,
  `scripts/make_map.py`, `tests/unit/test_make_map.py`, `tests/property/test_structure_map.py`,
  `tests/acceptance/test_structure_map.py`). No test was skipped, marked or deselected by this step.

### 5.1.5 Gate summary

| Check | Command | Result |
|---|---|---|
| Reproduction witnesses | the four §4.5 node ids, `-v` | **4 passed** (exit 0) |
| Affected feature's test set | the three structure-map modules, `-v` | **58 passed** (exit 0) |
| Covering tests per §6 | each of the three modules, `-v` | **19 / 7 / 32 passed** (exit 0 each) |
| Acceptance smoke | `uv run pytest tests/acceptance -q` | **396 passed, 1 skipped** (exit 0, 62.93s) |
| Full regression suite | `uv run pytest tests/ -v` | **not run here — deferred to the S6.4 pre-merge gate** (light tier, §6) |
| Tree state after the step | `git status --porcelain` | **empty** (nothing written by this step except this record) |
| Map freshness (check only) | `uv run python scripts/make_map.py --check` | **exit 0** |

### New findings from S5.1

| ID | Finding | Disposition |
|---|---|---|
| **F-22** | The acceptance-category smoke sweep reports **1 skipped** (`test_ac_031_symlink_rejected`, `tests/acceptance/filemanagement/test_filemanagement.py:364`) because `os.symlink` raises `OSError` on this Windows host. The skip is inside the test's own platform guard and predates this change. | No action. Recorded so the S6.4 full-suite count is read correctly: a `skipped` there is a host capability, not a weakened or deselected test, and the S6.4 run must report the same 1 skip on this host. |

**Gate ◆ S5.1: passed** — reproduction witnesses GREEN, the affected feature's test set fully GREEN
(including AC-021 and NFR-002), every §6 covering module GREEN, acceptance smoke GREEN. Lint and type
checks are **S5.2**; the traceability rows are **S5.3**; the full regression suite stays the **S6.4**
pre-merge gate. Next: **S5.2 Lint + types**.

## Phase 5 — S5.2 lint + types evidence (2026-10-10)

Every command below is the **CI invocation**, read off the workflow files in this worktree
(`.github/workflows/lint.yml`, `quality.yml`, `spec-validation.yml`), and was run in this worktree at
HEAD `7d6ac22` with a clean working tree. This is the **one whole-repo ruff sweep** of the change
(AGENTS.md "Tooling & Execution Environment" scope split: per-task steps lint only their changed paths;
the repo-wide sweep runs once at Phase 5, matching `lint.yml` exactly).

### 5.2.0 What this branch changed — the basis for every pre-existing / introduced call

`git diff --name-status main...HEAD`:

```text
M	STRUCTURE.md
M	docs/verification/map-default-drop-shift.md
M	scripts/make_map.py
M	tests/acceptance/test_structure_map.py
M	tests/property/test_structure_map.py
M	tests/unit/test_make_map.py
```

Consequences used below: **`src/` is untouched** (no bandit or `mypy src/` finding can be introduced by
this branch), **`pyproject.toml` and the lockfile are untouched** (no dependency finding is possible),
and the only lint/type-visible files this branch touches are `scripts/make_map.py` and the three
structure-map test modules.

### 5.2.1 The gate set

| # | Check | Command (as CI runs it) | Result line (verbatim) | Exit | Finding classification |
|---|---|---|---|---|---|
| 1 | Lint (whole-repo sweep) | `uv run ruff check .` | `All checks passed!` | **0** | **No finding at all** — nothing to classify as pre-existing or introduced; the repo is lint-clean at HEAD, exactly as CI sees it |
| 2 | Formatting | `uv run ruff format --check .` | `343 files already formatted` | **0** | No finding — clean at HEAD, so nothing introduced by the branch's `scripts/make_map.py` / test edits |
| 3 | Types, `src/` (gate) | `uv run mypy src/` | `Success: no issues found in 84 source files` | **0** | No finding; `src/` is not in this branch's diff, so this result is identical to `main`'s |
| 4 | Types, `scripts/` (gate) | `uv run mypy scripts/` | `Success: no issues found in 4 source files` | **0** | No finding — this is the tree the branch **does** change (`scripts/make_map.py`), and it is clean |
| 5 | Traceability referential integrity | `uv run python scripts/check_traceability.py` | `Traceability: PASS (881 matrix rows, 136 spec IDs, 804 test functions)` | **0** | **No finding** — see 5.2.2: the S5.3 rows are still owed, but the script cannot flag them |
| 6 | Cognitive complexity (CI scope: `src tests`) | `uv run complexipy src tests --max-complexity-allowed 15` | `All functions are within the allowed complexity.` | **0** | No finding; the branch's three new/edited test functions are inside the limit (5.2.3) |
| 7 | Dependencies | `uv run deptry .` | `Scanning 91 files...` / `Success! No dependency issues found.` | **0** | No finding; dependencies did not change (no `pyproject.toml`/lock in the diff) |
| 8 | Security | `uv run bandit -q -r src/` | 48 `[tester] WARNING nosec encountered (B105), but no failed test on file ...` lines, **no issue report**, no `Issue:` line | **0** | The 48 `nosec`-comment warnings are **pre-existing** — they are all in `src/backend/{authentication,mail,usermanagement}/feature_actions.py`, and `src/` is not in this branch's diff |

**ruff: clean. mypy: clean (both `src/` and `scripts/`). check_traceability: exit 0.**

### 5.2.2 check_traceability — why the expected S5.3 finding does not appear

The step brief predicted a possible finding for the missing **INV-007 / EDGE-017** rows (they are written
by **S5.3**). The script exits **0** instead, and that is correct, not a missed check:
`scripts/check_traceability.py` enforces referential integrity only for **`REQ-`/`AC-`** ids
(`REQ_OR_AC_RE.fullmatch(id_)` in check (1)), matched **globally** across the matrix, and `INV-`/`EDGE-`
rows are not required by it. `AC-014` already has matrix rows (from other specs — ids are namespaced per
spec file but the script matches by id alone), and the new witnesses are `INV-007`/`EDGE-017`/`AC-014`
shaped rows the script does not demand. Check (3) — every backticked test name in the matrix must exist
under `tests/` — also passes, so Phase 3/4 renamed or removed no test a matrix row cites.

**The rows are still owed and S5.3 must still write them** (AGENTS.md: every normative requirement needs
at least one GREEN test row; the CI script is a floor, not the gate). Nothing was "fixed" here.

### 5.2.3 Complexity headroom for the branch's own test functions (from the gate run in 5.2.1 #6)

`test_inv_007_signature_fidelity_survives_default_abbreviation` **14** (limit 15 — the tightest function
this branch adds), `test_ac_014_symbol_inventory_and_unparsed_signatures` **10**,
`test_edge_017_over_long_default_keeps_its_slot` **4**. All pass; the 14 is recorded so a future edit to
that property test does not silently cross the gate.

### 5.2.4 Informational only — `scripts/` is not in the complexity gate

CI's complexity job scopes `src tests`; `scripts/` is the separate `complexipy-scripts` TODO, so this was
**not** run as a gate. Informational run `uv run complexipy scripts --max-complexity-allowed 15` exits 1
with **4 pre-existing over-limit functions**: `check_traceability.py::check` 17,
`check_traceability.py::matrix_rows` 19, `validate_task_dag.py::check_acyclic` 22,
`verify_spec.py::main` 22. **`scripts/make_map.py` — the file this branch changes — is fully within the
limit (max 12, `_member_lines`)**, so this branch adds nothing to that TODO's debt.

### 5.2.5 Step hygiene

- No file was edited by this step: every check was already clean, so there was nothing trivial to fix and
  no finding was "fixed" out of scope. The only write is this section.
- `git status --porcelain` before the step: empty. After the step: only
  `docs/verification/map-default-drop-shift.md`.
- The full `tests/` suite was **not** run here (S5.1 record; full regression remains the **S6.4**
  pre-merge gate per the light-tier rule, §6).

### New findings from S5.2

| ID | Finding | Disposition |
|---|---|---|
| **F-23** | `uv run bandit -q -r src/` emits **48 `nosec encountered (B105), but no failed test`** warnings — redundant `# nosec B105` comments on `feature_actions.py` permission-key strings in authentication, mail and usermanagement. Exit code 0, so CI's security job is green; the noise is pre-existing (`src/` is not in this branch's diff). | No action in this change (out of scope, `src/` untouched). Worth a Problem Log / future chore: either drop the redundant `nosec` comments or run bandit with `--no-nosec-warnings`-style quieting. |
| **F-24** | `check_traceability.py` cannot flag a missing `INV-`/`EDGE-` row (it enforces rows for `REQ-`/`AC-` only), so a change that forgets its invariant/edge rows passes CI. This change's INV-007/EDGE-017 rows are exactly that case. | S5.3 writes the rows regardless (the AGENTS.md obligation, not the script, is the gate). Recorded for the after-workflow-optimization: the script's floor is weaker than the written rule. |

**Gate ◆ S5.2: passed** — ruff clean (whole repo, matching CI), ruff format clean, mypy clean over `src/`
and `scripts/`, `check_traceability.py` exit 0, complexipy green over CI's scope, deptry clean, bandit
exit 0 (pre-existing `nosec` warnings only). **Zero findings introduced by this branch.** Next: **S5.3
Update traceability**.

## Phase 5 — S5.3 traceability update (2026-10-10)

HEAD at entry: `9d93c94` (`docs(map-default-drop-shift): S5.2 lint + types evidence`), `git status
--porcelain` **empty** (checked before writing anything — nothing of another step was in the tree).
This step writes **only** `docs/verification/traceability.md` and this file: no `src/`, no `tests/`, no
spec, no `AGENTS.md`/`CHANGELOG.md`, no `STRUCTURE.md`, no `docs/todo/` or `docs/questions/`. **No test
was run** — the evidence cited in the new rows is the S5.1 record (`7d6ac22`), and the full regression
suite stays the **S6.4** pre-merge gate (light tier, §6).

### 5.3.1 Where the rows go

The matrix section for this spec is **`## Structure Map Matrix (structure-map FEATURE — S5.3,
2026-10-09)`** (`docs/verification/traceability.md`, the section that lists the structure-map REQ/AC, INV,
EDGE and NFR rows in four tables). The rows were placed in the existing tables so the ID order stays
ascending, and a dated amendment note was added to that section's preamble so a reader sees why the ID and
row counts differ from the 2026-10-09 record.

### 5.3.2 Rows added / updated

| Row | Action | Witness cited (exists under `tests/`) | Status cell (gate record, change + date inside the cell) |
|---|---|---|---|
| `INV-007 (REQ-014)` | **added** (INV table, after INV-006) | `test_inv_007_signature_fidelity_survives_default_abbreviation` (`tests/property/test_structure_map.py:628`) | `GREEN (map-default-drop-shift S5.1 targeted+smoke: property module 7 passed, structure-map modules 58 passed, 2026-10-10, commits 0ecf7bc RED → 0c73790 fix, evidence 7d6ac22; ID added by Spec Amendment PR A, merge d8ba07f)` |
| `EDGE-017 (REQ-014)` | **added** (EDGE table, after EDGE-016) | `test_edge_017_over_long_default_keeps_its_slot` (`tests/unit/test_make_map.py:1028`) | `GREEN (… unit module 19 passed, structure-map modules 58 passed …)` — same gate record |
| `REQ-014 / AC-014` | **updated in place** (the only row of the 27 this change touched: PR A amended its wording, Phase 3 re-derived its witness) | `test_ac_014_symbol_inventory_and_unparsed_signatures` (`tests/unit/test_make_map.py:996`, re-derived) **plus** `test_ac_014_committed_map_renders_over_long_default_in_place` (`tests/acceptance/test_structure_map.py:1506`, new acceptance witness) | `GREEN (map-default-drop-shift S5.1 targeted+smoke: 4 reproduction witnesses passed, structure-map modules 58 passed — 19 unit / 7 property / 32 acceptance, acceptance smoke 396 passed + 1 pre-existing host skip, 2026-10-10, commits 0ecf7bc RED → 0c73790 fix, evidence 7d6ac22; wording amended by Spec Amendment PR A, merge d8ba07f. Prior record as observed by structure-map: S5.1 full suite 816 passed/1 skipped; S5.2 clean; commit 3ec204c, 2026-10-09)` |

Every Status cell starts with a **declared** value (`GREEN`) and carries this change's name and date inside
the cell (Q-129 convention B), so the counts are read as *this change's* gate, not a refresh of
structure-map's. No number was invented: `4 passed`, `58 passed (19 / 7 / 32)` and `396 passed, 1 skipped`
are the verbatim S5.1 result lines (§5.1.1–§5.1.4).

**Not touched (convention B).** The other 26 REQ/AC rows, INV-001…INV-006, EDGE-001…EDGE-016, all 7 NFR
rows, and every row of every other change's section are byte-identical to `9d93c94` — this change did not
re-run and therefore did not refresh them. The only prose edits are the section's dated amendment note and
the two sub-headings' row counts (`INV (6 rows …)` → `INV (7 rows …)`, `EDGE (16 rows)` → `EDGE (17 rows)`),
corrected because the tables they head now contain the added rows (finding F-25).

Matrix totals after the step: **58 rows in the structure-map section** (27 REQ/AC + 7 INV + 17 EDGE +
7 NFR) covering the spec's **85 IDs** (27 REQ + 27 AC + 7 INV + 17 EDGE + 7 NFR, counted with
`grep -o "\bREQ-[0-9]\{3\}\b" docs/specs/structure-map.md | sort -u | wc -l` per prefix).

### 5.3.3 Checker output (the CI `traceability` job command)

| Moment | Command | Verbatim output | Exit |
|---|---|---|---|
| Before the edit (baseline at `9d93c94`) | `uv run python scripts/check_traceability.py` | `Traceability: PASS (881 matrix rows, 136 spec IDs, 804 test functions)` | **0** |
| After the edit | `uv run python scripts/check_traceability.py` | `Traceability: PASS (883 matrix rows, 136 spec IDs, 804 test functions)` | **0** |

Row count **+2** (the two added rows; the REQ-014/AC-014 row was updated in place, not added), spec IDs and
test-function count unchanged — this step added no ID and no test.

### 5.3.4 F-09 and F-24 dispositions

- **F-09 — closed by this step.** The rows PR A deliberately left out (the checker's rule (3) fails any row
  citing a backticked test function that does not exist under `tests/`, and the witnesses did not exist
  before Phase 3 `0ecf7bc`) are now written, and rule (3) passes with them: all four cited functions are
  defined under `tests/` (verified by `grep -n "def test_…"` at 5.3.2 and by the checker's exit 0).
- **F-24 — disposition: the written rule is the gate, and it is satisfied.** The checker still cannot flag
  a missing `INV-`/`EDGE-` row, so its PASS is not evidence that INV-007/EDGE-017 have rows; the rows
  themselves are. They are now present, each with a GREEN witness, so the AGENTS.md obligation ("every
  normative requirement MUST have at least one executable test") holds for the two IDs this change added.
  The script's weakness stands as recorded for the after-workflow-optimization — nothing was changed in
  `scripts/`.

### 5.3.5 Cross-check against spec §11 (not a gate, a consistency read)

The matrix citations match the spec's own §11 Test Strategy rows exactly — `structure-map.md:533`
(AC-014 → `test_ac_014_symbol_inventory_and_unparsed_signatures`), `:553` (INV-007 →
`test_inv_007_signature_fidelity_survives_default_abbreviation`), `:570` (EDGE-017 →
`test_edge_017_over_long_default_keeps_its_slot`). The acceptance witness
`test_ac_014_committed_map_renders_over_long_default_in_place` is an **extra** witness this change wrote
(§4.2) and is not listed in §11 — the matrix may cite more witnesses than the spec's strategy table names;
the reverse would be a finding.

### New findings from S5.3

| ID | Finding | Disposition |
|---|---|---|
| **F-25** | The structure-map section's sub-headings carry hard-coded row counts (`### INV (6 rows, property witnesses)`, `### EDGE (16 rows)`). Adding a row to a table makes its heading stale, and `check_traceability.py` does not police prose counts, so the staleness is invisible to CI. | Corrected in this step to `7 rows` / `17 rows`, each annotated with the change and date that added the row, and the section preamble's `83 IDs` / `56 rows` record is left intact with a dated amendment note stating the new totals (85 IDs, 58 rows) — the original sentence stays as the historical record of the 2026-10-09 step. Recorded for the after-workflow-optimization: counts embedded in headings are a drift source. |

**Gate ◆ S5.3: passed** — `INV-007` and `EDGE-017` rows added and the touched `REQ-014 / AC-014` row
updated, all citing test functions that exist in this worktree; `check_traceability.py` exits **0**
(`PASS (883 matrix rows, 136 spec IDs, 804 test functions)`). Next: **S5.4 Verification report**.

## Phase 5 — S5.4 verification report (2026-10-10)

HEAD at entry: `d1fa73f` (`docs(map-default-drop-shift): S5.3 traceability rows for INV-007/EDGE-017 +
REQ-014/AC-014`), `git status --porcelain` **empty** (checked before writing anything). This step writes
**only this file**: no `src/`, no `tests/`, no spec, no `docs/verification/traceability.md` (S5.3 owns it),
no `CHANGELOG.md`, no `pyproject.toml`, no `STRUCTURE.md`, no `docs/todo/` or `docs/questions/`, no PR, no
version bump. **No test was run beyond the targeted re-runs named in 5.4.2; the full `tests/` suite was
deliberately not run** (light tier, §6 — it is the S6.4 pre-merge gate, 5.4.3). No test was modified,
weakened, deleted or deselected at any point in Phase 5.

Normative basis for the report: the triage record (§1–§6) + the **amended** spec
`docs/specs/structure-map.md` **v2** (Spec Amendment PR A #79, merged `d8ba07f`) — amended **REQ-014**
(`:270`, rule text `:287-294`) and **AC-014** (`:429`), new **INV-007** (§8, `:454`) and new **EDGE-017**
(§9, `:476`). The fix is `0c73790` (`scripts/make_map.py`) with the S4.3 comment-only refactor `db425ae`,
and the regenerated `STRUCTURE.md` committed **in the same commit** as the `.py` change (REQ-023).

### 5.4.1 Affected-ID coverage (spec coverage)

One row per normative ID **this change owns** — the two IDs PR A amended and the two it added. Witness
functions and their line numbers were re-read from the tree at `d1fa73f`; statuses are the S5.1 gate
(§5.1.1) re-confirmed by this step's targeted re-run (5.4.2 #1).

| ID (spec location) | Witnessing test function(s) | Category | Observed status |
|---|---|---|---|
| **REQ-014** — amended by PR A v2 (`:270`, rule text `:287-294`) | `test_ac_014_symbol_inventory_and_unparsed_signatures` (`tests/unit/test_make_map.py:996`, re-derived in place for the amended wording) **and** `test_ac_014_committed_map_renders_over_long_default_in_place` (`tests/acceptance/test_structure_map.py:1506`, new witness on the committed artifact) | **unit + acceptance** | **GREEN** — both pass (this step: `4 passed in 3.10s`, exit 0; S5.1 §5.1.1 `4 passed in 3.31s`) |
| **AC-014** — amended by PR A v2 (`:429`) | the same two witnesses (the AC-014 row cites both) | **unit + acceptance** | **GREEN** — same run; the re-derived unit witness keeps every pre-existing needle and adds three positive `=…` needles, so it is strictly stronger than the pre-amendment witness, never weaker (§4.4, F-05) |
| **INV-007** — added by PR A v2 (§8 Invariants, `:454`) | `test_inv_007_signature_fidelity_survives_default_abbreviation` (`tests/property/test_structure_map.py:628`) | **property** (Hypothesis over default length × parameter slot — the category the spec's §11 row `:553` requires for an invariant) | **GREEN** — same run; property module 7 passed (§5.1.3) |
| **EDGE-017** — added by PR A v2 (§9 Edge Cases, `:476`) | `test_edge_017_over_long_default_keeps_its_slot` (`tests/unit/test_make_map.py:1028`) | **unit** | **GREEN** — same run; unit module 19 passed (§5.1.3). Covers all three slots plus the two branches unreachable in the tree today (F-12) |

**Spec coverage: 4 / 4 affected IDs have at least one GREEN witness = 100%.** Every witness named above is
also a matrix row in `docs/verification/traceability.md` (S5.3 §5.3.2: the `REQ-014 / AC-014` row updated
in place, `INV-007` and `EDGE-017` rows added), each Status cell starting with the declared value `GREEN`
and carrying this change's name and date inside the cell (Q-129 convention B). The matrix citations match
the spec's own §11 Test Strategy rows (`structure-map.md:533`, `:553`, `:570`) exactly; the acceptance
witness is an **extra** witness this change wrote (§4.2), which is permitted.

**Not counted in the coverage figure** — the IDs this change only had to leave unbroken (§2), each green in
the same runs: `REQ-021 / AC-021` (`test_ac_021_committed_map_matches_fresh_render` — red on `main` at
triage, green since the Phase 4 regeneration), `REQ-019 / INV-001` (determinism — `make_map.py --check`
exit 0, idempotent placeholder), `INV-006` (hook cleanliness — `…` is mid-line), `NFR-002`
(`test_nfr_002_map_line_budget`, map still 1 941 lines ≤ 2 000), `REQ-023 / AC-023` (the map is regenerated
in the same commit as the `.py` change).

### 5.4.2 Gate set actually run (light tier)

Every result below is copied verbatim from the S5.1 / S5.2 / S5.3 sections of this file, except the two
rows marked *re-run here*, which this step executed at `d1fa73f`.

| # | Gate (light-tier ISSUE) | Command | Result | Exit | Source |
|---|---|---|---|---|---|
| 1 | Reproduction witnesses GREEN (the four §4.5 node ids) | `uv run pytest tests/unit/test_make_map.py::test_edge_017_over_long_default_keeps_its_slot tests/unit/test_make_map.py::test_ac_014_symbol_inventory_and_unparsed_signatures tests/property/test_structure_map.py::test_inv_007_signature_fidelity_survives_default_abbreviation tests/acceptance/test_structure_map.py::test_ac_014_committed_map_renders_over_long_default_in_place -v` | **`4 passed in 3.10s`** — 0 failed, 0 skipped, 0 xfail, 0 errors | **0** | *re-run here* (S5.1 §5.1.1: `4 passed in 3.31s`) |
| 2 | Covering tests named in §6, each module on its own | `uv run pytest tests/unit/test_make_map.py -v` / `… tests/property/test_structure_map.py -v` / `… tests/acceptance/test_structure_map.py -v` | **`19 passed`** / **`7 passed`** / **`32 passed`** — reconciles against the §3.5 baseline with no test lost (§5.1.3) | 0 / 0 / 0 | S5.1 §5.1.3 |
| 3 | Affected feature's test directory (structure-map: unit + property + acceptance) | `uv run pytest tests/unit/test_make_map.py tests/property/test_structure_map.py tests/acceptance/test_structure_map.py -v` | **`58 passed in 44.77s`** — 0 failed, 0 skipped, 0 deselected; includes AC-021 and NFR-002 green | **0** | S5.1 §5.1.2 |
| 4 | Smoke sweep | `uv run pytest tests/acceptance -q` | **`396 passed, 1 skipped in 62.93s`** — the single skip is the pre-existing host-dependent `test_ac_031_symlink_rejected` guard (F-22) | **0** | S5.1 §5.1.4 |
| 5 | Lint — the one whole-repo sweep of the change (matches `lint.yml`) | `uv run ruff check .` | `All checks passed!` | **0** | S5.2 5.2.1 #1 |
| 6 | Formatting | `uv run ruff format --check .` | `343 files already formatted` | **0** | S5.2 5.2.1 #2 |
| 7 | Types (CI gate, `quality.yml`) | `uv run mypy src/` | `Success: no issues found in 84 source files` | **0** | S5.2 5.2.1 #3 |
| 8 | Types over the tree the change edits | `uv run mypy scripts/` | `Success: no issues found in 4 source files` | **0** | S5.2 5.2.1 #4 |
| 9 | Traceability referential integrity (ISSUE Phase 5 obligation 11) | `uv run python scripts/check_traceability.py` | `Traceability: PASS (883 matrix rows, 136 spec IDs, 804 test functions)` | **0** | *re-run here* (identical to S5.3's post-edit run, §5.3.3) |
| 10 | Map freshness (check only, P-94) | `uv run python scripts/make_map.py --check` | no output, `STRUCTURE.md` unmodified | **0** | S5.1 §5.1.5 / S4.4 |
| 11 | Cognitive complexity, CI scope | `uv run complexipy src tests --max-complexity-allowed 15` | `All functions are within the allowed complexity.` (tightest function this branch adds: 14 / limit 15, §5.2.3) | **0** | S5.2 5.2.1 #6 |
| 12 | Dependencies | `uv run deptry .` | `Success! No dependency issues found.` (no dependency was added; `pyproject.toml`/lock not in the diff) | **0** | S5.2 5.2.1 #7 |
| 13 | Security | `uv run bandit -q -r src/` | no issue report; 48 pre-existing `nosec`-comment warnings only (F-23) | **0** | S5.2 5.2.1 #8 |

**ruff: clean. mypy: clean (`src/` and `scripts/`). check_traceability: exit 0.** Zero findings were
introduced by this branch (S5.2 5.2.1 classification column).

### 5.4.3 What the light tier defers — open item for S6.4

Under the light-tier qualification (§6, AGENTS.md "Light ISSUE tier"), Phase 5 ran **targeted + smoke**
instead of the full regression suite. Therefore:

- **OPEN ITEM → S6.4 (Phase 6 pre-merge gate):** `uv run pytest tests/ -v` — the **full regression suite**
  — MUST pass **before the PR opens**, and its result MUST be recorded in the Phase 6 review report
  (AGENTS.md Phase 5 ISSUE item 9 / Light ISSUE tier; skill "MUST → ISSUE"). It was **not** run in Phase 5
  by design, and it is the only light-tier gate not yet green.
- Reading the S6.4 count correctly: on this host the acceptance category reports **1 skipped**
  (`test_ac_031_symlink_rejected`, F-22) — a host capability, not a deselected or weakened test.
- If `test_ac_021_committed_map_matches_fresh_render` is red at that gate, the cause is the map, not the
  fix: regenerate (`uv run python scripts/make_map.py`) and re-commit the map with the `.py` change, never
  hand-edit `STRUCTURE.md`; the second, CRLF-dependent cause of that test is F-03 (mitigation: regenerate
  immediately before the full-suite run).
- Also owed at S6.4 (not Phase 5, recorded here per the verify skill "All types"): the `CHANGELOG.md`
  entry under `## [Unreleased]` → `Fixed` (F-20; it does **not** exist at this phase) and the `patch`
  version bump `1.1.0 → 1.1.1` with the entries moved to `## [1.1.1] - <date>` in the bump commit.

### 5.4.4 Phase 5 findings ledger (F-21…F-25)

| ID | Recorded at | Finding (short) | Disposition | Open after Phase 5? |
|---|---|---|---|---|
| **F-21** | S4.2 | The map diff is **6** lines, not the predicted 5: the map renders its own per-module line count (`scripts/make_map.py` 567 → 581 lines), which the out-of-repo probe could not predict. | Expected, not a defect — generated content of the artifact; total stays 1 941 lines so NFR-002 holds, and no signature line outside the §5.3 set changed. Recorded so S6.x reviewers do not read the sixth line as scope creep. | **no** |
| **F-22** | S5.1 | The acceptance smoke sweep reports **1 skipped** (`test_ac_031_symlink_rejected`) — the test's own `os.symlink` platform guard on a Windows host without symlink privilege. | No action; pre-existing and outside this branch's diff. Recorded so the S6.4 full-suite count is read correctly (a skip there is not a weakened test). | **no** (carried into the S6.4 reading note, 5.4.3) |
| **F-23** | S5.2 | `bandit -q -r src/` emits 48 redundant-`nosec` warnings (exit 0, CI green). | No action in this change (`src/` untouched, out of scope). Candidate for a future chore / Problem Log. | **no** (out of scope, recorded) |
| **F-24** | S5.2 | `check_traceability.py` cannot flag a missing `INV-`/`EDGE-` matrix row (it enforces rows for `REQ-`/`AC-` only), so its PASS is not evidence for INV-007/EDGE-017. | The written AGENTS.md rule is the gate, and it is satisfied: S5.3 added both rows with GREEN witnesses (§5.3.2, §5.3.4). Script weakness recorded for the after-workflow-optimization; nothing in `scripts/` was changed. | **no** |
| **F-25** | S5.3 | The matrix sub-headings hard-code row counts (`INV (6 rows)` / `EDGE (16 rows)`), and no CI check polices prose counts. | Corrected in S5.3 to `7 rows` / `17 rows` with the change and date annotated; the section preamble keeps its 2026-10-09 record plus a dated amendment note (85 IDs, 58 rows). Recorded for the after-workflow-optimization. | **no** |

**No finding is open.** F-23/F-24/F-25 are pre-existing or tooling observations handed to the
after-workflow-optimization; F-21/F-22 are explanations, not defects. The pre-existing items carried from
Phase P (`F-01`/`F-02` resolved by the Phase 4 regeneration — AC-021 green since `0c73790`; `F-03` CRLF
fragility, out of scope, mitigation noted at 5.4.3; `F-09` closed by S5.3) are unchanged by this step.

### 5.4.5 Phase 5 gate verdict

**◆ S5.4: passed.** Exit criterion met: **spec coverage = 100%** (4/4 affected IDs — `REQ-014`, `AC-014`,
`INV-007`, `EDGE-017` — each with at least one GREEN witness, each with a GREEN matrix row citing a test
function that exists in this worktree) **and** every light-tier gate green (5.4.2 rows 1–13, all exit 0).
`verify_spec.py` is not a gate for ISSUE (FEATURE/CROSS-CUTTING only); the ISSUE obligation 11 —
`check_traceability.py` re-run — exits **0** (`PASS (883 matrix rows, 136 spec IDs, 804 test functions)`).

**Phase 5 is closed.** State machine: `REFACTORED` (S4.4) → **`VERIFIED`** (traceability updated in S5.3,
spec coverage 100%, light-tier gate set green). The one deferred gate — the full regression suite — is
recorded as the **S6.4 pre-merge gate** (5.4.3) and must be green in the Phase 6 review report before the
PR opens.

**Gate ◆ Phase 5: passed.** Next: **S6.1 Review vs. normative basis** (Phase 6, REVIEW).

## Phase 6 — S6.1 review vs. the normative basis (2026-10-10)

HEAD at entry: `496d218` (`docs(map-default-drop-shift): S5.4 verification report …`), `git status
--porcelain` **empty** before the step and after it (the only write is this section). Type **ISSUE,
light tier**, so the normative basis is the **triage record (§1–§6) + the affected spec IDs**, and the
ISSUE review gate is: *the reproduction tests are GREEN; the fix introduces no behavior beyond the
affected spec IDs; the full regression suite has no new failures* (the last clause is the S6.4
pre-merge gate under the light tier, §6 / 5.4.3).

**Bounded inputs used (per AGENTS.md "Bounded scope (per S6.x step)", P-27).** The FINAL state of the
files the change touched — `git diff --name-status main...HEAD` → `M STRUCTURE.md`,
`M docs/verification/map-default-drop-shift.md`, `M docs/verification/traceability.md`,
`M scripts/make_map.py`, `M tests/acceptance/test_structure_map.py`,
`M tests/property/test_structure_map.py`, `M tests/unit/test_make_map.py` — read as final content, NOT
a commit-by-commit code review. The single exception is the test-weakening check, which the step brief
names as legitimate and which can only be done against the previous test state (`git show 0ecf7bc`).

**Normative basis as it stands on `main`.** `docs/specs/structure-map.md` **v2**: REQ-014 heading `:270`,
rule text `:287-294`; AC-014 `:429`; INV-007 `:454` (§8); EDGE-017 `:476` (§9); §11 witnesses `:533`,
`:553`, `:570`; changelog v2 `:642`. The amendment reached `main` through Spec Amendment **PR A #79**,
merge `d8ba07f`, spec commit `b0c5d96` — `git merge-base --is-ancestor b0c5d96 main` and
`… d8ba07f HEAD` both succeed, and PR B touches **no** spec file
(`git diff --name-status main...HEAD -- docs/specs/` is empty), so the Spec Amendment Workflow item 6
(merge the spec PR before implementation) is satisfied and this change authored no spec text of its own.

**Commands this step ran (targeted / read-only only — no full suite, no code or test edit):**

| Check | Command | Result |
|---|---|---|
| Reproduction witnesses re-run | the four §4.5 node ids, `-q` | **`4 passed in 3.47s`** (exit 0) |
| The three structure-map modules | `uv run pytest tests/unit/test_make_map.py tests/property/test_structure_map.py tests/acceptance/test_structure_map.py -q` | **`58 passed in 72.26s`** (exit 0, 0 skipped/deselected) |
| Map freshness (check only, P-94) | `uv run python scripts/make_map.py --check` | **exit 0**, no output, `STRUCTURE.md` unmodified afterwards |
| Artifact-level INV-007 audit (read-only AST scan of the tracked tree) | `git ls-files` + `ast` over `src`/`tests`/`scripts`/`migrations` | **8 over-long defaults in 4 functions** — and the committed map carries **exactly 8 `…` occurrences in exactly 4 signature spans** (`STRUCTURE.md` `AuthService.__init__`, `build_auth_service`, `build_memory_auth_service`, `simple_template`): no placeholder missing, none spurious |
| Map self-consistency | `wc -l scripts/make_map.py` vs `STRUCTURE.md:487` | **581** vs `#### scripts/make_map.py (581 lines)`; map total **1 941** lines (NFR-002 ≤ 2 000) |
| Full regression suite | `uv run pytest tests/` | **not run** — the S6.4 pre-merge gate (light tier, §6) |

### Verdict per review question

**1. Does the final `scripts/make_map.py` satisfy the amended REQ-014 / AC-014 and the new INV-007 /
EDGE-017? — YES.**

- **REQ-014 v2** (`structure-map.md:290-293`): *"a default that exceeds the threshold is abbreviated to
  the single-character placeholder **`…` in its own slot** — the parameter is never removed from the
  rendered list and never loses its `=` separator, so the rendered list preserves the source's parameter
  names, their order, the positional-only / positional / keyword-only split, and **which parameters carry
  a default**. The rule is **uniform** across positional, positional-only and keyword-only defaults."*
  Code: `scripts/make_map.py:397-398` — `args.defaults = [_abbreviate_default(d) for d in args.defaults]`
  and `args.kw_defaults = [None if d is None else _abbreviate_default(d) for d in args.kw_defaults]`:
  a **substitution in place over both lists**, so list alignment (and therefore names, order, slot split
  and the defaults-set) is structurally preserved — the deletion that caused the shift is gone. The
  abbreviation itself is `scripts/make_map.py:381-385` (`_abbreviate_default` →
  `ast.Name(id=_DEFAULT_MARKER)`, `_DEFAULT_MARKER = "…"` at `:80`). *Witnesses:*
  `test_edge_017_over_long_default_keeps_its_slot` (`tests/unit/test_make_map.py:1028`) and
  `test_ac_014_symbol_inventory_and_unparsed_signatures` (`tests/unit/test_make_map.py:996`).
- **AC-014 v2** (`:429`): *"the signature text equals the `ast.unparse` rendering **except that a
  parameter default whose unparsed text exceeds 20 characters renders as the `…` placeholder in its own
  slot** … **And** the rendered parameter list, **with every `…` replaced by the literal `...`**, parses
  with `ast.parse` and yields the same parameter names, order, positional-only / positional /
  keyword-only split and set of defaulted parameters as the source."* The first clause holds because
  `_signature` (`scripts/make_map.py:402-415`) is unchanged and still calls `_drop_long_defaults(node.args)`
  at `:410` then unparses `node.args` at `:414` — the
  placeholder is the only deviation from a plain `ast.unparse` render. The parse/fidelity clause is
  witnessed clause-by-clause by `test_inv_007_signature_fidelity_survives_default_abbreviation`
  (`tests/property/test_structure_map.py:628`, helpers `_inv007_failures` clauses 1–5).
- **INV-007** (`:454`): witnessed by the same property test, whose expected rendering is computed from
  the **source AST** (`_expected_params`, `tests/property/test_structure_map.py:553`), not from the
  generator — so it is not a tautology of the implementation. Its last clause (*"a `…` appears **only**
  where the source default's unparsed text exceeds the REQ-014 threshold"*) also holds over the
  committed artifact: this step's independent AST scan and map scan agree exactly (8 ↔ 8, above).
  Latent caveat recorded as **F-26** (not a current violation).
- **EDGE-017** (`:476`): *"The parameter is rendered in its own slot as `name: annotation=…`; the
  placeholder never shifts a neighbouring default onto an earlier parameter, a parameter with no default
  is never given one, and a parameter with a default is never rendered without one."* All four clauses
  are pinned by `_EDGE017_MODULE` / `_EDGE017_LINES` / `_EDGE017_NEEDLES` (`tests/unit/test_make_map.py:693-740`): the three
  slots (`shift` / `posonly` / `keys`), a function whose **only** default is over-long (`only`), the
  no-default keyword-only parameter (`need: int,` present **and** `need: int=…` absent — the F-08 trap),
  the shift itself as negative needles (`b: str=1`, `c: list[int]='xy'` must be absent), and the
  unchanged 20-character boundary (`edge(exact: str='0123456789abcdefgh')`, Q-8).

**2. Is the fix the minimal fix? — YES.** The entire implementation delta is **two hunks** in
`scripts/make_map.py` (`git diff --numstat main...HEAD -- scripts/make_map.py` → **+25 / −11**): one new
helper (`_abbreviate_default`, `:381-385`), the two rewritten comprehensions in `_drop_long_defaults`, one new
module constant (`_DEFAULT_MARKER`), and two documentation corrections (the `_DEFAULT_MAX_CHARS` comment
at `:73`, the `_drop_long_defaults` docstring). Untouched, exactly as triage §5.5 required:
`_signature`, `_class_name` (REQ-016), `type_params` (REQ-017), the threshold value
`_DEFAULT_MAX_CHARS = 20` (`:74`), the CLI, every other generator output, and every `src/` module. No
new dependency, no new pattern (so no ADR, per the AGENTS.md ADR threshold), no compatibility flag or
setting (Q-18). **What the change introduced that the spec does not require:** only implementation
mechanism, no behavior — (a) the `ast.Name(id=_DEFAULT_MARKER)` injection and its explanatory comment
(the spec deliberately leaves the mechanism open; F-07/F-19), (b) one **extra** acceptance witness not
listed in spec §11 (`test_ac_014_committed_map_renders_over_long_default_in_place`) — permitted, since
the matrix/§11 may cite more witnesses than the strategy table names, never fewer (S5.3 §5.3.5).

**3. Does the observed behaviour match what the triage predicted? — YES, with one already-recorded
prediction delta.** §3.2's required line and the committed map now agree byte-for-byte
(`- def \`simple_template(name: str='test', subject: str='Test {{who}}', body_html: str=…,
body_text: str='Test {{who}}') -> EmailTemplate\``), and §3.3's required
`reset_token_ttl: timedelta=…`, `lockout_duration: timedelta=…`, `origin: str=…` are all present on the
`AuthService.__init__` map line while its short neighbours `session_ttl: timedelta=timedelta(days=7)`
and `max_failed_attempts: int=5` are unharmed — the observed-vs-required statement (defaults attached to
the wrong parameter / optional parameters rendered as required) is reversed. §3.3's scan (8 over-long
defaults, 4 functions, 3 map lines keyword-only + 1 positional) reproduces exactly at this HEAD. The
delta: §5.3/S4.1 predicted **5** changed map lines, the change produced **6** — the sixth is the map's
own per-module line count for the edited file (`#### scripts/make_map.py (567 lines)` → `(581 lines)`),
recorded and explained as **F-21**; it is generated content of the artifact, not scope creep.

**4. Was any acceptance test weakened, narrowed or deleted to reach GREEN? — NO.**
`git diff main...HEAD -- tests/` removes **no** test function (a grep for removed `def test_` lines
returns nothing); three witnesses were added. The only pre-existing witness that changed is
`test_ac_014_symbol_inventory_and_unparsed_signatures`, **re-derived in place** from the amended AC-014
— authorized by the Spec Amendment Workflow and Q-11, and the change is **strictly stronger**
(`git show 0ecf7bc -- tests/unit/test_make_map.py`):

| Aspect | Before `0ecf7bc` | After `0ecf7bc` (final state) |
|---|---|---|
| `_AC014_LINES` | 13 expected lines; `items(pool: list[int])` and `resize(... data: dict[str, int], … over: str)` — the **omission** the v1 wording allowed | same 13 lines, **2 of them re-worded** to the v2 rendering — `items(pool: list[int]=…)` and `resize(... data: dict[str, int]=…, …, over: str=…)` (the `resize` line carries the over-long keyword-only defaults `data`/`over`, F-05) — the old strings are now **wrong per spec v2**, so this is re-derivation, not relaxation |
| `_AC014_DEFAULTS` needles | 6 needles (3 positive, 3 negative) | **all 6 kept verbatim + 3 positive added** (`data: dict[str, int]=…`, `over: str=…`, `pool: list[int]=…`) = 9 — strictly more assertions |
| Docstring | "a parameter default shown only when its unparsed text is ≤ 20 characters" | the v2 wording (verbatim ≤ 20, longer abbreviated in its own slot) |
| Skips / xfails / deselect | none | none (this step: `58 passed`, 0 skipped, 0 deselected) |

The new acceptance witness follows the established artifact-level pattern of
`test_ac_021_committed_map_matches_fresh_render` / `test_nfr_002_map_line_budget` (REQ-021/AC-021 make
the committed map the object under test) and locates both witnesses **by content**, asserting exactly one
matching line each, so it cannot pass vacuously (F-11).

**5. Is the regenerated `STRUCTURE.md` consistent with the map rule (REQ-021 / REQ-023)? — YES.**
`0c73790` (the fix) contains **`scripts/make_map.py` and `STRUCTURE.md` in the same commit** — the
REQ-023 / AGENTS.md "Structure Map" same-commit regeneration rule. The S4.3 comment-only commit
`db425ae` carries **no** map diff, which is legal and verified rather than assumed: the regeneration was
byte-identical, because `STRUCTURE.md`'s blob is the same at `0c73790` and `db425ae` (`1a8b586`) and the
only property the map records for that file is its line count, which is **581 at both commits** (the
comment edit replaced one line with one line). Fresh at HEAD: `make_map.py --check` → exit 0 (this step,
tree clean afterwards); the map's own count line matches the file (581); total 1 941 lines (NFR-002);
`test_ac_021_committed_map_matches_fresh_render` is GREEN in this step's 58-passed run. The map delta is
6 lines, all generated content, no hand edit (REQ-022/EDGE-010 respected).

**6. ISSUE-specific: did the fix introduce behavior beyond the affected spec IDs? — NO, and no
reclassification is required.** Every rendered-text change traces to an ID amended or added by the merged
amendment: REQ-014 v2 / AC-014 v2 (the placeholder rule), INV-007 (fidelity), EDGE-017 (the three slots
plus the two boundary shapes). The two non-signature map lines are generated metadata the required
regeneration absorbs (F-01/F-16/F-21), not new behavior. No new CLI surface, setting, flag, dependency,
`src/` change or backend behavior; the change stays inside one feature (the structure-map generator and
its artifact), so the light-tier qualification (§6) still holds and the Escalation Rules are not
triggered.

### Findings

| ID | Finding | Severity | Disposition |
|---|---|---|---|
| **F-26** | INV-007's last clause ("a `…` appears **only** where the source default's unparsed text exceeds the REQ-014 threshold") is not enforceable against a source default whose **own text contains a literal `…`** and fits the threshold: `def f(x: str = "…")` renders `x: str='…'`, which is indistinguishable from the placeholder, and the INV-007 strategy never draws such a value (`_SHORT_DEFAULTS = ("1", "'xy'", "None", "42")`, `tests/property/test_structure_map.py:483`), so no witness would flag it. Measured at this HEAD: **0** tracked `.py` defaults contain `…` at all, so the committed artifact satisfies the clause (8 placeholders ↔ 8 over-long defaults) and there is **no current violation**. | **Low** (latent witness/spec gap, no present defect) | **Deferred — out of scope.** Closing it needs either a spec-wording refinement (a spec amendment, not this ISSUE) or an extra value in the property strategy; neither is required by the affected IDs. Recorded for the after-workflow-optimization. |
| **F-27** | `_drop_long_defaults` (`scripts/make_map.py:387`) is now a **misnomer** — it abbreviates, it no longer drops. | **Info** (naming) | **Accepted as-is / deferred.** S4.3 considered the rename and rejected it (the name is the reference key across this change's records and the sibling TODO; the docstring's first line states the v2 rule). Cosmetic, out of scope for an ISSUE fix. |
| **F-28** | Three module constants hold the same `"…"` character (`_SUMMARY_MARKER:71`, `_DEFAULT_MARKER:80`, `_FIELD_MARKER:85`). | **Info** (duplication) | **Accepted as-is.** The file's convention is one marker constant per rule, each carrying its own spec ID (REQ-018 / REQ-014 v2 / REQ-017); collapsing them would rename two out-of-scope constants for cosmetics (S4.3). |
| **F-29** | `test_ac_014_committed_map_renders_over_long_default_in_place` pins the **whole** `simple_template` map line, including its docstring summary — an unrelated docstring edit in `tests/mail_test_helpers.py` would break an AC-014 acceptance test. | **Low** (witness brittleness, intentional) | **Accepted.** The committed artifact is the object under test (REQ-021/AC-021 precedent), the witness locates by content and requires exactly one match, and the failure message prints both lines, so a future break is diagnosable, not silent. |
| **F-30** | No witness **parses** the committed map's signature lines: INV-007's parse clause is witnessed over generated synthetic modules (property) and the artifact is witnessed by needles (acceptance). | **Info** (coverage shape) | **No action — covered by measurement.** This step's independent audit (8 over-long defaults in the tree ↔ 8 placeholders in 4 map signature spans) confirms the clause over the artifact. Recorded so the audit is not mistaken for a test. |
| **F-31** | The map delta is 6 lines, of which 2 are generated metadata (`docs/` file count, `make_map.py`'s own line count) rather than the fix. | **Info** | **Closed at S6.1 — verified not scope creep** (F-01/F-16/F-21 reconciled: 4 signature lines + 2 metadata lines, total 1 941 unchanged, `--check` exit 0). |
| **F-32** | `CHANGELOG.md` has **no** `## [Unreleased]` entry and `pyproject.toml` is still `1.1.0` at this HEAD. | **Open item, not a defect** | **Deferred to S6.4** — AGENTS.md Phase 6 items 10–11 (entry under `Fixed`, `bump-my-version bump patch` `1.1.0 → 1.1.1`, entries moved to `## [1.1.1] - <date>` in the bump commit) and F-20. The review skill flags a missing changelog **when the PR opens**, not in S6.1. **Blocking for S6.4, not for this gate.** |

### Does any finding block a clean review?

**No.** F-26…F-31 are low/informational and either accepted with reasons or deferred as out of scope for
this ISSUE's IDs; none contradicts the normative basis, none is an unimplemented or unauthorized
behavior, and no acceptance test was weakened, narrowed or deleted. **F-32 is not a review finding
against the normative basis** — it is the Phase 6 obligation owed at S6.4, together with the light-tier
**full regression suite** (`uv run pytest tests/ -v`, 5.4.3), which must be green before the PR opens and
must be recorded in the review report (S6.3/S6.4).

**Review Order note.** This step covers skill Review Order steps 1 (**normative basis**) and 3
(**acceptance tests, weakening**). Steps 2 (traceability), 4–5 (implementation quality, feature
boundaries and architecture rules) and 6–7 (quality, observability) are **S6.2**/**S6.3**; observability
is not applicable to this change (the spec states the `scripts/` tooling is outside the backend tracing
policy, `structure-map.md:505-507`).

**Gate ◆ S6.1: passed** — the change implements exactly what its normative basis requires, no more and
no less; 7 findings recorded, **0 blocking**. Next: **S6.2 Traceability + boundaries**.

## Phase 6 — S6.2 traceability + boundaries (2026-10-10)

HEAD at entry: `87f2ad4` (`docs(map-default-drop-shift): S6.1 review vs normative basis`), `git status
--porcelain` **empty** before the step and after it (the only write is this section). This step writes
**only this file**: no `src/`, no `tests/`, no `docs/verification/traceability.md` (S5.3 owns it), no spec,
no `AGENTS.md`/`CHANGELOG.md`, no `STRUCTURE.md`, no `docs/todo/` or `docs/questions/`, no code edit, no PR,
no version bump. **The full test suite was not run** — under the light tier (§6) it is the S6.4 pre-merge
gate (5.4.3); the only test execution here is the targeted four-witness re-run in the table below.

**Bounded inputs used (per AGENTS.md "Bounded scope (per S6.x step)", P-27).** The structure-map section
of the matrix (`docs/verification/traceability.md:997-1107`), this file's S5.3 (§5.3.2–§5.3.5), S5.4
(§5.4.1–§5.4.4) and S6.1 (findings F-26…F-32) sections, and the **FINAL** state of the seven files
`git diff --name-status main...HEAD` lists — read as final content, not a commit-by-commit diff. The one
historical diff examined is `git show d1fa73f -- docs/verification/traceability.md` (and the equivalent
whole-branch `git diff main...HEAD -- docs/verification/traceability.md`), which check 3 requires.

### Commands run (targeted / read-only only — no full suite, no edit)

| # | Command | Result | Exit |
|---|---|---|---|
| 1 | `uv run python scripts/check_traceability.py` (the CI `traceability` job, `.github/workflows/spec-validation.yml`) | `Traceability: PASS (883 matrix rows, 136 spec IDs, 804 test functions)` | **0** |
| 2 | The four §4.5 witnesses, `-q` (targeted, to confirm the rows' `GREEN` still reads true) | `4 passed in 2.63s` | **0** |
| 3 | `uv run python scripts/make_map.py --check` (check only, P-94) | no output; `git status --porcelain` empty afterwards | **0** |
| 4 | `git diff --stat main...HEAD -- src/` / `--numstat` | **empty** (no `src/` file touched) | 0 |
| 5 | `git diff --name-status main...HEAD` | 7 files, all `M` (no `A`/`R`/`D` — nothing added or moved) | 0 |
| 6 | `git show --stat 0c73790` / `git rev-parse 0c73790:STRUCTURE.md db425ae:STRUCTURE.md HEAD:STRUCTURE.md` | see check 5 below | 0 |
| 7 | Matrix row parse with the checker's own `matrix_rows()` over `git show main:…` vs `git show HEAD:…` | `main` **881 rows** → `HEAD` **883 rows** (+2) | 0 |
| 8 | `git diff main...HEAD -- tests/ \| grep -E "^[+-]\s*def test_"` | **3 added, 0 removed** | — |
| 9 | `git diff main...HEAD \| grep -E "^[+-]\s*(from\|import)\s"` | 4 lines, all in `tests/property/test_structure_map.py` (see check 4) | — |

### Check 1 — Traceability completeness (the four IDs this change owns): **INTACT**

Every normative ID this change owns has a matrix row in the structure-map section, each citing a test
function that exists in this worktree at the exact line the row cites.

| ID | Matrix row (`docs/verification/traceability.md`) | Cited witness | Witness exists (grep `def <name>`) | Status token |
|---|---|---|---|---|
| `REQ-014` + `AC-014` | `:1047` (updated in place) | `test_ac_014_symbol_inventory_and_unparsed_signatures`; `test_ac_014_committed_map_renders_over_long_default_in_place` | `tests/unit/test_make_map.py:996`; `tests/acceptance/test_structure_map.py:1506` | `GREEN` (declared) |
| `INV-007` | `:1072` (added) | `test_inv_007_signature_fidelity_survives_default_abbreviation` | `tests/property/test_structure_map.py:628` | `GREEN` (declared) |
| `EDGE-017` | `:1094` (added) | `test_edge_017_over_long_default_keeps_its_slot` | `tests/unit/test_make_map.py:1028` | `GREEN` (declared) |

Checker (command 1): **`Traceability: PASS (883 matrix rows, 136 spec IDs, 804 test functions)`, exit 0** —
identical to the S5.3 post-edit and S5.4 re-run lines (§5.3.3, §5.4.2 #9), i.e. nothing this step changed
and nothing has drifted since.

**F-24 re-confirmed by reading the checker, and narrowed.** `scripts/check_traceability.py:102-105`
implements rule (1) — "every ID defined by a spec has a row" — behind
`REQ_OR_AC_RE.fullmatch(id_)` (`:15` = `\b(?:REQ|AC)-\d+\b`), so a **missing `INV-`/`EDGE-` row is invisible
to CI**: the PASS is *not* evidence that the two rows exist, and they were therefore read directly (the
table above, `:1072` and `:1094`). Conversely rule (3) at `:112-115` polices **every** backticked
`test_*` in **every** row of a Status table, so the *existence* of the two INV/EDGE witnesses **is**
checker-verified — the gap is one-directional (missing row, not missing test). Rule (2) (`:107-110`)
confirms the two new IDs are defined by a spec: `INV-007` and `EDGE-017` are present in
`docs/specs/structure-map.md` (v2, amended IDs `REQ-014`/`AC-014` likewise), which is why the rows pass.

### Check 2 — Every test this change added or changed traces back to a normative ID: **INTACT, no orphan**

`git diff main...HEAD -- tests/` adds **3** `def test_…` and removes **0** (command 8). Each names its ID
in the first line of its docstring, and each is cited by exactly one matrix row (1 hit per name in
`docs/verification/traceability.md`):

| Test (final state) | Category dir | ID cited in the docstring | Matrix row |
|---|---|---|---|
| `test_ac_014_committed_map_renders_over_long_default_in_place` (`tests/acceptance/test_structure_map.py:1506`) | acceptance | "**AC-014/EDGE-017 (REQ-014)**: the committed STRUCTURE.md abbreviates an over-long parameter default to the `…` placeholder in its own slot…" | `:1047` |
| `test_inv_007_signature_fidelity_survives_default_abbreviation` (`tests/property/test_structure_map.py:628`) | property (Hypothesis `@given(module=_signature_module())`, `:638`) | "**INV-007 (REQ-014)**: … the same positional-only / positional / keyword-only split and exactly the set of parameters that carry a default…" | `:1072` |
| `test_edge_017_over_long_default_keeps_its_slot` (`tests/unit/test_make_map.py:1028`) | unit | "**EDGE-017 (REQ-014)**: a parameter default whose unparsed text exceeds 20 characters is abbreviated to the `…` placeholder in its own slot…" | `:1094` |
| `test_ac_014_symbol_inventory_and_unparsed_signatures` (`tests/unit/test_make_map.py:996`) — **changed**, not added | unit | "**AC-014 (REQ-014)**: … a parameter default of ≤ 20 characters shown verbatim while a longer one is abbreviated to the `…` placeholder in its own slot (**EDGE-017**)…" | `:1047` |

Category placement matches the Test Category Hierarchy (artifact-level witness → `tests/acceptance/`,
invariant over an input space → `tests/property/`, local generator behaviour → `tests/unit/`), which is
also the category the spec's §11 Test Strategy assigns to each ID (`structure-map.md:533`, `:553`, `:570`,
cross-read at §5.3.5). Everything else the branch adds under `tests/` is a **helper or fixture**, not a
test — `_ELLIPSIS`, `_PLACEHOLDER`, `_DEFAULT_MAX_CHARS`, `_MAX_PARAMS`, `_MAX_FUNCTIONS`, `_DEF_LINE`,
`_signature_module`, `_expected_params`, `_inv007_failures`, `_EDGE017_MODULE`, `_EDGE017_LINES`,
`_SIMPLE_TEMPLATE_MARKER`, `_SIMPLE_TEMPLATE_LINE`, `_AUTH_SERVICE_INIT_MARKER` — so no orphan test exists
in either direction. The fixture source strings declare no `test_*` functions (`shift`, `only`, `posonly`,
`keys`, `edge`), so they cannot inflate the checker's test-name set either.

### Check 3 — No row refreshed that this change did not touch (Q-129, convention B): **INTACT — exactly 2 added, 1 updated**

`git show d1fa73f -- docs/verification/traceability.md` and the whole-branch equivalent
`git diff main...HEAD -- docs/verification/traceability.md` (the branch touched the matrix in that one
commit only) agree, and the whole-branch view is the stronger check because it covers every commit of the
change:

| Measure | Value |
|---|---|
| Changed table lines (whole branch) | **3 added, 1 removed** → `INV-007` row added, `EDGE-017` row added, `REQ-014 / AC-014` row removed+re-added = **updated in place** |
| Net matrix rows | `main` **881** → `HEAD` **883** (+2), parsed with the checker's own `matrix_rows()` over `git show <ref>:docs/verification/traceability.md` — matches the checker's `883 matrix rows` and S5.3's `881 → 883` (§5.3.3) |
| Rows in the structure-map section | **58** (lines 1034–1106): 27 REQ/AC + 7 INV + 17 EDGE + 7 NFR, i.e. **85 IDs** — exactly the totals the S5.3 amendment note states (`:1018-1020`) |
| Diff hunk positions | `@@ -1014`, `@@ -1031`, `@@ -1046`, `@@ -1056`, `@@ -1077` — **all inside the structure-map section** (it starts at `:997`); no other change's section was touched |
| Non-row edits | 13 preamble lines (the dated amendment note) + 2 sub-heading lines (`### INV (6 rows…)` → `(7 rows… 2026-10-10)`, `### EDGE (16 rows)` → `(17 rows… 2026-10-10)`, F-25) — prose only, no Status cell |

So the count is exactly what S5.3 reported (**2 added, 1 updated in place**), and the other 26 REQ/AC rows,
INV-001…INV-006, EDGE-001…EDGE-016, all 7 NFR rows and every row of every other section are byte-identical
to `main` — no historical gate record was refreshed by a change that did not re-run it.

### Check 4 — Feature boundaries and architecture rules: **INTACT**

| Boundary | Evidence |
|---|---|
| `src/backend/**` untouched | `git diff --stat main...HEAD -- src/` and `--numstat` are both **empty** (command 4) — no backend behaviour, no model, no service, no migration, no `pyproject.toml`/lock in the diff |
| Nothing moved to the wrong place | `git diff --name-status main...HEAD` → 7 × `M`, **no `A`/`R`/`D`**: the generator stays in `scripts/make_map.py`, the generated artifact stays at the repository root (`STRUCTURE.md`), the tests stay in `tests/unit/`, `tests/property/`, `tests/acceptance/`, the records stay in `docs/verification/` |
| No cross-feature internal import introduced | The branch's **only** import changes (command 9) are in `tests/property/test_structure_map.py`: `+import ast`, `+import copy`, `Mapping` → `Mapping, Sequence`, and `hypothesis` gains `assume` — stdlib plus the already-declared property-testing dependency. `scripts/make_map.py:16-25` is **stdlib-only and unchanged by the branch** (REQ-001), so the generator still imports no feature. The apparent `from backend.logging import logged, logged_class` at `tests/unit/test_make_map.py:745` is a line **inside the `_AC015_MODULE` fixture source string** (the pre-existing AC-015 witness), not an import of the test module, and it is not in this branch's diff |
| Flat-feature-package note | The repo has flat feature packages under `src/backend/` and **no** `model/` or `services/` directory anywhere; this change created no directory and none was expected, so the "code lives in the correct feature directory" check resolves to: the change belongs to the structure-map feature, whose whole footprint is `scripts/make_map.py` + `STRUCTURE.md` + its three test modules |
| Dependency rule | No dependency added (`deptry` clean at S5.2 5.2.1 #7; `pyproject.toml` not in the diff), so no ADR is owed (AGENTS.md ADR threshold: new dependency / new pattern / cross-feature interface — none present) |
| Observability | Not applicable: the spec places the `scripts/` tooling outside the backend tracing policy (`structure-map.md:505-507`, recorded in S6.1) |

### Check 5 — Generated-file rule (REQ-023 / AGENTS.md "Structure Map"): **INTACT**

- `git show --stat 0c73790` → `STRUCTURE.md | 12 ±` **and** `scripts/make_map.py | 34 ±` **in the same
  commit** — the map was regenerated in the same commit as the `.py` change (REQ-023, triage §5.3).
- The later comment-only refactor `db425ae` carries **no** map diff, and that is verified rather than
  assumed: `git rev-parse 0c73790:STRUCTURE.md db425ae:STRUCTURE.md HEAD:STRUCTURE.md` → all three are
  blob **`1a8b586`**, and `git show <ref>:scripts/make_map.py | wc -l` is **581 at both** commits — the only
  property the map records for that file (its line count) did not change, so a regeneration would have been
  byte-identical.
- Fresh at HEAD: `uv run python scripts/make_map.py --check` → **exit 0**, no output, working tree still
  clean (command 3) — the committed map is a byte-exact fresh render, so it was **not hand-edited**
  (REQ-022 / EDGE-010).
- The map delta is 6 lines, all generated content: 4 signature lines (`AuthService.__init__`,
  `build_auth_service`, `build_memory_auth_service`, `simple_template`) plus 2 metadata lines
  (`docs/ — 225 → 231 files`, `#### scripts/make_map.py (567 lines) → (581 lines)`) — F-21/F-31, reconciled
  at S6.1, not scope creep.

### Findings

| ID | Finding | Severity | Disposition |
|---|---|---|---|
| **F-33** | The structure-map `NFR-006` row (`docs/verification/traceability.md:1105`) cites `wc -l scripts/make_map.py` = **567 lines**; the file is **581** at HEAD, so the number inside that cell no longer describes the current tree. | **Info** (stale number inside a historical cell — not a stale row) | **No action — and refreshing it would be the violation.** The cell is the dated record of the structure-map S5.1/S5.2 gate (2026-10-09, commit `3ec204c`), `NFR-006` is a spec §11 **record row with no witness by design**, and this change did not touch `NFR-006` — under decision Q-129 (convention B) a later change updates only the rows it actually touched. Recorded so S6.3 does not read it as a referential-integrity defect (the checker's rules 1–4 do not, and cannot, police numbers inside a Status cell). |
| **F-34** | The matrix's own "Drift Checks" list (`docs/verification/traceability.md:1118-1126`) promises CI detects an "**Orphaned test:** a test function has no spec reference", but `check_traceability.py` implements no orphan rule at all (rules 1–4, `:102-121`), and rule (1) is restricted to `REQ`/`AC` (`:15`, `:104`), so a missing `INV-`/`EDGE-` row is also invisible — the same one-directional gap F-24 recorded. | **Info** (pre-existing tooling gap, outside this ISSUE's scope) | **No action in this change** — changing `scripts/` is out of scope (triage §8, the parameter-default rule only). Both directions were therefore verified by hand for this change: all 4 owned IDs have rows (check 1) and all 3 added tests are cited exactly once in the matrix (check 2), so there is **no orphan and no missing row here**. Handed to the after-workflow-optimization together with F-24 and F-25. |

### Does any finding block a clean review at S6.3?

**No.** F-33 and F-34 are informational: neither contradicts the normative basis, neither is a missing
traceability link or an orphaned test, and neither is actionable inside this ISSUE's scope. Traceability is
complete for the four IDs this change owns (checker exit 0, plus the two rows read directly because of the
F-24/F-34 gap), no test is orphaned, no untouched row was refreshed, boundaries and architecture rules hold
(`src/` untouched, no new import, nothing moved), and the generated-file rule is satisfied.

The only items still open for this change are the ones S6.1 already named and S6.4 owes: **F-32** (the
`CHANGELOG.md` `## [Unreleased]` → `Fixed` entry and the `patch` bump `1.1.0 → 1.1.1` with the entries moved
to `## [1.1.1] - <date>`) and the light-tier **full regression suite** (`uv run pytest tests/ -v`, 5.4.3),
which must be green before the PR opens and recorded in the review report.

**Review Order note.** This step covers skill Review Order steps 2 (**traceability**), 5 (**architecture /
feature boundaries**) and the boundary half of 4; step 1 (normative basis) and step 3 (test weakening) were
closed at S6.1, and steps 6–7 (quality, observability) are **S6.3** — quality gates were already recorded
green at S5.2 (5.2.1 #1–#8, #11–#13).

**Gate ◆ S6.2: passed** — traceability intact (4/4 owned IDs with a row citing an existing witness; checker
`PASS (883 matrix rows, 136 spec IDs, 804 test functions)`, exit 0), zero orphaned tests, exactly 2 rows
added + 1 updated in place and no other row refreshed, boundaries and architecture rules respected
(`src/` diff empty), generated-file rule satisfied (map and `.py` in one commit, `--check` exit 0).
2 findings recorded, **0 blocking**. Next: **S6.3 Review report (clean)**.

## Phase 6 — S6.3 review report (2026-10-10)

HEAD at entry: `1b0da55` (`docs(map-default-drop-shift): S6.2 traceability + boundaries`), `git status
--porcelain` **empty** before the step and after it (the only write is this section). This step writes
**only this file**: no `src/`, no `tests/`, no `scripts/`, no `docs/verification/traceability.md`, no spec,
no `AGENTS.md`, no `CHANGELOG.md`, no `pyproject.toml`, no `STRUCTURE.md`, no `docs/todo/` or
`docs/questions/`, no PR, no version bump. **No test suite was run** — under the light tier (§6) the full
regression suite is the **S6.4 pre-merge gate** (5.4.3) and re-running it here would be the unbounded
re-review P-27 warns about; lint and types were **not** re-run either (S5.2 5.2.1 #1–#8, #11–#13 is the
evidence, re-listed at S5.4 5.4.2 rows 5–8 and 11–13). Commands run here are read-only: `git status
--porcelain`, `git log`, `git diff --name-status main...HEAD`, the S6.1/S6.2 sections of this file, and the
current state of `CHANGELOG.md` (`## [Unreleased]` has **no** entry for this change) and `pyproject.toml`
(`version = "1.1.0"`, `:4`) — the F-32 state, read, not changed.

**Bounded inputs (per AGENTS.md "Bounded scope (per S6.x step)").** This report consolidates the two
review steps that already did the reviewing — **S6.1** (commit `87f2ad4`, six verdicts, findings F-26…F-32)
and **S6.2** (commit `1b0da55`, five checks, findings F-33…F-34) — plus the Phase 5 record (S5.1–S5.4:
spec coverage 100%, 13 light-tier gates green, F-21…F-25 closed). The code was **not** re-reviewed from
scratch; the FINAL state of the seven files `git diff --name-status main...HEAD` lists was reviewed at
S6.1/S6.2 and nothing has changed since (`git status --porcelain` empty at both entries).

### 6.3.1 The ISSUE review-gate criteria, one by one

AGENTS.md "Review Gate (Phase 6)", ISSUE row, plus the "All types" clause and the light-tier deferral
(§6, AGENTS.md "Light ISSUE tier").

| # | Criterion (verbatim) | Verdict at S6.3 | Evidence (section / commit) |
|---|---|---|---|
| 1 | *"the reproduction tests are GREEN"* | **SATISFIED** | The four §4.5 node ids (`test_edge_017_over_long_default_keeps_its_slot`, `test_ac_014_symbol_inventory_and_unparsed_signatures`, `test_inv_007_signature_fidelity_survives_default_abbreviation`, `test_ac_014_committed_map_renders_over_long_default_in_place`): `4 passed` exit 0 at S5.1 §5.1.1 (`3.31s`), S5.4 5.4.2 #1 (`3.10s`), S6.1 (`3.47s`) and S6.2 command 2 (`2.63s`) — four independent re-runs, 0 failed / 0 skipped / 0 xfail / 0 deselected. RED was observed first at S3.2 (`5b51614`) and the Phase 4 fix is `0c73790`. |
| 2 | *"the fix introduces no behavior beyond the affected spec IDs"* | **SATISFIED** | S6.1 verdict 2 (the whole implementation delta is **+25 / −11** in `scripts/make_map.py`, one helper + two comprehensions + one constant + two doc corrections; `_signature`, `_class_name`, `type_params`, the threshold `20`, the CLI and every `src/` module untouched) and verdict 6 (every rendered-text change traces to `REQ-014` v2 / `AC-014` v2 / `INV-007` / `EDGE-017`; the two non-signature map lines are generated metadata, F-21/F-31). No new dependency, setting, flag or public interface; `git diff --stat main...HEAD -- src/` empty (S6.2 Check 4). No reclassification owed — the Escalation Rules were not triggered. |
| 3 | *"the full regression suite has no new failures"* | **NOT YET SATISFIED — the single open gate, by design** | Under the light-tier qualification (§6) Phase 5 ran **targeted + smoke** instead, and AGENTS.md Phase 5 ISSUE item 9 + the review skill ("MUST → ISSUE") make the **full regression suite the Phase 6 pre-merge gate**: `uv run pytest tests/ -v` MUST pass **before the PR opens (S6.4)** and its result MUST be recorded in this review report. It was deliberately not run at S5.x (5.4.3) nor at S6.1/S6.2. Supporting evidence that it is expected to pass: the acceptance smoke sweep `396 passed, 1 skipped` (S5.1 §5.1.4), the three structure-map modules `58 passed` (S5.1 §5.1.2, S6.1), and the only known red on `main` — `test_ac_021_committed_map_matches_fresh_render`, F-01/F-02/F-16 — has been green since the Phase 4 regeneration in `0c73790`. |
| 4 | *All types: "no acceptance test was weakened or deleted to achieve GREEN"* | **SATISFIED** | S6.1 verdict 4: `git diff main...HEAD -- tests/` adds **3** `def test_…` and removes **0** (re-confirmed as command 8 at S6.2); the single changed witness `test_ac_014_symbol_inventory_and_unparsed_signatures` was **re-derived in place** from the amended AC-014 — authorized by the Spec Amendment Workflow (PR A #79, merge `d8ba07f`) and Q-11 — and is **strictly stronger** (all 6 needles kept, 3 positive needles added; the two re-worded expected lines are the ones the old wording made wrong, F-05). No skip, xfail or deselection anywhere. |
| 5 | *All types: "feature boundaries and architecture rules are respected"* | **SATISFIED** | S6.2 Check 4: `src/` diff empty; 7 × `M` and **no** `A`/`R`/`D` (nothing added, moved or renamed); the branch's only import changes are stdlib + the already-declared `hypothesis` extras in `tests/property/test_structure_map.py`; `scripts/make_map.py:16-25` stays stdlib-only; no dependency added, so no ADR owed. |
| 6 | *Phase 6 check 2: every REQ/AC has at least one GREEN test; every test traces to a normative ID* | **SATISFIED** | S6.2 Checks 1–3: rows for `REQ-014`/`AC-014` (`traceability.md:1047`, updated in place), `INV-007` (`:1072`) and `EDGE-017` (`:1094`), each citing a witness that exists at the cited line; `scripts/check_traceability.py` → `PASS (883 matrix rows, 136 spec IDs, 804 test functions)` exit 0; zero orphaned tests (all 3 added tests cited exactly once); exactly **2 rows added + 1 updated**, no untouched row refreshed (Q-129 convention B). Spec coverage **4/4 = 100%** (S5.4 §5.4.1). |
| 7 | *Phase 6 item 10: a `CHANGELOG.md` entry under `## [Unreleased]`* | **OWED at S6.4 — not a defect at this gate** | F-32 (S6.1): `CHANGELOG.md` has no entry for this change and `pyproject.toml` is still `1.1.0`. The review skill flags a missing changelog **when the PR opens**, not in S6.1/S6.3; AGENTS.md Phase 6 items 10–11 assign it to S6.4. Listed as obligation (a)/(b) in 6.3.5. |

**The single open gate.** Exactly one review-gate criterion is not yet green: **criterion 3, the full
regression suite** (`uv run pytest tests/ -v`), which the light tier moves to **S6.4 as the pre-merge
gate**. It is open *by design*, not because a failure is known. Everything the review examines — the
normative basis, the tests, traceability, boundaries, the generated artifact, quality gates — is closed.
Until that run is green and recorded here, this change **must not** have its PR opened, and the CLEAN
verdict below is explicitly **conditional** on it.

### 6.3.2 Consolidated Phase 6 findings (F-26 … F-34)

All nine Phase 6 findings, from S6.1 (`87f2ad4`) and S6.2 (`1b0da55`), with the resolution actually taken
or the explicit deferral:

| ID | Finding | Severity | Resolution |
|---|---|---|---|
| **F-26** | INV-007's "a `…` appears **only** where the source default exceeds the threshold" clause is not enforceable against a source default whose own text contains a literal `…` within the threshold, and the property strategy never draws such a value (`_SHORT_DEFAULTS`, `tests/property/test_structure_map.py:483`). Measured: **0** tracked `.py` defaults contain `…`, so the artifact satisfies the clause (8 placeholders ↔ 8 over-long defaults). | Low (latent witness/spec gap, **no present violation**) | **Deferred — out of scope.** Closing it needs a spec-wording amendment (a separate Spec Amendment, not this ISSUE) or an extra value in the property strategy; neither is required by the affected IDs. Handed to the after-workflow-optimization. |
| **F-27** | `_drop_long_defaults` (`scripts/make_map.py:387`) is now a misnomer — it abbreviates, no longer drops. | Info (naming) | **Accepted as-is / deferred** (decided at S4.3): the name is the reference key across this change's records and the sibling TODO, and the docstring's first line states the v2 rule. Cosmetic, outside an ISSUE fix. |
| **F-28** | Three module constants hold the same `"…"` (`_SUMMARY_MARKER:71`, `_DEFAULT_MARKER:80`, `_FIELD_MARKER:85`). | Info (duplication) | **Accepted as-is.** The file's convention is one marker constant per rule, each carrying its own spec ID (REQ-018 / REQ-014 v2 / REQ-017); collapsing them would rename two out-of-scope constants for cosmetics. |
| **F-29** | The new acceptance witness pins the whole `simple_template` map line, so an unrelated docstring edit in `tests/mail_test_helpers.py` would break an AC-014 test. | Low (witness brittleness, intentional) | **Accepted.** The committed artifact is the object under test (REQ-021/AC-021 precedent), the witness locates by content and requires exactly one match (cannot pass vacuously, F-11), and the failure message prints both lines — a future break is diagnosable, not silent. |
| **F-30** | No witness **parses** the committed map's signature lines (INV-007's parse clause is witnessed over generated synthetic modules; the artifact by needles). | Info (coverage shape) | **No action — covered by measurement.** S6.1's independent read-only AST audit agrees with the artifact exactly (8 over-long defaults in the tree ↔ 8 `…` in 4 map signature spans). Recorded so the audit is not mistaken for a test. |
| **F-31** | The map delta is 6 lines, 2 of them generated metadata (`docs/` file count, `make_map.py`'s own line count) rather than the fix. | Info | **Closed at S6.1** — verified not scope creep: 4 signature lines + 2 metadata lines, reconciled against F-01/F-16/F-21; total 1 941 lines unchanged (NFR-002), `make_map.py --check` exit 0. |
| **F-32** | `CHANGELOG.md` has no `## [Unreleased]` entry and `pyproject.toml` is still `1.1.0`. | **Open item, not a defect** | **Deferred to S6.4** — AGENTS.md Phase 6 items 10–11: the entry under `Fixed`, then `bump-my-version bump patch` (`1.1.0 → 1.1.1`) with the entries moved to `## [1.1.1] - <date>` in the bump commit. **Blocking for S6.4, not for this gate** (the skill flags a missing changelog when the PR opens). |
| **F-33** | The structure-map `NFR-006` row (`traceability.md:1105`) cites `wc -l scripts/make_map.py` = **567**; the file is **581** at HEAD. | Info (stale number inside a historical cell — **not** a stale row) | **No action — refreshing it would be the violation.** The cell is the dated record of the structure-map S5.1/S5.2 gate (2026-10-09, `3ec204c`); `NFR-006` is a spec §11 record row with no witness by design, and this change did not touch it (Q-129 convention B). The checker's rules cannot police numbers inside a Status cell, so the row was read directly. |
| **F-34** | The matrix's "Drift Checks" list promises CI detects an *orphaned test*, but `check_traceability.py` implements no orphan rule (rules 1–4, `:102-121`) and rule (1) is restricted to `REQ`/`AC` (`:15`), so a missing `INV-`/`EDGE-` row is invisible too — the one-directional gap F-24 recorded. | Info (pre-existing tooling gap, outside this ISSUE's scope) | **No action in this change** — `scripts/` is out of scope (triage §8: the parameter-default rule only). Both directions were verified by hand for this change instead (S6.2 Checks 1–2: no missing row, no orphan). Handed to the after-workflow-optimization with F-24 and F-25. |

**No finding is open as a defect in this change.** F-26…F-31 and F-33/F-34 are low or informational and are
either accepted with a stated reason or explicitly deferred as outside this ISSUE's IDs; none contradicts
the normative basis, none is unimplemented or unauthorized behavior, none is a missing traceability link or
an orphaned test, and no acceptance test was weakened, narrowed or deleted. **F-32 is the only item still
outstanding**, and it is a Phase 6 obligation owed at S6.4, not a finding against the change. The Phase 5
ledger (F-21…F-25, §5.4.4) and the Phase P carry-overs (F-01/F-02 resolved by the Phase 4 regeneration;
F-03 out of scope with a mitigation; F-09 closed at S5.3) are likewise all closed or recorded.

### 6.3.3 Phase 6 checks that do not apply to this change, and where the applicable ones closed

- **Check 9 — "document reusable shared capabilities in `AGENTS.md`": NOT APPLICABLE.** AGENTS.md scopes it
to **FEATURE/CROSS-CUTTING only**, and this change is an **ISSUE**. It would not qualify on its own merits
either: the delta is a rendering-rule fix inside one `scripts/` tool, not a shared capability a future
change would call (the structure-map feature's usage note already exists in AGENTS.md "Structure Map" and
the `code-structure-map` skill). **No `AGENTS.md` edit was made and none is owed.**
- **Checks 3 and 4 — feature boundaries and architecture rules: already done at S6.2 (Check 4)**, not
  re-run here: `src/` diff empty, no file added/moved/renamed, no cross-feature internal import introduced
  (the only import changes are stdlib + `hypothesis` extras in one test module), no dependency added and
  therefore no ADR owed. The repo has flat feature packages under `src/backend/` and no `model/` or
  `services/` directory, so the "correct feature directory" check resolves to the structure-map footprint
  (`scripts/make_map.py` + `STRUCTURE.md` + its three test modules), which the change left in place.
- **Check 10 (CHANGELOG), 11 (version bump), 12 (open the PR)** are S6.4's, listed in 6.3.5.
- Where the remaining Phase 6 checks closed: **check 1** (review vs. the normative basis) → S6.1 verdicts
  1–6; **check 2** (traceability) → S6.2 Checks 1–3; **check 5** (acceptance tests not weakened/deleted)
  → S6.1 verdict 4; **check 6** (no behavior beyond the spec IDs / beyond the type's contract) → S6.1
  verdict 6; **check 7** (the report itself) → this section; **check 8** (clean report ⇒ the change is
  complete) → the verdict in 6.3.6, conditional on the S6.4 gate.
- **Review Order steps 6 and 7 (quality, observability), which S6.1/S6.2 both deferred to this step:**
  **quality — closed on existing evidence**, `uv run ruff check .` (`All checks passed!`),
  `ruff format --check .` (`343 files already formatted`), `mypy src/` (`84 source files`) and
  `mypy scripts/` (`4 source files`), `complexipy src tests --max-complexity-allowed 15` (tightest new
  path 14/15), `deptry .` and `bandit -q -r src/` all exit 0 with zero findings introduced by this branch
  (S5.2 5.2.1 #1–#8, #11–#13; re-listed S5.4 5.4.2 rows 5–8, 11–13) — implementation style was reviewed
  only **after** the normative basis, per the skill's Review Order and MUST-NOT. **Observability — not
  applicable**: the spec places the `scripts/` tooling outside the backend tracing policy
  (`docs/specs/structure-map.md:505-507`), the generator's observable contract (CLI, pinned exit codes,
  stdout) is unchanged (S6.1 verdict 2), and no `src/` feature gained or lost a log statement.

### 6.3.4 What S6.4 must do before the PR opens (in this order)

1. **(a) `CHANGELOG.md` entry** under `## [Unreleased]` → **`Fixed`** (AGENTS.md Phase 6 item 10; F-32/F-20
   — it does **not** exist yet). One line per user-observable change, traced to what this change actually
   did and nothing more: the structure-map generator no longer **drops** a parameter default whose
   unparsed text exceeds 20 characters but abbreviates it to the `…` placeholder **in its own slot**, so
   `STRUCTURE.md` signature lines no longer shift an over-long default onto the following parameter or
   render a defaulted parameter as required — the corrected renderings are `AuthService.__init__`,
   `build_auth_service`, `build_memory_auth_service` and `simple_template`. Cite the amended rule
   (`structure-map.md` v2, REQ-014/AC-014, INV-007, EDGE-017). Do **not** invent prose beyond that.
2. **(b) Version bump per the change type** — ISSUE → **`patch`**: `bump-my-version bump patch`
   (`1.1.0 → 1.1.1`) with a **clean working tree** (`allow_dirty` off), in the change worktree; then move
   the `## [Unreleased]` entries into a new `## [1.1.1] - <YYYY-MM-DD>` section **in the same commit** as
   the bump (`CHANGELOG.md` is hand-maintained; `bump-my-version` does not touch it; `tag = false`, no tag
   on the change branch). Dry-run first if unsure: `bump-my-version bump patch --dry-run`.
3. **(c) The full regression suite — the light-tier pre-merge gate (the single open gate, 6.3.1 #3):**
   regenerate the map **immediately before** the run (`uv run python scripts/make_map.py`, then
   `uv run python scripts/make_map.py --check` exit 0) — the F-01 host caveat is the `docs/` file-count
   line going stale as `main` gains planning records, and F-03 is the CRLF (`i/lf w/crlf`,
   `core.autocrlf=true`) second cause of `test_ac_021_committed_map_matches_fresh_render`; regeneration
   fixes both for the run, and `STRUCTURE.md` is **never** hand-edited. Then run
   **`uv run pytest tests/ -v`** and require it to pass with **no new failures**. Read the count correctly:
   the acceptance category reports **1 skipped** on this host (`test_ac_031_symlink_rejected`, F-22) — a
   platform capability guard, not a deselected or weakened test. If `test_ac_021…` is red, the cause is the
   map, not the fix: regenerate and re-commit the map with the `.py` change (REQ-023).
   **The result (command, counts, exit code, and the map state it was taken against) MUST be recorded in
   this review report** — appended to this section as the S6.4 pre-merge gate record — because AGENTS.md
   Phase 5 ISSUE item 9 / "Light ISSUE tier" and the review skill require the full-regression result to be
   in the review report, not merely in a commit message.
4. **(d) Open the PR** for `issue/map-default-drop-shift` → `main` (git skill, "Create PR") and present it
   for human review/merge, **then STOP**. The agent MUST NOT merge the PR (human governance); the change
   then goes **WAITING** until the merge, after which S7.1 cleanup runs.

If the full-suite gate at (c) does **not** pass, this CLEAN verdict is void: the change stays unmerged,
the failure is classified (pre-existing vs regression, AGENTS.md Phase 5 ISSUE item 12), and the change
re-enters Phase 4 (or Phase 3) with a fresh subagent — the PR is not opened.

### 6.3.5 Verdict

The change satisfies every ISSUE review-gate criterion that is in scope at this step: the reproduction
tests are GREEN (four independent re-runs), the fix introduces no behavior beyond the affected spec IDs
(`REQ-014` v2, `AC-014` v2, `INV-007`, `EDGE-017` — the merged Spec Amendment PR A #79), no acceptance test
was weakened or deleted, traceability is complete with zero orphans and no untouched row refreshed, feature
boundaries and architecture rules hold, the generated-file rule is satisfied, and the quality gates are
clean. All nine Phase 6 findings are resolved, accepted with a reason, or explicitly deferred as out of
scope; **none is open as a defect**. The one criterion not yet green — the **full regression suite**
`uv run pytest tests/ -v` — is the light-tier **S6.4 pre-merge gate** and is recorded as the **single open
gate** (6.3.1 #3, 6.3.4 (c)).

**◆ S6.3: review report CLEAN (conditional on the S6.4 full-regression pre-merge gate)**

Next: **S6.4 Bump version + open PR** — obligations (a)–(d) in 6.3.4, in that order.

---

## Phase 6 — S6.4 pre-merge gate + release (2026-10-10)

HEAD at entry: `081082c` (the S6.3 review report), `git status --porcelain` **empty** at entry and after
every commit made here. This step writes **`CHANGELOG.md`, `pyproject.toml`, `uv.lock` and this file** —
no `src/`, no `tests/`, no `scripts/`, no `STRUCTURE.md`, no spec, no `docs/verification/traceability.md`,
no `docs/todo/`, no `docs/questions/`, no `AGENTS.md`. **Nothing was merged; no tag was created.**

### 6.4.1 Sync with `main`

| Command | Result |
|---|---|
| `git fetch origin` | `origin/main` = `414b908` (`chore(map-default-drop-shift): status IN-WORKFLOW (PR A #79 merged as d8ba07f, Phase 3 starts)`) |
| `git merge-base --is-ancestor origin/main HEAD` | exit **0** — `origin/main` is already an ancestor of this branch |
| `git merge origin/main` | `Already up to date.` — **no merge commit, no conflict**, so the "take either side and regenerate `STRUCTURE.md`" rule was never reached |

The branch was cut from `main` `7299108` and PR A #79 merged into `main` **from this same branch**
(`d8ba07f`), so every planning-record commit `main` has gained since the cut is already carried here.

### 6.4.2 (a) `CHANGELOG.md` entry — commit `e7c8b30`

`docs(map-default-drop-shift): changelog entry` (`1 file changed, 10 insertions(+)`) — one entry under
`## [Unreleased]` → **`Fixed`** (that heading did not exist in the section and was created; the Keep a
Changelog order `Added` → `Fixed` is preserved). The prose is derived from §3.2 and §3.3 (the two live
witnesses), §5.1 (the fix) and 6.3.4 (a): the generator no longer drops an over-long default but
abbreviates it to the `…` placeholder in the parameter's own slot, so signature lines no longer shift a
default onto the following parameter or render a defaulted parameter as required; the four corrected
renderings and the amended rule (`structure-map.md` v2 — REQ-014/AC-014, INV-007, EDGE-017) are named.
Nothing else was added to the file.

### 6.4.3 (c) The full regression suite — the light-tier pre-merge gate (6.3.1 #3) — **CLOSED**

Map freshness first, per 6.3.4 (c) (the F-01 / F-03 mitigation):

| Command | Result | Exit |
|---|---|---|
| `uv run python scripts/make_map.py --check` (at `e7c8b30`) | no output — the committed map **is** the fresh render | **0** |
| `git status --porcelain` immediately after | empty — nothing to regenerate, so **no** `chore(…): regenerate STRUCTURE.md` commit was owed (finding F-37) | — |

The gate itself:

| Command | Result | Exit | Wall time | Taken at |
|---|---|---|---|---|
| `uv run pytest tests/ -q` | **819 passed, 1 skipped** | 0 (no `FAILED`/`ERROR` line; the exit code is captured explicitly in the run below) | `252.04s` | `e7c8b30` |
| `uv run pytest tests/ -q` | **819 passed, 1 skipped** | **0** | `253.01s (0:04:13)` | `c223e84` — the final code commit |

- **No new failures.** The single skip is `tests/acceptance/filemanagement/test_filemanagement.py:364`
  (`test_ac_031_symlink_rejected`, "symlinks not available on this host") — the pre-existing
  host-capability guard recorded as **F-22**, not a deselected, newly-skipped or weakened test.
  `-p no:randomly` was not needed: no randomly-ordered failure had to be reproduced.
- **Count reconciliation.** The highest full-suite record in `docs/verification/traceability.md` is
  `816 passed, 1 skipped` (structure-map S5.1, 2026-10-09, `3ec204c`); this change adds exactly **3**
  `def test_…` (`git diff --stat main...HEAD -- tests/` → `+358 / −14`, **0** test definitions removed)
  → **819**. Nothing disappeared, so the delta is fully explained.
- **Why the result is valid at the final commit.** `c223e84` touches only `pyproject.toml`, `uv.lock` and
  `CHANGELOG.md`; no test asserts the project version (`tests/contract/logging/test_dependency_contract.py`
  parses `pyproject.toml` for deptry/quality-gate keys only), and the suite was re-run at `c223e84` anyway,
  with the exit code captured, so the gate is measured against the tree that will actually merge.

**◆ The single open gate of 6.3.1 (#3) is closed: the full regression suite passes.** The S6.3 CLEAN
verdict is therefore **no longer conditional**.

### 6.4.4 (b) Version bump — commit `c223e84` `chore(release): 1.1.1`

ISSUE → **patch** (AGENTS.md "Versioning"). Working tree clean before the bump (`allow_dirty` is off).

| Command / step | Result |
|---|---|
| `uv tool run bump-my-version bump patch --dry-run` | exit **0** — `1.1.0 → 1.1.1`; would change `pyproject.toml:4` and `[tool.bumpversion] current_version` (finding F-35 covers the tool's silent/`UnicodeEncodeError` logging on this host) |
| `uv tool run bump-my-version bump patch --no-commit` | exit **0** — both lines changed, **no commit, no tag** |
| `uv lock` | `Resolved 113 packages` / `Updated python-template v1.1.0 -> v1.1.1`, exit **0** |
| `CHANGELOG.md` | the `## [Unreleased]` entries moved to **`## [1.1.1] - 2026-10-10`** in the same commit; an empty `## [Unreleased]` heading is kept for the next change (the section carried this change's `Fixed` entry plus the two post-1.1.0 `Added` entries, all of which belong to this release) |
| `git commit -m "chore(release): 1.1.1"` | one commit, `3 files changed, 5 insertions(+), 3 deletions(-)`: `pyproject.toml` (+2/−2), `uv.lock` (+1/−1), `CHANGELOG.md` (+2) |
| `git tag` | unchanged — **no tag created** (`tag = false`) |

**Order note.** The task-definition runs the pre-merge gate (c) **before** the bump (b) — the reverse of
6.3.4's (b)→(c) order — so the gate was measured against the pre-release tree at `e7c8b30` **and** then
re-run at the release commit `c223e84` (6.4.3) to cover the bump itself. Both runs are identical.

### 6.4.5 Re-verification after the changelog and release commits

| Command | Result | Exit |
|---|---|---|
| `uv run python scripts/make_map.py --check` | no output | **0** |
| `uv run python scripts/check_traceability.py` | `Traceability: PASS (883 matrix rows, 136 spec IDs, 804 test functions)` | **0** |
| `uv run ruff check .` | `All checks passed!` | **0** |
| `uv run ruff format --check .` | `343 files already formatted` | 0 |
| `git status --porcelain` | empty | — |

### 6.4.6 (d) PR — **#80**

- Branch pushed: `52fa324..c223e84 → origin/issue/map-default-drop-shift`.
- **PR #80** — https://github.com/jackthenet/python-template/pull/80 — `issue/map-default-drop-shift` →
  `main`, 15 commits, not a draft. Body: type ISSUE (light tier), the defect + root cause, the normative
  basis (merged Spec Amendment **#79**, `d8ba07f`, `structure-map.md` v2), the Phase 5 coverage table
  (spec coverage 100%, 4/4 IDs green), the S6.3 CLEAN verdict + this pre-merge result, the traceability
  rows, the `1.1.0 → 1.1.1` bump, and the F-01…F-34 ledger by pointer to this file.
- **Not merged, not approved, not commented on, no auto-merge, no tag** (human governance). The change now
  goes **WAITING**; when the human merges, **S7.1** post-merge cleanup resumes it with a fresh subagent.
- CI as observed right after opening: `lint`, `type-check`, `spec-validation`, `security`, `traceability`,
  `dependency-review`, `dependencies`, `docs`, `migrations`, `complexity` → **SUCCESS**; `tests` and
  `coverage` → still **IN PROGRESS** (hence `mergeStateStatus: UNSTABLE`, i.e. pending checks, not failing).

### New findings from S6.4 (F-35 … F-37)

| ID | Finding | Severity | Disposition |
|---|---|---|---|
| **F-35** | `bump-my-version` 1.5.1 renders its log through `rich`; the `→` in the configured message `Bump version: {current} → {new}` raises `UnicodeEncodeError` on the cp1252 Windows console (visible only with `--verbose`), and at the default level a plain `--dry-run` prints **nothing at all**, which reads as a silent failure. | Info (host/tooling friction; exit 0, the bump is correct) | **No action in this change** — the bump was verified from `git diff`, not from the tool's stdout, and `--no-commit` sidesteps the message. Problem Log entry for the after-workflow-optimization: on Windows, capture bump evidence from `git diff` + `--dry-run --verbose`. |
| **F-36** | Patching `CHANGELOG.md` with a script that reads it as text and writes it back rewrites the whole working copy to LF (`core.autocrlf=true`, the F-03 family): 10 CRLF / 287 bare LF after the first write. | Info (host line-ending friction, **no repo effect**) | **Fixed in-step** — the file was re-normalised to CRLF (299 CRLF, 0 bare LF) before the release commit, and `git diff` stayed at exactly the intended `+2` lines because the index normalises to LF. Note for future steps: patch this repo's text files with an ending-preserving tool, or re-normalise before committing. |
| **F-37** | The 6.3.4 (c) instruction to regenerate the map immediately before the full-suite run was **not needed** here: `make_map.py --check` exits 0 at `e7c8b30` and at `c223e84`, because the branch already carries every `main` commit, so the `docs/` file-count line (F-01) is current. | Info (the F-01/F-03 caveat is conditional, not permanent) | **No action** — the mitigation stays written down; it fires only when `main` gains `docs/` files while a change worktree is behind. Re-run `--check` after any `git merge origin/main`. |

**No finding is open as a defect.** F-35/F-36/F-37 are host/tooling observations; F-32 (changelog + bump)
is **closed** by this step; F-01/F-02 stay resolved since `0c73790`; F-03 stays out of scope with the
mitigation exercised and shown unnecessary at this commit (F-37).

### ◆ S6.4 verdict

(a) changelog entry under `Fixed` ✔ · (c) **full regression suite: 819 passed, 1 skipped, exit 0** at the
final code commit — the light tier's single open gate closed ✔ · (b) version bump **1.1.0 → 1.1.1** with
the entries moved to `## [1.1.1] - 2026-10-10` in one release commit, no tag ✔ · (d) **PR #80** open
against `main` ✔ · `check_traceability.py` exit 0 ✔ · working tree clean ✔ · nothing merged ✔.

**Next: S7.1 post-merge cleanup — after the human merges PR #80.**
