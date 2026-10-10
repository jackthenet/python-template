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
